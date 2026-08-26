#!/usr/bin/env python3
"""Curriculum D7 grader -- ONERA M6 lift-constrained transonic drag minimisation.

REFUSES (exit 2) rather than degrades.  CLAUDE.md rule 4.

THE TWO DEFECTS THIS GRADER IS BUILT AGAINST, both measured on this ladder:

 1. `A4/curriculum_D3/d3_grade.py` returned PASS at 0.0000 % with zero sign
    flips OVER AN EMPTY COMPONENT SET.  A present-but-unparseable FD block gave
    an empty list WITH THE KEY PRESENT; the refusal tested key presence and
    never non-emptiness; the plateau loop iterated zero times, so a step was
    "selected" without one comparison.  L-302: an instrument that cannot say
    "I measured nothing" will report a number it did not measure.
    -> G5 refuses BY COUNT, WITH THE COUNT PRINTED, before it grades anything,
       and every loop that could trip zero times asserts and prints its own
       trip count.
 2. D4-DEF-1: `d4_grade.py` DECLARED `--selftest` at argparse and never read
    it, so `--selftest` alongside a full invocation SILENTLY RAN A FULL GRADE
    and exited clean.  A reader could have recorded "grader selftest passed"
    when no selftest existed.
    -> HERE `--selftest` IS WIRED FROM THE FIRST COMMIT, has a DISTINCT EXIT
       PATH (exit 3, used by nothing else), writes NO --out file, and is
       DEMONSTRATED against deliberately broken fixtures.  It is not asserted
       to work; it is shown to FAIL when the thing it checks is broken.

PARSE-FROM-FILES DISCIPLINE.  Every graded number is read from a FILE.  MPI log
splicing on this ladder is MEASURED (A2/per_component_table/RESULTS.md sec.2.2,
commit 79679a84): four ranks interleave on one stdout and sever arrays
mid-number.  The arm log is read ONLY for short single-line markers -- the
container uid, the IDWarp .so md5, and G13's `PetscConvergedReason: N` -- whose
corruption makes them FAIL TO MATCH rather than silently mis-read.  There is no
stdout fallback for any graded quantity; a missing file is a REFUSAL.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# ============ REGISTERED CONSTANTS -- PREREGISTRATION.md, frozen ============
N_COMPONENTS_REGISTERED = 5                                    # sec.6
COMPONENTS_REGISTERED = [["shape", 115], ["twist", 1], ["patchV", 1],
                         ["shape", 0], ["shape", 119]]         # sec.6
CL_TOL_PER_MAJOR = 5.0e-4          # sec.4 band A
CL_TOL_FINAL = 1.0e-5              # sec.4 band B (IPOPT constr_viol_tol)
DRAG_BAND_PCT = (3.0, 25.0)        # sec.4 band C  [3 %, 25 %], prediction 10 %
FD_BAND_PCT_PER_COMPONENT = 5.0    # sec.4 band D
FD_BAND_PCT_AGGREGATE = 5.0        # sec.4 band D
PLATEAU_TOL_PCT = 10.0             # sec.4 band E
MAX_ITER_REGISTERED = 30           # sec.1 / sec.2a -- COST-DERIVED
NCELLS = 42120                     # sec.1
RANKS = 4                          # sec.1
DECOMP_METHOD = "scotch"           # sec.5
DELIVERED_CORES_FLOOR = 3.0        # sec.5
# ---------------------------------------------------------------------------
# D7R-GRADER-DEF-6, REPAIRED AT ITS CAUSE AND NOT AT THE RECORD.
#
# The D7R grading path was D7's grader carrying D7's constants -- CAPS["O"]
# = 600.0 and ITEM_CEILING = 928.0 -- against D7R's registered 900.0 and no
# item ceiling at all.  g10_caps therefore read `overrun_core_min: 332.533`
# against a threshold that was NEVER D7R's.
#
# THE REMEDY FOR A WRONG CONSTANT IS THE RIGHT CONSTANT.  Declaring the gate
# that holds it non-binding would repair the RECORD instead of the
# INSTRUMENT and would trade a five-minute fix for a permanent blind spot
# (dafoam-supervisor, ruling 3, 2026-08-26).
#
# AND THEY ARE NOT MERELY TYPED HERE.  `assert_caps_against_document()` below
# PARSES PREREGISTRATION.md sec.7 and REFUSES if any value here differs from
# the one the frozen document registers.  A constant copied by hand can
# drift from the registration; a constant checked against it cannot drift
# silently.
CAPS = {"P1": 8.0, "X": 15.0, "ACC": 60.0, "F-S": 750.0, "F-P": 750.0}   # sec.7
PREDICTED = {"P1": 0.75, "X": 2.0, "ACC": 25.0, "F-S": 485.0, "F-P": 485.0}
CEILINGS = {"P1": 32.0, "X": 60.0, "ACC": 240.0, "F-S": 3000.0, "F-P": 3000.0}
ITEM_CEILING_CORE_MIN = sum(CEILINGS.values())          # sec.7, DERIVED not typed
ITEM_PREDICTED_CORE_MIN = 997.75                        # sec.7
MD5_RUNSCRIPT = "e43902ed2cfc99022c6e21e075f88695"
MD5_FD = "92b3fa8d20a41da029590ed3bdde4203"
MD5_EXTRACT = "651d40c78cc52288a856934c108d1334"
PLANT = 1.234e-03                  # CLAUDE.md rule 3
RATE_USD_PER_CORE_H = 0.0513       # CLAUDE.md rule 12
COST_BASIS = ("c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED "
              "-- the box cannot read its own billing "
              "(COMPUTE_BUDGET_CHARTER.md sec.5). Every dollar figure this "
              "grader emits is DERIVED.")

VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED",
         "PENDING"}


class Refuse(Exception):
    pass


# ===================== THE CAPS ARE CHECKED, NOT COPIED =====================
# D4's sec.8 asserts its cap against the document rather than copying it, and
# ruling 3 (2026-08-26) requires the same here.  D7R-GRADER-DEF-6 existed
# BECAUSE a ported grader carried its predecessor's constants and nothing ever
# compared them to the document that was actually frozen.
CAP_ROW = re.compile(
    r"^\|\s*`(?P<arm>[A-Za-z0-9\-]+)`\s*\|[^|]*\|[^|]*\|"
    r"\s*\*\*(?P<pred>[0-9.]+)\*\*\s*\|"
    r"\s*(?P<cap>[0-9.]+)\s*\|"
    r"\s*(?P<ceil>[0-9.]+)\s*\|")


def parse_registered_caps(doc_path):
    """Read sec.7's arm table out of the FROZEN pre-registration."""
    if not os.path.isfile(doc_path):
        refuse("caps", {"pre_registration_absent": doc_path,
                        "note": "the caps in this file are checked against the "
                                "document, so an absent document is a refusal "
                                "and never a reason to trust the constants"})
    rows = {}
    for line in open(doc_path, errors="replace"):
        m = CAP_ROW.match(line.strip())
        if m:
            rows[m.group("arm")] = {"predicted": float(m.group("pred")),
                                    "cap": float(m.group("cap")),
                                    "ceiling": float(m.group("ceil"))}
    if not rows:
        refuse("caps", {"no_arm_rows_parsed": doc_path,
                        "note": "a document this parser cannot read is a "
                                "document it must not silently half-apply "
                                "(L-302)"})
    return rows


def assert_caps_against_document(doc_path):
    """REFUSE unless every constant in this file equals the frozen one."""
    reg = parse_registered_caps(doc_path)
    bad, checked = [], 0
    for arm in sorted(set(CAPS) | set(reg)):
        if arm not in reg:
            bad.append({"arm": arm, "in_grader_not_in_document": True})
            continue
        if arm not in CAPS:
            bad.append({"arm": arm, "in_document_not_in_grader": True})
            continue
        for key, here in (("cap", CAPS[arm]), ("ceiling", CEILINGS.get(arm)),
                          ("predicted", PREDICTED.get(arm))):
            checked += 1
            there = reg[arm][key]
            if here is None or abs(here - there) > 1e-9:
                bad.append({"arm": arm, "field": key, "in_grader": here,
                            "in_document": there})
    if checked == 0:
        refuse("caps", {"n_values_checked": 0,
                        "note": "an assertion that compared nothing is not an "
                                "assertion (L-302)"})
    if bad:
        refuse("caps", {"grader_constants_disagree_with_the_frozen_document": bad,
                        "document": doc_path,
                        "note": "this is D7R-GRADER-DEF-6 by name, and it is "
                                "refused here rather than reported later"})
    return {"document": os.path.abspath(doc_path), "n_values_checked": checked,
            "arms": sorted(CAPS), "registered": reg}


def refuse(where, detail):
    raise Refuse("%s: %s" % (where, json.dumps(detail, sort_keys=True,
                                               default=str)[:1500]))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read_json(path, where):
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    if os.path.getsize(path) == 0:
        refuse(where, {"empty_file": path})
    with open(path) as fh:
        try:
            return json.load(fh)
        except Exception as exc:                        # noqa: BLE001
            refuse(where, {"unparseable": path, "error": repr(exc)[:300]})


def require_rows(doc, where, row_label):
    """STRUCTURAL REFUSAL, BY NAME -- the D4-DEF-3 class.

    D4's grader indexed `d["rows"][:2]` on an FD artifact whose `rows` key was
    ABSENT and raised an UNCAUGHT KeyError: rc=1, a traceback, and NO VERDICT
    FILE AT ALL -- on the gate whose whole purpose was to prove that malformed
    input is refused BY NAME.  A gate that dies instead of refusing has not
    refused; it has crashed, and a crash writes no verdict.

    MEASURED in THIS grader before the freeze (D7-GRADER-DEF-2): with `rows`
    given as a JSON OBJECT rather than a list, `g6_plant`'s `orig.get("rows")
    or []` passed a truthy dict through, `enumerate` then yielded the dict's
    KEYS as strings, and `r.get(...)` raised an UNCAUGHT AttributeError.  With
    `rows` null, `g7_count_control` raised an UNCAUGHT TypeError.  Both are the
    D4-DEF-3 shape and both are refused here instead.

    Returns the validated non-empty list of dict rows, or REFUSES by name."""
    if not isinstance(doc, dict):
        refuse(where, {"row": row_label, "refusal_id": "DOC_NOT_OBJECT",
                       "type": type(doc).__name__})
    if "rows" not in doc:
        refuse(where, {"row": row_label, "refusal_id": "ROWS_KEY_ABSENT",
                       "keys_present": sorted(doc.keys())[:20]})
    rows = doc["rows"]
    if not isinstance(rows, list):
        refuse(where, {"row": row_label, "refusal_id": "ROWS_NOT_A_LIST",
                       "type": type(rows).__name__})
    if len(rows) == 0:
        refuse(where, {"row": row_label, "refusal_id": "ROWS_EMPTY",
                       "n_rows": 0,
                       "n_registered": N_COMPONENTS_REGISTERED})
    bad = [i for i, r in enumerate(rows) if not isinstance(r, dict)]
    if bad:
        refuse(where, {"row": row_label, "refusal_id": "ROW_NOT_AN_OBJECT",
                       "n_rows": len(rows), "bad_indices": bad[:20],
                       "bad_types": [type(rows[i]).__name__ for i in bad[:20]]})
    return rows


# ------------------------------------------------------------ IPOPT reader
IPOPT_ROW = re.compile(
    r"^\s*(\d+)r?\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s")


def read_ipopt(path, where="G3"):
    """Parse IPOPT's OWN output FILE.  IPOPT writes `opt_IPOPT.txt` itself, so
    the MPI stdout interleave cannot reach it."""
    if not os.path.isfile(path):
        refuse(where, {"absent": path,
                       "note": "IPOPT's own output file is the registered "
                               "source for G3/G4; there is no stdout fallback"})
    txt = open(path, errors="replace").read()
    rows = []
    for line in txt.splitlines():
        m = IPOPT_ROW.match(line)
        if m:
            try:
                rows.append({"iter": int(m.group(1)),
                             "objective": float(m.group(2)),
                             "inf_pr": float(m.group(3)),
                             "inf_du": float(m.group(4))})
            except ValueError:
                continue
    exits = [l.strip() for l in txt.splitlines() if l.strip().startswith("EXIT")]
    if not rows:
        refuse(where, {"no_iteration_rows_parsed": path, "bytes": len(txt),
                       "note": "an IPOPT file with zero parsed rows is a "
                               "REFUSAL, never an optimisation with no majors"})
    return {"rows": rows, "n_rows": len(rows), "exit_lines": exits,
            "exit": exits[-1] if exits else None, "bytes": len(txt)}


# ------------------------------------------------------------ ledger reader
def read_ledger(path, where="G1"):
    if not os.path.isfile(path):
        refuse(where, {"absent": path})
    arms = {}
    order = []
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        rec = {}
        for tok in re.finditer(r"(\w+)=(\[[^\]]*\]|\S+)", line.strip()):
            rec[tok.group(1)] = tok.group(2)
        # PARENTHESISED KEYS, CAPTURED EXPLICITLY.  `\w+` CANNOT match
        # `inspect(exit,oomkilled)`: it matches only the trailing `oomkilled`,
        # so `rec.get("inspect(exit,oomkilled)")` returned None and G11 --
        # THE OOM GATE -- passed unconditionally, on every run, forever.
        # A gate that cannot fail is not a gate.  MEASURED by this file's own
        # coverage unit G11_OOMKilled_true_fails, 2026-08-25, BEFORE the freeze.
        #
        # ATTRIBUTION, CORRECTED BEFORE IT WAS COMMITTED.  I first recorded that
        # `A2/curriculum_D4/d4_grade.py` shares this defect, having tested only
        # its GENERIC ledger regex.  IT DOES NOT: D4's G11 reads a SEPARATE,
        # dedicated structured parser (`d4_grade.py:551`) that captures the
        # parenthesised key correctly, and its g11 reads `r["oomkilled"]` from
        # that.  THE DEFECT IS THIS FILE'S ALONE, introduced by adapting D4's
        # ledger FORMAT with a simpler reader than D4's.  Recorded this way
        # because a false defect attribution against a peer's committed
        # instrument is worse than the defect it alleges.
        for key, pat in (("inspect(exit,oomkilled)",
                          r"inspect\(exit,oomkilled\)=(\[[^\]]*\])"),):
            m = re.search(pat, line)
            if m:
                rec[key] = m.group(1)
        a = rec.get("ARM")
        if a:
            arms[a] = rec
            order.append(a)
    if not arms:
        refuse(where, {"no_arm_rows": path,
                       "note": "a preflight abort writes NO ledger row; G1 "
                               "refuses on arm_absent_from_ledger rather than "
                               "grading an absence"})
    return {"arms": arms, "order": order}


def _f(rec, key, where, arm):
    v = rec.get(key)
    if v is None:
        refuse(where, {"arm": arm, "ledger_field_absent": key})
    try:
        return float(v)
    except ValueError:
        refuse(where, {"arm": arm, "ledger_field_unparseable": key, "value": v})


# ==================== ADDENDUM 2 (L-342) -- FIELD CLASSES ==================
# Sanaa's universal rule, d4d0c29d / L-342: "a bookkeeping failure invalidates
# the bookkeeping, never the physics artifacts -- and graders must separate
# physics-critical fields from infrastructure fields so a dead poller can never
# void a run again."  Approved as a pre-registered amendment by dafoam-supervisor
# (ruling [lab-attributed], 2026-08-26, conditions C1-C3).  NO band, threshold,
# cap or verdict rule moves.
#
# PHYSICS fields -- gates read these; absence REFUSES (unchanged behaviour).
PHYSICS_FIELDS = ("rc", "inspect(exit,oomkilled)")
# INFRASTRUCTURE fields -- absence -> NOT_MEASURED, DISCLOSED, grade proceeds.
INFRA_FIELDS = ("wall_s", "core_min", "cap_core_min", "enforced_core_min",
                "enforced_wall_s", "memavail_pre_GiB", "memavail_post_GiB",
                "memavail_min_during", "delivered_cores_mean",
                "siblings_pre", "siblings_post")
NOT_MEASURED = "NOT_MEASURED"


def _infra(rec, key, where, arm):
    """C1: ABSENT (key missing or None) -> NOT_MEASURED and proceed.
    PRESENT-BUT-UNPARSEABLE -> REFUSE naming the key and the value.  A present
    garbage value is not an absence; collapsing the two is the absent/passing
    collapse this family fights."""
    if key not in INFRA_FIELDS:
        refuse(where, {"arm": arm, "not_an_infrastructure_field": key,
                       "note": "_infra may only be asked about INFRA_FIELDS; "
                               "a physics field goes through _f and refuses"})
    v = rec.get(key)
    if v is None:
        return NOT_MEASURED
    try:
        return float(str(v).strip("[]").split()[0])
    except (ValueError, IndexError):
        refuse(where, {"arm": arm, "ledger_field_unparseable": key, "value": v,
                       "note": "PRESENT but unparseable is not ABSENT (C1)"})


