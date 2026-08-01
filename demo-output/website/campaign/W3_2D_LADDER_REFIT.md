# W3 — the five two-dimensional ladders, refitted

Item: `w3-refit-the-2d-ladders`, approved 2026-07-31 22:18:09 UTC,
`est_core_min` 20. Run 2026-08-01. **No compute**: every ladder in this file
was already solved and stored, and the work is a refit.

Machine-readable companion: `W3_2D_LADDER_REFIT.json`, written by refitting
each ladder through `chief_engineer.uq.eca_hoekstra_band` at both
dimensionalities and reading the verdict through `uq.reportable_band`.

---

## 1. Half the premise was already false when the item was approved

The proposal states:

> The band fit derives mesh size from the cube root of cell count and none of
> the five two-dimensional acts overrides it, so every one has been fitted as
> though it were three-dimensional.

That was true when the proposal was drafted, at **2026-07-31 18:18:27 UTC**. It
stopped being true **fourteen minutes later**, at commit 6d3cb925,
**2026-07-31 18:32:34 UTC**, "Five 2D ladders were being fitted with the cube
root; they now pass dim=2". All five workflows have passed `dim=2` since, with
the justification inline at each call site. Every stored act artifact for the
five postdates that commit.

The item was then **approved at 22:18:09 UTC, four hours after the fix landed**,
against a rationale nobody re-read. The refit half of the objective was
already done and the docket had no way to know.

What remained genuinely open is the proposal's second clause — *"and see which
earn a band"* — and its stated hope, *"Some of these may have been denied a
band they earned."* That is answered below.

## 2. None of the five earns a band, at either dimensionality

| ladder | rungs (cells) | p at dim=2 | p at dim=3 | band | guard that holds it |
| --- | --- | --- | --- | --- | --- |
| supersonic wedge, shock angle | 1 800 / 7 200 / 28 800 | 0.035 | 0.052 | none | order_window **and** extrapolation_sanity |
| supersonic cone, shock angle | 1 800 / 7 200 / 28 800 | 0.801 | 1.202 | none | extrapolation_sanity |
| diamond airfoil, wave drag | 2 000 / 8 000 / 32 000 | 6.233 | 9.349 | none | order_window |
| hypersonic cylinder, standoff | 1 000 / 4 000 / 16 000 | — | — | none | monotone |
| cylinder vortex shedding, Strouhal | 2 496 / 5 032 / 8 640 | 2.436 | 3.654 | none | extrapolation_sanity (dim=2); order_window **and** extrapolation_sanity (dim=3) |

`uq.reportable_band` returns `None` for all five at both dimensionalities. **The
non-conclusive verdicts are confirmed on the right arithmetic.** The hope that
some had been denied a band they earned does not survive the refit.

## 3. Why dimensionality could never have rescued any of them, and this is general

The Richardson extrapolated value is **identical at dim=2 and dim=3 on all
five**, to machine precision (the vortex-shedding pair differ in the 13th
significant figure, which is the fit's own arithmetic and not a difference).

That is structural, not a coincidence of these five. The observed order is
fitted so that `r^p` reproduces the measured ratio of successive increments,
and the extrapolation depends on the pair only through `r^p`. Change the
dimensionality and `r` and `p` move together in exactly compensating
directions. So:

> **Dimensionality can only ever move a verdict through the `order_window`
> guard.** It cannot move `monotone`, `increment_trend`, `distinct_rungs` or
> `extrapolation_sanity`, because none of those reads `p` or `r` separately.

Applied to the five: the cone, the hypersonic cylinder and the vortex shedder
are held by guards that are dimensionality-invariant, so their verdicts were
never in question. The wedge and the diamond are held by `order_window`, but
at **0.035** and **6.233** they are so far outside the credible window
[0.5, 2.5] that the factor of 1.5 between dimensionalities cannot reach it from
either side. Two of five were even theoretically in scope, and neither was
close.

The one thing dimensionality did move is the **stated reason**, on exactly one
ladder. The cylinder vortex shedder was declined for `order_window` at dim=3
(p = 3.654) and is declined for `extrapolation_sanity` at dim=2 (p = 2.436,
inside the window). Same verdict, different reason — which is the near miss
already docketed as `w8-right-verdict-wrong-reason`, and it is confirmed here
at both dimensionalities.

## 4. A finding the refit turned up that was not what it was looking for

**The supersonic wedge fails two guards and its act names only the weaker
one.** The published narration reads:

> the ladder is not conclusive because the observed order p = 0.034 falls
> outside the credible range 0.5 to 2.5, so no band is read from that spread

`guards_failed` for that ladder is `['order_window', 'extrapolation_sanity']`,
at **both** dimensionalities. The second is the serious one. The wedge's
increments are -1.465 and -1.430 degrees, so they barely shrink at all; the fit
returns p = 0.035, and the Richardson step multiplies the finest increment by
`1/(r^p - 1)` = **40.7**. The ladder therefore extrapolates the shock angle to
**-13.73 degrees** — not merely outside the range the rungs measured, but
physically impossible, since a shock angle cannot be negative.

`uq.guards_holding` exists precisely to say "the verdict does not rest on the
stated reason alone", and it returns two entries here. Nothing in the act
surfaces it. Correcting the order alone would not have moved the wedge, and a
reader of the transcript has no way to know that. A follow-on is filed.

### 4a. Correction, 2026-08-01: this section's digits came from rounded rungs

`w3-every-guard-that-holds-a-ladder` re-read the wedge through the act's own
fit rather than through this file's, and the two do not agree on the number.
**This section fitted the rungs as the act's ladder table PRINTS them**, at
three decimals: 47.588 / 46.123 / 44.693. The act fits what it solved:
47.58767882153372 / 46.12330850878531 / 44.692792746510406.

| | p | increments (deg) | amplification | extrapolated shock angle (deg) |
| --- | --- | --- | --- | --- |
| rungs as printed (this file, §4) | 0.035 | −1.465, −1.430 | 40.86 | **−13.733** |
| rungs as solved (the act's own fit) | 0.034 | −1.46437, −1.43052 | 42.25 | **−15.753** |

Both readings are on the record and neither is withdrawn. At an observed order
this close to zero the extrapolation amplifies the finest increment by more
than forty, so rounding the rungs at the third decimal moves the extrapolated
angle by **2.02 degrees**. Nothing that decides anything moves: `guards_failed`
is `['order_window', 'extrapolation_sanity']` on both, `conclusive` is False on
both, `reportable_band` is `None` on both, and the angle is impossible on both.
The act quotes the fit that ran; `sdk/tests/test_uq.py`
(`test_rounding_the_rungs_moves_the_digit_and_not_the_verdict`) pins the pair.

The same caution applies to §2's other observed orders, which were all fitted
from rungs as displayed: the act's own fits read 0.801 → 0.800 (cone), 6.233 →
6.296 (diamond) and 2.436 → 2.430 (vortex shedding). None of those changes a
guard or a verdict either.

## 5. Cost

`est_core_min` 20.0 on the docket. **Measured: no compute at all**, 0.0
core-minutes and no ranks — every rung was already solved and stored, and the
refit is arithmetic over five stored triples. The docket's estimate is an
estimate that was never derived; the drafter had no way to know that a "refit"
item costs nothing, because the docket has no cost class for work that reads
stored records rather than producing new ones.
