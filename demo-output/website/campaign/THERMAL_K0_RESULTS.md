# Cooling ladder (campaign F14), rung K0 — RESULTS

**Date:** 2026-08-17
**Predictions:** `THERMAL_K0_PREREGISTRATION.md`, written and committed before
the first solver invocation. Read it first; this file is only the outcomes.
**Cases, scripts, logs:** `THERMAL_K0_runs/`
**Standing check built here:** `scripts/heat_balance.py`

> **CAPABILITY RUNGS. NOT RESULTS ABOUT THE WORLD.**
> K0a and K0b establish that this lab can drive a buoyancy-coupled solver and
> that the watts coming out of it balance. They are validated against **no
> published reference datum**. Nothing in this file may appear on the wall, on
> the website, in application materials or on any external surface as a result,
> and no data-center or cooling language attaches to any of it. The first rung
> permitted to make a claim about reality is **K0c, the validation gate, which
> was not in this dispatch and was not run.**

> **LABEL — RESOLVED, 2026-08-17. This campaign is F14.**
> It was dispatched as "F11", but F11 was already taken by the 2026-07-30
> lid-driven-cavity verification ladder (`F11_lid_driven_cavity_ladder.md`,
> `F11_runs/`). A concurrent agent ruled the collision while these rungs were
> running: **the cooling campaign is F14 from that commit forward, F11 continues
> to mean the lid-driven cavity ladder**, and F14 was verified unused
> repository-wide. See `docs/campaigns/F14-cooling-ladder/README.md`.
>
> `THERMAL_K0_PREREGISTRATION.md` §0 still records the collision as open and
> awaiting a ruling. **It is deliberately not edited.** A preregistration whose
> text is revised after the fact stops being a preregistration; its whole value
> is that it can be diffed against its own commit. Read its §0 as superseded by
> this line. `THERMAL_K0_*` is a physics name that never collided, so nothing
> here is renamed either.

---

## 1. What ran, and what it cost

| case | what it is | cells | wall clock |
|---|---|---:|---:|
| `K0a_heated_box` | feasibility rung, hot floor strip, cold ceiling | 400 | 1.40 s |
| `K0a_heated_box_g0` | control twin, g = 0 → pure conduction | 400 | 1.23 s |
| `K0a_heated_box_source` | control twin, planted 5.000e-03 W volumetric source | 400 | 1.43 s |
| `K0b_cavity_Ra1e5` | physics rung, differentially heated square cavity | 4096 | 31.84 s |
| `K0b_cavity_g0` | control twin, g = 0 → exact 1-D conduction | 4096 | 13.86 s |

Solver: `buoyantBoussinesqSimpleFoam`, OpenFOAM v2606, laminar, steady SIMPLE,
serial, one core throughout.

**Total: 51.65 s wall clock on one core = 0.86 core-minutes** (the clean-rebuild
run that produced the committed state; a first identical run measured 50.78 s). Post-processing
(all audits, all controls, the analysis) adds roughly another 0.5 core-minutes.
**Call it under 1.5 core-minutes for the whole rung**, against a pre-registered
estimate of under 10. Nothing was decomposed; nothing touched a queue.

**Dollar cost is not stated because I have no verified $/core-hour rate for this
machine.** The lab's own unit of account is core-minutes (`scripts/cost_calibration.py`)
and that is what is reported. Inventing a rate to make the number look precise
is the kind of undeclared figure this lab has been cleaning up all week.

---

## 2. Regime numbers — every claim below carries these

| | K0a | K0b |
|---|---|---|
| **Rayleigh Ra_L** | **9.148568e+05** | **9.999988e+04** (target 1.000e+05) |
| Grashof Gr_L | 1.294339e+06 | 1.414798e+05 |
| Prandtl Pr | 0.706814 | 0.706814 |
| L | 0.10 m | 0.10 m |
| dT (wall to wall) | 10.000000 K | 1.093066 K |
| **Richardson Ri** | **not defined independently** | **not defined independently** |
| **Boussinesq beta.dT** | **3.333333e-02** | **3.643553e-03** |
| Boussinesq status | **satisfied**, beta.dT is 30x below 1 | **satisfied**, 275x below 1 |
| max dT measured in field | 7.140344 K (cells), 10.000000 K incl. walls | 1.080672 K (cells), 1.093066 K incl. walls |

