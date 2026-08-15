# Ladder V — rung V13, CLOSE-OUT in negative-verdict-review format

**Assembled 2026-08-11, 01:13 → 01:24 UTC (`date -u` run at open and at close; machine TZ
`Etc/UTC`, so every timestamp below is UTC without conversion).**
Owner: the V13 close-out agent. **Read-only except this file.** I executed no rung, graded
no rung, and edited no surface. Zero scoring calls; **the ledger stands at 6**. Nothing was
sent, emailed, uploaded or filed.

Protocol: `LADDER_V_TRIPLE_VERIFICATION.md` (Pass 4 additions and the termination rule at
`5bffb476`). V13's specification: *every rung PASS/FAIL with evidence links, the claims
table, the skeptic's report, and a single consolidated list of anything that changed during
verification. No rung self-graded; the three pass-owners sign their own sections.*

**Frame, stated before any count.** Every verdict below was read from **the rung's own
record**, not from another report's summary of it — summaries have been wrong repeatedly
tonight (V15 round 2's N2 and N3 are both cases of a report mis-describing work that was
itself correct). Where a verdict rests on a measurement I did not take, the row says so and
names whose it is. I re-derived nothing: this is a collection and a judgement, not a rung.

**What this close-out structurally cannot contain.** It cannot see uncommitted work in the
other live agents' trees. It cannot see text committed after 01:18 UTC (HEAD `ce0b14be` at
open, which is another family's pre-registration and not ladder text). It cannot adjudicate
whether an artifact is itself right; only what each record says about it. **Two rungs were
still executing when this was assembled and their slots are marked PENDING in §8** — I did
not wait for them and I did not guess their outcomes.

---

## 1. THE CENTRAL FINDING

> **Every defect this ladder found was in what the package SAID about the science. Not one
> was a defect in the science.**

That sentence is the most important thing this exercise established, and it is not a
consolation prize — it is a measurement, made by three independent passes attacking from
three directions, and it survived all of them.

The seven exhibits, each verifiable at its own record:

| # | what was found | what it was a defect IN |
|---|---|---|
| 1 | A cover email whose subject line and body announced **0.0654** over an attachment scoring **0.056647** — the previous round's score over the current files | the letter, not the files |
| 2 | A **tracked, shipping** archive carrying a prior-art sentence struck five days earlier, crediting two author groups with a control mechanism they never reported — to a readership that includes two of the benchmark's own authors | the archive, not the prior-art analysis, which had been correct in the `.tex` since `d84b649f` |
| 3 | **Four external surfaces** claiming best-on-board **4 of 8** without disclosing that **two of the four are the organisers' own unmodified baseline** | the count's presentation; the two rows are honestly what they are, and §4.7 had already named this the highest-priority disclosure |
| 4 | A description document quoting **5.8×10⁻⁴** as the submitted ducts' continuity residual — a number belonging to `AR_7_Ret_180`, the **validation** duct, which is not in the submission | the sentence; the three submitted ducts measure 8.5 / 5.3 / 5.4 ×10⁻⁴ and always did |
| 5 | **Three verification zeros that were unsound** — the instrument used in all three prior passes is line-bounded and returns 0 on a file that demonstrably contains the sentence wrapped over five lines | the instrument, not the artifact: the sentence is genuinely absent, now on evidence that cannot fake a zero |
| 6 | A rule **withdrawn at its statements but never at its origin** — the internal-only gate on P(rank 1) was reversed, and the clause every copy was made from still read the old way | the rule's propagation, not the probability, which is 68% with a 2–100% interval either way |
| 7 | A **live audit guard failing the public wall for being correct** — `self_audit.py` was pinned to the round-3 entry and reported the round-5 wall as wrong | the guard, not the wall |

The substance held under every attack that was mounted at it. The score reproduces
**bit-for-bit in two independent clean environments** (Pass 1, A1: `0.056647191704213645`
under numpy 2.5.2 in a fresh venv; Pass 3, §1.3: the same digits, cold, by an agent with no
prior contact with the closure line). The leakage assertions **execute** and fire on three
injected violations. The untrained claim is proven **structurally** — an exhaustive
enumeration of every numeric literal in the QCR implementation finds exactly one free
coefficient, `Ccr1`, defaulting to Spalart's published 0.3, with every override channel
measured shut in all three test arms. No test-case LES field exists anywhere in the three
test-duct run trees, while both validation arms carry three each — which is the positive
control that makes the absence a measurement. One duct case walks unbroken from config to
scored number with a byte check at every link.

**And the package would still have been sent wrong.** That is the finding. A lab can be
right about the physics, right about the leakage, right about the provenance, and still
hand a steward a letter that contradicts its own attachment. The layer between the work and
the reader is not a formality; on this entry it was, by a wide margin, the least verified
thing in the building — and it is the only layer the reader ever sees.

**The corollary, which the ladder found the hard way and which is the reason V15 exists:**
that layer includes the verification reports themselves. The claims-table pass wrote 442
lines of outward prose and that prose failed the claims table. The date-correction pass
mis-counted the dates it had correctly corrected. The sweep that reported a prohibition
holding had measured in the opposite direction. **Every one of those is the same class as
the seven above, one level up.**

---

## 2. RUNG TABLE — V1 to V15

Verdicts as their own records state them. **"Independently confirmed by"** names an agent
that did not produce the thing verified; where nobody qualifies, the row says
**SELF-GRADED — weaker** in plain terms.

