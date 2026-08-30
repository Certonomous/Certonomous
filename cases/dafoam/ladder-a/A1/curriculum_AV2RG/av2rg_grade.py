#!/usr/bin/env python3
"""AV2RG SUCCESSOR COMPARATOR -- re-grades AV2R **and AV2** from their PRESERVED RUN ROOTS
through a repair for ONE root cause: THE PRODUCER NEVER WROTE `gmresRelTol` INTO THE ARTEFACT
IDENTITY.  ZERO SOLVER COMPUTE: nothing meshed, nothing solved, no container, no GPU.

THE ROOT CAUSE, MEASURED FROM DISK AND NOT FROM THE RECORD.  `av2r_xf.py:56-63`
`idwarp_identity()` returns `{"idwarp_file", "libidwarp_so_md5"}` and NOTHING ELSE; that
dict is written verbatim as `out["identity"]` at `av2r_xf.py:203` (mode X) and `:259`
(mode FAD).  The producer DOES hold the value -- `av2r_xf.py:152-156` emits
`(daOptions.get("adjEqnOption") or {}).get("gmresRelTol")` into the JSONL sidecar ONE
STATEMENT EARLIER -- and simply does not copy it into the artefact.  The frozen grader then
reads `j["identity"]["gmresRelTol"]` (`av2r_grade.py:321`), gets `None`, and REFUSES at
`av2r_grade.py:511-513`.  **THE GRADER IS NOT DEFECTIVE.  IT REFUSED ON ABSENT DATA, WHICH
IS THE CORRECT BEHAVIOUR**, and this successor does not treat it as though it were.

TWO ITEMS, ONE INSTRUMENT, BECAUSE IT IS ONE LINE OF SOURCE.  `idwarp_identity()` is
BYTE-IDENTICAL between `curriculum_AV2/av2_xf.py` and `curriculum_AV2R/av2r_xf.py`; AV2's
grader reads the same key by the same path (`av2_grade.py:252`) and refuses in the same
clause (`:442-443`) against the same registered `1.0e-6` (`:70`).  Measured on AV2's own
preserved root: all four arms carry `identity` keys exactly `['idwarp_file',
'libidwarp_so_md5']` and all three sources read `1e-06`.  A fifth implementation is what
this family keeps paying for, so AV2 is an entry here and not a new case.

REPAIRS ARE A SET PER ITEM, and AV2 needs TWO.  AV2 also carries the `writeCompression`
DATUM defect, which AVWC repaired (`0/U` vs `0/U.gz`); AVWC's re-grade cleared it and AV2
then landed on THIS clause.  So AV2 = {DATUM, GMRES} and AV2R = {GMRES}.  **THE DATUM
RESOLVER IS AVWC'S OWN, IMPORTED AND md5-VERIFIED -- NOT REWRITTEN.**  AV2R needs no datum
repair: `av2r_grade.py:73` already resolves by candidate set.

REBIND SETS, PER ITEM.  AV2R rebinds NOTHING (the empty set): the repair is upstream, so it
is applied where AVWC applied AV1R's producer repair (`avwc_grade.py:171-190`) -- the
recovered value is written into a COPY of the artefact and the frozen `grade()` runs
COMPLETELY UNMODIFIED.  AV2 rebinds exactly `arm_datum`, AVWC's registered name for the
datum variant.  The audit fingerprints every callable before and after and REFUSES if the
rebound set is not exactly the item's registered set.

THE REPAIR PRESERVES THE ARTEFACT'S MTIME.  Both frozen graders age-guard the artefact
(`av2r_grade.py:288-289`, `av2_grade.py:219-220`), so a rewrite that stamped a fresh mtime
would make a rule-4 PHYSICS guard pass on THIS INSTRUMENT'S WRITE.  `repair_identity_in_copy`
restores and verifies the original (atime, mtime), and U-AGE below plants an mtime OLDER
than the datum to prove the guard can still fire after the repair.

PRESERVED ROOTS ARE NEVER WRITTEN.  Every run and every plant works on a `cp -a` COPY in
scratch.  Before and after, an md5 manifest of every regular file in the preserved root is
taken and this comparator REFUSES (`PRESERVED_ROOT_MUTATED`, naming the moved paths) if a
single hash moves.  It reads the DISK, not `git status` -- a run root is not in git, so a
git-based cleanliness check is blind to exactly the thing being protected.

BIRTH REQUIREMENT, BOTH DIRECTIONS.  A repaired reader's whole risk is that it LAUNDERS A
GENUINE ABSENCE INTO A PASS, so the MUST-FLAG direction is the point and not decoration.
Every plant travels real preserved files, the real recovery reader and the real frozen
grader.

L-332: NO `assert` anywhere; this module counts `ast.Assert` nodes in its own source and in
the reader's and refuses on any.  No unconditional success print.
"""
import ast
import glob
import importlib.util
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = os.path.dirname(HERE)
# AMENDMENT 2 (2026-08-30): THE FLAG MUST PRECEDE THE FIRST IMPORT, NOT SIT INSIDE `_load`.
# v1.1 set `sys.dont_write_bytecode` inside `_load()` only, so THIS module's own reader was
# byte-compiled at the import below before the flag was ever set, and a
# `av2rg_reader.cpython-312.opt-1.pyc` landed in this directory during the v1.1 run.  A stale
# `.pyc` INVERTS a mutation test -- clean control fails, mutated case passes -- and
# PYTHONDONTWRITEBYTECODE does NOT cure it; only clearing `__pycache__` does.  The frozen
# case directories were clean, so the REGISTERED claim was not falsified; this closes the
# hazard at its source instead of relying on the caller to clear the directory first.
sys.dont_write_bytecode = True
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import av2rg_reader as R                                                    # noqa: E402

VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 28

# ---- REGISTERED, frozen with PREREGISTRATION.md (Amendment 1 for the AV2 entry) --------
AVWC_CASE = "curriculum_AVWC"
AVWC_GRADE_MD5 = "6e390f8f3c0df5d4229dd3640590ca44"   # == HEAD blob, verified at the freeze
AVWC_READER_MD5 = "1a7f3f211f44c7b67b4f8f2d4c65bf4a"  # == HEAD blob, verified at the freeze

ITEMS = {
    # AV2R's datum variant was already repaired IN-ITEM (`av2r_grade.py:73`
    # DATUM_REF_CANDIDATES), so its only defect is the producer's omission and its grader is
    # run COMPLETELY UNMODIFIED.
    "AV2R": {"repairs": ("GMRES",), "rebind": (), "case": "curriculum_AV2R",
             "prefix": "av2r", "datum_file": ".av2r_age_datum",
             "grader": "av2r_grade.py", "grader_md5": "8a2dcebd954f56d9970601fc7761787a",
             "producer": "av2r_xf.py", "producer_md5": "32a755bc9fa84bc0e03ab02bb6ec3c3c",
             "root": "/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality",
             "defect_lines": "av2r_xf.py:56-63 `idwarp_identity()` (THE PRODUCER); the grader "
                             "(av2r_grade.py:321, :511-513) is NOT defective",
             "original_refusal": 'G-DP {"gmresRelTol_in_artefact": null, "registered": 1e-06, '
                                 '"row": "S"} -> NOT A RESULT '
                                 '(AV2R_grade_20260828T024400Z.json)'},
    # AV2 carries BOTH the writeCompression DATUM variant (repaired by AVWC) and this
    # producer omission.  Measured, not assumed: AVWC's re-grade cleared the datum and AV2
    # landed on THIS clause (`curriculum_AVWC/AVWC_regrade.json`).
    "AV2": {"repairs": ("DATUM", "GMRES"), "rebind": ("arm_datum",), "case": "curriculum_AV2",
            "prefix": "av2", "datum_file": ".av2_age_datum",
            "grader": "av2_grade.py", "grader_md5": "4bde0ad7dbdd3e460dcef1fe6d063979",
            "producer": "av2_xf.py", "producer_md5": "76bc93090062e0bf03de2344709e384f",
            "root": "/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality",
            "defect_lines": "av2_xf.py:56-63 `idwarp_identity()` -- BYTE-IDENTICAL to "
                            "av2r_xf.py:56-63 -- PLUS the writeCompression datum variant at "
                            "av2_grade.py:186-188 that AVWC repaired",
            "original_refusal": 'G1 age_reference_absent .../X-S/0/U -> NOT A RESULT; after '
                                "AVWC's datum repair, G-DP "
                                '{"gmresRelTol_in_artefact": null, "row": "S"} -> NOT A RESULT '
                                "(curriculum_AVWC/AVWC_regrade.json)"},
}

REPAIRED_ARMS = ("X-S", "X-P", "FAD-S", "FAD-P")   # every arm whose artefact carries `identity`
CONSUMED_ARMS = ("X-S", "X-P")                     # the only two a frozen grader reads it from
GMRES_EXPECTED_ON_THE_REAL_ROOTS = 1.0e-6          # registered as the PREDICTION, not as a gate


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


def load_frozen(item):
    """Import the item's frozen grader and its frozen producer AFTER proving each file on
    disk is the file that was frozen.  Bytecode writing is disabled so importing a frozen
    case's module cannot drop a `__pycache__` into its directory and no stale bytecode can
    invert a unit."""
    spec = ITEMS[item]
    gpath = os.path.join(A1, spec["case"], spec["grader"])
    ppath = os.path.join(A1, spec["case"], spec["producer"])
    mod = _load(gpath, "av2rg_frozen_grader_%s" % item, spec["grader_md5"], "GRADER")
    prod = _load(ppath, "av2rg_frozen_producer_%s" % item, spec["producer_md5"], "PRODUCER")
    return mod, prod, gpath, ppath


