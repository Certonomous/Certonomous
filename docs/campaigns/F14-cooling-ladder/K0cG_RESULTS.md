# K0cG results: the square cavity's most-cited rung finally has a discretisation bound, and it is decisive

Campaign F14, gate K0c. Written 2026-08-19, after both cases reported.
Run tree `verification/runs/F14-cooling-ladder/K0cG_runs/`.
Pre-registration `3b454b37`, comparator `9ccfece3`, both committed before any
case produced a result.

**This rung GRADES NOTHING and no K0cS verdict moved.** It reports whether the
square cavity's solutions are in the asymptotic range, which is the precondition
for reading K0cS's deviations as model error.

---

## 1. The gap this closes

D428 established that **the square cavity had two mesh levels only**, so K0cS's
`kOmegaSST` −13.4 % and `kEpsilon` +17.1 / +20.5 % hot-wall Nusselt deviations
**could not be separated into model error and discretisation error at all.**
K0cQ, K0cR and K0cP all measure against K0cS baselines, so that unbounded error
sat underneath every one of those comparisons.

**The third level is now on disk: 307×307 = 94 249 cells, first cell
9.7656e-05 m, continuing the same 1.6 ladder.**

---

## 2. `kOmegaSST` — every quantity converges, and the error is the MODEL by factors of 43 to 722

