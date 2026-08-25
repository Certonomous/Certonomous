# D4-DEF-4 and D4-DEF-5 — two defects in the FROZEN arm-F instruments

**Status: INTERNAL LAB DEFECT NOTE. Nothing here is filed, sent or reported outside this box**
(`CLAUDE.md` rule 7). Both defects are in **this lab's own instruments**, not in DAFoam,
OpenMDAO, IPOPT or pyOptSparse upstream. No upstream defect report arises from this note.

Written by the arm-F lane, 2026-08-25, after arm F was launched and crashed. Every number below
cites an artifact still on disk.

---

## 0. One-paragraph summary

Arm F ran, and **failed in 15 wall seconds with `openmdao.core.analysis_error.AnalysisError:
Mesh quality error!`**. Triage says the crash is not a solver failure, a mesh failure, a memory
failure or a toolchain failure. **The frozen endpoint extractor hands the frozen FD producer a
design vector in DRIVER-SCALED units, and the FD producer sets it as PHYSICAL units.** For
`shape` the registered scaler is `10.0`, so arm F set the wing shape to **ten times** its
optimised deformation and destroyed the mesh. That is **D4-DEF-4**.

While triaging it, a second and independent defect surfaced in the same instrument:
`d4_major_history.json`, the file gate **G2** is registered to read for the CL-feasibility
band, is labelled per-major but **its rows are function calls, not IPOPT majors** — 125 rows
against 80 majors, and the extra rows include the pre-optimisation feasibility sweep whose
whole job is to move CL *off* target while it searches. That is **D4-DEF-5**.

**The crash is lucky, not designed, and that is the most important sentence in this note.** See
§4.

---

## 1. What ran

