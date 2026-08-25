# MATRIX_CONTRIBUTION — the cfd family's rows for the lab coverage matrix

**What this file is.** The cfd line's offered rows for the lab coverage matrix the
**verification** team owns at `docs/COVERAGE_MATRIX.md`. That file is **not cfd's**.
This contribution **does not create, write to, edit or touch it**. The owner re-maps,
re-scores, merges or rejects any row here without asking.

Written 2026-08-25 by a cfd `lab-lane` at the cfd supervisor's direction. **ZERO
COMPUTE** — no solver, no mesh, no training. Every figure below is quoted from a
landed record or from a named artefact on disk; nothing was re-run. The one piece of
arithmetic this lane performed itself is §0.2, and it is arithmetic on numbers already
in a committed artefact, not a new measurement.

Verdict words are the fixed `CLAUDE.md` rule-1 vocabulary (`PASS` / `GATE REACHED` /
`GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`). Tier words are the matrix's five
(`HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` / `NEVER RUN`).

**Submissions are parked.** Nothing here is filed, sent, uploaded or registered
anywhere outside this box.

---

## 0. The rubric this file applied — the OWNER'S, not a fourth private one

### 0.1 cfd does not define its own V / G / P

`docs/COVERAGE_MATRIX.md` §2 records that closure, dafoam and heat-transfer each
defined V, G and P differently, and differently from the chief's rubric, so none of
their tiers could be transcribed. **cfd's contribution therefore uses the owner's
published rubric verbatim and defines nothing of its own.** From `COVERAGE_MATRIX.md`
§1:

| column | scores green ONLY when |
| --- | --- |
| **V** — code verification | there is an **exact solution**, a **manufactured solution**, or a **correlation**, and the case was compared against it |
| **G** — grid convergence | there is a **CONVERGING Roache triple**, with **GCI at Fs = 1.25** and an **observed order p** |
| **P** — validation | against a **public primary source**, with the **pre-registration ON DISK** |

**Every V-green cell below names WHICH of the three it is** — exact, manufactured, or
correlation — because "V" without that word is the cell that rots first.

The owner's three rulings (`COVERAGE_MATRIX.md` §2.2) are applied as written:

* **Ruling 1** — `GATE REACHED` when **at least one** of V / G / P is missing, and the
  row names **every** missing letter; `SURVEYED` is reserved for rows with **no
  pre-registered gate at all**.
* **Ruling 2** — an **unsettled** observed order still scores `G`, and every G-green row
  additionally discloses whether the order has settled, quoting the sequence if it is
  still moving. No row here is called asymptotic.
* **Ruling 3** — `P` is green only against a source the lab **HOLDS and can read**. A
  value reaching the lab through a third party is `SECONDARY` and does not score P.

If the owner's rubric moves, **the evidence clauses in each cell are the durable part**
and the letters should be recomputed from them.

### 0.2 A finding this lane owes the owner before the rows: the Eca–Hoekstra band IS the GCI at Fs = 1.25

`COVERAGE_MATRIX.md` §4 fact 1 leaves an open question that decides whether cfd can
score a G at all:

> *"The open question is whether an **Eca-Hoekstra certifier verdict is the same
> instrument as a Roache triple with a GCI at Fs = 1.25**; they are not obviously the
> same, and the answer decides the fact."*

**It is answerable from the artefact alone, and the answer is yes.** Take the flat
plate's finest triple straight out of `cases/tmr/flatplate_sst.json`
(`convergence_extended.cd_triples[2]`), and solve the certifier's own band back for its
safety factor:

* Cd triple `0.0028342538677 / 0.0028564381699 / 0.0028635838023`, r = 2, certifier
  `observed_order` **1.6344055714456223**, certifier `reportable_band_abs`
  **4.244064059104043e-06**.
* `Fs = band × (r^p − 1) / |f_med − f_fine|` = **1.2500000000**.
* Independently on Cf(x = 0.970084): p **1.528107096548118**, band
  **5.084493331132672e-06** → `Fs` = **1.2500000000**.
* And `band / f_fine` reproduces the file's own `gci_fine_pct` to eight figures:
  **0.14820813 %** against the recorded `0.14820813191132226`, **0.18799768 %** against
  the recorded `0.18799768435862288`.

The code agrees with the arithmetic: `sdk/chief_engineer/uq.py:588` is
`band = fs * abs(e21) / (r21 ** p_used - 1.0)` inside `eca_hoekstra_band`, whose
signature (`:448`) defaults `fs: float = 1.25`; the sibling `ladder_band` writes the
same formula literally at `:298` and labels it *"GCI band, Fs = 1.25"*.

**So the certifier's "reportable band" is Roache's GCI at Fs = 1.25, computed on the
fine mesh, with an observed order.** It is the same instrument under a different name —
a naming convention the module documents at `:456` (*"GCI stays internal; the Eca and
Hoekstra citation is the allowed name"*).

**What this does NOT settle**, and the owner should not read it as settled:

1. **It is not the lab's Roache instrument.** `scripts/roache_triple.py` (blob
   `8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`, commit `9c69a79a`) is the ported T-family
   arithmetic. The flat plate was graded by the SDK's certifier, **not** by that file,
   and no cfd ladder has been put through `roache_triple.py` yet. Two implementations
   agreeing on a formula is not the same as one ladder graded twice.
2. **Rule 5's clause (1) is a live question on this triple** — see Row 7. The owner, not
   this lane, rules on it.

---

## 1. Scope — what "cfd territory" was enumerated, and what was not

Territory read as: `cases/` **except** `RANS_LES_closure_models/` and `dafoam/`;
`verification/runs/` **except** `T-family/`, `F14-cooling-ladder/`, `THERMAL_K0_runs/`;
`verification/campaign/`; `models/`.

**Two deliberate exclusions, stated so the owner does not read a silence as a zero:**

* **`cases/ansys_verification/` and `verification/runs/ansys_verification/` are NOT
  scored here.** They are the ansys-verification team's territory under the current
  roster and that team files its own rows. Excluding them is a jurisdiction call, not a
  finding about their content.
* **`sdk/` is not cfd territory** and no `sdk/` row is offered. §0.2 cites `uq.py` as
  *evidence about an instrument*, which is a reading, not a claim on the file.

**The filing hazard that shapes this survey, recorded because it will mislead the next
reader too:** the verdicts live in `verification/campaign/*.md`, **one level up from the
run trees**. Most directories under `verification/runs/` carry no README, no RESULTS and
no marker file — `verification/runs/F12_runs/` holds a `reference/` directory and
nothing else, `verification/runs/MESH_AUDIT_runs/` holds only `log.checkMesh` files.
**An empty run directory here is not evidence that a family is ungraded.** Separately,
`grep` in this environment is a shell function wrapping `ugrep --ignore-files`, so
gitignored trees (`cases/mega-batch/work/`, 1,244 files) are invisible to a grep sweep;
disk checks below used `/usr/bin/grep`, `find` and `ls`.

