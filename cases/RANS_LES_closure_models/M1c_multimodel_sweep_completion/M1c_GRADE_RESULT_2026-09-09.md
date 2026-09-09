# M1-C MULTI-MODEL SWEEP COMPLETION RE-RUN — GRADE RESULT, 2026-09-09

## VERDICT: GATE FAIL (now governed by G2 — a harness identity check, NOT completion). G0 PASS + G1 PASS: the full 78-arm sweep COMPLETES and the arms are correctly applied.

The 6 cap-bound arms that made M1d's GATE FAIL **completion-dominated** (G0) have
been re-run to strict rule-4 completion. Grading the full merged 78-arm root with
the FROZEN, pinned `grade_m1d.py` (instrument sha256 `a1ee1905…628790`, == the
A.1 pin; planted-zero control LIVE, `passed=True`, read-back
0.0012339999999966267; birth_verified True) yields:

| gate | verdict | evidence |
|---|---|---|
| **C1** planted zero | **PASS** | reader is live (sees the 1.234e-3 plant); L-508 repair inherited |
| **G0** completion + age guard | **PASS** | **n_complete = 78/78, incomplete = []** — the 6 re-run arms all COMPLETE (state=COMPLETE, last_time=20000, all rule-4 clauses True) |
| **G1** arm application | **PASS** | n_bad = 0 — dict model and the solver's own `Selecting RAS turbulence model` line agree on every row |
| **G2** null-arm identity | **GATE FAIL** | rel-L2(U) null vs shipped reference: all_rows_max **0.02419 > ceiling 0.01** (32/39 meeting, band 1e-3); the duct cases. Gate's own label: *"a harness check, NOT a precision claim"* |
| **G3** arm separation (SPREAD ONLY) | **GATE REACHED** | 39/39 separate (>1e-2), max spread 0.10143 — a sensitivity spread, not an accuracy verdict |
| **G4** cap-bound census | **GATE REACHED** | 0 cap-bound (≤ 8) |

`grade_m1d.py` rc = 1 reflects the **G2 GATE FAIL**. STANDING RULE 5 DOES NOT APPLY
(one shipped mesh per case, no grid triple → no GCI, no Roache triple; stated
in-gate). nonfinite_census: 0 rows nonfinite of 9,320,000 solves. fatal_census:
n_fatal_narrow = 0 (the 78 trapfpe banners are the benign `kInf 0; omegaInf 0;`
BC-token tokens, not real fatals). Primary artifact: `/home/ubuntu/closure-data/m1c_completion/gate_m1c.json`.

## What changed from M1d, and what it means

- **M1d's GATE FAIL was COMPLETION-DOMINATED** (G0 failing on 6 incomplete arms;
  G2/G3 dominated by the missing rows). **M1-C completes the 6 arms → G0 PASSES**,
  and the sweep is now fully graded.
- **The remaining GATE FAIL is G2** — the null-arm re-solve's `U` differs from the
  *shipped baseline SST RANS reference field* by max 0.02419 (> the 0.01 ceiling)
  on the duct cases. This is the SAME 0.024 signal M1d saw; it is **NOT a
  model-accuracy / precision claim** — G2 is a gross-harness-error detector (its
  own label), comparing a null re-solve against a shipped reference of the same
  model class. The closure line's model-error product is **M2** (error-vs-DNS-truth),
  NOT G2.
- **The wins to cite are G0 PASS (78/78 complete) and G1 PASS (arms correctly
  applied)** — the full multi-model sweep is now a completed, graded result.

## §2bc exhaustion-evidence classification of THIS verdict

Complete run (G0 PASS) failing a gate (G2) → checklist Path B. G2 is a HARNESS
identity check, not the closure model-accuracy product, so its GATE FAIL is **NOT
an E2 closure model-accuracy miss**. Numerics are exhausted-not-implicated (N-X4:
the duct p-initial-residual plateau is a floating-reference normalization
artifact; the flows converge — nonfinite census clean, G0/G1 pass, min_k/min_omega
at machine-small). The 0.024 rests on a shipped reference whose upstream
provenance carries the standing **rule-15 gap** (absent duct-DNS / closure-challenge
papers, on Sanaa's desk). **Classification: E2-EDGE — FLAGGED, NOT LOCKED**, for
three independent reasons: (a) the E1/E2 boundary is pending Sanaa's confirm
(§2bc.3 ⚠); (b) G2 is by its own label a harness check, not a precision claim,
so it is not the closure line's terminal model-accuracy finding (that is M2); and
(c) the rule-15 provenance gap blocks reading 0.024 as a model signal at all. No
`exhaustion_evidence` machine-readable block is locked this cycle.

## Cost (rule 12)

M1-C incremental (the 6 re-run arms, MEASURED from `gate_m1c.json` per-row
core_min): AR_1 3.3167 + AR_7 24.7833 + AR_14 60.1833 + PH_Breuer 62.5 (kOmega) +
AR_1 3.6167 + PH_Breuer 63.45 (kOmegaSST_null) = **217.85 core-min** = 3.631
core-h × $0.0513/core-h = **$0.186 DERIVED** (owner-stated rate, not measured — the
box cannot read its own billing). **Under the A.3 MAX cap of 379.567 core-min
(57.4%); no overrun.** (The gate's `total_core_min_measured` = 866.18 is the merged
78-arm total, mostly the inherited 72 M1 rows — not the M1-C spend.) Estimate-vs-
actual row filed in `docs/COST_CALIBRATION.md`.

## Provenance

- Prereg FROZEN `84c163bf` (SUPERVISOR FREEZE STAMP; grading path = frozen
  `grade_m1d.py`, pin `a1ee1905…628790`; pre-first-compute staging-path amendment
  `e738ed43`, L-512).
- Rows dropped live `861ba1c3` (PH_Breuer-first; prereg_commit=84c163bf,
  memory_floor_gb=1.0, `--require-binding` accepted); bookkeeping correction of one
  daemon-race 0-byte row blob `cbf29fe1` (L-342, no physics impact — verified: 1
  LAUNCH_LOG line per arm, no double-launch).
- §2ba dual mechanism: detached autograder (pid 746064, re-hashed grade_m1d.py vs
  pin, refuses on mismatch, rc inside wrapper) + live monitor (pid 746065); daemon
  pid 1887 admitted all 6 under the 14.4-core ceiling.
- Supersedes M1d (`M1d_GRADE_RESULT_2026-09-09.md`) as the completed successor of
  the M1 arc. SUBMISSIONS PARKED.
