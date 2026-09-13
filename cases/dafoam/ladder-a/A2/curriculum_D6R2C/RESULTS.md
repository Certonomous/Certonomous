# D6R2C arm `O_mp` - RESULTS. Sanaa's D6R2 After-item 10 report.

**Verdict: `GATE FAIL` by 2.79x on G3, proceeding on directive E.**

**Item:** `D6R2C`, curriculum item on the A2 wing, three lift conditions, one geometry.
**Arm reported:** `O_mp`, the production multipoint optimisation. Complete and graded.
**Registration:** `cases/dafoam/ladder-a/A2/curriculum_D6R2C/PREREGISTRATION.md` at version 1.3,
frozen at `7f685867d`, with ADDENDUM 1, 2 and 3 appended.
**Grade record:** `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp_GRADE.json`.
**Assembled:** 2026-09-13T04:57:47Z (read from `date -u` in the invocation that wrote this line).
**Repository HEAD at assembly:** `94aeb5f96cfe9802eb896bf5cec7107f14db22f3`.
**Written by** a dafoam `lab-lane` for the `dafoam-supervisor`. **Zero solver core-minutes were
spent producing this report**; every number below is read from an artefact already on disk, and the
three figures were re-rendered by a reader that starts no solver.

**SUBMISSIONS PARKED** (`CLAUDE.md` rule 7). Nothing in this file is sent, filed, uploaded,
registered, posted or commented anywhere. That includes the two upstream-shaped findings in section 1
and section 11: they are written down here and they go nowhere. Sending is Sanaa's alone.

---

## 0. HOW TO READ THIS FILE, AND THE THREE THINGS IT WILL NOT DO

**The verdict word is fixed and is not softened anywhere below.** `GATE FAIL`. `G1`, `G2`, `G4`
and `G5` hold; `G3` misses by 2.79x. The drag result is good and the lift constraints are not held;
both facts are stated at full size and neither is used to shade the other.

**Two of Sanaa's ten items have not run.** Her item 8 (the shape/twist/trim decomposition) and her
item 9 (the fresh-mesh confirmation) are being pre-registered by a peer lane. Their sections below are
present, headed, and carry the reserved token `PENDING: <path>` in the sense
`REPORTING_CHARTER.md` §2 rule 5 fixes: *the artefact behind the section could not be read.* **No
number for either is invented, estimated or foreshadowed here.** `PENDING` in this file never
qualifies the `GATE FAIL`; it is a queue state on two sections that have no run behind them yet.

**The six fixed headings of `REPORTING_CHARTER.md` §2 are the MORNING REPORT's and are not used
here.** This is an item report answering a ten-part instruction, and imposing the morning frame on it
would produce a document matching neither. What this file does take from that charter, because those
clauses are not morning-specific: the reserved words `nothing` and `PENDING: <path>`; a
`Source:` line under every section; the rule that a cited artefact not on disk is a finding
**inside** the section that cited it; and the eight provenance tags made lab-wide by the 2026-08-31
amendment - `MEASURED` `DERIVED` `EXTRAPOLATED` `REGISTERED` `REPORTED-BY-OWNER`
`BORROWED` `ASSUMED` `TRANSCRIBED`.

**The word "transonic" is not a description of this case and is not used as one.** ADDENDUM 2
struck it: `U0 = 100.0 m/s`, `T0 = 300 K`, so `M_inf = 0.288`, and a peer lane measured the
maximum LOCAL Mach at 0.380. The case is **compressible subsonic**. The run root and the item's
directory keep "transonic" in their names as a disclosed misnomer, because renaming would break every
existing citation. **There is no shock in this flow and no figure here shows one.**

Source: `cases/dafoam/ladder-a/A2/curriculum_D6R2C/PREREGISTRATION.md` §4 and ADDENDUM 2;
`docs/charters/REPORTING_CHARTER.md` §2 and the 2026-08-31 amendment.

---

## 1. GRADIENT SPOT-CHECK TABLE

**The honest headline first: THIS ITEM HAS NO FINITE-DIFFERENCE TABLE, AT ANY DESIGN POINT.**

`DAFOAM_CHARTER.md` §1 is the bright line: *"A DAFoam gradient is not a result until a
finite-difference table stands beside it at a step proved to lie in the plateau."* §9 sharpens it for
this exact case: *"Every optimisation reports a finite-difference check of the gradient **at its final
design point**, not only at the baseline."* **Neither is satisfied for D6R2C, and the registration
said so in advance rather than being caught out.** §10 of the frozen registration:

> *"It does not verify the gradient against finite differences. That is the `F_mp` / D6RF family.
> `ARM0` compares the gradient **to itself at another rank count** — that is a *decomposition*
> check, not an *accuracy* check, and no reader may present it as one."*

**What was searched before concluding this, and how.** `MEASURED`, by execution:
`check_totals` appears **0** times in the arm log `O_mp_20260913T013230Z_226722.log`, and the
strings `Jfwd` and `J_fd` appear **0** times each; the only 81 matches on "Total Derivative" are
OpenMDAO's own `Driver total derivatives for iteration: n` lines, which are adjoint solves, not FD.
The frozen producer `d6r2c_opt_runScript.py` **does** carry an FD facility at line 572-575
(`prob.check_totals(compact_print=False, step=1e-3, form="central", step_calc="abs")`), and the arm
ran `run_driver`, so that branch was never entered. **Note what that branch would have been even if
run: one step, `1e-3`, with no sweep.** `DAFOAM_CHARTER.md` §3 requires the step be proved to lie
in a plateau, read **per component**, so a single-step `check_totals` would not by itself clear §1
either.

**The nearest FD evidence in the lab, named so the gap is visible rather than merely asserted.**
`cases/dafoam/ladder-a/A2/per_component_table/RESULTS.md` carries a 96-shape-DV per-component FD
table on the A2 MACH tutorial wing: `CD` wrt `dvs.shape`, SHIPPED toolchain, aggregate
**1.7138 %** with **zero sign flips**, but **79 of 96** components within 5 %, **89** within 15 %, and
**7 beyond 15 %**, worst **-360.75 %** at index 18; and on the PATCHED toolchain a sign flip at index
46 (analytic `+2.27367571e-06` against FD `-2.52460969e-06`). `TRANSCRIBED` from that file's
HEADLINE section. **It is not this item's FD table and must not be read as one:** it is a
single-point case, a different objective and constraint set, and a different design point from any
D6R2C iterate. **It is cited to show the lab owns an instrument for this, not to stand in for a run
that did not happen.** The A2 FD family that would produce the real table - D6RF, D6RF3, D6RF7,
D6RF9, D6RF10, D6RF11, D6RF12 - has reached `NOT A RESULT` at every rung this lane opened.

### 1.1 What this item DOES have: a 2-versus-4 rank self-consistency check

| what | value | tag |
|---|---|---|
| instrument | `d6r2c_arm0_gradient_health.py`, md5 `7da73e35a50b146247dd1b214d4e69c8` at freeze, **in the freeze commit** | `REGISTERED` |
| what it compares | every total derivative of `{obj.J, CL_cl04, CL_cl05, CL_cl06}` wrt `{twist, shape}`, 4-rank dump against 2-rank dump | `REGISTERED` |
| tolerance | **1.0e-4 relative**, per component, normalised by `\|\|g4\|\|_inf` for that `(of, wrt)` pair, **registered before the arm ran and before iteration 1 of `O_mp`** | `REGISTERED`, `PREREGISTRATION.md` §7 |
| components compared | **412** | `MEASURED`, `ARM0_VERDICT.json` |
| components below the `1e-12` floor | **0** | `MEASURED`, same file |
| components disagreeing | **27** | `MEASURED`, same file |
| worst relative disagreement | **2.9256121090562716e-04** at `cl04.aero_post.CL\|shape[80]` | `MEASURED`, same file |
| **verdict** | **`GATE FAIL`, by 2.926x against the registered 1.0e-4** | `DERIVED` (worst / tolerance) |
| sign flips among the 27 | **0** - every disagreeing pair has the same sign at 2 and at 4 ranks | `MEASURED`, this lane, from the two dumps |

