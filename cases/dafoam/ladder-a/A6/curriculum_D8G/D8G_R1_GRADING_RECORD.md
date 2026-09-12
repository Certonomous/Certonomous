# D8G R1 — GRADING RECORD. **NOT A RESULT** (comparator refusal) — with a real, bounded finding beside it.

Graded 2026-09-12 by a `lab-lane` of the dafoam team against
`cases/dafoam/ladder-a/A6/curriculum_D8G/PREREGISTRATION.md` as amended by
**ADDENDUM 7 (`c852c6319`)** and **ADDENDUM 8 (`7e0d0d747`)**.
SUBMISSIONS PARKED (CLAUDE.md rule 7).

Run root: `/home/ubuntu/certonomous-runs/CURRICULUM-D8G-R1-a6-grid-triple`
Arm: `L1-P-R1`, log `L1-P-R1_20260912T044934Z.log`

---

## 1. VERDICT — AND WHY IT IS NOT THE HEADLINE EITHER WAY

**`NOT A RESULT`.**

`d8g_grade.py --root /home/ubuntu/certonomous-runs/CURRICULUM-D8G-R1-a6-grid-triple`,
**unchanged**, refused:

```
REFUSAL: {"REFUSE": "ledger", "detail": {
  "note": "PRESENT-BUT-GARBAGE row: refused, never skipped",
  "row_unparseable": "ARM=L1-P-R1 ROW=D8G-R1 rc=0 ... "}} -> NOT A RESULT
```

**The refusal is correct and the comparator behaved exactly as designed.** Two reasons,
and the first is the one that matters:

1. **The arm id `L1-P-R1` is not a registered arm.** `d8g_grade.py:212` fixes
   `ARMS_REQUIRED = ["L1-P","L2-P","L3-P","A2-P","F2-P","L1-S","L2-S","L3-S","A2-S","F2-S"]`.
   The R1 repair arm ran under an id the frozen comparator has never heard of, so its
   ledger row parses to nothing — and this comparator **refuses a present-but-garbage row
   rather than skipping it**, which is the right behaviour and the reason the refusal is
   trustworthy.
2. **One arm of ten has run.** Even under a recognised id, `grade()` walks all ten arms
   and would refuse on the nine absent ones.

