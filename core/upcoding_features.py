"""Experimental diagnosis-mix and per-patient tariff-jump indicators.

Upcoding usually stays inside the tariff ceiling, so cap-based rules never fire.
These are observable associations between billed codes and peer practice, not
clinical findings: nothing here establishes that care was inappropriate.
"""
import numpy as np
import pandas as pd

from core.detect import assert_no_labels

UPCODING_FEATURES = ["f_icd_mix_z", "f_pat_tarif_jump"]


def _mix_z(claims, faskes):
    """How far a facility's share of one code sits from same-type peers billing the same code."""
    counts = claims.groupby(["faskes_id", "icd"]).size().unstack(fill_value=0)
    share = counts.div(counts.sum(axis=1), axis=0)
    peers = share.groupby(faskes.set_index("faskes_id")["type"].reindex(share.index))
    z = ((share - peers.transform("mean")) / (peers.transform("std").fillna(0) + 1e-6)).clip(-6, 12)
    key = pd.MultiIndex.from_arrays([claims.faskes_id.to_numpy(), claims.icd.to_numpy()])
    return z.stack().reindex(key).fillna(0.).to_numpy()


def _tariff_jump(claims):
    """Claim tariff against the median of the same patient's strictly earlier claims."""
    jumps = {}
    ordered = claims.sort_values(["visit_ts", "claim_id"], kind="stable")
    for _, group in ordered.groupby("patient_id", sort=False):
        times = group.visit_ts.to_numpy()
        tariffs = group.tarif.to_numpy(dtype=float)
        for i, claim_id in enumerate(group.claim_id.to_numpy()):
            # Equal service timestamps are excluded so ties do not depend on row order.
            end = int(np.searchsorted(times, times[i], side="left"))
            if end:
                prior = float(np.median(tariffs[:end]))
                jumps[claim_id] = float(np.clip((tariffs[i] - prior) / max(tariffs[i], 1.), -1., 1.))
    return pd.Series(jumps, dtype=float).reindex(claims.claim_id).fillna(0.).to_numpy()


def extend(claims, base, faskes):
    assert_no_labels(claims, faskes)
    return base.join(pd.DataFrame({UPCODING_FEATURES[0]: _mix_z(claims, faskes),
                                   UPCODING_FEATURES[1]: _tariff_jump(claims)}, index=base.index))


def indicators(row):
    notes = []
    if row.f_icd_mix_z > 3:
        notes.append(f"Kode diagnosis ini ditagih faskes tersebut {row.f_icd_mix_z:.1f} simpangan baku "
                     "di atas porsi faskes sejenis; bandingkan dengan rekam medis dan kapabilitas layanan.")
    if row.f_pat_tarif_jump > .5:
        notes.append(f"Selisih tarif terhadap median klaim peserta sebelumnya setara "
                     f"{row.f_pat_tarif_jump:.0%} dari tarif saat ini; "
                     "ini rasio terhadap tarif saat ini, bukan persentase kenaikan dari median. "
                     "Periksa dasar peningkatan kode diagnosis.")
    return notes
