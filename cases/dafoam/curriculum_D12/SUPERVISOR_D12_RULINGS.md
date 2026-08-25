# D12 — SUPERVISOR'S RULINGS: the FD pairs accepted, and four calls on D12-proper

**Written 2026-08-25 by dafoam-supervisor.** Rulings, **not parked referrals**, under Sanaa's
2026-08-25 disposal rule. Committed **before** any lane acts on them.

**SUBMISSIONS ARE PARKED.** Nothing here is sent, filed, uploaded, posted or commented.
Every defect below is in **this lab's own instruments** — no upstream report arises.

---

## 1. THE FD PAIRS — BOTH VERDICTS ACCEPTED, AND THE SPLIT VINDICATES THE BUY

I ruled earlier today that the D10 and D12 probe gradients had to be bought an FD pair, over
a real counter-argument I recorded at the time: a reachability probe's gradient is an
existence witness, and charter §2 may not bite. **One pair passed and one could not
adjudicate. That split is a better outcome than two passes and it is worth stating why.**

### D10-F′ — `PASS`. **Charter §2 is now satisfied for D10-P′.**

| quantity | value |
|---|---|
| adjoint `d(HFX)/d(patchV[0])` | `1.9771502962421681e+02` |
| central FD at the reference step | `1.9771503832566850e+02` |
| **relative error** | **`4.401007e-08`** against a band of `5.0e-2` |
| reference step | `h = 1.000e-03` m/s |
| δ_repeat | **exactly `0.000000e+00`** |

Plateau established over all six registered steps, adjacent values agreeing to between
`1.3e-07` and `1.9e-04` against a registered `1.0e-2`. **The step is PROVED to lie in the
plateau, not asserted** — charter §2's actual requirement.

**The corroboration nobody designed in is the strongest part.** The error column is a clean
**V with its minimum exactly at the reference step**: `2.3e-06, 3.9e-07, `**`4.4e-08`**`,
1.8e-07, 6.3e-06, 2.0e-04` — roundoff rising as `h` falls, `O(h²)` truncation rising as `h`
grows. **The reference-step rule is positional over the plateau and never reads the adjoint,
yet it landed on the step that independently minimises disagreement. A grader fitting the
step to the answer cannot produce that.** That is an unforgeable signature and I weight it
accordingly.

**I accept the record's own caution and I will not let it be dropped downstream.**
`4.4e-08` is tight enough that §7's 2.5–5 % harness floor would ordinarily make it *"a claim
about the harness"*. The escape is legitimate and narrow: `DAFOAM_CHARTER.md` §2 records
that the floor is calibrated on **`shape`** DVs **through IDWarp**, and `patchV` is a
boundary condition with **no mesh warp anywhere in its chain**. **But all three supporting
facts are consistency arguments and none is an independent measurement, and the record says
so.** That caveat travels with the number.

### D12-F′ — `NOT A RESULT` on both components. **Charter §2 is STILL NOT satisfied for D12.**

All 24 stages `rc=0`, `OOMKilled false`, **every control passed** — this is not a failed run.
Longest run of consecutive FD steps agreeing to 1 %: **one**, on each component. **There is
no plateau, so there is no admissible step, so there is no FD table.**

**The verdict is not an artifact of a tolerance, and the lane checked that against itself
rather than waiting to be asked.** At 2 %, at 5 %, and at D12-proper's own registered 2 %,
neither component plateaus. Component 3 would need **10 %**; component 0 would need **50 %**,
wider than the charter's entire FAIL threshold.

**THE HEADLINE, AND IT IS A NUMERICS FACT THIS FAMILY DID NOT HAVE:** **δ_repeat is exactly
`0.000000e+00` while the objective's perturbation-response floor is ≈ `1.65e-06` absolute
(`1.8e-05` relative) on component 3 — three-plus orders of magnitude above it — and
≈ `8.4e-09` on component 0. THE FLOOR IS COMPONENT-DEPENDENT.** Measured model-free: the FD
signal at `h=1e-5` is `1.05e-06`, **smaller** than the `3.07e-06` at `h=1e-6`. **A linear
response cannot do that.** From `h=1e-4` up the signal scales cleanly 10× per decade.
Noise-limited and truncation error cross at **~5 %**: on this window **an FD verification
could not have beaten ~5 % even in principle.**

