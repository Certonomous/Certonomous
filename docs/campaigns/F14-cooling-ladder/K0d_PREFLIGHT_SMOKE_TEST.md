# K0d pre-flight smoke test — AMENDMENT 2 §A2.4, executed 2026-08-25

**Verdict: `PASS`.**

**What that verdict covers, quoted from the clause that registered it**
(`K0d_PREREGISTRATION.md` `AMENDMENT 2` §A2.4 clause 4): *"On success it proves
ONE thing and it is stated narrowly: the dictionaries are sufficient for the
solver to take a step in this regime. It is **not** evidence about the physics,
the mesh quality, convergence, or any graded quantity, and it may not be cited as
such."* **Nothing in this file may be cited for physics, mesh, convergence or any
graded quantity. It is not a K0d result and it grades nothing.**

**K0d remains `FROZEN, ARMED AND UNFIRED`.** This test does not authorise the
launch; `AMENDMENT 4` §A4.10 states why, and the supervisor's diff read of
`AMENDMENT 4` is the undelegatable check that stands between this and graded
compute.

---

## 1. The four registered conditions of §A2.4, each met and each shown

| § A2.4 clause | requirement | what was done | met |
| --- | --- | --- | --- |
| 1 | **one timestep on the COARSEST mesh**, with K0d's own `constant/`, `system/` and `0/` dictionaries | `endTime 1`, `deltaT 1`, `startTime 0`; **L1, 25 600 cells**, §4's design value **exactly** | **YES** |
| 2 | **in a scratch directory OUTSIDE `verification/runs/`** | `/home/ubuntu/certonomous-runs/K0d_smoke_L1/` | **YES** |
| 3 | **on failure: ABORT, no graded solve, the failure is a finding triaged by the supervisor** | did not arise — `rc = 0` | n/a |
| 4 | **on success it proves one narrow thing and may not be cited further** | stated at the head of this file and repeated at §5 | **YES** |

**`verification/runs/F14-cooling-ladder/K0d_runs/` was NOT created**, before,
during or after this test. Re-checked after the solver exited:
`find verification/runs -iname '*K0d*'` returns **nothing**, and
`ls -d verification/runs/F14-cooling-ladder/K0d_runs` returns
*No such file or directory*. **The one-character control
`find verification/runs -iname '*K0c*'` returns run directories**, so the finder
is shown able to report a match (rule 3 applied to a search).

---

## 2. What ran, and what it measured

**Environment:** OpenFOAM `v2606` (`api=2606, patch=0`),
`/usr/lib/openfoam/openfoam2606`, single rank, serial, 2D.

| step | result |
| --- | --- |
| `blockMesh` | **`rc = 0`**, `End` line present, **`nCells: 25600`** — equal to §4's L1 design value **exactly** |
| `checkMesh` | **`rc = 0`**, `Mesh OK.`, max aspect ratio **21.00124**, non-orthogonality **max 0, average 0**, total volume **0.010816 m³** = `1.04 × 1.04 × 0.01` |
| `buoyantBoussinesqSimpleFoam` | **`rc = 0`**, `End` line present, **`Time = 1` reached**, `ExecutionTime = 0.24 s` |

**All seven fields of `AMENDMENT 3` §A3.4's `kOmegaSST` completion set were
written at time `1`:** `T`, `U`, `p_rgh`, `alphat`, `nut`, `k`, `omega` — each a
non-empty file. **This is the narrow claim, and it is now measured rather than
assumed.**

**Residual behaviour on the single iteration, reported and NOT interpreted:**
`Ux` 1 → 9.07e-4, `Uy` 1 → 1.67e-2, `T` 1 → 4.46e-3, `p_rgh` 1 → 7.30e-3 in 14
GAMG iterations, `omega` 2.16e-2 → 1.23e-4, `k` 1 → 6.95e-3; time-step continuity
error `sum local 8.38e-05`, `global -2.74e-06`. **One iteration of a steady SIMPLE
solve says nothing about convergence and none of these numbers is a K0d result.**

