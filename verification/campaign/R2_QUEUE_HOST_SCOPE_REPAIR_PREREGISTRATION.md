# R2 — PRE-REGISTRATION: THE QUEUE-VALIDATOR HOST-SCOPE REPAIR, as a frozen, capped, schedulable REPAIR ITEM

**Team:** cfd. **Owner:** cfd-supervisor. **Registering lane:** cfd lane **REPAIRQ**, 2026-08-28.
**Status at writing: FROZEN ON COMMIT. No code exists. Zero compute has been spent.**

**Authority for registering a repair as a queue item.** Sanaa's amendment of 2026-08-28T17:01Z,
verbatim: *"Freeze-ahead counts repair-registrations; a team blocked on findings freezes the repairs
and runs them — queue depth 0 with open findings is impossible by definition."* Measured by this
lane at 2026-08-28T17:08Z: `verification/queue/cfd/*.json` → **0 entries**.

**The specification this item implements is already frozen and is NOT re-opened here:**
`docs/standards/QUEUE_ENTRY_HOST_SCOPE.md`, frozen at commit
**`ed77957c4e56cd12e1d5d0c620b218805bd4306b`** (2026-08-28T16:33:02Z), verified by this lane to be
an ancestor of HEAD `7959a75ec9719d17c7a337fda6fa32b15b5c7d12`. That document fixes the invariant
(§1), the complete site enumeration (§3), the ruling **candidate (a) — SKIP and report NOT
EVALUATED, never PASS** (§4.2), the ruling that `COMMIT-EXISTS` / `PREREG-AT-COMMIT` stay
**evaluated for every host with the residual named** (§4.3), the two permitted edits to
`queue_runner.py` (§5.4), and the fourteen controls **H1–H14** (§8).

---

## 1. WHAT THIS ITEM IS, IN ONE PARAGRAPH

`scripts/queue_entry_check.py` contains the string `host` **zero times**. Two of its live clauses —
`check_age_guard()` reading the working tree at `:309-310` and `:316-317`, and
`check_cwd_launchable()` reading it at `:348` — refuse an entry whose `cwd` is absent **on this
box**, including an entry declared to run on another box where that `cwd` exists. Because
`queue_runner.py::tick()` validates at `:702` and **physically moves** the file to `<team>/refused/`
at `:703-705` **before** reading `host` at `:707`, that false refusal is an **eviction**, not a
misread number. This item makes the validator host-aware in the one direction the spec ruled, adds
the `NOT EVALUATED` reporting channel, and proves by control that the narrowing did not become a
hole.

## 2. WHAT THIS LANE RE-VERIFIED, AND ONE FIGURE THAT HAD MOVED

Read from the one named file each, this invocation:

- `check_age_guard()` is defined at `queue_entry_check.py:285`; its working-tree reads are the
  `Path(cwd)` / `target.is_dir()` pair and the `target.iterdir()` / `child.is_dir()` loop. Its
  docstring already carries ruling **R-AGE-CWD**: an **absent** `cwd` returns **CLEAN** from this
  clause and is EXEC's finding. **So AGE-GUARD's live host-sensitivity is narrower than the brief
  implies**: on an absent foreign `cwd` it returns `[]` today; it refuses only where the foreign
  `cwd` *exists locally* and holds a time directory — a false refusal about **another box's**
  tree read off **this** box's. Both remain in scope under the spec's §3 ruling, and this
  distinction is registered so the H1 control is read correctly: **H1's `len(unevaluated) == 2`
  limb is the load-bearing one for AGE-GUARD, not a refusal-suppression limb.**
- `check_cwd_launchable()` refuses under the word `EXEC` whenever `Path(cwd).is_dir()` is False.
  **This is the clause that produces the eviction**, and it is the clause the negative control
  must show still bites for a local entry.
- `require_binding_clause()` refuses **only** when the entry file is not in
  `verification/queue/<team>/`, and its own text says the refusal *"is the ABSENCE of a check, not a
  failed one."* This item does not touch it.
