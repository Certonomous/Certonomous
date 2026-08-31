# SUPERSEDED DRAFTING RECORD — THIS BLOCK HAS **LANDED**

> **THE HEADING BELOW IS STRUCK AND ITS CLAIM IS NO LONGER TRUE.** This file said
> *"DRAFT — NOT LANDED, NOT APPENDED, NOT COMMITTED"*. **It landed as AMENDMENT 3 on
> 2026-08-31**, cleared by the dafoam-supervisor after a personal read, appended to
> `cases/dafoam/ladder-a/A1/curriculum_SO1bR/PREREGISTRATION.md` through
> `scripts/append_block.py`. **The authoritative text is the one in `PREREGISTRATION.md`;
> this file is the drafting record only and MUST NOT be edited to diverge from it.**
> The header is corrected rather than left standing, because a file asserting "NOT LANDED"
> about something that has landed is precisely the misdirection this amendment exists to
> fix — the same defect, one directory over.

~~**This file is a DRAFT of a proposed AMENDMENT 3 to
`cases/dafoam/ladder-a/A1/curriculum_SO1bR/PREREGISTRATION.md`.** It exists so the
dafoam-supervisor can read the block before it lands. **`PREREGISTRATION.md` is
byte-unchanged and has not been opened for writing by the lane that wrote this file.**
Nothing below is in force.~~ If the supervisor clears it, the block from the horizontal rule
onward is **appended at the foot** of the frozen document through `scripts/append_block.py`
— the same mechanism AMENDMENT 1 used, so no shell sees the body — and nothing above the
append point is touched.

**Nothing here is sent, filed, uploaded, registered, posted or commented outside this box.
SUBMISSIONS ARE PARKED** (`CLAUDE.md` rule 7).

---

> **RENUMBERED, AND FLAGGED RATHER THAN DONE QUIETLY.** This block was drafted as
> AMENDMENT 2. While it was awaiting the supervisor's read, the **aggregate call-site repair
> landed as AMENDMENT 2** (2026-08-31, `so1br_chain_driver.sh:206` destroyed `AGG` by its own
> first use), because that amendment had to land in the same commit as the code change it
> describes. **This block therefore becomes AMENDMENT 3, and the version bump moves 1.2 →
> 1.3.** The renumber is stated here, not applied silently; the supervisor should confirm it
> before this lands. **Its prefix-invariance proof (§A3.4) must be RE-RUN against the
> document as it now stands (861 lines, 57,491 bytes) — the 654-line/44,718-byte figures
> below were measured before AMENDMENT 2 landed and are STALE.** They are left visible rather
> than overwritten so the staleness is auditable.

## AMENDMENT 3 — 2026-08-31 — THE §9 AND §12 EXISTENCE CLAIMS ARE SUPERSEDED BY AMENDMENT 1, WHICH LANDED IN THE SAME COMMIT THAT MADE THEM FALSE

**Version 1.2 → 1.3. Lines whose number changed above this section: 0** — to be proved in
§A3.4 by byte comparison of the pre-append prefix against the document as it stands at the
moment of landing, **not merely asserted**.

**This amendment moves no gate, no threshold, no band, no cap and no label**, and re-pins no
md5. It is a **supersession notice on two existence claims** and nothing else. Under
`CLAUDE.md` rule 6 the originals are **struck, never rewritten**: the struck text stays
exactly where it is, in its own words, and this section is the only place a reader is told
it no longer holds.

### A3.1 WHAT IS STRUCK

**STRUCK — §9, the table headed "FILES A STAGE-2 RUN WOULD NEED, EXISTENCE CHECKED FIRST —
AND THEY DO NOT EXIST", rows 1 and 2:**

> ~~`| cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_chain_driver.sh | **NO** |`~~
> ~~`| cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_run_arm.sh | **NO** |`~~

**STRUCK — §12, the sentence beginning "That chain needs two files", and the two bullets
under it that describe those files as owed:**

> ~~"That chain needs two files **which do not exist** (§9)"~~

**STRUCK — §12's opening line, insofar as it directs the reader to a conclusion that
AMENDMENT 1 had already reversed before the commit closed:**

> ~~"**This is the section to read before believing SO-1bR is ready to run.**"~~

**§12's heading, "STAGE 2 IS NOT FROZEN HERE", is struck as a statement about the document
and NOT as a statement about Stage 1.** Everything §12 says about *why* Stage 1 stopped
where it did — that ≈ 844 lines of derived shell which cannot be executed would be exactly
the unverified surface §9 warns about — **stands, and is the reason the two-stage shape was
right.** Nothing in this amendment claims Stage 1 should have gone further.

### A3.2 WHY THE STRIKE IS A SUPERSESSION AND NOT A CORRECTION OF FACT

