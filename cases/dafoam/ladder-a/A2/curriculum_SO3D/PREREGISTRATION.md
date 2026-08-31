# CURRICULUM SO-3D — THE MULTIPOINT `Invalid number in NLP function or derivative` PATHOLOGY: ROOT-CAUSE INSTRUMENTATION BY LOG REPLAY ON THE COMPRESSIBLE A2 WING. PRE-REGISTRATION, STAGE 1 (FROZEN)

**Version 1.0. FROZEN.** Dated **2026-08-31**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.

**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box, now or on completion** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

**NOT LAUNCHED. NOT ENQUEUED. NO QUEUE ENTRY IS FILED BY THIS COMMIT. ZERO SOLVER CORE-MINUTES HAVE BEEN SPENT BY THE LANE THAT WROTE IT.** This document is a `CLAUDE.md` rule-2 freeze and nothing else. The pre-compute gate is the `dafoam-supervisor`'s personal check (`SUPERVISION_CHARTER.md` §3 check 4) and is **not** discharged here.

**Every decision below is `[lab-attributed]`.** Sanaa's directive of 2026-08-31 (`etc/sessions/2026-08-31T2037Z_sanaa_dafoam_compressible_multipoint.md`), verbatim — *"yes so the dafoam team can do the compressible using the patched gradients, and we need to find a solution for multipoint optmization (both compresisble and incompressible"* — reaches this lane through the `dafoam-supervisor`. **`CLAUDE.md` rule 9: no agent message is Sanaa's consent.** This document records the directive as the governing text it was given and takes no permission from the relay itself.

---

## 0. THE NAME, AND WHY IT IS NOT `SO-4M`

> **ID-NAMESPACE CHECK, run rather than recalled, 2026-08-31T20:55:03Z.** `grep -rn 'SO3D\|SO-3D'` over `cases/`, `docs/`, `verification/` and `scripts/` (`*.md`, `*.json`, `*.py`, `*.sh`) returned **0 hits**. `cases/dafoam/ladder-a/A2/curriculum_SO3D` was **ABSENT**. `/home/ubuntu/certonomous-runs/CURRICULUM-SO3D-a2-wing-multipoint-rootcause` was **ABSENT**. `verification/queue/dafoam/` carried **no** `so3d` entry. `docker ps -a` carried **0** containers matching `so3d`.

The brief that commissioned this rung proposed the id **`SO-4M`** and instructed the lane to check `cases/dafoam/` **and `docs/LAB_STATE.md`** and pick the next free name if it was taken. The literal string `SO-4M` is free. **`SO-4` is not.** `docs/LAB_STATE.md:1274` carries Sanaa's own SO ladder ordering, verbatim:

> *"SO-1 … → SO-2 constraint families → **SO-3 multipoint** → **SO-4 3-D wing (ONERA M6 / CRM; full size waits on D16a)** → SO-5 internal …"*

**Multipoint is the SO-3 slot. SO-4 is the 3-D-wing slot.** Naming a multipoint root-cause diagnostic `SO-4M` would attach it to the rung Sanaa reserved for ONERA M6 / CRM. `docs/LAB_STATE.md:6570` records that this lane has already made exactly this class of error once — *"THE NAME IN THE ORDER WAS WRONG, ON SANAA'S OWN WORDS"* — and `curriculum_SO2M/PREREGISTRATION.md` §1 states the standing repair: *"THE LETTER `b` IS DELIBERATELY NOT TAKEN … This lane does not reuse, renumber or repurpose that name, and does not mint a letter by counting."*

