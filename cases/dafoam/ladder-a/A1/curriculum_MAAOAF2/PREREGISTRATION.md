# MAAOAF2 — MA288, `potentialFoam`-baselined settings ladder — **PERMISSION: NOT_FROZEN — DRAFT**

Not frozen, not enqueued, no compute spent. This lane froze nothing, committed nothing and launched nothing;
`dafoam-supervisor` does all three. Nothing leaves the box (rule 7).

**Inherited by reference, restated nowhere:** `../curriculum_MAAOAF/PREREGISTRATION.md` (frozen `3e2257590`,
`ADDENDUM 1` `266f34bfc`) and its `RESULTS.md` (`3858c5890`) — the §1 MA288 diagnosis, `VERDICT_CLASS =
G-NOBAND`, `VERDICT_CEILING = GATE REACHED` (**`PASS` is unreachable here**), 500-iteration arms, np = 1,
α = 4°, the promotion gate, and the `FALSIFIER`. **This item registers only what MAAOAF does not hold.**

## 1. What is inherited as settled, and the two things measured for this item

**`N2` IS THE BASELINE OF EVERY ARM.** `potentialFoam -writePhi` — wired in `fvSolution` as
`potentialFlow{nNonOrthogonalCorrectors 20;}` with a `Phi` solver and never invoked — moved first clip from
iteration **1** to **167** with **zero** clips through 100, and cost **less** than the control (9.100 vs
9.950 core-min). Necessary, not sufficient: clipping regrows (t200 1, t300 4, t400 3, t500 9) to 1021 total,
ending `p initRes 0.6170459`, `he initRes 0.2006319`, cumulative continuity 45.45
(`/home/ubuntu/certonomous-runs/MAAOAF-ma288-init/N2_20260911T023634Z.log`, last `Time = 500` block; first
clip `Bounding p>20000` at log line 3370).

| measured for THIS item | value | artifact |
|---|---|---|
| **MA288 RUN-mesh max non-orthogonality** | **31.503°**, average 1.710°; maxAR 212103.67, max skew 1.3968 | `/home/ubuntu/certonomous-runs/MAAOA/MA288/out/trim.log:505,508,511` |
| **TRAP, and I nearly took it.** `case/checkMesh.log` reads max non-orth **22.749°**, maxAR **97.87** — that is a **4,032-cell** generation-stage mesh at `/mnt/MESH`, **not** the 130,304-cell run mesh. The run mesh's own `checkMesh` is printed inside `trim.log`. | — | `…/MA288/case/checkMesh.log:87,90` vs `out/trim.log:505` |
| **Which `div` terms are already bounded.** `div(phi,e\|h\|K\|Ekp\|nuTilda\|k\|omega\|epsilon)` and `div(pc)` are **ALL already `bounded Gauss upwind`** — first order, maximally bounded, nothing left to tighten. `div(phi,U)` is the only second-order term and **MAAOAF `N3` already tested it** (upwind: 7.5 % fewer clips, iteration-1 clip unchanged). **There is NO `div(phi,rho)` term at all** — `DARhoSimpleFoam` carries density through `rho = ψp`, not a transport equation. | — | `…/MA288/case/system/fvSchemes` |
| `e ↔ T` inversion, **verified against MAAOAF's frozen mapping in both directions**: `e = C_v·T − C_p·T_std`, `C_p 1005`, `W 28.97` → `R 287.003`, `C_v 717.997`, `T_std 298.15`. It reproduces the frozen `5.5e4 → 493.9 K` and `−2.2e5 → 110.9 K` (frozen: 494.0, 111.0). | — | `constant/thermophysicalProperties`; MAAOAF §1 row 4 |

