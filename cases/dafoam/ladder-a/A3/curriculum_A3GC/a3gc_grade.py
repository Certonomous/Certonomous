#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A3GC COMPARATOR -- **FROZEN by the dafoam-supervisor, 2026-09-11.**

Grading path for `A3GC` -- the ONERA M6 PRIMAL grid-convergence triple
(L3=c2/N17, L2=c1/N33, L1=c0/N65), pre-registered at

    cases/dafoam/ladder-a/A3/curriculum_A3GC/PREREGISTRATION.md
    committed 085ab04ef9c7e5b18af5fad5a721040594274174 (523 lines, incl. AMENDMENT 1)

This file implements ONLY gates registered in that document.  No criterion here
was invented by the comparator; every threshold carries the section that fixed
it.  **This file IS the frozen grading path** (CLAUDE.md rule 2): the
dafoam-supervisor froze it 2026-09-11 and pinned its md5 into
PREREGISTRATION.md at the freeze commit.  It carried a `.DRAFT` suffix until
that moment and the suffix was dropped IN THE SAME ACT, because a `.DRAFT`
suffix on a frozen instrument misleads exactly as badly as a suffix-less
unfrozen one, only in the other direction.

**IT WAS FROZEN BEFORE ITS RUNNER EXISTED, DELIBERATELY AND IN THAT ORDER.**
The comparator is the SPECIFICATION and the runner conforms to it.  Freezing
first is the maximally credible order: it makes it impossible for the grader to
be shaped to whatever the solver happens to emit.

SUBMISSIONS PARKED (CLAUDE.md rule 7).  Nothing here sends anything anywhere.

=======================================================================
DESIGN LAW THIS FILE IS BOUND BY
=======================================================================

* **It refuses (exit 2) rather than degrades** (PREREG Sec.3 preamble;
  CLAUDE.md rule 4 closing clause).  Every reader that cannot establish what it
  was asked to establish calls `refuse()`.  There is no silent default, no
  `except: pass`, and no "0 because nothing was found".

* **A graded run root is EVIDENCE and is NEVER written into.**  Every plant,
  every reconstruct and every shock re-run happens in a COPY under a scratch
  directory, and the original is asserted byte-identical afterwards
  (`assert_unchanged()`).  `logs_A3/` in particular is read-only: it is the
  record of what ran (PREREG Sec.4.5).

* **Verdict vocabulary is fixed and closed** (CLAUDE.md rule 1):
  PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
  `VERDICTS` below is the whole vocabulary and `emit_verdict()` refuses any
  token outside it.

* **Planted-zero control** (CLAUDE.md rule 3; PREREG Sec.3.4).  Every reader in
  this file that can return a zero, an emptiness or a pass has a matching
  `plant_*` function that writes a KNOWN perturbation into a COPY of a real
  artifact OF THIS FAMILY'S OWN ON-DISK FORMAT and reads it back through the
  real path.  Sec.3.4 records why the format matters: a lane's reader tested for
  `constant/polyMesh/owner` and returned a false zero on every A3/M6 tree while
  correctly finding 7 cases elsewhere -- these meshes store `owner.gz`.  A
  reader shown able to see a non-zero SOMEWHERE is not shown able to see one IN
  THE CLASS BEING ASKED ABOUT.  Measured again by this lane 2026-09-11:
  /home/ubuntu/certonomous-runs/A3-onera-m6-transonic/constant/polyMesh/
  holds owner.gz, faces.gz, points.gz, neighbour.gz -- and a plain `boundary`.

=======================================================================
WHY THERE IS AN ADF/CGNS READER IN HERE
=======================================================================
PREREG Sec.3.1 limb 3 requires the three surfaces be compared AS POINT
COORDINATES read out of each CGNS, and forbids substituting an md5.  Measured
2026-09-11: the A3GC surfaces are **ADF-format CGNS**, not HDF5 --

    head -c 8 s_c3.cgns -> c0 a8 a3 a9 41 44 46 20   ("...ADF ")

-- so h5py would not help even if it were installed (it is not).  `cgns_utils`
lives only inside the pinned image and is not importable on the host (PREREG
Sec.2.2).  Rather than make the registered coordinate limb unrunnable, this file
carries a small pure-stdlib ADF reader.

**It is validated against the pre-registration's own measurements**, by a tool
path entirely different from the one that produced them (that lane used
`cgns_utils` inside the image; this reads the bytes).  Measured 2026-09-11 on
/home/ubuntu/certonomous-runs/A3GC-mesh-family-probe/ :

    file                        this reader   PREREG Sec.2.3
    m6_surfaceMesh_fine.cgns      101913         101913
    s_c1.cgns                      26001          26001
    s_c2.cgns                       6765           6765
    s_c3.cgns                       1827           1827

    bbox y-extent  c0/c1/c2  +-0.039426   PREREG Sec.2.4  +-0.039426
    bbox y-extent  c3        +-0.039320   PREREG Sec.2.4  +-0.039320

Four node counts and four bounding boxes reproduced exactly.  That is the
reader's own planted control in the identity direction, and `plant_cgns()` is
its control in the difference direction.
"""

import argparse
import ast
import filecmp
import glob
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time

# =====================================================================
# 0.  VERDICT VOCABULARY AND REFUSAL
# =====================================================================

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

EXIT_OK = 0
EXIT_VERDICT_NOT_PASS = 1
EXIT_REFUSE = 2


def refuse(code, msg):
    """Refuse rather than degrade.  PREREG Sec.3 preamble: every one of these
    refuses (exit 2) rather than degrades."""
    sys.stdout.flush()
    sys.stderr.write("\nREFUSE [%s]\n  %s\n" % (code, msg))
    sys.stderr.write("  exit 2 -- the comparator could not establish what it was "
                     "asked to establish.  This is NOT a verdict.\n")
    sys.stderr.flush()
    sys.exit(EXIT_REFUSE)


def emit_verdict(label, verdict, detail=""):
    if verdict not in VERDICTS:
        refuse("VOCAB", "verdict token %r is outside the fixed vocabulary %r "
                        "(CLAUDE.md rule 1)" % (verdict, list(VERDICTS)))
    print("  VERDICT  %-28s : %s%s" % (label, verdict, ("   -- " + detail) if detail else ""))
    return verdict


# ---------------------------------------------------------------------
# VERDICT SEVERITY -- TOTAL OVER THE WHOLE VOCABULARY.
#
# *** DEFECT B, FOUND BY THE dafoam-supervisor 2026-09-11 AND REPAIRED HERE. ***
# The composed line used to rank THREE of the six tokens:
#
#     order = ["NOT A RESULT", "GATE FAIL", "PASS"]
#     overall = sorted(verdicts.values(), key=lambda v: order.index(v))[0]
#
# `order.index(v)` raises ValueError on PENDING, GATE REACHED or BLOCKED -- a
# TRACEBACK, not a refusal -- and would silently mis-sort any token it did
# happen to find.  A comparator refuses cleanly or it is not a comparator (this
# file's own preamble; PREREG Sec.3: "every one of these refuses (exit 2) rather
# than degrades").  The order below is TOTAL over VERDICTS and worst-first.
#
# WHY THIS PRECEDENCE.  It is not a gate and it registers no threshold; it is
# the fixed vocabulary's own ordering, and each clause cites the rule that
# forces it:
#
#   NOT A RESULT  worst     standing rule 5 / PREREG Sec.4.2: "the gate can only
#                           turn a PASS or GATE FAIL INTO NOT A RESULT, never
#                           the reverse."  Nothing may outrank it.
#   GATE FAIL     next      CLAUDE.md rule 1: PENDING "is a display/queue state
#                           ... use it for 'not yet run', NEVER to soften a
#                           GATE FAIL."  So GATE FAIL must outrank BLOCKED and
#                           PENDING, or a queue state would soften a failure.
#   BLOCKED                 no graded evidence, because an obstruction was hit.
#   PENDING                 no graded evidence, because it has not yet run.
#                           Both outrank the graded-good tokens: an item cannot
#                           stand at PASS on a stage that produced no evidence.
#   GATE REACHED            a graded outcome short of a band statement.
#   PASS          best      the only token that means every graded gate passed.
VERDICT_SEVERITY = ("NOT A RESULT", "GATE FAIL", "BLOCKED", "PENDING",
                    "GATE REACHED", "PASS")


def compose_verdicts(items):
    """items: {gate label -> verdict token}.  Returns the WORST token present.

    Refuses (exit 2) rather than raising, on any of the three ways this can be
    asked something it cannot answer:
      * VERDICT_SEVERITY not a permutation of VERDICTS -- the ordering is not
        total, which is exactly the defect being repaired;
      * a token outside the fixed vocabulary -- `.index()` would raise;
      * an EMPTY item set -- a composition over nothing would return a vacuous
        PASS, which is a planted zero (CLAUDE.md rule 3).
    """
    if sorted(VERDICT_SEVERITY) != sorted(VERDICTS):
        refuse("COMPOSE", "VERDICT_SEVERITY %r is not a permutation of the fixed "
                          "vocabulary %r.  The composition ordering is not TOTAL "
                          "and would raise on a token it does not list "
                          "(CLAUDE.md rule 1)."
               % (list(VERDICT_SEVERITY), list(VERDICTS)))
    if not items:
        refuse("COMPOSE", "asked to compose an item verdict over ZERO gates.  An "
                          "empty composition would return the best token in the "
                          "vocabulary out of no evidence at all -- a zero from a "
                          "reader not shown able to see a non-zero (CLAUDE.md "
                          "rule 3).")
    for lab in sorted(items):
        if items[lab] not in VERDICT_SEVERITY:
            refuse("COMPOSE", "gate %r carries verdict token %r, which is outside "
                              "the fixed vocabulary %r.  Refusing rather than "
                              "sorting it (CLAUDE.md rule 1)."
                   % (lab, items[lab], list(VERDICTS)))
    return min(items.values(), key=VERDICT_SEVERITY.index)


# =====================================================================
# 1.  REGISTERED CONSTANTS -- every one cites the section that fixed it
# =====================================================================

PREREG_PATH = "cases/dafoam/ladder-a/A3/curriculum_A3GC/PREREGISTRATION.md"
PREREG_COMMIT = "085ab04ef9c7e5b18af5fad5a721040594274174"

# --- Sec.2.5: the three levels.  Departure from these counts is launch-blocking.
LEVELS = ("L3", "L2", "L1")                      # coarse -> fine
REG_CELLS = {"L3": 99840, "L2": 798720, "L1": 6389760}
REG_SURFACE_FACES = {"L3": 6240, "L2": 24960, "L1": 99840}
REG_N_LAYERS = {"L3": 17, "L2": 33, "L1": 65}
REG_SURFACE_TAG = {"L3": "c2", "L2": "c1", "L1": "c0"}

# --- Sec.3.1: G-SYS
REG_CELL_RATIO = 8.000
REG_CELL_RATIO_TOL = 0.001
REG_FACE_RATIO = 4                               # "exactly 4"
REG_ROOT_CHORD = 0.8059                          # logs_A3/extract_cp.py c_root
REG_BBOX_TOL = 1.0e-5 * REG_ROOT_CHORD           # "1e-5 of root chord" = 8.059e-6
REG_TE_REL_TOL = 0.01                            # "agrees ... to 1 %"

# --- Sec.3.5 / N-D43: the accept floor is the PRODUCT.
REG_PRIMAL_MIN_RES_TOL = 1.0e-08
REG_PRIMAL_MIN_RES_TOL_DIFF = 100.0
REG_ACCEPT_FLOOR = REG_PRIMAL_MIN_RES_TOL * REG_PRIMAL_MIN_RES_TOL_DIFF   # 1e-06

# --- Sec.3.6 / N-D44: initial residuals only.  `finalRes` is never read.
REG_INITRES_EQNS = ("U0", "U1", "U2", "he", "p", "nuTilda")
REG_INITRES_MAX = 1.0e-06
# AMENDMENT 1(b) item 3: a tighter floor reported as a DIAGNOSTIC, never graded.
REG_DIAGNOSTIC_FLOOR = 1.0e-07

# --- AMENDMENT 1(a): G-PLAT
REG_PLAT_WINDOW = 10                             # last 10 printed samples
REG_PLAT_MARGIN = 10.0                           # "at least ten times smaller"
REG_PLAT_FUNCTIONALS = ("CD", "CL")

# --- Sec.4.3: bands
REG_P_BAND = (1.0, 3.0)
REG_GCI_BAND = {"CD": 0.030, "CL": 0.025}        # PASS bands (3.0 %, 2.5 %)
REG_GCI_PREDICTED = {"CD": 0.020, "CL": 0.015}   # predictions, reported not gated
REG_FS = 1.25
REG_R = 2.0                                      # Sec.2.5: r = 2 exactly

# --- Sec.4.1: anchor (NOT a member of the family -- c2 with N=65)
ANCHOR_CD = 0.0229956
ANCHOR_CL = 0.3131159

# --- Sec.4.5: shock predictions P1-P4
REG_SHOCK_STATIONS = (0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99)
REG_P1_STATIONS = (0.80, 0.90)
REG_P1_PASS_PCT = 0.40                           # >= +40 % slope on L1 vs L3
REG_P1_FALSIFY_PCT = 0.15                        # < +15 % at BOTH -> falsified
REG_P2_MEAN_ABS_DROP = 0.30                      # mean |dx/c| falls >= 30 %
REG_P2_ETA20_PASS = 0.060                        # eta=0.20 error below +0.060 c
REG_P2_ETA20_FALSIFY = 0.085                     # stays above +0.085 c -> falsified
REG_P3_PASS_RMS = 0.055
REG_P3_FALSIFY_RMS = 0.070
REG_BASELINE_POOLED_RMS = 0.0575                 # Sec.4.5, measured on 399,360 cells

# --- AMENDMENT 3(a): each prediction's own token.  Sec.4.5 gives every
#     prediction TWO thresholds -- a PASS condition and a separate, lower
#     FALSIFICATION condition -- and named no token for either.  Registered:
#       PASS         the registered Sec.4.5 PASS condition holds
#       GATE FAIL    the registered Sec.4.5 FALSIFICATION condition holds
#       NOT A RESULT the MIDDLE BAND between them, "because a registration that
#                    supplies two thresholds has by construction declared the
#                    space between them evidence for neither"
#     DIRECTION NOTE (AMENDMENT 3(a), and it would otherwise be a trap): the
#     falsification condition points DOWNWARD for P1 (a small increase falsifies)
#     and UPWARD for P2 and P3 (a large error falsifies).  Each is therefore
#     tested AS Sec.4.5 WORDS IT below, and no boundary is restated in a
#     direction-neutral form that would silently move it.
#
# --- AMENDMENT 3(b): P4's "all fail" means ALL THREE FALSIFIED, the STRONG
#     form.  A counter-hypothesis is ADOPTED on strong evidence, never on mere
#     non-confirmation; and the strong form is the CONSERVATIVE direction --
#     it makes P4 HARDER to fire.
REG_P4_REQUIRES_ALL_FALSIFIED = True


def prediction_token(passed, falsified):
    """AMENDMENT 3(a).  One prediction's token from its two registered conditions.

    Refuses on the impossible corner rather than picking a winner: a prediction
    cannot simultaneously meet its PASS condition and its FALSIFICATION
    condition, and if the arithmetic ever says both, the comparator has a defect
    and must not render a verdict out of it.
    """
    if passed and falsified:
        refuse("SHOCK", "a prediction reported BOTH its Sec.4.5 PASS condition and "
                        "its Sec.4.5 FALSIFICATION condition.  Those are disjoint by "
                        "construction; the comparator will not choose between them.")
    if passed:
        return "PASS"
    if falsified:
        return "GATE FAIL"
    return "NOT A RESULT"

# --- Sec.3.4: the planted perturbation.  A distinctive value no mesh or log
#     could carry by accident.
PLANT = 1.234e-03
PLANT_CELLS = 1234567
PLANT_FACES = 4321


# =====================================================================
# 2.  EVIDENCE PROTECTION -- a graded run root is never written into
# =====================================================================

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Untouched(object):
    """Context manager.  Records sha256 of every named original on entry and
    asserts every one byte-identical on exit.  Wrap ANY operation that copies,
    plants into, or re-runs against a graded artifact."""

    def __init__(self, paths, label):
        self.paths = [p for p in paths if os.path.isfile(p)]
        self.label = label
        self.before = {}

    def __enter__(self):
        for p in self.paths:
            self.before[p] = (sha256_file(p), os.path.getsize(p))
        return self

    def __exit__(self, *exc):
        for p, (h, n) in self.before.items():
            if not os.path.isfile(p):
                refuse("EVIDENCE", "%s: original vanished during %s: %s" % (p, self.label, p))
            h2, n2 = sha256_file(p), os.path.getsize(p)
            if (h2, n2) != (h, n):
                refuse("EVIDENCE",
                       "%s was MODIFIED during %s.\n  before sha256=%s size=%d"
                       "\n  after  sha256=%s size=%d\n"
                       "  A graded run root is evidence and is never written into."
                       % (p, self.label, h, n, h2, n2))
        return False


def copy_tree_readonly_source(src, dst, label):
    """Copy a directory to scratch and assert the SOURCE unchanged afterwards."""
    if not os.path.isdir(src):
        refuse("EVIDENCE", "%s: source directory does not exist: %s" % (label, src))
    originals = []
    for root, _dirs, files in os.walk(src):
        for f in files:
            originals.append(os.path.join(root, f))
    with Untouched(originals, "copy of " + label):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst, symlinks=True)
    return dst


# =====================================================================
# 3.  READERS
# =====================================================================
# Every reader below has a matching plant_* control in section 6.

def _open_maybe_gz(path_base, what):
    """These meshes store owner.gz, not owner (PREREG Sec.3.4).  Try BOTH, and
    say which one was read -- a reader that silently tries only one is the
    reader that produced the false zero Sec.3.4 records."""
    for cand, opener in ((path_base, open), (path_base + ".gz", gzip.open)):
        if os.path.isfile(cand):
            return cand, opener(cand, "rb")
    refuse("READ", "%s: neither %s nor %s.gz exists.  (PREREG Sec.3.4: this "
                   "family stores .gz -- a reader that checks only the plain "
                   "name returns a FALSE ZERO here.)" % (what, path_base, path_base))


# ---------------------------------------------------------------- polyMesh

_NOTE_RE = re.compile(rb"nCells\s*:\s*(\d+)")
_NPOINTS_RE = re.compile(rb"nPoints\s*:\s*(\d+)")
_NFACES_RE = re.compile(rb"nFaces\s*:\s*(\d+)")


def read_cell_count(case_root):
    """nCells from constant/polyMesh/owner{,.gz}'s FoamFile `note` line."""
    base = os.path.join(case_root, "constant", "polyMesh", "owner")
    which, fh = _open_maybe_gz(base, "cell count")
    try:
        head = fh.read(4096)
    finally:
        fh.close()
    m = _NOTE_RE.search(head)
    if not m:
        refuse("READ", "%s: no `nCells:` in the FoamFile note of %s.  Refusing "
                       "rather than reporting 0." % (case_root, which))
    return int(m.group(1)), which


