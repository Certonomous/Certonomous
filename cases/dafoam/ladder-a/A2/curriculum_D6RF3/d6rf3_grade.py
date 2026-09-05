#!/usr/bin/env python3
"""Curriculum D6RF3 -- THE FROZEN GRADING PATH for `F_mp` and `REF_off`.

DERIVED FROM `curriculum_D6RF2/d6rf2_grade.py`
(md5 `32a539780e34fe6d7945b7e301badc0f`, 43,462 bytes, re-hashed on disk before
this file was written).  The deltas are in
`d6rf3_grade_DELTAS_from_d6rf2.diff` beside this file and there are SIX
mechanisms in them, all registered in `PREREGISTRATION.md` before compute:

  M1  `CD_i(mp)` HAS A NEW SOURCE (section 2a).  `gate_off` and `gate_price`
      no longer read `hist["CD_<pt>"][-1]`.  `D6RF3-DEF-4` established BY
      COMPLETE ENUMERATION of the registered `OptView.hst` (md5
      `70fafa07bdee618fef13039433c01114`; 1,013 rows, 1,007 iteration records,
      863 carrying `funcs`) that **the file contains no `CD` at all**.  The
      source is now the FD arm's own `baseline` primal, which already measured
      it -- zero marginal core-minutes -- and every row carries
      `CD_mp_source = FD_BASELINE_PRIMAL`.
  M2  THE SECTION 3f FINITENESS CLAUSE, `D6RF3-DEF-5`'s repair.  The parent
      carried **zero** finiteness guards in 43,462 bytes.  `NaN < 0.0` is
      False, so its registered `negative -> NOT A RESULT` limb did not fire;
      `NaN <= 1.0e-3` is False, so the PASS limb did not fire; control reached
      `else` -> **`GATE FAIL`**.  With `cd_mp = NaN`, `cd_mp <= cd_ref` is also
      False -> `GATE FAIL` on all three off-design points.  **Four gated rows
      manufactured from a non-number, and nothing in the item would have said
      so.**  Every value read from an artefact and compared against a threshold
      now goes through `_ff`, which raises `NonFinite` naming the artefact, the
      key and the token as read.  STRICTLY RESTRICTIVE: it can only turn a PASS
      or GATE FAIL INTO a NOT A RESULT.
  M3  A THIRD PLANTED-ZERO CONTROL (section 3e), because the source moved: the
      CD reader.  Its reader is IMPORTED from `d6rf3_cd_plant_control.py` and
      is the same function the gates call.  All three controls now report one
      of `EXERCISED-PASS` / `EXERCISED-FAIL` / `NOT EXERCISED`, printed beside
      the verdict, never counted as a pass and never inferred from the absence
      of a failure.
  M4  `X-CDLOG` (section 3d), REPORTED AND GATED BY NOTHING: the per-point
      difference between the FD baseline CD and the stdout-recovered CD of the
      last finite major, with the composite-identity residual beside it.  NO
      THRESHOLD.  NO VERDICT.  IT MOVES NOTHING.
  M5  `PRODUCT_WRITER` and `cap_reachability`, two executable checks that
      would each have caught a real defect in a frozen set of this lineage.
  M6  The section 3g ladder gains a rung: non-finite input sits at rung 3,
      ABOVE the G-DVL and pathology rungs.

WHAT THE PLATEAU SAYS, AND WHAT IT DOES NOT.  The `s_lo`/`s_hi` pair IS
`VERIFICATION_CHARTER.md:854-855` step 1's "two or three point mini-sweep", and
`DAFOAM_CHARTER.md` section 20 (addendum 2026-09-04) rules that this SATISFIES
section 3.  **No shortfall caveat is printed and none is owed**; writing "no
plateau proof is claimed" would be a false self-deprecation, which is a
misstatement in the modest direction and still a misstatement.  What IS printed
per component is that the pair is ONE-SIDED by construction -- graded at `s_hi`
with its only neighbour below -- with the family's measured instance of the
blind side firing (D16 `shape[6]`, 14.0978 % coarse against 1.1268 % fine).

THIS ITEM SHIPS ONE ROW.  `DAFOAM_CHARTER.md` section 6 wants two.  The PATCHED
row is bought; the SHIPPED row is NOT bought and is PRICED anyway at 155.70
core-min, on the artefact's own face, because an unbought row that is priced can
be bought by a successor and an unbought row that is unpriced quietly becomes
never.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python -O` deletes them.

This file IS the grading path fixed at the pre-registration commit
(`CLAUDE.md` rule 2).  Its md5 is pinned in `PREREGISTRATION.md` section 7 and
in the queue row; it verifies at execution that its own bytes on disk equal the
committed blob at HEAD, and it REFUSES (exit 2) if they do not.

VOCABULARY.  `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` and
no other word (`CLAUDE.md` rule 1).  `GATE REACHED` is DELIBERATELY ABSENT: it
labels an optimiser stopped by a wall clock, an iteration cap or a budget
(`DAFOAM_CHARTER.md` section 9), and THIS ITEM RUNS NO OPTIMISER.  A word that
can never fire is not registered.

REFUSES RATHER THAN DEGRADES (exit 2), as this family's comparators do.

THE PLANTED-ZERO CONTROLS (`CLAUDE.md` rule 3) are not optional decoration and
are not skippable: `G-FD` and `G-PRICE` each plant a known perturbation into a
COPY of the artefact they read, read it back FROM DISK through the SAME reader,
and REFUSE if the reader cannot see it.  Both also assert the unperturbed
original is byte-unchanged.  A zero -- or an agreement -- from a reader not
shown able to see a non-zero is not evidence.

L-342 FIELD CLASSES.  Absent INFRASTRUCTURE (a delivered-cores sample, a
container kernel clock) is reported `NOT_MEASURED` beside the verdict and voids
only the claim that depends on it.  Absent PHYSICS (a log, an rc, a registered
artefact whose producing arm ran) REFUSES.  Bookkeeping never voids physics.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys

# ============================ REGISTERED CONSTANTS ==========================
# Every value in this block is frozen by PREREGISTRATION.md before compute.
ITEM = "D6RF3"
ARMS = ["F_mp", "REF_off"]
ARM_KIND = {"F_mp": "SOLVER", "REF_off": "SCRIPT"}
ARM_DIR = {"F_mp": "F_mp", "REF_off": "REF_off"}

RANKS = 4
CAPS = {"F_mp": 480.0, "REF_off": 190.0}
TMO = {"F_mp": 7110, "REF_off": 2760}
FRAME_ALLOWANCE_S = 90
KILL_GRACE_S = 60
FRAME_GAP_ALLOWANCE_S = FRAME_ALLOWANCE_S - KILL_GRACE_S      # 30
CAP_INVERSION_TOL_CORE_MIN = 0.02

CPUSET = "2,3,4,14"
DELIVERED_MIN = 3.0
MEMORY = "20g"

DIGEST_PATCHED = ("sha256:2927768a16acdea0330180fff95c8879"
                  "c1dda9efcf6028728523b7dee30f6d35")
DIGEST_SHIPPED = ("sha256:9d45679d55fd47f5ca7afd99cabb86c7"
                  "c2729cf2acf34c438eb33af5290f07fc")     # NAMED UNBOUGHT
IDWARP_SO_MD5 = "85f59e87253e0a71a813f64ca6e4c425"

# FD bright line -- band D, inherited BY CITATION from D6R PREREGISTRATION.md
# section 3e (VERIFICATION_CHARTER.md section 7 through D6 section 3 and
# DAFOAM_CHARTER.md section 2).  NOT re-derived here.
FD_BAND_PCT = 5.0
AGG_BAND_PCT = 5.0
PLATEAU_TOL_PCT = 10.0
SIGN_FLIP_PATHOLOGY = 2

# D4's PATCHED single-point optimum, re-read from ITS OWN artefact and refused
# if it has moved.
CD_F_D4_RECORDED = 2.1125978108239574e-02
D4_OPT_IPOPT = ("/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/"
                "O/opt_IPOPT.txt")
PRICE_BAND = (0.0, 1.0e-3)

# REPORTED, NOT GATED (Sanaa 2026-09-03 ~20:00Z): the composite reduction is a
# number about an optimisation that exited on a non-finite objective.
RED_BAND_PCT = (15.0, 40.0)

POINTS = ["cl04", "cl05", "cl06"]
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}

PLANT = 1.234e-03                    # the planted-zero perturbation, registered
PLANT_REL_TOL = 1.0e-9

# ---------------------- section 2a: WHERE CD_i(mp) COMES FROM ---------------
# The gated source, FIXED BEFORE COMPUTE.  `d6rf3_major_history.json` is NOT
# the source and CANNOT be: D6RF3-DEF-4 enumerated the producing history
# COMPLETELY (OptView.hst md5 70fafa07bdee618fef13039433c01114; 1,013 rows,
# 1,007 iteration records, 863 carrying `funcs`) and found NO CD in any
# structure of any record.  A file that cannot contain the quantity is not a
# source for it.
CD_ARTEFACT = "d6rf3_fd_endpoint.json"
CD_JSON_PATH = ("points", "<pt>", "CD")     # section 2a's registered path
CD_MP_SOURCE_LABEL = "FD_BASELINE_PRIMAL"
CD_MP_SOURCE_STATEMENT = (
    "CD_i(mp) is prob.get_val('<pt>.aero_post.CD') in the `baseline` primal of "
    "d6rf3_fd_endpoint.py, at the endpoint design vector reconstructed to "
    "PHYSICAL units. It is NOT D6RF section 0a's `last accepted major of a "
    "failed optimisation`; the two agree only to primal convergence and THIS "
    "ITEM MAKES NO CLAIM THAT THEY ARE THE SAME NUMBER. No result of this item "
    "may be compared to a D6R- or D6RF-era CD_i(mp) without this label "
    "travelling with the number (DAFOAM_CHARTER.md section 18.6 refinement 2).")

# ---------------- section 3f: THE FINITENESS CLAUSE, D6RF3-DEF-5's repair ----
# `d6rf2_grade.py` carried ZERO finiteness guards in 43,462 bytes (measured).
# `NaN < 0.0` is False, so the registered `negative -> NOT A RESULT` limb did
# NOT fire and control fell through to GATE FAIL; `NaN <= cd_ref` is False, so
# all three off-design points read GATE FAIL.  FOUR GATED ROWS MANUFACTURED
# FROM A NON-NUMBER.  Registered before compute; STRICTLY RESTRICTIVE -- it can
# only turn a PASS or GATE FAIL INTO a NOT A RESULT, never the reverse.
NON_FINITE_REASON = "NON_FINITE_INPUT"
# The clause's registered binding list, section 3f, VERBATIM and NOT WIDENED:
FINITENESS_BINDS = ("G-OFF", "G-PRICE", "G-FD", "G-DVL", "R-RED")

# ------- section 2b / 3d: X-CDLOG, REPORTED AND GATED BY NOTHING ------------
# The three CD recovered from D6R's O_mp stdout at the LAST FINITE MAJOR
# (history row 998), matched to that row by CL.  Registered here as CONSTANTS
# rather than re-derived at grading time, because re-deriving them means
# re-scanning a 262k-line log and the numbers are already fixed by section 2b.
CDLOG = {"cl04": 1.846929883e-02, "cl05": 2.176156349e-02, "cl06": 2.696277508e-02}
CDLOG_LINES = {"cl04": 262185, "cl05": 262411, "cl06": 261901}
CDLOG_SOURCE = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-"
                "multipoint/O_mp -- stdout of the producing optimisation")
CDLOG_J_AT_ROW_998 = 0.022238800232340834
CDLOG_COMPOSITE_RESID_ABS = 9.840833e-12       # sum(w_i*CD_i) - J, recomputed
CDLOG_COMPOSITE_RESID_REL = 4.425074e-10

# ---------------- DAFOAM_CHARTER.md section 6: TWO ROWS OR IT IS NOT A -----
# ---------------- VERDICT.  THIS ITEM BUYS ONE, AND PRICES THE OTHER. -------
ROW_BOUGHT = "PATCHED"
ROW_NOT_BOUGHT = "SHIPPED"
# An unbought row that is PRICED can be bought by a successor; an unbought row
# that is UNPRICED quietly becomes never.  This is `F_mp`'s own estimate: a
# SHIPPED row is the same arm on stock IDWarp at the same cap.
SHIPPED_ROW_PRICE_CORE_MIN = 155.70
PREDICTED_CORE_MIN = {"F_mp": 155.70, "REF_off": 60.07}

# ---- DAFOAM_CHARTER.md section 18.3, applied to PRODUCTS as well as to -----
# ---- instruments.  D6RF3-DEF-6: in the frozen D6RF2 set the grader, the -----
# ---- launcher and the writer disagreed on the name of a registered product.
PRODUCT_WRITER = {
    "d6rf3_endpoint_dvs_PHYSICAL.json": "d6rf3_endpoint_physical.py",
    "d6rf3_endpoint_dvs_DRIVERSCALED.json": "d6rf3_endpoint_physical.py",
    "d6rf3_endpoint_dvs.json": "d6rf3_extract_endpoint.py",
    "d6rf3_major_history.json": "d6rf3_extract_endpoint.py",
    "d6rf3_fd_endpoint.json": "d6rf3_fd_endpoint.py",
    "d6rf3_ref_off.json": "d6rf3_ref_off.py",
}

REGISTERED_CHAIN_OUTCOMES = ("STOPPED_AT_FIRST_NONZERO", "STOPPED_H5",
                             "BLOCKED_H5", "BLOCKED_AGGREGATE",
                             "REFUSED_ALREADY_BOUGHT", "ABORT")

ARTEFACT_PRODUCER = {
    "d6rf3_endpoint_dvs_PHYSICAL.json": "F_mp",
    "d6rf3_endpoint_dvs_DRIVERSCALED.json": "F_mp",
    "d6rf3_endpoint_dvs.json": "F_mp",
    "d6rf3_major_history.json": "F_mp",
    "d6rf3_fd_endpoint.json": "F_mp",
    "d4_endpoint_dvs_PHYSICAL.json": "REF_off",
    "d4_endpoint_dvs.json": "REF_off",
    "d6rf3_ref_off.json": "REF_off",
}
REGISTERED_PRODUCTS = {
    "F_mp": ["d6rf3_endpoint_dvs_PHYSICAL.json", "d6rf3_endpoint_dvs_DRIVERSCALED.json",
             "d6rf3_endpoint_dvs.json", "d6rf3_major_history.json",
             "d6rf3_fd_endpoint.json"],
    "REF_off": ["d4_endpoint_dvs_PHYSICAL.json", "d4_endpoint_dvs.json",
                "d6rf3_ref_off.json"],
}
TERMINAL_STATEMENT = "Finalising parallel run"
# ===========================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir,
                                    os.pardir, os.pardir))

sys.path.insert(0, HERE)
# THE ONE CD READER OF THIS ITEM.  Imported, not re-implemented: the reader the
# section 3e control plants into must be BYTE-FOR-BYTE the reader the gate uses,
# or the control controls nothing.
import d6rf3_cd_plant_control as cdc                               # noqa: E402


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str)[:4000])


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _f(x):
    """A repr()'d float from an artefact, or a float, or REFUSE."""
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            refuse("float_parse", {"value": x[:120]})
    refuse("float_parse", {"type": type(x).__name__})