**THE 27 ARE ENUMERATED BELOW, AND THE FROZEN COMPARATOR PRINTS ONLY 20 OF THEM.**
`d6r2c_arm0_gradient_health.py:208` is `for r in rows[:20]:`, with no line saying the list was
cut. So a reader of the instrument's own output can name 20 of the 27 components it counted.
`MEASURED` by this lane: the printed output carries exactly **20** `MISS` lines beside a verdict
line reading **27**. The seven it does not name are re-derived here by applying the instrument's own
rule (`REL_TOL = 1.0e-4`, scale `= max|g_4rank|` per pair) to the two dumps on disk.

| # | component | 2-rank | 4-rank | rel | named by the comparator |
|---|---|---|---|---|---|
| 1 | `cl04.aero_post.CL\|shape[1]` | -2.006051051379e-02 | -2.003055546751e-02 | 1.132e-04 | yes |
| 2 | `cl04.aero_post.CL\|shape[64]` | +9.599208559201e-02 | +9.593935211406e-02 | 1.993e-04 | yes |
| 3 | `cl04.aero_post.CL\|shape[65]` | +1.008021560845e-01 | +1.007585518079e-01 | 1.648e-04 | yes |
| 4 | `cl04.aero_post.CL\|shape[72]` | +1.166081342325e-01 | +1.165441386613e-01 | 2.419e-04 | yes |
| 5 | `cl04.aero_post.CL\|shape[73]` | +1.208091466540e-01 | +1.207612896829e-01 | 1.809e-04 | yes |
| 6 | `cl04.aero_post.CL\|shape[80]` | -2.322680425500e-01 | -2.321906297541e-01 | **2.926e-04** | yes, the worst |
| 7 | `cl04.aero_post.CL\|shape[81]` | -2.646570547743e-01 | -2.646037584366e-01 | 2.014e-04 | yes |
| 8 | `cl04.aero_post.CL\|shape[88]` | -2.063621765107e-01 | -2.063085726598e-01 | 2.026e-04 | yes |
| 9 | `cl04.aero_post.CL\|shape[89]` | -2.402341964864e-01 | -2.402021817794e-01 | 1.210e-04 | yes |
| 10 | `cl05.aero_post.CL\|shape[4]` | -1.633196481991e-02 | -1.636597219348e-02 | 1.285e-04 | yes |
| 11-19 | `cl06.aero_post.CL\|shape[{1,64,65,72,73,80,81,88,89}]` | identical to rows 1-9 | identical to rows 1-9 | identical to rows 1-9 | yes |
| 20 | `obj.J\|shape[3]` | +5.747728213469e-03 | +5.749936751409e-03 | 1.535e-04 | yes, the last one printed |
| 21 | `obj.J\|shape[5]` | +3.764453568208e-03 | +3.761994916014e-03 | 1.709e-04 | **NO** |
| 22 | `obj.J\|shape[6]` | +2.716405766451e-03 | +2.714684789135e-03 | 1.196e-04 | **NO** |
| 23 | `obj.J\|shape[13]` | +3.488401707681e-03 | +3.486762006807e-03 | 1.140e-04 | **NO** |
| 24 | `obj.J\|shape[64]` | +4.973890290246e-03 | +4.972358179349e-03 | 1.065e-04 | **NO** |
| 25 | `obj.J\|shape[72]` | +5.796033888315e-03 | +5.794357428227e-03 | 1.165e-04 | **NO** |
| 26 | `obj.J\|shape[80]` | -1.262121015774e-02 | -1.261943051690e-02 | 1.237e-04 | **NO** |
| 27 | `obj.J\|twist[4]` | +4.672414120031e-04 | +4.671169492586e-04 | 1.056e-04 | **NO** |

### 1.2 A SECOND FINDING, AND IT IS THE LARGER ONE: THE ARM-0 DUMP'S THREE LIFT GRADIENTS ARE NOT THREE

`MEASURED` by this lane, directly from the two dump files:

- In `ARM0_4R/arm0_totals.json`, `cl04.aero_post.CL|shape`, `cl05.aero_post.CL|shape` and
  `cl06.aero_post.CL|shape` are **bit-identical**, `max|difference| = 0.000e+00` across all 96
  components; the same holds for the three `|twist` vectors.
- In `ARM0_2R/arm0_totals.json`, `cl04` and `cl06` are **bit-identical**, while `cl05` differs
  from both by at most **7.820e-05**.
- **In the optimisation's own history the three ARE distinct.** `O_mp/OptView.hst`, read through
  `d6r2c_sens_figure.py`'s `hst_read`: at the first, middle and last gradient record the three
  `d(CL)/d(dvs.shape)` vectors differ, `max|difference|` **4.932e-03 / 2.135e-03 / 2.901e-03**
  respectively, and `d(CL)/d(dvs.twist)` likewise. The cross-scenario `patchV` blocks are
  identically zero, as they should be, which is the live control that the reader can see both
  identity and difference in the same field.

**What follows, and what does not.**

1. **The `GATE FAIL` stands and is not rescued by this.** The worst disagreement, 2.926e-04, lies in
   a vector that exists in both dumps and does disagree between them. Nothing here makes 27 into 0.
2. **"27 of 412 components" is not 27 of 412 independent derivatives.** `DERIVED` from the
   duplication above: against the 4-rank reference exactly **206 of the 412** compared values are
   distinct (96 `obj.J|shape` + 7 `obj.J|twist` + 96 for the single distinct `CL|shape` vector +
   7 for the single distinct `CL|twist` vector); at 2 ranks **309 of 412** are distinct. Of the 27
   disagreements, **18 are distinct** - rows 1-9 and rows 11-19 above are the same nine numbers
   counted twice.
3. **The mechanism is NOT determined by this lane and is not guessed at here.** The dump code
   (`d6r2c_arm0_gradient_health.py:136-149`) asks OpenMDAO for
   `compute_totals(of=["obj.J","cl04.aero_post.CL","cl05.aero_post.CL","cl06.aero_post.CL"],
   wrt=["twist","shape"])` and writes each returned pair under its own key, so there is no key
   collision in the writer. Why `compute_totals` returned identical arrays for three different
   scenarios in the arm-0 model while the optimiser's own driver did not is **NOT MEASURED** and is
   routed to the `dafoam-supervisor`. **It is not filed anywhere** (rule 7).
4. **It does not touch `G1`-`G5`.** Section 4 gates on the optimiser's termination, the objective
   ratio, the final-design lift misses, the artefacts and the ownership. None of them reads arm 0.

### 1.3 The spot-check table, stated as what it is

| check | what it compares | result | is it a §1 bright-line FD check |
|---|---|---|---|
| arm 0, 2 vs 4 ranks | the same adjoint against itself under a different scotch partition | **`GATE FAIL`**, 2.926x | **no** - decomposition, not accuracy |
| A-2 objective cross-check | `d6r2c_evals.jsonl` `obj.J` against the log's `Jf` | agree to **4.71e-10** against a print ulp of 1e-08 | no |
| `G3` corroboration | the grader's `cl06` miss against IPOPT's own `Constraint violation` | **identical to seventeen digits**, 2.7869956827836218e-03 | no |
| finite differences, baseline | analytic gradient against a central difference at a swept step | **`PENDING`** | this is the check that is absent |
| finite differences, final design | the same at the design `O_mp` ended on | **`PENDING`** | this is the check `DAFOAM_CHARTER.md` §9 names explicitly |

