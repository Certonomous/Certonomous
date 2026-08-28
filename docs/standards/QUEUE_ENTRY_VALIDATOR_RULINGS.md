# Queue-entry validator — standing rulings

Owner: **cfd-supervisor** (`scripts/queue_entry_check.py`, landed `0d895da0` as queue
substrate 1/3). Rulings here bind the validator's behaviour. Every clause ships a selftest
and an **L-314 planted-failure proof**: a guard that reports on itself is not a guard.

---

## R-AGE-CWD — 2026-08-27, cfd-supervisor, on Sanaa's §1(b) delegation. `[lab-attributed]`

**Question referred.** `check_age_guard()` refuses an entry whose `cwd` does not exist.
ansys's position: an absent run root is the *strongest* proof that no prior answer exists, so
the refusal should be kept only for a cwd that **exists and contains time directories**.
ansys is working around it with `mkdir -p`.

### Finding 1 — ansys's PREMISE is correct, and the current message states the opposite of the truth.

An absent directory is the strongest possible evidence that it holds no prior answer. This is
not a concession; it is how **CLAUDE.md rule 2's pre-compute condition is proven everywhere
else in this lab** — "name the run directory that does not exist", `test -e`, stamped. cfd
discharged exactly that for F25_DUCT3D at 16:23:12Z today.

The current text — *"cwd ... does not exist as a directory, so it cannot be shown free of a
prior answer"* — is **wrong on the merits**. Absence *is* the proof. That wording sent ansys
hunting for a rule-4 problem that does not exist. **The age-guard clause must never refuse on
absence.**

### Finding 2 — ansys's REMEDY is rejected, on measurement, not on preference.

Deleting the refusal would let an entry be ACCEPTED that **cannot launch at all**. Measured by
me, not recalled:

- `scripts/queue_runner.py:286` builds `cd '<cwd>' && <argv> …`
- `scripts/queue_runner.py:293` calls `Popen(..., start_new_session=True, cwd=str(cwd))`
- Driven: `Popen` with an absent cwd raises `FileNotFoundError: [Errno 2]`; `bash -c "cd
  <absent>"` returns **rc 1**.

So an absent `cwd` moves a **filing-time refusal** into a **launch-time death** — and the
runner writes its `LAUNCHED` record *first*. That manufactures precisely the stale-launch-record
class **L-344** was written to kill. Strictly worse than refusing.

### Ruling — SPLIT THE CLAUSE. Both halves are kept; neither is loosened.

1. **`check_age_guard()` applies only to a `cwd` that EXISTS.** Refuse on pre-existing time
   directories exactly as today. An absent `cwd` is **not** an age-guard finding and returns
   clean from this clause.
2. **New `check_cwd_launchable()` refuses an absent `cwd` under its own word, `EXEC`**, never
   `AGE-GUARD`, with a message that names the mechanism and the fix:
   `EXEC: cwd <path> does not exist; queue_runner.py chdirs into it (:286) and Popen(cwd=)
   raises FileNotFoundError (:293), so this entry would be recorded LAUNCHED and die. Fix:
   name an existing directory as cwd — the CASE directory is the lab convention — or mkdir -p
   it before filing.`
3. **`mkdir -p` is a legitimate remedy, not a workaround.** ansys should keep doing it.
4. **The preferred convention is the case directory**, and it already works: **10 of 10**
   launched cfd entries name `cases/<CASE>/`, which always exists; the launcher creates its own
   run root from absolute paths and ignores `cwd`. This needs no code change and is the
   one-line fix for any team blocked today.

**Net effect on queue depth: zero entries that pass today begin failing, and zero entries that
fail today begin passing.** The refusal is re-labelled and correctly attributed, not removed.
Nothing here weakens rule 4.

### Selftest and L-314 planted-failure proof (required before this ruling is believed)

| control | entry | must refuse under | must NOT refuse under |
|---|---|---|---|
| A | `cwd` absent | `EXEC` | `AGE-GUARD` |
| B | `cwd` exists, holds a time directory `0.1/` | `AGE-GUARD` | `EXEC` |
| C | `cwd` exists, clean | — (ACCEPTED) | — |

**Planted failures — each must FLIP a control, proving the clause is load-bearing and
reachable, not merely present:**
- disable `check_cwd_launchable` → **A must be ACCEPTED** (proves A's refusal comes from that
  clause and not incidentally from another);
- disable the time-directory scan → **B must be ACCEPTED**;
- re-point `check_age_guard` at absence → **A must refuse under `AGE-GUARD`**, which is the
  defect this ruling removes; the selftest must show it can be reintroduced and caught.

**L-314 Instance 1 applies to the harness that runs this selftest, and cfd paid for it again
today:** `set -e` is NOT in force in the agent Bash context. An assertion inside a `python3`
heredoc raises and **the surrounding shell continues** — at `da7e1477` a cfd assertion aborted
and the commit landed anyway. The selftest must therefore **return a checked exit code**, and
any caller must test it explicitly; a selftest whose failure is only printed is not a gate.

---

## R-TEAM-BINDING — 2026-08-27, cfd-supervisor. `[lab-attributed]` — **Sanaa may overrule.**

**An entry's `team` field MUST equal the team directory it sits in.** A mismatch is a
`TEAM-BINDING` validation failure, and therefore — correctly — a `refused/` outcome.

### Why this lands by the RULINGS route and not as an amendment to the standard

**This is a tooling-correctness clause.** It moves no gate, threshold, cap or label. It
refuses **only an entry that contradicts its own declared `team` field** — an entry
inconsistent with itself. It creates **no new gate on lab process**, and the runner already
moves refused entries to `refused/`, so this adds a **refusal reason to a mechanism that
already exists**, not a new mechanism. The `EXEC` clause (R-AGE-CWD above) landed by exactly
this route and is the live precedent.

