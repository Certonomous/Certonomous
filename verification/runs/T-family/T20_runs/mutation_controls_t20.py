#!/usr/bin/env python3
"""MUTATION CONTROLS for analyse_t20.py.

WHY THIS EXISTS.  `--selftest` printing PASS proves that the limbs RAN.  It does
not prove that any limb can FAIL, and a limb that cannot fail is not a check --
it is decoration that reports green for exactly as long as nobody looks.  This
harness makes each limb's discriminating power a MEASUREMENT: it plants ONE
defect in a COPY of analyse_t20.py, runs that copy's own `--selftest`, and
requires that the limb the defect targets goes red AND THAT NO OTHER LIMB DOES.

A mutation that reddens nothing means the limb is decoration.  A mutation that
reddens everything means the limb set is entangled and no single limb is
diagnostic.  Both are failures here.

ONE EXCEPTION, DECLARED RATHER THAN HIDDEN.  A defect in a quantity that is
load-bearing for the RUNG verdict cannot be isolated to one limb, because taking
the rung down is the correct behaviour.  Such an entry carries `isolated=False`
with its reason written into its own label, and its blast radius is MEASURED and
PRINTED.  Exactly one entry uses it.

THE COPY NEVER TOUCHES THE LIVE TREE.  A scratch directory mirroring the
repository's depth is built, the frozen pre-registration, the two pinned
instruments and scripts/ are SYMLINKED into it (so the sha256 pins still hold on
identical bytes), and the mutated comparator runs entirely inside it.  The live
verification/runs/T-family/T20_runs/ is neither read nor written by any mutation.

__pycache__ is cleared before every control run -- a stale bytecode cache inverts
mutation tests, making the clean control fail and the mutated case pass, and
PYTHONDONTWRITEBYTECODE does not fix it.

Exit: 0 all controls behaved, 1 otherwise.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "analyse_t20.py")

# (label, targeted limb substring, [(find, replace), ...], isolated)
# Each entry plants exactly ONE DEFECT -- which is sometimes one edit and sometimes
# two edits that together are one coherent wrong patch.  The "targeted limb" is
# matched against the `[FAIL]` lines the mutated selftest prints.
#
# `isolated` is normally True: the defect must redden its target AND NOTHING ELSE,
# because a limb that only goes red alongside twenty others is not diagnostic.
# It is set False, WITH A WRITTEN REASON, where a defect is genuinely load-bearing
# for the rung verdict and therefore CANNOT be isolated.  Forcing such a defect
# into a one-limb shape would misrepresent its real blast radius, so the radius is
# MEASURED AND PRINTED instead of engineered away.
MUTATIONS = [
    ("S0a: the row set stops being checked against section 12 -- V5 dropped from the "
     "implemented set, which is the 5/6 trap in its purest form",
     "S0a the implemented row set",
     [('GATED_ROW_IDS = ["V1", "V2", "V3", "V4", "V5", "P1", "P2", "P3", "P4"]',
       'GATED_ROW_IDS = ["V1", "V2", "V3", "V4", "P1", "P2", "P3", "P4"]')], True),

    ("V5-ABSENT: the comparator QUIETLY SKIPS a case that is not on disk and then INVENTS "
     "the planted arm's result -- the dead-lever-to-clean-sheet failure, written out as the "
     "two-line patch that would actually cause it",
     "V5 ABSENT",
     [("    for case in sorted(FROZEN_CASES):\n        ok, bad, det = completion(",
       "    for case in sorted(FROZEN_CASES):\n        if not os.path.isdir(os.path.join("
       "root, case)):\n            continue\n        ok, bad, det = completion("),
      ("    if balp is None:\n        not_a_result(",
       "    if balp is None:\n        balp = dict(C=bal[\"C\"] + 0.10)\n    if False:\n"
       "        not_a_result(")], True),

    ("S1: the band becomes ONE-SIDED, so a negative drift can never fail it",
     "S1 -1.5 x band",
     [('bv = "PASS" if lo <= value <= hi else "GATE FAIL"',
       'bv = "PASS" if value <= hi else "GATE FAIL"')], True),

    ("S2: clause 4 stops refusing a BLIND reader",
     "S2 BLIND reader",
     [("            if floor is None:                                               # clause 4",
       "            if False:                                                       # clause 4")],
     True),

    ("S3: the negative arm gains an absolute tolerance, which is precisely T3's defect",
     "S3 NOISY reader",
     [("            if dneg != 0.0:", "            if dneg > 1e-13:")], True),

    ("S4: clause 5's plant sizing is relaxed to zero, so an undersized plant passes",
     "S4 UNDERSIZED plant",
     [('G["plant_sizing_frac"] = float(m.group(1))',
       'G["plant_sizing_frac"] = 0.0')], True),

    ("S5b: clause 8's floor ceiling is loosened past every ladder magnitude",
     "S5b writePrecision 6",
     [('if floor > GATES["floor_max_K"]:                                # clause 8',
       'if floor > 1.0e3:                                               # clause 8')], True),

    ("S6a: the balance instrument returns unity BY CONSTRUCTION -- a reader that cannot see "
     "the planted 10 %.  NOT ISOLATED, and the reason is structural rather than a defect in "
     "the limb set: C is load-bearing for the RUNG verdict through V5, whose refusal section "
     "12 makes fatal, so a broken balance instrument correctly takes the whole rung down with "
     "it.  The blast radius is measured and printed rather than engineered away",
     "S6a a forged pair",
     [('    return dict(C=(e_stored + e_conv) / e_src, E_src=e_src, E_stored=e_stored,',
       '    return dict(C=1.0, E_src=e_src, E_stored=e_stored,')], False),

    ("S7 STRICTNESS: the AGE GUARD accepts a field the SAME AGE as 0/T instead of strictly "
     "newer.  This mutation is the reason the strictness arm exists: against the OLDER-field "
     "arm alone it changed nothing and passed unnoticed",
     "conjunct 6 STRICTNESS",
     [("                if not tf > t0:", "                if not tf >= t0:")], True),

    ("EXACT: an EXACT triple is treated as gradeable, which is rule 5 clause (2) deleted",
     "an EXACT temporal triple",
     [('    if tr is not None and tr["state"] != "CONVERGING":',
       '    if tr is not None and tr["state"] not in ("CONVERGING", "EXACT"):')], True),

    ("SEPARATION (a): a PREDICTION is read inside the gating path, silently converting an "
     "expectation into a gate",
     "GATE/PREDICTION separation (a)",
     [('    bv = "PASS" if lo <= value <= hi else "GATE FAIL"',
       '    _p = PREDICTIONS\n    bv = "PASS" if lo <= value <= hi else "GATE FAIL"')], True),

    ("SEPARATION (b): the prediction reporter reads a GATE",
     "GATE/PREDICTION separation (b)",
     [('    for rowid, q, i in R_ROWS:\n        t = SAMPLE_TIMES[i - 1]',
       '    _g = GATES\n    for rowid, q, i in R_ROWS:\n        t = SAMPLE_TIMES[i - 1]')],
     True),

    ("S8a: a limb outcome becomes nondeterministic, so the empty and populated passes stop "
     "agreeing",
     "S8a INVARIANCE",
     [('    fails, probe = [], []\n',
       '    fails, probe = [], []\n    probe.append(("nondet", id(object())))\n')], True),

    ("S8c: a limb reads the LIVE run tree -- analyse_t18.py's exact defect",
     "S8c: NO limb read anything",
     [('    fails, probe = [], []\n',
       '    fails, probe = [], []\n    try:\n        open(os.path.join(os.path.dirname('
       'os.path.abspath(__file__)), "T20_LC_f", "CASE.txt")).read()\n'
       '    except OSError:\n        pass\n')], True),

    ("S8d: the name HERE appears inside the selftest functions",
     "S8d: `HERE` references",
     [('    fails, probe = [], []\n',
       '    fails, probe = [], []\n    probe.append(("here", HERE is not None))\n')], True),
]


def build_sandbox(tmp, source_text):
    d = os.path.join(tmp, "verification", "runs", "T-family", "T20_runs")
    os.makedirs(d)
    os.makedirs(os.path.join(tmp, "docs", "campaigns", "T-family"))
    os.symlink(os.path.join(REPO, "docs", "campaigns", "T-family", "T20_PREREGISTRATION.md"),
               os.path.join(tmp, "docs", "campaigns", "T-family", "T20_PREREGISTRATION.md"))
    os.symlink(os.path.join(REPO, "scripts"), os.path.join(tmp, "scripts"))
    for f in ("T20_registered.json", "T20_prose_cases_7b93b2c8.json"):
        os.symlink(os.path.join(HERE, f), os.path.join(d, f))
    p = os.path.join(d, "analyse_t20.py")
    open(p, "w").write(source_text)
    return p


def failing_limbs(out):
    """ONLY the printed `[FAIL]` lines.

    The trailing `SELFTEST FAIL (n failed): a; b` summary repeats the SAME limbs
    under their short labels, and counting both made one red limb look like two --
    which reported entanglement where there was none.  The limb set is read from
    the printed lines, which is the one place each failure appears exactly once
    per pass (twice overall, since S8a runs the whole set twice by registration)."""
    return [ln.strip()[7:] for ln in out.splitlines() if ln.strip().startswith("[FAIL]")]


def run_selftest(source_text):
    tmp = tempfile.mkdtemp(prefix="t20mut_")
    try:
        p = build_sandbox(tmp, source_text)
        for root, dirs, _f in os.walk(REPO if False else tmp):
            for dd in list(dirs):
                if dd == "__pycache__":
                    shutil.rmtree(os.path.join(root, dd), ignore_errors=True)
        shutil.rmtree(os.path.join(REPO, "scripts", "__pycache__"), ignore_errors=True)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, p, "--selftest"], capture_output=True, text=True,
                           timeout=2400, env=env)
        return r.returncode, r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    clean = open(SRC).read()
    print("MUTATION CONTROLS for analyse_t20.py")
    print("=" * 78)
    rc, out = run_selftest(clean)
    base_fails = failing_limbs(out)
    ok0 = (rc == 0 and not base_fails)
    print("[%s] CONTROL (unmutated, in the sandbox): SELFTEST rc=%d, %d failing limbs"
          % ("ok  " if ok0 else "FAIL", rc, len(base_fails)))
    if not ok0:
        print("      the clean control does not pass in the sandbox; every mutation result "
              "below would be uninterpretable.")
        for f in base_fails[:8]:
            print("      %s" % f)
        return 1

    bad = 0
    print("")
    print("%-3s %-6s %-6s  %s" % ("#", "rc", "reds", "mutation -> targeted limb"))
    print("-" * 78)
    for i, (label, target, edits, isolated) in enumerate(MUTATIONS, start=1):
        src = clean
        applied = 0
        for find, repl in edits:
            if find not in src:
                break
            src = src.replace(find, repl, 1)
            applied += 1
        if applied != len(edits):
            print("[FAIL] %2d  mutation did not apply -- the anchor is gone from the source, so "
                  "this control measures nothing: %s" % (i, label))
            bad += 1
            continue
        rc, out = run_selftest(src)
        reds = failing_limbs(out)
        hit = [f for f in reds if target in f]
        others = [f for f in reds if target not in f]
        good = (len(hit) >= 1) and (not others or not isolated)
        crashed = "Traceback" in out
        state = "ok  " if (good and not crashed) else "FAIL"
        print("[%s] %2d  rc=%-3s %-4d  %s" % (state, i, rc, len(reds), label.split(" -- ")[0]))
        print("            targeted: %s%s" % (target, "" if isolated else
              "   [isolation NOT required -- see the label]"))
        if not isolated and others:
            print("            blast radius, MEASURED: %d other limbs also red" % len(others))
        if not good or crashed:
            bad += 1
            if crashed:
                print("            MUTANT CRASHED rather than reddening a limb")
            if not hit:
                print("            THE TARGETED LIMB DID NOT GO RED -- it is decoration, not a "
                      "check")
            for f in others[:5]:
                print("            also red (the limb set is entangled): %s" % f[:110])
    print("-" * 78)
    print("MUTATION CONTROLS %s (%d of %d misbehaved)"
          % ("PASS" if not bad else "FAIL", bad, len(MUTATIONS)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
