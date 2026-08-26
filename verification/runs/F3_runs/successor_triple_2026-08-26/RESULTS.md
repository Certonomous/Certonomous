# F3 SUCCESSOR (grid triples) — RESULTS

**Graded 2026-08-26.** Pre-registration `verification/campaign/F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md`,
frozen at **`5891db27`** (v3, plus ADDENDUM 1 `382a526e` and ADDENDUM 2 `b468164c`, both
pre-grade, both altering no gate, threshold, cap or label).

**Graded path, in order:** `check_complete_f3s.py` (blob `0cd7f158`) → **rc 0, all 8 cases
COMPLETE** → `grade_f3s.py` (blob `d67d415f`, unchanged since the freeze) with
`--prereg-commit 5891db27`. Plain `python3`; both halves refuse `-O`.

---

## THE TALLY: 0 PASS · 0 GATE FAIL · **3 NOT A RESULT** · 0 PENDING

| gate | verdict | fine value | exact | deviation | band | **band verdict** | triple | why NOT A RESULT |
|---|---|---|---|---|---|---|---|---|
| G-F3S-1 wedge surface pressure | **NOT A RESULT** | 1.8640752447 | 1.86387051818 | **+0.0110 %** | ±0.5 % | **PASS** | OSCILLATORY | rule 5 limb (2) |
| G-F3S-2 wedge shock angle | **NOT A RESULT** | 32.2531525441 | 31.8505922313 | **+1.2639 %** | ±2.0 % | **PASS** | OSCILLATORY | rule 5 limb **(1)** — coarse and medium NOT_PLATEAUED |
| G-F3S-5 diamond wave drag | **NOT A RESULT** | 0.0134060944457 | 0.0134302783462 | **−0.1801 %** | ±1.0 % | **PASS** | OSCILLATORY | rule 5 limb (2) |

**No GCI is quoted on any row** — none of the three triples is monotone, and `GCI_pct` is absent
from all three, not merely unprinted. Observed order is `None` on all three for the same reason.

### The headline, stated plainly

**All three rows would have been `PASS` on the band alone. All three are `NOT A RESULT` once
rule 5 is actually asked.** That is what this rung was built to find out, and it is exactly how
the 2026-07-28 record graded these same cases: on the band, with no triple and no plateau test.

**The gate only ever moved verdicts one way — three `PASS`es into `NOT A RESULT`, never the
reverse.** Rule 5's asymmetry, demonstrated on real output rather than asserted.

---

## THE REGISTERED PREDICTION: **CONFIRMED**

Registered before compute (Annex E, and prominently in its own section): *the 2026-07-28 diamond
M2.5 triple is non-monotone (0.013428 → 0.013395 → 0.013406) and if it reproduces it grades
`OSCILLATORY` → `NOT A RESULT`.*

| level | 2026-07-28 | this rung | relative difference |
|---|---|---|---|
| coarse | 0.013428 | 0.01342773097 | −2.00e-05 |
| medium | 0.013395 | 0.01339532681 | +2.44e-05 |
| fine | 0.013406 | 0.01340609445 | +7.05e-06 |

**It reproduced to five significant figures, with the same down-then-up increment pattern.**
The triple graded `OSCILLATORY`; the row is `NOT A RESULT`.

**THIS IS THE RUNG WORKING. IT IS A CONFIRMED PREDICTION, NOT A FAILURE.** A conversion that
returns `NOT A RESULT` on a triple it predicted would be non-monotone has done its job: the
2026-07-28 **−0.18 % deviation**, which reads like a clean result, rests on a grid triple that
carries **no discretization-error estimate at all**. Nobody may read these rows as a failed rung,
as wasted compute, or as a reason to revisit the gate.

## The finding that was NOT predicted

**G-F3S-2 failed at limb (1), before the triple was ever consulted.** The wedge shock angle had
**not plateaued at coarse or medium**:

| level | β drift over window | tolerance | state | window samples |
|---|---|---|---|---|
| coarse | 2.282e-03 | 2.0e-03 | **NOT_PLATEAUED** | 39 |
| medium | 3.467e-03 | 2.0e-03 | **NOT_PLATEAUED** | 50 |
| fine | 7.304e-04 | 2.0e-03 | PLATEAUED | 102 |

The tolerance is **band ÷ 10**, fixed before any value was seen. Element 4's floor of 30 window
samples was met at every level **including the binding coarse one** — the cadence was chosen from
measured step counts, and that is why the gate could be evaluated at all rather than refusing.

**Only the Class C gate could have found this**, and no band-only or triple-only check would
have. `p_wall_mean` and `cd` plateaued at all three levels; iterative state was `CONVERGED`
everywhere on the direct-solver basis.

---

## Controls