**PetscConvergedReason: 2 appears throughout the adjoint solves in the arm-0 logs and is not
evidence about a derivative.** `DAFOAM_CHARTER.md` §1: it is a statement about a Krylov solve.

Source: `docs/charters/DAFOAM_CHARTER.md` §1, §2, §3, §9;
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/PREREGISTRATION.md` §7, §10;
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_arm0_gradient_health.py` (line 208 for the print
cap, lines 136-149 for the dump);
`cases/dafoam/ladder-a/A2/per_component_table/RESULTS.md`;
run root `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/` -
`ARM0_VERDICT.json`, `ARM0_2R/arm0_totals.json`, `ARM0_4R/arm0_totals.json`,
`O_mp/OptView.hst`, `O_mp_20260913T013230Z_226722.log`.

---

## 2. PARALLELISM-HEALTH LINE

> **`GATE FAIL` by 2.93x on the registered 1.0e-4 tolerance: worst relative disagreement
> 2.926e-04 at `cl04.aero_post.CL|shape[80]`, 27 of 412 compared components disagreeing, 0 of 412
> below the 1e-12 floor, 2 ranks against 4. Proceeding on directive E.**

**This is not a pass and is not reported as one.** The registration's own §7 fixed what a failure
here means before the arm ran: *"An `ARM0` `GATE FAIL` is a finding about the decomposition and is
reported as one; it is not a reason to change the rank count and then re-grade."* No rank count was
changed. The tolerance was registered before arm 0 ran and before iteration 1 of `O_mp`, at
`PREREGISTRATION.md` §7, and the reason for choosing 1.0e-4 rather than bitwise is registered in
the same place: the adjoint is GMRES to `gmresRelTol = 1.0e-6` and the primal to `1.0e-8` on
different partitions, so 1e-4 sits two decades looser than the adjoint's own tolerance and two decades
tighter than the ~1e-2 level at which a missed halo exchange shows up in this family.

**`O_mp` launched anyway.** §7 also registered *"`O_mp` does not launch until `ARM0` reads
`PASS`."* It did not read `PASS`, and `O_mp` ran. The authority for that is Sanaa's directive E,
and this report states the departure rather than letting the parallelism line read as clean.

**Read this line together with section 1.2.** The 412-component count triple-counts one lift-gradient
vector at 4 ranks. The verdict is unaffected; the denominator is not what it looks like.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/ARM0_VERDICT.json`;
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/PREREGISTRATION.md` §7.

---

## 3. CONVERGENCE HISTORY

**The objective is NOT monotone and the table below shows every rise.** The run terminated at its
registered budget of 25 IPOPT major iterations with `EXIT: Maximum Number of Iterations Exceeded.`,
which §1a of the registration named in advance as the expected termination: *"`max_iter = 25` is a
BUDGET ON IPOPT MAJOR ITERATIONS. It is NOT a convergence tolerance and no reader may present a run
that reaches it as converged."* **This run is not converged and is not described as converged.**

All 26 rows, `TRANSCRIBED` from `O_mp/opt_IPOPT.txt`:

| major | objective | inf_pr | inf_du | note |
|---|---|---|---|---|
| 0 | 3.0641631e-02 | 4.21e-08 | 8.13e-03 | `J0` |
| 1 | 3.0631067e-02 | 1.66e-07 | 5.71e-03 | |
| 2 | 2.8625963e-02 | 1.88e-03 | 5.81e-02 | |
| 3 | 2.5132705e-02 | 6.76e-03 | 2.71e-03 | |
| 4 | 2.5680714e-02 | 1.30e-02 | 7.89e-03 | **rise 1 of 2** |
| 5 | 2.8117733e-02 | 2.62e-02 | 6.05e-03 | **rise 2 of 2** |
| 6 | 2.6939703e-02 | 2.26e-02 | 3.42e-03 | falls again |
| 7 | 2.4976239e-02 | 4.49e-03 | 6.85e-04 | |
| 8 | 2.4567002e-02 | 2.44e-03 | 1.93e-03 | |
| 9 | 2.7605615e-02 | 1.39e-03 | 3.39e-03 | **rise, single** |
| 10 | 2.4603956e-02 | 5.04e-03 | 1.28e-03 | |
| 11 | 2.3534713e-02 | 6.65e-03 | 4.63e-04 | |
| 12 | 2.3260046e-02 | 3.87e-03 | 2.94e-04 | |
| 13 | 2.3000825e-02 | 3.37e-04 | 3.75e-04 | |
| 14 | 2.2960209e-02 | 3.20e-04 | 5.15e-04 | |
| 15 | 2.2934928e-02 | 3.13e-04 | 3.77e-04 | |
| 16 | 2.2906979e-02 | 3.13e-04 | 2.58e-04 | |
| 17 | **2.2906456e-02** | **3.13e-04** | 3.40e-04 | **BEST objective of the run** |
| 18 | 2.4699992e-02 | 3.91e-04 | 3.50e-03 | **rise 1 of 2** |
| 19 | 2.6955134e-02 | 3.95e-04 | 5.41e-03 | **rise 2 of 2** |
| 20 | 2.4312158e-02 | 3.26e-03 | 4.33e-03 | falls again |
| 21 | 2.3571003e-02 | 3.33e-03 | 2.79e-03 | |
| 22 | 2.3231549e-02 | 3.03e-03 | 2.56e-03 | |
| 23 | 2.3105276e-02 | 2.85e-03 | 2.33e-03 | |
| 24 | 2.3077470e-02 | 2.81e-03 | 2.26e-03 | |
| 25 | **2.3063260e-02** | **2.79e-03** | 2.23e-03 | **FINAL, and `Jf` for `G2`** |

**`G2` GRADES THE FINAL, NOT THE BEST, AND BOTH ARE GIVEN HERE.**

| | value | reduction against `J0` | tag |
|---|---|---|---|
| `J0`, major 0 | 0.03064163 | - | `MEASURED`, log line 11568 |
| best, major **17** | 0.022906456 | **25.244 %** | `MEASURED`, `opt_IPOPT.txt` |
| **final, major 25** | **0.02306326** | **24.732 %** | `MEASURED`, log line 54198 |
| `G2` threshold `0.90 x J0` | 0.027577467 | 10 % | `REGISTERED`, §4 |
| `G2` margin `Jf - threshold` | **-4.514207e-03** | | `DERIVED` |

The final objective sits **0.685 % above** the best the run reached. `G2` is graded on the final and
passes with 14.7 percentage points of room over the registered 10 % bar.

**AN OBSERVATION ABOUT MAJOR 17, AND IT IS NOT A RE-GRADE AND CHANGES NOTHING.** At major 17 the
worst constraint violation over all constraints was **3.13e-04**. `G3`'s registered tolerance is
**1.0e-3** on the lift misses, and the lift misses are bounded above by `inf_pr`. So the iterate at
major 17 would have satisfied `G3`, and its objective would have satisfied `G2` more comfortably
than the final one does. **Section 4 registers the FINAL design and nothing else** - *"`G3` — THE
LIFT CONSTRAINTS ARE HELD AT THE FINAL DESIGN"* - and rule 2 closes the gates at first compute.
**Picking major 17 after seeing the answer is exactly the move pre-registration exists to prevent, and
it is not made here.** The fact is recorded because a reader is entitled to know the trajectory passed
through a point that would have graded differently, and because it is the strongest available argument
for the successor item to buy more majors rather than to re-read this one.

**SANAA'S ITEM-7 STOP RULE 1, CHECKED AGAINST THE REGISTERED SOURCE.** The rule fires on the
objective rising **three consecutive majors**. `MEASURED` by this lane from the table above: the
longest run of consecutive rises is **two**, and it occurs twice, at majors 3-4-5 and at majors
17-18-19. The rule's condition was never met on IPOPT's own table. **This does not retire ADDENDUM 3
§A3.5's disclosure that the registered monitor never ran** - no `D6R2C_MONITOR.jsonl` exists, and
nothing watched this run live. It is an after-the-fact check of the same condition from the same
artefact the monitor would have read, and it agrees with the supervisor's ruling that item 7 did not
fire.