`docs/standards/QUEUE_ENTRY_STANDARD.md` is **Sanaa's** and is **not edited**: it receives a
dated **cross-reference pointer** at its foot and nothing else. **D539's posture is unchanged
by this ruling** — adding a gate on lab process is reserved to Sanaa, and this is not one; a
measured rate is never an authorisation (`CLAUDE.md` rule 9).

### The defect, measured

`queue_runner.list_entries()` (`:387-395`) iterates **by directory** and never reads `team`;
`tick()` carries that directory's name into the round-robin cursor, the `LAUNCH_LOG.tsv` row
and the `<team>/launched/` destination. `check_schema` (`queue_entry_check.py:154-155`) asks
only whether `team` is one of the six, never **which** one. So an entry declaring one team in
another team's drop path launches and is recorded as the **directory's** — corrupting verdict
ownership and per-team queue depth. **A metric that can be silently wrong is worse than one
that is absent.**

### The two refusals this adds, and there are no others

| clause | refuses | never refuses |
|---|---|---|
| `TEAM-BINDING` | an entry whose `team` differs from its containing team directory | a missing/out-of-roster `team` (SCHEMA's, once); a file outside the six directories |
| `REQUIRE-BINDING` | **only under `--require-binding`:** a file outside the six directories, i.e. one where binding could not be checked | anything when the flag is absent |

`check_team_binding()` has three `return` statements, one of which is a refusal.
`require_binding_clause()` has two, one of which is a refusal. **Those two are the entire
refusal surface of this change** — enumerated from the AST, not read off the source.

### `NOT CHECKED`, not `NOT BOUND`

Outside the six directories the verdict prints a `TEAM-BINDING: NOT CHECKED` block naming
what was not checked and where it will be, in a **different shape** from the one-line
`TEAM-BINDING: bound to <team>/` a bound entry gets. **`NOT BOUND` would describe the
entry's state; `NOT CHECKED` describes the limit of our knowledge**, and the planted-zero
principle is about knowledge. It is not a refusal, because refusing there would force every
lane to copy into the drop path **before** validating — to validate only once the launch is
armed — which inverts the safe order and contradicts check-4-before-the-drop.
`--require-binding` is what makes it bite, and the enqueue procedure runs it **on the queued
copy, in place, after the copy**.

### Controls — C1–C12, spec `docs/standards/QUEUE_ENTRY_TEAM_BINDING.md` (frozen `b23b5638`, v1.1)

| # | control | planted failure it rests on |
|---|---|---|
| C1 | a matching entry draws no `TEAM-BINDING` | — (guards a check that refuses everything) |
| **C2** | **mismatch REFUSED, message naming both sides** | **the plant itself** |
| **C3** | **the clause no-opped → C2 must FLIP to accepted** | **C2 is worthless without it** |
| C4 | `validate()` with no `entry_path` raises loudly | — |
| C5 | the path defaulted → C4 flips, the mismatch validates clean and silently | the silent-skip defect, reproduced |
| C6 | a missing `team` refuses **once**, by SCHEMA | — |
| C7 | a draft outside the queue is accepted **and** says `NOT CHECKED` | — |
| C8 | the note suppressed → C7 flips | proves C7 read the note, not the absence of a refusal |
| C9 | one real `queue_runner.tick()`: moved to `refused/`, clause named, **nothing launched** | asserts the recognised path shape first, so it cannot pass vacuously |
| C10 | zero `ast.Assert` nodes after the change (L-332) | — |
| **C11** | **unbound entry accepted without `--require-binding`, REFUSED with it** | **the flag's plant** |
| **C12** | **the clause no-opped → C11 must FLIP** | **C11 is worthless without it** |

Plus a hygiene control: no control artefact may reach the real drop path — *the drop path is
a launch button, and a test file there is a launch.*

**Measured before the code existed and re-measured at landing:** entries in all six drop
paths carrying a `team` that disagrees with their directory — **zero**, and zero across the
`launched/` records. The clause is **preventive**; it invalidates no existing verdict.

**Known limit, recorded rather than hidden:** the clause recognises the path shape
`.../verification/queue/<team>/`. A runner started with a **non-default `--root`** is
therefore unbound and silently so. Production is unaffected (`DEFAULT_ROOT` is
`<repo>/verification/queue`; cron passes no `--root`). Referred, not fixed here — relaxing
the path shape changes the invariant, not its implementation.

---

## R-CAP — 2026-08-27, verification-supervisor, on the chief's lab-wide order. `[lab-attributed]`

**Question.** 50 of 109 queue entries were reported to carry no
`cap_core_min_registered`. What must an entry carry, and what must the validator do
when it does not?

### R-CAP.1 THE CLAUSE

**Every queue entry carries ONE of two fields on its face:**

- **`cap_core_min_registered`** — a positive number, **TRANSCRIBED from the case's
  pre-registration BEFORE compute**, never derived at queue time and never inferred
  from the estimate; **or**
- **`cap_status: "UNCAPPED-LEGACY"`** — an explicit declaration that no cap was
  registered.

**The validator WARNS on the absence of both and NEVER REFUSES** (D539: a cap is a
budget control, and turning its absence into a refusal would install enforcement
this lab has deliberately left **ADVISORY, OFF** — see
`docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md`).

**BUT: a `cap_core_min_registered` that DISAGREES with the figure in its own
pre-registration REFUSES.** **The ground is different and must not be confused with
the one above.** That refusal is **not a gate and not a budget judgement — it is a
FREEZE CHECK under standing rule 2.** The pre-registration fixes the cap before
compute; an entry restating it differently is a **transcription that contradicts its
frozen source**, and that is refused on the same authority that refuses any drifted
citation. **D539's advisory posture governs ENFORCEMENT of a cap; it says nothing
about the INTEGRITY of a transcribed one.**

### R-CAP.2 WHY `UNCAPPED-LEGACY` IS AN ADEQUATE ANSWER AND SILENCE IS NOT

An absent field and a declared absence are **different states**, and today they are
indistinguishable on the entry's face. **The declaration costs nothing and converts
"nobody transcribed it" into "there was nothing to transcribe" — two facts a later
reader must be able to tell apart.** This is the same principle as `nothing` versus
`PENDING:` in `REPORTING_CHARTER` §2 rules 4 and 5, and as naming **which** conjunct
failed in `COMMIT_INTEGRITY_STANDARD` §A1.4.

**It is also NOT a licence.** `UNCAPPED-LEGACY` records that no cap was registered
**for an entry already written**; it is not available to a new registration, which
must carry a cap under `CLAUDE.md` rule 12 — *every run is costed in its
pre-registration*.

### R-CAP.3 ⚠ THE GROUND FOR THIS CLAUSE IS SHARPER THAN THE MISSING FIELD, AND IT WAS MEASURED TODAY

`scripts/queue_runner.py:625-640` already handles an absent cap **honestly**: it
writes `ESTIMATE_OVERRUN.txt`, whose text states *"THIS IS AN ESTIMATE OVERRUN, NOT
A CAP … No cap was crossed by this record"* and discloses that the runner does not
enforce a registered cap either. **That disclosure is exemplary and this clause does
not disturb it.**

**The hazard is what happens ONE LAYER OUT.** Three completed runs carried
`CAP_OVERRUN.txt` files and a standards ruling was sought on whether their verdicts
survived. **Verified at source: none had breached its cap — 0.35× estimate, 0.58×
cap, 0.56× cap.** A monitor had compared spend against the **point estimate** and
labelled the result with **cap** language. **Both available rulings would have been
wrong** (`L-380`).

> **When the cap field is absent, tooling substitutes the estimate and then labels
> the result in cap language. The missing field is not a bookkeeping gap; it is what
> lets an estimate wear a cap's name.** That is the ground for R-CAP.

### R-CAP.4 THE PLANTED CONTROL — four limbs, and C4 is the one that makes C1 worth having

| control | scenario | required |
| --- | --- | --- |
| **C1** | entry with **neither** field | **WARN**, entry still admitted |
| **C2** | entry with `cap_status: UNCAPPED-LEGACY` | **PASS, SILENT** — a declared absence is not warned about, or the declaration buys nothing |
| **C3** | `cap_core_min_registered` **disagreeing** with its pre-registration | **REFUSE**, naming both figures and the registration path |
| **C4** | `cap_core_min_registered` **agreeing** with its pre-registration | **PASS, SILENT** |
| **C5** | **the clause no-opped → C1 and C3 must FLIP** | **C1 and C3 are worthless without it** |

**C4 is not decoration.** A validator shown only to warn and refuse is not shown to
**discriminate**; without C4, C1 and C3 are consistent with a check that fires on
everything. **And C3 must be driven against a REAL pre-registration file**, not a
fixture whose shape production never reads — `COMMIT_INTEGRITY_STANDARD` G1.

### R-CAP.5 ⚠⚠ THE REFERRED FIGURE DOES NOT REPRODUCE, AND THE DENOMINATOR IS THE FINDING

**Measured here at HEAD** (`git ls-tree -r HEAD`, never `git ls-files` — `L-92`):
**72 live queue entries, 53 with the cap field, 19 without.**
**Measured on DISK:** **135 entries, 78 with, 57 without.**

**Neither is 50 of 109.** The referred figure sits **between** the two frames, so it
is a **third population** this team has not identified. **The clause is written on
the MECHANISM (R-CAP.3), which does not depend on the count, and NOT on the figure.
The 50 of 109 is neither adopted nor contradicted — it is UNRECONCILED, and is
recorded as such rather than repeated.**

**AND THE LARGER FINDING IS THE GAP BETWEEN THE FRAMES: 135 queue entries exist on
disk and only 56 are tracked at HEAD. SEVENTY-NINE ARE IN NO COMMIT.** Every
HEAD-based sweep — this one, `scripts/check_filing.py`, and any future validator
census — **is blind to more than half the queue.** That is the same defect this team
recorded today in `DEAD_LEVER_AUDIT` §4 and `L-376`: **quoting an instrument's
output inherits its denominator.** **The validator runs on entries as it finds them,
so its own reach is unaffected; what is affected is every CENSUS anyone takes of the
queue, including the one that produced the referred figure.** **Referred to the
chief; not resolved here.**

### R-CAP.6 NOT CLAIMED

**No entry is edited by this ruling and no run is stopped.** `cap_status` currently
appears in **zero** tracked JSONs, so this field is new and every existing entry is
non-conforming until amended — **which is why the validator warns and does not
refuse.** **Whether the 19 (or 57) uncapped entries should be back-filled with a
transcribed cap or marked `UNCAPPED-LEGACY` is per-entry and belongs to each owning
team**, since only the owner can read the registration and say which is true.

### R-CAP.7 — AMENDMENT, 2026-08-27, same day: `UNCAPPED-LEGACY` IS A FINDING, NOT A DEFAULT, AND THE CLAUSE ABOVE SPECIFIES A MECHANISM THAT DOES NOT EXIST

**Appended; nothing above is rewritten. Raised by the chief on cfd's specimen and
closure's measurement; both verified here at source.**

**§7.1 THE HOLE IN R-CAP.1, AND IT IS MINE.** R-CAP.1 lets an entry declare
`cap_status: "UNCAPPED-LEGACY"` and did **not** require that anyone read the
registration first. **So a transcription MISS could be laundered into a permanent
declaration that no cap was ever registered** — a property **declared by
construction and never tested against the measurement**, which is the defect class
this team adopted as `VERIFICATION_CHARTER` §2g.5 this same day, appearing in my own
clause four minutes after I wrote it.

**THE AMENDED RULE:**

> **`cap_status: "UNCAPPED-LEGACY"` is applied ONLY AFTER the case's registration has
> been READ, and the entry carries the SEARCH THAT ESTABLISHED THE ABSENCE — the
> registration path and the lines searched.** A declaration without its search is an
> assertion, not a finding, and is refused the same way a zero without a planted
> control is refused.

**§7.2 THE SPECIMEN, VERIFIED HERE, AND IT IS SHARPER THAN REPORTED.**
`verification/queue/cfd/launched/F16b_SL2.json` carries **NO cap-bearing key at
all** — not a null, not a zero; its only cost key is **`cost_core_min_estimate`** —
while `verification/campaign/F16b_SL2_PREREGISTRATION.md:122` reads **"REGISTERED
CAP: 5 core-minutes"**.

**So an absent entry field is NOT evidence of an unregistered cap.** And note what
the specimen is: **the entry carries ONLY the estimate.** That is **R-CAP.3's
mechanism and this transcription miss in the same record** — when the cap is absent
the estimate is the only figure present, and tooling one layer out then labels
estimate-derived results in **cap** language. **The two defects are not neighbours;
they are the same entry.**

**§7.3 LAUNCHED RECORDS ARE HISTORICAL AND ARE NOT BACK-FILLED.** A record of what
ran is a record of what ran. **Editing it to carry a cap it did not carry at launch
would make the historical record agree with a rule written afterwards** — the move
this team refuses for pre-registrations. **The specimen is cited as EVIDENCE, and
nothing about it is corrected.**

**§7.4 ⚠⚠ THE CLAUSE ABOVE SPECIFIES A MECHANISM THAT DOES NOT EXIST. STATED ON ITS
FACE.** Closure measured, with a recognition control and a positive control (the
field stripped → **rc 0**), that **`scripts/queue_entry_check.py` has ZERO cap
logic.** **Verified here independently: `cap_core_min_registered`, `cap_status` and
"registered cap" return ZERO hits in that file.**

**R-CAP IS THEREFORE A SPECIFICATION FOR cfd TO BUILD, NOT A DESCRIPTION OF
BEHAVIOUR THAT RUNS TODAY.** Nothing in R-CAP.1–R-CAP.6 is currently enforced by any
instrument.

> **AND THE CONSEQUENCE, WHICH IS STANDING RULE 3 AT QUEUE SCALE (closure's words,
> adopted): until the clause is live, compliance with the cap-field order is
> evidenced ONLY by a BY-HAND comparison of the entry against its registration with
> the LINES NAMED. A validator `rc 0` is a zero from a reader shown UNABLE TO SEE A
> NON-ZERO.** Anyone reporting the queue clean on the strength of the validator is
> reporting the silence of a check that was never written.

**§7.5 THE CONTROL SET, REPLACING R-CAP.4's — the middle limb is the new one and it
is the one that matters.**

| control | scenario | required |
| --- | --- | --- |
| **C1** | entry with **neither** field | **WARN** |
| **C1b** | **absent or null cap field, registration DOES register a cap** | **WARN "transcription miss"** — **NEVER accepted as legacy** |
| **C2** | `UNCAPPED-LEGACY` **carrying its search**, registration genuinely capless | **PASS, SILENT** |
| **C2b** | `UNCAPPED-LEGACY` **without** its search | **WARN** — a declaration without its search is an assertion |
| **C3** | entry cap **≠** registration cap | **REFUSE** (freeze check, rule 2) |
| **C4** | entry cap **=** registration cap | **PASS, SILENT** — without this the others are consistent with a check that fires on everything |
| **C5** | clause no-opped → **C1, C1b and C3 must FLIP** | they are worthless without it |

**C1b must be driven on the F16b_SL2 shape** — an entry carrying only
`cost_core_min_estimate` against a registration whose cap line is real — because
that is the shape production actually holds (`COMMIT_INTEGRITY_STANDARD` G1: a
control whose scenario production never takes has not tested the clause).

### R-CAP.8 — AMENDMENT, 2026-08-27: THE REFUSE BRANCH REQUIRES AN UNAMBIGUOUS PARSE, AND A FIRST-MATCH READER WOULD REFUSE PRECISELY THE ENTRIES THAT OBEYED RULE 2

**Appended; nothing above is rewritten. cfd built a naive cap parser BEFORE writing
anything and measured THREE FALSE DISAGREEMENTS IN FIVE on its own well-disciplined
entries — all three would have become FALSE REFUSALS under R-CAP.1's REFUSE branch.
All three verified here at source.**

**§8.1 THE THREE CAUSES, EACH WITH ITS SPECIMEN.**

1. **THOUSANDS SEPARATOR.** `F23_HP_WEDGE_PREREGISTRATION.md:249` reads
   **"REGISTERED CAP: 1,100 core-minutes"**. Driven here: a naive `\d+` extraction
   returns **`['1', '100']`**, matching neither each other nor 1100; a
   separator-aware read returns **`['1100']`**. **F23 is CORRECT and would have been
   refused.**
2. **⚠⚠ FIRST-MATCH-WINS ON AN AMENDED REGISTRATION — THE ONE THAT MATTERS.**
   `F25_DUCT3D_PREREGISTRATION.md:335` carries the **superseded** "REGISTERED CAP:
   1,400 core-minutes"; the live value **2000** sits in its **pre-compute
   amendment** at `:473`, is named as `cap_core_min_registered` at `:491` and
   reaffirmed at `:582`. **A reader taking the FIRST cap line refuses the entry for
   AGREEING WITH THE AMENDED VALUE.**
3. **PHRASING AND LOCATION VARIANCE.**
   `cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md:183` reads **"Cap: 10.2
   core-minutes = 1.5 x the estimate"** — not "REGISTERED CAP" — **and lives under
   `cases/`, not `verification/campaign/`.** Both conventions are usual; neither is
   guaranteed.

**§8.2 WHY CAUSE 2 IS A DIFFERENT KIND OF DEFECT FROM THE OTHER TWO.**

Causes 1 and 3 are ordinary parser brittleness. **Cause 2 is not random: it
systematically refuses exactly those entries whose caps were LEGITIMATELY AMENDED
PRE-COMPUTE under standing rule 2, and passes registrations nobody ever corrected.**

> **A freeze check that reads a superseded number is not a freeze check — it is a
> check that PUNISHES CORRECT BEHAVIOUR AND REWARDS NEGLECT.** It inverts the
> incentive of the very rule it exists to enforce.

**This is `L-377`'s shape in a second place on the same day** — a metric whose
construction penalises the teams that obeyed the filing or amendment rule. **Named
here as a class, not as an F25 fact.**

**§8.3 THE CLAUSES, ADOPTED.**

- **(a) REFUSE REQUIRES AN UNAMBIGUOUS PARSE; AMBIGUITY WARNS.** No cap line found,
  more than one unresolved candidate, or a value not resolvable to a single number →
  **WARN, naming what it found and where it looked. NEVER REFUSE.**
- **(b) RESOLVE THE LAST BINDING CAP STATEMENT, NOT THE FIRST, AND RECORD THE LINE
  USED.** The refusal message **quotes the line it parsed and the value it got**, so
  a human checks the refusal in one glance rather than re-deriving it.
- **(c) THE PARSE IS SEPARATOR-AWARE AND PHRASE-TOLERANT**, and it must search the
  registration **wherever it lives** — `verification/campaign/` **and** `cases/`.
- **(d) THE `UNCAPPED-LEGACY` TEST IS A PROPERTY OF THE REGISTRATION, NEVER OF THE
  ENTRY.** Already ruled at R-CAP.7 and restated because cfd reached it
  independently from `F16b_SL2`: **a label asserting an absence must carry the search
  that established it — the same standard this lab holds a planted-zero control to.**

**§8.4 THE ASYMMETRY IS THE GROUND, AND IT IS THE THIRD TIME THIS TEAM HAS USED IT
TODAY.** A missed transcription miss costs **a warning nobody acted on**. A false
refusal **blocks real work at the queue and creates pressure to route around the
validator — and a validator people route around is worse than none.**

**So a check resting on a FREE-TEXT PARSE — evidence of a lesser kind than a
committed number — may only move toward the SAFER outcome.** Identical in form to
`COMMIT_INTEGRITY_STANDARD` §A1.2's *"(iii) may only refuse, never authorise"* and
to rule 5's one-way gate. **Here the safe direction is the opposite one — toward
WARN rather than toward REFUSE — because here a refusal is the destructive act.**
**The principle is not "always refuse" or "always warn"; it is that weaker evidence
may only push toward whichever outcome cannot destroy work.**

**§8.5 AND cfd's LIMIT ON ITS OWN EVIDENCE IS THE ARGUMENT FOR (a) BEING THE
DEFAULT.** cfd disclosed unprompted that this is **five registrations in one team,
all written under similar conventions, and that the three causes are certainly not
exhaustive.** **Exactly so — and that is why (a) is the DEFAULT POSTURE and not a
fallback.** A parser whose known failure list is admittedly incomplete must not hold
a refusal power; **the unknown fourth cause is the one that will produce the false
refusal nobody predicted.**

**§8.6 THE CONTROL SET, EXTENDED. Each limb driven to FIRE and to NOT-FIRE.**

| control | scenario | required |
| --- | --- | --- |
| **C6** | cap written with a **thousands separator** (`1,100`) | **PASS, SILENT** — no false disagreement |
| **C7** | **amended registration, first ≠ last** cap line (the F25 shape) | **MUST NOT REFUSE** — resolves to the LAST binding value |
| **C8** | phrase variant (`Cap:` not `REGISTERED CAP`) and a registration under `cases/` | found, **PASS SILENT** |
| **C9** | **two unresolved candidates** | **WARN**, naming both and where it looked — **never REFUSE** |
| **C10** | no cap line at all in a registration | **WARN**, naming where it looked |

**C7 is the one that must exist or cause 2 ships.** **C9 and C10 are the limbs that
prove (a): without them the clause is consistent with a parser that refuses whenever
it is confused.**

**§8.7 ONE RULE ON THE BY-HAND EVIDENCE, AND IT BINDS THIS TEAM TOO.** Until the
clause is built (R-CAP.7 §7.4), compliance is evidenced by hand — **and a by-hand
comparison counts ONLY WITH THE LINE NAMED.** *"I checked and it matches"* **is not
evidence**; it is the human form of a validator `rc 0` from a reader shown unable to
see a non-zero. **cfd's five-entry comparison named its lines and therefore counts.**

---

## R-QCOMMIT — 2026-08-27, verification-supervisor, writing the chief's ruling. `[lab-attributed, Sanaa may overrule]`

**The chief's ruling, adopted lab-wide, with the census method corrected and the
controls specified. Zero compute. No entry edited, no run stopped.**

### R-QCOMMIT.1 THE THREE CLAUSES

- **(a) A QUEUE ENTRY IS COMMITTED BEFORE IT IS DROPPED.** The entry is the **third
  leg of the freeze**, beside the pre-registration and the grading path. **An
  uncommitted entry lets the runner spend from a file whose `cap_core_min_registered`,
  `ranks` and `prereg_commit` are still MUTABLE** — which is rule 2's defect with the
  gate moved into a different file.
- **(b) THE LAUNCHED RECORD IS COMMITTED BY THE OWNING TEAM AT ITS NEXT BOARD WRITE,
  AS IT STOOD AT LAUNCH.** The runner's later `status_seen_utc` stamps are
  **infrastructure, re-committed without ceremony** (`QUEUE_RUNNER.md:109`), and are
  **NEVER read as a records failure.** A record of what ran is a record of what ran
  (`R-CAP.7` §7.3).
- **(c) UNTIL (a) IS MET THE CENSUS FRAME IS DISK.** A HEAD-scoped census of a queue
  that is not yet committed-before-drop measures compliance with (a), not the queue.

### R-QCOMMIT.2 THE CENSUS IS A SET DIFFERENCE, NEVER A SUBTRACTION OF COUNTS

**The runner MOVES an entry from `<team>/<name>.json` to
`<team>/launched/<name>.json` at launch.** A move is a **delete plus an add**, so
**subtracting counts nets it to zero and can go NEGATIVE.**

> **A census names its ENUMERATOR, its PATH SET, and its CLOCK — and compares SETS
> with `comm`, never totals with arithmetic.**

**The proof the subtraction method was broken is that it returned NEGATIVE counts.**
Measured here at **2026-08-27T22:25:34Z**, enumerators named:

| quantity | figure |
| --- | --- |
| `find verification/queue -type f -name '*.json'` | **121** |
| `git ls-tree -r HEAD -- verification/queue` | **138** |
| **on disk, NOT at HEAD (untracked)** — set difference | **0** |
| **at HEAD, NOT on disk (move fossils)** — set difference | **17** (heat-transfer 10, dafoam 4, ansys 2, closure 1) |
| **naive subtraction** | **−17** — a negative count, which is the method refuting itself |

### R-QCOMMIT.3 ⚠ AND A CENSUS WITHOUT ITS CLOCK IS NOT A MEASUREMENT — DEMONSTRATED, NOT ARGUED

The chief's reading at **22:21:53Z** returned **69 untracked lab-wide** (heat-transfer
48, dafoam 21). **Mine at 22:25:34Z returns 0.** **Neither is wrong.** In those
**three minutes and forty-one seconds** the teams committed their queue files under
clause (a).

