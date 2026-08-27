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
