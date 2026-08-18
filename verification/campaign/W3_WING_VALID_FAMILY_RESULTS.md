# W3 — valid single-knob wing ladders: results

**Solved 2026-08-02 05:46:28 → 05:51:26 UTC**, controls to 05:57:44.
Pre-registration: `W3_WING_VALID_FAMILY_PREREGISTRATION.md`, committed at
83e28569 before any solver was launched. Items `agp-e71b0542e6f9` (NACA 0012)
and `agp-64393439352d` (NACA 4412).

---

## 1. The numbers

Cd is the mean over the final 20% of each rung's own force history, read from
that rung's `postProcessing/forceCoeffs1/0/coefficient.dat`. **All eight rungs
stopped on `residualControl`, not on a cap** — every one printed "SIMPLE
solution converged".

### NACA 0012 finite wing

| rung | cells | h-ratio | Cd | increment | 2σ (final 20%) | iters |
| --- | --- | --- | --- | --- | --- | --- |
| r1 | 140 545 | — | 0.012052229 | — | 5.45 × 10⁻⁷ | 153 |
| r2 | 224 431 | 1.16884 | 0.010405872 | −1.646 × 10⁻³ | 1.84 × 10⁻⁷ | 148 |
| r3 | 358 430 | 1.16889 | 0.008479216 | −1.927 × 10⁻³ | 8.90 × 10⁻⁷ | 142 |
| r4 | 525 692 | 1.13617 | 0.008435098 | **−4.412 × 10⁻⁵** | 2.64 × 10⁻⁶ | 156 |

### NACA 4412 finite wing

| rung | cells | h-ratio | Cd | increment | 2σ (final 20%) | iters |
| --- | --- | --- | --- | --- | --- | --- |
| r1 | 137 569 | — | 0.021671412 | — | 5.80 × 10⁻⁶ | 123 |
| r2 | 213 918 | 1.15853 | 0.020498598 | −1.173 × 10⁻³ | 1.87 × 10⁻⁶ | 117 |
| r3 | 340 996 | 1.16816 | 0.018966957 | −1.532 × 10⁻³ | 1.22 × 10⁻⁵ | 119 |
| r4 | 518 748 | 1.15010 | 0.021940394 | **+2.973 × 10⁻³** | 1.44 × 10⁻⁶ | 117 |

### The r1 control, and it is a good one

| body | r1 Cd, re-solved at 4 ranks | stored production Cd | apart |
| --- | --- | --- | --- |
| NACA 0012 | 0.012052229 | 0.012053 | 8 × 10⁻⁷ |
| NACA 4412 | 0.021671412 | 0.021672 | 6 × 10⁻⁷ |

The r1 rungs reproduce their stored production drag **to seven decimal
places**, across a change from 16 ranks to 4 and, on the 0012, across the
35-cell `locationInMesh` nudge. So the families are anchored on the act's own
mesh and the act's own answer, and neither the rank change nor the nudge moved
the physics. The NACA 0012 also converged in **153 iterations here and 153 in
the stored run**, iteration for iteration.

## 2. The fits, and the pre-registered predictions

| | NACA 0012 | NACA 4412 |
| --- | --- | --- |
| `observed_order` | **24.048** | none |
| `monotone` | true | **false** |
| `asymptotic` | true | — |
| `clamped` | true | — |
| `richardson_extrapolated` | 0.00843295 | none |
| `band_abs` | 1.4668 × 10⁻⁴ | 3.7168 × 10⁻³ |
| `guards_holding` | `order_window` | `monotone` |
| `conclusive` | false | false |
| **`uq.reportable_band`** | **None** | **None** |
| old two-recipe fit, for reference | p = 3.173, band 1.512 × 10⁻² | p = 10.467, band 1.129 × 10⁻² |