- **MEASURED, not inherited:** `python3 scripts/queue_entry_check.py --selftest` returns **rc 0**
  with **31 controls fired**, in **0.53 wall s**, in this invocation. That is the pre-repair
  baseline H14 compares against, and it is the cost basis in §9.

**A FIGURE FROM A SIBLING SPEC THAT HAS MOVED, REPORTED NOT REPAIRED.**
`UNIQUE_SELECTOR_RULE.md` §10 records `scripts/check_filing.py` as **34 violations across 7 rules,
rc 1**, measured earlier on 2026-08-28. **This lane measured 37 violations across 8 rules, rc 1**,
at 2026-08-28T17:11Z. Neither figure is wrong; the tree moved between them. It is recorded here
because a state reading has a shelf life, and because §9's mandatory re-measurement clause below
rests on exactly that principle.

## 3. THE OBSERVABLE — AND IT IS NOT A RICHARDSON QUANTITY

**The observable is the CONTROL OUTCOME VECTOR** `(H1 … H14)`, each element `FIRED` / `HELD` /
`FLIPPED` / `NOT RUN`, as enumerated in `QUEUE_ENTRY_HOST_SCOPE.md` §8 at its freeze commit, taken
together with the two **set-equality** readings of H14.

**Stated explicitly, so it cannot later be asked for:**

- There is **no grid triple**, no refinement ratio `r`, no mesh and no field.
- **NO OBSERVED ORDER OF ACCURACY IS COMPUTED** and none will be reported.
- **NO GCI IS COMPUTED OR QUOTED.**
- `scripts/roache_triple.py` is **not called**. Standing rule 5 is **inapplicable** to this row —
  not waived, not satisfied — because rule 5 grades a row that has a grid triple and this row does
  not have one. The precedent for an ordinal/structural observable is
  `cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md` §4.
- `NOT EVALUATED` is a **validator-clause reporting token**, not a verdict. It never appears on a
  result row and it is deliberately **not** one of the six words of standing rule 1.

## 4. THE REGISTERED GATES — fixed before the work runs

| gate | statement | verdict if met | verdict if not |
|---|---|---|---|
| **G-R2-1 — THE POSITIVE CONTROL FIRES ON THE UNREPAIRED CODE (H10)** | With the host-scope clause removed as a registered mutant, the foreign-host entry driven through a real `tick()` **IS** moved to `refused/`, a `<CASE_ID>.REFUSED.txt` **is** written naming `EXEC`, and `tick()` returns `"REFUSED-ONLY"` | required for **PASS** | **GATE FAIL** — the eviction was never demonstrated end to end, so nothing was shown repaired |
| **G-R2-2 — THE DEFECT STOPS FIRING ON THE REPAIRED CODE (H9)** | Same entry, same real `tick()`, repaired code: the entry is **still at its original path**; `refused/` **does not exist**; `LAUNCH_LOG.tsv` line count **unchanged**; `tick()` returns `"HELD"`; and the runner log contains **both** the `SKIP` line naming the host **and** two `NOT-EVALUATED` lines naming `EXEC` and `AGE-GUARD` | required for **PASS** | **GATE FAIL** |
| **G-R2-3 — SKIPPED IS NOT PASSED (H1 + H4)** | H1: `validate()` returns **no** `EXEC:` and **no** `AGE-GUARD:` failure, and `unevaluated` has **len == 2**, each string containing the declared host. H4: with the `unevaluated` append suppressed, **H1 FLIPS on its `len == 2` limb** | required for **PASS** | **GATE FAIL** — without H4, H1 cannot tell NOT EVALUATED from PASS |
| **G-R2-4 — THE NEGATIVE CONTROL (§6)** | H2, H2b and H2c **all three** refuse | required for **PASS** | **GATE FAIL** |
| **G-R2-5 — THE NARROWING IS NARROW (H5 + H6)** | H5: a foreign-host entry with a nonexistent `prereg_commit` is **REFUSED** with a `COMMIT-EXISTS:` failure. H6: a foreign-host entry with a missing field, a shell-string `launch_cmd` and a contradicting `team` draws **three** failures — two `SCHEMA:` and one `TEAM-BINDING:` | required for **PASS** | **GATE FAIL** — a foreign host became a blanket exemption |
| **G-R2-6 — THE BLIND CALLER REFUSES (H7 + H8)** | H7: `validate()` called without the `unevaluated` argument raises **`TypeError`**. H8: given a `None` default with the appends guarded, **H7 FLIPS** | required for **PASS** | **GATE FAIL** |
| **G-R2-7 — THE OLD PLANT IS SHOWN BLIND (H11 + H12)** | H11: `queue_runner.py` control 6's plant is repaired to an absent `cwd` and its existing assertions still hold. H12: control 6 run with its **original** existing `cwd` **and** the repair removed **PASSES ANYWAY** | required for **PASS** | **GATE FAIL** |
| **G-R2-8 — NOTHING ELSE MOVED (H13 + H14)** | H13: **zero** `ast.Assert` nodes in both instruments, counted by AST. H14: the sorted check-name-plus-status sets of both `--selftest` suites, before and after, **differ by nothing but the rows added here** | required for **PASS** | **GATE FAIL** |
| **G-R2-9 — INVARIANCE** | §7's named set is **bit-identical** | required for **PASS** | **GATE FAIL** |