**This is why the pairs were worth buying and it is the opposite of what I expected.** A
repeat-only noise estimate said the objective was noiseless. **It is not noiseless where it
matters — under perturbation — and δ_repeat cannot see that.** Had D12-proper been sized off
δ_repeat alone it would have chosen a step in the noise floor and produced a table whose
disagreement had nothing to do with the adjoint.

**What the lane refused to say, correctly:** component 0 sits 30–46 % from its adjoint at
every step, and the central estimate at `h=1e-3` nearly coincides with the one-sided estimate
the plant implied, **so that 30 % gap is not curvature.** Without a plateau it cannot be
separated from an unconverged FD, so **it appears in no verdict** and is carried as a
recommendation. **A gap that cannot be attributed is not evidence in either direction**, and
refusing to bank it as a finding is the right call.

**Both probes' `GATE REACHED` reachability verdicts are UNTOUCHED**, as my ruling fenced.

---

## 2. THE CATCH THAT MATTERS MOST — MY OWN CHECK WOULD HAVE CERTIFIED A DOCUMENT, NOT AN ARMED ITEM

**`PREREGISTRATION.md` §4 names FOUR instruments. TWO DO NOT EXIST**: `d12r_series.py` and —
decisively — **`d12r_stage_and_run.sh`, THE LAUNCHER. There is nothing to run.**

**I verified this myself and I applied L-325's own prescription this time**, having failed to
apply it four hours ago: a **predicate that names the thing sought** (`find -name`), never a
pager, **plus a planted name I knew existed to prove the pattern returns it.**
`d12r_grade.py` came back; `d12r_series.py` and `d12r_stage_and_run.sh` are **absent from
disk anywhere** and `git log --all` returns **nothing on any branch** for either.

**Had the lane obeyed its brief and committed that document as a v1.0 freeze, my
non-delegable check #4 — "the pre-registration is committed" — would have returned TRUE, and
it would have been certifying a DOCUMENT rather than an ARMED ITEM.** The gates would have
closed against a half-absent instrument set.

**That is a defect in the check as I have been running it, and it is mine, not the lane's.**
Rule 2 freezes the gate; it does not ask whether the thing the gate grades can run.
**AMENDED, effective now, for every item in this family: my pre-compute check is that the
pre-registration is committed AND that every instrument it names EXISTS — established by a
predicate naming each file, with a planted control proving the enumeration can return a name
it should find.** A pre-registration naming an absent instrument is **not armed**; it is a
plan. **Twice today "not found" has been the return value of two different situations, and
both times the instrument was mine.**

---

## 3. RULING — THE LAUNCHER IS AUTHORED, AND THE SAFEGUARD IS MY READ, NOT A LANE BOUNDARY

The lane declined to write it and **flagged the judgement as mine to overrule** rather than
quietly doing either thing. Its argument: authoring the launcher would put **author and
auditor of a 250-core-min item in one lane**, under a third lane's pre-registration.

**The concern is real and raising it was right. I rule the other way, and the reason is
`D4-DEF-4`, which landed today.**

A launcher is **not** an auditor — every graded quantity comes from the frozen comparator
reading artifacts on disk, and the comparator was authored by a different lane and is frozen.
**But a launcher IS a PRODUCER, and D4-DEF-4 just proved that the producer is exactly where
invisible corruption lives.** D4's endpoint was extracted in driver-scaled units and applied
as physical; **every count-, plant- and order-based control downstream passed on it and the
fully armed instrument set would have certified a design point that was not the optimum.**
Author/auditor separation would not have caught that. **What catches it is a supervisor
reading the producer as code, and a control that establishes WHERE the run point is.**

**RULING, with three binding conditions:**

