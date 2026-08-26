# K0b — D403 ladder re-run. Pre-registration

**Campaign F14, rung K0b, mesh-sensitivity re-run closing the open half of
D403. Written 2026-08-18 BEFORE any solver was launched for it.** Every
threshold, every prediction, every outcome-to-meaning mapping and the cost
estimate below were fixed here and committed before the first solve.

---

## 1. Why this existed

`docs/DOCKET.md` D403 recorded that the K0b mesh-sensitivity rung had been
unrunnable since MOVE_MAP batch 7: `build_and_run.sh` and `analyse_k0b_mesh.py`
had both named
`demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5`, which R20 had
moved to `verification/runs/THERMAL_K0_runs`. The shell guard
`[ -d "$SRC/0.orig" ]` had been FALSE and the script had exited 2 on every
invocation.

Commit `726f477e` repaired both sites: the repository root was FOUND by walking
up for the `scripts/lab_paths.py` sentinel rather than counted in `..`
segments, and the archive was resolved through `lab_paths.run_archive`. D403
was then marked **CLOSED IN PART**, and the agent that landed the repair named
the open half in its own words:

> *"D403 remains OPEN on the re-run. The ladder has not been re-run; K0b's
> published mesh-sensitivity numbers are still unchecked against a rebuilt
> 64x64 leg. That is compute nobody here was authorised to spend."*

Sanaa granted standing authority on 2026-08-18 for any run under $25 by the
running agent's own estimate. That estimate is the instrument, so it was
written down here before the first solve rather than after.

## 2. The cost estimate — written before the run, and it is the instrument

Measured rate, verified against the AWS public pricing feed on 2026-08-18:
**$0.0513 per core-hour** (c7a.4xlarge on-demand, us-east-2, $0.82112/hr across
16 vCPU). $25 therefore bought ~487 core-hours.

The estimate was built from this rung's own recorded measurements rather than
from a guess. `K0b_m32/COST.txt` recorded 3.623 s and `K0b_m128/COST.txt`
recorded 189.550 s to `endTime 4000` plus 575.880 s of continuation to 16000.
The 64x64 leg was never separately timed as a leg of this rung; the archive
case's own solver log recorded `ExecutionTime = 31.77 s` at t = 4000.

| Item | Basis | Estimate (core-seconds) |
| --- | --- | --- |
| 32x32 solve | `K0b_m32/COST.txt` 3.623 s | 4 |
| 64x64 solve, fresh | archive log ExecutionTime 31.77 s + mesh/IO overhead | 50 |
| 128x128 solve to t = 4000 | `K0b_m128/COST.txt` 189.550 s | 190 |
| 128x128 continuation to t = 16000 | `K0b_m128/COST.txt` 575.880 s | 576 |
| Re-measurement of the archive 64x64 copy | blockMesh + postProcess | 20 |
| Analysis passes (blockMesh, writeCellCentres, field parse, 5 cases) | observed class | 60 |
| **Total** | | **900 core-seconds = 15.0 core-minutes** |

**Pre-registered estimate: 20 core-minutes with contingency, i.e.
20/60 x $0.0513 = $0.0171 — call it $0.02.** That is 0.07 % of the $25
authorisation.

**Hard stop, fixed here: 60 core-minutes, i.e. $0.052.** If the run exceeded
that, it was to be stopped and re-estimated rather than pressed on. This
campaign carries a VOID cost estimate on record — K2b priced steady runs for an
unsteady question — and the remedy adopted there was to stop, not to absorb.

## 3. What was to be run, and where it was to be written

A **distinct output path** was fixed in advance:
`verification/runs/F14-cooling-ladder/K0b_D403_rerun/`. The existing rung tree
`K0b_mesh_sensitivity/` was NOT to be re-run in place, for a reason that is
not fastidiousness: `build_and_run.sh` opens each leg with `rm -rf "$dst"`, and
`K0b_m32/` and `K0b_m128/` hold **41 tracked files** including both `COST.txt`,
every solver log, and `system/controlDict.4000`. Re-running in place would have
destroyed the published record this run exists to grade. Two baselines have
already been lost in this lab to runs clobbering one output path.

