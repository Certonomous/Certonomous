#!/usr/bin/env python3
"""Curriculum D6RF4 -- THE LAUNCHER-GUARD DRIVE, AND IT IS BUILT TO SURVIVE THE
FREEZE.

THE PROBLEM THIS FILE EXISTS FOR, and it is not hypothetical -- it cost the
`W3S` item three rounds on 2026-09-05.  **EVERY FREEZE ACT DESTROYS THE CONTROLS
WHOSE PREMISE IS THE PRE-FREEZE VALUE.**  On `W3S` two acts killed three
controls in sequence, each discovered only after the previous was repaired, and
the fourth instance was not a control at all: it was the launcher's own first
screen, still asserting *"IT LAUNCHES NOTHING"* on a file that could by then
start a container.

So no control here reads the LIVE `PERMISSION`.  Every direction PLANTS its
value into a MUTATED COPY of `d6rf4_run_arm.sh` and checks the **REASON TOKEN,
NOT THE RC** -- so each one fires identically before and after the freeze, and
the drive is worth re-running the moment the field is filled.

WHY THE REASON TOKEN AND NOT THE RC.  `d6rf4_run_arm.sh` returns `3` for
G-FREEZE, for G-FREEZE-UNIQUE, for G-FREEZE-SHAPE, for G-ROOT and for G-ANCHOR.
An rc-3 assertion would pass on a copy that never reached the gate under test
and would report a guard as working while a different guard did the work.  That
is `L-493`'s shape -- a control that tests for PRESENCE is satisfied by the
right answer arriving by the WRONG ROUTE -- so each direction asserts the token
its own gate prints.

THE ZERO-COMPUTE PROPERTY IS A PROPERTY OF THE FIXTURE, NOT OF `PERMISSION`.
This is the one that nearly bit `W3S`: its selftest's zero-compute guarantee
rested on a disabled flag, so raising the flag would have started containers had
the fixture not independently put a refusal ahead of every `docker run`.  Here
`neuter()` inserts a refusal ahead of EVERY container-touching line of every
copy it makes, and ASSERTS its own insertion count -- a neutering that neutered
nothing is a planted zero.  Direction 2 then SHOWS that refusal firing, so the
fixture's safety is demonstrated rather than asserted.

AND THE OTHER DRIVES ARE SWEPT TOO (direction 7).  `d6rf4_grade_drive.py`,
`d6rf4_finiteness_mutation.py`, `d6rf4_accept_floor_control.py` and the rest
carry zero-compute claims in their own docstrings.  Those claims rest on the
fixtures and NOT on `PERMISSION`, and direction 7 asserts that mechanically, by
`ast`, rather than leaving a reader to take the docstrings' word for it.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python -O` deletes them.
"""
import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LAUNCHER = os.path.join(HERE, "d6rf4_run_arm.sh")
PLACEHOLDER = "NOT_FROZEN"
# THE FIXTURE SHAS ARE READ FROM GIT, because the launcher's resolution limb
# asks git whether the value names a commit whose tree CONTAINS this item's
# pre-registration.  A hard-coded fixture value could not exercise that limb in
# either direction, and a control that cannot reach the gate it names is not a
# control (L-493).
REPO = "/home/ubuntu/Certonomous"
PREREG = "cases/dafoam/ladder-a/A2/curriculum_D6RF4/PREREGISTRATION.md"


def _git(*a):
    r = subprocess.run(["git", "-C", REPO, *a], stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL, text=True)
    return r.returncode, r.stdout.strip()


def _fixture_shas():
    """(a real commit CARRYING the prereg, its 8-char abbreviation, a real
    commit NOT carrying it, a hex value that names no commit)."""
    _, carrying = _git("log", "-1", "--format=%H", "--", PREREG)
    _, no_carry = _git("rev-list", "-1", "--max-parents=0", "HEAD")
    return carrying, carrying[:8], no_carry, "0" * 40


CARRYING, CARRYING_ABBREV, NOT_CARRYING, NO_SUCH = None, None, None, None
FIXTURE_SHA = None
PERM_RE = re.compile(r'^PERMISSION=.*$', re.M)
# Lines that can touch a container.  `sudo` is included because every docker
# call in this launcher goes through it, and a future line might not say
# "docker" at all.
DANGER_RE = re.compile(r'^(?!\s*#).*(\bdocker\b|^\s*sudo\b|\bsudo -n\b)', re.M)
FIXTURE_REFUSAL = "D6RF4_FIXTURE_REFUSAL"

