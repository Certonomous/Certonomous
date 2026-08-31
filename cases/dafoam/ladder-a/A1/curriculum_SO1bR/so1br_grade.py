#!/usr/bin/env python3
"""SO-1bR COMPARATOR -- THE SUCCESSOR TO SO-1b.  IT RE-IMPLEMENTS NO GATE.

SO-1b did not launch.  Its frozen chain driver evaluated its dependency on SO-1a
before creating any run root, read `REFUSE no_gates.G5_PATCHED`, and closed the item
at rc = 7 with ZERO core-minutes spent -- which is the no-launch branch WORKING, not
failing.  What changed since is that SO-1a's successor SO-1aR produced a grade
artefact that DOES carry `gates.G5_PATCHED`, reading PASS on both gradients.  The
precondition is satisfied in SUBSTANCE and unsatisfiable in FORM, because the frozen
glob `SO1a_grade_*.json` cannot match `SO1aR_grade_*.json`.

SO-1bR is that repair, taken as a NEW REGISTERED INPUT rather than a renamed old one.
See `so1br_precondition.py` for why the rename is forbidden and for G-PROV.

======================= HOW THIS COMPARATOR RELATES TO SO-1b's =======================
It imports SO-1b's OWN FROZEN COMPARATOR, proves the file on disk is byte-identical to
the committed blob, REBINDS EXACTLY ONE NAME, and runs THE FROZEN `grade()`.  Every
band, threshold, composition rule, planted control and refusal clause that decides a
verdict is LITERALLY THE FROZEN CODE, UNEDITED ON DISK.  Nothing here re-derives
`FD_BAND_PCT`, `AGG_BAND_PCT`, `PLATEAU_TOL_PCT`, `MIN_GRADED`, `TB_MAX_PASSING`,
`COMPONENTS_REGISTERED`, `STEPS_REGISTERED`, `CAPS` or any prediction band, and a unit
CHECKS that they did not move across the rebind rather than promising it.

THE REBIND IS AUDITED, NOT ASSERTED.  Every callable in the imported module is
fingerprinted before and after; the set of names whose identity moved must be EXACTLY
the registered set or the run REFUSES.  Refusals are raised through THE FROZEN
MODULE'S OWN `refuse()`, so a refusal from the repaired path is shaped exactly like
the refusal that instrument would itself have raised.

=================== THE ONE REBIND: C5, THE trapFpe FALSE POSITIVE ===================
MEASURED, NOT SUSPECTED.  `so1b_grade.py:131-133` lists `"Floating point exception"`
in `FATAL_TOKENS`, and `so1b_grade.py:420-423` tests it with a WHOLE-FILE SUBSTRING
scan (`t in text`).  `so1b_grade.py:490` builds the C5 haystack for a SCRIPT arm as
the arm log PLUS the artefact, and the MESH arm's artefact is `checkMesh.log`.
OpenFOAM's own startup banner reads

    trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).

and it stands at line 18 of SO-1a's `MESH/checkMesh.log` on the preserved run root
(md5 `22aa9cfa6725eb904123aefaebf63cfd`).  SO-1b's MESH arm runs the same `checkMesh`
on the same tutorial, so the frozen C5 clause would refuse SO-1bR's MESH arm on a
SAFETY NOTICE -- a CERTAIN refusal, not a possible one.  SO-1a paid for exactly this:
five clean arms and 9.416 core-min of intact physics returned NOT A RESULT.

THE REPAIR IS ADOPTED, NOT REINVENTED, from `curriculum_SO1aR/so1ar_grade.py`
(`REAL_BANNER_LINE` at :285, the reasoning at :192-231, `fatal_token_sites` at :498).
Its three load-bearing properties are preserved and each is DRIVEN below:

  * THE TOKEN STAYS.  What is removed is the WHOLE-FILE SUBSTRING SCAN, never the
    token.  Deleting `"Floating point exception"` would be the blinding this repair
    must not do.
  * PER LINE, WITH A NARROW BENIGN EXCLUSION.  A benign banner on line 18 can never
    suppress a real crash on line 400, and that is driven.
  * ANCHORING WITH `^` IS NOT THE FIX AND IS DELIBERATELY NOT ADOPTED.  OpenMPI's real
    crash report reads `mpirun noticed that process rank 2 exited on signal 8
    (Floating point exception).` -- NOT line-initial and carrying no handler symbol.
    `^Floating point exception` would MISS it.  An over-narrow EXCLUSION costs a FALSE
    REFUSAL; an over-narrow POSITIVE ANCHOR costs a MISSED CRASH, and the false
    refusal is the survivable error.
  * `Foam::sigFpe::sigHandler` is added as an EXTRA POSITIVE token (adopted from
    `so1ar_grade.py:202`, itself from `sdk/chief_engineer/head_engineer.py:188`).  It
    STRENGTHENS detection and never weakens it.

The frozen `FATAL_TOKENS` TUPLE IS NOT REBOUND.  The repaired closure reads the frozen
tuple from the module and adds the extra positive token locally, so the frozen
constant table is provably untouched and the rebound name count stays at ONE.

========================= WHAT THIS FILE DOES NOT DO =========================
It does NOT launch anything.  `grade_root()` is the Stage-2 entry point and refuses
when the run root is absent, which it is at this freeze.  Stage 2 -- the derived chain
driver and arm launcher -- is NOT frozen by this document and is NOT claimed done;
see PREREGISTRATION.md section 12.

L-332: NO `assert` anywhere; the module counts `ast.Assert` nodes in its own source
and in `so1br_precondition.py` and refuses on any, so `python3 -O` cannot strip a
check.  No unconditional success print.
"""

