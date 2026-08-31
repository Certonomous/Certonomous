# PRE-REGISTRATION — VMFL038: Falling Film Over an Inclined Plane

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — printed
p.131-132 (Overview, Test Case, Geometry, Boundary Conditions; sidecar L3509-3557).**
Sidecar title-page verified against the PDF beside it under `CLAUDE.md` rule 15 on
2026-08-31 by this lane: the sidecar's first page (`.txt` L1-14) and the PDF's page 1
both read *"Ansys Fluid Dynamics Verification Manual / ANSYS, Inc. / Southpointe /
2600 Ansys Drive / Canonsburg, PA 15317 / ansysinfo@ansys.com / Release 2026 R1 /
March 2026 / © 2026 Synopsys, Inc. and ANSYS, Inc."* Not by filename, file type or hash.

Drafted by `ansys-lane-opus48`, **2026-08-31**, for the supervisor to freeze, under
the FREEZE-CLOCK directive (Sanaa 2026-08-31T15:13Z, relayed by the
ansys-verification supervisor). This is a **frozen file** under `CLAUDE.md` rule 6 from
the moment its commit lands: departures are dated addenda at the foot, never edits
above.

**FIRST REGISTRATION OF THIS CASE.** VMFL038 has **no** row in
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` (`grep -c VMFL038`
returns **0** at 2026-08-31T15:13:36Z) and no prior VMFL038 case directory,
comparator, launcher or graded run root has ever existed. It supersedes nothing.

---

## 0. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

**THE GRADED SOLVER HAS NOT STARTED. The gate, the band, the GCI ceiling, the mesh
family, the cap and the named outcomes below are predictions — the entire evidentiary
content of this document.**

Checked at **2026-08-31T15:13:36Z**, and stated so a reader can re-run each check:

| condition | how it was checked | result |
|---|---|---|
| the graded run root does not exist | `test -e verification/runs/ansys_verification/VMFL038` | **ABSENT** |
| it is absent from the runs tree listing | `ls verification/runs/ansys_verification/` — VMFL038 not among the entries | **absent** |
| the register carries no VMFL038 row | `grep -c VMFL038` on the register | **0** |
| this case directory holds no `0/` or numeric time directory | the case directory holds only `case/`, this file, the comparator, the launcher and the defect note | **no answer on disk** |

**A FEASIBILITY SOLVE EXISTS IN SCRATCH, AND IT IS DISCLOSED HERE RATHER THAN HIDDEN.**
Under the FREEZE-CLOCK directive an L1 (Ny=40) feasibility solve was run **in the
scratchpad, outside `verification/runs/`**, before this freeze. **It did NOT set, move
or inform the gate value or the band**: `tau_w` was **not** computed from it (that is
forbidden — it is the gate quantity), and `TOL = 2 %` is a-priori and was fixed by the
supervisor before any VMFL038 field existed anywhere. What the feasibility solve DID
inform is the **completion-clause mechanics** (§6): it established that
`residualControl` must be on `p` only, because the transverse velocity `Uy` is
machine-zero (`max|Uy| = 3.4e-12 m/s`) and its normalised residual is a 0/0 artifact
that floors near `1e-3`. A completion clause is not a gate value; the freeze's
evidentiary content — that the gate could not be fitted to the answer — is intact,
because the gate is derived from the manual (§2) and the band predates every field.
The feasibility solve also confirmed, as a diagnostic, that the **velocity field is
machine-exact** (`max|Ux| = 0.196200` = the analytic `u_max`), which is the evidence
that RULING 1 (gate on wall shear, not velocity) was necessary.

**Amendments before the first GRADED compute are legal and must restate this condition
and how it was checked, naming the run directory that does not exist. After the first
graded compute the gates close: dated addenda only, none altering a gate, threshold,
band, cap or ceiling.**

---

## 1. THE TEN-LINE FORM

```
1.  CASE       : VMFL038 -- Falling film over an inclined plane, manual p.131-132.
                 Solver = simpleFoam (OpenFOAM v2606), steady incompressible laminar,
                 2-D planar (empty front/back), SINGLE-PHASE, GRAVITY-OFF,
                 PRESSURE-DRIVEN. Film delta=0.01 m, plane length L=0.18 m.
