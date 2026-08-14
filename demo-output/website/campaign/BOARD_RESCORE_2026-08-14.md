# The live-board re-score (B-1): 0.056647 against the six-entry board, recomputed

**[OPUS-A], 2026-08-14, at repo commit `45922a65`.** Recomputed, not transcribed.

**This is a state claim and it carries its anchor** (W-5): *as of the retrievals recorded in
§1, the board read as below, and the figures in §3 were produced by the run in §2.* The board
will move again. Every number here is a claim about a board at a moment.

**Nothing has been submitted, sent, emailed, filed, uploaded or registered.** Submissions are
PARKED and reserved to Katie. §5 drafts a sentence *for* Katie; it is not an outbound artifact
and it has not been placed in one. The only network action taken in producing this document
was a read-only HTTP GET of a public README (§1.2), which is a retrieval, not a submission.

---

## 1. The board of record, and whether it is still current

### 1.1 The board of record

`demo-output/website/campaign/BOARD_MOVED_2026-08-11.md` (committed `9cb2a20a`) is the
board of record. It records a six-entry leaderboard **fetched 2026-08-11T23:33Z** from
`raw.githubusercontent.com/rmcconke/closure-challenge-benchmark/main/README.md`
(sha256 `1f124a8857a6b611832478879fc22ff353ee3308434b966849d4f29946d85c5b`), corroborated at
the time by a second fetch of the rendered project page.

The six overall scores were **re-parsed out of that markdown file mechanically** for this
re-score, not read across from any intermediate document, and checked against the
`published_overall` block that `sdk/scripts/probability_of_rank.py` computes from. They agree
on all six rows: Yang 0.0580, Reissmann/Fang/Sandberg 0.0595, Wu & Zhang 0.0624,
Tian/Buchanan/Hickel/Dwight 0.0641, Liu/Wang/Zhao/Xiao 0.0737, Montoya/Oulghelou/Cinnella
0.0779.

### 1.2 A freshness check was performed, and it was a fetch

**I fetched the live board.** Read-only HTTP GET of
`https://raw.githubusercontent.com/rmcconke/closure-challenge-benchmark/main/README.md`,
**retrieved 2026-08-14T21:01Z**. This is stated plainly because the whole finding of
`BOARD_MOVED_2026-08-11.md` is that a board read from a frozen artifact ages silently, and
because the check that document recommends costs exactly one fetch.

**The live board at 2026-08-14T21:01Z is unchanged from the 2026-08-11T23:33Z retrieval.**
Six entries; the same ranks, the same author lists, the same six overall scores, and the same
forty-eight per-case values across the same eight case columns. The board of record is
therefore **current as of 2026-08-14T21:01Z**, and the eight case columns remain unchanged, so
the scores are still like-for-like against ours.

No retrieval newer than 2026-08-11 existed in the tree before this one. This document is now
the newest retrieval the lab holds.

## 2. What was run, and on what

    python3 sdk/scripts/probability_of_rank.py --json <scratch>/rank_live.json

`sdk/scripts/probability_of_rank.py` (committed `5c9c63fb`) is the authoritative
recomputation. It was **re-run for this document**; no stored output was cited. Its `__pycache__`
was cleared first.

* **Zero solver calls. Zero scoring calls.** The script reads numbers already on disk.
* **Our entry is read from its machine record**, not transcribed:
  `demo-output/website/closure_challenge_round5_qcr.json` (anchor `1b982ae1`),
  `official_test_harness_result.round5_per_case_full`, whose eight values mean to
  `round5_overall_full` = **0.056647191704213645** exactly. The script refuses to run if they
  do not.
* **The frozen benchmark pin was not moved.** `~/closure-challenge-benchmark` stays at
  `deb9155`; it scores, it does not rank. Ranking numbers came from the live README.
* **Section 0's reproduction check passed for all six rows** — each row's eight published
  per-case values average to its published overall. Had any row failed, the run aborts.

## 3. The derived standings

### 3.1 The full board with our entry placed

Board scores are the means of the published per-case values (shown to 6 dp; the board
publishes them to 4 dp). Lower is better. Our margin is ours minus theirs — negative is ahead.

| Rank | Entry | Overall | Our margin | Pairwise verdict |
|---|---|---|---|---|
| **1** | **Ours (local scoring, NOT an official placement)** | **0.056647** | — | — |
| 2 | Yang | 0.058013 | −0.001365 | **not statistically decided** |
| 3 | Reissmann, Fang, and Sandberg | 0.059525 | −0.002878 | **not statistically decided** |
| 4 | Wu and Zhang | 0.062412 | −0.005765 | **not statistically decided** |
| 5 | Tian, Buchanan, Hickel, Dwight | 0.064138 | −0.007490 | **not statistically decided** |
| 6 | Liu, Wang, Zhao, and Xiao | 0.073687 | −0.017040 | decided |
| 7 | Montoya, Oulghelou, and Cinnella | 0.077863 | −0.021215 | decided |

**Point rank 1 of 7.** The board's own six entries keep the ranks it publishes (Yang 1 through
Montoya 6); the table above is the seven-way standing with our entry inserted.

