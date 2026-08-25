# F13 pre-registration — ONERA M6 wing, transonic, run 308

**FROZEN by the commit that lands this file.** Written 2026-08-25 before any solver was
launched under this registration and before the mesh instrument it registers exists on disk.
Team: cfd. Form: the **10-line pre-registration form** (Sanaa, 2026-08-25) — seven required
fields, then cost and the ABSENT registry that CLAUDE.md rules 12 and 2 require of every
registration regardless of form. v1.0.

---

## 1. CASE

ONERA M6 semi-span wing, transonic, **M∞ = 0.8395, α = 3.06°, Re = 11.72 × 10⁶** on root
chord — read from the held artifact's **own zone headers**, identical on all seven zones.
Solver `rhoSimpleFoam` (steady compressible SIMPLE), **k-ω SST**, fully turbulent, continuous
wall functions (`nutUSpaldingWallFunction`) valid across the whole y⁺ range — chosen because a
nested ladder cannot hold y⁺ fixed and a switching wall function would change the discrete
operator mid-triple.

Closed **non-dimensionally**, because the tunnel's stagnation conditions are in the unheld
primary: T∞ = 288.15 K, p∞ = 101 325 Pa (ISA, **chosen not measured**), U∞ = 285.67 m/s,
ρ∞ = 1.2251, **ν∞ = 1.9642e-5 m²/s back-solved to deliver the held Re**, μ∞ = 2.4064e-5 Pa·s.
**μ is set to reproduce Re; it is not a physical air property at 288.15 K (≈1.79e-5).**

Geometry: `sdk/geometry/onera_m6_wing.stl` — 12,480 triangles, bounds x [0, 1.14396],
y [−0.03943, +0.03943], z [0, 1.21640]; header reads `Certonomous patch-extracted STL`.
`c_root = 0.8059 m` from `cases/dafoam/ladder-a/A3_onera_m6.json`. **Both are DERIVATIVE of
the DAFoam tutorial. No primary definition of the M6 planform or the ONERA D section is held
on this box.** V and G grade the solver and the mesh against themselves on the registered
geometry and are unaffected; **P would be affected, and P is not claimed.**

## 2. REFERENCE — AND THE DISCLOSURE THAT DOES NOT COMPRESS

`cases/dafoam/ladder-a/logs_A3/case_2308.dat` — blob **`1fac3174946a70bf34dbc7c970f860f11d284642`**,
**22,695 B**, sha256 `020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0`.
`TITLE = "M6 WING - SURFACE PRESSURE DISTRIBUTIONS"`; `VARIABLES = "Section","Tap","X/L","Z/L","CP"`;
**7 zones, Sections 1–4 at 34 taps and 5–7 at 45 taps = 271 taps** (184 upper, 87 lower).

**THE CEILING, ON THE FACE OF THIS DOCUMENT:**

- **AGARD AR-138 (1979) is NOT HELD ON THIS BOX.** Zero tracked files match `AR-138`; a
  previous lane swept every PDF on the machine with a planted control.
- **The artifact does not self-attribute.** `/usr/bin/grep -c` over its 22,695 bytes:
  `AGARD` **0**, `Schmitt` **0**, `Charpin` **0**, `AR-138` **0**, `2308` **0**, `ONERA` **0**.
  **Each zero is PLANTED, not assumed** (rule 3): the same reader on a copy carrying one
  inserted line naming all six returned **1 for every one**. Positive controls on the
  unmodified file: `M6 WING` 1, `Run=` 7, `Mach` 7. **`2308` occurs only in the FILENAME.**
- **Its attribution to AGARD AR-138 Case 2308 rests on this lab's own prose and on a
  filename. The primary it transcribes is NOT HELD and HAS NOT BEEN OPENED BY THIS LAB.**
- **Rule 15 title-page verification is IMPOSSIBLE on this box** — there is no retrieved
  document to verify.
