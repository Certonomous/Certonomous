# K0b — D403 ladder re-run. Results

**Campaign F14, rung K0b. Executed 2026-08-18 against the pre-registration
committed at `a157ccba` BEFORE the first solve**
(`K0b_D403_RERUN_PREREGISTRATION.md`). Run tree:
`verification/runs/F14-cooling-ladder/K0b_D403_rerun/`.

---

## 1. Verdicts

| Item | Verdict |
| --- | --- |
| **V1 — K0b's published mesh-sensitivity numbers reproduce** | **PASS.** Bit-for-bit, on all three legs. |
| **V2 — K0b's numbers move with mesh by a stated amount** | **PASS.** Triple monotone on every graded quantity, fine-pair GCI 0.243 % on `Nu_avg_hot`, worst 0.784 %. |
| **V3 — the committed `build_and_run.sh` reproduces the rung unaided** | **GATE FAIL.** Run alone it produced a 128x128 leg **4.490 % below** the published `Nu_avg_hot` and an observed order of **−1.25** against the published **+1.94**. |

The re-run therefore **confirmed the rung's numbers and failed the rung's
script**, and those are two different findings about the same directory.

## 2. Cost — the pre-registered estimate against the actual

The authorisation clause was *"less than $25 in your estimated computations"*,
which made the estimate the instrument. It was written into §2 of the
pre-registration and committed before the first solve.

| | core-minutes | dollars at $0.0513/core-hour |
| --- | ---: | ---: |
| **Pre-registered estimate** (§2, with contingency) | **20.0** | **$0.0171** |
| Pre-registered hard stop | 60.0 | $0.0513 |
| **Actual, wall-clock basis** | **13.974** | **$0.0119** |
| Actual, solver-CPU basis (`ExecutionTime`) | 13.627 | $0.0117 |

**The run came in 30.1 % UNDER its own estimate and consumed 0.048 % of the
$25 authorisation.** The hard stop was never approached and no re-estimate was
required.

Itemised, wall-clock seconds, single core throughout:

| Item | s |
| --- | ---: |
| 32x32 solve (blockMesh + checkMesh + solver) | 3.499 |
| **64x64 solve, fresh — the leg D403 named** | 33.469 |
| 128x128 solve to t = 4000 | 186.442 |
| 128x128 continuation to t = 16000 | 606.331 |
| Five `measure()` passes and the end-to-end analysis | 8.705 |
| **Total** | **838.446 s = 13.974 core-minutes** |

**One caveat on the instrument, recorded because it nearly mattered.** Another
lane launched eleven `buoyantBoussinesqSimpleFoam` processes in
`verification/runs/F14-cooling-ladder/K0cS_runs/` while the 128x128
continuation ran, taking the load average to 12.83. Wall clock stops being a
cost instrument on a contended box. The solver's own `ExecutionTime` is CPU
time and does not, so both bases are quoted above; on the continuation they
read 597.21 s CPU against 606.33 s wall, a 1.5 % inflation, so the contention
changed the charge by less than the rounding. Nothing was killed: the eleven
foreign processes were resolved by `readlink /proc/<pid>/exe` and separated
from this run's solver by **cwd**, which a peer cannot share — this run's was
pid 2399049 at `.../K0b_D403_rerun/K0b_m128`.

## 3. What was run, and where

The existing rung was **not** re-run in place. `build_and_run.sh` opens each
leg with `rm -rf "$dst"` and `K0b_mesh_sensitivity/` holds 41 tracked files
including both `COST.txt`, every solver log and `system/controlDict.4000`;
re-running in place would have destroyed the record this run existed to grade.

`build_and_run.sh` was copied with **exactly one edit**, the one declared in
§3 of the pre-registration: the leg list `for n in 32 128` widened to
`for n in 32 64 128`, in both loops. `diff` against the committed script showed
those two lines and nothing else. `analyse_k0b_mesh.py` was copied and `cmp`
proved byte-identical, then run unedited.

Five measurements, all through that byte-identical `measure()`:

| Tag | Case | t | cells |
| --- | --- | ---: | ---: |
| L32 | fresh 32x32 | 1386 | 1024 |
| **L64** | **fresh 64x64** | 4000 | 4096 |
| L64P | byte copy of the committed archive case | 4000 | 4096 |
| L128a | fresh 128x128, stopped at `endTime 4000` | 4000 | 16384 |
| L128b | L128a continued to t = 16000 | 16000 | 16384 |

The script's own guard passed **33 `cmp` checks** (11 files x 3 legs): every
dictionary except the one edited `blockMeshDict` line was byte-identical to the
archive case. For n = 64 the `sed` substitution is a no-op on the archive's own
`hex (0 1 3 2 4 5 7 6) (64 64 1)`, so **12 of 12** of L64's dictionaries —
`blockMeshDict` included — were byte-identical to the archive's. L64 was
therefore the committed 64x64 case rebuilt from its own tracked inputs and
nothing else. `checkMesh` reported *Mesh OK*, max non-orthogonality 0, on all
three meshes at 1024 / 4096 / 16384 cells.

## 4. The leg D403 named: the fresh 64x64 reproduced the archive bit-for-bit

This was the open half of D403 — *"K0b's published mesh-sensitivity numbers are
still unchecked against a rebuilt 64x64 leg"* — and it is settled.

**All six written time directories of the fresh solve were byte-identical to
the committed archive case**, not merely close:

| | result |
| --- | --- |
| `4000/T`, `4000/U`, `4000/p`, `4000/p_rgh`, `4000/phi`, `4000/alphat` | **6 of 6 IDENTICAL** |
| `10/T`, `20/T`, `50/T`, `100/T`, `500/T` | **5 of 5 IDENTICAL** |
| final initial residuals, all four variables | identical to every digit the log prints |

The final residuals of the fresh leg read Ux 1.479456076e-07, Uy
1.62140557e-07, T 9.593143463e-08, p_rgh 1.476541214e-07 — the same sixteen
digits the archive's own log carried from 2026-08-17. The solver build was the
same, `_481094f-20260618 OPENFOAM=2606`, and the run was serial and
deterministic.

## 5. Every deviation from the published numbers, as a number

Threshold from §4 of the pre-registration: **< 0.1 % reproduced, > 1 % NOT
REPRODUCED**, and the band between carries no verdict.

### L32, L64 and L128b — thirteen quantities each, all exact

| Leg | quantities compared | bit-for-bit exact | largest deviation |
| --- | ---: | ---: | ---: |
| L32 vs published 32x32 | 13 | **13** | **0** |
| **L64 vs published 64x64** | 13 | **13** | **0** |
| L64P vs published 64x64 | 13 | **13** | **0** |
| L128b vs published 128x128 | 13 | **13** | **0** |

The thirteen were `Nu_avg_hot`, `Nu_avg_cold`, `Nu_max_hot`, `Nu_min_hot`,
`V_star_max`, `V_star_min`, `U_star_max`, `U_star_min`, `x_over_L_at_v_max`,
`stratification_S_leastsq_mid25pct`, `energy_balance_pct`, `Pr` and `dT_K`.
Not one differed in its last printed digit. The stopping iteration of the
32x32 leg reproduced as well — `SIMPLE solution converged in 1386 iterations`,
against the published `t = 1386`, an integer that cannot be hit by accident.

**The deviation of the published numbers from the re-run is zero, on every
graded quantity, on every leg run under the published protocol.** There is no
percentage to quote because there is no difference to express as one.

### L128a — the script run alone, and here the deviations are large

