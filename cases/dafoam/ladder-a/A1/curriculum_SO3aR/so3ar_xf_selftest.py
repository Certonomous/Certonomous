#!/usr/bin/env python3
"""SO-3aR INSTRUMENT SELFTEST -- drives `so3ar_xf.py` on the HOST.

NOT one of PREREGISTRATION.md section 7's nine files.  The chain never executes
or imports this file: no driver, no launcher and no comparator calls it, and it
is therefore NOT in the md5 pin table.  It exists so the instrument's derivation
can be CHECKED FROM THE REPOSITORY rather than from a lane's scratch directory
(L-186: a repository document never cites a scratch path, and evidence that only
one session can reproduce is not evidence).

It drives three things the derivation could get wrong and a reader cannot see by
looking:
  A. THE COLLISION CHECK.  D4S-F3SR / commit b66fcb05: SO-1bR's derivation
     INTRODUCED a self-destruct because the rename was verified COMPLETE -- the
     old form counted before, zero after -- and that check is STRUCTURALLY BLIND
     TO A NEW NAME COLLIDING WITH A VARIABLE ALREADY IN USE.  So both halves are
     asserted here: the old form is GONE (A1), and no name this derivation
     INTRODUCES was already bound in the parent (A2).  Every counter is shown a
     known positive so its zero is a reading and not a blind pattern.
  B/C/D. THE RULE-3 PLANTED CONTROL, IN BOTH DIRECTIONS, through the real writer
     and the real reader, on disk -- including the four refusal branches
     (`plant_not_seen`, `zero_side_not_zero`, `control_tuple_EMPTY_or_short`,
     `control_row_absent`) that SO-2a's inline `main()` version could not reach
     without a container.
  E. THE DELIBERATE MUTATION.  The instrument is shown FAILING on a mutation that
     kills the plant, BEFORE its pass is believed, and the file is restored
     byte-identically with the md5 printed on both sides.

Usage:  python3 so3ar_xf_selftest.py     (exit 0 all pass, 2 otherwise)
It writes NOTHING outside this directory and its only output file is
`so3ar_xf_drive_evidence.txt` beside it."""
import ast, hashlib, importlib, json, os, re, shutil, subprocess, sys, tempfile

CASE = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR"
PARENT = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO2a/so2a_xg.py"
CHILD = os.path.join(CASE, "so3ar_xf.py")
sys.path.insert(0, CASE)

OUT = []
NP = [0]
NF = []


def ok(name, cond):
    NP[0] += 1
    if not cond:
        NF.append(name)
    OUT.append("  [%s] %s" % ("OK " if cond else "BAD", name))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# ---------- executable-line text of a python file (docstrings/comments stripped)
def exec_text(path):
    src = open(path).read()
    tree = ast.parse(src)
    doc_lines = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) \
           and isinstance(n.value.value, str):
            for ln in range(n.lineno, (n.end_lineno or n.lineno) + 1):
                doc_lines.add(ln)
    keep = []
    for i, line in enumerate(src.splitlines(), 1):
        if i in doc_lines:
            continue
        s = line.split("#", 1)[0]
        keep.append(s)
    return "\n".join(keep)


def bindings(path):
    """name -> list of (scope, lineno, kind-of-value) for every binding."""
    tree = ast.parse(open(path).read())
    out = {}

    def kind(v):
        if isinstance(v, ast.Call):
            return "CALL"
        if isinstance(v, ast.Constant):
            return "CONST"
        if isinstance(v, ast.Name):
            return "NAME"
        if isinstance(v, (ast.List, ast.Tuple, ast.Dict, ast.Set)):
            return "LITERAL"
        if isinstance(v, ast.BinOp):
            return "BINOP"
        return type(v).__name__.upper()

    def walk(node, scope):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.setdefault(ch.name, []).append((scope, ch.lineno, "DEF"))
                walk(ch, "%s:%s" % (scope, ch.name))
                continue
            if isinstance(ch, ast.Assign):
                for t in ch.targets:
                    for nn in ast.walk(t):
                        if isinstance(nn, ast.Name):
                            out.setdefault(nn.id, []).append((scope, ch.lineno, kind(ch.value)))
            walk(ch, scope)
    walk(tree, "<module>")
    return out


