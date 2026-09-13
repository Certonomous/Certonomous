# `D6R2C-ARM0-DEF-1` — the arm-0 parallelism-health instrument certifies an operating point the deliverable never visits, and two-thirds of its component count are verbatim replicates

**NOT FILED.** Internal record only. Nothing here is sent, posted, filed or reported outside this
box (`CLAUDE.md` rule 7). **This is a defect in this lab's own instrument** —
`d6r2c_arm0_gradient_health.py`, written here — **not in DAFoam, OpenMDAO, mphys, pyGeo or any
upstream project**, so **no upstream draft is owed and none is prepared.** No upstream behaviour is
alleged anywhere in this record.

**Status: REGISTERED, NOT REPAIRED.** This record names a defect and repairs nothing. The instrument
`d6r2c_arm0_gradient_health.py` is **not edited by this record** and its md5 does not move
(`21419e51dd6ee177ff79684867659fa8` at writing).

**Date:** 2026-09-13.
**Item:** `D6R2C` (`CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable`), arm `ARM0`.
**Component:** `cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_arm0_gradient_health.py`, the
`--dump` path; registered at `PREREGISTRATION.md` section 7.
**Found by:** `dafoam-supervisor`, reading the two arm-0 dumps (board block S-176).
**Mechanism established and the competing hypothesis refuted by:** a dafoam `lab-lane`, 2026-09-13,
from artefacts on disk, **running no solver**.
**Disclosed in the registration at:** `PREREGISTRATION.md` **ADDENDUM 4 §A4.1**.

**Id derivation (rule 11 — from the tail, the MAXIMUM EXISTING NUMBER, never a count).** A grep for
`D6R2C-[A-Z]+-DEF-[0-9]+` over `cases/`, `docs/`, `verification/` and `scripts/` returns **zero
hits**: the `D6R2C-*` defect series has no existing member in any sub-series. The maximum existing
number on the `D6R2C-ARM0` series is therefore **absent**, and this record takes **1**. Neighbouring
series in `cases/dafoam/ladder-a/` that were checked and are **not** extended by this record:
`D6-GRADER-DEF-{1,2}`, `D6R-GRADER-DEF-{1,2}`, `D6R-PREREG-DEF-1`, `D6RF-GUARD-DEF-1`. **No id is
reused and nothing is renumbered.**

---

## 1. WHAT IT CHANGES: NOTHING

**No gate moves. No threshold, band, cap or label moves. No verdict changes, and no verdict can be
changed by this record.**

`ARM0` is **`GATE FAIL`** and stays `GATE FAIL`: 27 of 412 components over the registered
`1.0e-4`, worst **`2.925612e-04`** at `cl04.aero_post.CL|shape[80]`, 2 ranks against 4, 0 below the
`1e-12` floor. `ARM0_VERDICT.json` (md5 `41dd8ac74d298390e6f398f058306b2e`) is not edited.

**And the verdict is not merely untouched — it is independently robust to this defect.** Of the 27
disagreeing components, **8 lie in `obj.J|shape` and `obj.J|twist`**, which are single arrays and
are structurally incapable of replication. **Discard every replicated row and the comparison is
still `GATE FAIL`** (worst in the single rows: `1.708777e-04` at `obj.J|shape[80]`). The
instrument's *decision* is right. What is wrong is **what the decision is about**.

---

## 2. THE DEFECT, BY LINE

`d6r2c_arm0_gradient_health.py --dump` execs the producer's header only —
`src[:anchor]`, where the anchor is the whole line `# OpenMDAO setup`
(`:88-98`, `:121`) — and then builds its **own** problem and takes derivatives at the model's
default design point:

```
:132  prob = om.Problem()
:133  prob.model = Top()
:134  prob.setup(mode="rev")
:136  prob.run_model()
:137  of = ["obj.J"] + ["%s.aero_post.CL" % p for p in POINTS]
:139  totals = prob.compute_totals(of=of, wrt=wrt)
```

The anchor sits at **`d6r2c_opt_runScript.py:292`**. The trim that gives the three points three
different angles of attack —

```
:529  if args.task == "run_driver":
:532      optFuncs.findFeasibleDesign(["%s.aero_post.CL" % pt for pt in POINTS], ...)
```

— sits **240 lines below it**, so `--dump` never reaches it. At the default point every scenario
carries the same trim variable:

