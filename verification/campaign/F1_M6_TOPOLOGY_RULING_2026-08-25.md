# ONERA M6 — THE MESH CANNOT PASS THE ADMISSION GATE AS BUILT, AND THAT IS A FINDING ABOUT THE TOPOLOGY

**Written by the cfd supervisor personally, 2026-08-25.** This is a
`SUPERVISION_CHARTER.md` §3 check-3 ruling — a conclusion large enough to change
this family's direction, taken only after the evidence was defended against
itself. `[lab-attributed]` under Sanaa's desk-item disposal rule of this date;
**overrulable**.

**Moves no gate, threshold, cap or label.** `MESH_STANDARD.md` §3.1's 70° hard gate
is **not touched** — retiring or widening a gate threshold is **reserved to Sanaa**
(rule 9). The frozen `verification/campaign/F13_ONERA_M6_PREREGISTRATION.md`
(blob `7456a7b3dc62`) is **not edited**.

**Evidence, all committed:** `ed726454` (the 38-variant sweep), `92dbcf96` (the
recovery that established the previous batch produced no mesh at all), and
`c6431c9e` (the earlier localisation, which this ruling **corrects on measurement
and does not discard**).

---

## 1. THE MEASUREMENT

**38 variants. `blockMesh` rc = 0 on all 38. `checkMesh` rc = 0 on all 38. ZERO
clear `MESH_STANDARD.md` §3.1's hard gate of 70° maximum non-orthogonality.**
Best **81.5834°**, worst **89.9638°**. Every number read from that variant's own
`log.checkMesh`, all 38 of which are in the tree.

**`MESH_STANDARD.md` §8.2 is NOT engaged**: no tool refused a topology, so no
topology was substituted to make a number appear.

## 2. THE THREE FACTS THAT CARRY THE RULING

**2.1 The maximum is NOT at the trailing edge.** `worst_nonortho.py` recomputes
every internal face with OpenFOAM's own pyramid-weighted cell-centre algorithm and
takes the argmax, under **two planted controls** that make it exit 2 without
printing if either fails: it must reproduce `checkMesh`'s own maximum to < 0.05°
(**achieved to 0.00002°**), and a displaced point of the winning face must move
that face's angle. The winner:

> `z0_tail_lo, i = 0, j = 31/31, k = 19/19`, centroid `(1.134134, −13.850016, 1.166844)`
> — **|y| = 13.85 of a 16.118 farfield radius. The OUTERMOST wall-normal cell.**
> Not a wall face. Not a tip-fill face.

**This CORRECTS `c6431c9e` on measurement, and the correction is a distinction, not
a retraction.** That commit localised the bad faces to the sharp trailing edge, and
**that is true of the > 70° POPULATION** — 516 of 598 faces in the tip fill, with
`locate_bad_faces.py --selftest` passing. **It is FALSE of the MAXIMUM, which is
the number §3.1 actually gates on.** The population and the maximum live in
different places.

**2.2 The floor is DIAL-INVARIANT, and both dials that touch it are frozen.**
`F1_BETA` and `F1_RFAC` are the only dials that reach that face, and **both are
fixed by the frozen pre-registration §5**. Swept as a diagnostic: `BETA`
`10.575549 → 1.0`, a **tenfold** change, moves the maximum **0.36°** and is then
**exactly constant at 81.5834 for beta = 8, 6, 5, 4, 3, 2, 1**, while the maximum
aspect ratio collapses `5934 → 570`. **The dial is unquestionably acting; the
maximum does not care.**

`worst_nonortho.py` on `b3_BETA_3` shows why: **the winning face has MOVED**, out of
the wrap and into the tip-fill aft strip. **Lowering beta removes one mechanism and
exposes a second sitting 0.36° below it** — which the `F1_MK` repair does not
remove either (81.5971).

> **Two independent mechanisms, disjoint dial sets, 0.36° apart. That is an
> ENVELOPE, not a defect being missed.**

Also inert on the maximum, bit-identical to seven figures: `CORE_S ∈ {0.25, 0.50,
0.75}` and `NR = 8`, all 81.9396. **`TSCALE` is the only dial that reaches the TE
angle and it is INADMISSIBLE — a thickened section is not the ONERA M6** — and it
makes the maximum worse anyway.

**2.3 BOTH mechanistic hypotheses were FALSIFIED BY MEASUREMENT.** Recorded because
a reader taking only the conclusion would otherwise inherit a story this lane
disproved.

- **The butterfly's degenerate strip corners are REAL and are NOT what the gate
  reads.** `block_corner_angles.py` (planted control: recovers 90/135/180° on quads
  exact to < 1e-9 by construction, and sees a displaced corner move) finds **four**
  tip-fill blocks with corners of **exactly 180.000000°** — the core corners `mle`
  and `mte` sit at the same chordwise stations as the surface break points, so three
  corners of each side strip fall on one vertical line. The `F1_MK` repair removes
  all four at any `MK ≥ 0.25` — **and the maximum does not move by one digit**:
  81.9396 with and without, severe faces 598 → 610. *(A first attempt, `F1_MSHIFT`,
  only relocated the degeneracy: the strip corner deviates by `atan(CS·t/d)` and the
  core corner by `90 − atan(CS·t/d)`, so **the two deviations sum to exactly 90 for
  every offset**. It can be shared, never removed.)*
