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

No retrieval newer than 2026-08-11 existed in the tree before this one. A sweep of the tree at
`45922a65` — tracked files and gitignored ones alike, the latter with GNU `grep` at
`/usr/bin/grep` because the `grep` on PATH is ugrep and honours `.gitignore` (L-75) — found
**exactly two board-fetch timestamps in existence anywhere**: `2026-08-11T23:33Z` and this
document's `2026-08-14T21:01Z`. This document is now the newest retrieval the lab holds.

### 1.3 A third, independent corroboration was already in the tree and had not been connected

`demo-output/website/CLOSURE_SUBMISSION_REQUIREMENTS.md` §1 records that **Katie pasted the
challenge's live GitHub README on 2026-08-12**, by hand — *"The fleet did not fetch it; no
network read of the upstream repo was made for this document."* That document's purpose was
the submission procedure, but it states in passing that the page Katie pasted carried **Yang
at 0.0580 at rank 1** on a six-row leaderboard, and it names the **upstream HEAD as
`d572d40c`**.

**The board therefore has three independent confirmations at three dates by three routes:**
the fleet's two-route fetch of 2026-08-11T23:33Z, Katie's human paste of 2026-08-12, and the
read-only fetch of 2026-08-14T21:01Z recorded here. They agree. The 08-12 corroboration was
sitting in a document about submission procedure and had not been read as board evidence by
anything that reasons about the board — which is worth noting in its own right, since it is
the same shape as the finding `BOARD_MOVED_2026-08-11.md` §5 generalises: an artifact holding
a fact for one purpose, unread by the purpose that needed it.

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

*Basis note, added 2026-08-15 (the only placement of it in this corpus).* Because the board
publishes per-case values to 4 dp, every margin in this table carries ±5e-5 from the board's
printing alone; the six-decimal forms are the precision of the derivation, not a claim of
accuracy to 1e-6. The margin over **Yang** on the **six-entry** board retrieved
**2026-08-11T23:33Z** and re-verified unchanged **2026-08-14T21:01Z** is **0.001365** as
derived and **[0.00132, 0.00140]** on what the board's printings support; against it the seed
bound stands at **177%** as derived and **172%–184%** across that interval — it exceeds the
margin at every point of the range. Nothing in this table is rewritten by this note; the
figures are the correctly-rounded printings of the derivation and they stand. Measured by
interval propagation in `campaign/MARGIN_PRECISION_INTERVAL_2026-08-15.md` §2.3–2.5, committed
`eadcd112`; docket **D127**.

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
| Wu & Zhang | 84.7% | −0.953 | 0.017102 | ~~5/8~~ **4 or 5 of 8** ‡ | **not statistically decided** |
| Tian, Buchanan, Hickel & Dwight | 86.0% | −1.033 | 0.020512 | 5/8 | **not statistically decided** |
| Liu, Wang, Zhao & Xiao | 98.7% | −2.203 | 0.021875 | 7/8 | decided |
| Montoya, Oulghelou & Cinnella | 99.8% | −2.912 | 0.020608 | 7/8 | decided |

**Four of six pairwise comparisons are not statistically decided; two are.** Against Yang the
paired t is −0.189 and the per-case dispersion is 0.0204 — **fifteen times the 0.001365
margin**, and four of eight cases go to Yang.

**‡ REPAIRED 2026-08-15. The Wu & Zhang cases-won cell now reads `4 or 5 of 8`, because the
published board cannot say which — and the verdict is unchanged.** The struck `5/8` is left
visible above. *What falsified it:* the interval propagation in
`campaign/MARGIN_PRECISION_INTERVAL_2026-08-15.md` §3.1, committed `eadcd112`, filed as
`docs/DOCKET.md` **D133**, and re-derived cell by cell before this edit rather than taken on
report. One of the five cases counted as won is `AR_1_Ret_360`: our
`0.04547044480564218` against Wu & Zhang's **printed** `0.0455`. The board publishes per-case
values to four decimals, so `0.0455` denotes a true value anywhere in
**[0.045450, 0.045550]** — a half-ulp of ±5e-5 — and **our value lies inside that interval**,
2.96e-5 away, which is **0.59 of a half-ulp**. Whether we won that case is therefore not
determined by anything the board publishes, and no work on our side can determine it: our
per-case values are already full doubles, so the interval closes only if the organisers print
more digits.

**Re-derived over all 48 cells of the six-entry board** (`LIVE_BOARD` read by `ast` from
`sdk/scripts/probability_of_rank.py`, never imported; ours from
`closure_challenge_round5_qcr.json` → `round5_per_case_full`; every `__pycache__` purged
first): **`AR_1_Ret_360` against Wu & Zhang is the only cell of the 48 below the half-ulp.**
The three smallest gaps on the board are all in Wu & Zhang's own column — 0.59, then
**1.64** half-ulps (`AR_3_Ret_360`, 8.22e-5) and **6.77** (`AR_14_Ret_180`, 3.39e-4) — and
outside that column the smallest per-case gap anywhere is **26.2 half-ulps**. **No other
cases-won cell in this table is affected.** Tian's `5/8`, Yang's and Reissmann's `4/8` and
both `7/8` rows were re-derived and every one of their eight cells is determined; in
particular Tian's `5/8` is exact and shares nothing with this defect but the integer.

