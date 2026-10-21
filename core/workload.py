"""Conservative prototype limits; not a production throughput guarantee."""
import numpy as np
import pandas as pd

MAX_CLAIMS = 30_000
MAX_REFERENCE_ROWS = 50_000
MAX_EPISODE_ROWS = 500
MAX_DOCTOR_WINDOW = 500


def require_budget(claims, **references):
    if len(claims) > MAX_CLAIMS:
        raise ValueError(f"Snapshot dibatasi {MAX_CLAIMS:,} klaim termasuk riwayat; gunakan periode lebih pendek.")
    if any(len(frame) > MAX_REFERENCE_ROWS for frame in references.values()):
        raise ValueError(f"Tabel referensi dibatasi {MAX_REFERENCE_ROWS:,} baris.")
    if not {"patient_id", "doctor_id", "visit_ts"}.issubset(claims):
        return
    if claims.groupby("patient_id").size().max() > MAX_EPISODE_ROWS:
        raise ValueError(f"Snapshot dibatasi {MAX_EPISODE_ROWS} klaim per peserta.")
    if not pd.api.types.is_datetime64_any_dtype(claims.visit_ts):
        return
    for _, group in claims.groupby("doctor_id"):
        times = np.sort(group.visit_ts.astype("int64").to_numpy())
        width = pd.Timedelta(minutes=30).value
        sizes = np.searchsorted(times, times + width, side="right") - np.searchsorted(times, times - width)
        if len(sizes) and sizes.max() > MAX_DOCTOR_WINDOW:
            raise ValueError(f"Kepadatan melebihi {MAX_DOCTOR_WINDOW} klaim per dokter dalam jendela ±30 menit.")