**ADDENDUM 7 does register the arm by that name** — `PREREGISTRATION.md:1752` ("Applied
to `L1-P-R1`") and `:1808` — while stating at `:1341`, `:1397`, `:1424`, `:1531` and
`:1596` that `d8g_grade.py` `12688063e20cbb6fa79cf08d0996d4e1` **is NOT TOUCHED**. Those
two facts are consistent as written but leave a gap: **a repair arm was registered under
an id the untouched instrument cannot grade.** That is a registration/instrument
mismatch, it is disclosed here rather than worked around, and **closing it is the
supervisor's call, not this lane's** — the frozen comparator has not been edited
(CLAUDE.md rule 6).

### 1.1 What `NOT A RESULT` does and does not mean here

It means **no graded verdict exists for D8G R1**. It does **not** mean the run failed, and
it does not erase what the log measures. §2 below is measurement, clearly labelled as
measurement, and it is not a verdict and must never be quoted as one.

---

## 2. THE MEASUREMENT — THE FIX TRANSFERRED. THAT IS THE FINDING.

Read directly from `L1-P-R1_20260912T044934Z.log` and `L1-P-R1/d8g_P.json`.

| quantity | pre-fix arm | **R1 (post-fix)** |
|---|---|---|
| log | `CURRICULUM-D8G-a6-grid-triple/L1-P_20260911T234236Z_2435242.log` | `L1-P-R1_20260912T044934Z.log` |
| last `nuTilda initRes` | **4.073982e-04** (rising: 3.924e-04 → 3.991e-04 → 4.074e-04) | **7.873598471886472e-05** |
| against the 1.0e-04 accept floor | **4.07×** — plateaued above it | **0.787× — CLEARED** |
| `Primal solution failed!` | **17 occurrences** | **0** |
| `p` sub-iterations per outer step | **1** (the LOOSE rule) | **13** (the TIGHT rule) |
| last `Time` | 1000 | 2000 |
| `End` line | — | present |

`d8g_P.json` was written: **CD = 0.04380537021659878**, **CL = 0.34000584724055816**,
cells 5,568 (= registered L1), `nprocs` 4, `endTime` 2000, `printInterval` 10,
`points_md5 8a7448714d003932b500eca6fa496709`, `libidwarp.so` md5
`85f59e87253e0a71a813f64ca6e4c425`. Ledger: `rc=0 inspect(exit,oom)=[0|false]
wall_s=3293 ranks=4 core_min=219.533`.

**THE READING.** ADDENDUM 7 registered the transfer of the D6RF10-R3 package to the CRM
wing-body as **UNTESTED**, in those words, because **A6 is not the A2 MACH wing**. It
cleared. **So the D6RF10-R3 package is not case-specific.** The mechanism is visible and
measured on both sides, not inferred: the package swaps the loose inner-solve rule
(`relTol 0.1`, `tolerance 0`, `nSweeps 1`) for the tight one (`GAMG relTol 0.001 /
tolerance 1e-12 / minIter 5`, `smoothSolver relTol 0.001 / tolerance 1e-09 / nSweeps 3`),
and the pressure equation goes from **1 inner solve per outer step to 13** — at both the
first and the last outer step, so it is the rule and not a transient.

### 2.1 THE BOUNDS, AND THEY TRAVEL WITH THE FINDING

* **This is not a verdict about DAFoam.** It is a verdict about **this patched build's
  primal**. D8G is **PATCHED ROW ONLY**: the `-S` (shipped) row has not run, so there is
  no controlled comparison against stock.
* **The gradient is unverified.** No `A` arm and no `F` arm has run. Nothing here says
  anything about the adjoint.
* **One level, and it is the coarsest.** L1 is **5,568 cells** of a registered
  5,568 / 44,544 / 356,352 triple. No grid triple, no observed order, no GCI.
* **The wall treatment is coarse.** `yPlus min 48.3, max 563.3, mean 141.7` — squarely
  wall-function territory, far from a resolved boundary layer.
* **`NOT A RESULT` is the verdict.** The transfer finding is a **measurement pending the
  item's comparator**, and it stays labelled that way until nine more arms run under ids
  the frozen instrument can parse.

---

## 3. FROZEN-PATH PROVENANCE — CHECKED, NOT ASSUMED

| artifact | md5 on disk | committed blob | agree |
|---|---|---|---|
| `d8g_grade.py` | `12688063e20cbb6fa79cf08d0996d4e1` | `7e0d0d747:` → same; `HEAD:` → same | **yes** |
| `PREREGISTRATION.md` | `8679f5f676bfb06f2e428372969eb24f` | `7e0d0d747:` → same | **yes** |

The md5 registered in the pre-registration (`:1215`) is the md5 that ran. Working tree is
clean for both files.

**The comparator was shown to be alive before it was believed** (CLAUDE.md rule 3, in the
spirit of the planted zero): `d8g_grade.py --selftest` → **`D8G GRADER SELFTEST PASS
50/50`**, `failures=0`, counted against the frozen `EXPECTED_UNITS`. Among the 50 are the
units that would have caught this row had it been a corpse — U44 (a primal truncated at
iteration 490 of 1000 with a perfectly flat tail and an artefact still claiming endTime
1000), U46 (endTime reached with no `End` line), U48 (field set absent from any rank),
U49 (fields present but not newer than the arm's age datum), U30 (artefact older than the
age datum). **A refusal from an instrument that passes 50/50 is evidence; one from an
untested instrument is not.**

---

## 4. STRICT COMPLETION (rule 4), READ INDEPENDENTLY OF THE REFUSAL

The comparator refused at the ledger before reaching its completion gate, so these were
read directly. They are **reported, not graded** — they are not a substitute for the
gate:

| clause | measured |
|---|---|
| `rc = 0` | yes, ledger + `STATUS.L1-P-R1`; `inspect(exit,oom)=[0|false]` |
| `End` line | present |
| last time == `endTime` | `Time = 2000`, `controlDict endTime 2000` (from `d8g_P.json`) |
| fields at `endTime` | four `processor*` trees written 05:44, terminal artefact `d8g_P.json` written |
| age datum | `.d8g_age_datum` present (04:49); artefacts at 05:44 postdate it |

---

## 5. COST — RULE 12, ESTIMATE VERSUS ACTUAL

Registered estimate: **~35 core-min**, `PREREGISTRATION.md:88` (ADDENDUM 7) — "4 ranks;
prior arm measured 16.1 core-min gross at `endTime 1000` on the loose rule, of which
~16.5 core-min is fixed per-run overhead". Note the basis's first word is **"Estimate"**,
which `scripts/cost_calibration.py` records as the class that has produced every over-run
above 1.05× on this ledger.

| basis | figure | ratio |
|---|---|---|
| predicted | 35.000 core-min | 1.000× |
| actual, **gross** (ledger `core_min`, `wall_s 3293 × 4`) | **219.533 core-min** | **6.272×** |
| actual, **cleaned** (`ExecutionTime 1384.92 s × 4`) | **92.328 core-min** | **2.638×** |

**Attribution — misprediction and contention named separately, neither divided into the
other** (`COMPUTE_BUDGET_CHARTER.md` §6):

* **MISPREDICTION 2.638×, and it has a named mechanical cause.** The ~35 estimate
  doubled a prior arm's 16.1 core-min for 2× the iterations (`endTime` 1000 → 2000) but
  **did not price the tighter inner-solve rule — which is the very thing the arm was
  testing.** Measured: **13 pressure sub-iterations per outer step under the tight rule
  against 1 under the loose rule**, at both the first and last outer step. A ~13× increase
  in linear-solve work per outer step, entirely unpriced. **This is misprediction, not
  contention, and it is not laundered into contention.**
* **CONTENTION 2.378×** — `wall_s / ExecutionTime = 3293 / 1384.92`. The box carried
  three other live solvers (D6R2, D6RF11, A3GC L2) through this arm's window.
* 2.638 × 2.378 = **6.274**, against the measured gross ratio **6.272** — the split
  closes to 0.03 %.
* **WASTE: separately named as ZERO.** No stall (`wall_s 3293` is under the 3600 s stall
  threshold), no re-run of this arm, no discarded output.

**CAP.** `CAPS["L1-P"] = 46.977` core-min (3× the 15.659 point estimate) and
`CAP_IS_A_STOP = False` (§6.4, suspended for this 3D item). Gross **219.533** is
**4.67×** that cap: **recorded and reported, not a stop** — consistent with
`d8g_grade.py` selftest unit U39, which exists precisely so an over-cap arm is reported
with its ratio and the item still grades.

**Dollars: $0.188 at $0.0513/core-h on the gross basis — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 6. WHAT I COULD NOT VERIFY

* **No graded number for R1 exists and none is asserted.** Every figure in §2 is a log or
  artefact reading, not a comparator output.
* **The `-S` shipped row has not run**, so "the patch fixed it" is not a controlled
  claim — only "the patched build's primal cleared its floor where a prior patched arm on
  the loose rule did not".
* **I did not run `d8g_grade.py` against a synthesised ledger row** under a recognised
  arm id to see what the rest of the gates would say. That would mean feeding the frozen
  comparator a row that does not describe a registered arm, and I am not doing that on my
  own authority.
* **`PREDICTED_CORE_MIN["L1-P"] = 15.659`** in the comparator against **~35 core-min** in
  ADDENDUM 7 for this repair arm. Both are on record; which one G10 would have used for
  R1 is undetermined because R1 never reached G10. The calibration above uses **35**, the
  figure registered for *this* arm. Against 15.659 the gross ratio would be 14.02×.
