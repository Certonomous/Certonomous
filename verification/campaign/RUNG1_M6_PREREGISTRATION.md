# RUNG 1 pre-registration — ONERA M6, surface pressures against AGARD AR-138, with the family band

**Team: cfd. Case id `RUNG1-M6`. v1.0, drafted 2026-09-03.**

> ## ⚠ DRAFT — **NOT FROZEN**, AND IT IS **NOT YET FREEZABLE**
>
> Two independent reasons, and the second is the important one:
>
> 1. The rule-2 freeze is the cfd supervisor's **non-delegable personal check**
>    (`SUPERVISION_CHARTER.md` §3). This lane does not take it.
> 2. 🔴 **`MESH_STANDARD.md` §8.1 FORBIDS THE FREEZE TODAY.** *"No cfd mesh-ladder
>    pre-registration is frozen until at least one level has been BUILT, `checkMesh`'d, and SHOWN
>    ADMISSIBLE against the gates that registration will carry."* **No M6 mesh admissible under
>    §3.1 has ever been built by this lab.** §5's `R1-M0` is the measurement that lifts this, and
>    it is the first thing this ladder does.
>
> **NOTHING LAUNCHES AGAINST THIS FILE. NO COMPUTE HAS BEEN RUN UNDER IT.** Registered run roots
> verified ABSENT at drafting: `verification/runs/RUNG1_M6_runs/`,
> `verification/runs/RUNG1_M6_runs/M0_pyhyp_admission/`, `.../L1`, `.../L2`, `.../L3`.

**Authority.** Sanaa's standing order of 2026-09-03 ~00:30Z (`…_sanaa_industrial_benchmark_ladder.md`),
her two-tier mesh ruling and Rung 0 rewording of ~17:30Z (`…_sanaa_mesh_standard_and_freeze_enforcement.md`),
and her compute envelope of ~18:00Z (`…_sanaa_compute_envelope.md`). Her priority, verbatim:

> Priority unchanged: M6 family now, CRM registration in parallel, HLPW behind CRM held. **The first
> thing I want to see is M6 surface pressures against AGARD tunnel data with the family band — a case
> an industry person cannot call easy.**

**Case `RUNG1-M6` is NOT `M6I`, `M6S`, `F13` or `F1`.** M6I is POST-compute with `R0 GATE FAIL`;
its verdicts and its frozen gates are untouched here and are neither reopened nor superseded.

---

## 1. THE REFERENCE IS MACHINE-READABLE, HASH-PINNED, AND INDEPENDENTLY CORROBORATED — NO DIGITIZATION IS NEEDED

**This was the open question and it is closed by measurement.**

| the reference | `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/case_2308.dat` |
|---|---|
| sha256 | **`020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0`** — the same hash M6I's §1 registers as byte-identical to NASA TMR's published copy |
| format | Tecplot `F=POINT`, `VARIABLES = "Section", "Tap", "X/L", "Z/L", "CP"` |
| zone header | `Run= 308, Mach= 0.8395, Alpha= 3.06, Re= 11.72x10**6` |
| structure | **7 zones**, `I = 34 / 34 / 34 / 34 / 45 / 45 / 45` = **271 data rows** |

**THE CORROBORATION, AND IT IS BETWEEN TWO INDEPENDENT ARTIFACTS.** AR-138's own §5.1.1 prose reads
*"271 pressure orifices divided in 7 sections (y/b = 0.20/0.44/0.65/0.80/0.90/0.96 and 0.99)"*.
**The machine file has exactly 7 zones and exactly 271 rows.** The report's prose count and the data
file's row count were read separately and agree.

### 1.1 🔴 AND THE PDF SIDECAR MUST NOT BE USED FOR NUMBERS — MEASURED, NOT SUSPECTED

`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.txt` is an **OCR** sidecar.
Title-page verified independently here per rule 15 / L-144: it renders *"AGARD Advisory Report No. 138
— EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT — REPORT OF THE FLUID DYNAMICS PANEL WORKING
GROUP 04"* — **and renders "ADVISORY GROUP" as `ADVISORY GROW` on its own title page.**

Its Table B1-13, the table for **this very case**, extracts as:

```
M6 N I N G       - sURF4CE PRFSSURE DISTRISUTIONS        T E S T 2308
no      =         .9395
ALPHI       =       3.P6
REC             1  11.72*10k*6
```

> **THE OCR READS MACH `.9395`. THE MACHINE FILE AND THE REGISTRATION READ `0.8395`. AN 8 WAS READ
> AS A 9 — A 12 % ERROR IN THE FREESTREAM MACH NUMBER OF A TRANSONIC CASE.**
> `ALPHA` renders as `ALPHI = 3.P6`; the exponent `**6` as `k*6`. Neighbouring tables render
> `MO = .qT5o`, `MO = .337i!`, `ALPHA = 1.n~`. **And the numeric BODY of every table is absent from
> the text layer entirely** — between B1-13's header and B1-14's header there are only blank lines.

**RULING FOR THIS REGISTRATION, and it is a gate, not advice:**

> **THE AR-138 PDF IS PROVENANCE. IT IS NEVER A SOURCE OF NUMBERS. Every reference value used by
> Gate P comes from `case_2308.dat` at the pinned sha256, and the comparator refuses to run if the
> hash does not match.** No agent hand-reads a value out of the PDF or its sidecar into this
> ladder.

**Consequence for Sanaa's ~16:00Z digitization ruling:** digitization was approved as its own
instrumented task with stated read-off uncertainty folded into the gate band. **It is NOT needed
here** — the data is already machine-readable at a pinned hash, so Gate P's band carries **no
read-off uncertainty term**, and that absence is itself a claim this registration makes and must be
able to defend.

---

## 2. THE GRID IS THE PROBLEM, AND THE TWO-TIER RULING DOES NOT SOLVE IT

**M6 has no workshop committee GRID family.** AR-138 supplies **tunnel data, not grids**. NASA TMR's
M6 distribution `wing-release-072319.zip` contains a **generator** — `hcf_wing_v5p0.f90`,
`hcf_coarsening_v3p9.f90` and the M6 namelists — **not grid files.** Participants run the generator
themselves.

**Therefore an M6 grid is LAB-BUILT, the 70° generation gate binds it unchanged, and Sanaa's
committee-grid tier does not reach it.** Her ruling is explicit that the 70° gate is *"our generation
standard: every mesh the lab builds must meet it, unchanged."*

### 2.1 What the box actually holds, re-verified here rather than relayed

| family | levels | provenance | 70° |
|---|---|---|---|
| **M6I `wing_strct.{1..5}.lb8.ugrid`** (`verification/runs/M6I_runs/mesh/`) | **5 nested levels**, file sizes 55.69 / 7.04 / 0.901 / 0.118 / 0.0161 MB (ratios 7.91 / 7.82 / 7.64 / 7.31; the **cell** ratio is exactly 8) | 🔴 **LAB-BUILT** — dated 2026-09-01 17:28 beside `hcf_wing`, `hcf_coarsening`, `input.nml` and `log.hcf_wing`, whose first lines read *"Wing grid generator … Reading the input file: input.nml"*. **Generator output, not a download.** | **FAILS: 87.66 / 86.46 / 87.75°** |
| DPW5 L1.T hex / prism / hybrid | **ONE level, three CELL TYPES** | committee-distributed | 89.71 / 89.94 / 90.00° |
| HLPW6 h6c1_rans_3a_1 | **ONE grid** | committee-distributed | 89.98° |

> **THE ONLY NESTED REFINEMENT FAMILY THIS LAB OWNS IS LAB-BUILT AND FAILS OUR OWN 70° GENERATION
> GATE. THE ONLY GRIDS ADMISSIBLE AS COMMITTEE GRIDS EXIST AT EXACTLY ONE LEVEL EACH. NEITHER
> COMBINATION YIELDS A CERTIFIED BAND.**
> **This is an ACQUISITION problem, not a permission problem, and no ruling of Sanaa's touches it.**

### 2.2 Why re-running the TMR namelist will probably NOT fix it — stated as inference, with its evidence

M6I's own `R0_RESULTS.md` measured, on the **published TMR topology**:

- max non-orthogonality **87.6620 → 86.4646 → 87.7462°**, **non-monotone and essentially FLAT across
  a 64× cell increase.** *"A maximum that does not move under 64× refinement is a floor."*