- **AND IT IS NOT COMPUTABLE EITHER.** The artifact carries **no spanwise coordinate**.
  `Z/L` spans [−0.0489, +0.0489] at every section — that is the thickness coordinate on the
  *local* chord, not a station. Searched with a planted control (a copy with a `"Y/SPAN"`
  header returns `Y/` 1, `SPAN` 1): `Y/`, `y/`, `SPAN`, `span`, `Eta`, `eta`, `ETA`, `2Y`,
  `Y=`, `Station`, `y/b` — **0, all eleven.** A solution cannot be interpolated onto a tap
  whose spanwise position is unknown. Station values circulate in the open literature;
  **they are not held here and this registration will not use them.**
- **THEREFORE GATE P IS `PENDING` AND IS NOT CLAIMED.** `PENDING` in its charter sense — a
  queue state for *not yet run* (VERIFICATION §9, REPORTING §2 rule 5). **P has not failed.
  It has not been attempted.**
- **AS FROZEN, THIS CASE CANNOT REACH `HOLDS`**, because `HOLDS` requires all three columns
  and this registration gates two. **A V+G `PASS` here is NOT an M6 validation.**
- **UNBLOCK, registered now:** if AGARD AR-138 reaches this box and **title-page verifies**
  (never by filename, file type or hash), the seven stations are read from it and **P becomes
  claimable WITHOUT changing any gate, band, threshold, cap or label.** That is the entire
  reason to register P today. It lands as a dated addendum; no line above it is edited.
  **Nothing here is a request to obtain the document — SUBMISSIONS ARE PARKED (rule 7).**

**REFERENCE-ACCURACY DISCLOSURE (mandatory).** Bands were asked to be "justified from the
reference's stated accuracy." **That justification is UNAVAILABLE — the document that would
state an accuracy is not held, and no experimental uncertainty for run 308 exists anywhere
this lab can read. No such number is invented here.** Every band below instead names one of:
**(1)** discretisation-order expectation, **(2)** the instrument's own resolution, **(3)** an
exact algebraic property, **(4)** the tap spacing of the held data — **(4) is used only in
Gate P, which is not claimed.**

## 3. QUANTITIES

**V — code verification. Self-referential; owes nothing to any document.**
- **V0** planted-zero control: the comparator plants `1.234e-03` **by index** into an on-disk
  copy of every field it reads, re-reads through the same path, and **refuses (exit 2)** if it
  cannot see it.
- **V1** freestream preservation: all patches incl. the wing set to the freestream state, so
  uniform flow is the **exact** solution; measure `max|U − U∞|/|U∞|` over interior cells after
  50 iterations. Verifies the metric identities and boundary-flux assembly on this family —
  **not** the turbulence model or the shock capturing.
- **V2** global mass conservation at the converged primal: `|ṁ_in − ṁ_out|/ṁ_in`.
- **V3** symmetry-plane exactness (NULL test): `max|U·n|/|U∞|` on the root plane.
  **PLANTED CONTROL, mandatory:** the same check on a copy whose root patch is `zeroGradient`
  **must FAIL**; if it does not, V3's pass is `NOT A RESULT`.

**G — grid convergence. Self-referential.**
- **G1** C_D, **G2** C_L (wing patch force ÷ ½ρ∞U∞²S_ref; `S_ref` computed from the registered
  surface and printed to 6 s.f. with every result).
- **G3** x_shock/c at z/b = 0.50 **of the registered geometry** — a location on the mesh, not
  on any tap table — by **sonic crossing** (Cp crossing Cp* from below on the recompression,
  linearly interpolated). Steepest-gradient is also recorded, always with its lattice
  resolution beside it, and **never quoted alone** (the F2 lesson).

**P — `PENDING`, NOT CLAIMED.** Cp RMS vs the 271 taps, upper and lower separately, plus
per-section shock position.

## 4. BANDS

