# Ladder V — rungs V1, V3, V4, V5 executed 2026-08-08 (PASS 1 record-hardening)

Protocol: `LADDER_V_TRIPLE_VERIFICATION.md`. Submissions are PARKED (Katie,
2026-08-07): nothing here prepares, assembles, or sends anything anywhere.
Rungs V2/V7/V10 were executed earlier today and are not repeated
(`LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md`).

**The scoring-call distinction, stated up front because it is load-bearing.**
Rung V1 recomputes the round-5 scores offline, with the benchmark's own
scoring code installed into a scratchpad venv outside the repo. This is NOT a
scoring call against the lab's pre-registration ledger: the prediction set
re-scored is the identical, hash-frozen, already-scored set of the 6th
pre-registered call (2026-08-07, `07a7fe9e`); no new prediction exists, no
model decision hangs on the output, and the only thing the recomputation can
decide is PASS/FAIL of this verification rung. The ledger counts distinct
prediction sets scored; it stood at 6 before this rung and stands at 6 after
it. This is the same re-derivation the ladder itself assigns to Sanaa's own
hands at the send gate ("she re-runs V1 and V3").

Executor: the Closure/UQ family supervisor as PASS-1 owner (charter §3). Per
the ladder's no-self-grading rule: this executor produced none of the round-5
work verified here — not the QCR implementation, not the rule freeze, not the
solves, not the pre-registration, not the scoring call, and not the surfaces.
Verdicts are evidence-only; the chief reviews.

---

## RUNG V1 — score re-derivation in a clean environment: **PASS** (every digit identical; every byte identical)

### The clean environment (all under the session scratchpad, outside the repo)

- Fresh `python3 -m venv` (python 3.x system interpreter; numpy 2.5.1,
  scipy 1.18.0).
- Eval package installed from a **fresh clone** of
  `/home/ubuntu/closure-challenge-pkg` checked out at
  `1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162` (clean tree) — the same eval
  commit rounds 1–5 recorded. **Pinned package version installed and
  recorded: `closure-challenge 0.3.1`** (pip metadata; matches
  `pyproject.toml` at that commit).
- Benchmark: **fresh clone** checked out at the frozen commit
  `deb91557184af3cb95f5190494ec52d8f2c6a0d1` (clean tree).
- Ground truth used by the scorer is the package's own bundled
  `src/closure_challenge/data/ground_truth_test.npz` at the pinned commit.

### Recomputation (`evaluate_from_csv_by_case` + `score_from_csv` on `demo-output/website/closure_challenge_submission_round5/test/`)

Compared by `repr()` equality (i.e., every digit) against
`closure_challenge_round5_qcr.json`'s `round5_per_case_full` /
`round5_overall_full`:

| case | recomputed (fresh venv) | recorded (6th call, `07a7fe9e`) | verdict |
|---|---|---|---|
| alpha_15_13929_4048 | 0.05010529499681675 | 0.05010529499681675 | MATCH |
| alpha_15_13929_2024 | 0.10111218200472648 | 0.10111218200472648 | MATCH |
| alpha_05_4071_4048 | 0.04610779144551565 | 0.04610779144551565 | MATCH |
| alpha_05_4071_2024 | 0.07186293244687289 | 0.07186293244687289 | MATCH |
| AR_1_Ret_360 | 0.04547044480564218 | 0.04547044480564218 | MATCH |
| AR_3_Ret_360 | 0.039982156323801255 | 0.039982156323801255 | MATCH |
| AR_14_Ret_180 | 0.035338619029087186 | 0.035338619029087186 | MATCH |
| NASA_2DWMH | 0.0631981125812468 | 0.0631981125812468 | MATCH |
| **OVERALL** | **0.056647191704213645** | **0.056647191704213645** | **MATCH** |

The overall also equals the recomputed mean of the 8 per-case values exactly.
Not a digit moved.

### Byte-compare against what the solves produced

