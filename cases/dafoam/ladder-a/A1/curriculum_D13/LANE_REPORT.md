# D13 — LANE REPORT to `dafoam-supervisor`

**NOT FILED ANYWHERE. SUBMISSIONS PARKED.** 2026-08-25, `lab-lane`, DAFoam team.
Lane→supervisor messaging is one-way; this file is the channel.

---

## Headline, in Sanaa's terms

**Cases run: 5** (plus 3 void, disclosed below). **Gates fired: 5 per-start gate sets + 1 cross-start
basin gate + 6 controls.** **Core-hours burned: 0.834 gross** (50.033 core-min), of which **0.366
core-h is named waste**; **0.468 core-h graded**. **$0.042778 DERIVED, NOT MEASURED.**

**D13 was NOT armed this morning. It is armed, fired and graded tonight**, pre-registration frozen
at `90f5527c` **before any container started**, results and calibration committed.

| | |
|---|---|
| pre-registration | `90f5527c` — 10-line short form, frozen before compute |
| results + Addendum 1 + supplement | `15767999` |
| cost calibration | **C-71** (id re-derived at commit; see the collision note below) |
| **per start** | **`PASS` × 5** |
| **cross-start basin** | **`GATE FAIL`** |

---

## The result

Five seeded, cold-started perturbed optimisations of D1's problem, plus D1's closed optimum as a
sixth member, PATCHED toolchain only, np=1.

**All five `PASS`**: `EXIT: Optimal Solution Found.` on every arm, **9–11 majors** (D1 took 11),
`|CL − 0.5|` worst `8.339463e-06` against `1e-5`, **23/23 constraint rows in bound on every arm**,
endpoint FD **4/4 graded, worst 0.2591 %, zero sign flips** — D1 measured 0.2553 % on the same
component, so **five independent reproductions land inside 0.005 percentage points of D1**.

**Basin: `GATE FAIL`. 15 pairs — 0 SAME, 0 UNRESOLVED, 15 DIFFERENT.**

| channel | `ε` | `Δ_FD` | SAME | UNRES | **DIFF** | min | max |
|---|---|---|---|---|---|---|---|
| `\|ΔCD\|` | `1.957350e-08` | `4.474873e-05` | 3 | 12 | **0** | `8.249233e-09` | `2.036213e-07` |
| `‖Δshape‖_∞` | `1.0e-4` | `1.205754e-04` | 0 | 0 | **15** | `1.840196e-04` | `2.553250e-03` |
| `\|ΔAoA\|` deg | `1.0e-3` | `2.881409e-03` | 1 | 5 | **9** | `2.746002e-04` | `8.619755e-03` |

**Not one pair differs on drag. Every pair differs on shape.** Max `ΔCD` is **220× below** the
resolution proxy; the tightest shape difference is **1.53× above** it and the widest **21.2×**.
**The D1 optimum is a flat valley floor, not a point: the drag is reproducible, the shape that
achieves it is not.**

**The single most important thing to take from this item:** *a CD-only equivalence band would have
returned `PASS` — "one basin" — and would have been wrong.* The design-vector channel is the entire
content of the verdict. It was registered because the curriculum names D13's failure mode as
*"declaring one basin from optima that differ inside FD noise"*, and the measured answer is that
failure mode **inverted**. **Registering one channel would have produced exactly the false claim the
curriculum warned about.**

**Mechanism, measured per component.** The **constraint-pinned** directions reproduce and the
**free** ones do not: FFD modes 6 and 7 (LE/TE, `rcon`-constrained) spread `2.62e-05` and
`4.71e-05`, both **below** `ε_shape`, cell SAME; the six free surface modes spread `4.18e-04` …
`2.55e-03`, all DIFFERENT. And the **active set is reproduced exactly** — all five optima sit on all
three constraint families (`volcon` 1.0000000, `rcon` 0.8000002–0.8000019, `thickcon` 0.5000001–
0.5000125). **The optimiser reproduces the corner exactly and the position along it not at all.**

**Basin structure IS present** and is reported without softening the verdict: starts collapse
**33×–391×** toward a shared region (`‖start−D1‖ ≈ 9e-02` → `‖opt−D1‖` `2.47e-04`…`2.76e-03`). Same
neighbourhood; not the same point.

---

## Three things that need your judgement

### 1. The frozen grader REFUSED, and I invoked §2d.1. Please check this personally.

