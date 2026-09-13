#!/usr/bin/env python3
# ===========================================================================
# d6r2c_fm6_init.py -- THE ONE REGISTERED CHANGE OF ARM FM6
# ===========================================================================
#
# Registered by PREREGISTRATION_AFTER_ITEM9_R2.md sections 2 and 11, and IN THE
# SAME COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# WHAT IT DOES, IN ONE SENTENCE.  It replaces the fresh-mesh case's freestream
# initial condition with O_mp's CONVERGED FIELDS AT THE SAME DESIGN POINT,
# transferred CELL-FOR-CELL BY INDEX, and refuses if the premise of that index
# transfer does not hold.
#
# WHY AN INDEX TRANSFER AND NOT A MAP.  MEASURED, not assumed: faces.gz,
# owner.gz, neighbour.gz and boundary are BYTE-IDENTICAL across all three
# meshes -- the base, the fresh extrusion, and the warped mesh O_mp ran:
#     faces.gz      0a94bba01e37c8587676b056c7a2bb05
#     owner.gz      16febaf5dfa4137ef7fb1ec4a3659ec5
#     neighbour.gz  803a7546fd09fcbd673ef1ed52b4fcd6
#     boundary      c8d1891562dc7a1d5822cd6b94c2c2d4
# Only points.gz differs.  Same topology, different geometry.  Cell index i is
# therefore the SAME STRUCTURED CELL in all three, and the transfer carries NO
# INTERPOLATION ERROR AT ALL -- it removes an error term instead of disclosing
# one.  THE PREMISE IS ASSERTED HERE AND THIS FILE REFUSES (exit 2) IF IT FAILS;
# it is never assumed from the fact that the counts match.
#
# THIS FILE PRODUCES AN INITIAL CONDITION.  IT GRADES NOTHING.  Every threshold
# lives in d6r2c_fm6_grade.py, which reads what this file records and re-derives
# the checksums itself rather than trusting them.
#
# IT NEVER WRITES INTO O_mp.  O_mp is a GRADED run directory whose artefacts a
# closed verdict cites by path.  This file opens it READ-ONLY, and the planted
# control of --selftest runs on synthetic trees in a temporary directory.
#
# HONEST GAP, NAMED BEFORE IT IS DISCOVERED (registration section 11a): this
# file has never been executed against a real decomposed case.  What is driven
# at the freeze is --selftest, which exercises the reconstruction, the header
# rewrite, the internalField splice and every refusal path on synthetic inputs.
# ===========================================================================
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import re
import sys
import time

# ---------------------------------------------------------------------------
# THE REGISTERED CONSTANTS.  Each carries the sentence it was copied from.
# ---------------------------------------------------------------------------

# "faces.gz / owner.gz / neighbour.gz / boundary are byte-identical across all
#  three meshes" -- registration section 2a, the premise of the index transfer.
CONNECTIVITY_MD5 = {
    "faces.gz": "0a94bba01e37c8587676b056c7a2bb05",
    "owner.gz": "16febaf5dfa4137ef7fb1ec4a3659ec5",
    "neighbour.gz": "803a7546fd09fcbd673ef1ed52b4fcd6",
    "boundary": "c8d1891562dc7a1d5822cd6b94c2c2d4",
}
# "38,304 cells, 40,209 points" -- registration section 9a.
N_CELLS = 38304
# "the source is O_mp's F record n = 88, fail = 0, the converged primal at the
#  design point this arm solves" -- registration section 2b.
SOURCE_TIME = "1000"
SOURCE_RECORD_N = 88
EVALS_MD5 = "2c0b8143caad198cd2e21d8047986aa3"
# "the transfer set is exactly the volFields the destination case's own 0.orig
#  carries" -- registration section 2c.  MEASURED from 0.orig, never assumed:
# T U alphat nuTilda nut p.  phi is a surfaceScalarField and is NOT transferred.
EXPECTED_FIELDS = ("T", "U", "alphat", "nuTilda", "nut", "p")
# "the three conditions" -- PREREGISTRATION.md section 1.
RUN_DIRS = ("mp04", "mp05", "mp06")
RECORD = "d6r2c_fm6_init.json"
# "d6r2c_fm6_init.py plants PLANT = 1.234e-03 into a value it read back from
#  disk" -- registration section 7.
PLANT = 1.234e-03

# ---- ADDENDUM 3.  THE FM7 DEFECT AND THE TWO REFUSALS IT BUYS.
#
# FM7 transferred all six fields correctly into the UNDECOMPOSED 0/ -- readback
# 0.0 on every cell -- AND THE SOLVER NEVER SAW THEM.  DAFoam decomposes ONCE, at
# the DEFORM phase's prob.setup(), one phase before this one runs; at the solve
# phase processorN/ already exists and is what the solver reads.  The registration
# said "the transfer must happen before prob.setup()" and was right about the
# constraint and wrong about WHICH setup().
#
# THE FLOOR WAS THEN IDENTICAL TO FM5's TO ALL TEN DIGITS, WHICH LOOKS EXACTLY
# LIKE A REFUTATION OF THE REGISTERED CHANGE AND IS NOT ONE.  You cannot refute a
# change that did not take effect.  Two refusals now make that impossible to
# misread, and NEITHER IS A GATE -- section 11a already registers this condition
# in words and these make a registered condition executable (2d.1, and the
# sibling registration's D5 is likewise "a refusal, not a gate").
#
#   REFUSAL 1, THE PRECONDITION, in phase init, BEFORE the solve: every
#   processorN/0/<field> is read back FROM DISK and compared against the slice of
#   the source it was built from.  Seconds, not 7.533 core-min.
#
#   REFUSAL 2, THE SECOND LINE, in phase verify, after the arm exits: if the
#   solve-phase residuals are BIT-IDENTICAL to FM5's, the transfer did not reach
#   the solver whatever phase init believed.  Both anchors come from runs the
#   next arm did not produce.
FM5_T100_P_RESIDUAL = 1.103361217e-03    # "p initRes: 0.001103361217" at Time = 100
FM5_FLOOR = 1.278377566e-05              # "Primal min residual 1.278377566e-05"