**THE FIGURE'S x AXIS IS NOT IPOPT'S MAJOR COUNTER, AND THE FIGURE NOW SAYS SO.** The convergence
figure is drawn from `OptView.hst` records carrying `isMajor=True`, of which there are **87**,
indexed 0..86. IPOPT's own table has **26** rows, 0..25. The reader's default axis label was
"major iteration", which reads as IPOPT's; under `--figure-standard` it now reads
"pyoptsparse history record, isMajor". **The table above, not the figure, is the authoritative
convergence history**, because §4 registers the log and `opt_IPOPT.txt` as the sources.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp/opt_IPOPT.txt`;
`O_mp_GRADE.json` (`gates_physics.G2`); `PREREGISTRATION.md` §1a, §4, §6, ADDENDUM 3 §A3.5.

---

## 4. DECOMPOSITION TABLE (Sanaa's After-item 8)

**PENDING: /home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh/ (arm `DEC`)**

Her item 8, verbatim: *"Decomposition, two extra solves at matched lift: twist-only re-trimmed, and
the full optimum; table shows shape vs twist vs trim contributions before any percentage is quoted."*

**The solves have not run and the run root does not exist.** `MEASURED` twice, and the two readings
differ, so both are given rather than the later one alone. At **2026-09-13T04:52:36Z** this lane
listed `cases/dafoam/ladder-a/A2/curriculum_D6R2C/` and `cases/dafoam/ladder-a/A2/` and found **no
registration**. At **2026-09-13T05:00:35Z**, re-checking before this line was written, the peer lane's
`PREREGISTRATION_AFTER_ITEMS.md` **is** on disk, **version 1.0, DRAFT, NOT YET FROZEN**, declaring
*"0 core-min, 0 containers and 0 meshes at the time of writing"*, with arm `DEC` running the five
decomposition states `B -> T -> S -> F -> O` in one container at 4 ranks into the new run root named
above. **The verdict path within that root is a `--out` argument of `d6r2c_after_grade.py` and is
not fixed by the registration, so the root and the arm are named and no filename is invented.**

**The token above is `REPORTING_CHARTER.md` §2 rule 5's and means the artefact could not be read**,
which is still true: a registration that has not been committed has not frozen anything, and no
container has started.

**Nothing is estimated in its place.** In particular, **the shape, twist and trim shares of the
24.732 % weighted drag reduction are NOT computed anywhere in this report**, and the per-condition
table in section 6 is a before/after split by flight condition, which is a different decomposition
and is not a substitute for hers.

**This is not a gate and does not qualify the `GATE FAIL`.** `PENDING` here means two solves have
not been bought.

Source: `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md` line 21;
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/PREREGISTRATION_AFTER_ITEMS.md` (draft, uncommitted at
the stamp above); directory listings at both stamps above.

---

## 5. FRESH-MESH CONFIRMATION (Sanaa's After-item 9)

**PENDING: /home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh/ (arm `FM`)**

Her item 9, verbatim: *"Fresh mesh on the final shape from the family script, re-solve at every
condition, confirm the weighted drag within band of the deformed-mesh value."*

**No fresh mesh has been generated and no re-solve has run.** Arm `FM` in the same draft
registration covers it at 4 ranks, with a third arm `FM_L2` at one further `cgns_utils coarsen`
level registered as **reported, never gated, no triple, no GCI, no observed order**. **The band is
in that registration and this lane does not quote it**, for the reason the registration itself is
built around: a band this report reproduced could be read as this report's, and a band quoted after
the comparison is not a band. **Nothing here reserves a result for it.**

**What this section will be able to say when it runs, and what it cannot say now.** Every drag number
in this report comes from the **deformed** mesh - the baseline mesh warped by IDWarp under the FFD
displacements, 25 majors of warping deep. Section 11 records four `checkMesh` aspect-ratio trips on
that deformed mesh. **Until item 9 runs, the lab does not know how much of the 24.732 % survives
re-meshing**, and this report does not guess.

Source: `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md` line 22;
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/PREREGISTRATION_AFTER_ITEMS.md` (draft, uncommitted at
the stamp in section 4).

---

## 6. PER-CONDITION DRAG AND LIFT, BEFORE AND AFTER

**The weights are Sanaa's and are stated before any number: `w = (0.25, 0.50, 0.25)` on
`(cl04, cl05, cl06)`, and `J = 0.25*CD04 + 0.50*CD05 + 0.25*CD06`.** `REGISTERED`,
`PREREGISTRATION.md` §1.

**HOW THE PER-CONDITION DRAG WAS OBTAINED, BECAUSE IT IS NOT IN THE DRIVER RECORD.**
`MEASURED` by this lane: the `kind == "F"` records of `d6r2c_evals.jsonl` carry exactly six
function keys - the three `CL`s, `thickcon`, `volcon` and `obj.J`. **The three per-condition
`CD` values are not recorded anywhere by the production chain.** They exist only as the solver's own
per-primal print in the arm log, and **the log carries no scenario label on those lines.**
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_percondition_table.py` therefore attributes each
primal to a condition **by a measured quantity and never by assumed ordering**: a window of three
consecutive primal blocks is accepted only if its three converged `CL`s match the three the driver
recorded for that evaluation to `1e-8`, **and** its weighted drag sum reproduces that evaluation's
recorded `obj.J`. **That second clause is the whole evidence**: three drag coefficients that
reproduce the registered objective are the three the objective was built from.

- **Corroboration, before design:** `|J_reconstructed - J_recorded|` = **1.002e-12** at the baseline
  and **1.322e-12** at the final design, against a matching tolerance of 1e-8. Four decades of margin.
- **Planted control (rule 3):** `--selftest` perturbs each reconstructed `CD` in turn by
  `PLANT = 1.234e-03` and requires the corroboration to reject it. **`D6R2C_PERCOND SELFTEST PASS
  n=8`** - 2 value-unique windows and 6 planted rejections, exit 0. A reader that could not see a
  perturbation of that size could not certify the agreement above.

### 6.1 Drag, per condition

| condition | CL target | `CD` before | `CD` after | change | reduction | share of the weighted drop |
|---|---|---|---|---|---|---|
| `cl04` | 0.4 | 0.02244233877 | 0.01925971927 | -0.00318262 | **14.181 %** | 10.499 % |
| `cl05` | 0.5 | 0.02961980803 | 0.02259468495 | -0.00702512 | **23.718 %** | 46.350 % |
| `cl06` | 0.6 | 0.04088457093 | 0.02780394895 | -0.01308062 | **31.994 %** | 43.151 % |
| **weighted `J`** | | **0.030641631440** | **0.023063259530** | -0.007578372 | **24.732 %** | 100 % |

All six `CD` values `MEASURED` from `O_mp_20260913T013230Z_226722.log` at 10 significant digits;
the weighted row `DERIVED` from them at the registered weights and agreeing with the grader's
independently computed `reduction_percent` of **24.73226783301019 %**.

**The per-condition numbers are the honest content and the single weighted figure hides them.** The
optimiser bought most of its improvement at the two higher-lift conditions: `cl06` alone drops
32.0 % of its drag, `cl04` only 14.2 %. **`cl05` carries double weight**, so its 23.7 % is 46.4 %
of the weighted drop while `cl06`'s larger 32.0 % contributes 43.2 %. A reader given only
"24.7 % drag reduction" would not know that the low-lift condition improved least.

### 6.2 Lift, per condition, with the miss that decides `G3`

