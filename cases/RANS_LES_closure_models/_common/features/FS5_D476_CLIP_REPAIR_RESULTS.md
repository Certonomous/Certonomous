# FS5 instrument amendment, D476: results and gate grading

**2026-08-23.** Implementation of `FS5_D476_CLIP_REPAIR_PREREGISTRATION.md`,
frozen at commit `bf4956bc`, blob `8fac067cf4a2c19a205df529db6c79bd48e31f3d`.
The freeze was verified before any code was touched: `git rev-parse HEAD:<path>`,
`git hash-object <path>` and `git rev-parse bf4956bc:<path>` all returned that
blob.

**Headline: A1 PASS, A2 PASS, A4 PASS, A3 GATE FAIL.** The A3 failure is
diagnosed below and is NOT caused by this change; it is referred, not loosened.
Under the pre-registration's section 7 no closure build relies on the amended
instrument until the verification-supervisor's audit returns.

---

## 1. What was changed

| file | change |
|---|---|
| `build_features.py` | computes `q1_wallRe_raw = sqrt(max(k,0)) d / (50 nu)`, unclipped; stores it per case under the `.npz` key `D` with names in `diag_names`; manifest gains `diagnostics` + `diagnostics_note` and a per-case `n_diag_nonfinite` |
| `fs2_audit.py` | `read_companion` / `companion_coverage` / `planted_control` / `companion_block`; new JSON block `coverage.q1_wallRe_unclipped_companion`; `frac_at_min` / `frac_at_max` per feature |
| `FEATURE_LIBRARY.md` | dated Amendment 1 appended at the foot, version 1.1 |
| `make_feature_library.py` | **scope addition, see section 6** — carries hand-written amendments across regeneration |

Regenerated outside git: 40 case `.npz` files, `manifest.json` and
`fs2_audit.json` under `/home/ubuntu/closure-data/features/`. The pre-repair
state is preserved at `/home/ubuntu/closure-data/features_backup_pre_D476/`,
including `A2_before.json`, the before-hashes taken before any code was edited.

`q1_wallRe` is now written as `min(q1_wallRe_raw, 2.0)` off the single
`q1_wallRe_raw` expression, so the diagnostic companion cannot drift from the
feature it shadows and their NaN handling is identical by construction rather
than by assertion. Gate A2 proves the refactor is bit-exact.

## 2. Gate A1 — planted control: **PASS**

The control injects a value strictly above every training companion value into
a copy of a TEST case's companion column, writes it to a temporary `.npz`, and
reads it back through `read_companion()` and `companion_coverage()` — the same
path the audit itself uses. It plants into the smallest finite cell, which
cannot already be flagged, so a working reader must show exactly one more
flagged cell.

Live result: case `AR_14_Ret_180`, cell 31818, planted 83.4855
(= 1.5 x the training max 55.657); flagged cells **0 -> 1**; maximum read back
83.4855. Verdict PASS.

**The refusal path was proven live, not merely present.** Two mutations of the
reader were run as subprocesses and the audit's exit status checked:

| mutation | expected rc | observed rc |
|---|---|---|
| unmutated control | 0 | 0 |
| `clipped_reader` — the reader sees only the clipped column (i.e. the D476 defect itself) | 2 | 2 |
| `ignores_disk` — the reader never re-reads the path it is handed | 2 | 2 |

Both mutants exited 2 with the refusal text naming the planted value, the cell,
and the expected-versus-observed flagged counts. A control that cannot fail is
not a control; this one fails when the reader is blinded in exactly the way the
defect blinded it.

The companion instrument also refuses (exit 2) if the companion is absent from
any case `.npz`, rather than degrading to silence — the failure mode being
repaired here was silence.

## 3. Gate A2 — model-facing identity: **PASS**

Before-hashes were taken **first**, before any code was edited. sha256 is over
array content (dtype, shape, C-order bytes), not the `.npz` container.

- **40 of 40** cases: `F` sha256 byte-identical before vs after.
- **40 of 40** cases: per-case `names` list sha256 byte-identical.
- Manifest `features` name-list sha256 unchanged:
  `3a6ea49ad8d20b00090479ab77cc7419189a9a7554009be5a8c340f04e943512`.
- Every `F` remains `float32`, shape unchanged; `.npz` keys went from
  `['F','names']` to `['D','F','diag_names','names']`.

Zero mismatches. The 110-column model-facing matrix is untouched.

