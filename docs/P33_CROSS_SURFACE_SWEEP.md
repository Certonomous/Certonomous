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

- LIVE-AND-STALE: **6 findings** across 6 distinct surface classes — tracked zip (1), its
  untracked twin (1), one stray sentence in `closure.html` (1), a whole later section of the
  LaTeX report (1, ~6 line-instances), one generator literal propagating into 2 JSON outputs
  + 1 live-rendered HTML surface + 2 tests (1 root cause, 5 downstream effects), and the
  guard script's own interval regex (1 root cause, undermines confidence in every other PASS
  it has issued since 2026-08-11).
- STRUCK-AND-KEPT verified correct: 10+ surfaces sampled, including two "blanket notice over
  a mixture" cases that were both checked explicitly and found to be honest in their own
  scope.
- In-flight, not counted either way: `DESCRIPTION_DOCUMENT.md`.
