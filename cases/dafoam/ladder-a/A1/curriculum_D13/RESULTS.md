# Curriculum item D13 — basin/restart robustness on the D1 problem: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-25 by a `lab-lane` of the DAFoam team.** The governing document is
`PREREGISTRATION.md` in this directory, frozen before any container started at commit
**`90f5527c`**, as amended by its own **Addendum 1** (filed after first compute under
`VERIFICATION_CHARTER.md` §2d.1). **This file does not revise the pre-registration.** No gate,
threshold, cap, equivalence-band edge, label or start vector was altered by this lane.

---

## 1. Verdicts

| row | image | what it graded | verdict |
|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` (`sha256:2927768a…e30f6d35`) | five seeded perturbed starts of D1's problem, each cold-started, each with its endpoint gradient re-verified against finite differences at the design point it actually reached | see below |
| **SHIPPED** | — | — | **NOT BOUGHT** — registered as not bought in `PREREGISTRATION.md` §0, on the supervisor's ruling, before any start ran |

**Per start — all five from the fixed vocabulary:**

| start | verdict | IPOPT exit | majors | `CD` | `\|CL − 0.5\|` | FD graded | worst FD | core-min |
|---|---|---|---|---|---|---|---|---|
| **s1** | **`PASS`** | `EXIT: Optimal Solution Found.` | 11 | `0.017527908103768686` | `4.223094e-07` | **4/4** | **0.2568 %** | 6.383 |
| **s2** | **`PASS`** | `EXIT: Optimal Solution Found.` | 9 | `0.017528032918957957` | `4.982993e-07` | **4/4** | **0.2540 %** | 5.217 |
| **s3** | **`PASS`** | `EXIT: Optimal Solution Found.` | 10 | `0.017527829297657737` | `8.339463e-06` | **4/4** | **0.2557 %** | 5.617 |
| **s4** | **`PASS`** | `EXIT: Optimal Solution Found.` | 9 | `0.017527992899864696` | `1.003317e-06` | **4/4** | **0.2591 %** | 5.150 |
| **s5** | **`PASS`** | `EXIT: Optimal Solution Found.` | 10 | `0.017527890060862118` | `1.300993e-06` | **4/4** | **0.2582 %** | 5.683 |

**CROSS-START BASIN VERDICT, against the band frozen at `90f5527c` before any start ran:**

# `GATE FAIL`

**15 of 15 pairs `DIFFERENT`. 0 `SAME`. 0 `UNRESOLVED`.** The registered claim — *these starts reach
the same optimum* — is **falsified**, and the falsification is the result.

**The graded claim, stated once, in full.** Five perturbed starts, seeded and cold-started, plus
D1's closed optimum as a sixth member, all converge on the **same corner of the feasible set** with
**indistinguishable drag** and **measurably different shape**. Every pairwise `ΔCD` is at most
**`2.036213e-07`** — **220× below** the registered FD-noise proxy and about 10× the case's own
measured plateau noise η — so **not one pair is `DIFFERENT` on the objective.** But every pairwise
`‖Δshape‖_∞` **exceeds** the proxy, by **1.53× at the tightest pair and 21.2× at the widest** — so
**all fifteen pairs are `DIFFERENT` on the design vector.** **The optimum of the D1 problem is a
flat valley floor, not a point: the drag is reproducible and the shape that achieves it is not.**

---

## 2. The band did the work it was registered to do — and a one-channel band would have been wrong

**Per-channel cell counts over all 15 pairs**, against the edges frozen in `PREREGISTRATION.md` §4:

| channel | `ε` (SAME edge) | `Δ_FD` (proxy edge) | SAME | UNRESOLVED | **DIFFERENT** | min Δ | max Δ |
|---|---|---|---|---|---|---|---|
| `\|ΔCD\|` | `1.957350e-08` (= η, measured) | `4.474873e-05` | 3 | 12 | **0** | `8.249233e-09` | `2.036213e-07` |
| `‖Δshape‖_∞` | `1.0e-4` (= `SHAPE_FLOOR`) | `1.205754e-04` | 0 | 0 | **15** | `1.840196e-04` | `2.553250e-03` |
| `\|ΔAoA\|` deg | `1.0e-3` (= `PATCHV_FLOOR`) | `2.881409e-03` | 1 | 5 | **9** | `2.746002e-04` | `8.619755e-03` |

**Read this table before reading the verdict.** A CD-only equivalence band would have returned
**`PASS` — "one basin" — and it would have been wrong.** The design-vector channel is the entire
content of this verdict. That channel was registered *because* the curriculum names D13's own
failure mode as *"declaring one basin from optima that differ inside FD noise"*, and the measured
answer is that failure mode **inverted**: the optima agree far **inside** the noise on the objective
and differ **outside** it on the design. Registering one channel would have produced exactly the
false claim the curriculum warned about.

**The `DIFFERENT` verdict does not rest on a marginal pair.** The tightest of all fifteen shape
differences, `1.840196e-04`, is 1.53× the proxy and 1.84× `ε_shape`; the widest is 21.2× the proxy.
There is no pair whose classification would flip under a small change to `Δ_FD`.

### 2.1 The mechanism, measured per component — the constraint-pinned directions reproduce, the free ones do not

Spread (max − min) of each FFD mode across the six optima:

| mode | spread | cell | what pins it |
|---|---|---|---|
| 0 | `9.869159e-04` | **DIFFERENT** | free surface mode |
| 1 | `4.177217e-04` | **DIFFERENT** | free surface mode |
| 2 | `2.553250e-03` | **DIFFERENT** | free surface mode — the widest |
| 3 | `8.584500e-04` | **DIFFERENT** | free surface mode |
| 4 | `1.234552e-03` | **DIFFERENT** | free surface mode |
| 5 | `8.805920e-04` | **DIFFERENT** | free surface mode |
| **6** | **`2.620284e-05`** | **SAME** | **LE/TE mode — `rcon`-constrained** |
| **7** | **`4.708504e-05`** | **SAME** | **LE/TE mode — `rcon`-constrained** |

**The two LE/TE modes reproduce below `ε_shape`; the six free surface modes do not.** And the corner
itself is reproduced exactly — every one of the five optima sits on all three constraint families:

| start | `volcon` (floor 1.0) | `rcon` ×2 (floor 0.8) | `thickcon` min (floor 0.5) |
|---|---|---|---|
| s1 | `1.000000019` | `0.800000169` | `0.500000164` |
| s2 | `1.000000302` | `0.800000564` | `0.500003419` |
| s3 | `1.000000811` | `0.800001898` | `0.500012517` |
| s4 | `1.000000333` | `0.800000328` | `0.500010311` |
| s5 | `1.000000129` | `0.800000528` | `0.500000134` |

**The optimiser reproduces the ACTIVE SET exactly and the position along the corner's free
directions not at all.** That is a coherent physical reading of a `GATE FAIL`, and it is consistent
with D1's own §4.4 finding that three of four constraint families are active at its optimum.

### 2.2 There IS basin structure, and it is reported because the verdict is not the whole story

The starts do collapse toward a common region — they simply do not collapse to a point:

| start | `‖start − D1‖₂` (shape) | `‖optimum − D1‖₂` | collapse |
|---|---|---|---|
| s1 | `9.673308e-02` | `2.471263e-04` | **391×** |
| s2 | `9.121502e-02` | `2.764002e-03` | **33×** |
| s3 | `9.780223e-02` | `4.754618e-04` | **206×** |
| s4 | `8.753767e-02` | `2.343684e-03` | **37×** |
| s5 | `9.259031e-02` | `2.838748e-04` | **326×** |

**Stated as the limit it is:** a 33–391× collapse toward a shared region is real and is reported,
but it is **not** the registered claim. The registered claim was equivalence inside a frozen band,
and that claim failed. **This paragraph does not soften the verdict and must not be read as doing
so** — it is here because a reader who saw only "GATE FAIL" would wrongly conclude the starts went
to unrelated places.

### 2.3 Six optima, one drag

All six `CD` values span `0.017527829297657737` … `0.017528032918957957` — a spread of
**`2.036213e-07`**, about **10.4× η** and **220× below** the FD-noise proxy. Five independent
perturbed optimisations and D1's own closed run agree on the drag to the seventh significant figure.

---

## 3. The frozen grader REFUSED, and that refusal is published FIRST

`d13_grade.py` (md5 `f0b2ccfd0271d1301eec70df820d32e3`, the file frozen in `PREREGISTRATION.md` §9)
was run against the completed arms and **refused, exit 2**:

> `D13_REFUSE AGE_GUARD_NO_REFERENCE {"path": ".../s1/0/U"}`

Preserved verbatim at `D13_GRADE_FROZEN_REFUSAL.txt` in the run root. **The comparator refused
rather than degraded.**

**The cause is a defect in this lane's grader, not in any run**, and it is measured: `CLAUDE.md`
rule 4's age guard presumes a field the run does not rewrite, and **a DAFoam optimisation rewrites
`0/` in place — it gzips `0/U` to `0/U.gz` during the solve.** `0/U` is absent on all five D13 arms
**and on D1's own closed arm O**, so the guard is unsatisfiable on this **family**. `0/U.gz` carries
an end-of-run mtime one second before (or equal to) the endpoint JSON, so handing it to the guard
would manufacture a meaningless green — and this lane did not do that.

**The clause is recorded `NOT EXERCISED` with its reason measured**, and its evidentiary purpose is
discharged by a **stronger, pre-launch** assertion: G8's cold start `rm -rf`'d each arm directory,
re-copied it from `base/` and asserted **`no stale endpoint`** before the container started. All
five launch records carry the line. *The answer file did not exist at all, asserted in advance* is
stronger than *the answer is newer than `0/T`*, inferred afterwards.

`d13_grade_supplement.py` (md5 `b30a187d804b96d2bc08cbd04db9e33d`) then produced the verdicts above.
It differs from the frozen grader in **exactly two hunks** — a header and the age-guard limb —
proved by `d13_grade_supplement.diff` (md5 `d69ee3dafe38f7aeb1b1427b6c9992cc`). **The four §2d.1
conditions are enumerated with their evidence in `PREREGISTRATION.md` Addendum 1 §A1.4.** The
load-bearing condition (2) is met by the frozen grader's **own guard**, which fires before any
number is read and therefore cannot have been selected to move a verdict; and **§A1.5 records the
check §2d.1 does not require: the repair moves this item toward `GATE FAIL`, never toward `PASS`.**

**What moved: nothing.** Not one `CD`, shape component, FD number, band edge or threshold.

### 3.1 A second grader defect, disclosed and NOT repaired

`read_ipopt`'s regexes anchor `\s*$` after one number; **IPOPT prints those lines in two columns**,
so `nlp_error` and `constr_viol` both return `None`. **Consequence, stated precisely: G2's third
limb — IPOPT's own constraint-violation scalar — is `NOT EXERCISED`.** G2's other two limbs
(`|CL − 0.5| ≤ 1e-5`; all 23 constraint rows in bound) **do** gate and are unaffected, and G1 reads
only `exit` and `majors`. The scalars, **read directly from each `opt_IPOPT.txt` and reported as
directly-read figures, never as gated ones**:

| start | `Constraint violation` (tol `1e-5`) | `Overall NLP error` (tol `1e-5`) |
|---|---|---|
| s1 | `4.4734182558237023e-07` | `1.1687075415504582e-06` |
| s2 | `4.8573928901340935e-07` | `7.2713220448953647e-06` |
| s3 | `8.3498435170525909e-06` | `8.3498435170525909e-06` |
| s4 | `1.0168206623917264e-06` | `8.1758877616078011e-06` |
| s5 | `1.3009951081999205e-06` | `6.8740912497612309e-06` |

All ten values are inside `1e-5`. **This is not repaired**: it is not blocking, and §2d.1's exception
is not a licence to tidy.

---

## 4. Attempt 1 was VOID on a measured execution defect — and the defect is a reusable lab finding

**Attempt 1 ran three arms concurrently and was aborted after 21.983 core-min. That spend is NAMED
WASTE, reported here separately and NEVER netted off** (`COMPUTE_BUDGET_CHARTER.md` §6). The
precedent is D1's own arm E run 1, VOID and named waste at 0.300 core-min.

**THE FINDING, and it was measured before it was acted on:**

> **`mpirun -np 1` inside a `--cpus=1` container binds rank 0 to the FIRST core of the HOST topology
> the container sees. Every concurrent container therefore binds to the SAME core, so N concurrent
> arms share ONE core and per-arm throughput falls as 1/N. `--cpus=1` is honoured as a quota and is
> NOT the limiter — the BINDING is.**

| measurement | attempt 1 (3 concurrent) | attempt 2 (serial) |
|---|---|---|
| solver process affinity | **`0`** on all three arms | **`0`** — *unchanged* |
| cores actually used, cgroup `usage_usec` delta | **0.250** | **1.000** |
| cgroup `cpu.max` | `100000 100000` (= 1.0 core) | same |
| periods throttled | **16 of 3578 = 0.45 %** — *not quota-limited* | — |
| host idle (`vmstat`) | **61 %** — *not core-starved* | — |
| duty (`ExecutionTime`/wall) | **≈ 0.29** | — |
| rate | **≈ 167 s/major** | **≈ 27 s/major** |

**D1's arm O measured 0.91 duty and 25.3 s/major running ALONE.** D1 and D2 never met this because
they never ran two arms at once.

**The control that makes this a mechanism rather than a hypothesis:** the affinity was **identical**
in both attempts (`0`), only the sibling count changed, and throughput moved **4×**. Same binding,
different contention, measured recovery. The peer container `d8_opt` read `affinity=8-15` and was
**not** the competitor. Full provenance in `core_pinning_finding.json` in the run root.

**The repair used was serial execution — NO frozen file was edited and no gate, threshold, cap or
label changed.** `--cpuset-cpus` or `mpirun --bind-to none` would also fix it but require editing
the launcher, which is frozen at the pre-registration commit (`CLAUDE.md` rule 6).

---

## 5. Per-start gates, in full

**G0 completion** — `rc = 0`, container `.State.ExitCode 0`, `.State.OOMKilled false`, IPOPT `EXIT:`
present, majors **<** the `max_iter 40` cap, endpoint key set asserted by name, `.ok.<STAMP>`
sentinel present, G8 cold start asserted **pre-launch**: **all five complete.** The age-guard clause
is **`NOT EXERCISED`** (§3). **No start was capped, timed out or stopped by a ceiling**, so
`GATE REACHED` is not the verdict on any row.

**G2 feasibility** — every start: **23 of 23 geometric constraint rows in bound, 0 out of bound**
(20 `thickcon`, 1 `volcon`, 2 `rcon` — the same count D1 measured), `|CL − 0.5|` worst
`8.339463e-06` against the registered `1.0e-5`.

**G3 the FD table, with the count refusal firing on every arm** — marker
`D13_G3_COMPONENT_COUNT where=s<k> n_named=4 n_present=4 n_graded=4 min_required=3` on all five.
**4 of 4 named components graded on every start, zero sign flips, worst relative error 0.2591 %**
against the registered 5 %. D1 measured **0.2553 %** on the same component (`patchV[1]`); **five
independent perturbed optimisations reproduce D1's endpoint FD agreement to within 0.005 percentage
points.**

**G4 trivial baseline** — `shape[6]` at the deliberately wrong step `1e-8`: **112.57 %, 112.59 %,
112.88 %, 113.25 %, 113.26 %, every one sign-flipped.** D1 measured **112.6004 %**. **The instrument
can fail, and does, on all five arms.**

**G5 controls (`CLAUDE.md` rule 3)** — run against a **REAL D13 endpoint JSON**, never a synthetic
fixture, and **all five passed**:

| control | outcome |
|---|---|
| planted-zero, all 5 consumed channels | **OK** — worst residual vs plant `4.27e-17`, source md5 unchanged before and after |
| **negative** — blind reader | **REFUSED** `PLANTED_ZERO` |
| **EMPTY-SET** — `fd = {}` | **REFUSED** `FD_BLOCK_EMPTY`, `n_components_present: 0` printed |
| **SHORT-SET** — 1 of 4 gradeable | **REFUSED** `FD_TOO_FEW_GRADED`, `n_graded: 1, min_required: 3` printed |
| key-set — `CD` → `CD_final` | **REFUSED** `ENDPOINT_KEYSET` **by name**, not `KeyError` |
| planted-zero on D1 arm O's own JSON | **OK**, md5 `e63f57710cee6e2170f2e9cef39f8b2a` unchanged |

**The two set-size controls are the L-302 repair and they were exercised, not asserted.**
`curriculum_D3/d3_grade.py` returns `PASS` at 0.0000 % with zero sign flips over an **empty
component set**; D13's gate refuses on an empty or short set **by count, with the count printed**,
and the controls prove it. **All five controls were also dry-run on the HOST at ZERO COMPUTE against
D1 arm O's real endpoint JSON BEFORE the pre-registration was frozen**, so the coupling — not just
the arithmetic — was proved before any container started.

**A free cross-check fell out of that dry run:** the D13 gate, reading D1 arm O's raw JSON with a
reader D1 never used, independently re-derived **4/4 graded, worst 0.25526 %, zero sign flips** —
reproducing `curriculum_D1/RESULTS.md` §5.2's published **0.2553 %**.

**G7 image identity** — in-process `IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425` (patched) and
`nProcs : 1` on all five arms; a mismatch would have refused.

**G9 memory** — peak RSS `1.6906` … `1.6950` GiB against the registered 2.0 GiB ceiling and the
`--memory=6g --memory-swap=6g` kernel cap. **`.State.OOMKilled false` on all five.** D1 measured
`1.6964` GiB.

**G6 launch gate** — re-run as its own command before every launch; `preflight_history.txt` records
`gate=OPEN` on all eight samples, worst `MemAvailable` **26.59 GiB** against the 12 GiB floor.
**No departure was taken and none was requested.**

---

## 6. The start set

**Seed 13**, `numpy.random.default_rng(13)` PCG64, `dshape` drawn first from
`uniform(-1e-2, +1e-2, (5,8))`, `daoa` second from `uniform(-1, +1, 5)`; the **literal table in
`d13_basin.py` §1 is the authority**. The grader re-derived each arm's start vector from that table
and compared it to what the arm actually set: **exact match, zero deviation, on all five.**

**A measured bonus the design anticipated.** The pre-registration registered the generator as
**numpy 2.5.1**; the container carries **numpy 1.23.5**. The producer regenerated the table from the
seed inside the container and printed the deviation: **`max_shape_dev=4.683753e-16`,
`aoa_dev=1.687539e-14`** — float round-trip precision. **The PCG64 `uniform` stream is measured
stable across two numpy majors**, so the start set is regenerable from the seed as well as from the
literal, and the decision to make the literal the authority cost nothing and guaranteed identity.

---

## 7. Predictions scored

| registered (§8) | band | measured | score |
|---|---|---|---|
| majors per start, point **15** | **[8, 40)** | **9, 9, 10, 10, 11** | **HIT on band; point over by 1.53×** |
| per start, point **7.7 core-min** | — | **5.150 … 6.383**, mean **5.61** | **0.73×** |
| total, point **40.0 core-min** | **≤ 80.0** | **28.050** graded / **50.033** gross | **HIT on band on both figures** |
| HARD CEILING **100.0 core-min** | — | **50.033 gross** | **not approached; no run stopped by it** |
| peak RSS ceiling **2.0 GiB** | — | **1.6950** worst | **HIT** |
| per-start ceiling **25.0 core-min** | — | **6.383** worst | **HIT, by 3.9×** |

**The per-start cost anchor was excellent and the major count was not.** D1's arm O measured
**6.017 core-min**; D13's five arms measured **5.150–6.383**, bracketing it. The **15-major** point
estimate assumed a perturbed start would need materially more majors than D1's 11 to restore
feasibility; **it needed fewer — 9.8 on average** — because `findFeasibleDesign` restores the `CL`
equality by angle of attack *before* `run_driver` starts, so the optimiser never sees the
infeasibility the estimate was pricing.

---

## 8. Cost — and the estimate-versus-actual comparison (`CLAUDE.md` rule 12)

| figure | value |
|---|---|
| **GROSS, waste included** | **50.033 core-min** = **$0.042778 DERIVED, NOT MEASURED** |
| **NAMED WASTE** (attempt 1, core-pinning; §4) | **21.983 core-min**, reported separately, **never netted off** |
| **graded arms** | **28.050 core-min** = **$0.023983 DERIVED** |
| predicted point / band / ceiling | **40.0** / **≤ 80.0** / **100.0** core-min |
| **ratio, graded / predicted** | **0.7013×** |
| **ratio, gross / predicted** | **1.2508×** — inside the ≤ 80.0 band |
| stall rule | longest arm 383 wall s, nowhere near the 3600 s threshold — **gross == cleaned** for the graded arms |
| `cost_basis` | **c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED**; every dollar figure **DERIVED** (`COMPUTE_BUDGET_CHARTER.md` §5) |

**No overrun. No run was stopped by a ceiling.** Calibration row filed as **C-65** in
`docs/COST_CALIBRATION.md`.

**The price moved, as §8 registered in advance.** The curriculum's **~350 core-min / $0.30** was
struck before any compute and restated at **40.0 core-min** on D1's measured 7.000 core-min anchor.
**The restated figure was right and the struck one was 7× too high**: the item finished at 28.050
core-min of graded compute — **12.5× under the curriculum's number**.

---

## 9. What this item does NOT claim — §10 of the pre-registration, re-affirmed after the fact

1. **No toolchain-independent basin result.** PATCHED row only; the SHIPPED row was **NOT BOUGHT**
   and no measurement here bears on it.
2. **`Δ_FD` is a PROXY.** It is D1's measured **adjoint-vs-FD agreement on a gradient component**,
   reused as a tolerance on a **design vector** and an **objective**. **The `GATE FAIL` rests on this
   proxy**, and the honest statement of the finding is therefore: *the optima differ by more than the
   only endpoint-noise figure measured on this case.* A direct measurement of design-vector
   reproducibility on this case does not exist and is **not** claimed here. **The successor item
   should measure it** — repeat one start N times under identical conditions and read the spread.
3. **η was measured at the BASELINE design**, not at any of these five endpoints. The registered
   mitigation — the two-rung plateau test at each endpoint — was executed and every component passed
   it by more than an order of magnitude (worst clearance 345, requirement 5). **It remains a
   mitigation and is not upgraded into a measurement of endpoint noise.**
4. **Five starts is five starts**, at `±1.0e-2` in `shape` and `±1.0°` in AoA. Nothing here speaks to
   larger perturbations, and **this is not a claim about how many basins the problem has.**
5. **No Roache triple, no GCI.** No grid ladder was run; `CLAUDE.md` rule 5's vocabulary is not
   borrowed.
6. **The age-guard clause is `NOT EXERCISED`** (§3), and **G2's IPOPT-scalar limb is `NOT EXERCISED`**
   (§3.1). Neither is reported as passed.

---

## 10. Artifacts

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart/`:
`ledger.txt`, `preflight_history.txt`, `D13_GRADE.json`, `D13_GRADE_FROZEN_REFUSAL.txt`,
`D13_GRADE_SUPPLEMENT.txt`, `core_pinning_finding.json`, `void_arms_waste.json`,
`s{1..5}/endpoint_d13.json`, `s{1..5}/opt_IPOPT.txt`, `s{1..5}_<STAMP>.log` with `.ok.<STAMP>`
sentinels, `s{1..5}_launch.out` carrying the pre-launch `G8 OK` lines.

**Instrument identity re-verified AFTER the run against the HEAD blobs of the pre-registration
commit** — the frozen file **is** the file that ran:
`d13_basin.py` `e96d77ff53e356d67f54a4cc46338c0e`,
`d13_opt_runScript.py` `bf6500c7ef89f7f5c8be02292e274181`,
`d1_fd_endpoint.py` `7e454d2f1830a40086465d9b5c57a941` (**byte-identical to D1's frozen instrument**),
each verified identical across HEAD blob, run root and the staged arm directory.
`d13_script.diff` carries **exactly 3 hunks**, matching §9's registered count.

*Ends.*
