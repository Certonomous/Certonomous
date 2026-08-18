# K2e — where the Boussinesq model stops being right, measured

**Campaign F14 (cooling ladder), rung K2e. Thermal lane. 2026-08-18.**
**Tier: SOLVER-BACKED.** This is a comparison of two models on identical
geometry. It has no experimental reference, it makes no claim against one, and
under `sdk/chief_engineer/lab.py` it cannot reach VALIDATED — that chip is
reserved for a number graded against a published experiment and inside its band.
Nothing below may be quoted as validation.

Pre-registration: [`K2e_PREREGISTRATION.md`](K2e_PREREGISTRATION.md), written
and timestamped 2026-08-18T03:33:56Z at HEAD `0869284`, **before any K2e solver
ran**. Every threshold used to declare a separation is that file's; none was
chosen after seeing a curve. Runs, scripts and gate table:
[`K2e_runs/`](K2e_runs/).

---

## 1. The finding, in one paragraph

`docs/physics_rules.yaml` says `boussinesq_beta_dT_max: 0.1`. Measured on the
de Vahl Davis square cavity at **Ra = 1e5 held fixed**, with only
**eps = beta.dT** moving: **the standing limit is not one number, because the
two models do not separate on one quantity.** The **peak horizontal velocity on
the vertical mid-plane separates first, in the bracket eps ∈ (0.0333, 0.0500]** —
between a third and a half of the limit — and by the limit it is already
**2.47 % apart**. The **Nusselt number, which is the quantity every thermal rung
in this campaign actually grades on, is the last to move**: **0.063 % apart at
eps = 0.1**, and it does not reach the 1 % floor until **eps ∈ (0.30, 0.40]**.
The reason is a difference of order, measured over the sweep and not assumed:

| quantity | divergence law | order in beta.dT |
|---|---|---|
| `u_max*` peak horizontal velocity, vertical mid-plane | **D = 24.91 · (beta.dT)^1.005 %** | **first** |
| `S_rms` centro-symmetry defect of theta | **0.0831 · (beta.dT)^1.002** | **first** |
| `theta_c` dimensionless temperature at the cavity centre | **0.0343 · (beta.dT)^0.999** | **first** |
| `<theta>_V` volume-average dimensionless temperature | **0.0353 · (beta.dT)^1.002** | **first** |
| **`Nu_h` hot-wall Nusselt number** | **D = 6.355 · (beta.dT)^1.968 %** | **second** |

Symmetry breaking and the velocity field are **first order** in beta.dT. The
wall heat flux is **second order** — it is protected to leading order by the
centro-symmetry the Boussinesq equations possess and the variable-density
equations do not. That single fact explains the whole curve, and it is why a
single scalar limit cannot serve both a heat-transfer answer and a flow-structure
answer.

**Both registered outcomes happened, on different quantities.** Outcome 1 (they
separate before 0.1, the rule is too loose) holds for velocity and symmetry.
Outcome 3 (they agree past 0.1, the rule is more conservative than it needs to
be) holds for the Nusselt number, by roughly a factor of four in beta.dT.

---

## 2. What ran

30 cases: two solvers × a sweep of eps, on a mandatory two-mesh pair.

| | |
|---|---|
| geometry | square cavity L = H = 0.10 m, depth 0.01 m, 1 cell, `empty` front/back — K0c's geometry unchanged |
| Ra | **1e5, held fixed at every sweep point** |
| Pr | 0.71; TRef 300 K; beta = 1/300 exactly; laminar; g = 9.81 m/s2 |
| knob | `nu(dT) = sqrt(g.beta.dT.L^3.Pr/Ra)`, so raising dT does **not** raise Ra |
| Boussinesq | `buoyantBoussinesqSimpleFoam`, OpenFOAM v2606 stock |
| variable density | `buoyantSimpleFoam`, v2606 stock, `heRhoThermo` / `incompressiblePerfectGas` / `const` transport / `hConst` / `sensibleEnthalpy` |
| meshes | **48 × 48** (full 11-point sweep) and **96 × 96** (4 points), refinement factor **2.0**; cell Peclet 1.42 and 0.71, both under K0c's limit of 2 for `bounded Gauss linear` |
| sweep | eps = 0.001, 0.010, 0.0333, 0.050, 0.0667, 0.0833, 0.100, 0.150, 0.200, 0.300, 0.400 (dT = 0.3 … 120 K) |
| iterations | fixed per case, **no `residualControl`** — 3000 (48²), 6000 (96²), 8000 for the eps = 0.001 pair; both solvers at a given eps always run the same count |
| convergence | governed criterion, `physics_rules.yaml` `thermal.monitor_*`: peak-to-peak of Nu_h over a fixed 400-iteration window ≤ 0.02 %, sampled every 50, ≥ 9 samples |

