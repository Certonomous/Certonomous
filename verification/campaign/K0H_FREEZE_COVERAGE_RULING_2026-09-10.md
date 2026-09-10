# RULING — K0h's 11-path freeze set: **THE `COVERAGE` CLAUSE IS NOT WIDENED, BECAUSE IT NEEDS NO WIDENING. THE BLOCKER IS TWO LINES ABOVE IT, THE DEFECT IS LAB-WIDE ACROSS ALL FIVE TEAMS, AND THE MECHANISM IS WRONG IN BOTH DIRECTIONS**

**Ruled by:** verification-supervisor, as owner of `scripts/check_comparator_freeze.py` (`SUPERVISION_CHARTER.md` §3 check-1, an instrument read done personally and as a diff-level read of the source, not relayed).
**Date:** 2026-09-10. **HEAD at ruling:** `c41672a8`. **Routed by:** the chief, from heat-transfer.
**Cost:** **0 solver core-min, $0.00.** A source read plus a corpus sweep.
**Recorded `[lab-attributed]`; item (2) of §5 is on Sanaa's desk.**

---

## 1. THE QUESTION AS PUT, AND WHY ITS PREMISE IS REFUTED

heat-transfer asks that **`check_comparator_freeze.py`'s `COVERAGE` clause be widened from 8 to 11** before K0h can freeze. `K0h_PREREGISTRATION.md:1197` states it plainly:

> *"The freeze set is now **ELEVEN paths, not eight** … `scripts/check_comparator_freeze.py` enforces IDENTITY, CURRENCY and COVERAGE over the set; **COVERAGE is the clause that must be updated from 8 to 11.**"*

**`COVERAGE` HAS NO 8 IN IT. IT NEVER DID, AND IT IS ALREADY SIZE-AGNOSTIC.** Read at source:

- `pin_rows()` (`:411-437`) iterates **`for rel in sorted(pins)`** — one row per pinned path, however many there are.
- The figure printed is `PIN COVERAGE: {len(prows) - len(uncovered)} of {len(prows)}` (`:1560`) — **`len(prows)` IS the registration's own count.** An 11-path registration prints `11 of 11`.
- The clause's own text (`:97-102`) says exactly this: *"every pinned path must be judged. A pinned path that the walk does not reach is **INJECTED into the population by explicit path, whatever it is called and wherever it lives**."*
- **The only literal `8` in the file is a status sort-order key** — `"NO-MARKERS": 8` at `:1485`. There is no cap, no count, no eight.

**So the clause is not widened, and no code change to `COVERAGE` is owed.** heat-transfer's diagnosis was right that *something* blocks an 11-path freeze; it named the wrong clause, and the thing it named is sound.

---

## 2. WHERE THE BLOCKER ACTUALLY IS — `PIN_PATH`, TWO LINES ABOVE

`scripts/check_comparator_freeze.py:260`:

```python
PIN_PATH = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./+-]*\.(?:py|sh))`")
```

**A pin is only recognised if the path ends in `.py` or `.sh`.** `registered_pins()` (`:384-409`) builds the pin dict from that regex alone, so a pinned path with any other suffix **never enters `pins`**, never reaches `pin_rows()`, and is therefore not merely un-judged — **it is invisible, and `COVERAGE` cannot report it missing because `COVERAGE` never hears of it.**

**K0h's eleven are: the eight of §7.7, plus `orchestrate_k0h.py` — nine `.py`/`.sh` — plus `verification/campaign/K0h_STAGE_MANIFEST.json` and `…/K0h_PREFREEZE_EXTRACTION_DEMONSTRATION.txt`.** The last two are exactly the two the regex cannot see.

**The consequence is the shape `COVERAGE` exists to stop, arriving through the one door `COVERAGE` does not watch.** The instrument would print a clean, complete-looking **`PIN COVERAGE: 9 of 9`** — and the pre-registration itself says what is thereby left loose (`:1197`):

> *"**The manifest is not optional to pin** — it holds the ceiling and every cap, so a freeze that pins the code and leaves the manifest loose **leaves the numbers loose**."*

**That is correct and this ruling adopts it.** A freeze that certifies the comparator and not the file carrying the ceiling and the caps has not frozen the grading path; it has frozen the half that does not set the answer.

**This is the second instance of one class in this team's territory today**, and it is named as such rather than filed as a coincidence: `D593` found `check_filing.py` reporting `PASS` over a population its reader could not see, and `§2c`'s own words apply unchanged to both — *"a check reporting no violations over a population it could not evaluate has not passed; it has not run."*

---

## 3. THE DEFECT IS NOT K0h'S. IT IS LAB-WIDE, MEASURED, AND IT HAS BEEN DROPPING REFERENCE DATA FROM EVERY FREEZE CHECK IN THIS REPOSITORY

Swept by this supervisor over **1,677 registration-like `.md` files** (`docs/`, `verification/campaign/`, `cases/`), applying the tool's own `registered_pins()` logic with the suffix set widened to `.json`/`.csv`/`.txt` and struck spans dropped exactly as the tool drops them.

**39 files across ALL FIVE TEAMS gain pinned paths — 138 distinct paths.** By team: **heat-transfer 13, ansys 9, dafoam 8, cfd/verification 8, closure 1.**

**And the paths are not incidental. They are the inputs that decide verdicts:**

- **`T13`, `T14`, `T15`, `T16`, `T17`, `T18`, `T19`, `T9aR1b` `_registered.json`** — the registered sets, **carrying caps and thresholds**, across the whole T-family;
- **`gate_t3.json`, `gate_t17.json`, `gate_t18.json`, `gate_t19b.json`** — the gate records themselves;
- **`T5_reference_primary.json`**, **`suboff_reference_ReL1p2e7.json`**, **`tm_reference_M2p0_tc15.json`**, **`cases/dafoam/a2gc_levels.json`**;
- **`vmfl011_benchmark_xnorm.csv`, `vmfl013_fluent_wall4_nu.csv`, `vmfl013_vogel_eaton_nu.csv`** — the **Ansys benchmark reference data** three credentialed cases grade against;
- **`verification/campaign/K0h_STAGE_MANIFEST.json`** — K0h's ceiling and caps.

**A freeze check that pins the comparator but not the reference the comparator compares against does not answer its own question.** `IDENTITY`'s stated purpose (`:103-107`) is *"is the file that ran the file that was frozen"* — and for a graded row the reference data is as much "the file that ran" as the script is. **A reference `.csv` could be edited between freeze and grade and every limb of this instrument would still report `PIN-OK`.** No claim is made here that any such edit has occurred; the exposure is reported, not an incident.

---

## 4. AND THE MECHANISM IS WRONG IN THE OTHER DIRECTION TOO, WHICH IS WHY THE OBVIOUS FIX IS REFUSED

**Widening the suffix list is NOT the repair.** Of the 138 paths a data-extension widening would capture, this supervisor classified them:

| class | count | share |
|---|---|---|
| **A — INPUTS that decide a verdict** (registered sets, references, benchmarks, gate records, the K0h manifest) | **29** | 21 % |
| **B — OUTPUTS the run PRODUCES** (`COST.txt`, `RUN_RC.txt`, `SOLVER_RC.txt`, `*_GRADED.json`, `GRADING_*.json`, `CONTENTION.txt`, `CAP_OVERRUN.txt`, `LAUNCH*.txt`, `*.coresec.txt`, `verification/queue/**/launched/*.json`) | **102** | 74 % |
| unclassified | 7 | 5 % |

**Pinning an OUTPUT is incoherent, and it is incoherent in a way that breaks the instrument.** `IDENTITY` demands the worktree bytes equal the HEAD blob; **a run's output changes when the run runs.** A blanket suffix widening would therefore make this freeze check **refuse the majority of the very cases it exists to certify** — `PIN-DRIFT` on `COST.txt` for every case that recorded a cost.

**So the suffix whitelist is the wrong mechanism in both directions:** it silently drops the load-bearing inputs (K0h's manifest, seven `_registered.json`, three benchmark `.csv`), and if widened by suffix it silently captures 102 run outputs. **What may be pinned is a property of the REGISTRATION'S DECLARATION, not of a filename's extension** — which is precisely the argument the file's own header already makes against globs (`:90-93`): *"THE FIX IS NOT MORE GLOBS. A longer pattern list reproduces the defect with a longer list: it still decides the population from FILE NAMES, which is a property of nobody's registration."* **The `PIN_PATH` suffix list is that same defect, in the flag written to cure it.**

**`.md` is EXCLUDED from any proposed widening, and this is a narrowing this ruling adds.** Many of the 39 gain only *other `.md` documents* cited as predecessors in a movement-chain table — prose citations sitting in a row that happens to carry a blob, not pin claims. Capturing those would be `§17a`'s over-reach, which *"looks like rigour while it is happening"*.

---

## 5. WHAT IS DECIDED, WHAT IS REFUSED, AND WHAT GOES TO SANAA

**(1) `COVERAGE` IS NOT WIDENED — ANSWERED, NOT DECLINED.** No change is owed to it; the clause is size-agnostic and correct as written. **heat-transfer's freeze-ahead is not held by this clause and never was.**

**(2) THE `PIN_PATH` REPAIR IS REFUSED TO EVERY AGENT INCLUDING ME, AND IS PUT ON SANAA'S DESK WITH ITS MEASURED POPULATION.** `D539` is this team's own ruling: *"a checker that refuses a commit is a GATE ON LAB PROCESS, and **ADDING a gate is reserved to Sanaa exactly as retiring one is**"*, clause (a) *"**NO AGENT MAY FLIP IT** … a measured rate that 'looks acceptable' is not an authorisation."* This change would make an **adopted, refusing** instrument refuse across **39 registrations in five teams**, and **the fact that this supervisor believes the input half of it is correct is exactly the reasoning `D539` forbids acting on.** The desk item is the **29 / 102 split**, because that is the number her ruling has to rest on: *which* paths a registration may pin is the question, not *how many*.

**(3) L-221 / L-222 APPLY, AND THE ANSWER TO heat-transfer'S QUESTION IS YES.** Their principle — *insert with an assert, never replace; and a lesson is not applied until **every** call site asserts it* — transfers directly. Any eventual repair **extends** the alternation and never rewrites the pattern, and it is not applied until a control fires **both ways in the same run**: a newly-recognised path must pin, **and** a `.py`/`.sh` path must still pin. There is exactly one call site (`registered_pins()`, `:384`) and its selftest must carry both arms; a one-directional control here would certify the widening while a silent narrowing went unmeasured, which is `§28.19`'s form.

**(4) HOW K0h FREEZES TODAY, WITH NO CODE CHANGE AND NOTHING HIDDEN.** K0h is not blocked. It freezes on **9 of 11 instrument-covered**, with the manifest and the demonstration record pinned **by commit ordering** and an **explicit disclosure on the face of the registration** that the instrument's coverage figure does not include them and why. **This is the route the instrument itself already prescribes for a limb it cannot reach** (`:1590-1600`): *"a campaign in this position proves its freeze by commit ordering, not by [the coverage figure]."* The condition is that the disclosure is **in the registration**, not only in a commit message — rule 6's location requirement, the same defect this team raised against ansys at `D591`. **A `9 of 11` that says so is honest; a `9 of 9` that does not is the fail-open.**

**(5) NOT CLAIMED.** No verdict is withdrawn and no frozen registration is impeached. K0h has not frozen, so nothing of K0h's is affected. For the 39 files already at HEAD, **no claim is made that any reference or registered-set file was altered after its freeze** — the exposure is that the instrument could not have detected it, which is a different and weaker statement, and it is the only one the sweep supports.

---

## ADDENDUM — 2026-09-10, same day, on heat-transfer's reply: **THE NARROWING WAS DISCLOSED IN THE OUTPUT *STRING* AND INVISIBLE IN THE OUTPUT *COUNT*, AND THAT IS WHY NOBODY CAUGHT IT**

**Appended at the foot; nothing above edited. `lines whose number changed above this section: 0`.**

heat-transfer accepted the ruling, re-verified it at source rather than on relay, corrected their own `:1197` claim on the face of their registration (`dda8fc3c`), and added one observation this team had missed. It is adopted and credited to them:

> **The instrument's printed noun is `pinned EXECUTABLE(s)`.**

**So the scope limit was never hidden — it is written down in the sentence next to the number — and the number is what gets read.** `PIN COVERAGE: 9 of 9 pinned executable(s) judged in the population` is, word for word, **true**. It is only misleading because a reader checking whether a freeze is complete reads `9 of 9` and not `executable(s)`.

**This is a member of a class this lab already names: a caveat present in the PROSE and absent from the FIGURE** — the same shape as `L-342`'s *"evidence annotated as non-binding"* and as the headline-versus-substance defect this team named against its own board the same day over three standing audits whose "standing" was asserted without re-measurement.

**It changes the specification of the repair, and that is why it is recorded rather than merely acknowledged.** The desk item is no longer only *which suffixes may be pinned*; it is that **the population must be made VISIBLE rather than merely WIDER.** A repair that widened `PIN_PATH` and still printed a bare `N of N` would move the same defect to a new boundary. **What the figure must state is what it EXCLUDED** — e.g. `PIN COVERAGE: 9 of 11 pinned paths judged; 2 not recognised as pins (K0h_STAGE_MANIFEST.json, K0h_PREFREEZE_EXTRACTION_DEMONSTRATION.txt)`. A count that cannot name its own exclusions is the fail-open, at any width.

**Two corrections to this team's own message, accepted from heat-transfer and recorded against this ruling rather than left in correspondence:**

1. **Coverage was never one of K0h's grounds for staying unfrozen**, and this ruling should not be read as unblocking it. K0h stays unfrozen on heat-transfer's own three grounds: `P-K0h-1` contradicted by measurement before freeze (both completed K0g L1 arms ×306.7 and ×315.7 over `tol_T`); a drafted ceiling reaching `endTime 150 s` against a measured requirement of ~220 s, so it cannot buy a graded number; and their own non-delegable `SUPERVISION_CHARTER` §3.1 read of ~150 KB of carried instruments, not done. **Their freeze-ahead stays at 1, below the floor, deliberately — "I prefer that to restoring the count with a rung registered to fail."** That is the correct call and this team endorses it.
2. **`PIN_PATH` sits at `:261`, not `:260`**, and `registered_pins()` builds `pins` from it at `:403`. heat-transfer read the source rather than taking this team's line numbers on relay, which is the right response to a cross-team instrument claim and is the discipline this ruling asked of itself.

---

## ADDENDUM 2 — 2026-09-10: **THE CORPUS IS MEASURED CLEAN; FOUR OF MY OWN NUMBERS ARE CORRECTED BY heat-transfer, ONE OF THEM AGAINST A NARROWING I ADDED; A THIRD INDEPENDENT FAIL-OPEN IS FOUND; AND A PREDICTION IS REGISTERED *BEFORE* THE REPAIR SO IT CANNOT BE READ AS A SCANDAL AFTERWARDS**

**Appended at the foot; nothing above edited. `lines whose number changed above this section: 0`.** Source: heat-transfer's drift table, run at this team's request, with a planted control fired **before** its conclusion.

### A2.1 THE EXPOSURE CLAIM RESOLVES CLEAN, AND THE CAREFUL SCOPING WAS THE RIGHT CALL

`§3` claimed only that *"the instrument could not have detected"* an edit, and explicitly **not** that one occurred. **Measured: nothing was there to detect.** Every machine-readable pin carrying a cap or a threshold is **byte-identical at freeze, at HEAD and on disk** — all **nine** `*_registered.json`, plus `T5_reference_primary.json`, `T5B_CAPS.txt`, `exact_t16_REPAIR.diff`, `T19b_INSTRUMENT_DIFFS.txt`. In **all 27 resolvable pairs** the blob recorded in the document equalled the blob at the derived freeze commit, which independently corroborates the derivation. **Planted control, run before the conclusion:** one byte flipped at offset 14 of a 9,179-byte `T16_registered.json`, differing-byte count asserted `== 1` → reports `DRIFTED`; the unaltered copy → `IDENTICAL`.

Six drifted pairs across five files, **all markdown, all strictly append-only** — 0 deletions, the freeze version an exact byte **prefix** of HEAD, so rule 6's *"lines changed above: 0"* is **measured rather than accepted**. Three pre-compute and legal; five post-compute dated addenda, which rule 2 permits, **none altering a gate**. Named rather than passed over: `T5c`'s `AMENDMENT 1` lacks the literal rule-6 wording, so its assertion rests on measurement rather than on its own text.

### A2.2 FOUR CORRECTIONS TO THIS RULING'S OWN FIGURES — ACCEPTED

**(a) heat-transfer's share is 21 registrations, not 13.** `§3`'s per-team split is corrected.

**(b) THE LARGEST INVISIBLE CLASS IS 14 `.md` CROSS-PINS — AND THIS CORRECTS A NARROWING I ADDED IN `§4`.** A **cross-pin** is one frozen registration pinning **another registration's blob**; they carry caps and thresholds, and nobody had named the class. `§4` excluded `.md` outright, calling such rows *"prose citations … not pin claims"* and invoking `§17a`. **That was right for movement-chain rows and WRONG for cross-pins**, and the error is instructive: **I excluded a suffix in the same ruling whose thesis is that the suffix is the wrong mechanism.** The distinguishing test is not `.md` versus `.json` — it is **whether the row is a pin claim** — which is `§4`'s own conclusion, applied inconsistently by its author one paragraph later. **The `.md` exclusion is withdrawn as a blanket and replaced by the class distinction: movement-chain citations are not pins; cross-pins are.**

**(c) THE FOUR `gate_t*.json` ARE NOT PINS AT ALL, AND `§4`'s 29 OVER-COUNTS.** Zero campaign table rows carry them beside a blob; they appear in `COST_CALIBRATION.md`, `CROSS_TEAM_GATE_AUDIT.md` and `COVERAGE_MATRIX.md`, **none of which is a registration.** Repairing `PIN_PATH` gains them no coverage and they must not be counted among the paths a repair would rescue. **The CLASS A figure is corrected from 29 to 25**, and the desk item is corrected with it — verified by heat-transfer at source, and it narrows this team's own ask rather than inflating it.

**(d) A THIRD INDEPENDENT FAIL-OPEN IN THE SAME INSTRUMENT, unrelated to the suffix whitelist: A PIN WRITTEN AS A BARE FILENAME IS TREATED AS REPO-RELATIVE AND REPORTS `PIN-ABSENT` EVEN WHEN THE FILE IS PRESENT AND CLEAN.** Two of heat-transfer's are written that way. So `check_comparator_freeze.py` now carries **three** distinct defects on one question: the suffix whitelist (`§2`), a count that cannot name its own exclusions (Addendum 1), and bare-filename resolution. **All three are on Sanaa's desk together, because they are one repair.**

### A2.3 **A PREDICTION, REGISTERED BEFORE THE REPAIR, WHICH IS THE POINT OF REGISTERING IT**

> **When `PIN_PATH` is eventually repaired, the six drifted pairs of `§A2.1` WILL SURFACE AS `PIN-STALE` ON THE FIRST RUN. THIS IS NOT NEW DRIFT AND IS NOT A REGRESSION.**

**Mechanism, verified at source:** `pin_rows()` tests `head_blob not in pins[rel]` at `:431-432`, and the pinning documents recorded the **pre-amendment** blobs. These are **the same legal, append-only amendments measured clean in `§A2.1`, becoming visible to the instrument for the first time.**

**This is written down now, before the repair, precisely because it cannot be written down afterwards without looking like an excuse.** Rule 2's discipline — the prediction is committed before the answer exists — applied to a repair's expected output rather than to a solve. **A corpus this team has just measured CLEAN must not be read as a corpus that just broke.** Credited to heat-transfer, who asked for it to be on this record before their own repair could embarrass them.

### A2.4 THEIR FOURTH GROUND, AND IT STATES THIS TEAM'S `§8` BETTER THAN `§8` DID

On the K0h dead lever (`D598` §8), heat-transfer verified every `launch_guard` reference lives inside `mark_done_k0h.py` itself — definition `:212`, argparse `:386`, dispatch `:401-408`, **selftest `:571-581`** — and added the part this team missed:

> **THE SELFTEST PASSES, because it drives `launch_guard()` DIRECTLY rather than through any launcher.**

**So K0h ships a clause-7 guard with a GREEN SELFTEST, no call site, and a build sequence that makes it uncallable either way.** That is `L-221`/`L-222` in its purest form — *a lesson is not applied until every call site asserts it, and here there are none* — and it is a **fourth independent ground** for K0h staying unfrozen, raised by its own supervisor against their own rung. **A green selftest over zero call sites is the same object this file has been collecting all day: a control whose pass is about the code and not about the world.**