**On Richardson.** Both rungs are pure natural convection with no imposed
velocity scale. If Re is built from the buoyancy velocity sqrt(g.beta.dT.L),
then Re^2 = Gr and **Ri = Gr/Re^2 = 1 identically, for every case in this class,
whatever the physics does**. That is an identity, and per W-2 an identity cannot
gate anything, so it is reported as "not defined independently" rather than as a
number that looks like a measurement. Ri becomes real only when a forced flow is
imposed — that is the rack-row module, which is not authorized.

**On Boussinesq.** The approximation needs beta.dT << 1. It is satisfied in both
rungs by wide margins, measured from the solved fields rather than assumed. It is
**not violated here**. It would be violated at the dT a real rack exhaust runs at:
beta.dT reaches 0.1 at dT = 30 K, and a 40 K rise puts it at 0.13. **Any later
rung at data-center dT must either justify Boussinesq explicitly or move to a
compressible thermo solver.** `scripts/heat_balance.py` prints this line on every
run and says "VIOLATED" in words when beta.dT is not small.

---

## 3. Heat-balance closure

The standing check, `scripts/heat_balance.py`, computes for every boundary patch

    Q_into_domain = rho.cp.alphaEff . integral_patch (n . grad T) dA

with the surface integral taken as `areaNormalIntegrate` of `grad(T)` recomputed
in the same postProcess pass, which is exactly the solver's own `snGrad`.
Imbalance is the net leak as a percentage of the heat actually entering.

| audited case | Q in (W) | Q net (W) | **imbalance** |
|---|---:|---:|---:|
| **K0a** heated box | 1.566506568e-02 | +8.815766e-08 | **0.000563 %** |
| **K0b** cavity Ra 1e5 | 1.309110371e-03 | -4.050203e-09 | **0.000309 %** |
| K0a g=0 twin | 2.202123075e-03 | +9.017224e-07 | 0.040948 % |
| K0b g=0 twin | 2.875109417e-04 | -1.315001e-09 | 0.000457 % |
| K0a planted-source twin | 1.391321646e-02 | -5.000240e-03 | **35.938778 %** (by design) |

Both rungs closed to better than **0.001 %**. Section 6 explains why that number
is far weaker evidence than it looks, and what was built to compensate.

---

## 4. Predictions against outcomes

Every row was written before the run. "MISSED" means the gate passed but my
point estimate was wrong, which is worth recording separately from a failure.

### K0a

| id | prediction | outcome | verdict |
|---|---|---|---|
| A1 | runs to stop condition, no FPE; T < 1e-6, U < 1e-5, p_rgh < 1e-3 | ran 2000 iterations; final T 5.039e-07, Ux 3.445e-07, Uy 3.465e-07, p_rgh 7.759e-07 | **PASS** |
| A2 | Nu = Q(g on)/Q(g off) **> 1.5**, expected 2–6 | Q(g on) = 1.566506568e-02 W, Q(g off) = 2.202123075e-03 W, **Nu = 7.1136** | **PASS on the gate, point estimate MISSED HIGH** |
| A3 | g=0 twin max\|U\| < 1e-8; g-on max\|U\| in 0.02–0.5 | g=0: **0.000000000e+00 m/s exactly**; g-on: **6.760893e-02 m/s** | **PASS** |
| A4 | imbalance < 2 % | **0.000563 %** | **PASS** |

### K0b

