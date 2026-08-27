# The fail-open gate sweep — what was found, and what was not

Docket item **B2**. Fleet agent, 2026-08-11. The frame for this sweep is
`docs/FAIL_OPEN_GATE_POPULATION.md`, written before the sweep and committed at
`aeafa3db` so the sweep could not choose its own denominator.

**Scope:** the population in that document **minus `scripts/self_audit.py`**,
which the V16 agent held for the duration. Its 17 sites re-enter the population
when V16 closes.

The question this sweep had to answer, per site, is the frame's and not a
broader one:

> When this `except` fires, does the swallowed surface still count toward a
> verdict that gets **published** — as agreement, as absence, or as zero?

---

## 1. The positive control, first, because it gates everything after it

A sweep that returns "few or no fail-open gates" is worth nothing unless it was
shown capable of finding one.

**Control:** `scripts/self_audit.py::check_board_placement_words` at
`038b36da`, read out of git rather than reproduced by hand, is a known-positive
instance of the exact shape.

**Result: FLAGGED.** The method flags the exact handler — the
`except Exception` that did `unreadable += 1; continue` — and reports the
discriminating fact about it: `unreadable` is written by the handler and is
**not** among the names the verdict's status can depend on.

```
POSITIVE CONTROL  scripts/self_audit.py@038b36da::check_board_placement_words
  line  1355  except OSError             writes=-              moves_verdict=-  FLAGGED
  line  1362  except UnicodeDecodeError  writes=-              moves_verdict=-  FLAGGED
  line  1373  except Exception           writes=['unreadable'] moves_verdict=-  FLAGGED
  -> FLAGGED (3 of 3 shape site(s) in that function)
```

**Negative control, and the positive is worthless without it:** the *repaired*
version of the same function, in the working tree, is **cleared** — its handler
records into `skipped`, and `if skipped:` reaches the status. A method that
flagged everything would pass the first half of this control and mean nothing.

```
NEGATIVE CONTROL  scripts/self_audit.py (working tree)::check_board_placement_words
  -> the repaired handler records into a name the verdict consults: True

CONTROL PASSED in both directions.
```

Re-runnable: `python3 scripts/fail_open_scan.py --control`, non-zero exit if
either direction fails. It runs on every suite pass via
`sdk/tests/test_fail_open_scan.py`.

**Building the instrument caught one defect in the instrument.** The first
draft counted only `=` and `+=` as recording a skip, so `skipped.append(...)`
— the idiom the real repair uses — read as recording nothing, and the **fixed**
code flagged. The negative control is what found that. A method calibrated only
on the positive would have shipped inverted.

### The stale-bytecode hazard, and why it does not invert this sweep

Docket **D1/D1a** records that a mutation test in this lab returned a perfectly
inverted matrix from a stale `__pycache__` entry: Python's timestamp
invalidation compares `int(st_mtime)` — whole seconds — plus size, so a
length-preserving edit inside one second matches both halves of the key.
`PYTHONDONTWRITEBYTECODE=1` **does not fix it** — it stops Python *writing* a
`.pyc`, not *reading* one that already exists.

This is load-bearing here rather than incidental, because the whole method
rests on injection, and **the failure direction is a false negative**: if a
stale module served the un-injected code, the gate would report its normal
verdict and a real fail-open would be classified as safe.

Three things bound that risk, and they are stated so a reader can check them
rather than take them:

1. **The scan itself never imports what it scans.** It reads source text and
   walks the AST. Both controls likewise: the positive control comes from
   `git show 038b36da:scripts/self_audit.py` as a **string**, and the negative
   control reads the working-tree file as text. No bytecode is involved at any
   point in the control, which is the part a stale cache would most quietly
   corrupt.
2. **No site in this sweep was cleared BY an injection that came back
   negative.** Injection was used only in the positive direction, to
   **confirm** the two defects and candidate C7. Of the 13 out-of-scope sites,
   **3 were afterwards fired at on a cold cache and stayed clean** and **10 are
   cleared by static argument and were never fired at** — split out in §5,
   because "could not make it fire" and "never fired at it" look identical in
   the output. The 7 candidates are recorded as *not shown to fire*, which is
   the opposite of a clean bill.
3. **Both injections are patch-based, not source-mutating, and each asserts
   that it bit.** They use `unittest.mock.patch` against live module objects,
   so no `.pyc` can serve an un-injected version. Defect 1's run reports
   `STALE BYTES UNCHANGED: True` — direct filesystem evidence the `unlink` was
   really refused; defect 2's before-and-after runs produce *different record
   keys*, which cannot happen if the same code ran twice. Both were re-run with
   every `__pycache__` in the tree deleted and `PYTHONPYCACHEPREFIX` pointed at
   a fresh directory, and both reproduce. The shipped tests carry the same
   bite-assertions (`"the injection did not bite"`), so a future stale cache
   reddens the suite instead of quietly passing it.

### What the method is

For each `except` handler whose body swallows (only `pass`/`continue`/`break`,
or ending in one within three lines):

1. find the enclosing function `F`;
2. does `F` **emit a verdict** — a `Result(...)`/status-token return, a
   `sys.exit`, a status-carrying `print`, an assignment to
   `status|verdict|ok|passed|clean|result|gate`;
3. compute **guard names** — every name the *choice* of verdict can depend on:
   names in `if`/ternary/`while`/`assert` tests in `F`, plus names in the
   **status position** of a verdict emission. Names appearing only in **text**
   (a summary, a detail line, an f-string) do **not** count;
4. compute **swallow writes** — names the handler assigns, augments, or mutates;
5. **flag** when `F` emits a verdict and swallow-writes ∩ guard-names is empty.

Step 3 is the whole method. The known positive **did** record its skip — in the
frame line — and still shipped a green STATUS. Recording a skip in prose is not
a third verdict.

**A flag is a CANDIDATE, not a defect.** Only injection settles one.

---

## 2. The counts, with frame and filter and commit

**Frame:** tracked files only, `git ls-files '*.py'`. No count here comes from
`grep -r`, which in this environment execs `ugrep --ignore-files` and would have
silently excluded gitignored paths (**L-75**). Files that will not parse are
reported as `UNPARSED` and counted; there were none.

Measured **before** this sweep's fixes, at `85cc1078`:

| Quantity | Count |
|---|---|
| Tracked `.py` files scanned (excluding `self_audit.py` and the scanner) | **475** |
| Files that would not parse (`UNPARSED`) | **0** |
| Fail-open **SHAPE** sites | **145** |
| …in a function that emits a verdict at all | **32** |
| …**FLAGGED** (verdict emitted, swallow cannot move it) | **32** |

Measured **after** the fixes, at `bfbf0523`: 481 files, 0 UNPARSED, **135**
shape sites, **20** flagged. The tree moved under this sweep — other agents
committed while it ran — so the two file counts are not the same denominator
and are not differenced here. The flag count fell by exactly the twelve sites
fixed below.

### The headline, and it is not a large number

**113 of the 145 shape sites — 78% — are in functions that emit no verdict at
all.** They cannot reach a published verdict by any path, so they are out of
scope by construction, and saying so is a result rather than a gap.

Of the 32 that survived that filter, after reading and injection:

| Classification | Sites |
|---|---|
| **Demonstrated defects** — injection fired, published verdict was wrong | **12** |
| **Candidates** — plausible, could **not** be made to fire | **7** |
| **Out of scope** — the exception path cannot reach a published verdict | **13** |

**Most uses of this shape in this repository are correct**, and that is the
honest finding. Skipping a binary, tolerating a missing optional field, and
handling a path that vanished mid-walk are all legitimate, and reporting the
145 or the 32 as "fail-open gates" would be the count-inflation error this lab
already recorded as **L-67**.

---

## 3. Demonstrated defects

### Defect 1 — ten acts published a certificate withdrawal that never happened

**12 sites → 11 of them here**, across eight workflows. Commit `cec0fa09`.

Every act in `sdk/workflows/` opened its certificate block with

```python
try:
    cert_path.unlink()
except OSError:
    pass
```

and then published, with no condition attached:

> "The previous run's certificate is withdrawn, so nothing out of date is
> served."

**The injection**, on shipped code, run through `workflows.valve_study.main`:
plant a certificate from an earlier mission in the act's output directory, make
`Path.unlink` raise `PermissionError`, make `build_certificate_v2` raise so no
new page lands on top, and run the act.

**Before the fix**, the published transcript read:

```
CHIEF ENGINEER: • No certificate could be issued for this run. • The previous
run's certificate is withdrawn, so nothing out of date is served. • The result
above stands on the transcript and the report.

PUBLISHED CLAIM PRESENT: True
STALE CERTIFICATE STILL ON DISK: True
STALE BYTES UNCHANGED: True
```

An earlier mission's certificate, byte for byte on disk, under a camera-facing
line saying it had been withdrawn.

**After the fix**, the same injection publishes:

```
CHIEF ENGINEER: • No certificate could be issued for this run. • The previous
run's certificate COULD NOT be withdrawn (PermissionError: injected: read-only
medium), so an out-of-date page may still be served. Treat any certificate at
that address as belonging to an earlier run until it is removed by hand.
```