import sys

# ABOVE ANY OTHER IMPORT (see so1br_precondition.py for the measured reason).
sys.dont_write_bytecode = True

import ast              # noqa: E402
import hashlib          # noqa: E402
import importlib.util   # noqa: E402
import json             # noqa: E402
import os               # noqa: E402
import re               # noqa: E402
import shutil           # noqa: E402
import tempfile         # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = os.path.dirname(HERE)
REPO = "/home/ubuntu/Certonomous"

sys.path.insert(0, HERE)
import so1br_precondition as P                                        # noqa: E402

ITEM = "SO1bR"

# ---- THE FROZEN PREDECESSOR, PINNED THREE WAYS -------------------------------------
FROZEN_GRADER = os.path.join(A1, "curriculum_SO1b", "so1b_grade.py")
FROZEN_GRADER_REL = "cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_grade.py"
FROZEN_GRADER_MD5 = "88157ca3c04798750e97b87ca3d02a15"
FROZEN_GRADER_BLOB = "f7ba5f7b5d405f8d4d6dbc82bb538397ac8dff09"

# ---- THE REGISTERED REBIND SET.  EXACTLY ONE NAME. ----------------------------------
REGISTERED_REBIND = ("fatal_tokens_in",)

# The frozen module's gate-deciding constants.  A unit reads each BEFORE and AFTER the
# rebind and refuses on any movement -- the claim "this successor re-implements no
# band" is CHECKED rather than promised.
FROZEN_CONSTANTS_WATCHED = (
    "FATAL_TOKENS", "FD_BAND_PCT", "AGG_BAND_PCT", "PLATEAU_TOL_PCT", "MIN_GRADED",
    "NEAR_ZERO_ABS", "TB_MAX_PASSING", "TB_STEPS_REGISTERED", "COMPONENTS_REGISTERED",
    "STEPS_REGISTERED", "CAPS", "ITEM_CEILING_CORE_MIN", "CELLS_EXPECTED", "PRED",
    "CL_TARGET", "CL_RESIDUAL_MAX", "GEO_BOUNDS", "GEO_ROWS_EXPECTED",
    "MAX_ITER_REGISTERED", "OPTIMIZER_REGISTERED", "IMG_DIGEST", "SO_MD5",
    "CPUSET_REGISTERED", "VOCAB", "EXPECTED_UNITS")

# ---- THE C5 REPAIR, ADOPTED FROM curriculum_SO1aR/so1ar_grade.py --------------------
# ADOPTED as an EXTRA POSITIVE token (so1ar_grade.py:202).  Strengthens; never weakens.
EXTRA_POSITIVE_TOKENS = ("Foam::sigFpe::sigHandler",)
# The ONLY suppression this comparator carries, adopted verbatim (so1ar_grade.py:228-232).
BENIGN_LINE_PATTERNS = (
    (r"^\s*trapFpe:\s",
     "OpenFOAM sigFpe SETUP banner -- an ENABLEMENT NOTICE, not a crash"),
)
BENIGN_LINE_RE = tuple((re.compile(_p), _why) for _p, _why in BENIGN_LINE_PATTERNS)

# ---- REAL BYTES, READ FROM A PRESERVED RUN ROOT, NEVER INVENTED ---------------------
# The C5 repair is proven on REAL LOG BYTES.  This is SO-1a's OWN `MESH/checkMesh.log`
# on its preserved root; the ONE LINE at :18 is what returned NOT A RESULT on five
# clean arms.  SO-1aR froze a byte-identical fixture beside its own comparator, so the
# same bytes are available on TWO independent channels and a unit checks they agree.
REAL_CHECKMESH = ("/home/ubuntu/certonomous-runs/"
                  "CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/MESH/checkMesh.log")
REAL_CHECKMESH_MD5 = "22aa9cfa6725eb904123aefaebf63cfd"
SO1AR_FIXTURE_CHECKMESH = os.path.join(A1, "curriculum_SO1aR",
                                       "so1ar_fixture_REAL_SO1a_MESH_checkMesh.log")
REAL_BANNER_LINE = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)."
REAL_BANNER_LINE_NO = 18
# A REALISTIC OpenMPI crash report.  PLANTED, NOT CAPTURED -- said plainly, because a
# planted line described as captured would be exactly the dishonesty this lab exists to
# stop.  Its SHAPE is adopted from `so1ar_grade.py:1702-1706`, and its shape is the
# whole point: it is NOT line-initial, so `^Floating point exception` would MISS it.
PLANTED_MPI_CRASH_LINE = ("mpirun noticed that process rank 2 exited on signal 8 "
                          "(Floating point exception).")
PLANTED_SIGFPE_STACK_LINE = "#3  Foam::sigFpe::sigHandler(int) at ??:?"