| gate | band | derivation basis |
|---|---|---|
| **V1** | `≤ 1.0e-6` | **(3)** + the registered `p` linear tolerance 1e-8: 50 iterations of worst-case drop error give 5e-7; 1e-6 is one binary order above. Failable only by a real metric/flux defect. |
| **V2** | `≤ 1.0e-6` | **(3)** — the registered harmonized `residualControl`. A global imbalance cannot be claimed tighter than the local criterion the solver stopped on, and must not be looser: a boundary-flux defect breaks the global integral while every local residual is satisfied. |
| **V3** | `≤ 1.0e-12` | **(3)** — `symmetryPlane` removes `U·n` **algebraically**; the exact answer is zero and round-off is ~1e-16. 1e-12 is four orders above it. |
| **G1 C_D** | `GCI_fine ≤ 3.0 %` at Fs = 1.25 | **(1)** — second order in smooth regions, first order at a captured shock ⇒ p ∈ [1,2]; at r = 2 that is `1.25·│e₂₁│` (p=1) to `0.417·│e₂₁│` (p=2), so 3 % ⇔ a fine-to-medium change of **2.4 %–7.2 %**. |
| **G2 C_L** | `GCI_fine ≤ 1.5 %` | **(1)** — C_L is the whole-surface pressure integral, not the shock's exact position; the better-behaved member gets **half** G1's width. |
| **G3 x_shock** | `GCI_fine ≤ 0.0125 chord, ABSOLUTE` | **(2)** — the fine level's uniform chordwise cell is **0.00625 c** (admission-checked ≤ 0.00650 c from the built mesh). **A GCI narrower than one cell of the finest mesh is not claimable**; 0.0125 c is **exactly two fine cells**. Derived from the mesh, not from the data. |
| **P1** upper Cp RMS | `≤ 0.110` | **(4), NOT CLAIMED.** Measured tap spacing 0.0500 c (Sec 1–4) / 0.0399 c (Sec 5–7); measured max single-interval shock rise **0.6402** (Sec 5), median 0.4233. At the P3 tolerance ≈0.63 taps sit in the mismatch window ⇒ `0.64·√(0.63/31)` ≈ **0.091**, +≈20 % headroom. |
| **P2** lower Cp RMS | `≤ 0.045` | **(4), NOT CLAIMED.** No shock on the lower surface, so only the smooth term survives: ≈0.4 × P1. |
| **P3** shock position | `≤ 0.025 chord` | **(4), NOT CLAIMED.** **Half the coarsest section's tap interval** — the data cannot resolve its own shock better than that. |

Transcription precision of the held Cp is **5 significant figures** (≈1e-4 near Cp = 1).
**That is a transcription resolution, not a measurement accuracy, and is not used as a proxy
for one.** — This lab's F1 record reports upper Cp RMS 0.049–0.114 on a 399k-cell M6 solve;
**it did NOT set the bands above** (which run from tap spacing and the measured shock jump
only) and is disclosed here rather than hidden. Sanaa has ruled the old favourable comparison
is history and cannot score P; this registration does not revive it.

## 5. LADDER — three levels, GEOMETRICALLY SIMILAR, admission-checked at every level

**The similarity rule.** Every edge distribution is a **continuous stretching mapping with a
FIXED shape parameter β**, sampled at `n_m = n_base·m`:
`y(ξ) = L(e^{βξ} − 1)/(e^{β} − 1)`, `ξ = i/n_m`. Because ξ = i/n and ξ = 2i/2n are the same ξ,
**the coarse nodes are a SUBSET of the medium nodes, which are a subset of the fine nodes.**

**MEASURED at the freeze:** `max│y₃₂[i] − y₆₄[2i]│ = 0.000e+00`, `max│y₆₄[i] − y₁₂₈[2i]│ =
0.000e+00`, `max│y₃₂[i] − y₁₂₈[4i]│ = 0.000e+00` c_root (wall-normal); `max│x₁₁[i] − x₄₄[4i]│
= 0.000e+00` (chordwise). **CONTRAST, same instrument:** the other obvious recipe — halving
the first cell **exactly** while doubling the count — is **NOT nested**: `max│y₃₂[i] −
y₆₄[2i]│ = 6.6993e-02 c_root`, **335× the first cell.** It looks more similar and is less so;
rejected for that measured reason.