> **Two honest readings of the same quantity, taken four minutes apart, differ by
> 69. A queue census without its clock is not a measurement of anything.**

This is `REPORTING_CHARTER` v2.3's stamp clause reaching a quantity rather than a
report, and it is why **frame-stating is a requirement of the census and not a
courtesy.** **Clause (a) is already substantially complied with** — that is the
finding those two readings jointly support, and neither supports it alone.

### R-QCOMMIT.4 ⚠⚠ TRACKED-AND-STALE IS THE INVISIBLE FAILURE AND THE WORSE ONE

**The compliance census compares each queue file's CONTENT against the HEAD blob —
`git cat-file -e HEAD:<path>` plus a sha256 — NEVER a tracked/untracked flag.**

Closure found `launched/G1_grid_triple.json` **TRACKED at HEAD but DIVERGENT on
disk**: HEAD carried the **pre-amendment** entry while the **amended** one is what
launched (`prereg_commit` re-filed `03be2015` → `a90077df`, **legal, because the
first launch produced zero physics**).

> **An untracked-only census scores that file COMPLIANT. A tracked-but-stale entry
> is worse than an untracked one, because it carries a HEAD blob that a reader will
> trust and that is not what ran.** Untracked is a gap a reader can see;
> tracked-and-stale is a gap that looks like evidence.

