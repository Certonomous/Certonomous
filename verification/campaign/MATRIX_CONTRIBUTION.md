# MATRIX_CONTRIBUTION — the cfd family's rows for the lab coverage matrix

**What this file is.** The cfd line's offered rows for the lab coverage matrix the
**verification** team owns at `docs/COVERAGE_MATRIX.md`. That file is **not cfd's**.
This contribution **does not create, write to, edit or touch it**. The owner re-maps,
re-scores, merges or rejects any row here without asking.

**Version 2, 2026-08-25. THIS IS A REBUILD, AND THE REASON IS A DEFECT FINDING
AGAINST VERSION 1.** Version 1 (blob `9060e751`, 521 lines, 19 rows, landed at HEAD
`af2b23b0`) was audited by the verification team and found **"selected, not
exhaustive, and several are families rather than rows."** The cfd supervisor accepts
that finding without argument. Version 1's rows are not deleted from the record: §5
below strikes every one of them individually, says what it became, and says why any
tier that moved, moved. **A tier that moved did so because the OWNER'S RUBRIC MOVED
and version 1 applied a struck ruling** — see §0.1, which is the single most
consequential correction in this file.

Written by a cfd `lab-lane` at the cfd supervisor's direction. **ZERO SOLVER
COMPUTE** — no solver, no mesh, no MPI rank, no training. Cost is closed out in §8.

Verdict words are the fixed `CLAUDE.md` rule-1 vocabulary (`PASS` / `GATE REACHED` /
`GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`). Tier words are the matrix's
five (`HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` / `NEVER RUN`). **These are
two different vocabularies and `GATE REACHED` appears in both meaning different
things** (`COVERAGE_MATRIX.md` §1.1). Every row prints the two separately.

**Submissions are parked.** Nothing here is filed, sent, uploaded or registered
anywhere outside this box.

---

## 0. The rubric this file applied — the OWNER'S, and the CURRENT owner's

### 0.1 THE CORRECTION THAT MOVES THE MOST CELLS: version 1 scored under a STRUCK ruling

`docs/COVERAGE_MATRIX.md` §2.2 has been amended twice since version 1 was written,
and version 1 scored against the **original** Ruling 1 — the one the owner has since
struck twice, in its own words, "*left standing above*" so a reader can see what
changed. Version 1's §0.1 quotes the struck text verbatim:

> *"**Ruling 1** — `GATE REACHED` when **at least one** of V / G / P is missing, and
> the row names **every** missing letter; `SURVEYED` is reserved for rows with **no
> pre-registered gate at all**."*

**That is not the rule any more.** The owner's Ruling 1 now stands in its third form,
and the owner states why each earlier form broke — on a real row, not on an argument.
Quoted from `COVERAGE_MATRIX.md` §2.2, "Ruling 1 — SECOND AMENDMENT, 2026-08-25. The
tier counts GREEN columns, not missing ones":

| green columns | tier |
| --- | --- |
| **3** | **HOLDS** |
| **1 or 2**, under a frozen pre-registration | **GATE REACHED** — and the row names every missing letter |
| **0** | **SURVEYED** — *nothing on the V / G / P axes*, whatever lab gates the row passed |
| a green column's own gate returned FAIL, or a blocker | **NOT HELD** |
| no solve | **NEVER RUN** |

**And there is a fourth ruling version 1 never saw at all — Ruling 4, which empties
the P column.** Quoted:

> *"**Ruling: `P` is green only for a comparison against MEASURED PHYSICAL REALITY —
> an experiment or measured data — from a public primary source, with the
> pre-registration on disk. An exact solution, an analytic benchmark, a manufactured
> solution, a correlation, another code's result, or a numerical benchmark scores `V`
> if it qualifies there, and scores `P` never.**"*

**Consequence for cfd, stated first because it is the headline and it is
unflattering: cfd's one green P is withdrawn. The P column is now EMPTY across the
whole family.** Version 1 scored `P` green on row 13 (F6b periodic hills) against the
**held** limb of its three-source reattachment band. Read the prereg's own source
table (`F6b_ERCOFTAC_PREREGISTRATION.md:92-94`): the held limb — Breuer, Peller, Rapp
& Manhart (2009), x_R/h = **4.69** — is an **LES/DNS Reynolds-number series**, a
computation. The **experimental** limb is Rapp & Manhart (2011), x_R/h = **4.21**,
PIV/LDA water channel, and the lab does **not** hold it; it reached the lab through
the ERCOFTAC KBwiki, which is `SECONDARY` under the owner's Ruling 3. **So the limb
that is the experiment is not held, and the limb that is held is not an experiment.**
Under Ruling 4 that scores no P at all. Struck in §8, row 13.

The other two published rulings are applied as written:

* **Ruling 2** — an **unsettled** observed order still scores `G`, and every G-green
  row additionally discloses whether the order has settled, quoting the sequence if it
  is still moving. **No row here is called asymptotic.**
* **Ruling 3** — `P` is green only against a source the lab **HOLDS and can read**. A
  value reaching the lab through a third party is `SECONDARY` and does not score P.

And the columns themselves, unchanged, from `COVERAGE_MATRIX.md` §1:

| column | scores green ONLY when |
| --- | --- |
| **V** — code verification | there is an **exact solution**, a **manufactured solution**, or a **correlation**, and the case was compared against it |
| **G** — grid convergence | there is a **CONVERGING Roache triple**, with **GCI at Fs = 1.25** and an **observed order p** |
| **P** — validation | against **measured physical reality** from a **public primary source** the lab holds, with the **pre-registration ON DISK** |

**Every V-green cell below names WHICH of the three it is** — exact, manufactured, or
correlation — because "V" without that word is the cell that rots first.

**cfd defines nothing of its own.** Where the owner's rubric is silent, §0.2 says so
and refuses to fill the silence.

### 0.2 A GAP IN THE OWNER'S RULING 1 THAT cfd WILL NOT CLOSE, and it hits seven rows

Ruling 1's final form conditions `GATE REACHED` on **"1 or 2 [green], *under a frozen
pre-registration*"**, and glosses `SURVEYED` as **"*nothing on the V / G / P axes*"**.

**cfd holds SEVEN rows that have a green column and NO frozen pre-registration.** They
fit neither cell:

* calling them `GATE REACHED` ignores the qualifier the owner wrote into the rule;
* calling them `SURVEYED` asserts the gloss — *nothing on the V/G/P axes* — which is
  **false on its face** for a row with a green column. The strongest of the six is the
  TMR flat plate, which carries the best grid convergence anywhere in the lab outside
  the thermal family.

**This is exactly the shape of the two breaking cases that produced the owner's own
two amendments** (dafoam's 24 rows in one direction, VMFL005 in the other), and cfd is
not entitled to rule on it. **Every such row below is tiered `RUBRIC GAP — owner's
ruling required`, with both candidate tiers from the fixed five named in the cell.**
That is not a sixth tier and is not offered as one; it is an explicit refusal to
assign a tier the published rubric does not reach. The seven are collected in §8.1 so
the owner can close them in one pass.

**Note which way the ambiguity cuts.** If the owner reads the qualifier as
mandatory, all seven fall toward `SURVEYED` and cfd's `GATE REACHED` count is **1**.
If the owner reads it as descriptive, cfd's `GATE REACHED` count is **8**. **cfd does not
pick the flattering one and does not pick the harsh one.**

### 0.3 Carried forward from version 1: the Eca–Hoekstra band IS the GCI at Fs = 1.25

`COVERAGE_MATRIX.md` §4 fact 1 left open whether an Eca–Hoekstra certifier verdict is
the same instrument as a Roache triple with a GCI at Fs = 1.25. **It is answerable
from the artefact alone and the answer is yes.** From `cases/tmr/flatplate_sst.json`
(`convergence_extended.cd_triples[2]`): Cd triple `0.0028342538677 / 0.0028564381699 /
0.0028635838023`, r = 2, certifier `observed_order` **1.6344055714456223**, certifier
`reportable_band_abs` **4.244064059104043e-06**; solving the certifier's own band back
for its safety factor, `Fs = band × (r^p − 1) / |f_med − f_fine|` = **1.2500000000**.
Independently on Cf(x = 0.970084): p **1.528107096548118**, band
**5.084493331132672e-06**, `Fs` = **1.2500000000**. `band / f_fine` reproduces the
file's own `gci_fine_pct` to eight figures: **0.14820813 %** against the recorded
`0.14820813191132226` and **0.18799768 %** against `0.18799768435862288`. The code
agrees: `sdk/chief_engineer/uq.py:588` is `band = fs * abs(e21) / (r21 ** p_used -
1.0)` inside `eca_hoekstra_band`, whose signature (`:448`) defaults `fs: float = 1.25`.

**What this does NOT settle**, and the owner should not read it as settled: it is
**not the lab's Roache instrument**. `scripts/roache_triple.py` (blob
`8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`, commit `9c69a79a`) is the ported T-family
arithmetic, and **no cfd ladder has been graded by it**. Two implementations agreeing
on a formula is not one ladder graded twice.

### 0.4 STANDING CONSTRAINT — no GCI, observed order or Richardson value in this file
comes from `sdk/workflows/tmr_verification.py`

Three implementations in that file quote a negative GCI (−10.714 %) on a divergent
triple. **cfd quotes nothing from it** until verification reports. Its geometry
helpers may be used; its GCI may not. Every Roache/GCI value cfd offers comes from
`scripts/roache_triple.py` or, where a stored certifier value is quoted, is named as
the SDK certifier's and is shown in §0.3 to be the Fs = 1.25 GCI by arithmetic.

---

## 1. Scope, method, and what "exhaustive" cost

### 1.1 Territory, enumerated rather than sampled

Territory read as: `cases/` **except** `RANS_LES_closure_models/` and `dafoam/`;
`verification/runs/` **except** `T-family/`, `F14-cooling-ladder/`,
`THERMAL_K0_runs/`; `verification/campaign/`; `models/`.

**How each enumeration was made, stated per claim because the two instruments see
different things:**

* **Tracked state** — `git ls-tree -r HEAD <dir>` and `git cat-file -e HEAD:<path>`.
  Used for every "exists at HEAD" claim and every blob citation.
* **Disk state** — `/usr/bin/find` (the real binary) and `/usr/bin/grep`. Used for
  every "on disk" claim. **`grep` in this shell is a function wrapping `ugrep
  --ignore-files`**, so gitignored trees are invisible to it — `cases/mega-batch/`
  carries **9 tracked files and 1,244 on disk**, and a grep sweep sees the 9.
  `verification/runs/MESH_AUDIT_runs/` is **on disk and absent from HEAD** and was
  found by `find`, not by git.
* **Out-of-repo run trees** — `/home/ubuntu/certonomous-runs/`, walked by
  `scripts/recipe_audit.py --discover` (`os.walk`, consults neither git nor grep).
  417 case directories enumerated.

**Two deliberate exclusions, stated so a silence is not read as a zero:**

* **`cases/ansys_verification/` and `verification/runs/ansys_verification/` are NOT
  scored here** — the ansys-verification team's territory under the current roster,
  and that team files its own rows. A jurisdiction call, not a finding.
* **`sdk/` is not cfd territory** and no `sdk/` row is offered. §0.3 and §0.4 cite
  `sdk/` files as *evidence about instruments*, which is a reading, not a claim.

### 1.2 The filing hazard that shapes this survey

**The verdicts live in `verification/campaign/*.md`, one level up from the run
trees.** Most directories under `verification/runs/` carry no README, no RESULTS and
no marker: `verification/runs/F12_runs/` holds a `reference/` directory and nothing
else; `verification/runs/MESH_AUDIT_runs/` holds only `log.checkMesh` files. **An
empty run directory here is not evidence that a family is ungraded**, and the reverse
also holds — a fat `verification/campaign/` is not evidence that a family ran.

### 1.3 Read depth, disclosed per row group

A row's evidence is only as good as what was read. Rows carried over from version 1
rest on records that version's lane read in full and this lane re-checked against
HEAD. **Rows new in this version marked `[head-read]` in the evidence cell rest on the
record's opening section and its cited path, not on a full read.** That is stated
rather than hidden, and a `[head-read]` row is offered to the owner as an enumeration
with a citation, not as an audit.

---

## 2. The rows — physics campaigns, the F family

`F13` **does not exist in this lab.** Searched at HEAD across `docs/`,
`verification/`, `cases/` and `models/`: the only hits are dafoam `D13`/`F13` strings
inside `cases/dafoam/`. `F14` is the heat-transfer team's cooling ladder and is out of
cfd territory. The F family in cfd territory is **F1–F12**, and every one of them has
a row.

