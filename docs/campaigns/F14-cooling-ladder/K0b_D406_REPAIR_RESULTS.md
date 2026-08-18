# K0b — D406 script repair. Results

**Campaign F14, rung K0b. Executed 2026-08-18 against the pre-registration
committed at `211d401e` BEFORE the first solve**
(`K0b_D406_REPAIR_PREREGISTRATION.md`). Run tree:
`verification/runs/F14-cooling-ladder/K0b_D406_repair/`.

---

## 1. Verdicts

| Item | Verdict |
| --- | --- |
| **W1 — the repaired script reproduces the published rung unaided** | **PASS.** The two documented commands, unmodified, from a clean start: **39 of 39 graded quantities bit-identical** across three legs. Largest deviation **0**. |
| **W2 — the repair does not disturb the converged leg** | **PASS.** The 32x32 leg stopped itself at t = 1386, was **not** continued, and gained no `controlDict.4000`. |
| **W3 — the ladder statement survives the repair** | **PASS.** Triple monotone on all six graded quantities; **48 of 48 Richardson leaves bit-identical**. |
| **W4 — the committed archive case is untouched** | **PASS.** 88 of 89 files md5-identical, the 89th an untracked OpenFOAM log the analysis regenerates by design; `git status` on that tree returned **0 lines**. |

**D406 closes.** Its own *"to settle"* was *"encode the continuation in
`build_and_run.sh` … so that the script alone reproduces the published leg, and
re-run the rung once against the amended script to prove it."* Both halves were
done and the second is W1.

## 2. What was changed

Two tracked files, exactly the two declared in §3 of the pre-registration, and
no others.

### `build_and_run.sh`

| Change | What it removed |
| --- | --- |
| An explicit second stage, entered only by a leg that did **not** stop itself on `residualControl` | the missing continuation |
| The stopping reason READ from the solver's own `SIMPLE solution converged in N iterations` line | an inference from time directories or from a single residual, which is D407's shape |
| The stage-2 `controlDict` DERIVED from the source case's own dictionary on every invocation — `startFrom latestTime`, `endTime 16000`, `writeInterval 2000` | the dependency on a hand edit, and with it the clobber: there was nothing left for the copy step to destroy |
| `system/controlDict.4000` written **by the script**, immediately before the rewrite, and `cmp`-proved against the source case's dictionary at that moment | a fingerprint of a human action, promoted to an output of the script |
| A guard that the two dictionaries with the three key lines removed are identical, and that each of the three new lines stands in its declared form | a continuation dictionary that had also picked up a scheme or a `residualControl` target |
| Per-PID `wait` with each status checked | a bare `wait`, which returns 0 however its jobs ended — the same class of silence D406 is about |

`analyse_k0b_mesh.py` was **not edited**. Its worktree blob
`3876b8a4c039b33f7677b3aaee97ebc6da12f098` is HEAD's blob for that path, and the
copy that ran in the run tree carries the same hash.

### `README.md`

The continuation was rewritten from a historical note about a hand edit into a
description of a step the script performs, and the two commands were given
their own section. Two stale paths were corrected and were **named in the
pre-registration before they were touched**:
`demo-output/website/campaign/THERMAL_K0_RESULTS.md` and
`demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5`, neither of
which has existed since R20/R21. That is D403's defect in the instruction
document rather than in the code.

**No published result document was edited.** `k0b_mesh_sensitivity.json` and
`K0b_D403_RERUN_RESULTS.md` record runs that happened and were not touched.

## 3. Cost — the pre-registered estimate against the actual

| | core-minutes | dollars at $0.0513/core-hour |
| --- | ---: | ---: |
| **Pre-registered estimate** (§2, with contingency) | **17.0** | **$0.0145** |
| Pre-registered hard stop | 45.0 | $0.0385 |
| **Actual, wall-clock basis** | **12.701** | **$0.0109** |
| Actual, solver-CPU basis (`ExecutionTime`) | 12.663 | $0.0108 |

**The run came in 25.3 % UNDER its own estimate and consumed 0.043 % of the $25
authorisation.** The hard stop was never approached and no re-estimate was
required.

Itemised, single core throughout:

| Item | wall s | solver CPU s |
| --- | ---: | ---: |
| 32x32 solve (`foamListTimes` + `blockMesh` + `checkMesh` + solver) | 3.531 | 2.67 |
| 128x128 solve to t = 4000 | 190.325 | 189.19 |
| **128x128 continuation to t = 16000, performed by the script** | **564.768** | **564.49** |
| `analyse_k0b_mesh.py`, end to end over three legs | 3.434 | — |
| **Total** | **762.058 s = 12.701 core-minutes** | **759.78 s = 12.663 core-minutes** |

**Both bases are quoted because other lanes were on the box.** Two foreign
`buoyantBoussinesqSimpleFoam` processes ran at 99.5 % CPU throughout, pids
2396479 and 2396481, resolved by `readlink /proc/<pid>/exe` and separated from
this run's solver by **cwd** — `verification/runs/F14-cooling-ladder/K0cS_runs/S_LS_f`
and `.../S_KE_f`, against this run's pid 2517713 at
`.../K0b_D406_repair/K0b_m128`. Nothing was killed. Across the three solves
wall stood **0.30 %** above solver CPU (758.624 s against 756.35 s), against the
1.5 % the D403 lane measured under a load average of 12.83; this box carried a
load average near 3.1 and sixteen cores, so the contention changed the charge by
less than the rounding.

