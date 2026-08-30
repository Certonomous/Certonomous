#!/usr/bin/env python3
"""AV2RG SUCCESSOR COMPARATOR -- re-grades AV2R from its PRESERVED RUN ROOT through a repair
for ONE root cause: THE PRODUCER NEVER WROTE `gmresRelTol` INTO THE ARTEFACT IDENTITY.
ZERO SOLVER COMPUTE: nothing meshed, nothing solved, no container, no GPU.

THE ROOT CAUSE, MEASURED FROM DISK AND NOT FROM THE RECORD.  `av2r_xf.py:56-63`
`idwarp_identity()` returns `{"idwarp_file", "libidwarp_so_md5"}` and NOTHING ELSE; that
dict is written verbatim as `out["identity"]` at `av2r_xf.py:203` (mode X) and `:259`
(mode FAD).  The producer DOES hold the value -- `av2r_xf.py:152-156` emits
`(daOptions.get("adjEqnOption") or {}).get("gmresRelTol")` into the JSONL sidecar ONE
STATEMENT EARLIER -- and simply does not copy it into the artefact.  The frozen grader then
reads `j["identity"]["gmresRelTol"]` (`av2r_grade.py:321`), gets `None`, and REFUSES at
`av2r_grade.py:511-513`.  **THE GRADER IS NOT DEFECTIVE.  IT REFUSED ON ABSENT DATA, WHICH
IS THE CORRECT BEHAVIOUR**, and this successor does not treat it as though it were.

THEREFORE THIS COMPARATOR REBINDS NOTHING.  Registered rebind set: the EMPTY SET.  The
repair is upstream, so it is applied where AVWC applied AV1R's producer repair
(`avwc_grade.py:171-190`): the recovered value is written into a COPY of the artefact and
the frozen `grade()` is then run COMPLETELY UNMODIFIED.  Every band, threshold, composition
rule, planted control and refusal clause that decides the verdict is literally the frozen
code, unedited on disk.  The rebind audit fingerprints every callable before and after and
REFUSES if the rebound set is not exactly `()`.

THE REGISTERED SOURCE IS NOT CHANGED.  `curriculum_AV2R/PREREGISTRATION.md:72` registers
that the grader reads `gmresRelTol` FROM THE ARTEFACT IDENTITY.  It still does.  What this
successor restores is the field the producer was supposed to put there, recovered from the
three independent on-disk sources described in `av2rg_reader.py` and required to agree
EXACTLY -- the frozen grader's own `g_toolchain` three-source rule (`av2r_grade.py:466-479`)
applied to the quantity the producer dropped.

PRESERVED ROOT IS NEVER WRITTEN.  Every run and every plant works on a `cp -a` COPY in
scratch.  Before and after, an md5 manifest of every regular file in the preserved root is
taken and this comparator REFUSES (`PRESERVED_ROOT_MUTATED`, naming the moved paths) if a
single hash moves.  It reads the DISK, not `git status` -- a run root is not in git, so a
git-based cleanliness check is blind to exactly the thing being protected.

BIRTH REQUIREMENT, BOTH DIRECTIONS.  A repaired reader's whole risk is that it LAUNDERS A
GENUINE ABSENCE INTO A PASS, so the MUST-FLAG direction is the point and not decoration.
Every plant travels real preserved files, the real recovery reader and the real frozen
grader.  Registered plants: all three sources absent; each single source absent (there is
no two-of-three vote); the sources made to disagree; the md5 pin on the frozen source
broken; a WRONG-BUT-PRESENT tolerance planted into the repaired artefact (the frozen
grader's own clause must fire and must NOT read PASS); and a reverse total perturbed past
the frozen band so the gate is shown able to still fail.

L-332: NO `assert` anywhere; this module counts `ast.Assert` nodes in its own source and in
the reader's and refuses on any.  No unconditional success print.
"""
import ast
import glob
import hashlib
import importlib.util
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import av2rg_reader as R                                                    # noqa: E402

VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 18

