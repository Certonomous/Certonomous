# Closure line — §2bc exhaustion-evidence re-audit of standing GATE FAIL / NOT A RESULT

**Owner:** closure-supervisor. **Authority:** VERIFICATION_CHARTER §2bc (Sanaa 2026-09-09,
CHARTER v1.74) + §2ay; classification protocol `verification/EXHAUSTION_REAUDIT_CHECKLIST.md`.
**Date:** 2026-09-09. **Nature:** FLAGS-ONLY. This record moves NO landed number, re-grades
nothing, widens no gate. It classifies each standing `GATE FAIL` / `NOT A RESULT` in closure
territory as terminal-acceptable or premature-and-routed, per the fixed vocabulary
(NON-TERMINAL | EXHAUSTION-PROVEN-TERMINAL(E1) | EXHAUSTION-PROVEN-TERMINAL(E2) | NEEDS-SUCCESSOR
| ESCALATED).

## Population

Enumerated from the landed grade-result records in `cases/RANS_LES_closure_models/` and
cross-checked against `verification/campaign/` and the closure `*.json` artifacts. The closure
line's only standing rung-level graded verdicts in the `GATE FAIL` / `NOT A RESULT` vocabulary
are the two live rows of the **M1 multi-model-sweep arc**; a third grade attempt (M1 original)
landed **BLOCKED** (a distinct vocabulary state, outside the §2bc population) and is recorded
here as the chain root for provenance.

**Instrument blind-spot correction (added after the §2ay sweep ran).**
`scripts/check_completion_enforcement.py` enumerated ZERO closure fails — a DECLARED blind spot:
it reads only its four committed source registers, and the closure line's verdicts live in
per-rung `*_GRADE_RESULT_*.md` and per-case `RESULTS.md` files not in that source list. A disk
sweep of `cases/RANS_LES_closure_models/` surfaced, beyond the M1 arc, **six additional landed
closure fails** in the ML-closure and sparta-build records — classified in the "Additional
population" section below. The §2ay instrument's population is therefore INCOMPLETE for closure;
this is itself owed to verification as a source-list gap (the closure grade-result / RESULTS.md
records should be enumerable).

Not in the population (verified): `planted_zero_verdict` control values inside
`R4_sparta_build/artefacts/fs3.json` are per-feature planted-zero CONTROL results (a control
column within a data artifact), not rung-level terminal verdicts. `M2`, `LR1`, `G2`, `RC1/RC2`,
`Ling arm 2` are PENDING / unfrozen (not landed fails). `R4b-I+R4b` is **BLOCKED (Sanaa)** — a
distinct vocabulary state, not a §2bc fail.

## Classification rows

Format (checklist §4): `id | verdict | completes | classification | numerics-ladder ref |
model/setup rule-out ref | capability rule-out ref | successor ref | note`

### Row 1 — M1d (grade_m1d.py)

- **id:** M1d multi-model sweep regrade (G1 fix) — `cases/RANS_LES_closure_models/M1d_multimodel_sweep_g1fix/M1d_GRADE_RESULT_2026-09-09.md`
- **verdict:** GATE FAIL (governed by G0)
- **completes:** MIXED — 72/78 rows complete; **6 arms do NOT complete** (rc=124 wall-timeout,
  no `20000/` dir). The overall GATE FAIL is **completion-dominated** (G0), with G2/G3 dominated
  by the missing rows (a gate that cannot see all its rows fails rather than passes). G1 = PASS,
  G4 = GATE REACHED — these are the clean results.
- **classification: NON-TERMINAL / has-successor.**
- **numerics-ladder ref:** N-X4 (`docs/NUMERICS_KNOWLEDGE.md:6527`) — the duct-family
  p-initial-residual plateau is a floating-reference NORMALIZATION artifact, not
  non-convergence; iterative convergence judged from continuity + flow-field stationarity. The
  6 incomplete arms are CAP-BOUND (a fixable endTime-cap artifact), not diverging.
- **model/setup rule-out ref:** duct G2-reference provenance established =
  shipped baseline SST RANS field (M1d addendum 2, `a8634d90`); the 0.024 G2 signal is a
  same-model criterion difference, not a precision claim.
- **capability rule-out ref:** n/a for the classification (the fail is not being claimed a
  measured capability limit — the 6 arms are cap-bound and re-runnable).
