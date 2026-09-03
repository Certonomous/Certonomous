# SPEC — freeze enforcement at the choke point

**Authority.** `[SANAA-DIRECT]`, 2026-09-03, captured verbatim at
`etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md`.
Her words, quoted rather than paraphrased because the wiring order is the ruling:

> **Freeze enforcement: highest lab priority after the auto-stop patch. Wiring
> order: (1) the queue daemon refuses to grade any run whose comparator's sha
> does not match its frozen registration — enforcement at the choke point first,
> primitive is fine; (2) coverage measured and reported weekly (graders with
> reachable freeze coverage / total) until it reads 145/145; (3) then a planted
> violation proves the enforcer fires through the real path — the enforcer is
> itself an instrument and gets instrument-tested; (4) a one-line honest note
> goes into the lab record: freeze enforcement was documentary until [date];
> every certificate issued before then relied on process discipline, not
> tooling. No re-grading of past results unless a specific comparator is shown
> to have moved — but the note is on the record.**

**Status.** SPEC. Nothing here is implemented and nothing here changes a gate,
threshold, band, cap or label. **`scripts/` and the queue daemon are outside this
team's folder scope**, and being handed the program does not widen that scope
(`CLAUDE.md` rule 9) — this team **specs**, cfd **implements the daemon hook**.
The line is the same one held at `VERIFICATION_CHARTER.md` §2q.

**Author:** verification-supervisor. **Solver compute: 0 core-min, $0.00.**

---

## 0. What is being cured, stated plainly

`CLAUDE.md` rule 2 names `scripts/check_comparator_freeze.py` as what enforces
the comparator freeze. The instrument exists, it is good, and — on the reading
carried into this session and **under re-derivation at the time of writing,
marked `VERIFY`** — **nothing executable invokes it.** An instrument nobody runs
does not enforce; it documents. That is the whole of the defect, and it is the
same class as the two board checks recorded in `BOARD_BASE_RULE_PROPOSAL.md` as
*"built, committed, wired into nothing."*

**The lab's own charter already names this shape.** `§2p`: a pass must be
attributable, and a pass from a degenerate path is not evidence. `§2p.2`'s
empty-input test applied to the status quo returns the verdict in one line:
**the freeze rule passes every run in the repository, and would do so if every
comparator in it had been rewritten this morning.**

---

## 1. Limb 1 — the choke-point refusal

**The primitive, as ordered.** At grade time the queue daemon:

1. resolves the comparator path for the case being graded;
2. hashes the comparator's **on-disk bytes**;
3. compares that hash against the sha recorded in the case's **frozen
   registration**;
4. on **MISMATCH** — refuses. It does not grade, does not emit a verdict, and
   does not fall through to a default. The refusal names the case, the
   comparator path, the expected sha and the observed sha.

Steps 1–4 are the whole of limb 1. *Primitive is fine* is her instruction and it
is the right one: the enforcement value is in the refusal existing at the choke
point, not in its sophistication.

### 1.1 THE DESIGN DECISION THIS SPEC EXISTS TO TAKE: what happens when there is no reachable frozen sha

This is the question that decides whether the enforcer is real, and it cannot be
deferred to the implementer.

A large fraction of the lab's graders currently have **no reachable freeze
evidence at all** — they are reported `NO-MARKERS` by the existing instrument
rather than judged. So the daemon will constantly meet cases where there is
nothing to compare against. Two obvious answers, both wrong:

| answer | what it actually does |
|---|---|
| **unreachable → grade anyway, silently** | The enforcer is a **no-op on exactly the population that needs it.** Feed it a case with no freeze evidence and it passes — `§2p`'s degenerate path, installed at the choke point, on day one. |
| **unreachable → refuse** | The lab **stops grading almost everything immediately.** An enforcer that halts the lab gets switched off within a day, and then enforcement is documentary again with an extra script. |

