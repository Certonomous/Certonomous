# 🔴 DRAFT — NOT AUTHORISED TO LAUNCH. SUPERVISOR CHECK 4 HAS NOT BEEN PERFORMED.

**Nothing here may be launched.** This is the successor to the retired H5 arm.
`cfd-supervisor`'s check 4 is personal and undelegable and **has not happened**.

**✅ THE RULE-2 OBSTACLE IS CLEARED — updated 2026-09-04.** This document was
first committed carrying, in this position, a notice that it was **NOT
FREEZABLE** because the comparator it specifies did not exist and §8's blob slot
was empty. **`analyse_f28_h5b.py` now exists, is selftested, is mutation-
controlled, and is committed at blob `347db71584ffc600365e039a88b24806ff2b50a4`**
(§8), together with the launcher and the coverage probe. All three were committed
**before** their blobs were recorded here, so no state has ever named a
non-existent object. **The document is now freezable.**

**It is still a DRAFT and still may not launch.** Freezable is not frozen, and
frozen is not authorised: **check 4 has not been performed.**

**Date:** 2026-09-04 · **Team:** cfd · **Lane:** `lab-lane`
**Run root this registers:** `verification/runs/F28_runs/H5A_L1_dp1000_U20` —
**does not exist**, checked by directory listing immediately before writing this.
**Parent rung:** `F28G_L1_dp1000_U20`, `NOT A RESULT` at `23eeff7e`.
**Predecessor:** `F28G_H5_RESIDUAL_FIELD_PREREGISTRATION.md` — **its gates are
closed and none of them transfer.**

---

## 1. WHY THE PREDECESSOR WAS RETIRED, IN ONE PARAGRAPH

The H5 arm as frozen is **`NOT A RESULT` — its measurand was confounded**,
established **before** the arm ran. OpenFOAM writes
`finestResidual = tsource() - Apsi` (`GAMGSolverSolve.C:72`), **un-normalised**;
in finite volume each cell's equation is integrated over its own volume, so
`|r|` carries cell volume. **Two independent routes to the same diagnosis:**

- **From the residual:** Spearman ρ = **+0.8034** between `abs(residual)` and
  cell size; the top-355 cells at **176,034×** the median size; **248 of 355**
  shared with the top-355 **by size**.
- **From the zone geometry alone, touching no residual:** `Z-ELSEWHERE` is
  **51.1 % of the cells and 99.9868 % of the VOLUME**, so a volume-carrying
  quantity lands there **by construction**.

Everything below inherits the predecessor's §1–§4, §6, §10 and §12 **by
citation**. Its **gates, thresholds, zones and labels are inherited by
NOTHING.**

---

## 2. THE MEASURAND — RESIDUAL DENSITY, AND WHY IT IS FORCED

> **The gate quantity is the residual DENSITY `d_c = r_c / V_c`**, on **real**
> cell volumes from `postProcess -func writeCellVolumes`.

**Forced by dimensional reasoning, stated without reference to any outcome:**
`r_c` is the residual of cell `c`'s equation **integrated over that cell's
volume**. Measured on this mesh, real cell volumes span
**1.406118e-16 → 4.687060e-02, a max/min ratio of 3.333e+14**. Comparing raw
`r_c` across cells differing by **fourteen orders of magnitude** in volume
compares incommensurable quantities; only the density is comparable.

**A candidate that was ruled and then refuted, recorded because the refutation is
part of why this one is trusted.** `cfd-supervisor` first ruled a
`normFactor`-matched replacement. `lduMatrix::normFactor` is a **single global
scalar per solve**, so dividing by it is a uniform rescale: measured, `f1%` RAW
and `f1%` normFactor-matched were **0.9979393588 both, difference 0.000e+00, the
same 355 cells**, and **identical coverage on both fields**. It restores
commensurability **exactly** and removes **none** of the confound. He withdrew it
as his error.

**⚠ NON-BLINDNESS, DISCLOSED.** The density proposal was made **after** seeing
that it moves the zone tally to Z-DUCT/Z-HUB. **The discharge is publication, not
assurance:** §4.4 requires **all three candidates — raw, `normFactor`-matched and
density — to be reported every time**. Agreement makes the choice moot;
disagreement **is** the finding.

