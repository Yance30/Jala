"""Loop verifikator (versi sederhana): keputusan "dismiss" menurunkan skor dan mengubah peringkat.

Ini kalibrasi ringan di tingkat klaster, BUKAN pelatihan ulang model. Aturannya sengaja transparan:
  * dismiss      : skor klaster x DISMISS_FACTOR
  * klaster serupa (tipologi sama dan kemiripan kosinus profil ICD >= SIM_THRESHOLD, belum diputuskan
    verifikator): skor x (1 - SIMILAR_MAX_DROP * kemiripan). Diturunkan, tidak disembunyikan, dan bisa dibatalkan.
  * confirm      : skor tidak berubah, dan klaster yang sudah dikonfirmasi tidak ikut diturunkan oleh kemiripan.
Bila dismiss keliru pada klaster fraud, klaster serupanya ikut turun (tetap terlihat). Itu keterbatasan yang
diakui; UI menampilkan daftar klaster yang ikut turun dan tombol batal.

Modul ini tidak membaca label, kecuali `evaluate_loop` yang khusus untuk menilai.
"""
from __future__ import annotations

import dataclasses
from datetime import datetime

import numpy as np
import pandas as pd

from core.live import AUTO_FLAG, Live

DISMISS_FACTOR = 0.4
SIMILAR_MAX_DROP = 0.25
SIM_THRESHOLD = 0.85
VERDICTS = ("dismiss", "confirm")


def record(feedback: dict | None, cid: str, verdict: str, note: str = "", at: str | None = None) -> dict:
    if verdict not in VERDICTS:
        raise ValueError(f"verdict harus salah satu dari {VERDICTS}")
    out = dict(feedback or {})
    out[cid] = {"verdict": verdict, "note": note, "at": at or datetime.now().strftime("%Y-%m-%d %H:%M")}
    return out


def undo(feedback: dict | None, cid: str) -> dict:
    out = dict(feedback or {})
    out.pop(cid, None)
    return out


def icd_profile(live: Live, c: dict) -> pd.Series:
    return live.flagged.loc[c["idx"]].icd.value_counts(normalize=True)


def similarity(pa: pd.Series, pb: pd.Series) -> float:
    idx = pa.index.union(pb.index)
    a, b = pa.reindex(idx, fill_value=0).values, pb.reindex(idx, fill_value=0).values
    den = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / den) if den else 0.0


def adjust(live: Live, feedback: dict | None) -> Live:
    """Tampilan Live dengan skor setelah umpan balik. Tanpa umpan balik, mengembalikan `live` apa adanya."""
    fb = {k: v for k, v in (feedback or {}).items() if k in live.by_id}
    if not fb:
        return live
    dismissed = [k for k, v in fb.items() if v["verdict"] == "dismiss"]
    profiles = {c["id"]: icd_profile(live, c) for c in live.clusters}
    new = []
    for c in live.clusters:
        cid, factor, info = c["id"], 1.0, None
        if cid in fb and fb[cid]["verdict"] == "dismiss":
            factor, info = DISMISS_FACTOR, {"kind": "dismiss", "source": cid, "sim": 1.0}
        elif cid in fb:
            info = {"kind": "confirm", "source": cid, "sim": 1.0}
        else:
            for d in dismissed:
                dc = live.by_id[d]
                if dc["typology"] != c["typology"]:
                    continue
                sim = similarity(profiles[cid], profiles[d])
                if sim >= SIM_THRESHOLD:
                    f = 1 - SIMILAR_MAX_DROP * sim
                    if f < factor:
                        factor, info = f, {"kind": "similar", "source": d, "sim": sim}
        nc = dict(c)
        nc["score_base"], nc["score"], nc["fb"] = c["score"], int(round(c["score"] * factor)), info
        new.append(nc)
    new.sort(key=lambda x: (-x["score"], -x["n"]))
    return dataclasses.replace(live, clusters=new, by_id={c["id"]: c for c in new})


