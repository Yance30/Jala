"""Observed links in a scored batch, not inferred fraud rings or model attribution."""
import json

import pandas as pd


def build(claims, claim_id, *, days=30, graph_limit=40):
    if days < 1 or graph_limit < 1 or claims.claim_id.duplicated().any():
        raise ValueError("Jendela dan batas graf harus positif; ID klaim harus unik.")
    indexed = claims.set_index("claim_id")
    if claim_id not in indexed.index:
        raise ValueError("Klaim tidak ditemukan dalam batch.")
    focus = indexed.loc[claim_id]
    delta = (claims.visit_ts - focus.visit_ts).abs()
    same_patient = claims.patient_id.eq(focus.patient_id)
    same_doctor = claims.doctor_id.eq(focus.doctor_id)
    ref = claims.get("referral_from_doctor", pd.Series(None, index=claims.index, dtype=object))
    doctor_links = ref.eq(focus.doctor_id)
    focus_ref = focus.get("referral_from_doctor")
    if pd.notna(focus_ref) and str(focus_ref).strip():
        doctor_links |= claims.doctor_id.eq(focus_ref) | ref.eq(focus_ref)
    selected = claims[(delta <= pd.Timedelta(days=days)) & (same_patient | same_doctor | doctor_links)].copy()
    selected["keterkaitan"] = [
        "; ".join(reason for match, reason in (
            (row.claim_id == claim_id, "Klaim terpilih"),
            (row.patient_id == focus.patient_id, "Peserta sama"),
            (row.doctor_id == focus.doctor_id, "Dokter sama"),
            (bool(doctor_links.loc[i]), "Dokter terkait rujukan")) if match)
        for i, row in selected.iterrows()
    ]
    selected = selected.sort_values(["visit_ts", "claim_id"], kind="stable")
    # Keep focus visible even if many earlier claims fill the graph budget.
    neighbours = selected[selected.claim_id.ne(claim_id)].copy()
    neighbours["_distance"] = (neighbours.visit_ts - focus.visit_ts).abs()
    graph_rows = pd.concat([selected[selected.claim_id.eq(claim_id)],
                            neighbours.sort_values(["_distance", "claim_id"]).head(graph_limit - 1)])
    nodes, edges = {}, []

    def node(kind, value):
        key = (kind, str(value))
        nodes[key] = dict(kind=kind, label=str(value))
        return key

    for row in graph_rows.itertuples():
        claim = node("Klaim", row.claim_id)
        for kind, value, relation in (
            ("Peserta", row.patient_id, "peserta"),
            ("Dokter", row.doctor_id, "dokter layanan"),
            ("Faskes", row.faskes_id, "faskes layanan"),
            ("Diagnosis", row.icd, "kode tercatat"),
            ("Dokter", getattr(row, "referral_from_doctor", None), "dokter perujuk"),
            ("Faskes", getattr(row, "referral_from_faskes", None), "faskes asal rujukan"),
        ):
            if pd.notna(value) and str(value).strip():
                edges.append((node(kind, value), claim, relation))
    return dict(focus=claim_id, days=days, related=selected, nodes=nodes, edges=edges,
                graph_claims=len(graph_rows), omitted=len(selected) - len(graph_rows),
                referral_available="referral_from_doctor" in claims.columns,
                total_tariff=float(selected.tarif.sum()))


def evidence(queue, context):
    ids = set(context["related"].claim_id)
    return dict(batch_id=queue["id"], model=queue["model"], focus=context["focus"],
                scope=f"Batch prediksi tersimpan saja, jendela +/-{context['days']} hari dari waktu layanan.",
                selection="Peserta sama, dokter layanan sama, atau dokter terkait rujukan; bukan klaster fraud.",
                total_claimed_tariff=context["total_tariff"],
                claims=json.loads(context["related"].to_json(orient="records", date_format="iso")),
                review_events=[event for event in queue["events"] if event["claim_id"] in ids],
                limitations=["Nilai klaim bukan kerugian fraud.", "Hubungan bukan bukti sebab-akibat.",
                             "Riwayat di luar batch dan rekam medis tidak disertakan."])
