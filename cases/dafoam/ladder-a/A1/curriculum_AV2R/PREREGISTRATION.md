# CURRICULUM AV-2R — FORWARD-mode AD against REVERSE-mode AD at the TOTAL level (the dot-product / duality test) on the A1 NACA0012 baseline, `DASimpleFoam`, 4,032 cells, np = 1, TWO TOOLCHAIN ROWS — SUCCESSOR PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-27**. Lane: dafoam `lab-lane` (C). Supervisor: `dafoam-supervisor`.
**This item is the SUCCESSOR to `curriculum_AV2`, whose frozen comparator REFUSED at G1 and whose verdict is and remains `NOT A RESULT` (`0d743dc2`).** AV-2 is not re-graded, not repaired and not superseded as a record.

**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box, now or ever** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED. Permission for the detached launch: Sanaa's own words at **`bc0e687e`**. Every decision here is `[lab-attributed]`.

---

## 1. WHY A SUCCESSOR, WHAT WAS ALREADY OBSERVED, AND WHAT IS THEREFORE EXCLUDED FROM THE PREDICTION SET

### 1.1 The refusal, and the supervisor's ruling

`av2_grade.py:63` fixed `DATUM_REF = {a: ("0.orig/U" if a == "MESH" else "0/U") …}` and AV-2's §3 gate text named `0/U`. The tutorial runs **`writeCompression on`**, so a **serial** arm's solver rewrites time 0 compressed and `0/U` becomes `0/U.gz`. **AV-2 is np = 1 on every arm by registration, so it could not have reached a verdict on any arm — the refusal was structurally certain before the first container started.** Measured on AV-2's own run root and recorded in `av2r_datum_control_evidence.txt`: **4 of 4 solver arms carry only `0/U.gz`**, each strictly newer than its datum (`X-S` +55 s, `FAD-S` +402 s, `X-P` +51 s, `FAD-P` +417 s) — **the age guard's SUBSTANCE held on every arm; only the PATH vanished.**

**THE RULING, `[lab-attributed]`: `VERIFICATION_CHARTER.md` §2d.1 IS REFUSED. Re-register as successors.** The supervisor's reasoning, reproduced at the supervisor's instruction so it is not silently re-litigated later:

> This family has now refused §2d.1 four times on the same ground — **an exception used when the ordinary path is open is an exception being widened.** Here the ordinary path is not merely open, it is **cheap**: AV-1 and AV-2 together spent **28.187 core-min ($0.024 DERIVED)**, so re-registration costs about half an hour of one core to buy back. **An exception that saves $0.02 is not an exception worth having.**

### 1.2 WHAT AV-2's RUN ALREADY SHOWED — stated in full, because a prediction about something already observed is worth nothing

AV-2's arms all exited rc 0 and their artefacts are on disk. This lane read them during crash triage. **Everything in this subsection is EXCLUDED from §6's prediction set**, and §6 marks the exclusions.

