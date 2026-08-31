# AGE GUARD REFERENT AUDIT — T-family

**Date:** 2026-08-31
**Team:** heat-transfer
**Scope:** every run case under `verification/runs/T-family/`
**Status:** AUDIT ONLY. Nothing is repaired by this document. See section 7.

---

## 0. The question

CLAUDE.md rule 4's strict completion rule ends with the **age guard**: *"every field
at `endTime` NEWER than the case's own `0/T` — the age guard, because `0/T` is
touched last at launch and so dates the run allowed to produce the answer."*

The guard's entire evidentiary content is one file's **mtime**. This audit asks
whether that file is under version control, and if not, whether the omission is a
correctness hole, a designed policy, or a durability limit.

---

## 1. The finding, verified at source

Case `verification/runs/T-family/T20_runs/T20_LC_c`:

| Artifact | mtime |
|---|---|
| `0/cellRegion/T` (the referent) | 2026-08-31 16:45:23.720821218 +0000 |
| `4500/cellRegion/T` (the endTime field) | 2026-08-31 16:45:24.039824073 +0000 |

The endTime field is newer by **0.319 s**. The guard **HOLDS** for this case.

`git ls-files` on that case returns **15 tracked files**. `0.orig/cellRegion/T` and
`0.orig/cellRegion/p` are among them. **No file under `0/` is tracked.** The age
guard's referent exists only on disk.

---

## 2. Family-wide counts (TASK 1)

Enumerated by walking `verification/runs/T-family/`, treating a directory as a case
if it holds `system/` or `constant/` or a `log.solve*`, and as **run** if it holds a
`log.*`, a `STATUS`/`DONE` marker, or more than one numeric time directory. Tracking
was resolved against a single `git ls-files -- verification/runs/T-family` snapshot
(2,759 tracked files) at HEAD `a6ed5e4c`.

**259 run cases** found.