**Registered β, FIXED across levels:** wall-normal `β = 10.575549` over 20 c_root,
`n_base = 32`; chordwise S1 (x/c 0→0.10) `β = ln(12.5) = 2.525729`, `n_base = 11`; chordwise
S2 (x/c 0.10→1.00) **UNIFORM**, `n_base = 36`; spanwise 20 + tip cap 6, uniform; wake 16 each
side, uniform. **β_S1 = ln(12.5) is not tuned** — it is the exact derivative-matching value
that makes S1's join cell equal S2's uniform cell (`0.10βe^β/((e^β−1)n_S1) = 0.90/n_S2` with
an LE cell of 0.002 c ⇒ `e^β = 0.025/0.002`, `n_S1 ≈ 11`). **Measured join jump 0.892 → 0.943
→ 0.970**, converging to 1.000. **S2 is deliberately UNIFORM** because the shock sits at
x/c ≈ 0.18–0.60 and a shock-position gate must not be quantised by clustering.

| level | `n_chord × n_normal × n_span` | cells | ranks | δ₀ [µm] | y⁺ (est.) | S2 cell | `simpleGrading` E (wall-normal) |
|---|---|---|---|---|---|---|---|
| **L1** m=1 | 126 × 32 × 26 | **104,832** | 4 | 161.18 | ≈42.2 | 0.02500 c | **28 143.3** |
| **L2** m=2 | 252 × 64 × 52 | **838,656** | 8 | 73.95 | ≈19.4 | 0.01250 c | **33 200.0** |
| **L3** m=4 | 504 × 128 × 104 | **6,709,248** | 16 | 35.45 | ≈9.3 | 0.00625 c | **36 059.6** |

`n_chord = 126m` = 2×(11m + 36m) surface + 2×16m wake; `n_span = 26m` = 20m root→tip + 6m
tip cap (the M6 tip is a flat cut, so the cap is geometry, not a simplification).

**MEASURED: `h = (N_ref/N)^(1/3)` gives r = 2.000000000 for BOTH consecutive pairs.**
Equal-ratio, `dim = 3`, **r = 2 exactly**.

**Registered in advance so it is not later read as a defect:** in a truly nested family the
first cell scales as `2·(1 + O(β/n))`, **not exactly 2** — measured **δ₀ ratios 2.17968 and
2.08613**. **The quoted `simpleGrading` E CHANGES with level, and that change is what makes
the family nested. Holding E fixed would NOT** — measured δ₀ ratios then are **1.87509** and
**1.93654**, on a non-nested distribution. Three different E values are the recipe working,
not an inconsistency. **y⁺ falls ≈2× per level by construction**, which is why continuous
wall functions are registered in §1.

**ADMISSION CHECKS — every level, from THREE REAL `checkMesh` LOGS:** max non-orthogonality
**≤ 70°**; max skewness **≤ 4**; `checkMesh` prints `Mesh OK`; node nesting L1 ⊂ L2 ⊂ L3 read
from the built `polyMesh` to 1e-12 c_root; `r = 2.000 ± 0.002`; **L1 max y⁺ ≤ 300** (L2/L3
reported, not gated); **L3 S2 chordwise cell ≤ 0.00650 c** measured from the built mesh.
**AN ABSENT `checkMesh` LOG READS `ABSENT`. IT NEVER READS CLEAN** — the comparator `test -e`s
each of the three paths, emits `ABSENT` (not silence, not a pass) for any missing one, and
**refuses to grade G on that level.**

**Grading:** `scripts/roache_triple.py --dim 3`, equal-ratio, **Fs = 1.25**. Rule-5 ordering
unmodified: (1) any level not iteratively converged or not plateaued → `NOT A RESULT`;
(2) triple `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` → `NOT A RESULT`, value and both
triples and orders printed beside it; (3) `CONVERGING` → `PASS` inside the band else
`GATE FAIL`, GCI printed. **The gate can only turn a PASS or GATE FAIL INTO `NOT A RESULT`,
never the reverse. NEVER QUOTE A GCI WHEN THE THREE VALUES ARE NOT MONOTONE.** Observed order
p and the Richardson extrapolate are **reported, never gated** — the verdict grades the
**fine value**, never the extrapolate.