| item | value | artifact |
|---|---|---|
| stager | `bash d4_stage_F.sh`, rc 0, 2026-08-25T21:12:50Z | `<runroot>/F_STAGING_EVIDENCE.txt` |
| arm | `bash d4_run_arm.sh F dafoam-idwarp-rot:v1`, frozen launcher, md5 `399957c616215c8f1ae078abe2e97958` re-verified at launch | `<runroot>/F_driver.out` |
| result | **`rc = 1`, wall 15 s, 4 ranks, 1.0 core-min**; `docker inspect` (exit, OOMKilled) = **`1 false`** | `<runroot>/ledger.txt`, arm `F` row |
| image | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` — the registered **PATCHED** digest; IDWarp `.so` md5 `85f59e87253e0a71a813f64ca6e4c425` | `ledger.txt`, arm log |
| failure | `openmdao.core.analysis_error.AnalysisError: 'scenario1.coupling.solver' <class DAFoamSolver>: Error calling solve_nonlinear(), Mesh quality error!` on the **first primal**, preceded by `***Number of non-orthogonality errors: 2989.` and `***Error in face pyramids: 6090 faces are incorrectly oriented.` | `<runroot>/F_20260825T211339Z_2574215.log` |

`<runroot>` = `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin`.

**Not OOM, not a cap-stop, not contention.** `OOMKilled false` from the kernel's own record;
15 s against an enforced 1800 s timeout; `siblings_pre=[]` and `siblings_post=[]` — no other
container was live. The exit code is **1**, and prereg §7b's reserved launcher codes are
4/5/64/65, so this is not a preflight abort either: the container ran and the payload raised.

**Stage 1 of arm F SUCCEEDED.** `d4_extract_endpoint.py` wrote `d4_endpoint_dvs.json` and
`d4_major_history.json` and printed `D4_ENDPOINT_DVS_WRITTEN … n_major_rows=125 n_shape=96`.
Only stage 2, the MPI FD producer, failed. Both files exist and are the evidence below.

---

## 2. D4-DEF-4 — the endpoint is extracted in DRIVER-SCALED units and applied as PHYSICAL

### 2.1 The registered scalers

`d4_opt_runScript.py` (frozen, md5 `2906d52a5dbed2bacbaeaf85a37d3fe8`), lines 173-175, and
`U0 = 100.0` at line 24:

```
self.add_design_var("twist",  lower=-10.0, upper=10.0,          scaler=0.1)
self.add_design_var("shape",  lower=-1.0,  upper=1.0,           scaler=10.0)
self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)
```

### 2.2 The extracted endpoint violates its own bounds — which cannot happen

From `<runroot>/F/d4_endpoint_dvs.json`, written by the frozen extractor:

| DV | registered PHYSICAL bounds | extracted value | inside bounds? |
|---|---|---|---|
| `shape` (96) | `[-1, 1]` | max abs **6.0245919**, **62 of 96 components outside `[-1,1]`** | **NO** |
| `twist` (7) | `[-10, 10]` deg | max abs **0.28020223** | yes, but implausibly small |
| `patchV[0]` | **pinned, `lower = upper = U0 = 100.0`** | **10.0** | **NO** |

**`patchV[0]` is the unforgeable control.** Its lower and upper bounds are *the same number*,
`U0 = 100.0`. Its physical value at every iterate is therefore **definitionally 100.0** — no
optimiser can move it and IPOPT does not violate bound constraints. The extractor returns
**10.0**. That is exactly `100.0 × 0.1`, the registered `patchV` scaler, to all digits. There
is no second explanation available for a pinned variable.

Apply the same factor to the others and everything lands inside its bounds:

| DV | extracted (scaled) | ÷ scaler ⇒ PHYSICAL | inside bounds? |
|---|---|---|---|
| `shape` | 6.0245919 | **0.60245919** | yes, `[-1, 1]` |
| `twist` | 0.28020223 | **2.8020223 deg** | yes, `[-10, 10]`, and a sensible wing twist |
| `patchV` | `[10.0, 0.11959663]` | **`[100.0, 1.1959663]`** | yes; AoA 1.196 deg against `aoa0 = 4.0` |

### 2.3 Measured, not inferred: the history stores driver-scaled values and no flag undoes it

`d4_extract_endpoint.py` calls `h.getValues(major=True, scale=False)`, which its docstring
treats as returning physical values. Measured directly inside the registered container
(`<runroot>/d4_triage_scaling.py`, output `<runroot>/d4_triage_scaling.out`):

* **`scale=False` and `scale=True` return IDENTICAL values** — `shape` max abs
  `6.024591873823496` under both, `patchV` `[10.0, 0.1195966323219245]` under both.
* `History.getDVInfo()` shows what pyOptSparse was actually handed:
  `dvs.patchV` **lower `[10.0, 0.0]`, upper `[10.0, 1.0]`**; `dvs.shape` **lower `-10.0`**
  (96×); and **`scale` = 1.0 for every DV**.

Those are the physical bounds multiplied by the registered scalers — `[100, 0..10] × 0.1 =
[10, 0..1]`, `[-1, 1] × 10 = [-10, 10]`. **OpenMDAO's driver applies `scaler` BEFORE pyOptSparse
sees the problem**, so pyOptSparse's own scale factor is 1.0, its `scale` flag is a no-op, and
`OptView.hst` contains driver-scaled values with **no flag anywhere that converts them back**.
The `scale=False` argument in the frozen extractor is **inert**: it cannot do the thing the
instrument was written believing it does.

### 2.4 The mechanism of the crash

`d4_fd_endpoint.py` (frozen, md5 `c6112b0ec3bfdb5287345e350500f64a`) does

```
prob.set_val(key, np.array(dvs[key], dtype=float))
```

`prob.set_val` sets the **model/physical** value. So arm F set:

* `shape` to **10×** its optimum → FFD displacements ten times the optimised deformation →
  2989 non-orthogonality errors, 6090 mis-oriented face pyramids → `Mesh quality error!`
* `twist` to **0.1×** its optimum (2.80 deg → 0.280 deg)
* `patchV` to **`[10.0, 0.1196]`** — a **10 m/s freestream instead of 100 m/s** and an AoA of
  0.1196 deg instead of 1.196 deg.

**Arm O never saw this.** `grep -c "Mesh quality error"` over the full arm-O log
(`O_20260825T181237Z_2359354.log`) returns **0**, as does the non-orthogonality-error count.
Arm O drove the model through OpenMDAO in physical units throughout; only the round-trip
through `OptView.hst` introduces the factor.

### 2.5 The endpoint itself is CORRECT — the defect is purely the units

Worth stating so the repair is not over-scoped. The extractor picks the right **row**:
`_final_CD` = `0.021125978108239574`, which equals arm O's IPOPT objective
`2.1125978108239574e-02` (`<runroot>/O/opt_IPOPT.txt`) **to all 17 digits**. The last history
row IS the accepted optimum. Only its **units** are wrong.

---

## 3. D4-DEF-5 — `d4_major_history.json` rows are FUNCTION CALLS, not majors

Independent of D4-DEF-4, in the same frozen instrument, and it bears on **G2**.

* The file carries **125 rows**. `O/opt_IPOPT.txt` carries **81 iteration rows (0-80)** and
  states `Number of Iterations....: 80`.
* Every one of the 125 rows has `isMajor = 1`, and `getValues(major=False)` returns **the same
  125 rows** — the flag does not separate anything here
  (`<runroot>/d4_triage_majors.py`, `<runroot>/d4_triage_majors.out`).
* **Arithmetic proof that the rows are not majors, not an inference.** `inf_pr` is IPOPT's
  maximum violation over **all** constraints, so `|CL − 0.5| ≤ inf_pr` must hold **at every
  major**. The maximum `inf_pr` over all 81 IPOPT rows is **1.08e-02** (iteration 4). The
  worst row of `d4_major_history.json` has **`|CL − 0.5| = 2.8292e-02`**. A row whose CL
  violation **exceeds the largest constraint violation IPOPT ever recorded at a major** cannot
  be a major.
* **Where the extra rows come from.** `d4_opt_runScript.py:241` calls
  `optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"], targets=[CL_target],
  designVarsComp=[1])` **before** `prob.run_driver()`. It sweeps AoA to *find* the CL=0.5
  design. Its primals land in the same history. IPOPT line-search trials add more (the
  iteration table's trailing column sums to 101 over 81 rows).

**The consequence, and it is severe.** Band A is registered as `|CL − 0.5| ≤ 5.0e-4` **at every
major**. Graded over this file, **37 of 125 rows exceed the band** and G2 would return
**`GATE FAIL`** — *using evaluations from the routine whose entire purpose is to establish CL
feasibility before the optimisation starts, plus line-search trial points the optimiser
rejected.* **That `GATE FAIL` would have been wrong.** Band A remains **NOT ESTABLISHED**, as
`RESULTS.md` §3a already had it from the `inf_pr` bound, and **prediction P3 stays UNSCORED**.

**Band B is unaffected and is bought.** It reads the **final** row, and the final row is proved
to be the accepted optimum by the 17-digit CD match of §2.5. `|CL − 0.5| = 7.3747727758e-08`
against the band's `1.0e-5` — **PASS**, and it corroborates the independent `inf_pr` figure of
7.37e-08 in `O/opt_IPOPT.txt`.

**Planted-zero control on that reader** (`CLAUDE.md` rule 3), run before the number was
believed: planting `1.234e-03` into `CL[-1]` on disk and re-reading **through the same reader**
moves the graded number to `1.2339262523e-03`, matching the exact expectation
`|(CL[-1] − 0.5) + 1.234e-03|` to a residual of `1.28e-17` — i.e. **from inside band B to
outside it**. The count channel distinguishes 125 rows from a truncated 2. A blind reader that
ignores the path it is handed returns identical output on clean and planted inputs and is
**REFUSED**. The first run of this control **fired and refused**, because the naive expectation
`delta == PLANT` is wrong when `CL[-1] < 0.5` and the plant flips the deviation's sign; the
expectation was corrected, not the reader, and the control kept its teeth.

---

## 4. THE CRASH IS LUCKY, NOT DESIGNED — and this is the finding that matters

Nothing in D4's registered gate set was watching for a units error in the endpoint.

`shape` carries scaler **10.0**, so its corruption was a factor of ten and the mesh could not
survive it. **Had `shape`'s scaler been 1.0 — as it is for the objective and both aerodynamic
constraints — the mesh would have survived, every primal would have converged, and arm F would
have produced a complete, well-formed, plausible-looking FD table at a design point that is not
the optimum**, with `twist` 10× wrong and the freestream 10× wrong underneath it. Every count
refusal would have passed: five components requested, five rows returned, in the registered
order. G6's plant would have been seen. G6b's blind reader would have been refused. G7's four
mutations would each have raised their named refusal. **The instrument set was fully armed and
would have certified the table.**

That is precisely the shape of the D3 catastrophe recorded in prereg §7a — *"a partial plant
reads on the page exactly like a complete one"* — with the corruption moved one stage upstream,
out of the grader and into the **producer**. Every control D4 built lives downstream of
`d4_endpoint_dvs.json` and **takes that file's contents as given**. L-302 says an instrument
that cannot say "I measured nothing" will report a number it did not measure; the sibling this
note adds is: **an instrument that cannot say "I measured the wrong point" will report a number
it measured correctly at the wrong place.**

**A units error is invisible to every count-based, plant-based and order-based control in the
D4 gate set.** The registered controls check *that* five components were measured, not *where*.

---

## 5. What this does NOT establish

Named plainly, because an honest gap is worth more than a confident guess.

1. **The FD table is not measured.** No adjoint-vs-FD comparison exists at D4's endpoint. The
   bright line (`DAFOAM_CHARTER.md` §2, §9) is **not** crossed, and D4's 28.6758 % drag
   reduction remains **`BLOCKED`, not validated**. Predictions **P5, P6 and P9 stay PENDING** —
   unscored, not missed.
2. **The proposed physical values are NOT verified by a solve.** §2.2's ÷scaler column is
   arithmetic plus a bounds check plus the pinned-`patchV` control. **No primal has been run at
   the corrected design point**, so it is not yet demonstrated that the corrected vector
   reproduces `CD = 2.1125978e-02`. **That reproduction is the acceptance test any repair must
   pass, and this lane did not run it** — the instruments are frozen and this lane is not
   entitled to re-freeze them (§6).
3. **Whether the same defect affects other items in this family is NOT checked.** Any lab
   instrument reading DVs back out of a pyOptSparse history and re-applying them through
   `prob.set_val` is exposed to the same factor whenever an OpenMDAO `scaler` is not 1.0. This
   lane checked D4 only. **This is the highest-value follow-up and it is unclaimed.**
4. **The 125 rows are not fully decomposed.** 81 majors + 101 line-search trials ≠ 125 exactly;
   the feasibility sweep supplies the remainder but the exact mapping was not reconstructed. It
   is **not needed** for the finding: the `inf_pr` contradiction of §3 is decisive on its own.

---

## 6. What a repair would require — NOT taken by this lane

`d4_extract_endpoint.py` is **frozen** at md5 `ee7d3c99fd716da23779cb651961918e`
(`PREREGISTRATION.md` §9a), and `CLAUDE.md` rule 6 forbids editing a frozen file. The frozen
launcher **asserts that md5 before every launch** and aborts with code 4 if it differs, so an
edited extractor cannot run under the registered launcher at all. **The freeze is working
exactly as designed** — it is the reason this defect surfaced as a hard, dated, attributable
crash instead of a quiet number.

Therefore **arm F cannot be run correctly with the currently frozen instrument set**, and the
repair is **not this lane's to take**. It needs a decision at supervisor level about the
governed path (`VERIFICATION_CHARTER.md` §2d.1's repair exception is the clause to read), and
any repaired instrument must:

1. convert driver-scaled history values to physical by **dividing by the registered `scaler`
   read from the producer**, never by a constant copied into the extractor;
2. **assert the reconstructed physical vector lies inside the registered DV bounds** and refuse
   if not — the check that would have caught this before a single core-minute was spent;
3. **assert `patchV[0] == U0` exactly**, the pinned control, and refuse otherwise;
4. **re-run the primal at the reconstructed endpoint and require `CD` to reproduce
   `2.1125978108239574e-02`** before any FD step is taken — an endpoint that does not reproduce
   the optimum's objective is not the optimum;
5. separate **majors from function calls** in `d4_major_history.json`, or state in the file that
   it cannot, so G2 can never grade band A over feasibility-sweep points.

Items 2, 3 and 4 are each independently sufficient to have caught D4-DEF-4.

**Nothing is sent, filed or submitted. This note stays in the box** (`CLAUDE.md` rule 7).