| Population | Count |
|---|---:|
| Run cases with a thermal age-guard referent on disk (`0/T` or `0/<region>/T`) | **213** |
| — referent **UNTRACKED** at HEAD | **209** |
| — referent **TRACKED** at HEAD | **4** |
| Run cases with `0/` but no `T` inside it (guard's referent does not apply) | 45 |
| Run cases with no `0/` on disk at all | 1 |

**The headline count: 209 of 213 run cases with a thermal referent — 98.1% — carry
an age-guard referent that is untracked at HEAD.**

### Referent shape

The referent path varies by rung, as expected for a family that mixes single- and
multi-region cases:

- flat `0/T`: **176** cases
- multi-region `0/<region>/T`: **37** cases (e.g. `0/cellRegion/T` in `T20_runs`)

### The four tracked exceptions

All four are in `T11_runs`, all flat `0/T`:

- `verification/runs/T-family/T11_runs/T11_PW_c/0/T`
- `verification/runs/T-family/T11_runs/T11_PW_f/0/T`
- `verification/runs/T-family/T11_runs/T11_PW_f_CT/0/T`
- `verification/runs/T-family/T11_runs/T11_PW_m/0/T`

For all four the tracked blob's sha256 **matches the file on disk byte for byte**, so
none of them is a stale tracked referent contradicting its own case. Their tracking
appears incidental rather than policy — no other rung shows it.

### The 45 non-applicable cases

`0/` exists but holds no `T`: 34 hold only `viewFactorField`, 10 hold only `U` and
`p`, 1 holds `U k nut omega p`. These are not thermal-field-set cases, so rule 4's
`0/T` referent does not apply to them. They are **excluded from the 213 denominator**,
and that exclusion is stated rather than absorbed.

### The one case with no `0/`

`verification/runs/T-family/T1_runs/P_10k.attempt1_stale` — the directory name
already declares it a stale attempt, and it holds no numeric time directory.

### Untracked by rung (209 cases)

`T1_runs` 77 · `T9a_runs` 15 · `T10a_runs` 13 · `T24_runs` 12 · `T9aH_runs` 10 ·
`T3_runs` 9 · `T20_runs` 8 · `T5_runs` 8 · `T19b_runs` 6 · `T14_runs` 4 ·
`T17_runs` 4 · `T18_runs` 4 · `T23_runs` 4 · `T10aR_runs` 3 · `T10aR2_runs` 3 ·
`T13_runs` 3 · `T16_runs` 3 · `T4_runs` 3 · `T4b_runs` 3 · `T5b_runs` 3 ·
`T8_runs` 3 · `T9aR1b_runs` 3 · `T9aR1c_runs` 3 · `T19_runs` 2 · `T15_runs` 1 ·
`T22_runs` 2

### `0.orig/` is NOT uniformly tracked either

The premise that `0.orig/` is the tracked case definition holds for `T20_LC_c` but
**not for the family**. Of the 213 referent-bearing run cases:

| `0.orig/` state | Count |
|---|---:|
| present and **tracked** | **85** |
| present and **untracked** | **127** |
| absent entirely | 1 |

And of the 209 cases whose referent is untracked, **128 also have no tracked
`0.orig/`**. For those 128 the rebuild source is untracked too — the case cannot be
regenerated from git at all, let alone re-verified. This is a larger gap than the
referent question on its own and is reported here because the audit uncovered it.

---

## 3. The .gitignore answer (TASK 1, last clause)

**No .gitignore rule causes `0/` to be ignored anywhere under
`verification/runs/T-family/`.** There is **no `.gitignore` file anywhere under that
tree** — the eight `.gitignore` files in the repository are at the root,
`.pytest_cache/` (×3), `verification/runs/R4_runs/`, `docs/papers/closure/`, and two
under `verification/runs/F14-cooling-ladder/`. `.git/info/exclude` contains only
`.claude/` state paths.

Verified authoritatively rather than by pattern-reading: `git check-ignore --stdin -v`
was run over **all 209 untracked referent paths** and returned **zero matches**.

**Planted control (rule 3).** A zero from a reader not shown able to see a non-zero is
not evidence. The identical invocation, with two known-ignored paths spliced into the
same stdin list, returned both of them with the matching rule cited:

- `verification/runs/R4_runs/processor0/PLANT` → matched `verification/runs/R4_runs/.gitignore:4:processor*/`
- `verification/runs/D5_rsm_runs/anycase/0/T` → matched `.gitignore:59:verification/runs/*_runs/*/[0-9]*/`

The reader is therefore **proven able to see a non-zero**, and the zero over the 209
real paths is evidence.

### Why the existing policy does not reach the T-family — and what it actually says

The second planted path is instructive. `.gitignore:59`
(`verification/runs/*_runs/*/[0-9]*/`) **does** ignore `0/` — but only where the first
path segment under `verification/runs/` is itself `*_runs`. T-family paths are
`verification/runs/T-family/<rung>_runs/<case>/0/...` — the campaign segment
`T-family` intervenes, and a `*` glob does not cross `/`. The same reasoning is
written into the file itself at lines 148-151 and 235-242, where the author records
that the `*_runs`/`*_work` spelling was chosen **deliberately** so the rules would
**not** reach campaign-segmented trees.

More important, the repository's own written policy on `0/` is **split**, and the
dominant block favours tracking it:

- `.gitignore:161` (K2b block) — *"`0.orig/` is case INPUT and must travel, `0/` and
  every solved time directory are OUTPUT."*
- `.gitignore:183-185` (BATCH 2 block, citing `MOVE_MAP_2026-08-16.md` §7.2) —
  *"Case dictionaries (`system/`, `constant/`) and initial conditions (`0/`,
  `0.orig/`) are source -- they regenerate the run -- while solver time directories
  and solver logs are output."*

And BATCH 2's rules are spelled `[1-9]*/` (lines 243-250), **not** `[0-9]*/` — that
character class excludes `0/` on purpose, so batch 2's ignore rules deliberately leave
`0/` trackable.

