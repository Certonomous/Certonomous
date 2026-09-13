# Wolf Dynamics DrivAer, FINE — PRE-REGISTRATION

## 🔴 STATUS: **NOT FROZEN. NO COMPUTE HAS RUN AND NONE MAY RUN.**

**This document is a DRAFT handed to cfd-supervisor.** The freeze is the **supervisor's
personal check** under `SUPERVISION_CHARTER.md` §3 and it **may not be delegated to the
drafting lane**. The lane will **not launch** until the supervisor has *committed* this
file and *said so*.

**Proof that no compute has run**, checkable at review time and the reason this line exists
before any gate below:

- The run directory **`/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/fine_R1` DOES NOT
  EXIST.** `ls` it. A gate cannot have been fitted to an answer that has not been produced.
- Nothing has been staged, copied or converted for the fine case. The only Wolf Dynamics
  directory under `certonomous-runs/` is `coarse_R1`, graded and committed at
  `verification/campaign/WOLFDYNAMICS_DRIVAER_COARSE_RESULTS.md`.

Until this document is committed, **amendments are legal** (rule 2), and each must state
the condition and how it was checked — the condition being the non-existence of the run
directory named above. **After the freeze, gates are closed and changes land only as dated
addenda that cannot alter a gate, threshold, cap or label.**

---

## 0. WHAT THIS RUN IS, IN ONE LINE

Run Wolf Dynamics' **fine** DrivAer case **verbatim** — their mesh, their dictionaries,
their scripts, their rank count — in the **same Foundation OpenFOAM 9 container** that ran
the coarse rung, and compare against **their own shipped fine artifacts**.

---

## 1. THE CASE, ITS SOURCE, AND ITS HASHES

- Archive root: `/home/ubuntu/upstream/published-openfoam-setups/wolfdynamics-drivaer/drivaer_fine/`
- Manifest: `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.wolfdynamics-drivaer.txt`
- In-repo pointer: `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md`, committed at `799c88e78`
- **Manifest verified against disk at drafting time: `sha256sum -c` returned `101 OK`,
  0 failures**, over the whole archive (coarse and fine).
- Validation document: `docs/papers/benchmark_test_cases/guerrero_2022_drivaer_validation_wolfdynamics.pdf`,
  sha256 `510569660b16416423300d85e8fd173879731863ee71de88a91a8a744bcbc734`, title-page
  verified per rule 15 in the coarse registration and not re-litigated here.

### 1.1 The fine case's own files, hashed at drafting time

| file | sha256 |
|---|---|
| `system/controlDict` | `b10999239e202385e652a6cf1eec0a667f94a688d0ed6dd098612653bb8f90bd` |
| `system/fvSchemes` | `a7be7c65deccb38426e24ff9fa046ba2ed0efa1dba83dbc20e63bb02b2491e17` |
| `system/fvSolution` | `10d8b6fa1dc07d9a0892759743940cca7c7b96db647bd648369ed60ab61a7178` |
| **`system/decomposeParDict`** | **`46f7b439c2a5c0d1c744769c236070365aafa2a2529a2703c40967d827d8eb7c`** |
| `system/fvConstraints` | `96cce6dc5a83ecb95a77f11b3ad7705c081683794b718e6f4fe74725c6006b38` |
| `system/meshQualityDict` | `31fa72f113518a7105965ef578a452b57be240461f87b311a7eed19163a14e7e` |
| `system/blockMeshDict` | `2b3471e81c19ac8270eb69e8f79d6ff49ff98cd3b975bf332eb248e5b315754b` |
| `system/snappyHexMeshDict` | `bd3794109d26306e9e11f0595b53240668d4390f95b6ddc6fd73ebc80407abd0` |
| `system/surfaceFeaturesDict` | `9bc79fdb386616b5609d2d678a81f80e1cba68b322e7ccb52efaadf55678f515` |
| `constant/transportProperties` | `917ba87a40e207c785ab06471c59d51060533d472208799d5e61d92bb352c86a` |
| `constant/turbulenceProperties` | `716ca7e0533b61dcc9df1b274a46e0ffdf923951ff4030091c8cd40bfcd379a7` |
| `0_org/U` | `040e4ee42ee3807ad64ef77c2af21fa8004aae317b14777f653c2f76917f1cc4` |
| `0_org/p` | `d43c0b0f061dfe680fa3d516a80e6d674b45ab098072d4495d85c0e65148a06b` |
| `0_org/k` | `7912c5e28fcc9c706c39e56e9dc089367a7b73779e98ca635c84911a724bd4b4` |
| `0_org/omega` | `20f32d1ad7617a17f426dd938efa24024419535336406a9557848cf90c20c273` |
| `0_org/nut` | `85dd3aec372f67340c6b5421755c4f08f97646ebe6a91754a302de09cb200c46` |
| **`mesh/mesh_fine.msh`** | **`372b8ae2581b8ed2e50e757ea028e6d81d001fd2ec223bbd57bd8f024455f830`** (820,744,718 B) |
| `run_all_fluent.sh` | `a2d1e6a9667be6f0969ff83704a45faf7ebaf142da9257207dd9a757540164a4` |
| `run_mesh_fluent.sh` | `072fdad5e24cf8b26e253015ee10e7336e724d9684b8c49007143f92f1b4bacd` |
| `run_solver_fluent.sh` | `d3ff0f6a3b39ed52e88a80eff84a8b64e531f4ed6fa0e8391203afe9b95f7328` |
| their shipped `sol_logs/fine/postProcessing/all/0/forceCoeffs.dat` | `17b702a26443c10d22d436377727c4dd2247b771e3fbbe2b16e8905e13bdfab6` (1,190,523 B) |
| their shipped `sol_logs/fine/log.solver` | `d2762fc2e75ef1fa4e319b9e697f8340c615182c897eeea0ba48434ee1e9d916` |