| id | prediction | outcome | verdict |
|---|---|---|---|
| B1 | runs; T < 1e-7, U < 1e-6, p_rgh < 1e-4 | ran 4000 iterations; final T 9.593e-08, Ux 1.479e-07, Uy 1.621e-07, p_rgh 1.477e-07 | **PASS** (T marginally, at 0.96 of the limit) |
| B2 | V*_max 40–110; U*_max 20–60 | **V\* = +68.372 / -68.372**, **U\* = +34.881 / -34.882** | **PASS** |
| B3 | S > 0.3 (conduction gives exactly 0), expected 0.5–1.2 | **S = 1.0747** (central difference at centre), **1.0413** (least squares over middle 25 %) | **PASS** |
| B4 | imbalance < 0.5 % | **0.000309 %** | **PASS** |
| B5 | Nu 3–7, point estimate 4.98 from 0.28.Ra^(1/4) | **Nu = 4.5538** vs the closed-form conduction denominator | **PASS**, point estimate high by 9.4 % |
| B6 | max dT = 1.093066 K; beta.dT = 3.64e-03 | wall-to-wall 1.093066 K, cell field range 1.080672 K, beta.dT 3.643553e-03 | **PASS** |

**The plume and the stratified core are both present.** The upward jet on the
mid-height plane peaks at **x/L = 0.0703** — the fifth cell off the hot wall,
i.e. inside a wall boundary layer, which is where a natural-convection plume
belongs and not where a spurious cavity-scale circulation would put it. The
downward jet mirrors it at x/L = 0.9297, and V*_max and V*_min agree to six
figures in magnitude, which is the centro-symmetry this cavity must have and
was not imposed anywhere. The core carries a positive vertical temperature
gradient of S ≈ 1.04–1.07 against a conduction solution whose value is exactly
zero. Their absence would have been the finding; they are present.

---

## 5. Controls, with readbacks

| id | what it protects | readback | outcome |
|---|---|---|---|
| **C1** | the A3 **zero** (no gravity → no motion) | same max\|U\| extractor run on the g-ON case FIRST: returned **6.760893e-02 m/s**, so the extractor is demonstrably alive; g dictionary read back as `(0 0.0 0)` vs `(0 -9.81 0)` | **PASS** — the zero is physics, not a broken pipeline |
| **C2** | the auditor's whole chain vs **closed form** | 1-D conduction twin, Q = rho.cp.alpha.(dT/L).A = **2.874765413e-04 W**; auditor measured **2.875109417e-04 W** | **PASS, error +0.0120 %**; sign convention correct (heat enters at the hot wall), Q_cold = -Q_hot |
| **C3** | that the auditor moves on unconverged fields | imbalance at t = 10/20/50/100/500 = 0.0128 / 0.1214 / 0.0712 / 0.0362 / 0.0851 % | **PREDICTION FAILED — see §6** |
| **C3b** | that the auditor can report a **failing** balance | plant file present and names `T (4.275222401e-06 0)`; **solver log confirms** `Creating finite-volume options from "constant/fvOptions"` and `Source: plantedHeatSource`; base-case log contains 0 occurrences | **PASS** — net boundary flux **-5.000239930e-03 W** against a planted **5.000000000e-03 W**, recovery error **+0.0048 %**, imbalance **35.94 %**, auditor exit code **1** |
| **C4** | that the auditor reads properties from the case | `Pr` keyword confirmed present in the base file (0.706814) and the mutant file confirmed to DIFFER by diff before measuring | **PASS** — Q_hotWall 1.309110371e-03 → 2.618220742e-03 W, **ratio 2.000000, error +0.00000 %** |

Every plant was verified present against the thing that actually consumes it —
C3b's readback is the **solver log**, not merely the existence of the file,
because an `fvOptions` the solver never opened is a silent no-op and reads
exactly like a clean pass.

---

## 6. C3 failed its prediction, and that is the most useful thing in this rung

**Predicted:** imbalance > 20 % on an early, unconverged snapshot.
**Observed:** 0.0128 % at iteration 10, never above 0.13 % at any iteration.

