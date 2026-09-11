# REFERRAL TO VERIFICATION — the graded statistic's own noise exceeds the signal it grades

**NOT FILED. NOT SENT. This is an internal referral drafted by a cfd `lab-lane`, 2026-09-11,
and it leaves no box.** It proposes nothing to anyone outside this repository (CLAUDE.md
rule 7). It is addressed to the verification team because the question is theirs, and it is
placed under the case it concerns rather than in a scratch path (rule 13).

**cfd has NOT touched the grading path and does not propose to.** This referral asks a
question; it does not answer one.

---

## 1. The observation, measured

`grade_mrf_np.py` grades `Np` from the value of `total_z` **at `endTime`** — one
instantaneous sample. Measured on the three MRF_R2 graded 4000 levels, from
`postProcessing/impellerForces/0/moment.dat` (quantity `total_z`, column 3, resolved from the
header by the frozen reader — **not** `viscous_z`):

| level | `Np` at `endTime` (the graded value) | mean, last 1000 iterations | relative sd, last 50 | multiple of the signal |
|---|---:|---:|---:|---:|
| coarse | 4.206205499 | 4.236737618 | 1.019e-02 | **2.87×** |
| medium | 4.221156836 | 4.225278355 | 1.010e-02 | **2.84×** |
| fine | 4.439168331 | 4.441224291 | 7.035e-03 | **1.98×** |

The level-to-level signal the triple must resolve is the **smaller** difference,
coarse→medium = **3.554590e-03** relative. (medium→fine is 5.164733e-02.)

**The graded statistic's own noise is 2.87× the signal it is being asked to resolve.**

## 2. Why this is not an iteration-count problem

The oscillation is present at 4000 and there is no measured reason to expect it absent at
8000; the relative sd over the last 1000 iterations (8.6e-03 on coarse) is the same order as
over the last 50. **No iteration count fixes a point sample of a fluctuating quantity.**

Note that S12 (MONITOR_STANDARD) already *saw* this: it called all three levels `PLATEAUED`
with monotone fractions 0.4675–0.5195, which its own standard glosses as *"a settled history
wobbles without displacement"*. **S12 correctly identified the wobble. What nothing did was
propagate the wobble into the uncertainty of the graded value.**

## 3. How it was found — by an instrument that grades nothing

Not by looking for it. A **free** comparison of the graded 4000 coarse level against the
ET8000 coarse level at iteration 4000 — same mesh, same config, a different `scotch`
partition — was taken to measure run-to-run reproducibility. Read as a point sample it gave
8.274582e-03 and fired a registered stopping branch. An adversarial check on that number,
run **before it travelled**, showed the difference collapses with averaging:

| window | relative difference | vs the registered criterion 5.095632e-04 |
|---:|---:|---|
| 1 | 8.274582e-03 | over by 16.5× |
| 200 | 4.419758e-03 | over by 8.8× |
| **1000** | **2.907564e-04** | **PASS** |

Between-run separation (1000-iteration means) ÷ within-run sd = **0.034**. The partitions
agree; the point samples do not. **The partition was never the problem. The sampling is.**

## 3a. THE SUBSTANCE OF THIS REFERRAL — a structural gap, not a broken instrument

**The question is not "is this grader wrong". It is:**

> ***WHY DOES A MEASURED WOBBLE NEVER REACH THE UNCERTAINTY OF THE VALUE IT WOBBLES AROUND?***

**The lab already had the measurement.** S12 measured this family's scatter, named it, and
wrote it down: all three levels `PLATEAUED`, monotone fractions **0.4675 / 0.4935 / 0.5195**,
which `MONITOR_STANDARD` itself glosses as *"a settled history wobbles without displacement"*.
The wobble was measured. It was recorded. **And then the grader took a point sample at
`endTime` as though it were a number without an interval.**

**Nothing in the pipeline joins those two facts.** Monitors measure scatter; graders take
point samples; **no instrument carries the first into the second.** S12 was not wrong,
`grade_mrf_np.py` was not wrong on its own terms, and the two never met. That is a
**structural gap**, not a bug in either — and it indicts the pipeline rather than any one
instrument.

**Which is why it generalises.** Any family whose monitor reports scatter and whose grader
reports a point value has the same gap, whether or not its numbers happen to be far enough
apart for it to matter. This one's numbers were not: the wobble is **2.87×** the signal.

---

## 4. What is asked of verification, and what is NOT

**ASKED:** whether a grading statistic whose own noise exceeds the level-to-level signal is a
`VERIFICATION_CHARTER.md` §2d.1 matter — a demonstrable error on a frozen, post-compute
grading path, established by an instrument that grades nothing — and if so, what the remedy
is for a rung already graded under it. The four §2d.1 conditions are the verification team's
to apply, not cfd's.

**NOT ASKED AND NOT PROPOSED:** no regrade, no change to `grade_mrf_np.py`, no change to any
band, threshold, cap or label, and no revision of MRF_R2's verdict. **MRF_R2 at 4000 remains
`NOT A RESULT` and that is unchanged by everything in this document.**

**DIAGNOSTIC ONLY, offered to show what the frozen choice costs and NOT as a verdict:**
rebuilt from 1000-iteration means the triple is coarse 4.236737618 / medium 4.225278355 /
fine 4.441224291 — **not even monotone**, where the point-sampled triple was.

## 5. Why it matters beyond MRF

***A Roache triple is meaningless unless the level-to-level differences exceed the noise in
the graded statistic — and this lab has never measured that noise for any family.***

The noise here is **within-run oscillation, not partition scatter**, which is the worse of the
two: partitions are one family's configuration choice, while point-sampling a fluctuating
quantity at `endTime` is present in **every** family that does it. The DrivAer successor
independently carries a registered requirement for *a plateau statistic that can see
amplitude, not a two-sample increment* — **two families, the same defect, found independently
within the hour.**

**Every `DIVERGENT` triple in this lab is a candidate for this explanation, and none of them
has the measurement that would test it. CANDIDATE, NOT CONCLUSION**: measured on one family,
at one iteration count, and the between-run half of it rests on a single pair with no degrees
of freedom.

## 6. A separate, smaller finding in the same evidence, also not fixed here

`scotch` partitions the same mesh differently on every invocation — four measured partitions
of one 154,715-cell mesh from one identical `decomposeParDict` (md5 `ea1336801ca0`,
`method scotch;`, no seed, no coeffs): 77900/76815, 77011/77704, 77505/77210, 76965/77750.
**This is ours, not an OpenFOAM defect** — the library offers deterministic methods and we
asked for none. It does **not** move the graded answer (§3 above), but it means **no parallel
run in this lab can be reproduced or re-graded from its inputs.** The durable repair costs
negative compute: decompose once per level and archive `processor*/constant/polyMesh` as a
run artifact. That goes to `MESH_STANDARD` as a **proposal**; cfd does not amend a standard.
