# FS5 instrument amendment, D476: the q1_wallRe clip blindness — pre-registration

**Version 1.0 — 2026-08-23. FROZEN at the commit that introduces this file;
verify by hashing the file that ran against the committed blob (rule 2).**
Author: closure-supervisor. Authority: chief dispatch of 2026-08-23
("D476 q1_wallRe clip repair — DISPATCHED TO YOU, chief-directed"), scope
verbatim: *"the FS5 coverage-instrument blindness on q1_wallRe (clip at 2;
unclipped companion column vs declared exemption per D476)."* Records this
amends: D476, N-B38, COVERAGE.md's carried-forward blindness note.

This is an INSTRUMENT amendment, not a result. It is written under rule 2/6
forms: registered before implementation, and every frozen file it touches is
amended by dated addendum only.

## 1. The defect, restated from the instrument's own lines

`build_features.py:134` defines
`q1_wallRe = min(sqrt(max(k,0)) * dwall / (50 nu), 2.0)`.
`fs2_audit.py:97-104` (FS5 coverage) flags `X > hi` where `hi` is the
per-column training maximum. On this column training max = clip = 2.0 and
every test value is also clipped at 2.0, so the above-max branch is
STRUCTURALLY unreachable: max = p99 = p50 = 2.0 over 641,652 cells
(`fs2_audit.json`, N-B38). The below-min branch is not blind and is not
touched. The round-5 Re_y trap measured 1.85x and 2.07x excursions UNCLIPPED
on exactly this axis — physics leaving the training envelope while the
clipped model input stays trivially in-range.

## 2. The decision (the supervisor's ruling under the chief's dispatch)

**Option (a), unclipped companion column, audit-side.** Rationale: a declared
exemption documents the blindness and measures nothing; the companion removes
it. The companion is a DIAGNOSTIC read by the FS5 instrument only — it is NOT
a feature: the 110-column model-facing matrix `F`, the `features` list in the
manifest, and everything any selection or fit reads are unchanged and must be
proven unchanged (gate A2). The two coverage readings mean different things
and the instrument must label them: the clipped column answers "is the MODEL
INPUT inside the training range" (above-max: trivially yes, by construction);
the companion answers "is the PHYSICS inside the training envelope" — the
question FS5 exists to ask.

## 3. Registered changes (semantics binding; key names are implementation's)

