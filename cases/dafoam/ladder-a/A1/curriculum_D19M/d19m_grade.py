#!/usr/bin/env python3
r"""Curriculum D19M -- THE FROZEN COMPARATOR.  Reads artefacts; runs no solver.

    d19m_grade.py --root <run root> --out <grade json>
    d19m_grade.py --selftest

===========================================================================
I. THE ONE SENTENCE THIS ITEM CANNOT SUPPORT, ENFORCED IN CODE
===========================================================================
**THIS ITEM CAN NEVER PUBLISH `PASS`.**  Not on either row, not at item level,
whatever every gate returns.  `VERDICT_CEILING = "GATE REACHED"` is applied by
`_apply_ceiling()` as the LAST step of composition, and `G-PROV` REFUSES (exit 2)
if the ceiling has been removed or widened.

The reason is `DAFOAM_CHARTER.md` section 1, this lab's own bright line:

  > *A DAFoam gradient is not a result until a finite-difference table stands
  > beside it at a step proved to lie in the plateau.*

**THE COMPRESSIBLE SINGLE-POINT GRADIENT HAS NO GRADED VERDICT AT ALL, AND ITS
PLATEAU DID NOT CLOSE.**  Both re-measured at this freeze:

  * `CURRICULUM-D19R` phase 1 ran clean -- `MESH X2 S8 N2 S1 R1` all rc=0,
    chain_rc 0, 12.416 core-min -- and **its grader REFUSED, rc=2, emitting no
    verdict**.  Its successor `CURRICULUM-D19R2`'s grading attempt 1 also
    returned **NOT A RESULT** (refusal `G19R-1h`).
  * `.../CURRICULUM-D19R-.../d19r_selected_step.json`: `all_two_sided = false`,
    `score_pct = 21.060684242435336`, `binding = ["shape[7]", "CD", "fine"]`.

So an optimisation on this ground inherits an **UNVERIFIED GRADIENT**.  It is
still worth buying -- the optimiser is the only instrument that can say whether
the compressible adjoint DRIVES A DESCENT on this case, and nothing else on the
ladder answers that -- but its headline verdict must not imply a plateau that
did not close.  The ceiling is how that is enforced rather than asked for.

===========================================================================
II. `shape[7]` IS A REGISTERED NON-RESULT, AND IT IS NOT RESCUABLE
===========================================================================
`G-PLAT7` sets `shape[7]/CD` to `NOT A RESULT` **from the registered list in
`d19m_xf.EXCLUDED_FROM_AGGREGATE`, never from the measured value.**  At s* on
D19R's own np=1 arm it agrees with the adjoint to **1.65155 %** -- INSIDE the
5 % band -- and it is excluded anyway, because what is missing is not agreement
but the PROOF that the estimate at s* is trustworthy, and that proof is the
plateau.  A selftest leg drives a `shape[7]` row that PASSES every band and
requires the gate to return `NOT A RESULT` regardless.

Its reading is PUBLISHED beside the aggregate, never instead of it
(`DAFOAM_CHARTER.md` section 3), and the aggregate's own key is named
`aggregate_pct_excl_flagged` so no reader can take it for an all-component one.

===========================================================================
III. WHAT THIS COMPARATOR REFUSES, AND WHAT IT MERELY GRADES
===========================================================================
**A REFUSAL IS `NOT A RESULT`, NEVER A DEGRADED VERDICT, AND IT EXITS 2.**
It refuses on a MALFORMED artefact and on a broken provenance.  It **NEVER**
refuses on an ABSENT one: D6 registered a chain stop as a meaningful outcome and
its grader refused with ZERO gate readings because one arm carried no ledger row,
leaving 2,257.933 core-min of real optimisation behind an instrument that could
not read it (L-322).  Here an absent arm is a **census reading** that `G-STAGES`
gates on, and every arm that ran is graded.

**NO `assert` STATEMENT APPEARS ANYWHERE IN THIS FILE.**  `python3 -O` strips
them, so an assert is not a guard (L-332).  `count_asserts()` proves it and is
itself proved against a planted assert.

**NO KEY IS FOUND BY A RECURSIVE HUNT.**  Every nested location is an explicit
path.  A reader that goes looking until it finds something will always find
something.

**`GCI` / Roache triple gating: NO GRID TRIPLE IS REGISTERED.**  This is a
single-grid optimisation on A1's own 4,032-cell mesh.  `CLAUDE.md` rule 5 has no
row to act on here, and this comparator says so rather than leaving a reader to
infer it from an absence.
"""
import argparse
import ast
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d19m_xf as XF                                              # noqa: E402
import d19m_age_guard as AGE                                      # noqa: E402
import d19m_stall as STALL                                        # noqa: E402

ITEM = "D19M"
VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# ---- THE CEILING.  See the module docstring, part I. -------------------------
VERDICT_CEILING = "GATE REACHED"
CEILING_REASON = (
    "The compressible single-point gradient this optimisation spends has NO "
    "GRADED VERDICT (D19R's grader refused rc=2; D19R2 grading attempt 1 = NOT A "
    "RESULT) and its plateau did NOT close (all_two_sided=false, "
    "score_pct=21.060684242435336, binding=[shape[7],CD,fine]).  "
    "DAFOAM_CHARTER.md section 1: a gradient is not a result until an FD table "
    "stands beside it at a step PROVED to lie in the plateau.  This item "
    "therefore cannot publish PASS on any row or at item level, whatever its "
    "gates return.  REGISTERED BEFORE THE RUN.")

# ---- the declared program ----------------------------------------------------
ARMS_DECLARED = ["MESH", "O-S", "XE-S", "FE-S", "O-P", "XE-P", "FE-P"]
N_DECLARED = len(ARMS_DECLARED)
ARM_ROW = {"MESH": "SHIPPED", "O-S": "SHIPPED", "XE-S": "SHIPPED", "FE-S": "SHIPPED",
           "O-P": "PATCHED", "XE-P": "PATCHED", "FE-P": "PATCHED"}
ARM_RANKS = {a: 1 for a in ARMS_DECLARED}          # np = 1 ON EVERY ARM
ARM_KIND = {"MESH": "SCRIPT", "O-S": "O", "O-P": "O",
            "XE-S": "XE", "XE-P": "XE", "FE-S": "FE", "FE-P": "FE"}
TERMINAL = {"O": "D19M_O_WRITTEN", "XE": "D19M_X_WRITTEN", "FE": "D19M_F_WRITTEN"}
ARTEFACT = {"O": "d19m_O.json", "XE": "d19m_X.json", "FE": "d19m_F.json"}

# ---- THE REGISTERED CAP TABLE (PREREGISTRATION.md section 12) -----------------
# Caps are CEILINGS.  Predictions are ESTIMATES.  They are different numbers and
# the rule-12 ratio is taken against the PREDICTION, never against the cap.
CAPS = {"MESH": 5.0, "O-S": 40.0, "O-P": 40.0,
        "XE-S": 12.0, "XE-P": 12.0, "FE-S": 20.0, "FE-P": 20.0}
PREDICTED_CORE_MIN = {"MESH": 0.20, "O-S": 8.64, "O-P": 8.64,
                      "XE-S": 2.60, "XE-P": 2.60, "FE-S": 5.71, "FE-P": 5.71}
ITEM_CEILING_CORE_MIN = sum(CAPS.values())         # ASSERTED as the sum, never restated
CAP_MARGIN_S = 180                                 # the C-188 cap frame
RATE_USD_PER_CORE_H = 0.0513
COST_BASIS = ("c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER 2026-08-21/22, "
              "NOT MEASURED -- this box cannot read its own billing "
              "(COMPUTE_BUDGET_CHARTER.md section 5).  Core-minutes ARE measured, "
              "from this item's own ledger rows (wall_s x ranks / 60).")

# ---- registered placement and toolchain --------------------------------------
CPUSET_REGISTERED = "13"
MESH_CELLS = 4032
DIGEST = {"PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35",
          "SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"}
SO_MD5 = {"PATCHED": "85f59e87253e0a71a813f64ca6e4c425",
          "SHIPPED": "f0fcb488e0e98156575cd19548e91663"}

# ---- the registered intermediate threshold (DAFOAM_CHARTER.md section 9) ------
# A cap-stopped or stall-stopped optimiser is GATE REACHED only where this was
# met; otherwise NOT A RESULT.  Never PASS, and never described by the size of
# the improvement it reached.
MIN_WEIGHTED_DRAG_REDUCTION_PCT = 2.0
# THREE graded components, not D19O's four: this item has FOUR components
# (patchV is not a DV here) of which shape[7] is the registered non-result.
MIN_GRADED_COMPONENTS = 3
# G-ALPHA: the operating points read BACK through the model must equal the
# registered ones. A scenario silently wired to the wrong angle would produce a
# gradient against a flow condition nobody registered, and every band would pass.
ALPHAS_REGISTERED = [2.787333582, 4.787333582, 6.787333582]
ALPHA_ABS_TOL = 1.0e-12
WEIGHTS_REGISTERED = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
MP_STRUCT_RTOL = 1.0e-10
MIN_MAJORS_TO_HAVE_SEARCHED = 5

# ---- the travelling provenance (G-PROV) --------------------------------------
# Every link is read on disk at grade time.  An item verdict that leans on an
# upstream reading carries that reading with it or it publishes nothing.
PROV_CHAIN = [
    {"link": "CURRICULUM-D19R",
     "relation": "DIRECT -- the compressible FD plateau sweep this optimisation's "
                 "step and components come from",
     "item_verdict": "NOT A RESULT",
     "why": "its grader REFUSED rc=2 and emitted no verdict",
     "basis": "/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-"
              "plateau/d19r_selected_step.json",
     "must_contain": '"all_two_sided": false'},
    {"link": "CURRICULUM-D19R2",
     "relation": "INHERITED -- the re-grade built to give D19R a verdict",
     "item_verdict": "NOT A RESULT",
     "why": "grading attempt 1 refused at G19R-1h (MANIFEST_ENTRY_MUTATED on "
            "system/decomposeParDict, an np>1 artefact); no grade JSON written",
     "basis": os.path.join(HERE, "..", "curriculum_D19R2", "RESULTS.md"),
     "must_contain": "NOT A RESULT"},
]

FATAL_TOKENS = ("Traceback (most recent call last)", "MPI_ABORT", "Segmentation fault",
                "std::bad_alloc", "PETSC ERROR", "Killed")
# G-NOOPT: an explicit list of names, never a substring sweep.
OPTIMISER_EVIDENCE = ("opt_IPOPT.txt", "OptView.hst", "opt_SNOPT_print.txt", "opt_SLSQP.txt")

# ---- THE LIVE PLANTED-ZERO CONTROLS (CLAUDE.md rule 3) ----------------------
# Sanaa, 2026-08-28: no instrument grades anything until *"was THIS reader ever
# shown able to see a non-zero THROUGH THE REAL CODE PATH?"* is answered YES,
# demonstrated.  A selftest on fixtures proves the code COULD see a plant at
# build time; these controls answer the different question rule 3 actually asks —
# **was this reader, on THIS run root, against THESE files, shown able to see a
# non-zero?**  A green suite is a result about the comparator; a plant read back
# from the actual run root is a result about the reading.
PLANT_NUM = 1.234e-03          # additive, onto every derivative
PLANT_CELLS_OFFSET = 7         # offset FROM DISK, never a fixed constant
PLANT_FATAL = "Traceback (most recent call last)"     # a REAL member of FATAL_TOKENS
PLANT_MARKER = "opt_IPOPT.txt"                        # a REAL member of OPTIMISER_EVIDENCE
PLANT_EXIT = "EXIT: Optimal Solution Found."