### 1.2 FINE VERSUS COARSE — MEASURED BY HASH, SO THE DELTA IS A FACT

Every file above was hashed against its coarse counterpart:

**IDENTICAL between coarse and fine** — `fvSchemes`, `fvSolution`, **`decomposeParDict`**,
`fvConstraints`, `transportProperties`, `turbulenceProperties`, **all five `0_org` initial
fields**, `run_all_fluent.sh`, `run_solver_fluent.sh`.

**DIFFERENT** — `controlDict`, `blockMeshDict`, `snappyHexMeshDict`, `surfaceFeaturesDict`,
`meshQualityDict`, `run_mesh_fluent.sh`.

And the differences are exactly two things, read from the diffs rather than assumed:

1. **`controlDict`: `endTime 1000` → `endTime 10000`.** That is the only substantive
   change; the rest of the diff is whitespace and one missing space in
   `patches ( ruotapost);`.
2. **`run_mesh_fluent.sh`: `mesh_coarse.msh` → `mesh_fine.msh`.**

`blockMeshDict`, `snappyHexMeshDict`, `surfaceFeaturesDict` and `meshQualityDict` differ but
are **NEVER EXECUTED**: the mesh ships as a Fluent `.msh` and is converted by
`fluent3DMeshToFoam`; `run_mesh_fluent.sh` has its `checkMesh` line commented out and calls
no mesher. **The physics setup of the fine case is byte-identical to the coarse one. The
only physics difference between the two rungs is the mesh and the iteration count.**

---

## 2. 🔴 THE FINDING THAT CHANGES WHAT THIS RUN CAN CLAIM — READ THIS BEFORE THE GATES

**THEIR SHIPPED FINE SOLUTION WAS NOT PRODUCED AT THE RANK COUNT THEIR OWN CASE FILES
SPECIFY.**

| source | ranks |
|---|---|
| `drivaer_fine/system/decomposeParDict` | **`numberOfSubdomains 4`** |
| `drivaer_fine/run_solver_fluent.sh` | **`procs=4`** |
| **`drivaer_fine/sol_logs/fine/log.solver:52`** | **`nProcs : 40`** |

For the **coarse** rung the three agreed — `decomposeParDict 4`, `procs=4`, and the shipped
`log.solver:26` reads `nProcs : 4` — which is **why** the coarse rung came out
byte-identical and why that byte-identity was expected in advance. **For the fine rung they
do not agree.** Their shipped fine result was computed with a **40-way scotch
decomposition** on a machine whose case header reads `Case : /home/joegi/tmp/drivaer`.

**THREE CONSEQUENCES, REGISTERED BEFORE THE RUN:**

1. **Running at 4 is still the correct verbatim choice and this registration does not
   change it.** Verbatim means *their shipped case files, unmodified*, and their shipped
   case files say 4. Taking 40 would mean **editing `decomposeParDict`** to chase a number
   that appears only in a log — that is a modification, and it is the thing this whole
   exercise refuses to do. The instruction also stands independently: **4 ranks, their
   number, not what is free.** The DrivAer lane holds 20 reserved ranks; 4 of them is
   correct and **the remaining 16 stay idle by Sanaa's explicit order — nobody borrows
   them.**