1. **The registered `BLOCKED` branch fired on both images.** `FAD-S/av2_FAD.json` and `FAD-P/av2_FAD.json`: `blocked_any` **true**, 5 of 5 rows `BLOCKED`, `n_add_dvgeo` **1** on every row (a subsystem does expose `add_dvgeo`; the seed was placed), `useAD` `{"mode": "forward", "dvName": …, "seedIndex": k}` per component, and `control_fail` **false**.
2. **The registered silent-no-op hazard did NOT materialise.** None of the three forward-channel refusals (exact `0.0`, exact `1.0`, function echo) fired, because **no forward value was produced at all**. Every row carries `AnalysisError("'scenario1.coupling.solver' <class DAFoamSolver>: Error calling solve_nonlinear(), Primal solution failed!")`.
3. **The primal does NOT diverge, and it is not refused by an early guard.** Read from the arm logs: under a forward seed the primal runs the full `endTime 1000` and its residual falls **algebraically** — `U0 initRes` 1.05e-03 / 2.78e-04 / 1.56e-04 / 1.07e-04 at iterations 100 / 200 / 300 / 400, reaching 3.51e-05 at 1000. The **reverse-mode** primal on the identical staged case converges **geometrically** — 6.52e-04 / 1.48e-05 / 5.36e-07 / 1.33e-08 at the same iterations — and satisfies the tolerance at **iteration 435** with `Minimal residual 9.822715611394694e-09`.
4. **The refusal is DAFoam's own `checkPrimalFailure()`** (`src/adjoint/DASolver/DASolver.C:2721-2760` in the image), whose criterion is `primalMaxRes / primalMinResTol > primalMinResTolDiff`. With `primalMinResTol 1e-8` (the tutorial's) and `primalMinResTolDiff` at the library default **1e2** (`dafoam/pyDAFoam.py:517`), the effective acceptance is **1e-6** and the run reached **7.4997e-05** — 75× outside, and 7.5e3 against a 1e2 ratio bar.
5. **`primalMaxRes` is BIT-IDENTICAL between the two images**, and takes only two distinct values across the five seeds, in the same order on both: `7.499668076651931e-05` (`shape[0]`, `shape[6]`, `patchV[1]`) and `7.495510217564101e-05` (`shape[3]`, `shape[7]`).
6. **The forward channel IS live and DOES carry a tangent.** The arm logs print `ADF-Deriv` beside `CD` and `CL` at every print interval. At `endTime` on `FAD-S` seed `shape[0]`, the `CL` tangent reads **0.9983742395429173**, rising monotonically (0.98812 at 800, 0.99343 at 900), against the reverse-mode total for the same component of **1.037472696796837** — **3.8 % short and still climbing**. On `FAD-P` seed `patchV[1]` the `CL` tangent reads 0.08752324154522112 against a reverse total of 0.08923320066130686 — 1.9 % short. **These are LOG readings, not artefact values; no `ε_k` was computed and none is quoted, then or now.**
7. **DAFoam's own shipped forward-AD regression cannot be run in-image as shipped.** `tests/runRegTests_DASimpleFoamForward.py` exists and its reference `refs/DAFoam_Test_DASimpleFoamForwardRef.txt` is present, but its case fixture `reg_test_files-main` is **absent from both images** and `tests/Allrun` retrieves it by `wget` from `github.com` at run time. **Not attempted; no external retrieval was made and none is authorised here.** What CAN be read without it: the regression uses `primalMinResTol 1.0e-12` with `primalMinResTolDiff 1e4` — an effective acceptance of **1e-8**, i.e. **100× STRICTER in absolute terms than this case's 1e-6** — on a 343-cell `ConvergentChannel` at np = 4. **So the tolerance configuration is not the explanation**; and `av2r_xf.py`'s forward loop reproduces `tests/testFuncs.py:17-52` (`run_tests`) exactly — fresh `om.Problem` per component, `prob.setup(mode="rev")`, `add_dvgeo`, `run_model()`, tangent read as `prob.get_val(func)[0]`. **The invocation pattern is not the difference; the case is.**

### 1.3 WHAT AV-2R THEREFORE BUYS, STATED BEFORE IT RUNS

**Three things, and no more.**

1. **An AWARDABLE VERDICT instead of a refusal.** AV-2's `RESULTS.md` §2 says it plainly: `BLOCKED` is not a verdict a lane may award by reading the composition rule off a run whose comparator refused first. With G1 able to read, the registered composition — *"either row `BLOCKED` → `BLOCKED`"* — produces a verdict the record can carry.
2. **A DETERMINISM measurement on the ADF primal that has never been taken** (P8): AV-2 measured the terminal residual once; **nothing has ever tested whether a repeat reproduces it.** A non-reproducing `primalMaxRes` would be a far larger finding than a reproducing one, and both are worth the 15 core-min.
3. **The instrument predictions P9/P10**, which the old grader could not have produced at all.

**AV-2R's registered item verdict is `BLOCKED`, written here in advance so it cannot later be presented as a discovery.** Registering a rung whose most likely outcome is known is only honest if the freeze says so, and this one does.

**NOT decided by this lane, and named because it is the obvious next question:** whether the forward-mode primal reaches acceptance under a longer budget or a relaxed `primalMinResTolDiff` is **unmeasured**, and it is the item that would actually cash the duality test. Changing `endTime` or `primalMinResTolDiff` changes the case under test and is a **supervisor's design decision**, not a lane's. It is recorded here as an open item and is **not** part of AV-2R.

**Also NOT decided here:** `docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md` (v1.0 `aa5cd787`, v1.0a `c3f08b6d`) states that the total-level forward-AD-vs-reverse-AD form **is exposed**. §1.2 items 1, 4 and 6 bear on that claim — the channel is exposed in the API and does carry a tangent, and what refuses is the primal convergence gate. **The standard's dated correction, if one is owed, is the supervisor's and is not made in this document.**

### 1.4 What protects this freeze