The three duct CSVs were never copied from anywhere — the round-5 forward
script wrote them straight from the converged fields. So the byte-compare is
done the strong way: **regenerate them from the raw solve artifacts** in the
fresh venv (Ofpp parse of `{case}_qcr/{t}/U` in
`/home/ubuntu/certonomous-runs/w3-qcr-rank1/`, shipped cell centres
`data/DUCT/{case}/constant/C` from the deb91557 clone, shipped
`data/evaluation_points/{case}_points.csv` coordinates, scipy
`NearestNDInterpolator`, `np.savetxt fmt=%.10g` — no scoring-package function
imported) and compare bytes:

| file | check | verdict |
|---|---|---|
| AR_1_Ret_360.csv | regenerated from `395/U` | **BYTE-IDENTICAL**; sha256 `bb8d61fb…` matches pre-reg §3 and the call record |
| AR_3_Ret_360.csv | regenerated from `1956/U` | **BYTE-IDENTICAL**; sha256 `c567ff25…` matches |
| AR_14_Ret_180.csv | regenerated from `8947/U` | **BYTE-IDENTICAL**; sha256 `286610c0…` matches |
| 5 non-duct CSVs | vs `closure_challenge_submission_round5/test/` ↔ `closure_challenge_submission_round4/test/` | all 5 **BYTE-IDENTICAL** to the round-4 files they claim to be |
| all 8 | `sha256sum` on disk vs `R5_PREREGISTRATION.md` §3 and `closure_challenge_round5_qcr.json` | all 8 match (re-confirms V7) |

---

## RUNG V3 — leakage assertions executed, not read: **PASS**

### (a) the assertion block, run live

`sdk/scripts/closure_baseline_error_gate.py` lines **84–86** (module level)
were executed three ways in one process (lab venv, scratchpad driver
`v3_live.py`): (1) by importing the module, which runs the block; (2) by
re-executing the three asserts verbatim — `len(_PH_TRAIN)==21 and
len(_PH_VAL)==4`, empty `train∩val`, empty `(train∪val)∩test` — all PASS;
(3) by a **negative control**: injecting a test case into the train set makes
the assert fire, proving the guard is live, not decorative.

The driver armed the family-standard raising-stub guard before any case was
touched (all nine scoring/truth entry points stubbed in `closure_challenge`,
`dataset_utils`, and `eval`; `cc.score()` proven to raise) and it stayed armed
to exit. Ground truth was read only for the 21 PH training cases — the gate's
legitimate regression targets. No scoring entry point was reachable.

### (b) §4.1's line citations, re-cited against current code

§4.1 lives in `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` (lines 262–286; Katie's
send package — re-cited here, not edited there). Its numbers were cited
against `apply_closure_ph_gate.py` @ `f5c98f96`; the 2026-07-30 docstring
correction (`fe121af2`) shifted the body by +13 lines. Verified against
`f5c98f96` that the old citations were correct then, and against HEAD that
every claim still holds now:

| §4.1 claim | old line(s) | current line(s) | still holds? |
|---|---|---|---|
| `_load_ground_truth_U` inside `for case in gate._PH_TRAIN` | 115 | **128** (loop at 126) | YES — train-only loop |
| test-case loop calls `ph._load_rans_fields` only, `# no U_LES read` | 165–167 | **178–180** (loop at 178) | YES — features only |
| `_load_ground_truth_U` inside `for c in ph._PH_TRAIN` | 215 | **228** (loop at 225) | YES — train-only loop |
| gate split asserts in `closure_baseline_error_gate.py` | (quoted, unnumbered) | **84–86** | YES — executed live above |

Completeness note the old citation did not need: current lines 262–264 also
read duct ground truth (`ext._load_duct_ground_truth_U`) — inside
`for case in ext._DUCT_TRAIN`, training ducts only. No other ground-truth
read exists in the file.

### (c) the four test-case gate decisions, reproduced from train-only inputs

The full STAGE-1/STAGE-2 pipeline was re-run under the armed guard: features
and baseline targets from the 21 train cases only → screening → top-3
(`p90_I4_W2S`, `frac_backflow`, `p90_I3_S3` — matches record) → RidgeCV
alpha **0.7499** (matches) → train-LOO median threshold **0.1263** (matches)
→ frozen model evaluated on the 4 PH test cases' RANS-only features:

| case | reproduced | recorded (round-3 JSON) | verdict |
|---|---|---|---|
| alpha_15_13929_4048 | 0.1503 → APPLY | 0.1503 → APPLY | MATCH |
| alpha_15_13929_2024 | 0.1525 → APPLY | 0.1525 → APPLY | MATCH |
| alpha_05_4071_4048 | 0.0420 → DECLINE | 0.0420 → DECLINE | MATCH |
| alpha_05_4071_2024 | 0.0034 → DECLINE | 0.0034 → DECLINE | MATCH |

All four decisions reproduce from train-only inputs, to the recorded 4 dp,
with no test truth readable in the process.

---

## RUNG V4 — AR_1_Ret_360 traced end-to-end by hand: **PASS** (one unbroken chain, every link byte-verified)

Run dir: `/home/ubuntu/certonomous-runs/w3-qcr-rank1/AR_1_Ret_360_qcr/`.

1. **Config.** `constant/turbulenceProperties`: `RASModel kOmegaSSTQCR`,
   no coefficient overrides. `system/controlDict` differs from the shipped
   benchmark case in exactly four ways, all read in the diff:
   `libs (libkOmegaSSTQCRTurbulenceModels.so)` instead of the organisers'
   frozen-model lib; `startFrom startTime; startTime 0` (fresh solve);
   `endTime 3000` annotated "frozen cap, RULE_FREEZE.md §5" (the cap frozen
   at `0bade54a` before any solve); two `#includeFunc` probe lines commented
   out. `caseDef`, `system/fvSchemes`, `system/fvSolution`,
   `system/fvOptions` (the `#calc "$Re_b*$nu/$h"` bulk-velocity forcing —
   the origin of the run dir's `dynamicCode/`, emitting the constant 85.395
   from shipped physical parameters): **all byte-identical to the shipped**
   `closure-challenge-benchmark/data/DUCT/AR_1_Ret_360/`.
2. **Mesh.** All five `constant/polyMesh` files (`points`, `faces`, `owner`,
   `neighbour`, `boundary`) **byte-identical** to the benchmark's shipped
   mesh. 3025 cells. Initial fields `0/U`, `0/k`, `0/omega`, `0/p`
   byte-identical to the shipped `0/`. No `*_LES` file anywhere in the case.
3. **Solver log.** `log.simpleFoam`: OpenFOAM v2606 `simpleFoam`, host
   ip-172-31-43-247, PID 3548, started 2026-08-07 20:01:13; "Selecting RAS
   turbulence model kOmegaSSTQCR"; `printCoeffs` shows the full coefficient
   dict ending `Ccr1 0.3`; 395 real `Time =` iterations with per-iteration
   residuals; terminates "**SIMPLE solution converged in 395 iterations**"
   under `fvSolution`'s `residualControl { k 5e-6; omega 1e-10; }` — final
   iteration initial residuals k 4.9e-6, omega 6.2e-11, both under their
   thresholds; U residuals ~1e-6 at that point. `ledger.txt`:
   `AR_1_Ret_360_qcr rc=0 wall_s=9`. Launched by `run_arm.sh` (in the run
   tree): plain `simpleFoam` under the OpenFOAM 2606 bashrc.
4. **Field.** `395/U`: `nonuniform List<vector>`, **3025** entries — one per
   mesh cell, parsed cleanly by Ofpp.
5. **Interpolation.** `NearestNDInterpolator(C, U)` with shipped
   `constant/C` (3025 centres) onto shipped
   `data/evaluation_points/AR_1_Ret_360_points.csv` (1000×3, coordinates
   only), written `np.savetxt(..., fmt="%.10g")`. Re-executed in the V1
   clean venv: output **byte-identical** to the committed
   `closure_challenge_submission_round5/test/AR_1_Ret_360.csv`.
6. **CSV shape.** 1000 rows × 3 comma-separated columns, headerless, all
   finite; sha256 `bb8d61fbbfd99f5099628cedf7b76a203558daa87e3235006b0c8527ea703e7e`
   = the pre-registration §3 value = the call record's value.