2.  REFERENCE  : tau_w = 39.24 Pa -- PHYSICAL wall shear stress on the inclined plane.
                 ANALYTICAL, closed form: Bird, Stewart & Lightfoot, Transport
                 Phenomena, p.45 (the manual's OWN cited Reference). An exact solution
                 of the SAME laminar constant-property Navier-Stokes the solver
                 discretises -> model-form error zero by construction -> PASS-capable.
3.  GATE VALUE : DERIVED, two independent routes agreeing exactly (RULING 1):
                 tau_w = mu*2*u_max/delta = 1*2*0.1962/0.01 = 39.24 Pa
                 tau_w = (dp/L)*delta     = 3924*0.01        = 39.24 Pa
                 Ansys reports a velocity profile (Fig .38.2); no Ansys tau_w is quoted
                 and none is used. CONTEXT never enters the gate.
4.  CEILING    : PASS (analytical reference of the solved model; CHARTER sec.11.1).
5.  GATE       : |tau_w - 39.24| / 39.24 <= 0.02 at the FINEST level L3,
                 AND a CONVERGING Roache triple on tau_w (CLAUDE.md rule 5),
                 AND fine-grid GCI <= GCI_MAX = 0.02 (RULING 4).
6.  DIAGNOSTIC : velocity is NOT gated (RULING 1): u_max=0.1962, u_bar=0.1308 m/s,
                 full-profile RMS vs 0.1962*(1-(y/0.01)^2), and whether it is
                 machine-exact -- all reported, none gated.
7.  FAMILY     : film-normal triple, r=2, Ny = 40 / 80 / 160; Nx FIXED at 180.
                 Fs=1.25. Roache on tau_w at the fully-developed wall window.
8.  COMPLETION : CLAUDE.md rule 4 in full, with the age guard, adapted for a
                 residualControl { p 1e-10 }-terminated steady solve (sec.6): last
                 Time STRICTLY LESS THAN endTime, plus the final Ux initial residual
                 below ITER_RES_FLOOR. Comparator REFUSES (exit 2) on any failed clause.
9.  CONTROLS   : planted zero, two stages, on the wall-shear channel, FIRED AT ALL
                 THREE LEVELS (sec.8); cardinality guard on every read; numeric time
                 dir; AST guard (0 asserts); wall-shear uniformity refusal.
10. COST       : ESTIMATE 6 core-min, RANKS=1. CAP 15 core-min, RUNNING TOTAL across
                 the three solves. Overrun STOPS the run (rule 12). cost_basis
                 $0.0513/core-h, reported-by-owner; $ derived. 15 core-min = $0.0128.
```

---

## 2. THE CASE, DERIVED FROM THE MANUAL (RULING 2)

Manual p.131, quoted for the load-bearing numbers:

> *"Laminar flow of a fluid over an inclined plane, driven by the pressure difference
> due to gravity head is modeled. The flow channel is inclined at an angle β = 30° with
> the horizontal direction."* Material: **density 800 kg/m3, viscosity 1 kg/m-s**.
> Geometry: **1 m X 18 m**, angle 30°. BCs: **gauge pressure at inlet 0 N/m2, outlet
> -706.32 N/m2**.

**THE PHYSICS IS SINGLE-PHASE, LAMINAR, GRAVITY-OFF, PRESSURE-DRIVEN.** Physics/Models
reads *"Laminar Flow"*; the driving head is imposed ENTIRELY as the outlet gauge
pressure (gravity off). The free surface is a **zero-shear boundary** (`symmetryPlane`),
NOT a VOF interface; there is **no VOF and no wall-film model** here, despite any
`_film` naming in the archive. Solver: steady `simpleFoam`, laminar, 2-D planar with
`empty` front/back.

**THE GEOMETRY IS DERIVED FROM THE MANUAL'S OWN PRINTED NUMBERS, in this order
(RULING 2), and the archive is corroboration only:**

| step | identity | value |
|---|---|---|
| L | `Delta_p / (rho*g*sin(beta))` = `706.32 / (800*9.81*sin30)` | **0.18 m** |
| check | `rho*g*sin(beta)*L` reproduces the printed outlet gauge | **706.32 N/m2** exactly |
| delta | `L / 18` from the printed **1:18** aspect ratio | **0.01 m** |
| dp/L | `Delta_p / L` = `rho*g*sin(beta)` (two routes agree) | **3924 Pa/m** |
| u_max | `(dp/L)*delta^2/(2 mu)` | **0.1962 m/s** |
| tau_w | `(dp/L)*delta` = `mu*2*u_max/delta` | **39.24 Pa** |

**THE PRINTED "1 m X 18 m" IS A UNITS ERROR — 100x the self-consistent geometry** (a
metre-for-centimetre slip), recorded as a finding in
`MANUAL_DEFECT_geometry_units.md` (NOT FILED; RULING 3). The self-consistent geometry
is used; the printed absolute dimensions are not. A useful property: **`tau_w =
Delta_p / 18` is SCALE-INVARIANT under the units error** (it depends only on the
correctly-printed outlet gauge and aspect ratio), so the gate is robust to the defect,
while `u_max` would be off 100x — one more reason the gate is wall shear, not velocity.

**THE ARCHIVE WAS NOT USED AS A SOURCE.** `VMFL038_film-exp.csv` (Ansys's plotted
analytical target) and any `.wbpz` are cited as **independent corroboration only** and
are **never** the source of any registered number — a setup input may come from the
archive, a gate value may not, ever. Neither archive copy is written to, moved or
deleted by this case.

**Kinematic conversion, since simpleFoam is incompressible.** `nu = mu/rho = 1/800 =
0.00125 m2/s`. Outlet kinematic pressure `p = -706.32/800 = -0.882900 m2/s2`. simpleFoam's
`wallShearStress` is KINEMATIC (m2/s2); the comparator multiplies by `rho = 800` to
recover physical Pa (§5, §9).

---

## 3. THE REFERENCE TIER — ANALYTICAL, AND WHY `PASS` IS AVAILABLE

**Reference kind: ANALYTICAL.** Bird, Stewart & Lightfoot (p.45) reduce the steady,
fully-developed, unidirectional, laminar, constant-property incompressible
Navier-Stokes exactly to `mu d2u/dy2 = dp/dz = const`, integrated to a parabola, from
which `tau_w = (dp/L)*delta` follows in closed form. **This is an exact solution OF THE
SAME CONTINUUM MODEL the solver discretises, from a NAMED PRIMARY REFERENCE.**

Therefore model-form error is **zero by construction**, and per
`ANSYS_VERIFICATION_CHARTER` §11.1 and `VERIFICATION_CHARTER` §2h.4 condition 1
(*"the exact or manufactured solution of the same continuum model the solver
discretises. Not an experiment, not a correlation, not a different model"*), **`PASS`
is available on a CONVERGING triple**. The ceiling is hard-coded `TIER_CEILING = "PASS"`
in `grade_vmfl038.py`; the sole limb is the physics limb.

This is **not** the experimental/continuum tier that caps VMFL063 and VMFL069 at
`GATE REACHED`. It is not a benchmark, not a digitised figure, not a correlation.

---

## 4. THE MESH FAMILY AND THE ROACHE TRIPLE

2-D planar, all-hex, single block, `blockMesh` from
`case/system/blockMeshDict.template`. **UNIFORM grading (1 1 1)** — a uniform mesh is
load-bearing (§1 line 6 / RULING 1): on it a 2nd-order FV scheme reproduces the exact
parabolic velocity to round-off. Origin at the inlet on the plane: `x` streamwise
(0 -> L=0.18 m), `y` film-normal (0 = the no-slip plane `wall`, delta=0.01 m = the
zero-shear `freeSurface`), `z` a 1-cell span (empty).

Boundaries: `inlet` (`patch`, p fixedValue 0, U zeroGradient), `outlet` (`patch`, p
fixedValue -0.882900, U zeroGradient), `wall` (`wall`, no-slip, y=0 — **the graded
surface**), `freeSurface` (`symmetryPlane`, y=delta — zero shear), `frontAndBack`
(`empty`).

### The three levels, r = 2, FILM-NORMAL ONLY

| level | Nx (fixed) | Ny | total cells | dy off the wall |
|---|---|---|---|---|
| **L1** | 180 | 40 | 7 200 | 2.5e-4 m |
| **L2** | 180 | 80 | 14 400 | 1.25e-4 m |
| **L3** | 180 | 160 | 28 800 | 6.25e-5 m |

**WHY ONLY Ny REFINES, DISCLOSED BEFORE THE FREEZE.** The wall-shear truncation error
lives in the **film-normal** direction: OpenFOAM computes the wall shear from a
one-sided near-wall gradient `snGrad(U_x) = u(dy/2)/(dy/2)`, whose leading error is
`O(dy)` and depends on `dy` alone. The streamwise resolution does not affect the
fully-developed wall shear (uniform along `x`). So the representative mesh parameter for
this functional is the film-normal spacing `dy`, which halves at exactly `r = 2` per
level; `Nx` is held FIXED at 180 so the triple isolates the film-normal truncation. This
is a legitimate systematic refinement for a functional whose discretisation error is a
function of `dy` only; it is stated rather than glossed.

### The triple, and rule 5

- Functional: **`tau_w` (mean physical wall shear in the developed window)**, per level.
- `roache(f_L1, f_L2, f_L3)` with `r=2.0`, **`Fs=1.25`**, observed-order floor
  `P_MIN=0.05`, and a **round-off floor** `EXACT_REL = 1e-8` (RULING 5).
- A triple that is not `CONVERGING` makes the row `NOT A RESULT`, whatever the value
  (`DIVERGENT`, `OSCILLATORY`, `STAGNANT`, `EXACT`, or `p < P_MIN`). **No GCI is quoted
  in any non-CONVERGING state.** Rule 5 is ONE-WAY.

---

## 5. THE GATE

```
tau_w = RHO * mean over the fully-developed wall window [0.09, 0.18] m of
        |kinematic wallShearStress_x| on the `wall` patch          [physical Pa]
GATE:  |tau_w - 39.24| / 39.24 <= 0.02   at the finest level L3
AND    the Roache triple on tau_w is CONVERGING
AND    the fine-grid GCI <= GCI_MAX = 0.02
```

**THE BAND, A-PRIORI (RULING 4).** `TOL = 0.02` (2 %, relative) is fixed a-priori from
boundary-gradient truncation on a resolved film, by the supervisor, **before any
VMFL038 field existed**. It is NOT set from any probe or run — a run that measured
`tau_w` convergence would be computing the gate quantity, which is the unregistered-run
failure this team refuses. It is wider than the near-wall first-order truncation the
family will resolve (predicted L3 deviation is a fraction of a percent), and it is not
tighter than the two-significant-figure reference `39.24` can support.

**THE GCI CEILING, A NAMED OUTCOME (RULING 4).** `GCI_MAX = 0.02` is registered BESIDE
the tolerance. A CONVERGING triple whose value sits inside the band but whose fine-grid
GCI **exceeds** `GCI_MAX` is **`NOT A RESULT`, not `PASS`** — the discretisation
uncertainty is larger than the band it must sit inside, so a PASS cannot be certified.
This is the instrument fix bought twice already (VMFL063 GCI 120.62 %, VMFL069-R2 GCI
145.91 %): **a GCI larger than the band it qualifies does not ride silently inside a
PASS.** The rule is REFUSE-to-`NOT A RESULT`, and it is stated here as the chosen
disposition. Rule 5 permits the gate to turn a would-be PASS into `NOT A RESULT`.

**THE KINEMATIC->PHYSICAL CONVERSION, ASSUMED AND FALSIFIABLE (§9).** The comparator
reads the incompressible KINEMATIC wall shear and multiplies by `RHO = 800`. **ASSUMED:**
simpleFoam's `wallShearStress` function object reports kinematic stress (m2/s2). If it
carried physical units the gate would read 800x high and **GATE FAIL** — a named outcome,
not a silent error.

**THE DEVELOPED WINDOW.** `[0.09, 0.18] m` is the downstream half, past any entrance
effect. The comparator REFUSES if the wall shear's peak-to-peak/mean in the window
exceeds `UNIFORM_TOL = 0.05` — a not-developed flow makes the single-value gate
meaningless. This is a quality control, not the band.

---

## 6. STRICT COMPLETION (CLAUDE.md rule 4, IN FULL)

Applied at every level; the comparator **REFUSES (exit 2) rather than grading a partial
run.**

**PHYSICS-CRITICAL — each clause gates:**

1. **`rc = 0`** from `RUN_RC.<level>`, captured inside the detached subshell.
2. **An `End` line** in `log.simpleFoam` (exact name, cardinality-guarded).
3. **`SIMPLE solution converged` present.**
4. **last `Time` < `endTime`.** **DECLARED ADAPTATION of rule 4's "last == endTime"
   clause for a residualControl-terminated STEADY solve, declared HERE before compute.**
   For a steady solve `last == endTime` means it ran out of clock WITHOUT converging —
   the opposite of completion. The precedent is VMFL063 §6 clause 4 / VMFL064-R2.
5. **`residualControl` is on `p` ONLY, and the comparator INDEPENDENTLY confirms the
   streamwise momentum is settled: the final `Ux` initial residual < `ITER_RES_FLOOR =
   1e-5`.** This is a feasibility-established necessity, not an omission: `Uy` is
   machine-zero (`max|Uy| = 3.4e-12 m/s`) and its normalised residual is a 0/0 artifact
   that floors near `1e-3` and can never trip any tolerance — a run controlled on `U`
   would ALWAYS reach `endTime` and grade `NOT A RESULT` for a pure-bookkeeping reason.
   `p` is the physical driver; when `p` is converged the pressure-driven `Ux` is
   developed, and the comparator checks that `Ux` residual directly rather than on trust.
   Feasibility L1: converged in 2093 iters, final `Ux` initial residual `7.9e-7`.
6. **`ExecutionTime` count == the last `Time`.**
7. **Fields present at that time:** `U`, `p`, `wallShearStress`, `Cx`, `Cy`.
8. **The numerically-latest time directory (`key=float`) equals the log's last `Time`.**
   A disagreement refuses (the lexicographic-sort hazard, L-339).
9. **AGE GUARD.** Every field at the converged time strictly NEWER than the case's own
   `0/U`, which the launcher `touch`es LAST, immediately before the solver. The launcher
   additionally refuses to launch into a level directory already holding `0/` or a
   numeric time directory, matched by regex, never a `[0-9]*` glob.

**INFRASTRUCTURE (L-342):** `RUN_RC.<level>`, `COST.txt`. Absent -> rc `NOT MEASURED`,
disclosed, grade PROCEEDS on the physics clauses. Present and non-zero -> REFUSE.

---

## 7. COST (CLAUDE.md rule 12)

| item | value |
|---|---|
| **ranks** | 1 (serial, all three solves) |
| **ESTIMATE** | **6 core-min** total |
| **CAP** | **15 core-min, RUNNING TOTAL across L1+L2+L3** |
| `cost_basis` | c7a.4xlarge at **$0.0513/core-h**, owner-stated 2026-08-21/22 — **REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars are **DERIVED**. |
| **$ at estimate** | **$0.00513 derived** (6 core-min = 0.1 core-h) |
| **$ at cap** | **$0.01283 derived** (15 core-min = 0.25 core-h) |

**How the estimate was built.** Feasibility L1 (Ny=40, 7 200 cells) converged in
**13.4 wall-s** at RANKS=1 = 0.22 core-min. L2 (14 400 cells) and L3 (28 800 cells) cost
roughly in proportion to cells x iterations; a conservative roll-up is L1 0.22, L2 ~1,
L3 ~4 core-min -> **~5-6 core-min**, registered 6. **The cap is 15 core-min (2.5x the
estimate), and an overrun STOPS the run (rc 124); endTime is never reduced to fit a
cap.** A SCOPING PROBE IS DECLINED (RULING 6): the case costs less than the probe would
cost to design. Estimate-versus-actual calibration is OWED at completion (rule 12).

**PRE-FLIGHT SMOKE (CHARTER Amendment 1.4 Clause B, RULING 6).** The launcher's
`VMFL_SMOKE=1` mode runs L1 at endTime 10 **in scratch only** (it refuses any run root
not under a scratch path), proving the toolchain STARTS. **A smoke proves the case will
START, never that the numerics will hold** (VMFL069-R1 passed a 3-step smoke and diverged
at step 65). The feasibility solve of §0 already exercised the full L1 toolchain in
scratch (blockMesh, checkMesh Mesh OK, simpleFoam to convergence).

---

## 8. THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3)

*A zero from a reader not shown able to see a non-zero is not evidence.* Two stages, on
the wall-shear channel, **FIRED AT ALL THREE LEVELS** — not L1 only, closing the
disclosed weakness of VMFL063 row #44 and VMFL069-R2 (which fired at L1 only).

| stage | what is planted | what must happen |
|---|---|---|
| **P1a — reader sensitivity** | a SIZED offset `K_PLANT * max\|tau_kin\|` (`K_PLANT=0.05`) added, in the magnitude-INCREASING direction, to the x-component of **EVERY** `wall` face of a **COPY of the real solver bytes** (header/dimensions/other patches untouched) | every value read back **FROM DISK through the production reader** moves by exactly the plant |
| **P1b — gate-functional sensitivity** | the **same** planted file | the FULL gate functional (mean physical wall shear) must move by exactly `RHO*plant` Pa |

The plant is written **to disk** and read back through the **production reader**, not
into an in-memory list — the defect this team shipped on 2026-08-28 in two graders.
Either stage failing REFUSES (exit 2).

**AND THE CONTROL IS SHOWN ABLE TO FAIL.** `--selftest` monkeypatches the writer to a
no-op so the plant never reaches disk and checks the control then **refuses**; it also
checks the control refuses on a channel that is identically zero. A control never shown
failing is untested.

**THE AST GUARD.** `_ast_guard()` walks the file's own AST (from source, same count
under both interpreters) and REFUSES if the `ast.Assert` count is not 0 — `python3 -O`
deletes asserts (L-332). Verified at drafting: `ast.Assert` **0**, `ast.Raise` **40**.
Runs in `--selftest` AND on the grading path.

**THE CARDINALITY GUARD.** Every file read goes through `one_match()`, which REFUSES
unless the pattern matches exactly one path; `sorted(glob.glob(...))[-1]` appears
nowhere. `numeric_latest_time_dir()` sorts `key=float` and is cross-checked against the
log's last Time. `--selftest` builds `0`, `950`, `2000` and shows the numeric selector
returns `2000` while the lexicographic answer would be `950`.

**`--selftest`: 52 checks, 0 failures, rc 0 under BOTH `python3` and `python3 -O`**
(`__pycache__` cleared before each). The launcher runs both, requires equal PASS/FAIL
counts and rc and the AST marker in both outputs, and requires ten named control markers
present — so a selftest that silently stopped driving a control cannot pass the launcher.

---

## 9. ERROR BUDGET — disclosed BEFORE the freeze

**CHARTER Amendment 1.4 CLAUSE A (the axisymmetric-wedge bias) DOES NOT APPLY.** VMFL038
is 2-D planar with `empty` front/back — no wedge, no azimuthal discretisation, no
`sec(t/2)` bias. Recorded as not applying so its absence is not read as an omission.

| source | magnitude / direction | how obtained |
|---|---|---|
| **Near-wall gradient truncation** | `O(dy)`, first order, monotone; the SIGNAL the triple measures and the GCI bounds | the wall-shear reader uses a one-sided `snGrad` |
| **Kinematic->physical conversion** | **ASSUMED** simpleFoam reports kinematic wall shear; comparator multiplies by `RHO=800`. **Falsifier:** if it were physical, the gate reads 800x high -> GATE FAIL | OpenFOAM incompressible convention |
| **Iterative (streamwise)** | final `Ux` residual `< 1e-5`; iterative `tau_w` error `< ~4e-4 Pa` = `~0.001 %`, far below the band | completion clause 5 |
| **Manual units error** | the printed `1 m x 18 m` is 100x; the derived `0.01 x 0.18` is used, and `tau_w = Delta_p/18` is scale-invariant to it | `MANUAL_DEFECT_geometry_units.md` |
| **Reference resolution** | `39.24` is four significant figures; well inside the 2 % band | manual table |
| **Free-surface idealisation** | the film is modelled as a fixed-thickness zero-shear top (`symmetryPlane`), the manual's own model | manual p.131 |

**None of these widens the band. The band is 2 % and the disclosure obligation is on the
disclosure, never on the tolerance.**

---

## 10. NAMED LIVE OUTCOMES — every one can happen, each written down now

The fixed vocabulary and nothing else (`CLAUDE.md` rule 1).

| # | outcome | the condition that produces it |
|---|---|---|
| 1 | **`PASS`** | triple `CONVERGING`, L3 inside the 2 % band, fine-grid GCI <= 2 %. A credential. |
| 2 | **`GATE FAIL`** | triple `CONVERGING`, L3 **outside** the 2 % band. Includes the units-assumption falsifier (an 800x reading if the reported field were physical). A finding, recorded with its numbers. |
| 3 | **`NOT A RESULT` — triple EXACT (RULING 5)** | the coarse-to-fine `tau_w` differences both fall below the round-off floor `EXACT_REL*\|f3\| = 1e-8*\|f3\|`: the wall shear is reproduced to round-off across the family (as the velocity is), so there is nothing to refine. **FALSIFIER, stated now:** if `\|d21\|` and `\|d32\|` both drop below `~4e-7 Pa`, the triple is EXACT and the row is NOT A RESULT whatever the value. Predicted differences are `~0.06-0.12 Pa`, ~1e5x above the floor, so this is not expected — but it is registered as live, because RULING 1's whole point is that an exact solution can be too exactly reproduced to gate on. |
| 4 | **`NOT A RESULT` — GCI > GCI_MAX (RULING 4)** | triple `CONVERGING`, value inside the band, but fine-grid GCI > 2 %: the discretisation uncertainty exceeds the band and a PASS cannot be certified. |
| 5 | **`NOT A RESULT` — triple not CONVERGING** | `DIVERGENT` (R >= 1), `OSCILLATORY` (R < 0), `STAGNANT` (a near-zero difference, or `p < P_MIN`). No GCI printed. |
| 6 | **`NOT A RESULT` — the solve never converged** | no `SIMPLE solution converged`, or last `Time == endTime` (ran out of clock), or the final `Ux` residual above `ITER_RES_FLOOR`, or a non-developed (non-uniform) wall window. |
| 7 | **`NOT A RESULT` — a control did not fire** | either plant stage unseen at any level; cardinality guard matching != 1; the AST guard finding an assert. |
| 8 | **`NOT A RESULT` — completion clause failed** | missing `End`, `ExecutionTime` mismatch, a missing field, the age guard, a recorded non-zero rc, or the time-directory cross-check disagreeing. |
| 9 | **`BLOCKED`** | the toolchain is absent (no `simpleFoam`, no `blockMesh`) or `blockMesh` fails. A crash is a FINDING, not a retry. |
| 10 | **`PENDING`** | registered and not yet run — the state this document is in as it is committed. |

**THE PREDICTION, and it is the falsifiable content of this document:** the gate above
can return any of outcomes 1-9; it is not constructed so only one answer is possible.
The `--selftest` proves the gate CAN return `PASS`, `GATE FAIL`, and `NOT A RESULT` (via
EXACT and via GCI>GCI_MAX), each on an end-to-end arm. This lane declines to predict
which lands.

---

## 11. THE GRADING PATH, FROZEN

| artefact | path |
|---|---|
| pre-registration | `cases/ansys_verification/VMFL038/PREREGISTRATION.md` (this file) |
| comparator | `cases/ansys_verification/VMFL038/grade_vmfl038.py` |
| launcher | `cases/ansys_verification/VMFL038/run_vmfl038.sh` |
| manual-defect note | `cases/ansys_verification/VMFL038/MANUAL_DEFECT_geometry_units.md` (NOT FILED) |
| case inputs | `cases/ansys_verification/VMFL038/case/` — 9 files |
| graded run root | `verification/runs/ansys_verification/VMFL038/` — **does not exist at this freeze** |

**The launcher refuses to spend a core-minute unless, at launch:** this file and the
comparator on disk hash equal to their HEAD blobs; all 9 case inputs hash equal to their
own HEAD blobs; the comparator's `--selftest` is green under both interpreters with equal
PASS/FAIL counts, rc, the AST marker in both, and all ten named control markers; and each
level directory holds no `0/` and no numeric time directory. It records both blobs in
`LAUNCH_RECORD.txt` and mints a `birth_certificate.json` per level.

`grade_vmfl038.py --verify-frozen` re-hashes this file and the comparator against HEAD at
grade time and returns rc 2 on any mismatch.

**No SECTION of this registration reaches the freeze with an open gate question
(CHARTER §11.2).** Every band, ceiling, level, cap and label above is decided. The one
mechanics question the feasibility solve raised — how the case declares convergence — is
RESOLVED in §6 (p-only residualControl plus the `Ux` residual check), not deferred.

---

## 12. WHAT THIS REGISTRATION DOES NOT CLAIM

- **It is not a statement about Ansys.** This box has no Ansys solver. It is a statement
  about this lab's `simpleFoam` against Bird/Stewart/Lightfoot's analytical wall shear.
- **It does not claim the archive's setup.** The geometry is derived from the manual; the
  archive CSV is corroboration only, never a source.
- **It establishes nothing about meshes finer than L3**, nor about the streamwise
  resolution beyond Nx=180 (held fixed by design).
- **The velocity is a diagnostic, not a result.** No verdict rests on it.
- **Nothing here is sent anywhere.** Submissions are parked; the manual is proprietary
  Ansys documentation held for this lab's private use (`CLAUDE.md` rules 7 and 8).
