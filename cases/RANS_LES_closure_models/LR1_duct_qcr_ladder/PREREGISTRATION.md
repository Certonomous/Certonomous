# LR1 — MODEL-FORM VALIDATION LADDER ON `DUCT/AR_1_Ret_360` (SST-linear vs corrections)

**Rung (PROVISIONAL id):** `LR1_duct_qcr_ladder`
**Team:** closure
**Status:** `prereg_commit: PENDING_SUPERVISOR_FREEZE`. The gates, thresholds,
bands, cap and label below are **drafted and not yet closed**. The freeze is the
supervisor's act, performed personally under `SUPERVISION_CHARTER.md` §3 check 4,
and is a commit whose message carries the sha256 of this document and of the grade
instrument once written. **Nothing has been staged into a run root, no queue entry
has been filed, no comparator has been written, and no compute has been spent.**
Standing rule 2 closes these gates at the freeze; before it, amendments are legal
and **must state the condition and how it was checked** — every drafted threshold
below is marked `PENDING-FREEZE` for exactly that reason.
**Drafted:** 2026-09-07, by a closure drafting lane on the closure supervisor's
dispatch, as authorised zero-compute F6 preparation.

**Naming, and it is a PROVISION, not a claim on the matrix.** The id
`LR1_duct_qcr_ladder` is **provisional**. This record is a *contribution handed to
its owner*: exactly as `cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md` §0
states of every row it offers — *"the owner re-maps, renames, merges or rejects any
row here without asking"* — the matrix owner / Sanaa may re-map this id (it may
belong in an `L` ladder column, or be folded beside G2 in the `G`/`P` columns; that
is the owner's call). The letters here are offered so a re-mapping is a mechanical
relabel, not a re-audit. This rung claims nothing about the R ladder R1–R6
(`docs/closure/CLOSURE_LINE_RESTART_DOCTRINE.md`).

---

## 0. WHAT THIS RUNG IS, AND THE ONE THING IT MUST NOT BE READ AS CLAIMING

This is **Sanaa's model-form validation ladder** (her 2026-09-04 directive,
`etc/sessions/2026-09-04T1510Z_sanaa_model_form_closure_ladder.md`, authority
`0910b664`) applied to the square duct — the **"first ladder record" of**
`docs/closure/correction_library/INGEST_PLAN.md` **§4 Phase 3**, targeting Sanaa's
named first certified product recorded in that plan's §1: **"correction X recovers
this flow where SST could not."** It sits directly **above G2**
(`cases/RANS_LES_closure_models/G2_grid_triple_duct/PREREGISTRATION.md`), which is
the grid-convergence / numerical-cause rung for the SST duct, and it **reuses G2's
grid triple** (§2.2).

