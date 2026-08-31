# JF1 L1 — UNBLOWN NACA 0012, alpha = 0 — FEASIBILITY READOUT

**LABEL: `feasibility`. NO GATE SCORES ANYTHING ON THIS RUN.** No gate, threshold
or verdict of the fixed vocabulary (`PASS` / `GATE REACHED` / `GATE FAIL` /
`NOT A RESULT` / `BLOCKED` / `PENDING`) attaches to it. It counts toward no
result column and no challenge column. No GCI, no observed order and no `PASS`
is computed, quoted or implied here, and none may be derived from it downstream.
Where a number below disagrees with `verification/campaign/JF1_PREREGISTRATION.md`
that is a **finding**, reported as such — never a gate failure.

Authority: Sanaa's SANAA-DIRECT of 2026-08-31, commit `927924f1`, verbatim —
*"start the L1 feasibility solves on Cases 1 and 2 NOW — no freeze required for
feasibility/physics rungs, never was."*

---

## 1. What ran

| | |
|---|---|
| row | UNBLOWN, `C_mu` = 0, alpha = 0 deg, `jetSlot` treated as a **WALL** (noSlip) |
| solver | `simpleFoam`, steady, incompressible, `kOmegaSST`, OpenFOAM v2606 |
| wall treatment | `nutLowReWallFunction` + `omegaWallFunction`, low-Re, **no wall functions in the log-law sense** |
| physics | `Re_c` = 1.0e6, c = 1 m, `U_inf` = 10 m/s, nu = 1.0e-5 m²/s |
| ranks | 1 (serial) |
| launched | 2026-08-31T15:40:37Z, pid 67215, by the detached queue runner |
| finished | 2026-08-31T16:04:23Z, launcher **rc 0**, `stage_at_exit` `done` |
| cost | **23.7667 core-min MEASURED** (wall 1426 s × 1 rank ÷ 60) against a 45.0 core-min registered cap |

The registration cited by the launch is `b52ed93b`, which is **not** the freeze
commit `12b1bd84` (the registration was frozen at 15:29Z, while this lane was
building the mesh). That is lawful here and only here: **a feasibility rung
requires no freeze**, and no gate of that registration scores on this run. It is
recorded rather than glossed because the launcher was subsequently hardened by a
peer to pin the freeze commit and blob, and would now refuse this invocation.

## 2. Mesh — MEASURED by `checkMesh` on disk (`log.checkMesh`)

| metric | measured | JF1 draft gate | lab standard |
|---|---|---|---|
| cells | **39 984** (408 tangential × 98 normal × 1 span) | ~40 k target | — |
| max non-orthogonality | **57.53** (average 10.03) | < 65 | < 70 |
| max skewness | **2.296** | < 4 | < 4 |
| negative volumes | **0** | exactly 0 | exactly 0 |
| max aspect ratio | **859.95** | reported; > 1000 needs justification | advisory 1000 |
| `checkMesh` overall | **`Mesh OK`** | must print it | — |

**Recorded choices** (Sanaa §1.2/§1.3 *"record which"*), printed by
`build_jf1.py` at every build so they cannot be lost from a report:

- **Topology: O-MESH**, not C-mesh. Farfield a circle of radius 26.0 m about the
  quarter chord; minimum body-to-farfield distance **25.25 c**, so the ≥ 25 c
  requirement holds at the trailing edge and not merely at the leading edge.
- **`jetSlot` is a WALL** in this row. With no jet there is no jet BC, so the
  known defect at an unblown slot — `k = 1.5 (I V_j)² = 0` and `omega = 0` —
  cannot bite. The slot is carried as its own patch, so the blown row needs a BC
  change and `--slot-type patch`, not a new script.
- Section truncated at `x = 0.991271` of the raw NACA table and rescaled by
  `1.008806`, so the chord is exactly 1 m and the blunt base exactly 5.000 mm.

**DISCLOSED LIMITATION.** An O-mesh does **not** satisfy §1.3's wake box (3 c
behind the TE at BL-comparable spacing) — it coarsens circumferentially with
radius. **This mesh is admissible for the unblown feasibility row only; a
C-topology is required before any blown or gated row.**

## 3. Near-wall distribution — RE-DERIVED SO IT CLOSES

