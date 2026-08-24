#!/usr/bin/env python3
"""Control C0 (F4_SIGFPE_STEP01_PREREGISTRATION.md section 6): is the Step-0
instrument INERT?

Prereg section 4.2 argues inertness clause by clause and labels itself an
argument, not a measurement. C0 converts it. Two throwaway copies of the SAME
fresh 0/ are run -- one with the published rhoCentralFoamBounded, one with the
instrumented rhoCentralFoamBoundedDiag -- and the first 200 `Time = ` blocks are
compared.

Method, stated so the result is reproducible from this file alone:
  * a BLOCK runs from a `^Time = ` line up to (not including) the next one;
  * the first N_BLOCKS blocks of each log are taken;
  * from the DIAG log only, the two lines the instrument adds -- `BOUNDDIAG:`
    and `BOUNDHIST:` -- are removed. They are the whole point of the
    instrument; C0 asks whether anything ELSE moved;
  * wall-clock-dependent lines (`ExecutionTime`, `ClockTime`) are dropped from
    BOTH, because they cannot agree between two separate processes and say
    nothing about the solution;
  * every remaining line is compared position by position, byte for byte. That
    covers `Time =`, the Courant lines, every residual line and every
    `BOUND: e below eMin in N cell(s) ... worst e = ... at cell ...` line in one
    test, and it is STRICTER than the prereg's enumeration: any line the prereg
    did not think to name is also compared.

Standing rule 3 applies to C0 itself: an "identical" verdict from a comparator
not shown able to report "different" is not evidence. So the comparator plants a
known perturbation into a copy of the diag block-list and asserts it reports a
difference. If the plant is invisible, C0 REFUSES rather than passing.

Exit 0 = INERT (and the plant was seen). Exit 2 = NOT inert, or the plant was
not seen. Anything but exit 0 stops Step 0 from launching.
"""
import re
import sys
from pathlib import Path

N_BLOCKS = 200
RE_TIME = re.compile(r"^Time = (\S+)\s*$")
RE_BOUND = re.compile(r"^BOUND: ")
DROP_FROM_DIAG = ("BOUNDDIAG:", "BOUNDHIST:")
DROP_FROM_BOTH = ("ExecutionTime", "ClockTime")


def blocks(path: Path, n: int, strip_instrument: bool) -> list[list[str]]:
    out: list[list[str]] = []
    cur: list[str] | None = None
    for raw in path.read_text(errors="replace").splitlines():
        if RE_TIME.match(raw):
            if cur is not None:
                out.append(cur)
                if len(out) >= n:
                    return out
            cur = [raw]
            continue
        if cur is None:
            continue                      # pre-first-block banner
        if raw.startswith(DROP_FROM_BOTH):
            continue
        if strip_instrument and raw.startswith(DROP_FROM_INSTRUMENT_PREFIXES):
            continue
        cur.append(raw)
    if cur is not None and len(out) < n:
        out.append(cur)
    return out


DROP_FROM_INSTRUMENT_PREFIXES = DROP_FROM_DIAG


def compare(a: list[list[str]], b: list[list[str]]) -> list[str]:
    """-> list of human-readable disagreements (empty == identical)."""
    bad: list[str] = []
    if len(a) != len(b):
        bad.append(f"block count differs: published={len(a)} diag={len(b)}")
    for i, (ba, bb) in enumerate(zip(a, b)):
        if ba != bb:
            for j in range(max(len(ba), len(bb))):
                la = ba[j] if j < len(ba) else "<missing>"
                lb = bb[j] if j < len(bb) else "<missing>"
                if la != lb:
                    bad.append(
                        f"block {i} ({ba[0] if ba else '?'}) line {j}:\n"
                        f"    published: {la!r}\n"
                        f"    diag     : {lb!r}"
                    )
    return bad


def main() -> int:
    here = Path(__file__).resolve().parent.parent
    pub = here / "c0_twin_published" / "log.c0"
    dia = here / "c0_twin_diag" / "log.c0"
    A = blocks(pub, N_BLOCKS, strip_instrument=False)
    B = blocks(dia, N_BLOCKS, strip_instrument=True)

    print(f"published log: {pub}")
    print(f"diag log     : {dia}")
    print(f"blocks compared: published={len(A)} diag={len(B)} (target {N_BLOCKS})")
    if len(A) < N_BLOCKS or len(B) < N_BLOCKS:
        print(f"C0 REFUSES: fewer than {N_BLOCKS} blocks in one of the logs.")
        return 2

    n_bound_pub = sum(1 for blk in A for ln in blk if RE_BOUND.match(ln))
    n_bound_dia = sum(1 for blk in B for ln in blk if RE_BOUND.match(ln))
    print(f"BOUND: lines inside the compared window: published={n_bound_pub} "
          f"diag={n_bound_dia}")

    bad = compare(A, B)

    # --- the plant (standing rule 3): can this comparator report a difference?
    import copy
    Bp = copy.deepcopy(B)
    victim = next((i for i, blk in enumerate(Bp)
                   if any(RE_BOUND.match(ln) for ln in blk)), None)
    if victim is None:
        print("C0 REFUSES: no BOUND: line inside the window, so the plant "
              "cannot be placed on the line class C0 exists to compare.")
        return 2
    k = next(j for j, ln in enumerate(Bp[victim]) if RE_BOUND.match(ln))
    original = Bp[victim][k]
    Bp[victim][k] = original.replace("e below eMin in ", "e below eMin in 999999 ", 1)
    planted_bad = compare(A, Bp)
    if len(planted_bad) <= len(bad):
        print("C0 REFUSES: the planted perturbation was NOT seen by this "
              "comparator -- an 'identical' verdict from it would be a blind "
              "zero (standing rule 3).")
        return 2
    print(f"PLANT ok: a perturbed BOUND: line in block {victim} was seen "
          f"({len(planted_bad)} disagreement(s) vs {len(bad)} unperturbed). "
          "The comparator is able to report a difference.")

    if bad:
        print(f"\nC0 RESULT: NOT INERT -- {len(bad)} disagreement(s) in the "
              f"first {N_BLOCKS} blocks. Step 0 does NOT launch (prereg 6).")
        for line in bad[:40]:
            print("  " + line)
        if len(bad) > 40:
            print(f"  ... {len(bad) - 40} more")
        return 2

    print(f"\nC0 RESULT: INERT. Every line of the first {N_BLOCKS} `Time = ` "
          "blocks is byte-identical between the published rhoCentralFoamBounded "
          "and the instrumented rhoCentralFoamBoundedDiag, once the two ADDED "
          "lines (BOUNDDIAG:, BOUNDHIST:) and the wall-clock lines are removed. "
          "That covers Time, the Courant lines, every residual line and every "
          "BOUND: line (N, worst-e to all printed digits, worst cell).")
    print("prereg 4.2's inertness argument is now a MEASUREMENT.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
