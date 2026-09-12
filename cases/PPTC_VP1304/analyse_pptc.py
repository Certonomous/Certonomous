#!/usr/bin/env python3
"""PPTC VP1304 open-water comparator.

Reads the OpenFOAM `forces` functionObject output for one advance ratio, forms KT, 10KQ
and eta_O, and grades them against the band FROZEN in
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` (commit 09396b48).

THIS COMPARATOR REFUSES RATHER THAN DEGRADES.  It exits 2, printing REFUSE and the reason,
and prints no coefficient at all, if any of the following is not satisfied:

  C1  FREEZE     the frozen pre-registration on disk does not hash to the committed blob;
  C2  SELF-TEST  the coefficient formulas do not reproduce Report 3752's OWN measured
                 thrust and torque in newtons from its OWN tabulated coefficients;
  C3  PLANT      a known perturbation written into the force file on disk is not read back
                 at the expected magnitude.

C2 and C3 are the planted-zero doctrine (CLAUDE.md rule 3): a zero -- or any small number --
from a reader not shown able to see a known NON-ZERO is not evidence.  C2 plants nothing:
it is a non-zero supplied by the source document itself, which is stronger, because it tests
the physics constants and not merely the file parser.  C3 tests the parser.

Usage
  analyse_pptc.py --selftest
  analyse_pptc.py --case <dir> --J <value> [--forces-name forcesBody] [--window 500]
"""
from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import shutil
import sys

# --------------------------------------------------------------------------------------
# FROZEN CONSTANTS.  Every value below is quoted from the frozen pre-registration, which is
# quoted from Report 3752.  None of them is a run-time choice.
# --------------------------------------------------------------------------------------

PREREG = 'cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md'

# The grading path is pinned to the frozen pre-registration AS AMENDED, and the whole
# history of that pin is recorded here so a reader can see what changed and when.
#
#   v1.0  sha256 5611e24bee05ecc5862f1907166efc9015f3875c7035265e922a3174f777ad38
#         blob   7047d9aad5da20b66fa3f92cf65d8fea094781d6
#         commit 09396b48990da3ce8e91714cd1a35f3fbc07e4de   (the original freeze)
#   v1.1  AMENDMENT 1, 2026-09-12, appended at the foot BEFORE FIRST COMPUTE
#         (verification/runs/PPTC_VP1304/ did not exist), on Sanaa's 22:55Z
#         "pptc shaft diameter: find out". It corrects the shaft diameter in section
#         2.2(b) from 0.075 m to the measured 0.040 m and ALTERS NO GATE, THRESHOLD,
#         CAP OR LABEL -- every constant in this comparator is unchanged by it, which
#         is why re-pinning is legitimate rather than a moved goalpost.
#         Verified: lines whose number changed above the amendment: 0.
#
# This pin was exercised: run against v1.1 while still pinned to v1.0, the comparator
# refused with exit 2 and printed both hashes. C1 is not decorative.
PREREG_SHA256 = '3524f8ad7b0bce1a365f500ac62dbc998763bb666adedaeb4e8727363720bd5b'
PREREG_BLOB = '845974fab273e2c02b4e13ee3cc22727943ebad2'
PREREG_COMMIT = '09396b48990da3ce8e91714cd1a35f3fbc07e4de'
PREREG_VERSION = '1.3 (amendments 1, 2 and 3)'
#   v1.2  AMENDMENT 2, 2026-09-12, also before first compute: the comparator's
#         torque is BLADE TORQUE ONLY, so the two integration sets below differ.
#         Alters no gate, threshold, cap or label.
#   v1.3  AMENDMENT 3, 2026-09-12, before first compute: the THRUST patch list is
#         established from SVA's correction algebra instead of inherited from the
#         same gloss amendment 2 disproved on torque. It CONFIRMS the list below
#         unchanged. Every term SVA retains, these patches produce; every term SVA
#         subtracts, our geometry does not produce. No registered quantity changed.