# ---- REGISTERED, frozen with PREREGISTRATION.md ---------------------------------------
ITEM = "AV2R"
CASE = "curriculum_AV2R"
GRADER = "av2r_grade.py"
GRADER_MD5 = "8a2dcebd954f56d9970601fc7761787a"      # == HEAD blob, verified at the freeze
PRODUCER = "av2r_xf.py"
PRODUCER_MD5 = "32a755bc9fa84bc0e03ab02bb6ec3c3c"    # == HEAD blob, verified at the freeze
ROOT = "/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality"
REBIND_REGISTERED = ()                               # THE EMPTY SET -- nothing is rebound
REPAIRED_ARMS = ("X-S", "X-P", "FAD-S", "FAD-P")     # every arm whose artefact carries `identity`
CONSUMED_ARMS = ("X-S", "X-P")                       # the only two the frozen grader reads it from
GMRES_EXPECTED_ON_THE_REAL_ROOT = 1.0e-6             # registered as the PREDICTION, not as a gate
DEFECT_LINES = ("av2r_xf.py:56-63 `idwarp_identity()` (THE PRODUCER) -- the artefact identity "
                "omits `gmresRelTol`; the value is emitted to the JSONL sidecar at :152-156 "
                "one statement earlier. The grader (av2r_grade.py:321, :511-513) is NOT defective.")
ORIGINAL_REFUSAL = ('G-DP {"gmresRelTol_in_artefact": null, "registered": 1e-06, "row": "S"} '
                    '-> NOT A RESULT (AV2R_grade_20260828T024400Z.json)')


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def md5_file(p):
    return R.md5_file(p)


def manifest(root):
    """md5 of every regular file under `root`, keyed by relative path."""
    out = {}
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.isfile(p) and not os.path.islink(p):
                out[os.path.relpath(p, root)] = md5_file(p)
    return out


def _load(path, name, want_md5, tag):
    sys.dont_write_bytecode = True
    got = md5_file(path)
    if got != want_md5:
        refuse("FROZEN_%s_MD5" % tag, {"path": path, "registered": want_md5, "on_disk": got})
    sp = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(sp)
    sys.modules[name] = mod
    sp.loader.exec_module(mod)
    return mod


def load_frozen():
    """Import the frozen grader and the frozen producer AFTER proving each file on disk is
    the file that was frozen.  Bytecode writing is disabled so importing a frozen case's
    module cannot drop a `__pycache__` into its directory and no stale bytecode can invert
    a unit."""
    gpath = os.path.join(A1, CASE, GRADER)
    ppath = os.path.join(A1, CASE, PRODUCER)
    mod = _load(gpath, "av2rg_frozen_grader", GRADER_MD5, "GRADER")
    prod = _load(ppath, "av2rg_frozen_producer", PRODUCER_MD5, "PRODUCER")
    return mod, prod, gpath, ppath


def _fingerprint(mod):
    return {k: id(v) for k, v in vars(mod).items() if callable(v)}


def arm_log_path(copy_root, arm, rows):
    """The arm's solver log, named by the FROZEN grader's own ledger row -- not by a glob,
    so the successor reads the log the frozen instrument itself would have read."""
    name = (rows.get(arm) or {}).get("log")
    return os.path.join(copy_root, name) if name else None


def repair_in_copy(mod, prod, copy_root):
    """Recover `gmresRelTol` per arm from the three registered sources and write it into the
    COPY's artefact identity.  Refusals are raised through THE FROZEN MODULE'S OWN `refuse`,
    so a refusal from here is shaped exactly like the refusal that instrument would have
    raised and carries no new vocabulary.  The expected runScript md5 is taken from the
    FROZEN PRODUCER'S OWN `PRODUCER_MD5` constant, never written here."""
    rows = mod.read_ledger(os.path.join(copy_root, "ledger.txt"))
    rec = {}
    for arm in REPAIRED_ARMS:
        adir = os.path.join(copy_root, arm)
        mode = R.arm_mode(arm)
        art = os.path.join(adir, R.ARTEFACT[mode])
        if not os.path.isfile(art):
            mod.refuse("G-DP", {"artefact_absent": art, "arm": arm})
        val, prov = R.recover_gmres_rel_tol(adir, mode, arm_log_path(copy_root, arm, rows),
                                            prod.PRODUCER_MD5, mod.refuse)
        prov["repair"] = R.repair_identity_in_copy(art, val, mod.refuse)
        prov["consumed_by_frozen_grader"] = arm in CONSUMED_ARMS
        rec[arm] = prov
    return rec