| Rung | Verdict | Owner (executor) | Evidence | Independently confirmed by |
|---|---|---|---|---|
| **V1** — clean-environment re-score | **PASS**, twice | Closure/UQ family supervisor as Pass-1 owner | `LADDER_V_RUNGS_V1_V3_V4_V5_2026-08-08.md` (`9a21d65c`); re-run `LADDER_V_PASS1_2026-08-11.md` §A1 (`5a21b4fd`) | **YES — Pass 3**, cold, different agent, no contact with the line: same 8 per-case values and the same 20-digit overall (`LADDER_V_PASS3_COLD…` §1.3). Also re-derived under a *different* numpy build (2.5.1 → 2.5.2), bit-identical |
| **V2** — pre-registration chain | **PASS** | V2/V7/V10 executor (`49f71b8c`) | `LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` | **YES — Pass 1 (A2)** re-derived another executor's rung and *strengthened* it: AR_7 start times read from the OpenFOAM log headers instead of inferred from wall time, plus two new tamper checks (8 CSVs byte-frozen since `e865076b`; `R5_RULE_FREEZE.md` has one commit ever) |
| **V3** — leakage assertions executed | **PASS** (leg c FAILED on re-run, since fixed) | Pass 1 | 08-08 record; re-run `LADDER_V_PASS1…` §A3 and §"RE-RUN EXECUTED" | **YES, twice** — Pass 2 re-read the anchors statically (§2, row 4.1); the V6 closure pass re-verified all of them at HEAD (`472f9f92`). Leg (c), the stale §4.1 citations in the send draft, was **failed by Pass 1 against its own pre-registered failure condition**, fixed by the chief (`2ef8ae3b`), and that fix was then verified line-by-line by **V15 round 1** (T38–T41), an agent that wrote none of it |
| **V4** — one duct traced end to end | **PASS** | Pass 1 | 08-08 record §V4; re-run §A4 — `AR_1_Ret_360`, 14 shipped files byte-identical, 395-iteration converged solve, CSV sha256 `bb8d61fb…` → `0.04547044480564218` | **YES — Pass 3** re-derived the same three duct CSVs from the frozen fields at **max abs deviation 0.000e+00**, without reading Pass 1's report |
| **V5** — QCR provenance | **PASS WITH EXCEPTIONS** (chief declined to upgrade) | Pass 1 | `LADDER_V_PASS1…` §A5; addendum `e59ae644` | **YES, and it is the sharpest self-correction in the ladder**: the 08-08 PASS was overturned *by the same role re-running it*, which found five load-bearing surfaces naming our untrained QCR2000 without citing whose constant 0.3 is — one of them a public page into which the **sibling V10 rung** had written the claim 13 minutes before the V5 sweep committed (`git log -S` → `49f71b8c`). Post-Pass-2 re-run: 28 uncited files → 28, identical set, six new QCR-naming files all citing. **Two gaps remain open** (`benchmarks.html`, `CLOSURE_CHALLENGE_STATUS.md`); three are correctly refused (frozen artifacts + another agent's signed report) |
| **V6** — §4 audit re-run against round 5 | **PASS** (was: PASS on the rule, FAIL on currency) | raised by Pass 2; discharged by the V6/V10/V14 closure pass (`472f9f92`) | `LADDER_V_PASS2…` §2; `LADDER_V_V6_V10_V14_CLOSURE.md` §3 | **PARTIAL — see §8 PENDING-2.** All nine findings were re-verified at HEAD rather than inherited from Pass 2, which is strong; but `472f9f92` is one of three commits **the closure pass itself named as unread by anyone but its author** |
| **V7** — kill the two known defects | **PASS**, and the count was three not two | V2/V7/V10 executor (`49f71b8c`), extended by Pass 2 | 08-08 record §V7; `LADDER_V_PASS2…` §3 | **YES — V14**, an independent mechanical search over the same claim class, re-confirmed the artifact and found **two further stale generator strings** the rung had not listed (ranks 6 and 7), including one the script *writes into a manifest* at line 412 |
| **V8** — claims table + banned list | **FAIL — 8 failing claims** (all dispositioned; see §3) | Pass 2 | `LADDER_V_PASS2…` §4, claims C1–C17 | **YES — V15 round 1** audited Pass 2's own table and **reversed the evidence under C9** (F9) and flagged C13 as grading 16 surfaces against a rule withdrawn two rows later; round 3 corrected C9's evidence in place (`63009dd3`) with the verdict left standing. The rank-claim strengthening and its withdrawal are the chief's protocol edits, not rung executions |
| **V9** — prior-art completeness | **FAIL → FIXED** | Pass 2 | `LADDER_V_PASS2…` §5 | **YES, and the confirmation found more than the rung did.** V14's search found the struck sentence still verbatim in the **tracked shipping archive** — a surface Pass 2's frame did not contain. Fixed by rebuild; the absence was then re-verified with a **wrap-proof instrument and a planted positive control** (`7cd558b1`) after the three prior zeros were shown unsound |
| **V10** — cross-surface number sweep | **PASS (08-08) → FAIL (Pass 2) → FAIL (closure pass) → closed `2b251689` + `7cd558b1`** | three different owners in sequence | 08-08 record §V10; `LADDER_V_PASS2…` §6; `LADDER_V_V6_V10_V14_CLOSURE.md` §4; `BUNDLE_REBUILD_2026-08-10.md` | **NO — SELF-GRADED at the last step, and this is the weakest confirmation in the table.** The bundle's rebuild was verified by the pass that rebuilt it. The evidence is unusually strong for a self-grade (committed zip extracted and grepped, then served over HTTP and read as a viewer receives it, drift check 56/56 byte-for-byte, wrap-proof absence sweep with its control passing) — but no agent that did not write the fix has read it. See §8 PENDING-2 |
| **V11** — cold reproduction | **PASS** — reproduced to the last bit | Pass 3 (no prior contact with the closure line) | `LADDER_V_PASS3_COLD_2026-08-11.md` §1, defects D1–D11 | **YES — Pass 1 (A1)**, in an independently built environment, reaches the same 20 digits; the two never read each other |
| **V12** — the skeptic's report | **DELIVERED** (not a pass/fail rung) | Pass 3 | `LADDER_V_PASS3_COLD…` §3; reproduced in full at §4 below | **PARTIAL — V15 round 1 (T49)** checked its P(rank 1) = 0.674 against the internal 0.676 and recorded that **two figures for the same quantity circulate in ladder text with no document reconciling them** |
| **V13** — this close-out | **DELIVERED** | the V13 agent (me) | this file | **NOT APPLICABLE, and stated rather than hidden**: a close-out that collects verdicts cannot be confirmed by re-collecting them. What is checkable here is whether each row matches its cited record — every one was read at its own record, and the four places where a record disagrees with another record are flagged in-line rather than smoothed |
| **V14** — mechanical surface discovery | **PASS as executed** (method was a search, not a list) | an agent that had written to none of the surfaces (`d358fd96`) | `LADDER_V_V14_SURFACE_DISCOVERY.md` — 48,654 files / 15 GB, six frames each with a positive control, 227 claim-carrying lines → **11 stale surfaces** | **YES — the V6/V10/V14 closure pass** re-verified the classification on the 8 items it owned, **changed one** (rank 5 could not be closed on the document because the number is hard-coded in its generator), found **two hits the list did not contain**, and **refused one repair** because it would change a research gate's meaning. **V15 round 2** then audited that pass's first six commits: every row passed |
| **V15** — ladder text re-enters the claims table | **FAIL (round 1: 10 findings) → FAIL (round 2: 6 new) → round 3 → round 4 PENDING** | round 1 and round 2 run by two different agents, neither of whom wrote any audited text | `LADDER_V_V15_LADDER_TEXT_CLAIMS.md` (`6afe15e3`); `LADDER_V_V15_ROUND2.md` (`c1ebfb4f`) | **YES by construction** — each round is executed by an agent that wrote none of the text it audits, which is the rung's own rule. **Round 3's output has not yet been independently measured** — see §8 PENDING-1 |

### 2.1 Rungs whose verdict was reached by their own executor, stated plainly

The ladder's rule is *no agent verifies work it produced*. That rule was kept everywhere:
no executor graded an artifact they authored. But **"did not write the artifact" is a
weaker property than "was independently confirmed"**, and three rows deserve the
distinction:

1. **V10's final state is self-graded** (the bundle's rebuilder verified his own rebuild).
   Mitigation: the verification is end-to-end through served HTTP, not by inference from
   sources — which is exactly the inference that left the bundle stale for ten days.
2. **V6's discharge (`472f9f92`) is unread by anyone but its author**, and its author said
   so and named it as the next round's scope rather than declaring it clean.
3. **V5's exception status rests on a single role's two executions.** The re-run overturned
   the earlier PASS, which is the strongest available evidence that the role is not
   protecting its own prior verdict — but no third party has re-swept the citation frame.

**One further defect of the record, reported not fixed** (this file is read-only elsewhere):
the status ledger in `LADDER_V_TRIPLE_VERIFICATION.md` still lists **V6, V8, V9, V11, V12
and V13 as "waits for unpark"** and shows no entry for V14 or V15. All six have since been
executed. The ledger is the chief's; the table above is the current state.

---

## 3. THE CLAIMS TABLE, FINAL STATE