- **The sharp-TE wedge floor of `90 − 2a` is WRONG IN SIGN.** The wedge does open as
  `U2 → 1` (7.358° → 41.820°), predicting the maximum should **fall** to 48°.
  Measured it **RISES** monotonically 81.9396 → 89.9638 while the aspect ratio
  explodes 5934 → 310 120.

## 3. RULING

> **The ONERA M6 mesh as built CANNOT pass `MESH_STANDARD.md` §3.1. This is a
> finding about the TOPOLOGY, not about the dials. The trailing-edge study was
> answering the wrong question, and the sweep is what proved it.**
>
> **The butterfly-with-tip-fill topology is `GATE FAIL` against §3.1 on its own
> admission check — 81.5834° against a hard gate of 70°, dial-invariant.**
>
> **The dial question is CLOSED. No 39th variant of this topology is to be built.**
> `BETA`, `RFAC`, `CORE_S`, `NR`, `MK`, `MSHIFT` and `TSCALE` are all answered and
> the answers are on disk.

**M6 is Sanaa's named second HOLDS path and it is held ONLY by its own admission
gate** — not by cost, and under her 2026-08-25 lift cost is no longer a reason to
hold anything.

## 4. THE CHEAPEST TEST OF MY OWN RULING, AND I HAVE ORDERED IT RUN FIRST

A ruling this size should be attackable, so I have named the experiment that would
break it.

> **Replace ONLY the outer blocks with an orthogonal far-field shell, leaving the
> near-body butterfly untouched.**
>
> **If the maximum drops below 70°, my ruling is confirmed in its strong form: the
> near-body butterfly was never the problem.**
> **If it does not, my ruling is WRONG and the near-body topology is implicated
> after all — and I want to know that.**

A lane is building it now under
`verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study/`, with a C-H grid and a
true O-grid wrap as the fallbacks. `blockMesh`/`checkMesh` are serial and cheap;
this is minutes of compute, not hours.

**The measurement standard is the one already set on this case:** whatever the lane
concludes about the outer-boundary mechanism, it must show it with a computed face
normal and a cell-centre vector through `worst_nonortho.py`'s own algorithm, and it
must be able to **make the number move by moving a point**. Two hypotheses on this
case have already been killed by measurement; a third gets the same treatment.

## 5. THE LAWFUL ROUTE FOR THE FROZEN PRE-REGISTRATION

`F13_ONERA_M6_PREREGISTRATION.md` is frozen at blob `7456a7b3dc62` and its disk copy
hash-matches. **It is UNFIRED — no solver has ever run under it.**

**Ruling on a question a reader will otherwise have to guess at: the 38-variant
sweep did NOT close its gates.** Those variants ran an **unregistered trial
generator** producing `blockMesh`/`checkMesh` only; they are a **mesh admissibility
diagnostic**, not the registered experiment, and no gate quantity was read from
them. "First compute" in rule 2 means the registered experiment. **So an amendment
is still legal**, and it must state its condition and how it was checked by naming
the run directories that do not exist, `test -e`'d **in the same shell invocation**
as the assertion.

§5 of the freeze fixes `BETA` and `RFAC`, so a topology change touches it. **Rule 6
governs: appended at the foot, version bump, and `lines whose number changed above
this section: 0` MEASURED by diffing the leading lines against the HEAD blob, never
asserted.** The lane drafts it; **it comes to me before it is committed, and nothing
fires until then.**

## 6. VERDICTS

| object | verdict | number |
|---|---|---|
| M6 butterfly topology vs `MESH_STANDARD.md` §3.1 | **`GATE FAIL`** | 81.5834° best of 38, against a 70° hard gate; dial-invariant |
| F13/F1 ONERA M6 registered ladder | **`BLOCKED`** | on its own admission check, not on cost |
| the trailing-edge dial study | **closed** | both hypotheses falsified by measurement; maximum is at the farfield, not the TE |

## 7. THE LESSON, AND IT LANDED TWICE IN THIS TEAM ON ONE DAY

F1: the >70° **population** is at the trailing edge; the **maximum** is at the
outermost farfield cell. F12: the departure **origin** is on the aerofoil; the
**terminus** is in the wake (`F12_CRASH_TRIAGE_ROUND2_2026-08-25.md` §2).

**Both times a reader was one step from concluding the earlier localisation was
wrong. Both times it was right about a different quantity.**

> **Name the quantity before you name the place. "Where is it worst" and "where is
> it made" are different questions, and a localisation answers only the one it was
> asked.**

Filed for landing as a lesson by a lane; recorded here so it survives if that lane
dies.

## 8. COST

**The 38-variant sweep is a completed process and rule 12's calibration is owed on
it** — by the lane that ran it, against its own estimate, in `docs/COST_CALIBRATION.md`,
with **waste named separately** and dollars **derived at $0.0513/core-h, not
measured**. Flagged here as **owed, not filed**, because I did not run it and will
not state an actual I did not read from a log. **This ruling itself is ZERO
COMPUTE** and owes no row.
