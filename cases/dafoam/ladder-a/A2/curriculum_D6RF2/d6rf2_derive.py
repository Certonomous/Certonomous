#!/usr/bin/env python3
"""Curriculum D6RF2 -- derive this item's four instruments from D6R's frozen
bytes by an ENUMERATED SUBSTITUTION SET, every substitution asserted
PRESENT-THEN-ABSENT.  Anything not in the set is D6R's bytes.

THE DEFECT THIS ITEM EXISTS TO REPAIR -- `D6RF-BLOCKING-1`.
`d6r_opt_runScript.py` carries the sentinel `# OpenMDAO setup` TWICE: at `:230`,
the real anchor, and at `:21`, INSIDE THE MODULE DOCSTRING, in the sentence that
explains why the anchor exists.  **The sentence explaining the anchor contains
the anchor, and thereby breaks it.**  Both consumers refuse on a count other than
one (`d6r_fd_endpoint.py:67`, `d6r_ref_off.py:53`), so BOTH D6RF arms were
unrunnable, and so were D6R's own.

MEASURED, and it shows the refusal was protecting the item rather than obstructing
it: `split(ANCHOR)[0]` returns **1,396 characters of a 12,861-character file** --
truncated inside the docstring -- where the correct header is **10,275**.  The
truncated header carries `daOptions` (the docstring mentions it) but NOT
`class Top`, NOT `POINTS` and NOT `U0`.  **A count-of-1 test at the wrong site
would still have been wrong, which is why this item asserts the header's LENGTH
and CONTENT and not merely the count.**

⚠ A CORRECTION TO THE RULING THAT COMMISSIONED THIS ITEM.  The ruling says the
fix "is a DOCSTRING REWORD and changes no executable byte", and that the
successor "stages its OWN copy of the producer with a new pin".  Both are true of
the producer -- and they are NOT SUFFICIENT, because **both consumers hardcode
`PRODUCER_MD5 = "93edb4a231e13a7af065368f61a468ef"`** (`d6r_fd_endpoint.py:31`,
`d6r_ref_off.py:30`) and check it BEFORE they ever count the anchor.  A
one-character reword therefore makes them refuse one step EARLIER, at the md5.
So this item must derive the consumers too.  It does, by substitution of exactly
two constants each -- the producer's NAME and its MD5 -- and nothing else.
**D6R's originals are not edited and not moved** (`CLAUDE.md` rule 6); D6R's
record and pins stay intact.

`d6r_extract_endpoint.py` does NOT use the anchor (measured: zero occurrences)
and is staged UNCHANGED.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D6R = os.path.abspath(os.path.join(HERE, os.pardir, "curriculum_D6R"))
D6RF = os.path.abspath(os.path.join(HERE, os.pardir, "curriculum_D6RF"))

ANCHOR = "# OpenMDAO setup"
SRC_PRODUCER_MD5 = "93edb4a231e13a7af065368f61a468ef"

# ---- THE ONE SUBSTITUTION IN THE PRODUCER.  Prose only; no executable byte. --
# The replacement NAMES the anchor without REPRODUCING it, which is the whole
# repair.  It is asserted not to contain the sentinel.
OLD_DOC = ("""switch are D4's bytes.  The ANCHOR line `# OpenMDAO setup` is kept so that
d6r_fd_endpoint.py and d6r_ref_off.py exec the header exactly as D4's FD
instrument does.""")
NEW_DOC = ("""switch are D4's bytes.  The anchor comment at the head of the OpenMDAO
model section is kept so that this item's FD and off-design instruments exec the
header exactly as D4's FD instrument does.  THE SENTINEL IS DELIBERATELY NOT
REPRODUCED IN THIS DOCSTRING: in the predecessor it was, which made it occur
twice in the file and made every consumer that splits on it refuse
(D6RF-BLOCKING-1).  Name the anchor; never quote it.""")

SUBS = {
    "d6rf2_opt_runScript.py": ("d6r_opt_runScript.py", [(OLD_DOC, NEW_DOC)]),
    "d6rf2_fd_endpoint.py": ("d6r_fd_endpoint.py", [
        ('PRODUCER = "d6r_opt_runScript.py"', 'PRODUCER = "d6rf2_opt_runScript.py"'),
        ('PRODUCER_MD5 = "%s"' % SRC_PRODUCER_MD5, 'PRODUCER_MD5 = "{{PRODUCER_MD5}}"')]),
    "d6rf2_ref_off.py": ("d6r_ref_off.py", [
        ('PRODUCER = "d6r_opt_runScript.py"', 'PRODUCER = "d6rf2_opt_runScript.py"'),
        ('PRODUCER_MD5 = "%s"' % SRC_PRODUCER_MD5, 'PRODUCER_MD5 = "{{PRODUCER_MD5}}"')]),
}
# the physical wrapper is D6RF's, which pins the same producer md5
SUBS_D6RF = {
    "d6rf2_endpoint_physical.py": ("d6rf_endpoint_physical.py", [
        ('RUNSCRIPT = "d6r_opt_runScript.py"', 'RUNSCRIPT = "d6rf2_opt_runScript.py"'),
        ('MD5_RUNSCRIPT = "%s"' % SRC_PRODUCER_MD5, 'MD5_RUNSCRIPT = "{{PRODUCER_MD5}}"'),
        ("import d6rf_endpoint_locus as locus", "import d6rf2_endpoint_locus as locus")]),
}


def md5_of_text(t):
    return hashlib.md5(t.encode()).hexdigest()


def fail(msg):
    sys.stderr.write("D6RF2_DERIVE ABORT %s\n" % msg)
    sys.exit(2)


def derive_one(src_dir, src_name, dst_name, subs, out):
    src_path = os.path.join(src_dir, src_name)
    if not os.path.isfile(src_path):
        fail("source absent: %s" % src_path)
    text = open(src_path).read()
    src_md5 = md5_of_text(text)
    print("  %-28s <- %-28s src md5 %s" % (dst_name, src_name, src_md5))
    for old, new in subs:
        # PRESENT-THEN-ABSENT: the old form must be there exactly once before,
        # and gone exactly once after.  A substitution that matched nothing is a
        # silent no-op and is the defect this pattern exists to prevent.
        n = text.count(old)
        if n != 1:
            fail("substitution source occurs %d times (need exactly 1) in %s:\n    %r"
                 % (n, src_name, old[:120]))
        text = text.replace(old, new, 1)
        if old in text:
            fail("substitution did not take in %s: %r still present" % (src_name, old[:120]))
        if new not in text:
            fail("substitution target absent after replace in %s" % src_name)
        print("      OK  %-60s -> %s" % (old.splitlines()[0][:58], new.splitlines()[0][:40]))
    open(os.path.join(out, dst_name), "w").write(text)
    return text


def main():
    out = HERE
    print("D6RF2 DERIVATION -- enumerated substitutions, present-then-absent\n")

    # ---- 1. the producer -------------------------------------------------
    name, subs = SUBS["d6rf2_opt_runScript.py"]
    prod = derive_one(D6R, name, "d6rf2_opt_runScript.py", subs, out)

    # ---- 2. THE REPAIR IS ASSERTED, NOT ASSUMED --------------------------
    orig = open(os.path.join(D6R, name)).read()
    if orig.count(ANCHOR) != 2:
        fail("the ORIGINAL producer no longer carries the sentinel twice "
             "(%d) -- the premise of this item has changed" % orig.count(ANCHOR))
    n = prod.count(ANCHOR)
    print("\n  ANCHOR COUNT  original %d  ->  repaired %d" % (orig.count(ANCHOR), n))
    if n != 1:
        fail("the repaired producer carries the sentinel %d times, need exactly 1" % n)

    # THE LENGTH AND CONTENT ASSERTION -- a count of 1 AT THE WRONG SITE would
    # still be wrong, so the header is checked for what it must contain.
    head = prod.split(ANCHOR)[0]
    orig_correct_head = ANCHOR.join(orig.split(ANCHOR)[:-1])
    orig_broken_head = orig.split(ANCHOR)[0]
    print("  HEADER LENGTH original-broken %d  original-correct %d  repaired %d"
          % (len(orig_broken_head), len(orig_correct_head), len(head)))
    if len(head) < 10000:
        fail("the repaired header is %d chars -- far short of the ~10,275 the "
             "correct split yields; the anchor is at the wrong site" % len(head))
    for sym in ("class Top", "POINTS", "U0 =", "daOptions", "CL_TARGETS", "WEIGHTS"):
        if sym not in head:
            fail("the repaired header does not carry %r -- the consumers exec it "
                 "and read that name out of the namespace" % sym)
    print("  HEADER CONTENT class Top / POINTS / U0 / daOptions / CL_TARGETS / WEIGHTS  ALL PRESENT")
    # and the strongest form: the repaired header IS the original's correct
    # header with exactly this item's substitution applied, byte for byte.
    expect = orig_correct_head.replace(OLD_DOC, NEW_DOC, 1)
    if head != expect:
        fail("the repaired header is NOT the original's correct header with the "
             "registered substitution applied (len %d vs %d)" % (len(head), len(expect)))
    print("  HEADER IDENTITY  repaired header == original CORRECT header + the "
          "registered substitution, BYTE FOR BYTE")
    if ANCHOR in NEW_DOC:
        fail("the replacement docstring REPRODUCES the sentinel")

    # ---- 3. the consumers, re-pinned to the repaired producer ------------
    pmd5 = md5_of_text(prod)
    print("\n  repaired producer md5 %s\n" % pmd5)
    for dst, (src, subs) in sorted(SUBS.items()):
        if dst == "d6rf2_opt_runScript.py":
            continue
        t = derive_one(D6R, src, dst, subs, out)
        t = t.replace("{{PRODUCER_MD5}}", pmd5)
        open(os.path.join(out, dst), "w").write(t)
    for dst, (src, subs) in sorted(SUBS_D6RF.items()):
        t = derive_one(D6RF, src, dst, subs, out)
        t = t.replace("{{PRODUCER_MD5}}", pmd5)
        open(os.path.join(out, dst), "w").write(t)

    # ---- 4. every derived consumer must now agree with the producer ------
    print("\n  CROSS-PIN CHECK -- every derived file names the repaired producer "
          "and its md5:")
    ok = True
    for f in ("d6rf2_fd_endpoint.py", "d6rf2_ref_off.py", "d6rf2_endpoint_physical.py"):
        t = open(os.path.join(out, f)).read()
        a = "d6rf2_opt_runScript.py" in t
        b = pmd5 in t
        c = SRC_PRODUCER_MD5 not in t
        print("    %-30s names-producer=%s  pins-new-md5=%s  old-md5-gone=%s"
              % (f, a, b, c))
        ok = ok and a and b and c
    if not ok:
        fail("a derived consumer does not agree with the repaired producer")
    print("\nD6RF2_DERIVE OK -- 4 files derived, every substitution asserted "
          "present-then-absent, D6R's originals untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