**P1 is scored FALSE.** It read: *"neither valid family returns an observed
order above 2.5 … An observed order above 2.5 on a single-knob family scores
P1 FALSE and the audit's central claim is wrong."* The NACA 0012 returns
**24.048**, which is further outside the window than the 3.173 the audit
blamed on the mixed step. **Removing the mixed step did not make the order
sane; it made it worse.** The audit's §4 claim that two-knob ladders fail on
arithmetic while one-knob ladders fail on physics is corrected in place, in
that file, rather than quietly dropped.

**P2 is scored TRUE.** The NACA 4412 comes back non-monotone. The prediction
was cheap — it was that at least one of two would misbehave, and every
single-knob family this lab has built has misbehaved — and it is recorded as
scored rather than dressed up.

**P3 is scored FALSE.** It predicted the NACA 4412 would move further in
relative terms because its old level-step moved Cd 5.5× more than its
background step. It moved **less**: the 0012's drag falls 30.01% across its
family, the 4412's net change is −1.24% and its largest excursion 12.48%. The
inference from the old ladder's step ratio did not transfer, which is another
way of saying the old ladder's numbers were not measuring what they appeared
to.

## 3. The control that reframes both results

**Not pre-registered.** It was added after reading §1, in the same shape as
R4's c4b: an **independent mesh at nominally the same resolution**, background
divisions (64 116 39) → (65 115 40), everything else identical, solved at the
same 4 ranks.

| body | r4 | r4b | | |
| --- | --- | --- | --- | --- |
| | cells / Cd | cells / Cd | \|ΔCd\| | vs the r3→r4 increment |
| NACA 0012 | 525 692 / 0.008435098 | 534 106 / **0.008255182** | 1.799 × 10⁻⁴ | **408%** |
| NACA 4412 | 518 748 / 0.021940394 | 561 528 / **0.018689055** | 3.251 × 10⁻³ | **109%** |

Both controls converged on `residualControl` (146 and 114 iterations) at 2σ of
3.48 × 10⁻⁶ and 2.91 × 10⁻⁵.

**On the NACA 0012 the mesh-to-mesh scatter is four times the increment the
p = 24.048 was fitted on.** The order is an artefact of a finest pair whose
difference is below the resolution of the mesh generator, and 24.048 is what a
power law returns when you divide a real increment by a number that is mostly
noise. The band 1.4668 × 10⁻⁴ is nonsense for the same reason; `conclusive` is
false and `reportable_band` is None, so nothing published rests on it, but the
number should not be read as a tight band that merely failed a window check.

**On the NACA 4412 the turn does not survive either.** r4b at 561 528 cells
reads 0.018689055, which is **below** r3's 0.018966957 — it continues the
descent that r4 appeared to reverse. The "non-monotone" verdict rests on a
+2.973 × 10⁻³ increment against a 3.251 × 10⁻³ mesh scatter. So the 4412's
ladder is not established as non-monotone; it is established as **unresolved**
at that rung.

### Why this is meshing noise and not the two noise sources already ruled out

* **Not iterative.** Every rung and both controls stopped on `residualControl`
  at 1e-4, with final-window 2σ between 1.84 × 10⁻⁷ and 2.91 × 10⁻⁵. The
  pre-registered gate **G2** — 2σ below 10% of the smallest increment — holds
  on both bodies: the 0012's worst rung is 2.64 × 10⁻⁶ against a smallest
  increment of 4.412 × 10⁻⁵, which is 6.0%, and the 4412's is 1.04%. **G2 held
  and G2 tested the wrong noise.** That is the honest reading: the gate I wrote
  before the solve measured iterative settling, and what defeats these ladders
  is the mesh generator. A gate for it belongs in the pre-registration next
  time, not in a section written afterwards.
* **Not decomposition.** All ten solves ran at 4 ranks, scotch, 34 392 to
  140 382 cells per rank.