**Every band, threshold, verdict rule, control and prediction P1–P7 is carried forward VERBATIM from AV-2's frozen text at `3e2cbf74`, frozen before AV-2's first container started.** No band is new; none could have been fitted to anything. The substantive change is the datum resolution in §3's G1, and **a datum resolution cannot move a number** — it decides whether the instrument can read at all, and its correctness rests on a DRIVEN CONTROL (§3a), not on the answer it produces. The four predictions added in §6 are labelled with what they are about and with which of §1.2's observations they are and are not downstream of.

## 2. ARMS — five, in this order, one detached chain, TWO ROWS, every arm np = 1 — CARRIED FORWARD UNCHANGED

`MESH`, `X-S`, `FAD-S`, `X-P`, `FAD-P`. `-S` = SHIPPED `dafoam/opt-packages:latest` (`sha256:9d45679d…5290f07fc`, `libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663`); `-P` = PATCHED `dafoam-idwarp-rot:v1` (`sha256:2927768a…dee30f6d35`, md5 `85f59e87253e0a71a813f64ca6e4c425`). Registered components: `shape[0]`, `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]`. Run root **`/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality`**. **`writeCompression on` is left exactly as the tutorial ships it** — turning it off would hide the defect rather than instrument it, and would change the case under test.

**Registered `BLOCKED` branch, carried forward verbatim:** if `libs/ADF` does not import, no subsystem exposes `add_dvgeo`, **or forward mode raises on this case**, the instrument writes the row `blocked` with the exception text, still writes the artefact, and exits 0 with `AV2R_FAD_BLOCKED` in the log. **The third condition is the one AV-2 met.**

**The planted controls (rule 3), carried forward unchanged:** artefact-level `PLANT = 1.234e-03` re-read through the same reader with `AV2R_PLANTED_CONTROL_SEEN` required in every solver log; the grader's own plant; a **SIGN-FLIPPED reverse copy** that must read `GATE FAIL` 5/5; a **silent-zero forward plant** that must be refused; and the forward-channel triple refusal (exact `0.0` / exact `1.0` / function echo within 1e-6).

## 3. GATES, THRESHOLDS AND LABELS — `av2r_grade.py` — EVERY BAND CARRIED FORWARD VERBATIM FROM `3e2cbf74`

Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else.

* **G1 — completion, ARM-KIND AWARE:** kernel `rc == 0` from `docker inspect`, `OOMKilled false`, the age guard, `AV2R_X_WRITTEN` / `AV2R_FAD_WRITTEN` **and** `AV2R_PLANTED_CONTROL_SEEN` in every solver log, `Mesh OK.` for MESH; any clause failing → **`NOT A RESULT`**. L-342 field classes unchanged; **the age guard remains a PHYSICS field.**
* **G1's age-guard datum — THE ONE SUBSTANTIVE CHANGE, identical in wording and in code to AV-1R §3:**
  1. The **datum FILE** `.av2r_age_datum` is the anchor; its own mtime must date its own recorded epoch to within `DATUM_SELF_TOL_S = 5 s` (measured on 10 of 10 AV-1/AV-2 arms: **0 s**), else REFUSE.
  2. The staged-field reference is resolved **BY EXISTENCE over the registered candidate SET** `("0/U", "0/U.gz")` — `("0.orig/U", "0.orig/U.gz")` on MESH — **never by name**. Exactly one must exist: none → REFUSE `age_reference_absent`; more than one → REFUSE `age_reference_ambiguous`.
  3. The resolved reference must be **no older than** the datum; it MAY be newer, which is the compressed rewrite and is legitimate.
  4. **`writeCompression` is read from the arm's OWN `system/controlDict` and RECORDED, never gated;** absent → `NOT_MEASURED` (L-342 infrastructure), never a refusal.
  5. The resolution travels with the verdict as `datum_resolution` in the grade json.
