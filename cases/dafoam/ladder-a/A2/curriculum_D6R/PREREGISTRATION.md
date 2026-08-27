# Curriculum D6R — the successor D6's two grader defects require: a chain stop that GRADES, a cap enforced and graded on clocks that agree, and a stall that is not a cap hit

**Item id:** `D6R` (dafoam curriculum successor to `D6`, `cases/dafoam/EXPERTISE_CURRICULUM.md:96`).
**Version 1.0 — FROZEN 2026-08-27 by dafoam `lab-lane` M for `dafoam-supervisor`.**
**Committed BEFORE any container starts** (`CLAUDE.md` rule 2). The freeze sha is the commit that
introduces this file. Permission for detached launches: **`bc0e687e`** (Sanaa's words, boarded
verbatim). **Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7;
`DAFOAM_CHARTER.md` §10). **No frozen file is edited** (rule 6). **This item has burned 0 core-min,
started no container, and IS NOT ENQUEUED** — the queue entry beside this file is a **DRAFT**.

> **ID-NAMESPACE WARNING.** `docs/DOCKET.md` carries fleet-defect rows numbered D5, D6, D14, D15 —
> different objects from the dafoam curriculum items. Every `D<n>` in this file is the **curriculum**
> item.

## 0. What D6 produced, and why a successor is the only route

D6's `O_mp` ran 8 h 20 m and was killed by its own registered container deadline. Its ledger row
(`/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint/ledger.txt`) reads
`rc=124 wall_s=30008 ranks=4 core_min=2000.533 cap_core_min=2000.0 enforced_wall_s=30000
inspect(exit,oomkilled)=[124 false] delivered_cores_mean=[3.9768 n=1984 max_nr_throttled=98176]`,
and `STATUS.chain` closed `chain=STOPPED_AT_FIRST_NONZERO arm=O_mp rc=124`, so `ACC_mp`, `F_mp` and
`REF_off` never ran. **D6's item verdict is `NOT A RESULT` by comparator refusal with ZERO gate
readings, and it stands.** The item spent **2,000.533 core-min**, so **its gates are CLOSED**
(rule 2) and **rule 5 is one-way**: nothing on D6 is repaired here. **`VERIFICATION_CHARTER.md`
§2d.1 has been refused seven times in this family and is not proposed an eighth time.**

Three registration defects are carried forward as repairs, and nothing else moves.

**`D6-GRADER-DEF-1` — the registration and the instrument contradict each other.** D6's
`PREREGISTRATION.md:115-117` registers a chain stop at `O_mp` as a *meaningful outcome* — *"a
finding about multipoint feasibility at np=4 on this box, not a wasted run"* — and `:299` lists
`STOPPED_AT_FIRST_NONZERO` among its registered chain outcomes. **But `d6_grade.py:218-220` refuses
whenever any arm lacks a ledger row** (`refuse("G1", {"arm_absent_from_ledger": …})`, exit 2). The
driver is registered to stop the chain; the grader is registered to require all four arms. **The
item could not grade one of its own registered paths** (L-322).

**`D6-GRADER-DEF-2`, latent.** `d6_grade.py:176-179` calls `subprocess.run(..., capture_output=True,
text=True, stderr=subprocess.STDOUT)`. That combination raises `ValueError: stdout and stderr
arguments may not be used with capture_output`, **reproduced on this box under `python3` AND
`python3 -O` (CPython 3.12.3)**, so `docker_logs()` has never been able to return since freeze. Its
only call site is `:224`, reached only when an arm is missing from the ledger **and** exactly one
container survives to stand in. On D6's run `names` was empty and `:219` refused first. Had one
leftover container existed, **the grader would have died with a traceback instead of refusing**
(L-357).

**`D6-CAP-FRAME-1` (L-371), measured.** D6 enforced its cap as `timeout` **inside** the container
(`d6_run_arm.sh:347`) and graded `CORE_MIN` from a wall bracketed around `docker run` **on the
host** (`:336`/`:376`/`:399` → `d6_grade.py:502`). Measured gap **30,008 − 30,000 = 8 s = 0.5333
core-min at 4 ranks**, and the recorded excess is **2,000.533 − 2,000.000 = 0.533 core-min — the
same number. An arm that obeyed its registered deadline exactly recorded 0.027 % above its own cap.**
D6's `D4_CAP_ASSERT` (`d6_run_arm.sh:194-202`) cannot catch it: it derives the timeout from the cap
and re-checks by **inverting the same arithmetic inside one frame**, so it passes on every run.

---

## 1. What changes from D6, and only this