- **successor ref:** **M1-C** 6-arm completion re-run — `cases/RANS_LES_closure_models/M1c_multimodel_sweep_completion/PREREGISTRATION.md`.
  Prereg + grade path frozen at `84c163bf`, rows finalized `1cabf269`, staging-path AMENDMENT
  (pre-first-compute) at `e738ed43` (L-512); grade path = frozen `grade_m1d.py` (pin `a1ee1905`).
  ACTIVE dated successor, currently HELD on the live Sanaa-via-chief M6 "no new heavy launches"
  hold (LAB_STATE UPDATE 6/7); fires on the chief's M6-clear signal. Zero compute spent.
  **Two documentation-integrity VERIFY items** (do not affect the NON-TERMINAL classification;
  logged for a §3 follow-up): (i) the prereg header STATUS line reportedly still reads DRAFT/NOT
  FROZEN despite the `84c163bf` freeze commit — reconcile the header against the freeze; (ii) the
  M1-C→M1d linkage lives in the prereg's `parent registration` cell and §A.1 grading-path table,
  NOT in a line-leading `Predecessor:`/`Supersedes:` field, so the §2ay recorded-lineage reader
  would not auto-detect it — a line-leading successor field is owed (pre-first-compute, changes
  no gate/threshold/cap/label, rule 2).
