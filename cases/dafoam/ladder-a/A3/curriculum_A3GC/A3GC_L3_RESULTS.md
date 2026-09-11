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

---

# A3GC L3 — RUN 2, WITH THE REGISTERED INCIDENCE AND FORCE FRAME, 2026-09-11

**VERDICT: `NOT A RESULT`.** **GROUND 1 IS CLEARED. GROUND 2 ALONE DECIDES IT.**

## Ground 1 — CLEARED, and confirmed by a prediction made before the run existed

`Setting UMag = 291.6 AoA = 3.06 degs at 1(inout)` appears **once** in `primal.log`
(count 0 on both earlier runs). Applied angle read from `processor0/0/U.gz`, the
field the **solver** wrote: **aoa 3.060000°, |U| 291.600000, Uz 0** — not doubled,
with 6.12° planted through the same reader and refused by name.

| | measured | §4.1 anchor | |
|---|---|---|---|
| **CD** | **0.029779800534915524** | 0.0229956 | +29.50 % |
| CL | 0.30339175096960158 | 0.3131159 | −3.11 % |

**THE CONFIRMING NUMBER IS CD, NOT CL.** From the *stopped* wrong-frame run the
supervisor projected true-frame CD = **0.029781** by adding the omitted induced
projection. The independently completed run gives **0.0297798005** — a difference of
**−1.20e-06, −0.0040 %**, from two different runs at two different iteration counts.
**CL rose 1.03e+05× and would have looked correct either way**, which is why it was
the wrong discriminator and CD was the right one.

## Rule-4 completion — every limb held

`rc = 0` · `End` ×2 · last `Time = 6000` = `endTime` · **61** `ExecutionTime` samples
= 1 + 6000/100 · fields at `processor*/{0,2000,4000,6000}` · **age guard: all 40
endTime files newer than `0/T` (22:39:57Z)**, the guard restored to discriminating
after it was found vacuous at a July-28 stamp.

## GROUND 2 — NOT ITERATIVELY CONVERGED. THIS IS THE VERDICT.

Registered floor `primalMinResTol 1e-8 × primalMinResTolDiff 100 = 1e-6`.

| equation | final `initRes` | vs floor |
|---|---|---|
| **p** | **2.290019532e-05** | **22.9× ABOVE** |
| nuTilda | 6.812089e-06 | 6.8× above |
| he | 7.957234e-07 | below |
| U0/U1/U2 | 3.0e-07 … 5.2e-07 | below |

**p is DEAD FLAT**: 2.257e-05 (sample 20) → 2.294e-05 (40) → 2.290e-05 (61),
oscillating in a 2.26–2.31e-05 band with no descent. The gate is the **maximum**, so
`he` and the velocities do not rescue it. Across three runs p has gone **6.288e-05 →
2.264e-05 → 2.290e-05**: the incidence repair bought 2.7× and then stopped.
**NOTHING WAS TUNED TO CHASE IT.** Standing rule 5 clause 1.

**This is a finding about this case at 99,840 cells, not a defect to be engineered
away**: the coarse level of the registered family does not reach its own registered
accept floor in 6000 iterations.

## Cost — and a correction to the earlier contention framing

854.9 wall s × 4 = **57.0 core-min GROSS**; `ExecutionTime` 439.6 s × 4 = **29.3
core-min** of computation. **The gap is NOT mostly contention**: the solver's own
`ClockTime` 451 s against `ExecutionTime` 439.6 s puts in-solve contention at **11.4 s
— 2.5 %, 0.76 core-min**. The other **26.9 core-min is fixed per-run overhead**
outside the solver's clock — container start, `decomposePar`, the TensorFlow import in
DAFoam init, field writing, teardown — **and it will repeat on L2 and L1.** The
earlier record's "~46 % contention" overstated the box and understated this overhead.

**Waste, named and not absorbed: 5.8 core-min** (a prepare discarded because the
runner was edited while bash was still reading it). Session ≈ **67.7 core-min GROSS**,
**$0.058 DERIVED, NOT MEASURED**.

## Not asserted

**No triple exists — this is one level of three**, and the gate is the Roache triple
over L3/L2/L1. The +29.50 % CD gap against the anchor is **not interpreted**: §4.1
states the 399,360-cell anchor is not a family member. `evaluate_shock` has still
never run against real VTK.