> **RULED — the enforcer takes THREE outcomes, not two, and the third is dated:**
>
> - **MISMATCH → REFUSE**, from the day the hook lands. This is unconditional.
>   A comparator whose bytes disagree with its frozen registration is the exact
>   condition rule 2 exists to catch, and there is no transition period for it.
> - **MATCH → GRADE**, normally.
> - **UNREACHABLE → GRADE, and RECORD THE UNREACHABILITY** on the run's own
>   record, in a field a later sweep can count. It is never silently ignored and
>   it is never confused with a match. The count is the weekly coverage metric of
>   limb 2.
>
> **AND THE THIRD OUTCOME CARRIES A SUNSET, or it is permanent.** A
> "report-only" state with no end date is documentary enforcement wearing a
> second costume, and this team would be installing the very thing it is being
> asked to remove. **At the sunset, UNREACHABLE becomes REFUSE.**

**The sunset date is Sanaa's to set, and this spec recommends the one she has
already named.** Her limb 2 runs the coverage metric *"until it reads 145/145"* —
that is, until no grader is unreachable. **The condition she set as the target is
exactly the condition that makes the third outcome unnecessary.** Recommendation:
**UNREACHABLE becomes REFUSE when coverage first reads full**, with the changeover
announced one weekly report in advance so no team is surprised by a refusal.

### 1.2 What the daemon must NOT do

- **It must not repair.** A mismatch is refused and reported; it is never
  resolved by re-hashing, re-freezing, or picking the nearer of two candidates.
- **It must not grade partially.** A refused run produces no verdict at all — not
  a `GATE FAIL`, not a `NOT A RESULT`. Those are verdicts about the *physics*; a
  freeze mismatch is a statement that **no verdict is admissible from this
  artifact**. `BLOCKED` is the display state for the queue.
- **It must not be bypassable by a flag that defaults to on.** If an override
  exists at all it is narrow, it must name the specific case, and its use is
  visible in the run record — the `Board-Repair:` escape in
  `BOARD_BASE_RULE_PROPOSAL.md` is the precedent for how to shape an escape that
  is necessary without being an off switch.

---

## 2. Limb 2 — the coverage metric

**Sanaa's definition, adopted verbatim:** *graders with reachable freeze coverage
/ total.*

- **Denominator:** every grader in the walked population — `analyse_*.py`,
  `grade_*.py`, `score_*.py` under `POPULATION_ROOTS`, currently
  `("verification", "cases", "docs/campaigns")`.
- **Numerator:** every grader whose row carries a **judged freeze verdict** —
  i.e. any status **not** in the instrument's own `UNJUDGED` set
  (`AMBIGUOUS-SCOPE`, `NO-MARKERS`, `UNDATED-MARKER`).

> **RULED — COVERAGE IS REACHABILITY, NOT INNOCENCE.** A row judged `UNFROZEN`,
> `UNCOMMITTED` or `MODIFIED_AFTER_COMMIT` is **COVERED and FAILING**. A row
> reported `NO-MARKERS` is **not covered at all**. These are opposite conditions
> and a single number that mixes them can be improved **by hiding violations** —
> which is the one way this metric could make the lab worse than no metric.
>
> **The weekly report therefore carries TWO axes and never collapses them:**
> **coverage** = judged / total, and **compliance** = frozen / judged.
> A team may raise coverage only by making a grader's freeze evidence reachable,
> never by making a failure disappear.

**Refusals the metric itself must carry**, because a coverage number is an
instrument and gets the same treatment as any other:

- **empty population → REFUSE**, not `0/0` and not "clean". Already law
  (`§2p.2`) and already implemented in the walker; the metric must not
  re-introduce it at a higher level.
- **the metric reports the per-status breakdown beside the ratio**, so a reader
  can always reconstruct both axes from the printed row.

**⚠ ONE THING TO PUT TO SANAA BEFORE THIS NUMBER IS REPORTED TO HER.** Her target
reads *"until it reads 145/145"*. The figure **145** reached this session as the
count of `NO-MARKERS` **rows**, not as the count of **all** graders — so *"145"*
may be the numerator's deficit rather than the denominator. **The two readings
give different targets, and this team will not silently pick one.** The
denominator is being re-derived; the first weekly report will state the measured
total explicitly and ask her to confirm which figure she meant.