**The prediction was wrong, and the reason matters.** For a **closed domain with
impermeable walls under a steady conservative discretisation**, the boundary heat
balance is very nearly an *identity*. The discrete temperature equation is solved
to tight linear tolerance at every outer iteration; `div(phi,T)` integrates to
zero over the domain because `phi` is conservative and no wall passes mass; so
the boundary conduction terms are forced to sum to zero **at every iteration,
converged or not**. The residual 1e-4 to 1e-1 % is linear-solver tolerance and
continuity-error residue, not physics.

**This is W-2 biting.** A gate whose quantity is derivable by construction cannot
gate anything. I pre-registered B4 and A4 as if a near-zero imbalance were
evidence about the solution. On a closed wall-bounded case, it is largely
evidence about the discretisation instead.

**What the check is still worth, stated precisely.** It is not worthless — it is
narrower than I claimed. It catches:

- wrong fluid properties (**C4** demonstrates this, exactly),
- wrong patch areas, wrong sign conventions, a patch omitted from the sum
  (**C2** demonstrates this against a closed-form answer),
- **any unaccounted energy source or sink** (**C3b**: 5 mW planted, 35.9 %
  imbalance, exit code 1, recovered to 0.005 %),
- and, critically, **any case with through-flow**, where the advective enthalpy
  flux is a genuinely independent contribution and the balance is *not* an
  identity.

That last point is the one that matters for everything after this rung. A rack
row has inlets, outlets and volumetric power. On such a case this check has real
teeth. On a sealed box it mostly checks itself.

**Consequence, and it is now enforced in code.** `C3b` — a planted source of
known power — replaced C3 as the auditor's positive control, and
`scripts/heat_balance.py` **refuses with exit code 2** rather than print a
number when it meets a non-wall patch (`--allow-advective`) or a non-zero
`alphat` (`--allow-turbulent`), because neither of those paths has been
calibrated against a known answer yet. A checker that returns a number for
every input teaches nobody anything.

---

## 7. Residual histories

Initial residual of the outer SIMPLE iteration. Full series in
`THERMAL_K0_runs/analysis.json`; solver logs in each case as
`log.buoyantBoussinesqSimpleFoam`.

| case | field | n | first | 10 % | 50 % | final |
|---|---|---:|---:|---:|---:|---:|
| K0a | Ux | 2000 | 1.416e-03 | 1.421e-04 | 1.496e-06 | 3.445e-07 |
| K0a | Uy | 2000 | 1.874e-17 | 1.528e-04 | 1.374e-06 | 3.465e-07 |
| K0a | T | 2000 | 1.000e+00 | 2.380e-03 | 1.257e-05 | **5.039e-07** |
| K0a | p_rgh | 2000 | 1.000e+00 | 6.993e-04 | 5.016e-06 | 7.759e-07 |
| K0a g=0 | Ux, Uy, p_rgh | 2000 | 0.000e+00 | 0.000e+00 | 0.000e+00 | **0.000e+00** |
| K0a g=0 | T | 2000 | 1.000e+00 | 1.791e-03 | 4.272e-05 | 4.757e-07 |
| K0b | Ux | 4000 | 1.000e+00 | 8.160e-04 | 3.014e-05 | 1.479e-07 |
| K0b | Uy | 4000 | 2.137e-01 | 8.850e-04 | 2.876e-05 | 1.621e-07 |
| K0b | T | 4000 | 1.000e+00 | 1.343e-03 | 1.763e-05 | **9.593e-08** |
| K0b | p_rgh | 4000 | 1.000e+00 | 2.112e-03 | 2.375e-05 | 1.477e-07 |
| K0b g=0 | T | 4000 | 1.000e+00 | 5.074e-04 | 7.446e-06 | 5.828e-08 |

**Stated plainly: neither rung reached its `residualControl` target of 1e-08.**
Both stopped at `endTime` with residuals plateaued in the 1e-07 to 1e-08 band —
the linear-solver tolerance floor, not a converging trend. The pre-registered A1
and B1 bands were met, but "converged" is the wrong word for what happened and
is not used here. A tighter stop would need tighter `fvSolution` tolerances, not
more iterations.