Pass 2's V8 table as executed: **8 FAIL, 3 INCOMPLETE, 6 PASS.** Dispositions below are as
of 01:18 UTC on 2026-08-11 and each names where it landed.

| # | claim | verdict as found | disposition now |
|---|---|---|---|
| **C1** | cover email: subject and body say **"overall 0.0654"** | **FAIL — the worst finding in the pass.** The attachment scores 0.056647 | **BLOCKED, not rewritten.** The email is Katie's; Pass 2 put a blocking banner at §5 of the draft that cannot be proofread past. The new `DESCRIPTION_DOCUMENT.md` supersedes §5.3 in substance. **Still needs Katie** |
| **C2** | §5.1 points at `closure_challenge_submission/test/` | **FAIL — the round-3 directory** | Superseded by the round-5 package + its new README; the draft is banner-blocked |
| **C3** | §5.2 per-case row: "improvement −0.0382, 36.9% below floor" | **FAIL — every row stale** | Round 5 verified: **−0.0470, 45.3%** below the 0.1036 floor; carried into the description document |
| **C4** | **"best on the public board on four of the eight"** on `benchmarks.json`, `wall/wall.json`, `build_benchmarks.py` and a hero KPI tile | **FAIL on the banned list** — two of the four are the organisers' own unmodified RANS field | **FIXED on all four**, generator and both JSONs re-verified key-by-key; `self_audit.py` now **fails the wall** if the count appears without the disclosure (positive control fired on the second attempt — the first regex missed by four characters) |
| **C5** | §5.3 item 7: "four distinct prediction sets scored" | **FAIL — six** | Corrected; the description document states six and states it is a **self-imposed** discipline, not benchmark compliance |
| **C6** | §5.3 items 6, 8, 9 | **FAIL — 3 of 9 disclosures do not describe the attached files** | All three rewritten. Item 8's replacement then became **V15 finding F1** and was corrected again at `7de8733c`; the row itself carries a dated correction note rather than reading silently right |
| **C7** | §5.3 discloses the round-2 leakage only | **FAIL — the most serious disclosure gap in the package.** The round-5 route was chosen while the per-case test scores were known | **FIXED at full strength** as disclosure 3b of the description document — admission first, mitigations after, and an explicit *"No mitigation below cancels that sentence"*. V15 round 1 judged this section **the best writing in the package** on the hard criterion |
| **C8** | "Reissmann's published 0.059525" | **FAIL on the word "published"** — the README publishes 0.0595 | Corrected; like-for-like re-score gives **0.0595338**, margin **0.0028863**. The error ran *against* the entry by 8×10⁻⁶ |
| **C9** | no "comfortable AR_14 lead" anywhere | **PASS — verdict right, evidence false** | The verdict stands; the evidence was corrected in place at `63009dd3` after **V15 F9**. Re-swept: 76 hit lines tree-wide, four are the prohibition, ten are ordinary uses, **none is a win claim**. Positive control seeded and fired — the original sweep ran none |
| **C10** | no novelty claim on gated correction | **PASS** | Holds; re-swept in V15 round 2 (P44) with a control |
| **C11** | no official-rank language | **PASS** | Holds; 24 hits, every one a disclaimer |
| **C12** | soft-adaptive-leakage disclosure in the lab's own words | **PASS for rounds 1–3** | Round 5's is C7 and now travels |
| **C13** | every rank claim carries P(rank 1), interval, and the not-decided pairs | **PASS on 16 surfaces — then the rule changed two rows later** | **Re-graded.** V15 F7 showed four external surfaces edited by the ladder and left non-compliant with the rule the same commit adopted; **closed at `656c09c9`**, with a guard added that reads the surface |
| **C14** | the internal/external split on the figure | **WITHDRAWN, and the reversal is right** | The figure travels, never without its interval. One new prohibition replaces the split. **The withdrawal is not fully propagated — see §5, items 46 and 54, and §7** |
| **C15** | §4.7's asymmetry argument | **INCOMPLETE — never extended to the three QCR rows** | Written into the description document §2 and §6 |
| **C16** | the seed bound against the margin | **INCOMPLETE → quantified**: 0.002419 / 0.0028863 = **84%** | Correct only with the unrounded bound, and stated unrounded. A neighbouring sentence then attributed 52.0/80.5% to 0.002419 when the bootstrap loaded 0.0024 — **V15 round 2 N5**, corrected at `35c59035` |
| **C17** | on the two declined cases the supplied baseline beats **all four** published entries | **PASS — an asset, not a defect** | Stated as a property of the benchmark, deliberately not folded into our result. Independently verified by Pass 3 |

**The ladder's own text, audited against the same table (V15):** round 1 — **4 FAIL, 5
INCOMPLETE, 3 OBSERVATION, 21 PASS**, ranked into findings F1–F10 (53 claims examined,
T1–T53). Round 2 — **6 FAIL, 3 OBSERVATION, 24 PASS** over the fix round's own output,
ranked into N1–N6. Round 1's two blocking findings (F1, F2) are closed;
round 2's six (N1–N6) are closed; **whether closing them created new failures is the
measurement that has not yet been made** (§8).

---

## 4. THE SKEPTIC'S REPORT — read this before answering any question about this entry

Pass 3's V12, in the voice of a reviewer who has read the package once and is inclined to
disbelieve it. Not softened. Each has the record's best answer beside it, and — added by
this close-out — **what has changed since the report was written**, because two of the three
answers are materially stronger now than when they were first given.

### W1. "You chose the ducts because the answer key told you where you were losing, and you chose QCR because the entry above you already publishes good duct numbers with it. Your pre-registration freezes the last degree of freedom after the one that mattered was spent — and your disclosure list doesn't mention any of it."

**Concede the premise immediately. It is true, we wrote it down first, and it is now in the
document that travels.**

`R5_RULE_FREEZE.md` opens by conceding it in the lab's own words, *before any round-5 number
existed*: **"we already know the round-4 test-duct scores … and any protocol that lets those
numbers choose between the QCR field and the existing ML field is test-truth-informed model
selection. Every degree of freedom in that choice is therefore closed here, in writing,
before any new number exists."** It then closes them, and every closure was verified against
something other than the prose:

- **All-or-none across all three test ducts**, decided on `AR_7_Ret_180` — the benchmark's
  own *suggested validation* duct, not a test case.
- **`Ccr1 = 0.3` frozen before any solve** — Spalart's published constant. Verified in the
  compiled default and absent from every case dictionary.
- **Gate thresholds set from training ducts before the validation arms ran** (V1 ≤ 0.70,
  V2 *r* ≥ 0.85); measured 0.4770 / 0.9284.
- **The `AR_14` loss accepted in advance, in writing.** It then happened — 0.0325 → 0.0353,
  the nominal best-on-board tie gone — **and was not reverted.** A pre-registration that
  never costs anything is decoration; this one cost a result and was honoured.
- **No test ground truth was reachable**: zero `*_LES` files in any of the three test-duct
  run directories, three in each `AR_7` arm — the positive control that makes the absence a
  measurement.
- The rule as written prohibits training or validating on test-case **data**. That did not
  happen. It does not prohibit reading your own preview scores; the benchmark ships the test
  ground truth and instructs submitters to preview (README @ `deb91557`, line 98).

