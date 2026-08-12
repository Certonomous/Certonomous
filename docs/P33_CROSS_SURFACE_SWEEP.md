# P3.3 — Cross-surface consistency sweep of the closure-challenge numbers

Grader: [SONNET]. Report-only; no surface edited. Swept at HEAD `5a15844f` (2026-08-12),
against the canonical values as of `1b982ae1`: overall **0.056647** (full precision
`0.056647191704213645`); **P(rank 1) = 50%** (50.2%), double-bootstrap **0–97% at 95%**;
live board **six** entries (Yang 0.0580 / Reissmann-Fang-Sandberg 0.0595 / Wu & Zhang 0.0624
/ Tian-Buchanan-Hickel-Dwight 0.0641 / Liu-Wang-Zhao-Xiao 0.0737 / Montoya-Oulghelou-Cinnella
0.0779); **four** pairwise leads not statistically decided (incl. leader Yang), Liu and
Montoya decided; best-on-board **2 of 8**, model's own count **0 of 8** (both survivors are
the organisers' unmodified RANS baseline through the decline gate); nothing submitted.

## 0. Verification of the canonical values themselves (executed, not read)

- `demo-output/website/closure_challenge_round5_qcr.json`: `verdict.measured_overall` =
  `0.056647191704213645`, `verdict.verdict` = `ACCEPT`. Matches.
- Ran `python3 sdk/scripts/probability_of_rank.py` in full (pure arithmetic over committed
  per-case scores, ~1 min, no compute authorization needed). Reproduced independently:
  point rank 1 at 0.056647; **50.15% MC / 50.2% reported**; double bootstrap **0.2%–96.9%**
  (rounds to the published 0–97%); **4 comparisons NOT statistically decided** (Yang t=-0.189,
  Reissmann t=-0.495, Wu & Zhang t=-0.953, Tian/Buchanan/Hickel/Dwight t=-1.033) and **2
  decided** (Liu t=-2.203/98.7%, Montoya t=-2.912/99.8%); seed bound 34.2%/65.4%; the
  reproduction-check block confirms all 6 board entries' means match their published overall
  to 4dp. Every canonical figure in the task brief is confirmed by execution, not assumed.
- `qcr.json`'s own `leaderboard_comparison_dated_2026_08_07` block is itself a append-only
  history containing the superseded 68%/2–100%/"rank 1 of 5"/four-entry figures — but every
  one of them sits under a field explicitly named `rank_companion_2026_08_11_six_entry_board`
  / `best_on_board_count_2026_08_11_six_entry_board` that states **"SUPERSEDES X on every
  figure"** and restates the correct current numbers. This is **STRUCK-AND-KEPT, correctly
  done** — not a defect, despite being the single most consequential file in the sweep.

## 1. Tooling used, per pass, with positive controls

| Pass | Tool | Positive control |
|---|---|---|
| Tracked-file text search | `git grep -n` | Returns 453+912 raw hits across two multi-pattern sweeps before any filtering; corroborated against `docs/DOCKET.md` D56/D48 entries that independently name the same files. |
| Untracked/ignored paths | `/usr/bin/grep` (real GNU grep) | Repo-root `grep -rl "68%" .` (aliased, ugrep --ignore-files) found **66** files; `/usr/bin/grep -rl "68%" --exclude-dir=.git .` found **104**. The 38-file delta is exactly the class the trap warns about: `dist/certonomous-demo/` (gitignored extracted bundle), `mission-output/`, `__pycache__/*.pyc`, and a numpy wheel — none of which the aliased command can see. Confirms the trap is live in this tree today, not hypothetical. |
| Archive members | `python3 -c "import zipfile"` | Read `dist/certonomous-demo.zip` member list (103 members) and decoded 3 target members directly; no text sweep opens archives, so this is the only way to see them. |

## 2. LIVE-AND-STALE findings (current defects — nobody should act on the parked
DESCRIPTION_DOCUMENT.md item below, everything else is real and static)