**One observation carried honestly rather than omitted:** the log contains
`bounding omega, min: -69.947402 max: 4184.7156 average: 167.3933` on the first
iteration. **A bounding message on iteration 1 of a SIMPLE solve from a uniform
initial field is ordinary and is not a failure** — the run reached `Time = 1`,
exited `rc = 0` and wrote every field. **It is recorded because a message a
reader would notice should not first be seen by them in the log**, and because
`AMENDMENT 2` §A2.3's whole point is that latent defects do not announce
themselves. **If it persists across the graded run it is a finding for that run,
not for this test.**

---

## 3. THE INPUT THIS TEST EXISTS TO EXERCISE — `AMENDMENT 4`'s inlet `omega`

The dictionaries carry **`AMENDMENT 4` §A4.3's registered inlet
`omega = 51.2 s⁻¹`** on the inlet patch `x = 0, y ∈ [1.022, 1.040]`, computed as
`ε / (C_mu k) = 5.76e-3 / (0.09 × 1.25e-3)`, with inlet `k = 1.25e-3 m²/s²` from
§3.2 and `C_mu = kOmegaSST`'s `betaStar = 0.09` read from
`kOmegaSSTBase.C:341`. **Before `AMENDMENT 4` this case could not have been
built without an unregistered choice; the solver has now taken a step with the
registered value.**

---

## 4. TWO THINGS THIS TEST MEASURED THAT WERE PREVIOUSLY ONLY EXPECTED

**FIRST — `phi` IS written.** `AMENDMENT 4` §A4.7 disclosed and carried Finding 4:
guards `HB` and `MB` read `phi`, which is in no registered completion field set,
and the disclosure rested on `buoyantBoussinesqSimpleFoam` writing it and on
completed **sibling** cases having it. **Measured here on K0d's own dictionaries:
time directory `1` contains `phi`** (and `p`) alongside the seven registered
fields. **The disclosure is now supported by K0d's own case rather than by
inference from siblings.** It does **not** repair Finding 4 — `phi` is still in no
completion field set, and only the supervisor can put it there in the
still-open pre-compute window.

**SECOND — the field set is EXACTLY the registered set plus `p` and `phi`.**
Nothing the completion rule demands is missing, and nothing unexpected appears.

---

## 5. WHAT THIS TEST DOES NOT ESTABLISH — stated so it cannot be borrowed

- **Not physics.** One iteration from a uniform field. No graded quantity of
  §7.3 was computed and none could be.
- **Not the mesh.** `checkMesh` reporting `Mesh OK` is **not** §4's mesh gate.
  **`check_k0d_mesh.py` conditions A–G were NOT run** — the script does not exist
  yet (see below) — and its **planted-positive test has not fired**. Condition A
  (cell count) happens to be satisfied at 25 600, and that single coincidence is
  not the gate.
- **Not convergence.** §6's criterion is a change between checkpoints at
  `endTime − 4000` and `endTime`. This run has one timestep.
- **Not the graded case.** See §6.

---

## 6. THE DICTIONARIES ARE SCRATCH DRAFTS, NOT THE GRADED CASE — registered plainly

`AMENDMENT 4` §A4.9 Finding 7 recorded that **`build_k0d.py` does not exist on
disk**, checked against two working controls. It still does not. **The
dictionaries exercised here were written for this smoke test and are the first
K0d dictionaries to exist anywhere.**

**Registered consequence, so it cannot be discovered later:** the graded run is
built by **`build_k0d.py` under §9**, with **`AMENDMENT 4` §A4.3's inlet
`omega`**, and its mesh must pass **`check_k0d_mesh.py`'s conditions A–G with the
planted-positive test FIRING** (§4). **These scratch dictionaries are not
promoted to the graded case by having passed this test**, and §A2.4 clause 4
already forbids citing this test for anything but the one narrow claim.

**Three inputs the smoke test had to choose that the pre-registration does not
register, disclosed in full and NOT registered by this lane:**