**PASS iff all nine hold. Any one not holding is `GATE FAIL`.** §8's conditions take precedence.

## 5. THE BIRTH REQUIREMENT — Sanaa directive 1, AS A REFUSAL CONDITION ON THIS INSTRUMENT

Sanaa's directive of 2026-08-28T17:01Z: *"A planted control must travel the real production path —
written by the real producer's code, read through the real reader … no instrument grades anything
until that answer is yes, demonstrated."*

**THE REAL PRODUCER, NAMED.** `scripts/queue_runner.py` — specifically `launch()`, which is the
code that writes a queue entry's committed form: `:515` `launched_dir = path.parent / "launched"`,
`:517` `dst = launched_dir / path.name`, `:520` `shutil.move(...)`, `:536`
`dst.write_text(json.dumps(meta, indent=2) + "\n")` where `meta` is the entry dict plus `_launch`
(`:522`) and `_field_classes` (`:526-535`). **The runner is the producer of an entry's on-disk
form.**

**THE REAL READER, NAMED.** `queue_entry_check.validate(entry, root, entry_path, unevaluated, …)`
— the production function, reached through `queue_runner.py::tick()` at `:702`. **Not a
re-implementation, not a stub, not a dict passed straight to a clause.**

**BR-1 — THE END-TO-END DEMONSTRATION, MANDATORY, AND THE INSTRUMENT REFUSES WITHOUT IT.**

> **H9 and H10 are driven through a real `tick()` on a queue root of PRODUCTION'S SHAPE** —
> `<scratch>/…/verification/queue/<team>/`, the exact shape `QUEUE_ENTRY_TEAM_BINDING.md` amendment
> 2 made mandatory after a control passed vacuously on a flat `c9root/cfd/`. The entry H9 reads is
> **written by the runner's own code path**, not hand-composed: the control drops a valid entry,
> lets `tick()` launch-and-move it so that `launch()` at `:520`/`:536` produces the file, and the
> control then reads **that** file back.
>
> **THE REFUSAL.** Before it grades anything, the driver asserts, in the same invocation:
> (i) the entry H9/H10 operate on was **written by `queue_runner.launch()`** and carries the
> `_launch` and `_field_classes` keys that only `:522`/`:526-535` add — a hand-written entry
> lacking them is refused;
> (ii) the declared `cwd` is asserted **absent locally** by `Path(cwd).exists() is False`
> **before** the call, so the clause under test can actually reach its refusal branch — this is the
> exact repair of the blind plant that H11/H12 measure in `queue_runner.py` control 6, whose
> `good3` inherited an **existing** `cwd` and could therefore never reach EXEC;
> (iii) **H10 fires first**: the pre-repair mutant must be observed **evicting** the entry — file
> moved to `refused/`, `REFUSED.txt` written, `tick()` returning `"REFUSED-ONLY"` — before the
> repaired run is allowed to report that it does not.
> **If any of (i)–(iii) fails the driver exits 2 and grades NOTHING.**