**Conclusion on the gitignore question: the omission under the T-family is NOT
deliberate policy.** No rule ignores it; the repository's dominant written policy
classes `0/` as source that should travel; and the T-family's untracked `0/` is an
omission from the tracking sweep, not an exclusion by it.

---

## 4. Is the guard fail-closed? (TASK 3) — THE CRUX

Three comparators were read **and exercised**, each with a two-arm live control. A
guard that silently passes when its referent is missing would be a genuine correctness
hole; a guard that refuses is fail-closed.

### 4.1 `verification/runs/T-family/T3_runs/mark_done_t3.py`

Code (lines 85-86): `if not os.path.isfile(t0): fails.append("no 0/T, so the run's start cannot be dated")`.

Exercised on a scratch copy of case `D_m` with its `STATUS.D_m` alongside, so the run
reaches past the STATUS clause to the age guard.

- **ARM A (control, `0/T` present):** the age guard produced no complaint.
- **ARM B (plant, `0/T` removed):** one **new** fail line appeared —
  `no 0/T, so the run's start cannot be dated`.

The delta between the arms is exactly the age-guard fail line. **FAIL-CLOSED.**

*(An earlier attempt at this test short-circuited on a missing STATUS file and never
reached the clause under test; it was discarded as void rather than reported as a
pass. Recorded because a control that does not reach its clause is worse than none.)*

### 4.2 `verification/runs/T-family/T1_runs/mark_done_t1b_L4.py`

Code (`_fields_and_age`, lines 86-88): the referent's existence is checked explicitly
before `os.path.getmtime` is called, and a missing referent appends
`no {label}, so the run cannot be dated`.

Exercised on scratch copies of its four registered cases with their STATUS files.

- **ARM A (control):** `R_10k_x` reported **`PASS  [ext1 included]`**, as did the other
  three. The comparator is demonstrably able to certify a case, so a failure in ARM B
  is a real flip and not a background failure.
- **ARM B (plant, `0/T` removed from `R_10k_x`):** that case flipped to
  **`NOT DONE  R_10k_x [ext1 present]  - no 0/T, so the run cannot be dated`**.

A clean **PASS → NOT DONE** flip caused solely by removing the referent.
**FAIL-CLOSED.**

### 4.3 `verification/runs/T-family/T20_runs/analyse_t20.py`

Code (conjunct 6, lines 891-893): `if not os.path.isfile(zero): bad.append("conjunct 6: no 0/%s/T, so the AGE GUARD has no datum")`.
`completion()` returns `(not bad, bad, det)`, so any entry in `bad` fails the case.

Exercised by loading the module body up to its `__main__` guard and calling
`completion()` directly on a scratch copy of `T20_LC_c` with a synthetic
`{"endTime": 4500.0, "steps": 750}` — a **structural probe of conjunct 6, not a
grading**, since the frozen document was not used.

- **ARM A (control):** zero conjunct-6 failures, and `det["mtime_0_T"]` **was
  recorded** — proof the guard actually executed rather than being skipped.
- **ARM B (plant, `0/cellRegion/T` removed):** exactly one conjunct-6 failure,
  `conjunct 6: no 0/cellRegion/T, so the AGE GUARD has no datum`, and `mtime_0_T` was
  no longer recorded.

**FAIL-CLOSED.** (A `conjunct 1: no STATUS.T20_LC_c` failure was present in **both**
arms because the STATUS file was not copied; being constant across arms it does not
confound the delta, and it is disclosed rather than trimmed.)

### 4.4 Verdict on TASK 3

**All three comparators FAIL CLOSED. No comparator in the family was found to skip
the age guard, or to treat its clause as satisfied, when the referent is absent.**
There is **no silent-pass correctness hole**.

### 4.5 A noted difference, not a defect

`mark_done_t3.py` and `mark_done_t1b_L4.py` fail a field whose mtime is `< age`
(equal mtimes pass); `analyse_t20.py` fails on `not tf > t0` (equal mtimes fail).
`analyse_t20.py` documents this choice at its lines 1556-1561. Recorded for the
record; it is not part of this audit's question and no change is proposed.

