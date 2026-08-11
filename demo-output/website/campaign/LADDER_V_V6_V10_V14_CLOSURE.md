# Ladder V — closing V6, V10 and V14's stale list

**Executed 2026-08-10 23:37 UTC → 2026-08-11 00:20 UTC (clock, `date -u`, run before any
date was written; the date rolled over mid-pass and the notes written either side carry
the date that was true when each was written — see §6, P43).**

Owner: an agent that had written to none of the surfaces below. **Zero scoring calls; the
ledger stands at 6.** Nothing was sent, emailed, uploaded or filed. Nine commits, every
one a single-step pathspec commit; no bare commit was made, because six agents are live in
this repository.

---

## 0. FRAME, STATED BEFORE ANY COUNT

Every count below is worthless without its frame, so here they are first.

- **"my eight"** means V14 stale-list ranks **4 and 6–11** — eight files. Ranks 1–2 (the
  shipping bundle and its gitignored mirror) were rebuilt and verified by another agent
  before this pass; rank 3 (`LAPTOP_SHOOT.md`) is Katie's shoot script and hers to change.
  **I did not touch `dist/`, `LAPTOP_SHOOT.md` or `latex/*.tex`.**
- **"STALE"** means an old number **presented as current**. **"HISTORICAL"** means an old
  number correctly labelled as history — *correct, and vandalism to "fix"*. The judgement
  is made per hit, not per file: one file can carry both.
- **"verified"** means I read the primary artifact myself in this pass. Where I read
  another pass's measurement instead, the row says so and names whose it is.
- **Reach.** Every sweep uses `/bin/grep` directly — never this lab's ignore-honouring
  wrapper — with `--exclude-dir=.git`. No claim below rests on a compressed log; had one,
  `zgrep` would apply. **Every negative carries a positive control**, recorded at the row
  that depends on it.
- **What this frame structurally cannot contain.** It cannot see uncommitted work in the
  other live agents' trees. **The corpus moved under me three times** in the window
  2026-08-10 23:37 → 2026-08-11 00:23 UTC — `c1ebfb4f`, `39d22bab` and `d9552d73`, all by
  agents other than me, counted with `git log --since` and filtered against my own nine
  hashes rather than eyeballed — and one of those peers audited my first six commits while
  I was still writing the last three; credited in §6 rather than claimed here. It cannot adjudicate whether
  an artifact is *itself* right; only whether the sentence matches it. It cannot read a
  number rendered into a PNG, which is V14's own §6.1 limit and is unchanged by this pass.

---

## 1. THE EIGHT JUDGEMENTS

### Rank 4 — `demo-output/website/CLOSURE_RANK1_CAMPAIGN.md` — **STALE** (`5af41163`)

**Why STALE and not HISTORICAL.** The document is dated (*"Drafted 2026-08-05"*) but the
sentence is not: §1 opens *"Our entry of record is round 4, **0.065438**"* in the present
tense, with no supersession note, and the plan's per-case table and its *"today (round 4)"*
scenario row repeat it. A dated document does not date its own sentences — a reader who
opens at §1 meets a present-tense claim about where the lab stands. Round 4 held that
status until **2026-08-07**.

**Changed:** a dated supersession banner at the head. **The plan's body is untouched** —
the −0.005913 deficit, the per-case gaps, the route pricing. Those *are* the reasoning that
produced the round-5 decision; re-basing them onto round 5 would rewrite a plan into a
report of its own outcome and destroy the record of what was decided on what evidence.
Because the banner states *"rank 1 of 5 scored locally"*, it carries the rank companion in
full: **P(rank 1) = 68%**, the **2–100% at 95%** interval, the undecided pairs (Reissmann
t = −0.50, Wu & Zhang t = −0.95) and the decided ones (Liu 98.7%, Montoya 99.8%).