**What changed since:** when Pass 3 wrote this, its closing paragraph read *"the honest
sentence already exists, in the lab's own words, and is being withheld by an oversight
rather than a decision."* **That is no longer true.** The concession is disclosure 3b of
`DESCRIPTION_DOCUMENT.md`, at full strength, with the mitigations placed after it and
explicitly disclaimed as not cancelling it — and the exculpatory clause that used to be the
section's only uncited sentence now carries its citation (benchmark README §Submission,
`deb91557`, lines 98 and 21). **Do not argue this point defensively. Quote 3b.**

### W2. "Your margin is 0.0029. Your own measured seed uncertainty on the model behind three of your eight files is 0.0024. Delete one case and you are rank 2. This is a point estimate wearing a crown."

**Agree, and hand over the number that proves you already knew.**

- Case-level bootstrap over the eight scored cases, B = 200,000: **P(rank 1) = 0.674**
  (0.676 at B = 400,000 internally).
- **An eight-case sample cannot pin that tighter than 2–100% at 95%** (double bootstrap).
  Never state 68% without it — a bare 68% is a worse claim than none, because 68% sounds
  settled and eight cases do not support settled.
- Leave-one-out: **drop `alpha_15_13929_2024` and the entry falls to rank 2.** Every other
  single deletion keeps rank 1. Drop the hump and P rises to 91%.
- Paired per-case: **t = −0.50 vs Reissmann, −0.95 vs Wu & Zhang — not decided.** Liu
  (98.7%) and Montoya (99.8%) are.
- `AR_1` and `AR_3` margins (0.00003, 0.00008) are **ties below published precision** and
  must never be quoted as per-case wins.
- ~~The seed bound covers **84%** of the margin, and a seed draw the lab did not control moves
  P(rank 1) from **52% to 81%**.~~ **STRUCK 2026-08-15 — AND THE INSTRUCTION REVERSES WITH THE
  FIGURE.** Both halves were computed against the **four-entry** board, where the entry ahead of
  ours was Reissmann, Fang & Sandberg and the margin was 0.0028863; `0.002419121853891026 /
  0.0028863365997926355 = 0.8381` is why it read 84%. The board gained two entrants at
  **2026-08-11T23:33Z** (six entries, re-verified unchanged by read-only fetch at
  **2026-08-14T21:01Z**), and the entry immediately ahead of ours is now **Yang at 0.058013**
  with a margin of **0.001365**. Re-derived from the committed records —
  `closure_challenge_seed_sensitivity.json` → `overall_equivalent_S_bound` =
  **0.002419121853891026**, `probability_of_rank.py` → `LIVE_BOARD`, and
  `probability_of_rank_record.json` — the ratio is **177%**: **the bound does not cover part of
  the margin, it exceeds it by 77%.** The seed draw moves P(rank 1) from **34% to 65%** about an
  as-scored **50%**, not 52% to 81%, and loaded adversely our overall is **0.059047** against
  Yang's **0.058013**, so the adverse end **loses the point lead outright**.
  **This bullet is an INSTRUCTION, not a report** — it sits under §W2's *"hand over the number
  that proves you already knew"* — so correcting the figure alone would leave it armed. **The
  number to hand over is 177% and the loss of the lead.** Handing over 84% concedes a
  qualification on a standing that survives it; this standing does not survive it, and a reviewer
  handed 84% would be given the weaker of two true-sounding claims where the evidence supports
  only the stronger. Falsified by the board move of 2026-08-11T23:33Z; withdrawn in the
  travelling document at commit `cc906ec9`, in the cover email at commit `d80649f9`, and reaching
  this closeout only now — the fifth surface, docket **D105**.

**What changed since:** Pass 3's sharpest observation was that the lab had computed this
number and ruled it internal-only while the outward artifact kept asserting "rank 1" — *"I
got 0.674 from the shipped CSVs and the public leaderboard in about a minute. Any reviewer
can."* **The gate was withdrawn the same night on exactly that reasoning.** The figure now
travels with the entry, with its interval and its undecided pairs, on every claim-bearing
surface including the four external ones and the 40-page report. **The strongest answer to
this challenge is to have raised it first, in writing, in the document you sent.**

**Known residue, and say it if asked** rather than being caught by it: three surfaces still
state the withdrawn internal-only rule — the closure family's own supervision guidelines,
a deliberate "wording note" in the internal send draft, and an approved dated proposal that
needs a supersession note rather than an edit. All three are internal, all three are
reported at §7, and the origin clause the copies were made from now carries a dated
supersession note (`d7d51974`).

### W3. "Half of what you submitted is not your method, and the part that is your method makes things worse on the one case you took outside its training family. You are not entering a closure model; you are entering a well-chosen file-selection strategy."

**This is the charge that a leaderboard row cannot answer, so answer it before the row
does.** The decomposition, all of it reproducible from the package plus the public
benchmark (floor = the supplied RANS field everywhere = **0.1036347**):

| component | cases | contribution |
|---|---|---|
| trained PH ML correction | `alpha_15_13929_4048`, `alpha_15_13929_2024` | **−0.0232** |
| **untrained** QCR2000 forward solves | the three ducts | **−0.0239** |
| trained ML on the hump | `NASA_2DWMH` | **+0.00014** — worse than doing nothing |
| the organisers' own file, byte-for-byte | `alpha_05_4071_*` | **0** |
| | | **= 0.056647** |

Three of eight are our machine learning. Three are a published 25-year-old constitutive term
any OpenFOAM user can switch on. Two are the file every entrant is handed for free —
confirmed byte-equivalent to the supplied solve at 4.99×10⁻¹⁰, the CSV's own write precision.
**All of it is disclosed, and disclosed harder than a reviewer would have found it.** §8.3
identifies the free 0.00014 available by reverting the hump and **refuses it**, because
singling out that case requires knowing its test score — the third such refusal on the
record.

And there is a finding here a steward may value more than the rank: **on exactly the two
cases the train-only decline gate withheld the correction, the supplied baseline beats all
four published entries** (0.046108 vs a best published 0.0569; 0.071863 vs 0.0760). A rule
fitted on 21 training cases and validated on 4 non-test cases identified, blind, the two
flows on which every published method in the field damages the answer. **That result does
not depend on our score at all.**

**Where the package supported no answer, and now does:** *"a leaderboard row carries a name
and a number and nothing else."* Pass 3's recommendation — one line in the cover material
saying **three of our eight predictions are an untrained QCR2000 forward solve and two are
your own baseline unchanged; only three are our model** — is now in the description
document's §2 table and §6, and the best-on-board count carries *"two of which are the
baseline rows"* in the same sentence, unhedged, with the model's own count given as **2 of
8**.

**The one thing not to do under pressure on any of the three:** do not reach for a mitigation
before the concession. Every one of these answers is strong *because* it concedes first, and
the record shows the lab writing the concession down before it had the result.

---

## 5. CONSOLIDATED LIST OF EVERYTHING THAT CHANGED DURING VERIFICATION

**64 changes**, every one made by the ladder or by a chief ruling inside it, in chronological
order of the commit that landed it. This is the artefact nobody had assembled; it is
assembled from the passes' own change tables and from `git log --name-only`, not from
summaries. "Reported, not fixed" items are **not** in this list — they are in §7.

### 5.1 The 2026-08-08 record-hardening rungs

