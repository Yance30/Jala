"""Create a repeatable synthetic demo and a frozen multi-run evaluation."""
import argparse
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
from components.external_lab import example_files
from core import batch
from core.batch_store import runtime
from core.contract import MINIMAL
from core.evaluate import expected_hits
from core.import_data import load, run_holdout
from core.independent_scenarios import generate


def provenance():
    digest = hashlib.sha256()
    for path in sorted((ROOT / "core").glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return dict(runtime=runtime(), source_sha256=digest.hexdigest(),
                lock_sha256={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                             for name in ("requirements-lock.txt", "requirements-lock-win.txt")})


def frozen_evaluation(output):
    protocol = json.loads((ROOT / "docs/evaluation-protocol-v2.json").read_text(encoding="utf-8"))
    cases = [generate(seed, start=protocol["training_start"], days=85, n_routine=protocol["n_routine"])
             for seed in protocol["training_seeds"]]
    tables = {name: pd.concat([getattr(case, name) for case in cases], ignore_index=True) for name in MINIMAL}
    labels = pd.concat([case.labels for case in cases], ignore_index=True)
    runs = []
    for day in protocol["cutoff_days"]:
        cutoff = pd.Timestamp(protocol["training_start"]) + pd.Timedelta(days=day)
        claims = tables["claims"][tables["claims"].submit_ts <= cutoff]
        model = batch.train(claims, **{k: v for k, v in tables.items() if k != "claims"},
                            labels=labels[labels.claim_id.isin(claims.claim_id)], cutoff=cutoff)
        for seed in protocol["holdout_seeds"]:
            case = generate(seed, start=protocol["holdout_start"], n_routine=protocol["n_routine"])
            scored = batch.predict(model, case.claims, as_of=case.claims.submit_ts.max(),
                                   references={k: getattr(case, k) for k in MINIMAL if k != "claims"})
            aligned = case.labels.set_index("claim_id").loc[scored.claim_id]
            for capacity in protocol["capacities"]:
                metrics = batch.evaluate(scored, case.labels, capacity=capacity)
                families = []
                for family in sorted(aligned.scenario.unique()):
                    mask = aligned.scenario.eq(family).to_numpy(int)
                    hits = float(expected_hits(mask, scored.priority_score.to_numpy(), [metrics["capacity"]])[0])
                    families.append(dict(family=family, n=int(mask.sum()), reviewed=hits,
                                         fraction_reviewed=hits / mask.sum(),
                                         planted_fraud=bool(aligned.loc[aligned.scenario.eq(family), "is_fraud"].any())))
                runs.append(dict(seed=seed, cutoff=cutoff.isoformat(), metrics=metrics, families=families))
            print(f"Evaluated cutoff {day}, seed {seed}", flush=True)
    ranges = {}
    for capacity in protocol["capacities"]:
        selected = [r["metrics"] for r in runs if r["metrics"]["capacity"] == capacity]
        ranges[str(capacity)] = {key: dict(min=min(m[key] for m in selected), max=max(m[key] for m in selected))
                                for key in ("precision_at_k", "recall_at_k", "expected_false_reviews")}
    report = dict(protocol=protocol, provenance=provenance(), model_version=batch.VERSION,
                  ranges_not_confidence_intervals=ranges, runs=runs)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")


def build_pack(output):
    files = example_files()
    data = load(files)
    _, scores, report = run_holdout(data, cutoff="2026-09-30", capacity=100)
    scenario = generate(31, n_routine=500)
    scored_ids = set(scores.claim_id)
    tasks, answers = [], []
    for name in ("phantom_distributed", "legit_dialysis"):
        ids = scenario.labels.loc[scenario.labels.scenario.eq(name) & scenario.labels.claim_id.isin(scored_ids), "claim_id"]
        cid = sorted(ids)[0]
        tasks.append(dict(case_id=cid, task="Telusuri catatan pembanding, jelaskan ketidakpastian, dan catat rekomendasi beserta sumbernya."))
        answers.append(dict(case_id=cid, planted_scenario=name,
                            warning="Label pembangkit, bukan keputusan klinis. Nilai kualitas alasan dan bukti, bukan tebakan label saja."))
    tasks.append(dict(case_id="date-only", task="Validasi paket insufficient. Jelaskan mengapa skor tidak boleh ditafsirkan."))
    answers.append(dict(case_id="date-only", expected="Data belum cukup untuk dinilai; jangan mengisi jam buatan."))
    contents = {f"package/{name}": value for name, value in files.items()}
    insufficient = dict(files)
    claims = data.tables["claims"].copy()
    for column in ("visit_ts", "submit_ts"):
        claims[column] = claims[column].dt.normalize()
    insufficient["claims.csv"] = claims.to_csv(index=False).encode()
    contents.update({f"insufficient/{name}": value for name, value in insufficient.items()})
    contents["expected-results.json"] = json.dumps(dict(report=report, provenance=provenance()), indent=2).encode()
    contents["participant/tasks.json"] = json.dumps(tasks, ensure_ascii=False, indent=2).encode()
    contents["facilitator/answer-key.json"] = json.dumps(answers, ensure_ascii=False, indent=2).encode()
    contents["participant/observations.csv"] = (
        "participant_pseudonym,case_id,condition,order,start_utc,end_utc,duration_seconds,"
        "recommendation,evidence_ids,reasoning_errors,decision_changed,notes\n").encode()
    contents["README.md"] = (ROOT / "docs/review-pilot.md").read_bytes()
    manifest = {name: hashlib.sha256(value).hexdigest() for name, value in sorted(contents.items())}
    contents["manifest.json"] = json.dumps(manifest, indent=2).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, raw in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw)
    print(f"Created {output}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()
    if args.evaluate:
        frozen_evaluation(ROOT / "docs/evaluation-v2.json")
    build_pack(ROOT / "artifacts/jala-review-pack.zip")
