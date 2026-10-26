"""Fixed exploratory ablation; same classifier, folds and review budgets."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.synthetic import generate_world
from core.detect import build_features, rule_flags
from core.evaluate import _cv_scores, _summarize, fold_assignment, CAVEATS

SEEDS = (2026, 2027, 2028)
LOCAL = ['f_out_region', 'f_gap_prev_h', 'f_dup_recent', 'f_ref', 'f_tarif_ratio', 'f_tarif_match_prev']


def run():
    results = []
    for seed in SEEDS:
        w = generate_world(seed)
        x = build_features(w.claims, w.faskes, w.affiliations, w.patients)
        labels = w.labels.set_index('claim_id').loc[x.index, 'is_fraud'].to_numpy(dtype=int)
        facilities = w.claims.set_index('claim_id').loc[x.index, 'faskes_id']
        folds = fold_assignment(w).reindex(facilities).to_numpy()
        rules = rule_flags(w.claims).loc[x.index]
        scores = {
            'rules': (rules.rule_over_cap + rules.rule_same_day_dup).to_numpy(dtype=float),
            'local_history_gbm': _cv_scores(x[LOCAL], labels, folds, seed),
            'full_graph_gbm': _cv_scores(x, labels, folds, seed),
        }
        results.append({'seed': seed, 'claims': len(x), 'fraud': int(labels.sum()),
                        'metrics': {name: _summarize(labels, score, ks=(20, 50, 100)) for name, score in scores.items()}})
        print('Completed seed', seed, flush=True)
    return {'local_features': LOCAL, 'full_features': list(x.columns), 'seeds': list(SEEDS),
            'limitations': CAVEATS + ['Exploratory ablation, not a new independent holdout or operational validation.',
                'Local baseline retains patient history and row-level reference lookups; removed features include network and facility aggregates. The difference is not a pure causal effect of graph structure.',
                'Same classifier settings and grouped folds for both GBMs; no tuning on these results.'],
            'results': results}


if __name__ == '__main__':
    Path('docs/graph-ablation.json').write_text(json.dumps(run(), indent=2), encoding='utf-8')
