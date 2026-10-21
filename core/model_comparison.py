"""Frozen temporal challenger protocol; no hyperparameter search on test outcomes."""
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from core import batch
from core.evaluate import expected_hits
from core.independent_scenarios import generate
from core.synthetic import DEFAULT, PERIOD_START, generate_world

DEVELOPMENT_SEEDS = (101, 211)
HOLDOUT_SEEDS = (809, 811)
CUTOFF_DAYS = (45, 60, 75)


def run():
    world = generate_world(cfg=replace(DEFAULT, chronological_submissions=True))
    development = [generate(s, start="2026-07-01", days=85, n_routine=1000) for s in DEVELOPMENT_SEEDS]
    frames = {name: pd.concat([getattr(w, name) for w in [world] + development], ignore_index=True)
              for name in ("claims", "faskes", "patients", "affiliations")}
    labels = pd.concat([w.labels[["claim_id", "is_fraud"]] for w in [world] + development], ignore_index=True)
    results = []
    for day in CUTOFF_DAYS:
        cutoff = PERIOD_START + pd.Timedelta(days=day)
        models = {}
        for name, tables, outcomes, mode in (
            ("original", {k: getattr(world, k) for k in frames}, world.labels, "base"),
            ("expanded_base", frames, labels, "base"), ("temporal", frames, labels, "temporal")
        ):
            history = tables["claims"][tables["claims"].submit_ts <= cutoff]
            models[name] = batch.train(history, **{k: v for k, v in tables.items() if k != "claims"},
                                       labels=outcomes[outcomes.claim_id.isin(history.claim_id)],
                                       cutoff=cutoff, feature_set=mode)
        for seed in HOLDOUT_SEEDS:
            case = generate(seed, start="2026-10-05")
            refs = {k: getattr(case, k) for k in ("faskes", "patients", "affiliations")}
            for name, model in models.items():
                scored = batch.predict(model, case.claims, as_of=case.claims.submit_ts.max(), references=refs)
                aligned = case.labels.set_index("claim_id").loc[scored.claim_id]
                per_case = []
                for scenario in sorted(aligned.scenario.unique()):
                    mask = aligned.scenario.eq(scenario).to_numpy(dtype=int)
                    hits = expected_hits(mask, scored.priority_score.to_numpy(), [100, 300])
                    per_case.append(dict(scenario=scenario, n_claims=int(mask.sum()),
                                         reviewed_at_100=float(hits[0]), reviewed_at_300=float(hits[1])))
                top100 = batch.evaluate(scored, case.labels, capacity=100)
                top300 = batch.evaluate(scored, case.labels, capacity=300)
                results.append(dict(cutoff_day=day, seed=seed, model=name, metadata=model.metadata,
                                    top100=top100, top300=top300, scenarios=per_case,
                                    false_reviews_at_300=300 - top300["expected_fraud_at_k"]))
    summary = {}
    for name in ("original", "expanded_base", "temporal"):
        selected = [r for r in results if r["model"] == name]
        summary[name] = {key: float(np.mean([r["top100"][key] for r in selected]))
                         for key in ("auc", "average_precision", "recall_at_k", "precision_at_k")}
        summary[name]["false_reviews_at_300"] = float(np.mean([r["false_reviews_at_300"] for r in selected]))
    pairs = [(next(r for r in results if r["model"] == "temporal" and r["seed"] == seed and r["cutoff_day"] == day),
              next(r for r in results if r["model"] == "expanded_base" and r["seed"] == seed and r["cutoff_day"] == day))
             for day in CUTOFF_DAYS for seed in HOLDOUT_SEEDS]
    gate = (summary["temporal"]["precision_at_k"] > summary["expanded_base"]["precision_at_k"]
            and all(a["top100"]["precision_at_k"] >= b["top100"]["precision_at_k"] for a, b in pairs)
            and all(a["false_reviews_at_300"] <= b["false_reviews_at_300"] for a, b in pairs))
    return dict(protocol="temporal-challenger-v1", development_seeds=list(DEVELOPMENT_SEEDS),
                holdout_seeds=list(HOLDOUT_SEEDS), cutoff_days=list(CUTOFF_DAYS), summary=summary,
                promotion_gate_passed=bool(gate), runs=results,
                limitations=["Same scenario templates in development and holdout, disjoint seeds/entities only.",
                             "No tuning on these holdout outcomes. Old evaluation seeds 31/47/59 are excluded.",
                             "All models see the same complete closed test batch; reference tables are static.",
                             "Promotion gate is experimental; production default is not changed automatically.",
                             "Clinical appropriateness and duplicate payment cannot be established from these fields."])


if __name__ == "__main__":
    report = run()
    path = Path("docs/model-comparison.json")
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"summary": report["summary"], "promotion_gate_passed": report["promotion_gate_passed"]}, indent=2))