Five measurements were fixed:

| Tag | Case | What it tests |
| --- | --- | --- |
| **L32** | fresh 32x32 solve from the archive dictionaries | reproduction of the published coarse leg |
| **L64** | **fresh 64x64 solve** from the archive dictionaries | the leg D403 names — never assembled since the move |
| **L64P** | byte copy of the committed archive case, re-measured | provenance: did the published JSON come from these fields through this code path |
| **L128a** | fresh 128x128 solve stopped at `endTime 4000` | what `build_and_run.sh` ALONE produces, with no manual step |
| **L128b** | L128a continued to t = 16000 | reproduction of the published fine leg under the published protocol |

`build_and_run.sh` was to be copied verbatim into the re-run directory with
**exactly one edit**: the leg list `for n in 32 128` widened to
`for n in 32 64 128`. For n = 64 the script's `sed` substitution is a no-op on
the archive's own `hex (0 1 3 2 4 5 7 6) (64 64 1)`, so L64's dictionaries are
byte-identical to the archive's and the script's own 11-file `cmp` guard proves
it. `analyse_k0b_mesh.py` was to be copied verbatim and not edited at all.

The committed archive case at `verification/runs/THERMAL_K0_runs/` was NOT to
be written to. `measure()` writes `constant/polyMesh`, `log.blockMesh` and
`log.cellCentres` into whatever case it is handed; L64P exists so that those
writes land on a copy.

## 4. Predictions, fixed before the first solve

### P-A — provenance of the published 64x64 numbers (L64P)

Re-measuring the committed t = 4000 fields through the same code path shall
reproduce the published `Nu_avg_hot = 4.553798947182756` to **|relative
deviation| < 1e-9**. This is a re-read of the same bytes by the same
arithmetic and is close to an identity; it is **reported and gated only on
provenance**, never treated as evidence about the flow
(`VERIFICATION_CHARTER.md:106-111`). A deviation above 1e-9 would mean the
published JSON was not produced from these fields by this code.

### P-B — the leg D403 names: does a fresh 64x64 solve reproduce it? (L64)

**Predicted: yes, to within 0.1 %**, and plausibly to machine precision — the
solver build is the same `_481094f-20260618 OPENFOAM=2606` that wrote the
archive log on 2026-08-17, the run is serial and deterministic, and every
dictionary is byte-identical.

| |Nu_avg_hot(L64) − 4.553798947182756| / 4.553798947182756 | reading |
| --- | --- |
| **< 0.1 %** | the published 64x64 number REPRODUCED |
| 0.1 % – 1 % | reproduced in kind, deviating in value; every deviation quoted as a number |
| **> 1 %** | **NOT REPRODUCED.** To be reported at full volume, ahead of every other result in the record |

### P-C — the 32x32 leg (L32)

Predicted to reproduce `Nu_avg_hot = 4.649689954678544` within 0.1 %, and
predicted to **terminate at t = 1386** by `residualControl` rather than at
`endTime 4000`. The stopping iteration is a sharper reproduction signal than
the value: it is an integer, and it cannot be hit by accident.

### P-D — does `build_and_run.sh` ALONE reproduce the published rung? (L128a)

**Predicted: NO, and this is the prediction this re-run exists to make in
advance rather than to discover after the fact.** The committed
`build_and_run.sh` runs every leg to the source case's `endTime 4000` and
contains **no continuation step**. The published 128x128 leg was continued by
hand to 16000 iterations; the rung's own README describes the continuation in
prose and `K0b_m128/system/controlDict.4000` is the surviving fingerprint of
the hand edit, but nothing in the script performs it.

Predicted: L128a lands near the README's own account of the unconverged value,
**Nu_avg_hot ≈ 4.3255**, i.e. **≈ 4.5 % below** the published
`4.528816741169209`; and the triple 4.6497 / 4.5538 / 4.3255 is non-monotone in
the Richardson sense with an observed order near **−1.25**.