**Real volumes are mandatory.** The vertex bounding-box proxy used to convict the
predecessor gives Spearman **+0.9843** against real `V` but a `proxy/real` ratio
spanning **1.000 → 416.544**: **it ranks well and scales badly.** Adequate to
convict; **inadequate as a gate quantity.** It is not carried forward.

---

## 3. THE PROPOSITION

> **P′.** At the parent rung's plateau, the cell-wise **gating** initial residual
> **density** of `p` is **spatially concentrated** — the 355 cells (1 %) of
> largest `|d|` carry at least **half** of the domain-summed `|d|` — **stably
> across at least 4 of 5 decorrelated snapshots**.

**`p` ONLY.** `Uy` is **reported and not gated** — §5.3 records why, and it is a
finding about the zone set rather than a defect to be engineered away.

**Why `p` is not a retreat:** the founding argument was always about the **gating
solve of pressure** — the quantity `residualControl` tests
(`simpleControl.C`/`solutionControl.C`, predecessor §2.3) and whose global norm
is the challenged-and-upheld `0.1578798513`.

---

## 4. THE GATES

`N_top = floor(0.01 × 35544) = 355`. **The null for every zone statistic is the
COUNT fraction**, because the statistic is a share of the **top-N by density**
and under uniform density every cell ties, so the top-N is an arbitrary subset
and each zone's expected share is its share of **cells**. *(Volume fraction is
the null for a share of TOTAL mass — a different statistic. Both are published in
§4.5.)*

### 4.1 GATE G1 — CONCENTRATION. **GATED.**

| | |
|---|---|
| statistic | `f1% = (Σ|d| over the 355 largest) / (Σ|d| over all 35,544)` |
| **null** | `355/35544 = 0.0099876` |
| **threshold** | **`f1% ≥ 0.50`, i.e. ≥ 50.06 × the null** |
| **PASS** | in **≥ 4 of 5** snapshots |
| **GATE FAIL** | otherwise, by the named condition of §4.3 |

**The threshold is set fresh, and the number coincides with the predecessor's
because the ARGUMENT is the same, not because it was carried over.** The plain
meaning of "concentrated" is *a minority of cells carries the majority of the
quantity* — that statement fixes 0.50 independently of any observation, and it is
what put the predecessor's threshold **50×** above its null. **A threshold
anchored to a null computed from geometry cannot be tuned by an observation.**

**⚠ AND THIS GATE CAN ACTUALLY FAIL, WHICH THE PREDECESSOR'S COULD NOT.** The
single observed density value is **`f1%` = 0.6496**, clearing 0.50 by only
**1.30×** — where the predecessor's raw 0.9979 cleared it by 2.0× and could not
plausibly have failed. **Disclosed: I have seen 0.6496.** I am registering the
threshold anyway, because it is fixed by the plain-meaning argument and not by
that number — and **a gate that can fail is a better gate than one that cannot.**

### 4.2 GATE G2′ — EXCLUSION. **GATED, SYMMETRICALLY, OVER ALL FIVE ZONES.**

**Applied identically to every zone, with no zone named in advance as the
expected one.** For each zone `Z`:

| | |
|---|---|
| statistic | `share(Z)` = Z's fraction of the top-355 `|d|` mass |
| null | Z's **count fraction** (§4.5) |
| **EXCLUDED** | `share(Z) ≤ 0.10 × null(Z)` — *carries less than a tenth of what chance alone would give it* |
| **stability** | the exclusion must hold in **≥ 4 of 5** snapshots |

**Why symmetric.** The sharp statements in the pilot were the negative ones, and
I saw them before proposing this. **The discharge is that the rule is uniform:**
it is not written for the zones that came back zero; it is a rule that would fire
on **any** of the five, and a reader can check that it would.

**Why exclusion has headroom where attribution does not.** Measured against
their nulls, the attribution figures are Z-DUCT **2.10×**, Z-HUB **3.80×**,
DUCT+HUB **2.66×**, NAMED union **2.04×** — all knife-edge, and **structurally
so: the four named zones already occupy 48.9 % of the cells**, so no attribution
threshold on this zone set can reach G1's 50× headroom. That is a property of the
zone set, not of the run. **Exclusion is measured against a floor of zero and is
not subject to it.**