> **⚠ SUPERSEDED IN ITS FIGURES BY §7 (same day, measured). The `145` above is
> WRONG — the measured count is `144`, and neither figure is the denominator.
> Read §7 before quoting any number from this section.**

---

## 3. Limb 3 — the enforcer is itself an instrument

Her words: *the enforcer is itself an instrument and gets instrument-tested*, and
the test drives **the real path**. Required arms, each tied to the degenerate
path it closes:

| # | arm | drives | expected | closes |
|---|---|---|---|---|
| 1 | **planted mismatch** — a scratch case whose comparator's bytes are altered after its registration froze the sha | the **production** daemon | **REFUSED, not graded** | the enforcer does not fire at all |
| 2 | **positive control** — an untouched, correctly frozen scratch case | the **production** daemon | **GRADED normally** | `§2p.3(e)`: a refuser that refuses everything is, from its verdicts alone, indistinguishable from a correct one |
| 3 | **wrong-object control** — a case where a *different* file changed while the comparator's sha is untouched | the **production** daemon | **GRADED** | the enforcer keyed on the wrong artifact and merely detects "something moved" |
| 4 | **empty input** (`§2p.2`) — a case with no comparator resolvable at all | the **production** daemon | **NOT a silent pass** — recorded UNREACHABLE per §1.1, or refused after the sunset | the degenerate path |

**Binding conditions on the harness:**

- **The production daemon, never a copy** (`§2p.3(d)`): a test that exercises a
  redundant copy of the guarded logic tests nothing. If the daemon cannot be
  driven end-to-end, that is a finding about the daemon, not a licence to test a
  stand-in.
- **Scratch cases only.** No arm touches a real run, a real registration or a
  real verdict.
- **The plant must be recoverable and recovered** (`§2o`): the harness reads its
  own plant back and refuses if it cannot see it, before it believes any arm.
- **`__pycache__` is cleared between the control and the planted run** — the
  stale-bytecode inversion has made a clean control fail and a mutated case pass
  in this lab before.

---

## 4. Limb 4 — the honest note

Her template: *"freeze enforcement was documentary until [date]; every
certificate issued before then relied on process discipline, not tooling."*

**Adopted, and this spec proposes it be made sharper in one respect, because the
plain template understates the finding against us.** There are **two** dates, and
the gap between them is the part worth recording:

> **Freeze enforcement was documentary until `[HOOK DATE]`. The enforcing
> instrument, `scripts/check_comparator_freeze.py`, existed from `[SCRIPT
> DATE]` — but nothing executable invoked it, so between those two dates the lab
> held a freeze enforcer it never ran. Every certificate issued before
> `[HOOK DATE]` relied on process discipline, not tooling. No recorded verdict is
> withdrawn on this account; a specific comparator shown to have moved is a
> separate matter and is handled on its own facts.**

**Both dates are under re-derivation and neither is asserted here.** `[HOOK
DATE]` is the day limb 1 lands in the daemon and is therefore still in the
future; `[SCRIPT DATE]` is the instrument's first commit.

**Why the second sentence belongs in a note about our own credibility:** "we had
no tool" and "we had the tool and never wired it in" are different admissions,
and the second is the one that generalises. **It is also this team's own defect** —
`§2q` is where this team specced the widening of that very instrument and
recorded that `scripts/` was out of its scope, which is correct and is also how
an instrument ends up owned by nobody at the moment it needs wiring.

**Where it lands:** a clause in `VERIFICATION_CHARTER.md` (this team's file, and
the file that governs certificate issuance), a `docs/LESSONS.md` entry, and — for
certificates issued after the hook date — a provenance line, so a future reader
of a certificate can tell which side of the date it was issued on **from the
certificate itself** rather than by knowing this history.

---

## 5. Marker association — **EVIDENCE PENDING, principle stated**

Limb 2 cannot reach full coverage while graders are unreachable, and the largest
known cause is **how a comparator is associated with the runs it grades.**

**MEASURED, by me, at source.** `scripts/check_comparator_freeze.py:315` —
`markers = read_markers(tree)`. The completion markers a comparator is judged
against are read from **the comparator's own directory**. Association is
therefore **same-directory**, and a comparator that does not sit beside its run
tree has no evidence to be judged on. `docs/campaigns/T-family/analyse_t23g2.py`
is the worked example: `§2d.9.2` ruled **permanently** that it does not move, so
this is not a filing accident that tidying can fix.