def load_avwc():
    """AVWC's frozen datum machinery, md5-verified and ADOPTED.  This successor does not
    write a second datum resolver: `resolve_datum` is AVWC's, which in turn adopted
    `so1a_grade.py:292-338`.  A lesson is not applied until every call site asserts it, and
    a repair is not adopted until it is the SAME CODE."""
    _load(os.path.join(A1, AVWC_CASE, "avwc_reader.py"), "av2rg_avwc_reader",
          AVWC_READER_MD5, "AVWC_READER")
    return _load(os.path.join(A1, AVWC_CASE, "avwc_grade.py"), "av2rg_avwc_grade",
                 AVWC_GRADE_MD5, "AVWC_GRADE")


def _fingerprint(mod):
    return {k: id(v) for k, v in vars(mod).items() if callable(v)}


def arm_log_path(root, arm, rows):
    """The arm's solver log, named by the FROZEN grader's own ledger row -- not by a glob,
    so the successor reads the log the frozen instrument itself would have read."""
    name = (rows.get(arm) or {}).get("log")
    return os.path.join(root, name) if name else None


def repair_gmres_in_copy(item, mod, prod, copy_root):
    """Recover `gmresRelTol` per arm from the three registered sources and write it into the
    COPY's artefact identity, preserving the artefact's mtime.  Refusals are raised through
    THE FROZEN MODULE'S OWN `refuse`, so a refusal from here is shaped exactly like the
    refusal that instrument would have raised and carries no new vocabulary.  The expected
    runScript md5 is taken from the FROZEN PRODUCER'S OWN `PRODUCER_MD5` constant, never
    written here."""
    spec = ITEMS[item]
    prefix = spec["prefix"]
    rows = mod.read_ledger(os.path.join(copy_root, "ledger.txt"))
    rec = {}
    for arm in REPAIRED_ARMS:
        adir = os.path.join(copy_root, arm)
        mode = R.arm_mode(arm)
        art = os.path.join(adir, R.artefact_name(prefix, mode))
        if not os.path.isfile(art):
            mod.refuse("G-DP", {"artefact_absent": art, "arm": arm})
        val, prov = R.recover_gmres_rel_tol(adir, prefix, mode,
                                            arm_log_path(copy_root, arm, rows),
                                            prod.PRODUCER_MD5, mod.refuse)
        prov["repair"] = R.repair_identity_in_copy(art, val, mod.refuse)
        prov["consumed_by_frozen_grader"] = arm in CONSUMED_ARMS
        rec[arm] = prov
    return rec


def regrade(item, workdir, mutate=None, post_repair=None, repairs=None, tag=None):
    """Re-grade ONE item on a COPY of its preserved root.  `mutate(copy_root)` plants BEFORE
    the repair; `post_repair(copy_root)` plants AFTER it.  Neither ever touches the preserved
    root, and the manifest below is what proves it rather than what asserts it."""
    spec = ITEMS[item]
    src = spec["root"]
    tag = tag or "real"
    if not os.path.isdir(src):
        refuse("PRESERVED_ROOT_ABSENT", {"item": item, "root": src})
    before = manifest(src)
    copy_root = os.path.join(workdir, "root_%s_%s" % (item, tag))
    if os.path.isdir(copy_root):
        shutil.rmtree(copy_root)
    shutil.copytree(src, copy_root, symlinks=True)
    pc = os.path.join(copy_root, "__pycache__")
    if os.path.isdir(pc):
        shutil.rmtree(pc)
    if mutate:
        mutate(copy_root)
    mod, prod, gpath, ppath = load_frozen(item)
    fp0 = _fingerprint(mod)
    applied = tuple(repairs) if repairs is not None else tuple(spec["repairs"])
    for x in applied:
        if x not in spec["repairs"]:
            refuse("UNREGISTERED_REPAIR", {"item": item, "asked": x,
                                           "registered": list(spec["repairs"])})
    out = {"item": item, "tag": tag, "repairs_applied": list(applied),
           "frozen_grader": gpath, "frozen_grader_md5": spec["grader_md5"],
           "frozen_producer": ppath, "frozen_producer_md5": spec["producer_md5"],
           "defect_lines": spec["defect_lines"], "original_refusal": spec["original_refusal"]}
    audit, recovery = {}, None
    try:
        if "DATUM" in applied:
            avwc = load_avwc()
            mod.arm_datum = avwc.make_repaired_arm_datum(mod, spec["datum_file"], audit)
        if "GMRES" in applied:
            recovery = repair_gmres_in_copy(item, mod, prod, copy_root)
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
    expected = tuple(spec["rebind"]) if "DATUM" in applied else ()
    if rebound != expected:
        refuse("REBIND_AUDIT", {"item": item, "expected": list(expected), "actual": list(rebound),
                                "note": "the successor replaces exactly the registered names and "
                                        "no others; everything else that decides the verdict is "
                                        "the frozen code"})
    out["names_rebound"] = list(rebound)
    out["recovery"] = recovery
    out["datum_resolution"] = audit or None
    if out["verdict"] not in VOCAB:
        refuse("VOCAB", {"item": item, "verdict": out["verdict"]})
    after = manifest(src)
    out["preserved_root"] = src
    out["preserved_root_files"] = len(before)
    out["root_manifest_identical"] = (before == after)
    if not out["root_manifest_identical"]:
        moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        refuse("PRESERVED_ROOT_MUTATED", {"item": item, "root": src, "files_moved": moved[:20]})
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
def _prefix(item):
    return ITEMS[item]["prefix"]