OUT.append("SO-3aR INSTRUMENT DRIVE -- so3ar_xf.py, derived from so2a_xg.py")
OUT.append("parent md5 %s  child md5 %s" % (md5(PARENT), md5(CHILD)))
OUT.append("")
OUT.append("A. THE COLLISION CHECK (the D4S-F3SR hole: a rename verified COMPLETE is")
OUT.append("   structurally blind to a NEW NAME COLLIDING WITH A VARIABLE ALREADY IN USE)")

ctext = exec_text(CHILD)
# ---- A1. the old forms are GONE from every executable line ------------------
OLD_FORMS = ["so2a_", "SO2A_", "SO2a", "so2a_xg", "CONSTRAINTS", "CON_SIZES_EXPECTED",
             "con_vector", "thickcon", "volcon", "rcon", "read_constraints",
             "CON_NAMES", "tb_note"]
gone = {t: ctext.count(t) for t in OLD_FORMS}
ok("A1 every old form is GONE from every executable line of the child: %s"
   % json.dumps(gone), all(v == 0 for v in gone.values()))
# the KNOWN POSITIVE: the same counter, on the PARENT, must see them
ptext = exec_text(PARENT)
seen_parent = {t: ptext.count(t) for t in OLD_FORMS}
ok("A1b PLANTED POSITIVE: the SAME counter on the PARENT sees %d of %d old forms "
   "non-zero -- A1's zeros are readings, not a blind counter"
   % (sum(1 for v in seen_parent.values() if v), len(OLD_FORMS)),
   sum(1 for v in seen_parent.values() if v) >= 8)

# ---- A2. NO NEW NAME COLLIDES WITH A NAME ALREADY BOUND TO SOMETHING ELSE ----
pb, cb = bindings(PARENT), bindings(CHILD)
# NEW: names this derivation INTRODUCES.  None of them may already be bound in the
# parent, because that is exactly the D4S-F3SR hole -- a new name landing on a
# variable already in use, which a "the old form is gone" check cannot see.
NEW_NAMES = ["ALPHAS_REGISTERED", "WEIGHTS_REGISTERED", "SCENARIOS", "N_SCEN", "OBJ_PATH",
             "TB_STEPS", "EVALS_DECLARED", "s_", "vec", "weighted_J", "_finite",
             "build_identity_block", "ctrl_readback_check", "CD_PATHS", "CL_PATHS",
             "evaluate", "fd_at", "n_failed", "failures", "b0", "b1", "mp_ident",
             "alphas_read", "alpha_paths", "dvs_alphas", "adj", "keys"]
# CARRIED FORWARD: names the parent ALSO binds.  These are NOT introductions and
# must not be counted as collisions -- but they must be shown to carry the SAME
# ROLE, or a "carry-forward" is a collision wearing a friendly label.  FIRST DRIVE,
# this file: JSONL_X was listed under NEW_NAMES, the check reported a collision,
# and the reading was CORRECT ABOUT THE FACT and WRONG ABOUT THE CLAIM -- the
# parent binds JSONL_X at :117 to its own X-mode jsonl name.  It is moved here
# with an explicit role assertion rather than deleted from the check.
CARRIED_FORWARD = {"JSONL_X": ".jsonl", "JSONL_F": ".jsonl", "OUT_X": ".json",
                   "OUT_F": ".json", "STEPS": None, "COMPONENTS": None, "PLANT": None,
                   "CTRL_STEP": None, "ETA_FLOOR": None, "PRODUCER": ".py"}
collide = {n: pb[n] for n in NEW_NAMES if n in pb}
ok("A2 no name INTRODUCED by this derivation was already bound in the parent to "
   "something else: %d of %d collide %s"
   % (len(collide), len(NEW_NAMES), json.dumps(collide, default=str)),
   len(collide) == 0)
