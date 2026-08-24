# Thermal rows for the lab coverage matrix — a CONTRIBUTION
---

## SUPERVISOR'S BANNER — added 2026-08-24 at the first commit of this file. READ BEFORE LIFTING ANY ROW.

This file was written by a `lab-lane` that was **killed by a session usage limit
before it could commit**. It survived on disk, untracked, and is landed here
unchanged except for this banner, so that it cannot be lost a second time.
**Landing it is preservation, not endorsement.**

Two things a reader must know before lifting a single row.

### 1. THE ROWS ARE UNAUDITED

No supervisor has yet checked these rows against the records they cite. A
row-by-row audit is in progress and its corrections will land as a **dated
follow-up commit**, not as edits that hide the difference. Until that audit
lands, **treat every row as a claim awaiting verification.**

The governing constraint on this file, stated so the audit can be checked
against it: **no row may claim more than its verdict.** The thermal family is
the one place in this lab with CONVERGING Roache triples, which makes these
rows the coverage matrix's load-bearing ones and makes an overclaim here more
expensive than an overclaim anywhere else.

The specific traps the audit is checking, named here so they cannot be quietly
skipped:

- **T3's `G2` (`x_peak/H`) triple IS `CONVERGING`** — `p = 4.304`, GCI 0.0188 % —
  **and the row is still `NOT A RESULT`**, because gate (1) (iterative
  non-convergence) fires first under standing rule 5. A converging triple is
  necessary for a graded row and is not sufficient for one. Any row that reads
  T3's `G2` as a credit is claiming more than its verdict.
- **T1b returns `PASS` x4 against its frozen comparator while every triple is
  `DIVERGENT` or `STAGNANT`** (D440). There is **no mesh-converged value** in
  T1b until the L4 rung lands.
- **K0cG's `kOmegaSST` deviation/GCI ratios are 43x, 84x, 112x, 233x and 722x.**
  That is a *bounded discretisation error*, which is what makes the misses
  attributable. It is not a pass and must never be lifted as one.

### 2. THE V / G / P COLUMNS DO NOT MEAN THE SAME THING IN EVERY CONTRIBUTION FILE — DO NOT LIFT ACROSS FILES

`docs/COVERAGE_MATRIX.md` **does not exist**, at HEAD or on disk, as of this
commit. The schema it will use has therefore **never been fixed by its owner**,
the verification supervisor. In its absence three different meanings for the
same three letters are already in circulation, and one of them is already
committed:

| source | `V` means | `G` means | `P` means |
| --- | --- | --- | --- |
| **this file** (§0.1) | a **CONVERGING Roache triple with an observed order** | a **pre-registered gate with a threshold**, and its frozen verdict | the **reference is on disk and title-page verified** |
| `cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md` §lines 30-32, **committed at HEAD** (`a42fd634`) | a **verification instrument demonstrated able to fail** — planted zero, identity test, independent re-derivation | a **pre-registered numeric gate that could have failed**, frozen by sha before the run | a **pre-registered prediction, made before the run and graded** |
| the brief under which the consolidation week was described to this team | **code verification** — exact, manufactured or correlation | a **CONVERGING Roache triple + GCI + observed order** | **validation against a public primary with a pre-registration on disk** |

These are not three wordings of one scale. They are three different scales.
`V` in this file is approximately `G` in the brief; `P` in this file is
strictly weaker than `P` in the brief, which additionally requires a
pre-registration on disk; and `V` in the closure file has no counterpart in
either of the other two. **A matrix assembled by lifting rows out of all three
without re-keying them would be a measurement of nothing** — the same failure
class as D389, where a normalisation reads ~24x tighter than it is, moved up to
the level of the schema.

**Consequence, and it is binding on any lane reading this file:** no row here
may be lifted into `docs/COVERAGE_MATRIX.md` until the verification supervisor
fixes the schema and this file is re-keyed to it, in a dated amendment, by its
owning team. **This team does not re-key it unilaterally** — the schema is
verification's to fix and the divergence is cross-family, so it is escalated,
not decided here.

*Banner written by the heat-transfer supervisor, 2026-08-24. Zero compute.
Nothing below this line was altered.*

---


**This file is a contribution, not an assertion.** `docs/COVERAGE_MATRIX.md` is
owned and being built by the **verification supervisor**. Nothing here writes to
it, creates it or amends it. This file is written in the heat-transfer team's own
territory so that a verification lane can **lift rows straight out of it**.

Written 2026-08-24 by a heat-transfer `lab-lane`, at **zero compute**, against
HEAD `69d2f1ba`. Every sha below is a real `git log -1 --format=%h -- <path>`
lookup performed while writing, not a recollection.

**Verdict vocabulary is the fixed set** (CLAUDE.md rule 1): PASS / GATE REACHED /
GATE FAIL / NOT A RESULT / BLOCKED / PENDING. **Tier vocabulary is Sanaa's five
words, used with no synonyms**: HOLDS / GATE REACHED / SURVEYED / NOT HELD /
NEVER RUN.

**Where a summary and a record disagree, the RECORD wins and the disagreement is
reported** — §9 lists four such disagreements found while writing, three of them
against `docs/inventory/2026-08-24/LAB_INVENTORY.md` §6 (`529bfc08`) and one
against this lane's own brief.

---

## 0. How to read a row

### 0.1 The V / G / P columns

| column | question it answers | values used here |
| --- | --- | --- |
| **V** — verification | Is there a **converged Roache triple with an observed order** for this class? (code/solution verification) | `V YES` (CONVERGING triple, `p` quoted) / `V NO` (triple DIVERGENT, STAGNANT, OSCILLATORY or EXACT, or no ladder) / `V PARTIAL` (some rows converge, some do not) / `V NONE` (no solve) |
| **G** — gate | Is there a **pre-registered gate with a threshold**, and what did it return? | the frozen verdict, from the fixed vocabulary; `G NONE` where no gate was ever armed |
| **P** — primary | Is the experimental or analytical reference **ON DISK and title-page verified**? | `P PAPER-HELD` (a title-page-verified paper or primary data files on disk) / `P ANALYTIC-HELD` (closed form, no paper needed; the comparator re-derives it and refuses if it does not reproduce) / `P FORMULA` (a published correlation stated as an equation) / `P SECONDARY` (the value reaches the lab through a third party; the originating paper is **not** on disk) / `P NOT HELD` (named, sought, not obtained) / `P NONE` |

**`P` is never marked held for a paper that is not on disk.** `P SECONDARY` and
`P ANALYTIC-HELD` are deliberately distinct from `P PAPER-HELD` for exactly this
reason: K0c's headline PASS rests on de Vahl Davis reached **through Han and Xie
(2019) Table 3**, and de Vahl Davis 1983 itself is paywalled and was never read
(`K0c_RESULTS.md:50-51,71`).

### 0.2 The five tiers, defined so they are liftable

| tier | means |
| --- | --- |
| **HOLDS** | a pre-registered gate returned **PASS** on a **CONVERGING** triple against a reference the lab holds. The lab can make this claim and defend it. |
| **GATE REACHED** | the gate was evaluated and the row is **reported, not graded** — the deviation sits below a stated floor, so the comparison cannot discriminate. Not a PASS. |
| **SURVEYED** | the class has been **run and measured**, and nothing in it is a held claim about the world: capability rungs, solver-backed model-vs-model comparisons with no experimental reference, diagnosis arms, defect characterisations. |
| **NOT HELD** | the class was gated against a reference and the gate **did not close** — GATE FAIL, or NOT A RESULT under the binding triple gate. **The lab has evidence and the answer is no.** This is a scientific position, not an absence. |
| **NEVER RUN** | no solver has run in this class. |

**A cell can carry more than one tier at sub-class granularity.** Where it does,
§2 assigns the cell **the strongest held claim** and names the split; §3 carries
the sub-rows so a lane may lift either granularity. **The census in §8 is given
at both levels**, because the cell-level census flatters the record and the
sub-row census does not.

---

## 1. The cross

Rows are the cross of **{2D, axisymmetric, 3D}** with **{buoyant-thermal,
conjugate, radiation, forced-convection-internal, forced-convection-external,
mixed-convection}** — **18 cells, all of them present, including the empty
ones.** The empty ones are the most informative rows in the table and they are
not omitted.

*(The coincidence that the cross is 18 cells and §4.2 discusses an "18-combination"
finding is exactly that — a coincidence. They count different things and must not
be conflated.)*

---

## 2. The 18 cells

