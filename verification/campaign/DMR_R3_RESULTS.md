# DMR rung R3 (h = 1/240) — results: **the solver crashed, and that is the finding**

Run 2026-09-01 against `DMR_R3_TRIPLE_PREREGISTRATION.md`, committed `68742cec`
**before** the rung was built (`res240` did not exist; `ls` returned "No such
file or directory"). Driver `verification/runs/DMR_runs/run_r3.sh`, detached
under `setsid`, rc measured **inside** the wrapper at every step.

## Verdicts

| gate | verdict | why |
| --- | --- | --- |
| **Gate V3** — kinematics vs exact theory at 1/240 | **`NOT A RESULT`** | the rung never reached t = 0.2, so no reading exists. Not a `GATE FAIL`: nothing was measured against the tolerance. |
| **Gate T** — the grid-convergence triple | **`BLOCKED`** | a triple needs three levels and only two exist. The precondition is unmet, so no classification, no observed order and no GCI is computed or quotable. |
| **The rung as a whole** | **`NOT A RESULT`** | compute ran to a crash; no number was produced. Same shape as the `C-100` precedent in `docs/COST_CALIBRATION.md`. |

**The two existing rungs are untouched and unaffected.** Gate V remains `PASS` at
1/60 and 1/120 on the 2026-08-07 record. **DMR is still a two-rung, exact-solution
result and is still shootable on that basis.**

## What happened, measured

| step | rc | wall | ranks |
| --- | --- | --- | --- |
| `blockMesh` | 0 | 2 s | 1 |
| `checkMesh` | 0 | 2 s | 1 |
| `setExprFields` | 0 | 19 s | 1 |
| `decomposePar` | 0 | 3 s | 1 |
| **`rhoCentralFoam`** | **136** | **120 s** | **4** |

`checkMesh` on the 230,400-cell grid reports **max non-orthogonality 0** and
`Mesh OK` — the mesh is not implicated.

The solver reached **t = 0.10863175** of an `endTime` of 0.2 — **54 % of the
way** — and died with **rc = 136 = 128 + 8, SIGFPE**.

## Triage — and it is not a time-step runaway

**The fault is a negative argument to `sqrt`.** The stack's deepest named frame is
`Foam::sqrt(Foam::Field<double>&, Foam::UList<double> const&)`, reached from
`rhoCentralFoam` and caught by `Foam::sigFpe::sigHandler`. In this solver `sqrt`
on a field at that point is the **speed of sound**, so the argument going
negative means a **locally negative temperature**.

**It is a trapped exception, not a silent NaN.** The log's own header records
`trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)`. The failure
is loud by construction, which is what a run should do.

**The time-step controller was behaving normally right up to the fault**, so
"it ran away" is excluded by measurement:

| last three steps | `deltaT` | max Courant |
| --- | --- | --- |
| t = 0.10854529 | 4.3225304e-05 | 0.19974985 |
| t = 0.10858852 | 4.3225304e-05 | 0.19976799 |
| t = 0.10863175 | 4.3225304e-05 | 0.19975400 |

`deltaT` is constant and max Courant sits at **0.1998 against the registered
`maxCo` 0.2** — the control is working exactly as specified.

**The last written field is completely healthy.** `t = 0.10` reconstructed and
read (0.05 core-min of diagnostic post-processing): over all 230,400 cells,
**T min = 1.000000 (exactly the pre-shock value), rho min = 1.4, p min = 1, and
ZERO negative values in any of the three.** Max p 706.87, max rho 33.88.

**So the failure is sudden and local**: from a field with no negative value
anywhere, to a negative temperature, inside about 200 time steps.

**What I could NOT determine, stated rather than guessed:** *where* the negative
temperature first appears. The fields at the failing step were never written, and
locating it would need an instrumented re-run, which is new compute this filing
does not authorise. **The candidate regions — the documented inlet-bottom corner
artifact, and the strong expansion behind the Mach stem — are hypotheses, not
findings, and are recorded as such.**

## The physical reading, offered as a hypothesis and labelled one

`rhoCentralFoam`'s Kurganov central-upwind flux with `vanLeer` reconstruction
carries **no positivity-preserving limiter**. At Mach 10 the reconstructed
left/right states in a strong expansion can produce a negative internal energy,
and the finer the grid the sharper the reconstructed gradients. **The frozen
numerics family survives at 1/60 and 1/120 and does not survive at 1/240.**
That is consistent with a robustness ceiling between those resolutions; it is
not proven by this single run.

## What is NOT being done, deliberately

**The numerics are not retuned and the rung is not re-run.** The pre-registration
names as a disqualifier *"any difference in scheme, constants, boundary
conditions, `maxCo`, write times or rank count between R3 and the two existing
rungs — the triple requires one numerics family and a difference invalidates it
rather than being corrected for."* Lowering `maxCo`, adding a limiter or
switching the flux would produce a rung that **runs** and a triple that **means
nothing**, because it would no longer be the same scheme as R1 and R2.

**A crash is a disqualifier in the frozen filing and is recorded, not softened.**
Whether to open a successor filing — a positivity-limited variant graded as its
own family, or a 1/180 rung at r = 1.5 — is a supervisor's call and is not taken
here.

## Cost — measured, against a filing that was not breached

| | core-min | basis |
| --- | --- | --- |
| pre-registered estimate | **16.0** | §6 |
| **HARD CAP** | **35.0** | §6 — **not breached**; `R3_CAP_BREACH.txt` absent |
| solve + setup, actual | **8.43** | 506 core-seconds accumulated per step with that step's own rank count, from `R3_PROGRESS.txt` |
| post-crash diagnostic | 0.05 | `reconstructPar -time 0.1`, 3 s serial |
| **total** | **8.48** | |

**The ratio 8.48 / 16.0 = 0.53 must NOT be read as estimate quality.** The
process did not complete, so there is no actual-for-the-predicted-work to
compare: 0.53 is *spend at the point of failure*, and the 16.0 priced a run that
reached t = 0.2. **Stated rather than withheld, and labelled rather than
flattered.**

**$0.0073 DERIVED, NOT MEASURED** — 8.48 core-min = 0.1413 core-h at
$0.0513/core-h, c7a.4xlarge, reported-by-owner
(`COMPUTE_BUDGET_CHARTER.md` §5: the box cannot read its own billing).

**Waste:** the 8.48 core-min bought **no graded output**. It is named here in
full rather than absorbed. Whether it is booked as waste or as the price of a
discovered robustness ceiling is the supervisor's ruling; **this record does not
book it as a result.**

## What this bought, honestly

A **negative result with a clear mechanism**: the DMR numerics family has a
resolution ceiling between 1/120 and 1/240, and the failure mode is a negative
temperature under a trapped FPE rather than a quiet degradation. **That is worth
knowing before anyone proposes a finer DMR rung**, and it is the outcome a
triple attempt exists to expose. It also settles, by measurement rather than
argument, that the two-rung pair is what this campaign honestly has.