* **G-M2 — mesh identity:** `cells == 4,032` → `PASS`, else `GATE FAIL`.
* **G-DP — the bright line, per ROW, on CD and on CL:** for each registered component `k`, `ε_k = |g_fwd,k − g_rev,k| / max(|g_fwd,k|, |g_rev,k|)` with **band `ε_k ≤ 1.0e-5`** = 10 × the adjoint solve's `gmresRelTol` (1e-6); **the grader reads `gmresRelTol` from the artefact identity and REFUSES if it is not 1e-6** — a different tolerance is a different band. `max(|·|) < 1e-14` → `NEAR_ZERO`, component `NOT A RESULT`; a `blocked` forward row → the component and the row are **`BLOCKED`**; fewer than 3 graded components → the row is `NOT A RESULT`; any component outside the band → the row is **`GATE FAIL`** with the component named. Row verdict precedence: `BLOCKED` > `NOT A RESULT` > `GATE FAIL` > `PASS`.
* **G9 — toolchain per row:** ledger `DIGEST`, the container's `D4S_IDWARP_SO_MD5:` print and the artefact's in-process md5 must all name the row's toolchain; mismatch → `GATE FAIL`.
* **G10 — caps (§4):** every arm `core_min ≤ cap`, sum ≤ **75.0**; a crossing is `GATE FAIL`.
* **G11 — OOM hard:** `OOMKilled true` is a G1 refusal, never a re-fire.
* **G12 — placement:** `cpuset == 0,1` on every arm; delivered cores recorded, not gated, at one rank.
* **DIVERGENCE** shipped-vs-patched on the reverse CD gradient is reported per component with its number; the forward-vs-reverse discrepancy per row is the gate.
* **Item verdict (composition registered here, unchanged):** any refusal → **`NOT A RESULT`**; either row `BLOCKED` → **`BLOCKED`**; else either row `NOT A RESULT` → **`NOT A RESULT`**; else any of G-M2/G9/G10/G12 or any row `GATE FAIL` → **`GATE FAIL`**; else **`PASS`**. No grid family → **NO GCI**; no FD table → **no FD verdict is quoted**.

### 3a. THE DRIVEN CONTROL ON THE RELAXED GUARD — a guard relaxed without a control showing it can still fire is a guard RETIRED, not repaired

Seven selftest units (`UD1`–`UD7`), identical to AV-1R's, and the frozen `EXPECTED_UNITS` rises from 25 to **32** so the count itself is a gate. Evidence: `av2r_grade_selftest_evidence.txt`, **32/32 under `python3` and 32/32 under `python3 -O`, `ast.Assert` count 0**.

| unit | what it drives | required outcome |
|---|---|---|
| UD1 | every solver arm carrying **only** `0/U.gz` — the exact shape that refused AV-2 on 4 of 4 arms | grades; no refusal |
| UD2 | the resolution is recorded and names `0/U.gz`, with its candidate set | recorded |
| UD3 | `writeCompression` read from the arm's own `controlDict` | recorded `on`, never gated |
| **UD4** | **NEITHER candidate on disk** | **REFUSE `age_reference_absent`** |
| UD5 | BOTH candidates on disk | REFUSE `age_reference_ambiguous` |
| UD6 | datum content back-dated 60 s against its own mtime | REFUSE `age_datum_self_inconsistent` |
| UD7 | resolved reference older than the datum | REFUSE `age_reference_older_than_datum` |

**Driven against the REAL artefacts** (`av2r_datum_control.py`, a pre-compute diagnostic that grades nothing, reads no artefact, quotes no band and reaches no verdict): the successor grader's own `resolve_datum_ref` and `read_write_compression` are called on AV-2's run root — **5 of 5 arms resolve, 4 by `0/U.gz` and 1 by `0.orig/U`, self-delta 0 s on every arm** — then on a planted directory with neither candidate, where the guard **fires**, and on the same directory with `0/U.gz` planted, where the resolver **sees it**. Recorded in `av2r_datum_control_evidence.txt`. **This does not grade AV-2 and AV-2 remains `NOT A RESULT`.**

## 4. COST — DERIVED FROM NAMED ANCHORS, NOT MEASURED — carried forward, with AV-2's own measurement named beside it

Anchors: **C-31**, **C-71**, **C-135** as in `3e2cbf74`, and now **AV-2's own ledger**, a measurement of these very arms: MESH 0.167, X-S 1.017, FAD-S 8.267, X-P 1.017, FAD-P 8.617 → **19.085 core-min**. **The registered point is left at AV-2's 15.3** rather than moved to the measured 19.085 — the estimate is not tuned to a measurement taken after the freeze it belongs to; the gap is a calibration finding, not a band.