def regrade(workdir, mutate=None, post_repair=None, tag="real"):
    """Re-grade AV2R on a COPY of its preserved root.  `mutate(copy_root)` plants BEFORE the
    repair; `post_repair(copy_root)` plants AFTER it.  Neither ever touches the preserved
    root, and the manifest below is what proves it rather than what asserts it."""
    if not os.path.isdir(ROOT):
        refuse("PRESERVED_ROOT_ABSENT", {"item": ITEM, "root": ROOT})
    before = manifest(ROOT)
    copy_root = os.path.join(workdir, "root_%s" % tag)
    if os.path.isdir(copy_root):
        shutil.rmtree(copy_root)
    shutil.copytree(ROOT, copy_root, symlinks=True)
    pc = os.path.join(copy_root, "__pycache__")
    if os.path.isdir(pc):
        shutil.rmtree(pc)
    if mutate:
        mutate(copy_root)
    mod, prod, gpath, ppath = load_frozen()
    fp0 = _fingerprint(mod)
    out = {"item": ITEM, "tag": tag, "frozen_grader": gpath, "frozen_grader_md5": GRADER_MD5,
           "frozen_producer": ppath, "frozen_producer_md5": PRODUCER_MD5,
           "defect_lines": DEFECT_LINES, "original_refusal": ORIGINAL_REFUSAL,
           "repairs_applied": ["IDENTITY_GMRES_REL_TOL"]}
    recovery = None
    try:
        recovery = repair_in_copy(mod, prod, copy_root)
        if post_repair:
            post_repair(copy_root)
        r = mod.grade(copy_root)
        out["verdict"] = r.get("verdict")
        out["refusal"] = None
        out["grade"] = r
    except Exception as ex:                                                # noqa: BLE001
        if type(ex).__name__ != "Refusal":
            raise
        out["verdict"] = "NOT A RESULT"
        out["refusal"] = str(ex)
        out["grade"] = None
    fp1 = _fingerprint(mod)
    rebound = tuple(sorted(k for k in set(fp0) | set(fp1) if fp0.get(k) != fp1.get(k)))
    if rebound != REBIND_REGISTERED:
        refuse("REBIND_AUDIT", {"expected": list(REBIND_REGISTERED), "actual": list(rebound),
                                "note": "AV2RG rebinds NOTHING; the frozen grader runs unmodified "
                                        "and every band, threshold and composition rule that "
                                        "decides the verdict is the frozen code"})
    out["names_rebound"] = list(rebound)
    out["recovery"] = recovery
    if out["verdict"] not in VOCAB:
        refuse("VOCAB", {"verdict": out["verdict"]})
    after = manifest(ROOT)
    out["preserved_root"] = ROOT
    out["preserved_root_files"] = len(before)
    out["root_manifest_identical"] = (before == after)
    if not out["root_manifest_identical"]:
        moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        refuse("PRESERVED_ROOT_MUTATED", {"root": ROOT, "files_moved": moved[:20]})
    return out


def refusal_clause(out):
    """The refusal's own key and detail keys, so a control can check WHICH clause fired, not
    merely that something did.  A control that only checks 'it refused' passes on the wrong
    refusal."""
    if not out.get("refusal"):
        return None
    txt = out["refusal"]
    i = txt.find("{")
    try:
        d = json.loads(txt[i:]) if i >= 0 else {}
    except ValueError:
        return "UNPARSEABLE"
    det = d.get("detail")
    keys = sorted(det.keys()) if isinstance(det, dict) else []
    return "%s:%s" % (d.get("REFUSE"), ",".join(keys))


# ================= birth-requirement plants (COPIES only, never the preserved root) =====
def _jsonl_path(copy_root, arm):
    return os.path.join(copy_root, arm, R.JSONL[R.arm_mode(arm)])


def _log_paths(copy_root, arm):
    return [p for p in glob.glob(os.path.join(copy_root, "%s_*" % arm)) if p.endswith(".log")]


def _rewrite_identity(copy_root, arm, fn):
    p = _jsonl_path(copy_root, arm)
    lines = []
    for line in open(p, errors="replace"):
        s = line.strip()
        if s:
            try:
                j = json.loads(s)
            except ValueError:
                lines.append(line)
                continue
            if j.get("kind") == "identity":
                keep = fn(j)
                if keep is None:
                    continue
                lines.append(json.dumps(keep, sort_keys=True) + "\n")
                continue
        lines.append(line)
    open(p, "w").writelines(lines)


def plant_drop_runtime(arm):
    """Remove the identity record from the JSONL -- source R absent."""
    def f(root):
        _rewrite_identity(root, arm, lambda j: None)
    return f


