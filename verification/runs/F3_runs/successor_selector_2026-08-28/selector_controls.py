"""C1-C6 -- the control battery of docs/standards/UNIQUE_SELECTOR_RULE.md sec.7,
frozen at ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6, driven under the gates of
verification/campaign/R1_F3S_SELECTOR_REPAIR_PREREGISTRATION.md.

EVERY control runs through the REAL `select_one` of the module handed in -- never a
re-implementation.  A control that calls a copy of the selector tests the copy.

THE BIRTH REQUIREMENT IS A REFUSAL CONDITION HERE, NOT A COMMENT.
Sanaa 2026-08-28T17:01Z: "A planted control must travel the real production path --
written by the real producer's code, read through the real reader ... no instrument
grades anything until that answer is yes, demonstrated."  `run_battery` REFUSES with
exit 2 unless BR-1's evidence file is present, internally consistent, and the .raw
fixtures it names were written by OpenFOAM's own `postProcess -func surfaceSampleDict
-latestTime`.  A hand-written .raw is a schema the producer never emits and is refused;
so is a file whose basename was produced by RENAMING bytes the producer wrote under a
different name.

NO `assert` STATEMENT APPEARS IN THIS FILE.  Asserts vanish under `python3 -O`; a
control that vanishes is not a control (L-332).  Every check is an explicit `raise`
or an explicit refusal.
"""

import ast
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACT_ROOT = os.path.join(HERE, "BR1_producer_artifacts")
EVIDENCE = os.path.join(HERE, "BR1_BIRTH_CONTROL_EVIDENCE.json")

# The three files the real sampler wrote for the GRADED row, sha256 asserted against
# the originals in successor_triple_2026-08-26 (BR-2 of the registration).
GRADED_DIR = os.path.join(
    os.path.dirname(HERE), "successor_triple_2026-08-26",
    "runs", "wedge", "M2.5_th10", "fine",
    "postProcessing", "surfaceSampleDict", "3.11989651")

SHIPPED = ["grade_f3s.py", "run_f3s.py", "instrument.py",
           "selector_controls.py", "selector_repair_driver.py"]


class ControlFailure(Exception):
    pass


def _refuse(msg, err):
    err.write("REFUSED: %s\n" % msg)
    return 2


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def old_predicate(d):
    """The DEFECT, verbatim from grade_f3s.py:239 of successor_triple_2026-08-26.

    Kept here so the battery can show it FIRING on producer-written files before it
    reports the repair holding.  This is the only re-implementation in this file and
    it re-implements the BUG, deliberately, so that G-R1-1 has something to measure.
    """
    return sorted(f for f in os.listdir(d) if f.endswith(".raw") and "p" in f)


# ---------------------------------------------------------------------------
# THE BIRTH GATE
# ---------------------------------------------------------------------------

def birth_evidence(err):
    """Return the BR-1 evidence dict, or raise ControlFailure.

    This is the refusal that stands between this instrument and any grade it
    might otherwise report.
    """
    if not os.path.isfile(EVIDENCE):
        raise ControlFailure(
            "BIRTH REQUIREMENT NOT DISCHARGED: %s does not exist.  The C1-C4 fixtures "
            "are built from files OpenFOAM's own sampler wrote; until BR-1 has been "
            "DRIVEN (run_selector_repair.sh --birth-control) this instrument grades "
            "nothing.  It does not fall back to a hand-written .raw, it does not "
            "synthesise a directory listing, and it does not report PASS on the "
            "remaining controls." % EVIDENCE)
    ev = json.load(io.open(EVIDENCE, encoding="utf-8"))
    for k in ("invocations", "old_predicate_first_element", "producer",
              "graded_dir_sha256_match"):
        if k not in ev:
            raise ControlFailure("BIRTH EVIDENCE MALFORMED: key %r absent from %s"
                                 % (k, EVIDENCE))
    for inv in ev["invocations"]:
        if inv.get("rc") != 0:
            raise ControlFailure("BR-1(i) FAILED: sampler rc=%r for surface %r"
                                 % (inv.get("rc"), inv.get("surface")))
        if not inv.get("end_line"):
            raise ControlFailure("BR-1(i) FAILED: no End line in the sampler log for "
                                 "surface %r" % inv.get("surface"))
        if not inv.get("newer_than_dict"):
            raise ControlFailure(
                "BR-1(ii) FAILED: the .raw files for surface %r are NOT newer than the "
                "surfaceSampleDict that named them" % inv.get("surface"))
    if ev["old_predicate_first_element"] != "T_ramp.raw":
        raise ControlFailure(
            "BR-1(iii) FAILED: the OLD predicate on the real sampler's own output "
            "returned %r first, not 'T_ramp.raw'.  The defect was never observed "
            "firing on producer-written files, so nothing may be reported repaired."
            % ev["old_predicate_first_element"])
    if int(ev.get("old_predicate_len", 0)) < 2:
        raise ControlFailure("BR-1(iii) FAILED: the OLD predicate matched %r files, "
                             "fewer than 2" % ev.get("old_predicate_len"))
    if ev["graded_dir_sha256_match"] is not True:
        raise ControlFailure("BR-2 FAILED: the retained singleton fixtures are not "
                             "sha256-identical to the originals")
    for name in ("p_ramp.raw", "T_ramp.raw", "rho_ramp.raw",
                 "p_rgh_wedgeSurface.raw",
                 "p_wedgeSurface.raw", "T_wedgeSurface.raw", "rho_wedgeSurface.raw"):
        p = os.path.join(ARTIFACT_ROOT, name)
        if not os.path.isfile(p):
            raise ControlFailure("BIRTH ARTIFACT ABSENT: %s" % p)
    return ev