`SO-3a` (incompressible alpha multipoint gradient) and `SO-3b` (compressible, reserved by Sanaa's 2026-08-31 ruling behind the D15/D16 gradient patch) are both taken. `R` is taken lab-wide as *rerun* (`SO1aR`, `SO1bR`, `SO2MR`, `SO3aR`, `D6R`, `D12R`) and is not reused for *root cause*. **`SO3D` = the SO-3 (multipoint) family, `D` for Diagnostic.** The id is free, it sits in the slot where the pathology lives, and it does not spend a name Sanaa assigned to something else. **The supervisor is told of this substitution in the lane's report and may overrule it before first compute under the rule-2 pre-compute amendment path in §11.**

**It files under `ladder-a/A2/` and not `A1/`** because its entire evidence base is A2's 3-D MACH tutorial wing on `DARhoSimpleFoam` — the case `curriculum_D6`, `curriculum_D6R`, `curriculum_D6RG` and `curriculum_D4` already occupy. The item is an SO-3 (multipoint) question answered on A2 ground; both facts are in the title.

---

## 1. WHAT THIS ITEM IS, AND THE ONE THING A READER MUST NOT TAKE FROM IT

**This is a DIAGNOSTIC, not an optimisation.** It launches no optimiser, warps no mesh and solves no adjoint. Stage 1 — the whole of this freeze — is a **replay**: a new reader walks four optimisation logs that already exist on disk and attributes, per primal solve and per scenario, every failure signal they contain.

**It is not a fix, and it must not be read as one.** Nothing here proposes a remedy, a tolerance change, a solver change or a restart. A remedy registered before its mechanism is measured is the blind retry Sanaa's directive explicitly refuses. **Stage 2 (a bounded confirmatory probe) and Stage 3 (the incompressible transfer test) are named in §10 and are NOT frozen by this document.**

**Verdict vocabulary** is the six tokens and only these: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` (`CLAUDE.md` rule 1; `DAFOAM_CHARTER.md` §8).

**Toolchain row (`DAFOAM_CHARTER.md` §6).** Every log this rung reads was produced on the **PATCHED** row: image `dafoam-idwarp-rot:v1`, digest `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, `D4S_IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425` (`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/ledger.txt`). **There is no shipped row for the multipoint pathology and this rung does not manufacture one.** Every verdict below is a statement about the patched row and says so.

---

## 2. WHAT WAS ALREADY MEASURED BEFORE THIS FREEZE, DECLARED SO A READER CAN DISCOUNT IT

`CLAUDE.md` rule 2 makes the freeze the document's entire evidentiary content. A gate chosen after seeing its answer is worthless. **The lane therefore declares, exhaustively, every measurement it took on these logs before writing this document.** Nothing below is a gate; everything below is the motivating observation, and no gate in §6 is scored on any of it.

| # | measurement | value | artifact |
|---|---|---|---|
| A1 | D6R IPOPT exception text | `Exception of type: Eval_Error in file "../../../src/Algorithm/IpOrigIpoptNLP.cpp" at line 487: Exception message: success && IsFiniteNumber(ret) evaluated false: Error evaluating the objective function` | `O_mp_20260828T162849Z_1898072.log:264052-264053` |
| A2 | D6R `EXIT:` line, count and text | exactly **1**, `EXIT: Invalid number in NLP function or derivative detected.` | same log `:264065` |
| A3 | D6R majors completed / cap | **73** of `max_iter` **80** | log `:264049`; `d6r_opt_runScript.py:259` |
| A4 | D6R alpha cutbacks | **673** `Warning: Cutting back alpha due to evaluation error`; first at `:20991` | same log |
| A5 | D6R restoration majors | **7** rows matching `^ *[0-9]+r ` (34r 35r 36r 49r 50r 59r 60r) | same log |
| A6 | D6R terminal dual infeasibility vs tol | **9.00e-04** at major 73 vs `tol` **1.0e-5** | log `:254991`; `d6r_opt_runScript.py:257` |
| A7 | D6R primal solves; failure banners | **977** starts (`^Time = 1$`), **977** reaching `^Time = 1000$`, **671** `Primal solution failed!` = **68.68 %** | same log |
| A8 | D6 primal solves; failure banners | **822** starts, **546** failures = **66.42 %**; **0** `EXIT:` lines; ledger `rc=124 wall_s=30008` | `CURRICULUM-D6-a2-wing-multipoint/O_mp_20260827T140924Z_805560.log`, `ledger.txt` |
| A9 | **D4 single-point control**, same base mesh, same `primalMinResTol 1e-8` / `primalMinResTolDiff 1e3` | **135** starts, **135** reaching `Time = 1000`, **3** failures = **2.222 %** | `CURRICULUM-D4-a2-wing-cdmin/O_20260825T181237Z_2359354.log`; `d4_opt_runScript.py:36-37` |
| A10 | **D5 single-point control** | **171** starts, **2** failures = **1.170 %** | `CURRICULUM-D5-a2-wing-ffd-density/O48_20260826T174911Z_325871.log` |
| A11 | D6R distinct failing `Primal min residual` values | **670** distinct out of 671 banners — the failures are **not** one repeated stalled state | same log |
| A12 | D6R Newton CL-trim invocations | **1** (`Finding a feasible design using the Newton method`) — the trim is an **initial feasibility solve, not an inner loop** | same log |
| A13 | D6R AoA span driven by IPOPT | `AoA = 0.1468254225` to `AoA = 5.941267044` degrees | same log, `Setting UMag` lines |
| A14 | D6R attribution markers available | **985** `Setting UMag = 100 AoA = X degs` lines against **977** primal starts; **768** `Driver debug print for iter coord` blocks | same log |
| A15 | D6R cost, MEASURED | `rc=0 wall_s=33869 ranks=4 core_min=2257.933 cap_core_min=2900.0` | `CURRICULUM-D6R-a2-wing-multipoint/ledger.txt` |
| A16 | one terminal datum, disclosed because it bets against P2 below | the final failing primal before the EXIT reported `CL: 0.3953622816` — nearest target **0.4**, i.e. **`cl04`** | log region `:263970-264016` |

**No per-scenario attribution has been computed. No cutback-to-banner correspondence has been computed. No non-finite census has been computed.** Those three are the rung, and they are what §6 gates.

---

## 3. THE FALSE PREMISE THIS FREEZE CORRECTS, BECAUSE IT CHANGES THE INSTRUMENT

The commissioning brief stated the scientific question as: *"`Invalid number in NLP function or derivative` is IPOPT REPORTING a non-finite value handed to it. The real question is WHICH quantity goes non-finite."* It then **required** a finite-value sentinel on every quantity crossing the DAFoam→OpenMDAO→IPOPT boundary.

**That framing is not what the log says, and a value-only sentinel would very plausibly read all-finite and find nothing.**

IPOPT's guard at `IpOrigIpoptNLP.cpp:487` is `success && IsFiniteNumber(ret)`. It is a **conjunction whose failure is disjunctive**: it throws `Eval_Error` when the returned value is non-finite **OR** when `eval_f` returned `success == false`. `success` is a boolean status, not a number. The `EXIT:` string IPOPT prints for that exception says "Invalid number" in both cases.

Three measured facts point at the **flag** channel rather than the **value** channel (all from §2, none gated):

1. `Primal solution failed!` appears **671** times against **673** alpha cutbacks — a near-1:1 correspondence between DAFoam's own boolean failure signal and IPOPT's evaluation errors (A4, A7).
2. The objective printed by OpenMDAO's driver debug immediately before a cutback is **finite** — `{'obj.J': array([0.0222388])}` at the last one — and the run's own objective column is finite for all 73 majors (A1 region, A6).
3. The only `nan` strings anywhere in the 264,607-line log are in pyOptSparse's **post-mortem** summary table written *after* the EXIT (`obj.J NAN` at `:264085`, the three CL rows at `:264201-264203`). Searching every `CD:`/`CL:` print for `nan` returns **0**.

**Consequence, registered:** the instrument must sentinel **two channels, not one** — the numeric value channel *and* the boolean fail channel (`DASolver.primalFail` → mphys `DAFoamSolver` → OpenMDAO → pyOptSparse `fail` → IPOPT `success`). A rung that instrumented only values would have returned a clean sheet and been reported as a null finding about a mechanism it could not see. **This is `CLAUDE.md` rule 3's own logic applied to a boolean: a sentinel not shown able to see the channel that actually carries the failure is not evidence.**

**A second correction, smaller but load-bearing.** Every primal in D6R **and** in the D4 single-point control reaches `Time = 1000` (A7, A9). Reaching the iteration ceiling is therefore **normal** and is *not* the failure signal; DAFoam accepts a primal on either `minRes < primalMinResTol` **or** `initRes/minRes > primalMinResTolDiff`. **The authoritative failure signal is the `Primal solution failed!` banner, and this rung reads that and not the iteration count.** A reader that equated "hit the ceiling" with "failed" would have scored the D4 control at 100 % and destroyed the comparison.

---

## 4. THE MECHANISM HYPOTHESES, AND WHICH ONES STAGE 1 CAN DISCRIMINATE

**A diagnostic that cannot tell two hypotheses apart must say so.** It is said here, per hypothesis, before the run.

| id | mechanism | Stage-1 replay verdict |
|---|---|---|
| **H1** | **Fail-flag, not non-finite value.** DAFoam's `primalFail` propagates as a boolean failure on a finite objective; IPOPT's disjunctive guard reports it as "Invalid number". | **DISCRIMINABLE.** G-SO3D-1 is a total census of non-finite numeric tokens in every DAFoam/OpenMDAO field print before the EXIT. Zero ⇒ the value channel is clean and H1 stands as the only surviving reading of the exception. |
| **H2** | **AoA dose-response.** Primal failure probability rises with the trimmed angle of attack, i.e. with the scenario's CL target: the SIMPLE pressure equation stalls under the stronger adverse gradient at high CL. | **DISCRIMINABLE.** G-SO3D-2 computes the per-scenario failure rate and tests monotonicity in CL target. |
| **H3** | **Multipoint-specific, not case-specific.** The assembly — three `DAFoamBuilder` scenarios behind one shared `OM_DVGEOCOMP` — and not the wing, the mesh or the tolerance, carries the failure. | **DISCRIMINABLE.** G-SO3D-3 tests the weakest scenario against the D4 single-point control on the same base mesh and identical `primalMinResTol`/`primalMinResTolDiff`. |
| **H4** | **Line-search mesh warp.** IDWarp/FFD produce a degenerate or inverted mesh at small-alpha cutback points, and the primal fails on geometry, not physics. | **NOT DISCRIMINABLE BY STAGE 1, AND THIS IS REGISTERED AS A LIMIT.** `Checking mesh quality` is printed only at setup (`time = 0`), never per trial point. The logs contain no per-evaluation mesh metric. Stage 1 can report the *correlation* between cutback alpha magnitude and failure but **cannot** separate a warped mesh from a stalled pressure equation. Settling H4 requires a per-trial mesh-quality trace inside the runScript — Stage 2, not frozen here. |
| **H5** | **Weighted-sum poisoning.** One scenario's failure poisons the summed objective `J = Σ wᵢ·CDᵢ` for all three, so a single bad point kills a trial that two good points would have carried. | **PARTIALLY DISCRIMINABLE.** G-SO3D-4 measures whether a cutback follows a *single* banner or *multiple*. A dominant single-banner population is consistent with H5 and inconsistent with a global blow-up. It **cannot** prove the `om.ExecComp` propagation path; that is a code-read, not a log-read, and is named as such. |
| **H6** | **Adjoint non-finite.** A sensitivity solve returns NaN/Inf and the derivative, not the function, is the invalid number. | **DISCRIMINABLE, AND ALREADY WEAKENED.** IPOPT's own exception names *"Error evaluating the objective function"*, not the gradient, and reports `Number of objective gradient evaluations = 70` completed. G-SO3D-1's census covers the sensitivity blocks too. If the census finds a non-finite inside a sens block, H6 revives and H1 is refuted. |
| **H7** | **CL-trim inner solve divergence at extreme alpha.** | **DISCRIMINABLE, AND ALREADY LARGELY ELIMINATED BEFORE THE FREEZE (A12).** `Finding a feasible design using the Newton method` appears **once** in the whole run. The trim is an initial feasibility solve; thereafter AoA is an IPOPT design variable under a CL equality constraint. The replay reports the count for both logs so the elimination is on the record rather than in this paragraph. |

---

## 5. THE REGISTERED PREDICTIONS

**Falsifiable, stated before the reader exists, and one of them is a deliberate bet against the lane's own only observation.**

- **P1 (channel).** In `D6R O_mp_20260828T162849Z_1898072.log`, restricted to lines **1 … 264048** (i.e. strictly before the IPOPT summary block that begins at `:264049`), the count of non-finite numeric tokens — `nan`, `-nan`, `inf`, `-inf`, `NaN`, `Inf` in any case, appearing as or inside a numeric field of a DAFoam or OpenMDAO print — is **exactly 0**.
- **P2 (dose).** Per-scenario primal-failure rate in D6R is **strictly monotone increasing** in CL target: `r(cl04) < r(cl05) < r(cl06)`.
  > **DISCLOSED CONTRARY DATUM.** The single terminal failing primal the lane inspected before this freeze reported `CL: 0.3953622816`, which attributes to **`cl04`** — the *lowest* target (§2 A16). **P2 is registered against the lane's only observation, on mechanism (H2), not on data.** If P2 is refuted, H2 falls and the lane's physical reasoning was wrong; that is the point of registering it.
- **P3 (specificity).** The **lowest** of the three per-scenario failure rates in D6R is at least **5×** the D4 single-point control rate of **2.222 %** — i.e. `min(r) ≥ 11.11 %`.
  > P2 and P3 are in deliberate tension. If failures concentrate entirely in `cl06`, P2 passes and P3 fails. If all three scenarios fail alike, P3 passes and P2 fails. The 2×2 is the discriminator and is registered as such: **P2✓P3✗ ⇒ dose (H2). P2✗P3✓ ⇒ the assembly (H3). P2✓P3✓ ⇒ both. P2✗P3✗ ⇒ NULL, see §8.**
- **P4 (coupling).** For each of the 673 `Cutting back alpha due to evaluation error` lines in D6R, scanning backward to the nearest preceding `Driver debug print for iter coord` line, at least one `Primal solution failed!` banner lies strictly between them, for **≥ 90 %** of the 673.

---

## 6. THE GATES

Each gate names its artifact, its threshold and its label. Thresholds are frozen at this commit and may not move (`CLAUDE.md` rule 2).

| gate | question | artifact | PASS | GATE FAIL |
|---|---|---|---|---|
| **G-SO3D-P** | **PLANT CONTROL.** Does the reader see deliberately planted failures? | `so3d_plant_report.json` | all three plants of §7 detected **exactly** as registered | any plant missed or mis-located |
| **G-SO3D-1** | channel: value or flag? | `so3d_replay.json` → `nonfinite_census` | P1 holds (count == 0) ⇒ H1 stands | count ≥ 1 ⇒ H1 refuted, H6 revived; the census names file, line and token |
| **G-SO3D-2** | dose-response in CL target | `so3d_replay.json` → `per_scenario` | P2 holds (strict monotone) | not monotone ⇒ H2 refuted |
| **G-SO3D-3** | multipoint-specific vs case-specific | `so3d_replay.json` → `per_scenario`, `controls` | P3 holds (`min(r) ≥ 11.11 %`) | `min(r) < 11.11 %` |
| **G-SO3D-4** | single-scenario poisoning of the sum | `so3d_replay.json` → `cutback_coupling` | P4 holds (≥ 90 %) | < 90 % |

**Gate ordering, and it is not negotiable.**

1. **G-SO3D-P is scored first.** If it does not PASS, the reader **exits 2** and **every other gate is `NOT A RESULT`**, whatever number it computed. A clean sheet from a sentinel not shown able to see a dirty one is not evidence (`CLAUDE.md` rule 3).
2. **A missing or truncated log is `NOT A RESULT`, never a zero.** The reader asserts each of the four logs exists, is non-empty, and its byte length and sha256 match the values recorded by the reader at first read, before scoring anything.
3. `NOT A RESULT` can only replace a `PASS` or a `GATE FAIL`; it is never reversed (`CLAUDE.md` rule 5's ordering principle, applied here to the plant rather than to a grid triple).

---

## 7. THE PLANTED CONTROL — THREE CHANNELS, AND THE RELATIVE SIZING RULE

**`CLAUDE.md` rule 3, and the specific repair SO-2M paid for on 2026-08-31: a plant is sized RELATIVE to the quantity it perturbs, never as a bare absolute.** SO-2M planted `1.234e-03` into a functional it had never been sized against; it was 2.48 % of that functional and could not cross its own 5 % band, so the control could not have failed and therefore proved nothing. **Every plant below is defined as a transformation of the quantity's own value, or as an insertion into the quantity's own alphabet, and each is constructed to cross the threshold the reader actually tests.**

Plants are applied to a **copy** of the log under the run root. **The originals in `/home/ubuntu/certonomous-runs/` are never written to**, and the reader asserts the original's sha256 is unchanged after the plant pass.

| plant | channel | definition (content-addressed, not by absolute line number) | registered expectation |
|---|---|---|---|
| **PLANT-A** | **value** | In the copy, take the **first** line matching `^CD: ` at or after line **200000**. Replace its numeric value with the token `nan`. | `nonfinite_census` reports **exactly 1** non-finite, at that line, field `CD`. Census on the unplanted copy reports **0**. A reader that returns 0 on the planted copy **refuses**. |
| **PLANT-B** | **flag** | In the copy, **delete** the first `Primal solution failed!` at or after line **200000**, and **insert** one immediately after the first `End` line at or after line **100000**. | The per-scenario failure counts move by **exactly −1** in the scenario owning the deleted banner and **exactly +1** in the scenario owning the inserted one, and the total is unchanged at **671**. Any other movement **refuses**. |
| **PLANT-C** | **dose / classification, RELATIVE** | In the copy, take the first line matching `^Primal min residual ` at or after line **150000**, read its value `R`, and rewrite it as `R × 1e-4`. | **Sized by construction to cross the reader's own threshold:** the measured plateau is `R ≈ 7.09e-05`, so `R × 1e-4 ≈ 7.09e-09`, which is **below `primalMinResTol = 1.0e-8`**. The reader's converged/failed classification for that one record must **flip** from failed to converged, and no other record may move. A plant that does not flip the classification **refuses** — and, per the SO-2M lesson, the multiplier is registered as a **ratio against `R` itself**, not as an absolute residual, precisely so it cannot fail to cross. |

**Refusal semantics.** On any plant miss the reader prints the plant, the expectation, what it actually saw, and exits **2**. It does **not** degrade to a warning (`CLAUDE.md` rule 4's refuse-rather-than-degrade principle).

---

## 8. THE NULL-RESULT CRITERION

**Registered before the run, so a null cannot be dressed up afterwards.**

If **G-SO3D-1 PASSes** (value channel clean) while **G-SO3D-2 and G-SO3D-4 both GATE FAIL** (no dose-response, no single-scenario coupling), then the failure population is **not attributable by log replay**. In that case:

- the rung's mechanism finding is **`NOT A RESULT`**, stated in those words;
- the rung still reports G-SO3D-1 and G-SO3D-3 as measured verdicts, because those are independent measurements and remain valid;
- the rung **names the instrument that would be required** — a per-trial-point trace inside the runScript carrying, for each scenario and each evaluation: the design vector, the warped-mesh quality metrics, the primal's residual history, `DASolver.primalFail`, the functional values, and the boolean actually returned to pyOptSparse — and registers it as **Stage 2**;
- it proposes **no remedy**. A remedy proposed on a null is the blind retry this rung exists to replace.

**A second null path.** If the plant control fails (G-SO3D-P), the rung is `NOT A RESULT` in its entirety and the reader itself is the finding.

---

## 9. VEHICLE — AND WHY THE BRIEF'S DICHOTOMY IS DECLINED

The brief posed a choice between the cheap incompressible A1 vehicle (which has never reproduced the pathology) and the compressible A2 vehicle (where the pathology lives, at roughly 2,000 core-min per attempt). **Neither is taken, because a third option dominates both.**

**PRIMARY VEHICLE: the compressible A2 logs that already exist on disk.** The pathology has already been reproduced **twice** on A2 — D6 (546/822 primal failures, killed by its container deadline at `rc=124`) and D6R (671/977, dead on the `EXIT:`) — at a MEASURED combined cost of **2000.533 + 2257.933 = 4258.466 core-min** the lab has already paid. Those logs carry, per §2 A14, the attribution markers needed: 985 `Setting UMag = 100 AoA = X degs` lines against 977 primal starts, 768 driver-debug blocks, and a `CL:`/`CD:` print at the foot of every primal. **This vehicle reaches the exact case where the pathology lives, on the exact toolchain row that produced it, at ZERO solver core-minutes.** A cheap diagnostic that reaches the phenomenon beats an expensive one that reproduces it, and this one reaches it without a solver at all.

**The two single-point controls are part of the vehicle and are the reason it can say anything specific.** `CURRICULUM-D4-a2-wing-cdmin` shares the D6R base mesh by ledger (`base_src=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/base`), the same solver, the same image digest and the **identical** `primalMinResTol 1e-8` / `primalMinResTolDiff 1e3` (`d4_opt_runScript.py:36-37` against `d6r_opt_runScript.py:64-65`). It failed **3 of 135**. `CURRICULUM-D5` failed **2 of 171**. Without those controls the multipoint rate would be a number with nothing to be large *relative to*.

**INCOMPRESSIBLE A1 IS DELIBERATELY NOT THE VEHICLE, and the reason is evidential, not economic.** A1 has never reproduced this pathology, and the lab's only incompressible multipoint attempt — `curriculum_SO3aR` — died tonight on a **different and unrelated** cause: no per-point `run_directory`, so all three scenarios renamed to the same time `0.0001` and collided inside `pyDAFoam.renameSolution` (`curriculum_SO3aR/RESULTS.md:179,185,196`, pointing at `pyDAFoam.py:1543`). **That is a lab plumbing regression, not the pathology**, and this document does not conflate the two. There is therefore **no incompressible multipoint evidence on disk to replay**, and a rung that cannot reach the phenomenon is not an investigation of it.

**How the incompressible half of Sanaa's directive is answered.** It is answered by **Stage 3, registered here as scope and not frozen**: once SO-3aR's `run_directory` regression is repaired and an incompressible multipoint run exists, the *same reader* is pointed at it and the same four gates are re-scored. **The reader is written to be case-agnostic for exactly this reason** — it keys on `Primal solution failed!`, `Setting UMag`, `Driver debug print for iter coord`, `CD:`/`CL:` and the IPOPT major table, all of which are solver-independent DAFoam/mphys/pyOptSparse strings present in `DASimpleFoam` runs too. **If the incompressible transfer shows the same signature, the mechanism is the multipoint assembly; if it does not, the mechanism is compressible-specific.** That is the transfer test, and it is Stage 3.

---

## 10. WHAT IS NOT FROZEN HERE

- **Stage 2** — the instrumented, bounded, primal-only probe at design points extracted from the failing majors, carrying the per-trial mesh-quality trace that Stage 1 provably cannot supply (H4, §4). Its threshold, cap and label are **not** set by this document and it may not run under this freeze.
- **Stage 3** — the incompressible transfer test, blocked behind the SO-3aR `run_directory` repair.
- **Any remedy at all.** No tolerance change, no solver change, no `max_iter` change, no restart strategy and no multipoint reformulation is registered, proposed or implied.

---

## 11. COST, CAP AND STOP RULE (`CLAUDE.md` rule 12)

**Stage 1 buys ZERO solver core-minutes.** It launches no container, no MPI job and no OpenFOAM process. It is single-process post-processing on the host over four log files, `np = 1`.

| field | value |
|---|---|
| unit | **core-minutes** = wall seconds × ranks ÷ 60 |
| ranks | **1** (host post-processing; no container, no queue entry) |
| **predicted cost** | **6 core-min** point estimate, **3–10 core-min** bracket. Basis: four logs totalling ≈ 0.9 M lines, three full passes each (census, attribution, coupling) plus the plant pass on a copied 264,607-line log. **This is a PREDICTION, not a measurement.** |
| **registered cap** | **12 core-min** |
| **stop rule** | At **12 core-min** the reader **stops**. An overrun does not receive a new budget (`CLAUDE.md` rule 12). A rung stopped at the cap is **`BLOCKED`** on cost and is **not** `GATE FAIL`; no gate below it is scored. |
| solver core-min | **0**, capped at **0**. Any solver launch under this item id is out of registration. |
| **cost basis** | **MEASURED at completion** from `/usr/bin/time` wall seconds × 1 rank ÷ 60, recorded in `so3d_replay.json` → `cost_core_min_measured`. |
| dollars | **DERIVED, NOT MEASURED.** At the recorded rate **$0.0513/core-h** (owner-stated 2026-08-21/22): 12 core-min cap = 0.2 core-h = **$0.01026**. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so this figure is derived and is **reported-by-owner**, never measured. |
| pre-authorisation | Under $25 and therefore inside the standing pre-authorisation. **A blanket is not a per-item read** (`CLAUDE.md` rule 9): the item is costed here on its own terms. |
| scale, for calibration | D6R's own single attempt cost **2257.933 core-min MEASURED** (`ledger.txt`). This rung's cap is **0.53 %** of one reproduction attempt. |
| **rule-12 calibration** | On completion, predicted (6 core-min point, 3–10 bracket) against measured, with the ratio and its attribution, lands as a row in `docs/COST_CALIBRATION.md`. **A completion report without it is incomplete.** |

---

## 12. THE GRADING PATH, AND THE ONE CONDITION THIS FREEZE LEAVES OPEN

`CLAUDE.md` rule 2 fixes the grading path at the pre-registration commit and requires the frozen file to be hashed against its committed blob. **This commit freezes the pre-registration only; the reader `so3d_replay.py` does not yet exist.** That is disclosed rather than papered over, and the rule-2 pre-compute amendment path is used exactly as it is written — *"Before first compute, amendments are legal and must state the condition and how it was checked (name the run directory that does not exist)."*

**Registered condition, and it is binding.** Stage 1 **may not run** until `cases/dafoam/ladder-a/A2/curriculum_SO3D/so3d_replay.py` is committed and its **md5 and line count** are recorded in a dated amendment appended to the foot of *this* document, under the `DAFOAM_CHARTER.md` §6 / `CLAUDE.md` rule 6 amendment form (version bump, `lines whose number changed above this section: 0`). **The amendment may add the hash. It may not alter a gate, a threshold, a prediction, a plant, a cap or a label.**

**How the condition was checked, 2026-08-31T20:55:03Z:** the run root **`/home/ubuntu/certonomous-runs/CURRICULUM-SO3D-a2-wing-multipoint-rootcause` does not exist**; `verification/queue/dafoam/` carries no `so3d` entry; `docker ps -a` matches **0** containers named `so3d`; and `cases/dafoam/ladder-a/A2/curriculum_SO3D/` contains this document and nothing else. **No compute has occurred under this item, so the pre-compute amendment window is open.**

**Frozen artifact names** (fixed now, so a later file cannot be substituted): `so3d_replay.py` (reader), `so3d_replay.json` (result), `so3d_plant_report.json` (plant control), `RESULTS.md` (record). All under the case directory. **No repository document produced by this item may cite a scratchpad path** (`CLAUDE.md` rule 13).

---

## 13. FREEZE STATEMENT

This document is **FROZEN** at the commit that introduces it. After first compute its gates are closed; anything further lands as a dated addendum that cannot alter a gate, threshold, cap or label, and originals are struck rather than rewritten (`CLAUDE.md` rule 2, rule 6).

**FREEZE ONLY. NOT ENQUEUED. NO QUEUE ENTRY. ZERO SOLVER CORE-MINUTES. SUBMISSIONS PARKED.**