def read_patches(case_root):
    """{patch: (type, nFaces)} from constant/polyMesh/boundary{,.gz}."""
    base = os.path.join(case_root, "constant", "polyMesh", "boundary")
    which, fh = _open_maybe_gz(base, "patch table")
    try:
        txt = fh.read().decode("utf-8", "replace")
    finally:
        fh.close()
    # strip the FoamFile header block, then walk `name { ... }` entries
    body = txt
    i = body.find("FoamFile")
    if i >= 0:
        j = body.find("}", body.find("{", i))
        body = body[j + 1:]
    patches = {}
    for m in re.finditer(r"^\s*([A-Za-z_][\w.]*)\s*\n\s*\{(.*?)\n\s*\}", body,
                         re.S | re.M):
        name, blk = m.group(1), m.group(2)
        tm = re.search(r"\btype\s+([\w.]+)\s*;", blk)
        fm = re.search(r"\bnFaces\s+(\d+)\s*;", blk)
        if tm and fm:
            patches[name] = (tm.group(1), int(fm.group(1)))
    if not patches:
        refuse("READ", "%s: parsed ZERO patches out of %s.  A zero patch count "
                       "is never reported as a measurement (CLAUDE.md rule 3)."
               % (case_root, which))
    return patches, which


# ---------------------------------------------------------------- ADF / CGNS

class ADF(object):
    """Minimal read-only ADF (CGNS legacy binary) reader -- stdlib only.

    Node record, measured byte-for-byte on s_c3.cgns 2026-09-11:
        'NoDe' | name[32] | label[32] | nsub[8h] | lsub[8h] | subptr[12h]
              | dtype[32] | ndim[2h] | dims[12*8h] | nchunk[4h] | dptr[12h] | 'TaiL'
    Sub-node table: 'SNTb' | endptr[12h] | (name[32] | ptr[12h])*lsub | 'snTE'
    Data chunk:     'DaTa' | endptr[12h] | <raw> | 'EndC'
    Disk pointer:   block[8h] * BLOCKSIZE + offset[4h];  offset == BLOCKSIZE is NULL.
    Endianness/sizes are declared in the file header ('AdF2LB' = little-endian).
    """

    BLOCK = 4096

    def __init__(self, path):
        self.path = path
        with open(path, "rb") as fh:
            self.b = fh.read()
        if self.b[:8] != b"\xc0\xa8\xa3\xa9ADF ":
            refuse("CGNS", "%s: not an ADF-format CGNS file (magic %r).  This "
                           "reader handles the format this family actually uses; "
                           "it refuses rather than guess." % (path, self.b[:8]))
        if b"AdF2LB" not in self.b[:128]:
            refuse("CGNS", "%s: ADF header does not declare little-endian (LB). "
                           "Refusing rather than misread every float." % path)

    def _ptr(self, raw):
        s = raw.decode("ascii")
        blk, off = int(s[:8], 16), int(s[8:], 16)
        return None if off >= self.BLOCK else blk * self.BLOCK + off

    def node(self, o):
        b = self.b
        if b[o:o + 4] != b"NoDe":
            refuse("CGNS", "%s: expected NoDe tag at %d, found %r" % (self.path, o, b[o:o + 4]))
        p = o + 4
        name = b[p:p + 32].decode("ascii", "replace").rstrip(); p += 32
        label = b[p:p + 32].decode("ascii", "replace").rstrip(); p += 32
        nsub = int(b[p:p + 8], 16); p += 8
        lsub = int(b[p:p + 8], 16); p += 8
        subp = self._ptr(b[p:p + 12]); p += 12
        dt = b[p:p + 32].decode("ascii", "replace").rstrip(); p += 32
        ndim = int(b[p:p + 2], 16); p += 2
        dims = [int(b[p + 8 * i:p + 8 * i + 8], 16) for i in range(12)]; p += 96
        nchunk = int(b[p:p + 4], 16); p += 4
        dptr = self._ptr(b[p:p + 12]); p += 12
        if b[p:p + 4] != b"TaiL":
            refuse("CGNS", "%s: node at %d has no TaiL tag (found %r) -- the "
                           "record layout does not match; refusing."
                   % (self.path, o, b[p:p + 4]))
        return dict(name=name, label=label, nsub=nsub, lsub=lsub, subp=subp,
                    dt=dt, ndim=ndim, dims=dims[:ndim], nchunk=nchunk, dptr=dptr)

    def children(self, n):
        out = []
        if n["subp"] is None or n["nsub"] == 0:
            return out
        o = n["subp"]
        if self.b[o:o + 4] != b"SNTb":
            refuse("CGNS", "%s: sub-node table at %d has no SNTb tag" % (self.path, o))
        o += 16                                   # 'SNTb' + 12-hex end pointer
        for _ in range(n["lsub"]):
            nm = self.b[o:o + 32].decode("ascii", "replace").rstrip()
            cp = self._ptr(self.b[o + 32:o + 44])
            o += 44
            if cp is not None and not nm.startswith("unused"):
                out.append((nm, cp))
        return out

    def data(self, n):
        if n["dptr"] is None or n["nchunk"] == 0:
            return None
        o = n["dptr"]
        if self.b[o:o + 4] != b"DaTa":
            refuse("CGNS", "%s: data chunk at %d has no DaTa tag" % (self.path, o))
        o += 16                                   # 'DaTa' + 12-hex end pointer
        cnt = 1
        for d in n["dims"]:
            cnt *= d
        if n["dt"] == "R8":
            return struct.unpack("<%dd" % cnt, self.b[o:o + 8 * cnt])
        if n["dt"] == "R4":
            return struct.unpack("<%df" % cnt, self.b[o:o + 4 * cnt])
        if n["dt"] == "I4":
            return struct.unpack("<%di" % cnt, self.b[o:o + 4 * cnt])
        return None

    def zone_points(self):
        """[(x,y,z), ...] over every Zone_t/GridCoordinates_t in every base,
        in file order.  Refuses on an empty read."""
        root = self.node(self.b.find(b"NoDeADF MotherNode"))
        pts = []
        for _bn, bo in self.children(root):
            bn2 = self.node(bo)
            if bn2["label"] != "CGNSBase_t":
                continue
            for _zn, zo in self.children(bn2):
                z = self.node(zo)
                if z["label"] != "Zone_t":
                    continue
                for _gn, go in self.children(z):
                    g = self.node(go)
                    if g["label"] != "GridCoordinates_t":
                        continue
                    c = {}
                    for cn, co in self.children(g):
                        cd = self.node(co)
                        if cd["label"] == "DataArray_t":
                            c[cn] = self.data(cd)
                    need = ("CoordinateX", "CoordinateY", "CoordinateZ")
                    if not all(k in c and c[k] is not None for k in need):
                        refuse("CGNS", "%s: a GridCoordinates_t is missing one of "
                                       "%r -- refusing rather than dropping a zone"
                               % (self.path, need))
                    pts.extend(zip(c["CoordinateX"], c["CoordinateY"], c["CoordinateZ"]))
        if not pts:
            refuse("CGNS", "%s: read ZERO points.  A zero from a reader is not "
                           "evidence (CLAUDE.md rule 3)." % self.path)
        return pts


def read_surface_points(path):
    return ADF(path).zone_points()


def bbox(points):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]; zs = [p[2] for p in points]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def te_thickness(points, frac, z_halfband=0.01, aft_frac=1.0e-4):
    """Trailing-edge thickness at a span station, as the y-extent of the points
    lying in the aft `aft_frac` of local chord within a z band of half-width
    `z_halfband * span` about `frac * span`.

    *** DIAGNOSTIC ONLY.  THIS IS NOT A GATE. ***
    PREREG Sec.3.1 limb 5 fixed a 1 % cross-level tolerance on TE thickness but
    recorded NO measurement recipe, and none could be reconstructed.  AMENDMENT
    2(a) STRUCK it as a gate -- because it is UNMEASURABLE AS WRITTEN, NOT
    because it failed -- and replaced it with the strictly stronger `G-NEST`.
    The cause is structural: every window-based TE statistic is point-density
    dependent, and these levels differ 4x in point count by construction (the
    aft window holds n=1 on L3, giving exactly 0.0, against n=5 on L2 and n=9 on
    L1).  It fails even between the two FINEST levels, where no zero is
    involved: tip 2.974395e-03 on L2 against 2.917384e-03 on L1, a 1.9 % spread.
    Sec.2.4's own tip figure (~7.14e-04) is not reproduced by any recipe tried
    (~2.9e-03), so Sec.2.4's numbers came from a recipe that is not recorded and
    cannot be recovered.  This function is the comparator's stated definition,
    it is reported per level, and it never gates anything.
    """
    span = max(p[2] for p in points)
    if span <= 0:
        refuse("GEOM", "degenerate span")
    zc = frac * span
    band = [p for p in points if abs(p[2] - zc) <= z_halfband * span]
    if len(band) < 3:
        return None, 0                            # Sec.2.4's "(strip empty)"
    xte = max(p[0] for p in band)
    xle = min(p[0] for p in band)
    chord = xte - xle
    sel = [p for p in band if p[0] >= xte - aft_frac * chord]
    ys = [p[1] for p in sel]
    return (max(ys) - min(ys)), len(sel)