---

## 5. Hazard or design? (TASK 2) — both sides from evidence

### 5.1 The case AGAINST hazard

1. **`0/` is solver-armed run output at launch.** `run_one_t20.sh:186` does
   `cp -r "$CASE_DIR/0.orig" "$CASE_DIR/0"` and `:188` does
   `touch "$CASE_DIR/0/$REGION/T"`. `build_t20.py` writes only `0.orig/` (line 204);
   its own header (line 3) states *"the launcher arms 0/ from 0.orig/ and touches
   0/<region>/T LAST"*. So `0/` is manufactured, not authored.
2. **The referent is regenerable in principle** wherever `0.orig/` is tracked —
   85 of 213 cases.
3. **The guard fails closed under regeneration, measured.** A regenerated referent
   carries a fresh mtime. Exercised: after `cp -r 0.orig/. 0/` and
   `touch 0/cellRegion/T`, `analyse_t20.py`'s conjunct 6 fired with
   *"4500/cellRegion/T is NOT NEWER than 0/cellRegion/T (1788194724.039824 <=
   1788217216.449145) -- the field does not date to the run that was allowed to
   produce it."* Restoration therefore produces a **refusal**, never a wrong pass.
4. **The launcher independently refuses a case that already has `0/`.**
   `run_one_t20.sh:140-145` is a launch guard that exits 2 if `0/` or a numeric time
   directory exists, matching rule 4's *"A guard refuses a case where `0` or a time
   dir already exists."* A restored referent cannot be laundered by a re-launch.
5. **FILING_CHARTER separates inputs from outputs**, and `verification/runs/` is the
   run-output root by CLAUDE.md's own locations table.

### 5.2 The case FOR hazard

1. **After a `git clean`, the referent is gone and an already-graded case can never be
   re-verified against rule 4's sixth clause.** The other five clauses survive in
   tracked artifacts; this one does not. A verdict that cannot be re-checked is weaker
   than one that can.
2. **Regeneration does not restore re-verifiability, it only restores refusal.** By
   §5.1 item 3, a restored `0/` makes the guard *fail*, not pass. The case would then
   read as incomplete forever.
3. **128 of the 209 affected cases have no tracked `0.orig/` either**, so for those the
   referent is not even regenerable.
4. **The omission is not backed by any rule** (§3), and the repository's own dominant
   written policy classes `0/` as source that should travel.

### 5.3 The decisive fact — and it cuts against the repair

**Git does not preserve mtimes.** Measured: `0.orig/cellRegion/T` sits on disk with
mtime `2026-08-31 16:43:05`; the same blob extracted from HEAD via `git archive`
landed with mtime `2026-08-31 22:59:04` — the extraction time.

Therefore **tracking `0/` would not restore the age guard's re-verifiability.** A
referent restored from git carries a checkout-time mtime, exactly as a
launcher-regenerated one does, and would make the guard refuse for the same reason.
Git preserves **content**; the age guard depends on **mtime**, which git does not
carry. The proposed repair does not fix the stated problem.

### 5.4 Which way the evidence falls — stated plainly

**This is a DURABILITY CONCERN ABOUT RE-VERIFICATION, NOT A CORRECTNESS HOLE.**

- Every comparator examined **fails closed** when the referent is missing (§4.4) and
  **fails closed** when it is restored with a fresh mtime (§5.1 item 3). No path was
  found by which the loss of `0/` converts into a wrongly-passed case. Every already-
  written verdict in this family was produced with the referent present on disk.
- What is genuinely lost under a `git clean` is the ability to **re-run the completion
  check on an already-graded case and have it pass**. That is a real weakening of the
  evidence chain and should not be waved away.
- But the obvious repair — track `0/` — **does not cure it** (§5.3), because git does
  not carry the mtime the guard reads. A durable fix would have to record the
  referent's **mtime as data** in a tracked artifact at grading time, not the file
  itself. That is a design change, not a filing fix, and it is not proposed here.

