#!/usr/bin/env python3
"""MDS-1 -- MESH DIMENSION SURVEY 1.

Reader for the survey named and owned in `docs/standards/MESH_STANDARD.md` §11.5,
as corrected by that file's §12 amendment of 2026-08-27.

WHAT THIS IS AND IS NOT
-----------------------
This reader COLLECTS a distribution. It sets NO threshold, issues NO verdict word,
and admits or rejects NO mesh. §11.4 already fixes that no value of either quantity
makes a mesh inadmissible; §11.2 fixes that a threshold may not be argued from the
case that made somebody look. Collecting the survey and setting a gate are different
acts and this file performs only the first.

ZERO COMPUTE. Both §11 quantities are read back from `log.checkMesh` files already
on disk. No solver, no mesher, no `checkMesh` invocation.

THE FIVE THINGS §11.5's OWN TEXT GOT WRONG, AND WHAT THIS READER DOES INSTEAD
----------------------------------------------------------------------------
1. ENUMERATOR. §11.5 counted `find . -name 'log.checkMesh*'`. That misses the
   `<stem>.log.checkMesh` filename shape entirely -- including the whole 78-log
   `verification/runs/MESH_AUDIT_runs/2026-08-08/` pool. §11.5 warned MDS-1 to name
   its enumerator or produce "a false zero of exactly the kind standing rule 3
   exists to catch", and then produced one. This reader covers BOTH shapes and
   states its enumerator in its own output.
2. LABEL FORMS ARE NOT EXHAUSTIVE. `=` and `:` do not cover the population: some
   runs stop before the aspect check and carry NEITHER. Such a log is recorded as
   `ABSENT`, never as a number and never dropped.
3. NON-POSITIVE MINIMUM VOLUME. The cell-volume ratio is UNDEFINED precisely where
   the mesh is worst. Behaviour is fixed HERE, before collection, so the specimen
   §11 most wants cannot silently leave the distribution: a mesh whose minimum cell
   volume is negative, zero, or unprinted is REPORTED AS SUCH with its negative
   value, is counted in the census, and is EXCLUDED from ratio percentiles with the
   exclusion stated as a number.
4/5. Provenance and home: see the §12 amendment. This file IS the discharge of
   §11.5's anti-deferral clause.

CONTROLS (standing rule 3). A zero from a reader not shown able to see a non-zero is
not evidence. `--selftest` drives four planted perturbations to FIRE and their
unperturbed twins to STAY SILENT. `--selftest` is run and its result recorded before
any distribution in this directory is believed.

REFUSALS. This reader REFUSES (exit 2) rather than degrades: under `python -O`; if
any `assert` statement is found in its own source; on any unreadable input; on a
corpus root that does not exist; and on any control that does not behave.

QUARANTINE. `verification/runs/F5b_runs/` is pruned by explicit path test on every
candidate and the pruned count is reported. Its reader awaits Sanaa's ruling on a
permission denial; nothing under it is opened by this file.

OUTSIDE-REPO ROOTS are read ONLY. Nothing outside the repository is written,
modified, moved or deleted by this file.
"""

import argparse
import ast
import json
import math
import os
import re
import shutil
import sys
import tempfile

VERSION = "MDS1-reader-1.0 (2026-08-27)"

# ---------------------------------------------------------------------------
# Refusal machinery. No `assert` statement appears anywhere in this file: under
# `python -O` an assert is stripped and a guard that vanishes is worse than no
# guard. Every check below raises or exits explicitly.
# ---------------------------------------------------------------------------

RC_REFUSE = 2


def refuse(reason, detail=""):
    sys.stderr.write("MDS-1 READER REFUSES: %s\n" % reason)
    if detail:
        sys.stderr.write("  %s\n" % detail)
    sys.stderr.write("  (refusing rather than degrading; exit %d)\n" % RC_REFUSE)
    sys.exit(RC_REFUSE)


