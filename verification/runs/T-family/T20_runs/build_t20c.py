#!/usr/bin/env python3
"""Build ONE registered T20 case, WITH `constant/g` AND -- for the registered
planted arm ONLY -- the registered per-case `fvOptions` volumetric-source
override.  SUCCESSOR TO build_t20b.py FOR THE BUILDER ONLY.

  *** THIS BUILDER IS NOT YET AUTHORISED TO RUN.  NO T20_LC_P10 CASE EXISTS. ***

WHY THIS FILE EXISTS.  T20 graded on 2026-08-31 as `NOT A RESULT` FOR THE WHOLE
RUNG -- comparator exit 3 at S7 criterion (i) -- because `T20_LC_P10` was never
built.  P10 is verdict-map row V5's only case and S12 (:1062) registers that a
refusal there takes the whole rung down.  The other six cases are rule-4
complete.  The rung is forfeit for want of one 3000-step case whose registered
POINT is 0.1584 core-min (S11.2 :1017).

The reason P10 could not be built is stated, in advance, by this rung's own
prose-transcription file, `T20_prose_cases_7b93b2c8.json` -> `_stopped` ->
`T20_LC_P10` -> `what_would_be_needed`:

    "A per-case physics override honoured by the builder."

`build_t20.py:136-146` writes the `fvOptions` explicit source from the GLOBAL
block `physics.q_volumetric`, and the case schema carries no per-case physics
field at all.  A `q_volumetric` key added to a P10 case entry would be INERT --
the builder would emit 5000 and the tree would be byte-identical to `T20_LC_f`
while the registration claimed it was the +10 % planted arm.  That is a
registered lever connected to nothing, and it is worse than an absent case
because it would silently PASS a planted control that never planted anything.
THIS FILE IS THAT MISSING LEVER, AND NOTHING ELSE.

  *** THE AUTHORISATION QUESTION IS OPEN, AND THIS FILE DOES NOT ANSWER IT. ***

Whether this builder repair needs a `VERIFICATION_CHARTER.md` §2d.1 grant is
**REFERRED TO VERIFICATION AND UNRULED**.  The permissive reading is that no
gate, threshold, band, cap or label moves -- 5500 is registered PROSE at
`T20_PREREGISTRATION.md:793-794`, frozen at commit `7b93b2c8`, and this is the
same "conform the mechanism to the registration" move ruled legal without a
§2d.1 grant for T19 (`DEAD_LEVER_AUDIT.md` §21.2) and for T20's own
transcription (§24.2).  THE COUNTER-ARGUMENT IS REAL AND IS NOT WAVED AWAY: a
per-case override of a rung-global `physics` value is a NEW BUILDER CAPABILITY
introduced AFTER first compute (2026-08-31T00:12:44Z), and after first compute
gates are closed.  The heat-transfer supervisor is the beneficiary of the
permissive reading and will not self-grant it.  Clearance for `build_t20b.py`'s
`constant/g` repair is EXPLICITLY NOT clearance for this one: `g` is forced by
the solver and changes no physics, whereas `q` is a registered physical value.
Treating the first as authority for the second is permission laundering
(CLAUDE.md rule 9), and it is refused here in code, not only in prose:

  * `LIVE_TREE_PLANTED_INTERLOCK` -- this file REFUSES (exit 2) to emit the
    registered planted case ANYWHERE INSIDE THIS RUNG'S OWN DIRECTORY.  It can
    be exercised, paired-built and byte-compared in scratch; it cannot produce
    the run.  Lifting that clause is verification's ruling to make, and it is a
    one-line, dated, disclosed edit made BEFORE this builder's first compute.
  * A second, independent interlock already exists and is not this file's:
    `run_one_t20.sh:80-82` refuses to launch any case absent from
    `T20_registered.json`, and `T20_LC_P10` is not in it.

WHAT THIS FILE IS NOT.
  * It is NOT an edit to `build_t20.py` or `build_t20b.py`.  Both are left
    untouched (CLAUDE.md rule 6).  This is a successor that CALLS them.
  * It introduces NO new registration document and TRANSCRIBES NOTHING.  It
    does not add `T20_LC_P10` to `T20_registered.json` (which it hashes before
    and after and refuses if it moved by one byte) and it does not add P10 to
    `T20_prose_cases_7b93b2c8.json`, whose `_stopped` entry STOPS that case
    under `DEAD_LEVER_AUDIT.md` §24.4(a).  Transcribing P10 is a SEPARATE act,
    separately ruled, and is not taken here.
  * It is NOT a new rule, standard or tool.  It is the one lever the frozen
    registration already describes and the builder could not reach.

THE PLANTED VALUE IS NOT A CALLER'S CHOICE.  Every number is read from a frozen
artifact at call time:
  * the BASE `q'''` from `T20_registered.json` -> `physics.q_volumetric`;
  * the CASE NAME, the FACTOR and the PLANTED VALUE from the frozen
    pre-registration's own sentence at S7.2 :793-794, parsed from the bytes of
    the COMMITTED BLOB at `prereg_commit`, with the working-tree file required
    to be byte-equal to it.
The builder REFUSES if: the sentence is not uniquely pinned; the document's base
disagrees with the registered `physics` base; planted != factor x base in EXACT
rational arithmetic; the override is requested for any case other than the one
the document names; or the override value is anything but the document's own.
A builder that accepts an arbitrary source is a lever to FABRICATE a planted
arm, and the whole evidentiary value of V5 is that it cannot be fabricated.

HOW THE DELTA IS KEPT MINIMAL, BY CONSTRUCTION AND NOT BY PROMISE.  This file
does not reimplement its parents.  It CALLS `build_t20b.build()` -- which itself
calls `build_t20.main()` -- and then rewrites ONE TOKEN in ONE FILE.  `--paired`
measures that rather than asserting it: the same case is built through
`build_t20b.py` and through this file into two scratch roots and every emitted
byte is compared.

usage: build_t20c.py --case T20_LC_c [--root <dir>]
       build_t20c.py --case <planted case> --params <json> --planted-source 5500
       build_t20c.py --paired [--case T20_LC_c]
       build_t20c.py --selftest
"""
import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