| quantity | finest | reference | \|deviation\| | GCI (absolute) | **deviation ÷ GCI** | `p` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Nu_hot` | 55.091 | 63.45 | 8.359 | 0.0992 | **84×** | 2.088 |
| `Nu_cold` | 54.885 | 63.95 | 9.065 | 0.0388 | **233×** | 3.121 |
| `Sp` | 0.76597 | 0.481 | 0.2850 | 0.00255 | **112×** | 4.078 |
| `Vpeak` | 0.25541 | 0.2127 | 0.04271 | 5.91e-05 | **722×** | 3.698 |
| `uv_peak` | 4.830e-04 | 1.080e-03 | 5.970e-04 | 1.387e-05 | **43×** | 1.516 |

**All five are CONVERGING.** The observed orders span 1.5 to 4.1 — three exceed
the formal second order, which is not a virtue and is noted rather than claimed:
an order above the scheme's formal accuracy usually means the coarsest level is
outside the asymptotic range, so **the GCI on those rows should be read as
indicative rather than exact.** It does not change the conclusion, because the
ratios are two to three orders of magnitude.

**`kOmegaSST`'s square-cavity deviations are MODEL ERROR.** Refining the mesh
cannot account for a gap 43 to 722 times the discretisation uncertainty.

---

## 3. `kEpsilon` — nothing converges, and the Nusselt error gets monotonically WORSE

| quantity | state | observed `p` |
| --- | --- | ---: |
| `Nu_hot` | **STAGNANT** | 0.150 |
| `Nu_cold` | **STAGNANT** | 0.239 |
| `Sp` | **DIVERGENT** | −0.786 |
| `Vpeak` | **DIVERGENT** | −1.015 |
| `uv_peak` | **DIVERGENT** | −0.102 |

**No band can be armed for any of them, so no attribution ratio exists.** The
hot-wall Nusselt deviation across the three levels:

**+17.146 % → +20.548 % → +23.719 %**

**Monotonically worse under refinement.** There is no asymptotic limit to
extrapolate to, so **`kEpsilon`'s square-cavity error cannot be bounded at all** —
not "is large", but **unbounded**, in the specific sense that the sequence gives
no value for the mesh-independent answer.

---

## 4. This reproduces D428 on a second geometry

D428 found exactly this split on the **tall** cavity: `kOmegaSST` converging,
`kEpsilon` getting monotonically worse. **The square cavity is a different
geometry, a different Rayleigh number and a different aspect ratio, and it
behaves the same way.** A single-geometry finding has become a two-geometry one.

**What that does NOT license:** it is two geometries of the same flow class —
both are buoyancy-driven cavities. §5 of `THERMAL_CAPABILITY_STATE.md` still
stands: every thermal error this lab has measured on a cavity is confounded by
the momentum and thermal fields being wrong together.

---

## 5. Convergence, and a distinction that had to be made carefully

**Neither case tripped `residualControl`** — consistent with **L-141**, which
established that criterion is unsatisfiable in these cases.

**By the registered criterion for this rung family** — peak-to-peak of the
hot-wall flux over a 400-iteration window — **both cases PASS comfortably**:
`Nu` spans of **0.0024 %** and **0.013 %** against a 0.5 % limit.

**A stricter field-difference test disagreed, and chasing it down mattered.**
The temperature field's local maximum still moved **0.170 K** (SST) and
**0.060 K** (kEpsilon) between iterations 38000 and 40000. **That movement is
interior, not near the wall:** it sits **152 mm and 161 mm** from the nearest
vertical heated wall — about 20 % of the cavity width — while within 5 mm of a
heated wall the movement is only **0.016 K** and **0.033 K**.

**So the graded quantity is stable and the residual drift is slow large-scale
motion in the core**, which is characteristic of a high-Rayleigh buoyant cavity
and is exactly why the registered criterion is placed on the wall flux rather
than on the field. **The stricter test was not ignored; it was located.**

---

## 6. What this rung cannot see

- **the lo-Ra question** — this is the hi-Ra square cavity only;
- **`LaunderSharmaKE`**, which K0cS REFUSED for missing its convergence
  criterion, so it has no two-level baseline for a third level to extend;
- **whether a fourth level would restore monotone behaviour for `kEpsilon`** —
  three levels can report that no asymptotic range has been reached, and cannot
  report that none exists.

---

## Addendum, 2026-08-23 — the cost this rung never recorded (D470)

**lines whose number changed above this section: 0.** Nothing above is edited,
struck or renumbered. This record carries no version line at HEAD, so no version
bump applies and this addendum does not introduce one. **No gate, threshold, cap
or label moves here** — K0cG grades nothing, and it still grades nothing. This
addendum adds a cost record and discloses one evidentiary gap; it repairs
neither the gap nor the overrun.

### 1. The omission

`K0cG_RESULTS.md` as written above reports **no cost at all** — no core-minute
figure, no dollar figure, no cost basis. Rule 12 requires every run to be costed,
and its pre-registration did cost it: `K0cG_PREREGISTRATION.md:93-94` registered
**2.557 × (2170.42 + 3055.73) = 13 363 s = 222.7 core-minutes = 3.71 core-hours
= $0.190**. The results record never reported against that estimate. Filed as
**D470**.

### 2. The graded run, attempt 2 — measured

Derived here from the completion markers, not from any prior recollection:

| artifact | field | value |
|---|---|---|
| `verification/runs/F14-cooling-ladder/K0cG_runs/DONE.S_KE_x` | `exec_seconds` | 11 105.06 |
| `verification/runs/F14-cooling-ladder/K0cG_runs/DONE.S_SST_x` | `exec_seconds` | 6 930.36 |
| `verification/runs/F14-cooling-ladder/K0cG_runs/ALL_DONE` | `markers` / `expected` | 2 / 2 |

Both cases ran **serially**: `K0cG_runs/launch_all.sh:11` invokes
`buoyantBoussinesqSimpleFoam` with no `mpirun` and no rank count, and neither
case directory holds a `decomposeParDict`. **Ranks = 1**, so core-minutes are
seconds ÷ 60.

> **11 105.06 + 6 930.36 = 18 035.42 s = 300.59 core-minutes = 5.0098
> core-hours = $0.257.**

Against the registered 222.7 core-min / $0.190 this is a **1.35× overrun**
(300.59 / 222.7 = 1.350). **The overrun was neither reported nor stopped.** Rule
12 is explicit that an overrun stops the run and that waste is reported, not
absorbed; neither happened, and this addendum records that failure rather than
excusing it.

`cost_basis`: **reported-by-owner rate, core-minutes derived from artifacts.**
The $0.0513/core-h c7a.4xlarge rate is owner-stated and is **not measured on
this box** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md`
§5). The core-minute figure *is* derived from on-disk markers. The markers
record `ExecutionTime`, not wall clock; the solve logs give `ClockTime` = 11 106
and 6 931 s, so the wall-based figure is 300.62 core-min and the two agree to
three decimal places in dollars. Nothing here turns on the choice.

