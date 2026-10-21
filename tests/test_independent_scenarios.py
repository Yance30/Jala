import ast
import inspect

import pandas as pd

from core import independent_scenarios
from core.data_quality import require_valid
from core.detect import build_features


def test_separate_generator_is_deterministic_and_has_no_detector_dependency():
    source = ast.parse(inspect.getsource(independent_scenarios))
    modules = [n.module or "" for n in ast.walk(source) if isinstance(n, ast.ImportFrom)]
    assert not any(name.startswith("core") for name in modules)
    a, b = independent_scenarios.generate(11), independent_scenarios.generate(11)
    pd.testing.assert_frame_equal(a.claims, b.claims)
    assert require_valid(a.claims, a.faskes, a.affiliations, a.patients)["passed"]
    assert "is_fraud" not in a.claims
    assert set(a.labels.scenario) >= {"repeat_delayed", "phantom_distributed", "selfref_oneway", "legit_dialysis"}


def test_delayed_rebilling_uses_different_timing_and_custom_tariff_is_used():
    case = independent_scenarios.generate(17)
    delayed = case.labels.query("scenario == 'repeat_delayed'").claim_id
    x = build_features(case.claims, case.faskes, case.affiliations, case.patients)
    # No other routine visit can create a recent duplicate in most planted delayed episodes.
    assert (x.loc[delayed, "f_gap_prev_h"] > 48).mean() > .5
    caps = {"I10": 500000, "E11.9": 600000, "N18.6": 2400000}
    custom = build_features(case.claims, case.faskes, case.affiliations, case.patients, tariff_caps=caps)
    pd.testing.assert_series_equal(custom.f_tarif_ratio, x.f_tarif_ratio / 2)