**Registered BEFORE the run, so it cannot be presented as a discovery:** if
**Z-AXIS** is EXCLUDED across the required snapshots, **that is a result about
H4**, whose entire content is the near-axis extreme aspect ratio (checkMesh max
53,458.4; smallest strictly-positive point radius on this mesh 2.592e-06 m). An
exclusion at the axis is **evidence against H4**. If it is **not** excluded, H4
is **not** thereby supported — the gate is one-directional and says so here.

### 4.2a 🔴 G3′ IS LOAD-BEARING, NOT SUPPORTING — A CONSEQUENCE OF THE 1.30× MARGIN

**Registered explicitly rather than left implicit.** The retired gate's raw
`f1%` of 0.9979 cleared 0.50 by **2.0×**, so its stability requirement was
**almost decorative** — no plausible snapshot variation could have changed that
verdict. **This gate clears by 1.30×.**

> **At 1.30×, SNAPSHOT-TO-SNAPSHOT VARIATION CAN DECIDE THE VERDICT. G3′'s
> "4 of 5" requirement is therefore doing REAL work, not ceremonial work: the
> concentration verdict is genuinely at risk from instability.**

**Consequence, binding on every reader and on any report:** **a single-snapshot
`f1%` may NEVER be quoted as the result.** The 0.6496 already on record
(predecessor §15C.2, §15F.2) is one snapshot of a `NOT A RESULT` run and is
disqualified three ways over; it is **not** a preview of this gate's outcome.

### 4.2b THE NUMERICAL DETERMINISM RULES — FIXED HERE, BEFORE THE COMPARATOR IS WRITTEN

**`cfd-supervisor`'s instruction, and the reason: at this margin an incidental
implementation choice could move the third digit and therefore the verdict, and
"an unregistered implementation detail that can flip a gate is a threshold nobody
voted on."** These are fixed by this document and **not** by whatever the code
happens to do:

| # | choice | **REGISTERED RULE** |
|---|---|---|
| D1 | how many cells in the top set | **exactly `N_top = floor(0.01 × 35544) = 355`, by COUNT** — never "355 plus ties", never a rank-with-ties set of variable size |
| D2 | ordering, and tie-breaking | sort by the **total order `(−|d_c|, c)`** — magnitude descending, then **cell index ascending**. A total order, so the result does not depend on sort stability or on input order |
| D3 | accumulation of both sums | **`math.fsum`**, which is **exactly rounded and therefore order-independent**. This does not *choose* an accumulation order; it **removes the question** |
| D4 | the density | `d_c = r_c / V_c` then `abs`. `V_c > 0` for every cell, so `abs(r_c/V_c)` and `abs(r_c)/V_c` are identical; D3 governs the sums either way |
| D5 | the comparison | `f1% >= 0.50` **exactly** — no tolerance, no epsilon. Likewise `share(Z) <= 0.10 × null(Z)` exactly |
| D6 | zone shares | same `fsum` rule as D3, over the same top-355 set from D1/D2 |

### 4.2c THE FRAGILITY CONTROL — MEASURED, AND THE GATE IS ROBUST TO NUMERICS

He required a control: *"perturb the tie-breaking rule and show the verdict does
not move, or show by how much it does."* Measured on the pilot's real field,
before writing the comparator:

| combination | `f1%` |
|---|---|
| index ASC + `fsum` | 0.64960682870616526 |
| index DESC + `fsum` | 0.64960682870616526 |
| random tie-break + `fsum` | 0.64960682870616526 |
| index ASC + naive left→right | 0.64960682870616038 |
| index ASC + naive right→left | 0.64960682870616548 |
| index ASC + ascending-sorted sum | 0.64960682870616560 |

| | |
|---|---|
| **spread, max − min** | **5.218e-15** |
| margin above threshold | 0.149607 (**1.30×**) |
| **spread as a fraction of the margin** | **3.49e-14** |
| **does the verdict move?** | **NO — every combination agrees** |

**And tie-breaking is moot on this data, measured rather than assumed:** all
**35,544 values are distinct**; the value at rank 355 is `8.9928e+01` and at rank
356 is `8.9215e+01`, a **0.8 % relative gap**, with exactly **one** cell at the
cut. D2 is registered anyway, because a future snapshot may tie and the rule must
not be invented at that moment.

