# Ladder V — consolidated state of record, 2026-08-16

**Executed 2026-08-16T00:29Z → 00:5xZ by a consolidation pass that graded no rung, repaired
nothing, and is an author of nothing it reports on.** No solver run. No scoring call — the
scoring ledger stands at **6**. Nothing sent, uploaded, filed or registered; the submission is
**PARKED** and reserved to Katie. The scoring pin `deb91557` was not moved. `dist/` was not
touched. This pass wrote exactly two files: this document and `docs/DOCKET.md`.

**What this is.** Five rungs moved on 2026-08-15/16 and the ladder's ledger
(`campaign/LADDER_V_TRIPLE_VERIFICATION.md`) has been amended many times by many hands. Nobody
had established the whole picture in one place. Every verdict below is traced to the grade
document that produced it and the commit that anchors it, and every one is checked against the
ladder's own ledger row. **It is a measurement, not a summary** — the load-bearing facts were
re-executed here rather than read off the grades that reported them, and where my execution
disagrees with a report, both are printed.

---

## 0. THE LIMIT THAT A READER MUST CARRY OUT OF THIS DOCUMENT

**No reader of this repository can re-derive any independence claim this document contains.**
Every grade cited below asserts that its author wrote none of the text it graded. **None of
those assertions is checkable from the tree.** All commits on this box carry one identity,
`Ubuntu <ubuntu@ip-172-31-43-247.us-east-2.compute.internal>`; there is no `user.name`
configured; git prints its "configured automatically from your username and hostname" warning
on every commit. Independence in this lab is established **only** from per-agent dispatch
records under `~/.claude/projects/…/subagents/`, which are **untracked and per-machine** — they
are not in any clone, not in any archive, and not in this document. This is docket **D130**.

**`scripts/check_rung_attribution.py` is not cited here and must not be cited by anyone.** Per
**D173** it has emitted exactly one identity across one hundred percent of its deployed life,
that identity is this session's, and run with a closing commit against a graded one it returns
`VERDICT: AUTHOR` for every pairing. It names a *session*, not an agent. A grade defended by it
is undefended.

**Guard output is reported here as a fact about the guard, never as evidence about the text.**
`board_placement_faults` has no arithmetic predicate (**D88**), binds an ordinal only to a
*named published entrant* so it is structurally incapable of faulting any claim about **our own**
placement (**D151**), skips strike-marked sentences (**D85**), and returns `([], [])` on a
shipping member carrying four placements. `check_rank_claim_surfaces` opens that same archive,
returns `WARN`, and names none of its faults. `_best_on_board_faults` never opens any of these
files in production, because its only caller binds it to the credentials wall's `our_entry`
string (**D129**), and its `_BEST_COUNT` pattern is bounded by `[^.\n]` so a wrapped sentence
defeats it (**D223**). **A zero from any of these confirms nothing.**

**The PDF arm is unmeasured and no PDF claim is graded here.** `\sout{}` is strike-and-keep, so
a withdrawn figure sits in the text layer of a *correctly repaired* document exactly as it sits
in a stale one. Grading a PDF requires rendering to PNG; this pass did not render one, so it
grades none. Sixty-eight PDFs are in the corpus and eight four-entry hits are recorded in
`latex/closure_challenge_report.pdf` (**D91**), from a text extract, and that is not a grade.

**The counting frame, measured at 2026-08-16T00:35Z, not inherited.**

