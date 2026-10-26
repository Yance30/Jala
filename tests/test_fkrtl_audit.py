import io
import zipfile

import pandas as pd

from scripts.audit_fkrtl_source import audit


def test_audit_counts_relationships_without_exporting_identifiers(tmp_path):
    frames = {
        '202403_fkrtl.dta': pd.DataFrame(dict(PSTV01=['secret-a', 'secret-b'], FKL02=['v1', 'v2'],
            FKL03=pd.to_datetime(['2024-01-02', '2024-01-02']),
            FKL04=pd.to_datetime(['2024-01-03', '2024-01-01']),
            FKL18=['A', ''], FKL47=[100., -1.], FKL48=[90., -1.])),
        '202405_diagnosissekunder.dta': pd.DataFrame(dict(FKL02=['v1', 'v1', 'orphan'], FKL24=['A', 'B', 'C'])),
        '2015202401_kepesertaan.dta': pd.DataFrame(dict(PSTV01=['secret-a', 'secret-a'], PSTV16=[2023, 2024], PSTV10=[1, 1])),
    }
    path = tmp_path / 'source.zip'
    with zipfile.ZipFile(path, 'w') as z:
        for name, frame in frames.items():
            buf = io.BytesIO()
            frame.to_stata(buf, write_index=False, version=118)
            z.writestr('2025/Data Sampel Reguler Edisi 2025/data/' + name, buf.getvalue())
    report = audit(path)
    visits = report['tables']['202403_fkrtl.dta']
    assert visits['rows'] == 2 and visits['missing']['FKL18'] == 1
    assert visits['negative_costs']['FKL47'] == 1
    assert visits['discharge_before_arrival'] == 1
    diagnoses = report['tables']['202405_diagnosissekunder.dta']
    assert diagnoses['unmatched_rows'] == 1
    assert diagnoses['duplicate_key_rows'] == 1  # expected one-to-many, not duplicate visits
    members = report['tables']['2015202401_kepesertaan.dta']
    assert members['fkrtl_participants_missing_from_membership'] == 1
    assert members['duplicate_key_rows'] == 1  # do not blindly join on participant alone
    assert 'secret-a' not in str(report) and 'v1' not in str(report)
