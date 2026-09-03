# PROPOSAL — NOT ADOPTED — board migration to per-team files plus a generated rollup

**Status:** PROPOSAL, DRAFTED FOR SANAA'S SIGN-OFF. Nothing here is in force and
nothing here has been executed. Sanaa's 2026-09-03 ~16:00Z ruling 5 approved the
**direction** and ordered the **migration drafted for her sign-off, no urgency**;
her words: *"board-file structure — adopt the per-team-files-plus-generated-rollup
direction from the splice proposal; no more shared-write board file. Draft the
migration for my sign-off, no urgency."* This document does not change
`CLAUDE.md`, any charter, any `.claude/` configuration or any board file, and the
author changed none of them.

**Filing note.** `docs/<TOPIC>_PROPOSAL.md` is the lab's established location for
an infrastructure proposal — **seven** precedents on disk `[MEASURED, `ls
docs/*_PROPOSAL.md`, this document excluded]`, and `check_filing.py` R2
(`docs/*.md` is `UPPER_SNAKE`). `docs/proposals/` still does not exist and is
registered in no filing rule; `BOARD_BASE_RULE_PROPOSAL.md` declined to create it
for that reason and this document follows the same precedent.

**Author:** verification-supervisor. **Solver compute: 0 core-min, $0.00.**
**Gates · thresholds · bands · caps · labels changed: 0 · 0 · 0 · 0 · 0.**

---

## 1. The defect, measured

`docs/LAB_STATE.md` is **one file of 34,089 lines** `[MEASURED, `wc -l` at
`6319743d`]` carrying **seven** `## ` sections written concurrently by seven
different agents. The failure this produces is not theoretical: it is the **four
silent section reverts of 2026-08-23** recorded in `BOARD_BASE_RULE_PROPOSAL.md`
§3, and this team's own `UPDATE V-45` — *"I spent the night auditing other teams'
board-keeping and my own board was ten commits stale."*

The current mitigation is a **splice**: `scripts/lab_state_section.py` rebuilds
the file from a committed revision, replaces exactly one `## <team>` section, and
writes the result to scratch so the shared worktree copy is never touched. It is
a good instrument and this proposal keeps its splitter. But a splice is a
discipline applied to a shared write; it does not remove the shared write, and
two of the three instruments built to police that write are — in
`BOARD_BASE_RULE_PROPOSAL.md`'s own words — **"built, committed, wired into
nothing."**

**Section sizes, so the scale of the migration is visible** `[MEASURED, `grep -n
'^## '`]`:

| section | lines | writer |
|---|---|---|
| preamble (no `## ` heading) | 38 | nobody — see §4 |
| `## CHIEF — standing directives in force` | 1,392 | chief |
| `## closure` | 3,409 | closure-supervisor |
| `## dafoam` | 8,415 | dafoam-supervisor |
| `## heat-transfer` | 8,644 | heat-transfer-supervisor |
| `## cfd` | 3,928 | cfd-supervisor |
| `## verification` | 1,804 | verification-supervisor |
| `## ansys-verification` | 6,459 | ansys-verification-supervisor |
| **total** | **34,089** | — |

The seven figures plus the preamble sum to 34,089 exactly; that identity is the
migration's own arithmetic check and it is stated here so a reader can redo it.

---

## 2. What is proposed

**One writable file per writer, and a rollup that is GENERATED and owned by
nobody.**

1. **Seven per-team board files**, each with exactly one writer:
   `docs/LAB_STATE_CHIEF.md`, `docs/LAB_STATE_CLOSURE.md`,
   `docs/LAB_STATE_DAFOAM.md`, `docs/LAB_STATE_HEAT_TRANSFER.md`,
   `docs/LAB_STATE_CFD.md`, `docs/LAB_STATE_VERIFICATION.md`,
   `docs/LAB_STATE_ANSYS_VERIFICATION.md`.

   **Why top-level and not `docs/lab_state/`:** the flat names already satisfy
   `check_filing.py` R2 (`docs/*.md` is `UPPER_SNAKE`) and need **no filing-rule
   amendment**. A `docs/lab_state/` directory is tidier and I would prefer it on
   aesthetics alone, but it is registered in no filing rule, so adopting it
   costs a filing-charter amendment — which is Sanaa's to grant, not mine to
   assume. **Both options are put; the flat one is recommended because it is the
   one that changes no rule.**

2. **`docs/LAB_STATE.md` becomes GENERATED.** Its first lines say so, name the
   seven sources, name the generator, carry the generation time from `date -u`,
   and carry **each source's blob sha** so a reader can tell a fresh rollup from
   a stale one without trusting the header's own timestamp.

3. **`scripts/gen_lab_state.py`** builds the rollup: preamble template, then the
   seven sources in roster order.

4. **`scripts/check_lab_state_rollup.py`** recomputes each source's digest
   against the rollup header and **REFUSES (exit 2)** on mismatch — which is the
   single observable signature of both failure modes that matter: a rollup that
   was hand-edited, and a rollup that is stale because a source moved without
   regeneration.

**The handoff channel does not change meaning.** `CLAUDE.md`'s FIRST-ACTION rule
and every brief point at `docs/LAB_STATE.md`; after this change that path still
resolves to the whole board, and a supervisor still reads its own section first.
What changes is that **writing** it is no longer a shared write.

---

## 3. The guard, and why this proposal names its choke point in advance

A generated file that any agent can still edit, policed by a checker that runs
nowhere, is a **dead lever** — and this lab has at least three of them already:
`check_board_sections.py` and `check_board_reconciliation.py` are both recorded
as *"built, committed, wired into nothing"*, and `check_comparator_freeze.py` is
the constitutional freeze enforcer that, on the reading carried into this
session, **nothing executable invokes** — a claim under re-derivation by this
team at the time of writing and **marked `VERIFY`** rather than asserted, because
a dead-lever count is exactly the kind of figure this lab has twice propagated
without checking. Sanaa's freeze-enforcement ruling of the same day cures that class by
demanding enforcement **at the choke point**, and this proposal is held to the
same standard rather than repeating the pattern in a new file.

**Named choke point:** `check_lab_state_rollup.py` runs **in the same shell
invocation as the board commit**, terminated `|| exit 1`. Not as a hook that can
be absent, not as a report a reader may skim.

**I state this against my own record, because it is my own defect.**
`FAIL_OPEN_GATE_AUDIT` §27.6: I built a foreign-content assert, **it fired**, it
printed its finding in the same invocation immediately before the commit — **and
the commit proceeded, because I wrote `echo` and never wrote `|| exit 1`.** A
guard that reports and does not refuse is `§2p`'s exact shape, and I shipped one
inside the audit file that names the class. **The `|| exit 1` above is not a
detail.**

**Controls required before either script is believed** — the four limbs this
team's own charter now mandates, each tied to the degenerate path it closes:

| limb | clause | the control |
|---|---|---|
| empty input | `§2p.2` | **zero source files → REFUSE.** A board that emits an empty rollup reading *"nothing running"* because its sources vanished is the worst output this tool can produce, and it is the one an unguarded generator gives. |
| planted alternative | `§2o` | plant a **one-byte** edit into the rollup and prove the checker fires; separately, edit a **source** without regenerating and prove it fires. Two failure modes, two plants. |
| positive control | `§2p.3(e)` | a correctly-generated rollup must still **PASS** in the same run. A checker that refuses everything is "strict" in the trivial sense and is indistinguishable, from its verdicts alone, from a correct one. |
| no redundant copy | `§2p.3(d)` | the controls drive the **production** generator and the **production** checker. A test that exercises a copy of the guarded logic tests nothing. |

---

## 4. The migration itself, and the proof that it moved nothing

**Use the production splitter, not a new one.** `scripts/lab_state_section.py`
already implements `split(text, team)` — heading to next `## ` heading or EOF.
The migration calls that function, so the bytes are cut by the same code the lab
has been trusting to cut them for two weeks (`§2p.3(d)`).

**The preamble has no `## ` heading and therefore no owner.** Lines 1–38 are not
any team's section. Making them an eighth writable file would create a file with
no writer — the shape that produces orphaned records. **They become the
generator's header template instead**, so they are regenerated rather than
edited.

**Refuse the migration unless it is byte-identical.** Concatenate the header
template and the seven split outputs and `cmp` the result against
`git show HEAD:docs/LAB_STATE.md`. **Non-zero `cmp` aborts the migration.** This
is `§2p.6.2`'s reference shape applied to the migration: *a repair that cannot
show what it did not move is not finished.* The content edit and the structural
move are **never** in the same commit.

### 4.1 One thing the migration must NOT settle by accident

`UPDATE V-53` records an unresolved question: **a second `UPDATE V-33`/`V-34`
pair exists near the `## ansys-verification` boundary, colliding with this
team's own ids, and whose blocks they are is unsettled.** A line-boundary split
assigns them to whichever section's line range contains them — which would
**silently adjudicate an open ownership question as a side effect of a file
move.**

**Ruled for this proposal:** the split is by line boundary, the disputed pair is
**named explicitly in the migration commit message**, and ownership is
adjudicated **separately, on its merits, afterwards**. A migration is not a venue
for deciding whose record something is.

---

## 5. Honest limits, stated because they bear on the adoption decision

- **This removes the cross-team clobber class entirely** — two writers never
  touch one path again — **and it does not remove L-223.** A lane can still
  `read-tree` a stale HEAD and clobber **its own** file. The post-commit verify
  in `CLAUDE.md` rule 10 remains the only defence against that, and it remains
  not optional.
- **It does not make team attribution verifiable.** Every commit in this
  repository carries one `Ubuntu` identity, so "this file has one writer" is a
  **convention the roster declares**, not a fact git can check. The per-team file
  makes a foreign write **visible in the diff**; it does not make it impossible.
- **It adds a staleness failure mode that does not exist today.** One file cannot
  be stale against itself; a rollup can. That is why the digest check and its
  choke-point wiring are part of the proposal and not a follow-up.
- **The rollup grows a merge surface at generation time.** Two teams committing
  within seconds both regenerate; the loser's rollup is stale until the next
  generation. This is a **benign** staleness — the sources are correct and the
  checker will say so — but it will produce refusals that look like defects, and
  a team meeting one for the first time should be told it is the expected
  behaviour rather than a bug.
- **A stale docstring found while drafting this**, reported rather than fixed
  because `scripts/` is outside this team's folder scope:
  `scripts/lab_state_section.py` line 4 says `docs/LAB_STATE.md` *"is shared by
  five teams."* It is **seven sections** today. The code is correct; its
  description of the world is two teams out of date.

---

## 6. What this proposal asks of Sanaa

| # | question | recommendation |
|---|---|---|
| 1 | adopt per-team files + generated rollup? | direction already approved 2026-09-03; this is the mechanics |
| 2 | flat `docs/LAB_STATE_<TEAM>.md`, or `docs/lab_state/<team>.md`? | **flat** — it needs no filing-rule amendment; the directory form is tidier and costs one |
| 3 | may the generated `docs/LAB_STATE.md` keep that path? | **yes** — every brief and the FIRST-ACTION rule point at it |
| 4 | who writes the two scripts? | `scripts/` is outside this team's scope; **this document is the spec, and the build is referred** — being told the call is mine does not widen my scope (`CLAUDE.md` rule 9) |
| 5 | the disputed `V-33`/`V-34` pair | adjudicated **separately**, never as a side effect of the move (§4.1) |

**Not asked, and deliberately:** no gate, threshold, band, cap or label is
touched by anything above, and no recorded verdict is affected.
