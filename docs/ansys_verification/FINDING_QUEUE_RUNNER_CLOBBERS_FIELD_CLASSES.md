# FINDING — `queue_runner.py` SILENTLY DISCARDS AN AUTHORED `_field_classes`, AND THE LOSS CAN ONLY EVER LOOSEN A GATE

**Team:** ansys-verification. **Written by the supervisor personally** as `SUPERVISION_CHARTER` §3 check 1
(a measurement-adjacent script read **as source**, not relayed) and check 3 (a big claim defended against its
own evidence before being repeated upward). **Date:** 2026-08-31. **Zero compute.**

> **THE HEADLINE, AND THE HALF THAT EXONERATES US IS STATED FIRST BECAUSE IT IS THE HALF I CHECKED HARDEST:**
> **no landed ansys credential is affected.** The defect is real, it is total in scope, and it did **not** reach
> any grading. Reporting it as a credential problem would have been the more dramatic and the false claim.

---

## 1 — What was measured

While inspecting uncommitted state in this team's territory I found four queue entries deleted from the queue
root with untracked counterparts under `launched/`. They are **moves, not losses** — every key of the HEAD
queue-root blob survives into the `launched/` copy, verified key-by-key on all four
(`VMFL033-R2`, `VMFL038`, `VMFL063`, `VMFL069-R2`).

