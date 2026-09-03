# F5b COMPLETION SUCCESSOR COMPARATOR — PRE-REGISTRATION (STAGE 1)

**Status: DRAFT, NOT FROZEN. No F5b artifact has been graded with this instrument and none may
be until this document is committed and the §9 hold question below is answered by Sanaa.**

| | |
| --- | --- |
| team | cfd |
| rung | F5b physics rung — **instrument repair**, not a new physics rung |
| parent registration | `verification/campaign/F5b_PHYSICS_PREREGISTRATION.md` (**FROZEN; untouched by this document**) |
| comparator | `cases/F5b_pitching_airfoil/analyse_f5b_completion_successor.py` |
| predecessor | `verification/runs/F5b_runs/analyse_f5b_physics.py` — **EVIDENCE. Not edited, moved, copied, patched, imported or deleted.** |
| authority | Sanaa, 2026-09-03 ~22:50Z: *"and you have my GO for all ur asks"*, item 3 = **F5b OPTION 1 GO**. Captured at `etc/sessions/2026-09-03T2250Z_sanaa_go_all_asks.md`, commit `fbab523b`. **Her GO is a per-item reading of an enumerated list, not a blanket** (rule 9). |
| compute spent on F5b to date under this document | **ZERO** |

---

## 1. What option 1 is, quoted from the record rather than paraphrased

`docs/LAB_STATE.md:24642`, cfd board 48, committed:

> **The options are enumerated in the restatement routed to the chief.** In short: (1) successor
> comparator at a new path, no edit to the held file — legal on her own 2026-08-28 mechanism,
> needs no ruling on the denial at all; (2) rule narrowly on the denial, authorise the single
> step-2 correction; (3) discard the working-tree change — but rule 10 forbids
> `checkout --`/`reset`/`stash` and a restore is itself an edit to the denied file; (4) re-solve
> from scratch, ~39.4 core-min / ~$0.034 derived, cheap but discards intact artifacts; (5) leave
> it held — status quo, `NOT A RESULT` stands, topic open past the rule-freeze intent that
> instrument repairs be done once and closed.

`docs/LAB_STATE.md:24305`, same board:

> **F5b** — unruled since 2026-08-25, **nine days**. One-paragraph restatement delivered;
> recommendation is **option 1** (successor comparator at a new path, already legal under her own
> 2026-08-28 ruling, needing no ruling on the denial at all) and **I have not taken it**, because
> the hold artifact is unconditional and an agent's reading of her ruling is not her consent.

**This document builds exactly that: a successor comparator at a new path, with no edit to the
held file.** It is scoped to option 1 and to nothing wider.

**⚠ ONE CORRECTION TO THE LEGALITY CLAIM, MADE AGAINST OUR OWN RECOMMENDATION.** Option 1 is
described as *"legal on her own 2026-08-28 mechanism"*. Read at source
(`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md`), the sentence
*"Re-grades are successor comparators frozen by sha (rule 2); the original frozen files are never
edited"* is at **line 15, OUTSIDE the blockquote — it is the chief's routing note, not Sanaa's
words.** Her verbatim words in that directive (line 13) are *"re-grade each from preserved
artifacts through the repaired instrument"*, and they are scoped to **dafoam's seven readers**,
not to F5b. The successor mechanism is therefore supported by her words in **shape** but was
never ruled by her for **this rung** on 2026-08-28. What authorises this work is her **2026-09-03
option-1 GO**, and nothing earlier. *Stated because a mechanism attributed to the owner that turns
out to be the lab's own reading is how a lab acquires permissions nobody granted (rule 9).*

---

## 2. The defect, re-derived from the artifacts by this lane

**Not taken from the prose about it.** Every figure below was measured by this lane on
2026-09-03, reading directory names and mtimes only.

| what | measured |
| --- | --- |
| frozen predecessor blob at HEAD | `6c6d34d02e6de925457dbfdbf75a0e004168f345` — byte-identical to the stage-2 freeze blob at `a80d5f36` |
| the defective line | `analyse_f5b_physics.py:772` (HEAD blob) `tdir = os.path.join(case, END_TIME_STR)` with `END_TIME_STR = "21.9440"` at `:120`; the same `tdir` carries clause 6 at `:816` |
| what OpenFOAM actually wrote | `verification/runs/F5b_runs/physics_p1/case/**21.944**/` |
| does `case/21.9440/` exist | **NO** |
| entries in `case/21.944/` | `U Uf k meshPhi nut omega p phi polyMesh uniform yPlus` |
| required fields (parent registration §5 clause 4) | `U p k omega nut` — **all five present** |
| clause 4 under the defective reader | `os.path.isdir(case/21.9440)` is False → **ok4 = False**, all five fields reported missing |
| clause 4 under a correct reader | **ok4 = True**, `missing: none` |
| clause 6 under the defective reader | `"0/ or endTime dir absent"` → **ok6 = False** |
| clause 6 under a correct reader | argmax over `case/0/` is **`phi` at mtime 1787674465.215816**; earliest mtime in `case/21.944/` is **1787676831.571532**; every endTime file is **2366.36 s newer** → **ok6 = True**, `NOT strictly newer: none` |