| # | Surface | What's stale | Evidence |
|---|---|---|---|
| 1 | **`dist/certonomous-demo.zip` (TRACKED)** | 3 members carry the full superseded set: `site/closure.html` — `RANK 1 OF 5`, `P(rank 1) = 68%`, `2–100% at 95%`, and even the never-externally-published `67.6%`; `site/benchmarks.html` — `P(rank 1) = 68%`, `2–100% at 95%`; `snapshot/lab_stats.json` — same, plus `rank 1 of 5` and a "four of eight" best-on-board framing (with the RANS disclosure correctly attached, just to the wrong count). Last rebuilt at `b9233e51`, which is **~230 commits before** `5c9c63fb` (the 68%→50% recompute) — the zip has not been touched since the board moved. This is exactly `docs/DOCKET.md` row **D56** (8 stale instances / 3 files), independently reproduced here by reading the archive directly. | `python3 -c "import zipfile..."` on the tracked archive, quoted above. |
| 2 | `dist/certonomous-demo/` (untracked, gitignored extracted copy — `.gitignore:72`) | Identical staleness to #1, confirmed with real grep at explicit paths. This is the copy a plain `grep -r` sweep from repo root will simply never see. | `/usr/bin/grep -n "68%..." dist/certonomous-demo/site/{benchmarks,closure}.html` |
| 3 | `demo-output/website/closure.html:502` | Single unstruck, live sentence in the closing "honest bottom line" paragraph: *"...holds no official rank — **rank 1 of 5** is our local scoring at a pinned benchmark commit, with a seed-uncertainty bound comparable to its margin."* Every other occurrence in this file (lines 65–145, 370–426) was correctly repaired with `<s>` + dated notes; this one, in a separate closing section, was missed. | `git grep -n "rank 1 of 5" demo-output/website/closure.html` → only unstruck hit in the file. |
| 4 | `demo-output/website/latex/closure_challenge_report.tex` | Two disjoint regions in the **same document**. Front matter/summary (lines 59–70, 207–221, 258–300, 331–362) is correctly repaired: live 50%/0–97%/Yang/six-entry, old figures under `\sout{}`. But a **later narrative+table region is not**, and states the old figures live, unstruck, present tense: L737 *"the entry at the top of the local board — at 68% probability, ... no tighter than 2–100% at 95%"*; L787-790 *"P(rank 1) = 68%, an estimate eight cases pin no tighter than 2–100% at 95%"*; L807 *"the rank the good end promised is worth 68% — 2–100% at 95%"*; L858-859 *"the overall row's rank carries P(rank 1) = 68% (2–100% at 95%)"*; L877 table cell *"rank 1 of 5, scored locally; P 68% (2–100% at 95%)"*. This is the textbook case the brief warned about — a repair pass fixed the front matter and missed a restatement deeper in the same document. (One further instance, L2359, `P(rank 1) = 0.674` inside a provenance/changelog table citing what a specific past artifact established — read as historical citation, lower confidence as a live defect, flagged for judgment rather than counted.) | `git grep -n "68\\\\%\|2--100\\\\%\|rank 1 of 5"` against the file, quoted above with line numbers. |
| 5 | `sdk/scripts/build_benchmarks.py:99-101` (and everything it generates) | `_CLOSURE["target_rank"] = 4`, `target_overall = 0.0779`, `target_per_case = [Montoya's 8 values]` — unchanged since before the board moved from 4→6 entries. Montoya is now **rank 6 of 6** on the live board, not 4. This literal is a straight passthrough into `benchmarks.json` (confirmed: `target_rank: 4` present in the committed file) and into `wall/wall.json` (same value, confirmed by reading `research.closure.target_rank` in the committed JSON) via `lab_stats.research_programs()`. It is then **rendered live**: `sdk/chief_engineer/control_room.html:2311` does `` `Public leaderboard, rank #${cl.target_rank} entry: overall ${cl.target_overall.toFixed(4)}` `` — i.e. the control room UI currently displays "rank #4 entry: overall 0.0779" for a value that is actually rank #6 on the board the rest of the same page (the `_CLOSURE["our_entry"]` prose, correctly repaired) describes as six entries. Two tests, `sdk/tests/test_ledger_learning.py:238-239` and `sdk/tests/test_mega_batch.py:234-235`, assert `target_rank == 4` and `target_overall == 0.0779` — so fixing the generator constant without updating these tests will redden the suite; they currently encode the stale assumption as a passing expectation. **This is a generator-vs-current-state disagreement, not a generator-vs-output disagreement** — `benchmarks.json`/`wall.json` faithfully mirror what the generator emits; the generator itself never picked up the six-entry board for this one field, even though the adjacent `our_entry` narrative string in the same dict (lines 102–145) was fully and correctly repaired. Line 85's comment (`# ... rank 1 of 5 scored locally at benchmark commit deb91557 --`) is also stale but is a dead comment, not rendered data — noted for completeness at lower severity. | `git grep -n "target_rank" sdk/` across `build_benchmarks.py`, `lab_stats.py`, `control_room.html`, `test_ledger_learning.py`, `test_mega_batch.py`; `python3 -c "import json..."` on `benchmarks.json` confirms `target_rank: 4` in the committed output. |
| 6 | **`scripts/self_audit.py`** (the guard, not a claim surface — but load-bearing) | `_RANK_INTERVAL = re.compile("2\\s*[-‐-―]\\s*100\\s*%")` (line 425) is the **only** pattern the rank-claim-companion checker (`check_rank_claim_surfaces`, `_rank_companions_missing`) accepts as satisfying "the interval must travel with the figure." There is no reference anywhere in this file to `0-97`, `0–97`, `six-entry`, `six entrant`, or `Yang` (confirmed: zero `git grep` hits for all five). `_RANK_FIGURE = "P(rank 1)"` is a bare-token check — it validates the *label* is present, never the *number*, so it cannot distinguish a correctly-updated 50% claim from a stale 68% one. Two consequences, both real: (a) a surface that correctly states only the current `0–97% at 95%` interval, without also retaining the old `2-100%` string nearby, would be **falsely FAULTED** by this checker as missing its interval; (b) a surface that keeps the old `2-100%` text nearby as struck-and-kept history (which is the house style — see §0 and §3 below) **incidentally satisfies** the regex regardless of whether its live claim is current, because the search is a raw substring/regex test over the whole file with no strikethrough-awareness (documented in the function's own docstring: "one compliant paragraph clears every claim in that file"). So a green result from this specific check does not, on its own, confirm the live claim is the current 50%/0–97% figure — only that the string `2-100%` occurs somewhere in the file. `sdk/tests/test_rank_claim_surfaces.py` has zero references to `0-97`/`_RANK_INTERVAL`/`six-entry`/`Yang` either, so nothing in the test suite currently exercises or would catch this. This is a genuine generator/checker staleness, structurally more consequential than any single stale figure since it is the instrument the lab relies on to catch the rest. | `git grep -n "_RANK_INTERVAL\s*=\|0-97\|0–97\|six-entry\|Yang" scripts/self_audit.py sdk/tests/test_rank_claim_surfaces.py`; `Read` of `scripts/self_audit.py:415-474, 523-610`. |

## 2a. Additional LIVE-AND-STALE findings — corroboration pass

Two general-purpose agents were dispatched mid-sweep to cover the campaign/*.md bulk and a
second pass over structured/generator surfaces (methodology: `git grep`, plus positive
controls confirming no target path was gitignored). Per this report's own standing rule
("you must not be the author of anything you grade… establish facts by execution"), every
claim below was **independently re-verified by direct `Read`/`git grep`/`sed` execution
before inclusion** — none is taken on the agents' word alone. Line numbers and quotes are
from my own re-read.

| # | Surface | What's stale | Verified evidence |
|---|---|---|---|
| 7 | `demo-output/website/ACTIVE_RESEARCH.md:583` | *"Best-on-board now 4 of 8 (both alpha_15, both alpha_05)."* Live, unstruck, no dated note, no RANS-baseline disclosure. Canonical current value is 2 of 8 (0 of 8 model's own). | Read L575-590: confirmed unstruck, sits inside the round-5-acceptance narrative with no forward pointer to the six-entry recompute. |
| 8 | `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:504` | *"Best-on-board count drops **5 of 8 → 4 of 8**."* Same defect; this sits in §0f, the section this file's own later block (L536-564) correctly repairs for P(rank1)/interval/board — but never revisits this count. | Read L495-525: confirmed live, unstruck; the file's correct six-entry update block is 30+ lines below and never mentions best-on-board. |
| 9 | `demo-output/website/agenda/CHALLENGE_LANDSCAPE.md:104` | *"best-on-board is **4 of 8**"* sits inside a blockquote explicitly headed **"Superseded 2026-08-07"** — i.e. a dated correction whose own content is now itself stale a second time (board moved again 2026-08-11) and was never re-corrected. The correctly-updated P(rank1)/interval/board block sits immediately below (L108-124) but addresses only the probability, not this count. | Read L95-129: confirmed exact nesting — a "superseded" note that is itself superseded and doesn't know it. |
| 10 | `demo-output/website/agenda/CHALLENGE_LANDSCAPE.md:134-138` | *"'Best on five of eight' was withdrawn... two clear leads, one nominal, two baseline rows, three behind."* States the four-entry-board-era attribution as the standing correction ("must not come back"), unstruck, never updated for the six-entry board's 2-of-8/0-of-8 result. | Read L131-140, same block. |
| 11 | **`demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §10, L1441-1488** | **The most serious single finding in this sweep.** A blockquote titled *"Wording note — CORRECTED 2026-08-11. What stood here was stale, and this document contradicted itself about the same figure in two places."* — sitting **20-40 lines below** the document's own correct 50%/0–97%/six-entry figures (L1425-1428, in the same §10) — itself concludes: *"The rule that now governs every rank claim in this package… carries **P(rank 1) = 68%** (67.6%…) together with its interval: **2–100% at 95%**…"*, unstruck, presented as the authoritative current rule. This is a genuine self-contradiction inside one section of one file: the document fixed itself once (withdrawing an internal/external split, both dated 2026-08-10) and that fix is correctly labeled "CORRECTED 2026-08-11" — but a second, later wave of staleness (the six-entry board move, also 2026-08-11 but at 23:33Z, after this note was written) landed on top of it and was never caught. The label "CORRECTED" is doing real damage here: it reads as settled to anyone who doesn't check the date-of-day against `BOARD_MOVED_2026-08-11.md`. | Full read, L1415-1520, quoted in-place; reproduced verbatim above. |
| 12 | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`, end of the same §10 block (~L1504-1508) | *"Best-on-board is now **4 of 8**, not 5 of 8; §5.3 and the cover email's item 2 must say 4."* Same file's own §5.2 (L690-700, verified LIVE-AND-CORRECT with the ZERO-of-8 disclosure) already supersedes this, but this later passage was never reconciled against it — two different best-on-board counts stand unresolved in the same document. | Read confirms exact text and the contradiction with L690-700. |
| 13 | `demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md:53,65` | This is the file every other repaired surface **cites as the source of the V8 rule** ("Source: `campaign/LADDER_V_TRIPLE_VERIFICATION.md`, V8 amendment 2026-08-10"). It states the rule itself using the stale interval and stale not-decided pair list, unstruck: L53 *"not-decided pairs (currently Reissmann and Wu & Zhang; Liu and Montoya are decided)"* — missing Yang and Tian entirely; L65 *"tighter than 2–100% at 95%"*. `git grep -c "six-entry\|50.2\|0-97\|0–97\|Yang" LADDER_V_TRIPLE_VERIFICATION.md` returns **zero** — this file was never touched by the six-entry recomputation at all, even though dozens of other files cite it as their authority. | Read L45-70 confirmed exact quotes; `git grep -c` confirmed zero hits for every six-entry-era token. |
| 14 | `demo-output/website/campaign/COLD_START_TEST_2026-08-11.md:327-328, 387-388` | States the 68%/2-100% interval as the governing "Claims" rule (L327-328) and repeats it in a risk-scenario narrative (L387-388), unstruck, no forward pointer. **Mitigated but not excused**: the file timestamps itself 01:13-01:17 UTC on 2026-08-11 (L6, L434), which is genuinely *before* the board-move discovery at 23:33 UTC the same day — so it was accurate when written. But nothing marks it as time-bound, and a reader today has no signal that a same-day, same-file-name event superseded it hours later. | Read L320-335, L382-392, and timestamp lines L6/L100/L434 confirmed. |
| 15 | `demo-output/website/latex/closure_challenge_report.tex:201` | The document's own section header claims blanket coverage: *"The board moved on 2026-08-11, and every probability in this document is struck"* (`\subsubsection*`, L201, `\label{sec:boardmoved}`). This claim is **false in its own scope** — item #4 in §2 above lists ~6 unstruck live instances of exactly the probability this header claims to have struck everywhere. This reframes item #4: it isn't merely an incomplete repair, it's a document that explicitly and incorrectly asserts completeness. | Read L195-215, confirmed banner wording verbatim. |
| 16 | `closure_challenge_report.tex`, `tab:prank` (L304-321) | Cited repeatedly elsewhere in the *correctly-repaired* prose (L66, L259-262, L361 area) as the evidentiary table behind "P(rank 1) = 50%, four leads not statistically decided" — but the table itself (caption cites the superseded `PROBABILITY_OF_RANK_2026-08-10.md`) has only **4 rows**: Reissmann, Wu & Zhang, Liu, Montoya. Yang and Tian/Buchanan/Hickel/Dwight are **entirely absent** from the table a correct, live sentence points readers to. The table is not struck; it sits directly under a `\sout{}`-struck old-figure line, but is itself the un-struck, un-replaced, stale artifact. | Read L295-321, confirmed table has exactly 4 tabular rows and the caption's cited source. |
| 17 | `closure_challenge_report.tex`, §`sec:bestonboard`/`sec:attribution` (L882-932) | An entire subsection, ironically titled *"How the 'best on board' count must be reported,"* is itself unreported-correctly: live prose *"we hold the best score on the public board on four of eight cases"* and `tab:attribution` states *"Our model, clear lead: **2**"* on both `alpha_15` cases — but the document's own §`sec:boardmoved` (L234) already discloses those two cases were **lost** to Tian/Buchanan/Hickel/Dwight on the six-entry board, making the model's true clear-lead count **zero**, not two. The only acknowledgment anywhere in the document is a single forward pointer at L234 (*"§sec:bestonboard is superseded accordingly"*) — a reader who reaches §sec:bestonboard on its own (via the table reference, a search, or straight-through reading) sees no correction in the section itself. | Read L880-932 in full, confirmed live prose and table contents; confirmed the only pointer is the single upstream L234 clause, not repeated at the section itself. |
| 18 | `scripts/self_audit.py:329-332` | `check_closure_wall()`'s own logic: `if re.search(r"\b(three\|five) of the eight\b", ...)`, flags **that** as stale and states in its own fault message *"round 5 records four of eight (the AR_14 tie was lost, priced in writing)"* — i.e. the checker's hardcoded ground truth for "best-on-board count" is **4 of 8**, which is now itself the superseded value; canonical current is **2 of 8** (0 of 8 model's own). This is backwards from item #6's failure mode (missing recognition) — here the checker actively asserts a wrong value as correct, so it would **fault a currently-correct "2 of 8" statement** as if it were the error. | Read `scripts/self_audit.py:323-338` directly, quoted verbatim above. |
| 19 | `sdk/tests/test_rank_claim_surfaces.py:98-99, 156-161` | `COMPLIANT = """On the published board our 0.0566 is rank 1 of 5, scored locally at deb91557. P(rank 1) = 68%, and eight cases cannot pin that tighter than 2-100% at 95%. ..."""` is the test suite's own canonical example of a *compliant* surface — hardcoded with the superseded rank-of-5/68%/2-100% figures, because the test only checks that the guard's companion-detection mechanism fires, not that the number is current (consistent with item #6's finding that `_RANK_FIGURE`/`_RANK_INTERVAL` are content-blind). More consequential: `test_the_live_page_carries_what_the_rule_requires` (L156-161) reads the **real** `closure.html` off disk and asserts `_rank_companions_missing(page) == []`. This currently passes — **but only because `closure.html` still contains the literal struck string `<s>P(rank 1) = 68%, 2–100% at 95%</s>`** as kept history (§3 above). The test's docstring claims it pins "what the rule requires" (i.e., the current rule), but it would pass identically on a page whose live claim used the wrong number, and it would newly **fail** on a page that is fully compliant with the *current* rule but has since had its old struck text tidied away — since the regex has no strikethrough-awareness (confirmed in item #6). The test does not test what it says it tests. | Read `sdk/tests/test_rank_claim_surfaces.py:1-15, 95-127, 156-161` directly; cross-checked against the confirmed presence of the struck string in `closure.html` (§2, item #3 investigation). |
| 20 (soft) | `docs/PRODUCT_LIST.md:53` | *"**ROUND 5, 0.056647, RANK 1 OF 5**"* (bold, unstruck) heads the 4B changelog bullet. Unlike its sibling figures in the same bullet — P(rank1), interval, best-on-board, all of which get a proper dated `~~struck~~`/`**SUPERSEDED**` treatment 6-20 lines later in the identical bullet (L59-76, confirmed correct) — this specific headline phrase is never revisited to reflect the seven-entrant field (six board + us). A minor, self-inconsistent-treatment finding inside an otherwise well-maintained changelog entry, not counted with the harder LIVE-AND-STALE cluster above because the surrounding entry is explicitly historical/changelog in nature. | Read L50-77 directly, confirmed the bolded unstruck phrase and the correctly-struck siblings in the same bullet. |

**Not independently re-verified, included at agent-reported confidence only:** the corroborating
agent's `pytest`/module-import checks on `build_benchmarks.py`/`test_rank_claim_surfaces.py`
(reported as non-mutating, all green/agreeing with §2 item #5's manual trace) and the note that
`benchmarks.json`'s `generated_at: 2026-07-31T08:17:26Z` predates its own closure-section content
dates — consistent with hand-patching rather than a full regenerator run; a provenance flag, not a
numeric defect, so not counted in the summary below.

## 3. STRUCK-AND-KEPT (correct — verified, not a defect) — sampled surfaces

All of the following carry the full superseded set (68%, 67.6%, 2–100%, "rank 1 of 5",
four-entry board, 38–91% LOO, 52–81% seed) **only** under `~~...~~`, `<s>...</s>`, or a
dated "SUPERSEDED/STRUCK 2026-08-1x" note that correctly names the replacement, and were
individually verified to also carry the live-correct figures alongside:
`demo-output/website/CLOSURE_CHALLENGE_STATUS.md` (L536-564), `CLOSURE_RANK1_CAMPAIGN.md`
(L32-46), `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` (L92-169 — see harder case below),
`campaign/CHALLENGE_SLATE_2026-08.md` (L37), `agenda/CHALLENGE_LANDSCAPE.md` (L101-124),
`benchmarks.html`, `closure.html` (all instances except item #3 above),
`campaign/PROBABILITY_OF_RANK_2026-08-10.md` (see harder case below),
`agenda/proposals/probability-of-rank-a-posterior-over-our-score-against-the-board.json`
(the `supersession_note` field explicitly narrates why the 68%/2-100% figures it names are
historical and kept unedited by house policy — correct), `sdk/scripts/build_benchmarks.py`'s
`our_entry` string (correct; only `target_rank` sibling field, item #5, is stale),
`closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` (see §4, in-flight).

**The harder case, checked explicitly, found twice, both handled correctly:**
- `PROBABILITY_OF_RANK_2026-08-10.md` opens with a blanket banner "⛔ EVERY PROBABILITY IN
  THIS DOCUMENT IS SUPERSEDED." Checked whether anything live-and-current sits under it
  unacknowledged: no — lines 11-32, immediately under the banner, are a reconciliation table
  giving old-vs-new side by side (`~~68%~~` / `**50%**` etc.), so the blanket claim is true
  in its own scope and the live content is explicitly marked as such, not silently exempted.
- `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md:100-169` has the identical shape: "(c) and (d)…
  EVERY FIGURE… IS SUPERSEDED — SEE (e)," followed by the struck original text kept verbatim,
  then "(e) RECOMPUTED 2026-08-11" restating all figures correctly (50%, 0–97%, four
  not-decided incl. new leader, three-deletion-wide standing, seed bound crossing the rank
  boundary). Correct.

## 4. In-flight, excluded from action (per instructions — flag only)

`demo-output/website/closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`, being
repaired by another agent concurrently. Snapshot at time of sweep: appears well-repaired —
headline (L3) states bare `0.056647` (acceptable, not a rank claim); the P(rank 1) section
(L300-397) properly strikes 68%/67.6%/38–91%/2–100%/52–81% with dated "struck 2026-08-12"
notes beside live 50.2%/34.2%/65.4%/78.5%/0–97% figures; best-on-board (L83-99) uses the
dated-supersession pattern correctly, disclosing 2-of-8→0-of-8 RANS baseline. **Do not act
on this row — it was mid-repair when read and may have changed again by the time this is
read.**

## 5. Bare-figure caveat-travel violations

None found as **live** violations. Every live P(rank 1)/50%/68% occurrence located in this
sweep carries its interval and (post-2026-08-11) its board in the same sentence or adjacent
clause — including the stale cluster in item #4 above, which is wrong on the *number* but
not on the *pattern* (it still states "68%… 2–100% at 95%… not statistically decided"
together). The one exception is the checker itself (item #6): because `_RANK_FIGURE` is a
bare-token match, `self_audit.py` cannot itself detect a bare-figure violation that uses the
*correct* number — it would only catch a bare `P(rank 1)` token with no interval nearby, not
a bare `50%` with no `P(rank 1)` label. Not evidenced as exploited in this sweep, but it is a
structural gap in the guard, consistent with item #6.

## 6. What I did not find

- No live four-entry-board framing anywhere in `benchmarks.html`, `closure.html`,
  `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md`, `CHALLENGE_LANDSCAPE.md`,
  `CLOSURE_CHALLENGE_STATUS.md`, or the LaTeX front matter — all correctly show six entries
  and Yang as leader.
- No live "38–91%" or "52–81%" anywhere (only struck, in `DESCRIPTION_DOCUMENT.md` and the
  LaTeX front matter).
- `docs/PRODUCT_LIST.md` and `docs/DOCKET.md` are append-only chronological logs; their many
  historical mentions of 68%/rank-1-of-5/four entries are narration of past events, not live
  claims, and are correctly out of scope for this classification (confirmed by reading the
  tail of `PRODUCT_LIST.md`, which is current and rank-neutral).

## Summary counts

- LIVE-AND-STALE: **19 findings** (items #1-19 above; item #20 is a soft/minor finding kept
  separate), every one confirmed by this grader's own direct execution (`Read`/`git grep`/
  `sed`/`python3 zipfile`) — none accepted on a subagent's word alone, per this task's own
  no-summary-trusting rule. By class:
  - Shipping artifacts: tracked zip (#1) + its untracked twin (#2).
  - Best-on-board count drift (a defect class this grader's first pass missed entirely,
    caught by the corroboration sweep and independently re-verified): #7, #8, #9, #10, #12,
    #17.
  - One stray unstruck sentence: closure.html:502 (#3).
  - The LaTeX report, now understood as **structurally**, not just incompletely, stale: a
    section-header banner that falsely claims full coverage (#15), a whole later
    probability-narrative section it failed to cover (#4, ~6 instances), a table cited by
    correct prose but never updated itself (#16), and a whole subsection with its own table
    stale in place behind a single easy-to-miss forward pointer (#17).
  - `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`'s self-contradictory "CORRECTED 2026-08-11" block
    that reinstates the stale rule as governing, 20-40 lines below the correct figures in the
    same section (#11) — the single most consequential finding in this sweep, plus one more
    uncorrected best-on-board count in the same file (#12).
  - The V8 rule's own cited source-of-truth file, never updated for the six-entry board
    despite being what every other repaired surface points to as its authority (#13).
  - One time-bound file, mitigated but unflagged for a later reader (#14).
  - The generator literal (#5, `build_benchmarks.py`'s `target_rank`/`target_overall`),
    propagating into 2 JSON outputs, 1 live-rendered UI surface, and 2 tests.
  - The guard itself, stale in **two independent, opposite-failure-mode ways**: its interval
    regex cannot recognize the current interval at all (#6), and its best-on-board regex
    actively asserts the superseded "4 of 8" as ground truth (#18) — undermining confidence
    in every PASS either check has issued since 2026-08-11.
  - The test suite baking the stale figure in as its own "compliant" fixture, and one test
    that passes for the wrong reason and would fail on genuinely-correct content once old
    struck text is tidied away (#19).
- Soft/minor, not counted in the 19: `docs/PRODUCT_LIST.md:53` (#20) — inconsistent
  treatment within an otherwise well-maintained changelog bullet.
- STRUCK-AND-KEPT verified correct: 10+ surfaces sampled, including two "blanket notice over
  a mixture" cases that were both checked explicitly and found to be honest in their own
  scope — a sharp contrast with the LaTeX report's banner (#15), which makes the identical
  claim and is false.
- In-flight, not counted either way: `DESCRIPTION_DOCUMENT.md`.
