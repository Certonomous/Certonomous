#!/usr/bin/env python3
"""
F11 CONVERSION -- THE FROZEN GRADING PATH.

This file implements, and only implements, the pre-registration frozen at
``verification/campaign/F11_CONVERSION_PREREGISTRATION.md`` (committed
157793db5ff6bbdda7ab22299abe5725d96e9b37).  Every station, reference value,
band, band interval, cell count, plant constant, plateau threshold, plateau
window, completion clause, dimensionality and ratio form below is TRANSCRIBED
from that document.  NOTHING here was chosen by the author of this file.  Its
sha256 is recorded in that document's dated PRE-COMPUTE addendum under
section 8.2, and this script REFUSES to grade until that addendum exists.

WHAT THIS FILE DOES NOT DO.  It does not implement GCI, Richardson
extrapolation or rule 5's ordering.  Those live in the shared instrument
``scripts/roache_triple.py``, frozen at git blob
``8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`` (section 8.1), and this file
verifies the module it imports IS that blob before it grades anything.  Rule 5
is applied by ``roache_triple.grade_ladder`` and by nothing here.

WHERE THE TWO HALVES OF THE PLATEAU LIVE (2026-08-25 PRE-COMPUTE AMENDMENT,
arm B).  A mechanism probe measured that the frozen section 6.1 arrangement --
the `centerlineProfiles` object itself on `timeStep` / 250 -- writes NOTHING at
the early `residualControl` stop, so `centerlineProfiles/<N>/` never exists and
the frozen clause C4 fails by construction on every run.  The amendment leaves
`centerlineProfiles` at `onEnd` and adds a SEPARATELY NAMED `centerlineSeries`
object at `timeStep` / 250.  In this file that means, and means only:

  * THE GRADED VALUE and the completion clauses C4 / C6 still read
    `postProcessing/centerlineProfiles/<N>/` -- the frozen literal path,
    untouched, at the CONVERGED iteration;
  * the plateau's EARLIER samples are read from
    `postProcessing/centerlineSeries/`, its final sample being the same
    converged artifact the gate grades.

No band, station, reference, completion clause or verdict changed.  An absent
or too-short series is UNMEASURED, never a pass, and NO FALLBACK to the last
periodic sample is taken -- that would grade the drift of a materially
less-converged state.

REFUSAL DISCIPLINE (CLAUDE.md rule 4).  This comparator refuses (exit 2)
rather than degrade.  A planted-zero control that cannot see its plant
refuses.  A level failing any clause of the completion rule is NOT graded --
it carries the label, never a number, and its ladder is NOT A RESULT.  An
unmeasured plateau is reported UNMEASURED and drives NOT A RESULT through
rule 5 step (a); it is never reported as passed.

THE ONE THING A READER SHOULD CHECK FIRST.  Station selection is where this
suite can most easily grade the wrong number, and the frozen document says so
(section 3.2 route 1).  The row is selected by COORDINATE, the matched
coordinate is asserted against the registered station, and PZ-2 requires the
selector to be shown UNABLE to see a plant at any other station in the file.

EXIT CODES, the instrument's own convention: 0 = PASS, 1 = GATE FAIL,
3 = NOT A RESULT, 2 = REFUSE.  A gate that was never launched prints PENDING
and, having no grade at all, exits in the 3 class -- stated here because it is
a display/exit mapping and not a verdict: the printed verdict stays PENDING
(section 9: PENDING is never used to soften a fail).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
F11_ROOT = os.path.dirname(HERE)                  # verification/runs/F11_runs
REPO = os.path.dirname(os.path.dirname(os.path.dirname(F11_ROOT)))
REL_SELF = os.path.relpath(os.path.abspath(__file__), REPO)
REL_PEER = os.path.join(os.path.dirname(REL_SELF), "rerun_f11.py")

sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, F11_ROOT)

import roache_triple as RT                                          # noqa: E402


# ===========================================================================
# 0.  REFUSAL
# ===========================================================================

class Refusal(Exception):
    """Raised where the selftest can catch it; the CLI turns it into exit 2."""


def refuse(msg):
    raise Refusal(msg)


# ===========================================================================
# 1.  FROZEN CONSTANTS -- transcribed from the pre-registration, not chosen
# ===========================================================================

PREREG_REL = "verification/campaign/F11_CONVERSION_PREREGISTRATION.md"
PREREG_FREEZE_COMMIT = "157793db5ff6bbdda7ab22299abe5725d96e9b37"

# --- section 8.1: the shared instrument, fixed BY BLOB and not by path ------
INSTRUMENT_REL = "scripts/roache_triple.py"
INSTRUMENT_BLOB = "8dee0d31e94d3f59d28658f88a4cd6df80ae8e39"
INSTRUMENT_SHA256 = \
    "452f475181c9897000ea530b39a84bd3e7e9927e0a3fd39fe8b1105f538ac051"

# --- section 4.4: the grid triple, dimensionality and ratio form ------------
DIM = 2                     # stated, never defaulted (VERIFICATION 3.1)
FORM = "equal"              # asserted, never "auto" -- the instrument REFUSES
                            # an unequal ladder handed to the equal path
FS = 1.25                   # Roache safety factor (instrument constant)

# --- section 6: the run matrix.  (level name, n, cells, endTime) ------------
LEVELS = (
    ("coarse", 32, 1024, 4000),
    ("medium", 64, 4096, 4000),
    ("fine", 128, 16384, 9000),
)
LEVEL_NAMES = tuple(lv[0] for lv in LEVELS)
CELLS = {lv[0]: lv[2] for lv in LEVELS}
END_TIME = {lv[0]: lv[3] for lv in LEVELS}
RUNGS = ("re1000", "re100")            # launch order, section 7

# --- section 4.6: planted-zero controls -------------------------------------
PLANT = 1.234e-03                      # the lab constant (roache_triple.PLANT)
PZ_TOL = 1.0e-12                       # "differs ... by > 1e-12"
NEAREST_COORD_TOL = 1.0e-6             # PZ-3 "nearest-coordinate match (1e-6)"
COORD_ROUND = 4                        # PZ-3 "the round(coord, 4) lookup"

# --- section 4.3 / 4.5: plateau ---------------------------------------------
PLATEAU_TOL = 1.0e-6                   # lid-speed units
PLATEAU_MIN_ITER_GAP = 250             # "at least 250 iterations before it"

# --- the .xy artifact layout -------------------------------------------------
# OpenFOAM `sets` with `setFormat raw`, a `cloud` set and `fields (U)` writes
# SIX whitespace-separated columns and NO header line: x y z Ux Uy Uz.  There
# are therefore NO COLUMN NAMES to match on, and that is a fact about the
# format, not a shortcut taken here.  What replaces a name match, and is
# asserted on every read:
#   * the column count is exactly 6 and every field parses as a float;
#   * if a `#` header IS present (some OpenFOAM builds emit one) its names are
#     parsed and a disagreement with this layout REFUSES;
#   * the profile's FIXED coordinate is constant over every row and equals the
#     registered value -- this is what catches a swapped or wrong file;
#   * the graded ROW is selected by COORDINATE, never by index, and the
#     coordinate actually matched is asserted against the registered station.
XY_COLUMNS = ("x", "y", "z", "Ux", "Uy", "Uz")
COL = {name: i for i, name in enumerate(XY_COLUMNS)}

# set name -> (fixed coordinate axis, its frozen value, varying axis)
PROFILES = {
    "uAlongX05": dict(fixed_axis="x", fixed_value=0.5, station_axis="y"),
    "vAlongY05": dict(fixed_axis="y", fixed_value=0.5, station_axis="x"),
}
COMPONENT_OF = {"u": "Ux", "v": "Uy"}

# --- section 3: THE SIX GATES ------------------------------------------------
# reference, band half-width and band interval are all transcribed literally.
# b_pos / b_ref are section 4.2's split, reported beside every row (3.4) and
# used by no verdict.  weak_bar / can_bite are section 3.2 route 2 and section
# 4.2's own declarations, printed on the row's face as those sections require.
GATES = (
    dict(id="G-F11-1", rung="re100", re=100, profile="uAlongX05",
         component="u", station=0.9766, reference=+0.84123,
         band_half=0.037, lo=+0.804230, hi=+0.878230,
         max_secant_slope=6.7850, b_pos=0.010198, b_ref=0.026504,
         weak_bar=True, can_bite=False),
    dict(id="G-F11-2", rung="re100", re=100, profile="vAlongY05",
         component="v", station=0.8047, reference=-0.24533,
         band_half=0.0081, lo=-0.253430, hi=-0.237230,
         max_secant_slope=0.9841, b_pos=0.004253, b_ref=0.003844,
         weak_bar=False, can_bite=True),
    dict(id="G-F11-3", rung="re100", re=100, profile="uAlongX05",
         component="u", station=0.5000, reference=-0.20581,
         band_half=0.0078, lo=-0.213610, hi=-0.198010,
         max_secant_slope=0.5922, b_pos=0.005468, b_ref=0.002313,
         weak_bar=False, can_bite=True),
    dict(id="G-F11-4", rung="re1000", re=1000, profile="uAlongX05",
         component="u", station=0.9766, reference=+0.65928,
         band_half=0.079, lo=+0.580280, hi=+0.738280,
         max_secant_slope=14.5607, b_pos=0.021885, b_ref=0.056878,
         weak_bar=True, can_bite=False),
    dict(id="G-F11-5", rung="re1000", re=1000, profile="vAlongY05",
         component="v", station=0.9063, reference=-0.51500,
         band_half=0.021, lo=-0.536000, hi=-0.494000,
         max_secant_slope=3.1569, b_pos=0.008595, b_ref=0.012332,
         weak_bar=False, can_bite=False),
    dict(id="G-F11-6", rung="re1000", re=1000, profile="uAlongX05",
         component="u", station=0.5000, reference=-0.06080,
         band_half=0.014, lo=-0.074800, hi=-0.046800,
         max_secant_slope=1.0053, b_pos=0.009283, b_ref=0.003927,
         weak_bar=False, can_bite=True),
)

# The twelve band-interval endpoints as the frozen document PRINTS them, to
# six decimals.  At grade time each of these must be found as a literal token
# in the pre-registration blob: that is how this file proves its bands ARE the
# document's bands rather than merely claiming to be.
BAND_TOKENS = ("0.804230", "0.878230", "0.253430", "0.237230",
               "0.213610", "0.198010", "0.580280", "0.738280",
               "0.536000", "0.494000", "0.074800", "0.046800")

# --- the two sampling directories (2026-08-25 pre-compute amendment) --------
# PROFILES_DIR is the FROZEN literal path: the graded value and the completion
# clauses C4/C6 read it, at the converged iteration, and nothing here changes
# that.  SERIES_DIR carries the periodic samples the PLATEAU's earlier term is
# read from.  They are deliberately two different names: collapsing them is the
# defect the amendment repairs, and grade_f11.py --selftest carries a mutation
# control that FAILS if the plateau reader is pointed back at PROFILES_DIR.
PROFILES_DIR = "centerlineProfiles"
SERIES_DIR = "centerlineSeries"

# --- section 5: the completion rule, with its three declared departures ------
REQUIRED_FIELDS = ("U", "p")
SAMPLE_SETS = ("uAlongX05", "vAlongY05")
SOLVER_LOG = "log.simpleFoam"
CHECKMESH_LOG = "log.checkMesh"
CONVERGED_RE = re.compile(r"^SIMPLE solution converged in (\d+) iterations",
                          re.M)

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
            "BLOCKED", "PENDING")

EXIT_OK, EXIT_FAIL, EXIT_REFUSE, EXIT_NOT_A_RESULT = 0, 1, 2, 3


# ===========================================================================
# 2.  THE FREEZE CHECKS  (CLAUDE.md rule 2; pre-registration 8.1 and 8.2)
# ===========================================================================

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


def git_blob_sha1(data):
    """The git blob object id of ``data`` -- computed here rather than shelled
    out, so the check does not depend on a working tree state."""
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def _git(args):
    p = subprocess.run(["git", "-C", REPO] + args,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        refuse("git %s failed: %s" % (" ".join(args),
                                      p.stderr.decode().strip()))
    return p.stdout


def verify_instrument_blob():
    """Section 8.1.  The path is not the freeze; the BLOB is.  The instrument
    on disk must be byte-identical to git blob INSTRUMENT_BLOB, checked three
    independent ways: the blob id computed from the bytes, the sha256, and a
    byte comparison against what git hands back for that blob id."""
    path = os.path.join(REPO, INSTRUMENT_REL)
    if not os.path.isfile(path):
        refuse("the frozen instrument %s is not on disk" % INSTRUMENT_REL)
    with open(path, "rb") as fh:
        data = fh.read()
    got_blob = git_blob_sha1(data)
    if got_blob != INSTRUMENT_BLOB:
        refuse("the instrument on disk is NOT the frozen blob.\n"
               "  frozen  %s\n  on disk %s\n"
               "  (pre-registration section 8.1; a freeze that is claimed and "
               "not checked is a claim about intent)"
               % (INSTRUMENT_BLOB, got_blob))
    got_sha = sha256_bytes(data)
    if got_sha != INSTRUMENT_SHA256:
        refuse("the instrument's sha256 does not match section 8.1.\n"
               "  frozen  %s\n  on disk %s" % (INSTRUMENT_SHA256, got_sha))
    committed = _git(["cat-file", "blob", INSTRUMENT_BLOB])
    if committed != data:
        refuse("git cat-file blob %s does not match the file on disk byte for "
               "byte" % INSTRUMENT_BLOB)
    # and the module actually imported is the file we just hashed
    imported = os.path.abspath(getattr(RT, "__file__", ""))
    if imported != os.path.abspath(path):
        refuse("the imported roache_triple module is %s, not the frozen "
               "instrument at %s" % (imported, path))
    return dict(path=INSTRUMENT_REL, blob=INSTRUMENT_BLOB, sha256=got_sha,
                bytes=len(data), verified=True)


def verify_own_freeze(prereg_commit):
    """Section 8.2.  Both scripts are committed with their sha256 recorded in
    a dated PRE-COMPUTE addendum to the pre-registration BEFORE the first
    solve.  This function is that requirement made executable: the addendum
    must already carry this file's sha256, or nothing is graded.

    The check is FORMAT-AGNOSTIC on purpose.  The frozen document does not fix
    the addendum's wording, and inventing a wording here would be inventing a
    clause.  What it asserts is only what section 8.2 actually promises: that
    the sha256 of each script appears in the document.
    """
    try:
        blob = _git(["cat-file", "blob",
                     "%s:%s" % (prereg_commit, PREREG_REL)])
    except Refusal:
        refuse("the pre-registration %s is not in commit %s"
               % (PREREG_REL, prereg_commit))
    text = blob.decode("utf-8", "replace")

    # (a) the bands in this file ARE the bands in that document.
    missing = [t for t in BAND_TOKENS if t not in text]
    if missing:
        refuse("band interval endpoints %s are not in the pre-registration at "
               "%s; this file's bands are not that document's bands"
               % (missing, prereg_commit))

    # (b) the instrument this file will use is the one that document froze.
    for tok, what in ((INSTRUMENT_BLOB, "instrument blob"),
                      (INSTRUMENT_SHA256, "instrument sha256")):
        if tok not in text:
            refuse("the %s %s is not named in the pre-registration at %s"
                   % (what, tok, prereg_commit))

    # (c) THE SECTION 8.2 ADDENDUM.  Refuse until it has landed.
    self_sha = sha256_file(os.path.abspath(__file__))
    peer_path = os.path.join(REPO, REL_PEER)
    peer_sha = sha256_file(peer_path) if os.path.isfile(peer_path) else None
    if self_sha not in text:
        refuse("the section 8.2 PRE-COMPUTE addendum has not landed, or this "
               "file is not the file it recorded.\n"
               "  %s sha256 on disk = %s\n"
               "  that token does not appear in %s at %s.\n"
               "  Section 8.2: both files are committed, with their sha256 "
               "recorded in a dated addendum, BEFORE the first solve.  Until "
               "then there is no frozen grading path and nothing is graded."
               % (REL_SELF, self_sha, PREREG_REL, prereg_commit))
    if peer_sha is None:
        refuse("the launcher %s is not on disk; section 8.2 freezes BOTH "
               "scripts" % REL_PEER)
    if peer_sha not in text:
        refuse("the launcher's sha256 %s does not appear in %s at %s; section "
               "8.2 freezes BOTH scripts and only one is recorded"
               % (peer_sha, PREREG_REL, prereg_commit))

    return dict(prereg=PREREG_REL, prereg_commit=prereg_commit,
                prereg_sha256=sha256_bytes(blob),
                prereg_freeze_commit_declared=PREREG_FREEZE_COMMIT,
                grading_path=REL_SELF, grading_path_sha256=self_sha,
                launcher=REL_PEER, launcher_sha256=peer_sha,
                band_tokens_found=len(BAND_TOKENS), addendum_present=True)


# ===========================================================================
# 3.  THE .xy READ PATH  -- parsed by asserted layout, selected by COORDINATE
# ===========================================================================

def parse_xy(path, set_name):
    """Return the rows of one sampled profile, with the format asserted.

    REFUSES on: a missing file, a header naming columns this layout does not
    expect, a row that is not six floats, a duplicated station coordinate, or
    a profile whose FIXED coordinate is not the registered constant on every
    row.  That last one is what a name match would have bought us and the
    format does not provide.
    """
    if set_name not in PROFILES:
        refuse("unknown sample set %r" % set_name)
    spec = PROFILES[set_name]
    if not os.path.isfile(path):
        refuse("no sampled artifact at %s" % path)
    with open(path, "r", errors="replace") as fh:
        raw = fh.read()

    rows, headers = [], []
    for lineno, line in enumerate(raw.splitlines(), 1):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            headers.append(s.lstrip("#").strip())
            continue
        parts = s.split()
        if len(parts) != len(XY_COLUMNS):
            refuse("%s line %d has %d columns, not %d; the frozen layout is "
                   "%s and this comparator will not guess at a different one"
                   % (path, lineno, len(parts), len(XY_COLUMNS),
                      " ".join(XY_COLUMNS)))
        try:
            rows.append(tuple(float(p) for p in parts))
        except ValueError as exc:
            refuse("%s line %d does not parse as six floats: %s"
                   % (path, lineno, exc))

    # If a header IS present, it must agree with the frozen layout.
    for h in headers:
        toks = [t for t in re.split(r"[\s,]+", h) if t]
        if len(toks) == len(XY_COLUMNS):
            norm = [t.strip().lower() for t in toks]
            want = [c.lower() for c in XY_COLUMNS]
            if norm != want:
                refuse("%s carries a column header %r that disagrees with the "
                       "frozen layout %s; refusing rather than guessing which "
                       "is right" % (path, h, " ".join(XY_COLUMNS)))

    if not rows:
        refuse("%s contains no data rows" % path)

    fixed_i = COL[spec["fixed_axis"]]
    bad = [r[fixed_i] for r in rows
           if abs(r[fixed_i] - spec["fixed_value"]) > NEAREST_COORD_TOL]
    if bad:
        refuse("%s claims to be profile %r, whose %s must be %.6f on every "
               "row, but %d rows have %s in %s.  This file is not the profile "
               "it is named."
               % (path, set_name, spec["fixed_axis"], spec["fixed_value"],
                  len(bad), spec["fixed_axis"], sorted(set(bad))[:4]))

    st_i = COL[spec["station_axis"]]
    keys = [round(r[st_i], COORD_ROUND) for r in rows]
    if len(set(keys)) != len(keys):
        dup = sorted(k for k in set(keys) if keys.count(k) > 1)
        refuse("%s has duplicate station coordinates %s at round(%d); the "
               "round-to-4 lookup registered in section 4.6 is not "
               "single-valued on this file" % (path, dup, COORD_ROUND))
    return rows


def select_station(rows, set_name, component, station, path="<memory>"):
    """THE REGISTERED READ PATH: the round(coord, 4) dictionary lookup of
    section 4.6 PZ-3.  Selected BY COORDINATE, never by row index, and the
    coordinate actually matched is ASSERTED against the registered station.
    """
    spec = PROFILES[set_name]
    st_i = COL[spec["station_axis"]]
    comp_i = COL[COMPONENT_OF[component]]
    by_coord = {round(r[st_i], COORD_ROUND): r for r in rows}
    key = round(float(station), COORD_ROUND)
    if key not in by_coord:
        refuse("station %s = %.4f is not sampled in %s; available %s"
               % (spec["station_axis"], station, path, sorted(by_coord)))
    row = by_coord[key]
    matched = row[st_i]
    if abs(matched - float(station)) > NEAREST_COORD_TOL:
        refuse("station selector matched %s = %.10f for a registered station "
               "of %.10f in %s -- outside the %g tolerance"
               % (spec["station_axis"], matched, station, path,
                  NEAREST_COORD_TOL))
    return float(row[comp_i]), float(matched)


def select_station_nearest(rows, set_name, component, station,
                           path="<memory>"):
    """PZ-3's INDEPENDENT re-derivation: nearest-coordinate match at 1e-6.
    Deliberately a different algorithm from ``select_station``."""
    spec = PROFILES[set_name]
    st_i = COL[spec["station_axis"]]
    comp_i = COL[COMPONENT_OF[component]]
    best = min(rows, key=lambda r: abs(r[st_i] - float(station)))
    if abs(best[st_i] - float(station)) > NEAREST_COORD_TOL:
        refuse("nearest-coordinate re-derivation found no station within %g "
               "of %.4f in %s" % (NEAREST_COORD_TOL, station, path))
    return float(best[comp_i]), float(best[st_i])


def write_xy(path, rows):
    """Re-emit rows in the same whitespace-separated raw format at full
    round-trip precision.  Used only for the planted COPIES; the graded
    artifact is never written to."""
    with open(path, "w") as fh:
        for r in rows:
            fh.write(" ".join("%.17g" % v for v in r) + "\n")


# ===========================================================================
# 4.  PLANTED-ZERO CONTROLS  (CLAUDE.md rule 3; pre-registration section 4.6)
# ===========================================================================

def pz_controls(path, set_name, component, station):
    """PZ-1, PZ-2 and PZ-3 exactly as section 4.6 registers them, all three on
    F11's OWN `.xy` artifact through F11's OWN parser and station selector --
    deliberately NOT roache_triple's generic `read_series` control, which
    would prove a JSON reader can see a plant in a file the case never writes.

    Returns (pz1, pz2, pz3).  Any failure REFUSES; none is skippable.
    """
    rows = parse_xy(path, set_name)
    spec = PROFILES[set_name]
    st_i = COL[spec["station_axis"]]
    comp_i = COL[COMPONENT_OF[component]]
    before, matched = select_station(rows, set_name, component, station, path)
    key = round(float(station), COORD_ROUND)

    tmp = tempfile.mkdtemp(prefix="f11_plant_")
    try:
        work = os.path.join(tmp, os.path.basename(path))

        # ---- a control ON the control: the re-emission must round-trip -----
        write_xy(work, rows)
        rt_val, _ = select_station(parse_xy(work, set_name), set_name,
                                   component, station, work)
        if abs(rt_val - before) > PZ_TOL:
            refuse("the plant harness itself is lossy: re-emitting %s without "
                   "any plant moved the graded value by %.3e.  A control that "
                   "cannot round-trip proves nothing about a plant."
                   % (path, rt_val - before))

        # ---- PZ-1: plant AT the graded station, read it back --------------
        planted = [list(r) for r in rows]
        for r in planted:
            if round(r[st_i], COORD_ROUND) == key:
                r[comp_i] += PLANT
        write_xy(work, planted)
        after, _ = select_station(parse_xy(work, set_name), set_name,
                                  component, station, work)
        pz1 = RT.external_plant_control(
            "f11_xy_parser+station_selector", before, after, plant=PLANT,
            artifact=os.path.abspath(path),
            level="%s@%s=%.4f" % (component, spec["station_axis"], station))
        pz1.update(control="PZ-1", before=before, after=after,
                   matched_coord=matched)
        if not pz1["passed"]:
            refuse("PZ-1 FAILED: the F11 parser + station selector did not see "
                   "its planted %.6e at %s = %.4f in %s (saw %.6e).  Its zeros "
                   "mean nothing (CLAUDE.md rule 3)."
                   % (PLANT, spec["station_axis"], station, path,
                      pz1["reader_delta"]))

        # ---- PZ-2: plant at EVERY OTHER station; the graded value must not
        #      move at all.  Section 4.6 registers one different station; this
        #      runs the same test against all of them, which is strictly
        #      stronger and requires no choice of which one.
        bled = []
        for j, r in enumerate(rows):
            if round(r[st_i], COORD_ROUND) == key:
                continue
            other = [list(x) for x in rows]
            other[j][comp_i] += PLANT
            write_xy(work, other)
            seen, seen_coord = select_station(parse_xy(work, set_name),
                                              set_name, component, station,
                                              work)
            if abs(seen - before) > PZ_TOL:
                bled.append(dict(planted_at_row=j,
                                 planted_at_coord=r[st_i],
                                 graded_moved_by=seen - before,
                                 graded_coord=seen_coord))
        pz2 = dict(control="PZ-2", passed=not bled, planted=PLANT,
                   reader="f11_station_selector",
                   artifact=os.path.abspath(path),
                   foreign_stations_tested=len(rows) - 1,
                   graded_station_moved_at=bled)
        if bled:
            refuse("PZ-2 FAILED: a plant at %d OTHER station(s) of %s moved "
                   "the graded value at %s = %.4f.  The station selector is "
                   "not reading the row it claims to read -- %s"
                   % (len(bled), path, spec["station_axis"], station,
                      bled[:2]))

        # ---- PZ-3: independent re-derivation ------------------------------
        near, near_coord = select_station_nearest(rows, set_name, component,
                                                  station, path)
        pz3 = dict(control="PZ-3", passed=abs(near - before) <= PZ_TOL,
                   reader="nearest_coordinate_match",
                   artifact=os.path.abspath(path),
                   dict_lookup_value=before, nearest_match_value=near,
                   dict_lookup_coord=matched, nearest_match_coord=near_coord,
                   delta=near - before, tolerance=PZ_TOL)
        if not pz3["passed"]:
            refuse("PZ-3 FAILED: the nearest-coordinate re-derivation (%r) "
                   "and the round(coord, %d) lookup (%r) disagree by %.3e in "
                   "%s" % (near, COORD_ROUND, before, near - before, path))
        return pz1, pz2, pz3
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# 5.  THE COMPLETION RULE  (CLAUDE.md rule 4; pre-registration section 5)
# ===========================================================================

def _time_dirs(case_dir):
    out = []
    for d in os.listdir(case_dir):
        if re.fullmatch(r"[0-9]+", d) and os.path.isdir(
                os.path.join(case_dir, d)):
            out.append(int(d))
    return sorted(out)


def _series_times(case_dir):
    """The iterations at which the PERIODIC series was written.  Reads
    SERIES_DIR and not PROFILES_DIR: PROFILES_DIR holds exactly one directory,
    the converged iteration, and reading the periodic series from it would find
    no earlier sample at all.  An absent directory is [] -- reported, never
    read as a pass."""
    base = os.path.join(case_dir, "postProcessing", SERIES_DIR)
    if not os.path.isdir(base):
        return []
    out = []
    for d in os.listdir(base):
        if re.fullmatch(r"[0-9]+", d) and os.path.isdir(
                os.path.join(base, d)):
            out.append(int(d))
    return sorted(out)


def _read_end_time(case_dir):
    path = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(path):
        return None
    txt = open(path, errors="replace").read()
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", txt, re.M)
    return int(float(m.group(1))) if m else None


def checkmesh_certificate(case_dir):
    """Section 4.4, mesh birth certificate (VERIFICATION section 9 v1.5).
    A level whose checkMesh is not clean does not enter the ladder.

    "Clean" is read from checkMesh's OWN statement -- `Mesh OK.` present and no
    `Failed N mesh checks` line -- the same discipline L-14/L-21 imposes on the
    solver's own convergence statement.  An ABSENT log is reported ABSENT, not
    clean and not dirty (VERIFICATION section 9, ran_before_found).
    """
    path = os.path.join(case_dir, CHECKMESH_LOG)
    if not os.path.isfile(path):
        return dict(state="ABSENT", clean=False, log=path,
                    note="mesh birth certificate missing; the level is "
                         "quarantined from the ladder (section 4.4)")
    txt = open(path, errors="replace").read()
    failed = re.search(r"^Failed\s+\d+\s+mesh\s+checks", txt, re.M)
    ok = re.search(r"^Mesh OK\.", txt, re.M)
    if failed:
        return dict(state="NOT_CLEAN", clean=False, log=path,
                    note=failed.group(0))
    if ok:
        return dict(state="CLEAN", clean=True, log=path, note="Mesh OK.")
    return dict(state="CANNOT_TELL", clean=False, log=path,
                note="checkMesh log carries neither 'Mesh OK.' nor a "
                     "'Failed N mesh checks' line")


def completion_check(case_dir):
    """All-or-nothing, section 5.  Returns (ok, clauses).

    Departures C3, C5 and C4/C6 are the ones the pre-registration declares in
    advance; they are transcribed, not re-derived.
    """
    c = {"ran_before_found": "checked"}
    log = os.path.join(case_dir, SOLVER_LOG)

    # C1 -- rc == 0, written on disk by the launcher.
    rc_path = os.path.join(case_dir, "run_rc.txt")
    c["C1_rc_zero"] = (os.path.isfile(rc_path)
                       and open(rc_path).read().strip() == "0")

    if not os.path.isfile(log):
        for k in ("C2_end_line", "C3_converged_before_cap",
                  "C4_fields_and_samples", "C5_log_step_integrity",
                  "C6_age_guard"):
            c[k] = False
        c["ran_before_found"] = "solver log absent -- the check could not run"
        return False, c

    txt = open(log, errors="replace").read()

    # C2 -- an End line.
    c["C2_end_line"] = bool(re.search(r"^End\s*$", txt, re.M))

    # C3 (declared departure 1) -- STRICTER than "last time == endTime":
    # the solver's own convergence statement, the last written time equal to
    # that iteration N, and N strictly below the cap.  A cap-terminated run
    # FAILS C3.
    m = CONVERGED_RE.search(txt)
    n_conv = int(m.group(1)) if m else None
    end_time = _read_end_time(case_dir)
    tds = [t for t in _time_dirs(case_dir) if t > 0]
    c["_converged_iterations"] = n_conv
    c["_endTime"] = end_time
    c["_last_time_dir"] = tds[-1] if tds else None
    c["C3_converged_before_cap"] = bool(
        n_conv is not None and end_time is not None and tds
        and tds[-1] == n_conv and n_conv < end_time)

    # C5 (declared departure 2) -- one ExecutionTime line per Time line, both
    # equal to the converged iteration count, both > 0.
    n_time = len(re.findall(r"^Time = ", txt, re.M))
    n_exec = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    c["_n_time_lines"], c["_n_exec_lines"] = n_time, n_exec
    c["C5_log_step_integrity"] = bool(
        n_time == n_exec and n_time > 0 and n_conv is not None
        and n_time == n_conv)

    # C4 (declared departure 3) -- U and p at the last written time, PLUS both
    # sampled .xy files under centerlineProfiles/<N>/.
    sample_dir = None
    if n_conv is not None:
        sample_dir = os.path.join(case_dir, "postProcessing",
                                  PROFILES_DIR, str(n_conv))
    missing = []
    if tds:
        d = os.path.join(case_dir, str(tds[-1]))
        missing += [f for f in REQUIRED_FIELDS
                    if not os.path.isfile(os.path.join(d, f))]
    else:
        missing.append("<no time directory>")
    xy_paths = []
    if sample_dir and os.path.isdir(sample_dir):
        for s in SAMPLE_SETS:
            p = os.path.join(sample_dir, "%s_U.xy" % s)
            xy_paths.append(p)
            if not os.path.isfile(p):
                missing.append(os.path.relpath(p, case_dir))
    else:
        missing.append("postProcessing/%s/%s/" % (PROFILES_DIR, n_conv))
    c["C4_fields_and_samples"] = not missing
    c["_missing"] = missing

    # C6 -- THE AGE GUARD, stricter than the rule: the reference is the LATEST
    # mtime anywhere in the case's own 0/, and the guard extends to the two
    # sampled artifacts the gate actually reads.
    zero = os.path.join(case_dir, "0")
    if tds and os.path.isdir(zero) and not missing:
        zmt = max([os.path.getmtime(os.path.join(zero, f))
                   for f in os.listdir(zero)] or [0.0])
        d = os.path.join(case_dir, str(tds[-1]))
        ages, ok = {}, True
        for f in REQUIRED_FIELDS:
            p = os.path.join(d, f)
            ages[f] = os.path.getmtime(p) - zmt
            if ages[f] <= 0:
                ok = False
        for p in xy_paths:
            ages[os.path.basename(p)] = os.path.getmtime(p) - zmt
            if ages[os.path.basename(p)] <= 0:
                ok = False
        c["C6_age_guard"] = ok
        c["_age_margin_s"] = {k: round(v, 3) for k, v in ages.items()}
    else:
        c["C6_age_guard"] = False

    ok = all(v for k, v in c.items() if k.startswith("C"))
    return ok, c


def iterative_state(case_dir):
    """Section 4.5.  CONVERGED iff scripts/check_convergence.py says so, keyed
    off the solver's OWN statement and never off a residual read in isolation
    (L-14 / L-21).  CANNOT_TELL is reported as CANNOT_TELL and is not a pass.
    """
    log = os.path.join(case_dir, SOLVER_LOG)
    if not os.path.isfile(log):
        return "LOG_ABSENT", dict(reason="no %s" % SOLVER_LOG)
    try:
        from check_convergence import classify
    except Exception as exc:                                   # noqa: BLE001
        refuse("scripts/check_convergence.py could not be imported, and the "
               "pre-registration names it as the iterative-convergence "
               "measurement: %r" % (exc,))
    res = classify(log, case_dir)
    return res.get("status", "CANNOT_TELL"), res


def plateau_state(case_dir, set_name, component, station, final_iteration):
    """Section 4.5.  PLATEAUED iff |q(final sample) - q(latest earlier sample
    at least 250 iterations before it)| <= 1.0e-6.

    THE CRITERION, THE THRESHOLD, THE 250-ITERATION WINDOW AND THE STATION ARE
    UNCHANGED.  The 2026-08-25 pre-compute amendment changed one thing only:
    the two terms now live in two directories.

      * q(final) is read from ``postProcessing/centerlineProfiles/<N>/`` at the
        CONVERGED iteration -- the same artifact, the same station and the same
        parser the gate grades.  ``final_iteration`` is the converged iteration
        the completion rule already established; it is passed in rather than
        re-derived, so this function and clause C3 cannot disagree about what
        "final" means.
      * the earlier samples are the periodic series in
        ``postProcessing/centerlineSeries/``.

    IF NO SERIES SAMPLE AT LEAST 250 ITERATIONS BEFORE THE CONVERGED ITERATION
    EXISTS -- INCLUDING WHEN THE SERIES DIRECTORY IS ABSENT ENTIRELY -- THE
    PLATEAU IS UNMEASURED.  It is reported UNMEASURED and grades that level NOT
    A RESULT through rule 5 step (a); it is never silently a pass, and NO
    FALLBACK to the last periodic sample is taken in place of the converged
    one, because that would grade the drift of a materially less-converged
    state.
    """
    series_base = os.path.join(case_dir, "postProcessing", SERIES_DIR)
    graded_base = os.path.join(case_dir, "postProcessing", PROFILES_DIR)
    if final_iteration is None:
        return "UNMEASURED", dict(
            reason="the converged iteration is unknown, so the final sample "
                   "cannot be identified and the criterion cannot be "
                   "evaluated",
            samples=[], series_dir=series_base, graded_dir=graded_base)
    final = int(final_iteration)
    times = _series_times(case_dir)
    earlier = [t for t in times if t <= final - PLATEAU_MIN_ITER_GAP]
    if not earlier:
        return "UNMEASURED", dict(
            reason="no %s sample at least %d iterations before the converged "
                   "iteration %d exists (series on disk: %s); the criterion "
                   "cannot be evaluated and an unevaluated step is not a "
                   "passed one"
                   % (SERIES_DIR, PLATEAU_MIN_ITER_GAP, final,
                      times if times else "none"),
            samples=times, final=final, series_dir=series_base,
            graded_dir=graded_base)
    prev = earlier[-1]

    def q(base, t):
        p = os.path.join(base, str(t), "%s_U.xy" % set_name)
        v, _ = select_station(parse_xy(p, set_name), set_name, component,
                              station, p)
        return v

    q_final, q_prev = q(graded_base, final), q(series_base, prev)
    drift = abs(q_final - q_prev)
    state = "PLATEAUED" if drift <= PLATEAU_TOL else "NOT_PLATEAUED"
    return state, dict(final_iteration=final, compared_iteration=prev,
                       iteration_gap=final - prev, q_final=q_final,
                       q_earlier=q_prev, drift=drift,
                       threshold=PLATEAU_TOL, samples=times,
                       final_read_from=os.path.join(graded_base, str(final)),
                       earlier_read_from=os.path.join(series_base, str(prev)))


# ===========================================================================
# 6.  DIAGNOSTICS -- reported, never gated  (section 3.4)
# ===========================================================================

def diagnostic_profile(path, set_name, re_number):
    """The 17-point profile reproduced against Ghia at every level.  Section
    3.4: this moves NO verdict.  Boundary rows are the imposed BC (an IDENTITY
    under VERIFICATION 2a) and are flagged as such."""
    import cavity_ladder
    table = (cavity_ladder.U_ALONG_X05[re_number] if set_name == "uAlongX05"
             else cavity_ladder.V_ALONG_Y05[re_number])
    comp = "u" if set_name == "uAlongX05" else "v"
    rows = parse_xy(path, set_name)
    pts = []
    for coord, ref in table:
        try:
            val, matched = select_station(rows, set_name, comp, coord, path)
        except Refusal:
            continue
        pts.append(dict(coord=coord, matched_coord=matched, reference=ref,
                        measured=val, deviation=val - ref,
                        boundary_identity=coord in (0.0, 1.0)))
    interior = [p for p in pts if not p["boundary_identity"]]
    devs = [abs(p["deviation"]) for p in interior]
    return dict(set=set_name, artifact=os.path.abspath(path),
                gated=False, note="DIAGNOSTIC ONLY -- section 3.4, moves no "
                                  "verdict", n_interior=len(interior),
                max_abs_deviation=max(devs) if devs else None,
                rms_abs_deviation=((sum(d * d for d in devs) / len(devs))
                                   ** 0.5) if devs else None,
                points=pts)


# ===========================================================================
# 7.  GRADING
# ===========================================================================

def case_dir_for(root, rung, level):
    return os.path.join(root, rung, level)


def grade(root, freeze):
    report = dict(
        family="F11",
        pre_registration=PREREG_REL,
        pre_registration_freeze_commit=PREREG_FREEZE_COMMIT,
        freeze=freeze,
        dim=DIM, ratio_form=FORM, fs=FS,
        plant=PLANT, plateau_threshold=PLATEAU_TOL,
        plateau_min_iteration_gap=PLATEAU_MIN_ITER_GAP,
        graded_sample_dir=PROFILES_DIR,
        plateau_series_dir=SERIES_DIR,
        sampling_note="2026-08-25 PRE-COMPUTE AMENDMENT (arm B): the graded "
                      "value and completion clauses C4/C6 read the FROZEN "
                      "literal path postProcessing/%s/<N>/ at the CONVERGED "
                      "iteration; the plateau's earlier samples are read from "
                      "postProcessing/%s/. No band, station, reference, "
                      "completion clause or verdict logic changed."
                      % (PROFILES_DIR, SERIES_DIR),
        discrimination_test="UNMEASURABLE, not satisfied (section 3.3): the "
                            "hypothesis has no runnable null arm and the row "
                            "is recorded unmeasured",
        coverage_matrix=dict(V="NOT EARNABLE BY THIS RUN (section 10)",
                             G="what this run is for -- earned only on a "
                               "CONVERGING triple",
                             P="BLOCKED -- the Ghia primary is not on disk, "
                               "so rule 15's title-page verification cannot "
                               "be performed (sections 3.1, 10)"),
        levels={}, gates={}, diagnostics={}, planted_zero_controls=[],
        cost=dict(note="core-minutes = wall s x ranks / 60; a "
                       "docs/COST_CALIBRATION.md row is MANDATORY at "
                       "completion (section 7, CLAUDE.md rule 12)"))

    # ---- per level: completion, convergence, mesh certificate, cost --------
    level_info = {}
    for rung in RUNGS:
        for name, n, cells, cap in LEVELS:
            key = "%s/%s" % (rung, name)
            cd = case_dir_for(root, rung, name)
            if not os.path.isdir(cd):
                level_info[key] = dict(status="PENDING", case_dir=cd,
                                       note="case directory does not exist -- "
                                            "not launched (section 7)")
                report["levels"][key] = level_info[key]
                continue
            ok, clauses = completion_check(cd)
            it_state, it_detail = iterative_state(cd)
            mesh = checkmesh_certificate(cd)
            timing = os.path.join(cd, "launch_timing.json")
            t = json.load(open(timing)) if os.path.isfile(timing) else {}
            info = dict(status="COMPLETE" if ok else "INCOMPLETE",
                        case_dir=cd, n=n, cells=cells, endTime=cap,
                        completion=clauses,
                        iterative_convergence=it_state,
                        iterative_detail={k: v for k, v in it_detail.items()
                                          if k in ("status", "reason",
                                                   "solver_type")},
                        mesh_certificate=mesh,
                        wall_s=t.get("wall_s"), ranks=t.get("ranks"),
                        core_minutes=(round(t["wall_s"] * t.get("ranks", 1)
                                            / 60.0, 4)
                                      if t.get("wall_s") is not None
                                      else None),
                        iterations=clauses.get("_converged_iterations"))
            level_info[key] = info
            report["levels"][key] = info

    spent = [v["core_minutes"] for v in level_info.values()
             if v.get("core_minutes") is not None]
    report["cost"]["actual_core_minutes"] = round(sum(spent), 4) if spent \
        else None
    report["cost"]["levels_with_timing"] = len(spent)

    # ---- diagnostics, per level per profile --------------------------------
    for rung in RUNGS:
        re_number = 100 if rung == "re100" else 1000
        for name, _n, _c, _cap in LEVELS:
            key = "%s/%s" % (rung, name)
            info = level_info[key]
            if info["status"] != "COMPLETE":
                continue
            n_conv = info["completion"]["_converged_iterations"]
            sdir = os.path.join(info["case_dir"], "postProcessing",
                                PROFILES_DIR, str(n_conv))
            for s in SAMPLE_SETS:
                report["diagnostics"]["%s/%s" % (key, s)] = \
                    diagnostic_profile(os.path.join(sdir, "%s_U.xy" % s),
                                       s, re_number)

    # ---- the six gates -----------------------------------------------------
    for g in GATES:
        gid, rung = g["id"], g["rung"]
        keys = ["%s/%s" % (rung, lv) for lv in LEVEL_NAMES]
        infos = [level_info[k] for k in keys]

        head = dict(
            gate=gid, rung="Re %d" % g["re"],
            quantity="%s at (%s)" % (
                g["component"],
                "0.5, %.4f" % g["station"] if g["profile"] == "uAlongX05"
                else "%.4f, 0.5" % g["station"]),
            station=g["station"], profile=g["profile"],
            component=g["component"], reference=g["reference"],
            band_half_width=g["band_half"], band=[g["lo"], g["hi"]],
            band_terms=dict(B_pos=g["b_pos"], B_ref=g["b_ref"],
                            sum=round(g["b_pos"] + g["b_ref"], 9),
                            max_secant_slope=g["max_secant_slope"],
                            B_ref_fraction_pct=round(
                                100.0 * g["b_ref"]
                                / (g["b_pos"] + g["b_ref"]), 1)),
            weak_bar=g["weak_bar"], band_can_bite=g["can_bite"],
            declarations=[])
        if g["weak_bar"]:
            head["declarations"].append(
                "WEAK BAR (section 3.2 route 2): %.0f %% of this band's "
                "half-width is the REFERENCE's own resolution, not our mesh. "
                "A materially wrong solve could pass this band. The "
                "load-bearing content of this row is the triple, the observed "
                "order and the GCI -- NOT the band."
                % head["band_terms"]["B_ref_fraction_pct"])
        if not g["can_bite"]:
            head["declarations"].append(
                "This band is WIDER than the largest deviation anywhere in the "
                "2026-07-30 record (0.01734 lid-speed units); it is not a bar "
                "a real solve can fail (section 4.2).")

        # PENDING: a level was never launched.
        pend = [k for k, i in zip(keys, infos) if i["status"] == "PENDING"]
        if pend:
            head.update(verdict="PENDING",
                        why="levels %s were not launched; section 7 loses a "
                            "whole rung, never one level of a triple" % pend)
            report["gates"][gid] = head
            continue

        # NOT A RESULT: a level exists and failed completion or its mesh
        # birth certificate.  It is LABELLED and carries no number.
        bad = []
        for k, i in zip(keys, infos):
            if i["status"] != "COMPLETE":
                failed = sorted(c for c, v in i["completion"].items()
                                if c.startswith("C") and not v)
                bad.append("%s: %s" % (k, ",".join(failed) or "INCOMPLETE"))
            if not i["mesh_certificate"]["clean"]:
                bad.append("%s: checkMesh %s"
                           % (k, i["mesh_certificate"]["state"]))
        if bad:
            head.update(verdict="NOT A RESULT",
                        why="the completion rule / mesh birth certificate "
                            "failed and the level carries the label, never a "
                            "number: " + "; ".join(bad),
                        levels_labelled=bad)
            report["gates"][gid] = head
            continue

        # ---- controls, per level, before any value is trusted --------------
        controls, levels, plateaus, iteratives = [], [], {}, {}
        pz1_fine = None
        for k, lv, i in zip(keys, LEVEL_NAMES, infos):
            n_conv = i["completion"]["_converged_iterations"]
            xy = os.path.join(i["case_dir"], "postProcessing",
                              PROFILES_DIR, str(n_conv),
                              "%s_U.xy" % g["profile"])
            p1, p2, p3 = pz_controls(xy, g["profile"], g["component"],
                                     g["station"])
            for p in (p1, p2, p3):
                p["gate"], p["level"] = gid, lv
                controls.append(p)
            if lv == LEVEL_NAMES[-1]:
                pz1_fine = p1
            value, matched = select_station(parse_xy(xy, g["profile"]),
                                            g["profile"], g["component"],
                                            g["station"], xy)
            levels.append(dict(name=lv, cells=CELLS[lv], value=value,
                               matched_coord=matched, artifact=xy))
            iteratives[lv] = i["iterative_convergence"]
            st, detail = plateau_state(i["case_dir"], g["profile"],
                                       g["component"], g["station"],
                                       n_conv)
            plateaus[lv] = st
            head.setdefault("plateau_detail", {})[lv] = detail
        report["planted_zero_controls"].extend(controls)

        # ---- rule 5, applied by the frozen instrument and by nothing here --
        try:
            row = RT.grade_ladder(
                quantity="%s %s" % (gid, head["quantity"]),
                levels=[dict(name=l["name"], cells=l["cells"],
                             value=l["value"]) for l in levels],
                dim=DIM, band=(g["lo"], g["hi"]), plant_control=pz1_fine,
                iterative_states=iteratives, plateau_states=plateaus,
                fs=FS, form=FORM, reference=g["reference"])
        except RT.Refusal as exc:
            refuse("%s: the frozen instrument REFUSED -- %s" % (gid, exc))

        head.update(verdict=row["verdict"], value=row["value"],
                    band_verdict=row["band_verdict"],
                    deviation_from_reference=row["value"] - g["reference"],
                    why=row["why"], monotone=row["monotone"],
                    orders=row["orders"], states=row["states"],
                    triples=row["triples"],
                    levels_measured=levels,
                    iterative_convergence=iteratives, plateau=plateaus,
                    instrument_row=row)
        if "GCI_pct" in row:
            head.update(order=row["order"], GCI_pct=row["GCI_pct"],
                        GCI_abs=row["GCI_abs"],
                        richardson=row["richardson"],
                        richardson_parent_convention=row[
                            "richardson_parent_convention"],
                        richardson_note="richardson is the CORRECTED Roache "
                                        "extrapolate and is what F11 quotes; "
                                        "richardson_parent_convention is the "
                                        "thermal parents' SIGN-FLIPPED form, "
                                        "printed beside it (section 8.1). "
                                        "Both are display-only: band_verdict "
                                        "grades the FINE VALUE.")
            gci_abs, dev = row["GCI_abs"], abs(row["value"] - g["reference"])
            if gci_abs < dev:
                head["gci_vs_reference_reading"] = (
                    "Registered in advance (section 9): the GCI (%.6g) is "
                    "SMALLER than the deviation from Ghia (%.6g) at this "
                    "station, which means the residual disagreement is NOT "
                    "discretisation error in this lab's solve. Three "
                    "CANDIDATE causes, NONE of them measured by this run: the "
                    "reference's own resolution (B_ref = %.6g), the "
                    "corner-singularity regularisation the two methods "
                    "necessarily differ on, and the linearUpwind advection "
                    "scheme. This is not a solver defect and not a Ghia "
                    "defect." % (gci_abs, dev, g["b_ref"]))
        report["gates"][gid] = head

    return report


# ===========================================================================
# 8.  DISPLAY
# ===========================================================================

def format_report(rep):
    out = []
    out.append("F11 CONVERSION -- graded against %s" % rep["pre_registration"])
    out.append("  frozen at %s   dim = %d   form = %r   Fs = %s"
               % (rep["pre_registration_freeze_commit"], rep["dim"],
                  rep["ratio_form"], rep["fs"]))
    f = rep["freeze"]
    out.append("  instrument %s blob %s  VERIFIED"
               % (f["instrument"]["path"], f["instrument"]["blob"]))
    out.append("  grading path %s sha256 %s  RECORDED IN THE SECTION 8.2 "
               "ADDENDUM" % (f["self"]["grading_path"],
                             f["self"]["grading_path_sha256"]))
    out.append("")
    out.append("LEVELS")
    for k, v in rep["levels"].items():
        if v["status"] == "PENDING":
            out.append("  %-16s PENDING -- not launched" % k)
            continue
        out.append("  %-16s %-10s cells %6d  iters %-6s  checkMesh %-11s  "
                   "convergence %-13s  %s core-min"
                   % (k, v["status"], v["cells"], v["iterations"],
                      v["mesh_certificate"]["state"],
                      v["iterative_convergence"], v["core_minutes"]))
        if v["status"] != "COMPLETE":
            failed = sorted(c for c, ok in v["completion"].items()
                            if c.startswith("C") and not ok)
            out.append("        FAILED CLAUSES: %s" % ", ".join(failed))
    out.append("")
    out.append("GATES")
    for gid, g in rep["gates"].items():
        out.append("")
        out.append("  [%s] %s  %s  ref %+.5f  band [%+.6f, %+.6f]"
                   % (gid, g["rung"], g["quantity"], g["reference"],
                      g["band"][0], g["band"][1]))
        bt = g["band_terms"]
        out.append("        B_pos %.6f + B_ref %.6f = %.6f   (B_ref is "
                   "%.1f %% of the half-width)"
                   % (bt["B_pos"], bt["B_ref"], bt["sum"],
                      bt["B_ref_fraction_pct"]))
        for d in g["declarations"]:
            out.append("        ** %s" % d)
        if "instrument_row" in g:
            out.append(RT.format_row(g["instrument_row"]))
            for lv, det in g.get("plateau_detail", {}).items():
                if "drift" in det:
                    out.append("        plateau %-7s drift %.3e over "
                               "iterations %d -> %d (threshold %g)"
                               % (lv, det["drift"], det["compared_iteration"],
                                  det["final_iteration"], det["threshold"]))
                else:
                    out.append("        plateau %-7s UNMEASURED -- %s"
                               % (lv, det["reason"]))
            if "gci_vs_reference_reading" in g:
                out.append("        %s" % g["gci_vs_reference_reading"])
        else:
            out.append("        VERDICT: %s -- %s" % (g["verdict"], g["why"]))
    out.append("")
    out.append("REPORTED AND NEVER GATED (section 3.4)")
    out.append("  discrimination test: %s" % rep["discrimination_test"])
    out.append("  coverage matrix P: %s" % rep["coverage_matrix"]["P"])
    out.append("  %d diagnostic profiles, %d planted-zero controls, all PASSED"
               % (len(rep["diagnostics"]), len(rep["planted_zero_controls"])))
    out.append("  cost: %s core-min actual over %d timed levels. %s"
               % (rep["cost"]["actual_core_minutes"],
                  rep["cost"]["levels_with_timing"], rep["cost"]["note"]))
    return "\n".join(out)


def overall_exit(rep):
    """Worst verdict across the six gates, in the instrument's own codes.

    PENDING has no code of its own in that convention; it is mapped into the
    "cannot be graded at all" class (3) and the PRINTED verdict stays PENDING.
    That is a display/exit mapping, stated here rather than left implicit --
    section 9: PENDING is never used to soften a fail.
    """
    vs = [g["verdict"] for g in rep["gates"].values()]
    if "NOT A RESULT" in vs or "PENDING" in vs:
        return EXIT_NOT_A_RESULT
    if "GATE FAIL" in vs:
        return EXIT_FAIL
    return EXIT_OK


# ===========================================================================
# 9.  SELFTEST -- N-T8 value controls, mutation controls, band controls
# ===========================================================================

_CHECKS = []
_MUTATIONS = []


def check(name, ok, detail="", mutation=False):
    _CHECKS.append((name, bool(ok), detail))
    if mutation:
        _MUTATIONS.append(name)
    print("  [%s] %s%s" % ("ok " if ok else "FAIL", name,
                           "   " + detail if detail else ""))


def _synth_xy(set_name, stations, values, fixed=0.5, component="u"):
    """A synthetic .xy whose value at every station is KNOWN BY CONSTRUCTION."""
    spec = PROFILES[set_name]
    comp_i = COL[COMPONENT_OF[component]]
    st_i = COL[spec["station_axis"]]
    fx_i = COL[spec["fixed_axis"]]
    rows = []
    for s, v in zip(stations, values):
        r = [0.0] * len(XY_COLUMNS)
        r[fx_i] = fixed
        r[st_i] = s
        r[2] = 0.05
        r[comp_i] = v
        rows.append(tuple(r))
    return rows


def selftest():
    print("grade_f11.py --selftest")
    print("N-T8 (heat-transfer, commit 792acd8f): every comparator's selftest "
          "carries a VALUE-checking\ncontrol against a synthetic case whose "
          "answer is known by construction, asserted to 1e-12\nrelative -- "
          "not a check that a key exists. A test that passes on both the right "
          "and the\nwrong answer tests nothing, so every value control below "
          "is paired with a MUTATION.")
    tmpd = tempfile.mkdtemp(prefix="f11_selftest_")
    try:
        # ---------------------------------------------------------------
        print("\n(i) the frozen constants are self-consistent -- a "
              "transcription error would show here")
        for g in GATES:
            check("%s: reference %+0.5f -/+ band %g reproduces the frozen "
                  "interval [%+.6f, %+.6f]"
                  % (g["id"], g["reference"], g["band_half"], g["lo"],
                     g["hi"]),
                  abs((g["reference"] - g["band_half"]) - g["lo"]) < 1e-12
                  and abs((g["reference"] + g["band_half"]) - g["hi"]) < 1e-12,
                  "lo delta %.2e hi delta %.2e"
                  % ((g["reference"] - g["band_half"]) - g["lo"],
                     (g["reference"] + g["band_half"]) - g["hi"]))
        for g in GATES:
            s = g["b_pos"] + g["b_ref"]
            check("%s: B_pos + B_ref = %.6f rounds UP to the frozen band %g"
                  % (g["id"], s, g["band_half"]),
                  g["band_half"] >= s and (g["band_half"] - s) < 0.0011,
                  "slack %.6f" % (g["band_half"] - s))
        check("the three cells are 1024/4096/16384 as section 4.4 fixes them",
              [c for _, _, c, _ in LEVELS] == [1024, 4096, 16384])
        check("dim is the int 2, stated and never defaulted", DIM == 2
              and isinstance(DIM, int) and not isinstance(DIM, bool))
        check("form is 'equal', never 'auto'", FORM == "equal")
        check("PLANT is the lab constant, identical to roache_triple.PLANT",
              PLANT == RT.PLANT == 1.234e-03)
        check("Fs is 1.25, identical to roache_triple.FS", FS == RT.FS == 1.25)

        # ---------------------------------------------------------------
        print("\n(ii) the ladder geometry: r21 = r32 = 2 EXACTLY, and the "
              "equal-ratio path refuses otherwise")
        r21 = RT.refinement_ratio(4096, 16384, DIM)
        r32 = RT.refinement_ratio(1024, 4096, DIM)
        check("r21 == 2.0 exactly at dim = 2", abs(r21 - 2.0) < 1e-15,
              "r21 = %.17g" % r21)
        check("r32 == 2.0 exactly at dim = 2", abs(r32 - 2.0) < 1e-15,
              "r32 = %.17g" % r32)
        try:
            RT.triple_from_cells(1.1, 1.04, 1.01, 1024, 5000, 16384, DIM,
                                 form=FORM)
            check("form='equal' REFUSES an unequal ladder (mutation control)",
                  False, "no refusal", mutation=True)
        except RT.Refusal:
            check("form='equal' REFUSES an unequal ladder (mutation control)",
                  True, "an unequal ladder cannot be silently graded on the "
                        "equal formula", mutation=True)
        t2 = RT.triple_from_cells(1.16, 1.04, 1.01, 1024, 4096, 16384, DIM,
                                  form=FORM)
        t3 = RT.triple_from_cells(1.16, 1.04, 1.01, 1024, 4096, 16384, 3,
                                  form=FORM)
        check("the SAME ladder read at dim = 3 gives an order exactly 1.5x "
              "the dim = 2 one (the 4G defect; mutation control)",
              abs(t3["order"] / t2["order"] - 1.5) < 1e-12,
              "p2 = %.6f, p3 = %.6f" % (t2["order"], t3["order"]),
              mutation=True)

        # ---------------------------------------------------------------
        print("\n(iii) N-T8 VALUE CONTROL on the F11 read path: a synthetic "
              ".xy whose answer is known by construction")
        stations = [1.0000, 0.9766, 0.8047, 0.5000, 0.2813, 0.0000]
        values = [0.111111111111, -0.222222222222, 0.333333333333,
                  -0.444444444444, 0.555555555555, 0.0]
        xy = os.path.join(tmpd, "uAlongX05_U.xy")
        write_xy(xy, _synth_xy("uAlongX05", stations, values))
        for s, v in zip(stations, values):
            got, coord = select_station(parse_xy(xy, "uAlongX05"),
                                        "uAlongX05", "u", s, xy)
            check("station y = %.4f reads its CONSTRUCTED value %.12f to "
                  "1e-12 relative" % (s, v),
                  abs(got - v) <= 1e-12 * max(1.0, abs(v))
                  and abs(coord - s) < 1e-12,
                  "read %.12f at coord %.4f" % (got, coord))

        print("      MUTATION: move one station's value and prove the READ "
              "changes by exactly that")
        mut = list(values)
        mut[1] += 0.25
        write_xy(xy, _synth_xy("uAlongX05", stations, mut))
        got, _ = select_station(parse_xy(xy, "uAlongX05"), "uAlongX05", "u",
                                0.9766, xy)
        check("mutating y = 0.9766 by +0.25 moves the read by exactly +0.25",
              abs(got - (values[1] + 0.25)) <= 1e-12, "read %.12f" % got,
              mutation=True)
        got_other, _ = select_station(parse_xy(xy, "uAlongX05"), "uAlongX05",
                                      "u", 0.5000, xy)
        check("and the OTHER station did NOT move (the selector is not "
              "returning a fixed row)",
              abs(got_other - values[3]) <= 1e-12, "read %.12f" % got_other,
              mutation=True)
        write_xy(xy, _synth_xy("uAlongX05", stations, values))

        # ---------------------------------------------------------------
        print("\n(iv) the parser refuses rather than degrades")
        bad = os.path.join(tmpd, "bad_uAlongX05_U.xy")
        rows = [list(r) for r in _synth_xy("uAlongX05", stations, values)]
        rows[2][COL["x"]] = 0.4                       # fixed coord wrong
        write_xy(bad, [tuple(r) for r in rows])
        try:
            parse_xy(bad, "uAlongX05")
            check("REFUSES a uAlongX05 file whose x is not 0.5 on every row",
                  False, "no refusal")
        except Refusal as exc:
            check("REFUSES a uAlongX05 file whose x is not 0.5 on every row",
                  True, str(exc)[:60])
        with open(bad, "w") as fh:
            fh.write("0.5 0.9766 0.05 1.0\n")
        try:
            parse_xy(bad, "uAlongX05")
            check("REFUSES a row that is not six columns", False, "no refusal")
        except Refusal:
            check("REFUSES a row that is not six columns", True)
        with open(bad, "w") as fh:
            fh.write("# x y z p q r\n0.5 0.9766 0.05 1 0 0\n")
        try:
            parse_xy(bad, "uAlongX05")
            check("REFUSES a header naming columns this layout does not "
                  "expect", False, "no refusal")
        except Refusal:
            check("REFUSES a header naming columns this layout does not "
                  "expect", True)
        dup = os.path.join(tmpd, "dup_uAlongX05_U.xy")
        write_xy(dup, _synth_xy("uAlongX05", [0.5, 0.5], [1.0, 2.0]))
        try:
            parse_xy(dup, "uAlongX05")
            check("REFUSES duplicated station coordinates", False, "no refusal")
        except Refusal:
            check("REFUSES duplicated station coordinates", True)
        try:
            select_station(parse_xy(xy, "uAlongX05"), "uAlongX05", "u", 0.7,
                           xy)
            check("REFUSES a station that is not sampled", False, "no refusal")
        except Refusal:
            check("REFUSES a station that is not sampled", True)

        # ---------------------------------------------------------------
        print("\n(v) the planted-zero controls, and a CONTROL ON THE CONTROL "
              "-- PZ-2 must be able to FAIL")
        p1, p2, p3 = pz_controls(xy, "uAlongX05", "u", 0.9766)
        check("PZ-1: the F11 parser + station selector SEES its planted "
              "1.234e-03 to 1e-12", p1["passed"]
              and abs(p1["reader_delta"] - PLANT) <= PZ_TOL,
              "saw %.6e" % p1["reader_delta"])
        check("PZ-2: a plant at every one of the %d OTHER stations leaves the "
              "graded value untouched" % p2["foreign_stations_tested"],
              p2["passed"] and p2["foreign_stations_tested"] == 5)
        check("PZ-3: nearest-coordinate re-derivation reproduces the "
              "round(coord,4) lookup to 1e-12", p3["passed"],
              "delta %.3e" % p3["delta"])
        after = parse_xy(xy, "uAlongX05")
        v_after, _ = select_station(after, "uAlongX05", "u", 0.9766, xy)
        check("the controls did not disturb the graded artifact",
              abs(v_after - values[1]) == 0.0, "planted into temp copies only")

        print("      MUTATION: a DELIBERATELY BROKEN selector that returns a "
              "FIXED ROW must FAIL PZ-2")
        real_select = globals()["select_station"]

        def fixed_row_selector(rows_, set_name_, component_, station_,
                               path_="<memory>"):
            r = rows_[1]                              # always row 1
            return (float(r[COL[COMPONENT_OF[component_]]]),
                    float(station_))                  # and LIES about the coord
        globals()["select_station"] = fixed_row_selector
        try:
            pz_controls(xy, "uAlongX05", "u", 0.5000)
            check("a fixed-row selector FAILS PZ-2 (control on the control)",
                  False, "PZ-2 passed a selector that reads the wrong row",
                  mutation=True)
        except Refusal as exc:
            check("a fixed-row selector FAILS PZ-2 (control on the control)",
                  "PZ-2 FAILED" in str(exc) or "PZ-1 FAILED" in str(exc),
                  str(exc)[:70], mutation=True)
        finally:
            globals()["select_station"] = real_select
        blind = RT.external_plant_control("blinded", 1.0, 1.0)
        check("a BLIND reader fails external_plant_control", not blind["passed"])

        # ---------------------------------------------------------------
        print("\n(vi) N-T8 VALUE CONTROL on the GRADE: a synthetic "
              "second-order ladder whose limit is 1.0 by construction")
        print("      The ladder is 1.16 / 1.04 / 1.01 on F11's OWN cells "
              "1024/4096/16384 at dim = 2.\n      It is a power law with limit "
              "1.0 by construction (e32/e21 = 4 exactly, so\n      "
              "p = ln4/ln2 = 2 and the extrapolate is 1.01 - 0.03/3 = 1.00), "
              "and it is the\n      SAME construction N-T8 registers and the "
              "frozen instrument's own (iii-b) uses.\n      It is chosen over "
              "f = 1 + 0.1 h^2 because that form loses five digits to\n      "
              "cancellation before the order is ever formed -- see the "
              "conditioning control below.")
        exact = 1.0
        vals = [1.16, 1.04, 1.01]
        lv = [dict(name=n, cells=c, value=v) for n, c, v in
              zip(LEVEL_NAMES, (1024, 4096, 16384), vals)]
        it_ok = {n: "CONVERGED" for n in LEVEL_NAMES}
        pl_ok = {n: "PLATEAUED" for n in LEVEL_NAMES}
        fine = vals[-1]
        row = RT.grade_ladder("synthetic", lv, DIM,
                              (fine - 1e-6, fine + 1e-6), p1,
                              iterative_states=it_ok, plateau_states=pl_ok,
                              fs=FS, form=FORM)
        check("the synthetic ladder recovers the CONSTRUCTED order p = 2 to "
              "1e-12", abs(row["order"] - 2.0) <= 1e-12 * 2.0,
              "p = %.16f" % row["order"])
        check("and extrapolates to the CONSTRUCTED limit 1.0 to 1e-12 "
              "relative", abs(row["richardson"] - exact) <= 1e-12 * exact,
              "richardson = %.16f" % row["richardson"])
        print("      CONDITIONING CONTROL, so the 1e-12 above is not read as "
              "a claim about every ladder:")
        hs = [RT.representative_h(c, DIM) for c in (1024, 4096, 16384)]
        pl_vals = [exact + 0.1 * h ** 2.0 for h in hs]
        pl_row = RT.triple_from_cells(*pl_vals, 1024, 4096, 16384, DIM,
                                      form=FORM)
        check("f = 1 + 0.1 h^2 on the SAME cells recovers p = 2 only to 1e-9 "
              "-- the loss is CANCELLATION in forming e21, not a defect in "
              "the instrument",
              1e-12 < abs(pl_row["order"] - 2.0) <= 1e-9,
              "p = %.14f, error %.3e" % (pl_row["order"],
                                         abs(pl_row["order"] - 2.0)))
        check("and its extrapolate still lands on 1.0 to 1e-12 relative "
              "(the extrapolate is better conditioned than the order)",
              abs(pl_row["richardson"] - exact) <= 1e-12 * exact,
              "richardson = %.16f" % pl_row["richardson"])
        check("richardson + richardson_parent_convention == 2 * f_fine "
              "exactly (the sign identity)",
              abs(row["richardson"] + row["richardson_parent_convention"]
                  - 2.0 * fine) < 1e-15)
        check("verdict is PASS inside the band, with a GCI printed",
              row["verdict"] == "PASS" and "GCI_pct" in row,
              "GCI %.6f %%" % row["GCI_pct"])

        print("      MUTATION: the SAME ladder outside the band must GATE FAIL")
        row_f = RT.grade_ladder("synthetic", lv, DIM, (fine + 1.0, fine + 2.0),
                                p1, iterative_states=it_ok,
                                plateau_states=pl_ok, fs=FS, form=FORM)
        check("a band violation IS caught: same triple, band moved -> "
              "GATE FAIL", row_f["verdict"] == "GATE FAIL"
              and row_f["band_verdict"] == "GATE FAIL", mutation=True)
        print("      MUTATION: perturb the COARSE value into non-monotonicity")
        lv_osc = copy.deepcopy(lv)
        lv_osc[0]["value"] = vals[-1] - 1.0
        row_o = RT.grade_ladder("synthetic", lv_osc, DIM,
                                (fine - 1e-6, fine + 1e-6), p1,
                                iterative_states=it_ok, plateau_states=pl_ok,
                                fs=FS, form=FORM)
        check("a non-monotone triple -> NOT A RESULT with NO GCI, even though "
              "the band verdict was PASS",
              row_o["verdict"] == "NOT A RESULT"
              and row_o["band_verdict"] == "PASS"
              and "GCI_pct" not in row_o, mutation=True)
        print("      MUTATION: an UNMEASURED plateau must outrank a PASS")
        row_p = RT.grade_ladder("synthetic", lv, DIM,
                                (fine - 1e-6, fine + 1e-6), p1,
                                iterative_states=it_ok,
                                plateau_states=dict(pl_ok, fine="UNMEASURED"),
                                fs=FS, form=FORM)
        check("plateau UNMEASURED -> NOT A RESULT, band verdict still PASS "
              "beside it", row_p["verdict"] == "NOT A RESULT"
              and row_p["band_verdict"] == "PASS", mutation=True)
        print("      MUTATION: an unconverged level must outrank a PASS")
        row_i = RT.grade_ladder("synthetic", lv, DIM,
                                (fine - 1e-6, fine + 1e-6), p1,
                                iterative_states=dict(it_ok,
                                                      medium="CANNOT_TELL"),
                                plateau_states=pl_ok, fs=FS, form=FORM)
        check("iterative CANNOT_TELL -> NOT A RESULT (an unevaluated step is "
              "not a passed one)", row_i["verdict"] == "NOT A RESULT",
              mutation=True)

        # ---------------------------------------------------------------
        print("\n(vii) every one of the six FROZEN bands is exercised, inside "
              "and outside")
        for g in GATES:
            eps = g["band_half"] * 1e-6
            inside, _ = RT.band_verdict(g["reference"], (g["lo"], g["hi"]))
            out_hi, _ = RT.band_verdict(g["hi"] + eps, (g["lo"], g["hi"]))
            out_lo, _ = RT.band_verdict(g["lo"] - eps, (g["lo"], g["hi"]))
            edge_hi, _ = RT.band_verdict(g["hi"], (g["lo"], g["hi"]))
            check("%s: reference PASSes, both edges PASS, and a value %g "
                  "outside either edge GATE FAILs" % (g["id"], eps),
                  inside == "PASS" and edge_hi == "PASS"
                  and out_hi == "GATE FAIL" and out_lo == "GATE FAIL",
                  mutation=True)

        # ---------------------------------------------------------------
        print("\n(viii) the plateau measurement, on a synthetic ARM B sample "
              "tree")
        print("      2026-08-25 PRE-COMPUTE AMENDMENT. The tree below is the "
              "layout the mechanism probe\n      MEASURED at Re 1000, n = 32: "
              "a periodic series at 250 and 500 under\n      "
              "postProcessing/%s/, and the graded artifact at the CONVERGED\n"
              "      iteration 747 under postProcessing/%s/747/ -- the frozen "
              "literal path.\n      q(final) is read from the GRADED "
              "directory; the earlier term from the SERIES."
              % (SERIES_DIR, PROFILES_DIR))
        case = os.path.join(tmpd, "case")
        series = os.path.join(case, "postProcessing", SERIES_DIR)
        graded = os.path.join(case, "postProcessing", PROFILES_DIR)
        N_CONV = 747
        # Values EXACT IN BINARY, so the 1e-12 assertions below are claims
        # about the reader and not about decimal rounding: the drift is
        # 2**-22 = 2.384185791015625e-07 exactly, comfortably under the frozen
        # 1.0e-6 threshold.
        V_250 = -0.25
        V_500 = -0.30                 # deliberately FAR from both, to prove
                                      # the >=250-iteration window picks 250
                                      # and NOT the nearer sample at 500
        DRIFT = 2.0 ** -22
        V_747 = V_250 + DRIFT

        def _write_sample(base, t, v):
            d = os.path.join(base, str(t))
            os.makedirs(d, exist_ok=True)
            write_xy(os.path.join(d, "uAlongX05_U.xy"),
                     _synth_xy("uAlongX05", stations,
                               [0.0, 0.0, 0.0, v, 0.0, 0.0]))

        _write_sample(series, 250, V_250)
        _write_sample(series, 500, V_500)
        _write_sample(graded, N_CONV, V_747)

        st, det = plateau_state(case, "uAlongX05", "u", 0.5000, N_CONV)
        check("PLATEAUED when the drift over a >=%d-iteration gap is under "
              "%g" % (PLATEAU_MIN_ITER_GAP, PLATEAU_TOL), st == "PLATEAUED",
              "drift %.6e over %d -> %d" % (det["drift"],
                                            det["compared_iteration"],
                                            det["final_iteration"]))
        check("N-T8 VALUE CONTROL: the drift is the CONSTRUCTED 2**-22 = "
              "%.17g to 1e-12 relative" % DRIFT,
              abs(det["drift"] - DRIFT) <= 1e-12 * DRIFT,
              "read %.17g" % det["drift"])
        check("q(final) is the CONSTRUCTED converged value %.17g and "
              "q(earlier) the CONSTRUCTED %.17g, both to 1e-12 relative"
              % (V_747, V_250),
              abs(det["q_final"] - V_747) <= 1e-12 * abs(V_747)
              and abs(det["q_earlier"] - V_250) <= 1e-12 * abs(V_250))
        check("the compared sample is the latest one at least %d iterations "
              "earlier -- 250, NOT the nearer 500 (%d > %d - %d)"
              % (PLATEAU_MIN_ITER_GAP, 500, N_CONV, PLATEAU_MIN_ITER_GAP),
              det["compared_iteration"] == 250
              and det["iteration_gap"] == N_CONV - 250
              and abs(det["q_earlier"] - V_500) > 0.04,
              "gap %d" % det["iteration_gap"])
        check("q(final) is read from postProcessing/%s/%d/ -- the FROZEN "
              "literal path at the converged iteration -- and the earlier "
              "term from postProcessing/%s/250/"
              % (PROFILES_DIR, N_CONV, SERIES_DIR),
              det["final_read_from"].endswith(os.path.join(PROFILES_DIR,
                                                           str(N_CONV)))
              and det["earlier_read_from"].endswith(
                  os.path.join(SERIES_DIR, "250")))

        print("      THE MUTATION THIS AMENDMENT EXISTS FOR: point the "
              "plateau reader BACK at %s" % PROFILES_DIR)
        print("      %s holds exactly ONE directory -- the converged "
              "iteration -- so a reader pointed\n      there finds no earlier "
              "sample at all. It must go UNMEASURED, never PLATEAUED."
              % PROFILES_DIR)
        _real_series_dir = globals()["SERIES_DIR"]
        globals()["SERIES_DIR"] = PROFILES_DIR
        try:
            st_m, det_m = plateau_state(case, "uAlongX05", "u", 0.5000, N_CONV)
        finally:
            globals()["SERIES_DIR"] = _real_series_dir
        check("the plateau reader pointed back at %s -> UNMEASURED, never a "
              "pass (mutation control)" % PROFILES_DIR,
              st_m == "UNMEASURED", det_m["reason"][:64], mutation=True)
        check("CONTROL ON THAT CONTROL: with %s restored the same tree reads "
              "PLATEAUED again, so the mutation above is not an artefact of "
              "the harness" % SERIES_DIR,
              plateau_state(case, "uAlongX05", "u", 0.5000,
                            N_CONV)[0] == "PLATEAUED")

        print("      THE MUTATION THE SUPERVISOR'S RULING NAMES: take the "
              "GRADED value from the PERIODIC series")
        print("      Arm B's entire content is that the two reads are "
              "SEPARATE. A comparator whose GRADED\n      read is pointed at "
              "%s is reading a different artifact at a different\n      "
              "iteration; it must REFUSE, never return a number."
              % SERIES_DIR)
        _real_profiles_dir = globals()["PROFILES_DIR"]
        globals()["PROFILES_DIR"] = SERIES_DIR
        try:
            _st_g, _ = plateau_state(case, "uAlongX05", "u", 0.5000, N_CONV)
            _g_ref, _gmsg = False, "returned %s without refusing" % _st_g
        except Refusal as _exc:
            _g_ref, _gmsg = True, str(_exc)
        finally:
            globals()["PROFILES_DIR"] = _real_profiles_dir
        check("the GRADED read pointed at %s REFUSES: the periodic series has "
              "no directory at the converged iteration %d, and a comparator "
              "that grades the series is not grading what C4 names (mutation "
              "control)" % (SERIES_DIR, N_CONV), _g_ref, _gmsg[:64],
              mutation=True)
        check("CONTROL ON THAT CONTROL: with %s restored the same tree reads "
              "PLATEAUED again" % PROFILES_DIR,
              plateau_state(case, "uAlongX05", "u", 0.5000,
                            N_CONV)[0] == "PLATEAUED")

        print("      THE REJECTED ALTERNATIVE, QUANTIFIED: grade the LAST "
              "PERIODIC directory instead of the converged one")
        _fb = os.path.join(series, "500", "uAlongX05_U.xy")
        _q_fb, _ = select_station(parse_xy(_fb, "uAlongX05"), "uAlongX05",
                                  "u", 0.5000, _fb)
        _gap = abs(_q_fb - det["q_final"])
        check("relaxing C4 to accept the last periodic directory would grade "
              "iteration 500 and not %d, moving the graded value by the "
              "CONSTRUCTED %.17g -- %.0fx the %g plateau tolerance.  That is a "
              "GATE CHANGE, which is why arm B was adopted and the relaxation "
              "REJECTED" % (N_CONV, abs(V_500 - V_747), _gap / PLATEAU_TOL,
                            PLATEAU_TOL),
              abs(_q_fb - V_500) <= 1e-12 * abs(V_500)
              and _gap > 1.0e4 * PLATEAU_TOL, "gap %.6e" % _gap)

        print("      MUTATION: widen the drift past the threshold")
        _write_sample(graded, N_CONV, V_250 + 2.0 ** -19)
        st2, det2 = plateau_state(case, "uAlongX05", "u", 0.5000, N_CONV)
        check("NOT_PLATEAUED once the drift exceeds %g (mutation control)"
              % PLATEAU_TOL, st2 == "NOT_PLATEAUED",
              "drift %.6e" % det2["drift"], mutation=True)
        _write_sample(graded, N_CONV, V_747)

        print("      MUTATION: a series that is TOO SHORT -- every sample "
              "inside the 250-iteration window")
        shutil.rmtree(os.path.join(series, "250"))
        st4, det4 = plateau_state(case, "uAlongX05", "u", 0.5000, N_CONV)
        check("only a sample at 500, which is inside the window of 747 -> "
              "UNMEASURED (reported unmeasured, NOT passed)",
              st4 == "UNMEASURED" and det4["samples"] == [500],
              det4["reason"][:64], mutation=True)

        print("      MUTATION: remove the %s directory entirely" % SERIES_DIR)
        shutil.rmtree(series)
        st3, det3 = plateau_state(case, "uAlongX05", "u", 0.5000, N_CONV)
        check("an ABSENT periodic series -> UNMEASURED naming %s, never a pass"
              % SERIES_DIR,
              st3 == "UNMEASURED" and SERIES_DIR in det3["reason"]
              and det3["samples"] == [], det3["reason"][:64], mutation=True)
        check("an unknown converged iteration -> UNMEASURED, never a pass",
              plateau_state(case, "uAlongX05", "u", 0.5000, None)[0]
              == "UNMEASURED", mutation=True)

        print("      and it REFUSES, rather than degrades, if the GRADED "
              "artifact is missing")
        _write_sample(series, 250, V_250)
        shutil.rmtree(os.path.join(graded, str(N_CONV)))
        try:
            plateau_state(case, "uAlongX05", "u", 0.5000, N_CONV)
            check("a missing graded artifact REFUSES", False, "no refusal",
                  mutation=True)
        except Refusal:
            check("a missing graded artifact REFUSES rather than falling back "
                  "to the last periodic sample", True, mutation=True)
        shutil.rmtree(case)

        # ---------------------------------------------------------------
        print("\n(ix) the completion rule, on a synthetic case")
        cc = os.path.join(tmpd, "cc")
        os.makedirs(os.path.join(cc, "system"))
        os.makedirs(os.path.join(cc, "0"))
        open(os.path.join(cc, "system", "controlDict"), "w").write(
            "endTime         4000;\n")
        open(os.path.join(cc, "0", "U"), "w").write("x\n")
        open(os.path.join(cc, "run_rc.txt"), "w").write("0\n")
        log_ok = ("".join("Time = %d\nExecutionTime = 1 s\n" % i
                          for i in range(1, 1506))
                  + "SIMPLE solution converged in 1505 iterations\n\nEnd\n")
        open(os.path.join(cc, SOLVER_LOG), "w").write(log_ok)
        os.makedirs(os.path.join(cc, "1505"))
        # NOTE the LITERAL "centerlineProfiles" here, not PROFILES_DIR: the
        # completion clause C4 names a literal path in the frozen document and
        # this control is what proves the constant still equals it.
        check("PROFILES_DIR is still the frozen literal 'centerlineProfiles'",
              PROFILES_DIR == "centerlineProfiles")
        sd = os.path.join(cc, "postProcessing", "centerlineProfiles", "1505")
        os.makedirs(sd)
        import time as _t
        _t.sleep(0.01)
        for f in REQUIRED_FIELDS:
            open(os.path.join(cc, "1505", f), "w").write("x\n")
        for s in SAMPLE_SETS:
            write_xy(os.path.join(sd, "%s_U.xy" % s),
                     _synth_xy(s, stations, values))
        ok, cl = completion_check(cc)
        check("a well-formed case passes all six clauses", ok,
              ",".join(k for k in sorted(cl) if k.startswith("C")))
        print("      MUTATION: break each clause in turn and prove it is "
              "caught")
        open(os.path.join(cc, "run_rc.txt"), "w").write("1\n")
        check("C1 caught: rc != 0", not completion_check(cc)[0], mutation=True)
        open(os.path.join(cc, "run_rc.txt"), "w").write("0\n")
        open(os.path.join(cc, SOLVER_LOG), "w").write(
            log_ok.replace("\nEnd\n", "\n"))
        ok2, cl2 = completion_check(cc)
        check("C2 caught: no End line",
              not ok2 and not cl2["C2_end_line"], mutation=True)
        open(os.path.join(cc, SOLVER_LOG), "w").write(log_ok)
        open(os.path.join(cc, "system", "controlDict"), "w").write(
            "endTime         1505;\n")
        ok3, cl3 = completion_check(cc)
        check("C3 caught: a CAP-terminated run (N == endTime) FAILS, which is "
              "the departure section 5 declares",
              not ok3 and not cl3["C3_converged_before_cap"], mutation=True)
        open(os.path.join(cc, "system", "controlDict"), "w").write(
            "endTime         4000;\n")
        open(os.path.join(cc, SOLVER_LOG), "w").write(
            log_ok.replace("ExecutionTime = 1 s\n", "", 1))
        ok4, cl4 = completion_check(cc)
        check("C5 caught: an ExecutionTime line missing from the log",
              not ok4 and not cl4["C5_log_step_integrity"], mutation=True)
        open(os.path.join(cc, SOLVER_LOG), "w").write(log_ok)
        os.unlink(os.path.join(sd, "uAlongX05_U.xy"))
        ok5, cl5 = completion_check(cc)
        check("C4 caught: a sampled .xy missing at the converged iteration",
              not ok5 and not cl5["C4_fields_and_samples"], mutation=True)
        write_xy(os.path.join(sd, "uAlongX05_U.xy"),
                 _synth_xy("uAlongX05", stations, values))
        _t.sleep(0.01)
        os.utime(os.path.join(cc, "0", "U"), None)      # 0/ newer than fields
        ok6, cl6 = completion_check(cc)
        check("C6 caught: the AGE GUARD fails when 0/ is newer than the "
              "fields", not ok6 and not cl6["C6_age_guard"], mutation=True)

        print("      and the mesh birth certificate")
        check("an ABSENT log.checkMesh is reported ABSENT, not clean",
              checkmesh_certificate(cc)["state"] == "ABSENT"
              and not checkmesh_certificate(cc)["clean"])
        open(os.path.join(cc, CHECKMESH_LOG), "w").write("Mesh OK.\n\nEnd\n")
        check("'Mesh OK.' reads CLEAN", checkmesh_certificate(cc)["clean"])
        open(os.path.join(cc, CHECKMESH_LOG), "w").write(
            "Failed 2 mesh checks.\n\nEnd\n")
        check("'Failed N mesh checks' reads NOT_CLEAN (mutation control)",
              checkmesh_certificate(cc)["state"] == "NOT_CLEAN", mutation=True)

        # ---------------------------------------------------------------
        print("\n(x) the freeze checks bite")
        inst = verify_instrument_blob()
        check("the instrument on disk IS blob %s" % INSTRUMENT_BLOB,
              inst["verified"], "sha256 %s" % inst["sha256"][:16])
        print("      MUTATION: a single byte changed in the instrument must "
              "REFUSE")
        with open(os.path.join(REPO, INSTRUMENT_REL), "rb") as fh:
            data = fh.read()
        check("git_blob_sha1 reproduces git's own object id",
              git_blob_sha1(data) == INSTRUMENT_BLOB)
        check("a one-byte mutation changes the blob id (mutation control)",
              git_blob_sha1(data + b"\n") != INSTRUMENT_BLOB, mutation=True)
        try:
            verify_own_freeze("0" * 40)
            check("REFUSES a pre-registration commit that does not exist",
                  False, "no refusal")
        except Refusal:
            check("REFUSES a pre-registration commit that does not exist", True)

        # ---------------------------------------------------------------
        print("\n(xi) the launcher agrees with this comparator on the matrix")
        try:
            import rerun_f11
            check("rerun_f11 LEVELS match", rerun_f11.LEVELS == LEVELS,
                  str(rerun_f11.LEVELS))
            check("rerun_f11 RUNGS match", rerun_f11.RUNGS == RUNGS)
            check("rerun_f11 cap is 13.0 core-min / 780 core-s",
                  rerun_f11.CAP_CORE_MIN == 13.0
                  and rerun_f11.CAP_CORE_S == 780.0)
            frozen_caps = {("re1000", "coarse"): 60, ("re1000", "medium"): 60,
                           ("re1000", "fine"): 442, ("re100", "coarse"): 60,
                           ("re100", "medium"): 60, ("re100", "fine"): 674}
            bad = {k: (round(rerun_f11.wall_cap(k)), v)
                   for k, v in frozen_caps.items()
                   if round(rerun_f11.wall_cap(k)) != v}
            check("max(60, 2.5 x predicted) reproduces section 7's frozen "
                  "per-run caps 60/60/442/60/60/674", not bad, str(bad))
            check("the four waves sum to the frozen 8.02 core-min prediction",
                  abs(sum(rerun_f11.PRED.values()) / 60.0 - 8.02) < 0.005,
                  "%.4f core-min" % (sum(rerun_f11.PRED.values()) / 60.0))

            # ---- THE 2026-08-25 PRE-COMPUTE AMENDMENT, CHECKED ACROSS BOTH
            # SCRIPTS.  The launcher writes two separately named sampling
            # objects and this comparator reads two separately named
            # directories.  If either side is collapsed the other silently
            # stops measuring what it claims to measure, so the coupling is
            # asserted here rather than left to two matching comments.
            check("the launcher's GRADED object name IS this comparator's "
                  "graded directory", rerun_f11.PROFILES_OBJECT == PROFILES_DIR,
                  rerun_f11.PROFILES_OBJECT)
            check("the launcher's PERIODIC object name IS this comparator's "
                  "plateau series directory",
                  rerun_f11.SERIES_OBJECT == SERIES_DIR,
                  rerun_f11.SERIES_OBJECT)
            check("the two names are DIFFERENT -- collapsing them back into "
                  "one is the defect the amendment repairs, and this check "
                  "FAILS if they are (mutation control)",
                  PROFILES_DIR != SERIES_DIR
                  and rerun_f11.PROFILES_OBJECT != rerun_f11.SERIES_OBJECT,
                  mutation=True)
            check("the launcher samples every %d iterations, which is <= the "
                  "plateau's %d-iteration window, so any run converging at N "
                  ">= %d has an earlier sample to compare against"
                  % (rerun_f11.SERIES_INTERVAL, PLATEAU_MIN_ITER_GAP,
                     2 * PLATEAU_MIN_ITER_GAP),
                  rerun_f11.SERIES_INTERVAL <= PLATEAU_MIN_ITER_GAP)
            import cavity_ladder as _cl
            _virgin = _cl.control_dict(4000)
            try:
                rerun_f11.assert_arm_b_arrangement(_virgin, 4000)
                check("the launcher's arrangement asserter REFUSES a "
                      "single-sampling-object dictionary (cross-script "
                      "mutation control)", False, "no refusal", mutation=True)
            except RuntimeError as _exc:
                check("the launcher's arrangement asserter REFUSES a "
                      "single-sampling-object dictionary (cross-script "
                      "mutation control)", "COLLAPSED" in str(_exc),
                      str(_exc)[:60], mutation=True)
            cap_sum = sum(rerun_f11.wall_cap(k) for k in frozen_caps)
            check("the per-run caps sum ABOVE the budget -- which is why the "
                  "watchdog, not the per-run caps, is the binding enforcement",
                  cap_sum > rerun_f11.CAP_CORE_S,
                  "%.3f s (%.2f core-min) vs a %.0f s budget"
                  % (cap_sum, cap_sum / 60.0, rerun_f11.CAP_CORE_S))
            # A DEFECT IN THE FROZEN DOCUMENT, surfaced by this check and
            # carried in every selftest run rather than left in a report.
            # Section 7 says "the per-run caps sum to 1,296 s (21.6
            # core-min)". The six caps that same paragraph registers -- 60,
            # 60, 442, 60, 60, 674 -- sum to 1,355.575 s (22.59 core-min).
            # The arithmetic is wrong by 59.575 s. It is IMMATERIAL to the
            # clause's conclusion, which is that the caps sum ABOVE the 780 s
            # budget so the watchdog is the binding enforcement: that holds a
            # fortiori at the larger figure. NOTHING HERE IS ADJUSTED TO SUIT
            # IT -- the caps implemented are the six the document registers.
            check("DOCUMENT DEFECT, recorded not repaired: section 7 states "
                  "the caps sum to 1,296 s where its own six caps sum to "
                  "1,355.575 s. Immaterial -- both are far above the 780 s "
                  "budget and the conclusion holds a fortiori.",
                  abs(cap_sum - 1355.575) < 1e-3,
                  "document 1296.000 s | registered caps %.3f s | "
                  "discrepancy %.3f s" % (cap_sum, cap_sum - 1296.0))
        except ImportError as exc:
            check("rerun_f11 imports", False, str(exc))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    n_ok = sum(1 for _, ok, _ in _CHECKS if ok)
    print("\n%d/%d checks passed" % (n_ok, len(_CHECKS)))
    print("%d of them are MUTATION controls -- each proves the grade CHANGES "
          "when the answer does." % len(_MUTATIONS))
    print("VALUE controls (N-T8): the six station reads at 1e-12, the "
          "synthetic order p = 2 at 1e-12,\nand the synthetic Richardson "
          "limit 1.0 at 1e-12 relative -- every one against a case whose\n"
          "answer is known by construction, none against a key's mere "
          "presence.")
    if n_ok != len(_CHECKS):
        print("\nFAILED: " + "; ".join(n for n, ok, _ in _CHECKS if not ok))
    return EXIT_OK if n_ok == len(_CHECKS) else EXIT_FAIL


# ===========================================================================
# 10. CLI
# ===========================================================================

def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--prereg-commit",
                    help="the commit whose tree carries the pre-registration "
                         "WITH its section 8.2 PRE-COMPUTE addendum recording "
                         "this file's sha256. REQUIRED to grade.")
    ap.add_argument("--root", default=os.path.join(HERE, "runs"))
    ap.add_argument("--json-out",
                    default=os.path.join(HERE, "F11_CONVERSION_GRADED.json"))
    ap.add_argument("--print-sha256", action="store_true",
                    help="print this file's sha256 and exit -- the value the "
                         "section 8.2 addendum records")
    a = ap.parse_args(argv)

    if a.print_sha256:
        print("%s  %s" % (sha256_file(os.path.abspath(__file__)), REL_SELF))
        return EXIT_OK
    if a.selftest:
        return selftest()
    if not a.prereg_commit:
        ap.error("--prereg-commit is required (or --selftest)")

    try:
        freeze = dict(instrument=verify_instrument_blob(),
                      self=verify_own_freeze(a.prereg_commit))
        rep = grade(a.root, freeze)
    except Refusal as exc:
        sys.stderr.write("REFUSE: %s\n" % exc)
        return EXIT_REFUSE
    except RT.Refusal as exc:
        sys.stderr.write("REFUSE (frozen instrument): %s\n" % exc)
        return EXIT_REFUSE

    print(format_report(rep))
    with open(a.json_out, "w") as fh:
        json.dump(rep, fh, indent=2, sort_keys=True, default=str)
    print("\nwritten: %s" % os.path.abspath(a.json_out))
    return overall_exit(rep)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
