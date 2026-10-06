"""Hasil evaluasi nyata (core.evaluate) untuk dipakai di layar. Dihitung sekali per sesi server."""
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st
import joblib

from core import feedback as fb_mod
from core import feedback_eval
from core import live as live_mod
from core import review_history as review_store
from core.evaluate import benchmark
from core.synthetic import SEED, World, generate_world

_ENGINE_CACHE_VERSION = 2
_ENGINE_CACHE_DIR = Path(__file__).resolve().parents[1] / ".jala" / "cache"


@st.cache_resource(show_spinner="Menghitung skor dan klaster pada data sintetis…")
def _engine(seed: int = SEED):
    """Satu kali per server: dunia sintetis, skor (validasi silang per faskes), dan klaster hasil Louvain."""
    cache_path = _ENGINE_CACHE_DIR / f"engine-v{_ENGINE_CACHE_VERSION}-seed-{seed}.joblib"
    try:
        payload = joblib.load(cache_path)
        if payload.get("version") == _ENGINE_CACHE_VERSION and payload.get("seed") == seed:
            return payload["benchmark"], payload["live"]
    except Exception:
        pass
    world = generate_world(seed)
    bm = benchmark(seed, world=world)
    live = live_mod.build(world, bm.scored)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(prefix="engine-", suffix=".tmp", dir=cache_path.parent)
        os.close(fd)
        joblib.dump({"version": _ENGINE_CACHE_VERSION, "seed": seed,
                     "benchmark": bm, "live": live}, tmp_path)
        os.replace(tmp_path, cache_path)
    except OSError:
        try:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except OSError:
            pass
    return bm, live


@st.cache_resource(show_spinner=False)
def get_world(seed: int = SEED) -> World:
    """Dunia sintetis yang sama untuk evaluasi dampak, tanpa label di jalur deteksi."""
    return generate_world(seed)


def get_metrics(seed: int = SEED) -> dict:
    return _engine(seed)[0].metrics


def get_live_base(seed: int = SEED) -> live_mod.Live:
    """Klaster dengan skor dasar model, tanpa umpan balik verifikator."""
    return _engine(seed)[1]


@st.cache_data(show_spinner=False)
def get_error_dismissal_report(seed: int = SEED) -> dict:
    return feedback_eval.evaluate_wrong_dismissal(get_live_base(seed), get_world(seed))


def get_feedback() -> dict:
    """Keputusan verifikator pada sesi ini ({cluster_id: {verdict, note, at}}). Kosong di luar sesi Streamlit."""
    try:
        return dict(st.session_state.get("feedback", {}))
    except Exception:
        return {}


def get_live(seed: int = SEED) -> live_mod.Live:
    """Data layar dari skor nyata (Risk Ranking, Claim Details, Network Graph, Audit, Dashboard),
    dengan kalibrasi ringan dari keputusan verifikator sesi ini (core.feedback)."""
    return fb_mod.adjust(get_live_base(seed), get_feedback())


def apply_verdict(cid: str, verdict: str, note: str = "") -> None:
    """Catat keputusan verifikator; skor dan peringkat dihitung ulang pada render berikutnya."""
    st.session_state["feedback"] = fb_mod.record(get_feedback(), cid, verdict, note)


def record_review_event(cid: str, action: str, note: str = "", score_before: int | None = None,
                        score_after: int | None = None) -> None:
    """Tambahkan event pemeriksaan berstruktur ke riwayat lokal yang persisten."""
    history = st.session_state.setdefault("review_history", [])
    event = {
        "case_id": cid,
        "action": action,
        "note": note.strip(),
        "at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "actor": "Verifikator (sesi demo)",
        "score_before": score_before,
        "score_after": score_after,
    }
    history.append(event)
    del history[:-500]
    try:
        event["event_id"] = review_store.append_event(event)
        st.session_state.pop("review_history_error", None)
    except (OSError, ValueError, TypeError):
        st.session_state["review_history_error"] = "Riwayat tidak dapat disimpan ke basis data lokal."
    except Exception:
        st.session_state["review_history_error"] = "Riwayat tidak dapat disimpan ke basis data lokal."


def get_review_history(cid: str | None = None) -> list[dict]:
    try:
        history = review_store.list_events(cid)
        st.session_state.pop("review_history_error", None)
        return history
    except Exception:
        st.session_state["review_history_error"] = "Riwayat lokal tidak dapat dibaca dari basis data."
        history = st.session_state.get("review_history", [])
        return [event for event in history if cid is None or event.get("case_id") == cid]


def undo_verdict(cid: str) -> None:
    before = get_live().by_id.get(cid, {}).get("score")
    st.session_state["feedback"] = fb_mod.undo(get_feedback(), cid)
    after = get_live().by_id.get(cid, {}).get("score")
    record_review_event(cid, "Umpan balik dibatalkan", score_before=before, score_after=after)
    audited = st.session_state.get("audited", {})
    if audited.get(cid) in ("dismiss", "freeze"):
        audited.pop(cid)


def reset_feedback() -> None:
    previous = get_feedback()
    scores_before = {cid: get_live().by_id.get(cid, {}).get("score") for cid in previous}
    st.session_state["feedback"] = {}
    st.session_state["audited"] = {}
    current = get_live()
    for cid in previous:
        record_review_event(cid, "Umpan balik sesi diatur ulang",
                            score_before=scores_before[cid],
                            score_after=current.by_id.get(cid, {}).get("score"))


def reset_demo() -> None:
    """Pulihkan status demo tanpa menghapus riwayat audit persisten atau cache model/data."""
    reset_feedback()
    st.session_state["audit_log"] = []
    st.session_state["note_draft"] = ""
    st.session_state["selected_cluster"] = None
    st.session_state["zoom"] = 1.0
    st.session_state["isolate"] = False
    st.session_state["tour_step"] = 0
    st.session_state.pop("risk_chip", None)
    st.session_state["case_search_query"] = ""
    st.session_state["case_search_filter"] = "Semua pola"


ROBUSTNESS_PATH = Path(__file__).resolve().parent.parent / "docs" / "robustness.json"
TEMPORAL_IMPACT_PATH = Path(__file__).resolve().parent.parent / "docs" / "temporal_impact.json"


@st.cache_data(show_spinner=False)
def get_robustness() -> dict | None:
    """Hasil `python -m core.robustness --json docs/robustness.json` (sekitar 90 detik, jadi dibaca dari berkas)."""
    try:
        return json.loads(ROBUSTNESS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@st.cache_data(show_spinner=False)
def get_temporal_impact() -> dict | None:
    try:
        return json.loads(TEMPORAL_IMPACT_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