## 4. Gate A3 — audit identity up to addition: **GATE FAIL**

`fs2_audit.json` new-vs-old, with `frac_at_min`, `frac_at_max` and
`q1_wallRe_unclipped_companion` stripped, is **not** exactly identical. Six
values differ. All six are the same statistic:

| family | before | after |
|---|---|---|
| POOLED | 3.283683756107853e+17 | 2.3283210207745232e+17 |
| cbfs | 1.9974553177957281e+18 | 2.460895918948894e+17 |
| duct | 1.1668277550363688e+33 | 2.1724294644486465e+33 |
| hill | 2.181588325970533e+17 | 6.432994908028177e+17 |
| hill_breuer | 2.2260848443269914e+17 | 9.627266059057542e+17 |
| hump | 2.849150482633467e+18 | 2.0245029833104083e+17 |

Nothing else moved: every rank, rank deficiency, dead-feature list,
near-constant list, per-feature statistic, FS5 coverage figure and
tensor-basis-rank figure is identical.

**This is reported as a finding, not absorbed, and the gate is not loosened.**

### 4.1 Triage

`singular_value_ratio_first_to_last` is `s[0] / max(s[-1], 1e-300)` on the
column-standardised feature matrix. Every family is rank-deficient (POOLED rank
100 of 110; duct 96 of 110), so `s[-1]` is a singular value that is
**analytically zero**; its computed value is pure rounding noise at ~1e-15
against `s[0]` ~ 7.5e+02. The ratio is therefore a report on the floating-point
noise floor, not on the data.

Four facts fix the cause:

1. **The inputs are byte-identical** — gate A2. The data cannot be the cause.
2. **The baseline is code-fair.** The previous `fs2_audit.json` was written
   2026-08-21 18:01 by `8a380cb9`; the only later commit touching
   `fs2_audit.py`, `fd3aa735`, added four comment lines and no computation.
3. **Repeat runs are bit-identical.** Two back-to-back runs in the same
   environment produced the same six values exactly. The figure is not
   stochastic.
4. **It moves with the OpenBLAS thread count.** On the `hump` family, with the
   input matrix held fixed, `s[0]` agrees to 15 significant digits and the rank
   is 100 at every thread count, while `s[-1]` and hence the ratio do not:

   | threads | s[-1] | s0/sN |
   |---|---|---|
   | 1 | 2.267684039992980e-16 | 3.3123e+18 |
   | 2 | 4.290996083576846e-15 | 1.7505e+17 |
   | 4 | 2.636297439624634e-16 | **2.8492e+18** |
   | 8 | 1.570158387523222e-15 | 4.7837e+17 |
   | 16 | 3.710149199281392e-15 | **2.0245e+17** |

   The baseline's hump value is 2.849150482633467e+18 — the 4-thread value. The
   new run's is 2.0245029833104083e+17 — the 16-thread value.

**Confirmation.** Re-running the amended audit pinned to `OPENBLAS_NUM_THREADS=4`,
the thread count under which the baseline was produced, makes the stripped
new-vs-old comparison **exactly identical: zero differences, canonical-text
identity true.** So the D476 change alters no pre-existing audit value; the A3
mismatch is entirely attributable to the BLAS thread count, which OpenBLAS
selects at run time (`DYNAMIC_ARCH`, `NO_AFFINITY`, `MAX_THREADS=64`, 16 cores)
and which therefore varies with machine load between sessions.

**No thread pinning has been adopted.** Pinning would convert this gate from
failed to passed by changing how the instrument is run, which is not registered
and would be engineering a pass. The delivered `fs2_audit.json` is the
unpinned run. The pinned run was kept as labelled diagnostic evidence only.

### 4.2 What is referred, and to whom

Two questions, neither of them this lane's to settle:

- **Is the statistic fit to be published at all?** `s[0]/s[-1]` of a
  rank-deficient matrix is a condition number of a singular matrix — it is
  infinite in exact arithmetic, and any finite value printed for it is a
  property of the LAPACK path, not of the feature library. A conditioning
  figure that means something would be `s[0]/s[r-1]` over the retained rank.
- **Should the instrument pin its BLAS thread count** so that exact-identity
  gates like A3 are meaningful on this box?

Both are instrument-standard questions for the verification-supervisor, and
changing either is a separate pre-registered decision.

## 5. Gate A4 — frozen-file form: **PASS**

`FEATURE_LIBRARY.md`, 205 lines -> 259 lines.

