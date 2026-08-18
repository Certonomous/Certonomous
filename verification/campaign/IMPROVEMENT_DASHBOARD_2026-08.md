# Improvement metrics dashboard — 2026-08 (first monthly snapshot)

First concrete cut of the §1 dashboard from `docs/CAPABILITY_STRATEGY.md`
(Katie's directive, 2026-08-08; commit 47e52caa): the five metrics, measured
from the records that already exist — `LESSONS.md` L-1..L-40, the 2026-08-08
audit records, the negative-verdict review, the run archive, and git history.
No framework, no new instrumentation; every number below carries its
derivation so next month's snapshot can recompute it the same way. Compiled
2026-08-08 (UTC) by the self-improvement machinery agent. Zero solver
core-min; read-only on all existing records.

**Baseline notice:** this is month 1. Metrics 1, 2 and 5 are genuine
month-over-month trend metrics from this point on. Metrics 3 and 4 are
measured over cohorts that only exist because of this specific week's audit
orders (the dead-lever audit, the mesh audit, the negative-verdict review),
so their month-2 values will depend on whether equivalent re-audit cohorts
exist then — they are **baseline-only** this month in the sense that the
cohort definition, not just the number, must be re-established next time.

---

## Metric 1 — Repeat-incident rate: 2 of 40 lessons recurred after codification (5%)

**Definition applied:** a lesson counts as a repeat only if its failure mode
recurred AFTER the lesson was written down. Instances that occurred before
codification — including all four commit-collision instances recorded in
`campaign/SHARED_TREE_COMMIT_HAZARD.md` (the 2026-08-02 `self_audit.py`
sweep-in under `37086d38`, the 2026-08-07 pair under `d52446e7`, and the
`git reset` displacement of `770436f9`), which predate that record's
completed both-edges rule — count as the incident that produced the lesson,
not as recurrence.

**The two repeats:**

1. **L-5 / P4 (orphaned collectors).** The lesson's own text is the
   evidence: the agent-exits-while-solver-runs pattern recurred "three times
   before the rule was written **and three more after**" (the ladder agent
   twice, the DPW agent once, post-codification). This is the clearest
   measured case of a written rule failing to change behavior — and it is
   also the clearest cure on record: D12 moved the collector into
   `scripts/launch_solve.sh` structurally, and no recurrence has been
   recorded since (the dead-lever audit's F-family batch agent death on
   2026-08-08 was a *fork* death, the adjacent standing-lesson class, and
   its findings were recovered — not an orphaned solve).
2. **L-1 (verify the record against git history before investigating) —
   counted conservatively.** On 2026-08-07 the chief's negative-verdict
   review carried F5c's "converged solves 4–12× wrong" as an open mystery
   and proposed diagnostics for it, while commit `fe121af2` (2026-07-31)
   had already proven the reading was the wallShearStress sign convention
   (`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` entry 5 outcome).
   L-1's rule — check history before investing in a stated premise — was
   codified 2026-07-27 and was not applied. The lab logged this as a new
   lesson (L-39, verdict aging) rather than an L-1 repeat; both readings
   are defensible, and the conservative one (count it) is used here. The
   judgment call is stated so next month's compiler can apply the same one.

**Not counted, and why:** L-12's two directory sweeps and L-32's two
stale-record instances all predate their lessons' writing; L-19/L-22/L-28
are recorded by the lessons file itself as *new modes in the L-16 family*,
not repeats of an existing lesson ("same lesson twice" is the bar, and the
file distinguishes them explicitly); the four dead levers found by the
2026-08-08 audit are pre-codification instances of L-40 that the audit was
run to find.

**Rate: 2/40 = 5%.**

**What would make this number better next month:** zero NEW
post-codification recurrences in September, and specifically: L-39's
reconciliation sweep actually being run before any review or filing that
carries a standing verdict (that is the live recurrence channel — it fired
twice in one week counting the review itself). The structural lesson from
the one cured repeat (L-5→D12): a lesson that recurs even once after
writing should be presumed prose-immune and moved into the harness, which
is exactly the strategy's post-mortem-to-preflight SLA item.