class NonFinite(Exception):
    """Section 3f.  Raised AT THE POINT OF READING, carrying the artefact, the
    key and the token AS READ -- not a bare flag, because a gate that says
    NON_FINITE_INPUT without naming what it read is not actionable."""

    def __init__(self, artefact, key, token):
        self.detail = {"reason": NON_FINITE_REASON, "artefact": artefact,
                       "key": key, "token_as_read": token}
        Exception.__init__(self, json.dumps(self.detail, sort_keys=True,
                                            default=str))


def _ff(x, artefact, key):
    """THE SECTION 3f READER.  Every value this grader reads from an artefact
    and compares against a threshold goes through here.

    `_f` parses `float('nan')`, `float('inf')` and `float('-inf')` WITHOUT
    COMPLAINT -- that is not a bug in `_f`, it is what `float()` does -- and
    every ordered comparison against a NaN is False, so a NaN silently takes
    the `else` branch of any two-limb test.  D6RF3-DEF-5 is exactly that: the
    endpoint row of the producing history is index 1006, whose `funcs` are ALL
    NaN (687 of 863 `funcs` rows are non-finite), and the parent grader would
    have printed GATE FAIL on four gated rows from it.

    THE REPAIR IS STRICTLY RESTRICTIVE.  Raising here can only turn a PASS or
    a GATE FAIL INTO a NOT A RESULT.  It can never produce a PASS, never
    produce a GATE FAIL, and never rescue a row -- which is `CLAUDE.md` rule
    5's own permitted direction of travel."""
    v = _f(x)
    if not math.isfinite(v):
        raise NonFinite(artefact, key, repr(x) if isinstance(x, str) else v)
    return v


def _nar_non_finite(base, exc):
    """Fold a NonFinite into a gate result.  ALWAYS `NOT A RESULT`, NEVER
    `GATE FAIL` and NEVER `PASS` (section 3f)."""
    out = dict(base)
    out["verdict"] = "NOT A RESULT"
    out["reason"] = NON_FINITE_REASON
    out["non_finite"] = exc.detail
    out["clause"] = ("PREREGISTRATION.md section 3f: a non-finite value makes "
                     "its gate NOT A RESULT naming the artefact, the key and "
                     "the token as read. It is NEVER GATE FAIL and never PASS.")
    return out


def cap_reachability():
    """THE CAP-versus-DEADLINE REACHABILITY CHECK, run at every grading and
    printable as ARITHMETIC.

    Two independent stopping conditions guard each arm and they are stated in
    DIFFERENT UNITS: `cap_core_min` (core-minutes, rule 12's unit) and `TMO`
    (in-container wall seconds, what `timeout` actually enforces).  If they
    are not reconciled, one of them is decorative:

        cap_wall_equivalent_s = cap_core_min * 60 / ranks
        max_spend_at_TMO_core_min = TMO * ranks / 60

    If `cap_wall_equivalent_s` <= `TMO` the CAP fires first and the deadline
    never runs; if it exceeds `TMO` by more than the frame allowance, the CAP
    IS UNREACHABLE and a cap breach can never be the recorded stopping
    condition -- the run is always killed on the clock instead, and the ledger
    records the wrong reason for the stop.  The registered design here is
    `TMO + FRAME_ALLOWANCE_S == cap_wall_equivalent_s` EXACTLY: the deadline
    bounds the in-container program and the frame allowance is the container
    start/stop outside it, so the two together are the cap and neither is
    decorative.  REFUSES if that identity does not hold."""
    out = {"ranks": RANKS, "frame_allowance_s": FRAME_ALLOWANCE_S, "arms": {}}
    for arm in ARMS:
        cap, tmo = CAPS[arm], TMO[arm]
        cap_wall = cap * 60.0 / RANKS
        max_spend = tmo * RANKS / 60.0
        residual = cap_wall - (tmo + FRAME_ALLOWANCE_S)
        r = {"cap_core_min": cap, "TMO_s": tmo,
             "cap_wall_equivalent_s": cap_wall,
             "TMO_plus_frame_s": tmo + FRAME_ALLOWANCE_S,
             "identity_residual_s": residual,
             "max_spend_at_TMO_core_min": max_spend,
             "cap_headroom_core_min": cap - max_spend,
             "cap_reachable": cap_wall > tmo,
             "predicted_core_min": PREDICTED_CORE_MIN[arm],
             "predicted_over_cap": PREDICTED_CORE_MIN[arm] > cap}
        if abs(residual) > 1.0e-6:
            refuse("CAP_REACHABILITY",
                   dict(r, arm=arm,
                        note="cap_core_min*60/ranks != TMO + frame allowance: "
                             "the cap and the deadline are not reconciled and "
                             "one of them is decorative"))
        if r["predicted_over_cap"]:
            refuse("CAP_REACHABILITY",
                   dict(r, arm=arm, note="the registered estimate exceeds the "
                                         "cap it is registered under"))
        out["arms"][arm] = r
    out["ceiling_core_min"] = sum(CAPS.values())
    out["total_predicted_core_min"] = sum(PREDICTED_CORE_MIN.values())
    return out