def _docker_inspect_container(name):
    """The kernel's record, read live.  Returns None when docker cannot answer."""
    import subprocess
    try:
        r = subprocess.run(["sudo", "-n", "docker", "inspect", "--format",
                            "{{.State.ExitCode}} {{.State.OOMKilled}} "
                            "{{.State.StartedAt}} {{.State.FinishedAt}}", name],
                           capture_output=True, text=True, timeout=20)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    parts = r.stdout.split()
    if len(parts) < 4:
        return None
    return {"exit": parts[0], "oomkilled": parts[1],
            "started": parts[2], "finished": parts[3]}


def _iso_to_epoch(s):
    import datetime
    s = s.strip()
    if s.startswith("0001-"):
        return None
    s = re.sub(r"(\.\d{1,6})\d*Z$", r"\1Z", s)
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.datetime.strptime(s, fmt).replace(
                tzinfo=datetime.timezone.utc).timestamp()
        except ValueError:
            continue
    return None


def _rc_from_marker_or_container(base, arm, inspector=None, containers=None):
    """C2.  The ledger row is BOOKKEEPING.  The kernel's record survives it in
    two places, read in this order:
      (1) the launcher's own marker `<ARM>_<stamp>.log.ok.<stamp>` /
          `.fail.<stamp>`, whose rc IS `docker inspect .State.ExitCode`
          (d7fr_run_arm.sh:564, :632-636) -- carries rc and the log name;
      (2) the container `d7fr_<ARM_>_<stamp>` itself, if the launcher died
          before removing it at :593 -- carries rc, the OOM bit, StartedAt and
          FinishedAt, from which wall_s and core_min = wall_s x RANKS / 60.
    Every recovered field records its `_source`.  Returns None when NEITHER
    exists: only then is the arm absent.  `inspector`/`containers` are
    injection points for the selftest; production uses docker."""
    out = {"_source": {}}
    tag = arm.replace("-", "_")
    try:
        names = sorted(os.listdir(base))
    except OSError:
        names = []
    fails = [n for n in names if re.match(r"^%s_\S+\.log\.fail\." % re.escape(arm), n)]
    oks = [n for n in names if re.match(r"^%s_\S+\.log\.ok\." % re.escape(arm), n)]
    marker = (fails or oks or [None])[0]
    if marker:
        m = re.search(r"rc=(-?\d+)", open(os.path.join(base, marker),
                                         errors="replace").read())
        if m:
            out["rc"] = m.group(1)
            out["_source"]["rc"] = "marker:" + marker
            out["log"] = marker.split(".log.")[0] + ".log"
            out["_source"]["log"] = "marker:" + marker
    if containers is None:
        import subprocess
        try:
            r = subprocess.run(["sudo", "-n", "docker", "ps", "-a", "--format",
                                "{{.Names}}"], capture_output=True, text=True,
                               timeout=20)
            containers = r.stdout.split() if r.returncode == 0 else []
        except Exception:
            containers = []
    cands = [c for c in containers if c.startswith("d7fr_%s_" % tag)]
    if cands:
        insp = (inspector or _docker_inspect_container)(sorted(cands)[-1])
        if insp:
            out["container"] = sorted(cands)[-1]
            if "rc" not in out:
                out["rc"] = insp["exit"]
                out["_source"]["rc"] = "docker_inspect:" + out["container"]
            out["inspect(exit,oomkilled)"] = "[%s %s]" % (insp["exit"], insp["oomkilled"])
            out["_source"]["inspect(exit,oomkilled)"] = "docker_inspect:" + out["container"]
            t0, t1 = _iso_to_epoch(insp["started"]), _iso_to_epoch(insp["finished"])
            if t0 is not None and t1 is not None and t1 >= t0:
                out["wall_s"] = "%d" % int(round(t1 - t0))
                out["core_min"] = "%.3f" % (int(round(t1 - t0)) * RANKS / 60.0)
                out["_source"]["wall_s"] = "docker_inspect:StartedAt/FinishedAt"
                out["_source"]["core_min"] = "derived:wall_s x RANKS / 60"
    if "rc" not in out:
        return None
    return out


# ================================ GATES ====================================
# ==================== ARM KINDS, READ FROM THE LAUNCHER ====================
# D7F-DEF-1.  A Python arm that runs no solve emits no `End` line BY DESIGN, so
# demanding one asks a SOLVER question of a NON-SOLVER.  The predecessor did
# exactly that and would have returned NOT A RESULT for the whole item on the
# strength of a healthy `rc = 0` P1 -- after the FD arms had spent their
# registered core-minutes.
#
# THE RULE IS NOT "ACCEPT ABSENCE".  IT IS "ASK THE RIGHT QUESTION, AND REFUSE
# IF IT CANNOT BE ANSWERED" (dafoam-supervisor, ruling on D7F-DEF-1).  Every
# kind must present SOME evidence of completion; an arm whose kind cannot be
# determined is a REFUSAL, never a pass.
#
# AND THE KINDS ARE READ OUT OF THE LAUNCHER, NEVER TYPED HERE.  A table copied
# by hand drifts from the file that actually runs the arms -- which is the
# D7R-GRADER-DEF-6 shape one level up.
ARM_BRANCH = re.compile(r"^\s{2}([A-Za-z0-9|\-]+)\)\s+CMD=", re.M)


def parse_arm_kinds(launcher_path):
    """{arm: kind} from the launcher's own `case "$ARM" in` command branches.

    SOLVER     an mpirun branch running a DAFoam producer -> prints `End`
    DECOMPOSE  a decomposePar branch -> writes the decomposition maps
    PYTHON     a branch with no OpenFOAM solve -> writes its own artifact
    """
    if not os.path.isfile(launcher_path):
        refuse("G1", {"launcher_absent": launcher_path,
                      "note": "arm kinds are READ from the launcher; without it "
                              "this gate cannot know which question to ask of "
                              "which arm, and it refuses rather than guessing"})
    txt = open(launcher_path, errors="replace").read()
    out = {}
    for m in ARM_BRANCH.finditer(txt):
        names = m.group(1).split("|")
        start = m.end()
        end = txt.find('" ;;', start)
        body = txt[start:end if end > 0 else start + 2000]
        if "decomposePar" in body:
            kind = "DECOMPOSE"
        elif "mpirun" in body and re.search(
                r"python\s+d7f?r?_?\w*(opt_runScript|fd_endpoint|accept_primal)\.py",
                body):
            kind = "SOLVER"
        else:
            kind = "PYTHON"
        for n in names:
            out[n] = kind
    if not out:
        refuse("G1", {"no_arm_branches_parsed": launcher_path,
                      "note": "a launcher this parser cannot read is one it must "
                              "not silently half-apply (L-302)"})
    return out


# what each kind must PRESENT.  Every kind presents something; none is exempt.
KIND_EVIDENCE = {
    "SOLVER": "an `End` line in the arm's own log",
    "DECOMPOSE": "the decomposition maps the arm exists to write",
    "PYTHON": "its own named output artifact, newer than the age datum",
}
KIND_ARTIFACTS = {
    "DECOMPOSE": ["d7_decomp_A.json", "d7_decomp_B.json"],
    "PYTHON": ["d7_endpoint_dvs_PHYSICAL.json"],
}


# ==================== ADDENDUM 3 -- STAGED INPUTS ARE NOT OUTPUTS =============
# dafoam-supervisor ruling [lab-attributed] 2026-08-26, under d4d0c29d / L-342
# and VERIFICATION_CHARTER sec.2d.1 (all four conditions met non-vacuously, see
# PREREGISTRATION.md ADDENDUM 3).  The D7-port age guard tested a STAGED
# REFERENCE INPUT (D7R arm O's OptView.hst / opt_IPOPT.txt, copied with its
# mtime by the launcher's H4, d7fr_run_arm.sh:351-361) as if it were an output.
# The exemption list is READ FROM THE FROZEN STAGE'S OWN RECORD -- the
# `D7FR_H4_PASS arm=<arm> ... <file>=<md5>` line the launcher printed for THIS
# arm -- and each named file is VERIFIED BY md5 against that record.  Never a
# wildcard; a named file whose md5 moved REFUSES.  Every produced artefact is
# still age-checked.
H4_LINE = re.compile(r"^D7FR_H4_PASS\s+arm=(\S+)\s+(.*)$", re.M)


def _h4_staged_inputs(base, work):
    """-> ({filename: md5}, source_path) from this arm's own H4 record, or
    ({}, None) when the arm printed no H4 line (then nothing is exempt)."""
    arm = os.path.basename(os.path.normpath(work))
    for cand in ("%s_attempt.log" % arm, "%s_chain_launcher.out" % arm):
        p = os.path.join(base, cand)
        if not os.path.isfile(p):
            continue
        for m in H4_LINE.finditer(open(p, errors="replace").read()):
            if m.group(1) != arm:
                continue
            staged = {}
            for tok in m.group(2).split():
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    if "." in k and re.fullmatch(r"[0-9a-f]{32}", v):
                        staged[k] = v
            if staged:
                return staged, p
    return {}, None


def g1_completion(base, work, ledger, arms_expected, launcher=None,
                  inspector=None, containers=None):
    """rc == 0, the producer's own output FILE terminal, and THE AGE GUARD --
    every graded artifact strictly newer than the case's own 0/U, whose mtime
    the launcher wrote to `.d7_age_datum` at stage time.

    CLAUDE.md rule 4's THERMAL FIELD LIST IS THE T-FAMILY'S AND DOES NOT APPLY
    HERE; PREREGISTRATION.md sec.7 G1 says so, and this grader does not pretend
    to it.

    D7R-GRADER-DEF-7, REPAIRED HERE.  D7's `g1_completion` named THREE clauses
    in this docstring and implemented TWO: there was no terminal-statement read
    anywhere in it, and in that whole 74,338-byte file the string `End` occurred
    EXACTLY ONCE -- inside this docstring.  The clause existed in one place and
    that place was prose (L-335).  THE THIRD CLAUSE IS NOW EXECUTABLE, below,
    and `scripts/check_docstring_clauses.py` is run against THIS function as a
    condition of the freeze."""
    kinds = parse_arm_kinds(
        launcher or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "d7fr_run_arm.sh"))
    out = {"arms": {}, "age_guard": {}, "arm_kinds": kinds}
    ok = True
    for arm in arms_expected:
        if arm not in ledger["arms"]:
            # ADDENDUM 2 (L-342, C2): a missing ROW is bookkeeping.  Ask the
            # kernel's record before calling the arm absent.
            fb = _rc_from_marker_or_container(base, arm, inspector=inspector,
                                              containers=containers)
            if fb is None:
                out["arms"][arm] = {"status": "arm_absent_from_ledger"}
                ok = False
                continue
            rec = dict(fb)
            rec["_ledger_row"] = NOT_MEASURED
        else:
            rec = ledger["arms"][arm]
        rc = _f(rec, "rc", "G1", arm)
        out["arms"][arm] = {"rc": rc, "wall_s": _infra(rec, "wall_s", "G1", arm),
                            "core_min": _infra(rec, "core_min", "G1", arm),
                            "inspect": rec.get("inspect(exit,oomkilled)"),
                            "_source": rec.get("_source", {"rc": "ledger_row"}),
                            "ledger_row": rec.get("_ledger_row", "PRESENT")}
        if NOT_MEASURED in (out["arms"][arm]["wall_s"], out["arms"][arm]["core_min"]) \
                or rec.get("_ledger_row") == NOT_MEASURED:
            out.setdefault("not_measured", []).append(
                {"arm": arm, "fields": [k for k in ("wall_s", "core_min")
                                        if out["arms"][arm][k] == NOT_MEASURED],
                 "ledger_row": rec.get("_ledger_row", "PRESENT")})
        if rc != 0:
            ok = False
        # ---- THE TERMINAL CLAUSE, ARM-KIND AWARE, D7F-DEF-1's repair -------
        kind = kinds.get(arm)
        if kind is None:
            refuse("G1", {"arm": arm, "kind_not_determinable": True,
                          "kinds_parsed": kinds,
                          "note": "this arm has no command branch in the "
                                  "launcher, so there is no way to know which "
                                  "evidence of completion to demand.  REFUSED "
                                  "rather than passed"})
        logname = rec.get("log")
        lpath = os.path.join(base, logname) if logname else None
        # (a) THE COMPLETION MARKER, and it now MEANS completion.  `.ok` is
        #     written only on rc == 0, `.fail` only on rc != 0, NEITHER means
        #     the launcher itself died and the outcome is UNKNOWN.
        ok_m = [f for f in os.listdir(base) if logname and f.startswith(logname + ".ok.")]
        fail_m = [f for f in os.listdir(base) if logname and f.startswith(logname + ".fail.")]
        if fail_m:
            marker = {"state": "FAILED", "file": fail_m[0]}
        elif ok_m:
            marker = {"state": "OK", "file": ok_m[0]}
        else:
            marker = {"state": "UNKNOWN",
                      "note": "neither marker: the launcher died before "
                              "recording an outcome. NOT read as either"}
        # (b) THE KIND'S OWN EVIDENCE.  Every kind presents something.
        ev = {"kind": kind, "must_present": KIND_EVIDENCE[kind]}
        if kind == "SOLVER":
            if not lpath or not os.path.isfile(lpath):
                ev["present"] = False
                ev["why"] = "arm log absent"
            else:
                ltxt = open(lpath, errors="replace").read()
                ev["End_line"] = any(l.strip() == "End" for l in ltxt.splitlines())
                ev["present"] = ev["End_line"]
        else:
            need = KIND_ARTIFACTS[kind]
            adir = os.path.join(base, arm)
            found = {n: os.path.isfile(os.path.join(adir, n)) for n in need}
            ev["artifacts"] = found
            ev["present"] = all(found.values())
        out["arms"][arm]["log_terminal"] = {"log": logname, "marker": marker,
                                            "evidence": ev}
        if marker["state"] != "OK" or not ev["present"]:
            ok = False
    datum_path = os.path.join(work, ".d7_age_datum")
    if not os.path.isfile(datum_path):
        refuse("G1", {"age_datum_absent": datum_path,
                      "note": "without the datum there is no age guard, and a "
                              "stale artifact is indistinguishable from a "
                              "fresh one"})
    datum = int(open(datum_path).read().strip())
    n_checked = 0
    staged, h4_src = _h4_staged_inputs(base, work)
    out["age_guard"]["_h4_record"] = h4_src
    out["age_guard"]["_staged_inputs_exempt"] = []
    for name in ("opt_IPOPT.txt", "OptView.hst", "d7_major_history.json",
                 "d7_endpoint_dvs.json"):
        p = os.path.join(work, name)
        if not os.path.isfile(p):
            out["age_guard"][name] = "ABSENT"
            ok = False
            continue
        mt = int(os.stat(p).st_mtime)
        fresh = mt > datum
        if name in staged:
            # ADDENDUM 3: a STAGED INPUT must match the H4 record's md5; it is
            # then EXEMPT from the newer-than-datum test (an inherited input
            # must be OLD, launcher :348).  A mismatch is a REFUSAL.
            got = md5_of(p)
            if got != staged[name]:
                refuse("G1", {"arm_work": work, "staged_input_md5_mismatch": name,
                              "h4_record": staged[name], "on_disk": got,
                              "h4_source": h4_src})
            out["age_guard"][name] = {"mtime": mt, "datum": datum, "newer": fresh,
                                      "STAGED_INPUT_EXEMPT": True,
                                      "h4_md5": got, "h4_source": h4_src}
            out["age_guard"]["_staged_inputs_exempt"].append(name)
            continue
        out["age_guard"][name] = {"mtime": mt, "datum": datum, "newer": fresh}
        n_checked += 1
        if not fresh:
            ok = False
    # L-302: the loop asserts its own trip count.
    out["age_guard"]["_n_artifacts_checked"] = n_checked
    if n_checked == 0:
        refuse("G1", {"age_guard_checked_zero_artifacts": True,
                      "note": "an age guard that checked nothing is not a guard"})
    out["pass"] = ok
    return out