| # | was | became | where | commit |
|---|---|---|---|---|
| 1 | no Spalart citation on a record presenting QCR work | dated additive citation note below the frozen frontier | `campaign/R5_PREREGISTRATION.md` | `9a21d65c` (V5) |
| 2 | same | same | `campaign/F6b_QCR_PREREGISTRATION.md` | `9a21d65c` |
| 3 | same | same | `campaign/F6b_QCR_RESULTS.md` | `9a21d65c` |
| 4 | same | same | `campaign/W1_HUMP_CHALLENGE_PREREGISTRATION.md` | `9a21d65c` |
| 5 | same | same | `campaign/W1_HUMP_CHALLENGE_RESULTS.md` | `9a21d65c` |
| 6 | generator literal at round 3: "four pre-registered scoring calls", `our_score = 0.0676`, "five of the eight" — **a live regression trap that would have silently reverted the public page on its next run** | round 5 / six calls / 0.0566 / 4 of 8, verified to reproduce the on-disk `benchmarks.json` block key-by-key | `sdk/scripts/build_benchmarks.py` | `49f71b8c` (V7) |
| 7 | "the lab's ledger (five distinct prediction sets scored, **ever**)" | scoped to the round-4 manifest; six after round 5 stated | `sdk/scripts/closure_round4_manifest.py` | `49f71b8c` |
| 8 | round-3-era "four official scoring calls, ever" quoted as standing text; "must not consume a fifth call" | quote scoped and dated; "fifth" → "new" | `sdk/scripts/export_closure_submission_csvs.py` | `49f71b8c` |
| 9 | §1 a round-3 fossil: 0.0676, four calls, 5 of 8, round-3 duct per-case | round 5 throughout with every caveat, recomputed improvements, AR_14 removed from the best-on-board table with the spent-tie note | `demo-output/website/benchmarks.html` | `49f71b8c` (V10) |
| 10 | two round-4-era sentences reading as present tense ("its 0.0654"; round 4 called "the entry of record") | scoped to round 5 and to the park | `demo-output/website/ACTIVE_RESEARCH.md` | `49f71b8c` |

### 5.2 Pass 2 (adversarial), commit `92562841`

| # | was | became | where |
|---|---|---|---|
| 11 | the **struck** prior-art sentence, crediting four author groups with a control mechanism | the mandated two-part split: *identify* (Ling & Templeton 2015, Wu et al. 2017) vs *control* (Steiner 2022, Buchanan 2025), named separately | `closure.html` |
| 12 | hero KPI *"4 of 8 — better than every published entry"* | the same count **with the organiser-baseline qualification** | `benchmarks.html` |
| 13 | bare count in `our_entry` | same qualification | `benchmarks.json` |
| 14 | bare count in `our_entry` | same qualification | `wall/wall.json` |
| 15 | generator literal without the qualification | same qualification, re-verified key-by-key against both JSONs | `sdk/scripts/build_benchmarks.py` |
| 16 | closure guard **pinned to round 3**, failing the correct wall; error text "four official calls"; "round 3 records five of eight" | re-pinned to the round-5 record; precision-aware comparison at the wall's own published precision; both counts corrected; **new check** failing the wall if 4-of-8 appears without the baseline disclosure (4 positive controls, one of which exposed a regex that could never have fired) | `scripts/self_audit.py` |
| 17 | docstring "the ledger stays at 5 distinct prediction sets scored" as standing present-tense text | scoped to the script's own run, cumulative six stated | `sdk/scripts/closure_round5_qcr_forward.py` |
| 18 | the Buchanan firewall stated as a **prohibition** only | discharged as a dated **chronology** — CSV byte-identical across rounds 3–5, written 16 h before the paper was first mentioned; the one disclosed use named rather than denied | `CLOSURE_CHALLENGE_PRIOR_ART.md` §2.4 |
| 19 | §5 read as a sendable package | **blocking banner** making the cover-email/attachment mismatch impossible to proofread past; no claim of Katie's rewritten | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` |
| 20 | internal-only gate on P(rank 1) live; §7 surface count 15; a "count must equal N" check | gate withdrawn (banner + amended propagation rule); count 15 → 16 with the `.tex`'s history; the count check **retired** for three invariants | `campaign/PROBABILITY_OF_RANK_2026-08-10.md` |
| 21 | V8 as originally written | the V8 amendment recording the withdrawal and the new no-bare-figure prohibition | `campaign/LADDER_V_TRIPLE_VERIFICATION.md` |
| 22 | **the required description document did not exist** — §5.3 was a specification for one | `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`, **NEW, 349 lines** | the package |
| 23 | the package did not say where the benchmark or scorer is, or how to install | `closure_challenge_submission_round5/README.md`, **NEW, 93 lines**, with an integrity command **executed verbatim, 8/8 OK** | the package |

### 5.3 Chief rulings executed inside the ladder

| # | was | became | where | commit |
|---|---|---|---|---|
| 24 | §4.1 cites lines 115 / 165–167 / 215 — stale by +13 since `fe121af2`; **three passes declined the fix in writing** | 128 / 178–180 / 228, verified against HEAD | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | `2ef8ae3b` |
| 25 | changelog dates taken from a dispatch header rather than the clock | corrected, and L-53 recorded | `docs/PRODUCT_LIST.md`, `LESSONS.md` | `e59ae644` |
| 26 | P(rank 1) internal-only | **reversal ruled**: a figure an outsider recomputes in a minute is not protected by being withheld | `docs/PRODUCT_LIST.md` | `c1187949` |
| 27 | citation note dated the code shift *2026-07-30* | **2026-07-31** — a wrong date inside a note about stale references (V15 F8) | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | `a454c6bb` |

### 5.4 Fix round 1 — closing V15 round 1's F1–F7/F10