# ------------------ DAFOAM_CHARTER.md section 18.3, on PRODUCTS -------------
def product_writer_check():
    """EVERY registered product is asserted to be NAMED, as a literal, in the
    instrument registered as writing it -- existence of the writer asserted
    BEFORE any read of it.

    This exists because `D6RF3-DEF-6` happened in the frozen `D6RF2` set:
    `d6rf2_grade.py:94/:104/:458` and `d6rf2_run_arm.sh:546` registered
    `d6rf2_endpoint_dvs_PHYSICAL.json` while `d6rf2_endpoint_physical.py:75`,
    the only writer, still wrote `D6RF`'s `d6rf_endpoint_dvs_PHYSICAL.json`.
    `gate_g1`'s age guard walks `REGISTERED_PRODUCTS` and refuses
    `registered_product_absent` when the producing arm RAN -- so the item
    would have refused at grading however clean the arms were, and no md5
    freeze over the instrument set could have seen it: every pinned file
    hashed correctly.  Section 18.3's own sentence: these are different
    questions and the second cannot be inferred from the first at any level
    of agreement.

    REFUSES rather than grading, because a product-name disagreement makes
    every downstream reading meaningless rather than merely failing."""
    out = {}
    for arm in ARMS:
        for prod in REGISTERED_PRODUCTS[arm]:
            writer = PRODUCT_WRITER.get(prod)
            if writer is None:
                out[prod] = {"writer": None, "named_by_writer": None,
                             "note": "d4_* products are D4's own instruments, "
                                     "staged unchanged and out of scope"}
                continue
            wpath = os.path.join(HERE, writer)
            if not os.path.isfile(wpath):                 # EXISTENCE FIRST
                refuse("PRODUCT_WRITER", {"product": prod, "writer": writer,
                                          "writer_absent_on_disk": wpath})
            with open(wpath, errors="replace") as fh:
                named = prod in fh.read()
            out[prod] = {"writer": writer, "named_by_writer": named}
            if not named:
                refuse("PRODUCT_WRITER",
                       {"product": prod, "writer": writer,
                        "the_writer_does_not_name_the_product": True,
                        "note": "D6RF3-DEF-6's class. A product registered "
                                "under a name no instrument writes makes G1's "
                                "age guard refuse on a clean run."})
    return out


# ------------------------------------------------------------ freeze check
def freeze_check(paths):
    """The frozen file IS the file that ran: disk == git blob at HEAD."""
    out = {}
    for rel in paths:
        disk = os.path.join(REPO, rel)
        if not os.path.isfile(disk):
            refuse("FREEZE", {"absent_on_disk": rel})
        on_disk = md5_of(disk)
        try:
            blob = subprocess.run(["git", "-C", REPO, "cat-file", "blob",
                                   "HEAD:%s" % rel],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  check=True).stdout
        except Exception as e:                                   # noqa: BLE001
            refuse("FREEZE", {"git_cat_file_failed": rel, "error": repr(e)[:300]})
        committed = hashlib.md5(blob).hexdigest()
        out[rel] = {"on_disk_md5": on_disk, "committed_blob_md5_HEAD": committed,
                    "disk_equals_committed_blob": on_disk == committed}
        if on_disk != committed:
            refuse("FREEZE", {"path": rel, "on_disk_md5": on_disk,
                              "committed_blob_md5_HEAD": committed,
                              "note": "the grading path is fixed at the "
                                      "pre-registration commit (rule 2)"})
    return out


# ------------------------------------------------------------ ledger reader
_TOK = re.compile(r'(?P<k>[A-Za-z_][\w(),]*)=(?P<v>\[[^\]]*\]|\S*)')


def parse_ledger(path):
    """Return {arm: row-dict} plus the raw extra lines.  REFUSES on a duplicate
    arm row -- D6's grader silently kept the last of two, and a strengthening
    can only turn a pass into a stop."""
    if not os.path.isfile(path):
        refuse("LEDGER", {"absent": path})
    rows, extra, seen = {}, [], []
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.startswith("ARM="):
                extra.append(line)
                continue
            rec = {m.group("k"): m.group("v") for m in _TOK.finditer(line)}
            arm = rec.get("ARM")
            seen.append(arm)
            if arm in rows:
                refuse("LEDGER", {"duplicate_arm_row": arm, "arms_seen": seen,
                                  "note": "refused, not last-wins"})
            rec["_raw"] = line
            rows[arm] = rec
    return rows, extra


def read_chain_status(path):
    """REFUSES on multiplicity: exactly one `chain=started`, at most one
    terminal outcome (D6R AMENDMENT 1)."""
    if not os.path.isfile(path):
        return None
    started, terminal, arm_rc = [], [], {}
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("chain=started"):
                started.append(line)
            elif line.startswith("chain="):
                terminal.append(line)
            elif line.startswith("arm="):
                m = re.match(r'arm=(\S+)\s+rc=(-?\d+)', line)
                if m:
                    arm_rc[m.group(1)] = int(m.group(2))
    if len(started) != 1:
        refuse("CHAIN_STATUS", {"n_chain_started": len(started),
                               "note": "a second fire into an existing root "
                                       "makes the census unreadable"})
    if len(terminal) > 1:
        refuse("CHAIN_STATUS", {"n_terminal_outcomes": len(terminal),
                               "lines": terminal})
    out = {"started": started[0], "arm_rc": arm_rc, "terminal": None,
           "outcome": None, "stop_arm": None, "stop_rc": None, "not_run": []}
    if terminal:
        t = terminal[0]
        out["terminal"] = t
        m = re.match(r'chain=(\S+)', t)
        out["outcome"] = m.group(1) if m else None
        m = re.search(r'\barm=(\S+)', t)
        out["stop_arm"] = m.group(1) if m else None
        m = re.search(r'\brc=(-?\d+)', t)
        out["stop_rc"] = int(m.group(1)) if m else None
        m = re.search(r'not_run=\[([^\]]*)\]', t)
        out["not_run"] = m.group(1).split() if m else []
    return out


# ------------------------------------------------------------- arm census
def arm_census(root, ledger_rows, chain):
    """1 ledger row -> RAN.  2 no row, chain accounts for the absence ->
    NOT_RUN with its reason.  3 otherwise REFUSE."""
    census = {}
    for arm in ARMS:
        if arm in ledger_rows:
            census[arm] = {"state": "RAN", "source": "ledger_row"}
            continue
        if chain and chain["outcome"] in REGISTERED_CHAIN_OUTCOMES \
                and arm in chain["not_run"]:
            census[arm] = {"state": "NOT_RUN",
                           "reason": "REGISTERED_CHAIN_%s" % chain["outcome"],
                           "stop_arm": chain["stop_arm"],
                           "stop_rc": chain["stop_rc"],
                           "chain_record": os.path.join(root, "STATUS.chain"),
                           "note": "the registration names this outcome; the "
                                   "arm bought 0 core-min"}
            continue
        refuse("CENSUS", {"arm": arm, "arm_absent_from_ledger": True,
                          "chain_outcome": (chain or {}).get("outcome"),
                          "chain_not_run": (chain or {}).get("not_run"),
                          "note": "COMPLETE accounts for nothing -- after a "
                                  "complete chain no arm may be missing"})
    return census


# ------------------------------------------------------------------- G1
def gate_g1(root, ledger_rows, census):
    res = {"gate": "G1_completion", "arms": {}, "all_arms_ran": True,
           "ran_clean": True, "not_measured": []}
    for arm in ARMS:
        st = census[arm]
        if st["state"] != "RAN":
            res["all_arms_ran"] = False
            res["arms"][arm] = {"state": "NOT_RUN", "reason": st.get("reason"),
                                "core_min": 0.0}
            continue
        row = ledger_rows[arm]
        a = {"state": "RAN", "arm_kind": ARM_KIND[arm]}
        rc = int(row.get("rc", "999"))
        insp = row.get("inspect(exit,oomkilled)", "[]").strip("[]").split()
        if len(insp) != 2:
            refuse("G1", {"arm": arm, "inspect_field_unreadable": row.get(
                "inspect(exit,oomkilled)")})
        kernel_rc, oom = int(insp[0]), insp[1]
        if kernel_rc != rc:
            refuse("G1", {"arm": arm, "harness_rc": rc, "kernel_rc": kernel_rc,
                          "note": "harness and kernel disagree on rc"})
        a["rc"] = rc
        a["kernel_rc"] = kernel_rc
        a["oomkilled"] = oom
        a["rc_clause_pass"] = (rc == 0)
        a["oom_clause_pass"] = (oom == "false")

        log = os.path.join(root, row.get("log", ""))
        if not os.path.isfile(log):
            refuse("G1", {"arm": arm, "log_absent": log,
                          "note": "a log is PHYSICS, not infrastructure"})
        a["log"] = log
        if ARM_KIND[arm] == "SOLVER":
            last = None
            with open(log, errors="replace") as fh:
                for line in fh:
                    s = line.strip()
                    if s:
                        last = s
            a["terminal_last_line"] = last
            a["terminal_clause_pass"] = (last == TERMINAL_STATEMENT)
        else:
            ok = [f for f in os.listdir(root)
                  if f.startswith(os.path.basename(log) + ".ok.")]
            a["ok_markers"] = ok
            a["terminal_clause_pass"] = (len(ok) == 1)

        # ---- the AGE GUARD (rule 4) -------------------------------------
        wd = os.path.join(root, ARM_DIR[arm])
        datum_file = os.path.join(wd, ".d4_age_datum")
        if not os.path.isfile(datum_file):
            refuse("G1", {"arm": arm, "age_datum_absent": datum_file,
                          "note": "without the datum the age guard cannot run, "
                                  "and the age guard is PHYSICS"})
        with open(datum_file) as fh:
            datum = float(fh.read().strip())
        ages, age_pass = {}, True
        for prod in REGISTERED_PRODUCTS[arm]:
            p = os.path.join(wd, prod)
            if not os.path.isfile(p):
                refuse("G1", {"arm": arm, "registered_product_absent": p,
                              "note": "the producing arm RAN, so an absent "
                                      "product refuses (D6's behaviour, kept)"})
            mt = os.stat(p).st_mtime
            ages[prod] = {"mtime": mt, "newer_than_datum": mt > datum}
            age_pass = age_pass and mt > datum
        a["age_datum"] = datum
        a["age_detail"] = ages
        a["age_clause_pass"] = age_pass

        a["core_min"] = _f(row.get("core_min", "nan"))
        a["wall_s"] = _f(row.get("wall_s", "nan"))
        a["ranks"] = int(row.get("ranks", "0"))
        a["clauses_all_pass"] = all([a["rc_clause_pass"], a["oom_clause_pass"],
                                     a["terminal_clause_pass"],
                                     a["age_clause_pass"]])
        if not a["clauses_all_pass"]:
            res["ran_clean"] = False
        res["arms"][arm] = a
    return res