> **THE HONEST SUMMARY, AND THE TWO HALVES POINT OPPOSITE WAYS: this gate is
> FRAGILE TO PHYSICS AND ROBUST TO NUMERICS.** Snapshot-to-snapshot variation can
> decide it (§4.2a); implementation choices cannot, by fourteen orders of
> magnitude. **G3′ carries the risk; the determinism rules carry none of it.**

### 4.3 GATE G3′ — STABILITY, and the three named conditions

Five snapshots at **15040, 15080, 15120, 15160, 15200** (spacing justified at
predecessor §5.4; the lag-40 autocorrelation remains an **interpolation**, which
is why `≥ 4 of 5` tolerates one outlier).

**Any G1 or G2′ shortfall names WHICH of three exhaustive conditions fired** —
the repair already landed in the predecessor's comparator and carried forward:

- **INSUFFICIENT** — fewer snapshots than required. The gate **cannot be
  judged**: verdict **`NOT A RESULT`**, no physics conclusion, no hypothesis
  touched.
- **DIFFUSE** — enough snapshots, **none** reached threshold. **The only
  condition in which an H4 gloss is legitimate.**
- **UNSTABLE** — enough snapshots, some reached threshold but too few.
  **Concentrated, not stably so. NOT diffuse, no H4 gloss.**

### 4.4 LOCATION ATTRIBUTION — **REPORTED, EXPLICITLY NOT GATED**

Every zone's share is reported **beside its null and its multiple**, for **all
three candidate quantities**, every time.

> **NO LOCATION-ATTRIBUTION GATE IS REGISTERED AND NO LOCATION-ATTRIBUTION CLAIM
> IS GRADED.** A bare `0.5262` can be cited as though it had passed something; a
> `0.5262 (null 0.2510, 2.10×, UNGATED)` cannot. **This mitigation is required
> because "reported but not gated" is L-478's family** — *a name is not a
> control* — and a printed figure with no gate behind it is exactly the shape
> that gets cited later as if it had one.

### 4.5 THE NULLS — properties of the mesh and the zones, of no run

| zone | cells | **count fraction (the null)** | volume fraction |
|---|---|---|---|
| Z-DISK | 700 | **0.019694** | 1.663321e-06 |
| Z-DUCT | 8,923 | **0.251041** | 3.767350e-05 |
| Z-HUB | 4,405 | **0.123931** | 3.115737e-06 |
| Z-AXIS | 3,350 | **0.094249** | 9.009345e-05 |
| Z-ELSEWHERE | 18,166 | **0.511085** | **0.9998675** |

Zone envelopes and their precedence order are **unchanged** from predecessor
§5.3 and are **not** redrawn. **In particular the `Z-DUCT` lower bound stays at
`x ≥ 0.0000`:** two cells at `x = −2.51e-06` and `−1.53e-05` carrying **0.3 %**
of the top-355 mass are **correctly** outside it. They do not round negative —
they **are** negative, by 10¹⁵–10¹⁶ times the double-precision resolution there —
so an "epsilon justified by centroid precision" would be **a boundary move
wearing arithmetic's clothes**. `cfd-supervisor` authorised such an epsilon on a
description of mine that was wrong, and **withdrew it** when the coordinates were
read. **Change nothing is the disposition.**

---

## 5. WHAT IS FIXED BY THE SUPERVISOR

1. **Concentration is gated; location attribution is not** (§4.1, §4.4).
2. **Exclusion is registered symmetrically over every zone, or not at all**
   (§4.2), and **tested across snapshots**.
3. **`p` only.** `Uy` is reported UNCOVERED and **not fixed** (§5.3).
4. **The null is the count fraction** (§4.5).
5. **Labels:** `GATE FAIL` when a threshold is missed; **`NOT A RESULT`** when
   the run is not strictly complete (§6), when the grid triple is not
   `CONVERGING`, or when a gate could not be judged. **Never a softened
   `PENDING`.**
6. **No reuse of the parent's verdict.** `F28G_L1_dp1000_U20` is `NOT A RESULT`
   and **a `NOT A RESULT` is not a baseline.**

### 5.3 `Uy` IS REPORTED UNCOVERED AND IS NOT FIXED