- severe fraction **8.22 → 6.81 → 6.55 %**, plateauing near 6.5 %, **not vanishing**.
- **every** severe face within **2.275 root chords** of the root leading edge — the wing and tip
  region, none in the far field.
- the published topology **contains collapsed lines**.

**Inference, and it is labelled as one:** the 87° is a property of the **TMR-published topology**, not
of resolution or of `target_y_plus`. **Running the unrun production namelist
`input.nml_wing_strct_2_stt` would therefore very likely fail 70° too.** **THIS IS NOT MEASURED and
no gate below rests on it.** It is stated to explain why §5 spends its first two core-minutes on a
**different topology** rather than on a finer version of the failing one.

### 2.3 One boundary question referred to Sanaa's desk, not answered here

TMR distributes a **generator plus a namelist** that deterministically produces one grid. If every
participant runs that namelist, they all use the same grid — which is Sanaa's own stated rationale for
the committee tier (*"they exist for comparability with the workshop's own results, where every
participant used the same grids"*). **Is a grid built by running the publisher's own generator on the
publisher's own UNMODIFIED namelist a "workshop committee family"?**

**This registration does NOT assume yes.** It proceeds on the conservative reading — lab-built, 70°
binds. **The question only becomes load-bearing if §5's `R1-M0` shows that no in-house M6 topology
clears 70°**, and it is referred now so that it is on her desk before it is on the critical path.

---

## 3. CASE AND CONDITIONS

ONERA M6 semi-span wing, **AGARD AR-138 test 2308**: **M∞ = 0.8395, α = 3.06°, Re = 11.72 × 10⁶ on
the mean aerodynamic chord c = 0.64607 m**, `S_ref = 0.7532 m²`. Taken from `case_2308.dat`'s zone
header at the pinned hash — **never from the OCR sidecar (§1.1)**.

**Registered so it cannot be confused later, carried forward from M6I §1:** NASA TMR's page specifies
`Re_c_root = 14.6e6` on the **root** chord. `14.6e6 × 0.64607/0.810491 = 11.64e6`. **This ladder uses
Re = 11.72e6 on the MAC. Applying 14.6e6 to the MAC would be wrong by 25 %.**

**Solver:** `rhoSimpleFoam` (steady compressible SIMPLE), **k-ω SST**, fully turbulent,
`nutUSpaldingWallFunction` — continuous across the whole `y⁺` range, so a switching wall function
cannot change the discrete operator part-way along a triple.

Closed non-dimensionally (AR-138 B1-3 §3.7 records tunnel stagnation temperature 292–315 K,
*"cannot be controlled"*): `T∞ = 288.15 K`, `p∞ = 101 325 Pa` (ISA, **chosen not measured**), `U∞`
from `M∞`, and **`μ∞` back-solved to deliver Re = 11.72e6. `μ` reproduces `Re`; it is not a physical
property of air at 288.15 K.**

---

## 4. GATES, THRESHOLDS, CAPS AND LABELS — **DRAFTED, NOT FROZEN**

### Gate A — mesh admission. Everything is gated behind it.

Per level, from three real `checkMesh` logs, read off the reported **maximum**, never off a verdict
string and never off the closing `Failed N mesh checks` line (which ranks grids backwards — measured
in `RUNG0_MESH_IMPORT_PREREGISTRATION.md` §3).

| check | threshold | source |
|---|---|---|
| max non-orthogonality | **≤ 70°** | `MESH_STANDARD.md` §3.1 — **lab-built mesh, the generation gate binds unchanged** |
| max skewness | **≤ 4** | §3.2 |
| cell-count ratio, both pairs | **`r³` exact on integers** | `L-430` |
| node nesting L1 ⊃ L2 ⊃ L3 | **≤ 1e-12 root chords** | |
| per-level graded values read back from the **built mesh** | required | §9.2 — the requested parameter is the thing that lied in F12; only the returned value tells the truth |
| §11.4 fields non-null | required | max aspect ratio, `aspect_ratio_flagged`, min/max cell volume, derived `cell_volume_ratio`, `geometric_directions` |

**If Gate A fails, the case is `BLOCKED` and NO SOLVER RUNS.** Firing an inadmissible ladder is the
F12 failure and the F1/M6I failure; this registration declines to repeat it.

### Gate G — grid convergence. Graded quantities: `C_D` primary, `C_L` companion.

| gate | threshold |
|---|---|
| **G1** iterative convergence | change in `C_D` over the last 500 iterations **≤ 1/10 of the L1–L2 difference**, on every level |
| **G2** residual behaviour | **see §4.1 — DRAFTED, and deliberately NOT 1e-8** |
| **G3** observed order | `p` in **1.5 – 2.5** |
| **G4** GCI | `GCI_fine` on `C_D` at **`Fs = 1.25`**, printed on every number, **never quoted when the three values are not monotone** |

**Rule 5 ordering unmodified.** (1) any level not iteratively converged or not plateaued →
**`NOT A RESULT`**; (2) triple `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` → **`NOT A RESULT`**, with
the value, both triples and both orders printed beside it; (3) `CONVERGING` → `PASS` inside the band
else `GATE FAIL`, GCI printed. **The gate can only turn a `PASS` or `GATE FAIL` INTO `NOT A RESULT`,
never the reverse.** Graded by `scripts/roache_triple.py --dim 3`, equal-ratio, `Fs = 1.25`.
Three levels is both the minimum and the sufficient count (§9.1, Sanaa's ruling); a fourth is a
research option and is never owed.

### 4.1 🔴 G2 — THE RESIDUAL GATE, DRAFTED AS PLATEAU-AND-STATIONARITY, AND **NOT** AS 1e-8

**A hard 1e-8 residual gate on this case would spend the entire budget and return `NOT A RESULT`.
That is not a prediction; it is what the only relevant log on this box measures.**

Read by this lane from `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/run_model_run3.log`,
initial residuals at `Time = 3000` against `Time = 6000` — **three thousand further iterations**:

| field | Time 3000 | Time 6000 | move over 3,000 iterations |
|---|---|---|---|
| `p` | 3.7717e-07 | 3.7442e-07 | **−0.73 %** |
| `he` | 2.6421e-07 | 2.6347e-07 | −0.28 % |
| `U0` | 1.0472e-07 | 1.0457e-07 | −0.14 % |
| `nuTilda` | 8.9803e-07 | 8.9858e-07 | **+0.06 % — the WRONG WAY** |
| `U1` (the closest any field comes to the gate) | 6.8822e-08 | 6.8892e-08 | **+0.10 %, and 6.9× ABOVE 1e-8** |
| **`C_D`** | 0.02299549803674881 | 0.0229955633492643 | **2.8e-06 relative** |

> **THE SOLUTION IS CONVERGED AND THE GATE THAT FAILS IS NOT THE ONE THAT MATTERS.** A 1e-8 floor
> makes the **expected spend equal the cap** and the **expected verdict `NOT A RESULT`**, on a run
> whose answer stopped moving in the sixth decimal place.

**DRAFTED G2 — three clauses, all three required:**

- **G2a — REDUCTION.** Every scaled initial residual has fallen **≥ 4 orders of magnitude** from its
  own value at iteration 1. *(A real convergence claim, and one the measured history clears: the
  fields above sit at 1e-07–9e-07 from O(1) starts.)*
- **G2b — PLATEAU, DECLARED AS A PLATEAU.** Over the last **1,000** iterations, each monitored
  residual's relative drift is **≤ 5 %**, in either direction. *(The measured history drifts under
  1 % over 3,000 — it clears this comfortably, and a run still falling fast would fail it and be
  told to keep going.)*
- **G2c — STATIONARITY OF THE ANSWER.** `C_D` stationary over the last **2,000** iterations to
  **≤ 1/10 of the L1–L2 difference**. *(This is the clause that bears on the result.)*

**AND THE DISCLOSURE THAT MAKES IT HONEST, which is not optional and travels onto the certificate:**

> **The residual reached a FLOOR and did not converge to machine zero. The plateau value of every
> monitored residual is REPORTED beside the result.** A plateau is not convergence, and this gate
> says so on its own face rather than letting a `PASS` imply it.

**THE CAVEAT, KEPT AND NOT DROPPED.** That history is **`DARhoSimpleCFoam` / Spalart-Allmaras under
a DAFoam optimisation driver at `yPlus` mean 33.75, max 103.5** (read from the same log lines) — a
**wall-function** solve. **It is NOT k-ω SST wall-resolved at `y⁺ ≈ 0.25–1.0`, which is what §3
registers.** A wall-resolved solve has a different residual-floor mechanism and the direction of the
difference is **unknown**. It is the only evidence in hand; it is not evidence about the registered
configuration. **Disclosed further:** the 4-order / 5 % / 1,000-iteration numbers were chosen while
looking at a *different* configuration's data. That is legitimate — it is a different case — and it
is stated so that nobody later mistakes it for a threshold fitted to this ladder's own answer.

**THE GATE CHOICE IS THE SUPERVISOR'S TO TAKE AND SANAA'S TO OVERTURN. This lane drafts it and does
not freeze it.** M6I's frozen 1e-8 is POST-compute and does not move.

### Gate P — surface pressures against AGARD AR-138. **SANAA'S DELIVERABLE.**

`C_p` at the **seven published sections `y/b = 0.20 / 0.44 / 0.65 / 0.80 / 0.90 / 0.96 / 0.99`**,
against the **271 tapped values** of `case_2308.dat` at the pinned sha256, with the **grid-family
band** from Gate G carried on every station.

**The band is the sum of three named channels, and none is folded into another:**

| channel | value | status |
|---|---|---|
| numerical (mesh) | **`GCI_fine` from the Gate G family**, `Fs = 1.25` | measured by this ladder |
| reference accuracy | **`ΔCp = ±0.02` at `Mo = 0.84`** — AR-138 B1-4 §6.1 | published |
| read-off | **ZERO — the reference is machine-readable at a pinned hash** (§1) | claimed, and defensible |

**TWO SYSTEMATICS THAT ARE DISCLOSED AND NOT PUT IN THE BAND, because quantifying them would be
inventing a number:**

1. **AR-138 B1-4 §6.2 records "Wall interference corrections: no corrections"**, with a
   semispan-to-tunnel-width ratio of **0.7** (§4.2). The report declines to quantify it and so does
   this registration.
2. **The trailing edge.** AGARD's design TE is **0.14104 % chord thick**; the TMR/TMBWG geometry's is
   **sharp, 0.000 %**. **A `Cp` comparison in the rear 10 % of chord reads that difference, not the
   model.** Gate P is therefore graded on `x/c ≤ 0.90` and the rear 10 % is **plotted and reported,
   never graded.**

**GATE P IS A VALIDATION GATE AND IT SITS BEHIND GATE A AND GATE G.** A `PASS` on a family that is
not `CONVERGING` is `NOT A RESULT` by rule 5, whatever the pressures look like.

---

## 5. 🔴 `R1-M0` — THE DECISIVE MEASUREMENT, AND IT COSTS TWO CORE-MINUTES

> **DOES A pyHyp-GENERATED, WALL-RESOLVED ONERA M6 FAMILY CLEAR 70° AT ALL?**
> **NOBODY KNOWS. IT HAS NEVER BEEN MEASURED. SANAA'S ENTIRE TOP DELIVERABLE SITS BEHIND IT.**

**What we do and do not have from M6S-P.** The pyHyp probe ran and returned `pyhyp_rc 0`, min quality
**0.14054** all-positive over 92 levels, march closed on 12.0, achieved first cell 1.43e-06.
**By that registration's own §1.1 this CAN KILL option 3 and CANNOT CLEAR IT.** It ran **no
`plot3dToFoam`, no `checkMesh`, no solver. It says NOTHING about 70°.**

**`R1-M0`, registered here as the ladder's first act:** generate one **coarse** wall-resolved M6 with
pyHyp, convert it, and run `checkMesh`. **Patch identity is irrelevant to this check** — non-orthogonality
and skewness are cell geometry — so the cheapest converter is used and **no fidelity claim whatever
attaches to it.**

| | |
|---|---|
| **outcome if max non-orth ≤ 70°** | Gate A is satisfiable, §8.1's build-before-freeze is discharged, and this registration becomes **freezable**. |
| **outcome if max non-orth > 70°** | **branches (a1)/(a2) are dead**, snappy (§6 branch (b)) becomes the route, and §2.3's boundary question moves onto the critical path and goes to Sanaa. |
| **label** | **NO verdict of the fixed vocabulary attaches to `R1-M0`.** It is an admissibility measurement that gates a freeze. It grades nothing. |
| **estimate** | **2.0 core-min** |
| **hard cap (~3× the estimate, §7)** | **6.0 core-min — $0.0051 DERIVED** |
| **structural enforcement** | `timeout 360` at 1 rank |

**It cannot be skipped, and §8.1 is the reason: a registration frozen from an assumed mesh is exactly
what cost F1 its entire ladder** — arithmetically exact, node nesting 0.000e+00 m, and **inadmissible
at every level from the moment it was written.**

---

## 6. THE BRANCHES, AND WHAT EACH COSTS

**Rate basis, re-derived by this lane from the log and not re-cited** (the registered 3.362e-06 was
**100.18× too high**; the `ExecutionTime` prints are 100 iterations apart under `printInterval 100`):
**3.3977e-08 core-min/cell/iteration** point estimate, **4.02e-08 conservative**, from three runs
re-derived from scratch across a 9.5× mesh range (42,120 / 79,560 / 399,360 cells → 4.02e-08 /
2.91e-08 / 3.40e-08 whole-run). **The wider 2.69e-08–4.72e-08 band is NOT used: five of its eight
runs were never re-derived.** Estimates below use the **conservative 4.02e-08**.

**Iteration schedule 2,000 / 3,000 / 4,000 (coarse / medium / fine).** Measured headroom, not
assumed: cold-start `C_D` is within 1e-4 relative of final **from iteration 700**.

| branch | levels (cells) | est. core-min | **hard cap (~3×)** | derived $ at cap | where it runs |
|---|---|---|---|---|---|
| **`R1-M0`** admission probe | one coarse level | **2.0** | **6** | **$0.0051** | on box |
| **(a1)** pyHyp nested | 8,970 / 71,760 / 574,080 | **101.7** | **306** | **$0.2617** | on box |
| **(a2)** pyHyp nested | 143,520 / 1,148,160 / 9,185,280 | **1,627.0** | **4,881** | **$4.1733** | on box; **solver memory at 9.2 Mcell is UNMEASURED** (§7.2) |
| **(b)** snappy, full scope | 5.0M / 16.9M / 57.0M | **11,595.2** | **34,786** | **$29.74** *(at the on-box rate; it does not run on-box — see §7.1)* | **RENTED, 64–128 core** |
| **(b-on-box)** snappy, on-box alternative | 0.85M / 2.87M / 9.68M | **1,971.2** | **5,914** | **$5.0561** | on box |

**Branch (b)'s triple is RECONSTRUCTED, not read.** No derivation for it exists on disk; 5.0M /
16.875M / 56.95M at `r = 1.5` with 2,000/3,000/4,000 iterations is the only combination that
reproduces the board's 11,452 core-min at the corrected rate, to 1.3 %. **Stated as inference.**

**⚠ Branch (b)'s `snappyHexMesh` GENERATION cost is UNCOSTED — no measured snappy rate is in hand at
any mesh size.** §8.1 forbids freezing (b) before one level is built and `checkMesh`'d anyway, **and
building that level yields the missing rate for free.** Do that before (b) is frozen, either way.

---

## 7. COST — rule 12 under Sanaa's ~18:00Z envelope law

> **"The estimate is an instrument, not a permission slip."** — Sanaa, 2026-09-03 ~18:00Z.

**Unit: core-minutes.** Dollars **DERIVED, NOT MEASURED** at the on-box `c7a.4xlarge`
**$0.0513/core-h** (owner-stated, corroborated `Xiao2016_EnKF/PREREGISTRATION.md:197`). **The box
cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5).

