# CRM-WING-ALONE — NASA Common Research Model **WING-ALONE**, pyHyp-extruded r = 2 structured family

<!-- ============================ DRAFT BANNER — STRIKE THIS ONE BLOCK ============================ -->
> ## 🟠 DRAFT. **NOT FROZEN. NOT AUTHORISED. NO COMPUTE HAS RUN UNDER IT.** §12's freeze block is BLANK.
> Drafted by a cfd `lab-lane`, 2026-09-11, on the cfd-supervisor's brief, **after** the gating
> measurement in §3 returned a positive result. **Check 4 — pre-registration COMMITTED before
> compute — is the supervisor's, is personal, and is not delegated to this lane.**
> **§10 carries OPEN DECISIONS RESERVED TO THE SUPERVISOR.** They are marked, not filled. A gate this
> lane invented would defeat the entire evidentiary purpose of the freeze (rule 2).
> **THIS BANNER IS A SINGLE BLOCK BOUNDED BY THE TWO COMMENT RULES ABOVE AND BELOW IT, SO IT CAN BE
> STRUCK AT FREEZE IN ONE EDIT.**
> **SUBMISSIONS PARKED (rule 7). No agent's message is Sanaa's consent (rule 9).**
<!-- ========================== END DRAFT BANNER — STRIKE TO HERE ================================= -->

---

## 1. 🔴 THIS RUNG INHERITS NOTHING FROM `CRM_M085`

`CRM_M085` is **`BLOCKED`**, conclusively, and it is **post-compute**, so rule 2 has closed its gates.
Its own title names both of its dead premises:

> *"CRM-M085 — NASA Common Research Model **wing-body** at M∞ = 0.85, **DPW5 hex refinement family**"*
> — `verification/campaign/CRM_M085_PREREGISTRATION.md:1`

1. the **DPW5 hex family is refuted** — every quality column worsens monotonically with refinement, so
   no finer member can clear the gates; and
2. **no CRM wing-body surface exists on this box** (established by a sweep over **geometry**, never
   over names — three artifacts named `crm_wingbody` are all wing-only, one of them a tracked repo asset).

**This is a NEW rung with its own registration, never an amendment to that one.** It inherits **none**
of `CRM_M085`'s gates, thresholds, caps, labels, solver rulings or mesh verdicts. Where this document
needs a fact from that tree it re-derives or re-cites it explicitly. **The word WING-ALONE is in the
title for exactly this reason**: the geometry is different, so the registration must be.

---

## 2. WHAT IS BEING REGISTERED

A **three-level, geometrically nested, r = 2 grid family** on the CRM **wing-alone** surface, built by
hyperbolic extrusion (pyHyp) from three structured multiblock CGNS surfaces that **all now exist on
disk**, for a Roache grid-convergence study (rule 5) of an aerodynamic quantity of interest named in §10.

---

## 3. THE GATING MEASUREMENT — A MULTIBLOCK CGNS COARSENER EXISTS AND WORKS

This registration was **gated** on a measurement, and was not written until it returned. The question:
does a tool exist in this box's toolchain that coarsens a multiblock CGNS **while preserving block
connectivity**, so that a **third, coarser surface level** exists at all?