# ---- THE FORWARD-AD QUESTION, ANSWERED BY MEASUREMENT ------------------------------
# AV2RG measured that DAFoam's FORWARD-AD PRIMAL DOES NOT CONVERGE on this case at
# these settings -- 20 FAD readings, zero graded, item BLOCKED.  If SO-1bR depended
# anywhere on a forward-AD reference it would BLOCK the same way, so the dependency is
# CHECKED HERE rather than reasoned about.  The tokens are the ones a forward-AD path
# would have to name; the derivative mode is read from the instruments themselves.
FORWARD_AD_TOKENS = ("forwardAD", "useAD", "adMode", "runMode", "complexify",
                     "dFdWSeed", "seedVec", "mode=\"fwd\"", "mode='fwd'")
AD_SCANNED_FILES = ("so1b_of.py", "so1b_runScript.py", "so1b_grade.py",
                    "so1b_run_arm.sh", "so1b_chain_driver.sh")
REQUIRED_DERIVATIVE_MODE = 'prob.setup(mode="rev")'

VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# FROZEN BEFORE EXECUTION (PREREGISTRATION.md section 8).  47 units.
EXPECTED_UNITS = 47

# Sites recorded by the repaired predicate, for the record rather than for the gate.
SITES = {"fatal": [], "benign": []}


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read()))
               if isinstance(n, ast.Assert))


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path):
    """The git blob sha of the file ON DISK, computed locally.  Compared against
    `git rev-parse HEAD:<path>` this answers rule 2's question -- is the frozen file
    the file that ran -- without trusting a second tool to hash it the same way."""
    data = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def manifest(root):
    """md5 of every regular file under `root`, keyed by relative path.  IT READS THE
    DISK, NOT GIT: a run root is not in git, so a git-based cleanliness check is blind
    to exactly the thing being protected."""
    out = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            p = os.path.join(dirpath, name)
            if os.path.isfile(p) and not os.path.islink(p):
                out[os.path.relpath(p, root)] = md5_file(p)
    return out


