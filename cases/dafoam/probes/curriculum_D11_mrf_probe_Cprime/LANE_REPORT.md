# D11-C′ — LANE REPORT

**To:** `dafoam-supervisor`. **From:** dafoam `lab-lane`, 2026-08-25.
Nothing filed, sent or posted (rule 7).

---

## 1. Verdict

**`GATE REACHED`.** **A plateau WAS demonstrated for component 1.**

## 2. The correction you need first: the probe was NOT partly fired — it had finished

Your brief recorded *"4 stages ran, last one `rc=0` at 17:52Z, `TOTAL_SPENT_CORE_MIN=3.0337`"*. Those
two figures cannot both describe a 4-stage run, and the ledger settles it: **all 25 registered
containers ran** — 1 mesh + 2 `compute_totals` + 22 `run_model` — every one `rc=0`, finishing at
17:55Z, and `TOTAL_SPENT_CORE_MIN=3.0337` is the **total for all 25**, which is why it matched.
The 4-stage reading was an early tail of a log that kept growing. **I fired nothing for D11-C′ and
re-ran nothing**; there were no registered stages left. That freed the box for D9, which is where
the compute went.

## 3. The numbers, with their artifacts

Artifact root: `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D11C/`, ledger
`ledger.txt`, stamp `20260825T175244Z_2328716`.

**Freeze re-verified as you asked.** `git hash-object` on disk, `git rev-parse HEAD:<path>` and
`git rev-parse a02de9fa:<path>` all return `fab55707777e4b38e32e56e34e7fba814e657990`. Identical —
no abort. All four frozen instruments also hash **MATCH** against their committed blobs, and the
md5s are the ones §11 registered.

**COMPONENT 1 — the thing this probe was bought to buy:**

| quantity | value |
|---|---|
| adjoint `dTPIn_dpatchV[1]`, ω = 30 rad/s | **`-1.3660119098e-04`** 1/deg |
| plateau FD at the reference step `h = 1.0e-03` deg | `-1.3657515496e-04` 1/deg |
| **relative error** | **`1.906351e-04`** — inside the pre-registered `5.0e-2` band by ~262× |
| **plateau** | **DEMONSTRATED**: `h ∈ [1.0e-05, 1.0e-01]`, **5 consecutive usable steps**, spread ≈ `1.15e-02` against `PLATEAU_TOL_REL = 2.0e-2` |
| MRF-attributable fraction of component 1 | `1.0000230483` — the plant reaches the graded quantity |
| measured noise floor | `2.633418e-16` (repeat `0.0`, cross-task `0.0`, `ε·|TPIn|` with `TPIn = 1.1859858226134654`) |

**Yes — the plateau was DEMONSTRATED, and it is the answer to the question you posed.** The
reference step is the **middle of the longest qualifying window**, fixed by the rule frozen in §4
before compute, not chosen after seeing the agreement. `h = 1.0e+00` falls ~5 % away and is
correctly excluded from the window.

## 4. Your reservation about D11-F′ was right when written — and is now DISCHARGED

You pinned: *"D11-F's `FD_H = 1.0e-3` is a FIXED step with NO plateau demonstration, so
`1.704895e-07` is NOT a verified gradient and may not be quoted as one."* Correct at the time.
G11C-6 — registered in advance as **not** altering the probe verdict — ran the component-0 sweep in
m/s and found a plateau over `h ∈ [1.0e-04, 1.0e-01]`, 4 consecutive usable steps, reference
`h = 1.0e-03`, agreement **`1.704895e-07`**.

**D11-F′'s step lies INSIDE that demonstrated plateau.** The figure is **retroactively defended** and
may now be quoted as a plateau-step agreement **citing this record**, not D11-F′ alone. **D11-F′ was
not edited — not one byte**; its `GATE REACHED` stands as recorded.

Your table's underlying point survives intact and should not be softened: the component D11-F′
checked is ~99.99 % non-MRF, and until D11-C′ ran, nothing had checked the component the MRF term
dominates. That gap was real. It is now closed.

## 5. What I could not verify, stated plainly

- **The zero repeat bounds REPRODUCIBILITY only.** `|base1 − base2| = 0.000000e+00` and
  `|base1 − omegaP| = 0.000000e+00` because the substrate is deterministic at np = 1, so the floor
  fell back to the representational epsilon. **It does not bound iterative-truncation jitter.** What
  bounds truncation here is the sweep — six steps over five decades, five agreeing to ~1 %. The
  grader prints this disclosure itself rather than absorbing it.
- **No toolchain-independent claim.** Only the **shipped** row was bought. The `subpclu` patched
  adjoint path could in principle reach this and was not tested.
- **Nothing at engineering rotational rates.** 30 rad/s on 720 cells. The measured fact that
  **300 rad/s stalls this steady substrate** still stands and must go into D11's own
  pre-registration, which needs a rotating-frame-appropriate or unsteady case.

## 6. Cost, and the calibration row

**Gross 3.0337 core-min. Cleaned 3.0337** — identical, longest stage wall 10 s, nowhere near the
3600 s stall rule. **Waste 0.0, named separately and not absorbed into the ratio** — no re-run, no
stall, no abandoned container. Predicted 3.2 → **ratio 0.948**. Cap 8.0, **38 % used**.
**$0.0026 derived, NOT measured**, at $0.0513/core-h reported-by-owner.

**Gap attribution:** essentially all of the 5.2 % underspend is the **mesh stage** — predicted 0.22
core-min, measured **0.0167**. The 22 `run_model` containers were predicted at 0.12 core-min and
measured a mean of **0.12198**, a **1.6 %** error. **Contention: nil measurable** — walls held at
7–8 s and `measured_affinity=[13]` on all 25 stages, so no contention channel is claimed.

Calibration row **`C-75`** in `docs/COST_CALIBRATION.md`. The D11 chain's prior 3.0168 core-min is
named separately there and is **not** absorbed into this ratio, as §6 registered.

## 7. Full record

`cases/dafoam/probes/curriculum_D11_mrf_probe_Cprime/RESULTS.md`.
