#!/usr/bin/env python3
"""STEP-0 NEGATIVITY READER -- DMR R3 numerics-robustness diagnostic.

**************************************************************************
*  THIS IS A MEASUREMENT SCRIPT.  FLAG FOR THE cfd SUPERVISOR'S §3      *
*  CHECK-1 (measurement-script diffs read as diffs).                   *
**************************************************************************

WHAT IT MEASURES (answer-blind; heeds L-501)
--------------------------------------------
The R3p (1/240) positivity successor SIGFPE'd in `Foam::sqrt(Field&,...)` inside
`rhoCentralFoam` at t = 0.11648.  The stack trace names only the sqrt-of-Field
call and CANNOT tell apart its two physical sites:
  * rhoCentralFoam.C:136  volScalarField c = sqrt(Cp/Cv * rPsi)  -- the CELL-CENTRE
    sound speed; a negative argument here means a negative CELL-CENTRE temperature
    (a post-update energy/positivity failure).
  * rhoCentralFoam.C:137/143  cSf_pos, cSf_neg -- the RECONSTRUCTED FACE sound
    speeds; a negative argument here means a reconstructed FACE temperature
    undershoot below zero (a limiter/reconstruction failure).

STEP 0 restarts R3p from t = 0.10 with a `fieldMinMax` functionObject on
(T e p rho U), `location yes`, `writeControl timeStep`, and NO numerics change,
so the min/max and the CELL LOCATION of the extremum are recorded EVERY step
through the failing window.  This reader parses that output and reports which
physical scalar field FIRST goes negative, at what time, and WHERE -- the
answer-blind measurement that selects the mechanism-appropriate lever.  It reads
NO scheme file and grades NO gate; it produces a MEASUREMENT, not a verdict.

TWO-SIDED PLANTED-ZERO CONTROL (CLAUDE.md rule 3; "plant the zero"; cf. L-459
"take the number, never the tool's own OK line")
-------------------------------------------------------------------------------
A "no field went negative" answer -- or any answer -- from a reader NOT SHOWN
able to see a known negative is not evidence.  Before any real report this reader:
  (1) plants a KNOWN NEGATIVE extremum into a COPY of the just-parsed records at
      a time earlier than any real row (so it MUST be the detected first-negative)
      and reads it back THROUGH THE SAME parse+detect path; if the planted
      negative is not recovered it REFUSES (exit 2) -- the reader is blind and its
      "which field went negative" answer is worthless.
  (2) plants an ABSENCE (all mins clamped strictly positive) and requires the
      detector to return "no negative" -- it must not hallucinate a negative on
      clean data.
The control "fires both ways": with the detector healthy the plant is SEEN
(exit 0); with the detector deliberately BLINDED (`--selftest-blind`, or env
DMR_STEP0_BLIND=1) it CANNOT see the plant and the control REFUSES (exit 2).

Usage:
    step0_negativity_reader.py <fieldMinMax.dat | postProcessing dir> [--out PATH]
    step0_negativity_reader.py --selftest        # control SEEN arm  -> exit 0
    step0_negativity_reader.py --selftest-blind  # control BLIND arm  -> exit 2

`--out` is REQUIRED to write and this reader NEVER overwrites an existing file.
"""
import os
import re
import sys
import json
import copy
import argparse
import tempfile
from pathlib import Path

# The physical scalar fields REPORTED as diagnostic context.  mag(U) is a
# magnitude (>= 0 by construction) so it is reported but never a negativity flag.
PHYS_SCALARS = ("T", "e", "p", "rho")

# The fields whose negativity is PHYSICALLY unbounded-below and so DRIVES
# first_negative and the mechanism attribution: T (thermodynamic temperature,
# > 0 required for the sqrt in the cell-centre sound speed) and rho (density,
# > 0 required).  `e` and `p` are DELIBERATELY EXCLUDED from the trigger: under
# this thermo `e` is SENSIBLE internal energy (Hf 0, sensible baseline) and is
# REFERENCE-RELATIVE, so it is legitimately negative from the first step and, left
# in the trigger, emits a FALSE-EARLY first_negative on `e` that MASKS the physical
# T signal; `p` follows T*rho and is reported, not triggered.  `e` and `p` remain
# in PHYS_SCALARS for diagnostic-context reporting only.
POSITIVITY_SCALARS = ("T", "rho")

