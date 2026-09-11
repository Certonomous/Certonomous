# K2f throwaway-case compute cost — PARKED ROW

**NOT a row in `docs/COST_CALIBRATION.md`.** That ledger is refusing lab-wide at
exit 7 and its repair sits with the verification team; this row is parked beside
the rung and is appended to the ledger when the ledger can accept it. Rule 12's
estimate-versus-actual comparison is done here in full, not deferred.

**Scope:** the §3.1 `A-INPUT` and §7 `A-DRIVE` pre-freeze obligations only.
**This is NOT the K2f ladder.** No graded level was built, no graded level was
launched, and nothing here is a registered measurement of the rung.

---

## PREDICTED — written 2026-09-11T16:20Z, BEFORE any solver started

| item | figure |
|---|---|
| throwaway mesh | `K2f_L1` divisions, **58,368 cells**, built into a TEMP root, never into the run tree |
| ranks | **1 (serial)** — box load average 5.83 on 16 vCPU at prediction time; T4e (pid 1233987) and cfd's SUBOFF mesher are running and are NOT ours |
| iterations | **20** (`endTime 20`, the registered `A-INPUT` size) |
| solver, contention-free | 58,368 x 20 / 187,598 cell-iter/core-s = **6.22 core-s** |
| mesh generation (blockMesh + topoSet + checkMesh -allGeometry -allTopology) | **25 core-s**, from K2d's L1 build |
| contention factor assumed | **1.3** |
| POINT per case | (6.22 + 25) x 1.3 = **40.6 core-s = 0.68 core-min** |
| cases | **3** — `A-INPUT` positive arm, `A-INPUT` negative arm (`functions` removed), `A-DRIVE` tree |
| **PREDICTED POINT** | **2.03 core-min** |
| **CAP** | **6.0 core-min** (3x point). **An overrun stops the run; it does not get a new budget.** |
| **DERIVED dollars at cap** | 6.0 core-min = 0.100 core-h x $0.0513/core-h = **$0.0051** — **DERIVED, NEVER MEASURED**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

**Rate basis:** K2d's measured L1 rate, 187,598 cell-iter/core-s
(`K2f_PREREGISTRATION.md` §10.1). Measured at 4 ranks; applied here at 1 rank,
which is a **per-core** rate and therefore the right unit, but the 4->1
extrapolation is an assumption and is named as one.

---

## ACTUAL — filled after the arms were driven

*(see the ACTUAL block appended below)*

### ACTUAL — measured 2026-09-11, from the driver's own wall clock

| item | predicted | **actual** | ratio |
|---|---:|---:|---:|
| mesh generation (blockMesh + topoSet + checkMesh, 58,368 cells) | 25.0 core-s | **2.0 core-s** | **0.08** |
| solver, per arm (20 iterations, 1 rank) | 6.22 core-s | **6.0 core-s** (pos), **5.0 core-s** (neg) | **0.96 / 0.80** |
| meshes built | 3 | **1** (the negative arm reuses the positive arm's mesh) | 0.33 |
| contention factor | 1.30 assumed | not separable at this size | — |
| **TOTAL solver + mesh** | **2.03 core-min** | **0.217 core-min** (13 wall s x 1 rank / 60) | **0.107** |
| **DERIVED dollars** | $0.0017 | **$0.00019** — **DERIVED, NEVER MEASURED** | |
| cap | 6.0 core-min | **not approached** — 3.6 % of cap | |

**Comparator compute, stated separately because it is not solver time:**
`--selftest` **2.9 wall s** at 1 rank = **0.048 core-min**, 50 arms. The two
drive-arm passes add roughly the same again. Box load average **11.37** on 16
vCPU while these ran.

### ATTRIBUTION OF THE GAP — rule 12 requires the gap be attributed, not absorbed

**Ratio actual/predicted = 0.107. Three named causes, none of them waste:**

1. **MISPREDICTION, mesh generation, 12x over.** I priced a 58,368-cell
   `blockMesh` + `topoSet` + `checkMesh -allGeometry -allTopology` at 25 core-s
   from a half-remembered K2d L1 figure. It is **2 core-s**. The lab should not
   carry 25 s as a mesh-generation prior at this size.
2. **MISPREDICTION, scope.** I predicted three separate builds and built one,
   reusing the mesh across both `A-INPUT` arms — which is also the *better*
   experiment, because the negative arm then differs from the positive one in
   the `functions` block **and in nothing else**.
3. **NO WASTE.** No run was abandoned, no arm was re-run for a fixed defect at
   solver cost; every repair this session was to Python and cost no solver time.

**THE ONE FIGURE WORTH CARRYING FORWARD, AND IT IS THE RATE MODEL:**
the solver arm predicted **6.22 core-s** and measured **6.0 core-s**, a ratio of
**0.96**. Back-solved, this run achieved **194,560 cell-iter/core-s** against
K2d's measured **187,598** — **1.037x**, inside 4 %.
**Registration §10.1's rate model reproduced on a fresh build at a different
rank count**, which is the substance of what `P-K2f-3` predicts and is recorded
here as an early, informal corroboration. **It does not score `P-K2f-3`**: that
prediction is written against L1 -> L2 at `endTime` 3000 and is scored there, on
the graded ladder, or not at all.

### WHAT THIS ROW IS NOT

It is **not** a measurement of rung K2f. No graded level was built into
`K2f_runs/`, no graded level was launched, and the registration remains
**UNFROZEN**. The throwaway trees were built under the session scratchpad and
are gone.