## 6. DECOMPOSITION SEED — pinned, and CHECKED not asserted

**Method `hierarchical`. `scotch` is not used anywhere in this registration.** `hierarchical`
exposes no RNG seed; **the pinned parameters that stand in for one are the factorisation `n`
and the coordinate `order`**, both written explicitly in `system/decomposeParDict`:

| level | ranks | **partition A** | **partition B** |
|---|---|---|---|
| L1 | 4 | `n (4 1 1)`, `order xyz` | `n (1 4 1)`, `order xyz` |
| L2 | 8 | `n (4 2 1)`, `order xyz` | `n (1 4 2)`, `order xyz` |
| L3 | 16 | `n (4 2 2)`, `order xyz` | `n (2 2 4)`, `order xyz` |

**Both members of each pair are deterministic and genuinely different. The doctrine bans
non-determinism, not difference.**

**ADMISSION GATE D — determinism MEASURED, never assumed.** The doctrine's §5 states no
method has been *shown* deterministic on this box and forbids assuming one is. Before any
level feeds a gate: `decomposePar` **10×** from a byte-identical case, `sha256` of every
`processor*/constant/polyMesh/cellProcAddressing`, and **exactly ONE distinct partition set
must result. More than one ⇒ the level is `BLOCKED` and feeds no gate.** Run for both members
at all three levels — six checks, 60 invocations, costed in §8.

## 7. CRITERIA — the C3 two-leg rule, NOT the twitchiest residual channel

**Both legs required.**

- **Leg 1, stationarity of the graded quantity**, over the last 500 iterations:
  drift `|q(N) − q(N−500)|/|q(N)| ≤ 1.0e-4` **and** peak-to-peak `≤ 2.0e-4·|q(N)|`.
  **Basis (1):** the tightest band this feeds is G2's 1.5 %; a criterion **150× below** the
  tightest band it feeds cannot be what decides the verdict.
- **Leg 2, reproducibility across the partition pair**: `|q(pA) − q(pB)|/|q| ≤ 1.0e-3` for
  C_D and C_L; `≤ 2.0e-3` chord absolute for x_shock.
  **Basis (1), and DISCLOSED AS AN EXTRAPOLATION.** The only partition-pair reproducibility
  this lab has measured is F6a's — **2.169e-5 in x/c** (0.0017 % of value; the separation
  channel **2.857e-7**), `F6a_GREENBLATT_PREREGISTRATION.md` Addendum 5 §A5.4. **1.0e-3 is
  ≈46× wider**, set wide deliberately because F6a was **2D at ~50k cells** and L3 here is
  **3D at 6.7M** — 134× the cells and a different reduction tree. **This is an extrapolation
  from one measurement on one other case, and this registration does not call it a measured
  band for this case.**

**RESIDUAL CRITERIA — HARMONIZED (doctrine C2).**
`residualControl { p 1e-6; U 1e-6; e 1e-6; k 1e-6; omega 1e-6; }` —
**`bind_ratio` = max/min over primary channels = 1.000 exactly.** No channel is tighter than
its siblings, so **no channel can become the sole binding criterion** and the F6a pathology
cannot arise by construction. **The one-line justification C2 requires:** *every primary
channel is held to the same criterion precisely so the stopping decision is never delegated
to one channel; 1e-6 is a floor and is not the gate.* No auxiliary channel appears — there is
no mesh motion, so no `pcorr`.

**Linear-solver tolerances — reported under a SEPARATE heading, NEVER ratioed against the
above** (doctrine axis A1: a different key measuring a different quantity): `p`/`pFinal`
`GAMG` **1e-8**; `U`,`e`,`k`,`omega` (+`Final`) `smoothSolver` **1e-9**. V1's band derives
from the `p` entry.

**THE INVERSION, STATED IN ADVANCE:**
> **A run meeting BOTH legs but NOT the residual floor IS GRADED**, with its full residual
> state printed beside the value.
> **A run meeting the residual floor but FAILING EITHER LEG is `NOT A RESULT`.**

