# V10 — fourth non-author grade of 2026-08-16, against the repair at `38cd036f`

**VERDICT: FAIL.**

**The rung falls inside the submission package again — not at the site the third grade named,
which was repaired correctly, but at two more instances of the same class in the same file,
both of which the repair opened, cleared on half of D294, and left. `DESCRIPTION_DOCUMENT.md`
now asserts in §4 that `AR_14_Ret_180`'s best-on-board tie *is lost* and in §2 that there
*was no best-on-board tie on this case to lose*. One travelling document, opposite
assertions, both landed on 2026-08-16. Every other criterion surface strikes the phrase and
says the tie was never a live one.**

**Grader:** an agent that wrote none of V10 — no grade, no repair, no reopen, no closure
record — and none of the surfaces below. Graded at HEAD `38cd036f`. Read-only across the
repository except this file and one docket row. **Nothing was repaired.** No solver ran, no
scoring call was made, the ledger stood at 6, nothing was sent, uploaded or registered, and
`dist/`, `demo-output/website/latex/`, `motorbike-video/` and `LAPTOP_SHOOT.md` were not
touched.

**THE FRAME WAS PINNED AND THE PIN WAS TESTED, because HEAD moved eight commits under this
grade while it ran.** The sweep initially resolved blobs through `HEAD:`; `HEAD` advanced from
`51d8eb43` to `38cd036f` mid-measurement, and `38cd036f` is the repair under grade, so a
moving frame could have had this grade reading the *pre-repair* file. The whole sweep was
re-run with the frame **pinned to `38cd036f`** and the two runs compared byte for byte:
**identical, zero differing lines.** The measurement was therefore never contaminated — but it
was checked rather than assumed, and `51d8eb43` was confirmed an **ancestor** of `38cd036f`
first, so the tree had advanced normally rather than been rewritten.

**Why a fourth grade, and what it was told to look for.** V10 has failed three times and each
failure landed on a surface the previous grade never reached — `ACTIVE_RESEARCH.md:29`, then
six instances on `closure.html` where three had been reported, then the submission package,
which no V10 grade had opened at all. **The shape is the same every time: a repair that fixed
a LIST instead of a CLASS.** This grade was run against that shape, and it found it a fourth
time — this time inside a file the repair had already swept.

---

## 1. The criterion, quoted from where it is, not from where records cite it

Older records cite `:359-362`; it has drifted. At `38cd036f` it is
`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md:386-389`, verbatim:

> - **V10. Cross-surface number sweep**: closure.html, the Active Research board, the wall,
>   PRODUCT_LIST, and the submission package must all carry round-5 numbers with the same caveats —
>   one inconsistent surface fails the rung (the board was still showing round 3 at last report;
>   that class of drift is what this rung exists to catch).

**The operative words are "the same caveats" and "one inconsistent surface fails".** The test
is not whether each sentence can be defended alone. It is whether the five surfaces agree.
There is no tolerance clause.

**The five surfaces resolved to paths**, and every one swept whole, never by line range:
`demo-output/website/closure.html` · `demo-output/website/ACTIVE_RESEARCH.md` ·
`demo-output/website/wall/wall.html` and `wall/wall.json` · `docs/PRODUCT_LIST.md` · all
**eleven** tracked members of `demo-output/website/closure_challenge_submission_round5/`
(3 text + 8 prediction CSVs, enumerated by `git ls-tree -r`). `benchmarks.html` was swept
beside them as a sixth, because it carries the same claim class.

---

## 2. The arithmetic, re-derived and not quoted from any document including the dispatch

`ast.literal_eval` on the `LIVE_BOARD` assignment node in
`sdk/scripts/probability_of_rank.py` — **parsed, never imported** — joined to
`demo-output/website/closure_challenge_round5_qcr.json`
`official_test_harness_result.round5_per_case_full` and `.round4_per_case`.

**`AR_14_Ret_180`, the live six-entry board, seven positions counting ours:**