| quantity | script alone (t = 4000) | published (t = 16000) | deviation |
| --- | ---: | ---: | ---: |
| `Nu_avg_hot` | 4.3254648850 | 4.5288167412 | **−4.490 %** |
| `Nu_avg_cold` | 4.3257406232 | 4.5288233281 | −4.484 % |
| `Nu_max_hot` | 7.3064967715 | 7.7572684541 | **−5.811 %** |
| `Nu_min_hot` | 0.8079556038 | 0.7276237665 | **+11.040 %** |
| `V_star_max` | 66.3550134651 | 68.6112455926 | −3.288 % |
| `V_star_min` | −66.3596502921 | −68.6112857924 | +3.282 % |
| `U_star_max` | 33.6597990183 | 34.7968015796 | −3.268 % |
| `U_star_min` | −33.6614658262 | −34.7968493880 | +3.263 % |
| `stratification_S_leastsq_mid25pct` | 0.9161418789 | 1.0374274577 | **−11.691 %** |
| `x_over_L_at_v_max` | 0.06640625 | 0.06640625 | exact |

Ten of thirteen quantities moved; three (`x_over_L_at_v_max`, `Pr`, `dT_K`)
did not. Every one of the six **graded** quantities landed beyond the 1 %
NOT REPRODUCED threshold.

## 6. The ladder

### Under the published protocol — reproduced exactly, including the ladder statistics

| quantity | 32x32 | 64x64 | 128x128 | 64→128 % | p | GCI % | published p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `Nu_avg_hot` | 4.6497 | 4.5538 | 4.5288 | 0.552 | **1.94** | **0.243** | 1.94 |
| `Nu_max_hot` | 8.2613 | 7.8726 | 7.7573 | 1.487 | 1.75 | 0.784 | 1.75 |
| `Nu_min_hot` | 0.7172 | 0.7257 | 0.7276 | 0.269 | 2.12 | 0.100 | 2.12 |
| `V_star_max` | 66.4840 | 68.3723 | 68.6112 | 0.348 | 2.98 | 0.063 | 2.98 |
| `U_star_max` | 35.3073 | 34.8814 | 34.7968 | 0.243 | 2.33 | 0.075 | 2.33 |
| `stratification_S_leastsq_mid25pct` | 1.0551 | 1.0413 | 1.0374 | 0.372 | 1.84 | 0.180 | 1.84 |

Monotone on all six. Richardson extrapolate on `Nu_avg_hot` 4.520015145256470,
against the published 4.52001514525647 — the same digits.

**So the answer to proposal P2 stands unchanged: K0b's published `Nu_avg` moves
by 0.552 % between 64x64 and 128x128, with a fine-pair GCI of 0.243 %.** The
largest movement of any graded quantity across that refinement was
`Nu_max_hot` at 1.487 %, GCI 0.784 %.

### Under the script alone — the same ladder, and it does not converge

| quantity | 32x32 | 64x64 | 128x128 | 64→128 % | p |
| --- | ---: | ---: | ---: | ---: | ---: |
| `Nu_avg_hot` | 4.6497 | 4.5538 | 4.3255 | 5.279 | **−1.25** |
| `Nu_max_hot` | 8.2613 | 7.8726 | 7.3065 | 7.748 | −0.54 |
| `Nu_min_hot` | 0.7172 | 0.7257 | 0.8080 | 10.185 | −3.28 |
| `V_star_max` | 66.4840 | 68.3723 | 66.3550 | 3.040 | **non-monotone** |
| `U_star_max` | 35.3073 | 34.8814 | 33.6598 | 3.629 | −1.52 |
| `stratification_S_leastsq_mid25pct` | 1.0551 | 1.0413 | 0.9161 | 13.660 | −3.17 |

Five of six observed orders negative and the sixth non-monotone, so
`analyse_k0b_mesh.richardson` correctly refused to extrapolate through it. A
reader who ran the committed script and read this table would conclude the case
**diverges under refinement**. It does not; the leg was unconverged.

## 7. The end-to-end reproduction: 11 differing leaves, none of them physics

The committed `analyse_k0b_mesh.py` was then run **unmodified**, exit 0, and
its `k0b_mesh_sensitivity.json` compared leaf-by-leaf against the published
one. **11 leaves differed out of the 674 the published document carries**, and every
one of the 11 fell into two classes:

| class | leaves | what they were |
| --- | ---: | --- |
| wall clock and derived cost | 8 | timings of this machine on this day |
| `case` path strings | 3 | the pre-move spellings the published record was written with |