| condition | target | `CL` before | miss before | `CL` after | **miss after** | against 1.0e-3 |
|---|---|---|---|---|---|---|
| `cl04` | 0.4 | 0.4000000002 | 2.0e-10 | 0.399446101576034 | **5.539e-04** | inside |
| `cl05` | 0.5 | 0.5000000000 | 0.0 | 0.498790141539629 | **1.210e-03** | **outside, 1.21x** |
| `cl06` | 0.6 | 0.5999999579 | 4.2e-08 | 0.597213004317216 | **2.787e-03** | **outside, 2.79x** |

`CL` after and the misses are `MEASURED`, quoted from `O_mp_GRADE.json` `gates_physics.G3` at
full precision; `CL` before is `MEASURED` from the log at its print precision.

**This table is the `GATE FAIL`.** The baseline satisfied all three lift equalities to 4.2e-08,
because `findFeasibleDesign` trimmed it there before iteration 1. Twenty-five majors later, two of
three are outside the registered band, and the worst is 2.79x over it. **The optimiser traded lift
accuracy for drag and ran out of majors before it traded it back**; the constraint violation was still
falling at major 25 (2.85e-03, 2.81e-03, 2.79e-03 over majors 23, 24, 25).

**The seventeen-digit corroboration.** IPOPT's own summary reads
`Constraint violation....: 2.7869956827836218e-03`. The grader's `cl06` miss, computed from
`d6r2c_evals.jsonl` by a wholly separate code path, is `0.0027869956827836218`. **Identical to the
last digit**, and the `dafoam-supervisor` recomputed it by a third path to the same value. Two
instruments sharing no code agree, which makes the miss a property of the run rather than of the
reading the grader took for ambiguity A-2.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/` -
`O_mp_20260913T013230Z_226722.log`, `O_mp/d6r2c_evals.jsonl`, `O_mp/opt_IPOPT.txt`,
`O_mp_GRADE.json`; instrument
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_percondition_table.py`;
`PREREGISTRATION.md` §1, §4.

---

## 7. THE FIVE GATES AS GRADED

| gate | result | the numbers | tag |
|---|---|---|---|
| `G1` optimiser terminated at its registered budget | **PASS** | `rc = 0`; `Number of Iterations....: 25`; exactly one `EXIT:` line and it is the registered `EXIT: Maximum Number of Iterations Exceeded.` | `MEASURED` |
| `G2` weighted drag reduction `>= 10 %` | **PASS** | `J0` 0.03064163, `Jf` 0.02306326, ratio 0.7526773216698981, **24.732 %**, margin -4.514207e-03, print resolution 1e-08 | `MEASURED` |
| `G3` lift held at the final design, `<= 1.0e-3` | **MISS** | worst **2.787e-03** at `cl06`, **2.79x** over; `cl05` 1.210e-03; `cl04` 5.539e-04 | `MEASURED` |
| `G4` results saved and they are this run's | **PASS** | four artefacts present and strictly newer than the age datum; time `1000` in **all twelve** `mp0{4,5,6}/processor{0..3}`, 15 files each, **zero** entries not newer | `MEASURED` |
| `G5` it ran as ubuntu | **PASS** | **7,291** entries scanned, **zero** owned by uid 0 or gid 0 and newer than the datum | `MEASURED` |
| cap | **not crossed** | 672.933 core-min against 2359.5, margin **-1686.567**; no `D6R2C_CAP_CROSSED arm=O_mp` row in the ledger | `MEASURED` |

**Label rule, unchanged from §4:** `GATE FAIL` = `G1` and `G4` and `G5` hold and `G2` or
`G3` misses. **`GATE FAIL`.**

**THE AMBIGUITIES THE GRADER REFUSED TO RESOLVE ARE CARRIED, NOT DROPPED.**
`O_mp_GRADE.json` `ambiguities_not_resolved` lists four: A-1 which printed `obj.J` form `G2`
means; A-2 which record is the final design for `G3`; A-3 what "field data" enumerates for `G4`;
A-4 the log's printed precision floors `G2`.

**A-1 was ruled by the `dafoam-supervisor` on 2026-09-13: grade on the dictionary form.** The
alternative reading is preserved in the grade record as `g2_alternative_reading` and is reproduced
here so a later reader can disagree on the evidence: the pyOptSparse summary-table rows give
`J0 = 0.0` (log line 11945, printed `0.000000E+00`) and `Jf = 0.02306326` (log line 53221), a
ratio of `null`, and `G2` **false** under that reading. The ruling's ground is that the
table-form's pre-solve row is an uninitialised slot and a reading that puts a zero in the denominator
of `Jf <= 0.90 x J0` cannot be the one §4 intends. **Reported, not graded.**

**THE DISCLOSURE THAT TRAVELS WITH THIS VERDICT PERMANENTLY.** `d6r2c_grade.py`, the instrument §4
names, **did not exist at the freeze** - absent from the working tree, from every tree in this
repository's git history, from §11's frozen-instrument table and from ADDENDUM 1's updated table. **The
grading path for `G1`-`G5` was NOT fixed at the pre-registration commit**, which rule 2 requires,
although it WAS fixed for the kill-and-resume proof and for arm 0. The grader was written on
2026-09-13 while `O_mp` was at iteration 23 of 25 and finished after it exited, md5
`ca159f6cee00c3e571195b44d2967659`. Every threshold, literal, comparison direction and label was
copied verbatim from the frozen §4, each constant carrying the sentence it was copied from; 43 planted
controls passed, including one that plants a real uid-0 file; and the supervisor read the instrument
as a diff before any of its output was believed, which caught a defect one evaluation away from
manufacturing a `GATE FAIL` out of NaN arithmetic. **None of that repairs the rule-2 defect and
this report does not offer it as a repair.** A reader is entitled to weigh this verdict below one
produced by a frozen path.

**The registered stop-rule monitor never ran.** No `D6R2C_MONITOR.jsonl` exists anywhere on this
box and the string `d6r2c_monitor` appears in no launcher, chain or script. §6 was unsatisfied for
this run.

Source: `O_mp_GRADE.json`; `PREREGISTRATION.md` §4, §6, §11, ADDENDUM 3 §A3.1-§A3.5, §A3.7.

---

## 8. SECTIONS AND SKIN-SENSITIVITY FIGURES

### 8.1 What was produced, and where