**Convergence: 30 of 30 runs meet the governed criterion.** Worst spread on the
whole set is **0.000134 %**, a factor of 149 inside the 0.02 % gate. Verified
twice by different code: `analyse_k2e.py`'s own implementation, and the
campaign's own instrument `scripts/check_convergence.py --monitor-regex` run
independently over all 30 logs, which returned exit 0 on every one.

Neither solver is a lab build. Both ship with `openfoam2606-common`;
`docs/OPENFOAM_SOLVER_BUILD.md` is not needed for this rung and its four
artefacts are not involved.

---

## 3. Establishing like with like, BEFORE comparing anything

The two solvers share neither a temperature datum nor an equation of state, and
a datum mismatch is the obvious way to manufacture a spectacular and false
divergence. Four anchors, all constructed by one generator from one table, and
then a measurement that would catch any of them failing.

1. **Datum.** Both fields are absolute K; `T_hot` and `T_cold` are written from
   the same numbers. Witnessed in both solvers' own logs by the `hotT`/`coldT`
   function objects: every case reads **exactly** 300 ± dT/2.
2. **Equation of state is the exact function the Boussinesq model linearises.**
   `incompressiblePerfectGas` gives rho = pRef/(R.T), so
   beta_true = -(1/rho)(drho/dT) = 1/T, **= 3.33333e-03 1/K at TRef = 300 K**,
   which is the Boussinesq case's `beta` to the digit. What is measured is the
   truncation of a Taylor expansion, not a difference of fluid.
3. **Reference density, hence Ra.** `pRef` is fixed at 101325 Pa at every point,
   so rho_ref = 1.176413 kg/m3 is constant and mu = nu.rho_ref. Ra, Pr and beta
   are then identical between solvers and across the sweep **by construction**,
   independent of the solution. `perfectGas` was rejected for this reason: in a
   sealed cavity its thermodynamic pressure moves to conserve mass, shifting
   rho_ref ~1.4 % and Ra ~2.8 % at dT = 120 K — the same order as the effect
   being measured. The price paid instead is that sealed-cavity mass is not held
   fixed; that price is stated, and it removes a confounder from the swept axis.
4. **Thermal diffusivity.** k = mu.Cp/Pr with mu, Cp, Pr constant, so the
   variable-density thermal diffusivity equals nu/Pr at 300 K and varies off it —
   which is the physics being measured. Constant k also means the
   temperature-gradient Nusselt and the heat-flux Nusselt are **the same
   number**, so Q1 carries no definitional choice.

**The measurement that would catch a failure — control C-2, the eps → 0 null
test.** At eps = 0.001 every non-Boussinesq term is O(1e-3) or smaller, so the
two solvers must agree. Measured on 48²:

| | D `Nu_h` | D `u_max*` | D `v_max*` | `theta_c` | `S_rms` |
|---|---:|---:|---:|---:|---:|
| at eps = 0.001 | **0.097 %** | **0.209 %** | **0.080 %** | −0.00003 | +0.00008 |

**The like-with-like construction is good to about 0.2 %.** That is a measured
ceiling on any residual datum or property mismatch, and every separation
reported in §4 clears it by at least a factor of five. A 1 K datum offset would
show as ~0.3 % on Nu_h here, where no physics can produce it.

**Control C-1, and it is the design's own falsifier.** At fixed Ra and Pr the
non-dimensional Boussinesq problem does not depend on eps at all, so the
Boussinesq branch of every curve must be a flat line. Measured peak-to-peak
spread across the whole sweep:

| mesh | `Nu_h` | `u_max*` | `v_max*` |
|---|---:|---:|---:|
| 48² | 3.4e-08 % | 4.2e-08 % | 5.9e-08 % |
| 96² | 2.1e-08 % | 1.9e-08 % | 3.5e-08 % |

Flat to eight decimal places. A mis-scaled `nu` — the one thing that would make
this sweep meaningless — cannot survive that.

---

## 4. The divergence curve

Full table with every quantity and both meshes:
[`K2e_runs/GATE_TABLE.md`](K2e_runs/GATE_TABLE.md). Pre-registered thresholds:
Class A separates when D ≥ 1.0 % **and** D ≥ 3 × (summed convergence noise);
Class B separates when |Q_vd| ≥ 0.005 in units of dT **and** ≥ 3 × the
Boussinesq numerical floor. **Bold = separated.**

