# RESULTS — VMFL038-R2: Falling Film Over an Inclined Plane

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, printed p.131-132.**
Graded **2026-08-31T20:03Z** by `ansys-lane-opus` (Opus 5) against the frozen
pre-registration `cases/ansys_verification/VMFL038-R2/PREREGISTRATION.md` at freeze
commit **`9a6aea9b8f1c63dcd3135798cb9dbca3b3b84f3e`**.

## ROW VERDICT: **`PASS`** — both limbs

| limb | quantity | verdict | value at L3 | reference | band | margin |
|---|---|---|---|---|---|---|
| **A** | `tau_w`, physical wall shear, Pa | **`PASS`** | 39.239999983452442 | 39.24 (exact) | `FLOOR_REL` = 1e-8 | worst level deviation **4.217e-10**, 24x inside |
| **B** | `u_bar`, mean film velocity, m/s | **`PASS`** | 0.13081021868265238 | 0.1308 (exact) | `TOL_B` = 0.005 | deviation **7.812e-05**, **64x inside** |

Row verdict is the weakest limb verdict. Both limbs `PASS`, so the row is **`PASS`** —
this lab's **tenth** credential from this suite.

**AND THE HONEST LIMIT OF LIMB A, WHICH THE ROW CARRIES VERBATIM:**

> **LIMB A VERIFIES CONSERVATION, NOT ACCURACY. Its `PASS` is a floor demonstration and
> nothing more.**

`tau_w` is exact **by the conservation structure of the scheme** (`PREREGISTRATION`
§3.3), so limb A does not test how accurately anything is resolved. It tests that the
implementation conserves momentum, **which it does by construction**. A coding error in
the flux assembly, a wrong `nu`, a mis-set boundary condition or the kinematic/physical
confusion of §5.4 would each break it — but the claim is **very nearly tautological**
and must not be read as an accuracy result. **Limb B is where this case's verification
content lives.**

---

## 1. THE FROZEN POINT PREDICTIONS AGAINST WHAT WAS MEASURED

`PREREGISTRATION` §10 registered these to eight or more significant figures **before
any graded compute**. This is the falsifiable content of the freeze and it is reported
first.

| quantity | **PREDICTED (frozen §10)** | **MEASURED** | agreement |
|---|---|---|---|
| `u_bar` L1 | **0.13096350000** | 0.1309634999999747 | **2.5e-14 abs** |
| `u_bar` L2 | **0.13084087500** | 0.13084087499992711 | **7.3e-14 abs** |
| `u_bar` L3 | **0.13081021875** | 0.13081021868265238 | **6.7e-11 abs — 10 significant figures** |
| `tau_w`, every level | **39.24 to <1e-8 rel** | 2.263e-13 / -1.744e-12 / -4.217e-10 rel | inside, by 24x at the worst level |
| `d21` | **-1.22625000e-04** | -1.2262500004686e-04 | 7 s.f. |
| `d32` | **-3.06562500e-05** | -3.0656317e-05 | 6 s.f. |
| `R = d32/d21` | **0.25** | **0.2500005485245849** | 6 s.f. |
| observed order `p` | **2.0000000** | **1.9999968345886787** | **5 s.f.** |
| fine-grid GCI | **9.7648e-05** | **9.764912120872237e-05** | **5 s.f.** |
| profile shift `K h²/8` L1/L2/L3 | 1.2262500e-04 / 3.0656250e-05 / 7.6640625e-06 | 1.226250000e-04 / 3.065624986e-05 / 7.663995147e-06 | 10 / 9 / 6 s.f. |

**L3'S THREE PREDICTIONS HAD NEVER BEEN OBSERVED BY ANYBODY** — the pre-freeze probe
was deliberately not converged at 360x80, and `PREREGISTRATION` §7.1 says so in the
frozen bytes. `u_bar` at L3 came back at **0.13081021868265238** against a registered
**0.13081021875**: **ten significant figures, on a number nobody had seen.** That is
the strongest single piece of evidence this registration produced, and it is what §0.1
traded the probe's disclosure cost for.

**AND ONE REGISTERED PREDICTION THAT IS PARTIALLY FALSIFIED — reported because the
comparator measured it and the honest reading is not the flattering one.** §10 predicted
`u_max` **machine-exact at every level**, and the comparator's `machine_exact` flag uses
a 1e-12 relative bar:

| level | `u_max` measured | rel dev | `machine_exact` at the 1e-12 bar |
|---|---|---|---|
| L1 | 0.19620000000000001 | -1.415e-16 | **True** |
| L2 | 0.19619999999900001 | -5.097e-12 | **False** |
| L3 | 0.196199999894 | -5.403e-10 | **False** |

