# HLPW6 test case 1: what the compute number does not cover

Addendum to `FEASIBILITY_PROBE.md` in this directory, written 2026-08-01 as a
second pass over the same item. That record answers the question that was
asked — can `hlpw6-testcase1-coarse-grid-entry` run on this machine, and what
does it cost — and the answer stands: yes, at 4.55 GiB of 30.6, for 6,390
core-min at 14 ranks.

This note covers four things that no core-minute figure covers, and that
change what "approve this item" means. Two agents probed the compute question
in parallel; nobody had looked at these.

---

## 1. Under the item's own ABSOLUTE list, this entry can be prepared but never sent

The launch prompt forbids, verbatim: creating any account, requesting a
participant identifier, opening a merge request against the submission
repository, contacting the organisers, and joining a technology focus group
distribution list.

The workshop's submission mechanism is a **pull request against a public code
repository**. Participants fork `High-Lift-Prediction-Workshop/HLPW6-TC1` and
push a directory named `PID_Organization_Solver`, where `PID` is a
workshop-assigned participant identifier. The instructions state that the
submitter is assumed to already hold a free account with that hosting service
and point to its sign-up page if not
(`https://aiaa-hlpw.org/assets/HLPW6/HLPW6-GitHub-InstructionsRevA.pdf`).

So submission requires **all three** of the things the item forbids: an
account, a participant identifier, and a merge request. That is not a
contradiction in the item — it says "Prepare, do not send" and it means it —
but it has a consequence worth stating plainly:

> **The credential this proposal exists to chase is gated behind a decision
> only Katie can make, not behind any amount of compute.** Spending 6,390
> core-minutes produces a result that cannot leave this building until that
> decision is taken. The compute is the cheap half.

The grid download is genuinely unauthenticated and was done without any of
that; the workshop's own guidance is that the data are publicly available and
freely usable (`https://aiaa-hlpw.org/HLPW6/faq`, Q16). Downloading and
submitting are different gates and only the first one is open.

## 2. The required deliverables are a rendering job, and it is unpriced

Test case 1 asks for more than forces
(`https://aiaa-hlpw.org/HLPW6/TC1_Post`):

* surface streamlines,
* surface skin-friction-**magnitude** contours (magnitude, not the x
  component — the launch prompt already flags this),
* vorticity components and magnitude on defined volume cut planes,
* surface pressure and skin friction along named chordwise rows (WA to WG on
  the wing and slat, FA to FC on the flap) and spanwise rows (WSA to WSF),
* **five mandatory named views** (`VIEW_1_WING` through `VIEW_5_B2_BOT`) plus
  three vorticity views (`VIEW_6a/b/c`), produced against a
  **committee-supplied Tecplot layout file** with a fixed colormap (skin
  friction 0 to 0.02, orthographic camera, units in inches).

None of that is in the 6,390 core-minutes, and none of it is a solver run. It
is a post-processing and rendering pipeline this lab does not have, driving a
commercial visualisation package this lab does not appear to own, against a
layout file that assumes its own data structure. Reproducing those eight views
faithfully from OpenFOAM output is real, unestimated work, and it sits between
a finished solve and anything that could be called an entry.

**This is the same defect the forecast names in its own section 4.1: a
diagnosis priced as a rung, a grid priced without its iterations. Here it is a
solve priced without its deliverable.**

## 3. The case is blind, which is the item's strongest argument and is confirmed

The specification states that at the beginning of the workshop the case exists
only in computational form and no experimental data is available, and that it
will predominantly be used blind
(`https://aiaa-hlpw.org/assets/HLPW6/HLPW6_Test_Case_1_v1.0.pdf`). The kickoff
material adds that experimental data may appear mid-workshop.

That is worth confirming rather than assuming, because it is the whole reason
the proposal argues this credential cannot be an artifact of hindsight. It
holds.

The conditions are also self-consistent in a way that is worth recording,
because it is the check that the case was set up at the published state rather
than at a guess: the specification's reference static temperature 518.67 R,
static pressure 14.696 psi and MAC of 30 inches give rho = 1.225, a = 340.3
m/s, and at M = 0.20 a freestream of 68.06 m/s with nu = 1.46e-5 — standard
sea-level air, for which U x MAC / nu = 3.55e6, exactly the specified chord
Reynolds number. Three independently quoted numbers closing on the fourth.

## 4. Where the memory ceiling falls in the workshop's own grid levels

`FEASIBILITY_PROBE.md` puts this box's primal ceiling near 15 to 17 million
cells. The HeldenMesh fixed family publishes seven levels, and the useful form
of that statement is which of them this machine could actually take. Applying
the measured law (1.585e-3 MiB per cell plus 872 MiB at 14 ranks) with the
0.893 correction the real grid's face ratio earned:

| level | cells | predicted peak, 14 ranks | on a 30.6 GiB box |
|---|---:|---:|---|
| **3a** | **2,661,338** | **4,548 MiB (measured)** | **runs, 14.5% of the box** |
| 3b | 5,730,017 | ~8,900 MiB | fits comfortably |
| 3c | 17,156,244 | ~25,100 MiB | marginal, no room for anything else |
| 3d | 38,396,606 | ~55,100 MiB | does not fit |
| 3e to 3g | 121.6M to 933.9M | far beyond | does not fit |

Grid levels from the committee's published grid statistics for family
R.1.TC1.01 (`https://aiaa-hlpw.org/assets/HLPW6/grids/HLPW6_R1TC1_01_GridStats.png`).

**The lab can reach the second grid level of a workshop family on the hardware
it already owns.** That is a materially different sentence from the one the
docket has been carrying, and it is the one a grid-convergence claim would
need. It is also the honest ceiling: two levels of a seven-level family is not
a grid-convergence study, and the workshop's finer levels are not reachable
here at any iteration count.

## 5. What follows

Nothing here changes the compute verdict or the 6,390 core-min price. It
changes what the item is:

1. **The item as filed cannot produce a submission**, only a result. Whether
   that result is worth producing depends on whether Katie will lift the
   ABSOLUTE list, and that decision can be taken today, for free, before any
   core-minute is spent.
2. **If she will not, the item should be rescoped rather than run**: the value
   of a workshop entry that cannot be entered is the pipeline demonstration,
   and a pipeline demonstration does not need six angles.
3. **If she will, the deliverable pipeline needs its own estimate** before the
   solve is queued, because it is currently priced at zero and it is not zero.
4. **The reusable asset is unaffected and remains the best thing here.** The
   import path works and is validated on a production committee grid,
   regardless of what is decided about this entry.