**Envelope:** $1,000 standing, Rungs 0–3, **no per-case dollar approval inside it, ever again.**
Every spend files a row in **`docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md`**.
**Caps are the team's, set at ~3× its own estimate.** An overrun **STOPS the run; it does not get a
new budget.** A row over 3,600 wall s is a **stall**, reported as waste, **separately named, never
absorbed** into the actual/predicted ratio.

**Escalation to Sanaa, and only these three, each preceded by the escalating agent's own arithmetic
re-derivation from the artifact:** a single run projected over **$150** (= **175,439 core-min**); the
envelope reaching **80 %** (= **$800** = **935,673 core-min**); a **third** attempt of something that
already failed twice. **No branch in §6 approaches any of them.**

### 7.1 The two node-sizing rules — DIFFERENT JOBS, AND THEY MUST NOT BE AVERAGED

| job class | rule | her words |
|---|---|---|
| **serial converter / import** | rent for **MEMORY**, at the **smallest core count that fits it** | *"do not rent 16 vCPU for a serial converter — take the smallest instance that fits memory"* (~17:30Z) |
| **fine-grid solve** | rent for **CORES**, **64–128 core spot** | *"rent the node the grid needs — CRM fine-grid class means 64–128 core spot instances; never crop a grid to a box"* (~18:00Z) |

