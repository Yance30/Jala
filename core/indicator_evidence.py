"""Bounded, traceable observed records; not feature attribution or proof of fraud."""
import json
import numpy as np
import pandas as pd

FIELDS = ["claim_id", "patient_id", "doctor_id", "faskes_id", "icd", "tarif", "visit_ts", "submit_ts"]


def attach(snapshot, features):
    # Serialize once, not once per focus claim. Window lookups use sorted arrays.
    records = {row["claim_id"]: row for row in json.loads(
        snapshot[FIELDS].to_json(orient="records", date_format="iso", date_unit="ns", double_precision=15))}
    focus_rows = snapshot.set_index("claim_id")
    ordered = snapshot.sort_values(["patient_id", "icd", "visit_ts", "claim_id"], kind="stable")
    previous = dict(zip(ordered.claim_id, ordered.groupby(["patient_id", "icd"]).claim_id.shift()))
    def windows(key, time):
        result = {}
        for name, group in snapshot.groupby(key):
            group = group.sort_values([time, "claim_id"], kind="stable")
            result[name] = (group[time].to_numpy(dtype="datetime64[ns]").astype("int64"),
                            group.claim_id.to_numpy(), group.faskes_id.to_numpy())
        return result
    doctors, facilities = windows("doctor_id", "visit_ts"), windows("faskes_id", "submit_ts")
    referral = {key: group.claim_id.tolist() for key, group in
                snapshot.sort_values(["visit_ts", "claim_id"]).groupby("referral_from_doctor")}
    def window(index, key, timestamp, width, facility=None, exclude=None):
        times, ids, faskes = index[key]
        lo = np.searchsorted(times, timestamp.value - width)
        hi = np.searchsorted(times, timestamp.value + width, side="right")
        chosen = ids[lo:hi]
        if facility is not None:
            chosen = chosen[faskes[lo:hi] != facility]
        if exclude is not None:
            chosen = chosen[chosen != exclude]
        return chosen.tolist()
    output = []
    for cid, values in features.iterrows():
        focus = focus_rows.loc[cid]
        groups = {}
        prior_id = previous.get(cid)
        if pd.notna(prior_id):
            groups["Klaim pembanding peserta dan diagnosis"] = [prior_id]
        if values.f_doc_conc:
            groups["Dokter lintas faskes ±30 menit"] = window(
                doctors, focus.doctor_id, focus.visit_ts, pd.Timedelta(minutes=30).value, facility=focus.faskes_id)
        if values.f_burst_z > 2:
            groups["Pengajuan faskes ±60 detik"] = window(
                facilities, focus.faskes_id, focus.submit_ts, pd.Timedelta(seconds=60).value, exclude=cid)
        if pd.notna(focus.referral_from_doctor) and focus.referral_from_doctor in referral:
            groups["Rujukan dokter dalam snapshot"] = referral[focus.referral_from_doctor]
        evidence = {}
        for label, ids in groups.items():
            evidence[label] = dict(total=len(ids), shown=min(len(ids), 8),
                                   records=[records[key] for key in ids[:8]])
        output.append(json.dumps(dict(
            focus=records[cid],
            feature_values={key: float(value) for key, value in values.items()},
            comparisons=evidence,
            scope="Snapshot pelatihan + riwayat observasi + batch aktif; maksimal 8 catatan per indikator.",
            limitations="Catatan dan nilai fitur adalah konteks observasi, bukan atribusi model atau bukti fraud."),
            ensure_ascii=False))
    return output