# ---------------------------------------------------- G-CAPS / G9 / G12
def gate_caps(ledger_rows, census):
    res = {"gate": "G-CAPS", "arms": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN", "core_min": 0.0}
            continue
        row = ledger_rows[arm]
        cm = _f(row.get("core_min", "nan"))
        cap = CAPS[arm]
        a = {"core_min": cm, "cap_core_min": cap, "within_cap": cm <= cap}
        inv = (TMO[arm] + FRAME_ALLOWANCE_S) * RANKS / 60.0
        a["deadline_in_container_s"] = TMO[arm]
        a["cap_inversion_core_min"] = inv
        a["inversion_matches_cap"] = abs(inv - cap) <= CAP_INVERSION_TOL_CORE_MIN
        cw = row.get("container_wall_s")
        if cw in (None, "", "NOT_MEASURED"):
            a["container_wall_s"] = "NOT_MEASURED"
            a["deadline_frame_pass"] = "NOT_MEASURED"
            a["frame_gap_within_allowance"] = "NOT_MEASURED"
            res["not_measured"].append("%s/container_wall_s" % arm)
        else:
            cwv = _f(cw)
            a["container_wall_s"] = cwv
            a["deadline_frame_pass"] = cwv <= TMO[arm] + KILL_GRACE_S
            gap = _f(row.get("wall_s", "nan")) - cwv
            a["host_minus_container_s"] = gap
            a["frame_gap_within_allowance"] = gap <= FRAME_GAP_ALLOWANCE_S
        fa = row.get("frame_allowance_s")
        a["frame_allowance_matches_registered"] = (
            fa is not None and int(_f(fa)) == FRAME_ALLOWANCE_S)
        limbs = [a["within_cap"], a["inversion_matches_cap"],
                 a["frame_allowance_matches_registered"]]
        for k in ("deadline_frame_pass", "frame_gap_within_allowance"):
            if a[k] is not True and a[k] != "NOT_MEASURED":
                limbs.append(False)
        a["verdict"] = "PASS" if all(limbs) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


def gate_toolchain(root, ledger_rows, census):
    res = {"gate": "G9_toolchain", "arms": {}, "verdict": "PASS",
           "shipped_row": "NAMED UNBOUGHT: %s" % DIGEST_SHIPPED}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN"}
            continue
        row = ledger_rows[arm]
        a = {"row": row.get("ROW"), "digest": row.get("DIGEST")}
        a["digest_is_patched"] = (row.get("DIGEST") == DIGEST_PATCHED)
        a["row_is_patched"] = (row.get("ROW") == "PATCHED")
        log = os.path.join(root, row.get("log", ""))
        seen = None
        if os.path.isfile(log):
            with open(log, errors="replace") as fh:
                for line in fh:
                    if "D4S_IDWARP_SO_MD5:" in line or "D4_IDWARP_SO_MD5:" in line:
                        seen = line.strip().split(":")[-1].strip()
                        break
        a["idwarp_so_md5_in_log"] = seen
        a["idwarp_so_md5_matches"] = (seen == IDWARP_SO_MD5)
        a["verdict"] = "PASS" if all([a["digest_is_patched"], a["row_is_patched"],
                                      a["idwarp_so_md5_matches"]]) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


def gate_placement(ledger_rows, census):
    res = {"gate": "G12_placement", "arms": {}, "verdict": "PASS",
           "not_measured": []}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN"}
            continue
        row = ledger_rows[arm]
        a = {"cpuset": row.get("cpuset"), "memory": row.get("memory")}
        a["cpuset_matches_registered"] = (row.get("cpuset") == CPUSET)
        a["memory_matches_registered"] = (row.get("memory") == MEMORY)
        dm = row.get("delivered_cores_mean", "[]").strip("[]").split()
        if not dm or dm[0] == "NOT_MEASURED":
            a["delivered_cores_mean"] = "NOT_MEASURED"
            a["delivered_pass"] = "NOT_MEASURED"
            res["not_measured"].append("%s/delivered_cores_mean" % arm)
        else:
            a["delivered_cores_mean"] = _f(dm[0])
            a["delivered_pass"] = a["delivered_cores_mean"] >= DELIVERED_MIN
        limbs = [a["cpuset_matches_registered"], a["memory_matches_registered"]]
        if a["delivered_pass"] is not True and a["delivered_pass"] != "NOT_MEASURED":
            limbs.append(False)
        a["verdict"] = "PASS" if all(limbs) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


# -------------------------------------------------------------- G-DVL
DV_KEYS = ("twist", "shape", "patchV_cl04", "patchV_cl05", "patchV_cl06")


def _dv_finiteness(path, artefact):
    """Section 3f over a PHYSICAL design-vector artefact.  Raises `NonFinite`
    naming the first offending component; returns the census otherwise."""
    if not os.path.isfile(path):
        refuse("G-DVL", {"artefact_absent_although_producer_ran": path})
    with open(path) as fh:
        doc = json.load(fh)
    out = {"n_checked": 0, "keys": {}}
    for k in DV_KEYS:
        if k not in doc:
            continue
        vals = doc[k]
        out["keys"][k] = len(vals)
        for i, v in enumerate(vals):
            out["n_checked"] += 1
            _ff(v, artefact, "%s[%d]" % (k, i))
    if out["n_checked"] == 0:
        refuse("G-DVL", {"path": path, "no_registered_dv_family_present": True,
                         "keys_present": sorted(doc)[:40],
                         "note": "a finiteness control with nothing to check "
                                 "is not a control (L-302)"})
    return out


def gate_dvl(root, census, runscript_d6r, runscript_d4):
    """Re-read BOTH published physical artefacts from disk and re-assert the two
    locus controls at GRADING time.  Never trusts the producer's say-so."""
    sys.path.insert(0, HERE)
    import d6rf3_endpoint_locus as locus
    res = {"gate": "G-DVL_endpoint_locus", "arms": {}}
    verdicts = []
    for arm, art, rs in (("F_mp", "d6rf3_endpoint_dvs_PHYSICAL.json", runscript_d6r),
                         ("REF_off", "d4_endpoint_dvs_PHYSICAL.json", runscript_d4)):
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"verdict": "NOT A RESULT",
                                "reason": "ARM_DID_NOT_RUN",
                                "producing_arm": arm, "artefact": art}
            verdicts.append("NOT A RESULT")
            continue
        path = os.path.join(root, ARM_DIR[arm], art)
        # ---- section 3f binds G-DVL --------------------------------------
        # Checked HERE, at the grader's boundary, and NOT by editing
        # `d6rf3_endpoint_locus.py`: a non-finite design component makes every
        # locus control (pinned witness, bounds containment) return False for
        # a reason that has nothing to do with the locus, which would read as
        # `GATE FAIL -- the design point is not the one the registration
        # names`. That is the wrong finding stated confidently.
        try:
            nf = _dv_finiteness(path, art)
        except NonFinite as e:
            r = _nar_non_finite({"artefact": path,
                                 "registration_source": rs}, e)
            res["arms"][arm] = r
            verdicts.append("NOT A RESULT")
            continue
        try:
            r = locus.gate(path, rs)
            r["verdict"] = "PASS"
        except locus.LocusRefusal as e:
            r = {"verdict": "GATE FAIL", "artefact": path,
                 "registration_source": rs, "control_refusal": str(e)[:900]}
        r["finiteness"] = nf
        res["arms"][arm] = r
        verdicts.append(r["verdict"])
    res["verdict"] = ("NOT A RESULT" if "NOT A RESULT" in verdicts else
                      ("GATE FAIL" if "GATE FAIL" in verdicts else "PASS"))
    return res


# -------------------------------------------- readers + planted-zero controls
def read_fd(path):
    """THE FD READER.  One function, used for the real artefact AND for the
    planted copy -- a control that exercises a different reader controls
    nothing."""
    with open(path) as fh:
        doc = json.load(fh)
    rows = []
    for r in doc.get("rows", []):
        rec = {"dv": r.get("dv"), "idx": r.get("idx"), "status": r.get("status")}
        if r.get("status") == "PLANNED":
            rec["J_adj"] = _f(r.get("J_adj"))
            fd = r.get("fd") or {}
            for lab in ("s_lo", "s_hi"):
                leg = fd.get(lab) or {}
                rec[lab] = {"ok": bool(leg.get("ok")),
                            "step": leg.get("step"),
                            "d": _f(leg["d"]) if leg.get("ok") else None}
        rows.append(rec)
    return {"rows": rows, "n_rows": doc.get("n_rows"),
            "eta_used": _f(doc.get("eta_used", "nan")),
            "eta_floored": doc.get("eta_floored"),
            "producer_md5": doc.get("producer_md5")}


def plant_into_fd(src, dst):
    """Plant PLANT into the FIRST PLANNED row's s_hi derivative, BY KEY, and
    write the perturbed copy.  Returns the row identity that was planted."""
    with open(src) as fh:
        doc = json.load(fh)
    for r in doc.get("rows", []):
        if r.get("status") != "PLANNED":
            continue
        leg = (r.get("fd") or {}).get("s_hi") or {}
        if not leg.get("ok"):
            continue
        leg["d"] = repr(float(leg["d"]) + PLANT)
        with open(dst, "w") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        return {"dv": r.get("dv"), "idx": r.get("idx")}
    return None