**But `_field_classes` had CHANGED in three of the four, and it changed in one direction: from a
case-specific declaration to a generic template.** That block is what a grader uses to split
`physics_critical` from `infrastructure`, and under L-342 (Sanaa's universal rule, 2026-08-26)
**only a `physics_critical` field may produce `NOT A RESULT`.** A field quietly demoted out of that list
can no longer refuse a run.

### What was discarded, verbatim in substance

| entry | authored `physics_critical` content the runner discarded |
|---|---|
| `VMFL033-R2` | `MESH_BIRTH_CERTIFICATE.txt` radii, **read back from OpenFOAM's own `C` field** |
| `VMFL063` | `birth_certificate.json` **per level, minted from that level's own `checkMesh`** |
| `VMFL069-R2` | the named fields `U, p_rgh, alpha.fluid1, Cx, Cy` at `endTime`, **`U` at the plateau time**, and the `ExecutionTime count == Time-line count` conjunct |

`VMFL069-R2` additionally lost the closing sentence of its own `rule` string —
*"Bookkeeping never voids physics (Sanaa, universal rule 2026-08-26)"* — which the runner's template does not carry.

---

## 2 — The time order, which is what decides innocence

The innocent explanation is that the queue-root copies were enriched *after* the runs, and the `launched/`
copies faithfully record what was in force at launch. **Measured, and it is false in all three cases:**

| entry | authored `_field_classes` committed | launch (`_launch.utc`) | authored **before** launch by |
|---|---|---|---|
| `VMFL033-R2` | `9f7056d7`, 08-31 16:31 | 2026-08-31T16:31:56Z | same minute |
| `VMFL063` | `a40dd270`, 08-28 16:55 | 2026-08-28T17:41:40Z | **46 min** |
| `VMFL069-R2` | `fd7afc1c`, 08-30 23:50 | 2026-08-30T23:51:22Z | ~1 min |

**The richer declaration existed in the committed queue entry before the runner ever read it.** The runner
overwrote it.

---

## 3 — The mechanism, read as source and not inferred from behaviour

`scripts/queue_runner.py`, launch path:

- `:549` — `meta = dict(entry)` copies the authored entry, **including any authored `_field_classes`**;
- `:555` — `meta["_field_classes"] = dict(...)` is an **unconditional assignment**. Not a merge, not a
  `setdefault`, no `if "_field_classes" not in meta` guard. Whatever the author declared is gone;
- `:556-563` — the fixed template that replaces it, whose `physics_critical` is two generic strings;
- `:564` — the clobbered record is written to `launched/`.

`scripts/queue_runner.R5_CANDIDATE.py` carries the identical code at the identical lines.

**A note against my own case, because the adjacent line looks like a second defect and is not.** The runner's
self-check at `:934-935` asserts the launched record's `physics_critical` contains `"STATUS.SELFTEST_OK"`,
which the template at `:556` never writes — it writes `f"STATUS.{case_id} …"`. That is **consistent, not
broken**: the check runs under a selftest whose `case_id` *is* `SELFTEST_OK`. I checked this before including
it, and it is not part of the finding.

---

## 4 — Scope: total, and measured rather than sampled

- ansys queue-root entries ever committed: **8**
- of those, entries that authored a `_field_classes`: **3** (`VMFL033-R2`, `VMFL063`, `VMFL069-R2`)
- of those 3, overwritten: **3**
- `launched/` records on disk: **13** — carrying the generic template: **13**; carrying anything else: **0**

**The runner has never once preserved an authored declaration.** The overwrite rate is 100 %.

---

## 5 — Why the credentials nevertheless STAND

**No ansys comparator reads the queue JSON.** Measured: a repository-wide search for any `.py` under
`cases/ansys_verification/` or `scripts/` referencing `queue/ansys-verification` returns **zero files**. This
team's frozen comparators grade from the run root directly, and `_field_classes` in a queue entry is, for
ansys, **documentation of the split rather than the executable split.**

Therefore **row #46 (`VMFL069-R2`) and row #48 (`VMFL033-R2`) were not graded against the weakened list**, and
neither was `VMFL063` (row #44). **No row moves, none is re-graded, and no verdict is disturbed.** This is a
bookkeeping defect in the launch record, and **bookkeeping never voids physics.**

---

## 6 — Why it is still worth a finding, and why the direction matters

**Other teams' graders DO read `_field_classes`.** Measured: `cases/F17_kovasznay/grade_f17.py`,
`F17b`, `F17c`, `F18`, `F18b`, `F19_SOD`, `F20_ISENTROPIC_VORTEX`, `F21_womersley`, `F22_lamb_oseen`,
`F23_HP_WEDGE`, `F24_PRANDTL_MEYER`, `F25_DUCT3D`, `F27_WOMERSLEY_PIPE` and `scripts/r2_host_scope_driver.py`
all reference it. **Wiring an ansys grader to read it is the natural next step and would be the correct
design** — and on the day someone does, it will read the boilerplate and not the declaration.

> **THE ASYMMETRY IS THE POINT. The overwrite replaces a longer, case-specific `physics_critical` list with a
> shorter generic one. It can therefore only ever DEMOTE a field out of the refusing set — it can loosen a
> gate and it can never tighten one.** A silent default that fails in the permissive direction is the wrong
> default. Had the template been the *superset*, this would be a curiosity; it is the subset, so it is a
> hazard.

An author who writes a careful case-specific declaration currently has **no way to know it was discarded** —
the queue entry they committed still shows it, and only the `launched/` copy carries the loss.

---

## 7 — Disposition

**REPORTED, NOT REPAIRED.** `scripts/queue_runner.py` is **not this team's territory** and I have changed
nothing in it, proposed no patch and touched no line. The same discipline as the `§2h.6` label collision:
their script is theirs. Routed via the chief.

**The suggested repair is one line and is theirs to accept or refuse:** merge rather than assign — preserve an
authored `physics_critical`/`infrastructure` and union the template into it, or at minimum refuse to launch an
entry whose authored declaration would be discarded. **Either is a change to a measurement-adjacent script and
needs its owner's read, not mine.**

**For this team, prospectively:** an ansys pre-registration that wants a case-specific physics-critical set
must put it **in the frozen comparator**, where it is executable and cannot be overwritten — **not in the
queue entry, where it is advisory and is in fact discarded.** The three entries above were written in good
faith into a field that does not survive.

**The authored text is not lost and is citable:** it stands in the committed queue-root blobs at
`git show 9f7056d7:verification/queue/ansys-verification/VMFL033-R2.json`,
`git show b7bed168:verification/queue/ansys-verification/VMFL063.json` and
`git show fd7afc1c:verification/queue/ansys-verification/VMFL069-R2.json`.

**VERIFY (stated, not filled in):** I have not established whether the *other* teams whose graders read
`_field_classes` launch through this same runner. If they do, the finding reaches their gates **executably**
and is materially more serious there than here. That check belongs to the runner's owner and I have not made it.