RHO = 998.99          # kg/m3,  Report 3752 page 2.11 header
NU = 1.124e-6         # m2/s,   Report 3752 page 2.11 header
D = 0.250             # m,      Report 3752 Table 1
N_RPS = 15.0          # 1/s,    registered rotation rate
C07 = 0.10417         # m,      Report 3752 Table 1

# Single blade passage of 72 degrees: the solved sector is one fifth of the propeller,
# blades, hub, cap and shaft alike.  Registered in pre-registration section 6.1.
PASSAGE_DEG = 72.0
SECTOR_MULTIPLIER = 360.0 / PASSAGE_DEG      # 5.0

# Thrust is the axial force in the thrust direction.  The CAD places the nose cap at +x and
# the shaft at -x (GEOMETRY_ADMISSION_RECORD.md section 2), so the freestream runs +x -> -x
# and thrust on the body acts toward +x.  Torque is about the same axis.
AXIS = 0              # x
THRUST_SIGN = +1.0

# AMENDMENT 2: THE TWO INTEGRATION SETS ARE NOT THE SAME SET, and that is not an oversight.
# Report 3752 annex A2.1: "The measured torque will be corrected for the effect frictional
# values of torque, taken with the shaft rotating at the same speed with an axis symmetric
# mass mounted at the position of the rotor."  An axisymmetric bladeless body run at speed and
# subtracted removes EVERY rotating friction torque that is not the blades.  SVA's own
# correction sheets 4 and 5 subtract Q_hub in BOTH the "blades and hub" and the "blades only"
# configuration, and 10KQ is identical digit-for-digit between pages 2.11 and 2.13 at all
# fourteen tabulated J -- which two tables with different torque content could not be.
#
#   THRUST (KT): blades + hub + cap + shaft   -- page 2.11 retains the hub assembly's drag
#   TORQUE (KQ): blades ONLY                  -- every non-blade rotating friction subtracted
#   shaftExtension (x < -356 mm): EXCLUDED FROM BOTH.  It is our domain's artefact, not part
#     of the physical model the dynamometer measured, and at 1.144 m it is three times the
#     shaft length the CAD contains.
#
# Leaving the non-blade torque in would bias 10KQ by about +0.76 % -- only 9 % of the band
# half-width, but 19 % of the top of the prediction window in section 5 AND CARRYING THE SAME
# SIGN, so it would be indistinguishable after the fact from the transition physics that
# prediction is about.
FORCES_THRUST = 'forcesThrust'   # functionObject over blades hub cap shaft
FORCES_TORQUE = 'forcesTorque'   # functionObject over blades only
PATCHES_THRUST = ('blades', 'hub', 'cap', 'shaft')
PATCHES_TORQUE = ('blades',)
PATCHES_EXCLUDED = ('shaftExtension',)

# Report 3752 page 2.11, "corrected with idle torque and gap force".  THE COMPARATOR.
MEASURED = {
    0.7985: (0.5052, 1.1836, 0.542),
    0.9314: (0.4297, 1.0493, 0.607),
    1.0683: (0.3538, 0.9096, 0.661),
    1.2021: (0.2797, 0.7676, 0.697),
    1.3308: (0.2082, 0.6300, 0.700),
    1.4594: (0.1394, 0.4944, 0.655),
}

# Pre-registration section 4.5, centring B.  Half-widths in percent of the measured value.
BAND_PCT = {
    0.7985: (3.84, 5.26),
    0.9314: (4.85, 6.72),
    1.0683: (6.11, 7.69),
    1.2021: (7.55, 8.10),
    1.3308: (10.86, 8.36),
    1.4594: (12.65, 8.50),      # clamped at the J = 1.4 workshop value, disclosed
}

# Declared-secondary tighter reading (pre-registration section 4.7), reported never gating.
FALLBACK_PCT = {J: ((3.0, 4.0) if J <= 1.33 else (6.0, 8.0)) for J in MEASURED}

