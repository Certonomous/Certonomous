# Ladder V — independent grade of rungs V12, V13 and V14

**Graded 2026-08-15, 20:16–21:0xZ (clock audited with `date -u` before any date was written).**
Repo at grading: `1a847fa8` at first read, `9dca4738` at write. No solver run, no scoring call —
**the ledger stands at 6**. Nothing sent, uploaded, filed or registered; the scoring pin
`deb91557` was not moved. `dist/`, `LAPTOP_SHOOT.md`, `motorbike-video/`, `scripts/self_audit.py`,
`docs/USING_THIS_LAB.md`, `closure.html`, `ACTIVE_RESEARCH.md`, `CLOSURE_CHALLENGE_STATUS.md`,
`closure_challenge_round5_qcr.json`, `docs/PRODUCT_LIST.md` and other agents' in-flight round
documents were **read and never written**.

These three rungs had never received a non-author verdict at all. This document supplies one for
each.

---

## 0. INDEPENDENCE — how it is established, and the exact size of the claim

**Git cannot establish it.** `git log --format='%an <%ae>'` returns one identity —
`Ubuntu <ubuntu@ip-172-31-43-247…>` — for the overwhelming majority of the 1,899 commits in this
repository, and git emits its "configured automatically from your username and hostname" warning
on every one. A commit's author field cannot separate any two agents in this lab.

**The session container cannot establish it either.** This session has been open since
2026-08-04, before every commit under grade.

**What does.** `~/.claude/projects/-home-ubuntu-Certonomous/64b13819-…/subagents/` holds one
`.jsonl` transcript and one `meta.json` per dispatched agent. Mine is
**`agent-aa2b2865640f72efe`**, whose `meta.json` reads
`{"agentType":"general-purpose","description":"Grade rungs V12, V13 and V14",…}` and whose file
was created at **2026-08-15 20:16:55.355966037 +0000**. My first tool action — `date -u` — ran at
**20:16:58Z**, three seconds later. That record is my earliest existence in this machine.

**The reasoning against the commit timestamps.** Every artifact under grade was written before my
record opened, by a measurable margin:

| what I grade | its commit | committed | my first record | margin |
|---|---|---|---|---|
| V12's repair (`§W2` of `LADDER_V_PASS3_COLD_2026-08-11.md`) | `29beb7cf` | 2026-08-15 01:01:21Z | 20:16:55Z | **19h 15m earlier** |
| V13 §8 PENDING-2 discharge | `dde6e1cf` / `9e466dd4` | 02:06:03Z / 02:07:33Z | 20:16:55Z | **18h 09m earlier** |
| V14's 08-15 re-run (same pass as V12's repair) | `29beb7cf` | 01:01:21Z | 20:16:55Z | **19h 15m earlier** |
| V14's original green | `d358fd96` | 2026-08-10 | 20:16:55Z | ~5 days earlier |

I could not have written any of them: the earliest moment at which this agent existed postdates
the latest of them by more than eighteen hours. I have written to none of the graded surfaces, and
the only file I create is this one.

**THE LIMIT, stated because the claim is worth less than it looks.**
`scripts/check_rung_attribution.py --emit-trailer` emits the **same value for every agent in this
session** — its own text at lines 86–100 says so outright: *"every subagent of a session inherits
the same `CLAUDE_CODE_SESSION_ID` and the same `CLAUDE_PID`… TWO AGENTS DISPATCHED BY THE SAME
CHIEF SESSION READ AS THE SAME AGENT."* It names a **session**, not an agent. And the subagent
directory is **untracked and per-machine**: it is not in this repository, it will not survive a
clone, and **no reader of the repository can re-derive the paragraph above** (D130). What I have
is a machine-local record consistent with independence, not a portable proof of it. A reader who
declines to accept it is not being unreasonable.

---

## 1. SCOPE, declared before grading (R-CONVERGE)

**In scope.** Exactly three questions, one per rung, each read from
`LADDER_V_TRIPLE_VERIFICATION.md` **as the criterion is written there**:

1. **V12** (§"PASS 3", lines 184–186) — does the skeptic's report state the three weakest points
   as an outside reviewer would state them, each with the record's best answer, and do the figures
   the ledger's V12 row asserts re-derive?
2. **V13** (§"CLOSE-OUT", line 591) — are the close-out's two PENDING slots answered, do
   PENDING-2's measurements reproduce under my own execution, and is the status ledger accurate?
3. **V14** (§"PASS 4", lines 196–204) — executed as a **search**, does the mechanically derived
   surface set come back clean over the current corpus?

**Out of scope, FILED not appended.** Anything found outside those three questions is written into
`docs/DOCKET.md` as a numbered row and is **not** used to move any of the three verdicts. In
particular I did not re-audit V15 round 7's 25 findings, did not re-grade V5/V6/V8/V10/V16, and did
not open the D38 rule-set question.

---