- **Appended only:** the pre-amendment file is a strict byte prefix of the
  amended file; the first 205 lines are byte-identical. **Lines whose number
  changed above this section: 0.**
- **Version bumped:** Amendment 1 declares document version 1.1 and records
  that the text above was unversioned (version 1.0).
- The amendment states that the companion exists, is a diagnostic, is read by
  the audit alone, and is **not row 111** — the library is still 110 features.

## 6. Scope addition, disclosed

`make_feature_library.py` was changed, which section 3 of the pre-registration
does not list. Reason: `FEATURE_LIBRARY.md` is a **generated** file, and the
generator opens it `"w"` and rewrites it whole. A rule-6 amendment appended to
it would be silently deleted by the next run of the reproduce block printed in
the file's own "Reproducing" section. An amendment that erases itself is not an
amendment, so the generator now carries everything below a marker line forward,
with an assert on both sides of the write.

Proven by round trip: after re-running `make_feature_library.py`, the file is
byte-identical to the amended file, carrying 54 amendment lines forward.

This alters no gate, threshold, cap or label. It is recorded as a dated
addendum at the foot of the pre-registration.

## 7. What the companion measures — the first reading

Training companion range, pooled over the 32 training cases (484,034 cells, 0
non-finite): min 3.68e-10, p50 **2.994**, p99 **32.88**, max **55.657**.

Note what the p50 alone establishes: the median unclipped value is 2.994,
already above the clip of 2.0.

| test case | cells | above training max | worst excursion (training spans) | case max | x training max |
|---|---|---|---|---|---|
| AR_14_Ret_180 | 31,819 | 0 (0.000 %) | -0.9352 | 3.607 | 0.06 |
| AR_1_Ret_360 | 3,025 | 0 (0.000 %) | -0.8674 | 7.379 | 0.13 |
| AR_3_Ret_360 | 8,748 | 0 (0.000 %) | -0.8518 | 8.248 | 0.15 |
| **NASA_2DWMH** | 51,626 | **4,954 (9.596 %)** | **+5.1111** | **340.1** | **6.11** |
| alpha_05_4071_2024 | 15,600 | 0 (0.000 %) | -0.4014 | 33.32 | 0.60 |
| alpha_05_4071_4048 | 15,600 | 0 (0.000 %) | -0.4306 | 31.69 | 0.57 |
| alpha_15_13929_2024 | 15,600 | 0 (0.000 %) | -0.4918 | 28.29 | 0.51 |
| alpha_15_13929_4048 | 15,600 | 0 (0.000 %) | -0.5097 | 27.29 | 0.49 |

No non-finite cells in any test case.

**The reading.** Seven of eight test cases sit inside the training envelope on
this axis. The NASA hump does not: 9.596 % of its cells are above the training
maximum, the worst by 5.1 training spans, reaching 6.1x the training maximum.
The clipped instrument reported this case as in-range on the above-max branch —
by construction, since every value on both sides was pinned at 2.0. That is the
blindness D476 recorded, now measured. It is consistent in direction with the
round-5 Re_y trap, which measured 1.85x and 2.07x excursions unclipped on this
same axis.

**No verdict moves from this.** Per section 5 of the pre-registration and the
chief's clause quoted there, this is instrument information reported beside the
standing verdicts. R4 does not use `q1_wallRe`.

## 8. Saturation scan (N-B38 closure)

`frac_at_min` / `frac_at_max` now sit on all 110 pooled columns. Three features
have `frac_at_max` above 0.1 %:

| feature | frac_at_max | frac_at_min | max |
|---|---|---|---|
| `I3_trW2__A` | 1.0000 | 1.0000 | -0.25 |
| `I3_trW2__B` | 1.0000 | 1.0000 | -0.25 |
| `q1_wallRe` | **0.5784** | 0.0000 | 2 |
| `q4_pgradAlongStreamline` | 0.0006 | 0.0005 | 0.5 |

- **`q1_wallRe`: 57.84 % of all 641,652 pooled cells sit exactly on the clip.**
  This is the size of the blindness D476 identified — the clip is not a rare
  guard, it is the modal value of the column.
- `I3_trW2__A/B` are exactly constant at -0.25 on every cell. This is **not a
  new discovery**: both were already in the pooled `near_constant_features`
  list, and the value is analytic — `tr(W_hat^2) = -||W_hat||^2` and the
  bounded normalisation makes `||W_hat||^2 = 1/4` identically, so both variants
  are constant by construction. The saturation columns corroborate the existing
  flag rather than adding to it.