# Report 3752 page 2.12, measured values at test 11F0395, used ONLY as the C2 control.
# (J, n_rps, T_newton, Q_newton_metre, KT_2p13, tenKQ_2p13)
SELFTEST_ROWS = [
    (1.2021, 14.974, 255.63, 16.791, 0.2922, 0.7676),
    (1.0683, 14.978, 318.74, 19.907, 0.3641, 0.9096),
    (0.9314, 15.023, 385.70, 23.102, 0.4380, 1.0493),
]
SELFTEST_TOL_PCT = 0.25

PLANT_FACTOR = 1.0500          # pre-registration section 8.2
PLANT_EXPECTED_PCT = 5.00
PLANT_TOL_PCT = 0.01


class Refusal(Exception):
    pass


# --------------------------------------------------------------------------------------
# Coefficients
# --------------------------------------------------------------------------------------

def kt(thrust_n: float, n_rps: float = N_RPS) -> float:
    return thrust_n / (RHO * n_rps ** 2 * D ** 4)


def kq(torque_nm: float, n_rps: float = N_RPS) -> float:
    return torque_nm / (RHO * n_rps ** 2 * D ** 5)


def eta_o(J: float, kt_v: float, kq_v: float) -> float:
    if kq_v == 0.0:
        raise Refusal('eta_O undefined: KQ is exactly zero')
    return J * kt_v / (2.0 * math.pi * kq_v)


def thrust_from_kt(kt_v: float, n_rps: float) -> float:
    return kt_v * RHO * n_rps ** 2 * D ** 4


def torque_from_kq(kq_v: float, n_rps: float) -> float:
    return kq_v * RHO * n_rps ** 2 * D ** 5


def reynolds(J: float, n_rps: float = N_RPS) -> float:
    """Report 3752 annex: Re = c0.7 sqrt(V^2 + (0.7 pi n D)^2) / nu."""
    v = J * n_rps * D
    return C07 * math.hypot(v, 0.7 * math.pi * n_rps * D) / NU


# --------------------------------------------------------------------------------------
# C1 -- the freeze
# --------------------------------------------------------------------------------------

def check_freeze(repo_root: str) -> str:
    path = os.path.join(repo_root, PREREG)
    if not os.path.exists(path):
        raise Refusal(f'frozen pre-registration not on disk at {path}')
    with open(path, 'rb') as fh:
        got = hashlib.sha256(fh.read()).hexdigest()
    if got != PREREG_SHA256:
        raise Refusal(
            'the frozen pre-registration is NOT the file that was committed.\n'
            f'    expected sha256 {PREREG_SHA256}\n'
            f'    found    sha256 {got}\n'
            f'    committed blob  {PREREG_BLOB} at {PREREG_COMMIT}\n'
            '    The grading path is fixed at the pre-registration commit; a comparator may\n'
            '    not grade against an edited freeze.')
    return got


# --------------------------------------------------------------------------------------
# C2 -- the source document's own non-zero
# --------------------------------------------------------------------------------------

def check_selftest(verbose: bool = True) -> None:
    """Reproduce Report 3752 page 2.12's measured newtons from page 2.13's coefficients.

    This is a KNOWN NON-ZERO supplied by the source document, not by us.  It exercises rho,
    D, the n^2 D^4 and n^2 D^5 groups and the coefficient definitions together.  If any of
    them is wrong this fails, and a wrong constant is exactly the failure that produces a
    confident, plausible, wrong KT.
    """
    worst = 0.0
    for J, n_rps, t_meas, q_meas, kt_ref, tenkq_ref in SELFTEST_ROWS:
        t_pred = thrust_from_kt(kt_ref, n_rps)
        q_pred = torque_from_kq(tenkq_ref / 10.0, n_rps)
        dt = 100.0 * (t_pred - t_meas) / t_meas
        dq = 100.0 * (q_pred - q_meas) / q_meas
        worst = max(worst, abs(dt), abs(dq))
        if verbose:
            print(f'    J={J:.4f} n={n_rps:.3f}  T {t_pred:9.2f} N vs measured {t_meas:9.2f} N '
                  f'({dt:+.3f}%)   Q {q_pred:8.3f} Nm vs measured {q_meas:8.3f} Nm ({dq:+.3f}%)')
    if worst > SELFTEST_TOL_PCT:
        raise Refusal(
            f'coefficient self-test FAILED: worst deviation {worst:.3f}% exceeds '
            f'{SELFTEST_TOL_PCT}%.\n'
            '    The comparator cannot reproduce Report 3752\'s own measured thrust and\n'
            '    torque from its own tabulated coefficients, so its constants are wrong and\n'
            '    every coefficient it would print is wrong with them.')
    if verbose:
        print(f'    worst deviation {worst:.3f}% (tolerance {SELFTEST_TOL_PCT}%)  -- C2 PASS')


