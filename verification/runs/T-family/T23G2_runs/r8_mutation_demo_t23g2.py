"""R8 MUTATION DEMONSTRATION -- the positive control is shown able to FAIL.

VERIFICATION_CHARTER.md section 2p.7, limb (d): "A TEST THAT EXERCISES A
REDUNDANT COPY OF THE GUARDED LOGIC TESTS NOTHING... THE TEST FOR LIMB (d) IS
MUTATION OF THE PRODUCTION PATH SPECIFICALLY: mutate the line that RUNS and
require the suite to fail.  A suite that survives a mutation of production code
is not testing production code."

WHAT THIS DOES.  For each mutation it copies the SHIPPED comparator to a scratch
tree, applies ONE literal patch to a line R8 actually shipped -- asserting the
patch text occurs EXACTLY ONCE, so a mutation that no longer applies RAISES
rather than silently passing -- and re-runs r8_gate_control_t23g2.py against the
copy.  THE SUITE MUST GO RED.  A mutation the suite survives is a measured blind
spot and is printed as SURVIVED, never smoothed over.

M0 IS THE NEGATIVE ARM AND IT IS NOT OPTIONAL.  An UNMUTATED copy is run through
exactly the same copy-and-drive machinery and MUST come back GREEN.  Without it,
"the suite went red" could be an artifact of the copying rather than of the
mutation, which is section 2p's own shape.

__pycache__ IS CLEARED BEFORE EVERY RUN.  Stale bytecode has inverted a mutation
test in this lab before: a clean control failing and a mutated case passing.

IT GRADES NOTHING and it never writes to the production tree.  The production
comparator's sha256 is taken before and after the whole run and asserted equal.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

REPO = "/home/ubuntu/Certonomous"
SRC = os.path.join(REPO, "docs/campaigns/T-family")
CONTROL = os.path.join(REPO, "verification/runs/T-family/T23G2_runs",
                       "r8_gate_control_t23g2.py")
COPIED = ("analyse_t23g2.py", "t23g_readonly_diagnosis.py")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


PRODUCTION_SHA_BEFORE = sha(os.path.join(SRC, "analyse_t23g2.py"))

# (id, what R8 line it breaks, old, new, the controls expected to flip)
MUTATIONS = [
    ("M1", "limb 1 never fires (section 2d.10 licensing clause removed)",
     "    if bad_it or bad_pl:\n        grounds.append(",
     "    if False:\n        grounds.append(",
     "1, 5, 6"),
    ("M2", "limb 2 never fires (section 2p degenerate-path ground removed)",
     "    if iter_change <= 0.0:\n        grounds.append(",
     "    if False:\n        grounds.append(",
     "1, 4"),
    ("M3", "DIRECTION INVERTED -- the voided cell returns PASS again",
     '        return "NOT A RESULT", would_be, smallest, grounds',
     '        return "PASS", would_be, smallest, grounds',
     "1, 4, 5, 6"),
    ("M4", "RATIO_MIN made inert in the comparison R8 left untouched",
     '    return (("PASS" if ratio >= RATIO_MIN else "GATE FAIL")',
     '    return (("PASS" if ratio >= 0.0 else "GATE FAIL")',
     "3"),
    ("M5", "R5's planted-zero refusal removed",
     '        if control is None:\n            refuse("G-RATIO would PASS',
     '        if control is None and False:\n            refuse("G-RATIO would PASS',
     "9 ONLY -- control 8 CANNOT see this one, and that is why 9 exists"),
    ("M6", "step-(a)-unevaluable refusal removed, states silently defaulted",
     '    if iterative_states is None:\n        refuse("G-RATIO: no iterative',
     '    if iterative_states is None:\n        iterative_states = {}\n'
     '    if False:\n        refuse("G-RATIO: no iterative',
     "7"),
]


def clear_pycache(root):
    for dirpath, dirnames, _ in os.walk(root):
        for d in list(dirnames):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(dirpath, d), ignore_errors=True)
                dirnames.remove(d)


def run_control(cmp_dir):
    clear_pycache(cmp_dir)
    clear_pycache(os.path.join(REPO, "scripts"))
    env = dict(os.environ, T23G2_CMP_DIR=cmp_dir, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, CONTROL], env=env,
                       capture_output=True, text=True)
    failed = [ln for ln in r.stdout.splitlines() if "CONTROL FAILED" in ln]
    tally = [ln for ln in r.stdout.splitlines()
             if ln.startswith("R8 GATE CONTROL:")]
    return r.returncode, (tally[0] if tally else "NO TALLY LINE"), len(failed)


def stage(mut=None):
    d = tempfile.mkdtemp(prefix="r8_mut_")
    for f in COPIED:
        shutil.copy2(os.path.join(SRC, f), os.path.join(d, f))
    if mut is not None:
        _, _, old, new, _ = mut
        p = os.path.join(d, "analyse_t23g2.py")
        s = open(p).read()
        got = s.count(old)
        if got != 1:
            raise AssertionError(
                "mutation %s: expected EXACTLY 1 occurrence of %r, found %d -- "
                "the mutation no longer applies to the shipped code and this "
                "RAISES rather than reporting a false green"
                % (mut[0], old[:60], got))
        open(p, "w").write(s.replace(old, new))
    return d


print("=" * 74)
print("R8 MUTATION DEMONSTRATION -- section 2p.7 limb (d)")
print("  production comparator sha256 before: %s" % PRODUCTION_SHA_BEFORE)
print("=" * 74)

rows = []

# ---- M0, the NEGATIVE arm: unmutated copy MUST be green ------------------
d = stage(None)
rc, tally, nfail = run_control(d)
shutil.rmtree(d, ignore_errors=True)
m0_ok = (rc == 0 and nfail == 0)
print("-" * 74)
print("M0  NEGATIVE ARM -- unmutated copy through the same machinery")
print("    required GREEN (rc 0, 0 controls failed)")
print("    got rc=%d  %s  controls failed: %d" % (rc, tally, nfail))
print("    %s" % ("AS REQUIRED" if m0_ok else
                  "DEMONSTRATION INVALID -- the copy machinery itself is broken"))
rows.append(("M0", "negative arm, no mutation", "GREEN",
             "GREEN" if m0_ok else "RED", m0_ok))

# ---- M1..M6, each MUST turn the suite red --------------------------------
for mut in MUTATIONS:
    mid, what, _, _, expect_controls = mut
    d = stage(mut)
    rc, tally, nfail = run_control(d)
    shutil.rmtree(d, ignore_errors=True)
    killed = (rc != 0 and nfail > 0)
    print("-" * 74)
    print("%s  %s" % (mid, what))
    print("    expected to flip controls: %s" % expect_controls)
    print("    got rc=%d  %s  controls failed: %d" % (rc, tally, nfail))
    print("    %s" % ("SUITE WENT RED -- mutation KILLED" if killed else
                      "SUITE SURVIVED -- A MEASURED BLIND SPOT"))
    rows.append((mid, what, "RED", "RED" if killed else "GREEN", killed))

after = sha(os.path.join(SRC, "analyse_t23g2.py"))
same = (after == PRODUCTION_SHA_BEFORE)
print("=" * 74)
kills = sum(1 for r in rows[1:] if r[4])
print("MUTATIONS KILLED: %d of %d" % (kills, len(MUTATIONS)))
print("NEGATIVE ARM M0 : %s" % ("GREEN, as required" if m0_ok else "BROKEN"))
print("production comparator sha256 after : %s   %s"
      % (after, "UNCHANGED" if same else "*** CHANGED -- STOP ***"))
print("=" * 74)
sys.exit(0 if (m0_ok and kills == len(MUTATIONS) and same) else 1)