SELF = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SELF)
import build_t20   # noqa: E402  -- grandparent; called, never modified
import build_t20b  # noqa: E402  -- parent; called, never modified

EXIT_REFUSE = 2
REAL_REG = os.path.join(SELF, "T20_registered.json")

# The registered sentence, S7.2 :793-794 of the frozen pre-registration.  The
# CASE NAME, the PLANTED VALUE, the BASE and the FACTOR are all read out of it;
# none of the four is written here.
PLANT_RE = re.compile(
    r"\*\*Planted\*\*\s*\(`(T20_[A-Za-z0-9_]+)`\)\s*:\s*identical case with\s*"
    r"`fvOptions`\s*explicit source\s*`([0-9]+(?:\.[0-9]+)?)`\s*"
    r"\(=\s*([0-9]+(?:\.[0-9]+)?)\s*[×x]\s*([0-9]+(?:\.[0-9]+)?)\)")

# THE INTERLOCK.  See the header.  This clause, and only this clause, is what
# verification's ruling would lift.
LIVE_TREE_PLANTED_INTERLOCK = True


def refuse(msg):
    sys.stderr.write("REFUSE (exit %d): %s\n" % (EXIT_REFUSE, msg))
    sys.exit(EXIT_REFUSE)


def _sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _sha256(path):
    return _sha256_bytes(open(path, "rb").read())


def _inside(path, parent):
    rp, pp = os.path.realpath(path), os.path.realpath(parent)
    return rp == pp or rp.startswith(pp + os.sep)


# --------------------------------------------------------------------------
# THE FROZEN READ.  Both numbers, and the case name, come from frozen artifacts.
# --------------------------------------------------------------------------
class Plant(object):
    def __init__(self, case, planted, base, factor, doc_sha, src):
        self.case = case
        self.planted = planted        # Fraction
        self.base = base              # Fraction, from physics.q_volumetric
        self.doc_base = None          # Fraction, from the document sentence
        self.factor = factor          # Fraction
        self.doc_sha = doc_sha
        self.src = src


def committed_blob_text(commit, relpath):
    """Bytes of the frozen document AS COMMITTED.  Fail-closed: if git cannot
    produce the blob the builder REFUSES rather than falling back to the
    working tree, because the working tree is exactly what the check exists to
    doubt (CLAUDE.md rule 2 -- hash the frozen file against the committed blob)."""
    try:
        top = subprocess.check_output(["git", "-C", SELF, "rev-parse",
                                       "--show-toplevel"],
                                      stderr=subprocess.DEVNULL).decode().strip()
        out = subprocess.check_output(["git", "-C", top, "cat-file", "blob",
                                       "%s:%s" % (commit, relpath)],
                                      stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError) as e:
        refuse("cannot read the COMMITTED blob %s:%s (%s). The frozen document "
               "cannot be verified, so nothing is built." % (commit, relpath, e))
    return out.decode("utf-8", "replace")