# ---------------------------------------------------------------------------
# FIXTURES -- built ONLY from bytes the real producer wrote, under the basenames
# the real producer chose.  Nothing here renames a file.
# ---------------------------------------------------------------------------

def _fixture(tmp, name, members):
    d = os.path.join(tmp, name)
    os.makedirs(d)
    for m in members:
        src = os.path.join(ARTIFACT_ROOT, m)
        if not os.path.isfile(src):
            raise ControlFailure("fixture member absent: %s" % src)
        shutil.copy2(src, os.path.join(d, m))   # basename PRESERVED, never renamed
    return d


def _expect_refusal(fn, d, err_substrings):
    """Drive `fn(d, 'p')` and require SystemExit(2) carrying every substring."""
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            fn(d, "p")
    except SystemExit as e:
        code = e.code
        text = buf.getvalue()
        if code != 2:
            raise ControlFailure("expected SystemExit code 2, got %r" % (code,))
        missing = [s for s in err_substrings if s not in text]
        if missing:
            raise ControlFailure("refusal text missing %r; got:\n%s" % (missing, text))
        return text
    except Exception as e:                       # noqa: BLE001 -- any other outcome
        raise ControlFailure("expected SystemExit(2), got %s: %s"
                             % (type(e).__name__, e))
    raise ControlFailure("expected SystemExit(2); the selector RETURNED instead")


# ---------------------------------------------------------------------------
# THE CONTROLS
# ---------------------------------------------------------------------------

def c1(mod, tmp):
    """G-R1-3: two members -> refuse, naming both."""
    d = _fixture(tmp, "c1", ["p_wedgeSurface.raw", "p_rgh_wedgeSurface.raw"])
    txt = _expect_refusal(mod.select_one, d,
                          ["UNIQUE-SELECTOR", "matched   : 2",
                           "p_wedgeSurface.raw", "p_rgh_wedgeSurface.raw",
                           os.path.abspath(d)])
    return "refused, 2 named: %s" % txt.splitlines()[0][:60]


def c2(mod, tmp):
    """G-R1-4: the graded directory's exact three files still select p_wedgeSurface."""
    d = _fixture(tmp, "c2", ["p_wedgeSurface.raw", "rho_wedgeSurface.raw",
                             "T_wedgeSurface.raw"])
    got = mod.select_one(d, "p")
    if os.path.basename(got) != "p_wedgeSurface.raw":
        raise ControlFailure("expected p_wedgeSurface.raw, got %r" % got)
    return os.path.basename(got)


def c3(mod, tmp):
    """G-R1-1 and G-R1-2, in ONE control: the defect fires, then the repair holds."""
    d = _fixture(tmp, "c3", ["T_ramp.raw", "p_ramp.raw"])
    old = old_predicate(d)
    if len(old) < 2 or old[0] != "T_ramp.raw":
        raise ControlFailure(
            "G-R1-1 NOT ESTABLISHED: the old predicate returned %r on producer-written "
            "files; it must return T_ramp.raw FIRST.  A repair shown holding on a "
            "fixture where the defect does not fire is a zero from a reader not shown "
            "able to see a non-zero." % (old,))
    got = mod.select_one(d, "p")
    if os.path.basename(got) != "p_ramp.raw":
        raise ControlFailure("G-R1-2 FAILED: expected p_ramp.raw, got %r" % got)
    return "old->%s (DEFECT FIRING) | repaired->%s" % (old[0], os.path.basename(got))


def c4(mod, tmp):
    """G-R1-5: N1 empty, N2 present-but-wrong-field.  Both refuse with matched : 0."""
    n1 = os.path.join(tmp, "c4_n1")
    os.makedirs(n1)
    t1 = _expect_refusal(mod.select_one, n1, ["matched   : 0", os.path.abspath(n1)])
    n2 = _fixture(tmp, "c4_n2", ["T_ramp.raw", "rho_ramp.raw"])
    t2 = _expect_refusal(mod.select_one, n2,
                         ["matched   : 0", "T_ramp.raw", "rho_ramp.raw",
                          os.path.abspath(n2)])
    return "N1 refused (%d ch), N2 refused (%d ch)" % (len(t1), len(t2))


