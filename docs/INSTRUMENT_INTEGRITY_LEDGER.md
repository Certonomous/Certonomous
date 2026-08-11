# Instrument integrity ledger

**Standing dispatch from the lab director. Compiled 2026-08-11. Read-and-record: nothing
found here was fixed in this pass.**

This lab's instruments fail more often than its physics does, and the failures share one
shape: **an instrument returns a clean, confident, negative result that is false, and the
negative is trusted because nothing looked wrong.** This ledger turns that scattered
history into one auditable list.

Its one new column, and the reason it exists, is the last one: **does the verdict line
state its own reach?** A verdict that says *complies* without saying *over what* is how a
narrow instrument gets read as coverage. A caveat in a code comment does not reach the
person reading the verdict.

## 0. What this pass found

| | |
|---|---|
| **Denominator** | 534 tracked `.py`/`.sh` files; 296 hit at least one of four independent instrument-detection axes; 142 of those are production (non-test, non-`demo-output`) |
| **Profiled verdicts** | **66** — the 34 `self_audit.py` checks plus 32 standing instruments |
| **reach demonstrated** | **30** |
| **reach assumed** | **25** |
| **known-blind-and-shipping** | **11** ← *the finding* |
| **Verdicts that state their own reach** | **14 of 34** self-audit checks carry a numeric denominator; **30 of 34** carry a written blind spot that the terminal verdict never prints |
| **Hump-adjoint attempts** | **11 distinct attempts + 3 staging faults. 0 were ever deliberately reproduced as a negative control. 4 abandoned with no root cause; 2 built and never executed.** |

**Two false greens were reproduced firsthand in this pass** (§4.1, §4.2). Both are the
empty-corpus shape: the instrument scanned nothing and said clean.

**Prior work this builds on, and does not repeat.**
`demo-output/website/campaign/INSTRUMENT_INTEGRITY_2026-08-11.md` swept the same estate on
a different axis — *fail-open* and *false-positive channel* — and enumerated 100
function-level instruments, of which 67 never ask "did the check run?" and 20 are
false-positive channels. That pass is the authority on those columns and its FP-1..FP-23
numbering is cited throughout. **This ledger adds the two columns it did not carry:
demonstrated reach, and whether the verdict states its reach.** Where a finding is that
pass's, it is labelled so.

---

## 1. How the instruments were enumerated, and what the denominator was

**A list assembled by hand is exactly the surface where a forgotten instrument survives.**
The enumeration was therefore run on four independent axes, chosen so that no two share a
failure mode, and unioned.

Base denominator: `git ls-files '*.py' '*.sh'` = **534 files**.

| axis | rule | hits | files *only* this axis found |
|---|---|---|---|
| **A — verdict emission** | a `print`/`echo`/`write` line carrying `PASS FAIL VERDICT GREEN RED COMPLIAN COMPLIES VIOLATION CLEAN BLOCKED APPROVED REJECT OK ✓ ✗` | 89 | 6 |
| **B — self-declaration** | the *filename* contains `audit gate check verif valid guard preflight monitor score grade criterion certificat sentinel forensic test_` | 137 | 8 |
| **C — enforcement** | the file exits non-zero on a condition (`sys.exit(1|2)`, `raise SystemExit`, `exit 1`, `return 1`) | 165 | 59 |
| **D — alternate lexicon** | emits `SETTLED UNSETTLED ACCEPT "within tolerance" "no violation" CONSISTENT MISMATCH DRIFT STALE ✅ ❌ ⚠` | 24 | 2 |
| **union** | | **296** | |

### 1.1 The axes disagree, and that is the point

**No single axis found them all, and the shortfalls are large:**

- **Axis A missed 12 of axis D's 24.** Half the instruments that speak an alternate verdict
  dialect are invisible to the primary verdict lexicon. Had the sweep stopped at A —
  which is the obvious first thing to write — it would have returned a confident list
  missing half of a whole class.
- **Axes A and D together missed 13 standing instruments that only their names revealed**,
  among them `sdk/chief_engineer/mesh_certificate.py`, `sdk/chief_engineer/compute_audit.py`,
  `sdk/chief_engineer/certificate.py`, `sdk/scripts/citation_tier_audit.py`,
  `sdk/scripts/closure_baseline_error_gate.py`, `sdk/scripts/closure_decline_gate_audit.py`,
  `sdk/scripts/sparta_frozen_score.py`, `sdk/scripts/validate_pressure_fields.py`,
  `sdk/scripts/validate_motorbike_pressure.py`, `scripts/check_convergence_sweep.py`.
  Every one of these is load-bearing. **`mesh_certificate.py` — the instrument whose
  false-clean is item 3 in the director's own list of documented failures — is not found by
  any verdict-word search of its source.**