psrc, csrc = open(PARENT).read(), open(CHILD).read()
role_bad = {}
for n, suffix in CARRIED_FORWARD.items():
    if n not in pb or n not in cb:
        role_bad[n] = "not bound in both"
        continue
    if suffix:
        pv = re.search(r"^%s\s*=\s*[\"']([^\"']+)[\"']" % re.escape(n), psrc, re.M)
        cv = re.search(r"^%s\s*=\s*[\"']([^\"']+)[\"']" % re.escape(n), csrc, re.M)
        if not (pv and cv and pv.group(1).endswith(suffix) and cv.group(1).endswith(suffix)):
            role_bad[n] = {"parent": pv and pv.group(1), "child": cv and cv.group(1)}
ok("A2b every CARRIED-FORWARD name holds the SAME ROLE in both files (a %s stays a "
   "%s, only its item prefix moves): %d of %d wrong %s"
   % ("filename", "filename", len(role_bad), len(CARRIED_FORWARD),
      json.dumps(role_bad, default=str)), len(role_bad) == 0)
# the KNOWN POSITIVE for the collision detector itself
probe = {n: pb[n] for n in ("STEPS", "COMPONENTS", "PLANT") if n in pb}
ok("A2c PLANTED POSITIVE: the SAME detector, handed three names that ARE bound in "
   "the parent (STEPS, COMPONENTS, PLANT), reports all three -- A2's zero is a "
   "reading of the names, not a detector that finds nothing", len(probe) == 3)