Measured: `Uy`'s density coverage is **0.2492** — **258 of 355** top cells and
**75.1 %** of the mass fall **outside every named envelope**, spread over
x ∈ [−0.030, 2.513] and r out to **2.898**. **Real spread, not a boundary
artifact.**

> **This is a FINDING ABOUT THE ZONE MODEL, not a defect to engineer away. The
> four named zones do not describe where `Uy`'s residual density lives.** It is
> published here as a **permanent limitation of the zone set**. If anyone ever
> wants to gate `Uy`, **the zones must be derived from geometry or physics
> INDEPENDENTLY, pre-registered, and only then tested against data — never drawn
> to contain an observed distribution.**

### 5.4 🔴 NAMED LIMITATION — SINGLE GRID. NO ROACHE VERDICT IS POSSIBLE

Carried forward from predecessor §5.5a and **not** weakened. **This is a
single-grid spatial diagnostic and may never produce a Roache-gated verdict.**
Rule 5 gates on a triple; there is no triple; a triple that does not exist cannot
be `CONVERGING`. **No GCI may be computed or quoted, and no result may be
labelled grid-converged.** P′ is about **where the residual density sits on ONE
mesh**, not about whether that location is **mesh-independent** — and H4, being a
hypothesis *about the mesh*, can be implicated or excluded but never confirmed at
one level. **The same structural shape as Rung 2's single-refinement-level gap**,
and the two should read as one class.

---

## 6. STRICT COMPLETION (standing rule 4)

Unchanged from predecessor §7 **including its two substitutions, both already
ruled**: `ExecutionTime count == endTime − startTime` = **200** (approved as a
faithful restatement for a restart), and the age-guard anchor
**`RESTART_SENTINEL`**, written by the launcher as its last action before the
solver line — **not `0/p`, which is inherited from the parent's launch and would
make the guard vacuous.**

**Proven by running, not by reading** (predecessor §15C.1): with amendment 3 the
solution fields land at `endTime` and `processor0` holds `0, 15000, 15072` and
nothing else.

---

## 7. CONTROLS (standing rule 3)

1. **Planted zero.** `Σ|d| > 0`; a zero sum **REFUSES (exit 2)**, never grades.
2. **Commensurability / the founding argument's own falsifier.** The **raw**
   field, `normFactor`-matched, must give `Σ|r| / (.dat scalar)` **constant
   across the five snapshots to 1 part in 10³**. **If it is not constant, the
   commensurability claim is false and the arm's founding argument fails with
   it.** Single-snapshot values recorded for comparison: `p` **1.831866e+02**.
   *(This limb has never run — one snapshot has no constancy to test.)*
3. **Injected perturbation.** `PLANT = 1.234e-03` written into a **scratch copy**
   and read back through the same path; refuse if unseen.
4. **Coverage control.** A synthetic concentration placed **outside every
   envelope** must report **UNCOVERED**, not be silently binned;
   `f28_h5_coverage_probe.py --selftest`, blob
   `a34be22ed89ea8f9db606f0eaee8d7ee5981df17`, eight limbs.
5. **Field identity.** Six `initialResidual:*` fields, **35,544 values each**,
   read by the **prefix** name `initialResidual:p` — **never** a suffix matcher.
   *(A suffix pattern matches none of `initialResidual:p`, `initialResidual_p`,
   `initialResidualp` and does match `pResidual`, which the solver never
   writes.)*

---

## 8. THE GRADING PATH — AND THE GAP

| file | blob |
|---|---|
| `run_f28_h5.sh` (launcher, unchanged, mode `arm`) | `f3534f1be02768a35b9449ef8ed38b171560a034` |
| `f28_h5_coverage_probe.py` | `a34be22ed89ea8f9db606f0eaee8d7ee5981df17` |
| **`analyse_f28_h5b.py`** | **`347db71584ffc600365e039a88b24806ff2b50a4`** |

**§8.1 THE DOCUMENT IS NOW FREEZABLE.** All three blobs exist and are committed;
the file was committed **before** its blob was recorded here, so no state has
ever named a non-existent object. The banner at the top of this document is
updated accordingly: **it remains a DRAFT NOT AUTHORISED TO LAUNCH — check 4 has
not been performed — but the rule-2 obstacle is cleared.**

**§8.2 THE COMPARATOR'S MUTATION CONTROL CONVICTED MY OWN SUITE TWICE.** Recorded
because a suite that was once blind in a specific way should say where.