**The principle, which does not depend on the pending measurement:**

> **RULED — ASSOCIATION IS DECLARED, NEVER INFERRED FROM A POOL.** Pooling every
> marker in reach and letting the source-name scope sort it out is rejected: the
> instrument's own docstring establishes that pooling is a false-positive
> generator, and repo-wide pooling makes it worse, because the failure mode is a
> **false `UNFROZEN`** — a false accusation against a team, which under limb 1
> becomes a **refusal to grade a sound run**. An enforcer that blocks good work
> on a widening artifact will be switched off, and deservedly.
>
> **A declaration is accepted from either side, in this precedence:** (1) the
> **frozen registration**, where it names both the comparator and the run tree —
> authoritative, because rule 2 fixes the grading path at the pre-registration
> commit and the registration cannot move after first compute; (2) failing that,
> the **comparator's own source** naming its run tree. **If both exist and
> DISAGREE, REFUSE (exit 2) — never choose.** A disagreement about which runs a
> comparator grades is precisely the condition in which a silent pick is worst.
>
> **AND THE DECLARED TREE IS NOT ENOUGH BY ITSELF.** The declared tree must also
> contain at least one marker **named by the comparator's own source** under the
> existing scope rule. Two independent limbs must agree, and the source-name limb
> is the one that cannot be aimed at a convenient tree.

**The direction check, stated because a widening that can flatter its user is
worse than no widening:** could a team declare the tree whose earliest marker is
latest, and so buy itself a `FROZEN`? Where the declaration lives in the
sha-frozen registration, no — it cannot move after first compute. Where it lives
in the comparator, editing it moves the comparator's **last-commit date later**,
which can only make the freeze test **harsher**. **The residual hole, named
rather than papered over:** a comparator committed early carrying a declaration
pointing at a tree that did not yet exist and was populated later. The
two-limb requirement above is the mitigation, and it is a mitigation, not a
proof.

**What is pending:** whether cross-directory association is in fact the dominant
cause of unreachability, or whether the unreachable population is mostly
scripts that grade nothing and were swept in by a name pattern. **The two call
for different repairs — association machinery versus population refinement — and
building the first before measuring would be this lab's recurring error of
propagating a class on an unchecked count.** The classification is in flight;
this section is completed when it reports.

---

## 6. What this spec does not do

- **It orders no re-grading.** Sanaa: *"No re-grading of past results unless a
  specific comparator is shown to have moved."* Adopted without qualification.
- **It changes no gate, threshold, band, cap or label** — 0 · 0 · 0 · 0 · 0.
- **It amends no script.** `scripts/` is outside this team's scope; this document
  is the specification and the build is cfd's.
- **It does not claim the enforcer will catch a comparator edited before its
  registration was written.** Freeze is a claim about *order*, and an artifact
  that never had an honest order cannot be rescued by a hash comparison. The
  instrument finds the timestamp; a human reads the diff.

---

## 7. MEASURED UPDATE — same day, and it corrects this document in four places

**Appended 2026-09-03, after the fact-establishment this spec called for
returned. Sections 1–6 are left standing and are corrected here, never
rewritten.** Every figure below was re-derived from disk by this supervisor with
a whole-repo run of the instrument, not relayed.

### 7.1 The coverage figures — **the number this program was briefed on is wrong**

| status | rows `[MEASURED]` |
|---|---|
| `NO-MARKERS` | **144** |
| `FROZEN` | **27** |
| `UNFROZEN` | **10** |
| `AMBIGUOUS-SCOPE` | **5** |
| `AMENDED_AFTER` | **3** |
| `UNCOMMITTED` · `MODIFIED_AFTER_COMMIT` · `UNDATED-MARKER` | **0 · 0 · 0** |
| **total walked** | **189** |
| **JUDGED — i.e. COVERED, §2 sense** | **40 of 189** |

