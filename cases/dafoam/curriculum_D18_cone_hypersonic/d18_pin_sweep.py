#!/usr/bin/env python3
"""D18 PIN SWEEP -- every `MD5_*=` constant in the launcher and the driver must equal the
md5 of the file it names.

WHY THIS EXISTS, and it is not hypothetical. A stale pin is `D8R-DRIVER-DEF-1`: the frozen
driver named an instrument md5 that no longer matched, and the chain would have aborted at
staging, exit 4, at zero compute -- a whole item's launch bought nothing. Building D18 by
copy-and-delta from D17 left FOUR stale pins (`MD5_LAUNCHER` and `MD5_GRADER` and `MD5_XF`
in the driver, `MD5_XF` in the launcher), because the renamed files hash differently and
nothing was checking. THE G-ROOT.5 SELFTEST CAUGHT ONE OF THEM; this sweep catches all of
them at once and is cheap enough to run before every freeze.

ORDER MATTERS AND IS ENFORCED: the launcher's own md5 is computed AFTER the launcher is
final, because editing the launcher changes it. A sweep that fixed pins in one pass and
then reported clean would be reporting on a file it had itself invalidated.

REFUSES (exit 2) on any stale pin. `--selftest` drives a PLANTED stale pin (L-314).
"""
import argparse, hashlib, os, re, sys

FILES = {"MD5_LAUNCHER": "d18_run_arm.sh", "MD5_GRADER": "d18_grade.py",
         "MD5_RUNSCRIPT": "d18_runScript.py", "MD5_XF": "d18_xf.py",
         "MD5_DECOMP": "d18_decomposeParDict", "MD5_MACH": "d18_mach_agreement.py"}
SOURCES = ("d18_chain_driver.sh", "d18_run_arm.sh")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def sweep(root):
    """Returns (rows, stale). A source or target that cannot be read is STALE, never a pass."""
    rows, stale = [], []
    seen = 0
    for src in SOURCES:
        sp = os.path.join(root, src)
        if not os.path.isfile(sp):
            stale.append((src, "-", "SOURCE ABSENT", "-")); continue
        s = open(sp, errors="replace").read()
        for key, fname in FILES.items():
            fp = os.path.join(root, fname)
            for m in re.finditer(r"^%s=([0-9a-f]{32})" % key, s, re.M):
                seen += 1
                if not os.path.isfile(fp):
                    stale.append((src, key, m.group(1), "TARGET ABSENT")); continue
                want = md5(fp)
                rows.append((src, key, m.group(1), want, m.group(1) == want))
                if m.group(1) != want:
                    stale.append((src, key, m.group(1), want))
    if seen == 0:
        # A clean zero over an empty population is the false green this lab has been misled
        # by three times. No pins found means the reader is broken, not that all pins are good.
        stale.append(("<sweep>", "<none found>", "-",
                      "REFUSE: zero MD5_ pins matched -- an empty population is not a pass"))
    return rows, stale


def selftest(root, tmpdir):
    """PLANTED-FAILURE PROOF (Sanaa sec.1, L-314). Zero compute. No `assert`: `-O` strips those."""
    import shutil, tempfile
    n = 0; bad = []

    def unit(name, cond):
        nonlocal n
        n += 1
        print("  [%s] %s" % ("OK " if cond else "BAD", name))
        if not cond:
            bad.append(name)

    rows, stale = sweep(root)
    unit("(1) the REAL case directory sweeps CLEAN across %d pin(s)" % len(rows), not stale and rows)

    d = os.path.join(tempfile.mkdtemp(dir=tmpdir), "case")
    shutil.copytree(root, d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # (2) PLANT a stale pin -- the exact D8R-DRIVER-DEF-1 shape.
    p = os.path.join(d, "d18_chain_driver.sh"); s = open(p).read()
    open(p, "w").write(re.sub(r"^MD5_XF=[0-9a-f]{32}", "MD5_XF=" + "0" * 32, s, flags=re.M))
    _, st = sweep(d)
    unit("(2) PLANTED a stale MD5_XF in the driver -> DETECTED",
         any(k == "MD5_XF" and src == "d18_chain_driver.sh" for src, k, _, _ in st))

    # (3) PLANT the shape that actually happened here: edit a target so its pin goes stale.
    shutil.rmtree(d); shutil.copytree(root, d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    with open(os.path.join(d, "d18_xf.py"), "a") as f:
        f.write("\n# planted edit -- the file moved and the pin did not\n")
    _, st = sweep(d)
    unit("(3) PLANTED an edit to d18_xf.py with its pins unchanged -> DETECTED in BOTH sources",
         len([1 for src, k, _, _ in st if k == "MD5_XF"]) == 2)

    # (4) A target that vanished is STALE, never a pass.
    shutil.rmtree(d); shutil.copytree(root, d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    os.unlink(os.path.join(d, "d18_mach_agreement.py"))
    _, st = sweep(d)
    unit("(4) PLANTED the G-MACH instrument ABSENT -> STALE, not a silent pass",
         any(w == "TARGET ABSENT" for _, _, _, w in st))

    # (5) The empty-population control: a reader that finds nothing must REFUSE.
    shutil.rmtree(d); os.makedirs(d)
    _, st = sweep(d)
    unit("(5) PLANTED an empty directory -> REFUSES rather than reporting a clean zero",
         any("empty population" in str(w) for _, _, _, w in st))

    shutil.rmtree(os.path.dirname(d), ignore_errors=True)
    print("D18 PIN SWEEP SELFTEST units=%d failures=%d python_O=%s" % (n, len(bad), not __debug__))
    if n != 5 or bad:
        print("D18 PIN SWEEP SELFTEST FAIL: %s" % (bad or "unit count %d != 5" % n))
        return 2
    print("D18 PIN SWEEP SELFTEST PASS 5/5")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.root, a.tmpdir)
    rows, stale = sweep(a.root)
    for src, key, got, want, ok in rows:
        print("  [%s] %-14s in %-22s %s" % ("OK " if ok else "STALE", key, src, got))
    if stale:
        print("D18 PIN SWEEP REFUSES: %d stale pin(s)" % len(stale))
        for r in stale:
            print("   %s" % (r,))
        return 2
    print("D18 PIN SWEEP CLEAN: %d pin(s), every one equal to the file it names" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