**Verified, and one number deliberately left wrong-looking.** `0.065438` is **not** the
full-precision round-4 overall. Round 4 is `0.06543140783850523`
(`closure_challenge_trained_entry_round4_duct.json`). `0.065438` is the mean of the eight
**rounded** per-case values — I computed it: `(0.0501+0.1011+0.0461+0.0719+0.0811+0.0775+
0.0325+0.0632)/8 = 0.0654375`. §1 states that construction itself (*"Both reproduce from
their per-case columns exactly"*) and uses it against Reissmann's `0.059525`, which is
built the same way. **Correcting it would break the like-for-like comparison the section
rests on**, so it is recorded in the banner instead. It is the same construction Pass 2
flagged at claim C8 against the word *"published"*.

### Rank 5 — `closure_eval/closure_eval_master_table.md` + `.json` — **STALE** (`dc13f1cc`)

**The hard call of the eight.** The row *is* labelled — `ours, round 4 (recorded, not
submitted)` — and a label is exactly what makes a superseded number true. On the label
alone it would be HISTORICAL. It is STALE because of where the label sits: the document
titles itself **master statistics table**, and its §A is headed *"The public leaderboard,
as published"* with our row inside the board. A reader takes that row as the lab's standing,
and no supersession note anywhere told them otherwise.

**And the number was frozen in a derived output.** `0.0654` is hard-coded in the generator,
`sdk/scripts/closure_eval_battery/build_master_table.py` — twice: once as the row, once in
the sentence *"nothing here changes the recorded 0.0654"*. **Patching the document alone
would have regenerated the stale claim on the next run**, which is the exact failure mode
V14 §4 named ("a derived surface outliving its source"). The note therefore goes in the
**generator**, and both outputs are re-derived from it.

**Verified by running the generator, not by inspecting it.** `build_master_table.py` was
run into a scratch `OUT_DIR` (patching `bmt.bc.OUT_DIR`, the exact module object the script
dereferences), before and after the edit:

- **Before:** the scratch output is byte-identical to the committed `.md` except the
  assembly-date line, and the `.json` identical except `generated_at`. That establishes the
  generator as these two files' source of truth.
- **After:** the diff is exactly the supersession note and the `round-4 0.0654` correction.
- The committed files are then the **generator's own emission** with the original
  2026-08-05 assembly stamp restored — not a hand-patch that could drift back. Re-running a
  third time reproduces the committed files exactly, stamp excluded.

*(An earlier attempt at this harness patched the wrong module object — dual import paths
gave two `battery_common` modules — and wrote into the repository. Caught immediately by
`git status`, reverted with `git checkout`, and the harness was fixed to patch `bmt.bc`.
Recorded because a verification harness that writes to what it measures is a defect even
when the diff is reverted.)*

### Rank 6 — `sdk/scripts/export_closure_submission_csvs.py` — **STALE**, and worse than listed (`4381d634`)

Line 6: *"The lab's **round-3 entry of record** (overall 0.0676…)"* — a present-tense status
claim on a superseded round, in a live script. Scoped to the date it was true (2026-07-30)
with the supersession chain named. The file already carried exactly this treatment at line
25 from the 2026-08-08 pass; the two are now consistent.

**What checking the output found.** The brief says a generator that emits a stale number is
worse than a document carrying one, so I read what this script *writes*: at line 412 it
writes *"reproducing the **round-3 gated entry of record**"* into
`closure_challenge_submission/MANIFEST.json`. **V14 listed the docstring only.** A docstring
misleads a reader of the script; the manifest string is a claim on an artifact. Both fixed.

### Rank 7 — `sdk/scripts/closure_round4_manifest.py:116` — **STALE** in the generator, **HISTORICAL** on disk (`4381d634`)

The generator writes *"round 4 (**the entry of record**, overall 0.0654)"* into the round-4
manifest. The round label is correct and stays — the manifest *is* round 4 — and only the
status parenthetical is scoped, to *"the entry of record until 2026-08-07"*.

**The two manifests already on disk are NOT touched, and that is a judgement.**
`closure_challenge_submission/MANIFEST.json` is stamped `2026-07-30T18:58:52Z` and
`…_round4/MANIFEST.json` `2026-08-05T15:08:42Z`. On those dates each claim was true. They
are dated round-scoped artifacts whose whole purpose is to hold their round's numbers —
V14 §3.2 classes them HISTORICAL — and **rewriting a dated artifact's text while keeping its
date would forge the record rather than correct it.** The generators are what would emit
the claim as true *today*, and those are fixed.

**Both scopings are written to survive a re-run**: they state when the status *ended*, not
when the file was written, so a later regeneration cannot falsify them the way a "when this
was written" phrasing would.

### Rank 8 — `demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md:380` — **STALE** in one word, and a second finding beside it (`a3a4ab3a`)

*"nothing here changes **the recorded** 0.0654"* — the definite article makes a superseded
number *the* record. Corrected to *"the recorded **round-4** 0.0654"*. The section is a
correct dated report of what the battery measured on the round-4 fields and is not rewritten.
**The same sentence is emitted by `build_master_table.py`** and was corrected there in
`dc13f1cc` — fixing only the document would have left the generator regenerating it.

**The larger finding, which V14 did not list.** The same paragraph says our submitted
corrected duct fields violate continuity *"at **2.3–3.4%**"*. Round 5 replaced all three
duct predictions with an untrained QCR forward solve. Measured
`rms div U / rms grad U`, from `closure_challenge_round5_qcr_forward.json`
`/arms/{case}_qcr/div_over_grad`:

| submitted duct | round-5 value |
|---|---|
| `AR_1_Ret_360` | 8.5×10⁻⁴ (`0.00085136`) |
| `AR_3_Ret_360` | 5.3×10⁻⁴ (`0.00052808`) |
| `AR_14_Ret_180` | 5.4×10⁻⁴ (`0.00054396`) |

Two orders of magnitude better. **A number that overstates a defect of our own entry is
still a stale claim**, and it sits in the section a reader goes to for exactly that
question. Handled by a dated additive note, because 2.3–3.4% is a correct measurement of
the round-4 fields and deleting it would destroy the finding it records.

**The note names the three submitted cases individually and states that `AR_7_Ret_180`
(5.8×10⁻⁴) is the VALIDATION duct and is not in the submission.** That is V15's finding F1
exactly — a validation case's number offered as the submitted files' number, in the
flattering direction — and quoting the range without naming the arms is precisely how F1
happened. `filecmp` over the two submission directories, run in this pass, confirms 5 of 8
CSVs byte-identical and exactly the three ducts changed, which is what makes the note's
"hills and NASA unchanged" clause true.

### Rank 9 — `docs/NUMERICS_KNOWLEDGE.md:560` — **STALE** in one word, plus a **STOP AND REPORT** (`79f4529c`)

*"beats our **current** 0.0741 on the PH-only sub-score"*. Round 2 was the entry of record
when this reading round was logged (2026-07-28), so the number is right and only *current*
is wrong. Corrected to *"our round-2 0.0741"*, with the current entry of record named.

**Reported, not fixed, because the repair would change MEANING rather than accuracy.**
`0.0741` is round 2's **overall across all eight cases**. Round 2's **PH-only** sub-score is
**0.080225** — the mean of `0.0501 / 0.1011 / 0.0723 / 0.0974`, computed here from
`closure_challenge_trained_entry_round2.json`. **The gate names a PH-only comparison and
states an overall bar.** Moving the bar to 0.080225, or deleting *"PH-only"*, changes which
experiment the gate is. So both candidate bars are written into the entry (0.080225 at
round 2; **0.0673** on the current entry, with the caveat that two of those four rows are
the supplied baseline the decline gate passed through untouched) and the choice is left to
its author. **A silent re-point would have been the worst available outcome**: it would have
looked like a currency fix and would quietly have redefined a research gate nobody reviewed.

### Rank 10 — `closure_challenge_C2_error_decomposition.md:136` — **STALE by omission** (`249b611c`)

The row read `**ours (unsubmitted)** | **0.0741**` with **no round label**, under the heading
*"Where we actually stand"*. §1 scopes the whole document to round 2; the table does not,
and a table is read on its own. The label is added; a dated note names the three rounds
since (0.0676, 0.0654, 0.056647). **The *"between rank 3 and rank 4, 0.0004 off rank 3"*
reading is left exactly as written** — it is round 2's, it is the finding the decomposition
exists to record, and re-basing it would delete the deficit the document was built to explain.

### Rank 11 — `agenda/LIBRARY_ACCESS_LIST.md:249` — **STALE** (`249b611c`)

*"citable wherever the lab explains what 0.0654 means"*. The claim is that a benchmark
README quotation is citable; the score is illustration, and pinning it to a round was never
part of what the sentence asserts. Rewritten **round-free** (*"what its overall score
means"*) with both the current `0.056647` and the superseded `0.0654` recorded in the note —
so the sentence cannot go stale again on the next round.

### Summary of the eight

| rank | surface | judgement | what changed |
|---|---|---|---|
| 4 | `CLOSURE_RANK1_CAMPAIGN.md` | **STALE** | dated supersession banner; body and arithmetic untouched |
| 5 | `closure_eval_master_table.md` + `.json` | **STALE** (label correct, presentation not) | note added **in the generator**, both outputs re-derived and verified by re-running it |
| 6 | `export_closure_submission_csvs.py` | **STALE** | docstring scoped **and** the manifest string it emits, which the rung had not listed |
| 7 | `closure_round4_manifest.py` | **STALE** (generator) / **HISTORICAL** (on-disk manifests) | status parenthetical scoped in the generator; dated manifests deliberately untouched |
| 8 | `CLOSURE_EVALUATION_PROTOCOL.md` | **STALE** | one word, **plus** a dated round-5 note on a duct measurement that no longer describes the submission |
| 9 | `docs/NUMERICS_KNOWLEDGE.md` | **STALE** (word) + **STOP-AND-REPORT** (meaning) | *current* → *round-2*; the PH-only/overall mismatch reported with both bars computed, not repaired |
| 10 | `closure_challenge_C2_error_decomposition.md` | **STALE by omission** | round label on the row; the round-2 reading left standing |
| 11 | `agenda/LIBRARY_ACCESS_LIST.md` | **STALE** | rewritten round-free with both values recorded |

**Two findings V14's list did not contain**, both found by asking what a generator
*produces* rather than what it says: the round-3 manifest purpose string (rank 6) and the
2.3–3.4% duct figure (rank 8). **One finding refused**, and refused loudly (rank 9).

---

## 2. V15's TWO ITEMS

### F7 — four external surfaces, non-compliant with the rule their own commit adopted (`656c09c9`)

`benchmarks.html`, `benchmarks.json`, `wall/wall.json` and `build_benchmarks.py` each made a
rank claim, each carried the sweep token, and **none carried P(rank 1) or its interval**.
Commit `92562841` both adopted *"any rank claim, internal or external, carries P(rank 1) and
its interval"* and edited all four without applying it. Pass 2 called it a follow-on item;
V15 disagreed and V15 is right — **a pass that edits a surface after a rule changes is that
surface's most recent author.**

All four now carry **P(rank 1) = 68%** and that an eight-case sample **cannot pin it tighter
than 2–100% at 95%**. The undecided pairs were already present and are unchanged. The figure
appears on none of the four without its interval, which is the one prohibition the
2026-08-10 reversal added.

**Verified key-by-key, not eyeballed.** The generator's literal is the single source for the
JSON text, so both JSONs were rewritten **from** the literal: `our_entry` in
`benchmarks.json` and `wall/wall.json` is byte-equal to `build_benchmarks._CLOSURE`, and
`target_rank` / `target_overall` / `target_per_case` / `our_score` / `our_per_case` all
match. The three strings `sdk/tests/test_mega_batch.py` requires survive, the em-dash
prohibition holds, and that suite passes **14/14**.

**A guard, because a rule that binds surfaces needs a check that reads a surface.**
`scripts/self_audit.py`'s closure guard now fails the wall if `our_entry` says *rank 1*
without `P(rank 1)`, without a 2–100% interval, or without the sweep token. **Four positive
controls**, run against an in-memory copy of the wall so the file was never touched:

| injected | expected | result |
|---|---|---|
| figure stripped | FAIL | **FAIL** |
| interval stripped | FAIL | **FAIL** |
| sweep token stripped | FAIL | **FAIL** |
| rank claim removed entirely | PASS | **PASS** |
| unmodified | PASS | **PASS** |

The last two matter as much as the first three: a guard that fires on text carrying no rank
claim is the false positive that gets a guard deleted.

### F9 — a sweep claim that was false where a positive control would have shown it (`63009dd3`)

Pass 2's C9 read *"Swept the corpus for `comfortab*`: **every occurrence in the closure line
is the prohibition**"*. **The verdict was right and its evidence was false**, so the evidence
is corrected in place and the PASS left standing — struck, not deleted, matching the
treatment finding F1 already received at C6 in the same table.

Re-swept, `/bin/grep -rniI "comfortab" --exclude-dir=.git .`: **76 hit lines tree-wide, 59
under `demo-output/website/`, 15 in the closure line** excluding the ladder's own reports.
**Four are the prohibition** (`closure_challenge_trained_entry_round4_duct.json:88`,
`CLOSURE_CHALLENGE_STATUS.md:394` and `:639`, `latex/closure_challenge_report.tex:864`); a
fifth restates the banned-list rule. **Ten are ordinary uses**, and one is exactly what the
claim denied existed: `PROBABILITY_OF_RANK_2026-08-10.md:151`, *"Larger and more comfortable
than the Reissmann comparison"* — a comfort descriptor **applied to a margin**, in a file
that same commit edited.

**V15 named two counter-examples; there are ten.** The nine beyond the `PROBABILITY_OF_RANK`
one are training-regime containment (×3), three *"uncomfortable"* concessions, a *"not a
reason to feel comfortable"*, a prior-art verdict, and `CLOSURE_RANK1_CAMPAIGN.md:341`'s
*"the comfortable reading"* — which sits in a sentence **refusing** it. **None is a win
claim**, which is why the verdict survives while its evidence does not. The restated claim
is the one C9 needed: *no surface describes the AR_14 lead, or any lead, as a comfortable
**win***.

**Positive control, which the original sweep did not carry.** A scratch file reading *"Our
AR_14_Ret_180 lead of 0.00003 is a comfortable win over Reissmann"* was seeded under
`demo-output/website/`, the sweep returned it, and the file was deleted with `git status`
left clean. **Provenance measured, not assumed**: `git log -S` puts the `PROBABILITY_OF_RANK`
sentence at `b2aa6887` (2026-08-10 16:00) and the `CLOSURE_RANK1_CAMPAIGN` one at `0afd7e61`
(2026-08-05 17:33) — **both pre-ladder**, so neither sentence is ladder-authored and only
the row describing them was.

---

## 3. V6 — THE CURRENCY PASS (`472f9f92`)

V6 stood at **PASS ON THE RULE, FAIL ON CURRENCY**. The rule half never moved. The currency
half failed because §4 of `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` audits **round 3**
(0.0676) while the entry of record is **round 5**, and the per-finding round-5 verdicts
existed only in Pass 2's report — a file a reader of the audit does not have open. **The
block now sits in §4 itself**, where a reader of the audit meets it.

**Nothing in §4.1–§4.9 is rewritten or deleted.** Every one of the nine findings gets an
explicit round-5 verdict, and **where a finding is moot it says so with its reason**: §4.4's
docstring defect and §4.5's missing artifact are both discharged, yet §4.9 still lists them
as blocking; §4.9 itself is superseded whole and is kept, because it is the summary *of that
audit*. Three findings do not describe round 5 and each gets a disposition rather than a
verdict borrowed from Pass 2 — §4.3 **HOLDS AND IS INCOMPLETE** (round 5 introduced a
second, larger leakage instance the section postdates), §4.7's count is stale at *"two of
five"* where round 5 records four of eight while its substance is discharged, §4.9
superseded.

**Every verdict re-verified at HEAD in this pass, not inherited:**

| finding | verification |
|---|---|
| 4.1 | anchors read at HEAD: ground-truth reads at `apply_closure_ph_gate.py:128` (inside `for case in gate._PH_TRAIN:  # 21 cases, train only`, line 126) and `:228` (inside `for c in ph._PH_TRAIN:`, 225); test loop at `:178`, `_load_rans_fields` at `:179` annotated `# no U_LES read`; three executable assertions at `closure_baseline_error_gate.py:84–86` |
| 4.2 | `filecmp` over the two submission directories: five CSVs byte-identical, exactly the three ducts changed |
| 4.3 | quote read with `git show 0bade54a:` at the frozen commit, line 11, **not** from the mutable working copy |
| 4.4 | four call sites counted: `:218–219` (floor), `:301–302` (entry). Two prediction sets, one new |
| 4.5 | all eight round-5 CSVs re-read: 1000×3, comma-delimited, finite, and the **only** alphabetic character in any of the eight files is the `e` of scientific notation. `AR_1_Ret_360.csv` → `bb8d61fb…`, the value Pass 1 traced end-to-end in V4 |
| 4.6 | `MANIFEST.json:37` `eval_package_version_string_note`; `README.md:52–54` |
| 4.7 | the organiser-baseline qualification present on all four external surfaces; `self_audit` fails the wall if the count appears without it |
| 4.8 | dated to `deb91557` everywhere; **"current" is explicitly NOT certified here** — that needs a network read this pass did not make |

**The untrained duct path's own compliance line**, measured rather than asserted:

| question | verdict | measurement |
|---|---|---|
| used at solve time only? | **YES** | `kOmegaSSTQCR` is an in-PDE constitutive term (`kOmegaSSTQCR.C:60`, `.H:14`); the forward script asserts `SIMPLE solution converged in {t} iterations` per arm and writes the CSVs from the converged fields. **There is no post-hoc step to audit because there is none** |
| touched no test data? | **YES — and the absence is a measurement** | `find` over the run tree: `AR_1_Ret_360_qcr`, `AR_3_Ret_360_qcr`, `AR_14_Ret_180_qcr` hold **0** `*_LES*` files each; `AR_7_Ret_180_qcr` and `AR_7_Ret_180_sst` hold **3 each**. `AR_7_Ret_180` is the suggested DUCT **validation** case, and its two arms are the **positive control** that proves the finder works |
| zero fitted parameters? | **YES** | `Ccr1 = 0.3` compiled as the default at `kOmegaSSTQCR.C:91–99` (`getOrAddToDict("Ccr1", coeffDict_, 0.3)`) and overridden in **no** case dictionary in the round-5 run tree |
| stated in the description? | **WAS NOT. Now YES** | `DESCRIPTION_DOCUMENT.md` §2, §3, §6 — and stated as a **concession**: the term is published, it is not ours, and the entry above ours already runs one |

**The audit's central finding survives round 5 and covers LESS ground than it did**: three
of the eight rows are now produced by a published term with nothing in it to fit.

---

## 4. VERDICTS

### V6 — **PASS**

The rule half was never in doubt and this pass re-verified it at HEAD rather than inheriting
it. The currency half is discharged **in the document that carries the audit**: all nine
findings verdicted against round 5, two moot findings kept with their reason, three
non-current findings dispositioned, and the untrained path given the compliance line it
never had, with a positive control behind its one load-bearing negative.

### V10 — **FAIL. One surface, and I caused half of it.**

The rung's own wording is *"one inconsistent surface fails the rung"*, so I will not grade
it green.

**Everything in the working tree is consistent.** V14's stale list is cleared for ranks 1–2
(rebuilt by another agent, verified through served HTML), **4 and 6–11 (this pass)**, and
rank 3 is Katie's shoot script and dispositioned to her. All four external surfaces now
carry the rank companion. `self_audit`'s two closure checks — *closure entry of record* and
*benchmarks vs closure record* — both **PASS**.

**The shipping bundle does not.** `self_audit`'s *bundle drift vs tree* reports two files
behind, and I measured which is whose rather than assuming:

- **`demo-output/website/benchmarks.html` — MINE.** The bundled page is byte-identical to
  this file's *previous* committed state, so my F7 fix put it one clause behind. **The
  shipped bundle also carries the rank claim without the companion**, which the rebuild at
  `892f11f7` could not have fixed, because the rule was applied to these surfaces only now.
- **`sdk/chief_engineer/head_engineer.py` — not mine, and it predates me.** Another family
  committed it at `1471b8f3` (2026-08-10 21:49), **ten minutes after** the last bundle
  rebuild `a1545dbd` (21:39). The check was already failing when I arrived.

**I did not rebuild `dist/`**: it is ring-fenced for this rung, and a rebuild re-snapshots
live `lab_stats` counters and would ship another family's change I have not verified.
**Remedy, for the bundle's owner:** re-run `scripts/build_laptop_bundle.py`, then verify by
extracting the zip and grepping it rather than inferring from the sources — and confirm
`site/benchmarks.html` carries `P(rank 1)` and its interval, which no previous rebuild could
have contained.

### V14 — **PASS, unchanged as a rung; its stale list is now dispositioned in full**

V14's verdict was about its **method** — a search, not a list — and that verdict stands. This
pass re-verified its classification on the eight items it owns and **changed one**: rank 5
is not closable by a note on the document, because the number is hard-coded in a generator,
so the fix had to go into `build_master_table.py`. It also found **two hits the list did not
contain**, both by asking what a generator emits, and it **refused one repair** because the
repair would change a research gate's meaning.

Disposition of the eleven: **1–2 rebuilt and verified** (another agent) · **3 with Katie**
· **4, 6–11 cleared here**. Open: rank 3, and the bundle's re-rebuild under V10 above.

---

## 5. THIS ROUND IS NOT A FIXED POINT, AND SAYING SO IS THE POINT

The termination rule requires that a fix round introduce **zero** new failures in its own
output. **Mine introduced one**: the bundle drift on `benchmarks.html` (§4, V10). It is
named, attributed, and handed to its owner with the remedy; it is not absorbed and it is not
called cosmetic.

**Round 3's scope from this pass:** that drift, plus my last three commits (`656c09c9`,
`63009dd3`, `472f9f92`), which fall **outside** the peer audit in §6 and have not been read
by anyone who did not write them.

---

## 6. INDEPENDENT AUDIT OF THIS PASS, CREDITED RATHER THAN CLAIMED

While I was working, a peer running V15 round 2 (`c1ebfb4f`, `39d22bab`,
`campaign/LADDER_V_V15_ROUND2.md`) audited my first six commits — an agent that wrote none of
my text, which is what the termination rule requires and which I could not do for myself.
Its frame froze at HEAD `249b611c` (2026-08-11 00:07:16 UTC).

**Every row it raised on my work passed** — P29–P43 and P47/P49: the round dates, the
`0.0654375` arithmetic, the deliberate non-correction of the −0.005913 deficit, the rank
companion on the `5af41163` banner, the F1-correct naming of `AR_7`, the 0.080225 / 0.0673
sub-scores, the decision to report rather than re-point the gate, and the date discipline
either side of midnight. It rated the generator-not-output choice in `dc13f1cc` and
`4381d634` as "the failure mode this rung named, closed at the source".

**One observation of theirs I accept and record here rather than rebut:** *O4 — the
byte-for-byte regeneration claim in `dc13f1cc` is inherited by that rung, not verified by
it*, because re-running a closure generator is not a read-only act. It is verified **in this
pass** (§1, rank 5) — three runs into a scratch `OUT_DIR`, before, after, and again — and a
later rung wanting it independently confirmed must re-run the generator itself.

**Its finding N2** — *"four external surfaces still make a rank claim with no figure and no
interval"* — was open at its HEAD and is **closed by `656c09c9`**, twenty minutes after its
frame froze. Its other five findings are not mine and are not addressed here.

---

## 7. COMMITS

| hash | what |
|---|---|
| `dc13f1cc` | V14 rank 5 — master statistics table; note in the generator, outputs re-derived |
| `5af41163` | V14 rank 4 — rank-1 campaign plan; dated banner, arithmetic left alone |
| `4381d634` | V14 ranks 6 + 7 — two live generators, and the manifest string the list missed |
| `a3a4ab3a` | V14 rank 8 — protocol doc; one word, plus the duct measurement round 5 superseded |
| `79f4529c` | V14 rank 9 — `NUMERICS_KNOWLEDGE`; one word fixed, one gate reported not repaired |
| `249b611c` | V14 ranks 10 + 11 — unlabelled standings row, illustrative score made round-free |
| `656c09c9` | V15 F7 — rank companion on four external surfaces, and a guard with four positive controls |
| `63009dd3` | V15 F9 — C9's evidence corrected in place, verdict left standing |
| `472f9f92` | V6 — nine findings verdicted against round 5, untrained path's compliance line |

---

**Signed: the V6/V10/V14 closure pass, 2026-08-11 00:20 UTC (clock).**
Zero scoring calls; ledger unchanged at 6. Nothing was sent, emailed, uploaded or filed.
`dist/`, `LAPTOP_SHOOT.md` and `latex/*.tex` were not touched. No agent verified its own
prose: the §6 audit is a peer's, and the three commits it could not reach are named as
round 3's scope rather than declared clean.