**Coverage today is `40 / 189`.** The briefed `145` is wrong; the measured count
is `144`; and **neither is the denominator.** The target as stated corresponds to
no figure this instrument emits. **Referred to Sanaa, not silently
reinterpreted.**

### 7.2 **§1's premise is wrong: there is no grading step to hook**

`[MEASURED]` The queue daemon performs exactly one state transition — **queued →
launched**. It moves an entry file into `launched/` and never reads a result.
**A hook placed "where the daemon grades" would never fire, because no such line
exists.**

> **RULED: THE HONEST CHOKE POINT IS THE LAUNCH, NOT THE GRADE.** Enforcement
> attaches to the queue-entry validation that already refuses entries on the live
> path every tick. This is a correction to the **mechanism** of Sanaa's
> instruction, not to her ruling, and it serves her intent better: the run is
> refused **before the compute is spent**, not after.

§1's three outcomes are unaffected — they now govern launch rather than grading.

### 7.3 **A trap §1 did not name, and it would have fired immediately**

> **RULED: `UNFROZEN` IS NOT `ILLEGAL`.** `§2d.1`'s four-condition repair
> exception exists *because* this instrument's own first pass mis-condemned a
> lawfully repaired comparator — and that comparator **still reads `UNFROZEN`
> today**, one of the ten. **An enforcer keyed on the freeze instrument's
> `UNFROZEN` verdict would refuse every comparator lawfully repaired under
> `§2d.1`.** The enforcement quantity is the **sha mismatch against the frozen
> registration — a byte comparison** — never the instrument's timestamp verdict.
> The two answer different questions and only the first is what she ordered.

### 7.4 **§5's pending question is answered, and the obvious repair was the wrong one**

`[MEASURED]` **Every completion marker in this repository lives in three run
trees. Zero exist under `cases/`, under `docs/campaigns/`, or in any other run
subtree.** Of the 144 unjudged rows:

- **9** carry evidence a pairing repair could reach — **5** cross-directory,
  **4** also cross-convention (a marker carrying no case identity at all);
- **~135** have **no completion-marker evidence anywhere in the repository** —
  real graders in campaigns that never adopted the convention the freeze test
  reads.

> **RULED: THE COVERAGE HOLE IS NOT PRINCIPALLY A PAIRING DEFECT.** It is that
> four of six teams never adopted the evidence convention. A pairing repair is
> worth building and **converts 9 rows of 144**. Full coverage needs a completion
> convention those campaigns do not have — **which is a different piece of work,
> owned by those teams, and it is the larger half.**

**§5's principle (association is DECLARED, never inferred from a pool) stands
unchanged** and governs the 9. **What §5 held back is now the finding: a program
that had built the association machinery first would have spent its effort on
6 % of the gap and reported a repair.** That restraint is the only reason this
section states a proportion instead of a plan.

### 7.5 The honest note's two dates are established

`[MEASURED]` The instrument has **three commits ever, the first `2026-08-19`.**
Four independent searches — tracked sources at HEAD, the whole worktree, crontab
and system units, and git hooks — find **no executable invocation of it**. The
one file that names it uses it as a **hash fixture**, not as an enforcer to run.

**So: the instrument existed from 2026-08-19 and fired zero times in the fifteen
days to this date.** §4's two-date wording is correct as drafted and now carries
its first date. The second — the wiring date — is still in the future at the time
of writing.

### 7.6 **⚠ COORDINATION, NOT DESIGN: limb 1 is already being built by another team**

Uncommitted work implementing limb 1 exists in the working tree, authored
elsewhere and **independently reaching §7.2's conclusion in its own header** —
that the daemon has no grading step and the launch is the honest choke point.
**Inspected, not touched** (`CLAUDE.md` rule 10: an unexpected change is
inspected, never reverted).

**This makes the next step a coordination call before it is a design call.** This
spec is offered to that work as its specification, not as a rival to it. Two
things must be reconciled before either is believed: **(a)** its entry-count
figures and this team's disagree, and the discrepancy must be resolved before
**either** number is cited in a record; **(b)** §7.3's `UNFROZEN ≠ ILLEGAL`
constraint must reach it **before** it lands, or it will refuse lawfully repaired
comparators on day one.