1. **The launcher is authored by the lane that fires it.**
2. **I READ IT PERSONALLY AS A DIFF BEFORE ANY NUMBER IT PRODUCES IS BELIEVED**
   (`SUPERVISION_CHARTER.md` §3 check 1, non-delegable). It is a measurement-critical
   instrument and is treated as one. **"I tested it, it's fine" from the lane that wrote it
   is evidence, not my read.**
3. **It carries a WHERE-control, not only THAT-controls.** The D12 case has no pinned DV
   analogue to `patchV[0]`, so the equivalent is: **the launcher writes, and the comparator
   reads back from disk, the actual perturbation applied to each component** — magnitude,
   sign and index — and the grade **refuses** if the applied perturbation does not match the
   registered one. **A count of stages is not a witness of what was perturbed.**

**The two-phase structure the lane identified is real and is not an obstacle:** G12R-4 sizes
the sweep from `|g_i|` taken from S5's adjoint, so S6's steps are not computable until S5
finishes. **The launcher stages in two phases; it does not choose a step.** The rule that
selects the step stays frozen in the comparator and must remain **positional over the
plateau, never reading the adjoint** — which is precisely the property that made D10-F′'s
V-shaped minimum an unforgeable corroboration.

---

## 4. RULING — `δ_eff := max(δ_repeat, δ_window, δ_pert)`. **APPROVED.**

As registered, G12R-4 computes `δ_eff = max(δ_repeat, δ_window)`, **both from UNPERTURBED
runs.** D12-F′ measured `δ_repeat = 0.000000e+00` against a perturbation-response floor of
≈ `1.65e-06` — **three-plus orders above.** **An unperturbed-run noise estimate is
demonstrably blind to the floor that actually limits the finite difference.** That is
measured, not preferred.

**Legal, and the condition is stated:** D12-proper's run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D12-cylinder-unsteady/` **does not exist**, checked
by `test -e` returning false; **no container has started for this item.** The pre-registration
is **not yet committed**. Rule 2's pre-compute window is fully open, so this is an amendment
before first compute, not an addendum after it.

**It can only RAISE `h_min`**, which is the conservative direction: it can cause a `NOT A
RESULT` and cannot manufacture a `PASS`. **A change that can only make the gate harder is not
the change §2d.1 exists to prevent.**

**Condition: `δ_pert` is MEASURED for D12-proper's own configuration, not imported from
D12-F′.** The floor is **component-dependent** — `1.65e-06` versus `8.4e-09` on two
components of the same probe — so it is a property of a configuration, exactly as
`DAFOAM_CHARTER.md` §5 says an FD reference is. **Importing it would be inventing a price
across configurations.**

## 5. RULING — G12R-0 MUST CARRY THE AGE GUARD AND THE `ExecutionTime` COUNT. **REQUIRED.**

Not a preference and not mine to waive: **`CLAUDE.md` rule 4 is a standing rule.** A
completion gate without the age guard cannot tell a fresh result from a stale directory, and
`0/` is touched last at launch precisely so it dates the run allowed to produce the answer.
**Pre-compute, so legal; mandatory, so not optional.** The lane correctly noted this repair
and the missing launcher are **one piece of work** — G12R-0 reads the launcher's manifest.

## 6. RULING — THE `δ_window ≡ 0` HAZARD IS RESOLVED BEFORE THE FREEZE, NOT AFTER

`δ_window` is **identically zero whenever `W` divides the shedding period** — and **`W = 300`
is registered.** The lane found this through a fixture bug (`U-06` used `W=2` on a period-2
series) and **the fixture bug encoded a real hazard**, which is the most useful kind of test
failure. **Resolve pre-commit:** measure the shedding period for this configuration and
either choose `W` so it cannot divide it, or state why `δ_window` is not load-bearing given
§4's `δ_pert`. **Do not freeze a document whose noise floor can be identically zero by
construction.**

## 7. THE SELFTEST DEFECTS — ACCEPTED, AND `M3` IS THE ONE THAT MATTERS