# The drives whose docstrings carry a zero-compute claim, and the call shapes
# that would falsify it.
DRIVES = ("d6rf4_grade_drive.py", "d6rf4_finiteness_mutation.py",
          "d6rf4_accept_floor_control.py", "d6rf4_cd_plant_control.py",
          "d6rf4_anchor_gate.py", "d6rf4_endpoint_locus.py",
          "d6rf4_units_assert.py", "d6rf4_grade.py",
          "d6rf4_instrument_table_extraction.py")
DANGER_TOKENS = ("docker", "mpirun", "run_arm", "_cmd.sh", "sudo")


def neuter(dst, permission):
    """Write a copy of the launcher with `PERMISSION` planted AND every
    container-touching line refused ahead of time.

    Returns (n_perm, n_neutered).  BOTH counts are asserted by the caller:
    a plant that planted nothing and a neutering that neutered nothing are the
    same failure, and both would make this drive report success for the wrong
    reason (CLAUDE.md rule 3)."""
    src = open(LAUNCHER, errors="replace").read()
    n_perm = len(PERM_RE.findall(src))
    out = PERM_RE.sub("PERMISSION=%s" % permission, src)
    lines, n_neut = out.split("\n"), 0
    guarded = []
    for ln in lines:
        if DANGER_RE.match(ln):
            indent = ln[:len(ln) - len(ln.lstrip())]
            guarded.append(
                '%secho "%s this is a NEUTERED FIXTURE COPY; the next line '
                'would touch a container. No container is ever created by this '
                'drive."' % (indent, FIXTURE_REFUSAL))
            guarded.append("%sexit 90" % indent)
            n_neut += 1
        guarded.append(ln)
    with open(dst, "w") as fh:
        fh.write("\n".join(guarded))
    os.chmod(dst, 0o755)
    return n_perm, n_neut


def run(path, *argv):
    r = subprocess.run(["bash", path, *argv], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, timeout=180)
    return r.returncode, r.stdout


def check(label, ok, detail):
    print("  %-5s %-58s %s" % ("OK" if ok else "FAIL", label, detail))
    return 0 if ok else 1