# --------------------------------------------------------------------------------------
# Reading the forces functionObject
# --------------------------------------------------------------------------------------

_NUM = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')


def _parse_dat(path: str):
    """Return (times, rows) where each row is the flat list of numbers on that line."""
    times, rows = [], []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            vals = [float(v) for v in _NUM.findall(s.replace('(', ' ').replace(')', ' '))]
            if len(vals) < 4:
                continue
            times.append(vals[0])
            rows.append(vals[1:])
    return times, rows


def find_force_files(case: str, name: str):
    """Locate the newest force.dat and moment.dat under postProcessing/<name>/."""
    base = os.path.join(case, 'postProcessing', name)
    if not os.path.isdir(base):
        raise Refusal(f'no forces output directory at {base}')
    force_files, moment_files = [], []
    for t in sorted(os.listdir(base)):
        d = os.path.join(base, t)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.startswith('force') and fn.endswith('.dat'):
                force_files.append(os.path.join(d, fn))
            elif fn.startswith('moment') and fn.endswith('.dat'):
                moment_files.append(os.path.join(d, fn))
    if not force_files:
        raise Refusal(f'no force*.dat under {base}')
    if not moment_files:
        raise Refusal(f'no moment*.dat under {base}')
    return sorted(force_files), sorted(moment_files)


def read_axial_and_torque(case: str, name: str, window: int):
    """Return (n_samples, mean_axial_force_N, mean_axial_moment_Nm, last_time) for the
    SOLVED SECTOR -- the sector multiplier is applied by the caller, once, visibly."""
    ffs, mfs = find_force_files(case, name)
    ft, fr = [], []
    for p in ffs:
        t, r = _parse_dat(p)
        ft += t
        fr += r
    mt, mr = [], []
    for p in mfs:
        t, r = _parse_dat(p)
        mt += t
        mr += r
    if not fr or not mr:
        raise Refusal('force or moment file contained no numeric rows')
    k = min(window, len(fr), len(mr))
    fx = [row[AXIS] for row in fr[-k:]]
    mx = [row[AXIS] for row in mr[-k:]]
    return k, sum(fx) / k, sum(mx) / k, ft[-1]


# --------------------------------------------------------------------------------------
# C3 -- the plant
# --------------------------------------------------------------------------------------