- Every other bounded feature has `frac_at_max` = 0, i.e. no other hard-bound
  saturation. As the pre-registration's section 8 anticipated, that does not
  settle whether asymptotically-bounded `_b`-form features crowd their bounds
  without touching them (the frac_at_max = 0 with p99 near the bound pattern);
  reading that is the verification-supervisor's audit question, not a repair
  taken here.

## 9. Cost (rule 12)

Registered: estimate 2-6 core-minutes, cap 0.5 core-h (30 core-minutes).

Measured, single process each:

| run | wall s | CPU s |
|---|---|---|
| `build_features.py` (regeneration, 40 cases) | 73.44 | not captured |
| `fs2_audit.py`, delivered unpinned run | 88.57 | not captured |
| `fs2_audit.py`, repeat run (CPU measured) | 35.15 | 105.81 |
| `fs2_audit.py`, pinned-thread diagnostic | 27.72 | not captured |
| A1 refusal proof, 3 subprocesses | 6.64 | not captured |
| `make_feature_library.py` round trip | ~1 | not captured |

- **Registered scope** (one regeneration plus one audit run): 73.44 s wall for
  the build plus 105.81 measured CPU-s for the audit, **~3.0 core-minutes** —
  inside the registered 2-6 core-minute estimate.
- **Total for the item**, including gate grading, the A1 refusal proof, the
  thread sweep and the A3 triage: ~333 s wall across all runs;
  **~10-12 core-minutes gross**, against the 30 core-minute cap. **No overrun.**

`cost_basis`: wall and CPU seconds measured on this box by `/usr/bin/time`; the
core-minute totals for runs where CPU was not captured are **estimated** from
the one measured audit run's CPU-to-wall ratio (~3x, OpenBLAS threading the
SVD), not measured. Dollar figures are not quoted: the box cannot read its own
billing, so any rate is reported-by-owner.

## 10. What this lane could not verify

- **Whether the A3 statistic should exist in its current form.** The triage
  establishes the mechanism; whether to change or retire
  `singular_value_ratio_first_to_last`, or to pin the BLAS thread count, is a
  standards decision and is referred, not taken.
- **Whether the NASA_2DWMH excursion has any consequence for any standing
  result.** It is reported as instrument information only; no re-grading was
  attempted and none is implied by this lane.
- **The `_b`-form crowding pattern** described in section 8, which the
  saturation columns do not resolve.

---

## ADDENDUM 2 — 2026-08-24

**Document version 1.1.** Everything above this line is version 1.0 (the text
above carried no version field). Rule 6: **appended only, nothing above edited.**
**Lines whose number changed above this section: 0** — verified, not merely
asserted: the 290-line pre-addendum body is byte-identical to the committed blob
`b362ea32fe7891b066c3999ba65ee735d201e0e1`, re-checked in the same shell
invocation as this append by piping the first 290 lines through
`git hash-object --stdin`.

Written 2026-08-24T16:05:46Z by a closure lane at the closure-supervisor's direction.
Addendum 1 of this item is the dated addendum at the foot of
`FS5_D476_CLIP_REPAIR_PREREGISTRATION.md` (appended `7e973ba8`); this is the
item's second addendum and the first appended to this results file. It alters
**no gate, threshold, cap or label**: A1, A2 and A4 remain **PASS**, A3 remains
**GATE FAIL**, and FS5 remains a **STANDING GATE, armed**.

### A2.1 The adoption ruling, recorded verbatim

Section 7 of the frozen pre-registration reads "no closure build relies on the
amended instrument before that audit returns." Verification's cross-team audit
pass 6 has returned — `docs/CROSS_TEAM_GATE_AUDIT.md` §25–§34, at commit
`542408f7`, **CANDIDATE** (a verification lane's read; the verification
supervisor's own read governs). The closure supervisor re-derived the audit's
load-bearing findings personally from the delivered artefacts and rules as
follows. The words are the supervisor's, unaltered; line breaks are wrapping.

> ADOPTION BLOCK LIFTED for the unclipped q1_wallRe_raw companion as an
> AUDIT-SIDE DIAGNOSTIC ONLY — 2026-08-24, closure-supervisor, on verification's
> audit pass 6 (542408f7, CANDIDATE) plus the supervisor's own independent
> re-derivation of its A1/A2/A3 findings from the delivered artefacts. Scope of
> the lift, stated so it cannot be read wider: (i) the companion may be read and
> reported by FS5 coverage discharges; (ii) it is never in F, never a feature,
> never a correction, never applied to any prediction (L-219/L-220, charter
> §22.4); (iii) A3 stays GATE FAIL — nothing here re-grades it;
> (iv) `singular_value_ratio_first_to_last` is NOT to be quoted as a number in
> any closure record until a registered instrument decision adopts verification's
> recommendation (a) (rank + smallest singular value against the registered
> rtol; ratio only when s[-1] clears it, else 'unbounded (analytically
> singular)') — that adoption and recommendation (b) (pin threads / gate on
> stored bytes) are standards decisions on Sanaa's desk; (v) if the verification
> supervisor's own read reverses any pass-6 finding, this lift is void and the
> block re-arms without further ruling. FS5 remains a STANDING GATE, armed.