def require(condition, reason, detail=""):
    if not condition:
        refuse(reason, detail)


def guard_optimised_interpreter():
    """`python -O` strips assert statements. This reader carries none, but a
    future editor might add one, so the interpreter mode itself is refused."""
    if not __debug__:
        sys.stderr.write(
            "MDS-1 READER REFUSES: running under `python -O`.\n"
            "  Optimised mode strips `assert` statements, so no guard written in this\n"
            "  file can be trusted to exist at runtime. Re-run without -O.\n"
            "  (exit %d)\n" % RC_REFUSE
        )
        sys.exit(RC_REFUSE)


def guard_no_assert_statements():
    """Count `ast.Assert` nodes in this file's own source. Required: exactly 0."""
    path = os.path.abspath(__file__)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            source = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        refuse("cannot read own source for the ast.Assert guard", "%s: %s" % (path, exc))
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        refuse("cannot parse own source for the ast.Assert guard", str(exc))
    count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))
    if count != 0:
        refuse(
            "this file contains %d `assert` statement(s); required 0" % count,
            "An assert vanishes under -O. Convert it to refuse()/require().",
        )
    return count


# ---------------------------------------------------------------------------
# Enumeration -- BOTH filename shapes, stated as a command in the output.
# ---------------------------------------------------------------------------

# Shape 1: the basename IS the log, optionally suffixed  -> log.checkMesh, log.checkMesh.1
# Shape 2: the log is stem-prefixed                      -> rung6b.log.checkMesh, c3b.log.checkMesh
NAME_SHAPES = ("log.checkMesh*", "*.log.checkMesh*")

ENUMERATOR_COMMAND = (
    "find <root> -path '*/verification/runs/F5b_runs' -prune -o "
    "\\( -name 'log.checkMesh*' -o -name '*.log.checkMesh*' \\) -type f -print"
)

# Excluded, and why, stated in the reader so it cannot be lost from a report:
#   .git/                       -- object store, not a run record
#   verification/runs/F5b_runs/ -- QUARANTINED pending Sanaa's ruling on a
#                                  permission denial; not opened, counted only
EXCLUSION_NOTE = {
    ".git": "git object store; not a run record",
    "F5b_runs": (
        "QUARANTINED pending Sanaa's ruling on a permission denial; "
        "not opened by this reader, only counted as pruned"
    ),
}

QUARANTINE_MARKER = os.path.join("verification", "runs", "F5b_runs")


def is_candidate_name(basename):
    if basename.startswith("log.checkMesh"):
        return True
    return ".log.checkMesh" in basename


def enumerate_logs(roots):
    """Walk `roots`, returning (kept_paths, pruned_quarantine_count).

    Pruning is by explicit path test on every candidate, not by a glob that might
    or might not match -- the quarantine is too important to leave to a pattern.
    """
    kept = []
    pruned = 0
    for root in roots:
        if not os.path.isdir(root):
            refuse("corpus root does not exist", root)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            if QUARANTINE_MARKER in os.path.abspath(dirpath):
                # Count candidates by FILENAME, recursively, and descend no further
                # with the reader: names are listed, contents are never read. A
                # count that stopped at the quarantine's top directory would report
                # 0 for a populated tree -- which is the false zero standing rule 3
                # exists to catch, produced by the guard itself. (This was caught by
                # control C6 on the first run of this reader, not reasoned about.)
                for qdir, _qsub, qfiles in os.walk(dirpath):
                    pruned += sum(1 for f in qfiles if is_candidate_name(f))
                dirnames[:] = []
                continue
            for name in filenames:
                if is_candidate_name(name):
                    full = os.path.join(dirpath, name)
                    if QUARANTINE_MARKER in os.path.abspath(full):
                        pruned += 1
                        continue
                    kept.append(full)
    return sorted(set(kept)), pruned


# ---------------------------------------------------------------------------
# Parsing. Field names verified against real logs, per §11.3.
# ---------------------------------------------------------------------------

