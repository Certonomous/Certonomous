# K2e pre-registration — where the Boussinesq model stops being right

**Campaign F14 (cooling ladder), rung K2e. Thermal lane.**
**Written 2026-08-18T03:33:56Z, at HEAD `0869284`, BEFORE any K2e solver ran.**

This file is the pre-registration. Nothing in it may be edited after the first
K2e solve; corrections go in `K2e_RESULTS.md` as an explicit, dated amendment
that names what changed and why. A threshold chosen after seeing the curve is
not a threshold.

---

## 0. What this rung is, and what tier it can reach

`docs/physics_rules.yaml` block `thermal` carries `boussinesq_beta_dT_max: 0.1`
and `boussinesq_dT_max_K_at_TRef_300: 30.0`. Every F14 rung so far has treated
that number as a fence to stay behind. K2e turns it into a measurement: it runs
the same case under the Boussinesq solver and under a variable-density solver
across a sweep of beta.dT that brackets 0.1, and reports where and by how much
the two models separate.

**This is a MODEL-COMPARISON rung. It has NO experimental reference.** Under
the lab's fidelity chips (`sdk/chief_engineer/lab.py`, VERIFICATION_CHARTER.md
"the verdict vocabulary is fixed") its tier is **SOLVER-BACKED** — "a real solve
produced it; no experimental comparison (or the comparison is not
like-for-like)". It **cannot** reach VALIDATED, which `lab.py` reserves for a
number graded against a published experiment and inside its band, and it must
never be quoted as if it had. What it can establish is a *difference between two
models on identical geometry*, which is a self-contained statement: it depends
on no external data, and in particular on none of the paywalled data that has
blocked the K2c raised-floor rung entirely.

Internal name F14 throughout. No application-domain language.

---

## 1. The case, and why it is this case

The de Vahl Davis square cavity already used by rung K0c
(`K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`), unchanged in geometry:

| quantity | value |
|---|---|
| L = H | 0.10 m |
| depth | 0.01 m, 1 cell, `empty` front/back (2-D) |
| g | 9.81 m/s2, -y |
| TRef | 300 K |
| T_hot / T_cold | 300 + dT/2 / 300 - dT/2, on the x = 0 and x = L walls |
| top and bottom | adiabatic, no-slip |
| Pr | 0.71 |
| **Ra** | **1e5, HELD FIXED at every point of the sweep** |
| turbulence | laminar |

### 1.1 The knob is dT at FIXED Ra, and this is the whole design

K0c set Ra by moving dT at fixed nu. K2e must do the opposite. If dT is raised
at fixed nu, Ra rises with it, both solvers change together for an ordinary
physical reason, and any measured separation is confounded with a change of
Rayleigh number. So Ra is pinned and the viscosity moves with dT:

    Ra = g.beta.dT.L^3 / (nu.alpha),  alpha = nu/Pr
    =>  nu(dT) = sqrt( g . beta . dT . L^3 . Pr / Ra ),   beta = 1/TRef = 1/300

At dT = 1.088162239 K this returns nu = 1.589461e-05 m2/s, which is K0c's own
number for Ra = 1e5 — the sweep passes exactly through the case K0c already
solved, and that is a check on the generator, not a coincidence.

**The consequence is the point of the design.** In non-dimensional form the
Boussinesq problem depends ONLY on (Ra, Pr). At fixed Ra and Pr its answer is
therefore *identical at every dT in the sweep*. The variable-density problem
depends on (Ra, Pr, **eps**) with **eps = beta.dT = dT/300**. So:

* the Boussinesq branch of every curve below is a **flat line by construction**,
  and if it is not flat, the setup — not the physics — is wrong. This is a
  built-in falsifier and it is checked in §5.
* every deviation of the variable-density branch from that flat line is a pure
  non-Boussinesq effect, at fixed Rayleigh number.

### 1.2 The sweep

eps = beta.dT = dT/300, nine points, bracketing the 0.1 rule:

| # | dT (K) | eps = beta.dT | relative to the rule |
|---:|---:|---:|---|
| 1 | 0.3 | 0.001 | null / like-with-like anchor |
| 2 | 3 | 0.01 | far inside |
| 3 | 10 | 0.03333 | inside (K0a's own operating point) |
| 4 | 20 | 0.06667 | inside |
| 5 | 30 | 0.10000 | **exactly the rule** |
| 6 | 45 | 0.15000 | outside |
| 7 | 60 | 0.20000 | outside |
| 8 | 90 | 0.30000 | far outside |
| 9 | 120 | 0.40000 | far outside |

Point 5 is the rule. Point 3 is where K0a actually ran. Point 7 (eps = 0.2) is
what a 20 K rack rise becomes under the K2a recirculation amplification
dT/(1-r) at r = 1/3 doubled — i.e. the sweep covers the range the campaign's
later rungs will sit in, not only the range the rule allows.

---

## 2. The two models, and the like-with-like construction

| | Boussinesq | variable density |
|---|---|---|
| solver | `buoyantBoussinesqSimpleFoam` | `buoyantSimpleFoam` |
| both shipped with | OpenFOAM v2606, `/usr/lib/openfoam/openfoam2606` | same |
| density | `rhok = 1 - beta(T - TRef)`, buoyancy term only | `rho = pRef/(R T)`, everywhere |
| pressure | `p_rgh` kinematic, m2/s2 | `p_rgh` in Pa |
| energy | `div(phi,T) - laplacian(alphaEff,T) = 0` | `div(phi,h) + div(phi,K) - laplacian(alphaEff,h) = rho(U.g)` |
| properties | nu, Pr constant | mu, Pr constant (`transport const`) |

**The two solvers do not share a temperature datum or an equation of state, so
the match is constructed rather than assumed. Four anchors, all checkable:**

1. **Temperature datum.** Both fields are absolute K, and both cases carry the
   *same* `T_hot` and `T_cold` numbers, generated from one table by one script.
   No offset exists to mismatch.
2. **Equation of state = the exact function the Boussinesq model linearises.**
   The variable-density case uses `equationOfState incompressiblePerfectGas`
   with `pRef 101325` fixed. Then rho = pRef/(R T) and
   beta_true = -(1/rho)(drho/dT) = 1/T, which at T = TRef = 300 K is exactly
   3.33333e-03 1/K — **the Boussinesq case's `beta`, to the digit.** The
   Boussinesq model is precisely the first-order Taylor expansion of this EOS
   about TRef. The separation measured is therefore the truncation of that
   expansion and nothing else; it is not a difference of fluid.
3. **Reference density, hence Ra, hence nu.** `pRef` is held at 101325 Pa at
   every sweep point, so rho_ref = pRef/(R.300) is a constant, and
   mu(dT) = nu(dT) . rho_ref. Ra, Pr and beta are then identical between the two
   solvers and across the whole sweep BY CONSTRUCTION, with no dependence on
   the solution. (`perfectGas` was rejected for exactly this reason: in a sealed
   cavity it lets the thermodynamic pressure move to conserve mass, which shifts
   rho_ref by ~1.4 % at dT = 120 K and Ra by ~2.8 % — the same order as the
   effect being measured. The price of `incompressiblePerfectGas` is that the
   sealed cavity's total mass is not held fixed; that price is stated, and it is
   the right trade because it removes a confounder from the axis being swept.)
4. **Thermal diffusivity.** Boussinesq diffuses T with alpha = nu/Pr.
   The variable-density case has k = mu.Cp/Pr with mu, Cp, Pr all constant, so
   its thermal diffusivity is mu/(rho.Pr), equal to nu/Pr **at T = 300 K** and
   varying off it. That variation is part of the non-Boussinesq physics being
   measured, not a mismatch.

**The null test that decides whether the match holds** is sweep point 1,
eps = 0.001. At that eps every non-Boussinesq term is O(1e-3) or smaller, so
the two solvers must agree on every quantity in §3 to within their own
convergence noise. **If they do not, the rung reports a datum/setup mismatch
and stops. It does not report physics.** This is registered as the primary
falsifier, because a datum mismatch is the obvious way to manufacture a
spectacular and false divergence.

### 2.1 What is deliberately NOT varied, and therefore not measured

`mu` and `k` are held **constant** in the variable-density case. A real gas has
mu(T), k(T) (Sutherland), which would add further divergence. So the curve this
rung produces isolates the **density** terms — the nonlinearity of rho(T), the
appearance of rho in inertia and in continuity, and the resulting variation of
nu and alpha — and is a **lower bound** on the total non-Boussinesq error of a
real gas at the same beta.dT. Stated here so it cannot be quietly dropped later.

---

## 3. The quantities compared — fixed now

All are dimensionless and are computed from the final written fields by ONE
function applied identically to both solvers (`analyse_k2e.py`), on the
structured blockMesh cell ordering (i fastest). alpha_ref = nu(dT)/Pr,
theta = (T - 300)/dT.

**Class A — magnitude quantities, non-zero under both models.**

| id | quantity | definition |
|---|---|---|
| Q1 | `Nu_h` | hot-wall mean Nusselt = <dT/dn>_hotWall . L / dT, from the `grad(T)` function object's `areaNormalIntegrate`, divided by wall area. (In the variable-density case k is constant, so the temperature-gradient Nusselt and the heat-flux Nusselt are the same number; there is no definitional choice to make.) |
| Q2 | `u_max*` | max over the vertical mid-plane x = L/2 of \|U_x\|.L/alpha_ref. Mid-plane falls on a face, so the two adjacent cell columns are averaged — the same operator on both solvers. |
| Q3 | `v_max*` | max over the horizontal mid-plane y = H/2 of \|U_y\|.L/alpha_ref, same two-row averaging. |

Divergence for Class A:  **D_Q(eps) = 100 . |Q_vd - Q_bou| / |Q_bou|  [%]**

**Class B — symmetry quantities, identically zero under Boussinesq.**

The Boussinesq cavity is exactly centro-symmetric: theta(x,y) = -theta(L-x,H-y).
Variable density breaks that symmetry. These quantities have **no non-zero
Boussinesq baseline**, so a percentage divergence is undefined for them and they
are reported as absolute values in units of dT. This is stated now, not after
the fact.

| id | quantity | definition |
|---|---|---|
| Q4 | `theta_c` | theta at the cavity centre (mean of the 4 central cells) |
| Q5 | `<theta>_V` | volume-average theta over all cells |
| Q6 | `S_rms` | RMS over cells of [theta(i,j) + theta(nx-1-i, ny-1-j)] |

Note Nu_hot vs Nu_cold is NOT in this list. On a sealed, steady, constant-k
cavity with adiabatic top and bottom, both models force Nu_h = Nu_c
identically — the gravity-work term integrates to zero over a closed domain
because the wall integral of rho.U vanishes. It is therefore a **closure check**
(§4), not a physics signal, and treating it as one would be exactly the error
`physics_rules.yaml` §4 warns about.

---

## 4. Convergence, heat balance, and controls — fixed now

**Convergence is the governed criterion, not residuals and not an endpoint.**
From `docs/physics_rules.yaml` block `thermal`:
`monitor_peak_to_peak_max_pct: 0.02`, `monitor_window_iterations: 400`,
`monitor_sample_interval_iterations: 50`, `monitor_min_samples: 9`.
Enforced with `scripts/check_convergence.py --monitor-regex` on the running
solver's own in-pass function-object output for **Nu_h**, for **every run of
both solvers**. Peak-to-peak spread over the last 400 iterations must be
<= 0.02 %. Runs that miss it are extended; a run still missing it at the end is
reported as NOT_CONVERGED and its point is struck from the curve rather than
quoted. `max|U|` and `theta_c` are monitored on the same schedule and their
spreads are reported beside Nu_h's, ungated.

**Heat balance** is run with `scripts/heat_balance.py` on every solve. **On these
cases it is near-identity and proves nothing about correctness** — every K2e case
is sealed and impermeable, so `heat_balance_closure_is_evidence_on_sealed_case:
false` applies in full. What it does establish, narrowly: wrong fluid properties,
a wrong patch area, a wrong sign, a patch dropped from the sum, an unaccounted
source. That is the only claim that will be made from it.

**Controls, with their kind stated in the results, distinguishing REACHABILITY
(the control can make the check fail) from RECOGNITION (the check merely reads
the value back).** Registered now:

| id | control | what it is for | kind |
|---|---|---|---|
| C-1 | **Boussinesq flatness.** Q1..Q3 from the Boussinesq solver across all nine eps at fixed Ra must vary by no more than the convergence noise. | The design's own falsifier: the Boussinesq branch is flat by theory (§1.1). If it drifts, the generator or the non-dimensionalisation is wrong. | reachability — a mis-scaled nu makes it fail |
| C-2 | **eps -> 0 null.** Sweep point 1 (eps = 0.001): both solvers agree on Q1..Q3 within noise and Q4..Q6 sit at the numerical floor. | Establishes like-with-like. A datum or property mismatch shows here, where physics cannot. | reachability — a T-datum offset of even 1 K makes it fail |
| C-3 | **K0c anchor.** The Boussinesq run at the sweep point nearest K0c's own Ra = 1e5 case reproduces K0c's Nu_avg to within the mesh difference. | Ties K2e's Nusselt estimator to an already-gated rung. | recognition — it reads a published number back |
| C-4 | **Mesh pair.** Every divergence is computed on two meshes (§5). | Separates model-form difference from discretisation error. | reachability |
| C-5 | **Solver-log control audit.** Every control above is verified from the SOLVER LOG (imposed wall temperatures via the `hotT`/`coldT` function objects, `rho min/max` printed by `buoyantSimpleFoam`'s own pEqn, mesh counts from `log.blockMesh`), never from the input dictionary. | An input file states an intent; a log states what ran. | reachability |

---

## 5. What counts as a separation — fixed now

**Class A.** A quantity Q has SEPARATED at eps when **both** hold:

* **D_Q(eps) >= 1.0 %** — an absolute floor, so that a very quiet pair of runs
  cannot make a 0.05 % difference "significant". 1.0 % is K0c's own tightest
  graded pass band (`GATE_TABLE.md`, the Nu_avg rows), i.e. the smallest
  difference this campaign has ever agreed to treat as real; and
* **D_Q(eps) >= 3 x (p2p_bou + p2p_vd)** — three times the summed measured
  peak-to-peak convergence noise of the two runs being differenced. With the
  governed 0.02 % criterion this term is <= 0.12 %, so the 1.0 % floor is
  expected to bind; it is written this way so that a run which converges worse
  than the criterion cannot smuggle its noise in as signal.

**Class B.** Q4/Q5/Q6 have SEPARATED at eps when **both** hold:

* **|Q_vd| >= 0.005** in units of dT (0.5 % of the imposed temperature
  difference — 0.15 K at the eps = 0.1 rule point); and
* **|Q_vd| >= 3 x |Q_bou|** at the same eps, where Q_bou is the numerical
  symmetry floor of the Boussinesq run.

**The headline.** "First quantity to separate" is reported **per class** and the
overall headline names the smallest eps at which ANY pre-registered quantity
separates, **with its class named**, because Class A and Class B are not on a
common axis and pretending they are would be a rhetorical trick.

**eps_sep(Q)** is reported as the bracketing interval between the last sweep
point that does not separate and the first that does. It is NOT interpolated to
a single number; the sweep is nine points and an interpolated crossing would
claim a resolution the sweep does not have.

**Mesh convergence of the divergence.** Mandatory, per `physics_rules.yaml` and
K0c §1.4. Two meshes, refinement factor 2.0 in each direction:
**48 x 48 (coarse)** and **96 x 96 (fine)**. The full nine-point sweep runs on
the coarse mesh under both solvers; the fine mesh runs both solvers at
eps = 0.03333, 0.10000, 0.30000. A divergence is **MESH-CONVERGED** when

    |D_coarse - D_fine| / D_fine  <=  0.20      (20 %)

at the fine-mesh eps points. If it is not, the rung reports the divergence as
**NOT mesh-converged** and says so in the headline, because a divergence that is
really discretisation error is worthless. Cell Peclet number stays below 2 on
both meshes (K0c's admissibility condition for `bounded Gauss linear`):
u2max_ref/N = 68.22/48 = 1.42 and 68.22/96 = 0.71.

---

## 6. Registered outcomes — all three are results

1. **They separate before eps = 0.1.** The standing rule is too loose for this
   case class and should tighten. Most useful outcome.
2. **They separate at or somewhat after eps = 0.1.** The rule is calibrated;
   the rung replaces "the rules say 0.1" with a measured number and a first
   quantity.
3. **They agree to within convergence noise all the way to eps = 0.4.** The
   limit is more conservative than it needs to be **for this case class**, and
   the rung says so. This is a real finding and will be reported as one, not
   buried. It would NOT license raising the rule generally: §2.1 already records
   that constant mu and k make this a lower bound, and a laminar 2-D cavity is
   not a rack row.

**Predicted before running** (recorded so the pre-registration can be scored,
not because the prediction gates anything): Class B separates first, because
symmetry breaking is a first-order-in-eps effect on a quantity whose baseline is
zero, whereas Q1..Q3 are even-order-dominated. Expected Class B separation near
eps ~ 0.03-0.07 and Class A separation near eps ~ 0.15-0.3, with Q1 (`Nu_h`) the
last of Class A to move.

---

## 7. Compute

Authorised: **40 core-minutes**, inside a 300 core-minute overnight ceiling for
the thermal lane shared with two other rungs. Every solve is single-core, so
core-minutes = summed wall clock; each case writes its own `COST.txt` and the
total is reported in `K2e_RESULTS.md` whether or not it lands inside the
authorisation. Cases are run concurrently across cores, which changes wall time
and not core-minutes.