**The g=0 twins report Ux, Uy and p_rgh residuals of exactly 0.000e+00 for all
2000/4000 iterations.** With gravity removed there is no forcing anywhere in the
momentum equation and U never leaves zero in floating point. That is independent
corroboration of C1 from a completely different measurement — the solver log
rather than a field extremum.

---

## 8. What did not work

1. **`grad(T)` read back from disk is silently wrong at walls, by 37 %.**
   `postProcess -func '<surfaceFieldValue>' -fields '(grad(T))'` against a
   previously written `grad(T)` gives `integral n.grad(T) dA = 0.377856775` on
   the K0a hot strip. Recomputing `grad(T)` in the **same** pass gives
   **0.595629494**. The in-pass value is the correct one: a by-hand
   `(T_wall - T_cell)/d` summation over the raw `T` cell values reproduces it to
   **7 significant figures** (1.566506568e-02 W both ways). The written file's
   wall boundary field does not carry the `snGrad` correction that `fvc::grad`
   applies in memory. `scripts/heat_balance.py` therefore always recomputes
   in-pass, and the trap is documented at the top of that file with both numbers
   so nobody re-derives it the hard way.

2. **The first auditor was not idempotent and aborted on its second run.**
   Using the default result names, `mag(U)` left in the time directory by the
   first audit made the second one die with `Failed to store pointer: mag(U).
   Risk of memory leakage`. **It failed inside `run_controls.sh` and the control
   script went on to report C3b's numbers anyway — from a stale JSON left by an
   earlier successful run.** That is precisely the "a wrong figure survives the
   pass that was supposed to fix things" pattern. Two fixes: derived fields now
   use private names and are deleted after every audit, and the `--json` target
   is **deleted before** the run so a crash leaves no file rather than last
   run's numbers wearing this run's name. Verified: three consecutive audits of
   the same case now return bit-identical output.

3. **`volFieldValue` has no `maxMag` operation** in v2606 (available: none min
   max sum sumMag average volAverage volIntegrate CoV weighted*). `max` on a
   vector is componentwise and is not max|U|. Worked around with a `mag`
   function object under a private result name.

4. **`run_cases.sh` died silently on first invocation** producing zero bytes of
   output, because `set -u` was in force while the OpenFOAM `bashrc` was sourced
   and that file dereferences unset variables, which exits a non-interactive
   shell. Fixed by sourcing first and enabling `set -u` after, plus an explicit
   `command -v blockMesh` check so an unavailable environment reports itself
   instead of looking like a clean no-op.

5. **C3's prediction was wrong** — §6.

6. **A2's point estimate was wrong** — Nu came out 7.11 against an expected 2–6.
   The gate (> 1.5) was the thing under test and it passed, but the band was not
   idle decoration and it missed.

7. **244 MB of intermediate time directories** were produced and trimmed to
   14 MB, keeping only the snapshots this record actually cites. They are
   gitignored and regenerable by `run_cases.sh`.

8. **My own trim deleted every case's `0.orig/` — the tracked initial conditions
   the whole tree is rebuilt from.** The loop was written as `for d in
   $C/[0-9]*/`, and `0.orig` starts with a digit, so the glob matched it and the
   keep-test (`is it "0"?`) said no. It is the **same `[0-9]*` collision** that
   makes the repo's ignore rule
   `demo-output/website/campaign/*_runs/*/[0-9]*/` swallow `0.orig`, which is
   why `.gitignore` now carries an explicit negation for it. Caught because the
   git-visible file list had no `0.orig` entries in it — the hygiene check found
   a data-loss bug, which is an argument for running the hygiene check. The trim
   now lives inside `run_cases.sh` on a `find -regex` that cannot match a
   directory with letters in it, with the reason written above it.

   **Everything was rebuilt from `build_cases.py` and re-run from scratch after
   this, and every number in this file reproduced bit-for-bit** — Q, imbalance,
   Nu, V\*, U\*, S, the C2 error of +0.0120 %, the C3b recovery of +0.0048 % and
   the C4 ratio of 2.000000 all came back identical on the clean rebuild. That
   accident bought an end-to-end reproducibility check that was not otherwise
   planned.