**`NEVER CROP A GRID TO A BOX.`** The 10-Mcell figure is a **fact about this box** and is **retired
as a limit on ambition.** Branch (b) is therefore registered at its **full 5/16.9/57M scope as a
rented branch**, with (b-on-box) kept beside it as the on-box alternative, **so the choice is made on
evidence rather than forced by the machine.**

**🔴 BLOCKED-ON-PRICE, and under the envelope this is a blocker on MEASUREMENT, not on permission.**
No rented instance price may be quoted from this box (rule 12). **Branch (b)'s core-minute cap of
34,786 is enforceable; its DOLLAR figure is not**, because the on-box rate does not apply to a rented
node. Rented spend enters the envelope ledger **in instance-hours with a console-read price, or it
does not enter as dollars at all** — and the ledger carries an explicit **UNPRICED BACKLOG** column
so the 80 % line cannot be crossed invisibly.

### 7.2 Disclosures on the basis, none of them absorbed into the estimate

1. **The basis is a `DARhoSimpleCFoam` primal under a DAFoam driver, not `rhoSimpleFoam` standalone.**
   It may include driver overhead. **Direction unknown; no correction applied.**
2. **It is Spalart-Allmaras at `y⁺ ≈ 34` with wall functions**, and §3 registers **k-ω SST
   wall-resolved at `y⁺ ≈ 0.25–1.0`** — two turbulence transport equations instead of one, on
   near-wall cells of far higher aspect ratio. **Direction: the true rate is HIGHER. Magnitude
   unmeasured.**
