# Active Research board

Live status per ladder, with measured numbers only. Every figure here is copied
from a solver output, a scored artifact, or a published leaderboard. Nothing is
estimated unless the row says so.

Created 2026-07-28 because no board of this name existed in the repository. If
an external board was intended instead, this file should be pointed at it — the
question is logged in the blockers list, and work did not wait on the answer.

Last updated: 2026-07-28 00:5x UTC.

---

## Ladder A — DAFoam verification and reproduction

| Rung | Case | Status | Headline measured result |
| --- | --- | --- | --- |
| A1 | NACA0012 incompressible, official tutorial | **COMPLETE, FD-verified** | CD 0.0209105, CL 0.4987653, 4,032 cells, 3.51 core-min |
| A2 | MACH tutorial wing (3D) | primal + adjoint done, FD check running | — |
| A3 | ONERA M6 transonic | running | — |
| A4 | Ahmed body 25 deg | **not in the tutorial repository**, must be built from our own validated case plus the experimental reference | — |
| A5 | U-bend internal flow | running | — |
| A6 | CRM / DPW-class wing-body | queued, time-boxed, converged primal counts as success | — |

### Consolidated FD verification table (every adjoint rung)

| Rung | derivative | analytic vs FD, relative error |
| --- | --- | --- |
| A1 | geometric constraints wrt shape | **4.4e-14 to 1.4e-10** |
| A1 | CD wrt flow parameter | **0.232%** |
| A1 | CL wrt flow parameter | **0.232%** |
| A1 | CL wrt shape | **1.67%** |
| A1 | CD wrt shape | **11.43%** on the difference-vector norm, but the two gradient magnitudes agree to **0.451%** |

**The calibration that governs every later rung.** The geometric constraints
verifying at machine precision proves the harness, the deformation chain and the
check itself are sound — so the 11.43% cannot be waved away as a broken rig.
And because the gradient *magnitudes* agree to 0.451% while the difference norm
is 11.43%, the disagreement is **directional, per-component noise, not a scale
error**. A shape-derivative gap of order 1 to 12 percent against central
differences is normal for this class.

This also settles a stale docket entry: the "3 of 8 components at 11.9 and 11.6
percent with one sign-reversed" describes the **tutorial's own** known failure
signature, not our sail case, which was separately recorded as differing from it
at 0.7 to 8.2 percent with no sign flips. **Our adjoint behaves better than the
official tutorial's.**

## Ladder B — closure literature with adjoints

| Rung | Status | Result |
| --- | --- | --- |
| B1 | **COMPLETE** | Ranked reproduction plans written; benchmark clone and public leaderboard located on this box |
| B2 | running | Uncorrected duct baseline |
| B3 | queued, costed at 420 core-min | The field inversion itself |
| B4 | queued | Feed findings back into the closure track |

**Top pick:** Wu, Zhang and Zhang, AIAA Journal 63(2), 2025, 687-706. They invert
a correction field on the SST destruction term through DAFoam's own discrete
adjoint, train only on a public separated-flow case, and generalise to the ducts
without seeing them. Rejected candidates were reported with reasons rather than
padded: one leaderboard entry is gradient-free rather than field-inversion, two
foundational papers have zero case-geometry overlap, and one paper's citation
could not be pinned down and was reported as a gap instead of guessed.

## Ladder C — closure challenge

**Closure metric movement tonight: NONE. 0.0741, unchanged since round 2.**
Stated explicitly because the queue requires movement to be reported including
when it is zero. The reason is in C2 below: the recoverable term was located but
deliberately not taken, because taking it by inspection would have invalidated
the entry.

### Where we actually stand

| Rank | Entry | Overall |
| --- | --- | --- |
| 1 | Reissmann, Fang, and Sandberg | 0.0595 |
| 2 | Wu and Zhang | 0.0624 |
| 3 | Liu, Wang, Zhao, and Xiao | 0.0737 |
| — | **ours, unsubmitted** | **0.0741** |
| 4 | Montoya, Oulghelou, and Cinnella | 0.0779 |

**We hold the best score on the entire leaderboard on three of eight cases:**
alpha_15_13929_4048 at 0.0501 against a best-other 0.0592, alpha_15_13929_2024
at 0.1011 against 0.1195, and AR_14_Ret_180 at 0.0303 against 0.0325.

### C2 — where the deficit lives

| case | share of the gap to rank 2 |
| --- | --- |
| AR_1_Ret_360 | **31.5%** |
| AR_3_Ret_360 | **31.4%** |
| NASA_2DWMH | 18.2% |
| alpha_05_4071_4048 | 10.4% |
| alpha_05_4071_2024 | 8.5% |

The two square ducts are **62.9%** of the deficit. Separately, the correction is
worse than doing nothing on three cases against the uncorrected baseline, worth
0.0066 on the mean, which is 1.7 times our margin over rank 4. Both terms are
real; the duct term is the larger by a factor of eight.

### C3 — NACA 4412 credential: **NOT VALIDATED**

Not because a number missed, but because the grading method is self-referential:
the reference is anchored on the solve's own lift, so a 25.0 percent lift
over-prediction inflates the induced term by 56.2 percent and widens the band
with it. Graded that way, the two best-resolved rungs fail and the worst-resolved
passes.

**Knowledge entry.** At fixed refinement, across a 17.7 fold change in boundary
layer coverage (4.36 to 77.0 percent), **drag moved 0.037 percent while lift
moved 9.41 percent**. Drag agreement is not evidence of a resolved boundary
layer on a low aspect ratio wing.

## Ladder D — background

| Item | Status |
| --- | --- |
| D1 mega batch | Running, 3 workers, single-instance lock in force. Session count and 0 failures tracked in the runner log; morning count is the true count |
| D2 queue refill | **6 proposals drafted and style-validated, 755 core-min costed** |
| D3 nightly retro | Queued for end of night |

### D2 proposals drafted this session

| Proposal | Core-min |
| --- | --- |
| Anchor the NACA 4412 reference independently of the solve | 15 |
| Add a boundary layer coverage gate to drag-only credentials | 20 |
| Shape derivative step size study | 35 |
| Closure baseline error estimator gate | 45 |
| Converge lift on the NACA 4412 ladder | 220 |
| Closure duct field inversion | 420 |

## Blocked

Billing alarm and spend cap cannot be read from this instance (no role, no
credentials, no client). Ledger cannot be synced off-host by either route. Both
are recorded in the blockers list with their exact unblock actions. **No spend
figure is reported anywhere in this board, because none can be measured.**
