# RC2 — THE KAANDORP DIVERGENCE-FLAG REPAIR, AND THE RE-GRADE FROM PRESERVED ARTIFACTS

> **THIS COMMIT IS NOT THE FREEZE.** This document is landed to preserve it and
> to make it reviewable; it is **NOT YET FROZEN** and **NOTHING MAY RUN AGAINST
> IT**. Standing rule 2 fixes the grading path **at the pre-registration
> commit**, and this item's instrument does not exist yet — so the freeze is the
> later commit that carries **this document AND its instrument together**, and
> that commit's sha is the one an entry's `prereg_commit` must cite. Any run
> before it is unregistered and its output is **NOT A RESULT**.
> — closure-supervisor, 2026-08-28


**Rung:** `RC2_kaandorp_divergence_repair`
**Team:** closure
**Class:** REPAIR-REGISTRATION (Sanaa's FREEZE-AHEAD amendment, 2026-08-28) — and
a **D548 instance**
**Status:** `prereg_commit: PENDING_SUPERVISOR_FREEZE`. The gates, thresholds, cap
and label below are drafted and are **not yet closed**; the freeze is the
supervisor's act, performed personally under `SUPERVISION_CHARTER.md` §3 check 4,
and it is a commit whose message carries the sha256 of this document and of both
instruments. **Nothing has been staged into the run root, no queue entry has been
filed, and no compute has been spent.**
**Drafted:** 2026-08-28, by a closure lane on the closure supervisor's dispatch.

**Why this item exists.** Sanaa's 2026-08-28 amendment makes repair-registrations
queue-eligible work, and her re-grade order — *"Enumerate every verdict, docket
row, or finding that cited any of the [defective] readers; re-grade each from
preserved artifacts through the repaired instrument; report which verdicts
moved"* — was given to dafoam for its seven readers. **RC2 is closure doing the
same thing for its own one.** Closure has exactly one such reader still on disk in
its defective form, and its repair has been listed as **"Queued, not done"** since
before G1 was written.

---

## 1. The defect, re-derived at drafting, not quoted from the board

### 1.1 The site

`cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/run_lane.py`, **350
lines**, sha256 `454e37f426296581c1eee7336a284334a3466ce952498928c9ccf31b744046d0`,
**disk byte-identical to `HEAD`** (verified by hashing the file and
`git show HEAD:<path>` in one invocation). Inside `parse_log` (:165):

    175	        if "Floating point exception" in line or "FOAM FATAL" in line:
    176	            diverged = True
    177	    out = dict(iterations=it, diverged=diverged, ended="End" in ...

The token `diverged` occurs at **exactly three lines — 168, 176, 177** — measured
by reading the file, not by `grep`.

### 1.2 The mechanism

OpenFOAM writes, at line 18 of every log this box produces:

    trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).

Line 175 tests an **unanchored substring**, so it matches that safety notice on the
first line of output of **every** run, healthy or not. `diverged` is a constant
`True`, not a measurement. This is D548's shape and L-396's lesson.

### 1.3 The consequence, MEASURED at drafting on the preserved artifacts

`/home/ubuntu/closure-data/aposteriori/kaandorp/results.json` holds **19 run
entries**, of which **16 carry a `diverged` key. All 16 read `diverged: true`.
All 16 also read `ended: true`.** Not one of the 16 preserved `log.run` files
contains any genuine fatal signature — `--> FOAM FATAL ERROR`,
`--> FOAM FATAL IO ERROR`, `FOAM exiting`, `Foam::sig*::sigHandler`,
`Foam::error::printStack`, a line-initial `Floating point exception` or
`Segmentation fault` — and **all 16 carry the `trapFpe` banner**. The flag is
false in fact on every row it appears on.

That is what `RESULTS.md:572` already discloses as limitation 3 — *"the
`diverged=True` banner artifact, confirmed by direct count. `results.json` carries
`diverged: true` on every scored row"* — with the repair listed at `RESULTS.md:899`
as **"Queued, not done: the `run_lane.py:175` divergence-flag repair"**. **This
registration is that item, and it is now also the closure instance of Sanaa's
re-grade order.**

### 1.4 A prior lane already analysed this and declined to land it — and that record binds this one

`cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/run_lane_banner_test_PROPOSED_NOTE.md`
(2026-08-25) and its companion `run_lane_banner_test_PROPOSED.diff` **both exist on
disk**. That lane wrote the one-line fix, argued it through, and **did not land
it**, on the ground that the repair *"changes what a registered gate trigger reads
on a closed campaign, in the direction that removes a failure flag."*

**RC2 does not overturn that call; it satisfies it.** The prior lane's objection
was to editing the frozen file. RC2 edits nothing: it builds a **successor**, and
it adds the half the prior lane did not attempt — the **re-grade**, which is what
turns a disarmed flag from a silent change into a recorded one.

**And RC2 supersedes the prior diff's control, for a reason that did not exist on
2026-08-25.** That note's §6 item 2 describes its planted control as *"Both
fixtures are string literals"*. Under Sanaa's 2026-08-28 clause — *"A control
defined in terms of the thing it controls is not a control … a control that writes
a schema the producer never emits, tests nothing and certifies blindness"* — a
string-literal fixture is **no longer sufficient**. RC2's control runs on **real
producer-written logs, named individually in §5.2**, and the prior diff is
therefore not landed in its own shape.

### 1.5 Freeze status, established by measurement

**`run_lane.py` is POST-COMPUTE and its gates are closed.** `git log` on the file
returns **two** commits: `0ebc9d53` (the a-posteriori results commit) and
`074f60da` (a follow-up). The second landed **after** the 2026-08-21 duct rows
ran, so a post-compute edit already has precedent on the record — and that
precedent is not a licence. The file carries **no version line and no amendment
record**; the pre-registration **does not name it** as the grading path and fixes
no sha for it; D492 states outright that no grading script is registered. But
`RESULTS.md:869` calls it *"a frozen mid-campaign instrument"* in a committed
record with a rule-6 assertion at its foot.

**RC2's ruling on that mixed picture, registered here before any compute:** the
file is treated as **frozen post-compute**. Standing rules 2 and 6 apply in full.
**`run_lane.py` IS NOT EDITED BY THIS ITEM, at any line, for any reason.** The
repair is a **successor module, frozen by sha at the RC2 pre-registration commit**.

---

## 2. What RC2 is, as ONE capped item

Two halves, one cap, one headline verdict.

**HALF A — the successor reader**, `rc2_divergence.py`, carrying a **two-direction
planted control on REAL logs** (§5.2), built from the lab's verified precedents:

* the FOAM-ERROR channel of `sdk/chief_engineer/mesh_certificate.py`'s `_FATAL`
  (`-->\s*FOAM FATAL(?:\s+IO)?\s+ERROR|FOAM exiting`), and
* the **line-anchored** FPE channel of `sdk/chief_engineer/head_engineer.py:188`
  (`Foam::sigFpe::sigHandler|^Floating point exception` under `re.MULTILINE`),

which is the same pair `grade_g2.py`'s repaired `FATAL_RE` (`:129`) and
`grade_g1b.py`'s `RE_FATAL` (`:299`) were built from. **Anchoring is what defeats
the banner:** the banner's phrase is preceded by `trapFpe: ` and so never begins
its line. Neither `trapFpe:` nor `trapping enabled` appears in any channel.

**HALF B — the re-grade from preserved artifacts**, `regrade_rc2.py`: enumerate
every row, verdict, docket item and finding that cited the flag; re-read the
preserved logs through **both** readers; and **report which verdicts moved.**

**Half B is the half that matters.** A repaired reader with no re-grade leaves
every number it already produced standing on the defect.

---

## 3. Substrate — the preserved artifacts, and THEY EXIST: checked, not assumed

### 3.1 The run root

`/home/ubuntu/closure-data/aposteriori/kaandorp/` **exists**, 33 entries, and holds:

| artifact | state at drafting |
|---|---|
| `results.json` | **PRESENT**, 21,975 bytes, mtime 2026-08-23 23:17 |
| `results_PRE_RELAUNCH_2026-08-23.json` | **PRESENT**, 11,331 bytes, mtime 2026-08-21 19:36 |
| `table.json` (written by `summarise.py`) | **PRESENT**, 6,843 bytes |
| `frozen_R_{AR_1_Ret_360,CBFS13700,PHLL10595}.json` | **PRESENT** |
| the 16 scored case directories, each with `log.run` | **ALL 16 PRESENT** |

### 3.2 The re-grade corpus, measured file by file

**All 16 `log.run` files that produced a `diverged` cell in `results.json` exist on
disk. Zero are missing. Total 268.0 MiB (0.2617 GiB).** Every one was opened at
drafting and read through the repaired pattern:

| case | `results.json` `diverged` | `ended` | `trapFpe` banner present | genuine fatal signature | log bytes |
|---|---|---|---|---|---|
| `AR_1_Ret_360__NULL` | **true** | true | yes | **none** | 30,278,532 |
| `AR_1_Ret_360__TRUTH` | **true** | true | yes | **none** | 538,993 |
| `AR_1_Ret_360__MEANB` | **true** | true | yes | **none** | 5,311,074 |
| `AR_1_Ret_360__ML0` | **true** | true | yes | **none** | 30,608,267 |
| `AR_1_Ret_360__ML1` | **true** | true | yes | **none** | 2,534,800 |
| `AR_1_Ret_360__ML2` | **true** | true | yes | **none** | 2,921,117 |
| `AR_1_Ret_360__MEANB64` | **true** | true | yes | **none** | 1,545,600 |
| `AR_3_Ret_360__NULL` | **true** | true | yes | **none** | 30,331,929 |
| `AR_3_Ret_360__TRUTH` | **true** | true | yes | **none** | 3,115,834 |
| `AR_3_Ret_360__MEANB` | **true** | true | yes | **none** | 32,691,552 |
| `CBFS13700__NULL` | **true** | true | yes | **none** | 897,986 |
| `CBFS13700__TRUTH` | **true** | true | yes | **none** | 30,401,290 |
| `CBFS13700__MEANB` | **true** | true | yes | **none** | 27,481,377 |
| `CBFS13700__ML0` | **true** | true | yes | **none** | 27,429,559 |
| `CBFS13700__ML1` | **true** | true | yes | **none** | 27,444,897 |
| `CBFS13700__ML2` | **true** | true | yes | **none** | 27,508,083 |

**16 of 16 flag cells would flip from `true` to `false`** under the repaired
reader. That is the drafting-time reading of the artifacts; it is **the registered
expectation** (§4.4), not the result, because the result must come from the frozen
successor through the frozen re-grade path.

### 3.3 A SECOND artifact carrying the flag, found at drafting and registered

`results_PRE_RELAUNCH_2026-08-23.json` carries **10 further rows with
`diverged: true`** — `AR_1_Ret_360__{NULL,TRUTH,MEANB,ML0,ML1,ML2,MEANB64}` and
`AR_3_Ret_360__{NULL,TRUTH,MEANB}`. All ten are a **subset of the 16 by name**,
and all ten case directories carry an mtime of **2026-08-21**, i.e. **before** the
2026-08-23 relaunch that produced the current file.

**The honest limit, registered rather than glossed:** the `log.run` on disk for
each of those ten is the log of the run that produced the **current** row of that
name. Whether it is byte-identical to the log that produced the **PRE_RELAUNCH**
row **cannot be established** — no hash of the original was preserved. The
2026-08-21 directory mtimes are evidence and are not proof. **RC2 therefore
re-grades the 16 current cells as a re-grade, and reports the 10 PRE_RELAUNCH
cells as `NOT A RESULT — artifact provenance unestablished`, naming all ten.** A
re-grade with no provably matching artifact is not a re-grade.

**Total flag-cell population: 26. Re-gradable: 16. Not re-gradable: 10, named.**

### 3.4 `table.json` carries NO flag cell, and that is load-bearing

Measured: `table.json` contains **zero** `diverged` keys. `summarise.py:22`'s
`state()` recomputes the convergence state independently, with the trap documented
in its own comment at `:29-31`. **The cross-lane table is therefore unaffected by
this repair in either direction** — which is a fact about the artifact, checked
here, not an inference from the code.

---

## 4. The re-grade: what is enumerated, and what "moved" means

### 4.1 The enumeration rule, frozen here

`regrade_rc2.py` walks **every `.md` and `.json` file in the repository outside
`.git`** and records, with file and line, every citation of:

* the literal `run_lane.py:175` (and `:176`, `:168`, `:177`);
* the `diverged` key in a Kaandorp context;
* the phrase `DIVERGED` in a Kaandorp context.

The rule is fixed here so the enumeration cannot be narrowed after the answer is
seen. **Its output is written to `CITATION_MANIFEST.json` in the run root and every
row of the re-grade table cites it.**

**Measured at drafting, the enumeration returns 18 repository files** carrying a
divergence token in a Kaandorp context, the densest being `docs/LAB_STATE.md`
(20 tokens), `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_PREREGISTRATION.md`
(18), `docs/LESSONS.md` (18), `run_lane_banner_test_PROPOSED_NOTE.md` (14),
`docs/dafoam/PRIOR_WORK_INVENTORY.md` (13), `docs/NUMERICS_KNOWLEDGE.md` (11),
`Kaandorp2020_TBRF/aposteriori/RESULTS.md` (7), `docs/COST_CALIBRATION.md` (6),
`docs/DOCKET.md` (6). **That is a drafting-time reading of a moving tree and it is
the expectation, not the gate.**

### 4.2 The consumer audit, and the one non-obvious result already measured

A code-level sweep for `["diverged"]`, `.get("diverged")` and `.diverged` across
**every `.py` file in the repository** returns exactly **two sites**, both in
`R4_sparta_build/score_aposteriori.py` (`:195`, `:196`), where
`entry.get("diverged")` gates whether `eps_U` is computed at all.

**Those two sites do NOT read Kaandorp's `results.json`.** They read the `**lf`
merge of that module's **own** `log_facts` (`:55`), whose FPE test is the correct
narrow `Foam::sigFpe::sigHandler` (`:70`) with a five-line comment describing this
exact trap. **R4 is not contaminated by this defect**, and the re-grade says so
from a reading rather than assuming isolation.

**Inside `run_lane.py` itself, nothing reads the flag.** The three occurrences are
an initialiser (:168), an assignment (:176) and a pack into the output dict (:177).
No branch, no gate, no skipped solve. Every scored metric is produced by `score()`,
which never receives `parse_log`'s output.

### 4.3 What "moved" means, defined before the answer

| category | definition |
|---|---|
| **FLAG MOVED** | the `diverged` cell's value differs between the frozen reader and the successor, on the same preserved log |
| **VERDICT MOVED** | a `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` on the committed record changes when re-derived with the repaired flag, every other input held byte-fixed |
| **TRIGGER DISARMED** | a registered gate trigger that the flag armed is no longer armed, *even though the verdict does not change*, because another registered leg of the same clause remains armed |

**The third category is registered deliberately.** The Kaandorp pre-registration
arms divergence as a `GATE FAIL` trigger twice — `PREREGISTRATION.md:230-231`
(*"**GATE FAIL** iff `mean(U_rms | ML) ≥` the gate, or any ML seed **diverges** or
fails to converge"*) and `:291-294` (*"**Divergence is a result, not an error.** A
configuration whose residuals rise monotonically, or that ends on a floating-point
exception, is recorded … and graded **GATE FAIL**"*). A repair that disarms one leg
of a two-leg clause without changing the verdict is **still a change to a
registered trigger after first compute**, and burying it inside "no verdict moved"
is exactly the shape of an evidence-annotated-as-non-binding failure. It is
reported as its own category.

### 4.4 REGISTERED EXPECTATION, on record before the run

| | expectation | basis |
|---|---|---|
| **FLAG MOVED** | **16 of 16** | §3.2, measured at drafting |
| **VERDICT MOVED** | **0** | the flag steers no branch (§4.2); `table.json` does not carry it (§3.4); R4's consumer reads a different reader (§4.2); and the defect's direction is a **false positive**, which can only add a spurious GATE FAIL, never remove a real one |
| **TRIGGER DISARMED** | **≥ 1, on H1** | `RESULTS.md:681` records H1's `GATE FAIL` as resting *"also on the 'fails to converge' clause — all three seeds"*. The `converged` field is computed independently from the residual history at `run_lane.py:183-196` and reads **false on 15 of the 16 rows** (the exception is `AR_3_Ret_360__TRUTH`). So the **"fails to converge" leg stays armed** while the **"diverges" leg disarms** |

**These are predictions and they gate nothing.** They are registered so that being
wrong is visible, and so that a "no verdict moved" outcome is a **confirmed
prediction** rather than a conclusion reached after looking.

---

## 5. Gate, threshold, cap and label

### 5.1 The ordering

1. If the successor's two-direction planted control (§5.2) does not fire in **both**
   directions on real logs, `rc2_divergence.py` **refuses (`sys.exit(2)`)** and
   **no re-grade runs at all**. Under standing rule 3 and Sanaa's birth
   requirement, an unproven reader grades nothing.
2. If any of the 16 preserved logs is absent, unreadable, or has an `mtime` newer
   than `results.json`, that row is **`NOT A RESULT`** and is named.
3. Only rows surviving 1 and 2 are re-graded.

### 5.2 THE BIRTH-REQUIREMENT GATE ON THE SUCCESSOR — on REAL logs, both directions

**Not synthetic strings.** Both directions are demonstrated on logs written by the
real producer, each named here, each verified present and each verified to carry
the stated signature at drafting:

**POSITIVE DIRECTION — the successor MUST read fatal on all six, and the three
distinct signature classes must all be represented:**

| real log | signature verified at drafting | bytes | clean `End` |
|---|---|---|---|
| `/home/ubuntu/closure-data/hump_gate/G0a_shipped/log.run` | `--> FOAM FATAL IO ERROR` | 13,527 | no |
| `/home/ubuntu/certonomous-runs/adjwall/HUMP51k/log.run` | `--> FOAM FATAL ERROR` | 1,548,129 | no |
| `/home/ubuntu/certonomous-runs/adjwall/N100k/log.run` | `--> FOAM FATAL ERROR` | 24,360 | no |
| `/home/ubuntu/certonomous-runs/adjwall/A1_4032/log.run` | `--> FOAM FATAL ERROR` | 46,744 | **yes** |
| `/home/ubuntu/Certonomous/verification/runs/DPW8_V2_runs/run_L4_diagA_relax/log.simpleFoam` | `Foam::sigFpe::sigHandler` | 304,371 | no |
| `/home/ubuntu/certonomous-runs/S1-cbfs-inversion/log.calib` | `--> FOAM FATAL ERROR` | 3,547,690 | **yes** |

**NEGATIVE DIRECTION — the successor MUST read NOT-fatal on all 16 of §3.2's
preserved Kaandorp logs**, every one of which carries the `trapFpe` banner and a
clean `End`. **These are the very artifacts the frozen reader gets wrong**, written
by the very producer whose output this reader grades.

**AND THE MIRROR, which is what makes it a control rather than a demonstration:**
the **frozen** `run_lane.py:175` predicate — reinstated for exactly one call, on
the `_blind_fatal` pattern `grade_g2.py:1320` already establishes — must
**disagree**, reading fatal on all 16. If it does not, the corpus is not the corpus
the defect lives on and the control **refuses**.

**Why this direction assignment and no other.** **The positive direction cannot be
demonstrated on this case's own artifacts:** not one of the 16 Kaandorp logs
contains a genuine fatal (§3.2), so a control confined to the case would prove only
that the reader can say "no". The positive corpus must come from elsewhere on this
box, and it is named file by file above rather than described.

`--selftest` runs both directions and exits 0 only if every one of the 22 named
files reads as registered. It must pass under `python3` **and** `python3 -O`, with
`__pycache__` cleared before each run.

### 5.3 The re-grade gate

| condition | verdict |
|---|---|
| control fires both directions; all 16 logs present and older than `results.json`; the re-grade table is written with every row citing its artifact | **`PASS`** |
| control fires; ≥1 row's artifact absent or provenance unestablished | **`PASS` on the graded rows, `NOT A RESULT` on the named rows** |
| the two-direction control does not fire | **`NOT A RESULT`** for the whole item, and the successor **may not grade anything** |
| the 10 PRE_RELAUNCH cells | **`NOT A RESULT — artifact provenance unestablished`**, registered in advance (§3.3) |

**RUNG HEADLINE.** RC2's headline is the re-grade's: `PASS` when every re-gradable
row has been re-graded from a preserved artifact through the controlled successor
and the movement table is written. **`PASS` here means "the re-grade was performed
and is defensible", NOT "nothing was wrong"** — 16 flag cells are expected to move
and that is the finding, not a failure.

Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING`,
passed through a checker that **refuses** on a synonym, a hedge or a lower-case
variant before printing.

### 5.4 WHAT RC2 MAY NOT DO — registered as a prohibition, not a preference

* **It may not edit `run_lane.py`.** Not one line, not a comment. Rules 2 and 6.
* **It may not rewrite `results.json` or `results_PRE_RELAUNCH_2026-08-23.json`.**
  The re-grade writes a **new** file, `REGRADE_RC2.json`, in the RC2 run root. The
  preserved artifacts are opened **read-only**.
* **It may not re-run the lane.** Re-running to regenerate `results.json` with the
  repaired flag would be a re-solve of a closed campaign, is not proposed, and is
  registered here as out of scope.
* **It may not change a committed verdict.** If a verdict moves, RC2 **reports the
  movement**; the ruling is the closure supervisor's and, per Sanaa's routing,
  verification rules on each moved verdict. **A lane does not move a verdict.**
* **It may not edit `RESULTS.md` above a new dated addendum.** Any record change is
  an appended, dated addendum carrying the assertion `lines whose number changed
  above this section: 0` — and even that is the supervisor's act, not this item's.

### 5.5 The registered falsifier

RC2 is falsified as an instrument if the successor reads fatal on any of the 16
banner-only Kaandorp logs, or NOT-fatal on any of the six named real fatals. Either
is a `NOT A RESULT` for the whole item and the successor is withdrawn, not tuned.

---

## 6. Controls

### 6.1 The two-direction planted control on real logs — §5.2, and it is the gate

Wired into **both** paths: the re-grade path, before any row is read, and
`--selftest`. It **refuses (`sys.exit(2)`)**, never warns.

### 6.2 THE BLIND CONTROL

The frozen `run_lane.py:175` predicate is reinstated for exactly one call and the
control must show it reading fatal on all 16 banner-only logs. **The control is
therefore shown firing on precisely the defect it was written for, on the real
artifacts that carry it** — not on a fixture, and not on a schema this instrument
wrote.

### 6.3 THE ARTIFACT-PROVENANCE CONTROL

Every re-graded row records its log's absolute path, byte size, `mtime_ns` and
sha256 into `REGRADE_RC2.json`, and the re-grade **refuses** a row whose log
`mtime` is **newer than `results.json`'s** — because a log written after the
results file did not produce the row being re-graded. This is the age guard of
standing rule 4 applied to a re-grade.

### 6.4 THE READ-ONLY CONTROL

Every preserved artifact is opened `"r"` and never `"w"`, `"a"` or `"r+"`. Before
exit the instrument re-`stat`s all 16 logs plus `results.json` and
`results_PRE_RELAUNCH_2026-08-23.json` and **refuses** if any `mtime_ns` or size
changed during the run. **A re-grade that modifies the artifact it re-grades has
destroyed its own evidence.**

### 6.5 L-332 — no refusal may be an `assert`

Every refusal in both instruments is a `raise` or a `sys.exit(2)`. Each parses its
**own** AST and refuses if a single `ast.Assert` node exists, with the counter first
shown able to count a **planted** assert. `--selftest` exits 0 under `python3` and
`python3 -O`, `__pycache__` cleared before each.

### 6.6 L-342 — physics against infrastructure

A missing timing record, a missing MaxRSS reading or an unreachable citation file is
an `INFRASTRUCTURE DEFECT`, printed and carried, and **voids no re-graded row**. A
missing or unprovable **artifact** is a PHYSICS refusal for its row and makes that
row `NOT A RESULT`.

---

## 7. Cost. Measured basis, and the box cannot read its own billing

**Rates, MEASURED on this box 2026-08-28** (the same two measurements RC1 §7
registers, taken by this lane): whole-text regex readers **46.5 MiB/s** (400-file
seed-7 sample, 17.95 s / 0.815 GiB); Python line-loop readers **10.9 MiB/s**
(60-file seed-11 sample through `grade_m1.parse_log` itself, 12.53 s / 0.133 GiB).
`run_lane.parse_log` is a line loop; the successor is whole-text regex.

| item | bytes | rate | wall s |
|---|---|---|---|
| 16 preserved logs through the **frozen** `run_lane.parse_log` (the before column) | 0.2617 GiB | 10.9 | **25** |
| 16 preserved logs through the **successor** (the after column) | 0.2617 GiB | 46.5 | **6** |
| the blind control — 16 logs through the reinstated frozen predicate | 0.2617 GiB | 10.9 | **25** |
| positive direction — the six named real logs | 0.0051 GiB | 46.5 | **1** |
| sha256 of the 16 logs (provenance control §6.3) | 0.2617 GiB | ~500 MiB/s | **1** |
| citation enumeration — every `.md`/`.json` outside `.git` | | | **15** |
| `--selftest` ×2 (`python3`, `python3 -O`), report and JSON assembly, startup | | | **60** |
| **solver compute** | | | **0 — RC2 launches no solver and re-runs nothing** |

    total wall ≈ 133 s at ranks = 1  ->  2.2 core-min

**REGISTERED ESTIMATE: 4.0 core-minutes.**
Derived: 0.0667 core-h × $0.0513/core-h = **$0.0034 — derived at the owner-stated
rate, reported-by-owner, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5).

**REGISTERED CAP: 12.0 core-minutes**, enforced as a wall-clock `timeout 720`
around the instrument.
Derived: 0.200 core-h × $0.0513 = **$0.0103 — derived, NOT MEASURED.**

**The cap's 3× ratio is justified rather than rounded.** The corpus is dominated by
six logs above 27 MiB each (the largest 32.7 MiB), read three times over; the
`10.9 MiB/s` line-loop rate was measured under whatever contention the box carried
with G2 mid-compute; and the citation walk crosses a repository whose size this
lane did not bound. **An overrun stops the run; it does not get a new budget**
(standing rule 12).

Both figures are far under $25 and inside the 2026-08-21 blanket. **A blanket is
not a per-item read** (standing rule 9); the cost is registered regardless.

**Estimate-versus-actual calibration is owed at completion** (standing rule 12) and
lands as a row in `docs/COST_CALIBRATION.md`, with waste named separately and never
absorbed into the ratio. **A completion report without it is incomplete.**

---

## 8. `memory_floor_gb` — an allowance, and it says so

RC2 holds **one log's text at a time**; the largest is **32,691,552 bytes
(31.2 MiB)**, measured. Add the citation manifest and the re-grade table, both well
under 10 MiB of JSON, and the interpreter.

**Registered: `memory_floor_gb = 0.5`, an ALLOWANCE** — roughly 16× the largest
single-file read, **explicitly not a measurement**, since this lane did not run the
instrument. The instrument wraps itself in `/usr/bin/time -v` and records MaxRSS,
converting the allowance into a reading for the next pre-registration. Its absence
is an INFRASTRUCTURE defect, not a refusal.

---

## 9. Queue entry

`QUEUE_ENTRY_DRAFT.json` sits **beside this document** and is **not** in the drop
path `verification/queue/closure/`. Two independent things stop it launching:

1. It is not in a drop path.
2. `prereg_commit` is the literal string `PENDING_SUPERVISOR_FREEZE`, which fails
   the validator's full-sha schema check.

**`enqueued_by` states explicitly that `SUPERVISION_CHARTER.md` §3 check 4 has NOT
been performed.** It is the supervisor's own non-delegable act.

**`cwd` is the RUN ROOT `/home/ubuntu/closure-data/rc2/`, pre-created empty by the
supervisor at enqueue** — never the Kaandorp run root, which holds the artifacts
this item must not touch, and never the repository case directory.
**This lane verified at drafting that `/home/ubuntu/closure-data/rc2` does not
exist**, and did not create it.

---

## 10. What it cannot see

1. **It cannot see whether any of the 16 runs actually diverged in the physical
   sense.** The repaired reader answers one question — *did this solver die on a
   fatal signal or a FOAM error?* — and the answer on all 16 is expected to be no.
   **A run that stagnated, hit the 30,000-iteration cap, or converged to a wrong
   answer is not "divergence" to this reader and never was.** `results.json`'s
   `converged` field is a separate channel on a separate code path and RC2 does not
   grade it.
2. **It cannot re-grade the 10 PRE_RELAUNCH cells**, and says so by name (§3.3).
3. **It cannot prove the repaired reader is complete.** The corpus demonstration
   proves it sees the fatals **these 22 named logs contain**: three signature
   classes — `--> FOAM FATAL ERROR`, `--> FOAM FATAL IO ERROR` and
   `Foam::sigFpe::sigHandler`. `FOAM exiting` alone, `Foam::error::printStack`
   alone, a line-initial shell `Floating point exception` or `Segmentation fault`,
   a `sigSegv` death and an OOM kill that leaves no marker at all are **not
   demonstrated on real artifacts by this item**. RC1 registers that same gap for
   the whole comparator population; RC2 does not close it.
4. **It cannot see a citation outside `.md` and `.json`.** A verdict recorded in a
   `.txt`, a figure caption or a notebook is invisible to §4.1's rule.
5. **It cannot rule on a moved verdict.** If one moves, RC2 reports it. Sanaa
   routed the ruling to verification; the closure supervisor triages first.
6. **It cannot speak for the four dafoam D548 sites** (`so1a_grade.py:125`,
   `so1b_grade.py:133`, `so1c_grade.py:157`, `d12y_w3_stage_and_run.sh:566`) or for
   the `sdk/` helpers. Those are named in D548 for their owners.
7. **It cannot close D548.** D548's settling action is *"one shared, tested
   fatal-detection helper with a two-direction planted control, plus a check that
   no comparator ships an unanchored `Floating point exception` test."* `scripts/`
   and `sdk/` are outside closure's folder scope. **RC2 builds the fourth
   independent copy of a correct predicate, which is rule 14's exact shape,** and
   it says so rather than pretending otherwise. RC2 makes its successor
   **importable** so a fifth site has something to import; it cannot make the
   shared helper live where it belongs.
8. **It cannot see whether the repaired flag would have changed the CONDUCT of the
   campaign** — whether a lane seeing `diverged: false` would have run the
   registered `bScale ∈ {0.8, 0.5}` divergence ladder that `RESULTS.md` §2.5
   records as *not triggered and not run*. That is a counterfactual about a closed
   campaign, and RC2 does not attempt it.

---

## 11. The grading path is fixed at the freeze

The instruments are `rc2_divergence.py` and `regrade_rc2.py` **as they exist at the
pre-registration commit**, hashed against the committed blobs before any result is
believed (standing rule 2; `scripts/check_comparator_freeze.py`).

**A LIFECYCLE FACT THIS DOCUMENT MUST CARRY:** at drafting time **neither
instrument exists.** This lane was dispatched to build the registration, not to run
the item. Rule 2 requires the grading path fixed at the pre-registration commit, so
**the freeze commit must carry this document and both instruments**, and until they
are written the freeze cannot legally be taken. That is the supervisor's call and is
recorded here as an open condition.

**Before first compute, amendments are legal and must state the condition and how
it was checked** — for this rung, that `/home/ubuntu/closure-data/rc2/` **does not
exist** and holds 0 core-minutes, verified by this lane at drafting.

---

## 12. Files

| file | role | exists at drafting |
|---|---|---|
| `PREREGISTRATION.md` | this document | **yes** |
| `QUEUE_ENTRY_DRAFT.json` | the queue entry, unvalidatable until the freeze | **yes** |
| `rc2_divergence.py` | the successor reader + the two-direction real-log control + the blind control; importable by a fifth call site | **NO — see §11** |
| `regrade_rc2.py` | the re-grade: citation enumeration, provenance control, before/after table, movement classification, vocabulary checker | **NO — see §11** |
| `REGRADE_RC2.json`, `CITATION_MANIFEST.json` | run artifacts in the run root | no |
| `RESULTS.md` | the graded record, written after the run | no |

**Not RC2's files, and not edited by RC2:**
`Kaandorp2020_TBRF/aposteriori/run_lane.py` (frozen, §1.5),
`.../RESULTS.md`, `.../PREREGISTRATION.md`,
`.../run_lane_banner_test_PROPOSED.diff` and `..._NOTE.md` (the 2026-08-25 record,
kept as the record of that analysis, superseded on its control by §1.4 and not
deleted).

---

## 13. ANTI-GAMING REGISTER (`docs/standards/NONCONVERGENCE_STANDARD.md`)

*"Answer-changing choices are never selected by agreement with the reference."*
**No RC2 run exists. No re-grade has been performed by anyone.**

| choice | registered reason, which names no answer |
|---|---|
| **the repair is a SUCCESSOR, not an edit** | `run_lane.py` is post-compute (`0ebc9d53`, `074f60da`) and `RESULTS.md:869` calls it a frozen mid-campaign instrument; rules 2 and 6 admit no edit. Established by measurement (§1.5), not by preference. |
| **the successor's pattern is the lab's existing precedent pair** | `mesh_certificate.py`'s `_FATAL` and `head_engineer.py:188`'s line-anchored form are already verified correct in this lab and already reused by `grade_g1b.py` and `grade_g2.py`. **No new pattern was invented and none was selected by trying candidates against the 16 logs.** |
| **the control's positive corpus is six named real logs from OUTSIDE this case** | forced, not chosen: none of the case's own 16 logs contains a genuine fatal (§3.2), so a control confined to the case could only ever demonstrate the negative direction. |
| **the negative corpus is the case's own 16 logs** | they are the artifacts the defect actually got wrong, written by the very producer whose output the reader grades — Sanaa's "real production path" read literally. |
| **the blind control reinstates the FROZEN predicate** | it must be shown firing on the defect it was written for, or its silence is a blind spot rather than a reading. The `_blind_fatal` shape is `grade_g2.py:1320`'s, already exercised. |
| **`mtime(log) < mtime(results.json)` as the provenance clause** | a log written after the results file did not produce the row; this is standing rule 4's age guard read backwards, and it is arithmetic, not a tolerance. |
| **the 10 PRE_RELAUNCH cells declared NOT A RESULT in advance** | their provenance cannot be established and no hash was preserved. Declaring them before the run is what stops them being quietly folded into a "26 of 26" headline afterwards. |
| **TRIGGER DISARMED registered as a third category** | a verdict that does not move can still rest on a trigger that has been disarmed; collapsing that into "no verdict moved" is the evidence-annotated-as-non-binding failure this lab already has a lesson for. |
| **estimate 4.0 / cap 12.0 core-min** | both rates measured on this box through real subject code (§7); the 3× ratio is justified by three named risks. |

**Two disclosures that belong here rather than in a footnote.**

* **This lane read `results.json`, all 16 logs and the 2026-08-25 proposed note
  before registering the gates.** What that reading established is the *defect's
  direction* (a false positive), the *artifact inventory* and the *absence of any
  genuine fatal in the case corpus* — properties of instruments and artifacts, not
  of any verdict. It is written into §3 and §4 so a reader can judge it rather than
  take this paragraph's word for it. The §4.4 expectations are stated **as
  expectations** for exactly this reason.
* **The prediction that no verdict moves is registered BEFORE the re-grade, and it
  is registered as the outcome that would be least convenient to discover
  afterwards.** If it holds, RC2's product is a closed loop and a disarmed trigger
  on the record. If it fails, RC2's product is a moved verdict — and the whole
  point of registering the expectation first is that nobody can then say the
  re-grade was not worth running.