# ---- THE BIRTH REGISTER -----------------------------------------------------
# Every reader that produces a graded number, with what it feeds and whether the
# hazard it carries is that A ZERO PASSES A GATE.
READERS = {
    "R1_read_ledger": {
        "produces": "core_min, rc, ranks, cpuset, digest -> G1/G9/G10/G12/G-NP",
        "producer": "d19m_run_arm.sh:d19m_ledger_row", "zero_passes_a_gate": False},
    "R2_read_fatal_tokens": {
        "produces": "fatal-token list -> G1  (**READS A ZERO AS A PASS**)",
        "producer": "the arm shell / OpenFOAM / DAFoam, via <ARM>_*.log",
        "zero_passes_a_gate": True},
    "R2b_read_benign_counts": {
        "produces": "benign line counts -> REPORTED, NEVER GATED",
        "producer": "OpenFOAM, via <ARM>_*.log", "zero_passes_a_gate": False},
    "R3_read_mesh_cells": {
        "produces": "cell count -> G-M2", "producer": "checkMesh, via MESH/checkMesh.log",
        "zero_passes_a_gate": False},
    "R4_read_optimiser_evidence": {
        "produces": "optimiser marker list -> G-NOOPT-ENDPOINT  (**READS A ZERO AS A PASS**)",
        "producer": "pyOptSparse/IPOPT, via the endpoint arm directory",
        "zero_passes_a_gate": True},
    "R5_read_X": {
        "produces": "adjoint totals -> G5_fd, G-TB  (CAN PASS ON A SMALL NUMBER)",
        "producer": "d19m_xf.py mode XE", "zero_passes_a_gate": True},
    "R6_read_F": {
        "produces": "FD derivative table -> G5_fd, G-TB, G-PLAT7",
        "producer": "d19m_xf.build_fd_step / row_from_fd / build_ctrl_row",
        "zero_passes_a_gate": True},
    "R7_read_ipopt": {
        "produces": "convergence statement, rows, stall -> G-OPT9",
        "producer": "IPOPT, via <arm>/opt_IPOPT.txt", "zero_passes_a_gate": True},
    "R8_read_alphas": {
        "produces": "the three operating points read back -> G-ALPHA  (**READS AN "
                    "EMPTY LIST AS ... nothing, which is why G-ALPHA fails closed "
                    "on it**)",
        "producer": "d19m_xf.py read_alphas, from the model itself",
        "zero_passes_a_gate": True},
}
# Benign lines that are COUNTED AND NAMED, never silently suppressed.  A
# suppression a reader cannot see is the same defect wearing the other hat.
BENIGN = {"simple_no_criteria": "SIMPLE: no convergence criteria found",
          "continuity_errors": "time step continuity errors",
          "trapfpe_notice": "trapFpe:"}

_LEDGER = re.compile(
    r"^ARM=(?P<arm>\S+)\s+ROW=(?P<row>\S+)\s+IMG=(?P<img>\S+)\s+DIGEST=(?P<digest>\S+)\s+"
    r"rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall>\d+)\s+ranks=(?P<ranks>\d+)\s+"
    r"core_min=(?P<core_min>[0-9.]+)\s+cap_core_min=(?P<cap>[0-9.]+).*?"
    r"cpuset=(?P<cpuset>\S+)", re.M)


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def count_asserts(path):
    """L-332: `python3 -O` strips `assert`, so an assert is not a guard.  This
    counts them in a file.  It is itself proved against a PLANTED assert in the
    selftest -- a zero from a reader never shown a non-zero is not evidence."""
    return sum(1 for n in ast.walk(ast.parse(open(path).read()))
               if isinstance(n, ast.Assert))


def dig(doc, path, default=None):
    """An EXPLICIT tuple path.  Never a recursive hunt."""
    cur = doc
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        elif isinstance(cur, list) and isinstance(k, int) and 0 <= k < len(cur):
            cur = cur[k]
        else:
            return default
    return cur