The draft's §4.3 registered `y1`, `g`, `N`, the farfield distance **and** an
in-`delta` count, which is one constraint too many; no three of them agreed with
the rest. The distribution below is solved, not asserted, and `build_jf1.py`
**refuses to emit** a level violating it. The arithmetic is printed at every
build into `log.build_jf1`.

```
  delta(x=c) = 0.37 c Re^-0.2                    = 2.334542e-02 m
  y1 (first-cell HEIGHT)                         = 5.000000e-06 m
  farfield radius about c/4                      = 26.0 m
  N = 97 would need g = 1.150131                 -> ABOVE the 1.15 cap, refused
  N = 98, g SOLVED from y1(g^N - 1)/(g - 1) = 26 = 1.148350   <= 1.15
  stack reaches                                  = 26.000000000 m, residual 4.09e-13
  COMPLETE layers inside delta                   = 47      (floor 30; draft floor 36)
```

All five quantities — `y1`, `N`, `g`, the farfield distance and the in-`delta`
count — close simultaneously.

**`y+` is MEASURED from the solved field, never assumed** (`yPlus` function
object, `postProcessing/yPlus/0/yPlus.dat`, Time 8000):

| patch | min | max | average |
|---|---|---|---|
| `airfoil` | 2.3472e-02 | **1.9142e-01** | 1.1360e-01 |
| `jetSlot` | 1.9730e-02 | 6.9193e-02 | 4.1394e-02 |

`max(y+) = 0.191`, i.e. **5.2× inside the ≤ 1 ceiling**.

**FINDING — §4.3.2's `y+` envelope is conservative by 2.6× on this row.** For
`C_mu = 0, alpha = 0` that section predicts `y1 = 1.0054e-05 m` for `y+ = 1`, so
at the registered `y1 = 5.0e-06 m` it predicts `max(y+) ≈ 0.497`. Measured:
**0.191**. The envelope evaluates a turbulent flat-plate correlation at
`x = 5.0e-04 m`, where the real flow is a stagnation boundary layer, and it
over-predicts `u_tau` there as its own text warns it might. The margin is in the
safe direction and no gate rests on it; it is recorded because a 2.6×
conservatism in `y1` is paid for in cells on every level of the ladder.

## 4. The converged coarse field — the answer Sanaa asked for

At Time 8000 (`postProcessing/forceCoeffs/0/coefficient.dat`):

| quantity | value |
|---|---|
| **Cd** | **1.103778e-02** |
| **CL** | **5.505955e-05** |
| CmPitch | −3.719509e-07 |

`Aref = c × span = 0.01`, so these are per-unit-span 2-D coefficients;
`Aref = 1.0` would have reported both 100× too small.

**Physical reading.** CL = 5.5e-05 and Cm = −3.7e-07 are zero to the precision
the discretisation can hold — the correct answer for a symmetric section at
alpha = 0, and a check the mesh could easily have failed asymmetrically. Cd =
1.104e-02 for a fully-turbulent NACA 0012 at `Re_c` = 1e6 sits in the range
general practice reports for this body and Reynolds number. **No comparand on
this box was consulted, and this run scores against none** — it is a sanity
reading, not a validation.

**Iterations and stationarity.** 8000 iterations, `End` written, last time ==
`endTime` = 8000, `simpleFoam` rc 0. Over the last 2000 iterations
(6000 → 8000):

```
  |dCd| = 1.958e-08     (Sanaa section 1.4 absolute bound |dCd| < 1e-5)
  |dCL| = 4.947e-07     (Sanaa section 1.4 absolute bound |dCL| < 1e-4)
  Cd range over the window: 1.1037699e-02 .. 1.1037908e-02
```

i.e. **500× and 200× inside the registered stationarity bounds.**

Continuity at Time 8000: `sum local = 1.853e-11`, `global = −5.683e-12`,
cumulative `−3.615e-07`. The instantaneous local error is 540× inside §1.4's
`< 1e-8`; the *cumulative* figure is a running sum over 8000 iterations and is
not the quantity that bound names — that ambiguity in §1.4 is noted, not
resolved here.

## 5. FINDING — THE FROZEN RESIDUAL CRITERION IS NOT REACHABLE ON THIS CONFIGURATION

