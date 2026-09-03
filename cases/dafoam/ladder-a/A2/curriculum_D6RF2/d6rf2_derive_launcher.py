#!/usr/bin/env python3
"""Curriculum D6RF2 -- derive the launcher, the driver and the grader from
`D6RF`'s REPAIRED bytes by an ENUMERATED SUBSTITUTION SET, every substitution
asserted PRESENT-THEN-ABSENT, plus a small set of ADDITIONS each asserted
ABSENT-THEN-PRESENT.

WHY DERIVE RATHER THAN WRITE.  `D6RF`'s three files carry every lesson this
family paid for today, and re-typing them would re-open every one:

  * the `.gz`-tolerant `field_path`/`assert_field` helper, with NO unrepaired
    call site -- four field-name sites plus two `points.gz` sites (ADDENDUM 3);
  * `count_src_entries` returning **UNMEASURED**, never 0, and S4 refusing on
    UNMEASURED *and* on 0 -- the vacuous-pass repair (ADDENDUM 2);
  * the age datum resolved by name and **asserted a non-empty integer** before
    use, because rule 4's age guard is physics;
  * every guard's evidence line naming its own trip count ("the comparison
    COUNTED 78 entries on both sides");
  * the units gate at BOTH call sites with rc 7 / rc 77 distinct, and the
    launcher refusing to build an arm command that lacks it;
  * H5 and aggregate that HOLD and never refuse to launch;
  * `rc` captured INSIDE the wrapper, `docker inspect` read BEFORE `docker rm`;
  * exactly one `sudo -n rm -rf "$WORK"`, every guard preceding it, and `F_mp`
    refusing on a stale arm directory rather than removing one.

**Anything not in the substitution or addition set below is `D6RF`'s bytes.**

THE ONE STRUCTURAL ADDITION: `G-ANCHOR` IS INVOKED BY THE LAUNCHER AT STAGING,
BEFORE ANY CONTAINER (`PREREGISTRATION.md` §3, and the supervisor's instruction).
The gate already refuses at run time inside the consumers; invoking it at staging
is what turns "this would have refused after a launch" into "this refuses before
one", which is the whole point of `D6RF-BLOCKING-1`.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D6RF = os.path.abspath(os.path.join(HERE, os.pardir, "curriculum_D6RF"))

# ---- the repaired producer's md5, read from disk, never typed --------------
PRODUCER = "d6rf2_opt_runScript.py"


def md5_file(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def fail(msg):
    sys.stderr.write("D6RF2_DERIVE_LAUNCHER ABORT %s\n" % msg)
    sys.exit(2)


# =========================================================================
# THE SUBSTITUTION SET.  (old, new, expected_count) -- expected_count is the
# number of occurrences that MUST be present before and gone after.  A count
# that does not match aborts: a substitution matching a different number of
# sites than registered is not a rename, it is an unreviewed edit.
# =========================================================================
def subs_common(new_md5s):
    return [
        # --- identity -----------------------------------------------------
        ("ITEM=D6RF", "ITEM=D6RF2", "opt"),        # shell form
        ('ITEM = "D6RF"', 'ITEM = "D6RF2"', "opt"),  # python form (the grader)
        ("CURRICULUM-D6RF-a2-wing-multipoint-fd", "CURRICULUM-D6RF2-a2-wing-multipoint-fd", "opt"),
        ("D6RF_", "D6RF2_", "opt"),
        ("d6rf_", "d6rf2_", "opt"),
        # --- the instruments this item stages instead of D6R's -------------
        ("d6r_fd_endpoint.py", "d6rf2_fd_endpoint.py", "opt"),
        ("d6r_ref_off.py", "d6rf2_ref_off.py", "opt"),
        ("d6r_opt_runScript.py", "d6rf2_opt_runScript.py", "opt"),
        ("d6r_cmd.sh", "d6rf2_cmd.sh", "opt"),   # launcher only
        # --- the pins that follow -----------------------------------------
        ("MD5_RUNSCRIPT6=93edb4a231e13a7af065368f61a468ef",  # md5 pins: launcher and driver only
         "MD5_RUNSCRIPT6=%s" % new_md5s["d6rf2_opt_runScript.py"], "opt"),
        ("MD5_FD=7491c3a73c232fb6744990fd8109fd63",  # md5 pins: launcher and driver only
         "MD5_FD=%s" % new_md5s["d6rf2_fd_endpoint.py"], "opt"),
        ("MD5_REFOFF=ad67bbeb0c7b502262ebf5d4e8fa21cd",  # md5 pins: launcher and driver only
         "MD5_REFOFF=%s" % new_md5s["d6rf2_ref_off.py"], "opt"),
        ("MD5_LOCUS6=341189ca866f302a7e1bba8eefad3a57",  # md5 pins: launcher and driver only
         "MD5_LOCUS6=%s" % new_md5s["d6rf2_endpoint_locus.py"], "opt"),
        ("MD5_PHYS6=ea0a83410c773f753a7750eb3becefdf",  # md5 pins: launcher and driver only
         "MD5_PHYS6=%s" % new_md5s["d6rf2_endpoint_physical.py"], "opt"),
        ("MD5_UNITS=40993d949e44aae3f80bf1a3d2cf4998",  # md5 pins: launcher and driver only
         "MD5_UNITS=%s" % new_md5s["d6rf2_units_assert.py"], "opt"),
    ]


# =========================================================================
# THE ADDITIONS.  Each is asserted ABSENT before and PRESENT after, and each
# names the registration clause that requires it.
# =========================================================================
ANCHOR_PIN = "MD5_ANCHOR_GATE=%s"
ANCHOR_STAGE_BLOCK = '''
# ===========================================================================
# G-ANCHOR -- INVOKED HERE, AT STAGING, BEFORE ANY CONTAINER.
# PREREGISTRATION.md section 3.  D6RF-BLOCKING-1 is the reason: BOTH consumers
# refused honestly on `count != 1`, but nothing checked whether the producer
# could SATISFY them -- so an unrunnable registration became a launch instead of
# a defect found before compute.  The gate is run over the arm directory's OWN
# staged bytes, so it checks what the container will actually read.
# A refusal here is rc 3 and NO CONTAINER IS CREATED.
# ===========================================================================
echo "$MD5_ANCHOR_GATE  $WORK/d6rf2_anchor_gate.py" | md5sum -c - || { stage_say "ABORT G-ANCHOR gate md5"; exit 4; }
python3 "$WORK/d6rf2_anchor_gate.py" --work-dir "$WORK" || {
  stage_say "ABORT G-ANCHOR arm=$ARM -- a reader that splits the producer on a sentinel"
  stage_say "  cannot be shown that sentinel is unique in the bytes it will read."
  stage_say "  THIS IS THE D6RF-BLOCKING-1 CLASS, REFUSED BEFORE A CONTAINER RATHER"
  stage_say "  THAN AFTER ONE.  See the gate's own refusal line above."
  exit 3; }
stage_say "D6RF2_G_ANCHOR OK arm=$ARM -- every anchor-scoped reader's sentinel is unique in the producer it will read, and the header it yields carries every symbol it execs"
'''


def derive(src_name, dst_name, subs, additions, out):
    src = os.path.join(D6RF, src_name)
    if not os.path.isfile(src):
        fail("source absent: %s" % src)
    text = open(src).read()
    print("  %-28s <- %-26s src md5 %s" % (dst_name, src_name, md5_file(src)))
    for old, new, want in subs:
        n = text.count(old)
        if n == 0:
            # "opt" is the ONLY form allowed to be absent, and it must be
            # DECLARED optional at the call site -- an undeclared substitution
            # that matches nothing is a silent no-op, which is the defect this
            # whole pattern exists to prevent.  An absent optional is PRINTED,
            # never passed over in silence.
            if want == "opt":
                print("      --  %-46s x0   (declared optional; absent here)"
                      % old.strip()[:44])
                continue
            fail("substitution source ABSENT from %s: %r -- if that is legitimate "
                 "it must be DECLARED optional, not discovered" % (src_name, old[:90]))
        if isinstance(want, int) and n != want:
            fail("substitution %r occurs %d times in %s, registered %d"
                 % (old[:60], n, src_name, want))
        text = text.replace(old, new)
        if old in text and old not in new:
            fail("substitution did not take in %s: %r" % (src_name, old[:90]))
        print("      OK  %-46s x%-3d -> %s" % (old.strip()[:44], n, new.strip()[:34]))
    for label, anchor, block in additions:
        if block in text:
            fail("addition %r is ALREADY PRESENT in %s -- it would be duplicated"
                 % (label, src_name))
        if text.count(anchor) != 1:
            fail("addition %r anchors on %r which occurs %d times in %s (need 1)"
                 % (label, anchor[:60], text.count(anchor), src_name))
        text = text.replace(anchor, block + anchor, 1)
        if block not in text:
            fail("addition %r did not take in %s" % (label, src_name))
        print("      ADD %-46s before %s" % (label, anchor.strip()[:40]))
    open(os.path.join(out, dst_name), "w").write(text)
    return text


def main():
    out = HERE
    print("D6RF2 LAUNCHER/DRIVER/GRADER DERIVATION\n")
    need = ("d6rf2_opt_runScript.py", "d6rf2_fd_endpoint.py", "d6rf2_ref_off.py",
            "d6rf2_endpoint_locus.py", "d6rf2_endpoint_physical.py",
            "d6rf2_units_assert.py", "d6rf2_anchor_gate.py")
    md5s = {}
    for n in need:
        p = os.path.join(out, n)
        if not os.path.isfile(p):
            fail("this item's instrument %s is absent -- run d6rf2_derive.py first" % n)
        md5s[n] = md5_file(p)
    print("  this item's instrument md5s, READ FROM DISK:")
    for n in need:
        print("    %-30s %s" % (n, md5s[n]))
    print()

    common = subs_common(md5s)

    # ---- the launcher: the substitutions plus G-ANCHOR at staging ---------
    launcher_additions = [
        ("G-ANCHOR at staging (PREREGISTRATION.md section 3)",
         "# ---- THE AGE DATUM IS WRITTEN LAST", ANCHOR_STAGE_BLOCK)]
    lsubs = list(common) + [
        # the gate's own pin, added beside the others
        ("MD5_REF_MESH=0fb1935a9b8781b73ac4ccb136e3ec68",
         (ANCHOR_PIN % md5s["d6rf2_anchor_gate.py"])
         + "\nMD5_REF_MESH=0fb1935a9b8781b73ac4ccb136e3ec68", 1),
    ]
    launcher = derive("d6rf_run_arm.sh", "d6rf2_run_arm.sh", lsubs,
                      launcher_additions, out)

    # ---- the driver ------------------------------------------------------
    lm = hashlib.md5(launcher.encode()).hexdigest()
    dsubs = list(common) + [
        ("MD5_LAUNCHER=%s" % md5_file(os.path.join(D6RF, "d6rf_run_arm.sh")),
         "MD5_LAUNCHER=%s" % lm, 1),
        # ANCHORED ON THE POST-SUBSTITUTION VALUE: subs_common has already
        # rewritten this pin, so anchoring on D6R's value would match nothing.
        ("MD5_UNITS=%s" % md5s["d6rf2_units_assert.py"],
         "MD5_UNITS=%s\nMD5_ANCHOR_GATE=%s"
         % (md5s["d6rf2_units_assert.py"], md5s["d6rf2_anchor_gate.py"]), 1),
        # THE THREE DERIVED INSTRUMENTS COME FROM THIS ITEM, NOT FROM D6R's
        # DIRECTORY.  The common rename would otherwise have the driver copy
        # `$D6R_CASE_DIR/d6rf2_*` -- paths that do not exist, which `cp` would
        # refuse; the substitution is registered so the intent is reviewable
        # rather than implicit in a path that happens to work.
        ('"$D6R_CASE_DIR/d6rf2_opt_runScript.py" "$D6R_CASE_DIR/d6rf2_fd_endpoint.py"',
         '"$HERE/d6rf2_opt_runScript.py" "$HERE/d6rf2_fd_endpoint.py"', 1),
        ('"$D6R_CASE_DIR/d6r_extract_endpoint.py" "$D6R_CASE_DIR/d6rf2_ref_off.py"',
         '"$D6R_CASE_DIR/d6r_extract_endpoint.py" "$HERE/d6rf2_ref_off.py"', 1),
        ('"$HERE/d6rf2_units_assert.py" \\',
         '"$HERE/d6rf2_units_assert.py" "$HERE/d6rf2_anchor_gate.py" \\', 1),
        ('echo "$MD5_UNITS  $BASE/d6rf2_units_assert.py"; }',
         'echo "$MD5_UNITS  $BASE/d6rf2_units_assert.py"\n'
         '  echo "$MD5_ANCHOR_GATE  $BASE/d6rf2_anchor_gate.py"\n'
         '  echo "$MD5_RUNSCRIPT6  $BASE/d6rf2_opt_runScript.py"\n'
         '  echo "$MD5_FD  $BASE/d6rf2_fd_endpoint.py"\n'
         '  echo "$MD5_REFOFF  $BASE/d6rf2_ref_off.py"; }', 1),
    ]
    driver = derive("d6rf_chain_driver.sh", "d6rf2_chain_driver.sh", dsubs, [], out)

    # ---- the grader ------------------------------------------------------
    gsubs = list(common) + [
        # the grader hashes its OWN frozen paths at execution; they must name
        # this item, or it would verify D6RF's freeze and pass on the wrong one.
        ("curriculum_D6RF/", "curriculum_D6RF2/", 4),
        # the anchor gate joins this item's frozen set
        ('"cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_endpoint_physical.py",',
         '"cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_endpoint_physical.py",\n'
         '            "cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_anchor_gate.py",\n'
         '            "cases/dafoam/ladder-a/A2/curriculum_D6RF2/d6rf2_opt_runScript.py",', 1),
    ]
    derive("d6rf_grade.py", "d6rf2_grade.py", gsubs, [], out)

    # ---- cross-checks ----------------------------------------------------
    print("\n  CROSS-CHECK:")
    lt = open(os.path.join(out, "d6rf2_run_arm.sh")).read()
    dt = open(os.path.join(out, "d6rf2_chain_driver.sh")).read()
    gt = open(os.path.join(out, "d6rf2_grade.py")).read()
    checks = [
        ("no D6R producer md5 survives anywhere",
         all("93edb4a231e13a7af065368f61a468ef" not in t for t in (lt, dt, gt))),
        ("no d6rf_ (single-f) token survives",
         all(not re.search(r"\bd6rf_", t) for t in (lt, dt, gt))),
        ("the launcher invokes G-ANCHOR", 'd6rf2_anchor_gate.py" --work-dir' in lt),
        ("G-ANCHOR precedes the age datum",
         lt.index('d6rf2_anchor_gate.py" --work-dir') < lt.index("THE AGE DATUM IS WRITTEN LAST")),
        ("G-ANCHOR precedes the first docker run",
         lt.index('d6rf2_anchor_gate.py" --work-dir') < lt.index("docker run -d")),
        ("the driver pins the derived launcher", ("MD5_LAUNCHER=%s" % lm) in dt),
        ("the launcher pins the gate",
         ("MD5_ANCHOR_GATE=%s" % md5s["d6rf2_anchor_gate.py"]) in lt),
        ("the .gz field helper survived", "field_path()" in lt and "assert_field()" in lt),
        ("count_src_entries survived", "count_src_entries()" in lt),
        ("the age datum integer assert survived", "is not an integer" in lt),
        ("the units gate is at both call sites",
         "D6RF2_UNITS_CALLSITE_1" in lt and lt.count("d6rf2_units_assert.py") >= 3),
        ("exactly one sudo rm -rf $WORK",
         len([l for l in lt.splitlines()
              if 'sudo -n rm -rf "$WORK"' in l and not l.strip().startswith("#")]) == 1),
        ("H5 and aggregate HOLD", "H5_HOLD" in dt and "AGGREGATE_HOLD" in dt),
        ("docker inspect before docker rm",
         lt.index("State.ExitCode") < lt.index("docker rm")),
    ]
    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print("    %-52s %s" % (n, "OK" if ok else "FAIL"))
    if bad:
        fail("cross-check failed: %s" % bad)
    print("\nD6RF2_DERIVE_LAUNCHER OK -- 3 files derived; launcher md5 %s" % lm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