2. **BIT-IDENTITY WITH THEIR SHIPPED FINE OUTPUT MUST NOT BE EXPECTED, AND A GATE THAT
   ASSUMED IT WOULD BE WRONG.** A 4-way scotch partition is not a 40-way one; it changes
   the summation order of every global reduction and it changes the GAMG agglomeration
   hierarchy built on the partition. The gates in §5 are therefore set on **physical
   agreement**, not on reproduction-to-the-bit, and the band rationale in §5.1 is written
   from that mechanism rather than fitted to an outcome.
3. **AND THIS MAKES THE FINE RUNG A STRONGER RESULT THAN THE COARSE ONE, WHICH IS SAID HERE
   IN ADVANCE SO IT CANNOT LOOK LIKE A CONSOLATION LATER.** The coarse rung's §1.1
   disclosure is that bit-identity proves verbatim execution and **cannot corroborate their
   number**. The fine rung does not have that problem in the same form: if a **4-rank**
   solve lands on a **40-rank** published result, the decompositions genuinely differ and
   the agreement is **partial independent corroboration** — partial, because the mesh,
   the code and the discretisation are still theirs.

---

## 3. ROUTE, CONTAINER AND THE DEVIATION TABLE

**Route A, identical to the coarse rung.** Their case is OpenFOAM **9 Foundation**; this
box's native install is **v2606 ESI**, a different fork. The case runs **unmodified inside
the Foundation OpenFOAM 9 container** — `openfoam/openfoam9-paraview56`, image
`eb76be2b2088`, entered as `--entrypoint /bin/bash -u 1000:1000`, sourcing
`/opt/openfoam9/etc/bashrc`. **The translation table is empty: zero keywords translated.**

Route B (translating to v2606) was measured and rejected for the coarse rung and the same
finding binds here: **`fvConstraints` is read NOWHERE in the v2606 source** —
`simpleFoam.C` includes only `fvOptions.H` — so their velocity limiter would be **silently
ignored, not refused**, and their own page 15 calls that limiter load-bearing against
divergence. `system/fvConstraints` is byte-identical between the coarse and fine cases
(`96cce6dc…`), so the trap is identical too.

**EVERY DEVIATION FROM THEIR RUN IS EITHER ZERO OR NAMED. THERE IS NO THIRD CATEGORY.**

| deviation | status |
|---|---|
| all 16 dictionaries and initial fields | **ZERO** — proven by sha256, §1.1 |
| their three run scripts | **ZERO** — run unmodified, `sh run_all_fluent.sh` |
| the mesh | **ZERO** — their shipped `mesh_fine.msh`, converted by their own script |
| rank count vs their **case files** | **ZERO** — 4, as `decomposeParDict` and `procs=4` say |
| **rank count vs their shipped fine LOG** | 🔴 **NAMED: 4 here against `nProcs : 40` there.** §2 |
| **OpenFOAM build string** | 🔴 **NAMED: `9-b456138dc4bc` here against `9-6adb71a2e61d` in both their shipped logs** |
| host CPU | **NAMED** — c7a.4xlarge (Zen 4, 2026) against their 2022 machine |

---

## 4. THE COMPARANDS — MEASURED FROM THEIR SHIPPED FINE ARTIFACTS BY THIS LANE

Read from `drivaer_fine/sol_logs/fine/postProcessing/all/0/forceCoeffs.dat`
(sha256 `17b702a2…`), **column resolved by NAME from the header**
`# Time Cm Cd Cl Cl(f) Cl(r)` → `Cd` is header index 2 = **column 3**. No column index is
assumed anywhere in the grading script.

| quantity | their shipped fine value | basis |
|---|---|---|
| rows | **10,001** (t = 0 … 10,000, `deltaT 1`) | the file |
| **Cd at iteration 10,000** | **0.257031412829** | the file's last row |
| **mean Cd over their own window, 200 → 10,000** | **0.256411937582** (**9,801 rows**) | their `fieldAverage timeStart 200`, no `timeEnd`, to `endTime 10000` |
| iterations completed | 10,000, terminating at `End` | `sol_logs/fine/log.solver` |
| their `ExecutionTime` | **24,153.39 s** (`ClockTime = 24,187 s`) | same log, last line |
| their ranks | **40** — §2 | same log, `:52` |
| **cells** | **4,048,483** | §4.1 |