# The planted control's known negative extremum.  Integer-free, distinctive.
PLANT_FIELD = "T"
PLANT_VALUE = -1.2345678e00
PLANT_TIME = -1.0                       # earlier than any real row -> must be first
PLANT_LOC = (0.5000000, 0.9000000, 0.0050000)
PLANT_TOL = 1e-9


class ReaderRefused(Exception):
    """The reader cannot testify.  Never downgrade this to a None or a zero."""


def _blind_env():
    return os.environ.get("DMR_STEP0_BLIND", "") not in ("", "0", "false", "False")


def _parse_loc(tok):
    m = re.search(r"\(([^)]*)\)", tok)
    if m is None:
        raise ReaderRefused(f"location token {tok!r}: no parenthesised vector")
    parts = m.group(1).split()
    if len(parts) != 3:
        raise ReaderRefused(f"location token {tok!r}: expected 3 components, got {len(parts)}")
    return tuple(float(x) for x in parts)


def parse_fieldminmax(dat_path):
    """Parse an OpenFOAM fieldMinMax .dat.  Refuses rather than guessing.

    Handles BOTH serial (Time field min location(min) max location(max)) and
    parallel (... +processor columns) layouts by reading the header line and
    resolving column indices by name.  Columns are tab-separated; a location
    vector `(x y z)` contains spaces but no tab, so a tab split keeps it whole.
    """
    p = Path(dat_path)
    if not p.exists():
        raise ReaderRefused(f"{p}: fieldMinMax output absent -- an absent probe reads ABSENT, never clean")
    lines = p.read_text().splitlines()
    header = None
    for ln in lines:
        if ln.lstrip().startswith("#") and "field" in ln and "min" in ln and "location(min)" in ln:
            header = ln
            break
    if header is None:
        raise ReaderRefused(f"{p}: no fieldMinMax header line (field/min/location(min)) matched")
    cols = [c.strip() for c in header.lstrip("#").split("\t")]
    cols = [c for c in cols if c != ""]
    # Column names are unique for the ones we need (Time, field, min,
    # location(min)); 'processor'/'max' duplicates are irrelevant here.
    try:
        i_time = cols.index("Time")
        i_field = cols.index("field")
        i_min = cols.index("min")
        i_locmin = cols.index("location(min)")
    except ValueError as exc:
        raise ReaderRefused(f"{p}: header missing a required column ({exc}); cols={cols}")

    recs = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        toks = [t.strip() for t in ln.split("\t")]
        toks = [t for t in toks if t != ""]
        need = max(i_time, i_field, i_min, i_locmin)
        if len(toks) <= need:
            raise ReaderRefused(
                f"{p}: data row has {len(toks)} tab-columns, need index {need}; row={ln!r}")
        recs.append(dict(
            time=float(toks[i_time]),
            field=toks[i_field],
            min=float(toks[i_min]),
            loc_min=_parse_loc(toks[i_locmin]),
        ))
    if not recs:
        raise ReaderRefused(f"{p}: header present but no data rows -- the probe wrote no steps")
    return recs


def first_negative(records, blind=False):
    """Earliest (time, field) among POSITIVITY_SCALARS (T, rho) whose min < 0.

    Returns the record dict of the first-negative, or None if none is negative.
    Keyed on T and rho ONLY -- `e` (reference-relative sensible energy) and `p`
    are diagnostic context, never a negativity trigger (see POSITIVITY_SCALARS).
    `blind` disables the negativity test (simulating a reader that cannot see a
    negative) -- used ONLY by the control's blind arm to prove the control
    fails closed.
    """
    blind = blind or _blind_env()
    hits = []
    for r in records:
        if r["field"] not in POSITIVITY_SCALARS:
            continue
        is_neg = (r["min"] < 0.0) and not blind
        if is_neg:
            hits.append(r)
    if not hits:
        return None
    # earliest time; tie -> most negative
    hits.sort(key=lambda r: (r["time"], r["min"]))
    return hits[0]


# ---------------------------------------------------------------------------
# THE TWO-SIDED PLANTED CONTROL.
# ---------------------------------------------------------------------------

