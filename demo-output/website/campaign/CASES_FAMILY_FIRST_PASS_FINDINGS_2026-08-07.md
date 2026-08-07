# Cases/Campaigns family supervisor — first-pass findings, 2026-08-07

Written by the standing Cases/Campaigns family supervisor (Fable) under the
SUPERVISION_CHARTER structure, first pass. Three parts: the family-state
blind-spot review, the family-N collection outcome, and the personal
line-by-line check of `sdk/scripts/model_form_batch.py` and the F6b analysis
script. **Every finding below was recorded in this file before any fix was
applied**; the "disposition" line on each says what was then done and what was
deliberately left alone.

Severity scale: HIGH = wrong verdict possible or honesty machinery bypassed;
MEDIUM = record inconsistency or state-loss path, verdicts unaffected on
present evidence; LOW = latent hazard or hygiene.

---

## Part 1 — code findings, `sdk/scripts/model_form_batch.py`

### C1 (HIGH) — family N never reached the pre-registered gate

10 of 12 family-N cells are recorded as
`runner error: coarse: Cd still moving (... peak-to-peak over the last 50
iterations); not defensible as steady`. That text is not this batch's gate: it
is `tmr_verification.py`'s own `_extract_record` raising on a **tail-50
absolute peak-to-peak > 1e-7** (`sdk/workflows/tmr_verification.py:995-997`)
— an absolute settle criterion of exactly the kind the batch design §4.3
rejected in favour of the scale-free S12 test ("the charter's absolute
`SETTLE_TOL = 3e-7` cannot do" what S12 does). The batch's `except Exception`
in `main()` then wrote a `runner error` record with `qoi: {}` and no
`qoi_source`, so the pre-registered gate (exit code, residualControl, S12,
mesh) was never applied, even though **the evidence to apply it is in each
cell's own archive** (`log.simpleFoam` and
`postProcessing/forceCoeffs1/0/coefficient.dat` both present under
`MODEL_FORM_runs/N_*/`). One absurd consequence on the record:
`N_a0_kEpsilon` was excluded for a p2p of **2.52e-07** — under the ladder's
own 3e-7 settle tolerance, and ~0.002% of its Cd.

**Verdict robustness, checked at zero compute before anything was changed:**
spot-checked `N_a0_kEpsilon`, `N_a0_SpalartAllmaras`, `N_a15_kEpsilon` — all
three ran to the 12000 backstop with zero `SIMPLE solution converged`
sentences, so all three fail the pre-registered gate too (`residualControl
not met`); and every N cell shares the 85.70° non-orthogonality grid, which
mesh-gates the entire family regardless (C2). **"Family N: no band" stands
under the real gate. What is wrong is the recorded reasons and the lost
`qoi_if_it_had_counted` values, not the verdict.**

Disposition: recorded here first; `run_cell_N` then fixed to catch the
workflow's `RuntimeError` and still apply `_grade` to the on-disk evidence,
carrying the workflow error as an additional named reason. The 12 existing
N records are left exactly as they stand — superseding them honestly means
`--redo-excluded` re-solves (~18 core-min), filed as a follow-up for approval,
not run.

### C2 (HIGH, design-level) — family N is dead on arrival under its own gate

The TMR-distributed coarse C-grid's max non-orthogonality is **85.70°**
against the Mesh Standard hard gate of 70° that the batch design §4.4 adopted
mechanically. The two N cells that got far enough to be graded
(`N_a10_kEpsilon`, `N_a10_kOmegaSST`) were excluded on exactly this, with
residualControl met and S12 settled — i.e. they were *converged members the
mesh gate refuses*. Since all twelve cells use the same grid family, **no N
cell can ever enter a band as designed.** The design §3 pre-registered the
wake-oscillation hazard but not this one, while quoting a "validated" family-N
baseline from the same grid. Not a code bug: a pre-registration blind spot.
Disposition: recorded; no quiet exemption added. The next design revision must
either move family N to a compliant grid or write a distributed-grid clause
into the pre-registration and defend it against MESH_STANDARD — that is a
design decision, escalated to the chief, not something the runner may decide.

### C3 (MEDIUM) — `--redo-excluded` can destroy a cell's live record

In `main()`, the superseding rename of `record.json` happened **before** the
budget check and the queue gate. A budget stop or queue yield immediately
after the rename leaves the cell with no live record — `--list` reports it
`pending`, and its exclusion history survives only in the superseded file.
State-loss path, no science lost to date (never hit: the only redo pass ran to
completion). Disposition: recorded, then fixed — the rename now happens only
after the budget and queue checks pass.

### C4 (MEDIUM) — family N's solver exit code is invisible to the gate