**Why two outcomes looked like enough for so long**, and why the fix is not
"warn on failure": on nearly every run there is **no previous page at all**,
`unlink` raises `FileNotFoundError`, and swallowing it is **correct** — nothing
stale is served either way. A fix that warned on every run would be switched
off within a week and would then be guarding nothing. So
`workflows.withdraw_certificate` returns *withdrawn* for both the removed case
and the nothing-there case, and speaks only for the third.

`sdk/workflows/aircraft_optimization.py`'s infeasible path is the sharpest of
the eleven: it has **no later certificate build** to overwrite a page the
unlink could not remove, so there the swallowed failure is the whole story.

**Test:** `sdk/tests/test_certificate_withdrawal.py`. It injects the raise and
asserts the published verdict is not a clean claim, carries the positive
control that a real withdrawal is still published as one, and **derives** the
act set from the source rather than listing it — an act added tomorrow that
claims a withdrawal without earning it fails the suite.

### Defect 2 — the mesh recheck dropped unreadable certificates out of its own denominator

**1 site.** `demo-output/website/campaign/MESH_CERT_RULINGS_2026-08-10/recheck_95.py:45`.
Commit `f847673d`.

```python
for p in RUNS.rglob('birth_certificate.json'):
    try: d = json.loads(p.read_text())
    except Exception: continue
```

The record it writes publishes `total`, `agree`, `drift`,
`checkMesh_did_not_run` and `points_hash_mismatch`. **None of those buckets was
"could not be read."**

**The injection:** two retrospective birth certificates in a throwaway runs
tree, one truncated mid-JSON, `checkMesh` stubbed to a clean log.

```
certificates on disk: 2
retrospective certificates: 1

PUBLISHED RECORD:  total: 1   agree: 1   drift: 0   checkMesh_did_not_run: 0
Does the published record mention the unreadable certificate at all? False
```

A hundred per cent agreement over a population silently one smaller than the
directory it claimed to sweep. After the fix the same injection reports
`certificates_found: 2`, `certificates_unreadable: 1`, the file named in
`unreadable_rows`, a `frame` line stating the denominator, and a non-zero exit.

**The fix is in the idiom the script already had.** One level in, the script
already refuses this exact error: *"A checkMesh that did not run states no cell
count… Never call that agreement,"* with `checkMesh_did_not_run` as its own
bucket. The repair is that bucket's twin at the population level.

**What this does NOT say.** The committed `recheck_95_record.json` is **not**
wrong. The population was independently re-counted against the tree on
2026-08-11 — **127** birth certificates on disk, **0** unparseable, **95**
retrospective — which is exactly the number it published. The blind spot did
not bite that run. The finding is that **the run could not have told anyone
either way**.

**Test:** `sdk/tests/test_recheck_population.py`, including a positive control
that a clean population still exits zero and reports zero unreadable, and a
regression that the inner third verdict still works.

---

## 4. Candidates — plausible, and I could not make them fire

Each of these is labelled a candidate because **I did not produce a wrong
published verdict from it.** None is fixed. Filed, per R-CONVERGE.

| # | Site | Why it is plausible | What would settle it |
|---|---|---|---|
| C1 | `sdk/chief_engineer/head_engineer.py:1084` | `except Exception: pass` around `line_hook(line)` — "telemetry must never take down a solve". An all-failing hook empties a published live chart with no marker on it. | A run with a raising hook; needs WSL + OpenFOAM, which this sweep may not launch. The step verdict itself comes from the process exit status, which the hook cannot touch — which is why this is a candidate and not a defect. |
| C2 | `sdk/workflows/aircraft_optimization.py:2034` | `except (KeyError, TypeError, ZeroDivisionError): pass  # a malformed result stays out of the table`. The finalist table is published; a dropped row is absence, and no count is published beside the table to reveal the gap. | A malformed VSPAERO polar through `_finalist_job`, and a check of whether any published figure states how many finalists were expected. |
| C3 | `sdk/workflows/ahmed_body.py:697` | Painted-field copy to the served directory swallowed; `announce_field` then publishes `/api/field/<act>/<name>` while the file stayed in the case directory. The act's own comment says the file must live directly under `out` for that URL to resolve. | Injecting the copy failure and fetching the announced URL. Needs a solved field. |
| C4 | `sdk/workflows/geometry_study.py:2262` | Same shape as C3. | Same. |
| C5 | `sdk/workflows/nasa_hump.py:833` | Same shape as C3. | Same. |
| C6 | `sdk/workflows/backstep_case.py:925` | A pressure profile whose rows all fail to parse is published as `[]` — indistinguishable from a file that held only comments. Weak: a `len(parts) < 4` guard already absorbs the realistic truncation. | A `wallSample` file with non-numeric fields, and a reader that distinguishes empty-because-unparsed from empty-because-absent. |
| C7 | `sdk/workflows/tmr_verification.py:438` | `parse_yplus_dat` keeps the **last parseable** row. Demonstrated behaviour: with a garbled final row the function returns the 200-iteration row, published downstream as `max y+` — "the converged state" per its own docstring, with nothing saying a row was dropped. | Whether the last *complete* row is the right answer is a semantic call, not a bug I can assert. It needs an owner's ruling, which is why it is filed rather than fixed. |

C7 is the only candidate whose mechanism I reproduced:

```
clean   -> {'min': 0.11, 'max': 0.95, 'average': 0.55}
garbled -> {'min': 0.11, 'max': 0.95, 'average': 0.55}   <- the 200-iteration row
```

---

## 5. Out of scope — the exception path cannot reach a published verdict

**13 flagged sites**, each with its reason. Saying so is a result.

### How each of these was cleared, in three groups and not two

*"I could not make it fire"* and *"I never fired it"* are identical in the
output, and only the harness tells them apart. Folding the second into the
first is how a clearance becomes a claim, so the 13 are split by **method of
clearance**, not by confidence:

- **Group 1 — the injection visibly moved the verdict.** Nothing here. No site
  in this section was *demonstrated* safe by an injection that fired and showed
  no movement; injection was used only in the positive direction, on the two
  defects and on candidate C7. A stale `.pyc` cannot manufacture a change that
  did not happen, so the two defects and C7 are immune by construction.
- **Group 2 — fired at, with every `__pycache__` in the tree deleted and
  `PYTHONPYCACHEPREFIX` pointed at a fresh directory, and still clean.**
  **3 sites.** Executed, cold cache:

  | Site | Injection | Result |
  |---|---|---|
  | `replay_console.py:141` | a real listener bound on the probe's first port; then all five ports in the range held | returned the **next** free port, not the occupied one; exhaustion raised `SystemExit("No free port between 26000 and 26005.")` — **fails closed** |
  | `docker_dafoam.py:323` | `write_certificate` called with no checkMesh log, and with a log carrying no cell count — the two states the swallowed `checkMesh` leaves behind | returned `None` and wrote **no** `birth_certificate.json` in both cases — quarantined, exactly as its comment claims |
  | `probeWallBranch.py:185` | every string form the guarding regex admits, including 400- and 4000-digit runs | **0** strings matching `^[0-9]+(\.[0-9]+)?$` that `float()` rejects — the handler is unreachable for anything the regex lets through |

- **Group 3 — cleared by ARGUMENT, never fired at.** **10 sites** — the
  remaining rows of the table below. Each is cleared by tracing whether a
  published verdict exists and whether the handler's writes can reach its
  status. That is a static argument, stated per site so it can be disagreed
  with, and it is **weaker evidence than an executed injection**. Firing at
  them needs a live solve, a live WSL/OpenFOAM step, or a live VSPAERO run,
  which this rung may not launch. **None of them should be read as
  experimentally cleared.**

**No site moved from cleared to fail-open** under the cold-cache re-check.

| Site | Reason it cannot publish a false verdict |
|---|---|
| `demo-output/…/probeWallBranch.py:185` | `float(d)` where `d` already matched `^[0-9]+(\.[0-9]+)?$`, so the handler is effectively unreachable; and an empty `timeDirs` prints `PROBE_ERROR` and exits 1. **Fails closed.** |
| `scripts/laptop_bundle/replay_console.py:141` | `except OSError: continue` on a bind probe **is** the semantics — port busy, try the next. Exhaustion raises `SystemExit`. **Fails closed.** |
| `sdk/chief_engineer/docker_dafoam.py:242` | A `sudo chown` for housekeeping after the step; the step verdict is `result.returncode`, which the handler cannot touch. Flagged only because `result = subprocess.run(...)` matches the scanner's status vocabulary — a declared blind spot of the instrument. |
| `sdk/chief_engineer/docker_dafoam.py:323` | If `checkMesh` cannot run, no log exists, `if check_log.exists():` is false, **no certificate is written**, and the entry stays quarantined at lookup. `write_certificate` returns `None` by design: *"a certificate is a record of a check that ran."* **A model instance of this shape used correctly.** |
| `sdk/chief_engineer/field_render.py:1517` | Unlink of a staging temp file inside `finally`. Cleanup only; the verdict already returned. |
| `sdk/chief_engineer/vspaero.py:149` | An unreadable prior result falls through to **solving fresh** — the more expensive, correct path. **Fails closed.** |
| `sdk/chief_engineer/vspaero.py:186` | Stamping `elapsed_s` back into `result.json`. The in-memory result keeps the value for this run; no published verdict reads the key, and the compute ledger is measured from the caller's wall clock. |
| `sdk/workflows/adjoint_optimization.py:1428` | Swallows the same unlink as Defect 1 but **publishes no withdrawal claim**, so no published verdict counts it. The one member of that family that was not a defect. |
| `sdk/workflows/aircraft_optimization.py:2462` | `record_learned` for a lesson store. Not a verdict. |
| `sdk/workflows/geometry_study.py:626` | `record_learned`; the returned `passed` comes from `mesh_gates_pass`, untouched by the handler. |
| `sdk/workflows/ahmed_body.py:578` | Malformed `coefficient.dat` rows feed a live `trace.point` replay chart, not a verdict. The comment on the same path notes nothing is spent to the ledger there. |
| `sdk/workflows/geometry_study.py:2125` | Same as above. |
| `sdk/workflows/tmr_verification.py:1336` | The lever-echo write. **Nothing in the tree checks for the echo block's presence**, so there is no gate to fool — a missing echo cannot be published as agreement. That no such check exists is docket **B7**, already open, and is not re-filed here. |