### R-QCOMMIT.5 THE FOSSILS ARE NOT DIRT AND CLEANING THEM IS A DELETION

The 17 "tracked-but-absent" paths are **runner-move fossils still at HEAD**.
**Cleaning them is an explicit `git mv` commit NAMING THE OLD PATHS — a deletion,
and therefore a supervisor's call in the owning team, NEVER a tidy-up** and never a
lane's initiative. `CLAUDE.md` rule 10: an unexpected change is inspected, never
reverted.

### R-QCOMMIT.6 CONTROLS — every limb driven both ways

| control | required |
| --- | --- |
| **entry dropped with NO commit containing its blob** | **WARN** (D539 — never REFUSE; a queue clause does not acquire a refusal power a cap clause was denied) |
| **MOVED entry** | counts as **tracked ONCE and untracked ZERO times** — the limb that catches the subtraction method |
| **tracked entry whose disk copy differs in ANY NON-RUNNER-STAMP key** | **FLAGGED** |
| **tracked entry differing ONLY in runner stamps** (`status_seen_utc`) | **PASSES** — or clause (b) is contradicted by the census that enforces it |
| **census re-run with no change** | identical output — a census that drifts against a static tree is measuring itself |

**The fourth row is the discriminating limb.** Without it the content check flags
every launched record the runner has touched, **which is every launched record**, and
the clause becomes noise that teams learn to ignore — `R-CAP.8` §8.4's route-around
hazard in a second place.

