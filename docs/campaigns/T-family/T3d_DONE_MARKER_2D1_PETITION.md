# T3d — **PETITION TO `verification-supervisor`: MAY ONE `DONE.R_fx` PRODUCER BE ADDED TO T3d's GRADING PATH AFTER FIRST COMPUTE?**

**From:** heat-transfer (drafted by a lane; the finding was verified at source by
the supervisor before this document was commissioned, and re-verified at source
by the lane that wrote it — every line number and every blob below was read on
disk, not taken from the brief).
**To:** `verification-supervisor`, who owns `docs/charters/VERIFICATION_CHARTER.md`
and therefore §2d.1 (`:1914` the clause, `:1936-1942` the four conditions,
`:1944-1947` condition (2)'s stated purpose).
**Written:** 2026-09-04T01:20Z, against HEAD `70c0fc2f`.
**Rung:** T3d — `verification/runs/T-family/T3_runs/R_fx`, live, iterating now.
**Registration:** `docs/campaigns/T-family/T3d_PREREGISTRATION.md`.

> **This is internal routing between two teams inside the box. `CLAUDE.md` rule 7
> (SUBMISSIONS PARKED) is not engaged and is not being tested: nothing here is
> sent, filed, uploaded, registered, posted or commented anywhere outside
> Certonomous.**

> **THIS PETITION GRANTS ITSELF NOTHING, AND THE FILE IT DESCRIBES DOES NOT
> EXIST.** `mark_done_t3d.py` **has not been written** — not as a draft, not
> uncommitted, not in a scratch directory. It was deliberately not drafted, so
> that verification is not handed a fait accompli. **No `DONE.R_fx` has been
> written and none will be written before a ruling.** The registered grading
> path is byte-unchanged: `analyse_t3d.py`, `build_t3d.py` and `launch_t3d.sh`
> stand at the sha256 values registered in `T3d_PREREGISTRATION.md` §6.

---

## 0. THE HONEST ASYMMETRY, LED WITH — because it is the whole of the question

**`mark_done_t3_rff.py` was registered for `R_ff` BEFORE `R_ff` had iterated.
The `mark_done_t3d.py` this petition describes would be added for `R_fx` AFTER
`R_fx` has iterated. That difference is not a detail of the petition; it is the
petition.**

`docs/campaigns/T-family/T3_R_FF_PREREGISTRATION.md:318` reads:

> `## AMENDMENT 1 — 2026-08-26 (PRE-FIRST-COMPUTE): the grading path, frozen.`

and `:320-324` discharges rule 2's pre-compute test in rule 2's own words — the
condition named and how it was checked:

> *"Immediately before this commit `ls verification/runs/T-family/T3_runs/` shows
> **no `STATUS.R_ff`, no `DONE.R_ff`, no `gate_t3_rff.json`**, and `R_ff/` holds
> no `0/`, no time directory and no `processor*` — `R_ff` has not iterated; zero
> core-minutes spent."*

**Nothing of that kind can be written today for `R_fx`.** `R_fx/0/T` was created
at 2026-09-03T18:04:05Z, `R_fx/log.solve` carries **17 152** `ExecutionTime`
lines of the registered 24 000 at 2026-09-04T01:15:46Z, and eight
`processor*` directories hold time directories up to `16000`. **The rung has
taken first compute. Its gates are closed under §2b/§2d and only §2d.1 can move
anything on its grading path.**

**Heat-transfer does not ask verification to treat the two cases as alike. They
are not alike. We ask for the post-compute exception on its own terms, and we
accept that the answer may be no.**

---

## 1. THE ASK, STATED NARROWLY

> **May ONE new file — `verification/runs/T-family/T3_runs/mark_done_t3d.py` —
> be added to T3d's grading path, whose entire case-specific content is
> `CASE = "R_fx"` in place of `mark_done_t3_rff.py`'s `CASE = "R_ff"`, and which
> imports the frozen `mark_done_t3` (blob `5da28c73`) and `mark_done_t3_ext1`
> (blob `e4cbb992`) UNMODIFIED, so that every clause of `CLAUDE.md` rule 4 that
> actually decides completion is code already frozen and already registered?**

**What the file would contain, and it is the point of the ask:** the rule-4
logic is **not written by this petition and not written by the new file**. It is
`mark_done_t3.check(root, case)` — clauses 1–6, `rc=0`, the `End` line, last time
== `endTime`, the field tuple, the `ExecutionTime` count, and the age guard —
called with `"R_fx"` as its argument. The new file adds the same
`reconstructpar_rc = 0` physics-critical clause and the same
infrastructure-is-disclosed-never-gating split that `mark_done_t3_rff.py`
already carries, because it *is* that file with one identifier changed.

**Explicitly NOT asked for, each refusal deliberate:**

| not asked | why not |
|---|---|
| a hand-written `DONE.R_fx` | **Refused by heat-transfer before this petition was drafted, and it is the reason the petition exists.** A hand-written marker would satisfy `analyse_t3d.py`'s check and certify nothing — it would *assert* rule 4's six clauses without *applying* them. That is precisely the fail-open the marker exists to prevent. |
| any edit to `analyse_t3d.py` | The comparator's refusal is **correct** and we do not want it weakened. See §3. |
| any edit to `mark_done_t3.py`, `mark_done_t3_ext1.py` or `mark_done_t3_rff.py` | Rule 6. They are imported unmodified or not touched at all. |
| a gate, threshold, band, cap or label move | None is involved. §9. |
| any re-grading of any past result | Sanaa 2026-09-03 17:30Z: *"No re-grading of past results unless a specific comparator is shown to have moved."* **No comparator has moved.** T3c's four `NOT A RESULT` rows and every T3 row stand untouched. |
| a backfill or a sweep of the other 38 `mark_done_*.py` scripts | Sanaa 20:00Z forbids building an instrument to measure another instrument's reach until the first has changed a verdict once. This one has changed none. |
| anything about **D-J1** | `T3d_DJ1_2D1_FORWARD_ONLY_PETITION.md` is a **separate** petition already with verification, on a different defect (`rng == 0 → 0.0`) in a different file. A ruling on either must not be read as a ruling on the other. |

---

## 2. THE BLOCKED RESULT, NAMED AND MEASURED

> ### **BLOCKED RESULT: T3d's entire triple. `analyse_t3d.grade()` refuses at exit 2 and emits NO row, NO GCI and NO verdict, for `R_m`, `R_f` and `R_fx` alike — the triple is graded whole or not at all.**

**Measured, at this write:**

| fact | value | artifact |
|---|---|---|
| `DONE.R_m`, `DONE.R_f` | **present** (2026-08-24 15:58) | `verification/runs/T-family/T3_runs/` |
| `DONE.R_fx` | **ABSENT** | same directory |
| `STATUS.R_fx` | **ABSENT** — the run has not finished | same directory |
| iterations done | **17 152** of the registered **24 000** | `R_fx/log.solve`, `^ExecutionTime` count |
| age-guard datum | **2026-09-03T18:04:05Z** | `R_fx/0/T` mtime |
| elapsed at 01:15:46Z | **25 901 s** at **8** ranks | difference of the two above |
| **core-min spent so far** | **≈ 3 453.5** — **DERIVED** (elapsed × ranks ÷ 60), **not measured**: the authoritative figure is `STATUS.R_fx`'s `core_min`, which does not exist yet | — |
| **projected total** | **≈ 4 832 core-min** at the observed 0.6622 it/s | derived, not measured |
| registered POINT estimate | **5 442.1 core-min** | `T3d_PREREGISTRATION.md` §5 |
| registered HARD CAP | **16 326 core-min** | `T3d_PREREGISTRATION.md` §5; enforced by `launch_t3d.sh:22,41` |

**If no producer is permitted, that compute grades to a refusal and T3d closes
`NOT A RESULT` on a grading path no outcome could have satisfied** — the same
defect class as **T19**, whose completion rule was mutually exclusive with its
own registered `residualControl` and which cost **29.133 core-min** to discover
(`docs/LAB_STATE.md:15329`;
`docs/campaigns/T-family/GATE_PREDICATE_SATISFIABILITY_READ_2026-09-03.md:223,364`).

**AND SUNK COMPUTE IS NOT AN ARGUMENT FOR RELIEF, WHICH THIS PETITION STATES
BEFORE VERIFICATION HAS TO.** The lab does not widen, repair or extend a grading
path because a run was expensive. Sanaa's standing rule is that gates are never
adjusted to fit an answer, and 4 832 core-min is not a reason to adjust one.
**The 4 832 core-min is stated so the ruling is made on a measured consequence
rather than an impression, and for no other purpose. If the four conditions are
not met, verification should refuse, and T3d should close `NOT A RESULT` on a
defect that is entirely ours.**

---

## 3. THE DEFECT, EXHIBITED BY QUOTATION AND BY MEASUREMENT — as §2d.5 requires

### 3.1 The refusal, and it is CORRECT

`verification/runs/T-family/T3_runs/analyse_t3d.py:172-177`:

```python
def grade(root, ladder=LADDER, out=print):
    missing = [c for c in ladder.values()
               if not os.path.isfile(os.path.join(root, "DONE.%s" % c))]
    if missing:
        refuse("no completion marker DONE.%s -- the triple is graded whole or not at all"
               % ", DONE.".join(missing))
```

`LADDER = {"c": "R_m", "m": "R_f", "f": "R_fx"}` (`:68`). **This behaviour is
right and heat-transfer does not want it changed.** A comparator that graded a
case without a completion marker would be reading fields it has not been shown
were written by the run allowed to produce them — rule 4's whole subject.

### 3.2 The registration REGISTERS THE REFUSAL AND REGISTERS NO PRODUCER FOR IT

`T3d_PREREGISTRATION.md` §6 registers **three** files by full sha256 —
`analyse_t3d.py`, `build_t3d.py`, `launch_t3d.sh` — **and no completion-marker
producer of any kind.** The same section, in its own registered text, records:

> *"`--selftest`: **PASS, 0 failed**, including arm S-9 and the `DONE.R_fx`
> refusal at exit 2."*

**So the registration is not silent about `DONE.R_fx`. It names the artifact, it
registers that the graded path refuses without it, and it registers a selftest
that drove that refusal — and it registers nothing that can produce it.** That
distinction matters under §2d.5 and §6 argues it there.

### 3.3 The launcher writes `STATUS`, never `DONE` — by design

`launch_t3d.sh:44` sets `STATUS="$ROOT/STATUS.$CASE"`; `:88-97` is `write_status`;
`:128` calls it. **No `DONE` marker is written anywhere in the file, and should
not be** — the launcher is the thing being judged, and a runner that certifies
its own completion is the fail-open `mark_done_t3.py`'s own docstring was written
against (*"under a rule the runner does not itself apply"*, `:2-3`).

### 3.4 Neither registered marker script targets `R_fx`

- `mark_done_t3.py:33` — `CASES = ["R_c", "R_m", "R_f", "P_m", "C_lam_m", "W_m", "D_m", "O_m"]`. **No `R_fx`, no `R_ff`.**
- `mark_done_t3_rff.py:30` — `CASE = "R_ff"`, a module-level constant read by `read_status`, `judge` and `run`; there is no argument that overrides it.

**Measured by reading both files end to end.** The departure is therefore
exhibited both ways §2d.5 demands: **by quotation** (§6's own sentence naming a
refusal on an artifact it registers no producer for) and **by measurement** (the
two identifier facts above and the two absent files in §2).

---

## 4. IS IT REALLY A ONE-IDENTIFIER CHANGE? — MEASURED, AND THE ANSWER IS "ONE BEHAVIOURAL IDENTIFIER, PLUS TWO NON-BEHAVIOURAL STRINGS"

**`mark_done_t3_rff.py` was read end to end (157 lines).** Every occurrence of
the case name in the file:

| line | text | class |
|---:|---|---|
| 30 | `CASE = "R_ff"` | **BEHAVIOURAL — the only one.** Read by `read_status` (`:36`), `judge` (`:51,53,54`), `run` (`:65,73,78,80,86,88`) and `_forge` (`:94,110,114`) |
| 2, 3, 4, 5, 9, 20, 21 | docstring prose (`"DONE marker for T3 R_ff…"`, `launch_t3_rff.sh`, `AMENDMENT 1`) | **non-behavioural** — no predicate reads it |
| 120 | `tempfile.mkdtemp(prefix="t3rffmd_")` | **non-behavioural** — names a throwaway selftest directory, deleted at `:135` |

**So the honest statement is: one behavioural identifier, plus a docstring that
must be rewritten to describe the new file truthfully, plus one cosmetic temp
prefix. It is not a literal one-token diff and this petition does not claim it
is.** What matters for §2d.1 is the *behavioural* count, and it is one.

**All six rule-4 clauses come from the imported frozen module — verified by
reading `mark_done_t3.py`:**

`mark_done_t3_rff.py:53` is `fails = list(MD.check(root, CASE))`. `MD.check` is
`mark_done_t3.check(root, case)` at `mark_done_t3.py:49-100` and carries, in one
function, every clause of rule 4 — each anchor below read on disk: the `STATUS`
`rc=0` test (`:58`), the `End` line (`:66-67`), the `ExecutionTime` count
(`:68`, asserted at `:98`), last time == `endTime` (`:79`), the field tuple with
its RAS branch (missing-field report at `:96`), and the **age guard** against
the case's own `0/T` (`:88-90`). **Nothing is restated in the `_rff` file.
Nothing would be restated in a `_t3d` file.**

**A fact that cuts FOR the ask and was checked because it might have cut against
it:** `mark_done_t3.check()` **takes `case` as a parameter and does not validate
it against `CASES`**. The hard-coded list at `:33` is only `argparse`'s default
in `main()` — `ap.add_argument("cases", nargs="*", default=CASES)` at `:105`.
**So calling the frozen `check()` on `"R_fx"` requires no
change to the frozen file whatever** — the frozen rule-4 logic is already
case-agnostic and already registered. This is the single strongest engineering
fact in the petition.

**Two facts checked because a "same shape" claim is worth nothing unless the
inputs match, and both hold:**

1. **`STATUS` format.** `mark_done_t3_rff.read_status` parses `key=value` lines
   and requires `reconstructpar_rc` as **physics-critical** (`:57-60`).
   `launch_t3d.sh:88-97` writes exactly that format and writes
   `reconstructpar_rc` at `:93` from the real `reconstructPar` rc captured at
   `:123`. **Compatible.**
2. **`INFRA_LOGS`.** `mark_done_t3_rff.py:32` looks for `log.launch`,
   `log.decomposePar`, `log.reconstructPar`, `log.checkMesh.run`.
   `launch_t3d.sh` writes all four (`:84, 113, 123, 112`). **Compatible.**

**And one small disclosure gap, stated against our own interest and NOT asked to
be fixed:** `launch_t3d.sh` also writes `cap_core_min`, `solver`, `solver_path`,
`note`, `started_utc` and `ended_utc`, and `mark_done_t3_rff.py`'s `INFRA` tuple
(`:31`) does not carry them, so a `_t3d` copy would not disclose them in the
marker text. **They are infrastructure, never gating, and they remain readable in
`STATUS.R_fx` itself.** Adding them would widen the change beyond one identifier,
so **this petition does not ask for it.** It is named here rather than discovered
later.

**One clause that would be inert, stated so nobody thinks it was hidden:**
`mark_done_t3_rff.py:54-55` applies `mark_done_t3_ext1.check_ext` when
`log.solve.ext1` exists. `R_fx` has no extension segment planned and none
exists, so `MDX.has_ext` (`mark_done_t3_ext1.py:87-88`) returns `False` and the
branch is never taken. **The import is retained anyway, unmodified, because
removing it would be a second behavioural change.**

---

## 5. THE PRECEDENT, AND ITS LIMIT — verified at source

**Verified.** `docs/campaigns/T-family/T3_R_FF_PREREGISTRATION.md:334` registers,
in AMENDMENT 1's frozen grading-path table:

> `| verification/runs/T-family/T3_runs/mark_done_t3_rff.py | 9436399f8682efb6 | 0ad4f08ee0ee10b6 | 157 |`

**And the registered blob is byte-identical at HEAD `70c0fc2f`:**
`git ls-tree` gives `9436399f8682efb6acfcf35ae74e85c3e434e2fd` for that path.
The two frozen modules it imports are likewise unchanged from the blobs its own
docstring names: `mark_done_t3.py` = `5da28c73…` (`:19`, *"HEAD blob 5da28c73"*)
and `mark_done_t3_ext1.py` = `e4cbb992…` (`:28`). **Three blob claims, three
matches, checked at HEAD rather than taken from the docstring.**

**THE LIMIT OF THE PRECEDENT, AND IT IS THE ONLY THING ABOUT IT THAT MATTERS.**
AMENDMENT 1's own heading is `(PRE-FIRST-COMPUTE)`. **It establishes that this
exact marker design was found acceptable; it establishes NOTHING about whether it
may be added after compute.** A precedent for the *content* of a change is not a
precedent for the *timing* of one, and §2d exists entirely about timing.
**Heat-transfer does not offer R_ff as authority for the ask. We offer it as
evidence for condition (1) — that what would be added is a known, reviewed,
already-frozen instrument rather than something invented today with the answer in
sight.**

---

## 6. THE FOUR §2d.1 CONDITIONS, ANSWERED BY NAME, IN ORDER — INCLUDING WHERE WE ARE WEAK

The clause, quoted from `VERIFICATION_CHARTER.md:1936-1942`:

> **A change on the grading path made after the first graded solve is permitted
> when, and only when, all four hold: (1) it repairs a DEMONSTRABLE ERROR rather
> than a preference; (2) the error was established by an instrument INDEPENDENT
> OF THE HYPOTHESIS — one that grades nothing, such as a near-identity, a guard
> or a control; (3) the record discloses it, names that instrument, and
> QUANTIFIES WHAT MOVED; and (4) the pre-repair values are recorded beside the
> published ones. Failing any of the four, 2d stands.**

### (1) A DEMONSTRABLE ERROR RATHER THAN A PREFERENCE — **MET, and it is demonstrable in the strict sense**

**The error is not that the comparator refuses. The error is that T3d's
registered artifact set cannot produce an input its own registered comparator
requires.** That is not a matter of taste and it is not a judgement call: it is
two file-existence facts and two hard-coded identifiers, all four in §3, any of
which a third party can re-derive in one command. **No outcome of the run can
satisfy the registered grading path.** T19 is the named specimen of that class in
this lab's own record, and its cost is on the board at 29.133 core-min.

**Where this is weaker than K0cS, said plainly:** K0cS's error made a *published
number wrong by 10–27 %*. **T3d's error makes no number wrong. It makes every
number unobtainable.** Verification may reasonably think an *absence* of numbers
is a lesser defect than *wrong* numbers, or may think it a greater one. We do not
argue it either way.

### (2) AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS — **MET, we believe, on TWO grounds, and the second is the one we rely on. THE HONEST DIFFICULTY IS NAMED FIRST.**

**The difficulty:** §2d.1's own examples — a near-identity, a guard, a control —
are **executable**, and **no heat balance, near-identity or planted control found
this.** It was found by **reading the frozen registration against the code**.
Read literally, that fails condition (2). We say so before arguing otherwise,
because verification has refused a petition for exactly this shape before
(`§2p.9`/`§2d.5`, `R6`: *"a MISSING instrument is neither agreement nor
disagreement… condition (2) has no object"*).

**Ground A — `CLAUDE.md` rule 4, a standing rule.** Verification ruled at
`VERIFICATION_CHARTER.md:4804` (§2d.9.1):

> *"**RULED: a standing rule is an instrument independent of the hypothesis for
> condition (2), on the same ground and with more force than a frozen
> registration.**"*

Rule 4 is lab-constitutional, predates T3d, grades nothing, and cannot know
which direction T3d's verdict wants. **The defect is a departure from rule 4:
rule 4 requires that a run be judged complete only by applying six clauses, and
T3d's registered set contains no instrument that applies them to `R_fx`.**

**Ground B — the frozen pre-registration itself, under §2d.5
(`VERIFICATION_CHARTER.md:4498`):**

> *"**THE FROZEN PRE-REGISTRATION IS AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS
> FOR CONDITION (2), WHEN AND ONLY WHEN THE DEFECT IS A DEMONSTRABLE DEPARTURE
> FROM ITS TEXT** — a registered feature absent from the code, a registered gate
> never implemented, a registered count the code does not meet, a band the
> registration does not carry. The departure must be exhibited by quotation and
> by measurement, both.**"*
>
> *"**AND IT IS NOT AN INSTRUMENT WHERE THE REGISTRATION IS SILENT. Silence
> cannot be departed from.**"*

**The silence limb is the sharpest thing pointed at this petition, and §3.2 is
our answer to it: T3d's §6 is NOT silent about `DONE.R_fx`. It names the
artifact and registers, in its own frozen text, that the comparator refuses at
exit 2 without it** — *"including arm S-9 and the `DONE.R_fx` refusal at exit 2"*.
A registration that registers a required input and registers no producer for it
is, we submit, the *"registered feature absent from the code"* limb rather than
the silence limb. **The quotation is §6's own sentence; the measurement is §3.4's
two identifiers and §2's two absent files. Both, as §2d.5 requires.**

**But we flag a tension in verification's own record rather than let it be found
later:** §2d.4.5's disposition table records `R2` as *"a registered feature never
built, **not** a departure"*, while §2d.5's granted list includes *"a registered
feature absent from the code"* as a departure. **Those two lines can be read
against each other and this petition does not resolve them. If §2d.4.5 governs,
condition (2) fails and §2d stands.** That is verification's call, not ours.

### (3) THE RECORD DISCLOSES IT, NAMES THAT INSTRUMENT, AND QUANTIFIES WHAT MOVED — **MET, BY DISCLOSING A MEASURED ABSENCE**

**Nothing moves, and the way to discharge that is already ruled.**
`VERIFICATION_CHARTER.md:4395` (§2d.3):

> *"**A `§2d.1` repair may satisfy conditions (3) and (4) by DISCLOSING AN
> ABSENCE — but the absence must be MEASURED AND NAMED, never asserted.** The
> record states **the count of graded solves under the registration (zero)** and
> **names the artifacts that do not exist**, resolvably."*

**Measured and named, resolvably:**

- **Graded solves under `T3d_PREREGISTRATION.md`: ZERO.** `analyse_t3d.py` has
  never graded. `gate_t3d.json` **does not exist** in
  `verification/runs/T-family/T3_runs/`.
- **`DONE.R_fx` does not exist. `STATUS.R_fx` does not exist.** Both named,
  both checked on disk at 2026-09-04T01:15:46Z.
- **Quantified movement: 0 rows, 0 verdicts, 0 GCI values, 0 gates, 0 bands, 0
  labels.** A file that decides only whether the comparator may read a case at
  all **cannot move a number**; it can only ever refuse more.
- The instrument is named twice, in §6 above: `CLAUDE.md` rule 4 (Ground A) and
  `T3d_PREREGISTRATION.md` §6 frozen at its registered sha256 (Ground B).

### (4) PRE-REPAIR VALUES RECORDED BESIDE THE PUBLISHED ONES — **MET VACUOUSLY, AND THE VACUITY IS THE DISCLOSURE**

**There are no pre-repair values, because there are no values.** The pre-repair
state of every T3d quantity is `refuse(): exit 2`, and it is recorded here as
such. Nothing is published under this registration; nothing is withdrawn;
nothing is restated. Under §2d.3's ruling, **the absence is the discharge,
provided it is measured — and §3 (3) above measures it.**

**Adjacent results that are NOT touched, so no reader infers otherwise:** T3c's
four `NOT A RESULT` rows, `gate_t3.json`, `gate_t3_rff.json`, and every T3 row
graded on 2026-08-24 stand exactly as published. **This petition would not cause
a single existing number to be recomputed.**

---

## 7. THE CASE AGAINST GRANTING, MADE AS VERIFICATION WOULD MAKE IT

**We put it at its strongest, because a petition that only argues its own side is
not evidence.**

> **7.1 The freeze exists precisely so a path cannot be adjusted with results in
> sight, and the results are in sight.** `R_fx` is at 17 152 of 24 000. The team
> asking for the addition is the team that will be graded by it. Rule 2 says the
> freeze *"is the document's entire evidentiary content: it proves the gate could
> not have been chosen to fit the answer."* **A grading-path artifact added at
> hour seven of a nine-hour run does not have that property, however innocuous
> its content.**
>
> **7.2 The registration had the opportunity and did not take it.**
> `T3d_PREREGISTRATION.md` §6 was written by a team that had registered a marker
> for `R_ff` eight days earlier under a heading that says `PRE-FIRST-COMPUTE` in
> capitals. It registered the comparator's `DONE.R_fx` refusal in its own §6 text
> and still registered no producer. **This is not an unforeseeable defect; it is
> the same team forgetting the same artifact class it had itself registered
> before.** §2d's answer to "we forgot" is that 2d stands.
>
> **7.3 "Innocuous" is exactly how erosion arrives.** A rule that permits
> post-compute grading-path additions *when they look small* has no stopping
> point, because every petitioner will believe theirs looks small. Verification
> has already ruled once today that **a restrictive repair is not
> self-certifying** (§2d.10, v1.42). *"It can only refuse more"* is an argument
> the next petitioner will also make.
>
> **7.4 The circularity warning applies.** §2d.1's closing sentence: *"Nothing a
> verdict depends on may be repaired on the authority of the verdict it
> produces."* Verification wrote at `:4436` that **a comparator's own failure to
> run must not become the qualification for relaxing the rule that governs
> repairing it.** T3d's ask has exactly that surface shape: *the grader refuses,
> therefore let us add something so it stops refusing.*

**Our answers, and where we concede:**

- **To 7.1 — this is the strongest and we do not defeat it, we narrow it.** What
  would be added **cannot select a direction**: it decides only whether the
  comparator may read `R_fx` at all, and only ever toward refusing more. Its
  content is a file frozen and registered **before `R_ff` iterated**, whose
  behavioural delta is one string. **But narrowing is not answering. If
  verification holds that timing alone disposes of it, that is a coherent reading
  of rule 2 and we do not dispute it.**
- **To 7.2 — CONCEDED IN FULL. The defect is entirely ours.** It is a
  registration failure by heat-transfer, made eight days after the same team got
  it right, and it belongs in this team's record as such whatever the ruling.
- **To 7.3 — we accept the principle and offer the stopping point rather than
  ask verification to invent one:** a grant here need be no wider than *a
  producer for an input the registration ITSELF NAMES as required and registers
  no producer for, whose logic is entirely imported from modules frozen before
  first compute, and which can only refuse more.* **If verification cannot state
  a stopping point it is willing to live with, it should refuse.**
- **To 7.4 — we think this one does NOT bite, and we say why rather than assert
  it.** `:4436`'s circularity was a petitioner using *the comparator's refusal*
  as the **ground for relaxing** the rule. **Nothing here is relaxed.** The
  refusal stays; the rule-4 clauses stay; the six clauses get *applied* rather
  than *asserted*. The verdict is not being repaired on its own authority — the
  verdict does not exist and might well be `NOT A RESULT` or `GATE FAIL` when it
  does. **§3 of the registration already predicts against a PASS.**

---

## 8. THE ALTERNATIVES — INCLUDING ONE THAT CUTS AGAINST THIS PETITION, DISCLOSED BECAUSE WE FOUND IT

**8.1 Hand-write `DONE.R_fx`.** **Refused by heat-transfer, and it is not on the
table.** It asserts rule 4's six clauses without applying them and is the exact
fail-open the marker exists to prevent. **Not requested, not drafted, and it
would remain wrong even if granted.**

**8.2 Run the frozen `mark_done_t3.py` with `R_fx` as a positional argument —
AND THIS ONE IS REAL, SO WE DISCLOSE IT AGAINST OUR OWN INTEREST.** As §4
records, `mark_done_t3.check()` does not validate its `case` argument against
`CASES`; `main()` takes `cases` as `nargs="*"` (`:105`). **`python3
mark_done_t3.py R_fx` would therefore apply rule 4 clauses 1–6 to `R_fx` and
write `DONE.R_fx`, using a file frozen since 2026-08-21 and adding no new file at
all.** Verification may well conclude that this needs no exception, and if so
this petition is moot and should be refused as unnecessary. **We did not run it
and will not run it before a ruling.**

**Why heat-transfer nonetheless prefers 8.3, argued honestly:**

- **It is still a post-compute grading-path act.** `mark_done_t3.py` is not in
  `T3d_PREREGISTRATION.md` §6 either. Using it is the same §2d question wearing
  different clothes — a *less* visible one, because it leaves no artifact for
  `check_comparator_freeze.py` to scope.
- **It drops a physics-critical clause.** `R_fx` runs **decomposed on 8 ranks**
  (`launch_t3d.sh:118-119`, `simple (8 1 1)`) and its fields are reconstructed at
  `:123`. `mark_done_t3.check` knows nothing of `reconstructpar_rc`; only the
  `_rff` design carries it (`:57-60`) and calls a failed reconstruction *"not a
  result"*. **A marker written by 8.2 could certify a case whose reconstruction
  failed.**
- **Its `STATUS` reader is the wrong one.** `mark_done_t3.check` greps
  `rc=(\d+)` out of a single-line pool-format `STATUS` (`:56-59`);
  `launch_t3d.sh` writes multi-line `key=value`. The regex would still find
  `rc=`, but it would also match nothing else it needs, and it discloses no
  infrastructure at all.
- **It would report no infrastructure.** No `wall_s`, `core_min`, `capped`,
  `checkmesh_rc` or `decomposepar_rc` in the marker — the disclosure split that
  Sanaa's *bookkeeping-never-voids-physics* rule and L-342 are built on.

**So 8.2 is cheaper and weaker. If verification prefers it, heat-transfer will
take it and record the weaker certification honestly — but verification should
choose it knowing it is choosing a marker that cannot see a failed
`reconstructPar`.**

**8.3 The ask of §1.** One file, one behavioural identifier, all rule-4 logic
imported frozen.

**8.4 Refuse everything.** T3d closes **`NOT A RESULT`** on an unsatisfiable
grading path; the defect is recorded against heat-transfer; the next rung
registers its marker in its own pre-registration where it costs nothing and needs
no exception — **which is the disposition verification itself prescribed for `R6`
(§2d.5): *"A gap in a registration is closed by the next registration, not by
repairing the rung that revealed it."*** **That sentence is the single closest
authority on this petition and it points at refusal. We cite it because it is
against us.**

---

## 9. WHAT THIS PETITION DOES NOT ASK FOR — the explicit nil list

| item | count |
|---|---:|
| gates created, moved or retired | **0** |
| thresholds, bands, caps, labels moved | **0** |
| edits to any frozen file | **0** |
| re-grading of any past result | **0** — Sanaa 17:30Z; **no comparator has moved** |
| backfills or sweeps of the other `mark_done_*.py` scripts | **0** — Sanaa 20:00Z |
| new compute authorised | **0 core-min** — `R_fx` is already running under its registered cap; this petition neither launches nor extends anything |
| bearing on **D-J1** | **none.** `T3d_DJ1_2D1_FORWARD_ONLY_PETITION.md` is separate and already with verification |
| sends, filings or anything leaving the box | **0** — rule 7, SUBMISSIONS PARKED |

**A grant would remove a legal obstacle. It would not be a verdict, a budget or
a launch order** — verification's own framing at `:4407`.

---

## 10. THE DEADLINE, AND THE FALLBACK IF NO RULING ARRIVES

**`R_fx` lands soon.** Measured at 2026-09-04T01:15:46Z: 17 152 of 24 000
iterations in 25 901 s = **0.6622 it/s**, so the remaining 6 848 iterations
project to **≈ 10 341 s** and a landing at **≈ 2026-09-04T04:08Z**. *(An earlier
estimate on the record reads ~03:48Z —
`GATE_PREDICATE_SATISFIABILITY_READ_2026-09-03.md:949`. Both are projections from
a rate; neither is a measurement, and reconstruction adds unmeasured time after
the last iteration.)*

> ### **FALLBACK, BINDING ON HEAT-TRANSFER FROM THIS COMMIT AND NOT CONTINGENT ON ANY RULING:**
>
> **If no ruling has arrived when `R_fx` lands, T3d holds at `PENDING`.**
>
> - **No grading is attempted.** `analyse_t3d.py` is not run against `R_fx`.
> - **No marker is written, by any means** — not by hand, not by `mark_done_t3.py`
>   positionally, not by a new file.
> - **`mark_done_t3d.py` is not written.**
> - The run is allowed to finish and `STATUS.R_fx` is allowed to be written by
>   the registered launcher, because that is the launcher doing its registered
>   job and is not a grading act.
>
> **`PENDING` here is `CLAUDE.md` rule 1's display/queue state — "not yet run" —
> and is NEVER a softened `GATE FAIL`.** If verification refuses, T3d's honest
> label is **`NOT A RESULT`**, and heat-transfer will publish it as that.

**There is no urgency-based ask.** Verification should take the time the question
needs; the compute is already spent either way and a rushed grant is worth less
to this lab than a considered refusal.

---

## 11. WHAT THIS PETITION COULD NOT SETTLE — stated as undetermined, not guessed

1. **Whether §2d.4.5's *"a registered feature never built, not a departure"* or
   §2d.5's *"a registered feature absent from the code"* governs §3.2.**
   **UNDETERMINED.** They point opposite ways on this fact pattern and only
   verification can say which controls.
2. **Whether 8.2 (`mark_done_t3.py R_fx`) is a grading-path change at all**, or
   merely running an already-registered tool on a new argument. **UNDETERMINED,
   and it may dispose of this petition entirely.**
3. **The actual core-min of `R_fx`.** **NOT MEASURED** — `STATUS.R_fx` does not
   exist. Every figure in §2 beyond the iteration count and the two mtimes is
   **derived**, and the rule-12 estimate-versus-actual row owed to
   `docs/COST_CALIBRATION.md` cannot be written until the run lands.
4. **Whether `R_fx` will converge, and what T3d's verdict would be if graded.**
   **UNKNOWN, and deliberately so.** `T3d_PREREGISTRATION.md` §3 registers the
   disclosure against its own interest and §2 registers a prediction that can
   lose. **This petition is written without knowing which way the answer goes,
   which is the only condition under which it is worth writing.**
5. **Whether any other live rung in this family has the same producer gap.**
   **NOT SWEPT** — Sanaa's 20:00Z rule forbids building the instrument to find
   out until this class has changed a verdict once. It has changed none.
