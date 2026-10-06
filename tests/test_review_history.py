from core import review_history
from components.verifier_tools import review_history_csv


def test_review_history_persists_between_database_connections(tmp_path, monkeypatch):
    db_path = tmp_path / "reviews.sqlite3"
    monkeypatch.setenv("JALA_REVIEW_HISTORY_DB", str(db_path))

    first_id = review_history.append_event({
        "case_id": "JALA-F006",
        "action": "Tandai sebagai pola wajar",
        "note": "Periksa jadwal layanan",
        "at": "2026-10-06T12:30:00+07:00",
        "actor": "Verifikator (sesi demo)",
        "score_before": 88,
        "score_after": 40,
    })
    review_history.append_event({
        "case_id": "JALA-F044",
        "action": "Jadwalkan pemeriksaan lapangan",
        "note": "",
        "at": "2026-10-06T12:31:00+07:00",
        "actor": "Verifikator (sesi demo)",
        "score_before": 91,
        "score_after": 91,
    })

    events = review_history.list_events("JALA-F006")
    assert len(events) == 1
    assert events[0]["event_id"] == first_id
    assert events[0]["note"] == "Periksa jadwal layanan"
    assert events[0]["score_before"] == 88 and events[0]["score_after"] == 40
    assert len(review_history.list_events()) == 2


def test_review_history_csv_preserves_indonesian_notes_and_quotes():
    exported = review_history_csv([{
        "event_id": 3,
        "case_id": "JALA-F006",
        "at": "2026-10-06T12:30:00+07:00",
        "actor": "Verifikator (sesi demo)",
        "action": "Klarifikasi pola",
        "note": 'Periksa "jadwal layanan", lalu cocokkan dengan bukti sumber.',
        "score_before": 88,
        "score_after": 40,
    }])

    text = exported.decode("utf-8-sig")
    assert text.splitlines()[0].startswith("event_id,case_id,at,actor,action,note,score_before,score_after,")
    assert "lingkungan_data,periode_data,batas_data,waktu_ekspor" in text.splitlines()[0]
    assert "Data sintetis; prototipe" in text
    assert '"Periksa ""jadwal layanan"", lalu cocokkan dengan bukti sumber."' in text
