#!/usr/bin/env python3
"""F12 P-reference fidelity cross-check: SECONDARY (on-disk, F12's reference of
record) vs AR-138 PRIMARY (human-read from the page image, per L-144).

Executes ruling d1a55db1 against the pre-registered spot tap set
(verification/campaign/F12_P_REFERENCE_CROSSCHECK_TAP_PREREG_2026-09-07.md,
committed 3a3edef1 BEFORE this comparison was tabulated).

PLANTED-ZERO CONTROL (CLAUDE.md rule 3): a comparator that could only ever emit
near-zero differences is worthless. Before the real comparison runs, a known
perturbation PLANT is written into a COPY of the secondary .dat on disk, read
back through the SAME on-disk loader, and the diff detector must SEE it at the
planted tap and nowhere else. If it cannot, the script REFUSES (exit 2) rather
than degrade to reporting a possibly-blind zero.

The PRIMARY Cp values below were read by a human this session off the rendered
page image of PDF p201 (A6-20), Table 6.7 "SURFACE PRESSURE DISTRIBUTION",
"CASE 9 M=0.730 ALPHA=3.19 RE=6500000", UPPER SURFACE column. They are NOT read
from any sidecar, filename, or OCR text layer (rule 15 / L-144).
"""
from __future__ import annotations
import sys, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECONDARY = HERE.parent / "reference" / "rae2822_case9_cp_upper.dat"

# --- pre-registered taps: (secondary x/c, primary x/c) ------------------------
TAPS = [
    (0.049974, 0.0500), (0.100047, 0.1000), (0.300038, 0.3000),
    (0.500030, 0.5000), (0.524967, 0.5250), (0.550003, 0.5500),
    (0.575039, 0.5750), (0.599976, 0.6000), (0.619647, 0.6196),
    (0.650048, 0.6500), (0.749994, 0.7500), (0.900013, 0.9000),
]
SHOCK = {0.500030, 0.524967, 0.550003, 0.575039, 0.599976, 0.619647, 0.650048}

# --- PRIMARY Cp, human-read from PDF p201 upper surface (per L-144) -----------
PRIMARY = {
    0.0500: -1.1973, 0.1000: -1.1123, 0.3000: -1.1535, 0.5000: -1.2853,
    0.5250: -1.3097, 0.5500: -1.1249, 0.5750: -0.7552, 0.6000: -0.6338,
    0.6196: -0.5681, 0.6500: -0.4949, 0.7500: -0.2983, 0.9000: -0.0325,
}

READ_TOL = 0.0001      # one print unit of the primary's 4-dp table
TAP_UNCERT = 0.0026    # experiment's own quoted tap uncertainty (AR-138 item 10)


def load_secondary(path: Path) -> list[tuple[float, float]]:
    """Parse (x/c, Cp) from an on-disk .dat, exactly as the F12 grader does."""
    pts = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        x, cp = line.split()
        pts.append((float(x), float(cp)))
    return sorted(pts)


def cp_at(pts: list[tuple[float, float]], x: float) -> float:
    """Nearest-station lookup; refuse if no station within 5e-4 of x."""
    best = min(pts, key=lambda p: abs(p[0] - x))
    if abs(best[0] - x) > 5e-4:
        raise SystemExit(f"REFUSE: no secondary station within 5e-4 of x={x}")
    return best[1]


def planted_zero_control() -> None:
    """Plant a known Cp perturbation into a disk copy, read it back, prove the
    reader+diff sees it. Refuse (exit 2) if the planted non-zero is invisible."""
    PLANT = 0.037000          # a value no real diff below approaches
    plant_x = 0.575039        # the steepest-recompression tap
    txt = SECONDARY.read_text().splitlines()
    out, planted_line = [], False
    for line in txt:
        s = line.strip()
        if not s or s.startswith("#"):
            out.append(line); continue
        x, cp = s.split()
        if abs(float(x) - plant_x) < 5e-4 and not planted_line:
            out.append(f"{float(x):.6f}  {float(cp) + PLANT:+.6f}")
            planted_line = True
        else:
            out.append(line)
    if not planted_line:
        print("PLANTED-ZERO CONTROL: REFUSE — could not plant (tap not found).")
        sys.exit(2)
    tmp = HERE / "_planted_secondary.dat"
    tmp.write_text("\n".join(out) + "\n")
    base = load_secondary(SECONDARY)
    pert = load_secondary(tmp)
    seen_at_plant = cp_at(pert, plant_x) - cp_at(base, plant_x)
    # elsewhere must be untouched
    seen_elsewhere = max(abs(cp_at(pert, sx) - cp_at(base, sx))
                         for sx, _ in TAPS if abs(sx - plant_x) >= 5e-4)
    tmp.unlink()
    ok = abs(seen_at_plant - PLANT) < 1e-6 and seen_elsewhere < 1e-9
    print(f"PLANTED-ZERO CONTROL: planted {PLANT:+.6f} at x={plant_x}; "
          f"reader saw {seen_at_plant:+.6f} there, {seen_elsewhere:.2e} elsewhere "
          f"-> {'SEEN (control passes)' if ok else 'BLIND'}")
    if not ok:
        print("REFUSE (exit 2): reader not shown able to see a non-zero.")
        sys.exit(2)


def main() -> None:
    planted_zero_control()
    sec = load_secondary(SECONDARY)
    print(f"\n{'x/c(sec)':>10} {'x/c(pri)':>9} {'Cp_sec':>10} {'Cp_pri':>9} "
          f"{'d=sec-pri':>11} {'|d|/tol':>8} {'shock':>6}")
    max_abs = 0.0
    worst = None
    for sx, px in TAPS:
        cps = cp_at(sec, sx)
        cpp = PRIMARY[px]
        d = cps - cpp
        if abs(d) > max_abs:
            max_abs, worst = abs(d), (sx, d)
        print(f"{sx:>10.6f} {px:>9.4f} {cps:>10.6f} {cpp:>9.4f} "
              f"{d:>+11.6f} {abs(d)/READ_TOL:>8.2f} "
              f"{'YES' if sx in SHOCK else '-':>6}")
    print(f"\nmax|d| = {max_abs:.6f} at x/c(sec)={worst[0]:.6f} (d={worst[1]:+.6f})")
    print(f"read tolerance   = {READ_TOL:.6f}  (one print unit, 4-dp table)")
    print(f"tap uncertainty  = {TAP_UNCERT:.6f}  (AR-138 item 10, Re=6.5e6)")
    print(f"max|d| as fraction of tap uncertainty = {max_abs/TAP_UNCERT:.4f}")
    within_read = max_abs <= READ_TOL
    within_uncert = max_abs <= TAP_UNCERT
    verdict = "MEETS" if within_uncert else "FAILS"
    print(f"\nDECISION: {verdict} the ruling's fidelity tolerance "
          f"(within_read={within_read}, within_tap_uncertainty={within_uncert})")


if __name__ == "__main__":
    main()