| entrant | score |
|---|---|
| **Yang** | **0.0250** |
| Reissmann, Fang & Sandberg | 0.0325 |
| **ours, round 4** | **0.0325** |
| Wu & Zhang | 0.0350 |
| **ours, round 5** | **0.035339** |
| Montoya, Oulghelou & Cinnella | 0.0487 |
| Tian, Buchanan, Hickel & Dwight | 0.0527 |
| Liu, Wang, Zhao & Xiao | 0.0548 |

Computed, not read: round 4's `0.0325` stands **2 of 7**, tied with Reissmann — the tie
membership was derived by equality test, returning `['Reissmann, Fang & Sandberg']`. Round 5's
`0.035339` stands **4 of 7**. The board minimum on this case is **Yang's 0.0250**.

**So there was never a best-on-board tie on this case *on the live board*, and there WAS one
on the superseded four-entry `deb91557` clone, in which Yang does not appear.** Both halves
matter, and the second half is what the failure below turns on: the two statements
*"there was no best-on-board tie to lose"* and *"the tie was against the four-entry clone"*
are each true of one board and false of the other, so a document that asserts both without
reconciling them has not stated one caveat — it has stated two that contradict.

---

## 3. Instrument, and the detection rule as it stands today rather than yesterday

**The standing instruction is no longer "use `\s+`".** Line-continuation prefixes are stripped
**with offsets preserved** — leading `>`, repeated `> >` and list markers overwritten with
spaces **in place, same length, newlines untouched** — so detection sees clean text while
every quotation, line number and strike span comes from the unmodified original. The strip is
asserted byte-length-equal on every line, and the whole-text assertion `len(stripped) ==
len(original)` runs on every file.

**And that alone is still not enough, which this instrument was built knowing.** A
hyphen-split wrap — `best-on-\n> board` — defeats a `\s+` pattern *even after* the prefix
repair, because a hyphen is not whitespace. **Every token joiner here is `[-\s]{1,20}`**,
which crosses a hyphen, a newline and a stripped prefix alike.

Strike spans are computed on the **original** bytes over three mechanisms (`~~…~~`, `<s>`,
`<del>`) and blanked in place, so liveness is decided by the real document.

Two recogniser families: **A**, the best-on-board / tie characterisation (nine forms); **B**,
an ordinal pinned on a board (five forms).

### 3.1 Controls — planted by line index, read back AT that index, before any zero was believed

| control | planted at | result |
|---|---|---|
| plain form, unwrapped | line 40 | **FOUND** |
| **wrap control**, split across a real newline | line 49 | **FOUND** |
| **blockquote-wrap control**, `best-on-\n> board` | line 58 | **FOUND** |
| inflected sibling sharing no 5-gram with the first | line 67 | **FOUND** |
| negative form `the tea is lost on that duct` | line 120 | **correctly rejected** |
| **struck negative** `<s>a best-on-board tie for best was lost</s>` | line 50 of `ACTIVE_RESEARCH.md` | **0 live hits on the planted line** |

Each plant went into a **scratchpad copy** of a real file's HEAD bytes — no tracked path was
written — and each was **read back by slicing the file at the planted index** and asserted
byte-equal to the planted form, rather than by searching the whole file for it.

**`scripts/control_kind.py` classified the ledger RECOGNITION**, derived from the evidence and
not from any label this grader typed: *four mutually independent forms in the vocabulary of a
claim surface characterising a case as board-best, all found; one negative form correctly
rejected.*

**The blockquote-wrap control reproduced the false zero before it fixed it**, which is the
only proof that the prefix repair is doing work: with the prefix repair **disabled** the
planted `best-on-\n> board` was **NOT FOUND**; with it **enabled** it was **FOUND**. The trap
is live, and knowing about it is not what caught it — the readback is.

---

## 4. The repair at `38cd036f`, tested on BOTH halves of D294