| | D6 (`NOT A RESULT`, comparator refusal, zero gate readings) | D6R |
|---|---|---|
| case, mesh, np=4, FFD 6×2×8 (96 DVs), twist (7), decomposition, three scenarios `cl04`/`cl05`/`cl06`, CL targets 0.4/0.5/0.6, weights **w = (0.25, 0.50, 0.25)**, composite `J = Σ wᵢ·CDᵢ`, geometric constraints, `findFeasibleDesign` trim | as D6 | **identical, byte-for-byte** — the four science instruments are D6's bytes with only the `d6_` → `d6r_` rename (`d6r_*_DELTAS_from_d6.diff`) |
| toolchain row | PATCHED `dafoam-idwarp-rot:v1` only; SHIPPED named **unbought** | **identical — PATCHED ONLY**; `G-ROW` refuses SHIPPED; §6 |
| optimiser | IPOPT `tol` 1e-5, **`max_iter` 100** | IPOPT `tol` 1e-5, **`max_iter` 80** — **the one science delta**, one line of `d6r_opt_runScript.py`, shown in full in §7. **The reason is not taste: at the MEASURED rate 80 majors cost 2,500.6 core-min and the registered compute window is 2,894.0, so THE OPTIMISER'S OWN CAP BINDS BEFORE THE CONTAINER DEADLINE, the arm exits rc=0, and the chain continues — which is exactly what D6 could not do.** 80 is D6's own P1 point, so this is a strict reduction in rope, never an extension |
| O_mp cap | 2,000.0 core-min, from `6.389 × 3 = 19.167` core-min/major | **2,900.0, RE-DERIVED FROM THE MEASURED 31.258 core-min/major** (§4). D6's cap could never have been met |
| cap frame | enforced in the container, graded on the host, unreconciled | **`FRAME_ALLOWANCE_S = 90`, the deadline moved DOWN, cross-pinned in launcher AND grader, and the container's own kernel clock recorded and GRADED** (§4b) |
| chain stop | registered as a finding; **refused by the grader** | **GRADED. The arms that ran are graded on their own limbs; the arms that did not are NAMED with their reason** (§3a) |
| optimiser outcome | not classified; a cap hit and a stall are the same row | **`G-D6R-OPT`, a registered five-rung ladder; a STALL is distinguishable from a cap hit and outranks it** (§3c) |
| `docker_logs()` | raises `ValueError` on every call | **repaired and DRIVEN under both interpreters** (§7, check 3a–3c) |

---

## 2. Arms — four, in this order, one detached chain

| arm | kind (G1) | task | work dir | container mem | new compute |
|---|---|---|---|---|---|
| O_mp | SOLVER | IPOPT `run_driver` on `J`, `max_iter` **80** | `O_mp/` (+ `mp04/ mp05/ mp06/` copies inside it) | 20g | yes |
| ACC_mp | SCRIPT | `compute_totals` on a cold staged copy: three primals + three adjoints in one process; the artefact is the log | `ACC_mp/` | 20g | yes |
| F_mp | SOLVER | `d6r_extract_endpoint.py` then `d6r_fd_endpoint.py`: endpoint FD table of **J** over five registered components | **`O_mp/`** — see §3b | 20g | yes |
| REF_off | SCRIPT | D4's PATCHED optimum geometry (staged read-only, md5 `0d956d6ccbc010402915710f662d3b11`) re-trimmed to CL 0.4/0.5/0.6 by `findFeasibleDesign` on the three `patchV` **only**; writes `d6r_ref_off.json` | `REF_off/` | 20g | yes |

Chain: `d6r_chain_driver.sh O_mp ACC_mp F_mp REF_off`, stops at the first non-zero rc — **and that
stop is now a GRADEABLE outcome** (§3a). **The five FD components, NAMED IN ADVANCE:** `shape[46]`,
`shape[18]`, `shape[0]`, `twist[0]`, `patchV_cl05[1]`.

---

## 3. Gates — registered before compute

`d6r_grade.py` (md5 in §7) is the grading path. Vocabulary: `PASS / GATE REACHED / GATE FAIL /
NOT A RESULT / BLOCKED / PENDING` and no other word.

### 3a. THE ARM CENSUS — how a chain stop is graded without refusing (repair 1)

Before any gate, the grader builds a census of the four registered arms, in this fixed order:

1. **a ledger row exists** → `RAN`.
2. **no ledger row, but exactly one surviving container** carrying `d6r_<ARM>_` → `RAN`, from the
   kernel record (a lost ledger row is bookkeeping and never voids physics, L-342). **Two or more
   candidates still REFUSE** — that is the guard `REFIRE_RUNBOOK.md` §1 forbids loosening, and it is
   **not** loosened: the line below a relaxed count reads rc from an earlier fire, and rc is physics.
   **Only the ZERO case moves**, because zero is not ambiguity, it is absence.
3. **no ledger row, no container, and the driver's own `STATUS.chain` accounts for the absence** →
   `NOT_RUN`, with `reason = REGISTERED_CHAIN_<OUTCOME>`, the stop arm and the stop rc **written into
   the verdict artefact**. The accounting outcomes are registered here and in the instrument:
   `STOPPED_AT_FIRST_NONZERO`, `STOPPED_H5`, `BLOCKED_H5`, `BLOCKED_AGGREGATE`,
   `REFUSED_ALREADY_BOUGHT`, `ABORT`. **`COMPLETE` accounts for nothing** — after a complete chain no
   arm may be missing.
4. **otherwise → REFUSE**, with the same message class D6 used. **This is not a widening.**

The driver is amended by one registered delta so the census is read from its own record and never
inferred: the stop line now carries `order=[…] not_run=[…]` beside `arm=` and `rc=`.

**Consequences, registered:**
* A gate whose input artefact's **producing arm did not run** returns **`NOT A RESULT`** naming that
  arm, the artefact and the reason `ARM_DID_NOT_RUN`. **Never `GATE FAIL` — nothing was measured
  that could fail.** The producer of every registered artefact is tabled in the instrument
  (`ARTEFACT_PRODUCER`).
* A gate whose input artefact is **absent although its producer DID run** still **REFUSES** —
  D6's behaviour, preserved exactly.
* **`G1` reports two separate facts**: `ran_clean` (every arm that ran held every completion clause)
  and `all_arms_ran`. A chain stop makes the second false and can leave the first true, **and the two
  are never the same verdict**.
* Arms that did not run bought **0 core-min** and are named as such at `G10`.
* `G9` and `G12` grade the arms that ran and **name the arms they did not grade**.

