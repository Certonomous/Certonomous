# W3 — the race's numerical channel: pre-registration

**Written 2026-08-01 14:25 UTC.** One solve has been run at this point and it
is a reproduction check, not a result: alpha = 0, Re_c = 1.0e6, reported
below. **No solve at any angle the stored record does not already hold has
been launched.** Every number that decides the outcome of gates G2, G3 and G4
is unmeasured when this file is written.

Item: `w3-race-shrink-the-dominant-term`, approved, `est_core_min` 30.

---

## 1. The proposal's premise, checked against the stored record first

The proposal says:

> The race headline now composes to plus or minus 0.43, and the numerical
> channel owns 0.419 of it because the peak sits on the alpha equals zero edge
> of a coarse angle grid, where a half-step bracket reads slope rather than
> curvature. [...] halving the grid step near the peak is a handful of cheap
> solves and attacks the only term that matters.

The **diagnosis is right and is confirmed arithmetically below. The remedy does
not follow from it.**

Computed from `demo-output/website/race/pass2/race.json` through
`workflows.shape_optimization._fit_quadratic` and
`workflows.race_study.peak_grid_bracket`, 2026-08-01:

The reduced-order lane's four anchors and the quadratic fitted through them:

| alpha (deg) | 0.0 | 3.3 | 6.7 | 10.0 |
| --- | --- | --- | --- | --- |
| L/D | 18.1407 | 15.7329 | 12.4662 | 10.1547 |

fit `L/D = 18.224708 - 0.837175 a + 0.00217707 a^2`.

Its stationary point is at **alpha = 192.27 deg**, four spans of the searched
interval outside it. `race_study` then applies
`alpha_star = min(max(vertex, ALPHAS[0]), ALPHAS[-1])`, so the stored
`alpha_star = 0.0` was **set by the clamp, not by a fitted peak**. The
Monte-Carlo lane agrees independently: its eleven nominal-Reynolds solves run
18.141, 17.855, 17.045, 16.045, 15.046, 14.000, 13.068, 12.222, 11.463,
10.774, 10.155 — **strictly decreasing across the whole domain**. Both lanes
report a maximum at the lower edge of the interval they were given.

The bracket is therefore evaluated one-sided at a boundary, and its behaviour
under refinement is exactly what a slope reading looks like:

| half-step (deg) | 0.5 | 0.25 | 0.125 |
| --- | --- | --- | --- |
| `peak_grid_bracket` | 0.41913 | 0.20943 | 0.10468 |

Each halving of the step halves the bracket, to five figures, and
`0.5 x |slope at 0| = 0.41859` recovers the headline 0.419 on its own. **A term
that falls exactly linearly with the step is not being resolved by refinement;
it is being redefined by it.** Halving the grid step near alpha = 0 would report
0.209 instead of 0.419 and would have measured nothing. That is the outcome the
proposal as written would have produced, and it is why the remedy is being
changed rather than executed.

## 2. What is actually unknown

Whether the peak exists at all inside the domain the act searched. The wing is
cambered (NACA 4412, `camber = 0.04`), so it carries lift at zero incidence
(`cl = 0.2483` measured), and a cambered section's lift-to-drag maximum sits
where induced drag equals profile drag, which for this wing may be at a
**negative** angle of attack. If it is, the stored 18.14 at alpha = 0 is a
boundary optimum of the search interval, the act's stated question ("where the
wing's lift-to-drag peaks over alpha 0-10 degrees") was answered correctly for
the interval it names, and the headline's numerical channel is not a grid
resolution term at all. Nothing in the stored record settles this, because
nothing in the stored record was solved below alpha = 0.

## 3. Gates, fixed now

**G1 — reproduction.** A fresh solve at alpha = 0, Re_c = 1.0e6 reproduces the
stored point. Threshold: L/D within 1e-6 of 18.140687390989.
*Result already in hand, recorded here as run: 2026-08-01 14:22:03 UTC, L/D
18.140687390989, cl 0.248302524055, cd 0.013687602829, 3.93 s.* **PASS**, and
it is bit-identical rather than merely inside tolerance.

**G2 — is the reported peak a boundary optimum?** Solve L/D on a 0.5-deg grid
over alpha in [-8, +3] at Re_c = 1.0e6.
*PASS* = the maximum of the solved series falls at alpha < 0, i.e. outside the
interval the act searched. *FAIL* = the maximum falls at alpha >= 0, in which
case the peak is interior after all and the proposal's remedy is the right one.

**G3 — does refinement shrink the term, or only rename it?** At whichever angle
G2 locates, evaluate the half-step bracket at half-steps 0.5, 0.25 and 0.125
against a quadratic fitted to the three solved points nearest that angle on a
0.125-deg grid.
*PASS* = the bracket ratio between half-step 0.5 and half-step 0.25 is nearer
4 than 2 (curvature-limited, so refinement genuinely resolves it). *FAIL* =
nearer 2 (slope-limited, so refinement only rescales it). The stored fit's
ratio is 2.0011, which is the FAIL signature, and G3 asks whether that survives
once the bracket is taken at a genuine interior maximum.

**G4 — the number.** Report the half-step bracket at the located peak at the
act's own stated tolerance, `TOLERANCE_DEG = 0.5`, and state whether the race's
composed headline band changes. No threshold: this is the reportable figure
whichever way G2 and G3 fall.

## 4. Cost, pre-committed

Measured: one VSPAERO solve of this wing at one alpha took **3.93 s** wall on
this box at 14:22:03 UTC 2026-08-01, single process.

G2 needs 23 solves ([-8, +3] at 0.5 deg). G3 needs at most 16 more on a
0.125-deg grid around the located angle. Call it 40 solves.

**Estimate: 40 x 3.93 s = 2.6 core-minutes**, run as **8 concurrent
single-process VSPAERO solves (these are separate processes, not MPI ranks;
VSPAERO is invoked without a thread flag here)**, so roughly 20 s of wall time.

The docket's `est_core_min` for this item is **30.0**, an estimate carrying no
rank count and no measured per-solve time. If the measurement lands near 2.6
the docket figure is over by about an order of magnitude, and that gap is
itself reportable: the item was ranked at 0.100 gain per core-minute on a price
nothing measured.