The finding is **not overstated as a correctness hole**, and it is **not dismissed**:
it is a durability limit with a non-obvious cure.

---

## 6. Verdict vocabulary

No gate is graded by this document, so no verdict from the rule-1 vocabulary is
claimed for the family. The one determination made — that all three comparators fail
closed — is a measured property of the code, evidenced in §4 by two-arm live controls.

---

## 7. WHAT IS NOT BEING CHANGED, AND WHY

**Nothing in this audit is repaired.** Specifically:

1. **`0/` is NOT added to git for any case.** Adding run-tree `0/` directories to
   version control is a **filing decision touching run-output policy** and the
   FILING_CHARTER, and it interacts with the split policy already written into
   `.gitignore` (§3). It is not a lane's call to take unilaterally. It is also, on the
   evidence of §5.3, **not the right repair** — it would add tracked files without
   restoring the property that was lost.
2. **No `.gitignore` rule is added, removed or re-pointed.**
3. **No comparator is edited.** All three fail closed as written; §4.5's mtime
   strict/non-strict difference is recorded, not touched. `analyse_t20.py` and the
   `mark_done_*` comparators are under rule 6 (frozen files are never edited) in any
   case.
4. **No `0.orig/` directory is added to git**, though 127 of 213 are untracked (§2).
   That is the larger gap and is referred upward with this document rather than acted
   on.
5. **No file on disk was modified.** All exercising in §4 and §5 was done on scratch
   copies outside the repository; the T-family run tree is byte-identical to its state
   before this audit.

Items 1 and 4 are **referred to the heat-transfer supervisor**, and through them to
whoever owns FILING_CHARTER, as a filing-policy question with a design component.

---

## 8. Honest gaps

- An independent enumeration by a different method (`find` for `system/controlDict`,
  then filtering on the presence of a `log.*`) returns **263** run cases against this
  audit's **259**. The 4-case discrepancy was **not resolved**; it most likely reflects
  the directory-pruning in this audit's tree walk. All per-case figures above are from
  the 259-case enumeration and none of the conclusions turn on the difference.
- The `analyse_t20.py` probe in §4.3 used a synthetic frozen dict and is a
  **structural probe of conjunct 6, not a grading**. It establishes the guard's
  behaviour on a missing referent; it establishes nothing about `T20_LC_c`'s verdict.
- Only three comparators were exercised. Other T-family comparators exist and were
  **not** tested; the claim in §4.4 is scoped to the three named.
- The four tracked `T11_runs` referents were checked for content match against HEAD,
  not for whether their mtimes still satisfy their own cases' guards.

---

*Compute: negligible — no solver was launched. This audit is filesystem and static
analysis only, with three comparator invocations on scratch copies; total well under
1 core-minute, which is below the resolution at which the COMPUTE_BUDGET_CHARTER
requires a costed row.*

---

## 9. RULING ON THE AGE-GUARD REFERENT — 2026-08-31 — heat-transfer supervisor

**Amendment status (rule 6).** This section is **appended**. Nothing above it is
edited, re-numbered or rewritten. **`lines whose number changed above this section: 0`**
— and that assertion is **verified by measurement, not written on faith**: immediately
before this append the file measured **375 lines** with sha256
`4a54ccd4f1e1547196572cc2bfd3e52294ee36e08f6bd2c70bbfdc24e2131660`; immediately after,
`head -375` of the file hashes to that same value. The document above carries no
version field; this is its first amendment and is numbered **v1.1** here.

This section records a **RULING**, not a proposal. §7's "audit only" status stands for
everything above; the determination below is what disposes of §7 item 1.

---

### 9.1 The ruling

**Run-tree `0/` IS NOT TO BE TRACKED.**

The reason is this audit's own decisive measurement at §5.3, **re-verified
independently before this ruling was recorded**: **git does not preserve mtimes.**