RE_ASPECT_EQ = re.compile(r"Max aspect ratio\s*=\s*([-+0-9.eE]+)")
RE_ASPECT_COLON = re.compile(r"Max aspect ratio:\s*([-+0-9.eE]+)")
RE_ASPECT_FLAG = re.compile(r"\*\*\*High aspect ratio cells found")
RE_VOLUMES = re.compile(
    r"Min volume\s*=\s*([-+0-9.eE]+)\.\s*Max volume\s*=\s*([-+0-9.eE]+)\."
)
RE_NEGVOL = re.compile(r"Minimum negative volume:\s*([-+0-9.eE]+)")
RE_NEGVOL_COUNT = re.compile(r"Number of negative volume cells:\s*(\d+)")
RE_DIRECTIONS = re.compile(r"Mesh has\s+(\d+)\s+geometric")
RE_NONORTH = re.compile(r"Mesh non-orthogonality Max:\s*([-+0-9.eE]+)")
RE_SKEW = re.compile(r"Max skewness\s*[=:]\s*([-+0-9.eE]+)")
RE_CELLS = re.compile(r"^\s*cells:\s+(\d+)\s*$", re.MULTILINE)
RE_FAILED = re.compile(r"Failed\s+(\d+)\s+mesh checks")
RE_MESH_OK = re.compile(r"^Mesh OK\.", re.MULTILINE)

# Volume-status vocabulary. These are STATUS labels for a survey, NOT verdict words:
# §11 issues none and neither does this reader.
VOL_OK = "MIN_POSITIVE"
VOL_NEGATIVE = "MIN_NEGATIVE"
VOL_ZERO = "MIN_ZERO"
VOL_ABSENT = "MIN_VOLUME_LINE_ABSENT"

ASPECT_EQ = "EQUALS_FORM"
ASPECT_COLON = "COLON_FORM"
ASPECT_ABSENT = "ABSENT"


def to_float(text, path, field):
    try:
        return float(text)
    except (TypeError, ValueError):
        refuse(
            "unparsable %s value %r -- refusing rather than recording a plausible zero" % (field, text),
            path,
        )


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        refuse("unreadable input log", "%s: %s" % (path, exc))