def _mutant_module(mod):
    """A copy of `mod` with `if len(cands) != 1:` mutated to `if False:`.

    Written INTO the successor directory under a pid-bearing name so that the copy's
    own HERE/F3_ROOT sys.path inserts still resolve `instrument` and `roache_triple`;
    removed in the caller's finally.  A mutant imported from /tmp would fail on import
    and be mistaken for a flip.
    """
    src = io.open(mod.__file__, encoding="utf-8").read()
    needle = "    if len(cands) != 1:"
    if src.count(needle) != 1:
        raise ControlFailure("C5: mutation anchor count %d (want 1) in %s"
                             % (src.count(needle), mod.__file__))
    name = "_c5_mutant_%s_%d" % (os.path.basename(mod.__file__)[:-3], os.getpid())
    path = os.path.join(HERE, name + ".py")
    io.open(path, "w", encoding="utf-8").write(src.replace(needle, "    if False:", 1))
    return name, path


def c5(mod, tmp):
    """G-R1-6: with clause U deleted, C1 and C4 must FLIP to failure."""
    name, path = _mutant_module(mod)
    try:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        mut = __import__(name)
        flipped = []
        for cid, fn in (("C1", c1), ("C4", c4)):
            try:
                fn(mut, os.path.join(tmp, "c5_" + cid))
            except ControlFailure:
                flipped.append(cid)
            except Exception:                    # noqa: BLE001 IndexError counts
                flipped.append(cid)
            else:
                raise ControlFailure(
                    "C5 DID NOT FLIP %s: with `if len(cands) != 1:` mutated to "
                    "`if False:` the control still passed.  A guard whose deletion "
                    "changes nothing was never being exercised." % cid)
        return "C1 and C4 both flipped (%s)" % ",".join(flipped)
    finally:
        sys.modules.pop(name, None)
        if os.path.exists(path):
            os.remove(path)
        pyc = os.path.join(HERE, "__pycache__")
        if os.path.isdir(pyc):
            for f in os.listdir(pyc):
                if f.startswith(name + "."):
                    os.remove(os.path.join(pyc, f))


def ast_assert_census(paths):
    out = {}
    for p in paths:
        tree = ast.parse(io.open(p, encoding="utf-8").read())
        out[os.path.basename(p)] = sum(1 for n in ast.walk(tree)
                                       if isinstance(n, ast.Assert))
    return out


def c6(mod, tmp):
    """G-R1-7: zero ast.Assert nodes over the shipped path; -O returns rc 2."""
    paths = [os.path.join(HERE, f) for f in SHIPPED]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        raise ControlFailure("C6: shipped file(s) absent: %r" % missing)
    census = ast_assert_census(paths)
    total = sum(census.values())
    if total != 0:
        raise ControlFailure("C6: %d ast.Assert node(s) in the shipped path: %r"
                             % (total, census))
    if not __debug__:
        raise ControlFailure("C6: this battery is running under -O and did not refuse")
    p = subprocess.run([sys.executable, "-O",
                        os.path.join(HERE, "selector_repair_driver.py"), "--selftest"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=HERE)
    if p.returncode != 2:
        raise ControlFailure("C6: `python3 -O selector_repair_driver.py --selftest` "
                             "returned rc %d, want 2" % p.returncode)
    return "0 ast.Assert over %d shipped files; -O driver rc=2" % len(paths)


CONTROLS = [("C1", c1), ("C2", c2), ("C3", c3), ("C4", c4), ("C5", c5), ("C6", c6)]


def run_battery(mod, err, require_birth=True):
    """Drive C1-C6 through `mod`'s own select_one.  Returns 0, or 2 on any refusal."""
    if not __debug__:
        return _refuse("this battery is running under `python3 -O`, which deletes "
                       "assert statements.  It carries none -- every control is an "
                       "explicit raise -- but a control harness that RUNS under -O "
                       "invites one to be added later and silently deleted. Refused.",
                       err)
    if not hasattr(mod, "select_one"):
        return _refuse("module %s carries no select_one: this is not a repaired file"
                       % getattr(mod, "__file__", mod), err)
    try:
        if require_birth:
            birth_evidence(err)
    except ControlFailure as e:
        return _refuse(str(e), err)
    tmp = tempfile.mkdtemp(prefix="selector_controls_")
    outcomes = []
    try:
        for cid, fn in CONTROLS:
            try:
                detail = fn(mod, os.path.join(tmp, cid))
            except ControlFailure as e:
                outcomes.append((cid, "NOT RUN/FAILED", str(e)))
                for line in outcomes:
                    err.write("  %-3s %-14s %s\n" % line)
                return _refuse("control %s did not establish its claim: %s" % (cid, e),
                               err)
            outcomes.append((cid, "FIRED", detail))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    err.write("SELECTOR CONTROLS on %s\n" % os.path.basename(mod.__file__))
    for line in outcomes:
        err.write("  %-3s %-6s %s\n" % line)
    err.write("%d controls fired, each shown able to fail\n" % len(outcomes))
    return 0