§1.4 registers *"residuals p, Ux, Uy, k, omega < 1e-6 (ALL channels the same
order)"* together with *"hit cap -> NOT A RESULT, never 'close enough'."*

Measured initial residuals, sampled through the run:

| channel | iter 2000 | 4000 | 6000 | 8000 |
|---|---|---|---|---|
| `p` | 4.039e-06 | 3.917e-06 | 3.992e-06 | 4.557e-06 |
| `Ux` | 2.111e-08 | 2.138e-08 | 2.089e-08 | 2.262e-08 |
| `k` | 3.556e-06 | 3.541e-06 | 3.556e-06 | 3.457e-06 |

`Ux` is three orders inside the criterion. **`p` and `k` are FLAT from iteration
2000 to 8000 at roughly 4× the criterion** — they plateau, they do not descend.
Running to §1.4's 20 000-iteration cap would not change that; it would spend
~35 more core-minutes to arrive at the same floor.

**The consequence for the gated campaign, stated plainly.** On this
configuration the frozen criterion would label **every** row `NOT A RESULT`
while the force coefficients are stationary to eight significant figures. That
is a pre-registration defect, not a solver failure, and it is the supervisor's
and Sanaa's to rule on — this lane changes no threshold.

**What I did NOT determine.** I have not isolated the cause of the plateau. Two
explanations are consistent with everything measured and I ran no control that
separates them: (a) limiter chatter — `cellLimited` gradients and
`limitedLinear` on `k`/`omega` switching cell-by-cell between iterations, which
holds a residual floor while the integrated force is unaffected; (b) weak
physical unsteadiness off the blunt 5 mm base, which is a bluff body a steady
solver cannot drive to zero. The Cd spread over the window is 2.1e-08, which is
very small for shedding and mildly favours (a), but that is an inference and not
a measurement. **Naming a cause here would be a guess presented as a finding.**

## 6. Other findings

- **§1.4's two farfield `omega` recipes disagree by 22×.**
  `omega = sqrt(k)/(C_mu^0.25 L)` with `L = 0.1 c` gives 0.2236 1/s, i.e. a
  freestream eddy-viscosity ratio `nut/nu = 67`, which contaminates the boundary
  layer. The section's own alternative *"or via viscosity ratio nut/nu = 3"*
  gives 5.0 1/s. **The alternative was taken** and the discrepancy is written
  into `0/omega` at the point of use. Note also that `C_mu` names two different
  things in §1.1 and §1.4 — the jet momentum coefficient and the `kOmegaSST`
  constant 0.09.
- **The O1 blow-up bound** `max|U| < 2 max(V_j, U_inf)` = 20.0 m/s does not bind
  at alpha = 0 and was not approached.

## 7. Artifacts, all retained, none under `TMPDIR`

| what | path |
|---|---|
| this run | `verification/runs/JF1_jet_flap/JF1_L1_UNBLOWN_A0/` |
| solver log, `checkMesh`, build arithmetic | `log.simpleFoam`, `log.checkMesh`, `log.build_jf1` |
| forces, `y+`, min/max, solver info | `postProcessing/` |
| fields | `1000/` … `8000/` |
| launcher status, solver rc | `RUN_STATUS.JF1_L1_UNBLOWN_A0.txt`, `SOLVER_RC.txt` |
| independent evidence snapshot | `../JF1_L1_UNBLOWN_A0_EVIDENCE_2026-08-31T1601Z/` |
| attempt 1, FAILED, retained | `../JF1_L1_UNBLOWN_A0.attempt1_FAILED_2026-08-31T1538Z/` |
| cost-calibration pilot | `../_pilot_2026-08-31T1535Z/` |
| mesh generator, launcher, dictionaries | `cases/JF1_JET_FLAP/` |

The evidence snapshot exists because `cases/JF1_JET_FLAP/run_jf1.sh` was edited
in place by a peer at 15:55:57Z while `bash` was still executing it, 15 minutes
into this solve. Editing a running shell script can shift the byte offset the
interpreter resumes from. The wrapper in fact completed correctly (rc 0,
`stage_at_exit` `done`), so no harm was done — but the snapshot was taken before
that was known, and it is kept as the independent copy of the physics.