| # | row | V | G | P | gate VERDICT (rule-1) | matrix TIER | evidence, by path |
|---|---|---|---|---|---|---|---|
| **C-1** | **F1 — ONERA M6 transonic wing, 3D** | NO | NO | **NO — and this row is the direct test of the lab's second standing fact.** The gate IS against a public primary **experiment** (Cp from AGARD AR-138). **There is no pre-registration on disk.** This lane re-enumerated every `*PREREGISTRATION*` in cfd territory — **42 in `verification/campaign/` plus 2 under `verification/runs/` (`FPE_DIAG_runs`, `GEN_ALT_runs`) = 44** — and not one registers a gate on F1 or ONERA M6. **CORRECTED 2026-08-25, and the correction is against this lane's own file.** Version 1 stated that the string "ONERA" appears *"in exactly one of the 44"*, `F12_PREREGISTRATION.md:64`. **That is FALSE and this version repeated it before checking.** Re-measured over all 44 blobs with `/usr/bin/grep`: it appears in **two** — `F12_PREREGISTRATION.md:64`, a cost-basis cross-reference (*"F1 (ONERA M6, 3D, 399k cells) was recorded GATE REACHED"*), and `CUBE_SAIL_DRAW_SCATTER_PREREGISTRATION.md:107`, a **rationale sentence for a mesh-certification ordering** (*"both ONERA M6 members I touched today were quarantined with no certificate at all until certified"*), which registers a gate on the **cube and sail** ladders, not on F1. **The load-bearing claim survives the correction and is what was actually checked: not one of the 44 registers a gate on F1 or ONERA M6.** The count beside it did not, and a precise-sounding figure carried forward unverified is exactly the cell this file warns about elsewhere. | **GATE REACHED**, 127.5 core-min: Cp RMS 0.049–0.114, shock within ±0.02–0.10 x/c, CD 0.02299556, CL 0.31311589 | **SURVEYED** (0 green) | `verification/campaign/A3_onera_m6_plateau.md`; `verification/campaign/3D_CAMPAIGN_CASE_SELECTION_MEMO.md`; mesh checks only at `verification/runs/MESH_AUDIT_runs/2026-08-08/mesh-cache__onera_m6__polyMesh.log.checkMesh` |
| **C-2** | **F2 — transonic NACA0012, 2D** | NO — the reference is a published **inviscid AGARD shock position** used as a validation target, not an exact solution the code is verified against | NO | NO — no pre-registration | **PASS (banded, resolution-limited)** — shock at x/c = 0.556 against ~0.60, **detector resolution ±0.052 x/c and the deviation NOT RESOLVED** | **SURVEYED** (0 green) | `verification/campaign/F2_transonic_naca0012.md`. A separate finding recorded honestly against the auditor: the "misdescribed as RAE2822" defect **does not hold** — every record naming F2 names it a NACA0012 |
| **C-3** | **F3a — supersonic wedge, oblique shock** | **GREEN — EXACT SOLUTION.** θ-β-M relations computed in `verification/runs/F3_runs/exact_theory.py` **before any CFD ran**, verified first against the NASA GRC wedge validation page on **all five** quantities to 6 significant figures. Solver run **inviscid (μ = 0)** so it solves the Euler equations the theory assumes | NO — three levels exist (1,800 / 7,200 / 28,800 cells, r = 2) but **no Roache triple, no GCI, no observed order anywhere in the family**: `observed_order`, `gci*` and `richardson` appear **zero times** in `F3_supersonic_exact_theory.json` | NO — exact theory is not the world, and the landed record carries no pre-registration | **PASS** — p2/p1 0.01–0.07 %, β within gate | **RUBRIC GAP — owner's ruling required** (1 green, no frozen prereg; candidates `GATE REACHED` missing G+P, or `SURVEYED`) | `verification/campaign/F3_supersonic_exact_theory.md` + `.json`; `verification/runs/F3_runs/exact_theory.py` |
| **C-4** | **F3b — supersonic cone, Taylor–Maccoll** | **GREEN — EXACT SOLUTION.** From-scratch Taylor–Maccoll ODE shooting integrator, same file, same pre-CFD verification | NO — as C-3 | NO — as C-3 | **PASS** — pc/p1 0.19–0.29 %, β 2.1–3.9 % | **RUBRIC GAP** (candidates as C-3) | as C-3 |
| **C-5** | **F3c — supersonic diamond airfoil, shock-expansion** | **GREEN — EXACT SOLUTION.** Prandtl–Meyer function and shock-expansion wave drag; PM(M=2) = 26.3798° with the inverse round-trip to 1e-13 | NO — as C-3 | NO — as C-3 | **PASS** — cd 0.18–0.26 % | **RUBRIC GAP** (candidates as C-3) | as C-3 |
| **C-6** | **F3 conversion — ARMED AND UNFIRED** | — | — | — | none — **`PENDING`**, zero compute | **NEVER RUN** | `verification/campaign/F3_CONVERSION_PREREGISTRATION.md`, **FROZEN at `2bf4915a`**. Verified on disk by this lane: `verification/runs/F3_runs/conversion_2026-08-24/` holds `rerun_f3.py` and `grade_f3.py` and **nothing else** — no `runs/` subtree (the exact path the freeze condition names), no case directory, no `log.rhoCentralFoam`. **Firing it converts C-3/C-4/C-5 out of the rubric gap** |
| **C-7** | **F4 — hypersonic blunt body, 2D cylinder M6–8** | **GREEN — CORRELATION.** Billig (1967) shock-standoff via Anderson, *Hypersonic and High-Temperature Gas Dynamics* 2nd ed. Eq. 5.37, and modified Newtonian surface pressure Eqs. 3.15–3.19. The coefficient was pulled **from the primary textbook page image, not from recall**: web search returned **4.76**, the printed value is **4.67**, and the record says so. **This family is genuinely ONE row** — standoff and Cp are two quantities on one case, not two gradeable cases | NO — `observed_order`, `gci*`, `richardson` appear **zero times** in `F4_hypersonic_blunt_body.json` | NO — a correlation is code verification, not validation; no pre-registration | **GATE REACHED, both gates PASS**, 14.66 core-min: standoff **+0.7 % to +2.3 %**, Cp RMS **3.87–3.91 %** | **RUBRIC GAP** (1 green, no frozen prereg; candidates `GATE REACHED` missing G+P, or `SURVEYED`) | `verification/campaign/F4_hypersonic_blunt_body.md` + `.json`; `verification/campaign/CAMPAIGN_STATUS.md`. **Caveat that must survive any conversion:** the M = 8 standoff is **not resolved above the detector's noise**, and the standoff detector carries a documented resolution-dependent bias |
| **C-8** | **F4-SIGFPE steps 0 and 1 — solver forensics** | NO — forensics on a floating-point exception; no exact, manufactured or correlation reference | NO — no grid ladder | NO — nothing compared to the world | Graded against a frozen pre-registration. **THE HEADLINE IS CONTINGENT ON A RULING THAT IS SANAA'S AND IS `PENDING`**: prereg §14.2 rules that §8 grades **event 1**; the record prints both readings and states that eliminating mechanism #7 *"is CONTINGENT ON THE EVENT-1 READING. Under event 2 it is not licensed at all."* Under event 2, §8.1 returns `BASELINE-NOT-RECOVERED` and the discrimination question is **`NOT A RESULT` whatever Step 1 showed**. The supervisor **CONTESTS** the audit's `NOT A RESULT` recommendation; the ruling is Sanaa's and is `PENDING` | **SURVEYED** (0 green) — **and the tier cannot move until Sanaa rules** | `verification/campaign/F4_SIGFPE_STEP01_RESULTS.md` (commit **`5b5f5183`**) against `F4_SIGFPE_STEP01_PREREGISTRATION.md`. Measured: event-1 `nLow` first differs at block 1, max \|Δ\| **18 cells (0.06 % of the mesh)**; event-2 `nLow` differs in **1,953** blocks. Cost close-out: predicted 9.316 core-min, actual **9.8560**, ratio **1.0580×**, plus **0.4468 core-min wasted** on two control twins — waste named separately, not absorbed |
| **C-9** | **F5a — unsteady 2D cylinder, Strouhal, Re 100–180** | **NO — contested, and the reason is Ruling 3.** The comparison is against a **correlation** (Roshko / Williamson), which is V-green on its face, **but `VERIFICATION_CHARTER.md` §6b records F5a's reference as `NOT OBTAINED` as a primary — what is held is SECONDARY, reproduced as a figure in a 2014 thesis** — graded *BANDED and LOWER CONFIDENCE*. Ruling 3 is written about P; **this lane scores V as NO on the same logic rather than take the more favourable reading, and flags that the owner may rule the other way** | NO | NO — `SECONDARY` does not score P, and the 2026-07-29 record carries no pre-registration | **PASS** — Strouhal within **0.7–4.6 %** across Re = 100–180 | **SURVEYED** (0 green) | `verification/campaign/F5a_cylinder_reynolds_ladder.md`; case definition at `cases/unsteady-cylinder/re100/case/`; `docs/charters/VERIFICATION_CHARTER.md` §6b. **What moves it: obtain and hold Williamson's primary, title-page verified** — that alone converts V |
| **C-10** | **R7 — Strouhal mesh-spacing sensitivity at Re 1000** | NO | NO — a sensitivity sweep, not a Roache triple | NO | Pre-registered at **`14eb8f11`** and answered — *"the low rung is robust, and it is not close"* | **SURVEYED** (0 green — a frozen gate that tested none of V/G/P, which is exactly what `SURVEYED` now asserts) | `verification/campaign/R7_STROUHAL_SPACING_PREREGISTRATION.md`, `R7_STROUHAL_SPACING_RESULTS.md` |
| **C-11** | **F5b — pitching NACA 0012 dynamic stall** | NO | NO | NO — the Gate rung is **`BLOCKED`** on a reference that is **`NOT OBTAINED`**: McAlister, Carr & McCroskey, NASA TP-1100 (1978), case (e). §6b's four fields travel with it | **`BLOCKED`.** The Physics rung's pre-registration is drafted and revised (Revision 2 at HEAD **`e9737c5f`**) but the **launch was denied by the permission system at ~17:45Z**: *"launch BLOCKED on a permission decision that is Sanaa's alone."* | **NOT HELD** (a blocker, in the tier definition's own words) | `verification/campaign/F5b_PHYSICS_PREREGISTRATION.md`; `verification/runs/F5b_runs/`. **The honesty clause that must travel with this row: the wrapper assertions are UNEXERCISED.** The record says so at `:1143` — A1 (run-directory absence), A2 (E2–E5 porcelain and md5s) and A3 have **never been run**. They are **descriptions of committed code, not measurements.** That is the planted-zero principle applied to a guard: an assertion nobody has watched fail is not evidence |
| **C-12** | **F5c — backward-facing step vs Driver & Seegmiller (1985)** | NO | NO | NO — no frozen gate on agreement with the experiment | **GATE NOT REACHED**, and its history is the sharpest self-correction in cfd's record. The 2026-07-29 reading of **0.5–1.5 H (a 4–12× miss)** was **withdrawn by the 2026-08-08 amendment as a `wallShearStress` sign-convention defect — "the 4–12× reattachment error never existed"** — corrected to **x_r/H ≈ 5.6 = −10.5 %** against **6.26 ± 0.10** | **NOT HELD** | `verification/campaign/F5bc_unsteady_statistics.md`; `verification/runs/F5c_runs/` |
| **C-13** | **F5c Stage A — does the −10.5 % regenerate?** | NO | NO | NO | **NOT REGENERATED** — A2 returns **6.996**, **1.396 H** from 5.6 against a pre-registered bar of **0.81 H**, firing pre-registered outcome **O3**: *"the ≈5.6 lives only in a committed docstring; if it does not come back from the configuration it is attributed to, the −10.5 % retracts to unmeasured."* **F5c's headline number is currently `unmeasured`, by its own pre-registered rule** | **NOT HELD** | `verification/campaign/F5C_STAGE_A_RESULTS.md`, prereg **`3734270d`** |
| **C-14** | **F5c lever isolation — was the attribution right?** | NO | NO | NO | **MISATTRIBUTED.** The **1.313 H** credited to SIMPLEC was **relaxation**: \|Δx_r/H\| **2.911** against a **6.560** bar for the algorithm alone (**NOT attributable**) versus **4.224** against a **2.578** bar for relaxation alone (**ATTRIBUTABLE**, 1.64× the bar) | **NOT HELD** | `verification/campaign/F5C_LEVER_ISOLATION_RESULTS.md`, prereg **`9eaefc7f`** |
| **C-15** | **F6a — NASA wall-mounted hump, baseline** | NO | NO | **NO — and this is the shortest path in cfd territory to a first green P, so read the cell rather than the letter.** The reference **experiment primary IS HELD ON DISK**: `docs/papers/benchmark_test_cases/greenblatt_et_al_cfdval2004_hump.pdf` **with its `.txt` sidecar**. What is missing is only a **frozen pre-registration gating agreement with it** — the 2026-07-29 agreement numbers were ungated. **VERIFY:** this lane did **not** title-page verify that PDF (rule 15) | **GATE REACHED**, ungated: separation **−1.59 %**, reattachment **+13.95 %** | **SURVEYED** (0 green) | `verification/campaign/F6_closure_aligned_flows.md` + `.json`; `verification/campaign/F6a_epistemic_band.md` |
| **C-16** | **F6a diffusion hypothesis — the k-SST limiter** | NO | NO | **NO, and the prereg says so itself.** The gates are a **probe of the limiter mechanism, not agreement**: *"relative to 1.100. This is a probe of the limiter mechanism, not tuning"* (`:48`), and *"No coefficient will be tuned to 1.100"* (`:140`). A mechanism gate frozen before the run is excellent practice and it is **not a P gate** | Graded per-model against a prereg committed **`4ec43da4`** BEFORE any run in the study executed | **SURVEYED** (0 green) | `verification/campaign/F6a_DIFFUSION_RESULTS.md`, `F6a_DIFFUSION_PREREGISTRATION.md` |
| **C-17** | **F6a epistemic band and propagation** | NO | NO | NO | Recorded; a scoping and banding record rather than a gate on the world | **SURVEYED** (0 green) `[head-read]` | `verification/campaign/F6a_EPISTEMIC_CASE.md`, `F6a_epistemic_band.md`, `F6a_epistemic_propagation.md` |
| **C-18** | **F6b — ERCOFTAC periodic hills, reattachment** | **NO.** F6b's internally-named "Gate V" is a **mesh-reproduction identity** — our own mesh from the published ERCOFTAC hill polynomial reattaching at **x/h = 7.6472** against the benchmark's shipped-mesh **7.6439**, **0.043 %** against a pre-registered ±5 %. An excellent instrument check and **not** the chief's V: no exact solution, no manufactured solution, no correlation. **The vocabulary collision `COVERAGE_MATRIX.md` §2 warns about appears inside a single record here** | NO — three rungs exist on the hill family but no converging triple with a GCI and an observed order is on record | **NO — WITHDRAWN FROM GREEN, see §0.1 and §8.** The band **[4.21, 4.70]** has its **experimental** limb (Rapp & Manhart 2011, 4.21) **secondary and not held**, and its **held** limb (Breuer et al. 2009, 4.69) is an **LES/DNS computation**. Under Ruling 4 neither scores P | **GATE REACHED (prediction falsified).** Reattachment **x/h = 7.6472** against **[4.21, 4.70]** — **+63 % to +82 %** | **NOT HELD** — the P gate this row armed under a pre-registration frozen before the first iteration returned a falsified prediction. *(Under the strictest reading of Ruling 1's FAIL clause — "a green column's own gate" — a row with no green column cannot reach NOT HELD by that clause and would fall to `SURVEYED`. cfd enters the **non-flattering** reading and names the alternative rather than choosing the kinder one.)* | `verification/campaign/F6b_ERCOFTAC_PREREGISTRATION.md` (committed **`31b0be16`** before the first iteration), `F6b_ERCOFTAC_RESULTS.md`; held paper `docs/papers/benchmark_test_cases/breuer_peller_rapp_manhart_caf2009_periodic_hills.pdf` + sidecar. **This is NOT a convergence artefact:** `F6b_RELAXATION_INVARIANCE_RESULTS.md` re-solved the medium rung at two further relaxation settings and got **7.6480** and **7.6458** against **7.6472** — **0.0105 %** and **0.0183 %** against a 0.5 % bar. **The +63 % miss is the model's, not an untested switch** — a defensible scientific position, not a shortfall |
| **C-19** | **F6b QCR2000 arm** | NO | NO | NO | **OUTCOME N — the null generalises.** `kOmegaSSTQCR` the single change on the 15,600-cell mesh | **SURVEYED** (0 green) | `verification/campaign/F6b_QCR_RESULTS.md`, `F6b_QCR_PREREGISTRATION.md` |
| **C-20** | **F6b relaxation invariance** | NO | NO | NO | Pre-registered at **`ce0b14be`**; agreement to **0.0105 %** and **0.0183 %** against a 0.5 % bar. **Convergence evidence that never consults a residual** — the instrument, not the physics | **SURVEYED** (0 green) | `verification/campaign/F6b_RELAXATION_INVARIANCE_RESULTS.md` |
| **C-21** | **F6d — random-matrix / maximum-entropy model-form UQ on periodic hills** | NO | NO | NO | The pre-registered validity gate **FIRED**: control `d0.2_s000` moved **−0.491 x/h**. The record's own discipline is the finding — *"a gate that can be [explained away after the fact] is not a gate"* | **NOT HELD** — a pre-registered validity gate fired | `verification/campaign/F6d_random_matrix_uq.md` + `.json`, `F6D_OPTION_A_PREREGISTRATION.md`, `F6D_OPTION_A_RESULT.md`, `F6D_ENSEMBLE_CONVERGENCE_AUDIT.md`, `F6D_COLLISION_INDEPENDENCE_CHECK.md`. Framework: Xiao, Wang & Ghanem, arXiv:1603.09656 |
| **C-22** | **F7 — free-surface dam break vs Martin & Moyce (1952)** | NO | NO | NO — §6b adjudicates this row explicitly: no tabulated Martin & Moyce data could be located and the lab **digitised a 2021 figure at 600 dpi** (arXiv:2108.08769 Fig. 7). Recorded **`NOT OBTAINED`** as a primary; under Ruling 3, `SECONDARY` | **GATE FAILED.** Front position Z(T): **+8.2 % mean / +11.0 % max** against a declared **5 %** tolerance — improved from the original **+13.6 % / +21.3 %** by the R1 audit of 2026-07-30, which also **retracted** the originally reported sign flip and root cause. **389.8 core-min** | **NOT HELD** | `verification/campaign/F7_marine_free_surface.md` + `.json`. **A quality note the owner should see:** the digitisation was **programmatic** — axis-tick pixel clusters for calibration, cross-marker centroid detection, *"not manual eyeballing"* — with a stated digitisation uncertainty. **The reference is secondary, and the handling of a secondary reference here is exemplary.** Two different statements; the tier turns on the first |
| **C-23** | **F7a re-gate — the measurement definition, pinned** | — | — | — | **Zero compute.** `F7a_REGATE_SPEC.md` frozen 2026-08-11 pins the measurement definition contractually so no future re-gate can drift it; reading A on the original gate case gives **+13.4 %**, reproducing the earlier figure | **SURVEYED** (0 green — an instrument contract, correctly ungreen) | `verification/campaign/F7a_REGATE_SPEC.md`, `F7a_REGATE_PREREGISTRATION.md` |
| **C-24** | **F7b / F7c — Wigley hull and DTMB 5415** | NO | NO | NO | **`BLOCKED`** behind C-22 | **NOT HELD** (a blocker) | `verification/campaign/F7c_DTMB5415_STAGING_PLAN.md`; `verification/campaign/NAVAL_CAPABILITY_GAP_MAP.md` |
| **C-25** | **F8 — UAE Phase VI rotor, MRF, 3D rotating machinery** | NO | NO | **NO — not for want of a pre-registration, but for want of a number to grade.** The prereg was written 2026-08-07 **before the force history was read** and discloses honestly what the agent had already seen. Reference **Hand et al. (2001)**, 800 N·m at 7 m/s, flagged **secondary tier in the record itself** | **NO VERDICT — unconverged forces are not gateable; MRF branch closed.** 230,135 cells, run to t = 1500 and restarted to t = 3000, `SIMPLE solution converged` appearing **zero times in either log**. Torque band **7,679 N·m peak-to-peak = 960 % of the reference** against a registered cap of **50 %**. 5.8 core-min | **NOT HELD** | `verification/campaign/F8_MRF_HAND2001_GATE.md`; `verification/runs/F8_runs/`. *"No verdict"* is the correct output and the branch was **closed** rather than left to be quietly reopened |
| **C-26** | **F9 — pulsatile valve orifice vs the Womersley solution** | **GREEN — EXACT SOLUTION** (Womersley 1955's analytic oscillatory pipe-flow profile). Gate 1 **PASS** at **−1.6 % / +0.2 %**. **VERIFY:** this lane did **not** locate a held copy of Womersley (1955) under `docs/papers/` and did **not** title-page verify one (rule 15). **If the paper is not held, Ruling 3's logic may bear on V as well as P and the owner should re-score this cell** | NO — no grid ladder, no observed order, no GCI | NO — no pre-registration document exists on disk for F9 in `verification/campaign/` | **GATE REACHED, mixed (2 PASS / 1 FAIL-with-cause-understood)**, < 35 core-min: Gate 1 **PASS**; Gate 2 **GATE FAIL** at 20–414 %, cause identified; Gate 3 **−94.0 % vs the ROM**, described by the record as pre-registered though **no pre-registration file is on disk** | **RUBRIC GAP** (1 green, no frozen prereg; candidates `GATE REACHED` missing G+P, or `SURVEYED`) | `verification/campaign/F9_pulsatile_valve.md` + `.json`; `verification/runs/F9_work/`; figures at `cases/valve/` |
| **C-27** | **F10 — 3D viscous RANS Ahmed body, the mega-batch family** | NO | NO | NO | Family added to `sdk/workflows/mega_batch.py` and measured through the real dispatch against a **scratch** ledger. **A y+ defect was found and fixed and the record says so at the top**: 17 of 52 F10 evaluations failed the y+ gate at the top of the Re range on the fixed `refinement=2` mesh; the mesh now follows Reynolds number | **SURVEYED** (0 green) `[head-read]` | `cases/mega-batch/F10_3D_VISCOUS_FAMILY.md`, `cases/mega-batch/F10_YPLUS_FIX.md` |
| **C-28** | **F11 — 2D lid-driven cavity vs Ghia, Ghia & Shin (1982)** | **NO.** The lid-driven cavity has no exact solution and none was used; Ghia et al. is a **computational benchmark**, which the record is careful about — it carries a section headed *"A definition that has to be stated precisely: this is VERIFICATION, not VALIDATION."* Under Ruling 4 a numerical benchmark scores **P never**, and it is not one of V's three instruments either | **NO, by the record's own disclosure.** Its grid section is headed *"Grid sensitivity, reported honestly (not claimed as clean Richardson convergence)"* — two mesh resolutions per rung, no triple, no GCI, no observed order | NO | **GATE REACHED**, both rungs (Re = 100 and Re = 1000), both quantities, both mesh resolutions | **SURVEYED** (0 green) | `verification/campaign/F11_lid_driven_cavity_ladder.md`; `verification/runs/F11_runs/` |
| **C-29** | **F11 conversion — FROZEN, unfired** | — | — | — | none — **`PENDING`**, zero compute | **NEVER RUN** | **CORRECTION TO VERSION 1, ROW 12.** Version 1 recorded that this pre-registration *"does not yet exist on disk"*. **It does.** `verification/campaign/F11_CONVERSION_PREREGISTRATION.md`, landed at commit **`157793db`**, *"frozen before any solver in this conversion has started"*, with the §2b.1 condition **checked rather than asserted** — `verification/runs/F11_runs/conversion_2026-08-25/runs/` does not exist, and the launcher **refuses (rc = 3)** any case directory that already exists, so the condition is **enforced** rather than stated once. **Nobody's error: concurrent lanes.** Version 1's cell was true when written |
| **C-30** | **F12 — RAE 2822, AGARD AR-138 Case 9** | NO — nothing has run | NO — nothing has run | NO — **but only one thing is missing, and it is the solve** | none — **`PENDING`** in the rule-1 display/queue sense. Not a softened `GATE FAIL`; nothing has been graded | **NEVER RUN** | **The most actionable row in the file.** Prereg on disk and frozen (`verification/campaign/F12_PREREGISTRATION.md`, *"Written 2026-07-30, before any solver was launched on this case"*), and it does the hard part properly: it solves **two** conditions because *"the published corrected conditions for this case do not agree and picking one silently is the classic way to be confidently wrong here"*. **Reference data already on disk:** `verification/runs/F12_runs/reference/` holds `rae2822_case9_cp_upper.dat`, `rae2822_case9_cp_lower.dat`, `rae2822_coordinates.dat`, the NPARC geometry files and `decode_tape.py`. **AGARD AR-138 is a public primary EXPERIMENT and the lab HOLDS the tape** — which under Ruling 4 is the rare cfd row where a green P is reachable at all. **VERIFY before launching:** `verification/runs/F12_runs/` currently holds only `reference/`, so the freeze condition still holds — **re-check it in the same shell invocation as the launch**, not from this file |

---

## 3. The rows — grid-ladder and workshop campaigns

**Version 1 folded every 3D ladder into one cell (its row 9). That was the audit's
"families rather than rows" finding at its worst, because the six ladders are
independently pre-registered and independently graded.** They are split here.

| # | row | V | G | P | gate VERDICT (rule-1) | matrix TIER | evidence, by path |
|---|---|---|---|---|---|---|---|
| **C-31** | **TMR 2D zero-pressure-gradient flat plate — the ONE G-green row in cfd territory** | **NO.** The reference is CFL3D and FUN3D published values from NASA's Turbulence Modeling Resource — **code-to-code**. Not exact, not manufactured, and no skin-friction correlation was compared against. Under Ruling 4, another code's result *"scores `V` if it qualifies there"* — and it does not qualify, because code-to-code is none of V's three instruments | **GREEN.** Finest triple **137×97 / 273×193 / 545×385** (13,056 / 52,224 / 208,896 cells), r = 2 at every step. **CONVERGING**: Cd `0.0028342538677 → 0.0028564381699 → 0.0028635838023`, monotone, increments shrinking at **all four** ladder steps — 1.1248e-4, 5.3084e-5, 2.2184e-5, **7.1456e-6**. **Observed order** Cd **1.6344**, Cf(0.970084) **1.5281**, both inside (1, 2). **GCI at Fs = 1.25**, recovered from the artefact in §0.3 rather than assumed: **4.244e-6 = 0.14821 %** on Cd, **5.085e-6 = 0.18800 %** on Cf. **Ruling 2 disclosure — the order is NOT settled and the sequence is quoted as the ruling requires:** Cd **1.0833 → 1.2587 → 1.6344**; Cf **1.0315 → 1.1110 → 1.5281**. **This row is NOT asymptotic and nothing here may be read as saying so** | **NO, on both halves.** **No pre-registration exists on disk for this ladder anywhere** — every `*PREREGISTRATION*` in the tree was enumerated and none names the flat plate. And four documented deviations break the same-model premise: incompressible `simpleFoam` analog of the M = 0.2 case; OpenFOAM `kOmegaSST` uses **strain** production where the TMR data is **SST-V** (**vorticity** production); the top boundary is an OpenFOAM freestream condition, not a Riemann farfield; grids match TMR cell counts and r = 2 with this module's **own blockMesh stretching, not the TMR point files** | The record's own: *"the first ladder in this corpus that the Eca–Hoekstra certifier declares CONCLUSIVE, on both functionals."* **No rule-1 gate verdict exists, because no gate was ever registered** | **RUBRIC GAP — owner's ruling required** (1 green — G — and no frozen prereg; candidates `GATE REACHED` missing V+P, or `SURVEYED`). **This is the row where the gap bites hardest and §0.2 exists because of it** | `cases/tmr/flatplate_sst.json` (`convergence_extended`); case dictionaries `models/tmr/flatplate/{coarse,fine,finer,finest}/`; run logs `cases/tmr/runs/`. **TWO FRAGILITIES THAT MUST RIDE ON THE FACE OF THIS CELL. (1) Iterative convergence is on a FORCE-PLATEAU reading, not a residual reading.** The 273×193 rung ran to its **9,000-iteration cap** rather than tripping `residualControl`: 4 of 5 controls met, **Uy at 6.38e-08 misses its 1e-08 target by about 6×**; the record accepts it because Cd is flat to 2.16e-09 over the last 50 iterations. **Under `CLAUDE.md` rule 5 clause (1) — "any level not iteratively converged or not plateaued → NOT A RESULT" — a strict residual reading would VOID this triple.** The record defends the force reading with a drift-bound study: `conclusive` at the low bound, the recorded value and the iterative asymptote alike (bands 4.231e-6 / 4.244e-6 / 4.231e-6). **This is the verification team's ruling to make, not cfd's. (2) The ladder inverts on a stopping rule.** The finest rung ran **36,000** SIMPLE iterations, not the 15,000 the module asks for. At the 15,000 cap Cd was 0.0028936144511, still falling by 1.04e-5 per thousand, and the extractor **refused it, correctly**: *"Accepting the 15000 value would have put Cd 3.00e-5 (1.05 %) high and turned the finest triple's increments from shrinking into growing, reporting the ladder as a divergence."* The counterfactual is stored beside it — at the 15,000 cap the observed order is **−0.7448**, `conclusive: false` |
| **C-32** | **TMR bump-in-channel on NASA's OWN grids (W1)** | NO — code-to-code against CFL3D | **NO, and the refusal is precise.** On NASA's own bump grids (89×41 / 177×81 / 353×161, exact point-drops at r = 2): Cd total observed order **4.037**, Cd pressure **3.200**, Cd viscous **1.246** — **`conclusive: no` on all three**, failing `order_window` = [0.5, 2.5] on the first two and `extrapolation_sanity` on the third. **No reportable band is issued.** The control that makes this a property of the CASE and not of this lab: **CFL3D's own pressure ladder on those same grids fits to 2.913 and is refused by the same guard** | NO — no public primary experiment; the comparison is to CFL3D | Pre-registered **outcome 1 MET** — the item asked whether swapping only the mesh brings the pressure order back, and it does: increments become monotone (−7.250e-4, −7.886e-5) and the fit returns a finite order where there was none. **The grade is still NOT CONCLUSIVE**, and that was *"predicted and committed while the rung was still running"* | **SURVEYED** (0 green) | `verification/campaign/W1_bump_nasa_grids.md`, prereg `W1_PREREGISTRATION.md` committed **`3e252b5c`** before any solve; grid byte-provenance `models/tmr/bump/grids/PROVENANCE.md` (commit **`1b5749f0`**) — the fetched grids decompress **byte-identically** to NASA's distribution. **G IS NOT REACHABLE ON THIS GRID FAMILY BY ADDING RUNGS:** *"the mesh was the problem, and the grids are not in the asymptotic range — two separate findings, the first ours and the second belonging to the grid family, which the reference code shares."* **This row is the honest counterweight to C-31 and should be read beside it** |
| **C-33** | **TMR bump-in-channel on the lab's OWN blockMesh family** | NO — code-to-code | **NO, and worse than C-32's no.** The pressure component has **no observed order at all** — its increments change sign at every matched iteration count | NO | none registered | **SURVEYED** (0 green) | `cases/tmr/bump_sst.json`, `cases/tmr/bump_cf_profiles.json`; case dictionaries `models/tmr/bump/{coarse,medium,fine}/`; `verification/campaign/4G_tmr_mesh_aspect_ratio.md` §10 |
| **C-34** | **TMR NACA 0012 — the closure comparison case** | NO — code-to-code | NO | NO | Recorded, not gated as a ladder | **SURVEYED** (0 green) `[head-read]` | `cases/tmr/C4_naca0012_closure.json` + `.md`, `cases/tmr/naca0012_status.json`; case dictionaries `models/tmr/naca0012/`. **Disposition on record:** `verification/campaign/W1_TMR_NACA0012_DISPOSITION.md` |
| **C-35** | **R4 — Ahmed 25°, the five-rung production ladder** | NO | **NO, measured.** Five rungs at refinement ratios **1.2200 / 1.2090 / 1.2128**, Cd **0.084802 → 0.079360 → 0.073993 → 0.074882** — **non-monotone**; the fifth rung **c5 is refused as ladder evidence** because it never tripped `residualControl` and its final-window 2σ is **5.16e-03 = 6.26 % of its own value** against a 5 % ceiling, and **6× the ladder increments themselves** | NO — the pre-registration grades **ladder arithmetic**, not agreement with an experiment | Gates **G1 and G2 MET**; the ladder question itself answered in the negative. **The failure is a result** | **NOT HELD** — the class question was asked under a frozen pre-registration and **answered no, on measurement** | `verification/campaign/R4_PREREGISTRATION.md` (**`6cdf8a41`**), `R4_ASYMPTOTIC_RESULTS.md`, `R4_AHMED_C3_LEG2_RESULTS.md`; `verification/runs/R4_runs/`. `W1_AHMED_LADDER_DISPOSITION.md` then ruled the 25° slant *"answered — in the negative, on measurement"* at **0 core-minutes**, and re-priced the remaining item from **240 to about 27 core-min. That is the matrix working** |
| **C-36** | **W3 — NACA 0012 finite wing, four-rung ladder** | NO | **NO.** Observed order **24.048**, `clamped: true`, `conclusive: false`, **`uq.reportable_band` = None**, guard failing `order_window` | NO | **P1 FALSE, P2 TRUE, P3 FALSE**, scored against the frozen text without editing it. The record's own sentence: *"Removing the mixed step did not make the order sane; it made it worse."* | **NOT HELD** | `verification/campaign/W3_WING_VALID_FAMILY_PREREGISTRATION.md` (**`83e28569`**), `W3_WING_VALID_FAMILY_RESULTS.md`, `W3_GUARD_SWEEP.json`; rung cases `/home/ubuntu/certonomous-runs/w3-naca0012_wing-family/r1…r4b`. **Adjacent and NOT folded in:** `W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md` — the 3D NACA 0012 wing's **published credential does not survive its own mesh** |
| **C-37** | **W3 — NACA 4412 finite wing, four-rung ladder** | NO | **NO.** `monotone: false`, no observed order, `conclusive: false`, band None | NO | non-monotone as pre-registered | **NOT HELD** | `verification/campaign/W3_WING_VALID_FAMILY_RESULTS.md`, `W3_NACA4412_LAYERED_REPLICATES.md`, `W3_NACA4412_RESOLUTION_SCATTER.md` + `.json`; rung cases `/home/ubuntu/certonomous-runs/w3-naca4412-layered-replicates/` |
| **C-38** | **W3 — cube, settle study** | NO | NO | NO | Pre-registered at **`ee30a7c3`** before any iteration was read; **3,000 iterations, mesh reproduced the production rung EXACTLY at 299,493 cells** — the check that nothing but `endTime` changed. **The prediction failed in the direction that is the most useful thing in the run**: OpenFOAM **never** printed the convergence string | **NOT HELD** — the pre-registered prediction was falsified | `verification/campaign/W3_CUBE_SETTLE_PREREGISTRATION.md`, `W3_CUBE_SETTLE_RESULTS.md` |
| **C-39** | **W3 / CUBE_SAIL — draw-scatter on the cube and the sail** | NO | NO | NO | Pre-registered; a scatter measurement, not a ladder grade | **SURVEYED** (0 green) `[head-read]` | `verification/campaign/CUBE_SAIL_DRAW_SCATTER_PREREGISTRATION.md`, `verification/campaign/DRAW_SCATTER_RETROFIT/` |
| **C-40** | **W3 — mesh noise floor** | NO | NO | NO | **P2 carried a stated consequence** — *"If this fails, the ladders were never…"* — and the record's own summary is *"the verdict survives; the magnitude does not."* **THE NUMBER THIS ROW EXISTS FOR:** snappyHexMesh is **nondeterministic** and its draw-to-draw scatter is comparable to the ladder increments — D6 = **1.35994e-03 = 0.710×** the noise floor | **SURVEYED** (0 green — a frozen gate on the instrument, not on V/G/P) | `verification/campaign/W3_MESH_NOISE_FLOOR_PREREGISTRATION.md`, `W3_MESH_NOISE_FLOOR_RESULTS.md`, `B52_RUNG6_REPLICATE_RESULTS.md` |
| **C-41** | **W3 — draw-scatter rule replay** | NO | NO | NO | **Entry condition PASSED** — 16 of 151 fire, *"neither every record nor none"*, which is the control that the rule discriminates at all | **SURVEYED** (0 green) | `verification/campaign/W3_DRAW_SCATTER_RULE_REPLAY_PREREGISTRATION.md`, `W3_DRAW_SCATTER_RULE_REPLAY_RESULTS.md` |
| **C-42** | **W3 — race, numerical shrink of the dominant term** | NO | NO | NO | **G1 reproduction PASS, bit-identical**, 2026-08-01 14:22:03 UTC | **SURVEYED** (0 green) | `verification/campaign/W3_RACE_NUMERICAL_PREREGISTRATION.md`, `W3_RACE_NUMERICAL_RESULTS.md` |
| **C-43** | **W3 — 2D ladder refit under corrected dimensionality** | NO | NO | NO | *"non-conclusive verdicts are confirmed on the right arithmetic"* — all five workflows pass `dim = 2`; **dimensionality can only ever move a verdict through the `order_window`** | **SURVEYED** (0 green) | `verification/campaign/W3_2D_LADDER_REFIT.md` + `.json` |
| **C-44** | **W3 — mesh quality gate, two values** | — | — | — | An instrument disagreement recorded, not a physics gate | **SURVEYED** (0 green) `[head-read]` | `verification/campaign/W3_MESH_QUALITY_GATE_TWO_VALUES.md` |
| **C-45** | **W1 hump at challenge conditions + QCR2000 arm** | NO | NO | NO | Pre-registered at **`74797a57`** before any solve; two `simpleFoam` solves at 4 MPI ranks each | **SURVEYED** (0 green) | `verification/campaign/W1_HUMP_CHALLENGE_PREREGISTRATION.md`, `W1_HUMP_CHALLENGE_RESULTS.md`; `verification/runs/W1_hump_runs/sst_qcr/` |
| **C-46** | **W1 hump a1 limiter sensitivity** | NO | NO | **NO — and the near-miss is worth naming.** The gate is a **mechanism bar** (Δreatt vs the SST baseline 1.2531, bar 0.010), not agreement with Greenblatt. The a1 = 0.34 arm moved **−0.0498 toward experiment, 5× the bar** — a direction, not a validated value | Pre-registered at **`d05b83c3`** before any solve. **OUTCOME ONE — the limiter is a mechanism.** a1_034 **converged at 1,701 iterations**, separation **0.6558**, reattachment **1.2033** | **SURVEYED** (0 green) | `verification/campaign/W1_HUMP_A1_PREREGISTRATION.md`, `W1_HUMP_A1_RESULTS.md`; `verification/runs/W1_hump_runs/a1_034/` |
| **C-47** | **W1 — hardness floor ruling** | — | — | — | A ruling record, zero compute | **SURVEYED** (0 green) `[head-read]` | `verification/campaign/W1_HARDNESS_FLOOR_RULING.md` |
| **C-48** | **B-52 — rung 6 replicate** | NO | NO | NO | **VERDICT: REPRODUCE. The RECIPE owns the floor** — castellation-driven draw scatter — and the prior claim *"the gate needs work"* is **refuted with room to spare** | **SURVEYED** (0 green) | `verification/campaign/B52_RUNG6_REPLICATE_PREREGISTRATION.md`, `B52_RUNG6_REPLICATE_RESULTS.md`; `verification/runs/B52_RUNG6_REPLICATE_runs/` |
| **C-49** | **B-52 — rung 7** | NO | **NO.** The stored order went **2.253 → None**: no order fitted, *"the ladder is no longer monotone"* | NO | The alternative outcome named in **G4** is the one that happened | **NOT HELD** | `verification/campaign/B52_RUNG7_PREREGISTRATION.md`, `B52_RUNG7_RESULTS.md`; `models/curriculum/uq-studies/b52.json` `seventh_rung` |
| **C-50** | **B-52 — rung 8** | NO | **NO.** **28.675 fitted, clamped, NOT used** — the `order_window` guard fails | NO | **Verdict 1 (zero compute): the surface-resolution hypothesis is REFUTED.** Built verbatim from rung 7 (`b52.stl` md5 `c27eec6c710f0a937ec8cfe84aec2cfe`, identical) with only `blockMeshDict` changed, (55 49 82) → (69 62 103) | **NOT HELD** | `verification/campaign/B52_RUNG8_PREREGISTRATION.md` (**`48cfedfb`**, before any eighth-rung mesh existed), `B52_RUNG8_RESULTS.md`; `models/curriculum/uq-studies/b52.json` `eighth_rung` |
| **C-51** | **B-52 — turn closure, and its withdrawal** | NO | NO | NO | **P1 TRUE** — *"the branch will be INDETERMINATE"*, **stated as the expected outcome from §1's arithmetic before meshing, not as a hedge**. The record names it *"[a] failure, not a physical finding"* | **NOT HELD** | `verification/campaign/B52_TURN_CLOSURE_PREREGISTRATION.md`, `B52_TURN_CLOSURE_RESULTS.md`, `B52_TURN_WITHDRAWAL_2026-08-10.md`, `B52_TURN_CLAIM_AUDIT_2026-08-10.md`, `B52_RECIPE_NOTE_BACKGROUND_PRODUCT.md` |
| **C-52** | **R4 — Ahmed turn draw scatter, and its withdrawal** | NO | NO | NO | **No SIGNAL/NOISE verdict is claimed**, and the record says so in its own opening: the c4 CI leg was deliberately not run, and *"the exclusion row is a sensitivity and must not be read as a verdict"* | **SURVEYED** (0 green) | `verification/campaign/R4_AHMED_TURN_DRAW_SCATTER_PREREGISTRATION.md`, `R4_AHMED_TURN_DRAW_SCATTER_RESULTS.md`, `R4_AHMED_TURN_WITHDRAWAL_2026-08-10.md`, `AHMED_BODY_RECONCILIATION.md` |
| **C-53** | **DMR — double Mach reflection (Woodward & Colella 1984)** | **GREEN — EXACT SOLUTION.** Gate V, incident-shock kinematics against exact theory: **PASS on both rungs** — res120 **+0.00338 (0.15 %)**, res60 **+0.00399 (0.17 %)** | NO — two rungs (Δ = 1/120 and 1/60). **Two rungs are not a triple**, and no GCI or observed order was computed | NO — Woodward & Colella is a published **computational** benchmark, and under Ruling 4 a numerical benchmark scores P never. The structure gates against it did not hold in any case | **Gate V PASS ×2. Gate P1 GATE FAIL as registered** — the double-Mach structure detector; *"the failure is the detector's geometry, recorded"*, *"left standing as FAIL per guidelines 1.3"*. **Gate P2 split**: rung-to-rung clause **PASS** (\|χ_R1 − χ_R2\| = 0.87° ≤ 1.5°), within-rung intercept clause **GATE FAIL as registered** at both rungs | **GATE REACHED — missing G and P.** *(The only unambiguous `GATE REACHED` in the family: 1 green column, under a pre-registration frozen before any mesh existed.)* **The owner may reasonably read the two registered FAILs as the row's headline and re-tier it `NOT HELD`; the evidence is the same either way and this cell is where the disagreement should be resolved** | `verification/campaign/DMR_PREREGISTRATION.md`, committed **`74797a57`** before any mesh existed; `DMR_RESULTS.md`; `verification/runs/DMR_runs/`. Both rungs Cartesian, max non-orthogonality **0**, max skewness **6.0e-10 / 2.7e-13**. **A third rung at Δ = 1/240 on the same generator makes a triple, and the meshes are Cartesian and byte-deterministic, so the ladder is clean by construction** |
| **C-54** | **DPW8_V2 — Joukowski airfoil vs the analytic inviscid solution** | **GREEN — EXACT SOLUTION.** `joukowski_theory.py`'s `cylinder_cp(θ)` against the closed form **Cp = 1 − 4 sin²θ**: **max abs error 0.000e+00 (machine precision)**. The gate is exact-valued — a symmetric geometry at α = 0 has **CL = 0 exactly** — and the CFD returns \|CL\| = **8.26e-08** at L1 and **2.04e-06** at L3, **PASS on both**. Two independent computational paths agree at **2.753e-17** | NO — the refinement family **stops at L3**; L4, the gate rung, is **INCOMPLETE and NOT GATED**, so there is no triple | NO — no pre-registration for the gates; and **ε = 0.1 is *"NOT independently confirmed from any DPW-8/HFCFDVW committee source found in this pass"*** — a documented deviation from the committee case, which is the case P would have to be against | **PASS** (theory vs closed form), **PASS** (zero-lift gate at L1 and L3). **L4 NOT GATED**, reported as incomplete rather than graded | **RUBRIC GAP** (1 green, no frozen prereg; candidates `GATE REACHED` missing G+P, or `SURVEYED`) | `verification/campaign/DPW8_V2_joukowski.md` + `.json`; `verification/runs/DPW8_V2_runs/`. **Confirming ε from a committee source is the separate, cheap step** |
| **C-55** | **DPW8_V2 L4 divergence diagnostic** | NO | NO | NO | Landed against a frozen pre-registration. **It is about WHY L4 diverged, not about the gate**, so it does not gate C-54 | **SURVEYED** (0 green) | `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_PREREGISTRATION.md`, `DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md` |
| **C-56** | **DPW8 / AEPW4 scoping** | — | — | — | Scoping, zero compute | **NEVER RUN** `[head-read]` | `verification/campaign/DPW8_AEPW4_SCOPING.md` + `.json` |
| **C-57** | **DPW5 committee grids — the topology experiment** | NO | NO | NO | **Predictions recorded 2026-08-01T08:03:49Z BEFORE any DPW5 solve was launched**, on mesh metrics already measured: **P1** the hybrid diverges (1,810,108 of 6,216,192 faces severely non-orthogonal, 29.1 %, average 51.85); **P2** the hex survives 200 iterations at second order (11,506 of 1,937,920, 0.59 %, average 23.71) | **SURVEYED** (0 green — a frozen prediction on solver survival, testing none of V/G/P) `[head-read]` | `cases/committee-grids/PREDICTIONS.md`, `COMMITTEE_GRID_NUMERICS.md`, `cases/committee-grids/logs/DPW5_*_checkMesh.log` (105 files tracked, 105 on disk) |
| **C-58** | **HLPW6 test case 1** | NO | NO | NO | none — **`PENDING`**. The feasibility probe answers only the compute question: it **can** run at **4.55 GiB of 30.6, for 6,390 core-min at 14 ranks**. **And it may never be sent** — the entry can be prepared but not submitted, per rule 7 | **NEVER RUN** | `cases/hlpw6/FEASIBILITY_PROBE.md` + `.json`, `cases/hlpw6/SUBMISSION_GATE.md`, `cases/hlpw6/RANK_SWEEP.md`, `cases/hlpw6/rank_sweep.jsonl` |

---

## 4. The rows — instrument and diagnostic campaigns

**Version 1 folded six independently pre-registered campaigns into one cell (its row
19).** They are split here. **They are correctly ungreen on V, G and P by
construction** — they diagnose the lab's own tools rather than answering a physics
question against a reference — and **scoring them green would be the exact inflation
this matrix is built to prevent.** Their value to the lab is upstream of V/G/P.

| # | row | V/G/P | gate VERDICT (rule-1) | matrix TIER | evidence, by path |
|---|---|---|---|---|---|
| **C-59** | **4G — TMR mesh aspect-ratio diagnosis** | NO / NO / NO | The *"insane mesh aspect ratio"* is diagnosed and **cleared as a solution defect in every case tested**: NASA's own TMR NACA 0012 C-grids report max aspect ratio **20,650,841 / 26,446,227 / 29,899,837** and *"Failed 4 mesh checks"*, so **the signature cannot by itself indicate a defect anywhere**. The real defect underneath was convergence, and the `cd_tail_spread` metric certifying the ladder read **4.6e-8 against a real drift ~4000× larger** | **SURVEYED** (0 green) | `verification/campaign/4G_tmr_mesh_aspect_ratio.md` + `.json` |
| **C-60** | **GEN_ALT — generator matrix** | NO / NO / NO | **COMPLETE and GRADED, verdict `GENERATOR-OWNED`**, with the verdict rule *"committed before the answer existed"* | **SURVEYED** (0 green) | `verification/campaign/GEN_ALT_generator_matrix.md`; prereg `verification/runs/GEN_ALT_runs/GEN_ALT_PREREGISTRATION.md` — **one of only two pre-registrations in cfd territory that live under a run tree rather than in `verification/campaign/`** |
| **C-61** | **MESH_AUDIT — mesh birth certificates** | NO / NO / NO | Audited; rulings landed | **SURVEYED** (0 green) | **THIS FAMILY IS ON DISK AND ABSENT FROM HEAD** and was found by `/usr/bin/find`, not by git: `verification/runs/MESH_AUDIT_runs/2026-08-08/` holds `log.checkMesh` files and nothing that grades a ladder — including the nine for the ONERA M6 meshes that C-1 depends on, and `study-ahmed_25-medium-b37e86__constant__polyMesh.log.checkMesh`, a rung of C-63. Prose at `verification/campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md` and `verification/campaign/MESH_CERT_RULINGS_2026-08-10/` |
| **C-62** | **MODEL_FORM — the model-form band** | NO / NO / NO | Banded. **The band is the min/max across CONVERGED members of a group; an unconverged cell is excluded and NAMED** — *"the NASA hump lesson: the band that failed to contain the experiment was the band that still had an unconverged member in it."* **Mesh-gate exemption on one group (R12, ruled 2026-08-07):** max non-orthogonality **85.70°** against the **70°** hard gate, on the reference community's own NASA TMR NACA 0012 C-grid; scope **model-form banding only**, and *"this exemption never travels"* to physics gates or credential verdicts | **SURVEYED** (0 green) | `verification/campaign/MODEL_FORM_BAND.md` + `.json`, `MODEL_FORM_BATCH_DESIGN.md`; `verification/runs/MODEL_FORM_runs/`. **STANDING CAVEAT THAT GOVERNS THESE BANDS — the lever-activity caveat (charter v1.5 §9):** for **32 of 36** cells the premise that members differ *only* in the closure is asserted from the runner's construction and is **NOT proven from artifacts** — stock `simpleFoam` echoes neither `fvSchemes` nor `fvSolution`. The **closure lever itself is proven for all 36**, and the **4** cells that carry the launcher echo are a positive control proving the premise outright. **The bands stand with the caveat on their face** |
| **C-63** | **MODEL_FORM extensions — H extension, H hills, FPE rescue, N_a10 third member** | NO / NO / NO | Each pre-registered before its solve. `N_a10` third member (SA) written **before the solve is launched**, with the settle criterion machine-specified for the runner at `MODEL_FORM_runs/adjusted_settle_n_a10.json` | **SURVEYED** (0 green) `[head-read]` | `verification/campaign/MODEL_FORM_H_EXTENSION_PREREGISTRATION.md`, `MODEL_FORM_H_HILLS_PREREGISTRATION.md`, `MODEL_FORM_FPE_RESCUE_PREREGISTRATION.md`, `N_A10_THIRD_MEMBER_PREREGISTRATION.md` |
| **C-64** | **FPE_DIAG — floating-point exception diagnosis** | NO / NO / NO | **Pre-registered before any probe ran, with zero-compute forensics executed first** | **SURVEYED** (0 green) | `verification/runs/FPE_DIAG_runs/` — the **second** of the two pre-registrations living under a run tree; `verification/campaign/ZERO_COMPUTE_DIAGNOSTICS_2026-08-08.md` |
| **C-65** | **D5_rsm — Reynolds-stress models on secondary flow** | NO / NO / NO | **Prediction committed at `45c0103` before any RSM run**, then scored: linear models give secondary flow at **~6e-16 % of U_bulk** (machine zero) against DNS **2.2201 %**; **SSG 55.01 %** of DNS, **LRR 206.96 %**. The record's own self-criticism is on the page: *"I reasoned from 'RSMs capture the…'"* and **framed the failure mode as under-prediction, never considering overshoot** — *"a failure of imagination, not of arithmetic"* | **SURVEYED** (0 green) | `verification/campaign/D5_RSM_PREDICTION.md`, `D5_RSM_RESULT.md`; `verification/runs/D5_rsm_runs/`. Four EBRSM launches failed before it ran, **each caught by `launch_solve.sh`'s guard** |
| **C-66** | **mbc_retry — mesh birth certificate retry batch** | NO / NO / NO | An infrastructure retry batch, six attempts logged | **SURVEYED** (0 green) `[head-read]` | `verification/runs/mbc_retry_2026-08-16/README.md` plus `mbc_retry{,2..6}.{log,err}` |
| **C-67** | **uq_batch — the 2026-08-16 UQ batch** | NO / NO / NO | An infrastructure batch | **SURVEYED** (0 green) `[head-read]` | `verification/runs/uq_batch_2026-08-16/README.md`, `uq_batch.log`, `uq_batch.err` |
| **C-68** | **The mega-batch ledger families** | NO / NO / NO | 207,000+ evaluations, of which **zero were 3D viscous CFD** before F10 (C-27). The inventory states its own limits plainly: *"Reynolds number: not recorded (inviscid method, no boundary layer)"* for the `vspaero-wing` family | **SURVEYED** (0 green) `[head-read]` | `cases/mega-batch/BATCH_INVENTORY.md`, `PHYSICS_FAMILIES.md`, `COST_SCALING.md`, `LEDGER_DUPLICATES.md`. **9 files tracked at HEAD, 1,244 on disk** — the gitignored work tree a grep sweep cannot see |

---

## 5. The rows — the stored curriculum ladders in `models/`

**These fourteen rows are new in version 2 and version 1 had none of them.** They are
the largest single omission the audit's "selected, not exhaustive" finding covers, and
they are also where the lab's stored observed orders physically live. **Every one of
them is now governed by a standing supervisor ruling on recipe forks** — recorded in
full at `verification/campaign/LADDER_RECIPE_RULING_2026-08-25.md` and annotated into
each study file itself.

> **THE RULING, stated once here and carried in every affected cell: an observed order
> computed across a RECIPE-FORKED gap is `NOT A RESULT`** — a slope fitted across a
> **change of experiment** (`VERIFICATION_CHARTER.md` §3.2), and under `CLAUDE.md`
> rule 5 a row whose triple is not a valid CONVERGING triple is `NOT A RESULT`
> whatever its value.
>
> **It says NOTHING against the underlying solves.** Every rung ran, every coefficient
> was measured, and nothing here impugns any of them. The ruling is against the
> **grid-convergence claims built on them** and against nothing else.
>
> **The affected rows move TOWARD `NOT A RESULT`, which `CLAUDE.md` rule 5's one-way
> door permits — never back.** The gate can turn a `PASS` or a `GATE FAIL` *into*
> `NOT A RESULT`, never the reverse.

The instrument: `scripts/recipe_audit.py`, first committed **`72bc966d`**, HEAD blob
**1,558 lines**, sha256 `4e45603038f7ae03c9236e7e800f3e1f87d47086eb4bf9e467520c125da8dd9a`.
Its sweep covered **461 candidate directories, 422 parsed, 14 ladders assembled: 7
RECIPE-FORKED, 4 recipe-clean, 3 unauditable.** **Every RECIPE-FORKED verdict below
was re-run by this lane against the rung directories named**, not taken from the
sweep's summary.

**THE INSTRUMENT'S STATED LIMIT, carried because a check that overstates its reach is
worse than none:** `similarity_failures()` treats **any** change of a block's grading
as a similarity failure — *"regraded cells are not scaled cells"*. **That is correct
for the uniform-background snappy ladders this sweep covers and WRONG for a
correctly-built GRADED ladder**, which *must* change its grading string as it refines
precisely in order to keep the first cell scaling. **F12's repaired RAE 2822 ladder
(C-30) is exactly such a family, so running `recipe_audit.py` against it would report a
SPURIOUS FORK.** Full statement and its executable control: §5.1 of
`verification/campaign/LADDER_RECIPE_RULING_2026-08-25.md`.

| # | row | ladder shape, measured | G | matrix TIER | evidence, by path |
|---|---|---|---|---|---|
| **C-69** | **curriculum `ahmed_25` — published p = 1.95** | **RECIPE-FORKED at gap 2.** background **9,450 → 28,080 → 28,080**; gap 1 `SCALED` (×2.9714), gap 2 background **HELD FIXED** and the recipe moved in **3 fields** | **NO — the published `observed_order` 1.95 is `NOT A RESULT`** under the standing ruling. **All three production rungs are on disk and the fork is DIRECTLY MEASURED, not inherited from prose** | **NOT HELD** | `models/curriculum/uq-studies/ahmed_25.json` (`numerical.observed_order`, `refit_in_place.reproduced_exactly.observed_order`, both annotated in place); rungs `/home/ubuntu/certonomous-runs/study-ahmed_25-coarse-40aacb` (20,621 cells), `…-medium-b37e86` (45,753), `…/w3-published-rung-ahmed_25/a` (79,439) — cell counts match the stored `levels[]` **to the cell** |
| **C-70** | **curriculum `ahmed_35` — published p = 3.169** | **RECIPE-FORKED at gap 2**, same shape: **9,450 → 28,080 → 28,080** | **NO — 3.169 is `NOT A RESULT`.** Directly measured | **NOT HELD** | `models/curriculum/uq-studies/ahmed_35.json`; rungs `study-ahmed_35-coarse-186b41` (20,425), `…-medium-d198f3` (45,813), `act7-ahmed_35-02688b` (79,778) |
| **C-71** | **curriculum `naca0012_wing` — published p = 3.173** | **RECIPE-FORKED at gap 2.** background **13,524 → 39,600 → 39,600**; gap 1 `SCALED` (×2.9281) | **NO — 3.173 is `NOT A RESULT`.** The file's own stored `recipe_audit` **already said so in its own words** — *"The three stored rungs are TWO mesh recipes, and no knob moves twice"* — and the stored `production_recipe_family_built.fit.observed_order` **24.048** is the separate W3 family, C-36 | **NOT HELD** | `models/curriculum/uq-studies/naca0012_wing.json`; rungs `study-naca0012_wing-coarse-09bec1` (27,265), `…-medium-520ccb` (67,356), `study-naca0012_wing-1021cb` (140,580) |
| **C-72** | **curriculum `naca4412_wing` — published p = 10.467, §3.2's OWN worked example** | **RECIPE-FORKED at gap 2.** background **13,524 → 39,600 → 39,600** | **NO — 10.467 is `NOT A RESULT`.** `VERIFICATION_CHARTER.md` §3.2 uses this ladder as its worked example of the defect, and **it is now measured mechanically rather than argued**. The superseded 4.625 in the same file is voided by the same ruling for the same reason | **NOT HELD** | `models/curriculum/uq-studies/naca4412_wing.json` (`numerical`, `superseded.numerical`, `refit_in_place` — all three annotated); rungs `study-naca4412_wing-coarse-a6c5e0` (27,237), `…-medium-337080` (67,826), `study-naca4412_wing-1af072` (137,569) |
| **C-73** | **curriculum `motorBike` — published p = 7.298** | **RECIPE-FORKED at BOTH gaps.** background **(20 8 8) = 1,280 on all three rungs** — the background never moves at all, and the recipe moves twice | **NO — 7.298 is `NOT A RESULT`** | **NOT HELD** | `models/curriculum/uq-studies/motorBike.json`; rungs `/home/ubuntu/certonomous-runs/mb-iterfix/coarse` (14,714), `mb-iterfix/medium` (66,302), `study-motorBike-f8b4a2` (353,688). **CORRECTION TO A LANDED RECORD:** `LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md` §2 classes this ladder `UNDETERMINABLE` on *"1 of 3"* rungs on disk. **All three are on disk**, so the fork is measured, not undeterminable |
| **C-74** | **`airliner_wing_span52` — no published p** | **RECIPE-FORKED at gap 2.** background **6,300 → 17,280 → 17,280**; gap 1 `SCALED` (×2.7429) | **NO.** No order was ever fitted, so nothing is withdrawn — **the row exists so that no order is ever fitted from these three rungs in future** | **NOT HELD** | `models/curriculum/uq-studies/airliner-wing.json` (carries no `numerical` block — annotated with the ruling nonetheless); rungs `study-airliner_wing_span52-coarse-1f61fe` (9,639), `…-medium-e565e1` (22,754), `study-airliner_wing_span52-2cdf8e` (32,385) |
| **C-75** | **`credential-repair-naca4412` — no published p** | **RECIPE-FORKED at BOTH gaps.** background **39,600 throughout**; the levels move (3 4) / (4 5) / (5 6) and the background never does | **NO.** As C-74, nothing is withdrawn and the row is a forward bar | **NOT HELD** | rungs `/home/ubuntu/certonomous-runs/credential-repair-naca4412-{medium,fine,finer}` (263,359 / 645,251 / 1,849,113 cells); annotated in `models/curriculum/uq-studies/naca4412_wing.json`, the study these rungs were built to repair |
| **C-76** | **curriculum `b52` — the stored 8-rung set** | `recipe_audit` **carved a single-recipe sub-family** out of a mixed set: coarse and medium used nearBody level 1 (max cell level 3); intermediate, production, fine-uq and finer2 used level 2 (max level 4) | **NO.** The carved family is recipe-clean; the **stored orders are still not G** — `numerical.observed_order` **28.675** is clamped and refused by `order_window`, and `refit_in_place` **2.253** is superseded by rung 7's *"no order fitted; the ladder is no longer monotone"* | **NOT HELD** | `models/curriculum/uq-studies/b52.json`; C-49, C-50, C-51 |
| **C-77** | **curriculum `cube`** | recipe-audited 2026-08-14 at **NO COMPUTE**, *"every reading below comes off an archived log or dictionary"* | **NO — `observed_order` is `null`.** There is no order to withdraw | **SURVEYED** (0 green) | `models/curriculum/uq-studies/cube.json`; C-38, C-39 |
| **C-78** | **curriculum `naca0015_sail` — published p = 1.696** | recipe-audited 2026-08-14 at NO COMPUTE; **not among the 7 forked**, and **not among the 4 recipe-clean either — it is one of the 3 UNAUDITABLE** | **NO. The order 1.696 is not withdrawn by the recipe ruling and is not certified by it either** — the rungs cannot be audited, so admissibility is unknown. **An unauditable ladder is not a clean one** | **SURVEYED** (0 green) | `models/curriculum/uq-studies/naca0015_sail.json`; `CUBE_SAIL_DRAW_SCATTER_PREREGISTRATION.md` |
| **C-79** | **curriculum `aortic_valve`** | **not a grid ladder** — a quadrature family | NO | **SURVEYED** (0 green) | `models/curriculum/uq-studies/aortic-valve.json`; case `models/curriculum/aortic_valve/`; C-26 |
| **C-80** | **curriculum `cylinder`, `flat_plate`, `sphere`** | **no ladder stored** — results only, no `observed_order` anywhere in `models/curriculum/results/` (checked by parsing all eight files, not by grep) | NO | **SURVEYED** (0 green) | `models/curriculum/results/{cylinder,flat_plate,sphere}.json`; cases `models/curriculum/{cylinder,flat_plate,sphere}/` |
| **C-81** | **`tmr_flatplate_fine` — the UQ propagation study** | **PRE-REGISTERED, with a `preregistration_contract` block and a `preregistered_utc` stamp in the artefact itself**, plus `deviations_from_preregistration`, `restart_verification`, `source_verification` and a `budget_core_min_remaining`. **This is the best-instrumented single artefact in cfd territory** | **NO — it propagates uncertainty on the flat plate; it does not compute a Roache triple.** Its `polynomial_chaos` `order_1`/`order_2` fields are **PCE expansion orders, not observed orders of convergence**, and must never be read as the latter | **SURVEYED** (0 green — a frozen gate that tested none of V/G/P) | `models/curriculum/uq-studies/tmr_flatplate_fine.json` |
| **C-82** | **`tmr_flatplate_modelform` — the model-form band artefact** | Carries its own `lever_activity_caveat` block | NO | **SURVEYED** (0 green) | `models/curriculum/uq-studies/tmr_flatplate_modelform.json`; C-62 |

---

## 6. Enumerated and NOT offered as a gradeable row — stated so no silence is read as a zero

**An omitted embarrassing row is worse than a blank one, and an omitted *irrelevant*
row is how "exhaustive" quietly becomes "selected".** Everything below was enumerated
in the same sweep and is deliberately not scored, with the reason on the face of it.

| path | what it is | why not a row |
|---|---|---|
| `cases/demo-surfaces/` | 6 tracked geometry assets (`b52.stl`, `motorBike.obj`, `naca0012_wing.stl`, `naca0015_sail.stl`, `naca4412_wing.stl`) | **geometry inputs, not a case.** They are consumed by C-69…C-78 and are cited there |
| `models/airplane/` | `airplane.stl`, `b52.stl` | same |
| `cases/valve/` | 5 PNG figures, `capture-manifest.json`, `shotlist.md` | **filming assets for C-26.** No solver, no gate |
| `verification/campaign/LADDER_V_*` (43 files) | the "Ladder V" text-claims audit rounds V1–V16, with grades, regrades, closures and non-author cross-checks | **no solver and no physics quantity.** It audits claims in records. It cannot carry a V, G or P and offering it a `NEVER RUN` tier would misdescribe it — `NEVER RUN` means *no solver has run in this class*, and there is no class of solve here |
| `verification/campaign/{W2_SPARTA_*, W2_*_READING, W5_SPARTA_GATE_STATUS, R5_*, S6_*}` | SpaRTA, closure-literature readings, the QCR forward entry, the S6 residual-stall wiring | **JURISDICTION.** These are closure-family and infrastructure content **filed in a cfd-territory directory**. cfd enumerates them and **defers scoring to the owning family** rather than scoring another team's work on cfd's read. *(`W2_SPARTA_REGRESSION.md`'s own header: docket item `w2-sparta-regression-discovery`, prereg committed 01:14 UTC before the library was evaluated, **137 core-min measured against 180 budgeted**. `W5_SPARTA_GATE_STATUS.md`: **"No solver was launched under either item, and that is the finding, not a shortfall."**)* |
| `verification/campaign/{MOVE_MAP_*, BOARD_*, AUDIT_*, DEAD_LEVER_*, WEEKLY_METRICS_*, CALIBRATION_SCORECARD_*, IMPROVEMENT_DASHBOARD_*, SWEEP_*, LESSON_PROPAGATION_*, OWNERSHIP_BOUNDARY_*, SHARED_TREE_COMMIT_HAZARD, NOT_PASSING_REGISTER, …}` | lab-administration records | **not cases.** Enumerated; not scored |
| `verification/campaign/CASES_FAMILY_SUPERVISION_GUIDELINES.md`, `CAMPAIGN_STATUS.md`, `NEXT_CASES_SLATE.md`, `RESEARCH_DIRECTIONS_2026-08.md`, `CHALLENGE_SLATE_2026-08.md` | governing and planning prose | as above |
| `models/curriculum/__pycache__/` | on disk, untracked | build artefact. **Named because a `find` sweep sees it and a `git ls-tree` does not**, and the difference is the point of §1.1 |

---

## 7. Census

### 7.1 Tier census — 82 rows

| tier | rows | share |
|---|---|---|
| **HOLDS** | **0** | — |
| **GATE REACHED** | **1** | C-53 (DMR) — the only row with a green column **and** a pre-registration frozen before compute |
| **SURVEYED** | **45** | 0 green columns |
| **NOT HELD** | **24** | an honest FAIL or a blocker |
| **NEVER RUN** | **5** | C-6, C-29, C-30, C-56, C-58 |
| **RUBRIC GAP — owner's ruling required** | **7** | C-3, C-4, C-5, C-7, C-26, C-31, C-54 — **not a tier; see §0.2** |
| **total** | **82** | |

**THE ZERO IN THE `HOLDS` COLUMN IS THE HONEST HEADLINE AND IS NOT SMOOTHED.** cfd
holds no row with V, G and P green at once, and after Ruling 4 **no row in cfd
territory is even one step from one.** C-30 (F12) is the closest: it has a **held
public primary experiment** and a **frozen pre-registration**, and needs the solve
plus a three-rung ladder.

### 7.2 Column census

| column | green | which |
|---|---|---|
| **V** | **7 of 82** | C-3 F3 wedge (**exact**), C-4 F3 cone (**exact**), C-5 F3 diamond (**exact**), C-7 F4 (**correlation**), C-26 F9 (**exact**, VERIFY on whether the source is held), C-53 DMR (**exact**), C-54 DPW8_V2 (**exact**) |
| **G** | **1 of 82** | C-31, the TMR flat plate — and it sits in the rubric gap, because the family that earned the lab's best grid convergence never pre-registered it |
| **P** | **0 of 82** | **none.** Version 1 offered one; §0.1 withdraws it under the owner's Ruling 4 |

### 7.3 What going exhaustive cost, in rows

| | count |
|---|---|
| rows in version 1 | **19** |
| rows in version 2 | **82** |
| of which: version-1 rows split into their individual gradeable rows | **+16** |
| of which: families version 1 never enumerated at all | **+47** |

**The 16 from splitting**, family cell → rows:

| version 1 cell | split into |
|---|---|
| Row 1, "F3 supersonic inviscid exact-theory suite (wedge / cone / diamond)" | **C-3 wedge, C-4 cone, C-5 diamond** — three geometries, three independent exact solutions, three separately gated PASSes |
| Row 8, "TMR bump-in-channel, including W1 on NASA's own grids" | **C-32 NASA's own grids, C-33 the lab's own blockMesh family** — two grid families with **different** G refusals, and merging them hid that the second is worse than the first |
| Row 9, "3D grid ladders (Ahmed 25°, finite wings, B-52, cube)" | **C-35 R4 Ahmed, C-36 W3 NACA 0012, C-37 W3 NACA 4412, C-38 W3 cube, C-76 b52, C-78 sail** — six ladders, each independently pre-registered and independently graded |
| Row 13, "2D separated turbulent flow (NASA hump, periodic hills, backward-facing step)" | **C-15 hump, C-18 periodic hills, C-12 backward-facing step** (and C-13, C-14, C-16, C-17, C-19, C-20 as separately pre-registered follow-ons) |
| Row 14, "Unsteady 2D cylinder (F5a, R7)" | **C-9 F5a Strouhal Re 100–180, C-10 R7 mesh sensitivity at Re 1000** |
| Row 16, "F7 free-surface dam break" | **C-22 dam break, C-23 the re-gate contract, C-24 F7b/F7c blocked** |
| Row 19, "Instrument and diagnostic campaigns (4G, GEN_ALT, MESH_AUDIT, MODEL_FORM, FPE_DIAG, D5_rsm)" | **C-59, C-60, C-61, C-62, C-64, C-65** — six campaigns, six pre-registrations, six verdicts, one cell |

**Where a family genuinely IS one row, this file says so on the face of the cell**
rather than leaving it ambiguous — C-7 (F4: standoff and Cp are two quantities on one
case) and C-80 (three curriculum bodies with no ladder stored between them) are the
two that carry that sentence explicitly.

---

## 8. Version 1's rows, struck individually

**Nothing from version 1 is silently rewritten.** Every one of its 19 rows is listed
with what it became and, where the tier moved, why.

| v1 row | v1 tier | v2 row(s) | v2 tier | why it moved |
|---|---|---|---|---|
| 1 F3 | SURVEYED | C-3, C-4, C-5 | ~~SURVEYED~~ → **RUBRIC GAP** | Version 1 applied the **struck** Ruling 1 ("SURVEYED is reserved for rows with no pre-registered gate at all"). Under the final Ruling 1 a row with a green V is not *"nothing on the V/G/P axes"*, and the published rule does not reach it. §0.2 |
| 2 F4 | SURVEYED | C-7 | ~~SURVEYED~~ → **RUBRIC GAP** | as row 1 |
| 3 DMR | GATE REACHED — missing G and P | C-53 | **GATE REACHED — missing G and P** | **unchanged.** 1 green under a frozen prereg is `GATE REACHED` under every form of Ruling 1 |
| 4 DPW8_V2 | SURVEYED | C-54 (+C-55 new) | ~~SURVEYED~~ → **RUBRIC GAP** | as row 1 |
| 5 F9 | SURVEYED | C-26 | ~~SURVEYED~~ → **RUBRIC GAP** | as row 1 |
| 6 F4-SIGFPE | GATE REACHED — missing V, G and P | C-8 | ~~GATE REACHED~~ → **SURVEYED** | **The struck Ruling 1 tiered by counting MISSING columns; the final one counts GREEN columns.** A row with zero green is `SURVEYED`. The owner's own words on why: calling a row missing all three `GATE REACHED` *"flatters them, and it flatters them in the direction of the lab's own interests, which is the direction a rubric must never drift"* |
| 7 TMR flat plate | SURVEYED | C-31 | ~~SURVEYED~~ → **RUBRIC GAP** | as row 1. **This is the sharpest instance**: version 1's own cell already named the tension and asked the owner to settle it. §0.2 is that request, restated as a refusal to guess |
| 8 TMR bump / W1 | GATE REACHED — missing V, G and P | C-32, C-33 | ~~GATE REACHED~~ → **SURVEYED** ×2 | as row 6, plus the split |
| 9 3D ladders | NOT HELD | C-35, C-36, C-37, C-38, C-76, C-78 | **NOT HELD** ×4, **SURVEYED** ×2 | The four ladders that armed a pre-registered G gate and refused a converging triple stay `NOT HELD`. **`cube` (C-77) has no order to fail and `naca0015_sail` (C-78) is UNAUDITABLE rather than failed** — merging them into a single `NOT HELD` overstated the evidence against them |
| 10 F2 | SURVEYED | C-2 | **SURVEYED** | unchanged |
| 11 F12 | NEVER RUN | C-30 | **NEVER RUN** | unchanged |
| 12 F11 | SURVEYED | C-28 (+C-29) | **SURVEYED** | tier unchanged. **The row's factual claim is CORRECTED:** version 1 recorded that `F11_CONVERSION_PREREGISTRATION.md` *"does not yet exist on disk"*. **It exists**, at `verification/campaign/F11_CONVERSION_PREREGISTRATION.md`, commit **`157793db`**. Nobody's error — concurrent lanes; version 1's cell was true when written |
| 13 2D separated | NOT HELD | C-12, C-15, C-18 (+6 follow-ons) | **NOT HELD** ×5, **SURVEYED** ×4 | tier survives on C-18. **THE SCORE MOVED: version 1 scored `P` GREEN on this row and version 2 scores it NO.** Under the owner's **Ruling 4**, which version 1 never saw, `P` requires **measured physical reality**. The band's held limb (Breuer 2009, 4.69) is an **LES/DNS computation**; its experimental limb (Rapp & Manhart 2011, 4.21) is **not held** and is `SECONDARY` under Ruling 3. **This withdrawal empties cfd's P column** |
| 14 cylinder shedding | GATE REACHED — missing V, G and P | C-9, C-10 | ~~GATE REACHED~~ → **SURVEYED** ×2 | as row 6 |
| 15 F5b | NOT HELD | C-11 | **NOT HELD** | unchanged (a blocker) |
| 16 F7 | NOT HELD | C-22 (+C-23, C-24) | **NOT HELD**, **SURVEYED**, **NOT HELD** | tier survives on C-22 |
| 17 F1 | SURVEYED | C-1 | **SURVEYED** | unchanged. **A correction this lane ALMOST made and then measured instead:** having found that `F11_CONVERSION_PREREGISTRATION.md` landed after version 1 was written, this lane expected version 1's count of **44** to be stale by one. **It is not.** Re-enumerated at HEAD: **42** in `verification/campaign/` (F11's conversion prereg is among them) **+ 2** under `verification/runs/` = **44**, unchanged. The near-miss is recorded because an "obvious" arithmetic correction that nobody counts is exactly how a false figure enters a record. **The claim it supports is unaffected: not one of the 44 registers a gate on F1 or ONERA M6** |
| 18 F8 | NOT HELD | C-25 | **NOT HELD** | unchanged |
| 19 instruments | GATE REACHED — missing V, G and P | C-59, C-60, C-61, C-62, C-64, C-65 | ~~GATE REACHED~~ → **SURVEYED** ×6 | as row 6, plus the split |

**Net effect of the rubric correction alone, before any new row was added:** 5 rows
moved **down** from `GATE REACHED` to `SURVEYED` (rows 6, 8, 14, 19 and their splits),
6 moved **out** of `SURVEYED` into the rubric gap, and **1 green cell was withdrawn**.
**Every movement is in the unflattering direction.** That is what an owner's rubric
tightening looks like when it is applied honestly, and it is the reason cfd does not
apply a rubric of its own.

### 8.1 The seven rubric-gap rows, collected for a one-pass ruling

| row | green column | frozen prereg? | if the qualifier is mandatory | if it is descriptive |
|---|---|---|---|---|
| C-3 F3 wedge | V (exact) | no | SURVEYED | GATE REACHED — missing G, P |
| C-4 F3 cone | V (exact) | no | SURVEYED | GATE REACHED — missing G, P |
| C-5 F3 diamond | V (exact) | no | SURVEYED | GATE REACHED — missing G, P |
| C-7 F4 | V (correlation) | no | SURVEYED | GATE REACHED — missing G, P |
| C-26 F9 | V (exact) | no | SURVEYED | GATE REACHED — missing G, P |
| C-31 TMR flat plate | **G** | no | SURVEYED | GATE REACHED — missing V, P |
| C-54 DPW8_V2 | V (exact) | no | SURVEYED | GATE REACHED — missing G, P |

**Note that C-3, C-4, C-5 and C-26 all leave the gap the moment their conversion
pre-registrations fire** — `F3_CONVERSION_PREREGISTRATION.md` is already **FROZEN and
UNFIRED** (C-6). **C-31's gap does not close that way**; it needs a pre-registration
written for the flat plate, and none exists.

---

## 9. Items marked VERIFY, and what these rows cannot see

### 9.1 VERIFY

| item | row | why |
|---|---|---|
| Whether Womersley (1955) is **held** on this box and title-page verified | C-26, V | No copy found under `docs/papers/`. If it is not held, Ruling 3's logic may bear on V and the cell should be re-scored |
| Title-page verification of `docs/papers/benchmark_test_cases/greenblatt_et_al_cfdval2004_hump.pdf` | C-15, P | The PDF and its `.txt` sidecar are on disk and it is the **experiment primary** that makes C-15 the shortest path to cfd's first green P. **Rule 15 forbids verifying a paper by filename or hash**, and this lane did not open the title page |
| Title-page verification of `breuer_peller_rapp_manhart_caf2009_periodic_hills.pdf` | C-18 | Carried from version 1. It no longer carries a green cell, but the withdrawal in §0.1 rests on reading it as an **LES/DNS** paper, and that reading came from the pre-registration's source table, not from the PDF's title page |
| Whether the F12 run tree is still empty at launch time | C-30 | `verification/runs/F12_runs/` held only `reference/` when this was written. **Re-check the freeze condition in the same shell invocation as the launch**, not from this file |
| Every row marked `[head-read]` | 12 rows | Read to the record's opening section and its cited path, not in full. Offered as enumeration with a citation, **not as an audit** |

### 9.2 What these rows cannot see

* **They cannot see a `HOLDS`.** Not one row has V, G and P green at once, and after
  Ruling 4 no row is one step from it.
* **They cannot see a green P at all.** Zero of 82. Three rows (C-9, C-11, C-22) are
  held down by `NOT OBTAINED` references rather than by physics, and **acquiring four
  papers would move more cells here than any solve cfd could run.**
* **They cannot see 3D grid convergence.** Four pre-registered 3D families each
  refused a converging triple, and seven stored curriculum ladders are `NOT A RESULT`
  on recipe grounds before their arithmetic is even reached.
* **They cannot see 3D validation against experiment under a pre-registration.** cfd
  **confirms** `COVERAGE_MATRIX.md` §4 fact 2 for its own territory, on an
  enumeration of all 44 pre-registration files, not on impression.
* **They cannot see whether the lab's own Roache instrument agrees.**
  `scripts/roache_triple.py` passes 53/53 selftests and **has graded no cfd ladder.**
  §0.3's arithmetic identity between the two implementations' formulas is not the same
  as one ladder graded by both.
* **They cannot see iterative convergence on a residual reading for C-31.** The one
  G-green triple rests on a force-plateau reading; a strict rule 5 clause (1) reading
  would void it. **That ruling is the verification team's.**
* **They cannot see C-8's headline at settled value** — contingent on a `PENDING`
  ruling that is Sanaa's.
* **They cannot see C-11's wrapper assertions working.** Unexercised; descriptions of
  code, not measurements.
* **They cannot see inside the gitignored trees except by name.**
  `cases/mega-batch/` holds 1,244 files on disk and 9 at HEAD; C-68 is scored on the 9.
* **They cannot see cost as money.** No dollar figure is quoted. The box cannot read
  its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
* **They cannot see whether the tier words survive Sanaa's reading of the rubric.**
  `COVERAGE_MATRIX.md` §0 states the rubric is the chief's **reconstruction** of her
  directive. **If she reads it differently every tier here is re-derived from the same
  evidence clauses**, which is why each cell carries its evidence and not only its
  letter.

---

## 10. Provenance, cost, and what this contribution does not do

**Written** 2026-08-25 by a cfd `lab-lane` under the cfd supervisor, against HEAD
`af2b23b0`. **Supersedes** version 1, blob `9060e751`.

**ZERO SOLVER COMPUTE** — no solver, no mesh, no MPI rank, no training. The lane did
run `scripts/recipe_audit.py --selftest` (**PASS**: 53 value controls, 12 mutation
controls, 6 refusal controls, live `ahmed_25` regression fixture present, 8
stated-limit controls) and re-ran seven ladder audits and one `--discover` walk over
417 case directories. **Those are single-rank Python reads of dictionaries on disk.**
**Estimate-versus-actual (rule 12):** predicted 0 core-minutes of solver time, actual
**0 core-minutes of solver time**, ratio n/a, zero waste. The Python analysis time was
not instrumented and is **reported as an estimate under 2 core-minutes — an estimate,
not a measurement**, and is labelled so rather than quoted as if a log backed it. **No
`docs/COST_CALIBRATION.md` row is due**, because no compute process completed; this is
a scoring and filing task, and saying so plainly is the calibration honesty rule 12
asks for.

**Sources read:** `CLAUDE.md` in full; `docs/COVERAGE_MATRIX.md` §0–§2.2 and §3–§4
**from the HEAD blob**, including the two Ruling-1 amendments and Ruling 4 that
version 1 predates; `docs/charters/VERIFICATION_CHARTER.md` §3.2, §3.4, §6b;
`docs/charters/FILING_CHARTER.md`; `docs/charters/REPORTING_CHARTER.md`; and each
record and artefact cited in the rows above.

**Two things this contribution does not do:**

1. **It does not touch `docs/COVERAGE_MATRIX.md`.** That file is the verification
   team's; it was **read from the HEAD blob and not modified.**
2. **It does not edit `docs/charters/VERIFICATION_CHARTER.md`.** §3.2's NACA 4412
   worked example is now **measured** to be exactly the defect the charter describes
   (C-72, p = 10.467, RECIPE-FORKED at gap 2). A note for the verification team is
   drafted at `verification/campaign/LADDER_RECIPE_RULING_2026-08-25.md` §7 and is
   **for the chief to route**. cfd does not edit another team's charter.

**Submissions are parked.** Nothing here is filed, sent, uploaded or registered
outside this box.

---

## 11. AMENDMENT 1 — 2026-08-25: three VERIFY items discharged by title-page verification, and one over-broad statement corrected

**Version 2.1.** Appended at the foot under `CLAUDE.md` rule 6 because other records
— including the dispatch that produced this amendment — cite this file **by line
number**. Nothing above is edited.

**lines whose number changed above this section: 0**

**ZERO SOLVER COMPUTE.** No solver, no mesher, no case directory, no MPI rank. The
work in this section is PDF rendering and reading, single-rank, plus filesystem
sweeps. Cost is closed out in §11.7.

**No score and no tier moves in this amendment.** §11.6 states that positively rather
than leaving it to be inferred, and §11.5 names the one cell whose re-score is now
**live and referred to the owner** rather than taken by cfd.

### 11.1 Method — how the title pages were verified, and why the method matters

Rule 15 forbids verifying a paper by file type, filename, hash or sidecar. Each PDF
below was verified by **rendering its page 1 to a PNG at 150 dpi and reading the
rendered image** — i.e. by looking at what a human reader would see, not at metadata
and not at extracted text. Extracted text was used **afterwards**, and only to locate
and quote body content whose page had already been rendered and read.

That ordering is the point. The Greenblatt PDF's own embedded metadata reads
`Title: Microsoft Word - PortlandPaperPart1.doc`, `Author: Administrator` — a
manifest built from metadata would have recorded this paper as authored by
"Administrator". **The rendered page says something completely different, and the
rendered page is the paper.**

This lane rendered and read three page images: Greenblatt page 1, Greenblatt page 7
(Table 2), and Breuer page 1.

### 11.2 VERIFY item at line 511 (C-15, P) — **DISCHARGED**

**Struck**, from the C-15 P cell at line 236 and from the VERIFY table at line 511:

> ~~**VERIFY:** this lane did **not** title-page verify that PDF (rule 15)~~
> ~~| Title-page verification of `docs/papers/benchmark_test_cases/greenblatt_et_al_cfdval2004_hump.pdf` | C-15, P | … **Rule 15 forbids verifying a paper by filename or hash**, and this lane did not open the title page |~~

**Restated, from the rendered page 1 read by this lane:**

* **AIAA-2004-2220**, printed top-right of the title page.
* **"A Separation Control CFD Validation Test Case — Part 1: Baseline & Steady
  Suction."**
* **David Greenblatt, Keith B. Paschal, Chung-Sheng Yao, Jerome Harris, Norman W.
  Schaeffler and Anthony E. Washburn.**
* **Flow Physics and Control Branch, NASA Langley Research Center, Hampton VA**
  (the printed ZIP reads `2361-2199`, which is a typographic error in the paper
  itself; recorded as printed and not silently corrected).
* **2nd AIAA Flow Control Conference, June 28 – July 1, 2004, Portland, OR.**
* Abstract, first sentence, verbatim: *"Low speed flow separation over a
  wall-mounted hump, and its control using steady suction, were **studied
  experimentally** in order to generate a data set for a workshop aimed at
  validating CFD turbulence models."*
* The author footnotes place every one of the six authors in the Flow Physics &
  Control Branch at Mail Stop 170 — **the people who took the measurements are the
  people who wrote the paper.**

**Sidecar checked and found real, not a stub:**
`greenblatt_et_al_cfdval2004_hump.txt` is **2,480 lines / 46,845 non-whitespace
characters**, and its content was confirmed against the rendered pages (title-page
text at sidecar lines 6–16; Table 2 at line 458; §V "Test Cases" at 346–357).

**Verdict on the item: DISCHARGED.** Under the owner's Ruling 4 this is a **public
primary experiment**, held on disk, readable, and authored by the experimentalists.
It is the case C-15 and F6a name. **Rule 15 is satisfied by reading, not by
inference.**

**What does NOT change: C-15's P cell stays `NO`, and its tier stays `SURVEYED`.**
The source was never the missing piece — the cell already said so. What is missing
is a **frozen pre-registration gating agreement with it**, and until one exists and
fires, the source being verified changes nothing about the score. Recording the
discharge without moving the cell is the honest outcome, and moving the cell here
would be exactly the error rule 2 exists to prevent.

### 11.3 VERIFY item at line 512 (C-18) — **DISCHARGED**, and it is the item that forces §11.4

**Struck**, from the VERIFY table at line 512:

> ~~| Title-page verification of `breuer_peller_rapp_manhart_caf2009_periodic_hills.pdf` | C-18 | … that reading came from the pre-registration's source table, not from the PDF's title page |~~

**Restated, from the rendered page 1 read by this lane:**

* **"Flow over periodic hills – Numerical and experimental study in a wide range of
  Reynolds numbers."**
* **M. Breuer, N. Peller, Ch. Rapp, M. Manhart** — Lehrstuhl für Strömungsmechanik,
  Universität Erlangen-Nürnberg; Fachgebiet Hydromechanik, Technische Universität
  München.
* **Computers & Fluids 38 (2009) 433–457**, doi `10.1016/j.compfluid.2008.05.002`,
  received 4 February 2008, available online 28 May 2008.
* Abstract, verbatim: *"We present results predicted by direct numerical simulations
  (DNS) and highly resolved large-eddy simulations (LES) achieved by two completely
  independent codes. **Furthermore, these numerical results are supported by new
  experimental data from PIV measurements.**"*

**The title page discharges the item and simultaneously falsifies the sentence the
item was supporting.** The paper's own title contains the words **"Numerical *and
experimental* study"**. §11.4 corrects it.

### 11.4 THE CORRECTION — an over-broad statement, struck and restated precisely. **The withdrawal it supports STANDS.**

**Struck**, at three places, quoted exactly as they stand above and left standing
above so a reader can see what changed:

> ~~§0.1, line 72: "the held limb — Breuer, Peller, Rapp & Manhart (2009), x_R/h = **4.69** — is an **LES/DNS Reynolds-number series**, a computation."~~
>
> ~~C-18's P cell, line 239: "its **held** limb (Breuer et al. 2009, 4.69) is an **LES/DNS computation**."~~
>
> ~~§8 row 13, line 470: "The band's held limb (Breuer 2009, 4.69) is an **LES/DNS computation**."~~

**Restated, and the difference is not cosmetic:**

> **The CITED VALUE 4.69 is a computation. The PAPER is not.**

**Evidence for the first half, measured by this lane in the held sidecar:**
`4.69` occurs exactly once (sidecar line 2116), inside the sentence *"The
corresponding values of the reattachment lengths are xR/h = 5.24, 5.19, 5.41, 5.09,
and 4.69 for Re = 700 to 10,595, respectively"*, which is the series plotted in
**Fig. 22**, whose caption reads (sidecar line 2176): *"Separation length and
reattachment length vs. Reynolds number; **comparison of predictions by LESOCC and
MGLET***." LESOCC and MGLET are the paper's two LES/DNS codes. **The 4.69 the F6b
band held is an LES prediction at Re = 10,595 and is not a measurement.**

**Evidence for the second half:** the paper's title and abstract, quoted in §11.3.
It reports **new PIV experiments** performed for this study alongside the
computations.

**Why the withdrawal still stands, measured and not assumed.** A sidecar sweep for a
tabulated **experimental** reattachment length found none: every numeric reattachment
figure in the paper traces to Fig. 22 and to the two codes. The paper's experimental
content appears as **figures** — Fig. 18 and Fig. 19 compare PIV measurements against
predictions at x/h = 0.5, 2, 4 and 6 for Re = 5,600 and 10,595 — and **a digitised
figure is a weaker basis than a tabulated value.** So the F6b band's held limb remains
a computation, its experimental limb (Rapp & Manhart 2011, 4.21) remains unheld and
`SECONDARY` under Ruling 3, **and C-18's P cell stays withdrawn from green under
Ruling 4. Nothing in this correction rescues C-18.**

**Why the correction is made anyway, which is the whole point of this section.** A
record that overstates its ground invites a correct rebuttal that then *looks like*
it overturns the conclusion. Anyone reading "Breuer 2009 is an LES/DNS computation"
against a paper titled *"Numerical **and experimental** study"* can refute cfd's
sentence in one line — and having refuted the sentence, would reasonably believe the
withdrawal it justified had fallen with it. **It has not.** The narrow claim — *this
value, 4.69, is a prediction* — is both true and sufficient, and it is the claim the
record should have carried.

**One consequence, stated as an opening and NOT as a result.** Because the paper does
contain public primary experimental data and the lab holds it, a P-green on the
periodic-hill family is **not categorically closed** by Ruling 4 the way version 2's
wording implied. It would require a **fresh frozen pre-registration gating a quantity
the paper reports experimentally** — the PIV profiles of Figs. 18–19 — and would
inherit the figure-digitisation weakness named above. **This is an open route, not a
claim. No cell moves on it, and cfd offers it to the owner rather than scoring it.**

### 11.5 VERIFY item at line 510 (C-26, V) — **MEASURED: NOT HELD. The conditional has fired, and the re-score is REFERRED, not taken.**

**The gap, measured rather than searched-for-and-shrugged-at:**

* `/usr/bin/find` over **all of `/home/ubuntu`**, excluding `.git`, for `*womersley*`
  and the misspellings `*womers*`, `*wormersley*`, `*womersly*`: **zero papers.**
  Every hit is a lab-generated artefact of our own — `cases/valve/02-womersley.png`,
  `verification/runs/F9_work/womersley_followup_results.json`,
  `verification/runs/F9_work/womersley_probe_check`, two `demo-output` copies, and a
  solve-registry log.
* **A filename sweep alone would not be evidence** (a paper can be filed under any
  name), so a content sweep was run as the control: **all 610 PDFs on the box** were
  passed through `pdftotext` over their first three pages and grepped for
  "womersley". **Zero hits.** The reader was demonstrated able to see a non-zero on
  the same instrument in §11.2 and §11.3, where it read two title pages correctly.
* Instruments named per the standing constraint: `/usr/bin/find` and `/usr/bin/grep`
  for the disk (`grep -r` in this environment honours ignore files and is blind to
  gitignored trees).

**Recorded as a plain gap: F9 has a solve with no held primary behind it. Rule 15 has
nothing to bite on** — there is no artefact to title-page verify.

**The re-score is the OWNER's, and cfd does not take it here.** Line 510's own
conditional was *"If it is not held, Ruling 3's logic may bear on V and the cell
should be re-scored"*, and that condition is now met on measurement. Both readings
are named rather than the kinder one being chosen silently:

* **The non-flattering reading** — the Womersley analytic solution reached this lab
  through a textbook, a review or a code, not through a source the lab holds and can
  read; under Ruling 3's logic C-26's **V drops to `NO`** and the row leaves the
  §8.1 rubric gap for `SURVEYED` at **0 green**.
* **The alternative** — Ruling 3 is written about **P**, and Ruling 4 puts an
  **exact/analytic solution** squarely in **V** without conditioning V on holding the
  originating paper. On that reading C-26's V stands and only the provenance note
  changes.

**cfd states its own inclination and does not act on it: the non-flattering reading.**
This file's §0 stance is that cfd applies the owner's rubric and does not invent one,
and extending a P-clause to V is a rubric extension, not an application. **Referred
to the verification team as owner of `docs/COVERAGE_MATRIX.md`. C-26's cells are left
exactly as they stand at line 247 pending that ruling, and this amendment claims no
authority to move them.**

### 11.6 What this amendment does NOT change

* **No V, G or P cell changes value.** C-15 P stays `NO`; C-18 P stays withdrawn;
  C-26 V is untouched and referred.
* **No tier changes.** C-15 stays `SURVEYED`; C-18 stays `NOT HELD`; C-26 stays in
  the §8.1 rubric gap.
* **The census in §7 is unchanged**, including *"They cannot see a green P at all.
  Zero of 82."* **A verified source is not a green P.** Under Ruling 4 a green P
  needs the measured-reality source **and** a pre-registration on disk gating the
  comparison; §11.2 supplies the first and not the second.
* **No gate, threshold, cap or label anywhere in the lab is altered by this section.**

### 11.7 Cost

**Predicted 0 core-minutes of solver time; actual 0 core-minutes of solver time.** No
solver, no mesher, no MPI rank. The spend is three `pdftoppm` renders, one
`pdftotext` sweep over 610 PDFs, two `find` sweeps and a handful of greps — all
single-rank reads. **Not instrumented, and therefore reported as an estimate under 3
core-minutes — an estimate, not a measurement**, and labelled so rather than quoted
as if a log backed it.

**No `docs/COST_CALIBRATION.md` row is due, and this is a ruling and not a lapse.**
Rule 12's estimate-versus-actual duty attaches at the completion of a *compute*
process; a process with **no core-minutes has no actual to compare against an
estimate**, and inventing a denominator would corrupt the ledger. The cfd supervisor
ruled this standing on 2026-08-25: **zero-compute dispatches add no calibration row.**
Version 2's §10 reached the same conclusion independently and is consistent with it.

**Submissions are parked.** Nothing in this amendment is filed, sent, uploaded or
registered outside this box.