def plant_drop_container(arm):
    """Strip the DAOption echo lines from the log copy -- source C absent."""
    def f(root):
        for p in _log_paths(root, arm):
            txt = open(p, errors="replace").read().splitlines(True)
            open(p, "w").writelines([l for l in txt if not R.LOG_ECHO_RE.match(l)])
    return f


def plant_drop_frozen(arm):
    """Remove the arm's runScript -- source F absent."""
    def f(root):
        p = os.path.join(root, arm, R.RUNSCRIPT)
        if os.path.isfile(p):
            os.remove(p)
    return f


def plant_drop_all(arm):
    def f(root):
        plant_drop_runtime(arm)(root)
        plant_drop_container(arm)(root)
        plant_drop_frozen(arm)(root)
    return f


def plant_disagree(arm, value):
    """Plant a DIFFERENT tolerance into source R alone.  The other two still read the real
    value, so the three no longer name one tolerance and the recovery must REFUSE -- which
    is what proves all three are actually read rather than one being trusted."""
    def f(root):
        def fn(j):
            j[R.IDENTITY_KEY] = value
            return j
        _rewrite_identity(root, arm, fn)
    return f


def plant_break_frozen_md5(arm):
    """Append one byte to the arm's runScript.  The md5 pin -- taken from the FROZEN
    PRODUCER's own constant -- must catch it before any value is parsed."""
    def f(root):
        with open(os.path.join(root, arm, R.RUNSCRIPT), "a") as fh:
            fh.write("\n")
    return f


def plant_wrong_tolerance_after_repair(arm, value):
    """AFTER the repair, overwrite the artefact identity with a WRONG BUT PRESENT tolerance.
    THE LAUNDERING TEST: the frozen grader's OWN clause (`av2r_grade.py:511-513`) must fire
    and the item must NOT read PASS.  A repaired reader that turns a wrong tolerance into a
    pass is worse than the refusal it replaced."""
    def f(root):
        p = os.path.join(root, arm, R.ARTEFACT[R.arm_mode(arm)])
        j = json.load(open(p))
        j["identity"][R.IDENTITY_KEY] = value
        json.dump(j, open(p, "w"), indent=1, sort_keys=True)
    return f


def plant_reverse_total_out_of_band(arm, of_key, dv, idx, factor):
    """AFTER the repair, move ONE registered reverse total far outside the frozen band, so
    the gate is shown ABLE TO STILL FAIL on a repaired case.  Registered conditional: if the
    SHIPPED forward row returns MEASURED components the perturbed component must NOT read
    PASS; if that row is `blocked` the frozen composition maps it to BLOCKED and the unit
    records the branch it took."""
    def f(root):
        p = os.path.join(root, arm, R.ARTEFACT[R.arm_mode(arm)])
        j = json.load(open(p))
        v = float(j["adjoint"][of_key][dv][idx])
        j["adjoint"][of_key][dv][idx] = repr(v * factor if v != 0.0 else factor)
        json.dump(j, open(p, "w"), indent=1, sort_keys=True)
    return f