**Neither struck claim was false when it was written.** §9 and §12 were authored at Stage 1,
when the two files genuinely did not exist, and the §13 rule-2 condition recorded that
absence with a planted-zero control. `AMENDMENT 1 — STAGE 2 REGISTERED: THE DERIVED DRIVER
AND LAUNCHER` was then appended **at the foot of the same document, inside the same commit**
`fa18e2312fb2a35f93f57f29c799b8dfe33ec07a`, and registered both files.

**So the defect is not an error. It is a document that contradicts itself within one commit,
and it contradicts itself in the direction that stops work.** §12's first line instructs the
reader: *"This is the section to read before believing SO-1bR is ready to run."* A reader who
obeys that instruction reaches "two files which do not exist" and concludes the item cannot
run — while the amendment 200 lines below registers those same two files with md5 pins the
driver asserts at run time. **An append-only convention keeps earlier text honest about when
it was written; it does not, on its own, stop that text from misdirecting a later reader.
This block is the missing signpost.**

### A3.3 THE MEASURED CURRENT STATE OF THE TWO STRUCK FILES

Read from disk and from git on 2026-08-31, by running the commands rather than recalling
them. `HEAD` at the reading: `998dc230f68f0d1d6a528792dcb1e5813c82325d`.

| file | exists | committed at `fa18e231` | disk vs HEAD blob | md5 on disk | pin the driver asserts |
|---|---|---|---|---|---|
| `so1br_chain_driver.sh` | **yes** | yes | **byte-identical** | — | it *is* the driver |
| `so1br_run_arm.sh` | **yes** | yes | **byte-identical** | `9e1b626dc26b7ee04ea4ed4c7cffdff1` | `MD5_LAUNCHER` (`:35`) — **agrees** |
| `so1br_grade_cli.py` | **yes** | yes | **byte-identical** | `f8dfc85d827f6fbf66ec425753fbd669` | `MD5_GRADER` (`:36`) — **agrees** |
| `so1br_precondition.py` | **yes** | yes | **byte-identical** | `447eaada4a896fc5f8b0f4ced4cb2af8` | `MD5_PRECOND` (`:84`) — **agrees** |
| `so1br_aggregate_memory.py` | **yes** | yes | **byte-identical** | `709ab0b98ef0302a3a3a318588f9493f` | `MD5_AGG` (`:85`) — **agrees** |

All sixteen files in the case directory are byte-identical to their `HEAD` blobs, and
`fa18e231` is an ancestor of that `HEAD`.

**The registered input is present**, which is the whole reason SO-1bR exists:
`/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/SO1aR_grade_20260828T171830Z.json`,
md5 `194c0440b8e36e8044795449c7df7edb` — **agreeing with the §9 pin**.

### A3.4 THE PREFIX-INVARIANCE PROOF — MEASURED, NOT ASSERTED

`CLAUDE.md` rule 6 requires the assertion *"lines whose number changed above this section:
0"*. **An assertion of that shape is worth nothing unless somebody ran the comparison**, and
other records cite this document by line number with at least one citation sitting inside an
executable check, so a silent renumbering above this point would break them.

**STRUCK — the figures this block carried while it was a draft.** They were measured on
2026-08-31 *before* AMENDMENT 2 landed, and AMENDMENT 2 added 207 lines to the foot of this
document. They are **struck in place and left visible**, never silently refreshed, so that a
reader can audit the staleness rather than discover it:

> | reading | value |
> |---|---|
> | ~~`PREREGISTRATION.md` before the append~~ | ~~**654 lines, 44,718 bytes**~~ |
> | ~~candidate after the append~~ | ~~781 lines, 52,527 bytes~~ |
> | ~~first 44,718 bytes / first 654 lines, vs the original with `cmp`~~ | ~~IDENTICAL, rc = 0~~ |
> | ~~`## ` headings~~ | ~~all **15** at identical line numbers~~ |

**RE-MEASURED AT THE MOMENT OF LANDING**, in the **same shell invocation as the append**, so
that no peer commit between measuring and appending can invalidate it. The proof compares the
**pre-append prefix** of the landed document against the document exactly as it stood:

| reading | value |
|---|---|
| `PREREGISTRATION.md` immediately before this append | **@@NL@@ lines, @@NB@@ bytes**, md5 `@@MD5@@` |
| first @@NB@@ bytes of the result, compared to the whole pre-append document with `cmp` | **@@PBYTES@@** |
| first @@NL@@ lines of the result, compared to the whole pre-append document with `cmp` | **@@PLINES@@** |
| line number of all `## ` headings, before vs after | **@@PHEAD@@** |

**Lines whose number changed above this section: @@PVERDICT@@.**

