"""Weekly synthetic replay for time-to-first-detection comparisons.

This is an evaluation tool, not the live detector. Each week's claims are scored after
that week's batch closes; the GBM is fit only on earlier weeks. All results remain
synthetic because the baseline rules and labels are generated in this repository.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from core.detect import build_features, rule_flags
from core.synthetic import SEED, World, generate_world


def weekly_replay(world: World, capacity_per_week: int = 500) -> dict:
    claims = world.claims.sort_values("submit_ts").reset_index(drop=True)
    labels = world.labels.set_index("claim_id")
    start = claims.submit_ts.min().normalize()
    end = claims.submit_ts.max().normalize() + pd.Timedelta(days=1)
    boundaries = pd.date_range(start, end, freq="7D")
    if len(boundaries) == 0 or boundaries[0] != start:
        boundaries = boundaries.insert(0, start)
    if boundaries[-1] < end:
        boundaries = boundaries.append(pd.DatetimeIndex([end]))

    history: list[dict] = []
    first: dict[str, dict] = {}
    capacity_grid = list(range(0, 1201, 5))
    for wi, (lo, hi) in enumerate(zip(boundaries[:-1], boundaries[1:]), start=1):
        current = claims[(claims.submit_ts >= lo) & (claims.submit_ts < hi)]
        if current.empty:
            continue
        prior = claims[claims.submit_ts < lo]
        snapshot = claims[claims.submit_ts < hi]
        x_all = build_features(snapshot, world.faskes, world.affiliations, world.patients)
        cur_ids = set(current.claim_id)
        x_test = x_all.loc[x_all.index.isin(cur_ids)]
        y_train = labels.loc[prior.claim_id, "is_fraud"].to_numpy(dtype=int)
        # Training features are rebuilt from the historical prefix only so current-week
        # claims cannot alter features for training rows.
        x_train = build_features(prior, world.faskes, world.affiliations, world.patients) if not prior.empty else pd.DataFrame()
        train_ids = list(x_train.index)
        graph_available = len(train_ids) > 0 and len(np.unique(y_train)) == 2
        if graph_available:
            model = HistGradientBoostingClassifier(max_depth=4, learning_rate=.08, max_iter=150,
                                                   class_weight="balanced", random_state=world.seed)
            model.fit(x_train, y_train)
            graph_score = model.predict_proba(x_test)[:, 1]
        else:
            graph_score = np.zeros(len(x_test), dtype=float)
        rules = rule_flags(current).loc[x_test.index]
        rule_score = (rules.rule_over_cap + rules.rule_same_day_dup).to_numpy(dtype=float)
        y = labels.loc[x_test.index, "is_fraud"].to_numpy(dtype=int)
        group = labels.loc[x_test.index, "group"].astype(str).to_numpy()
        def captured(score):
            order = np.argsort(-score, kind="stable")[:capacity_per_week]
            return set(group[order][y[order] == 1])

        def capacity_curve(score):
            order = np.argsort(-score, kind="stable")
            hits = np.r_[0, np.cumsum(y[order])]
            return [int(hits[min(k, len(y))]) for k in capacity_grid]

        caught_graph = captured(graph_score) if graph_available else set()
        caught_rules = captured(rule_score)
        active_rings = sorted(set(group[y == 1]))
        for ring in active_rings:
            item = first.setdefault(ring, {"ring": ring, "typology": str(labels.loc[
                labels.group == ring, "typology"].iloc[0]), "first_week_active": wi})
            if ring in caught_graph and "jala_week" not in item:
                item["jala_week"] = wi
                item["jala_date"] = lo.date().isoformat()
            if ring in caught_rules and "rules_week" not in item:
                item["rules_week"] = wi
                item["rules_date"] = lo.date().isoformat()
        history.append({"week": wi, "start": lo.date().isoformat(), "n_claims": int(len(current)),
                        "n_fraud": int(y.sum()), "capacity": int(capacity_per_week),
                        "rings_active": len(active_rings), "rings_caught_jala": len(caught_graph),
                        "rings_caught_rules": len(caught_rules), "jala_model_available": graph_available,
                        "capacity_curve": {"capacity_per_week": capacity_grid,
                                           "fraud_caught_jala": capacity_curve(graph_score) if graph_available else [0] * len(capacity_grid),
                                           "fraud_caught_rules": capacity_curve(rule_score)}})

    rows = []
    for ring, item in sorted(first.items()):
        jala_week, rules_week = item.get("jala_week"), item.get("rules_week")
        rows.append({**item, "weeks_earlier": (rules_week - jala_week)
                     if jala_week is not None and rules_week is not None else None})
    return {"meta": {"seed": world.seed, "capacity_claims_per_week": capacity_per_week,
                      "n_claims": int(len(claims)), "n_weeks": len(history),
                      "method": "weekly batch; GBM fit only on earlier claims; rules scored on the current batch",
                      "caveat": "Retrospective synthetic replay. The feature builder sees the complete current-week batch; "
                                "this is not a live or prospective BPJS result."},
            "weekly": history, "capacity_grid": capacity_grid, "rings": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--capacity-per-week", type=int, default=500)
    parser.add_argument("--json", default="docs/temporal_impact.json")
    args = parser.parse_args()
    result = weekly_replay(generate_world(SEED), args.capacity_per_week)
    path = Path(args.json)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {path}: {len(result['rings'])} synthetic rings over {result['meta']['n_weeks']} weeks")


if __name__ == "__main__":
    main()