**Sensitivity and convergence figures**, rendered for this report at
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/D6R2C-REPORT-FIGURES-20260913T044526Z/`:

| file | what it shows |
|---|---|
| `D6R2C_O_mp_sens_ffd_lattice_dJdshape.png` | `dJ/d(shape)` on the 96 FFD control points, lower and upper sheets, plus all 96 by index |
| `D6R2C_O_mp_sens_twist_dJdtwist.png` | `dJ/d(twist)` on the seven free twist stations |
| `D6R2C_O_mp_convergence_history.png` | objective and worst constraint violation against the history's `isMajor` index |
| `D6R2C_O_mp_sens_report.json` | the numbers behind all three, with the planted-control verdict |
| `D6R2C_O_mp_sheet_text.json` | the explanatory text moved off the images by the figure standard |

**Planted control (rule 3): `PLANTED CONTROL PASSED`.** The reader renders once, writes a perturbed
copy of the history to disk, re-reads that copy **through the same code path**, re-renders, and
compares both the PNG bytes and the numeric summary; it exits 2 rather than certify a figure it cannot
see its own input in.

**Field and geometry images**, 18 of them, produced by the completion hook at
`.../D6R2C-RENDER-COPY-20260913T041628Z/png/` with sidecar `D6R2C_RENDER_SIDECAR.json`: for each of
`mp04`, `mp05`, `mp06`, a `Cp` spanwise-section slice, a `Cp` wing surface, a local-Mach
spanwise-section slice, a local-Mach wing surface, the mesh on the wing, and the optimised shape.
`MEASURED`: 18 files on disk, matching the sidecar's `images_total`.

### 8.2 THE HEADLINE NUMBER FROM THE SENSITIVITY FIGURE, AND THE THING IT IS NOT

`max |dJ/d(shape)| = 1.239597e-03`, signed **-1.239597e-03**, at design variable **84**, which maps
to FFD `(i=5 chordwise, j=0 lower sheet, k=4 spanwise)` at `x = 7.7203 m`, `z = 9.1036 m`.
`MEASURED`, from `O_mp/OptView.hst` record 173. **Values are as RECORDED, in the optimiser's
driver-scaled space**; `add_design_var` scaler is 10.0 for `shape`, so
`dJ/d(physical FFD displacement) = 10 x` the plotted value. The reader reports the recorded value as
primary and the physical value as an explicitly derived column; it never silently multiplies.

**IT IS A LATTICE SENSITIVITY AND NOT A SKIN MAP, AND THE DIFFERENCE IS NOT COSMETIC.** Sanaa's item
10 asks for a "skin-sensitivity figure". **The production chain writes no `sensMap`, no
`writeSens` and no `writeDeformedFFD`**, so `dI/dx` as a surface field is never produced.
Mapping the 96 lattice numbers onto the wing skin needs the DVGeo B-spline Jacobian
`dXsurface/dXffd`, which is not on disk. **A smooth skin map drawn here would be an interpolation
nobody registered**, so the reader draws the sensitivity where it honestly lives, on the FFD control
lattice at the lattice's true planform coordinates, and refuses to draw the other. The mapping from DV
index to FFD index is not assumed either: `--verify-mapping` re-derives it from the sign structure of
`d(thickcon)/d(shape)`, which is non-negative for every `j=1` control point and non-positive for
every `j=0` point, and refuses if that fails.

### 8.3 THE FIGURE STANDARD, AND WHERE THESE FIGURES MEET IT AND WHERE THEY DO NOT

The standard is Sanaa's, captured verbatim at
`etc/sessions/2026-09-01T0310Z_sanaa_actA_figure_header_standard.md` (commit `569346b3`), and it
applies to every act: *"Figures carry no paragraphs. Each figure has: a title of at most 10 words,
axis labels with units, a colour bar with numeric ticks and the unit only, a legend inside the axes,
and one caption line of at most 20 words. Every explanation currently printed inside a figure ... moves
to the sheet text as a single compact paragraph per figure. No capitalised phrases ... no
meta-commentary about the figure itself."*

**What was changed to meet it.** `d6r2c_sens_figure.py` gained a `--figure-standard` flag. The
multi-line monospace footers, which were five, four and five lines, are replaced by one caption line
each, and the text they carried is **moved, not deleted**, to `D6R2C_O_mp_sheet_text.json` and
reproduced in section 8.2 above as this report's sheet text. The flag refuses (exit 2) if a caption
exceeds 20 words. The captions now read, at 11, 12 and 13 words:

- *"Objective sensitivity on the 96 FFD control points, not on the wing skin."*
- *"Objective sensitivity to the seven free twist stations; the root station is fixed."*
- *"Objective and worst constraint violation, read from the optimiser history on disk."*

**RESIDUAL DEPARTURES, DISCLOSED RATHER THAN CLAIMED AWAY.** `MEASURED` by reading the images:

1. The lattice figure's two subplot titles still read `LOWER sheet (FFD j=0)` and
   `UPPER sheet (FFD j=1)`, which carry capitalised words the standard bars.
2. The lattice figure's lower-panel x-axis label carries the index-mapping formula
   `DV n -> FFD i=n//16, j=(n%16)//8, k=n%8`, which is explanatory text on the image.
3. **The 18 ParaView renders carry NO title and NO caption line at all.** They have a colour bar with
   numeric ticks and the quantity, which the standard asks for, and nothing else. **They do not meet
   the title clause or the caption clause**, and this report does not claim they do. The render script
   `d6r2c_render.py` contains no reference to the figure standard.
4. The convergence figure's axes carry no units, because the objective is a drag coefficient and the
   abscissa is an iteration index; neither has one. Stated rather than left as an unexplained absence.

**A NOTE ON WHAT THE FIELD FIGURES CAN AND CANNOT SHOW.** `M_inf = 0.288` and the measured maximum
local Mach on a completed state is **0.380**. **There is no shock and no figure here draws one at any
contour level.** A demo that advertised a transonic wing optimisation and showed this case would be
advertising something these artefacts cannot support.

### 8.4 No figure script failed

Both the sensitivity reader and the completion-hook render ran to a clean product: the reader printed
`D6R2C SENS OK` with `PLANTED CONTROL PASSED` and exited 0; the render wrote 18 of 18 images. **The
render wrapper's own exit code is not the success criterion and its sidecar says why**: pvbatch exits
1 under xvfb on a `GLXBadContext` during GL teardown, after every image is written and after its own
report prints `errors=0`, so success is judged by images counted on disk. `MEASURED`: 18 on disk.

Source: figure directory
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/D6R2C-REPORT-FIGURES-20260913T044526Z/`
(`D6R2C_O_mp_sens_report.json`, `D6R2C_O_mp_sheet_text.json`); render copy
`.../D6R2C-RENDER-COPY-20260913T041628Z/` (`D6R2C_RENDER_SIDECAR.json`, `png/`);
instrument `cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_sens_figure.py`;
standard `etc/sessions/2026-09-01T0310Z_sanaa_actA_figure_header_standard.md`.

---

## 9. COMPUTE TABLE

### 9.1 Ranks, core-minutes, wall

| arm | ranks | wall s | core-min | cost ranks | registered cap | crossed | rc |
|---|---|---|---|---|---|---|---|
| `KR_REF` | 4 | 4,073 | 271.533 | 4 | 420.0 | no | 0 |
| `KR_KILL` | 4 | 3,595 | 239.667 | 4 | 234.0 | **yes, reported** | 137 (SIGKILL by design) |
| `KR_RES` (first) | 4 | 21 | 1.400 | 4 | 420.0 | no | 73 (guard refusal) |
| `KR_RES` | 4 | 2,305 | 153.667 | 4 | 420.0 | no | 0 |
| `KR_REF2` | 4 | 388 | 25.867 | 4 | 420.0 | no | 137 |
| `ARM0_4R` | 4 | 2,013 | 134.200 | 4 | 45.0 | **yes, reported** | 0 |
| `ARM0_2R` | 4 | 2,867 | 95.567 | **2** | 60.0 | **yes, reported** | 0 |
| `ARM0_4R` (rerun) | 4 | 31 | 2.067 | 4 | 45.0 | no | 1 |
| `ARM0_2R` (rerun) | 4 | 11 | 0.367 | 2 | 60.0 | no | 1 |
| `ARM0_4R` (final) | 4 | 1,984 | 132.267 | 4 | 45.0 | **yes, reported** | 0 |
| `ARM0_2R` (final) | 4 | 3,014 | 100.467 | 2 | 60.0 | **yes, reported** | 0 |
| **`O_mp`** | **4** | **10,094** | **672.933** | **4** | **2359.5** | **no** | **0** |

All rows `MEASURED`, `TRANSCRIBED` from
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/ledger.txt`,
which the launcher wrote at each container exit (`d6r2c_run_arm.sh:372`).
`core_min = wall_s x cost_ranks / 60`. **Every cap crossing above was REPORTED and no cap was ever
raised**, per `PREREGISTRATION.md` §8 read with Sanaa's directive #17; the ledger rows read
`action=REPORTED_RUN_CONTINUES_NOT_A_RESULT_AND_CAP_NEVER_RAISED`.

`O_mp` wall 10,094 s = **2.804 h**. **Placement, `REGISTERED` at §9:** `RANKS = 4`,
`CPUSET = 2,3,4,5`, `--memory=20g --memory-swap=20g`, declared `memory_footprint_gb = 17`.
`MemAvailable` at launch **669.81 GiB**, `load1` **27.90**, swap in use **0 kB**.