* **Not a trend effect from the control's own cell count.** The 0012's r4b
  carries 1.6% more cells; at the ladder's own local sensitivity that predicts
  about 6 × 10⁻⁵ of change and the measured difference is 1.8 × 10⁻⁴, three
  times as much. The 4412's r4b carries 8.2% more cells, which on the r3→r4
  trend predicts about +4.7 × 10⁻⁴, and the measured difference is
  −3.25 × 10⁻³ — seven times the magnitude and the opposite sign.
* **Not mesh quality falling over.** checkMesh passes on all ten. Max
  non-orthogonality across the 0012's family is 36.3 to 44.0 and across the
  4412's 42.5 to 45.8, all far under the 70° gate, and neither degrades with
  refinement. The 4412's r4 does carry a max skewness of 3.165 against 1.49 to
  1.90 on its three coarser rungs — the one quality metric that moves — and
  that is a candidate mechanism for why an independently generated mesh at the
  same resolution lands 3.25 × 10⁻³ away. It is named, not claimed.

### Where the floor actually bites

The 0012's r2→r3 increment is 1.927 × 10⁻³, which is **10.7 times** the
1.799 × 10⁻⁴ mesh scatter. So the ladder is resolvable up to 358 430 cells and
stops being resolvable above it. **The useful statement is not "this wing's
ladder is inconclusive" but "this wing's drag cannot be refined past about
350 000 cells on this mesh family, because two meshes built to the same recipe
at the same resolution disagree by more than the next refinement step buys."**

> **CORRECTED 2026-08-02 06:10, by `W3_MESH_NOISE_FLOOR_RESULTS.md`.** The
> conclusions above stand; **the mechanism stated for them is half wrong, and
> the wrong half is the direction.** Replicates at all four rungs show the
> 0012's mesh scatter *falling* monotonically with cell count — 2.599 × 10⁻³,
> 1.112 × 10⁻³, 4.064 × 10⁻⁴, 1.799 × 10⁻⁴, an inverse-square law with
> scatter × N² constant to ±6% and a fitted exponent of 2.024. **The r4
> scatter is the smallest this generator produced, not the largest.** So the
> ladder did not run into rising noise; **its increment collapsed by a factor
> of 44 in one step** while the noise kept falling, and 4.08× is what a
> shrinking numerator does to a denominator that shrinks faster.
>
> The sentence "two meshes at the same resolution disagree by more than the
> next refinement step buys" is true at r4 and it is **more** true at r1,
> where the scatter is 158% of the increment. The dangerous rung is the
> coarsest one, not the finest, and every three-rung ladder in this corpus
> puts two of its three rungs at or below that resolution.

## 4. What this says about the corpus

Five genuine single-knob families now exist in this lab, on four geometries.
None of them shows the shrinking increments an asymptotic ladder requires:

| family | increments | ends |
| --- | --- | --- |
| B-52 (5 rungs, tonight) | −1.857e-3, +2.377e-3, +2.702e-3, −4.055e-3 | turns twice |
| Ahmed 25° (4 rungs, R4) | −5.442e-3, −5.367e-3, +8.895e-4 | turns |