---

## Metric 2 — Lessons→preflight conversion: 10 of 40 fully executable (25%), 10 partial, 20 prose-only

**Definition applied:** "converted" means an executable enforcement exists —
a script/gate/test/banner that fires without a human remembering the rule,
or a charter schema requirement that review mechanically fails on. A charter
*citation* alone is prose. Verified against the scripts and modules
themselves, not the lessons file's claims.

**Fully converted (10):**

| lesson | enforcement |
| --- | --- |
| L-2 (verifier self-reports) | `scripts/ledger_backup.py` parse-tolerant verified backup + `scripts/self_audit.py::check_ledger_integrity` re-derives counts |
| L-5 (orphaned collectors) | `scripts/launch_solve.sh` (D12): arms collector at launch, `setsid`'d, `--check` refutes false "finished" claims |
| L-6 (wrapper PID capture) | `scripts/launch_solve.sh` captures the real PID and keys on artifacts |
| L-14 (Initial vs Final residual) | `scripts/check_convergence.py` / `check_convergence_sweep.py` read the gate's own residual and the solver's converged statement |
| L-15 (exit code vs ConvergedReason) | same scripts + `check_convergence_validate.py` read PETSc/OpenFOAM convergence reasons, not exit codes |
| L-21 (residualControl dead field) | `scripts/case_preflight.sh` fails, pre-compute, any case whose residualControl names only untransported fields |
| L-24 (per-quantity convergence) | `sdk/chief_engineer/log_signatures.py` + MONITOR_STANDARD S-clauses (incl. the S10d magnitude-explosion detector adopted 2026-08-08, replayed over 974 histories, 5 fires / 0 false positives) |
| L-27 (gate artifacts retained) | `scripts/self_audit.py::check_evidence_paths_exist` + `check_f2_reproduction` (the incident's own regression) |
| L-30 (gate pinned by recipe ceiling) | `sdk/workflows/geometry_study.py::ceiling_pinned` + `sdk/chief_engineer/certificate.py::_mesh_rows` two-value gate, tested in `sdk/tests/test_geometry_study.py::PinnedGateTests` |
| L-40 (lever activity) | Verification Charter v1.5 §9 `levers_verified_active` schema (a conclusion citing an unverified lever fails review) + `sdk/chief_engineer/mesh_certificate.py` + the executed dead-lever and birth-certificate audits |

**Partially converted (10)** — machinery exists for the incident or a
sub-class, the general rule still rides on discipline: L-12 (`.gitignore`
blocks the solver-output sweep class; the pathspec-commit rule itself has no
hook), L-13 (the birth-certificate clause now blocks checkMesh-failing
meshes at entry; the dz-sweep-before-staging habit is prose), L-19 (S10d
catches divergence-behind-a-quiet-log; the relaunch-comparison test is
prose), L-22 (`check_evidence_paths_exist` verifies citations resolve; the
primary-evidence-per-crash-claim rule is prose), L-25 (`F7_runs/
front_metrics.py` sweeps that metric's free parameter; not generalized),
L-26 (the signcheck harness and realizability script exist as one-off
tools, not a gate on coded fvOptions), L-29 (the IDWarp patch +
`IDWARP_IMPORTED_FROM` provenance banner; the audit-every-guard rule is
prose), L-32 (`check_withdrawn_numbers` / `check_gate_table_vs_transcripts`
catch some satellite-vs-record drift; no check that a verdict change
reached the case's own file), L-35 (the operator cross-residual harness is
reusable in `W4-a4-discriminators/` but lives outside `scripts/`), L-36
(the decomposition-invariance gate is adopted practice with no script).

**Prose-only (20), named as the strategy demands:** L-1, L-3, L-4, L-7,
L-8, L-9, L-10, L-11, L-16, L-17, L-18, L-20, L-23, L-28, L-31, L-33,
L-34, L-37, L-38, L-39.

Of these, the ones with a plausible cheap harness next month: **L-1/L-39**
(a reconciliation-sweep script: given a record path, list commits since its
verdict date touching its evidence paths — the exact check entry 5's audit
did by hand), **L-11** (case_preflight gains an optional `--sibling` diff of
`turbulenceProperties` + `0/` field list), **L-18** (a briefing template
that machine-includes the standing constraints), **L-28** (detectors report
their increment; a distinct-value count over any published column is a
five-line check), **L-31** (charter §7 FD tables could require the
neighbouring-component control row mechanically).

**What would make this number better next month:** +3 conversions from the
list above, prioritized by metric 1's live recurrence channel — L-1/L-39
first, since it is the only lesson that repeated this month and remains
unenforced.

---

## Metric 3 — Median time-to-root-cause: 58.0 h (9 timed incidents; 55.8 h if the A4 defect counts once)

**Definition applied:** discovery = the first dated artifact recording the
symptom (in-record timestamp where one exists, else the commit that
recorded it); root cause = the commit/record establishing the proven
mechanism. Nine incident intervals could be timed end to end:

| incident | discovery | root cause | elapsed |
| --- | --- | --- | --- |
| pyDAFoam silent warm-start (A3 attempt-1) | 2026-08-08T02:40:18Z (in-record, `A3_SUBLU_RESULT.md:153`) | 02:45:32 (`f77b2607`, 0/U == 1000/U bit-exact) | **0.09 h** |
| L-26 F6a fvOptions sign flip | 2026-07-29T02:37:01Z (registry log `uq_oneC_…Z.log`) | 2026-07-30 17:09 (`40401742`, signcheck) | 38.5 h |
| L-29 IDWarp degenerate branch | 2026-07-29 22:05 (`5a7b6235`, 634% flip) | 2026-08-01 00:11 (`7303735a`, proof-by-repair) | 50.1 h |
| L-39 F5c "4–12×" | 2026-07-29 03:04 (`f6d667eb`) | 2026-07-31 06:53 (`fe121af2`, sign-convention control) | 51.8 h |
| L-35 A4 decomposition (operator-level) | 2026-08-02 07:03 (`ca861729`, 8.95%) | 2026-08-04 17:04 (`49ab2816`, 329×‖b‖ cross-residual) | 58.0 h |
| L-28 F2 detector quantisation | 2026-07-28 05:25 (`6cc7f629`) | 2026-07-30 17:10 (`515d9093`) | 59.8 h |
| L-37 A4 mechanism (limiter branch) | same discovery as L-35 | 2026-08-05 17:14 (`671f40bb`, one-word cure) | 82.2 h |
| L-30 gate pinning | 2026-07-27 04:18 (`cda25ddb`, "leading suspect" reading) | 2026-08-02 08:45 (`d5a76230` + `4a05304f` population check) | 148.4 h |
| L-40 M6 transonicPCOption dead lever | 2026-07-30 04:20 (`c2a03c02`, R5 conditioning wall) | 2026-08-08 02:29 (`12d3a7a3`, dead-code source line) | **214.2 h** |

**Median: 58.0 h** (55.8 h collapsing L-35/L-37 into one A4 incident).
Range 0.09 h → 214 h, and the range is the finding: the fastest
root-cause on record (warm-start, 5 minutes) happened inside a
pre-registered arm with the evidence discipline already pointed at the
run, while the slowest (the dead lever, 9 days) waited for a new lesson
CLASS (L-40) to exist before anyone thought to check the runtime log.

**Could not be timed, listed per the strategy's demand:** L-27's F2
unreconstructible number (the discovering "act-survey audit" left no
dated artifact — itself an L-27-shaped defect in the meta-record); L-22's
B3/F5c OOM misattribution (the record's own finding is that the claim
traces to no dated origin at all, so no interval exists); the M6
conditioning wall itself (still open — no root-cause end yet). A related
number deliberately NOT counted here: the 235.4 h between F5c's proof
(`fe121af2`) and its record correction (`a10ebc31`) is documentation
latency, tracked under metric 1's L-39 discussion, not time-to-root-cause.

**What would make this number better next month:** (a) median under 48 h;
(b) zero incidents in the untimeable bucket — which requires only that
discovery events get a dated line in a record at the moment of discovery
(the docket already timestamps work items; incidents need the same
habit); (c) no incident whose root-causing had to wait for a new lesson
class — the L-40 tail is the cost of a blind spot, and the lever-echo /
face-caveat machinery now under construction is priced to remove it.

---

## Metric 4 — Conclusions surviving re-audit: 307 of 315 re-audited claims survived (97.5%); 4 of 7 re-opened verdicts survived (57%)

The last 24 hours provide a clean cohort: three independent adversarial
re-audits of standing conclusions, per the supervisor-adversarial-
verification doctrine.

| re-audit | denominator (claims re-examined) | survived | died | survival |
| --- | --- | --- | --- | --- |
| Dead-lever audit (`DEAD_LEVER_AUDIT_2026-08-08.md`) | 130 lever/conclusion pairs (126 VERIFIED + 4 FOUND-DEAD; the 16 UNVERIFIABLE-FROM-LOGS are excluded — they neither survived nor died, they gained face caveats) | 126 | 4 (1 conclusion-reopening: `transonicPCOption: 2`; 3 previously caught) | 96.9% |
| Mesh birth-certificate audit (`MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md`) | 178 unique reachable meshes | 177 | 1 (A3 vcoarse, born broken, pyHyp tip collapse) | 99.4% |
| Negative-verdict review outcomes (`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`, entries with executed re-audits by 2026-08-08) | 7 entries (1, 2, 3, 5, 8, 11, 12) | 4 — entry 1 (+72% hills FAIL confirmed; QCR null is physics), entry 2 (hump bias confirmed at challenge conditions, a1 mechanism found), entry 3 (F8 fork resolved: BEM proves the limit cycle is basin behavior; steady-branch closure stands), entry 12 (G2 FAIL upheld through the weighted arm, `91fe03b3`/`d66f82a5`) | 3 — entry 5 (F5c's 4–12× premise DIED: sign convention, `fe121af2`), entry 8 (the M6 "conditioning wall" premise DIED at this rung: one dead token, PC-alone CONVERGED, `11b90d25`), entry 11 (the a10 non-containment DIED: under-membership; the n=3 band contains CFL3D) | 57% |
| **Pooled** | **315** | **307** | **8** | **97.5%** |

Read the two levels separately — they answer different questions. The
pooled 97.5% says the archive's evidence base is sound when re-derived
claim by claim. The 57% on re-opened negative verdicts says that when the
lab deliberately re-interrogates its own *conclusions*, nearly half move —
which is the re-audit machinery earning its cost, not a defect. A month in
which the second number rises toward 100% with the same re-audit effort is
a month the first-pass conclusions got better.

**What would make this number better next month:** (a) the pooled number
holds ≥97% on a freshly defined cohort (it will drift toward 100% only if
audits keep being adversarial — a 100% from soft audits is a worse
outcome); (b) the three face-caveat classes the dead-lever audit ordered
(F5c SIMPLEC, Ahmed SIMPLEC, TMR/A3 scheme narratives) actually appear on
the records' faces, so next month's audit finds zero owed caveats;
(c) fewer conclusions ENTER the month unverifiable-from-logs — the
audit's structural fix (drivers cat `fvSchemes`/dictionaries into logs)
closes the largest class at birth.

---

## Metric 5 — Orphaned-run count: 9 orphaned one-off run dirs; 299 batch-sample dirs with no per-run ledger entry; 43 record-referenced dirs no longer on disk

Measured by cross-referencing all 423 top-level entries of
`/home/ubuntu/certonomous-runs/` (411 directories + 12 stray `w3_*` queue
scripts/logs that should not live there at all) against every `.md`,
`.json` and `.jsonl` under `demo-output/website/` and `docs/` (including
both ledgers: `mega-batch/ledger.jsonl`, 208,194 rows, and
`campaign/MODEL_FORM_runs/ledger.jsonl`) plus `agenda/docket.json`.

- **103 run dirs are referenced by name** in records — every
  conclusion-bearing campaign/dafoam run dir among them.
- **9 one-off run dirs are orphans** — no record, ledger or docket entry
  names them: `W4-a4-localize`, `W4-repro-fromscratch`,
  `cache-bypass-check2-4fe617`, `cache-bypass-check-docker2-2a0877`,
  `study-airliner_wing_span52-2cdf8e`,
  `study-airliner_wing_span52-medium-e565e1`, `vspaero-proof`,
  `yplus-check-production`, and `modelform-cases` (empty; plausibly the
  live extension batch's staging dir — flagged, not touched).
  `W4-a4-localize` and `W4-repro-fromscratch` contain real solver logs
  from the decomposition-defect campaign whose *findings* are recorded
  but whose run dirs no record cites — the exact L-27 shape (a result
  whose artifact nobody can navigate to from the record).
- **299 batch-sample dirs have no per-run ledger entry anywhere**:
  `study-b52-*` (102), `act7-ahmed_25-*` (87), `act6-nasa_hump-*` (72),
  `act9-crm_wingbody-*` (36), `act8-onera_m6-*` (2). These are
  content-hash ensemble members whose AGGREGATE results are recorded
  (`mission-output/` field/body JSONs, the campaign band records), but the
  hash-named dirs themselves are addressable from no ledger — the
  mega-batch ledger covers different solver families entirely
  (cylinder/vspaero/reduced-order/transonic-naca/ahmed-3d). This is a
  structural property of the act machinery, not 299 separate accidents;
  it is counted separately from the 9 so the trend line is not dominated
  by one design decision.
- **Adjacent evidence, opposite direction (cited, not redone):** the mesh
  audit found **41 case meshes + 2 GENERATOR_FINDING work meshes**
  referenced from records but no longer on disk (38 of the 41 with
  retained certificates) — records pointing at nothing, the mirror image
  of dirs nothing points at.
- **One orphaned PRE-REGISTRATION** (chief ruling, from the calibration
  sweep): `campaign/F12_PREREGISTRATION.md` (2026-07-30) states four
  predictions and has no results record — a prediction set nothing ever
  graded, the pre-registration analogue of an orphaned run. Counted here,
  not in the calibration cohort.

**What would make this number better next month:** the 9 orphans triaged
(each either gains a one-line entry in the record its logs served, or is
deleted with a dated note); the birth-certificate proposal's registry
mechanics (`a-mesh-enters-with-its-birth-certificate-or-not-at-all`)
extended one step so act/study sample dirs get a per-run ledger line at
creation — after which this metric becomes a real zero-target counter; and
the 12 `w3_*` scripts/logs moved out of the run root.

---

## Recomputation notes for month 2

- Metric 1: re-sweep `LESSONS.md` (now L-1..L-40 + any new) against the
  month's incidents; apply the same conservative counting (borderline
  family-repeats count).
- Metric 2: re-run the enforcement grep
  (`grep -o "L-[0-9]\+" scripts/* sdk/chief_engineer/* sdk/workflows/*`)
  and re-verify each claimed conversion against the code, not the lesson.
- Metric 3: requires incidents to carry discovery AND root-cause
  timestamps; the pre-registration/docket records mostly do, informal
  finds mostly don't — see the missing-timestamp list in metric 3.
- Metric 4: needs a fresh adversarial re-audit cohort; if none is ordered
  in September, report "no cohort" rather than reusing this one.
- Metric 5: rerun the cross-reference (the exact commands are cheap:
  name-list × grep -F over records); count is comparable only if the
  same three-way split (orphans / unledgered batch samples / unreachable
  references) is kept.