def g2_cl(history, cl_target):
    """Bands A and B -- CL feasibility at EVERY major and at the FINAL major."""
    cl = history.get("CL")
    if not isinstance(cl, list) or len(cl) == 0:
        refuse("G2", {"CL_absent_or_empty": True, "type": type(cl).__name__,
                      "len": (len(cl) if isinstance(cl, list) else None)})
    n = len(cl)
    devs = [abs(v - cl_target) for v in cl]
    worst = max(devs)
    worst_i = devs.index(worst)
    final = devs[-1]
    return {"n_majors": n, "cl_target": cl_target,
            "_n_majors_examined": n,
            "max_abs_dev": worst, "max_abs_dev_at_major": worst_i,
            "final_abs_dev": final,
            "band_A_tol": CL_TOL_PER_MAJOR, "band_B_tol": CL_TOL_FINAL,
            "band_A_pass": bool(worst <= CL_TOL_PER_MAJOR),
            "band_B_pass": bool(final <= CL_TOL_FINAL),
            "pass": bool(worst <= CL_TOL_PER_MAJOR and final <= CL_TOL_FINAL)}


CONVERGED_TOKEN = "EXIT: Optimal Solution Found."


def g3_exit(ip):
    """DAFOAM_CHARTER.md sec.9: A CAP-STOP IS `GATE REACHED` OR `NOT A RESULT`,
    NEVER `PASS`.  PREREGISTRATION.md sec.11 P1 registers, IN ADVANCE, that D7
    is EXPECTED to cap-stop -- so a cap-stop may NOT be presented as an
    expectation met, and a genuine convergence MUST be reported as a surprise."""
    ex = ip["exit"]
    converged = bool(ex and CONVERGED_TOKEN in ex)
    n_majors = max(r["iter"] for r in ip["rows"]) + 1
    capstop = bool(ex and ("Maximum Number of Iterations Exceeded" in ex
                           or "Maximum CPU time exceeded" in ex
                           or "Maximum Wall" in ex))
    return {"exit_line": ex, "exit_lines_all": ip["exit_lines"],
            "n_iteration_rows": ip["n_rows"], "highest_iter": n_majors - 1,
            "n_majors_inclusive": n_majors,
            "max_iter_registered": MAX_ITER_REGISTERED,
            "converged": converged, "cap_stop": capstop,
            "pass_eligible": converged,
            "registered_expectation": "P1: D7 is EXPECTED to cap-stop; ceiling "
                                      "verdict GATE REACHED; a PASS within 30 "
                                      "majors is registered UNLIKELY in advance"}


def g4_drag(ip, history):
    """Band C, read from IPOPT's own file AND cross-checked against the history
    written by pyOptSparse.  Two independent writers must agree, or the number
    is not read from one of them and hoped about the other."""
    cd0 = ip["rows"][0]["objective"]
    cdf = ip["rows"][-1]["objective"]
    if cd0 == 0.0:
        refuse("G4", {"baseline_objective_zero": True})
    red = 100.0 * (cd0 - cdf) / cd0
    hist_cd = history.get("CD")
    xcheck = None
    if isinstance(hist_cd, list) and len(hist_cd) >= 2:
        hred = 100.0 * (hist_cd[0] - hist_cd[-1]) / hist_cd[0]
        xcheck = {"hist_CD0": hist_cd[0], "hist_CDf": hist_cd[-1],
                  "hist_reduction_pct": hred,
                  "agrees_within_0p5pct_abs": bool(abs(hred - red) <= 0.5)}
        if not xcheck["agrees_within_0p5pct_abs"]:
            refuse("G4", {"ipopt_vs_history_disagree": True,
                          "ipopt_reduction_pct": red,
                          "history_reduction_pct": hred,
                          "note": "two independent writers of the same "
                                  "quantity disagree; neither is graded"})
    lo, hi = DRAG_BAND_PCT
    return {"CD_baseline": cd0, "CD_final": cdf, "reduction_pct": red,
            "band": list(DRAG_BAND_PCT), "cross_check": xcheck,
            "pass": bool(lo <= red <= hi),
            "note": "a result outside the band is reported as a MISS, never "
                    "re-banded (PREREGISTRATION.md sec.4)"}


def g5_fd(fd, row_label):
    """Bands D and E.  REFUSES BY COUNT, WITH THE COUNT PRINTED, on an empty,
    short, long or REORDERED component set -- the D3 defect, by name."""
    rows = fd.get("rows")
    if rows is None:
        refuse("G5", {"row": row_label, "key_absent": "rows",
                      "refusal_id": "KEY_ABSENT"})
    if not isinstance(rows, list):
        refuse("G5", {"row": row_label, "rows_not_a_list": type(rows).__name__})
    n = len(rows)
    if n == 0:
        refuse("G5", {"row": row_label, "n_rows": 0,
                      "n_registered": N_COMPONENTS_REGISTERED,
                      "defect": "EMPTY COMPONENT SET -- the D3 defect, by name",
                      "refusal_id": "COUNT_EMPTY"})
    if n != N_COMPONENTS_REGISTERED:
        refuse("G5", {"row": row_label, "n_rows": n,
                      "n_registered": N_COMPONENTS_REGISTERED,
                      "defect": "SHORT OR LONG component set",
                      "refusal_id": "COUNT_MISMATCH"})
    got_order = [[r.get("dv"), r.get("idx")] for r in rows]
    if got_order != COMPONENTS_REGISTERED:
        refuse("G5", {"row": row_label, "component_order_mismatch": True,
                      "got": got_order, "registered": COMPONENTS_REGISTERED,
                      "defect": "REORDERED component set",
                      "refusal_id": "ORDER_MISMATCH"})

    graded, excluded, per = [], [], []
    plateau_trips = 0
    for r in rows:
        name = "%s[%s]" % (r.get("dv"), r.get("idx"))
        st = r.get("status")
        if st != "PLANNED":
            excluded.append({"component": name, "status": st,
                             "reason": "sec.6a: clearance below %s at every "
                                       "ladder rung -> NOT A RESULT for this "
                                       "component" % CLEARANCE_NOTE})
            per.append({"component": name, "status": st, "verdict": "NOT A RESULT"})
            continue
        fdd = r.get("fd") or {}
        lo, hi = fdd.get("s_lo"), fdd.get("s_hi")
        if not lo or not hi or not lo.get("ok") or not hi.get("ok"):
            excluded.append({"component": name, "status": "FAILED_STEP",
                             "s_lo_ok": bool(lo and lo.get("ok")),
                             "s_hi_ok": bool(hi and hi.get("ok"))})
            per.append({"component": name, "status": "FAILED_STEP",
                        "verdict": "NOT A RESULT"})
            continue
        d_lo, d_hi = float(lo["d"]), float(hi["d"])
        j = float(r["J_adj"])
        plateau_trips += 1
        if d_hi == 0.0:
            plat = float("inf")
        else:
            plat = 100.0 * abs(d_hi - d_lo) / abs(d_hi)
        rel = (float("inf") if d_lo == 0.0
               else 100.0 * abs(j - d_lo) / abs(d_lo))
        flip = bool(j * d_lo < 0.0)
        v = {"component": name, "J_adj": j, "d_s_lo": d_lo, "d_s_hi": d_hi,
             "step_lo": lo["step"], "step_hi": hi["step"],
             "rel_err_pct": rel, "plateau_pct": plat, "sign_flip": flip,
             "band_D_pass": bool(rel <= FD_BAND_PCT_PER_COMPONENT and not flip),
             "band_E_pass": bool(plat <= PLATEAU_TOL_PCT)}
        v["verdict"] = "PASS" if (v["band_D_pass"] and v["band_E_pass"]) else "GATE FAIL"
        graded.append(v)
        per.append(v)

    # L-302: the plateau loop MUST assert its own trip count against the number
    # of graded rows.  D3's plateau loop iterated ZERO times and a step was
    # "selected" without one comparison.
    if plateau_trips != len(graded):
        refuse("G5", {"row": row_label, "plateau_trip_count": plateau_trips,
                      "n_graded": len(graded),
                      "defect": "plateau loop trip count != graded row count"})
    if graded:
        agg = max(v["rel_err_pct"] for v in graded)
        flips = sum(1 for v in graded if v["sign_flip"])
    else:
        agg, flips = None, 0
    return {"row": row_label,
            "n_rows_read": n, "n_registered": N_COMPONENTS_REGISTERED,
            "n_graded": len(graded), "n_excluded": len(excluded),
            "coverage": "%d of %d" % (len(graded), N_COMPONENTS_REGISTERED),
            "_plateau_trip_count": plateau_trips,
            "per_component": per, "excluded": excluded,
            "aggregate_worst_rel_err_pct": agg, "sign_flips": flips,
            "eta_raw": fd.get("eta_raw"), "eta_used": fd.get("eta_used"),
            "eta_floored": fd.get("eta_floored"),
            "pass": bool(graded and agg is not None
                         and agg <= FD_BAND_PCT_AGGREGATE and flips == 0
                         and all(v["band_E_pass"] for v in graded))}


CLEARANCE_NOTE = "5"


def g6_plant(path, row_label, reader=None):
    """CLAUDE.md rule 3 -- PLANTED ZERO.  A zero from a reader not shown able
    to see a non-zero is not evidence.  Plant a known perturbation INTO THE
    ARTIFACT ON DISK, read it back THROUGH THE SAME READER, and refuse if the
    reader cannot see it.

    `reader` IS INJECTABLE ON PURPOSE.  The selftest hands this function a
    DELIBERATELY BLIND reader -- one that ignores the path and returns the
    pristine document -- and REQUIRES the control to FAIL.  Without that unit
    both `seen` and `moved` could be hard-coded True and no test would notice:
    MEASURED as mutation m3 while testing this selftest, before the freeze."""
    reader = reader or read_json
    orig = reader(path, "G6")
    rows = require_rows(orig, "G6", row_label)
    target = None
    for i, r in enumerate(rows):
        if r.get("status") == "PLANNED" and (r.get("fd") or {}).get("s_lo", {}).get("ok"):
            target = i
            break
    if target is None:
        return {"row": row_label, "pass": False,
                "note": "NOT_MEASURED -- no graded row exists to plant into; "
                        "this is reported, never counted as a passing plant"}
    tmpdir = tempfile.mkdtemp(prefix="d7plant_")
    try:
        p = os.path.join(tmpdir, os.path.basename(path))
        shutil.copy2(path, p)
        doc = reader(p, "G6")
        before = float(doc["rows"][target]["fd"]["s_lo"]["d"])
        doc["rows"][target]["fd"]["s_lo"]["d"] = repr(before + PLANT)
        with open(p, "w") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True)
        back = reader(p, "G6")
        after = float(back["rows"][target]["fd"]["s_lo"]["d"])
        seen = abs((after - before) - PLANT) < 1e-12
        # And the GRADER must see it too: re-grade the planted artifact and
        # require the graded number to MOVE.  A reader that can see the plant
        # while the gate cannot is not a control on the gate.
        base_graded = g5_fd(orig, row_label)
        plant_graded = g5_fd(back, row_label)
        moved = (base_graded["per_component"][target].get("d_s_lo")
                 != plant_graded["per_component"][target].get("d_s_lo"))
        return {"row": row_label, "plant": PLANT, "target_row": target,
                "value_before": before, "value_after": after,
                "reader_saw_plant": bool(seen),
                "grader_output_moved": bool(moved),
                "pass": bool(seen and moved)}
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def g6b_blind(path, row_label):
    """NEGATIVE CONTROL.  A reader that IGNORES the path it is handed must be
    REFUSED.  A control that cannot refuse is not a control."""
    tmpdir = tempfile.mkdtemp(prefix="d7blind_")
    try:
        missing = os.path.join(tmpdir, "does_not_exist.json")
        try:
            read_json(missing, "G6b")
        except Refuse as exc:
            return {"row": row_label, "pass": True,
                    "refusal": str(exc)[:200],
                    "note": "the reader refused a path that does not exist; a "
                            "blind reader would have returned the real file"}
        return {"row": row_label, "pass": False,
                "note": "THE READER DID NOT REFUSE A NON-EXISTENT PATH -- it is "
                        "blind to the path it is handed and every zero it "
                        "reports is worthless"}
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def g7_count_control(path, row_label):
    """COUNT CONTROL.  Four deliberate mutations, each of which MUST produce a
    NAMED refusal.  This is the live demonstration that G5's count refusal can
    fire -- not the assertion that it can."""
    orig = read_json(path, "G7")
    # STRUCTURAL REFUSAL FIRST.  Every mutation below subscripts `rows`; on a
    # malformed artifact those subscripts are the D4-DEF-3 crash, not a gate.
    # MEASURED before the freeze: `rows` absent -> KeyError, `rows` null ->
    # TypeError, `rows` a dict -> KeyError(slice) -- all UNCAUGHT.
    baseline_rows = require_rows(orig, "G7", row_label)
    muts = {}

    def try_mut(name, doc):
        try:
            g5_fd(doc, row_label + "/" + name)
        except Refuse as exc:
            return {"refused": True, "named": str(exc)[:300]}
        return {"refused": False,
                "note": "MUTATION NOT REFUSED -- the gate cannot see it"}

    d = json.loads(json.dumps(orig)); d["rows"] = []
    muts["rows_emptied"] = try_mut("rows_emptied", d)
    d = json.loads(json.dumps(orig)); d["rows"] = d["rows"][:2]
    muts["rows_shortened_to_2"] = try_mut("rows_shortened_to_2", d)
    d = json.loads(json.dumps(orig)); d["rows"] = list(reversed(d["rows"]))
    muts["rows_reversed"] = try_mut("rows_reversed", d)
    d = json.loads(json.dumps(orig)); d.pop("rows", None)
    muts["key_removed"] = try_mut("key_removed", d)

    n = len(muts)
    n_refused = sum(1 for v in muts.values() if v["refused"])
    # THE D3 SHAPE, GUARDED.  With a baseline of 0 rows every mutation refuses
    # trivially and `n_refused == 4` would read on the page EXACTLY like a
    # complete control over a full component set.  `require_rows` above already
    # refuses an empty baseline, and this asserts the consequence explicitly so
    # the count is never the only thing standing between a plant and a PASS.
    n_baseline = len(baseline_rows)
    return {"row": row_label, "mutations": muts,
            "_n_mutations_attempted": n, "n_refused": n_refused,
            "n_baseline_rows": n_baseline,
            "n_registered": N_COMPONENTS_REGISTERED,
            "pass": bool(n == 4 and n_refused == 4
                         and n_baseline == N_COMPONENTS_REGISTERED)}


def g8_decomp(work):
    """Decomposition determinism.  OpenFOAM's scotchDecomp exposes NO SEED;
    determinism is NOT by construction and is NOT asserted -- it is
    DEMONSTRATED.  If the two maps differ, EVERY np=4 number in this item is
    NOT A RESULT (PREREGISTRATION.md sec.5)."""
    a = read_json(os.path.join(work, "d7_decomp_A.json"), "G8")
    b = read_json(os.path.join(work, "d7_decomp_B.json"), "G8")
    ka, kb = sorted(a), sorted(b)
    sa = sum(a[k] for k in ka)
    identical = (ka == kb and all(a[k] == b[k] for k in ka))
    return {"map_A": a, "map_B": b, "identical": bool(identical),
            "n_subdomains_A": len(ka), "n_subdomains_B": len(kb),
            "sum_cells_A": sa, "sum_cells_B": sum(b[k] for k in kb),
            "ncells_registered": NCELLS,
            "sum_matches_registered": bool(sa == NCELLS),
            "pass": bool(identical and len(ka) == RANKS and sa == NCELLS),
            "consequence": "GATE FAIL here makes every np=4 number in this "
                           "item NOT A RESULT (PREREGISTRATION.md sec.5)"}


SO_MD5 = re.compile(r"D7_IDWARP_SO_MD5:\s*([0-9a-f]{32})")
UID = re.compile(r"D7_CONTAINER_UID:\s*(\d+)")


def g9_toolchain(base, ledger, arm_rows):
    """DAFOAM_CHARTER.md sec.11: THE HASH IS THE IDENTITY; THE VERSION STRING IS
    NOT.  A3 rung 2 measured `idwarp` reading version 2.6.2 on the PATCHED
    stack -- the version string discriminates NOTHING.

    D7 is a TWO-ROW item, so the two endpoint rows MUST show TWO DISTINCT .so
    md5s.  IDENTICAL md5s ACROSS THE ROWS MEANS THE A/B NEVER HAPPENED and the
    item is NOT A RESULT (PREREGISTRATION.md sec.7 G9)."""
    out = {"arms": {}}
    for arm in arm_rows:
        rec = ledger["arms"].get(arm)
        if rec is None:
            out["arms"][arm] = {"status": "arm_absent_from_ledger"}
            continue
        logname = rec.get("log")
        p = os.path.join(base, logname) if logname else None
        so, uid = None, None
        if p and os.path.isfile(p):
            txt = open(p, errors="replace").read()
            m = SO_MD5.findall(txt)
            u = UID.findall(txt)
            so = sorted(set(m))
            uid = sorted(set(u))
        out["arms"][arm] = {"digest": rec.get("DIGEST"), "image": rec.get("IMG"),
                            "row": rec.get("ROW"), "so_md5": so, "uid": uid,
                            "log": logname}
    fs = out["arms"].get("F-S", {}).get("so_md5") or []
    fp = out["arms"].get("F-P", {}).get("so_md5") or []
    both = bool(fs and fp)
    distinct = bool(both and set(fs) != set(fp))
    out["two_rows_present"] = both
    out["two_rows_distinct_so_md5"] = distinct
    out["pass"] = distinct
    out["consequence"] = ("identical .so md5 across the two endpoint rows means "
                          "the A/B never happened -> NOT A RESULT")
    return out