| # | dimension | class | V | G | P | tier | record path | sha |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | **2D** | buoyant-thermal | `V YES` — K0c triples CONVERGING, `p` 1.94–2.33 on the Richardson ladder | `PASS` — K0c gate, **0 of 20 graded rows failed**, largest deviation 1.139 % on a 3 % band | `P SECONDARY` — de Vahl Davis via Han and Xie (2019) Table 3; the 1983 original is paywalled and **was not read** | **HOLDS** *(laminar only — turbulent sub-class is **NOT HELD**, §3 S4/S5)* | `docs/campaigns/F14-cooling-ladder/K0c_RESULTS.md` | `8590c96a` |
| C2 | **2D** | conjugate | `V YES` — T9a R0 `p` 1.079, R2 `p` 0.952, both CONVERGING | `PASS` ×2 (R0 wall `q″`, R2 interface 2) | `P ANALYTIC-HELD` — closed-form composite wall; comparator refuses if the derivation does not reproduce | **HOLDS** *(pure solid conduction only — **fluid–solid CHT has NEVER RUN in any dimension**, §3 S11; hot interface **NOT HELD**, fin rows **GATE REACHED**)* | `docs/campaigns/T-family/T9a_RESULTS.md` | `0cbaea26` |
| C3 | **2D** | radiation | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** | — (all radiation work is 3D: C15) | — |
| C4 | **2D** | forced-convection-internal | `V PARTIAL` — T3 G2 `x_peak/H` **CONVERGING** (`p` 4.304, GCI 0.0188 %); G3/G4 STAGNANT | **`NOT A RESULT` 4 of 4**, at **gate (1) alone** of `T3_PREREGISTRATION.md` §7.1 | `P NOT HELD` — Vogel & Eaton 1985 **NOT OBTAINED** (ASME closed; every open archive checked and named in prereg §2) | **NOT HELD** | `docs/campaigns/T-family/T3_RESULTS.md` §14 | `2f1d6cb7` |
| C5 | **2D** | forced-convection-external | `V NONE` | `G NONE` — K0e is a **specification only**, zero compute, no solver launched | `P PAPER-HELD` — Bahrami 2005 NASA/TM-2005-212841 on disk, sha256 `0cd29adb…` | **NEVER RUN** *(and **BLOCKED by construction** if built as specified — no honest band from one correlation)* | `docs/campaigns/F14-cooling-ladder/K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md` | `4b336fad` |
| C6 | **2D** | mixed-convection | `V NO` — the module is **physically unsteady**; a steady triple is the wrong instrument | `G NONE` against any reference; the pilot's registered outcome mapping returned its **O1** branch | `P NONE` for the pilot; K2c-A's primary (Wibron 2018) **is** on disk but its rung is unrun | **SURVEYED** | `docs/campaigns/F14-cooling-ladder/K2b_PILOT_RESULTS.md` | `5c3fe5a8` |
| C7 | **axisymmetric** | buoyant-thermal | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** | — | — |
| C8 | **axisymmetric** | conjugate | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** | — | — |
| C9 | **axisymmetric** | radiation | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** | — | — |
| C10 | **axisymmetric** | forced-convection-internal | `V PARTIAL` — T1c L2 CONVERGING `p` 2.031, L0 `p` 1.854; **every T1b triple DIVERGENT or STAGNANT** | `PASS` ×3 (T1c L1, L2, L3); `GATE FAIL` ×1 (T1c L0); T1b returns **`PASS` ×4 by the frozen comparator and `NOT A RESULT` ×4 under the binding triple gate** | `P ANALYTIC-HELD` for T1c (`f·Re` = 64, 48/11, Graetz `λ₀²` = 7.313587 to 1.6e-08); `P FORMULA` for T1b (Dittus–Boelter / Gnielinski midpoint, band = their half-spread) | **HOLDS** *(T1c `f·Re` and constant-`q″` `Nu` only — constant-`Ts` `Nu` **NOT HELD**; turbulent pipe **NOT HELD**, and see §4.3, the tension row)* | `docs/campaigns/T-family/T1c_RESULTS.md` | `2f1d6cb7` |
| C11 | **axisymmetric** | forced-convection-external | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** | — | — |
| C12 | **axisymmetric** | mixed-convection | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** | — | — |
| C13 | **3D** | buoyant-thermal | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** *(every buoyant cavity this lab owns is 2D)* | — | — |
| C14 | **3D** | conjugate | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** *(T9c planned, unstarted; T5 would be the first fluid–solid CHT and its pre-registration is a draft)* | `docs/campaigns/T-family/T5_PREREGISTRATION_DRAFT.md` (unfrozen) | `a74b2f61` |
| C15 | **3D** | radiation | `V PARTIAL` — box B0/B2/B3 CONVERGING (`p` 0.954 / 0.853 / 0.825); **both sphere triples DIVERGENT** (`p` −3.253, −1.838) | `PASS` ×3 (box floor, x-walls, y-walls); `GATE FAIL` ×1 (ceiling); `NOT A RESULT` ×2 (spheres) | `P ANALYTIC-HELD` — closed-form surface-to-surface view factors and the two-surface network | **HOLDS** *(black box enclosure only — ceiling **NOT HELD**, grey spheres **NOT HELD**, **participating media NEVER RUN**)* | `docs/campaigns/T-family/T10a_RESULTS.md` | `31fd2268` |
| C16 | **3D** | forced-convection-internal | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** *(T3 is 2D by design — prereg §173: "Cases (8, all serial, all 2D)"; T1b/T1c are axisymmetric wedges)* | — | — |
| C17 | **3D** | forced-convection-external | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** | — | — |
| C18 | **3D** | mixed-convection | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** *(K2b 3D pre-registration exists and run directories exist; **no results** — PENDING, which is a queue state, not a tier)* | `docs/campaigns/F14-cooling-ladder/K2b_3D_UNSTEADINESS_PREREGISTRATION.md` | `5c3fe5a8` |

**Dimensionality was read from the meshes, not assumed.** T1b/T1c: `type wedge`
in `R_10k_x/constant/polyMesh/boundary:42` → axisymmetric. T3, T9a, E4a2, K0c
family, K2b pilot: `type empty` → 2D. T10a: 6-patch box and 2-patch sphere pair,
no `empty`, no `wedge` → 3D.

---

## 3. Sub-rows inside the occupied cells

The tier a cell carries in §2 is its **strongest held claim**. These are the
sub-classes underneath, and this is the granularity at which the family's honest
state is visible.