| Artifact | mtime | content sha256 (first 16) |
|---|---|---|
| `T20_LC_c/0.orig/cellRegion/T` on disk | 2026-08-31 16:43:05 | `0d653150b8e007c4` |
| the same blob at HEAD | *(git stores none)* | `0d653150b8e007c4` |
| that blob extracted from HEAD, §5.3's measurement | 2026-08-31 22:59:04 | `0d653150b8e007c4` |
| that blob extracted from HEAD, **this ruling's re-measurement** | 2026-08-31 23:06:21 | `0d653150b8e007c4` |

The two extractions disagree with each other by seven minutes and each agrees with the
wall clock at the moment it ran. That is not a discrepancy between them — **it is the
phenomenon itself**: the extracted mtime is the extraction time, and nothing else. The
content is byte-identical in every row.

**The age guard reads MTIME. Git carries CONTENT.**

Therefore **tracking `0/` would not restore what a `git clean` destroys.** A referent
restored from git carries a checkout-time mtime, exactly as a launcher-regenerated one
does.

And it is worse than merely useless. **It would look like a cure and is not one.** A
tracked referent that restores with the wrong mtime buys **false confidence** in
exchange for repository weight, and false confidence in a standing guard is the more
expensive of the two. The repair is refused on that ground, not on the ground of cost.

---

### 9.2 Classification

**This is A DURABILITY CONCERN ABOUT RE-VERIFICATION, NOT A CORRECTNESS HOLE.**

The classification is grounded in the measured fail-closed result, **in both
directions**.

**Absence direction.** All three comparators exercised in §4 with two-arm live controls
**refuse** when the referent is absent:

- `mark_done_t1b_L4.py` flipped **`PASS`** to
  **`NOT DONE — no 0/T, so the run cannot be dated`** (§4.2);
- `mark_done_t3.py` added **exactly one** fail line (§4.1);
- `analyse_t20.py`'s **conjunct 6** raised, and **stopped recording `mtime_0_T`** (§4.3).

**Restore direction — they refuse there too**, because a regenerated `0/` carries a
mtime **NEWER** than the endTime fields. Measured for `analyse_t20.py` at §5.1 item 3,
and **re-measured independently while recording this ruling**, on a scratch copy of
`T3_runs/D_m` outside the repository:

- **control arm** (`0/T` present) — no age-guard complaint;
- **plant arm** (`0/T` removed) — exactly one new line,
  `no 0/T, so the run's start cannot be dated`;
- **restore-the-plant arm** (`0/T` put back) — that line disappears again, so the delta
  is caused by the plant and by nothing else, and the reader is demonstrably live;
- **regeneration arm** (`cp -r 0.orig 0`, then `touch 0/T`) —
  `time 28000 holds fields OLDER than 0/T (T,U,p_rgh,alphat,phi,nut,k,omega) -- not
  written by this run`.

*Disclosed rather than trimmed:* a pre-existing
`20000 ExecutionTime lines, expected 28000` failure was present in **all four** arms of
that re-measurement, so this control never reached a `PASS` and is weaker than §4.2's
clean `PASS → NOT DONE` flip. Being constant across arms it does not confound the
delta, and the appear/disappear behaviour of the age-guard line across the plant and
restore arms carries the finding on its own.

**No path was found by which the loss of `0/` converts into a wrongly-passed case.**
Every verdict already written in this family was produced with the referent present on
disk. That is why this is a durability concern and not a hole.

---

### 9.3 What IS lost — recorded without softening

After a `git clean`, **the completion check on an already-graded case can no longer be
re-run and passed.** The other five clauses of rule 4 survive in tracked artifacts; the
sixth does not, and §5.1 item 3 establishes that regeneration restores only the
comparator's *refusal*, never its ability to certify.

**A verdict that cannot be re-checked is weaker than one that can.**

This ruling does not repair that, and does not present the refusal of the obvious
repair as though the problem had gone away. The weakness is real, it is unfixed, and it
is stated here so that it cannot later be discovered as a surprise.

