"""Read regular Stata tables locally; export aggregate quality metrics only."""
import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd


def audit(source):
    specs = [
        ('202403_fkrtl.dta', 'FKL02', ['PSTV01', 'FKL02', 'FKL03', 'FKL04', 'FKL18', 'FKL47', 'FKL48']),
        ('202405_diagnosissekunder.dta', 'FKL02', ['FKL02', 'FKL24']),
        ('2015202401_kepesertaan.dta', 'PSTV01', ['PSTV01', 'PSTV16', 'PSTV10']),
    ]
    result = {'scope': 'Full row scan, regular tables only; no fraud labels inferred', 'tables': {}}
    visits, patients = set(), set()
    with zipfile.ZipFile(source) as archive:
        for filename, key, columns in specs:
            names = [n for n in archive.namelist() if '/Data Sampel Reguler Edisi 2025/data/' in n and n.endswith('/' + filename)]
            if len(names) != 1:
                raise ValueError('Expected one regular source: ' + filename)
            stats = {'rows': 0, 'missing': {}, 'duplicate_key_rows': 0, 'dates': {}, 'negative_costs': {}, 'unmatched_rows': 0}
            seen = set()
            with tempfile.TemporaryFile() as temporary:
                with archive.open(names[0]) as raw:
                    shutil.copyfileobj(raw, temporary)
                temporary.seek(0)
                with pd.read_stata(temporary, iterator=True, chunksize=100000, convert_categoricals=False, columns=columns) as reader:
                    for frame in reader:
                        stats['rows'] += len(frame)
                        for column in columns:
                            series = frame[column]
                            missing = series.isna() | series.astype(str).str.strip().eq('')
                            stats['missing'][column] = stats['missing'].get(column, 0) + int(missing.sum())
                        ids = frame[key].dropna()
                        stats['duplicate_key_rows'] += int(ids.duplicated().sum()) + len(set(ids) & seen)
                        seen.update(ids)
                        if key == 'FKL02' and 'FKL47' in frame:
                            visits.update(ids)
                            patients.update(frame.PSTV01.dropna())
                            for col in ('FKL03', 'FKL04'):
                                dates = frame[col].dropna()
                                if len(dates):
                                    old = stats['dates'].get(col, [str(dates.min()), str(dates.max())])
                                    stats['dates'][col] = [min(old[0], str(dates.min())), max(old[1], str(dates.max()))]
                            for col in ('FKL47', 'FKL48'):
                                stats['negative_costs'][col] = stats['negative_costs'].get(col, 0) + int((frame[col] < 0).sum())
                            stats['discharge_before_arrival'] = stats.get('discharge_before_arrival', 0) + int((frame.FKL04 < frame.FKL03).sum())
                            stats['billed_differs_verified'] = stats.get('billed_differs_verified', 0) + int((frame.FKL47.notna() & frame.FKL48.notna() & frame.FKL47.ne(frame.FKL48)).sum())
                        elif key == 'FKL02':
                            stats['unmatched_rows'] += int((frame.FKL02.notna() & ~frame.FKL02.isin(visits)).sum())
            stats['unique_nonmissing_keys'] = len(seen)
            if key == 'PSTV01':
                stats['fkrtl_participants_missing_from_membership'] = len(patients - seen)
                stats['fkrtl_unique_participants'] = len(patients)
            result['tables'][filename] = stats
            print(filename, stats['rows'], 'rows scanned', flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.source)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
