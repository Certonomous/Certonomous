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
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

# --------------------------------------------------------------------------------------
# FROZEN CONSTANTS.  Every value below is quoted from the frozen pre-registration, which is
# quoted from Report 3752.  None of them is a run-time choice.
# --------------------------------------------------------------------------------------

PREREG = 'cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md'

# Repository root derived from THIS file's location (cases/PPTC_VP1304/), never from
# cwd: the comparator is run detached from the case directory, and a cwd-derived root
# would resolve into the run tree.
REPO_ROOT_FOR_SCRIPTS = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
# Set from --repo-root in main(); consulted ONLY if the path above does not carry
# scripts/solver_log_set.py. See the note at its use site.
_SCRIPTS_FALLBACK_ROOT = None

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
#   v1.4  AMENDMENT 4, 2026-09-13, before first compute. Appended at the foot; it
#         moved no gate, threshold, cap or label.
#
# ---------------------------------------------------------------------------------
# AMENDMENT 5 TO THE GRADING PATH -- 2026-09-13. HOW THE FREEZE IS RESOLVED, AND
# NOTHING ELSE.  No gate, threshold, band, cap or label is touched by this change;
# every constant below it is byte-unchanged.
#
# THE DEFECT.  Standing rule 2 says: verify the frozen file IS the file that ran by
# hashing it against THE COMMITTED BLOB.  The check this replaces hashed THE WHOLE
# FILE ON DISK against one stored sha256 -- so every legal pre-compute amendment
# invalidated it, and it had to be re-pinned by hand after each.  It FAILED PRECISELY
# WHEN THE DOCUMENT DID THE LEGAL THING.  Measured 2026-09-13: the comparator refused
# with exit 2 and printed no coefficient, because AMENDMENT 4 was appended on
# 2026-09-13 and the pin still carried the v1.3 sha256.  This is the defect CRM's
# ADDENDUM 13 D0 identified and A14.8 repaired for that act -- "a document that is
# pinned as a frozen instrument cannot also be the document that grows an addendum
# for every subsequent rung" -- and the canonical repair is that act's: pin by
# COMMIT, resolve with `git cat-file`, NEVER from disk.
#
# 🔴 A SECOND DEFECT, FOUND WHILE REPAIRING THE FIRST, AND IT MADE THE OLD REFUSAL
# MESSAGE FALSE.  The old constants named a blob and a commit THAT DO NOT GO
# TOGETHER: `845974fab273...` is the blob at commit `4f3e99de6` (AMENDMENT 3), not at
# `09396b48...`.  The blob at `09396b48...` is `7047d9aad5da...`.  A previous re-pin
# updated the sha256 and the blob to v1.3 and left the commit at the original freeze,
# so the message "committed blob 845974fab... at 09396b48..." asserted a pairing that
# has never existed.  The constants below are now mutually consistent and each is
# verified against `git` rather than transcribed.
#
# THE REPLACEMENT, AND WHY IT IS STRICTLY STRONGER.  Two clauses, from TWO DIFFERENT
# SOURCES -- the git object store and the filesystem -- so this is not an assert
# comparing a thing with itself (L-596's shape):
#   F1  The frozen text is read out of git at PREREG_COMMIT and must hash to BOTH
#       PREREG_BLOB_AT_COMMIT and PREREG_SHA256_AT_COMMIT.  Read from the object
#       store, so NO EDIT ON DISK CAN DEFEAT IT.
#   F2  The file on disk must BEGIN WITH that frozen text, byte for byte.  A legal
#       amendment appends and passes; an in-place edit ANYWHERE ABOVE the appended
#       tail fails.  This enforces rule 6's "lines whose number changed above this
#       section: 0" mechanically, which the old whole-file hash never did.
# The old check verified one thing weakly.  This verifies two things, one of which
# the old check could not express at all.
#
# CONDITION FOR THIS AMENDMENT, AND HOW IT WAS CHECKED (rule 2).  Before first
# compute FOR THE GRADING PATH: no PPTC solve has been graded by this comparator.
# Checked at the location the runs ACTUALLY USE -- `/home/ubuntu/certonomous-runs/
# PPTC_VP1304/` -- not at `verification/runs/PPTC_VP1304/`, which AMENDMENTS 1-3 named
# and which is not the run root, so their condition was true of a path that was never
# going to exist.  A control checked against the wrong location cannot fail, which
# makes it not a control; A4 corrected the method and this amendment keeps it.
# ---------------------------------------------------------------------------------

# Verified against `git rev-parse 09396b48...:<PREREG>` and `git cat-file`, not
# transcribed: the blob AT the commit, and the sha256 OF that blob's content.
PREREG_COMMIT = '09396b48990da3ce8e91714cd1a35f3fbc07e4de'
PREREG_BLOB_AT_COMMIT = '7047d9aad5da20b66fa3f92cf65d8fea094781d6'
PREREG_SHA256_AT_COMMIT = '5611e24bee05ecc5862f1907166efc9015f3875c7035265e922a3174f777ad38'
PREREG_VERSION = '1.4 (amendments 1-4; freeze resolved by commit, amendment 5)'
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