**So the rung's `NOT A RESULT` rests on two clauses that both fail on one trailing zero, while the
physics artifacts are present and intact.** Costed at `docs/COST_CALIBRATION.md` row C-65:
**39.426 core-min MEASURED**.

**⚠ A CORRECTION TO BOARD 48, from this lane's own listing.** Board 48
(`docs/LAB_STATE.md:24636`) reports `case/21.944/` as holding *"`polyMesh` and `uniform`"*. The
directory holds **eleven entries including all five required fields**. The board's statement is
incomplete in the direction that understates the case for repair.

**⚠ AND THE DEFECT IS IN THE FROZEN REGISTRATION'S OWN PROSE, NOT ONLY IN THE READER.** The parent
registration's §5 clauses 4 and 6 are written as `case/21.9440/` **contains** … . A numeric
resolver therefore **departs from the literal wording of a frozen document**, and that departure is
declared here rather than discovered later: what clause 4 requires is *the fields written at
endTime*, and `21.944` **is** OpenFOAM's own name for endTime 21.9440. **No gate, threshold, band,
cap or label of the parent registration is altered by this successor** (rule 2). The parent is not
edited; this is a separate, separately frozen document.

---

## 3. The repair, and why it is structural

`resolve_end_time_dir()` implements `VERIFICATION_CHARTER` **§2p.5**: *"A reader that knows which
time it needs SELECTS BY THAT TIME and REFUSES if it is not uniquely present."*

1. Every subdirectory whose name parses as a time is parsed **as a number**.
2. **Exact rule:** candidates whose parsed value equals the registered endTime exactly. Exactly one
   → selected. More than one → **REFUSE**.
3. **Write-quantum rule** (only if the exact rule matched none): a candidate within half a unit in
   the last of OpenFOAM's 6 significant figures. Exactly one → selected, and the record says it was
   resolved by this rule. Zero or more than one → **REFUSE**.
4. There is no third rule. It never sorts, never takes "the latest", and never chooses among
   several.

**Changing the constant `"21.9440"` to `"21.944"` was rejected as the repair** (L-321): it leaves
the identical trap armed for the next endTime whose OpenFOAM rendering differs from its registered
spelling. The predecessor's `TIME_DIR_TOL = 1.0e-9` was also rejected: it is not live at t ≈ 21.944
(both spellings parse to the same double) but misses by **3.0** at endTime 1234567, which OpenFOAM
renders `1.23457e+06`. The write-quantum rule covers that case **and still refuses on ambiguity**,
which the tolerance alone does not.

---

## 4. Positive controls (`CLAUDE.md` rule 3) — eleven, all driving the shipped code

`--selftest`, **measured green 2026-09-03, rc 0, 0.40 s wall**:

| id | plant | required behaviour |
| --- | --- | --- |
| C-N1 | clean tree, endTime name written by OpenFOAM's own formatting | every clause able to **PASS** |
| C-P0 | endTime spelled `21.9440`, `21.944`, `2.19440e+01` | **all three resolve** — the L-321 defect, planted and repaired |
| C-P1 | endTime directory absent | **rc 2** through the real entry point |
| C-P2 | two directories resolving to endTime | **rc 2**, no choice made |
| C-P3 | each of `U p k omega nut` removed in turn | clause 4 fails **and only clause 4**, field named |
| C-P4 | an endTime field back-dated below `max(mtime)` over `0/` | clause 6 fails |
| C-P5 | `record.json` absent | clause 1 fails — **L-320's load-bearing operand**, the one that had never been falsified in a passing run of the predecessor's suite |
| C-P6–P9 | prelude `End` blanked; wrong last time; wall over cap; step counts disagree | each fails **its own** clause |
| C-P10 | an internal error injected into the shipped path | **rc 70**, record emitted with the `instrument_error` block, traceback on stderr |
| C-M1 | shipped `check_completion()` **replaced** in a subprocess | the suite must go **RED** (measured rc 2) |
| C-M2 | shipped `resolve_end_time_dir()` **replaced** in a subprocess | the suite must go **RED** (measured rc 1) |