### 3.2 P(rank 1), recomputed

400,000-draw case-level bootstrap over the eight cases, seed 20260810:

| rank | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| share | **50.15%** | 19.00% | 14.65% | 10.56% | 4.68% | 0.77% | 0.18% |

* **P(rank 1) = 50.2%** — precisely 0.5015225, i.e. **200,609 of 400,000 draws**.
* **Monte-Carlo Wilson 95%: 49.997% – 50.307%.** This says only that the resampling ran long
  enough. **It is not the interval that ships.**
* **Double bootstrap, 2,000 outer × 4,000 inner, seed 31415 — this is the interval that
  ships:** **95% band 0.25% – 96.90%**, quoted as **0–97%**. 68% band 11.99% – 80.63%. In 1.55%
  of outer resamples P(rank 1) came out exactly 0.

  *Reproduction note.* The script's own console line prints the lower endpoint as `0.2%`
  because `f"{0.25:.1f}"` rounds half-to-even in Python. The stored value is exactly 0.25.
  Both round to **0** in the shipped `0–97%`, so the shipped interval is unaffected; the
  precise endpoints are recorded here so a future reader does not read `0.2` and `0.25` as a
  disagreement between two runs. They are one run, displayed two ways.

Eight cases cannot pin a probability of rank tighter than that. The width is the finding.

### 3.3 Which comparisons are decided

"Decided" requires all three of P(we lead) ≥ 0.98, |t| > 2.0, and ≥ 7 of 8 cases won — the
thresholds are in the script so they can be argued with rather than inferred from prose.

| Entry | P(we lead) | paired t | sd | cases won | verdict |
|---|---|---|---|---|---|
| Yang | 57.8% | −0.189 | 0.020441 | 4/8 | **not statistically decided** |
| Reissmann, Fang & Sandberg | 69.4% | −0.495 | 0.016436 | 4/8 | **not statistically decided** |
| Wu & Zhang | 84.7% | −0.953 | 0.017102 | 5/8 | **not statistically decided** |
| Tian, Buchanan, Hickel & Dwight | 86.0% | −1.033 | 0.020512 | 5/8 | **not statistically decided** |
| Liu, Wang, Zhao & Xiao | 98.7% | −2.203 | 0.021875 | 7/8 | decided |
| Montoya, Oulghelou & Cinnella | 99.8% | −2.912 | 0.020608 | 7/8 | decided |

**Four of six pairwise comparisons are not statistically decided; two are.** Against Yang the
paired t is −0.189 and the per-case dispersion is 0.0204 — **fifteen times the 0.001365
margin**, and four of eight cases go to Yang.

### 3.4 Two robustness checks that were also re-run

**Leave-one-case-out.** Dropping any one of the eight cases and re-ranking on the other seven:
our point rank **falls to 2 or 3 in three of the eight drops** (dropping
`alpha_15_13929_4048` → rank 2, `alpha_15_13929_2024` → rank 3, `alpha_05_4071_4048` → rank
2), with P(rank 1) between 31.7% and 32.2% in those three. In the other five drops rank 1
holds, with P(rank 1) from 44.2% to 78.5%. **Three of eight single cases each individually
carry the point-rank-1 claim.**

**Seed spread.** Loading the truth-free ±0.0024 seed-spread bound on the three one-seed
PH cases: adverse → overall 0.059047, **point rank 2**, P(rank 1) 34.2%; as scored → 0.056647,
rank 1, 50.2%; favourable → 0.054247, rank 1, 65.4%. **The adverse end of our own seed
uncertainty loses rank 1 on points.**

## 4. The V8-compliant claim sentence

> Against the six-entry Closure Challenge leaderboard retrieved 2026-08-11T23:33Z and
> re-verified unchanged 2026-08-14T21:01Z, our entry's locally scored overall of 0.056647 is
> the lowest number on the board, but the lead is **not statistically decided**: a
> 400,000-draw case-level bootstrap over the eight cases puts P(rank 1) at 50.2%, which those
> eight cases pin no tighter than 0–97% at 95% (double bootstrap), and four of the six
> pairwise comparisons — Yang, Reissmann/Fang/Sandberg, Wu & Zhang, and
> Tian/Buchanan/Hickel/Dwight — are **not statistically decided**, only Liu/Wang/Zhao/Xiao and
> Montoya/Oulghelou/Cinnella being decided. This is local scoring, not an official placement;
> nothing has been submitted.

**No surface may state the figure without the interval** (V8). A bare "50%" is a worse claim
than none, because it converts a number whose honest width is nearly the whole unit interval
into an apparent coin-flip that a reader will take as precise.

## 5. Proposed cover-email first sentence — FOR KATIE, NOT SENT

**This is a draft for Katie's decision. It has not been sent, emailed, or placed in any
outbound artifact, and it must not be until she rules on it.**

