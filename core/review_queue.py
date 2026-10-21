"""Session review queue: model scores and human decisions remain separate."""
import hashlib
import json

import pandas as pd

STATUSES = ("Belum ditinjau", "Perlu bukti tambahan", "Teruskan pemeriksaan", "Selesai ditinjau",
            "Penjelasan layanan wajar", "Kesalahan data", "Data belum cukup")
PRIORITIES = ("Ikuti skor model", "Dahulukan", "Tunda")


def progress(queue):
    """Count actual latest statuses; saving a note does not complete a review."""
    statuses = export(queue).review_status
    pending = int(statuses.eq("Belum ditinjau").sum())
    completed = int(statuses.isin(("Selesai ditinjau", "Penjelasan layanan wajar")).sum())
    return {"Belum ditinjau": pending, "Dalam pemeriksaan": len(statuses) - pending - completed,
            "Selesai": completed}


def prepare(claims, scores, metadata):
    if claims.claim_id.duplicated().any() or scores.claim_id.duplicated().any():
        raise ValueError("ID klaim harus unik.")
    if not set(scores.claim_id).issubset(claims.claim_id):
        raise ValueError("Prediksi tidak sesuai dengan paket klaim.")
    columns = ["claim_id", "faskes_id", "doctor_id", "patient_id", "icd", "tarif", "visit_ts", "submit_ts"]
    columns += [name for name in ("referral_from_faskes", "referral_from_doctor") if name in claims.columns]
    queue = scores.merge(claims[columns], on="claim_id", validate="one_to_one")
    queue = queue.sort_values(["priority_score", "claim_id"], ascending=[False, True]).reset_index(drop=True)
    digest = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode())
    digest.update(queue.to_json(date_format="iso").encode())
    return dict(id=digest.hexdigest(), claims=queue, model=metadata, decisions={}, events=[])


def record(queue, claim_id, status, note, actor="", priority="Ikuti skor model"):
    if claim_id not in set(queue["claims"].claim_id) or status not in STATUSES:
        raise ValueError("Klaim atau status tidak valid.")
    if priority not in PRIORITIES:
        raise ValueError("Prioritas kerja tidak valid.")
    note = note.strip()
    if not note or len(note) > 2000:
        raise ValueError("Catatan wajib diisi, maksimal 2000 karakter.")
    actor = actor.strip()
    if len(actor) > 120:
        raise ValueError("Nama pemeriksa maksimal 120 karakter.")
    event = dict(claim_id=claim_id, status=status, note=note, actor=actor, work_priority=priority,
                 timestamp=pd.Timestamp.now(tz="UTC").isoformat())
    queue["decisions"][claim_id] = event
    queue["events"].append(event.copy())


def export(queue):
    data = queue["claims"].copy()
    data["review_status"] = data.claim_id.map(lambda c: queue["decisions"].get(c, {}).get("status", STATUSES[0]))
    data["review_note"] = data.claim_id.map(lambda c: queue["decisions"].get(c, {}).get("note", ""))
    data["review_actor"] = data.claim_id.map(lambda c: queue["decisions"].get(c, {}).get("actor", ""))
    data["work_priority"] = data.claim_id.map(lambda c: queue["decisions"].get(c, {}).get("work_priority", PRIORITIES[0]))
    return data