- **note:** The GATE FAIL is a completion artifact routed to an active dated successor — exactly
  the §2bc "prove it isn't a fixable numerics/setup artifact" case, and it IS routed. Cite **G1
  PASS** as the win; overall FAIL is completion-limited (verification audit caveat, M1d addendum).
  **E2-EDGE FLAG (not locked):** once M1-C completes all 78 arms, IF a model-accuracy gate then
  still fails, THAT verdict could qualify as an E2 terminal (a genuine model-accuracy miss on the
  closure-challenge line, §2bc.3 E2 / §2an). It CANNOT be locked as E2 now for two independent
  reasons: (a) numerics are not yet exhausted on the 6 arms (M1-C held, not run); and (b) the G2
  reference-field provenance carries a **rule-15 gap** — the upstream duct DNS paper and the
  McConkey closure-challenge paper (arXiv:2603.28884 per benchmark README) are ABSENT from disk,
  so title-page verification of the model-error truth reference is currently impossible (on
  Sanaa's desk, institutional pull). The E1/E2 boundary is itself PENDING Sanaa's confirm
  (§2bc.3 ⚠). Flagged, not locked.

### Row 2 — M1b (grade_m1b.py)

- **id:** M1b multi-model sweep regrade — `cases/RANS_LES_closure_models/M1b_multimodel_sweep_regrade/M1b_GRADE_RESULT_2026-09-09.md`
- **verdict:** NOT A RESULT (G1 arm-application control cannot verify the log channel)
- **completes:** the regrade is a zero-compute regrade of on-disk runs; the NOT A RESULT is an
  INSTRUMENT verdict (§7: G1-fail ⇒ whole sweep NOT A RESULT), not a physics or completion fail.
- **classification: NON-TERMINAL / has-successor.**
- **numerics-ladder ref:** n/a — the cause is not numerics. The verdict is an inherited
  comparator defect **L-509**: `grade_m1b.py:394` MODEL_RE captures the generic
  `Selecting turbulence model type RAS` line before the model-specific line; `.search()` takes
  the first match. The arm WAS applied correctly; the reader mis-read the log channel.
- **model/setup rule-out ref:** n/a — not a model/setup fail; instrument defect, triaged from
  frozen source (§3 check-2, 25th-session board).
- **capability rule-out ref:** n/a.
- **successor ref:** **grade_m1d.py** (the sound successor grader, pin `a1ee1905`) — repairs the
  G1 log-reader; on the fixed reader **G1 PASS (n_bad=0)**, landed as M1d (Row 1). The successor
  is already RUN and its result landed. M1b's NOT A RESULT is fully superseded.
- **note:** A fixable instrument artifact (L-509), routed to and resolved by grade_m1d.py. Not
  terminal. No exhaustion evidence owed (§2bc scope excludes fails with an active/complete
  successor).

### Chain root (for provenance, OUTSIDE the §2bc population) — M1 (grade_m1.py)

- **id:** M1 multi-model sweep grade attempt — `cases/RANS_LES_closure_models/M1_multimodel_sweep/M1_GRADE_RESULT_2026-09-09.md`
- **verdict:** **BLOCKED** — frozen `grade_m1.py` REFUSED (exit 2) at its C1 planted-zero
  control before computing any gate (false-positive refusal, ~half-ULP short of PLANT at
  magnitude 47; L-508). This is the `BLOCKED` vocabulary state, NOT `GATE FAIL` / `NOT A RESULT`,
  so it is outside the §2bc population. Recorded here only as the arc root. Repaired by the C1
  fix inherited byte-identical into grade_m1b.py / grade_m1d.py.

## Additional population — the ML-closure and sparta/omega records (disk sweep)

These six + FS5 are landed closure fails the §2ay instrument did not enumerate (blind spot above).
Classified below by the same protocol. All are on the CLOSURE-CHALLENGE line (product = measuring
model error) except where noted; none carries an `exhaustion_evidence` block, and none has an
active dated successor via a line-leading `Predecessor:`/`Supersedes:` field (verified).

### Row 3 — Kaandorp2020_TBRF (a-priori)

- **id/path:** `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/RESULTS.md` · **GATE FAIL** (all 3
  pre-registered a-priori claims fail: 16-feat 6.382±2.110 WORSE than S,R-only 3.666; 10.9× worse
  than SST 0.584; unrealisable 0.0752, 4.7× truth).
- **completes:** n/a — A-PRIORI on frozen fields, NO solve. **classification: E2-EDGE — FLAGGED, NOT LOCKED.**
- **numerics ref:** vacuous (no solve → no numerics ladder). **model/setup:** the feature-set/model
  form IS the finding. **successor:** the a-posteriori re-solve (Row 4) is the charter-mandated
  re-solution of this a-priori screen.
- **note:** A clean closure-challenge a-priori model-accuracy miss → E2 candidate. NOT locked: (i)
  the E1/E2 boundary is pending Sanaa's confirm (§2bc.3 ⚠); (ii) the closure charter's bright line
  — *a closure is not a result until it has been re-solved* — means an a-priori-only miss is not
  yet a terminal "result"; its re-solve is Row 4, which is NEEDS-SUCCESSOR (broken propagation). So
  the terminal disposition of the Kaandorp closure question follows Row 4's successor, not this row.

### Row 4 — Kaandorp2020_TBRF/aposteriori

- **id/path:** `.../Kaandorp2020_TBRF/aposteriori/RESULTS.md` · **NOT A RESULT** (registered §5
  cascade: H0 truth-injection must cut U_rms ≥30% but U_rms ROSE +62.0% T1 / +57.0% T2 → broken
  propagation path → H1–H3 void).
- **completes:** YES (re-solves ran; G0b null PASS T1 / GATE FAIL T2). **classification: NEEDS-SUCCESSOR.**
- **numerics ref:** n/a. **model/setup:** NOT ruled out — implicated: injecting truth makes the
  solution WORSE, i.e. the propagation harness is broken. **successor owed:** a dated fix-until-runs
  successor that REPAIRS the propagation path before a valid closure can be graded.
- **note:** §2bc requires model/setup be ruled OUT for a terminal fail; here it is the suspect (a
  truth-injection control that fails proves the apparatus, not the model). Correctly a NOT A RESULT
  (not a model miss) — and correctly PREMATURE as terminal. Owed a propagation-repair successor.

### Row 5 — Wu2018_PIML_RF/aposteriori

- **id/path:** `.../Wu2018_PIML_RF/aposteriori/RESULTS.md` · **NOT A RESULT** (ceiling gate failed
  on all 3 cases; ML rows void by pre-registered falsifier 3; kDeficit=0, forest predicts no k).
- **completes:** YES (re-solves ran). **classification: NON-TERMINAL / has-successor.**
- **successor ref:** `.../Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md` (Row 6) — the sibling
  follow-up that froze k to test the k-collapse explanation; substantively the dated successor
  investigation (though not linked via a line-leading `Predecessor:` field — a doc-linkage fix owed).
- **note:** Not terminal — its continuation (frozenk) exists and landed. Out of §2bc terminal scope.

### Row 6 — Wu2018_PIML_RF/aposteriori_frozenk

- **id/path:** `.../Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md` · **NOT A RESULT** (ceiling gate
  failed on both arms/all 3; falsifier fired; voids H1,H2,H3; k FROZEN rules OUT the k-collapse
  explanation — "the k-collapse explanation was incomplete... it still fails").
- **completes:** YES (re-solve with k frozen). **classification: NEEDS-SUCCESSOR.**
- **numerics ref:** n/a. **model/setup:** the k-collapse explanation IS ruled out here (good); BUT
  the ceiling gate fails even on the TRUTH row (from Row 5) — a gate that rejects truth cannot yet
  discriminate model quality, i.e. the ceiling gate / propagation harness is not a validated
  instrument. **successor owed:** a successor that repairs / re-registers the ceiling gate so it
  admits the truth reference, before a NOT A RESULT here can stand as terminal.
- **note:** End of the current Wu chain (Row 5→Row 6), but it terminated on an instrument/gate
  question (truth-fails-ceiling), not a proven-exhausted model miss. Premature as terminal → owed a
  gate-validation successor. E2-EDGE only IF the ceiling gate is first shown to admit truth; flagged.

### Row 7 — R4_sparta_build

- **id/path:** `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` · **GATE FAIL** (a-priori
  b_rms bar: SpaRTA-class model beats train-mean in only 2 of 4 families, needed ≥3; both registered
  halves fired; the NOT A RESULT branch did not fire).
- **completes:** the GRADED metric is a-priori b_rms (no solve for the graded quantity). **classification: NEEDS-SUCCESSOR.**
- **numerics ref:** partial rule-out present — G3 continuity ≤1e-4 gate + realisability §4.6 +
  `docs/closure/R5_CONSTRAINTS_DISCHARGE_RECORD.md`; BUT `AR_1_Ret_180` ceiling 1.0628e-04 is NOT
  CONVERGED (a dimensional-threshold caveat noted). **model/setup:** the SpaRTA model form is the
  thing tested. **successor owed:** a FROZEN R5 successor prereg — the candidates (A/B/…) in
  `docs/closure/R5_DECISION_MEMO.md` are costed but UNREGISTERED (zero-compute, nothing frozen).
- **note:** A-priori closure-challenge model miss → E2-EDGE candidate. NOT locked: an active
  decision-routing (R5 memo) is open and one case is not converged (numerics not fully exhausted).
  Premature as terminal until R5 freezes a successor (or R5 concludes the model form genuinely
  misses with numerics exhausted → then E2). Flagged.

### Row 8 — R5C_omega_repair

- **id/path:** `cases/RANS_LES_closure_models/R5C_omega_repair/RESULTS.md` · **GATE FAIL** (G1
  identity on R4's 12 targets: max rel L2 kDeficit 1.1848e-04 > ≤1e-6 band on `alpha_10_12000_4048`,
  AND 3 of 12 not CONVERGED under G3; §3.1 rule 2: G1 fail → GATE FAIL, G4 never converts to PASS).
- **completes:** MIXED — the omega-clip (Patankar-split source) repair made 10 of 15 previously-
  INCOMPLETE hills COMPLETE; 10 of 27 converged; 15 hills remain INCOMPLETE. **classification: NEEDS-SUCCESSOR.**
- **numerics ref:** R5C IS itself the numerics-repair record (omega-clipping) +
  `R5_CONSTRAINTS_DISCHARGE_RECORD.md` — but the ladder is NOT exhausted: **3 of 12 not CONVERGED**
  (Roache rule-5: those rows are NOT A RESULT) and 15 hills still incomplete. **successor owed:** a
  successor that drives the 3 non-converged / 15 incomplete rows to convergence before the identity
  fail can stand. Same unregistered `R5_DECISION_MEMO.md` route.
- **note:** A live numerics/convergence question, not an exhausted finding — premature as terminal.

### Row 9 — FS5 D476 clip-repair (A3)

- **id/path:** `cases/RANS_LES_closure_models/_common/features/FS5_D476_CLIP_REPAIR_RESULTS.md`
  (prereg frozen `bf4956bc`, blob `8fac067c`) · **A1 PASS, A2 PASS, A4 PASS, A3 GATE FAIL** (A1
  planted control 83.4855; A2 bit-exact refactor identity, 40/40 F sha256 identical; A3 is the gate
  that fired). Instrument/feature-clip REPAIR record; a-priori/identity gates, no solve.
- **completes:** n/a (no solve). **classification: NON-TERMINAL (FS5 is a STANDING GATE).**
- **note:** FS5 is a STANDING GATE, permanently re-armed and never a terminal entry by design (my
  mandate; charter). The A3 fail is on the D476 clip-repair's own registered gate (owed a repair-
  successor within the standing gate), NOT on FS5's standing gate. SEPARATE STANDING CONCERN flagged
  (out of §2bc terminal scope): per `MATRIX_CONTRIBUTION §273` / `COVERAGE.md §5`, FS5's own standing
  gate carries NO number ("declared factor never declared, met zero times"; refuses to invent one
  post-hoc) — an unfalsifiable-standing-gate design issue that §2bc does not reach and that belongs
  to the FS2/FS5 standing-gate review, not this terminal-acceptability pass.

