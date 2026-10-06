"""Add traceable demo context to tabular downloads."""
from datetime import datetime

import pandas as pd

from data.mock_data import FOOTER_CUTOFF, QUARTER


def with_demo_context(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy whose rows carry the period, synthetic status, and export time."""
    result = frame.copy()
    result["lingkungan_data"] = "Data sintetis; prototipe"
    result["periode_data"] = QUARTER
    result["batas_data"] = FOOTER_CUTOFF
    result["waktu_ekspor"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return result


def csv_bytes(frame: pd.DataFrame) -> bytes:
    """Produce an Excel-friendly CSV with traceability fields."""
    return with_demo_context(frame).to_csv(index=False).encode("utf-8-sig")