1. `build_features.py`: additionally compute
   `q1_wallRe_raw = sqrt(max(k,0)) * dwall / (50 nu)` (no clip; NaN handling
   identical to q1_wallRe's) and store it in each case `.npz` as a separate
   diagnostic array with its own names list — never appended to `F`, never
   added to the manifest's `features`. Manifest gains a `diagnostics`
   declaration.
2. `fs2_audit.py`: (i) a planted control on the companion reader (gate A1);
   (ii) an FS5 subsection reporting, per TEST case against the TRAINING
   companion range: frac cells above training unclipped max, worst excursion
   in training-span units, and the training unclipped min/p50/p99/max —
   keyed as an `q1_wallRe_unclipped_companion` block whose label text states
   the model input remains clipped and in-range and that this is
   physical-envelope coverage; (iii) per-feature saturation statistics
   `frac_at_min` / `frac_at_max` over the pooled 110 columns — the N-B38
   "whether other bounded features saturate is UNMEASURED" closure. A
   measurement only: it changes no gate and repairs nothing beyond q1.
3. `FEATURE_LIBRARY.md`: dated amendment at the foot, version bump, `lines
   whose number changed above this section: 0` — recording that the companion
   exists, is a diagnostic, and is not row 111.
4. `fs2_audit.json` regenerated; the case `.npz` files under
   `/home/ubuntu/closure-data/features/` regenerated with the diagnostic
   block added.

## 4. Acceptance gates — verdict vocabulary, graded before belief

- **A1, planted control.** Inject a synthetic companion excursion (a value
  strictly above every training companion value, e.g. one cell at
  1.5 x training max) into a copy of a TEST case's companion column and read
  it back through the audit's own path: the reader must flag it. If it does
  not, the audit REFUSES (exit 2). PASS / GATE FAIL.
- **A2, model-facing identity.** For every case: sha256 of the `F` array (and
  of the `features` name list) byte-identical before vs after regeneration.
  One mismatch → GATE FAIL and STOP; nothing is loosened to "close enough".
- **A3, audit identity up to addition.** `fs2_audit.json` new-vs-old with the
  new keys stripped is exactly identical. Mismatch → GATE FAIL and STOP; a
  nondeterminism finding is reported, not absorbed.
- **A4, frozen-file form.** The FEATURE_LIBRARY.md amendment passes the
  rule-6 checks: appended only, version bumped, zero lines renumbered above.

## 5. What this may not do — the chief's clause, verbatim in force

*"No verdict may move retroactively from this repair — if re-grading anything
becomes implied, that is a separate pre-registered decision that goes to
Sanaa, not taken under this dispatch."* If the companion reveals excursions
on already-graded cases, that is reported as instrument information beside
the standing verdicts, which do not move. R4 does not use q1_wallRe; no R4
number is affected (D476).

## 6. Cost (rule 12)

Regeneration of the feature `.npz` set plus one audit run, single core, numpy
and field reads only, no solver. **Estimate 2–6 core-minutes; cap 0.5 core-h
(≈$0.026 at the reported-by-owner $0.0513/core-h).** `cost_basis`:
estimated-from-instrument-class (the prior FS2 audit and COVERAGE.md runs
were 0.5–1 core-minute class), measured wall time to be recorded in the
results addendum. Overrun stops the run.

## 7. Registered process gates

Implementation by one lab-lane. The supervisor reads the full diff personally
before any output is believed (SUPERVISION_CHARTER §3 check 1). The
verification-supervisor is flagged to audit the diff as a cross-team
gate-instrument change; **no closure build relies on the amended instrument
before that audit returns.** Amendments to this file after implementation
begins: dated addenda only, gates unalterable.

## 8. What this registration cannot see

Whether A3 exact-identity survives the numpy version on this box is asserted,
not yet demonstrated (same code path, same inputs, same machine — if it
fails, that is a finding under A3, not a reason to weaken A3). The saturation
scan (§3.2.iii) measures hard-bound saturation only; asymptotically-bounded
`_b`-form features that crowd their bound without touching it are
characterised by frac_at_max = 0 with p99 near the bound, and reading that
pattern is the verification-supervisor's audit question, not a repair taken
here.

---

## Addendum 1 - 2026-08-23, after implementation. Alters no gate.

Version 1.1. The registered text above is untouched: **lines whose number
changed above this section: 0**. No gate, threshold, cap or label is altered by
this addendum; sections 4, 5 and 6 stand exactly as frozen at `bf4956bc`
(blob `8fac067c`), against which the implementing lane hashed this file before
touching any code.

1. **Scope addition, one file beyond section 3.** `make_feature_library.py` was
   also changed. `FEATURE_LIBRARY.md` is a generated file and its generator
   rewrites it whole with mode `"w"`, so the section 3.3 amendment would have
   been silently deleted by the next run of the reproduce block printed inside
   `FEATURE_LIBRARY.md` itself. The generator now carries everything below a
   marker line forward, asserted on both sides of the write and proven by a
   byte-identical round trip. This adds no gate and changes no measurement.

2. **Results and grading** are recorded in `FS5_D476_CLIP_REPAIR_RESULTS.md`
   beside this file. Summary: **A1 PASS, A2 PASS, A4 PASS, A3 GATE FAIL.** The
   A3 mismatch is six values of `singular_value_ratio_first_to_last`, a ratio
   whose denominator is an analytically-zero singular value of a rank-deficient
   matrix; it tracks the OpenBLAS thread count and is identical to the baseline
   when pinned to the thread count that produced the baseline. The gate is
   recorded as failed and referred to the verification-supervisor. It is not
   loosened, and no thread pinning was adopted. Section 8 of the registered
   text anticipated exactly this and ruled it a finding rather than a reason to
   weaken A3; that ruling is followed.