Two consequences are worth stating so no later reader has to infer them. First,
the six differing values of section 4 are **not** re-labelled by this ruling —
section 4's `GATE FAIL` stands exactly as written, and the ruling forbids
quoting the statistic that produced it. Second, the lift is conditional on a
CANDIDATE audit; clause (v) is self-executing, so a reversal by the verification
supervisor needs no further closure ruling to re-arm the block.

### A2.2 Pass-6 residual items that were closure's to repair — discharged here

Pass 6 listed five residual hazards (§31) and two unestablished items (§34),
none of which moves a verdict. Those that are closure's are discharged below.

**§31.1 — the grading record did not cite the triage directory. It is cited
now.** The rc table in section 2 and the thread sweep in section 4.1 are read
from artefacts under **`/home/ubuntu/closure-data/D476_A3_triage/`**, which
holds **eight** files:

| file | bytes | what it is |
|---|---|---|
| `fs2_audit_pinned4.json` | 92,850 | the `OPENBLAS_NUM_THREADS=4` diagnostic run of section 4.1 |
| `fs2_audit_rep2.json` | 92,850 | the back-to-back repeat run of section 4.1 item 3 |
| `A2_before.json` | 12,461 | the gate-A2 before-hashes (a copy; the live original is in the backup directory below) |
| `A2_after.json` | 13,541 | the gate-A2 after-hashes |
| `a1_refusal_proof.py` | 2,553 | the section 2 mutation harness (control / `clipped_reader` / `ignores_disk`) |
| `a3_audit_identity.py` | 2,301 | the section 4 stripped new-vs-old comparator |
| `a3_diagnose.py` | 1,325 | the section 4.1 thread sweep |
| `hash_features.py` | 1,581 | the array-content hasher behind gate A2 |

The pre-repair state is at **`/home/ubuntu/closure-data/features_backup_pre_D476/`**
(already cited in section 1): the 40 pre-repair case `.npz`, `manifest.json`,
the pre-repair `fs2_audit.json`, and `A2_before.json` at its live mtime.

**§31.2 — disclosure attached to that citation: the triage directory's mtimes
date nothing.** It is a `cp` **without `-p`**. All eight files carry
`mtime == ctime` inside `2026-08-23 21:01:32.859738Z`–`21:01:32.865102Z`, a
~5.4 ms batch write, **after** the commit that already reported their contents.
The copy was a correct rescue out of a scratch location that L-186 says gets
wiped, but **no timestamp inside that directory dates any run**, and none is
offered as evidence of when anything ran. The timing evidence in this record
rests on `features/` and `features_backup_pre_D476/`, which carry live mtimes.

**§31.4 — the presentation nit in section 8, corrected here.** Section 8's
sentence "Three features have `frac_at_max` above 0.1 %" sits above a **four**-row
table. The count of three is correct; the fourth row is shown for context and is
**below** the 0.1 % threshold. Re-read from
`/home/ubuntu/closure-data/features/fs2_audit.json`, `per_feature`, by the lane
appending this addendum: `q4_pgradAlongStreamline` has
**`frac_at_max` = 0.0005781950340683112**, i.e. **0.0578 %** of the 641,652
pooled cells (`frac_at_min` = 0.0005485839676335459, `max` = 0.5). Section 8's
table shows it rounded to 0.0006. The three rows genuinely above 0.1 % are
`I3_trW2__A` and `I3_trW2__B` at 1.0000 and `q1_wallRe` at 0.5783727004669198.