def check_plant(case: str, name: str, window: int, verbose: bool = True) -> None:
    """Scale the axial force column on disk by PLANT_FACTOR, re-read through the SAME
    reader, and require the read-back to move by PLANT_EXPECTED_PCT.

    The plant is written to a COPY of the case's postProcessing tree and removed afterwards,
    so the graded data is never modified.  If the reader cannot see the plant, the comparator
    refuses: a reader that cannot see a 5 % change in the number it exists to read cannot be
    trusted to report that the number is in band.
    """
    ffs, _ = find_force_files(case, name)
    backups = []
    try:
        _, base_fx, _, _ = read_axial_and_torque(case, name, window)
        if base_fx == 0.0:
            raise Refusal('baseline axial force is exactly zero; the plant cannot be scaled '
                          'from it -- refusing rather than planting an absolute value onto '
                          'a reader that may be reading nothing at all')
        for p in ffs:
            b = p + '.preplant'
            shutil.copy2(p, b)
            backups.append((p, b))
            out = []
            with open(p) as fh:
                for line in fh:
                    s = line.rstrip('\n')
                    if not s.strip() or s.lstrip().startswith('#'):
                        out.append(s)
                        continue
                    has_paren = '(' in s
                    flat = s.replace('(', ' ').replace(')', ' ')
                    vals = [float(v) for v in _NUM.findall(flat)]
                    if len(vals) < 4:
                        out.append(s)
                        continue
                    vals[1 + AXIS] *= PLANT_FACTOR
                    if has_paren:
                        body = ' '.join(f'{v:.10g}' for v in vals[1:])
                        out.append(f'{vals[0]:.10g}\t({body})')
                    else:
                        out.append('\t'.join(f'{v:.10g}' for v in vals))
            with open(p, 'w') as fh:
                fh.write('\n'.join(out) + '\n')
        _, planted_fx, _, _ = read_axial_and_torque(case, name, window)
        moved = 100.0 * (planted_fx - base_fx) / base_fx
        if verbose:
            print(f'    baseline axial force {base_fx:.6g} N -> planted {planted_fx:.6g} N '
                  f'({moved:+.4f}%, expected {PLANT_EXPECTED_PCT:+.2f}%)')
        if abs(moved - PLANT_EXPECTED_PCT) > PLANT_TOL_PCT:
            raise Refusal(
                f'PLANTED PERTURBATION NOT DETECTED. A factor of {PLANT_FACTOR} was written '
                f'into the axial force column on disk and the reader reported a change of '
                f'{moved:+.4f}% against the expected {PLANT_EXPECTED_PCT:+.2f}% '
                f'(tolerance {PLANT_TOL_PCT}%).\n'
                '    This reader has not been shown able to see a known non-zero, so no\n'
                '    number it produces is evidence (CLAUDE.md rule 3).')
        if verbose:
            print('    -- C3 PASS')
    finally:
        for p, b in backups:
            shutil.move(b, p)


# --------------------------------------------------------------------------------------
# Grading
# --------------------------------------------------------------------------------------

def nearest_registered_J(J: float) -> float:
    j = min(MEASURED, key=lambda x: abs(x - J))
    if abs(j - J) > 1e-3:
        raise Refusal(
            f'J = {J} is not one of the six registered advance ratios '
            f'{sorted(MEASURED)}. The gate is defined only at the measured points; no\n'
            '    interpolation enters it (pre-registration section 3.1).')
    return j