7. **Scored number.** That byte-exact file scores
   **0.04547044480564218** under the pinned harness (V1, fresh venv) — the
   recorded AR_1 round-5 number, digit for digit, feeding the recorded
   overall 0.056647191704213645.

Config → mesh → solve → field → interpolation → CSV → score: no link is
asserted from prose; every link above was re-checked on the artifacts.

---

## RUNG V5 — QCR provenance: **PASS** (in-house history; structurally nothing to fit; citations verified, five records given dated citation notes)

### In-house history

`git log --follow` on `sdk/openfoam/qcr/kOmegaSSTQCR/kOmegaSSTQCR.C` and
`.H`: authored in-repo at **`303247bb`, 2026-08-05T17:33:27Z** ("The
quadratic term the linear model cannot express…"), the exact
`library_commit` the round-5 record claims, two days before the test solves
(2026-08-07) and 8 minutes before the rule freeze (`0bade54a`,
17:41:06Z). The built library
`/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/lib/libkOmegaSSTQCRTurbulenceModels.so`
hashes to sha256
`b741839596bc8624789652fdc69b476594dc24419edd21faedac004e2c1cc808`, matching
the record's `library_sha256`. `kOmegaSSTQCR` does not exist in stock
OpenFOAM v2606 (`/usr/lib/openfoam/openfoam2606/src` contains no QCR source
and no reference to the name): the implementation is the lab's, derived — as
its header states — from the rank-2 entry's published Eq. (1) and NASA TMR's
SA-QCR2000 form.

### The "untrained" claim, proven structurally

Everything in the duct path that could in principle carry a fitted number,
enumerated, with what it actually contains:

| path element | fittable content | finding |
|---|---|---|
| `kOmegaSSTQCR.C/.H` | the ONE new coefficient, `Ccr1_`, code default **0.3** (`getOrAddToDict`), declared "(Spalart 2000, untrained)"; k/omega transport inherited unchanged from `kOmegaSST` | 0.3 is Spalart (2000)'s published constant, untouched |
| `constant/turbulenceProperties` (all 4 arms) | could override any coefficient | overrides nothing; `printCoeffs` in all four logs shows stock SST constants + `Ccr1 0.3` |
| mesh, `0/` fields, `fvSchemes`, `fvSolution`, `fvOptions`, `caseDef` | could encode tuned inputs | all byte-identical to the benchmark's shipped files (V4) |
| `controlDict` | could encode a tuned stopping rule | only the lib swap, fresh start, the `RULE_FREEZE.md` §5 frozen cap, and commented probes |
| `dynamicCode/` in the solve dirs | on-the-fly compiled code | the benchmark's own `#calc` bulk-velocity constant (85.395) from shipped `caseDef` physics; same machinery in the organisers' own shipped case dirs |
| interpolation to the 1000 points | could smuggle a learned map | parameterless nearest-neighbour |
| run tree contents | training data / ML artifacts / test truth | none: no pickles, no model files; the only `*_LES` files sit under the two **AR_7** validation arms — AR_7 is the benchmark's designated validation duct, read for the pre-registered V1/V2 gate metrics; the three **test** duct dirs contain no truth of any kind |

There is nothing in the path with a free parameter to fit, except one
constant fixed in 2000 in the open literature. The claim is structural, as
the ladder demands.

### Spalart (2000) cited wherever QCR is named

Swept: `demo-output/website/campaign/*.md`, `closure.html`, the `.tex`, plus
the round-5 JSONs. Already citing correctly (untouched): `R5_RULE_FREEZE.md`,
`W3_QCR_DUCT_FALSIFIER.md`, `W2_WU_ZHANG_DESTRUCTION_FIML_READING.md`,
`DPW8_V2_joukowski.md`, `LADDER_V_TRIPLE_VERIFICATION.md`; `closure.html`
(three places, incl. "published by Spalart in 2000 — one constant, 0.3");
the `.tex` (prose at 81/346/2070 plus the full bibliography entry at 2233);
`closure_challenge_round5_qcr.json` (`model.provenance` carries the full
journal reference).

**Missing and fixed** — five campaign records that present QCR work but never
named its source; each received an identical **dated citation note**
(2026-08-08, marked additive-only, appended below the "nothing below this
line" frontier where one exists, no frozen clause touched):

- `campaign/R5_PREREGISTRATION.md`
- `campaign/F6b_QCR_PREREGISTRATION.md`
- `campaign/F6b_QCR_RESULTS.md`
- `campaign/W1_HUMP_CHALLENGE_PREREGISTRATION.md`
- `campaign/W1_HUMP_CHALLENGE_RESULTS.md`

**Reported, not edited:** `LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` names
"untrained QCR2000" without the citation — it is the signed report of
another verification agent, left to its owner (this report carries the full
citation for both). `CHALLENGE_SLATE_2026-08.md` and the `W1_HUMP_A1_*` pair
mention QCR only in passing with explicit pointers to records that now carry
the citation. The `.tex` and `PRODUCT_LIST` were not touched per the rung's
scope.

---

## What changed during this verification (consolidated, per V13)

| file | change |
|---|---|
| `campaign/R5_PREREGISTRATION.md` | dated Spalart (2000) citation note appended below the frozen-frontier line |
| `campaign/F6b_QCR_PREREGISTRATION.md` | same dated citation note |
| `campaign/F6b_QCR_RESULTS.md` | same dated citation note |
| `campaign/W1_HUMP_CHALLENGE_PREREGISTRATION.md` | same dated citation note |
| `campaign/W1_HUMP_CHALLENGE_RESULTS.md` | same dated citation note |
| `campaign/LADDER_V_RUNGS_V1_V3_V4_V5_2026-08-08.md` | this report (new) |

Not touched, deliberately: the submission CSVs and every MANIFEST/scoring
JSON (immutable), `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` (Katie's send
package — §4.1 re-cited here instead), the `.tex` (its Opus writer's),
`PRODUCT_LIST` (chief's), the sibling V2/V7/V10 report (its owner's), both
frozen checkouts (`closure-challenge-benchmark`, `closure-challenge-pkg` —
all V1 work ran on fresh clones in the scratchpad), and the scorer in the
lab's own environment (the offline recomputation ran only in the scratchpad
venv, and the ledger stands at 6, untouched).

## Verdicts

- **V1: PASS** — pinned `closure-challenge 0.3.1` @ `1c4e22c8` in a fresh
  venv, benchmark clone @ `deb91557`, all 8 per-case scores and the overall
  0.056647191704213645 reproduced to the last digit; duct CSVs regenerated
  from the raw solve fields byte-identical; the 5 unchanged CSVs
  byte-identical to round 4. Offline re-derivation of published numbers, not
  a ledger scoring call.
- **V3: PASS** — the assertion block executed live (with a firing negative
  control), §4.1's citations re-anchored (115→128, 165–167→178–180,
  215→228, asserts at 84–86) with every claim still true, and all four gate
  decisions reproduced from train-only inputs under an armed, proven
  scoring-stub guard.
- **V4: PASS** — AR_1_Ret_360 traced config → mesh → 395-iteration converged
  solve → `395/U` → nearest-neighbour interpolation → 1000×3 CSV →
  0.04547044480564218, with byte-level verification at every link.
- **V5: PASS** — in-house single-commit history at `303247bb` matching the
  recorded library hash; structurally nothing fittable in the duct path
  (`Ccr1 = 0.3`, Spalart's published constant, the only new coefficient);
  citations verified across the surfaces, five campaign records given dated
  citation notes, gaps in others' files reported not edited.

Signed: **Closure/UQ family supervisor, as PASS-1 owner** (charter §3;
ladder rule "no agent may verify work it produced" satisfied — none of the
verified round-5 artifacts were produced by this executor). Rungs
V6/V8/V9/V11/V12 remain bound to a concrete submission package and wait for
unpark; V13 close-out collects this report and its siblings.
