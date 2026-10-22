"""Small, explicit release identity for the About page."""
import os
from pathlib import Path
import re
import subprocess

RELEASE = "2026.10.22"
ROOT = Path(__file__).resolve().parents[1]


def build_identity():
    """Never substitute a known remote commit for the running checkout."""
    supplied = os.environ.get("JALA_BUILD_COMMIT", "").strip()
    if re.fullmatch(r"[0-9a-fA-F]{7,40}", supplied):
        return f"Commit build: {supplied[:7].lower()} (metadata deployment)"
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
            text=True, check=True, timeout=2,
        ).stdout.strip()
        if not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            return "Commit tidak tersedia"
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            cwd=ROOT, capture_output=True, text=True, check=True, timeout=2,
        ).stdout.strip()
        suffix = " — ada perubahan lokal; bukan salinan persis commit" if status else ""
        return f"Commit checkout: {sha[:7]}{suffix}"
    except (OSError, subprocess.SubprocessError):
        return "Commit tidak tersedia"
