#!/usr/bin/env python3
"""MUTATION CONTROLS for build_t20c.py.

WHY THIS EXISTS.  `--selftest` printing PASS proves that the limbs RAN.  It does
not prove that any limb can FAIL, and a limb that cannot fail is not a check --
it is decoration that reports green for exactly as long as nobody looks.  This
harness makes each limb's discriminating power a MEASUREMENT: it plants ONE
defect in a COPY of build_t20c.py, runs that copy's own `--selftest`, and
requires that the limb the defect targets goes red.

It is the same construction as `mutation_controls_t20.py` in this directory,
against a different instrument.  `isolated=True` demands the defect redden its
target AND NOTHING ELSE; `isolated=False` is used only where a defect genuinely
has a wider blast radius, the reason is written into the entry, and the radius
is MEASURED AND PRINTED rather than engineered away.

THE COPY NEVER TOUCHES THE LIVE TREE.  A scratch directory mirroring the
repository's depth is built; the frozen pre-registration, the registered JSON,
the prose-cases file and the two parent builders are SYMLINKED into it (so every
byte the mutant reads is the byte the real producer wrote), `.git` is symlinked
so the mutant's committed-blob check can still resolve, and `GIT_INDEX_FILE` is
pointed at a scratch file so no git call can touch the shared index (CLAUDE.md
rule 10).  Every mutant emits its cases inside its own sandbox.

__pycache__ is cleared before every control run -- a stale bytecode cache
inverts mutation tests, making the clean control fail and the mutated case pass,
and PYTHONDONTWRITEBYTECODE does not fix it.

Exit: 0 all controls behaved, 1 otherwise.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "build_t20c.py")

# (label, targeted limb substring, [(find, replace), ...], isolated)
MUTATIONS = [
    ("M1: the override stops being bound to the ONE registered case -- any case "
     "may be given a planted source, which is the lever to fabricate a planted arm",
     "override requested for T20_LC_c",
     [("        if case != plant.case:\n", "        if False:\n")], False),

    ("M2: the override stops being bound to the registered VALUE -- the caller "
     "chooses the plant, and a 'planted +10 %' arm could carry any number",
     "--planted-source",
     [("        if got != plant.planted:\n", "        if False:\n")], True),

    ("M3: the live-tree interlock is lifted -- the unruled builder emits the "
     "planted case into the rung's own directory",
     "LIVE rung tree",
     [("LIVE_TREE_PLANTED_INTERLOCK = True",
       "LIVE_TREE_PLANTED_INTERLOCK = False")], False),

    ("M4: the dead-lever guard is removed -- the planted case can be built with "
     "no plant at all, byte-identical to the unplanted arm",
     "WITHOUT an override",
     [("    elif case == plant.case:\n", "    elif False:\n")], True),

    ("M5: verify_source stops requiring the planted token -- a case whose source "
     "is an unregistered value passes the fail-closed reader",
     "unregistered value",
     [("    if txt.count(want) != 1:\n", "    if False:\n")], True),

    ("M6: verify_source stops requiring the base token to be GONE -- a case "
     "carrying both 5000 and 5500 passes as a planted arm",
     "planted AND the base token",
     [("    if base_tok in txt:\n", "    if False:\n")], True),

    ("M7: this file's own registration-moved check is removed -- a registration "
     "edited after the parent returned goes unseen",
     "AFTER the parent returned",
     [("        if _sha256(rp) != h:\n", "        if False:\n")], True),

    ("M8: the frozen document stops being hashed against the committed blob -- "
     "an EDITED pre-registration would supply the planted value",
     "one byte off the committed blob",
     [("    if ds != bs:\n", "    if False:\n")], True),

    ("M9: the pinning sentence stops having to be UNIQUE -- a second, different "
     "planted sentence would be silently ignored rather than refused",
     "a SECOND pinning sentence",
     [("    if len(ms) != 1:\n", "    if len(ms) < 1:\n")], True),

    ("M10: the document's own arithmetic stops being checked -- a document "
     "claiming 6000 = 5000 x 1.10 would be believed",
     "document pins 6000",
     [("    if planted != factor * doc_base:\n", "    if False:\n")], True),

    ("M11: the two frozen artifacts stop having to agree -- a document base of "
     "4000 against a registered physics base of 5000 would be believed",
     "document base 4000",
     [("    if doc_base != base:\n", "    if False:\n")], True),

    ("M12: the builder emits ONE extra file -- the 'changes nothing else' claim "
     "is exactly what the paired build exists to falsify",
     "PAIRED (",
     [("    d = os.path.join(root, case)\n    if planted_source is None:\n",
       "    d = os.path.join(root, case)\n"
       "    open(os.path.join(d, 'EXTRA'), 'w').close()\n"
       "    if planted_source is None:\n")], True),
]


def build_sandbox(tmp, source_text):
    d = os.path.join(tmp, "verification", "runs", "T-family", "T20_runs")
    os.makedirs(d)
    os.makedirs(os.path.join(tmp, "docs", "campaigns", "T-family"))
    os.symlink(os.path.join(REPO, "docs", "campaigns", "T-family",
                            "T20_PREREGISTRATION.md"),
               os.path.join(tmp, "docs", "campaigns", "T-family",
                            "T20_PREREGISTRATION.md"))
    # The mutant resolves the committed blob through git; the object database is
    # the real one and every call made is read-only (rev-parse, cat-file).
    os.symlink(os.path.join(REPO, ".git"), os.path.join(tmp, ".git"))
    for f in ("T20_registered.json", "T20_prose_cases_7b93b2c8.json",
              "build_t20.py", "build_t20b.py"):
        os.symlink(os.path.join(HERE, f), os.path.join(d, f))
    p = os.path.join(d, "build_t20c.py")
    open(p, "w").write(source_text)
    return p


def failing_limbs(out):
    return [ln.strip()[7:] for ln in out.splitlines()
            if ln.strip().startswith("[FAIL]")]


def run_selftest(source_text):
    tmp = tempfile.mkdtemp(prefix="t20cmut_")
    try:
        p = build_sandbox(tmp, source_text)
        for root, dirs, _f in os.walk(tmp):
            for dd in list(dirs):
                if dd == "__pycache__":
                    shutil.rmtree(os.path.join(root, dd), ignore_errors=True)
        shutil.rmtree(os.path.join(HERE, "__pycache__"), ignore_errors=True)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                   GIT_INDEX_FILE=os.path.join(tmp, "scratch_git_index"))
        r = subprocess.run([sys.executable, "-B", p, "--selftest"],
                           capture_output=True, text=True, timeout=1800, env=env)
        return r.returncode, r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    clean = open(SRC).read()
    print("MUTATION CONTROLS for build_t20c.py")
    print("=" * 78)
    rc, out = run_selftest(clean)
    base_fails = failing_limbs(out)
    ok0 = (rc == 0 and not base_fails)
    print("[%s] CONTROL (unmutated, in the sandbox): SELFTEST rc=%d, %d failing "
          "limbs" % ("ok  " if ok0 else "FAIL", rc, len(base_fails)))
    if not ok0:
        print("      the clean control does not pass in the sandbox; every "
              "mutation result below would be uninterpretable.")
        for f in base_fails[:8]:
            print("      %s" % f)
        sys.stdout.write(out[-3000:])
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
            print("[FAIL] %2d  mutation did not apply -- the anchor is gone from "
                  "the source, so this control measures nothing: %s" % (i, label))
            bad += 1
            continue
        rc, out = run_selftest(src)
        reds = failing_limbs(out)
        hit = [f for f in reds if target in f]
        others = [f for f in reds if target not in f]
        good = (len(hit) >= 1) and (not others or not isolated)
        crashed = "Traceback" in out
        state = "ok  " if (good and not crashed) else "FAIL"
        print("[%s] %2d  rc=%-3s %-4d  %s" % (state, i, rc, len(reds),
                                              label.split(" -- ")[0]))
        print("            targeted: %s%s" % (target, "" if isolated else
              "   [isolation NOT required -- see the label]"))
        if not isolated and others:
            print("            blast radius, MEASURED: %d other limbs also red"
                  % len(others))
            for f in others[:4]:
                print("              also red: %s" % f[:100])
        if not good or crashed:
            bad += 1
            if crashed:
                print("            MUTANT CRASHED rather than reddening a limb")
            if not hit:
                print("            THE TARGETED LIMB DID NOT GO RED -- it is "
                      "decoration, not a check")
            for f in others[:5]:
                print("            also red (the limb set is entangled): %s"
                      % f[:110])
    print("-" * 78)
    print("MUTATION CONTROLS %s (%d of %d misbehaved)"
          % ("PASS" if not bad else "FAIL", bad, len(MUTATIONS)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