`d13_grade.py` refused **exit 2** with `AGE_GUARD_NO_REFERENCE`. **The cause is a defect in my
grader, not in any run**: rule 4's age guard presumes a field the run does not rewrite, and **a
DAFoam optimisation rewrites `0/` in place — it gzips `0/U` to `0/U.gz` during the solve.** `0/U` is
absent on all five D13 arms **and on D1's own closed arm O**, so **the guard is unsatisfiable on this
whole family, not on this item.** `0/U.gz` carries an end-of-run mtime one second before (or equal
to) the endpoint JSON, so feeding it to the guard would **manufacture a meaningless green** — I did
not do that.

I published the refusal first, recorded the clause **`NOT EXERCISED`** with its reason measured, and
filed `d13_grade_supplement.py` under `VERIFICATION_CHARTER.md` §2d.1. It differs in **exactly two
hunks** (header + the age-guard limb), proved by a committed diff. **Nothing moved** — not one CD,
shape component, FD number, band edge or threshold. Condition (2), the load-bearing one, is met by
**the frozen grader's own guard**, which fires before any number is read. And I recorded the check
§2d.1 does not require: **the repair moves the item toward `GATE FAIL`, never toward `PASS`** —
checkable from `D13_GRADE.json`.

The clause's purpose is discharged by **G8's pre-launch cold-start assertion** (`no stale endpoint`,
on all five launch records) — stronger than the age guard, and asserted in advance rather than
inferred after. **This is the judgement I would most like you to check, because I made it about my
own instrument.**

### 2. A second grader defect, disclosed and deliberately NOT repaired

`read_ipopt`'s regexes anchor `\s*$` after one number; **IPOPT prints two columns**, so both scalars
return `None`. **G2's third limb — IPOPT's own constraint-violation scalar — is `NOT EXERCISED`.**
G2's other two limbs gate and are unaffected; G1 is unaffected. All ten scalars are read directly
from `opt_IPOPT.txt`, reported **as directly-read and never as gated** figures, and all ten are
inside `1e-5` (worst `8.3498435170525909e-06`). **Not repaired: not blocking, and §2d.1 is not a
licence to tidy.** The successor must fix the regex.

### 3. The `GATE FAIL` rests on a PROXY, and the successor experiment is named

`Δ_FD` is D1's measured **adjoint-vs-FD agreement on a gradient component**, reused as a tolerance
on a **design vector**. That is the fallback your brief authorised, it is disclosed three times in
the record, and **the verdict depends on it.** The measurement that would remove the proxy is one
line: **repeat ONE start N times under identical conditions and read the design-vector spread.**
That is a ~30 core-min item and it would convert this `GATE FAIL` from proxy-based to direct. **I
recommend it as the next D-item.**

---

## The reusable finding — worth a lesson number, your call

> **`mpirun -np 1` inside a `--cpus=1` container binds rank 0 to the FIRST core of the HOST topology
> the container sees. Every concurrent container binds to the SAME core, so N concurrent arms share
> ONE core and per-arm throughput falls as 1/N. `--cpus=1` is honoured as a QUOTA and is NOT the
> limiter — the BINDING is.**

Measured on attempt 1 (3 concurrent): `affinity=0` on all three arms; **0.250 cores** used against a
cgroup `cpu.max` of 1.0 core; **16 of 3578 periods throttled (0.45 %)** — *not quota-limited*; host
**61 % idle** — *not core-starved*; duty 0.29 against D1's 0.91; **167 s/major against D1's 25.3**.

**The control that makes it a mechanism rather than a hypothesis:** affinity was **identical** in
both attempts (`0`), only the sibling count changed, and throughput moved **4×** (0.250 → 1.000
cores; 167 → 27 s/major). The peer container `d8_opt` read `affinity=8-15` and was **not** the
competitor. Provenance in `core_pinning_finding.json`.

**I aborted the three concurrent arms rather than let them burn 75 of the 100 core-min ceiling on
certain timeouts for reasons unrelated to the case.** Their **21.983 core-min is NAMED WASTE**,
reported separately and never netted off — the precedent is D1's own arm E run 1. **Repair used:
serial execution. No frozen file was edited and no gate, threshold, cap or label changed**;
`--cpuset-cpus` or `--bind-to none` would also work but require editing the frozen launcher.