**Answer: YES — `cgns_utils coarsen`, from `cgnsutilities` in the MACH stack**, present in
`dafoam-team:v1` at `/home/dafoamuser/dafoam/packages/miniconda3/bin/cgns_utils`, help text
*"Coarsen a grid uniformly"*. Run on the `A6` surface it produced a 26-block output, **inner rc = 0**
(captured INSIDE the container wrapper — `docker run` exits 0 regardless of the work's rc).

*An arithmetically exact nesting is not the same thing as a coarsener that exists and works.* The
output is **a mesh nobody had ever looked at, produced by a tool nobody here had driven**, so it was
verified against things the tool cannot influence. **Three checks, all binding, all passed.**

### 3.1 Check 1 — block-by-block nesting, ALL 26 BLOCKS, NOT SAMPLED

| quantity | result |
|---|---|
| blocks in → out | **26 → 26**, every fine block name present in the output |
| dims | **exactly (n+1)/2 in both live directions in all 26 blocks** |
| minimum dim | **every coarse dim ≥ 3**, none excepted |
| **decimation deviation** | **0.000000e+00, maximum over all 26 blocks** |

The zero in the last row is the strong result. It says `coarsen` is a **pure node decimation** —
coarse block `[i,j]` is fine block `[2i,2j]` **bit-for-bit** — and **not** an interpolation or a
re-fit. The coarse node set is therefore a **strict subset** of the `A6` node set, so the discrete
geometry cannot have moved. Surface cells **2,784**, the predicted family value.

### 3.2 Check 2 — units-invariant planform against Vassberg, which the coarsener cannot influence

A sweep/taper reader was built and **validated on the source first**, so that it was a real instrument
before it was pointed at the output. It is bias-free by construction: it records each leading- and
trailing-edge node's **own** coordinates, never a bin centre.

**The reader's own resolution limit was characterised before its reading was believed.** Across every
bin count where the coarse point cloud is not starved (16–40 bins, minimum bin population ≥ 33):

| | quarter-chord sweep, outboard | taper referred to true centreline | LE/TE straight-line residual |
|---|---|---|---|
| `A6` source | **35.00244°** | **0.272794** | ≤ 3.7e-05 |
| coarsened output | **35.00243°** | **0.272793** | ≤ 4.6e-05 |
| **difference** | **1e-05 °** | **1e-06** | — |
| **Vassberg Table 1, verified at source** | **35°** (Λ_C/4) | **0.275** (λ) | — |

Sweep agrees with Vassberg to **0.007 %** and taper to **0.80 %**; source and output agree with each
other to **1e-05 degrees**. The trailing-edge residual of order 1e-05 says the outboard TE is a
mathematically straight line in both, which is the planform the source specifies.

🔴 **A RED WITH AN INNOCENT EXPLANATION, CLEARED RATHER THAN WAVED THROUGH.** At 60 bins the reader
returned taper **0.235** on the coarse mesh — a 14 % discrepancy. It was **not** written off. It was
diagnosed: at 60 bins the coarse cloud falls to a **minimum bin population of 4**, and the per-bin
extremum stops landing on the true edge (residual max jumps from 4.6e-05 to **0.223**). The defect is
in **the reader**, not the mesh — which Check 1's exact zero independently proves it cannot be. The
converged reading is the table above. **The starved configuration is recorded here rather than
deleted, because a reader that can produce 0.235 on a known-good mesh is a fact about this
instrument that the next user of it needs.**

### 3.3 Check 3 — block connectivity actually preserved

"Preserving block connectivity" is the claim, so it was tested directly rather than assumed. For each
level, every block-boundary node was counted by how many blocks contain it:

| level | surface cells | nodes in 1 block (free perimeter) | in 2 | **in 3** | **in 4** |
|---|---|---|---|---|---|
| coarsened output | 2,784 | 62 | 471 | **4** | **20** |
| `A6` source | 11,136 | 130 | 985 | **4** | **20** |
| `act9` source | 44,544 | 266 | 2,013 | **4** | **20** |

**The topological invariants are identical across all three levels — 4 triple-points and 20
quad-points.** These are the signature of the 26-block assembly and they do not survive a dropped or
mis-joined block. The 1- and 2-share counts scale with edge resolution, as halving requires. The
surface remains point-matched.

### 3.4 The three surfaces, and confirmation the right artifact was staged

| level | file | surface cells | provenance |
|---|---|---|---|
| L1 | `A6_coarse.cgns` | **2,784** | **produced by this measurement** |
| L2 | `A6-crm-wing/surfMesh.cgns` | **11,136** | pre-existing |
| L3 | `act9.../CRM_surfMesh.cgns` | **44,544** | pre-existing |

The `act9` archive was staged from **one of 37** `act9-crm_wingbody-*` directories, so the staged file
was **confirmed by geometry, not by its path**: 46,762 points and **44,544** surface cells, matching
the established figures exactly. (Its name contains `wingbody`; it is **wing-only**. See §1.)

**Artifacts:** `/home/ubuntu/certonomous-runs/CRM_WINGALONE_COARSEN_PROBE/` — `out/A6_coarse.cgns`
(the product), `census.py`, `nesting.py`, `planform.py`, `nbsweep.py`, `connect.py` (the readers).

---

## 4. THE FAMILY — STATED IN **CELL LAYERS**, NOT NODE COUNTS

A node count and a cell count differ by one per direction, and quoting a family in nodes is how an
r that is not what you think it is gets registered. **This family is stated in cell layers.**

| level | `N` (pyHyp nodes) | **cell layers** | surface cells | **volume cells** |
|---|---|---|---|---|
| **L1** | 53 | **52** | 2,784 | **144,768** |
| **L2** | 105 | **104** | 11,136 | **1,158,144** |
| **L3** | 209 | **208** | 44,544 | **9,265,152** |

| | L2/L1 | L3/L2 |
|---|---|---|
| volume-cell ratio | **8.000000** | **8.000000** |
| **linear r** | **2.000000** | **2.000000** |

**Refinement is in ALL THREE directions** — the surface refines in both its directions and the
extrusion refines normal to the wall. A family that refined only the surface would report an `r` it
does not have.

### 4.1 🟢 r = 2 IS FORCED, AND IT IS BETTER THAN 1.5 RATHER THAN A COMPROMISE

**Forced:** a structured multiblock surface coarsens only by **integer** factors. At r = 1.5 the block
dimensions give **10.667, 21.333, 2.667** — non-integer. One dimension, 24, **does** divide by 1.5,
**which is exactly how a partial check would wave 1.5 through.** The check was run over all 26 blocks
in both directions; r = 1.5 is unavailable. Every `A6` block dim is 2k+1, so exact halving is
available in **all 26 with none excepted** (§3.1).

**Better, not merely available:** the level-to-level signal scales as `h^p (r^p − 1)`, so r = 2
delivers a signal **×2.00 to ×2.40 larger than r = 1.5 for the same fine grid**. This is a direct
structural defence against the failure that killed MRF **twice** — a study whose signal was **a third
of its noise**. Equal ratios additionally mean the **standard Richardson form applies, with no Celik
unequal-r machinery at all.**

---

## 5. REFERENCE QUANTITIES — **CITED TO VASSBERG TABLE 1, NEVER TO THE MESH**

Every number in this table is the **source's**, not a measurement of any grid in §4. A reference
quantity read off a mesh is a circular gate.

🔴 **TABLE 1 IS IN INCHES. THE METRIC VALUES BELOW ARE EXACT UNIT CONVERSIONS OF IT, NOT QUOTATIONS
FROM IT** — and that is itself the first warning of §5.3's hazard: **the source of this geometry is an
imperial document.** All six were re-derived from the printed inch values by this lane and agree to
**≤ 4.5e-05** (the single non-zero residual is `Sref`, from rounding in the source's own 5th decimal).

| quantity | **Table 1, as printed (in)** | **registered value (SI, converted)** | conversion residual |
|---|---|---|---|
| `Sref` | **594,720.0 in²** | **383.6896 m²** | 4.5e-05 |
| `Cref` | **275.80 in** | **7.005320 m** | 0.0 |
| span (**full**) | **2,313.50 in** | semispan **29.381450 m** | 3.6e-15 |
| `Xref` | **1,325.90 in** | **33.677860 m** | 0.0 |
| `Yref` | **468.75 in** | **11.906250 m** | 0.0 |
| `Zref` | **177.95 in** | **4.519930 m** | 0.0 |
| λ (taper) | **0.275** | dimensionless | — |
| Λ_C/4 | **35°** | dimensionless | — |
| AR | **9.0** | dimensionless | — |

⚠️ **Table 1's "Span" row is the FULL span, 2,313.50 in.** The semispan above is half of it. A half-model
run that takes the printed row as a semispan doubles the aircraft.

**L-144 title-page verification — DONE BY THIS LANE, DIRECTLY, NOT INHERITED.** `docs/papers/
benchmark_test_cases/vassberg_2008_nasa_common_research_model.pdf` with its `.txt` sidecar: **AIAA
2008-6919, "Development of a Common Research Model for Applied CFD Validation Studies", Vassberg,
DeHaan, Rivers, Wahls (Boeing / NASA Langley).** Table 1 is titled *"Reference Quantities for the
CRM."* The yehudi break at **37 % semispan** used in §3.2 and §5.3 is the source's own wording.

### 5.1 Cross-check, reproduced here rather than asserted

Full span = 2 × 29.381450 = **58.762900 m**; span² = **3453.0784 m²**.

**span² / `Sref` = 3453.0784 / 383.6896 = 8.999666**, against the **stated AR of 9.0**. ✅ The four
numbers above are mutually consistent to **0.004 %**, so they were transcribed correctly.

### 5.2 🔴 REGISTERED TRAP — `Sref` IS THE AR DENOMINATOR; THE TRAP-WING AREA IS NOT

🔴 **CORRECTED AGAINST THE SOURCE, AND THE TRAP IS WORSE THAN FIRST DRAFTED.** The two areas are not
"two rows apart" — they are **ADJACENT, rows 1 and 2 of Table 1**, printed one directly above the other:

| Table 1 row 1 | `Sref` | **594,720.0 in²** | = 4,130 ft² | **the AR denominator and the force-coefficient reference area** |
|---|---|---|---|---|
| **Table 1 row 2** | **Trap-Wing Area** | **576,000.0 in²** | = 4,000 ft² | **NOT either of those** |

**Worked in the source's own native inches, with no unit conversion in the path at all:**

- span² / `Sref` = 2,313.50² / 594,720 = **8.999667** ✅ against the printed **AR 9.0**
- span² / trap-area = 2,313.50² / 576,000 = **9.292157** ❌

**That is a 3.25 % error in aspect ratio, from picking the wrong row of the right table.** `Sref` =
**383.6896 m²** is the AR denominator and the reference area for all force coefficients. **576,000 in²
is not, and is not to be used for either.**

### 5.3 🔴 REGISTERED HAZARD — THE MESH IS NOT IN METRES, AND NO MESH QUALITY SCREEN CAN CATCH IT

Measured this session from the surface itself: mesh tip at y = 3.7666681523, with the mesh root sitting
**0.4449 mesh-units outboard of the aircraft centreline**, giving a true semispan of **4.2115681523
mesh-units**. Against Vassberg's 29.381450 m:

**1 mesh-unit = 6.976368 m = 274.6602 in**, against `Cref` = **275.8000 in**.

**Anything read off that mesh as metres is wrong by a factor of 6.976×.**

🔴 **AND NO MESH QUALITY GATE WILL EVER FLAG IT.** Non-orthogonality, skewness, aspect ratio and
determinant are **scale-invariant**: the same mesh in either unit system produces **numerically
identical** quality columns. A clean `checkMesh` is therefore **no evidence at all** on this hazard.
It must be caught by the registered scaling below, never by a screen.

**The 0.4449 offset is independently corroborated, not fitted.** It was originally set to place the
yehudi break at the source's 37 % of semispan; it *independently* reproduces the source taper
(0.272794 measured against 0.275 stated, §3.2), and it *independently* reproduces the normalisation
above. Three constraints, one offset.

---

## 6. COST (rule 12) — ESTIMATED BEFORE COMPUTE, EVERY LEVEL COSTED

Basis: **core-minutes = wall s × ranks / 60.** Dollars **DERIVED, NOT MEASURED**, at the owner-stated
c7a.4xlarge **$0.0513/core-h** — this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Anchors, both measured on this box, not recalled:**
- **pyHyp extrusion:** the `59dfc5232` route probe marched **579,072 volume cells for ~7.5 core-min at
  1 rank** → **12.952 core-min/Mcell**, and wrote **282.5 bytes/cell**.
- **Convert + `checkMesh`:** **0.905 core-min/Mcell** (`RUNG0b_MESH_IMPORT_PREREGISTRATION.md`, record
  `33b77af5`, cited at `RUNG2_CRM_GRID_ACQUISITION_PREREGISTRATION.md:201`).

| level | volume cells | extrude (core-min) | convert+`checkMesh` (core-min) | volume-mesh disk |
|---|---|---|---|---|
| **L1** | 144,768 | **1.88** | **0.13** | **0.04 GB** |
| **L2** | 1,158,144 | **15.00** | **1.05** | **0.33 GB** |
| **L3** | 9,265,152 | **120.00** | **8.38** | **2.62 GB** |
| **total** | | **136.88** | **9.56** | **2.99 GB** |

**Mesh ladder total: 146.44 core-min = 2.4407 core-h = $0.1252 derived.** Solver cost is **not** costed
here because the solver is an open decision (§10); **§10 may not be frozen without its cost line**, and
a proposal with no cost is disqualified.

**Registered cap: 10× the mesh-ladder estimate = 1,464 core-min.** Per rule 12 an **overrun stops the
run; it does not get a new budget.** The rule-12 estimate-versus-actual row is owed to
`docs/COST_CALIBRATION.md` at process completion.

### 6.1 Registered precondition — DISK

**Measured 2026-09-11: 38 GB free, 93 % used**, before any staging. **The live figure is now 37 GB and
FALLING AT 3.78 GiB/h** (measured by another lane) — faster than this lane was briefed, so the window
is narrower than the raw free-space figure suggests and the ordering below is load-bearing, not tidy. The ladder needs **~2.99 GB** of
volume meshes alone, before any solution files. **L3 is to be extruded only after a free-space check
confirms ≥ 8 GB**, and the ladder is built **L1 → L2 → L3** so the cheap levels land first. The probe
directory itself is small (the coarse surface is 348,160 bytes).

---

## 7. 🔴 THE pyHyp CLEARANCE IS TOOLCHAIN-ONLY. IT IS NOT A CONFIGURATION CLEARANCE AND NOT A MESH ADMISSION

`59dfc5232` cleared pyHyp **end-to-end at `N` 53**: 53/53 layers marched, `Sl = 1.000`, **min quality
0.08110 and min volume 9.49e-13 positive at every layer**. That is a real result and it is why this
family is worth registering. **It is also strictly bounded:**

- **Nothing was `checkMesh`'d and nothing was converted, so NO Gate-M claim exists** from it.
- **`N` 105 and 209 are untested regimes**, and `cMax` **already saturated at 5.0** in the probe's
  outer layers at `N` 53. Doubling and quadrupling the layer count is where that saturation is most
  likely to bite. **L2 and L3 extrusion carry a genuine risk of not completing** — that is a
  registered risk, not a cost overrun.
- The probe ran at `N` 53 on the **`A6`** surface (579,072 cells) — which is **not a member of §4's
  family**, since the family pairs `N` 53 with the **2,784**-cell L1 surface. **The probe's exact
  configuration has never been run.**

**If an extrusion level fails to march, that level is `BLOCKED` and the triple is `NOT A RESULT`
(rule 5). It is not rescued by dropping to two levels or by a non-integer ratio.**

---

## 8. GRADING RULES THAT BIND THIS RUNG WHATEVER §10 SAYS

1. **Roache triple gating (rule 5).** A triple that is not `CONVERGING` is **`NOT A RESULT`**, whatever
   the value. GCI at Fs = 1.25. **Never quote a GCI when the three values are not monotone.**
2. **Strict completion rule (rule 4)** applies to every solve, all clauses, including the age guard.
3. **Planted-zero control (rule 3).** Any comparator reporting a zero or a null difference must plant a
   known perturbation, read it back from disk, and **refuse** if it cannot see it.
4. **Verdict vocabulary (rule 1)** only.
5. **Scaling assertion (§5.3).** Any script consuming a mesh from §4 must assert its unit system
   against `1 mesh-unit = 6.976368 m` **before** using any reference quantity. A clean `checkMesh` does
   not discharge this.

---

## 9. WHAT THIS LANE DID NOT VERIFY

Stated plainly, because an honest gap is worth more than a confident guess.

- **No volume mesh was built and no `checkMesh` was run.** §3 is a **surface**-level result. **No
  Gate-M claim is made anywhere in this document.**
- **No solver ran.** No aerodynamic quantity has been computed at any level.
- **`act9` being exactly 2× `A6` block-by-block was taken as established, not re-derived.** What this
  lane confirmed independently is that the **staged** `act9` file carries the established counts (§3.4)
  and the established topological invariants (§3.3).
- **The planform reader is this lane's own construction** and does not reproduce a previously quoted
  pair (34.91° / 0.2808) exactly; it returns **35.00244° / 0.272794**. Both land within ~1 % of
  Vassberg. This is a difference of instrument, **stated rather than reconciled**, and the reader's
  starved-configuration failure mode is recorded in §3.2.
- ~~Vassberg Table 1 values are as supplied in the brief and not re-read from the title page.~~
  **CLOSED.** The paper was on disk with a sidecar; this lane verified the title page (L-144) and read
  Table 1 directly. All six values confirmed, **and two errors in this lane's own first draft were
  found and corrected by doing so** (§5: the table is in inches, not metres; §5.2: the two areas are
  adjacent rows, not two apart). **The gap was worth closing rather than declaring.**

---

## 9A. THE TWO-READER RECONCILIATION — **THE SECOND READER DOES NOT EXIST ON DISK**

The supervisor asked, correctly, that two readers disagreeing on one geometry be reconciled as a
**measured** quantity before a freeze, not left as a provenance difference. **It cannot be done the way
it was asked, and the reason is itself the finding.**

**The earlier reader is not on this box.** Swept with a **live positive control** (the same sweep was
first shown able to find a string known to be present, so a zero here is evidence and not a blind
reader — rule 3): `34.91` and `0.2808` appear in **no `.md` or `.py` in the repository except this
document**; `0.4449` appears in no file but this one and a handful of solver residual logs where it is
a coincidental digit string. **No CRM planform reader exists anywhere in the repository or in
`certonomous-runs`.** Those two numbers reached this lane **only through a supervisor's brief**, with
no artifact behind them. **A number whose artifact is gone is not a result** — so there is no second
instrument to run, and running this lane's reader twice would prove nothing.

**What CAN be done, and is better than reader-versus-reader:** Table 1 is now verified at source
(§5), so **both readings can be graded against the source instead of against each other.**

| quantity | **source (Table 1, verified)** | **this lane's reader** | **the earlier figure** |
|---|---|---|---|
| quarter-chord sweep | **35°** | **35.00244° (+0.007 %)** | 34.91° (−0.257 %) |
| taper ratio | **0.275** | **0.272794 (−0.802 %)** | 0.2808 (+2.109 %) |

**This lane's reader is closer on both quantities, by 37× on sweep and 2.6× on taper** — and its
LE/TE straight-line residual of ≤ 4.6e-05 is independent evidence that it is resolving the real
planform. **That is not a claim that the earlier figure was wrong**; without its code, what produced it
cannot be inspected. It is a statement that **only one of the two readings is reproducible today**, and
the reproducible one agrees with the source better.

🔴 **THE REAL FINDING IS NOT WHICH READER WON.** A pair of geometry numbers was quoted, relied on, and
passed between lanes **all evening with no script and no artifact behind it.** Had this freeze cited
34.91°/0.2808, it would have cited something unreproducible. **That is the exact failure the citation
rule exists to prevent, and it was one freeze away.** This lane's readers are on disk, named in §3.4.

---

## 9B. REFERENCE DATA FOR A QoI BAND — **WHAT EXISTS, NOT WHAT WOULD BE NICE**

Swept for machine-readable CRM force or `Cp` data (`.csv`/`.json` across the repository and
`certonomous-runs`, with a live positive control). **The result determines whether §10's O3 can be a
graded band at all.**

| candidate | what it actually is | usable as a wing-alone band? |
|---|---|---|
| `docs/DPW-CRM-SCOPING.md` | median **257 drag counts**, IQR **252–262**, suggested band **250–264** | 🔴 **NO — explicitly "DPW-VI CFD Results — *Wing-Body* (Case 2A)"** |
| Vassberg 2008 Figs 11–13 | `Cp` distributions | 🔴 **NO — figures in a PDF, and an OVERFLOW solution of the *WB* configuration** |
| `verification/credibility/reference_tier_registry.json` | 15 entries | 🔴 **NO — zero Vassberg entries** |
| DPW5 `.json` in `RUNG0b_exports` | mesh-conversion roundtrip records | 🔴 **NO — not aerodynamic data** |

**Conclusion, stated plainly: there is NO machine-readable wing-alone CRM force or `Cp` dataset on this
box.** Everything available is **wing-body**. A fuselage is not a small correction to wing-alone drag,
so **grading a wing-alone solve against a wing-body band would be a category error that a plausible-looking
number would hide.** The scoping document's own figures are additionally web-sourced prose, and it
records that the wind-tunnel values are **held proprietary by NASA**.

Two further mismatches, recorded so they are not discovered after a gate cites one of them:
- **Reynolds number.** Vassberg's design point is **Rn = 40 million** per chord (flight); DPW's common
  condition is **Re = 5 × 10⁶** (wind tunnel). **These are not the same case.**
- **Configuration.** Vassberg's design point is quoted for the **wing/body**, not the wing alone.

🟢 **THE CONSEQUENCE, WHICH IS A LEGITIMATE OUTCOME AND NOT A SHORTFALL.** O3 should be registered as a
**grid-convergence gate alone** — an observed order and a GCI on a self-consistent QoI, which needs **no
external dataset** and is exactly what an r = 2.000000 nested triple is *for*. **The physics is then
REPORTED, NOT GATED.** Inventing a band would repeat `CRM_M085`'s error of grading against nothing; the
band is absent, so it is not registered. **Absence of reference data does not weaken a verification
rung — it only bars a validation claim, which this rung should not make.**

---

## 10. 🟠 OPEN DECISIONS — RESERVED TO THE SUPERVISOR, DELIBERATELY NOT FILLED

This lane measured the geometry and the toolchain. **It did not invent a gate.** Freezing any of the
following is the supervisor's act, and §12 cannot be signed until each carries a value **and a cost**.

| # | open decision | why this lane did not fill it |
|---|---|---|
| **O1** | **Flow condition** (M∞, Re, α or CL target) | not specified in the brief; determines everything below |
| **O2** | **Solver** | `CRM_M085`'s solver ruling is **not inherited** (§1); the §4 meshes are structured CGNS from the MACH stack, which points at a different solver than that rung's OpenFOAM path |
| **O3** | **QoI and its threshold band** | **rule 2: the gate is the document's entire evidentiary content.** A threshold chosen by the lane that produced the mesh proves nothing. **§9B now bounds this decision: no wing-alone reference data exists, so the honest form is a grid-convergence gate with the physics REPORTED, NOT GATED** |
| **O4** | **Observed-order band** for the Roache triple | same |
| **O5** | **Solver core-min estimate and cap** | follows O1–O2; **rule 12 forbids freezing without it** |

---

## 11. THE ANSWER TO THE QUESTION THAT GATED THIS DOCUMENT

**A multiblock CGNS coarsener exists in this box's toolchain and works on this surface.** The third
surface level exists on disk at 2,784 cells, nested exactly, connectivity preserved, planform
unchanged. **A three-level Roache triple at r = 2.000000 is therefore available** — subject to §7's
registered risk that `N` 105 and 209 have never been marched.

---

## 12. FREEZE BLOCK — **BLANK**

| field | value |
|---|---|
| frozen by | |
| freeze commit sha | |
| grading path fixed at | |
| date | |

**No compute may run under this document until this block is filled and committed (rule 2), and §10 is
closed.**