### 48 × 48, the full sweep

| dT K | eps = beta.dT | D `Nu_h` % | D `u_max*` % | D `v_max*` % | `theta_c` | `S_rms` | first separated |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.3 | 0.00100 | 0.097 | 0.209 | 0.080 | −0.00003 | +0.00008 | — |
| 3 | 0.01000 | 0.010 | 0.223 | 0.114 | −0.00034 | +0.00083 | — |
| 10 | 0.03333 | 0.010 | 0.815 | 0.407 | −0.00115 | +0.00275 | — |
| 15 | 0.05000 | 0.018 | **1.227** | 0.614 | −0.00172 | +0.00413 | **`u_max*`** |
| 20 | 0.06667 | 0.031 | **1.639** | 0.821 | −0.00229 | **+0.00551** | **`S_rms`** |
| 25 | 0.08333 | 0.047 | **2.049** | *1.029* | −0.00287 | **+0.00688** | |
| **30** | **0.10000** | **0.067** | **2.459** | *1.237* | −0.00344 | **+0.00826** | ← **the standing limit** |
| 45 | 0.15000 | 0.149 | **3.687** | *1.865* | **−0.00516** | **+0.01240** | **`theta_c`** |
| 60 | 0.20000 | 0.265 | **4.915** | *2.502* | **−0.00687** | **+0.01655** | |
| 90 | 0.30000 | 0.599 | **7.420** | *3.805* | **−0.01030** | **+0.02489** | |
| 120 | 0.40000 | **1.073** | **9.966** | *5.159* | **−0.01371** | **+0.03331** | **`Nu_h`** |

*`v_max*` is italicised throughout because its divergence is **not**
mesh-converged — see §5. It is excluded from every conclusion.*

### 96 × 96

| dT K | eps | D `Nu_h` % | D `u_max*` % | `theta_c` | `S_rms` | separated |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 10 | 0.03333 | 0.010 | 0.819 | −0.00109 | +0.00267 | — |
| 20 | 0.06667 | 0.029 | **1.646** | −0.00218 | **+0.00533** | `u_max*`, `S_rms` |
| 30 | 0.10000 | 0.063 | **2.470** | −0.00327 | **+0.00800** | `u_max*`, `S_rms` |
| 90 | 0.30000 | 0.568 | **7.449** | **−0.00978** | **+0.02409** | all but `Nu_h` |

### Separation brackets

Reported as brackets, never interpolated to a single number: the sweep has
eleven points and an interpolated crossing would claim a resolution it does not
have.

| quantity | class | separates at beta.dT ∈ | relative to the 0.1 limit |
|---|---|---|---|
| **`u_max*`** | A | **(0.0333, 0.0500]** on 48²; (0.0333, 0.0667] on 96² | **before it — about half** |
| **`S_rms`** | B | (0.0500, 0.0667] on 48²; (0.0333, 0.0667] on 96² | **before it** |
| `theta_c`, `<theta>_V` | B | (0.100, 0.150] | just after it |
| **`Nu_h`** | A | **(0.300, 0.400]** | **about 4× past it** |

**At the standing limit itself (eps = 0.1, fine mesh): `Nu_h` 0.063 %,
`u_max*` 2.470 %, `theta_c` −0.00327, `S_rms` +0.00800.**

---

## 5. Mesh convergence of the divergence — mandatory, and it struck one quantity

A divergence that is really discretisation error is worthless, so every
divergence is computed on both meshes and the pre-registered test is
|D_coarse − D_fine| / D_fine ≤ 0.20.

| quantity | relative change, 48² → 96², at eps = 0.0333 / 0.0667 / 0.100 / 0.300 | verdict |
|---|---|---|
| `Nu_h` | 0.040 / 0.050 / 0.052 / 0.053 | **MESH-CONVERGED** |
| `u_max*` | 0.005 / 0.005 / 0.004 / 0.004 | **MESH-CONVERGED** |
| `theta_c` | 0.052 / 0.052 / 0.052 / 0.053 | **MESH-CONVERGED** |
| `<theta>_V` | 0.040 / 0.040 / 0.040 / 0.040 | **MESH-CONVERGED** |
| `S_rms` | 0.033 / 0.033 / 0.033 / 0.033 | **MESH-CONVERGED** |
| `v_max*` | 0.261 / 0.257 / 0.255 / 0.240 | **NOT mesh-converged** |