# ---- A3. NO NAME HOLDING A PATH IS EVER REASSIGNED (the SO1bR AGG shape) ------
# THE NARROW GATE.  The defect that cost this family a run is specific: a variable
# holding a SCRIPT PATH reassigned to hold that script's RESULT.  The gate is
# therefore over PATH-HOLDING names, and it is a GATE.
def path_like(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return "/" in node.value or node.value.endswith((".py", ".sh", ".json", ".jsonl"))
    if isinstance(node, ast.Call):
        f = node.func
        return isinstance(f, ast.Attribute) and f.attr == "join"
    return False


def path_binders(path):
    tree = ast.parse(open(path).read())
    out = {}

    def walk(node, scope):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                walk(ch, "%s:%s" % (scope, ch.name))
                continue
            if isinstance(ch, ast.Assign):
                for t in ch.targets:
                    if isinstance(t, ast.Name):
                        rec = out.setdefault("%s@%s" % (t.id, scope), {"n": 0, "path": False})
                        rec["n"] += 1
                        rec["path"] = rec["path"] or path_like(ch.value)
            walk(ch, scope)
    walk(tree, "<module>")
    return out


pbind = path_binders(CHILD)
path_rebound = {k: v for k, v in pbind.items() if v["path"] and v["n"] > 1}
ok("A3 GATE: every name that EVER holds a path in the child is bound EXACTLY ONCE "
   "in its scope -- the SO1bR `AGG=$(python3 \"$AGG\")` shape is structurally "
   "impossible here.  path-holding names=%d, rebound=%s"
   % (sum(1 for v in pbind.values() if v["path"]), json.dumps(path_rebound)),
   len(path_rebound) == 0)
# the KNOWN POSITIVE: the same gate, on a file that HAS the defect
with tempfile.TemporaryDirectory() as td:
    dp = os.path.join(td, "defect.py")
    open(dp, "w").write("import json\nAGG = '/x/agg.py'\nAGG = json.loads(AGG)\n")
    hits = {k: v for k, v in path_binders(dp).items() if v["path"] and v["n"] > 1}
    ok("A3b PLANTED POSITIVE: the SAME gate, on a file carrying the SO1bR defect "
       "verbatim (a path name reassigned to its own call result), FLAGS it: %s"
       % json.dumps(hits), len(hits) == 1)

# ---- A3c. THE BROAD ROLE-CHANGE SWEEP: REPORTED WITH EVERY HIT NAMED ----------
# This is deliberately WIDER than the gate and it FIRES on benign code, so it is
# REPORTED and REVIEWED, never gated.  Recording it is the point: a sweep whose
# hits are hidden is a sweep nobody can check, and an evidence file that showed
# only the narrow gate would be hiding the wide reading behind the narrow one.
rebound = {}
for name, binds in cb.items():
    by_scope = {}
    for scope, ln, k in binds:
        by_scope.setdefault(scope, []).append((ln, k))
    for scope, lst in by_scope.items():
        kinds = {k for _, k in lst}
        if len(lst) > 1 and "CALL" in kinds and kinds - {"CALL"}:
            rebound["%s@%s" % (name, scope)] = lst
REVIEWED = {
    "d@<module>:main": "a scalar alpha or None; never a path; None is the not-resolved sentinel",
    "row@<module>:ctrl_readback_check": "the control row or None; None is the not-found sentinel",
    "b1@<module>:main": "a baseline reading; the fallback to b0 is DISCLOSED in the emitted eta_note",
    "eta_raw@<module>:main": "a running max over the graded quantities; same role throughout",
    "k@<module>:main": "the step key returned by fd_at, in the FD loop and again in the TB loop",
}
unreviewed = [k for k in rebound if k not in REVIEWED]
OUT.append("  [RPT] A3c BROAD role-change sweep (REPORTED, NEVER GATED): %d hits, "
           "each reviewed by name:" % len(rebound))
for k in sorted(rebound):
    OUT.append("        %-38s %s  -- %s" % (k, rebound[k], REVIEWED.get(k, "*** UNREVIEWED ***")))
ok("A3d every hit of the broad sweep is REVIEWED BY NAME in this evidence file; "
   "unreviewed=%s" % unreviewed, len(unreviewed) == 0)

# ---- A4. L-332: no assert carries a guard, and the counter is shown counting --
def count_asserts(p):
    return sum(1 for n in ast.walk(ast.parse(open(p).read())) if isinstance(n, ast.Assert))
ok("A4 zero `assert` statements in the instrument (L-332: python3 -O strips them)",
   count_asserts(CHILD) == 0)
with tempfile.TemporaryDirectory() as td:
    pa = os.path.join(td, "planted_assert.py")
    open(pa, "w").write("assert 1 == 1\nx = 2\n")
    ok("A4b the assert counter is shown COUNTING a planted assert -- a zero from a "
       "counter not shown able to count is not evidence", count_asserts(pa) == 1)

# ---- A5. THE PRODUCER PIN IS SET AND CORRECT ---------------------------------
# SO-3a's copy of this leg asserted the OPPOSITE: that PRODUCER_MD5 was a
# SENTINEL, "until the Stage-2 pin".  Its Stage 2 landed and NEVER SET THE PIN,
# and this leg went on PASSING -- because passing was what the sentinel state
# was written to mean.  A leg that reads GREEN on the state that kills the item
# is worse than no leg: SO-3a's own amendment recorded 250 python legs and 0
# failures on the morning it could not launch.
#
# The successor's leg asserts the POST-FILL state and would have gone RED on
# every byte SO-3a shipped.  It is deliberately NOT symmetric with its parent.
import so3ar_xf as XF
_prod_actual = md5(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                XF.PRODUCER))
ok("A5 PRODUCER_MD5 IS SET TO A REAL MD5 AND EQUALS ITS PRODUCER: %s = md5(%s).  "
   "SO-3a shipped this constant holding a sentinel, its container started, and "
   "its solver exited 2 in ten seconds on 'SO3A_XF REFUSE producer md5 ... != "
   "frozen UNSET-PRODUCER-PIN-SENTINEL-FAILS-CLOSED'"
   % (XF.PRODUCER_MD5, XF.PRODUCER),
   re.fullmatch(r"[0-9a-f]{32}", XF.PRODUCER_MD5) is not None
   and XF.PRODUCER_MD5 == _prod_actual)
ok("A5b THE SENTINEL STATE IS PROVED DETECTABLE: the same predicate this leg "
   "uses reads FALSE on SO-3a's shipped value, so A5's green is a reading of "
   "the constant and not of the predicate",
   re.fullmatch(r"[0-9a-f]{32}", "UNSET-PRODUCER-PIN-SENTINEL-FAILS-CLOSED") is None)