**Bit-identity, two-armed — PASSED.** `p_wall_mean = 2.8217691727272731` and
`beta = 31.931111435642887` are **bitwise equal** across F3's 2026-08-24 record, arm A
(uninstrumented re-run) and arm B (instrumented). Arm A also reproduced F3's 8,071 steps and both
written time directories exactly. The comparison was planted with a 1-ULP perturbation and caught
it. **Instrumentation is an observation, not an intervention — measured, not argued.**

**Planted-zero controls passed on every graded reader**, each planting into the real artifact and
requiring the graded quantity to move by exactly `PLANT` in its own units:
`p_wall_mean_from_raw`, `beta_5station_lstsq`, `cd_from_force`. **Plateau controls**: a ramp 100×
the tolerance is required to be rejected at every level.

**Inherited-value cross-checks: 6 of 6 agree.** Every band and exact reference is quoted with its
line number in the frozen registration and cross-checked at run time against `grade_f3.py`'s
independent frozen copy. **No band was re-derived by this rung.**

---

## Cost (standing rule 12)

| | core-s | core-min | $ derived |
|---|---|---|---|
| **actual (launcher envelope — the quantity Annex B governs)** | **949.79** | **15.8298** | **0.013535** |
| ClockTime sum (± 4 s quantisation; integer-second resolution) | 934.00 | 15.5667 | 0.013310 |
| expected | 882.70 | 14.7117 | 0.012578 |
| **HARD CAP** | 1,059.24 | 17.6541 | 0.015094 |

**`cap_respected: true`.** Dollars are **derived at $0.0513/core-h, never measured** — this box
cannot read its own billing. The envelope exceeds ClockTime by **15.79 core-s (1.66 %)**: case
build, `blockMesh`, `checkMesh` and `postProcess`, which `ExecutionTime` would also have excluded.

**Ratio actual/expected = 1.0760.** Attribution, kept separate and never netted:

- **Instrumentation uplift: registered 1.15, measured 1.2948** (arm B ÷ arm A, the same case).
  This is the misprediction that drove the one per-run overrun, `wedge/M2.5_th10/fine` at
  **236.29 against a 230.74 claim (+2.4 %)**. Annex B's global cap is what is enforced; the
  per-run figures are predicted claims at enforcement point 1.
- **Contention: measured on a provably bit-identical computation, which is the cleanest form
  this lab can obtain.** Arm A ran the same case as F3's 2026-08-24 run and produced
  **bit-identical output**: 164.09 core-s tonight against **190.01** then — **13.6 % FASTER**.
  With the arithmetic proven identical, that difference is environment, not work. **Waste: zero**
  (all 8 runs rc 0, none re-run, none killed).

**Estimate-versus-actual is recorded in `docs/COST_CALIBRATION.md` as row `C-112`.**

*Correction of record: this row was first committed as `C-98`, which was a COLLISION with an
existing ansys-verification row. The id had been re-derived in-invocation from the HEAD blob's
tail as the maximum, per rule 11 — but with a pattern (`^\| *C-[0-9]+`) blind to the ledger's
dominant `| **C-NNN** |` format, so it saw 97 rows where 113 exist and reported a maximum 14
short. **A maximum taken by a reader not shown able to match every row is not a maximum** —
standing rule 3 applied to an id sweep. The corrected extractor takes the first table cell,
strips bold and whitespace, and is planted in both formats before it is trusted.*

---

## Defects found in this rung, all by running instruments rather than reading them

1. **`RT.Refusal` raised, not exited** — every gate refusal would have surfaced as an rc-1
   traceback instead of the rc-2 refusal standing rule 4 requires. Found by mutating a guard.
2. **The frozen grading path implemented none of Annex C's completion rule.** Found preparing for
   the completion check; repaired in a separate file under ADDENDUM 1.
3. **The completion checker crashed, and the crash hid a fail-open** that would have certified a
   case it had just called NOT DONE. ADDENDUM 2.
4. **Annex B registers three cap enforcement points; the launcher implements two** — the in-flight
   watchdog is absent. No breach occurred; disclosed in ADDENDUM 2 §6, carried to the successor.

## Carried to the successor, deliberately not fixed here

The in-flight cap watchdog; the buffered solver log (`sh()` writes only at exit, so a stall is
indistinguishable from slow progress); and the four `assert`-carried gates in the shared
`scripts/roache_triple.py` (`:195, 632, 634, 637`), which this rung guards against only at its own
boundary with an `-O` entry refusal.

---

## What this rung does NOT do

**It does not change F3's tally.** F3 remains **CLOSED at 5 PASS, 1 GATE FAIL, 1 NOT A RESULT,
3 PENDING**; its three `PENDING` cells stay `PENDING` and stay `BLOCKED` as a launch request. No
frozen F3 file was edited. **No row of this rung is a credential.**