`u_max*` — the quantity carrying the headline — is mesh-converged to **0.5 %**,
the tightest on the table. `v_max*` fails at every eps by a nearly constant
25 %, which says its **eps-scaling is right and its amplitude is mesh-dependent**:
it is the peak vertical velocity, which lives inside the thin vertical wall
boundary layer and is the most under-resolved quantity in the set. **It is
struck from every conclusion**, and it is reported rather than dropped because
the mesh check existing and catching something is the evidence that the other
five results survived a test they could have failed.

---

## 6. Heat balance — reported, and it is not evidence

`scripts/heat_balance.py` ran on every case. **Every K2e case is sealed and
impermeable**, so `heat_balance_closure_is_evidence_on_sealed_case: false`
applies in full: the discrete equation forces the boundary terms to sum to zero
at every iteration, converged or not, and a pass here is **not evidence that the
physics is right**. Measured: **imbalance 0.0000 % on all 15 Boussinesq cases**,
and the same near-identity recomputed from the two wall integrals the running
solver printed reads **≤ 2.0e-05 %** on all 30.

What a pass still establishes, stated narrowly: it would catch wrong fluid
properties, a wrong patch area, a wrong sign convention, a patch omitted from
the sum, or an unaccounted source. It establishes nothing about the circulation,
about convergence, or about which of the two models is right.

**On the 15 variable-density cases `heat_balance.py` REFUSED to produce a
number at all.** It reads `constant/transportProperties` for `nu` and `Pr`, and
a `rhoThermo` case does not have one. The campaign's own heat-balance instrument
therefore has no path for the exact solver class the Boussinesq limit tells a
rung to move to. Docketed, with two further defects found on the same path — see
§8.

---

## 7. Controls, each with its kind

| id | control | result | kind |
|---|---|---|---|
| C-1 | Boussinesq branch flat across the sweep at fixed Ra | spread 2e-08 to 6e-08 % on both meshes | **reachability** — a mis-scaled `nu` makes it fail |
| C-2 | eps → 0 null test | 0.097 / 0.209 / 0.080 % on Nu_h / u_max* / v_max*; all below the 1.0 % floor | **reachability** — a 1 K datum offset would read ~0.3 % on Nu_h |
| C-3 | K0c anchor | K2e Boussinesq Nu 4.5878 (48²), 4.5383 (96²) against K0c's 4.5590 (64²), 4.5310 (128²); monotone and interleaved as mesh count demands | **recognition** — it reads a published number back and cannot fail informatively about K2e's own physics |
| C-4 | two-mesh pair on every divergence | struck `v_max*`, passed the other five | **reachability** — and it fired |
| C-5 | every control read from the SOLVER LOG | `hotT`/`coldT` return exactly 300 ± dT/2 on all 30; `buoyantSimpleFoam`'s own `rho min/max` matches pRef/(R.T) at the witnessed wall temperatures to 6 decimal places on all 15 | **reachability** — an input file states an intent, a log states what ran |
| — | convergence cross-check | `scripts/check_convergence.py --monitor-regex` independently returned exit 0 on all 30 logs | **reachability** |

`analyse_k2e.py` additionally **refuses to grade at all** if its own thresholds
have drifted from the pre-registration's text; that check runs before any case
is read (L-113: a sentence describing a check goes stale silently).

---

## 8. Defects found on the way

Three, all in `scripts/heat_balance.py`, all filed on the docket.

1. **It deletes the case's `postProcessing/` directory** (line 770,
   `shutil.rmtree(..., ignore_errors=True)`) before its own postProcess pass.
   That directory is the in-pass function-object history the campaign's **own**
   convergence gate reads. Auditing a case destroys its convergence evidence,
   silently and after the fact. Measured here: twelve Boussinesq cases lost
   `hotFlux`, `coldFlux`, `Umax` and `Tcentre` the moment they were audited.
   K0c's committed archive shows the same hole — only `hbAudit_*` survives under
   `K0c_runs/*/postProcessing/`.
2. **It has no path for a compressible (`rhoThermo`) case**, because it requires
   `constant/transportProperties`. The instrument cannot audit the solver class
   the Boussinesq rule points at.
3. **Six of its refusal paths exit 1, not the documented 2.** Its own docstring
   says "Exit 2 = the auditor REFUSED to produce a number", but the six
   `raise SystemExit("REFUSE: …")` sites exit 1 — the same code as "the balance
   did not close". Measured: a nonexistent case directory and an empty case both
   exit 1. A caller reading the exit status cannot tell a refusal from a finding.

