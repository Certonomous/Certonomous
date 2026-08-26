# VMFL017-R2 — PRE-REGISTRATION (frozen before compute; CLAUDE.md rule 2)

Transonic Flow over an RAE 2822 Airfoil. Ansys Fluid Dynamics Verification
Manual, Release 2026 R1, **p. 69**. Frozen file (rule 6): after first graded
compute, only dated addenda that cannot alter gate, threshold, cap or label.

## This is a NEW ROW citing the old, under VERIFICATION_CHARTER §6

VMFL017 **attempt 1** is `PENDING` (validation register **row #19**), frozen at
commit **`d1de064b`** with `RESULTS.md` at **`f746233a`**. **That `PENDING` stays
exactly as it is** — an honest record that the REGISTERED INSTRUMENT
(`rhoSimpleFoam`) did not converge: `FOAM FATAL ERROR: Negative initial
temperature T0` in the pressure-based solver's energy→temperature inversion at
shock formation (~150–540 iterations), reproduced at every attempt; two
principled stabilisation attempts (temperature limiting; first-order upwind with
tight relaxation) both diverged. **This was the PRINCIPAL RISK the attempt-1
pre-registration named BEFORE compute**, not a surprise, and it is neither a
solver-availability problem nor a mesh defect. The `PENDING` row is NOT removed,
NOT re-labelled.

## THE SUPERVISOR'S LADDER RULING (executed here)

**Switch the solver to `rhoCentralFoam` under this new registration.** Grounds
(the supervisor's, recorded verbatim in register row #19): a density-based,
shock-capturing scheme is the right instrument for a transonic case with an
embedded shock; a pressure-based steady solver inverting energy to temperature
across a forming shock is not. **This team has already carried a shock-capturing
case on `rhoCentralFoam` successfully — VMFL045, oblique shock over an inclined
ramp (register rows #5 and #7, `PASS`/`GATE REACHED`).** The `rhoCentralFoam`
scheme set (`fluxScheme Kurganov`, vanLeer reconstruction) is this box's proven
compressible instrument (F3 supersonic suite, VMFL051, VMFL045-R2), reused here
as SETUP KNOWLEDGE ONLY — none of those cases' gates, bands or reference values
is reused and no F3/VMFL051/VMFL045 file is touched.

## PRINCIPAL RISK re-stated for the NEW instrument (registered before compute)

`rhoCentralFoam` is **explicit and transient**, so the cost driver is the
**CFL-limited timestep integrated to a settled state, NOT an iteration count**
(this is priced on line 12 accordingly). The ONE predicted failure mode: the
transient force coefficients **do not settle to a plateau within the cap** —
either because the CFL-limited timestep makes the flow-through-to-steady
expensive, or because the near-wall explicit integration of a Re=6.5e6 turbulent
boundary layer is stiff. If it does not settle, the verdict is `NOT A RESULT`
(a non-plateaued window is refused, never averaged through), which is an honest
statement of the explicit instrument's limit at this cost, not a fabricated
number. Secondary risk: transonic **drag** is set by shock position and skin
friction and a coarse/under-settled level gives Cd far from 0.0168.

## VMFL041 — the "single solve serves both" intent, CHECKED AGAINST THE MANUAL and CORRECTED

The brief carried an intent (from register row #19) that *"VMFL017 and VMFL041
are the SAME RAE 2822 case from the SAME source … a single converged solve can
serve both."* **I checked this against the manual and it does NOT hold as
stated.** The manual gives the two cases DIFFERENT flow conditions:

| | VMFL017 (p.69) | VMFL041 (p.141) |
|---|---|---|
| angle of attack | **2.79°** | **3.19°** |
| viscosity μ | **1.983e-5** kg/m-s | **1.831e-5** kg/m-s |
| freestream spec | M=0.73, Re=6.5e6, p=43765 Pa | inlet velocity profile, avg **218 m/s** |
| gate quantity | integrated Cd, Cl | surface Cp distribution (figure) |
| turbulence | SST k-ω | SST |

These are the **corrected (2.79°) vs geometric (3.19°) angle of attack of the
same RAE 2822 Case-9 experiment** (a ~0.4° wind-tunnel-interference correction),
run at different freestream specifications and different viscosities. **A single
`rhoCentralFoam` solve at 2.79° / M=0.73 does NOT produce VMFL041's 3.19° /
218 m/s Cp distribution** — the angle of attack alone changes the surface Cp and
the shock position. **Therefore this registration is for VMFL017's conditions
ONLY.** Serving VMFL041 would require its own solve at its own AoA and freestream;
that is a separate registration and is NOT claimed here. Recorded as a
correction to the row-#19 intent so no downstream reader inherits a false
economy. (What IS shared: the RAE 2822 geometry/ordinates and the AGARD AR-138
source — reused with provenance.)

## The ten-line freeze (PREREG_TEMPLATE standard form + all four amendments)

```
1. CASE            : VMFL017-R2 — Transonic Flow over an RAE 2822 Airfoil —
                     manual p.69. Solver = rhoCentralFoam (OpenFOAM v2606),
                     kOmegaSST RAS, hePsiThermo/perfectGas, TRANSIENT explicit
                     (adjustTimeStep, maxCo), shock-capturing. 2D C-mesh,
                     characteristic far-field. NEW ROW citing attempt 1 (register
                     row #19, PENDING, commit d1de064b). NOT YET RUN;
                     verification/runs/ansys_verification/VMFL017/R2/ absent at
                     2026-08-25T22:30:00Z (checked: dir does not exist at freeze).
2. REFERENCE       : Cd = 0.0168 and Cl = 0.803. Source = P.H. Cook, M.A.
                     McDonald, M.C.P. Firmin, "Aerofoil RAE 2822 — Pressure
                     Distribution and Boundary Layer and Wake Measurements",
                     AGARD AR-138, 1979. Ansys Fluent reported Cd 0.016 (0.952),
                     Cl 0.78 (0.971); CFX Cd 0.0162 (0.9662), Cl 0.7981 (0.9339)
                     — CONTEXT ONLY, never the gate.
3. REFERENCE KIND  : measured/experimental → CAN buy P (AGARD AR-138 wind-tunnel
                     data; the manual is a public primary source).
4. TIER CEILING    : GATE REACHED. Team ceiling (Sanaa). (A measured reference
                     could in principle buy HOLDS/validation with BOTH bands met
                     at a CONVERGING finest level, but transonic drag's mesh and
                     settling sensitivity makes GATE REACHED the realistic and
                     registered ceiling.)
5. QUANTITIES      : Cd (drag) and Cl (lift) from OpenFOAM's forceCoeffs function
                     object on the 'aerofoil' patch, time-averaged over the final
                     settled window of PHYSICAL TIME. rhoInf=0.50823 kg/m3,
                     magUInf=253.4664 m/s, lRef=Aref=1 m, dragDir=(cos2.79,
                     sin2.79,0)=(0.998814,0.048685,0), liftDir=(-sin2.79,cos2.79,
                     0)=(-0.048685,0.998814,0). Forces read DIRECTLY from
                     OpenFOAM — no constructed geometry enters the gate.
6. BANDS (THE GATE): |Cd_lab − 0.0168|/0.0168 ≤ 0.10 AND |Cl_lab − 0.803|/0.803
                     ≤ 0.05, at the finest CONVERGING level. Justification (NOT
                     from a run): the manual's own Fluent is 4.8% off on Cd and
                     2.9% on Cl; transonic DRAG carries larger numerical
                     uncertainty (shock position + boundary-layer resolution) than
                     lift, so Cd gets 10% (~2x the manual's own gap + grid) and Cl
                     gets 5% (~the manual's own gap + margin). BOTH must hold.
7. LADDER          : rhoCentralFoam / kOmegaSST + characteristic far-field. Air
                     (manual p.69): molWeight 28.966, Cp 1006.43, mu 1.983e-5,
                     Pr = Cp*mu/k = 1006.43*1.983e-5/0.0242 = 0.82466 (k=0.0242).
                     energy sensibleInternalEnergy (e); fvSolution provides an
                     (h|e) energy solver (VMFL045 row #5 lesson: a viscous
                     rhoCentralFoam case needs the e entry). Mesh: birth-certified
                     ratio-2 C-mesh family from the in-repo RAE 2822 ordinates,
                     REUSED from the frozen VMFL017 attempt-1 blockMeshDicts
                     (same geometry; solver-independent). Geometry is a PUBLIC
                     reference reused with provenance; the solver result is verified.
8. DECOMPOSITION   : r=2 triple L1/L2/L3 = 23040 / 92160 / 368640 cells (mult
   SEED              1/2/4). SERIAL (RANKS=1; no RNG). TRANSIENT; endTime a
                     physical settling time (not iterations), adjustTimeStep,
                     maxCo. Single-grid if only L1 is run — verdict then single-grid.
9. PRINCIPAL RISK  : the transient force coefficients do NOT settle to a plateau
                     within the cap (explicit CFL-limited settling is the cost
                     driver, see above) -> NOT A RESULT; or a coarse/under-settled
                     level gives Cd far from 0.0168 -> GATE FAIL. The plateau
                     clause (line 13) refuses a non-settled window rather than
                     average through a transient.
10. EXPECTED ORDER : p_f ~ 1 EXPECTED — an embedded shock is a genuine
                     discontinuity; a conservative shock-capturing scheme has O(h)
                     shock-position error that pollutes the integrated forces at
                     first order (same reasoning as VMFL045). p_obs in [0.5,1.5];
                     p_obs > 2.0 SUSPICIOUSLY HIGH (flagged, not celebrated).
11. WEDGE/GEOM BIAS: N/A (2D Cartesian C-mesh, planar in z, empty frontAndBack —
                     not axisymmetric).
12. COST + CAP     : COST DRIVER IS THE CFL-LIMITED TIMESTEP TO A SETTLED STATE,
                     NOT AN ITERATION COUNT (rhoCentralFoam is explicit/transient).
                     Estimate ~800-1600 core-min TOTAL for the family is UNCERTAIN
                     for exactly this reason and is a RUNAWAY-GUARD basis, not a
                     confident point estimate; reported-by-owner (c7a.4xlarge
                     $0.0513/core-h; dollars DERIVED, not measured). PER-LEVEL caps
                     (NOT a shared drawdown): L1 300, L2 600, L3 1500 core-min;
                     each level records remaining budget AND prereg_blob at launch;
                     a disproportionate level is reported before the next launches;
                     endTime is NEVER silently reduced to fit a cap; an overrun
                     STOPS the run (rule 12).
13. CONTROLS       : grade_vmfl017_r2.py --selftest green; planted-zero
                     PLANT=7.531e-3 fires in the comparator (rule 3); strict
                     completion (End + age guard + last-time≈endTime for a
                     TRANSIENT adaptive-step solver — the VMFL045 departure form)
                     (rule 4); Roache triple gating on BOTH Cd and Cl, else
                     single-grid (rule 5); PLATEAU CLAUSE (Amendment 4, all five
                     items — fixed-or-fractional window WITH a minimum-sample
                     CANNOT_TELL refusal, a peak-to-peak growing-series rejector,
                     a null-range refusal, realised sample count recorded; CoV
                     only beside); LAUNCHER FREEZE CHECK of prereg+comparator vs
                     HEAD (Amendment 2); endTime/writeInterval assertion +
                     field-dir-at-endTime check + per-level caps (Amendment 3 +
                     the two new launcher artifacts); NO set -u.
```

## PHYSICS CONSISTENCY CHECK (carried forward from attempt 1 — PASSED)

Governing groups M and Re, from the manual's OWN inputs (p=43765 Pa, T=300 K,
M=0.73, air R=287.04 from MW=28.966, mu=1.983e-5, c=1 m): a=√(γRT)=347.2 m/s,
U=M·a=253.47 m/s, ρ=p/RT=0.5082 kg/m3, Re=ρUc/μ=**6.496e6** against the manual's
stated **6.5e6 — 0.06%**. The manual's stated inputs are self-consistent.

## FREEZE STATUS — honest disclosure (CLAUDE.md rule 16; not softened)

This document (the ladder ruling, the gate, the bands, the cost basis, the
VMFL041 correction) is frozen. The comparator `grade_vmfl017_r2.py` is committed
with `--selftest` green. **The launcher smoke test (PREREG_TEMPLATE Amendment 3
item 6 — a pre-flight run that exercises the launcher itself) is OUTSTANDING
because the box is at capacity and VMFL017-R2 is the second-priority case;** it
is registered here as the remaining gate before VMFL017-R2 may run, so no reader
mistakes a frozen document for a run-ready case. VMFL017-R2 is `NOT YET RUN`.

## Grading path (fixed at this commit) and the remaining build gate

**Committed and verifiable NOW:** the comparator
`cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py` (`--selftest` green;
forceCoeffs Cd/Cl reader, the Amendment-4 plateau clause, planted-zero, transient
strict completion, Roache-or-single-grid). This is the frozen grading path; a
launcher will verify it hashes equal to its HEAD blob before any solver starts.

**The REGISTERED REMAINING GATE before VMFL017-R2 may run** (disclosed, not
softened): the rhoCentralFoam **case inputs** (`fvSchemes` Kurganov + vanLeer;
`fvSolution` with an `(h|e)` energy solver — VMFL045 row #5 lesson; `constant/`
air `hePsiThermo/perfectGas`; `controlDict` transient + `forceCoeffs` FO;
characteristic far-field `0/` fields on the reused C-mesh) and the **launcher**
`run_vmfl017_r2.sh` (Amendment-3 six artifacts + endTime/writeInterval assertion +
field-dir-at-endTime check + per-level caps) MUST be built and MUST pass the
Amendment-3 item-6 launcher smoke test on the box. Those are not committed by this
freeze because the box is at capacity and none could be smoke-tested; committing
an unverified case as "frozen" would overclaim. Run root:
`verification/runs/ansys_verification/VMFL017/R2/`. VMFL017-R2 is `NOT YET RUN`.

---

## PRE-COMPUTE AMENDMENT 1 — 2026-08-26T16:12:19Z — comparator hardened; **the LAUNCH is BLOCKED**

**Author:** `ansys-lane-opus`. **Lines whose number changed above this section: 0** (appended
at the foot; nothing above is edited — rule 6).

### A. Legality, with the evidence (rule 2)

The run root `verification/runs/ansys_verification/VMFL017` **does not exist** at
**2026-08-26T16:12:19Z** (`ls -d` returns *No such file or directory*), so neither it nor
`.../VMFL017/R2` holds a level directory, a `RUN_RC.txt` or a `LAUNCH_RECORD.txt`. **First
compute has not happened**, so this amendment is pre-compute and the comparator may still be
hardened. **Nothing gated is touched:** the quantities (Cd, Cl), the bands (10 % / 5 %), the
references (0.0168 / 0.803), the level family, the per-level caps (300/600/1500 core-min),
RANKS = 1 and the tier ceiling label (`GATE REACHED`) are unchanged character for character.
Both changes below are **refusals**, which can only turn a would-be verdict into
`NOT A RESULT` or an exit-2, never the reverse.

### B. `assert verdict in VERDICTS` was VACUOUS under `python3 -O` — now an explicit refusal

`grade_vmfl017_r2.py:333` carried `assert verdict in VERDICTS` as the rule-1 vocabulary
guard. **Measured on this box:** `python3 -c 'assert False'` raises `AssertionError`;
`python3 -O -c 'assert False'` **raises nothing**. The guard therefore did not exist under the
interpreter this lab uses to prove its guards survive optimisation (the `554d0686` /
L-332 form — 22 test asserts found vacuous under `-O` the same night). It is replaced by
`check_vocabulary()`, an explicit `refuse()` → **exit 2**, driven by the selftest in **both**
directions (a legal verdict passes; `"looks fine"` refuses).
**`grep -nE '^\s*assert ' grade_vmfl017_r2.py` → 0**, from 1.

### C. Observed-order floor `P_MIN = 0.05`, with a planted control that DRIVES it

Per `docs/ansys_verification/FINDING_p_floor.md` §4, binding on every comparator this team
freezes. A triple whose observed order falls below `P_MIN` is **`NOT A RESULT`** and **NO GCI
is printed**. **This comparator carried the defect the FINDING names:** measured here, its
`roache()` classified the equally spaced triple `(1.0, 1.1, 1.2)` as **`CONVERGING` with
`p = 3.2e-15`** — the FINDING's own number — and would have quoted a GCI off it. It now
returns `STAGNANT`, `gci = None`.

The floor is **driven, not declared**, by `p_floor_control()`, planted into the comparator's
own `roache()` and its own (now single, shared) `verdict_for()`:

| probe | constructed | required |
|---|---|---|
| (a) equally spaced | `(1.0, 1.1, 1.2)` | `NOT A RESULT`, **no GCI**, *though both bands are met* |
| (b) below the floor | `p = 0.01`, genuinely computed | `NOT A RESULT`, **no GCI** — the probe that drives the floor itself, since (a) can be caught one step earlier by the ratio test |
| (c) above the floor | `p = 0.5` | `CONVERGING`, **GCI quoted**, `GATE REACHED` — the floor must not swallow real results |

It runs in `--selftest` **and** in `grade()` before any level is read. No `assert` carries any
of it.

**MEASURED at this amendment:** `--selftest` **20/20 PASS, 0 FAIL, exit 0, identical under
`python3` and `python3 -O`**. Three ad-hoc mutations (not added to any frozen file): defanging
`if p < P_MIN` → **exit 2 under both**; `P_MIN = 0.0` → **exit 2 under both**; defanging the
vocabulary refusal → **exit 1 under both**, no green line in any case.

**Comparator blob:** `0191d7ffa26dff86693328e38a9977d8b3db08ab` (freeze `f8871113`) →
**`97c556f4a0d07f021480c75144d1b72a811fc391`** (this amendment).

### D. **BLOCKED** — VMFL017-R2 is NOT launched, and this is why

`BLOCKED` is used here in its rule-1 sense: the lane was ordered to build
`run_vmfl017_r2.sh` **using only what this frozen pre-registration states**, and to stop
rather than guess. It stops. Four independent reasons, each sufficient:

**D.1 — `maxCo` is not registered anywhere, and it is THE driving input of this instrument.**
Line 8 says *"TRANSIENT; endTime a physical settling time (not iterations), adjustTimeStep,
maxCo"* and line 1 says *"(adjustTimeStep, maxCo)"* — **the parameter is named and its value
is never given**, in this document or in the frozen comparator. For an *explicit* solver the
Courant cap sets the timestep, and therefore sets both stability and the entire cost: at
`maxCo` 0.2 versus 0.5 the same physical `endTime` costs ~2.5× — against per-level caps of
300/600/1500 core-min this is the difference between a graded row and an rc-124 refusal. There
is no frozen predecessor to inherit it from: **VMFL017 attempt 1 was a STEADY pressure-based
`rhoSimpleFoam` run with no Courant control at all**, and this document states in as many
words that VMFL045/F3/VMFL051 are reused as *setup knowledge only*, with none of their
parameters entering this gate. `maxDeltaT` and the initial `deltaT` are unstated on the same
footing.

**D.2 — `writeInterval` is unstated, yet line 13 requires the launcher to ASSERT it.** Line 13
registers an *"endTime/writeInterval assertion"* as a required launcher artifact. A launcher
cannot assert a value the freeze never fixed. The comparator constrains the sampling only
indirectly (`PLATEAU_MIN_SAMPLES = 20` in a `WINDOW_FRAC = 0.20` window ⇒ ≥ 100 samples over
the run); it does not fix an interval.

**D.3 — This document's own REGISTERED REMAINING GATE has not been met.** Its closing section
states, unsoftened, that the `rhoCentralFoam` **case inputs** and the **launcher** *"MUST be
built and MUST pass the Amendment-3 item-6 launcher smoke test on the box"* before
VMFL017-R2 may run. **No smoke test has been run.** Launching now would breach the freeze's
own precondition — the one thing a pre-registration is for.

**D.4 — The case inputs on disk are UNCOMMITTED, i.e. NOT FROZEN.** `cases/.../VMFL017/R2/case/`
holds `0/{T,U,alphat,k,nut,omega,p}`, `constant/{thermophysicalProperties,turbulenceProperties}`
and `system/{blockMeshDict.L1,L2,L3, controlDict, fvSchemes, fvSolution}` — **none of them is
in `HEAD`** (checked path by path with `git rev-parse HEAD:<path>`; all report *not in HEAD*),
and their mtimes are **2026-08-26T04:29:54Z / 04:30:13Z**, another lane's work in progress.
Running against them would be running against unfrozen driving inputs, which rule 2 exists to
forbid, and the launch-time freeze check (which hashes disk against `HEAD`) structurally
cannot cover a path that has no `HEAD` blob. **This lane did not commit them:** they are
another agent's unfinished work, this lane cannot attest to them, and landing them would
launder unverified inputs into the freeze (rule 10; L-333 (c)).
*Recorded for whoever clears this:* the uncommitted `controlDict` carries `endTime 0.05`,
`maxCo 0.2`, `maxDeltaT 1e-5`, `deltaT 1e-9`, `writeInterval 0.05` (adjustableRunTime) and a
`forceCoeffs1` FO at `executeInterval 1e-4`; its `0/` fields match VMFL017 attempt 1's frozen
blobs byte for byte (`k` 0.024092, `omega` 61.7461, `T` 300, `p` 43765, `U` (253.16591
12.33759 0)). **Those are a peer's proposals, not a freeze**, and this amendment neither
adopts nor endorses them — it records them so the next lane knows the values exist and where.

**What clears the block, in one step:** a supervisor-cleared amendment to *this* document that
registers `maxCo`, `maxDeltaT`, `deltaT` and `writeInterval` as numbers (and confirms
`endTime = 0.05 s`, which today lives only in the comparator's `ENDTIME_PHYS`), committed
together with the case inputs, followed by the Amendment-3 item-6 launcher smoke test. All of
that is still pre-compute and therefore still legal — **until the first solver runs, and not
after.**

**Compute authority is NOT the obstacle.** Sanaa's permission at `bc0e687e` (*"anything that
leads to the lab having more runs under its belts"*) covers this launch. The obstacle is that
the freeze does not yet say what to run.

**Status:** VMFL017-R2 = `BLOCKED`. Attempt 1's register row #19 (`PENDING`) is untouched.