**WHY A HAND-COMPOSED ENTRY IS REFUSED, in this document's own words.** An entry dict assembled by
the test is a schema the producer never emitted; grading against it would certify that the
validator can read the test's idea of an entry. Sanaa's directive names this exact failure. And a
control whose `cwd` exists cannot reach the clause it claims to test — **the plant, not the
assertion, is where blindness lives**, which is precisely what H12 turns from a sentence into a
measurement.

**THE RESIDUAL, NAMED RATHER THAN DISCOVERED LATER.** `QUEUE_ENTRY_HOST_SCOPE.md` §4.3 accepts one
real false refusal: a pre-registration committed on the other instance and **not yet fetched into
this box's object store** draws a `COMMIT-EXISTS` refusal here and **is evicted** under the §2
ordering. This item does **not** fix that, deliberately — fixing it means making the freeze guard
host-conditional, which is a change to the invariant. The mitigation is procedural and belongs in
the enqueue procedure: the freeze is fetched into this repository before the entry is filed.

## 6. THE NEGATIVE CONTROL — the repair did not disable the thing it repaired

A **narrowing** is the dangerous direction. Three fixtures, all mandatory, all through the real
`validate()`:

| id | fixture | required outcome |
|---|---|---|
| **H2 — `host` absent** | the same entry dict, `host` key **removed**, identical absent `cwd` | failure list contains **exactly one** string starting `EXEC:`, containing the literal `cwd` value; `unevaluated` is **empty** (`len == 0`) |
| **H2b — `host: "local"`** | as above | identical requirement |
| **H2c — `host` = `os.uname().nodename`** (measured this invocation: `ip-172-31-43-247`) | as above | identical requirement |

**All three are required.** The host-equality set at `queue_runner.py:708` has three accepting
forms and a repair honouring only one would pass a single-form control. H3 mutates the host-scope
predicate to return "foreign" unconditionally and **H2 must FLIP** — a local entry that stops
drawing `EXEC` proves H2 was testing the predicate and not something incidentally in the way.

**This is the negative control the brief demands in its own terms: a LOCAL-host entry with an
absent `cwd` STILL REFUSES under `EXEC`.**

## 7. THE INVARIANCE SET — BIT-IDENTICAL, checked by hash

Hashed (`sha256`) before and after; any difference is `GATE FAIL` under G-R2-9, with the path
printed.

1. **Every file under `verification/queue/`** — every team directory, every `held/`, every
   `launched/`, `LAUNCH_LOG.tsv`, and the runner's own logs. **Nothing real is touched**; every
   control runs in a `tempfile` tree. This set is what proves it.
2. `docs/standards/QUEUE_ENTRY_HOST_SCOPE.md`, `docs/standards/QUEUE_ENTRY_TEAM_BINDING.md`,
   `docs/standards/QUEUE_ENTRY_VALIDATOR_RULINGS.md`, `docs/standards/QUEUE_ENTRY_STANDARD.md` —
   frozen standards; rule 6.
3. This document.
4. `scripts/queue_runner.py` **outside the two permitted edits of §5.4** — the file's diff against
   HEAD must consist of exactly (a) one additional argument at `:702` plus the list constructed
   immediately above it, and (b) one loop emitting `NOT-EVALUATED` lines immediately after. **Any
   third hunk is `GATE FAIL`.** The diff is read as a diff, by the supervisor, under
   `SUPERVISION_CHARTER.md` §3 check 1 — which a lane cannot discharge.

