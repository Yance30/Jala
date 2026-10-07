"""Verify each pinned lock still satisfies the ranges declared in requirements.txt.

Usage: python scripts/check_lock.py requirements-lock.txt [requirements-lock-win.txt ...]
Exits non-zero (listing every drift) when a lock is stale, so CI fails if
requirements.txt is bumped without regenerating the lock.
"""
from __future__ import annotations

import sys
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "requirements.txt"


def _read_ranges(path: Path) -> list[Requirement]:
    reqs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            reqs.append(Requirement(line))
    return reqs


def _read_pins(path: Path) -> dict[str, Version]:
    pins = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        req = Requirement(line)
        pins[req.name.lower().replace("_", "-")] = Version(req.specifier.__str__().lstrip("=") or "0")
    return pins


def check(lock_path: Path) -> list[str]:
    pins = _read_pins(lock_path)
    problems = []
    for req in _read_ranges(BASE):
        key = req.name.lower().replace("_", "-")
        if key not in pins:
            problems.append(f"{lock_path.name}: {req.name} tidak ada di lock")
            continue
        if not req.specifier.contains(pins[key], prereleases=True):
            problems.append(f"{lock_path.name}: {req.name}=={pins[key]} tidak memenuhi '{req}'")
    return problems


def main() -> int:
    locks = [ROOT / a for a in sys.argv[1:]] or [ROOT / "requirements-lock.txt"]
    all_problems: list[str] = []
    for lock in locks:
        if not lock.exists():
            all_problems.append(f"lock tidak ditemukan: {lock}")
            continue
        all_problems.extend(check(lock))
    if all_problems:
        print("Lock basi terhadap requirements.txt:")
        for p in all_problems:
            print(f"  - {p}")
        print("Regenerasi: python scripts/resolve_runtime_lock.py --platform linux|windows")
        return 1
    print(f"OK: {len(locks)} lock memenuhi {BASE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
