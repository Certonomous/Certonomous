# R7 — the cylinder ladder's Strouhal gate at Re 1000: results

Item: `r7-strouhal-mesh-sensitivity-across-the-ladder`. Gates fixed in
`R7_STROUHAL_SPACING_PREREGISTRATION.md`, committed 14eb8f11 at 14:33 UTC;
the twin was launched at 14:34 UTC and finished at 14:46 UTC on 2026-08-01.

Primary evidence: `F5_runs/re1000_coarsespacing/record.json`, its
`log.checkMesh` and its 22 MB `log.pimpleFoam`. Baseline:
`F5_runs/re1000/record.json`, solved 2026-07-30. The force history each
Strouhal is derived from sits in each case's `postProcessing` tree, which this
repository does not track for either member; both records were computed by the
same code path over the same window, so the comparison is record to record.

---

## The answer: the low rung is robust, and it is not close

**Strouhal moved 0.12%.** The pre-registered threshold for "robust" was under
5%; for "soft" it was over 15%.

| | Re 1000, this pair | Re 3900, the existing pair |
| --- | --- | --- |
| first-cell change | **+55.29%** | **+55.29%** |
| **Strouhal** | **+0.120%** | **-35.1%** |
| Cd mean | +0.653% | 11.0% |
| lift peak-to-peak | +0.412% | 6.3% (as Cl rms) |
| base suction | +0.576% | 6.9% |
| recirculation length | -0.196% | unchanged (both null) |

The same spacing perturbation that moves Strouhal by **35.1%** at Re 3900 moves
it by **0.12%** at Re 1000 — a factor of **293**. Every other gated quantity
moves one to two orders of magnitude less at the low rung as well.

**The chaotic-regime reading survives a prediction it made rather than the
observation that motivated it.** The proposal's stated expectation was that the
low rung would be robust, and it is. The Strouhal sensitivity therefore has an
**onset** somewhere between Re 1000 and Re 3900; it is not a property of the
method, the mesh family or the Strouhal extraction, all of which are shared.
**The ladder's lower Strouhal gates stand.**

What this does not establish is where the onset sits. Re 2000 has no twin and
is untested, and nothing here says whether the transition is gradual or sharp.

## The gates, as they fell

**G1 — is it a twin? PASS.** Both members hold **22,400 cells** and both report
`Mesh OK`. The achieved first-cell ratio is **1.5529306** against the Re 3900
pair's **1.5529226**, matched to 5 parts per million. Only the near-wall
grading differs, which is exactly how the Re 3900 pair differed. Max aspect
ratio 3.056 in the baseline against 2.788 in the twin; max skewness 0.0266
against 0.0160.

The wall stayed resolved in both, which the test needs in order to mean
anything: measured y+ max **0.665** on the baseline and **1.048** on the twin,
average 0.347 and 0.558. The coarser member is still a wall-resolved mesh, so
the comparison is between two valid solves and not between a good mesh and a
broken one.

**G2 — stationarity. PASS.** `halves_drift` on Cd over t = 45 to 90 resolves on
both: **0.853%** on the baseline and **0.898%** on the twin, against the 10%
gate. Both runs are judged on the same second-half window, and the twin's
window opens at t = 45.0065 against the baseline's 45.0063.

**G3 — the Strouhal comparison. PASS, robust branch.** Period 4.267432 against
4.262324, Strouhal 0.2343330 against 0.2346138, **+0.1198%**.

**G4 — everything else.** Reported in the table above. Strouhal is not special
at this rung: it is the *least* sensitive of the five quantities measured, not
the most. At Re 3900 it was by far the most sensitive. That reversal is the
result.

## Cost, estimated against measured, and a standing rule this refutes

| | ranks | wall | core-minutes |
| --- | --- | --- | --- |
| baseline, on the record | 1 | 2418.6 s | 40.31 |
| **twin, measured** | **4** | **709.6 s** | **47.31** |
| pre-registered estimate | 4 | 513 s | 34.2 |
| docket `est_core_min` | — | — | 45.0 |

The docket's 45.0 was **good, 4.9% under**. My own pre-registered 34.2 was
**38% under**, and it missed on exactly the number I flagged as most likely to
miss: I applied the lab's measured 4.71x four-rank speedup to a case with only
5,600 cells per rank, and got **3.41x**.

That matters beyond this run, because it inverts a standing planning rule.
The lab's guidance is that four ranks ran 4.71x faster than serial **while
costing 15% fewer core-minutes**, and that running serial out of caution costs
more of both. On this case the opposite is measured:

> **Four ranks cost 17.4% MORE core-minutes than one rank here** — 47.31
> against 40.31 — while running 3.41x faster in wall time.

The rule is not wrong, it is unqualified: it was measured on a case with a much
fatter decomposition. At 5,600 cells per rank the halo exchange is no longer
cheap against the interior work, and the trade turns into what it usually is —
wall time bought with core-minutes. **A four-rank cost estimate needs its cells
per rank stated, the same way it needs its rank count stated.** On this box, at
this size, 4 ranks is still the right call when wall time matters and the wrong
one when the box is contended.

The twin's step count also differs from the baseline's, 8,276 against 8,511, a
2.8% drop. Both runs use adaptive time stepping at max Courant 1.5 and the
twin's near-wall cells are larger, so it takes slightly larger steps. Neither
run was step-limited and both reached t = 90 exactly.

## What this does not settle

Re 2000 has no twin. If the onset is to be located rather than bracketed, that
is the next rung to pair, and it costs what this one did. A proposal is filed.