```
:113  aoa0 = 4.0
:270  self.dvs.add_output("patchV_" + pt, val=np.array([U0, aoa0]))   # same for all three points
:267-268  shape = 0 (96 components), twist = 0 (7 components)
```

**Consequence, and it is the defect in one sentence: `cl04`, `cl05` and `cl06` are the same
operating point at arm 0, so arm 0 certifies rank agreement at `AoA = 4.0 deg`, a condition the
deliverable visits at no iteration — and 206 of its 412 graded components are replicates of the
other 206.**

---

## 3. THE EVIDENCE, MEASURED

**3.1 The three scenarios are one operating point at arm 0 — shown in the primal, not inferred.**
In `ARM0_4R_20260913T000043Z_152777.log`, all three primals converge to bit-identical final force
coefficients: `CD: 0.02772949388  CL: 0.4775877833` at lines 2310-2311, 2534-2535 and 2758-2759.
Three scenarios, one converged state to eleven significant figures.

**3.2 The dump is correct given that state.** In `ARM0_4R/arm0_totals.json` the three
`CL|shape` arrays are bit-identical (`max|diff| = 0.000000e+00`, and the same md5 of each array's
canonical JSON), as are the three `CL|twist` arrays. Identical models require identical derivatives.

**3.3 The driver is genuinely multipoint, so the defect is confined to the instrument.** Read
directly from `O_mp/OptView.hst` (sqlite, table `unnamed`, pickled values; 52 records carry
`funcsSens`): at call counter `'0'` the three trim variables are **distinct** —
`patchV_cl04 = [10.0, 0.29303834]`, `patchV_cl05 = [10.0, 0.43261269]`,
`patchV_cl06 = [10.0, 0.5941267]`, i.e. AoA **2.930 / 4.326 / 5.941 deg** at the registered
scaler 0.1 — and the three CL gradients are distinct at every record inspected:

| `funcsSens` record | AoA cl04/cl05/cl06 (deg) | max&#124;d(CL04)−d(CL05)&#124; on `shape` | cl04−cl06 | cl05−cl06 |
|---|---|---|---|---|
| #1 (rowid 8) | 2.930 / 4.326 / 5.941 | `1.928490e-03` | `4.931654e-03` | `3.274477e-03` |
| #27 (rowid 148) | 1.313 / 2.514 / 3.778 | `1.114459e-03` | `2.134883e-03` | `1.135502e-03` |
| #52 (rowid 352) | 0.577 / 1.772 / 3.038 | `1.004606e-03` | `2.901037e-03` | `1.896431e-03` |

**The deliverable is not compromised by this defect.** It is the *check* that is weaker than it
was believed to be, not the optimisation it was checking.

---

## 4. THE COMPETING HYPOTHESIS, AND WHY IT IS REFUTED

It was put to this lane that the bit-identity might be **aliasing** — one array written three
times, either by the dump writer or by a `compute_totals` call resolving one `of` list against one
scenario. **Both forms are refuted, and the refutation is recorded because an aliasing diagnosis
would send a successor hunting a bug that does not exist.**

- **Not the writer.** `:147-148` iterates OpenMDAO's returned mapping, keys each entry by the
  `(of, wrt)` tuple it was handed, and materialises a **fresh list of floats per key**
  (`[float(x) for x in np.asarray(v).flatten()]`). No binding is shared and no key is written twice.
- **Not the `compute_totals` call.** The 4-rank log records **three separate CL adjoint solves**,
  each a `Solving Linear Equation…` with its own `Computing d[CL]/d[patchV]^T * psi`, at
  `1880.26 → 1902.42 s`, `1902.92 → 1925.22 s`, `1925.43 → 1947.86 s` (lines 3121-3150), roughly
  22.3 s each. The three arrays were computed, not copied.
- **And the 2-rank dump settles it a third way:** there, `cl05` differs from `cl04` and `cl06` by
  `7.819924e-05` on `shape`. **No aliasing writer can produce a dump in which the three keys are
  not all equal.**

---

## 5. WHAT IT COSTS, STATED AS ONE NUMBER