**Consequence for `M3`, registered as a finding, not hidden as a design choice:** the briefed `M3` —
"bounded/limited convection on `rho` and `e`" — **is a NO-OP on both limbs** and is **NOT registered**.
`e` is already `bounded Gauss upwind`; `rho` has no convection term. The one unbounded discrete operator
left is the **gradient** (`gradSchemes default Gauss linear`), which feeds `linearUpwindV grad(U)`, the
`corrected` laplacian's non-orthogonal correction and the `corrected` snGrad. `M3` is redirected there.

## 2. Arms — **each is `N2` PLUS EXACTLY ONE CHANGE.** MA288, α = 4°, np = 1, 500 iterations, `printInterval 1`

| arm | the single change | **prediction, registered now, from a measurement** | refuter |
|---|---|---|---|
| **M1** | relaxation halved as **one scalar damping factor λ = 0.5**: fields `(p\|p_rgh\|rho)` 0.30→**0.15**, equations `(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega)` 0.70→**0.35**. **"Matching" = the ratio α_U/α_p = 7/3 HELD FIXED**, so this is one degree of freedom, not two. **I explicitly REJECT the Patankar reading** α_p+α_U=1 → α_U 0.85: the shipped pair already sums to 1.00, so complementarity would *raise* momentum relaxation on a case whose largest single clip count is `U` (1184 of R0's 3748) — a change in the destabilising direction. | **Onset moves, residual does NOT improve.** N2 survives 167 iterations then degrades, i.e. a marginally unstable fixed point; halving λ halves the correction magnitude per outer iteration. Predict `first_clip_iteration` in **[250, 400]** and last-block max `initRes` **≥ 0.6170** (worse than N2), because halving relaxation also halves the convergence rate at a fixed 500-iteration budget. | **THE CONFOUND IS REGISTERED, NOT DISCOVERED LATER:** if onset lands near **334 ≈ 2×167** *and* the residual at onset matches N2's residual at 167, that is **pure time-rescaling, NOT stabilisation**, and M1 is reported as a null however good the onset looks. |
| **M2** | `fvSolution` `SIMPLE{nNonOrthogonalCorrectors}` **0 → 2** (`potentialFlow`'s 20 untouched) | **A5's reasoning TRANSFERS, a fortiori.** A5P2 broke a fixed point with two correctors that tightened linear tolerances, a tenfold iteration extension and SIMPLEC could not — residual 14,199×, `p` solve 53 inner iterations against 3 — on a mesh at **3.512°** where it was registered as a predicted NO-BREAK (`../A5/curriculum_A5P/PREREGISTRATION.md:134`, `../A5/curriculum_A5P2/RESULTS.md:15`). **MA288 is 31.503°, 8.97× worse**, with `laplacianSchemes corrected` and `snGradSchemes corrected` — fully explicit, unlimited corrections that at `nNonOrthogonalCorrectors 0` are **never iterated inside the outer step** and enter as a lagged source. **Predicted MOST LIKELY of the four to move onset:** `first_clip_iteration` **≥ 250**, total clips **< 1021**, last-block max `initRes` **< 0.6170**. **The aspect ratio is NOT the argument** — AR 212,103 is a different pathology and M2 says nothing about it. | onset within ±15 % of 167 ⇒ non-orthogonality is **not** the degradation mechanism at MA288, the 31.5° reading is a red herring against AR, and the A5 transfer is refuted on a mesh 9× less orthogonal than the one where it worked. |
| **M3** | `fvSchemes` `gradSchemes default`: `Gauss linear` → **`cellLimited Gauss linear 1`** (redirect, see §1) | **Partial, and less than M2.** N3 removed *one* consumer of `grad(U)` and bought 7.5 %; limiting the gradient **at source** touches every consumer — the `linearUpwindV` reconstruction, the non-orth correction on a 31.5° mesh, and the momentum pressure-gradient source. Predict onset in **[200, 300]**, total clips **< 1021**, residual within ±20 % of 0.6170. | onset **≥ 400** or clips 0 ⇒ the limiter, not the corrector, is the missing ingredient, and M2's mechanism is wrong. |
| **M4** | `primalVarBounds` **TIGHTENED to the PHYSICAL range** — `pMin 81060 pMax 121590` (±20 % of 101325); `eMin −1.2014e5 eMax −1.2439e4` (**T = 250.00 / 400.00 K exactly**, by the §1 inversion — note the physical `e` window is **entirely negative**, which is precisely why the shipped `eMin −2.2e5` read as innocuous and is **T = 111 K**); `rhoMin 0.70 rhoMax 1.70` (the `p`–`T` box corners are 0.7061/1.6946); `UMax 300 UMin −300` (3 × freestream 100 m/s; potential-flow peak suction at α = 4° is ~1.3–1.5×). Window **2.55× tighter** than shipped (150 K vs 383 K). | **THE MIRROR OF N1, AND THE POINT IS THE ASYMMETRY.** N1 WIDENED the bounds and died at `Time = 8` of `FOAM FATAL ERROR: Negative initial temperature T0: -1039.448985413342` (`thermoI.H:57`) — the bounds were the only thing keeping the energy field physical. **M4 tightens them so that A CLAMP IS A REFUSAL, NOT A RESCUE: any clip at all means the solve left physics, and the arm is `NOT A RESULT` the moment one fires.** For M4 alone, `first_clip_iteration` **IS the physics-exit iteration by construction.** Predict **1 < first clip ≤ 167**, likely ≪ 167 — the field starts at T 300, p 101325, potential-flow U ≈ 130, all well inside — so M4 measures a departure N2's loose bounds hid. A worse-looking onset here is **the measurement, not a worse arm.** | **zero clips through 500** ⇒ the field never left physics and every clip R0/N2 recorded was an artifact of bound *placement*. Coherent, not impossible: clipping is nonlinear feedback, so a tighter bound does not clip a strict superset. That would be a large finding and would be reported as one. |

## 3. Gates — binding

- **`G-BOUND`, `G-SAMPLE`, `G-RES` inherited UNCHANGED**, threshold included. `G-RES` stays at R0's floor
  **0.3762**: a gate that moves between rungs of one ladder is gate-shopping. Verdict: `GATE REACHED` iff
  clips == 0 **and** max `initRes` < 0.3762; `GATE FAIL` if clips == 0 and `initRes` ≥ 0.3762;
  **`NOT A RESULT` if clips > 0**, whatever the residual did.
- **`G-MATCH` — THE JUDGING RULE, REGISTERED BECAUSE IT DECIDED THE LAST RUNG.** Arms are compared on
  **`first_clip_iteration` and clip rate at MATCHED iterations t1 / t10 / t50 / t100**, and **NEVER on a
  total, and NEVER on how long an arm survived.** MAAOAF's N1 had the **lowest** total of four (8) and was
  the **worst** arm: its count fell to zero at t10 because the field had gone non-finite. **A FALLING CLIP
  COUNT IS NOT HEALTH.** Survival length is not a measurement at all — cfd's CRM ladder saw two identical
  configurations die at iterations 20 and 324 under MPI reduction-order non-determinism. **A
  `first_clip_iteration` field is registered for every arm** and the grader prints it unconditionally; a log
  ending short of 500 is stamped `TRUNCATED` and its total declared non-comparable.
- **Promotion gate** (full success; 4000-iteration trim on a `GATE REACHED` arm only) inherited unchanged:
  trimmed **and** zero `Bounding` on p/U/rho/e **and** `primalMaxRes ≤ 1.0e-6`, the floor being the product
  read from **this case's own log** — `primalMinResTol 1e-08` × `primalMinResTolDiff 100` — never carried.
  CL band `|CL − 0.5| ≤ 1.0e-4`.
- **`L7` ESCALATION CONDITION, REGISTERED NUMERICALLY AND IN ADVANCE.** If **no** arm M1–M4 satisfies all
  three of (a) `first_clip_iteration` > 1, (b) `first_clip_iteration` **≥ 250** (1.5 × N2's 167), and
  (c) last-block max `initRes` **< 0.6170** (N2's measured), then this item **declares the problem a
  FORMULATION question (L7), not a solver-settings question**, says so in its own `RESULTS.md`, and
  **does NOT propose a fifth settings rung.**

## 4. Planted-zero control — direction-aware, field-aware, and **ALREADY EXECUTED**

`maaoaf2_grade.py` runs **both** directions on **every** log. `plant_fail()` injects one `Bounding p<500000`
into the first `Time` block — verdict must become `NOT A RESULT` **and `first_clip_iteration` must read that
iteration**; `plant_pass()` strips the p/U/rho/e clips and rewrites the last block's `initRes` to `1e-9` —
verdict must become `GATE REACHED` **and `first_clip_iteration` must read `None`**. A reader that graded
correctly but reported the new field blind would make the whole judging rule a planted zero, so the field is
controlled too. Either direction failing to flip ⇒ **exit 2, no verdict**.
**Executed by this lane, before any arm exists, against all four real MAAOAF logs** (`R0`, `N1`, `N2`, `N3`):
all four graded `NOT A RESULT`, **both directions flipped on all four**, and the grader **reproduced the
frozen MAAOAF numbers exactly** — R0 3748 `{p 928, U 1184, rho 689, e 947}` first clip 1; N2 1021
`{p 411, U 150, rho 118, e 342}` **first clip 167**, matched census `{1:0, 10:0, 50:0, 100:0}`; N3 3466 first
clip 1; N1 8, first clip 1, **stamped `TRUNCATED` at last `Time = 8`**. New figures not in MAAOAF's record:
**R0's last-block max `initRes` is 0.7286090** and N3's **0.6178434**, so **N2's 0.6170459 is the lowest of
the three arms that reached 500** — the baseline claim is now quantified, not just asserted.

## 5. Cost — `cost_basis`: core-minutes measured from MAAOAF's own ledger; **dollars DERIVED, never measured**

Measured anchor, `…/MAAOAF-ma288-init/ledger.txt`, np = 1: R0 597 s = **9.950**, N2 546 s = **9.100**
(**`potentialFoam` included**), N3 487 s = **8.117**, N1 67 s = 1.117 (died). The baseline here is N2's
**9.100**, so the initialiser is *inside* the anchor, not added to it.

| arm | predicted core-min | basis | cap |
|---|---|---|---|
| M1 | 9.100 | same work per iteration, same 500 | 14.0 |
| M2 | 18.200 | pressure equation solved **3×** per outer iteration; ×2.0 whole-arm allowance | **26.0** |
| M3 | 10.010 | +1 gradient-limiter pass, +10 % | 14.0 |
| M4 | 9.100 | bounds only, no extra work (likely less — may exit early) | 14.0 |
| **total** | **46.410** | | **68.0** |

**ITEM CAP = 68.0 core-min**, and the per-arm caps sum to it **exactly** (26.0 + 3 × 14.0). Headroom
68.0 / 46.410 = **1.465**. 68.0 core-min = 1.13333 core-h × $0.0513/core-h = **$0.0581 DERIVED**
(owner-stated rate; the box cannot read its own billing). Wall caps at np = 1: M2 1560 s (`TMO` 2400 s),
others 840 s (`TMO` 1800 s); `LAUNCH_BUDGET_S` 600 s is a strict minority of both, asserted in the runner.
**An overrun stops that arm; it does not get a new budget** (rule 12). Estimate-vs-actual lands in
`docs/COST_CALIBRATION.md` at completion.

## 6. Unknown at draft time — stated, not smoothed

- Whether DAFoam applies `primalVarBounds` **before or after** the thermo model's own `T0` check. If after,
  M4's tight `e` bounds cannot prevent N1's `thermoI.H:57` abort, only relabel it. **A `FOAM FATAL ERROR`
  with a negative `T0` on M4 is M4's RESULT** (the arm found the physics exit), not `BLOCKED`.
- Whether `cellLimited Gauss linear 1` is accepted by this OpenFOAM v1812 build with `wallDist meshWave`.
  A dictionary-parse failure at startup is a `BLOCKED` M3, not a `GATE FAIL`, and the launch witness
  (`^ExecutionTime = `) will not fire — code 88 with `solver_call_seen`, distinguishing it.
- Whether `nNonOrthogonalCorrectors 2` interacts with DAFoam's residual bookkeeping (it changes the number
  of `p` solves per printed block). **`initRes` of the FIRST `p` solve in the block is what the grader
  reads**, unchanged; this is a reporting caveat, not a gate risk.
- Whether `printInterval 1` touches any solver state beyond printing. Assumed not; **unverified**, inherited.

## 7. Freeze values — handed to the supervisor, who freezes and launches; this lane did neither

| slot | value | how I know |
|---|---|---|
| run root | `/home/ubuntu/certonomous-runs/MAAOAF2-ma288-init` — **CONFIRMED ABSENT** | my own `ls`, at drafting |
| image | `dafoam-idwarp-rot:v1` — the PATCHED build the sweep and MAAOAF ran | inherited + confirmed below |
| image id | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **CONFIRMED, not assumed**: my own `docker inspect --format '{{.Id}}'` on this box, byte-equal to MAAOAF's |
| staged instrument | `../fixed_lift_mach_sweep/maaoa_runScript_comp.py`, md5 **`bd22df020be42fbd2eef14cbc25182f7`** | my own `md5sum`; unchanged from MAAOAF's freeze |
| grader md5 | **`f8ce662eeebbe90a11c8d48a2dd83790`** (`maaoaf2_grade.py`) | my own `md5sum` |
| runner md5 | **`29b8d2b57b390d0b3022c576a6310482`** (`maaoaf2_run_arm.sh`, **as drafted, WITH the 8 placeholders**) — the md5 **changes on substitution**; the supervisor records the post-substitution hash and verifies it against the committed blob. A file cannot hash itself. | my own `md5sum` |
| cpuset map | `M1→8 M2→9 M3→10 M4→11` — **all four confirmed free**: no containers running on this box at drafting | my own `docker ps` |
| per-arm | np 1, mem 3g, `endTime`/`writeInterval` 500, `printInterval` 1; `TMO` 1800 s (M2 2400 s); `CAP_COREMIN` 14.0 (M2 26.0) | — |

**Runner:** `maaoaf2_run_arm.sh`, derived from MAAOAF's **repaired** launcher (`266f34bfc`) and carrying its
discipline: `^ExecutionTime = ` witness with `^Time = ` the named decoy, codes 88/89/90, `docker kill` read
back, **no `2>/dev/null` on any docker reader**, disk-written pre-launch mtime capture compared by **strict
increase with no slack term**, suffixed-token `G-FREEZE.0` whose slot names are **described, never written**,
`mpirun --allow-run-as-root`, and `daOptions` patches appended **after** the md5-hashed physics block.
**`potentialFoam` is now BASELINE on every arm**, so three MAAOAF hazards become baseline asserts: the
initialiser's output is redirected on every arm and `LA.0c` asserts it on every arm; the age datum is **`0/T`,
not `0/U`** (`potentialFoam` rewrites `0/U`); and "no `0/Phi` at staging" is a baseline `G-DEADLEVER`.
**`LA.0c` carries the REPAIRED test** — a `potentialFoam` line with **no redirect operator anywhere**, not
"the line does not end in `>`", which matched a correctly redirected command and refused N2.
`G-ROOT.2` adds `MAAOAF-ma288-init` to the forbidden roots: this item reads the graded ladder and must never
write into it. New guard `G-COUNT` asserts, **before** any edit, the measured multiplicity of both `sed`
targets (`nNonOrthogonalCorrectors` ×2, `default Gauss linear;` ×1) — a `sed` that matches the *wrong* line
is invisible to a read-back of the *intended* line. M1's relaxation keys contain `|`, a `sed` metacharacter,
so M1 is applied by a **fixed-string** Python rewrite that asserts each key occurs exactly once.

**Exercised before freeze, on real bytes, by this lane:** `G-FREEZE.0` **refuses this draft** (8 placeholders,
exit 3) and **passes** a fully-substituted copy (0 matches), both `bash -n` clean — the A5P2 trap, tested in
both directions. M1's Python rewrite, M2's `sed` and M3's `sed` were dry-run against the **real** staged
`fvSolution`/`fvSchemes`: M1 → one `0.15`, one `0.35`, zero survivors of `0.30`/`0.70`; M2 → `SIMPLE` reads 2
with `potentialFlow` still 20; M3 → `gradSchemes` reads `cellLimited Gauss linear 1` with
`laplacianSchemes … Gauss linear corrected` and the `dev2` term untouched. Every `G-DEADLEVER` read-back for
those three passes. **M4's `daOptions` append is NOT dry-run against a live instrument** and is the one
staging path the supervisor should watch on first launch.

## FREEZE STAMP — 2026-09-11, dafoam-supervisor

**FROZEN.** Runner md5 `749f529430394a94faf96533584072a5` (post-substitution, `bash -n` clean, 0 slots); grader md5 `f8ce662eeebbe90a11c8d48a2dd83790`; image `dafoam-idwarp-rot:v1` @ `sha256:2927768a…`; staged `runScript.py` md5 `bd22df020be42fbd2eef14cbc25182f7`; run root **CONFIRMED ABSENT** by my own `ls`; cpusets M1→8 M2→9 M3→10 M4→11.

**§3 CHECK-1 BY EXECUTION.** I ran `maaoaf2_grade.py` against **all four real MAAOAF logs**: it reproduces the frozen numbers exactly — `first_clip_iteration` **1 / 1 / 167 / 1** for R0 / N1 / N2 / N3 — and **both planted-control directions passed on every one of the four**. `G-FREEZE.0` refuses the draft (my own run, exit 3) and passes a substituted copy.

**TWO MEASUREMENTS I RE-DERIVED MYSELF BECAUSE THEY CHANGED THE LADDER.**
**(i) MA288's max non-orthogonality is 31.503°** (average 1.710), , beside maxAR 212103.67 and max skew 1.3968. ⚠ **AND THE TRAP IS REAL:  reads 22.749° — but that file describes a 4,032-CELL GENERATION-STAGE MESH, not the 130,304-cell run mesh.** Two non-orthogonality numbers for "MA288" sit on disk and **only one is the case**. The run mesh's own  is printed inside . **So A5's lesson transfers *a fortiori*: A5P2 broke a fixed point with two correctors at 3.512°, and MA288 is 8.97× LESS orthogonal.** The aspect ratio of 212,103 is explicitly **not** the argument.
**(ii) M3 AS I BRIEFED IT WAS A NO-OP ON BOTH LIMBS, and the lane was right to refuse it.** Verified by me: every  except  is **already** , and ** does not exist — 0 occurrences** — because  carries density as , not a transport equation.  was already MAAOAF's N3. **A lane that registers the arm its supervisor asked for, when that arm cannot do anything, wastes a rung.** M3 is redirected to the one unbounded discrete operator left,  → .

**THE L7 CONDITION IS REGISTERED NUMERICALLY, IN ADVANCE:** unless some arm achieves onset **> 1** *and* **≥ 250** *and* a last-block max  **< 0.6170**, this item declares the problem a **FORMULATION question** and proposes **no fifth settings rung**. Two new figures make that threshold meaningful and were not in MAAOAF's record: R0's last-block max  is **0.7286090** and N3's **0.6178434**, so **N2's 0.6170459 is the lowest of the three arms that reached 500** — the bar is the incumbent's own number, not a round one.