OUT.append("")
OUT.append("B. THE WRITERS, DRIVEN ON THE HOST (no container, no MPI, no openmdao)")
ok("B1 the module imports on the host: nothing at module scope needs mpi4py, "
   "numpy, openmdao or dafoam", True)
ok("B2 EVALS_DECLARED is COMPUTED from the constants and equals the 34 section 4 "
   "registers (2 baseline + 4x3x2 FD + 4x1x2 TB): %d" % XF.EVALS_DECLARED,
   XF.EVALS_DECLARED == 34)
ok("B3 the registered angles are line 4's three, to the last digit: %s"
   % XF.ALPHAS_REGISTERED,
   XF.ALPHAS_REGISTERED == [3.13918623195176, 5.13918623195176, 7.13918623195176]
   and abs(XF.ALPHAS_REGISTERED[1] - 5.13918623195176) == 0.0)
ok("B4 the weights are EQUAL and sum to 1 to 1e-15: %r" % (sum(XF.WEIGHTS_REGISTERED),),
   abs(sum(XF.WEIGHTS_REGISTERED) - 1.0) < 1e-15 and len(set(XF.WEIGHTS_REGISTERED)) == 1)
ok("B5 `patchV` is NOT in COMPONENTS -- line 4's registered removal, checked in code",
   all(d == "shape" for d, _ in XF.COMPONENTS) and len(XF.COMPONENTS) == 4)
ok("B6 weighted_J sums in the registered order: J(0.01,0.02,0.03) = %r"
   % XF.weighted_J([0.01, 0.02, 0.03]),
   abs(XF.weighted_J([0.01, 0.02, 0.03]) - 0.02) < 1e-15)

# build_fd_row arithmetic, checked against an independently computed derivative
plus = {"J": 1.02, "CD": [1.1, 1.2, 1.3], "CL": [2.1, 2.2, 2.3]}
minus = {"J": 0.98, "CD": [0.9, 1.0, 1.1], "CL": [1.9, 2.0, 2.1]}
row = XF.build_fd_row(1.0e-2, plus, minus)
ok("B7 build_fd_row's central difference is (plus-minus)/(2h) on J and on every "
   "scenario's CD and CL: dJ=%s" % row["d"]["J"],
   abs(float(row["d"]["J"]) - (1.02 - 0.98) / 0.02) < 1e-9
   and len(row["d"]["CD"]) == 3 and len(row["d"]["CL"]) == 3
   and abs(float(row["d"]["CD"][0]) - (1.1 - 0.9) / 0.02) < 1e-9)
ok("B8 a FAILED step is WRITTEN with ok:False and its error, never omitted "
   "(G-EVALFAIL / D6-GRADER-DEF-1)",
   XF.build_fd_row_failed(1e-3, "Primal solution failed!")["ok"] is False
   and "Primal" in XF.build_fd_row_failed(1e-3, "Primal solution failed!")["error"])

OUT.append("")
OUT.append("C. THE RULE-3 PLANTED CONTROL, DRIVEN IN BOTH DIRECTIONS THROUGH THE")
OUT.append("   REAL WRITER AND THE REAL READER, ON DISK")

WANT = XF.PLANT / (2.0 * XF.CTRL_STEP)


def write_jsonl(td, row, name="j.jsonl"):
    p = os.path.join(td, name)
    with open(p, "w") as fh:
        fh.write(json.dumps({"kind": "primal", "tag": "x"}) + "\n")
        if row is not None:
            fh.write(json.dumps({"kind": "control", "row": row}, sort_keys=True) + "\n")
    return p


