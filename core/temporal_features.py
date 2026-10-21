"""Experimental historical-episode and directional-referral indicators.

These are observable associations, not proof of duplicate payment or inappropriate
referral. No clinical capability, payment outcome, or fraud label is inferred.
"""
import numpy as np
import pandas as pd

from core.detect import assert_no_labels

EXTRA_FEATURES = ["episode_prior_7d", "episode_cross_7d", "episode_prior_30d",
                  "episode_cross_tariff_similarity", "episode_gap_days", "episode_interval_cv",
                  "ref_target_share", "ref_target_patients", "ref_doctor_volume", "ref_destination_hhi"]


def extend(claims, base):
    assert_no_labels(claims)
    out = pd.DataFrame(0., index=base.index, columns=EXTRA_FEATURES)
    ordered = claims.sort_values(["visit_ts", "claim_id"], kind="stable")
    for _, group in ordered.groupby(["patient_id", "icd"], sort=False):
        times = (group.visit_ts - group.visit_ts.min()).dt.total_seconds().to_numpy() / 86400
        facility, tariffs, ids = group.faskes_id.to_numpy(), group.tarif.to_numpy(float), group.claim_id.to_numpy()
        for i, cid in enumerate(ids):
            # Strictly earlier service timestamps; equal-time rows do not depend on arbitrary row order.
            end = np.searchsorted(times, times[i], side="left")
            lo7 = np.searchsorted(times, times[i] - 7, side="left")
            lo30 = np.searchsorted(times, times[i] - 30, side="left")
            cross = facility[lo7:end] != facility[i]
            similarity = 0.
            if cross.any():
                prior = tariffs[lo7:end][cross]
                similarity = float(np.max(1 - np.abs(prior - tariffs[i]) / np.maximum(np.maximum(prior, tariffs[i]), 1)))
            gaps = np.diff(np.r_[times[lo30:end], times[i]])
            cv = float(gaps.std() / gaps.mean()) if len(gaps) >= 2 and gaps.mean() > 0 else 0.
            out.loc[cid, EXTRA_FEATURES[:6]] = [end - lo7, int(cross.sum()), end - lo30, similarity,
                                               times[i] - times[end - 1] if end > lo30 else 31., cv]
    refs = claims[claims.referral_from_doctor.notna() & claims.referral_from_doctor.ne("")]
    if not refs.empty:
        volume = refs.groupby("referral_from_doctor").size()
        pair = refs.groupby(["referral_from_doctor", "faskes_id"]).size()
        patients = refs.groupby(["referral_from_doctor", "faskes_id"]).patient_id.nunique()
        shares = pair / pair.index.get_level_values(0).map(volume)
        hhi = shares.pow(2).groupby(level=0).sum()
        for row in refs.itertuples():
            key = (row.referral_from_doctor, row.faskes_id)
            out.loc[row.claim_id, EXTRA_FEATURES[6:]] = [shares.loc[key], patients.loc[key],
                                                        volume.loc[row.referral_from_doctor], hhi.loc[row.referral_from_doctor]]
    return base.join(out)


def indicators(row):
    notes = []
    if row.episode_cross_7d:
        notes.append(f"{int(row.episode_cross_7d)} klaim sebelumnya dengan peserta/diagnosis sama di faskes lain dalam 7 hari; periksa episode dan pembayaran.")
    if row.ref_doctor_volume >= 5 and row.ref_target_share >= .8:
        notes.append(f"{row.ref_target_share:.0%} rujukan dokter menuju faskes ini; periksa kebutuhan dan kapabilitas layanan.")
    return notes