---

## 2. The nineteen rows

Each row prints the **gate VERDICT** (rule-1 vocabulary, quoted from the record) and the
**matrix TIER** as separate cells, per `COVERAGE_MATRIX.md` §1.1.

---

### Row 1 — F3, supersonic inviscid exact-theory suite (wedge / cone / diamond)

| field | value |
|---|---|
| **V** | **GREEN — EXACT SOLUTION.** θ-β-M oblique-shock relations, a from-scratch Taylor–Maccoll ODE shooting integrator, the Prandtl–Meyer function and shock-expansion wave drag, all computed in `verification/runs/F3_runs/exact_theory.py` **before any CFD ran**, and each verified against an independent published value first: the NASA GRC wedge validation page reproduced on **all five** quantities to 6 significant figures; PM(M=2) = 26.3798° with the inverse round-trip to 1e-13. The solver was run **inviscid (μ = 0)** precisely so it solves the same Euler equations the theory assumes. |
| **G** | **NO.** Three levels exist per case (wedge 1,800 / 7,200 / 28,800 cells at r = 2) but **no Roache triple, no GCI and no observed order is computed anywhere in the family** — the strings `observed_order`, `gci*` and `richardson` appear **zero times** in `verification/campaign/F3_supersonic_exact_theory.json`. |
| **P** | **NO.** Exact theory is not the world, and the landed record carries **no pre-registration**. |
| **Verdict** | **PASS** on five gates across 17 `rhoCentralFoam` runs, 38.45 core-min (`F3_supersonic_exact_theory.md`, 2026-07-28, repo @ `ce534b3`): wedge p2/p1 0.01–0.07 %, wedge β, cone pc/p1 0.19–0.29 %, cone β 2.1–3.9 %, diamond cd 0.18–0.26 %. |
| **Tier** | **SURVEYED** |
| **Why not higher** | Under `CLAUDE.md` rule 2 those PASSes are **results, not credentials**: no gate, threshold, cap or label was frozen before the solver started, so nothing proves the gates could not have been chosen to fit the answers. No pre-registered gate exists at all, which is Ruling 1's definition of `SURVEYED`. |
| **What moves it up** | **The instrument is already built and armed.** `verification/campaign/F3_CONVERSION_PREREGISTRATION.md` is **FROZEN at commit `2bf4915a`** and is **ARMED AND UNFIRED — zero compute.** Verified on disk by this lane: `verification/runs/F3_runs/conversion_2026-08-24/` holds `rerun_f3.py` and `grade_f3.py` and **nothing else** — no `runs/` subdirectory (the exact path the freeze condition names), no case directory, no `log.rhoCentralFoam`. Firing it converts this row from SURVEYED toward GATE REACHED missing G and P. Adding a Roache triple on the wedge — the cheapest case in the family — would then take G. |

---

### Row 2 — F4, hypersonic blunt body (2D cylinder, Mach 6–8)

| field | value |
|---|---|
| **V** | **GREEN — CORRELATION.** Billig (1967) shock-standoff correlation via Anderson, *Hypersonic and High-Temperature Gas Dynamics*, 2nd ed., Eq. 5.37, and the modified Newtonian surface-pressure law, Eqs. 3.15–3.19. The coefficient was **pulled from the primary textbook page image, not from recall**: an initial web search returned **4.76**; the printed value is **4.67**, and the record says so. |
| **G** | **NO.** Same as Row 1 — `observed_order`, `gci*` and `richardson` appear **zero times** in `F4_hypersonic_blunt_body.json`. |
| **P** | **NO.** A correlation is code verification, not validation; no pre-registration on the landed record. |
| **Verdict** | **GATE REACHED, both gates PASS**, 14.66 core-min: standoff **+0.7 % to +2.3 %**, Cp RMS **3.87–3.91 %** — *"with caveats stated plainly (M = 8 standoff not resolved above noise; standoff detector has a real resolution-dependent bias documented, not hidden)"* (`CAMPAIGN_STATUS.md`). |
| **Tier** | **SURVEYED** |
| **What moves it up** | Same conversion route as F3 — Sanaa's directive names F4 explicitly. A frozen pre-registration plus a three-rung standoff ladder would take the row to GATE REACHED missing P. **Note the caveat that must survive conversion:** the M = 8 standoff is not resolved above the detector's noise, so a re-run that does not fix the detector converts an unresolved number, not a result. |

---

### Row 3 — DMR, double Mach reflection (Woodward & Colella 1984)

| field | value |
|---|---|
| **V** | **GREEN — EXACT SOLUTION.** Gate V, incident-shock kinematics against exact theory: **PASS on both rungs** — res120 **+0.00338 (0.15 %)**, res60 **+0.00399 (0.17 %)**. |
| **G** | **NO.** Two rungs (Δ = 1/120 and 1/60). Two rungs are not a triple, and no GCI or observed order was computed. |
| **P** | **NO.** Woodward & Colella is a published **computational** benchmark, and the structure gates against it did not hold. |
| **Verdict** | Mixed, and both halves are on the record. **Gate V PASS ×2.** **Gate P1 FAIL as registered** — the double-Mach structure detector; *"the failure is the detector's geometry, recorded"*, and *"left standing as FAIL per guidelines 1.3"*. **Gate P2 split**: rung-to-rung clause **PASS** (\|χ_R1 − χ_R2\| = 0.87° ≤ 1.5°), within-rung intercept clause **FAIL as registered** at both rungs. |
| **Tier** | **GATE REACHED — missing G and P** |
| **Why this tier and not `NOT HELD`** | The registered FAILs are on a **detector-geometry** gate, not on the code-verification question this matrix's V column asks, and V passed on both rungs. **The owner may reasonably read the two registered FAILs as the row's headline and re-tier it `NOT HELD`; the evidence is the same either way and this cell is where the disagreement should be resolved.** |
| **Provenance** | Pre-registration `DMR_PREREGISTRATION.md` committed **`74797a57`** before any mesh existed. Both rungs Cartesian, max non-orthogonality 0, max skewness 6.0e-10 / 2.7e-13. |
| **What moves it up** | A third rung at Δ = 1/240 on the same generator makes a triple; the meshes are Cartesian and byte-deterministic, so the ladder is clean by construction. That would test G. P needs a quantity in Woodward & Colella that a detector can actually read — the current detector could not. |

---

### Row 4 — DPW8_V2, Joukowski airfoil against the analytic inviscid solution