def _plant_seen(records, blind=False):
    """Inject a KNOWN negative earlier than any real row; it must be recovered."""
    aug = copy.deepcopy(records)
    aug.insert(0, dict(time=PLANT_TIME, field=PLANT_FIELD,
                       min=PLANT_VALUE, loc_min=PLANT_LOC))
    hit = first_negative(aug, blind=blind)
    if hit is None:
        return False
    ok = (hit["field"] == PLANT_FIELD
          and abs(hit["min"] - PLANT_VALUE) < PLANT_TOL
          and abs(hit["time"] - PLANT_TIME) < PLANT_TOL
          and all(abs(a - b) < PLANT_TOL for a, b in zip(hit["loc_min"], PLANT_LOC)))
    return ok


def _plant_absence(records, blind=False):
    """Clamp all mins strictly positive; the detector must find NO negative."""
    clean = copy.deepcopy(records)
    for r in clean:
        if r["min"] < 0.0:
            r["min"] = abs(r["min"]) + 1.0
    return first_negative(clean, blind=blind) is None


def run_control(records, verbose=True):
    """Two-sided control run before any real report.  Refuses (exit 2) if blind."""
    blind = _blind_env()
    seen = _plant_seen(records, blind=blind)
    absence_ok = _plant_absence(records, blind=blind)
    if verbose:
        print(f"  CONTROL planted negative : planted {PLANT_FIELD}={PLANT_VALUE:.7e} "
              f"@ t={PLANT_TIME} loc={PLANT_LOC} -> {'SEEN' if seen else 'NOT SEEN'}")
        print(f"  CONTROL planted absence  : clean data -> "
              f"{'NO FALSE NEGATIVE' if absence_ok else 'HALLUCINATED A NEGATIVE'}")
    if not (seen and absence_ok):
        raise ReaderRefused(
            "PLANTED CONTROL FAILED. No field-negativity call from this reader is "
            f"evidence. planted-seen={seen}, absence-clean={absence_ok}"
            + ("  [DMR_STEP0_BLIND active]" if blind else ""))
    return True


def _annotate_region(loc):
    """Light physics anchor from the extremum location; ANNOTATION, not a claim."""
    x, y = loc[0], loc[1]
    if x < 0.5 and y < 0.3:
        return "near reflecting-wall / Mach-stem foot (x<0.5, y<0.3)"
    if 0.3 <= y <= 0.9 and x < 1.5:
        return "reflected-shock / triple-point region (approx)"
    return "elsewhere in the domain"


def measure(dat_path):
    """Parse, run the control FIRST, then report the first-negative measurement."""
    recs = parse_fieldminmax(dat_path)
    print(f"planted control on {dat_path} ({len(recs)} field-rows parsed):")
    run_control(recs)

    hit = first_negative(recs)
    times = sorted({r["time"] for r in recs})
    per_field = {}
    for f in PHYS_SCALARS:
        fr = [r for r in recs if r["field"] == f]
        if fr:
            mn = min(fr, key=lambda r: r["min"])
            per_field[f] = dict(min=mn["min"], time=mn["time"], loc_min=list(mn["loc_min"]))
    if hit is None:
        verdict = ("NO NEGATIVE OBSERVED in (T rho) across the written steps; "
                   "the failing step may not have been captured, or the FPE argument "
                   "went negative between writes -- inconclusive, not a clean pass.")
        site = None
    else:
        # cell vs face is NOT read from the .dat (the probe records cell-centre
        # field extrema); the LOCATION + which field disambiguates the mechanism.
        site = ("rhoCentralFoam.C:136 cell-centre sound speed (post-update "
                "energy/positivity failure)" if hit["field"] in ("T",)
                else "flux/energy field first-negative")
        verdict = (f"FIRST NEGATIVE: field {hit['field']} min={hit['min']:.6e} "
                   f"at t={hit['time']:g}, location {tuple(hit['loc_min'])} "
                   f"-- {_annotate_region(hit['loc_min'])}")
    result = dict(
        reader="step0_negativity_reader.py",
        control="two-sided planted-zero, run before reporting (rule 3)",
        dat=str(dat_path),
        n_field_rows=len(recs),
        times=times,
        per_field_min=per_field,
        first_negative=(None if hit is None else dict(
            field=hit["field"], min=hit["min"], time=hit["time"],
            loc_min=list(hit["loc_min"]),
            region=_annotate_region(hit["loc_min"]))),
        mechanism_note=site,
        verdict=verdict,
    )
    return result