def g10_caps(ledger, arms_expected):
    """G10 HAS TWO LIMBS AND THEY ARE NOT THE SAME KIND OF THING.
    dafoam-supervisor, ruling 3, 2026-08-26, registered IN ADVANCE.

    LIMB 1 -- `enforced cap == REGISTERED cap`, per arm, READ BACK OUT OF THE
             LEDGER THE LAUNCHER WROTE, never from the launcher's claim.  This
             is an INTEGRITY CHECK THAT THE LAUNCHER ENFORCED WHAT THE DOCUMENT
             REGISTERED -- precisely the D7R-DEF-8 / D12R class, a launcher and
             a document disagreeing, which bit this family three times in one
             night.  **THIS LIMB GATES.**  `pass` is limb 1 and limb 1 alone.

    LIMB 2 -- `actual <= cap`.  Under the reporting-cap design (sec.7) this limb
             IS the runaway guard, and a runaway guard that hard-fails a grade
             contradicts its own purpose.  **THIS LIMB IS REPORTED AND GATES
             NOTHING**, registered that way before compute with its reason
             frozen -- the D4 `ACC-2` and D12R2 step-proxy precedent.

    NON-GATING IS NOT NON-REPORTING, AND THAT IS THE HAZARD ATTACHED TO IT.
    "A printed discrepancy labelled 'diagnostic only' is worse than one never
    computed."  Every limb-2 crossing is therefore emitted with its NUMBER in
    core-minutes AND in derived dollars, under a key whose own name says it must
    be carried into the headline -- never a footnote, never a bare "within
    tolerance".  A quiet overrun is a defect."""
    out = {"arms": {}}
    ok = True
    overruns = []
    for arm in arms_expected:
        rec = ledger["arms"].get(arm)
        if rec is None:
            out["arms"][arm] = {"status": "arm_absent_from_ledger"}
            ok = False
            continue
        reg = CAPS.get(arm)
        if reg is None:
            refuse("G10", {"arm": arm, "no_registered_cap": True,
                           "registered_arms": sorted(CAPS),
                           "note": "an arm with no registered cap cannot be "
                                   "checked against one; LIMB 1 refuses rather "
                                   "than skipping the arm"})
        enf = _infra(rec, "enforced_core_min", "G10", arm)
        cap = _infra(rec, "cap_core_min", "G10", arm)
        act = _infra(rec, "core_min", "G10", arm)
        if NOT_MEASURED in (enf, cap, act):
            # ADDENDUM 2 (L-342, C3): a bookkeeping gate reading absent
            # bookkeeping is NOT_MEASURED -- DISCLOSED, NOT PASSED.  G10 is not
            # in map_verdict's hard list, so this cannot void the item; it is
            # named in the verdict line as a limitation.
            out["arms"][arm] = {"status": NOT_MEASURED, "registered_cap": reg,
                                "ledger_cap": cap, "enforced_core_min": enf,
                                "actual_core_min": act,
                                "LIMB1_cap_matches_registered": NOT_MEASURED,
                                "LIMB2_actual_within_cap": NOT_MEASURED,
                                "note": "ledger row incomplete; cap integrity "
                                        "unverifiable from bookkeeping"}
            out.setdefault("not_measured", []).append(arm)
            ok = False
            continue
        agree = abs(enf - reg) <= 0.02 and abs(cap - reg) <= 0.02
        within = act <= reg
        over = round(act - reg, 3) if not within else 0.0
        out["arms"][arm] = {"registered_cap": reg, "ledger_cap": cap,
                            "enforced_core_min": enf, "actual_core_min": act,
                            "LIMB1_cap_matches_registered": bool(agree),
                            "LIMB2_actual_within_cap": bool(within),
                            "overrun_core_min": over,
                            "overrun_usd_DERIVED": round(over / 60.0 * RATE_USD_PER_CORE_H, 4),
                            "predicted_core_min": PREDICTED.get(arm),
                            "ratio_actual_over_predicted": (
                                round(act / PREDICTED[arm], 4)
                                if PREDICTED.get(arm) else None)}
        if over > 0.0:
            overruns.append(
                {"arm": arm, "registered_cap": reg, "actual_core_min": act,
                 "overrun_core_min": over,
                 "overrun_pct_of_cap": round(100.0 * over / reg, 3),
                 "overrun_usd_DERIVED": round(over / 60.0 * RATE_USD_PER_CORE_H, 4),
                 "cost_basis": COST_BASIS})
        # LIMB 1 ONLY.  `within` is REPORTED and gates nothing (see docstring).
        if not agree:
            ok = False
    # Defensive: an `arm_absent_from_ledger` branch carries no
    # `actual_core_min`.  `.get` here is not laziness -- a KeyError would CRASH
    # the grader, and a crash produces no verdict at all, whereas an absent arm
    # must produce a REPORTED absence (check_grader_self_blindness ERROR 2).
    # ADDENDUM 2 (L-342): a NOT_MEASURED actual is EXCLUDED from the total and
    # the exclusion is named, never summed as zero.
    out["total_excludes_NOT_MEASURED_arms"] = [
        a for a in out["arms"] if out["arms"][a].get("actual_core_min") == NOT_MEASURED]
    total = sum(float(out["arms"][a].get("actual_core_min") or 0.0)
                if out["arms"][a].get("actual_core_min") != NOT_MEASURED else 0.0
                for a in out["arms"])
    out["total_actual_core_min"] = round(total, 3)
    out["item_predicted_core_min"] = ITEM_PREDICTED_CORE_MIN
    out["item_ratio_actual_over_predicted"] = round(total / ITEM_PREDICTED_CORE_MIN, 4)
    out["item_ceiling_core_min"] = ITEM_CEILING_CORE_MIN
    out["within_item_ceiling"] = bool(total <= ITEM_CEILING_CORE_MIN)
    out["total_usd_DERIVED"] = round(total / 60.0 * RATE_USD_PER_CORE_H, 4)
    out["cost_basis"] = COST_BASIS
    # --- LIMB 2, EMITTED LOUDLY OR NOT AT ALL --------------------------------
    # The key name is the instruction.  A reader who lifts G10 into a RESULTS
    # headline cannot lift it without seeing this, and a lane that omits it has
    # dropped a key whose name says it may not be dropped.
    out["LIMB2_REPORTED_NOT_GATING__CARRY_INTO_HEADLINE"] = {
        "n_overruns": len(overruns),
        "overruns": overruns,
        "rule": "actual <= cap is the runaway guard and GATES NOTHING (sec.7, "
                "ruling 3).  It is REPORTED with its number in core-minutes and "
                "in DERIVED dollars, in the RESULTS headline and in the cost "
                "row, never in a footnote and never as a bare 'within "
                "tolerance'.  A quiet overrun is a defect.",
        "gating_limb": "LIMB1_cap_matches_registered, and that limb alone"}
    out["pass"] = bool(ok)
    out["pass_is"] = "LIMB 1 ONLY -- enforced cap == registered cap"
    return out


def g11_oom(ledger, arms_expected, base=None, inspector=None, containers=None):
    """DAFOAM_CHARTER.md sec.7: OOM-killed -> NOT A RESULT ABOUT CONVERGENCE,
    recorded as stopped by memory.  Read from `docker inspect`, THE KERNEL'S
    OWN RECORD, not from the harness's impression."""
    out = {"arms": {}}
    any_oom = False
    n_absent = 0
    n_read = 0
    for arm in arms_expected:
        rec = ledger["arms"].get(arm)
        if rec is None:
            out["arms"][arm] = {"status": "arm_absent_from_ledger"}
            n_absent += 1
            continue
        insp = (rec.get("inspect(exit,oomkilled)") or "").strip("[]")
        src = "ledger_row"
        if not insp and base is not None:
            # ADDENDUM 2 (L-342): the OOM bit is PHYSICS (the kernel's record);
            # when the ROW lacks it, read it from the container itself if it
            # survives.  The marker carries no OOM bit, so only the container
            # can supply it.  G11 STAYS HARD.
            fb = _rc_from_marker_or_container(base, arm, inspector=inspector,
                                              containers=containers) or {}
            insp = (fb.get("inspect(exit,oomkilled)") or "").strip("[]")
            src = fb.get("_source", {}).get("inspect(exit,oomkilled)", src)
        if not insp:
            # The kernel bit was never recorded.  An unread bit is NOT a
            # clean bit.  D7-GRADER-DEF-1 was this gate reading `None` as
            # `False`; this is the same mistake one level up.
            out["arms"][arm] = {"inspect": "", "oom_killed": None,
                                "status": "OOM_BIT_NOT_RECORDED"}
            n_absent += 1
            continue
        oom = "true" in insp.lower()
        out["arms"][arm] = {"inspect": insp, "oom_killed": bool(oom), "_source": src}
        any_oom = any_oom or oom
        n_read += 1
    out["any_oom"] = bool(any_oom)
    out["n_arms_expected"] = len(arms_expected)
    out["n_arms_read"] = n_read
    out["n_arms_not_measured"] = n_absent
    # D7-GRADER-DEF-3, MEASURED before the freeze.  `pass = not any_oom` read
    # **PASS over an arm that never ran**: with every arm absent from the
    # ledger `any_oom` is False and the OOM gate reported a clean bill of
    # health for a container that was never created.  THAT IS THE D3 SHAPE --
    # a gate passing over an empty set reads on the page exactly like a gate
    # passing over a full one.  A gate that cannot fail over nothing is not a
    # gate.  NOT_MEASURED is not health.
    if n_absent:
        out["status"] = "NOT_MEASURED"
        out["pass"] = False
    else:
        out["status"] = "MEASURED"
        out["pass"] = not any_oom
    return out


def g12_placement(base, work_by_arm, ledger):
    """CPU PLACEMENT, MEASURED not inferred from the flag that was passed.
    `--cpus=4` does NOT hand out four distinct cores -- MEASURED, D13 lane,
    2026-08-25: 0.250 cores delivered against a 1.0-core quota with the host
    61 % idle.  REFUSES BY COUNT on fewer than four rank files.

    THE FINDING THIS GATE EXISTS TO PREVENT: a slow adjoint at np=4 reads
    EXACTLY like GMRES stagnation, which is a real failure mode measured on
    this ladder at N=52.  NO ADJOINT-CONDITIONING FINDING may be recorded by
    this item until G12 has ruled out core contention."""
    out = {"arms": {}}
    ok = True
    for arm, work in work_by_arm.items():
        files = sorted(f for f in os.listdir(work)
                       if re.match(r"^d7_placement_rank\d+\.json$", f)) \
            if os.path.isdir(work) else []
        if len(files) != RANKS:
            out["arms"][arm] = {"n_rank_files": len(files), "expected": RANKS,
                                "status": "REFUSED_BY_COUNT",
                                "refusal_id": "PLACEMENT_COUNT"}
            ok = False
            continue
        aff, singles = [], True
        for f in files:
            d = read_json(os.path.join(work, f), "G12")
            a = d.get("affinity") or []
            aff.append(sorted(a))
            if len(a) != 1:
                singles = False
        flat = [c for a in aff for c in a]
        distinct = len(set(tuple(a) for a in aff)) == RANKS
        rec = ledger["arms"].get(arm) or {}
        cpuset = rec.get("cpuset")
        inside = None
        if cpuset:
            try:
                pins = set(int(x) for x in cpuset.split(","))
                inside = set(flat).issubset(pins)
            except ValueError:
                inside = None
        dc = rec.get("delivered_cores_mean", "")
        m = re.match(r"^\[?([\d.]+)", dc or "")
        delivered = float(m.group(1)) if m else None
        out["arms"][arm] = {"n_rank_files": len(files), "affinity": aff,
                            "all_single_core": bool(singles),
                            "all_distinct": bool(distinct),
                            "cpuset": cpuset, "affinity_inside_cpuset": inside,
                            "delivered_cores_mean": (delivered if delivered
                                                     is not None
                                                     else "NOT_MEASURED"),
                            "delivered_floor": DELIVERED_CORES_FLOOR,
                            "delivered_pass": (bool(delivered >= DELIVERED_CORES_FLOOR)
                                               if delivered is not None else False)}
        if not (singles and distinct and inside and delivered is not None
                and delivered >= DELIVERED_CORES_FLOOR):
            ok = False
    out["pass"] = bool(ok)
    out["consequence"] = ("GATE FAIL -> every np=4 cost figure is "
                          "contention-contaminated and NO conditioning finding "
                          "may be drawn")
    return out


PETSC_REASON = re.compile(r"PetscConvergedReason:\s*(-?\d+)")


def g13_adjoint_health(base, ledger, arm="O"):
    """Band F -- EVERY major's adjoint must report PetscConvergedReason > 0.
    A `-9`-class reason is BLOCKED, RECORDED, NEVER SILENTLY SKIPPED.  A major
    whose adjoint did not converge cannot contribute a graded gradient, and an
    optimisation built on one is NOT A RESULT.

    `PetscConvergedReason: N` is a SHORT SINGLE LINE; MPI interleave makes it
    FAIL TO MATCH rather than silently mis-read, which is why the
    pre-registration registers the arm log as this gate's source."""
    rec = ledger["arms"].get(arm)
    if rec is None:
        return {"status": "arm_absent_from_ledger", "pass": False}
    logname = rec.get("log")
    p = os.path.join(base, logname) if logname else None
    if not p or not os.path.isfile(p):
        refuse("G13", {"arm_log_absent": p,
                       "note": "band F has no source; NOT_MEASURED is not a "
                               "passing adjoint-health gate"})
    txt = open(p, errors="replace").read()
    reasons = [int(x) for x in PETSC_REASON.findall(txt)]
    n = len(reasons)
    if n == 0:
        return {"n_reasons_found": 0, "pass": False,
                "status": "NOT_MEASURED",
                "note": "zero PetscConvergedReason lines in the arm log -- "
                        "this is REPORTED as not measured, never as health"}
    neg = [r for r in reasons if r <= 0]
    minus9 = [r for r in reasons if r == -9]
    return {"n_reasons_found": n, "_n_reasons_examined": n,
            "min_reason": min(reasons), "distinct": sorted(set(reasons)),
            "n_nonpositive": len(neg), "n_minus9": len(minus9),
            "blocked_class": bool(minus9),
            "pass": bool(not neg)}


def g13_in_item(base, ledger, arms_expected, fd_arms=("F-S", "F-P")):
    """ADDENDUM 3.  This item computes its adjoint gradient IN-ITEM: each FD arm's
    `compute_totals` runs one adjoint and prints one `PetscConvergedReason`.
    Band F is therefore read from THOSE arms' logs.  There is no arm `O` in this
    item; grading `O` here was a category error inherited from the D7 port.
    Pass = every present FD arm passes; no FD arm present -> NOT_MEASURED."""
    present = [a for a in fd_arms if a in arms_expected]
    out = {"source": "in-item: compute_totals adjoint in each FD arm's log",
           "fd_arms_graded": present, "arms": {}}
    if not present:
        out.update({"status": NOT_MEASURED, "pass": False,
                    "note": "no FD arm in the graded set; band F has no source"})
        return out
    ok = True
    for a in present:
        r = g13_adjoint_health(base, ledger, a)
        out["arms"][a] = r
        ok = ok and bool(r.get("pass"))
    out["pass"] = bool(ok)
    return out