### R-QCOMMIT.7 ON SANAA'S DESK, NOT DECIDED HERE

**`verification/queue/LAUNCH_LOG.tsv` is UNTRACKED**, excluded as a *log* under
Sanaa's §1 — **yet it is the register of what compute was launched.** **A file
excluded as a log cannot also be the register of last resort.** **Recommended
wording, hers because it touches §1:** *LAUNCH_LOG.tsv, and the GPU instance's
equivalent, is a **REGISTER**, tracked and committed by the runner owner at each
board write — or replaced by a tracked per-launch record.* **Recommended, NOT
adopted.**

### R-QCOMMIT.8 — AMENDMENT: `git ls-files` IS NOT A CENSUS INSTRUMENT IN THIS REPOSITORY, IN ANY FORM — AND THAT DOES **NOT** EXPLAIN AWAY §3's COMPLIANCE FINDING

**Appended; nothing above rewritten. From heat-transfer's calibration lane via the
chief. Both mechanisms verified here, and the point of this section is that they are
SEPARABLE.**

**§8.1 THE INSTRUMENT DEFECT, MEASURED.** `git ls-files --others` compares the disk
against the **SHARED INDEX**, and the private-index protocol **never updates it**
(`commit-tree` + `update-ref` do not touch `.git/index`, by design). **So every file
landed through a private index reads "untracked" to that command PERMANENTLY.**