# ================= the frozen predecessor =============================================
def load_frozen():
    """Import SO-1b's frozen comparator AFTER proving the file on disk is the file that
    was frozen -- by md5 AND by git blob sha.  Bytecode writing is already disabled at
    the top of this module, so importing a frozen case's comparator cannot drop a
    `__pycache__` into its directory and no stale bytecode can invert a unit."""
    if not os.path.isfile(FROZEN_GRADER):
        refuse("FROZEN_GRADER_ABSENT", {"path": FROZEN_GRADER})
    got = md5_file(FROZEN_GRADER)
    if got != FROZEN_GRADER_MD5:
        refuse("FROZEN_GRADER_MD5", {"path": FROZEN_GRADER,
                                     "registered": FROZEN_GRADER_MD5, "on_disk": got})
    blob = git_blob_sha(FROZEN_GRADER)
    if blob != FROZEN_GRADER_BLOB:
        refuse("FROZEN_GRADER_BLOB", {"path": FROZEN_GRADER,
                                      "registered": FROZEN_GRADER_BLOB, "on_disk": blob,
                                      "note": "rule 2: the frozen file must BE the file "
                                              "that was committed"})
    name = "so1br_frozen_so1b"
    spec = importlib.util.spec_from_file_location(name, FROZEN_GRADER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _fingerprint(mod):
    return {k: id(v) for k, v in vars(mod).items() if callable(v)}


def _constants(mod):
    return {k: repr(getattr(mod, k, None)) for k in FROZEN_CONSTANTS_WATCHED}


def benign_reason(line):
    """Why this ONE LINE is an enablement notice and not a crash, or None.  Narrow by
    construction: see BENIGN_LINE_PATTERNS."""
    for rx, why in BENIGN_LINE_RE:
        if rx.search(line):
            return why
    return None


def fatal_token_sites(text, source, tokens):
    """C5, REPAIRED.  Scans LINE BY LINE and PER SOURCE FILE, returning (sites, benign).

    LINE BY LINE, because the token test must be able to tell a CRASH from an
    ENABLEMENT NOTICE and a whole-file substring test cannot -- that is precisely what
    returned NOT A RESULT on SO-1a's five clean arms.  Every token is a single-line
    string, so splitting loses no match, and that is DRIVEN rather than asserted: one
    unit plants each token in turn and requires a hit for every one."""
    sites, benign = [], []
    for i, line in enumerate(text.splitlines(), 1):
        hit = [t for t in tokens if t in line]
        if not hit:
            continue
        why = benign_reason(line)
        rec = {"file": source, "line": i, "tokens": hit, "text": line.strip()[:200]}
        if why:
            rec["why_benign"] = why
            benign.append(rec)
        else:
            sites.append(rec)
    return sites, benign


def make_repaired_fatal_tokens_in(mod, source_hint="arm_output"):
    """THE ONE REBIND.  Same name, same signature and same RETURN TYPE as the frozen
    `fatal_tokens_in`, so the frozen `g_completion`'s C5 refusal clause -- its
    condition, its message and its verdict -- is untouched and still decides.

    The token set is the FROZEN module's own `FATAL_TOKENS` plus the adopted extra
    positive tokens.  The frozen tuple itself is NOT rebound."""
    tokens = tuple(mod.FATAL_TOKENS) + EXTRA_POSITIVE_TOKENS

    def fatal_tokens_in(text):
        sites, benign = fatal_token_sites(text, source_hint, tokens)
        SITES["fatal"].extend(sites)
        SITES["benign"].extend(benign)
        out = []
        for rec in sites:
            for t in rec["tokens"]:
                if t not in out:
                    out.append(t)
        return out
    return fatal_tokens_in


def adopt(mod):
    """Rebind the registered names and AUDIT the rebind.  REFUSES if the set of names
    whose identity moved is not EXACTLY the registered set."""
    fp0, c0 = _fingerprint(mod), _constants(mod)
    mod.fatal_tokens_in = make_repaired_fatal_tokens_in(mod)
    fp1, c1 = _fingerprint(mod), _constants(mod)
    rebound = tuple(sorted(k for k in set(fp0) | set(fp1) if fp0.get(k) != fp1.get(k)))
    if rebound != REGISTERED_REBIND:
        refuse("REBIND_AUDIT", {"expected": list(REGISTERED_REBIND),
                                "actual": list(rebound),
                                "note": "the successor replaces exactly the registered "
                                        "names and no others; everything else that "
                                        "decides the verdict is the frozen code"})
    moved = sorted(k for k in c0 if c0[k] != c1.get(k))
    if moved:
        refuse("FROZEN_CONSTANTS_MOVED", {"moved": moved,
                                          "note": "no band, threshold, cap, component "
                                                  "set or prediction may move across "
                                                  "the rebind"})
    return {"names_rebound": list(rebound), "constants_checked": len(c0),
            "constants_moved": moved}


# ================= G-PROV: nothing leaves without its provenance ======================
def emit(out, prov, refuser=None):
    """The ONLY exit from this comparator.  Attaches the upstream provenance block and
    the composed `verdict_line`, then puts the whole object through
    `require_travelling_provenance()`, which REFUSES rather than emit a verdict whose
    upstream `GATE FAIL` did not travel with it."""
    out = dict(out)
    out["upstream_provenance"] = prov
    out["verdict_line"] = P.compose_verdict_line(out.get("verdict"), prov)
    return P.require_travelling_provenance(out, refuse=refuser)


# ================= Stage 2 entry point (refuses at this freeze) =======================
def grade_root(root, workdir=None, mutate=None):
    """Run the FROZEN `grade()` on a `cp -a` COPY of a preserved run root, with an md5
    manifest taken before and after and a REFUSAL on any movement.

    AT THIS FREEZE THERE IS NO SO-1bR RUN ROOT, so every call refuses on
    `PRESERVED_ROOT_ABSENT`.  That is the correct behaviour and it is driven as a unit:
    a Stage-2 entry point that silently produced something with no root would be worse
    than one that refuses."""
    if not os.path.isdir(root):
        refuse("PRESERVED_ROOT_ABSENT", {"root": root,
                                         "note": "Stage 2 is not frozen by this document; "
                                                 "see PREREGISTRATION.md section 12"})
    before = manifest(root)
    tmp = workdir or tempfile.mkdtemp(prefix="so1br_")
    copy_root = os.path.join(tmp, "root_copy")
    if os.path.isdir(copy_root):
        shutil.rmtree(copy_root)
    shutil.copytree(root, copy_root, symlinks=True)
    for junk in ("__pycache__",):
        p = os.path.join(copy_root, junk)
        if os.path.isdir(p):
            shutil.rmtree(p)
    if mutate:
        mutate(copy_root)
    mod = load_frozen()
    audit = adopt(mod)
    pre = P.evaluate(refuse=mod.refuse)
    if pre["G_SO1AR"]["decision"] != "PROCEED":
        refuse("G-SO1AR", {"decision": pre["G_SO1AR"]["decision"], "reading": pre["G_SO1AR"]})
    out = {"item": "CURRICULUM-%s" % ITEM, "frozen_grader": FROZEN_GRADER,
           "frozen_grader_md5": FROZEN_GRADER_MD5, "rebind_audit": audit,
           "G_SO1AR": pre["G_SO1AR"]}
    try:
        r = mod.grade(copy_root)
        out["verdict"] = r.get("verdict")
        out["grade"] = r
        out["refusal"] = None
    except Exception as ex:                                           # noqa: BLE001
        if type(ex).__name__ != "Refusal":
            raise
        out["verdict"] = "NOT A RESULT"
        out["grade"] = None
        out["refusal"] = str(ex)
    out["c5_sites"] = {"fatal": SITES["fatal"], "benign": SITES["benign"]}
    after = manifest(root)
    movedp = sorted(set(before) ^ set(after)) + sorted(
        k for k in before if k in after and before[k] != after[k])
    if movedp:
        refuse("PRESERVED_ROOT_MUTATED", {"paths": movedp[:50], "root": root})
    out["preserved_root_manifest_files"] = len(before)
    return emit(out, pre["upstream_provenance"], refuser=mod.refuse)


# ================= SELFTEST ===========================================================
def _u(results, name, ok, detail=""):
    results.append({"unit": name, "ok": bool(ok), "detail": detail})
    print("  %-4s %-58s %s" % ("PASS" if ok else "FAIL", name, detail))


def _raises(fn, where_substr=None):
    """Run `fn`; return (True, message) if it raised a Refusal (either module's),
    optionally requiring the message to name a clause."""
    try:
        fn()
    except Exception as ex:                                           # noqa: BLE001
        if type(ex).__name__ != "Refusal":
            return False, "raised %s, not Refusal: %r" % (type(ex).__name__, ex)
        msg = str(ex)
        if where_substr and where_substr not in msg:
            return False, "refused, but not on %r: %s" % (where_substr, msg[:200])
        return True, msg
    return False, "DID NOT REFUSE"


def _mutated_input(tmp, mutate):
    """Write a MUTATED COPY of the registered input into scratch and return its path
    and md5.  THE PRESERVED ROOT IS NEVER WRITTEN."""
    G = json.load(open(P.REGISTERED_INPUT))
    mutate(G)
    path = os.path.join(tmp, "mutated_%d.json" % len(os.listdir(tmp)))
    with open(path, "w") as fh:
        json.dump(G, fh, sort_keys=True)
    return path, md5_file(path)


def selftest():
    results = []
    tmp = tempfile.mkdtemp(prefix="so1br_selftest_")
    print("SO1bR SELFTEST -- optimized=%s  scratch=%s" % (not __debug__, tmp))

    # ---------------- G-SO1AR: the registered input ----------------------------------
    print("\n[G-SO1AR] the registered input")
    _u(results, "U01_input_exists", os.path.isfile(P.REGISTERED_INPUT), P.REGISTERED_INPUT)
    got = md5_file(P.REGISTERED_INPUT) if os.path.isfile(P.REGISTERED_INPUT) else None
    _u(results, "U02_input_md5_matches_registered",
       got == P.REGISTERED_INPUT_MD5, "md5=%s" % got)

    G = json.load(open(P.REGISTERED_INPUT))
    src = os.path.basename(P.REGISTERED_INPUT)
    pre = P.precondition(G, src)
    _u(results, "U03_real_input_decision_PROCEED",
       pre["decision"] == "PROCEED", "decision=%s" % pre["decision"])
    _u(results, "U04_two_channels_agree",
       pre["row_PATCHED_gate_channel"] == pre["row_PATCHED_top_channel"] == "PASS",
       "gate=%s top=%s" % (pre["row_PATCHED_gate_channel"], pre["row_PATCHED_top_channel"]))
    _u(results, "U05_patched_G5_and_G5c_both_PASS",
       pre["G5_CD_PATCHED"] == "PASS" and pre["G5c_CL_PATCHED"] == "PASS",
       "G5_CD=%s G5c_CL=%s" % (pre["G5_CD_PATCHED"], pre["G5c_CL_PATCHED"]))

    ok, msg = _raises(lambda: P.read_registered_input(os.path.join(tmp, "nope.json")),
                      "registered_input_absent")
    _u(results, "U06_MUSTFLAG_input_absent_refuses", ok, msg[:90])

    bad = os.path.join(tmp, "md5moved.json")
    shutil.copyfile(P.REGISTERED_INPUT, bad)
    with open(bad, "a") as fh:
        fh.write("\n")
    ok, msg = _raises(lambda: P.read_registered_input(bad), "registered_input_md5_moved")
    _u(results, "U07_MUSTFLAG_input_md5_moved_refuses", ok, msg[:90])

    def _drop_gp(g):
        g["gates"].pop("G5_PATCHED", None)
    p8, m8 = _mutated_input(tmp, _drop_gp)
    ok, msg = _raises(lambda: P.precondition(json.load(open(p8)), "u08"),
                      "no_gates.G5_PATCHED")
    _u(results, "U08_MUSTFLAG_gates_G5_PATCHED_absent_refuses", ok,
       "the exact shape that closed SO-1b")

    def _drop_rowp(g):
        g["rows"].pop("PATCHED", None)
    p9, _ = _mutated_input(tmp, _drop_rowp)
    ok, msg = _raises(lambda: P.precondition(json.load(open(p9)), "u09"),
                      "rows.PATCHED_absent")
    _u(results, "U09_MUSTFLAG_rows_PATCHED_absent_refuses", ok, msg[:90])

    def _disagree(g):
        g["rows"]["PATCHED"] = "GATE FAIL"
    p10, _ = _mutated_input(tmp, _disagree)
    ok, msg = _raises(lambda: P.precondition(json.load(open(p10)), "u10"),
                      "channel_disagreement")
    _u(results, "U10_MUSTFLAG_channel_disagreement_refuses", ok, msg[:90])

    def _wrong_cd(g):
        g["gates"]["G5_PATCHED"]["G5_CD"]["verdict"] = "GATE FAIL"
        g["gates"]["G5_PATCHED"]["row_verdict"] = "GATE FAIL"
        g["rows"]["PATCHED"] = "GATE FAIL"
    p11, _ = _mutated_input(tmp, _wrong_cd)
    r11 = P.precondition(json.load(open(p11)), "u11")
    _u(results, "U11_MUSTFLAG_wrong_but_present_G5_CD_no_launch",
       r11["decision"] == "REFUSE",
       "well-formed and WRONG -> decision=%s (a frozen clause fired, not a parse error)"
       % r11["decision"])

    def _wrong_cl(g):
        g["gates"]["G5_PATCHED"]["G5c_CL"]["verdict"] = "GATE FAIL"
        g["gates"]["G5_PATCHED"]["row_verdict"] = "GATE FAIL"
        g["rows"]["PATCHED"] = "GATE FAIL"
    p12, _ = _mutated_input(tmp, _wrong_cl)
    r12 = P.precondition(json.load(open(p12)), "u12")
    _u(results, "U12_MUSTFLAG_wrong_but_present_G5c_CL_no_launch",
       r12["decision"] == "REFUSE",
       "the CONSTRAINT gradient is graded as an equal -> decision=%s" % r12["decision"])

    junk = os.path.join(tmp, "junk.json")
    open(junk, "w").write("{not json")
    ok, msg = _raises(lambda: P.read_registered_input(junk, md5_file(junk)),
                      "registered_input_unreadable")
    _u(results, "U13_MUSTFLAG_input_unreadable_refuses", ok, msg[:90])

    seen = P.frozen_glob_can_see(P.REGISTERED_INPUT)
    _u(results, "U14_frozen_SO1b_glob_cannot_see_registered_input",
       seen["can_see_registered_input"] is False and len(seen["matches"]) >= 1,
       "pattern %s matched %s -- the ruling, executed"
       % (seen["pattern"], seen["matches"]))

    # ---------------- G-PROV: the travelling shipped GATE FAIL -----------------------
    print("\n[G-PROV] the travelling shipped GATE FAIL")
    prov = P.shipped_provenance(G, src)
    _u(results, "U15_shipped_row_status_is_GATE_FAIL",
       prov["rows"]["SHIPPED"] == "GATE FAIL",
       "rows.SHIPPED=%r rows.PATCHED=%r" % (prov["rows"]["SHIPPED"], prov["rows"]["PATCHED"]))

    cd = prov["G5_SHIPPED"]["G5_CD"]
    _u(results, "U16_shipped_G5_CD_detail_travels",
       cd["verdict"] == "GATE FAIL" and cd["n_pass"] == 3 and cd["n_graded"] == 5
       and cd["sign_flips"] == 1 and abs(float(cd["aggregate_rel_err_pct"]) - 40.481353490548585) < 1e-9,
       "GATE FAIL %d/%d agg %.6f%% sign_flips=%d"
       % (cd["n_pass"], cd["n_graded"], float(cd["aggregate_rel_err_pct"]), cd["sign_flips"]))

    cl = prov["G5_SHIPPED"]["G5c_CL"]
    _u(results, "U17_shipped_G5c_CL_detail_travels",
       cl["verdict"] == "GATE FAIL" and cl["n_pass"] == 4 and cl["n_graded"] == 5
       and cl["band_D"] == "GATE FAIL" and cl["band_E"] == "PASS"
       and abs(float(cl["aggregate_rel_err_pct"]) - 4.326953773474209) < 1e-9,
       "GATE FAIL %d/%d agg %.6f%% band_D=%s band_E=%s"
       % (cl["n_pass"], cl["n_graded"], float(cl["aggregate_rel_err_pct"]),
          cl["band_D"], cl["band_E"]))

    w = cd["worst_component"]
    _u(results, "U18_worst_component_shape6_travels_with_its_sign_flip",
       w["dv"] == "shape" and w["idx"] == 6 and w["sign_flip"] is True
       and abs(float(w["rel_err_pct"]) - 637.7570114398126) < 1e-9,
       "%s[%s] %.4f%% sign_flip=%s" % (w["dv"], w["idx"], float(w["rel_err_pct"]), w["sign_flip"]))

    line = P.compose_verdict_line("PASS", prov)
    _u(results, "U19_verdict_line_carries_the_literal_GATE_FAIL_bytes",
       P.PROVENANCE_TOKEN in line, "token present, %d bytes" % len(line.encode("utf-8")))

    def _strip_shipped_row(g):
        g["rows"].pop("SHIPPED", None)
    p20, _ = _mutated_input(tmp, _strip_shipped_row)
    ok, msg = _raises(lambda: P.shipped_provenance(json.load(open(p20)), "u20"),
                      "shipped_row_status_absent")
    _u(results, "U20_MUSTFLAG_shipped_row_stripped_refuses", ok, msg[:90])

    def _strip_shipped_gates(g):
        g["gates"].pop("G5_SHIPPED", None)
    p21, _ = _mutated_input(tmp, _strip_shipped_gates)
    ok, msg = _raises(lambda: P.shipped_provenance(json.load(open(p21)), "u21"),
                      "gates.G5_SHIPPED_absent")
    _u(results, "U21_MUSTFLAG_shipped_gate_detail_stripped_refuses", ok, msg[:90])

    def _launder_shipped(g):
        g["rows"]["SHIPPED"] = "PASS"
    p22, _ = _mutated_input(tmp, _launder_shipped)
    ok, msg = _raises(lambda: P.shipped_provenance(json.load(open(p22)), "u22"),
                      "shipped_row_status_not_the_registered_word")
    _u(results, "U22_MUSTFLAG_shipped_row_laundered_to_PASS_refuses", ok, msg[:90])

    ok, msg = _raises(lambda: P.require_travelling_provenance({"verdict": "PASS"}),
                      "verdict_without_upstream_provenance")
    _u(results, "U23_MUSTFLAG_emit_without_provenance_refuses", ok, msg[:90])

    broken = {"verdict": "PASS", "upstream_provenance": prov,
              "verdict_line": line.replace("GATE FAIL", "")}
    ok, msg = _raises(lambda: P.require_travelling_provenance(broken),
                      "provenance_token_lost_from_verdict_line")
    _u(results, "U24_MUSTFLAG_GATE_FAIL_token_lost_in_transit_refuses", ok,
       "the unquoted-heredoc shape (e779bdc7)")

    tampered = {"verdict": "PASS", "upstream_provenance": prov,
                "verdict_line": line + "  GATE FAIL"}
    ok, msg = _raises(lambda: P.require_travelling_provenance(tampered),
                      "verdict_line_bytes_differ_from_the_intended_bytes")
    _u(results, "U25_MUSTFLAG_verdict_line_bytes_differ_refuses", ok,
       "landed bytes compared against intended bytes (L-405)")

    good = {"verdict": "PASS", "upstream_provenance": prov, "verdict_line": line}
    back = P.require_travelling_provenance(good)
    _u(results, "U26_MUSTNOTFLAG_well_formed_emit_passes",
       back is good and back["verdict"] == "PASS", "verdict unchanged")

    ok, msg = _raises(lambda: P.require_travelling_provenance(
        {"verdict": "roughly converged", "upstream_provenance": prov,
         "verdict_line": line}), "verdict_outside_the_fixed_vocabulary")
    _u(results, "U27_MUSTFLAG_verdict_outside_fixed_vocabulary_refuses", ok, msg[:90])

    # ---------------- C5: the trapFpe repair on REAL bytes ----------------------------
    print("\n[G-C5R] the trapFpe repair, on REAL log bytes")
    have_real = os.path.isfile(REAL_CHECKMESH)
    real_md5 = md5_file(REAL_CHECKMESH) if have_real else None
    fix_md5 = md5_file(SO1AR_FIXTURE_CHECKMESH) if os.path.isfile(SO1AR_FIXTURE_CHECKMESH) else None
    _u(results, "U28_real_checkMesh_md5_and_SO1aR_fixture_agree",
       have_real and real_md5 == REAL_CHECKMESH_MD5 and fix_md5 == REAL_CHECKMESH_MD5,
       "preserved=%s fixture=%s" % (real_md5, fix_md5))

    real_text = open(REAL_CHECKMESH, errors="replace").read() if have_real else ""
    lines = real_text.splitlines()
    got_line = lines[REAL_BANNER_LINE_NO - 1] if len(lines) >= REAL_BANNER_LINE_NO else ""
    _u(results, "U29_real_banner_line_18_is_byte_identical",
       got_line.strip() == REAL_BANNER_LINE, "checkMesh.log:%d" % REAL_BANNER_LINE_NO)

    mod = load_frozen()
    frozen_hits = mod.fatal_tokens_in(real_text)
    _u(results, "U30_FROZEN_predicate_DOES_hit_the_real_banner",
       frozen_hits == ["Floating point exception"],
       "so1b_grade.py:420-423 on real bytes -> %s  THE DEFECT, EXECUTED" % frozen_hits)

    audit = adopt(mod)
    SITES["fatal"], SITES["benign"] = [], []
    rep_hits = mod.fatal_tokens_in(real_text)
    _u(results, "U31_REPAIRED_predicate_clears_the_real_banner",
       rep_hits == [] and len(SITES["benign"]) == 1 and not SITES["fatal"],
       "0 fatal sites, %d benign exclusion, token NOT deleted" % len(SITES["benign"]))

    SITES["fatal"], SITES["benign"] = [], []
    mpi_hits = mod.fatal_tokens_in("some preamble\n" + PLANTED_MPI_CRASH_LINE + "\n")
    _u(results, "U32_REPAIRED_predicate_flags_the_non_line_initial_MPI_crash",
       mpi_hits == ["Floating point exception"] and len(SITES["fatal"]) == 1,
       "a '^' anchor would MISS this; the exclusion form does not")

    SITES["fatal"], SITES["benign"] = [], []
    stk = mod.fatal_tokens_in(PLANTED_SIGFPE_STACK_LINE + "\n")
    _u(results, "U33_REPAIRED_predicate_flags_the_sigFpe_handler_symbol",
       "Foam::sigFpe::sigHandler" in stk,
       "extra positive token adopted from so1ar_grade.py:202")

    every = []
    for t in tuple(mod.FATAL_TOKENS) + EXTRA_POSITIVE_TOKENS:
        SITES["fatal"], SITES["benign"] = [], []
        every.append(t in mod.fatal_tokens_in("preamble line\nXX %s XX\ntail\n" % t))
    _u(results, "U34_every_token_still_fires_when_planted_on_its_own_line",
       all(every), "%d/%d tokens, none lost to the line split" % (sum(every), len(every)))

    SITES["fatal"], SITES["benign"] = [], []
    mixed = (REAL_BANNER_LINE + "\n") + ("filler\n" * 380) + PLANTED_MPI_CRASH_LINE + "\n"
    mix_hits = mod.fatal_tokens_in(mixed)
    _u(results, "U35_benign_line_1_does_not_suppress_a_real_crash_later",
       mix_hits == ["Floating point exception"] and len(SITES["fatal"]) == 1
       and len(SITES["benign"]) == 1 and SITES["fatal"][0]["line"] > 380,
       "benign at line 1, fatal at line %d" % SITES["fatal"][0]["line"])

    # ---------------- adoption of the frozen predecessor ------------------------------
    print("\n[ADOPTION] the frozen predecessor")
    _u(results, "U36_frozen_grader_md5_matches_registered",
       md5_file(FROZEN_GRADER) == FROZEN_GRADER_MD5, FROZEN_GRADER_MD5)
    _u(results, "U37_frozen_grader_on_disk_is_the_committed_blob",
       git_blob_sha(FROZEN_GRADER) == FROZEN_GRADER_BLOB, FROZEN_GRADER_BLOB)

    src_txt = open(FROZEN_GRADER).read()
    _u(results, "U38_frozen_FATAL_TOKENS_carries_the_bare_FPE_token",
       "Floating point exception" in mod.FATAL_TOKENS
       and 'r"' not in src_txt.split("FATAL_TOKENS = ")[1].split(")")[0]
       and "def fatal_tokens_in" in src_txt,
       "THE trapFpe ANSWER: so1b_grade.py:133 carries the bare substring token")

    _u(results, "U39_rebind_audit_names_are_exactly_the_registered_set",
       tuple(audit["names_rebound"]) == REGISTERED_REBIND,
       "rebound=%s" % audit["names_rebound"])

    def _unregistered_rebind():
        m2 = load_frozen()
        fp0 = _fingerprint(m2)
        m2.fatal_tokens_in = make_repaired_fatal_tokens_in(m2)
        m2.g_cl = lambda *a, **k: None
        fp1 = _fingerprint(m2)
        rb = tuple(sorted(k for k in set(fp0) | set(fp1) if fp0.get(k) != fp1.get(k)))
        if rb != REGISTERED_REBIND:
            refuse("REBIND_AUDIT", {"expected": list(REGISTERED_REBIND), "actual": list(rb)})
    ok, msg = _raises(_unregistered_rebind, "REBIND_AUDIT")
    _u(results, "U40_MUSTFLAG_unregistered_rebind_is_caught", ok, msg[:90])

    def _through_frozen_refuse():
        mod.refuse("G1", {"driven": "a refusal from the repaired path"})
    ok, msg = _raises(_through_frozen_refuse, "G1")
    raised_type = None
    try:
        _through_frozen_refuse()
    except Exception as ex:                                           # noqa: BLE001
        raised_type = type(ex) is mod.Refusal
    _u(results, "U41_refusals_raise_through_the_frozen_modules_own_refuse",
       ok and raised_type is True, "type is so1b_grade.Refusal")

    _u(results, "U42_frozen_bands_and_thresholds_did_not_move",
       audit["constants_moved"] == [] and audit["constants_checked"] == len(FROZEN_CONSTANTS_WATCHED),
       "%d constants checked, 0 moved" % audit["constants_checked"])

    _u(results, "U43_shape6_is_in_the_frozen_COMPONENTS_REGISTERED",
       ["shape", 6] in mod.COMPONENTS_REGISTERED,
       "the component three instruments finger is IN the registered set: %s"
       % (mod.COMPONENTS_REGISTERED,))

    # ---------------- hygiene ---------------------------------------------------------
    print("\n[HYGIENE]")
    na_g = count_asserts(os.path.abspath(__file__))
    na_p = count_asserts(os.path.join(HERE, "so1br_precondition.py"))
    _u(results, "U44_zero_assert_in_so1br_grade", na_g == 0, "ast.Assert count = %d" % na_g)
    _u(results, "U45_zero_assert_in_so1br_precondition", na_p == 0, "ast.Assert count = %d" % na_p)

    ad_hits, modes = {}, {}
    for fn in AD_SCANNED_FILES:
        p = os.path.join(A1, "curriculum_SO1b", fn)
        txt = open(p, errors="replace").read() if os.path.isfile(p) else ""
        ad_hits[fn] = [t for t in FORWARD_AD_TOKENS if t in txt]
        modes[fn] = REQUIRED_DERIVATIVE_MODE in txt
    _u(results, "U46_no_forward_AD_dependency_anywhere_in_the_instrument_set",
       all(not v for v in ad_hits.values()) and modes["so1b_of.py"] and modes["so1b_runScript.py"],
       "0 forward-AD tokens in %d files; derivative mode is REVERSE in of.py and runScript.py"
       % len(AD_SCANNED_FILES))

    strays = []
    for d in ("curriculum_SO1b", "curriculum_SO1aR", "curriculum_SO1bR"):
        p = os.path.join(A1, d, "__pycache__")
        if os.path.isdir(p):
            strays.append(p)
    _u(results, "U47_no_pycache_written_beside_any_frozen_case",
       not strays and sys.dont_write_bytecode is True, "strays=%s" % strays)

    # ---------------- the Stage-2 entry point refuses with no root --------------------
    ok, _ = _raises(lambda: grade_root(os.path.join(tmp, "no_such_root")),
                    "PRESERVED_ROOT_ABSENT")
    if not ok:
        results.append({"unit": "STAGE2_ROOT_GUARD", "ok": False,
                        "detail": "grade_root did not refuse on an absent root"})
        print("  FAIL STAGE2_ROOT_GUARD")

    shutil.rmtree(tmp, ignore_errors=True)
    n = len(results)
    fails = [r["unit"] for r in results if not r["ok"]]
    print("\nunits run = %d / EXPECTED_UNITS = %d ; failures = %d ; optimized = %s"
          % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s"
              % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 1
    print("SO1bR SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)"
          % (n, EXPECTED_UNITS))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    print("SO1bR comparator.  Stage 1 is instrument-only: run with --selftest.  "
          "Stage 2 (grade_root) is not frozen by this document; see "
          "PREREGISTRATION.md section 12.")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
