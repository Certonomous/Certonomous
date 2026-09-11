# A3GC L3 — GRADING RECORD, 2026-09-11

**VERDICT: `NOT A RESULT`.** Two independent grounds, either sufficient.
Graded by the dafoam-supervisor against the frozen registration
(`PREREGISTRATION.md`, commit `367799db0`, AMENDMENTS 1–6).
**SUBMISSIONS PARKED.**

## The run

`/home/ubuntu/certonomous-runs/A3GC-L3/`, `DARhoSimpleCFoam`, np=4, detached,
rc captured inside the wrapper. Mesh: **99,840 cells**, exactly §2.5's
registered L3 count, built by frozen `a3gc_genmesh.sh`
`9fa240d9643308f5e9a4988614b58884`.

## Rule-4 completion — EVERY LIMB HELD

`rc = 0` (`primal.log.rc`) · two `End` lines · last `Time = 6000` = registered
`endTime` · **61 `ExecutionTime` samples = 1 + 6000/100**, matching
`printInterval 100` · fields at `processor*/{0,2000,4000,6000}`, `writeInterval
2000` honoured.

**THE RUN IS COMPLETE AND WELL-FORMED. THAT IS WHY THIS VERDICT MATTERS.**

## GROUND 1 — the registered flow condition was never applied

§4.1 registers `aoa0 = 3.06`. **`grep -n 'aoa\|alpha\|incidence' runScript_a3gc.py`
returns exactly ONE line — `21: aoa0 = 3.06`, the assignment.** The inlet is
written `"U0": {... "value": [U0, 0.0, 0.0]}` — **pure x, zero incidence** — and
`patchV`, declared with `flowAxis: x / normalAxis: y`, is never given a value.

| | measured | §4.1 anchor |
|---|---|---|
| CD | **0.01838232594** | 0.0229956 |
| CL | **2.954197352e-06** | 0.3131159 |

**CL is five orders of magnitude below the anchor.** The ONERA M6 carries a
symmetric section, so CL ≈ 0 at zero incidence is not a coincidence — it is the
signature. **This is not a value that missed its band: the solve answered a
different question from the one registered, so it is not a solve of A3GC's L3.**

**A COMPLETION GATE CANNOT SEE A WRONG FLOW CONDITION**, and a `grep` for
`aoa0` would have passed this file — the variable was present the whole time.

## GROUND 2 — not iteratively converged

Registered accept floor: `primalMinResTol 1e-8 × primalMinResTolDiff 100 =
1e-6`. Final per-equation `initRes`, flat over the last ~10 samples:
**p 6.288e-5 — 63× ABOVE the floor** · he 6.435e-7 · nuTilda 6.084e-6. The gate
is the maximum, so he and nuTilda do not rescue it. Standing rule 5 clause 1: a
level not iteratively converged is `NOT A RESULT` whatever its value.

## Cost — GROSS, and the basis is not clean

**63.7 core-min gross** (956 wall s × 4), against §5's 1,525 core-min estimate —
4.2% of it. **Honest computational measure: 34.4 core-min** (`ExecutionTime
515.63 s` × 4), so **~46% of wall time was contention, not computation**: box
load ran 11.4 → 70.4 on 16 vCPU across the session, none of it this item's.
Preceding failed attempts, named separately and not absorbed: **0 + 2.0 + 18.3
core-min** (rc 134 launch failure, rc 1 int/float refusal, rc 1 missing thermo
dict). A3GC total **84.0 core-min gross**. Dollars **DERIVED, NOT MEASURED** at
$0.0513/core-h: $0.072 for this run, $0.0718 for the item to date.

## Not asserted

The solution fields are in `processor*/` and have **not** been reconstructed. No
grid triple exists — this is one level of three. `evaluate_shock` has still never
run against real VTK.