`run_cell_N` passed a hard-coded `returncode=0` to `_grade`, so gate
criterion 1 ("the solver exited 0") was unverifiable for family N; it held
only because `run_naca_level` raises on a nonzero exit — which then hit C1's
swallow path. Disposition: recorded; the C1 fix routes that raise into
grading with the failure named, which closes the practical gap. The
`returncode=0` remains for the clean path and is now commented as
"guaranteed by run_naca_level's own raise-on-nonzero".

### C5 (LOW-MEDIUM) — the queue gate silently opens when docker fails

`live_solver_containers()` returns `[]` on any `sudo docker ps` failure, so
the yield-to-everything discipline silently disengages exactly when the fleet
state is unknown. Disposition: recorded, then fixed — the failure is now
logged as a blind-gate warning while still proceeding (availability over
deadlock, but visible in `runner.log`).

### C6 (LOW) — "stopped on the backstop" attached to cells that crashed

The exclusion reason `residualControl not met (stopped on the backstop)` was
appended unconditionally, including to the three `B_re1p2e7` FPE cells that
died at ~iteration 45 — they did not stop on any backstop. The verdicts are
right; the evidence wording is wrong in an honesty artifact. Disposition:
recorded, then fixed — the backstop attribution is now conditional on the
last iteration actually reaching the backstop.

### C7 (LOW) — runner-error path leaked run directories

The three N regime run dirs (`~/certonomous-runs/tmr-naca-a{0,10,15}-coarse`)
were left behind because the cleanup `rmtree` sat after the raising call.
Disposition: recorded; the C1 fix moves cleanup to a `finally`. The three
existing leftovers are deliberately kept until the C1 follow-up regrade is
decided — they are evidence.

### C8 (LOW) — the N path dirties tracked case directories

`run_naca_level` stages dictionaries into
`models/tmr/naca0012/a{alpha}/coarse/`, which is tracked; after the batch the
tree holds the **last model run's** dictionaries (realizableKE) over the
committed kOmegaSST baseline, plus an untracked generated `a15/`. Git noise
and a misleading on-disk "validated case". Disposition: recorded; tracked
files restored with `git checkout` after recording (they are regenerated on
every run); `a15/` left untracked; a staging-root change belongs to
`tmr_verification.py`'s owner, not this batch.

### Verified sound, for the record

- `qoi_source` stamping works as designed on the graded path
  (`P_re1e6_SpalartAllmaras` carries `solver log (coefficient.dat absent from
  collection)` and converged on the same S12 test; `N_a10_*` carry
  `coefficient.dat`).
- Band and study generation read `record.json` globs, so superseded renames
  are correctly invisible to `--band`/`--study`; the ledger is an index, not
  an input.
- `history_from_log`'s regex cannot hit the `Cd(f)/Cd(r)` split rows;
  `_scale_freestream` matches only the writers' own `:.8g` literals.
- `_extend_fv_schemes` raises when its marker is missing while
  `_extend_fv_solution` would silently no-op — asymmetric, but a missing
  solver entry fails loudly in simpleFoam and lands in the gate, so no silent
  wrongness path was found.

## Part 2 — code findings, F6b analysis (`campaign/F6b_runs/gate.py`)

### G1 — the self-corrected crossing-count logic is SOUND

The fix (refuse to name separation/reattachment unless there are **exactly
two** skin-friction sign changes; `steady_bubble` flag; nulls otherwise) is
correctly implemented at lines 150-152 and matches `gate_result.json`
(veryfine: 22 crossings, both quantities null) and the results record §4.
Crossing interpolation is a standard linear root with the denominator
guaranteed nonzero when a sign change fired; sorting by x is valid because
the ERCOFTAC hill wall is single-valued in x; the Cf normalisation constant
cannot move a zero crossing.

### G2 (LOW, latent) — an exact-zero sample double-counts one crossing

`np.sign` returns 0 on an exactly-zero Cf sample, producing two diffs (one
crossing counted twice at the same location). Improbable in floating-point
wall shear, and it fails **conservative** — the count leaves 2 and the script
refuses to name, never mislabels. Recorded, not fixed: the script is the
generator of a closed record and is not being edited after the fact.

### G3 (LOW, latent) — no direction check on the first crossing

The script assumes crossing 1 is separation (attached→separated) and
crossing 2 reattachment. True on this case (the crest at x=0 is attached;
the shipped anchor confirms 0.259/7.644) but unchecked — reuse on a case
whose sampled wall starts inside a bubble would swap the labels. Recorded
for the family guidelines (any reuse must add the sign-direction check),
not fixed in place.

## Part 3 — record consistency findings (blind-spot review)

### R1 (MEDIUM) — the 2026-07-29 F6b record still asserts the refuted Re_H identity