The control that makes the proof mean something: the comparison is **shown able to fail**.
The same byte-prefix comparison, run against a candidate built from a **deliberately mutated**
copy of the pre-append document — one token changed at line 298, the first struck row —
reports **@@PCONTROL@@**: it names the mutated line exactly. A comparison
not shown able to see a difference is not evidence (`CLAUDE.md` rule 3).

### A3.5 WHAT THIS AMENDMENT DOES NOT DO

* **No gate, threshold, band, cap or label moves.** `SO1BR-CAP-MANIFEST v1 MESH=5.0 O-P=25.0
  E-P=30.0 O-S=25.0 E-S=30.0 CEILING=115.0` is untouched; the 20.2 core-min point, the band
  `[11.0, 58.0]` and the 115.0 ceiling are untouched; `G-CPUSET`, `G-SO1AR`, `G-ROOT.5` and
  `G-CAP-PREREG` are untouched.
* **No md5 is re-pinned and no instrument is edited.** This block adds no file to the
  execution path and removes none.
* **The rule-2 condition is not re-opened, and it has now been CONSUMED rather than
  violated.** §13 and §A1.9 recorded, with a planted-zero control, that no `CURRICULUM-SO1b*`
  and no `CURRICULUM-SO1bR*` run root existed. That was true when written, and it was still
  true at **2026-08-31T15:01:00Z**, when the queue entry was filed after re-verifying it.
  **It is no longer true, and the reason is the legitimate one:** the queue runner launched
  this item at **2026-08-31T15:01:22Z** (pid 25003, ranks 1, est 20.2 core-min) and
  `/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt` is **the run root
  SO-1bR's own launch created**. This is stated plainly because the alternative — a rule-2
  bullet that silently keeps claiming zero after the item has fired — is exactly the kind of
  sentence this lab keeps paying for. **The pre-compute condition was satisfied before
  compute and was then spent by compute; it is not available to be re-asserted.** Any future
  amendment to this document must treat the rule-2 gate as CLOSED (`VERIFICATION_CHARTER.md`
  §2b: after first compute, changes land only as dated addenda that cannot alter a gate,
  threshold, cap or label).
* **It does not claim SO-1bR has produced a verdict.** At the time of writing this block the
  chain had launched but no arm had completed, no grade JSON existed and **no verdict of any
  kind is claimed here.** The item's verdict, when it exists, belongs in `RESULTS.md` and is
  the frozen comparator's to state, not this amendment's.

### A3.6 A CORRECTION TO AMENDMENT 2's OWN REPAIR COMMENT — QUOTED AND STRUCK, BYTES UNTOUCHED

**Placed here, beside the pin, because that is where a reader meets it.** AMENDMENT 2 §A2.7
re-registers `so1br_chain_driver.sh` at md5 **`1c5adb42c018dc5237cb9367542f2437`**. The
call-site guard those bytes contain carries a comment with **two stale internal citations**,
written while the amendment numbering was still unsettled:

> ~~`# ---- CALL-SITE GUARD (ADDENDUM 3, 2026-08-31; CLAUDE.md rule 14) ---------`~~
> ~~`# leaves the while AND the arm loop, landing exactly where :217's break lands`~~

**CORRECTED, and the correction lives here and not in the file:**

* the guard landed as **AMENDMENT 2**, not "ADDENDUM 3";
* the break it lands beside is at **`:227`** post-repair, not `:217` — `:217` was that line's
  number *before* the guard's own eleven lines were inserted above it.

**THE BYTES ARE DELIBERATELY NOT RE-CUT** (dafoam-supervisor's ruling, 2026-08-31). The
comment is **non-executable**; re-cutting it would move a **registered md5 pin that other
instruments assert against**, forcing a pin migration and a re-freeze **for zero behavioural
gain**, and a churned pin is itself a live risk — the driver aborts the chain on an md5
mismatch, so every pin migration is an opportunity to strand the item. **A wrong comment is
cheaper than a churned pin, provided the correction is recorded where the reader meets the
pin.** That is what this section is; it is rule 6's quote-and-strike applied to a file whose
bytes must not move.

**Nothing about the guard's behaviour is in question.** `break 2` demonstrably leaves both
loops — driven in both directions in §A2.6 — and the citation error is in the prose beside it,
never in the control.

### A3.7 THE LESSON THIS PAYS FOR

**An append-only document can be internally false without any single sentence in it being
false**, and the append convention actively hides it: every block is honest about its own
moment, so nothing looks wrong on a linear read. The failure surfaces only when a reader
enters partway and obeys a signpost written before the thing it points at changed. **A
section that tells the reader "read this before believing X" acquires a duty the rest of the
document does not have: it must be re-checked at every amendment, because its whole function
is to be entered out of order.** Registering that as a habit, not a one-off fix, is the
point of this block.