Three gaps, and **in all three the gate logic was right and the TEST was wrong**, which is
the honest and less flattering finding.

- **`U-09c`** asserted the CONDITIONAL band from a **30 % per-component** error when the
  statistic is the **vector-relative** error — 20.02 %, the FAIL band. **That is precisely
  the per-component-versus-aggregate confusion charter §2 forbids**, and until repair **the
  CONDITIONAL band had never been exercised by a passing unit.**
- **`M3` is the standing proof the battery finds real gaps: deleting the sign-flip override
  ENTIRELY left the whole selftest passing**, because `U-09s`'s aggregate is 160 % and the
  override is never load-bearing there. New unit `U-09s2` uses an aggregate of **0.1414 %** —
  inside the PASS band — with one flipped component. **A control that is never load-bearing
  in any unit is not tested, however many units reference it.** Same shape as `D4-DEF-1`.

**After repair: exit 0, 40 units, 6 of 6 mutants caught. All repairs are to TEST FIXTURES; no
gate, threshold, cap, band or label changed.** Accepted. **And the standing limit holds: six
mutants is not proof of correctness, and the gaps the battery does not probe are unknown by
construction.**

---

## 8. COST — ACCEPTED, AND THE ID DERIVATION CAUGHT A LIVE COLLISION

| arm | predicted | actual | ratio | waste | row |
|---|---|---|---|---|---|
| D10-F′ | 1.9339 | **1.7501** | **0.905×** | 0.000 | **C-85** |
| D12-F′ | 4.3544 | **3.2504** | **0.747×** | 0.000 | **C-86** |
| D12-proper | — | **0.000** | — | — | none owed |

**5.0005 core-min, $0.004275 DERIVED, not measured.** Both gaps attributed to misprediction
on the `run_model` anchor; guards never fired.

**D12-F′'s zero waste is argued rather than assumed, and I endorse the argument: a `NOT A
RESULT` from a sweep that ran correctly is a PURCHASE. Classifying it as waste would make the
ledger punish the lab's most useful outcome.**

**The tolerant hand-derivation caught exactly what it was there for.** The lane's first read
said max `C-83`; re-deriving **inside the committing invocation** returned **`C-84`** — a
peer's **bold-format** row had landed mid-work, the format that has now defeated a naive
regex twice. **Ids are allocated only at append time, against HEAD, derived by hand. This is
the second independent confirmation of that rule in one day.**

## 9. WHAT REMAINS UNVERIFIED, CARRIED FORWARD NOT BURIED

**Residual contention is UNMEASURED on both arms** — `--bind-to none` avoids a known
mechanism, and **avoiding a mechanism is not measuring the residual**; no uncontended control
was bought, and the box was at load 16 of 16 while these ran. **No part of D12-proper has been
run by anyone**, including its 250.4 core-min prediction, which §6.1 itself registers as under
test. **Whether `δ_window` at `W=300` exceeds the perturbation floor is UNKNOWN and
unknowable from anything measured so far.** **The mesh-warp mechanism hypothesis for the
component-dependent floor is UNTESTED.** **`check_grader_self_blindness.py` clean is not
proof of correctness** on any of the three graders. **The patched toolchain row is UNBOUGHT on
both arms and named as unbought** — sharper for D12-F′, where IDWarp *is* in the chain.
**Neither arm reached for a forward-AD or complex-step reference.**

## 10. FOR THE NUMERICS RECORD (N-D family)

**A time-averaged unsteady objective can have δ_repeat exactly zero and still be
noise-limited under perturbation, and the perturbation floor is COMPONENT-DEPENDENT.**
Measured here: `0.000000e+00` repeat, `1.65e-06` and `8.4e-09` perturbation floors on two
components of one configuration, with a **non-monotone FD signal below `h=1e-4`** that a
linear response cannot produce. **Consequence: an FD step sized from repeat noise alone is
sized from a quantity that does not bound the error it is meant to bound.** Offered to the
chief for `docs/NUMERICS_KNOWLEDGE.md`; **no `N-` id taken — ids at append time only.**
