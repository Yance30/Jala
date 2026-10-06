"""Label-aware synthetic evaluations for the verifier feedback loop."""
from __future__ import annotations

import numpy as np

from core import feedback
from core.live import AUTO_FLAG, Live


def evaluate_wrong_dismissal(live: Live, world, error_rates=(.1, .2), repeats: int = 100,
                             seed: int = 2026) -> dict:
    """Monte Carlo wrong-dismissal sensitivity; labels are evaluation-only."""
    lab = world.labels.set_index("claim_id")
    fraud_share = {c["id"]: float(lab.loc[c["idx"]].is_fraud.mean()) for c in live.clusters}
    is_fraud = {cid: share >= .5 for cid, share in fraud_share.items()}
    flagged = [c["id"] for c in live.clusters if c["score"] >= AUTO_FLAG]

    def precision(current):
        queue = [c for c in current.clusters if c["score"] >= AUTO_FLAG]
        return sum(is_fraud[c["id"]] for c in queue) / len(queue) if queue else 1.0

    rng = np.random.default_rng(seed)
    scenarios = []
    for rate in error_rates:
        precisions, demotions, dismissed_fraud = [], [], []
        for _ in range(repeats):
            decisions = {}
            for cid in flagged:
                if not is_fraud[cid] or rng.random() < rate:
                    decisions = feedback.record(decisions, cid, "dismiss", at="sim")
            current = feedback.adjust(live, decisions)
            precisions.append(precision(current))
            demotions.append(sum(is_fraud[c["id"]] and c["score"] < live.by_id[c["id"]]["score"]
                                 for c in current.clusters))
            dismissed_fraud.append(sum(is_fraud[cid] for cid in decisions))
        scenarios.append({"error_rate": float(rate), "repeats": repeats,
                          "precision_mean": float(np.mean(precisions)),
                          "precision_p10": float(np.quantile(precisions, .1)),
                          "precision_p90": float(np.quantile(precisions, .9)),
                          "fraud_clusters_demoted_mean": float(np.mean(demotions)),
                          "fraud_clusters_dismissed_mean": float(np.mean(dismissed_fraud))})
    return {"baseline_precision": precision(live), "n_flagged_clusters": len(flagged),
            "n_fraud_flagged": sum(is_fraud[cid] for cid in flagged), "scenarios": scenarios,
            "caveat": "Simulasi sintetis; tingkat salah 10%/20% diterapkan hanya pada klaster fraud yang ditinjau."}