def main():
    global CARRYING, CARRYING_ABBREV, NOT_CARRYING, NO_SUCH, FIXTURE_SHA
    CARRYING, CARRYING_ABBREV, NOT_CARRYING, NO_SUCH = _fixture_shas()
    FIXTURE_SHA = CARRYING
    tmp = tempfile.mkdtemp(prefix="d6rf4_guard_")
    rc = 0
    print("D6RF4 LAUNCHER-GUARD DRIVE -- EVERY DIRECTION ON A NEUTERED COPY")
    print("  the live PERMISSION is NEVER read by a control here, so every")
    print("  direction below fires identically BEFORE and AFTER the freeze")
    print("  launcher %s" % LAUNCHER)

    # ---- direction 0: the plant and the neutering both bit ----------------
    p_ph = os.path.join(tmp, "run_arm.PLACEHOLDER.sh")
    n_perm, n_neut = neuter(p_ph, PLACEHOLDER)
    rc |= check("direction 0  the PLANT bit: ^PERMISSION= sites rewritten",
                n_perm == 1, "sites=%d (exactly 1 required -- a second "
                             "assignment silently wins in shell)" % n_perm)
    rc |= check("direction 0  the NEUTERING bit: container lines refused",
                n_neut >= 1, "sites=%d (>=1 required; a neutering that "
                             "neutered nothing is a planted zero)" % n_neut)

    # ---- direction 1: the placeholder MUST refuse, by its own token -------
    r1, o1 = run(p_ph, "P_conv", "dafoam-idwarp-rot:v1")
    rc |= check("direction 1  PERMISSION=NOT_FROZEN -> ABORT G-FREEZE",
                "ABORT G-FREEZE this item is NOT FROZEN" in o1
                and FIXTURE_REFUSAL not in o1,
                "token seen=%s  rc=%d  reached_no_container_line=%s"
                % ("ABORT G-FREEZE this item is NOT FROZEN" in o1, r1,
                   FIXTURE_REFUSAL not in o1))

    # ---- direction 2: a FILLED sha must NOT trip G-FREEZE -----------------
    # ... and must instead reach the fixture's own refusal, which is what
    # DEMONSTRATES that the zero-compute property belongs to the fixture and
    # not to PERMISSION.  This is the W3S near-miss, driven.
    p_ok = os.path.join(tmp, "run_arm.FILLED.sh")
    neuter(p_ok, FIXTURE_SHA)
    r2, o2 = run(p_ok, "P_conv", "dafoam-idwarp-rot:v1")
    rc |= check("direction 2  a 40-hex PERMISSION -> G-FREEZE does NOT fire",
                "ABORT G-FREEZE" not in o2 and "D6RF4_G_FREEZE_PASS" in o2,
                "G_FREEZE_PASS=%s  rc=%d"
                % ("D6RF4_G_FREEZE_PASS" in o2, r2))
    rc |= check("direction 2  and the FIXTURE's refusal is what stops it",
                FIXTURE_REFUSAL in o2,
                "the neutered copy hit a container-touching line and REFUSED "
                "there -- so the drive's zero-compute property rests on the "
                "FIXTURE, not on PERMISSION")

    # ---- direction 3: a malformed field must refuse on SHAPE --------------
    # THE LIMB THAT SURVIVES THE FREEZE.  Once the placeholder is replaced,
    # direction 1's limb can never fire again; this one still can.
    for bad, why in (("main", "a branch name"),
                     ("2026-09-06", "a date"),
                     ("", "an empty edit"),
                     ("abc123", "a 6-char paste, under git's own minimum"),
                     ("Z" + FIXTURE_SHA[1:], "40 chars but not hex")):
        p_bad = os.path.join(tmp, "run_arm.BAD_%s.sh" % (bad or "empty"))
        neuter(p_bad, bad)
        r3, o3 = run(p_bad, "P_conv", "dafoam-idwarp-rot:v1")
        rc |= check("direction 3  PERMISSION=%-12r (%s) -> ABORT G-FREEZE-SHAPE"
                    % (bad, why),
                    "ABORT G-FREEZE-SHAPE" in o3 and FIXTURE_REFUSAL not in o3,
                    "rc=%d" % r3)

    # ---- direction 3b: the RESOLUTION limb, both ways ---------------------
    # A shape check only proves the field LOOKS like a sha.  Rule 2 wants the
    # pre-registration COMMITTED, so these two exercise the limb that asks git.
    for sha, label, want in (
            (CARRYING_ABBREV,
             "an 8-char abbreviation of a commit CARRYING the prereg "
             "(D6RF3's own convention: PERMISSION=bc0e687e)", None),
            (NO_SUCH, "40 hex naming NO commit", "ABORT G-FREEZE-SHA"),
            (NOT_CARRYING,
             "a REAL commit whose tree does NOT carry the prereg",
             "ABORT G-FREEZE-SHA")):
        p = os.path.join(tmp, "run_arm.RES_%s.sh" % sha[:8])
        neuter(p, sha)
        r, o = run(p, "P_conv", "dafoam-idwarp-rot:v1")
        if want is None:
            ok = "D6RF4_G_FREEZE_PASS" in o and "ABORT G-FREEZE" not in o
            detail = "G_FREEZE_PASS=%s rc=%d -- a 40-only check would have "
            detail = (detail % (ok, r)) + "REFUSED THE CORRECT ACT"
        else:
            ok = want in o and FIXTURE_REFUSAL not in o
            detail = "rc=%d" % r
        rc |= check("direction 3b PERMISSION=%s.. %s" % (sha[:8], label), ok,
                    detail)

    # ---- direction 4: a DUPLICATE assignment must refuse ------------------
    # Defect (c)'s own shape, planted: in shell the LAST assignment wins.
    p_dup = os.path.join(tmp, "run_arm.DUP.sh")
    neuter(p_dup, FIXTURE_SHA)
    txt = open(p_dup).read().replace(
        "PERMISSION=%s" % FIXTURE_SHA,
        "PERMISSION=%s\nPERMISSION=%s" % (FIXTURE_SHA, PLACEHOLDER), 1)
    open(p_dup, "w").write(txt)
    r4, o4 = run(p_dup, "P_conv", "dafoam-idwarp-rot:v1")
    rc |= check("direction 4  PERMISSION assigned TWICE -> ABORT "
                "G-FREEZE-UNIQUE",
                "ABORT G-FREEZE-UNIQUE" in o4 and FIXTURE_REFUSAL not in o4,
                "rc=%d -- the stale second assignment would otherwise have won "
                "silently" % r4)

    # ---- direction 5: G-ACCEPT-FLOOR's host-side half, both ways ----------
    p_np = os.path.join(tmp, "run_arm.NO_PLANT.sh")
    src = open(p_ok, errors="replace").read()
    open(p_np, "w").write("\n".join(
        l for l in src.split("\n") if "PLANTED CONTROL, DO NOT REMOVE" not in l))
    r5a, o5a = run(p_np, "P_conv", "dafoam-idwarp-rot:v1")
    rc |= check("direction 5  G-ACCEPT-FLOOR plant REMOVED -> refuses "
                "NOT SEEN",
                "the planted control was NOT SEEN" in o5a,
                "rc=%d -- a zero from a reader not shown able to see a "
                "non-zero is not evidence" % r5a)
    p_drift = os.path.join(tmp, "run_arm.DRIFT.sh")
    open(p_drift, "w").write(src.replace(
        "ACCEPT_FLOOR_PLANT_TAG=ACCEPT_FLOOR_PLANT",
        'DA_OPT_OVERRIDE="primalMinResTolDiff 1e12;"\n'
        "ACCEPT_FLOOR_PLANT_TAG=ACCEPT_FLOOR_PLANT", 1))
    r5b, o5b = run(p_drift, "P_conv", "dafoam-idwarp-rot:v1")
    rc |= check("direction 5  a REAL accept-floor assignment -> refuses and "
                "NAMES it",
                "this launcher SETS primalMinResTol" in o5b
                and "primalMinResTolDiff 1e12" in o5b,
                "rc=%d -- the offending line is printed, not merely counted"
                % r5b)

    # ---- direction 6: the LIVE launcher's own invariants ------------------
    live = open(LAUNCHER, errors="replace").read()
    n_live = len(PERM_RE.findall(live))
    rc |= check("direction 6  the LIVE launcher assigns PERMISSION exactly once",
                n_live == 1, "assignments=%d" % n_live)
    rc |= check("direction 6  the LIVE launcher offers NO environment bypass",
                "I_AM_THE_SUPERVISOR" not in live and "D6RF4_FORCE" not in live,
                "an env hatch would let any caller launch an unfrozen item, and "
                "this lane's own first draft of this drive USED one")
    m = PERM_RE.search(live)
    print("       LIVE VALUE, REPORTED AND NOT ASSERTED: %s"
          % (m.group(0) if m else "NOT FOUND"))
    print("       (this line is a READING, not a control -- the controls above "
          "all ran on copies)")

    # ---- direction 7: the OTHER drives' zero-compute claims, asserted -----
    print("  --- direction 7: every drive's zero-compute claim, by ast --------")
    for n in DRIVES:
        p = os.path.join(HERE, n)
        if not os.path.isfile(p):
            rc |= check("direction 7  %s" % n, False, "ABSENT")
            continue
        bad = []
        for node in ast.walk(ast.parse(open(p, errors="replace").read())):
            if not isinstance(node, ast.Call):
                continue
            fn = ast.unparse(node.func)
            if not fn.startswith(("subprocess.", "os.system", "os.popen",
                                  "os.exec", "os.spawn")):
                continue
            txt = ast.unparse(node).replace("\n", " ")
            if any(d in txt for d in DANGER_TOKENS):
                bad.append("%d:%s" % (node.lineno, txt[:90]))
        rc |= check("direction 7  %-38s reaches no container" % n,
                    not bad, "clean" if not bad else "; ".join(bad))
    print("       Nothing above depends on PERMISSION: these drives never")
    print("       invoke the launcher at all, so filling the freeze field")
    print("       cannot make any of them start a container.")

    print("\n  RESULT %s" % ("ALL DIRECTIONS AS REGISTERED" if rc == 0
                             else "NOT AS REGISTERED"))
    print("  solver core-minutes spent by this drive: 0.000 -- every launcher "
          "copy is neutered before it is run, and direction 2 SHOWS that "
          "neutering firing")
    shutil.rmtree(tmp, ignore_errors=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