D294's two halves: **(a)** does the claim travel with a board identifier; **(b)** is the claim
**true** of the board it names. The row's own words: *"a caveat-adjacency test grades whether a
claim TRAVELS WITH its board, and is silent on whether the claim is TRUE of that board."*

### 4.1 `:112-120` — the site the third grade failed the rung on. **REPAIRED. PASS on both halves.**

The false sentence was removed and replaced in-block with the four-entry provenance, the
six-entry board, **both** retrieval timestamps, and the derived placements. **Half (a):** the
block carries `deb91557`, `2026-08-11T23:33Z` and `2026-08-14T21:01Z`. **Half (b):** every
figure in it matches my independent derivation in §2 — `2 of 7` tied with Reissmann, `4 of 7`,
Yang's `0.0250`. Nothing to add; the site is correct.

### 4.2 `:97` — the heading the repair deliberately left. **I AGREE, and the reasoning holds.**

The repair argued a heading is its own block under D294, but that this one *"names a
disclosure section and asserts no value and no board frame, so neither half of the rule has
anything to bind to."* Tested rather than accepted:

> `### 2. Best-on-board count, stated with its own qualification`

**The reasoning is sound and I add a second ground it did not use.** *"Best-on-board count"* is
a **noun phrase naming a metric**, not a proposition — there is no truth-bearer for half (b)
to evaluate and no ordinal for half (a) to qualify. And the strongest objection available —
that a reader might take the heading as implying a nonzero count — **fails on the text
directly below it**, which states in the same section that the count belonging to our model is
**ZERO of 8**. The heading additionally flags its own caveat in its own words
(*"stated with its own qualification"*), so it points at the correction rather than away from
it. **Correctly left.**

### 4.3 `:173` and `:192` — **THE BLOCKER. Half (a) PASSES. The rung fails anyway.**

Both carry in-block board identifiers — `deb91557`, both retrieval timestamps, the six-entry
board — so **half (a) passes at both**, which is what the repair checked and why it cleared
them. It reported *"the placement class re-checked at 3 sites all with in-block
identifiers."*

**What was not checked is whether the document still says one thing.** Verbatim at
`38cd036f`, all three confirmed present by byte test:

> **§2, `:118-119`:** *"**`AR_14_Ret_180` was never best on board**, and there was no
> best-on-board tie on this case to lose; what was lost was a tie for second."*

> **§3b, `:173`:** *"**The loss then happened** — 0.0325 → 0.0353, **the best-on-board tie
> gone** *(board identifier added 2026-08-16 … the tie was against the **four**-entry
> `deb91557` clone …)*"*

> **§4, `:192`:** *"`AR_14_Ret_180` went 0.0325 → 0.0353 (+0.0029) in round 5 and **its
> 0.00003 best-on-board tie is lost**. *(Board identifier added 2026-08-16: the tie was
> against the **four**-entry `deb91557` clone …)*"*

**§2 says the tie never existed. §3b and §4 say it existed and was lost.** Same document, same
case, same day, opposite assertions.

**Measured rather than asserted**, with `scripts/use_mention_discriminator.py` and the claim
span passed explicitly as its API requires:

| site | claim span | verdict |
|---|---|---|
| `:192` | `its 0.00003 best-on-board tie is lost` | **ASSERT** — own voice, claim not set off or attributed |
| `:119` | `there was no best-on-board tie on this case to lose` | **CANNOT_TELL** |

**CANNOT_TELL was NOT promoted to ASSERT.** `:119` is hand-adjudicated as an assertion on
written grounds: it is bolded, in the document's own voice, inside the correction block the
repair itself wrote, and it is the sentence the repair added in order to *replace* a claim.
The discriminator returns CANNOT_TELL because the sentence carries neither an enclosure nor a
first-person marker, which is the instrument's declared limit and not evidence of neutrality.