3. **A registered super-linear disclosure that this lane's own measurement does NOT corroborate,
   surfaced rather than smoothed.** M6I §5 disclosure 2 registers cost ∝ `N^1.46`, which over a 9.5×
   mesh range should give a **2.8×** spread in the per-cell rate. The measured spread is **1.5× and
   NOT monotone in `N`** (42k: 4.02e-08, 79.5k: 2.91e-08, 399k: 3.40e-08). **Over 42k–399k the
   disclosure is not corroborated.** It may still bite above 1 Mcell, where the linear solver's
   iteration count grows. **A flat rate is used for the estimate and the super-linear risk is left
   in the cap headroom, which is what the headroom is for.**
4. **Solver memory is UNMEASURED at every level above 1 Mcell.** The 467 + 674 MiB/Mcell model is the
   **converter's** and **must not be transplanted to a solve.** Branch (a2) at 9.2 Mcell carries this
   as its named risk.
5. **The reference log was recorded under unknown contention. This estimate is GROSS.**

### 7.3 Calibration — rule 12's estimate-versus-actual

At every rung completion the actual core-minutes are read **from the logs**, the ratio
actual/predicted stated, the gap attributed (contention / waste / misprediction, **waste named
separately**), and a row filed to **both** `docs/COST_CALIBRATION.md` and the envelope ledger.
**A completion report without that comparison is incomplete.**