| arm | measured here |
|---|---|
| tracked | **20,714** files; `git grep -I` sees **19,212** of them, so **1,502** are binary-marked and invisible to a plain `-I` sweep — `git grep -a` is required |
| untracked, not ignored | **3** |
| gitignored | **37,244** |
| whole tree excluding `.git` | **57,463** files (V14's 2026-08-15 re-run measured 57,421 at `29beb7cf`) |

The shell's `grep` is a function wrapping `ugrep --ignore-files`; a plain `grep -r` in this
shell **cannot see gitignored trees at all**, which is where the largest evidence archives live.

---

## 1. THE STATE IN ONE LINE

**Twelve of sixteen rungs carry a pass; four do not; the ladder is NOT green and the send gate
is shut.** Seven rungs are plain PASS (V1, V2, V3, V4, V7, V9, V11). Five are PASS WITH
RESIDUALS (V6, V8, V12, V13, V14), carrying **nineteen residuals between them**, collected in §6
below. Four are open: **V5 FAIL**, **V10 FAIL** (on a tree that no longer exists — see §4),
**V15** at round 8 and **V16** at round 11, neither closing. **The R-VALUE consecutive-neutral
count is ZERO on both rungs that track it, and no round anywhere in this ladder's record has
ever declared itself belief-neutral** (§5).

**The ledger disagrees with the grade of record on nine of the sixteen rungs, and every one of
today's five moved rungs is among them.** That is filed as **D226**.

---

## 2. THE PER-RUNG TABLE

Verdicts are read from the grade document that produced them. "Ledger row" means the row in
`campaign/LADDER_V_TRIPLE_VERIFICATION.md` at HEAD; line numbers are HEAD's.

| Rung | Verdict of record | Grade document | Commit anchor | Date (UTC) | Ledger row | Agrees? |
|---|---|---|---|---|---|---|
| **V1** clean-environment re-score | **PASS** | `campaign/LADDER_V_PASS1_2026-08-11.md:85,162` | — (Pass 1, executed 2026-08-10) | 2026-08-10 | `:880` PASS (twice) | **YES** |
| **V2** pre-registration chain | **PASS** | `campaign/LADDER_V_PASS1_2026-08-11.md:224-226` | — | 2026-08-10 | `:881` PASS | **YES** |
| **V3** leakage assertions | **PASS**; leg (c) failed on re-run and was fixed by the chief at `2ef8ae3b`, then verified line-by-line by V15 round 1 | `campaign/LADDER_V_PASS1_2026-08-11.md:321`, re-run at `:743-745`; closure at `campaign/LADDER_V_V13_CLOSEOUT.md:87` | `2ef8ae3b` | 2026-08-10/11 | `:882` PASS (one leg failed on re-run; fixed) | **YES** |
| **V4** duct traced end to end | **PASS** | `campaign/LADDER_V_PASS1_2026-08-11.md:394-395` | — | 2026-08-10 | `:883` PASS | **YES** |
| **V5** QCR provenance | **FAIL** | `campaign/LADDER_V_V5_V14_REGRADE_2026-08-16.md:232`, `:475` | **`6d95f812`** | **2026-08-16T00:20:34Z** | `:884` **PASS WITH EXCEPTIONS** | **NO — D226(a)** |
| **V6** compliance audit vs round 5 | **PASS WITH RESIDUALS** (three) | `campaign/LADDER_V_V6_V10_REGRADE_2026-08-15.md:4`, `:191-193` | **`60073572`** | **2026-08-15T19:34:11Z** | `:885` **FAIL** at `377d6afb` | **NO — D226(b)** |
| **V7** known defects killed | **PASS** — three, not the two we knew | `campaign/LADDER_V_PASS2_2026-08-11.md:52` | — | 2026-08-10 | `:886` PASS | **YES** |
| **V8** claims table | **PASS WITH RESIDUALS** (three) | `campaign/LADDER_V_V5_V8_GRADE_2026-08-15.md:13`, `:437-439` | **`2a686b0a`** | **2026-08-15T20:07:27Z** | `:887` **FAIL** at `f8c889cc`; `:924` "OPEN — failed three times" | **NO — D226(c)** |
| **V9** prior-art completeness | **PASS** (FAIL → FIXED; the fix is durable — re-measured here) | `campaign/LADDER_V_PASS2_2026-08-11.md:54`; closure at `campaign/LADDER_V_V13_CLOSEOUT.md:93`, `:362` | `2b251689` / `7cd558b1` | 2026-08-10/11 | `:888` FAIL → FIXED, but the confirmation column still reads *"the struck sentence was then found still in the shipping archive"* | **Verdict yes; confirmation column STALE — D226(d)** |
| **V10** cross-surface / mechanical sweep | **FAIL** — and its four named blockers were all repaired 19 minutes later, ungraded since | `campaign/LADDER_V_V6_V10_REGRADE_2026-08-15.md:4`, `:400-401` | **`60073572`**; repair at **`cca64eaf`** | grade 2026-08-15T19:34:11Z; repair 19:53:29Z | `:889` **FAIL on three of five surfaces** at `377d6afb` | **NO — D226(e), and see D229** |
| **V11** cold reproduction | **PASS** — bit-for-bit from the package alone | `campaign/LADDER_V_PASS3_COLD_2026-08-11.md:170-171` | — | 2026-08-10 | `:890` PASS | **YES** |
| **V12** skeptic's report | **PASS WITH RESIDUALS** (R1, R2, R3) — all three since repaired at `6dbb3be6`, ungraded | `campaign/LADDER_V_V12_V13_V14_GRADE_2026-08-15.md:170` | **`9c2734f8`**; repair at **`6dbb3be6`** | grade 2026-08-15T21:00:12Z; repair 21:34:43Z | `:892` **DELIVERED** | **NO — D226(f)** |
| **V13** close-out | **PASS WITH RESIDUALS** (V13-a … V13-d) | `campaign/LADDER_V_V12_V13_V14_GRADE_2026-08-15.md:297` | **`9c2734f8`** | 2026-08-15T21:00:12Z | `:893` **DELIVERED** | **NO — D226(g)** |
| **V14** mechanical surface discovery | **PASS WITH RESIDUALS** (six) | `campaign/LADDER_V_V5_V14_REGRADE_2026-08-16.md:419`, `:476` | **`6d95f812`** | **2026-08-16T00:20:34Z** | `:894` **PASS as executed**, re-run "NOT clean"; `:930` OPEN | **NO — D226(h)** |
| **V15** ladder-written text | **FAIL** — round 8: **30 findings, four new shapes, NOT belief-neutral** | `campaign/LADDER_V_V15_ROUND8.md:471`, `:514-518`, `:520` | **`c1a13015`** (cells at `e0a4117a`, `d3a3f33b`, `05354615`) | 2026-08-15T20:27:57Z | `:895` stops at **round 7, 25 findings** | **NO — D226(i)** |
| **V16** rank-claim guard reach | **DOES NOT CLOSE** — round 11: **8 findings, four new shapes, NOT belief-neutral** | `campaign/LADDER_V_V16_ROUND11.md:3-5`, `:652-655`, `:878-879` | **`a5bbdeca`** (round at `94419cc8`) | 2026-08-15T22:37:37Z | `:896` enumerates rounds through 10 | **NO — D226(j)** |
| **TERMINATION RULE** (chief, 2026-08-10) | **NOT MET. The gate is shut.** | `campaign/LADDER_V_TRIPLE_VERIFICATION.md:507-530` | — | 2026-08-10 | `:920-931` "GREEN REQUIRES … and the gate is still shut" | **Conclusion agrees; five of its eight rows are stale — D226(k)** |

**The termination rule, measured against its own three clauses** (`:513-521`):

1. *"Every rung V1–V16 carries a PASS."* — **12 of 16.** V5, V10, V15, V16 do not.
2. *"A full re-run of V8, V10, V14 and V15 over the text written by the previous fix round
   introduces no new failures — not 'few', not 'only cosmetic ones'. Zero."* — **Not met.** The
   most recent V15 re-run (round 8) introduced **30**, of which **four are new shapes**, and six
   of them (F2, F4, F5, F6 and two others) are defects *written on 2026-08-15 by the repairs*.
3. *"That zero is itself measured by an agent that wrote none of the text in that round."* —
   Moot while clause 2 is unmet, **and unverifiable from the repository in any case** (§0).

---

## 3. LEDGER-VERSUS-GRADE DISAGREEMENTS — every one found

**Not repaired here.** A consolidation that edits the thing it is measuring cannot be trusted;
these are filed as **D226** and left for a non-author.

| # | Rung | Ledger says (HEAD) | Grade of record says | Age of the disagreement |
|---|---|---|---|---|
| a | **V5** | `:884` **PASS WITH EXCEPTIONS** | **FAIL**, three times over: `7ea96c0f` (02:23Z), `2a686b0a` (20:07Z), `6d95f812` (00:20Z) | **22 hours**, across three independent grades |
| b | **V6** | `:885` **FAIL** at `377d6afb`, on the §4.8 currency row | **PASS WITH RESIDUALS** at `60073572` — the blocker was repaired and the regrade cleared it | 5 hours |
| c | **V8** | `:887` **FAIL** at `f8c889cc`; and `:924` says "OPEN — and it has now failed three times" | **PASS WITH RESIDUALS** at `2a686b0a`; G1 clears, the 84%→177% reversal is real and propagated to all three sites including the cover email | 4½ hours |
| d | **V9** | `:888` confirmation column: *"the struck sentence was then found still in the shipping archive"* | The sentence was removed by the 2026-08-10 rebuild and **is not in the current archive** — re-measured here (below) | 5 days |
| e | **V10** | `:889` **FAIL on three of five named surfaces** at `377d6afb` | **FAIL on four named blockers** at `60073572` — a different, later, and more specific finding; and all four are since repaired | 5 hours |
| f | **V12** | `:892` **DELIVERED** | **PASS WITH RESIDUALS**, three named, all since repaired at `6dbb3be6` | 3½ hours |
| g | **V13** | `:893` **DELIVERED** | **PASS WITH RESIDUALS**, four named (V13-a … V13-d) | 3½ hours |
| h | **V14** | `:894` **PASS as executed**, re-run "NOT clean"; `:930` OPEN | **PASS WITH RESIDUALS**, six named | 4 minutes at the time of writing, and it is the one row nobody could reasonably have updated yet |
| i | **V15** | `:895` **round 7 FAIL, 25 findings** | **Round 8**, 30 findings, four new shapes | 4 hours |
| j | **V16** | `:896` enumerates grades 1–4 and rounds 5–10 | **Round 11**, 8 findings, four new shapes | 2 hours |
| k | **GREEN REQUIRES table** `:922-931` | V8 "OPEN, failed three times"; V16 "the rung is still not PASS" on round 7's two MATERIAL findings; V15 "round 7 returned 25"; V14 "OPEN"; V10 "DELIVERED 2026-08-11" | V8 passes with residuals; V16 is at round 11; V15 is at round 8; V14 passes with residuals; V10's independent confirmation is **owed again** | 4–5 hours; **five of eight rows** |
| l | **V5 ruling face** `:150-152` | *"**Four** of my arguments about this rung have now been refuted by execution"* | `:448-457` (commit `b2668906`, four hours later) accepts a **fifth** refuted argument and a sixth accepted defect; neither line was edited | 4 hours — **filed separately as D228** |

**Shape.** Eleven of these twelve are the same defect: **a summary row going stale against the
section or document it summarises, with neither edited.** That is docket **D141**, whose base
rate this lab measured at **1 in 11**. Here it is **9 in 16 rungs**, and the reason is
structural rather than careless — five rungs moved inside six hours, by five different graders,
and the ledger is edited by hand by whoever happens to be holding it. **The ledger is not a
reliable statement of where Ladder V stands, and this document exists because of that.**

**Row (d) re-measured here rather than inherited.** Against the current tracked archive
`dist/certonomous-demo.zip` — sha256 `34b8feed8301d91a8aa36d506326c89d74cf4b8ac42c2eb19a2948af1c00ba33`,
1,476,024 bytes, 90 file members plus 13 directory entries — both discriminating fragments of the
struck prior-art sentence (`controls where a data-driven correction is allowed to act`,
`has been published repeatedly`) return **zero hits**, whitespace-normalised so that a wrapped
sentence cannot hide, with a positive control (`Closure`) firing in **7** members. **V9's fix is
durable and the ledger's confirmation column has been wrong for five days.**

---

## 4. WHAT BLOCKS EACH NON-PASS RUNG, AND WHOSE IT IS

This is the part the owner acts on. Every item names a file, a line, and what would clear it.

### V5 — FAIL. Four in-frame tracked surfaces make the untrained claim about our own model with zero Spalart.

Graded against the chief's narrowed predicate (`78eb5530`): *"V5's site is where the UNTRAINED
CLAIM ABOUT OUR OWN MODEL is made — not every place the string QCR appears."*

| # | site | what is wrong | what clears it | **whose** |
|---|---|---|---|---|
| **V5-1** | `sdk/scripts/closure_eval_battery/build_master_table.py:246` and `:371` | **The third generator.** Both lines emit *"round 5 (untrained QCR2000 duct forward solve, the sixth pre-registered scoring call)"* with **zero** occurrences of Spalart. The frame ruling's own words are that *"a generator is the most load-bearing surface there is — it manufactures new copies after every repair"* | Name Spalart (2000) beside `Ccr1 = 0.3` in both emitted strings, then regenerate | **FLEET** |
| **V5-2** | `demo-output/website/closure_eval/closure_eval_master_table.md:20` | tracked output of V5-1, same sentence, zero Spalart | falls out of V5-1's regeneration | **FLEET** |
| **V5-3** | `demo-output/website/closure_eval/closure_eval_master_table.json:84` | tracked output of V5-1, same sentence, zero Spalart | falls out of V5-1's regeneration | **FLEET** |
| **V5-4** | `demo-output/website/campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md:121` | *"duct gains from the untrained QCR2000 term (nothing fitted)"* — **a withdrawn exclusion**, returned to frame by the enumeration's own withdrawal (D167) and unrepaired since. It is a site under **both** the literal and the narrowed predicate | An **L-44 dated addendum by the report's owner** — it is a signed report and may not be silently edited (`REGRADE:241`) | **OWNER of that report** (not the fleet, not the chief) |
| **V5-5** | `dist/certonomous-demo/snapshot/lab_stats.json` | gitignored arm; derived at build from `benchmarks.json`, so it carries the claim until a rebuild | **a bundle rebuild** | **OWNER** |

**Not a blocker, correctly:** `demo-output/website/closure_challenge_round5_qcr_forward.json` makes
the same claim as **JSON structure** — `"Ccr1": 0.3`, `"trained": false` — carries **zero**
occurrences of the string *untrained*, and matches **neither** the sweep pattern `untrained[- ]QCR`
**nor** the attribution guard's regex-plus-sentence-splitter predicate. Its exclusion holds on the
container ground. **But no arm of any V5 sweep can see it**, and that is a frame hole the rung's
face does not state (D222).

**V5's closing-condition ambiguity (D122) is DISCHARGED**, and a reader should not treat it as
open: the 2026-08-15 02:23Z grade filed it with **Owner: chief**, and the chief answered it at
`78eb5530` with the narrowed predicate. The predicate is **upheld on its measurement** — it
discriminates, four in-frame sites survive it, and the grade could not produce its falsifier —
**and not on the reasoning given for it** (§7).

### V10 — FAIL, and this is the most misleading row in the ladder.

**V10's verdict of record is a FAIL of a tree that no longer exists.** The regrade `60073572`
(19:34:11Z) named four blockers. The repair `cca64eaf` landed **nineteen minutes later**
(19:53:29Z) and its own commit message says *"V10 is NOT marked green here: the repairing agent
may not grade its own repair."* **No non-author has graded it since** — no V10 document exists
later than 19:32Z by mtime, and no commit after `cca64eaf` re-grades the rung.

**All four blockers verified cleared at HEAD by this pass, by execution:**

| blocker | site | state at HEAD, measured here |
|---|---|---|
| **B1** per-case table | `demo-output/website/closure.html:501-502` | Both gold badges struck and **replaced**: `<s>OUR MODEL LEADS</s> → <b>2nd of 7 — WE LOSE</b> this case`, each naming the holder and both numbers. **CLEARED** |
| **B2** the disclaimer | `closure.html:480-482` | Struck, with all three defects named at `:486-490`: the wrong column identified, *"it is **seven** of the eight rows, not six"*, and the badges and tags now covered. **CLEARED** |
| **B3** three live `rank 1 of 5` | `demo-output/website/ACTIVE_RESEARCH.md:12`, `:25`, `:580` | All three struck and corrected to **rank 1 of 7**, each naming the board by entrant count and retrieval date, each stating that a commit anchor is not an admissible board identifier. **CLEARED** |
| **B4** six-not-seven | `ACTIVE_RESEARCH.md:764` | `~~Six of its eight comparison values were wrong~~` struck and corrected to seven. **CLEARED** |
| **D150** sixth surface, outside V10's five | `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:9`, `:528`, `:873`, `:1226` | All four `rank 1 of 5` struck and corrected to `rank 1 of 7` on a six-entry board. **CLEARED** |

**What blocks V10 is therefore not a repair. It is a grade.**

> **V10 needs one thing: a non-author grader, dispatched against HEAD, who wrote none of
> `cca64eaf` and none of `60073572`, to re-run the regrade's own four falsifiers**
> (`REGRADE:415-420`) — re-render `closure.html`'s per-case column 2 from `LIVE_BOARD` and
> `round5_per_case_full`; show `Uncorrected` rather than `Best published` to be the stale column
> and seven of eight rather than six; show any of `ACTIVE_RESEARCH.md`'s three sites struck or
> board-named; show `0.0364` not to be the live `NASA_2DWMH` minimum. **All four fall ⇒ V10 is
> PASS.** **Whose: FLEET.** Filed as **D229**.

**A grader taking this on must be told two things.** First, the guards will report clean and
that means nothing (§0): `board_placement_faults` returns `([], [])` on all four surfaces while
`closure.html` carries live placements in the same text. Second, the regrade found the *same*
off-by-one — six where the truth is seven — in two independent places, one four days old (B2) and
one written the same day (B4), on different surfaces and from no shared source.

### V15 — round 9 is owed.

Nothing is "blocked": the rung is a loop that has not converged. Round 8 (`c1a13015`) returned
**30** findings over the 78 commits of 2026-08-15, **four of them new shapes** (F1, F3, M3, P15),
and six of them are defects *written on 2026-08-15 by that day's repairs*. Round 8's own words:
*"the count stands at zero."* **Whose: FLEET** — a grader who wrote none of the 2026-08-15/16
text, which now includes this document.

### V16 — round 12 is owed.

Round 11 (`a5bbdeca`) returned **8** findings, **four new shapes**, and states *"R-VALUE's
consecutive-neutral count stays at zero."* The round's finding of record: **the guard's
recogniser is the pin and its oracle is the live board, so it cannot see the leader.** Round 11
also carries its own addendum recording that the round's coverage claim was false 66 minutes
after it was written. **Whose: FLEET.**

### Standing blockers that are not any single rung's

| item | what it is | what clears it | **whose** |
|---|---|---|---|
| **The stale shipping bundle** | `dist/certonomous-demo.zip`, built **2026-08-14T21:16:50Z**, ships three true travelling faults at member `certonomous-demo/site/closure.html:341`, `:502`, `:503`. It also carries V5-5's `lab_stats.json` | **Rebuild.** `scripts/build_laptop_bundle.py` copies the site pages, all of which are now correct; a plain re-run clears every item with no hand-editing | **OWNER — `dist/` is the owner's and no rung may touch it** |
| **D38** | The four standing rules of 2026-08-11 contradict the charters they sit beside in six places, and none is enforced by any code. V15 round 6 records that a rung cannot close over a rule set that contradicts the charter defining what closing means | Amend the charters or the rules; two of the six are drafting fixes the chief can make, one is a measurement nobody has run | **OWNER (Katie)** on (1) and (3); **CHIEF** on (2), (4), (5); **FLEET** on (6) |
| **The six corrections that have not travelled** | Ledger `:927` records this as **NOT RE-MEASURED**, out of scope, and the count *four days old* — it is now **five** days old | Someone must re-measure it and state their frame | **FLEET** |
| **PASS WITH RESIDUALS has never met its own entry condition** | See §5. Five rungs carry it; its only written definition requires two consecutive belief-neutral rounds, which have occurred **zero times** | A chief ruling on whether PASS WITH RESIDUALS may be issued by a single grade | **CHIEF** — filed as **D227** |

---

## 5. THE R-VALUE COUNT — established from the round documents, not from anyone's assertion

**The rule** (`campaign/LADDER_V_TRIPLE_VERIFICATION.md:551-554`, Katie, 2026-08-11):

> **R-VALUE.** Each grade round records what it found and what it cost. When **two consecutive
> rounds return only findings that would not change an external reader's belief**, the rung
> closes as **PASS WITH RESIDUALS**, and the residuals become docket items.

### **THE COUNT IS ZERO. On both rungs. And it has never been anything else.**

**V15 — consecutive belief-neutral rounds: 0.**

| round | document | findings | new shapes | the round's own verdict | neutral? |
|---|---|---|---|---|---|
| 1 | `LADDER_V_V15_LADDER_TEXT_CLAIMS.md:145`, `:489` | 10 | — | *"NO. V15 FAILS. Two blocking defects…"* | **NO** |
| 2 | `LADDER_V_V15_ROUND2.md:508`, `:513` | 6 | — | `# NO.` *"Six new failures are in the fix round's own output"* | **NO** |
| 3 | (fix round; graded by round 4) | — | — | — | — |
| 4 | `LADDER_V_V15_ROUND4.md:680`, `:685` | 7 | — | `# NO.` *"Seven new failures are in round 3's own output"* | **NO** |
| 5 | `V15_ROUND5_NUMBER_RECONCILIATION.md:210-220` | 9 change-items | — | **the document has no R-VALUE section and states no neutrality verdict** | **cannot be counted either way** |
| 6 | `LADDER_V_V15_ROUND6.md:471`, `:480` | 20 | — | *"The termination rule wants zero new failures. It is not zero."* | **NO** |
| 7 | `LADDER_V_V15_ROUND7.md:709-712` | 25 | 4 | *"Is this round BELIEF-NEUTRAL? **No.**"* — first round to self-apply the test by name | **NO** |
| 8 | `LADDER_V_V15_ROUND8.md:471`, `:514-518` | **30** | **4** (F1, F3, M3, P15) | *"**VERDICT: this round is NOT belief-neutral.** … the count stands at zero."* | **NO** |

**V16 — consecutive belief-neutral rounds: 0.**

| round | document | findings | new shapes | the round's own verdict | neutral? |
|---|---|---|---|---|---|
| 1–4 | `V16_GRADE.md` §§6 / 8.4 / 9.6 / 10.5 | multiple exceptions per grade | — | **predate the rule; no R-VALUE language in the file** | not stated |
| 5 | `V16_GRADE_ROUND5.md:119-137` | 2 material (E2, E4) | — | *"the R-VALUE counter does not reach two. **V16 does not close on this round.**"* | **NO** |
| 6 | `V16_GRADE_ROUND6.md:157-169` | 4 material | — | *"the R-VALUE counter does not reach two."* | **NO** |
| 7 | `V16_GRADE_ROUND7.md:216-231`, `:240-241` | 2 material | — | *"V16 does not close this round … This grade is not clean, so it does not supply the second of the two."* | **NO** |
| 8 | **no document — commit `5e4a0cc5` only** | — | — | **no R-VALUE verdict, no belief-neutrality statement anywhere in its text** | **not self-declared** |
| 9 | **no document — commit `067caac0` only** | — | — | **no R-VALUE verdict** | **not self-declared** |
| 10 | **no document — commit `0c7b968d` only** | — | — | **no R-VALUE verdict** | **not self-declared** |
| 11 | `LADDER_V_V16_ROUND11.md:3-5`, `:652-655`, `:878-879` | **8** | **4** | *"the round is NOT belief-neutral … R-VALUE's consecutive-neutral count stays at **zero**."* | **NO** |

### Which rounds I counted, and why

**I counted every round that produced a document, and I counted it on that document's own
words.** Rounds that self-declare NOT neutral reset the count to zero and are the only rounds
that can be counted at all. Three things a reader must know:

1. **No round anywhere in this ladder's record has ever declared itself belief-neutral.** Not
   one, on either rung, in fifteen documented rounds. The count has therefore never been 1, let
   alone 2. **R-VALUE has never been within one round of closing anything.**
2. **V16 rounds 8, 9 and 10 have no documents.** Their entire record is three commit messages,
   and **none of the three contains the string "R-VALUE", "belief-neutral", or any neutrality
   verdict.** A round that leaves no gradeable record cannot supply either of R-VALUE's two.
3. **The single claim that a round was "scored neutral" is an assertion made *about* round 10 by
   round 11** (`LADDER_V_V16_ROUND11.md:712-713`) **and echoed by V15 round 8**
   (`:619-620`) — *"Round 10 was scored neutral and three new shapes appeared within forty
   minutes"* — and it is **not corroborated by anything round 10 itself wrote**, because round 10
   wrote nothing that survives as a document. Both citations are warnings *against* scoring
   neutrality early, not records of a neutral round.
4. **V15 round 5 is silent** and contributes nothing in either direction. Counting it as neutral
   because it did not say it was not would invert the rule.

### **The finding this count produces, and it is the one the chief must rule on**

**Five rungs — V6, V8, V12, V13, V14 — carry PASS WITH RESIDUALS. R-VALUE is the only place in
this lab where that verdict is defined, and its entry condition is two consecutive belief-neutral
rounds. That condition has been met zero times.** Each of the five was issued PASS WITH RESIDUALS
by a **single** grade. This may be exactly what the lab intends — but it is not what is written,
nobody has ruled on it, and **D38(1)** already records that PASS WITH RESIDUALS is a sixth gate
verdict against `VERIFICATION_CHARTER.md:95` (*"The verdict vocabulary is fixed"*), invisible by
construction to §16's negative-verdict-review sweep. **Filed as D227. Chief's.**

---

## 6. THE COLLECTED RESIDUALS — nineteen, in one place for the first time

A rung that passes with residuals nobody has collected is not the same as a rung that passes.

### V6 — three (`campaign/LADDER_V_V6_V10_REGRADE_2026-08-15.md:195-204`)

| id | residual | site |
|---|---|---|
| **V6-R1** | *"Ten of the eleven are byte-identical … the eleventh being §4.7"* is **nine of eleven**, differing in §4.7 **and** §4.8, under an explicit `HEAD` anchor. Self-inflicted by the commit that wrote it | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:299-300` |
| **V6-R2** | *"212 lines below in this same file"* is **256**. 212 was transcribed from the grade being repaired, where it pointed at §4.7's heading | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:321` |
| **V6-R3** | The block's headline conclusion about byte-identity is **right in principle and wrong in its count**, so a reader who checks it finds the sentence false and may discard the principle with it. *"That is the residual worth the most, because the principle is correct"* | same block |

Both V6-R1 and V6-R2 are machine-checkable in three lines and both survived a post-write sweep —
which is **D141**, V6's own blocker, still true after the repair.

### V8 — three (`campaign/LADDER_V_V5_V8_GRADE_2026-08-15.md:378-382`)

| id | residual | site |
|---|---|---|
| **V8-R1** | F4's certification *"thirty body lines are byte-identical"* is false — **three of 32 lines differ, not two**, independently reproduced by a different extraction. Ruled a residual rather than a blocker because it sits in the draft's §5 banner preamble, a document that does not travel | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §5 banner |
| **V8-R2** | A stray unstruck **84%** figure inside the kept, dated 2026-08-10 banner | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:666` |
| **V8-R3** | **No instrument enforces the new triple rule**; its own negative control `NEG-4` asserts `fired=False` by design | — |
| **D85** (standing, filed 2026-08-14) | The travelling ordinal repaired twice this week is **defended by no instrument at all**, and the strike-and-keep marker that makes it honest to a reader is exactly what blinds the guard to it. Mutation-proved: falsify the ordinal, keep the strike marker, zero faults. **Narrowed by a chief correction at `29452c51`** — there is no strike stripper, and six agents were briefed that there was | `DESCRIPTION_DOCUMENT.md:54` |

### V12 — three (`campaign/LADDER_V_V12_V13_V14_GRADE_2026-08-15.md:125-166`) — **all three since repaired at `6dbb3be6`, and the repair is ungraded**

| id | residual | site | state |
|---|---|---|---|
| **V12-R1** | **The one actionable recommendation in the rung's product instructed the lab to publish a figure the same document strikes 34 lines earlier** — `P(rank 1) ≈ 0.67`, the four-entry board's figure, **17 points optimistic in the direction that flatters us**, on the document that routes to the steward | `LADDER_V_PASS3_COLD_2026-08-11.md:525-527` | repaired at `6dbb3be6`: restated to **50.2%, 0–97% at 95%**, six entries retrieved 2026-08-11T23:33Z |
| **V12-R2** | §W3 claims the declined-gate baseline beats *"all four published entries (… a best published 0.0760)"*. The direction survives and **strengthens** — it beats all six — but the value is **Yang's 0.0748**; 0.0760 is Reissmann's | `LADDER_V_PASS3_COLD_2026-08-11.md:559-562` | repaired at `6dbb3be6` |
| **V12-R3** | **Adjacent bullets state one bound two ways.** `:399-403` quotes the JSON to eighteen digits (`0.002419121853891026` → 177% of the margin); `:404-407` prints `0.059047`/`0.054247`, which are `0.056647191704213645 ± 0.0024` — the **rounded script constant** `SEED_BOUND_ON_OVERALL` at `sdk/scripts/probability_of_rank.py:64`. The conclusion is unaffected (adverse sorts 2nd of 7 under either bound), which is why it survived — nothing downstream moved. **D179** | `LADDER_V_PASS3_COLD_2026-08-11.md:399-407` | repaired at `6dbb3be6` to `0.059066`/`0.054228` with an arithmetic table |

### V13 — four (`campaign/LADDER_V_V12_V13_V14_GRADE_2026-08-15.md:239-293`)

| id | residual |
|---|---|
| **V13-a** | The drift figure has **degraded by one**: §8's `51/56` was true when written and is **50/56** at HEAD, with `sdk/chief_engineer/certificate.py` a sixth stale member |
| **V13-b** | The correction is **one round stale**: it names rounds 5–7 and **round 8 exists** (`campaign/LADDER_V_V15_ROUND8.md`, `05354615`, 2026-08-15T20:18:50Z) |
| **V13-c** | §2's V10 row is stale against §8 of the same file: `LADDER_V_V13_CLOSEOUT.md:94` still says *"NO — SELF-GRADED"* while `:597` says V10 moves off CLOSED-BY-ITS-AUTHOR. Mitigated by design — a pointer to §8 exists |
| **V13-d** | `LADDER_V_TRIPLE_VERIFICATION.md:1147-1148` and the ledger's V13 row assert §8 is **unedited** and *"both slots are still empty as slots"*. Both were true at `29beb7cf` (01:01:21Z) and **false since `9e466dd4` (02:07:33Z)** added the DISCHARGED block |

**Standing beside V13, and not a residual: D118.** The lab's bundle-drift detector
`self_audit.check_bundle_drift()` compares tracked sources against `dist/certonomous-demo/`, a
**gitignored** directory, and **never opens `dist/certonomous-demo.zip` — the only file that
leaves this box.** That is why V14's residual 1 could exist at all.

### V14 — six (`campaign/LADDER_V_V5_V14_REGRADE_2026-08-16.md:428-442`)

| id | residual | whose |
|---|---|---|
| **V14-1** | **The shipping bundle is stale.** `dist/certonomous-demo.zip` (2026-08-14T21:16:50Z) ships three true travelling faults at member `closure.html:341`, `:502`, `:503`, all corrected on the tracked source. **Repair is a rebuild** | **OWNER** |
| **V14-2** | `_in_board_context`'s **300-character window** leaves three confirmed-true bare ordinals unfaulted at 1,219 / 1,443 / 1,319 characters. **Correctly not widened** — widening a context window to make a control pass changes what counts as evidence | owner of both checks |
| **V14-3** | `_BEST_COUNT`'s `[^.\n]` class **cannot cross a line break**, which is the sole reason `:342` is unreached. An **instrument defect currently recorded on the rung's face as an impossibility** (see §7) | fleet |
| **V14-4** | `_BEST_COUNT` carries a `\b`-after-digits shape on `(?:eight|8)\b`, so **`of 8.5` would match**. No instance in this corpus | fleet |
| **V14-5** | **D208's confirmed execution gap** on `0.0029` at `closure.html:411` produced no fault in the grade's run. (`benchmarks.html:148` is repaired at source) | fleet |
| **V14-6** | **The PDF arm is unmeasured.** No PDF claim is graded on this rung — and, per §0, none can be graded from a text extract | fleet |

**Nineteen residuals. Three of them (V12's) are repaired and awaiting a non-author grade. One
(V14-1) is the owner's and is the subject of §7's decisive fact. The remaining fifteen are open.**

---

## 7. THE DECISIVE FACT FOR V14 — the source is right and the artifact is stale

**State this before anything else about V14, because a reader who does not have it will read
three true faults as three live defects and they are not.**

**All three of V14's travelling faults sit inside `dist/certonomous-demo.zip`.** That archive was
**built 2026-08-14T21:16:50Z**. Its tracked source, `demo-output/website/closure.html`, was
**committed 2026-08-15T19:53:29Z at `cca64eaf`, with every one of those claims struck, dated
2026-08-15, and corrected.**

**Re-measured here by execution, not read from the grade:**

| probe | zip member `certonomous-demo/site/closure.html` | tracked `demo-output/website/closure.html` at HEAD |
|---|---|---|
| member timestamp / commit | **2026-08-12T16:31:22Z**, sha256 `80d94712…`, 41,094 chars | **`cca64eaf`, 2026-08-15T19:53:29Z**, 51,326 chars |
| `WE LOSE` | **0** | **2** |
| `<s>` strike openers | **5** | **25** |
| `of 7` | **1** | **11** |

The three faults are `:341` (`3rd of 5`), `:502` (`rank 1 of 5`) and `:503` (`comparable`). At the
tracked source each is struck and replaced: the ordinal to **4th of 7**, the best-on-board count to
**2 of 8**, the placement to **rank 1 of 7 entrants**, and the seed bound to **177% of the margin**
rather than *comparable to it*. `benchmarks.html:148` now reads *"the seed uncertainty is **larger**
than the margin, **not comparable** to it"*. All three `3rd of 5` occurrences surviving in the
tracked file are inside `<s>` tombstones — strike-and-keep, which is the correct repair.

> ### **The source is right. The artifact is stale. That is a rebuild, and the rebuild is the owner's.**
>
> `scripts/build_laptop_bundle.py` copies `demo-output/website/{closure.html, benchmarks.html,
> wall/wall.html}`, **all of which are already correct**, and re-snapshots the lab counters. **A
> plain re-run clears V14-1 and V5-5 together, with no hand-editing.** `dist/` was not touched by
> this pass and may not be touched by any rung.
>
> **The falsifier the grade set for its own PASS, restated so it is not lost:** rebuild the bundle
> and re-run `check_rank_claim_values`. **If the travelling arm does not go to zero, or if any
> *tracked* travelling surface faults, the PASS is wrong and V14 is FAIL.** And a grader who reads
> V14's gate as *"no travelling fault may stand, whatever its cause"* should read this rung as
> **FAIL until the rebuild**. Both readings are defensible; the rebuild settles them both.

---

## 8. CHIEF RULINGS THAT BEAR ON RUNGS — with their withdrawals

**Read this section before acting on any reasoning in it.** **Four of the chief's arguments on V5
and one whole concession on V14 have been refuted by execution** — the chief's own face says four
(`LADDER_V_TRIPLE_VERIFICATION.md:150-152`); counting the same way that line counts, the total at
HEAD is **five**, because a fifth was accepted four hours later and the line was not edited (§3
row l, **D228**). **A reader who inherits a withdrawn argument will act on it**, so each is printed
with its status.

| ruling | commit | recorded at | bears on | **STATUS** |
|---|---|---|---|---|
| **V5 frame ruling** — *generators are in frame; an unenumerated exclusion is not a frame, it is a gap* | **`3af7bd2b`**, 2026-08-15T02:24:57Z (repo anchor in the text: `b1d7faa3`) | `LADDER_V_TRIPLE_VERIFICATION.md:35-75` | V5 | **OUTCOME STANDS; THREE SUPPORTING ARGUMENTS WITHDRAWN** |
| ↳ **amendment 1** | **`25777f57`**, 2026-08-15T20:09:15Z (text anchor: `2a686b0a`) | `:77-115` | V5 | *"THREE OF ITS ARGUMENTS ARE WITHDRAWN. THE OUTCOME STANDS, ON A GROUND I DID NOT STATE."* |
| ↳ **amendment 2 — the predicate ruling**, carrying a **fourth** correction | **`78eb5530`**, 2026-08-15T20:26:20Z (text anchor: `e65137cd`) | `:117-152` | V5 | **STANDS on its measurement, not on its reasoning.** Narrows V5's site to *where the untrained claim about our own model is made* |
| ↳ **amendment 3 — the acceptance** | **`b2668906`**, 2026-08-16T00:22:34Z (text anchor: `dc05b690`) | `:448-457` | V5 **and** V14 | Accepts **two further defects** in the predicate ruling. *"Upheld on the measurement, not on the reasoning I gave for it, and the record should say so."* |
| **Board-referent ruling** — *the referent is fixed by the claim, not by the rung* | **`04489465`**, 2026-08-15T02:59:48Z (text anchor: `377d6afb`) | `:891` (a ledger table row) | V5, V6, V10 | **STANDS, unrefuted.** Adopted as binding by the V6/V10 regrade and used to fail two of V10's four blockers |
| **V14 denominator ruling** — *reach is repo-wide, gating is travelling-scoped* | **`9b9951a1`**, 2026-08-15T22:05:54Z (text anchor: `86dd1866`) | `:381-421` | V14 | **REACH/GATING SPLIT: LEGITIMATE**, re-measured, falsifier not triggered. **HUMAN-READING CONCESSION: WITHDRAWN.** A third premise refuted separately (D206) |
| **Rounding convention** | **`0b8fb5d6`**, 2026-08-15T02:54:16Z | `docs/DOCKET.md:490` (D120), `:497` (D127); charter form at `docs/charters/REPORTING_CHARTER.md:406-412` | figures across the ladder | **THE ORIGINAL RULING WAS REFUTED AND CLOSED AS REFUTED, NOT AS IMPLEMENTED** |

### The four (now five) V5 arguments refuted by execution — verbatim

**(1) W-2 cited backwards** — `:81-85`, withdrawn at `25777f57`:

> *"I cited W-2 backwards. W-2 is the identity test for a gate whose stated failure mode cannot
> occur. **An unsatisfiable criterion is not unfalsifiable — it is permanently falsified, which is
> the opposite defect.** The rejection of the literal reading survives, but the reason is that a
> criterion no execution can ever satisfy tells you nothing about the corpus, not that it is an
> identity. **Struck as reasoning, kept as record.**"*  Filed **D153**.

**(2) The frozen-artifact impossibility premise** — `:87-92`, withdrawn at `25777f57`:

> *"My impossibility premise is contradicted five paragraphs below it, inside this same ruling. I
> argued the frozen artifacts 'may never take a revision'; **`fe612d03` amended a signed report 20
> hours after signing**, and L-44 already permits a dated addendum. … **This is the D141 shape — a
> claim stale against another region of its own document — committed by me inside a ruling about
> frames.**"*  Filed **D154**.

**(3) The generator mechanism** — `:94-99`, withdrawn at `25777f57`:

> *"My generator claim is **right about reach and wrong about mechanism**. `build_benchmarks.py::main()`
> writes `benchmarks.json` and the `.png` only; the other two surfaces are second-order via
> `lab_stats.research_programs()`. **That is the same file-versus-sentence conflation this ruling
> indicts `e071075d` for one paragraph earlier** — I asked whether something writes that *file*
> while writing a sentence about what writes that *claim*."*  Filed **D152**.

**(4) The `MANIFEST.json`-alone concession** — `:120-128`, corrected at `78eb5530`:

> *"My amendment conceded a sound impossibility ground for `MANIFEST.json` **alone**. Wrong. The
> enumeration pass established the ground is a property of **the container, not of freezing**:
> L-44's dated addendum needs a region below the freeze line, and **a Markdown record has one where
> a JSON object does not.** So it covers **both JSONs** and **neither Markdown report** — wider than
> I allowed on one side, narrower on the other. It also established that *'left to its owner'* is a
> **routing rule, not a frame exclusion**."*  Filed **D167**, **D168**, **D169**.

**(5) The textual argument for the narrowing** — `:449-451`, accepted at `b2668906`, **after the
face's count of "four" was written and never edited**:

> *"the textual argument **fails** — the 'untrained is load-bearing' parenthetical attaches to the
> zero-fitted-parameters clause, separated from the citation clause by **a semicolon**, so the
> rung's own sentence does not say what I said it says"*

and a sixth accepted defect, of provenance rather than of argument (`:452-455`): the ruling issued
**3 minutes 11 seconds** after a pass that had measured thirteen unattributed sentences, declined
to repair them, and then made exactly those thirteen not-sites — *"the shape I rejected the two-site
reading for, arriving under my own hand."*

**What survives, and it is not small:** the frame is unchanged; the two-site reading is still
rejected because it arrived **by transcription**; the literal reading is still rejected because it
**cannot discriminate**; and the narrowed predicate survives because **it discriminates** — four
in-frame sites survive it and V5 still FAILS.

### The V14 concession, in full, and its withdrawal

**Issued** at `9b9951a1`, `:412-416`:

> *"`:342`'s `5 of 8 → 4 of 8` is **structurally unreachable by any board arithmetic**, because `4`
> is simultaneously the withdrawn best-on-board count and the correct cases-won count against the
> leader. **That one needs a human reading** and the rung should say so rather than pretend a rule
> covers it."*

**Withdrawn** at `b2668906`, `:422-432`:

> *"**THE HUMAN-READING CONCESSION IS WITHDRAWN.** … **I wrote an instrument defect into a ruling as
> a property of the world.** I said `:342` was structurally unreachable by any board arithmetic. It
> is not. `_BEST_COUNT` **already faults that quantity, with that wrong value, at eleven tracked
> sites** — one of them the identical sentence in Markdown. The real obstruction is a **25-character
> gap containing a newline**, which `[^.\n]{0,80}` excludes; proved by running the pattern on the
> shipped fragment and then on the same text with the newline replaced by a space. **A bounded
> character class is not a fact about the world, and 'no rule can decide this' was a claim about my
> regex.**"*

And the general form, which is the part worth keeping:

> *"An 'acknowledged limit' is only honest when the limit is real; otherwise it is the most
> comfortable possible error, **because it looks like restraint**."*

**A third premise of the same ruling was also refuted by execution** and is not covered by the
withdrawal: **D206** (`docs/DOCKET.md:571`) records that the ruling's claim that `_VALUE_BOARD_SIZE`
misses this class *"for exactly one reason"* is **refuted — there is a second gate**, the shared
`_in_board_context` 300-character window, **and it blocks three of the four claims the widening was
bought to catch.** The reach/gating split itself is the part that stands: re-measured by the
regrade at **three travelling faults with zero false positives**, against 25 lab-record faults that
are overwhelmingly correct dated records of the four-entry board, so repo-wide *gating* really
would be unusable rather than stricter. **Its stated falsifier is not triggered.**

### The rounding convention, and what a reader must not inherit

**Do not act on D120.** `docs/DOCKET.md:490` proposed that the margin be rewritten `0.001365` →
`0.001366` on six surfaces, on the ground that `0.001365` is *"a TRUNCATION where every other figure
in the family is a ROUND"*. **That is false and the row is CLOSED AS REFUTED, NOT AS IMPLEMENTED.**
D127 (`:497`) established by execution that `0.058013` is not the basis — **it is the six-decimal
printing of the basis.** `LIVE_BOARD`'s Yang column means to exactly `0.0580125`, and
`0.0580125 − 0.056647191704213645 = 0.0013653082957863563`, which is **`0.001365` at six decimals,
half-away-from-zero**. `0.001365` **is a round, is correct, and zero instances should change.** The
ruling's own author accepted the refutation **in full** at `0b8fb5d6`. What stands in its place is a
convention of **form alone, naming no figure**, at `docs/DOCKET.md:497`: *(1) a derived quantity is
computed from the most precise available inputs, **never from a printing of them** — subtracting a
rounded display of a value that exists unrounded in a committed record is a defect regardless of
which direction it moves the result; (2) **figures are rounded, never truncated**, half-away-from-zero;
(3) a quoted figure carries its basis.* The charter form is at
`docs/charters/REPORTING_CHARTER.md:406-412`: *"A figure is printed at the precision of the
derivation that produced it, and the uncertainty of its inputs is stated as an interval where the
quantity is defined — never by deleting digits. … Adopted by the chief 2026-08-15."*

---

## 9. WHAT THIS PASS COULD NOT MEASURE

Stated because a consolidation that does not say this is selling a completeness it has not earned.

- **Every independence claim in this document** (§0). Not weakened here; **unverifiable from the
  repository, by anyone, ever** — D130.
- **The PDF arm.** No PDF was rendered, so no PDF claim is graded. Eight four-entry hits are on
  record in `latex/closure_challenge_report.pdf` from a text extract; a text extract cannot
  distinguish a repaired `\sout{}` from a live claim, so that number is not a verdict.
- **The 955 PNGs.** No text search reaches them. Unchanged blind spot, stated rather than closed.
- **Rendered text.** A page can carry a claim its bytes do not contain.
- **The run tree.** 57,463 files exist outside `.git` and 37,244 are gitignored; this pass read
  none of the run archives, and a worktree-isolated agent would not have been able to.
- **Whether V10's repair is *correct*, only that it is *present*.** I verified by execution that
  all four named blockers are struck and replaced at HEAD. **Verifying that the replacements are
  right is the grade, and the grade is not mine to give** — that is D229 and it is the fleet's.
- **The six corrections that have not travelled.** Five days old and still not re-measured.

---

## 10. DOCKET ROWS THIS PASS FILED

**D226** — the ledger disagrees with the grade of record on nine of sixteen rungs.
**D227** — PASS WITH RESIDUALS is carried by five rungs and its only written entry condition has
been met zero times.
**D228** — the V5 ruling's own count of its refuted arguments went stale inside four hours, in the
same document, with neither line edited.
**D229** — V10's four blockers were repaired nineteen minutes after the grade that named them, and
its verdict of record is a FAIL of a tree that no longer exists.

> **ANCHOR NOTE, because a row anchored at a commit that does not mention it is a defect this lab
> has already filed once (`b1d7faa3`).** All four rows landed at **`a8b3bce6`** (2026-08-16T00:42:57Z),
> which is **another agent's commit**, not this pass's: that agent was committing its own `D225` with
> a `docs/DOCKET.md` pathspec while my four rows sat uncommitted in the same working tree, and
> `git commit -- <path>` takes the **working tree**, so all five rows travelled together. **The
> capture was declared by its author at `78300277`** (00:43:45Z) within a minute. The rows are
> byte-intact — verified here by reading them back out of `git show HEAD:docs/DOCKET.md` and
> checking column count and content. **Nothing was lost and nothing was silently taken**; this note
> exists so that a reader who runs `git log -S'| D226 |'` and finds a commit message about
> one-sided ids does not conclude the row is misfiled. This document itself is anchored at
> **`04144e7c`**.

*This document graded no rung, marked none green, repaired nothing, and is now an author of the
text above — so under R-ISOLATE it may not measure any of it again.*