def registered_plant(reg_path=REAL_REG, doc_text=None, blob_text=None):
    """Read the planted arm's case, factor and value from FROZEN artifacts.

    `doc_text`/`blob_text` exist so the planted controls can drive this reader
    on bytes written by the real producer with ONE mutation applied; they are
    never used by a real build.
    """
    reg = json.load(open(reg_path))
    base = Fraction(str(reg["physics"]["q_volumetric"]))
    commit, relpath = reg["prereg_commit"], reg["prereg_path"]

    if blob_text is None:
        blob_text = committed_blob_text(commit, relpath)
    if doc_text is None:
        try:
            top = subprocess.check_output(
                ["git", "-C", SELF, "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL).decode().strip()
        except (OSError, subprocess.CalledProcessError) as e:
            refuse("cannot locate the repository root to read the frozen "
                   "pre-registration (%s)" % e)
        wt = os.path.join(top, relpath)
        if not os.path.isfile(wt):
            refuse("the frozen pre-registration %s is not on disk" % wt)
        doc_text = open(wt, encoding="utf-8").read()

    ds, bs = _sha256_bytes(doc_text.encode()), _sha256_bytes(blob_text.encode())
    if ds != bs:
        refuse("the working-tree pre-registration does NOT match the committed "
               "blob at %s -- working tree sha256 %s, committed %s. A frozen "
               "file is never edited (CLAUDE.md rule 6); the registered plant "
               "is not read from an edited document." % (commit, ds, bs))

    flat = " ".join(blob_text.split())
    ms = PLANT_RE.findall(flat)
    if len(ms) != 1:
        refuse("the frozen document pins the planted source %d times, not once "
               "(%s). A value that is not UNIQUELY pinned is not registered, "
               "and no best guess is taken." % (len(ms), ms))
    case, planted_s, docbase_s, factor_s = ms[0]
    planted, doc_base, factor = (Fraction(planted_s), Fraction(docbase_s),
                                 Fraction(factor_s))

    if doc_base != base:
        refuse("the frozen document's base q''' is %s but T20_registered.json's "
               "physics.q_volumetric is %s. The two frozen artifacts disagree; "
               "the document wins and the transcription is what is wrong -- "
               "nothing is built on a disagreement."
               % (docbase_s, str(base)))
    if planted != factor * doc_base:
        refuse("the frozen document's own arithmetic does not close: %s != %s x "
               "%s (exact rational arithmetic). Nothing is built."
               % (planted_s, factor_s, docbase_s))

    p = Plant(case, planted, base, factor, ds,
              "%s:%s S7.2 planted-arm sentence" % (relpath, commit[:8]))
    p.doc_base = doc_base
    return p


# --------------------------------------------------------------------------
# THE ONE EMITTED CHANGE, AND ITS FAIL-CLOSED READER.
# --------------------------------------------------------------------------
def fvoptions_path(case_dir, region):
    return os.path.join(case_dir, "constant", region, "fvOptions")


def _token(value):
    """The exact token build_t20.py:144-146 emits for a source value."""
    return "explicit    constant %.10g;" % float(value)


def apply_override(case_dir, region, base, planted):
    """Rewrite EXACTLY ONE token.  Refuses on anything but a clean 1-for-1."""
    p = fvoptions_path(case_dir, region)
    if not os.path.isfile(p):
        refuse("no fvOptions at %s -- the parent did not emit the file this "
               "override exists to change" % p)
    txt = open(p).read()
    old, new = _token(base), _token(planted)
    n = txt.count(old)
    if n != 1:
        refuse("fvOptions carries the base source token %r %d times, not once. "
               "A multi-site or zero-site rewrite is not a per-case override; "
               "the case is LEFT ON DISK for inspection." % (old, n))
    out = txt.replace(old, new, 1)
    with open(p, "w") as f:
        f.write(out)
    back = open(p).read()
    if back.replace(new, old, 1) != txt:
        refuse("the fvOptions rewrite changed more than the one source token. "
               "The case is LEFT ON DISK for inspection.")
    return old, new


def verify_source(case_dir, region, base, planted):
    """FAIL-CLOSED reader.  Returns (ok, message); never raises on a bad tree.

    This is the limb the planted controls drive.  It must be able to FAIL, and
    selftest limbs (c2), (c3), (c6) and (c9) demonstrate that it does.
    """
    p = fvoptions_path(case_dir, region)
    if not os.path.isfile(p):
        return False, "fvOptions does not exist at %s" % p
    try:
        txt = open(p).read()
    except OSError as e:
        return False, "fvOptions exists but cannot be read: %s" % e
    if not txt.strip():
        return False, "fvOptions is empty"
    if "FoamFile" not in txt:
        return False, "fvOptions has no FoamFile header -- OpenFOAM will refuse it"
    if "scalarSemiImplicitSource" not in txt:
        return False, ("fvOptions is not a scalarSemiImplicitSource; the "
                       "registered volumetric source is that type")
    want, base_tok = _token(planted), _token(base)
    if txt.count(want) != 1:
        return False, ("fvOptions does not carry the registered planted source "
                       "token %r exactly once (found %d)"
                       % (want, txt.count(want)))
    if base_tok in txt:
        return False, ("fvOptions STILL carries the unplanted base token %r -- "
                       "a planted arm that also carries the base value is not a "
                       "planted arm" % base_tok)
    return True, ("fvOptions carries the registered planted source %s (= %s x %s)"
                  % (float(planted), float(planted) / float(base), float(base)))


# --------------------------------------------------------------------------
# BUILD
# --------------------------------------------------------------------------
def build(case, root, params_file=None, planted_source=None):
    plant = registered_plant()          # refuses on any frozen-artifact defect

    # --- the override is legal for ONE case and at ONE value, both frozen ---
    if planted_source is not None:
        if case != plant.case:
            refuse("a source override was requested for %s, but the frozen "
                   "document registers the planted arm as %s and no other case. "
                   "A per-case source on any other case is UNREGISTERED physics."
                   % (case, plant.case))
        try:
            got = Fraction(str(planted_source))
        except (ValueError, ZeroDivisionError):
            refuse("--planted-source %r is not a number" % planted_source)
        if got != plant.planted:
            refuse("--planted-source %s is not the registered planted value %s "
                   "(= %s x %s, %s). The planted value is NOT a caller's choice."
                   % (planted_source, plant.planted, plant.factor, plant.base,
                      plant.src))
    elif case == plant.case:
        refuse("%s is the registered planted arm and was requested WITHOUT "
               "--planted-source. The parent builder would emit the base source "
               "%s, producing a tree byte-identical to the unplanted case while "
               "the registration claimed a +%s%% plant -- a registered lever "
               "connected to nothing. Refused."
               % (case, float(plant.base),
                  float((plant.factor - 1) * 100)))

    # --- THE INTERLOCK: this builder may not emit the planted case for real ---
    if case == plant.case and LIVE_TREE_PLANTED_INTERLOCK and _inside(root, SELF):
        refuse("emitting %s into the live rung tree %s is NOT AUTHORISED. "
               "Whether this builder repair needs a VERIFICATION_CHARTER §2d.1 "
               "grant is REFERRED TO VERIFICATION AND UNRULED; no supervisor "
               "self-grants it, and clearance for build_t20b.py's constant/g "
               "repair is NOT clearance for a per-case physics override "
               "(CLAUDE.md rule 9). Scratch roots are permitted so the "
               "instrument can be verified before it is authorised."
               % (case, SELF))

    reg = json.load(open(REAL_REG))
    region = reg["region"]

    # --- THE REGISTRATION IS NEVER WRITTEN.  Watch every registration path in
    #     effect -- the real file, and whatever build_t20 is pointed at now --
    #     and refuse if either moves by a byte, before or after the parent runs.
    watch, seen = [], set()
    for p in (REAL_REG, build_t20.REG):
        rp = os.path.realpath(p)
        if rp in seen or not os.path.isfile(rp):
            continue
        seen.add(rp)
        watch.append((rp, _sha256(rp)))

    rc = build_t20b.build(case, root, params_file)   # emits EVERYTHING else
    if rc != 0:
        refuse("parent build_t20b.build() returned rc=%s" % rc)

    for rp, h in watch:
        if not os.path.isfile(rp):
            refuse("the registration %s DISAPPEARED during the build" % rp)
        if _sha256(rp) != h:
            refuse("the registration %s CHANGED during the build. It is the "
                   "registration and is never written." % rp)

    d = os.path.join(root, case)
    if planted_source is None:
        print("build_t20c: %s  -- no source override (registered base %s)"
              % (d, float(plant.base)))
        return 0

    old, new = apply_override(d, region, plant.base, plant.planted)
    ok, msg = verify_source(d, region, plant.base, plant.planted)
    if not ok:
        refuse("%s -- the case is LEFT ON DISK for inspection, never cleaned "
               "(CLAUDE.md rule 10)." % msg)

    for rp, h in watch:
        if _sha256(rp) != h:
            refuse("the registration %s CHANGED during the override" % rp)

    with open(os.path.join(d, "CASE.txt"), "a") as f:
        f.write("\nBUILDER SUCCESSOR: build_t20c.py applied the REGISTERED "
                "per-case fvOptions\nvolumetric-source override: %r -> %r.\n"
                "Base q''' %s from T20_registered.json physics.q_volumetric; "
                "planted value\n%s and factor %s read from %s.\n"
                "NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES; T20's "
                "pre-registration at\n7b93b2c8 governs unchanged. Whether this "
                "builder capability needs a\nVERIFICATION_CHARTER §2d.1 grant "
                "is REFERRED TO VERIFICATION AND UNRULED.\n"
                % (old, new, float(plant.base), float(plant.planted),
                   float(plant.factor), plant.src))
    print("build_t20c: %s  -- %s" % (d, msg))
    return 0


# --------------------------------------------------------------------------
# PAIRED BUILD.  The delta is MEASURED over emitted bytes, not asserted.
# --------------------------------------------------------------------------
def _tree(d):
    out = {}
    for r, _, fs in os.walk(d):
        for fn in fs:
            fp = os.path.join(r, fn)
            rel = os.path.relpath(fp, d)
            try:
                out[rel] = open(fp, "rb").read()
            except OSError:
                out[rel] = b"<unreadable>"
    return out


# Build-log lines that are PROCESS METADATA and cannot be equal between two
# runs of the same builder, let alone two builders.  MEASURED, not assumed: with
# only the root path normalised, the two log.blockMesh files differ on exactly
# two lines, both `PID    : <n>`.  The other keys are normalised for the same
# reason before they can bite (a build that straddles a second boundary would
# move Date/Time).  Everything else in the log is compared byte-for-byte.
_LOG_META = re.compile(
    r"^(Date|Time|Host|PID|Case|nProcs|Build|Exec|ExecutionTime|ClockTime)\b.*$",
    re.M)


def _norm_log(b, root):
    return _LOG_META.sub(lambda m: m.group(0).split()[0] + " <NORMALISED>",
                         b.replace(root, "<ROOT>"))


def _kind(rel):
    if os.path.basename(rel).startswith("log."):
        return "log"
    if rel == "CASE.txt":
        return "provenance"
    return "solver"


def paired(case, params_file=None, planted_source=None, tmp=None):
    """Build `case` through build_t20b.py and through this file into two scratch
    roots and compare EVERY emitted byte.  Returns a dict of counts."""
    own = tmp is None
    tmp = tmp or tempfile.mkdtemp(prefix="t20c_paired_")
    if _inside(tmp, SELF):
        refuse("paired-build scratch %s resolves INSIDE the live rung tree %s"
               % (tmp, SELF))
    try:
        rb = os.path.join(tmp, "b_" + case)
        rc_ = os.path.join(tmp, "c_" + case)
        os.makedirs(rb)
        os.makedirs(rc_)
        build_t20b.build(case, rb, params_file)
        build(case, rc_, params_file, planted_source)
        tb, tc = _tree(os.path.join(rb, case)), _tree(os.path.join(rc_, case))

        res = {"case": case, "only_b": sorted(set(tb) - set(tc)),
               "only_c": sorted(set(tc) - set(tb)), "common": 0,
               "solver_same": 0, "solver_diff": [], "prov_same": 0,
               "prov_diff": [], "prov_append_only": None, "prov_suffix": "",
               "log_same": 0, "log_diff": [], "byte_delta": {}}
        for rel in sorted(set(tb) & set(tc)):
            res["common"] += 1
            a, b = tb[rel], tc[rel]
            k = _kind(rel)
            if k == "log":
                a = _norm_log(a.decode("utf-8", "replace"),
                              os.path.join(rb, case)).encode()
                b = _norm_log(b.decode("utf-8", "replace"),
                              os.path.join(rc_, case)).encode()
                (res["log_diff"].append(rel) if a != b
                 else res.__setitem__("log_same", res["log_same"] + 1))
            elif k == "provenance":
                if a != b:
                    res["prov_diff"].append(rel)
                    # APPEND-ONLY is the claim, so it is MEASURED: c's CASE.txt
                    # must be b's bytes plus a suffix.  A rewritten provenance
                    # record would fail this and is not "one added disclosure".
                    res["prov_append_only"] = b.startswith(a)
                    res["prov_suffix"] = b[len(a):].decode("utf-8", "replace")
                else:
                    res["prov_same"] += 1
            else:
                if a != b:
                    res["solver_diff"].append(rel)
                    res["byte_delta"][rel] = (len(a), len(b))
                else:
                    res["solver_same"] += 1
        return res
    finally:
        if own:
            shutil.rmtree(tmp, ignore_errors=True)


def _print_paired(r):
    print("  paired build of %s: %d common files; only-in-b %s; only-in-c %s"
          % (r["case"], r["common"], r["only_b"], r["only_c"]))
    print("    SOLVER-READ files: %d byte-identical, %d differing %s"
          % (r["solver_same"], len(r["solver_diff"]), r["solver_diff"]))
    print("    PROVENANCE (CASE.txt): %d identical, %d differing %s"
          % (r["prov_same"], len(r["prov_diff"]), r["prov_diff"]))
    print("    BUILD LOGS (root path + process-metadata lines normalised): "
          "%d identical, %d differing %s"
          % (r["log_same"], len(r["log_diff"]), r["log_diff"]))


# --------------------------------------------------------------------------
# SELFTEST.  NO LIMB TOUCHES A LIVE RUN TREE, AND NO LIMB WRITES ANY FROZEN FILE.
#
# T20's S8 registers the first clause and it is not optional: analyse_t18.py:509
# and analyse_t19.py:691 each carried a limb that called into the LIVE tree and
# BOTH inverted on 2026-08-31 the moment the campaign succeeded.
#
# THE P10 FIXTURE IS NOT A TRANSCRIPTION, AND THIS IS LOAD-BEARING.  `T20_LC_P10`
# is STOPPED under DEAD_LEVER_AUDIT §24.4(a) and its mesh/step values are NOT
# transcribed anywhere in this lab.  This selftest therefore does NOT write P10's
# registered parameters.  It copies `T20_LC_c`'s ALREADY-REGISTERED entry under
# the planted case's name, in a tempfile that is deleted in a `finally`, purely
# to exercise the code path.  A case built from that fixture is NOT the
# registered P10 and could never be graded as it -- which is exactly why the
# fixture is safe and why this file transcribes nothing.
# --------------------------------------------------------------------------
def _fixture_params(case):
    reg = json.load(open(REAL_REG))
    entry = dict(reg["cases"]["T20_LC_c"])
    entry["_FIXTURE_NOT_A_REGISTRATION"] = (
        "COPIED VERBATIM FROM THE ALREADY-REGISTERED T20_LC_c ENTRY so the "
        "override code path can be exercised. This is NOT %s's registered "
        "parameter set: that case is STOPPED under DEAD_LEVER_AUDIT 24.4(a) and "
        "is transcribed nowhere. A case built from this fixture is a code-path "
        "exerciser and is NOT gradeable." % case)
    fd, p = tempfile.mkstemp(prefix="t20c_fixture_", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump({"_what_this_file_is": entry["_FIXTURE_NOT_A_REGISTRATION"],
                   "cases": {case: entry}}, f, indent=1)
    return p


def _refusal_code(fn, *a, **kw):
    """Run fn; return (exit_code_or_None, stderr_text). A refusal is exit 2."""
    err = tempfile.TemporaryFile(mode="w+")
    keep, sys.stderr = sys.stderr, err
    try:
        fn(*a, **kw)
        code = None
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    finally:
        sys.stderr = keep
        err.seek(0)
        txt = err.read()
        err.close()
    return code, txt


def selftest():
    fails = []

    def ok(cond, label):
        print("  [%s] %s" % ("ok " if cond else "FAIL", label))
        if not cond:
            fails.append(label)

    real_reg_sha = _sha256(REAL_REG)
    live_before = sorted(os.listdir(SELF))
    tmp = tempfile.mkdtemp(prefix="t20c_selftest_")
    if _inside(tmp, SELF):
        sys.exit("REFUSE: selftest scratch %s resolves INSIDE the live rung tree"
                 % tmp)
    fixture = None
    try:
        # ---- (c0) NEGATIVE: the real frozen artifacts read cleanly ---------
        plant = registered_plant()
        ok(str(plant.base) == "5000" and str(plant.planted) == "5500"
           and plant.factor == Fraction(11, 10),
           "FROZEN READ: case %s, base %s, factor %s, planted %s -- all from "
           "frozen artifacts" % (plant.case, plant.base, plant.factor,
                                 plant.planted))

        # ---- (c1) PAIRED BUILD, NON-PLANTED CASE: zero differences ---------
        r1 = paired("T20_LC_c", tmp=os.path.join(tmp, "p1"))
        _print_paired(r1)
        ok(not r1["only_b"] and not r1["only_c"] and not r1["solver_diff"]
           and not r1["prov_diff"] and not r1["log_diff"],
           "PAIRED (non-planted T20_LC_c): b and c emit BYTE-IDENTICAL trees "
           "(%d solver-read files identical, 0 differing, fvOptions included; "
           "CASE.txt identical; build log identical)" % r1["solver_same"])

        # ---- (c2) PLANTED CONTROL: override on a NON-planted case ----------
        code, txt = _refusal_code(build, "T20_LC_c", os.path.join(tmp, "x2"),
                                  None, str(plant.planted))
        ok(code == EXIT_REFUSE and "no other case" in txt,
           "PLANTED: override requested for T20_LC_c -> REFUSES (exit %s)" % code)
        ok(not os.path.exists(os.path.join(tmp, "x2", "T20_LC_c")),
           "PLANTED: the refused non-planted override emitted NO case directory")

        # ---- (c3) PLANTED CONTROL: override at the BASE value, not planted --
        fixture = _fixture_params(plant.case)
        code, txt = _refusal_code(build, plant.case, os.path.join(tmp, "x3"),
                                  fixture, str(plant.base))
        ok(code == EXIT_REFUSE and "NOT a caller's choice" in txt,
           "PLANTED: --planted-source %s (the BASE, not the plant) -> REFUSES "
           "(exit %s)" % (plant.base, code))
        code, _ = _refusal_code(build, plant.case, os.path.join(tmp, "x3b"),
                                fixture, "5500.0000001")
        ok(code == EXIT_REFUSE,
           "PLANTED: --planted-source 5500.0000001 -> REFUSES (exit %s)" % code)

        # ---- (c4) PLANTED CONTROL: the planted case with NO override -------
        code, txt = _refusal_code(build, plant.case, os.path.join(tmp, "x4"),
                                  fixture, None)
        ok(code == EXIT_REFUSE and "connected to nothing" in txt,
           "PLANTED: planted case built WITHOUT an override -> REFUSES (exit %s)"
           % code)

        # ---- (c5) PLANTED CONTROL: the live-tree interlock ------------------
        code, txt = _refusal_code(build, plant.case, SELF, fixture,
                                  str(plant.planted))
        ok(code == EXIT_REFUSE and "NOT AUTHORISED" in txt,
           "PLANTED: planted case into the LIVE rung tree -> REFUSES (exit %s)"
           % code)
        ok(sorted(os.listdir(SELF)) == live_before,
           "PLANTED: the interlock refusal created NOTHING in the live tree")

        # ---- (c6) POSITIVE + PAIRED: the planted case, at the planted value -
        r2 = paired(plant.case, params_file=fixture,
                    planted_source=str(plant.planted),
                    tmp=os.path.join(tmp, "p2"))
        _print_paired(r2)
        fv = os.path.join("constant", json.load(open(REAL_REG))["region"],
                          "fvOptions")
        ok(r2["solver_diff"] == [fv] and not r2["only_b"] and not r2["only_c"]
           and not r2["log_diff"],
           "PAIRED (planted arm): the ONLY differing solver-read file is %s "
           "(%d others byte-identical; build log identical). CASE.txt differs "
           "by the disclosure block ONLY: %s"
           % (fv, r2["solver_same"], r2["prov_diff"]))
        a, b = r2["byte_delta"].get(fv, (0, 0))
        ok(a == b, "PAIRED (planted arm): fvOptions same length %d bytes both "
                   "sides -- the delta is the VALUE token, nothing structural" % a)
        ok(r2["prov_append_only"] is True,
           "PAIRED (planted arm): CASE.txt is APPEND-ONLY -- c's bytes are b's "
           "bytes plus %d disclosure bytes, nothing rewritten"
           % len(r2["prov_suffix"]))

        rc_dir = os.path.join(tmp, "p2c")
        os.makedirs(rc_dir)
        build(plant.case, rc_dir, fixture, str(plant.planted))
        emitted = open(os.path.join(rc_dir, plant.case, fv)).read()
        ok(_token(plant.planted) in emitted and _token(plant.base) not in emitted,
           "POSITIVE: emitted fvOptions carries %r and NOT %r"
           % (_token(plant.planted), _token(plant.base)))
        ok(verify_source(os.path.join(rc_dir, plant.case),
                         json.load(open(REAL_REG))["region"],
                         plant.base, plant.planted)[0],
           "POSITIVE: verify_source ACCEPTS the tree the builder just wrote")

        # ---- (c7) PLANTED CONTROL: verify_source must be able to REFUSE ----
        rev = os.path.join(tmp, "reverted")
        shutil.copytree(os.path.join(rc_dir, plant.case), rev)
        rp = os.path.join(rev, fv)
        _t = open(rp).read()
        with open(rp, "w") as _f:
            _f.write(_t.replace(_token(plant.planted), _token(plant.base)))
        ok(not verify_source(rev, json.load(open(REAL_REG))["region"],
                             plant.base, plant.planted)[0],
           "PLANTED: fvOptions reverted to the base value -> verify_source REFUSES")
        # NEITHER token present: the planted arm's value is simply gone.  This
        # limb exists because it is the ONLY one that drives verify_source's
        # "planted token present exactly once" conjunct -- the reverted-tree
        # limb above is caught one conjunct earlier, so without this limb that
        # conjunct is decoration.  Measured by mutation control M5.
        neither = os.path.join(tmp, "neither")
        shutil.copytree(os.path.join(rc_dir, plant.case), neither)
        np_ = os.path.join(neither, fv)
        _t = open(np_).read()
        with open(np_, "w") as _f:
            _f.write(_t.replace(_token(plant.planted),
                                "explicit    constant 1234;"))
        ok(not verify_source(neither, json.load(open(REAL_REG))["region"],
                             plant.base, plant.planted)[0],
           "PLANTED: fvOptions source replaced by an unregistered value -> "
           "verify_source REFUSES")

        # BOTH tokens present: a second source line carrying the base value.
        # The ONLY limb that drives the "base token absent" conjunct.  Measured
        # by mutation control M6.
        both = os.path.join(tmp, "both")
        shutil.copytree(os.path.join(rc_dir, plant.case), both)
        bp = os.path.join(both, fv)
        _t = open(bp).read()
        with open(bp, "w") as _f:
            _f.write(_t.replace(_token(plant.planted),
                                _token(plant.planted) + "\n            "
                                + _token(plant.base)))
        ok(not verify_source(both, json.load(open(REAL_REG))["region"],
                             plant.base, plant.planted)[0],
           "PLANTED: fvOptions carries the planted AND the base token -> "
           "verify_source REFUSES")

        emp = os.path.join(tmp, "emptied")
        shutil.copytree(os.path.join(rc_dir, plant.case), emp)
        open(os.path.join(emp, fv), "w").close()
        ok(not verify_source(emp, json.load(open(REAL_REG))["region"],
                             plant.base, plant.planted)[0],
           "PLANTED: fvOptions EMPTIED -> verify_source REFUSES")

        # ---- (c8) PLANTED CONTROL: the registration MOVES mid-build --------
        #      The REAL registration is never written.  build_t20 is pointed at
        #      a scratch COPY for the limb and the plant mutates that copy.
        scratch_reg = os.path.join(tmp, "reg_copy.json")
        shutil.copyfile(REAL_REG, scratch_reg)
        real_main, real_bbuild = build_t20.main, build_t20b.build
        old_reg = build_t20.REG
        try:
            build_t20.REG = scratch_reg

            def mutating_main():
                rc = real_main()
                with open(build_t20.REG, "a") as f:
                    f.write("\n")          # ONE byte, mid-build
                return rc
            build_t20.main = mutating_main
            code, txt = _refusal_code(build, "T20_LC_c",
                                      os.path.join(tmp, "x8"), None, None)
            ok(code == EXIT_REFUSE and "CHANGED during the build" in txt,
               "PLANTED: registration moved by ONE byte DURING the parent build "
               "-> REFUSES (exit %s)" % code)
            build_t20.main = real_main

            def mutating_build(*a, **kw):
                rc = real_bbuild(*a, **kw)
                with open(build_t20.REG, "a") as f:
                    f.write("\n")          # ONE byte, AFTER the parent returned
                return rc
            build_t20b.build = mutating_build
            code, txt = _refusal_code(build, "T20_LC_c",
                                      os.path.join(tmp, "x8b"), None, None)
            ok(code == EXIT_REFUSE and "CHANGED during the build" in txt,
               "PLANTED: registration moved AFTER the parent returned -> this "
               "file's OWN check REFUSES (exit %s)" % code)
        finally:
            build_t20.main, build_t20b.build = real_main, real_bbuild
            build_t20.REG = old_reg

        # ---- (c9) PLANTED CONTROLS ON THE FROZEN DOCUMENT ------------------
        reg = json.load(open(REAL_REG))
        doc = committed_blob_text(reg["prereg_commit"], reg["prereg_path"])
        code, txt = _refusal_code(registered_plant, REAL_REG, doc + "\n", doc)
        ok(code == EXIT_REFUSE and "does NOT match the committed blob" in txt,
           "PLANTED: working-tree document one byte off the committed blob -> "
           "REFUSES (exit %s)" % code)

        bad = doc.replace("`5500` (= 5000", "`6000` (= 5000")
        ok(bad != doc, "PLANTED: the arithmetic mutation actually applied")
        code, txt = _refusal_code(registered_plant, REAL_REG, bad, bad)
        ok(code == EXIT_REFUSE and "arithmetic does not close" in txt,
           "PLANTED: document pins 6000 = 5000 x 1.10 -> REFUSES (exit %s)" % code)

        gone = doc.replace("**Planted** (`T20_LC_P10`)", "**Planted** (case)")
        ok(gone != doc, "PLANTED: the sentence-removal mutation actually applied")
        code, txt = _refusal_code(registered_plant, REAL_REG, gone, gone)
        ok(code == EXIT_REFUSE and "0 times, not once" in txt,
           "PLANTED: the pinning sentence unreadable -> REFUSES, no best guess "
           "(exit %s)" % code)

        two = doc + (
            "\n- **Planted** (`T20_LC_Q9`): identical case with `fvOptions` "
            "explicit source `9000` (= 5000 × 1.80) and nothing.\n")
        code, txt = _refusal_code(registered_plant, REAL_REG, two, two)
        ok(code == EXIT_REFUSE and "2 times, not once" in txt,
           "PLANTED: a SECOND pinning sentence -> REFUSES (exit %s)" % code)

        base_mismatch = doc.replace("`5500` (= 5000", "`5500` (= 4000")
        code, txt = _refusal_code(registered_plant, REAL_REG, base_mismatch,
                                  base_mismatch)
        ok(code == EXIT_REFUSE and "disagree" in txt,
           "PLANTED: document base 4000 vs registered physics 5000 -> REFUSES "
           "(exit %s)" % code)

        # ---- (c10) the family's standing AST check -------------------------
        src = open(os.path.abspath(__file__)).read()
        n = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(src)))
        planted_n = sum(isinstance(x, ast.Assert)
                        for x in ast.walk(ast.parse(src + "\nassert True\n")))
        ok(n == 0 and planted_n == 1,
           "AST assert count in this file = 0 (counter sees a planted assert: %d)"
           % planted_n)
    finally:
        if fixture and os.path.exists(fixture):
            os.remove(fixture)
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- (c11) the two things that must NOT have moved ---------------------
    ok(_sha256(REAL_REG) == real_reg_sha,
       "T20_registered.json sha256 UNCHANGED across the whole selftest (%s)"
       % real_reg_sha[:16])
    ok(sorted(os.listdir(SELF)) == live_before,
       "the live rung tree gained and lost NOTHING across the whole selftest "
       "(%d entries)" % len(live_before))

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case")
    ap.add_argument("--root", default=SELF)
    ap.add_argument("--params", default=None,
                    help="JSON supplying a case NOT in T20_registered.json. "
                         "That file is NEVER written.")
    ap.add_argument("--planted-source", default=None,
                    help="The registered planted volumetric source. REFUSED "
                         "unless it is exactly the value the frozen "
                         "pre-registration pins, for exactly the case it names.")
    ap.add_argument("--paired", action="store_true",
                    help="Build --case through build_t20b.py and through this "
                         "file into two scratch roots and compare every byte.")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.paired:
        _print_paired(paired(a.case or "T20_LC_c", a.params, a.planted_source))
        return 0
    if not a.case:
        ap.error("--case is required unless --selftest or --paired")
    return build(a.case, a.root, a.params, a.planted_source)


if __name__ == "__main__":
    sys.exit(main())