| arm | derivation | point (core-min) | cap (core-min) | in-container wall | mem |
|---|---|---|---|---|---|
| MESH | C-135 scaled to 4,032 cells + container start | **0.3** | 5.0 | 300 s | 4g |
| X-S, X-P | C-31 + a CL adjoint | **2.5** each | 10.0 each | 600 s | 4g |
| FAD-S, FAD-P | 1 primal + 5 forward-mode primals at 3× | **5.0** each | 25.0 each | 1,500 s | 4g |
| grader | zero compute | 0 | — | — | — |
| **total** | | **15.3** point, band **[8, 40]** | **ceiling 75.0 = Σ caps** | | |

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED**: point **$0.0131**, ceiling **$0.0641**. An overrun **stops the run**; it does not get a new budget. **A calibration row is owed at completion** (rule 12) and must compare against **both** the 15.3 point and AV-2's measured 19.085. **Already spent on this item before the freeze: 0.000 core-min of solver time** (the G-ROOT.5 selftest's sacrificial `sleep` containers, `--cpus=0.1 --cpuset-cpus=1` for a few seconds, are instrument time and are named rather than absorbed).

## 5. PLACEMENT, MEMORY AND THE DETACHED FORM — carried forward unchanged

`cpuset 0,1` on every arm; memory `4g` with `--memory-swap` equal and `--oom-score-adj=500`; one detached chain driver runs the five arms in order; per-arm in-container `timeout -k 60`; the windowed H5 memory gate before each arm; rc read from `docker inspect .State.ExitCode`, never from the `setsid` parent.

## 6. PREDICTIONS — scored HIT/MISS by the comparator, never adjusted

**P1–P7 are carried forward VERBATIM from `3e2cbf74`.** They were frozen before AV-2's first container started, so nothing observed since can have shaped them. **P1, P2 and P3 are expected `NOT_MEASURED`** because they grade `ε_k`, and `ε_k` needs a forward value that §1.2 shows was not produced. They are carried unchanged rather than withdrawn, so that **if** the forward channel does produce values this time, the band that grades them was frozen before any of this was seen.

| # | prediction | value / band | expected under §1.2 |
|---|---|---|---|
| **P1** | the PATCHED row is `PASS`: forward and reverse agree on all five components to the band | `ε_k ≤ 1e-5` on CD and CL | `NOT_MEASURED` (row `BLOCKED`) |
| **P2** | the SHIPPED row is `GATE FAIL` **on `shape[6]`** with ≥ 3 of the other 4 inside the band | `ε_shape[6] > 1e-5`, others ≤ 1e-5 | `NOT_MEASURED` (row `BLOCKED`) |
| **P3** | the PATCHED row's worst `ε` on CD is ≤ **1e-6** | `worst_eps ≤ 1e-6` | `NOT_MEASURED` |
| **P4** | the forward channel carries a tangent on both rows: no forward value is 0.0, 1.0 or a function echo | the grade reaches a verdict; a control refusal is `NOT A RESULT` | not refused; `control_fail` false |
| **P5** | FAD-S / X-S core-minute ratio in **[1.0, 4.0]** (point 2.0); total graded core-min in **[8, 40]** (point 15.3) | scored on the ledger | |
| **P6** | MESH wall ≤ 120 s | scored | |
| **P7** | `cells == 4,032` | scored | |

**FOUR PREDICTIONS ADDED FOR THE SUCCESSOR. Each names what it is downstream of, and none of them is a prediction about something already measured.**

| # | prediction | value / band | falsifier, and why it is open |
|---|---|---|---|
| **P8** | **DETERMINISM of the ADF primal.** On a fresh run, each forward arm's five `primalMaxRes` values reproduce AV-2's **to the bit** and in the same order: `7.499668076651931e-05` for `shape[0]`, `shape[6]`, `patchV[1]` and `7.495510217564101e-05` for `shape[3]`, `shape[7]`, **identically on both images** | read from the arm logs; scored as an equality on 20 values (5 seeds × 2 arms × 2 rows-of-record) | **AV-2 measured these ONCE. Nothing has ever tested whether a repeat reproduces them.** A MISS means the operator-overloaded forward primal is not deterministic on this box, which is a larger finding than a HIT and would put every forward-mode reading in the family in question |
| **P9** | **the datum resolves without a refusal on all five arms**, naming `0/U.gz` on all four solver arms and `0.orig/U` on MESH | `datum_resolution` in the grade json | MISS = the compression behaviour is not what §1.1 measured; instrument-level, cannot move G-DP |
| **P10** | `writeCompression` reads **`on`** on all five arms | recorded, never gated | MISS = the staged case is not the tutorial's |
| **P11** | **the item reaches an AWARDABLE verdict — no refusal — and that verdict is `BLOCKED`** by the registered composition | the grade json's `verdict` field | MISS in either direction is informative: a refusal means the datum repair did not reach the whole G1 path, and a non-`BLOCKED` verdict means the forward channel behaved differently on a repeat, which P8 would also register |