| outcome | reading |
| --- | --- |
| L128a within 0.1 % of 4.528816741169209 | the script DOES reproduce the rung unaided; P-D was wrong |
| L128a deviating > 1 % from 4.528816741169209 | **the committed script does not reproduce its own published numbers without an undocumented manual step** |

### P-E — the published fine leg under the published protocol (L128b)

Continuing L128a to t = 16000 with `startFrom latestTime`, `endTime 16000`,
`writeInterval 2000` — the exact edit whose fingerprint `controlDict.4000`
preserves — shall reproduce `Nu_avg_hot = 4.528816741169209` within 0.1 %.

### P-F — the mesh-sensitivity statement itself

With L32, L64P (or L64) and L128b, predicted: the triple monotone decreasing,
observed order **p ≈ 1.94**, Richardson extrapolate **≈ 4.5200**, fine-pair
**GCI ≈ 0.243 %**, and the 64→128 change **≈ 0.55 %**.

## 5. The convergence criterion, fixed here

A leg counts as **CONVERGED** only if, at its final iteration, the initial
residuals of all four solved variables met the case's own `residualControl`
targets — `p_rgh 1e-07`, `U 1e-08`, `T 1e-08` — or the run terminated because
`residualControl` fired. Anything else counts as **stopped at `endTime`**, and
its number is a number the solver had not finished moving.

**Registered before this run, from a reading of the committed archive log
rather than as a prediction:** the published 64x64 leg did NOT meet that
criterion. Its final initial residuals at t = 4000 were Ux 1.510e-07, Uy
1.657e-07, T 9.593e-08 and p_rgh 1.477e-07, against targets of 1e-08 for U and
T. `analyse_k0b_mesh.py:264-265` cites *"the final initial residual of 9.6e-08
in its own log"* as that leg's convergence evidence — which is the **T**
residual alone, the smallest of the four, and it stands **9.6x above T's own
1e-08 target** while U stands **16x above** its own. This is recorded here,
before the re-run, so that it cannot be presented afterwards as something the
re-run discovered.

## 6. What is reported and never gated on

`energy_balance_pct`, the hot-wall/cold-wall Nusselt closure, is a
**near-identity** on this case: the cavity is sealed, both vertical walls are
fixed-temperature Dirichlet, the horizontal walls are adiabatic, and any
converged discrete field satisfies the balance to solver tolerance whether or
not the physics is right. Per `VERIFICATION_CHARTER.md:106-111` it is reported
and **never gated on**. The same applies to the internal assertion at
`analyse_k0b_mesh.py:270`, which checks one estimator against another
estimator of the same cells.

## 7. Verdict mapping, fixed here

Three separately-verdicted items. Vocabulary is the fixed set — PASS, GATE
REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING.

| Item | PASS if | GATE FAIL if |
| --- | --- | --- |
| **V1 — the published numbers reproduce** | L32, L64 and L128b each within 0.1 % of their published `Nu_avg_hot`, and L64P within 1e-9 | any of them deviating > 1 % |
| **V2 — K0b's numbers move with mesh by a stated amount** | the three-mesh triple monotone, fine-pair GCI < 1 %, every quantity quoted with its 64→128 change | the triple non-monotone on `Nu_avg_hot`, so no convergence statement is available |
| **V3 — the committed script reproduces the rung unaided** | L128a within 0.1 % of the published fine leg | L128a deviating > 1 % — the script requires an undocumented manual step |

Anything between 0.1 % and 1 % is reported as a number in the record and
carries no verdict of its own.

**NOT A RESULT** if any leg failed to mesh, failed to solve, or produced a
field the analysis could not parse — a rung that half-ran is not a rung that
ran. **BLOCKED** if the archive could not be resolved, if the machine was
contended by another lane's solver such that timings were not attributable, or
if the hard stop in §2 was reached.

## 8. What this is not