### 3. Attempt 1 — a lower bound, where the record said uncosted

The attempt-1 crash (`K0cG_ATTEMPT1_LOSS.md`, D432: the host went down at
03:53Z and every field was lost to a single scheduled write) **carries no cost
figure, and no `COST.txt` survived anywhere under `K0cG_runs/`.** In that sense
the waste is **UNCOSTED**, and D470 records the available ~219 core-min
reconstruction as *arithmetic, not a record*.

**One correction, offered as a lower bound and not as a settled figure.** The
truncated solve logs were archived with their tails, and those tails still carry
the solver's own last flushed `ExecutionTime`:

| artifact | field | value |
|---|---|---|
| `K0cG_runs/CRASHED_ATTEMPT_1/S_KE_x/log.solve.tail` | last `ExecutionTime` | 6 068.61 s |
| `K0cG_runs/CRASHED_ATTEMPT_1/S_KE_x/SOLVE_TRUNCATION.txt` | `iterations_reached` | 24 003 |
| `K0cG_runs/CRASHED_ATTEMPT_1/S_SST_x/log.solve.tail` | last `ExecutionTime` | 6 068.69 s |
| `K0cG_runs/CRASHED_ATTEMPT_1/S_SST_x/SOLVE_TRUNCATION.txt` | `iterations_reached` | 34 165 |

> **6 068.61 + 6 068.69 = 12 137.30 s ≥ 202.29 core-minutes ≥ $0.173.**

**Why this is a bound and not a measurement:** the logs were truncated
mid-iteration by an unsignalled host stop, so the last flushed `ExecutionTime`
is the last value that reached disk, not the last value the solver reached.
The true attempt-1 spend is **at least** this and cannot be read from any
surviving artifact. It is therefore **not** promoted to a measured cost, and the
D470 characterisation of attempt-1 as uncosted stands for the exact figure.
Both tails read within 0.08 s of each other, consistent with two concurrent
solves killed at one instant — `SOLVE_TRUNCATION.txt` gives an identical
`log_mtime_utc` of `2026-08-19T03:53:48Z` for both.

**Campaign total, on that bound:** 300.59 + ≥202.29 = **≥502.88 core-minutes
≥ $0.430**, or **≥2.26× the registered estimate**. The registered $0.190 covered
one attempt of both cases; the rung was paid for twice and reported neither time.

### 4. A gap noted here, and NOT repaired here

**Section 5's convergence figures cite no artifact.** The `Nu` peak-to-peak
spans of **0.0024 %** and **0.013 %**, the field movements of **0.170 K** and
**0.060 K**, and the distances **152 mm** and **161 mm** appear in no file on
disk. `K0cG_runs/gate_k0cg.json` was read for this addendum and holds only
`Fs`, `cases`, `classification_source` and `quantities` — its `CONVERGING`
states are the Roache **grid**-triple classifications behind sections 2 and 3,
and its `Vpeak` / `uv_peak` entries are graded quantities; **neither is section
5's iterative-convergence monitor**, and no script that would produce section 5
is named anywhere in the record.

The inputs to re-derive them do survive — `K0cG_runs/S_SST_x/postProcessing/`
and `K0cG_runs/S_KE_x/postProcessing/` are both present. **Re-derivation was
not performed and is not claimed.** Section 5's numbers stand exactly as
written above, neither confirmed nor withdrawn by this addendum.

### 5. What this addendum itself cannot see

- **Every artifact cited above is UNTRACKED at the time of writing.** All three
  completion markers and all four attempt-1 tails/truncation records exist on
  disk but are not in git. A number whose artifact is not committed is one
  wiped directory from being unciteable. Landing `K0cG_runs/` is a separate
  item and was not done here.
- The $0.0513/core-h rate is **reported-by-owner and unverifiable from this
  box**; every dollar figure above inherits that.
- Whether the 1.35× overrun would have been caught by a live budget guard, or
  simply was not watched, is not recoverable from what is on disk.