def _jsonl_path(copy_root, item, arm):
    return os.path.join(copy_root, arm, R.jsonl_name(_prefix(item), R.arm_mode(arm)))


def _art_path(copy_root, item, arm):
    return os.path.join(copy_root, arm, R.artefact_name(_prefix(item), R.arm_mode(arm)))


def _log_paths(copy_root, arm):
    return [p for p in glob.glob(os.path.join(copy_root, "%s_*" % arm)) if p.endswith(".log")]


def _rewrite_identity(copy_root, item, arm, fn):
    p = _jsonl_path(copy_root, item, arm)
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


def plant_drop_runtime(item, arm):
    """Remove the identity record from the JSONL -- source R absent."""
    def f(root):
        _rewrite_identity(root, item, arm, lambda j: None)
    return f


def plant_drop_container(arm):
    """Strip the DAOption echo lines from the log copy -- source C absent."""
    def f(root):
        for p in _log_paths(root, arm):
            txt = open(p, errors="replace").read().splitlines(True)
            open(p, "w").writelines([l for l in txt if not R.LOG_ECHO_RE.match(l)])
    return f


def plant_drop_frozen(item, arm):
    """Remove the arm's runScript -- source F absent."""
    def f(root):
        p = os.path.join(root, arm, R.runscript_name(_prefix(item)))
        if os.path.isfile(p):
            os.remove(p)
    return f


def plant_drop_all(item, arm):
    def f(root):
        plant_drop_runtime(item, arm)(root)
        plant_drop_container(arm)(root)
        plant_drop_frozen(item, arm)(root)
    return f


def plant_disagree(item, arm, value):
    """Plant a DIFFERENT tolerance into source R alone.  The other two still read the real
    value, so the three no longer name one tolerance and the recovery must REFUSE -- which
    is what proves all three sources are read rather than one being trusted."""
    def f(root):
        def fn(j):
            j[R.IDENTITY_KEY] = value
            return j
        _rewrite_identity(root, item, arm, fn)
    return f


def plant_break_frozen_md5(item, arm):
    """Append one byte to the arm's runScript.  The md5 pin -- taken from the FROZEN
    PRODUCER's own constant -- must catch it BEFORE any value is parsed."""
    def f(root):
        with open(os.path.join(root, arm, R.runscript_name(_prefix(item))), "a") as fh:
            fh.write("\n")
    return f


def plant_wrong_tolerance_after_repair(item, arm, value):
    """AFTER the repair, overwrite the artefact identity with a WRONG BUT PRESENT tolerance.
    THE LAUNDERING TEST: the frozen grader's OWN clause must fire and the item must NOT read
    `PASS`.  A repaired reader that turns a wrong tolerance into a pass is worse than the
    refusal it replaced.  The mtime is preserved so this plant tests the tolerance clause and
    nothing else."""
    def f(root):
        p = _art_path(root, item, arm)
        st = os.stat(p)
        j = json.load(open(p))
        j["identity"][R.IDENTITY_KEY] = value
        json.dump(j, open(p, "w"), indent=1, sort_keys=True)
        os.utime(p, (st.st_atime, st.st_mtime))
    return f


def plant_artefact_older_than_datum(item, arm, seconds=100):
    """AFTER the repair, back-date the artefact BEFORE its arm's launch datum.  THE AGE GUARD
    MUST STILL FIRE.  This is the must-flag direction for the hazard the mtime preservation
    guards: if the repair had stamped a fresh mtime, this guard would have been silently
    satisfied by THIS INSTRUMENT'S WRITE on every arm, for ever."""
    def f(root):
        d = os.path.join(root, arm)
        datum = int(open(os.path.join(d, ITEMS[item]["datum_file"])).read().strip())
        p = _art_path(root, item, arm)
        os.utime(p, (datum - seconds, datum - seconds))
    return f


