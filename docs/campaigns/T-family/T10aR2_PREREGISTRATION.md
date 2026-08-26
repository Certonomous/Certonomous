# T10aR2 — the 2LI ladder: H-3(a) ceiling refinement of T10a-R, pre-registration (FROZEN, BUILT, NOT FIRED)

**Document v1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS ITERATED ON ANY
`R2_*` CASE.** Campaign T, rung **T10aR2**, directive Sanaa **H-3(a)** (*"T10a
follow-through: the ceiling miss gets a refinement arm (discretization finding,
cheap)"*), the refinement `docs/LAB_STATE.md` §7 lists next (*"H-3a T10a
ceiling refinement (EXACT, cheap)"*). Run tree
`verification/runs/T-family/T10aR2_runs/`. Verdict vocabulary fixed by
`CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED
/ PENDING.** Tier: **EXACT-tier follow-through, as the parent T10a-R** — every
row is PASS or GATE FAIL against a prediction registered here with a numeric
interval and a named falsifier; the reference is T10a's registered σ_OF exact
enclosure flux. Nothing here authorises a launch: **the fire order is the
heat-transfer supervisor's**; the queue entries are prepared in the
registering lane's scratchpad and dropped by the supervisor alone
(`QUEUE_ENTRY_STANDARD.md` §1).

**Scope: the BOX only.** No spheres (H-3(b)). **This arm grades NOTHING against
T10a's band; T10a (GATE FAIL) and T10a-R (GATE FAIL, 5 PASS / 4 GATE FAIL / 0
NOT A RESULT, `T10aR_RESULTS.md` §6) are closed and unchanged.**

**Condition (`CLAUDE.md` rule 2), and how it was checked.** At the moment this
file is committed, `T10aR2_runs/` holds the six instruments of §9,
`T10aR2_registered.json`, `log.build_preprocess`, and three case directories
`R2_c`, `R2_m`, `R2_f`, each holding `0.orig/ constant/ system/ BUILD.txt
CASE.txt log.blockMesh log.checkMesh.build log.viewFactorsGen
log.viewFactorsGen.time viewFactorField.build` and **no `0/`, no numeric time
directory, no `log.solve`, no `log.launch`**; the run root holds **no
`STATUS.R2_*`, no `DONE.R2_*`, no `gate_t10aR2.json`** (checked with `ls` and
`find -regex` immediately before the commit; `mark_done_t10aR2.py` and
`analyse_t10aR2.py` both **refuse on the live tree today**, `exit 2`). **Zero
solver core-minutes have been spent on this rung.** What did run, disclosed:
the **mesh-side preprocessing** (`blockMesh`, `checkMesh`, `viewFactorsGen`)
on the three cases at build, 2026-08-26 16:27–16:30Z — the Charter §2d class
of step the parent T10a-R ran before its own freeze commit — **205.8 s =
3.43 core-min, no solver, no `qr`**; and one **two-iteration smoke of `R2_c` in
a scratch root outside the repository** (§8: real `buoyantSimpleFoam`,
`endTime 2`, rc 0, `Time = 2`, `End`, 1.5 s), whose fields exercised the
comparator's live reader controls (§5) and are not in the run tree. **The
builder removed the `0/viewFactorField` the generator writes** (kept beside
the case as `viewFactorField.build`, not read by the solver) so that the run
tree holds no `0/`; the launcher creates `0/` from `0.orig` and touches `0/T`
last (§8).

**Provenance of the build.** A previous lane built the cases, the builder, the
launcher, the marker and `T10aR2_registered.json` and died on a usage limit
before writing this document or any comparator. This lane read every file,
ran and completed the selftests, wrote the comparator this rung was missing
(§6), diffed everything against the parent (§7), and repaired what §7.3 lists
— before anything was committed and before anything ran.

---

## 0. What the parent left open, and what R2 refines

T10a-R (`T10aR_RESULTS.md`) answered two things on the **2AI** ladder and one
thing at the **f level only**: (i) the band-smaller-than-error pattern does
**not** persist at a fourth level — the m/f/x triple is CONVERGING at p 0.685,
the Fs = 1.25 band opens to 0.147 % and covers the 0.0799 % error (RX3
falsified); (ii) tightening every solver tolerance moves **not one bit** of
any flux (RS2 identity); (iii) **switching the view-factor integration from
2AI midpoint to 2LI contour (`distTol` 8 → 80) at the f mesh moved every row
toward exact** — B1 by 0.046 %, B2 by 0.175 % — against a registered
prediction of ≤ 0.010 % (RQ1/RQ2 GATE FAIL, the analyst's reservation
confirmed). Its §8 stated the limit: *"R-q does not say which view factors
are right … 2LI is closer is measured against the continuous reference and is
not a proof that 2LI is the correct discretisation"*, and R-q existed at one
mesh only. **What is open: is the 2LI ladder itself CONVERGING, at what
order, does its remaining miss at f (0.07857 %, R_q) shrink with the mesh at
the same first-order-like rate the 2AI ladder showed (level-error ratios
1.66 / 1.50), and does the 2LI band at f cover the 2LI error?** That is this
arm's whole subject: the R-q knob applied at **every** level of the frozen
c/m/f family, one change per case, the ladder graded as the parent graded
its own.

## 1. The three cases — one registered change each from the frozen T10a level

`build_t10aR2.py` (§9) imports the frozen `build_t10a.py` (blob `37f99fb4`)
and calls its own dictionary writers — it copies no text — then **refuses**
unless every file it did not register as changed is byte-identical (sha256)
to the frozen T10a level and the one it did register is not, in either
direction (`verify()`), printing the count **from the values compared** (the
`T10aR_RESULTS.md` §9 literal-sentence defect is not repeated). Measured at
build (`log.build_preprocess`): *"14 files byte-identical, 1 file changed on
1 line: `distTol 8;` → `distTol 80;`"* on every case.

| case | from | `N`/m | divisions | cells (`log.checkMesh.build`) | radiating faces | the ONE change | ratio to previous |
|---|---|---:|---|---:|---:|---|---:|
| `R2_c` | `B_c` | 16 | 16 16 8 | **2 048** | 1 024 | `constant/viewFactorsDict` `distTol` 8 → **80** | — |
| `R2_m` | `B_m` | 26 | 26 26 13 | **8 788** | 2 704 | same | 1.6250 |
| `R2_f` | `B_f` | 42 | 42 42 21 | **37 044** | 7 056 | same | 1.6154 |

Geometry 1 × 1 × 0.5 m, six black patches (floor 600 K, ceiling 300 K, x-walls
400 K, y-walls 350 K, ε = 1), `GaussQuadTol 0.01`, `smoothing false`,
`radiationProperties` (`constantEmissivity true; useDirectSolver true`),
`fvSchemes`, `fvSolution`, `controlDict` (`endTime 20`, `writeInterval 5`,
four checkpoints), `g = (0 0 0)`, thermo, turbulence and every `0.orig` field
are the frozen T10a box, unchanged. As in T10a and T10a-R the GCI uses the
**nominal** r = 1.6 of the frozen `analyse_t1c` (the comparator refuses if
Fs/r differ from that module's); the built ratios above are stated and
printed, never silently reconciled. **`R2_f` is the identity twin of
`T10aR_runs/R_q`** (same mesh, same `distTol 80`): the RR1 precondition
`sha256(R2_f/constant/F) == sha256(R_q/constant/F)` **already holds at build**
— both `801700cf89dbd7b5…` — so the generator is deterministic across the
four days between the two builds; recorded here so it cannot later be
presented as a finding.

### 1.1 Birth certificate and the generation cost already paid

| case | blockMesh rc / s | checkMesh rc / s | max aspect | max skewness | non-orth | `viewFactorsGen` rc / wall s / peak RSS | `constant/F` bytes | `F` sha256 (first 16) |
|---|---|---|---:|---:|---:|---|---:|---|
| `R2_c` | 0 / 0.25 | 0 / 0.24 | 1 | 0 | 0 | 0 / **4.35** / 0.10 GB | 18 383 786 | `727039bea6460a63` |
| `R2_m` | 0 / 0.27 | 0 / 0.29 | 1.000 | 2.3e-14 | 0 | 0 / **27.79** / 0.52 GB | 129 652 037 | `997aa5ff494da022` |
| `R2_f` | 0 / 0.39 | 0 / 0.42 | 1.000 | 4.5e-14 | 0 | 0 / **173.66** / 2.73 GB | 885 438 151 | `801700cf89dbd7b5` |

`Mesh OK` on all three (`log.checkMesh.build`, sha256 `11221857…` /
`d256a97a…` / `a543e6f0…`). Generation at load average 11.9–12.6 (contended,
`nice 15`): 205.8 s total = **3.43 core-min**, spent before this freeze, no
solver. The parent's `distTol 80` cost 221 s at the same f mesh under 12
solvers; 173.66 s here. `constant/F`, `globalFaceFaces`, `mapDist`,
`polyMesh` and `viewFactorField.build` are **not committed** (845 MB at f; the
family convention); their sha256 and sizes are in each `BUILD.txt`, which is.

## 2. Registered rows — prediction, interval, falsifier (`T10aR2_registered.json` `rows`)

`dev` = 100·|value − exact|/|exact| with exact = the σ_OF B1 ceiling
**−3265.532221 W/m²** (T10a); `e_l` = value_l − exact; `move` = q_2LI − q_2AI
at the same mesh (signed, W/m²; the parent measured +1.504358 at f).

**Two branches, registered before the run so the measurement discriminates
them** (`branches_registered_before_the_run`): **H1** — the 2AI→2LI move is
mesh-independent in W/m² (+1.504 at every level): 2LI errors −8.628 / −4.583
/ −2.566, ratios 1.883 / 1.786, p 1.4805, band 0.07673 %, dev/band 1.024.
**H2** — the move scales with the level error (×0.630 at every level): errors
−6.385 / −3.836 / −2.566, ratios 1.664 / 1.495, p 1.482, band 0.0482 %,
dev/band 1.63. **The registered point is H1**; the intervals below contain H1
and exclude H2 on RR4, RR5 and RR6 (the comparator's selftest proves both
branches land where this table says).

| row | quantity | point | **interval (PASS)** | falsifier | needs the triple? |
|---|---|---:|---|---|---|
| **RR1** | **IDENTITY (Charter §2a)**: max |qr(R2_f) − qr(R_q)| over every radiating face, W/m² | 0.0 | **[0, 0]** | any nonzero difference, given the precondition (F byte-identical; if not, NOT A RESULT and the non-determinism reported) | no |
| **RR2** | observed p of the 2LI c/m/f triple for B1 | 1.48 | **[1.0, 2.0]** | p outside; a non-CONVERGING triple → **NOT A RESULT**, no verdict | yes |
| **RR3** | B1 dev at the 2LI f level, % | 0.07857 | **[0.078, 0.0792]** | outside (given RR1 this is the R_q number: the row states the headline, it does not test the physics) | no |
| **RR4a** | 2LI level-error ratio |e_c|/|e_m| | 1.883 | **[1.70, 2.10]** | outside; H2 gives 1.664 | no |
| **RR4b** | 2LI level-error ratio |e_m|/|e_f| | 1.786 | **[1.70, 2.10]** | outside; H2 gives 1.495 | no |
| **RR5** | dev ÷ GCI band at the 2LI f level | 1.024 | **[0.85, 1.30]** | > 1.30 (H2: the band-smaller-than-error pattern persists at 2AI strength) or < 0.85 (the band covers the error, as at T10a-R's fourth level) | yes |
| **RR6a** | move of B1 at level c (R2_c − B_c), W/m² | 1.504 | **[1.0, 2.0]** | outside; H2 gives 3.75 | no |
| **RR6b** | move of B1 at level m (R2_m − B_m), W/m² | 1.504 | **[1.0, 2.0]** | outside; H2 gives 2.25 | no |
| **RR7** | raw row-sum max defect of the written 2LI F, level f ÷ level c | 1.0 | **[0.7, 1.3]** | outside (the defect DOES move with the mesh under 2LI) | no |

**Reported, never graded:** B0 / B2 / B3 under the same 2LI ladder (triple
state, p, band, dev/band, sign-corrected Richardson, moves at c/m/f);
`closure_raw` and the T10a closure guard per case; row-sum defect per patch
per level; the Richardson extrapolate in both the shared (sign-defect) and the
corrected form side by side, graded on neither (T10a-R NEW INSTRUMENT 1).

## 3. Rule 5, the floors, and what refuses — the parent's gates, unchanged, plus the shared floor names

- **Rule 5 order** (D440, carried from T10a §5.2 / T10a-R §0): (1) any level
  not iteratively CONVERGED → the comparator **refuses** (`exit 2`; no triple
  is formed from an unconverged level); (2) a row that is a function of the
  triple (RR2, RR5) is **NOT A RESULT** unless the triple is CONVERGING, with
  value, triple and state printed and no GCI; the single-level rows carry the
  triple state beside them; (3) CONVERGING → PASS / GATE FAIL against the
  registered interval, GCI at Fs = 1.25 printed. Exactly the parent's
  semantics (its RX1/RX4 were graded beside a triple state; RX2/RX3 needed
  CONVERGING).
- **The observed-order floors — the SHARED names (`MESH_STANDARD.md` §10.5,
  chief ruling `01967a7b`).** `analyse_t10aR2.py` **imports `STAGNANT_FLOOR`
  and `P_MIN` from `scripts/roache_triple.py`** (blob `78e56a3b`) and defines
  neither. The frozen `analyse_t1c.gci` the parent used (via `analyse_t10a`)
  already carries the 0.5 floor as its own `STAGNANT` branch; the comparator
  **drives that branch at p = 0.49 / 0.51 at every run and refuses if the
  frozen floor is not the shared one**, and labels `|p| < P_MIN = 0.05`
  `DEGENERATE` beside the frozen state. **Verdict-equivalent to the parent**:
  its RX2 p = 0.685 was CONVERGING and stays so; STAGNANT and DEGENERATE are
  both NOT A RESULT. **Ground, rung-specific as this family rules it:**
  p_expected = 1.48 (RR2's point, the parent 2AI order) ÷ 3 = 0.49, taken as
  the family value 0.5; below it adjacent-level errors differ by < 1.6^0.5 =
  1.26×. The floor can only move a row INTO NOT A RESULT.
- **Convergence** (T10a §5.5, frozen `iterative_convergence`): `qr` identical
  value for value between the last two written checkpoints (15 and 20); no
  `residualControl` (L-141).
- **Planted-zero control** (rule 3, frozen `planted_zero_control`):
  **+1.234e-03 W/m²** planted by line index into a scratch copy of the earlier
  checkpoint's `qr`, read back through the same reader, the recovered maximum
  change required to equal **exactly** `fl(old + plant) − old` (T10a §5.5's
  exact-float rule); failure → refusal. Never writes into a case tree.
- **Closure guard**: `|c_raw − c_F| > 1e-2` (T10a's registered threshold, read
  from `T10a_registered.json`) makes a case VOID and withdraws every row →
  NOT A RESULT.
- **Mesh read-back**: box extents to 1e-12, every patch area to 1e-10, through
  the frozen `measure()`; refusal on mismatch.
- **Lean F instrument** (T10a-R NEW INSTRUMENT 2): validated against the
  frozen `read_F`/`dense_F`/`radiosity_on_F` on **every** R2 case
  (bit-identical matrix, radiosity and reciprocity ≤ 1e-12 relative) or the
  comparator refuses; then used for RR7 and the reported diagnostics.
- **Provenance**: the comparator prints the sha256 **and git blob** of every
  frozen instrument it imports, of itself and of the registered JSON, at every
  run.
- **Completion**: `mark_done_t10aR2.py` (§9), the strict rule with the age
  guard, L-342 field classes: **physics-critical** — in-wrapper `rc = 0`,
  `End`, last time == 20, `T` and `qr` present, `ExecutionTime` count == 20,
  every field newer than the case's own `0/T`; **absent STATUS → refusal
  (`exit 2`)**; **infrastructure** — `wall_s timeout_s ranks core_min capped
  checkmesh_rc started_utc ended_utc solver_path note` → NOT MEASURED,
  disclosed, grade proceeds; **`capped` is never a conjunct**. The runner's
  own `STATUS.<case_id>` in the case directory is an infrastructure record the
  marker never reads.

## 4. Cost — rule 12, from the parents' MEASURED figures

**Basis.** `T10a_runs/STATUS.B_{c,m,f}`: solve wall **1 / 13 / 389 s**
(serial, 2AI); `T10aR_runs/STATUS.R_q`: **2 639 s wall, 664 s `ExecutionTime`**
for the **identical** f-level 2LI case under 12 concurrent solvers at
`nice 15`; `docs/COST_CALIBRATION.md` **C-1** (T10a-R): gross/predicted
**2.77×**, attributed to contention plus the generator's under-predicted
memory at n = 18 496. The 2LI matrix does not change the dense-LU cost (same
n); generation is already paid (§1.1). The R2_c smoke: two iterations in
1.47 s, `checkMesh` 0.24 s.

| case | **POINT core-min** (derivation) | CEILING core-min (derivation) | **cap core-min** | `timeout` s = cap × 60 / 1 | cap ÷ ceiling |
|---|---:|---:|---:|---:|---:|
| `R2_c` | **0.03** (B_c `ExecutionTime` 1.63 s) | 0.05 (1 s × 2.77) | **10** | **600** | 200× (startup + reading an 18 MB F dominates a 1 s solve) |
| `R2_m` | **0.22** (B_m 13 s) | 0.60 (13 s × 2.77) | **30** | **1 800** | 50× |
| `R2_f` | **11.07** (R_q `ExecutionTime` 664 s, CPU, contended) | 43.98 (R_q wall 2 639 s, the measured contended figure) | **120** | **7 200** | 2.7× (10.8× the CPU time) |
| **total** | **11.32** (0.189 core-h) | 44.63 (0.744 core-h) | **160** (2.67 core-h) | | |

**USD at $0.0513/core-h, derived, not measured, reported-by-owner rate
(`COMPUTE_BUDGET_CHARTER.md` §5): POINT $0.0097, CEILING $0.0382, cap
$0.137.** Generation already spent: 3.43 core-min ($0.0029 derived). Caps are
runaway guards, not budgets; the ratio cap/POINT is large on `c` and `m`
because a 1–13 s solve is dominated by fixed cost, and small in absolute terms.
**Consequence for the queue runner's cap watch, disclosed:** with
`cost_core_min_estimate` = POINT (the family's entry convention, T3 `R_ff`),
the runner's `CAP_OVERRUN.txt` note (1.10 × POINT × 60 s = 2 s / 15 s for `c` /
`m`) may be written before the launch argv returns; it reports and never
kills (`QUEUE_RUNNER.md` step 5), and the wrapper's own `timeout` at the
registered cap is the stop. **Memory floor 3 GB**: R_q's solve measured
`maxRSS` 1.81 GB on the identical case (`STATUS.R_q`); the R2_f generation's
2.73 GB is already paid. Ranks 1 on every level (F15's ruling; the parent ran
serial). Estimate-versus-actual lands in `docs/COST_CALIBRATION.md` at
completion, beside C-1.

## 5. Predictions as numbers, and what the smoke measured before the freeze

The rows of §2 are the predictions: **P-RR1 0.0 [0, 0]; P-RR2 1.48 [1.0,
2.0]; P-RR3 0.07857 [0.078, 0.0792]; P-RR4a 1.883 [1.70, 2.10]; P-RR4b 1.786
[1.70, 2.10]; P-RR5 1.024 [0.85, 1.30]; P-RR6a 1.504 [1.0, 2.0]; P-RR6b 1.504
[1.0, 2.0]; P-RR7 1.0 [0.7, 1.3]** — all H1. **Registered expectation stated
plainly: the 2LI ladder is CONVERGING at the parent's implied order (p ≈ 1.48)
with the band-smaller-than-error pattern still present at f (dev/band ≈ 1.02),
i.e. the 2LI improvement is a mesh-independent shift of the whole ladder.** H2
(RR4/RR5/RR6 GATE FAIL) would say the 2LI improvement scales with the
discretisation error — that the two are the same thing seen twice — and is
the informative surprise; a CONVERGING triple with p < 1.0 or dev/band < 0.85
would say the 2LI ladder is already in the regime T10a-R's fourth 2AI level
reached. Either is reportable; none is retro-fitted.

**Live reader controls on the R2_c smoke (2 checkpoints, scratch):**
iteratively **CONVERGED** (max change 0.0 between t = 1 and 2, as fixed-T walls
require); planted **+1.234e-03 W/m² recovered as 0.0012340000002950546** =
`fl(old + plant) − old` exactly; lean F reader == frozen reader
**bit-identical** on the 2LI F (n = 1 024); 2LI F diagnostics: row-sum max
defect **0.01898**, python-vs-solver 3.3e-15, closure excess 8.8e-17 (not
VOID). These are instrument facts, not physics numbers.

## 6. The comparator — the parent's frozen `analyse_t10aR.py` CANNOT take these levels; a NEW reader is registered and frozen in this commit

`analyse_t10aR.py` (HEAD blob **`bf13efee`**, byte-identical in the worktree)
hard-codes its case list `("B_m", "B_f", "R_x", "R_q", "R_s")`, routes by the
`R_` prefix, and grades the RX*/RQ*/RS* row table of `T10aR_registered.json`;
it cannot take `R2_c/R2_m/R2_f` and is not amended (the `analyse_t3.py` →
`analyse_t3_rff.py` situation, T3_R_FF AMENDMENT 1). **`analyse_t10aR2.py`
(§9) IMPORTS it** and reuses, by name: `in_tree` (the tree shim that
redirects the frozen `analyse_t10a`'s `HERE` / `REG["cases"]` in-process and
restores them, proved in the selftest), `richardson_corrected`,
`read_F_dense_stream`, `radiosity_lean`, `reciprocity_max_defect_blocked`,
`F_diagnostics_lean`, `validate_lean_against_frozen` — and through it the
frozen `analyse_t10a` (`3c70263b`: `measure`, `row_value`, `mesh_patches`,
`time_dirs`, `read_qr_all`, `sigma_used`, `iterative_convergence`,
`planted_zero_control`, `gci` = `analyse_t1c.gci` `3d566802`, `CLOSURE_TOL`,
`REG["box"]`) and `exact_t10a` (`63c2cdef`). Its own routing helpers
(`tree_of`/`spec_of`/`case_dir`) are redirected in-process by `r2_names` for
the lean-F calls and restored (proved). It reads the frozen T10a tree for
`B_c/B_m/B_f`, the frozen T10a-R tree for `R_q`, and this tree for `R2_*`;
refuses on any absent `DONE` marker among the eight; writes
`gate_t10aR2.json` only.

**`--selftest`: 20/20 under `python3` and 20/20 under `python3 -O`** (with the
smoke; 17/17 without): AST 0 (the counter sees a planted assert); the shared
floors imported with no local definition; the frozen `gci` floor driven at
0.49 → STAGNANT / 0.51 → CONVERGING; DEGENERATE labelling at p = 0.02; Fs/r
agreement; shim restoration; **H1 → p 1.4798, band 0.07680 %, dev/band 1.023,
ratios 1.882 / 1.786, every row PASS; H2 → ratios 1.664 / 1.496, dev/band
1.62, move_c 3.75 → RR4a/RR4b/RR5/RR6a GATE FAIL with RR2/RR3 PASS** (the
registered discrimination, as a value control); an OSCILLATORY triple → RR2
and RR5 NOT A RESULT, single-level rows still graded; a VOID level withdraws
all nine rows; RR1 0 → PASS / 1e-14 → GATE FAIL / precondition failed → NOT A
RESULT; the closed RR5 interval edges; the corrected Richardson within 0.1 %
of exact on H1; the three smoke controls of §5; **driven refusals under both
interpreters (rc 2, `REFUSE` printed): missing `DONE`; a frozen floor that
moved; an unconverged level.**

## 7. Instruments against the parent — the supervisor's check-1 table

| item | T10a-R (frozen) | T10aR2 | class of change |
|---|---|---|---|
| reference, rows, bands | RX1–RX5, RQ1–RQ2, RS1–RS2 vs registered intervals | RR1–RR7 (§2) vs registered intervals, same σ_OF exact | new rows for a new question; no parent row re-graded |
| rule-5 order, D440 refusal on an unconverged level | yes | **identical** | none |
| observed-order floor | `analyse_t1c.gci`'s own `p < 0.5 → STAGNANT` (unnamed) | the same frozen branch, **named by the shared `STAGNANT_FLOOR` and driven at every run; `P_MIN = 0.05` → DEGENERATE label added** | **verdict-equivalent: STAGNANT below 0.5 / DEGENERATE below 0.05, same as the parent's semantics** |
| Fs 1.25, nominal r 1.6, refusal if the module differs | yes | identical | none |
| convergence rule (qr identical between checkpoints) | frozen | identical (imported) | none |
| planted zero +1.234e-03 W/m², exact-float rule | frozen | identical (imported) | none |
| closure guard 1e-2, mesh read-back | frozen | identical (imported) | none |
| lean F validation refusal (bit-identical, ≤ 1e-12) | on B_m/B_f/R_q/R_s | on **R2_c/R2_m/R2_f** | same rule, own cases |
| identity row | RS2: R_s vs B_f (solver bundle) | RR1: R2_f vs R_q (build determinism) | new identity, same form |
| Richardson corrected | reported, never graded | identical | none |
| completion rule | `mark_done_t10aR.py`: rc, End, last time, T+qr, count, age; no `capped` | `mark_done_t10aR2.py`: same six physics clauses; **absent STATUS → refuse**; `INFRA` tuple incl. `capped` disclosed, never a conjunct | L-342 applied |
| launcher | `preprocess_t10aR.sh` + `run_one_t10aR.sh` + `launch_t10aR.sh` (G1 lock, G2 `/proc` scan, G3 time dirs, no-F refusal), `rm -rf 0 && cp -r 0.orig 0` | `launch_t10aR2.sh` (`launch_k0f.sh` / `launch_t3_rff.sh` form): refuses `--ranks ≠ 1`, `--timeout ≠ registered`, unregistered case, existing `STATUS`, `0/`, time dir, running pid, missing mesh / fields / `constant/F` + `globalFaceFaces` / solver; `0/T` touched last; solver foreground under `timeout`, rc in-wrapper, `capped` witness, `exit "$RC"` | form changed, same guards; preprocessing moved to build |
| builder | `build_t10aR.py` (`verify()` sound, final sentence a literal — `T10aR_RESULTS.md` §9) | `build_t10aR2.py`: same `verify()` in both directions, the sentence printed **from the compared values**; runs the preprocessing and records wall / RSS / F sha per case | defect not repeated |

### 7.3 Repairs this lane made to the dead lane's files (all pre-first-compute; none moves an interval, threshold or cap)

1. **`analyse_t10aR2.py` written** — the rung had no comparator (§6).
2. `mark_done_t10aR2.py`: `--root` and a forge-based `--selftest` added (the
   dead lane's marker had none); **9/9 under both interpreters**: clean →
   DONE; rc=1 → NOT DONE; no End; short count; missing field; stale fields;
   absent STATUS → exit 2; all infrastructure fields absent → DONE with NOT
   MEASURED; AST 0. Clauses and classes unchanged.
3. `launch_t10aR2.sh`: `--timeout` must **equal** the registered value (was
   "not exceed"); an existing `STATUS` refused before anything is written.
   `bash -n` clean; ARM 1 **0 suspect globs**; **six refusal arms driven on a
   scratch copy** (ranks 2; timeout 100; timeout 601; existing STATUS;
   existing `0/`; `constant/F` removed) — each rc 2, nothing written.
4. `T10aR2_registered.json`: `tier` stated; `roache_floors` block added
   (§3); the cost block given its per-level POINT / CEILING / cap /
   derivation (§4; the dead lane's totals 8.1 / 50.0 core-min carried a
   generation term now disclosed as already spent and a 389 s f-solve basis
   now replaced by the identical case's measured 664 s / 2 639 s). **Rows,
   intervals, falsifiers, caps and timeouts are the dead lane's, unchanged.**
5. `build_t10aR2.py`: unchanged (AST 0; it built the cases and refuses to
   overwrite them).

## 8. Launch discipline

`launch_t10aR2.sh --case-dir DIR --timeout S --ranks 1 --no-detach` (the
queue entries' argv; without `--no-detach` it re-execs once under `setsid`):
refuses per §7's row before writing anything; runs `checkMesh`
(`log.checkMesh`, infrastructure); `cp -r 0.orig 0`, `touch 0/T` last; then
`timeout $S buoyantSimpleFoam -case DIR` in the foreground, `RC=$?`,
`STATUS.<case>` in the run root with `rc wall_s ranks core_min timeout_s
capped checkmesh_rc solver solver_path note started_utc ended_utc`,
`exit "$RC"`. The solver reads `constant/F`, `globalFaceFaces`, `mapDist`
written at build; `0/viewFactorField` is not needed (the smoke ran without
it: `Selecting radiationModel viewFactor`, rc 0).

```
/home/ubuntu/Certonomous/verification/runs/T-family/T10aR2_runs/launch_t10aR2.sh \
    --case-dir /home/ubuntu/Certonomous/verification/runs/T-family/T10aR2_runs/R2_<c|m|f> \
    --timeout <600|1800|7200> --ranks 1 --no-detach
```

## 9. The freeze set — committed in the same commit as this document

Git blobs with `git hash-object` on the exact files committed; sha256 first 16.

| file | git blob | sha256 | lines / note |
|---|---|---|---:|
| `verification/runs/T-family/T10aR2_runs/analyse_t10aR2.py` | **`a252463b`** | `efe25789f09f77a9` | 514; AST 0; selftest 20/20 both interpreters (with smoke) |
| `verification/runs/T-family/T10aR2_runs/mark_done_t10aR2.py` | **`4fbff6a7`** | `4b2e5e691772dfc9` | 256; AST 0; selftest 9/9 both interpreters |
| `verification/runs/T-family/T10aR2_runs/build_t10aR2.py` | `e85f8cb4` | `38d2be039e498268` | 246; AST 0; the file that built the cases |
| `verification/runs/T-family/T10aR2_runs/launch_t10aR2.sh` | `dd58c649` | `72a1cc25879787a3` | 161; ARM 1 0 globs; 6 arms driven |
| `verification/runs/T-family/T10aR2_runs/T10aR2_registered.json` | `d52c2ac6` | `d53dafab8be89e7f` | 262; rows, intervals, floors, caps, costs |
| `verification/runs/T-family/T10aR2_runs/log.build_preprocess` | `4ca7c544` | `b19d29dd47f8be58` | 38; the build/preprocess record |
| `T10aR2_runs/R2_{c,m,f}/system/{blockMeshDict,controlDict,fvSchemes,fvSolution}`, `constant/{boundaryRadiationProperties,g,radiationProperties,thermophysicalProperties,turbulenceProperties,viewFactorsDict}`, `0.orig/{T,U,p,p_rgh,qr}`, `CASE.txt`, `BUILD.txt`, `log.blockMesh`, `log.checkMesh.build`, `log.viewFactorsGen`, `log.viewFactorsGen.time` | committed | | dictionaries, birth certificates, generation records; `F`/`globalFaceFaces`/`mapDist`/`polyMesh`/`viewFactorField.build` not committed (§1.1) |

Frozen inherited instruments, by HEAD blob, byte-identical in the worktree at
the freeze: `analyse_t10aR.py` `bf13efee`, `analyse_t10a.py` `3c70263b`,
`exact_t10a.py` `63c2cdef`, `build_t10a.py` `37f99fb4`, `analyse_t1c.py`
`3d566802`, `scripts/roache_triple.py` `78e56a3b`,
`scripts/check_launcher_can_launch.py` `0035b098`. Verify the frozen file is
the file that ran by hashing it against the committed blob.

## 10. What this arm cannot see

- **Nothing about the spheres** (H-3(b)); nothing about T10a's or T10a-R's
  verdicts, which stand.
- **RR1 is an identity, not physics**: given a deterministic generator, R2_f
  *is* R_q, and RR3 is R_q's number restated. The physics is in RR2, RR4–RR7.
- **Which view factors are right** stays unanswered (the parent's §8 caveat):
  2LI moves the ladder toward the continuous exact; the exact discrete
  enclosure's view factors are not known.
- No asymptotic claim from a three-level ladder; the observed p is quoted
  beside every band.
- No participating media, no grey non-black surface, no `faceAgglomerate`, no
  iterative radiosity solver, no parallel operation, no production mesh —
  every T10a §9 bypass inherited.
- Nothing here authorises a launch or a send (rule 7: **SUBMISSIONS REMAIN
  PARKED**). No frozen T10a or T10a-R file is modified.

## 11. Status and certificate lines

**Status: PRE-REGISTERED, BUILT (incl. mesh-side preprocessing, 3.43
core-min), NOT FIRED; queue entries prepared (validator ACCEPTED, in the
registering lane's scratchpad only), NOT dropped — enqueueing is the
supervisor's check 4.**

- `R2_c`: built 2026-08-26T16:27:08Z, 2 048 cells / 1 024 faces, Mesh OK,
  F 18.4 MB; no `0/`, no time dir, no STATUS; POINT 0.03 / cap 10 core-min,
  timeout 600 s.
- `R2_m`: built 16:27:36Z, 8 788 / 2 704, Mesh OK, F 129.7 MB; POINT 0.22 / cap
  30, timeout 1 800 s.
- `R2_f`: built 16:30:31Z, 37 044 / 7 056, Mesh OK, F 885.4 MB
  (sha `801700cf…` == R_q's); POINT 11.07 / cap 120, timeout 7 200 s.
- Solver core-minutes on the rung at the freeze: **0**.

---

## AMENDMENT 1 — 2026-08-26 (PRE-FIRST-COMPUTE): the launcher's cwd-holder guard refused its own parent shell under the queue runner's `cd` form — three zero-compute refusals; guard re-frozen

**Document version 1.0 -> 1.1 (1.0 = the `fb4bf7e2` freeze; this amendment declares the numbering). Lines whose number changed above this section: 0** (appended to the worktree copy after verifying it byte-identical to the HEAD blob `1c28eec7`). Ruled by the heat-transfer supervisor `[lab-attributed]` after crash triage (check 2) and a personal read of the diff; drafted by the T5 lane. **Condition (`CLAUDE.md` rule 2), and how it was checked:** no solver has run on this rung — `R2_c`, `R2_m`, `R2_f` hold only `0.orig BUILD.txt CASE.txt constant log.* system viewFactorField.build` plus the runner's two infrastructure files (`ls` at 17:40Z); no `0/`, no numeric time directory, no in-wrapper `T10aR2_runs/STATUS.R2_*`, no `DONE.*`; `mark_done_t10aR2.py` refuses `no STATUS.R2_c`. **Solver core-minutes on the rung: 0.**

**What happened.** The queue runner (`scripts/queue_runner.py`, pid 189825) launched the three entries and `launch_t10aR2.sh` (blob `dd58c649`) refused each within one second, verbatim from `<case>/launcher.queue.out`:

- `R2_c` (runner `17:24:17Z LAUNCHED … pid=280743`): `REFUSE: pid 280744 is already running in R2_c`
- `R2_m` (`17:25:22Z … pid=284859`): `REFUSE: pid 284860 is already running in R2_m`
- `R2_f` (`17:26:27Z … pid=286905`): `REFUSE: pid 286906 is already running in R2_f`

**Ground.** The runner's fixed launch form is `setsid nohup bash -c 'cd <cwd>; <argv> > <cwd>/launcher.queue.out 2>&1; …'` (`docs/standards/QUEUE_RUNNER.md` §4; `scripts/queue_runner.py` line 26). That wrapper shell — pid = launch pid + 1 in every row — holds the case directory as cwd and is the launcher's own parent. The frozen guard (lines 133–135) scanned `/proc/*/cwd` for the case directory and excluded only `$$`, so it refused its own launch by construction. The runner's `<case>/STATUS.T10aR2_R2_*` files (`launcher_rc=2`) are INFRA records of the argv's exit (L-342), left in place; the consumed entries sit in `verification/queue/heat-transfer/launched/`.

**The repair — the only change in the file.** The four-line guard is replaced by a lineage-aware one (a `ppid_of()` reader of `/proc/<pid>/stat`, the launcher's ancestor chain `LINEAGE` walked from `$PPID` to pid 1, an `own_lineage()` test that also walks a candidate's ancestors to `$$`, and the same `/proc` scan, which now `continue`s on the launcher's own lineage and still refuses, naming the pid, on any foreign process). Nothing else moves: `--timeout` must still equal the registered cap, `--ranks` 1, the `0/` / time-dir / mesh / field / `F` refusals, `0/T` touched last, solver in the foreground under `timeout`, rc in-wrapper, `capped` witness, `exit "$RC"`. **Driven on a scratch copy of `R2_c` (`endTime 1`, outside the run tree, deleted afterwards):** (a) a planted foreign `sleep` with cwd = the scratch case dir → `REFUSE: pid 299723 is already running in R2_c`, rc 2, the planted pid named; (b) the runner's exact form `bash -c 'cd <scratch case> && launch_t10aR2.sh --case-dir … --timeout 600 --ranks 1 --no-detach'` → guard passed, `checkMesh` rc 0, `buoyantSimpleFoam` reached `Time = 1` and `End`, in-wrapper `STATUS.R2_c` `rc=0 wall_s=1 capped=no note=clean`. No field of the scratch copy was read.

**Freeze set, §9 row for the launcher — STRUCK, not deleted:** ~~`launch_t10aR2.sh` | `dd58c649` | `72a1cc25879787a3` | 161~~ → **`launch_t10aR2.sh` | `59fe37c1` | `602eef12be713d13` | 181; 0 `assert`; the two guard arms above driven.** Every other row of §9 is unchanged. No gate, band, interval, floor, cap, timeout or cost moves; §4's POINT 11.32 / caps 10 / 30 / 120 stand.

**Status after this amendment: PRE-REGISTERED, BUILT, NOT FIRED (three zero-compute refusals on record); re-enqueued as `T10aR2_R2_{c,m,f}_v2.json` citing this amendment's commit.**