def parse_log(path, text):
    """One record per log. NOTHING is ever dropped: a log that cannot supply a
    quantity records WHY, and is counted in the census either way."""
    record = {
        "path": path,
        "aspect_form": ASPECT_ABSENT,
        "max_aspect_ratio": None,
        "aspect_ratio_flagged": bool(RE_ASPECT_FLAG.search(text)),
        "min_cell_volume": None,
        "max_cell_volume": None,
        "cell_volume_ratio": None,
        "volume_status": VOL_ABSENT,
        "minimum_negative_volume": None,
        "negative_volume_cells": None,
        "geometric_directions": None,
        "max_non_orthogonality": None,
        "max_skewness": None,
        "cells": None,
        "checkMesh_verdict": None,
        "failed_checks": None,
    }

    m_eq = RE_ASPECT_EQ.search(text)
    m_co = RE_ASPECT_COLON.search(text)
    if m_eq and m_co:
        refuse(
            "log carries BOTH aspect-ratio label forms; §11.3 asserts they are "
            "mutually exclusive and this reader will not guess which is the mesh's",
            path,
        )
    if m_eq:
        record["aspect_form"] = ASPECT_EQ
        record["max_aspect_ratio"] = to_float(m_eq.group(1), path, "max aspect ratio (= form)")
    elif m_co:
        record["aspect_form"] = ASPECT_COLON
        record["max_aspect_ratio"] = to_float(m_co.group(1), path, "max aspect ratio (: form)")

    m_neg = RE_NEGVOL.search(text)
    if m_neg:
        record["minimum_negative_volume"] = to_float(m_neg.group(1), path, "minimum negative volume")
        m_negn = RE_NEGVOL_COUNT.search(text)
        if m_negn:
            record["negative_volume_cells"] = int(m_negn.group(1))

    m_vol = RE_VOLUMES.search(text)
    if m_vol:
        vmin = to_float(m_vol.group(1), path, "min cell volume")
        vmax = to_float(m_vol.group(2), path, "max cell volume")
        record["min_cell_volume"] = vmin
        record["max_cell_volume"] = vmax
        if vmin < 0.0:
            record["volume_status"] = VOL_NEGATIVE
        elif vmin == 0.0:
            record["volume_status"] = VOL_ZERO
        else:
            record["volume_status"] = VOL_OK
            record["cell_volume_ratio"] = vmax / vmin
    elif record["minimum_negative_volume"] is not None:
        # checkMesh printed the negative-volume diagnostic INSTEAD of the
        # `Min volume = ...` summary line. The mesh is the worst kind in the
        # population and it is recorded as such, not dropped.
        record["volume_status"] = VOL_NEGATIVE
        record["min_cell_volume"] = record["minimum_negative_volume"]

    m_dir = RE_DIRECTIONS.search(text)
    if m_dir:
        record["geometric_directions"] = int(m_dir.group(1))
    m_no = RE_NONORTH.search(text)
    if m_no:
        record["max_non_orthogonality"] = to_float(m_no.group(1), path, "max non-orthogonality")
    m_sk = RE_SKEW.search(text)
    if m_sk:
        record["max_skewness"] = to_float(m_sk.group(1), path, "max skewness")
    m_ce = RE_CELLS.search(text)
    if m_ce:
        record["cells"] = int(m_ce.group(1))

    m_fail = RE_FAILED.search(text)
    if m_fail:
        record["checkMesh_verdict"] = "Failed %s mesh checks." % m_fail.group(1)
        record["failed_checks"] = int(m_fail.group(1))
    elif RE_MESH_OK.search(text):
        record["checkMesh_verdict"] = "Mesh OK."
        record["failed_checks"] = 0
    return record


# ---------------------------------------------------------------------------
# Distribution
# ---------------------------------------------------------------------------

def percentile(sorted_values, fraction):
    """Linear-interpolated percentile on an already-sorted list."""
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = fraction * (len(sorted_values) - 1)
    low = int(math.floor(position))
    high = int(math.ceil(position))
    if low == high:
        return sorted_values[low]
    weight = position - low
    return sorted_values[low] * (1.0 - weight) + sorted_values[high] * weight


DECILES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
TAILS = [0.90, 0.95, 0.99]