## 2. RUNG V12 — the skeptic's report

### 2.1 The criterion, quoted, and an ambiguity in it

> **V12. The cold agent writes the skeptic's report**: the three weakest points of the entry as an
> outside reviewer would state them, each with the record's best answer beside it. This becomes
> Sanaa's briefing for any follow-up questions from the steward.

**AMBIGUITY, recorded as a finding.** *The criterion as written contains no accuracy clause and no
currency clause.* It requires three weakest points with answers beside them; it says nothing about
whether the figures must be true, or true **now**. The standard the 2026-08-15 repair applies —
*"a red-team brief that hands the skeptic a weaker version of the true case is a defect in the
rung's own instrument"* — is **derived**, not quoted. It is derivable, and I adopt it: "as an
outside reviewer would state them" is present tense, and an outside reviewer today reads the
six-entry board. But a grader who read only the criterion could pass this rung on a briefing whose
every number was four days stale, and two other graders hit criterion ambiguity on their own rungs
this week. **I grade against the criterion as written PLUS the derived currency standard, and say
so rather than let the derivation pass as text.**

### 2.2 Every figure re-derived — independently, not read

Sources, all read mechanically: ours from `demo-output/website/closure_challenge_round5_qcr.json`
→ `official_test_harness_result.round5_per_case_full` / `round5_overall_full`; the board from
`LIVE_BOARD` in `sdk/scripts/probability_of_rank.py` read **with `ast.literal_eval`, never
imported**; the seed bound from `demo-output/website/closure_challenge_seed_sensitivity.json`.
Bootstraps are **my own numpy implementation with my own seed**, not the lab's script.
`__pycache__` purged before every cell.

| figure the ledger's V12 row asserts | my re-derivation | verdict |
|---|---|---|
| margin `0.001365` over Yang, not `0.0029` | Yang = mean of 8 published per-case = `0.0580125`; ours `0.056647191704213645`; difference `0.0013653082957863563` → **`0.001365`** | **CONFIRMED** |
| seed bound `0.002419` is **177%** of it, not 84% | `spreads.overall_equivalent_S_bound` = `0.002419121853891026`; ÷ margin = **177.2%** (177.1% on the `0.058013` printed basis, 178.8% on the published `0.0580`) — all three bases give 177%, as D104 says | **CONFIRMED** |
| loaded adversely the point lead is gone | adverse overall ranks **2nd of 7**, behind Yang `0.058013`, ahead of Reissmann `0.059525` | **CONFIRMED** (see R3 for the printed digits) |
| P(rank 1) = 50.2%, interval 0–97% at 95% | 400,000-draw case-level bootstrap: **`0.5023` (200,924 / 400,000)**; double bootstrap 2,000 outer × 4,000 inner: **[0.007, 0.976]** | **CONFIRMED** within Monte-Carlo error (the row's `200,609` and mine differ only by RNG seed) |
| **three** of eight leave-one-out deletions lose point rank 1, not one | `alpha_15_13929_4048` → **rank 2**, `alpha_15_13929_2024` → **rank 3**, `alpha_05_4071_4048` → **rank 2**; the named three and no others. P(rank 1) 31.5–32.5% in those three, 44.1–78.7% in the other five | **CONFIRMED**, cases and ranks exact |
| **four** pairwise leads `not statistically decided`, not two | under `DECIDED_P/T/WINS = 0.98 / 2.0 / 7`: Yang 57.7% t −0.189 4/8; Reissmann 69.4% t −0.495 4/8; Wu & Zhang 84.8% t −0.953 5/8; Tian 86.1% t −1.033 5/8 — **all four undecided**. Liu 98.7% t −2.203 7/8 and Montoya 99.8% t −2.912 7/8 **decided** | **CONFIRMED** |
| best-on-board **2 of 8**, **zero of 8 earned** | ours beats all six published only on `alpha_05_4071_4048` (0.046108 vs best 0.0569) and `alpha_05_4071_2024` (0.071863 vs best 0.0748) → **2 of 8**; both are in `unchanged_cases_sha256`, i.e. the organisers' own file passed through by the decline gate (§W3's decomposition, contribution **0**) → **0 of 8 earned by our model** | **CONFIRMED** |
| the `4 or 5 of 8` Wu & Zhang cell (D133/D140) | `AR_1_Ret_360`: ours `0.04547044480564218` vs printed `0.0455`, gap `2.955e-05` = **0.591 of a half-ulp** — inside the printing interval, undetermined in either direction | **CONFIRMED** |
| per-case dispersion vs Yang "fifteen times the margin" | sd of paired differences `0.0204` ÷ `0.001365` = **14.95** | **CONFIRMED** |
| `AR_1`/`AR_3` behind by 0.0164 and 0.0089 | `0.045470 − 0.0291 = 0.016370`; `0.039982 − 0.0311 = 0.008882` | **CONFIRMED** |

