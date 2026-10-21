"""Separate synthetic scenario construction, with no production-generator imports.

Labels describe planted scenarios, not clinical findings. Independence here means
separate generation code; domain assumptions still come from the same project.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Scenario:
    claims: pd.DataFrame
    faskes: pd.DataFrame
    affiliations: pd.DataFrame
    patients: pd.DataFrame
    labels: pd.DataFrame


def generate(seed=31, *, start="2026-09-01", days=60, n_routine=2500, upcoding=False):
    if days < 14 or n_routine < 1:
        raise ValueError("Skenario membutuhkan minimal 14 hari dan satu klaim rutin.")
    rng = np.random.default_rng(seed)
    prefix = f"EXT{seed}-"
    start = pd.Timestamp(start)
    facilities = [f"{prefix}F{i}" for i in range(20)]
    doctors = [f"{prefix}D{i}" for i in range(80)]
    people = [f"{prefix}P{i}" for i in range(600)]
    faskes = pd.DataFrame([dict(faskes_id=f, type="klinik" if i < 16 else "rs_c",
                               region=f"EXT-R{i % 4}", capacity=40 if i < 16 else 150)
                          for i, f in enumerate(facilities)])
    affiliations = [(d, facilities[i // 4]) for i, d in enumerate(doctors)]
    # A physician can legitimately work at more than one facility.
    affiliations += [(doctors[i], facilities[17]) for i in range(8)]
    affiliations += [(doctors[0], facilities[i]) for i in (1, 2, 3)]
    affiliations = pd.DataFrame(affiliations, columns=["doctor_id", "faskes_id"]).drop_duplicates()
    patients = pd.DataFrame({"patient_id": people, "home_region": [f"EXT-R{i % 4}" for i in range(600)]})
    rows, labels = [], []

    def emit(f, d, p, icd, when, *, fraud=0, scenario="routine", source=None, refdoc=None, submitted=None):
        cid = f"{prefix}C{len(rows):06d}"
        tariff = {"I10": 180000, "E11.9": 220000, "N18.6": 950000, "I50": 1800000}[icd]
        submitted = submitted if submitted is not None else when + pd.Timedelta(hours=float(rng.uniform(8, 72)))
        rows.append(dict(claim_id=cid, faskes_id=facilities[f], doctor_id=doctors[d],
                         patient_id=people[p], icd=icd, tarif=float(tariff * rng.uniform(.85, 1.15)),
                         visit_ts=when, submit_ts=submitted,
                         referral_from_faskes=None if source is None else facilities[source],
                         referral_from_doctor=None if refdoc is None else doctors[refdoc]))
        labels.append(dict(claim_id=cid, is_fraud=fraud, scenario=scenario))

    def time():
        return start + pd.Timedelta(days=int(rng.integers(days - 6)), hours=float(rng.uniform(7, 19)))

    for _ in range(n_routine):
        f = int(rng.integers(20))
        people_local = [p for p in range(600) if p % 4 == f % 4]
        p = int(rng.choice(people_local if rng.random() < .8 else list(range(600))))
        emit(f, f * 4 + int(rng.integers(4)), p, str(rng.choice(["I10", "E11.9"])), time())

    # Fragmented phantom episodes: doctor concurrency, but submissions dispersed by days.
    for episode in range(20):
        t = time()
        for f in range(4):
            emit(f, 0, 500 + episode, "I10", t + pd.Timedelta(minutes=3 * f),
                 fraud=1, scenario="phantom_distributed")

    # Rebilling after 2.5–5 days, outside the original 48-hour recent-duplicate window.
    for episode in range(40):
        t, p = time(), 400 + episode
        emit(8, 32, p, "E11.9", t, scenario="repeat_original")
        emit(9, 36, p, "E11.9", t + pd.Timedelta(days=float(rng.uniform(2.5, 5))),
             fraud=1, scenario="repeat_delayed")

    # Planted affiliated referrals without a reciprocal cycle.
    for episode in range(80):
        emit(17, 68, 300 + episode, "E11.9", time(), fraud=1,
             scenario="selfref_oneway", source=0, refdoc=0)

    # Legitimate difficult examples: frequent dialysis, transfers, and office batch submission.
    for p in range(20):
        t = time()
        for k in range(4):
            emit(18, 72, p, "N18.6", t + pd.Timedelta(hours=36 * k), scenario="legit_dialysis")
    for episode in range(30):
        t, p = time(), 100 + episode
        emit(2, 8, p, "I10", t, scenario="legit_transfer")
        emit(16, 64, p, "I10", t + pd.Timedelta(hours=4), scenario="legit_transfer", source=2, refdoc=8)
    for day in (5, 20, 35):
        if day >= days:
            continue
        t = start + pd.Timedelta(days=day)
        for i in range(25):
            emit(19, 76 + i % 4, 200 + i, "I10", t + pd.Timedelta(hours=8, minutes=15 * i),
                 scenario="legit_office_batch", submitted=t + pd.Timedelta(days=1, hours=1))
    if upcoding:
        # A primary clinic bills heart failure for patients whose own record is routine
        # hypertension. Tariff stays under the I50 ceiling, so cap-based rules never fire;
        # the signal is the diagnosis mix versus same-type peers and the patient's own history.
        for episode in range(60):
            first = int(rng.integers(5, max(6, days - 30)))
            t = start + pd.Timedelta(days=first, hours=float(rng.uniform(7, 19)))
            p = 440 + episode % 60
            emit(5, 20, p, "I10", t, scenario="upcode_original")
            emit(5, 20, p, "I50", t + pd.Timedelta(days=float(rng.uniform(10, 20))),
                 fraud=1, scenario="upcoding")
        # Legitimate contrast: type-C hospitals really do manage heart failure, so I50 is
        # expected there and must not become fraud merely by being a high-severity code.
        for episode in range(40):
            facility, doctor = (16, 64) if episode % 2 else (17, 69)
            emit(facility, doctor, 225 + episode % 75, "I50", time(), scenario="legit_severe")
    return Scenario(pd.DataFrame(rows), faskes, affiliations, patients, pd.DataFrame(labels))