## Summary

| id | verdict | completes | classification | successor / owed |
|---|---|---|---|---|
| M1d | GATE FAIL (G0/completion-dominated) | 72/78 | NON-TERMINAL | M1-C (frozen `84c163bf`, held on M6) |
| M1b | NOT A RESULT (G1 defect L-509) | n/a (regrade) | NON-TERMINAL | grade_m1d.py (run, landed) |
| M1 | BLOCKED (C1 L-508) | grade refused | outside population | — |
| Kaandorp a-priori | GATE FAIL (×3 a-priori) | no solve | **E2-EDGE (flagged)** | re-solve = Row 4 |
| Kaandorp aposteriori | NOT A RESULT (H0 propagation) | yes | **NEEDS-SUCCESSOR** | propagation-path repair prereg |
| Wu aposteriori | NOT A RESULT (falsifier 3) | yes | NON-TERMINAL | frozenk sibling (Row 6) |
| Wu frozenk | NOT A RESULT (ceiling vs truth) | yes | **NEEDS-SUCCESSOR** | ceiling-gate validation prereg |
| R4 sparta | GATE FAIL (a-priori b_rms) | no solve | **NEEDS-SUCCESSOR** | frozen R5 successor (memo unregistered) |
| R5C omega_repair | GATE FAIL (identity + 3/12 unconverged) | mixed | **NEEDS-SUCCESSOR** | convergence-completion prereg |
| FS5 D476 A3 | A3 GATE FAIL (clip-repair) | no solve | NON-TERMINAL (standing gate) | clip-repair successor |