The rung's own `analyse_k0b_mesh.py` reported `new legs cost 12.644
core-minutes against 15 authorised` for the two legs it charges. This document's
12.701 is the same figure plus the analysis pass, which the rung does not
charge itself for.

## 4. How the proof was run, and why not in place

The rung was **not** re-run in place. `K0b_m32/` and `K0b_m128/` hold **36
tracked files** — both `COST.txt`, every solver log, `system/controlDict.4000` —
and `build_and_run.sh` opens each leg with `rm -rf "$dst"`. Running the
documented command in the rung directory would have destroyed the published
record this run existed to grade. See §8.

`build_and_run.sh` and `analyse_k0b_mesh.py` were copied into
`verification/runs/F14-cooling-ladder/K0b_D406_repair/` and run there **with no
edit of any kind**. Byte-identity was proved twice over, by `cmp` (exit 0) and
by hash:

| file | rung copy | run-tree copy |
| --- | --- | --- |
| `build_and_run.sh` | `8f98d8ab96efc66853593647a2c45f97e2b7ea50` | `8f98d8ab96efc66853593647a2c45f97e2b7ea50` |
| `analyse_k0b_mesh.py` | `3876b8a4c039b33f7677b3aaee97ebc6da12f098` | `3876b8a4c039b33f7677b3aaee97ebc6da12f098` |

The only thing that differed was `$HERE`, which decides where the two new legs
are built and nothing else; the 64x64 leg is resolved by name through
`lab_paths.run_archive` in both trees, which is why both work from anywhere
under the repository.

The two commands, in the order the README gives them, both exit 0 and both
carry a completion marker holding their exit code —
`DONE.build_and_run` (`exit_code 0`, 755.194 s) and `DONE.analyse`
(`exit_code 0`, 3.434 s). The script's own stdout was:

```
K0b_m32  wall 3.53 s
K0b_m32  stopped itself on residualControl; NOT continued
K0b_m128  wall 190.32 s
K0b_m128  continued to t = 16000, wall 564.77 s
```

Those four lines are the whole of D406 answered: the coarse leg was left where
it stopped, and the fine leg was continued **by the script**.

## 5. Every deviation from the published numbers, as a number

Threshold from §5 of the pre-registration: **< 0.1 % reproduced, > 1 % NOT
REPRODUCED**, and the band between carries no verdict.

| leg | quantities compared | bit-for-bit exact | largest deviation |
| --- | ---: | ---: | ---: |
| 32x32 (built by the script) | 13 | **13** | **0** |
| 64x64 (read in place from the committed archive) | 13 | **13** | **0** |
| **128x128 (built AND CONTINUED by the script)** | 13 | **13** | **0** |

The thirteen were `Nu_avg_hot`, `Nu_avg_cold`, `Nu_max_hot`, `Nu_min_hot`,
`V_star_max`, `V_star_min`, `U_star_max`, `U_star_min`, `x_over_L_at_v_max`,
`stratification_S_leastsq_mid25pct`, `energy_balance_pct`, `Pr` and `dT_K`.
Not one differed in its last printed digit. **There is no percentage to quote
because there is no difference to express as one.**

The published headline, at full precision, for the leg that carries the whole
finding:

| | re-run | published | deviation |
| --- | ---: | ---: | ---: |
| `Nu_avg_hot`, 128x128 | 4.528816741169209 | 4.528816741169209 | **0** |
| against what the UNREPAIRED script produced | 4.3254648850 | — | −4.490 % |

Three further reproductions that are integers or counts, and therefore cannot
be hit by accident:

| | re-run | published |
| --- | ---: | ---: |
| stopping time of the 32x32 leg | **1386** | 1386 |
| analysed time of the 128x128 leg | **16000** | 16000 |
| written times per leg (32 / 64 / 128) | **139 / 6 / 406** | 139 / 6 / 406 |
| `Nu_history_by_time` values bit-identical | **551 of 551** | — |

The 406 is the sharper of these: 400 writes at `writeInterval 10` to t = 4000
plus **six** at `writeInterval 2000` from the continuation. A run that had not
been continued would carry 400, and one continued with the wrong write interval
would not carry six.

## 6. The ladder

| quantity | 32x32 | 64x64 | 128x128 | 64→128 % | p | GCI % | leaves differing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `Nu_avg_hot` | 4.6497 | 4.5538 | 4.5288 | 0.552 | **1.94** | **0.243** | 0 of 8 |
| `Nu_max_hot` | 8.2613 | 7.8726 | 7.7573 | 1.487 | 1.75 | 0.784 | 0 of 8 |
| `Nu_min_hot` | 0.7172 | 0.7257 | 0.7276 | 0.269 | 2.12 | 0.100 | 0 of 8 |
| `V_star_max` | 66.4840 | 68.3723 | 68.6112 | 0.348 | 2.98 | 0.063 | 0 of 8 |
| `U_star_max` | 35.3073 | 34.8814 | 34.7968 | 0.243 | 2.33 | 0.075 | 0 of 8 |
| `stratification_S_leastsq_mid25pct` | 1.0551 | 1.0413 | 1.0374 | 0.372 | 1.84 | 0.180 | 0 of 8 |

Monotone on all six. `Nu_avg_hot` observed order **1.9404946505323346**,
extrapolate **4.52001514525647**, fine-pair GCI **0.24293309974126642 %**,
64→128 change **0.5516276643840857 %** — every digit the published document
carries.

**So P2's answer stands unchanged, and now stands on a script that produces it:
K0b's published `Nu_avg` moves by 0.552 % between 64x64 and 128x128, with a
fine-pair GCI of 0.243 %.**

## 7. The artifacts the second stage left, checked independently of the physics

Twenty checks, exit codes captured directly and never through a pipe
(`check_artifacts.sh`, `check_artifacts.txt`, overall exit 0).

| Prediction | Check | Result |
| --- | --- | --- |
| P-D.1 | `K0b_m128/log.buoyantBoussinesqSimpleFoam.continue` exists, opens at `Create mesh for time = 4000`, reaches `Time = 16000` | 3 of 3 exit 0 |
| P-D.2 | `COST.txt` carries `continue_wall_clock_s` **and still carries** the stage-1 `wall_clock_s` — appended, not rewritten | 2 of 2 exit 0 |
| P-D.3 | `controlDict.4000` byte-identical to the **published** one, and to the **archive case's own** `system/controlDict` | 2 of 2 exit 0 |
| P-D.4 | the final `controlDict` byte-identical to the published one | exit 0 |
| **P-B** | the 32x32 leg has **no** `controlDict.4000`, **no** continuation log, **no** `continue_wall_clock_s`, its `controlDict` is still the archive's own, and its log carries `SIMPLE solution converged in 1386 iterations` | 5 of 5 as predicted |
| — | all seven remaining dictionaries of both legs against the published ones | 7 of 7 exit 0 |

**P-D.3 is the one worth reading twice.** The continuation dictionary this
script derived is byte-identical to the one a human wrote in 2026-08-17, and
the stage-1 dictionary it preserved is byte-identical both to the published
fingerprint and to the archive case's own file. The script reproduces the hand
edit exactly, and no longer needs it to have survived.

That derivation was **also proved before the first solve**, as §5 P-D of the
pre-registration records: the three-key rewrite applied offline to the archive
case's `system/controlDict` produced a file `cmp`-identical to the published
`K0b_m128/system/controlDict`, exit 0. The pre-solve check established that the
derivation was right; this run established that the script performs it.

## 8. The end-to-end reproduction: 11 differing leaves of 674, none of them physics

The committed `analyse_k0b_mesh.py` was run **unmodified**, exit 0, and its
`k0b_mesh_sensitivity.json` compared leaf by leaf against the published one.
**674 leaves in each. 11 differed**, and every one fell into two classes:

| class | leaves | what they were |
| --- | ---: | --- |
| wall clock and derived cost | 8 | timings of this machine on this day |
| `case` path strings | 3 | where each leg was read from |

**Zero physics leaves differed** — not one entry of the 139-, 6- and 406-entry
`Nu_history_by_time` series, nor any Nusselt, velocity, stratification, observed
order, GCI or extrapolate. That is the same count and the same two classes the
D403 re-run reported, on a different run tree.

Two of the three path leaves are this run tree rather than the rung's, which is
expected and is the price of not running in place. The third is D403's own
defect still visible in the published artifact:

```
/legs/64x64/case
    re-run   : 'verification/runs/THERMAL_K0_runs/K0b_cavity_Ra1e5'
    published: 'demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5'
