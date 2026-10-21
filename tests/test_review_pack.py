import hashlib
import json
from pathlib import Path
import zipfile

from core.batch import VERSION


def test_review_pack_manifest_version_and_tasks():
    root = Path(__file__).resolve().parents[1]
    with zipfile.ZipFile(root / 'artifacts/jala-review-pack.zip') as archive:
        assert archive.testzip() is None
        manifest = json.loads(archive.read('manifest.json'))
        assert all(hashlib.sha256(archive.read(name)).hexdigest() == digest
                   for name, digest in manifest.items())
        expected = json.loads(archive.read('expected-results.json'))
        assert expected['report']['model']['version'] == VERSION
        tasks = json.loads(archive.read('participant/tasks.json'))
        assert len(tasks) == 3 and tasks[-1]['case_id'] == 'date-only'
        assert len(archive.read('participant/observations.csv').splitlines()) == 1
    evaluation = json.loads((root / 'docs/evaluation-v2.json').read_text(encoding='utf-8'))
    assert evaluation['model_version'] == VERSION
    assert len(evaluation['runs']) == 18  # six seed/cutoff combinations, three capacities