F6a closed `NOT A RESULT` because one channel 5,000× tighter than its siblings became the sole
binding criterion and measured the partition, not the convergence. **This registration cannot
repeat that.**

**Schemes:** `div(phi,U)`/`div(phi,e)` `Gauss linearUpwind grad(·)`; `div(phi,k)`,
`div(phi,omega)` `Gauss limitedLinear 1`; `grad` `Gauss linear`; `laplacian` `Gauss linear
corrected`. `endTime` **4000** (a cap, not the criterion). Far field 20 c_root,
`freestreamPressure`/`freestreamVelocity`; root plane `symmetryPlane` (V3 gates it).

**COMPLETION — rule 4, unmodified.** `rc = 0`; an `End` line; last time == the final written
time; fields `U p T k omega nut alphat rho` present; `ExecutionTime` count == iterations
reached; **every field at the final time NEWER than the case's own `0/U`** (the age guard). A
guard refuses a case where `0/` or a numeric time dir already exists. **Any clause missed ⇒
`NOT A RESULT`.** The comparator **refuses (exit 2) rather than degrades.**

**Vocabulary:** `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` /
`PENDING`. No synonyms, no hedging.

## 8. COST (rule 12) — costed before it can run

**Rate basis: `4.154e-6 core-s per cell-iteration`**, from this lab's own measured M6 run —
`cases/dafoam/ladder-a/A3_onera_m6.json` `stage_1_primal/runs[2]`: **1244.2 wall s × 4 ranks
= 4976.8 core-s** over **3000 iterations** on **399,360 cells**.

**Disclosed limits of that basis:** it was measured on **`DARhoSimpleCFoam` under Docker at 4
ranks**, and this registration runs **`rhoSimpleFoam` at 4/8/16 ranks** — **the transfer is an
ASSUMPTION, not a measurement**; **8- and 16-rank parallel efficiency is NOT measured on this
box for this case** (cells/rank 26.2k / 104.8k / 419.3k, all above the ~10k collapse floor,
but assumed constant); and convergence by 3000 iterations is assumed while `endTime` is 4000.
**These three are why the cap sits at 2.05× the estimate, and they are the hypotheses §8.1
tests.**

**Meshing priced at this team's MEASURED FIT `t ≈ 0.930 s × (N/23,040)^0.72` + ≈1.5 s
startup — labelled a measured fit, NOT linear in cells:** L1 **4.1 s**, L2 **13.5 s**, L3
**57.3 s**, total **74.9 s = 1.25 core-min**. **A linear model would say 308.9 s — 4.12×
higher.** It is not used.

| rung | what | ranks | est. core-min | **HARD CAP** |
|---|---|---|---|---|
| **R0** | build L1/L2/L3, `checkMesh` ×3, nesting + r + y⁺ admission, **gate D** (60 `decomposePar`) | 1–16 | 19.3 | **90** |
| **R1** | Gate V — 50 iterations at each level; V2/V3 read at the primal; V3 negative control | 4/8/16 | 26.5 | **120** |
| **R2** | L1 primal, partitions A **and** B | 4 | 43.5 | **150** |
| **R3** | L2 primal, partitions A **and** B | 8 | 348.4 | **800** |
| **R4** | L3 primal, partitions A **and** B | 16 | 2 787.0 | **4 840** |
| | **TOTAL** | | **3 224.7** | **6 000** |

**Dollars DERIVED and REPORTED-BY-OWNER, NEVER MEASURED**, at **$0.0513/core-h** (c7a.4xlarge,
owner-stated 2026-08-21/22; corroborated `Xiao2016_EnKF/PREREGISTRATION.md:197`). **The box
cannot read its own billing** (COMPUTE_BUDGET §5). Estimate **3 224.7 core-min = 53.75 core-h
→ $2.757 derived**; cap **6 000 core-min = 100.0 core-h → $5.130 derived**. Cap/estimate
**2.05×**. Both under the $25 pre-authorisation — **and a blanket is not a per-item reading
(rule 9); this row is the per-item costing.**

