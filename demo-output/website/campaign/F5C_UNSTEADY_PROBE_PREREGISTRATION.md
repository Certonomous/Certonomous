# F5c backward-facing step — retargeted unsteady-probe arm: pre-registration

**Written 2026-08-10. FILED FOR CHIEF REVIEW, NOT LAUNCHED.** No solve is spent
against this document until the chief approves it. Docket item:
`f5c-unsteady-probe-run` (well W1, `est_core_min` 25.0).

This document **replaces** the arm's previous pre-registration in substance. The
premise that one was written against is dead, and a pre-registration written
against a dead premise cannot be patched — it has to be re-asked.

Model rule, per SUPERVISION_CHARTER §5: written on the session default model.
Stated, not silent.

---

## 1. What died, and what the question actually is now

**The old premise.** Review entry 5 of 2026-08-07 sent this arm out to explain
*"converged solves 4–12× wrong on reattachment, wandering."*

**The premise is dead and our own repository killed it nine days before the
review was written.** Commit `fe121af2` (2026-07-31) proved in
`backstep_case.py::parse_wall_raw` that the original F5c detector read
OpenFOAM's `wallShearStress` with the sign backwards — on a lower wall the
function object returns τ_x **negative** under attached forward flow, so the
neg→pos crossing the detector called "reattachment at 0.5–1.5H" was the
downstream edge of the secondary corner eddy, and the "unexplained second
separation at x/H ≈ 6–8 persisting to exit" was the real reattachment followed
by ordinary attached flow. The archived `sign_convention_control` run (plain
channel, no step: attached forward flow, τ_x negative at all 100 wall faces) is
the empirical proof. Corrected reading: **x_r/H ≈ 5.6, i.e. −10.5% against
Driver & Seegmiller's 6.26 ± 0.10** — inside the documented linear-eddy-viscosity
underprediction family, not four to twelve times outside it.

**The inlet, separately, is not the mechanism either.** The zero-compute audit
(`ZERO_COMPUTE_DIAGNOSTICS_2026-08-08.md` Task 1) measured it clean at the
experiment's own reference station — δ/h +0.3%, Re_θ +5.0%, inside the declared
±10% — and mildly under-developed at the step lip (Re_θ = 4,768 measured against
5,000 documented, **−4.6%**; δ/h roughly −9 to −12%), owned by the uniform-k
inlet whose equilibrium-k repair already exists unrun.

**So the honest question this arm now asks is:**

> A −10.5% steady miss with wander. **Does a genuinely unsteady reattachment
> region explain the wander?**

It is emphatically **not** "why are we 4–12× wrong". Nobody is 4–12× wrong. The
arm is now a normal, well-posed RANS question about whether a steady fixed-point
formulation is being applied to a flow that does not have a fixed point, on a
case whose steady answer is already inside the closure's documented error family.

**And there is a prior question, which §2 makes this arm's declared first act:
whether the −10.5% number itself can be regenerated with provable levers.**

## 2. The declared FIRST ACT — regenerate −10.5% with provable levers

**Binding instruction, from the charter-§9 caveat now carried on
`F5bc_unsteady_statistics.md`'s face** (`DEAD_LEVER_AUDIT_2026-08-08.md`,
commit `946e4a26`):

> Binding on the retargeted unsteady-probe arm (`f5c-unsteady-probe-run`): its
> rewritten pre-registration's **first act must regenerate this number with
> provable levers** — archived case dirs, logs retained, and the algorithm
> choice made log-provable.

**Why the number is currently unprovable, verified rather than restated.** The
caveat gives two grounds. Both were re-checked against the artifacts before this
document was written:

1. *The six original diagnostic runs' logs were never archived.* Confirmed:
   `F5c_runs/` holds only `sign_convention_control`.
2. *A surviving log could not prove it anyway, because simpleFoam prints
   identical `SIMPLE:` banners whether `fvSolution` sets `consistent yes` or
   not.* **One log did survive** — the 20,000-iteration extended run, at
   `demo-output/website/solve_registry/f5c_extended_simplec20k_20260730T042423Z.log`,
   16.4 MB, complete to `ExecutionTime = 1865.6 s`. It is a direct test of the
   caveat's claim, and the claim holds: **grepping that log for `consistent`,
   `SIMPLEC` and `relaxationFactors` returns nothing at all.** The one surviving
   artifact from the family carries zero evidence of the lever the headline is
   attributed to. The caveat is not a worry about lost logs; it is a property of
   the solver, demonstrated on the only log we still have.