def _f(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


# ============================================================================
# READERS
# ============================================================================
def read_ledger(root):
    p = os.path.join(root, "ledger.txt")
    if not os.path.isfile(p):
        return {}, []
    text = open(p, errors="replace").read()
    rows = {}
    order = []
    for m in _LEDGER.finditer(text):
        arm = m.group("arm")
        rows[arm] = {"arm": arm, "row": m.group("row"), "image": m.group("img"),
                     "digest": m.group("digest"), "rc": int(m.group("rc")),
                     "wall_s": int(m.group("wall")), "ranks": int(m.group("ranks")),
                     "core_min": _f(m.group("core_min")), "cap": _f(m.group("cap")),
                     "cpuset": m.group("cpuset")}
        order.append(arm)
    # the .so md5 the LOADING PROCESS printed, per arm
    for arm in rows:
        rows[arm]["so_md5"] = None
    for line in text.splitlines():
        m = re.match(r"^D19M_G9_(OK|REFUSE) arm=(\S+).*?libidwarp_so_md5=(\S+)", line)
        if m and m.group(2) in rows:
            rows[m.group(2)]["so_md5"] = m.group(3)
    return rows, order


def read_arm_log(root, arm):
    """The newest `<ARM>_*.log`, by name.  Deterministic, not a glob race."""
    cands = sorted(f for f in os.listdir(root)
                   if f.startswith(arm + "_") and f.endswith(".log"))
    if not cands:
        return None, ""
    p = os.path.join(root, cands[-1])
    return p, open(p, errors="replace").read()


# ---------------------------------------------------------------------------
# THE NAMED READERS.  Every reader that produces a graded number is a FUNCTION
# with a name, so the live planted-zero controls below can call THE REAL ONE
# rather than re-implementing it.  A control that re-implements its reader can
# agree with itself while disagreeing with the instrument.
# ---------------------------------------------------------------------------
def read_mesh_cells(path):
    """R3 -> G-M2."""
    if not os.path.isfile(path):
        return None
    m = re.search(r"^\s*cells:\s*(\d+)\s*$", open(path, errors="replace").read(), re.M)
    return int(m.group(1)) if m else None


def read_fatal_tokens(text):
    """R2 -> G1.  **READS A ZERO AS A PASS.**  A reader that silently matches
    nothing returns the same empty list as a clean run, and every gate behind it
    stays green.  That is why it carries a live control."""
    low = text.lower()
    return [t for t in FATAL_TOKENS if t.lower() in low]


def read_benign_counts(text):
    """R2b -> REPORTED, NEVER GATED."""
    low = text.lower()
    return {k: low.count(v.lower()) for k, v in BENIGN.items()}


def read_optimiser_evidence(arm_dir, doc):
    """R4 -> G-NOOPT-ENDPOINT.  **READS A ZERO AS A PASS**, same hazard as R2."""
    seen = [ev for ev in OPTIMISER_EVIDENCE
            if os.path.exists(os.path.join(arm_dir, ev))]
    if doc is not None and doc.get("no_optimiser_ran") is not True:
        seen.append("artefact_does_not_declare:no_optimiser_ran")
    return seen


def read_X(path):
    """R5 -> G5_fd, G-TB, G-MP-STRUCT.  The MULTIPOINT adjoint: dJ/dshape, the
    three dCD_i/dshape and the three dCL_i/dshape, all over the SHARED vector."""
    doc = json.load(open(path))
    a = doc.get("adjoint") or {}
    out = {"J": [_f(v) for v in (a.get("J") or [])],
           "CD": [[_f(v) for v in arr] for arr in (a.get("CD") or [])],
           "CL": [[_f(v) for v in arr] for arr in (a.get("CL") or [])]}
    return out


def read_F(path):
    """R6 -> G5_fd, G-TB, G-PLAT7.  The MULTIPOINT FD table: dJ and the three
    dCL_i per step.  CTRL is excluded -- it is the instrument's own control row,
    not a derivative."""
    doc = json.load(open(path))
    out = {}
    for r in doc.get("rows", []):
        if r.get("status") != "MEASURED":
            continue
        vals = {}
        for st, v in (r.get("fd") or {}).items():
            if v.get("ok"):
                vals[st] = {"dJ": _f(v.get("dJ")),
                            "dCL": [_f(x) for x in (v.get("dCL") or [])]}
        out[(r.get("dv"), r.get("idx"))] = vals
    return out


def read_alphas(path):
    """R8 -> G-ALPHA.  The operating points read BACK out of the artefact, on
    both of the producer's read paths."""
    doc = json.load(open(path))
    return doc.get("alphas_read_back") or []


def read_ipopt(path):
    """R7 -> G-OPT9.  The optimiser's own words, through the frozen detector."""
    return STALL.read_log(path)


def load_artefact(root, arm):
    """Returns (doc, path) or (None, path).  An ABSENT artefact is a CENSUS
    reading and returns None; a MALFORMED one REFUSES."""
    kind = ARM_KIND[arm]
    if kind == "SCRIPT":
        return None, None
    p = os.path.join(root, arm, ARTEFACT[kind])
    if not os.path.isfile(p):
        return None, p
    try:
        return json.load(open(p)), p
    except Exception as exc:                                      # noqa: BLE001
        refuse("ARTEFACT_MALFORMED", {"path": p, "error": repr(exc)[:300]})


# ============================================================================
# THE LIVE PLANTED-ZERO CONTROLS
#
# Each one: plants a known perturbation into a COPY under `grader_controls/`,
# reads it back FROM DISK THROUGH THE REAL READER FUNCTION (imported and called,
# never re-implemented), and REFUSES (exit 2) if the plant is not recovered.
#
# EVERY ONE CARRIES A DEGENERACY ARM.  A control whose unplanted value already
# equals its planted value has demonstrated nothing — it would report itself
# exercised while the reader was blind.  So each control reads the UNPLANTED
# artefact first and refuses if the two already agree.
#
# WHERE THE TARGET COMES FROM.  A control prefers the REAL artefact on this run
# root.  Where the arm did not run, the target is built by the INSTRUMENT'S OWN
# WRITERS (`d19m_xf.build_fd_row` / `build_ctrl_row`) or from the launcher's own
# terminal strings, and the register records which it was — `target_kind`
# `REAL` or `WRITER_BUILT`.  A reader must be born either way; what changes is
# only what it was born against, and that is stated rather than blurred.
# ============================================================================
def _plant_dir(root):
    d = os.path.join(root, "grader_controls")
    os.makedirs(d, exist_ok=True)
    return d


def _first_arm_with(root, arms_ran, kinds):
    for a in ARMS_DECLARED:
        if a in arms_ran and ARM_KIND[a] in kinds:
            return a
    return None


def ctrl_ledger(root):
    """R1's birth.  Bump one arm's `core_min` and require the real ledger reader
    to read the changed number back off disk."""
    src = os.path.join(root, "ledger.txt")
    if not os.path.isfile(src):
        refuse("CONTROL", {"ctrl_ledger_no_target": src})
    text = open(src, errors="replace").read()
    before, _ = read_ledger(root)
    if not before:
        refuse("CONTROL", {"ctrl_ledger_reader_saw_no_rows": src,
                           "note": "the reader must be born against a row it can see"})
    arm = sorted(before)[0]
    was = before[arm]["core_min"]
    want = round((was or 0.0) + PLANT_NUM, 6)
    planted = re.sub(r"(^ARM=%s .*?core_min=)[0-9.]+" % re.escape(arm),
                     r"\g<1>%s" % want, text, count=1, flags=re.M)
    if planted == text:
        refuse("CONTROL", {"ctrl_ledger_no_substitution": {"arm": arm, "was": was}})
    cd = os.path.join(_plant_dir(root), "ledger_planted")
    os.makedirs(cd, exist_ok=True)
    with open(os.path.join(cd, "ledger.txt"), "w") as fh:
        fh.write(planted)
    after, _ = read_ledger(cd)
    got = (after.get(arm) or {}).get("core_min")
    if got is None or abs(got - want) > 1e-9:
        refuse("CONTROL", {"ctrl_ledger_not_seen": {"arm": arm, "want": want, "read_back": got}})
    if was is not None and abs(was - want) < 1e-12:
        refuse("CONTROL", {"ctrl_ledger_DEGENERATE": {"unplanted": was, "planted": want}})
    return {"seen": True, "reader": "read_ledger", "target_kind": "REAL", "arm": arm,
            "unplanted": was, "planted": want, "read_back": got, "file": cd}


def ctrl_mesh_cells(root):
    """R3's birth.  The cells reader must read a DIFFERENT number off a changed
    real `checkMesh.log`, not merely the expected one off the real log."""
    src = os.path.join(root, "MESH", "checkMesh.log")
    kind = "REAL"
    if not os.path.isfile(src):
        kind = "WRITER_BUILT"
        src = os.path.join(_plant_dir(root), "checkMesh_source.log")
        with open(src, "w") as fh:
            fh.write("    cells:            %d\n" % MESH_CELLS)
    was = read_mesh_cells(src)
    if was is None:
        refuse("CONTROL", {"ctrl_mesh_no_target": src,
                           "note": "the plant must land on bytes the reader reads"})
    want = was + PLANT_CELLS_OFFSET          # OFFSET FROM DISK, never a constant
    txt = open(src, errors="replace").read()
    planted = re.sub(r"^(\s*cells:\s*)\d+\s*$", r"\g<1>%d" % want, txt, count=1, flags=re.M)
    if planted == txt:
        refuse("CONTROL", {"ctrl_mesh_no_substitution": src})
    cp = os.path.join(_plant_dir(root), "checkMesh_planted.log")
    with open(cp, "w") as fh:
        fh.write(planted)
    got = read_mesh_cells(cp)
    if got != want:
        refuse("CONTROL", {"ctrl_mesh_not_seen": {"read_back": got, "want": want}})
    if got == was:
        refuse("CONTROL", {"ctrl_mesh_DEGENERATE": {"unplanted": was, "planted": got}})
    return {"seen": True, "reader": "read_mesh_cells", "target_kind": kind,
            "unplanted": was, "planted": want, "read_back": got, "file": cp}


def ctrl_fatal_tokens(root, arms_ran):
    """R2's birth, AND IT IS THE ONE THAT MATTERS MOST.  This reader passes a
    gate on an EMPTY list, so a silently-broken matcher returns exactly what a
    clean run returns.  Both directions are driven: the unplanted log must read
    CLEAN, and the same log with a real fatal token appended must read DIRTY."""
    arm = sorted(arms_ran)[0] if arms_ran else None
    kind, text = "REAL", ""
    if arm:
        _p, text = read_arm_log(root, arm)
    if not text:
        kind, arm = "WRITER_BUILT", arm or "MESH"
        text = ("D4S_IDWARP_SO_MD5: %s\nSIMPLE: no convergence criteria found\n"
                "D19M_MESH_IDENTITY_ALL_OK\n" % SO_MD5["SHIPPED"])
    before = read_fatal_tokens(text)
    planted_text = text + "\n" + PLANT_FATAL + "\n"
    cp = os.path.join(_plant_dir(root), "fatal_planted_%s.log" % arm)
    with open(cp, "w") as fh:
        fh.write(planted_text)
    after = read_fatal_tokens(open(cp, errors="replace").read())
    if PLANT_FATAL not in after:
        refuse("CONTROL", {"ctrl_fatal_not_seen": {"planted": PLANT_FATAL, "read_back": after,
                           "note": "the fatal-token reader cannot see a fatal token; every "
                                   "G1 PASS behind it would be a zero from a blind reader"}})
    if before == after:
        refuse("CONTROL", {"ctrl_fatal_DEGENERATE": {"unplanted": before, "planted": after}})
    return {"seen": True, "reader": "read_fatal_tokens", "target_kind": kind, "arm": arm,
            "unplanted": before, "planted": after, "zero_passes_a_gate": True, "file": cp}


def ctrl_optimiser_evidence(root, arms_ran):
    """R4's birth.  Same hazard as R2: this reader passes `G-NOOPT-ENDPOINT` on an
    EMPTY list.  The unplanted endpoint directory must read CLEAN and the same
    directory with a real marker present must read DIRTY."""
    arm = _first_arm_with(root, arms_ran, ("XE", "FE"))
    kind = "REAL"
    if arm:
        src_dir = os.path.join(root, arm)
        doc, _ = load_artefact(root, arm)
    else:
        kind, arm = "WRITER_BUILT", "FE-P"
        src_dir = os.path.join(_plant_dir(root), "noopt_source")
        os.makedirs(src_dir, exist_ok=True)
        doc = {"no_optimiser_ran": True}
    before = read_optimiser_evidence(src_dir, doc)
    cd = os.path.join(_plant_dir(root), "noopt_planted_%s" % arm)
    os.makedirs(cd, exist_ok=True)
    with open(os.path.join(cd, PLANT_MARKER), "w") as fh:
        fh.write("planted by the grader's own control; not an optimiser run\n")
    after = read_optimiser_evidence(cd, doc)
    if PLANT_MARKER not in after:
        refuse("CONTROL", {"ctrl_optmarker_not_seen": {"planted": PLANT_MARKER,
                           "read_back": after,
                           "note": "the optimiser-marker reader cannot see a marker; every "
                                   "G-NOOPT-ENDPOINT PASS behind it would be a blind zero"}})
    if before == after:
        refuse("CONTROL", {"ctrl_optmarker_DEGENERATE": {"unplanted": before, "planted": after}})
    # The SECOND direction of the same reader: the artefact's own declaration.
    undeclared = read_optimiser_evidence(src_dir, {"no_optimiser_ran": False})
    if "artefact_does_not_declare:no_optimiser_ran" not in undeclared:
        refuse("CONTROL", {"ctrl_optmarker_declaration_leg_failed": undeclared})
    return {"seen": True, "reader": "read_optimiser_evidence", "target_kind": kind,
            "arm": arm, "unplanted": before, "planted": after,
            "declaration_leg": undeclared, "zero_passes_a_gate": True, "file": cd}


def ctrl_X(root, arms_ran):
    """R5's birth.  Add PLANT_NUM to every adjoint component -- `J`, all three
    `CD` and all three `CL` -- re-read FROM DISK through the real reader, and
    require every value to have moved by exactly PLANT_NUM."""
    arm = _first_arm_with(root, arms_ran, ("XE",))
    kind = "REAL"
    if arm:
        src = os.path.join(root, arm, ARTEFACT["XE"])
        doc = json.load(open(src))
    else:
        kind, arm = "WRITER_BUILT", "XE-P"
        n = 8
        doc = {"adjoint": {
            "J": [repr(1.0e-2 * (i + 1)) for i in range(n)],
            "CD": [[repr(1.0e-2 * (i + 1) + 0.001 * j) for i in range(n)]
                   for j in range(len(XF.SCENARIOS))],
            "CL": [[repr(1.0 + i + j) for i in range(n)]
                   for j in range(len(XF.SCENARIOS))]}}
        src = os.path.join(_plant_dir(root), "X_source.json")
        with open(src, "w") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True)
    before = read_X(src)
    # A READER THAT RETURNS A BROKEN SHAPE MUST REFUSE, NOT CRASH.  A KeyError
    # here would be an uncaught traceback where the contract says exit 2, and a
    # crash is not a verdict.
    for k in ("J", "CD", "CL"):
        if k not in before:
            refuse("CONTROL", {"ctrl_X_reader_shape_broken":
                               {"missing_key": k, "got_keys": sorted(before)}})
    if not before["J"]:
        refuse("CONTROL", {"ctrl_X_reader_saw_no_J": src,
                           "note": "the adjoint reader must be born against a J "
                                   "array it can see"})
    j = json.loads(json.dumps(doc))
    j["adjoint"]["J"] = [repr(float(v) + PLANT_NUM) for v in j["adjoint"]["J"]]
    for of in ("CD", "CL"):
        j["adjoint"][of] = [[repr(float(v) + PLANT_NUM) for v in arr]
                            for arr in j["adjoint"][of]]
    cp = os.path.join(_plant_dir(root), "X_%s_planted.json" % arm)
    with open(cp, "w") as fh:
        json.dump(j, fh, indent=1, sort_keys=True)
    after = read_X(cp)
    worst, n = 0.0, 0
    for k, a0 in enumerate(before["J"]):
        b0 = after["J"][k]
        worst = max(worst, abs((b0 - a0) - PLANT_NUM)); n += 1
    for of in ("CD", "CL"):
        for i, arr in enumerate(before[of]):
            for k, a0 in enumerate(arr):
                b0 = after[of][i][k]
                worst = max(worst, abs((b0 - a0) - PLANT_NUM)); n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"ctrl_X_not_seen": {"n_values": n, "worst_residual": worst,
                                               "plant": PLANT_NUM}})
    return {"seen": True, "reader": "read_X", "target_kind": kind, "arm": arm,
            "n_values": n, "worst_residual": worst, "plant": PLANT_NUM, "file": cp}