**[AMENDED 2026-08-10 — chief ruling `8f5bf878`: the Ahmed row's "turns" is WITHDRAWN. Four same-recipe draws at c3 give s = 8.97e-4 even with the most extreme removed — 1.01× the +8.895e-4 increment in this row. With the B-52 row already withdrawn (`7abb0ba3`), **BOTH bodies this table called "turns" are now withdrawn.** See `campaign/R4_AHMED_TURN_WITHDRAWAL_2026-08-10.md`.]**

| NACA 4412 (4 rungs, tonight) | −1.173e-3, −1.532e-3, +2.973e-3 | turns, **inside the mesh scatter** |
| NACA 0012 (4 rungs, tonight) | −1.646e-3, −1.927e-3, −4.412e-5 | flattens, **inside the mesh scatter** |

**[WITHDRAWN 2026-08-10 — chief ruling `7abb0ba3`. The B-52 ladder's "turn" is withdrawn as a claim: the published −4.055e-3 is max(rung 6) − min(rung 7) of eight same-recipe draws, and re-estimated from all of them the rung 6→7 increment is +8.2e-5 ± 1.2e-3 (t = 0.071) — 49× smaller, opposite in sign, and smaller than the resolution-mismatch bias. A selected extremum is not a measurement. See `campaign/B52_TURN_WITHDRAWAL_2026-08-10.md`. Original text retained below.]** One of the four no longer turns, so the COUNT does not survive; the table does, amended.

**Four for four.** The recipe audit found a real defect and blamed the wrong
thing for the symptom. What the corpus looks like once the defect is removed
is a set of flows whose drag stops responding cleanly to refinement somewhere
between 300 000 and 500 000 cells — and on the two bodies where it was
measured, that is exactly where an independently generated mesh at the same
resolution starts to disagree by more than the refinement step.

**A prediction that is now available and was not before:** the B-52's turn at
441 057 cells and the Ahmed 25°'s at 454 691 sit in the same band, and neither
has had a replicate-mesh control at its turning rung. R4 ran one at c4b and
measured 9.7 × 10⁻⁵ against an 8.895 × 10⁻⁴ increment — 11%, which cleared the
**[SCORED 2026-08-10: this paragraph's recommendation was taken. The B-52's replicate WAS run, and so was the Ahmed's missing end. Both turns are now withdrawn. The prediction was right and the record acted on it nine days later.]**

Ahmed. The B-52's has never been run. **It should be, before the B-52's
oscillation is treated as physics**, and it is the single cheapest experiment
on this board: one mesh and one solve at 2 ranks, about 12 core-minutes on
tonight's measurement.

## 5. Cost

Cost is taken from `ExecutionTime`, not wall clock, because ten solves ran
three-at-a-time and wall clock reads the contention — the B-52 lesson from
earlier tonight.

| stage | ranks | cells/rank | ExecutionTime | core-min |
| --- | --- | --- | --- | --- |
| NACA 0012 r1–r4 | 4 | 35 136 – 131 423 | 336.61 s | **22.44** |
| NACA 4412 r1–r4 | 4 | 34 392 – 129 687 | 254.75 s | **16.98** |
| r4b controls, both | 4 | 133 527 / 140 382 | 204.94 s | **13.66** |
| meshing, all attempts including six discarded | 1 | — | — | **≈17** |
| **total** | | | | **≈70 core-minutes** |

Against `est_core_min` 40.0 for the two items — **75% over**, which the
pre-registration said in advance it would be and why: the items priced one
extra rung on an existing ladder, and what ran was two four-rung ladders that
did not exist plus two controls.

Against **my own** pre-registered estimate of 100–130 core-minutes it came in
at 70, **35% under the bottom of my range.** The cause is identifiable and
worth carrying: I assumed iteration counts would grow with refinement, because
R4 measured them growing 158, 212, 220, 623, 1668 and then not converging at
all on the Ahmed 25°. **On these wings they did not grow at all** — 153, 148,
142, 156 on the 0012 and 123, 117, 119, 117 on the 4412, flat across a 3.7×
change in cell count. So R4's "the steady solve stops being steady under
refinement" is a property of the Ahmed body, not of refinement, and it should
not be used to price a different body's ladder. I used it to price these and
over-paid by a third.

## 6. What is not changed

No `numerical` block on either wing's study record is refitted from these
numbers, and no credentials-wall row is rebuilt. The reason is in the
pre-registration's G5 and it is stronger now than when it was written: the
NACA 0012's published envelope of ±0.015 — **125.45% of the 0.01205 it sits
beside** — is the subject of the open ruling
`w3-a-declined-ladder-still-publishes-an-envelope`, and the number this
experiment would put in its place is one the experiment itself shows is below
the mesh generator's own resolution. A number that is about to be ruled on
should move once, by the ruling, and it should not be replaced by a tighter
number that is less trustworthy than the loose one.

What the study records get is what was measured: the family, the controls, and
the floor.