**A strengthening adopted at the same time, disclosed because it is not one of the three repairs:**
D6's grader silently kept the LAST of two ledger rows for one arm. D6R **refuses** on
`duplicate_arm_row`, as the family's other five graders do. A strengthening can only turn a pass
into a stop.

### 3b. `ARM_DIR` — the mapping, its reason, and its assertion (repair 2)

**A CORRECTION AGAINST THE BRIEF THAT COMMISSIONED THIS ITEM.** The brief called
`ARM_DIR["F_mp"] = "O_mp"` an aliasing defect. **It is not a defect; it is the registered design, and
it is correct.** `F_mp` is registered to run **inside** `O_mp/` — D6 `PREREGISTRATION.md` §2 gives
F_mp the work dir `O_mp/`, and `d6_run_arm.sh:278` sets `WORK="$BASE/O_mp"` for that arm, stages only
the two FD instruments into it, and reads the optimiser's `OptView.hst` there. A per-arm artefact is
therefore already sought where the arm that writes it puts it.

**The real fault next to it** is the one repair 1 fixes: when `F_mp` never ran, its three products
were absent from a directory that exists and is populated by `O_mp`, and D6's grader had no way to
say *"that arm did not run"* — it refused. The mapping was never the problem.

**What D6R adds, therefore, is not a new mapping but an assertion and a producer table:**

| arm | work dir | reason (registered) |
|---|---|---|
| `O_mp` | `O_mp/` | its own staged case |
| `ACC_mp` | `ACC_mp/` | its own staged case |
| **`F_mp`** | **`O_mp/`** | **registered to run inside `O_mp/` — it reads the optimiser endpoint** |
| `REF_off` | `REF_off/` | its own staged case |

| artefact | producing arm |
|---|---|
| `opt_IPOPT.txt`, `OptView.hst` | `O_mp` |
| `d6r_fd_endpoint.json`, `d6r_endpoint_dvs.json`, `d6r_major_history.json` | `F_mp` |
| `d6r_ref_off.json` | `REF_off` |

`d6r_grade.py:launcher_mapping_check()` **reads the launcher's own bytes** and refuses unless
`WORK="$BASE/O_mp"` is present in it. Driven, and shown to refuse when pointed at a line the launcher
does not carry (check 2m). A mapping nobody checks is a mapping that drifts.

### 3c. `G-D6R-OPT` — the optimiser's own outcome, and a stall is not a cap hit (repair 3)

`DAFOAM_CHARTER.md` §9: an optimiser stopped by a wall clock, an iteration cap or a budget is
`GATE REACHED` where a registered intermediate threshold was met and `NOT A RESULT` otherwise —
**never `PASS`**. D6 did not merely run slow. Measured on its own log
(`O_mp_20260827T140924Z_805560.log`, read read-only at zero compute and driven through this
classifier at check 5h): **548** occurrences of `Cutting back alpha`, **64** majors after the initial
point, **7** restoration majors, and dual infeasibility **worsening from 5.78e-04 at major 58 to
1.14e-03 at major 64** against `tol` 1e-5.

**The ladder, evaluated in this REGISTERED ORDER:**

| rung | condition | optimisation limb |
|---|---|---|
| 1 | **`DEADLINE`** — `rc == 124`, or the container's own kernel wall ≥ the registered deadline | **`NOT A RESULT`**; the endpoint is not a design point the optimiser chose |
| 2 | **`STALLED`** — no `EXIT: Optimal Solution Found` **AND** `S1` **AND** `S2` | **`NOT A RESULT`**, with every indicator printed beside it |
| 3 | **`ITERATION_CAP`** — `EXIT: Maximum Number of Iterations Exceeded.` and not stalled | **`GATE REACHED`** if `G-D6R-2` is `PASS`, else `NOT A RESULT`. **Never `PASS`.** |
| 4 | **`CONVERGED`** — `EXIT: Optimal Solution Found.` | `PASS`-eligible |
| 5 | anything else | **`UNCLASSIFIED` → `NOT A RESULT`**, EXIT line quoted verbatim |

**`STALLED` is tested BEFORE `ITERATION_CAP`**, so a stalled run that also exhausts its iterations is
reported as a **stall** — the more informative label, and the one that cannot flatter. The two
indicators, registered with their thresholds before compute:

* **`S1` (line search failing):** `cutbacks_per_major ≥ 1.0`. A converging IPOPT line search accepts
  `alpha` on most majors; a sustained rate ≥ 1 means it fails once per major on average. **D6 measured
  8.56/major**, so the threshold is set at roughly one eighth of the measured value — deliberately
  conservative, so a healthier run is not called stalled.
* **`S2` (no dual progress):** `inf_du(last major) ≥ inf_du(major at 90 % of N)`. Dual infeasibility
  not decreasing over the final decile.
* **`S3` (restoration):** the count of `r`-suffixed major rows is **reported beside the verdict and
  does not gate**, because a healthy IPOPT run may take one.

### 3d. The other gates, and the registered verdict ladder

* **G1 — completion, ARM-KIND AWARE** (D5/D6 form, unchanged): SOLVER arms — kernel `rc == 0` from
  `docker inspect .State.ExitCode` (refuse on a harness/kernel disagreement), `OOMKilled false`, the
  **positional** terminal statement `Finalising parallel run` as the last non-empty log line, and the
  age guard on the registered products. SCRIPT arms — kernel `rc == 0`, the `.ok` marker, and the
  registered artefact newer than the arm's datum; the terminal statement reported, not composed.
  **REF_off's staged input `OptView.hst` is exempt from the age guard BY MD5 ONLY** (registered
  `0d956d6c…`; a moved md5 refuses). L-342 field classes as D6: absent infrastructure → `NOT_MEASURED`
  named beside the verdict; present-but-garbage → REFUSE; absent physics → REFUSE.