def ctrl_F(root, arms_ran):
    """R6's birth.  Add PLANT_NUM to every `dJ` and every `dCL_i` at every step --
    including the trivial-baseline step -- re-read FROM DISK through the real
    reader, and require every value to have moved by exactly PLANT_NUM."""
    arm = _first_arm_with(root, arms_ran, ("FE",))
    kind = "REAL"
    if arm:
        src = os.path.join(root, arm, ARTEFACT["FE"])
        doc = json.load(open(src))
    else:
        kind, arm = "WRITER_BUILT", "FE-P"
        rows = []
        for dv, idx in XF.COMPONENTS:
            per = {}
            for st in list(XF.FD_STEPS_ENDPOINT[dv]) + [XF.TB_STEP]:
                per[st] = (0.0146 + 1e-3 * st, 0.0146 - 1e-3 * st,
                           [0.42 + st * (i + 1) for i in range(len(XF.SCENARIOS))],
                           [0.42 - st * (i + 1) for i in range(len(XF.SCENARIOS))])
            rows.append(XF.build_fd_row(dv, idx, per))         # THE REAL WRITER
        rows.append(XF.build_ctrl_row(0.0146, [0.42] * len(XF.SCENARIOS)))
        doc = {"rows": rows, "n_rows": len(rows)}
        src = os.path.join(_plant_dir(root), "F_source.json")
        with open(src, "w") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True)
    before = read_F(src)
    if not before:
        refuse("CONTROL", {"ctrl_F_reader_saw_no_rows": src,
                           "note": "the FD reader must be born against a row it can see"})
    j = json.loads(json.dumps(doc))
    for r in j.get("rows", []):
        if r.get("dv") == "CTRL" or r.get("status") != "MEASURED":
            continue
        for v in (r.get("fd") or {}).values():
            if v.get("ok"):
                v["dJ"] = repr(float(v["dJ"]) + PLANT_NUM)
                v["dCL"] = [repr(float(x) + PLANT_NUM) for x in v["dCL"]]
    cp = os.path.join(_plant_dir(root), "F_%s_planted.json" % arm)
    with open(cp, "w") as fh:
        json.dump(j, fh, indent=1, sort_keys=True)
    after = read_F(cp)
    worst, n, tb = 0.0, 0, 0
    for key, steps in before.items():
        for st, v in steps.items():
            b0 = (after.get(key) or {}).get(st)
            if b0 is None:
                refuse("CONTROL", {"ctrl_F_key_lost": {"key": list(key), "step": st}})
            worst = max(worst, abs((b0["dJ"] - v["dJ"]) - PLANT_NUM)); n += 1
            for i, x in enumerate(v["dCL"]):
                worst = max(worst, abs((b0["dCL"][i] - x) - PLANT_NUM)); n += 1
            if abs(float(st) - XF.TB_STEP) < 1e-30:
                tb += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"ctrl_F_not_seen": {"n_values": n, "worst_residual": worst,
                                               "plant": PLANT_NUM}})
    if tb == 0:
        refuse("CONTROL", {"ctrl_F_trivial_baseline_not_traversed":
                           {"note": "the control must reach the steps G-TB grades, "
                                    "or G-TB's reader is unborn"}})
    return {"seen": True, "reader": "read_F", "target_kind": kind, "arm": arm,
            "n_values": n, "n_trivial_baseline_values": tb,
            "worst_residual": worst, "plant": PLANT_NUM, "file": cp}


def ctrl_alphas(root, arms_ran):
    """R8's birth.  G-ALPHA is the one gate a multipoint item can pass blind: if
    the reader returns an empty list the gate has nothing to compare, and if it
    returned the REGISTERED values regardless of the artefact it would pass on a
    scenario wired to the wrong angle.  Both are driven."""
    arm = None
    for a in ARMS_DECLARED:
        if a in arms_ran and ARM_KIND[a] in ("O", "XE", "FE"):
            arm = a
            break
    kind = "REAL"
    if arm:
        _doc, src = load_artefact(root, arm)
    else:
        kind, arm = "WRITER_BUILT", "O-P"
        src = os.path.join(_plant_dir(root), "alphas_source.json")
        with open(src, "w") as fh:
            json.dump({"alphas_read_back": [
                {"scenario": sc, "registered": ALPHAS_REGISTERED[i],
                 "read_dvs": ALPHAS_REGISTERED[i], "read_scenario": ALPHAS_REGISTERED[i]}
                for i, sc in enumerate(XF.SCENARIOS)]}, fh, indent=1, sort_keys=True)
    before = read_alphas(src)
    if not before:
        refuse("CONTROL", {"ctrl_alphas_reader_saw_nothing": src,
                           "note": "G-ALPHA's reader must be born against a list it "
                                   "can see, or its PASS is a blind zero"})
    doc = json.load(open(src))
    j = json.loads(json.dumps(doc))
    j["alphas_read_back"][0]["read_dvs"] = \
        float(j["alphas_read_back"][0]["read_dvs"]) + 1.0        # a whole degree off
    cp = os.path.join(_plant_dir(root), "alphas_%s_planted.json" % arm)
    with open(cp, "w") as fh:
        json.dump(j, fh, indent=1, sort_keys=True)
    after = read_alphas(cp)
    if after[0]["read_dvs"] == before[0]["read_dvs"]:
        refuse("CONTROL", {"ctrl_alphas_not_seen":
                           {"before": before[0], "after": after[0],
                            "note": "the reader cannot see a one-degree change in an "
                                    "operating point"}})
    if before == after:
        refuse("CONTROL", {"ctrl_alphas_DEGENERATE": {"before": before, "after": after}})
    return {"seen": True, "reader": "read_alphas", "target_kind": kind, "arm": arm,
            "n_points": len(before), "unplanted_first": before[0].get("read_dvs"),
            "planted_first": after[0].get("read_dvs"), "plant_deg": 1.0, "file": cp}


def ctrl_ipopt(root, arms_ran):
    """R7's birth, BOTH DIRECTIONS.  `converged: False` is what a broken parser
    returns AND what an unconverged run returns, so the reader is required to
    return True on bytes that carry the statement and False on bytes that do
    not — on the same log."""
    arm = _first_arm_with(root, arms_ran, ("O",))
    kind = "REAL"
    src = os.path.join(root, arm, "opt_IPOPT.txt") if arm else None
    if not (src and os.path.isfile(src)):
        kind, arm = "WRITER_BUILT", arm or "O-P"
        src = os.path.join(_plant_dir(root), "ipopt_source.txt")
        with open(src, "w") as fh:
            fh.write("iter objective inf_pr inf_du lg(mu) ||d|| lg(rg) alpha_du alpha_pr ls\n")
            for i in range(12):
                fh.write(" %3d  1.0e-02 1.00e-06 %8.2e  -5.0 1.00e-03  -1.0 1.00e+00 "
                         "1.00e+00  1\n" % (i, 10.0 ** (-i - 1)))
    text = open(src, errors="replace").read()
    # BOTH LEGS ARE BUILT FROM THE SAME STRIPPED BYTES, and that is not a detail.
    # Planting onto the ORIGINAL text left any pre-existing `EXIT:` line in place,
    # and `_EXIT.search` takes the FIRST match — so on a log already ending
    # `EXIT: Maximum Number of Iterations Exceeded.` the positive leg read that
    # line instead of the plant and the control refused a working reader.  Caught
    # by driving it; the two legs must differ in the plant and in NOTHING ELSE.
    stripped = "\n".join(l for l in text.splitlines() if not l.startswith("EXIT:")) + "\n"
    # NEGATIVE leg: the statement stripped out -> the reader must say NOT converged.
    neg = os.path.join(_plant_dir(root), "ipopt_%s_stripped.txt" % arm)
    with open(neg, "w") as fh:
        fh.write(stripped)
    r_neg = read_ipopt(neg)
    if r_neg["convergence"]["converged"]:
        refuse("CONTROL", {"ctrl_ipopt_negative_leg_failed":
                           {"note": "the reader reports CONVERGED on bytes carrying no EXIT "
                                    "line -- this is the A2 failure, where a table that simply "
                                    "stops was read as a result"}})
    # POSITIVE leg: the SAME bytes plus the statement -> the reader must SEE it.
    pos = os.path.join(_plant_dir(root), "ipopt_%s_planted.txt" % arm)
    with open(pos, "w") as fh:
        fh.write(stripped.rstrip("\n") + "\n" + PLANT_EXIT + "\n")
    r_pos = read_ipopt(pos)
    if not r_pos["convergence"]["converged"]:
        refuse("CONTROL", {"ctrl_ipopt_positive_leg_failed":
                           {"planted": PLANT_EXIT, "read_back": r_pos["convergence"],
                            "note": "the reader cannot see the optimiser's own convergence "
                                    "statement; every G-OPT9 reading behind it is blind"}})
    if r_neg["n_rows"] == 0:
        refuse("CONTROL", {"ctrl_ipopt_no_rows_parsed":
                           {"note": "the row reader saw zero rows; G-OPT9's major count and "
                                    "the stall detector would both be reading a blind zero"}})
    if r_neg["convergence"]["converged"] == r_pos["convergence"]["converged"]:
        refuse("CONTROL", {"ctrl_ipopt_DEGENERATE":
                           {"stripped": r_neg["convergence"], "planted": r_pos["convergence"]}})
    return {"seen": True, "reader": "read_ipopt", "target_kind": kind, "arm": arm,
            "negative_leg_converged": r_neg["convergence"]["converged"],
            "positive_leg_converged": r_pos["convergence"]["converged"],
            "rows_parsed": r_neg["n_rows"], "files": [neg, pos]}


def run_live_controls(root, arms_ran):
    """Every control, on THIS run root.  Any failure REFUSES (exit 2) before a
    single gate is composed — a comparator whose readers are not shown able to
    see a non-zero grades nothing."""
    c = {}
    c["R1_read_ledger"] = ctrl_ledger(root)
    c["R2_read_fatal_tokens"] = ctrl_fatal_tokens(root, arms_ran)
    c["R2b_read_benign_counts"] = ctrl_benign(root, arms_ran)
    c["R3_read_mesh_cells"] = ctrl_mesh_cells(root)
    c["R4_read_optimiser_evidence"] = ctrl_optimiser_evidence(root, arms_ran)
    c["R5_read_X"] = ctrl_X(root, arms_ran)
    c["R6_read_F"] = ctrl_F(root, arms_ran)
    c["R7_read_ipopt"] = ctrl_ipopt(root, arms_ran)
    c["R8_read_alphas"] = ctrl_alphas(root, arms_ran)
    return c


def ctrl_benign(root, arms_ran):
    """R2b's birth.  Reported, never gated — and still born, because a benign
    count that silently reads zero would hide the very suppression the count
    exists to make visible."""
    arm = sorted(arms_ran)[0] if arms_ran else None
    kind, text = "REAL", ""
    if arm:
        _p, text = read_arm_log(root, arm)
    if not text:
        kind, arm = "WRITER_BUILT", arm or "MESH"
        text = "D19M_MESH_IDENTITY_ALL_OK\n"
    before = read_benign_counts(text)
    planted_text = text + "".join("\n%s\n" % v for v in BENIGN.values())
    cp = os.path.join(_plant_dir(root), "benign_planted_%s.log" % arm)
    with open(cp, "w") as fh:
        fh.write(planted_text)
    after = read_benign_counts(open(cp, errors="replace").read())
    missed = [k for k in BENIGN if after[k] <= before[k]]
    if missed:
        refuse("CONTROL", {"ctrl_benign_not_seen": {"missed": missed, "before": before,
                                                    "after": after}})
    return {"seen": True, "reader": "read_benign_counts", "target_kind": kind, "arm": arm,
            "unplanted": before, "planted": after}


def birth_record(controls):
    """`n_not_born` is computed FROM THE CONTROLS THAT ACTUALLY RAN on this run
    root, never from a hand-maintained flag."""
    readers = {}
    for k, v in READERS.items():
        c = controls.get(k) or {}
        readers[k] = {**v, "born": bool(c.get("seen")),
                      "born_against": c.get("target_kind"), "control": k}
    not_born = [k for k, v in readers.items() if not v["born"]]
    return {"requirement": ("Sanaa 2026-08-28: no instrument grades anything until 'was THIS "
                           "reader ever shown able to see a non-zero THROUGH THE REAL CODE "
                           "PATH?' is answered YES, demonstrated -- on THIS run root, against "
                           "THESE files, not on a fixture at build time"),
            "readers": readers, "n_readers": len(readers),
            "n_born": sum(1 for v in readers.values() if v["born"]),
            "n_not_born": len(not_born), "not_born": not_born,
            "n_readers_whose_zero_passes_a_gate":
                sum(1 for v in readers.values() if v["zero_passes_a_gate"]),
            "plant_dir": "grader_controls/",
            "note": ("The plants NEVER touch a graded artefact: every one is written to a "
                     "separate copy under grader_controls/ and the item's verdict is composed "
                     "from the unplanted bytes alone.")}