9. **No dollar cost is reported.** There is no verified $/core-hour rate for
   this machine in the repository, and the lab's unit of account is
   core-minutes. Inventing a rate would have made the report look more precise
   and been a figure nobody derived.

---

## 9. Proposals — written, not run, because they are outside this authorization

Per the dispatch: work that suggests a run outside K0a/K0b gets a proposal and a
stop. These are **not** requests to proceed; they need the owner's explicit word
with a cost estimate attached.

**P1 — K0c, the validation gate. This is the blocking item.** Everything above
is a capability rung and stays off every external surface until K0c passes.
K0b was deliberately built at Ra = 1.000e5 in the standard differentially heated
square cavity configuration so that a published-benchmark comparison is a
drop-in: same geometry, same Ra, quantities already extracted (Nu, U*, V*,
stratification). **K0c is not mine and I did not run it.**

Its gate specification already exists, written by a concurrent agent while these
rungs ran: `docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`.
K0b's geometry and Ra line up with its laminar rung, and the solve is 32 s on
one core, so the compute is not the constraint — the reference sourcing is.

**Constraint carried over from that spec, and it binds B5 in this document:
three reference values are marked NOT OBTAINED** — core stratification on the
laminar rung, Nusselt number on the turbulent rung, and the Blay primary for
K0d. **No rung may be marked passed against a number the executing agent
produced itself.** My Nu point estimate of 4.98 from 0.28.Ra^(1/4) is my own
scaling estimate, is labelled as such throughout, and **cannot grade anything**.
The measured 4.5538 is likewise a capability number and not a validated one.

**P2 — mesh sensitivity on K0b.** Every K0b number above is from a single
64x64 mesh. A single-mesh number is not a converged number.

Cost basis, stated so it can be checked rather than believed: the measured
64x64 solve is **31.88 s = 0.531 core-minutes**. Cost per iteration scales with
cell count N; the SIMPLE iteration count for an elliptic problem scales roughly
with 1/h, i.e. with sqrt(N) in 2D, so total cost scales as N^1.5. Relative to
64x64 that gives 0.125x for 32x32 and 8x for 128x128:

| mesh | cells | scaling factor | projected core-minutes |
|---|---:|---:|---:|
| 32x32 | 1024 | 0.125 | 0.07 |
| 64x64 | 4096 | 1 (measured) | 0.53 |
| 128x128 | 16384 | 8 | 4.25 |
| | | **triple total** | **4.85** |

Applying this lab's 3x planning multiplier: **ask for 15 core-minutes.** The
basis is a measurement of this exact case on this exact machine, not an
estimate, which by `scripts/cost_calibration.py`'s own finding is the class of
basis that has never over-run by more than 1.05x here.

Worth doing **before** K0c rather than after: a validation gate against a
mesh-unconverged solution tells you nothing about the model.

**P3 — extend `heat_balance.py` to the advective and turbulent paths.** Both
currently **refuse** rather than guess. The rack-row module needs both, and
neither should be enabled without its own calibration case with a known answer,
in the manner of C2. This is script work plus one small calibration case; it is
not a large solve.

**P4 — Boussinesq validity at data-center temperature rises.** beta.dT crosses
0.1 at dT = 30 K. Any rung at realistic rack dT must either justify the
approximation or move to a compressible thermophysical solver. That is a
solver-selection decision to take **before** compute is spent, not after.

**Not proposed, and not run: K2b, the rack-row module, and any turbulent SST
case.** Those carry real spend and are explicitly outside this dispatch.
