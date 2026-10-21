import json

import pandas as pd
import pytest

from components.external_lab import example_files
from core import batch
from core.import_data import load, run_holdout


@pytest.fixture
def files():
    return example_files()


def test_external_package_with_mapping_and_custom_tariffs(files):
    files["claims.csv"] = files["claims.csv"].replace(b"claim_id", b"nomor_klaim").replace(b"I10", b"CUSTOM")
    files["mapping.json"] = json.dumps({"claims": {"nomor_klaim": "claim_id"}}).encode()
    files["tariff_caps.json"] = json.dumps({"CUSTOM": 400000, "E11.9": 300000, "N18.6": 1200000}).encode()
    data = load(files)
    model, scores, report = run_holdout(data, cutoff="2026-09-30", capacity=30)
    assert report["evaluation_available"] and len(scores) == report["n_predicted"]
    assert model.tariff_caps["CUSTOM"] == 400000
    assert len(report["model"]["tariff_fingerprint"]) == 64


def test_test_labels_are_optional_and_do_not_change_predictions(files):
    data = load(files)
    _, scores, report = run_holdout(data, cutoff="2026-09-30")
    future = data.tables["claims"].query("submit_ts > '2026-09-30'").claim_id
    data.labels = data.labels[~data.labels.claim_id.isin(future)]
    _, without_labels, report = run_holdout(data, cutoff="2026-09-30")
    assert not report["evaluation_available"] and "jala" not in report
    pd.testing.assert_frame_equal(scores, without_labels)


@pytest.mark.parametrize("change", ["duplicate_header", "label_in_claims", "unknown_ref", "invalid_time", "missing_file"])
def test_invalid_packages_are_blocked(files, change):
    if change == "duplicate_header":
        files["claims.csv"] = files["claims.csv"].replace(b"doctor_id", b"patient_id", 1)
    elif change == "label_in_claims":
        files["claims.csv"] = files["claims.csv"].replace(b"doctor_id", b"is_fraud", 1)
    elif change == "unknown_ref":
        files["patients.csv"] = files["patients.csv"].replace(b"EXT31-P", b"OTHER-")
    elif change == "invalid_time":
        files["claims.csv"] = files["claims.csv"].replace(b"2026-09", b"not-date", 1)
    else:
        del files["faskes.csv"]
    with pytest.raises(ValueError):
        load(files)


def test_timezone_normalization_and_leading_zero_ids(files):
    files["claims.csv"] = files["claims.csv"].replace(b"EXT31-P", b"000")
    files["patients.csv"] = files["patients.csv"].replace(b"EXT31-P", b"000")
    data = load(files)
    assert data.tables["claims"].patient_id.str.startswith("000").all()
    assert data.tables["claims"].submit_ts.dt.tz is None


def test_offset_times_are_converted_to_utc():
    from core.import_data import _csv
    raw = b"claim_id,faskes_id,doctor_id,patient_id,icd,tarif,visit_ts,submit_ts,referral_from_faskes,referral_from_doctor\n001,F,D,P,I10,100,2026-09-01T07:00:00+07:00,2026-09-01T08:00:00+07:00,,\n"
    frame = _csv(raw, "claims", {})
    assert frame.claim_id.iloc[0] == "001"
    assert frame.visit_ts.iloc[0] == pd.Timestamp("2026-09-01T00:00:00")


def test_extra_csv_cells_are_not_silently_shifted(files):
    lines = files["claims.csv"].splitlines()
    lines[1] += b",extra"
    files["claims.csv"] = b"\n".join(lines)
    with pytest.raises(ValueError, match="jumlah kolom"):
        load(files)


def test_conflicting_reference_snapshot_rejected(files):
    data = load(files)
    model, _, _ = run_holdout(data, cutoff="2026-09-30")
    refs = {name: frame.copy() for name, frame in data.tables.items() if name != "claims"}
    refs["faskes"].loc[0, "capacity"] += 1
    incoming = data.tables["claims"].query("submit_ts > '2026-09-30'")
    with pytest.raises(ValueError, match="bertentangan"):
        batch.predict(model, incoming, as_of=incoming.submit_ts.max(), references=refs)


def test_external_lab_flow():
    from streamlit.testing.v1 import AppTest
    from core import batch_store
    app = AppTest.from_string("from components.external_lab import render\nrender()", default_timeout=90).run()
    app.button(key="external_example").click().run()
    assert not app.exception
    assert any("pemeriksaan struktur kolom" in str(x.value) for x in app.caption)
    app.button(key="external_run").click().run()
    assert not app.exception
    assert app.session_state["external_result"][2]["evaluation_available"]
    app.button(key="external_save_model").click().run()
    assert not app.exception
    assert len(batch_store.list_models()) == 1
    app.button(key="external_to_review").click().run()
    assert not app.exception
    assert app.session_state["page"] == "batch_review"
    queue = batch_store.load_queue(app.session_state["batch_review"])
    assert len(queue["claims"]) == len(app.session_state["external_result"][1])
    cid = queue["claims"].iloc[0].claim_id
    batch_store.save_decision(queue["id"], cid, "Perlu bukti tambahan", "Periksa bukti")
    app.button(key="external_to_review").click().run()
    assert len(batch_store.load_queue(queue["id"])["events"]) == 1


def test_switching_dataset_clears_saved_predictions():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_string("from components.external_lab import render\nrender()").run(timeout=30)
    app.session_state["saved_result"] = "hasil paket sebelumnya"
    app.button(key="external_example").click().run(timeout=30)
    assert not app.exception
    assert "saved_result" not in app.session_state
