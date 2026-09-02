#!/usr/bin/env python3
"""T25R5 ARM VERIFIER -- pre-registration section 4.2 check E6.

⛔ DEFAULT-DENY, and it REFUSES (exit 2) rather than degrading.

E6: an arm's dictionaries may differ from the T25R4 baseline ONLY inside the two
`p_rgh` solver blocks, and only in keys that are not `tolerance` and not `relTol`.
Anything else -- another equation's solver, the module region, PIMPLE,
relaxationFactors, fvSchemes -- DISQUALIFIES the arm, and its iteration count is
then not eligible for G-T5 whatever it is.

THE METHOD IS A PROOF, NOT A PARSE.  Take the arm's coolant fvSolution, splice
the BASELINE's two p_rgh blocks back in, and require the result to be BYTE-
IDENTICAL to the baseline file.  If one byte anywhere outside those two blocks
had moved, the splice could not reproduce the baseline.  No dictionary parser is
trusted, and there is nothing for a regex to miss.

    python3 verify_arm_t25R5.py --arm C4 [--case <dir>]
    python3 verify_arm_t25R5.py --selftest

Exit 0 = the arm is admissible.  Exit 2 = REFUSE.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_CASE = os.path.join(os.path.dirname(HERE), "T25R4_MODULE_runs", "P1")
EXIT_REFUSE = 2

# --- FROZEN AT THE PRE-REGISTRATION (section 1, section 2).  These four values are
# --- the registered CONVERGENCE CRITERION and no arm may alter them.  A swapped
# --- tolerance would make the whole probe meaningless while leaving every other
# --- check green, which is exactly why they are asserted literally here.
REQUIRED = {
    ("p_rgh.*", "tolerance"): "1e-13",
    ("p_rgh.*", "relTol"):    "0.01",
    ("p_rghFinal", "tolerance"): "1e-13",
    ("p_rghFinal", "relTol"):    "1e-3",
}
# D0 is the section 3.4a pressure-share DIAGNOSTIC.  Its relTol departure is
# REGISTERED, it produces NO PHYSICS, and it is never compared or cited.  It is
# named here so the exception is visible rather than silent.
D0_RELTOL = "0.5"

BLOCK_START = re.compile(r'^\s*(?:"p_rgh\.\*"|p_rghFinal)\s*$')


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def span(text):
    """1-based [lo, hi] line span covering BOTH p_rgh blocks, by brace matching."""
    lines = text.split("\n")
    try:
        lo = next(i for i, l in enumerate(lines) if l.strip() == '"p_rgh.*"')
        j = next(i for i, l in enumerate(lines) if l.strip() == "p_rghFinal")
    except StopIteration:
        return None
    depth = 0
    while j < len(lines) - 1:
        j += 1
        depth += lines[j].count("{") - lines[j].count("}")
        if depth == 0 and "}" in lines[j]:
            return lo, j
    return None


def splice(text, donor):
    """Replace text's two p_rgh blocks with donor's. Returns None if either lacks them."""
    a, b = span(text) or (None, None), span(donor) or (None, None)
    if a[0] is None or b[0] is None:
        return None
    tl, dl = text.split("\n"), donor.split("\n")
    return "\n".join(tl[:a[0]] + dl[b[0]:b[1] + 1] + tl[a[1] + 1:])


def read(p):
    if not os.path.isfile(p):
        refuse("required file %s DOES NOT EXIST. Default-deny: an absent "
               "dictionary is not a matching one." % p)
    return open(p).read()


def block_values(text):
    """{(block, key): value} for keys at the TOP level of the two p_rgh blocks.

    Brace depth is tracked because C4 nests a `preconditioner { ... }` sub-dict
    inside `"p_rgh.*"`.  A depth-blind reader closes the block on the sub-dict's
    `}` and never sees the `tolerance`/`relTol` lines that follow it -- which
    made this verifier REFUSE a legitimate arm until its own selftest caught it.
    Keys nested deeper than the block itself are deliberately NOT recorded: the
    registered criterion lives at the block's top level and nowhere else.
    """
    out, cur, depth = {}, None, 0
    for ln in text.split("\n"):
        s = ln.strip()
        if cur is None:
            if BLOCK_START.match(ln):
                cur, depth = s.strip('"'), 0
            continue
        depth += s.count("{") - s.count("}")
        if depth <= 0 and "}" in s:
            cur = None
            continue
        if depth == 1 and s.endswith(";"):
            parts = s[:-1].split()
            if len(parts) == 2:
                out.setdefault((cur, parts[0]), parts[1])
    return out


def verify(arm, case=None, base=None, quiet=False):
    base = base or BASE_CASE
    case = case or os.path.join(HERE, arm)
    say = (lambda *a: None) if quiet else print

    b_cool = read(os.path.join(base, "system", "coolant", "fvSolution"))
    if os.path.isdir(os.path.join(case, "system")):
        a_cool = read(os.path.join(case, "system", "coolant", "fvSolution"))
        a_mod = read(os.path.join(case, "system", "module", "fvSolution"))
        b_mod = read(os.path.join(base, "system", "module", "fvSolution"))
        if a_mod != b_mod:
            refuse("arm %s: the MODULE region fvSolution differs from the "
                   "baseline. E6. The probe tunes the coolant p_rgh solver and "
                   "nothing else." % arm)
        for reg in ("coolant", "module"):
            fa = os.path.join(case, "system", reg, "fvSchemes")
            fb = os.path.join(base, "system", reg, "fvSchemes")
            if read(fa) != read(fb):
                refuse("arm %s: %s/fvSchemes differs from the baseline. E6. "
                       "Discretisation is physics, not linear-solver tuning."
                       % (arm, reg))
    else:
        a_cool = read(os.path.join(HERE, "arms", "fvSolution.coolant." + arm))
        say("  (dictionary-only mode: no staged case at %s)" % case)

    # ---- THE PROOF: splice the baseline's blocks in and demand byte-identity.
    spliced = splice(a_cool, b_cool)
    if spliced is None:
        refuse("arm %s: could not locate both p_rgh blocks. A dictionary this "
               "verifier cannot bound is one it cannot clear." % arm)
    if spliced != b_cool:
        n = sum(1 for x, y in zip(spliced.split("\n"), b_cool.split("\n")) if x != y)
        refuse("arm %s: %d line(s) differ from the baseline OUTSIDE the two "
               "p_rgh blocks. E6 DISQUALIFIES this arm; its iteration count is "
               "not eligible for G-T5." % (arm, n))
    say("  ok   outside the two p_rgh blocks: byte-identical to the baseline")

    # ---- The registered convergence criterion, asserted literally.
    v = block_values(a_cool)
    for (blk, key), want in REQUIRED.items():
        if arm == "D0" and key == "relTol":
            want = D0_RELTOL
        got = v.get((blk, key))
        if got != want:
            refuse("arm %s: %s/%s is %r, registered %r. The convergence "
                   "CRITERION is not tunable -- section 2. A swapped tolerance "
                   "makes every iteration count in this probe meaningless."
                   % (arm, blk, key, got, want))
    say("  ok   tolerance 1e-13 x2 and the registered relTol values: as frozen"
        + ("  (D0's registered relTol 0.5 exception applied)" if arm == "D0" else ""))
    say("  ADMISSIBLE: %s" % arm)
    return 0


def selftest():
    import tempfile, shutil
    fails = [0]

    def chk(n, c):
        print("  %-4s %s" % ("ok" if c else "FAIL", n))
        if not c:
            fails[0] += 1

    def run(arm, base):
        try:
            return verify(arm, case=os.path.join(base, "nonexistent_case"),
                          base=base, quiet=True)
        except SystemExit as e:
            return e.code

    tmp = tempfile.mkdtemp(prefix="t25r5_")
    try:
        b = os.path.join(tmp, "base", "system", "coolant")
        os.makedirs(b)
        src = read(os.path.join(BASE_CASE, "system", "coolant", "fvSolution"))
        open(os.path.join(b, "fvSolution"), "w").write(src)
        os.makedirs(os.path.join(tmp, "arms"))
        global HERE
        keep, HERE = HERE, tmp

        def put(name, text):
            open(os.path.join(tmp, "arms", "fvSolution.coolant." + name),
                 "w").write(text)

        base = os.path.join(tmp, "base")
        for a in ("B0", "C1", "C2", "C3", "C4", "C5", "D0"):
            put(a, read(os.path.join(keep, "arms", "fvSolution.coolant." + a)))
            chk("real arm %s is ADMISSIBLE (exit 0)" % a, run(a, base) == 0)

        # --- PLANTED CONTROLS (rule 3).  Every clearance above is a zero, and a
        # --- zero from a reader not shown able to see a non-zero is not evidence.
        plants = [
            ("out-of-block: h tolerance 1e-10 -> 1e-09",
             src.replace("        tolerance       1e-10;", "        tolerance       1e-09;", 1)),
            ("out-of-block: relaxation h 0.7 -> 0.65",
             src.replace("        h           0.7;", "        h           0.65;", 1)),
            ("out-of-block: nOuterCorrectors-adjacent PIMPLE key nCorrectors 2 -> 3",
             src.replace("    nCorrectors     2;", "    nCorrectors     3;", 1)),
            ("out-of-block: rho solver PCG -> PBiCGStab",
             src.replace("        solver          PCG;", "        solver          PBiCGStab;", 1)),
            ("IN-block but FORBIDDEN: p_rgh relTol 0.01 -> 0.05",
             src.replace("        relTol          0.01;", "        relTol          0.05;", 1)),
            ("IN-block but FORBIDDEN: tolerance 1e-13 -> 1e-12",
             src.replace("        tolerance       1e-13;", "        tolerance       1e-12;", 1)),
        ]
        for name, mutant in plants:
            chk("PLANTED %s -> the mutant CHANGED the file" % name, mutant != src)
            put("PLANT", mutant)
            chk("PLANTED %s -> REFUSES (exit 2)" % name,
                run("PLANT", base) == EXIT_REFUSE)

        # --- REGRESSION PLANT for the depth bug this verifier's own selftest
        # --- caught: a nested sub-dict inside `"p_rgh.*"` (C4's shape) used to
        # --- make a depth-blind reader close the block early, miss the
        # --- tolerance line entirely, and REFUSE a legitimate arm.  Here the
        # --- nested arm carries a BAD tolerance AFTER the sub-dict: a reader
        # --- that cannot see past the nesting would clear it.
        c4 = read(os.path.join(keep, "arms", "fvSolution.coolant.C4"))
        put("NEST_OK", c4)
        chk("nested sub-dict arm with a GOOD tolerance -> ADMISSIBLE",
            run("NEST_OK", base) == 0)
        put("NEST_BAD", c4.replace("        tolerance       1e-13;",
                                   "        tolerance       1e-11;", 1))
        chk("PLANTED nested sub-dict arm with tolerance 1e-13 -> 1e-11 AFTER "
            "the sub-dict -> REFUSES", run("NEST_BAD", base) == EXIT_REFUSE)

        put("TRUNC", "\n".join(src.split("\n")[:20]))
        chk("a dictionary with NO p_rgh blocks -> REFUSES",
            run("TRUNC", base) == EXIT_REFUSE)
        chk("a MISSING arm file -> REFUSES (absence is not a match)",
            run("NOPE", base) == EXIT_REFUSE)
        HERE = keep
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails[0] else "FAIL", fails[0]))
    return 0 if not fails[0] else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    i = sys.argv.index("--arm")
    c = sys.argv[sys.argv.index("--case") + 1] if "--case" in sys.argv else None
    sys.exit(verify(sys.argv[i + 1], case=c))