# ============================================================================
# GATES
# ============================================================================
def g_prov():
    """The travelling chain.  REFUSES (exit 2) if it cannot be read, if any link
    is missing its basis, or if the verdict ceiling has been removed."""
    if VERDICT_CEILING not in VOCAB:
        refuse("G-PROV", {"verdict_ceiling_outside_vocabulary": VERDICT_CEILING})
    if VERDICT_CEILING == "PASS":
        refuse("G-PROV", {"verdict_ceiling_widened_to_PASS": CEILING_REASON})
    links = []
    for spec in PROV_CHAIN:
        basis = os.path.abspath(spec["basis"])
        exists = os.path.isfile(basis)
        contains = False
        if exists:
            txt = open(basis, errors="replace").read()
            contains = spec["must_contain"] in txt
        if not exists or not contains:
            refuse("G-PROV", {"link": spec["link"], "basis": basis,
                              "basis_exists": exists,
                              "basis_carries_%r" % spec["must_contain"]: contains,
                              "note": "an item that leans on an upstream reading "
                                      "carries that reading or publishes nothing"})
        if spec["item_verdict"] not in VOCAB:
            refuse("G-PROV", {"link": spec["link"],
                              "verdict_outside_vocabulary": spec["item_verdict"]})
        links.append({**spec, "basis": basis, "basis_exists": True,
                      "basis_carries_marker": True})
    return {"verdict": "SATISFIED", "n_links": len(links), "links": links,
            "verdict_ceiling": VERDICT_CEILING, "ceiling_reason": CEILING_REASON}


def g_stages(ran):
    """DECLARED vs EXECUTED as a GATE INPUT, not a footnote.  W3 logged 20 blocked
    stages of 33 perfectly, in two agreeing artefacts, and nothing read them."""
    short = N_DECLARED - len(ran)
    return {"declared": N_DECLARED, "executed": len(ran), "short": short,
            "arms_declared": ARMS_DECLARED, "arms_ran": sorted(ran),
            "arms_missing": [a for a in ARMS_DECLARED if a not in ran],
            "verdict": "PASS" if short == 0 else "NOT A RESULT"}


def g_completion(root, arm, led, doc):
    """CLAUDE.md rule 4, all of it or none of it: rc = 0, terminal statement, no
    fatal token, and the AGE GUARD.  Benign lines are COUNTED AND NAMED."""
    out = {"arm": arm, "clauses": {}}
    out["clauses"]["rc_zero"] = bool(led and led["rc"] == 0)
    lp, text = read_arm_log(root, arm)
    out["log"] = os.path.basename(lp) if lp else None
    kind = ARM_KIND[arm]
    if kind == "SCRIPT":
        out["clauses"]["terminal_statement"] = bool("D19M_MESH_IDENTITY_ALL_OK" in text)
    else:
        out["clauses"]["terminal_statement"] = bool(TERMINAL[kind] in text)
        out["clauses"]["artefact_present"] = doc is not None
    hits = read_fatal_tokens(text)                        # THE NAMED READER
    out["clauses"]["no_fatal_token"] = not hits
    out["fatal_tokens_seen"] = hits
    out["benign_counts"] = read_benign_counts(text)       # THE NAMED READER
    out["_benign_note"] = ("COUNTED AND NAMED, never suppressed.  `SIMPLE: no "
                           "convergence criteria found` is OpenFOAM's banner and is "
                           "NOT evidence: DAFoam applies its own primalMinResTol.  "
                           "`trapFpe:` is an ENABLEMENT notice, not a crash.")
    # ---- the age guard --------------------------------------------------------
    ag = {"ran": False}
    mpath = os.path.join(root, arm, ".d19m_manifest.json")
    spath = AGE.sentinel_path(root, arm)
    if os.path.isfile(mpath) and os.path.isfile(spath):
        arts = [ARTEFACT[kind]] if kind != "SCRIPT" else ["checkMesh.log"]
        try:
            ev = AGE.check_arm(os.path.join(root, arm), arts, spath,
                               json.load(open(mpath)), [root])
            ag = {"ran": True, "ok": True, "evidence": ev}
        except AGE.Refusal as exc:
            d = json.loads(str(exc))
            ag = {"ran": True, "ok": False, "refusal": d}
            # THE REGISTERED FALSIFIER of the np=1 premise.  See section 5 of the
            # pre-registration: if this fires on `system/decomposeParDict`, np=1
            # did NOT prevent the D19R2 mutation, and that is a MEASUREMENT.  The
            # guard is NOT weakened after the fact.
            if (d.get("REFUSE") == "MANIFEST_ENTRY_MUTATED"
                    and "decomposeParDict" in str(d.get("detail", ""))):
                ag["np1_premise_falsified"] = True
    out["age_guard"] = ag
    out["clauses"]["age_guard"] = bool(ag.get("ok"))
    out["verdict"] = "PASS" if all(out["clauses"].values()) else "GATE FAIL"
    return out


def g_np(led_rows):
    """np = 1 on every arm.  A CONDITION ON THE INHERITANCE, not a setting."""
    bad = {a: r["ranks"] for a, r in led_rows.items() if r["ranks"] != ARM_RANKS.get(a, 1)}
    return {"registered": ARM_RANKS, "violations": bad,
            "verdict": "PASS" if not bad else "GATE FAIL",
            "why": "DAFOAM_CHARTER.md section 5 forbids carrying an FD reference "
                   "across np; A4 measured a 16,600x spread between two "
                   "decompositions of one mesh.  np=1 ALSO makes D19R2's "
                   "MANIFEST_ENTRY_MUTATED blocker unreachable, because "
                   "decomposePar never runs."}


def g9_toolchain(led_rows):
    bad = []
    for a, r in led_rows.items():
        want_row = ARM_ROW.get(a)
        if r["row"] != want_row:
            bad.append({"arm": a, "field": "row", "got": r["row"], "want": want_row})
        if r["digest"] != DIGEST.get(want_row):
            bad.append({"arm": a, "field": "digest", "got": r["digest"],
                        "want": DIGEST.get(want_row)})
        if r["so_md5"] != SO_MD5.get(want_row):
            bad.append({"arm": a, "field": "libidwarp_so_md5", "got": r["so_md5"],
                        "want": SO_MD5.get(want_row)})
    return {"registered_digests": DIGEST, "registered_so_md5": SO_MD5,
            "mismatches": bad, "verdict": "PASS" if not bad else "GATE FAIL",
            "why": "DAFOAM_CHARTER.md section 6: toolchain identity is an image "
                   "digest and a library hash, NEVER a version string.  All three "
                   "images report DAFoam 5.0.0."}


def g12_placement(led_rows):
    bad = {a: r["cpuset"] for a, r in led_rows.items() if r["cpuset"] != CPUSET_REGISTERED}
    return {"registered_cpuset": CPUSET_REGISTERED, "violations": bad,
            "verdict": "PASS" if not bad else "GATE FAIL",
            "delivered_cores_floor_composed": False,
            "_floor_note": "At np = 1 an overlapping cpuset costs wall time and "
                           "could not fail this gate, so the delivered-cores floor "
                           "is NOT COMPOSED and is registered as not composed.  The "
                           "sampler's reading is still published as a number."}


def g10_caps(led_rows):
    per, total = {}, 0.0
    over = []
    for a, r in led_rows.items():
        cm = r["core_min"] or 0.0
        total += cm
        pred = PREDICTED_CORE_MIN.get(a)
        per[a] = {"core_min": cm, "cap": CAPS.get(a), "predicted": pred,
                  "ratio_actual_over_predicted": (cm / pred) if pred else None,
                  "over_cap": bool(CAPS.get(a) is not None and cm > CAPS[a])}
        if per[a]["over_cap"]:
            over.append(a)
    # ITEM_CEILING is Sigma(CAPS), asserted here rather than restated by hand.
    ceiling_ok = abs(ITEM_CEILING_CORE_MIN - sum(CAPS.values())) < 1e-9
    if not ceiling_ok:
        refuse("G10", {"item_ceiling": ITEM_CEILING_CORE_MIN,
                       "sum_of_caps": sum(CAPS.values())})
    return {"per_arm": per, "total_core_min": round(total, 4),
            "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
            "item_point_prediction_core_min": round(sum(PREDICTED_CORE_MIN.values()), 4),
            "arms_over_cap": over,
            "total_over_ceiling": bool(total > ITEM_CEILING_CORE_MIN),
            "usd_derived_not_measured": round(total / 60.0 * RATE_USD_PER_CORE_H, 6),
            "cost_basis": COST_BASIS,
            "ratio_actual_over_predicted_item":
                round(total / sum(PREDICTED_CORE_MIN.values()), 4)
                if sum(PREDICTED_CORE_MIN.values()) else None,
            "verdict": "PASS" if (not over and total <= ITEM_CEILING_CORE_MIN)
                       else "GATE FAIL",
            "_cap_vs_prediction": "Caps are CEILINGS; predictions are ESTIMATES.  The "
                                  "rule-12 ratio is taken against the PREDICTION, "
                                  "never against the cap."}


def g_mesh(root):
    p = os.path.join(root, "MESH", "checkMesh.log")
    if not os.path.isfile(p):
        return {"verdict": "NOT A RESULT", "cells": None, "registered": MESH_CELLS,
                "note": "no checkMesh.log -- the MESH arm did not run"}
    cells = read_mesh_cells(p)                            # THE NAMED READER
    return {"cells": cells, "registered": MESH_CELLS,
            "verdict": "PASS" if cells == MESH_CELLS else "GATE FAIL"}


def g_designpoint(root, arms_ran):
    """The endpoint arms were evaluated AT THE OPTIMUM, and at THEIR OWN row's
    optimum.  `DAFOAM_CHARTER.md` section 9: the FD check is at the FINAL design
    point, not only at the baseline."""
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in arms_ran:
        kind = ARM_KIND[arm]
        if kind not in ("XE", "FE"):
            continue
        row = ARM_ROW[arm]
        o_arm = "O-S" if row == "SHIPPED" else "O-P"
        xo_p = os.path.join(root, o_arm, XF.XOPT)
        doc, _ = load_artefact(root, arm)
        rec = {"expects": xo_p, "xopt_present": os.path.isfile(xo_p)}
        if not rec["xopt_present"] or doc is None:
            rec["ok"] = False
        else:
            xo = json.load(open(xo_p))
            dp = dig(doc, ("design_point",), {})
            rec["row_match"] = (xo.get("row") == row == doc.get("row"))
            rec["shape_match"] = (dp.get("shape") == xo.get("shape"))
            rec["patchV_match"] = (dp.get("patchV") == xo.get("patchV"))
            rec["not_baseline"] = any(_f(v, 0.0) != 0.0 for v in (dp.get("shape") or []))
            rec["ok"] = bool(rec["row_match"] and rec["shape_match"] and rec["patchV_match"])
            rec["_not_baseline_note"] = (
                "`not_baseline` is REPORTED, NEVER GATED: an optimiser that "
                "legitimately converges at the baseline would otherwise be failed "
                "for succeeding.  What IS gated is that the endpoint arm read its "
                "OWN row's d19m_xopt.json and used those exact bytes.")
        out["per_arm"][arm] = rec
        if not rec.get("ok"):
            out["verdict"] = "GATE FAIL"
    return out


