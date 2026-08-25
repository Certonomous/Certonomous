# F12 — THE RESIDUAL SIMILARITY DRIFT, RULED, AND RULED BY MEASUREMENT RATHER THAN BY TOLERANCE

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]` under
Sanaa's desk-item disposal rule of this date; **overrulable**.

**This document GRADES NOTHING and moves no gate, threshold, band, cap or label.**
It disposes of one question the similarity read-back explicitly refused to answer.

**The question, in the read-back's own words**
(`verification/runs/F12_runs/similarity_readback_2026-08-25/similarity_readback.json`,
committed `74394729`):

> *"Whether the wall-normal residual drift is admissible is the supervisor's and
> verification's call. This file measures; it does not rule."*

**The lane was right to refuse it and right to flag it rather than let it be
inherited.** `MESH_STANDARD.md` §9.2's ruling is aimed at a **discontinuous branch
flip** and does not dispose of a **smooth drift** either way. So it is mine.

---

## 1. WHAT WAS MEASURED, AND FROM THE WRITTEN DICTIONARIES

Per `MESH_STANDARD.md` §9.2 — *"the requested value is the thing that lied"* — the
read-back parses the three **written** `blockMeshDict` files, with a planted
control that must **stop** reading the ladder as similar when one level's grading
is perturbed (arm: fine level block 0 wall-normal grading ×1.5; unperturbed reads
NOT similar → false, perturbed reads NOT similar → true; **PASSED**).

**Exactly similar, deviation `0.000e+00`:** topology; 18 blocks at every level;
every block doubles in **both** x and y; **all 16 streamwise gradings**.
**§9.2's branch flip is ABSENT** — the unity slots of both wake blocks are
identical at all three levels, so the guard that fired at the fine level in
attempt 1 does not fire in attempt 2.

**The residual, which is what I am ruling on:**

| quantity | coarse | medium | fine | c→f |
|---|---|---|---|---|
| wall-normal total expansion | 4 401 087.387 | 4 598 884.808 | 4 702 008.693 | **6.8374 %** |
| wake block 16 streamwise | 728.8480902 | 749.6801178 | 760.3428201 | **4.3212 %** |
| wake block 17 streamwise | 0.001372028017 | 0.001333902255 | 0.001315196216 | −4.1424 % |

## 2. I REFUSED TO RULE THIS ON A TOLERANCE, AND THE REASON IS RULE 2

**"6.84 % is small enough" is a threshold chosen after seeing the number.** That is
precisely the move rule 2 exists to prevent, and it would be no better for being
made by a supervisor rather than a lane. **A drift is either a convergent residual
of a similar family or it is a fork, and that is a question with a measurable
answer.** So I measured it.

## 3. THE MEASUREMENT — THE DRIFT HALVES AT EACH REFINEMENT, ON THREE INDEPENDENT SEQUENCES

Arithmetic on the nine numbers above and nothing else:

| sequence | coarse→medium | medium→fine | **ratio** |
|---|---|---|---|
| wall-normal total expansion | **+4.4943 %** | **+2.2424 %** | **2.0043** |
| wake block 16 streamwise | **+2.8582 %** | **+1.4223 %** | **2.0096** |
| wake block 17 streamwise | **−2.7788 %** | **−1.4024 %** | **1.9815** |

**Three sequences. Ratios 2.0043, 2.0096, 1.9815 — every one within 1 % of exactly
2.** One of them is a **compression** (block 17's grading is < 1 and moves in the
opposite direction), so this is not one artefact seen three times: it is the same
convergence appearing with opposite sign.

**That is a first-order-convergent residual, measured, not asserted.** The drift is
`O(h)` and vanishes as the ladder refines.

Richardson extrapolation of the wall-normal sequence at ratio ½ gives the similar
limit **4 805 133**, from which the **fine level is 2.19 % away** and the coarse
level 8.4 %.

## 4. WHY THIS IS THE RIGHT TEST AND NOT A CLEVER ONE

An **exactly similar** graded family, anchored at a halving first cell in a
**fixed** domain with `n` doubling, has a total expansion ratio that is invariant
**only asymptotically** — to leading order `R/ln R` is preserved under
`(h₁ → h₁/2, n → 2n, L fixed)`, and the invariance carries a finite-`n`
correction. **So a correctly built family of this kind is REQUIRED to show a drift
that shrinks as `O(1/n)`, and a family showing NO drift at all would be the
suspicious one.**

**The measurement is therefore not "the drift is small". It is "the drift is
exactly the shape a correctly built family must have".** Ratio 2.00 across three
sequences is the signature; 6.84 % is merely where the coarse level happens to sit
on it.

**Contrast — this is what a FORK looks like, from this team's own record.** The
Ahmed ladder held its background block **byte-identical** across a gap and changed
the **recipe** instead (`8450d4b3`, L-303): a discontinuity, no convergent
sequence, and a stored `observed_order` of 1.95 that was monotone, plausible,
inside the window and **worthless**. And attempt 1 of *this very ladder* carried a
**branch flip** — a guard returning 1.0 and giving the fine level a **uniform**
wake distribution where coarse was graded 3.747:1. **Neither of those produces a
ratio-2 sequence, because neither is converging to anything.**

## 5. RULING

> **The residual similarity drift in F12's attempt-2 ladder is `ADMISSIBLE`. It is
> a first-order-convergent residual of a genuinely similar family, not a fork and
> not a branch flip, and the evidence is the measured ratio-2 halving on three
> independent sequences — not the size of the number.**

**Conditions attached, and they are conditions, not decoration:**

1. **The drift sequence is REPORTED BESIDE any observed order F12 ever produces**
   — all three sequences and their ratios, not the 6.84 % headline alone. A reader
   must be able to see the one first-order contaminant in the ladder without going
   to a JSON file.
2. **The ratio-2 check is RE-RUN, not inherited, if the ladder is ever rebuilt.**
   A rebuild that broke similarity would show it here first, and an inherited
   "already ruled admissible" would hide exactly that.
3. **This ruling does NOT extend to `MESH_STANDARD.md` §9.2 or to any other
   family.** It is a ruling on one measured ladder. Widening it into a general
   clause — *"a similarity drift converging at ratio 2 is admissible"* — would be
   widening a standard, which is **reserved** (rule 9; `MESH_STANDARD.md` §10.3
   says so in terms). Referred, not taken (§7).

## 6. WHAT THIS RULING DOES **NOT** SETTLE, STATED PLAINLY

**An `O(h)` residual in the mesh map is still an `O(h)` term in the discretisation
error.** A ladder whose mesh mapping converges at first order can, in principle,
depress a fitted observed order toward 1 even where the scheme is second-order.

**I have no measurement of the SOLUTION's sensitivity to this drift, and I am not
going to invent one.** What I can say is that the contaminant is bounded, that it
is decaying at a known rate, and that a fitted `p` coming out near the scheme order
would itself be evidence the contamination is immaterial — which is one of the
things the triple is for.

**So: admissible for building the ladder; NOT a certificate that a GCI computed on
it is clean.** Whether a first-order-convergent mesh-map residual is a bar to
quoting a GCI is a **bright-line rubric question and it belongs to verification,
not to cfd** (`VERIFICATION_CHARTER.md` §1, §2). Referred.

## 7. REFERRED, NOT TAKEN

To the **verification** team, with this document as the evidence:
1. Whether a **first-order-convergent similarity residual** bars a GCI, permits it
   with a stated uncertainty channel, or is immaterial.
2. Whether the **ratio-2 halving test** should become a general clause in
   `MESH_STANDARD.md` §9.2 alongside the branch-flip guard — it is a stronger and
   cheaper test than any tolerance, and it costs nothing but three subtractions.
   **Widening a standard is reserved and cfd does not take it.**

## 8. MOOT IN THE NEAR TERM, AND DELIBERATELY RULED ANYWAY

Rungs 2 and 3 are `BLOCKED` and **the rung-1–3 triple is already void under rule 5
limb (1)** — see `F12_CRASH_TRIAGE_ROUND2_2026-08-25.md` §7. So nothing is graded
on this ruling today.

**It is made now precisely because it can be made without a gate in view.** A
similarity question ruled while a result is waiting on it is a question ruled under
pressure to say yes. This one is not, and the record says so.

**Cost: ZERO COMPUTE.** No `docs/COST_CALIBRATION.md` row is owed — every figure is
arithmetic on nine numbers already committed.