* **G-D6R-1 — per-point:** for each CL target, `CDᵢ(mp) ≤ CDᵢ(REF_off)` → `PASS`, else `GATE FAIL`.
  **Three verdicts, always all three reported.**
* **G-D6R-2 — composite:** `(J₀ − J_f)/J₀` in **[15, 40] %** → `PASS`, else `GATE FAIL`. Band
  unchanged from D6.
* **G-D6R-3 — single-point price:** `CD₀.₅(mp) − CD_f(D4) ∈ [0, 1.0e-3]` → `PASS`; `> 1.0e-3` →
  `GATE FAIL`; **negative → `NOT A RESULT` pending triage** (a finding about D4). `CD_f(D4)` is
  **re-read** from `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt`
  (read-only), refused if it differs from the recorded `2.1125978108239574e-02`, through a reader
  carrying a **planted-zero control** (`PLANT = 1.234e-03`, plant-and-read-back, unperturbed copy
  unchanged; refuse if blind).
* **G-D6R-4 — the FD bright line on J:** per component `|d(s_hi) − J_adj| / |d(s_hi)| ≤ 5 %`, no sign
  flip, plateau `≤ 10 %`; aggregate vector-relative error `≤ 5 %`; **≥ 2 sign flips → `NOT A RESULT`
  (the pathology, named in advance)**. No grid family: **no GCI is quoted.**
* **G9 / G10 / G12:** PATCHED digest on every row and the PATCHED `libidwarp.so` md5 in every log
  (`D4S_IDWARP_SO_MD5:`); the cap gate of §4b; `cpuset == 2,3,4,14` on every row, delivered ≥ 3.0 of
  4 where measured, `NOT_MEASURED` disclosed.

**THE VERDICT LADDER, in order** (`d6r_grade.py:compose`). A `NOT A RESULT` can only turn a `PASS`,
`GATE REACHED` or `GATE FAIL` **into** a `NOT A RESULT`, never the reverse:

1. a completion clause failed on an arm that **ran** → **`NOT A RESULT`**;
2. a registered arm **did not run** → **`NOT A RESULT`**, arms named (the item can never be `PASS`
   with an arm unbought);
3. `G-D6R-OPT` is `DEADLINE`, `STALLED` or `UNCLASSIFIED` → **`NOT A RESULT`**;
4. the registered pathologies — `G-D6R-4` sign-flip pathology, `G-D6R-3` negative price →
   **`NOT A RESULT`**;
5. any gate `NOT A RESULT` for want of an input → **`NOT A RESULT`**;
6. else any gate `GATE FAIL` → **`GATE FAIL`**;
7. else `ITERATION_CAP` → **`GATE REACHED`** if `G-D6R-2` is `PASS`, else `NOT A RESULT`;
8. else → **`PASS`**.

### 3e. Which FD band, and why — the check the supervisor asked for

**Band D is used, and it is the right band, because no limb of D6R is an np-invariance or a
decomposition comparison.** `FD_BAND_PCT 5.0`, `AGG_BAND_PCT 5.0`, `PLATEAU_TOL_PCT 10.0` are
**inherited BY CITATION** from `VERIFICATION_CHARTER.md` §7 through D6 §3 and `DAFOAM_CHARTER.md` §2,
and are **not re-derived here**. `G-D6R-4` compares a **finite-difference estimate against an adjoint
gradient** at one np on one decomposition — the instrument band D was calibrated for. The much
tighter registered band at `docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md:91-92` — **`s_g ≤ 1.0e-3`
and `s_J ≤ 2.2e-5`, fifty times tighter than band D** — governs **np-invariance and partition
comparisons**, where the two arms differ only in decomposition and band D would be far too loose to
detect the effect at all. **D6R registers no such limb**: every arm runs at np=4 with one
decomposition, `G-D6R-1` and `G-D6R-3` compare drag coefficients between different *optimisations*
(a physics difference, gated on an absolute band, not a reproducibility band), and `G-D6R-2` is a
ratio within one run. **If a decomposition or np arm is ever added to this item it must carry the
`1.0e-3 / 2.2e-5` band and not this one.**

---

## 4. Cost — RE-DERIVED FROM THE MEASURED ANCHOR, NOT INHERITED

**The anchor, named explicitly: `31.258 core-min/major`, MEASURED on this exact case at np=4** —
C-188 (`docs/COST_CALIBRATION.md:271`, committed `8262f123`), derived as `2,000.533 core-min / 64
majors`. D6 registered `6.389 × 3 = 19.167`; **measured / registered = 1.6308×**. At the measured
rate **D6's own registered 80-major point costs 2,500.6 core-min — 125.0 % of its 2,000.0 cap, so
that cap could never have been met.** This family's estimating error is in the **anchor choice, not
the rate** (C-182), and this section fixes the anchor.

The anchor is **gross and amortises the arm's setup into its majors**. That is stated rather than
split, because D6's log carries no per-line timestamps and a two-term model would be invented, not
measured; amortising is conservative for `majors > 64` and is the figure the lab published.