**The live daemon.** `scripts/queue_runner.py --daemon` was running as **pid 1120800** at
2026-08-28T17:1xZ, elapsed 23:36:34. **This item must not restart, signal or race it.** The driver
touches no file under `verification/queue/` (clause 1) and starts no daemon; if
`verification/queue/runner.pid` names a live process at driver start, the driver records that fact
and proceeds only in its scratch trees. **A repair to the validator does not entitle anyone to
bounce the runner**, and any restart is the supervisor's decision, not this item's.

## 8. CRITERIA — how the verdict is reached, in order

1. **BLOCKED** if §11's enqueue preconditions are unmet at launch. Nothing is graded.
2. **NOT A RESULT** if BR-1 refuses (exit 2) — the instrument was never shown able to see the
   eviction through the real code path.
3. **NOT A RESULT** if the driver's completion clause fails: rc != 0, no terminal record line, or
   any of H1–H14 reported `NOT RUN`.
4. **GATE FAIL** if any of G-R2-1 … G-R2-9 is not met, naming which.
5. **PASS** iff all nine are met and none of 1–3 applies.

**No partial credit, no degraded reading** (rule 4).

## 9. COST, CAP AND CALIBRATION — rule 12

### 9.1 The basis, term by term, each labelled MEASURED or ALLOWANCE

`ranks = 1`. Core-minutes = wall s × ranks ÷ 60.

| term | wall s | basis |
|---|---|---|
| a) `queue_entry_check.py --selftest` × 3 — the pre-repair baseline for H14, the post-repair run, and the `-O` run at H13 | 1.6 | **MEASURED.** One run took **0.53 wall s**, rc 0, 31 controls, in this invocation. |
| b) the new rows H1–H8 added to that suite | 2.0 | **ALLOWANCE**, on the measured per-control rate of 0.53 s ÷ 31 ≈ 0.017 s, carried generously because H1/H2/H2b/H2c each construct a `tempfile` production-shape tree. |
| c) `queue_runner.py --selftest` × 2 — pre and post, carrying H9/H10's real `tick()` and H11/H12's control 6 | **40.0** | **ALLOWANCE — NOT MEASURED, AND THIS LANE DECLINES TO MEASURE IT.** A `queue_runner.py --daemon` is live as pid 1120800; CLAUDE.md's *"do not touch running solvers"* and the fleet-invisibility of that process make invoking the runner's own selftest from a registering lane the wrong risk to take for a cost figure. **This is the single largest term and it is a guess. It is labelled as one.** |
| d) H9/H10's end-to-end ticks and §9.2's mandatory blast-radius re-measurement sweep | 5.0 | **ALLOWANCE.** |
| **TOTAL** | **48.6** | |

### 9.2 THE ESTIMATE, THE CAP AND THE RATIO

| | value |
|---|---|
| **cost_core_min_estimate** | **0.8100** core-min (48.6 wall s × 1 rank ÷ 60) |
| **cap_core_min_registered** | **1.2000** core-min |
| **cap / estimate** | **1.4815** |
| dollars at the estimate | **$0.000693** — **DERIVED, NOT MEASURED** |
| dollars at the cap | **$0.001026** — **DERIVED, NOT MEASURED** |

Rate **$0.0513 per core-hour**, c7a.4xlarge, **owner-stated and reported-by-owner, never
measured** (`COMPUTE_BUDGET_CHARTER.md` §5).

**HOW THE CAP IS ENFORCED, and it is never raised.** The cap converts to a wall allowance of
**72.0 s** at 1 rank, handed to `timeout` **around term (c)** — the only unmeasured term. An
overrun **kills the step and STOPS the item**, leaving the controls incomplete, which §8 clause 3
grades **NOT A RESULT**. **The correct response to term (c) proving larger than 40 s is a NOT A
RESULT and a re-registration with a measured basis — not a new budget.**

**MANDATORY RE-MEASUREMENT AT IMPLEMENTATION.** `QUEUE_ENTRY_HOST_SCOPE.md` §9's blast-radius table
dates from before the code was written and the spec itself requires it re-run **in the same shell
invocation that lands the code**, with the fresh counts recorded. This registration adopts that
requirement as a gate condition of the record: **a completion record that carries §9's stale counts
rather than fresh ones is incomplete.** The counts to re-derive: entries carrying a `host` field;
of those, foreign vs local; foreign-host entries whose `cwd` exists locally; foreign-host entries in
a globbed drop path; `refused/` directories existing; entries ever refused lab-wide.