---

## 8. COMPLETION — rule 4, strict, all-or-nothing

A level is done only if **all** of it holds: `rc = 0`; an `End` line; **last time == `endTime`**;
fields `U p T rho nut k omega` present at `endTime`; `ExecutionTime` count == `endTime`; and **every
field at `endTime` NEWER than the case's own `0/U`** — the age guard. **The launcher refuses a case
where `0` or a time directory already exists.** The comparator **refuses (exit 2) rather than
degrade** on any failed clause. **An absent `checkMesh` log reads `ABSENT`. It never reads clean.**

**Ranks are taken from the SOLVER LOG's own banner, never from `system/decomposeParDict`** — measured
trap: `A3-onera-m6-transonic/system/decomposeParDict` now reads `numberOfSubdomains 2` and
**post-dates the run**, whose banner says `nProcs : 4`. **And the banner's FIRST occurrence is not
the primal's**: `nProcs : 1` sits at line 30, the primal banner at line 63. **Taking the first match
halves the rate.**

---

## 9. PLANTED CONTROLS — rule 3, on every zero this ladder can report

| reader | plant | must see |
|---|---|---|
| `checkMesh` quality reader | a log of the **`=`** label form **and** one of the **`:`** form | a **non-null** max aspect ratio from **each** — a reader matching only `=` sees 761 of the lab's 916 logs and **silently misses exactly the 155 pathological ones** |
| `checkMesh` quality reader | `Min volume` ≠ `Max volume` | a **non-trivial** derived cell-volume ratio, never 1 |
| `C_p` comparator | perturb one tap's `CP` in a **scratch copy** of `case_2308.dat` | the station deviation moves by the planted amount |
| `C_p` comparator | corrupt the reference file's sha256 | **REFUSAL**, not a silent fallback |
| force reader | perturb `C_D` in a scratch `postProcessing` file | the deviation moves |
| residual reader | feed a log whose residuals are still falling | **G2b FAILS** — the plateau clause must be able to say no |
| similarity reader | perturb one built mesh's node position | nesting check reports **non-zero**, not zero |

