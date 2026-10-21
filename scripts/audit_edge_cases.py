"""Read-only reproductions for the 2026-10-20 code audit; no database writes."""
from pathlib import Path
import ast
from collections import Counter
import json
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from tests.test_detect import _tiny
from core.detect import build_features
from core.data_quality import inspect
from core.batch import _features
from core.upcoding_features import _tariff_jump, indicators
from core.review_queue import prepare, record, export
from core.csv_export import safe_csv


def inventory():
    root = Path(__file__).resolve().parents[1]
    names = sorted(set(subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
    ).decode().split("\0")) - {""})
    counts, errors, sizes = Counter(), [], []
    for name in names:
        path = root / name
        if not path.is_file():
            continue
        # Test-run artifacts are not project source.
        if path.parts and name.startswith(".audit-test-tmp/"):
            continue
        raw = path.read_bytes()
        counts[path.suffix or path.name] += 1
        if path.suffix in (".py", ".md", ".json", ".toml", ".yml", ".txt", ".bat", ".ini"):
            try:
                text = raw.decode("utf-8-sig")
                if path.suffix == ".py":
                    ast.parse(text, filename=name)
                    sizes.append((len(text.splitlines()), name))
                # Devcontainer accepts JSON with comments (JSONC).
                if path.suffix == ".json" and name != ".devcontainer/devcontainer.json":
                    json.loads(text)
            except Exception as error:
                errors.append((name, str(error)))
    print("INVENTORY", json.dumps(dict(counts=counts, parse_errors=errors,
                                     largest_python=sorted(sizes, reverse=True)[:10])), flush=True)


def main():
    inventory()
    rows = [
        ("C1", "A", "d1", "p1", "I10", 0, "2026-07-01 09:00", "2026-07-01 10:00", None, None),
        ("C2", "B", "d1", "p1", "I10", 0, "2026-07-01 09:00", "2026-07-01 10:00", None, None),
    ]
    tables = _tiny(rows)
    print("ZERO_TARIFF_VALIDATION", inspect(*tables)["passed"], flush=True)
    try:
        result = _features(*tables, {"I10": 250000})
        print("ZERO_TARIFF_FEATURES_FINITE", not result.isna().any().any(), flush=True)
    except ValueError as error:
        print("ZERO_TARIFF_FEATURE_ERROR", str(error), flush=True)
    claims, fac, aff, patients = _tiny([
        tuple(100 if i == 5 else value for i, value in enumerate(row))
        for row in rows
    ])
    a = build_features(claims, fac, aff, patients)
    b = build_features(claims.iloc[::-1], fac, aff, patients)
    print("TIE_ORDER_A", a[["f_gap_prev_h", "f_dup_cross"]].to_dict("index"), flush=True)
    print("TIE_ORDER_B", b[["f_gap_prev_h", "f_dup_cross"]].to_dict("index"), flush=True)
    pd.testing.assert_frame_equal(a.sort_index(), b.sort_index())
    scores = pd.DataFrame({"claim_id": ["C1"], "priority_score": [90]})
    queue = prepare(claims, scores, {"version": "audit"})
    record(queue, "C1", "Perlu bukti tambahan", "=1+1", "tester")
    print("CSV_FORMULA_ESCAPED", "'=1+1" in safe_csv(export(queue)), flush=True)
    claims.loc[1, "visit_ts"] = pd.Timestamp("2026-07-02 09:00")
    claims.loc[:, "tarif"] = [100, 300]
    jump = _tariff_jump(claims)[1]
    print("TARIFF_ACTUAL_INCREASE", 2.0, "FEATURE", jump, "EXPLANATION",
          indicators(pd.Series({"f_icd_mix_z": 0, "f_pat_tarif_jump": jump})), flush=True)


if __name__ == "__main__":
    main()
