"""Read the reproducible, exploratory synthetic comparison artifact."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st


def render():
    path = Path(__file__).resolve().parents[1] / 'docs' / 'graph-ablation.json'
    if not path.exists():
        return
    with st.expander('Nilai tambah fitur jaringan: eksperimen pembanding'):
        report = json.loads(path.read_text(encoding='utf-8'))
        st.write('Perbandingan pada data sintetis, dengan fold dan kapasitas pemeriksaan yang sama. Kedua model GBM memakai pengaturan classifier yang sama.')
        capacity = st.selectbox('Kapasitas pembanding', [20, 50, 100], key='ablation_capacity')
        names = {'rules': 'Aturan sederhana', 'local_history_gbm': 'GBM klaim + riwayat peserta',
                 'full_graph_gbm': 'GBM fitur lengkap + jaringan'}
        rows = []
        for run in report['results']:
            for model, metrics in run['metrics'].items():
                precision = metrics['precision_at_k'][str(capacity)]
                rows.append({'Seed': run['seed'], 'Metode': names[model],
                             'Precision': precision, 'Recall': metrics['recall_at_k'][str(capacity)],
                             'Kasus sah ikut diperiksa (ekspektasi)': capacity * (1 - precision)})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
        st.caption('Precision dan recall memakai skala 0–1. Nilai ekspektasi memperhitungkan skor seri. Hasil retrospektif pada tiga seed sintetis; bukan akurasi data BPJS atau bukti penghematan operasional.')
        st.caption('Pembanding mempertahankan riwayat peserta. Fitur yang dihilangkan mencakup jaringan dan agregat fasilitas, sehingga selisih hasil bukan efek murni struktur graf.')
        st.download_button('Unduh rincian eksperimen pembanding', path.read_bytes(),
                           file_name='jala-graph-ablation.json', mime='application/json')
