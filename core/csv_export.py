"""Spreadsheet-safe CSV output. Source values are never mutated."""
import pandas as pd


def safe_csv(frame: pd.DataFrame) -> str:
    def text_cell(value):
        if isinstance(value, str) and value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
            return "'" + value
        if isinstance(value, str) and value.startswith(("\t", "\r", "\n")):
            return "'" + value
        return value
    return frame.map(text_cell).to_csv(index=False)