**MESH DECOMPOSITION - this is the rank decomposition and it is NOT Sanaa's item 8.** Section 4 above
is item 8 and is `PENDING`. `MEASURED` from the arm log, scotch on 4 ranks:

| processor | cells | points | processor faces |
|---|---|---|---|
| 0 | 9,504 | 10,868 | 1,320 |
| 1 | 9,600 | 10,563 | 1,360 |
| 2 | 9,608 | 10,613 | 1,360 |
| 3 | 9,592 | 11,044 | 1,496 |
| **total** | **38,304** | | 2,768 shared |

**THIS CORRECTS THE FROZEN REGISTRATION, AND THE CORRECTION IS NOT SMALL.** `PREREGISTRATION.md` §1
records the mesh as *"9,504 cells, single grid"*. **9,504 is processor 0's share under a 4-way scotch
decomposition, not the mesh.** `MEASURED` by two independent sources in this lane's own hands: the
log's decomposition table sums to 9504 + 9600 + 9608 + 9592 = **38,304**, and the mesh's own
`base/constant/polyMesh/owner` header reads
`note "nPoints:40209  nCells:38304  nFaces:116756  nInternalFaces:113068"`. **The registration's
figure is low by a factor of four.** The landed cost-calibration row
`C-20260913T043733.251556Z-17681dfe` repeats the 9,504 figure and inherits the error.
**No gate reads the cell count**, so nothing is re-graded; **the frozen file is not edited by this
lane** (rule 6) and the repair, if any, is a dated addendum for its author. The correct figure for
every downstream use is **38,304 cells**.

### 9.2 Estimate against actual (rule 12)

| | value | tag |
|---|---|---|
| predicted, frozen **before any container started** | **786.5 core-min** | `REGISTERED`, §8 at `7f685867d` |
| basis of the prediction | 25 majors x **31.258 core-min/major** (C-188, `8262f123`) = 781.5, + 5 preamble | `REGISTERED` over a `MEASURED` anchor |
| **actual** | **672.933 core-min** | `MEASURED`, ledger `ARM=O_mp` |
| **ratio actual/predicted** | **0.856** | `DERIVED` |
| measured per-major cost | **26.917 core-min** against the 31.258 anchor, ratio **0.861** | `DERIVED` |
| predicted dollars | **$0.672** | `DERIVED`, never measured |
| actual dollars | **$0.575** | `DERIVED`, never measured |

**Dollars are DERIVED and are not a measurement.** The rate is $0.0513/core-h on a c7a.4xlarge,
**reported-by-owner**; this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). The box
is now an r7a.4xlarge and the rate on record is the c7a.4xlarge figure, used unchanged rather than
invented, and that substitution was named in §8 of the registration rather than buried.

**Attribution: MISPREDICTION, in the conservative direction.** The estimate was 16.9 % high; the
majors came in cheaper than the anchor that set them. **CONTENTION: NOT MEASURED for this arm**, and
that is stated as absent rather than approximated - the launcher wrote no `delivered_cores_mean` for
`O_mp`, and `load1_pre = 27.90` is a pre-launch reading on a 96-core host, not a delivered-core
measurement.

**WASTE, NAMED SEPARATELY AND NEVER ABSORBED INTO THE RATIO (`COMPUTE_BUDGET_CHARTER.md` §6):
51.955 core-min, 7.72 % of the run**, on the **52 of 87** `kind == "F"` evaluations that returned
`fail = 1`, summed from their own `eval_wall_s` fields x 4 ranks / 60. `MEASURED`. **Honest
caveat so the figure is not over-read:** these are not waste in the optimiser's sense, because IPOPT
consumed each failure to cut its step. They are named because §6 requires waste to be named, and
because the next estimate for this family must know the fraction.

**GROSS OR CLEANED: cleaned equals gross, and the reason is given rather than assumed.** The run is
one ledger row of 10,094 wall s, which does exceed the charter §2 3,600-s threshold; that threshold
identifies a **stalled** row and this row is not one. Evidence of progress throughout: 88 function and
26 gradient evaluations recorded with the last at `wall_since_start_s = 9799.634`, checkpoint rows in
the ledger at the registered 1,800-s cadence through 04:02:32Z, and IPOPT reaching iteration 25. **No
core-minute is deducted on that basis.**

**ACCOUNTING RESIDUE, STATED AND NOT APPROXIMATED.** The 87 `F` evaluations account for 166.145
core-min and the 26 `G` evaluations for 303.320, together **469.465** of the 672.933. The remaining
**203.468 core-min** is container preamble, mesh warping, IPOPT internals, checkpoint rotation and the
final field write, **which this run did not instrument separately**. No attribution is offered for it.

**The calibration row is landed**, at `docs/COST_CALIBRATION.md` row
`C-20260913T043733.251556Z-17681dfe`, under that file's append rules and the rule-10 private-index
protocol.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/ledger.txt`,
`O_mp_20260913T013230Z_226722.log`, `O_mp/d6r2c_evals.jsonl`,
`base/constant/polyMesh/owner`; `PREREGISTRATION.md` §1, §8, §9;
`docs/COST_CALIBRATION.md` row `C-20260913T043733.251556Z-17681dfe`;
`docs/charters/COMPUTE_BUDGET_CHARTER.md` §5, §6.

---

## 10. CERTIFICATE SLOT

**Honest, in Sanaa's own words for this slot: single grid, band pending.**

| field | entry |
|---|---|
| what is certified | **nothing is certified by this item** |
| grid family | **none. One mesh, 38,304 cells, three scenarios sharing it.** |
| Roache triple | **none.** §4 of the registration: *"A Roache triple is NOT claimed and no GCI is quoted."* |
| observed order | **not computed, and rule 5 does not apply** - there is no triple to gate |
| GCI | **not quoted.** Quoting one from a single grid would be a fabricated label |
| discretisation band | **PENDING** - it needs the grid family this item deliberately did not buy |
| fresh-mesh band | **PENDING** - Sanaa's item 9, section 5 above, not yet registered |
| finite-difference table | **PENDING** - section 1; the `DAFOAM_CHARTER.md` §1 bright line is not met |
| parallelism health | **`GATE FAIL`**, 2.926x, section 2 |
| verdict | **`GATE FAIL`** by 2.79x on `G3` |
| grading-path integrity | **DEFECTIVE and disclosed** - the production grader was written after the run produced data; rule 2 not met for `G1`-`G5` |
| stop-rule monitoring | **not performed** - the registered monitor was never invoked |

**What this item is entitled to claim, in one sentence.** *On a single 38,304-cell mesh, a 25-major
IPOPT optimisation of a compressible-subsonic wing at three lift conditions reduced the weighted mean
drag coefficient by 24.732 % and did not hold two of its three lift equality constraints to the
registered 1.0e-3, terminating at its iteration budget rather than at a tolerance.*

**What it is NOT entitled to claim.** That the answer is grid-converged; that the gradient driving it
is verified; that the drag reduction survives re-meshing; that the shape, twist and trim shares of it
are known; that the optimiser converged. **`DAFOAM_CHARTER.md` §9 also holds: an optimiser stopped
by an iteration cap is never `PASS`.** It is not `PASS` here, and the reason is `G3`, not the
cap.

Source: `PREREGISTRATION.md` §4, §10; `docs/charters/DAFOAM_CHARTER.md` §1, §9;
`docs/charters/VERIFICATION_CHARTER.md` §2.

---

## 11. WHAT THE FAILED EVALUATIONS WERE, AND THE MESH TRIPS

**52 of 87 `kind == "F"` evaluations returned `fail = 1`.** They appear here rather than being
hidden. **26 of 26 `kind == "G"` gradient evaluations returned `fail = 0`.**

**They are NOT the D6/D6R NaN signature §6 was written against.** The mechanism, `MEASURED` except
where marked:

- **The fail threshold is `1.0e-5`**, arithmetic on this registration's own frozen constants:
  `primalMinResTol = 1.0e-8` x `primalMinResTolDiff = 1e3` (`d6r2c_opt_runScript.py:126-127`).
- **48 `Primal min residual` blocks appear in the arm log and all 48 are failures.** Minimum failed
  residual **1.000005615e-05**, maximum **7.312316479e-05**. The minimum sits about six parts in ten
  million above the threshold: **these are primals that missed the bar by rounding, not primals that
  diverged.**
- **The partition has zero overlap**: the largest non-failed residual is **9.985532e-06**, below the
  smallest failed one. **`BORROWED`, chain depth 1: this figure is the `dafoam-supervisor`'s
  measurement, relayed.** This lane confirmed the value occurs in the log as a converged primal's
  `p` initial residual but **did not independently reproduce it as the maximum over the non-failed
  partition**, and does not present it as its own.
- **The NaN in the ledger is a driver-level encoding of one fail flag**, not a solver NaN, proved by
  the geometric constraints also reading NaN on the same record.

**MESH-QUALITY TRIPS: FOUR, NOT ONE, AND THE WORST IS NOT THE ONE ON RECORD.** ADDENDUM 3 §A3.6
records *"`High aspect ratio cells found, Max aspect ratio: 1026.908433, number of cells 1` — one
cell ... **Measured by this lane** (one occurrence in the log)."* `MEASURED` by this lane, in this
invocation: the message occurs **four** times in `O_mp_20260913T013230Z_226722.log`, at maximum
aspect ratios **1050.3162**, **1007.373135**, **1026.908433** and **1049.209899**, each on **one**
cell. The value 1026.908433 does occur exactly once, which is presumably how the count arose, but it
is the **third** of four and **not the worst**. The worst deformed-mesh aspect ratio this run produced
is **1050.3162**. The undeformed base mesh reports `Max aspect ratio = 684.4022128 OK` against
`checkMesh`'s own 1000 reporting threshold. Worst non-orthogonality over the run: **80.90429398**,
against **66.96543422** on the base mesh.

**No gate moves on any of this.** Section 4 does not gate on evaluation failures, residuals or mesh
quality, and this section adds no gate that does. **The frozen addendum is not edited by this lane**
(rule 6); the correction is recorded here and routed to its author.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp_20260913T013230Z_226722.log`,
`O_mp/d6r2c_evals.jsonl`; `cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_opt_runScript.py:126-127`;
`PREREGISTRATION.md` ADDENDUM 3 §A3.6.