Measured now over `verification/queue`: **`git ls-files --others` reports 80 JSON
files as untracked, and ALL 80 ARE AT HEAD.** **An 80-of-80 false-positive rate — the
instrument is not noisy, it is inverted.**

> **`git ls-files`, IN ANY FORM, IS NOT A CENSUS INSTRUMENT IN THIS REPOSITORY.**
> The untracked census **enumerates DISK with `find`** and tests each path with
> **`git cat-file -e HEAD:<path>`**, or set-differences against
> **`git ls-tree -r HEAD`**. This is `L-92` — *`ls-files` answers the INDEX* —
> reaching the `--others` flag, where it is worse: **`--others` inverts rather than
> lags.**

**THE FORWARD HAZARD IS THE REASON THIS IS URGENT:** the next `ls-files`-based run
will report **~80 untracked**, all of them at HEAD, and **read as a REGRESSION THAT
NEVER HAPPENED** — a fleet-wide alarm about compliance that was already achieved.

**§8.2 ⚠ AND IT DOES NOT EXPLAIN AWAY §3. BOTH MECHANISMS ARE REAL AND THEY ARE
SEPARABLE — checked, because the tempting move is to let the artefact swallow the
finding.**

The natural inference is that the chief's **69** was the artefact and no compliance
occurred. **That inference is WRONG, and it is refuted by the commit graph.** Between
**22:21:53Z** and **22:25:34Z** five commits landed queue files:

| commit | team | what landed |
| --- | --- | --- |
| `dcb6a2ac` | heat-transfer | W1c queue entries frozen — *the third leg of the freeze* |
| `e1818f16` | heat-transfer | **45 untracked entries landed** |
| `ce00f57e` | dafoam | **the 20 untracked `launched/` records landed** |
| `ee4c331c` | heat-transfer | W1c dropped, three frozen entries moved |
| `09fdff24` | dafoam | `held/D6_chain.json` landed |

**45 + 20 = 65, against the chief's heat-transfer 48 / dafoam 21 = 69. The
compliance was REAL and is the dominant term.**

**So §R-QCOMMIT.3 stands and so does its lesson: two honest readings four minutes
apart differed because the quantity moved.** **What §8.1 adds is a SECOND defect that
will corrupt the NEXT reading, not a refutation of the last one.** **A newly found
instrument defect is not automatically the explanation for every prior number the
instrument was near** — that inference is as unearned as the one it replaces.

**§8.3 CONTROLS, ADDED.**

| control | required |
| --- | --- |
| a file landed **via a private index and never written to the index** | **counts as TRACKED** — the limb that catches `ls-files --others` |
| a genuinely untracked file | counts as **UNTRACKED** — or the census cannot see the thing it exists for |
| the census re-run after a private-index commit | the new path counts **tracked once**, and the count **does not regress** |

**§8.4 THE FOSSILS ARE PROVEN MOVES, WHICH SETTLES THE `git mv` WORDING.** Measured:
**every one of the 17 "tracked-but-absent" paths is paired with a same-named
counterpart on disk across the `launched/` boundary.** **That is direct evidence of a
MOVE rather than a deletion** — so the cleanup commit is a `git mv` **naming both the
old and the new path**, and it must never be recorded as a removal of work.
**Still a deletion at the tree level, still the owning supervisor's call, still never
a tidy-up.**

### R-QCOMMIT.9 — THE LAUNCHED RECORD LANDS AS A **RENAME**, NOT AS AN ADDITION — and two corrections to the referral that reached me with it

**Appended; nothing above rewritten. From heat-transfer's lane via the chief.
Verified here by execution, and two of the referral's claims did not survive.**

**§9.1 THE CLAUSE, ADOPTED.**

> **The launched record lands at the next board write AS A RENAME of the committed
> root entry — git's `R100`, same blob, new path — never as an ADDITION beside it.**
> **A rename is not the pure-deletion reversion signature rule 10 and `L-350`
> forbid, because the blob survives at the new path and the content diff is 0/0.**

**Verified on the exemplar:** `commit:ee4c331c` reports **three `R100` rows, 0
insertions, 0 deletions**, and `held/W1c_*` is now **absent from HEAD and absent from
disk — stranding nothing.** **The fossil class is retired going forward.**

**AND THE FOSSILS ARE NOT A PROPERTY OF GIT.** They are the residue of committing the
launched path as an **addition** while the root path stays at HEAD. **The count grows
by one per launch under current practice** — measured **17 at 22:25:34Z** and **19 at
22:44:16Z**, nineteen minutes apart. **A clock-stamped census again (`L-388`).**

**§9.2 ⚠ CORRECTION 1 — THE PAIRING PROOF IS *NOT* CONTENT IDENTITY, AND A CHECK
BUILT ON IT WOULD FAIL ON EVERY PAIR.**

The referral states each root fossil has a same-basename `launched/` counterpart
**"with identical content — the pairing is the deletion's proof."** **Measured: of
the 19 fossils, 18 have a counterpart at HEAD and ZERO of the 18 are byte-identical.**

**The differences reduce to exactly two keys — `_field_classes` and `_launch` —**
sampled across three pairs and identical in each: **runner-added launch metadata,
which is precisely what clause (b) calls infrastructure.**

> **So the pairing test is NOT byte equality. It is: SAME BASENAME across the
> `launched/` boundary, WITH ALL DIFFERENCES CONFINED TO A NAMED RUNNER-KEY SET
> (`_launch`, `_field_classes`, `status_seen_utc`).** **A content-identity check
> would refuse all eighteen genuine pairs** — `R-QCOMMIT.6`'s discriminating-limb
> hazard, arriving in the very test proposed as the proof.

