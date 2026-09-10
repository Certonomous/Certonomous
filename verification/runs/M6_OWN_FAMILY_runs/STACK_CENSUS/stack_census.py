#!/usr/bin/env python3
"""Census of SIGFPE backtrace frames across OpenFOAM solver logs.

WHY THIS EXISTS. A previous reader used `grep -A4 "sigFpe::sigHandler"` and reported
"ZERO logs carry a hePsiThermo frame". That was FALSE. In a 4-rank parallel log the
handler line and the frame of interest are EIGHT lines apart, and rank prefixes
([0] [1] [2]) shred single frames across several lines. A 4-line window cannot see
it. THE ZERO CAME FROM A READER THAT COULD NOT SEE A NON-ZERO (rule 3).

So this reader is PLANT-CONTROLLED: it is shown able to return a POSITIVE on a log
known to contain the frame, and a DIFFERENT positive on a log known to contain a
different frame, before any absence it reports is believed. It REFUSES if the
known-positive comes back empty.
"""
import re, sys, pathlib

# READER DEFECT #2, caught by CONTROL A refusing. The first version required at
# least one `::name` AFTER the class: `Foam::[A-Za-z_]\w*(?:::[A-Za-z_~]\w*)+`.
# `Foam::hePsiThermo<...>::calculate` is followed by `<`, not `::`, so that pattern
# could NEVER match it -- it silently matched `Foam::species::thermo` from inside
# the TEMPLATE ARGUMENTS instead. A template-heavy symbol is invisible to a regex
# that assumes `::` directly follows the class name.
FRAME = re.compile(r"Foam::([A-Za-z_][A-Za-z0-9_]*)")
RANK  = re.compile(r"^\s*(?:\[\d+\]\s*)+")

def frames(path):
    """Every Foam:: symbol appearing anywhere AFTER the first sigFpe handler line.
    No window: the whole tail is scanned, rank prefixes stripped."""
    txt = pathlib.Path(path).read_text(errors="replace")
    i = txt.find("sigFpe::sigHandler")
    if i < 0:
        return None                      # no SIGFPE stack at all
    tail = "\n".join(RANK.sub("", ln) for ln in txt[i:].splitlines())
    out, seen = [], set()
    for m in FRAME.finditer(tail):
        s = m.group(1)
        if s == "sigFpe":
            continue
        if s not in seen:
            seen.add(s); out.append(s)
    return out

def main():
    root = pathlib.Path(sys.argv[1])
    logs = sorted(root.glob("*/*/log.rhoSimpleFoam")) + sorted(root.glob("*/log.rhoSimpleFoam"))
    logs = sorted(set(logs))

    # ---- PLANTED CONTROLS, run BEFORE any absence is reported --------------
    pos = root / "L2/solve/log.rhoSimpleFoam"          # known to contain hePsiThermo
    alt = root / "L2/smoke_simplec/log.rhoSimpleFoam"  # known to contain GAMGSolver
    pf, af = frames(pos), frames(alt)
    ok_pos = pf is not None and any("hePsiThermo" in f for f in pf)
    ok_alt = af is not None and any("GAMGSolver" in f for f in af)
    ok_neg = pf is not None and not any("GAMGSolver" in f for f in pf)
    print(f"CONTROL A (known-positive hePsiThermo in L2/solve)      : {'SEEN' if ok_pos else 'NOT SEEN'}")
    print(f"CONTROL B (known-positive GAMGSolver in smoke_simplec)  : {'SEEN' if ok_alt else 'NOT SEEN'}")
    print(f"CONTROL C (reader DISCRIMINATES: no GAMG in L2/solve)   : {'DISCRIMINATES' if ok_neg else 'FAILS'}")
    if not (ok_pos and ok_alt and ok_neg):
        print("REFUSED: the reader was not shown able to see both positives and to tell them apart.")
        return 2
    print()
    for lg in logs:
        fr = frames(lg)
        rel = str(lg.relative_to(root))
        if fr is None:
            print(f"  {rel:<48} NO SIGFPE STACK")
        else:
            thermo = "hePsiThermo" if any("hePsiThermo" in f for f in fr) else "-"
            print(f"  {rel:<48} thermo={thermo:<11} top3={fr[:3]}")
    return 0

sys.exit(main())