| id | cell | sub-class | V | G | P | tier | record path | sha |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | C1 | laminar differentially heated square cavity, Ra 1e3–1e6 | `V YES`, CONVERGING, `p` 1.94–2.33 | `PASS`, **0 of 20 graded** | `P SECONDARY` | **HOLDS** | `docs/campaigns/F14-cooling-ladder/K0c_RESULTS.md` | `8590c96a` |
| S2 | C1 | laminar buoyant capability rungs K0a / K0b | `V NO` — capability rungs, no Roache ladder claimed | `PASS` on their own capability gates; **"validated against no published reference datum"** in the record's own words | `P NONE` **by design** | **SURVEYED** | `verification/runs/THERMAL_K0_runs/README.md` | `a1fbe127` |
| S2b | C1 | K0b reproduction repair (V3 → W1–W4) | `V NO` | `PASS` ×4 (W1–W4); 39 of 39 graded quantities bit-identical, 48 of 48 Richardson leaves bit-identical | `P NONE` | **SURVEYED** | `docs/campaigns/F14-cooling-ladder/K0b_D406_REPAIR_RESULTS.md` | `f279aac5` |
| S3 | C1 | Boussinesq validity limit, K2e | `V NO` — a model-separation sweep, not a grid ladder | `G` thresholds pre-registered `0869284` before any K2e solver ran; velocity separates at ε ∈ (0.0333, 0.0500]; `Nu` last, 0.063 % at ε = 0.1, 1 % not until ε ∈ (0.30, 0.40] | `P NONE` — **SOLVER-BACKED, cannot reach VALIDATED**; the record says so on its face | **SURVEYED** | `docs/campaigns/F14-cooling-ladder/K2e_RESULTS.md` | `b845b603` |
| S3b | C1 | heat-balance instrument, KV1 | `V NO` | `PASS` — instrument validated with mutation tests, 0.93 core-min | `P NONE` | **SURVEYED** | `docs/campaigns/F14-cooling-ladder/KV1_RESULTS.md` | `65684e7c` |
| **S4** | C1 | **turbulent square cavity, Ra 1.58e9 (Ampofo)** | `V PARTIAL` — K0cG: **kOmegaSST all five CONVERGING**; **kEpsilon all five STAGNANT or DIVERGENT** | `GATE FAIL` — kOmegaSST 8 of 10, kEpsilon 6 of 10, LaunderSharmaKE **REFUSED** (not graded); rung 14 of 20, **0 models passed** | `P PAPER-HELD` — Ampofo & Karayiannis 2003 READ IN FULL, Fig. 11 digitised ±0.15 | **NOT HELD** — see §4.2 | `docs/campaigns/F14-cooling-ladder/K0cS_RESULTS.md` | `c83d9501` |
| **S5** | C1 | **turbulent tall cavity, AR 28.7, Ra 0.86e6 / 1.43e6 (Betts & Bokhari)** | `V NO` for the graded rows | `GATE FAIL` — K0cT 8 of 18 graded rows; Nusselt re-grade `GATE FAIL` both Ra; K0cX `GATE FAIL` all three models, **24 of 42** | `P PAPER-HELD` — ERCOFTAC Case 079 primary files on disk (22 files, archive SHA-256 in the manifest); Table 1 read in full, SHA-256 `905cce61…` | **NOT HELD** — see §4.2 | `docs/campaigns/F14-cooling-ladder/K0cT_RESULTS.md` | `cccf7a9f` |
| S5b | C1 | tall-cavity Nusselt re-grade | `V NO` | `GATE FAIL`, both Ra; **explicitly not a pre-registered prediction** — the solve values pre-date the reference and the record says so | `P PAPER-HELD` — Betts & Bokhari Table 1, p. 682: 5.85 and 7.57 | **NOT HELD** | `docs/campaigns/F14-cooling-ladder/K0cT_NUSSELT_REGRADE.md` | `336a364d` |
| S5c | C1 | cross-geometry transfer, K0cX | `V PARTIAL` — **only 1 of 6 model/quantity pairs is in the asymptotic range** | `GATE FAIL`, **24 of 42** graded rows (D420 corrected from 24 of 60), 0 of 3 models passed | `P PAPER-HELD` | **NOT HELD** | `docs/campaigns/F14-cooling-ladder/K0cX_RESULTS.md` | `c557f847` |
| **S5d** | C1 | **third mesh level / model-error attribution, K0cG** | `V PARTIAL` — kOmegaSST five quantities CONVERGING (`p` 1.516–4.078); kEpsilon five STAGNANT/DIVERGENT | **GRADES NOTHING** — the arm arms no gate and moved no K0cS verdict; see §7 for the vocabulary translation | `P PAPER-HELD` (inherits Ampofo) | **SURVEYED** *(the arm itself)* — **its finding is what makes S4 NOT HELD rather than merely unconverged; §4.2** | `docs/campaigns/F14-cooling-ladder/K0cG_RESULTS.md` | `878f1556` |
| S5e | C1 | Prandtl-number sweep, K0cP | `V NO` | no gate on the world; registered predictions met in direction and scale; **a constant `Prt` would need 1.115–1.243**, above everything measured, and differs between meshes | `P PAPER-HELD` (inherits) | **SURVEYED** | `docs/campaigns/F14-cooling-ladder/K0cP_RESULTS.md` | `bff31cff` |
| S5f | C1 | QCR anisotropy, K0cQ | `V NO` | the anisotropy route is **ruled out by 50–250×**; the result is a **NULL**, and a frozen comparator with zero markers on disk is what makes a null readable at all | `P PAPER-HELD` (inherits) | **SURVEYED** | `docs/campaigns/F14-cooling-ladder/K0cQ_RESULTS.md` | `10a932e4` |
| S5g | C1 | SSG Reynolds-stress closure, K0cR | `V NO` | fixing the stress closure moved velocity **19 points toward** the experiment and wall heat flux **30 points away**, in the same solves | `P PAPER-HELD` (inherits) | **SURVEYED** | `docs/campaigns/F14-cooling-ladder/K0cR_RESULTS.md` | `e8f5ae30` |
| S6 | C2 | multilayer solid conduction — wall flux and interface 2 | `V YES` — CONVERGING, `p` 1.079 and 0.952 | `PASS` ×2: `q″` 19.854991 vs exact 19.502682, dev 1.806 % on GCI 2.043 %; `T_i2` −0.51 mK on a 0.75 mK band | `P ANALYTIC-HELD` | **HOLDS** | `docs/campaigns/T-family/T9a_RESULTS.md` | `0cbaea26` |
| S7 | C2 | hot-side interface temperature (T9a R1) | `V YES` — CONVERGING, `p` 1.738 | `GATE FAIL` — **−2.41 mK against a 0.92 mK GCI band** | `P ANALYTIC-HELD` | **NOT HELD** — and the **cause is CONFIRMED**, not suspected: it is the **interface scheme**; §4.6 | `docs/campaigns/T-family/T9a_RESULTS.md` | `0cbaea26` |
| S8 | C2 | fin efficiency and fin tip ratio (T9a R3, R4) | `V YES` — CONVERGING, `p` 1.990 and 1.997 | **`GATE REACHED`** — the GCI bands (0.00077 %, 0.00011 %) sit **below the 0.025 % O(Bi) floor**, so the comparison cannot discriminate; reported, not graded | `P ANALYTIC-HELD` — and the fin equation is 1D and valid only to O(Bi), which is why the floor exists | **GATE REACHED** | `docs/campaigns/T-family/T9a_RESULTS.md` | `0cbaea26` |
| S9 | C2 | interface-scheme diagnosis arm, T9a-D | `V PARTIAL` — B0/B2 triple **STAGNANT**, `p` 0.130 → NOT A RESULT (**predicted in advance**) | 3 `PASS`, 1 `GATE FAIL`, 3 `NOT A RESULT` of 7 registered rows — **every one as the arm's own pre-registered arithmetic predicted, including the two rows where that arithmetic contradicted the directive** | `P ANALYTIC-HELD` | **SURVEYED** *(a diagnosis, which grades no T9a row)* | `docs/campaigns/T-family/T9aD_RESULTS.md` | `a74b2f61` |
| S10 | C2 | harmonic-interpolation re-grade, T9a-H | `V NO` on the frozen path — FR0/FR1 **OSCILLATORY**, FR2 **DIVERGENT** | **split grading path, never merged**: frozen path FR0/FR1/FR2 `NOT A RESULT`, FR3/FR4 `GATE REACHED`; new instrument H1–H6 **6 PASS, 0 GATE FAIL** (H6 a specificity row counting toward nothing) | `P ANALYTIC-HELD` | **SURVEYED** — **it does not make T9a pass and did not try**; T9a's R1 GATE FAIL stands | `docs/campaigns/T-family/T9aH_RESULTS.md` | `b698dfc3` |
| S11 | C2 | **fluid–solid conjugate heat transfer (true CHT)** | `V NONE` | `G NONE` | `P PAPER-HELD` for the intended first rung (Meinders 1998, title-page verified, sha256 `36c89a54…`, re-verified on disk 2026-08-22) | **NEVER RUN** | `docs/campaigns/T-family/T5_PREREGISTRATION_DRAFT.md` (**unfrozen**, 12 INTERPRETATIONs on Sanaa's desk) | `a74b2f61` |
| **S12** | C4 | **heated backward-facing step (separated thermal), T3** | `V PARTIAL` — G2 `x_peak/H` **CONVERGING**, `p` 4.304, GCI 0.0188 %, RE 6.1403; G3/G4 moved DIVERGENT → STAGNANT (`p` 0.23 / 0.22) | **`NOT A RESULT` 4 of 4** at **gate (1) alone**; §4.4 | `P NOT HELD` — Vogel & Eaton 1985 **NOT OBTAINED**; open secondary Smirnov 2016 (CC-BY) digitised as **REPORT-ONLY** | **NOT HELD** | `docs/campaigns/T-family/T3_RESULTS.md` §14 / `T3_EXT1_AMENDMENT.md` §15 | `2f1d6cb7` / `3dd28411` |
| S13 | C4 | fan / air-mover boundary-condition operating point, E4a2 | `V YES` — R1 observed order **1.959** in [1.6, 2.4], GCI **0.393 %**, CONVERGING | `PASS` **8 of 8**; `Q` 1.502157061e-07 vs exact 1.5e-07, dev **0.144 %** | `P ANALYTIC-HELD` | **HOLDS** *(adjunct: this backs a **flow** quantity and, in the DC certificate's own words, "**backs the BOUNDARY CONDITION, not any fan**" — it is not a heat-transfer gate)* | `docs/campaigns/T-family/E4a2_RESULTS.md` | `2d639d3b` |
| S14 | C4 | fan-BC first attempt, E4a | `V NO` — comparator order `None` | **`NOT A RESULT`** (D493) — the registered bit-identity convergence gate cannot close on iterates creeping ~6e-11 relative at writePrecision 12 | `P ANALYTIC-HELD` | **NOT HELD** | `docs/campaigns/T-family/E4a_RESULTS.md` | `44001fc4` |
| S15 | C6 | rack-row module, 2D vertical slice, K2b pilot | `V NO` | **PHYSICALLY UNSTEADY** — 6.0 s limit cycle, 1.1 K amplitude; the **steady cost plan is VOID**. Found for 36.75 core-min against a plan it invalidated that would have cost 374–697 | `P NONE` | **SURVEYED** | `docs/campaigns/F14-cooling-ladder/K2b_PILOT_RESULTS.md` | `5c3fe5a8` |
| S16 | C6 | Blay cavity turbulent mixed convection, K0d | `V NONE` | `G NONE` — specification only, zero compute, no solver launched | `P NOT HELD` — Blay, Mergui & Niculae 1992 **NOT OBTAINED** | **NEVER RUN** — **a K0d pre-registration is being armed in a parallel lane as this is written: prereg being armed, unfired.** No K0d file was written or touched by this lane. | `docs/campaigns/F14-cooling-ladder/K0d_TURBULENT_MIXED_CONVECTION_GATE.md` | `208fef5c` |
| S17 | C6 | hard-floor rack-inlet validation, K2c-A | `V NONE` | `G NONE` — **armable**; rung not built. TREND-ONLY until Figures 3/6/7/8 are digitised | `P PAPER-HELD` — Wibron, Ljung & Lundström 2018, *Energies* 11(3) 644, CC-BY, READ IN FULL, SHA-256 `4de4798e…`, on disk | **NEVER RUN** | `docs/campaigns/F14-cooling-ladder/K2c_RACK_ROW_VALIDATION_SEARCH.md` §3.1 | `cc4f1a64` |
| S18 | C6 | raised-floor / perforated-tile validation, K2c-B | `V NONE` | `G NONE` — **BLOCKED**: no raised-floor gate rows are written and no provisional reference numbers exist, because there is no primary to write them against | `P NOT HELD` — Schmidt & Cruz 2002, VanGilder & Schmidt 2005/2006, Abdelmaksoud 2010 all `is_oa: false`, no repository copies found | **NEVER RUN** | `docs/campaigns/F14-cooling-ladder/K2c_RACK_ROW_VALIDATION_SEARCH.md` §3.2 | `cc4f1a64` |
| S18b | C6 | rack-row module specification, K2a | `V NONE` | `G NONE` — specification, **zero compute** | `P NONE` | **NEVER RUN** | `docs/campaigns/F14-cooling-ladder/K2a_RACK_ROW_MODULE_SPEC.md` | `151bd7ea` |
| S19 | C10 | laminar pipe `f·Re` and constant-`q″` `Nu` (T1c L1, L2, L3) | `V YES` — L2 CONVERGING, `p` 2.031 | `PASS` ×3: `f·Re` 63.98771 vs exact 64, dev 0.0192 % on a 0.0236 % band (twice); `Nu` 4.365298 vs 4.3636364, dev 0.0381 % on 0.0459 % | `P ANALYTIC-HELD` — and the comparator **refuses to run unless the references reproduce** | **HOLDS** | `docs/campaigns/T-family/T1c_RESULTS.md` | `2f1d6cb7` |
| S20 | C10 | laminar pipe constant-`Ts` `Nu` (T1c L0) | `V YES` — CONVERGING, `p` 1.854 | `GATE FAIL` — 3.659958 vs exact 3.6567934, dev **0.0865 % against a 0.0301 % band**, ~2.9 bands out | `P ANALYTIC-HELD` — Graetz eigenproblem, `λ₀²` = 7.313587, agreeing with the tabulated value to 1.6e-08 | **NOT HELD** | `docs/campaigns/T-family/T1c_RESULTS.md` | `2f1d6cb7` |
| **S21** | C10 | **turbulent pipe `Nu`, Re 1e4 / 3e4 / 1e5 / 3e5 (T1b B0/B2/B4/B6)** | `V NO` — **every one of the four triples is DIVERGENT or STAGNANT**; `p` −0.219, −0.150, −0.059, +0.010 | **BOTH readings are displayed and neither is picked**: `PASS` ×4 as returned by the frozen comparator (`08732fd6`, verified byte-identical, sha256 `647d7412…`), **and** `NOT A RESULT` ×4 under the binding triple gate (CLAUDE.md rule 5). D440 | `P FORMULA` — Dittus–Boelter / Gnielinski midpoint, band their half-spread, `T1b_band.json` committed before any case directory existed | **NOT HELD**, *with the tension displayed and the pendency explicit* — §4.3 | `docs/campaigns/T-family/T1b_RESULTS.md`; gate `T1b_L4_AMENDMENT.md` | `07313b68` / `17209b50` |
| S22 | C15 | black box enclosure — floor, x-walls, y-walls (T10a B0, B2, B3) | `V YES` — CONVERGING, `p` 0.954 / 0.853 / 0.825 | `PASS` ×3: floor dev 0.02557 % on 0.03326 %; x-walls 0.48631 % on 0.67756 %; y-walls 0.32987 % on 0.48472 % | `P ANALYTIC-HELD` — closed-form view factors; ε = 1 verified to 0.005 % | **HOLDS** | `docs/campaigns/T-family/T10a_RESULTS.md` | `31fd2268` |
| S23 | C15 | black box enclosure — ceiling (T10a B1) | `V YES` — CONVERGING, `p` 1.480 | `GATE FAIL` — **0.12463 % against a 0.07676 % GCI band**, ~1.6 bands | `P ANALYTIC-HELD` | **NOT HELD** | `docs/campaigns/T-family/T10a_RESULTS.md` | `31fd2268` |
| S24 | C15 | grey concentric spheres (T10a S0, S1) | `V NO` — both triples **DIVERGENT**, `p` −3.253 and −1.838 | **`NOT A RESULT`** ×2; no band armed (Charter §2c — a band on a NOT A RESULT row is UNMEASURED, not zero) | `P ANALYTIC-HELD` — two-surface network | **NOT HELD** — and the **cause is CONFIRMED**: the `viewFactorsGen` row-sum defect, §4.7 | `docs/campaigns/T-family/T10a_RESULTS.md` | `31fd2268` |
| S25 | C15 | ceiling refinement arm, T10a-R | `V YES` on its own ladder — RX2 triple CONVERGING | **grades NOTHING against T10a's band**; T10a stands closed at GATE FAIL. Against **this arm's own** registered bands: `GATE FAIL` including **RX3 falsifier FIRED** (dev ÷ band 0.542 ≤ 1.0 — the band covers the error), and the **band-smaller-than-error pattern dies at level four** | `P ANALYTIC-HELD` | **SURVEYED** | `docs/campaigns/T-family/T10aR_RESULTS.md` | `cdb5cc0b` |
| S26 | C15 | view-factor quadrature defect characterisation, T10a-VF | `V NO` — the defect is non-converging under fixed quadrature by construction | no gate on the world; the defect has **a single named cause, a closed-form size and a one-key workaround** (`alpha = exp(-3/2)` or `distTol = 1`), **not yet graded** | `P ANALYTIC-HELD` | **SURVEYED**. **SUBMISSIONS PARKED** — `docs/upstream/T10a_viewFactorsGen_rowsum_NOT_FILED.md` opens with `NOT FILED`; upstream candidate #4; filing is Sanaa's call alone | `docs/campaigns/T-family/T10aVF_RESULTS.md` | `6a9b8c41` |
| S27 | C15 | **participating-media radiation** | `V NONE` | `G NONE` | `P NONE` | **NEVER RUN** | — | — |

---

## 4. The load-bearing findings, each with its numbers

### 4.1 K0c is this family's ONE CLEAN GATE PASS — and the 20-vs-24 denominator is RESOLVED on disk

**`GATE PASS. 0 of 20 GRADED rows failed.`** Largest deviation anywhere on the
gate **1.139 %** on a **3 %** band. **41.73 core-minutes** produced the table,
**plus roughly 44.3 core-minutes discarded** — and the discarded figure is
labelled on its own record as **reconstructed, not measured**.

**The 20-vs-24 discrepancy flagged in `LAB_INVENTORY.md` §6 is RESOLVED from
disk, and both files already agree on the corrected figure.** It is not two
sources disagreeing about a fact; it is one file's **headline** disagreeing with
that same file's own **dated correction**, which is exactly how CLAUDE.md rule 6
requires a frozen record to be repaired:

| where | what it says | status |
| --- | --- | --- |
| `K0c_RESULTS.md:18` and `:103` (the headline) | "GATE PASS. 0 of 24 graded rows failed." | **SUPERSEDED** by the correction below, which is in the same file and says so |
| `K0c_RESULTS.md:527-563`, *Dated correction, 2026-08-18 — the denominator, not the verdict* | "**The corrected statement of this rung is: GATE PASS, 0 of 20 GRADED rows failed, with 4 identity rows reported and counted toward nothing.**" | **IN FORCE** |
| `docs/THERMAL_CAPABILITY_STATE.md:33` | "GATE PASS, 0 of 20 graded rows failed (D419 corrected the denominator from 24)" | **agrees with the correction** |

**Why 24 and 20 are both true of different things.** `gate_k0c.json` carries **24
entries in `gate_rows`**, of which **4 are `"quantity": "energy_balance"`** —
boundary heat balance on a sealed cavity, a **demonstrated identity**. Charter
§2a: a gate whose quantity is derivable by construction from its own inputs may
be **reported** and **may never be gated on**. The four measured between
**3.06e-05 %** and **7.09e-05 %** against a 0.5 % band — five orders of magnitude
inside a band they could not have missed.

**The verdict does not move and no number moves. What moves is the evidence base,
which was overstated by 20 %.** It was found not by review but by the
discrimination check `scripts/check_row_discrimination.py` (rule D3-GUARD-GRADED)
running a g = 0 null arm, which observed the energy-balance row was the only one
of six the null arm also passed, at **0.000 bands** — the signature of a row that
cannot come out differently. Docketed **D414**; the corrected denominator is
**D419**.

**One residual, carried openly:** `gate_k0c.json` still carries the four identity
rows inside `gate_rows`, because separating them there regenerates a published
artifact. The record names this and rules that **the prose section, not the JSON,
is the correct one**.

**For the matrix:** the row should read **0 of 20**, never 0 of 24, and the
"largest deviation 1.14 % on a 3 % band" is 1.139 % as printed.

### 4.2 The turbulent-thermal front is NOT HELD — and that is a defensible scientific position, stated as one

> **Sanaa, verbatim:** *"the 18-combination zero-pass finding enters the matrix as
> NOT HELD with its model-error attribution (43-722x GCI proof) — that's a
> defensible scientific position, stated as one"*

**The attribution, stated exactly.** From `K0cG_RESULTS.md` §2, the table at
lines 29–35 — **kOmegaSST, square cavity, deviation ÷ GCI:**

| quantity | finest | reference | \|deviation\| | GCI (absolute) | **deviation ÷ GCI** | `p` | triple |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `Nu_hot` | 55.091 | 63.45 | 8.359 | 0.0992 | **84×** | 2.088 | CONVERGING |
| `Nu_cold` | 54.885 | 63.95 | 9.065 | 0.0388 | **233×** | 3.121 | CONVERGING |
| `Sp` | 0.76597 | 0.481 | 0.2850 | 0.00255 | **112×** | 4.078 | CONVERGING |
| `Vpeak` | 0.25541 | 0.2127 | 0.04271 | 5.91e-05 | **722×** | 3.698 | CONVERGING |
| `uv_peak` | 4.830e-04 | 1.080e-03 | 5.970e-04 | 1.387e-05 | **43×** | 1.516 | CONVERGING |

Record path `docs/campaigns/F14-cooling-ladder/K0cG_RESULTS.md`, sha `878f1556`.
**43 and 722 are the minimum and maximum of that five-row set.**

**What the ratio proves.** The deviation from experiment is **43 to 722 times the
grid-convergence uncertainty** on the same quantity. Refining the mesh cannot
account for a gap two to three orders of magnitude larger than the discretisation
uncertainty. **The gap is MODEL ERROR, not grid error.** That is a *positive
scientific finding* — the lab measured which of two candidate causes it is — and
it is emphatically **not** a failure to converge: all five triples are CONVERGING.

**Two precisions the matrix must not blur** (both verified independently by the
heat-transfer supervisor against §2 and §3 of the record):

1. **kEpsilon has NO attribution ratio at all.** §3: `Nu_hot` **STAGNANT**
   (`p` 0.150), `Nu_cold` **STAGNANT** (0.239), `Sp` **DIVERGENT** (−0.786),
   `Vpeak` **DIVERGENT** (−1.015), `uv_peak` **DIVERGENT** (−0.102). The record's
   own words: *"No band can be armed for any of them, so no attribution ratio
   exists."* Under rule 5 those are **NOT A RESULT**.
   **Therefore: the zero-pass is the OBSERVATION, across every combination; the
   43–722× is the ATTRIBUTION, and it is carried by kOmegaSST's five converged
   quantities on the square cavity.** Stated that way it is a *stronger* position,
   not a weaker one, because it is the one the evidence actually supports.
2. **The record volunteers its own caveat and it is carried here in full.** Three
   of the five observed orders (3.121, 4.078, 3.698) **exceed the formal second
   order**, which usually means the coarsest level is outside the asymptotic
   range, so *"the GCI on those rows should be read as indicative rather than
   exact."* The record then argues the conclusion survives **because the ratios
   are two to three orders of magnitude**. Both halves travel together — the
   caveat and the argument.

**The "18 combinations" accounting — what the records actually support.**

**No record in this repository uses the phrase "18 combinations", "18-combination"
or "eighteen combinations".** (Verified by a full-repo grep; the only "eighteen"
in a countable sense is **D420's** *"EIGHTEEN OF SIXTY K0cX ROWS THAT GRADED
NOTHING LEFT THE TALLY"* — 18 non-discriminating **rows**, an entirely different
quantity that must not be confused with 18 combinations.) The number is Sanaa's
framing, so here is the accounting the records do support:

**Axis 1 — models (3):** `kOmegaSST`, `kEpsilon`, `LaunderSharmaKE`.
**Axis 2 — geometry × Rayleigh conditions (3):** square cavity at Ra 1.58e9
(K0cS, Ampofo); tall cavity AR 28.7 at Ra 0.86e6; tall cavity AR 28.7 at
Ra 1.43e6 (K0cT / K0cX, Betts & Bokhari).
**Axis 3 — quantity class (2):** a graded **velocity** quantity and a graded
**heat** quantity. This axis is not decorative: the synthesis's central
transferable result is that on both geometries *"the momentum error and the
thermal error were not slaved to one another, and the model ranking INVERTED
between them"* — square cavity, kEpsilon nearer on velocity and kOmegaSST nearer
on heat; tall cavity, kOmegaSST nearer on velocity and LaunderSharmaKE nearer on
heat.

| reading | count | passes |
| --- | ---: | ---: |
| model × (geometry, Ra) | **3 × 3 = 9** | **0** |
| model × (geometry, Ra) × quantity class | **3 × 3 × 2 = 18** | **0** |

**So "18" is supported only on the three-axis reading, model × geometry ×
quantity, and the records support it exactly.** On the two-axis reading the
number is **9**. **This contribution recommends the matrix state the axes rather
than the bare number** — "three models × three geometry/Rayleigh conditions ×
two quantity classes, zero passes" — because the bare 18 is indistinguishable
from D420's unrelated 18 and from the 18 cells of this very matrix.

**Row-level tallies, for a lane that prefers them** (these are rows, not
combinations): K0cS **14 of 20 graded rows failed, 0 models passed**; K0cT **8 of
18 graded rows failed** plus a Nusselt re-grade **GATE FAIL** on both Ra; K0cX
**24 of 42 graded rows failed, 0 of 3 models passed**.

**Headline for the matrix:** *three models, two geometries, three Rayleigh
decades, **zero passes**; gradient-diffusion refuted three ways* — by experiment
on the value (K0cP: no constant `Prt` works; the value needed is 1.115–1.243,
above everything measured, and differs between meshes), by anisotropy
(K0cQ: ruled out by 50–250×), and by stress closure (K0cR: velocity 19 points
better, heat flux 30 points worse, in the same solves).

**And the control that makes it a modelling statement rather than a numerics
one costs nothing, because both rungs were already run:** the laminar K0c rung
is the same solver family, same geometry class, same schemes, same mesh-pair
discipline, same comparator architecture — zero rows failed and the worst
deviation was 1.139 %. **The one thing that changed between that result and the
turbulent rungs was the closure.**

**No turbulence model has ever passed a turbulent thermal gate against experiment
in this lab.** That is the deepest open problem the family owns, and it is
**reference-limited as much as model-limited** — a buoyancy-driven flux term
needing transported temperature variance is **named, not built**.

### 4.3 T1b's tension is SHOWN, not resolved

**Both readings, side by side, and this contribution picks neither.**

| row | `Re` | value | reference | band | deviation | **grid triple** | `p` | **reading A — frozen comparator** | **reading B — binding triple gate** |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| B0 | 1e4 | 31.619 | 30.907 | 2.84 % | 2.305 % | **DIVERGENT** | −0.219 | **PASS** | **NOT A RESULT** |
| B2 | 3e4 | 72.480 | 73.684 | 1.635 % | 3.89 % | **DIVERGENT** | −0.150 | **PASS** | **NOT A RESULT** |
| B4 | 1e5 | 185.771 | 190.398 | 2.430 % | 5.33 % | **DIVERGENT** | −0.059 | **PASS** | **NOT A RESULT** |
| B6 | 3e5 | 449.255 | 456.723 | 1.635 % | 5.75 % | **STAGNANT** | +0.010 | **PASS** | **NOT A RESULT** |

**Reading A** is what the frozen comparator returned. `analyse_t1b.py` was frozen
at commit `08732fd6` (2026-08-19 19:10:04 Z) **before any case solved**, and
verified byte-identical at analysis time, sha256 `647d7412…`. **A comparator's
PASS is not overwritten after the fact** — that is Charter §2d, and it is the
whole evidentiary content of a freeze.

**Reading B** is CLAUDE.md rule 5: *a row whose grid triple is not CONVERGING is
NOT A RESULT, whatever its value.* Every one of the four triples is DIVERGENT or
STAGNANT. **The gate can only turn a PASS into NOT A RESULT, never the reverse** —
so reading B can never manufacture a pass out of reading A, only withdraw one.

**Attribution: D440.** The tension is on the record as a docketed item, not as an
editorial choice by this lane. The candidate amendment that would adopt reading B
formally lives at `T1b_RESULTS.md` §8; `T1b_L4_AMENDMENT.md` (`17209b50`) is
where the binding triple gate is written down.

**Both readings agree on the one thing that matters for the matrix: NONE of the
four is a mesh-converged value.** The tier is **NOT HELD**, and it is NOT HELD
under either reading — under A because a PASS on a non-converged ladder is not a
capability, under B because the row is NOT A RESULT outright.

**The pendency is explicit, and it is live on this box as this is written.**
The L4 arms `R_*_x` extend the ladder to a fourth level. Read from disk, not from
a summary:

| arm | `endTime` | last time directory | marker | state |
| --- | ---: | ---: | --- | --- |
| `R_10k_x` | 20 000 | 20 000 | `DONE.R_10k_x` present | **complete** |
| `R_30k_x` | 80 000 | 58 000 | none | **in progress** |
| `R_100k_x` | 80 000 | 64 000 | none | **in progress** |
| `R_300k_x` | 80 000 | 78 000 | none | **in progress, and LIVE** — time directory 78 000 written within 30 minutes of this write |

Run tree `verification/runs/T-family/T1_runs/`. **Until the three unfinished arms
land, no mesh-converged value exists for this class**, and any matrix cell for it
must carry that pendency on its face. **No solver was touched by this lane** —
the arm states above were read from `controlDict` and directory listings only.

### 4.4 T3 is NOT A RESULT 4/4, and it fails at gate (1) alone

**After the ext1 extension the rung is 8/8 complete** under the two-segment
strict rule (`mark_done_t3_ext1.py`): both segments `rc=0`, both `End` lines, the
summed `ExecutionTime` identity (20 000 + 58 000 = 78 000 == `endTime` on `R_f`),
the first ext1 `Time = 20001` continuity test, and **two** age-guard data (`0/T`
and `STATUS.<case>`). `R_f` finished 2026-08-24T14:53:19Z. The frozen comparator
`analyse_t3.py` (sha `f41c544d…`, byte-identical to the §11 blob, verified by two
lanes) exited 0 with the **planted zero 1.234e-03 K read back and passed**.

**Tally: PASS 0 / GATE FAIL 0 / NOT A RESULT 4 / BLOCKED 0; 0 of 4 graded.**

**WHERE it fails, precisely: gate (1) alone** of `T3_PREREGISTRATION.md` §7.1 —
not gate (2), and not the missing-primary gate (3).

- `R_m` and `R_f` are **CONVERGED** (9.68e-08 and 7.80e-08).
- It is **`R_c`** that stops the ladder, **in a limit cycle at the 80 000 cap**
  (rel Δ`T` 4.83e-02). **This is not a surprise and not an excuse:**
  `T3_PREREGISTRATION.md` §11 **registered it in advance** as an outcome the rung
  **reports rather than averages**. The rung says so and does not average.
- **One triple, G2 `x_peak/H`, is CONVERGING** — `p` **4.304**, GCI **0.0188 %**,
  Richardson extrapolate 6.1403 — **and it is NOT A RESULT anyway, because gate
  (1) fires before a triple is consulted.** This is the triple gate operating in
  **the only direction rule 5 allows**: turning a gradeable row **into** NOT A
  RESULT, never the reverse.
- What else moved: the St ladder is **monotone in mesh for the first time**;
  G3/G4 moved **DIVERGENT → STAGNANT** (`p` 0.23 / 0.22); `R_f`'s heat balance
  went 8.234 % → **0.000393 %**.

**The missing primary is necessary and NOT SUFFICIENT, and it is NOT today's
binding constraint.** Vogel & Eaton 1985 is **NOT OBTAINED** — ASME closed, every
open archive checked and named in prereg §2 — and its absence remains
disqualifying. But gate (3) sits **downstream** of gates (1) and (2), which fire
first. Obtaining the paper tomorrow would not move this rung off NOT A RESULT.

**Registered response:** a fourth mesh level (`R_m`, `R_f`, `R_ff`) — **PROPOSED
and NOT RUN**, needing its own costed pre-registration (rough bound 150–200
core-h, USD 8–10 derived). Docketed **D495**.

**Cost:** ext1 **4 798.05 core-min = 79.968 core-h = $4.102 derived (not
measured)** against $4.08 registered = **1.005×**, from two cancelling errors;
rung total **120.29 core-h / $6.171 derived**, 24.7 % of the $25 threshold. Waste
nil.

**Records:** `docs/campaigns/T-family/T3_RESULTS.md` §14 (`2f1d6cb7`) and
`docs/campaigns/T-family/T3_EXT1_AMENDMENT.md` §15 (`3dd28411`).

### 4.5 The DC certificate — the accounting, CORRECTED against the file

**The brief this lane was given said "ten backed lines (8 PASS, 2 GATE REACHED)".
Read against `docs/product/DC_CERTIFICATE_TEMPLATE.md` (`5a197a41`), that is
STALE. The file holds ELEVEN.** Its own §2 summary line reads: *"Eleven lines, of
which two are GATE REACHED and nine are PASS."* Counted row by row from the §2
table, that is **9 PASS + 2 GATE REACHED = 11**. The eleventh is the **E4a2 fan
boundary-condition line**, added at `5a197a41`.

| backing rung | lines | verdict | class |
| --- | ---: | --- | --- |
| T1c L2, L1, L3 | 3 | `PASS` | laminar duct forced convection + laminar friction |
| T9a R0, R2 | 2 | `PASS` | solid conduction (wall flux, interface temperature) |
| T9a R3, R4 | 2 | **`GATE REACHED`** | fin conduction (bands below the O(Bi) floor) |
| T10a B0, B2, B3 | 3 | `PASS` | surface-to-surface radiation, black box enclosure |
| E4a2 G1 | 1 | `PASS` | fan / air-mover **boundary condition** — a flow quantity |

**The substantive claim in the brief SURVIVES and is sharpened.** Every backed
line is **conduction, laminar, radiation — or a boundary-condition verification**.
**None is turbulent. None is mixed-convection. None is buoyant.** The eleventh
line does not weaken this: the certificate itself flags it *"**This backs the
BOUNDARY CONDITION, not any fan**"*, and it is a volumetric flow rate, not a heat
quantity.

**And all four DC quantity classes are PENDING — confirmed against §4 of the
file:**

| DC quantity class | rung(s) that would back it | state |
| --- | --- | --- |
| **inlet temperature** | T5 → T12 | **PENDING** — T5 primary HELD, cost registration pending; T12 ACQUIRE, over $25 |
| **recirculation** | T5 → T8 | **PENDING** |
| **stratification height** | T8 → T12 | **PENDING** — T8 has a partial-EXACT entry rung (Morton–Taylor–Turner plume entrainment) available before its data arrives |
| **transient response** | T11 | **PENDING** — lumped and 1D transient solutions are closed form; the published transient data is not held |

**`PENDING` here is used as the charter reserves it** — a display/queue state for
work not yet run, never a softened GATE FAIL.

**For the matrix:** *eleven backed certificate lines, nine PASS and two GATE
REACHED, and **not one of the four quantity classes a data centre is actually
specified on** is among them.*

### 4.6 T9a / T9a-H — conjugate, with the cause CONFIRMED

R0 `PASS`, R2 `PASS`, **R1 `GATE FAIL`** (−2.41 mK against a 0.92 mK GCI band),
R3/R4 **`GATE REACHED`** below the 0.025 % O(Bi) floor, 4 controls MET.

**The cause is CONFIRMED, not suspected: it is the interface scheme.** T9a-D
(directive H-4, D454, L-227): replacing `Gauss linear` with `Gauss harmonic` on
`laplacian(DT,T)` drops the R1 level error from **−5.43 / −3.34 / −2.41 mK** to
**0 / −3.2e-09 / −3.0e-09 mK** — a factor **8.2e+08** at the finest level against
a registered threshold of 3 — and drops the R0 flux excess from **+1.806 % to
+0.0000000 %**. Every harmonic level reproduces the closed form to all nine
printed digits, **on the 35-cell coarse mesh included**.

**T9a-H re-graded under harmonic interpolation and it does not rescue T9a.** The
grading path is **SPLIT and the two halves are never merged**: the frozen T9a
comparator returns FR0 / FR1 **NOT A RESULT** (OSCILLATORY), FR2 **NOT A RESULT**
(DIVERGENT), FR3 / FR4 **GATE REACHED**; the new instrument `analyse_t9aH.py`
returns H1–H6 **6 PASS, 0 GATE FAIL** (H6 a specificity row counting toward
nothing). **No T9a number moved and no frozen file was edited.** The record says
plainly: *"It does not make T9a pass and did not try."* The discrimination test
HC4 — the null arm on the same mesh with `Gauss linear` — fails H1/H2/H3 as
required, which is what makes H1–H3 evidence at all.

### 4.7 T10a — radiation, with the cause CONFIRMED and PARKED

Box: **3 of 4 PASS**, ceiling **GATE FAIL** at 0.12463 % against a 0.07676 %
band. Spheres: **NOT A RESULT ×2** on DIVERGENT triples. 12 controls MET, 6
UNMEASURED (**a band on a NOT A RESULT row is UNMEASURED, not zero** — Charter
§2c). One §2d.1 zero-referent repair disclosed, **graded rows byte-identical
across it**. D447.

**T10a-R** (H-3a) took the ceiling to a fourth level and **grades NOTHING against
T10a's band** — T10a stands closed at GATE FAIL. Against its own registered
bands it is **GATE FAIL** with **RX3's falsifier FIRED** (deviation ÷ band 0.542,
i.e. the band covers the error), the **band-smaller-than-error pattern dies at
level four**, and the **quadrature method is confirmed material** (RQ2 fired);
iteration is exonerated.

**T10a-VF** (H-3b) named the cause: a **`viewFactorsGen` alpha-regularisation
defect** in the 2LI branch's treatment of the coincident-edge log singularity —
a **defect of the utility**, not a mesh, orientation, agglomeration or
faceted-sphere artefact. Closed form, one-key workaround (`alpha = exp(-3/2)` or
`distTol = 1`), **not yet graded**. D457, L-231.

**SUBMISSIONS PARKED (rule 7).** Upstream candidate #4 is a draft at
`docs/upstream/T10a_viewFactorsGen_rowsum_NOT_FILED.md` whose **opening line**
reads `NOT FILED — draft for Sanaa's decision`. Nothing has been sent, no issue
opened, no maintainer contacted. **Filing is Sanaa's decision alone.**

### 4.8 T1a / K0e — BLOCKED, and the reason is structural, not a shortage

The reference **is** on disk: Bahrami, P. A. (2005), *Heat Transfer on a Flat
Plate with Uniform and Step Temperature Distributions*, NASA/TM-2005-212841 — US
government work, openly available, filed at
`docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf`,
sha256 `0cd29adb…`. **P is HELD.**

**And the rung still cannot be gated**, because **no honest band can be armed
from a single correlation** — there is no second independent source to give the
band a half-spread, which is exactly the construction T1b uses (Dittus–Boelter
against Gnielinski). This is `BLOCKED` in the charter sense: a gate that cannot
be armed, not a run that failed. **The tier is NEVER RUN** (no solver has been
launched — the K0e document is a specification at zero compute), and the
**BLOCKED** status attaches to the gate, not to the class's history.

**Why the class matters more than its size suggests.** Every thermal result this
lab owns is a buoyant cavity, where the momentum field and the thermal field are
both wrong **and are coupled through buoyancy**. A zero-pressure-gradient flat
plate breaks that confound: momentum closure is the best-validated thing the lab
owns and buoyancy is absent by construction, so **any Stanton-number error would
be attributable to the thermal closure alone**. This is the rung that would make
the family's closure findings **transferable rather than cavity-specific**.

### 4.9 K2b — mixed convection, and a physics finding that voided a cost plan

**The module at 70 % provisioning is PHYSICALLY UNSTEADY**: a **6.0 s limit
cycle** at **1.1 K amplitude**. The steady formulation is therefore the wrong
tool and **the §9 steady cost estimate is VOID**. It was found for **36.75
core-minutes**, against a plan it invalidated **that would have cost 374–697**.
Rung spend **65.4 of 81.4 core-minutes authorised; 16.0 returned unspent.**

**The 3D graded pair remains unrun and unauthorised.** A K2b 3D unsteadiness
pre-registration exists and run directories exist; **there are no results**.

---

## 5. Classes that have NEVER RUN

Named explicitly, because an unnamed absence is invisible.

| class | nearest planned rung | primary status | tier |
| --- | --- | --- | --- |
| **Participating-media radiation** | — | none sought | **NEVER RUN** |
| **Phase change** | — | none sought | **NEVER RUN** |
| **Humidity** | — | none sought | **NEVER RUN** |
| **Transient thermal response / thermal mass** | T11 (partial EXACT: lumped and 1D transient solutions are closed form) | published transient data **not held** | **NEVER RUN** |
| **3D conjugate (fluid–solid)** | T9c; T5 would be the first CHT of any dimension | T5's Meinders 1998 **P PAPER-HELD**; T5 prereg is a **draft, unfrozen**, 12 INTERPRETATIONs on Sanaa's desk | **NEVER RUN** |
| **Turbulent mixed convection** | K0d (Blay cavity) | Blay 1992 **NOT OBTAINED**. **A K0d pre-registration is being armed in a parallel lane — prereg being armed, unfired.** No K0d file was created or edited by this lane. | **NEVER RUN** |
| **Impinging jet** | T4 | **PARTIAL** — ERCOFTAC case025 tabulated `Nu(r/D)` on disk (Re 23k/70k, H/D 2/6; one mislabeled header noted) + Martin correlation with stated validity from an open NREL report; **the `Nu` uncertainty is SECOND-HAND (2.4 %, KB Wiki quoting Baughn & Shimizu)**; graded rows need the closed ASME primaries | **NEVER RUN** |
| **Heated cubes (the rack physic)** | T5 | **P PAPER-HELD** — Meinders 1998 TU Delft thesis, OPEN, title-page verified, sha256 `36c89a54…`, stated uncertainty 5 % mid-face / 10 % edges in local `h`; **digitisable figures, no tabulated appendix** | **NEVER RUN** |
| **Plume / stratification (the aisle physic)** | T8 | partial EXACT — **Morton–Taylor–Turner entrainment theory is closed form**; the room data is not held | **NEVER RUN** |
| **Room-scale ventilation** | T12 | ACQUIRE, **over $25** | **NEVER RUN** |
| **Rack row** | T13 / K2a | inherits everything above it; **unplaced** — not in the spine, not in the H-5 completion order | **NEVER RUN** |
| **Rayleigh–Bénard `Nu`–`Ra` scaling** | T6 | 3–4 decades of published scaling data; **transient, far over $25** | **NEVER RUN** |
| **Mixed-convection regime map** | T7 | generalises K0d; per-run cheap, **aggregate may exceed $25** | **NEVER RUN** |
| **Tube bank** | T2 | FORMULA (Zukauskas) — needs the correlation's **stated validity range** cited, not just its algebra | **NEVER RUN** |
| **Natural convection + radiation combined** | T10b | combined-mode data, ACQUIRE | **NEVER RUN** |
| **Conjugate flat plate** | T9b | ACQUIRE | **NEVER RUN** |
| **Raised-floor / perforated-tile rack inlet** | K2c-B | **BLOCKED** — no primary; all candidates `is_oa: false`, no repository copies | **NEVER RUN** |

Source for the ladder rows: `docs/campaigns/T-family/T_FAMILY_INDEX.md`
(`3dd28411`).

---

## 6. Standing caveat 1 — D389 / S13, **and a correction to this lane's brief**

**This lane was briefed that "D389 is OPEN and deliberately unrepaired". Read
against the record, that is FALSE. D389 was SETTLED by D393, the repair landed,
and the corpus re-grade was performed.** The record beats the summary
(`docs/DOCKET.md`, `a9b67abc`).

**What D389 recorded.** `thermal.monitor_peak_to_peak_max_pct` (0.02 %) was
applied to `spread / |last value|`. For K0c's Nusselt number — an O(1)
dimensionless group — the mean **is** the scale and that is right. For a
rack-inlet temperature the mean is ~289–300 K while the physically meaningful
scale is the rack rise Δ`T` = 12 K, so **0.02 % of the mean is 0.058 K where
0.02 % of the signal is 0.0024 K** — the **~24×** figure. D393 restates the same
defect on the tightest case as **a factor of 3,343** (mean 289 K, range 0.086 K).
**Both numbers are in the record and they measure different framings of the same
fault; the matrix should not quote one as if it were the other.**

**What D393 did.** The spread is now referred to **the range the quantity spanned
over the run** — `heat_monitor_normaliser: range_spanned_over_run`, live on disk
at **`docs/physics_rules.yaml:255`** (`d4575a69`), MONITOR_STANDARD v1.12,
`scripts/check_convergence.py`. The threshold **number** is unchanged at 0.02 %
because its original derivation — *"one fiftieth of the tightest pass band K0c
gated on"* — was always a fraction of the thing being resolved, and the mean was
only a proxy. **The same repair fixed a second fault** (the v1.11 null-variation
clause, which had refused four committed K2e cases that print sixteen significant
figures bit-identically across the window after travelling 0.53).

**What the re-grade found — and this is the part that matters most for the
matrix.** All **49 committed cases** (K0c 11, K2e 30, K2b 8) were re-graded
against the original criterion. **Exactly TWO verdicts changed, both K2b's:**
`K2bP_fine` CONVERGED → CANNOT_TELL, `K2bP_coarse` CONVERGED → NOT_CONVERGED at
3.3876 % of its range — **which agrees with the two independent instruments on
that same run** (heat balance 0.7857 % out, S13 on the free boundary 0.03973 %).
**All 11 K0c verdicts and all 30 K2e verdicts are UNCHANGED.** Both constants
were shown non-load-bearing by sweep: the threshold gives an identical verdict
set anywhere in (0.0027, 0.0642] %, a 24× span with 0.02 inside it.

**Consequence for the matrix.** D389's stated fear — that re-normalisation *"moves
verdicts across the whole thermal corpus (K0c's eleven, K2e's thirty, KV1's
three)"* — **did not materialise**. **No cell in §2 or §3 has a verdict that
depends on the mean-normalised S13**, because the only two verdicts the repair
moved were K2b's convergence states, and **K2b is tiered SURVEYED and carries no
gate against a reference in any case**. This is stated as a positive finding, not
an assumption: it rests on the re-grade of 49 cases recorded at D393, and any
verification lane may re-derive it from `docs/physics_rules.yaml:255` and
`scripts/check_convergence.py`.

**What this lane could NOT verify:** it did not re-execute the 49-case re-grade
itself. The statement above cites D393's record and the on-disk configuration
key; it is not an independent measurement by this lane.

---

## 7. Standing caveat 2 — vocabulary drift in the F14 records, translated and auditable

`LAB_INVENTORY.md` §6 flags branch labels sitting where verdicts should be.
**Every one met while writing this file is translated to the fixed vocabulary,
and the original word is recorded beside it so the translation can be audited.**
None of these translations edits any record — they are readings, offered to the
matrix.

| original word, as it stands in the record | where | what it actually is | translation offered to the matrix |
| --- | --- | --- | --- |
| **FORM** | `K0cP_RESULTS.md:10` — *"Verdict: FORM"* | a **pre-registered branch label** from K0cP's own outcome mapping (the failure is in the *form* of gradient diffusion, not in the value of a constant); both registered predictions were met in direction and scale | **SURVEYED** — the arm grades nothing against the world; its finding is that no constant `Prt` works (the value needed is 1.115–1.243, above everything measured) |
| **SMALL** | `K0cQ_RESULTS.md:14` — *"Verdict: SMALL"* | a **pre-registered branch label**: the anisotropy route is ruled out by 50–250× | **SURVEYED** — and the result is a **NULL**, which is precisely the result most easily manufactured by an instrument that was not looking properly; what makes it readable is that the comparator was frozen with **zero completion markers on disk** |
| **WORSE** | `K0cR_RESULTS.md:13` — *"Verdict: WORSE, by the rule registered before compute"* | a **pre-registered branch label**: SSG moved velocity 19 points toward the experiment and wall heat flux 30 points away | **SURVEYED** |
| **REFUSED** | `K0cS_RESULTS.md:20` — `LaunderSharmaKE` **REFUSED** | **not a failed gate — an ungraded model.** The fine mesh missed the **registered** convergence criterion, so the comparator declined to grade rather than degrading. The distinguishing evidence: `fmu` 0.887 → 0.034, **25 996 bounding-`k` events of 40 000 iterations**, Reynolds stress four orders below molecular — the model **relaminarised** | **NOT A RESULT** — this is a refusal under the strict completion / convergence discipline, which is exactly what rule 5's clause (1) describes. **It is NOT a GATE FAIL and must not be counted as one**; K0cS's headline correctly reports "0 models passed" rather than "3 models failed" |
| **GRADES NOTHING** | `K0cG_RESULTS.md:8` — *"This rung GRADES NOTHING and no K0cS verdict moved"* | an **honest scope statement**: the arm reports whether the solutions are in the asymptotic range, which is the *precondition* for reading K0cS's deviations as model error | **SURVEYED** for the arm itself. **Its output is what licenses S4's NOT HELD** (§4.2) |
| **O1** | `K2b_PILOT_RESULTS.md:1501` — *"Outcome: O1 — PHYSICALLY UNSTEADY"* | a **pre-registered outcome-mapping branch**, fixed before anything ran | **SURVEYED**, with the physics finding stated as the substance: 6.0 s limit cycle, 1.1 K amplitude, steady cost plan VOID. The record itself flags the honest limit — a 2D slice can both suppress a 3D instability and manufacture oscillations a 3D flow would damp, so **O1 is a warning about the 3D case, not a measurement of it** |

**A note the matrix should carry:** all six of these are **pre-registered branch
labels, not ad-hoc adjectives**. That is materially better than hedging prose —
each was fixed before compute and each could have come out the other way. The
defect is that a **branch label is being read as a verdict** by anything sweeping
the corpus, and rule 1 admits only the six verdict words. The translations above
are the repair for the matrix; repairing the records themselves is a W-4
amendment and is not this lane's call.

---

## 8. THE CENSUS

### 8.1 Cell-level census — the 18 cells of §2

| tier | cells | which |
| --- | ---: | --- |
| **HOLDS** | **4** | C1 2D buoyant-thermal; C2 2D conjugate; C10 axisym forced-convection-internal; C15 3D radiation |
| **GATE REACHED** | **0** | — (GATE REACHED appears only at sub-row granularity: T9a R3/R4) |
| **SURVEYED** | **1** | C6 2D mixed-convection |
| **NOT HELD** | **1** | C4 2D forced-convection-internal |
| **NEVER RUN** | **12** | C3, C5, C7, C8, C9, C11, C12, C13, C14, C16, C17, C18 |
| **total** | **18** | |

> ### **NEVER RUN: 12 of 18 cells — two thirds of the thermal cross.**

**Read the four HOLDS cells narrowly.** Each holds on a *sub-class* and each
carries a NOT HELD sub-class inside it: C1 holds **laminar only**; C2 holds
**pure solid conduction only**, and fluid–solid CHT has never run in any
dimension; C10 holds **`f·Re` and constant-`q″` `Nu` only**; C15 holds **the
black box enclosure only**, and participating media has never run.

**The cell-level census flatters the record**, because a single PASS anywhere in
a cell promotes the whole cell to HOLDS. §8.2 is the honest one.

### 8.2 Sub-row census — the 36 sub-rows of §3

**This is the honest census.** Counted by id from the §3 table:
S1, S2, S2b, S3, S3b, S4, S5, S5b, S5c, S5d, S5e, S5f, S5g, S6, S7, S8, S9, S10,
S11, S12, S13, S14, S15, S16, S17, S18, S18b, S19, S20, S21, S22, S23, S24, S25,
S26, S27 — **36 rows**.

| tier | sub-rows | which |
| --- | ---: | --- |
| **HOLDS** | **5** | S1 (K0c laminar cavity), S6 (T9a wall flux + interface 2), S13 (E4a2 fan BC — a *flow* quantity, adjunct), S19 (T1c `f·Re` + constant-`q″` `Nu`), S22 (T10a box floor/x-walls/y-walls) |
| **GATE REACHED** | **1** | S8 (T9a fin efficiency + fin tip ratio, bands below the O(Bi) floor) |
| **SURVEYED** | **13** | S2, S2b, S3, S3b, S5d, S5e, S5f, S5g, S9, S10, S15, S25, S26 |
| **NOT HELD** | **11** | S4, S5, S5b, S5c, S7, S12, S14, S20, S21, S23, S24 |
| **NEVER RUN** | **6** | S11, S16, S17, S18, S18b, S27 |
| **total** | **36** | 5 + 1 + 13 + 11 + 6 = 36 |

**Plus the §5 roster: 17 named classes with no solve.** Four of those 17 already
appear above as sub-rows (S11 fluid–solid CHT, S16 K0d, S18 K2c-B raised floor,
S27 participating media); **13 are additional** and appear nowhere in §3, because
there is nothing to describe. **Total distinct thermal classes with no solve:
6 + 13 = 19.**

### 8.3 The headline for the verification supervisor

- **One clean gate PASS in the whole family**: K0c laminar square cavity,
  **0 of 20 graded rows failed**, largest deviation **1.139 %** on a **3 %**
  band, **41.73 core-min** (+ ~44.3 discarded, reconstructed not measured).
- **Twelve of eighteen cells have NEVER RUN.**
- **Eleven sub-rows are NOT HELD** — and NOT HELD here means *the lab measured it
  and the answer is no*, with the model-error attribution to prove it, not
  *nobody looked*.
- **No turbulence model has ever passed a turbulent thermal gate against
  experiment.**
- **No forced-convection heat-transfer PASS with a converged triple exists**:
  T1b's triples diverge, T3 is NOT A RESULT at gate (1), K0e cannot be gated by
  construction.
- **Every DC quantity class a data centre is actually specified on — inlet
  temperature, recirculation, stratification height, transient response — is
  PENDING.**

---

## 9. Disagreements this lane REPORTED rather than resolved

**Where a summary and a record disagree, the record wins.** Four were found.

| # | disagreement | what the RECORD says | what the SUMMARY says | disposition |
| --- | --- | --- | --- | --- |
| **1** | **K0c denominator, 20 vs 24** | `K0c_RESULTS.md:546` dated correction 2026-08-18: **0 of 20 GRADED rows, 4 identity rows reported and counted toward nothing.** `THERMAL_CAPABILITY_STATE.md:33` agrees: "0 of 20 … (D419 corrected the denominator from 24)" | `LAB_INVENTORY.md` §6 (`529bfc08`): *"the K0c denominator (24 vs 20) differs between the results file and the capability state"* | **RESOLVED, and the summary's characterisation is itself inaccurate.** The two files **agree**; what differs is the results file's superseded **headline** against its own dated correction, which is how rule 6 requires a frozen record to be repaired. **Use 0 of 20.** |
| **2** | **K0cX denominator, 42 vs 60** | `K0cX_RESULTS.md:422` dated correction 2026-08-18: **"GATE FAIL, 24 of 42"**, superseding "24 of 60"; D420 applied as six lines, **evidence base overstated by 43 %**; `THERMAL_CAPABILITY_STATE.md:35` agrees | `LAB_INVENTORY.md` §6: *"K0cX cross-geometry GATE FAIL for all three models (24/60 rows…)"* | **The summary is STALE.** Same defect shape as #1: eighteen non-discriminating rows (R3, R7, R9 — which passed for every model on every mesh **and for the laminar control**) left the tally and **no verdict, failure count or number moved**. **Use 24 of 42.** |
| **3** | **D389 status** | `docs/DOCKET.md` D393: *"**SETTLES D389**"*; repair live at `docs/physics_rules.yaml:255` (`heat_monitor_normaliser: range_spanned_over_run`); 49-case re-grade performed; **exactly two verdicts moved, both K2b's**; K0c's 11 and K2e's 30 **unchanged** | this lane's own brief: *"D389 is OPEN and deliberately unrepaired … changing it re-grades the whole thermal corpus and moves verdicts across K0c / K2e / KV1"* | **The brief is stale against the record.** Carried in §6 with both the original defect and its settlement. **No cell's verdict in this contribution depends on the mean-normalised S13.** |
| **4** | **DC certificate line count** | `DC_CERTIFICATE_TEMPLATE.md:70` (`5a197a41`): *"**Eleven lines**, of which two are GATE REACHED and **nine** are PASS"*; the §2 table carries 11 rows | this lane's brief and `LAB_INVENTORY.md` §6: *"ten backed lines (8 PASS, 2 GATE REACHED)"* | **The summaries are stale by one line** — the E4a2 fan-BC line. **The substantive claim survives**: still none turbulent, none mixed-convection, none buoyant; all four DC quantity classes still PENDING. **Use 11 lines: 9 PASS, 2 GATE REACHED.** |

**Every census integer in §8 is derivable from the id lists printed beside it**,
so a verification lane can re-check the arithmetic without re-reading the
records. That is deliberate: D414 and D420 were both inflated denominators that
nobody caught **because nothing failed**, and a census that cannot be re-derived
is the same shape of defect.

---

## 10. Scope, and what this lane did NOT do

- **`docs/COVERAGE_MATRIX.md` was NOT created, read-modify-written, or touched in
  any way.** It did not exist on disk at the time this lane began (checked). It
  is the **verification supervisor's** file.
- **No K0d file was written, created or edited.** A K0d pre-registration is being
  armed in a parallel lane; it is referenced here only as *"prereg being armed,
  unfired"*.
- **No solver was touched, started or stopped.** The T1b L4 arm states in §4.3
  were read from `system/controlDict`, directory listings and completion markers.
  Total compute spent by this lane: **zero core-minutes.**
- **No run was re-executed and no comparator was re-run.** Every number here is
  quoted from a record on disk, with that record's path and the sha that last
  changed it.
- **Nothing was sent, filed, uploaded, registered, posted or commented anywhere
  outside this box** (rule 7). The T10a-VF upstream draft remains **NOT FILED**.
- **No repository path cited here is a scratch path** (rule 13).