**Every figure in the V12 ledger row re-derives.** The repair's substance is correct and the
skeptic's case is as bad as it says.

### 2.3 Residuals — three, all inside the rung's own product

**R1 — BLOCKS THE SEND-GATE USE OF THIS DOCUMENT. The rung's one actionable recommendation
instructs the lab to publish a figure the rung itself struck 34 lines earlier.**
`LADDER_V_PASS3_COLD_2026-08-11.md:525-527`:

> *"**Recommendation, and it is the cheapest thing in this report:** put the number in the external
> text. 'Rank 1 on the point estimate; P(rank 1) ≈ 0.67 by a case-level bootstrap over eight
> cases' is a stronger claim than 'rank 1,'…"*

`0.67` is the **four-entry board's** figure. Line 491 of the same file strikes it: *"Struck
2026-08-15: four-entry board. Now 50.2%…"* The recommendation is **unstruck**, is the only
sentence in the rung that proposes text for a travelling surface, and is **17 points optimistic in
the direction that flatters us** — the exact class the repair was written to remove. Line 518
(*"I got 0.674 from the shipped CSVs… Any reviewer can"*) is its premise and carries the same
figure. **The send gate routes this document to Sanaa** (*"she re-runs V1 and V3 with her own
hands, reads V12"*), so this is not a lab-record staleness: it is a live instruction, on the path
to the steward, to publish a wrong number.

**R2 — §W3 carries four-entry framing, unstruck, and one stale value.**
`:559-562`: *"on exactly the two test cases the train-only decline gate withheld the correction,
the supplied baseline beats **all four published entries** (0.046108 against a best published
0.0569; 0.071863 against a **best published 0.0760**)."* Measured against the six-entry board the
**claim's direction survives** — the baseline still beats all six on both cases — but the count is
four and the second best-published value is wrong: on `alpha_05_4071_2024` the board's best is
**Yang's 0.0748**, not Reissmann's 0.0760. The repair block was scoped to §W2; §W3 was not swept,
and the ledger row's own words are *"it did so for four days on **every figure it carries**."*

**R3 — the repair block is internally inconsistent about the seed bound, in adjacent bullets.**
The bullet at `:399-403` asserts the bound is `0.002419121853891026` and derives **177%** from it.
The bullet at `:404-407` prints adverse `0.059047` and favourable `0.054247`. Those two figures
are **not** what the stated bound gives:

```
0.056647191704213645 + 0.002419121853891026 = 0.059066    (printed: 0.059047)
0.056647191704213645 - 0.002419121853891026 = 0.054228    (printed: 0.054247)
0.056647191704213645 ± 0.0024                = 0.059047 / 0.054247   ← exact match
```

`0.0024` is `SEED_BOUND_ON_OVERALL` at `sdk/scripts/probability_of_rank.py:64` — the **rounded
script constant**. So one bullet quotes the JSON to eighteen digits and the next uses the script's
two-digit rounding, with no note that they differ. **The conclusion is unaffected** (adverse ranks
2nd of 7 under both), which is why this is a defect of derivation and not of candour — the same
shape the V16 line calls *"a measurement whose inputs are not in the repository"*, one level down.

### 2.4 V12 verdict

> ## PASS WITH RESIDUALS — R1, R2, R3, plus the criterion ambiguity of §2.1

Every figure the repair asserts re-derives exactly under independent execution, and the rung's
structure (three weakest points, each with the record's best answer) is intact. It does not earn a
clean green because its product still carries three stale figures, one of which — R1 — is a live
recommendation to put a 17-point-optimistic number into external text, on the document the send
gate hands to Sanaa. **R1 must close before this document is read as a briefing.** It does not
block the rung, because the rung's criterion asks for the three weakest points and they are there
and correct.

**FALSIFIER.** Show that `LADDER_V_PASS3_COLD_2026-08-11.md:517-527` and `:559-562` are struck,
dated or corrected to the six-entry board at the commit this grade names — that clears R1 and R2.
Or show that the seed bound of record is `0.0024` rather than `0.002419121853891026` — that clears
R3 and instead falsifies the 177% bullet, which cannot be true of both. Or re-run a 400,000-draw
case-level bootstrap and get P(rank 1) outside [0.49, 0.51], or a leave-one-out that loses point
rank 1 on any count other than three — either overturns §2.2.

---

## 3. RUNG V13 — the close-out

### 3.1 PENDING-1 — verified

The slot asks whether round 4's audit found the ladder at the fixed point. **Answered: NO**
(`LADDER_V_V15_ROUND4.md` §7). I verified the containment claim rather than the verdict, because
the verdict is round 4's to give: **all fourteen commits PENDING-1 names are ancestors of HEAD
(14/14) and all fourteen lie inside round 6's declared range `656c09c9..2266c4e3` (14/14)**,
checked with `git merge-base --is-ancestor` and `git rev-list`, not read.

### 3.2 PENDING-2 — both halves re-derived, both reproduce exactly

**Q69 — the run-tree `*_LES*` positive control.** Run in the main checkout with `/usr/bin/find`
(the shell's `find` is `bfs`), against `/home/ubuntu/certonomous-runs/w3-qcr-rank1/`. **Evidence
count printed before the verdict**, as the slot requires:

| arm | files | `*_LES*` |
|---|---|---|
| `AR_1_Ret_360_qcr` | 52 | **0** |
| `AR_3_Ret_360_qcr` | 52 | **0** |
| `AR_14_Ret_180_qcr` | 52 | **0** |
| `AR_7_Ret_180_qcr` | 55 | **3** |
| `AR_7_Ret_180_sst` | 55 | **3** |
| **five arms** | **266** | **6 control hits** |
| whole tree incl. 10 top-level files | **276** | 6 |

**Exact reproduction** of §8's `266 / 0-0-0 / 3-3 / 6`. *And the two numbers in circulation are both
right under different frames*: §8 says **266 across the five arms** and states its frame; the V6/V10
ledger row says **276** and does not. Only one of them names what it counted.

I confirm §8's own caveat and repeat it: the glob is an enumeration over **filenames**, so it
cannot see truth read from outside the arms, and the compliance line must not be cited as though
the glob alone settled it.

**Q60 — V10's drift check.** Re-derived against the **tracked** `dist/certonomous-demo.zip`, not
the gitignored build directory: for each revision I extracted the zip blob with `git show
<rev>:dist/certonomous-demo.zip`, decoded it with `zipfile` (**never byte-grepped**), and compared
each member against the source blob **at that same revision** via `git show <rev>:<path>`. The copy
list re-derives at **56 = 49 control-room + 4 launcher + 3 pages**, matching §8's decomposition:

| revision | members in zip | graded | same | differs | absent |
|---|---|---|---|---|---|
| `2b251689` | 90 | 56 | **56** | 0 | 0 |
| `7cd558b1` | 90 | 56 | **56** | 0 | 0 |
| `297b82a0` (the discharge's HEAD) | 90 | 56 | **51** | 5 | 0 |
| **`HEAD`** | 90 | 56 | **50** | **6** | 0 |

`297b82a0`'s five differing members are exactly the five §8 names — `agenda.py`, `exec_bits.py`,
`closure.html`, `benchmarks.html`, `wall.html`. **Exact reproduction.**

**RESIDUAL V13-a — it has since degraded by one.** At HEAD the count is **50 / 56**, with
`sdk/chief_engineer/certificate.py` a sixth stale member. §8's `51/56` was true when written and is
now one file stale.

**Confirmed repaired since §8 wrote it:** D118's durable half. §8 records *"`check_bundle_drift()`
never opens the shipped artifact… Reported, not repaired."* At HEAD the function's docstring reads
*"IT READS THE ZIP, NOT THE DIRECTORY BESIDE IT (2026-08-15, D118)"* and it is three-valued from an
empty set. Run in production it returns **FAIL** naming the same six members I derived
independently — *reported as a fact about the guard, not cited as evidence*; the agreement is
worth something only because I derived the six without it.

**Still open, and I confirmed it by opening the container:** the shipped zip's
`certonomous-demo/site/closure.html:502-503` carries *"rank 1 of 5 is our local scoring at a pinned
benchmark commit, with a seed-uncertainty bound comparable to its margin"* — **live prose**, while
`:139` of the same shipped file says *"rank 1 of 7 on the live"* board. D112's shape, in the
artifact that ships. See §4, which finds it is not alone.

### 3.3 The ledger table — verified in both directions

The V13 row's charge is that the ledger was stale **both ways**. Both entries have since been
struck and corrected; I verified the **corrections**, since the repairing pass may not.

- **V15 was listed at "round 5 PENDING."** Rounds 5, 6 and 7 have run. All three cited commits
  exist with matching subjects: `1b0433eb` (round 5, 2026-08-11 07:29:59Z), `769b43f6` (round 6,
  21:56:58Z, "seven rotted claims"), `edbaa0fe` (round 7, 2026-08-15 00:27:48Z, "twenty-five new
  failures"). The corrected row's "round 7 FAIL, 25 findings" matches round 7's own self-reported
  count at its `:713` and `:796`. **The correction is accurate.**
- **RESIDUAL V13-b — and the correction is now itself one round stale.** **Round 8 exists**:
  `demo-output/website/campaign/LADDER_V_V15_ROUND8.md`, committed `05354615` at **2026-08-15
  20:18:50Z** — three minutes after my record opened, and after the row was corrected. The row
  names rounds 5–7 only. This is not a criticism of the correction; it is the ledger's structural
  condition, and it is the reason I record the clock.
- **V16 was listed "SELF-GRADED by construction."** Verified false: `V16_GRADE.md` (grades 1–4),
  `V16_GRADE_ROUND5.md`, `V16_GRADE_ROUND6.md`, `V16_GRADE_ROUND7.md` all exist on disk, and
  `5ef1fd1a`, `db18553b`, `5e4a0cc5`, `067caac0`, `0c7b968d` all exist with subjects matching the
  rounds the row assigns them. **At least seven independent grades. The correction is accurate**,
  and the row is right that the old text understated the lab's own evidence.

### 3.4 Two staleness residuals in the close-out's own reporting

**RESIDUAL V13-c — §2's V10 row is stale against §8 of the same file.**
`LADDER_V_V13_CLOSEOUT.md:94` still reads *"**NO — SELF-GRADED at the last step, and this is the
weakest confirmation in the table.**"* `:597` of the same file reads *"V10 therefore **moves off**
CLOSED-BY-ITS-AUTHOR."* Neither is struck against the other. **Mitigated, and the mitigation is by
design**: the §2 row ends *"See §8 PENDING-2"*, so a reader following the pointer gets the update.
I record it because a verdict cell that is false on its face and true only via its footnote is the
D141 shape with a seatbelt, and the seatbelt is a convention, not an instrument.

**RESIDUAL V13-d — `LADDER_V_TRIPLE_VERIFICATION.md` asserts §8 is unedited, and it has been
edited.** `:1001-1002` reads *"`LADDER_V_V13_CLOSEOUT.md` §8 is **not edited**… **Both slots are
still empty as slots**"*, and the ledger's V13 row at `:637` says the same. Written at `29beb7cf`,
**2026-08-15 01:01:21Z** — at which moment both were true. §8 was then edited at `9e466dd4`,
**02:07:33Z**, which added the `#### DISCHARGED 2026-08-15` block that fills PENDING-2. Both
sentences have been false for nineteen hours. *This is the close-out's own charge — a ledger stale
against the lab — recurring in the document that made the charge.*

### 3.5 V13 verdict

> ## PASS WITH RESIDUALS — V13-a, V13-b, V13-c, V13-d

Both PENDING slots are answered. PENDING-1's scope containment verifies 14/14 twice over.
PENDING-2's two measurements — the ones the close-out honestly refused to assume — **reproduce
exactly under my own execution**, at digit-level agreement on every figure: 266 files / 0-0-0 /
3-3 / 6 control hits, and 56/56, 56/56, 51/56 with the five named members. The ledger's two
stale-in-both-directions rows are corrected and both corrections check out. The residuals are all
of one kind — **the record moving under a correct statement** — and none of them touches a
measurement.

**FALSIFIER.** Re-run my Q60 derivation (zip blob at a revision vs source blobs at the *same*
revision, `zipfile`-decoded) and get anything other than 56/56, 56/56, 51/56, 50/56 with those
member names; or count the five run-tree arms with `/usr/bin/find` and get anything other than
266 files with 6 `*_LES*` control hits concentrated in the two `AR_7` arms. Either overturns §3.2
and with it the discharge. Or show `LADDER_V_V13_CLOSEOUT.md` §8 has no `DISCHARGED` block — that
clears V13-d.

---

## 4. RUNG V14 — the mechanical sweep

### 4.1 The criterion, and the frame I ran it in

> **V14 (A14). Mechanical surface discovery, not a maintained list.** …a **repo-wide search for
> every score literal** … **plus every prior-art sentence fragment**, across **tracked files,
> built artifacts, and shipping archives** including `dist/`. The searcher must prove its own reach
> first … and state what its frame structurally cannot contain. … **the rung fails if its method is
> a list rather than a search.**

Its green is the 2026-08-10 sweep (`d358fd96`); **494 commits have landed since**, and 84 since the
2026-08-15 re-run at `29beb7cf`. Re-running it as the list of what it found last time fails it by
construction, so **every literal below is re-derived from machine records and nothing is copied
from either prior report.**

**TOOL IDENTITY, proved not assumed.** `type grep` and `type find` both return **`is a function`**
in this shell — the wrappers are `ugrep --ignore-files` and `bfs`. Every count below used
`/usr/bin/grep` (**GNU grep 3.11**) and `/usr/bin/find` (**GNU findutils 4.9.0**), confirmed by
`--version`. `__pycache__` purged before every cell. Containers were **decoded** (`zipfile`,
`pdftotext`, `zgrep`), never byte-grepped.

**THE FOUR ARMS, measured, with the count stated for each.**

| arm | reach | size | claim-shaped hits | control |
|---|---|---|---|---|
| **1 — tracked** | `git grep -a` | **20,698** files. `-a` reaches **1,476** files `git grep -I` skips as binary; **11 of those hold no NUL byte at all** (3 certificates, 2 b52 PDFs, `blade.stl`, `motorBike.obj` ×2, 3 aircraft `.stl`) — invisible to every `grep -I` sweep and to the shell's wrapper | 34 files, **128 occurrences** of `rank 1 of 5`; 58 unstruck in a 400-char window, of which the great majority are use-vs-mention | `closure` → 534 files; `zzqqxxnotpresent` → 0 |
| **2 — untracked** | `git ls-files --others --exclude-standard` | **3**: `.autostop-hold`, and two other agents' in-flight test files | 0 | — |
| **3 — gitignored** | `git ls-files --others --ignored --exclude-standard`, `xargs -0` fixed-string prefilter (85 s) | **37,244** | **3**: `dist/certonomous-demo/site/{closure,benchmarks}.html` (the extracted bundle) and one `__pycache__/self_audit.cpython-312.pyc` (NOT-A-CLAIM: the guard's own comment strings) | `closure` → 791 files |
| **4 — run tree** | `/usr/bin/find` + `/usr/bin/grep -aF`, three size bands | **132,049 files / 66 GB, COVERED IN FULL** | **0 claim-shaped hits in every band** | `FoamFile` → 60,868 / 3,958 / 2,013 |

**Arm 4 is extended, not inherited.** The prior pass covered 121,523 files ≤2 MB and left 10,526
larger ones uncovered. I swept all three bands myself: **121,523** (≤2 M, 72 s) + **4,418**
(exactly 2 M, 49 s) + **6,108** (>2 M, **51 GB**, 6 m 42 s) = **132,049**, which equals
`/usr/bin/find … -type f | wc -l` exactly. Zero hits on `rank 1 of 5`, `RANK 1 OF 5`,
`comparable to its margin`, `P(rank 1)`, `scored locally` in any band, with a positive control
firing in each. With the bare numeric `0.056647` included the >2 M band returns 461 files — all
OpenFOAM `U`/`nut`/`phi`/`points`/`R` field and mesh data: **numeric coincidence, NOT-A-CLAIM by
construction**, the same conclusion both prior runs reached.

> **A HOLE IN MY OWN FRAME, CAUGHT AND CLOSED, RECORDED BECAUSE IT IS THE DEFECT CLASS THIS LAB
> RANKS HIGHEST.** My first partition was `-size -2M` and `-size +2M`. GNU `find` rounds sizes
> **up**, so those two predicates are **not complementary**: the 4,418 files that round to exactly
> 2 M fall through both. That partition covered 127,631 of 132,049 files — **96.7%** — and would
> have let me report "the run tree is clean" over a hole containing 4,418 unread files. Nothing
> flagged it. **What caught it was adding the three band counts and checking the sum against the
> total**, which is the only reason this row says 132,049 and means it.

**CONTAINERS, decoded.**

| container | reach | measured |
|---|---|---|
| **shipping archive** | `dist/certonomous-demo.zip`, tracked, `zipfile`-decoded, **90 members** | **24 four-entry-class occurrences; 9 unstruck.** See §4.3 |
| **PDF** | `pdftotext` over **68** PDFs | **68 non-empty, 0 extraction failures.** 2 files hit: `demo-output/website/latex/closure_challenge_report.pdf` (**2× `rank 1 of 5`, 14× `68%`** — D91/D148, already filed, not re-filed) and `docs/papers/Paper1.pdf` (**1 — a false positive**: `1.68%` matched by my unanchored `68%`) |
| **gzip** | `zgrep` over **529** `.gz` | **0 hits.** Control: `zgrep -c ''` on `…/polyMesh/owner.gz` returns **15,522** lines — the null is an absence, not a broken pipe |
| **git history** | commit messages and blobs | **NOT-A-CLAIM by construction.** Rewriting a dated commit message to fix a number is strictly worse than the stale number |
| **images** | *unreadable by any text search* | **955 PNGs, 0 SVGs.** Unchanged blind spot, stated rather than closed |

### 4.2 The literal set, re-derived

| rule | source, read mechanically | yield |
|---|---|---|
| **S** — our scores | every numeric leaf under `official_test_harness_result` in the **19** `demo-output/website/closure_challenge_*.json` files, values in (0,1) | **39 distinct** |
| **B** — the board | `LIVE_BOARD` in `sdk/scripts/probability_of_rank.py` via `ast.literal_eval` (never imported): 6 entrants × 8 per-case + 6 overalls | **54 distinct** |
| **R** — derived | margin over Yang `0.001365`; over Reissmann `0.002878`; seed bound `0.002419121853891026` and the script's `0.0024` | 4 |
| **P** — prior art | the struck sentence's fragments, recovered from `git show 92562841` | — |

Rules S and B **reproduce the 08-15 re-run's 39 and 54 exactly**, from the sources rather than from
its text. **Rule P is clean**: the fragment *"controls where a data-driven correction is allowed to
act has been published repeatedly"* survives in exactly **one** place tree-wide —
`LADDER_V_V14_SURFACE_DISCOVERY.md:199`, quoting it in order to document it (use-vs-mention,
NOT-A-CLAIM) — and in **zero** zip members, **zero** gitignored files and **zero** PDFs, with the
zip control (`Closure` in 7 of 90 members) firing.

### 4.3 THE FINDING — the shipped archive carries EIGHT live claims, and the re-run named ONE

Every one of these is **struck on its tracked source page** and **live in the tracked shipping
archive**, because the zip is six files stale (§3.2). They survive *only* in the artifact that
leaves this box:

| shipped member : line | the live text | what is true |
|---|---|---|
| `site/closure.html:341` | *"the case falls to **3rd of 5**, and our best-on-board count* | four-entry ordinal |
| `site/closure.html:342` | *drops **5 of 8 → 4 of 8***" | best-on-board is **2 of 8**, 0 earned |
| `site/closure.html:411` | *"— **comparable to the 0.0029 margin over the published leader**"* | margin is `0.001365` over Yang; the bound is **177%** of it, not "comparable" |
| `site/closure.html:434` | *"**2nd of 5** — was 3rd; ties Wu & Zhang at published precision"* | four-entry ordinal; and the tie is `0.591` of a half-ulp, undetermined (D133) |
| `site/closure.html:435` | *"**3rd of 5** — 0.03998 against Wu & Zhang's 0.0399"* | four-entry ordinal |
| `site/closure.html:436` | *"**3rd of 5** — the tie for best, lost as pre-registered"* | four-entry ordinal |
| `site/closure.html:502-503` | *"**rank 1 of 5** is our local scoring… with a seed-uncertainty bound **comparable to its margin**"* | **the one the re-run named** (D112); `:139` of the same shipped file says *rank 1 of 7* |
| `site/benchmarks.html:148-149` | *"the **0.0029 margin** over the published leader carries a truth-free seed-uncertainty bound of **comparable size (0.0024)**"* | struck on the source at `benchmarks.html:156` on 2026-08-14; **still shipping** |

Measured the same way on the **tracked sources**: **15 of 15** occurrences of this class are
STRUCK. In the **shipped zip**: **9 of 15 are LIVE** (the ninth, `lab_stats.py:5`, is a docstring
warning against exactly this fraction — NOT-A-CLAIM, excluded above).

**WHY THE RE-RUN SAW ONE.** Its Frame C reported *"Six hits. Five are correct struck-and-kept
tombstones. One is not."* — six because it searched **its own derived literal set**, and that set
is Rules S, B and R: **score literals**. `2nd of 5`, `3rd of 5`, `5 of 8 → 4 of 8` are **ordinals
and counts about ourselves**, not score literals; they appear in **no** rule the criterion names.
Its search was correct and complete *for the families it derived*, and the families are the gap.

**AND THE SHAPE RECURRED AGAINST THE INSTRUMENT THAT NAMED IT.** The re-run's own transferable
lesson is *"a clearance verified against a list cannot see a fourth defect standing beside the
three the list names."* Its report then **became a list of one**, and seven stood beside it.

**Reported as a fact about the guard, not cited as evidence either way:**
`check_rank_claim_surfaces` **does open the archive** — its frame line reads *"20700 tracked
path(s) plus the members of 1 shipping archive(s)"* — returns **WARN**, and names **none of the
eight**. `check_board_placement_words` returns WARN on a test fixture. `check_bundle_drift`
returns FAIL and names the six stale members, agreeing with my independent derivation. I derived
the eight without any of them.

### 4.4 A citation that cannot be resolved

The re-run's Frame D row attributes its 8 four-entry PDF hits to **`latex/closure_challenge_report.pdf`**,
and V16's criterion at `LADDER_V_TRIPLE_VERIFICATION.md:236` names **`latex/closure_challenge_report.tex`**
as *"the real instance"* justifying whole-text matching; `LADDER_V_PASS2_2026-08-11.md:245` cites
`latex/closure_challenge_report.tex:864`, `:825`, `:905`. **`latex/` does not exist at the repo
root** — `ls -d latex` fails and `git ls-files` returns only
`demo-output/website/latex/closure_challenge_report.{tex,pdf}`. Every one of those anchors is
unresolvable as written, in exactly the class V15 round 7 §3.2 opened as "repo-rooted citation
resolution." *(The same is true of the do-not-touch pathspec `latex/*` in my own dispatch: it
matches nothing. I read and did not write the real path regardless.)*

### 4.5 What my frame structurally cannot contain

Stated because a sweep that does not say this is selling a green it has not earned: **rendered
text** (a page can carry a claim its bytes do not contain); **PDF figure and font layers**, which
`pdftotext` silently drops; anything inside the **955 PNGs**; **semantic variants** of any claim
that share no searched fragment; and — a limit of my own instrument, demonstrated rather than
asserted — **my fixed strings carry no word boundaries**, which is why `1.68%` in
`docs/papers/Paper1.pdf` matched `68%`. It **can** contain untracked and gitignored trees and the
run tree, which is where arms 3 and 4 above came from and where the shell's default tools cannot
follow. **And the honest weakness to attack first is my strike predicate**: a 400-character
proximity window is a heuristic, not a parser — a claim struck 500 characters upstream reads as
live to it, and a live claim within 400 characters of an unrelated strike reads as struck. I chose
the window because the chief's correction at `29452c51` records that
`board_placement_faults` has **no strike stripper** and uses a 400-character proximity window; I
inherited the constant and it is not derived from anything.

### 4.6 V14 verdict

> ## FAIL — on two blockers

**BLOCKER V14-1. The tracked shipping archive carries eight live claims that are struck on their
sources, and seven of them have never been named.** The rung exists because *"a surface nobody
listed is exactly where a stale claim survives."* This is that surface, and the sweep of record
lists one item on it. The archive is the only copy of this code that leaves the box.

**BLOCKER V14-2. The criterion's own literal families cannot reach the class.** *"Every score
literal … plus every prior-art sentence fragment"* enumerates two families and omits the ordinals
and counts we assert **about ourselves** — the very class D151 records as having **no denominator
predicate anywhere in the lab**. A rung whose method is fully faithful to its criterion and still
misses seven of eight defects has a criterion that is a **list of families where it demands a
search**, which is the failure the rung's own last sentence names. **This is a defect in the
rung's definition, not only in its execution**, and it cannot be closed by re-running the sweep.

Neither blocker is repaired here: `dist/` and the public pages have designated owners, and a rung
criterion is Katie's. **Reported, not fixed.** V14's 2026-08-10 green does not carry to the current
corpus, and the 2026-08-15 re-run's own verdict — NOT CLEAN — is confirmed and **enlarged**.

**FALSIFIER.** Extract `dist/certonomous-demo.zip` at the commit this grade names, decode
`site/closure.html` and `site/benchmarks.html` with `zipfile`, and show **fewer than eight**
unstruck occurrences of the class in §4.3 — that overturns V14-1. Or show that `2nd of 5`,
`3rd of 5` and `4 of 8` **are** derivable from Rules S, B or R as the criterion defines them —
that overturns V14-2 and makes the omission an execution error instead of a definitional one. Or
re-partition the run tree by any complementary predicate and find a claim-shaped hit in the
132,049 files — that overturns §4.1's arm 4.

---

## 5. WHAT THE INSTRUMENTS COULD NOT TELL ME

1. **Whether V12's briefing is *complete* as a red team.** I verified every figure it carries. I
   have no instrument for a weakest point it never raised, and neither does the criterion.
2. **Whether the eight shipped claims have been read by anyone outside this lab.** The bundle is
   the backup console for a shoot; who has run it is not in the repository.
3. **Whether my strike predicate is right.** §4.5. A 400-character window is inherited, not
   derived.
4. **Whether the run tree's ≤2 M band is unchanged since the prior pass.** My 121,523 matches
   theirs exactly, but I swept it rather than infer that from the match — and a matching count is
   not a matching set.
5. **Anything about rendered pages, PNG contents, or PDF figure layers.** §4.5.
6. **My own independence, to a reader of the repository.** §0. The evidence is machine-local and
   untracked (D130), and `--emit-trailer` names a session, not an agent.

---

## 6. VERDICTS

| rung | verdict | what it turns on |
|---|---|---|
| **V12** skeptic's report | **PASS WITH RESIDUALS** — R1, R2, R3, + criterion ambiguity | every repaired figure re-derives exactly; the product still carries three stale figures, one a live recommendation to publish `P(rank 1) ≈ 0.67` externally |
| **V13** close-out | **PASS WITH RESIDUALS** — V13-a, V13-b, V13-c, V13-d | both PENDING slots answered; both PENDING-2 measurements reproduce digit-for-digit under my own execution; both ledger corrections check out; four staleness residuals, none touching a measurement |
| **V14** mechanical sweep | **FAIL** — V14-1, V14-2 | eight live claims in the tracked shipping archive, seven never named; and the criterion's literal families structurally cannot reach the class |

**No rung is marked green by this pass beyond what the table says, and this pass has no standing to
mark the ladder green.** Under R-ISOLATE I am now an author of this text and may not grade it: the
V12/V13/V14 residuals above, and this document itself, owe a V15 claims-table pass by a non-author.

**Filed to `docs/DOCKET.md`, not appended here:** the residuals R1, R2, R3, V13-a and the §4.4
citation defect. V14-1 and V14-2 are the rung's blockers and are stated above.

*Signed: the independent grader of Ladder V rungs V12, V13 and V14 — subagent record
`agent-aa2b2865640f72efe`, first action 2026-08-15 20:16:55Z, which postdates every graded commit
by more than eighteen hours. Zero solver runs, zero scoring calls, **ledger 6**. Nothing sent,
uploaded, filed or registered; the scoring pin was not moved. Read-only except this file and the
docket rows it names.*
