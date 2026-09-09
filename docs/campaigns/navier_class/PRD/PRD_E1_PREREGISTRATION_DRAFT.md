# PRD-E1 — PRE-REGISTRATION (DRAFT)

# DRAFT — NOT FROZEN, NOTHING RUN

> **This document is a DRAFT prepared by a heat-transfer `lab-lane` at the
> heat-transfer-supervisor's dispatch, 2026-09-09. It is NOT sha-frozen, NO
> compute has been launched, and NO comparator/build scripts have been authored.**
> It authorises nothing. The §3 supervisor review, the sha-freeze, the script
> authoring, the §2bb pre-flight, the final mesh decision and the launch are the
> supervisor's, and the GCI/Roache banding + Fs are coordinated with the
> verification team via the chief. Verdict vocabulary is fixed by `CLAUDE.md`
> rule 1 (`PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING`);
> no other word is used below as a verdict. Every physical figure below is a
> **frozen DESIGN INPUT** (chosen, not measured) unless tagged otherwise.

---

## §0 — CASE IDENTITY + CAMPAIGN LINEAGE

- **Case:** Porous Radiator Duct (PRD). Air forced through a full-cross-section
  porous core in a straight duct; the core is modelled as a Darcy–Forchheimer
  volumetric momentum sink.