**`:192` is an ASSERT by measurement, on the surface that leaves the lab.** That alone is the
finding: the submission package asserts, in its own voice, that a best-on-board tie on
`AR_14_Ret_180` existed and was lost, while the same package asserts two sections earlier that
no such tie ever existed.

---

## 5. The inter-surface test the criterion actually asks — and the package is the odd one out

The criterion is about **the same caveats across surfaces**. Measured, every live family-A hit
opened by hand:

| surface | how it resolves the AR_14 tie |
|---|---|
| `closure.html` `:192`, `:197` | *"**struck 2026-08-16: there was no best-on-board tie to lose**"* — wording **struck** |
| `closure.html` `:302` | `<s>a best-on-board tie</s>` **`a tie for second`** — **struck and replaced** |
| `closure.html` `:373` | *"so **there was never a best-on-board tie to lose**"* — **struck** |
| `closure.html` `:403` | `<s>a tie</s>` **`a tie for second`** … *"it was never best-on-board"* — **struck** |
| `ACTIVE_RESEARCH.md` `:29-37` | `~~AR_14's nominal best-on-board tie was lost~~` → **"AR_14's nominal tie with Reissmann was lost"** — **struck and replaced** |
| `benchmarks.html` `:128-130` | *"On the six-entry board … **so that tie was never a live one**"* — resolved |
| `wall/wall.json` `:56` | superseded counter **struck**, kept visible, six-entry board named in-block |
| **`DESCRIPTION_DOCUMENT.md` `:173`, `:192`** | **wording LEFT ASSERTED AND UNSTRUCK**, parenthetical appended |

**Every one of the other criterion surfaces strikes the "best-on-board tie" characterisation
and says the tie was never a live one. The submission package alone leaves it asserted — and
simultaneously denies it in its own §2.** That is one inconsistent surface, it is the one that
travels, and under the criterion's own words the rung fails with no tolerance to spend.

**Two independent grounds, and the first does not depend on any view about how strikes ought
to be done:**

1. **Intra-surface contradiction.** §2 and §4 of one travelling document assert opposite
   things about the same case. A reader of the package cannot determine whether an
   `AR_14_Ret_180` best-on-board tie ever existed.
2. **Inter-surface divergence.** The package's caveat is not the caveat the other five
   surfaces carry.

**And the class-not-list shape is exact:** the repair fixed the one site the third grade
named, opened the other instances, cleared them on half (a), and left the document
self-contradictory. **A per-site check cannot see a defect that lives in the agreement between
sites** — which is the same shape D49 recorded one rung over, where a per-row check could not
see a defect living in a pairing.

---

## 6. The three items I was told to rule on rather than ignore

**6.1 `docs/PRODUCT_LIST.md:1810-1812`, ruled outside the claim class (D246). I AGREE**, on
two independent grounds neither of which is inherited. **(i)** My recogniser matched
**11 family-A and 39 family-B** hits in that file and matched `1810-1812` **not at all** — an
instrument built for this class does not see it. **(ii)** Re-verified by execution:
**`0.0748` occurs ZERO times in that file's 3,996 lines.** Independently, the sentence names
its board **by entrant count** — *"the supplied baseline beats all four published entries"* —
which is the lab's own admissible identifier form, and its subject is the **organisers'
baseline**, not our entry's standing.

**6.2 The surviving live matches on `closure.html`. I AGREE — and my sweep found six more than
the third grade adjudicated, and all six are also clean.** My broader family returned **ten**
live family-A hits there (`:124`, `:129`, `:192`, `:197`, `:302`, `:319`, `:373`, `:381`,
`:403`, `:467`), against the four previously ruled on. Every one was opened: each carries an
explicit refuting or dating operator **and** an in-block board identifier, and `:467` is a
leaderboard table row whose board is named in the table header (*"live, fetched 2026-08-11"*)
and which is true of that board. **The extra six strengthen the third grade rather than
qualifying it: a wider recogniser found more of the class on that page and none of it live as
a defect.**