| arm | anchor | predicted (core-min) | cap (core-min) | deadline in container (s) | compute window (core-min) | window / predicted |
|---|---|---|---|---|---|---|
| O_mp | **80 × 31.258 (MEASURED)** | **2,500.6** | **2,900.0** | **43,410** | **2,894.0** | **1.157×** |
| ACC_mp | 9.0 × **1.6308** (the same ×3 model, measured short by 63 %) | **14.7** | 30.0 | 360 | 24.0 | 1.635× |
| F_mp | 141.8 × **1.6308** | **231.2** | 300.0 | 4,410 | 294.0 | 1.271× |
| REF_off | 10.5 × **1.6308** | **17.1** | 40.0 | 510 | 34.0 | 1.986× |
| **total** | | **2,763.7** | **ceiling 3,270.0** | | | |

**THE `max_iter` ARITHMETIC, SHOWN (the `D5-PREREG-DEF-1` class, named and avoided):**
`max_iter = 80`; `80 × 31.258 = 2,500.6 core-min`; the registered compute window is
`TMO × ranks ÷ 60 = 43,410 × 4 ÷ 60 = 2,894.0 core-min`; **2,500.6 < 2,894.0, margin 15.7 %**.
The iteration count is **hard-bounded by the optimiser**, so the only uncertainty is the rate, and
the rate was measured over 64 majors of this identical configuration. **`max_iter` fits the cap, and
because it does, IPOPT stops itself, `rc = 0`, and the chain continues to the three arms D6 never
bought.**

