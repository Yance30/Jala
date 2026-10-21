"""Local storage status: saved models, review queues, runtime versions, audit trail."""
import json

import pandas as pd
import streamlit as st

from core import batch_store


def render():
    st.header("Status sistem")
    from components.data_management import render as data_management
    data_management()
    st.caption("Penyimpanan dibatasi ke ruang aktif. Checksum mendeteksi korupsi berkas, bukan penyuntingan "
               "beritikad buruk; jejak audit belum tahan perubahan administrator mesin.")
    path = batch_store.database_path()
    size = f" · {path.stat().st_size / 1024:.0f} KB" if path.exists() else " · belum dibuat"
    st.caption(f"Basis data: {path}{size}")
    models = batch_store.model_details()
    queues = batch_store.queue_summary()
    left, right = st.columns(2)
    left.metric("Model tersimpan", len(models))
    right.metric("Antrean tinjauan", len(queues))

    st.subheader("Model tersimpan")
    if not models:
        st.info("Belum ada model tersimpan; simpan dari Data & Prediksi.")
    else:
        current = batch_store.runtime()
        rows = [dict(checksum=m["id"][:16], dibuat=m["created"][:16],
                     versi=m["metadata"].get("version"),
                     fitur=m["metadata"].get("feature_set", "base"),
                     runtime_cocok=m["runtime"] == current) for m in models]
        st.dataframe(pd.DataFrame(rows), hide_index=True)
        st.caption("runtime_cocok bernilai benar bila versi Python/sklearn/numpy/pandas saat model disimpan "
                   "sama dengan lingkungan sekarang; model dengan nilai salah menolak dimuat.")
        with st.expander("Versi runtime tiap model"):
            st.json({m["id"][:16]: m["runtime"] for m in models})

    st.subheader("Antrean dan jejak audit")
    if not queues:
        st.info("Belum ada antrean tinjauan tersimpan.")
        return
    labels = {q["id"]: f"{q['id'][:10]} · {q['created'][:16]} · {q['events']} peristiwa" for q in queues}
    st.selectbox("Antrean", list(labels), key="status_queue", format_func=labels.get)
    events = batch_store.queue_events(st.session_state["status_queue"])
    if not events:
        st.caption("Belum ada keputusan tercatat pada antrean ini.")
        return
    table = pd.DataFrame([dict(waktu=e["timestamp"][:16], klaim=e["claim_id"], status=e["status"],
                               pemeriksa=e.get("actor") or "tidak tercatat", catatan=e["note"][:60])
                          for e in events])
    st.dataframe(table, hide_index=True)
    st.download_button("Unduh jejak audit", json.dumps(events, ensure_ascii=False, indent=2),
                       file_name="jala-audit-trail.json", mime="application/json")