| field | value |
|---|---|
| **V** | **GREEN — EXACT SOLUTION.** `joukowski_theory.py`'s `cylinder_cp(θ)` checked against the closed form **Cp = 1 − 4 sin²θ**: **max abs error 0.000e+00 (machine precision)**. The gate itself is exact-valued: a symmetric geometry at α = 0 has **CL = 0 exactly**, and the CFD returns \|CL\| = **8.26e-08** at L1 and **2.04e-06** at L3 — **PASS on both**. Two independent computational paths agree at **2.753e-17**. |
| **G** | **NO.** The refinement family **stops at L3**: L4 (the gate rung) is **INCOMPLETE and NOT GATED**, so there is no triple. |
| **P** | **NO.** No pre-registration for the gates; and the geometry parameter **ε = 0.1 is *"NOT independently confirmed from any DPW-8/HFCFDVW committee source found in this pass"*** — a documented deviation from the committee case, which is the case P would have to be against. |
| **Verdict** | **PASS** — theory implementation vs published closed form; **PASS** — zero-lift gate at L1 and L3. **L4 NOT GATED**, reported as incomplete rather than graded. |
| **Tier** | **SURVEYED** |
| **What moves it up** | Complete L4 under a frozen pre-registration and the row has a triple to test for G. **`DPW8_V2_L4_DIVERGENCE_DIAG_PREREGISTRATION.md` already exists** and its results are landed — that diagnostic is about *why* L4 diverged, not about the gate, so it does not gate this row. Confirming ε from a committee source is the separate, cheap step that unblocks P. |

---

### Row 5 — F9, pulsatile valve orifice against the Womersley solution