**The prediction holds at L1 and misses at L2 and L3 by five and ten orders below the
band it would have been gated against — but it misses, and "machine-exact at every
level" was the registered wording.** The departure tracks the iterative residual floor
(2.8e-13 / 5.5e-14 / 7.6e-13) and the accumulated round-off of a longer solve, not any
discretisation effect: the profile error still matches `K h²/8` to six significant
figures at L3, which is the discretisation channel. **`u_max` is a REPORTED, NOT GATED
diagnostic** (`PREREGISTRATION` §1 line 6 — the VMFL070 trap), so **no verdict moves**.
It is recorded here rather than quietly dropped because R1's post-mortem turned on
exactly this quantity: R1's `u_max` was **0.89 % low**; R2's worst level is **5.4e-10
low**, an improvement of seven orders, and the residual gap is honestly a miss against
the registered word "machine-exact".

---

## 2. WHAT R2 CHANGED AND WHETHER IT WORKED

R1 (row **#47**, **`NOT A RESULT`**, which **stands**) died of a `DIVERGENT` triple with
`R = 9.051` on a one-dimensionally refined ladder. Three changes were registered.

| # | change | did it work |
|---|---|---|
| **1** | **ISOTROPIC ladder** — `Nx` and `Ny` both x2 per level; cells x4; `dx/dy` constant | **YES.** `checkMesh` birth certificates: cells **1 800 / 7 200 / 28 800** (each equal to the frozen expectation, refused otherwise), **max AR 4.0 / 4.0 / 4.0**, max skewness 8.3e-14 / — / 3.3e-13, max non-orthogonality **0.0** at every level, `Mesh OK` at all three. R1 was 7 200/14 400/28 800 with AR 4 → 8 → 16. |
| **2** | **`residualControl` REMOVED**; fixed per-level `endTime` past the momentum residual floor; convergence decided by the comparator's disjunction | **YES, and it is the change that mattered most.** Final `Ux` initial residuals **2.814e-13 / 5.450e-14 / 7.571e-13** — R1's were 7.889e-07 / 1.467e-06 / 3.721e-06 and *grew* down the ladder. All three levels reached `Time == endTime` exactly (8000 / 16000 / 32000) with one `End` line each and `rc = 0`. |
| **3** | **Triple moved off `tau_w` onto `u_bar`**; `tau_w` kept as a no-triple floor demonstration | **YES, and §3.3's proof is confirmed on the graded bytes.** `tau_w` is mesh-invariant to **4.219e-10** across a 16x cell-count range. Had the triple stayed on `tau_w`, its differences would have been ~1e-11 relative — below `EXACT_REL` — and the row would have graded **`EXACT` → `NOT A RESULT`** for the second time. |

---

## 3. THE CONVERGENCE DISJUNCTION EARNED ITS KEEP AT L3

`PREREGISTRATION` §6.2's clause accepts a level on **C1 OR C2**, never both.

| level | limb satisfied | C1 (final `Ux` ≤ 1e-10) | C2 (both channels' rel p2p ≤ 1e-9 over the last 25 %) |
|---|---|---|---|
| L1 | **C1** | True, 2.8138e-13 | True (tau 1.02e-12, ubar 7.64e-13), 20 samples |
| L2 | **C1** | True, 5.4504e-14 | True (tau 2.00e-11, ubar 2.45e-11), 40 samples |
| **L3** | **C1** | True, 7.5712e-13 | **False** (tau **1.07e-09**, ubar **1.31e-09**), 80 samples |

**L3's C2 limb FAILED, by 7 % and 31 % over the 1e-9 plateau tolerance, and C1 carried
it.** Had the clause been written as VMFL006's **conjunction** — a residual floor
**AND** a flat functional — **L3 would have refused and VMFL038-R2 would be a second
`NOT A RESULT`.** The disjunction was designed against VMFL006's failure and it is the
reason this row exists. It is recorded as a live near-miss, not as a design triumph:
the L3 plateau tolerance is marginal on this case and a future registration should size
`PLATEAU_TOL` against the round-off the level actually carries rather than against a
round number.

---

## 4. THE CONTROLS — all fired, on the graded bytes

**PLANTED ZERO, BOTH CHANNELS, ALL THREE LEVELS — SIX RECORDS, six passes.** Planted to
disk on a COPY of the real solver bytes, read back through the PRODUCTION reader, and
the FULL gate functional recomputed.

| level | channel | plant | gate moved | expected | worst readback error |
|---|---|---|---|---|---|
| L1 | PLANT-A `wallShearStress` | 2.4525e-03 kin | 1.962000000 Pa | 1.962000000 Pa | 1.735e-18 |
| L1 | PLANT-B `U` | 9.810e-03 m/s | 9.810000000e-03 | 9.810000000e-03 | 1.214e-17 |
| L2 | PLANT-A | 2.4525e-03 kin | 1.962000000 Pa | 1.962000000 Pa | 1.735e-18 |
| L2 | PLANT-B | 9.810e-03 m/s | 9.810000000e-03 | 9.810000000e-03 | 1.214e-17 |
| L3 | PLANT-A | 2.4525e-03 kin | 1.961999999 Pa | 1.961999999 Pa | 3.469e-18 |
| L3 | PLANT-B | 9.810e-03 m/s | 9.809999995e-03 | 9.809999995e-03 | 1.214e-17 |

**PHASE ORDER, recorded by the comparator itself** in `phases_executed`:
`0 AST guard` → `1 discovery` → **`2 PLANTED ZERO (both channels, all levels)`** →
`3 completion` → `4 convergence` → `5 functionals` → `6 triple and verdict`. The plants
precede every clause that can refuse, which is the VMFL006 fix (its plant list was
empty because a refusal fired ahead of it).

**Other controls, on the graded path:** AST guard `ast.Assert` **0** / `ast.Raise` 46,
counted from source so the number is identical under `-O`; `one_match()` cardinality
guard on every file opened; NUMERIC time-directory selection cross-checked against each
log's last `Time`; per-level age guard — all five fields at `endTime` newer than **that
level's own** `0/U`; wall-shear streamwise uniformity 9.378e-11 / 3.874e-11 / 6.116e-12,
far inside `UNIFORM_TOL` 0.05.

**At launch, before a core-minute was spent:** 13 frozen files hashed equal to their
HEAD blobs; comparator `--selftest` **45/45, 0 failures, rc 0** under **both** `python3`
and `python3 -O` with equal PASS/FAIL counts and the AST marker in both, 20 named
controls driven; mesh generator `--selftest` 23/23 under both; token-subset containment
green on both templates; controlDict value-position check `endTime=8000/16000/32000`,
`writeInterval` equal to it, FO intervals `['100']`; **`writeFields` present in 2/2
`fieldValue` blocks at every level.**

---

## 5. COST — MEASURED, AND THE CALIBRATION AGAINST THE FROZEN BRACKET

| level | cells | `endTime` | wall s | **core-min MEASURED** | s per cell-iteration |
|---|---|---|---|---|---|
| L1 | 1 800 | 8 000 | 11 | **0.1833** | 7.64e-7 |
| L2 | 7 200 | 16 000 | 75 | **1.2500** | 6.51e-7 |
| L3 | 28 800 | 32 000 | 648 | **10.8000** | 7.03e-7 |
| | | | | **12.2333 TOTAL** | |

- **PREDICTED (frozen §7.2): a BRACKET, 17.0 – 33.8 core-min.** **MEASURED 12.2333.**
- **Ratio actual/predicted = 0.720 against the lower bracket end, 0.362 against the
  upper. The run came in BELOW the registered bracket — an over-prediction, not an
  over-run.**
- **Attribution: MISPREDICTION, not waste and not contention.** The lower bracket priced
  the work at R1's own measured 9.69e-7 s per cell-iteration; R2 ran at **7.03e-7** at
  the same 28 800 cells — **1.38x faster than R1's measured rate on the same box and the
  same solver.** The upper bracket priced the two peer 4-rank jobs that held 8 of 16
  cores during the pre-freeze probe; **those jobs had finished by launch**, so the
  contention the upper bracket existed to cover never materialised.
- **WASTE: ZERO.** No level was re-run, no `timeout` fired, no `rc` was non-zero, no
  `CAP_OVERRUN.txt` was written. **Cap 90 core-min, 13.6 % used.**
- **$ DERIVED, NOT MEASURED: $0.010459** at the owner-stated $0.0513/core-h
  (REPORTED-BY-OWNER, 2026-08-21/22; the box cannot read its own billing,
  `COMPUTE_BUDGET_CHARTER` §5).
- **The cap guard that actually bounded this run was the launcher's per-level
  `timeout ${TIMEOUT_S}s`** — 5400 / 5389 / 5314 s, drawn down from the running total.
  **No `ENFORCE` claim is made for the runner**
  (`docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md:3` — ADVISORY/INERT/OFF).
- **SEPARATELY NAMED AND NOT ABSORBED (`COMPUTE_BUDGET_CHARTER` §6): the pre-freeze
  diagnostic probe cost ≈ 60 core-min of SCRATCH compute** (three levels at 90x20,
  180x40 and 360x80, disclosed in `PREREGISTRATION` §0.1). It is not part of the 12.2333
  and it bought the finding that saved the case. **Total compute attributable to
  VMFL038-R2 is therefore ≈ 72 core-min, ≈ $0.062 derived.**

---

## 6. ARTEFACTS

| artefact | path / sha |
|---|---|
| freeze commit | **`9a6aea9b8f1c63dcd3135798cb9dbca3b3b84f3e`** |
| pre-registration blob | **`fe28e7ec7e0ec273afc279e4fa77622ca7e57bb9`** |
| comparator blob | **`662643863390cecea36ec14f3f0d1a24b5efe91a`** |
| mesh generator blob | **`eb779cfc5b44e711e25f6b3526739c61fe2a3134`** |
| machine-readable grading record | `verification/runs/ansys_verification/VMFL038-R2/GRADING_RECORD_2026-08-31T2003Z.json` |
| launch record / contention / cost | `LAUNCH_RECORD.txt`, `CONTENTION.txt`, `COST.txt`, `RUN_RC.L1|L2|L3` |
| per-level fields | `L1/8000/`, `L2/16000/`, `L3/32000/` (`U`, `p`, `wallShearStress`, `Cx`, `Cy`) |
| mesh birth certificates | `L1|L2|L3/birth_certificate.json` |
| queue entry (launched) | `verification/queue/ansys-verification/launched/VMFL038-R2.json`, committed `04c8349a` |

`grade_vmfl038r2.py --verify-frozen` was run **before** grading: 3/3 OK, disk == HEAD.

---

## 7. THE REGISTER ROW, DRAFTED FOR THE SUPERVISOR

Row number **#51** (max existing is **#50**, re-derived at drafting; assign from the
tail again at commit, `CLAUDE.md` rule 11).

```
| **#51** | **VMFL038-R2** — Falling Film Over an Inclined Plane (VM2026R1, printed **p. 131-132**). **NEW registration succeeding row #47 (`NOT A RESULT`)** per VERIFICATION_CHARTER §6: a new row citing #47, which is not removed, re-labelled or softened. **THREE registered changes: (1) the ordered one — the ladder is ISOTROPIC, Nx and Ny both x2 per level, cells x4, dx/dy CONSTANT at 4 (R1 pinned Nx at 180: cells x2, AR 4 → 8 → 16); (2) `residualControl` REMOVED for a fixed per-level endTime past the momentum residual floor, because R1's p-only stop criterion was blind to the graded quantity and its final Ux residual GREW down the ladder; (3) THE TRIPLE MOVED OFF `tau_w` ONTO `u_bar`.** Change 3 is a correction of the dispatching brief, raised by the lane and upheld in full by the supervisor: **`tau_w` on this problem carries NO discretisation error — it is pinned to the exact value by DISCRETE GLOBAL MOMENTUM CONSERVATION on any mesh at any refinement (proof at PREREGISTRATION §3.3; measured mesh-invariant to 4.219e-10 across a 16x cell range)** — so a Roache triple on it could only ever have graded `EXACT` → `NOT A RESULT`. case/ SIX files byte-identical to R1 (`0/U`, `0/p`, all three `constant/`, `fvSchemes`), THREE differing, one per named change (`diff -rq` and blob sha, both recorded). R1's frozen files untouched | 2026-08-31 | **`PASS`** | **TWO LIMBS, both `PASS`. LIMB B (where the verification content is): `u_bar` at L3 = 0.13081021868265238 m/s vs exact 0.1308, deviation 7.812e-05 = 0.0078 %, inside the frozen 0.5 % band by 64x. Roache triple on `u_bar`, r = 2, Fs = 1.25: coarse 0.1309634999999747 / medium 0.13084087499992711 / fine 0.13081021868265238; state `CONVERGING`; R = 0.2500005; observed order p = 1.9999968; GCI_fine = 9.7649e-05 = 0.0098 %, 205x below the 2 % ceiling. LIMB A: `tau_w` = 39.239999983452442 Pa at L3, worst level deviation 4.217e-10 relative, mesh invariance 4.219e-10, inside the 1e-8 floor. THE FROZEN §10 POINT PREDICTIONS WERE MET TO 10 SIGNIFICANT FIGURES AT L3 — a level NEVER OBSERVED before the freeze (predicted 0.13081021875, measured 0.13081021868265238) — and p, R and GCI to 5-6 s.f.** | Bird, Stewart & Lightfoot, *Transport Phenomena* p.45 — the manual's OWN cited Reference; the EXACT solution of the same continuum model `simpleFoam` discretises, so model-form error is zero by construction. `tau_w` = 39.24 Pa and `u_bar` = 0.1308 m/s, each DERIVED IN THE COMPARATOR by two independent routes in double precision, never transcribed. **The manual's printed geometry "1 m X 18 m" is a 100x units error; the self-consistent 0.01 x 0.18 m is derived from the manual's own printed outlet gauge and 1:18 ratio (`VMFL038/MANUAL_DEFECT_geometry_units.md`, NOT FILED)** (VM2026R1 p. 131-132) | **LIMB B: 0.5 % on `u_bar` at L3, plus `CONVERGING` triple with p ≥ P_MIN = 1.0 and GCI ≤ GCI_MAX = 0.02. THE BAND IS SET BY WHAT A KNOWN PAST DEFECT DOES TO IT, not by what the run was expected to do: R1's measured L3 `u_bar` deficit was 0.82 %, and a 0.5 % band GATE FAILs that run. P_MIN raised from R1's 0.05; GCI_MAX held at 0.02 but now 4x the band it qualifies rather than equal to it. LIMB A: FLOOR_REL = 1e-8 at every level AND mesh invariance ≤ 1e-8, from an a-priori sqrt(N_cell·N_iter)·eps = 6.7e-12 round-off argument, 1500x margin** | `verification/runs/ansys_verification/VMFL038-R2/` | **`9a6aea9b`** (freeze; prereg blob `fe28e7ec7e0e`; ancestor of HEAD; all 13 frozen files hash IDENTICAL disk = freeze = HEAD; run root ABSENT at 19:47:21Z by the lane's own `test -e`, created empty at 19:50:24Z after the freeze landed) | **`662643863390`** (`grade_vmfl038r2.py` blob; `--selftest` 45/45 rc 0 under `python3` and `python3 -O` with equal PASS/FAIL counts and the AST marker in both; 20 named controls DRIVEN to real refusals; AST no-assert guard clean, `ast.Assert` 0 / `ast.Raise` 46; SIX planted-zero records, both channels x three levels, all passed, worst readback error 3.5e-18) | **12.2333 MEASURED** (L1 0.1833 / L2 1.2500 / L3 10.8000; RANKS 1) vs EXTRAPOLATED bracket 17.0–33.8, ratio **0.720** against the lower end — came in BELOW the bracket; misprediction not waste (R2 ran at 7.03e-7 s/cell-iteration where R1 measured 9.69e-7, and the peer contention the upper bracket priced had cleared by launch); waste 0; cap 90, 13.6 % used. **The ≈60 core-min pre-freeze scratch probe is named separately and NOT absorbed (§0.1)** | **$0.010459 DERIVED** (not measured; $0.0513/core-h, REPORTED-BY-OWNER) | `verification/runs/ansys_verification/VMFL038-R2/RESULTS.md` |
```

**AND THE SENTENCE THE SUPERVISOR REQUIRED ON THE ROW'S FACE**, to be appended to the
row's verdict cell or carried as the note immediately beneath it:

> **LIMB A VERIFIES CONSERVATION, NOT ACCURACY. Its `PASS` is a floor demonstration and
> nothing more.** It establishes that the implementation conserves momentum — which it
> does by construction — and is very nearly tautological. **Limb B is where this case's
> verification content lives**, and it is the only limb of this row that could have been
> wrong in an interesting way.

---

## 8. WHAT THIS ROW DOES NOT CLAIM

- **It is not a statement about Ansys.** This box has no Ansys solver. It is a statement
  about this lab's `simpleFoam` against Bird/Stewart/Lightfoot's exact solution.
- **It does not retract R1.** Row #47 `NOT A RESULT` stands on its own evidence, and
  R1's four frozen files were verified untouched at the freeze.
- **Limb A's `PASS` is not an accuracy result.** See §7's required sentence.
- **It establishes nothing about meshes outside 1 800 – 28 800 cells**, nor about the
  aspect ratios R1 explored and R2 does not.
- **It does not decide the question `VERIFICATION_CHARTER` §2h.3 refers to Sanaa** —
  whether an exact-solution reference should be `PASS`-capable in a no-triple
  registration generally. Limb A rests on §2h.4's five express conditions and nothing
  wider (`ANSYS_VERIFICATION_CHARTER` §11.1 point 2).
- **`u_max` is a diagnostic and its registered "machine-exact at every level" wording
  MISSED at L2 and L3** (§1). No verdict rests on it, and the miss is recorded rather
  than dropped.
- **Nothing here is sent anywhere.** Submissions are parked (`CLAUDE.md` rules 7 and 8).