The 0.256412 figure independently re-measured here matches the value the **coarse**
registration recorded at §6b before that rung ran, which is a small cross-check that the
same file is being read the same way by two different readings.

**Their averaging window is registered as THEIRS and used unchanged.** It is a fixed
window, not a detection rule. **This lab's stationarity gate is NOT substituted into their
case**; if it is reported at all it is reported beside their number and never in place of it.

### 4.1 Cell count — RE-DERIVED, NOT RELAYED

Counted from the Fluent `.msh` header itself: the cells section reads
`(12 (0 1 3dc663 0 ...))`, i.e. cells `0x1` … `0x3dc663`, giving
**0x3dc663 − 0x1 + 1 = 4,048,483 cells**. Their document says *"approximately 4048000"*.
The same method gave the coarse mesh 669,416 against *"approximately 660000"*, and
`checkMesh` then measured exactly 669,416 — so **the method has already been shown right
once on this case family.**

### 4.2 🔴 THEIR FINE RUN DID NOT MEET ITS OWN CONVERGENCE CRITERION EITHER

`system/fvSolution` carries `residualControl { p 1.0e-3; U 1.0e-3; k 1.0e-3; omega 1.0e-3; }`
— byte-identical to the coarse case's. **`SIMPLE solution converged` appears ZERO times in
their shipped fine `log.solver`** across all 10,000 iterations. Their fine run stopped at
`endTime`, not at convergence.

**This is disclosed BEFORE the run because it shapes the gates**: the **endpoint** of a
non-stationary iterate is the fragile comparand and the **9,801-row window mean** is the
robust one. §5 weights them accordingly, in advance.

---

## 5. THE GATES

Frozen at the supervisor's commit of this file. `Cd_ours` is from our run's
`postProcessing/all/0/forceCoeffs.dat`, produced by their unmodified `all` `forceCoeffs`
function object, column resolved **by name**.

- **F1 — WINDOW-MEAN AGREEMENT (the primary gate).**
  `|mean(Cd_ours, 200→10000) − 0.256412| / 0.256412 ≤ **1.0 %**` → **`PASS`**, else
  **`GATE FAIL`**.
- **F2 — ENDPOINT AGREEMENT (secondary, deliberately wider).**
  `|Cd_ours(10000) − 0.257031| / 0.257031 ≤ **2.0 %**` → **`PASS`**, else **`GATE FAIL`**.
- **F3 — MESH IDENTITY.** `fluent3DMeshToFoam` + `checkMesh` report **4,048,483 cells** →
  **`PASS`**, else **`GATE FAIL`** (their mesh is not the mesh we ran).
- **F4 — COMPLETION.** `rc = 0`; an `End` line; last time == `endTime` = **10000**; the
  full field set present at 10000; the `ExecutionTime` print count == `round(10000/1)` =
  10000; and every field at 10000 **newer** than the case's launch stamp (age guard). Any
  clause failing → **`NOT A RESULT`**, whatever the Cd says.
- **F5 — RANK DISCLOSURE.** Our `log.solver` must print **`nProcs : 4`**. If it prints
  anything else the run was not the registered run → **`NOT A RESULT`**. And the grading
  record **must state, in its verdict section, that their shipped fine log prints
  `nProcs : 40`** — §2's finding travels with the verdict or the verdict is incomplete.

### 5.1 BAND RATIONALE, STATED BEFORE THE ANSWER IS KNOWN

The bands are **wider than the coarse rung's** and the reason is mechanical, not
discretionary. The coarse rung's 2.0 % was set to absorb a build-string difference and
CPU-dependent summation order, and it came in at 0.00012 % because the decomposition
matched and the arithmetic was bit-reproducible. **Here the decomposition does not match**
(§2), so global-reduction order genuinely differs, **and their reference iterate is not
converged** (§4.2), so it carries iterate noise of its own.

- **F1 at 1.0 %** because averaging 9,801 iterations suppresses both effects: a
  decomposition-induced perturbation that does not change the physics should wash out of a
  9,801-sample mean well inside 1 %.
- **F2 at 2.0 %** because a single snapshot of a drifting iterate does not have that
  protection. **F2 is the weaker gate and this document says so in advance**; a `GATE FAIL`
  on F2 with a `PASS` on F1 would be read as iterate noise, not as a physics disagreement,
  **and that reading is registered here so it cannot be invented afterwards.**
- **Neither band gets widened after the fact, and neither gets narrowed either.**
- **A result inside 0.5 % on F1 will be reported as such.**