`demo-output/website/dafoam/f6b_periodic_hills/F6b_periodic_hills.md:41`
still states `Re_H = Ubar * h / nu` with no correction pointer, while
`F6b_ERCOFTAC_RESULTS.md` §1b indicts "both records" and the product list
says the label error was corrected. The ERCOFTAC pre-registration is
correctly left unedited with the §1b correction pointing at it; the 07-29
record got no such pointer. Disposition: dated correction note added to the
07-29 record (that file already carries three dated corrections; this is its
own convention).

### R2 (MEDIUM) — the TP-500-29494 conflation survives in two secondary records

`F8_MRF_HAND2001_GATE.md` §2 established: TP-500-29494 is **Simms et al.**
(figure-only torque), TP-500-29955 is **Hand et al.** (no torque table), and
the 800 N·m at 7 m/s is secondary-tier (Processes 12(9):1994 Table 6).
`NOT_PASSING_REGISTER.md:529` and `NEXT_CASES_SLATE.md` item 1 still
attribute a published 7 m/s torque table to "Hand et al. ... TP-500-29494".
The proposal's `outcome` field and `CAMPAIGN_STATUS.md` already carry the
correction. Disposition: dated correction notes added to the register and
the slate, pointing at F8 gate §2; original text left in place per the
correction convention.

### R3 (LOW) — the slate re-rounds the Driver–Seegmiller Reynolds number

`NEXT_CASES_SLATE.md` item 3 quotes "Re_H = 37,500" — the exact rounding the
F5c record's own parameters block rejected ("Re_H ≈ 36,000, not the task
brief's rounded Re≈37,500", `F5bc_unsteady_statistics.md`). Cosmetic, but it
re-seeds the drift the record went out of its way to stop. Disposition:
folded into the slate's dated correction note (R2).

### R4 (LOW) — product-list F8 entry leads with its superseded mechanism

`docs/PRODUCT_LIST.md` 4D still opens the F8 item with "MECHANISM FOUND …
the rotor was set spinning AGAINST its power-extracting direction" — refuted
by the §10 STL audit recorded later in the same entry. The entry is
chronological and self-correcting on a full read, but the list's own
convention strikes refuted premises (see the F5c `~~OOM~~` line).
Disposition: reported to the chief — **list custody is the chief's**, this
family does not edit `PRODUCT_LIST.md`.

### R5 (LOW) — F8 gate file's section order ends §17, then §13

Both are titled "Cost, final"; §17 supersedes §13 but sits above it.
Append-only writing produced the order. Harmless, mildly confusing; left
as-is (record files are not reshuffled after the fact), noted here so nobody
"fixes" it silently later.

### R6 (INFO) — F5b's record half still ends in placeholders

`F5bc_unsteady_statistics.md`'s F5b sections "Physics" and "Gate" read
"*to be completed*". Consistent with the open docket item and the slate's
resolve-the-reference-first ruling; the dangling promise belongs to whoever
runs `w1-f5b-pitching-naca0012` and must be closed then.

### R7 (INFO) — family-P exclusion bookkeeping is CONSISTENT

Checked cell-for-cell across `MODEL_FORM_BAND.json`, `MODEL_FORM_BAND.md`
and `models/curriculum/uq-studies/tmr_flatplate_modelform.json`: members,
excluded cells, reasons, band endpoints, spreads, and the CFL3D
contained / FUN3D not-contained flags at re5e6 all agree. The study record
is family-P-scoped by construction (`write_study` filters `family == "P"`),
which matches its title; N adds no band and therefore no study delta.

### R8 (INFO) — pre-existing tree noise, not touched

`models/curriculum/uq-studies/ahmed_25.json` sits modified in the tree with
a timestamp-only delta (`updated_utc`), and an untracked
`F7_runs/F7a_R1/res16_*` sweep (the product list's "loose end", flagged
2026-08-07) belongs to the marine line's triage. Neither is this pass's to
adjudicate; both left untouched.

## Part 4 — family-N collection outcome

The detached run (launched 20:10:20Z, PID 10186) **completed and self-folded
before this pass began**: last cell finished 20:28:32Z, whereupon the runner's
own end-of-loop `write_band()` regenerated `MODEL_FORM_BAND.{json,md}`
(generated_utc 2026-08-07T20:28:32Z, 32/32 cells, 35.61 core-min total;
family N session spend 18.18/60 core-min). All 12 N cells hold `record.json`;
`--list` shows no pending cell. Result: **N_a0 / N_a10 / N_a15 each 0
converged, 4 excluded — family N has no band**, subject to the C1/C2 findings
above about the recorded reasons. Nothing further to collect; the design
document's §8b launch log gets a dated completion entry, and the study record
needs no change (no band to fold). The three leftover run dirs are C7's.