| field | value |
|---|---|
| **V** | **GREEN — EXACT SOLUTION** (Womersley 1955's analytic oscillatory pipe-flow profile). Gate 1 **PASS** at **−1.6 % / +0.2 %**. **VERIFY:** this lane did **not** locate a held copy of Womersley (1955) under `docs/papers/` and did **not** title-page verify one (rule 15). If the paper is not held, Ruling 3's logic may bear on V as well as P and the owner should re-score this cell. |
| **G** | **NO.** No grid ladder, no observed order, no GCI. |
| **P** | **NO.** No pre-registration document exists on disk for F9 in `verification/campaign/`. |
| **Verdict** | **GATE REACHED, mixed (2 PASS / 1 FAIL-with-cause-understood)**, < 35 core-min: Gate 1 **PASS**; Gate 2 **FAIL** at 20–414 %, cause identified; Gate 3 **−94.0 % vs the ROM**, described by the record as pre-registered though no pre-registration file is on disk. |
| **Tier** | **SURVEYED** |
| **What moves it up** | Obtain and hold Womersley (1955), title-page verified, which firms V. Then a frozen pre-registration and a three-rung ladder on the fixed-leaflet orifice. |

---

### Row 6 — F4-SIGFPE, steps 0 and 1 — the solver-forensics experiment

| field | value |
|---|---|
| **V** | **NO.** This is solver forensics on a floating-point exception, not a physics case; it compares against no exact solution, no manufactured solution and no correlation. |
| **G** | **NO.** No grid ladder. |
| **P** | **NO.** Nothing is compared against the world. |
| **Verdict** | Graded, `verification/campaign/F4_SIGFPE_STEP01_RESULTS.md`, commit **`5b5f5183`**, against `F4_SIGFPE_STEP01_PREREGISTRATION.md`. |
| **Tier** | **GATE REACHED — missing V, G and P** |
| **THE CONTINGENCY, and it is the row** | **The headline is contingent on a ruling that is Sanaa's and is `PENDING`.** Prereg §14.2 rules that §8 grades **event 1**; the record prints both readings side by side and states in its own words that **the elimination of mechanism #7 (prereg §9.1 row 2) "is CONTINGENT ON THE EVENT-1 READING. Under event 2 it is not licensed at all."** Under event 2, §8.1 returns `BASELINE-NOT-RECOVERED` and the discrimination question is **`NOT A RESULT` whatever Step 1 showed**. **The supervisor CONTESTS the audit's `NOT A RESULT` recommendation; the ruling is Sanaa's and is `PENDING`** (§C1.4). **This row must be read at its contingent value, not its optimistic one.** |
| **Measured, for the owner's context** | Event-1 `nLow` first differs at block 1, **max \|Δ\| = 18 cells (0.06 % of the mesh)**; event-2 `nLow` differs in **1,953** of the blocks. Cost close-out: predicted 9.316 core-min, actual **9.8560 core-min**, ratio **1.0580×**, plus **0.4468 core-min wasted** on two control twins running 299 `Time =` blocks where control C0 compares 200 — waste named separately, not absorbed. |
| **What moves it up** | Nothing cfd can do. **The tier cannot move until Sanaa rules on event 1 vs event 2.** A row like this is why the matrix prints verdict and tier separately. |

---

### Row 7 — TMR 2D zero-pressure-gradient flat plate — **the one G-green row in cfd territory**

| field | value |
|---|---|
| **V** | **NO.** The reference is CFL3D and FUN3D published values from NASA's Turbulence Modeling Resource — **code-to-code**, not an exact solution, not a manufactured solution, and no skin-friction correlation was compared against. |
| **G** | **GREEN.** Finest triple **137×97 + 273×193 + 545×385** (13,056 / 52,224 / 208,896 cells), r = 2 at every step. **CONVERGING**: Cd `0.0028342538677 → 0.0028564381699 → 0.0028635838023`, monotone, and increments shrink at **all four** ladder steps — 1.1248e-4, 5.3084e-5, 2.2184e-5, **7.1456e-6**. **Observed order** Cd **1.6344**, Cf(0.970084) **1.5281**, both inside (1, 2). **GCI at Fs = 1.25**, recovered from the artefact in §0.2 rather than assumed: **4.244e-6 = 0.14821 % of the value** on Cd, **5.085e-6 = 0.18800 %** on Cf. Artefact: `cases/tmr/flatplate_sst.json`, `convergence_extended`. |
| **G — order settled? (Ruling 2 disclosure)** | **NO — the order is still rising and the sequence is quoted as the ruling requires.** Cd **1.0833 → 1.2587 → 1.6344**; Cf **1.0315 → 1.1110 → 1.5281**. **This row is NOT asymptotic and nothing here may be read as saying so.** `VERIFICATION_CHARTER.md` §3.4 records two independent causes, neither a defect in the result: the grid family is not exactly self-similar (first-cell heights ratio 1.815, 1.905, 1.952, 1.976, approaching 2 from below), and **the reference codes drift the same way on NASA's own grids with NASA's own published values** — CFL3D 0.9468, 1.0611, 1.3383 and FUN3D 0.8172, 0.9784, 1.0703, **neither conclusive on any triple under the same certifier**. |
| **P** | **NO, on both halves.** **No pre-registration exists on disk for this ladder anywhere** — this lane searched every `*PREREGISTRATION*` in the tree and none names the flat plate. And four documented deviations break the same-model premise the comparison would need: incompressible `simpleFoam` analog of the M = 0.2 case; OpenFOAM `kOmegaSST` uses **strain** production where the TMR data is **SST-V** (vorticity production); the top boundary is an OpenFOAM freestream condition, not a Riemann farfield; grids match TMR cell counts and r = 2 with this module's **own blockMesh stretching, not the TMR point files**. |
| **Verdict** | The record's own: *"the first ladder in this corpus that the Eca–Hoekstra certifier declares CONCLUSIVE, on both functionals."* No rule-1 gate verdict exists, because no gate was ever registered. |
| **Tier** | **SURVEYED** |
| **The tier tension, named rather than papered over** | Under Ruling 1's reservation clause — *"SURVEYED is reserved for rows with no pre-registered gate at all"* — this row is `SURVEYED`, because no pre-registered gate exists. Read instead as a pure V/G/P count it is **GATE REACHED, missing V and P**. **The two readings disagree and the owner should settle it, because this is the row where they collide: it is the strongest G evidence in the family and the weakest pre-registration evidence.** The G cell is green under either reading, and the G cell is what this row is for. |
| **Two fragilities that must ride on the face of this cell** | **(1) Iterative convergence is on a force-plateau reading, not a residual reading.** The 273×193 rung ran to its **9,000-iteration cap** rather than tripping `residualControl`: 4 of 5 controls met, **Uy at 6.38e-08 misses its 1e-08 target by about 6×**; the record accepts it because Cd is flat to 2.16e-09 over the last 50 iterations. **Under `CLAUDE.md` rule 5 clause (1) — "any level not iteratively converged or not plateaued → NOT A RESULT" — a strict residual reading would void this triple.** The record defends the force reading with a drift-bound study: the verdict is `conclusive` at the low bound, the recorded value and the iterative asymptote alike (bands 4.231e-6 / 4.244e-6 / 4.231e-6). **This is the verification team's ruling to make, not cfd's.** **(2) The ladder inverts on a stopping rule.** The finest rung ran **36,000** SIMPLE iterations, not the 15,000 the module asks for. At the 15,000 cap Cd was 0.0028936144511, still falling by 1.04e-5 per thousand, and the extractor **refused it, correctly**. The record's own sentence: *"Accepting the 15000 value would have put Cd 3.00e-5 (1.05 %) high and turned the finest triple's increments from shrinking into growing, reporting the ladder as a divergence."* A counterfactual is stored beside it: at the 15,000 cap the observed order is **−0.7448**, `conclusive: false`, reason *"successive increments grow with refinement"*. |
| **What moves it up** | Two things, both cheap and neither speculative. **(a) V:** compare Cf against a published skin-friction correlation, which is a zero-solve post-process on fields already on disk. **(b) P:** freeze a pre-registration and re-grade, and — because the reference is code-to-code and the model is not the same model — state plainly whether the owner accepts a code-to-code reference as "the world" at all. **(c) Cross-grade the ladder through `scripts/roache_triple.py`** so the lab's own instrument, not only the SDK's, has certified it. |

---

### Row 8 — TMR bump-in-channel, including W1 on NASA's own grids

| field | value |
|---|---|
| **V** | **NO.** Code-to-code against CFL3D, as Row 7. |
| **G** | **NO, and the refusal is precise.** On **NASA's own bump grids** (89×41 / 177×81 / 353×161, exact point-drops at r = 2): Cd total observed order **4.037**, Cd pressure **3.200**, Cd viscous **1.246** — **`conclusive: no` on all three**, failing `order_window` = [0.5, 2.5] on the first two and `extrapolation_sanity` on the third. **No reportable band is issued.** The control that makes this a property of the case rather than of this lab: **CFL3D's own pressure ladder on those same grids fits to 2.913 and is refused by the same guard.** On the lab's own blockMesh bump family the pressure component has **no observed order at all** — its increments change sign at every matched iteration count (4G §10). |
| **P** | **NO.** No public primary experiment; the comparison is to CFL3D. |
| **Verdict** | Pre-registered **outcome 1 MET** — the item asked whether swapping only the mesh brings the pressure order back, and it does: increments become monotone (−7.250e-4, −7.886e-5) and the fit returns a finite order where there was none. **The grade is still NOT CONCLUSIVE**, and that was *"predicted and committed while the rung was still running"*. |
| **Tier** | **GATE REACHED — missing V, G and P** |
| **Provenance** | `W1_PREREGISTRATION.md` committed **`3e252b5c`** before any solve; grid byte-provenance at `models/tmr/bump/grids/PROVENANCE.md` (commit `1b5749f0`) — the fetched grids decompress **byte-identically** to NASA's distribution. |
| **What moves it up** | **G is not reachable on this grid family by adding rungs.** The record's own one-line result is *"the mesh was the problem, and the grids are not in the asymptotic range — two separate findings, the first ours and the second belonging to the grid family, which the reference code shares."* Moving G means a different grid family, not more of this one. **This row is the honest counterweight to Row 7 and should be read beside it.** |

---

### Row 9 — 3D grid ladders (Ahmed 25°, finite wings, B-52, cube)

| field | value |
|---|---|
| **V** | **NO.** No exact, manufactured or correlation reference on any of them. |
| **G** | **NO — and this is the cleanest measured negative in the contribution.** Three independent 3D single-knob families, each pre-registered before any solve, each refusing a converging triple. **Ahmed 25° (R4, prereg `6cdf8a41`)**: five rungs at refinement ratios 1.2200 / 1.2090 / 1.2128, Cd 0.084802 → 0.079360 → 0.073993 → 0.074882 — **non-monotone**; the fifth rung **c5 is refused as ladder evidence** because it never tripped `residualControl` and its final-window 2σ is **5.16e-03 = 6.26 % of its own value**, against a 5 % ceiling, and **6× the ladder increments themselves**. **NACA 0012 finite wing (W3, prereg `83e28569`)**: four rungs, observed order **24.048**, `clamped: true`, `conclusive: false`, **`uq.reportable_band` = None**, guard failing `order_window`. **NACA 4412 finite wing**: **`monotone: false`**, no observed order, `conclusive: false`, band None. **Not one 3D reportable band exists in cfd territory.** |
| **P** | **NO.** These pre-registrations grade **ladder arithmetic**, not agreement with an experiment. |
| **Verdict** | R4 gates G1 and G2 **MET**; the ladder question itself answered in the negative. W3: **P1 FALSE, P2 TRUE, P3 FALSE**, scored against the frozen text without editing it. The W3 record's own sentence: *"Removing the mixed step did not make the order sane; it made it worse."* |
| **Tier** | **NOT HELD** |
| **Why NOT HELD and not GATE REACHED** | Not "inconclusive", not "not yet". The class question — *does a 3D asymptotic ladder exist on this lab's meshes* — was **asked under three frozen pre-registrations and answered no, on measurement**. `W1_AHMED_LADDER_DISPOSITION.md` then ruled the 25° slant *"answered — in the negative, on measurement"* at **0 core-minutes**, and re-priced the remaining item from 240 to about 27 core-min. That is the matrix working. |
| **What moves it up** | A 3D grid family that is genuinely self-similar under one knob. Every family tried so far either changes recipe mid-ladder (`W3_LADDER_RECIPE_AUDIT.md`: two recipes with no knob moved twice) or is generated by a **nondeterministic** snappyHexMesh whose draw-to-draw scatter is comparable to the increments (`W3_MESH_NOISE_FLOOR_RESULTS.md`, `B52_RUNG6_REPLICATE_RESULTS.md`: D6 = 1.35994e-03 = **0.710×** the noise floor). **This is a meshing problem, not a solver problem, and it is the single highest-value unblocking item in cfd's territory.** |

---

### Row 10 — F2, transonic NACA0012 (2D)

| field | value |
|---|---|
| **V** | **NO.** The reference is a published inviscid AGARD shock position, used as a validation target, not an exact solution the code is verified against. |
| **G** | **NO.** |
| **P** | **NO.** No pre-registration. |
| **Verdict** | **PASS (banded, resolution-limited)** — shock at x/c = 0.556 against ~0.60, with the record stating in the same breath that the **detector resolution is ±0.052 x/c and the deviation is NOT RESOLVED**. A separate finding is recorded honestly against the auditor: the "misdescribed as RAE2822" defect **does not hold** — every record that names F2 names it a NACA0012, and the record says so rather than silently dropping the finding. |
| **Tier** | **SURVEYED** |
| **Adjacent, and not folded in** | `W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md`: the 3D NACA 0012 wing's **published credential does not survive its own mesh**. Different case, same family name — the owner should not merge them. |
| **What moves it up** | Sharpen the shock detector below the deviation it is being asked to resolve, then freeze a pre-registration. A PASS whose deviation is inside its own detector's resolution is a band, not a hit. |

---

### Row 11 — F12, RAE 2822, AGARD AR-138 Case 9

| field | value |
|---|---|
| **V** | **NO** — nothing has run. |
| **G** | **NO** — nothing has run. |
| **P** | **NO** — but **only one thing is missing, and it is the solve.** |
| **Verdict** | none — **`PENDING`** in the rule-1 display/queue sense. Not a softened `GATE FAIL`; nothing has been graded. |
| **Tier** | **NEVER RUN** |
| **Why this row is here and why it is the most actionable in the file** | **The pre-registration is on disk and frozen** (`F12_PREREGISTRATION.md`, *"Written 2026-07-30, before any solver was launched on this case"*), and it does the hard part properly: it solves **two** conditions because *"the published corrected conditions for this case do not agree and picking one silently is the classic way to be confidently wrong here"* — workshop M = 0.734 / α = 2.79° as the primary grade, tape M = 0.730 at one mesh level for sensitivity. **And the reference data is already on disk**: `verification/runs/F12_runs/reference/` holds `rae2822_case9_cp_upper.dat`, `rae2822_case9_cp_lower.dat`, `rae2822_coordinates.dat`, the NPARC geometry files and `decode_tape.py`. **AGARD AR-138 is a public primary experiment and the lab HOLDS the tape.** |
| **What moves it up** | **Run it.** This is the only row in cfd territory where a green P is one solve away: prereg frozen ✓, primary source held and readable ✓, grading path fixed ✓. Add a three-rung ladder in the same pre-registration and the row is a candidate for the lab's first non-thermal `HOLDS`. **VERIFY before launching:** `verification/runs/F12_runs/` currently holds only `reference/`, so the freeze condition (no run directory) still holds — re-check it in the same shell invocation as the launch. |

---

### Row 12 — F11, 2D lid-driven cavity (Ghia, Ghia & Shin 1982)

| field | value |
|---|---|
| **V** | **NO.** The lid-driven cavity has no exact solution and none was used; Ghia et al. is a **computational benchmark**, which the record itself is careful about — it carries a section headed *"A definition that has to be stated precisely: this is VERIFICATION, not VALIDATION."* |
| **G** | **NO, by the record's own disclosure.** Its grid section is headed *"Grid sensitivity, reported honestly (not claimed as clean Richardson convergence)"* — two mesh resolutions per rung, no triple, no GCI, no observed order. |
| **P** | **NO.** No pre-registration landed. |
| **Verdict** | **GATE REACHED, both rungs (Re = 100 and Re = 1000), both quantities, both mesh resolutions.** |
| **Tier** | **SURVEYED** |
| **COORDINATION — this row is IN PROGRESS and is not this lane's to close** | **A peer cfd lane is writing `verification/campaign/F11_CONVERSION_PREREGISTRATION.md` right now.** This lane did **not** write it, did **not** edit it, and confirmed at the time of writing that the file **does not yet exist on disk**. **The prereg is `PENDING` and this row should be re-scored by whoever lands it.** F11 is named in Sanaa's conversion directive alongside F3 and F4. |
| **What moves it up** | The conversion pre-registration in progress, plus a genuine three-rung ladder in place of the current two-resolution sensitivity check. Note that **P will still not be green**: Ghia et al. is a benchmark computation, so under the owner's rubric this case can reach GATE REACHED missing V and P, and no further, unless the owner rules a computational benchmark counts as a public primary source. **That ruling is worth having explicitly, because it decides several rows in this file.** |

---

### Row 13 — 2D separated turbulent flow (NASA hump, periodic hills, backward-facing step)

| field | value |
|---|---|
| **V** | **NO.** F6b's internally-named "Gate V" is a **mesh-reproduction identity** — our own mesh from the published ERCOFTAC hill polynomial reattaching at **x/h = 7.6472** against the benchmark's shipped-mesh **7.6439**, a difference of **0.043 %** against a pre-registered ±5 %. That is an excellent instrument check and it is **not** the chief's V: no exact solution, no manufactured solution, no correlation. **The vocabulary collision is exactly the one `COVERAGE_MATRIX.md` §2 warns about, and it appears inside a single record here.** |
| **G** | **NO.** Three rungs exist on the hill family but no converging triple with a GCI and an observed order is on record. |
| **P** | **GREEN, on one limb of a three-source band, and the limb is named.** Pre-registration `F6b_ERCOFTAC_PREREGISTRATION.md` committed **`31b0be16` before the first iteration ran**, registering the reference band **x_R/h ∈ [4.21, 4.70]** from three sources. **Held and readable:** Breuer, Peller, Rapp & Manhart (2009), *Computers & Fluids* **38**, 433–457 — `docs/papers/benchmark_test_cases/breuer_peller_rapp_manhart_caf2009_periodic_hills.pdf` **with its `.txt` sidecar**, supplying x_R/h = **4.69**. **NOT held:** Fröhlich et al. (2005) *JFM* **526** (reached through the NASA TMR page) and Rapp & Manhart (2011) *Exp. Fluids* **51** (reached through ERCOFTAC KBwiki) — under Ruling 3 both are **SECONDARY**, and **the experimental end of the band, 4.21, is the one that is secondary**. **VERIFY:** this lane did not title-page verify the held PDF (rule 15). |
| **Verdict** | **GATE REACHED (prediction falsified).** Reattachment **x/h = 7.6472** against the band **[4.21, 4.70]** — **+63 % to +82 %**. F6a NASA hump: separation **−1.59 %**, reattachment **+13.95 %**, `GATE REACHED`, ungated by any pre-registration. F5c backward-facing step against Driver & Seegmiller (1985), x_r/H = **6.26 ± 0.10**: **GATE NOT REACHED**, and its history is the sharpest self-correction in cfd's record. The 2026-07-29 reading of **0.5–1.5 H (a 4–12× miss)** was **withdrawn by the 2026-08-08 amendment as a `wallShearStress` sign-convention defect — "the 4–12× reattachment error never existed"** — corrected to **x_r/H ≈ 5.6 = −10.5 %**. Then `F5C_STAGE_A_RESULTS.md` (prereg `3734270d`) asked whether the −10.5 % regenerates from provable levers: **NOT REGENERATED** — A2 returns **6.996**, **1.396 H** from 5.6 against a pre-registered bar of **0.81 H** — firing pre-registered outcome **O3**, *"the ≈5.6 lives only in a committed docstring; if it does not come back from the configuration it is attributed to, the −10.5 % retracts to unmeasured."* And `F5C_LEVER_ISOLATION_RESULTS.md` (prereg `9eaefc7f`) then found the attribution **misattributed**: the **1.313 H** credited to SIMPLEC was **relaxation** — `\|Δx_r/H\|` 2.911 against a 6.560 bar for the algorithm alone (**NOT attributable**) versus **4.224** against a 2.578 bar for relaxation alone (**ATTRIBUTABLE**, 1.64× the bar). **F5c's headline number is currently `unmeasured`, by its own pre-registered rule.** |
| **Tier** | **NOT HELD** |
| **Why NOT HELD** | An honest FAIL on the validation quantity, under a pre-registration frozen before the first iteration, and it is **not** a convergence artefact: `F6b_RELAXATION_INVARIANCE_RESULTS.md` (pre-registered at `ce0b14be`) re-solved the medium rung at two further relaxation settings and got **7.6480** and **7.6458** against **7.6472** — agreement to **0.0105 %** and **0.0183 %** against a 0.5 % bar, which is convergence evidence that never consults a residual. **The +63 % to +66 % miss is the model's, not an untested switch.** That is a defensible scientific position, not a shortfall. |
| **What moves it up** | Nothing moves the P verdict — it is the linear-eddy-viscosity bubble-length deficiency, which is what closure exists to attack. **The tier moves when the model changes, not when the mesh does.** What cfd can do: obtain Rapp & Manhart (2011) so the **experimental** limb of the band is held rather than secondary, and add a converging triple for G. |

---

### Row 14 — Unsteady 2D cylinder, vortex shedding (F5a, R7)

| field | value |
|---|---|
| **V** | **NO — contested, and the reason is Ruling 3.** The Strouhal comparison is against a **correlation** (Roshko / Williamson), which would be V-green on its face, **but `VERIFICATION_CHARTER.md` §6b records F5a's reference as `NOT OBTAINED` as a primary — what is held is SECONDARY, reproduced as a figure in a 2014 thesis** — and the row is graded *BANDED and LOWER CONFIDENCE*. Ruling 3 is written about P; **this lane scores V as NO on the same logic rather than take the more favourable reading, and flags that the owner may rule the other way.** |
| **G** | **NO.** |
| **P** | **NO.** `SECONDARY` does not score P under Ruling 3, and the 2026-07-29 record carries no pre-registration. |
| **Verdict** | F5a: **PASS**, Strouhal within **0.7–4.6 %** across Re = 100–180. R7: pre-registered at `14eb8f11` and answered — *"the low rung is robust, and it is not close"* on the Strouhal gate's mesh sensitivity at Re 1000. |
| **Tier** | **GATE REACHED — missing V, G and P** (R7's frozen gate is what keeps this off `SURVEYED`) |
| **What moves it up** | Obtain Williamson's primary and hold it, title-page verified — that alone converts V and makes P reachable. The reference gap, not the physics, is what holds this row down, and it is the cheapest fix in the file after F12. |

---

### Row 15 — F5b, pitching NACA 0012 dynamic stall

| field | value |
|---|---|
| **V** | **NO.** |
| **G** | **NO.** |
| **P** | **NO.** The Gate rung is **`BLOCKED`** on a reference that is **`NOT OBTAINED`** — McAlister, Carr & McCroskey, NASA TP-1100 (1978), case (e). §6b's four fields travel with it. |
| **Verdict** | **`BLOCKED`.** The Physics rung's pre-registration is drafted and revised (Revision 2 at HEAD `e9737c5f`) but the **launch was denied by the permission system at ~17:45Z** and the record states plainly: *"launch BLOCKED on a permission decision that is Sanaa's alone."* |
| **Tier** | **NOT HELD** (a blocker, in the tier definition's own words) |
| **The honesty clause that must travel with this row** | **The wrapper assertions are UNEXERCISED.** The record says so itself at `:1143`: A1 (run-directory absence), A2 (E2–E5 porcelain and md5s) and A3 have **never been run**. **They are descriptions of committed code, not measurements**, and no reader may credit them as demonstrated. This is the planted-zero principle applied to a guard rather than a comparator: an assertion nobody has watched fail is not evidence. |
| **What moves it up** | Two independent unblocks, both reserved: **Sanaa's permission decision** for the launch, and **obtaining NASA TP-1100** for the Gate rung. Neither is cfd's to take. |

---

### Row 16 — F7, free-surface dam break (Martin & Moyce 1952)

| field | value |
|---|---|
| **V** | **NO.** |
| **G** | **NO.** |
| **P** | **NO.** `VERIFICATION_CHARTER.md` §6b adjudicates this row explicitly: no tabulated Martin & Moyce (1952) data could be located, and the lab **digitised a 2021 figure at 600 dpi** (arXiv:2108.08769 Fig. 7). Recorded as **`NOT OBTAINED` as a primary**. Under Ruling 3 that is `SECONDARY`. |
| **Verdict** | **GATE FAILED.** Front position Z(T): **+8.2 % mean / +11.0 % max** against a declared **5 %** tolerance — improved from the original **+13.6 % / +21.3 %** by the R1 audit of 2026-07-30, which also **retracted** the originally reported sign flip and root cause. **389.8 core-min.** Rungs F7b (Wigley hull) and F7c (workshop hull) are **`BLOCKED`** behind it. |
| **Tier** | **NOT HELD** |
| **A quality note the owner should see** | The digitisation was **programmatic** — axis-tick pixel clusters for calibration and cross-marker centroid detection, *"not manual eyeballing"* — with a stated digitisation uncertainty, and `F7a_REGATE_SPEC.md` (frozen 2026-08-11, zero compute) pins the measurement definition contractually so no future re-gate can drift it. **The reference is secondary, and the handling of a secondary reference here is exemplary.** Those are two different statements and the tier turns on the first. |
| **What moves it up** | Obtain Martin & Moyce (1952) as a primary. Until then the row cannot score P however well it solves, which is precisely the finding §6b exists to make visible. |

---

### Row 17 — F1, ONERA M6 transonic wing (3D)

| field | value |
|---|---|
| **V** | **NO.** |
| **G** | **NO.** See Row 9 — no 3D converging triple exists in this family. `MESH_AUDIT_runs/2026-08-08/` holds nine `log.checkMesh` files for the ONERA M6 meshes and nothing that grades a ladder. |
| **P** | **NO — and this row is the direct test of the lab's second standing fact.** The gate **is** against a public primary experiment: Cp distribution from **AGARD AR-138**. **There is no pre-registration on disk.** This lane enumerated every `*PREREGISTRATION*` file in cfd territory — **42 in `verification/campaign/` plus 2 under `verification/runs/` (`GEN_ALT_runs`, `FPE_DIAG_runs`) = 44** — and **not one registers a gate on F1 or ONERA M6.** Stated exactly, because a loose version of this claim is falsifiable: the string "ONERA" appears in exactly **one** of the 44, `F12_PREREGISTRATION.md:64`, and it is a **cost-basis cross-reference** (*"F1 (ONERA M6, 3D, 399k cells) was recorded GATE REACHED"*), not a gate. (A second hit, `W1_HUMP_A1_PREREGISTRATION.md:42`, is the word "exonerated".) |
| **Verdict** | **GATE REACHED**, 127.5 core-min: Cp RMS **0.049–0.114**, shock position within **±0.02–0.10 x/c**, CD = 0.02299556, CL = 0.31311589. Read as *"textbook signature of mesh-diffusion smearing on coarse grid (399,360 cells), not gross solver defect."* |
| **Tier** | **SURVEYED** |
| **THE STANDING FACT, tested rather than assumed** | `COVERAGE_MATRIX.md` §4 fact 2: *"No 3D PASS against experiment with a pre-registration on disk exists at all."* **Within cfd territory this lane could not refute it, and F1 is the closest candidate there is.** F1 has the experiment and lacks the pre-registration; F8 (Row 18) has a pre-registration and could not produce a gateable number; the Ahmed, wing, cube and B-52 pre-registrations all grade ladder arithmetic rather than agreement with an experiment. **cfd's contribution to that fact is: CONFIRMED for this territory, on an enumeration of all 44 pre-registration files, not on impression.** |
| **What moves it up** | Freeze a pre-registration and re-grade F1 against AGARD AR-138 — the reference and the mesh already exist, so this is a conversion, not a new campaign. **It is the shortest path in the whole lab to a first 3D P.** |

---

### Row 18 — F8, UAE Phase VI rotor, MRF (3D rotating machinery)

| field | value |
|---|---|
| **V** | **NO.** |
| **G** | **NO.** |
| **P** | **NO — not for want of a pre-registration, but for want of a number to grade.** The pre-registration was written 2026-08-07 **before the force history was read**, and it discloses honestly what the agent had already seen in context before writing. The reference is **Hand et al. (2001)**, 800 N·m at 7 m/s, flagged **secondary tier** in the record itself. |
| **Verdict** | **NO VERDICT — unconverged forces are not gateable; MRF branch closed.** 230,135 cells, run to t = 1500 and restarted to t = 3000, `SIMPLE solution converged` appearing **zero times in either log**. Torque band **7,679 N·m peak-to-peak = 960 % of the reference**, against a registered cap of 50 %. 5.8 core-min. |
| **Tier** | **NOT HELD** |
| **Why this is the right row and not a hidden one** | *"No verdict"* is the correct output and the branch was **closed** rather than left open to be quietly reopened by a later reader. A 960 %-of-reference band reported as a band, beside a 50 % cap, is what an honest instrument looks like when the answer is no. |
| **What moves it up** | The MRF formulation is the blocker, not the mesh and not the reference. Reopening means a different rotating-frame approach and a new pre-registration, and the record already says so. Hold Hand et al. (2001) as a primary at the same time. |

---

### Row 19 — Instrument and diagnostic campaigns (4G, GEN_ALT, MESH_AUDIT, MODEL_FORM, FPE_DIAG, D5_rsm)

| field | value |
|---|---|
| **V / G / P** | **NO, NO, NO — by construction, and the row exists to say so.** These campaigns diagnose the lab's own tools; they do not answer a physics question against a reference. **Scoring them V/G/P green would be the exact inflation this matrix is built to prevent.** |
| **Verdict** | Several are properly graded against frozen pre-declarations. **GEN_ALT: COMPLETE and GRADED, verdict `GENERATOR-OWNED`**, with the verdict rule *"committed before the answer existed"* (`GEN_ALT_runs/GEN_ALT_PREREGISTRATION.md`). **4G:** the *"insane mesh aspect ratio"* is diagnosed and **cleared as a solution defect in every case tested** — NASA's own TMR NACA0012 C-grids report max aspect ratio **20,650,841 / 26,446,227 / 29,899,837** and *"Failed 4 mesh checks"*, so the signature cannot by itself indicate a defect anywhere; the real defect underneath was convergence, and the `cd_tail_spread` metric certifying the ladder read **4.6e-8 against a real drift ~4000× larger**. **FPE_DIAG:** pre-registered before any probe ran, with zero-compute forensics executed first. **D5_rsm:** prediction committed at `45c0103` before any RSM run, then scored — linear models give secondary flow at **~6e-16 % of U_bulk** (machine zero) against DNS **2.2201 %**, SSG **55.01 %** of DNS, LRR **206.96 %**. |
| **Tier** | **GATE REACHED — missing V, G and P** |
| **Standing caveat that governs MODEL_FORM's bands** | The **lever-activity caveat** (charter v1.5 §9): for **32 of 36** cells the premise that members differ *only* in the closure is asserted from the runner's construction and is **NOT proven from artifacts** — stock `simpleFoam` echoes neither `fvSchemes` nor `fvSolution`. The closure lever itself is proven for all 36. **Positive control:** the 4 cells that carry the launcher echo prove the premise outright. The bands **stand with the caveat on their face**. |
| **What moves it up** | Nothing should. **These rows are correctly ungreen and the matrix is better for having them counted.** Their value to the lab is upstream of V/G/P. |

---

## 3. Census

### 3.1 Tier census

| tier | rows | which |
|---|---|---|
| **HOLDS** | **0** | — |
| **GATE REACHED** | **5** | Row 3 (DMR), Row 6 (F4-SIGFPE), Row 8 (bump / W1), Row 14 (cylinder shedding), Row 19 (instruments) |
| **SURVEYED** | **8** | Row 1 (F3), Row 2 (F4), Row 4 (DPW8_V2), Row 5 (F9), Row 7 (flat plate), Row 10 (F2), Row 12 (F11), Row 17 (F1) |
| **NOT HELD** | **5** | Row 9 (3D ladders), Row 13 (2D separated), Row 15 (F5b), Row 16 (F7), Row 18 (F8) |
| **NEVER RUN** | **1** | Row 11 (F12) |
| **total** | **19** | |

### 3.2 Column census — the two numbers the owner asked for

| column | green | which |
|---|---|---|
| **V** | **5 of 19** | Row 1 F3 (**exact**), Row 2 F4 (**correlation**), Row 3 DMR (**exact**), Row 4 DPW8_V2 (**exact**), Row 5 F9 (**exact**, with a VERIFY on whether the source is held) |
| **G** | **1 of 19** | Row 7, the TMR flat plate — and it is `SURVEYED`, because the family that earned the lab's best grid convergence never pre-registered it |
| **P** | **1 of 19** | Row 13, F6b periodic hills — green on the **held** Breuer 2009 limb of a three-source band, with the **experimental** limb secondary and a title-page check outstanding |

### 3.3 Reading the census down the columns

**cfd's strength is V and the other three families do not have it.** `COVERAGE_MATRIX.md`
§2 records that **none** of closure's, dafoam's or heat-transfer's V definitions is the
chief's V. cfd's five V-green rows are the chief's V, literally: closed-form gas
dynamics, a Taylor–Maccoll integrator, a conformal-map potential-flow solution, an
oscillatory-pipe-flow solution and a published shock-standoff correlation, each compared
against and each verified against an independent published value **before** the CFD was
trusted. **If the matrix has a V column at all, these are the rows that fill it.**

**cfd's weakness is pre-registration, and it is concentrated in exactly the rows that
would otherwise be strongest.** Eight rows are `SURVEYED` — every one of them because no
gate was frozen before the solver started, not because the work is thin. **Row 7 is the
sharpest case in the lab: the best grid convergence anywhere outside the thermal family
sits in a `SURVEYED` row, because the ladder that produced it was never pre-registered.**
Rule 2's price is paid here, visibly, and the conversion campaign Sanaa directed is the
repayment.

**One green P, and the shape of it matters more than the count.** Row 13's P is green on
the limb the lab **holds** and secondary on the limb that is the **experiment**. Three
further rows (F5a, F7, F5b) are held down by `NOT OBTAINED` references rather than by
physics. **Acquiring four papers would move more cells in this matrix than any solve
cfd could run**, which is a statement about where the lab's next hour goes.

---

## 4. What these rows cannot see

* **They cannot see a `HOLDS`.** Not one row in cfd territory has V, G and P green at
  once, and no row is one step from it. Row 11 (F12) is two: run it, and rule on whether
  a code-to-code or benchmark reference counts as "the world".
* **They cannot see 3D grid convergence.** Three pre-registered 3D families each refused
  a converging triple, and Row 9 is that finding, not that absence.
* **They cannot see 3D validation against experiment under a pre-registration.** cfd
  **confirms** `COVERAGE_MATRIX.md` §4 fact 2 for its own territory, on an enumeration
  of all 44 pre-registration files.
* **They cannot see whether the lab's own Roache instrument agrees.**
  `scripts/roache_triple.py` exists, passes 53/53 selftests, and **has graded no cfd
  ladder.** A tool existing is not a G earned, and §0.2's arithmetic identity between the
  two instruments' formulas is not the same as one ladder graded by both.
* **They cannot see iterative convergence on a residual reading for Row 7.** The one
  G-green triple rests on a force-plateau reading; a strict `CLAUDE.md` rule 5 clause (1)
  reading would void it. **That ruling is the verification team's.**
* **They cannot see the F4-SIGFPE headline at settled value.** Row 6 is contingent on a
  `PENDING` ruling that is Sanaa's.
* **They cannot see F5b's wrapper assertions working.** They are unexercised and are
  descriptions of code, not measurements.
* **They cannot see cost as money.** No dollar figure is quoted in this file. The box
  cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
* **They cannot see whether the tier words survive Sanaa's reading of the rubric.**
  `COVERAGE_MATRIX.md` §0 states the rubric is the chief's **reconstruction** of her
  directive, not her verbatim words. **If she reads it differently every tier here is
  re-derived from the same evidence clauses**, which is why each cell carries its
  evidence and not only its letter.
* **They cannot see anything cfd has not landed.** This is a survey of records at HEAD on
  2026-08-25. Where a cell says VERIFY, this lane did not verify it.

---

## 5. Items marked VERIFY

| item | row | why |
|---|---|---|
| Whether Womersley (1955) is **held** on this box and title-page verified | Row 5, V | This lane found no copy under `docs/papers/`. If it is not held, Ruling 3's logic may bear on V and the cell should be re-scored. |
| Title-page verification of `breuer_peller_rapp_manhart_caf2009_periodic_hills.pdf` | Row 13, P | The PDF and its `.txt` sidecar are on disk; **rule 15 forbids verifying a paper by filename or hash**, and this lane did not open the title page. The only green P in the file rests on it. |
| Whether the F12 run tree is still empty at launch time | Row 11 | `verification/runs/F12_runs/` held only `reference/` when this was written. The freeze condition must be re-checked **in the same shell invocation as the launch**, not inherited from this file. |

**Nothing else in this file is marked VERIFY.** Every other figure was read from the
record or artefact cited beside it.

---

## 6. Provenance, cost, and what this contribution does not do

**Written** 2026-08-25 by a cfd `lab-lane` under the cfd supervisor. **ZERO COMPUTE** —
no solver, no mesh, no MPI rank. **Estimate-versus-actual (rule 12):** predicted 0
core-minutes, actual **0 core-minutes**, ratio n/a, zero waste. **No
`docs/COST_CALIBRATION.md` row is due**, because no compute process completed; this is a
scoring and filing task and stating that plainly is the calibration honesty the rule
asks for.

**Sources read:** `CLAUDE.md` in full; `docs/charters/VERIFICATION_CHARTER.md`
§1, §2, §2a–§2e, §3.1, §3.2, §3.4, §6b, §9; `docs/charters/RESULT_PRIORITY_CHARTER.md`;
`docs/charters/FILING_CHARTER.md`; `docs/COVERAGE_MATRIX.md` §0–§2.2, §4 (the owner's
rubric and rulings, applied verbatim); closure's committed contribution read from the
blob at `a42fd634`, not from the worktree; the on-disk `cases/dafoam/MATRIX_CONTRIBUTION.md`
and `docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` **for structure only** — both are
untracked and may change, and **no number was lifted from either**; and each record and
artefact cited in the rows above.

**Two coordination facts, recorded so a peer is not stepped on:**

1. **`verification/campaign/F11_CONVERSION_PREREGISTRATION.md` is a peer lane's, in
   progress.** This lane did not write it, did not edit it, and Row 12 is marked
   accordingly.
2. **`cases/dafoam/MATRIX_CONTRIBUTION.md` and
   `docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` are UNCOMMITTED on disk.** They are
   their families' to commit. **This contribution commits nothing but itself.**

**This file creates, writes to and touches nothing in `docs/`.**
`docs/COVERAGE_MATRIX.md` is the verification team's, and it was **read and not modified**.