**AND THE NINETEENTH HAS NO COUNTERPART AT HEAD AT ALL.** It is **named as unpaired
rather than assumed into the class**; the pairing is **18 of 19**, not 19 of 19, and
that one must be resolved by its owner before any cleanup touches it.

**§9.3 ⚠⚠ CORRECTION 2 — THE MANDATED SHAPE COLLIDED WITH THIS TEAM'S OWN COMMIT
GUARD, AND THE GUARD WOULD HAVE REFUSED IT.**

`COMMIT_INTEGRITY_STANDARD` clause 3 asserted the diff is **"NON-EMPTY and
single-path."** **A rename is TWO paths:** `ee4c331c` returns **6 paths** under
`git diff-tree -r` without rename detection. **This team's own guard would have
refused the exact commit shape this clause mandates** — `L-362` again, **inside one
team's own standards.**

**Fixed at `commit:90ae7ea2` (`COMMIT_INTEGRITY_STANDARD` v1.3):** the assertion is
now against a **declared EXPECTED PATH SET**, and a rename declares **two** members
plus a matched **`R100`, 0/0** check. **A rename that is not `R100` is a rename plus
an edit and is not a rename for that clause's purposes.** **R-QCOMMIT.9 is not
executable without that fix, and the two clauses are to be read together.**

**§9.4 THE NAIVE ESTIMATOR STAYS WRONG ON ITS OWN SEPARATE GROUND.** Retiring the
fossil class does **not** repair the subtraction estimator: **it assumes
`tracked ⊆ disk`**, which a move violates regardless of how the move is committed.
**Two independent defects; fixing one does not fix the other**, and `R-QCOMMIT.2`'s
set-difference method stands unchanged.

**§9.5 NOT CLAIMED.** **The existing fossils are a ONE-TIME PAIRED CLEAN, and the
deletions themselves remain on Sanaa's desk** — this clause governs **future**
launches and authorises nothing retrospective. **The cleanup remains an explicit
`git mv` naming both paths, the owning supervisor's call, never a lane's
initiative.**

---

### R-AGE-CWD.3 — AMENDMENT, 2026-08-28: THE `EXEC` CLAUSE IS **HOST-BLIND**, AND ON A TWO-HOST LAB ITS OWN JUSTIFICATION INVERTS

**Ruled by verification-supervisor, from a personal read of the gating script
(`SUPERVISION_CHARTER` §3 check 1 — a measurement/gating script's diff is read by the
supervisor, never relayed). Zero compute. No verdict moves; no entry is re-graded.**

**The clause is not withdrawn.** `check_cwd_launchable()` is kept for the reason R-AGE-CWD
gave: an entry with an absent `cwd` is recorded `LAUNCHED` and then dies, and refusing at
filing time is better than a launch-time death behind a stale record. **What is amended is
its scope, because the clause silently assumes something that stopped being true on
2026-08-22.**

**The defect, at source.** `scripts/queue_entry_check.py:348`:

```python
    if Path(cwd).is_dir():
        return []
```

`Path(cwd).is_dir()` is evaluated on **the machine running the validator**. Every sentence of
the surrounding docstring reasons about `scripts/queue_runner.py:286` and `:293` — code that
runs on **the machine that executes the case**. **The clause tests one host and argues about
another, and until this lab had a second host those were the same machine.**

**They are not the same machine now.** `docs/GPU_CAPABILITY_STATE.md` records GPU quota granted
2026-08-22; a GPU is a **separate instance**, launched per run. A GPU case's `cwd` lives on the
GPU host. The CPU box, where the validator runs, has never seen it.

**AND THE ERROR RUNS IN BOTH DIRECTIONS, WHICH IS WHY THE SCOPE HAD TO BE WRITTEN DOWN RATHER
THAN THE CHECK SIMPLY LOOSENED.**

| | validator host | executing host | clause says | truth |
|---|---|---|---|---|
| **false `EXEC`** | absent | present | refuse | **launchable — a good entry is rejected** |
| **false accept** | present | absent | accept | **dies at launch behind a stale `LAUNCHED` record** |

**The second row is the clause's own stated failure mode, delivered by the clause while it
reports green.** A directory that exists on the CPU box and not on the GPU host — the ordinary
condition for any case whose tree has not yet been pushed — produces **exactly** the outcome
`check_cwd_launchable()` exists to prevent, and produces no finding. **A gate whose green is
indistinguishable from its own failure mode is not a weak gate; it is an inverted one**, and it
belongs to the class `DEAD_LEVER_AUDIT` §5 named: **a guard whose verdict is independent of the
data it purports to read.** Here the verdict is not independent of *a* filesystem — it is
independent of **the one that decides the answer.**

**RULED.**

1. **`EXEC` binds only where the validator host IS the executing host.** An entry whose
   execution host is not the validator's host is **`NOT MEASURED` for `EXEC`** — never a pass,
   never a refusal. A finding this check cannot make must not be reported as a check it made.
2. **An entry must therefore DECLARE its execution host.** Where the field is absent the entry
   is treated as local, and **that assumption is stated in the finding text**, so a reader can
   see which proposition was actually tested.
3. **This is `L-392` in a second costume, and that is the ground rather than an analogy.**
   `L-392`: *a sha that resolves locally is not a statement about the local machine.* Here: **a
   path that resolves locally is not a statement about the machine that will chdir into it.**
   Both are a **transfer** question answered with a **local** lookup, and both return a
   confident, well-formed, wrong answer. **Third occurrence of that shape in this lab in six
   days.** The general form, offered for the standard: **a check that queries host A to decide a
   proposition about host B has not measured the proposition, whatever it prints.**
4. **No repair is ordered here.** The instrument is `cfd`'s
   (`scripts/queue_entry_check.py`); this ruling fixes what the clause *means* and hands the
   code change to its owner, who also owes this team the host-blind spec as a diff.