**A zero from a reader not shown able to see a non-zero is not evidence. A `PASS` reported by a
reader whose plant did not fire is `NOT A RESULT`, not a pass.**

---

## 10. WHAT THIS REGISTRATION DOES NOT CLAIM

1. **It does not claim an admissible M6 mesh exists.** §5 measures that; it has never been measured.
2. **It does not claim the TMR production namelist would fail 70°** — §2.2 is inference with its
   evidence attached, and no gate rests on it.
3. **It does not claim M6 has a committee grid family.** It claims the opposite, and refers the
   boundary question (§2.3) rather than deciding it.
4. **It does not claim `Cp` agreement in the rear 10 % of chord means anything** — the TE differs by
   construction, and that region is plotted, never graded.
5. **It does not quantify the uncorrected wall interference.** AR-138 declines to; so does this.
6. **It claims no rented-instance dollar figure.** `BLOCKED-ON-PRICE`.
7. **Nothing is sent, filed, submitted or registered outside this box (rule 7).**

---

## 11. FROZEN PATHS

| what | path |
|---|---|
| this registration | `verification/campaign/RUNG1_M6_PREREGISTRATION.md` |
| run root (**ABSENT**) | `verification/runs/RUNG1_M6_runs/` |
| admission probe root (**ABSENT**) | `verification/runs/RUNG1_M6_runs/M0_pyhyp_admission/` |
| level roots (**ABSENT**) | `verification/runs/RUNG1_M6_runs/{L1,L2,L3}/` |
| reference data, **hash-pinned** | `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/case_2308.dat` sha256 `020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0` |
| comparator (**does not exist; to be written**) | `verification/runs/RUNG1_M6_runs/analyse_rung1_m6.py` |
| envelope ledger | `docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md` |

---

## 12. WHAT IS OWED TO SANAA'S DESK

1. 🔴 **THE ACQUISITION PROBLEM (§2.1).** The only nested family we own is lab-built and fails our own
   70° gate; the only committee-admissible grids exist at one level each. **Neither combination yields
   a certified band, and no ruling of hers touches it.** It needs grids acquired, not a permission.
2. **The §2.3 boundary question** — is the publisher's generator-plus-unmodified-namelist a "workshop
   committee family"? Only load-bearing if §5 shows no in-house M6 topology clears 70°.
3. **The G2 residual gate (§4.1)** — drafted as plateau-and-stationarity, **not** 1e-8, on measured
   evidence from a different configuration. Hers to overturn.
4. **Gate P's zero read-off uncertainty (§1)** — claimed because the reference is machine-readable at
   a pinned hash, which is a claim rather than a default.