class Refusal(Exception):
    """Refuse, never degrade."""


def _md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _open(path):
    """Open <path> or <path>.gz, whichever exists.  OpenFOAM writes either."""
    if os.path.isfile(path):
        return open(path, "r", errors="replace")
    if os.path.isfile(path + ".gz"):
        return gzip.open(path + ".gz", "rt", errors="replace")
    raise Refusal("REFUSE_MISSING_FILE %s (and %s.gz)" % (path, path))


def _exists(path):
    return os.path.isfile(path) or os.path.isfile(path + ".gz")


# ---------------------------------------------------------------------------
# THE OPENFOAM FIELD FILE -- read the internalField, splice a new one in
# ---------------------------------------------------------------------------

_INT_RE = re.compile(r"^internalField\s+(uniform|nonuniform)\b", re.M)


def read_internal(text, n_expected=None):
    """Return (kind, values) where kind is 'scalar' or 'vector'.

    A uniform field is expanded to n_expected entries; a nonuniform one is read
    as written.  REFUSES on anything it does not recognise -- there is no
    default and no silent skip."""
    m = _INT_RE.search(text)
    if not m:
        raise Refusal("REFUSE_NO_INTERNALFIELD -- the file carries no "
                      "internalField entry this reader recognises")
    rest = text[m.end():]
    if m.group(1) == "uniform":
        body = rest[:rest.index(";")].strip()
        if body.startswith("("):
            vals = tuple(float(x) for x in body.strip("()").split())
            if len(vals) != 3:
                raise Refusal("REFUSE_UNIFORM_RANK uniform vector with %d "
                              "components" % len(vals))
            if n_expected is None:
                raise Refusal("REFUSE_UNIFORM_NO_COUNT cannot expand a uniform "
                              "field without the cell count")
            return "vector", [vals] * n_expected
        if n_expected is None:
            raise Refusal("REFUSE_UNIFORM_NO_COUNT cannot expand a uniform "
                          "field without the cell count")
        return "scalar", [float(body)] * n_expected
    # nonuniform: List<scalar> or List<vector>, then a count, then ( ... )
    head = rest[:rest.index("(")]
    kind = "vector" if "List<vector>" in head else (
        "scalar" if "List<scalar>" in head else None)
    if kind is None:
        raise Refusal("REFUSE_UNKNOWN_LIST %r -- this reader handles "
                      "List<scalar> and List<vector> and refuses the rest"
                      % head.strip()[:60])
    cnt = int(re.search(r"(\d+)\s*$", head.strip()).group(1))
    a = rest.index("(")
    depth = 0
    for i in range(a, len(rest)):
        if rest[i] == "(":
            depth += 1
        elif rest[i] == ")":
            depth -= 1
            if depth == 0:
                b = i
                break
    else:
        raise Refusal("REFUSE_UNBALANCED_LIST in internalField")
    inner = rest[a + 1:b]
    if kind == "scalar":
        vals = [float(x) for x in inner.split()]
    else:
        toks = [float(x) for x in inner.replace("(", " ").replace(")", " ").split()]
        vals = [tuple(toks[3 * k:3 * k + 3]) for k in range(len(toks) // 3)]
    if len(vals) != cnt:
        raise Refusal("REFUSE_LIST_COUNT header says %d, body carries %d"
                      % (cnt, len(vals)))
    return kind, vals


def splice_internal(text, kind, values):
    """Return `text` with its internalField replaced by `values`.

    EVERYTHING ELSE IS PRESERVED BYTE FOR BYTE -- and the boundaryField in
    particular.  The destination case's own boundary conditions are the case
    definition and this file does not touch them (registration section 2c)."""
    m = _INT_RE.search(text)
    if not m:
        raise Refusal("REFUSE_NO_INTERNALFIELD in the destination template")
    rest = text[m.end():]
    if m.group(1) == "uniform":
        end = m.end() + rest.index(";") + 1
    else:
        a = rest.index("(")
        depth = 0
        for i in range(a, len(rest)):
            if rest[i] == "(":
                depth += 1
            elif rest[i] == ")":
                depth -= 1
                if depth == 0:
                    break
        end = m.end() + rest.index(";", i) + 1
    if kind == "scalar":
        body = "\n".join("%.17g" % v for v in values)
        typ = "List<scalar>"
    else:
        body = "\n".join("(%.17g %.17g %.17g)" % v for v in values)
        typ = "List<vector>"
    new = "internalField   nonuniform %s\n%d\n(\n%s\n)\n;" % (typ, len(values), body)
    return text[:m.start()] + new + text[end:]


def read_labels(path):
    with _open(path) as fh:
        txt = fh.read()
    i = txt.index("// * * *")
    i = txt.index("\n", i)
    t = txt[i:]
    a = t.index("(")
    b = t.rindex(")")
    return [int(x) for x in t[a + 1:b].split()]


# ---------------------------------------------------------------------------
# THE RECONSTRUCTION -- what reconstructPar does for a volField's internal
# field, done in-process so it is testable without a container
# ---------------------------------------------------------------------------

def reconstruct_internal_from(mp_dir, field, time_dir, n_cells=N_CELLS):
    """reconstruct_internal against an arbitrary time directory.  Used by the
    round-trip identity control; the run path always uses SOURCE_TIME."""
    saved = globals()["SOURCE_TIME"]
    globals()["SOURCE_TIME"] = time_dir
    try:
        return reconstruct_internal(mp_dir, field, n_cells)[1]
    finally:
        globals()["SOURCE_TIME"] = saved


def reconstruct_internal(src_mp_dir, field, n_cells=N_CELLS):
    """Assemble the undecomposed internalField from the decomposed pieces, using
    each processor's own cellProcAddressing.

    REFUSES on a duplicate global index or a hole.  A partially filled field
    would be an initial condition nobody could describe."""
    procs = sorted(d for d in os.listdir(src_mp_dir)
                   if re.fullmatch(r"processor\d+", d))
    if not procs:
        raise Refusal("REFUSE_NO_PROCESSOR_DIRS in %s" % src_mp_dir)
    out = [None] * n_cells
    kind = None
    n_seen = 0
    for pd in procs:
        addr = read_labels(os.path.join(src_mp_dir, pd, "constant", "polyMesh",
                                        "cellProcAddressing"))
        fp = os.path.join(src_mp_dir, pd, SOURCE_TIME, field)
        with _open(fp) as fh:
            k, vals = read_internal(fh.read(), n_expected=len(addr))
        if kind is None:
            kind = k
        elif k != kind:
            raise Refusal("REFUSE_MIXED_RANK %s is %s on %s and %s elsewhere"
                          % (field, k, pd, kind))
        if len(vals) != len(addr):
            raise Refusal("REFUSE_ADDR_COUNT %s %s: %d values against %d "
                          "addressed cells" % (field, pd, len(vals), len(addr)))
        for k2, g in enumerate(addr):
            if not (0 <= g < n_cells):
                raise Refusal("REFUSE_ADDR_RANGE %s %s: global index %d outside "
                              "[0, %d)" % (field, pd, g, n_cells))
            if out[g] is not None:
                raise Refusal("REFUSE_ADDR_DUPLICATE %s: global cell %d written "
                              "twice -- the decomposition addressing is not a "
                              "partition" % (field, g))
            out[g] = vals[k2]
            n_seen += 1
    holes = [i for i, v in enumerate(out) if v is None]
    if holes:
        raise Refusal("REFUSE_ADDR_HOLE %s: %d of %d cells unwritten (first %r) "
                      "-- a partially filled initial field is not an initial "
                      "field" % (field, len(holes), n_cells, holes[:5]))
    if n_seen != n_cells:
        raise Refusal("REFUSE_ADDR_COUNT_TOTAL %s: %d writes for %d cells"
                      % (field, n_seen, n_cells))
    return kind, out


def distribute_internal(values, kind, mp_dir, field, n_cells=N_CELLS):
    """Write the undecomposed field back into each processorN/0/<field>.

    THE EXACT INVERSE of reconstruct_internal, through THE SAME
    cellProcAddressing.  No interpolation: cell g of the global array becomes
    local cell k of processor n, where addr[k] == g.

    THE TEMPLATE IS EACH PROCESSOR'S OWN 0/<field>, so its boundaryField -- which
    carries the inter-processor patches the undecomposed file does not have -- is
    preserved byte for byte.  Splicing a decomposed field into an undecomposed
    template would produce a file OpenFOAM cannot read.

    Returns a per-processor record and REFUSES if a read-back differs by
    anything at all."""
    procs = sorted(d for d in os.listdir(mp_dir)
                   if re.fullmatch(r"processor\d+", d))
    if not procs:
        raise Refusal(
            "REFUSE_NO_DESTINATION_PROCESSORS %s carries no processorN/ -- the "
            "solver reads the DECOMPOSED fields and there is nowhere to put them. "
            "This phase must run AFTER the decomposition exists (ADDENDUM 3)."
            % mp_dir)
    rows = {}
    for pd in procs:
        addr = read_labels(os.path.join(mp_dir, pd, "constant", "polyMesh",
                                        "cellProcAddressing"))
        for g in addr:
            if not (0 <= g < n_cells):
                raise Refusal("REFUSE_ADDR_RANGE %s %s: global index %d outside "
                              "[0, %d)" % (field, pd, g, n_cells))
        local = [values[g] for g in addr]
        base = os.path.join(mp_dir, pd, "0", field)
        if not _exists(base):
            raise Refusal("REFUSE_NO_PROC_TEMPLATE %s -- each processor's own "
                          "0/%s is the template, because it carries the "
                          "inter-processor boundary patches" % (base, field))
        with _open(base) as fh:
            tmpl = fh.read()
        k_t, _ = read_internal(tmpl, n_expected=len(addr))
        if k_t != kind:
            raise Refusal("REFUSE_PROC_RANK %s %s: template is %s, field is %s"
                          % (field, pd, k_t, kind))
        out = splice_internal(tmpl, kind, local)
        if os.path.isfile(base + ".gz"):
            os.remove(base + ".gz")      # exactly one file, never two
        with open(base, "w") as fh:
            fh.write(out)
        # REFUSAL 1: READ IT BACK FROM DISK.  A value this file believes it wrote
        # into the place the solver reads is not evidence that the solver will
        # read it.  FM7 is why this clause exists.
        with open(base) as fh:
            k_b, back = read_internal(fh.read(), n_expected=len(addr))
        if k_b != kind or len(back) != len(local):
            raise Refusal("REFUSE_PROC_READBACK_SHAPE %s %s: wrote %s x %d, read "
                          "%s x %d" % (field, pd, kind, len(local), k_b, len(back)))
        worst = 0.0
        for a, b in zip(local, back):
            worst = max(worst, abs(a - b) if kind == "scalar"
                        else max(abs(x - y) for x, y in zip(a, b)))
        if worst != 0.0:
            raise Refusal(
                "REFUSE_PROC_READBACK %s %s: the field read back from the place "
                "the solver reads differs from the field written, worst %.6e"
                % (field, pd, worst))
        rows[pd] = {"n_local": len(local), "readback_worst_abs_diff": worst,
                    "dest_md5": _md5_file(base),
                    "first_local": (local[0] if kind == "scalar" else list(local[0]))}
    return rows


# ---------------------------------------------------------------------------
# THE PREMISE -- asserted, never assumed
# ---------------------------------------------------------------------------

def assert_connectivity(polymesh_dir, tag):
    """The index transfer is only meaningful if the two meshes share cell
    ordering.  That is MEASURED here, by hash, on every run."""
    got = {}
    for name, want in CONNECTIVITY_MD5.items():
        p = os.path.join(polymesh_dir, name)
        if not os.path.isfile(p):
            raise Refusal("REFUSE_MISSING_CONNECTIVITY %s in %s (%s)"
                          % (name, polymesh_dir, tag))
        g = _md5_file(p)
        got[name] = g
        if g != want:
            raise Refusal(
                "REFUSE_CONNECTIVITY_MISMATCH %s %s\n  got  %s\n  want %s\n"
                "  THE INDEX TRANSFER'S PREMISE DOES NOT HOLD: cell i is not the "
                "same cell in both meshes, so a cell-for-cell copy would be "
                "meaningless.  This is refused, never degraded to an "
                "interpolation (registration section 2a)." % (tag, name, g, want))
    return got


# ---------------------------------------------------------------------------
# THE PHASE
# ---------------------------------------------------------------------------

def phase_init(arm_dir, omp_dir, evals, out_path, _plant=None):
    if os.geteuid() == 0:
        raise Refusal("REFUSE_ROOT this arm runs as ubuntu, never root "
                      "(Sanaa Launch item 6)")
    t0 = time.time()
    ev = os.path.join(omp_dir, "d6r2c_evals.jsonl")
    if os.path.isfile(ev):
        got = _md5_file(ev)
        if got != EVALS_MD5:
            raise Refusal("REFUSE_EVALS_MD5 got %s want %s -- the inherited "
                          "record is not the artefact this registration pinned"
                          % (got, EVALS_MD5))
    elif os.path.isfile(evals):
        got = _md5_file(evals)
        if got != EVALS_MD5:
            raise Refusal("REFUSE_EVALS_MD5 got %s want %s" % (got, EVALS_MD5))
    else:
        raise Refusal("REFUSE_NO_EVALS neither %s nor %s" % (ev, evals))

    # THE PREMISE, on the DESTINATION mesh -- the fresh extrusion.
    conn_dst = assert_connectivity(os.path.join(arm_dir, "constant", "polyMesh"),
                                   "fresh mesh (destination)")
    rec = {"kind": "FM6_INIT",
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "uid": os.getuid(), "gid": os.getgid(),
           "source": {"dir": omp_dir, "time": SOURCE_TIME,
                      "record_n": SOURCE_RECORD_N, "evals_md5": got},
           "connectivity_destination": conn_dst,
           "connectivity_registered": dict(CONNECTIVITY_MD5),
           "n_cells": N_CELLS,
           "transfer_set": list(EXPECTED_FIELDS),
           "conditions": {},
           "DEADLINE_IN_CONTAINER_S": "NONE"}

    for mp in RUN_DIRS:
        src = os.path.join(omp_dir, mp)
        dst = os.path.join(arm_dir, mp)
        if not os.path.isdir(src):
            raise Refusal("REFUSE_NO_SOURCE_CONDITION %s" % src)
        # THE PREMISE, on the SOURCE mesh -- the warped mesh O_mp ran.
        conn_src = assert_connectivity(os.path.join(src, "constant", "polyMesh"),
                                       "warped mesh %s (source)" % mp)
        orig = os.path.join(dst, "0.orig")
        if not os.path.isdir(orig):
            raise Refusal("REFUSE_NO_0ORIG %s -- the destination's own field set "
                          "is what defines the transfer set" % orig)
        present = tuple(sorted(f for f in os.listdir(orig)
                               if not f.startswith(".")))
        if present != tuple(sorted(EXPECTED_FIELDS)):
            raise Refusal(
                "REFUSE_FIELD_SET %s carries %r, registration section 2c "
                "registers %r -- the transfer set is MEASURED from 0.orig and a "
                "difference is a change to the case, not to this file"
                % (orig, present, tuple(sorted(EXPECTED_FIELDS))))
        rows = {}
        for f in EXPECTED_FIELDS:
            kind, vals = reconstruct_internal(src, f)
            if _plant == (mp, f):
                if kind == "scalar":
                    vals = list(vals)
                    vals[0] = vals[0] + PLANT
                else:
                    vals = list(vals)
                    vals[0] = (vals[0][0] + PLANT, vals[0][1], vals[0][2])
            # the destination's OWN 0.orig is the template: its boundaryField is
            # the case definition and is preserved byte for byte.
            with _open(os.path.join(orig, f)) as fh:
                tmpl = fh.read()
            out = splice_internal(tmpl, kind, vals)
            dp = os.path.join(dst, "0", f)
            if not os.path.isdir(os.path.dirname(dp)):
                os.makedirs(os.path.dirname(dp))
            for stale in (dp + ".gz",):
                if os.path.isfile(stale):
                    os.remove(stale)
            with open(dp, "w") as fh:
                fh.write(out)
            # READ IT BACK FROM DISK.  A value this file believes it wrote is not
            # evidence that the file on disk carries it.
            with open(dp) as fh:
                k2, back = read_internal(fh.read(), n_expected=N_CELLS)
            if k2 != kind or len(back) != len(vals):
                raise Refusal("REFUSE_READBACK_SHAPE %s/%s wrote %s x %d, read "
                              "%s x %d" % (mp, f, kind, len(vals), k2, len(back)))
            worst = 0.0
            for a, b in zip(vals, back):
                if kind == "scalar":
                    worst = max(worst, abs(a - b))
                else:
                    worst = max(worst, max(abs(x - y) for x, y in zip(a, b)))
            if worst != 0.0:
                raise Refusal("REFUSE_READBACK %s/%s: the field read back from "
                              "disk differs from the field written, worst %.6e"
                              % (mp, f, worst))
            # ---- AND NOW WHERE THE SOLVER ACTUALLY READS (ADDENDUM 3) --------
            # The undecomposed 0/ above is the reconstruction record.  THE
            # DECOMPOSED WRITE BELOW IS THE ONE THE SOLVER READS, and FM7 proved
            # that writing only the former changes nothing at all.
            procs = distribute_internal(vals, kind, dst, f)
            rows[f] = {"kind": kind, "n": len(vals),
                       "readback_worst_abs_diff": worst,
                       "dest_md5": _md5_file(dp),
                       "first_cell": (vals[0] if kind == "scalar" else list(vals[0])),
                       "sum_abs": sum(abs(v) if kind == "scalar"
                                      else abs(v[0]) + abs(v[1]) + abs(v[2])
                                      for v in vals),
                       "decomposed": procs,
                       "decomposed_cells": sum(p["n_local"] for p in procs.values()),
                       "decomposed_readback_worst": max(
                           p["readback_worst_abs_diff"] for p in procs.values())}
            if rows[f]["decomposed_cells"] != N_CELLS:
                raise Refusal(
                    "REFUSE_DECOMPOSED_COVERAGE %s/%s: the processors cover %d "
                    "cells, not %d -- the solver would read a partially written "
                    "field" % (mp, f, rows[f]["decomposed_cells"], N_CELLS))
        rec["conditions"][mp] = {"connectivity_source": conn_src, "fields": rows,
                                 "wrote_where_the_solver_reads":
                                     "mp/processorN/0/<field>, through the same "
                                     "cellProcAddressing (ADDENDUM 3)"}

    rec["wall_s"] = time.time() - t0
    with open(out_path, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    return 0


# ---------------------------------------------------------------------------
# REFUSAL 2 -- THE SECOND LINE OF DEFENCE, AFTER THE ARM EXITS
# ---------------------------------------------------------------------------

def solve_residuals(log_text):
    """The solve phase's pressure residual at Time = 100, and the reported floor.

    The log holds MORE THAN ONE solver run -- the deform phase's and the solve
    phase's.  The SOLVE phase is the LAST Time = 100 block, so the last match is
    taken and the earlier ones are ignored.  Returns (t100, floor), either None
    if the log does not carry it."""
    t100 = None
    at100 = False
    for ln in log_text.splitlines():
        if re.match(r"^Time = 100$", ln):
            at100 = True
            continue
        if at100:
            m = re.match(r"^p initRes: ([0-9.eE+-]+)", ln)
            if m:
                t100 = float(m.group(1))
                at100 = False
            elif re.match(r"^Time = ", ln):
                at100 = False
    floors = re.findall(r"Primal min residual ([0-9.eE+-]+)", log_text)
    return t100, (float(floors[-1]) if floors else None)


def phase_verify(log_path):
    """REFUSE (exit 2) if the solve-phase residuals are BIT-IDENTICAL to FM5's.

    FM5 started from freestream.  If this arm's trajectory matches it exactly,
    THE TRANSFER DID NOT REACH THE SOLVER, whatever phase init believed, and the
    floor that follows is NOT evidence about the registered change.

    NOT A GATE.  It writes no verdict and assigns no label; it makes executable a
    condition section 11a already registers in words (2d.1)."""
    if not os.path.isfile(log_path):
        raise Refusal("REFUSE_NO_LOG %s" % log_path)
    t100, floor = solve_residuals(open(log_path, errors="replace").read())
    out = {"t100_p_initRes": t100, "floor": floor,
           "FM5_T100_P_RESIDUAL": FM5_T100_P_RESIDUAL, "FM5_FLOOR": FM5_FLOOR}
    hits = []
    if t100 is not None and t100 == FM5_T100_P_RESIDUAL:
        hits.append("t=100 p initRes is BIT-IDENTICAL to FM5's %.12g" % FM5_T100_P_RESIDUAL)
    if floor is not None and floor == FM5_FLOOR:
        hits.append("the floor is BIT-IDENTICAL to FM5's %.12g" % FM5_FLOOR)
    out["matches_fm5"] = hits
    print("D6R2C_FM6_VERIFY t100=%r floor=%r matches_fm5=%d" % (t100, floor, len(hits)))
    if hits:
        raise Refusal(
            "REFUSE_FREESTREAM_TRAJECTORY the solve reproduced FM5 exactly:\n  "
            + "\n  ".join(hits)
            + "\n  FM5 STARTED FROM FREESTREAM.  An identical trajectory means an "
              "identical initial state, so the transfer did NOT reach the solver "
              "and the floor is NOT evidence about the registered change.\n"
              "  YOU CANNOT REFUTE A CHANGE THAT DID NOT TAKE EFFECT.\n"
              "  This is a PRODUCER DEFECT (section 11a): stopped, NOT A RESULT, "
              "repaired under VERIFICATION_CHARTER 2d.1.  No gate is added and no "
              "threshold is moved.")
    return 0


# ---------------------------------------------------------------------------
# SELFTEST -- pure logic only.  No container, no O_mp, no run directory.
# ---------------------------------------------------------------------------

def selftest():
    import shutil
    import tempfile
    ok = True
    n = 0

    def check(name, got, want):
        nonlocal ok, n
        n += 1
        if got != want:
            ok = False
            print("SELFTEST CONTROL FAILED: %s\n  got  %r\n  want %r"
                  % (name, got, want))

    HDR = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n"
           "    location \"%s\";\n    object %s;\n}\n"
           "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")

    def scal(vals, loc="1000", obj="p"):
        return (HDR % ("volScalarField", loc, obj)
                + "internalField   nonuniform List<scalar>\n%d\n(\n%s\n)\n;\n\n"
                % (len(vals), "\n".join("%.17g" % v for v in vals))
                + "boundaryField\n{\n    wing { type zeroGradient; }\n}\n")

    def vec(vals, loc="1000", obj="U"):
        return (HDR % ("volVectorField", loc, obj)
                + "internalField   nonuniform List<vector>\n%d\n(\n%s\n)\n;\n\n"
                % (len(vals), "\n".join("(%.17g %.17g %.17g)" % v for v in vals))
                + "boundaryField\n{\n    wing { type fixedValue; value uniform (0 0 0); }\n}\n")

    tmp = tempfile.mkdtemp(prefix="d6r2c_fm6_init_selftest_")
    try:
        # ---- the reader, on every form it must accept, and one it must not ----
        k, v = read_internal(scal([1.0, 2.0, 3.0]))
        check("reader: nonuniform scalar", (k, v), ("scalar", [1.0, 2.0, 3.0]))
        k, v = read_internal(vec([(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]))
        check("reader: nonuniform vector",
              (k, v), ("vector", [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]))
        u = HDR % ("volScalarField", "0", "p") + "internalField   uniform 7.5;\n"
        check("reader: uniform scalar expands to the cell count",
              read_internal(u, n_expected=4), ("scalar", [7.5] * 4))
        uv = HDR % ("volVectorField", "0", "U") + "internalField   uniform (1 2 3);\n"
        check("reader: uniform vector expands",
              read_internal(uv, n_expected=2), ("vector", [(1.0, 2.0, 3.0)] * 2))
        try:
            read_internal(HDR % ("volScalarField", "0", "p") + "boundaryField { }\n")
            check("reader: no internalField -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("reader: no internalField -> REFUSE_NO_INTERNALFIELD",
                  str(e).startswith("REFUSE_NO_INTERNALFIELD"), True)
        try:
            bad = scal([1.0, 2.0, 3.0]).replace("\n3\n", "\n4\n", 1)
            read_internal(bad)
            check("reader: count mismatch -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("reader: header count != body count -> REFUSE_LIST_COUNT",
                  str(e).startswith("REFUSE_LIST_COUNT"), True)
        try:
            read_internal(HDR % ("surfaceScalarField", "1000", "phi")
                          + "internalField   nonuniform List<label>\n1\n(\n2\n)\n;\n")
            check("reader: List<label> -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("reader: an unhandled list type -> REFUSE_UNKNOWN_LIST",
                  str(e).startswith("REFUSE_UNKNOWN_LIST"), True)

        # ---- the splice preserves EVERYTHING but the internalField ----------
        tmpl = scal([9.0, 9.0, 9.0], loc="0", obj="p")
        out = splice_internal(tmpl, "scalar", [1.0, 2.0, 3.0])
        check("splice: the new values land", read_internal(out)[1], [1.0, 2.0, 3.0])
        check("splice: the boundaryField survives byte for byte",
              out[out.index("boundaryField"):], tmpl[tmpl.index("boundaryField"):])
        check("splice: the header survives byte for byte",
              out[:out.index("internalField")], tmpl[:tmpl.index("internalField")])
        outu = splice_internal(HDR % ("volScalarField", "0", "p")
                               + "internalField   uniform 0;\n\nboundaryField\n{\n}\n",
                               "scalar", [4.0, 5.0])
        check("splice: a UNIFORM template is replaced too",
              read_internal(outu)[1], [4.0, 5.0])

        # ---- the reconstruction, on a synthetic two-processor decomposition --
        # global cells 0..5; processor0 owns {4,0,2}, processor1 owns {1,5,3} --
        # deliberately NOT contiguous and NOT sorted, which is the whole reason
        # cellProcAddressing exists.
        def mk_src(root, addr0, addr1, v0, v1, field="p", body=scal):
            for pd, addr, vals in (("processor0", addr0, v0), ("processor1", addr1, v1)):
                pm = os.path.join(root, pd, "constant", "polyMesh")
                os.makedirs(pm, exist_ok=True)
                with open(os.path.join(pm, "cellProcAddressing"), "w") as fh:
                    fh.write(HDR % ("labelList", "constant/polyMesh",
                                    "cellProcAddressing")
                             + "%d\n(\n%s\n)\n" % (len(addr),
                                                   "\n".join(str(x) for x in addr)))
                td = os.path.join(root, pd, SOURCE_TIME)
                os.makedirs(td, exist_ok=True)
                with open(os.path.join(td, field), "w") as fh:
                    fh.write(body(vals))
            return root
        r = mk_src(tmp + "/s1", [4, 0, 2], [1, 5, 3],
                   [40.0, 0.0, 20.0], [10.0, 50.0, 30.0])
        k, v = reconstruct_internal(r, "p", n_cells=6)
        check("reconstruct: values land at their GLOBAL index",
              v, [0.0, 10.0, 20.0, 30.0, 40.0, 50.0])
        check("reconstruct: rank is carried", k, "scalar")
        r = mk_src(tmp + "/s2", [4, 0, 2], [1, 5, 3],
                   [(4.0, 0, 0), (0.0, 0, 0), (2.0, 0, 0)],
                   [(1.0, 0, 0), (5.0, 0, 0), (3.0, 0, 0)], field="U", body=vec)
        k, v = reconstruct_internal(r, "U", n_cells=6)
        check("reconstruct: vectors land at their GLOBAL index",
              [x[0] for x in v], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        # a duplicate global index must REFUSE, not overwrite
        r = mk_src(tmp + "/s3", [4, 0, 2], [1, 5, 2],
                   [40.0, 0.0, 20.0], [10.0, 50.0, 30.0])
        try:
            reconstruct_internal(r, "p", n_cells=6)
            check("reconstruct: duplicate index -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("reconstruct: duplicate global index -> REFUSE_ADDR_DUPLICATE",
                  str(e).startswith("REFUSE_ADDR_DUPLICATE"), True)
        # a hole must REFUSE, not pass a partially filled field
        r = mk_src(tmp + "/s4", [4, 0, 2], [1, 5, 3],
                   [40.0, 0.0, 20.0], [10.0, 50.0, 30.0])
        try:
            reconstruct_internal(r, "p", n_cells=8)
            check("reconstruct: a hole -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("reconstruct: an unwritten cell -> REFUSE_ADDR_HOLE",
                  str(e).startswith("REFUSE_ADDR_HOLE"), True)
        # an out-of-range index must REFUSE
        r = mk_src(tmp + "/s5", [4, 0, 2], [1, 5, 99],
                   [40.0, 0.0, 20.0], [10.0, 50.0, 30.0])
        try:
            reconstruct_internal(r, "p", n_cells=6)
            check("reconstruct: index out of range -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("reconstruct: a global index outside the mesh -> REFUSE_ADDR_RANGE",
                  str(e).startswith("REFUSE_ADDR_RANGE"), True)
        # addressing/value count disagreement must REFUSE
        r = mk_src(tmp + "/s6", [4, 0, 2], [1, 5, 3],
                   [40.0, 0.0], [10.0, 50.0, 30.0])
        try:
            reconstruct_internal(r, "p", n_cells=6)
            check("reconstruct: count disagreement -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("reconstruct: values != addressed cells -> REFUSE_ADDR_COUNT",
                  str(e).startswith("REFUSE_ADDR_COUNT"), True)

        # ---- the premise assertion, which is the point of the whole file -----
        pm = os.path.join(tmp, "pm")
        os.makedirs(pm, exist_ok=True)
        for name in CONNECTIVITY_MD5:
            with open(os.path.join(pm, name), "w") as fh:
                fh.write("not the registered bytes\n")
        try:
            assert_connectivity(pm, "synthetic")
            check("premise: wrong connectivity -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("premise: wrong connectivity -> REFUSE_CONNECTIVITY_MISMATCH",
                  str(e).startswith("REFUSE_CONNECTIVITY_MISMATCH"), True)
            check("premise: the refusal explains WHY an index copy is then void",
                  "cell i is not the same cell" in str(e), True)
        os.remove(os.path.join(pm, "faces.gz"))
        try:
            assert_connectivity(pm, "synthetic")
            check("premise: missing connectivity -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("premise: a missing connectivity file -> REFUSE_MISSING/MISMATCH",
                  str(e).split()[0] in ("REFUSE_MISSING_CONNECTIVITY",
                                        "REFUSE_CONNECTIVITY_MISMATCH"), True)
        # NEGATIVE CONTROL: the REAL fresh mesh must PASS, and this is the one
        # check in this selftest that is anchored OUTSIDE the instrument.
        real = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-"
                "decomposition-and-freshmesh/FM5/constant/polyMesh")
        if os.path.isdir(real):
            try:
                got = assert_connectivity(real, "the real fresh mesh")
                check("premise NEGATIVE: the REAL fresh mesh satisfies it",
                      got["faces.gz"], CONNECTIVITY_MD5["faces.gz"])
            except Refusal as e:
                check("premise NEGATIVE: the real fresh mesh must pass", str(e), "pass")
        else:
            print("  (note: the real fresh mesh is not on this box; the external "
                  "negative control did not run)")

        # ================= ADDENDUM 3: THE DISTRIBUTOR ======================
        # THE ROUND-TRIP IDENTITY.  reconstruct -> distribute -> reconstruct must
        # return the IDENTICAL array.  If that holds, the two maps are exact
        # inverses and the transfer carries no error at all.
        def mk_dst(root, addr0, addr1, seed, field="p", body=scal):
            for pd, addr in (("processor0", addr0), ("processor1", addr1)):
                pm = os.path.join(root, pd, "constant", "polyMesh")
                os.makedirs(pm, exist_ok=True)
                with open(os.path.join(pm, "cellProcAddressing"), "w") as fh:
                    fh.write(HDR % ("labelList", "constant/polyMesh",
                                    "cellProcAddressing")
                             + "%d\n(\n%s\n)\n" % (len(addr),
                                                   "\n".join(str(x) for x in addr)))
                td = os.path.join(root, pd, "0")
                os.makedirs(td, exist_ok=True)
                with open(os.path.join(td, field), "w") as fh:
                    fh.write(body([seed] * len(addr)))
            return root
        A0, A1 = [4, 0, 2], [1, 5, 3]
        GLOBAL = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
        d = mk_dst(tmp + "/d1", A0, A1, -1.0)
        procs = distribute_internal(GLOBAL, "scalar", d, "p", n_cells=6)
        check("distribute: every processor written", sorted(procs), ["processor0", "processor1"])
        check("distribute: read-back is EXACTLY zero",
              max(p["readback_worst_abs_diff"] for p in procs.values()), 0.0)
        check("distribute: the cells are covered exactly once",
              sum(p["n_local"] for p in procs.values()), 6)
        # THE ROUND TRIP
        back = reconstruct_internal_from(d, "p", "0", n_cells=6)
        check("ROUND TRIP: reconstruct(distribute(x)) == x", back, GLOBAL)
        # vectors too
        dv = mk_dst(tmp + "/d2", A0, A1, (-1.0, 0.0, 0.0), field="U", body=vec)
        GV = [(float(i), 0.0, 0.0) for i in range(6)]
        distribute_internal(GV, "vector", dv, "U", n_cells=6)
        check("ROUND TRIP: vectors survive it too",
              reconstruct_internal_from(dv, "U", "0", n_cells=6), GV)
        # the template that carries the processor boundary patches is PRESERVED
        with open(os.path.join(d, "processor0", "0", "p")) as fh:
            got = fh.read()
        check("distribute: the processor boundaryField survives byte for byte",
              got[got.index("boundaryField"):],
              scal([0.0])[scal([0.0]).index("boundaryField"):])
        # NO DESTINATION PROCESSORS -> refusal, not a silent undecomposed-only write
        os.makedirs(tmp + "/d3", exist_ok=True)
        try:
            distribute_internal(GLOBAL, "scalar", tmp + "/d3", "p", n_cells=6)
            check("distribute: no processorN -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("distribute: no processorN -> REFUSE_NO_DESTINATION_PROCESSORS",
                  str(e).startswith("REFUSE_NO_DESTINATION_PROCESSORS"), True)
        # a missing per-processor template -> refusal
        d4 = mk_dst(tmp + "/d4", A0, A1, -1.0)
        os.remove(os.path.join(d4, "processor1", "0", "p"))
        try:
            distribute_internal(GLOBAL, "scalar", d4, "p", n_cells=6)
            check("distribute: missing template -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("distribute: missing per-processor template -> REFUSE_NO_PROC_TEMPLATE",
                  str(e).startswith("REFUSE_NO_PROC_TEMPLATE"), True)

        # ================= ADDENDUM 3: REFUSAL 2, phase verify ==============
        # FM5's own numbers, and FM7's, which were bit-identical to them.
        FM5LOG = ("Time = 100\np initRes: 0.0003970258637 finalRes: 1 nIters: 3\n"
                  "Time = 200\nTime = 100\np initRes: 0.001103361217 finalRes: 1 nIters: 3\n"
                  "Time = 1000\nPrimal min residual 1.278377566e-05\n")
        lg = os.path.join(tmp, "fm5.log")
        open(lg, "w").write(FM5LOG)
        t100, floor = solve_residuals(FM5LOG)
        check("verify: the SOLVE phase's t=100 is taken, not the deform phase's",
              t100, FM5_T100_P_RESIDUAL)
        check("verify: the floor is read", floor, FM5_FLOOR)
        try:
            phase_verify(lg)
            check("verify: an FM5-identical trajectory -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("verify: FM5-identical -> REFUSE_FREESTREAM_TRAJECTORY",
                  str(e).startswith("REFUSE_FREESTREAM_TRAJECTORY"), True)
            check("verify: the refusal says you cannot refute a change that did not happen",
                  "CANNOT REFUTE A CHANGE THAT DID NOT TAKE EFFECT" in str(e), True)
        # NEGATIVE CONTROL: a trajectory that DIFFERS must NOT refuse.  Without
        # this the refusal could be unconditional and nobody would know.
        ok_log = FM5LOG.replace("0.001103361217", "0.000217409881") \
                       .replace("1.278377566e-05", "3.041122e-09")
        lg2 = os.path.join(tmp, "ok.log")
        open(lg2, "w").write(ok_log)
        try:
            check("verify NEGATIVE: a DIFFERENT trajectory does NOT refuse",
                  phase_verify(lg2), 0)
        except Refusal as e:
            check("verify NEGATIVE: must not refuse", str(e), "no refusal")
        # one ulp off each anchor must also NOT refuse -- the test is EQUALITY,
        # not proximity, so a genuinely different run is never blocked by it.
        one_ulp = FM5LOG.replace("1.278377566e-05",
                                 repr(math.nextafter(FM5_FLOOR, 1.0)))
        lg3 = os.path.join(tmp, "ulp.log")
        open(lg3, "w").write(one_ulp.replace("0.001103361217", "0.001103361218"))
        try:
            check("verify NEGATIVE: ONE ULP off both anchors does NOT refuse",
                  phase_verify(lg3), 0)
        except Refusal as e:
            check("verify NEGATIVE: one ulp must not refuse", str(e), "no refusal")
        try:
            phase_verify(os.path.join(tmp, "nosuch.log"))
            check("verify: a missing log -> refusal", "no refusal", "Refusal")
        except Refusal as e:
            check("verify: a missing log -> REFUSE_NO_LOG",
                  str(e).startswith("REFUSE_NO_LOG"), True)

        # ---- the planted control (rule 3), end to end on a synthetic tree ----
        # PLANT into a value read back from disk, and prove the reader SEES it.
        base = scal([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        k, v = read_internal(base)
        planted = splice_internal(base, k, [v[0] + PLANT] + v[1:])
        k2, v2 = read_internal(planted)
        check("plant: the reader sees a PLANT of 1.234e-03",
              abs((v2[0] - v[0]) - PLANT) < 1e-15, True)
        check("plant: and sees it in the first cell, not somewhere else",
              v2[1:], v[1:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("D6R2C_FM6_INIT SELFTEST %s n=%d" % ("PASS" if ok else "FAIL", n))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="FM6 phase init: transfer O_mp's converged fields at the same "
                    "design point onto the fresh mesh, cell-for-cell by index.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--phase", choices=("init", "verify"), default="init")
    ap.add_argument("--log", help="the arm log, for --phase verify")
    ap.add_argument("--arm-dir", default=os.getcwd())
    ap.add_argument("--omp-dir", default="/mnt/parent/O_mp")
    ap.add_argument("--evals", default="d6r2c_evals_final.jsonl")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    try:
        if a.phase == "verify":
            if not a.log:
                ap.error("--log is required for --phase verify")
            return phase_verify(a.log)
        return phase_init(a.arm_dir, a.omp_dir, a.evals,
                          os.path.join(a.arm_dir, RECORD))
    except Refusal as e:
        print("D6R2C_FM6_INIT REFUSED\n%s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
