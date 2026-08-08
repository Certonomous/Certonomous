# Ladder V — rungs V2, V7, V10 executed 2026-08-08 (the three EXECUTABLE-NOW rungs)

Protocol: `LADDER_V_TRIPLE_VERIFICATION.md` @ `ac4a83e1` (2026-08-08T01:54:30Z).
Submissions are PARKED (Katie, 2026-08-07); this execution hardens the record and
prepares nothing for sending. **No scoring call was made or needed** — every check
below is static (git history, file bytes, CSV shape, text sweep). The ledger stands
at 6, untouched.

Executor: a verification agent that produced none of the round-5 work it verifies
(the pre-registration, the solves, the scoring call, and the surfaces were all
authored by other sessions). Verdicts are PASS/FAIL with evidence only; the chief
reviews.

---

## RUNG V2 — pre-registration chain: **PASS**

Method: `git log --format='%h %cI %s'` on the round-5 artifact paths; solver-log
mtimes and wall times from the surviving run tree
`/home/ubuntu/certonomous-runs/w3-qcr-rank1/` (per-arm `log.simpleFoam`,
`ledger.txt`); byte-hashes recomputed on disk.

### The chain, as a table (all times UTC)

| # | artifact | commit | timestamp | ordering proof |
|---|---|---|---|---|
| 1 | `campaign/R5_RULE_FREEZE.md` — the criterion that judged the solves: V1 (QCR/SST scaled-MAE ratio ≤ 0.70), V2 (in-plane r ≥ 0.85), V3 (converge on `residualControl`), all-or-none application, AR_14 loss accepted in writing | `0bade54a` | 2026-08-05T**17:41:06** | precedes every solve below |
| 2 | AR_7_Ret_180 QCR validation solve | — (run tree) | log finished 2026-08-05T**17:46:44**; wall 308 s ⇒ started ≥ 17:41:36 | started ≥ 30 s **after** the freeze commit |
| 3 | AR_7_Ret_180 SST validation solve | — (run tree) | log finished 2026-08-05T**17:47:01**; wall 325 s ⇒ started ≥ 17:41:36 | started **after** the freeze commit |
| 4 | AR_1_Ret_360 QCR test solve | — (run tree) | log finished 2026-08-07T**20:01:22** | 2 days after the freeze |
| 5 | AR_3_Ret_360 QCR test solve | — (run tree) | log finished 2026-08-07T**20:03:01** | after the freeze |
| 6 | AR_14_Ret_180 QCR test solve | — (run tree) | log finished 2026-08-07T**20:26:04** | after the freeze |
| 7 | `campaign/R5_PREREGISTRATION.md` + `R5_validation_AR7.json` + the 8 staged CSVs + `closure_challenge_round5_qcr_forward.json` — accept criterion (overall < 0.065438), expectation band (0.059–0.0666), AR_14 risk statement, §3 SHA-256 table | `e865076b` | 2026-08-07T**20:38:52** | after every solve, **before** the scoring call |
| 8 | 6th scoring call record — `closure_challenge_round5_qcr.json`, round-5 MANIFEST, status/board updates | `07a7fe9e` | 2026-08-07T**20:51:51** | last: 12m 59s after the pre-registration |