def g_noopt_endpoint(root, arms_ran):
    """No optimiser ran in an endpoint arm.  An `opt_IPOPT.txt` under XE/FE means
    the endpoint moved, and the gradient would not be at the point it names."""
    bad = []
    for arm in arms_ran:
        if ARM_KIND[arm] not in ("XE", "FE"):
            continue
        doc, _ = load_artefact(root, arm)
        for ev in read_optimiser_evidence(os.path.join(root, arm), doc):   # THE NAMED READER
            bad.append({"arm": arm, "optimiser_evidence": ev})
    return {"violations": bad, "verdict": "PASS" if not bad else "GATE FAIL",
            "_zero_passes_this_gate": "read_optimiser_evidence returns an EMPTY list for a "
                                      "clean endpoint arm AND for a reader that matches "
                                      "nothing.  Its live control (R4) is what separates "
                                      "the two, and it REFUSES exit 2 if the reader is blind."}


def g_evalfail(root, arms_ran):
    """A failed evaluation is WRITTEN, not omitted.  An F arm that silently writes
    fewer rows and calls itself complete is what this gate exists to catch."""
    out = {"per_arm": {}, "verdict": "PASS"}
    n_comp = len(XF.COMPONENTS)
    n_steps = len(XF.FD_STEPS_ENDPOINT["shape"]) + 1        # + the trivial baseline
    declared_expected = n_comp * n_steps * 2 + 2            # + baseline and repeat
    out["evals_declared_expected"] = declared_expected
    out["primals_per_evaluation"] = len(XF.SCENARIOS)
    out["primals_expected"] = declared_expected * len(XF.SCENARIOS)
    out["_census_arithmetic"] = ("%d components x %d steps (3 decade + 1 trivial "
                                 "baseline) x 2 signs + 2 baselines = %d "
                                 "EVALUATIONS, each of which is %d primals (one per "
                                 "operating point) = %d primals per FE arm"
                                 % (n_comp, n_steps, declared_expected,
                                    len(XF.SCENARIOS),
                                    declared_expected * len(XF.SCENARIOS)))
    for arm in arms_ran:
        if ARM_KIND[arm] != "FE":
            continue
        doc, _ = load_artefact(root, arm)
        if doc is None:
            out["per_arm"][arm] = {"artefact": "ABSENT"}
            continue
        d = doc.get("evaluations_declared")
        rec = {"declared": d, "failed": doc.get("evaluations_failed"),
               "failures": doc.get("evaluation_failures"),
               "matches_census": (d == declared_expected)}
        out["per_arm"][arm] = rec
        if not rec["matches_census"]:
            out["verdict"] = "GATE FAIL"
    return out


def g_opt9(root, row, arms_ran):
    """`DAFOAM_CHARTER.md` section 9, per row.

    PASS is reachable from this gate ONLY where IPOPT printed its OWN convergence
    statement.  It is then still capped by `_apply_ceiling`.  A cap-, budget- or
    stall-stopped run is GATE REACHED where the registered intermediate threshold
    was met and NOT A RESULT otherwise -- never PASS, and never described by the
    size of the improvement it reached."""
    arm = "O-S" if row == "SHIPPED" else "O-P"
    if arm not in arms_ran:
        return {"arm": arm, "verdict": "NOT A RESULT", "why": "arm did not run"}
    doc, _ = load_artefact(root, arm)
    if doc is None:
        return {"arm": arm, "verdict": "NOT A RESULT", "why": "no d19m_O.json"}
    printed = doc.get("ipopt_printed_convergence") is True
    exit_text = doc.get("ipopt_exit")
    rows_n = doc.get("ipopt_table_rows") or 0
    red = _f(doc.get("weighted_drag_reduction_pct"))
    stall = doc.get("stall") or {}
    stalled = bool(stall.get("A"))
    met = bool(red is not None and red >= MIN_WEIGHTED_DRAG_REDUCTION_PCT
               and rows_n >= MIN_MAJORS_TO_HAVE_SEARCHED)
    if printed:
        verdict = "PASS"
        why = "IPOPT printed its OWN convergence statement: %r" % exit_text
    elif met:
        verdict = "GATE REACHED"
        why = ("stopped without a convergence statement (exit=%r, stall_A=%s) and the "
               "REGISTERED intermediate threshold was met: %.4f %% >= %.1f %% over "
               "%d majors >= %d" % (exit_text, stalled, red, MIN_WEIGHTED_DRAG_REDUCTION_PCT,
                                    rows_n, MIN_MAJORS_TO_HAVE_SEARCHED))
    else:
        verdict = "NOT A RESULT"
        why = ("stopped without a convergence statement (exit=%r) and the registered "
               "intermediate threshold was NOT met (reduction=%r over %d majors)"
               % (exit_text, red, rows_n))
    return {"arm": arm, "verdict": verdict, "why": why,
            "ipopt_exit": exit_text, "ipopt_printed_convergence": printed,
            "ipopt_table_rows": rows_n, "ipopt_n_iterations": doc.get("ipopt_n_iterations"),
            "max_iter_registered": XF.MAX_MAJORS,
            "reached_iteration_cap": bool(rows_n >= XF.MAX_MAJORS),
            "stall_condition_A": stall.get("A"),
            "stall_condition_B_state": stall.get("condition_B_state"),
            "weighted_drag_reduction_pct": red,
            "J_baseline": doc.get("J_baseline"), "J_final": doc.get("J_final"),
            "CD_baseline": doc.get("CD_baseline"), "CD_final": doc.get("CD_final"),
            "CL_baseline": doc.get("CL_baseline"), "CL_final": doc.get("CL_final"),
            "alphas": doc.get("alphas"), "weights": doc.get("weights"),
            "_cl_travels": "CL is UNCONSTRAINED here -- alpha is the operating point, so "
                           "there is no DV to trim with. THE THREE-CL TRIPLE therefore "
                           "travels with every weighted-drag number this item "
                           "publishes. A reduction at unstated lift is not a "
                           "reportable number.",
            "_improvement_grades_nothing":
                "DAFOAM_CHARTER.md section 9 forbids grading an optimisation by the "
                "size of its improvement.  `drag_reduction_pct` is reported and is "
                "an input to the REGISTERED intermediate threshold only.",
            "registered_intermediate_threshold_pct": MIN_WEIGHTED_DRAG_REDUCTION_PCT,
            "registered_min_majors": MIN_MAJORS_TO_HAVE_SEARCHED}


def g_fd(root, row, arms_ran):
    """Band D per component and band E on the aggregate, on the WEIGHTED
    OBJECTIVE `J` and on each scenario's `CL`, AT THE FINAL DESIGN POINT, with
    the DECADE plateau proved per pair and `shape[7]` EXCLUDED BY NAME."""
    xe = "XE-S" if row == "SHIPPED" else "XE-P"
    fe = "FE-S" if row == "SHIPPED" else "FE-P"
    out = {"xe_arm": xe, "fe_arm": fe,
           "excluded_from_aggregate": [list(c) for c in XF.EXCLUDED_FROM_AGGREGATE],
           "excluded_from_aggregate_reason": XF.EXCLUSION_REASON,
           "band_D_pct": XF.FD_BAND_PCT, "band_E_pct": XF.AGG_BAND_PCT,
           "plateau_tol_pct": XF.PLATEAU_TOL_PCT,
           "quantity": "J = SUM_i w_i CD_i, plus the three per-scenario CL",
           "scenarios": XF.SCENARIOS, "weights": XF.WEIGHTS}
    if xe not in arms_ran or fe not in arms_ran:
        out.update({"verdict": "NOT A RESULT",
                    "why": "an endpoint arm did not run (%s=%s, %s=%s)"
                           % (xe, xe in arms_ran, fe, fe in arms_ran)})
        return out
    xdoc, xpath = load_artefact(root, xe)
    fdoc, fpath = load_artefact(root, fe)
    if xdoc is None or fdoc is None:
        out.update({"verdict": "NOT A RESULT", "why": "an endpoint artefact is absent"})
        return out

    adj = read_X(xpath)                                   # THE NAMED READER
    fd = read_F(fpath)                                    # THE NAMED READER
    s_key = repr(XF.S_STAR["shape"])
    pairs_J, pairs_CL = [], []
    per = {}
    for r in fdoc.get("rows", []):
        if r.get("status") != "MEASURED":
            continue
        dv, idx = r.get("dv"), r.get("idx")
        key = "%s[%s]" % (dv, idx)
        excluded = XF.is_excluded(dv, idx)
        at = (fd.get((dv, idx)) or {}).get(s_key)
        rec = {"excluded_from_aggregate": excluded, "registered_non_result": excluded,
               "plateau_J": r.get("plateau_J"), "plateau_CL": r.get("plateau_CL")}

        # ---- the weighted objective ----------------------------------------
        aJ = adj["J"][idx] if idx < len(adj["J"]) else None
        fJ = (at or {}).get("dJ")
        eJ = XF.rel_pct(aJ, fJ)
        flipJ = bool(aJ is not None and fJ is not None and aJ * fJ < 0)
        platJ = r.get("plateau_J") or {}
        if excluded:
            vJ = "NOT A RESULT"
        elif eJ is None or not platJ.get("two_sided"):
            vJ = "NOT A RESULT"
        elif flipJ or eJ > XF.FD_BAND_PCT:
            vJ = "GATE FAIL"
        else:
            vJ = "PASS"
        rec["J"] = {"adjoint": aJ, "fd_at_s_star": fJ, "rel_pct": eJ,
                    "sign_flip": flipJ, "plateau_two_sided": platJ.get("two_sided"),
                    "verdict": vJ}
        if not excluded and aJ is not None and fJ is not None:
            pairs_J.append((aJ, fJ))

        # ---- the three per-scenario CL -------------------------------------
        rec["CL"] = []
        for i, sc in enumerate(XF.SCENARIOS):
            aC = (adj["CL"][i][idx] if i < len(adj["CL"]) and idx < len(adj["CL"][i])
                  else None)
            fC = ((at or {}).get("dCL") or [None] * len(XF.SCENARIOS))[i] if at else None
            eC = XF.rel_pct(aC, fC)
            flipC = bool(aC is not None and fC is not None and aC * fC < 0)
            platC = ((r.get("plateau_CL") or [{}] * len(XF.SCENARIOS))[i]) or {}
            if excluded:
                vC = "NOT A RESULT"
            elif eC is None or not platC.get("two_sided"):
                vC = "NOT A RESULT"
            elif flipC or eC > XF.FD_BAND_PCT:
                vC = "GATE FAIL"
            else:
                vC = "PASS"
            rec["CL"].append({"scenario": sc, "adjoint": aC, "fd_at_s_star": fC,
                              "rel_pct": eC, "sign_flip": flipC,
                              "plateau_two_sided": platC.get("two_sided"),
                              "verdict": vC})
            if not excluded and aC is not None and fC is not None:
                pairs_CL.append((aC, fC))
        per[key] = rec

    agg_J = XF.aggregate_excl_flagged(pairs_J)
    agg_CL = XF.aggregate_excl_flagged(pairs_CL)
    graded = [k for k, v in per.items() if not v["excluded_from_aggregate"]]
    fails = [k for k in graded
             if per[k]["J"]["verdict"] == "GATE FAIL"
             or any(c["verdict"] == "GATE FAIL" for c in per[k]["CL"])]
    nars = [k for k in graded
            if per[k]["J"]["verdict"] == "NOT A RESULT"
            or any(c["verdict"] == "NOT A RESULT" for c in per[k]["CL"])]

    if len(graded) < MIN_GRADED_COMPONENTS or nars:
        verdict = "NOT A RESULT"
    elif fails or (agg_J is not None and agg_J > XF.AGG_BAND_PCT) \
            or (agg_CL is not None and agg_CL > XF.AGG_BAND_PCT):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"

    out.update({
        "per_component": per, "n_graded_components": len(graded),
        "min_graded_components": MIN_GRADED_COMPONENTS,
        "graded_components": sorted(graded),
        "components_gate_fail": sorted(fails),
        "components_not_a_result": sorted(nars),
        "aggregate_pct_excl_flagged_J": agg_J,
        "aggregate_pct_excl_flagged_CL": agg_CL,
        "_aggregate_key_name": "The key says `excl_flagged` because the aggregate is "
                               "over THREE components, not four. shape[7] is EXCLUDED "
                               "BY NAME and its own reading is published above, beside "
                               "the aggregate and never instead of it "
                               "(DAFOAM_CHARTER.md section 3).",
        "harness_floor_pct": [2.5, 5.0],
        "_harness_floor": "VERIFICATION_CHARTER.md section 7 step 4: the harness-sound "
                          "floor on this stack is 2.5 to 5 %% vector-norm relative "
                          "error, and a number below that is a claim about the "
                          "harness. REPORTED, NEVER GATED.",
        "verdict": verdict})
    return out