def _git(repo_root: str, *args: str) -> bytes:
    """Run git in the repository and return stdout, or raise Refusal."""
    r = subprocess.run(('git',) + args, cwd=repo_root,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise Refusal(f'git {" ".join(args)} failed (rc={r.returncode}): '
                      f'{r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout


def frozen_text(repo_root: str, commit: str = PREREG_COMMIT,
                path: str = PREREG) -> bytes:
    """THE FROZEN REGISTRATION, READ OUT OF GIT AND NEVER FROM DISK.

    This is the whole point of amendment 5: the object store is immutable for a given
    commit, so no edit to the working tree can change what this returns."""
    return _git(repo_root, 'cat-file', 'blob', f'{commit}:{path}')


def check_freeze(repo_root: str, prereg: str = PREREG,
                 commit: str = PREREG_COMMIT,
                 blob: str = PREREG_BLOB_AT_COMMIT,
                 sha256_at_commit: str = PREREG_SHA256_AT_COMMIT,
                 disk_path: str | None = None) -> str:
    """C1, as amended 2026-09-13.  Two clauses, TWO DIFFERENT SOURCES.

    F1 -- the frozen text read from the GIT OBJECT STORE at `commit` must hash to the
          declared blob and sha256.  A disk edit cannot defeat this.
    F2 -- the file ON DISK must BEGIN WITH that frozen text, byte for byte.  A legal
          appended amendment passes; an in-place edit above the tail does not.

    Returns the sha256 of the frozen text.  Raises Refusal, never degrades."""
    # `prereg` names the path INSIDE GIT; `disk_path` names the file on the filesystem.
    # They are the same file in production and are separable ONLY so the F2 controls can
    # point the disk clause at a fixture without disturbing the git clause or writing
    # anything into the repository.
    path = disk_path or os.path.join(repo_root, prereg)
    if not os.path.exists(path):
        raise Refusal(f'frozen pre-registration not on disk at {path}')

    # ---- F1.  From git.  NOT from disk.
    froz = frozen_text(repo_root, commit, prereg)
    # git's blob id is sha1 over the header "blob <len>\0" plus the content. Computed
    # here rather than shelled out to `git hash-object`, so this clause depends on the
    # object's BYTES and not on a second git invocation agreeing with the first.
    got_blob = hashlib.sha1(b'blob %d\x00' % len(froz) + froz).hexdigest()
    got_sha = hashlib.sha256(froz).hexdigest()
    if got_blob != blob or got_sha != sha256_at_commit:
        raise Refusal(
            'THE PINNED COMMIT DOES NOT CARRY THE PINNED FROZEN TEXT.\n'
            f'    commit          {commit}\n'
            f'    expected blob   {blob}\n'
            f'    found    blob   {got_blob}\n'
            f'    expected sha256 {sha256_at_commit}\n'
            f'    found    sha256 {got_sha}\n'
            '    The grading path is fixed at the pre-registration commit; if the commit\n'
            '    and the blob disagree, the pin names a pairing that does not exist.')

    # ---- F2.  From the filesystem.  A DIFFERENT SOURCE from F1 -- that is deliberate,
    # because an assert that compares a thing with itself is not an assert (L-596).
    with open(path, 'rb') as fh:
        disk = fh.read()
    if not disk.startswith(froz):
        n = min(len(disk), len(froz))
        where = next((i for i in range(n) if disk[i] != froz[i]), n)
        raise Refusal(
            'THE FROZEN REGISTRATION HAS BEEN EDITED IN PLACE, NOT AMENDED.\n'
            f'    frozen text at {commit}: {len(froz)} bytes\n'
            f'    file on disk           : {len(disk)} bytes\n'
            f'    first divergence at byte {where}\n'
            '    Rule 6: a departure is a DATED AMENDMENT APPENDED AT THE FOOT, with\n'
            '    "lines whose number changed above this section: 0". A comparator may not\n'
            '    grade against a frozen file whose frozen part has moved.')
    return got_sha


def freeze_controls(repo_root: str, verbose: bool = True) -> None:
    """C1's FAILING-DIRECTION CONTROLS.  A freeze check repaired into one that cannot
    fail is far worse than one that was failing too often, so each clause is driven to
    REFUSE on a case built to break it, and then the real pin is required to PASS.

    Run ALWAYS, before the instrument is pointed at anything -- the habit taken from
    `verification/runs/PPTC_VP1304_runs/spd_gate.py:257`. An instrument armed once and
    trusted thereafter is an instrument nobody is checking."""
    fired = []

    # --- F1 must refuse a mutated blob: same commit, wrong declared hashes.
    try:
        check_freeze(repo_root, blob='0' * 40)
        raise Refusal('CONTROL FAILED: F1 accepted a mutated blob sha. The freeze check '
                      'cannot fail and is therefore not a check.')
    except Refusal as e:
        if 'CONTROL FAILED' in str(e):
            raise
        fired.append('F1/blob')
    try:
        check_freeze(repo_root, sha256_at_commit='0' * 64)
        raise Refusal('CONTROL FAILED: F1 accepted a mutated sha256.')
    except Refusal as e:
        if 'CONTROL FAILED' in str(e):
            raise
        fired.append('F1/sha256')

    # --- F1 must refuse a commit that does not carry this text.
    try:
        check_freeze(repo_root, commit='HEAD')
        raise Refusal('CONTROL FAILED: F1 accepted HEAD as the frozen commit, so the '
                      'pin does not pin anything.')
    except Refusal as e:
        if 'CONTROL FAILED' in str(e):
            raise
        fired.append('F1/commit')

    # --- F2 must refuse an IN-PLACE EDIT inside the frozen region, and must ACCEPT an
    # appended one.  Driven on real copies, not on a mocked reader.
    froz = frozen_text(repo_root)
    with tempfile.TemporaryDirectory() as td:
        dst = os.path.join(td, 'probe.md')       # OUTSIDE the repository, always

        # (a) frozen text plus an APPENDED amendment -> MUST PASS.
        with open(dst, 'wb') as fh:
            fh.write(froz + b'\n## APPENDED AMENDMENT PROBE\n')
        check_freeze(repo_root, disk_path=dst)
        fired.append('F2/append-accepted')

        # (b) ONE BYTE changed INSIDE the frozen region -> MUST REFUSE.  This is the
        # clause the old whole-file hash could not express at all.
        mut = bytearray(froz)
        mid = len(mut) // 2
        mut[mid] = mut[mid] ^ 0x20
        with open(dst, 'wb') as fh:
            fh.write(bytes(mut) + b'\n## APPENDED AMENDMENT PROBE\n')
        try:
            check_freeze(repo_root, disk_path=dst)
            raise Refusal('CONTROL FAILED: F2 accepted a file whose FROZEN REGION had '
                          'been edited in place. Rule 6 is unenforced.')
        except Refusal as e:
            if 'CONTROL FAILED' in str(e):
                raise
            fired.append('F2/inplace-refused')

        # (c) TRUNCATED -> MUST REFUSE.
        with open(dst, 'wb') as fh:
            fh.write(froz[:-10])
        try:
            check_freeze(repo_root, disk_path=dst)
            raise Refusal('CONTROL FAILED: F2 accepted a TRUNCATED frozen file.')
        except Refusal as e:
            if 'CONTROL FAILED' in str(e):
                raise
            fired.append('F2/truncation-refused')

    # --- and the control on the controls: the REAL pin must PASS.
    real = check_freeze(repo_root)
    if real != PREREG_SHA256_AT_COMMIT:
        raise Refusal('CONTROL FAILED: the real pin does not pass its own check.')
    if verbose:
        print(f'  C1 controls ARMED: {len(fired)} clauses driven to their failing '
              f'direction ({", ".join(fired)}), and the real pin still PASSES.')


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

# --------------------------------------------------------------------------------------
# C4 -- MAY A FORCE BE READ FROM THIS CASE AT ALL?   (amendment 6, 2026-09-13)
# --------------------------------------------------------------------------------------
# REFUSAL-ONLY, and that is what makes it addable without touching a frozen threshold:
# standing rule 5 lets a gate turn a reading INTO `NOT A RESULT` and never the reverse, so
# nothing here can produce, improve or rescue a KT -- it can only decline to serve one.
#
# 🔴 WHY.  C1, C2 and C3 test the freeze, the physics constants and the parser.  NONE of
# them asks whether the run FINISHED or whether the propeller ROTATED.  Without C4 this
# comparator reads KT and KQ off a force file whatever produced it.
#
# THE HAZARD IS MEASURED, NOT HYPOTHESISED.  On the CRM wing-body act, `SOLVE_T_SST` died of
# SIGFPE at iteration 22 with its field at p max 3.86761822375e+129, and SIX OF ITS
# TWENTY-ONE STEPS still carried a pressure Cd inside the admissible band [0, 0.2] -- +0.0800,
# +0.0538, +0.0404, +0.0170, +0.0004, +0.0091 -- while the total ran to -4.414128e+88.
# A PLAUSIBLE, BAND-PASSING COEFFICIENT OUT OF A DESTROYED SOLUTION.  And on THIS act the
# same shape has a sharper form: `dead_lever_audit.sh:8-12` records that a `cellZone MRFzone`
# naming a zone that does not exist means MRF SILENTLY DOES NOTHING, THE PROPELLER DOES NOT
# ROTATE, and the case converges to a tidy number that looks like a bad mesh rather than like
# no rotation at all.  A KT from a stationary propeller is the same family as SST's quiet
# pressure Cd: a plausible number from a dead configuration.
#
# 🔴 WHAT IS DELIBERATELY *NOT* IMPORTED.  The CRM comparator's field clause gates p and
# max|U| against ceilings registered in THAT act (2*p0 and 2*U_inf, in Pa and m/s).  THOSE
# NUMBERS DO NOT TRANSFER: PPTC is incompressible, its `p` is kinematic, and its velocity
# scale is the blade tip speed, not a freestream.  THIS PRE-REGISTRATION REGISTERS NO FIELD
# BOUND OR DIVERGENCE CRITERION -- swept for one before writing this.  So the field-ceiling
# clause is reported `BLOCKED pending registration` AND IS NOT INVENTED HERE.  Importing
# CRM's constants would be exactly the error this act has already made three times: a number
# carried across from the run that is not the run.
#
# WHAT REMAINS IS STILL DECISIVE.  G-1 alone would have refused SST: rc=136, no `End` line,
# and 21 of its registered steps reached.  A run that did not finish cannot hand over a force.

SOLVER = 'simpleFoam'


def _read_rc(case: str):
    """PPTC writes a bare integer to RC.txt and `exec_rc=N` to SOLVER_RC.txt
    (`launch_pptc.sh:104,110`).  Both are read; they must agree if both exist."""
    vals = {}
    p1 = os.path.join(case, 'RC.txt')
    if os.path.isfile(p1):
        m = re.search(r'(-?\d+)', open(p1).read())
        if m:
            vals['RC.txt'] = int(m.group(1))
    p2 = os.path.join(case, 'SOLVER_RC.txt')
    if os.path.isfile(p2):
        m = re.search(r'exec_rc=(-?\d+)', open(p2).read())
        if m:
            vals['SOLVER_RC.txt'] = int(m.group(1))
    if not vals:
        return None, 'neither RC.txt nor SOLVER_RC.txt is present'
    if len(set(vals.values())) > 1:
        return None, f'the two rc files disagree: {vals}'
    return next(iter(vals.values())), None


def _controldict_int(case: str, key: str):
    p = os.path.join(case, 'system', 'controlDict')
    if not os.path.isfile(p):
        return None
    m = re.search(r'^\s*%s\s+([^;]+);' % re.escape(key), open(p).read(), re.M)
    if not m:
        return None
    try:
        return float(m.group(1).strip())
    except ValueError:
        return None


def check_completion(case: str) -> dict:
    """Standing rule 4 on a PPTC run, using the D631 STRONGEST READING of the
    ExecutionTime clause: DISTINCT physics steps UNIONED ACROSS LOG SEGMENTS, required to be
    exactly {1 .. endTime}.  That reading is `scripts/solver_log_set.py`, adopted from
    `cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py:212`; a line count in one file
    double-counts every step a resume re-ran."""
    r: dict = {'case': case}
    rc, rc_err = _read_rc(case)
    r['rc'], r['rc_error'] = rc, rc_err
    r['clause_rc_zero'] = (rc == 0)

    end_time = _controldict_int(case, 'endTime')
    delta_t = _controldict_int(case, 'deltaT') or 1.0
    r['endTime'], r['deltaT'] = end_time, delta_t
    if end_time is None:
        r['clause_end_line'] = r['clause_last_eq_endTime'] = False
        r['clause_exec_count'] = False
        r['ok'] = False
        r['error'] = 'system/controlDict carries no readable endTime'
        return r

    # `scripts/` is resolved from THIS FILE's location, never from cwd -- the comparator
    # is run detached from the case directory and a cwd-derived root would resolve into
    # the run tree.  THE FALLBACK EXISTS FOR ONE REASON AND IT IS NOT CONVENIENCE: a
    # mutation control copies this file to a temporary directory and runs it, and
    # without the fallback the copy dies on `ModuleNotFoundError` BEFORE reaching the
    # mutated line -- so the control would report a refusal it never actually caused.
    # Found exactly that way, 2026-09-13.  The fallback is tried ONLY when the
    # file-derived path does not carry the module, so production behaviour is unchanged.
    cands = [os.path.join(REPO_ROOT_FOR_SCRIPTS, 'scripts'),
             os.path.join(_SCRIPTS_FALLBACK_ROOT, 'scripts') if _SCRIPTS_FALLBACK_ROOT
             else None]
    repo_scripts = next(
        (c for c in cands if c and os.path.isfile(os.path.join(c, 'solver_log_set.py'))),
        cands[0])
    if repo_scripts not in sys.path:
        sys.path.insert(0, repo_scripts)
    import solver_log_set as _sls
    sc = _sls.scan(case, SOLVER, end_time=end_time, delta_t=delta_t)
    r['clause_end_line'] = sc['end_line']
    r['clause_last_eq_endTime'] = sc.get('clause_last_eq_endTime', False)
    r['clause_exec_count'] = sc.get('clause_exec_count', False)
    r['last_Time'] = sc['last_time']
    r['n_steps_distinct'] = sc['n_steps']
    r['n_missing_steps'] = sc.get('n_missing_steps')
    r['n_log_segments'] = sc['n_segments']
    r['exec_count_reading'] = ('D631: distinct physics steps unioned across segments, '
                               'set == {1..endTime}')

    # fields at endTime, and THE AGE GUARD, in whichever layout the run used
    procs = sorted(d for d in os.listdir(case) if re.fullmatch(r'processor\d+', d)) \
        if os.path.isdir(case) else []
    r['n_processor_trees'] = len(procs)
    roots = [os.path.join(case, d) for d in procs] or [case]
    tname = None
    for root in roots:
        if not os.path.isdir(root):
            continue
        for nm in os.listdir(root):
            try:
                if abs(float(nm) - end_time) < 1e-9:
                    tname = nm
                    break
            except ValueError:
                continue
        if tname:
            break
    r['endTime_dirname'] = tname
    missing, newest_anchor = [], -1.0
    worst_margin = None
    for root in roots:
        td = os.path.join(root, tname) if tname else None
        zero = os.path.join(root, '0')
        if os.path.isdir(zero):
            for f in os.listdir(zero):
                try:
                    newest_anchor = max(newest_anchor, os.path.getmtime(os.path.join(zero, f)))
                except OSError:
                    pass
        if not td or not os.path.isdir(td):
            missing.append(f'{os.path.basename(root)}/{tname}')
            continue
        present = set(os.listdir(td))
        for f in ('U', 'p'):
            if f not in present:
                missing.append(f'{os.path.basename(root)}/{tname}/{f}')
    r['fields_missing'] = missing[:10]
    r['clause_fields'] = (tname is not None and not missing)
    if r['clause_fields'] and newest_anchor > 0:
        for root in roots:
            for f in ('U', 'p'):
                fp = os.path.join(root, tname, f)
                try:
                    d = os.path.getmtime(fp) - newest_anchor
                except OSError:
                    d = -1.0
                if worst_margin is None or d < worst_margin:
                    worst_margin = d
    r['age_margin_worst_s'] = worst_margin
    r['clause_age_guard'] = (worst_margin is not None and worst_margin > 0.0)

    r['ok'] = all([r['clause_rc_zero'], r['clause_end_line'], r['clause_last_eq_endTime'],
                   r['clause_exec_count'], r['clause_fields'], r['clause_age_guard']])
    return r


_ZONE_HEAD_BYTES = 65536          # the count precedes the payload; never read the payload


def zone_cell_count(path: str, zone: str):
    """Cells in `zone` as declared by an OpenFOAM `cellZones` file.  None if absent.

    🔴 WRITTEN AFTER THE FIRST READ OF A REAL FILE CAUGHT THE NAIVE VERSION.  The version
    this replaces split on the FIRST textual occurrence of the zone name and took the first
    digits-only line after it.  On a real `cellZones` the first occurrence is in the
    FoamFile header --

            meta
            {
                names           ( MRFzone );
            }

    -- so the first digits-only line after it is `1`, THE NUMBER OF ZONES.  Measured on
    `SMOKE360_J0.7985`: it reported 1 cell where the truth is 11,412,958.  The verdict
    happened to be unaffected because nothing gated on the count, but AMENDMENT 6 and the
    docstring both claimed the clause checked that the zone was NON-EMPTY, and it did not.
    An empty zone would have passed.

    Real files are `format binary`: the cell count is ASCII and PRECEDES the binary payload,
    so only the head of the file is decoded and the payload is never parsed.

    The count is taken from the zone's OWN BLOCK, located as a line that is exactly the zone
    name followed by `{`, and read from the `cellLabels ... List<label> <n>` declaration --
    the only place the cell count is stated."""
    with open(path, 'rb') as fh:
        head = fh.read(_ZONE_HEAD_BYTES).decode('utf-8', 'replace')
    # the zone's own block: a line that IS the name, then `{`. Never the header's
    # `names ( <name> )`, which is why the match is anchored to line start and end.
    m = re.search(r'^[ \t]*%s[ \t]*\r?\n[ \t]*\{' % re.escape(zone), head, re.M)
    if not m:
        return None
    seg = head[m.end():]
    mm = re.search(r'cellLabels\s+List<label>\s*\r?\n?\s*(\d+)', seg)
    if not mm:
        # an empty zone may be written as `cellLabels List<label> 0()` or with no list
        mm = re.search(r'cellLabels\s+List<label>\s*(\d+)', seg)
    return int(mm.group(1)) if mm else 0


def check_live_lever(case: str) -> dict:
    """🔴 DID THE PROPELLER ACTUALLY ROTATE?

    `constant/MRFProperties` names a `cellZone`.  If that zone is absent from
    `constant/polyMesh/cellZones`, or holds no cells, or its `omega` is zero, MRF does
    nothing and the solve is of a STATIONARY propeller -- which still produces a tidy,
    finite, plausible KT.  Structural, so it needs no registered threshold: a zone either
    exists and is non-empty, or it does not."""
    r: dict = {}
    mrf = os.path.join(case, 'constant', 'MRFProperties')
    if not os.path.isfile(mrf):
        r['ok'] = False
        r['reason'] = 'constant/MRFProperties is absent: nothing rotates this propeller'
        return r
    body = open(mrf).read()
    m = re.search(r'cellZone\s+(\w+)', body)
    if not m:
        r['ok'] = False
        r['reason'] = 'MRFProperties names no cellZone'
        return r
    zone = m.group(1)
    r['cellZone'] = zone
    om = re.search(r'omega\s+(?:constant\s+)?(-?[0-9.eE+-]+)', body)
    r['omega'] = float(om.group(1)) if om else None
    zpaths = [os.path.join(case, 'constant', 'polyMesh', 'cellZones')]
    zpaths += [os.path.join(case, d, 'constant', 'polyMesh', 'cellZones')
               for d in sorted(os.listdir(case))
               if re.fullmatch(r'processor\d+', d)] if os.path.isdir(case) else []
    found, ncells, read = False, 0, []
    for zp in zpaths:
        if not os.path.isfile(zp):
            continue
        n = zone_cell_count(zp, zone)
        if n is not None:
            found = True
            ncells += n
            read.append(f'{os.path.relpath(zp, case)}:{n}')
    r['zone_found'] = found
    r['cells_in_zone'] = ncells
    r['cellZones_read'] = read[:8]
    r['n_cellZones_files_read'] = len(read)
    if found and ncells <= 0:
        r['ok'] = False
        r['reason'] = (f'cellZone {zone!r} exists but holds {ncells} cells across '
                       f'{len(read)} cellZones file(s). AN EMPTY ZONE IS A DEAD LEVER: '
                       'MRF has nothing to rotate.')
        return r
    if not found:
        r['ok'] = False
        r['reason'] = (f'MRFProperties names cellZone {zone!r} but no cellZones file on disk '
                       'contains it. MRF IS A DEAD LEVER: the propeller does not rotate and '
                       'the case still converges to a plausible KT '
                       '(dead_lever_audit.sh:8-12).')
        return r
    if r['omega'] is not None and abs(r['omega']) == 0.0:
        r['ok'] = False
        r['reason'] = f'MRF omega is {r["omega"]}: the propeller does not rotate'
        return r
    r['ok'] = True
    return r


def force_is_readable(case: str, verbose: bool = True) -> dict:
    """C4.  Refusal-only.  Any one clause withholds every force from this case."""
    r: dict = {'refusals': [], 'clauses': {}}

    comp = check_completion(case)
    r['completion'] = comp
    r['clauses']['G-1_run_completed'] = bool(comp.get('ok'))
    if not comp.get('ok'):
        failed = [k.replace('clause_', '') for k in
                  ('clause_rc_zero', 'clause_end_line', 'clause_last_eq_endTime',
                   'clause_exec_count', 'clause_fields', 'clause_age_guard')
                  if not comp.get(k)]
        r['refusals'].append(
            'G-1: standing rule 4 is not satisfied; clauses failing: '
            + ', '.join(failed) + '. A run that did not finish cannot hand over a force.')

    lever = check_live_lever(case)
    r['live_lever'] = lever
    r['clauses']['G-2_propeller_rotates'] = bool(lever.get('ok'))
    if not lever.get('ok'):
        r['refusals'].append('G-2: ' + str(lever.get('reason')))

    # G-3 is registered as UNAVAILABLE rather than invented.  See the header note.
    r['clauses']['G-3_field_ceiling'] = 'BLOCKED'
    r['field_ceiling_note'] = (
        'BLOCKED pending registration: this pre-registration registers no field bound or '
        'divergence criterion, and CRM\'s ceilings (2*p0, 2*U_inf) are compressible-case '
        'constants that do not transfer to an incompressible propeller. NOT INVENTED HERE. '
        'G-1 alone would have refused the CRM SST artifact this clause exists for '
        '(rc=136, no End line, 21 steps of its registered length).')

    r['readable'] = not r['refusals']
    r['basis'] = ('REFUSAL-ONLY (standing rule 5): this gate can turn a force reading into '
                  'NOT A RESULT and can never produce, improve or rescue one.')
    if verbose:
        if r['readable']:
            print('    C4 PASS -- run complete under rule 4, and the MRF lever is live '
                  f'(cellZone {lever.get("cellZone")}, omega {lever.get("omega")})')
        else:
            for x in r['refusals']:
                print('    C4 REFUSE -- ' + x)
    return r


def _cellzones_text(zone: str, ncells: int) -> str:
    '''A `cellZones` file IN THE REAL SHAPE, header trap included.

    🔴 THE `meta { names ( <zone> ); }` BLOCK IS NOT DECORATION -- IT IS THE FIXTURE.
    A real OpenFOAM cellZones names the zone TWICE: once in the FoamFile header's `meta`
    block and once as the zone's own definition. The parser this replaced split on the
    FIRST occurrence, landed in the header, and read the ZONE COUNT (`1`) as the CELL
    COUNT. A fixture without this header cannot reproduce that, and the hand-written
    fixture that preceded it did not -- which is why the bug survived until a real file
    was read. Any fixture for this parser MUST carry the header.'''
    return ("""FoamFile
{
    version     2.0;
    format      ascii;
    class       regIOobject;
    location    "constant/polyMesh";
    object      cellZones;
    meta
    {
        names           ( %s );
    }
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

1
(
%s
{
    type            cellZone;
    cellLabels      List<label>
%d
(
)
;
}
)
""" % (zone, zone, ncells))


def _c4_fixture(root: str, end: int = 5, rc: int = 0, end_line: bool = True,
                steps=None, zone: str = 'MRFzone', zone_on_disk: bool = True,
                omega: float = 94.2, fields: bool = True, age_ok: bool = True,
                ncells: int = 11412958, nproc: int = 0) -> str:
    """A synthetic PPTC run that PASSES C4, unless asked to break exactly one clause."""
    os.makedirs(os.path.join(root, 'system'), exist_ok=True)
    os.makedirs(os.path.join(root, 'constant', 'polyMesh'), exist_ok=True)
    open(os.path.join(root, 'system', 'controlDict'), 'w').write(
        'application simpleFoam;\nendTime %d;\ndeltaT 1;\n' % end)
    open(os.path.join(root, 'RC.txt'), 'w').write('%d\n' % rc)
    open(os.path.join(root, 'constant', 'MRFProperties'), 'w').write(
        'MRF1\n{\n    cellZone %s;\n    active yes;\n    omega constant %g;\n}\n'
        % (zone, omega))
    if zone_on_disk and nproc == 0:
        open(os.path.join(root, 'constant', 'polyMesh', 'cellZones'), 'w').write(
            _cellzones_text(zone, ncells))
    elif zone_on_disk:
        # DECOMPOSED: each processor tree carries its own cellZones and the counts SUM.
        per = ncells // nproc
        for i in range(nproc):
            d = os.path.join(root, 'processor%d' % i, 'constant', 'polyMesh')
            os.makedirs(d, exist_ok=True)
            n = per + (ncells - per * nproc if i == nproc - 1 else 0)
            open(os.path.join(d, 'cellZones'), 'w').write(_cellzones_text(zone, n))
    else:
        open(os.path.join(root, 'constant', 'polyMesh', 'cellZones'), 'w').write(
            '0\n(\n)\n')
    ts = steps if steps is not None else list(range(1, end + 1))
    body = ''.join('Time = %d\n\nExecutionTime = %d s  ClockTime = %d s\n\n' % (t, t, t)
                   for t in ts)
    open(os.path.join(root, 'log.simpleFoam'), 'w').write(
        'Build : v2606\n' + body + ('End\n' if end_line else ''))
    # Fields live in EVERY processor tree on a decomposed run and at the case root
    # otherwise -- the same layout `check_completion` walks.  Getting this wrong is how
    # the decomposed control first went red, which is the control doing its job.
    t0 = time.time() - 10000.0
    tree_roots = ([os.path.join(root, 'processor%d' % i) for i in range(nproc)]
                  if nproc else [root])
    for tr in tree_roots:
        z = os.path.join(tr, '0')
        os.makedirs(z, exist_ok=True)
        for f in ('U', 'p'):
            fp = os.path.join(z, f)
            open(fp, 'w').write('// 0\n')
            os.utime(fp, (t0, t0))
        if fields:
            td = os.path.join(tr, str(end))
            os.makedirs(td, exist_ok=True)
            for f in ('U', 'p'):
                fp = os.path.join(td, f)
                open(fp, 'w').write('// t\n')
                m = t0 + (500.0 if age_ok else -500.0)
                os.utime(fp, (m, m))
    return root


def readable_controls(verbose: bool = True) -> None:
    """C4's FAILING-DIRECTION CONTROLS.  Every clause driven to REFUSE on a fixture built
    to break it, AND the clean fixture required to stay READABLE -- a gate that refuses
    everything is not a gate.  Run ALWAYS, before the instrument is pointed at anything
    (`spd_gate.py:257`).  Fixtures live in a tempdir, never in a run tree."""
    cases = [
        ('rc != 0 -- SST shape', dict(rc=136), 'G-1'),
        ('no End line -- SST shape', dict(end_line=False), 'G-1'),
        ('stopped short -- SST reached 21 of its length', dict(steps=[1, 2, 3]), 'G-1'),
        ('no endTime fields', dict(fields=False), 'G-1'),
        ('age guard: endTime fields older than 0/', dict(age_ok=False), 'G-1'),
        ('MRF cellZone absent from disk -- DEAD LEVER', dict(zone_on_disk=False), 'G-2'),
        ('MRF omega == 0 -- DEAD LEVER', dict(omega=0.0), 'G-2'),
        ('MRF cellZone EMPTY -- DEAD LEVER', dict(ncells=0), 'G-2'),
    ]
    fired = []
    with tempfile.TemporaryDirectory() as td:
        clean = force_is_readable(_c4_fixture(os.path.join(td, 'clean')), verbose=False)
        if not clean['readable']:
            raise Refusal('CONTROL FAILED: C4 refuses a clean run. A gate that refuses '
                          'everything is not a gate: ' + '; '.join(clean['refusals']))
        fired.append('clean-accepted')
        for i, (name, kw, clause) in enumerate(cases):
            r = force_is_readable(_c4_fixture(os.path.join(td, 'f%d' % i), **kw),
                                  verbose=False)
            if r['readable']:
                raise Refusal(f'CONTROL FAILED: C4 accepted a case built to break it '
                              f'({name}). The clause cannot fail and is therefore not a '
                              'clause.')
            if not any(x.startswith(clause) for x in r['refusals']):
                raise Refusal(f'CONTROL FAILED: {name} refused, but not on {clause} -- '
                              f'it refused on {r["refusals"][0][:60]!r}. A gate that '
                              'refuses for the wrong reason is not evidence about the '
                              'right one.')
            fired.append(clause + '/' + name.split(' --')[0].split(':')[0].strip())
        # THE COUNT MUST BE READ FROM THE ZONE'S OWN BLOCK, NOT FROM THE HEADER.
        # This is the regression control for the fault a real file caught: the naive
        # parser returned 1, the number of ZONES, and an empty zone would have passed.
        probe = _c4_fixture(os.path.join(td, 'count'), ncells=11412958)
        lev = check_live_lever(probe)
        if lev.get('cells_in_zone') != 11412958:
            raise Refusal('CONTROL FAILED: the cellZone cell count read as '
                          f'{lev.get("cells_in_zone")!r}, not 11412958. The parser is '
                          'reading the header, not the zone block -- the exact fault a '
                          'real binary cellZones caught on SMOKE360_J0.7985.')
        fired.append('G-2/count-from-zone-block')

        # DECOMPOSED: eight trees, counts must SUM. Exercised here because the
        # design-point family decomposes and a spurious refusal at 48 ranks is expensive.
        dec = _c4_fixture(os.path.join(td, 'dec'), nproc=8, ncells=11412958)
        levd = check_live_lever(dec)
        if levd.get('cells_in_zone') != 11412958 or levd.get('n_cellZones_files_read') != 8:
            raise Refusal('CONTROL FAILED: decomposed cellZones did not sum across trees '
                          f'({levd.get("cells_in_zone")!r} from '
                          f'{levd.get("n_cellZones_files_read")!r} files).')
        if not force_is_readable(dec, verbose=False)['readable']:
            raise Refusal('CONTROL FAILED: a clean DECOMPOSED run was refused.')
        fired.append('G-2/decomposed-sum')

        # MRFProperties missing entirely
        root = _c4_fixture(os.path.join(td, 'nomrf'))
        os.remove(os.path.join(root, 'constant', 'MRFProperties'))
        r = force_is_readable(root, verbose=False)
        if r['readable']:
            raise Refusal('CONTROL FAILED: C4 accepted a case with no MRFProperties.')
        fired.append('G-2/MRFProperties-absent')
    if verbose:
        print(f'  C4 controls ARMED: {len(fired)} clauses driven '
              f'({len(fired) - 1} to REFUSE, the clean fixture to READABLE).')


# --------------------------------------------------------------------------------------
# PROVENANCE -- IS THIS THE OUTPUT OF A REAL SOLVE?   (amendment 9, 2026-09-13)
# --------------------------------------------------------------------------------------
# 🔴 THE HAZARD, FOUND BY ARMING C3 BEFORE THE MESH LANDED.  The registered synthetic forces
# tree (`plant_calibration/make_synthetic_forces.py`) is built FROM the measured KT 0.5052,
# so reading 0.5052 back is A ROUND TRIP OF THE ALGEBRA AND NOT EVIDENCE ABOUT THE FLOW.
# Run end to end on it, this comparator printed `VERDICT: PASS` with the real bands, the real
# eta_O and deviations of +0.00% -- BYTE-INDISTINGUISHABLE FROM A GENUINE VERDICT.  In a
# report, a board block or a screenshot it reads as a PPTC pass, and nothing downstream can
# tell.
#
# THE POLARITY IS DELIBERATE AND IT IS THE WHOLE DESIGN.  This does NOT try to detect a
# synthetic tree -- a synthetic tree built some other way would slip through and the marker
# would be worse than useless for being trusted.  IT REQUIRES POSITIVE EVIDENCE OF A REAL
# SOLVE and treats everything else as UNVERIFIED.  Same doctrine as standing rule 3: the
# default is not-shown-to-be-real, and the burden is on the artifact.
#
# IT CANNOT MOVE A VERDICT, IN EITHER DIRECTION.  It labels.  A real PASS prints exactly as
# it printed before this amendment; an unverified one prints the same verdict token WITH its
# provenance attached, and `_emit_verdict` makes a bare `VERDICT: PASS` on unverified input
# STRUCTURALLY UNREACHABLE rather than merely discouraged.

PROV_REAL = 'REAL-SOLVE'
PROV_UNVERIFIED = 'UNVERIFIED-PROVENANCE'


def provenance(case: str) -> dict:
    """Positive evidence that `case` holds the output of a real OpenFOAM solve.

    OpenFOAM writes a banner no fixture generator reproduces by accident -- `Build  :`,
    `Exec   :`, `nProcs :` and `Case   :`.  The `Case   :` line names the directory the
    solver actually ran in, so a log copied in from elsewhere does not confer provenance on
    the tree it was copied into."""
    r: dict = {'evidence': [], 'missing': []}
    log = os.path.join(case, 'log.' + SOLVER)
    if not os.path.isfile(log):
        r['missing'].append(f'no log.{SOLVER} in the case')
        r['status'] = PROV_UNVERIFIED
        r['reason'] = (f'no solver log: nothing in this tree shows a solver ever ran in it')
        return r
    with open(log, errors='replace') as fh:
        head = fh.read(8192)
    for key in ('Build  :', 'Exec   :', 'nProcs :', 'Case   :'):
        (r['evidence'] if key in head else r['missing']).append(key.strip())
    m = re.search(r'^Case   : (.+)$', head, re.M)
    r['case_line'] = m.group(1).strip() if m else None
    same = False
    if r['case_line']:
        try:
            same = os.path.realpath(r['case_line']) == os.path.realpath(case)
        except OSError:
            same = False
    r['case_line_matches_this_tree'] = same
    if r['missing'] or not same:
        r['status'] = PROV_UNVERIFIED
        r['reason'] = ('the solver log does not establish that this tree is a real solve'
                       + (f'; missing banner fields {r["missing"]}' if r['missing'] else '')
                       + ('' if same else
                          f'; its `Case` line names {r["case_line"]!r}, not this directory'))
        return r
    r['status'] = PROV_REAL
    r['reason'] = 'solver banner present and its Case line names this directory'
    return r


def _emit_verdict(verdict: str, prov: dict) -> str:
    """THE ONLY PLACE A VERDICT IS RENDERED.  Returns the string to print.

    On unverified provenance the verdict token NEVER appears unqualified -- not as a
    convention but because this function is the single emitter and it appends the
    qualification unconditionally."""
    if prov.get('status') == PROV_REAL:
        return f'VERDICT: {verdict}'
    return (f'VERDICT: {verdict}   [{PROV_UNVERIFIED} -- NOT A RESULT ABOUT VP1304]')


def _provenance_banner(prov: dict) -> str:
    if prov.get('status') == PROV_REAL:
        return ''
    return (
        '\n' + '=' * 78 +
        '\n  🔴 UNVERIFIED PROVENANCE -- THIS IS NOT A RESULT ABOUT THE PPTC PROPELLER.'
        '\n  ' + str(prov.get('reason')) +
        '\n  Every number ABOVE is a round trip of this comparator\'s own algebra over'
        '\n  whatever was in the input tree. It demonstrates that the pipeline computes;'
        '\n  it is evidence about NO propeller. Do not quote it, plot it or screenshot it'
        '\n  as a PPTC coefficient.'
        '\n' + '=' * 78)


def provenance_controls(verbose: bool = True) -> None:
    """The marker's failing direction, both ways: a synthetic tree MUST be marked, a real
    one MUST NOT be, and NEITHER may move a verdict."""
    real_banner = ('/*------------------*- C++ -*------------------*\\\n'
                   'Build  : _481094f-20260618 OPENFOAM=2606 version=2606\n'
                   'Arch   : "LSB;label=32;scalar=64"\n'
                   'Exec   : %s -parallel\nDate   : Sep 13 2026\n'
                   'nProcs : 8\nCase   : %s\n')
    with tempfile.TemporaryDirectory() as td:
        syn = os.path.join(td, 'syn')
        os.makedirs(syn, exist_ok=True)
        p_syn = provenance(syn)
        if p_syn['status'] != PROV_UNVERIFIED:
            raise Refusal('CONTROL FAILED: a tree with no solver log was accepted as a '
                          'real solve. The marker cannot fire and is not a marker.')
        if 'VERDICT: PASS' == _emit_verdict('PASS', p_syn):
            raise Refusal('CONTROL FAILED: a BARE `VERDICT: PASS` was emitted on '
                          'unverified provenance.')

        real = os.path.join(td, 'real')
        os.makedirs(real, exist_ok=True)
        open(os.path.join(real, 'log.' + SOLVER), 'w').write(real_banner % (SOLVER, real))
        p_real = provenance(real)
        if p_real['status'] != PROV_REAL:
            raise Refusal('CONTROL FAILED: a tree carrying a real OpenFOAM banner whose '
                          '`Case` line names it was NOT accepted. The marker fires on '
                          f'everything, which is not a marker: {p_real.get("reason")}')
        if _emit_verdict('PASS', p_real) != 'VERDICT: PASS':
            raise Refusal('CONTROL FAILED: the marker altered a REAL verdict. It labels; '
                          'it does not adjudicate.')
        if _provenance_banner(p_real) != '':
            raise Refusal('CONTROL FAILED: the banner printed on a real solve.')

        # A BORROWED LOG CONFERS NOTHING: same banner, another directory's Case line.
        borrowed = os.path.join(td, 'borrowed')
        os.makedirs(borrowed, exist_ok=True)
        open(os.path.join(borrowed, 'log.' + SOLVER), 'w').write(
            real_banner % (SOLVER, real))
        if provenance(borrowed)['status'] != PROV_UNVERIFIED:
            raise Refusal('CONTROL FAILED: a log copied in from another case conferred '
                          'provenance on the tree it was copied into.')

        # and the verdict TOKEN is untouched in both directions
        for v in ('PASS', 'GATE FAIL', 'NOT A RESULT'):
            if not _emit_verdict(v, p_syn).startswith(f'VERDICT: {v}'):
                raise Refusal(f'CONTROL FAILED: the marker changed the {v!r} token.')
    if verbose:
        print('  provenance controls ARMED: no-log marked, real banner accepted, borrowed '
              'log refused, verdict token unchanged in both directions.')


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
    ap.add_argument('--json', action='store_true',
                    help='emit the machine-readable row, provenance included')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    globals()['_SCRIPTS_FALLBACK_ROOT'] = os.path.abspath(a.repo_root)

    try:
        # THE CONTROLS RUN ALWAYS, BEFORE THE INSTRUMENT IS POINTED AT ANYTHING -- the
        # habit taken from verification/runs/PPTC_VP1304_runs/spd_gate.py:257. An
        # instrument armed once and trusted thereafter is an instrument nobody is
        # checking, and a freeze check repaired into one that CANNOT FAIL would be far
        # worse than the one that was failing too often.
        print('C1  FREEZE     verifying the frozen pre-registration is the file that ran')
        freeze_controls(a.repo_root)
        print(f'    frozen text at {PREREG_COMMIT[:9]} sha256 {check_freeze(a.repo_root)}'
              '  -- C1 PASS')
        print('C2  SELF-TEST  reproducing Report 3752 page 2.12 measured N and Nm from its '
              'own page 2.13 coefficients')
        check_selftest()

        if a.selftest:
            print('\nSELF-TEST COMPLETE. C1 and C2 pass. C3 requires a case with forces output.')
            return 0

        if not a.case or a.J is None:
            raise Refusal('--case and --J are required unless --selftest is given')

        print('C5  PROVENANCE is this the output of a REAL solve? (labels; never adjudicates)')
        provenance_controls()
        _prov = provenance(a.case)
        print(f'    {_prov["status"]} -- {_prov["reason"]}')

        print('C4  READABLE   may a force be read from this case at all? (refusal-only)')
        readable_controls()
        _fr = force_is_readable(a.case)
        if not _fr['readable']:
            raise Refusal('C4: no force may be read from this case.\n    '
                          + '\n    '.join(_fr['refusals']))

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
        print('\n' + _emit_verdict(g['verdict'], _prov))
        if g['verdict'] == 'GATE FAIL':
            m = max(abs(g['d_kt']) - BAND_PCT[g['J']][0], abs(g['d_kq']) - BAND_PCT[g['J']][1])
            print(f'  margin outside the band: {m:+.2f} percentage points')
        print('  NOTE: this verdict is subject to Roache triple gating. A row whose grid '
              'triple is not CONVERGING is NOT A RESULT whatever this says.')
        print(_provenance_banner(_prov))

        if a.json:
            # THE MARKER TRAVELS IN THE MACHINE-READABLE ROW TOO. An aggregator that lifts
            # `verdict` out of a JSON row and drops the human banner would otherwise carry a
            # synthetic PASS into a table with nothing attached to it.
            json.dump({'case': os.path.abspath(a.case), 'J': g['J'],
                       'KT': kt_v, 'tenKQ': tenkq, 'eta_O': eta,
                       'verdict': g['verdict'],
                       'verdict_rendered': _emit_verdict(g['verdict'], _prov),
                       'provenance': _prov.get('status'),
                       'provenance_reason': _prov.get('reason'),
                       'is_a_result_about_VP1304': _prov.get('status') == PROV_REAL,
                       'deviation_pct': {'KT': g['d_kt'], 'tenKQ': g['d_kq']},
                       'comparator': os.path.abspath(__file__),
                       'prereg_commit': PREREG_COMMIT,
                       'roache_note': 'subject to Roache triple gating (standing rule 5)'},
                      sys.stdout, indent=1)
            sys.stdout.write('\n')
        return 0

    except Refusal as e:
        print(f'\nREFUSE: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
