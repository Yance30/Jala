"""Evaluate a fixed legacy-family model on separately constructed scenarios."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pandas as pd

from core import batch
from core.data_quality import require_valid
from core.detect import rule_flags
from core.evaluate import expected_hits
from core.independent_scenarios import generate
from core.synthetic import DEFAULT, PERIOD_START, generate_world


def run(seeds=(31, 47, 59), capacity=100):
    if not seeds or capacity < 1:
        raise ValueError("Perlu minimal satu seed dan kapasitas positif.")
    world = generate_world(cfg=replace(DEFAULT, chronological_submissions=True))
    cutoff = PERIOD_START + pd.Timedelta(days=60)
    historical = world.claims[world.claims.submit_ts <= cutoff]
    model = batch.train(historical, world.faskes, world.affiliations, world.patients,
                        world.labels[world.labels.claim_id.isin(historical.claim_id)], cutoff=cutoff)
    runs = []
    for seed in seeds:
        case = generate(seed)
        refs = {name: getattr(case, name) for name in ("faskes", "affiliations", "patients")}
        quality = require_valid(case.claims, **refs)
        scores = batch.predict(model, case.claims, as_of=case.claims.submit_ts.max(), references=refs)
        rules = rule_flags(case.claims, tariff_caps=model.tariff_caps)
        baseline = pd.DataFrame({"claim_id": rules.index,
                                 "priority_score": rules.rule_over_cap + rules.rule_same_day_dup})
        metrics = batch.evaluate(scores, case.labels, capacity=capacity)
        aligned = case.labels.set_index("claim_id").loc[scores.claim_id]
        per_scenario = []
        for scenario, group in aligned.groupby("scenario"):
            mask = (aligned.scenario == scenario).to_numpy(dtype=int)
            caught = float(expected_hits(mask, scores.priority_score.to_numpy(), [metrics["capacity"]])[0])
            per_scenario.append(dict(scenario=scenario, n_claims=len(group), n_fraud=int(group.is_fraud.sum()),
                                     expected_reviewed_at_k=caught, fraction_reviewed=caught / len(group)))
        runs.append(dict(seed=seed, quality=quality, jala=metrics,
                         rules=batch.evaluate(baseline, case.labels, capacity=capacity), scenarios=per_scenario))
    return {"protocol": "independent-construction-v1", "training_model": model.metadata, "runs": runs,
            "mean": {key: float(np.mean([r["jala"][key] for r in runs]))
                     for key in ("auc", "average_precision", "precision_at_k", "recall_at_k")},
            "limitations": ["Separate generation code, but scenarios designed by the same project; not external expert validation.",
                            "All entities are new; snapshot contains historical training graph and the complete new batch.",
                            "Labels describe planted synthetic cases, not confirmed clinical fraud.",
                            "Seeds repeat one scenario family; no confidence interval or real-world accuracy claim.",
                            "Model is trained once and never tuned or retrained on scenario outcomes."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=Path("docs/independent-evaluation.json"))
    parser.add_argument("--capacity", type=int, default=100)
    args = parser.parse_args()
    report = run(capacity=args.capacity)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(args.json), "mean": report["mean"]}, indent=2))


if __name__ == "__main__":
    main()