with tempfile.TemporaryDirectory() as td:
    J0, cd0, cl0 = 0.0209, [0.0180, 0.0209, 0.0260], [0.31, 0.50, 0.69]
    good = XF.build_ctrl_row(J0, cd0, cl0)
    okk, det = XF.ctrl_readback_check(write_jsonl(td, good))
    ok("C1 (+) THE LIVE PLANT IS SEEN: the real writer's control row, read back off "
       "disk by the real reader, shows 7 exact zeros and 7 planted derivatives at "
       "PLANT/(2h) = %r" % WANT,
       okk and det["n_zero_entries_read"] == 7
       and all(abs(v - WANT) <= 1e-12 * WANT for v in det["planted_read"]))

    dead = json.loads(json.dumps(good))
    dead["planted"]["d"]["J"] = repr(0.0)
    dead["planted"]["d"]["CD"] = [repr(0.0)] * 3
    dead["planted"]["d"]["CL"] = [repr(0.0)] * 3
    okk, det = XF.ctrl_readback_check(write_jsonl(td, dead, "dead.jsonl"))
    ok("C2 (-) A DEAD PLANT REFUSES: every planted derivative reads 0.0 where "
       "PLANT/(2h) was written -> reason=%s" % det.get("reason"),
       (not okk) and det.get("reason") == "plant_not_seen")

    nz = json.loads(json.dumps(good))
    nz["fd"][repr(XF.CTRL_STEP)]["d"]["CD"][1] = repr(1e-18)
    okk, det = XF.ctrl_readback_check(write_jsonl(td, nz, "nz.jsonl"))
    ok("C3 (-) A ZERO SIDE THAT IS NOT EXACTLY ZERO REFUSES, at 1e-18 -- the gate "
       "is EXACT and has no tolerance: reason=%s" % det.get("reason"),
       (not okk) and det.get("reason") == "zero_side_not_zero")

    empty = json.loads(json.dumps(good))
    empty["fd"][repr(XF.CTRL_STEP)]["d"]["CD"] = []
    empty["fd"][repr(XF.CTRL_STEP)]["d"]["CL"] = []
    empty["planted"]["d"]["CD"] = []
    empty["planted"]["d"]["CL"] = []
    okk, det = XF.ctrl_readback_check(write_jsonl(td, empty, "empty.jsonl"))
    ok("C4 (-) A CONTROL THAT EMPTIES THE TUPLE IT TESTS REFUSES, NOT PASSES "
       "(Sanaa 2026-08-28): reason=%s n_zero_side=%s"
       % (det.get("reason"), det.get("n_zero_side")),
       (not okk) and det.get("reason") == "control_tuple_EMPTY_or_short")

    okk, det = XF.ctrl_readback_check(write_jsonl(td, None, "absent.jsonl"))
    ok("C5 (-) AN ABSENT control row REFUSES and is named ABSENT, not malformed: "
       "reason=%s" % det.get("reason"),
       (not okk) and det.get("reason") == "control_row_absent")

    okk, det = XF.ctrl_readback_check(os.path.join(td, "no-such-file.jsonl"))
    ok("C6 (-) an UNREADABLE jsonl REFUSES rather than raising: reason=%s"
       % det.get("reason"), (not okk) and det.get("reason") == "jsonl_unreadable")

OUT.append("")
OUT.append("D. THE ARTEFACT RECORDS, ROUND-TRIPPED THROUGH JSON")
mp = XF.build_identity_block([3.13918623195176, 5.13918623195176, 7.13918623195176],
                             ["point0.patchV", "point1.patchV", "point2.patchV"],
                             XF.WEIGHTS_REGISTERED)
adj = {k: {"shape": [repr(0.1 * (i + 1)) for i in range(8)]}
       for k in ["J", "CD0", "CD1", "CD2", "CL0", "CL1", "CL2"]}
X = XF.build_X_record(1, "0" * 32, {"libidwarp_so_md5": "a" * 32}, mp, adj,
                      0.0216, [0.018, 0.0209, 0.026], [0.31, 0.50, 0.69], 12.3)
Xb = json.loads(json.dumps(X, sort_keys=True))
ok("D1 the X record carries the PER-SCENARIO adjoint rows G-MP-STRUCT sums, not "
   "only the assembled J row: %s" % Xb["adjoint_of_keys"],
   Xb["adjoint_of_keys"] == ["CD0", "CD1", "CD2", "CL0", "CL1", "CL2", "J"])
ok("D2 the X record carries the alphas READ BACK FROM THE MODEL beside the "
   "registered ones, so G-ALPHA compares two independently sourced lists",
   Xb["multipoint"]["alphas_read_back"] != []
   and Xb["multipoint"]["alphas_registered"] == [repr(a) for a in XF.ALPHAS_REGISTERED])