# ---------------------------------------------------------------- solver log

# Measured on cases/dafoam/ladder-a/logs_A3/run_model_run3.log 2026-09-11:
#   "CD: 0.0229954141918625 final: 0.0229954141918625"   (61 samples / 6000 iter)
#   "U0 initRes: 1.038238535669736e-07 finalRes: 1.000287445913249e-08 nIters: 2"
#   "ExecutionTime = 1221.21 s  ClockTime = 1233 s"      then "End"
_FUNC_RE = {f: re.compile(r"^%s:\s+([-+0-9.eEnaN]+)" % f, re.M) for f in ("CD", "CL")}
_INITRES_RE = re.compile(r"^(\w+)\s+initRes:\s+([-+0-9.eEnaN]+)\s+finalRes:", re.M)
_TIME_RE = re.compile(r"^Time = ([0-9.eE+-]+)\s*$", re.M)
_EXEC_RE = re.compile(r"^ExecutionTime = ([0-9.eE+-]+) s", re.M)
_PMR_RE = re.compile(r"Primal min residual\s+([0-9.eE+-]+)")
_DAOPT_RE = {
    "primalMinResTol": re.compile(r"^\s*primalMinResTol\s+([0-9.eE+-]+)\s*;", re.M),
    "primalMinResTolDiff": re.compile(r"^\s*primalMinResTolDiff\s+([0-9.eE+-]+)\s*;", re.M),
    "printInterval": re.compile(r"^\s*printInterval\s+([0-9]+)\s*;", re.M),
}

#  *** N-D44 GUARD, STRUCTURAL. ***
#  PREREG Sec.3.6: "No gate in this item reads finalRes.  A finalRes comparator
#  is structurally blind to the condition DAFoam fails on."  _INITRES_RE above
#  captures group(2) = the value that follows `initRes:`, and the literal
#  `finalRes:` appears in the pattern ONLY as a right anchor -- it is never a
#  capture group, so no code path in this file can return it.  The selftest
#  feeds this reader a log carrying a SMALL initRes beside a LARGE finalRes and
#  asserts the small one comes back.
#
#  *** THIS GUARD WAS AN `assert` AND IS NOT ANY MORE (L-332). ***  Found by
#  this lane 2026-09-11 while repairing Defects A and B: `python3 -O` strips
#  `assert` outright, so under -O the one structural guard standing between the
#  reader and N-D44's blindness simply was not there.  A comparator that gates
#  on `assert` gates on nothing under -O.  It refuses now, in both modes.
if "finalRes" in _INITRES_RE.pattern.split("(")[1]:
    refuse("N-D44", "finalRes sits inside the FIRST CAPTURE GROUP of _INITRES_RE. "
                    "PREREG Sec.3.6: 'No gate in this item reads finalRes.  A "
                    "finalRes comparator is structurally blind to the condition "
                    "DAFoam fails on.'  Refusing to run at all.")


def count_ast_asserts(path=None):
    """L-332: count this module's own `ast.Assert` nodes.

    A comparator that gates on `assert` gates on NOTHING under `python3 -O`.
    This file must carry zero, and it checks itself rather than trusting a
    reader elsewhere to check it.  Reads the SOURCE FILE from disk, not the
    compiled module, because that is the artifact the freeze hashes.
    """
    p = path or os.path.abspath(__file__)
    try:
        src = open(p, "r", encoding="utf-8", errors="replace").read()
    except OSError as e:
        refuse("L-332", "cannot read own source at %s to run the assert census: "
                        "%s.  A census that cannot read anything is a planted "
                        "zero (CLAUDE.md rule 3)." % (p, e))
    tree = ast.parse(src)
    nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    return len(nodes), [n.lineno for n in nodes]


def guard_no_asserts():
    """Refuse to run at all if this file carries an `assert` (L-332)."""
    n, lines = count_ast_asserts()
    if n:
        refuse("L-332", "this comparator carries %d `assert` statement(s), at "
                        "line(s) %s.  `python3 -O` strips them, so every one is a "
                        "gate that disappears under an interpreter flag (L-332). "
                        "Refusing to run." % (n, lines))
    return n


def read_log(path):
    if not os.path.isfile(path):
        refuse("READ", "solver log does not exist: %s" % path)
    with open(path, "r", errors="replace") as fh:
        txt = fh.read()
    out = {"path": path, "bytes": len(txt)}

    out["CD"] = [float(m) for m in _FUNC_RE["CD"].findall(txt)]
    out["CL"] = [float(m) for m in _FUNC_RE["CL"].findall(txt)]
    out["times"] = [float(m) for m in _TIME_RE.findall(txt)]
    out["exec_times"] = [float(m) for m in _EXEC_RE.findall(txt)]
    out["end_line"] = bool(re.search(r"^End\s*$", txt, re.M))

    for k, rx in _DAOPT_RE.items():
        m = rx.search(txt)
        out[k] = float(m.group(1)) if m else None
    m = _PMR_RE.search(txt)
    out["primal_min_residual"] = float(m.group(1)) if m else None

    # Per-equation INITIAL residuals at the LAST printed step (Sec.3.6 limb 2).
    # Walk the last `Time = ` block only, so a converged tail is not confused
    # with an early iteration.
    tmarks = [m.start() for m in _TIME_RE.finditer(txt)]
    tail = txt[tmarks[-1]:] if tmarks else txt
    last = {}
    for eq, val in _INITRES_RE.findall(tail):
        last[eq] = float(val)
    out["last_initRes"] = last
    return out


# =====================================================================
# 4.  GATES
# =====================================================================

def gate_g_sys(surfaces, cells, faces, report):
    """PREREG Sec.3.1.  Five limbs.  Refuses (exit 2) on any failure."""
    print("\n--- G-SYS  (PREREG Sec.3.1) ---")
    ok = True

    # limb 1 -- cell-count ratio 8.000 +- 0.001 per step
    for fine, coarse in (("L2", "L3"), ("L1", "L2")):
        r = cells[fine] / float(cells[coarse])
        good = abs(r - REG_CELL_RATIO) <= REG_CELL_RATIO_TOL
        print("  limb1 cells   %s/%s = %d/%d = %.6f   (8.000 +- 0.001)  %s"
              % (fine, coarse, cells[fine], cells[coarse], r, "OK" if good else "FAIL"))
        ok &= good
    for lv in LEVELS:
        if cells[lv] != REG_CELLS[lv]:
            refuse("G-SYS", "Sec.2.5 / Sec.6 stage 1: %s has %d cells, registered "
                            "%d.  'Any departure from 99,840 / 798,720 / 6,389,760 "
                            "is a launch-blocking refusal, not a note.'"
                   % (lv, cells[lv], REG_CELLS[lv]))

    # limb 2 -- surface face-count ratio EXACTLY 4
    #   *** THE MEASURED TRAP THIS LIMB EXISTS FOR ***
    #   /home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse has EXACTLY
    #   99,840 cells -- the registered L3 count -- and is NOT L3.  Measured
    #   2026-09-11 from its own constant/polyMesh: note "nCells:99840", and
    #   `wing` nFaces = 1560 (surface c3, N=65), against the registered L3's
    #   `wing` nFaces = 6240 (surface c2, N=17).  Same cell count, different
    #   body, different discretisation.  CELL COUNT ALONE DOES NOT IDENTIFY A
    #   LEVEL, and limb 1 above would have waved that mesh through.
    for fine, coarse in (("L2", "L3"), ("L1", "L2")):
        num, den = faces[fine], faces[coarse]
        good = (den > 0) and (num == REG_FACE_RATIO * den)
        print("  limb2 faces   %s/%s = %d/%d  (exactly 4)  %s"
              % (fine, coarse, num, den, "OK" if good else "FAIL"))
        ok &= good
    for lv in LEVELS:
        if faces[lv] != REG_SURFACE_FACES[lv]:
            print("  limb2 IDENTITY FAIL  %s `wing` nFaces = %d, registered %d "
                  "(surface %s).  Cell count alone does not identify a level."
                  % (lv, faces[lv], REG_SURFACE_FACES[lv], REG_SURFACE_TAG[lv]))
            ok = False

    # limb 3 -- COORDINATE ARRAYS DIFFER.  Never an md5 (Sec.3.1 block quote:
    # md5-on-CGNS is not reproducible in the difference direction -- same
    # operator, same input, same byte count, different hash).
    pts = {lv: surfaces[lv] for lv in LEVELS}
    for fine, coarse in (("L2", "L3"), ("L1", "L2")):
        a, b_ = pts[coarse], pts[fine]
        differ = (len(a) != len(b_)) or (a != b_)
        print("  limb3 coords  %s(%d pts) vs %s(%d pts) DIFFER : %s"
              % (coarse, len(a), fine, len(b_), "OK" if differ else "FAIL"))
        ok &= differ

    # limb 4 -- bounding boxes agree to 1e-5 of root chord (body identity)
    boxes = {lv: bbox(pts[lv]) for lv in LEVELS}
    ref = boxes["L1"]
    for lv in LEVELS:
        d = max(max(abs(boxes[lv][i][k] - ref[i][k]) for k in range(3)) for i in range(2))
        good = d <= REG_BBOX_TOL
        print("  limb4 bbox    %s vs L1 : max |d| = %.3e  (tol %.3e = 1e-5 c_root)  %s"
              % (lv, d, REG_BBOX_TOL, "OK" if good else "FAIL"))
        ok &= good
        report.setdefault("bbox", {})[lv] = boxes[lv]

    # limb 5' -- G-NEST.  REGISTERED GATE (AMENDMENT 2(a)), replacing the
    # limb 5 that amendment struck.  Every point of the coarser surface must be
    # present BIT-EXACTLY in the finer surface, level by level.
    #
    #   An exact factor-2 coarsening MUST satisfy this: IT SELECTS ALTERNATE
    #   POINTS, IT DOES NOT MOVE THEM.  Measured 2026-09-11 on the real surfaces
    #   under /home/ubuntu/certonomous-runs/A3GC-mesh-family-probe/ : 0 misses of
    #   6,765 c2 points in c1, and 0 misses of 26,001 c1 points in c0.  A single
    #   1e-6 nudge to one coordinate breaks it (selftest B4).
    #
    #   THIS IS A STATEMENT NO md5 CAN EXPRESS, and it is sharper than any
    #   thickness tolerance -- which is why AMENDMENT 2(a) could strike limb 5
    #   and leave body identity BETTER guarded than before, not worse.  Sec.3.1's
    #   warning against hash comparisons is unaffected and stands.
    print("  --- G-NEST (limb 5', AMENDMENT 2(a)) ---")
    for fine, coarse in (("L2", "L3"), ("L1", "L2")):
        a, b_ = pts[coarse], pts[fine]
        S = set(b_)
        miss = sum(1 for q in a if q not in S)
        print("  G-NEST        every %s point present BIT-EXACTLY in %s : "
              "%d misses of %d  %s"
              % (coarse, fine, miss, len(a), "OK" if miss == 0 else "FAIL"))
        report.setdefault("G-NEST", {})["%s_in_%s" % (coarse, fine)] = {
            "misses": miss, "of": len(a)}
        ok &= (miss == 0)

    # limb 5 -- TE thickness at root/mid/tip.
    # *** STRUCK AS A GATE BY AMENDMENT 2(a).  DIAGNOSTIC ONLY, NEVER GATING. ***
    te = {}
    for lv in LEVELS:
        te[lv] = {}
        for lab, frac in (("root", 0.0), ("mid", 0.5), ("tip", 1.0)):
            v, n = te_thickness(pts[lv], frac)
            te[lv][lab] = v
            print("  limb5 TE      %s %-4s = %s  (n=%d)   [DIAGNOSTIC]"
                  % (lv, lab, "STRIP EMPTY" if v is None else "%.6e" % v, n))
    report["te_thickness"] = te
    spreads = {}
    for lab in ("root", "mid", "tip"):
        vals = [te[lv][lab] for lv in LEVELS]
        if any(v is None for v in vals):
            print("  limb5 %-4s    DIAGNOSTIC: a level has an empty strip -> "
                  "not comparable" % lab)
            spreads[lab] = None
            continue
        lo, hi = min(vals), max(vals)
        rel = (hi - lo) / hi if hi > 0 else (0.0 if lo == 0 else float("inf"))
        spreads[lab] = rel
        print("  limb5 %-4s    DIAGNOSTIC: spread = %.4f %%   (the STRUCK 1 %% "
              "tolerance would have said %s)"
              % (lab, 100.0 * rel, "OK" if rel <= REG_TE_REL_TOL else "FAIL"))
    report["G-SYS_limb5_diagnostic_spreads"] = spreads
    print("  limb5         *** REPORTED, NEVER GATING.  AMENDMENT 2(a) STRUCK this")
    print("                limb as a gate because it is UNMEASURABLE AS WRITTEN,")
    print("                NOT because it failed.  Sec.3.1 limb 5 fixed a 1 %")
    print("                tolerance but recorded no recipe, and every window-based")
    print("                TE statistic is point-density dependent while these")
    print("                levels differ 4x in point count by construction.  It")
    print("                fails even between the two FINEST levels, where no zero")
    print("                is involved: tip 2.974395e-03 on L2 against 2.917384e-03")
    print("                on L1, 1.9 % against 1 %.  Body identity is carried by")
    print("                limb 4 and by G-NEST instead. ***")

    report["G-SYS"] = bool(ok)
    if not ok:
        refuse("G-SYS", "the family is not proved systematic (PREREG Sec.3.1). "
                        "Every failing limb is named above.  A red is never "
                        "inferred green (PREREG Sec.6 stage 2).")
    print("  G-SYS: all five limbs green")
    return True