Zero physics leaves differed — not one of the 406-entry, 138-entry and 6-entry
`Nu_history_by_time` series, nor any Nusselt, velocity, stratification,
observed order, GCI or extrapolate.

The three path leaves are D403 itself, visible in the artifact:

```
/legs/64x64/case
    re-run   : 'verification/runs/THERMAL_K0_runs/K0b_cavity_Ra1e5'
    published: 'demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5'
```

The published record named the directory R20 moved; the re-run resolved it
through `lab_paths.run_archive` and found the successor. That is the repair of
`726f477e` working on live data rather than on a resolution probe.

**The committed archive case was not written to.** All 89 of its files were
md5-summed before the end-to-end run and after: **88 unchanged**, and the one
that changed was `log.cellCentres`, an untracked OpenFOAM log the analysis
regenerates by design. `git status` on
`verification/runs/THERMAL_K0_runs/` returned empty afterwards.

## 8. V3, at full volume: the committed script does not reproduce its own rung

`build_and_run.sh` runs every leg to the source case's `endTime 4000` and
**contains no continuation step**. The published 128x128 leg was continued by
hand to 16000 iterations. The rung's README describes that continuation in
prose and `K0b_m128/system/controlDict.4000` is the surviving fingerprint of
the hand edit — but nothing executable performs it, and the copy step at
`build_and_run.sh:69` overwrites `system/controlDict` from the source case on
every invocation, so the hand edit cannot even survive a re-run of the script
that is supposed to have produced it.

Whoever ran `build_and_run.sh` and then `analyse_k0b_mesh.py` — the two
commands the README documents, in the order it documents them — got the §6
lower table: **`Nu_avg_hot` 4.3255, observed order −1.25, GCI negative, and one
quantity non-monotone.** Not the published result.

This was **predicted in §4 of the pre-registration as P-D, before the first
solve**, from reading the script rather than from running it, and the predicted
value was *"≈ 4.3255, i.e. ≈ 4.5 % below"*. The measured value was 4.3254648850
and the measured deviation 4.490 %.

The continuation was reproduced here by applying exactly the recorded edit —
`startFrom latestTime`, `endTime 16000`, `writeInterval 2000` — and both the
pre-continuation and post-continuation `controlDict` were `cmp`-proved
**byte-identical to the published ones** before the solver was launched. With
that manual step the published numbers came back exactly. **The rung's numbers
were never in doubt; its executability without an undocumented human step
was.** Filed as **D406**.

## 9. The convergence criterion

Fixed in §5 of the pre-registration: a leg counted as CONVERGED only if all
four solved variables met the case's own `residualControl` — `p_rgh 1e-07`,
`U 1e-08`, `T 1e-08` — or the run terminated because `residualControl` fired.

| leg | terminated by | Ux | Uy | T | p_rgh | verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 32x32 | **`residualControl`, at 1386** | 9.67e-09 | 7.44e-09 | 8.15e-09 | 1.21e-08 | **CONVERGED** |
| 64x64 | `endTime 4000` | 1.48e-07 | 1.62e-07 | 9.59e-08 | 1.48e-07 | stopped at `endTime` |
| 128x128 at 4000 | `endTime 4000` | 8.71e-05 | 9.39e-05 | 5.28e-05 | 6.71e-05 | stopped at `endTime` |
| 128x128 at 16000 | `endTime 16000` | 2.36e-08 | 2.77e-08 | 2.51e-08 | 3.44e-08 | stopped at `endTime` |

**Only the 32x32 leg met its own case's `residualControl`.** The 64x64 leg
stood **16x above** the U target and **9.6x above** the T target; the 128x128
leg at 16000 stood **2.8x** and **2.5x** above them. Both were nonetheless well
inside the mesh-sensitivity signal they were used to measure — the 64→128
change is 0.552 % while the 64x64 leg's last 3500 iterations moved `Nu_avg` by
14.35 % — so this does not disturb §6, and it is recorded rather than gated.