---

## 6. What this sweep does not cover

Stated rather than discovered later.

- **`scripts/self_audit.py` (17 sites)** was out of scope throughout. It
  re-enters the population when V16 closes.
- **The scan reads Python only.** Shell, JavaScript and notebook gates are
  outside the frame entirely, and no count here says anything about them.
- **The dataflow is intraprocedural and name-based.** A swallow that reaches a
  verdict through an attribute, a mutable container held elsewhere, a global,
  or a second function is invisible to step 5. **A cleared site is not a
  proven-safe site**, and the 113 out-of-scope-by-construction sites rest on
  the same limitation.
- **Verdict detection keys on vocabulary.** A verdict published under names the
  scanner does not know is missed; a non-verdict named `result` is flagged.
- **Shape detection requires the handler to swallow syntactically.** A handler
  that logs and then returns a default value is a fail-open this scan does not
  model, and there is no measurement here of how many of those exist.
- **The control depends on a path and a commit.** `--control` hardcodes
  `scripts/self_audit.py` and pins `038b36da`. A repo move under Katie's
  section 7 breaks the **control** while the scan keeps running and keeps
  reporting negatives. That asymmetry is written into the scanner's own header
  and is filed in `docs/DOCKET.md`.
- **Green here is not coverage.** It means no *flagged* site outside the fixed
  twelve was shown to publish a false verdict — a narrower statement than it
  looks.

---

## 7. RE-RUN, 2026-08-23 — the scan re-executed against the corpus as it now stands

**Lines whose number changed above this section: 0.** Appended at the foot;
nothing above was edited (rule 6).

**Sweep date:** 2026-08-23, 19:47–19:52 UTC. **Executor:** `lab-lane`,
verification team. **Compute: zero core-minutes.** **Read-and-record: no gate,
script, test or verdict was modified by this pass**, and nothing below is a
re-grading of any team's published result.

### 7.1 The control, first, because it still gates everything after it

```
$ python3 scripts/fail_open_scan.py --control
POSITIVE CONTROL  scripts/self_audit.py@038b36da::check_board_placement_words
  line  1355  except OSError             writes=-              moves_verdict=-  FLAGGED
  line  1362  except UnicodeDecodeError  writes=-              moves_verdict=-  FLAGGED
  line  1373  except Exception           writes=['unreadable'] moves_verdict=-  FLAGGED
  -> FLAGGED (3 of 3 shape site(s) in that function)

NEGATIVE CONTROL  scripts/self_audit.py (working tree)::check_board_placement_words
  -> the repaired handler records into a name the verdict consults: True

CONTROL PASSED in both directions.                                    exit 0
```

**§6's named hazard did not fire.** That bullet warned that a repository move
would break the control — which pins `scripts/self_audit.py` at `038b36da` —
while the scan kept reporting negatives. The MOVE_MAP reorganisation has since
halved the tracked-file count (20,562 → 9,767) and `scripts/self_audit.py`
survived it at its path. **The control is still pointed at its real subject and
still separates on-from-off.** Every number below is reported only because this
ran first and passed.

### 7.2 The counts, with frame and filter and commit

**Frame:** `git ls-files '*.py'`, no `grep -r` anywhere (L-75). Taken while HEAD
moved `c7dc6add` → `090c070c`; the scan stamped `090c070c`.

| quantity | 2026-08-11 (`bfbf0523`, post-fix) | 2026-08-23 (`090c070c`) |
|---|---|---|
| tracked `.py` scanned (excluding `self_audit.py` and the scanner) | 481 | **688** |
| `UNPARSED` | 0 | **1** |
| fail-open **SHAPE** sites | 135 | **204** |
| …in a function that emits a verdict at all | not published post-fix | **44** |
| …**FLAGGED** | 20 | **38** |

