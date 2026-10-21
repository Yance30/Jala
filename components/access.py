"""Initialize identity before any route accesses storage."""
import os
import secrets
import importlib.util
import streamlit as st

from core import access


def initialize():
    mode = access.mode()
    if mode == "local":
        return
    if mode == "demo":
        token = st.session_state.setdefault("_storage_identity", secrets.token_hex(32))
        access.set_scope("session:" + token)
        return
    issuer = os.environ.get("JALA_OIDC_ISSUER", "")
    if not issuer:
        st.error("Mode bersama belum dikonfigurasi: administrator perlu menetapkan penyedia login.")
        st.stop()
    if importlib.util.find_spec("authlib") is None:
        st.error("Mode bersama memerlukan dependensi login: administrator perlu memasang requirements-auth.txt.")
        st.stop()
    if not st.user.is_logged_in:
        st.info("Masuk untuk membuka ruang pemeriksaan pribadi.")
        if st.button("Masuk"):
            st.login()
        st.stop()
    if st.user.get("iss") != issuer or not st.user.get("sub"):
        st.error("Identitas login tidak berasal dari penyedia yang diizinkan.")
        st.stop()
    access.set_scope("oidc:" + issuer + ":" + st.user["sub"])
    if st.sidebar.button("Keluar"):
        st.logout()
