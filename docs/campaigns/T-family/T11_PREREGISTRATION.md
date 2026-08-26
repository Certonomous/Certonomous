# T11 — transient conduction in a plane wall, EXACT tier: pre-registration (FROZEN)

**FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN.** Campaign T, rung **T11**, the
last entry in H-5's tier-completion order and the **only rung on the T ladder
that is blocked by nothing except our own work.** Verdict vocabulary fixed by
`CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING.**

## 0. WHAT THIS RUNG IS, AND WHAT IT IS NOT — first paragraph, not a footnote

**This is SOLID-ONLY transient conduction. There is no fluid in it.** It is the
**transient half** of the conjugate problem, not conjugate heat transfer.

> **T11 earns `V` for TRANSIENT CONDUCTION and NOT for conjugate heat transfer.**
> `T_FAMILY_INDEX.md` calls T11 a "transient conjugate module"; that describes
> the eventual rung, not this entry arm. **Claiming conjugate here would be a
> tier overclaim into the coverage matrix, which is the one place an overclaim
> becomes a credential.** True transient conjugate requires
> `chtMultiRegionFoam` — present on this box, unused by this family — and is a
> separate rung with its own registration.

**Condition at freeze** (`CLAUDE.md` rule 2). The run tree is
`verification/runs/T-family/T11_runs/`. At the moment this file is committed
that tree holds **seven instruments and no case directory**: `T11_PW_c`,
`T11_PW_m` and `T11_PW_f` **do not exist** — no `0/`, no `0.orig/`, no mesh, no
`log.solve`, no `STATUS`, no `DONE`. **Zero core-minutes have been spent on this
rung.**

**Disclosed scratch probes, because they shaped this document.** Before the
freeze, `build_t11.py` was run against a **scratch root outside the repository**
and `laplacianFoam` was executed there. Nothing was written into the repository
and no registered case was touched. Three things came out of it and all three
are recorded below rather than quietly absorbed: the **`DILU` refusal** (§3.2),
the **mesh-dependent `valueFraction`** (§5, now **L-341**), and the **band
being far too loose** (§6.1).

---

## 1. The three questions answered before anything was written

The supervisor required these answered **before** a pre-registration existed.

### 1.1 What closed-form solution, and where does the lab hold it?

**No transient-conduction textbook or paper is on disk.** Searched by name:
incropera, carslaw, jaeger, ozisik, bergman, lienhard, mills, kays, holman,
"heat conduction", "transient conduction", lumped, biot, fourier — **zero hits
each**, against a positive control in the same sweep returning meinders 1,
narumanchi 1, bahrami 2. **The zeros are real absences, not a blind reader.**

**That does not block an EXACT-tier rung, because this lab does not source EXACT
referents from pages — it DERIVES them.** Rule 15 governs **retrieved papers**:
it forbids trusting a document you have not title-page verified. **A derivation
transcribes nothing and therefore cannot inherit a transcription error.** The
precedent is settled and three-fold on disk — `exact_laminar_pipe.py` (T1c),
`exact_t9a.py` (T9a), `exact_t10a.py` (T10a) — and stated outright in
`T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md` §2.1: the constants are
*"reproduced in the rung's own comparator from the derivation, not typed in from
a textbook page."*

**The solution, written out.** One-dimensional transient conduction in a plane
wall of half-thickness `L`, insulated/symmetric at `x = 0`, convective at
`x = L`, constant properties, uniform initial temperature:

    theta(x*, Fo) = SUM_n  C_n exp(-zeta_n^2 Fo) cos(zeta_n x*)
    C_n           = 4 sin(zeta_n) / (2 zeta_n + sin(2 zeta_n))
    zeta_n tan(zeta_n) = Bi
    theta = (T - T_inf)/(T_0 - T_inf),  x* = x/L,  Fo = alpha t / L^2,  Bi = h L / k

and the **volume average**, which is this rung's primary graded quantity:

    theta_mean(Fo) = SUM_n C_n exp(-zeta_n^2 Fo) sin(zeta_n)/zeta_n

### 1.2 Under exactly what assumptions is it exact?

One-dimensional; constant `k`, `rho`, `c`; no internal generation; uniform and
constant `h` and `T_inf`; no phase change; no radiation; uniform initial
temperature; insulated or symmetric centreplane.

**The series is exact for all `Fo`.** Two familiar reductions are **not**, and
this rung uses them **only as controls, never as the referent**:

| reduction | valid only for |
|---|---|
| one-term truncation | `Fo > 0.2` |
| lumped capacitance | `Bi < 0.1` |
| semi-infinite solid | penetration depth much less than `L`, roughly `Fo < 0.05` |

**An exact solution outside its assumptions is not exact; it is wrong with
confidence.** The registered referent is the full series, evaluated with 80
terms.

### 1.3 Can the lab's solver be posed in that regime? **YES — measured, not assumed**

**The existing T9a machinery is NOT transient**: `T9a_runs/*/system/fvSchemes`
carries `ddtSchemes { default steadyState; }`. So feasibility was **driven** on
a scratch 1-D wall rather than argued. With the Robin coefficient derived
correctly, `laplacianFoam` reproduces the analytic series at the centreplane to
**1.4e-05 to 4.9e-05 relative** across `Fo` 0.05–0.20 at `N = 200`; the residual
is discretisation error, which is exactly what the Roache triple measures.

---

## 2. The registered case

| quantity | value |
|---|---|
| geometry | plane wall, half-thickness `L` = 0.01 m, 1-D (one cell across, `empty` sides) |
| `alpha` (`DT`) | 1.0e-05 m^2/s |
| `Bi` | **1.0** — deliberately O(1): outside the lumped regime, so the rung tests the full series and not a limit |
| `x = 0` | insulated / symmetry — `zeroGradient` |
| `x = L` | convective Robin — `mixed`, coefficient per §5 |
| initial | `theta` = 1 uniform (`T_0` = 1, `T_inf` = 0, so `theta` = `T`) |
| `endTime` | 2.0 s, i.e. **`Fo` = 0.20** |
| `deltaT` | **1.0e-04 s, FIXED ON EVERY LEVEL** — see §4 |
| solver | `laplacianFoam` |

---

## 3. Numerics, and two things the scratch probe forced

### 3.1 Schemes

`ddtSchemes Euler`; `laplacianSchemes Gauss linear corrected`;
`snGradSchemes corrected`.

### 3.2 `PCG` / `DIC`, and the refusal that is the GOOD outcome

`laplacianFoam`'s matrix is **symmetric**, and OpenFOAM **refuses** an
asymmetric preconditioner on it outright: `PBiCGStab` with `DILU` returns
`Unknown symmetric matrix preconditioner type DILU` and the solver stops.

**The failure mode is recorded, not just the fix.** A solver that stops is far
better than one that silently accepts an inappropriate preconditioner and
returns a plausible wrong field. This refusal is a property of the library worth
knowing, and it was found by **running**, not by reading a dictionary.

---

## 4. The mesh family and the time step

| level | `N` cells | `dx` (m) | `deltaT` (s) | steps |
|---|---:|---:|---:|---:|
| `T11_PW_c` | **100** | 1.000e-04 | 1.0e-04 | 20 000 |
| `T11_PW_m` | **200** | 5.000e-05 | 1.0e-04 | 20 000 |
| `T11_PW_f` | **400** | 2.500e-05 | 1.0e-04 | 20 000 |

**`r21 = r32 = 2` exactly**, by construction.

**`deltaT` is fixed across levels deliberately, and the consequence is stated
rather than hidden.** Refining only in space makes the temporal error
**common-mode**, so the Roache triple isolates **spatial** discretisation — which
is what a GCI is for. **The temporal error does NOT cancel in Richardson
extrapolation; it biases all three levels equally.** Control **C-T** (§7)
measures that bias by halving `deltaT` at the fine level and reporting the
movement. It is measured, not assumed away.

---

## 5. THE ROBIN COEFFICIENT IS MESH-DEPENDENT — L-341

OpenFOAM's `mixed` condition forms
`T_face = f*refValue + (1-f)*(T_cell + refGrad/deltaCoeff)`. Matching it to
`-k dT/dx = h (T - T_inf)` gives

    f = (h/k) / ((h/k) + deltaCoeff),   deltaCoeff = 1/(dx/2) = 2N/L
    =>  f = Bi / (Bi + 2N)

**`f` CONTAINS THE MESH SPACING.**

| level | `N` | `deltaCoeff` | **`valueFraction`** |
|---|---:|---:|---:|
| `c` | 100 | 20 000 | **4.97512438e-03** |
| `m` | 200 | 40 000 | **2.49376559e-03** |
| `f` | 400 | 80 000 | **1.24843945e-03** |

> **A hardcoded `f` would have given every level a DIFFERENT EFFECTIVE BOUNDARY
> CONDITION while the dictionaries looked identical. The Roache triple would
> then measure boundary-condition error instead of discretisation error —
> converging cleanly to the wrong answer and reporting a respectable observed
> order.** That is the worst available failure: not a refusal, not an obvious
> wrong number, but a *clean-looking convergence study of the wrong thing.*

**Measured before this rung existed:** a plausible guess of `f = 0.3333` put the
solution **18 % out** at `Fo` = 0.2 while still looking like a perfectly
converged field. This is **L-341**.

**THE GUARD.** `build_t11.py --check-levels` recomputes `f` for all three levels
and **REFUSES (exit 2)** unless all three differ and each equals the derived
`Bi/(Bi+2N)`. **Shown able to fire:** with the formula replaced by a constant it
returns exit 2 naming the identical values, both in-process and as a subprocess.

---

## 6. The graded rows

| row | quantity | reference at `Fo` = 0.20, `Bi` = 1 |
|---|---|---|
| **G1** | **`theta_mean`** — volume average, the stored-energy quantity | **0.8515954577** |
| **G2** | `theta` at `x*` = 0 (centreplane) | **0.9506417785** |
| **G3** | `theta` at `x*` = 1 (convective face) | **0.6433907845** |

**G1 is primary because it is MESH-INDEPENDENT BY CONSTRUCTION.** A pointwise
value has to be interpolated to a fixed `x*` — cell centres move with the mesh —
and that interpolation error would enter the triple alongside the discretisation
error it is supposed to isolate. G2 and G3 are graded too, with the
interpolation disclosed.

### 6.1 The band, and why the first one was rejected

**Registered band: `+/- 1.0e-04` relative (0.01 %) on the FINE-level value.**

This is an **accuracy claim**, not a fitted number: *this solver, on this mesh
family, reproduces the analytic transient to better than 0.01 %.* It is
falsifiable — a wrong Robin coefficient put the answer 18 % out (§5), a
first-order spatial scheme would not clear it, and a wrong preconditioner
refuses outright.

**A first draft registered `+/- 5.0e-04` and it was rejected before freeze.** A
scratch probe measured the **coarse** level at `+4.393e-06` relative — clearing
that band by a factor of 100. **A band the coarsest mesh clears by two orders of
magnitude is not a gate.** The probe is disclosed here rather than buried, and
the prediction that the tightened band still passes is registered as **P1**, to
be scored either way.

---

## 7. Controls

| id | control | refusal |
|---|---|---|
| **C1** | `valueFraction` differs across all three levels and equals `Bi/(Bi+2N)` | `exit 2` (§5) |
| **C2** | **Route B**: the series satisfies the heat equation, both boundary conditions and the initial condition, by finite differences on its own output | `exit 2` |
| **C3** | closed-form `theta_mean` agrees with Simpson quadrature of `theta(x*)` to 1e-09 | `exit 2` |
| **C4** | planted-zero control, both arms, **measured** detection floor | `exit 2` (§8) |
| **C5** | strict completion rule with the age guard | `NOT DONE` (§9) |
| **C-T** | **temporal-bias control**: halve `deltaT` at the fine level; report the movement in G1 | **REPORTED**, not gated |
| **C-L** | lumped limit — **SELF-CONSISTENCY ONLY** (§8.1) | `exit 2` if the collapse is not linear in `Bi` |

### 7.1 The gate — `CLAUDE.md` rule 5, fixed order

In `apply_gate()`, **the only function in `analyse_t11.py` that writes a
verdict**: (1) a level that did not reach `endTime`, or in which any timestep's
final residual exceeded `1e-10` → `NOT A RESULT`; (2) a triple that is
`DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → `NOT A RESULT`; (3) only
then the band. **GCI at `Fs = 1.25`.** No observed order is quoted for a
non-monotone triple and no GCI where no order exists.

**Gate (1) is stated for a TRANSIENT rung.** There is no iterative convergence
to a steady state here; the analogous conditions are that the time integration
reached `endTime` and that every timestep's linear solve converged.

**The Richardson extrapolate is REPORTED and never gated on**, in the **correct**
form `f_fine - e21/den`. `analyse_t3.py:384` and `analyse_t1c.py:337` carry the
inverted form; that was established **display-only lab-wide at `2f1d6cb7`** and
is not reproduced here.

**No `assert` statement appears in any of the four Python instruments** —
confirmed by `scripts/check_assert_guards.py` and by an independent AST check
under a planted positive control. Every refusal is `sys.exit(2)` and fires
identically under `python3 -O`.

---

## 8. The planted-zero control — rule 3

`analyse_t11.py:planted_zero_control()`. **`PLANT` = `1.234e-03`**, the constant
`analyse_t3.py:81` uses. Both arms run and both must give their registered
answer:

- **NEGATIVE ARM** — identical bytes must read back **exactly `0.0`**. Anything
  else and the reader is **noisy**, its zeros are not zeros, and every T11
  number depending on it is **withdrawn, not re-graded**.
- **POSITIVE ARM** — the plant is located **structurally by index, never by
  matching a value**, and read back through **the same `read_theta()` that
  produces every graded number**. If the reader returns exactly zero it is
  **blind** and the control refuses.
- **THE DETECTION FLOOR IS MEASURED, NOT ASSUMED.** A descending ladder
  (`1.0, 1e-1, 1e-2, 1.234e-03, 1e-4, 1e-5, 1e-6, 1e-7`) is driven through the
  same reader and **the smallest magnitude it still resolves is recorded**. If
  the registered `PLANT` sits at or below that floor the control **REFUSES**,
  naming the magnitude that *was* visible. On T8 a registered plant of
  `1.234e-03` was invisible against a `dmax` of `1.012e-01` — **82x the plant** —
  and the control passed while seeing nothing. That cannot happen here silently.
- **Copies first**, and refuses if the scratch copy resolves inside the case tree.

### 8.1 Two checks, and they are NOT the same kind of thing

**This distinction is registered because conflating them is the same error as a
planted control that plants into the wrong channel.**

| check | what it is | what it can prove |
|---|---|---|
| **lumped limit** (`Bi -> 0` gives `exp(-Bi Fo)`; measured 1.68e-04 at `Bi` = 1e-3 and 1.67e-05 at 1e-4, **linear in `Bi`**) | a limit **of this same series** — **SELF-CONSISTENCY** | the algebra is right. **It cannot prove the series is the right series.** |
| **`laplacianFoam` agreement** (1.4e-05–4.9e-05 at `N` = 200) | a numerical PDE solution against an analytic expansion, **sharing no algebra** — **GENUINELY INDEPENDENT** | this is what earns `V`. |

**The `laplacianFoam` agreement is what earns `V`; the lumped limit is hygiene.**

---

## 9. The completion rule and the launcher

`mark_done_t11.py`, all-or-nothing: `rc = 0`; an `End` line; last time ==
`endTime`; field `T` present; **`ExecutionTime` count == `endTime`/`deltaT`**;
and **every field at `endTime` NEWER than the case's own `0/T`**.

**Note the generalisation in clause 5.** The steady rungs write "count ==
`endTime`" only because their `deltaT` is 1. T11 is transient with
`deltaT` = 1e-04, so the clause is the *same* clause — one `ExecutionTime` line
per timestep — expressed for a case whose timestep is not unity.

**AN ABSENT `STATUS` IS `NOT DONE`, NEVER AN INFERENCE**, and a `STATUS` with no
`capped` field is itself a refusal.

**`run_one_t11.sh`** captures `rc` **from the solver**, never from a `setsid` or
`nohup` wrapper that returns 0 for a crashed child; writes `capped = (wall_s >=
timeout_s)` as an **independent expiry witness**, because measured on this box a
child that genuinely exits 124 is indistinguishable from a wall-clock expiry and
137 is both a `--kill-after` expiry and the OOM killer; matches time directories
by **regex with fullmatch semantics, never a shell glob** (`[0-9]*` matches
`0.orig`); and ends **`exit "$RC"`, never `exit 0`**.

**Both arms of `scripts/check_launcher_can_launch.py` were run before this
freeze.** ARM 1 (no time-directory glob): clean. ARM 2 (the **real solver**, one
timestep, scratch root): **PASS — `rc = 0`, reached `Time = 0.0001`.** ARM 2 was
**generalised for this rung**: it previously hardcoded `endTime 1`, which is one
iteration only when `deltaT` is 1 and would silently have run 10 000 steps here.

---

## 10. Cost — rule 12

**Rate MEASURED on this box, on this rung's own coarse case**, not borrowed:
**5.255e-07 core-s per cell-step** (N = 100, 20 000 steps, wall 1.051 s,
`ranks = 1`).

| level | cell-steps | **POINT core-min** | **cap** | cap/POINT | `timeout` (s) |
|---|---:|---:|---:|---:|---:|
| `c` | 2 000 000 | 0.0175 | **2** | 114 | 120 |
| `m` | 4 000 000 | 0.0350 | **4** | 114 | 240 |
| `f` | 8 000 000 | 0.0701 | **8** | 114 | 480 |
| **total** | | **0.123** | **14** | | |

**POINT 0.123 core-min = 0.00204 core-h = $0.000105 derived.
CAP 14 core-min = 0.233 core-h = $0.0120 derived.** At $0.0513/core-h,
c7a.4xlarge, **reported-by-owner, not measured** — the box cannot read its own
billing. **Every dollar figure is DERIVED, NOT MEASURED.**

**On the cap ratio, stated honestly in both directions.** T1b's `R_10k_x` had a
**2.46 %** margin, which is a coin-flip on the estimate rather than a guard.
114x looks like the opposite error, and would be, if the absolute cost were
material — it is **a tenth of a core-minute**. The failure mode being guarded
here is not an overrun but a **hang**, and a 2-to-8 minute wall-clock ceiling
catches one promptly while never touching a healthy run. `ranks = 1`, three
levels concurrent.

`timeout = cap_core_min * 60 / ranks`, coded that way. At the cap the solver is
killed, `capped=yes` lands in `STATUS`, `mark_done_t11.py` refuses. **An overrun
stops the run; it does not get a new budget.**

Calibration against this POINT lands in `docs/COST_CALIBRATION.md` at rung
completion; a completion report without it is incomplete.

---

## 11. The predictions — registered before compute

**P1.** All three graded rows **PASS** inside `+/- 1.0e-04` relative. Registered
*because* it is the comfortable answer; if a row fails, that is the more
valuable outcome and is recorded as such — not re-run until it agrees.

**P2.** All three triples are **CONVERGING** with observed order `p` in
**[1.5, 2.5]**, the second-order band the `Gauss linear corrected` Laplacian
should deliver. A value outside it scores P2 **wrong** and is reported.

**P3.** Control **C-T** moves G1 by **less than 10 %** of the band when
`deltaT` is halved — i.e. the temporal bias is small against the spatial band.
If it does not, the triple is measuring time-stepping error and the rung says so.

---

## 12. The freeze set

Committed **in the same commit as this document**, so §12's assertion is true at
the moment it binds.

| file | sha256 (first 16) | lines |
|---|---|---|
| `verification/runs/T-family/T11_runs/exact_t11.py` | `87604118964069e4` | 215 |
| `verification/runs/T-family/T11_runs/build_t11.py` | `a91cefcbd8925f68` | 179 |
| `verification/runs/T-family/T11_runs/analyse_t11.py` | `d73290093940595d` | 344 |
| `verification/runs/T-family/T11_runs/mark_done_t11.py` | `9ac63a506f060e76` | 146 |
| `verification/runs/T-family/T11_runs/run_one_t11.sh` | `7b9ef0513500a3f3` | 69 |
| `verification/runs/T-family/T11_runs/launch_t11.sh` | `8fb7df855867caa5` | 19 |

---

## 13. What this document does not do

- It **does not** modify any frozen file.
- It **does not** authorise a launch. Firing is the supervisor's call after the
  comparator diff is read personally.
- It **does not** claim conjugate heat transfer (§0).
- It **does not** claim a capability. **No rung is a capability until it has
  reported.**
- It **does not** authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7).

---

## AMENDMENT 1 — 2026-08-26 (PRE-FIRST-COMPUTE): observed-order floor P_MIN = 0.5

**Document version 1.0 -> 1.1; 1.0 = the `ca9aad86` freeze.** (The frozen text
carried no version line; this amendment is the first and declares the numbering.)

**Condition (`CLAUDE.md` rule 2), and how it was checked.** A pre-registration may
be amended only before its first compute. Checked on 2026-08-26, immediately
before this commit: `ls verification/runs/T-family/T11_runs/` lists the six
instruments and `__pycache__/` only — the run directories **`T11_PW_c`,
`T11_PW_m` and `T11_PW_f` do not exist**, and there is no `log.solve`, no
`STATUS.*` and no `DONE.*` anywhere under the tree; `mark_done_t11.py` reports
`NOT DONE ... no case directory` for all three levels. **Zero core-minutes have
been spent on this rung.** The diff of `analyse_t11.py` against the frozen blob
was read personally by the heat-transfer supervisor (twice: at `P_MIN = 0.05`,
then again at `0.5` after the selftest exposed the first value as too low —
the ruling is recorded on the board) and cleared before anything was committed.

**What changes — one file, `analyse_t11.py`, frozen blob `2d5934ba`'s sibling
`d73290093940595d` (344 lines) -> git blob `ca391ddfca63550a4750c17e1d5ffaa7ecf1da0f`,
sha256 first-16 `ccd39ef1505e763b`, 419 lines (+79 / -4).**

1. **A fifth degenerate class in `classify()`: `NO_DEMONSTRATED_ORDER`.** The
   four frozen rejections (`EXACT`, `STAGNANT`, `OSCILLATORY`, `DIVERGENT`) all
   test the sign and ordering of the error ratio; none tests the magnitude of
   the observed order itself. Measured on the frozen file: a triple whose fine
   and medium errors differ by one part in 1e6 is `CONVERGING` with
   `p = 1.3e-06` and a GCI of 1.407e-03 — a tidy 0.14 % that looks like a
   measurement. Now: if `p < P_MIN` the triple is `NO_DEMONSTRATED_ORDER`; the
   order is still returned and printed beside the row, as rule 5 requires.
2. **`P_MIN = 0.5`, supervisor's ground.** T11's registered expectation is
   `p` in `[1.5, 2.5]` (§11 P2, second-order scheme). At `r = 2`, `p < 0.5`
   means adjacent-level errors differ by less than `2^0.5 = 1.41x` — the
   "levels too close to resolve an order" state T3 measured — and a GCI formed
   by dividing by `(2^p - 1)` there is a number that looks like a measurement.
3. **The GCI and the Richardson extrapolate are REFUSED below `P_MIN`** (return
   `None`; printed as `REFUSED`), in addition to the frozen refusal for a
   non-monotone triple.
4. **`apply_gate()` gate (2)** now also sends `NO_DEMONSTRATED_ORDER` to
   `NOT A RESULT`, naming `p` and `P_MIN` in the reason.
5. **`--selftest`** drives the degenerate triples through the same
   `apply_gate()` that grades the rung: ratios `1+1e-6`, `1+1e-3`, `1+0.1`
   (`p` = 1.3e-06, 1.4e-03, 0.138) must each be `NOT A RESULT` with no GCI;
   `2^0.6` (`p` = 0.600, just above the floor) and a healthy second-order
   triple (`p` = 2.000) must each be `PASS` with a GCI present. Prints
   `SELFTEST PASS` / `FAIL`, exits 0 / 1. Run before this commit under both
   `python3` and `python3 -O`: **PASS, rc = 0, identical output.** Forced
   failure shown under `-O`: with `P_MIN` forced to 0.05 in-process, the
   `1+0.1` row grades `PASS` with GCI 1.250e-08 and the selftest returns 1.
   No `assert` statement was added (AST count 0).

**Direction.** This amendment can only move rows **INTO** `NOT A RESULT`. No
gate threshold, band, cap, timeout, rank count, reference value, or verdict
label is loosened; every row that graded `NOT A RESULT` under the frozen file
still does. §6.1's band, §10's costs and caps, and §11's predictions are
untouched. The §12 freeze-set line for `analyse_t11.py` is superseded by the
hashes above; the other five instruments are byte-identical to the freeze.

**lines whose number changed above this section: 0**