### 5.2 MANDATORY DISAVOWALS, BINDING ON ANY PASS

1. **This is a REPRODUCTION exercise, and against the wind tunnel the fine rung is a
   different claim from the coarse one — but it is still not this lab's validation.** Their
   published reference data (p.19) gives **EXP TUM ASME 0.247** and **EXP TUM SA 0.243**,
   and their shipped fine window mean of 0.256412 is **+3.81 %** and **+5.52 %** against
   those. If our run lands near theirs it lands near those too. **The lab claims a
   reproduction of their computation; it does not thereby claim a validated DrivAer.**
2. **The §6b discrepancy in their published material is carried forward UNRESOLVED.** The
   shipped case has **Setup 2** boundary conditions (rotating wheels + moving ground,
   published Cd 0.2426) while the shipped fine solution averages **0.256412**, which is
   **0.19 % from Setup 3 (0.2569)** and **5.7 % from Setup 2**. **A reproduction that lands
   near 0.2569 must NOT be written up as reproducing 0.2426.** We do not know which of
   their rows the shipped solution corresponds to, we changed nothing to make it agree, and
   this rung does not resolve it.
3. **THE §5 CONDITION OF THE COARSE REGISTRATION BINDS EVERY Cd FROM THIS RUN TOO.** This
   is the original TUM DrivAer: a **half model**, 30 m/s, nu = 1.5881327800829875e-05,
   reference area 1.073476 m², `ffminy type symmetry`. **It is a DIFFERENT experiment from
   the full-scale 38.889 m/s configuration this lab's other DrivAer gates are anchored on,
   and no Cd from this run may be compared against this lab's other DrivAer band.**

---

## 6. FALSIFIABLE PREDICTIONS, WITH NUMBERS, BEFORE THE RUN

- **P1 — the force file will NOT be byte-identical to theirs.** The coarse one was, to the
  byte; this one will not be, because the decomposition differs (§2). **If it IS
  byte-identical, this lane's reading of `nProcs : 40` is wrong and the whole of §2 must be
  retracted** — that is the test, and it is registered as one.
- **P2 — F1 will PASS, and by more than a factor of 5** (i.e. inside 0.2 %). Decomposition
  changes summation order, not physics, and a 9,801-sample mean is insensitive to it.
- **P3 — F2 will PASS but by a smaller margin than F1**, because their endpoint is a
  snapshot of a non-converged iterate.
- **P4 — F3 will PASS exactly at 4,048,483**, as the same derivation did on the coarse mesh.
- **P5 — `SIMPLE solution converged` will appear ZERO times in our log**, as it does in
  theirs and as it did in our coarse run. The run will stop at `endTime`.
- **P6 — the run will take 34–40 h of wall clock** at 4 ranks (§7).

---

## 7. RANKS, COST AND CAP — RULE 12

**Ranks: 4.** Their `decomposeParDict numberOfSubdomains 4` and their
`run_solver_fluent.sh procs=4`, both unmodified. §2 explains at length why the 40 in their
log does **not** move this number. **Taking more would change the scotch partition and the
GAMG agglomeration built on it — a numerical deviation that would destroy the verbatim
claim.** The DrivAer lane's other 16 reserved ranks **stay idle by Sanaa's explicit order.**

**COST, PRE-REGISTERED. Two independent routes, and the prediction is set against the
larger.**

| route | basis | wall | core-minutes |
|---|---|---|---|
| **1 — our own measured coarse, scaled** | our coarse `simpleFoam` `ExecutionTime = 2167.01 s` for 669,416 cells × 1,000 iterations at 4 ranks = **3.2372 × 10⁻⁶ s per cell-iteration**; × 4,048,483 × 10,000 | 131,056 s = **36.4 h** | **8,737** |
| **2 — their fine, scaled to 4 ranks and to this box** | their `ExecutionTime = 24,153.39 s` at 40 ranks, × 10 for ideal strong scaling to 4, ÷ **1.802** — the **measured** this-box-over-their-box speedup from the coarse rung | 134,037 s = **37.2 h** | **8,936** |
| pipeline (`fluent3DMeshToFoam` + `decomposePar` + `checkMesh` + `renumberMesh` + `potentialFoam`) | coarse pipeline scaled by `.msh` bytes and by cells | ~164 s | ~11 |

**The two routes agree to 2.3 %**, which is the best corroboration available without running
it. Route 2's ideal-scaling assumption is optimistic and is named as such.