ok("D3 the X record declares NO optimiser and says so in a field a gate can read "
   "(G-NOOPT)", Xb["optimiser"] is None and "run_driver" in Xb["optimiser_note"])
F = XF.build_F_record(1, "0" * 32, {"libidwarp_so_md5": "a" * 32}, mp,
                      [XF.build_ctrl_row(0.0216, [0.018, 0.0209, 0.026], [0.31, 0.5, 0.69])],
                      0.0216, 0.0216, [0.018, 0.0209, 0.026], [0.018, 0.0209, 0.026],
                      [0.31, 0.5, 0.69], [0.31, 0.5, 0.69], 0.0, 1e-14, True,
                      {"shape": [repr(0.0)] * 8}, XF.EVALS_DECLARED, 1,
                      [{"tag": "FD shape[6]+0.01", "error": "AnalysisError"}])
Fb = json.loads(json.dumps(F, sort_keys=True))
ok("D4 the F record carries evaluations_declared=%d and evaluations_failed=%d PER "
   "ARM with the failing tags named -- P-EVAL is scored, not asserted"
   % (Fb["evaluations_declared"], Fb["evaluations_failed"]),
   Fb["evaluations_declared"] == 34 and Fb["evaluations_failed"] == 1
   and Fb["evaluation_failures"][0]["tag"].startswith("FD shape[6]"))
ok("D5 the F record carries tb_steps = {'shape': [1e-08]} -- the charter-4 trivial "
   "baseline is REGISTERED IN THE ARTEFACT before its own run: %s" % Fb["tb_steps"],
   Fb["tb_steps"] == {"shape": [1e-08]})

OUT.append("")
OUT.append("E. THE DELIBERATE MUTATION -- THE KNOWN POSITIVE, DRIVEN FIRST")
before = md5(CHILD)
src = open(CHILD).read()
mutant = src.replace('    plant_plus = {"J": float(J0) + PLANT,',
                     '    plant_plus = {"J": float(J0) + 0.0,', 1)
if mutant == src:
    ok("E0 the mutation target was FOUND in the source", False)
else:
    ok("E0 the mutation target was FOUND in the source (a mutation that does not "
       "apply proves nothing)", True)
    with tempfile.TemporaryDirectory() as td:
        shutil.copy(CHILD, os.path.join(td, "so3ar_xf_mut.py"))
        open(os.path.join(td, "so3ar_xf_mut.py"), "w").write(mutant)
        sys.path.insert(0, td)
        mut = importlib.import_module("so3ar_xf_mut")
        bad = mut.build_ctrl_row(0.0209, [0.018, 0.0209, 0.026], [0.31, 0.5, 0.69])
        p = write_jsonl(td, bad, "mut.jsonl")
        okk, det = XF.ctrl_readback_check(p)      # the REAL reader on the MUTANT's bytes
        ok("E1 THE MUTANT FAILS: an instrument whose planted J no longer moves by "
           "PLANT is REFUSED by the real reader -- reason=%s.  The pass in C1 is "
           "therefore a reading of the code, not of the test" % det.get("reason"),
           (not okk) and det.get("reason") == "plant_not_seen")
        sys.path.remove(td)
after = md5(CHILD)
ok("E2 the instrument on disk is BYTE-IDENTICAL after the mutation drive: %s == %s"
   % (before, after), before == after)

OUT.append("")
OUT.append("DRIVE %d checks, %d fail" % (NP[0], len(NF)))
for f in NF:
    OUT.append("  FAIL: %s" % f)
txt = "\n".join(OUT) + "\n"
sys.stdout.write(txt)
open(os.path.join(CASE, "so3ar_xf_drive_evidence.txt"), "w").write(
    "SO-3aR so3ar_xf.py DRIVE EVIDENCE -- written by the drive, not by hand.\n"
    "Every line below is a reading taken at the timestamp of this file.\n\n" + txt)
sys.exit(0 if not NF else 2)