**This is an accuracy repair and not a retreat, and it must not be read as one.** "Decided"
requires **≥ 7 of 8** cases won (`DECIDED_WINS = 7` in the script, alongside P ≥ 0.98 and
|t| > 2.0). The verdict against Wu & Zhang is **not statistically decided** at 4 and at 5
alike; P(we lead), the paired *t* and the sd are unmoved. §3.1's standing, §3.2's P(rank 1),
§3.4's robustness checks and §4's claim sentence are all untouched. What changes is that the
cell now says what is known instead of asserting a resolution the published data cannot
supply **in either direction** — writing a bare `4/8` here would be the same error mirrored,
and it is not written.

This also makes the table agree with two live surfaces that already carried the correct
reading and had been disagreeing with it: `demo-output/website/CLOSURE_CHALLENGE_STATUS.md`
(*"`AR_1_Ret_360` and `AR_3_Ret_360` are ties below published precision … and are not
per-case wins or losses"*) and `docs/PRODUCT_LIST.md` (*"AR_1/AR_3 margins … are ties below
published precision and must never be quoted as per-case wins"*). On `AR_3_Ret_360` those two
surfaces are **more cautious than the half-ulp model rather than wrong**: that gap is 1.64
half-ulps, so it is determined under rounding — Wu & Zhang win it — and it reads as a tie only
under a full-ulp convention.

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
correction.

**Measured at `45922a65`, and the answer is that there is no convention.** Across tracked
`.md`, `.html`, `.tex` and `.json` surfaces, excluding solver run directories and logs:
**seventeen files carry both forms**, among them `closure.html` (0.056647 ×2, 0.0566 ×11),
`CLOSURE_CHALLENGE_STATUS.md` (×7 / ×10), `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` (×13 / ×2),
`ACTIVE_RESEARCH.md` (×3 / ×5), `docs/PRODUCT_LIST.md` (×5 / ×5) and this document.
Several surfaces carry only the 4 dp form — including three that travel or are generated:
`benchmarks.html`, `benchmarks.json` and `wall/wall.json`.

**So the two roundings are not used consistently, and no surface anywhere states that they are
the same number.** This is recorded as a finding, not repaired: both forms are faithful, no
figure is wrong, and rewriting hundreds of instances across live surfaces during an open
verification is precisely the kind of sweep that introduces the error it means to prevent.
What is cheap and would settle it is one sentence, once, wherever the entry score is first
defined, saying that 0.0566 is 0.056647191704213645 to the board's own precision.

*Caveat on the measurement, so it is not over-read.* The `0.0566`-only list also contains
files where the string is a numeric coincidence in field data rather than our entry score —
`demo-output/plots/pressure_slices/validation/regenerated/b52_field.json`,
`naca4412_wing_field.json` and `demo-output/website/dafoam/ladder-a/A2_shape_frames.json`.
Those are not rank surfaces and were not counted as such. The seventeen both-forms files were
each confirmed to be discussing the closure entry.

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

### 7.2 Two further findings from the sweep, both filed rather than fixed

**D58 — a board date with no retrieval behind it.**
`demo-output/website/campaign/CLOSURE_STAGE1_AND_C2_STATUS.md:443` reads *"the live
leaderboard **at 2026-08-05** has six rows, not four, with a new rank 1 (Yang, 0.0580) and a
new rank 4 (Tian, Buchanan, Hickel, Dwight, 0.0641)."* **No 2026-08-05 retrieval exists
anywhere in the tree** — §1.2's sweep found only the 08-11 and 08-14 timestamps, and the
earliest evidence for the six-row board is the 08-11T23:33Z fetch. **The sentence is not
falsified and is therefore NOT struck under L-76:** the board may well have had six rows on
2026-08-05, and striking a claim that has merely lost its source would misrepresent what is
known. What is wrong with it is its date and its tense, and the irony is exact — the paragraph
it sits in exists to complain that C2's *"leaderboard rows are undated in the table itself"*.
Filed as D58.

**D59 — three `docs/` surfaces the cross-surface sweep never classified.**
`docs/P33_CROSS_SURFACE_SWEEP.md` ruled `docs/PRODUCT_LIST.md` and `docs/DOCKET.md` out of
scope **by name**, as append-only chronological logs whose historical figures are quotations
rather than claims — a principled and defensible exclusion. `docs/HANDSHAKE.md`,
`docs/H4_ALLOCATION_AUDIT.md` and `docs/CAPABILITY_STRATEGY.md` are named **neither as swept
nor as excluded**, and each states the figure with no interval and no `not statistically
decided` on the same line (measured at `45922a65`: HANDSHAKE.md L39, L42, L111, L272;
H4_ALLOCATION_AUDIT.md L75, L349; CAPABILITY_STRATEGY.md L82, L85). **Most of those instances
read as the same chronological-log class already excluded** — commit-subject recaps and
descriptions of other surfaces' staleness. `docs/HANDSHAKE.md:111` is the one that does not:
*"(P(rank 1) now 50%, board now …"* states the figure as current. **The finding filed is the
classification gap, not a count of violations** — asserting nine breaches here would be
claiming more than was measured, and re-drawing the line between a claim and a quotation to
make a number come out is the failure D54 already names. Filed as D59.

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
