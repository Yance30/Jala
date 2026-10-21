"""Baseline versus the upcoding candidate on a planted diagnosis-mix family.

The upcoding family and the features that detect it were designed by the same
team, so this measures whether a known blind spot closes, not whether the model
generalises to upcoding as it occurs in practice.
"""
import json
from pathlib import Path

import pandas as pd

from core import batch
from core.evaluate import expected_hits
from core.independent_scenarios import generate

TARIFF_CAPS = {"I10": 250000, "E11.9": 300000, "N18.6": 1200000, "I50": 2400000}
TRAIN_SEEDS = (101, 211)
TEST_SEEDS = (1201, 1213)
CUTOFF = "2026-09-01"
CAPACITIES = (50, 100, 200, 300)
FAMILIES = ("upcoding", "phantom_distributed", "repeat_delayed", "selfref_oneway")
BENIGN = ("legit_severe", "legit_dialysis", "legit_transfer", "legit_office_batch", "routine")


def run():
    cases = [generate(s, start="2026-07-01", days=85, n_routine=1000, upcoding=True) for s in TRAIN_SEEDS]
    tables = {k: pd.concat([getattr(c, k) for c in cases], ignore_index=True)
              for k in ("claims", "faskes", "patients", "affiliations")}
    labels = pd.concat([c.labels[["claim_id", "is_fraud"]] for c in cases], ignore_index=True)
    history = tables["claims"][tables["claims"].submit_ts <= pd.Timestamp(CUTOFF)]
    references = {k: v for k, v in tables.items() if k != "claims"}
    models = {}
    for mode in ("base", "upcoding"):
        models[mode] = batch.train(history, **references,
                                   labels=labels[labels.claim_id.isin(history.claim_id)],
                                   cutoff=CUTOFF, tariff_caps=TARIFF_CAPS, feature_set=mode)
        print(f"Trained: {mode}", flush=True)

    results = []
    for seed in TEST_SEEDS:
        case = generate(seed, start="2026-10-05", upcoding=True)
        refs = {k: getattr(case, k) for k in ("faskes", "patients", "affiliations")}
        for mode, model in models.items():
            scores = batch.predict(model, case.claims, as_of=case.claims.submit_ts.max(), references=refs)
            aligned = case.labels.set_index("claim_id").loc[scores.claim_id]
            priority = scores.priority_score.to_numpy()
            families = []
            for family in FAMILIES + BENIGN:
                target = aligned.scenario.eq(family).to_numpy(int)
                if not target.sum():
                    continue
                hits = expected_hits(target, priority, list(CAPACITIES))
                families.append(dict(family=family, labelled=bool(family in FAMILIES), n=int(target.sum()),
                                     recall={str(k): float(h / target.sum()) for k, h in zip(CAPACITIES, hits)}))
            results.append(dict(seed=seed, feature_set=mode, model=model.metadata,
                                metrics={str(k): batch.evaluate(scores, case.labels, capacity=k) for k in CAPACITIES},
                                families=families))
    return dict(protocol="upcoding-candidate-v1", cutoff=CUTOFF, tariff_caps=TARIFF_CAPS,
                train_seeds=list(TRAIN_SEEDS), test_seeds=list(TEST_SEEDS), runs=results,
                limitations=[
                    "The upcoding family and the two candidate features were designed by the same team; "
                    "this shows a known blind spot closing, not generalisation to real upcoding.",
                    "Planted pattern is one clinic billing I50 for patients whose own record is routine I10. "
                    "Real upcoding varies in code pair, setting, and documentation.",
                    "Synthetic independent-scenario data only; not operational BPJS validation and no clinical review.",
                    "No hyperparameter tuning on the test seeds; baseline graph + GBM settings unchanged.",
                    "legit_severe rows are counted with the same recall formula but are benign; "
                    "a non-zero value there is a false-review cost, not detection."])


if __name__ == "__main__":
    report = run()
    Path("docs/upcoding-evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Saved docs/upcoding-evaluation.json", flush=True)