# ================= selftest ============================================================
def selftest(tmp):
    n = 0
    fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    mod, prod, _g, _p = load_frozen()
    G = GMRES_EXPECTED_ON_THE_REAL_ROOT

    # ---- the three sources in isolation, on the REAL preserved files ------------------
    xs = os.path.join(ROOT, "X-S")
    rows = mod.read_ledger(os.path.join(ROOT, "ledger.txt"))
    r_v, r_p = R.source_runtime(xs, "X", mod.refuse)
    unit("U1 SOURCE R on the REAL preserved X-S: exactly one `identity` record and it carries "
         "`gmresRelTol` = %r -- the value the PRODUCER ITSELF held one statement before it "
         "wrote the identity dict that omits it (%s)" % (r_v, os.path.basename(r_p)), r_v == G)
    c_v, c_p = R.source_container(arm_log_path(ROOT, "X-S", rows), mod.refuse)
    unit("U2 SOURCE C on the REAL preserved X-S solver log: the container's own DAOption echo "
         "reads `gmresRelTol %r;` -- what DASimpleFoam actually PARSED, not anybody's record "
         "of what it was asked to be (%s)" % (c_v, os.path.basename(c_p)), c_v == G)
    f_v, f_p = R.source_frozen(xs, prod.PRODUCER_MD5, mod.refuse)
    unit("U3 SOURCE F on the REAL preserved X-S runScript: md5 == the FROZEN PRODUCER'S OWN "
         "`PRODUCER_MD5` (%s) and `daOptions['adjEqnOption']['gmresRelTol']` parses to %r by "
         "`ast`, WITHOUT EXECUTING THE FILE" % (prod.PRODUCER_MD5[:8], f_v), f_v == G)
    xp = os.path.join(ROOT, "X-P")
    p_r, _ = R.source_runtime(xp, "X", mod.refuse)
    p_c, _ = R.source_container(arm_log_path(ROOT, "X-P", rows), mod.refuse)
    p_f, _ = R.source_frozen(xp, prod.PRODUCER_MD5, mod.refuse)
    unit("U4 THE PATCHED ROW IS MEASURED, NOT INFERRED FROM THE SHIPPED ROW: all three sources "
         "on the REAL preserved X-P read %r, %r, %r independently" % (p_r, p_c, p_f),
         p_r == p_c == p_f == G)

    # ---- MUST-NOT-FLAG: the real preserved root ---------------------------------------
    real = regrade(tmp, tag="real")
    unit("U5 MUST-NOT-FLAG: on the REAL preserved root the original refusal "
         "`G-DP gmresRelTol_in_artefact null` is GONE -- no refusal raised anywhere in this "
         "re-grade names `gmresRelTol` (clause now %r)" % refusal_clause(real),
         "gmresRelTol" not in (real["refusal"] or ""))
    unit("U6 the repair is VISIBLE ON DISK where the producer left a hole: on both arms the "
         "frozen grader consumes (X-S, X-P) the COPY's `identity.gmresRelTol` reads %r where "
         "the preserved artefact carries the key NOT AT ALL"
         % G,
         all(real["recovery"][a]["repair"]["before"] is None
             and real["recovery"][a]["repair"]["after"] == G for a in CONSUMED_ARMS))
    unit("U7 REBIND AUDIT: the set of rebound callables is EXACTLY the empty set -- the frozen "
         "grader ran COMPLETELY UNMODIFIED, so every band, threshold, planted control and "
         "composition rule that decided this verdict is the frozen code, unedited on disk",
         real["names_rebound"] == [])
    unit("U8 the PRESERVED run root is byte-identical after the re-grade (%d regular files, "
         "md5 manifest before == after, read from the DISK and not from `git status`)"
         % real["preserved_root_files"], real["root_manifest_identical"])
    unit("U9 the verdict is from the FIXED vocabulary and is whatever the FROZEN instrument "
         "produced (got %r)" % real["verdict"], real["verdict"] in VOCAB)

    # ---- MUST-FLAG: absence must never be laundered into a pass ------------------------
    b_all = regrade(tmp, mutate=plant_drop_all("X-S"), tag="drop_all")
    unit("U10 MUST-FLAG: ALL THREE sources removed from X-S -> still REFUSED, and the verdict "
         "is NOT A RESULT. A repaired reader that cannot still refuse is not repaired, it is "
         "disabled (clause %r)" % refusal_clause(b_all),
         b_all["verdict"] == "NOT A RESULT" and "gmresRelTol_source_absent" in (b_all["refusal"] or ""))
    b_r = regrade(tmp, mutate=plant_drop_runtime("X-S"), tag="drop_runtime")
    unit("U11 MUST-FLAG: source R alone removed -> REFUSED. THERE IS NO TWO-OF-THREE VOTE: a "
         "missing source means the tolerance the adjoint solve ran at is unknown, and an "
         "unknown tolerance is not a band (clause %r)" % refusal_clause(b_r),
         b_r["verdict"] == "NOT A RESULT" and "RUNTIME" in (b_r["refusal"] or ""))
    b_c = regrade(tmp, mutate=plant_drop_container("X-S"), tag="drop_container")
    unit("U12 MUST-FLAG: source C alone removed (the DAOption echo stripped from the log copy) "
         "-> REFUSED, proving the log is genuinely read and is not decoration (clause %r)"
         % refusal_clause(b_c),
         b_c["verdict"] == "NOT A RESULT" and "CONTAINER" in (b_c["refusal"] or ""))
    b_f = regrade(tmp, mutate=plant_drop_frozen("X-S"), tag="drop_frozen")
    unit("U13 MUST-FLAG: source F alone removed -> REFUSED (clause %r)" % refusal_clause(b_f),
         b_f["verdict"] == "NOT A RESULT" and "FROZEN" in (b_f["refusal"] or ""))
    b_d = regrade(tmp, mutate=plant_disagree("X-S", 1.0e-5), tag="disagree")
    unit("U14 MUST-FLAG: 1e-5 planted into source R ALONE -> REFUSED on "
         "`gmresRelTol_sources_disagree` with all three values printed. This is what proves "
         "all three sources are read rather than one being trusted and two decorated "
         "(clause %r)" % refusal_clause(b_d),
         b_d["verdict"] == "NOT A RESULT" and "gmresRelTol_sources_disagree" in (b_d["refusal"] or ""))
    b_m = regrade(tmp, mutate=plant_break_frozen_md5("X-S"), tag="break_md5")
    unit("U15 MUST-FLAG: one byte appended to X-S's runScript -> REFUSED on "
         "`gmresRelTol_runscript_md5_moved` BEFORE any value is parsed. The pin is taken from "
         "the FROZEN PRODUCER'S OWN constant, so the successor cannot silently read a "
         "different runScript (clause %r)" % refusal_clause(b_m),
         b_m["verdict"] == "NOT A RESULT" and "gmresRelTol_runscript_md5_moved" in (b_m["refusal"] or ""))

    # ---- MUST-FLAG: a WRONG BUT PRESENT tolerance must not become a PASS ---------------
    b_w = regrade(tmp, post_repair=plant_wrong_tolerance_after_repair("X-S", 1.0e-5), tag="wrong_tol")
    unit("U16 MUST-FLAG, THE LAUNDERING TEST: a wrong-but-PRESENT tolerance (1e-5) planted into "
         "the repaired artefact -> THE FROZEN GRADER'S OWN CLAUSE `av2r_grade.py:511-513` "
         "fires, `gmresRelTol_in_artefact` reads 1e-05 and the verdict is NOT A RESULT. The "
         "repair restores the field; it does not weaken the check the field feeds (clause %r)"
         % refusal_clause(b_w),
         b_w["verdict"] == "NOT A RESULT" and "gmresRelTol_in_artefact" in (b_w["refusal"] or ""))

    # ---- MUST-FLAG: the gate must still be able to fail on a repaired case -------------
    b_g = regrade(tmp, post_repair=plant_reverse_total_out_of_band("X-S", "CD", "shape", 3, 2.0),
                  tag="out_of_band")
    unit("U17 MUST-FLAG: with the repair applied, one registered reverse total (CD/shape[3]) "
         "DOUBLED -- five orders outside the frozen band 1.0e-5 -- the item does NOT read PASS. "
         "REGISTERED CONDITIONAL: if the SHIPPED forward row returns MEASURED components the "
         "frozen G-DP reads GATE FAIL or refuses on it; if that row is `blocked` the frozen "
         "composition maps the item to BLOCKED. Either branch satisfies this unit; what is "
         "forbidden is PASS. Branch taken: verdict %r, clause %r"
         % (b_g["verdict"], refusal_clause(b_g)),
         b_g["verdict"] != "PASS" and b_g["verdict"] in VOCAB)

    unit("U18 every plant ran on a COPY: the preserved run root is byte-identical after ALL "
         "eight re-grades in this selftest",
         all(x["root_manifest_identical"] for x in (real, b_all, b_r, b_c, b_f, b_d, b_m, b_w, b_g)))

    print("AV2RG SELFTEST units=%d expected=%d failures=%d python_O=%s"
          % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("AV2RG SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    for p in (os.path.abspath(__file__), os.path.join(HERE, "av2rg_reader.py")):
        if count_asserts(p) != 0:
            print("REFUSAL: %s carries an assert statement (L-332)" % p)
            return 2
    d = os.path.join(a.tmpdir, "av2rg_%d" % os.getpid())
    os.makedirs(d, exist_ok=True)
    if a.selftest:
        return selftest(d)
    try:
        r = regrade(d, tag="real")
    except Refusal as ex:
        r = {"item": ITEM, "verdict": "NOT A RESULT", "successor_refusal": str(ex)}
    print("%-5s  ORIGINAL: NOT A RESULT (%s)" % (ITEM, ORIGINAL_REFUSAL))
    print("       RE-GRADED: %s   rebound=%s   preserved_root_identical=%s"
          % (r.get("verdict"), r.get("names_rebound"), r.get("root_manifest_identical")))
    if r.get("refusal"):
        print("       refusal clause: %s" % refusal_clause(r))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