def g_plat7(fd_gate):
    """`shape[7]` is a REGISTERED NON-RESULT.  Re-stated as its own reading so it
    appears on the record even if a reader skips `g_fd`, and set FROM THE
    REGISTERED LIST -- never from the measured value.

    CARRIED FORWARD UNCHANGED FROM D19O, AND THE REASON IS NOW SHARPER RATHER
    THAN WEAKER.  D19O MEASURED that at ITS optimum this component is 28x larger
    than at the baseline and that its plateau CLOSES there.  That is evidence a
    SUCCESSOR may use to register it as gradable IN ADVANCE.  It is not licence
    to grade it here: this item optimises a different objective and reaches a
    different design point, and promoting a component after seeing a good number
    is the move the registration exists to prevent."""
    per = fd_gate.get("per_component", {})
    recs = {}
    for dv, idx in XF.EXCLUDED_FROM_AGGREGATE:
        k = "%s[%d]" % (dv, idx)
        r = per.get(k, {})
        recs[k] = {"verdict": "NOT A RESULT",
                   "set_from": "REGISTERED LIST, never from the measured value",
                   "measured_J": r.get("J"), "measured_CL": r.get("CL"),
                   "plateau_J": r.get("plateau_J")}
    return {"components": recs, "verdict": "NOT A RESULT",
            "why": XF.EXCLUSION_REASON,
            "d19o_finding": "curriculum_D19O/RESULTS.md section 3.1: |dCD/dshape[7]| "
                            "5.887e-03 at D19O's optimum against 2.099e-04 at the "
                            "baseline, plateau two-sided there. ITS NEAR-NULLITY IS A "
                            "PROPERTY OF THE BASELINE, NOT OF THE COMPONENT -- and "
                            "that is a SUCCESSOR's registration to make in advance, "
                            "not this item's to make after the fact."}


def g_tb(root, row, arms_ran):
    """`DAFOAM_CHARTER.md` section 4: the same probe at a DELIBERATELY WRONG step.
    If the wrong step also passes, the gate is not measuring what it claims and
    the row's FD verdict is WITHDRAWN to NOT A RESULT.  Graded on `J`.

    A probe that ERRORED counts as FAILING the baseline."""
    fe = "FE-S" if row == "SHIPPED" else "FE-P"
    xe = "XE-S" if row == "SHIPPED" else "XE-P"
    out = {"fe_arm": fe, "step": XF.TB_STEP, "max_passing": XF.TB_MAX_PASSING,
           "quantity": "J",
           "_why_this_step": "five orders below s*. On a J derivative of order 1e-2 "
                             "the FD numerator at 1e-8 is ~1e-10, at or below the "
                             "measured primal repeatability on this case at np=1. The "
                             "estimate is noise and MUST fail band D."}
    if fe not in arms_ran or xe not in arms_ran:
        out.update({"verdict": "NOT A RESULT", "why": "an endpoint arm did not run"})
        return out
    fdoc, fpath = load_artefact(root, fe)
    xdoc, xpath = load_artefact(root, xe)
    if fdoc is None or xdoc is None:
        out.update({"verdict": "NOT A RESULT", "why": "an endpoint artefact is absent"})
        return out
    adj = read_X(xpath)
    fd = read_F(fpath)
    passing, rows = [], {}
    for r in fdoc.get("rows", []):
        if r.get("status") != "MEASURED":
            continue
        dv, idx = r.get("dv"), r.get("idx")
        if XF.is_excluded(dv, idx):
            continue
        k = "%s[%s]" % (dv, idx)
        at = (fd.get((dv, idx)) or {}).get(repr(XF.TB_STEP))
        if not at or at.get("dJ") is None:
            rows[k] = {"evaluable": False, "passes_band_D": False,
                       "note": "a probe that errored counts as FAILING the baseline"}
            continue
        aJ = adj["J"][idx] if idx < len(adj["J"]) else None
        e = XF.rel_pct(aJ, at["dJ"])
        pz = bool(e is not None and e <= XF.FD_BAND_PCT)
        rows[k] = {"evaluable": True, "rel_pct": e, "passes_band_D": pz}
        if pz:
            passing.append(k)
    out.update({"per_component": rows, "n_passing": len(passing),
                "components_passing": sorted(passing),
                "verdict": "PASS" if len(passing) <= XF.TB_MAX_PASSING else "GATE FAIL",
                "withdraws_row_fd_verdict": bool(len(passing) > XF.TB_MAX_PASSING)})
    return out


def g_alpha(root, arms_ran):
    """THE OPERATING POINTS ARE READ BACK, NOT ASSUMED.

    A scenario silently wired to the wrong angle produces a gradient against a
    flow condition nobody registered -- and EVERY band would still pass, because
    the FD and the adjoint would both be taken at the same wrong angle.  This is
    the one defect a multipoint item can carry invisibly, so it is gated."""
    out = {"registered_alphas": ALPHAS_REGISTERED, "abs_tol": ALPHA_ABS_TOL,
           "registered_weights": WEIGHTS_REGISTERED, "per_arm": {}, "verdict": "PASS"}
    seen_any = False
    for arm in arms_ran:
        if ARM_KIND[arm] not in ("O", "XE", "FE"):
            continue
        doc, path = load_artefact(root, arm)
        if doc is None:
            continue
        rd = read_alphas(path)                            # THE NAMED READER
        if not rd:
            out["per_arm"][arm] = {"read": None, "ok": False,
                                   "why": "artefact carries no alphas_read_back"}
            out["verdict"] = "GATE FAIL"
            continue
        seen_any = True
        bad = []
        for i, e in enumerate(rd):
            want = ALPHAS_REGISTERED[i] if i < len(ALPHAS_REGISTERED) else None
            if want is None or abs((e.get("read_dvs") or 0.0) - want) > ALPHA_ABS_TOL:
                bad.append({"i": i, "want": want, "read_dvs": e.get("read_dvs")})
            sc = e.get("read_scenario")
            if sc is not None and abs(sc - (want or 0.0)) > ALPHA_ABS_TOL:
                bad.append({"i": i, "want": want, "read_scenario": sc})
        if len(rd) != len(ALPHAS_REGISTERED):
            bad.append({"n_read": len(rd), "n_registered": len(ALPHAS_REGISTERED)})
        # the weights the artefact declares must be the registered ones too
        if list(doc.get("weights") or []) != WEIGHTS_REGISTERED:
            bad.append({"weights_declared": doc.get("weights"),
                        "weights_registered": WEIGHTS_REGISTERED})
        out["per_arm"][arm] = {"read": rd, "ok": not bad, "mismatches": bad}
        if bad:
            out["verdict"] = "GATE FAIL"
    if not seen_any:
        out["verdict"] = "NOT A RESULT"
        out["why"] = "no arm produced an artefact carrying the operating points"
    return out


def g_mp_struct(root, row, arms_ran):
    """`dJ/dx` must equal `SUM_i w_i dCD_i/dx` FROM THE ARTEFACT'S OWN COMPONENTS.

    This is what makes `J` a statement about ONE design vector rather than about
    three that happen to be equal -- the D6 defect, where `geometry_<pt>` was
    built PER SCENARIO.  Computed here from the adjoint the run wrote, never
    from the producer's expression."""
    xe = "XE-S" if row == "SHIPPED" else "XE-P"
    out = {"xe_arm": xe, "rtol": MP_STRUCT_RTOL, "weights": WEIGHTS_REGISTERED}
    if xe not in arms_ran:
        out.update({"verdict": "NOT A RESULT", "why": "the XE arm did not run"})
        return out
    xdoc, xpath = load_artefact(root, xe)
    if xdoc is None:
        out.update({"verdict": "NOT A RESULT", "why": "no d19m_X.json"})
        return out
    a = read_X(xpath)
    if not a["J"] or len(a["CD"]) != len(WEIGHTS_REGISTERED):
        out.update({"verdict": "NOT A RESULT",
                    "why": "the adjoint artefact carries %d CD arrays for %d weights"
                           % (len(a["CD"]), len(WEIGHTS_REGISTERED))})
        return out
    worst, n, per = 0.0, 0, []
    for k in range(len(a["J"])):
        recon = sum(WEIGHTS_REGISTERED[i] * a["CD"][i][k]
                    for i in range(len(WEIGHTS_REGISTERED)))
        got = a["J"][k]
        rel = abs(got - recon) / abs(got) if got else abs(got - recon)
        per.append({"k": k, "dJ": got, "sum_w_dCD": recon, "rel": rel})
        worst = max(worst, rel)
        n += 1
    out.update({"n_components": n, "worst_rel": worst, "per_component": per,
                "verdict": "PASS" if (n > 0 and worst <= MP_STRUCT_RTOL)
                           else "GATE FAIL"})
    return out


# ============================================================================
# COMPOSITION# ============================================================================
# COMPOSITION
# ============================================================================
def _apply_ceiling(verdict):
    """THE LAST STEP OF EVERY COMPOSITION.  See the module docstring, part I.
    `PASS` becomes the ceiling; every other token passes through unchanged, so
    the ceiling can only make a verdict WORSE and never better."""
    order = {"PASS": 6, "GATE REACHED": 5, "PENDING": 4, "BLOCKED": 3,
             "GATE FAIL": 2, "NOT A RESULT": 1}
    if order.get(verdict, 0) > order.get(VERDICT_CEILING, 0):
        return VERDICT_CEILING, True
    return verdict, False