def read_d4_cd_f(path):
    """THE PRICE READER.  Takes the LAST field of the single `^Objective` line
    of D4's IPOPT summary.  Refuses on zero or more than one such line."""
    if not os.path.isfile(path):
        refuse("PRICE_READER", {"absent": path})
    hits = []
    with open(path, errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if line.startswith("Objective"):
                hits.append((i, line.rstrip("\n")))
    if len(hits) != 1:
        refuse("PRICE_READER", {"n_objective_lines": len(hits), "path": path})
    parts = hits[0][1].replace(":", " ").split()
    return _f(parts[-1]), {"line_no": hits[0][0], "line": hits[0][1]}


def plant_into_d4(src, dst):
    """Plant PLANT into the objective on a COPY, BY LINE INDEX."""
    with open(src, errors="replace") as fh:
        lines = fh.readlines()
    idx = [i for i, l in enumerate(lines) if l.startswith("Objective")]
    if len(idx) != 1:
        refuse("PRICE_PLANT", {"n_objective_lines": len(idx)})
    i = idx[0]
    parts = lines[i].replace(":", " ").split()
    val = float(parts[-1]) + PLANT
    lines[i] = "Objective...............:   %.16e    %.16e\n" % (val, val)
    with open(dst, "w") as fh:
        fh.writelines(lines)
        fh.flush()
        os.fsync(fh.fileno())
    return i + 1


def run_planted_controls(ctrl_dir, fd_path):
    """CLAUDE.md rule 3.  THREE controls now, not two -- section 3e.  Each
    plants, reads back FROM DISK through the SAME reader the gate uses, and
    REFUSES if the reader is blind.  Each asserts the unperturbed original is
    byte-unchanged: a control that modifies what it grades is not a control.

    EVERY CONTROL REPORTS ONE OF THREE STATES -- `EXERCISED-PASS`,
    `EXERCISED-FAIL`, `NOT EXERCISED` -- and `NOT EXERCISED` is printed beside
    the verdict, never counted as a pass and never inferred from the absence of
    a failure.  `DAFOAM_CHARTER.md` section 18.5 records this as a PROPOSAL for
    the whole lab and deliberately does NOT enact it there, because that is
    Sanaa's call; it is taken here, inside this item's own comparator, where
    this item may take it.  The finding behind it is this lineage's own: D6R's
    frozen grader short-circuited `g_price` when an arm did not run, so its
    planted control never executed and nothing said so -- the control's silence
    and the control's success were indistinguishable in the record."""
    os.makedirs(ctrl_dir, exist_ok=True)
    out = {"PLANT": PLANT, "rel_tol": PLANT_REL_TOL}

    # ---- control 1: the FD reader ----
    if fd_path is None or not os.path.isfile(fd_path):
        out["fd_control"] = {"state": cdc.NOT_EXERCISED,
                             "reader_saw_the_plant": None,
                             "why": "the FD artefact's producing arm did "
                                    "not run; there is nothing to read and "
                                    "no gate is computed from it"}
    else:
        m_before = md5_of(fd_path)
        base = read_fd(fd_path)
        planted_copy = os.path.join(ctrl_dir, "d6r_fd_endpoint.PLANTED.json")
        who = plant_into_fd(fd_path, planted_copy)
        if who is None:
            refuse("PLANT_FD", {"no_PLANNED_row_with_an_ok_s_hi_leg": True,
                                "note": "a control with nothing to plant into "
                                        "is not a control (L-302)"})
        got = read_fd(planted_copy)
        b = [r for r in base["rows"]
             if r["dv"] == who["dv"] and r["idx"] == who["idx"]][0]["s_hi"]["d"]
        g = [r for r in got["rows"]
             if r["dv"] == who["dv"] and r["idx"] == who["idx"]][0]["s_hi"]["d"]
        delta = g - b
        seen = abs(delta - PLANT) <= PLANT_REL_TOL * max(abs(PLANT), abs(b), 1.0)
        m_after = md5_of(fd_path)
        out["fd_control"] = {"planted_into": who, "unperturbed": b,
                             "planted_read_back": g, "delta": delta,
                             "reader_saw_the_plant": seen,
                             "state": (cdc.EXERCISED_PASS if seen
                                       else cdc.EXERCISED_FAIL),
                             "original_md5_before": m_before,
                             "original_md5_after": m_after,
                             "original_unchanged": m_before == m_after,
                             "planted_copy": planted_copy}
        if not seen:
            refuse("PLANT_FD", out["fd_control"])
        if m_before != m_after:
            refuse("PLANT_FD", {"the_control_modified_the_artefact_it_grades":
                                True, **out["fd_control"]})

    # ---- control 2: the D4 price reader ----
    m_before = md5_of(D4_OPT_IPOPT)
    base_cd, where = read_d4_cd_f(D4_OPT_IPOPT)
    planted_copy = os.path.join(ctrl_dir, "d4_opt_IPOPT.PLANTED.txt")
    ln = plant_into_d4(D4_OPT_IPOPT, planted_copy)
    got_cd, _ = read_d4_cd_f(planted_copy)
    delta = got_cd - base_cd
    seen = abs(delta - PLANT) <= PLANT_REL_TOL * max(abs(PLANT), abs(base_cd), 1.0)
    m_after = md5_of(D4_OPT_IPOPT)
    out["price_control"] = {"planted_at_line": ln, "unperturbed": base_cd,
                            "planted_read_back": got_cd, "delta": delta,
                            "reader_saw_the_plant": seen,
                            "state": (cdc.EXERCISED_PASS if seen
                                      else cdc.EXERCISED_FAIL),
                            "source_line": where,
                            "original_md5_before": m_before,
                            "original_md5_after": m_after,
                            "original_unchanged": m_before == m_after,
                            "planted_copy": planted_copy}
    if not seen:
        refuse("PLANT_PRICE", out["price_control"])
    if m_before != m_after:
        refuse("PLANT_PRICE", {"the_control_modified_D4s_preserved_artefact":
                               True, **out["price_control"]})

    # ---- control 3: THE CD READER -- NEW, because the SOURCE MOVED ---------
    # Section 3e.  `G-OFF` and `G-PRICE` no longer read CD from the producing
    # history (D6RF3-DEF-4: it contains none) but from the FD arm's own
    # baseline primal.  A CD read from a new source is not evidence until a
    # reader has been shown able to see a non-zero in it.  The control and the
    # graded path are LITERALLY THE SAME FUNCTION -- `cdc.read_cd` -- so the
    # control cannot drift away from what it controls.
    try:
        out["cd_control"] = cdc.run_cd_control(ctrl_dir, fd_path)
    except cdc.CDRefusal as e:
        refuse("PLANT_CD", {"cd_control_refused": str(e)[:1500]})

    out["control_states"] = {k: out[k].get("state")
                             for k in ("fd_control", "price_control",
                                       "cd_control")}
    out["n_not_exercised"] = sum(1 for v in out["control_states"].values()
                                 if v == cdc.NOT_EXERCISED)
    with open(os.path.join(ctrl_dir, "planted_controls.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    return out


# ---------------------------------------------------------------- G-FD
def gate_fd(root, census):
    art = "d6rf3_fd_endpoint.json"
    producer = ARTEFACT_PRODUCER[art]
    base = {"gate": "G-FD_bright_line_on_J", "artefact": art,
            "producing_arm": producer, "band_pct": FD_BAND_PCT,
            "aggregate_band_pct": AGG_BAND_PCT,
            "plateau_tol_pct": PLATEAU_TOL_PCT,
            "sign_flip_pathology_at": SIGN_FLIP_PATHOLOGY,
            "band_provenance": "band D, inherited BY CITATION from D6R "
                               "PREREGISTRATION.md section 3e; NOT re-derived"}
    if census[producer]["state"] != "RAN":
        base.update({"verdict": "NOT A RESULT", "reason": "ARM_DID_NOT_RUN",
                     "arm_state": census[producer],
                     "note": "the arm that writes this artefact did not run, "
                             "so this gate has NO INPUT. That is NOT a GATE "
                             "FAIL -- nothing was measured that could fail."})
        return base
    path = os.path.join(root, ARM_DIR[producer], art)
    if not os.path.isfile(path):
        refuse("G-FD", {"artefact_absent_although_producer_ran": path})
    doc = read_fd(path)
    comps, flips, num, den = [], 0, 0.0, 0.0
    n_planned = 0
    n_nonfinite = 0
    for r in doc["rows"]:
        c = {"dv": r["dv"], "idx": r["idx"], "status": r["status"]}
        if r["status"] != "PLANNED":
            c["verdict"] = "NOT A RESULT"
            c["reason"] = "component status %s -- no FD was taken" % r["status"]
            comps.append(c)
            continue
        lo, hi = r.get("s_lo") or {}, r.get("s_hi") or {}
        if not (lo.get("ok") and hi.get("ok")):
            c["verdict"] = "NOT A RESULT"
            c["reason"] = "an FD step did not evaluate"
            c["s_lo_ok"], c["s_hi_ok"] = lo.get("ok"), hi.get("ok")
            comps.append(c)
            continue
        n_planned += 1
        d_hi, d_lo, jadj = hi["d"], lo["d"], r["J_adj"]
        # ---- section 3f, per component -----------------------------------
        try:
            jadj = _ff(jadj, art, "rows[%s[%s]].J_adj" % (r["dv"], r["idx"]))
            d_lo = _ff(d_lo, art, "rows[%s[%s]].fd.s_lo.d" % (r["dv"], r["idx"]))
            d_hi = _ff(d_hi, art, "rows[%s[%s]].fd.s_hi.d" % (r["dv"], r["idx"]))
        except NonFinite as e:
            c.update(_nar_non_finite({}, e))
            n_nonfinite += 1
            comps.append(c)
            continue
        c.update({"J_adj": jadj, "d_s_lo": d_lo, "d_s_hi": d_hi,
                  "step_lo": lo["step"], "step_hi": hi["step"]})
        c["rel_err_pct"] = (abs(d_hi - jadj) / abs(d_hi) * 100.0
                            if d_hi != 0.0 else float("inf"))
        c["plateau_pct"] = (abs(d_hi - d_lo) / abs(d_hi) * 100.0
                            if d_hi != 0.0 else float("inf"))
        # ---- the plateau, per DAFOAM_CHARTER.md section 3 and section 20 ---
        # The `s_lo`/`s_hi` pair IS `VERIFICATION_CHARTER.md` section 7 step
        # 1's "two or three point mini-sweep", which section 3 delegates the
        # definition to and section 20 (addendum 2026-09-04) RULES satisfies
        # section 3.  No shortfall caveat is printed and none is owed.
        # WHAT IS PRINTED, because it is TRUE and is strength of evidence
        # rather than compliance: the pair is graded at `s_hi` with its only
        # neighbour BELOW, so the coarse side is unmeasured.  This family has a
        # measured instance of that blind side firing.
        c["plateau_proved_against"] = [lo["step"]]
        c["plateau_graded_at"] = hi["step"]
        c["plateau_sidedness"] = "ONE-SIDED (fine side only; coarse unmeasured)"
        c["plateau_authority"] = (
            "VERIFICATION_CHARTER.md:854-855 step 1, two-or-three-point "
            "mini-sweep; DAFOAM_CHARTER.md section 3 delegates to it and "
            "section 20 rules that a two-point mini-sweep SATISFIES section 3")
        c["coarse_side_note"] = (
            "A third, COARSER point is the cheapest evidence available and is "
            "a STRENGTHENING, not a duty; declining it is not a breach "
            "(DAFOAM_CHARTER.md section 20.2). Measured instance of the blind "
            "side firing: D15_D16_FD_STEP_TABLE.md:234, D16 PATCHED CL "
            "shape[6], 14.0978 % coarse-side deviation against 1.1268 % "
            "fine-side. THIS ITEM DECLINES THE THIRD POINT AND SAYS SO.")
        c["sign_flip"] = (d_hi * jadj) < 0.0
        if c["sign_flip"]:
            flips += 1
        c["in_band"] = c["rel_err_pct"] <= FD_BAND_PCT
        c["plateau_pass"] = c["plateau_pct"] <= PLATEAU_TOL_PCT
        c["verdict"] = ("PASS" if (c["in_band"] and c["plateau_pass"]
                                   and not c["sign_flip"]) else "GATE FAIL")
        num += (d_hi - jadj) ** 2
        den += d_hi ** 2
        comps.append(c)
    base["components"] = comps
    base["n_planned"] = n_planned
    base["n_non_finite_components"] = n_nonfinite
    base["sign_flips"] = flips
    base["eta_used"] = doc["eta_used"]
    base["eta_floored"] = doc["eta_floored"]
    base["plateau_authority"] = (
        "VERIFICATION_CHARTER.md:854-855 step 1's two-or-three-point "
        "mini-sweep. DAFOAM_CHARTER.md section 20 rules that the two-point "
        "ladder SATISFIES section 3; NO SHORTFALL CAVEAT IS OWED and printing "
        "one would be a false self-deprecation.")
    # ---- section 3f on eta: the aggregate is scaled by it ------------------
    try:
        _ff(doc["eta_used"], art, "eta_used")
    except NonFinite as e:
        return _nar_non_finite(base, e)
    if n_planned == 0:
        base.update({"verdict": "NOT A RESULT",
                     "reason": ("no component produced a usable FD pair"
                                if n_nonfinite == 0 else
                                "no component produced a FINITE FD pair; %d "
                                "were non-finite" % n_nonfinite)})
        return base
    agg = (math.sqrt(num) / math.sqrt(den) * 100.0
           if den > 0 else float("inf"))
    # ---- section 3f on the aggregate --------------------------------------
    # `inf` is non-finite and reaches here when every `d_hi` is zero.  It is
    # NOT a 100 %-style failure to be graded GATE FAIL; it is an absent
    # measurement wearing a float's type.
    if not math.isfinite(agg):
        return _nar_non_finite(base, NonFinite(
            art, "aggregate_rel_err_pct", repr(agg)))
    base["aggregate_rel_err_pct"] = agg
    base["aggregate_pass"] = base["aggregate_rel_err_pct"] <= AGG_BAND_PCT
    if flips >= SIGN_FLIP_PATHOLOGY:
        base["pathology_NOT_A_RESULT"] = True
        base["verdict"] = "NOT A RESULT"
        base["reason"] = ("%d sign flips >= the registered pathology threshold "
                          "%d -- named in advance" % (flips, SIGN_FLIP_PATHOLOGY))
        return base
    base["pathology_NOT_A_RESULT"] = False
    per_ok = all(c.get("verdict") == "PASS" for c in comps
                 if c.get("status") == "PLANNED" and "verdict" in c
                 and c.get("rel_err_pct") is not None)
    any_nar = any(c.get("verdict") == "NOT A RESULT" for c in comps)
    if any_nar:
        base["verdict"] = "NOT A RESULT"
        base["reason"] = "at least one registered component produced no FD pair"
    else:
        base["verdict"] = "PASS" if (per_ok and base["aggregate_pass"]) else "GATE FAIL"
    return base


# ------------------------------------------------------- G-OFF / G-PRICE
def _major_history(root, census):
    art = "d6rf3_major_history.json"
    producer = ARTEFACT_PRODUCER[art]
    if census[producer]["state"] != "RAN":
        return None, producer, art
    path = os.path.join(root, ARM_DIR[producer], art)
    if not os.path.isfile(path):
        refuse("MAJOR_HISTORY", {"absent_although_producer_ran": path})
    with open(path) as fh:
        return json.load(fh), producer, art


def _cd_path(root, census):
    """The path of section 2a's registered CD source, or None if its producing
    arm did not run."""
    producer = ARTEFACT_PRODUCER[CD_ARTEFACT]
    if census[producer]["state"] != "RAN":
        return None, producer
    p = os.path.join(root, ARM_DIR[producer], CD_ARTEFACT)
    if not os.path.isfile(p):
        refuse("CD_SOURCE", {"absent_although_producer_ran": p})
    return p, producer


def gate_off(root, census):
    """G-OFF, section 3a.  RE-POINTED: `CD_i(mp)` is section 2a's source.

    `d6rf2_grade.py:760` read `hist["CD_<pt>"][-1]` from the producing
    optimiser's history.  D6RF3-DEF-4 established by COMPLETE ENUMERATION that
    the history holds no CD at all, and D6RF3-DEF-5 established that its last
    row is `NaN` throughout -- so on the frozen parent, had the extractor not
    refused first, all three points would have read `GATE FAIL` off a
    non-number, because `NaN <= cd_ref` is False."""
    res = {"gate": "G-OFF_per_point",
           "artefacts": [CD_ARTEFACT, "d6rf3_ref_off.json"],
           "CD_mp_source": CD_MP_SOURCE_LABEL,
           "CD_mp_source_statement": CD_MP_SOURCE_STATEMENT,
           "caveat": ("The producing optimisation exited `Invalid number in "
                      "NLP function or derivative detected.` (D6R "
                      "O_mp/opt_IPOPT.txt:822, G-D6R-OPT UNCLASSIFIED) and 687 "
                      "of its 863 recorded funcs rows are non-finite. The "
                      "endpoint is a design point, not an optimum, and this "
                      "gate makes no optimality claim."),
           "per_point": {}}
    cdp, cdprod = _cd_path(root, census)
    if cdp is None:
        res.update({"verdict": "NOT A RESULT", "reason": "ARM_DID_NOT_RUN",
                    "producing_arm": cdprod, "artefact": CD_ARTEFACT,
                    "per_point": {p: {"verdict": "NOT A RESULT",
                                      "reason": "ARM_DID_NOT_RUN",
                                      "CD_mp_source": CD_MP_SOURCE_LABEL}
                                  for p in POINTS}})
        return res
    if census["REF_off"]["state"] != "RAN":
        res.update({"verdict": "NOT A RESULT", "reason": "ARM_DID_NOT_RUN",
                    "producing_arm": "REF_off", "artefact": "d6rf3_ref_off.json",
                    "per_point": {p: {"verdict": "NOT A RESULT",
                                      "reason": "ARM_DID_NOT_RUN",
                                      "CD_mp_source": CD_MP_SOURCE_LABEL}
                                  for p in POINTS}})
        return res
    rp = os.path.join(root, ARM_DIR["REF_off"], "d6rf3_ref_off.json")
    if not os.path.isfile(rp):
        refuse("G-OFF", {"artefact_absent_although_producer_ran": rp})
    with open(rp) as fh:
        ref = json.load(fh)
    verds = []
    for p in POINTS:
        row = {"CL_target": CL_TARGETS[p], "CD_mp_source": CD_MP_SOURCE_LABEL,
               "CD_mp_key": "points.%s.CD" % p, "CD_mp_artefact": CD_ARTEFACT}
        if p not in ref.get("points", {}):
            refuse("G-OFF", {"ref_off_missing_point": p})
        try:
            # ONE reader for CD, shared with the section 3e control.
            cd_mp = _ff(cdc.read_cd(cdp, p), CD_ARTEFACT, "points.%s.CD" % p)
            cd_ref = _ff(ref["points"][p]["CD"], "d6rf3_ref_off.json",
                         "points.%s.CD" % p)
            cl_ref = _ff(ref["points"][p]["CL"], "d6rf3_ref_off.json",
                         "points.%s.CL" % p)
        except cdc.CDRefusal as e:
            refuse("G-OFF", {"cd_reader_refused": str(e)[:1200]})
        except NonFinite as e:
            row.update(_nar_non_finite({}, e))
            res["per_point"][p] = row
            verds.append("NOT A RESULT")
            continue
        v = "PASS" if cd_mp <= cd_ref else "GATE FAIL"
        verds.append(v)
        row.update({"CD_mp": cd_mp, "CD_REF_off": cd_ref, "CL_REF_off": cl_ref,
                    "gain_REF_minus_mp": cd_ref - cd_mp, "verdict": v})
        res["per_point"][p] = row
    res["verdict"] = ("NOT A RESULT" if "NOT A RESULT" in verds else
                      ("PASS" if all(v == "PASS" for v in verds)
                       else "GATE FAIL"))
    return res


def report_cdlog(root, census):
    """`X-CDLOG`, section 3d.  REPORTED, NOT GATED.  NO THRESHOLD, NO VERDICT,
    AND IT MOVES NOTHING.

    Section 2b's registered reasons for demoting the stdout reconstruction to a
    cross-check: the SERIES is not reconstructable (977 converged primal
    terminations against the 2,589 point-primals implied by 863 major rows,
    distributed 760/110/98); the registered instrument's own docstring chose
    the history file over stdout because it is immune to the MPI interleave;
    and it cannot become the gated source without becoming outcome-selected
    (section 5).  A disagreement here is a FINDING TO BE REPORTED and does not
    move any gate, because the gated source was fixed before either number
    existed."""
    res = {"row": "X-CDLOG_stdout_cross_check", "gating": False,
           "threshold": None, "verdict": None,
           "log_source": CDLOG_SOURCE,
           "log_lines": CDLOG_LINES,
           "CD_log_at_last_finite_major": CDLOG,
           "composite_identity": {
               "weights": WEIGHTS,
               "J_history_row_998": CDLOG_J_AT_ROW_998,
               "residual_abs": CDLOG_COMPOSITE_RESID_ABS,
               "residual_rel": CDLOG_COMPOSITE_RESID_REL,
               "note": "sum(w_i*CD_i) against the history's J at the last "
                       "FINITE major, at the log's 10-significant-figure "
                       "print precision. It grades nothing and has no "
                       "direction."},
           "why_not_gated": ("section 2b, three registered reasons; and the "
                             "gated source was fixed before either number "
                             "existed"),
           "per_point": {}}
    cdp, cdprod = _cd_path(root, census)
    if cdp is None:
        res.update({"reason": "ARM_DID_NOT_RUN", "producing_arm": cdprod})
        return res
    for p in POINTS:
        try:
            cd_b = _f(cdc.read_cd(cdp, p))
        except cdc.CDRefusal as e:
            res["per_point"][p] = {"unreadable": str(e)[:400]}
            continue
        finite = math.isfinite(cd_b)
        rel = (abs(cd_b - CDLOG[p]) / abs(CDLOG[p])) if finite else None
        res["per_point"][p] = {"CD_baseline_primal": cd_b,
                               "CD_log_last_finite_major": CDLOG[p],
                               "abs_rel_difference": rel,
                               "finite": finite,
                               "CD_mp_source": CD_MP_SOURCE_LABEL}
    # Falsifier F1 (section 8), REPORTED: the primal's own repeatability,
    # measured in the same run as |J - J_repeat|, is the yardstick the
    # disagreement is read against.  F1 is a reported falsifier and does NOT
    # move G-OFF or G-PRICE.
    try:
        with open(cdp) as fh:
            doc = json.load(fh)
        res["F1_yardstick_eta_raw"] = _f(doc.get("eta_raw", "nan"))
        res["F1_statement"] = (
            "If points.<pt>.CD disagrees with the stdout reconstruction by "
            "more than the primal's own repeatability (eta_raw), section 2a's "
            "premise that the baseline primal measures the same physical "
            "quantity the log recorded is FALSE and this item reports that as "
            "its finding. REPORTED, not gated.")
    except (OSError, ValueError):
        res["F1_yardstick_eta_raw"] = None
    return res


def gate_price(root, census, controls):
    res = {"gate": "G-PRICE_single_point", "band": list(PRICE_BAND),
           "reference_recorded": CD_F_D4_RECORDED,
           "reference_source": D4_OPT_IPOPT}
    cd_f, where = read_d4_cd_f(D4_OPT_IPOPT)
    res["reference_reread"] = cd_f
    res["reference_line"] = where
    res["planted_control"] = controls.get("price_control", {}).get(
        "reader_saw_the_plant")
    res["planted_control_state"] = controls.get("price_control", {}).get("state")
    res["cd_planted_control_state"] = controls.get("cd_control", {}).get("state")
    res["CD_mp_source"] = CD_MP_SOURCE_LABEL
    res["CD_mp_source_statement"] = CD_MP_SOURCE_STATEMENT
    res["band_provenance"] = (
        "[0, 1.0e-3] and the negative -> NOT A RESULT limb are D6RF's, carried "
        "BYTE-FOR-BYTE and NOT WIDENED. Sanaa's standing boundary, 2026-09-04: "
        "`it never means adjusting the gate until the answer fits.`")
    if cd_f != CD_F_D4_RECORDED:
        refuse("G-PRICE", {"D4_reference_moved": {"recorded": CD_F_D4_RECORDED,
                                                  "reread": cd_f}})
    cdp, cdprod = _cd_path(root, census)
    if cdp is None:
        res.update({"verdict": "NOT A RESULT", "reason": "ARM_DID_NOT_RUN",
                    "producing_arm": cdprod, "artefact": CD_ARTEFACT})
        return res
    try:
        cd_mp = _ff(cdc.read_cd(cdp, "cl05"), CD_ARTEFACT, "points.cl05.CD")
    except cdc.CDRefusal as e:
        refuse("G-PRICE", {"cd_reader_refused": str(e)[:1200]})
    except NonFinite as e:
        # D6RF3-DEF-5's exact repair.  The parent computed `NaN - cd_f = NaN`,
        # found `NaN < 0.0` False so the registered `negative -> NOT A RESULT`
        # limb did NOT fire, found `NaN <= 1.0e-3` False so the PASS limb did
        # not fire, and reached `else` -> GATE FAIL.  A verdict manufactured
        # from a non-number.  It is NOT A RESULT here, and it is NOT A RESULT
        # for the stated reason, naming the artefact and the key.
        return _nar_non_finite(res, e)
    price = cd_mp - cd_f
    res["CD_cl05_mp"] = cd_mp
    res["price"] = price
    if price < 0.0:
        res["verdict"] = "NOT A RESULT"
        res["reason"] = ("a negative price is a finding about D4, named in "
                         "advance as pending triage")
    elif price <= PRICE_BAND[1]:
        res["verdict"] = "PASS"
    else:
        res["verdict"] = "GATE FAIL"
    return res


def report_reduction(root, census):
    """REPORTED, NOT GATED (Sanaa 2026-09-03 ~20:00Z)."""
    res = {"row": "R-RED_composite_reduction", "gating": False,
           "band_pct_for_reference": list(RED_BAND_PCT),
           "why_not_gated": ("the producing optimisation exited on a "
                             "non-finite objective (G-D6R-OPT UNCLASSIFIED), "
                             "so a reduction along its trajectory is a number, "
                             "not a claim about a converged optimum")}
    hist, hp, ha = _major_history(root, census)
    if hist is None:
        res.update({"value_pct": None, "reason": "ARM_DID_NOT_RUN",
                    "producing_arm": hp})
        return res
    J = [_f(v) for v in hist["J"]]
    res["n_major"] = len(J)
    res["n_non_finite_J"] = sum(1 for v in J if not math.isfinite(v))
    # ---- section 3c + section 3f: THE NON-FINITE DISCLOSURE ----------------
    # `J_f` from this history IS non-finite (D6RF3-DEF-5: the last row of the
    # producing history is index 1006 and every one of its `funcs` is NaN).
    # The row must SAY SO rather than print a number derived from one.  This
    # is a REPORTED row, so there is no verdict to make NOT A RESULT -- the
    # disclosure is the whole obligation, and a reduction printed from a NaN
    # would be exactly the "evidence annotated as non-binding" failure.
    try:
        j0 = _ff(J[0], "d6rf3_major_history.json", "J[0]")
        jf = _ff(J[-1], "d6rf3_major_history.json", "J[-1]")
    except NonFinite as e:
        res.update({"J0": J[0], "Jf": J[-1], "value_pct": None,
                    "reason": NON_FINITE_REASON, "non_finite": e.detail,
                    "inside_reference_band": None,
                    "disclosure": (
                        "NO REDUCTION IS PRINTED. %d of %d recorded J values "
                        "in this history are non-finite and the endpoint row "
                        "is one of them. A percentage computed from a NaN is "
                        "not a small number, it is not a number."
                        % (res["n_non_finite_J"], res["n_major"]))})
        return res
    res["J0"], res["Jf"] = j0, jf
    res["value_pct"] = (j0 - jf) / j0 * 100.0 if j0 != 0 else None
    res["inside_reference_band"] = (
        res["value_pct"] is not None
        and RED_BAND_PCT[0] <= res["value_pct"] <= RED_BAND_PCT[1])
    return res


# ------------------------------------------------------------- composition
def compose(g1, dvl, fd, off, price, caps, tool, place, census):
    """THE REGISTERED VERDICT LADDER, in order.  A NOT A RESULT can only turn a
    PASS or GATE FAIL INTO a NOT A RESULT, never the reverse."""
    reasons = []
    ran = [a for a in ARMS if census[a]["state"] == "RAN"]
    notrun = [a for a in ARMS if census[a]["state"] != "RAN"]

    dirty = [a for a in ran if not g1["arms"][a].get("clauses_all_pass")]
    if dirty:
        reasons.append("rung 1: completion clause failed on arm(s) %s" % dirty)
        return "NOT A RESULT", reasons
    if notrun:
        reasons.append("rung 2: registered arm(s) %s did not run; the item can "
                       "never be PASS with an arm unbought" % notrun)
        return "NOT A RESULT", reasons
    # ---- rung 3: ANY GATED INPUT NON-FINITE (section 3f, D6RF3-DEF-5) ------
    # Placed ABOVE the G-DVL and pathology rungs deliberately.  A gate whose
    # input was a NaN did not measure the thing its name says, so its GATE FAIL
    # or PASS is not evidence about the design point OR about the gradient, and
    # attributing it to either would be the confident wrong finding.
    nf = []
    for g in (dvl, fd, off, price):
        if g.get("reason") == NON_FINITE_REASON:
            nf.append({"gate": g.get("gate"), "non_finite": g.get("non_finite")})
        for p, row in (g.get("per_point") or {}).items():
            if row.get("reason") == NON_FINITE_REASON:
                nf.append({"gate": g.get("gate"), "point": p,
                           "non_finite": row.get("non_finite")})
        for c in (g.get("components") or []):
            if c.get("reason") == NON_FINITE_REASON:
                nf.append({"gate": g.get("gate"),
                           "component": "%s[%s]" % (c.get("dv"), c.get("idx")),
                           "non_finite": c.get("non_finite")})
    if nf:
        reasons.append("rung 3: gated input(s) NON-FINITE, artefact and key "
                       "named: %s" % json.dumps(nf, sort_keys=True,
                                                default=str)[:1500])
        return "NOT A RESULT", reasons
    if dvl["verdict"] == "GATE FAIL":
        reasons.append("rung 4: G-DVL GATE FAIL -- the design point on disk is "
                       "not the one the registration names, so nothing "
                       "downstream of it measures what it says")
        return "NOT A RESULT", reasons
    if fd.get("pathology_NOT_A_RESULT"):
        reasons.append("rung 5: the registered FD sign-flip pathology fired")
        return "NOT A RESULT", reasons
    if price["verdict"] == "NOT A RESULT" and price.get("price", 0.0) < 0.0:
        reasons.append("rung 5: negative single-point price -- a finding about "
                       "D4, named in advance")
        return "NOT A RESULT", reasons
    nar = [g["gate"] for g in (dvl, fd, off, price)
           if g.get("verdict") == "NOT A RESULT"]
    if nar:
        reasons.append("rung 6: gate(s) %s NOT A RESULT for want of an input" % nar)
        return "NOT A RESULT", reasons
    gf = [g["gate"] for g in (dvl, fd, off, price, caps, tool, place)
          if g.get("verdict") == "GATE FAIL"]
    if gf:
        reasons.append("rung 7: gate(s) %s GATE FAIL" % gf)
        return "GATE FAIL", reasons
    reasons.append("rung 8: every gated row PASS")
    return "PASS", reasons


# ------------------------------------------------------------------- main
def grade(root, out_path, skip_freeze=False, runscript_d6r=None,
          runscript_d4=None, d4_ref=None):
    global D4_OPT_IPOPT
    if d4_ref:
        D4_OPT_IPOPT = d4_ref
    frozen = {}
    if not skip_freeze:
        # DAFOAM_CHARTER.md section 18.3: EXISTENCE IS ASSERTED FIRST AND
        # SEPARATELY, and `freeze_check` does exactly that (`absent_on_disk`
        # refuses before any md5 is taken).  The list is EVERY file this
        # grading path EXECUTES OR IMPORTS, extracted from the code rather than
        # written from memory -- `d6rf3_cd_plant_control.py` is on it because
        # this file imports it, and it is the row a list written from memory
        # would have missed, which is SO2a-DRIVER-DEF-1's exact shape.
        frozen = freeze_check([
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/PREREGISTRATION.md",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_grade.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_cd_plant_control.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_endpoint_locus.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_endpoint_physical.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_extract_endpoint.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_fd_endpoint.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_ref_off.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_anchor_gate.py",
            "cases/dafoam/ladder-a/A2/curriculum_D6RF3/d6rf3_opt_runScript.py",
        ])
    rs6 = runscript_d6r or os.path.join(HERE, "d6rf3_opt_runScript.py")
    rs4 = runscript_d4 or os.path.join(
        HERE, os.pardir, "curriculum_D4", "d4_opt_runScript.py")
    rs6, rs4 = os.path.abspath(rs6), os.path.abspath(rs4)

    products = product_writer_check()
    ledger_rows, extra = parse_ledger(os.path.join(root, "ledger.txt"))
    chain = read_chain_status(os.path.join(root, "STATUS.chain"))
    census = arm_census(root, ledger_rows, chain)

    ctrl_dir = os.path.join(os.path.dirname(os.path.abspath(out_path)),
                            "grader_controls")
    fd_path = None
    if census[ARTEFACT_PRODUCER["d6rf3_fd_endpoint.json"]]["state"] == "RAN":
        fd_path = os.path.join(root, ARM_DIR["F_mp"], "d6rf3_fd_endpoint.json")
    controls = run_planted_controls(ctrl_dir, fd_path)
    reach = cap_reachability()

    g1 = gate_g1(root, ledger_rows, census)
    caps = gate_caps(ledger_rows, census)
    tool = gate_toolchain(root, ledger_rows, census)
    place = gate_placement(ledger_rows, census)
    dvl = gate_dvl(root, census, rs6, rs4)
    fd = gate_fd(root, census)
    off = gate_off(root, census)
    price = gate_price(root, census, controls)
    red = report_reduction(root, census)
    cdlog = report_cdlog(root, census)

    verdict, reasons = compose(g1, dvl, fd, off, price, caps, tool, place, census)
    spend = sum(g1["arms"][a].get("core_min", 0.0) for a in ARMS)
    doc = {
        "item": ITEM,
        "verdict": verdict,
        "verdict_reasons": reasons,
        "frozen": frozen,
        "product_writer_check": products,
        "cap_reachability": reach,
        "census": census,
        "chain_status": chain,
        "planted_controls": controls,
        "grade": {"G1": g1, "G-DVL": dvl, "G-FD": fd, "G-OFF": off,
                  "G-PRICE": price, "G-CAPS": caps, "G9": tool, "G12": place},
        "reported_not_gated": {"R-RED": red, "X-CDLOG": cdlog},
        # ---- DAFOAM_CHARTER.md section 6, ON THE ARTEFACT'S OWN FACE -------
        "two_row_rule": {
            "row_bought": ROW_BOUGHT,
            "row_not_bought": ROW_NOT_BOUGHT,
            "shipped_row_price_core_min": SHIPPED_ROW_PRICE_CORE_MIN,
            "shipped_row_price_basis": (
                "a second F_mp on stock IDWarp at the same cap; F_mp's own "
                "registered estimate, PREREGISTRATION.md section 4a"),
            "is_a_full_charter_section_6_verdict": False,
            "statement": (
                "THIS IS A ONE-ROW, PATCHED-ROW VERDICT AND IS LABELLED SO "
                "WHEREVER IT APPEARS. A one-row item is NOT a full "
                "DAFOAM_CHARTER.md section 6 verdict about DAFoam and must "
                "not be reported as one. The SHIPPED row is NOT BOUGHT and is "
                "PRICED anyway at %.2f core-min: an unbought row that is "
                "priced can be bought by a successor; an unbought row that is "
                "unpriced quietly becomes never."
                % SHIPPED_ROW_PRICE_CORE_MIN),
            "version_string_is_not_an_identity": (
                "all three images report DAFoam 5.0.0 / OpenFOAM v2506 / "
                "PETSc 3.15.5 while the IDWarp patch moves the reverse-mode "
                "derivative on the defect's own DOFs by seven orders of "
                "magnitude and the version string still reads 2.6.2")},
        "spend_core_min": spend,
        "cost_basis": ("c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT "
                       "MEASURED (COMPUTE_BUDGET_CHARTER.md section 5). "
                       "Dollars DERIVED, never measured."),
        "spend_usd_derived": round(spend / 60.0 * 0.0513, 6),
        "ceiling_core_min": sum(CAPS.values()),
        "ledger_extra_lines": extra,
    }
    with open(out_path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    print("D6RF3_VERDICT %s  spend %.3f core-min of a %.1f ceiling  -> %s"
          % (verdict, spend, sum(CAPS.values()), out_path))
    # G1 reports TWO SEPARATE FACTS and they are never the same verdict:
    # a chain stop makes `all_arms_ran` false and can leave `ran_clean` true.
    print("  %-26s ran_clean=%s all_arms_ran=%s"
          % (g1["gate"], g1["ran_clean"], g1["all_arms_ran"]))
    for g in (dvl, fd, off, price, caps, tool, place):
        print("  %-26s %s%s" % (g["gate"], g.get("verdict", "-"),
                                ("  reason=%s" % g["reason"])
                                if g.get("reason") == NON_FINITE_REASON else ""))
    print("  %-26s %s (REPORTED, NOT GATED)"
          % (red["row"], red.get("value_pct")))
    print("  %-26s per-point rel diff, NO THRESHOLD, NO VERDICT (REPORTED, "
          "NOT GATED)" % cdlog["row"])
    # Every rule-3 control's state is printed BESIDE the verdict, and
    # `NOT EXERCISED` is never omitted and never counted as a pass.
    print("  %-26s %s   NOT EXERCISED count = %d"
          % ("planted controls", json.dumps(controls.get("control_states", {}),
                                            sort_keys=True),
             controls.get("n_not_exercised", 0)))
    print("  %-26s row bought = %s; row NOT bought = %s, PRICED at %.2f "
          "core-min; NOT a full charter section 6 verdict"
          % ("two-row rule", ROW_BOUGHT, ROW_NOT_BOUGHT,
             SHIPPED_ROW_PRICE_CORE_MIN))
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--skip-freeze", action="store_true",
                    help="selftest fixtures only; NEVER on a real grading run")
    ap.add_argument("--runscript-d6r")
    ap.add_argument("--runscript-d4")
    ap.add_argument("--d4-ref")
    ap.add_argument("--cap-arithmetic", action="store_true",
                    help="print the cap/deadline reachability arithmetic and "
                         "exit; no run root needed, no compute")
    a = ap.parse_args()
    if a.cap_arithmetic:
        try:
            r = cap_reachability()
        except Refusal as e:
            sys.stderr.write("D6RF3_GRADE REFUSED %s\n" % e)
            return 2
        print("D6RF3 CAP / DEADLINE REACHABILITY -- ranks=%d frame_allowance_s=%d"
              % (r["ranks"], r["frame_allowance_s"]))
        for arm in ARMS:
            x = r["arms"][arm]
            print("  %-8s cap %7.2f core-min x 60 / %d ranks = %8.1f wall s"
                  % (arm, x["cap_core_min"], r["ranks"],
                     x["cap_wall_equivalent_s"]))
            print("  %-8s TMO %7d s + frame %d s          = %8.1f wall s   "
                  "residual %+.1e s" % ("", x["TMO_s"], r["frame_allowance_s"],
                                        x["TMO_plus_frame_s"],
                                        x["identity_residual_s"]))
            print("  %-8s max spend at TMO = %d x %d / 60 = %7.2f core-min  "
                  "(cap headroom %.2f)" % ("", x["TMO_s"], r["ranks"],
                                           x["max_spend_at_TMO_core_min"],
                                           x["cap_headroom_core_min"]))
            print("  %-8s predicted %7.2f core-min  <= cap %.2f : %s"
                  % ("", x["predicted_core_min"], x["cap_core_min"],
                     "OK" if not x["predicted_over_cap"] else "REFUSE"))
        print("  TOTAL predicted %.2f core-min against ceiling %.1f core-min"
              % (r["total_predicted_core_min"], r["ceiling_core_min"]))
        return 0
    if a.selftest:
        # The parent named `d6rf2_grade_selftest`, which DOES NOT EXIST on
        # disk -- `--selftest` was an ImportError in the frozen D6RF2 set.
        # This item's section 3f harness IS the selftest that matters and it
        # is a real file beside this one.
        import d6rf3_finiteness_mutation as st
        return st.drive()
    if not a.root or not a.out:
        sys.stderr.write("usage: d6rf3_grade.py --root <run root> --out <json>\n")
        return 64
    try:
        grade(a.root, a.out, a.skip_freeze, a.runscript_d6r, a.runscript_d4,
              a.d4_ref)
    except Refusal as e:
        sys.stderr.write("D6RF3_GRADE REFUSED %s\n" % e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