```

**The committed archive case was not written to.** All 89 of its files were
md5-summed before the run and after: **88 unchanged**, and the one that changed
was `log.cellCentres`, an untracked OpenFOAM log the analysis regenerates by
design — the same single exception the D403 lane reported. `git status` on
`verification/runs/THERMAL_K0_runs/` returned **0 lines** afterwards.

## 9. D407 — the picture did not move, and this is the number that says so

Registered as P-F in §6 of the pre-registration, before the solve, so that it
could not be claimed either way afterwards without a measurement. All four
final initial residuals of every leg, beside the case's own `residualControl`
targets, with the stopping reason read from the solver's own statement
(`residuals.py`, `residuals.txt`):

| leg | stopped by | at | Ux | Uy | T | p_rgh | verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 32x32 | **`residualControl`** | 1386 | 9.67e-09 | 7.44e-09 | 8.15e-09 | 1.21e-08 | **CONVERGED, 4 of 4 targets met** |
| 128x128 stage 1 | `endTime` | 4000 | 8.71e-05 | 9.39e-05 | 5.28e-05 | 6.71e-05 | 0 of 4 met; 8714x above the U target |
| 128x128 continued | `endTime` | 16000 | 2.36e-08 | 2.77e-08 | 2.51e-08 | 3.44e-08 | 1 of 4 met (`p_rgh`); U 2.4x and 2.8x above, T 2.5x above |
| 64x64 (archive) | `endTime` | 4000 | 1.48e-07 | 1.62e-07 | 9.59e-08 | 1.48e-07 | 0 of 4 met; U 14.8x and 16.2x above, T 9.6x above |

**Across the whole ladder exactly one leg met its own case's `residualControl` —
the 32x32 — which is precisely what D407 says. This repair did not change it,
and was not expected to.** The continuation carries the fine leg from 8714x
above the U target to 2.4x above it, which is a large improvement and is still
not the target.

**D407 stays OPEN.** Its defect is one sentence of
`analyse_k0b_mesh.py:264-265`, this task did not edit that file, and its repair
— report all four residuals beside their targets and state the stopping reason
— would have been unverifiable inside the commit that also grades this one.

**One correction to D407's own arithmetic, offered because this run had to read
the same log.** That row quotes the 64x64 leg's Ux as **1.510e-07** and Uy as
**1.657e-07**. Those are the values at t = 3998, two iterations before the end.
The **final** initial residuals, at t = 4000, are Ux **1.479456076e-07** and Uy
**1.62140557e-07**, which is what `K0b_D403_RERUN_RESULTS.md` §4 records. The
finding is untouched — 14.8x above the U target rather than 15.1x — and the row
is not edited, per W-4.

## 10. Reported, never gated on

`energy_balance_pct` is an **identity on this case**: the cavity is sealed, both
vertical walls are fixed-temperature Dirichlet and the horizontals adiabatic, so
any converged discrete field satisfies it to solver tolerance whether or not the
physics is right (`VERIFICATION_CHARTER.md:106-111`). Its values reproduced
exactly (3.542e-05, 3.094e-04, 1.454e-04) and **no verdict rests on them**. The
same applies to the internal assertion at `analyse_k0b_mesh.py:270`, which
checks one estimator of the hot-wall Nusselt number against another estimator of
the same cells.

**The load-bearing result is not an identity.** The 128x128 leg was meshed,
solved from `0.orig` and continued by the script from the archive's own
dictionaries; a wrong mesh, a wrong scheme, a changed dictionary, a continuation
that did not fire, a continuation that fired to the wrong `endTime`, or a
continuation that wrote at the wrong interval would each have broken the match,
and none did. The 64x64 leg **is** close to a re-read of the same bytes and is
declared as such: it is provenance, not evidence about the flow.

## 11. What is left open, and one row is new

**D407 — OPEN.** §9 above; unchanged by this repair, deliberately not folded in.

**D410 — FILED, and it is a defect of the same instrument this task repaired.**
`build_and_run.sh` opens each leg with `rm -rf "$dst"`. Run in the rung
directory — which is where its README documents it and where a reader would
naturally run it — it deletes **36 tracked files**: both `COST.txt`, every
solver log, `system/controlDict.4000`, and every dictionary of both legs. That
is the published record of the rung, and the D403 re-run declined to re-run in
place for exactly this reason. **This repair's answer to it is currently a
paragraph in the README**, which is the same prose-not-executable shape D406
named, one hazard along. It was **excluded because it was not in the change set
declared in §3 of the pre-registration**, and adding an undeclared behaviour
change after the fact would spend the instrument this task exists to honour: a
guard that makes the documented command refuse is a workflow decision, and this
run could not have proved one anyway.

## 12. Artifacts

| Path | What |
| --- | --- |
| `docs/campaigns/F14-cooling-ladder/K0b_D406_REPAIR_PREREGISTRATION.md` | committed at `211d401e`, before the first solve |
| `verification/runs/F14-cooling-ladder/K0b_D406_repair/build_and_run.sh` | the repaired script, byte-identical to the committed one |
| `.../analyse_k0b_mesh.py` | byte-identical to HEAD's blob, run unmodified |
| `.../k0b_mesh_sensitivity.json` | the end-to-end reproduction of §8 |
| `.../grade_d406.py`, `.../grade_d406.txt`, `.../k0b_d406_regrade.json` | every deviation as a number |
| `.../check_artifacts.sh`, `.../check_artifacts.txt` | the twenty artifact checks of §7 |
| `.../residuals.py`, `.../residuals.txt` | the four-residual table of §9 |
| `.../K0b_m32/`, `.../K0b_m128/` | the two legs, with logs and `COST.txt` |
| `.../DONE.build_and_run`, `.../DONE.analyse` | completion markers; each carries its exit code |

Time directories and `constant/polyMesh` are ignored by
`K0b_D406_repair/.gitignore`, a directory-local file for the reason the D403
re-run tree states: the repository `.gitignore` is shared and carried 357
foreign staged paths while this ran, and a write-back to a shared file is a
merge.

## 13. What this is not

**Not a validation.** K0b is a capability rung graded against no published
datum and nothing here changes that. The de Vahl Davis reference values live in
K0c next door and were not applied: these cases keep K0b's `Pr = 0.706814` and
its `limitedLinear`/`linearUpwind` schemes deliberately.

**Not a re-measurement of the physics.** The D403 re-run established that the
published numbers reproduce bit-for-bit under the published protocol, and this
run reproduced them again. What was under test was whether the committed script
performs that protocol without a human in the middle of it.

**The observed orders in §6 are diagnostics, not certificates.** They are
meaningful only if all three meshes lie in the asymptotic range, and with r = 2
across a factor of sixteen in cell count that remains an assumption this rung
states rather than proves.

## 14. D406

**CLOSED.** The continuation is encoded in `build_and_run.sh`, the dependency on
a hand-edited `controlDict` is gone, and the two commands the README documents
reproduce the published table from a clean start with **zero deviation on 39 of
39 graded quantities, 551 of 551 history values and 48 of 48 ladder leaves**.
