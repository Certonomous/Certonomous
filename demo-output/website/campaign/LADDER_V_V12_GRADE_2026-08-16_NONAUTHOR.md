# Ladder V — V12, graded at HEAD by a non-author

**Verdict: `PASS`.** Plain, as R-CONVERGE requires. No residual label is attached, because
neither "PASS WITH RESIDUALS" nor "PASS WITH EXCEPTIONS" is a legal outcome.

**Ruling on the `closure.html` instances: they defeat NEITHER clause.** Grounds in §4. They
are filed, not appended.

Graded at frame **`678cb7e8`** (2026-08-16T20:57Z). Every figure below was re-derived by
execution; nothing is quoted from the dispatch brief, from the repair's commit message, or
from the peer grades.

---

## 0. INDEPENDENCE

| field | value |
|---|---|
| this grader | `agent-ae0ce79e959ec8ea0` |
| V12's repair of record | `1fc1f639` — `agent-a3ca1abfef4a6b371` |
| the prior V12 FAIL | `b4596cb4` — `agent-aaf894dca7319cd1e` |
| the V10 re-grade | `f4f05b0f` — `agent-adccb1ac6d2c77c7a` |

**I wrote none of them** — not the product, not the repairs, not the grade being replaced.
This is a genuine non-author grade, unlike my own V16 round 13, where I declared R-ISOLATE
unsatisfied on its face.

---

## 1. V12's CLOSING CONDITION, IN MY WORDS

V12 asks for two things, and they are separable:

**Clause (i) — the three weakest points, each with the record's BEST answer beside it.**
The report must state the three strongest charges a skeptic can bring against the entry,
and set beside each the best answer the record can make. *"Best"* was ruled a **quality
clause even with no accuracy clause imported** (D227 entitlement): **if a better answer to
that same charge exists anywhere in the same document, the clause is not met.** It is not
enough that an answer be present or defensible; it must be the best one the record holds.

**Clause (ii) — the product BECOMES Sanaa's standing briefing.**
A living instrument she can brief from, not a signed snapshot. The entitlement measurement
ruled that a product carrying a caveat that it *"must not yet be read as the briefing"* has
not met a criterion saying it becomes one.

**What V12 does NOT ask for**, and this decides §4: it does not ask that every claim-bearing
surface in the lab agree with the briefing. It asks that the report's three answers be the
best ones, and that the report be fit to brief from.

---

## 2. THE BOARD, RE-DERIVED — never quoted (defect class B4)

`ast.literal_eval` on the `LIVE_BOARD` assignment node in
`sdk/scripts/probability_of_rank.py` (the module is **not imported**), joined to
`official_test_harness_result.round5_per_case_full`:

```
entrants 6 -> 7 positions counting us       best-on-board (six-entry): 2 of 8
```

**The claim the prior FAIL turned on, tested on both boards:**

| board | AR_14_Ret_180, round 4's `0.0325` | was there a BEST-ON-BOARD tie? |
|---|---|---|
| **four-entry `deb91557`** | order `US, Reissmann, Wu, Montoya, Liu`; minimum `0.0325` held by **US and Reissmann** | **YES — a real tie at the minimum** |
| **six-entry live** | order `Yang, US, Reissmann, …`; **rank 2 of 7**, Yang leads at `0.0250` | **NO** |

Round 5's `0.035339` stands **4 of 7** on the six-entry board. And the best-on-board count:
**4 of 8 on the four-entry board, 2 of 8 on the six-entry board** — both re-derived here.

**So the sentence is TRUE of the four-entry board and FALSE of the six-entry board.** That
is the whole of the residual, and it is a board-identification problem rather than an
arithmetic one.

---

## 3. THE PRODUCT, SWEPT WHOLE-FILE WITH A RECOGNITION CONTROL

`demo-output/website/campaign/LADDER_V_PASS3_COLD_2026-08-11.md`, read from `HEAD:` rather
than the worktree. Every pattern built with `\s+`, never a literal space, so a claim that
wraps is still found. Strike spans (`~~`, `<s>`, `<del>`, `\sout{`) blanked **in place**,
offsets preserved.

**Controls first, because a zero without a live control is not evidence:**

| control | result |
|---|---|
| **RECOGNITION control** — five *mutually independent* paraphrases, planted **by line index**, read back before the run | readback **OK**; fired in **5 of 5** planted classes |
| **struck negative control** — the same five, wrapped in `~~` | gained **0** |
| strike balance | 34 `~~` markers, **even** |