# ---------------------------------------------------------------------------
# Synthetic fixture for the selftest -- a small valid fieldMinMax .dat.  The
# selftest exercises the REAL parse + detect path via a temp file on disk.
# ---------------------------------------------------------------------------
_SYNTH = (
    "# Field minima and maxima\n"
    "# Time            \tfield             \tmin               \tlocation(min)     \tprocessor         \tmax               \tlocation(max)     \tprocessor         \n"
    "0.10000000        \tT                 \t9.5000000000e-01\t(1.0000000000e+00 5.0000000000e-01 5.0000000000e-03)\t0\t2.0000000000e+01\t(2.0e-01 9.0e-01 5.0e-03)\t1\n"
    "0.10000000        \tmag(U)            \t0.0000000000e+00\t(3.0e-02 3.0e-02 0.0e+00)\t0\t7.0e+00\t(1.0e+00 5.0e-01 5.0e-03)\t1\n"
    "0.10000000        \tp                 \t9.9000000000e-01\t(3.5e+00 5.0e-01 5.0e-03)\t0\t1.2e+02\t(2.0e-01 9.0e-01 5.0e-03)\t1\n"
    "0.10000000        \trho               \t1.3900000000e+00\t(3.5e+00 5.0e-01 5.0e-03)\t0\t8.0e+00\t(2.0e-01 9.0e-01 5.0e-03)\t1\n"
)


def _synth_records():
    with tempfile.NamedTemporaryFile("w", suffix=".dat", delete=False) as f:
        f.write(_SYNTH)
        tmp = f.name
    try:
        return parse_fieldminmax(tmp)
    finally:
        os.unlink(tmp)


def selftest(blind):
    recs = _synth_records()
    if not blind:
        seen = _plant_seen(recs, blind=False)
        absence_ok = _plant_absence(recs, blind=False)
        print(f"SELFTEST (healthy): planted negative -> {'SEEN' if seen else 'NOT SEEN'}; "
              f"clean data -> {'NO FALSE NEGATIVE' if absence_ok else 'HALLUCINATED'}")
        if seen and absence_ok:
            print("SELFTEST: PASS -- control SEES the planted negative and stays "
                  "silent on clean data. exit 0")
            return 0
        print("SELFTEST: FAIL -- control could not see a planted negative on healthy "
              "data; this reader must not be trusted. exit 2")
        return 2
    # blind arm: the detector is deliberately blinded; the control MUST refuse.
    seen = _plant_seen(recs, blind=True)
    print(f"SELFTEST-BLIND (detector blinded): planted negative -> "
          f"{'SEEN' if seen else 'NOT SEEN'}")
    if not seen:
        print("SELFTEST-BLIND: control CORRECTLY REFUSES -- a blinded reader cannot "
              "see the planted negative, so its answer is not evidence. exit 2")
        return 2
    print("SELFTEST-BLIND: CONTROL BROKEN -- the plant was 'seen' while blinded; "
          "the control does not fail closed. exit 3")
    return 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?",
                    help="fieldMinMax.dat, or a postProcessing dir to search under")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-blind", dest="selftest_blind", action="store_true")
    a = ap.parse_args()

    if a.selftest and a.selftest_blind:
        raise SystemExit("choose one of --selftest / --selftest-blind")
    if a.selftest:
        return selftest(blind=False)
    if a.selftest_blind:
        return selftest(blind=True)

    if not a.target:
        raise SystemExit("usage: step0_negativity_reader.py <fieldMinMax.dat|dir> "
                         "[--out PATH] | --selftest | --selftest-blind")

    t = Path(a.target)
    if t.is_dir():
        cands = sorted(t.rglob("fieldMinMax.dat"))
        if not cands:
            raise ReaderRefused(f"{t}: no fieldMinMax.dat found under it")
        t = cands[-1]
        print(f"(resolved to {t})")

    result = measure(t)
    out = json.dumps(result, indent=1)
    print(out)
    print("\n" + result["verdict"])
    if a.out:
        p = Path(a.out)
        if p.exists():
            raise ReaderRefused(
                f"{p} already exists. This reader never overwrites a result file.")
        p.write_text(out)
        print(f"\nwritten: {p}")
    else:
        print("\n(no --out given: nothing written)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReaderRefused as exc:
        print(f"\nREADER REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