def grade(J: float, kt_v: float, tenkq_v: float):
    j = nearest_registered_J(J)
    kt_m, kq_m, eta_m = MEASURED[j]
    p_kt, p_kq = BAND_PCT[j]
    lo_t, hi_t = kt_m * (1 - p_kt / 100), kt_m * (1 + p_kt / 100)
    lo_q, hi_q = kq_m * (1 - p_kq / 100), kq_m * (1 + p_kq / 100)
    in_t = lo_t <= kt_v <= hi_t
    in_q = lo_q <= tenkq_v <= hi_q
    verdict = 'PASS' if (in_t and in_q) else 'GATE FAIL'
    return dict(J=j, kt_m=kt_m, kq_m=kq_m, eta_m=eta_m,
                band_kt=(lo_t, hi_t), band_kq=(lo_q, hi_q),
                in_kt=in_t, in_kq=in_q, verdict=verdict,
                d_kt=100 * (kt_v - kt_m) / kt_m, d_kq=100 * (tenkq_v - kq_m) / kq_m)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--case')
    ap.add_argument('--J', type=float)
    ap.add_argument('--window', type=int, default=500)
    ap.add_argument('--repo-root', default=os.getcwd())
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()

    try:
        print('C1  FREEZE     verifying the frozen pre-registration is the file that ran')
        print(f'    sha256 {check_freeze(a.repo_root)}  -- C1 PASS')
        print('C2  SELF-TEST  reproducing Report 3752 page 2.12 measured N and Nm from its '
              'own page 2.13 coefficients')
        check_selftest()

        if a.selftest:
            print('\nSELF-TEST COMPLETE. C1 and C2 pass. C3 requires a case with forces output.')
            return 0

        if not a.case or a.J is None:
            raise Refusal('--case and --J are required unless --selftest is given')

        print('C3  PLANT      planting a known perturbation into EACH reader and reading it back')
        print(f'    thrust set {FORCES_THRUST} over {PATCHES_THRUST}')
        check_plant(a.case, FORCES_THRUST, a.window)
        print(f'    torque set {FORCES_TORQUE} over {PATCHES_TORQUE}')
        check_plant(a.case, FORCES_TORQUE, a.window)

        k, fx, _, tlast = read_axial_and_torque(a.case, FORCES_THRUST, a.window)
        _, _, mx, _ = read_axial_and_torque(a.case, FORCES_TORQUE, a.window)
        thrust = THRUST_SIGN * fx * SECTOR_MULTIPLIER
        torque = abs(mx) * SECTOR_MULTIPLIER
        kt_v = kt(thrust)
        kq_v = kq(torque)
        tenkq = 10.0 * kq_v
        eta = eta_o(a.J, kt_v, kq_v)

        print(f'\nlast time {tlast}, averaged over the last {k} samples, '
              f'sector multiplier {SECTOR_MULTIPLIER:g} applied once')
        print(f'  KT integrated over {PATCHES_THRUST}; KQ over {PATCHES_TORQUE}; '
              f'{PATCHES_EXCLUDED} excluded from both (amendment 2)')
        print(f'  thrust {thrust:12.4f} N      torque {torque:10.4f} N m      '
              f'Re {reynolds(a.J):.3e}')
        print(f'  KT {kt_v:9.4f}   10KQ {tenkq:9.4f}   eta_O {eta:8.4f}')

        if kt_v < 0:
            print('\nNEGATIVE KT. Pre-registration section 7 stops the case here: the '
                  'registered rotation sign is flipped and the flip is RECORDED, not '
                  'quietly applied.')
            return 3

        g = grade(a.J, kt_v, tenkq)
        print(f'\n  measured (Report 3752 p2.11)  KT {g["kt_m"]:.4f}   10KQ {g["kq_m"]:.4f}'
              f'   eta_O {g["eta_m"]:.3f}')
        print(f'  band (centring B, 2 sigma)    KT [{g["band_kt"][0]:.4f}, {g["band_kt"][1]:.4f}]'
              f'   10KQ [{g["band_kq"][0]:.4f}, {g["band_kq"][1]:.4f}]')
        print(f'  deviation                     KT {g["d_kt"]:+.2f}%   10KQ {g["d_kq"]:+.2f}%')
        fb_t, fb_q = FALLBACK_PCT[g['J']]
        print(f'  [secondary, NOT gating] the permitted fallback band would have been '
              f'KT +-{fb_t:.0f}%, 10KQ +-{fb_q:.0f}%: '
              f'KT {"in" if abs(g["d_kt"]) <= fb_t else "OUT"}, '
              f'10KQ {"in" if abs(g["d_kq"]) <= fb_q else "OUT"}')
        print(f'\nVERDICT: {g["verdict"]}')
        if g['verdict'] == 'GATE FAIL':
            m = max(abs(g['d_kt']) - BAND_PCT[g['J']][0], abs(g['d_kq']) - BAND_PCT[g['J']][1])
            print(f'  margin outside the band: {m:+.2f} percentage points')
        print('  NOTE: this verdict is subject to Roache triple gating. A row whose grid '
              'triple is not CONVERGING is NOT A RESULT whatever this says.')
        return 0

    except Refusal as e:
        print(f'\nREFUSE: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