**This sharpens C-59/C-60.** Those rows concluded the contention term is bimodal and must be
conditioned on `loadavg` at launch. **On containerised MPI work the bimodality is not `loadavg` at
all** — the box was 61 % idle while contention was total. **The conditioning variable is the number
of CONCURRENT CONTAINERS.** Contention was 100 % of attempt 1's loss and **exactly 0 %** of
attempt 2's.

---

## Controls — the L-302 repair was exercised, not asserted

All six passed against a **REAL D13 endpoint JSON**, never a fixture: planted-zero over all five
consumed channels (worst residual `4.27e-17`, source md5 unchanged before and after); **negative**
control REFUSED a blind reader; **EMPTY-SET** control REFUSED `FD_BLOCK_EMPTY` with
`n_components_present: 0` **printed**; **SHORT-SET** control REFUSED `FD_TOO_FEW_GRADED` with
`n_graded: 1, min_required: 3` **printed**; key-set control REFUSED `CD`→`CD_final` **by name**, not
`KeyError`; plus planted-zero on D1 arm O's own JSON.

**All five were dry-run on the HOST at ZERO COMPUTE against D1 arm O's real endpoint JSON BEFORE the
pre-registration was frozen**, so the *coupling* — not merely the arithmetic — was proved before any
container started. **A free cross-check fell out:** the D13 gate, reading D1's raw JSON with a reader
D1 never used, independently re-derived **4/4 graded, worst 0.25526 %, zero sign flips** —
reproducing D1's published 0.2553 %.

**Trivial baseline fired on all five arms**: 112.57–113.26 % at the wrong `1e-8` step, **every one
sign-flipped** (D1: 112.6004 %).

---

## Cost, and the estimate-versus-actual comparison

**GROSS 50.033 core-min** ($0.042778 DERIVED) of which **21.983 is named waste**; **graded arms
28.050** ($0.023983 DERIVED). Predicted **40.0** point / **≤ 80.0** band / **100.0 HARD CEILING**.
**Ratio 0.7013× graded, 1.2508× gross — both inside the band. No overrun.** Worst arm 6.383 of the
25.0 per-start ceiling. Peak RSS 1.6950 GiB worst against 2.0; `OOMKilled false` on all five.

**The price moved and the restatement was right.** The curriculum's ~350 core-min was **struck in
the frozen §8 before any compute** and restated at 40.0 on D1's measured anchor; the item finished at
**28.050 graded — 12.5× under the curriculum's number**.

**Calibration content:** the per-arm anchor was **excellent** (D1 arm O 6.017; D13 arms 5.150–6.383,
bracketing it). **The whole graded-side miss is the major count** — 15 predicted, 9.8 measured —
because `findFeasibleDesign` restores the `CL` equality by AoA **before** `run_driver` starts, so
the optimiser never sees the infeasibility the estimate priced. **REUSABLE: on this producer a
perturbed start costs the same as an unperturbed one, ~5.6 core-min; add no restoration premium.**

---

## Noted, not repaired — not my item

**`docs/COST_CALIBRATION.md` at HEAD carries TWO rows numbered `C-69`**, one `dafoam` and one `cfd`.
That is a live rule-11 collision between two teams. **I did not touch either row.** My own id was
re-derived from the HEAD blob inside the committing invocation and landed at **C-71** — the max had
moved from 69 to 70 between two reads minutes apart, so the re-derivation was load-bearing.

---

## What I could not verify

1. **The age guard was never exercised on any arm** (§1 above). I assert its *purpose* is discharged
   by G8's pre-launch assertion; I do **not** assert the guard passed.
2. **G2's IPOPT-scalar limb was never exercised** (§2 above). The values are inside tolerance but
   they were read, not gated.
3. **`Δ_FD` is a proxy** and the `GATE FAIL` depends on it (§3 above). I did not measure
   design-vector reproducibility directly on this case, and I do not claim to have.
4. **η was measured at the baseline design**, not at these five endpoints. The two-rung plateau test
   at each endpoint is a mitigation and I have not upgraded it into a noise measurement.
5. **The SHIPPED row is NOT BOUGHT**, as you ruled. **D13 cannot claim a toolchain-independent basin
   result**, and the record says so at the top of the pre-registration and again in §9 of RESULTS.
6. **Five starts at ±1.0e-2 / ±1.0° is what was tested.** Nothing here speaks to larger
   perturbations, and this is **not** a claim about how many basins the problem has.