**AN OVERRUN STOPS THE RUN. IT DOES NOT GET A NEW BUDGET.** A rung reaching its cap is halted
and reported as halted; the campaign does not continue on the next rung's allowance. **A row
over 3600 wall s is a stall**, reported as waste, separately named, never absorbed into the
ratio (COMPUTE_BUDGET §6).

### 8.1 Calibration obligation (rule 12, Sanaa 2026-08-23)

At every process completion — each rung graded, and the case closed — the estimate above is
compared against the actual. Actuals in **core-minutes from logs**; dollars **derived at the
recorded rate and labelled derived, not measured**. The comparison states actual/predicted
and attributes the gap — contention, waste, misprediction — with **waste separately named,
never folded into the ratio**. It lands as a row in **`docs/COST_CALIBRATION.md`** under that
file's append rules and the rule-10 private-index protocol. **A completion report without
this comparison is incomplete.**

## 9. EVERY RUN DIRECTORY REGISTERED BY NAME AND PROVED ABSENT

**`test -e` run inside the same shell invocation that wrote the freeze commit.** Paths
relative to `/home/ubuntu/Certonomous/`.

`cases/F13_onera_m6/` · `cases/F13_onera_m6/make_blockmesh_m6.py` ·
`verification/runs/F13_ONERA_M6_runs/` · `…/analyse_f13.py` · `…/mesh/m1/` · `…/mesh/m2/` ·
`…/mesh/m4/` · `…/mesh/m1/log.checkMesh` · `…/mesh/m2/log.checkMesh` · `…/mesh/m4/log.checkMesh` ·
`…/V_freestream_m1/` · `…/V_freestream_m2/` · `…/V_freestream_m4/` ·
`…/V3_negative_control_zeroGradient/` · `…/L1_m1_pA/` · `…/L1_m1_pB/` · `…/L2_m2_pA/` ·
`…/L2_m2_pB/` · `…/L3_m4_pA/` · `…/L3_m4_pB/` · `…/decompose_determinism/` ·
`verification/campaign/F13_RESULTS.md`

**— 22 paths, every one ABSENT at the freeze; the machine-captured evidence is in the freeze
commit message.** The comparator's grading path is fixed at this commit: before grading,
`analyse_f13.py` is hashed against the blob committed here and **a mismatch is a refusal, not
a warning** (rule 2).

## 10. WHAT THIS DOCUMENT CANNOT SEE

1. **Whether the held artifact is a faithful transcription of AGARD AR-138 Case 2308.** It
   cannot be checked from this box. **Nothing here asserts it is, or that it is not.**
2. **Whether the registered geometry is the true ONERA M6** — the STL is patch-extracted from
   a tutorial mesh. V and G do not care; P would.
3. **Whether `hierarchical` is deterministic on this box** — not assumed; gate D measures it.
4. **Whether the family will pass its own admission checks.** Nesting and r are proved
   exactly; **non-orthogonality and skewness cannot be known before it is built**, which is
   why they are gated from three real logs and why an ABSENT log reads `ABSENT`.
5. **Whether 3000 iterations suffice, and whether 8-/16-rank efficiency holds** — assumptions,
   tested by §8.1.
6. **The tunnel's stagnation conditions, wall corrections and transition state** — all in the
   unheld primary; the case is closed non-dimensionally.
7. **Whether Fs = 1.25 is adequate on a shock-bearing 3D triple** — used because it is the
   lab's standing convention, not because this case has been shown to warrant it.

## 11. FREEZE

Gates, thresholds, caps and labels are **closed at first compute** (rule 2). Before first
compute an amendment is legal **only if it states the condition and how it was checked** —
naming a run directory from §9 that does not exist. After first compute, changes land **only
as dated addenda that cannot alter a gate, threshold, cap or label**; originals are struck,
never rewritten. This is a **frozen file**: a departure is a dated amendment at the foot with
a version bump and `lines whose number changed above this section: 0`.

<!-- addenda, if any, below this line; nothing above it is ever edited -->