# ============================== MAPPING ====================================
def map_verdict(g):
    """ADDENDUM 2 (L-342, C3): a NOT_MEASURED gate status NEVER composes to
    PASS silently.  Every NOT_MEASURED limb is listed BY NAME in the verdict
    line as a stated limitation.  The mapping itself is byte-unchanged in
    `_map_verdict_core`."""
    v = _map_verdict_core(g)
    nm = []
    if g.get("G1", {}).get("not_measured"):
        for e in g["G1"]["not_measured"]:
            nm.append("G1 arm %s: %s NOT_MEASURED%s" % (
                e["arm"], ",".join(e["fields"]) or "(no infra field)",
                " (ledger row absent; rc from the kernel's record)"
                if e.get("ledger_row") == NOT_MEASURED else ""))
    if g.get("G10", {}).get("not_measured"):
        nm.append("G10 limb 1 NOT_MEASURED for arms %s (disclosed, not passed)"
                  % ",".join(g["G10"]["not_measured"]))
    if g.get("G11", {}).get("status") == NOT_MEASURED:
        nm.append("G11 NOT_MEASURED (hard: the OOM bit was unreadable from row "
                  "and container)")
    for arm, d in (g.get("G12", {}).get("arms") or {}).items():
        if d.get("delivered_cores_mean") == NOT_MEASURED:
            nm.append("G12 arm %s: delivered_cores_mean NOT_MEASURED" % arm)
    for arm, d in (g.get("G13", {}).get("arms") or {}).items():
        if d.get("status") == NOT_MEASURED:
            nm.append("G13 arm %s: zero PetscConvergedReason lines (hard)" % arm)
    ex = (g.get("G1", {}).get("age_guard") or {}).get("_staged_inputs_exempt")
    if ex:
        nm.append("G1 age guard: staged inputs %s EXEMPT by H4 record (Addendum 3)"
                  % ",".join(ex))
    v["not_measured"] = nm
    if nm:
        v["because"] = list(v.get("because", [])) + [
            "LIMITATIONS (L-342, infrastructure NOT_MEASURED): " + "; ".join(nm)]
    return v


def _map_verdict_core(g):
    """PREREGISTRATION.md sec.7, and DAFOAM_CHARTER.md sec.9.

    THE ONE-WAY RULE (CLAUDE.md rule 5, by analogy, and sec.7 G3): a gate can
    only turn a PASS or GATE REACHED **into** NOT A RESULT, never the reverse.
    A CAP-STOP IS NEVER `PASS`."""
    hard = []
    if not g["G1"]["pass"]:
        hard.append("G1 completion/age guard")
    if not g["G8"]["pass"]:
        hard.append("G8 decomposition determinism")
    if not g["G11"]["pass"]:
        hard.append("G11 OOMKilled")
    if not g["G13"]["pass"]:
        hard.append("G13 adjoint health (band F)")
    if not g["G6"]["pass"]:
        hard.append("G6 planted zero")
    if not g["G6b"]["pass"]:
        hard.append("G6b blind-reader negative control")
    if not g["G7"]["pass"]:
        hard.append("G7 count control")
    if g["G9"]["two_rows_present"] and not g["G9"]["pass"]:
        hard.append("G9 two rows carry identical IDWarp .so md5")

    if hard:
        return {"verdict": "NOT A RESULT", "because": hard}

    g3, g4, g2 = g["G3"], g["G4"], g["G2"]
    if g3["converged"]:
        if g4["pass"] and g2["pass"]:
            return {"verdict": "PASS",
                    "because": ["IPOPT printed %r" % CONVERGED_TOKEN,
                                "band C and bands A/B hold"],
                    "SURPRISE": "PREREGISTRATION.md sec.11 P1 registered a PASS "
                                "within 30 majors on this shock-dominated "
                                "transonic problem as UNLIKELY IN ADVANCE. "
                                "This is a GENUINE SURPRISE and must be "
                                "reported as one, not as an expectation met."}
        return {"verdict": "GATE FAIL",
                "because": ["IPOPT converged but a frozen band did not hold",
                            "band C pass=%s" % g4["pass"],
                            "bands A/B pass=%s" % g2["pass"]]}
    # NOT converged -> cap-stop territory.  NEVER PASS.
    if g4["pass"] and g2["band_A_pass"]:
        return {"verdict": "GATE REACHED",
                "because": ["IPOPT did not print %r" % CONVERGED_TOKEN,
                            "exit=%r" % g3["exit_line"],
                            "band C holds (%.4f %% in %s)"
                            % (g4["reduction_pct"], g4["band"]),
                            "band A holds"],
                "charter": "DAFOAM_CHARTER.md sec.9 -- a cap-stop is GATE "
                           "REACHED or NOT A RESULT, NEVER PASS",
                "expectation": "PREREGISTRATION.md sec.11 P1 registered this "
                               "cap-stop IN ADVANCE. Nobody may present it as "
                               "an expectation met -- it was predicted, and "
                               "the prediction is scored, not celebrated."}
    return {"verdict": "NOT A RESULT",
            "because": ["cap-stop AND a frozen band did not hold",
                        "band C pass=%s" % g4["pass"],
                        "band A pass=%s" % g2["band_A_pass"]],
            "charter": "DAFOAM_CHARTER.md sec.9 / PREREGISTRATION.md sec.7 G3"}


# ============================== MAIN =======================================
def grade(base, work, out_path, arms, cl_target_path, fd_paths, doc_path,
          launcher=None):
    caps_ok = assert_caps_against_document(doc_path)
    ledger = read_ledger(os.path.join(base, "ledger.txt"))
    g = {}
    g["G1"] = g1_completion(base, work, ledger, arms, launcher)
    hist = read_json(os.path.join(work, "d7_major_history.json"), "G2")
    clt = read_json(cl_target_path, "G2")
    cl_target = float(clt["CL_target"])
    g["G2"] = g2_cl(hist, cl_target)
    ip = read_ipopt(os.path.join(work, "opt_IPOPT.txt"))
    g["G3"] = g3_exit(ip)
    g["G4"] = g4_drag(ip, hist)
    g5 = {}
    g6 = {"pass": True, "rows": {}}
    g6b = {"pass": True, "rows": {}}
    g7 = {"pass": True, "rows": {}}
    n_fd_rows_seen = 0
    for label, p in fd_paths.items():
        if not os.path.isfile(p):
            g5[label] = {"status": "ABSENT", "path": p, "pass": False,
                              "n_rows_read": 0, "n_graded": 0,
                              "n_excluded": 0,
                              "coverage": "0 of %d" % N_COMPONENTS_REGISTERED,
                              "_plateau_trip_count": 0,
                              "per_component": [], "excluded": [],
                              "aggregate_worst_rel_err_pct": None,
                              "sign_flips": 0}
            g6["rows"][label] = {"status": "ABSENT", "pass": False}
            g6["pass"] = False
            g6b["rows"][label] = {"status": "ABSENT", "pass": False}
            g6b["pass"] = False
            g7["rows"][label] = {"status": "ABSENT", "pass": False}
            g7["pass"] = False
            continue
        n_fd_rows_seen += 1
        fd = read_json(p, "G5")
        g5[label] = g5_fd(fd, label)
        r6 = g6_plant(p, label); g6["rows"][label] = r6
        g6["pass"] = g6["pass"] and r6["pass"]
        r6b = g6b_blind(p, label); g6b["rows"][label] = r6b
        g6b["pass"] = g6b["pass"] and r6b["pass"]
        r7 = g7_count_control(p, label); g7["rows"][label] = r7
        g7["pass"] = g7["pass"] and r7["pass"]
    g5["_n_toolchain_rows_read"] = n_fd_rows_seen
    if n_fd_rows_seen == 0:
        g6["pass"] = False
        g6b["pass"] = False
        g7["pass"] = False
        g6["note"] = ("NOT_MEASURED -- zero FD artifacts present; a plant "
                           "that was never made is not a passing plant")
    g["G5"], g["G6"], g["G6b"], g["G7"] = g5, g6, g6b, g7
    g["G8"] = g8_decomp(work if os.path.isfile(os.path.join(work, "d7_decomp_A.json"))
                        else os.path.join(base, "P1"))
    g["G9"] = g9_toolchain(base, ledger, ["F-S", "F-P"])
    g["G10"] = g10_caps(ledger, arms)
    g["G11"] = g11_oom(ledger, arms, base=base)
    g["G12"] = g12_placement(base, {a: os.path.join(base, a) for a in arms}, ledger)
    g["G13"] = g13_in_item(base, ledger, arms)          # ADDENDUM 3

    verdict = map_verdict(g)
    if verdict["verdict"] not in VOCAB:
        refuse("map_verdict", {"verdict_not_in_fixed_vocabulary":
                               verdict["verdict"], "vocabulary": sorted(VOCAB)})
    doc = {"item": "curriculum_D7FR", "base": base, "work": work,
           "caps_asserted_against_document": caps_ok,
           "cost_basis": COST_BASIS,
           "gates": g, "verdict": verdict,
           "registered_components": COMPONENTS_REGISTERED,
           "frozen_md5": {"producer": MD5_RUNSCRIPT, "fd": MD5_FD,
                          "extract": MD5_EXTRACT}}
    with open(out_path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True, default=str)
        fh.flush()
        os.fsync(fh.fileno())
    return doc


# ====================== SELFTEST -- WIRED, NOT ADVERTISED ==================
# D4-DEF-1, by name: `d4_grade.py` DECLARED `--selftest` and never read it.
# Here the flag has a DISTINCT EXIT PATH (3), writes NO --out, and DEMONSTRATES
# each unit by building a fixture that violates exactly ONE thing and requiring
# THIS FILE'S OWN function to refuse or to fail it.  Unit CLEAN is the
# DISCRIMINATION CONTROL: without it, a "failing" unit could not distinguish a
# working gate from a broken fixture.
def _st_fd_doc(mutate=None):
    rows = []
    for dv, idx in COMPONENTS_REGISTERED:
        j = 1.0e-1 if dv == "shape" else 1.0e-2
        rows.append({"dv": dv, "idx": idx, "status": "PLANNED",
                     "s_lo": 1.0e-2, "s_hi": 3.0e-2, "J_adj": repr(j),
                     "C_lo": 1000.0, "C_hi": 3000.0,
                     "fd": {"s_lo": {"step": 1.0e-2, "d": repr(j * 1.001),
                                     "ok": True},
                            "s_hi": {"step": 3.0e-2, "d": repr(j * 1.002),
                                     "ok": True}}})
    doc = {"rows": rows, "n_rows": len(rows), "eta_raw": repr(1e-9),
           "eta_used": repr(1e-9), "eta_floored": False}
    if mutate:
        mutate(doc)
    return doc