---

## 9. What this does and does not license

**Does.** It replaces "the rules say 0.1" with measured coefficients. Any later
rung can now compute its own admissible beta.dT from the accuracy it needs:
D(Nu_h) = 6.36·(beta.dT)² %, D(u_max*) = 24.9·(beta.dT) %,
|theta_c| = 0.0343·(beta.dT), |S_rms| = 0.0831·(beta.dT). Worked through the
K2a recirculation amplification dT_span = dT_rack/(1−r): at r = 1/3 a 20 K rise
gives a 30 K span, eps = 0.1, and a Boussinesq solve of it is **0.06 % off on
wall heat flux and 2.5 % off on peak velocity**. A 40 K rise at the same r gives
eps = 0.2: **0.27 % and 4.9 %**.

**Does not.**
- **No experimental reference exists here.** SOLVER-BACKED, not VALIDATED.
  Both models could be wrong together and this rung would not see it.
- **Constant mu and k.** A real gas has mu(T), k(T). Every number above is a
  **lower bound** on the non-Boussinesq error of a real gas at the same beta.dT.
- **One case class.** Two-dimensional, laminar, steady, Ra = 1e5, Pr = 0.71,
  square cavity, differentially heated side walls. A rack row is turbulent,
  three-dimensional, and driven by through-flow. The **exponents** are the part
  most likely to transfer, because they come from the structure of the
  expansion; the **coefficients** are properties of this case.
- **`v_max*` is struck** and no claim rests on it.
- The sealed cavity's total mass is not held fixed (§3 anchor 3). That was
  chosen to keep Ra exactly on the swept axis and it is not a defect, but it is
  not the closed-cavity low-Mach model either.

**Recommended change to `docs/physics_rules.yaml`, not made here.** A single
`boussinesq_beta_dT_max` cannot serve both answers. It should become at least
two numbers — one for a rung graded on heat transfer, one for a rung graded on
flow structure — or be replaced outright by the measured laws above, with the
scope limits carried alongside them. **This rung proposes; it does not edit the
governed file.**

---

## 10. Reproduction, followed literally from a fresh temporary directory

Three documents in this campaign shipped recipes that could not be followed
because they were written mid-run. `K2e_runs/README.md`'s three recipes were
therefore executed verbatim, from a `mktemp -d`, after the document was written:

| recipe | executed | result |
|---|---|---|
| re-derive `GATE_TABLE.md` from the archive without re-solving | in full | output **identical** to the committed file, `diff` clean |
| reproduce the convergence gate with `scripts/check_convergence.py` | in full | 30 of 30 CONVERGED, 0 failures |
| re-solve from scratch | **partially — see below** | 30 of 30 built cases **byte-identical** to the archived ones across `0.orig/`, `constant/`, `system/` (90 directory comparisons, 0 differences); the two rule-point cases re-solved **bit-identical** in `Nu_h` and in the final `T` and `U` |

**What was not executed, and why.** The full re-solve of all 30 cases would cost
another ~21 core-minutes and take this rung past its 40 core-minute
authorisation. Two cases were re-solved instead, at eps = 0.1 — the standing
limit, and the point the headline is quoted at — one under each solver. The
generator was verified in full: every one of the 30 case definitions it writes
is byte-identical to the case that was actually solved, so what the recipe
rebuilds is provably the same problem, and the two it was allowed to solve came
back bit-identical. That is the reproduction claim, and it is not the stronger
one.

---

## 11. Compute

| item | core-minutes |
|---|---:|
| the 30 archived solves | **20.91** |
| discarded first pass (a `volFieldValue` operation `maxMag` that v2606 does not have; 24 cases, all failed in ~1.4 s) | 0.51 |
| setup pilot and two single-case calibration runs | 0.67 |
| solves superseded by the eight re-runs (iteration-count change, bracket refinement) | 5.44 |
| `heat_balance.py` and analysis passes (4 × 30 cases, ~15 s wall each) | ~1.0 |
| the §10 reproduction re-solve (2 cases) | 0.37 |
| **total** | **~28.9** |

**Authorised: 40 core-minutes. Spent: ~28.9, about 72 %.** Every solve is
single-core, so core-minutes equal summed wall clock; cases were run 6–8 at a
time, which changed wall time and not core-minutes. Against the thermal lane's
300 core-minute overnight ceiling shared with two other rungs, this rung took
about 9.6 %.