Every ordering the anti-hindsight argument needs holds with margin: the rule that
decided *where the model ships* (`0bade54a`) predates the first validation iteration
by at least 30 seconds and the test solves by two days; the *score-accept* criterion
and the hash-frozen prediction set (`e865076b`) predate the one scoring call by
13 minutes. Stated precisely, because the distinction matters: `0bade54a` froze the
gate that judged the solves; the numeric accept bar 0.065438 (= beat the round-4
entry of record) was frozen at `e865076b` — after the solves, which cannot inform it
(it is round 4's own already-public number), and before the call that judged it.

### 6th call vs its pre-registration: **MATCH**, clause by clause

| pre-registered (`e865076b`) | the call's record (`07a7fe9e`, `closure_challenge_round5_qcr.json`) | verdict |
|---|---|---|
| accept iff overall < 0.065438 (§5) | `verdict.accept_criterion` quotes §5 verbatim; measured 0.056647 < 0.065438 → ACCEPT | MATCH |
| expectation band 0.059–0.0666 (§5) | band recorded; result noted as landing below it, "recorded, not celebrated" | MATCH |
| exactly ONE scoring call, made by the supervisor's designee, not the producing session (§5, header) | `scoring_calls.this_run` = 1, cumulative = 6, `made_by` = the designated scoring agent 2026-08-07 | MATCH |
| all-or-none: 3 ducts QCR, 5 CSVs byte-identical to round 4 (§3) | 3 changed + 5 unchanged hashes recorded; unchanged 5 scored identically to round 4 | MATCH |
| §3 SHA-256 table, 8 files | recomputed on disk 2026-08-08 (`sha256sum` over `closure_challenge_submission_round5/test/`): **all 8 match §3 byte-for-byte** | MATCH |
| AR_14 risk accepted in writing; any regression reported, not reverted (§4, §5) | risk materialised (+0.0029, tie lost, 3 of 5), reported and not reverted, bundle judged as bundle | MATCH |

No clause was added, dropped, or re-thresholded between `e865076b` and `07a7fe9e`.

---

## RUNG V7 — the two known defects: **PASS** (defect (a) fix verified + 3 further count claims corrected; defect (b) artifact verified against the accepted format)

### (a) scoring-call count claims, all reconciled against the ledger (6 cumulative: floor, rounds 1–5)

The original false sentence (`apply_closure_ph_gate.py` docstring, "Exactly ONE
`score()`/`evaluate_by_case()` call is made") was fixed 2026-07-30
(SUBMISSION_DRAFT §4.4, RESOLVED). **Verified still true against the code**: the
docstring (lines 37–53) now says one *new* prediction set, four invocations, and
names both pairs — which is exactly what the code does
(`score`/`evaluate_by_case` on the floor at lines 218–219, on the entry at
lines 301–302).

Full grep of `sdk/` for count claims, each reconciled:

| file:line | claim | reconciliation | action |
|---|---|---|---|
| `sdk/scripts/apply_closure_ph_gate.py:37–53` | "4th official scoring call … after the floor, round 1, and round 2"; four invocations, two sets | true of round 3, correctly scoped, call sites verified (218–219, 301–302) | none — correct |
| `sdk/scripts/closure_round4_duct_rescale.py:38–40` | "official call #5 under the unit the ledger has always counted" | true of round 4, correctly scoped | none — correct |
| `sdk/scripts/closure_round5_qcr_forward.py:26–28` | "This script makes none … the ledger stays at 5" | true: that script made no call; the 6th came later, from the scoring agent | none — correct |
| `sdk/scripts/closure_criterion_on_test_features.py:10` | "Whether to spend a 5th official scoring call … is the coordinator's decision" | historical tense, dated to the round-3 era, makes no claim about the current count | none — noted |
| `sdk/scripts/closure_round4_manifest.py:135` | "The lab's ledger (five distinct prediction sets scored, **ever**)" | **false as a standing claim** since 2026-08-07 (the count is 6); "ever" was the same defect-shape as the original | **FIXED**: scoped to "as of this round-4 manifest; six after round 5's 2026-08-07 call" |
| `sdk/scripts/export_closure_submission_csvs.py:25` | quoted "four official scoring calls, ever" + "must not consume a fifth call" | **stale as standing text** (round-3-era script) | **FIXED**: scoped the quote to its writing date, stated the cumulative six, "fifth" → "new" |
| `sdk/scripts/build_benchmarks.py:19–21, 94–98, 101` | docstring "four pre-registered scoring calls"; `_CLOSURE["our_entry"]` "0.0676 … four … five of the eight"; `our_score = 0.0676` "(best measured position to date)" | **false as standing claims and a live regression trap**: the round-5 session hand-updated `benchmarks.json`/`wall.json` but left this generator literal at round 3, so its next run would have silently regressed the public page — the exact failure its own KEEP-IN-SYNC comment warns about | **FIXED**: docstring and `_CLOSURE` updated to round 5 / six calls / 0.0566; verified programmatically that the literal now reproduces the on-disk `benchmarks.json` `closure_challenge` block **exactly, key by key** |
| `sdk/tests/test_mega_batch.py:247` | "(0.056647, ACCEPT, the sixth pre-registered scoring call, commit 07a7fe9e)" | consistent with the ledger; file has other agents' uncommitted work | none — verified only, not touched |

Historical records (round-1–4 JSONs, dated reviews, the SUBMISSION_DRAFT's own
quoted-then-resolved defect text) carry period-correct counts and were left alone.

### (b) the submittable artifact, verified against the accepted format

Benchmark checkout: `/home/ubuntu/closure-challenge-benchmark` @
`deb91557184af3cb95f5190494ec52d8f2c6a0d1` (the frozen commit; `git log -1`
confirmed). The four accepted submissions in `submissions/` use two layouts:
flat `{case}.csv` (wu, montoya, wang) and per-case `{case}/predictions.csv`
(reissmann). The README instructs: interpolate to the evaluation points, save
CSVs in a `test` subdirectory, send that subdirectory.

The round-5 artifact `demo-output/website/closure_challenge_submission_round5/test/`
(committed at `e865076b`, MANIFEST at `07a7fe9e`) was verified on disk:

- **8 files, one per case, named `{case}.csv`** — the flat accepted layout, matching
  wu/montoya/wang and the eval loader's `folder/f"{case}.csv"` expectation;
- **every file 1000 rows × 3 columns, comma-delimited, no header, all values
  finite** (parsed row-by-row, first row float-parses — no header token);
- **all 8 SHA-256 match** the pre-registration §3 table and the split
  unchanged/changed tables in `closure_challenge_round5_qcr.json`;
- side-by-side with `submissions/wu/AR_14_Ret_180.csv` (1000×3, headerless): same
  shape, same delimiter, same column convention (Ux, Uy, Uz at the 1000 evaluation
  points), values of the same physical magnitude per column.

Already assembled, correctly formatted; nothing needed assembling. **Nothing was
sent anywhere; the artifact stays local and submissions stay parked.**

---

## RUNG V10 — cross-surface number sweep: **PASS after fixes** (two drifted surfaces found, both mine to fix, both fixed)

Numbers checked on every surface: 0.0566 / 0.056647; rank 1 of 5 **scored locally**
at `deb91557`, not an official placement, unsubmitted; six scoring calls; AR_14 tie
(the round-4 0.00003 nominal lead) **spent/lost** per the pre-registered risk;
best-on-board 4 of 8 (was 5); seed-uncertainty bound 0.0024 vs the 0.002878 margin;
duct gains from the **untrained** QCR2000 term (nothing fitted).

| surface | number shown | caveats present? | verdict |
|---|---|---|---|
| `demo-output/website/closure.html` | 0.0566 hero, 0.056647 in §2/§4 | rank-1-local (lines 95, 109, 338, 434), AR_14 tie lost + 0.00003 (line 304), seed bound comparable to margin (113, 346–353), untrained framing (155, 238, 293, 411) | **CONSISTENT** — no edit |
| `demo-output/website/ACTIVE_RESEARCH.md` | round 5 in header (11–19), standings table (624–639) with rank-1-local + "was five" best-on-board | yes throughout | **CONSISTENT after 2 fixes**: two round-4-era sentences read as present-tense with 0.0654 — the "Ambition ahead … its 0.0654" line (now scoped: 0.0566 since round 5, submissions parked) and the defect-2 parenthetical calling round 4 "the entry of record" (now points at the round-5 CSVs too) |
| `demo-output/website/wall/wall.json` | 0.0566, "six pre-registered scoring calls", "four of the eight", rank-1-local caveat verbatim | yes | **CONSISTENT** — no edit |
| `demo-output/website/wall/wall.html` | renders `wall.json`; carries no closure literal of its own | n/a | **CONSISTENT** — no edit |
| `demo-output/website/benchmarks.json` | 0.0566, six calls, round-5 per-case, rank-1-local caveat | yes | **CONSISTENT** — no edit |
| `demo-output/website/benchmarks.html` | **WAS: 0.0676, "4 scoring calls", "four … across three rounds", "5 of 8", round-3 duct per-case (0.0303/0.0862/0.0919)** — hand-maintained page last touched 2026-07-30, whole §1 a round-3 fossil | were absent | **DRIFTED → FIXED**: §1 rewritten to round 5 (0.0566, six calls, 4 of 8, round-5 duct rows with recomputed improvements −67.8/−64.7/−40.2%, AR_14 removed from the best-on-board table with the spent-tie note), rank-1-local caveat in the lede and the score tile, seed-bound-vs-margin and steward's-number caveats in the closing note, sources line updated |
| `docs/PRODUCT_LIST.md` §4B (READ-ONLY for this rung — chief-owned) | round 5, 0.056647, rank 1, 6th call, "Caveat everywhere: LOCAL scoring" | yes | **CONSISTENT on the numbers — NOT EDITED.** Two minor stale notes reported to the chief below |
| `demo-output/website/latex/closure_challenge_report.tex` (owned by its designated Opus writer — NOT EDITED) | 0.056647 throughout; "rank 1, stated once with its caveat attached" (215); AR_14 0.00003 priced-and-lost (85, 690, 715); seed bound 0.00242 vs margin (1731); untrained-QCR framing (261–262, 603+) | yes, thoroughly | **CONSISTENT — no drift to report** |

### Reported to the chief, not edited (chief-owned surface)

`docs/PRODUCT_LIST.md`, two stale sentences inside §4B — numbers are fine, the
staleness is in side-notes:

1. Line ~54–55: the NEW ITEM note "**closure.html coherent rewrite** … (page still
   shows round 4) — dispatched 2026-08-07". `closure.html` now shows round 5 with
   the full caveat set; the parenthetical no longer describes the page, and the
   dispatched item appears to be done.
2. Line ~56–57: "alpha=15,AR14 status: **still best-on-board**, but AR_14 lead
   collapsed to 0.00003 …" — after round 5, AR_14 is NOT best-on-board (tie lost,
   3 of 5) and best-on-board is 4 of 8. The crossed-off item above it says so; this
   older crossed-off line contradicts it if read alone.