def gate_g_cold(case_root, launch_epoch, report):
    """PREREG Sec.3.3.  pyDAFoam writes the primal end state back into time-0,
    so a second run of a case directory silently warm-starts.  Measured on this
    very case (Sec.3.3): A3-onera-m6-transonic/processor0/0/U.gz is 5,476,863 B,
    mtime 2026-07-28 02:48 -- the size of the t=629 field and newer than it,
    while every other field in that `0` is a ~450 B placeholder."""
    print("\n--- G-COLD  (PREREG Sec.3.3) on %s ---" % case_root)
    bad = []

    # limb 1 -- no time directory other than 0, in the root or in any processor*
    roots = [case_root] + sorted(glob.glob(os.path.join(case_root, "processor*")))
    for r in roots:
        if not os.path.isdir(r):
            continue
        for d in sorted(os.listdir(r)):
            full = os.path.join(r, d)
            if not os.path.isdir(full):
                continue
            try:
                t = float(d)
            except ValueError:
                continue
            if t != 0.0:
                bad.append("time directory %s exists" % full)

    # limb 2 -- every field in 0 predates launch and is placeholder-sized
    sizes = {}
    for r in roots:
        z = os.path.join(r, "0")
        if not os.path.isdir(z):
            continue
        for f in sorted(os.listdir(z)):
            fp = os.path.join(z, f)
            if not os.path.isfile(fp):
                continue
            st = os.stat(fp)
            sizes[fp] = st.st_size
            if launch_epoch is not None and st.st_mtime > launch_epoch:
                bad.append("0-field newer than launch: %s (mtime %s)"
                           % (fp, time.strftime("%Y-%m-%d %H:%M:%S",
                                                time.localtime(st.st_mtime))))
    if sizes:
        med = sorted(sizes.values())[len(sizes) // 2]
        for fp, n in sizes.items():
            if med > 0 and n > 50 * med:
                bad.append("0-field is %d B against a %d B median -- this is a "
                           "WRITTEN SOLUTION, not an initial condition: %s"
                           % (n, med, fp))
    else:
        refuse("G-COLD", "%s: read ZERO fields under any `0` directory.  A zero "
                         "from a reader not shown able to see a non-zero is not "
                         "evidence (CLAUDE.md rule 3)." % case_root)

    report.setdefault("G-COLD", {})[case_root] = {"violations": bad, "n_fields": len(sizes)}
    for b in bad:
        print("  VIOLATION  %s" % b)
    if bad:
        refuse("G-COLD", "%s is not a clean cold start.  Sec.3.3: 'A guard that "
                         "finds either condition violated REFUSES the level; it "
                         "does not clean up and proceed.'" % case_root)
    print("  G-COLD: clean (%d fields under `0`, no non-zero time directory)" % len(sizes))
    return True


def gate_g_tol(log, report):
    """PREREG Sec.3.5.  The accept floor is the PRODUCT (N-D43)."""
    print("\n--- G-TOL  (PREREG Sec.3.5) ---")
    t, d = log.get("primalMinResTol"), log.get("primalMinResTolDiff")
    if t is None or d is None:
        refuse("G-TOL", "%s: the solver's own DAOption dump does not print "
                        "primalMinResTol / primalMinResTolDiff.  Refusing rather "
                        "than assuming the registered values." % log["path"])
    print("  primalMinResTol     = %g   (registered %g)" % (t, REG_PRIMAL_MIN_RES_TOL))
    print("  primalMinResTolDiff = %g   (registered %g)" % (d, REG_PRIMAL_MIN_RES_TOL_DIFF))
    floor = t * d
    print("  accept floor (PRODUCT, N-D43) = %g   (registered %g)" % (floor, REG_ACCEPT_FLOOR))
    report.setdefault("G-TOL", {})[log["path"]] = {"tol": t, "diff": d, "floor": floor}
    if t != REG_PRIMAL_MIN_RES_TOL or d != REG_PRIMAL_MIN_RES_TOL_DIFF:
        refuse("G-TOL", "Sec.3.5: 'G-TOL refuses if the solver's own DAOption dump "
                        "on any level prints anything else.'  Got %g x %g, "
                        "registered %g x %g.  No number is carried across from "
                        "another level or another item."
               % (t, d, REG_PRIMAL_MIN_RES_TOL, REG_PRIMAL_MIN_RES_TOL_DIFF))
    return floor


def gate_g_res(log, accept_floor, report):
    """PREREG Sec.3.6 (N-D44).  READS `initRes`, NEVER `finalRes`.

    AMENDMENT 1(b): this limb is RETAINED AS A COMPLETION PRECONDITION AND IS
    EXPLICITLY NOT A DISCRIMINATING GATE -- its threshold (1e-06) is numerically
    identical to the solver's own acceptance product, so a primal handed back
    without an AnalysisError has already satisfied approximately what it asks.
    It is never quoted, alone, as evidence that a level converged.  The
    discriminating limb is G-PLAT.
    """
    print("\n--- G-RES  (PREREG Sec.3.6 / N-D44)  [PRECONDITION, NOT DISCRIMINATING] ---")
    print("  BINDING ROUTE: the per-equation initRes lines (Sec.3.6 limb 2, "
          "AMENDMENT 2(b)).")
    last = log["last_initRes"]
    if not last:
        refuse("G-RES", "%s: read ZERO per-equation initRes lines.  Refusing "
                        "rather than reporting convergence from an empty read."
               % log["path"])
    ok = True
    worst = 0.0
    for eq in REG_INITRES_EQNS:
        if eq not in last:
            print("  %-8s initRes  MISSING at the last printed step" % eq)
            ok = False
            continue
        v = last[eq]
        worst = max(worst, v)
        good = v <= REG_INITRES_MAX
        print("  %-8s initRes = %.6e   (<= %g)  %s" % (eq, v, REG_INITRES_MAX,
                                                       "OK" if good else "FAIL"))
        ok &= good
    # AMENDMENT 2(b): the `Primal min residual` banner is REPORTING-ONLY.
    # Measured: the string occurs ZERO times in
    # cases/dafoam/ladder-a/logs_A3/run_model_run3.log, the validated primal of
    # this very case.  It is emitted by the pyDAFoam driver, not by the runScript
    # path this family uses.  ITS ABSENCE IS REPORTED LOUDLY AND IS NEVER A
    # REFUSAL, because absence is a property of the DRIVER PATH, not of the
    # solution.  The per-equation initRes route above is the BINDING route.
    pmr = log.get("primal_min_residual")
    if pmr is None:
        print("  Primal min residual: *** LINE ABSENT from this log. ***")
        print("    REPORTED, NOT GATED (AMENDMENT 2(b)).  Absence is a property of the")
        print("    pyDAFoam driver path, not of the solution, and is never a refusal.")
        print("    The BINDING route is the per-equation initRes lines above.")
    else:
        good = pmr < accept_floor
        print("  Primal min residual = %.6e   (< accept floor %g)  %s   "
              "[REPORTED, NOT GATED -- AMENDMENT 2(b)]"
              % (pmr, accept_floor, "would pass" if good else "would NOT pass"))
    # AMENDMENT 1(b) item 3 -- tighter floor REPORTED, never graded
    print("  DIAGNOSTIC (reported, NEVER graded -- AMENDMENT 1(b) item 3):")
    print("    worst per-equation initRes = %.6e  vs tighter floor %g : %s"
          % (worst, REG_DIAGNOSTIC_FLOOR,
             "would pass" if worst <= REG_DIAGNOSTIC_FLOOR else "would NOT pass"))
    report.setdefault("G-RES", {})[log["path"]] = {
        "last_initRes": last, "primal_min_residual": pmr,
        "worst_initRes": worst, "precondition_met": bool(ok)}
    return bool(ok)


# =====================================================================
# G-COMPLETE -- PREREG Sec.3.7 / CLAUDE.md rule 4.
#
# *** WHY THIS EXISTS, AND WHY IT IS A REPAIR AND NOT A NEW GATE. ***
# Sec.3.7 has registered the strict completion rule and the age guard since the
# document was written.  The comparator DID NOT IMPLEMENT ITS OWN REGISTRATION:
# `read_log` parsed `end_line`, `times` and `exec_times` and NOTHING EVER READ
# THEM AGAIN.  Found 2026-09-11 by reading the code, before any level had solved.
# Making the instrument do what its document already says it does is a repair.
#
# THE FAILURE IT PREVENTS, CONCRETELY: a level that dies at iteration 4,000 with
# no `End` line leaves a TRUNCATED log whose tail is PERFECTLY PLATEAUED -- a
# dead solve plateaus better than a live one -- so G-PLAT passes it, the triple
# grades CONVERGING, and the item returns a converged verdict ON A CORPSE.
#
# DIRECTION: every clause here can only turn a PASS into NOT A RESULT.  It adds
# refusals and can never manufacture a favourable verdict.
# =====================================================================

_CONTROLDICT_RE = {
    "endTime": re.compile(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", re.M),
    "deltaT": re.compile(r"^\s*deltaT\s+([0-9.eE+-]+)\s*;", re.M),
    "writeInterval": re.compile(r"^\s*writeInterval\s+([0-9.eE+-]+)\s*;", re.M),
}


def read_controldict(case_root):
    """endTime / deltaT / writeInterval from the case's OWN system/controlDict.

    The solver log does not print endTime (measured: zero occurrences in
    cases/dafoam/ladder-a/logs_A3/run_model_run3.log, the validated primal of
    this case), so `last time == endTime` cannot be checked from the log alone
    and the case's own controlDict is the only source.  Refuses if absent
    rather than assuming a value.
    """
    p = os.path.join(case_root, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("G-COMPLETE", "%s: no system/controlDict, so `last time == endTime` "
                             "(CLAUDE.md rule 4) cannot be checked.  The solver log "
                             "does not print endTime.  Refusing rather than "
                             "assuming one." % case_root)
    txt = open(p, "r", errors="replace").read()
    out = {}
    for k, rx in _CONTROLDICT_RE.items():
        m = rx.search(txt)
        out[k] = float(m.group(1)) if m else None
    if out["endTime"] is None:
        refuse("G-COMPLETE", "%s: system/controlDict has no `endTime` entry." % p)
    return out


def _field_basenames(d):
    """Field names in a time directory, `.gz` stripped, sub-directories ignored
    (polyMesh/ and uniform/ are not fields)."""
    out = {}
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        fp = os.path.join(d, f)
        if not os.path.isfile(fp):
            continue
        out[f[:-3] if f.endswith(".gz") else f] = fp
    return out


def _time_dirs(root):
    """{float time: path} for every numeric directory directly under `root`."""
    out = {}
    if not os.path.isdir(root):
        return out
    for d in sorted(os.listdir(root)):
        full = os.path.join(root, d)
        if not os.path.isdir(full):
            continue
        try:
            out[float(d)] = full
        except ValueError:
            pass
    return out


def read_rc(case_root, log_path):
    """The solver's exit code, from an artifact the RUNNER must write.

    CLAUDE.md rule 4 clause 1 is `rc = 0`, and an exit code is not in the log --
    `setsid timeout cmd` exits 0 for every outcome, so an rc captured AROUND the
    launch is worthless and only an rc captured INSIDE the detached wrapper means
    anything.  Looked for, in order: <case>/<logbasename>.rc, then <case>/rc.
    ABSENT -> REFUSE.  A missing exit code is not a zero exit code.
    """
    cands = [os.path.join(case_root, os.path.basename(log_path) + ".rc"),
             os.path.join(case_root, "rc")]
    for c in cands:
        if os.path.isfile(c):
            txt = open(c, "r", errors="replace").read().strip()
            m = re.search(r"(-?\d+)", txt)
            if not m:
                refuse("G-COMPLETE", "%s: exit-code artifact holds no integer: %r"
                       % (c, txt[:80]))
            return int(m.group(1)), c
    refuse("G-COMPLETE", "%s: no solver exit code on disk.  CLAUDE.md rule 4 "
                         "clause 1 is `rc = 0` and A MISSING EXIT CODE IS NOT A "
                         "ZERO EXIT CODE.  The runner must write it to one of:\n"
                         "    %s\n"
                         "  capturing it INSIDE the detached wrapper -- `setsid "
                         "timeout cmd` returns 0 for every outcome, so an rc taken "
                         "around the launch measures nothing."
           % (case_root, "\n    ".join(cands)))


def gate_g_complete(case_root, log, level, report):
    """PREREG Sec.3.7 / CLAUDE.md rule 4.  ALL of it holds, or the level is
    NOT A RESULT and -- by standing rule 5 clause 1 -- the triple with it.

    EVERY CLAUSE PRINTS ITS MEASURED VALUE, pass or fail: a completion gate that
    reports only its verdict is unauditable.
    """
    print("\n--- G-COMPLETE  (PREREG Sec.3.7 / CLAUDE.md rule 4) on %s ---" % level)
    cd = read_controldict(case_root)
    rc, rc_src = read_rc(case_root, log["path"])
    rec = {"controlDict": cd, "rc": rc, "rc_source": rc_src, "clauses": {}}
    ok = True

    def clause(name, good, detail):
        rec["clauses"][name] = {"pass": bool(good), "detail": detail}
        print("  %-26s %-4s  %s" % (name, "OK" if good else "FAIL", detail))
        return bool(good)

    # ---- clause 1: rc == 0
    ok &= clause("1 rc == 0", rc == 0, "rc = %d   (from %s)" % (rc, rc_src))

    # ---- clause 2: an `End` line
    ok &= clause("2 `End` line present", log["end_line"],
                 "End line %s in %s" % ("FOUND" if log["end_line"] else "ABSENT",
                                        os.path.basename(log["path"])))

    # ---- clause 3: last time == endTime
    times = log["times"]
    if not times:
        ok &= clause("3 last time == endTime", False,
                     "read ZERO `Time = ` lines -- refusing to call that complete")
        last_t = None
    else:
        last_t = times[-1]
        ok &= clause("3 last time == endTime", last_t == cd["endTime"],
                     "last printed Time = %g, controlDict endTime = %g"
                     % (last_t, cd["endTime"]))

    # ---- clause 5: ExecutionTime count consistent with the step count.
    # NOTE ON WHICH FORM APPLIES.  CLAUDE.md rule 4 clause 5 reads
    # `ExecutionTime count == round(endTime/deltaT)` for the HISTORICAL UNIT-STEP
    # case where every step is printed, and `n_exec == steps written` otherwise.
    # THIS FAMILY PRINTS AT printInterval, NOT EVERY STEP -- measured on the
    # validated primal: 61 ExecutionTime lines against endTime 6000 and deltaT 1.
    # The binding form here is therefore n_exec == n_times.  The round(E/dT)
    # arithmetic is printed BESIDE it as a REPORTED cross-check, never gated.
    n_exec, n_times = len(log["exec_times"]), len(times)
    ok &= clause("5 ExecutionTime count", n_exec == n_times,
                 "%d ExecutionTime lines vs %d `Time = ` lines" % (n_exec, n_times))
    pi = log.get("printInterval")
    if pi and cd["endTime"]:
        pred = 1 + int(cd["endTime"] // pi)
        print("  %-26s      predicted 1 + floor(endTime/printInterval) = "
              "1 + floor(%g/%g) = %d, measured %d   [REPORTED, NOT GATED]"
              % ("  cadence cross-check", cd["endTime"], pi, pred, n_times))
        rec["cadence_predicted"] = pred

    # ---- clause 4: fields present at endTime, and clause 6: THE AGE GUARD.
    # Time directories live under the case root for a reconstructed run and under
    # processor*/ for a decomposed one; BOTH are searched, and finding none at
    # endTime is a failure, never a pass.
    roots = [case_root] + sorted(glob.glob(os.path.join(case_root, "processor*")))
    end_dirs, zero_dirs = [], []
    for r in roots:
        td = _time_dirs(r)
        if cd["endTime"] in td:
            end_dirs.append(td[cd["endTime"]])
        if 0.0 in td:
            zero_dirs.append(td[0.0])
    if not end_dirs:
        ok &= clause("4 fields at endTime", False,
                     "NO time directory `%g` under %s or any processor* -- a run "
                     "whose endTime was never written is not complete"
                     % (cd["endTime"], case_root))
        ok &= clause("6 AGE GUARD", False, "no endTime directory to age-check")
    else:
        # required fields = whatever the case's OWN `0` holds.  NOT an invented
        # list: the item must have written back what it initialised.
        req = set()
        for z in zero_dirs:
            req |= set(_field_basenames(z))
        got = set()
        for e in end_dirs:
            got |= set(_field_basenames(e))
        missing = sorted(req - got)
        ok &= clause("4 fields at endTime", (not missing) and bool(req),
                     ("all %d field(s) from `0` present at endTime: %s"
                      % (len(req), " ".join(sorted(req)))) if (req and not missing)
                     else ("MISSING at endTime: %s" % " ".join(missing) if missing
                           else "read ZERO fields under any `0` -- refusing to "
                                "call an empty requirement satisfied"))

        # ---- clause 6: THE AGE GUARD.
        # Every field at endTime must be NEWER than the case's own `0/T`, because
        # `0/T` is touched last at launch and so DATES THE RUN ALLOWED TO PRODUCE
        # THE ANSWER.  A field older than it was produced by some earlier run.
        ref, ref_path = None, None
        for z in zero_dirs:
            fb = _field_basenames(z)
            if "T" in fb:
                st = os.stat(fb["T"])
                if ref is None or st.st_mtime > ref:
                    ref, ref_path = st.st_mtime, fb["T"]
        if ref is None:
            ok &= clause("6 AGE GUARD", False,
                         "no `0/T` in %s or any processor* -- the age guard has no "
                         "reference and is NOT waived for want of one" % case_root)
        else:
            stale = []
            n_checked = 0
            for e in end_dirs:
                for nm, fp in sorted(_field_basenames(e).items()):
                    n_checked += 1
                    if os.stat(fp).st_mtime <= ref:
                        stale.append(nm)
            ok &= clause("6 AGE GUARD", not stale and n_checked > 0,
                         ("all %d endTime field(s) NEWER than %s"
                          % (n_checked, ref_path)) if (not stale and n_checked)
                         else ("%d endTime field(s) NOT newer than %s: %s"
                               % (len(stale), ref_path, " ".join(sorted(set(stale))))
                               if stale else
                               "read ZERO fields at endTime -- not a pass"))

    rec["pass"] = bool(ok)
    report.setdefault("G-COMPLETE", {})[level] = rec
    if not ok:
        print("  G-COMPLETE: %s is NOT COMPLETE -> NOT A RESULT, and by standing "
              "rule 5 clause 1 the triple with it." % level)
    else:
        print("  G-COMPLETE: all six clauses hold for %s." % level)
    return bool(ok)


def peak_to_peak(xs):
    """AMENDMENT 1(a): the registered statistic is the PEAK-TO-PEAK excursion
    max - min over the window.

    *** AN ADJACENT-SAMPLE DELTA IS REFUSED BY NAME, AND THIS IS WHY. ***
    An adjacent-sample difference is an INCREMENT, not an EXCURSION: a signal
    drifting steadily in one direction has a small increment at every step and
    never plateaus at all.  This is precisely the defect the cfd team's DrivAer
    Gate A1 plateau limb carried and that this lab caught on 2026-09-10 -- a
    two-sample increment wearing a plateau's name, passing by 120x while the
    signal's own excursion over 500 iterations was 8.35 %.  It is not repeated
    here.  `adjacent_delta()` below exists ONLY so the record can print both
    forms side by side (AMENDMENT 1(a)'s honesty note); no gate reads it.
    """
    return max(xs) - min(xs)


def adjacent_delta(xs):
    """REPORTED, NEVER GATED.  See peak_to_peak()."""
    return max(abs(xs[i + 1] - xs[i]) for i in range(len(xs) - 1)) if len(xs) > 1 else 0.0


def gate_g_plat(hist, level_to_level_diff, report, level, func):
    """AMENDMENT 1(a).  Iterative error >= 10x smaller than the level-to-level
    difference, for CD AND CL, from the solver's own CD:/CL: log lines.

    Window: the LAST 10 PRINTED SAMPLES.  Fewer than 10 -> that level is
    NOT A RESULT for want of evidence ("a window that cannot exhibit an
    excursion cannot prove a plateau, and a level that printed too rarely to be
    judged is not thereby judged converged").
    """
    if len(hist) < REG_PLAT_WINDOW:
        print("    %s %s: only %d printed samples (need %d) -> NOT A RESULT "
              "for want of evidence" % (level, func, len(hist), REG_PLAT_WINDOW))
        report.setdefault("G-PLAT", {}).setdefault(level, {})[func] = {
            "n_samples": len(hist), "verdict": "NOT A RESULT",
            "reason": "fewer than %d printed samples" % REG_PLAT_WINDOW}
        return False, "NOT A RESULT"
    win = hist[-REG_PLAT_WINDOW:]
    p2p = peak_to_peak(win)
    adj = adjacent_delta(win)                     # reported only
    need = abs(level_to_level_diff) / REG_PLAT_MARGIN
    ok = p2p <= need
    print("    %s %s: peak-to-peak(last %d) = %.6e   need <= %.6e "
          "(= |level-to-level %.6e| / 10)  %s"
          % (level, func, REG_PLAT_WINDOW, p2p, need, level_to_level_diff,
             "OK" if ok else "FAIL"))
    print("        [reported, NOT gated] max adjacent-sample delta = %.6e "
          "(ratio p2p/adjacent = %.2f)" % (adj, (p2p / adj) if adj > 0 else float("inf")))
    report.setdefault("G-PLAT", {}).setdefault(level, {})[func] = {
        "n_samples": len(hist), "window": REG_PLAT_WINDOW,
        "peak_to_peak": p2p, "adjacent_delta_reported_only": adj,
        "threshold": need, "level_to_level_diff": level_to_level_diff,
        "verdict": "PASS" if ok else "NOT A RESULT"}
    return ok, ("PASS" if ok else "NOT A RESULT")


# ---------------------------------------------------------------- Roache

def classify_triple(f3, f2, f1, r=REG_R):
    """Standing rule 5 / PREREG Sec.4.2.  f3 coarse, f2 medium, f1 fine.
    Returns (class, p, R, eps32, eps21)."""
    eps32 = f3 - f2
    eps21 = f2 - f1
    tiny = 1e-14 * max(1.0, abs(f1))
    if abs(eps32) <= tiny and abs(eps21) <= tiny:
        return "EXACT", None, None, eps32, eps21
    if abs(eps32) <= tiny or abs(eps21) <= tiny:
        return "STAGNANT", None, None, eps32, eps21
    R = eps21 / eps32
    if R < 0.0:
        return "OSCILLATORY", None, R, eps32, eps21
    if abs(R - 1.0) < 1e-6:
        return "STAGNANT", None, R, eps32, eps21
    if R >= 1.0:
        return "DIVERGENT", None, R, eps32, eps21
    p = math.log(abs(eps32 / eps21)) / math.log(r)
    return "CONVERGING", p, R, eps32, eps21


def gci_fine(f1, eps21, p, r=REG_R, Fs=REG_FS):
    den = (r ** p) - 1.0
    if den <= 0 or f1 == 0:
        return None
    return Fs * abs(eps21 / f1) / den


def richardson(f1, f2, p, r=REG_R):
    den = (r ** p) - 1.0
    if den <= 0:
        return None
    return f1 + (f1 - f2) / den


def is_monotone(f3, f2, f1):
    return (f3 - f2) * (f2 - f1) > 0.0


def gate_g_triple(func, vals, plat_ok, res_ok, complete_ok, report):
    """Standing rule 5, APPLIED IN ORDER (PREREG Sec.4.2):
      (1) any level not iteratively converged or failing G-PLAT -> NOT A RESULT
      (2) triple DIVERGENT/STAGNANT/OSCILLATORY/EXACT -> NOT A RESULT, with the
          value, BOTH triples and BOTH orders printed beside it
      (3) CONVERGING -> PASS inside the Sec.4.3 band else GATE FAIL, GCI printed
    The gate can only turn a PASS or GATE FAIL INTO NOT A RESULT, never the
    reverse.  GCI is NEVER quoted when the three values are not monotone.
    """
    f3, f2, f1 = vals["L3"], vals["L2"], vals["L1"]
    cls, p, R, eps32, eps21 = classify_triple(f3, f2, f1)
    mono = is_monotone(f3, f2, f1)
    gci = gci_fine(f1, eps21, p) if (cls == "CONVERGING" and mono and p is not None) else None
    rex = richardson(f1, f2, p) if (cls == "CONVERGING" and p is not None) else None

    rec = {"values": {"L3": f3, "L2": f2, "L1": f1},
           "class": cls, "p": p, "R": R, "eps32": eps32, "eps21": eps21,
           "monotone": mono, "GCI_fine": gci, "richardson": rex}

    print("\n  %s triple:  L3 = %.8g   L2 = %.8g   L1 = %.8g" % (func, f3, f2, f1))
    print("    eps32 = %.6e   eps21 = %.6e   R = %s   class = %s"
          % (eps32, eps21, ("%.6f" % R) if R is not None else "n/a", cls))
    print("    observed order p = %s   [SURFACE-AND-OUTER-FIELD ORDER, PREREG Sec.2.6 "
          "-- s0 is held fixed at 1.0e-4 on all three levels, so the near-wall "
          "spacing is non-systematic]" % (("%.4f" % p) if p is not None else "n/a"))
    if mono and gci is not None:
        print("    GCI(fine, Fs=%.2f) = %.4f %%   (PASS band <= %.1f %%, prediction <= %.1f %%)"
              % (REG_FS, 100 * gci, 100 * REG_GCI_BAND[func], 100 * REG_GCI_PREDICTED[func]))
        print("    Richardson-extrapolated %s = %.8g" % (func, rex))
    else:
        print("    GCI: NOT QUOTED -- the three values are not monotone "
              "(standing rule 5: never quote a GCI when the three values are not "
              "monotone).")

    # ---- clause 1 (precedence): a level not COMPLETE / not converged / not plateaued
    if not complete_ok or not plat_ok or not res_ok:
        why = []
        if not complete_ok:
            why.append("G-COMPLETE (Sec.3.7 / rule 4)")
        if not plat_ok:
            why.append("G-PLAT")
        if not res_ok:
            why.append("the G-RES precondition")
        rec["verdict"] = emit_verdict(
            "%s triple" % func, "NOT A RESULT",
            "clause 1: a level failed " + " and ".join(why))
        report.setdefault("triples", {})[func] = rec
        return rec["verdict"]

    # ---- clause 2
    if cls != "CONVERGING":
        rec["verdict"] = emit_verdict("%s triple" % func, "NOT A RESULT",
                                      "clause 2: triple is %s" % cls)
        report.setdefault("triples", {})[func] = rec
        return rec["verdict"]

    # ---- clause 3
    lo, hi = REG_P_BAND
    if not (lo <= p <= hi):
        # Sec.4.3: p outside the band -> the triple is not CONVERGING -> NOT A RESULT.
        rec["verdict"] = emit_verdict(
            "%s triple" % func, "NOT A RESULT",
            "clause 3 / Sec.4.3: observed order p = %.4f outside [%.1f, %.1f]"
            % (p, lo, hi))
        report.setdefault("triples", {})[func] = rec
        return rec["verdict"]
    if gci is None:
        rec["verdict"] = emit_verdict("%s triple" % func, "NOT A RESULT",
                                      "GCI not computable on a non-monotone triple")
        report.setdefault("triples", {})[func] = rec
        return rec["verdict"]
    if gci <= REG_GCI_BAND[func]:
        rec["verdict"] = emit_verdict("%s triple" % func, "PASS",
                                      "p = %.4f in [1.0,3.0], GCI = %.4f %% <= %.1f %%"
                                      % (p, 100 * gci, 100 * REG_GCI_BAND[func]))
    else:
        rec["verdict"] = emit_verdict("%s triple" % func, "GATE FAIL",
                                      "GCI = %.4f %% exceeds the registered %.1f %%"
                                      % (100 * gci, 100 * REG_GCI_BAND[func]))
    report.setdefault("triples", {})[func] = rec
    return rec["verdict"]


# =====================================================================
# 5.  SHOCK PREDICTIONS P1-P4  (PREREG Sec.4.5)
# =====================================================================

LOGS_A3 = os.path.join("cases", "dafoam", "ladder-a", "logs_A3")


def run_shock_chain(vtp_path, workdir, logs_a3=LOGS_A3):
    """Re-run the ARCHIVED comparator path -- logs_A3/extract_cp.py then
    logs_A3/compare_cp.py against logs_A3/case_2308.dat -- ON COPIES.

    *** THE logs_A3 ARCHIVE IS READ-ONLY AND IS NEVER EDITED: it is the record
    of what ran (PREREG Sec.4.5). ***  The three archived files are copied into
    `workdir`, both scripts are executed there with `workdir` as cwd (they write
    cp_extracted.json / cp_comparison.json / shock_location.json into cwd), and
    the ORIGINALS ARE ASSERTED BYTE-IDENTICAL afterwards.
    """
    need = ["extract_cp.py", "compare_cp.py", "shock_location.py", "case_2308.dat"]
    srcs = [os.path.join(logs_a3, n) for n in need]
    for s in srcs:
        if not os.path.isfile(s):
            refuse("SHOCK", "archived comparator input missing: %s" % s)
    os.makedirs(workdir, exist_ok=True)
    with Untouched(srcs, "shock comparator re-run"):
        for s, n in zip(srcs, need):
            shutil.copy2(s, os.path.join(workdir, n))
        env = dict(os.environ)
        r1 = subprocess.run([sys.executable, "extract_cp.py", os.path.abspath(vtp_path),
                             "cp_extracted.json"], cwd=workdir, env=env,
                            capture_output=True, text=True)
        if r1.returncode != 0:
            refuse("SHOCK", "extract_cp.py failed (rc=%d) on %s\n%s"
                   % (r1.returncode, vtp_path, r1.stderr[-2000:]))
        for script, out in (("compare_cp.py", "cp_comparison.json"),
                            ("shock_location.py", "shock_location.json")):
            r = subprocess.run([sys.executable, script], cwd=workdir, env=env,
                               capture_output=True, text=True)
            if r.returncode != 0:
                refuse("SHOCK", "%s failed (rc=%d)\n%s" % (script, r.returncode,
                                                           r.stderr[-2000:]))
    return (json.load(open(os.path.join(workdir, "cp_comparison.json"))),
            json.load(open(os.path.join(workdir, "shock_location.json"))))


def pooled_upper_rms(cmp_json):
    num, n = 0.0, 0
    for eta, surfs in cmp_json.items():
        u = surfs.get("upper")
        if not u:
            continue
        num += (u["rms_dev"] ** 2) * u["n_common"]
        n += u["n_common"]
    if n == 0:
        refuse("SHOCK", "pooled upper-surface RMS read ZERO common points.  A "
                        "zero from a reader not shown able to see a non-zero is "
                        "not evidence (CLAUDE.md rule 3).")
    return math.sqrt(num / n), n


def evaluate_shock(shock_L3, shock_L1, cmp_L1, report, triple_converging):
    """P1-P4, PREREG Sec.4.5.  Each can fail, and failure is reported as failure.

    `triple_converging` is TRUE only when BOTH the CD and the CL triple classified
    CONVERGING.  Sec.4.5 P4 conditions the counter-hypothesis on exactly that, so
    the caller measures it and this function never infers it.
    """
    print("\n--- SHOCK PREDICTIONS P1-P4  (PREREG Sec.4.5) ---")
    res = {}

    # P1 -- Cp slope through the shock increases by >= 40 % at eta 0.80 and 0.90
    incs = {}
    for eta in REG_P1_STATIONS:
        k = str(eta)
        s3 = shock_L3.get(k, shock_L3.get("%.1f" % eta, {})).get("cfd_slope")
        s1 = shock_L1.get(k, shock_L1.get("%.1f" % eta, {})).get("cfd_slope")
        if s3 is None or s1 is None:
            refuse("SHOCK", "P1: slope missing at eta=%s on L3 or L1" % k)
        incs[eta] = (s1 - s3) / s3
        print("  P1  eta=%.2f  slope L3 = %.3f -> L1 = %.3f  (%+.1f %%)"
              % (eta, s3, s1, 100 * incs[eta]))
    p1_pass = all(v >= REG_P1_PASS_PCT for v in incs.values())
    p1_falsified = all(v < REG_P1_FALSIFY_PCT for v in incs.values())
    res["P1"] = {"increases": incs, "pass": p1_pass, "falsified": p1_falsified}
    res["P1"]["verdict"] = emit_verdict(
        "P1 sharpening", prediction_token(p1_pass, p1_falsified),
        ("falsified (< +15 %% at BOTH stations): the smearing is model, not mesh"
         if p1_falsified else
         ("" if p1_pass else
          "MIDDLE BAND (AMENDMENT 3(a)): neither >= +40 %% at both stations nor "
          "< +15 %% at both -- the registration supplies two thresholds and has "
          "declared the space between them evidence for NEITHER")))

    # P2 -- mean |shock position error| falls >= 30 %, and eta=0.20 below +0.060 c
    def mean_abs(sh):
        vs = [abs(sh[k]["shift_xoc"]) for k in sh if sh[k].get("shift_xoc") is not None]
        if not vs:
            refuse("SHOCK", "P2: read ZERO shock shifts")
        return sum(vs) / len(vs)
    m3, m1 = mean_abs(shock_L3), mean_abs(shock_L1)
    drop = (m3 - m1) / m3 if m3 else 0.0
    e20 = shock_L1.get("0.2", shock_L1.get("0.20", {})).get("shift_xoc")
    if e20 is None:
        refuse("SHOCK", "P2: eta=0.20 shift missing on L1")
    print("  P2  mean |dx/c| L3 = %.4f -> L1 = %.4f  (%+.1f %%);  eta=0.20 on L1 = %+.4f c"
          % (m3, m1, -100 * drop, e20))
    p2_pass = (drop >= REG_P2_MEAN_ABS_DROP) and (e20 < REG_P2_ETA20_PASS)
    p2_falsified = (e20 > REG_P2_ETA20_FALSIFY)
    res["P2"] = {"mean_L3": m3, "mean_L1": m1, "drop": drop, "eta20_L1": e20,
                 "pass": p2_pass, "falsified": p2_falsified}
    res["P2"]["verdict"] = emit_verdict(
        "P2 position", prediction_token(p2_pass, p2_falsified),
        ("falsified (eta=0.20 stays above +0.085 c): the aft bias is the "
         "SA model's shock/BL interaction, not resolution" if p2_falsified else
         ("" if p2_pass else
          "MIDDLE BAND (AMENDMENT 3(a)): the Sec.4.5 PASS pair (drop >= 30 %% AND "
          "eta=0.20 < +0.060 c) is not met and eta=0.20 is not above +0.085 c")))

    # P3 -- pooled upper-surface Cp RMS on L1 improves to <= 0.055
    rms, npts = pooled_upper_rms(cmp_L1)
    print("  P3  pooled upper-surface Cp RMS on L1 = %.4f over %d common points "
          "(baseline %.4f at 399,360 cells)" % (rms, npts, REG_BASELINE_POOLED_RMS))
    p3_pass = rms <= REG_P3_PASS_RMS
    p3_falsified = rms > REG_P3_FALSIFY_RMS
    res["P3"] = {"pooled_upper_rms_L1": rms, "n_points": npts,
                 "pass": p3_pass, "falsified": p3_falsified}
    res["P3"]["verdict"] = emit_verdict(
        "P3 pooled Cp", prediction_token(p3_pass, p3_falsified),
        ("falsified (> 0.070)" if p3_falsified else
         ("" if p3_pass else
          "MIDDLE BAND (AMENDMENT 3(a)): 0.055 < RMS <= 0.070")))

    # ---- P4 -- the registered counter-hypothesis.
    #
    # AMENDMENT 3(b): "all fail" means ALL THREE **FALSIFIED**, the STRONG form.
    # Sec.4.5 gives each prediction a PASS threshold AND a separate, lower
    # FALSIFICATION threshold, so "all fail" read two ways: all-three-not-PASS
    # (weak) or all-three-FALSIFIED (strong).  The WEAK reading would let P4 fire
    # on three MIDDLING results, and a counter-hypothesis is ADOPTED on strong
    # evidence, never on mere non-confirmation.  The strong form is also the
    # CONSERVATIVE direction: it makes P4 HARDER to fire.
    #
    # AMENDMENT 3(c): if FEWER THAN ALL THREE are falsified, P4 DOES NOT FIRE and
    # ITS REGISTERED READING IS NOT PRINTED -- so it cannot be adopted after the
    # fact by a reader skimming the output for it.
    all_falsified = p1_falsified and p2_falsified and p3_falsified
    all_not_pass = not (p1_pass and p2_pass and p3_pass)
    p4 = all_falsified if REG_P4_REQUIRES_ALL_FALSIFIED else all_not_pass
    res["P4_counter_hypothesis_active"] = p4
    res["P4_all_falsified"] = all_falsified
    res["P4_triple_converging"] = bool(triple_converging)
    if p4 and triple_converging:
        print("  P4  ALL THREE FALSIFIED and the CD/CL triple is CONVERGING.")
        print("      The registered reading (Sec.4.5 P4) is:")
        print('      "the M6 shock disagreement on this configuration is a '
              'turbulence-model limitation, not a grid limitation"')
        print("      -- and that is a RESULT, reported as such, not a failure of the item.")
    elif p4 and not triple_converging:
        print("  P4  all three FALSIFIED, but the CD/CL triple is NOT CONVERGING.")
        print("      Sec.4.5 conditions P4 on a CONVERGING triple, so P4 DOES NOT FIRE")
        print("      and its registered reading is NOT printed (AMENDMENT 3(c)/(d)).")
    else:
        print("  P4  NOT ACTIVE.  AMENDMENT 3(b): P4 fires only when ALL THREE are")
        print("      FALSIFIED (the STRONG form).  Falsified here: P1=%s P2=%s P3=%s."
              % (p1_falsified, p2_falsified, p3_falsified))
        if all_not_pass and not all_falsified:
            print("      (All three are non-PASS, which is the WEAK reading of Sec.4.5's")
            print("       'all fail'.  THAT READING IS NOT REGISTERED and P4 stays shut:")
            print("       a counter-hypothesis is adopted on strong evidence, never on")
            print("       mere non-confirmation.)")

    # ---- THE SHOCK STAGE'S OWN TOKEN.
    # AMENDMENT 3(d): when all three are FALSIFIED **and** the triple is
    # CONVERGING the stage is GATE REACHED -- the item reached and evaluated its
    # registered gate and produced a graded outcome that is NOT a band statement.
    # *** THAT IS AN INTERPRETIVE CHOICE BY A SUPERVISOR, NOT A READING OFF THE
    # DOCUMENT.  Sec.4.5 P4 gives a PROSE reading and names NONE of the six
    # tokens, while Sec.6 stage 5 requires one.  It is not PASS (no shock band
    # was met); it is not GATE FAIL (Sec.4.5 registers this exact configuration
    # as "a *result* ... not a failure of the item", and a preference does not
    # overwrite a frozen registration).  Precedent: D8R's G-O. ***
    # AMENDMENT 3(c): otherwise the stage carries the WORST of the three
    # per-prediction tokens, under the ordering of AMENDMENT 3(e).
    toks = {"P1 sharpening": res["P1"]["verdict"],
            "P2 position": res["P2"]["verdict"],
            "P3 pooled Cp": res["P3"]["verdict"]}
    if p4 and triple_converging:
        stage = emit_verdict("P1-P4 shock stage", "GATE REACHED",
                             "AMENDMENT 3(d), AN INTERPRETIVE CHOICE: all three "
                             "FALSIFIED with a CONVERGING triple is registered at "
                             "Sec.4.5 P4 as a RESULT, not a failure of the item; "
                             "the document names no token and a supervisor chose "
                             "this one")
    else:
        stage = emit_verdict("P1-P4 shock stage", compose_verdicts(toks),
                             "AMENDMENT 3(c): worst of %s"
                             % ", ".join("%s = %s" % (k, toks[k]) for k in sorted(toks)))
    res["stage_verdict"] = stage
    report["shock"] = res
    return res


# =====================================================================
# 6.  PLANTED-ZERO CONTROLS  (CLAUDE.md rule 3; PREREG Sec.3.4)
# =====================================================================
# Each plants a KNOWN perturbation into a COPY of a real artifact of THIS
# family's own on-disk format, reads it back THROUGH THE REAL READER, and
# refuses if the reader cannot see it.  The originals are asserted unchanged.

def plant_cell_count(src_case, scratch):
    """owner.gz -- gzip, because this family stores owner.gz, not owner."""
    dst = os.path.join(scratch, "plant_cells")
    base = os.path.join(src_case, "constant", "polyMesh", "owner")
    src = base + ".gz" if os.path.isfile(base + ".gz") else base
    with Untouched([src], "plant_cell_count"):
        os.makedirs(os.path.join(dst, "constant", "polyMesh"), exist_ok=True)
        raw = (gzip.open(src, "rb") if src.endswith(".gz") else open(src, "rb")).read()
        true_n, _ = read_cell_count(src_case)
        newraw = raw.replace(b"nCells:%d" % true_n, b"nCells:%d" % PLANT_CELLS, 1)
        if newraw == raw:
            refuse("PLANT", "could not plant into %s -- the `nCells:%d` token was "
                            "not found to replace" % (src, true_n))
        out = os.path.join(dst, "constant", "polyMesh", "owner.gz")
        with gzip.open(out, "wb") as fh:
            fh.write(newraw)
    seen, which = read_cell_count(dst)
    return {"true": true_n, "planted": PLANT_CELLS, "read_back": seen,
            "read_from": which, "ok": seen == PLANT_CELLS}


def plant_patch_faces(src_case, scratch):
    """constant/polyMesh/boundary -- plain text on this family."""
    dst = os.path.join(scratch, "plant_faces")
    base = os.path.join(src_case, "constant", "polyMesh", "boundary")
    src = base + ".gz" if os.path.isfile(base + ".gz") else base
    with Untouched([src], "plant_patch_faces"):
        os.makedirs(os.path.join(dst, "constant", "polyMesh"), exist_ok=True)
        raw = (gzip.open(src, "rb") if src.endswith(".gz") else open(src, "rb")).read()
        pat, _ = read_patches(src_case)
        true_f = pat["wing"][1]
        newraw = raw.replace(b"nFaces          %d" % true_f,
                             b"nFaces          %d" % PLANT_FACES, 1)
        if newraw == raw:
            newraw = re.sub(rb"nFaces\s+%d" % true_f,
                            b"nFaces          %d" % PLANT_FACES, raw, count=1)
        if newraw == raw:
            refuse("PLANT", "could not plant into %s" % src)
        out = os.path.join(dst, "constant", "polyMesh", "boundary")
        with open(out, "wb") as fh:
            fh.write(newraw)
    pat2, which = read_patches(dst)
    seen = pat2["wing"][1]
    return {"true": true_f, "planted": PLANT_FACES, "read_back": seen,
            "read_from": which, "ok": seen == PLANT_FACES}


def plant_cgns(src_cgns, scratch):
    """Perturb ONE coordinate double in a COPY of the ADF file and prove the
    coordinate reader sees it.  This is the control for G-SYS limbs 3/4/5 --
    the limbs an md5 is forbidden to stand in for (PREREG Sec.3.1)."""
    dst = os.path.join(scratch, "plant_" + os.path.basename(src_cgns))
    with Untouched([src_cgns], "plant_cgns"):
        shutil.copy2(src_cgns, dst)
        a = ADF(dst)
        root = a.node(a.b.find(b"NoDeADF MotherNode"))
        target = None
        for _bn, bo in a.children(root):
            bn2 = a.node(bo)
            if bn2["label"] != "CGNSBase_t":
                continue
            for _zn, zo in a.children(bn2):
                z = a.node(zo)
                if z["label"] != "Zone_t":
                    continue
                for _gn, go in a.children(z):
                    g = a.node(go)
                    if g["label"] != "GridCoordinates_t":
                        continue
                    for cn, co in a.children(g):
                        if cn == "CoordinateY":
                            target = a.node(co)
                            break
                    if target:
                        break
                if target:
                    break
            if target:
                break
        if target is None:
            refuse("PLANT", "%s: no CoordinateY DataArray_t to plant into" % dst)
        off = target["dptr"] + 16
        buf = bytearray(open(dst, "rb").read())
        old = struct.unpack("<d", bytes(buf[off:off + 8]))[0]
        new = old + PLANT
        buf[off:off + 8] = struct.pack("<d", new)
        with open(dst, "wb") as fh:
            fh.write(bytes(buf))
    before = read_surface_points(src_cgns)
    after = read_surface_points(dst)
    diffs = sum(1 for u, v in zip(before, after) if u != v)
    delta = max(abs(v[1] - u[1]) for u, v in zip(before, after)) if before else 0.0
    return {"planted": PLANT, "points_changed": diffs, "max_dy_seen": delta,
            "ok": diffs == 1 and abs(delta - PLANT) < 1e-12,
            "bbox_before": bbox(before), "bbox_after": bbox(after)}


def plant_log_functional(src_log, scratch, func="CD"):
    """Plant a KNOWN excursion into a COPY of a real solver log and prove the
    CD:/CL: reader -- the one G-PLAT depends on -- sees it."""
    dst = os.path.join(scratch, "plant_%s_%s" % (func, os.path.basename(src_log)))
    with Untouched([src_log], "plant_log_functional"):
        txt = open(src_log, errors="replace").read()
        base = read_log(src_log)
        if len(base[func]) < REG_PLAT_WINDOW:
            refuse("PLANT", "%s has only %d %s samples -- too few to plant a "
                            "window control into" % (src_log, len(base[func]), func))
        lines = txt.split("\n")
        idx = [i for i, l in enumerate(lines) if l.startswith(func + ":")]
        tgt = idx[-REG_PLAT_WINDOW // 2]
        v = float(lines[tgt].split()[1])
        lines[tgt] = "%s: %.17g final: %.17g" % (func, v + PLANT, v + PLANT)
        open(dst, "w").write("\n".join(lines))
    got = read_log(dst)
    p2p_before = peak_to_peak(base[func][-REG_PLAT_WINDOW:])
    p2p_after = peak_to_peak(got[func][-REG_PLAT_WINDOW:])
    return {"planted": PLANT, "n_samples_before": len(base[func]),
            "n_samples_after": len(got[func]),
            "p2p_before": p2p_before, "p2p_after": p2p_after,
            "ok": (len(got[func]) == len(base[func])) and (p2p_after >= 0.9 * PLANT)}


def plant_initres(src_log, scratch):
    """N-D44 control.  Plant a SMALL initRes beside a LARGE finalRes on the last
    step and prove the reader returns the SMALL one -- i.e. that it reads
    initRes and is structurally incapable of returning finalRes."""
    dst = os.path.join(scratch, "plant_initres_" + os.path.basename(src_log))
    with Untouched([src_log], "plant_initres"):
        lines = open(src_log, errors="replace").read().split("\n")
        idx = [i for i, l in enumerate(lines) if re.match(r"^p initRes:", l)]
        if not idx:
            refuse("PLANT", "%s: no `p initRes:` line to plant into" % src_log)
        lines[idx[-1]] = "p initRes: %.17g finalRes: %.17g nIters: 2" % (PLANT * 1e-9, 9.99)
        open(dst, "w").write("\n".join(lines))
    got = read_log(dst)
    seen = got["last_initRes"].get("p")
    return {"planted_initRes": PLANT * 1e-9, "decoy_finalRes": 9.99,
            "read_back": seen,
            "ok": seen is not None and abs(seen - PLANT * 1e-9) < 1e-24}


# =====================================================================
# 7.  DRIVER
# =====================================================================

def level_dir(args, lv):
    return {"L3": args.l3, "L2": args.l2, "L1": args.l1}[lv]


def find_log(case_root, name):
    if name:
        p = os.path.join(case_root, name)
        if not os.path.isfile(p):
            refuse("READ", "named solver log not found: %s" % p)
        return p
    cands = sorted(glob.glob(os.path.join(case_root, "log*")) +
                   glob.glob(os.path.join(case_root, "*.log")))
    if not cands:
        refuse("READ", "%s: no solver log found (looked for log* and *.log).  "
                       "Refusing rather than grading an absent history." % case_root)
    if len(cands) > 1:
        refuse("READ", "%s: %d candidate solver logs -- name one with --log-name. "
                       "Picking one by glob order is a coin flip and this "
                       "comparator does not guess.\n    %s"
               % (case_root, len(cands), "\n    ".join(cands)))
    return cands[0]


def cmd_grade(args):
    report = {"prereg": PREREG_PATH, "prereg_commit": PREREG_COMMIT,
              "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print("=" * 78)
    print("A3GC COMPARATOR (DRAFT) -- grading path for %s" % PREREG_PATH)
    print("pre-registration commit %s" % PREREG_COMMIT)
    print("=" * 78)

    cells, faces, surfaces, logs = {}, {}, {}, {}
    for lv in LEVELS:
        root = level_dir(args, lv)
        if not root:
            refuse("ARGS", "level %s has no run root (--%s)" % (lv, lv.lower()))
        n, which = read_cell_count(root)
        cells[lv] = n
        pat, bwhich = read_patches(root)
        if "wing" not in pat:
            refuse("READ", "%s: no `wing` patch in %s" % (root, bwhich))
        faces[lv] = pat["wing"][1]
        print("  %s  %-52s cells=%d  wing nFaces=%d  (from %s)"
              % (lv, root, n, faces[lv], os.path.basename(which)))
        # Sec.3.2 assertion carried here: no empty/wedge patch on any level
        for nm, (ty, nf) in sorted(pat.items()):
            if ty in ("empty", "wedge"):
                refuse("G-MESH", "%s: patch `%s` has type `%s` (PREREG Sec.3.2: "
                                 "no patch of type empty or wedge on any level)"
                       % (root, nm, ty))
        s = args.surfaces.get(lv) if args.surfaces else None
        if not s:
            s = os.path.join(root, "surfaceMesh.cgns")
        if not os.path.isfile(s):
            refuse("READ", "%s: surface CGNS not found at %s.  Sec.3.1 limb 3 is a "
                           "COORDINATE comparison and cannot be run without it; "
                           "substituting an md5 is forbidden by Sec.3.1." % (lv, s))
        surfaces[lv] = read_surface_points(s)
        report.setdefault("surface_files", {})[lv] = s

    gate_g_sys(surfaces, cells, faces, report)

    launch_epoch = None
    if args.launch_epoch:
        launch_epoch = float(args.launch_epoch)
    if args.cold:
        for lv in LEVELS:
            gate_g_cold(level_dir(args, lv), launch_epoch, report)
    else:
        print("\n--- G-COLD: not requested (--cold).  Sec.3.3 runs it AT LAUNCH, "
              "per level, before the solver starts. ---")

    res_ok, complete_ok = {}, {}
    hist = {"CD": {}, "CL": {}}
    for lv in LEVELS:
        root = level_dir(args, lv)
        lp = find_log(root, args.log_name)
        logs[lv] = read_log(lp)
        print("\n===== %s : %s =====" % (lv, lp))
        floor = gate_g_tol(logs[lv], report)
        res_ok[lv] = gate_g_res(logs[lv], floor, report)
        # PREREG Sec.3.7 / CLAUDE.md rule 4 -- ALL of it, or the level is
        # NOT A RESULT.  This runs BEFORE G-PLAT deliberately: a truncated log
        # has a perfectly plateaued tail, so G-PLAT must never be the only thing
        # standing between a dead solve and a CONVERGING verdict.
        complete_ok[lv] = gate_g_complete(root, logs[lv], lv, report)
        for f in REG_PLAT_FUNCTIONALS:
            hist[f][lv] = logs[lv][f]
            if not logs[lv][f]:
                refuse("READ", "%s: read ZERO `%s:` lines out of %s.  AMENDMENT 1(a) "
                               "registers the solver's own log as the source of the "
                               "functional history; a zero here is a reader failure, "
                               "not a measurement." % (lv, f, lp))

    # ---- G-PLAT needs the level-to-level differences, so the final values first
    finals = {f: {lv: hist[f][lv][-1] for lv in LEVELS} for f in REG_PLAT_FUNCTIONALS}
    print("\n--- G-PLAT  (AMENDMENT 1(a)) ---")
    print("  Statistic: PEAK-TO-PEAK max-min over the last %d printed samples." % REG_PLAT_WINDOW)
    print("  An adjacent-sample delta is REFUSED BY NAME (see peak_to_peak()).")
    plat_ok = {}
    for f in REG_PLAT_FUNCTIONALS:
        d32 = finals[f]["L3"] - finals[f]["L2"]
        d21 = finals[f]["L2"] - finals[f]["L1"]
        # PINNED BY AMENDMENT 2(c): the binding difference is
        #     min(|f_L3 - f_L2|, |f_L2 - f_L1|)
        # -- the conservative reading, because the smaller difference is the one
        # iterative noise can swamp and the one Richardson extrapolation rests
        # on.  THIS IS THE REGISTRATION'S CHOICE, NOT THE COMPARATOR'S.
        binding = min(abs(d32), abs(d21))
        print("  %s: level-to-level diffs |L3-L2| = %.6e, |L2-L1| = %.6e "
              "-> binding = min(...) = %.6e  [PINNED, AMENDMENT 2(c)]"
              % (f, abs(d32), abs(d21), binding))
        allok = True
        for lv in LEVELS:
            ok, _v = gate_g_plat(hist[f][lv], binding, report, lv, f)
            allok &= ok
        plat_ok[f] = allok

    print("\n--- G-TRIPLE  (standing rule 5 / PREREG Sec.4.2, applied in order) ---")
    verdicts = {}
    for f in REG_PLAT_FUNCTIONALS:
        all_res_ok = all(res_ok[lv] for lv in LEVELS)
        all_complete = all(complete_ok[lv] for lv in LEVELS)
        verdicts[f] = gate_g_triple(f, finals[f], plat_ok[f], all_res_ok,
                                    all_complete, report)

    # Both triples and both orders printed beside any NOT A RESULT (clause 2)
    if any(v == "NOT A RESULT" for v in verdicts.values()):
        print("\n  BOTH TRIPLES AND BOTH ORDERS, printed beside the NOT A RESULT "
              "(standing rule 5 clause 2):")
        for f in REG_PLAT_FUNCTIONALS:
            r = report["triples"][f]
            print("    %s: L3=%.8g L2=%.8g L1=%.8g  class=%s  p=%s"
                  % (f, r["values"]["L3"], r["values"]["L2"], r["values"]["L1"],
                     r["class"], ("%.4f" % r["p"]) if r["p"] is not None else "n/a"))

    # ---- Sec.4.4 FALSIFIER
    if verdicts["CD"] == "NOT A RESULT":
        print("\n  Sec.4.4 FALSIFIER: the CD triple is not CONVERGING.  A3GC is "
              "REFUTED, and the honest statement is that a surface-refined family "
              "did not deliver a convergent primal on this case either -- a "
              "finding about the CASE, not about the family.  It is NOT repaired "
              "by adding a level, widening the band, or dropping the coarse level.")

    # ---- shock  (PREREG Sec.4.5; Sec.6 stage 5)
    #
    # *** DEFECT A, FOUND BY THE dafoam-supervisor 2026-09-11 AND REPAIRED HERE. ***
    # NEITHER branch below used to write into `verdicts`, and the composed line
    # was taken over CD and CL ONLY.  The observed consequence, on the clean
    # triple: "VERDICT  P1-P4 shock : PENDING" followed by "VERDICT  A3GC
    # OVERALL : PASS".  A registered stage that produced NO GRADED EVIDENCE left
    # the item standing at PASS.
    #
    # Sec.6 stage 5 registers the grading path as "Roache order applied (Sec.4.2);
    # GCI at Fs=1.25; SHOCK PREDICTIONS P1-P4 EVALUATED", and AMENDMENT 2's
    # closing paragraph preserves it verbatim ("Sec.4.5's P1-P4 ... stand exactly
    # as registered").  P1-P4 evaluation is therefore a REGISTERED STAGE of the
    # grading path, not an optional extra, and CLAUDE.md rule 1 fixes PENDING as
    # "not yet run" and forbids it softening anything.  The PENDING branch is
    # consequently entered into the composition, where it cannot produce a PASS.
    if args.vtp_l3 and args.vtp_l1:
        wd3 = os.path.join(args.scratch, "shock_L3")
        wd1 = os.path.join(args.scratch, "shock_L1")
        _c3, s3 = run_shock_chain(args.vtp_l3, wd3, args.logs_a3)
        c1, s1 = run_shock_chain(args.vtp_l1, wd1, args.logs_a3)
        # Sec.4.5 P4 is conditioned on "the CD/CL triple being CONVERGING".
        # MEASURED HERE from the classifier's own output, never inferred from a
        # verdict token (a triple can be NOT A RESULT for a clause-1 reason while
        # still classifying CONVERGING, and vice versa).
        classes = {f: report["triples"][f]["class"] for f in REG_PLAT_FUNCTIONALS}
        triple_converging = all(c == "CONVERGING" for c in classes.values())
        print("\n  Sec.4.5 P4 precondition: CD class = %s, CL class = %s "
              "-> triple CONVERGING = %s"
              % (classes["CD"], classes["CL"], triple_converging))
        sres = evaluate_shock({str(k): v for k, v in s3.items()},
                              {str(k): v for k, v in s1.items()}, c1, report,
                              triple_converging)
        verdicts["P1-P4 shock"] = sres["stage_verdict"]
    else:
        print("\n--- SHOCK P1-P4 ---")
        verdicts["P1-P4 shock"] = emit_verdict(
            "P1-P4 shock", "PENDING",
            "no surface VTK supplied (--vtp-l3 / --vtp-l1); the archived "
            "comparator path has not been re-run.  Sec.6 stage 5 registers this "
            "evaluation as part of the grading path, so the item is NOT GRADED")

    # ---- overall
    print("\n" + "=" * 78)
    # AMENDMENT 3(e) REGISTERS THIS COMPOSITION.  Before it, the document
    # registered none -- the string "overall" did not occur in it at all -- and
    # this comparator REFUSED [COMPOSE-UNREGISTERED] rather than choose one.
    # That refusal is now RESOLVED, not removed: the rule it waited for exists.
    #
    #   NOT A RESULT < GATE FAIL < BLOCKED < PENDING < GATE REACHED < PASS
    #
    # IT IS NOT A GATE AND REGISTERS NO THRESHOLD -- it is the six tokens ranked
    # by how little evidence each carries, every clause forced by a standing rule
    # (see VERDICT_SEVERITY above for the per-clause citations).
    #
    # CONSEQUENCE, registered at AMENDMENT 3(e) before it could embarrass anyone:
    # Sec.6 stage 5 registers P1-P4 evaluation as part of the grading path, so
    # WHILE THE SHOCK STAGE IS UN-EVALUATED THE ITEM IS PENDING AND CANNOT BE
    # PASS, however well the CD and CL triples grade.
    overall = compose_verdicts(verdicts)
    emit_verdict("A3GC OVERALL", overall,
                 "composed worst-first over %s"
                 % ", ".join("%s = %s" % (k, verdicts[k]) for k in sorted(verdicts)))
    print("=" * 78)
    report["verdicts"] = verdicts
    report["overall"] = overall
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(report, fh, indent=1, default=str)
        print("wrote %s" % args.json)
    return EXIT_OK if overall == "PASS" else EXIT_VERDICT_NOT_PASS


def cmd_plant(args):
    """Run every planted-zero control and print a machine-readable block."""
    os.makedirs(args.scratch, exist_ok=True)
    out = {}
    if args.case:
        out["cell_count"] = plant_cell_count(args.case, args.scratch)
        out["patch_faces"] = plant_patch_faces(args.case, args.scratch)
    if args.cgns:
        out["cgns_coords"] = plant_cgns(args.cgns, args.scratch)
    if args.log:
        out["log_CD"] = plant_log_functional(args.log, args.scratch, "CD")
        out["log_CL"] = plant_log_functional(args.log, args.scratch, "CL")
        out["initres_ND44"] = plant_initres(args.log, args.scratch)
    print(json.dumps(out, indent=1, default=str))
    bad = [k for k, v in out.items() if isinstance(v, dict) and not v.get("ok")]
    if not out:
        refuse("PLANT", "no plant target given -- nothing was controlled")
    if bad:
        refuse("PLANT", "the reader could not see the planted perturbation in: %s. "
                        "A zero from a reader not shown able to see a non-zero is "
                        "not evidence (CLAUDE.md rule 3)." % ", ".join(bad))
    print("ALL PLANTED CONTROLS SEEN")
    return EXIT_OK


def cmd_plat(args):
    """Run G-PLAT alone on one log against a supplied level-to-level difference.
    Used by the mutation controls in the selftest."""
    log = read_log(args.log)
    hist = log[args.func]
    if not hist:
        refuse("READ", "%s: ZERO `%s:` samples" % (args.log, args.func))
    report = {}
    print("--- G-PLAT standalone: %s  %s  (%d samples) ---"
          % (args.log, args.func, len(hist)))
    ok, verdict = gate_g_plat(hist, args.diff, report, args.level, args.func)
    emit_verdict("G-PLAT %s %s" % (args.level, args.func),
                 "PASS" if ok else "NOT A RESULT")
    return EXIT_OK if ok else EXIT_VERDICT_NOT_PASS


def cmd_cold(args):
    """Run G-COLD alone on one case root.  Used by the mutation controls."""
    report = {}
    gate_g_cold(args.case, float(args.launch_epoch) if args.launch_epoch else None, report)
    emit_verdict("G-COLD %s" % args.case, "GATE REACHED", "clean cold start")
    return EXIT_OK


def cmd_shock(args):
    """Drive `evaluate_shock()` from SUPPLIED JSON, in the exact shape the
    archived logs_A3 chain writes (`shock_location.json`, `cp_comparison.json`).

    WHY THIS EXISTS, stated so nobody mistakes it for a convenience.  P1-P4 read
    Cp from SOLVED SURFACE FIELDS.  **No solved field and no surface VTK exists
    for any A3GC level**, so the archived chain cannot be run and the whole of
    AMENDMENT 3(a)-(d) would otherwise sit in a code path NOTHING CAN DRIVE --
    which is exactly where DEFECT B lived.  This makes the prediction logic
    inspectable and controllable without inventing a solve.

    *** ANY JSON HANDED TO THIS SUBCOMMAND IS AN INPUT, NOT A MEASUREMENT.  It
    renders NO LAB RESULT and NOTHING it prints may be quoted as one. ***
    """
    def load(p, what):
        if not os.path.isfile(p):
            refuse("SHOCK", "%s not found: %s" % (what, p))
        with open(p) as fh:
            d = json.load(fh)
        if not d:
            refuse("SHOCK", "%s read EMPTY from %s.  A zero from a reader not "
                            "shown able to see a non-zero is not evidence "
                            "(CLAUDE.md rule 3)." % (what, p))
        return d
    print("=" * 78)
    print("A3GC SHOCK PREDICTION LOGIC, DRIVEN FROM SUPPLIED JSON.")
    print("*** THE INPUTS BELOW ARE INPUTS, NOT MEASUREMENTS.  evaluate_shock has")
    print("    NEVER RUN AGAINST REAL VTK -- none exists for any A3GC level. ***")
    print("=" * 78)
    report = {}
    res = evaluate_shock(load(args.shock_l3, "shock_location.json for L3"),
                         load(args.shock_l1, "shock_location.json for L1"),
                         load(args.cmp_l1, "cp_comparison.json for L1"),
                         report, args.triple_converging)
    return EXIT_OK if res["stage_verdict"] == "PASS" else EXIT_VERDICT_NOT_PASS


def cmd_compose(args):
    """Drive `compose_verdicts()` directly, with no solve and no fixture.

    This is NOT a test-only backdoor: it is the composition rule made
    INSPECTABLE from the command line, which is the only way a reader can check
    the ordering over tokens the grading path does not happen to produce today.
    DEFECT B was exactly that -- an ordering over three of six tokens, sitting
    in a code path nothing drove.

    `--census` drives EVERY token in the fixed vocabulary through the ordering,
    singly and paired against PASS, and prints the composed result for each.
    """
    if args.census:
        print("--- VERDICT_SEVERITY census: every token in the fixed vocabulary ---")
        print("  ordering (worst-first): %s" % " < ".join(VERDICT_SEVERITY))
        for t in VERDICTS:
            solo = compose_verdicts({"only": t})
            pair = compose_verdicts({"other": "PASS", "only": t})
            print("  token %-13s solo -> %-13s  beside a PASS -> %s" % (t, solo, pair))
            if solo != t:
                refuse("COMPOSE", "composing the single token %r returned %r"
                       % (t, solo))
            if pair != t:
                refuse("COMPOSE", "token %r beside a PASS composed to %r; every "
                                  "token in the vocabulary is at least as severe "
                                  "as PASS" % (t, pair))
        print("  every one of the %d tokens composed without raising." % len(VERDICTS))
        return EXIT_OK
    items = {}
    for spec in (args.gate or []):
        if "=" not in spec:
            refuse("ARGS", "--gate wants LABEL=TOKEN, got %r" % spec)
        lab, tok = spec.split("=", 1)
        items[lab.strip()] = tok.strip()
    overall = compose_verdicts(items)
    for lab in sorted(items):
        print("  gate %-28s : %s" % (lab, items[lab]))
    emit_verdict("COMPOSED", overall, "worst-first over %d gate(s)" % len(items))
    return EXIT_OK if overall == "PASS" else EXIT_VERDICT_NOT_PASS


def cmd_probe(args):
    """Dump the measured quantities for one run root, for the selftest."""
    out = {}
    n, which = read_cell_count(args.case)
    out["cells"] = n
    out["cells_read_from"] = which
    pat, bw = read_patches(args.case)
    out["patches"] = {k: {"type": v[0], "nFaces": v[1]} for k, v in pat.items()}
    out["patches_read_from"] = bw
    if args.cgns:
        p = read_surface_points(args.cgns)
        out["cgns_points"] = len(p)
        out["cgns_bbox"] = bbox(p)
    print(json.dumps(out, indent=1, default=str))
    return EXIT_OK


def main(argv=None):
    ap = argparse.ArgumentParser(description="A3GC comparator (FROZEN 2026-09-11)")
    sub = ap.add_subparsers(dest="cmd")

    g = sub.add_parser("grade")
    g.add_argument("--l3", required=True)
    g.add_argument("--l2", required=True)
    g.add_argument("--l1", required=True)
    g.add_argument("--surface-l3"); g.add_argument("--surface-l2"); g.add_argument("--surface-l1")
    g.add_argument("--log-name", default=None)
    g.add_argument("--cold", action="store_true")
    g.add_argument("--launch-epoch", default=None)
    g.add_argument("--vtp-l3"); g.add_argument("--vtp-l1")
    g.add_argument("--logs-a3", default=LOGS_A3)
    g.add_argument("--scratch", default=os.path.join(tempfile.gettempdir(), "a3gc_scratch"))
    g.add_argument("--json", default=None)

    p = sub.add_parser("plant")
    p.add_argument("--case"); p.add_argument("--cgns"); p.add_argument("--log")
    p.add_argument("--scratch", required=True)

    q = sub.add_parser("plat")
    q.add_argument("--log", required=True)
    q.add_argument("--func", default="CD", choices=list(REG_PLAT_FUNCTIONALS))
    q.add_argument("--diff", type=float, required=True)
    q.add_argument("--level", default="Lx")

    c = sub.add_parser("cold")
    c.add_argument("--case", required=True)
    c.add_argument("--launch-epoch", default=None)

    r = sub.add_parser("probe")
    r.add_argument("--case", required=True)
    r.add_argument("--cgns")

    k = sub.add_parser("shock")
    k.add_argument("--shock-l3", required=True)
    k.add_argument("--shock-l1", required=True)
    k.add_argument("--cmp-l1", required=True)
    k.add_argument("--triple-converging", dest="triple_converging",
                   action="store_true", default=None,
                   help="Sec.4.5 P4's precondition, stated explicitly")
    k.add_argument("--triple-not-converging", dest="triple_converging",
                   action="store_false",
                   help="the other half of the P4 precondition")

    m = sub.add_parser("compose")
    m.add_argument("--gate", action="append",
                   help="LABEL=TOKEN, repeatable")
    m.add_argument("--census", action="store_true",
                   help="drive every token of the fixed vocabulary through the "
                        "ordering and print the composed result for each")

    a = ap.parse_args(argv)
    # L-332, on EVERY invocation and in both interpreter modes: this file must
    # carry zero `assert` statements, and it counts its own rather than trusting
    # a reader elsewhere.  It refuses to run if it finds one.
    guard_no_asserts()
    if a.cmd == "grade":
        a.surfaces = {"L3": a.surface_l3, "L2": a.surface_l2, "L1": a.surface_l1}
        os.makedirs(a.scratch, exist_ok=True)
        return cmd_grade(a)
    if a.cmd == "plant":
        return cmd_plant(a)
    if a.cmd == "plat":
        return cmd_plat(a)
    if a.cmd == "cold":
        return cmd_cold(a)
    if a.cmd == "probe":
        return cmd_probe(a)
    if a.cmd == "compose":
        return cmd_compose(a)
    if a.cmd == "shock":
        if a.triple_converging is None:
            refuse("ARGS", "name the Sec.4.5 P4 precondition explicitly: "
                           "--triple-converging or --triple-not-converging.  P4 "
                           "is conditioned on it and the comparator will not "
                           "assume it either way.")
        return cmd_shock(a)
    ap.print_help()
    return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main())