- **PREDICTED: 9,100 core-minutes.**
- **Upper bound registered: 12,000 core-minutes** — 32 % of headroom over the larger route,
  for contention and for the strong-scaling assumption.
- **Dollars: 9,100 / 60 × $0.0513 = $7.78 — DERIVED, NOT MEASURED** (upper bound $10.26,
  also derived). Rate owner-stated for c7a.4xlarge; the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **For the record, their own fine run cost 16,102.3 core-minutes** (24,153.39 s × 40 / 60)
  — 1.77× ours, because 40 ranks at ~2× lower per-core throughput is less efficient than 4
  ranks at higher throughput. That comparison is **derived from two logs**, not measured
  head-to-head.
- **Actual will be compared against the 9,100 at completion** in `docs/COST_CALIBRATION.md`
  with the ratio and the gap attributed, contention named separately from misprediction and
  waste named separately from both — rule 12's calibration clause.

**CAP: none.** Sanaa's ruling of 2026-09-12, directive #17: no run is stopped by a time or
budget cap. **The cost is stated because rule 12 requires every run to be costed. It is not
a stop condition.** The run is also inside the $25 pre-authorisation by a factor of three.

**RESOURCES — checked at drafting, not assumed:** 239 GB free on `/`. The coarse staged
case occupies 1.1 GB from a 128 MB `.msh`; the fine `.msh` is 6.41× larger, so the staged
fine case is expected at **7–9 GB**, with `purgeWrite 2` capping retained time directories
at two. **Headroom is ample and this was measured with `df`, not assumed.**

---

## 8. EXECUTION PLAN, FROZEN

1. Stage `drivaer_fine` to `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/fine_R1`
   **by copy**, then **re-verify the staged copy against the published manifest with paths
   rebased** — the same two-proof procedure the coarse rung used. A staged file whose hash
   differs from the source **stops the run**.
2. Write `LAUNCH_STAMP.txt` (UTC) and `CONTAINER_ID.txt` before the container starts, so
   the age guard of F4 has a reference older than every field it will check.
3. Run **`sh run_all_fluent.sh`, unmodified**, inside the container as
   `--entrypoint /bin/bash -u 1000:1000`, `source /opt/openfoam9/etc/bashrc`, capturing
   `rc` **inside** the detached wrapper and writing `RUN_RC.txt`.
4. On completion, grade F1–F5 with a script that resolves `Cd` **by header name**, and that
   is given a **planted control** before any zero or any "no difference" is believed: a
   perturbed copy must make the comparison instrument report a difference, and a +1.0 on
   one row must move the window mean by exactly 1/9801.
5. **Render on completion** per Sanaa's standing ParaView rule — mesh surface, surface `p`,
   surface `yPlus` — with the face-count guard, the planted colour control and the
   graded-tree census, filed under `RENDERS/` beside the run.
6. **Append the calibration row** to `docs/COST_CALIBRATION.md`.

---

## 9. WHAT THIS LANE COULD NOT VERIFY AT DRAFTING TIME

- **Why their fine log says 40 when their case files say 4.** The finding is a fact read off
  `sol_logs/fine/log.solver:52`; the explanation is not available on this box and **is not
  guessed at here.**
- **Whether their 40-rank result is itself decomposition-converged.** Nothing shipped lets
  us check it. If our 4-rank run disagrees with theirs beyond the F1 band, **that is a
  finding about decomposition sensitivity in an unconverged steady RANS solve, not
  automatically an error on either side**, and the grading record must say so rather than
  assign blame.
- **The strong-scaling assumption in cost Route 2** (40 → 4 ranks taken as ideal) is
  unverified and optimistic; Route 1, measured on this box, is the better anchor and the
  registered figure is set against the larger of the two anyway.
- **Whether 36–40 h of wall clock on 4 held ranks is an acceptable occupancy** is the
  supervisor's call, not this lane's. It is raised here explicitly so the freeze is taken
  with that number in view.

---

## 10. SIGN-OFF

**Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN. NO COMPUTE HAS RUN.**

**The freeze is cfd-supervisor's personal check and may not be delegated** — it is check 4
of `SUPERVISION_CHARTER.md` §3, and the supervisor is expected to read this file in full,
including §2, before committing it. **The lane will not launch until the supervisor has
committed this document and said so.** The commit that lands this file **is** the freeze,
and the grading path is fixed at that commit; the frozen file will be verified by
`git hash-object` against the committed blob before the verdict is written, as it was for
the coarse rung.

**Contains no submission and no external communication. Nothing leaves the box.**