### 9.3 CALIBRATION AT COMPLETION (rule 12's calibration clause)

At completion: actual core-minutes from the driver's own log, gross and cleaned separately; waste
named separately and never absorbed into the ratio; the ratio actual/predicted against **0.8100**;
the gap attributed to contention, waste or misprediction — **and, because term (c) is a guess, the
attribution must say explicitly how much of any gap is term (c)'s misprediction**; dollars
**derived, not measured**. A row lands in **`docs/COST_CALIBRATION.md`**. **A completion report
without this comparison is incomplete.**

## 10. RULE-2 ABSENCE CONDITION, CHECKED IN THIS WRITING INVOCATION

**`/home/ubuntu/Certonomous/verification/runs/TOOLING_REPAIRS` DOES NOT EXIST at
2026-08-28T17:12:20Z**, and neither does its child
**`/home/ubuntu/Certonomous/verification/runs/TOOLING_REPAIRS/R2_QUEUE_HOST_SCOPE_2026-08-28`**.
Checked **four ways** each in that invocation: `os.path.exists` → **False**; `os.path.lexists` →
**False**; `os.path.isdir` → **False**; `glob` on the literal path → **[]**. A fifth, wider check:
`glob('verification/runs/TOOLING*')` → **[]**.

**`/home/ubuntu/Certonomous/scripts/run_r2_host_scope_repair.sh` DOES NOT EXIST**, checked the same
four ways at the same instant.

**Additionally, and this is the clause that dates the defect as still latent:**
`find verification/queue -maxdepth 2 -name refused -type d` returns **nothing** — **zero `refused/`
directories exist under any team**, so **zero entries have ever been refused lab-wide** and there is
nothing for this repair to back-fill. **0.000 core-min have been spent under this registration.**

Amendments **before** first compute remain legal under rule 2 and must state this condition and how
it was checked, naming the directory that does not exist. After first compute the gates are closed
and changes land only as dated addenda that cannot alter a gate, threshold, cap or label.

## 11. LAUNCH SHAPE — for the supervisor's check 4; **NOT an authorisation**

    bash /home/ubuntu/Certonomous/scripts/run_r2_host_scope_repair.sh \
         --prereg-commit=<the sha of THIS document's adding commit>

The driver **fires nothing without `--prereg-commit`**, verifies the sha is a commit in this
repository, and verifies that `docs/standards/QUEUE_ENTRY_HOST_SCOPE.md` at
`ed77957c4e56cd12e1d5d0c620b218805bd4306b` hashes to the blob it was frozen as.

**ENQUEUE PRECONDITIONS — four, and the queue validator checks NONE of them.**

1. `scripts/run_r2_host_scope_repair.sh` **exists** at the absolute path above. The validator does
   **not** check `launch_cmd[1]`; an entry naming an absent script validates cleanly and then dies
   at launch behind a LAUNCHED record — the L-344 class.
2. `bash scripts/run_r2_host_scope_repair.sh --selftest` returns **rc 0**, and the driver's python
   entry point under `python3 -O` returns **rc 2**.
3. The two permitted `queue_runner.py` edits (§5.4 of the spec, §7 clause 4 here) are read **as a
   diff** by the supervisor personally. `SUPERVISION_CHARTER.md` §3 check 1 — measurement-script
   diffs read as diffs — may never be delegated, and a lane's control result is not that check.
4. The `prereg_commit` placeholder in the held queue entry has been replaced with the real sha.

**A REFERRAL THIS LANE DOES NOT RESOLVE, carried forward from the spec's own head matter.**
`QUEUE_ENTRY_HOST_SCOPE.md` refers to the chief the question of whether **narrowing** a validator
refusal is a tooling ruling of the kind `QUEUE_ENTRY_VALIDATOR_RULINGS.md` already carries, or an
**amendment to `QUEUE_ENTRY_STANDARD.md`** — which is Sanaa's alone. **This registration does not
answer it and does not route around it.** If the chief rules it an amendment, this item becomes
`BLOCKED` on the same footing as R3 and its verdict is that word, not prose.