**Not a validation.** K0b was a capability rung graded against no published
datum, and nothing here changes that. The de Vahl Davis comparison lives in
K0c next door and its reference values were not applied: these cases keep
K0b's `Pr = 0.706814` and its `limitedLinear`/`linearUpwind` schemes
deliberately, because the question is whether K0b's OWN published numbers move
with mesh.

**Not a re-costing of the original rung.** The original two-leg run was paid
for at its own authorisation. The core-minutes charged here are this re-run's.

---

## AMENDMENT A2 — 2026-08-26, **POST-COMPUTE. DISCLOSURE ONLY.** Document **v1.0 → v1.1**.

**`lines whose number changed above this section: 0`.** This amendment is appended
at the foot. Nothing above it has been edited, struck, reworded or renumbered — the
assertion is **measured**, by comparing every line above this section byte-for-byte
against this file's blob at `HEAD` before the amendment was written. **No gate,
threshold, cap or label is altered, and none could be:** this amendment adds no test,
changes no instrument and moves no number.

**Version convention, stated so it is not read as an invented history:** this document
carried no explicit version string. It is named **v1.0** as it stood, and this
amendment takes it to **v1.1**. No earlier version is claimed to have existed.

**Condition — POST-COMPUTE.** This rung has graded and published. `CLAUDE.md` rule 2
therefore governs in its post-compute limb: *"changes land only as dated addenda that
cannot alter a gate, threshold, cap or label."* **This is such an addendum.** No
original is struck and **no verdict in this rung is reopened.**

### The defect — `assert` is not a guard, because `python3 -O` deletes it

`python3 -O` and `PYTHONOPTIMIZE=1` **remove every `assert` statement outright.** A
check written as an `assert` therefore cannot carry a refusal, a guard, a control or a
gate: under one interpreter flag it is gone and the surrounding code walks on. Measured
elsewhere in this lab, not hypothesised — `analyse_t8.py` under `-O` returns
`GATE REACHED` where `CLAUDE.md` rule 5 forbids it, with no error and rc 0; and a
planted-control selftest under `-O` **printed `PLANTED CONTROL PASSED` on an estimator
returning zeros** (L-332).

**This rung's exposure, re-derived 2026-08-26 by an AST parse of the blob at `HEAD`
(never `grep`, so a docstring mentioning the word is not miscounted):**

**`verification/runs/F14-cooling-ladder/K0b_D403_rerun/analyse_k0b_mesh.py` — ONE
`ast.Assert` node, and it is a NEAR-IDENTITY CROSS-CHECK inside the function that
RETURNS THE GRADED NUSSELT NUMBER:**

```
270:    assert abs(nu_at_time(case, t, Th, Tc) - mean(nu_hot)) < 1e-12 * abs(mean(nu_hot))
```

Its own comment states the job: *"cross-check the grid-mapped estimator used above
against the x-fastest-ordering shortcut used for the history, at the analysed time."*
**Two independent routes to the same Nusselt number, required to agree to 1e-12
relative.** The `dict(...)` returned on the very next lines carries `Nu_avg_hot`,
`Nu_avg_cold`, `Nu_max_hot` and `Nu_min_hot` — **the graded quantities.**

**THIS IS THE §2d.1 INSTRUMENT CLASS, AND THAT IS WHY IT MATTERS MOST.**
`VERIFICATION_CHARTER.md` §2d.1 condition (2) — *the load-bearing one*, in the charter's
own words — requires that a post-compute repair be established by *"an instrument
INDEPENDENT OF THE HYPOTHESIS — one that grades nothing, such as a near-identity, a
guard or a control."* **This assert is exactly such a near-identity.**

> **THE VERY INSTRUMENT CLASS THAT WOULD LICENSE A FUTURE REPAIR IS REMOVABLE BY AN
> INTERPRETER FLAG. Under `-O`, a disagreement between the two estimators passes
> silently, the returned Nusselt comes from whichever ordering the code happened to
> take, and the lab loses the one kind of evidence its own charter says can be trusted
> to find an error — because it cannot have been selected to move a verdict in a wanted
> direction.**