- **Axis C alone contributed 59 unique files**, but it is the least specific: a non-zero
  exit is also how ordinary scripts report I/O errors.

**This is the documented lab failure recurring at the meta level.** The corpus glob of
FP-1 (`rglob("*.log")` against OpenFOAM's `log.<app>`) adopted six monitor rules on 28% of
the evidence because one naming convention was assumed to be the convention. An
enumeration built on one verdict lexicon would have made the identical error about
instruments. **The union is reported rather than any single axis, and the per-axis
shortfalls are published above so the reach of this ledger's own denominator is legible.**

### 1.2 What this frame structurally cannot contain

Stated, not discovered later:

- **Gates that are human procedure in Markdown.** Not code, not in the frame.
- **Solver-side gates inside OpenFOAM dictionaries** (`residualControl`, `fvOptions`
  limiters). These grade, and they are invisible to a search over `.py`/`.sh`.
- **CI and git-hook gates.** There are none — no `.github/workflows`, no non-sample hooks
  (confirmed by the prior pass).
- **`.ps1` files, and any verdict travelling through a token none of the four axes name.**
  An unquantified residual false-negative rate, stated because it is real.
- **Compiled PDFs and binaries.** Anything that does not decode as UTF-8 is invisible to
  all four axes — the same blindness `check_rank_claim_surfaces` declares about itself.

### 1.3 The profiled subset

The 142 production files in the union are more than can carry a four-column profile each,
and most are producers whose `OK` is progress output rather than a verdict about evidence.
**66 verdicts were profiled in full**: the 34 checks inside `scripts/self_audit.py` (each is
an independent instrument with its own verdict line) and 32 standing instruments — those
that are re-run across cases and whose verdict is cited by a record. The remainder are
one-shot campaign-local gates under `demo-output/website/campaign/**` and
`demo-output/website/dafoam/**` (24 candidates), enumerated but not profiled; the largest
family there is 20 copies of `hump_gate_analysis.py`, one per sweep arm.

---

## 2. The classification

**reach demonstrated** — the instrument has been shown to FIRE on a true positive: a
planted bad input, a known-answer suite, or an observed firing on a real defect.
**reach assumed** — it looks correct and has never been shown to fire.
**known-blind-and-shipping** — a blind spot is documented *somewhere*, and the instrument
is in service unchanged with that blind spot.

| class | count | share |
|---|---|---|
| reach demonstrated | 30 | 45% |
| reach assumed | 25 | 38% |
| **known-blind-and-shipping** | **11** | **17%** |

**One verdict in six in this lab ships with a blind spot its own authors have written
down, and more than one in three has never been shown to fire at all.** That is the
finding. The blind spots are not unknown — they are known, recorded,
and invisible at the point of reading.

### 2.1 `self_audit.py` — 34 checks

Run over the working tree on 2026-08-11: **PASS 15, WARN 8, FAIL 8, INFO 3.**

> *Caveat on this tally.* `scripts/self_audit.py` currently carries a 301-line uncommitted
> working-tree change by another agent (the word-form placement guard, §4.4). The numbers
> above are the working tree, not `HEAD`. They are reported as measured and labelled.

**Reach demonstrated — 17.** Fifteen are firing right now on real defects, which is the
strongest available demonstration; two more (`check_board_placement_words`,
`check_bundle_drift`) pass but carry tests. Eighteen checks are currently non-PASS, but one
of them — `check_rank_claim_surfaces` — is classed **known-blind-and-shipping** instead
(§4.4): it fires, and it is documented blind to three instances of its own class.

**Known-blind-and-shipping — 1.** `check_rank_claim_surfaces`.

**Reach assumed — 16.** These return PASS or INFO, have **no test anywhere in the suite**,
and have never been observed firing:

`check_wall_counters_vs_ledger` · `check_closure_entry_of_record` ·
`check_memory_scaling_law` · `check_withdrawn_numbers` · `check_f2_reproduction` ·
`check_cost_predictions` · `check_benchmarks_vs_closure_record` ·
`check_statistical_labels` · `check_channel_totals_use_one_rule` ·
`check_restated_thresholds` · `check_campaign_json_citations` ·
`check_stored_rungs_carry_solved_precision` · `check_declined_ladders_name_their_guard` ·
`check_order_window_declines_state_their_dimensionality` ·
`check_every_finding_prices_its_remedy` · `check_every_check_states_its_basis`

**32 of the 34 checks have no test at all.** Only `check_rank_claim_surfaces` and
`check_bundle_drift` are exercised by `sdk/tests/`. For the 16 that also currently pass,
*nothing in the repository distinguishes "this check found no defect" from "this check
cannot find a defect".*

### 2.2 The 32 standing instruments

Twenty-three are profiled individually below (13 demonstrated, 10 known-blind); the
remaining nine are the *reach assumed* group named after the table.
`check_rank_claim_surfaces` appears here for context but is counted once, in §2.1.

| instrument | class | basis for the class |
|---|---|---|
| `scripts/check_convergence.py` | **demonstrated** | `check_convergence_validate.py` — 13 known-answer cases incl. `NOT_CONVERGED` and `CANNOT_TELL`; **re-run in this pass, all 13 pass** |
| `sdk/chief_engineer/log_signatures.py` (S6,S8–S12,S10d) | **demonstrated** | 72 tests, 20 fire-named, plus archive sweeps (`test_archive_sweep_names_the_known_fires_and_no_others`); S6 captured 135/135 pre-registered sentinels on production |
| `sdk/chief_engineer/exec_bits.py` | **demonstrated** | 15 tests, 5 fire-named; fired in production on `case_preflight.sh`'s missing bit |
| `sdk/chief_engineer/mesh_certificate.py` `parse_check_log` | **demonstrated** | 33 tests, 6 fire-named; `VERDICT_UNVERIFIED` + `_FATAL` added after a real false-clean; used as the positive-control template by the prior pass |
| `sdk/chief_engineer/lever_echo.py` | **demonstrated** | 54 tests, 8 fire-named |
| `sdk/chief_engineer/uncertainty_band.py` `compose` | **demonstrated** | 14 tests, 4 fire-named; carries a conclusiveness flag |
| `sdk/chief_engineer/uq.py` `reportable_band` | **demonstrated** | 59 tests, 6 fire-named |
| `sdk/workflows/tmr_verification.py` | **demonstrated** | 76 tests, 9 fire-named |
| `sdk/scripts/validate_motorbike_pressure.py` | **demonstrated** | 37 tests, 7 fire-named |
| `scripts/morning_report.py` | **demonstrated** | 17 tests, 6 fire-named; named third state `PENDING:` |
| `sdk/scripts/dow_2011_table42_check.py` | **demonstrated** | carries its own negative control |
| `scripts/mint_retrospective_certificates.py` | **demonstrated** | every refusal is a named class; no test file |
| `scripts/case_preflight.sh` | **known-blind** | fires (positive control: `FAIL: 0/U header has no class entry`) **and passes an empty directory** — §4.1 |
| `sdk/scripts/is_idle.sh` | **known-blind** | 6 work classes absent from a hand-written list; realized power-off 2026-07-30 10:40 (FP-9). Escalated, deliberately not fixed |
| `scripts/audit_transcripts.sh` | **known-blind** | reports clean over a **non-existent corpus root** — §4.2 (new) |
| `scripts/self_audit.py` `check_rank_claim_surfaces` | **known-blind** | digit-anchored; 3 known misses; fix uncommitted — §4.4 |
| `sdk/chief_engineer/head_engineer.py` `report_markdown` | **known-blind** | 8 of 9 archived reports print `Geometry \| n/a, no issues found` (FP-7) |
| `sdk/workflows/geometry_study.py` `mesh_gates_pass` | **known-blind** | `returncode` never read; gates `in_validated_regime` for 9 workflows (FP-6) |
| `sdk/chief_engineer/lab.py` `trust` | **known-blind** | `grid_conclusive` has a third state; `converged` does not (FP-19) |
| `scripts/ledger_backup.py` | **known-blind** | `.METADATA` asserts "verified backup" facts nothing checked (FP-18) |
| `sdk/scripts/validate_closure_mesh_recon.py` | **known-blind** | 3 PASS strings hand-transcribed into `…round2.json:65` (FP-15) |
| `sdk/scripts/closure_divergence_audit.py` | **known-blind** | `.get(k, 0.0)` default makes a missing key read as agreement (FP-16) |
| `scripts/check_convergence_sweep.py` | **known-blind** | gates L-14 closure, never asks whether the check ran (FP-17) |
| `scripts/contention_audit.py` | **demonstrated** | the model citizen: its own output says *"A window that reads clean here is not PROVEN clean"* |

**Reach assumed among the standing set — 9** (`audit_camera_discretion.sh`,
`verify_warm_replay.sh`, `gate_table.py`, `citation_tier_audit.py`,
`closure_baseline_error_gate.py`, `sparta_frozen_score.py`, `replay_monitor_rules.py`
post-fix, `validate_pressure_fields.py`, `credibility.py`). `replay_monitor_rules.py`
deserves its own line: **its glob defect is fixed and the corrected replay has not been
re-run**, so the six rules adopted on 28% of the evidence are still adopted on that
evidence.

---

## 3. The reach column — does the verdict state what it covered?

This is the highest-value column and the one the lab has not been keeping.

### 3.1 `self_audit.py` — the blind spot exists as structured data and is suppressed

`self_audit.py` is ahead of every other instrument here: it carries a `BASIS` table giving
each of its 34 checks a declared kind (`EVIDENCE` 13, `PROPERTY` 13, `SURFACE` 4,
`GENERATOR` 2, `META` 2), a *catches* string, and **a written blind spot for every single
check**. `check_every_check_states_its_basis` enforces that no check ships without one.
This is the right architecture and should be the model for the rest of the estate.

**And then the terminal print suppresses 30 of the 34 blind spots.**
`scripts/self_audit.py:3713`:

```python
if declared and (declared[0] in (GENERATOR, TRANSCRIBED)
                 or declared[3]):
    print(f"         BLIND TO: {declared[2]}")
```

`BLIND TO:` prints only for `GENERATOR`/`TRANSCRIBED` checks or those naming a shared
symbol — **4 of 34**. The other 30 blind spots are computed, attached to the row, written
into `--json`, and never shown to the human reading the report. Among the suppressed:

- `check_f2_reproduction` — *"BLIND: whether that raw file is the run the record names"* —
  prints `PASS  F2 Cd and Cl match the raw force file at iteration 2000`.
- `check_memory_scaling_law` — *"BLIND: the measurements themselves, which are read from
  the SAME document that states the law. A mistyped MiB figure refits to the mistyped law
  and passes."* — prints `PASS  published memory law reproduces from its own data`.
- `check_closure_entry_of_record` — *"BLIND: whether the file it opens is the entry of
  record; that name is hard-coded here"* — prints `PASS  the wall quotes the current entry
  of record`.

**The lab's own tonight-lesson, exactly.** A caveat in a comment does not reach the person
reading the verdict — and neither does a caveat in a dict the printer skips. It is worse
than a comment, because its presence in the data structure makes the check *pass* its own
meta-audit while the reader still never sees it.

### 3.2 Denominators on the verdict line

Testing each of the 34 verdict summaries for whether it states what it swept:

| category | count | example |
|---|---|---|
| **A — numeric denominator (reach stated)** | 14 | `all 34 check(s) declare what they test` |
| **B — universal word, no number (reach implied, unquantified)** | 6 | `every published counter re-derives from the ledger` |
| **C — bare fault count, no denominator at all (reach absent)** | 14 | `5 credential field(s) do not re-derive` — *of how many?* |

Category C is the dangerous one on a PASS. `PASS  the wall quotes the current entry of
record`, `PASS  F2 Cd and Cl match the raw force file`, `PASS  published memory law
reproduces from its own data`, `PASS  the published closure block matches the generator` —
each is a true statement about one artifact, phrased as a property of the lab.

### 3.3 Standing instruments — reach on the verdict line

| instrument | verdict line | states its reach? |
|---|---|---|
| `contention_audit.py:190` | *"A window that reads clean here is not PROVEN clean: this ratio sees …"* | **YES — the model** |
| `launch_solve.sh:199` | *"PREFLIGHT NOT RUN: $PF is missing. The case was NOT checked; this is not a pass."* | **YES — a named third state** |
| `check_convergence.py` | `CANNOT_TELL`, exit 2 | **YES — a named third state** |
| `mesh_certificate.py` | `VERDICT_UNVERIFIED`, *"this log records a crash, not a clean mesh"* | **YES** |
| `morning_report.py` | `PENDING:` | **YES** |
| `log_signatures.grade_bounding_episode` | `{"graded": False}` | **YES** — and it is the *only* one of the module's detectors with a third state; the other six return a bare `None` that consumers read as clean |
| `case_preflight.sh:249` | `PREFLIGHT PASS -- clear to launch` | **NO** — no count of checks run vs skipped |
| `audit_transcripts.sh:63` | `clean: no banned vocabulary in any act transcript` | **NO** — no count of transcripts, no count of rules |
| `validate_closure_mesh_recon.py:116` | `SUMMARY: geometry=True gradU=True walldist=True` | **NO** |
| `self_audit` rank guard | `every travelling surface complies` | **NO** — and the reach it omits is the defect (§4.4) |
| `is_idle.sh:73` | `IDLE` | **NO** — no statement of which processes were probed |
| `closure_divergence_audit.py:132` | `[guard] verified: closure_challenge.score() now raises` | **NO** |
| `audit_camera_discretion.sh:162` | *"Review aid. Every line below needs a human judgement; false positives are expected."* | **YES** — for its false-positive rate; silent on its false-negative reach |

---

## 4. The findings, ranked by what a false green would cost

Ranking is by cost of a false green, not by frequency. Per L-45, a false-positive channel
outranks a larger false-negative.

### 4.1 R1 — `case_preflight.sh` returns PASS on an empty directory, silently, at the one call site that matters

**Cost of a false green: a lost multi-hour solve, or the box.** This gate stands in front
of every long solve; 146 `.done` records rest on it, and
`F11_lid_driven_cavity_ladder.md:174` archives *"run clean on every case before launch"* on
this basis.

**Reproduced firsthand in this pass:**

```
$ bash scripts/case_preflight.sh <empty dir>
  ok:   no processor dirs (will decompose fresh)
  (model undetermined; skipping field check)
  ok:   solver field headers parsed              <- over ZERO fields
  (no polyMesh/boundary yet -- mesh not generated, skipping patch check)
PREFLIGHT PASS -- clear to launch                exit=0

$ bash scripts/case_preflight.sh <empty dir> --quiet
                                                 exit=0   (no output whatsoever)
```

`--quiet` is exactly how `launch_solve.sh` invokes it. The two skip notes are the only
evidence anything was skipped, and they are suppressed at the only call site that matters.

**The instrument is not a rubber stamp** — given a `0/U` with no `class` entry it prints
`FAIL: 0/U header has no class entry` and exits 1. It fires. **It simply counts nothing,
and its PASS does not distinguish "5 of 5 checks ran and passed" from "2 of 5 ran and 3
were skipped for missing inputs".**

*This is the prior pass's FP-2, independently reproduced here. Deliberately not fixed
there: proposal P6 names a 146-record `.done` corpus replay as the prerequisite.*

### 4.2 R2 — `audit_transcripts.sh` reports clean over a corpus root that does not exist (NEW)

**Cost of a false green: the cache is revealed on camera.** This is the pre-filming
discretion gate. Its own header calls the no-reveal rule *"the single most important
rule"*.

**Reproduced firsthand, two controls:**

```
$ OUT=<empty dir>          →   clean: no banned vocabulary in any act transcript   exit=0
$ OUT=<path that does not exist>  →   clean: no banned vocabulary in any act transcript   exit=0
```

The real corpus is **17 transcripts**. The verdict names none of them. The mechanism is
`for f in "$OUT"/*/transcript.*; do [ -f "$f" ] || continue` — an unmatched glob expands to
its own literal, the `continue` fires, `hits` stays 0, and 0 hits prints `clean`.

**This is FP-1's shape in a second instrument.** FP-1 was a glob that matched a quarter of
its corpus; this is a glob that can match none of it and say so as *clean*. The prior pass
listed this file as FP-12/13 on the "asks did it run?" column but did not run this control
and did not record the non-existent-root case.

### 4.3 R3 — 30 of 34 self-audit blind spots are written down and never printed

**Cost of a false green: the lab's top-level integrity report reads as coverage it does not
have.** Detailed at §3.1. This is the single highest-leverage row in the ledger because the
data already exists; only the print gate stands between it and the reader.

### 4.4 R4 — the rank-claim guard is anchored to a spelling, and the fix is uncommitted

`scripts/self_audit.py:407` `_RANK_CLAIM` is **digit-anchored** — it matches `rank 1 of N`,
`P(rank 1)`, `best/lowest overall`. A placement claim is not a claim about digits. Three
instances of the class it exists to catch were missed:

```
DESCRIPTION_DOCUMENT.md:54     "The rank-3 entry, Wu & Zhang's SST-QCRC"
CLOSURE_CHALLENGE_STATUS.md:559  the same sentence, its parent
DESCRIPTION_DOCUMENT.md:202    "Our margin over the runner-up"
```

The file's own comment already admits it: *"a rank claim phrased in words it has no pattern
for"*. **And the verdict line beside that comment reads `every travelling surface
complies`** — the comment does not travel with the verdict.

**Status.** The three data defects are fixed. The guard in `HEAD` is still the
digit-anchored one; a word-form replacement (`_PLACE`, `_PLACE_WORD`, `_PLACE_UNNAMED`,
whole-text rather than line-bounded matching) exists **only as an uncommitted working-tree
change**, and another agent is live in that file. **Not touched by this pass.**

### 4.5 R5 — `is_idle.sh` powers the box off from an absence

**Cost of a false green: a mid-campaign power-off. Already realized, 2026-07-30 10:40.**
`found` is built from `pgrep -x` over a hand-written list; `pgrep`'s exit status is never
read; an empty result is a decision to power the machine off. `checkMesh` (182 archived
logs), `potentialFoam` (49), `surfaceFeatureExtract` (24), `setFields` (21), `sample` (20)
and `topoSet` (2) are all absent from the list. **Escalated to the chief, deliberately not
settled inside the family** — and the correct fix is not "add six names", which is the same
hand-written list one entry longer.

### 4.6 R6 — 16 self-audit checks and 15 standing instruments have never been shown to fire

**Cost of a false green: unbounded, and unmeasurable, which is the problem.** An instrument
that has never fired has not been shown to work. `check_withdrawn_numbers` guards against a
retracted figure reaching a promotional surface; `check_f2_reproduction` is described in
its own basis as *"the shape the others are measured against"*. Neither has a test, and
neither has been observed firing.

### 4.7 R7 — `log_signatures`' six detectors return a bare `None` that consumers read as clean

Only `grade_bounding_episode` carries `{"graded": False}`. The other six cannot distinguish
*no finding* from *not graded*. The detectors themselves are the best-controlled
instruments in the lab (§2.2) — **the defect is in the interface, not the detection**,
which is why it ranks below instruments that are themselves blind.

---

## 5. The hump-adjoint attempts

The director asked for this by name. Every attempt is listed; two are near-duplicates of
others and are kept and labelled rather than merged.

**Eleven distinct attempts, plus three staging faults inside the first.** Nine reached a
DAFoam adjoint stage; two were built and never executed. **Not one hump failure was ever
deliberately re-run as a negative control.** The only env-off regression control in the
whole programme is on CBFS, not the hump.

| # | id / date | what was tried | failure signature | reproduced as a negative control? | diagnosed or abandoned? |
|---|---|---|---|---|---|
| A0 | 2026-07-31, staging | three setup faults getting the F6a hump into DAFoam | `Wrong token type - expected scalar value`; `FOAM FATAL IO ERROR` from `decomposePar`; then bare `SEGV` | **No** | **Diagnosed** — DAFoam does not check `decomposePar`'s exit status |
| A1 | 2026-07-31 `8e65a4de` `hump_adjoint_run1.log` | DAFoam v5 discrete adjoint, `DASimpleFoam`, kOmegaSST, 51,626 beta DVs on `betaFIOmega`, objective = variance of `wallShearStress` vs NASA Cf; rcm, pcFill 1, 4 ranks | `Total iterations: 0. PetscConvergedReason: -9` at `KSP Residual norm 1.094138002900e+00`; `Residual tolerance not satisfied, solution failed!`; `AnalysisError: Adjoint solution failed!` | **No re-run.** Reproduced only incidentally by A3 | **Diagnosed late (2026-08-04)** — singular ILU sub-block. **But the diagnosis was performed on CBFS's dumped matrix, not the hump's** |
| A2 | 2026-07-31 `d498f198` `hump_wf_run1.log` | rung 1: `useWallFunction: True` | `Total iterations: 0. PetscConvergedReason: -9`, residual `1.094652221149e+00` | **No** | **Refuted as mechanism, not diagnosed.** Author records *"prediction 1 was mine and it was wrong"* |
| A3 | 2026-07-31 `d498f198` `hump_nofvopt_run1.log` | rung 2: `limitVelocity` fvOption removed | `Total iterations: 0. PetscConvergedReason: -9`, residual `1.094138002900e+00` — **identical to A1 to 13 digits** | **Closest thing to one** — same residual with one lever changed, but not run as a control | **Refuted as mechanism** |
| A4 | 2026-07-31 `d498f198` `hump_nrn_run1.log` | rung 3: `normalizeResiduals 1 ( None )` | `Total iterations: 2000. PetscConvergedReason: -3`; residual **exactly flat**, `1.094138002900e+00` at iteration 0 **and** at iteration 2000 | **No** | **ABANDONED — no root cause.** *"not slow convergence, zero progress"* |
| A5 | 2026-07-31 `d498f198` `hump_nat_run1.log` | rung 4: `jacMatReOrdering: natural` | `Total iterations: 1000. PetscConvergedReason: -3`; `1.094138002900e+00` → `1.094138002841e+00` — movement in the 11th digit over 1000 iterations | **No** | **ABANDONED — no root cause.** Ordering later shown *"neither necessary nor sufficient"* |
| A6 | 2026-08-04 `1cd44c04` `hump_sublu_computetotals.log` | same script + `DAFOAM_SUBPC_TYPE=lu` (rebuilt `libDASolver`, image `dafoam-subpclu:v1`) | `rc=1 wall=819s ranks=4 core_min=54.60`; iteration 900 at `9.544468674795e-01`; **no `KSPConvergedReason` ever reached** — killed by `docker stop`; `min MemAvailable: 1617516 kB` | **No.** `WARMSTART_AUDIT.md:30` rates it *"COLD-CLEAN (single-run record; no rerun existed to contaminate)"* — i.e. explicitly never re-run | **ABANDONED without diagnosis.** *"-9 is gone… what remains is slow Krylov convergence against a memory envelope"* — the rate was never explained |
| A7 | 2026-08-04, no log | staging: pristine copy without case-root `caseDef`/`fieldDef` | `decomposePar` clean IO error; **no log retained**, ledgered only as *"~40 s"* | **No** | Diagnosed (trivial) |
| A8 | 2026-08-04, no log | staging as root | OpenFOAM refuses: *"administrator rights … dlopen"*; **no log retained** | **No** | Diagnosed (trivial) — fix `-u 1002:1002` |
| A9 | **2026-07-30** `certonomous-runs/adjwall/HUMP51k/log.run` | hump-geometry `DASimpleFoam` adjoint staging inside the memory-envelope sweep | **Never reached the adjoint linear solve.** Verified in this pass: the adjoint dict is echoed (`KSPCalcEigen`, `dRdW 1e-30`) and `dRdWT Jacobian Free created!` appears at line 665, then the log runs SIMPLE iterations and **ends mid-iteration** on 2026-07-30 19:14. No `Main iteration`, no `ConvergedReason` | **No** | **ABANDONED, undiagnosed, and until 2026-08-11 uncited by any archived record** |
| A10 | 2026-08-04 `runScript_hump_rich.py` | Richardson-wrapped sub-solve, `globalPCIters: 3`, `gmresRestart` capped at 500 | **NEVER RUN** — staged only | n/a | **ABANDONED before execution.** No docket proposal was ever filed (confirmed in this pass: `demo-output/website/agenda/` holds no `hump_rich` / `globalPCIters` / "Richardson-wrapped" entry) |
| A11 | 2026-08-04 `run_hump_fd.sh` | central-difference FD verification of the *hump* beta gradient (S1 protocol) | **NEVER RUN** — harness written; `fdlogs/` holds CBFS points only; no hump FD logs anywhere | n/a | **ABANDONED before execution** |

### 5.1 Attempts kept despite looking redundant

- **A2, A3, A4, A5 are one rung ladder** and could read as one attempt. They are four, and
  keeping them separate is what makes visible that **two were refuted and two were
  abandoned** — a merged row would have carried the ladder's overall verdict and lost the
  two undiagnosed stagnations entirely.
- **A9 is a near-duplicate of A1's staging** and is on a different date, in a different
  campaign, under a different sweep. It is the only attempt no archived record cited. **It
  is exactly the attempt a redundancy merge would have dropped.**
- **A7 and A8 are trivially-diagnosed staging faults with no logs.** They are kept because
  "no log retained" is itself the finding: two attempts exist in this lab's history whose
  only trace is a ~40 s ledger row.

### 5.2 What the abandonment pattern shows — the point of asking

**A4 and A5 are the answer to the director's question.** Both levers converted a
catastrophic failure (`-9`) into an honest stagnation (`-3`), and in both the residual is
flat to 13 significant figures across 1000–2000 iterations. Verified independently in this
pass against the logs. The record's own words: *"That is the same place R5 ended up on the
M6 family after four levers."*

**Nothing ever explained the stagnation.** When the `-9` was later cured (A6) the residual
began to descend, so the flat-residual state of A4/A5 was **superseded, never explained**.
No docket item, no test, no follow-up run.

**This is a real capability boundary hiding behind an assumed one.** The programme's
standing account is that the hump is *"blocked on convergence RATE vs memory envelope, not
singularity"*. That account rests on A6 — a run that was killed at iteration 900 and never
produced a `KSPConvergedReason`. **The rate was never measured to completion, and the
memory envelope was never shown to be the binding constraint.** `docs/PRODUCT_LIST.md`
still carries Stage 1 as `[-]` (attempted/blocked), and the "fresh budget" the record says
the Richardson attempt is waiting on **was never requested**: no proposal for it exists.
The last hump-adjoint compute in the archive is 2026-08-04 15:58Z.

### 5.3 Two record defects surfaced while searching (not corrected)

1. **A hump gradient is claimed that never existed.**
   `demo-output/website/dafoam/DEFECT_REACH_decomposition_cases.md:564` says *"the NASA-hump
   beta-field gradient from the pc-unblock session (FD-verified at 3 cells under its single
   decomposition) has not been re-run under a second decomposition"*. No hump gradient was
   ever produced. The pc-unblock session's FD-verified 3-cell gradient (cells
   5491/6740/12486) is **CBFS**; the hump run was killed at iteration 900 with no reason
   code. **The sentence describes a re-run that is owed on a gradient that does not exist.**
2. **A quoted hump number has no source log.** S1's *"inert at the solution, max abs U
   44.54"* — the number 44.54 appears in no archived hump log (prior pass; carried here
   because it is a hump-adjoint record defect).

### 5.4 The frame of this hump sweep

Three independent instruments over `/home/ubuntu` (17 GB `Certonomous` + 66 GB
`certonomous-runs`): a filename `find` (355 paths), a content fingerprint (`Find 622
reference points`, the hump objective), and a universal DAFoam-adjoint marker
(`transonicPCOption`) establishing the archive's total population of DAFoam adjoint logs at
651. **Structurally outside the frame:** runs that left no log (A7, A8 are the two known
ones — there may be more), the in-container DAFoam build, levers OpenFOAM never echoes, and
two 906 MB tarballs left unopened.

---

## 6. Recommended rungs

Not fixes. **A fix authored by the agent that found it, in the same pass, is the pattern
this lab has repeatedly had to unwind.** Each rung names its owner and its prerequisite.

| rung | what | cost | prerequisite |
|---|---|---|---|
| **V1** | Print `BLIND TO:` for all 34 self-audit checks, not 4. One condition at `self_audit.py:3713`. | **NO COMPUTE** — the strings already exist | none. *Owner: whoever holds `self_audit.py`; it is live right now* |
| **V2** | Give `audit_transcripts.sh` a denominator: refuse to say `clean` when the corpus is empty, and print `N transcripts × 3 rules scanned`. | **NO COMPUTE** | none |
| **V3** | Give `case_preflight.sh` a third state and a count: `PREFLIGHT PASS — 2 of 5 checks ran, 3 skipped (no mesh, no model)`, emitted under `--quiet` too. | **NO COMPUTE** | the 146-record `.done` corpus replay named as P6 by the prior pass — **do not touch the pattern before that replay runs** |
| **V4** | Re-run `replay_monitor_rules.py` on the corrected 1,375-log corpus and re-derive every fire rate in `MONITOR_STANDARD.md` §3.5. | **compute: a corpus replay, no solver** | none. **Six adopted rules currently rest on 28% of the evidence with the glob already fixed** |
| **V5** | Positive controls for the 16 never-fired self-audit checks: one planted defect each, asserting the check fires. | **NO COMPUTE** | V1 first, so the controls are written against a report that states its reach |
| **V6** | Give the six bare-`None` `log_signatures` detectors the `{"graded": False}` third state `grade_bounding_episode` already has. | **NO COMPUTE** | a sweep of consumers, since a bare `None` is currently read as clean |
| **V7** | **Hump A4/A5: reproduce the flat residual deliberately, as a negative control.** Two runs at ~16 and ~9 core-min. This is the cheapest way to convert an assumed capability boundary into a measured one. | **compute: ~25 core-min** | a docket proposal, which has never been filed |
| **V8** | Decide A10 explicitly: file the Richardson proposal or record the hump adjoint as declined with its reason. **Either is fine; the present state — a staged script and no proposal — is the one that is not.** | **NO COMPUTE** to record; ~55 core-min to run | director's call |
| **V9** | Correct `DEFECT_REACH_decomposition_cases.md:564`, which owes a re-run on a hump gradient that does not exist. | **NO COMPUTE** | §5.3 above |
| **V10** | `is_idle.sh`: replace the hand-written process list with a positive liveness signal (the job registry `launch_solve.sh` already maintains), and refuse to conclude IDLE when the probe itself failed. | **NO COMPUTE** | **escalated to the chief; never settled inside the family** |

---

## 7. What could not be established

Stated rather than left as silence.

- **Whether the 16 never-fired self-audit checks would fire.** No control was run — running
  one means planting a defect in the lab's records, which is a write this pass is not
  authorized to make. Recorded as *reach assumed*, which is the honest label, not as
  *broken*.
- **Whether A4/A5's flat residual is the same phenomenon as A1's `-9`.** The logs are
  consistent with it and nobody ever tested it. This is V7.
- **Whether attempts exist that left no log at all.** Two are known (A7, A8) because they
  were ledgered. **A third would be invisible to every instrument used here.** The frame
  cannot bound this.
- **The false-negative rate of this ledger's own enumeration.** Four axes were used and
  each missed instruments the others found (§1.1), which bounds the rate below but not
  above. A fifth axis would probably find more. **This ledger's denominator is a lower
  bound, not a census.**
- **Whether `docs/PRODUCT_LIST.md`'s Stage 1 `[-]` is current.** The file is owned by
  another agent and was read but not reconciled against the A6/A10 state described in §5.2.

---

*Compiled read-only. Nothing in this ledger was fixed, and no submission was sent, filed,
or uploaded. `scripts/self_audit.py`, `sdk/tests/test_rank_claim_surfaces.py`,
`closure_challenge_submission_round5/`, `LESSONS.md`, `docs/PRODUCT_LIST.md` and the
campaign records named in the dispatch were read and not modified.*