It reproduces the reproduction-target **OPTION (ii)** written into the library
entry `docs/closure/correction_library/entries/b_qcr2000_spalart2000.md` (§"What
`REPRODUCED` would have to mean"): the correction under test is **SST+QCR
(`kOmegaSSTQCR`, already built on this box)**, compared a-posteriori against
**SST-linear**, against the lab-held DNS/LES duct reference.

> **THE STANDING DISCLOSURE, AT THE TOP OF THE FILE AND NOT BURIED.** This is
> **NOT Spalart's own configuration.** Spalart 2000 demonstrated the QCR
> constitutive relation on **Spalart–Allmaras**, and **no SA-QCR exists on this
> box** (`b_qcr2000_spalart2000.md` `paper_validation_cases` and
> `what_it_cannot_see` (c), both read off the rendered page by the supervisor
> 2026-09-06). This rung is therefore **evidence ABOUT QCR in this lab's hands** —
> "SST+QCR recovers what SST-linear could not" — and is **NOT a reproduction of
> Spalart's paper result.** No line of this record may quietly substitute one for
> the other. The paper also publishes **no numeric error metric** for the duct
> ("much closer to experiment" and a figure are the whole of it, `claimed_effect`),
> so every gate below is registered against the reference data this lab holds, never
> against a figure of the paper's.

### 0.1 What this rung does NOT claim

* **It does not claim numerical convergence** — that is G2's product, cited here,
  not re-derived. LR1 is a **model-form** result: it grades whether a model's
  *constitutive form* produces the corner physics, having G2 rule out the mesh.
* **It does not claim to reproduce Spalart 2000** (see the disclosure above).
* **It does not register `ShihQuadraticKE` or `LienCubicKE` as provenance-tagged
  library entries.** Those entries cannot be registered until **Shih 1995
  (CMAME 125:287)** and **Craft, Launder & Suga 1996 (IJHFF 17:108)** are held and
  title-page verified (L-144); neither is on this box (retrieval gap, on Sanaa's
  desk). In this record they appear as **stock models that were run**, not as
  library entries, and no provenance claim is attached to them.
* **It does not treat "beating zero secondary flow" as the evaluation** (rule 3 /
  charter §1). The comparison of merit is **model-vs-DNS**; the trivial zero of the
  linear model is the thing being explained, not the bar being cleared.

---

## 1. THE LADDER, RECORDED IN FULL (Sanaa's four rungs, for the duct)

Sanaa's rule is that the **full ladder is recorded**, so the sweep is designed so
that whichever framing she chooses at freeze, the evidence is present. Every model
is run **a-posteriori on the G2 grid triple (L1/L2/L3)** against `AR_1_Ret_360`.

### 1.1 RUNG 1 — exhaust stock RANS

| model | class | lib | expectation registered before the run |
|---|---|---|---|
| `kOmegaSST` | linear EVM | stock (`libincompressibleTurbulenceModels.so`) | **the "SST could not" baseline** — `\|U_sec\|_max/U_bulk` below the floor (§3.1), a **model-form** null, not numerical (G2 rules out numerical). Corroborated already: G2 §4.0 measured the SST duct in-plane residuals never decrease and `Uy,Uz` sit at machine noise. |
| `realizableKE` | linear EVM | stock | linear control — near-null secondary flow |
| `kEpsilon` | linear EVM | stock | linear control — near-null secondary flow |
| `ShihQuadraticKE` | **nonlinear (quadratic) EVM** | stock (15 syms) | a **family-(b) quadratic constitutive relation** — MAY recover the duct at rung 1 |
| `LienCubicKE` | **nonlinear (cubic) EVM** | stock (18 syms, runtime `New`) | a **family-(b) cubic constitutive relation** — MAY recover the duct at rung 1 |
| `LienLeschziner` | **nonlinear EVM** | stock (17 syms) | MAY recover the duct at rung 1 |
| `LRR` | **RSM** | stock (6 syms) | resolves anisotropy transport — **likely recovers** |
| `SSG` | **RSM** | stock (6 syms) | resolves anisotropy transport — **likely recovers** |

All eight symbols confirmed present on this box by the supervisor (`nm -DC`;
positive controls `kEpsilon=12`, `kOmegaSST=19` syms) in
`libincompressibleTurbulenceModels.so` at
`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/lib/`.

> **THE CONSEQUENCE SANAA'S LADDER IMPLIES, REGISTERED NOW BEFORE ANY VALUE
> EXISTS.** If a **stock** model (a nonlinear EVM or an RSM) recovers the duct at
> rung 1, **the case resolves at rung 1 and never needs rung 3.** The certified
> result must then **honestly attribute recovery to the stock model**, and QCR
> becomes a **parallel rung-3 confirmation**, not the novelty. This record must
> **not** claim rung-3 novelty for something a stock nonlinear EVM does at rung 1.
> This is registered in advance precisely so the attribution cannot be chosen to
> fit the answer.

### 1.2 RUNG 2 — rule out the numerical cause

**Discharged by G2, cited, not re-run here.** A `CONVERGING` SST `gradP` triple in
G2 with a small GCI establishes that the discrete equations are solved
consistently, so the SST null secondary flow is **model-form, not mesh**. G2 is
itself `PENDING_SUPERVISOR_FREEZE`; see FREEZE PRECONDITION (a) in §8.

### 1.3 RUNG 3 — literature correction, applied individually

| model | class | lib | coefficient |
|---|---|---|---|
| `kOmegaSSTQCR` | SST + QCR2000 traceless quadratic correction | **USER** `libkOmegaSSTQCRTurbulenceModels.so` (`/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/lib/`, symbol resolves) | `Ccr1 = 0.3` (Spalart 2000 p. 253, **untrained**; `b_qcr2000_spalart2000.md` `install_stanza`) |

`Ccr1 = 0.3` is itself a **transferred calibration** — Spalart calibrated it "in
the outer region of a simple boundary layer" (p. 253) and this rung applies it to a
**duct** (L-219; `b_qcr2000_spalart2000.md` contraindication (5)). That transfer is
stated, not hidden, and it is the same condition charter §22.4 item 4 imposes on any
literature magnitude.

### 1.4 RUNG 4 — the lab's own GP closures

**BLOCKED — capability-absent.** No GP turbulence model is built on this box
(`INGEST_PLAN.md` §1 records this route as *"currently capability-absent, and that
is an honest gap"*). Recorded as `BLOCKED`, in the rule-1 vocabulary — **not a gap
papered over**, and not `NOT A RESULT` (nothing was run to produce a non-result).

### 1.5 The count that costs

**9 models are run** (8 at rung 1 + 1 at rung 3) **× 3 grid levels = 27 solves.**
Rung 2 is a citation (no solve); rung 4 is `BLOCKED` (no solve). The count drives
§7.

---

## 2. SUBSTRATE — every path is on this box, read-only

### 2.1 Reference data (read-only, never modified)

    /home/ubuntu/closure-challenge-benchmark/data/DUCT/AR_1_Ret_360   (primary)
    /home/ubuntu/closure-challenge-benchmark/data/DUCT/AR_1_Ret_180   (secondary Re, available)

A quarter square duct: `h = 1 mm`, `AR = 1`, `Re_b = 5693`, `Re_tau = 341.9805`,
`nu = 1.5e-5 m²/s` (`caseDef`, read this session). `U_bulk = Re_b·nu/h =
85.395 m/s` — the lab's own convention, identical to G2's `Ubar` (G2 §2.4).

Each `0/` carries `U_LES` (nonuniform `List<vector>`, **3025 entries** = the fine
55² mesh, verified this session: header `U_LES nonuniform List<vector>` then `3025`,
no `boundaryField`), whose vector components 2 and 3 are the **in-plane secondary
velocities `V`, `W`** — the load-bearing quantity, confirmed non-zero; plus
`tauij_LES` (full LES Reynolds-stress `symmTensor`), and RANS `U k nut omega p`.

> **THE DNS/LES GROUND TRUTH EXISTS ONLY ON THE FINE 3025-CELL (55²) MESH** — and
> **that mesh is NOT any of the G2 levels** (32²/64²/128²; §2.2). This is a
> load-bearing methodological fact, handled explicitly in §4.3 and flagged for the
> supervisor: the model-vs-DNS comparison must define a mesh mapping, and the clean
> route (Roache-extrapolate the model's fine value, compare the **scalar** to DNS)
> is registered there.

### 2.2 The grid triple — G2's, REUSED

G2's triple builds into `/home/ubuntu/closure-data/g2/{L1,L2,L3}` via
`cases/RANS_LES_closure_models/G2_grid_triple_duct/build_g2.py`:

| level | `N` per cross-plane direction | cells | ratio `r` |
|---|---|---|---|
| L1 | 32 | 1,024 | — |
| L2 | 64 | 4,096 | 2.0000 |
| L3 | 128 | 16,384 | 2.0000 |

`D_SPATIAL = 2`, `r = 2` exactly at both steps, `Fs = 1.25` — all as G2 §3
registers and its comparator hard-codes. **LR1 does not re-derive the mesh
family**; it inherits it under FREEZE PRECONDITION (a). The geometry is identical
for every model (a mesh knows nothing of the turbulence model), so reusing the
triple is exact; the **iteration budgets** are the open question (§3.3).

### 2.3 Everything the solves inherit from G2, and the ONE thing that changes

Every case-setup element G2 §2.4 fixed is inherited unchanged — `meanVelocityForce`
`meanVelocity1` with `Ubar = (Re_b·nu/h,0,0)`, wall-resolved
`nutLowReWallFunction`/`omegaWallFunction`, `bounded Gauss linearUpwind`
convection, `Gauss linear corrected` laplacians, `residualControl` emptied (rule 4),
`writePrecision 12`. **The one thing that changes per case is
`constant/turbulenceProperties` — the `RASModel` entry (and, for `kOmegaSSTQCR`, the
`kOmegaSSTQCRCoeffs { Ccr1 0.3; }` block and the `libs` line naming
`libkOmegaSSTQCRTurbulenceModels.so`).** The RSMs additionally need their own
initial/boundary fields for the stress tensor `R` and, for `LRR`/`SSG`, an
`epsilon` field rather than `omega` — this is a per-model staging requirement the
build script must satisfy, registered here as a known divergence from G2's
five-field stage (§6.2).

---

## 3. FUNCTIONALS AND METRICS

### 3.1 PRIMARY — the QUALITATIVE / BINARY certified claim

**Does the model produce secondary flow of the second kind — the corner-directed
in-plane field — where SST-linear produces none?** This is Sanaa's "recovers where
SST could not" and, per `INGEST_PLAN.md` §1 reason 1, it is a **binary,
demonstrable claim that needs no band to interpret**.

* **Metric M-bin:** peak in-plane secondary-velocity magnitude
  `|U_sec|_max / U_bulk`, with `|U_sec| = sqrt(V² + W²)` per cell, and the
  **corner-vortex count / topology** (the 8-vortex, two-per-corner pattern of a
  symmetric quarter duct).
* **Registered prediction:** linear EVMs (`kOmegaSST`, `realizableKE`, `kEpsilon`)
  give `|U_sec|_max/U_bulk` **below a small floor**; nonlinear EVMs, RSMs and QCR
  give a **non-zero, corner-directed field**.
* **DRAFT floor: `1e-3` (0.1 % of `U_bulk`).** `PENDING-FREEZE.` Basis: it sits
  ~20× below the measured DNS peak (0.0205, §3.2) and far above the machine-noise
  in-plane field a linear model produces on this case (G2 §4.0 measured `Uy,Uz` at
  noise; `BASELINES.md` §4 measures the linear-model in-plane velocity at `4e-16`
  of bulk). A floor here cleanly separates the two classes.

### 3.2 QUANTITATIVE acceptance vs DNS

`|U_sec|_max/U_bulk` (and the secondary-velocity profile along the corner
bisector, §4.3; and, if tractable, wall `Cf`) compared to the DNS `U_LES`.

> **THE DNS VALUE, EXTRACTED THIS SESSION SO THE DRAFT BAND IS REAL** (not a
> placeholder). From `AR_1_Ret_360/0/U_LES`, over all 3025 cells:
>
>     |U_sec|_max            = 1.7514638 m/s        (max over cells of sqrt(V²+W²))
>     U_bulk = Re_b·nu/h     = 85.395  m/s
>     |U_sec|_max / U_bulk   = 0.020510   (2.05 % of bulk)
>
> Artifact: `/home/ubuntu/closure-challenge-benchmark/data/DUCT/AR_1_Ret_360/0/U_LES`.
> Also measured there: max `|V| = 1.7354`, max `|W| = 1.7503`, max `|Ux| = 108.97`.

* **DRAFT acceptance band on `|U_sec|_max/U_bulk`: `[0.0123, 0.0287]`**, i.e.
  DNS `0.0205 ± 40 % relative`. `PENDING-FREEZE` — the width is a placeholder for
  the supervisor to set against the model spread and the shelf-D band, **not a
  measurement**. The band is registered against the **lab's DNS value 0.0205**, and
  it is against DNS, never against zero (§0.1).

> **RECONCILIATION FLAG FOR THE SUPERVISOR (a disagreement I found on disk).**
> `_common/BASELINES.md` §4 cites the DNS in-plane velocity as **"1.5 %"**, while
> my direct extraction of the **peak** gives **2.05 %**. These are almost certainly
> **different statistics** (a mean / bulk-secondary figure vs the peak
> `|U_sec|_max`), not a contradiction — but the band must be frozen against **one
> defined statistic**, and this record uses the **directly-measured peak with its
> artifact**. The supervisor should reconcile the two definitions at freeze.

### 3.3 Roache triple gating applies to the QUANTITATIVE metric (rule 5)

`|U_sec|_max/U_bulk` is graded on the G2 triple L1/L2/L3 **per model**, and
**standing rule 5 governs it in full**:

1. any level not iteratively converged or not plateaued → that model is
   **`NOT A RESULT`**, whatever its value;
2. a triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` → **`NOT A RESULT`**,
   value and both triples/orders printed beside it;
3. only a **`CONVERGING`** triple reaches the band; `PASS` inside the band else
   `GATE FAIL`; **GCI at `Fs = 1.25`**, printed; **never a GCI quoted on a
   non-monotone triple.** The gate can only turn a PASS/GATE FAIL **into**
   `NOT A RESULT`, never the reverse.

> **A CONVERGENCE RISK REGISTERED IN ADVANCE, NOT DISCOVERED LATER.** G2's
> iteration budgets (`endTime` 20k/30k/40k) were calibrated for **`kOmegaSST`**
> convergence. RSMs (`LRR`, `SSG`) and the nonlinear EVMs are stiffer and may not
> reach the IC gates at those budgets. This rung registers the **same fixed
> `endTime` per level for every model** and lets the IC gates rule a
> non-converging model **`NOT A RESULT`** — an **honest per-model outcome, not a
> rung failure**. Lengthening `endTime` after seeing a model did not converge is
> tuning against the answer (rule 2) and is a **separate, separately
> pre-registered rung**, never a re-run under this document.

### 3.4 A-posteriori is MANDATORY, and it is so by construction (charter §2)

This rung **re-solves** each model and **compares velocity fields** to DNS. It is
a-posteriori by construction; no a-priori stress-tensor scoring is performed here.
Stated so the reader is not left to infer it.

---

## 4. THE MODEL-FORM BAND, AND THE MESH MAPPING

### 4.1 SHELF-D MODEL-FORM BAND — REPORTED, NEVER APPLIED (charter §22.4)

Every reported prediction **ships the shelf-D eigenspace model-form band**
(`_common/uq_eigenspace/UQ_EIGENSPACE.md`; charter §22.4). It is **reported, never
applied to the prediction, never subtracted from the model-vs-DNS error**
(§22.4.2).

* **The axis the band cannot see, named (§22.4.1 / §22.4 requirement 1).** The
  shelf-D band perturbs **shape and orientation only** — Emory's eq. (4)/(7) keep
  `k` **outside the bracket** — so `k`-magnitude, and with it the momentum forcing,
  is **outside the envelope by construction**. Measured cost of that gap, quoted
  where the band is quoted: production containment **0.9279 to 0.9433**
  (`UQ_EIGENSPACE.md` §7 P-A2).
* **THE SHARED BLIND SPOT, stated per §22.4.2.** `kOmegaSSTQCR` is **traceless**
  (`b_qcr2000_spalart2000.md` `band_interaction: does_not`; derived: `O_ik
  taubar_ik = 0` for antisymmetric `O` and symmetric `taubar`), so **QCR also
  leaves `k` unchanged**. QCR and the shelf-D band are **both blind to
  `k`-magnitude.** Where they are shown together, the overlap in what **neither**
  can see — `k`-magnitude and its momentum forcing — is stated explicitly.
* **THE BAND IS REPORTED WITH ITS WIDTH AGAINST THE SIGNAL (§22.4.3, the P-A4
  worked example).** The secondary-velocity signal is small (~2 % of bulk). A band
  many times the signal is **itself `NOT A RESULT` for the band**, exactly as P-A4
  records a velocity coverage inside a 1,344× envelope as `NOT A RESULT` — *it is
  the width, not the coverage, that says so.* **REGISTERED EXPECTATION, and it is a
  live risk, not a formality:** the **duct-calibrated `delta_B` is 0.95–0.98**
  (`UQ_EIGENSPACE.md` §7: `AR_1_Ret_180` median 0.981, `AR_3_Ret_180` median
  0.954), i.e. **nearly the whole barycentric triangle** — because a linear model
  in a duct sits *near the wrong vertex* and only a near-total move contains the
  truth. A band that wide, mapped to a velocity band, may well be **`NOT A RESULT`
  for the band** by its own width criterion against a 2 %-of-bulk signal. That
  outcome is registered here in advance as the **expected** one; it does **not**
  change the primary binary verdict.
* **Use the DUCT-calibrated `delta_B`, NOT Emory's O(0.5) (§22.4.4, L-219).** The
  duct value 0.95–0.98 is measured in `UQ_EIGENSPACE.md` §7; Emory's O(0.5) is
  calibrated on flows where the model is qualitatively right and **understates**
  the duct.

### 4.2 The band never becomes a correction

Per §22.4 requirement 2: the band is **not** applied as a field correction, is
**not** subtracted from any model-vs-DNS error, and appears in **no** verdict
mapping in §5. It is a reported channel beside the prediction.

### 4.3 THE MESH MAPPING — DNS on 55², models on 32²/64²/128²

The DNS lives on the 3025-cell (55²) mesh, which is **not** any G2 level. The
comparison is therefore defined as:

1. **Scalar `|U_sec|_max/U_bulk` (the primary quantitative metric):** graded by
   **Roache on the model's own triple** (L1/L2/L3) to obtain the grid-converged
   extrapolated fine value `f_ext` (only when `CONVERGING`, §3.3), and **that
   single extrapolated scalar** is compared to the DNS `0.0205`. This route needs
   **no interpolation** between the model mesh and the DNS mesh — the max is a
   field scalar and the extrapolation removes the residual grid dependence. It is
   the clean, registered route.
2. **The corner-bisector profile (and any `Cf` distribution):** these are
   pointwise and **do** require a mapping. Registered: the model field is
   interpolated **onto the DNS sample points** (not the reverse — the DNS is the
   reference and is left untouched), by the comparator, with the interpolation
   scheme named in the frozen grade instrument. **If the profile comparison proves
   intractable within the cost cap it is reported `PENDING`, not forced** — the
   binary (§3.1) and the scalar (route 1) carry the certified claim on their own.

---

## 5. GATE, THRESHOLD, CAP, LABEL

### 5.1 Ordering (standing rule 5), not negotiable

1. Any level not complete (§6.3) or not iteratively converged (§6.4) → that model
   is **`NOT A RESULT`**, whatever any number says.
2. A triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` → **`NOT A RESULT`**,
   value and `R` printed beside it.
3. Only a `CONVERGING` triple reaches a band. The gate can turn a `PASS` or
   `GATE FAIL` **into** `NOT A RESULT`, never the reverse.

### 5.2 Verdict mapping (per model), in rule-1 vocabulary only

| condition | verdict |
|---|---|
| M-bin `|U_sec|_max/U_bulk` below the floor **and** no corner topology | **linear-null CONFIRMED** — reported as `PASS` of the *baseline prediction* for `kOmegaSST`/linear controls (the SST-could-not baseline holds) |
| M-bin above the floor **with** corner topology, quantitative triple `CONVERGING` **and** `f_ext` inside the DNS band | **`PASS`** — "recovers where SST-linear could not," quantitatively within band |
| M-bin above the floor with topology, triple `CONVERGING`, `f_ext` outside the DNS band | **`GATE FAIL`** — recovers qualitatively, misses the DNS band |
| triple not `CONVERGING` | **`NOT A RESULT`** (value + triple + orders printed) |
| rung 4 (GP) | **`BLOCKED`** (capability-absent) |

**The certified headline** is the **binary primary** (§3.1): *which models recover
the corner physics and which do not.* The quantitative band and the shelf-D band
are reported beside each recovering model and **never overturn the binary** except
via rule 5's one-way NOT-A-RESULT gate. Vocabulary is
`PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and the grade
instrument must pass every verdict through a checker that **refuses** on a synonym,
hedge or lower-case variant before printing (as `grade_g2.py` does).

### 5.3 The registered falsifier (charter §12)

LR1's **central prediction** is falsified if **`kOmegaSSTQCR` fails to produce a
corner-directed secondary field** (M-bin below the floor, or no corner topology) on
a `CONVERGING`, completed triple — i.e. QCR does **not** recover what SST-linear
could not, in this lab's hands. That is a `GATE FAIL` on the rung-3 claim and a
**publishable finding about SST+QCR on the duct**, not a failure of the rung. The
**parallel** falsifier registered in §1.1: if a **stock** nonlinear EVM/RSM
recovers the duct at rung 1, the rung-3 novelty claim for QCR is withdrawn and
recovery is attributed to the stock model.

---

## 6. CONTROLS — each a standing rule, not a nicety

### 6.1 COMPARATOR PLANTED-ZERO CONTROL (standing rule 3) — SPECIFIED, not written

The a-posteriori secondary-velocity comparator **MUST**, before reading any real
field:

1. **Plant a known non-zero perturbation** into the in-plane velocity field it
   reads, **through the same OpenFOAM-ASCII data path the production reader
   consumes** — write a `U` field on disk with a corner cell's `(V,W)` set to a
   known value such that `|U_sec|_max` takes a **known planted value**, and read it
   back through the **production `read_Usec` function**;
2. **REFUSE (`sys.exit(2)`)** if the reader does not return the plant; **refuse** if
   the substitution changed no bytes;
3. run the **inverse** — the same reader on the unplanted field must **not** return
   the plant (else it is a constant, not a reader);
4. run the **blind control** — a reader that returns `0.0` for every cell against
   the same planted field must **fire** the refusal, so the zero the real reader
   gives on a genuine linear-model null is a **reading, not a blind spot** (this is
   the whole point of rule 3 on this rung: the linear models are *expected* to read
   near-zero, and that zero must be **planted-controlled** or it is not evidence —
   `docs/.../a-zero-needs-a-live-planted-control.md`).

Per L-332: the refusal is a `raise`/`sys.exit(2)`, **never an `assert`** (deleted
under `python3 -O`), and the instrument parses its own AST to refuse if any
`ast.Assert` node exists, the counter first shown able to count a planted assert.

> **NOT WRITTEN NOW — SPECIFIED.** This document does not write the comparator.
> The comparator is written and its planted-zero control **demonstrated able to
> fail**, then **diff-read by the supervisor personally** (SUPERVISION §3 check 1),
> as FREEZE PRECONDITION (b) in §8, before any belief.

### 6.2 STRICT COMPLETION + AGE GUARD (standing rule 4) — per (model × level)

Every clause of rule 4 applies to each of the 27 solves, split PHYSICS (refuse) vs
INFRASTRUCTURE (named, recorded, voids nothing — L-342), exactly as G2 §6.3:
`rc = 0`; an `End` line; **last time == `endTime`**; the model's fields present at
`endTime` (`U p k` plus `omega` **or** `epsilon` per model, `nut`, and — for RSMs —
the stress field `R`); `ExecutionTime` line count `== endTime` (HARD equality, no
tolerance); and **every field at `endTime` strictly newer than the case's own
`0/U`** — the **age guard**, with `0/U` touched **last** at launch. The build
script **refuses to stage into a level directory that already exists**, so no solve
starts in a tree that already holds an answer.

> **A per-model divergence from G2's stage, registered.** G2 stages five fields;
> LR1's RSM cases (`LRR`, `SSG`) additionally require the stress field `R` and an
> `epsilon` field, and the QCR case requires the `kOmegaSSTQCRCoeffs` block + its
> `libs` line. The build script's field set is therefore **per-model**, and the
> completion check's required-field list is **per-model** — this is named here so a
> later reader finds a decision, not drift.

### 6.3 ITERATIVE CONVERGENCE (per model × level)

Registered as G2 §6.4 for the shared channels (`Ux`, `k`, `omega`/`epsilon`
initial-residual thresholds), **plus a plateau on `|U_sec|_max` itself** over the
final 10 % of writes — the in-plane quantity is the signal here (unlike G2, where
it was noise for the SST case), so it **is** gated for the recovering models. For a
model whose `|U_sec|_max` sits at the linear-null floor, the plateau is trivially
satisfied and the binary reads "null." Thresholds are drafted `PENDING-FREEZE`
against G2's measured floors and are set **from measurement, not borrowed**.

### 6.4 REFINEMENT-FAMILY + RECONSTRUCTION CONTROLS — inherited from G2

The mesh triple is G2's, so G2's reconstruction control (§6.1) and
refinement-family control (§6.2 — byte-identical `vertices` across levels, distinct
`nCells` in ratio `1:4:16`, read from `owner`, compared by **bytes** never line
count) both stand and are **re-checked at LR1 grade time**. LR1 adds a
per-model check: the staged `constant/turbulenceProperties` differs across models
**only** in the `RASModel`/coeffs/`libs` lines, and is **byte-identical across the
three levels for a given model**.

---

## 7. COST — measured basis, box cannot read its own billing (rule 12)

**Per-solve basis: `4.5e-6` s per cell-iteration, serial, 1 rank** — G2's
registered rate (G2 §7), deliberately conservative and above both measured duct
calibration points (`3.57e-6`, `4.01e-6` s/cell-it on
`aposteriori/kaandorp/AR_1_Ret_{360,3}__NULL/log.run`). With `ranks = 1`,
core-minutes = wall-minutes.

A **2-equation** solve over the G2 triple (endTimes 20k/30k/40k) is G2's measured
solver subtotal: **59.9 core-min per model** (cell-iterations
`2.048e7 + 1.2288e8 + 6.5536e8 = 7.9872e8`, ×`4.5e-6` s = 3594 s).

**Per-model-class multipliers — ESTIMATES, `PENDING-FREEZE`**, applied because
model classes differ in cost per cell-iteration (equation count and constitutive
work):

| class | models | multiplier (est.) | basis | subtotal core-min |
|---|---|---|---|---|
| linear 2-eq | `kOmegaSST`, `realizableKE`, `kEpsilon` | ×1.0 | G2's basis is a linear 2-eq rate | 179.7 |
| nonlinear EVM | `ShihQuadraticKE`, `LienCubicKE`, `LienLeschziner` | ×1.3 | same 2 transport eqs, heavier constitutive term | 233.6 |
| SST+QCR | `kOmegaSSTQCR` | ×1.2 | SST + traceless correction ≈ the `kOmegaSSTCorrected` rate G2 measured as its basis | 71.9 |
| RSM | `LRR`, `SSG` | ×3.0 | ~7 transport eqs (6 stresses + length-scale) vs 2 | 359.4 |

**Solver subtotal (est.): 844.6 core-min.** Plus per-model overhead
(`blockMesh`+`checkMesh` reuse G2's staged meshes ≈ 0; `-postProcess`/grading
≈ 0.8 core-min × 9 ≈ 7 core-min).

**REGISTERED ESTIMATE (DRAFT, `PENDING-FREEZE`): ≈ 852 core-minutes ≈ 14.2
core-hours.** Derived: 14.2 core-h × $0.0513/core-h = **$0.73 — DERIVED at the
owner-stated rate, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5: the box cannot
read its own billing).

**REGISTERED CAP (DRAFT, `PENDING-FREEZE`): 1,500 core-minutes** (≈ 1.76× the
estimate; the runaway guard, not a target; the RSM multiplier is the least certain
term and the cap carries its risk). Derived: 25 core-h × $0.0513 = **$1.28 —
DERIVED, NOT MEASURED.**

**Both figures are far under $25**, so each individual solve (≤ ~$0.06) and the
aggregate ($0.73) sit inside the 2026-08-21 blanket and inside
`CLOSURE_MODELLING_CHARTER.md` §18's 487 pre-authorised core-hours. **A blanket is
not a per-item read** (rule 9); the cost is registered regardless. **An overrun
stops the run; it does not get a new budget** (rule 12) — the run script must
enforce a per-level `timeout` and a cumulative watch that refuses to start a solve
whose budget would breach the cap.

**Estimate-versus-actual calibration is owed at completion** (rule 12): each
solve records `wall_s.txt`, and at rung/case completion the team lands a row in
`docs/COST_CALIBRATION.md` — ratio actual/predicted, gap attributed to contention /
waste / misprediction (waste named separately, never absorbed into the ratio), the
**per-model-class multipliers above turned from estimates into measurements** for
the next pre-registration. **A completion report without it is incomplete.**

---

## 8. FREEZE PRECONDITIONS (all must hold before the supervisor freezes)

This rung is **SEQUENCED** (Sanaa sequenced closure solves behind M6/CRM's first
rungs and the F6 separated-flow cases coming online; `docs/LAB_STATE.md` closure
section, 2026-09-07). It is drafted now as **authorised zero-compute F6 prep, NOT
launched.** The freeze may only occur when:

* **(a) G2 is frozen, run, and its SST `gradP` triple graded `CONVERGING`.** LR1's
  rung 2 (numerical cause) *is* G2; a non-`CONVERGING` G2 leaves the SST null
  unattributed and LR1 cannot claim model-form. G2 is presently
  `PENDING_SUPERVISOR_FREEZE`.
* **(b) The grade comparator is written, its planted-zero control (§6.1)
  demonstrated able to fail, and diff-read by the supervisor personally**
  (SUPERVISION §3 check 1) — a relayed check is not a check.
* **(c) All 27 target run directories are ABSENT** (rule 2 amendment condition —
  name them): `/home/ubuntu/closure-data/lr1/<model>/{L1,L2,L3}` for
  `<model> ∈ {kOmegaSST, realizableKE, kEpsilon, ShihQuadraticKE, LienCubicKE,
  LienLeschziner, LRR, SSG, kOmegaSSTQCR}`. The build script refuses if any exists.
* **(d) The reproduction-target choice — OPTION (ii), SST+QCR vs the lab DNS — is
  confirmed by the supervisor / Sanaa** (`b_qcr2000_spalart2000.md` records the
  choice as a Phase-2/registration decision, "neither is chosen here").
* **(e) The sequencing is lifted** — M6/CRM's first rungs and the F6 duct case are
  online, or Sanaa re-sequences. Until then this document is a **draft**, gates
  open, no compute.

---

## 9. QUEUE ENTRY — NOT DRAFTED, NOT FILED

**No `QUEUE_ENTRY_DRAFT.json` is created by this document.** The drop path
`verification/queue/closure/` is a **launch button, not a passive list** (D535,
L-348): a valid entry there is launched by the cron-restarted `queue_runner` within
~60 s. Because this rung is **sequenced and pre-freeze**, drafting a queue entry now
would be a loaded launch button. A queue entry is drafted **only after** the freeze
and only when the FREEZE PRECONDITIONS in §8 hold — and then it sits **beside the
frozen document in the case directory**, copied into the drop path by the
supervisor as a deliberate act.

---

## 10. PROVENANCE OF EVERY LOAD-BEARING FACT

| fact | source |
|---|---|
| Sanaa's model-form ladder directive | `etc/sessions/2026-09-04T1510Z_sanaa_model_form_closure_ladder.md` (authority `0910b664`) |
| "first ladder record," duct-first, "recovers where SST could not" | `docs/closure/correction_library/INGEST_PLAN.md` §1, §4 Phase 3 |
| reproduction-target OPTION (ii); NOT Spalart's config; SA-QCR absent; `Ccr1 0.3` untrained; traceless | `docs/closure/correction_library/entries/b_qcr2000_spalart2000.md` |
| grid triple, reuse, `D=2`, `r=2`, `Fs=1.25`; SST duct in-plane at noise | `cases/RANS_LES_closure_models/G2_grid_triple_duct/PREREGISTRATION.md` §3, §4.0 |
| DNS `|U_sec|_max/U_bulk = 0.0205` | `/home/ubuntu/closure-challenge-benchmark/data/DUCT/AR_1_Ret_360/0/U_LES` (extracted this session) |
| `U_bulk`, `Re_b`, `nu`, `h` | `.../AR_1_Ret_360/caseDef` |
| duct-calibrated `delta_B` 0.95–0.98; band width / P-A4; k-blind gap | `cases/RANS_LES_closure_models/_common/uq_eigenspace/UQ_EIGENSPACE.md` §5, §7; charter §22.4 |
| linear-model in-plane at `4e-16`; DNS "1.5%" reconciliation | `cases/RANS_LES_closure_models/_common/BASELINES.md` §4 |
| stock model symbols (`nm -DC`) | `.../openfoam2606/.../lib/libincompressibleTurbulenceModels.so` (supervisor) |
| `kOmegaSSTQCR` symbol resolves | `/home/ubuntu/OpenFOAM/ubuntu-v2606/.../lib/libkOmegaSSTQCRTurbulenceModels.so` (supervisor) |
| GP route capability-absent | `INGEST_PLAN.md` §1 |
| Shih 1995 / Craft-Launder-Suga 1996 not held (registration gap) | retrieval register, `INGEST_PLAN.md` §2, Sanaa's desk |

Every drafted number carries `PENDING-FREEZE` where it is a draft threshold, band,
floor, cap or multiplier. Nothing in this document is frozen until the supervisor's
freeze commit binds it by sha256.