**The three answer blocks are W1 `:317-361`, W2 `:362-620`, W3 `:621-727`.**

### 3.1 `:339` — the site the prior grade failed on. **REPAIRED, and correctly.**

The sentence now reads *"0.0325 → 0.0353, the nominal best-on-board tie gone"* followed
immediately by a parenthetical naming **the four-entry `deb91557` clone**, giving the
six-entry reading (*"no best-on-board tie to give up — round 4's 0.0325 stood 2 of 7,
behind Yang's 0.0250, and round 5's 0.0353 stands 4 of 7"*), the **retrieval date
2026-08-11T23:33Z**, the **re-verification 2026-08-14T21:01Z**, and its derivation.

**D294's rule is the right test and it passes both halves.** That rule holds a
caveat-adjacency test grades whether a claim **travels with** its board and is silent on
whether it is **true of** it. Here:

- **travels with:** yes — entrant count and retrieval date are on its own face.
- **true of:** yes — I re-derived it. On the four-entry board the tie was real.

**And the best answer is stated, not merely a caveat**: *"The cost the pre-registration paid
is real and is a second place given up, not a first."* That is the answer W1's charge
actually needs, since W1's charge is that the pre-registration was theatre and the size of
what it cost **is** the rebuttal.

### 3.2 The rest of the live hits — adjudicated, not counted

Ten pattern classes over the whole file. Every remaining live hit was opened by hand:

| site | what it is | live false claim? |
|---|---|---|
| `:265` | *"best-on-board count of 4 of 8"* in **§2 D7**, with the same board identifier appended; re-derived here as **4 of 8 four-entry / 2 of 8 six-entry** | **no** — true of its named board |
| `:362`, `:385` | `0.0029` inside W2's own **heading, quoting the skeptic**, and inside *"**not `0.0029`**"* — a correction naming the old value in order to reject it | no |
| `:443-445` | *"four pairwise comparisons undecided, not two"*; *"4 of 8 cases won"* against **Yang by name** — a **head-to-head** count, which I re-derived as correct | no |
| `:467-468`, `:486`, `:495`, `:533` | matches spanning a soft wrap in flowed prose; opened, none is a placement claim | no |
| `:548`, `:572`, `:584` | a quoted draft sentence inside a nested blockquote, and *"struck `0.67` one order of magnitude smaller"* — corrections naming what they strike | no |

A use-versus-mention pass returned `MENTION 3 / no-span 9` and is reported **as a volume
filter only** — nine of twelve had no locatable span, and per the standing rule
**`CANNOT_TELL` is never `ASSERT`.** The adjudication above is by hand.

**No live, unidentified, false claim remains in any of the three answer blocks.**

---

## 4. THE RULING ON `closure.html` — NEITHER CLAUSE

My own sweep of `closure.html` at `HEAD:` found the tie-claim phrasing live at three sites;
V10's grader, sweeping for more phrasings than my one pattern, found six. **I do not
re-litigate the count — I rule on the frame**, and I do not inherit the peer's routing,
which was a capability constraint rather than a scope finding.

**They defeat neither clause. Three grounds:**

**(1) Clause (i)'s frame is the answer blocks.** The clause binds *"the three weakest
points, each with the record's best answer beside it."* `closure.html` contains no weakest
point and no answer; it is a publication surface. The entitlement measurement that gave
this clause its teeth located R1 and R2 **inside the answer blocks** — that is the boundary
it drew, and it is the boundary I apply.

**(2) Clause (ii) is a property of the product's own readiness, and the wider reading makes
V12 unclosable.** The entitlement ruling defeated clause (ii) on the product's own caveat
that it *"must not yet be read as the briefing."* Reading clause (ii) to reach every
claim-bearing surface in the lab would mean V12 could not be closed by any action available
to its owner — the report's author cannot edit `closure.html`, which is **held elsewhere and
is never-touch in part**. **A criterion may not require more than the maximum permitted
action on the surface it grades** (`bcad2bbc`). That is the same test I applied to V16's C1
last round, and it points the same way here: the wide reading is not strict, it is **void**.

**(3) R-CONVERGE forbids double-counting one defect across two rungs.** Those sites are
inside **V10's declared scope**, and V10 was re-graded **FAIL** on them at `f4f05b0f`, with
two named blockers. Grading the same sites under V12 as well would let **one repair close
two rungs**, which is precisely what R-CONVERGE exists to prevent. They are already owned,
already failing a rung, and already have a repair in flight.

**Filed, not appended** — §6.

---

## 5. VERDICT

| clause | state at `678cb7e8` |
|---|---|
| **(i)** three weakest points, each with the record's best answer beside it | **MET.** W1's `:339` repaired and verified true of the board it names; W2 and W3 carry no live unidentified false claim; no better answer to any of the three charges sits elsewhere in the document |
| **(ii)** the product **becomes** Sanaa's standing briefing | **MET.** The caveat that defeated it — *"R1 must close before this document is read as a briefing"* — is discharged; R1, R2, R3 and the fourth residual are all repaired, and nothing in the product now withholds it from being briefed from |

### **`PASS`.**

**What a falsifier should attack**, in order of cheapness:

1. Show one live, unstruck, board-**unidentified** placement claim inside `:317-361`,
   `:362-620` or `:621-727`. My sweep's recognition control fired 5/5 and its struck
   negative gained 0, so the sweep can see one.
2. Show that the four-entry board did **not** carry a best-on-board tie at `0.0325` — that
   collapses §3.1 and returns the rung to FAIL.
3. Show a better answer to W1, W2 or W3 sitting elsewhere in the same document.
4. Overturn §4 by showing clause (ii) was always intended to reach publication surfaces —
   a ruling, not a measurement, and it belongs to the chief.

---

## 6. FILED, NOT APPENDED (R-CONVERGE)

- **The `closure.html` instances** — in **V10's** scope, already failing that rung at
  `f4f05b0f`, repair in flight. Not V12's.
- **A house-rule residual, one strike away.** `:339` and `:265` keep the superseded
  four-entry reading **unstruck**, with the correction adjacent. The house rule is
  **strike-and-keep**: the superseded figure is struck and left visible. Both sites keep it
  and do not strike it. This is **not** clause (i) or (ii) — the best answer *is* beside it
  and the claim *is* true of its named board — but a reader skimming the running prose meets
  the four-entry reading in the assertion slot and the current one in a parenthesis. One
  strike per site closes it.
- `latex/closure_challenge_report.tex:866, :2207` — never-touch, untouched, unread.
- `docs/PRODUCT_LIST.md` — peer-held, not entered.

---

## 7. WHAT THIS GRADE DID NOT DO

- **Nothing was repaired.** A grader that repairs the site it grades is the shape this
  ladder refuses; the house-rule residual in §6 is left for its owner.
- No solver ran. No scoring call was made; the ledger stands at **6**. Nothing was sent,
  uploaded, filed or registered. Submissions remain **PARKED**.
- The scoring pin `deb91557` was not moved and no board was re-pointed.
- No figure here was quoted from the dispatch brief, from `1fc1f639`'s commit message, or
  from either peer grade; every one was re-derived from `LIVE_BOARD` and the round-5 JSON.

---

## 8. ADDENDUM — two rulings landed after this grade was written, and neither moves it

**(1) "External reader" means external to the ROUND, not to the LAB** (chief, 2026-08-16),
with the paired limit that this *"does not make every finding belief-changing … the test is
whether a reader would believe something different, not whether any byte moved."*

**This does not disturb §4, because §4 never rested on the narrow reading.** None of its
three grounds says lab-published surfaces are ineligible to change belief; they say
`closure.html` is **outside V12's frame**:

- **(1)** clause (i) binds *answers to weakest points*, and that page holds neither;
- **(2)** the wide reading of clause (ii) makes V12 unclosable by any action available to
  its owner, which is `bcad2bbc`'s void condition;
- **(3)** the sites are inside **V10's** declared scope under R-CONVERGE.

All three are **frame** arguments, not **audience** arguments. A lab record is fully
eligible to change belief — it simply has to be inside the rung whose criterion is being
graded, and these are inside a different one.

**(2) All six `closure.html` instances were repaired at `fac54ab4`** (2026-08-16T20:56:23Z),
each made true of the live board and carrying its identifier inside its own block, with a
third non-author V10 grade running against that repair.

**This moots the question in practice and is stated rather than used.** This grade was
formed at `678cb7e8` and its ruling is a **frame** ruling: it would read identically had the
repair not landed, and it must, or it would be a ruling about a repair queue rather than
about V12's criterion. **The verdict is unchanged: `PASS`.**
