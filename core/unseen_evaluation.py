"""Leave one planted fraud family out of training, before feature construction."""
import json
from pathlib import Path

import pandas as pd

from core import batch
from core.evaluate import expected_hits
from core.independent_scenarios import generate

FAMILIES = ("phantom_distributed", "repeat_delayed", "selfref_oneway")
TRAIN_SEEDS = (101, 211)
TEST_SEEDS = (1201, 1213)


def training_tables(cases, excluded=None):
    labels = pd.concat([c.labels for c in cases], ignore_index=True)
    labels = labels[labels.scenario.ne(excluded)].copy()
    tables = {k: pd.concat([getattr(c, k) for c in cases], ignore_index=True)
              for k in ("claims", "faskes", "patients", "affiliations")}
    # Remove held-out claims entirely; masking labels would leak their graph structure.
    tables["claims"] = tables["claims"][tables["claims"].claim_id.isin(labels.claim_id)].copy()
    return tables, labels


def run():
    cases = [generate(s, start="2026-07-01", n_routine=1000) for s in TRAIN_SEEDS]
    results = []
    for excluded in (None,) + FAMILIES:
        tables, labels = training_tables(cases, excluded)
        model = batch.train(**tables, labels=labels[["claim_id", "is_fraud"]], cutoff="2026-10-01")
        print(f"Trained: {excluded or 'all_families'}", flush=True)
        for seed in TEST_SEEDS:
            case = generate(seed, start="2026-10-05")
            scores = batch.predict(model, case.claims, as_of=case.claims.submit_ts.max(),
                                   references={k: getattr(case, k) for k in ("faskes", "patients", "affiliations")})
            aligned = case.labels.set_index("claim_id").loc[scores.claim_id]
            families = []
            for family in FAMILIES:
                target = aligned.scenario.eq(family).to_numpy(int)
                hits = expected_hits(target, scores.priority_score.to_numpy(), [50, 100, 300])
                families.append(dict(family=family, n=int(target.sum()),
                                     recall={str(k): float(h / target.sum()) for k, h in zip((50, 100, 300), hits)}))
            results.append(dict(excluded_family=excluded, seed=seed, model=model.metadata,
                                metrics={str(k): batch.evaluate(scores, case.labels, capacity=k) for k in (50, 100, 300)},
                                families=families))
    return dict(protocol="leave-one-family-out-v1", train_seeds=list(TRAIN_SEEDS), test_seeds=list(TEST_SEEDS),
                runs=results, limitations=["Synthetic planted families from one generator, not operational validation.",
                "Only independent scenario data used for training; legacy generator excluded to avoid family overlap.",
                "Excluded claims removed before features; static entity references retained.",
                "No hyperparameter tuning on test seeds; baseline graph + GBM only."])


if __name__ == "__main__":
    report = run()
    Path("docs/unseen-evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Saved docs/unseen-evaluation.json", flush=True)