What it does disturb is one sentence of the rung's own reporting.
`analyse_k0b_mesh.py:264-265` gives the 64x64 leg's convergence evidence as
*"the final initial residual of 9.6e-08 in its own log"*. That is the **T**
residual alone, the **smallest of the four**, quoted against no target; T's own
target in the same case is 1e-08. This observation was registered in §5 of the
pre-registration **from a reading of the committed log before the re-run
started**, precisely so it could not be presented afterwards as something the
re-run discovered. Filed as **D407**.

## 10. Reported, never gated on

`energy_balance_pct` — the hot-wall against cold-wall Nusselt closure — is an
**identity on this case**: the cavity is sealed, both vertical walls are
fixed-temperature Dirichlet and the horizontals adiabatic, so any converged
discrete field satisfies it to solver tolerance whether or not the physics is
right (`VERIFICATION_CHARTER.md:106-111`). Its values reproduced exactly
(3.542e-05, 3.094e-04, 1.454e-04 on the three legs) and **no verdict rests on
them**. The same applies to the internal assertion at
`analyse_k0b_mesh.py:270`, which checks one estimator of the hot-wall Nusselt
number against another estimator of the same cells.

Worth stating plainly, because a re-run that reports "everything matched" is
exactly the shape an identity produces: the L64P leg — the byte copy of the
archive, re-measured — **is** close to an identity and was declared as one in
§4 before it ran. It tested provenance only. **The load-bearing result is
L64, a fresh solve from the tracked dictionaries, which is not an identity: a
wrong mesh, a wrong scheme, a changed dictionary or a different solver build
would each have broken it, and none did.**

## 11. What is not claimed

**Not a validation.** K0b was a capability rung graded against no published
datum, and this re-run did not change that. It says K0b's numbers are
reproducible and states how far they move with mesh. It says nothing about
whether they are right. The de Vahl Davis comparison lives in K0c next door
and its reference values were not applied here: these cases kept K0b's
`Pr = 0.706814` and its `limitedLinear`/`linearUpwind` schemes deliberately.

The observed orders in §6 are diagnostics, not certificates. They are
meaningful only if all three meshes lie in the asymptotic range, and with
r = 2 across a factor of sixteen in cell count that remains an assumption this
rung states rather than proves — as the module's own docstring already said.

## 12. Artifacts

| Path | What |
| --- | --- |
| `docs/campaigns/F14-cooling-ladder/K0b_D403_RERUN_PREREGISTRATION.md` | committed at `a157ccba`, before the first solve |
| `verification/runs/F14-cooling-ladder/K0b_D403_rerun/build_and_run.sh` | the committed script, one declared edit |
| `verification/runs/F14-cooling-ladder/K0b_D403_rerun/analyse_k0b_mesh.py` | byte-identical copy, run unmodified |
| `.../measure_leg.py`, `.../grade_d403.py` | the wrappers; they add no arithmetic |
| `.../measured_L32.json` … `.../measured_L128b_endTime16000.json` | the five leg measurements |
| `.../k0b_d403_regrade.json`, `.../grade_d403.txt` | every deviation as a number |
| `.../k0b_mesh_sensitivity.json` | the end-to-end reproduction of §7 |
| `.../K0b_m32/`, `.../K0b_m64/`, `.../K0b_m128/` | the three legs, with logs and `COST.txt` |
| `.../DONE.build_and_run`, `.../K0b_m128/DONE.continue`, `.../DONE.analyse` | completion markers; each carries its exit code |

Time directories are ignored by `K0b_D403_rerun/.gitignore` — a
directory-local file, because the repository `.gitignore` was shared and
carried another lane's uncommitted work while this ran. The provenance copy
`K0b_m64_published/` is ignored for the reason the sibling rung states: there
is one copy of the archive case in the repository and it is the committed one.

## 13. D403

**Closed.** The re-run named in D403's own *"to settle"* was executed, the
64x64 leg was rebuilt and reproduced the archive bit-for-bit, and the published
numbers were graded. Two findings that surfaced in doing it — the script's
missing continuation and the single-residual convergence claim — left this rung
as **D406** and **D407** rather than being absorbed into it.