**§27.5 and §27.6 / §34 — the thread-sweep rows and the delivered run's thread
count, acknowledged as not artefact-backed.** Of the five rows in section 4.1's
sweep table, only two are corroborated by a preserved artefact: **threads = 4 →
2.849150482633467e+18**, exactly the pre-D476 baseline `hump` value, and
**threads = 16 → 2.0245029833104083e+17**, exactly the delivered value. The
**threads = 1, 2 and 8 rows are transcribed prose with no surviving artefact** —
`a3_diagnose.py` printed to stdout and no stdout was preserved. Consequently the
statement that **the delivered run ran at 16 threads is an inference from that
sweep, not a recorded fact**: `fs2_audit.json` carries no BLAS implementation,
thread-count or numpy field (its top-level keys are exactly `coverage`,
`families`, `n_features`, `per_family`, `per_feature`, `rank_rcond`,
`tensor_basis_rank`, `zero_abs`, `zero_test` — re-read by this lane). **Nothing
load-bearing rests on the three uncorroborated rows.** The diagnosis of section
4.1 is carried by the pinned pair alone — unpinned six differences versus
`OPENBLAS_NUM_THREADS=4` zero differences, both preserved as JSON in the triage
directory — which establishes that the D476 change moved no pre-existing audit
value without needing any particular thread count to be true of the delivered
run. The missing environment provenance is verification's §31.5, and its repair
is recommendation (b), a standards decision (see A2.3).

**§31.3 — `make_feature_library.py`'s carry-forward was guarded only when the
marker was already present. Repaired in the same commit as this addendum.** The
carry-forward of section 6 ran under `if AMEND_MARK in prev:`, so a future
hand-written amendment appended **without** the marker line would have been
silently destroyed by the generator's `"w"` write — the exact failure mode
section 6 exists to repair. The generator now **refuses** rather than
overwrites: when the destination exists and carries no marker, it asserts that
the file has no lines beyond the generated text, and the refusal message prints
the marker line to insert. Nothing about what the generator *generates* changed,
and the guard was proven live in both directions, in a scratch copy, leaving the
repository file untouched:

| case | pre-repair generator | repaired generator |
|---|---|---|
| destination with the marker (the real amended file) | rewrites, byte-identical | rewrites, byte-identical (rc 0) |
| destination = generated body only, no marker, no extra lines | rewrites | rewrites (rc 0) — **no false refusal** |
| destination = generated body + a hand-written amendment, **no marker** | **rc 0, amendment silently destroyed** | **refuses, rc 1, destination unchanged** |

Round trip on the repository file: `FEATURE_LIBRARY.md` sha256
`73068606406878037a11751b8a19ff373ef892d75b201f0ffe2531606de17c5d`, 259 lines,
**identical before and after** re-running the repaired generator (205 generated
lines + 54 carried amendment lines).

### A2.3 What is owed, and to whom

**Owed to verification: nothing.** Every pass-6 item that was closure's to
repair is discharged above; the cost calibration verification asked after is
already ledgered as row **C-6** of `docs/COST_CALIBRATION.md` (registered 2–6
core-min against ~10–12 core-min gross and 3.0 core-min cleaned; ratio 0.75x
cleaned/predicted, 2.5–3x gross/predicted; attribution *misprediction of scope*;
zero waste, zero contention). This addendum's own compute is one generator round
trip and one scratch guard proof, **~0.02 core-minutes**, which adds no ledger
row. `cost_basis`: wall and CPU seconds measured on this box by `/usr/bin/time`;
no dollar figure is quoted, the box cannot read its own billing.

**On Sanaa's desk: two standards decisions, neither closure's to take** —
verification's recommendation **(a)**, publish rank and the smallest singular
value against the registered rtol and print `s[0]/s[-1]` only when `s[-1]`
clears that tolerance, else label it "unbounded (analytically singular)"; and
recommendation **(b)**, pin threads (or record a fixed N and the BLAS
implementation) for any gate whose criterion is exact identity of *recomputed*
floating-point quantities, with the stronger form being to gate on **stored**
primary bytes. Until (a) is adopted by a registered instrument decision, clause
(iv) of the ruling stands: `singular_value_ratio_first_to_last` is not quoted as
a number in any closure record.

**Still open, unchanged by this addendum:** A3's `GATE FAIL`; the `_b`-form
crowding question of section 8 and section 10, which the saturation columns do
not resolve; and the NASA_2DWMH excursion of section 7, which remains instrument
information beside the standing verdicts and re-grades nothing.