**C-M1/C-M2 exist because a sibling lane's checker could have had its entire `check()` deleted with
`--selftest` still reporting every plant fired.** They make that claim impossible here: the suite's
green is *demonstrated* to depend on the shipped functions, not asserted to.

**The fixture builds time-directory names by FORMATTING a number; the reader resolves them by
PARSING a name.** Two different routes (L-321) — which is why their agreement carries information
and why the predecessor's own selftest could never have caught this.

**Disclosed honestly: C-M2 goes red at rc 1, not rc 2** — the mutant leaves the module in a state
where an exception escapes the suite. The control's requirement is `rc != 0` and it is met; the
value is recorded rather than tidied.

---

## 5. Exit-code contract (`VERIFICATION_CHARTER` §2ak, ruled 2026-09-03 at `5577cec9`)

| code | meaning |
| --- | --- |
| **0** | the completion rule was evaluated. **The verdict is in the record, never in the exit code.** |
| **2** | `EXIT_REFUSE` — a registered refusal. A statement about the run, by a working instrument. |
| **70** | `EXIT_INSTRUMENT_ERROR` (`EX_SOFTWARE`). **A crash is not a refusal.** The record is emitted anyway with the exception type, message, raise site and the comparator's own blob sha; the traceback goes to stderr. |
| **1** | **not used by this file.** A `1` means the top-level handler itself failed — §2ak's stated floor, not papered over. |

**No bare `assert` appears in the file** (measured: 0 occurrences). Every guard raises.
**Measured `--selftest` rc: 0 under `python3`, 0 under `python3 -O`, 0 under `python3 -OO`; the
no-arguments refusal returns 2 under both `python3` and `python3 -O`** (L-332 / L-475).

---

## 6. Scope — stage 1 only, declared so it cannot be mistaken for more

**Implemented:** completion clauses 1–8 of the parent registration §5, with clauses 4 and 6 keyed
to the *resolved* endTime directory.

**NOT implemented — they raise `NotImplementedError`:** `grade_G1()` (loop area `A_L`),
`grade_G2()` (C_L excursion), `grade_G3()` (admissibility). **This instrument cannot report a gate
quantity by construction.** This mirrors the parent registration's own §9 staged freeze.

**Therefore stage 1 can never produce a rung verdict.** The best outcome it can reach is *the
completion clauses hold*, which makes the rung **`PENDING`** on a stage-2 gate evaluation — never
`PASS`, never `GATE FAIL`.

---

## 7. Pre-declared outcome map (`CLAUDE.md` rule 1 vocabulary only)

| # | condition | verdict written |
| --- | --- | --- |
| 1 | all eight completion clauses hold on `physics_p1` | the rung's standing **`NOT A RESULT`** is recorded as having rested on an instrument defect, and the rung becomes **`PENDING`** on stage 2. **No gate value is quoted, because none was computed.** |
| 2 | any clause other than 4 or 6 fails | **`NOT A RESULT`** stands on its own merits, the failing clause named, and the instrument-defect finding stands separately |
| 3 | clause 4 or 6 still fails after correct resolution | **`NOT A RESULT`** stands, and the repair is recorded as **not** the cause of the original verdict |
| 4 | the comparator refuses (rc 2) | **`NOT A RESULT`** — the reading is declined, no partial result quoted |
| 5 | the comparator errors (rc 70) | **`NOT A RESULT`** for the run **and** a docketed defect finding for the instrument. A crash repaired and re-run silently would destroy a measurement of our own instrument reliability (§2ak). |
| 6 | the §9 hold is not released | **`BLOCKED`** — the instrument exists, is frozen and is unused |

---

## 8. Cost (`CLAUDE.md` rule 12)

**Unit: core-minutes = wall seconds × ranks ÷ 60. Ranks = 1. No solver runs under this document.**

| item | value |
| --- | --- |
| **cost_basis** | **MEASURED ON THIS BOX, 2026-09-03**: `check_completion()` on a synthetic tree byte-matched to F5b's real artifact sizes (log 140,744,805 B against the real 140,744,871 B; `coefficient.dat` 9,691,232 B against the real 9,694,448 B — sizes read by `stat`, **no file contents opened**) ran in **4.67 s wall at 1 rank = 0.0779 core-min**, peak RSS **340.6 MB**, at load average **31.27** (contended; the direction is unfavourable, so the estimate is conservative) |
| **Point estimate** | **0.08 core-min** |
| **RUN CAP** | **1.00 core-min** (12.8× the point estimate). **An overrun stops the run; it does not get a new budget.** |
| **Selftest cost** | **0.40 s = 0.0067 core-min MEASURED**, run before this freeze on synthetic trees only |
| **Rate** | **$0.0513 / core-h**, c7a.4xlarge — **reported-by-owner, NOT measured.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| **Dollars at the cap** | 1.00 core-min = 0.0166667 core-h × $0.0513 = **$0.000855 — DERIVED, NOT MEASURED** |
| **Authorisation** | inside the $25 pre-authorisation; this is **this item's** cap, not a new ceiling (rule 9) |
| **Close-out** | on completion, actual vs this estimate lands as a row in `docs/COST_CALIBRATION.md` with the ratio and the gap attributed (rule 12) |