* **ranks 4**; wall **11.52 h** at the estimate, **13.62 h** at the ceiling.
* **`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot
  read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED, NOT MEASURED**: estimate
  **$2.3630** (46.061 core-h), ceiling **$2.7958** (54.500 core-h). Both far inside the $25
  pre-authorisation.
* **Exposure stated, and it is the one this cost table can be wrong about.** The 1.6308× correction
  is applied to `ACC_mp`, `F_mp` and `REF_off` from the *measurement of a different arm*. C-188
  attributes the miss to the ×3 multipoint scaling, which those three arms share, but **the mechanism
  is not established** and `F_mp` does FD primals rather than adjoints. The correction may over- or
  under-price them. It is applied because under-pricing them is what cut D6's chain, and each cap's
  window is ≥ 1.27× the corrected prediction.
* **`P7` is ALREADY ANSWERED and is NOT re-bought.** D6 measured `OOMKilled=false` after 8 h 20 m at
  np=4 in a 20g cgroup — **multipoint IS memory-feasible on this box** (C-188; the ledger's
  `inspect(exit,oomkilled)=[124 false]`). D6R scores P7 only as a **regression check on an answered
  question**, never as a purchase.
* A calibration row is owed at completion (`docs/COST_CALIBRATION.md`, rule 12).

### 4b. THE CAP FRAME — `D6-CAP-FRAME-1` / L-371, repaired the D4S-F3SR way

**The cap does not move. The enforced deadline moves DOWN.** The pattern is D4S-F3SR's
(`ed9cda90`), taken deliberately rather than reinvented.

`FRAME_ALLOWANCE_S = 90`, bounded at **85 s** and registered at 90:

| term | bound | why |
|---|---|---|
| `docker run` client + container create/start + in-container preamble before `timeout` begins | 10 s | measured upper bound **3.3 s** (D4S-F3S F-S) |
| `timeout -k 60` TERM → KILL escalation grace | 60 s | `KILL_GRACE_S`, registered |
| the poll loop's `sleep 10` granularity on `T1` | 10 s | |
| `docker logs` of the arm log + `docker inspect` before `T1` | 5 s | D6 measured the WHOLE gap at **8 s** on a 10.7 MB log |

`TMO = round(CAP × 60 / RANKS) − FRAME_ALLOWANCE_S`, and the launcher **refuses** if `TMO ≤ 0` and
**refuses** unless `(TMO + FRAME_ALLOWANCE_S) × RANKS ÷ 60` equals the registered cap to 0.02
core-min. **The inversion RE-ADDS the allowance, so no edit to it can silently widen the cap.**

**Which clock each side reads, stated:**

* **ENFORCED in the container frame** — `timeout -k 60 $TMO` inside the container.
* **GRADED in the host frame** — `WALL = T1 − T0`, `T0` taken before `docker run`, `T1` after the
  poll loop, the `docker logs` dump and the `docker inspect`. `core_min = WALL × 4 ÷ 60`.
* **RECONCILED by a third reading** — the launcher now also records the **container's own kernel
  clock** (`.State.StartedAt` / `.State.FinishedAt`, in the same inspect and **before** the `rm`) into
  the ledger as `container_wall_s`, alongside `frame_allowance_s`.

**`G10` binds three limbs, not one:** `within_cap` (host bracket ≤ the registered cap);
`deadline_frame_pass` (`container_wall_s ≤ TMO + KILL_GRACE_S`); `frame_gap_within_allowance`
(`host_wall − container_wall ≤ FRAME_ALLOWANCE_S − KILL_GRACE_S = 30 s`); plus
`frame_allowance_matches_registered`, cross-pinned against the ledger's own field. **An absent
container clock is INFRASTRUCTURE** (L-342): the frame limbs go `NOT_MEASURED` and the gate falls
back to the host bracket alone, **which is the stricter reading — the fallback can never turn a
failing cap into a pass.**

**The cap was not widened to absorb a frame gap.** Driven at check 4c: with D6's own measured 8 s
gap, an arm at the repaired deadline records **2,894.533 ≤ 2,900.0**, and the same arm under the
predecessor's un-shortened deadline would record **2,900.533 > 2,900.0** — exactly the 0.533 core-min
D6 recorded, one cap up.

---

## 5. Predictions — scored HIT / MISS / NOT A RESULT afterwards, never adjusted

| # | prediction | band / point |
|---|---|---|
| **P1** | **the optimiser does NOT converge in `max_iter` 80**; `G-D6R-OPT` ∈ {`ITERATION_CAP`, `STALLED`}, **point `STALLED`** | registered against D6's own measurement — 548 alpha cutbacks over 64 majors, 7 restoration majors, `inf_du` worsening 5.78e-04 → 1.14e-03 against `tol` 1e-5. **A MISS here is good news, and that is the point of writing it down** |
| P2 | composite reduction `(J₀ − J_f)/J₀` | **[15, 40] %, point 22 %** |
| P3 | single-point price at CL 0.5 | `CD₀.₅(mp) − 2.1125978e-02 ∈ [0, 1.0e-3]`, point **+3.0e-4** |
| P4 | off-design gain `CDᵢ(REF_off) − CDᵢ(mp)` | at 0.6 **> 0**, point +8.0e-4; at 0.4 **> 0**, point +2.0e-4 |
| P5 | O_mp cost | **[1,900, 2,900]** core-min, point **2,500.6** (80 × 31.258 MEASURED) |
| P6 | per-point verdicts | **all three `PASS`** |
| P7 | **ANSWERED BY D6, NOT RE-BOUGHT** — no arm OOM-killed at 20g | regression check only; HIT/MISS by `OOMKilled` |
| **P8** | **THE REPAIR'S OWN FALSIFIER: the chain COMPLETES — all four arms run** | because `max_iter × 31.258 = 2,500.6 < 2,894.0`, the optimiser's cap binds before the container's. D6's chain died at O_mp on rc=124 and bought nothing else. HIT/MISS by `chain=COMPLETE` and an empty NOT_RUN list |

**Predicted outcome, written before compute so it cannot be written afterwards.** On P1 as
registered, the item's most likely verdict is **`NOT A RESULT` by stall** (ladder rung 2), or
**`GATE REACHED`** if the stall indicators do not fire and the composite reduction lands in band.
**`PASS` requires an optimiser convergence statement this lane does not expect.** What D6R buys
regardless of P1 is the three arms D6 never ran — the endpoint FD table on the composite `J`
(`G-D6R-4`, never measured anywhere in this lab), the off-design reference `REF_off`, the three
per-point verdicts — plus a *graded* answer to "does this multipoint problem converge at all", which
today is an inference from a truncated run. §9 puts the buy decision on the supervisor's desk.

## 5b. Placement, memory and the detached form — registered by measurement at freeze

* **cpuset `2,3,4,14`** — D6's set, measured free at freeze. The only running container on this box
  at 2026-08-27T22:44Z–23:02Z is **`d8r_O-P_20260827T223101Z_1595223`** on cpuset **`0,1,12,15`**,
  14g (read read-only by `sudo -n docker inspect`; **not signalled, not written to, not otherwise
  touched**). The two sets are **disjoint**. Core 0 is not used by D6R.
* **Memory: every arm 20g, H5 floor 24.0 GiB** (cap + 4 GiB headroom, the D4-SHIPPED §4.4 formula).
  Never 8g. **Measured at freeze with `d6r_aggregate_memory.py 20 30.6`:**
  `{"live_caps_GiB": 14.0, "live": ["d8r_O-P_…"], "this_cap_GiB": 20.0,
  "host_noncontainer_rss_GiB": 2.68, "aggregate_GiB": 36.68, "ceiling_GiB": 30.6, "ok": false}` —
  **D6R cannot start beside D8R, and this is registered rather than discovered.** The consequence is
  §9's filing question, not a defect.
* **Delivered cores are measured** (cgroup sampler); absent → `NOT_MEASURED`.
* **The detached form** — `rc` from `docker inspect` into `STATUS.<arm>` inside the driver, no
  `--rm`, root staging on first fire, `ALREADY_BOUGHT`, the `CHAIN_DONE` EXIT-trap marker from birth
  — exactly as D6 Addendum 3. **G-ROOT.5 DEMONSTRATED 2026-08-27T23:02:36Z**
  (`d6r_groot5_selftest_evidence.txt`, **20/20**), and demonstrated **without creating a single
  container**: **16 containers before, 16 after**.

---

## 6. What this item does NOT claim, and the two rows

**TWO ROWS OR IT IS NOT A VERDICT** (`DAFOAM_CHARTER.md` **§6** — and note that D8R's queue entry and
D6's own launcher comment both cite "§11" for this rule, which is a **struck slip**; §11 is the
lessons-numbering clause. Corrected in `d6r_run_arm.sh`). Both digests **re-verified LIVE at
2026-08-27T22:44Z** against `sudo -n docker inspect` (plain `docker` is permission-denied, and
`TOOLCHAIN_INVENTORY.md` §3's list is stale by its own Amendment A1.2):

| row | image | digest, read live | state in D6R |
|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **the only row bought**; `G-ROW` refuses anything else |
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **NAMED UNBOUGHT** — no D6R number is a statement about the shipped toolchain |

`G9` is driven to `GATE FAIL` on a row carrying the SHIPPED digest and on a log whose
`libidwarp.so` md5 has moved (checks 6q, 6r): a version string is not an identity.

Nothing about weight sensitivity — a second weight set is a new item. Nothing at np≠4. No Strouhal,
no grid family, **no GCI**. Nothing about the stall's *cause*: D6's 548 `Cutting back alpha due to
evaluation error` point at trial-point primal failures rather than optimiser tuning, and **diagnosing
that is a separate item this one does not propose and does not price.**

---

## 7. Instruments, frozen by md5 at this commit

| file | md5 | derivation |
|---|---|---|
| `d6r_run_arm.sh` | `243f0f631719edf7ae354410276b3cfd` | `d6_run_arm.sh` (md5 `98472772…`) + `d6r_run_arm_DELTAS_from_d6.diff` (396 diff lines): item/root; **the cap frame block of §4b**; the re-derived cap table; the container-clock read and the two new ledger fields; forbidden roots **re-enumerated from disk** (D6 carried names for roots that do not exist and omitted eleven that do); the charter citation repaired **§11 → §6**; `d6r_` prefix and pidfile |
| `d6r_chain_driver.sh` | `623f3d3243ad5c9f092a7d4bfe1b01c5` | `d6_chain_driver.sh` @ Addendum 3 (md5 `b4ddca65…` — **note the false-drift trap: §7 of D6 froze `860b9842…`, superseded through Addendum 2 to `b4ddca65…`; a check that stops at §7 reports a false GATE FAIL**, L-370) + `d6r_chain_driver_DELTAS_from_d6.diff` (157 lines): names, launcher md5, instrument md5s, **and the stop line's `order=[…] not_run=[…]`** of §3a. `CHAIN_DONE` trap from birth |
| `d6r_grade.py` | `aa93ba1f6cc1dedad8d8c7efc7f2afeb` | **the grading path.** `d6_grade.py` (md5 `a76a7d5e…`) + `d6r_grade_DELTAS_from_d6.diff` (891 lines): the arm census (§3a); the `ARM_DIR` assertion and producer table (§3b); `G-D6R-OPT` (§3c); the `G10` frame limbs (§4b); the re-derived caps; the repaired `docker_logs()`; the duplicate-row refusal; the verdict ladder (§3d). **0 `assert` nodes by AST, counter shown counting a planted one** |
| `d6r_grade_selftest.py` | `2c95c49694a8071ef7e715cf320e3e8e` | **63/63 under `python3` AND `python3 -O`** with `__pycache__` cleared before each, output identical apart from the mode label (`d6r_grade_selftest_evidence.txt`) |
| `d6r_groot5_selftest.sh` | `ee7d6eabcc7e31bde8f50b1528ed9550` | **20/20** (`d6r_groot5_selftest_evidence.txt`), **zero containers created** |
| `d6r_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | **byte-identical** to `d6_aggregate_memory.py` and to `d4s_aggregate_memory.py` @ `8b91be2b` |
| `d6r_opt_runScript.py` | `93edb4a231e13a7af065368f61a468ef` | `d6_opt_runScript.py` (md5 `ae4b0305…`) with the `d6_` → `d6r_` rename and **one science line**: `"max_iter": 100,` → `"max_iter": 80,`. `d6r_opt_runScript_DELTAS_from_d6.diff`, **20 diff lines, and that one line is the whole of the science delta** |
| `d6r_fd_endpoint.py` | `7491c3a73c232fb6744990fd8109fd63` | `d6_fd_endpoint.py` renamed; `PRODUCER_MD5` re-pinned to the new runScript |
| `d6r_extract_endpoint.py` | `1743dd4232a7f06785f71be2f285f08d` | `d6_extract_endpoint.py` renamed |
| `d6r_ref_off.py` | `ad67bbeb0c7b502262ebf5d4e8fa21cd` | `d6_ref_off.py` renamed; `PRODUCER_MD5` re-pinned |
| `d4_extract_endpoint.py` | `ee7d3c99fd716da23779cb651961918e` | D4's, **unmodified** — reads D4's history for REF_off |

