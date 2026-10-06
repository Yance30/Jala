"""Display names for JALA's typology keys; internal model keys stay unchanged."""

LABELS = {
    "Phantom Billing": "Phantom Billing (Klaim Palsu)",
    "Repeat Billing": "Repeat Billing",
    "Self-Referral": "Rujukan tidak sesuai (Self-referral)",
}


def label(value: str) -> str:
    return LABELS.get(value, value)