**What makes it provable now, mechanically.** The lever echo
(`sdk/chief_engineer/lever_echo.py`, Verification Charter v1.5 §9, adopted
2026-08-08) writes a fenced `LEVER-ECHO` block at the head of every solver log
with the **sha256 of the exact bytes of `system/fvSolution`** (and `fvSchemes`,
the turbulence and transport dictionaries, and every `0/` field) that ran.
`backstep_case.py` already launches through the shared runner
(`from workflows.tmr_verification import _foam`), and `_foam` echoes on
`simpleFoam`, so **F5c gets the echo for free the moment it is re-run.**
`lever_echo.levers_verified_active()` then builds the record field from the log
itself.

That converts the algorithm attribution from a configuration statement into a
hash. The pre-registered proof is stated in §5 as leg A3: run the *same mesh and
iteration count* under SIMPLEC and under plain SIMPLE, and show (i) the two
echoed `system/fvSolution` sha256 values **differ**, and (ii) the two answers
differ. Until that pair exists, "SIMPLEC moved the number" is this lab's
assertion about its own settings, and this arm will not build on it.

**Also required, and currently missing.** `backstep_case.py` runs `checkMesh`
but never writes a mesh birth certificate. Every mesh this arm generates gets
`birth_certificate.json` written **at creation** from its own `log.checkMesh`
via `sdk/chief_engineer/mesh_certificate.py`, and
`mesh_certificate.certificate_admits()` must pass before `simpleFoam` launches —
MESH_STANDARD v1.1 / charter §9, born clean or it does not enter. The F5c blocks
are axis-aligned with exactly zero non-orthogonality and zero skewness, and their
only checkMesh finding is the expected near-wall high aspect ratio, which under
`parse_check_log` yields verdict `flagged` — an accepted verdict, and one that
belongs on the record rather than in a habit.

## 3. The detector, and what each mesh level can and cannot adjudicate

This is the constraint that shapes the whole arm, so it is stated before the
legs rather than discovered inside them.

x_r is read as a **zero crossing of Cf between adjacent wall face centres**. It
therefore cannot be resolved finer than the wall face spacing near the crossing.
From `backstep_case.py`'s own commit-`fe121af2` note:

| level | cells | face spacing near x/H ≈ 6 | can it adjudicate the ±0.10H reference band? |
| --- | --- | --- | --- |
| `coarse` | 9,050 | **0.55–0.81 H** | **No** — every increment is larger than the band |
| `medium` | 20,160 | 0.28–0.43 H | No |
| `fine` | 46,500 | 0.15–0.23 H | Marginal |
| `xr-coarse` | 28,300 | ≤ 0.05 H (uniform through the closure region) | **Yes** |
| `xr-medium` | 59,430 | ≤ 0.05 H | Yes |