**The four repairs, and where each is DRIVEN:**

| repair | driven at | shown |
|---|---|---|
| 1 — grade the arms that ran, name the arms that did not | checks **2a–2g** | the defect's own fixture returns a verdict instead of refusing; the three absent arms are named with reason, stop arm and stop rc; the arm that ran is still graded at G9/G10/G12; a stop later in the chain grades two arms and names two |
| 1′ — the guard is NOT loosened | checks **2h–2l** | an unexplained absence, a missing `STATUS.chain`, a chain that ran a different arm list, an absent product whose producer DID run, and a duplicate ledger row all still REFUSE |
| 2 — `ARM_DIR` stated and asserted | checks **1f, 2m** | the mapping is asserted against the launcher's own bytes and REFUSES when pointed at a line the launcher does not carry |
| 3 — the stall, registered and distinguishable | checks **5a–5h** | ITERATION_CAP → GATE REACHED never PASS; a stall on the same log → STALLED not ITERATION_CAP; a DEADLINE outranks a stall; an unregistered EXIT line → UNCLASSIFIED; **the classifier driven on D6's ACTUAL 10.7 MB log reads n_major 64, restoration 7, cutbacks 548 (8.56/major), inf_du 1.14e-03 at major 64 against 5.78e-04 at major 58** |
| 3′ — mutation control | check **5e** | raising `STALL_CUTBACKS_PER_MAJOR` out of reach makes the SAME log read ITERATION_CAP, so the STALLED label came from the threshold and not from the EXIT line |
| 4 — `docker_logs()` returns | checks **3a–3c** | the predecessor's exact argument combination RAISES (reproduced); the repaired function RETURNS a `str` and its stderr is merged. **Driven under both interpreters** |
| cap frame | checks **4a–4i** | the inversion equals the registered cap for all four arms; the repaired deadline is within cap and the predecessor's is not; a container outliving its deadline + grace GATE FAILs even with the host bracket inside the cap; a frame gap of 45 s > 30 s GATE FAILs; a mismatched `frame_allowance_s` GATE FAILs; an absent container clock falls back to the stricter host reading |