| mutation | first suite | after repair |
|---|---|---|
| D1 — "355 plus ties", variable-size top set | caught | caught (6 checks) |
| **D3 — naive accumulation replacing `fsum`** | **PASSED** | caught |
| D4 — non-positive-volume guard removed | crashed the suite | caught cleanly |
| **EXCL — Z-DISK and Z-AXIS hard-coded to share 0** | **PASSED** | caught |

- **D3 slipped through** because the limb asserted that `math.fsum` is
  order-independent — *a fact about the standard library, not about the code
  under grading*. It now drives `concentration` itself on a field where the two
  answers differ.
- **EXCL slipped through** because the limb placed the mass in `Z-DUCT` once, and
  the two zones the mutation zeroed were expected to be excluded anyway. **The
  limb now rotates the carrier through all five zones**, so any zone that cannot
  carry mass is caught. **That mutation is exactly the zone-specific
  special-casing §4.2's symmetry rule exists to forbid**, and the first suite
  would have certified it.

**Ordering, as ruled and now used by default: the file is committed FIRST and its
blob recorded in a LATER commit**, so no state ever names an object that does not
exist. **Trackedness is tested by the blob at HEAD (`git rev-parse HEAD:<path>`),
never by `git ls-files`, which under the private-index protocol under-reports.**

---

## 9. COST

**Cap: 2.67 core-min**, set by `cfd-supervisor`, unpadded. **An overrun stops the
arm; it does not get a new budget.**

```
200 × 0.042399 × 2.0 × 1.5  = 25.44 s   solve, at the pilot's MEASURED rate
  5 × 0.035    × 3.0        =  0.53 s   five snapshot writes, measured
  5 × 2.31                  = 11.55 s   reconstruct, NAMED SEPARATELY (not separable from assembly; conservative)
 10 × 0.20                  =  2.00 s   startup allowance
                              39.52 s → 2.63 core-min, + 0.04 assembly = 2.67
```

**Named separately and not folded in:** `writeCellVolumes` + `writeCellCentres`,
measured at 0.25 s + 0.29 s single-core = **0.009 core-min**. `decomposePar` is
**structurally 0.000 s** — the restart reuses the parent's `processor*`.

> **REGISTERED IN TERMS: THE PER-ITERATION SURCHARGE IS AN UPPER BOUND, NOT A
> VALUE.** The treatment limb measured **2.1 % faster** than the control, below
> run-to-run noise. **This cap rests on a bound and may never be cited as though
> it rested on a measured surcharge.**

**Dollars DERIVED, never measured** (`COMPUTE_BUDGET_CHARTER` §5): 2.68 core-min
= 0.0447 core-h × $0.0513/core-h = **$0.0023 derived**. A calibration row is owed
at completion.

---

## 10. WHAT IS NOT ESTABLISHED

- **VERIFY:** every figure quoted from the pilot is **one snapshot** of a
  `NOT A RESULT` run. **Stability of the concentration, of `p`'s coverage and of
  `Uy`'s failure is untested** — G3′ exists precisely because it is untested.
- **VERIFY:** the comparator does not exist (§8); this document is **not
  freezable** and must not be frozen until it does.
- **VERIFY:** the lag-40 autocorrelation is **interpolated** between the two
  reported points (lag 10, lag 400), not measured.
- **VERIFY:** the commensurability limb (§7.2) has **never run**.
- **VERIFY:** no alternative zone set has been tested for `Uy`, and drawing one
  after seeing where `Uy` lies would be the fitting this campaign has three times
  now avoided.
- **DISCLOSED:** I have seen the density tally, the exclusion zeros **and** the
  0.6496 concentration value. The mitigations are §2's published alternatives,
  §4.2's symmetric rule and §4.1's null-anchored threshold — **not an assurance
  that the choices were blind, because they were not.**

---

## 11. VERDICT

**None, and none is entitled.** This is a draft pre-registration. The H5 arm
remains **`NOT A RESULT`** on a confounded measurand; `F28G_L1_dp1000_U20`
remains **`NOT A RESULT`** at `23eeff7e`. **Compute spent producing this
document: 0.000 core-minutes.**

**SUBMISSIONS PARKED.**
