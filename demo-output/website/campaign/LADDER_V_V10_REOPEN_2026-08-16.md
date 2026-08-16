# Ladder V — V10 REOPENS: `ACTIVE_RESEARCH.md:29` was in class at `c2cd83bf`, and the sweep that cleared the surface could not have seen it

**Ruling: `ACTIVE_RESEARCH.md:29` falls INSIDE V10's declared claim class. The `PASS` issued at
`c2cd83bf` (2026-08-16T17:25:49Z) was not entitled.** The surface carried, unstruck, a board claim
that is false on the board of record, in the live round-5 paragraph, and V10's criterion has no
tolerance: *"one inconsistent surface fails the rung."*

This is said plainly and without softening. The grade at `c2cd83bf` is careful work — its board
re-derivation matches mine to the digit, its four controls are the best in this corpus, and it
caught a defect in its own reconciliation before believing it. **It missed this because its
recogniser structurally could not contain it, not because it was run carelessly**, and that
mechanism is the part worth keeping.

**Independence.** This grader wrote none of `c2cd83bf`, none of the `1a08e75d` grade it replaced,
and none of `ACTIVE_RESEARCH.md` before the repair recorded in §5 below. Independence rests on the
untracked dispatch record, not on git authorship (D130).

---

## 1. The claim, and that it is false

`demo-output/website/ACTIVE_RESEARCH.md:25-33` at `c2cd83bf`, the paragraph headed
**"Update 2026-08-07 UTC"**:

> **round 5 (2026-08-07) is the entry of record: overall 0.0566, ~~locally rank 1 of 5~~
> **locally rank 1 of 7** (STRUCK 2026-08-15: `1 of 5` was the four-entry clone's denominator …)**
> under the R5 pre-registration (criterion overall < 0.065438 → ACCEPT); **AR_14's nominal
> best-on-board tie was lost as pre-accepted in writing (+0.0029)** against −0.0731 on the two
> Ret_360 ducts; the 6th cumulative scoring call.

Re-derived by execution — `LIVE_BOARD` and its four-entry sibling `CONTROL_BOARD_2026_08_10`
parsed out of `sdk/scripts/probability_of_rank.py` by `ast.literal_eval`, **never imported**,
joined to `round4_per_case` and `round5_per_case_full` — the `AR_14_Ret_180` column of the
six-entry board ran:

| entrant | AR_14_Ret_180 |
|---|---|
| **Yang** | **0.0250** |
| Reissmann, Fang & Sandberg | 0.0325 |
| Wu & Zhang | 0.0350 |
| Montoya, Oulghelou & Cinnella | 0.0487 |
| Tian, Buchanan, Hickel & Dwight | 0.0527 |
| Liu, Wang, Zhao & Xiao | 0.0548 |

**Round 4's `0.0325` stood 2 of 7** — tied with Reissmann for **second**, behind Yang by `0.0075`.
Round 5's `0.035339` stands **4 of 7**. On the four-entry board, and only there, `0.0325` was
rank **1 of 5** and the tie was for best. **There was no best-on-board tie on the board of record
to lose.**

---

## 2. Why it is inside the class — five grounds, none of which is "V10 already passed"

**(1) It is not protected as dated history.** The `c2cd83bf` reading, which this pass applies
rather than re-litigates, protects material *"explicitly labelled and dated as superseded"* — the
three D238 sites sit under headers naming round 4 and round 3 **as superseded**. This paragraph is
the **superseding** one: it opens *"round 5 (2026-08-07) is the entry of record"* and closes *"The
round-4 paragraph below is superseded."* A dated header is not a superseded label.

**(2) It is a caveat travelling with a round-5 number.** `(+0.0029)` is the round-5 delta on
`AR_14_Ret_180`, and the best-on-board clause states what round 5 cost. V10's class is *"round-5
numbers **with the same caveats**"* — this is the caveat.

**(3) The other enumerated surfaces carry a different caveat on the same event, which is what
"inconsistent surface" means.** `closure.html:351-358` attaches *"the aspect-ratio-14 duct places
**4th of 7**, and the best-on-board count is **2 of 8** … **zero of the 8** belongs to our model"*,
with the four-entry ordinals struck and dated. `docs/PRODUCT_LIST.md:105-114` attaches *"`AR_14_Ret_180`
places **4 of 7**, and the best-on-board tally is **2 of the 8**"* and rules the earlier reading
*"obsolete."* `ACTIVE_RESEARCH.md:29` attaches none of it.

**(4) The maintainers' own conduct settles it.** The **same paragraph** was repaired on 2026-08-15,
`1 of 5` → `1 of 7`, with a dated six-entry note. **Protected history does not get repaired.** If
the date exempted the paragraph, that repair was unnecessary — and it was demanded by V10's own
regrade.

**(5) The claim is false, and it is one of a computed family.** §4 derives the complete set of
best-on-board flips between the two boards; `AR_14_Ret_180` at round 4 is one of five.

**What this ruling does NOT say.** `closure.html:351` carries the same characterisation
(*"Round 4 held a nominal 0.00003-level tie for best-on-board"*) unstruck — but it time-scopes it
to round 4 **and** supplies the six-entry correction in the same note, three lines down, with the
four-entry ordinals struck and dated. It carries the round-5 numbers with the same caveats and is
**not** an independent V10 blocker. The rung fails on one surface, not two.

---

## 3. How the `c2cd83bf` sweep missed it, which matters more than the miss

**Its recogniser was a list of stale LITERALS and stale PHRASES, and this claim contains neither.**
The instrument searched for eight four-entry literals — `0.0592 0.1195 0.0760 0.0387 0.0341 0.0325
0.0364 0.0350` — and fourteen patterns including `rank N of 5`, `Nth of 5`, `4 of 8`, `5 of 8`,
`OUR MODEL LEADS`, `best score on the entire leaderboard`, `lead the entire public leaderboard`,
`beats all four published entries` and `t-gold…>#1`.

The clause at `:29` contains:

* **no stale literal** — its only numbers are `+0.0029` and `−0.0731`, and neither is four-entry-specific;
* **no ordinal** — it states no rank and no denominator at all;
* **none of the fourteen phrases** — `best-on-board` was not among them.

**A stale CHARACTERISATION carries no stale number, so a number-sweep cannot see it.** That is the
general form: `c2cd83bf`'s instrument could only find drift with a figure attached, and its 89
adjudicated hits are 89 hits of the kind it could see. Its controls were sound and its zeros were
real; they were zeros of the wrong quantity.

**A second mechanism, found in this pass's own instrument and reported because it will bite the
next one.** A first cut here classified sites by whether a correction marker stood within ±3 lines.
`:29` was filed as *"a correction stands nearby"* — because the `1 of 5` → `1 of 7` strike sits
**three lines above it, correcting a different claim**. **A repaired claim masks its unrepaired
neighbour.** Every correction-proximity heuristic inherits this, and the shape is the same one
`docs/PRODUCT_LIST.md:105` already names — *"the repair stopped one line short"*.

---

## 4. Sweeping the class instead of the list

Three instruments were written and two were discarded, which is stated because the discards are
the evidence that the third is sound.

* **v1 — withdrawn 5-grams.** Premise: the strings this lab has struck define the stale class.
  **It returned a FALSE ZERO on the known case**: the withdrawn form reads *"the nominal
  best-on-board tie **is** lost"* and the live sibling reads *"nominal best-on-board tie **was**
  lost"*. One inflected verb, no shared 5-gram, no hit. **Discarded because it failed a case it
  was known to have to catch — which is the only reason its zeros were not believed.**
* **v2/v3 — withdrawn 3-grams.** Found the case and buried it in **10,206** sites, because
  strike-and-keep makes a withdrawn span a near-duplicate of the correct text beside it.
* **v4 — the stale set DERIVED FROM THE DATA.** Both boards are fully determined, so the
  quantities true of the four-entry board and false of the six-entry board can be **computed**.
  Not a maintained list: a derived one, complete by construction over what it covers.

**The five best-on-board flips, computed:**

| case | round | our value | four-entry | six-entry |
|---|---|---|---|---|
| `alpha_15_13929_4048` | r5 | 0.050105 | **1 of 5 — best** | 2 of 7 |
| `alpha_15_13929_4048` | r4 | 0.050100 | **1 of 5 — best** | 2 of 7 |
| `alpha_15_13929_2024` | r5 | 0.101112 | **1 of 5 — best** | 2 of 7 |
| `alpha_15_13929_2024` | r4 | 0.101100 | **1 of 5 — best** | 2 of 7 |
| `AR_14_Ret_180` | r4 | 0.032500 | **1 of 5 — best** | 2 of 7 |

Both `alpha_15` hills lost to Tian, Buchanan, Hickel & Dwight; `AR_14` to Yang. Also computed:
best-on-board count round 5 **4 of 8 → 2 of 8**, round 4 **5 of 8 → 2 of 8**; overall **rank 1 of 5
→ 1 of 7**; margin **0.0028778 over Reissmann → 0.0013653 over Yang**.

**Result over 1,773 tracked text files**, read through `git show HEAD:<path>` rather than `grep`
(which here is `ugrep --ignore-files`) or `git grep -I` (which skips the files `.gitattributes`
marks binary), every strike span blanked **in place** with offsets preserved, whitespace collapsed
so a wrapped claim matches its unwrapped twin: **1,216 bare sites and 647 marked**, of which **55
bare sites sit on live or travelling surfaces**. Most are correct history or carry their
correction; the adjudicated live-falsehood siblings of this one clause are in §5.

**Frame limit, stated:** `dist/` and `demo-output/website/latex/` are outside this sweep by
instruction. `dist/` is also **untracked**, so no `git grep` instrument in this lab can reach it —
that is `D252`.

---

## 5. Repaired, and routed

**Repaired here** (no peer holds these; line numbers are as at `c2cd83bf`, before the repairs
shifted them):

* `demo-output/website/ACTIVE_RESEARCH.md:29` — the V10 blocker. Struck in place, kept visible,
  with the six-entry reading beside it.
* `demo-output/website/ACTIVE_RESEARCH.md:617` — same phrase in the round-5 scoring-day block; the
  tie with Reissmann is exact and stands, `best-on-board` struck.
* `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:1269` — the identical clause standing **one
  sentence after** the margin above it was repaired to Yang's `0.001365`, while `:579` of the same
  file had carried the corrected reading since 2026-08-12. The same shape a third time.

Strike balance re-audited after editing: `ACTIVE_RESEARCH.md` 48 → 52 markers, `CLOSURE_CHALLENGE_STATUS.md`
114 → 116, both deltas even, depth in `[0,1]` and final 0 in both — so no dangling opener was
introduced that could blank an unrelated region.

**Routed, not touched:**

* `demo-output/website/closure.html:291` and `:351` — **peer-held.** Not a V10 blocker per §2, but
  the bare phrase at `:291` is worth a strike for hygiene under V8's banned-claims list.
* `docs/PRODUCT_LIST.md` — **peer-held.** `:1811` is already ruled in `c2cd83bf` §5.
* `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1382` — *"`AR_14_Ret_180`, the duct
  the entry scores best on the board on"*, present tense, bare, on a **travelling** document; the
  duct places 4 of 7. Phrasing is ambiguous between "best on the board" and "our best duct", so it
  is filed rather than edited by a grader.
* `campaign/LADDER_V_V13_CLOSEOUT.md:184` — a signed close-out; whether it inherits this class or
  is snapshot-protected under D227 §5 is the chief's, and is `D251`.

---

## 6. What V10 needs now

The blocker is repaired, so V10 is **not** left failing on a live surface. What is owed is the
same thing V12 was owed: **the `PASS` at `c2cd83bf` was not entitled as issued**, because the
surface was in-class inconsistent at that commit. **A fresh V10 grade against HEAD is owed, by a
non-author of `c2cd83bf` and of the repair recorded in §5** — which excludes this grader.

And the method finding should outlive both rungs: **a cross-surface sweep whose recogniser is a
list of stale literals cannot see a stale characterisation.** The derived-stale-set instrument in
§4 is offered as the replacement, because its coverage is computed from the boards rather than
remembered by whoever writes the sweep.

---

*Non-author ruling on rung V10, dispatched after the V12 grade at `b4596cb4` filed `D251`. No
scoring call was made and the ledger stands at 6; no solver was launched; nothing was submitted,
uploaded, registered or sent. `dist/`, `demo-output/website/latex/`, `motorbike-video/` and
`LAPTOP_SHOOT.md` were not written; `dist/` was read only.*