**Tally.** Standing closure fails: 9 rows in vocabulary (M1 BLOCKED excepted). Classified —
**4 NON-TERMINAL** (M1d, M1b, Wu-aposteriori, FS5), **4 NEEDS-SUCCESSOR** (Kaandorp-aposteriori,
Wu-frozenk, R4-sparta, R5C-omega), **2 E2-EDGE flagged not-locked** (Kaandorp-a-priori; and M1d's
eventual full-sweep disposition, Row 1 note; R4/Wu-frozenk carry conditional E2-edge notes).
**0 rows locked EXHAUSTION-PROVEN-TERMINAL** this cycle → no `exhaustion_evidence` machine-readable
block is owed yet; `scripts/check_exhaustion_evidence.py` has no terminal closure row to gate.

**Owed successors (fix-until-runs, §2ay state-(b)) — routed, NOT run this cycle (heavy work held):**
(1) Kaandorp-aposteriori — propagation-path repair; (2) Wu-frozenk — ceiling-gate validation
(admit the truth reference); (3) R4-sparta — freeze an R5 successor from the `R5_DECISION_MEMO.md`
candidates; (4) R5C-omega — drive the 3 non-converged / 15 incomplete rows to convergence. The R4
and R5C successors converge on the single R5 decision (currently unregistered candidates) — one
frozen R5 prereg discharges both. None launched (M6 hold + zero-compute cycle).

**E2-EDGE items flagged, NOT locked** (chief's instruction + §2bc.3 ⚠ pending-boundary): the
closure-challenge model-accuracy misses (Kaandorp a-priori; the eventual M1-C full sweep; a
numerics-exhausted R4/Wu-frozenk disposition) COULD become valid E2 terminal findings — the
line's product — but are not locked because (a) the E1/E2 boundary awaits Sanaa's confirm; (b) the
closure charter's bright line requires re-solution and the re-solves are NEEDS-SUCCESSOR; and (c) a
rule-15 provenance gap blocks the G2/M2 model-error reference (absent upstream papers — Shih 1995,
Craft/Launder/Suga 1996, the McConkey closure-challenge paper arXiv:2603.28884, the Vinuesa-lab
duct DNS — all on Sanaa's desk for institutional pull).

---
*Filed 2026-09-09 by closure-supervisor. Cross-check: the §2ay population sweep
(`scripts/check_completion_enforcement.py`) is the authoritative enumerator; if it surfaces a
closure fail not rowed above, this record is amended by a dated addendum (originals struck, never
rewritten — CLAUDE.md rule 6 / §2b).*