| | |
|---|---|
| graded components (`ARM0_VERDICT.json` `n_components`) | **412** |
| distinct derivatives actually compared | **206** |
| replicated slots (`CL × {shape, twist}`, written three times) | **309 slots holding 103 derivatives** |
| non-replicable slots (`obj.J\|shape`, `obj.J\|twist`) | **103 slots holding 103 derivatives** |
| disagreeing components as graded | **27** |
| — of which in replicated rows | **19** (`cl04` and `cl06` contribute the *identical* index set `[1,64,65,72,73,80,81,88,89]`; `cl05` contributes index `4`) |
| — of which in non-replicable `obj.J` rows | **8** |
| **distinct** disagreeing components | **18 of 206** |
| operating point certified | `AoA = 4.0 deg`, **visited by the deliverable at no iteration** |
| operating points the deliverable actually runs | `2.930 / 4.326 / 5.941 deg` at x0, moving thereafter |

`"n_components": 412` in `ARM0_VERDICT.json` is a count of **graded slots** and is accurate as such.
It is **not** a count of independent derivatives, and any reader who reads it as one over-reads the
check by a factor of two. **The artefact is not edited.**

---

## 6. THE SEPARATE OPEN FINDING THIS DEFECT DOES **NOT** EXPLAIN — AND DOES NOT SETTLE

At 2 ranks, `cl04` and `cl06` are bit-identical but **`cl05` is not**: `7.819924e-05` on `shape`,
`7.656112e-07` on `twist`. Board block S-176 read this as *"the first real parallel-decomposition
signal the ladder has produced"*, on the premise of *"three bitwise-identical problems"*.

**That premise is false as stated, and this record names it.** `geometry_cl05` is **not** the same
component as `geometry_cl04` and `geometry_cl06`: at `d6r2c_opt_runScript.py:260-264` the `cl05`
geometry alone carries `nom_addThicknessConstraints2D("thickcon", …)`,
`nom_addVolumeConstraint("volcon", …)` and two `nom_add_LETEConstraint(…)`, because section 1
registers the geometric constraints on the `cl05` geometry only. **`cl05` is the one point that
differs structurally, and `cl05` is exactly the point that differs numerically at 2 ranks.** The
self-consistency argument has an uncleared confound, so the finding is **downgraded from a
demonstrated parallel defect to an open finding with a named benign candidate.** It is not
dismissed; it may not be reported as a parallel defect on this evidence.

**A measurement that narrows it, new with this record:** the difference is **already present in the
PRIMAL**, before any adjoint. Final converged values in `ARM0_2R_20260913T003347Z_188691.log` —
`cl04` (lines 2180-2181) and `cl06` (2628-2629) both `CD: 0.02773273449  CL: 0.4775871603`; `cl05`
(2404-2405) `CD: 0.02772732376  CL: 0.4775876687`. **So it is not a halo-exchange or unsummed-
boundary defect in the adjoint** — section 7's own two examples — because it is visible in the
primal's converged forces.

**`NOT MEASURED`, and named as such.** This record cannot say whether the extra constraint pointsets
perturb `x_aero` and hence the primal, and **cannot reconcile that candidate with the 4-rank result,
where the same structural difference produces bit-identity across all three points.** No solver was
run for this record. The candidate is a candidate. Settling it needs its own pre-registered item.

---

## 7. WHAT A REPAIR WOULD HAVE TO BE — **NOT APPLIED BY THIS RECORD**

Recorded so a successor does not have to re-derive it, and **explicitly not done here**: repairing
the instrument now would be editing a gate's specification after seeing its output, which is what
this item has already refused twice.

1. **The operating point must be registered.** Section 7 registers the eight `(of, wrt)` pairs and
   the tolerance; it **never registers the condition the comparison is taken at**. A successor
   registration owes the trimmed condition **frozen before it runs** — either by having `--dump`
   run the trim, or by seeding the three `patchV` values from a frozen `d6r2c_x0.json`.
2. **The component count must be reported as distinct derivatives**, with replicates named, so
   `n_components` cannot be read as discriminating power it does not have.
3. **The selftest must drive the producer.** `--selftest` exercises `--compare` over synthetic
   dumps only; it is why `--dump` reached a production chain having never executed once
   (ADDENDUM 5 of the instrument's own docstring). A selftest that drives the grader and not the
   producer is not a selftest of the instrument, and this defect — invisible to `--compare` by
   construction — is a second instance of the same blind spot.

**None of 1-3 is applied.** `d6r2c_arm0_gradient_health.py` is unedited; its md5 is unchanged.