Including `scripts/self_audit.py` — which §6 says re-enters the population when
V16 closes, and whose closure this pass could not establish — the same scan reads
**689 files, 227 shape sites, 60 verdict-reaching, 51 flagged**, of which
`self_audit.py` contributes **23 shape sites and 13 flags** (it carried 17 sites
in 2026-08-11's out-of-scope note).

**A FLAG IS STILL A CANDIDATE, NOT A DEFECT.** §1's rule is unchanged and it
governs this section: **only injection settles one, and this pass injected
nothing.** Reporting 38 as "38 fail-open gates" would be L-67 exactly.

### 7.3 The 38, split by whether the audit of 2026-08-11 already saw them

| bucket | sites |
|---|---|
| in a file that existed at `bfbf0523` — the already-adjudicated set carried forward | **19** |
| in a file that did **not** exist at `bfbf0523` | **19** |

The 19 old-file flags are §4's seven candidates and §5's thirteen clearances,
at shifted line numbers (`tmr_verification.py:438`→`:450`,
`adjoint_optimization.py:1428`→`:1439`, `nasa_hump.py:833`→`:845`, and so on),
plus `sdk/chief_engineer/agenda.py:1292`, which is new code in an old file.
**No site cleared in 2026-08-11's §5 has moved back into the flagged-and-unread
bucket**, and none was re-injected here.

Two of the 19 new-file flags are **relocations, not new sites**:
`ops/laptop_bundle/replay_console.py:141` (was `scripts/laptop_bundle/…`) and
`cases/dafoam/work/NACA0012_Airfoil_Incompressible/probeWallBranch.py:185` (was
under `demo-output/`). Both were cleared in §5's Group 2 by an executed
cold-cache injection; the code is unchanged and the clearance travels with it.
**Genuinely new sites: 17.**

### 7.4 New candidates, ranked — recorded, not settled

**C8 — `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/scoreboard.py:74`.** The
whole of *"claim (i): FS-full vs FS-SRonly on the PRIMARY case AR_1_Ret_360"* is
inside one `try:` whose only handler is `except IndexError: pass`. The two
selectors it guards are `[m for m in r["runs"] if m.endswith("_full")][0]` and
the `_SRonly` twin. If either list is empty the `[0]` raises, **the entire
claim-(i) block prints nothing**, and the script continues to its `core_hours=`
line and exits 0. A reader of that output meets a scoreboard with no claim-(i)
section and **no sentence saying the section was skipped** — absence presented
as though it were the whole output. This is the §5-header shape (*"a surface
that could not be read is not a surface that agrees"*) applied to a closure
scoreboard. **Not injected. Not fixed. Candidate.**

**C9 — `verification/runs/F14-cooling-ladder/K0cT_runs/build_cases.py:177` and
`K0cX_runs/build_cases.py:189`, `load_dat`.** Rows of a **measured** thermal
profile that do not parse are dropped with `continue` and **no count is kept**;
the only guard is `if len(xs) < 2: raise SystemExit("REFUSE: fewer than two
usable rows…")`. The values returned feed `extrap()` and then
`rubber_profile_expr()`, i.e. they become the piecewise-linear **patch boundary
condition** of a K0c case whose verdict is published. A file that lost half its
rows to a formatting change builds a coarser BC and says so nowhere. This is
2026-08-11's candidate **C6** shape — but on a live boundary condition rather
than a report table, which is a higher blast radius than C6 had. **Not injected.
Not fixed. Candidate.**

**Benign by argument, never fired at — 15 of the 17.** Eleven are the
`latest_time`/`all_times` idiom (`float(dirname)` inside `try`, non-numeric
entries skipped, then `raise SystemExit("REFUSE: no time directories…")` when
the list is empty — **fails closed**) and the post-read `os.remove` of the
`C`/`Cx`/`Cy`/`Cz` temporaries written by `postProcess -func writeCellCentres`
(**cleanup after the value has been read**; the verdict cannot move). Four were
read line-by-line for this section —
`K0c_runs/analyse_k0c.py:265` and `:281`, `THERMAL_K0_runs/analyse.py:82`,
`K2e_runs/analyse_k2e.py:117`. **The other eleven were classified from their
handler context and NOT read in full, and none of the fifteen was injected.**
Per §5's own three-group discipline these are **Group 3 — cleared by argument,
never fired at — and that is weaker evidence than an executed injection.**

**An instrument false positive, recorded so 38 is not read as 38 candidates.**
`scripts/hand_carry.py:719` is flagged with `swallow_writes=['rc']` and
`moves_verdict=[]`: the handler does `print(f"  FAIL: {exc}")`, sets `rc = FAIL`
and continues — it moves the verdict **toward** failure. `rc` never appears in an
`if` test, so step 3's guard-name computation cannot see it. This is §6's
declared blind spot (*"verdict detection keys on vocabulary… a non-verdict named
`result` is flagged"*) firing in the false-positive direction, and it means the
38 contains at least one site that is the opposite of a fail-open.

### 7.5 UNPARSED went 0 → 1, and the cause is a tracked file that is not on disk

```
UNPARSED: scripts/mutation_harness_known_test_names.py
          FileNotFoundError: No such file or directory
```

The path is in `git ls-files` and absent from the working tree —
`git status --porcelain` reports it ` D`, an **uncommitted worktree deletion**,
alongside nine others. Per constitution rule 10 it was **inspected and not
reverted**; the index is the chief's call. It is recorded here because §2's
`UNPARSED` row exists precisely so a file the scan could not read is counted
rather than absorbed, and this is the first time that row is non-zero.

### 7.6 What this re-run did not cover

- **Nothing was injected.** The 2026-08-11 pass settled two defects by injection;
  this pass settled none, and every new row above is labelled candidate or
  cleared-by-argument accordingly.
- **`scripts/self_audit.py`'s 13 flags were not read.** Whether V16 has closed —
  the condition §6 attaches to their re-entry — was not established here.
- Every §6 limitation still holds unchanged: Python only; intraprocedural,
  name-based dataflow; vocabulary-keyed verdict detection; syntactic swallows
  only. **A cleared site is still not a proven-safe site**, and the 160 sites in
  functions emitting no verdict rest on the same limitation.

## 8. Dated note, 2026-08-24 — the UNPARSED line at §7's foot is explained and the file is back on disk

**Lines whose number changed above this section: 0.** Appended at the foot
from `git show HEAD:docs/FAIL_OPEN_GATE_AUDIT.md`, never from the worktree.

§7's re-run listed `UNPARSED: scripts/mutation_harness_known_test_names.py`.
It was unparsed because it was **absent from disk while tracked at HEAD**
(blob `5ec5a9ce26f0c355070d370f33fe2e8b2787be7b`, 203 lines; index entry
present) — the positive control that `scripts/check_absolutes.py:546` cites
as its evidence could not run, so §1's gate on everything after it was
resting on a file no scan could open.

**Mechanism, established by the verification supervisor from HEAD and disk
(2026-08-24, ~16:10Z).** The file is one of exactly ten unstaged tracked
deletions (` D`) in the shared worktree, and the ten are the same ten this
team's board listed on 2026-08-23 as "tracked, absent from disk": this
harness (`c83c9de0`, 2026-08-17T18:35:09Z, `Lab-Agent …/lab-check-repairs`
trailer), `docs/campaigns/F14-cooling-ladder/K1_STANDING_THERMAL_CHECKS.md`
(`4afefe54`, 2026-08-17T18:59:00Z), and the eight K2bP heat-balance
artifacts (`9f3971f6` MOVE_MAP R25, 2026-08-18; adjudicated by heat-transfer
as D477 — DELETE `a311d872`, REVERSED `0c742c66`). Each of the two 08-17
commits ADDED exactly one new file and that one file is the absent one; no
commit in the path's history ever deleted either; `git worktree list` shows
main only, but `H4_ALLOCATION_AUDIT.md` (`af16ceef`) found eight prunable
worktrees pointing into the since-wiped scratchpad. **Reading: the file was
never written to this worktree — it was committed from a scratchpad-resident
linked worktree, or by hash-object from a scratch path, on 08-17, and the
shared index only began reporting it as a deletion after the chief's
2026-08-23T21:15Z `read-tree HEAD` refresh gave the index an entry for it.
Not a disk-clearing event.** Same mechanism as D477's eight.

**Restore, under the chief's ruling of 2026-08-24 (same ruling as D477's,
Sanaa's standing authorisation and the D-1 precedent):** `git show
HEAD:<path> > <path>` in one invocation — never `checkout --`, the index
untouched. Restored file hash `5ec5a9ce26f0c355070d370f33fe2e8b2787be7b`
== `git rev-parse HEAD:<path>`; `git status --porcelain` on the path now
empty; **zero HEAD bytes changed**, so no commit carries the restore — this
note is its record. Executed by the supervisor rather than a lane because the
three-lane cap was full; disclosed. K1 and the eight are heat-transfer's under
the same ruling and were not touched.

**Consequence for this audit:** the `UNPARSED` line is retired as of this
note; the positive control it names is runnable again. Whether
`check_absolutes.py`'s selftest actually fires on the restored harness is a
re-run, not a note — it joins the next §7-class re-run of this audit, and
until then the §1 positive control is **restored, not re-proven**.

---

## 9. Dated note, 2026-08-24T17:31:21Z — the stamp/id-skew instrument is wired REPORT-ONLY, and there is no shared audit re-run entry point to wire it into

**Why this note is in THIS audit rather than in a new runner.** The instruction
was to add a report-only invocation of `scripts/check_stamp_vs_commit.py` to
whatever the six standing audits use as a shared re-run entry point, and if
there is none, not to invent one. **There is none.** The six re-runs of
2026-08-23 — `c5a9d4c7` (sweep-reframe), `f14fca9c` (this audit's §7),
`876a9ec1` (dead-lever), `af16ceef` (H4 allocation), `69df4876` (ledger
headline), `e3f3b521` (external referent) — each touch exactly ONE file, their
own audit, one commit apiece. Frame and filter for that claim: `git show --stat`
on those six shas, plus `/usr/bin/grep -rlE '_AUDIT\.md'` over every tracked
`.py` and `.sh`, which returns three files and no runner among them — this
instrument's own corpus glob in `scripts/check_stamp_vs_commit.py`, and two
`cases/dafoam/f6d_random_matrix_uq/` plotting scripts that cite
`F6D_ENSEMBLE_CONVERGENCE_AUDIT.md` in prose. The invocation is therefore
recorded here, in the audit that owns instrument-coverage findings.
`scripts/check_harness.py` and `scripts/check_filing.py` were not touched.

**The invocation — report-only, never a gate, never `--strict`:**

    python3 scripts/check_stamp_vs_commit.py --at <HEAD>

Exit 0 on this path by construction: `--strict` is the only flag that converts a
FIRE into a non-zero exit and it is deliberately not passed. Nothing depends on
this check's exit code, and no gate anywhere consults it.

**HEAD output summary — graded tree `86fb1b34`, counts only, exit 0.**

    LIMB 1  stamps vs the commit that introduced their line
      corpus files carrying stamps          66
      candidate tokens                     462
      graded (UTC-marked)                  404
      UNMARKED (not graded, listed)         58
      PLANNED (future-intent cue)            2
      FIRES                                 19

    LIMB 2  id citations vs the commit that appended their defining row
      corpus files carrying ids              90
      id tokens (L-nnn, Dnnn, C-nn, N-XXn) 3871
      graded                              3833
      DANGLING (distinct verdict)           38
      FIRES                                280

**Selftest beside it, same tree:** `python3 scripts/check_stamp_vs_commit.py
--selftest`, exit 0, **11 named controls, 4 mutants, 15 results; 0 failed**.
That summary line now names all three figures deliberately. The record has
carried two different counts of the same thing — `docs/COST_CALIBRATION.md`
C-25 says "9 planted controls" while the verification board says "six" — and
both were true at different granularities (6 named + 3 C6 mutants = 9 recorded
results). C-25 is an append-only ledger row and is **not rewritten**; the
ambiguity is closed at the instrument, where the next reader will meet it.

**What 280 does NOT license.** 280 limb-2 fires is not 280 findings, and this
note grades none of them. Measured breakdown over the immediately preceding
tree `e25908fe` (281 fires there, `--show-all` so the table was not capped):
**256 of 281 are D-family citations against `docs/DOCKET.md`**, 23 are C-family,
1 L, 1 N; **124 of 281 exceed 24 h**. That distribution is the signature of the
blame limitation the instrument prints on every run, not of 280 mis-numbered
citations: `git blame` names a line's LAST toucher, so a docket row edited long
after it landed reads as though it were appended then — D3's own row records
being "DEQUOTED 2026-08-11", and D1/D5/D9/D12 head the fire table with deltas of
288 to 485 hours, which is simply the age of the rows. For limb 1 the same error
is conservative (it can hide a fire, never manufacture one); **for limb 2 it cuts
both ways** — a reflowed citation reads quieter, a reflowed defining row louder —
and the instrument says exactly that in its closing NOTE. A limb-2 fire is a
triage prompt; it is not a verdict and must not be quoted as one.

**What is worth a reader's attention, and is why the limb was built.** Three of
the 38 DANGLING citations at `86fb1b34` sit on ONE board line,
`docs/LAB_STATE.md:423` — `D499`, `L-277` and `N-D32`, none of which has a
defining row at that tree. That is the D488/C-15 instance class live: ids
written into prose as a prediction of what the next append will be numbered,
before the append that would make them identifiers. It is reported as a count
and a verdict name, not adjudicated here — those three may land within the hour,
which is precisely the point rule 11 makes.

**Known false positives in the DANGLING set, disclosed rather than filtered
away.** 35 of the 38 are already-documented non-citations or known holes, and
they account for the whole set once the three live ones above are removed:
`C-2026` (25 occurrences) is a certificate serial in `docs/DOCKET.md` reading as
a C-family id; `D188` (3) and `D901` (2) are the two non-citations `D349`
already documents as such; `L-52` (4) is the hole CLAUDE.md rule 11 names by
name; `N-B21` (1) sits on `docs/DOCKET.md:828` beside `L-52`, in a row that is
itself about missing ids. 25 + 3 + 2 + 4 + 1 + 3 = 38. Filtering the known ones
out would make the instrument quieter and less honest, so they are listed on
every run instead.

**Standing weaknesses of this wiring.** (a) Nothing runs it on a schedule; it
runs when someone types it, exactly like the six audits themselves — this note
records an invocation, not an automation. (b) Its corpus is the fixed glob set
limb 1 already used, so a record outside `docs/`, `cases/` and `verification/`
is invisible to both limbs. (c) Report-only means a FIRE has no consequence
unless a reader acts on it; that was the supervisor's explicit decision on this
instrument and is recorded as such, not as an oversight.

**Consequence for this audit:** none of §1–§8 changes. This section adds a
coverage record only, and the fail-open sweep's own counts, control and verdicts
stand exactly as §7 and §8 left them.

*Lines whose number changed above this section: 0.*

---

## 10. RE-RUN AND PROPOSED EXTENSION, 2026-08-27 — the gate population that entered HEAD after `02a84b18`, graded on a prediction-first limb

**Lines whose number changed above this section: 0.** This section was appended
to a base taken from `git show HEAD:docs/FAIL_OPEN_GATE_AUDIT.md` at HEAD
`c9ff33d9`, asserted at **698 lines** before a byte was added, never from the
worktree. §1–§9 are byte-identical to that blob.

**Executor:** `lab-lane`, verification team, under the cross-team gate-audit
mandate. **Compute: ZERO core-minutes.** **Read-and-record: no gate, script,
pre-registration, comparator or verdict of any team was modified by this pass**,
and nothing below re-grades any team's published result. Findings, not fixes.

### 10.0 A finding before the audit: the worktree copy of THIS file was stale

`docs/FAIL_OPEN_GATE_AUDIT.md` on disk at the start of this pass was **548
lines** against HEAD's **698**, reported ` M` by `git status --porcelain`.
`diff <(git show HEAD:…) <disk>` returns **150 HEAD-only lines and ZERO
disk-only lines**: the worktree copy is a strict truncation that ends at §7's
foot and is missing **§8 and §9 entirely**. It carries nothing HEAD does not.
Per constitution rule 10 it was **inspected, not reverted**; the base for
everything below is the HEAD blob, and writing this section restores §8 and §9
to disk as a side effect of that choice. Recorded because an audit that had
appended to the disk copy would have silently deleted two dated sections — the
exact defect shape §6 exists to prevent.

### 10.1 The instrument this section applies, and the part of it that does not reach

**Restated from §1 and §105–§128, not reinvented.** The instrument of §1–§9 is a
static AST scan of tracked Python. Its unit is a **SHAPE site**: an `except`
handler whose body swallows. Its method is five steps — find the enclosing
function `F`; ask whether `F` **emits a verdict**; compute **guard names** (every
name the *choice* of verdict can depend on — `if`/ternary/`while`/`assert` tests
and the status position of an emission, **never** a name that appears only in
text); compute **swallow writes**; and **FLAG** when `F` emits a verdict and
swallow-writes ∩ guard-names is empty.

**Its verdict taxonomy for a gate, in its own words:**

| the instrument's word | what it means there |
|---|---|
| **FLAGGED** | verdict emitted and the swallow cannot move it — *"this gate could not have failed"* in the shape sense. **§1: "A flag is a CANDIDATE, not a defect."** |
| **Demonstrated defect** | injection fired and the published verdict was wrong. §3. Twelve of these. |
| **Candidate** | plausible, **could not be made to fire**. §4. This is the instrument's *"cannot tell"*. |
| **Out of scope / cleared** | the exception path cannot reach a published verdict — *"this gate discriminates"*. §5, split into **three** groups deliberately: cleared by static argument; **fired at and stayed clean**; and cleared by argument and **never fired at** — because *"could not make it fire"* and *"never fired at it"* look identical in the output. |
| **UNPARSED** | the scan could not read the file. §2 keeps this row so an unreadable file is counted rather than absorbed. |
| **Positive / negative control** | §1: *"A sweep that returns 'few or no fail-open gates' is worth nothing unless it was shown capable of finding one"* — and the negative control is what caught the instrument's own inverted first draft. |

**This instrument does not reach a pre-registered numeric band, and §6 already
says so.** §6's bullets state *"the scan reads Python only"*, that the dataflow
is *"intraprocedural and name-based"*, and that *"green here is not coverage"*.
Nothing in §1–§9 models a threshold, a band, a freeze timestamp or a comparator
hash. The population this pass was asked to grade — pre-registered thresholds
and graded verdict records — is a **different gate shape**, and applying the
`except`-swallow taxonomy to it would be an unannounced widening.

#### PROPOSED EXTENSION — attributed to this lane, NOT adopted, NOT a charter change

> **The prediction-first limb.** Proposed 2026-08-27 by the verification
> `lab-lane` that wrote §10. It is **a proposal on this page and nothing more**:
> no supervisor has ruled on it, it gates nothing, no comparator consults it, and
> retiring or adopting a standard is reserved to Sanaa (CLAUDE.md FIRST-ACTION
> rule). §1–§9's counts, controls and verdicts are untouched by it.

The limb keeps the existing taxonomy and re-points it at a pre-registration. Its
unit is a **gate**: one pre-registered threshold with a band, a comparator and a
graded value. Its question is the audit's own, transposed:

> When this gate was evaluated, could it have returned anything other than the
> outcome it returned?

Five tests, each of which makes a gate a **FAIL-OPEN CANDIDATE** (≡ FLAGGED):

- **(a) band unreachable** — the band is so wide no physically plausible result
  lands outside it. Requires naming a value that *would* have failed and saying
  whether it is reachable.
- **(b) threshold set from a visible answer** — the freeze commit does not
  precede the first artifact that could carry the answer. This is the method
  `docs/COVERAGE_MATRIX.md:676` §3.6 executed by hand on two ansys rows
  (`COVERAGE_MATRIX.md:681`, `:820`); §10.4 executes it across the population.
- **(c) no numeric comparator** — a prose gate.
- **(d) pass path and fail path reach the same recorded outcome.**
- **(e) the comparator's refusal path is unreachable** on the data the case can
  produce.

A gate **DISCRIMINATES** (≡ §5 *cleared*) when a plausible alternative outcome
would have failed it, and — §5's three-group discipline carried over verbatim —
the clearance is labelled by **how** it was reached: **shown to fail on real
data** (strongest), **driven through the frozen expression** (§3.6's method), or
**cleared by argument, never fired at** (weakest). **NOT MEASURED** (≡ UNPARSED)
is used wherever the artifact needed does not exist or could not be located, with
the reason.

#### The limb's positive control, first, because §1 gates everything after it

§1's rule is that a method returning "no fail-opens" is worthless until shown
able to return one — and that the *negative* control is what catches an inverted
instrument. **Both fired on this pass, on the first execution of test (b), and
the limb was wrong before it was right.**

Test (b) was first run with the run-artifact defined as *the earliest file of any
kind in the case's run directory*. It returned **nine negative skews** — nine
gates apparently pre-registered *after* their own run artifacts existed:
`VMFL003_M2` at **−666 s**, and eight T-family rungs from **−123 s** (`T14`) to
**−11,231 s** (`T13`).

**All nine are instrument false positives, and the disconfirming evidence is on
disk.** The earliest artifacts are `constant/transportProperties`, `0/p`,
`log.blockMesh`, `log.checkMesh.build`, `log.viewFactorsGen` — **case staging and
mesh generation, which produce no gate value**. `T10aR2`'s own freeze commit
`fb4bf7e2` says it in the subject line: *"PRE-REGISTERED and BUILT, NOT FIRED"*.
Re-run against the **solver** artifact (`log.solve`, `log.*Foam*`, `log.launch`,
`postProcessing/`), **every one of the nine is positive** — `VMFL003_M2` +546 s,
`T13` +5,923 s, `T14` +23,780 s.

**The control also indicts the method as §3.6 executed it.** §3.6's headline
figure for VMFL005 — *"earliest run artifact 18:45:21.32Z"*, giving **+194 s** —
is `verification/runs/ansys_verification/VMFL005/L1_100x10/0/p`, a **staged input
file**, not solver output. On the solver reading VMFL005 is **+205 s**. The two
readings agree on VMFL005 and disagree in sign on nine other rows, so **§3.6's
figure as published is not a stable definition** and this section states which
reading each number below uses. That correction is the extension's negative
control doing its job, and it is reported rather than filtered.

### 10.2 The population, by measurement

**Frame:** `git log --name-only 02a84b18..HEAD` over four pathspecs —
`'*PREREGISTRATION*.md'`, `'*RESULTS*.md'`, `'gate_*.json'`, and
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` — deduplicated.
**No `grep -r` anywhere in the population step (L-75):** `grep` in this
environment execs `ugrep --ignore-files` and is blind to gitignored paths, so the
denominator comes from git alone.

| quantity | count |
|---|---|
| distinct tracked paths entering HEAD after `02a84b18` on those pathspecs | **236** |
| …`PREREGISTRATION*.md` | **137** |
| …`*RESULTS*.md` | **98** |
| …the ansys register | **1** |
| newly **added** after `02a84b18` | **218** |
| **modified** (existed at `02a84b18`) | **18** |
| absent at HEAD (added then deleted within the window) | **4** |
| pre-registrations **present at HEAD** — the graded denominator | **133** |

By territory: **dafoam 75**, `verification/` tree **63**, **ansys 61**,
heat-transfer campaign prose **33**, closure **3**, `docs/ansys_verification` **1**.

**A pathspec correction.** `'gate_*.json'` as written returns **zero** paths: a
git pathspec glob is matched against the path from the repository root, so it
only matches a file named `gate_*.json` *at the root*. The lab's gate JSON is
`cases/dafoam/f6a_epistemic_band/**/gate_result_*.json` and
`verification/runs/F14-cooling-ladder/K0cG_runs/gate_k0cg.json`. Corrected to
`'*gate_*.json'`, **5** such paths entered HEAD in the window. They are counted
here and **not graded**; see §10.9.

The four deleted-within-window paths are
`cases/dafoam/ladder-a/A2/curriculum_D5/PREREGISTRATION_DRAFT.md`,
`…/curriculum_D6/PREREGISTRATION_DRAFT.md`,
`verification/campaign/F3_SUCCESSOR_BANDONLY_PREREGISTRATION.md` and
`verification/campaign/F6a_GREENBLATT_PREREGISTRATION_DRAFT.md`. Three are drafts
by their own filename; none is graded here.

### 10.3 THE GATES THAT ACTUALLY FAILED — at the front, because they are the proof the gates bite

§1's logic applied to this population: a sweep reporting "the gates discriminate"
is worth nothing without gates shown failing on real data. **They exist in
quantity, across four teams, and several fail on margins too narrow for any wide
band to explain.**

**The ansys validation register, `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`, 32 rows at HEAD:**

| verdict | rows |
|---|---|
| `PASS` | **6** (rows 1-indexed 2, 3, 7, 13, 15, 28) |
| `GATE REACHED` | **5** (20, 22, 23, 24, 30) |
| `NOT A RESULT` | **20** |
| `PENDING` | **1** (19) |

**20 of 32 rows — 62.5 % — are `NOT A RESULT`, and 6 are `PASS`.** A register that
could not fail does not look like this. Named instances, each with its
discriminating fact:

- **VMFL010** — `NOT A RESULT` on rule 5 step 2, and the row says the quiet part:
  the L3 value is **0.26 % from the reference 0.887, well inside the frozen 3 %
  band**, so a value-only reading calls it `GATE REACHED`. The `OSCILLATORY`
  triple overrode a comfortable in-band number. **The gate refused a number that
  would have passed.**
- **VMFL059** — `NOT A RESULT` on an `EXACT` triple, with `rc = 0`, `End` present,
  `last Time == endTime`, age guard passed and planted-zero passed on both
  patches. The register states the cause is a **mis-specified gate quantity, not
  a failed solve**. A clean solve was refused.
- **VMFL003-M2 arms A and B** — the register records
  **`gate_verdict_before_rule5` = `GATE FAIL`** on both, converted to
  `NOT A RESULT` by rule 5's permitted direction. **A literal `GATE FAIL` on real
  data, preserved in the record rather than absorbed.**
- **VMFL011** and **VMFL011-R2** — `NOT A RESULT` because the **frozen comparator
  refused (exit 2) on its own planted-zero control** (rule 3). R2's refusal text
  is quoted verbatim in the register from
  `verification/runs/ansys_verification/VMFL011-R2/GRADING.txt`. Test **(e)** is
  answered on real data for these two: **the refusal path is not merely reachable,
  it fired.**
- **VMFL017-R2** — `NOT A RESULT`: the registered per-level cap fired (`rc = 124`)
  and the comparator refused on strict completion (rule 4). The row adds *"not
  softened by having been predicted"*.
- **VMFL003-M2 arms C and D** — `NOT A RESULT`, LADDER INCOMPLETE: the frozen
  `PER_ARM_CAP = 40` core-min fired at **39.93** and **39.99** of 40. **A cost cap
  is a gate and it bit, to the second** (`ExecutionTime 1662.74 s` against a
  wrapper `timeout 1663`). No fresh cap was granted.
- **VMFL005**, the register's cleanest `PASS`, is where the *counterfactual* is on
  record: **Ansys's own CFX value of 10.49 Pa `GATE FAIL`s the frozen 2 % band
  (2.4414 %)**, and the pre-registration said so **before any number existed**
  (`docs/COVERAGE_MATRIX.md:681`ff). A commercial code's own published number for
  this exact case fails this gate.

**Outside ansys, named with file:line:**

- **`docs/campaigns/T-family/T1c_RESULTS.md:6`** — *"Rung verdict: GATE FAIL — 1
  of 4 graded rows failed."* Row **L0** at `:14`: `Nu` (constant `Ts`)
  **3.659958** against exact **3.6567934**, deviation **0.0865 %** against a
  **GCI band of 0.0301 %** — **failed by 2.87×**. Rows L1 (`:15`, 0.0192 % vs
  0.0236 %) and L2 (`:16`, 0.0381 % vs 0.0459 %) `PASS` on the same instrument.
  **The band here is the computed GCI, not a chosen number**, and it separated
  three rows from a fourth at the fourth decimal place. `:123` — *"The GATE FAIL
  is real and is not excused."*
- **`verification/campaign/F12_RESULTS.md:99`** — ADMISSION GATE A (mesh)
  **`GATE FAIL` at all three levels**. Frozen threshold *max non-orthogonality
  ≤ 70°*; measured **70.646 / 70.861 / 72.542** (`:112`–`:114`) from three real
  `checkMesh` logs. **The coarse level failed by 0.65° — a 0.92 % overshoot.**
  A gate that fails on a sub-1 % margin cannot be called unfailable. `F12`'s
  headline at `:22` is **`GATE FAIL` / `NOT HELD`**.
- **`docs/campaigns/T-family/T10aR2_RESULTS.md:3`** — *"2 PASS, 5 GATE FAIL, 2 NOT
  A RESULT against this arm's own registered rows."* Rows `:47`, `:48`, `:50`,
  `:51`: RR4a **1.883** and RR4b **1.786** against band **[1.70, 2.10]**;
  RR6a/RR6b **1.504** against **[1.0, 2.0]** — and each row carries the value the
  **competing hypothesis H2 predicts** (1.664 / 1.495 / 3.75 / 2.25). **This is
  the discrimination test of `VERIFICATION_CHARTER.md` §2c executed inside the
  results table**: the row separates H1 from H2 rather than from nothing, and
  RR6a's *"move at c is 4.9× H1"* is what failed it.
- **`cases/dafoam/ladder-a/A5/curriculum_D9/RESULTS.md:30`** — G9-3 `GATE FAIL`:
  `driver_failed=True`, `driver_iter_count=47` against `maxit=20`. `:38` — the
  gate *"maps driver failed to `GATE FAIL` irrespective of magnitude"*, i.e. **a
  boolean gate with no band to widen.** `:189` records a second: 46.840 %
  aggregate FD deviation **with two sign flips**.
- **`cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md`** —
  headline `GATE FAIL`, 11 `GATE FAIL` tokens in the record.
- **`docs/campaigns/T-family/T1b_RESULTS.md`** (6 `GATE FAIL`),
  **`T10aR_RESULTS.md`** (18), **`T3_RESULTS.md`** (5),
  **`docs/campaigns/F14-cooling-ladder/K0f_RESULTS.md:65`** (TALLY 0 of 10),
  **`verification/runs/F3_runs/conversion_2026-08-24/RESULTS.md`** (3),
  **`cases/dafoam/ladder-a/A1/curriculum_D2/RESULTS.md`** (9),
  **`…/curriculum_D13/RESULTS.md`** (5) — counted, not individually adjudicated.

**Headline verdicts across the 98 `*RESULTS*` records** (first `VERDICT`-line
token per file, at HEAD, ansys excluded to avoid double-counting the register):
`PASS` 15 · `NOT A RESULT` 13 · `GATE REACHED` 8 · `BLOCKED` 4 · `GATE FAIL` 3 ·
`PENDING` 3 · **no parseable verdict line 27**. The last figure is itself a
finding and is carried into §10.9.

### 10.4 Test (b) executed across the population — the §3.6 skew method, on the solver reading

**Method.** For each pre-registration: `T_p` = committer time of the commit that
**first added** the path (`git log --diff-filter=A … | tail -1`). `T_r` = earliest
mtime of a **solver** artifact in the case's run directory (`log.solve`,
`log.*Foam*`, `log.launch`, `postProcessing/`). `skew = T_r − T_p`. A negative or
near-zero skew is the finding.

**ansys — 30 cases measured, `verification/runs/ansys_verification/<case>/`:**

| skew band | cases |
|---|---|
| **negative** | **0** |
| +9 s … +99 s | VMFL019 **+9**, VMFL076 **+19**, VMFL011 **+27**, VMFL002 **+41**, VMFL004-R2 **+67**, VMFL036 **+95** |
| +100 s … +999 s | VMFL005 **+205**, VMFLGPU002 +233, VMFL051 +326, VMFL007 +348, VMFL045 +389, VMFL007_R2 +394, VMFL064-R2 (see below), VMFL011-R2 +419, VMFL023 +501, VMFL003_M2 **+546**, VMFL001 +628, VMFL033 +627, VMFL003 +922 |
| ≥ +1,000 s | VMFL045-R2 +1,207, VMFL059 +1,913, VMFL011-R3 +2,381, VMFL076-R2 +2,806, VMFLGPU001 +17,124, VMFL064 +41,239, VMFL017 +69,238 |

**T-family and F14 — 16 rungs measured:** T10aR **+299**, T10aR2 **+1,532**,
T4b **+1,946**, T4 **+1,984**, T9aH **+1,298**, T8 **+4,301**, T13 **+5,923**,
K0f **+6,710**, T10a **+7,742**, T3 **+12,181**, T14 **+23,780**, T15 **+37,429**,
T11 **+41,330**, T9aR1b **+41,777**, T5 **+43,085**, K0d **+99,342**.
**Negative: 0.**

**VERDICT on test (b): DISCRIMINATES — shown on real artifacts, 46 of 46
measurable gates.** No gate in the measured population has a pre-registration
committed after the solver could have shown its answer. **This closes the open
item at `docs/LAB_STATE.md:10405`** — *"Six of heat-transfer's seven `GATE
REACHED` rows have NOT had their frozen-pre-registration condition individually
verified… hash each prereg blob at HEAD and compare its commit time against the
earliest run artifact, the way §3.6 did"* — **for the timestamp half only.** The
**blob-hash half of that item is NOT closed here**: §10 measured commit times, not
blob identity, and rule 2's demand that *"the frozen file IS the file that ran"*
is a hash comparison this pass did not perform on any heat-transfer row.

**The tightest margin in the population is VMFL019 at +9 s**, then VMFL076 at
+19 s and VMFL011 at +27 s. These are **positive and therefore not fail-open under
(b)** — a first run of a case has no prior value to tune to, and 9 s is a
plausible commit-then-launch interval. They are named because the limb's own
threshold for "near-zero" should not be set after seeing them, and a supervisor
may reasonably want the launch scripts for those three read.

### 10.5 Test (c) — prose gates

**133 pre-registrations present at HEAD were scanned for any numeric-threshold
token** (`<`/`>`/`≤`/`≥`/`±` followed by a number, a percentage, a bracketed
interval, or scientific notation). **132 carry at least one. The single exception
is `cases/ansys_verification/_template/PREREGISTRATION_TEMPLATE.md`**, which is a
template and grades nothing.

**VERDICT on test (c): DISCRIMINATES — but cleared by argument, never fired at**
(§5 Group 3, the weakest of the three). The test detects the **presence of a
number**, not that the number is **the gate** or that a comparator reads it. A
pre-registration carrying a numeric cost estimate and a prose gate passes this
scan. **This is the limb's weakest limb and it is stated rather than glossed.**

A related defect **is** on record in a sibling audit and is not re-derived here:
`docs/COVERAGE_MATRIX.md` found cfd records grading in non-rule-1 vocabulary —
`GEN_ALT` grades *"GENERATOR-OWNED"*, `W1_hump` *"OUTCOME ONE"*, `F8`
*"NO VERDICT"* / *"NO MILESTONE"*. Those are pre-registered branch labels, which
is legitimate design, but **a sweep for the lab's verdicts does not see them** —
and neither does §10.3's headline scan, which is part of why 27 records returned
no parseable verdict line.

### 10.6 Test (a) — band width, sampled and not swept

Not executed across the population; **NOT MEASURED** for 133 pre-registrations as
a class. Four gates were read to source:

| gate | band, quoted | measured | ratio band/measured | what would have failed |
|---|---|---|---|---|
| VMFL005 dP | 2 % relative, frozen | 0.4979 % | **4.0×** | 10.49 Pa (CFX's own value) → `GATE FAIL` at 2.4414 %; also 10.45, 5.0, 20.0, 0.0 |
| VMFL064 `LR/s` | `\|LR/s − 5.0\|/5.0 ≤ 0.10` — `cases/ansys_verification/VMFL064-R2/PREREGISTRATION.md:53` | ~2.9 % (`:170`) | **3.4×** | `:57` records the band as *"deliberately looser"* than Fluent's own 1.8 %; `:180` names an inlet-profile change that would exceed it |
| VMFL011 `rms_vs_benchmark` | `BAND_RMS = 0.030` at L3 — `cases/ansys_verification/VMFL011-R2/PREREGISTRATION.md:46` | 0.0341 (attempt 1) | **0.88× — the case MISSES its own band** | `:266`: *"attempt 1's 0.0341 is 14 % above the band"* |
| T1c row L0 | GCI band 0.0301 % — `docs/campaigns/T-family/T1c_RESULTS.md:14` | 0.0865 % | **0.35× — failed** | the band is computed, not chosen |

**VMFL005's 4.0× is the loosest of the four and it is still a discriminating
gate**, because the counterfactual is not hypothetical: a commercial code's own
published number for this case falls outside it. **No fail-open under (a) among
the four read.** The other 129 are NOT MEASURED.

### 10.7 Test (d) — do the pass path and the fail path reach the same outcome?

The structural exposure in this lab is **rule 5's permitted conversion**: a
`GATE FAIL` and a `PASS` both become `NOT A RESULT` when the triple is not
`CONVERGING`. If the pre-conversion verdict is discarded, **a failing gate and a
passing gate leave the same recorded trace** — test (d) exactly.

**Measured:** `gate_verdict_before_rule5` appears in **12 tracked paths at HEAD**,
and the graders that emit it are **two**: `cases/ansys_verification/VMFL003/grade_vmfl003.py`
and `cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2.py` (plus its `_omega`
twin). It reaches
`verification/runs/ansys_verification/VMFL003_M2/A_kEpsilon/GRADING_A_kEpsilon.json`,
the register, `docs/CAPABILITY_GRID.md` and `docs/LAB_STATE.md`.

**Finding — FAIL-OPEN CANDIDATE under (d), scoped to the records that lack it.**
The ansys VMFL003 family preserves the distinction and is therefore **CLEARED —
shown on real data** (arms A and B record `GATE FAIL` before conversion). **Every
other `NOT A RESULT` in the population that arose from a rule-5 conversion does
not record which verdict it converted**, so pass-path and fail-path are
indistinguishable in the record for those rows. VMFL010 is the live illustration:
its register row *does* state in prose that a value-only reading would have called
it `GATE REACHED`, which is the same disclosure made by hand rather than by the
comparator.

**Proposed, attributed to this lane, not adopted:** a comparator that converts a
verdict under rule 5 should emit the pre-conversion verdict beside it, as
VMFL003's does. This is a **finding referred to each owning team**, not a fix, and
not a charter amendment — rule 5 is unchanged and this section does not touch it.

### 10.8 Test (f), proposed — the successor-rung exposure, and the lab passes it

**Proposed by this lane as an addition to the limb**, because test (b) cannot see
it. Test (b) asks whether the *case's own* run existed before the freeze. It
returns a large positive skew for a **successor rung** (`-R2`, `-R3`, `_M2`) whose
**predecessor's measured value was fully visible** when the successor's band was
frozen. **A successor's band is the shape most exposed to being chosen to fit, and
the skew test is blind to it by construction.**

**Population:** 11 successor rungs in the ansys family alone — VMFL001-R2,
VMFL003_M2, VMFL004-R2, VMFL007_R2, VMFL011-R2, VMFL011-R3, VMFL017/R2,
VMFL021/R2, VMFL045/R2, VMFL064-R2, VMFL076-R2.

**Measured on three, read to source — and all three are CLEARED, on the strongest
available evidence:**

- **VMFL011-R2** — `cases/ansys_verification/VMFL011-R2/PREREGISTRATION.md:46`:
  *"BANDS (THE GATE): rms_vs_benchmark <= 0.030 at L3. BYTE-IDENTICAL to attempt 1
  line 5."* `:244`–`:245`: *"The band could not have been chosen to fit, because
  the band was not chosen… made before any VMFL011 number existed."* And `:266`
  records that **attempt 1 missed that band by 14 %** — the team carried forward a
  band it already knew the case fails. **That is the opposite of a fail-open, and
  it is the model the extension should be calibrated on.**
- **VMFL076-R2** — `PREREGISTRATION.md:66` and `:101`: bands, ceiling, reference,
  quantities and ladder **CARRIED**, *"the same file"*. `:168` discloses the
  predecessor's exact measured values (0.9006 % against the 3.00 % band;
  5.397e-03 against 1.00e-02) **without moving either band**, and `:189` states
  *"`GATE FAIL` is a real possible outcome"*.
- **VMFL064-R2** — band `≤ 0.10` carried from run 1 (`:53`); `:170` names the
  expected ~2.9 % **in advance**, *"predicting in advance rather than discovering
  it"*; `:180` names a perturbation that would exceed the band.

**VERDICT on test (f): DISCRIMINATES for the three read — cleared by byte-identical
band carry-forward, verified against the predecessor's frozen text.** The other
eight successors are **NOT MEASURED**. This is a genuinely positive finding about
the ansys family's `§2c`/`§2d` discipline and it should not be flattened into the
counts.

### 10.9 Coverage limits — what §10 did not cover, stated rather than discovered later

- **§10 grades gates, not code. §1–§9's counts, controls, defects, candidates and
  clearances are untouched**, and the `except`-swallow scan was **not re-run** on
  this pass. §7's 38 flags and §7.4's C8/C9 stand exactly as they were left.
- **Nothing was injected, and nothing was driven through a frozen comparator by
  this lane.** §3.6's driving of six values through VMFL005's gate expression is
  **cited from `docs/COVERAGE_MATRIX.md:681`ff, not reproduced here.** Under §5's
  three-group discipline every clearance in §10.5–§10.8 is therefore **Group 3 —
  cleared by argument, never fired at** — except test (b) and test (e), which rest
  on artifacts and refusals that actually exist on disk.
- **Test (a) is NOT MEASURED for 129 of 133 pre-registrations.** No sweep of band
  width against physically reachable values was performed. This is the largest
  single gap in §10 and no count here should be read as covering it.
- **Test (e) is NOT MEASURED as a sweep.** It is answered on real data only for
  VMFL011 and VMFL011-R2 (planted-zero refusals that fired) and VMFL017-R2
  (completion refusal that fired). Whether each *other* comparator's refusal path
  is reachable on its own case's data was not established.
- **The blob-hash half of rule 2 was not performed.** §10.4 compares commit
  timestamps. It does **not** verify that the frozen pre-registration blob and the
  frozen comparator blob are byte-identical to what ran — the check
  `scripts/check_comparator_freeze.py` exists for, and the check §3.6 did perform
  by hand for VMFL005 and VMFL001-R2. **`docs/LAB_STATE.md:10405`'s item is
  therefore half-closed, not closed.**
- **16 of 46 skew rows required a run directory this lane could locate by naming
  convention.** `K0b_D403_RERUN`, `K0b_D406_REPAIR`, `T1b_L4_EXT2`,
  `T1b_L4_PLANTED_ZERO_CONTROL` and `T3_R_FF` have pre-registrations in the
  population and **no run directory found under the convention searched** — they
  are **NOT MEASURED**, not cleared.
- **dafoam's 75 population paths and closure's 3 were counted, not skew-tested.**
  Their run roots are not under a convention this pass could enumerate from git
  alone. Every dafoam verdict named in §10.3 is quoted from its record, and no
  dafoam pre-registration timestamp was measured.
- **The 5 `*gate_*.json` paths are counted and not graded.**
- **27 of 98 `*RESULTS*` records returned no parseable verdict line** to the
  vocabulary scan. Some of those are genuinely verdict-free lane notes; some
  publish under branch labels the scan cannot see (§10.5). **The split between
  those two was not measured**, and until it is, "27" is a scan limitation and not
  a count of undeclared results.
- **`grep -r` was used nowhere in the population step (L-75)**, but the frame is
  **tracked files at HEAD only**. Untracked run outputs, gitignored case archives
  and the out-of-git data roots (`/home/ubuntu/{closure-data,
  closure-challenge-benchmark,certonomous-runs}/`) are **outside this frame
  entirely**, and no count here says anything about them.
- **mtimes are evidence about a filesystem, not a notarised clock.** A restored,
  copied or `rsync`'d artifact carries a mtime that need not date the solve. §10.4
  is as strong as that assumption, which the §10.1 control showed can mislead in
  the fail-open direction if the artifact class is chosen carelessly.
- **The proposed extension is a proposal.** It gates nothing, no comparator
  consults it, no verdict in this repository depends on it, and adopting it is a
  supervisor-and-Sanaa matter, not this lane's.

*Lines whose number changed above this section: 0.*

## 11. DATED SECTION, 2026-08-27 — A **SECOND DIRECTION** OF FAIL-OPEN, MISSED BY EVERY SECTION ABOVE: THE GATE THAT **MEASURED** ITS CONDITION, **RECORDED** IT, **PRINTED** IT, AND THEN GRADED AS THOUGH IT HAD NOT

**Appended at the foot; nothing above edited. `Lines whose number changed above
this section: 0` — proved rather than asserted: the HEAD blob was verified to be
a byte-exact PREFIX of this file in the same shell invocation that wrote this
section. Found by this supervisor while auditing a heat-transfer correction, and
carried here because this audit is where the class belongs. Ruled in full at
`docs/L342_GRADER_AUDIT.md` Addendum 5 (`a9632c6f`); this section records the
CLASS, not the case.**

### 11.1 The instance, cited so it can be re-derived by content

`17436d64:verification/runs/T-family/T1_runs/analyse_t1b.py`, frozen at
`08732fd6` with all nineteen cases unsolved — a correctly pre-registered,
prediction-first comparator.

It encodes **limb (1)** of `CLAUDE.md` standing rule 5 faithfully, at `:172-187`:
any level not iteratively `CONVERGED`, or not plateaued across 60/70/80 D, emits
`NOT A RESULT` with a machine-written `why`. **Limb (2) — the triple-state gate —
is absent.** At `:193` the verdict is composed as

    verdict = "PASS" if dev <= bpct else "GATE FAIL"

and `g["state"]` appears nowhere in it. The state **is** computed, by
`3d566802:…/analyse_t1c.py:321-335 gci()`; it **is** written into the record; it
**is** printed. Its only role in the verdict is **cosmetic**, at `:203`, where it
decides whether `p` and the GCI are shown.

**Result, in `c35d4db4:…/gate_t1b.json` at HEAD:** rows B0/B2/B4/B6 carry
`"verdict": "PASS"` on triples that are **DIVERGENT / DIVERGENT / DIVERGENT /
STAGNANT** (p −0.2189 / −0.1504 / −0.0585 / +0.0105), with `GCI_pct` correctly
`null` on all four. **The instrument was right about the half of rule 5 that
forbids quoting a GCI off a non-monotone triple, and silent on the half of the
same sentence that forbids the verdict.**

### 11.2 WHY EVERY SECTION ABOVE MISSED IT — and this is the point of the section

§§1–10 hunt a gate that **could not fire**: an exception path that swallows a
failure, a comparator whose refusal is unreachable, a control that cannot see a
non-zero, a threshold never evaluated. **This gate fired perfectly.** Its
condition was evaluated, its value is correct, and it reached the record. What
failed is the **wiring between the measured condition and the composed verdict**.

**So there are two fail-open directions and this audit had a name for one:**

| direction | what is broken | how it is caught |
|---|---|---|
| **(A) — §§1–10** | the condition is **never evaluated**, or its refusal is unreachable | reachability: plant a failure and require the refusal |
| **(B) — this section** | the condition **is** evaluated and **does not reach the verdict** | **read the verdict expression and require every recorded gate field to appear in it** |

**A planted-failure control of the (A) kind CANNOT catch a (B) defect.** Plant a
divergent triple into `analyse_t1b.py` and it will faithfully record DIVERGENT —
and still return `PASS`. The control passes; the gate is open. **Every guard in
this lab that was proved by a planted failure has been proved against direction
(A) only.** That is not a claim any of them are broken; it is a statement about
what their proof covers, and it was not previously written down.

**THE TEST FOR (B), stated so it is checkable by a reader holding the file:**
*for every field a comparator records as a gate condition, that field's
identifier must appear in the expression that composes the verdict — or its
absence must be justified in the file.* `g["state"]` recorded, `g["state"]`
absent from `:193`, no justification: that is the whole detection, and it is a
grep plus a read, not a run.

### 11.3 The aggravating fact, and it is the finding worth carrying

**The defect was disclosed twice and corrected neither time.**

1. `07313b68`, the commit that landed the record, is titled *"T1b passes all four
   rows as returned, and every grid triple is divergent or stagnant"* — **the
   defect named in the act of committing it.**
2. `59c345bd:…/analyse_t1b_L4.py:138` carries the comment *"the frozen rule, for
   contrast: the same DIVERGENT triple PASSES under it — this is the defect the
   amendment closes"*, and at `:144-151` **hard-codes the recorded triples and
   asserts the correct verdict**. This supervisor ran it: **rc 0, PASSED.**

**A frozen, committed, executable assertion of the correct verdict has been
passing for days beside the record it contradicts.** For this audit's purposes
that is a distinct hazard from an unfired gate: **an unfired gate is a hole
nobody knows about; this is a hole with a green light next to it.** A sweep that
looks only for missing checks will not find it, because the check exists,
executes and passes — in a file that grades a different rung.

### 11.4 What is and is not claimed

- **No verdict moves anywhere in the lab from this section.** The prose reading
  boundary was already closed at HEAD in three places, including this team's own
  `e2b2d44a:docs/CAPABILITY_GRID.md:149`, whose cell verdict is **CAN NOT DO**
  precisely because of this. No census was flattered.
- **This is not an L-342 row and not re-gradeable.** The lab-wide re-grade
  population stays at **one** (dafoam D12R phase 1).
- **The population of direction-(B) defects in this repository is NOT MEASURED.**
  One instance is one instance. §11.2's test has not been run across the ~236
  paths of §10's population, and stating a count from one hit would repeat
  exactly the coverage-as-census defect this team published against itself in
  the L-342 audit's Addendum 1. **What is offered here is the class and its
  test, not a census.**
- **The sweep is proposed, not run, and it gates nothing.** No comparator
  consults this section and no verdict depends on it.

*Lines whose number changed above this section: 0.*