---

## 12. OPEN FINDINGS THIS REPORT RAISES

Each is a finding, not a gate. None changes the `GATE FAIL`. **None is filed anywhere** (rule 7).

| # | finding | where | effect on the verdict |
|---|---|---|---|
| 1 | **No FD table exists for this item at any design point**; `DAFOAM_CHARTER.md` §1 and §9 are unmet | §1 | none; the charter gap is disclosed, not waived |
| 2 | **The arm-0 dump's three `d(CL)/d(shape)` vectors are bit-identical at 4 ranks** and two of three at 2 ranks, while the optimiser's own history has them distinct; mechanism `NOT MEASURED` | §1.2 | none; the `GATE FAIL` stands on a vector that does disagree |
| 3 | **The arm-0 comparator prints 20 of the 27 components it counts**, silently (`:208`, `rows[:20]`); the seven are enumerated here | §1.1 | none |
| 4 | **The registration's mesh size is wrong by 4x** - 9,504 is one processor's share; the mesh is **38,304** cells | §9.1 | none; no gate reads it |
| 5 | **ADDENDUM 3 §A3.6 records one `checkMesh` aspect-ratio trip; there are four**, worst 1050.3162 not 1026.908433 | §11 | none |
| 6 | **The 18 ParaView renders carry no title and no caption**, so they do not meet the figure standard | §8.3 | none |
| 7 | **The convergence figure's default x-axis read "major iteration" for the history's 87 `isMajor` records**, against IPOPT's 26; relabelled under `--figure-standard` | §3, §8 | none |
| 8 | **`O_mp` launched on an `ARM0` `GATE FAIL`**, against §7's *"`O_mp` does not launch until `ARM0` reads `PASS`"*; authority is directive E | §2 | none; recorded as a departure |
| 9 | **The production grading path was not fixed at the pre-registration commit** (rule 2), disclosed in ADDENDUM 3 and repeated here because the disclosure travels with the verdict | §7 | the verdict may be weighed below one from a frozen path |
| 10 | **The registered stop-rule monitor never ran**; §6 was unsatisfied | §7 | none |

---

## 13. INSTRUMENTS THIS REPORT ADDED OR CHANGED

| file | what | controls |
|---|---|---|
| `cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_percondition_table.py` | **new.** Attributes each primal to a flight condition by matching its converged `CL` to the driver record and reproducing `obj.J` from the weighted drag sum. A reader: no gate, no grade, writes nothing into a run directory, starts no solver. | `--selftest`: **`D6R2C_PERCOND SELFTEST PASS n=8`**, 2 value-unique windows and 6 planted rejections at `PLANT = 1.234e-03` |
| `cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_sens_figure.py` | **changed.** Added `--figure-standard`: one caption line per figure with a 20-word refusal, the explanation moved to a `_sheet_text.json` sidecar, and the convergence x-axis named for the counter it actually plots. | the existing `--selftest-plant` re-run after the change: **`PLANTED CONTROL PASSED`**; plus a two-limb control on the new refusal, driven this invocation - a 10-word caption is **accepted** and a 21-word caption is **refused** with `D6R2C SENS REFUSE: caption for ctl_bad is 21 words, the standard allows 20`. A guard shown only to reject is not shown to discriminate. |

**Neither file is in the frozen-instrument table of §11 and neither was at the freeze**, so neither
edit is a rule-6 violation; `d6r2c_sens_figure.py` is a post-hoc reader built after the freeze for
this very item, and it says so in its own header.

**Nothing in this report was committed by this lane.**

---

## 14. WHAT THIS REPORT DOES NOT CLAIM

- **It does not soften `GATE FAIL`.** No section, token or adjective here qualifies it, and the two
  `PENDING` sections are queue states on unbought runs, not hedges on the verdict.
- **It does not present the arm-0 rank check as a gradient verification.** §10 of the registration
  forbade that in advance and section 1 repeats the prohibition.
- **It does not determine why the arm-0 dump aliases its lift gradients.** The fact is measured; the
  mechanism is `NOT MEASURED` and is routed, not guessed.
- **It does not re-grade anything**, does not move a gate, a threshold, a cap or a label, and does not
  edit a frozen file. Two corrections to frozen records are stated here for their authors to land as
  dated addenda.
- **It does not present the supervisor's residual-partition measurement as this lane's.** Section 11
  says which figures are measured here and which are relayed, with the chain depth.
- **It does not claim the figures fully meet the figure standard.** Four residual departures are named
  in section 8.3.
- **It does not describe this case as transonic** and shows no shock, because there is none.
- **It sends nothing, files nothing and uploads nothing.** Rule 7. Every finding in section 12 stays
  in this box until Sanaa decides otherwise.

**One style departure, disclosed rather than left to be found.** `REPORTING_CHARTER.md` §11 says a
surface never carries an em dash or an en dash. This file carries **three**, at lines 66, 278 and
746, and **all three sit inside verbatim quotations** of `PREREGISTRATION.md` §10, §4 and ADDENDUM
3 §A3.6. Restyling a character inside a quotation would falsify the quotation, which is the same
reading that charter's own amendment record took when it opened its §10 precision clause and left
it alone. Every other em dash this lane wrote, **26 of them**, was replaced with a plain hyphen.