- **Rung id:** **PRD-E1** — Porous Radiator Duct, **rung 1, EXACT-tier**.
- **Lineage:** the **Navier-class V&V spine, Case 3** (Sanaa-direct via chief,
  accepted 2026-09-09; `docs/LAB_STATE.md` heat-transfer update 44, and the
  Navier-spine reference-pack ruling at that file's line ~37467). Under that
  ruling, every Navier case's **first pre-registered gate is its EXACT-tier
  (analytic / regenerable) rung**; the MEASURED-tier gate rides `PENDING-data`
  because the reference packs are **link-only — zero PDFs and zero physical data
  values are on the box** (`/home/ubuntu/paper-incoming/CERTONOMOUS_REFERENCE_PACKS_BOTH/`,
  scoping lane a49468b9). For Case 3 the EXACT rung is the **Darcy–Forchheimer–Ergun
  analytic Δp-vs-velocity self-consistency gate**, which is exactly this rung.
- **DISAMBIGUATION (load-bearing to avoid a collision).** This "Case 3" is the
  **Navier-spine Case 3 (porous radiator)**. It is **NOT** the older T-family
  "Case 3" (the 16-point *motor-in-duct* CHT map, T23/T24,
  `docs/campaigns/T-family/CASE3_MAP_RESULTS.md`). Two different case-3 framings;
  this document concerns only the porous radiator.
- **Territory:** heat-transfer. Filing location **RULED by verification (§5 of
  `verification/campaign/PRD_E1_GATE_RULING_2026-09-09.md`), superseding the earlier
  `porous_radiator_duct/` sub-home**: the **canonical home is
  `docs/campaigns/navier_class/PRD/`** — the CASE dir is the case-id **`PRD`**, NOT
  `porous_radiator_duct`. This DRAFT now lives there
  (`docs/campaigns/navier_class/PRD/PRD_E1_PREREGISTRATION_DRAFT.md`). On **FREEZE**
  the record **renames to `PRD_E1_PREREGISTRATION.md`** and lands alongside
  `cases/navier_class/PRD/` (case inputs) and `verification/runs/navier_class/PRD/`
  (run outputs; NOT created yet — no compute has run), with the frozen prereg copy in
  `verification/campaign/`. **Rung id stays `PRD-E1`** (Case = `PRD`, rung `E1` =
  EXACT-tier rung 1; the alternative `N3E1` is REJECTED). `scripts/check_filing.py`
  **R7 now governs `docs/campaigns/navier_class/<CASE>/` at depth 5**, scoped to
  `navier_class` (registered by verification, HEAD 7d52dc13). See §11 item 2, now
  resolved, for the ruling of record.

---

## §1 — GEOMETRY (frozen design inputs)

All-hex straight duct, square cross-section, three streamwise segments:
inlet-development → **porous core** → outlet-recovery. Streamwise = **x**.

| quantity | symbol | frozen value | note |
|---|---|---|---|
| duct side (square section) | H | **0.100 m** | D_h = H = 0.100 m (square duct) |
| inlet-development length | L_in | **0.200 m** | = 2·D_h, approach-flow flattening |
| porous-core length | L_core | **0.100 m** | this is the **L** in Ergun Δp/L |
| outlet-recovery length | L_out | **0.200 m** | = 2·D_h, avoids outlet-BC contamination of the core |
| total length | L_tot | **0.500 m** | |
| bed porosity | ε | **0.40** | representative random-packed sphere bed |
| particle diameter | d_p | **0.003 m** | 3 mm spheres |
| working fluid | air | ρ = **1.2 kg/m³**, μ = **1.8e-5 Pa·s** (ν = 1.5e-5 m²/s) | incompressible, isothermal (constant properties) |

- **Porous zone:** a dedicated blockMesh block spanning **the full cross-section**
  (wall-to-wall, no bypass gap), x ∈ [L_in, L_in + L_core] = **[0.200, 0.300] m**.
  The cellZone is built by `topoSet` `boxToCell` over that byte-fixed bounding box
  (coincident with the core block bounds), so the same physical volume is captured
  at every mesh level.
- **Inlet:** uniform velocity U = (U_s, 0, 0) — the registered superficial value
  (§3). **Outlet:** fixed static pressure. **Duct walls:** no-slip.

---

## §2 — SOLVER, POROUS MODEL, AND THE EXACT D/f MAPPING

### 2.1 Solver + turbulence (frozen)
- **`simpleFoam`** — steady, incompressible, isothermal. The gate is pure
  hydraulics (Δp vs U_s); no energy equation. **NOTE (kinematic pressure):**
  `simpleFoam` solves kinematic pressure `p = P/ρ` [m²/s²]; the comparator MUST
  multiply the CFD Δp by ρ to obtain Pa before comparing with Ergun (which is in
  Pa). Flagged for the §2bb pre-flight (§2.4 below).
- **Turbulence:** **k-ω SST (Menter)**, RANS. **Wall treatment:** Menter's
  continuous / automatic near-wall treatment (`nutUSpaldingWallFunction` on nut;
  `omegaWallFunction`; `kqRWallFunction` on k), which is **valid across the whole
  y+ range**. We deliberately do **NOT** resolve to y+ ≤ 1: the gated Δp is
  **dominated by the volumetric D/f sink**, not by wall shear; the duct
  development/recovery boundary layers need only a *consistent* near-wall
  treatment across all levels (L-303 fixed recipe). The y+ gate (§5) checks the
  treatment stays inside its valid envelope and is applied consistently, not that
  y+ ≤ 1.
- **DELIBERATE EXCLUSIONS (stated with reason, per verification's pre-compute ruling):**
  - **NO Spalart–Rumsey farfield** — that is an external/tunnel BC; this is
    **internal duct flow** with an explicit inlet/outlet, so no farfield applies.
  - **NO Barlow–Rae–Pope blockage correction** — the core spans the full section
    and all references are per-frontal-area / superficial; there is no tunnel
    wall / model blockage ratio to correct. (Supervisor's call, corroborated by
    the Navier-spine ruling: cases 2/3/6 are internal, neither blockage nor
    farfield applies.)

### 2.2 Porous model (frozen)
- `fvOptions` → **`explicitPorositySource`**, `type DarcyForchheimer`, applied
  **volumetrically** over the full-cross-section core cellZone (NOT `porousBaffle`).

### 2.3 The exact D/f mapping — with the ½ρ derivation (LOAD-BEARING)

**Verified against the installed OpenFOAM v2606 source (api=2606, this box):**
- `…/porosityModel/DarcyForchheimer/DarcyForchheimer.H:34` documents the sink as
  **S = −(μ·d + (ρ|U|/2)·f)·U**, with d [1/m²] the Darcy coefficient and f [1/m]
  the Forchheimer coefficient (user-supplied `dXYZ`, `fXYZ`).
- `…/DarcyForchheimer.C:85-89` converts the user `fXYZ` to the internal `F_` with
  an explicit **`0.5`** factor, carrying the source comment
  *"the leading 0.5 is from 1/2*rho"*: `forchCoeff = 0.5*fXYZ`.
- `…/DarcyForchheimerTemplates.C:53,57-58` then assembles
  `Cd = μ·D_ + ρ|U|·F_` and applies `Udiag += V·isoCd; Usource -= V·((Cd − I·isoCd)·U)`.
- **Net:** the effective per-unit-volume sink is exactly
  **S = −(μ·d + ½·ρ|U|·f)·U** in terms of the **user-supplied** d, f. This lane
  reproduced the derivation from source; it is cited here as verified, and re-read
  is the supervisor's §3 check.

**Analytic Ergun law in SUPERFICIAL velocity U_s:**

    Δp/L = 150·μ(1−ε)²/(ε³ d_p²)·U_s  +  1.75·ρ(1−ε)/(ε³ d_p)·U_s²
         = A·U_s + B·U_s²

**Matching term-by-term to the OpenFOAM sink** (viscous → μ·d·U_s; inertial →
½·ρ·f·U_s²):

- **Darcy:**  d = 150·(1−ε)²/(ε³ d_p²)               [1/m²]
- **Forchheimer:**  f = 2×1.75·(1−ε)/(ε³ d_p) = **3.5**·(1−ε)/(ε³ d_p)  [1/m]

The **`3.5 = 2 × 1.75` is LOAD-BEARING**: it undoes OpenFOAM's internal ½ρ factor
so that ½·ρ·f = 1.75·ρ(1−ε)/(ε³ d_p) = B. Drop the factor of 2 and the inertial
Δp is **halved** — the single most likely silent error, which the smoke Δp-match
(§7) is designed to catch.

**Frozen coefficient values** (ε = 0.40, d_p = 0.003 m, air):

| coefficient | expression | value |
|---|---|---|
| A (Ergun viscous, per length) | 150·μ(1−ε)²/(ε³ d_p²) | **1687.5** Pa·s/m² |
| B (Ergun inertial, per length) | 1.75·ρ(1−ε)/(ε³ d_p) | **6562.5** Pa·s²/m³ |
| d (fed to OpenFOAM, streamwise) | 150·(1−ε)²/(ε³ d_p²) | **9.375e7** 1/m² |
| f (fed to OpenFOAM, streamwise) | 3.5·(1−ε)/(ε³ d_p) | **10937.5** 1/m |
| cross-check | ½·ρ·f | 0.5·1.2·10937.5 = **6562.5** = B ✓ |

### 2.4 Superficial-velocity convention (PINNED)
The `explicitPorositySource` default treats the **cell velocity as the
superficial (volume-averaged) velocity**, and the coefficients above are derived
in that convention. We therefore feed the inlet U as the **superficial** value
and expect the CFD Δp to reproduce the Ergun Δp evaluated at that same U_s.
**The smoke Δp-match (§7) IS the convention check**: under near-uniform approach
flow the CFD Δp must equal Ergun(U_s) within band, which can only hold if the
cell velocity is being used as superficial and the ½ρ factor is undone correctly.
*(For incompressible `simpleFoam`, exactly how ρ enters `explicitPorositySource`
and the kinematic-pressure handling is a verified-in-pre-flight item, §8/§2bb —
measured, not assumed.)*

### 2.5 Anisotropy — lateral-leakage suppression (PINNED)
Cross-stream (y, z) resistance is set **1000×** the streamwise value to suppress
any lateral leakage and keep the core flow 1-D:
`d = (9.375e7, 9.375e10, 9.375e10)`, `f = (10937.5, 1.09375e7, 1.09375e7)`.
**Anisotropy ratio = 1000, frozen.** (Belt-and-suspenders: the core already spans
the full section, so there is no bypass path; the ratio guards residual
cross-flow. Sensitivity: a much larger ratio stiffens the system without changing
the 1-D answer.)

---

## §3 — THE GATE (Ergun analytic + U_s set + proposed band + tier = EXACT)

- **Tier:** **EXACT** — the reference is the analytic Ergun law, **regenerable
  on-box, no external data**. This is a **self-consistency** gate: does the CFD
  reproduce the very law fed into its sink?
- **Registered superficial-velocity set** (5 points, spanning viscous-dominated to
  strongly inertial):

| U_s [m/s] | Re_p = ρU_s d_p/μ | Ergun Δp [Pa] | viscous fraction |
|---|---|---|---|
| **0.25** | 50 | **83.20** | 50.7 % |
| **0.50** | 100 | **248.44** | 34.0 % |
| **1.00** | 200 | **825.00** | 20.5 % |
| **2.00** | 400 | **2962.50** | 11.4 % |
| **4.00** | 800 | **11175.00** | 6.0 % |

  (Δp = A·L_core·U_s + B·L_core·U_s² = 168.75·U_s + 656.25·U_s², L_core = 0.10 m.)
  Both terms are genuinely exercised (viscous fraction 51 % → 6 %). Re_p 50–800
  sits inside the Ergun correlation's accepted range, though as a self-consistency
  gate regime-validity is not what is being tested.

- **`G-ERGUN` (the EXACT-tier gate):** at each registered U_s, the CFD Δp across
  the porous zone (area-averaged static p at the zone-inlet plane x=0.200 m minus
  the zone-outlet plane x=0.300 m, converted to Pa) must reproduce the analytic
  Ergun Δp **within a pre-registered relative band**, graded on a `CONVERGING`
  Roache triple (rule 5) with the band required to exceed the reported GCI.

- **PROPOSED band (supervisor + verification set the final value via chief):**
  **±3 % relative on Δp**, per U_s, at the gate level, with the hard constraint
  **band > reported GCI**; and an asymptotic sub-check that the
  Richardson-extrapolated Δp matches Ergun within **±1.5 %**.
  *Numeric justification (this is an EXACT analytic gate, so the band is tight and
  tied to discretization error, not loose):*
  - Second-order FV Δp on a converging hex grid — L3 discretization error is
    expected ≲ 1–2 % (GCI at Fs = 1.25 on a monotone triple).
  - Residual velocity non-uniformity across the core face (developing BL) vs the
    ideal 1-D uniform-U_s law — designed ≲ 1 % via 2·D_h development + the 1000×
    lateral resistance (registered loss mode in §4).
  - Measurement-plane averaging / plane placement — ≲ 0.5 %.
  - Quadrature sum ≈ 2–2.5 %; **±3 %** gives modest margin without being loose.
  *(Final band, the GCI/Roache banding and Fs are coordinated with verification
  via the chief; this is a proposal, not a decision.)*

---

## §4 — PREDICTIONS (prediction-first, frozen before any run)

| id | prediction |
|---|---|
| **P-DP** | CFD Δp reproduces analytic Ergun within the §3 band at all 5 U_s, on a `CONVERGING` triple |
| **P-CONV** | the monitored Δp **plateaus** (change < solver-noise floor over the last N iterations) at every U_s and every level; convergence gated on the plateau, never on rc = 0 alone (L-15/L-89) |
| **P-GRID** | the 3-level Δp triple is monotone/`CONVERGING` at each U_s; GCI (Fs = 1.25) shrinks with refinement; observed order p in [~1.5, 2.5] for a 2nd-order scheme |
| **P-YPLUS** | max wall-patch y+ stays inside the continuous-treatment envelope on every level (~40–80 / ~20–40 / ~10–20 at L1/L2/L3 at U_s = 1), consistent recipe across levels |
| **Registered loss modes** (a run may lose on any): (a) missing/incorrect ½ρ factor → inertial Δp halved; (b) velocity non-uniformity at the core face exceeding the band budget; (c) a pre-asymptotic / non-`CONVERGING` triple → `NOT A RESULT` (rule 5); (d) p-solver tolerance not ≥ 1 decade below the band → Δp gate not solver-resolvable (L-514); (e) lateral leakage if the anisotropy ratio is too small. |

---

## §5 — MESH LADDER + checkMesh GATE + y+ GATE + GCI PLAN

- **All-hex `blockMesh`**, three streamwise blocks (in / core / out); the core
  block IS the porous cellZone. **Refinement ratio r = 2**, uniform in all three
  directions. **Geometry + porous-zone definition held BYTE-FIXED across levels**
  (L-303): only the `simpleGrading` cell counts change (×2 per direction per
  level); every vertex coordinate and the topoSet box are byte-identical. **Never
  step a snappy level between rungs** (this is pure blockMesh; no snappyHexMesh).

| level | cross-section | streamwise (in/core/out) | cells |
|---|---|---|---|
| L1 (coarse) | 16 × 16 | 24 / 24 / 24 | **18,432** |
| L2 (medium) | 32 × 32 | 48 / 48 / 48 | **147,456** |
| L3 (fine) | 64 × 64 | 96 / 96 / 96 | **1,179,648** |
| **L4 (BUDGETED, L-244/N-T2)** | 128 × 128 | 192/192/192 | **9,437,184** |

  L4 is **budgeted, not committed** — run only if a triple is pre-asymptotic
  (non-monotone or observed order outside band), at the worst-behaved U_s.

- **`checkMesh` GATE:** non-orthogonality **< 70** (mean **< 20**), skewness
  **< 4** — a clean all-hex blockMesh duct is ≈ 0 / ≈ 0. A failure **stops the
  rung before any solver launches**. **Watch grading at the zone entry/exit**
  (L-142): the core block and the development blocks share the cross-section
  discretization and match streamwise cell size at the shared faces; cell
  expansion ratio ≤ 1.2 per cell in every band.
- **y+ GATE** (mirrors the T23G2R `G-YPLUS` pattern, tied to the wall treatment
  in use): report **max y+ on every wall patch, every level**; gate that y+ stays
  inside the **continuous/Menter treatment valid envelope** (proposed upper bound
  **≤ 200**, with the continuous treatment in use so no lower y+ is invalid), and
  that the near-wall recipe is applied **consistently across all three levels**
  (fixed recipe, L-303). Primary instrument
  `simpleFoam -postProcess -func yPlus -latestTime`; independent cross-check
  reader from U, nut, polyMesh that **plants a perturbation, reads it back, and
  refuses if it cannot see it** (rule 3); the two must agree, and a perfect zero
  from either is REFUSED. *(Final y+ threshold coordinated with verification.)*
- **GCI plan:** Roache/Celik triple graded per rule 5 ordering, **GCI at
  Fs = 1.25**, on a monotone `CONVERGING` triple only; GCI never quoted off a
  non-monotone triple. The gated quantity is Δp per U_s. The GCI/Roache banding +
  Fs are **coordinated with the verification team via the chief** (verification
  audits this prereg pre-compute).

---

## §6 — PLANTED-ZERO CONTROL DESIGN (rule 3)

The Δp comparator reads Δp from the pressure field the solver **wrote** to disk.
Three controls, and the zero is trusted only because the reader is shown able to
see a non-zero:

1. **Zero-visible control (`D=f=0`):** a case with the porous coefficients set to
   zero → CFD Δp ≈ 0 (only sub-Pa clear-duct friction, ≪ band). The reader reads
   this near-zero **from a file the solver wrote** — this shows the reader can
   report a zero.
2. **Non-zero-visible control (`D,f` set):** the real coefficients → Δp > 0 at
   Ergun order. This shows the same reader can report a non-zero. *(A zero from a
   reader not shown able to see a non-zero is refused — this pair is what licenses
   trusting control 1.)*
3. **Planted-perturbation read-back:** a distinctive known constant
   **`PLANT_DP = 3.210 Pa`** (non-round, sized to the reader's resolution and well
   above solver noise yet well below the smallest gated Δp of 83.2 Pa) is added to
   the zone-outlet plane pressure sample; the comparator asserts the reported Δp
   shifts by exactly `PLANT_DP` within tight tolerance, else **REFUSES**; the
   plant is then removed. This proves the reader is wired to the field the solver
   actually wrote (the T3/T10a `plant → read-back → refuse-if-unseen` pattern).

---

## §7 — THE SMOKE TEST (the pre-graded gate, run BEFORE the graded ladder)

Coarse (L1), single U_s = 1.0 m/s. **If any clause fails, STOP — do not launch
the ladder.** Clauses:

1. **`checkMesh`** passes the §5 gate (non-ortho < 70 / mean < 20, skew < 4).
2. **Porosity active:** Δp > 0 and at Ergun order (within a loose coarse factor,
   ~±20 %, on L1 — not the graded band).
3. **Planted-zero pair + plant read-back** (§6): D=f=0 → Δp ≈ 0; D,f set → Δp > 0;
   `PLANT_DP` read back and asserted.
4. **Δp plateau** (L-15/L-89): monitored Δp change < tol over the last N
   iterations — the convergence criterion, not rc = 0.
5. **Completion clauses** (rule 4 + age guard, adapted to the incompressible
   isothermal field set — see §8): rc = 0; `End` line; last time == `endTime`;
   fields **{U, p, k, omega, nut, phi}** present and **every one NEWER than the
   case's own `0/` dir** (age guard); `ExecutionTime` count == round(endTime/deltaT).
6. **L-514 measurement:** measure the near-convergence Δp sensitivity to the
   p-solver tolerance (run at relTol 1e-3 and 1e-5); confirm solver-induced Δp
   variation is ≥ 1 decade below the §3 band. **The final p-solver tolerances are
   pinned FROM THIS MEASUREMENT** (a dated addendum recording the measured
   sensitivity and chosen values; addenda cannot move a gate/band/label), rather
   than guessed. Provisional recipe: `p` solver relTol 1e-3, abs tol 1e-8 (one
   decade below the finest monitored-Δp resolution), explicit `maxIter`; SIMPLE
   `residualControl` p ≤ 1e-6.

---

## §8 — §2bb PRE-FLIGHT + §2ba AUTOGRADER + §2bc (specs only — NOT authored here)

- **§2bb pre-flight (executability, before freeze→launch; supervisor runs
  `scripts/check_ladder_preflight.py`-class check):** the level manifest (L1/L2/L3
  cell counts, byte-fixed vertices + topoSet across levels); the case builds,
  `blockMesh` + `topoSet` succeed, decomposition succeeds; `fvOptions` parses and
  the DarcyForchheimer coefficients read back equal to the §2.3 frozen values;
  a tiny exercise confirms the sink is **active** (D,f set → nonzero Δp) and
  **inert** (D=f=0 → ~zero Δp); **VERIFY** the incompressible-`explicitPorositySource`
  ρ handling and kinematic-pressure conversion (§2.1/§2.4) against the actual
  written fields — measured, not assumed.
- **§2ba detached autograder (spec):** a collector/grader launched **detached
  (PPID=1, survives fleet death)** that, per U_s and per level: watches the
  monitored Δp to **plateau**; applies the rule-4 completion clauses + age guard
  (incompressible field set); reads Δp via the planted-zero-controlled reader
  (§6); assembles the 3-level triple and grades it under rule 5 (`CONVERGING` →
  band test; else `NOT A RESULT` with both triples + orders printed); computes GCI
  at Fs = 1.25; applies `G-ERGUN`, the y+ gate and the checkMesh gate; writes a
  durable `gate_prd_e1.json`. **Not authored in this draft** (STOP-BEFORE-SCRIPTS).
- **§2bc exhaustion-evidence acceptance gate (CHARTER v1.74 §2bc, instrument
  `scripts/check_exhaustion_evidence.py`):** OpenFOAM plainly **CAN** do this
  (DarcyForchheimer is a standard, shipped porosity model — the §2bb active/inert
  exercise is the capability proof). Accordingly **no `BLOCKED` verdict is
  admissible without exhaustion evidence**; a stop is legal only if a genuine
  OpenFOAM incapacity is demonstrated and evidenced (Sanaa doubts one exists).

---

## §9 — COST ESTIMATE (rule 12: core-minutes, POINT + CAP, dollars derived)

Unit = **core-minutes** (wall s × ranks ÷ 60). Rate **c7a.4xlarge $0.0513/core-h**
(16 vCPU); **the box cannot read its own billing, so every dollar figure is
DERIVED, reported-by-owner, not measured** (`COMPUTE_BUDGET_CHARTER.md` §5).

- **Design:** the primary proposal runs **all 5 U_s at all 3 levels = 15 solves**
  (a `CONVERGING` triple per U_s), plus the smoke set. Per-solve wall-time design
  estimates on 16 ranks: L1 ~2 min, L2 ~10 min, L3 ~40 min.
- **POINT estimate:** per U_s (2+10+40) = 52 wall-min × 16 ranks = 832 core-min;
  × 5 U_s = **≈ 4160 core-min ≈ 69 core-h ≈ $3.6 (DERIVED)**. Smoke + planted-zero
  coarse solves add ≪ 5 core-h.
- **CAP:** includes one L4 contingency at the worst U_s (~9.4M cells, ~5 wall-h ×
  16 = ~80 core-min... → 4800 core-min) + reruns → **CAP ≈ 9000 core-min ≈ 150
  core-h ≈ $7.7 (DERIVED)**. **Under $25** (= 487 core-h at the recorded rate), so
  within the standing pre-authorisation — **still costed here per rule 12; a
  blanket is not a per-item read (rule 9).** An overrun **stops the run**.
- **Rule-12 calibration owed at completion:** actual core-min from logs vs this
  estimate, ratio + gap attribution, as a row in `docs/COST_CALIBRATION.md`.
- **Open cost lever:** a leaner alternative (anchor triple at one U_s + the curve
  at L3 only = 7 solves) roughly halves cost but gives per-point convergence
  evidence only at the anchor. See §11.

---

## §10 — DEFERRED TIERS + EXACT OFF-BOX DATA NEEDED FROM SANAA

**Flagged on Sanaa's desk; OFF-BOX; NOT fabricated.** These are MEASURED-tier
rungs that ride `PENDING-data` until the referenced source is retrieved to the
box **and title-page-verified (L-144)**; no unconfirmed number becomes a frozen
threshold.

- **Real-radiator D/f (louvered-fin / plate-fin core):** the actual Darcy–
  Forchheimer coefficients from **Kays & London,** *Compact Heat Exchangers* (or a
  named louvered-fin dataset) — needed to replace the Ergun packed-bed stand-in
  with a real radiator core. **Data value not on box.**
- **Idelchik duct-loss coefficients** for the development/recovery duct fittings —
  a follow-on validation. **Not on box.**
- **Mehta–Bradshaw uniformity K** — a planned follow-on rung demonstrating the
  flow-uniformity **mechanism on-box** (screen/honeycomb), **NOT gated against
  their K** until the datum is retrieved + TP-verified. **Not on box.**

**Exact ask of Sanaa:** retrieve to the box (as PDF + title-page verification) any
one of the above to unblock the corresponding MEASURED-tier rung; PRD-E1 itself
needs **none of them** — it is fully regenerable on-box.

---

## §11 — OPEN QUESTIONS FOR THE SUPERVISOR (§3)

1. **Final Δp band:** ±3 % proposed (with band > GCI, and ±1.5 % on the
   Richardson-extrapolated value). Verification + chief coordinate the final value
   + the GCI/Roache banding + Fs.
2. **Filing location + rung id — RESOLVED (verification §5, 2026-09-09):**
   `verification/campaign/PRD_E1_GATE_RULING_2026-09-09.md` §5 rules the canonical
   home is **`docs/campaigns/navier_class/PRD/`** — the CASE dir is the case-id
   **`PRD`**, superseding the earlier `porous_radiator_duct/` sub-home the chief's
   prior note used. Prose now lives there; on FREEZE this record **renames to
   `PRD_E1_PREREGISTRATION.md`** and lands with **`cases/navier_class/PRD/`** (case
   inputs), **`verification/runs/navier_class/PRD/`** (run outputs; not created — no
   compute yet), and the frozen prereg copy in **`verification/campaign/`**. Case id
   **PRD**; rung **E1**; the rung id **PRD-E1 is confirmed** and the alternative
   `N3E1` is **REJECTED**. This draft was relocated out of `docs/campaigns/T-family/`
   and then into `docs/campaigns/navier_class/PRD/` accordingly. Verification has
   **registered the `check_filing` form**: **R7 now governs
   `docs/campaigns/navier_class/<CASE>/` at depth 5**, scoped to `navier_class`
   (HEAD 7d52dc13); `PRD_E1_PREREGISTRATION.md` matches `CAMPAIGN_RECORD_MD`. The
   filing charter / `scripts/check_filing.py` remains the authority.
3. **Solve matrix (cost lever):** the rigorous 15-solve (5 U_s × 3 levels) design
   vs the leaner 7-solve (anchor triple + L3 curve). §9 costs both; both under $25.
4. **y+ gate threshold + wall treatment confirm:** continuous/Menter treatment
   with y+ ≤ 200 upper bound proposed — confirm this over a resolved-y+≤1 option.
5. **Incompressible ρ / kinematic-pressure handling** in `explicitPorositySource`:
   registered as VERIFY-in-§2bb (§2.4) — confirm this is the right place to pin it,
   or pin ρ explicitly in the frozen case.
6. **Completion field set** for isothermal incompressible `simpleFoam`
   ({U, p, k, omega, nut, phi} — NOT the thermal {T, p_rgh, alphat}); confirm the
   `mark_done`-class instrument is given this field list.

---

*END OF DRAFT — NOT FROZEN, NOTHING RUN.*

---

## AMENDMENT (pre-compute, 2026-09-09): verification PRD_E1_GATE_RULING adopted

**Condition (VERIFICATION_CHARTER §2b, stated and checked):** no PRD-E1 compute has
run — **`verification/runs/navier_class/PRD/` does not exist (verified 2026-09-09)** —
so the pre-registration is still open and this pre-compute amendment is LEGAL. It
alters no frozen physical figure; it ADOPTS the gate design ruled by verification.
This DRAFT remains **NOT FROZEN**.

**Source adopted (cited by path):**
`verification/campaign/PRD_E1_GATE_RULING_2026-09-09.md` (verification-supervisor,
2026-09-09). That ruling independently re-derived and **CONFIRMED** every frozen
physical figure in this draft (Ergun A = 1687.5, B = 6562.5; OpenFOAM-fed
d = 9.375e7, f = 10937.5 with ½ρf = 6562.5 = B; the five Δp
83.20 / 248.44 / 825.00 / 2962.50 / 11175.00 Pa; the 3.5 = 2×1.75 ½ρ-undo factor).
Those numbers are UNCHANGED — this amendment binds the GATE, not the physics.

### The BINDING gate elements now adopted (verbatim in force from the ruling)

1. **Ladder = FULL 15-solve** — 5 U_s {0.25, 0.5, 1, 2, 4 m/s} × 3 levels
   L1/L2/L3 at refinement ratio **r = 2**, i.e. a `CONVERGING` Roache triple per
   U_s. The **lean-7 design is REJECTED** (a single-grid value at four of five U_s
   is NOT A RESULT for a grid-gated quantity, and it leaves the inertial-dominated
   end where the ½ρ factor dominates ungraded). Ruling §3.

2. **`G-ERGUN`** — per-level CFD Δp reproduces analytic Ergun **within ±3 %
   relative**, per U_s, at the gate level, with the hard constraint **band >
   reported GCI**. **Pre-asymptotic guard (ruling §1.2):** if the reported **L3 GCI
   (Fs = 1.25) ≥ 2.0 % for any U_s**, that U_s is **PRE-ASYMPTOTIC** → run the
   already-budgeted **L4** and **re-form the triple at (L2, L3, L4)** before issuing
   any PASS / GATE FAIL for it. A band dominated by discretization is not graded.

3. **`G-ASYMP` (BINDING; ruling §1.3, elevated from sub-check to a gate)** — the
   **Richardson-extrapolated Δp within ±1.5 % of Ergun**, quoted **only on a
   monotone `CONVERGING` triple** (rule 5), never off a non-monotone one. A clean
   `CONVERGING` triple that lands inside ±3 % per-level but **outside ±1.5 %
   asymptotic is a `GATE FAIL` naming the mechanism** — core-face velocity
   non-uniformity, or the ρ / superficial-velocity handling in
   `explicitPorositySource` — and under **§2bc that is NEEDS-SUCCESSOR
   (non-terminal)** unless the model/setup ladder is exhausted; it is NOT an
   admissible terminal fail on first sight.

4. **Gate hierarchy (frozen order; ruling §1.4, rule 5):**
   (1) any level not iteratively converged / not plateaued → **NOT A RESULT**;
   (2) triple **not `CONVERGING`** (DIVERGENT / STAGNANT / OSCILLATORY / EXACT) →
   **NOT A RESULT**, both triples + orders printed beside it;
   (3) `CONVERGING` → **G-ERGUN AND G-ASYMP** → **PASS only if BOTH hold**, else
   **GATE FAIL** with the failing gate + mechanism named. **GCI (Fs = 1.25) is
   always printed.** **PASS at all five U_s is the credential.**

5. **GCI factor `Fs = 1.25` — CONFIRMED** (ruling §2; standing standard, not a
   choice) for a ≥3-grid study at constant r = 2 with an **observed order p
   reported**. **p outside [1, ~2.5] or a non-monotone triple → NOT A RESULT and
   run L4**; a **GCI is NEVER quoted off a non-monotone triple**.

### The 8 §4 freeze conditions carried forward (full text in the ruling §4)

The freeze may not proceed until all hold; each is stated fully at
`verification/campaign/PRD_E1_GATE_RULING_2026-09-09.md` §4:

1. **§2bb pre-flight PASS** — deadline sizing + each distinct solver path past
   decompose+first-solve; DarcyForchheimer coefficients read back == the §2.3 frozen
   values; sink exercised ACTIVE (D,f set → Δp>0) and INERT (D=f=0 → ~0); and the
   **MEASURED incompressible-`explicitPorositySource` ρ handling + kinematic→Pa
   conversion (§2.1/§2.4) resolved against the written fields BEFORE freeze**.
2. **3 planted-zero controls (rule 3)** — the D=f=0 / D,f-set visibility pair AND
   the **`PLANT_DP = 3.210 Pa`** read-back-or-refuse; a perfect zero from any reader
   is REFUSED.
3. **Verification's non-delegable §3 check-1 diff-read** of every measurement script
   (coefficient generator, Δp reader, y+ reader, triple/GCI grader) before any
   graded number is believed — where the v2606 ½ρ source claim is re-verified
   against the authored code.
4. **§2ba dual-mechanism run** — a live monitor AND a detached (PPID = 1) grader
   pinned to the FROZEN comparator (rule 2 disk == pin re-hash), surviving fleet
   death; neither substitutes for the other.
5. **Completion field set `{U, p, k, omega, nut, phi}`** (incompressible isothermal —
   NOT the thermal {T, p_rgh, alphat}); every field newer than the case's own `0/`
   (age guard); last time == endTime; **clause-5 `ExecutionTime == round(endTime/
   deltaT)` — FIXED-deltaT (steady simpleFoam, deltaT = 1 → == endTime)**, not the
   adaptive-dt path. The `mark_done`-class instrument is given this field list
   explicitly.
6. **y+ gate** — continuous / Menter treatment, **y+ ≤ 200 upper bound, consistent
   recipe across levels** (not y+ ≤ 1, because the gated Δp is dominated by the
   volumetric D/f sink, not wall shear); max y+ per patch per level reported; the
   cross-check reader plants → reads back → refuses (rule 3).
7. **Deliberate exclusions confirmed** — **NO Spalart–Rumsey** farfield and **NO
   Barlow–Rae–Pope** blockage: this is INTERNAL duct flow with an explicit
   inlet/outlet and a full-section core.
8. **§2bc OpenFOAM-capable** — DarcyForchheimer is a shipped model; the §2bb
   active/inert exercise IS the capability proof. No `BLOCKED` verdict is admissible
   without measured exhaustion evidence.

**Scope of this amendment:** it does not freeze anything, author any script, launch
any compute, or move any verdict. Script authoring (comparator / build / mark_done)
remains the next, separate step, gated on verification's §3 check-1 diff-read. The
draft's earlier §1–§11 proposals for band/Fs/ladder are now RESOLVED by the elements
above; where the earlier prose called them "proposed" or "coordinated via the chief,"
this amendment records that verification has RULED them.

*— heat-transfer `lab-lane`, pre-compute amendment 2026-09-09. STILL NOT FROZEN.*

---

## ADDENDUM (pre-compute, 2026-09-09): L-514 p-solver tolerance PINNED from the §7.6 two-relTol sensitivity measurement

**Condition (VERIFICATION_CHARTER §2b / CLAUDE.md rule 2, stated and checked):** no
PRD-E1 compute has run in its real run home — **`verification/runs/navier_class/PRD/`
does not exist (verified 2026-09-09 21:28 UTC)** — so the pre-registration is still
open and this pre-compute addendum is LEGAL. The §7.6 sensitivity solves below ran
**in a scratch working directory only** (session scratchpad `.../prd_l514/`); the
real run home was **NOT created**, so PRD-E1 remains freeze-legal (no compute in its
runs dir). This DRAFT remains **NOT FROZEN**.

**Scope (what this addendum may and may not do):** it pins the **linear p-solver
tolerance** required by §7 clause 6 and the §4 freeze conditions (the L-514 pin),
FROM a measurement, per the draft's own instruction that "the final p-solver
tolerances are pinned FROM THIS MEASUREMENT" (§7 clause 6). It **moves NO gate, band,
threshold, cap, label or physical figure**: `G-ERGUN` (±3 %), `G-ASYMP` (±1.5 %), the
gate hierarchy, Fs = 1.25, the five Ergun Δp targets, A/B, d/f, the mesh ladder and
the §9 cost cap are ALL UNCHANGED. It pins a solver tolerance only.

**Measurement (coarse L1, ACTIVE, U_s = 1.0 m/s, endTime 2000, serial / RANKS = 1,
scratch).** Two p-solver recipes, everything else byte-identical (GAMG / GaussSeidel,
maxIter at the GAMG default, SIMPLEC `consistent`, relaxation 0.9, no
`residualControl` — run-to-endTime per ruling §4.5):

| recipe | p relTol | p abs tol | plateau Δp [Pa] | rel. to Ergun 825 | plateau p init. residual |
|---|---|---|---|---|---|
| (a) provisional | 1e-3 | 1e-8 | **825.203** | +0.0247 % | 6.57e-9 |
| (b) tighter | 1e-5 | 1e-8 | **825.158** | +0.0192 % | 8.33e-10 |

- **Solver-induced Δp variation** |Δp(a) − Δp(b)| = **0.0453 Pa**.
- **±3 % band** at Ergun 825 Pa = **±24.75 Pa**. The variation is **546× smaller =
  2.74 decades below the band**, i.e. **≥ 1 decade below** — the L-514 requirement
  (§4 freeze conditions; §4 loss mode (d)) is **SATISFIED**: the Δp gate is
  solver-resolvable.
- **Binding limit = the ABSOLUTE tolerance, not relTol.** At plateau the p **initial**
  residual is already below abs tol 1e-8 in both recipes (6.57e-9 and 8.33e-10);
  relTol × initial residual (~1e-12 to 1e-15) is orders below abs 1e-8, so **relTol
  never binds** — abs tol 1e-8 floors the p-solve resolution. Tightening relTol from
  1e-3 to 1e-5 moves Δp by only 0.045 Pa, confirming relTol is not the controlling
  parameter.

**Δp reader:** `analyse_prd.read_dp_pa` (the ×ρ kinematic→Pa converter, RHO = 1.2),
last `surfaceFieldValue.dat` row at endTime; p_out_kin ≈ 0.079 (outlet fixed 0),
p_in_kin ≈ 687.7 → ×1.2 = the Δp above.

**PINNED FINAL p-solver values (= the provisional, CONFIRMED by measurement):**
- `p` linear-solver relTol = **1e-3**
- `p` linear-solver abs tolerance = **1e-8**
- `p` maxIter = **1000 (explicit; §7 clause 6)** — measurement confirmed maxIter never
  binds (0–1 sweeps at plateau).

The relTol and abs-tolerance pinned values **equal what `build_prd.py` writes**
(fvSolution p-block: `tolerance 1e-08; relTol 0.001;`). Per §7 clause 6, `maxIter
1000;` is now written **explicitly** in the p-block — a **behaviour-identical**
alignment, since the GAMG default is already 1000 and maxIter never binds (the
measurement above) — and the emitted `// L-514` marker now cites this addendum
(`§7.6 two-relTol sensitivity`) in place of the provisional wording.

**Cost (rule 12; core-min = wall_s × ranks ÷ 60; ranks = 1):** recipe (a) 72 s =
**1.200 core-min**; recipe (b) 73 s = **1.217 core-min**; total **2.417 core-min ≈
0.0403 core-h**. Dollars **DERIVED** at $0.0513/core-h = **≈ $0.0021** (reported-by-
owner, not measured — the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5). Well under the $25 pre-authorisation and the §9 cap.

*— heat-transfer `lab-lane`, L-514 p-solver pin addendum 2026-09-09. STILL NOT
FROZEN. No compute ran in the PRD run home; scratch only.*