---

### 9.4 The durable cure — IDENTIFIED, AND NOT TAKEN

The cure that would actually work is **recording the referent's mtime AS DATA in a
tracked artifact at grading time** — committing the number the guard reads, rather than
the file whose mtime git will not carry.

That is:

- **a design change to the completion instrument, not a filing change**;
- a change that **touches frozen comparators**, which rule 6 forbids editing outside a
  dated amendment with its own justification;
- **not taken tonight, and not by a lane.**

It is recorded here as identified so that the next agent to meet this question does not
have to re-derive it, and so that nobody mistakes §9.1's refusal for a finding that
nothing can be done.

---

### 9.5 Scope of this ruling

This ruling disposes of **run-tree `0/` only**.

It does **not** reach `0.orig/`. The larger gap this audit uncovered at §2 and recorded
at §7 item 4 — that of the referent-bearing run cases, a large majority have **no
tracked `0.orig/` either**, so the case cannot be regenerated from git at all — is
**not ruled on here**. `0.orig/` is **case definition rather than run output**, so the
FILING_CHARTER reasoning that keeps `0/` out does not obviously reach it, and
FILING_CHARTER is **not heat-transfer's to amend**. That question is referred to the
chief for routing in
`docs/campaigns/T-family/FILING_REFERRAL_0ORIG_REPRODUCIBILITY.md`.

---

### 9.6 Counts re-derived at this ruling — one figure above does not reproduce

The §2 census was re-derived independently at HEAD `62ceaac0` before this ruling was
recorded, by the method §2 states. Almost all of it reproduces exactly — the four
tracked `T11_runs` referents, the 45 non-applicable cases and their three shapes
(34 `viewFactorField`, 10 `U p`, 1 `U k nut omega p`), the 98.1% headline, the
`0.orig/` split of **85 tracked against 127 untracked**, and the §2 per-rung tally in
**every rung but one**.

Two figures do not reproduce, and §2 is **not** rewritten to match — the divergence is
disclosed here and carried in full in the referral named at §9.5:

1. **`T5_runs`**: §2 tallies **8** untracked thermal referents; the re-derivation finds
   **7**. `T5_runs` holds exactly seven cases with a `T`-bearing `0/`; the eighth
   directory, `X_2d`, has `0/` = `U k nut omega p` and no `T` anywhere beneath it, and
   is already counted in the 45. The consequential figures shift by one:
   **212** referent-bearing, **208** untracked, **127** with neither.
2. **`0.orig/` absent entirely**: §2 records **1**; the re-derivation finds **0** among
   referent-bearing cases. The 38 cases lacking `0.orig/` on disk are all
   `viewFactorField`-only or `reproducer/`, none of them referent-bearing.

Neither figure changes any conclusion in this document, and neither is load-bearing for
§9.1 or §9.2, whose evidence is measurement of behaviour rather than of population.
§8's unresolved 259-versus-263 enumeration discrepancy is **also not resolved by this
ruling**; the re-derivation lands on **263**, the higher of §8's two figures.

---

### 9.7 Verdict vocabulary

No gate is graded by this ruling, so **no verdict from the rule-1 vocabulary is claimed**.
§6 stands unchanged. What is recorded is a disposition of a filing question and a
classification of a finding, both grounded in measurements cited above by artifact.

*Compute: negligible. Filesystem and static analysis, one `git archive` extraction and
four invocations of `mark_done_t3.py` on a scratch copy outside the repository; total
well under 1 core-minute, below the resolution at which COMPUTE_BUDGET_CHARTER requires
a costed row. Estimate-versus-actual (rule 12): pre-registered as negligible, incurred
negligible, ratio ~1 — no calibration row is opened for a sub-resolution spend.*

*No file on disk under `verification/runs/T-family/` was modified by this ruling; the
`mark_done_t3.py` arms ran on a scratch copy, which was deleted, and the T3 run tree was
confirmed byte-identical to HEAD afterwards.*