def changes(before: Live, after: Live) -> list[dict]:
    """Klaster yang skor atau peringkatnya berubah antara dua tampilan."""
    rb = {c["id"]: i + 1 for i, c in enumerate(before.clusters)}
    out = []
    for i, c in enumerate(after.clusters, start=1):
        b = before.by_id[c["id"]]
        if c["score"] != b["score"] or i != rb[c["id"]]:
            fb = c.get("fb") or {}
            out.append({"id": c["id"], "name": c["name"], "score_before": b["score"], "score_after": c["score"],
                        "rank_before": rb[c["id"]], "rank_after": i, "kind": fb.get("kind"),
                        "source": fb.get("source"), "sim": fb.get("sim")})
    out.sort(key=lambda x: ({"dismiss": 0, "similar": 1}.get(x["kind"], 2), x["score_after"] - x["score_before"]))
    return out


def describe(ch: dict) -> str:
    rank = (f"peringkat #{ch['rank_before']} → #{ch['rank_after']}" if ch["rank_before"] != ch["rank_after"]
            else f"peringkat tetap #{ch['rank_after']}")
    if ch["kind"] == "dismiss":
        return f"{ch['id']}: skor {ch['score_before']}% → {ch['score_after']}%, {rank} (di-dismiss verifikator)"
    if ch["kind"] == "similar":
        return (f"{ch['id']}: skor {ch['score_before']}% → {ch['score_after']}%, {rank} "
                f"(pola diagnosis serupa {ch['sim']:.2f} dengan {ch['source']})")
    return f"{ch['id']}: {rank}"


def evaluate_loop(live: Live, world, fraud_threshold: float = .5) -> dict:
    """HANYA UNTUK MENILAI (memakai label): verifikator simulasi meninjau antrean dari atas; klaster yang
    sebenarnya tidak berisi fraud di-dismiss. Ukur presisi antrean Auto-Flagged dan beban peninjauan."""
    lab = world.labels.set_index("claim_id")
    share = {c["id"]: float(lab.loc[c["idx"]].is_fraud.mean()) for c in live.clusters}
    is_fraud = {k: v >= fraud_threshold for k, v in share.items()}

    def precision(lv: Live) -> float:
        q = [c["id"] for c in lv.clusters if c["score"] >= AUTO_FLAG]
        return sum(is_fraud[i] for i in q) / len(q) if q else 1.0

    def reviews_to_last_fraud(lv: Live) -> int:
        pos = [i for i, c in enumerate(lv.clusters, 1) if is_fraud[c["id"]]]
        return max(pos) if pos else 0

    fb: dict = {}
    steps = [{"dismissed": None, "precision": precision(live), "reviews_to_last_fraud": reviews_to_last_fraud(live),
              "fraud_clusters_demoted": 0}]
    cur = live
    reviewed: set = set()
    while True:
        nxt = next((c["id"] for c in cur.clusters if c["id"] not in reviewed), None)
        if nxt is None:
            break
        reviewed.add(nxt)
        if is_fraud[nxt]:
            continue
        fb = record(fb, nxt, "dismiss", at="sim")
        cur = adjust(live, fb)
        steps.append({"dismissed": nxt, "precision": precision(cur),
                      "reviews_to_last_fraud": reviews_to_last_fraud(cur),
                      "fraud_clusters_demoted": sum(1 for c in cur.clusters if is_fraud[c["id"]]
                                                     and c["score"] < live.by_id[c["id"]]["score"])})
    return {"n_clusters": len(live.clusters), "n_fraud_clusters": sum(is_fraud.values()), "steps": steps}


if __name__ == "__main__":
    from core import live as L
    from core.evaluate import benchmark
    from core.synthetic import generate_world
    w = generate_world()
    lv = L.build(w, benchmark(world=w).scored)
    for s in evaluate_loop(lv, w)["steps"]:
        print(s)