A queue entry is drafted at `verification/campaign/queue_entry_R2_QUEUE_HOST_SCOPE_REPAIR.json` and
is **HELD beside this registration. THIS LANE DOES NOT ENQUEUE IT and has committed nothing.**
**Enqueueing is not authorisation.**

## 12. WHAT IS **NOT** CLAIMED, REGISTERED OR AUTHORISED HERE

- **No verdict of any existing rung is re-graded**, in any team. Nothing has ever been refused by
  this validator (§10), so there is nothing to revisit.
- **No frozen comparator is edited.** `queue_entry_check.py` is live cfd tooling, not a
  pre-registration's frozen grading path; `queue_runner.py` is edited in exactly two places and the
  invariance set of §7 is what bounds it.
- **No gate, threshold, cap or label of any other registration is added, moved or removed.** No
  verdict-vocabulary word is added or retired; `NOT EVALUATED` is a clause-reporting token and never
  a verdict (§3).
- **The validator is not made to contact another host.** `_git()`'s read-only allowlist
  (`cat-file`, `rev-parse`, `ls-tree`) is unchanged and no subcommand is added to it. Candidate (c),
  ssh, was REFUSED by the spec and is not reopened.
- **The runner's decision order is not changed**, nor its refusal routing, round-robin, GPU clause
  or cap watch. The spec argued the reordering both ways and ruled **NO**.
- **`enqueued_by` is not checked or enforced.** Every process on this box shares one Ubuntu
  identity, so a check on it would return PASS for any string an agent chose while looking like an
  authorisation control.
- **No observed order and no GCI is produced** (§3); `roache_triple.py` is not called.
- **The live daemon is not restarted, signalled or reconfigured** (§7).
- **Nothing is sent, filed, uploaded, registered, posted or submitted** (rule 7). Submissions are
  PARKED.

---

*Registration ends. Written before implementation; the commit that lands it is the freeze.*

---

## DRAFTING NOTE — 2026-08-28T17:1xZ, BEFORE THE FREEZE, BEFORE ANY COMPUTE

**HEAD MOVED WHILE THIS DOCUMENT WAS BEING WRITTEN.** At this lane's first read HEAD was
`7959a75ec9719d17c7a337fda6fa32b15b5c7d12`; on completion it was
`83cb13dabdba2a053ccd2e3d0a1af226ccb151a9`. Peers commit constantly, and a HEAD sha quoted in a
document has a shelf life. **Re-verified in the closing invocation: all three of
`ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6`, `ed77957c4e56cd12e1d5d0c620b218805bd4306b` and
`7959a75ec9719d17c7a337fda6fa32b15b5c7d12` are ancestors of the new HEAD.** Every ancestry claim
above therefore still holds; only the reference point moved. **The supervisor re-derives the freeze
sha at the freeze, from `git log --diff-filter=A -- <this path>`, never from a subject line.**

**This lane committed nothing and staged nothing.** All six artifacts of this item — three
registrations and three held queue entries — stand as **untracked** working-tree files. The shared
git index was not touched, no `git add` of any form was issued, and `refs/heads/main` was not moved.

**Filing, measured before and after in this invocation:** `python3 scripts/check_filing.py` returned
**37 violations across 8 rules (rc 1)** before these files were written and **35 violations across 8
rules (rc 1)** after. **These six files contributed ZERO violations**; the decrease of two is a
peer's removal of `cases/F17c_kovasznay_floor/STATUS.F17c_KV40_FLOOR` and
`cases/F17c_kovasznay_floor/launcher.queue.out` under `R6-RUNARTIFACT` and is **not** this lane's
doing. Stated with its attribution because an improvement claimed by the wrong agent is a false
record in the cheap direction.