def selftest():
    units = []

    def unit(name, want, got, detail=""):
        ok = (want == got)
        units.append({"unit": name, "wanted": want, "got": got, "ok": ok,
                      "detail": detail})
        return ok

    # CLEAN -- the discrimination control.
    clean = _st_fd_doc()
    try:
        r = g5_fd(clean, "SELFTEST")
        unit("CLEAN_grades_all_pass", True,
             bool(r["pass"] and r["n_graded"] == N_COMPONENTS_REGISTERED),
             "n_graded=%d agg=%.6f" % (r["n_graded"],
                                       r["aggregate_worst_rel_err_pct"]))
    except Refuse as exc:
        unit("CLEAN_grades_all_pass", True, False, str(exc)[:200])

    # Count mutations -- each MUST refuse, AND MUST REFUSE FOR THE REGISTERED
    # REASON.  Asserting only "it refused" is NOT enough and this is measured,
    # not supposed: mutation m1 (below, in the record) DELETED the count
    # refusal outright and the SHORT and LONG fixtures were still refused --
    # by the ORDER check -- so an earlier version of this selftest scored 18/18
    # against a grader carrying the D3 defect. The refusal_id is now asserted.
    for name, mut, want_id in (
        ("EMPTY_refused_as_COUNT_EMPTY",
         lambda d: d.update(rows=[]), "COUNT_EMPTY"),
        ("SHORT_refused_as_COUNT_MISMATCH",
         lambda d: d.update(rows=d["rows"][:2]), "COUNT_MISMATCH"),
        ("LONG_refused_as_COUNT_MISMATCH",
         lambda d: d.update(rows=d["rows"] + [d["rows"][0]]), "COUNT_MISMATCH"),
        ("REORDERED_refused_as_ORDER_MISMATCH",
         lambda d: d.update(rows=list(reversed(d["rows"]))), "ORDER_MISMATCH"),
        ("KEY_REMOVED_refused_as_KEY_ABSENT",
         lambda d: d.pop("rows", None), "KEY_ABSENT"),
    ):
        try:
            g5_fd(_st_fd_doc(mut), "SELFTEST")
            unit(name, True, False, "GATE DID NOT REFUSE AT ALL")
        except Refuse as exc:
            got_id = want_id in str(exc)
            unit(name, True, bool(got_id),
                 ("refusal_id=%s" % want_id) if got_id
                 else "REFUSED FOR THE WRONG REASON: %s" % str(exc)[:140])

    # Band D must FAIL on a component far from FD, and on a SIGN FLIP.
    def far(d):
        d["rows"][0]["J_adj"] = repr(-5.0)
    r = g5_fd(_st_fd_doc(far), "SELFTEST")
    unit("SIGN_FLIP_fails_band_D", True,
         bool(not r["pass"] and r["sign_flips"] >= 1),
         "flips=%d" % r["sign_flips"])

    def offband(d):
        d["rows"][0]["J_adj"] = repr(1.0e-1 * 1.5)   # 50 % off
    r = g5_fd(_st_fd_doc(offband), "SELFTEST")
    unit("OFF_BAND_fails_band_D", True, bool(not r["pass"]),
         "agg=%.4f%%" % r["aggregate_worst_rel_err_pct"])

    # Band E must FAIL when the two steps disagree by more than the tolerance.
    def noplateau(d):
        d["rows"][0]["fd"]["s_hi"]["d"] = repr(1.0e-1 * 3.0)
    r = g5_fd(_st_fd_doc(noplateau), "SELFTEST")
    unit("NO_PLATEAU_fails_band_E", True,
         bool(not r["pass"] and not r["per_component"][0]["band_E_pass"]),
         "plateau=%.2f%%" % r["per_component"][0]["plateau_pct"])

    # G6b: the blind-reader control must PASS on a real reader.
    tmp = tempfile.mkdtemp(prefix="d7st_")
    try:
        p = os.path.join(tmp, "d7_fd_endpoint.json")
        with open(p, "w") as fh:
            json.dump(_st_fd_doc(), fh)
        unit("G6b_blind_control_passes", True, bool(g6b_blind(p, "SELFTEST")["pass"]))
        r6 = g6_plant(p, "SELFTEST")
        unit("G6_plant_visible_to_reader_and_grader", True, bool(r6["pass"]),
             "seen=%s moved=%s" % (r6.get("reader_saw_plant"),
                                   r6.get("grader_output_moved")))
        r7 = g7_count_control(p, "SELFTEST")
        unit("G7_four_named_refusals", True, bool(r7["pass"]),
             "n_refused=%d of %d" % (r7["n_refused"],
                                     r7["_n_mutations_attempted"]))

        # ---- D7-GRADER-DEF-2: THE D4-DEF-3 CLASS, UNIT-COVERED ------------
        # D4's grader raised an UNCAUGHT KeyError on an FD artifact whose
        # `rows` key was absent -- rc=1, a traceback, NO VERDICT FILE -- on
        # the gate whose purpose was to refuse malformed input BY NAME.  This
        # grader carried FOUR instances of the same shape and they were found
        # BY MEASUREMENT before the freeze, not by reading:
        #     rows absent -> KeyError (G7);  rows null -> TypeError (G7);
        #     rows a dict -> AttributeError (G6) AND KeyError(slice) (G7).
        # A CRASH IS NOT A REFUSAL.  A gate that dies writes no verdict, so
        # the malformed input it was built to catch goes UNRECORDED.  Every
        # malformed shape must now produce a NAMED Refuse from BOTH gates,
        # and the unit asserts THE NAME, never merely that something raised.
        for _shape, _doc, _want in (
                ("rows_key_absent", {"meta": {}}, "ROWS_KEY_ABSENT"),
                ("rows_null",       {"rows": None}, "ROWS_NOT_A_LIST"),
                ("rows_is_dict",    {"rows": {"a": 1}}, "ROWS_NOT_A_LIST"),
                ("rows_is_string",  {"rows": "abc"}, "ROWS_NOT_A_LIST"),
                ("rows_empty",      {"rows": []}, "ROWS_EMPTY"),
                ("row_not_object",  {"rows": [1, 2, 3]}, "ROW_NOT_AN_OBJECT"),
                ("doc_not_object",  [1, 2],       "DOC_NOT_OBJECT")):
            _bp = os.path.join(tmp, "malformed_%s.json" % _shape)
            with open(_bp, "w") as fh:
                json.dump(_doc, fh)
            for _gname, _gfn in (("G6", g6_plant), ("G7", g7_count_control)):
                try:
                    _gfn(_bp, "SELFTEST")
                    unit("DEF2_%s_%s_refused_by_name" % (_shape, _gname),
                         True, False, "DID NOT REFUSE -- gate is blind")
                except Refuse as _exc:
                    _got = _want in str(_exc)
                    unit("DEF2_%s_%s_refused_by_name" % (_shape, _gname),
                         True, bool(_got),
                         "refusal_id=%s" % (_want if _got else "WRONG:%s"
                                            % str(_exc)[:60]))
                except Exception as _exc:                      # noqa: BLE001
                    # THIS is the D4-DEF-3 failure mode and it must never pass.
                    unit("DEF2_%s_%s_refused_by_name" % (_shape, _gname),
                         True, False,
                         "CRASHED %s -- rc=1, no verdict file"
                         % type(_exc).__name__)

        # And the D3 shape in G7's own arithmetic: a baseline of the WRONG
        # LENGTH must not read as a complete control.  With 2 baseline rows
        # all four mutations still refuse and `n_refused == 4` -- which on the
        # page is indistinguishable from a complete control over all 5
        # registered components.  The baseline count is what separates them.
        _short = _st_fd_doc()
        _short["rows"] = _short["rows"][:2]
        _sp = os.path.join(tmp, "short_baseline.json")
        with open(_sp, "w") as fh:
            json.dump(_short, fh)
        _r7s = g7_count_control(_sp, "SELFTEST")
        unit("G7_SHORT_baseline_cannot_read_as_a_complete_control", True,
             bool(_r7s["n_refused"] == 4 and not _r7s["pass"]),
             "n_refused=%d baseline=%d registered=%d pass=%s"
             % (_r7s["n_refused"], _r7s["n_baseline_rows"],
                _r7s["n_registered"], _r7s["pass"]))

        # THE CONTROL ON THE CONTROL.  Hand g6_plant a DELIBERATELY BLIND
        # reader -- one that ignores the path it is given and returns the
        # pristine document every time -- and REQUIRE the planted-zero control
        # to FAIL.  CLAUDE.md rule 3 is that a zero from a reader not shown
        # able to see a non-zero is not evidence; this unit is what SHOWS it.
        # Without this unit, `seen` and `moved` could both be hard-coded True
        # and every other unit here would still score ok (measured: mutation
        # m3, before the freeze).
        pristine = json.loads(json.dumps(_st_fd_doc()))

        def blind_reader(_path, _where):
            return json.loads(json.dumps(pristine))

        rb = g6_plant(p, "SELFTEST", reader=blind_reader)
        unit("G6_BLIND_READER_makes_the_plant_FAIL", True,
             bool(not rb["pass"]),
             "seen=%s moved=%s" % (rb.get("reader_saw_plant"),
                                   rb.get("grader_output_moved")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # G3/mapping: A CAP-STOP MUST NEVER MAP TO PASS.  This is the charter
    # clause the whole item turns on, so it is DEMONSTRATED, not trusted.
    ok_g = {"G1": {"pass": True}, "G8": {"pass": True}, "G11": {"pass": True},
            "G13": {"pass": True}, "G6": {"pass": True}, "G6b": {"pass": True},
            "G7": {"pass": True},
            "G9": {"pass": True, "two_rows_present": True},
            "G3": {"converged": False, "exit_line": "EXIT: Maximum Number of "
                                                    "Iterations Exceeded."},
            "G4": {"pass": True, "reduction_pct": 10.0, "band": [3.0, 25.0]},
            "G2": {"pass": True, "band_A_pass": True}}
    v = map_verdict(ok_g)
    unit("CAPSTOP_never_PASS", True,
         bool(v["verdict"] == "GATE REACHED"), "got=%s" % v["verdict"])

    ok_g2 = json.loads(json.dumps(ok_g))
    ok_g2["G3"] = {"converged": True, "exit_line": CONVERGED_TOKEN}
    v = map_verdict(ok_g2)
    unit("CONVERGED_is_PASS_and_flagged_a_SURPRISE", True,
         bool(v["verdict"] == "PASS" and "SURPRISE" in v),
         "got=%s" % v["verdict"])

    ok_g3 = json.loads(json.dumps(ok_g))
    ok_g3["G13"] = {"pass": False}
    v = map_verdict(ok_g3)
    unit("ADJOINT_UNHEALTHY_is_NOT_A_RESULT", True,
         bool(v["verdict"] == "NOT A RESULT"), "got=%s" % v["verdict"])

    ok_g4 = json.loads(json.dumps(ok_g))
    ok_g4["G8"] = {"pass": False}
    v = map_verdict(ok_g4)
    unit("DECOMP_NONDETERMINISTIC_is_NOT_A_RESULT", True,
         bool(v["verdict"] == "NOT A RESULT"), "got=%s" % v["verdict"])

    # G8 must refuse a partition that does not sum to the registered cell count.
    tmp = tempfile.mkdtemp(prefix="d7st8_")
    try:
        for nm, vals in (("d7_decomp_A.json", {"processor0": 10530,
                                               "processor1": 10530,
                                               "processor2": 10530,
                                               "processor3": 10530}),
                         ("d7_decomp_B.json", {"processor0": 10530,
                                               "processor1": 10530,
                                               "processor2": 10530,
                                               "processor3": 10530})):
            with open(os.path.join(tmp, nm), "w") as fh:
                json.dump(vals, fh)
        unit("G8_clean_partition_passes", True, bool(g8_decomp(tmp)["pass"]))
        with open(os.path.join(tmp, "d7_decomp_B.json"), "w") as fh:
            json.dump({"processor0": 10531, "processor1": 10530,
                       "processor2": 10530, "processor3": 10529}, fh)
        unit("G8_differing_maps_fail", True, bool(not g8_decomp(tmp)["pass"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ================= GATE-COVERAGE UNITS =================================
    # THE SUPERVISOR'S RULING, 2026-08-25: counting a selftest's units measures
    # its SIZE, not its COVERAGE.  An earlier version of this selftest scored
    # 19/19 while exercising only G5, G6, G6b, G7, G8 and map_verdict -- NINE of
    # the fourteen gates this grader can emit had NO unit at all.  The units
    # below close that, one per unexercised gate, each built as a fixture that
    # VIOLATES exactly one thing.  The emitted-vs-exercised comparison is
    # printed by the banner at the end so the gap cannot silently reopen.
    tmp = tempfile.mkdtemp(prefix="d7cov_")
    try:
        # ---- G1: the AGE GUARD must fail a STALE artifact ------------------
        w = os.path.join(tmp, "work"); os.makedirs(w)
        led_p = os.path.join(tmp, "ledger.txt")
        with open(led_p, "w") as fh:
            fh.write("ARM=O ROW=SHIPPED IMG=i DIGEST=d rc=0 wall_s=100 ranks=4 "
                     "core_min=6.667 cap_core_min=600.0 enforced_wall_s=9000 "
                     "enforced_core_min=600.000000 memory=12g "
                     "inspect(exit,oomkilled)=[0 false] cpuset=2,3,4,6 "
                     "delivered_cores_mean=[3.9000 n=10 max_nr_throttled=0] "
                     "log=O.log\n")
        # A LAUNCHER FIXTURE, so the kinds are PARSED exactly as in production.
        lch = os.path.join(tmp, "lch.sh")
        open(lch, "w").write(
            'case "$ARM" in\n'
            '  P1) CMD="rm -rf processor* && decomposePar -force > a.log" ;;\n'
            '  X)   CMD="python d7fr_endpoint_physical.py --age-datum $A" ;;\n'
            '  O|F-S) CMD="mpirun -np 4 python d7_fd_endpoint.py" ;;\n'
            'esac\n')
        kk = parse_arm_kinds(lch)
        unit("KIND_decomposePar_arm_is_DECOMPOSE", "DECOMPOSE", kk.get("P1"))
        unit("KIND_python_only_arm_is_PYTHON", "PYTHON", kk.get("X"))
        unit("KIND_mpirun_solver_arm_is_SOLVER", "SOLVER", kk.get("O"))
        unit("KIND_alternation_branch_covers_both_arms", "SOLVER", kk.get("F-S"))
        try:
            parse_arm_kinds(os.path.join(tmp, "no_such_launcher.sh"))
            unit("KIND_absent_launcher_REFUSES", "REFUSED", "no-refusal")
        except Refuse:
            unit("KIND_absent_launcher_REFUSES", "REFUSED", "REFUSED")
        open(os.path.join(tmp, "empty.sh"), "w").write("# nothing\n")
        try:
            parse_arm_kinds(os.path.join(tmp, "empty.sh"))
            unit("KIND_unparseable_launcher_REFUSES", "REFUSED", "no-refusal")
        except Refuse:
            unit("KIND_unparseable_launcher_REFUSES", "REFUSED", "REFUSED")

        # THE SOLVER ARM's own log, and a marker that MEANS rc = 0.
        with open(os.path.join(tmp, "O.log"), "w") as fh:
            fh.write("Time = 1\nExecutionTime = 1 s\nEnd\n")
        open(os.path.join(tmp, "O.log.ok.STAMP1"), "w").write("rc=0 stamp=STAMP1 arm=O\n")
        led = read_ledger(led_p)
        unit("G1_ledger_reader_parses_an_arm_row", True,
             bool("O" in led["arms"] and led["arms"]["O"]["rc"] == "0"))
        import time as _t
        now = int(_t.time())
        with open(os.path.join(w, ".d7_age_datum"), "w") as fh:
            fh.write(str(now))
        for nm in ("opt_IPOPT.txt", "OptView.hst", "d7_major_history.json",
                   "d7_endpoint_dvs.json"):
            fp = os.path.join(w, nm)
            open(fp, "w").write("x")
            os.utime(fp, (now - 500, now - 500))     # STALE on purpose
        r = g1_completion(tmp, w, led, ["O"], lch)
        unit("G1_STALE_artifact_fails_age_guard", True, bool(not r["pass"]),
             "n_checked=%d" % r["age_guard"]["_n_artifacts_checked"])
        for nm in ("opt_IPOPT.txt", "OptView.hst", "d7_major_history.json",
                   "d7_endpoint_dvs.json"):
            os.utime(os.path.join(w, nm), (now + 500, now + 500))
        unit("G1_FRESH_artifacts_pass_age_guard", True,
             bool(g1_completion(tmp, w, led, ["O"], lch)["pass"]))
        unit("G1_MISSING_arm_is_absent_from_ledger_not_a_pass", True,
             bool(not g1_completion(tmp, w, led, ["O", "F-S"], lch)["pass"]))

        # ================= D7F-DEF-1, DRIVEN IN BOTH DIRECTIONS =============
        # (1) A HEALTHY PYTHON ARM MUST PASS.  This is the exact condition that
        #     broke the predecessor: a healthy rc=0 arm that emits no `End`.
        pled = os.path.join(tmp, "ledP.txt")
        open(pled, "w").write(
            "ARM=X ROW=SHIPPED IMG=i DIGEST=d rc=0 wall_s=9 ranks=4 "
            "core_min=0.6 cap_core_min=15.0 enforced_core_min=15.000000 "
            "inspect(exit,oomkilled)=[0 false] log=X.log\n")
        open(os.path.join(tmp, "X.log"), "w").write(
            "no End line anywhere -- this arm runs no solver\n")
        open(os.path.join(tmp, "X.log.ok.S2"), "w").write("rc=0 stamp=S2 arm=X\n")
        xdir = os.path.join(tmp, "X"); os.makedirs(xdir, exist_ok=True)
        open(os.path.join(xdir, ".d7_age_datum"), "w").write(str(now))
        for nm in ("opt_IPOPT.txt", "OptView.hst", "d7_major_history.json",
                   "d7_endpoint_dvs.json"):
            fp = os.path.join(xdir, nm); open(fp, "w").write("x")
            os.utime(fp, (now + 500, now + 500))
        open(os.path.join(xdir, "d7_endpoint_dvs_PHYSICAL.json"), "w").write("{}")
        unit("DEF1_python_arm_log_really_has_NO_End_line", False,
             any(l.strip() == "End" for l in
                 open(os.path.join(tmp, "X.log")).read().splitlines()),
             "the mutation is the REAL condition, not a stand-in")
        rP = g1_completion(tmp, xdir, read_ledger(pled), ["X"], lch)
        unit("DEF1_HEALTHY_PYTHON_ARM_PASSES_WITHOUT_AN_End_LINE", True,
             bool(rP["pass"]),
             "kind=%s -- the predecessor FAILED here" % rP["arm_kinds"].get("X"))
        # ...and it is NOT passing by exemption: remove its own artifact.
        os.remove(os.path.join(xdir, "d7_endpoint_dvs_PHYSICAL.json")) \
            if os.path.exists(os.path.join(xdir, "d7_endpoint_dvs_PHYSICAL.json")) else None
        unit("DEF1_PYTHON_ARM_WITHOUT_ITS_OWN_ARTIFACT_FAILS", True,
             bool(not g1_completion(tmp, xdir, read_ledger(pled), ["X"], lch)["pass"]),
             "every kind must PRESENT something; absence is not acceptance")
        open(os.path.join(xdir, "d7_endpoint_dvs_PHYSICAL.json"), "w").write("{}")
        unit("DEF1_PYTHON_ARM_WITH_ITS_ARTIFACT_PASSES_AGAIN", True,
             bool(g1_completion(tmp, xdir, read_ledger(pled), ["X"], lch)["pass"]))

        # (2) A CRASHED ARM MUST BE REFUSED BY THE MARKER, even with an `End`
        #     line present -- the false-clean limb the predecessor carried.
        cled = os.path.join(tmp, "ledC.txt")
        open(cled, "w").write(
            "ARM=O ROW=SHIPPED IMG=i DIGEST=d rc=1 wall_s=9 ranks=4 "
            "core_min=0.6 cap_core_min=600.0 enforced_core_min=600.000000 "
            "inspect(exit,oomkilled)=[1 false] log=C.log\n")
        open(os.path.join(tmp, "C.log"), "w").write("banner\nEnd\n")
        open(os.path.join(tmp, "C.log.fail.S3"), "w").write("rc=1 stamp=S3 arm=O\n")
        rC = g1_completion(tmp, w, read_ledger(cled), ["O"], lch)
        unit("DEF1_CRASHED_ARM_IS_REFUSED_BY_THE_MARKER", "FAILED",
             rC["arms"]["O"]["log_terminal"]["marker"]["state"])
        unit("DEF1_CRASHED_ARM_DOES_NOT_PASS_G1", True, bool(not rC["pass"]))
        # (3) NEITHER marker: the launcher died.  UNKNOWN, and not read as
        #     either -- the state a bare .ok/no-.ok pair could never express.
        os.remove(os.path.join(tmp, "C.log.fail.S3"))
        rU = g1_completion(tmp, w, read_ledger(cled), ["O"], lch)
        unit("DEF1_NEITHER_marker_is_UNKNOWN_not_OK_and_not_FAILED", "UNKNOWN",
             rU["arms"]["O"]["log_terminal"]["marker"]["state"])
        unit("DEF1_UNKNOWN_does_not_pass_G1", True, bool(not rU["pass"]))

        # ---- D7R-GRADER-DEF-6: the caps are CHECKED against the document ---
        pre = os.path.join(tmp, "PRE.md")
        good = ("| `P1` | t | SHIPPED | **0.75** | 8.0 | 32.0 |\n"
                "| `X` | t | SHIPPED | **2.0** | 15.0 | 60.0 |\n"
                "| `ACC` | t | SHIPPED | **25.0** | 60.0 | 240.0 |\n"
                "| `F-S` | t | SHIPPED | **485.0** | 750.0 | 3000.0 |\n"
                "| `F-P` | t | PATCHED | **485.0** | 750.0 | 3000.0 |\n")
        open(pre, "w").write(good)
        try:
            r10 = assert_caps_against_document(pre)
            unit("CAPS_agree_with_the_document", 15, r10["n_values_checked"])
        except Refuse as exc:
            unit("CAPS_agree_with_the_document", 15, str(exc)[:120])
        bad = good.replace("| 750.0 | 3000.0 |\n| `F-P`", "| 751.0 | 3000.0 |\n| `F-P`")
        unit("CAPS_mutation_applied", False, bad == good)
        open(pre, "w").write(bad)
        try:
            assert_caps_against_document(pre)
            unit("CAPS_ONE_MOVED_CAP_REFUSES", "REFUSED", "no-refusal")
        except Refuse:
            unit("CAPS_ONE_MOVED_CAP_REFUSES", "REFUSED", "REFUSED")
        open(pre, "w").write("# no table here\n")
        try:
            assert_caps_against_document(pre)
            unit("CAPS_UNPARSEABLE_DOCUMENT_REFUSES", "REFUSED", "no-refusal")
        except Refuse:
            unit("CAPS_UNPARSEABLE_DOCUMENT_REFUSES", "REFUSED", "REFUSED")

        # ---- G10's SPLIT, and that LIMB 2 gates NOTHING while REPORTING ----
        led10 = os.path.join(tmp, "ledger10.txt")
        with open(led10, "w") as fh:
            fh.write("ARM=X ROW=SHIPPED IMG=i DIGEST=d rc=0 wall_s=100 ranks=4 "
                     "core_min=20.0 cap_core_min=15.0 enforced_wall_s=225 "
                     "enforced_core_min=15.000000 memory=4g "
                     "inspect(exit,oomkilled)=[0 false] cpuset=2,3 "
                     "delivered_cores_mean=[3.9 n=3 max_nr_throttled=0] "
                     "log=X.log\n")
        r10 = g10_caps(read_ledger(led10, "G10"), ["X"])
        unit("G10_LIMB2_overrun_does_NOT_fail_the_gate", True, bool(r10["pass"]),
             "actual 20.0 over cap 15.0 and LIMB 1 agrees")
        loud = r10["LIMB2_REPORTED_NOT_GATING__CARRY_INTO_HEADLINE"]
        unit("G10_LIMB2_overrun_IS_REPORTED_with_its_number", 5.0,
             loud["overruns"][0]["overrun_core_min"] if loud["overruns"] else None)
        unit("G10_LIMB2_overrun_carries_DERIVED_dollars", True,
             bool(loud["overruns"] and loud["overruns"][0]["overrun_usd_DERIVED"] > 0))
        with open(led10, "w") as fh:
            fh.write("ARM=X ROW=SHIPPED IMG=i DIGEST=d rc=0 wall_s=100 ranks=4 "
                     "core_min=1.0 cap_core_min=99.0 enforced_wall_s=225 "
                     "enforced_core_min=99.000000 memory=4g "
                     "inspect(exit,oomkilled)=[0 false] cpuset=2,3 "
                     "delivered_cores_mean=[3.9 n=3 max_nr_throttled=0] "
                     "log=X.log\n")
        unit("G10_LIMB1_launcher_enforced_a_DIFFERENT_cap_FAILS_the_gate", True,
             bool(not g10_caps(read_ledger(led10, "G10"), ["X"])["pass"]),
             "ledger says 99.0, the document says 15.0 -- the D7R-DEF-8 class")

        # ---- G2: bands A and B --------------------------------------------
        t = 0.27
        unit("G2_feasible_history_passes_bands_A_and_B", True,
             bool(g2_cl({"CL": [t, t + 1e-6, t + 2e-6]}, t)["pass"]))
        unit("G2_band_A_violation_fails", True,
             bool(not g2_cl({"CL": [t, t + 1e-2, t]}, t)["band_A_pass"]))
        unit("G2_band_B_violation_fails", True,
             bool(not g2_cl({"CL": [t, t, t + 1e-3]}, t)["band_B_pass"]))
        try:
            g2_cl({"CL": []}, t)
            unit("G2_EMPTY_history_refused", True, False, "DID NOT REFUSE")
        except Refuse:
            unit("G2_EMPTY_history_refused", True, True)

        # ---- G3 / G4: IPOPT's own file, and the drag band ------------------
        def _ip_file(name, exitline, red):
            fp = os.path.join(tmp, name)
            cd0 = 3.3e-2
            rows = ["iter    objective    inf_pr   inf_du lg(mu)  ||d||"]
            nn = 8
            for i in range(nn):
                c = cd0 * (1.0 - red * i / (nn - 1))
                rows.append("  %2d  %.7e 4.16e-08 8.10e-03  -5.1 2.83e-01" % (i, c))
            rows.append(exitline)
            open(fp, "w").write("\n".join(rows) + "\n")
            return fp
        ipc = read_ipopt(_ip_file("ip_cap.txt",
                                  "EXIT: Maximum Number of Iterations Exceeded.",
                                  0.10))
        unit("G3_parses_IPOPT_rows_from_its_own_file", True,
             bool(ipc["n_rows"] == 8))
        r3 = g3_exit(ipc)
        unit("G3_CAPSTOP_detected_and_not_converged", True,
             bool(r3["cap_stop"] and not r3["converged"]))
        ipo = read_ipopt(_ip_file("ip_ok.txt", CONVERGED_TOKEN, 0.10))
        unit("G3_CONVERGED_detected", True, bool(g3_exit(ipo)["converged"]))
        try:
            fp = os.path.join(tmp, "ip_empty.txt"); open(fp, "w").write("nothing\n")
            read_ipopt(fp)
            unit("G3_ZERO_ROW_ipopt_file_refused", True, False, "DID NOT REFUSE")
        except Refuse:
            unit("G3_ZERO_ROW_ipopt_file_refused", True, True)
        hist_ok = {"CD": [3.3e-2, 3.3e-2 * 0.90], "CL": [t, t]}
        r4 = g4_drag(ipc, hist_ok)
        unit("G4_in_band_drag_reduction_passes", True,
             bool(r4["pass"]), "%.3f %%" % r4["reduction_pct"])
        ip_big = read_ipopt(_ip_file("ip_big.txt", CONVERGED_TOKEN, 0.60))
        unit("G4_out_of_band_reduction_fails_not_rebanded", True,
             bool(not g4_drag(ip_big, {"CD": [3.3e-2, 3.3e-2 * 0.40],
                                       "CL": [t, t]})["pass"]))
        try:
            g4_drag(ipc, {"CD": [3.3e-2, 3.3e-2 * 0.50], "CL": [t, t]})
            unit("G4_writer_DISAGREEMENT_refused", True, False, "DID NOT REFUSE")
        except Refuse:
            unit("G4_writer_DISAGREEMENT_refused", True, True)

        # ---- G9: TWO ROWS must carry TWO DISTINCT IDWarp .so md5s ----------
        b = os.path.join(tmp, "base"); os.makedirs(b)
        def _mkled(so_s, so_p):
            lp = os.path.join(b, "ledger.txt")
            open(lp, "w").write(
                "ARM=F-S ROW=SHIPPED IMG=a DIGEST=d1 rc=0 wall_s=1 ranks=4 core_min=1 "
                "cap_core_min=130.0 enforced_core_min=130.000000 log=fs.log\n"
                "ARM=F-P ROW=PATCHED IMG=b DIGEST=d2 rc=0 wall_s=1 ranks=4 core_min=1 "
                "cap_core_min=130.0 enforced_core_min=130.000000 log=fp.log\n")
            open(os.path.join(b, "fs.log"), "w").write(
                "D7_CONTAINER_UID: 0\nD7_IDWARP_SO_MD5: %s\n" % so_s)
            open(os.path.join(b, "fp.log"), "w").write(
                "D7_CONTAINER_UID: 0\nD7_IDWARP_SO_MD5: %s\n" % so_p)
            return read_ledger(lp)
        l_ok = _mkled("f" * 32, "8" * 32)
        unit("G9_two_DISTINCT_so_md5s_pass", True,
             bool(g9_toolchain(b, l_ok, ["F-S", "F-P"])["pass"]))
        l_bad = _mkled("f" * 32, "f" * 32)
        r9 = g9_toolchain(b, l_bad, ["F-S", "F-P"])
        unit("G9_IDENTICAL_so_md5s_mean_the_AB_never_happened", True,
             bool(not r9["pass"] and r9["two_rows_present"]))

        # ---- G10: enforced cap must equal the REGISTERED cap ---------------
        lp = os.path.join(tmp, "led10.txt")
        open(lp, "w").write(
            "ARM=F-S ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=100 ranks=4 core_min=500.0 "
            "cap_core_min=750.0 enforced_core_min=750.000000 log=o.log\n")
        unit("G10_matching_cap_passes", True,
             bool(g10_caps(read_ledger(lp), ["F-S"])["pass"]))
        open(lp, "w").write(
            "ARM=F-S ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=100 ranks=4 core_min=500.0 "
            "cap_core_min=1500.0 enforced_core_min=1500.000000 log=o.log\n")
        unit("G10_DRIFTED_cap_fails", True,
             bool(not g10_caps(read_ledger(lp), ["F-S"])["pass"]),
             "enforced 1500 vs registered %s" % CAPS["F-S"])
        open(lp, "w").write(
            "ARM=F-S ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=100 ranks=4 core_min=800.0 "
            "cap_core_min=750.0 enforced_core_min=750.000000 log=o.log\n")
        r10 = g10_caps(read_ledger(lp), ["F-S"])
        unit("G10_OVERRUN_reported_as_a_runaway_not_absorbed", True,
             bool(r10["arms"]["F-S"]["overrun_core_min"] > 0
                  and not r10["arms"]["F-S"]["LIMB2_actual_within_cap"]),
             "overrun=%.1f core-min" % r10["arms"]["F-S"]["overrun_core_min"])

        # ---- G11: the KERNEL's OOM bit ------------------------------------
        open(lp, "w").write(
            "ARM=O ROW=SHIPPED IMG=a DIGEST=d rc=137 wall_s=1 ranks=4 core_min=1 "
            "cap_core_min=600.0 enforced_core_min=600.000000 "
            "inspect(exit,oomkilled)=[137 true] log=o.log\n")
        unit("G11_OOMKilled_true_fails", True,
             bool(not g11_oom(read_ledger(lp), ["O"])["pass"]))
        open(lp, "w").write(
            "ARM=O ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=1 ranks=4 core_min=1 "
            "cap_core_min=600.0 enforced_core_min=600.000000 "
            "inspect(exit,oomkilled)=[0 false] log=o.log\n")
        # D7-GRADER-DEF-3: NOT_MEASURED IS NOT HEALTH.
        _empty_led = {"arms": {}}
        _r11e = g11_oom(_empty_led, ["O"])
        unit("G11_ABSENT_arm_is_NOT_MEASURED_not_a_clean_bill", True,
             bool(not _r11e["pass"] and _r11e["status"] == "NOT_MEASURED"
                  and _r11e["n_arms_read"] == 0),
             "expected=%d read=%d not_measured=%d pass=%s"
             % (_r11e["n_arms_expected"], _r11e["n_arms_read"],
                _r11e["n_arms_not_measured"], _r11e["pass"]))
        _blank_led = {"arms": {"O": {"rc": "0"}}}   # row present, OOM bit absent
        _r11b = g11_oom(_blank_led, ["O"])
        unit("G11_UNRECORDED_oom_bit_is_NOT_MEASURED_not_False", True,
             bool(not _r11b["pass"]
                  and _r11b["arms"]["O"]["status"] == "OOM_BIT_NOT_RECORDED"),
             "oom_killed=%s" % _r11b["arms"]["O"]["oom_killed"])
        unit("G11_OOMKilled_false_passes", True,
             bool(g11_oom(read_ledger(lp), ["O"])["pass"]))

        # ================= ADDENDUM 2 (L-342) -- FIELD CLASSES, DRIVEN =========
        # C1: ABSENT infra -> NOT_MEASURED and proceed; PRESENT garbage -> REFUSE.
        _ra = {"rc": "0"}
        unit("G1_L342_absent_infra_field_is_NOT_MEASURED_and_proceeds", True,
             bool(_infra(_ra, "wall_s", "G1", "O") == NOT_MEASURED))
        _rg = {"rc": "0", "wall_s": "abc"}
        try:
            _infra(_rg, "wall_s", "G1", "O"); _garb = False
        except Refuse as exc:
            _garb = ("ledger_field_unparseable" in str(exc) and "abc" in str(exc))
        unit("G1_L342_present_GARBAGE_infra_field_REFUSES_naming_key_and_value",
             True, bool(_garb))
        try:
            _infra(_ra, "rc", "G1", "O"); _phys = False
        except Refuse as exc:
            _phys = "not_an_infrastructure_field" in str(exc)
        unit("G1_L342_physics_field_cannot_be_read_as_infra", True, bool(_phys))
        # absent PHYSICS (rc) still REFUSES, unchanged
        try:
            _f({"wall_s": "1"}, "rc", "G1", "O"); _ap = False
        except Refuse as exc:
            _ap = "ledger_field_absent" in str(exc)
        unit("G1_L342_absent_PHYSICS_rc_still_REFUSES", True, bool(_ap))
        # a full G1 on a row lacking wall_s/core_min: proceeds, discloses
        bL = os.path.join(tmp, "b_l342"); oL = os.path.join(bL, "O"); os.makedirs(oL)
        lpL = os.path.join(bL, "ledger.txt")
        open(lpL, "w").write(
            "ARM=O ROW=SHIPPED IMG=a DIGEST=d rc=0 ranks=4 "
            "inspect(exit,oomkilled)=[0 false] log=o.log\n")
        open(os.path.join(bL, "o.log"), "w").write("Time = 1\nEnd\n")
        open(os.path.join(bL, "o.log.ok.S9"), "w").write("rc=0 stamp=S9 arm=O\n")
        open(os.path.join(oL, ".d7_age_datum"), "w").write(str(now))
        for nm in ("opt_IPOPT.txt", "OptView.hst", "d7_major_history.json",
                   "d7_endpoint_dvs.json"):
            fp = os.path.join(oL, nm); open(fp, "w").write("x")
            os.utime(fp, (now + 500, now + 500))
        rL = g1_completion(bL, oL, read_ledger(lpL), ["O"], lch)
        unit("G1_L342_row_lacking_wall_s_PROCEEDS_and_DISCLOSES", True,
             bool(rL["pass"] and rL["arms"]["O"]["wall_s"] == NOT_MEASURED
                  and rL["not_measured"][0]["fields"] == ["wall_s", "core_min"]),
             "pass=%s not_measured=%s" % (rL["pass"], rL.get("not_measured")))
        # rc=1 in the row -> G1 fails (unchanged)
        open(lpL, "w").write(
            "ARM=O ROW=SHIPPED IMG=a DIGEST=d rc=1 wall_s=1 ranks=4 core_min=0.1 "
            "inspect(exit,oomkilled)=[1 false] log=o.log\n")
        unit("G1_L342_rc_1_still_FAILS", True,
             bool(not g1_completion(bL, oL, read_ledger(lpL), ["O"], lch)["pass"]))
        # C2: ledger ROW ABSENT, marker present -> rc from the marker, graded
        open(lpL, "w").write("ARM=X ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=1 ranks=4 "
                             "core_min=0.1 inspect(exit,oomkilled)=[0 false] log=x.log\n")
        open(os.path.join(bL, "O_S9.log"), "w").write("Time = 1\nEnd\n")
        os.remove(os.path.join(bL, "o.log.ok.S9"))
        open(os.path.join(bL, "O_S9.log.ok.S9"), "w").write("rc=0 stamp=S9 arm=O\n")
        rLb = g1_completion(bL, oL, read_ledger(lpL), ["O"], lch, containers=[])
        unit("G1_L342_row_ABSENT_marker_present_grades_rc_from_marker", True,
             bool(rLb["pass"] and rLb["arms"]["O"]["rc"] == 0.0
                  and rLb["arms"]["O"]["_source"]["rc"].startswith("marker:")
                  and rLb["arms"]["O"]["ledger_row"] == NOT_MEASURED
                  and rLb["arms"]["O"]["wall_s"] == NOT_MEASURED),
             "src=%s" % rLb["arms"]["O"].get("_source"))
        # C2: container survives -> wall_s from StartedAt/FinishedAt, core_min derived
        def _fake_inspect(name):
            return {"exit": "0", "oomkilled": "false",
                    "started": "2026-08-26T16:00:00.000000000Z",
                    "finished": "2026-08-26T16:01:30.500000000Z"}
        fb = _rc_from_marker_or_container(bL, "O", inspector=_fake_inspect,
                                          containers=["d7fr_O_20260826T160000Z_1"])
        unit("G1_L342_container_survives_wall_s_from_inspect_core_min_derived", True,
             bool(fb["wall_s"] == "90" and fb["core_min"] == "%.3f" % (90 * RANKS / 60.0)
                  and fb["_source"]["wall_s"].startswith("docker_inspect")
                  and fb["inspect(exit,oomkilled)"] == "[0 false]"),
             "fb=%s" % {k: fb[k] for k in ("wall_s", "core_min")})
        unit("G1_L342_NEITHER_marker_nor_container_is_None", True,
             bool(_rc_from_marker_or_container(bL, "F-P", containers=[]) is None))
        # G11: row lacks the OOM bit, container has it -> read from the kernel
        _r11c = g11_oom({"arms": {"O": {"rc": "0"}}}, ["O"], base=bL,
                        inspector=_fake_inspect,
                        containers=["d7fr_O_20260826T160000Z_1"])
        unit("G11_L342_row_lacking_OOM_bit_reads_the_CONTAINER", True,
             bool(_r11c["pass"] and _r11c["arms"]["O"]["_source"].startswith("docker_inspect")))
        _r11d = g11_oom({"arms": {"O": {"rc": "0"}}}, ["O"], base=bL, containers=[])
        unit("G11_L342_row_lacking_OOM_bit_and_no_container_stays_HARD", True,
             bool(not _r11d["pass"] and _r11d["status"] == NOT_MEASURED))
        # C3: G10 limb 1 NOT_MEASURED is disclosed, not passed
        _r10n = g10_caps({"arms": {"F-S": {"rc": "0", "cap_core_min": "750.0"}}}, ["F-S"])
        unit("G10_L342_absent_cap_fields_NOT_MEASURED_disclosed_not_passed", True,
             bool(not _r10n["pass"] and _r10n["arms"]["F-S"]["status"] == NOT_MEASURED
                  and _r10n["not_measured"] == ["F-S"]))
        try:
            g10_caps({"arms": {"F-S": {"rc": "0", "cap_core_min": "x", "enforced_core_min": "1",
                                       "core_min": "1"}}}, ["F-S"]); _g10g = False
        except Refuse as exc:
            _g10g = "ledger_field_unparseable" in str(exc)
        unit("G10_L342_present_GARBAGE_cap_field_REFUSES", True, bool(_g10g))
        # ================= ADDENDUM 3 -- STAGED INPUTS, DRIVEN ================
        bA = os.path.join(tmp, "b_a3"); wA = os.path.join(bA, "X"); os.makedirs(wA)
        lpA = os.path.join(bA, "ledger.txt")
        open(lpA, "w").write(
            "ARM=X ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=9 ranks=4 core_min=0.6 "
            "cap_core_min=15.0 enforced_core_min=15.000000 "
            "inspect(exit,oomkilled)=[0 false] log=XA.log\n")
        open(os.path.join(bA, "XA.log"), "w").write("python arm\n")
        open(os.path.join(bA, "XA.log.ok.S1"), "w").write("rc=0 stamp=S1 arm=X\n")
        open(os.path.join(wA, ".d7_age_datum"), "w").write(str(now))
        for nm in ("opt_IPOPT.txt", "OptView.hst", "d7_major_history.json",
                   "d7_endpoint_dvs.json", "d7_endpoint_dvs_PHYSICAL.json"):
            fp = os.path.join(wA, nm); open(fp, "w").write("x-" + nm)
            os.utime(fp, (now + 500, now + 500))
        # the two STAGED inputs are OLD, as H4 says an inherited input must be
        for nm in ("opt_IPOPT.txt", "OptView.hst"):
            os.utime(os.path.join(wA, nm), (now - 5000, now - 5000))
        m_ov = md5_of(os.path.join(wA, "OptView.hst"))
        m_ip = md5_of(os.path.join(wA, "opt_IPOPT.txt"))
        # (i) NO H4 record -> the old staged files FAIL the age guard (unchanged)
        rA0 = g1_completion(bA, wA, read_ledger(lpA), ["X"], lch)
        unit("G1_A3_old_staged_file_UNNAMED_by_H4_fails_age_guard", True,
             bool(not rA0["pass"] and rA0["age_guard"]["_h4_record"] is None
                  and rA0["age_guard"]["_staged_inputs_exempt"] == []))
        # (ii) H4 record names both with matching md5 -> EXEMPT, proceeds
        open(os.path.join(bA, "X_attempt.log"), "w").write(
            "D7FR_G_ROOT_PASS item=D7FR\nD7FR_H4_PASS arm=X endpoint=D7R/O "
            "OptView.hst=%s opt_IPOPT.txt=%s\n" % (m_ov, m_ip))
        rA1 = g1_completion(bA, wA, read_ledger(lpA), ["X"], lch)
        unit("G1_A3_staged_files_NAMED_by_H4_with_matching_md5_are_EXEMPT", True,
             bool(rA1["pass"]
                  and sorted(rA1["age_guard"]["_staged_inputs_exempt"]) == ["OptView.hst", "opt_IPOPT.txt"]
                  and rA1["age_guard"]["OptView.hst"]["STAGED_INPUT_EXEMPT"]
                  and rA1["age_guard"]["_n_artifacts_checked"] == 2),
             "exempt=%s checked=%s" % (rA1["age_guard"]["_staged_inputs_exempt"],
                                       rA1["age_guard"]["_n_artifacts_checked"]))
        # (iii) the produced artefacts are STILL age-checked: make one stale
        os.utime(os.path.join(wA, "d7_major_history.json"), (now - 500, now - 500))
        unit("G1_A3_exemption_does_not_reach_PRODUCED_artefacts", True,
             bool(not g1_completion(bA, wA, read_ledger(lpA), ["X"], lch)["pass"]))
        os.utime(os.path.join(wA, "d7_major_history.json"), (now + 500, now + 500))
        # (iv) named but md5 MOVED -> REFUSE
        open(os.path.join(bA, "X_attempt.log"), "w").write(
            "D7FR_H4_PASS arm=X endpoint=D7R/O OptView.hst=%s opt_IPOPT.txt=%s\n"
            % ("0" * 32, m_ip))
        try:
            g1_completion(bA, wA, read_ledger(lpA), ["X"], lch); _mm = False
        except Refuse as exc:
            _mm = "staged_input_md5_mismatch" in str(exc)
        unit("G1_A3_named_staged_file_with_MOVED_md5_REFUSES", True, bool(_mm))
        # (v) an H4 line for ANOTHER arm exempts nothing here
        open(os.path.join(bA, "X_attempt.log"), "w").write(
            "D7FR_H4_PASS arm=ACC endpoint=D7R/O OptView.hst=%s opt_IPOPT.txt=%s\n"
            % (m_ov, m_ip))
        unit("G1_A3_H4_line_for_ANOTHER_arm_exempts_nothing", True,
             bool(not g1_completion(bA, wA, read_ledger(lpA), ["X"], lch)["pass"]))
        # G13 in-item: read from the FD arms, never from an arm O
        l13b = os.path.join(bA, "l13.txt")
        open(l13b, "w").write(
            "ARM=F-S ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=1 ranks=4 core_min=1 "
            "cap_core_min=750.0 enforced_core_min=750.000000 "
            "inspect(exit,oomkilled)=[0 false] log=fs.log\n")
        open(os.path.join(bA, "fs.log"), "w").write("PetscConvergedReason: 2\nEnd\n")
        r13i = g13_in_item(bA, read_ledger(l13b), ["P1", "X", "ACC", "F-S"])
        unit("G13_A3_in_item_reads_the_FD_arm_and_passes", True,
             bool(r13i["pass"] and r13i["fd_arms_graded"] == ["F-S"]
                  and r13i["arms"]["F-S"]["min_reason"] == 2))
        r13n = g13_in_item(bA, read_ledger(l13b), ["P1", "X", "ACC"])
        unit("G13_A3_no_FD_arm_is_NOT_MEASURED_not_health", True,
             bool(not r13n["pass"] and r13n["status"] == NOT_MEASURED))
        open(os.path.join(bA, "fs.log"), "w").write("PetscConvergedReason: -9\nEnd\n")
        unit("G13_A3_a_MINUS9_in_an_FD_arm_fails_band_F", True,
             bool(not g13_in_item(bA, read_ledger(l13b), ["F-S"])["pass"]))

        # C3: map_verdict NAMES every NOT_MEASURED limb in the verdict line
        _gm = json.loads(json.dumps(ok_g))
        _gm["G1"] = {"pass": True, "not_measured": [{"arm": "F-S", "fields": ["wall_s"],
                                                     "ledger_row": "PRESENT"}]}
        _gm["G10"] = {"pass": False, "not_measured": ["F-S"]}
        _gm["G12"] = {"pass": False, "arms": {"F-S": {"delivered_cores_mean": NOT_MEASURED}}}
        _vm = map_verdict(_gm)
        # THE MAPPING IS BYTE-UNCHANGED: the wrapper must return exactly the
        # core's verdict token and only ADD the named limitations.
        unit("MAP_L342_NOT_MEASURED_limbs_are_NAMED_in_the_verdict_line", True,
             bool(_vm["verdict"] == _map_verdict_core(_gm)["verdict"]
                  and len(_vm["not_measured"]) == 3
                  and any("LIMITATIONS" in b and "G10" in b and "G12" in b
                          for b in _vm["because"])),
             "not_measured=%d verdict=%s" % (len(_vm["not_measured"]), _vm["verdict"]))
        unit("MAP_L342_clean_gates_carry_an_EMPTY_limitation_list", True,
             bool(map_verdict(json.loads(json.dumps(ok_g)))["not_measured"] == []))

        # ---- G12: placement REFUSES BY COUNT, and needs DISTINCT cores -----
        b2 = os.path.join(tmp, "b2"); ow = os.path.join(b2, "O"); os.makedirs(ow)
        lp2 = os.path.join(b2, "ledger.txt")
        open(lp2, "w").write(
            "ARM=O ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=1 ranks=4 core_min=1 "
            "cap_core_min=600.0 enforced_core_min=600.000000 cpuset=2,3,4,6 "
            "delivered_cores_mean=[3.9000 n=9 max_nr_throttled=0] log=o.log\n")
        l12 = read_ledger(lp2)
        for i, c in enumerate([2, 3, 4]):            # only THREE rank files
            json.dump({"rank": i, "affinity": [c], "n_cores": 1},
                      open(os.path.join(ow, "d7_placement_rank%d.json" % i), "w"))
        # ASSERT THE NAMED REFUSAL, not merely that the gate failed.  With the
        # count check deleted, three rank files still fail the DISTINCTNESS
        # check, so "it failed" proved nothing about the count refusal --
        # MEASURED as mutation m10, which ESCAPED an earlier version of this
        # unit.  Same defect shape as m1.
        _r12 = g12_placement(b2, {"O": ow}, l12)
        unit("G12_REFUSES_BY_COUNT_named_PLACEMENT_COUNT", True,
             bool(not _r12["pass"]
                  and _r12["arms"]["O"].get("refusal_id") == "PLACEMENT_COUNT"),
             "n=3 expected=4 refusal_id=%s"
             % _r12["arms"]["O"].get("refusal_id"))
        json.dump({"rank": 3, "affinity": [6], "n_cores": 1},
                  open(os.path.join(ow, "d7_placement_rank3.json"), "w"))
        unit("G12_four_DISTINCT_pinned_cores_pass", True,
             bool(g12_placement(b2, {"O": ow}, l12)["pass"]))
        json.dump({"rank": 3, "affinity": [2], "n_cores": 1},
                  open(os.path.join(ow, "d7_placement_rank3.json"), "w"))
        unit("G12_COLLIDING_cores_fail", True,
             bool(not g12_placement(b2, {"O": ow}, l12)["pass"]))
        json.dump({"rank": 3, "affinity": [6], "n_cores": 1},
                  open(os.path.join(ow, "d7_placement_rank3.json"), "w"))
        open(lp2, "w").write(
            "ARM=O ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=1 ranks=4 core_min=1 "
            "cap_core_min=600.0 enforced_core_min=600.000000 cpuset=2,3,4,6 "
            "delivered_cores_mean=[0.2500 n=9 max_nr_throttled=88] log=o.log\n")
        unit("G12_STARVED_delivered_cores_fail", True,
             bool(not g12_placement(b2, {"O": read_ledger(lp2)}
                                    and {"O": ow}, read_ledger(lp2))["pass"]),
             "0.25 of 4 delivered, floor %.1f" % DELIVERED_CORES_FLOOR)

        # ---- G13: adjoint health, band F ----------------------------------
        b3 = os.path.join(tmp, "b3"); os.makedirs(b3)
        lp3 = os.path.join(b3, "ledger.txt")
        open(lp3, "w").write(
            "ARM=O ROW=SHIPPED IMG=a DIGEST=d rc=0 wall_s=1 ranks=4 core_min=1 "
            "cap_core_min=600.0 enforced_core_min=600.000000 log=o.log\n")
        l13 = read_ledger(lp3)
        open(os.path.join(b3, "o.log"), "w").write(
            "\n".join(["PetscConvergedReason: 2"] * 30) + "\n")
        unit("G13_all_positive_reasons_pass", True,
             bool(g13_adjoint_health(b3, l13, "O")["pass"]))
        open(os.path.join(b3, "o.log"), "w").write(
            "\n".join(["PetscConvergedReason: 2"] * 29
                       + ["PetscConvergedReason: -9"]) + "\n")
        r13 = g13_adjoint_health(b3, l13, "O")
        unit("G13_a_single_MINUS9_fails_band_F", True,
             bool(not r13["pass"] and r13["blocked_class"]),
             "n=%d min=%d" % (r13["n_reasons_found"], r13["min_reason"]))
        open(os.path.join(b3, "o.log"), "w").write("no reasons here\n")
        r13 = g13_adjoint_health(b3, l13, "O")
        unit("G13_ZERO_reasons_is_NOT_MEASURED_not_health", True,
             bool(not r13["pass"] and r13["status"] == "NOT_MEASURED"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for u in units if u["ok"])
    n = len(units)
    # THE COVERAGE COMPARISON, PRINTED.  Unit COUNT measures SIZE; this
    # measures COVERAGE.  A gate this grader can EMIT but the selftest never
    # EXERCISES is listed by name, because that is exactly how D4's 21-unit
    # selftest came to leave G5 -- this family's entire bright line -- untested.
    emitted = ["G1", "G2", "G3", "G4", "G5", "G6", "G6b", "G7", "G8", "G9",
               "G10", "G11", "G12", "G13"]
    exercised = sorted({u["unit"].split("_")[0] for u in units}
                       - {"CLEAN", "EMPTY", "SHORT", "LONG", "REORDERED",
                          "KEY", "SIGN", "OFF", "NO", "CAPSTOP", "CONVERGED",
                          "ADJOINT", "DECOMP", "MAP"},
                      key=lambda x: (len(x), x))
    # the map_verdict units exercise the mapping of G1/G8/G11/G13 hard-fails
    exercised = sorted(set(exercised) | {"G5", "G8", "G13"},
                       key=lambda x: (len(x), x))
    missing = [g for g in emitted if g not in exercised]
    sys.stdout.write("D7FR_SELFTEST units=%d passed=%d failed=%d\n"
                     % (n, n_ok, n - n_ok))
    sys.stdout.write("D7FR_SELFTEST_COVERAGE emitted=%d [%s]\n"
                     % (len(emitted), ",".join(emitted)))
    sys.stdout.write("D7FR_SELFTEST_COVERAGE exercised=%d [%s]\n"
                     % (len(exercised), ",".join(exercised)))
    sys.stdout.write("D7FR_SELFTEST_COVERAGE UNEXERCISED=%d [%s]\n"
                     % (len(missing), ",".join(missing) if missing else "none"))
    for u in units:
        sys.stdout.write("  %-46s %s  %s\n"
                         % (u["unit"], "ok" if u["ok"] else "FAILED",
                            u["detail"]))
    if n == 0:
        sys.stdout.write("D7FR_SELFTEST REFUSE zero units ran -- a selftest that "
                         "measured nothing is not a selftest (L-302)\n")
        return 3
    return 0 if n_ok == n else 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--work")
    ap.add_argument("--out")
    ap.add_argument("--cl-target")
    ap.add_argument("--launcher", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "d7fr_run_arm.sh"),
        help="the FROZEN launcher whose command branches define each arm's "
             "KIND; this grader REFUSES on an arm it cannot classify")
    ap.add_argument("--prereg", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "PREREGISTRATION.md"),
        help="the FROZEN pre-registration whose sec.7 the caps are checked "
             "against; this grader REFUSES if they disagree")
    ap.add_argument("--fd-shipped")
    ap.add_argument("--fd-patched")
    ap.add_argument("--arms", default="P1,X,ACC,F-S,F-P")
    # WIRED.  Read on the NEXT LINE, with a distinct exit path.  D4-DEF-1.
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        # DISTINCT EXIT PATH.  No --out is written.  Exit 3 is used by nothing
        # else in this file: a graded run exits 0 (D7FR_GRADER OK) or 2
        # (D7FR_GRADER REFUSED).
        sys.exit(selftest())

    for req in ("base", "work", "out", "cl_target"):
        if not getattr(a, req.replace("-", "_")):
            sys.stderr.write("D7FR_GRADER REFUSED missing --%s\n" % req.replace("_", "-"))
            sys.exit(2)
    fd_paths = {}
    if a.fd_shipped:
        fd_paths["SHIPPED"] = a.fd_shipped
    if a.fd_patched:
        fd_paths["PATCHED"] = a.fd_patched
    arms = [x for x in a.arms.split(",") if x]
    try:
        doc = grade(a.base, a.work, a.out, arms, a.cl_target, fd_paths,
                    a.prereg, a.launcher)
    except Refuse as exc:
        sys.stderr.write("D7FR_GRADER REFUSED %s\n" % exc)
        sys.exit(2)
    sys.stdout.write("D7FR_GRADER OK verdict=%s out=%s\n"
                     % (doc["verdict"]["verdict"], a.out))
    sys.exit(0)


if __name__ == "__main__":
    main()
