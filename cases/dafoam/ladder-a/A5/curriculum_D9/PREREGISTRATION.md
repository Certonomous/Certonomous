# D9 — U-BEND PRESSURE-LOSS MINIMISATION, ladder A5 — PRE-REGISTRATION

**Form:** the **10-line mini-prereg** (Sanaa, 2026-08-25: *"standard verification/validation cases
use the 10-line prereg form … minutes to freeze, not sessions"*). D9 is neither novel nor contested
— it is a tutorial-substrate optimisation on a case this lab has already gradient-verified — so it
gets the short form. **Rigor standard unchanged.**

**Frozen at the commit that adds this file. NO CONTAINER OF D9 HAS RUN: the run directory
`/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt/` DOES NOT EXIST at this commit**, and
neither does any `d9_out.json` anywhere on this box.
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

## THE TEN LINES

| # | field | value |
|---|---|---|
| **1** | **Case** | U-bend cooling channel, **4,800 cells**, `DASimpleFoam`, Spalart–Allmaras with wall functions, `U0 = 8.4 m/s`. Objective **`OBJ.val = TP1 − TP2`**, a **pure total-pressure loss** (the stock tutorial's HFX blend is not used). Design variables: **`shapexUpper` only, 27 components**, bounds ±0.04, scaler 25.0. Task: **SLSQP shape optimisation, then an endpoint FD verification of the gradient that drove it.** |
| **2** | **Reference** | **There is no external reference value** for a single-DV-group U-bend optimisation, so **the improvement magnitude is REPORTED, never gated.** The gated reference is the lab's own: `OBJ.val wrt shapexUpper` is **the one A5 total derivative this lab has FD-verified** — **PASS on the patched image, 2.768 % aggregate, 0 sign flips, np=1** (`A5/reverify_patched_idwarp_np1/RESULTS.md` §2, ledger rows 19–20). The FD side of the endpoint check is **central FD at a step PROVED to lie in a plateau**, per `DAFOAM_CHARTER.md` §1. |
| **3** | **Quantities** | `OBJ_baseline`, `OBJ_final`, `improvement`; **`delta_repeat`** (measured **before any FD step is sized**); `t_cal` from the **calibration major**; `J_an[i]`, `J_fd[i, h]` for **i = 0…26** over four registered steps; per-component plateau step `h*_i`; the gradeable count **N of M = 27**; `sched_affinity` **read back from each process**. |
| **4** | **Bands** | `FD_BAND_REL_AGG = 5.0e-2`; `MAX_SIGN_FLIPS = 0`; `PLATEAU_TOL_REL = 5.0e-2`; `PLATEAU_MIN_STEPS = 3`; `NOISE_FACTOR = 10.0`; `MIN_GRADED_FRACTION = 0.70` (**≥ 19 of 27**); `OBJ_IMPROVE_FACTOR = 10.0`; `FLOOR_DERIV = 1.0e-12`; `N_COMPONENTS_REQUIRED = 27`. FD steps: **`1e-5, 1e-4, 1e-3, 1e-2`** (spans A5's own step study's recommended 1e-3…1e-2 **and** the 1e-4 the published A5 number used). `MAXIT_CAL = 1`, `MAXIT_OPT = 20`. |
| **5** | **Ladder** | **A5**, the U-bend rung. This is the **first optimisation** on A5; every prior A5 item was a gradient check. |
| **6** | **Decomposition method AND seed** | **`np = 1` throughout.** `system/decomposeParDict` is left **byte-identical to the anchor** (md5 `1dbd9ead3f40a29f483444dc5fa1288b`), carrying `numberOfSubdomains 4; method scotch;` — and it is **NOT EXERCISED**: at `np = 1` `decomposePar` is never invoked, so the effective decomposition is the **trivial single domain** and scotch's internal randomness is never reached. **Seed:** `PYTHONHASHSEED=0` is pinned into every container. **No stochastic component exists in this chain** — SLSQP, pyGeo, IDWarp and SIMPLE are all deterministic — so there is no RNG seed to pin and none is claimed. **With np = 1 the parallel-determinism question does not arise and is not claimed to have been tested.** |
| **7** | **Criteria** | the gate table in §5 below; probe verdict = worst of **G9-0…G9-6**. |
| **8** | **Cap** | **REGISTERED CAP: 110.0 core-min**, cumulative over every container. |
| **9** | **Cost (derived)** | predicted **43 core-min** → **$0.0368**; at the cap → **$0.0941**. `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED.` |
| **10** | **Verdict labels** | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and no others. |

---

## 5. Gate table — fixed vocabulary only

| gate | test | verdict mapping |
|---|---|---|
| **G9-0** | all four of `cal`, `rep1`, `rep2`, `opt` present **and** `status == COMPLETE`; `len(shapexUpper) == 27` | a **missing or non-COMPLETE** stage → **NOT A RESULT**; a wrong **count** → **REFUSE (exit 2), count printed**; a malformed record → **REFUSE** |
| **G9-1** | **`delta_repeat` MEASURED BEFORE ANY FD STEP IS SIZED** from two identical `run_model` stages; noise floor `= max(delta_repeat, ε·\|OBJ\|)` | reported; feeds G9-3 and G9-4. **A zero repeat is DISCLOSED as bounding reproducibility only, never as bounding truncation jitter** |
| **G9-2** | the **CALIBRATION MAJOR** (`run_driver -maxit=1`) ran **FIRST** and completed | its wall time sets the buy's container timeout by the **frozen rule** `T_opt = min(3600, ceil(t_cal · (1 + MAXIT_OPT)))` — formula frozen here, input measured |
| **G9-3** | `OBJ_baseline − OBJ_final > 10 × noise floor`, driver not failed | improvement above the floor → **GATE REACHED**; not above it, or driver failed → **GATE FAIL**. **The MAGNITUDE is reported, not gated** (line 2) |
| **G9-4** | endpoint FD tables at ≥ 3 of the 4 registered steps, each at the **optimised** design point | fewer than 3 tables → **NOT A RESULT**; a *COMPLETED* stage with **no derivative key** → **BLOCKED**; a table at a **different design point** → **REFUSE** |
| **G9-5** | **N-of-M**: gradeable fraction `N/27 ≥ 0.70` | below → **NOT A RESULT**, with the ungradeable set printed and **split into named-in-advance and NOT-named-in-advance**; **zero gradeable → REFUSE** |
| **G9-6** | aggregate `Σ\|J_an − J_fd(h*)\| / Σ\|J_fd(h*)\| ≤ 5.0e-2` over **gradeable** components, **0 sign flips** | in band and no flips → **PASS**; else **GATE FAIL** |
| **G9-7** | measured `sched_affinity == [registered cpuset]` in every stage | mismatch → **GATE FAIL on the COST-ATTRIBUTION row only, NEVER on the derivative verdict** |

**Probe verdict** = worst of **G9-0…G9-6** in the order `PASS/GATE REACHED < GATE FAIL < NOT A RESULT < BLOCKED`; all clean → **`GATE REACHED`**.

**REGISTERED HONEST OUTCOME, written before the run:** *if the optimiser does not improve the
objective beyond the measured noise floor, the verdict is `GATE FAIL` and that is a reportable
result.* *If fewer than 19 of 27 components have a demonstrated plateau, the verdict is
`NOT A RESULT` and that too is a good outcome* — an aggregate quoted over components whose FD
never rose above the noise is exactly what `DAFOAM_CHARTER.md` §1 forbids. **This lane will not
manufacture a plateau by choosing a step after seeing the numbers:** the reference step is fixed by
rule — the **longest** qualifying window (ties → lowest start index), and within it the **middle**
step, **per component**.

## 5a. The plant (rule 3) — two, both on quantities that REACH THE VERDICT

1. **READER PLANT.** `PLANT = 1.234e-03` is written into `J_an[0]` of a copy of the endpoint
   record, read **back from disk**, and the difference compared to the planted value. **If the
   reader cannot see it, the grader REFUSES (exit 2).**
2. **PHYSICAL PLANT.** The optimiser must have **MOVED the design point**. If the endpoint
   `shapexUpper` is bit-identical to the all-zero baseline, the FD table is a table about the
   **baseline** geometry wearing the endpoint's name → **REFUSE**. Each endpoint stage is
   additionally asserted to have been evaluated at the *same* design point the driver ended on.

## 5b. L-302, and the D3 defect this grader is shaped against

`cases/dafoam/ladder-a/A4/curriculum_D3/d3_grade.py` returns **`PASS` at 0.0000 % with zero sign
flips over an EMPTY COMPONENT SET**: its refusal tests **key presence** and never non-emptiness, and
its plateau loop iterates zero times. Registered consequences, each **exercised by `--selftest`**:

- **refusal on an EMPTY *or SHORT* set, BY COUNT, with the count printed** (cases B, C, F);
- **no swallowed exception falling through to a declared constant** — a malformed record REFUSES (L);
- **the plateau loop cannot select a step from a zero-iteration search** — a component with no
  qualifying window is **UNGRADEABLE and COUNTED**, never defaulted to the first or last step (G, Q);
- **an all-ungradeable set REFUSES** rather than averaging to a clean number (G).

**Proven able to refuse before this commit:** `python3 d9_grade.py --selftest` → **16/16 PASS**
(A healthy; B empty set refuses with count; C short set refuses with count; E unmoved design point
refuses; F empty FD vector refuses with count; G no plateau anywhere refuses; H disagreement →
GATE FAIL; I sign flips → GATE FAIL; J missing stage → NOT A RESULT; K completed-but-no-key →
BLOCKED; L malformed record refuses; M endpoint at a different design point refuses; N no
improvement → GATE FAIL; O incomplete stage → NOT A RESULT; P misplacement caught without touching
the derivative verdict; Q partial gradeable set below the N-of-M floor → NOT A RESULT).
**`rc = 1` and `rc = 2` are different failures and a harness exit code is not a solver exit code:**
a missing stage maps to **NOT A RESULT**, never to `BLOCKED`, so this lane's own harness cannot
record a capability as absent that was never reached.
`python3 scripts/check_grader_self_blindness.py d9_grade.py` → **clean on both probes**, which is
**NOT a proof of correctness** and is not offered as one.

## 5c. The idx16-class, NAMED IN ADVANCE, with its consequence written here

Three components of A5's `shapexUpper` have a measured history of anomalous FD behaviour and are
**named here, before compute, as candidates to be FD-ungradeable**:

| idx | the measured history |
|---|---|
| **8** | **205.52 %** adjoint-vs-FD on the **stock** image (2 sign flips row) |
| **16** | np=4 FD reads **−4.30296296** against np=1's **−5.00483123**, **16.3 % apart**, while neighbouring idx15 agrees across rank counts to **5 parts in 100,000** — the anomaly localises to the **np=4 FD path**, which is why D9 is np=1 throughout |
| **17** | **121.86 %** adjoint-vs-FD on the **stock** image |

**THE CONSEQUENCE IS REGISTERED HERE, NOT DISCOVERED AFTERWARDS.** A component whose FD signal
never rises above `NOISE_FACTOR ×` the measured floor at **any** registered step, or which has no
qualifying plateau window, is **FD-UNGRADEABLE BY CONSTRUCTION**. It is **excluded from the
aggregate WITH THE COUNT PRINTED** — never averaged in as a zero — and the endpoint verdict is
stated as an explicit **N-of-M verification**. The grader prints the ungradeable set **split into
those named above and those NOT named above**, because an ungradeable component this document did
not anticipate is a different and more interesting finding than one it did.

## 5d. Rule 4, and the clause that is NOT EXERCISED

**`0/U` is gzipped to `0/U.gz` mid-solve by DAFoam, so rule 4's age guard is unsatisfiable on this
family** — the file the guard dates against ceases to exist during the run. Recorded as
**`NOT EXERCISED`, with the reason**, and its evidentiary purpose discharged by a **stronger,
PRE-LAUNCH** assertion in `d9_stage_and_run.sh`: each arm directory is destroyed, re-copied from the
anchor tree, and the **answer file, any time directory and `0/U.gz` are asserted ABSENT while the
container is not yet running** (`COLDSTART_PROVED` in the ledger).

**Disclosed as a `VERIFICATION_CHARTER.md` §2d.1 matter, four conditions enumerated:** (i) **the
defect is in the rule's applicability, not in the result** — the field the guard needs is deleted by
the toolchain, not by this lane; (ii) **it is disclosed before compute, here, in the frozen
document**; (iii) **the substitute is strictly stronger** — an absence proved before the process
starts versus an ordering inferred after it ends; (iv) **no gate, threshold, cap or label moves**,
and the substitute can only *refuse*, never *pass*, a stage. The other clauses of rule 4 (`rc`,
`docker inspect` exit code and `OOMKilled`, artifact presence, finite values) **are** exercised and
recorded per stage in the ledger. **This is the same repair D13 made and the supervisor ruled
legitimate; it is applied here in advance rather than after a refusal.**

## 6. Cost — RE-PRICED AGAINST A MEASURED ANCHOR, not carried forward

**The curriculum's estimate for D9 is ~200–400 core-min. That figure is NOT adopted.** Two
curriculum items were found badly overpredicted today (D12's 1,000–3,000 core-min ran 4–23× high;
D13's was also over), and a cost carried forward unexamined is not a costing.

**The measured anchor** is `cases/dafoam/ladder-a/A5/reverify_patched_idwarp_np1/RESULTS.md` §7,
which records the **np=1 patched A5 `check_totals` arm at 372 s wall = 6.200 core-min**, together
with its log `/home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock_checktotals.log`: **55 primal
solves totalling 228 s of solver time — 4.15 s per primal on 4,800 cells** — leaving ≈146 s of
one-off startup (imports, mesh load, `dRdW` colouring) plus one adjoint.

| stage | count | basis | core-min |
|---|---|---|---|
| `cal` — `run_driver -maxit=1` | 1 | 146 s startup + 2 primals + 1 adjoint ≈ 170 s | 2.8 |
| `rep1`, `rep2` — `run_model` | 2 | ≈125 s each | 4.2 |
| `opt` — `run_driver -maxit=20` | 1 | 146 s + 20 × (2 × 4.15 s + ≈16 s adjoint) ≈ 636 s | 10.6 |
| `fd_*` — `check_totals` × 4 steps | 4 | the measured 6.20 core-min arm, once per step | 24.9 |
| | | **PREDICTED TOTAL** | **≈ 43** |

**The re-price is 4.7×–9.3× below the curriculum figure**, and it is stated as a **prediction from a
measured anchor**, not as a measurement.

- **REGISTERED CAP: 110.0 core-min**, 2.6× the prediction. The margin is for **contention, not for
  slack**: at this commit the box carries `loadavg ≈ 21` on **16 cores** with a 12 GiB sibling
  (`d8_opt`) live, so wall clocks will stretch and **a guard that trips on ordinary contention is a
  guard that gets raised.** **An overrun STOPS the run; it does not get a new budget** (rule 12).
  Per-stage timeouts: `cal` 900 s, `rep*` 600 s, `fd_*` 1200 s, `opt` by the frozen rule in G9-2.
- **The launcher ASSERTS that the enforced cap equals this literal** — it aborts unless
  `grep -qF "REGISTERED CAP: 110.0 core-min"` finds this line in this file. There is deliberately
  **no environment override** for the cap.
- **$0.0368 predicted / $0.0941 at the cap — DERIVED, NOT MEASURED.**
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED.` The box cannot read
  its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Contention is disclosed, never absorbed into the actual/predicted ratio** (rule 12;
  `COMPUTE_BUDGET_CHARTER.md` §6). **5–11 % measured contention is acceptable and disclosed, not a
  defect.**

## 7. np, placement

**`np = 1`.** Every container is pinned with an explicit `--cpuset-cpus`, `--cpus=1`,
`--memory=3g`. **`mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE HOST
TOPOLOGY**, so concurrent containers collide on one core while the box reports itself idle —
measured on this box today at **0.250 cores delivered against a 1.0-core quota** with the host
**61 % idle**. **G9-7 compares the affinity READ BACK from inside each process against the
registered cpuset**; placement is never inferred from the flag that was passed. **Correctness is
unaffected by contention; cost is**, so a mismatch is attributed to the **CONTENTION** channel and
**never absorbed into the actual/predicted ratio**.

## 8. Toolchain — by IMAGE ID, not by tag

| item | identity |
|---|---|
| image | **`dafoam-idwarp-rot:v1`**, ID **`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`** — the **PATCHED** digest |
| IDWarp | **patched** (rotation derivative) |
| DAFoam / OpenFOAM / PETSc | 5.0.0 / v2506 / 3.15.5, as recorded for this image |

**A version string is not an identity** (`DAFOAM_CHARTER.md` §6). The launcher resolves and logs the
image ID at run time and **aborts if it cannot**.

## 9. The two-row shipped/patched rule — and WHY THE PATCHED ROW IS THE ONE BOUGHT

`DAFOAM_CHARTER.md` §6: *two rows or it is not a verdict about DAFoam.*

| row | toolchain | bought? |
|---|---|---|
| **patched** | `dafoam-idwarp-rot:v1`, ID `sha256:2927768a…e30f6d35` | **YES** |
| **shipped** | stock `dafoam/opt-packages:latest`, ID `sha256:9d45679d…90f07fc` | **NOT BOUGHT** |

**Named, with the reason and the consequence.** A5's `OBJ.val wrt shapexUpper` is **`GATE FAIL` on
stock — 46.840 % aggregate with TWO SIGN FLIPS** (idx8 205.52 %, idx17 121.86 %) — and **`PASS` on
the patched image at 2.768 % with zero flips** (ledger rows 19–20). **An optimiser driven by the
stock gradient would be descending on a derivative already measured to be wrong, including in
sign.** Running that arm would buy a statement about a broken gradient's optimisation trajectory,
which is not the registered question. **Consequence, stated plainly: D9 CANNOT claim a
toolchain-independent result.** Whatever it returns is a statement about the patched image only,
and the stock row stays **NOT BOUGHT** with this reason attached.

## 10. What this item does NOT establish

- It establishes **nothing about the other five DV groups.** `shapeyUpper`, `shapezUpper`,
  `shapexLower`, `shapeyLower`, `shapezLower` are still **declared to pyGeo** (so the FFD object is
  byte-identical to the anchor) but are **NOT optimiser design variables**, because **none of their
  total derivatives has ever been FD-verified on this ladder.** `DAFOAM_CHARTER.md` §2 forbids a
  DAFoam gradient entering an optimisation without an FD table beside it. The five
  `add_design_var` lines are **left in place, commented**, so the departure reads as a diff rather
  than as an absence. **A single-DV-group optimum is not the case's optimum and is not reported as
  one.**
- It establishes **nothing at np > 1.** The np=4 FD path carries a measured anomaly at idx16 and is
  deliberately not used.
- It does **not** transfer to the stock image (§9).
- A plateau demonstrated **at the optimised endpoint** says nothing about a plateau at the
  **baseline**, and is not quoted as one.

## 11. Frozen instruments (md5 at this commit)

| file | md5 |
|---|---|
| `d9_run_script.py` | `af5f07bc1d3b4aca4fb427e089df0761` |
| `d9_grade.py` | `7704513424bf623b024814f4b86f8f31` |
| `d9_stage_and_run.sh` | `7bb4234f75fa53556303c0c2408bb5a7` |
| anchor `system/decomposeParDict` (NOT EXERCISED, §6 line 6) | `1dbd9ead3f40a29f483444dc5fa1288b` |
| anchor `FFD/UBendDuctFFDSym.xyz` | `97f2000d9edc309c5d39745b774234a6` |
| anchor `system/controlDict` | `ba7aaf0fac44450894d942b9c0751c63` |
| anchor `system/fvSolution` | `31819fad6ffaa0b719e73fe3a7e198d9` |
| anchor `system/fvSchemes` | `3af197134a104f624824a7c04ee25b17` |
| anchor `constant/polyMesh/owner.gz` | `62d5c7de318e5b4c7e20df6fc57f6519` |

The anchor tree is `/home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock/`, whose `runScript.py`
(md5 `06fb0ed4228d9927992a12a2fb68055c`) is **the exact configuration the published A5 numbers came
from**. `d9_run_script.py` is derived from it and **every departure is enumerated as D9-1…D9-8 in
its own docstring and nowhere else.**

**The grading path is fixed at this commit.** After the run, each file is hashed against its
committed blob and the equality recorded in `RESULTS.md`; a mismatch is a `NOT A RESULT`.