| # | was | became | where | commit |
|---|---|---|---|---|
| 28 | **5.8×10⁻⁴** offered in bold as the submitted ducts' measured continuity residual | *"the three submitted ducts measure 8.5 (`AR_1`), 5.3 (`AR_3`) and 5.4 (`AR_14`) ×10⁻⁴"* — cases named, so the number can never be re-read as a case the reader will not receive | `DESCRIPTION_DOCUMENT.md` §3.7 | `7de8733c` |
| 29 | the same wrong number inside two verification reports | dated correction notes naming F1, struck rather than silently right | `LADDER_V_PASS2…` C6, `LADDER_V_PASS3_COLD…` D5 | `7de8733c` |
| 30 | **29 assertions across 15 files dated 2026-08-11 when the clock read 2026-08-10** — including both files that travel with the entry | corrected; **no file renamed** (five committed reports cite those paths), in-file dated notes instead; a code constant `WAIVER_REGISTER_DATED` corrected and proven to feed no logic | 15 files incl. both package files | `9477a2ed` |
| 31 | "written **three days before** the paper was read in full" — 55% overstated, in the flattering direction | **1 day 22 h 37 m**, corrected at four sites | `DESCRIPTION_DOCUMENT.md` §4, `PRIOR_ART` ×2, `PASS2` table | `b032bbae` |
| 32 | the 68% and the margin silently computed from **two different values** of Reissmann's score | the split stated on its face: the bootstrap rests on 0.059525, the margin on 0.0595338, the bootstrap **has not** been re-run, the difference is 9×10⁻⁶ ≈ 0.3% of the margin | `DESCRIPTION_DOCUMENT.md` §5 | `b032bbae` |
| 33 | the seed sensitivity moving P(rank 1) 52% → 81% did not travel | added as a fourth row of the outward interval table, per the reversal's own logic | `DESCRIPTION_DOCUMENT.md` | `b032bbae` |
| 34 | the disclosure's **only uncited sentence was its defence** | benchmark README @ `deb91557`, line 98 and line 21, cited inline and verified verbatim at the frozen commit | `DESCRIPTION_DOCUMENT.md` §3.3b | `b032bbae` |
| 35 | *"P(rank 1) = 68%"* bare, with **no interval**, still marked "internal only" — the exact prohibition the ladder had just adopted | figure + 2–100% interval + the 52–81% range + the named undecided pairs; withdrawn gate replaced | `campaign/CHALLENGE_SLATE_2026-08.md:37` | `b032bbae` |
| 36 | three records asserting the withdrawn internal-only rule | identical dated supersession sentence in all three, byte-identical to each other | `ACTIVE_RESEARCH.md`, `CLOSURE_CHALLENGE_STATUS.md`, `agenda/CHALLENGE_LANDSCAPE.md` | `1db6fc3c` |
| 37 | shipping bundle hero **0.0654** as "our entry of record" | **0.0566** | `dist/certonomous-demo.zip` → `site/closure.html` | `892f11f7` |
| 38 | shipping bundle KPI **0.0676** | **0.0566** | → `site/benchmarks.html` | `892f11f7` |
| 39 | bundled `lab_stats.json`: `our_score` 0.0676, "across **four** scoring calls" | 0.0566, "across **six**", round 5 | → `snapshot/lab_stats.json` | `892f11f7` |
| 40 | the **struck prior-art sentence, verbatim, in the shipping archive** | 0 hits anywhere in the bundle | → `site/closure.html:254–256` | `892f11f7` |
| 41 | the gitignored staging mirror carrying the same four defects | regenerated in place; tree and shipped artifact byte-for-byte identical | `dist/certonomous-demo/` | `892f11f7` |
| 42 | the bundle shipped a mission recording made **without the STL upload** — the exact failure Katie's own shoot script warns about at line 177 | replaced with the act that has the upload; all four acts complete in both | the bundle's recordings | `892f11f7` |
| 43 | bundle **absent** → drift check WARNs | **FAILs** — absence means the detector is off for the one artifact that leaves the box; hermetic control arms so it cannot become fail-always | `scripts/self_audit.py`, `sdk/tests/test_bundle_drift_gate.py` | `54cf11bb` |
| 44 | bundle behind by one file (`exec_bits.py`, committed nine minutes after the rebuild) | rebuilt; the one-file gap was caught by the detector within nine minutes | `dist/certonomous-demo.zip` | `a1545dbd` |

### 5.5 The V6/V10/V14 closure pass — V14's stale list, dispositioned

| # | was | became | where | commit |
|---|---|---|---|---|
| 45 | *"nothing here changes **the recorded** 0.0654"* hard-coded **in the generator**, so a document-only patch would regenerate it | supersession note put **in the generator**; both outputs re-derived and verified by running it into a scratch dir before / after / again | `build_master_table.py` + `closure_eval_master_table.{md,json}` | `dc13f1cc` |
| 46 | *"Our entry of record is round 4, 0.065438"* in the present tense, no supersession | dated supersession banner carrying the **full** rank companion (figure, 2–100% interval, both undecided pairs with *t*, both decided pairs); **the plan's arithmetic deliberately left alone**, because re-basing a plan onto its own outcome destroys the record of what was decided on what evidence | `CLOSURE_RANK1_CAMPAIGN.md` | `5af41163` |
| 47 | docstring calling round 3 *the entry of record* — **and the same claim written into a manifest at line 412**, which the discovery rung had not listed | both scoped and dated | `export_closure_submission_csvs.py` | `4381d634` |
| 48 | generator writes *"round 4 (**the entry of record**, overall 0.0654)"* | status parenthetical scoped to *"the entry of record until 2026-08-07"*; **the two dated manifests on disk deliberately untouched**, because rewriting a dated artifact's text under an unchanged date forges the record | `closure_round4_manifest.py` | `4381d634` |
| 49 | *"nothing here changes the recorded 0.0654"* (definite article) **and** a duct continuity figure of 2.3–3.4% that no longer describes the submission | *"the recorded round-4 0.0654"*, plus a dated note giving the round-5 values **and naming `AR_7_Ret_180` as the validation duct not in the submission** — V15's F1 trap, avoided on purpose | `CLOSURE_EVALUATION_PROTOCOL.md` | `a3a4ab3a` |
| 50 | *"beats our **current** 0.0741"* — pinning round 2 in a knowledge base agents read for guidance | *"our round-2 0.0741"*, with the current entry named. **The gate's PH-only/overall mismatch was reported, not repaired**, with both candidate bars computed | `docs/NUMERICS_KNOWLEDGE.md` | `79f4529c` |
| 51 | an **unlabelled** `ours (unsubmitted) 0.0741` row under a heading reading *"where we actually stand"* | round label + a dated note naming the three rounds since; the round-2 reading left standing | `closure_challenge_C2_error_decomposition.md` | `249b611c` |
| 52 | an illustrative score pinned to a round it had no reason to pin | rewritten **round-free**, with both the current and superseded values in the note | `agenda/LIBRARY_ACCESS_LIST.md` | `249b611c` |
| 53 | four external surfaces making a rank claim with **no figure and no interval** — under the rule their own commit adopted | all four carry **P(rank 1) = 68%** and **2–100% at 95%**; JSONs rewritten *from* the generator literal so they cannot drift; **a guard added that reads the surface**, with 4 failure controls and 2 must-pass controls | `benchmarks.html`, `benchmarks.json`, `wall/wall.json`, `build_benchmarks.py`, `self_audit.py` | `656c09c9` |
| 54 | C9's evidence sentence (*"every occurrence … is the prohibition"*) — false | corrected in place, verdict left standing, with the sweep re-run under a seeded positive control | `LADDER_V_PASS2…` C9 | `63009dd3` |
| 55 | §4's compliance audit describing **round 3**, with round-5 verdicts living only in a satellite report | all nine findings verdicted against round 5 **inside the audit itself**; moot findings kept with their reason; the untrained duct path given the compliance line it never had | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §4 | `472f9f92` |

### 5.6 Fix round 3 — closing V15 round 2's N1–N6