**Predicted item verdict, written here so it cannot be written afterwards: `BLOCKED`.** Stated in advance precisely because §1.2 makes it foreseeable. The rung is worth its 15 core-min for §1.3's three reasons and for no other.

## 7. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | derivation |
|---|---|---|
| `av2r_grade.py` | `8a2dcebd954f56d9970601fc7761787a` | AV-2's grader, renamed, + the §3 datum delta and UD1–UD7 |
| `av2r_run_arm.sh` | `5a157740ae39dc71d814f30a70ecd5ec` | AV-2's launcher, renamed, + the md5 pins that follow |
| `av2r_chain_driver.sh` | `19fdf1299113ab5172011fbfe7fe87ea` | AV-2's driver, renamed, + the md5 pins |
| `av2r_xf.py` | `32a755bc9fa84bc0e03ab02bb6ec3c3c` | AV-2's forward/reverse instrument, renamed only |
| `av2r_runScript.py` | `0557da51f6f179f6de865144343c499f` | byte copy of the shipped tutorial `runScript.py` — **unchanged by the rename** |
| `av2r_groot5_selftest.sh` | `ce7df0e4e967dcdc0e9842d450b7829a` | renamed only |
| `av2r_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | unchanged by the rename |
| `av2r_datum_control.py` | `b272e8f48d9ca01e4261745ed8d28354` | **NEW** — a pre-compute diagnostic, **not on the grading path** |

**How to audit this in two reads.** `AV2R_RENAME_MANIFEST.txt` records the mechanical step — every file read from the **HEAD blob** of `curriculum_AV2/` (never from the working tree, L-350) and passed through exactly `sed 's/AV2/AV2R/g; s/av2/av2r/g'` — with the md5 before, after the rename, and final. The three `*_DELTAS_from_av2.diff` files then show the substantive delta **against the renamed original**, so the rename does not appear in them: **209 / 14 / 19 lines**.

**G-ROOT.1–.5 driven from birth:** `av2r_groot5_selftest_evidence.txt`, **20 pass / 0 fail**, with the run root asserted **ABSENT before and after**. **No `assert` carries a guard** in any python file here (AST count 0, counted by the grader; L-332). **Classifier denials in this lane while building AV-2R: none.**

## 8. WHAT THIS ITEM WILL NOT ESTABLISH

It carries **no FD table** and moves **no capability-grid verdict** on its own. It says nothing about an optimiser, grid convergence (one mesh, no GCI), 3D or any Mach number. **It will not establish that the forward-mode channel is unusable in general** — only that on THIS case, at THIS `endTime` and THIS `primalMinResTolDiff`, the primal does not reach acceptance. Whether a longer budget or a relaxed ratio bar changes that is **unmeasured and out of scope** (§1.3). It will not re-grade AV-2, and AV-2's `NOT A RESULT` stands. **It does not amend `ADJOINT_VERIFICATION_STANDARD.md`**; any correction there is the supervisor's.

## 9. FREEZE AND QUEUE

**Committed BEFORE any container starts** (rule 2). **Freeze condition, checked and not assumed:** the run root `/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality` **does not exist** — asserted by the G-ROOT.5 selftest before and after its own run (`av2r_groot5_selftest_evidence.txt`, both lines), and 0.000 core-min of solver time has been spent in this tree.

The grading path is fixed at this commit: `av2r_grade.py` md5 `8a2dcebd954f56d9970601fc7761787a`, asserted by the chain driver before staging and again before the grade.

**NOT QUEUED BY THIS LANE.** No entry has been written to `verification/queue/dafoam/`, and the drop path is a launch button. **Enqueueing is the supervisor's act**, and `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own and is discharged on this sha. The entry, when the supervisor chooses to write it, is: team `dafoam`, `prereg_commit` = the sha of the commit introducing this file, `launch_cmd` = `["bash", "<abs>/av2r_chain_driver.sh", "MESH", "X-S", "FAD-S", "X-P", "FAD-P"]`, `cwd` = this directory, `ranks 1`, `cost_core_min_estimate 15.3`, `cap_core_min_registered 75.0`, `memory_floor_gb 8.0`, `cost_basis` derived / not measured, `permission bc0e687e`.

**Predicted outcome, written here so it cannot be written afterwards:** P4–P11 HIT, P1–P3 `NOT_MEASURED`; both rows **`BLOCKED`**; item **`BLOCKED`**; the standard's §2 status line gains its first AWARDED verdict on this rung, and it is a `BLOCKED` one.