def plant_reverse_total_out_of_band(item, arm, of_key, dv, idx, factor):
    """AFTER the repair, move ONE registered reverse total far outside the frozen band, so
    the gate is shown ABLE TO STILL FAIL on a repaired case.  REGISTERED CONDITIONAL: if the
    SHIPPED forward row returns MEASURED components the frozen `G-DP` reads `GATE FAIL` on
    the perturbed component or refuses on it; if that row is `blocked` the frozen composition
    maps the item to `BLOCKED`.  Either branch satisfies the unit; what is forbidden is
    `PASS`."""
    def f(root):
        p = _art_path(root, item, arm)
        st = os.stat(p)
        j = json.load(open(p))
        v = float(j["adjoint"][of_key][dv][idx])
        j["adjoint"][of_key][dv][idx] = repr(v * factor if v != 0.0 else factor)
        json.dump(j, open(p, "w"), indent=1, sort_keys=True)
        os.utime(p, (st.st_atime, st.st_mtime))
    return f


# ================= CONDITION C driver (§2d.1 ruling, 2026-08-30) =======================
CORRECTED_CLAUSE = "gmresRelTol_runtime_identity_records"


def _corrected_unit_can_fail(tmp, plant, tag):
    """PROVE the corrected U13/U14 assertions CAN STILL FAIL.  A corrected assertion that
    merely matches whatever the code happens to emit is the exact failure mode this sweep
    exists to catch, so `R.source_runtime` is replaced by a stub that RETURNS instead of
    refusing -- the reader is made not to refuse on precisely the plant the unit tests -- and
    the corrected condition must then read FALSE.  The real function is restored in a
    `finally` and the restoration is itself checked and reported, because a control that
    leaves a stub installed would silently disarm every unit after it."""
    realfn = R.source_runtime
    try:
        R.source_runtime = (lambda arm_dir, prefix, mode, refuse:
                            (GMRES_EXPECTED_ON_THE_REAL_ROOTS, "<stubbed: made not to refuse>"))
        out = regrade("AV2R", tmp, mutate=plant, tag=tag)
        fired = CORRECTED_CLAUSE in (out["refusal"] or "")
    finally:
        R.source_runtime = realfn
    return (not fired), (R.source_runtime is realfn), out


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

    G = GMRES_EXPECTED_ON_THE_REAL_ROOTS

    # ---- the three sources in isolation, on the REAL preserved files (AV2R) -----------
    mod, prod, _g, _p = load_frozen("AV2R")
    root2r = ITEMS["AV2R"]["root"]
    rows = mod.read_ledger(os.path.join(root2r, "ledger.txt"))
    xs = os.path.join(root2r, "X-S")
    r_v, r_p = R.source_runtime(xs, "av2r", "X", mod.refuse)
    unit("U1 SOURCE R on the REAL preserved AV2R X-S: exactly one `identity` record and it "
         "carries `gmresRelTol` = %r -- the value the PRODUCER ITSELF held one statement "
         "before it wrote the identity dict that omits it (%s)" % (r_v, os.path.basename(r_p)),
         r_v == G)
    c_v, c_p = R.source_container(arm_log_path(root2r, "X-S", rows), mod.refuse)
    unit("U2 SOURCE C on the REAL preserved AV2R X-S solver log: the container's own DAOption "
         "echo reads `gmresRelTol %r;` -- what DASimpleFoam actually PARSED, not anybody's "
         "record of what it was asked to be (%s)" % (c_v, os.path.basename(c_p)), c_v == G)
    f_v, _f_p = R.source_frozen(xs, "av2r", prod.PRODUCER_MD5, mod.refuse)
    unit("U3 SOURCE F on the REAL preserved AV2R X-S runScript: md5 == the FROZEN PRODUCER'S "
         "OWN `PRODUCER_MD5` (%s) and `daOptions['adjEqnOption']['gmresRelTol']` parses to %r "
         "by `ast`, WITHOUT EXECUTING THE FILE" % (prod.PRODUCER_MD5[:8], f_v), f_v == G)
    xp = os.path.join(root2r, "X-P")
    p_r, _ = R.source_runtime(xp, "av2r", "X", mod.refuse)
    p_c, _ = R.source_container(arm_log_path(root2r, "X-P", rows), mod.refuse)
    p_f, _ = R.source_frozen(xp, "av2r", prod.PRODUCER_MD5, mod.refuse)
    unit("U4 THE PATCHED ROW IS MEASURED, NOT INFERRED FROM THE SHIPPED ROW: all three sources "
         "on the REAL preserved AV2R X-P read %r, %r, %r independently" % (p_r, p_c, p_f),
         p_r == p_c == p_f == G)

    # ---- AV2's sources, measured on ITS root and not inherited from AV2R ---------------
    mod2, prod2, _g2, _p2 = load_frozen("AV2")
    root2 = ITEMS["AV2"]["root"]
    rows2 = mod2.read_ledger(os.path.join(root2, "ledger.txt"))
    a2 = {}
    for arm in CONSUMED_ARMS:
        d = os.path.join(root2, arm)
        a2[arm] = (R.source_runtime(d, "av2", "X", mod2.refuse)[0],
                   R.source_container(arm_log_path(root2, arm, rows2), mod2.refuse)[0],
                   R.source_frozen(d, "av2", prod2.PRODUCER_MD5, mod2.refuse)[0])
    unit("U5 AV2'S OWN ROOT IS MEASURED, NOT INHERITED: all three sources on X-S %s and on X-P "
         "%s. AV2 and AV2R have IDENTICAL arm names and both are serial on every arm "
         "(`av2_grade.py:59` == `av2r_grade.py:59`, ARM_RANKS all 1), so only the file prefix "
         "differs" % (a2["X-S"], a2["X-P"]),
         all(v == G for t in a2.values() for v in t))
    unit("U6 AV2'S GRADER READS THE SAME KEY BY THE SAME PATH and refuses in the same clause "
         "against the same registered tolerance -- which is why AV2 is an ENTRY here and not "
         "a fifth implementation",
         mod2.GMRES_REL_TOL_REGISTERED == mod.GMRES_REL_TOL_REGISTERED == G
         and mod2.DP_BAND == mod.DP_BAND)

    # ---- MUST-NOT-FLAG: the real preserved root (AV2R) ---------------------------------
    real = regrade("AV2R", tmp, tag="real")
    unit("U7 MUST-NOT-FLAG (AV2R): on the REAL preserved root the original refusal "
         "`G-DP gmresRelTol_in_artefact null` is GONE -- no refusal raised anywhere in this "
         "re-grade names `gmresRelTol` (clause now %r)" % refusal_clause(real),
         "gmresRelTol" not in (real["refusal"] or ""))
    unit("U8 the repair is VISIBLE ON DISK where the producer left a hole: on both arms the "
         "frozen grader consumes (X-S, X-P) the COPY's `identity.gmresRelTol` reads %r where "
         "the preserved artefact carries the key NOT AT ALL" % G,
         all(real["recovery"][a]["repair"]["before"] is None
             and real["recovery"][a]["repair"]["after"] == G for a in CONSUMED_ARMS))
    unit("U9 THE ARTEFACT'S MTIME SURVIVED THE REPAIR on all four repaired arms. Both frozen "
         "graders age-guard this very file (`av2r_grade.py:288-289`), and that guard is a "
         "rule-4 PHYSICS field: a rewrite that stamped a fresh mtime would make it pass on "
         "THIS INSTRUMENT'S WRITE instead of the solver's",
         all(real["recovery"][a]["repair"]["mtime_preserved"] for a in REPAIRED_ARMS))
    unit("U10 REBIND AUDIT (AV2R): the set of rebound callables is EXACTLY the empty set -- the "
         "frozen grader ran COMPLETELY UNMODIFIED, so every band, threshold, planted control "
         "and composition rule that decided this verdict is the frozen code, unedited on disk",
         real["names_rebound"] == [])
    unit("U11 AV2R's PRESERVED run root is byte-identical after the re-grade (%d regular files, "
         "md5 manifest before == after, read from the DISK and not from `git status`)"
         % real["preserved_root_files"], real["root_manifest_identical"])
    unit("U12 the verdict is from the FIXED vocabulary and is whatever the FROZEN instrument "
         "produced (got %r)" % real["verdict"], real["verdict"] in VOCAB)

    # ---- MUST-FLAG: absence must never be laundered into a pass ------------------------
    b_all = regrade("AV2R", tmp, mutate=plant_drop_all("AV2R", "X-S"), tag="drop_all")
    # AMENDMENT 2, §2d.1 repair.  ASSERTED IN v1.1: `"gmresRelTol_source_absent" in refusal`.
    # THAT STRING CANNOT BE RAISED ON THIS PATH: with the identity record removed,
    # `source_runtime` reaches its `len(ids) != 1` branch and refuses with
    # `gmresRelTol_runtime_identity_records` BEFORE it can reach the `v is None` branch that
    # names `gmresRelTol_source_absent`.  The reader was right; the unit was wrong about the
    # reader.  The corrected assertion names the clause the code ACTUALLY raises and is
    # therefore STRICTER, not weaker -- and U27 DRIVES it failing rather than claiming it.
    unit("U13 MUST-FLAG: ALL THREE sources removed from X-S -> still REFUSED, and the verdict "
         "is NOT A RESULT. A repaired reader that cannot still refuse is not repaired, it is "
         "disabled. The recovery SHORT-CIRCUITS on the FIRST source it cannot read, so with "
         "all three gone the clause raised is the RUNTIME one -- stated plainly rather than "
         "papered over (clause %r)" % refusal_clause(b_all),
         b_all["verdict"] == "NOT A RESULT"
         and "gmresRelTol_runtime_identity_records" in (b_all["refusal"] or ""))
    b_r = regrade("AV2R", tmp, mutate=plant_drop_runtime("AV2R", "X-S"), tag="drop_runtime")
    unit("U14 MUST-FLAG: source R alone removed -> REFUSED. THERE IS NO TWO-OF-THREE VOTE: a "
         "missing source means the tolerance the adjoint solve ran at is unknown, and an "
         "unknown tolerance is not a band (clause %r)" % refusal_clause(b_r),
         # AMENDMENT 2, §2d.1 repair.  ASSERTED IN v1.1: `"RUNTIME" in refusal` -- which is
         # additionally the WRONG CASE: the key the code emits carries lowercase `runtime`
         # inside `gmresRelTol_runtime_identity_records`.  U28 drives the correction failing.
         b_r["verdict"] == "NOT A RESULT"
         and "gmresRelTol_runtime_identity_records" in (b_r["refusal"] or ""))
    b_c = regrade("AV2R", tmp, mutate=plant_drop_container("X-S"), tag="drop_container")
    unit("U15 MUST-FLAG: source C alone removed (the DAOption echo stripped from the log copy) "
         "-> REFUSED, proving the log is genuinely read and is not decoration (clause %r)"
         % refusal_clause(b_c),
         b_c["verdict"] == "NOT A RESULT" and "CONTAINER" in (b_c["refusal"] or ""))
    b_f = regrade("AV2R", tmp, mutate=plant_drop_frozen("AV2R", "X-S"), tag="drop_frozen")
    unit("U16 MUST-FLAG: source F alone removed -> REFUSED (clause %r)" % refusal_clause(b_f),
         b_f["verdict"] == "NOT A RESULT" and "FROZEN" in (b_f["refusal"] or ""))
    b_d = regrade("AV2R", tmp, mutate=plant_disagree("AV2R", "X-S", 1.0e-5), tag="disagree")
    unit("U17 MUST-FLAG: 1e-5 planted into source R ALONE -> REFUSED on "
         "`gmresRelTol_sources_disagree` with all three values printed. This is what proves "
         "all three sources are read rather than one being trusted and two decorated "
         "(clause %r)" % refusal_clause(b_d),
         b_d["verdict"] == "NOT A RESULT"
         and "gmresRelTol_sources_disagree" in (b_d["refusal"] or ""))
    b_m = regrade("AV2R", tmp, mutate=plant_break_frozen_md5("AV2R", "X-S"), tag="break_md5")
    unit("U18 MUST-FLAG: one byte appended to X-S's runScript -> REFUSED on "
         "`gmresRelTol_runscript_md5_moved` BEFORE any value is parsed. The pin is taken from "
         "the FROZEN PRODUCER'S OWN constant, so the successor cannot silently read a "
         "different runScript (clause %r)" % refusal_clause(b_m),
         b_m["verdict"] == "NOT A RESULT"
         and "gmresRelTol_runscript_md5_moved" in (b_m["refusal"] or ""))

    # ---- MUST-FLAG: a WRONG BUT PRESENT tolerance must not become a PASS ---------------
    b_w = regrade("AV2R", tmp, post_repair=plant_wrong_tolerance_after_repair("AV2R", "X-S", 1.0e-5),
                  tag="wrong_tol")
    unit("U19 MUST-FLAG, THE LAUNDERING TEST: a wrong-but-PRESENT tolerance (1e-5) planted into "
         "the repaired artefact -> THE FROZEN GRADER'S OWN CLAUSE `av2r_grade.py:511-513` "
         "fires, `gmresRelTol_in_artefact` reads 1e-05 and the verdict is NOT A RESULT. The "
         "repair restores the field; it does not weaken the check the field feeds (clause %r)"
         % refusal_clause(b_w),
         b_w["verdict"] == "NOT A RESULT" and "gmresRelTol_in_artefact" in (b_w["refusal"] or ""))

    # ---- MUST-FLAG: the AGE GUARD must still be able to fire after the repair ----------
    b_a = regrade("AV2R", tmp, post_repair=plant_artefact_older_than_datum("AV2R", "X-S"),
                  tag="age_older")
    unit("U20 MUST-FLAG, THE AGE GUARD SURVIVES THE REPAIR: the repaired artefact back-dated "
         "BEFORE its arm's launch datum -> the FROZEN grader still refuses "
         "`artefact_not_newer_than_datum`. Had the repair stamped a fresh mtime this rule-4 "
         "PHYSICS guard would have been silently satisfied by this instrument's own write, on "
         "every arm, for ever (clause %r)" % refusal_clause(b_a),
         b_a["verdict"] == "NOT A RESULT"
         and "artefact_not_newer_than_datum" in (b_a["refusal"] or ""))

    # ---- MUST-FLAG: the gate must still be able to fail on a repaired case -------------
    b_g = regrade("AV2R", tmp,
                  post_repair=plant_reverse_total_out_of_band("AV2R", "X-S", "CD", "shape", 3, 2.0),
                  tag="out_of_band")
    unit("U21 MUST-FLAG: with the repair applied, one registered reverse total (CD/shape[3]) "
         "DOUBLED -- five orders outside the frozen band 1.0e-5 -- the item does NOT read PASS. "
         "REGISTERED CONDITIONAL: `GATE FAIL` (or a refusal on that component) if the SHIPPED "
         "forward row returns MEASURED components, `BLOCKED` if that row is blocked; what is "
         "forbidden is PASS. Branch taken: verdict %r, clause %r"
         % (b_g["verdict"], refusal_clause(b_g)),
         b_g["verdict"] != "PASS" and b_g["verdict"] in VOCAB)

    # ---- AV2: BOTH repairs, and the proof that it needs both ---------------------------
    a2g = regrade("AV2", tmp, repairs=("GMRES",), tag="gmres_only")
    unit("U22 AV2 WITH THE GMRES REPAIR ALONE still returns NOT A RESULT, and on a DIFFERENT "
         "clause -- the `writeCompression` datum variant. **AV2 CARRIES BOTH DEFECTS**, so a "
         "gmres-only repair moves it from one NOT A RESULT to another, and this unit is what "
         "proves that rather than asserting it (clause %r)" % refusal_clause(a2g),
         a2g["verdict"] == "NOT A RESULT" and "age_reference" in (a2g["refusal"] or "")
         and "gmresRelTol" not in (a2g["refusal"] or ""))
    a2b = regrade("AV2", tmp, tag="both")
    unit("U23 AV2 WITH BOTH REPAIRS: the original `G1 age_reference_absent` on `X-S/0/U` is GONE "
         "and no refusal names `gmresRelTol` either -- the datum resolves to the compressed "
         "twin and the recovered tolerance is in place (clause %r)" % refusal_clause(a2b),
         "age_reference_absent" not in (a2b["refusal"] or "")
         and "gmresRelTol" not in (a2b["refusal"] or ""))
    unit("U24 AV2 REBOUND EXACTLY `arm_datum`, AVWC's registered name, and the resolver IS "
         "AVWC's own code imported and md5-verified (%s) -- NOT a second implementation of a "
         "repair this family has already paid for once" % AVWC_READER_MD5[:8],
         a2b["names_rebound"] == ["arm_datum"] and a2b["datum_resolution"] is not None)
    a2w = regrade("AV2", tmp, post_repair=plant_wrong_tolerance_after_repair("AV2", "X-S", 1.0e-5),
                  tag="wrong_tol")
    unit("U25 MUST-FLAG on AV2 TOO, the laundering test is not inherited: a wrong-but-present "
         "1e-5 in the repaired artefact -> AV2's OWN frozen clause `av2_grade.py:442-443` fires "
         "and the verdict is NOT A RESULT (clause %r)" % refusal_clause(a2w),
         a2w["verdict"] == "NOT A RESULT" and "gmresRelTol_in_artefact" in (a2w["refusal"] or ""))

    # ---- CONDITION C of the §2d.1 ruling: the CORRECTED assertions are DRIVEN, not claimed --
    c13, c13r, o13 = _corrected_unit_can_fail(tmp, plant_drop_all("AV2R", "X-S"), "drive_u13")
    unit("U27 CONDITION C for U13: with `source_runtime` STUBBED so the reader does NOT refuse "
         "on the very plant U13 tests, U13's CORRECTED condition reads FALSE -- so the "
         "corrected assertion CAN still fail and is not merely matching whatever the code "
         "happens to emit. The stub is restored and the restoration is itself checked. A "
         "post-compute assertion change that cannot be shown able to fail is not a repair, it "
         "is a rubber stamp",
         c13 and c13r)
    c14, c14r, o14 = _corrected_unit_can_fail(tmp, plant_drop_runtime("AV2R", "X-S"), "drive_u14")
    unit("U28 CONDITION C for U14: same drive on the single-source plant -- stubbed, the "
         "corrected condition reads FALSE; restored, U14 passes on the real path above",
         c14 and c14r)

    every = (real, b_all, b_r, b_c, b_f, b_d, b_m, b_w, b_a, b_g, a2g, a2b, a2w, o13, o14)
    unit("U26 every plant ran on a COPY: BOTH preserved run roots are byte-identical after all "
         "%d re-grades in this selftest" % len(every),
         all(x["root_manifest_identical"] for x in every))

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
    ap.add_argument("--item", default=None, choices=sorted(ITEMS))
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
    items = [a.item] if a.item else sorted(ITEMS)
    res = {}
    for it in items:
        try:
            r = regrade(it, d, tag="real")
        except Refusal as ex:
            r = {"item": it, "verdict": "NOT A RESULT", "successor_refusal": str(ex)}
        r.pop("grade", None)
        res[it] = r
        print("%-5s  ORIGINAL: NOT A RESULT (%s)" % (it, ITEMS[it]["original_refusal"]))
        print("       RE-GRADED: %s   repairs=%s   rebound=%s   preserved_root_identical=%s"
              % (r.get("verdict"), r.get("repairs_applied"), r.get("names_rebound"),
                 r.get("root_manifest_identical")))
        if r.get("refusal"):
            print("       refusal clause: %s" % refusal_clause(r))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