| # | was | became | where | commit |
|---|---|---|---|---|
| 56 | *"INTERNAL ONLY; **the figure** never appears in an external claim"* — in the JSON the outward document cites as its source, **missed by four sweeps because every document writes "the 68% figure"** | withdrawn wording, matching the three records already corrected; `INTERNAL ONLY` now occurs zero times in the file. The surface set was then **re-derived structurally** — restriction predicate within 400 characters of a referent for the figure, no spelling of the sentence used — finding **14 statements, 8 correctly superseded, 6 still asserting** | `closure_challenge_round5_qcr.json` | `d9552d73` |
| 57 | *"Of 74 occurrences, 29 were assertions … 45 were references"* | **73 and 44**; the 29, the 19 files and the corrective work itself are exact and unchanged | `docs/PRODUCT_LIST.md` | `07af6f02` |
| 58 | *"the **manifest's own** changed-list"* — the manifest has no changed-list and never names `AR_7` | the forward record's `/what_ships`, which does. The underlying fact was true and proved two ways; only the named artifact was wrong, in a sentence whose point was that it was verified against the primary artifact | `docs/PRODUCT_LIST.md` | `8ce7cedd` |
| 59 | outward seed paragraph crediting **0.002419** for a bootstrap that loaded **0.0024** — the same precision defect it disclosed one paragraph earlier | corrected to the value the computation used | `DESCRIPTION_DOCUMENT.md` §5 | `35c59035` |
| 60 | a bare-figure sweep **calling itself exhaustive** over a frame it did not cover | the claim now states its true frame (per-surface, tracked `.md`/`.html`/`.py`) and the `.tex`'s sites are **routed to its owner**, not edited | `docs/PRODUCT_LIST.md` | `4e719a6b` |
| 61 | the shipped bundle two files behind (one from the rank-compliance fix, one from a monitor commit that landed ten minutes after the last rebuild) | rebuilt; drift check **56/56 byte-for-byte**, zip extracted and grepped, then **served and read over HTTP** — hero and KPI 0.0566, struck sentence zero, rank companion with its interval | `dist/certonomous-demo.zip` | `2b251689` |
| 62 | an absence claim resting on a **line-bounded grep**, used in all three prior passes | the standard now requires an instrument that cannot produce a false absence plus a positive control proving it; the absence re-verified three ways (committed archive, source, served bytes) across 78 text files, with a planted wrapped control that the old instrument reads as 0 and the new one finds in full | `CASES_FAMILY_SUPERVISION_GUIDELINES.md` §9; `BUNDLE_REBUILD_2026-08-10.md` addendum | `f2e16a47`, `7cd558b1` |
| 63 | a commit whose message did not describe its own diff (59 lines of a concurrent agent's work swept in) | provenance recorded on the entry, since history cannot be rewritten; **L-57** written: a pathspec commit isolates by file, not by author | `docs/PRODUCT_LIST.md`, `LESSONS.md` | `935f0f52`, `d7d51974` |
| 64 | the internal-only gate still live **at its origin** — the strategy proof clause every copy was made from | dated supersession note at the origin, and the same correction in the live round-5 standing item | `docs/CAPABILITY_STRATEGY.md:83`, `docs/PRODUCT_LIST.md:60–61` | `d7d51974` |

*(Round 4's `.tex` work — the figure carrying its interval at every site, the withdrawn
caution replaced with its own reasoning rather than deleted, and a one-word edit checked
against the document's own idiom — landed at `5fa933ee`, `e2fb6883`, `45b3be0f`, `ae6254cf`
between 01:07 and 01:10 UTC, i.e. during the assembly of this report. It is **not** numbered
above because no agent other than its author has yet read it; it is round 4's text and it is
the pending measurement in §8.)*

**Count: 64 changes.** Of them, **11 are to text that travels with the entry**, **13 are to
public or shipping surfaces**, **9 are to live code or generators**, and **the rest are to
the lab's own records** — which is itself the shape of the central finding: most of what had
to change was what the lab said about itself.

---

## 6. THE ROUND TREND, AND WHAT IT IMPLIES

| round | new failures in that round's own output | measured by | severity |
|---|---|---|---|
| **1** (`6afe15e3`) | **10** (F1–F10) | an agent that wrote none of the audited text | **2 BLOCKING, both in the outward package** |
| **2** (`c1ebfb4f`) | **6** (N1–N6) | a different agent, again wrote none of it | **0 blocking; exactly one touches the outward package**, and it is a precision label rather than a wrong number |
| **3** (`d9552d73` … `7cd558b1`) | **not yet independently measured** | — | its self-reported new failure is one bundle drift, named first rather than last by the pass that caused it |
| **4** (`5fa933ee` … `ae6254cf`) | **not yet independently measured** | — | — |

**The trend is right and it is two points long. Say both halves of that sentence.**

10 → 6 is a real decline, measured the same way twice by two different agents, and the
severity fell faster than the count: round 1 put two blocking defects in documents that
leave the lab; round 2 put none there. The failure class also **migrated inward** — from
what the package says about the science, to what the reports say about the package. That is
the direction you want: the defects are retreating from the reader.

**But rounds 3 and 4 have not been audited, so the trend has two measured points and two
empty ones, and a close-out that drew a line through four of them would be doing exactly
what this ladder exists to catch.** Round 3 in particular did not merely close six findings
— it found a **new class** while closing them (a rule withdrawn at its statements and never
at its origin; a grep missing a live surface by three characters; three prior verification
zeros that were unsound because the instrument was line-bounded). Every round so far has
produced at least one finding whose *shape* was new. The count falling is not the same as
the classes being exhausted.

**What it implies, stated as a judgement rather than a tally:**

1. **The fixed point is plausible within one or two more rounds, and it is not here.** The
   rule is explicit: green means a fix round introduces **zero** new failures in its own
   output, measured by someone who wrote none of it. Round 3's output includes a
   self-declared new failure (bundle drift) and three commits its own author flagged as
   unread. That is not zero.
2. **The recursion is terminating in practice, not just in principle.** Round 1 found
   defects in the entry's outward documents; round 2 found defects in the fix round's
   arithmetic *about* its own correct work; round 3 found defects in how a withdrawal
   propagates. Each round's findings are further from the reader than the last. A loop whose
   findings are converging on the lab's own bookkeeping is a loop about to run out of
   material.
3. **The one thing that would falsify that reading** is a round-4 audit that finds a defect
   in the outward package again. That is precisely what the pending measurement is for, and
   it is why this report does not declare the ladder green.

---

## 7. WHAT THE LADDER DID NOT ESTABLISH

A close-out that only lists successes is a marketing document. These are the things a
reader would be wrong to take from the record above.

**About the entry**

1. **It did not establish that the entry is first.** The point estimate is rank 1 of 5,
   scored **locally** at a benchmark commit frozen 2026-05-04. **P(rank 1) = 68%, and eight
   cases cannot pin that tighter than 2–100% at 95%.** The leads over Reissmann and Wu &
   Zhang are not statistically decided. Nothing has been submitted and the entry holds no
   official rank.
2. **It did not certify that the leaderboard position is current.** §4.8's "current" rests
   on a three-month-old clone. Certifying it needs a network read that no pass made, on
   purpose, because the frozen commit is load-bearing for V1 and V2.
3. **It did not make the trained third of the entry reproducible.** Three of the eight
   predictions come from a trained model with **no model file, no training script in the
   manifest, no hyperparameters and no seed shipped** (Pass 3, D8). Those three carry the
   entry's two largest per-case wins. The untrained third re-derives to exactly zero
   deviation; the trained third cannot be checked by anyone outside this lab — the reverse
   of how the package's confidence is distributed.
4. **It did not verify the trained third's provenance to the standard applied to the QCR
   third.** V5's structural proof — *nothing here could be fitted* — covers the duct path
   only.
5. **It did not test the disclosure strategy on a human.** No steward, reviewer or outside
   reader has seen this package. The claim that admitting first is more credible than
   defending first is a judgement the ladder acted on; it is not a result the ladder
   measured.

**About the ladder itself**

6. **It is not green, and the send gate is shut.** V15 has not reached the fixed point, two
   measurements are outstanding, Sanaa has not re-run V1 and V3 with her own hands, and
   neither she nor Katie has proofread the cover email. Author names and the reference URL
   are still `[KATIE TO FILL]`.
7. **V15 verified sentences against artifacts; it did not re-verify the artifacts.** Where
   V15 read Pass 1's, Pass 2's or Pass 3's measurement, it inherited their reliability and
   said so. That inheritance is the load-bearing assumption under the entire text audit.
8. **The searches have named blind spots and they are not hypothetical.** No text search can
   read a number rendered into a PNG: 955 PNGs exist, one was opened and **did** carry
   round-4 per-case scores (correctly self-labelled), and **24 further closure-named PNGs
   were never opened**. Binary artifacts, base64 VTK payloads and non-extracted binaries are
   out of frame. Everything outside `/home/ubuntu/Certonomous` is out of frame — including
   the round-5 run tree the record cites, the backups, and the agent memory. And **a stale
   claim carrying no number at all** — *"we lead the board"* — is unreachable by a literal
   search; the one instance caught was caught because it happened to sit beside a score.
9. **Several corrections have not travelled**, and are reported here rather than fixed
   because this rung is read-only and they have owners:
   - **`CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md:108–110`** — the closure family's own rule
     document still instructs supervisors that *"the figure is INTERNAL"*, under the
     withdrawn split.
   - **`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1184–1191`** — a *"Wording note, deliberate
     (chief ruling 2026-08-10)"* keeps the figure out of the outward draft *because it is
     internal by its own gate*, while line 575 of the same file states the withdrawal
     correctly. **The draft contradicts itself.**
   - **`agenda/proposals/probability-of-rank-…json`** — four fields of an approved, dated
     proposal still state the gate; it needs a supersession note, not an edit.
   - **`benchmarks.html` and `CLOSURE_CHALLENGE_STATUS.md`** still carry the load-bearing
     *"untrained QCR2000 … nothing fitted to anything"* claim **without naming whose
     constant 0.3 is** (V5's leg-3 exceptions, open since 2026-08-08).
   - **`LAPTOP_SHOOT.md`** — Katie's spoken shoot script still says the round-4 number *"is
     our entry of record"* and carries the withdrawn best-on-board phrasing. Hers.
   - **The `.tex` site counts do not reconcile across records** — V15 round 2 measured the
     figure at 7 sites, the chief's correction says 12, the report pass says all 10 now
     carry the interval. The file today has zero occurrences of the withdrawn rule and
     eleven lines carrying the interval, so the *substance* is closed; **the arithmetic
     about it was never reconciled**, which is this ladder's most persistent defect class
     appearing one last time in its own close-out.
10. **It did not establish that any of this is cheap.** Sixty-four changes, four fix rounds,
    fifteen rungs and at least eleven distinct agents were required to make a package say
    what the work actually did. Whether that ratio is acceptable is Katie's call, not the
    ladder's.

---

## 8. THE TWO PENDING SLOTS

Two rungs were still executing when this report was assembled. I did not wait for them and
I did not guess their outcomes. **I could not identify their agents from the commit stream
at 01:18 UTC**, so these slots name the two open *measurements* rather than the two live
agents; whichever rung lands first should be read into the slot it answers.

### PENDING-1 — the round-4 audit: is the ladder at the fixed point?

- **Waiting on:** an independent audit of round 3's and round 4's own output, by an agent
  that wrote none of it, per the termination rule.
- **Scope, already fixed by the record rather than by this report:** round 3's commits
  (`d9552d73`, `07af6f02`, `8ce7cedd`, `35c59035`, `4e719a6b`, plus `2b251689`, `7cd558b1`,
  `f2e16a47`, `935f0f52`, `d7d51974`) and round 4's four `.tex`/PRODUCT_LIST commits
  (`5fa933ee`, `e2fb6883`, `45b3be0f`, `ae6254cf`).
- **What its answer decides:** whether the ladder goes green. Zero new failures in that
  frame = fixed point = green. Anything else = round 5.
- **Do not read a fourth-round silence as a pass.** The termination rule's own words: if
  each round keeps producing failures, the answer is not to stop auditing — it is that the
  package is not ready.

### PENDING-2 — the three unread commits and V10's self-graded closure

- **Waiting on:** an independent read of the three commits the V6/V10/V14 closure pass named
  as *"outside the peer audit and not read by anyone who did not write them"* —
  **`656c09c9`** (the rank companion on four external surfaces + the new guard),
  **`63009dd3`** (C9's corrected evidence), **`472f9f92`** (V6's nine round-5 verdicts) —
  and on a non-author confirming **V10's** bundle closure (`2b251689`, `7cd558b1`).
- **Why it matters:** V6's PASS and V10's closure are the two verdicts in §2 that rest on
  their own authors' verification. Both are supported by unusually strong evidence
  (re-verification at HEAD; extraction plus served HTTP plus a wrap-proof absence control),
  and neither has been read by a second pair of eyes.
- **Until it lands, treat V6 as PASS-pending-confirmation and V10 as CLOSED-BY-ITS-AUTHOR**
  in any statement made outside this lab.

---

## 9. SIGNATURES

V13 collects the pass owners' signatures; **it does not sign for them, and it grades no
rung.** Each is quoted from that owner's own report, at the commit that carries it.

- **PASS 1 — re-derivation (V1, V3, V4, V5).** *"Signed: Closure/UQ family supervisor, as
  PASS-1 owner, personally per charter §3, running on Opus under a stated §5 model-rule
  override… Ladder rule 'no agent may verify work it produced' satisfied — none of the
  verified round-5 artifacts were produced by this executor."* —
  `LADDER_V_PASS1_2026-08-11.md`, `5a21b4fd` / re-run at `9fea8481`; earlier record
  `LADDER_V_RUNGS_V1_V3_V4_V5_2026-08-08.md`, `9a21d65c`.
- **PASS 2 — adversarial (V6, V7, V8, V9, V10).** *"Signed: the Ladder V Pass-2 owner
  (adversarial), 2026-08-10. Rungs V6, V7, V8, V9, V10 executed. Zero scoring calls; ledger
  unchanged at 6. Nothing was sent."* — `LADDER_V_PASS2_2026-08-11.md`, `92562841`.
- **PASS 3 — cold reproduction (V11, V12).** *"Pass-3 owner, Ladder V — outside-reviewer
  frame, cold reproduction 2026-08-10/11. No package file, record, ledger or score was
  modified by this pass."* — `LADDER_V_PASS3_COLD_2026-08-11.md`, `636c0b91`.
- **PASS 4 — structural (V14, V15).** V14: *"Reported, not fixed. Nothing on any checked
  surface was written by this rung"* — `LADDER_V_V14_SURFACE_DISCOVERY.md`, `d358fd96`.
  V15 round 1: *"Signed: the Ladder V rung V15 owner, 2026-08-10 (clock)"* — `6afe15e3`.
  V15 round 2: *"Signed: the Ladder V rung V15 round-2 owner, 2026-08-11 00:07 UTC (clock)"*
  — `c1ebfb4f`. Closure pass: *"Signed: the V6/V10/V14 closure pass, 2026-08-11 00:20 UTC"*
  — `171b1241`.

**V13, this file.** Assembled 2026-08-11 01:13–01:24 UTC by the close-out agent. Every
verdict was read at its own record; no rung was graded here; four inter-record
disagreements are flagged in place rather than smoothed; two measurements are outstanding
and are marked PENDING rather than assumed. Zero scoring calls, **ledger 6**. Read-only
except this file. **Nothing was sent, emailed, uploaded or filed, and the send gate remains
shut.**