Nothing to report on the `.tex`: it is current and carries every caveat.

---

## What changed during this verification (consolidated, per V13's future close-out)

| file | change |
|---|---|
| `sdk/scripts/build_benchmarks.py` | docstring + `_CLOSURE` literal synced from round 3 to round 5 (six calls, 0.0566, round-5 per-case, rank-1-local caveat); now byte-reproduces the live `benchmarks.json` closure block; regression-trap note added at the KEEP-IN-SYNC comment |
| `sdk/scripts/closure_round4_manifest.py` | "five … ever" scoped to the round-4 manifest, six-after-round-5 stated |
| `sdk/scripts/export_closure_submission_csvs.py` | round-3-era "four … ever" quote scoped and dated; "fifth call" → "new call" |
| `demo-output/website/benchmarks.html` | §1 updated round 3 → round 5 with all caveats (detail in the V10 table) |
| `demo-output/website/ACTIVE_RESEARCH.md` | two round-4-era present-tense sentences scoped to round 5 / the park |
| `demo-output/website/campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` | this report (new) |

Not touched, deliberately: `docs/PRODUCT_LIST.md` (chief's), the `.tex` (its Opus
writer's), `sdk/tests/test_mega_batch.py` and every other file with other agents'
uncommitted work, all historical JSON records, everything in
`/home/ubuntu/closure-challenge-benchmark` (frozen), and the scorer (never invoked).

## Verdicts

- **V2: PASS** — the chain is proven by commit timestamps and solver logs, and the 6th call MATCHES its pre-registration clause by clause.
- **V7: PASS** — defect (a)'s fix verified and three further stale count claims corrected in place; defect (b)'s artifact exists, is 1000×3 headerless in an accepted layout, and hash-matches its pre-registration.
- **V10: PASS after fixes** — six of eight surfaces were already consistent; `benchmarks.html` (round-3 fossil) and two sentences in `ACTIVE_RESEARCH.md` were drifted and are fixed; PRODUCT_LIST and the `.tex` audited and left to their owners (two minor PRODUCT_LIST staleness notes reported above).
