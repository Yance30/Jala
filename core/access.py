"""Server-established storage identity. Never accept scope from URL/form fields."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import os
from pathlib import Path
import time

_scope = ContextVar("jala_storage_scope", default=None)


def mode():
    value = os.environ.get("JALA_MODE", "demo")
    if value not in ("demo", "local", "shared"):
        raise ValueError("JALA_MODE harus demo, local, atau shared.")
    return value


def set_scope(identity):
    if not isinstance(identity, str) or not identity:
        raise ValueError("Identitas penyimpanan wajib.")
    digest = hashlib.sha256(identity.encode()).hexdigest()
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    if get_script_run_ctx(suppress_warning=True) is not None:
        import streamlit as st
        st.session_state['_storage_scope'] = digest
    return _scope.set(digest)


def current_scope():
    # Dialog/fragment reruns may not execute app.py and can use a fresh Context.
    # Resolve the server-established session identity on every storage operation.
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    if get_script_run_ctx(suppress_warning=True) is not None:
        import streamlit as st
        if mode() == 'local':
            return None
        scope = st.session_state.get('_storage_scope')
        if not scope:
            raise PermissionError('Identitas sesi penyimpanan belum ditetapkan.')
        if mode() == 'shared' and not st.user.is_logged_in:
            raise PermissionError('Login diperlukan untuk mengakses penyimpanan.')
        return scope
    return _scope.get()


def authenticated_owner():
    return current_scope() if mode() == "shared" else None


@contextmanager
def storage_scope(identity):
    token = set_scope(identity)
    try:
        yield
    finally:
        _scope.reset(token)


def scoped_path(base):
    base = Path(base)
    scope = current_scope()
    if scope is None:
        if mode() == "shared":
            raise PermissionError("Identitas terautentikasi diperlukan.")
        # CLI/local library users retain their explicitly selected database.
        return base
    namespace = "sessions" if mode() == "demo" else "owners"
    return base.parent / namespace / scope / base.name


def expire_demo_sessions(base, *, hours=24):
    """Remove only idle session DB files; never touch local/owner databases."""
    root = Path(base).parent / "sessions"
    if not root.exists() or root.is_symlink():
        return
    deadline = time.time() - hours * 3600
    allowed_names = {Path(base).name}
    history = os.environ.get("JALA_REVIEW_HISTORY_DB")
    if history:
        allowed_names.add(Path(history).name)
    for folder in root.iterdir():
        if folder.is_symlink() or not folder.is_dir() or len(folder.name) != 64:
            continue
        files = list(folder.iterdir())
        if not files or any(p.is_symlink() or not p.is_file() or
                            p.name not in allowed_names or p.stat().st_mtime >= deadline for p in files):
            continue
        for path in files:
            try:
                path.unlink()
            except OSError:
                break
        else:
            try:
                folder.rmdir()
            except OSError:
                pass