def summarise(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return {"n": 0}
    out = {
        "n": len(vals),
        "min": vals[0],
        "max": vals[-1],
        "median": percentile(vals, 0.5),
        "deciles": {("d%d" % int(f * 10)): percentile(vals, f) for f in DECILES},
    }
    for f in TAILS:
        out["p%d" % int(f * 100)] = percentile(vals, f)
    return out


def build_distribution(records):
    def split(pred):
        return [r for r in records if pred(r)]

    two_d = split(lambda r: r["geometric_directions"] == 2)
    three_d = split(lambda r: r["geometric_directions"] == 3)
    unknown_d = split(lambda r: r["geometric_directions"] not in (2, 3))

    def block(subset, label):
        ratio_eligible = [r for r in subset if r["volume_status"] == VOL_OK]
        excluded = [r for r in subset if r["volume_status"] != VOL_OK]
        return {
            "label": label,
            "logs": len(subset),
            "aspect": {
                "summary": summarise([r["max_aspect_ratio"] for r in subset]),
                "absent": sum(1 for r in subset if r["aspect_form"] == ASPECT_ABSENT),
                "equals_form": sum(1 for r in subset if r["aspect_form"] == ASPECT_EQ),
                "colon_form": sum(1 for r in subset if r["aspect_form"] == ASPECT_COLON),
                "flagged": sum(1 for r in subset if r["aspect_ratio_flagged"]),
            },
            "cell_volume_ratio": {
                "summary": summarise([r["cell_volume_ratio"] for r in ratio_eligible]),
                "excluded_from_percentiles": len(excluded),
                "exclusion_reasons": {
                    status: sum(1 for r in excluded if r["volume_status"] == status)
                    for status in (VOL_NEGATIVE, VOL_ZERO, VOL_ABSENT)
                },
            },
        }

    # Cross-tabulation. §3.3 ASSERTS that high aspect ratio is dangerous in company
    # and harmless when aligned; §11.5 requires MDS-1 be able to TEST that rather
    # than inherit it. Tabulated, not concluded.
    def crosstab(subset):
        buckets = {}
        for r in subset:
            a = r["max_aspect_ratio"]
            if a is None:
                continue
            a_band = "aspect<1000" if a < 1000.0 else ("1000<=aspect<1e4" if a < 1e4 else "aspect>=1e4")
            no = r["max_non_orthogonality"]
            n_band = "nonorth_unknown" if no is None else ("nonorth<65" if no < 65.0 else ("65<=nonorth<70" if no < 70.0 else "nonorth>=70"))
            sk = r["max_skewness"]
            s_band = "skew_unknown" if sk is None else ("skew<4" if sk < 4.0 else "skew>=4")
            key = "%s | %s | %s" % (a_band, n_band, s_band)
            entry = buckets.setdefault(key, {"logs": 0, "checkMesh_failed": 0})
            entry["logs"] += 1
            if r["failed_checks"]:
                entry["checkMesh_failed"] += 1
        return dict(sorted(buckets.items()))

    return {
        "all": block(records, "all logs"),
        "two_d": block(two_d, "2-D (geometric_directions == 2)"),
        "three_d": block(three_d, "3-D (geometric_directions == 3)"),
        "directions_unknown": block(unknown_d, "geometric_directions not printed"),
        "crosstab_aspect_x_nonorth_x_skew": crosstab(records),
        "note_2d": (
            "In a 2-D mesh with a unit-thickness empty direction the cell-volume "
            "ratio is an in-plane AREA ratio, not a volume ratio (§11.4's 2-D "
            "caveat). The two splits are not the same statistic and are never pooled."
        ),
    }


# ---------------------------------------------------------------------------
# CONTROLS -- standing rule 3. Four planted perturbations, each driven to FIRE,
# each with an unperturbed twin driven to STAY SILENT.
# ---------------------------------------------------------------------------

BASE_LOG_EQ = """Check mesh...
Mesh stats
    points:           46720
    cells:            23040
Checking geometry...
    Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)
    Max aspect ratio = 805.199 OK.
    Min volume = 1.30653e-09. Max volume = 41.8474.  Total volume = 13825.7.  Cell volumes OK.
    Mesh non-orthogonality Max: 51.1237 average: 17.375
    Max skewness = 0.95723 OK.

Mesh OK.

End
"""

BASE_LOG_COLON = """Check mesh...
Mesh stats
    points:           99999
    cells:            92160
Checking geometry...
    Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)
 ***High aspect ratio cells found, Max aspect ratio: 2842.46, number of cells 34
    Min volume = 3.1e-10. Max volume = 41.8474.  Total volume = 13825.7.  Cell volumes OK.
    Mesh non-orthogonality Max: 55.0 average: 18.0
    Max skewness = 1.1 OK.

Failed 1 mesh checks.

End
"""

BASE_LOG_NEGATIVE = """Check mesh...
Mesh stats
    points:           1000
    cells:            500
Checking geometry...
    Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)
 ***High aspect ratio cells found, Max aspect ratio: 2.07741e+95, number of cells 25
 ***Zero or negative cell volume detected.  Minimum negative volume: -3.30275e-09, Number of negative volume cells: 23

Failed 10 mesh checks.

End
"""

CONTROL_PLANT_ASPECT = 4321.99
CONTROL_PLANT_CELLS = 777777


class ControlFailure(Exception):
    pass


def _write(directory, name, text):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def _parse_file(path):
    return parse_log(path, read_text(path))


def run_selftest(verbose=True):
    """Every control is driven in BOTH directions: the perturbation must be SEEN
    (FIRE) and its unperturbed twin must be UNCHANGED (STAY SILENT). A control
    driven only one way proves nothing -- a reader that reports the plant on every
    input passes a FIRE-only test and is worthless."""
    results = []
    workdir = tempfile.mkdtemp(prefix="mds1_selftest_")
    try:
        # ---- control 1: perturbed ASPECT value, `=` form ----------------------
        silent = _parse_file(_write(workdir, "c1_silent.log.checkMesh", BASE_LOG_EQ))
        fired = _parse_file(_write(
            workdir, "c1_fired.log.checkMesh",
            BASE_LOG_EQ.replace("805.199", repr(CONTROL_PLANT_ASPECT))))
        ok_silent = silent["max_aspect_ratio"] == 805.199
        ok_fired = fired["max_aspect_ratio"] == CONTROL_PLANT_ASPECT
        results.append(("C1 aspect value (= form)", ok_silent, ok_fired,
                        "silent=%r fired=%r" % (silent["max_aspect_ratio"], fired["max_aspect_ratio"])))

        # ---- control 2: perturbed CELL COUNT -----------------------------------
        silent2 = _parse_file(_write(workdir, "c2_silent.log.checkMesh", BASE_LOG_EQ))
        fired2 = _parse_file(_write(
            workdir, "c2_fired.log.checkMesh",
            BASE_LOG_EQ.replace("23040", str(CONTROL_PLANT_CELLS))))
        ok_silent2 = silent2["cells"] == 23040
        ok_fired2 = fired2["cells"] == CONTROL_PLANT_CELLS
        results.append(("C2 cell count", ok_silent2, ok_fired2,
                        "silent=%r fired=%r" % (silent2["cells"], fired2["cells"])))

        # ---- control 3: REMOVED LOG -- the enumerator must lose exactly one ----
        pool = os.path.join(workdir, "pool")
        os.makedirs(pool, exist_ok=True)
        _write(pool, "log.checkMesh", BASE_LOG_EQ)            # shape 1
        victim = _write(pool, "rung6b.log.checkMesh", BASE_LOG_COLON)  # shape 2
        before, _ = enumerate_logs([pool])
        os.remove(victim)
        after, _ = enumerate_logs([pool])
        ok_silent3 = len(before) == 2
        ok_fired3 = len(after) == 1 and victim not in after
        results.append(("C3 removed log (both filename shapes enumerated)", ok_silent3, ok_fired3,
                        "before=%d after=%d" % (len(before), len(after))))

        # ---- control 4: the `:` LABEL FORM must be read as a non-null value ----
        colon = _parse_file(_write(workdir, "c4_colon.log.checkMesh", BASE_LOG_COLON))
        equals = _parse_file(_write(workdir, "c4_equals.log.checkMesh", BASE_LOG_EQ))
        ok_silent4 = (equals["aspect_form"] == ASPECT_EQ and equals["aspect_ratio_flagged"] is False)
        ok_fired4 = (colon["aspect_form"] == ASPECT_COLON
                     and colon["max_aspect_ratio"] == 2842.46
                     and colon["aspect_ratio_flagged"] is True)
        results.append(("C4 `:` label form read non-null", ok_silent4, ok_fired4,
                        "colon=%r flagged=%r equals_form=%r"
                        % (colon["max_aspect_ratio"], colon["aspect_ratio_flagged"], equals["aspect_form"])))

        # ---- control 5: NON-POSITIVE MINIMUM VOLUME is reported, never dropped --
        neg = _parse_file(_write(workdir, "c5_negative.log.checkMesh", BASE_LOG_NEGATIVE))
        pos = _parse_file(_write(workdir, "c5_positive.log.checkMesh", BASE_LOG_EQ))
        ok_silent5 = (pos["volume_status"] == VOL_OK
                      and pos["cell_volume_ratio"] is not None
                      and abs(pos["cell_volume_ratio"] - 41.8474 / 1.30653e-09) < 1.0)
        ok_fired5 = (neg["volume_status"] == VOL_NEGATIVE
                     and neg["cell_volume_ratio"] is None
                     and neg["minimum_negative_volume"] == -3.30275e-09
                     and neg["negative_volume_cells"] == 23
                     and neg["max_aspect_ratio"] == 2.07741e+95)
        results.append(("C5 non-positive min volume reported, not dropped", ok_silent5, ok_fired5,
                        "status=%r ratio=%r negvol=%r"
                        % (neg["volume_status"], neg["cell_volume_ratio"], neg["minimum_negative_volume"])))

        # ---- control 6: QUARANTINE prune -- F5b is counted and never opened -----
        qroot = os.path.join(workdir, "qroot")
        qdir = os.path.join(qroot, "verification", "runs", "F5b_runs", "level1")
        os.makedirs(qdir, exist_ok=True)
        _write(qdir, "log.checkMesh", BASE_LOG_EQ)
        odir = os.path.join(qroot, "verification", "runs", "OTHER_runs")
        os.makedirs(odir, exist_ok=True)
        _write(odir, "log.checkMesh", BASE_LOG_EQ)
        qkept, qpruned = enumerate_logs([qroot])
        ok_silent6 = len(qkept) == 1 and QUARANTINE_MARKER not in os.path.abspath(qkept[0])
        ok_fired6 = qpruned == 1
        results.append(("C6 F5b_runs pruned and counted, never opened", ok_silent6, ok_fired6,
                        "kept=%d pruned=%d" % (len(qkept), qpruned)))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    if verbose:
        print("MDS-1 CONTROLS (%s)" % VERSION)
        print("  each control driven BOTH ways: perturbation must FIRE, twin must STAY SILENT")
        for name, s_ok, f_ok, detail in results:
            print("  %-52s  silent:%-5s fire:%-5s  %s"
                  % (name, "OK" if s_ok else "BAD", "OK" if f_ok else "BAD", detail))
    bad = [r for r in results if not (r[1] and r[2])]
    if bad:
        refuse("%d control(s) did not behave; the reader is not entitled to report a "
               "distribution" % len(bad),
               "; ".join(r[0] for r in bad))
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DEFAULT_REPO_ROOT = "/home/ubuntu/Certonomous"
DEFAULT_OUTSIDE_ROOTS = ["/home/ubuntu/certonomous-runs", "/home/ubuntu/closure-data"]


def classify(path, repo_root):
    ap = os.path.abspath(path)
    if ap.startswith(os.path.abspath(repo_root) + os.sep):
        rel = os.path.relpath(ap, os.path.abspath(repo_root))
        return "repo:" + rel.split(os.sep)[0]
    return "outside-repo:" + os.path.abspath(path).split(os.sep)[3]


def main(argv):
    guard_optimised_interpreter()
    asserts = guard_no_assert_statements()

    parser = argparse.ArgumentParser(description="MDS-1 mesh dimension survey reader")
    parser.add_argument("--selftest", action="store_true",
                        help="drive the planted controls and exit")
    parser.add_argument("--repo-root", default=DEFAULT_REPO_ROOT)
    parser.add_argument("--outside-root", action="append", default=None,
                        help="read-only corpus root outside the repository")
    parser.add_argument("--out", default=None, help="write the survey JSON here")
    args = parser.parse_args(argv[1:])

    if args.selftest:
        run_selftest()
        print("ast.Assert nodes in this file: %d (required 0)" % asserts)
        print("ALL CONTROLS BEHAVED. The reader is entitled to report a distribution.")
        return 0

    # Controls are driven on EVERY survey run, not only under --selftest: a
    # distribution collected by a reader that was not shown able to see a
    # non-zero is not evidence (standing rule 3).
    run_selftest(verbose=False)

    outside = DEFAULT_OUTSIDE_ROOTS if args.outside_root is None else args.outside_root
    roots = [args.repo_root] + list(outside)
    paths, pruned = enumerate_logs(roots)
    require(paths, "enumerator returned ZERO logs -- refusing to report an empty "
                   "distribution as a survey", " ".join(roots))

    records = []
    for path in paths:
        records.append(parse_log(path, read_text(path)))

    by_class = {}
    for r in records:
        by_class.setdefault(classify(r["path"], args.repo_root), 0)
        by_class[classify(r["path"], args.repo_root)] += 1

    survey = {
        "reader": VERSION,
        "collected": "2026-08-27",
        "verdict_words_issued": "none -- §11 sets no threshold and this is a survey, not a gate",
        "enumerator_command": ENUMERATOR_COMMAND,
        "filename_shapes_covered": list(NAME_SHAPES),
        "exclusions": EXCLUSION_NOTE,
        "roots": [os.path.abspath(p) for p in roots],
        "outside_repo_roots_are_read_only": True,
        "ast_assert_nodes_in_reader": asserts,
        "logs_enumerated": len(paths),
        "f5b_quarantine_logs_pruned": pruned,
        "logs_by_class": dict(sorted(by_class.items())),
        "aspect_label_census": {
            ASPECT_EQ: sum(1 for r in records if r["aspect_form"] == ASPECT_EQ),
            ASPECT_COLON: sum(1 for r in records if r["aspect_form"] == ASPECT_COLON),
            ASPECT_ABSENT: sum(1 for r in records if r["aspect_form"] == ASPECT_ABSENT),
        },
        "volume_status_census": {
            status: sum(1 for r in records if r["volume_status"] == status)
            for status in (VOL_OK, VOL_NEGATIVE, VOL_ZERO, VOL_ABSENT)
        },
        "logs_with_negative_minimum_volume": [
            {"path": r["path"],
             "minimum_negative_volume": r["minimum_negative_volume"],
             "negative_volume_cells": r["negative_volume_cells"],
             "max_aspect_ratio": r["max_aspect_ratio"],
             "checkMesh_verdict": r["checkMesh_verdict"]}
            for r in records if r["volume_status"] == VOL_NEGATIVE
        ],
        "logs_with_no_aspect_field": [r["path"] for r in records if r["aspect_form"] == ASPECT_ABSENT],
        "distribution": build_distribution(records),
        "records": records,
    }

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "MDS1_SURVEY.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(survey, handle, indent=1, sort_keys=False)
        handle.write("\n")

    d = survey["distribution"]
    print("MDS-1 SURVEY -- %s" % VERSION)
    print("  enumerator: %s" % ENUMERATOR_COMMAND)
    print("  logs enumerated: %d   F5b quarantine pruned (never opened): %d"
          % (len(paths), pruned))
    print("  aspect label census: %s" % survey["aspect_label_census"])
    print("  volume status census: %s" % survey["volume_status_census"])
    for key in ("all", "two_d", "three_d", "directions_unknown"):
        b = d[key]
        print("  -- %s: %d logs" % (b["label"], b["logs"]))
        print("     aspect  n=%d %s" % (b["aspect"]["summary"].get("n", 0), b["aspect"]["summary"]))
        print("     ratio   n=%d excluded=%d %s"
              % (b["cell_volume_ratio"]["summary"].get("n", 0),
                 b["cell_volume_ratio"]["excluded_from_percentiles"],
                 b["cell_volume_ratio"]["summary"]))
    print("  NO THRESHOLD IS PROPOSED. Collecting the survey and setting a gate are")
    print("  different acts; only the first is authorised here (§11.2, §11.5).")
    print("  written: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