> Scored locally against the eight cases of the Closure Challenge benchmark, our entry's
> overall of 0.056647 is below every score on the six-entry leaderboard retrieved
> 2026-08-11T23:33Z and re-verified unchanged 2026-08-14T21:01Z — though on eight cases that
> lead is **not statistically decided**: P(rank 1) = 50.2%, which the eight cases pin no
> tighter than 0–97% at 95%, with the comparisons against Yang, Reissmann/Fang/Sandberg, Wu &
> Zhang, and Tian/Buchanan/Hickel/Dwight all **not statistically decided**.

A shorter variant, if the first is too long to open on — same compliance, same tokens:

> Our entry scores 0.056647 against the eight Closure Challenge cases, below all six entries
> on the leaderboard retrieved 2026-08-11T23:33Z (re-verified 2026-08-14T21:01Z), but with
> P(rank 1) = 50.2% on a 400,000-draw case-level bootstrap — an interval of 0–97% at 95% —
> the lead over Yang, Reissmann/Fang/Sandberg, Wu & Zhang and Tian/Buchanan/Hickel/Dwight is
> **not statistically decided**.

Both variants carry the figure, the interval, the undecided pairs, and the literal string
`not statistically decided` that V10's cross-surface sweep greps for.

## 6. Rounding: 0.0566 vs 0.056647

The machine record holds 0.056647191704213645. **0.056647** (6 dp) and **0.0566** (4 dp, the
board's own precision) are both faithful roundings of it and neither is wrong. What would be
wrong is a surface that states one while a neighbouring surface states the other for the same
quantity without saying they are the same number — the reader cannot tell a rounding from a
correction. §7 records what the sweep found.

## 7. Reproduction and drift

Everything in §3 reproduced from the script on a clean `__pycache__`.

**The re-run is bit-for-bit identical to the committed record.** This re-score's JSON output
was compared field by field against `sdk/scripts/probability_of_rank_record.json` — the file
from which `sdk/tests/test_rank_claim_surfaces.py` builds its fixtures, so that they move when
the board moves. Every field is equal under exact comparison, not to a tolerance:
`p_rank1` 0.5015225; `double95` [0.0025, 0.9690374999999998]; `double68`
[0.11988, 0.80633]; `mc_wilson95` [0.49997301242113207, 0.5030719583360436]; `point_rank` 1;
`leader` Yang; and the whole `pairwise`, `loo` and `seed` sub-dictionaries compared equal as
objects. The `frame` block agrees on all seven fields including `our_overall`
0.056647191704213645.

That is the strongest available check that this is a reproduction and not a re-statement: the
figures were regenerated from the script and the machine record, and they landed on the stored
values exactly, without any number being read across from a document.

### 7.1 Nothing moved, and that is the result

**The re-derivation moved no published figure.** Every headline number this re-score produced
is identical to the one `PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md` (`5c9c63fb`) already
holds: P(rank 1) 50.2%, the count 200,609 of 400,000, the 95% band 0.25% – 96.90% quoted as
0–97%, four undecided pairs and two decided, point rank 1, and the leave-one-out and
seed-spread tables. **No L-76 strike is therefore triggered by this re-score**, because L-76
strikes *falsified* claims and nothing here was falsified. A re-score that changes nothing is
still worth committing: it converts a single-author computation into a reproduced one, and it
is the first live-board comparison performed since the board moved.

Two things are recorded rather than fixed:

1. **The `0.2` / `0.25` display artifact**, described in §3.2. Not a defect in any published
   figure — the shipped interval is `0–97%` either way — but recorded so it is not later read
   as two runs disagreeing.

2. **No scheduled freshness check on the live board exists.** `BOARD_MOVED_2026-08-11.md` §5
   recommends one and prices it at one fetch; `sdk/tests/test_rank_claim_surfaces.py`'s
   `test_the_committed_record_matches_the_board_on_disk` is the nearest thing built, and it
   compares the committed record against the board **on disk** — two committed artifacts.
   **Nothing in the tree compares either against the live board.** A sweep for one at
   `45922a65` found only prose recommending it. The fetch in §1.2 is a one-off act by one
   agent on one day, not a check, and it must not be mistaken for one. **Filed as docket D57**;
   it is not fixed here because building a network-dependent check has the costs D55 already
   priced, and choosing between them is not this task's to make.

The V16 board-pin staleness (the guard and `sdk/tests/test_rank_claim_surfaces.py` still
pinning the superseded four-entry `reissmann 1, wu 2, liu 3, montoya 4`) was observed again
and is **already recorded** — `BOARD_MOVED_2026-08-11.md` §3 and docket D48/D55. It is not
re-filed here; re-filing a known open item as new is how a docket inflates.

## Related

- `demo-output/website/campaign/BOARD_MOVED_2026-08-11.md` — the board of record (`9cb2a20a`).
- `sdk/scripts/probability_of_rank.py` — the authoritative recomputation (`5c9c63fb`).
- `demo-output/website/closure_challenge_round5_qcr.json` — our entry's machine record (`1b982ae1`).
- `demo-output/website/campaign/PROBABILITY_OF_RANK_2026-08-10.md` — the superseded 68% figure and its four-entry board.
- `LESSONS.md` L-39 (verdicts age silently), L-75 (frames), L-76 (strike and keep), L-79 (quoted figures rot).