**`UNJUDGED`, not shown harmed.** No graded verdict on record was produced under `-O`
(the 2026-08-25T22:48Z bound), and **this rung is not re-graded on this ground.**

### §2d.1 is **NOT** invoked, and that is deliberate

`VERIFICATION_CHARTER.md` §2d.1 permits a grading-path change after first compute only
when all four of its conditions hold, including (3) *"the record discloses it, names
that instrument, and QUANTIFIES WHAT MOVED"* and (4) *"the pre-repair values are
recorded beside the published ones."*

**Conditions (3) and (4) are vacuous here, and that is the tell that §2d.1 is the wrong
instrument.** Converting `assert X, msg` into `if not X: refuse(...)` **cannot move any
number and cannot move any verdict on any run on record**: under plain `python3` both
forms refuse in exactly the same state, and only the mechanism and the return code
differ. The lab-wide bound of 2026-08-25T22:48Z measured that **no graded verdict on
record was produced under `-O`** — no run script invokes it, `PYTHONOPTIMIZE` is unset
on the host, and `__debug__ = True` was measured inside the DAFoam container too.
**There is nothing to quantify and nothing to record beside.**

> **INVOKING A NARROW EXCEPTION WHERE IT IS NOT NEEDED STRETCHES IT, AND A STRETCHED
> EXCEPTION IS HOW THE NEXT REAL ONE GETS WAVED THROUGH.**

§2d.1 was cut to fit a repair that moved every Nusselt number in a rung by 10–27 %.
**Reaching for it to authorise a change that moves nothing teaches the lab that the
exception is available for changes that are merely desirable.**

### What happens instead

1. **The instrument is NOT edited and stays byte-identical to its blob at `HEAD`**,
   verified at this amendment.
2. **This amendment is the disclosure**, so that a reader auditing the instrument does
   not have to rediscover the exposure.
3. **The repaired form lands in the SUCCESSOR's instrument and is never retrofitted
   here.**

### The form the successor must take — specified, not applied

**Territory rule, adopted from cfd under the disposal rule: no `assert` in an
instrument may carry a refusal, guard, control or gate.** The three-arm shape is cfd's
already-registered one (`verification/campaign/CFD_ASSERT_RULE_REFINEMENT_2026-08-25.md`
§1), adopted rather than invented:

1. **The guard becomes `raise` or `sys.exit(2)`, never an `assert`**, and becomes the
   **primary** runtime check rather than belt-and-braces beside a selftest. A selftest
   is a **test, not a runtime guard** — it does not run during grading.
2. **The refusal is DRIVEN under `python3 -O` and shown to FIRE identically**, against
   a sacrificial mutant, on the guarded path. **Not "the selftest passes under `-O`"**:
   a passing selftest exercises the clean path, and the clean path is the one an
   evaporated guard still walks. **A mutation battery cannot see this hole unless the
   battery is itself run under `-O`, because the battery and the hole live under
   different flags.**
3. **A statement-type check over the instrument's own AST requiring ZERO `Assert`
   nodes**, catching a revert **without running anything**. Committed implementation:
   `scripts/check_assert_guards.py --require-clean <path>`, whose own selftest plants an
   `assert` into a sacrificial fixture and **refuses if the checker cannot see it**.

**Specific to this rung, and it is the general point:** a near-identity is
**evidence**, not decoration, and evidence must be **reported, not merely tested**. The
successor must `refuse()` on disagreement **and print the measured relative difference
whichever way it falls** — a near-identity whose only output is silence cannot later be
cited under §2d.1, because there is no recorded value to cite.

### Cost

**Zero core-minutes.** No solver ran for this amendment. AST parsing on the login box.
`docs/COST_CALIBRATION.md` gains no row: there is no compute to calibrate.

**No verdict in this rung is reopened by this amendment. Nothing here has been sent,
filed, submitted, uploaded, registered or posted anywhere outside this box
(`CLAUDE.md` rule 7).**