1. **`beta` and `TRef`** for the Boussinesq expansion. Used here:
   `beta = 3.2657e-3 K⁻¹`, `TRef = 298.15 K`. **`beta` is DERIVABLE, not free** —
   from §3.4's registered `Ra = 2.13e9`, §3.1's `H = 1.04 m`, §3.2's
   `ΔT = 20 K`, `ν = 1.55e-5 m²/s` and `Pr = 0.71`:
   `beta = Ra·ν·α / (g·ΔT·H³) = 2.13e9 × 1.55e-5 × 2.1831e-5 / (9.81 × 20 × 1.124928) = 3.26577e-3 K⁻¹`;
   the dictionary carries **3.2657e-3**, that value rounded, and the rounding is
   stated rather than left for a reader to notice.
   **But it is nowhere written down in the pre-registration**, and **§3.3's
   disputed floor temperature moves it**: at `ΔT = 20.5 K` the same arithmetic
   gives **3.18612e-3 K⁻¹**, a **2.44 %** difference — the same 2.5 % §3.3 already
   registered on the driving difference, now shown to propagate into `beta`.
   **Referred to the supervisor. This lane does not register it.**
2. **Wall and outlet boundary TYPES for the turbulence fields.** §3.2 registers
   the outlet as *"zero gradient on `U`, `T` and every turbulent variable"* and
   §5 registers **wall-resolved, `y⁺ ≤ 1`**; the specific type names used here
   (`kLowReWallFunction`, `omegaWallFunction`, `nutLowReWallFunction`,
   `alphatJayatillekeWallFunction` with `Prt 0.85`) are **consistent with both**
   but are **not themselves registered**. Referred.
3. **Discretisation schemes and relaxation.** `fvSchemes` and `fvSolution` here
   are ordinary steady-SIMPLE choices. **The pre-registration registers no scheme
   set**, and schemes are a discretisation-error question that §4's ladder and
   §8.3's Roache gating are built to bound. Referred, and **noted as the one of
   the three most likely to matter to a graded number.**

**None of the three is registered by this file. A smoke-test record is not a
pre-registration**, and a lane may not register an input by using it (rule 9).

---

## 7. Cost, and the estimate-versus-actual comparison

`AMENDMENT 2` §A2.5 registered the cost as *"one timestep on the coarsest mesh —
**seconds**, well inside the \$25 pre-authorisation, \$-negligible, derived not
measured"*, and registered **no cap**.

| | value |
| --- | --- |
| **predicted** (§A2.5) | *"seconds"*, no cap, `$`-negligible **derived, not measured** |
| **actual, measured from the log** | solver `ExecutionTime` **0.24 s**; wall for the solver invocation **0.30 s**; `blockMesh` and `checkMesh` each sub-second |
| **actual in the lab's unit** | `0.30 s × 1 rank ÷ 60 =` **0.005 core-min** for the solve; **< 0.1 core-min** for the whole pre-flight including mesh generation and `checkMesh` |
| **ratio actual/predicted** | **inside the predicted order of magnitude.** *"Seconds"* is not a number, so no numeric ratio is claimed and none is invented |
| **attribution of the gap** | none to attribute: no contention, no waste, no stall (§6 of `COMPUTE_BUDGET_CHARTER.md`) |
| **dollars** | at the recorded `$0.0513/core-h`, **< \$0.0001 — DERIVED, NOT MEASURED**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

**Charged to K0d's rung**, as §A2.5 registers. **The registered POINT of 829.36
core-min and CEILING of 2 484.84 core-min are untouched** and this spend is
inside neither's graded accounting because no graded case ran.

**The calibration-ledger row is NOT written by this lane.** Rule 12 requires the
estimate-versus-actual comparison to land as a row in `docs/COST_CALIBRATION.md`;
this lane was instructed not to touch that file, so **the comparison is made
above in full and the ledger row is left for the supervisor**. This sentence is
the notice that it is outstanding.

---

## 8. Artifacts, by path

- Case, logs and the time directory `1`:
  **`/home/ubuntu/certonomous-runs/K0d_smoke_L1/`** — outside git and outside
  `verification/runs/`, per §A2.4 clause 2.
- Logs: `log.blockMesh`, `log.checkMesh`, `log.buoyantBoussinesqSimpleFoam`.
- Written fields: `1/{T,U,p_rgh,alphat,nut,k,omega}` plus `1/p` and `1/phi`.
- **These are scratch artifacts.** A number quoted from them is quoted from a
  smoke test and must say so.

*Written by the heat-transfer lane, 2026-08-25. Submissions remain **PARKED**.*