**Controls prove a positive branch by the ORDER of refusals, never by executing the protected path**
— every `d6r_groot5_selftest.sh` invocation passes a bogus image name into a temporary empty run root
(mode 775), so a launcher that got past G-ROOT.5 aborts at the L-251 mode check (rc=4) **before any
staging**, and the run root is asserted empty and then absent afterwards. **No mutation in this
item's selftest read INERT**; had one, it would be reported as proving nothing.

**Guard placement, verified by line number in `d6r_run_arm.sh`** (and re-verified mechanically inside
`d6r_groot5_selftest.sh`, which computes both numbers itself and refuses if the order is wrong):

| guard | line |
|---|---|
| G-ROOT.1 registered root, normalised | 35 |
| G-ROOT.2 forbidden roots, enumerated from disk | 48 |
| G-ROOT.3 ledger identity | 72 |
| G-ROOT.5 live container / live driver pid | 169–198 |
| **CAP FRAME + `D4_CAP_ASSERT`** | **227–240** |
| L-251 run-root mode 777 | 249 |
| the five staged-instrument md5 assertions | 252–256 |
| image digest and G-ROW (PATCHED only) | 260–272 |
| **FIRST DESTRUCTIVE STEP — `sudo -n rm -rf "$WORK"`** | **287** |
| **FIRST `docker run`** | **378** |

**Every guard precedes every destructive step.**

**`libs`-style insertion discipline (L-221/L-222):** no `libs` entry is added by this item; the
`ARM_DIR` mapping is **asserted at its call site**, not merely declared.

---

## 8. FREEZE

**Condition, and how it was checked (rule 2):**
`test -e /home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint` → **false**, checked three
times: at 2026-08-27T22:44Z before any file was written; at 23:02:36Z as the final assertion of
`d6r_groot5_selftest.sh` (which creates the root as a temporary empty directory, drives ten launcher
invocations into it, asserts it gained **0 entries**, `rmdir`s it and asserts its absence); and in
the committing invocation. **`sudo -n docker ps -a` carries no `d6r_` name; no `d6r_chain_driver`
process exists; `verification/queue/dafoam/` and `.../launched/` hold no `D6R` entry.**
**Container census: 16 before this lane began, 16 after — ZERO containers created.**
**This item has burned 0 core-min and started no arm container.**

**Committed BEFORE any container starts.** The grading path is fixed at this commit: `d6r_grade.py`
md5 `aa93ba1f6cc1dedad8d8c7efc7f2afeb`, **to be verified against its committed blob before grading**.
**After first compute the gates are closed**; changes land only as dated addenda that cannot alter a
gate, threshold, cap or label; originals are struck, never rewritten.

**Regime, from D4's registered flow, not guessed:** `DARhoSimpleFoam`, U∞ = 100 m/s, T∞ = 300 K →
M∞ = 0.288, Spalart–Allmaras RAS; 3D MACH wing (`curriculum_D4/PREREGISTRATION.md` §1).
**Capability-grid cell (068c2bf0): 3D · steady · subsonic-compressible.** D6R **DEEPENS** that cell's
evidence and does **not** move it: the SHIPPED row stays `PENDING`, and on this item's own registered
P1 the optimiser is not expected to converge.

---

## 9. ON THE SUPERVISOR'S DESK BEFORE ANY ENQUEUE — the buy question, stated against this lane's own item

**This is not a defect report; it is the honest reading of what D6R costs and what it is likely to
return, and it is the supervisor's call, not this lane's.**

About **90 %** of D6R's spend — `O_mp` at 2,500.6 of 2,763.7 predicted core-min — re-buys an
optimisation **this item's own P1 predicts will not converge**, in order to produce the design point
the other three arms read. The evidence for that prediction is D6's own measured log and it is
strong: 548 alpha cutbacks, 7 restoration majors, dual infeasibility rising over the last decile.
`Cutting back alpha due to evaluation error` is a *primal evaluation* failure at trial points, not an
optimiser-tuning problem, and running to 80 majors instead of 64 does not address it.

Three options, priced, for the supervisor to rule between:

1. **Enqueue D6R as frozen.** 2,763.7 core-min, $2.3630 derived, ~11.5 h. Buys the three unrun arms,
   the composite-`J` FD table, the off-design reference, three per-point verdicts, and a *graded*
   answer to the convergence question. Most likely item verdict: **`NOT A RESULT` by stall**.
2. **Ask this lane to register a cheaper variant** that keeps the three unrun arms and does not
   re-buy the optimisation — which requires ruling on whether D6's `O_mp` endpoint (an arm graded
   `NOT A RESULT`, rc=124) may serve as a successor's staged input. `REFIRE_RUNBOOK.md` §5 says a
   re-fire against an arm that bought a registered item is *"a re-registration question, not an
   operational one"* and explicitly **not a lane's to make**. This lane has not taken it.
3. **Hold D6R and register the stall diagnosis first**, so the optimisation is re-bought once, after
   the evaluation failures are understood, rather than twice.

**Filing.** `d6r_aggregate_memory.py` measured `aggregate_GiB 36.68 > 30.6, ok false` beside D8R's
live 14g, so a first-fit entry would wait at its own guard and BLOCK at zero compute — the shape
UPDATE F ruled against. If option 1 is taken, D6R should be filed as a **wait-wrapper behind D8R's
`CHAIN_DONE`**, the registered route
(`cases/dafoam/_common/dafoam_wait_then_launch.sh`, precondition
`/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/CHAIN_DONE`), exactly as D6 was filed
behind D5. **The queue entry beside this file is a DRAFT and is NOT on the drop path.** Enqueueing is
not authorisation: `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own.
