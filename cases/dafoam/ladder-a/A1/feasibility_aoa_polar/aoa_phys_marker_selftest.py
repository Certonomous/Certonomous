#!/usr/bin/env python3
"""G-PHYS -- BOTH LIMBS DRIVEN, in both directions.

WHY THIS FILE EXISTS. `aoa_run_arm_selftest.sh` drove G-PHYS's md5 limb and NOT
its marker-count limb. The clean producer passed the md5 limb, so the selftest
reported the guard healthy -- while the producer would have been REFUSED by the
limb that was never driven. G-PHYS caught it at the first launch attempt, before
any AOAC compute, and the refusal was correct: the generated file embedded the
marker strings as whole literals inside its own self-assert, so
`# ---- D19M_PHYSICS_END ----` occurred TWICE and the split was ambiguous.

THE LESSON, WHICH IS THE REASON THIS IS A SEPARATE FILE AND NOT AN EDIT:
**A GUARD IS NOT TESTED UNTIL EVERY LIMB OF IT IS DRIVEN.** A partial selftest
that reports PASS is worse than none, because it buys confidence it has not
earned. `aoa_run_arm_selftest.sh` is left byte-untouched -- it is on AOAI's
pinned grading path and AOAI is running -- so this limb gets its own instrument.
"""
import hashlib
import sys

PROD = ("/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/"
        "feasibility_aoa_polar/aoa_runScript_comp.py")
WANT = "c66504acc57bd9ef009599e883d2ef3b"
B = "# ---- D19M_PHYSICS_BEGIN ----\n"
E = "# ---- D19M_PHYSICS_END ----"


def g_phys(src):
    """Exactly what the arm and the producer's self-assert do. BOTH limbs."""
    nb, ne = src.count(B), src.count(E)
    if nb != 1 or ne != 1:
        return "REFUSE", "markers appear %d/%d, expected 1/1" % (nb, ne)
    got = hashlib.md5(src.split(B)[1].split(E)[0].strip().encode()).hexdigest()
    if got != WANT:
        return "REFUSE", "physics md5 %s != D19M's %s" % (got, WANT)
    return "PASS", "markers 1/1 and physics md5 %s" % got


def main():
    clean = open(PROD).read()
    fails = 0
    cases = [
        ("[+] clean producer", clean, "PASS",
         "a guard that fires on everything gets turned off"),
        ("[-] one physics byte moved", clean.replace("nuTilda0 = 4.5e-5",
                                                     "nuTilda0 = 4.6e-5"), "REFUSE",
         "the md5 limb"),
        ("[-] END marker duplicated", clean.replace(
            "# ---- D19M_PHYSICS_END ----\n",
            "# ---- D19M_PHYSICS_END ----\n# ---- D19M_PHYSICS_END ----\n", 1),
         "REFUSE", "THE LIMB THAT WAS NEVER DRIVEN -- the real defect's shape"),
        ("[-] BEGIN marker removed", clean.replace(B, "", 1), "REFUSE",
         "the marker-count limb, other direction"),
        ("[-] whole physics block gone", clean.replace(
            B + clean.split(B)[1].split(E)[0] + E, "", 1), "REFUSE",
         "the block cannot silently vanish"),
    ]
    print("G-PHYS SELFTEST -- both limbs, both directions")
    print("  producer: %s" % PROD)
    print("  producer md5: %s" % hashlib.md5(clean.encode()).hexdigest())
    print()
    for name, src, want, note in cases:
        got, why = g_phys(src)
        ok = got == want
        print("  %-32s want %-6s got %-6s %s" %
              (name, want, got, "PASS" if ok else "*** FAIL ***"))
        print("      %s | %s" % (why, note))
        if not ok:
            fails += 1
    print()
    if fails:
        print("G-PHYS SELFTEST FAIL: %d case(s)." % fails)
        return 2
    print("G-PHYS SELFTEST PASS: 5 cases, both limbs driven, both directions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