**6.3 The five `PRODUCT_LIST` hits with no board identifier in-block — clean, and here is why
rather than an assurance.** `:1826` and `:2014` classify **CANNOT_TELL** and were **not
promoted**; hand-adjudicated as records of a past finding on their own text — `:1826` reads
*"Four external surfaces … **claimed** best-on-board 4 of 8 … **Fixed**, generator re-verified
key by key"*, and `:2014` reads *"carries the **withdrawn** best-on-board phrasing … **Hers to
correct; surfaced, not edited**"*. `:2509` classifies **MENTION** on the positional test — the
claim is inside quotation marks. `:2413` names a *category* of sentence that was traced, and
`:2057` quotes a reservation. **None asserts a board standing.**

---

## 7. Everything else, clean by execution

All eight prediction CSVs and `MANIFEST.json` and `README.md` in the package returned
**0 raw, 0 live** on both families. `wall/wall.html` returned **0 raw** on both. Strike parity
in `DESCRIPTION_DOCUMENT.md` is **40 `~~` markers, even**, with no `<s>`/`<del>` at all, so no
dangling opener is blanking text — measured, because an unbalanced strike is itself a
false-zero mechanism.

**One reporting discipline observed rather than claimed:** the third grade recorded that its
own hit dump was piped through `head -220` and **silently truncated the package's site list at
8 of 31, hiding a live blocker**. Every listing in this grade was written **unpiped to a file
and read from the file**, and the family-A live list was printed in full — 34 hits, every one
opened.

---

## 8. Verdict

**FAIL.**

The rung's own words are *"one inconsistent surface fails the rung"*, and the inconsistent
surface is `demo-output/website/closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`,
which at `38cd036f` asserts both that `AR_14_Ret_180`'s best-on-board tie **is lost** (`:192`,
ASSERT by measurement; `:173` the same in a second section) and that **there was no
best-on-board tie on this case to lose** (`:119`).

**What would clear it**, stated so the repair is not a guess and so the next grader can check
it in one pass: bring `:173` and `:192` into line with the treatment every other criterion
surface already uses — strike the *characterisation* and not merely append a board identifier
to it, as `closure.html:302` and `ACTIVE_RESEARCH.md:29-31` both do — **or** narrow §2's
`:118-119` so its denial is explicitly scoped to the six-entry board rather than absolute.
Either resolves the contradiction; doing neither leaves the package asserting P and ¬P.

**What must NOT be done:** repairing only `:192` and leaving `:173`. That is the fourth
repetition of the shape this rung has now failed on four times, and `:173` is the harder one
to see because its correction is long and reads as thorough.

**I repaired nothing.** The blocker is recorded and routed, not fixed, because a fix authored
in the same pass as the finding destroys the record of which is which.

### 8.1 Falsifiers for this grade

- **§4.3 falls** if a reader shows that *"there was no best-on-board tie on this case to
  lose"* and *"its 0.00003 best-on-board tie is lost"* are consistent as written in one
  document. The scoping clause each would need is absent from both; supply it and the finding
  goes.
- **§5 falls** if the chief rules that a per-sentence board identifier is sufficient and that
  cross-section agreement is outside V10 — which would also reverse the third grade.
- **The sweep falls** if a form of this class exists outside the nine in family A. The control
  is RECOGNITION over four independent forms, which bounds that risk and does not remove it.

---

*Graded 2026-08-16 at `38cd036f` by an agent that authored no part of V10. Every figure
re-derived by parsing an assignment node, never by importing a module and never by quoting a
document, a docket row or the dispatch. Controls planted by line index into scratchpad copies
and read back at that index; RECOGNITION established by `scripts/control_kind.py`; the
blockquote-wrap false zero reproduced before it was repaired. `__pycache__` purged before
measuring. No listing that was read was piped. Nothing repaired, no rung closed, no guard
tuned, no solver run, no scoring call made; the ledger stands at 6, and nothing was sent,
uploaded or registered.*