---

## 9. Freeze condition, and the hold question this lane does NOT answer

**Freeze condition, measured in the writing invocation:** the newest write anywhere under
`verification/runs/F5b_runs/physics_p1/` is **`LANE_STATE.md` at 2026-08-25T16:58:42Z** (69 entries
walked). **No agent has inspected F5b's gate quantity; no `A_L` exists anywhere; `coefficient.dat`
has produced no derived artifact.** This lane preserved that in taking its measurements: directory
names, entry names, `stat` sizes and mtimes only. **Zero F5b file contents were opened.**

**THE HOLD.** `verification/runs/F5b_runs/DO_NOT_RUN_THE_WORKING_TREE_READER.md`, stamped
2026-08-25, four prohibitions:

> - **Do not run this file.**
> - **Do not edit, restore, rename, move or delete it** until Sanaa rules on the denial.
> - **Do not grade F5b with it**, or with any patched copy.
> - **Do not inspect F5b's gate quantity** by any means, including a quick look at a `.dat` or a
>   plot. Doing so voids the §2d.1 addendum path and would force a fresh solve.

**Where this document sits against it, stated plainly rather than resolved in our own favour:**

| prohibition | this successor |
| --- | --- |
| do not run the held file | **outside** — never run, never imported |
| do not edit/restore/rename/move/delete it | **outside** — untouched; its blob is unchanged by this work |
| do not grade F5b with it *or with any patched copy* | **outside as built** — this is a fresh instrument at a new path, written against the frozen *registration*, not a patch of the held file. **A successor produced by copying-and-fixing the held file would be inside this clause**, which is why none was made. |
| **do not inspect F5b's gate quantity** | **⚠ NOT OUTSIDE.** Stage 1 computes no gate quantity, but clause 5 **opens `coefficient*.dat` to count its rows**, and the hold names *"a quick look at a `.dat`"*. **Pointing this instrument at `physics_p1` is therefore inside the hold's fourth clause on a literal reading.** |

**AND THE HOLD'S RELEASE CONDITION IS NOT LITERALLY SATISFIED.** The hold releases *"until Sanaa
rules on the denial"*. **Option 1, by its own description, needs no ruling on the denial at all** —
so her option-1 GO authorises the successor **without** discharging the condition the hold names.

> **THEREFORE: BUILDING AND SELF-TESTING THIS INSTRUMENT PROCEEDS. RUNNING IT AGAINST
> `physics_p1` DOES NOT, UNTIL SANAA RELEASES THE HOLD OR STATES THAT HER OPTION-1 GO RELEASES
> IT.** Reading her option-1 GO as a release of a hold whose fourth clause it does not mention
> would be an agent's inference standing in for the owner's consent — **rule 9, the precise shape
> this lane was told to refuse.**

**Who may release it:** the hold names **Sanaa** and no one else. It was raised by a cfd lab-lane;
its release is not a lane's, not a supervisor's and not the chief's.

---

## 10. Filing

The comparator is filed at **`cases/F5b_pitching_airfoil/analyse_f5b_completion_successor.py`** —
**outside the run root.** The predecessor lived *inside* `verification/runs/F5b_runs/`, the very
directory whose absence was its own rule-2 pre-compute proof: two conditions that cannot both hold
at one commit. `scripts/check_filing.py` reports **no violation attributable to this file** (the
51 standing violations in that report are pre-existing and lab-wide).

---

## 11. What a supervisor must check before freezing this

1. Read `analyse_f5b_completion_successor.py` **as a diff** (non-delegable check 1), the resolver
   and the mutation controls first.
2. Confirm this document is **committed** before the instrument is pointed at any F5b artifact
   (non-delegable check 4).
3. Route §9's hold question to Sanaa. **This lane does not answer it and did not act on it.**
4. Decide whether the §2 correction to board 48's `21.944` listing, and the §1 correction to the
   "her own 2026-08-28 mechanism" attribution, need landing on the board.

**Drafted by:** cfd lab-lane, 2026-09-03. **Zero F5b compute. Zero F5b file contents read.**