def compose_row(row, gates):
    opt = gates["G-OPT9"][row]["verdict"]
    fd = gates["G5_fd"][row]["verdict"]
    tb = gates["G-TB"][row]["verdict"]
    mp = gates["G-MP-STRUCT"][row]["verdict"]
    if gates["G-TB"][row].get("withdraws_row_fd_verdict"):
        fd = "NOT A RESULT"
    # A row whose OPTIMISER is NOT A RESULT cannot be rescued by any other gate.
    if opt == "NOT A RESULT":
        raw, why = "NOT A RESULT", "the optimiser verdict is NOT A RESULT"
    elif "NOT A RESULT" in (fd, tb, mp):
        raw, why = ("NOT A RESULT",
                    "an endpoint gate is NOT A RESULT (fd=%s tb=%s mp_struct=%s)"
                    % (fd, tb, mp))
    elif "GATE FAIL" in (opt, fd, tb, mp):
        raw, why = ("GATE FAIL", "a gate failed (opt=%s fd=%s tb=%s mp_struct=%s)"
                    % (opt, fd, tb, mp))
    elif opt == "GATE REACHED":
        raw, why = "GATE REACHED", "the optimiser stopped without its own convergence statement"
    else:
        raw, why = "PASS", "every gate passed"
    # THE ENDPOINT FD CAN ONLY MAKE THINGS WORSE, NEVER BETTER.  An endpoint PASS
    # never upgrades a GATE REACHED optimiser.  Registered before the run.
    final, capped = _apply_ceiling(raw)
    return {"row": row, "verdict": final, "verdict_before_ceiling": raw,
            "capped_by_ceiling": capped, "why": why,
            "optimiser": opt, "endpoint_fd": fd, "trivial_baseline": tb,
            "mp_struct": mp}


def compose_item(gates, rows):
    stages = gates["G-STAGES"]["verdict"]
    rvs = [rows[r]["verdict"] for r in rows]
    hard = [gates[g]["verdict"] for g in
            ("G-M2_mesh_identity", "G-NP", "G9_toolchain", "G10_caps",
             "G12_placement", "G-DESIGNPOINT", "G-NOOPT-ENDPOINT", "G-EVALFAIL",
             "G-ALPHA")]
    hard += [gates["G-MP-STRUCT"][r]["verdict"] for r in ("SHIPPED", "PATCHED")]
    # ---- `hard` IS TESTED FOR BOTH TOKENS, AND THE SECOND ONE WAS MISSING ----
    # `D19M-COMPOSE-DEF-1`: this list was examined for "GATE FAIL" ONLY, so a hard
    # gate reporting "NOT A RESULT" fell through to `PASS` and was then capped to
    # `GATE REACHED` -- a verdict about an item whose subject the gate could not
    # read.  That INVERTS `CLAUDE.md` rule 5's direction: a gate may turn a PASS
    # INTO a NOT A RESULT and never the reverse.
    #
    # IT IS REACHABLE FROM THREE OF THE ELEVEN HARD READINGS, in five places,
    # swept by reading every gate's returns rather than by assuming G-ALPHA was
    # the only one:
    #   G-M2_mesh_identity : no checkMesh.log -- the MESH arm did not run
    #   G-ALPHA            : `not seen_any` -- no arm carried the operating points
    #   G-MP-STRUCT        : the XE arm did not run / no artefact / the artefact
    #                        carries the wrong number of CD arrays
    # The other eight (G-NP, G9, G10, G12, G-DESIGNPOINT, G-NOOPT-ENDPOINT,
    # G-EVALFAIL, and G-STAGES which is handled separately) emit only PASS or
    # GATE FAIL, and that was CHECKED, not assumed.
    #
    # INHERITED FROM `d19o_grade.py`, WHICH HAS THE IDENTICAL SHAPE.  It did not
    # bite D19O because every gate passed -- which is exactly how a fail-open
    # survives a green run, and is why one green run is not evidence that a
    # composition is sound.
    if (stages == "NOT A RESULT" or "NOT A RESULT" in rvs
            or "NOT A RESULT" in hard):
        raw = "NOT A RESULT"
    elif stages == "BLOCKED":
        raw = "BLOCKED"
    elif "GATE FAIL" in rvs or "GATE FAIL" in hard:
        raw = "GATE FAIL"
    elif "GATE REACHED" in rvs:
        raw = "GATE REACHED"
    else:
        raw = "PASS"
    final, capped = _apply_ceiling(raw)
    if final not in VOCAB:
        refuse("VOCAB", {"composed_verdict_outside_the_fixed_vocabulary": final})
    return final, raw, capped


HARD_GATES = ("G-M2_mesh_identity", "G-NP", "G9_toolchain", "G10_caps",
              "G12_placement", "G-DESIGNPOINT", "G-NOOPT-ENDPOINT", "G-EVALFAIL",
              "G-ALPHA")


def hard_gate_readings(gates):
    """Published on every record so a reader can see WHICH hard gate carried the
    item verdict, rather than inferring it from a token."""
    out = {g: gates[g]["verdict"] for g in HARD_GATES}
    for r in ("SHIPPED", "PATCHED"):
        out["G-MP-STRUCT[%s]" % r] = gates["G-MP-STRUCT"][r]["verdict"]
    return {"readings": out,
            "not_a_result": sorted(k for k, v in out.items() if v == "NOT A RESULT"),
            "gate_fail": sorted(k for k, v in out.items() if v == "GATE FAIL"),
            "_can_emit_not_a_result": ["G-M2_mesh_identity", "G-ALPHA",
                                       "G-MP-STRUCT[SHIPPED]", "G-MP-STRUCT[PATCHED]"],
            "_note": "Swept by reading every hard gate's returns: three of them can "
                     "emit NOT A RESULT; the other eight emit only PASS or GATE FAIL."}


def grade(root):
    prov = g_prov()
    led_rows, _order = read_ledger(root)
    arms_ran = [a for a in ARMS_DECLARED if a in led_rows]

    # ---- CLAUDE.md RULE 3, BEFORE A SINGLE GATE IS COMPOSED ------------------
    # Every reader is shown able to see a non-zero ON THIS RUN ROOT, through the
    # real reader function, or this comparator refuses and grades nothing.
    controls = run_live_controls(root, arms_ran)
    birth = birth_record(controls)
    if birth["n_not_born"] != 0:
        refuse("CONTROL", {"unborn_readers": birth["not_born"],
                           "note": "a reader not shown able to see a non-zero grades nothing"})

    gates = {"G-PROV": prov, "G-STAGES": g_stages(arms_ran)}
    gates["G-M2_mesh_identity"] = g_mesh(root)
    gates["G-NP"] = g_np(led_rows)
    gates["G9_toolchain"] = g9_toolchain(led_rows)
    gates["G12_placement"] = g12_placement(led_rows)
    gates["G10_caps"] = g10_caps(led_rows)
    gates["G-DESIGNPOINT"] = g_designpoint(root, arms_ran)
    gates["G-NOOPT-ENDPOINT"] = g_noopt_endpoint(root, arms_ran)
    gates["G-EVALFAIL"] = g_evalfail(root, arms_ran)

    comp = {}
    for arm in ARMS_DECLARED:
        if arm not in led_rows:
            comp[arm] = {"arm": arm, "verdict": "NOT RUN"}
            continue
        doc, _ = load_artefact(root, arm)
        comp[arm] = g_completion(root, arm, led_rows[arm], doc)
    gates["G1_completion"] = comp

    gates["G-ALPHA"] = g_alpha(root, arms_ran)
    gates["G-MP-STRUCT"] = {r: g_mp_struct(root, r, arms_ran)
                            for r in ("SHIPPED", "PATCHED")}
    gates["G-OPT9"] = {r: g_opt9(root, r, arms_ran) for r in ("SHIPPED", "PATCHED")}
    gates["G5_fd"] = {r: g_fd(root, r, arms_ran) for r in ("SHIPPED", "PATCHED")}
    gates["G-TB"] = {r: g_tb(root, r, arms_ran) for r in ("SHIPPED", "PATCHED")}
    gates["G-PLAT7"] = {r: g_plat7(gates["G5_fd"][r]) for r in ("SHIPPED", "PATCHED")}
    gates["G6_dot_product_duality"] = {
        "verdict": "NOT MEASURED",
        "why": "AV-2 measured that seeding forward mode makes the primal FAIL on "
               "this exact case on BOTH images.  Named, never composed."}
    gates["GCI_roache"] = {
        "verdict": "NOT APPLICABLE",
        "why": "No grid triple is registered: this is a single-grid optimisation on "
               "A1's own 4,032-cell mesh.  CLAUDE.md rule 5 has no row to act on "
               "here, and this comparator says so rather than leaving a reader to "
               "infer it from an absence."}

    rows = {r: compose_row(r, gates) for r in ("SHIPPED", "PATCHED")}
    verdict, raw, capped = compose_item(gates, rows)

    # THE CEILING BINDS AT ROW LEVEL AND THE ITEM INHERITS, so `capped` at item
    # level is normally False even when the ceiling did all the work.  A reader
    # of the item record must not have to reconstruct that, so it is stated:
    # `capped_by_ceiling_anywhere` is True if the ceiling bound EITHER row or the
    # item.  Without it, an item record could read `capped_by_ceiling: false`
    # beside a GATE REACHED that only exists BECAUSE of the ceiling -- which is
    # the shape of a true field that leaves a false impression.
    capped_anywhere = bool(capped or any(rows[r]["capped_by_ceiling"] for r in rows))

    return {
        "item": ITEM, "root": os.path.abspath(root),
        "grader_md5": md5_of(os.path.abspath(__file__)),
        "verdict": verdict, "verdict_before_ceiling": raw,
        "capped_by_ceiling": capped,
        "capped_by_ceiling_anywhere": capped_anywhere,
        "rows_capped_by_ceiling": [r for r in rows if rows[r]["capped_by_ceiling"]],
        "verdict_ceiling": VERDICT_CEILING, "verdict_ceiling_reason": CEILING_REASON,
        "verdict_statement":
            "%s -- %s.  THIS ITEM CANNOT PUBLISH PASS: it spends a compressible "
            "gradient with NO GRADED VERDICT whose plateau did not close "
            "(shape[7]/CD one-sided at 21.060684242435336 %%), and shape[7] is a "
            "REGISTERED NON-RESULT excluded by name from every aggregate."
            % (verdict, "two rows: SHIPPED=%s PATCHED=%s"
               % (rows["SHIPPED"]["verdict"], rows["PATCHED"]["verdict"])),
        "rows": rows, "gates": gates,
        "hard_gates": hard_gate_readings(gates),
        "controls": controls, "birth_register": birth,
        "vocabulary": list(VOCAB),
        "asserts_in_grader": count_asserts(os.path.abspath(__file__)),
        "submissions": "PARKED -- nothing in this item is filed, sent, uploaded, "
                       "registered, posted or commented outside this box "
                       "(CLAUDE.md rule 7; DAFOAM_CHARTER.md section 10).",
    }


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)      # MANDATORY: the driver names it,
    ap.add_argument("--selftest", action="store_true")   # not the comparator
    a = ap.parse_args(argv)
    try:
        out = grade(a.root)
    except Refusal as exc:
        sys.stderr.write("D19M_GRADE REFUSED: %s\n" % exc)
        return 2
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write("D19M_GRADE_WRITTEN %s verdict=%s rows=%s\n"
                     % (a.out, out["verdict"],
                        {r: out["rows"][r]["verdict"] for r in out["rows"]}))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        import d19m_grade_selftest as ST
        sys.exit(ST.main())
    sys.exit(main(sys.argv[1:]))
