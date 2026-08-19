# T1c diagnostic: what is the 0.075–0.111 % excess that survives mesh refinement?

Written 2026-08-19, **before either diagnostic case was built or solved.**

## The observation being explained

Both arms of T1c converge at second order and both **overshoot the exact
constant in the limit of zero mesh spacing**:

| arm | Richardson h→0 | exact | excess |
| --- | ---: | ---: | ---: |
| constant `Ts` | 3.6608395 | 3.6567934 | **+0.1106 %** |
| constant `q″` | 4.3669013 | 4.3636364 | **+0.0748 %** |

**The excess is therefore not discretisation error** — it is what remains after
discretisation is extrapolated away. It is small, but it is the difference
between the constant-Ts row passing and failing: that row deviates 0.0865 %
against a GCI band of 0.0301 %.

## The two candidates, which happen to sit at the same order of magnitude

**A — axial conduction.** The Graetz solution that produces 3.6568 and 48/11
**neglects axial conduction**, valid as the Péclet number → ∞. These cases run at
**Pe = Re·Pr = 71**, and the neglected term is O(1/Pe²) = **0.0198 %**.

**B — the wedge chord.** An OpenFOAM wedge replaces the circular arc by a flat
chord. The relative geometric defect is O((θ/2)²) = (2.5° in radians)² =
**0.190 %**.

**Both are within a factor of five of the observed excess, so neither can be
chosen by magnitude alone.** They are separated by experiment instead.

## The design: two cases, each a SINGLE-parameter change from `L_q_f`

Both use the constant-flux arm, whose exact constant is the clean rational 48/11
and which has no saturation complication, on the finest mesh (26 112 cells),
`endTime` 30000.

| case | change | Pe | wedge | everything else |
| --- | --- | ---: | ---: | --- |
| `D_Pe` | **`Pr` 0.71 → 2.84** | 71 → **284** | 5° | identical |
| `D_wedge` | **wedge 5° → 1°** | 71 | **1°** | identical |

**Why `Pr` and not `Re` for the Péclet test, which is the point of the design:**
raising `Re` would change the velocity field, the entry length and the friction
simultaneously. Raising `Pr` at fixed `Re` leaves **the momentum solution
bit-for-bit unchanged** — same mesh, same `U`, same pressure gradient, same
station — so any change in Nusselt is attributable to the thermal transport
alone. The thermal entry length grows to 0.05·Re·Pr = 14.2 D, still far short of
the 40 D sampling station.

## REGISTERED PREDICTIONS

**If A (axial conduction) dominates:** `D_Pe` raises Pe by 4×, so an O(1/Pe²)
term falls by **16×**. The excess should drop from **+0.0748 %** to about
**+0.005 %**. `D_wedge` should show **no significant change**.

**If B (the wedge chord) dominates:** `D_wedge` reduces the angle by 5×, so an
O(θ²) term falls by **25×**. The excess should drop from **+0.0748 %** to about
**+0.003 %**. `D_Pe` should show **no significant change**.

**If both contribute**, both cases reduce the excess and neither reaches zero,
and the two reductions should approximately account for the total.

**The falsifying outcome, stated so it cannot be explained away afterwards: if
NEITHER case moves the excess materially, both hypotheses are wrong** and the
excess is something this study has not named — in which case the honest report is
that the constant-Ts GATE FAIL has **no identified cause**, not that it has a
plausible one.

## What this diagnostic does not do

**It does not change any T1c verdict.** Row L0 GATE FAILs at 0.0865 % against a
0.0301 % band whatever the cause turns out to be, and these two cases are
**diagnostic, not graded** — they have no registered band and cannot pass or
fail. Explaining a failure is not the same as excusing it.
