# VMFL046-R7 — PRE-REGISTRATION (FROZEN)

**Supersonic flow with a normal shock in a converging–diverging nozzle.**
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 155 (VMFL046)**.

> **STATUS: FROZEN 2026-09-08T18:25:56Z**, after the ansys-verification supervisor's §3 checks
> (check-1 comparator + driver diff-read; check-2 smoke triage; check-3 capability; prereg gate
> byte-identical + cost caps). **The commit that adds this file to the repository IS THE FREEZE**
> (rule 2) — its sha is recorded by the freeze report and `docs/LAB_STATE.md`; a self-referencing
> sha cannot be embedded here (it would change this file's blob). **NOTHING is launched, filed or
> sent (rule 7).** The graded run root `verification/runs/ansys_verification/VMFL046-R7/` DID NOT
> EXIST at the freeze (rule 2, §3 check 4). Gates are now closed: any departure lands only as a
> dated addendum that cannot alter a gate, threshold, cap or label (rule 2). Blob shas quoted below
> are the frozen artifact blobs, re-verified at grading against the committed tree.

> **R7 IS ONE DELIBERATE CHANGE vs R6 AND NOTHING ELSE: the INITIAL CONDITION, `0/U`
> internalField `uniform (100 0 0) → uniform (0 0 0)` — the ANSWER-BLIND START-FROM-REST.**
> The SOLVER (`rhoCentralFoam`/Kurganov), the OUTLET (`waveTransmissive lInf 0.3`), the schemes
> (`vanLeer`/`vanLeerV`, `Euler`), `maxCo 0.2`, `maxDeltaT 1e-4`, the mesh, `endTime 0.080 s`, the
> `r = 2` triple, the sampler, `DELTA_X` and every gate limb of the comparator are **carried
> from R6 BYTE-IDENTICAL** (L-487). **Nothing in the gate is widened.**

---

## 1. WHY THIS DOCUMENT EXISTS — R6 CORE-DUMPED IN STARTUP, AND R7 IS ITS STARTUP-STABILISED SUCCESSOR

VMFL046 has been run R2/R3/R4 (`rhoPimpleFoam`, reflecting outlet — hunts), R5 (`rhoPimpleFoam`,
`waveTransmissive lInf 2.0` — washed out, register #62), and R6 (`rhoCentralFoam`, `lInf 0.3` —
register **row #63**). R6's L1 **core-dumped (rc 134)** at `Time ≈ 1.864806e-4 s` with

> `FOAM FATAL ERROR: Negative initial temperature T0: -16.02 K`

from the internal-energy → temperature inversion, during the impulsive transonic startup. The
frozen R6 comparator refused (exit 2) at strict completion — `NOT A RESULT`, nothing graded.

**The R6 triage (register #63) diagnosed a GENUINE transient-startup instability (state b), not
a capability gap.** R7 is its dated fix-until-runs (§2ay) successor. The R6→R7 startup-stabilised
plan is registered in `docs/ansys_verification/FIX_SUCCESSOR_REGISTRY.md`.

---

## 2. THE LEVER — START-FROM-REST, AND WHY (the Courant/diffusion ramp was FALSIFIED first)

### 2.1 The register's proposed PRIMARY lever (Courant/diffusion ramp) is FALSIFIED

The R6→R7 registry proposed, as its PRIMARY candidate, a two-phase **startup Courant ramp with a
more-diffusive startup reconstruction** (Minmod), then a restart at the frozen `vanLeer`/`maxCo 0.2`.
An **answer-blind scratch smoke FALSIFIED it**: Phase A with `reconstruct(rho/U/T) Minmod`/`MinmodV`
(the most-diffusive shipped TVD limiter — Greenshields et al. 2010 §4.1) at **`maxCo 0.05`** (4×
tighter than R6's 0.2, 10× below the central-scheme stability limit 0.5) **still core-dumped with
negative T at `Time ≈ 1.93e-4 s`** — essentially R6's own onset (1.86e-4 s), with the Courant held
at 0.0502 throughout. **Neither more spatial diffusion nor a lower Courant moves the onset**, so the
blow-up is *not* a reconstruction overshoot and *not* a Courant runaway.

### 2.2 The root cause and the fix

The negative temperature is the **impulsive uniform IC** driving `e = rhoE/rho − ½|U|²` negative:
`U = (100 0 0)` is subsonic (M≈0.25) **everywhere** — including the divergent section that is
supersonic at steady state — against a uniform `p = 200000 Pa` mismatched to both boundary
conditions (inlet total 301325, outlet 176325). An **answer-blind scratch smoke ISOLATED the fix**:
`0/U` internalField `(100 0 0) → (0 0 0)` — **start-from-rest** — at the **FROZEN R6 config**
(`vanLeer`, `maxCo 0.2`, `p = 200000`, `T = 400`) marched cleanly: `rc 0`, **no negative-T**, `End`
reached, Courant pinned at 0.209, a **sustained stable march to 4e-3 s** (~21× the onset, ~16× below
the graded-window start 0.064 s). Greenshields' own Sod validation started **"initially at rest"** and
ran stably with these exact schemes at CFL 0.2.

A second candidate — start-from-rest **and** `p` dropped to the outlet value 176325 — **blew up at
4.3e-4 s** (a larger inlet mismatch 301325 vs 176325 is more violent), so **`0/p` is carried
byte-identical** (`p = 200000`, `lInf 0.3` preserved). The lever is EXACTLY start-from-rest, nothing else.

### 2.3 Why the lever is GATE-BLIND (the L-487/§3 anti-circularity requirement)

- **Zero velocity plants no shock, no location, no directional bias**, so it **cannot move
  `x_shock`** — the gate quantity.
- The steady shock position in a CD nozzle is **uniquely set by the frozen pressure BCs** (inlet
  total 301325 Pa, outlet 176325 Pa), and for a convergent transient the **settled plateau is
  IC-independent** (the IC affects only the path, not the answer).
- The lever was selected by an **answer-blind robustness criterion only** ("does it clear the
  1.86e-4 s onset and march stably"); **no `x_shock`, outlet Δp or Mach was read** to select it.
- It is an **initial condition**, not a scheme/Courant/window/threshold — the graded window
  (0.064–0.080 s) runs the frozen configuration unchanged.

---

## 3. THE GATE — CARRIED FORWARD FROM R6 BYTE-IDENTICAL (L-487); THE COMPARATOR IS UNCHANGED

Because R7 is a **single run at the frozen R6 configuration** (not a restart, not a scheme change),
**no gate, config OR completion limb of the comparator changes.** Verified: the comparator **never
inspects the IC velocity** (its `internalField` reads are all the *output* `T` field at `endTime`;
it grades the `controlDict` `maxCo`/`endTime`/`nPoints`, the `blockMeshDict`, `log.rhoCentralFoam`,
the centreline samples and `T`@`endTime`).

The gate quantities, all BYTE-IDENTICAL to R1–R6:

| quantity | value |
|---|---|
| primary reference `x_shock` | **1.250 m** |
| band `SHOCK_TOL` | **±5 %** (half-width 0.0625 m) |
| plateau `DELTA_X` | **6.250e-04 m** |
| `endTime` | **0.080 s** |
| `SAMPLE_DT` | **5.0e-04 s** |
| `MAXCO_GRADED` | **0.2** |
| `maxDeltaT` | **1.0e-04 s** |
| plateau window | `W = endTime/10`, two adjacent windows (`N_WINDOWS = 2`) |
| Roache triple | `r = 2`, `Fs = 1.25`, `GCI_FINE_MAX = 0.15`, `P_OBS ∈ [0.5, 2.5]` |
| plants | A / B / C1 / C2 / D (planted-zero controls, rule 3) |

**Refinement:** the `r = 2` grid triple, identical to R1–R6; sampler `nPoints = 2(NXA+NXB)+1`.

| level | axial converging | axial diverging | transverse | cells | nPoints |
|---|---|---|---|---|---|
| L1 | 40 | 120 | 20 | 3,200 | 321 |
| L2 | 80 | 240 | 40 | 12,800 | 641 |
| L3 | 160 | 480 | 80 | 51,200 | 1,281 |

**The comparator is a COMMENT-ONLY successor of R6's.**

| artifact | git blob (current disk) | note |
|---|---|---|
| **`grade_vmfl046_r7.py`** (THE GRADING PATH) | **`02113dbeaeb1cec940214178451c92c17b274b93`** | comment-only successor of `grade_vmfl046_r6.py` (`bad1408f`): `ast.dump`-equal AND tokenize-equal excluding COMMENT tokens; docstring + printed banner carried byte-identical (they read "R6" on purpose, to preserve strict AST equality); `--selftest` **70 ok / 0 FAILED** under `python3` **and** `python3 -O` |
| **model-sameness ceiling** | **`GATE REACHED`** | carried from R6 byte-identical (§21.2: viscous 2-D NS vs inviscid quasi-1D reference). The comparator contains **no `PASS` code path** |

> **THE GATE IS NOT WIDENED.** Every gate constant is byte-identical to R6. `MAXCO_GRADED` stays 0.2.

---

## 4. THE DIAGNOSTIC LOGIC — PRE-COMMITTED, BEFORE ANY GRADED RUN

R7 changes the IC and nothing else. Its outcomes are pre-committed (identical branch structure to R6 §5):

> **BRANCH (a) — THE SHOCK STANDS AND PLATEAUS.** Every level plateaus (`P1,P2,P3 ≤ DELTA_X`) and
> the Roache triple on `x_shock` is `CONVERGING`. Verdict: **`GATE REACHED`** inside the 5 % band with
> no secondary fired, else **`GATE FAIL`**. This would be VMFL046's **first graded result** — R7 is
> the first run in the lineage expected to reach the graded window at all.
>
> **BRANCH (b) — IT HUNTS.** Any level fails the plateau at `endTime`. Verdict **`NOT A RESULT`**
> (rule 5 step 1); every level's P1/P2/P3 printed. No threshold/`endTime`/`maxCo`/window widened.
>
> **BRANCH (b′) — IT WASHES OUT.** The comparator refuses (no downward `M = 1` crossing). Verdict
> **`NOT A RESULT`** (instrument refusal) — `lInf 0.3` still too weak.
>
> **BRANCH (c) — A LEVEL HITS ITS COST CAP (`rc 124`).** **`NOT A RESULT`** (budget/kill class); the
> successor re-files its estimate from this run's own logs. No cap is raised mid-flight.
>
> **BRANCH (d) — grid triple not `CONVERGING`.** **`NOT A RESULT`** (rule 5 step 2), value and both
> triples printed. **The failing level is never dropped** (L-500).

**Honest predicted verdict: PENDING / directional.** Most likely **`GATE REACHED`** *if* the anchored
outlet (`lInf 0.3`) holds a standing shock inside the ±5 % band on a `CONVERGING` triple; otherwise
`NOT A RESULT` (hunt / washout / non-CONVERGING) or `GATE FAIL` (converged-and-outside-band). **No
`PASS` is reachable.** The R2–R5 **standing-vs-hunt-vs-washout question and whether `lInf 0.3`
anchors the back-pressure remain genuinely OPEN** — R6 died in startup before the graded window, so
R7 is the first VMFL046 run expected to reach it. **This registration reads no answer.**

---

## 5. COST — BASIS CARRIED FROM R6 (rhoCentralFoam still unmeasured; rule 12, §26.3)

**Point estimate 538 core-min**, carried from R6 (R4's measured per-level actuals L1 8.07 / L2 54.67 /
L3 426.27 = 489.0 core-min × a solver-conversion factor `f_solver = 1.10`): per level **L1 8.88 /
L2 60.14 / L3 468.90**. R6 core-dumped in startup, so the true `rhoCentralFoam` `f_solver` is **still
unmeasured**; start-from-rest may modestly change the step count but stays inside `f_solver ∈ [0.7, 1.5]`,
which the ~3× caps absorb.

**CAPS (§26.2, ≥ 3× per-level):** **L1 27 / L2 181 / L3 1410**, **running total 1614** core-min.
**An overrun STOPS the run** (`rc 124`, branch (c), rule 12); enforced twice in the driver.

**`cost_basis`.** core-min = wall_s × ranks(1) ÷ 60, **measured** at completion; the estimate is R4's
measured actuals × an arithmetic `f_solver` (a MODEL, not itself measured). Dollars **derived, not
measured** at **$0.0513/core-h** (c7a.4xlarge, owner-stated; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER §5`): point estimate **538 core-min → $0.460 derived**; running cap **1614
core-min → $1.380 derived**.

**Predicted-vs-actual row OWED at completion** (rule 12): a `docs/COST_CALIBRATION.md` row comparing
this 538-core-min estimate against R7's graded actual and **measuring the true `rhoCentralFoam`
`f_solver` against the assumed 1.10** (still owed from R6's crash).

**Answer-blind smoke cost (already spent, scratch):** the startup smokes were L1-only, ~0.017–0.083
core-min each (a few seconds' wall); waste 0.000 — they bought the falsification of the ramp lever and
the isolation of start-from-rest.

---

## 6. PARITY — PROVED FROM THE BYTES (R7 vs R6)

Per-file `git hash-object`, `cases/ansys_verification/VMFL046-R7/case` vs
`cases/ansys_verification/VMFL046-R6/case`:

- **NINE inputs byte-identical to R6** (blobs equal): `0/T`, `0/p` (`c2393adb…`, `p=200000`, `lInf 0.3`),
  `constant/momentumTransport`, `constant/thermophysicalProperties`, `constant/turbulenceProperties`,
  `system/blockMeshDict.template`, `system/controlDict.template`, `system/fvSchemes`, `system/fvSolution`.
- **ONE input changed:** `0/U` internalField `(100 0 0) → (0 0 0)` (blob `1035057a… → c566b1c2…`). The
  `0/U` **boundaryField is byte-identical** — its patch `value` placeholders legitimately retain
  `(100 0 0)`, so the driver's `(100 0 0)` refusal is scoped to the **internalField line only**.
- **File set: 10** (unchanged from R6).

The driver `run_vmfl046_r7.sh` carries a both-directions R6-parity assert (exit 7) enforcing all of
the above and refusing to launch otherwise.

---

## 7. FILES

| what | path |
|---|---|
| this registration (DRAFT) | `cases/ansys_verification/VMFL046-R7/PREREGISTRATION.md` |
| **the grading path** (blob `02113dbe`) | `cases/ansys_verification/VMFL046-R7/grade_vmfl046_r7.py` |
| the run driver (parity-asserted vs R6, blob `4790323e`) | `cases/ansys_verification/VMFL046-R7/run_vmfl046_r7.sh` |
| case inputs (10 files) | `cases/ansys_verification/VMFL046-R7/case/` |
| predecessor, **READ-ONLY** | `cases/ansys_verification/VMFL046-R6/` · `verification/runs/ansys_verification/VMFL046-R6/` |
| method paper (filed, title-verified rule 15) | `docs/papers/verification_validation/greenshields_2010_rhocentralfoam.pdf` + `.txt` |
| frozen reference (R1, unchanged) | `cases/ansys_verification/VMFL046/quasi1d_reference.py` |
| run root (**must not exist at freeze**) | `verification/runs/ansys_verification/VMFL046-R7/` — **ABSENT** |

### 7.1 FREEZE-READINESS (for the supervisor's §3 checks)

1. **Comparator** `grade_vmfl046_r7.py` — comment-only successor of `bad1408f`: `ast.dump`-equal AND
   tokenize-equal (excl. comments); `--selftest` 70 ok / 0 FAILED under `python3` and `python3 -O`.
2. **Run driver** `run_vmfl046_r7.sh` — `bash -n` clean; both-directions R6-parity assert; sources
   its own OpenFOAM env; per-level + running caps; age guard; HEAD input-integrity pin. A driver
   SMOKE dry-run (scratch root, `endTime 1.2e-3 s`, L1) launched clean (`RUN_RC 0`, no negative-T,
   `End`, last Time 0.0012 s) — the instantiated pipeline clears the R6 startup instability.
3. **Cost** (§5) — point estimate 538 core-min; caps 27 / 181 / 1410, running 1614.

**No graded compute has been performed** — the run root
`verification/runs/ansys_verification/VMFL046-R7/` does not exist (a launch-ordering step, not a
freeze defect). This document is FROZEN; the launch is authorized separately by the supervisor
after check-4 (prereg committed before compute) against the reported freeze sha.
