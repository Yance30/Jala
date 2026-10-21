"""Explicit data lifecycle actions scoped to the current storage identity."""
import streamlit as st
from core import batch_store, access


def clear_session():
    prefixes = ("external_", "saved_", "review_", "reviewer_", "decision_", "batch_review", "batch_experiment",
                "dataset_origin", "context_")
    for key in list(st.session_state):
        if key.startswith(prefixes):
            del st.session_state[key]


def render():
    with st.expander("Penyimpanan dan penghapusan data"):
        st.write("Model tersimpan mencakup parameter, riwayat klaim pelatihan dan tabel referensi. "
                 "Prediksi model tersimpan juga menyimpan riwayat observasi antarbatch. "
                 "Membuka antrean menyimpan klaim, konteks bukti, dan keputusan.")
        st.caption("Demo: ruang terpisah per sesi, dibersihkan setelah 24 jam tidak aktif saat aplikasi "
                   "kembali mengakses penyimpanan. Mode lokal/bersama: tersimpan sampai dihapus pemilik. "
                   "Menghapus model tidak menghapus salinan klaim di antrean; hapus keduanya bila diperlukan. "
                   "Penghapusan tidak menjamin penghapusan salinan backup atau unduhan.")
        st.caption(f"Mode penyimpanan: {access.mode()}. Peran pratinjau tidak memberikan akses tambahan.")
        st.button("Bersihkan paket dan hasil dari sesi", on_click=clear_session, key="data_clear_session")
        models, queues = batch_store.list_models(), batch_store.list_queues()
        options = {f"Model {m['id']}": ("model", m["id"]) for m in models}
        options.update({f"Antrean {q['id']}": ("queue", q["id"]) for q in queues})
        if options:
            target = st.selectbox("Data tersimpan yang akan dihapus", list(options), key="data_delete_target")
            confirm = st.checkbox("Saya memahami data terpilih dan riwayat terkait akan dihapus", key="data_delete_confirm")
            if st.button("Hapus data terpilih", disabled=not confirm, key="data_delete"):
                kind, key = options[target]
                (batch_store.delete_model if kind == "model" else batch_store.delete_queue)(key)
                clear_session()
                st.rerun()
        confirm_all = st.checkbox("Hapus seluruh model, riwayat observasi, antrean dan keputusan dalam ruang saya",
                                  key="data_clear_all_confirm")
        if st.button("Hapus seluruh data ruang saya", disabled=not confirm_all, key="data_clear_all"):
            batch_store.clear_workspace()
            clear_session()
            st.rerun()