**Consequence, pre-registered:** the *reproduction* question ("does ≈5.6 come
back") is asked on `coarse`, because reproducing the archived configuration means
reproducing its mesh. The *wander* question is **not answerable on `coarse` at
all** — a wander of 0.2H cannot be seen through a 0.55–0.81H detector — so no
wander verdict will be claimed from a `coarse` run, in either direction. The
wander question belongs to `xr-coarse` and nowhere cheaper. **No `xr-*` level has
ever been run.**

## 4. Materiality bars, all fixed before any run

| # | question | statistic | bar |
| --- | --- | --- | --- |
| **M1** | does −10.5% regenerate? | corrected x_r/H from leg A2 | **REGENERATED** if \|x_r/H − 5.6\| ≤ 0.81 H (one `coarse` face spacing at the crossing — the best this detector can do, and the honest bar for it). **NOT REGENERATED** otherwise, and the −10.5% headline retracts to *unmeasured* |
| **M2** | is the algorithm attribution provable? | echoed sha256 of `system/fvSolution` in A1 vs A3, and their x_r/H | **PROVEN** if the two hashes differ **and** \|Δx_r/H\| > 0.81 H. If the hashes differ but \|Δx_r/H\| ≤ 0.81 H, the honest reading is *the algorithm choice is not resolvable on this detector* — not that it does nothing |
| **M3** | is the wander real, in the primary reattachment? | peak-to-peak spread of x_r/H over the **final half** of leg B1's sampled iteration history | **MATERIAL** if spread > 0.20 H (the full width of the ±0.10 reference band). **IMMATERIAL** if spread ≤ 0.10 H (half the band). Between the two: **undecided**, reported as such |
| **M4** | is the inlet repair a repair? | Re_θ at the step lip, leg B2 vs B1 | **A REPAIR** if \|Re_θ − 5,000\|/5,000 falls below B1's measured −4.6%. Graded on Re_θ **and on nothing else** — `backstep_case.py`'s own instruction is that this option *"must not be selected on the basis of the reattachment length it produces"*, and this pre-registration binds itself to that |
| **M5** | does the inlet own part of the −10.5%? | Δx_r/H between B2 and B1, on the `xr-coarse` detector | **OWNS A SHARE** if \|Δx_r/H\| > 0.10 H (half the reference band, and ≥ 2 face spacings). **EXONERATED** if ≤ 0.05 H (one face spacing). Between: undecided |

M4 and M5 are deliberately separated. A repair that fixes the inlet metric and
moves nothing downstream is a *successful repair with no consequence for the
gate*, and that is a reportable result, not a disappointment to be argued around.

## 5. The legs, in order, with the price of each from its nearest measured basis

**Pricing discipline.** The calibration finding is binding: *"the predictor is
the basis, not a factor."* Every price below names the measurement it comes from
and states whether that measurement is of **the same configuration** (in which
case it is the predictor) or of a **different one** (in which case the assumption
carrying it across is written down and is falsifiable). All F5c runs are serial
(`nProcs: 1`), so core-min = wall-seconds / 60.

### Stage A — regeneration on `coarse` (the declared first act)

| leg | configuration | basis — the measurement it is priced from | core-min |
| --- | --- | --- | --- |
| **A1** | `coarse`, SIMPLEC (`consistent yes`, relax p 0.3 / U 0.6), 2,000 iterations, `--sample-every 50` | **the identical configuration**, `F5bc_unsteady_statistics.md` evidence table row 3: 142.6 s | **2.38** |
| **A2** | `coarse`, SIMPLEC, 8,000 iterations, `--sample-every 200` | **the identical configuration**, row 4: 672.4 s | **11.21** |
| **A3** | `coarse`, plain SIMPLE (`--simple`, relax p 0.15 / U 0.4), 2,000 iterations, `--sample-every 50` | **the identical configuration**, row 1: 115.3 s | **1.92** |
| | | **Stage A** | **15.51** |

A1 and A2 are the two runs the ≈5.6 headline is attributed to (the record says
"the SIMPLEC coarse case" without saying which iteration count, so both are run
rather than one guessed). A3 is what makes M2 answerable at all.

**Declared departure from the bases.** All three bases were measured with
`sample_every = 0`; these legs sample the wall profile periodically, which the
bases did not pay for. The sampling intervals above are chosen to hold each run
to ~40 samples so the I/O stays bounded, and **the measured overhead is reported
against the basis whatever it is**. It is named here so it cannot be reported
later as a surprise.

### Stage B — the detector-resolved pair (baseline vs the inlet repair)

| leg | configuration | basis | core-min |
| --- | --- | --- | --- |
| **B1** | `xr-coarse` (28,300 cells), SIMPLEC, 8,000 iterations, `--sample-every 100`, baseline uniform-k inlet | see below | **35–39** |
| **B2** | identical to B1 **plus `--inlet-bl-turbulence`** | same | **35–39** |
| | | **Stage B** | **70–78** |

**The basis, and the assumption carrying it.** Two independent measurements of
the *same solver on the same 9,050-cell mesh* give a per-iteration cost:
672.4 s / 8,000 = **0.0841 s/it** and 1,865.6 s / 20,000 = **0.0933 s/it** (the
latter from the surviving `solve_registry` log). `xr-coarse` is 28,300 cells =
**3.127×**. **The stated, falsifiable assumption is that serial simpleFoam cost
scales at most linearly in cell count at fixed iteration count**, giving
0.263–0.291 s/it and 2,100–2,330 s over 8,000 iterations. If the measured cost
exceeds the top of that band, the assumption is wrong and is reported wrong.

**Iteration count, and the continuation declared now.** `STEP_ITERATIONS` sets
20,000 for every `xr-*` level. This arm runs **8,000** and applies the module's
own settle criterion — *"a settled x_r history is the check that does not depend
on reading the right residual"* — to the sampled x_r history. **If the x_r
history is not settled at 8,000, the continuation to 20,000 costs a further
53–58 core-min per leg, and that number is declared here rather than discovered
mid-run.** M3 is evaluated on whatever history exists; an unsettled history is
itself evidence bearing on M3 and is reported as such.

### Stage C — the unsteady probe itself (NOT priced for approval here)

Stage C is what the docket item is named for, and this pre-registration
**declines to price it as an approved run**, for a reason that has to be on the
record:

**The docket's `est_core_min` 25 is not consistent with the docket's own stated
cost basis.** That basis is F5b's measurement that *"the unsteady pitching run to
one period is running roughly 15–25× longer in wall-time than the comparable
steady BFS coarse run (115 s)"*. Applied to the comparable steady run, 15–25×
115.3 s gives **29–48 core-min** — already over 25 before any of the following:

- **`pimpleFoam` does not exist for this case.** `backstep_case.py` is
  `simpleFoam`-only: `application simpleFoam`, `deltaT 1`, `endTime` counted in
  iterations, no `ddtSchemes` beyond steady state, no PIMPLE block. The unsteady
  path has to be **built**, and building it is not in the 25.
- **A time-mean needs a physical averaging window, not an iteration count.** The
  documented mechanism this arm is testing for is low-frequency bubble flapping
  (Eaton & Johnston 1981; Kaltenbach et al. 1994), whose Strouhal number is
  St_H ≈ 0.06–0.08 on U_ref/H — a flapping period of **12–17 H/U_ref**. Ten
  periods of averaging is 120–170 H/U_ref of simulated time, and that window is
  what sets the cost, not the mesh.
- **On the `xr-coarse` detector the same multiplier applied to B1's own wall
  gives 525–975 core-min.** On `coarse` it gives 29–48 core-min but the detector
  cannot adjudicate the band.

**So Stage C enters as a separately-priced, separately-approved item**, with its
own pre-registration, a hard wall cap, and partial reporting — which is what the
docket item's own gate already contemplates (*"A partial result is reported
rather than overspending, because unsteady cases have overrun this lab by fifteen
to twenty five times before"*). What Stage A and B buy is the right to ask for it
on evidence: **if M3 comes back IMMATERIAL, Stage C should not be run at all**,
and this arm will say so.

### Total requested now

**Stage A: 15.5 core-min. Stage B: 70–78 core-min. Requested total: 85–94
core-min against the docket's `est_core_min` 25.0 — a declared overrun of
3.4–3.8×.** The cause is named rather than discovered: the filed 25 (and the
zero-compute audit's *"one `xr-coarse` re-collection ... at ~25 core-min as
already filed"*) priced an `xr-coarse` run without a measured basis for one, and
no `xr-*` level has ever been run. The nearest measurements this lab owns say
`xr-coarse` alone is 35–39 core-min. Silent overrun is forbidden, so this is
stated before launch and not after.

**Recommended approval shape:** approve **Stage A alone first** (15.5 core-min).
It is the charter-mandated first act, it is priced from the identical
configurations, and it can retire or confirm the entire premise — including
outcome O3 below, which would make Stage B moot.

## 6. What each outcome means — stated before the runs

### On Stage A

- **O1 — regenerated and provable.** A2 returns x_r/H within one face spacing of
  5.6 (M1 REGENERATED), and A1/A3 differ in both hash and answer (M2 PROVEN).
  The −10.5% headline is now on evidence rails for the first time: archived case,
  retained log, hash-bound levers. **Stage B is justified and proceeds.**
- **O2 — regenerated but the algorithm attribution does not survive (M1
  REGENERATED, M2 not).** The number is real; "the SIMPLEC coarse case" was a
  label, not a cause. `F5bc_unsteady_statistics.md`'s SIMPLE-vs-SIMPLEC rows get
  a second amendment saying so, and Stage B proceeds on the regenerated
  baseline with the algorithm named as *not resolvable at this detector*.
- **O3 — NOT regenerated (M1 fails).** The ≈5.6 lives only in a committed
  docstring; if it does not come back from the configuration it is attributed to,
  **the −10.5% retracts to *unmeasured*** and F5c's status reverts to open with
  no headline number. **Stage B does not run**, because there would be nothing to
  measure a wander against. This outcome is why the charter made regeneration the
  first act, and it is a genuinely possible result, not a formality.

### On Stage B — and this is the arm's actual question

- **O4 — the wander is MATERIAL (M3).** The primary reattachment moves by more
  than the full reference band across a settled iteration history on a detector
  fine enough to see it. That is the signature of a steady fixed-point solver on
  a flow with no fixed point, and it is the direct, evidence-based case for
  Stage C: **the unsteady probe becomes the right next spend**, asked as "does a
  time-averaged URANS produce a stationary mean, and where does it land relative
  to 5.6 and to 6.26."
- **O5 — the wander is IMMATERIAL (M3).** The corrected primary reattachment is
  *stationary*, and the wander on the record was **the corner eddy's edge
  wandering, not the reattachment's** — which is precisely what the 2026-08-08
  amendment suspected but could not check. Then there is no wander to explain,
  **the unsteady probe's premise dies with it, and Stage C is not run.** F5c
  closes as an ordinary steady-RANS result: −10.5% against Driver–Seegmiller,
  inside the documented linear-eddy-viscosity underprediction family, reported
  with its band and its detector resolution on its face. *This outcome retires a
  live docket item, and it is the reason Stage B is worth more than Stage C.*
- **O6 — undecided wander.** Reported undecided with the settle state of the x_r
  history stated, and the 20,000-iteration continuation priced (§5) as the
  declared next ask. No branch is claimed from the gap.

### On the inlet repair

- **O7 — repair works and moves the gate (M4 repair, M5 owns a share).** Part of
  the −10.5% is inlet development, not closure error, and every subsequent F5c
  number — including anything Stage C measures — must be taken on the repaired
  inlet. The baseline configuration is superseded, not merely annotated.
- **O8 — repair works and moves nothing (M4 repair, M5 exonerated).** The
  clean result: the inlet metric is fixed, the gate quantity is indifferent, and
  the −10.5% is closure error to the resolution of this detector. The uniform-k
  inlet stops being a suspect. Reported as a success, because a measured
  exoneration is worth what it cost.
- **O9 — the repair does not repair (M4 fails).** `--inlet-bl-turbulence` moves
  Re_θ at the step no closer to 5,000. Then the option is mis-specified, is
  reported as mis-specified, and does **not** get carried forward as "the repair"
  in any later record. Given it has never been run, this is a real possibility
  and it is named here so it cannot be quietly dropped.

## 7. What will NOT be claimed

- No gate is declared PASSED by this arm. F5c's status is `GATE NOT REACHED`
  and only a detector-resolved run against the ±0.10H band could change that;
  Stage B is one mesh level, and one level does not close a gate.
- The 6.26 ± 0.10 reference is never adjusted, weighted, or re-derived to meet a
  computed number.
- **No wander verdict is claimed from any `coarse` run**, in either direction —
  the detector cannot support one (§3), and Stage A exists to answer M1 and M2,
  not M3.
- The inlet repair is never selected, preferred, or described as validated on the
  basis of the reattachment length it produces (§4 M4).
- Stage C is not launched under this pre-registration under any outcome. It gets
  its own document, its own price, and its own approval.

## 8. Execution discipline (on approval)

Pre-register-then-commit is already satisfied by this document; any approved
stage is launched only after this file's commit hash is cited in the run record.
Runs are `setsid`-detached with `.t0`/`.rc`/`.t1` ledgers and polled inline. Each
case directory is archived under `F5c_runs/<leg>/` via the existing `collect.py`
(system/, 0/, constant/, `log.checkMesh`, gzipped `log.simpleFoam`, `record.json`,
`wall_shear_profile.json`, `xr_history.json`, and the raw evidence samples) —
`postProcessing/` is gitignored, so the artifacts the claims rest on are lifted
out or they do not survive, which is exactly how the original six runs were lost.
Every mesh carries its birth certificate at creation (§2); every solver log
carries its lever echo, and `levers_verified_active` is written into each
`record.json` from the log itself. Box load, free memory and running containers
are checked before each launch and staggered against the A3 ladder agent's
container work.

*Nothing below this line existed when this document was committed.*
