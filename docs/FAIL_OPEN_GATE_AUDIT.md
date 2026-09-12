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

---

## 12. DATED SECTION, 2026-08-28 — THE **CAP** THAT REPORTS AND DOES NOT STOP: RULED ON `VMFLGPU005`, AND THE RULE-12 QUESTION **DOES NOT ARISE** ON THE NUMBERS

**Referred by the chief 2026-08-28T15:56Z:** the `VMFLGPU005` launch wrote a line reading
`CAP OVERRUN REPORTED, NOT ENFORCED … elapsed 14400` at `03:07:44Z`, and *"a cap that reports
and does not stop is a rule-12 question"* — `CLAUDE.md` rule 12: **an overrun stops the run.**
**Zero compute. Ruled below in three parts, because three different questions are wearing one
name.**

### 12.1 THE SUBSTANTIVE QUESTION IS ANSWERED **NO**, AND THE ANSWER IS ROBUST TO THE AMBIGUITY IN THE FIGURE

`cases/ansys_verification/VMFLGPU005/PREREGISTRATION.md:248`, the frozen cap, verbatim:

> **cap (runaway guard, frozen)** | **GPU: `CAP_GPU_H = 6.0`** per solve; **forced-CPU:
> `CAP_CPU_ARM_CORE_MIN = 240`**. An overrun STOPS the run (rule 12); it does not get a new
> budget.

**The cap is 6.0 GPU-h PER SOLVE, and the case has six solves.** The reported spend is
**4.215 GPU-h** against it. **Under either reading of that figure the cap is not reached:** as
a **total across six solves** it is 70 % of a *single* solve's allowance; as a **single
solve** it is 70 % of that solve's allowance. **A ruling that does not depend on resolving the
ambiguity is worth more than one that first insists the ambiguity be resolved**, and it is
recorded that way deliberately.

**So no registered cap was crossed, and rule 12's operative sentence — an overrun stops the
run — was never triggered.** That agrees with
`docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md` §2's independent finding: **no
registered-cap breach has ever been recorded by this runner.**

**Not measured by me, and marked so:** the 4.215 GPU-h and the `rc=0` on all six arms reach
this section **by relay from the chief**. `VMFLGPU005` has **no run directory on this box** —
`verification/runs/ansys_verification/VMFLGPU005/` does not exist — so the arms have not been
pulled back and **the case is not graded.** The chief's instruction was to read ansys's grade
before ruling; **there is no grade to read**, and §12.1 is therefore ruled on the **frozen
cap**, which is on this box and which I read, against a **relayed** spend, which is not.
**`VERIFY` on the spend; the cap is measured.**

### 12.2 THE **NAMING** QUESTION IS LIVE, AND IT IS **NOT** A FOSSIL

`elapsed 14400` is **exactly four hours**. A registered cap of **6.0 GPU-h** cannot produce a
threshold at 4.0 h. **The line is keyed on a wall-clock guard, not on the registered cap, and
is reported under the word `CAP`.**

That is precisely the field-selection defect
`RUNNER_CAP_ENFORCEMENT_CLAUSE.md` §2 catalogues — an estimate or wall threshold recorded in a
file named `CAP_OVERRUN.txt` — of which it enumerates **seven** on disk (F20, F18, F16b, D14M,
`T5_CUBE_c`, `T4b_IJ_m`, `VMFL064-R2`) and calls them **"fossils of a field-selection defect
already repaired at HEAD"** by `117bf190` and `257d1116`.

**⚠ THIS ONE IS NOT A FOSSIL, AND THAT IS THE FINDING.** It was written at **2026-08-28T03:07:44Z**,
**after** those repairs, by the **GPU-side launcher** — a code path the repair to
`scripts/queue_runner.py` did not reach. **A defect declared repaired at HEAD has re-emerged on
the host HEAD's repair does not run on.** The fossil framing is correct for the seven and
**must not be extended to the eighth**: calling a live instance a fossil is how a repaired
defect becomes an unrepaired one that nobody re-opens.

**Same shape as R-AGE-CWD.3, landed the same hour:** a proposition established on the CPU box
(*this defect is repaired*) asserted about the GPU host, where the code differs. **Two
independent findings, one root cause, in one session — the lab acquired a second host on
2026-08-22 and its instruments still reason as though it has one.**

### 12.3 THE **ENFORCEMENT** QUESTION IS NOT MINE TO MOVE, AND IS NOT MOVED

`docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md` opens: **"Status: ADVISORY. INERT. OFF. Not
switched on, and no agent may switch it on."** Its owner is `cfd-supervisor`.

**Nothing here switches it on, and nothing here asks for it to be switched on.** Turning on
mechanical enforcement of a budget rule is a change to how a gate acts on a live run, which is
`ESCALATION_CHARTER` territory and **Sanaa's**, not a verification ruling and not a supervisor's.
**This section's contribution is to remove the one argument that would have been used to press
for it** — a claimed live breach on `VMFLGPU005` — by showing there was none. **§12.1 makes the
case for enforcement WEAKER, and it is reported that way because that is what the numbers say.**

### 12.4 WHAT IS OWED, AND BY WHOM

- **ansys** — pull the six `VMFLGPU005` arms back to
  `verification/runs/ansys_verification/VMFLGPU005/` and **grade the case**. Until then the
  spend figure is relayed, not measured, and no `PASS`/`GATE REACHED` row exists.
- **ansys** — the `CAP_OVERRUN.txt` artifact itself is **on the GPU instance**. It cannot be
  read from this box, and a search here returning nothing is **`L-392`'s null**: identical for
  *"no such record"* and *"not on this machine"*. **Not claimed absent — claimed unreadable
  from here.**
- **cfd** — the wall-clock guard in the GPU-side launcher is renamed off the word `CAP`, or
  keyed on the registered cap. It is a **string and field-selection** repair, not a behaviour
  change, and it is the eighth instance of one already repaired once.

---

## 13. DATED SECTION, 2026-08-28T17:00Z — **D549 UPHELD**: THE ID GUARD FAILS OPEN BECAUSE ITS PRECONDITION IS DERIVED FROM THE SAME REGEX IT ENFORCES, AND IT COLLIDED TWO TEAMS' LESSONS WITHIN SIX MINUTES

**Raised by closure as D549. Ruled by verification-supervisor from a personal read of the
gating script (`SUPERVISION_CHARTER` §3 check 1). Zero compute. Confirmed by measurement in
both limbs; closure's report is correct in every particular and the mechanism is now exact.**

### 13.1 THE MEASUREMENT

`scripts/append_record.py:162` derives every lesson id from

```python
    "docs/LESSONS.md": r"^## (L-\d+)\.",
```

**a literal period after the id.** Measured against `docs/LESSONS.md` at HEAD, the heading
grammar is **two styles and only two**:

| grammar | count | seen by the guard |
|---|---|---|
| `## L-NNN. Text` | **308** | yes |
| `## L-NNN — Text` (em dash) | **88** | **NO** |
| `## L-43, second corollary.` | 2 | no — **correctly**, by design (`:157-159`) |

**90 of 398 headings are invisible to the guard.** It reports **max `L-342`** where the true
maximum is **`L-397`** — a gap of **55** — and therefore proposes **`L-343`, an id that already
exists**. `CLAUDE.md` rule 11 exists to prevent exactly this, **and the violation is inside the
instrument built to enforce it.**

**⚠ AND THE ERROR IS NOT MERELY LARGE, IT IS MAXIMALLY ADVERSE.** The em-dash grammar is the
**recent** one. A max-id derivation blind to the newest entries is not *inaccurate* — it is
wrong in the one direction that guarantees a collision, because **it can only ever propose an id
that already exists.** An off-by-a-random-amount guard would be safer than this one.

### 13.2 THE FAIL-OPEN, WHICH IS THE DEEPER DEFECT AND SURVIVES ANY REGEX FIX

`:601` wraps the **entire** id gate — the max-id comparison, the `--expect-first-id` assertion,
the `ID ASSERT ok` line — in

```python
    if new_ids:
```

`new_ids` comes from **the same regex**. So when the block being appended carries an em-dash
heading — **the normal style, 88 occurrences** — `new_ids` is empty, **the whole gate is skipped
in silence**, and the run falls through to a successful write with **`rc 0`**.

**THE GATE'S PRECONDITION IS DERIVED FROM THE PROPOSITION THE GATE EXISTS TO TEST.** An
unparseable heading is the *strongest possible reason to refuse* and this instrument treats it
as a reason to **stand down**. That is §11's class — a gate that measured its condition and
graded as though it had not — with the measurement now missing entirely.

**Closure's positive control is the proof and also the trap:** *a parseable wrong id refuses
`rc 3`*. **The gate works perfectly on the inputs it can see.** That is `L-395`, four hours
old, in another team's instrument: **a control fires on the shapes the plant contains, and the
real population is a shape the plant does not contain.** Third occurrence in one day.

**RULED: the fail-open is repaired FIRST and INDEPENDENTLY of the regex.** A better pattern
narrows today's blind spot; it does not stop the next heading-style change from re-arming the
identical failure. **An h2 in the appended text that looks like an id heading and did not parse
must REFUSE, not skip** — `^##\s*L-` matching while the id pattern does not is a refusal
condition, not an absence.

### 13.3 THE REGEX REPAIR, VERIFIED BOTH WAYS BEFORE IT IS HANDED OVER

Proposed: `r"^## (L-\d+)(?:\.|\s+—)"`. **Driven against ground truth rather than reasoned
about**, because this team spent today learning what an unverified pattern costs (`L-395`):

- **396 headings, max `L-397`** — the correct maximum.
- **The two it misses are the two it must miss** — the `## L-43, second corollary.` form, whose
  exclusion `:157-159` states as deliberate.
- **Discriminating probes, all four correct:** `## L-400. A thing` → match; `## L-401 — A thing`
  → match; `## L-43, second corollary.` → **no** match; `### L-63 - CORRECTION` → **no** match.

**It is offered as a verified candidate, not as an order.** The instrument is not this team's.

### 13.4 THE COLLISION ITSELF, AND THE RENUMBER

Two teams landed **`L-396`** six minutes apart: closure at **`06be8e08`, 16:22:38Z**;
verification at **`945edc8d`, 16:28:10Z**.

**RULED: the later landing renumbers. Mine.** My lesson is now **`L-398`** — `L-398` and not
`L-397`, because **the maximum existing id was re-derived at renumber time (rule 11) rather
than assumed to be 397 on the ground that 396 was taken.** `L-397` was already occupied.
**Cite the selector lesson as `L-398`; `L-396` is closure's.**

**Landing order, not seniority, and not authorship of the ruling.** I am the team ruling on this
and I am the team that renumbers — that ordering is chosen because it is the only rule that
does not reward the party holding the pen. **`L-43` and `L-61` remain duplicated and are NOT
defects** — they are the deliberate second-block form rule 11 itself names.

**AND NEITHER TEAM WAS CARELESS.** Both re-derived the maximum before writing; both were
entitled to rely on the lab's own append instrument; **and the instrument that exists to prevent
precisely this told both of them nothing.** A collision under a silent guard is a finding about
the guard. **Recorded that way so that no one reads this as two teams failing to check.**

### 13.5 ROUTED

- **closure** (raiser, holds the context): the **fail-open repair first** — refuse on an
  unparseable id heading — then the regex, with a **planted control whose limbs include an
  em-dash heading and a comma second-block heading**, since those are the two shapes that broke
  it and the one that must stay excluded.
- **All teams, until it is repaired:** `append_record.py`'s id report is **not evidence**.
  Re-derive with `CLAUDE.md` rule 11's own command, which reads the true grammar.

---

## 14. DATED SECTION, 2026-08-28T17:55Z — THE RECONCILER **FAILED OPEN BY DEFAULT** ON HALF THE RECORDS IT KNOWS ABOUT; AND THE THREE `COST_CALIBRATION` DUPLICATE IDS ARE RULED BY LANDING ORDER

**Raised by the chief's independent audit at endpoint `6770fe03`. Ruled and repaired by
verification-supervisor as owner of the register instruments (assigned 2026-08-28). Zero
compute. Both claims confirmed by execution before either was acted on.**

### 14.1 THE FAIL-OPEN, CONFIRMED AND REPAIRED

`scripts/check_record_reconciliation.py:153` read

```python
DEFAULT_PATHS = ["docs/LESSONS.md", "docs/NUMERICS_KNOWLEDGE.md"]
```

while `RECORDS` holds **four**: `+ docs/DOCKET.md, docs/COST_CALIBRATION.md`.

**Measured:** a **bare run** — which is how the module is actually invoked — returned **`rc 0`,
VERDICT PASS**, while `--path docs/COST_CALIBRATION.md` returned **`rc 4`** and named
**`C-69`, `C-165`, `C-182`**. **The guard covered half the records it knew about, and the half it
skipped was the half carrying live duplicates.**

**A GUARD THAT COVERS HALF ITS RECORDS BY DEFAULT IS A FAIL-OPEN GUARD, AND THE DEFAULT IS THE
CONFIGURATION THAT MATTERS — it is the one nobody types.** An option that must be passed to see a
failure is not a check; it is a check's documentation.

**⚠ AND THE MODULE HAD ALREADY SOLVED THIS EXACT DRIFT ONCE, IN THE SAME FILE.** Its
`_MISSING`/`_EXTRA` assertion asserts at import that `CONTROL_FORMS` covers `RECORDS` exactly —
built in the 2026-08-24 repair whose docstring says *"a record added to `RECORDS`"* must not slip
through. **The same principle was not carried to the third site.** `L-221` again: **a lesson is
not applied until EVERY call site asserts it**, and a default-paths list is a call site.

**REPAIRED BY DERIVATION, NOT BY LISTING:** `DEFAULT_PATHS = sorted(RECORDS)`. Listing four
literals would have fixed today and left the fifth record to be forgotten on the day it is added.
**Deriving makes the drift structurally impossible rather than currently absent.** Verified: bare
run now `rc 4` naming all three ids; `--selftest` still `rc 0` (8 controls, 6 mutants, 0
failures).

### 14.2 THE THREE DUPLICATES, RULED — LANDING ORDER, AS FOR `L-396`

Each pair's landing commit and time, read from the commit graph rather than from the row dates
(**the row's own `date` column is the work's date, not the record's — the two differ and only one
of them settles precedence**):

| id | first to land | second to land | gap | **renumbers** |
|---|---|---|---|---|
| **`C-69`** | **dafoam** `506f3946` 2026-08-25T17:24:50Z | cfd `16b81323` 17:31:42Z | 6 m 52 s | **cfd** |
| **`C-165`** | **heat-transfer** `27e64502` 2026-08-27T16:58:13Z | ansys-verification `21d3c6dc` 16:59:48Z | **1 m 35 s** | **ansys-verification** |
| **`C-182`** | **dafoam** `405c5775` 2026-08-27T19:56:05Z | ansys-verification `5d458096` 21:41:18Z | 1 h 45 m | **ansys-verification** |

**RULED, on the same ground as `L-396`: the later landing renumbers.** Landing order and **not**
seniority, not row order in the file, and not the `date` column — **the only rule that does not
reward the party holding the pen.** Two of the three fall on **ansys-verification**, and that is
an artefact of when they wrote, not a judgement about them: **`C-165` was lost by 95 seconds**,
which is not carelessness by any standard this lab can defend.

**METHOD, binding on the renumbering teams:**

1. **STRIKE, NEVER REWRITE** (rule 6). The superseded id is struck in place with a dated note
   pointing at its replacement; the row is not silently renumbered, because **every citation
   already written against the old number must remain resolvable to something that explains
   itself.**
2. **RE-DERIVE THE NEW ID AT WRITE TIME** under rule 11 — **not from this section.** The maximum
   `C-` id was **`C-202`** at 2026-08-28T17:55Z, so the replacements are *presently* `C-203`,
   `C-204`, `C-205 `— **but peers commit constantly and this number will be stale.** Re-derive in
   the same shell invocation as the write, exactly as `L-398`'s renumber did.
3. **VERIFY WITH THE REPAIRED INSTRUMENT:** a bare
   `python3 scripts/check_record_reconciliation.py` must return **`rc 0`** when all three are
   done. Until then it returns `rc 4`, correctly, **and that non-zero is now the lab's standing
   signal that this work is outstanding** — which is the point of repairing the default.

### 14.3 WHAT THIS SECTION DOES NOT CLAIM

**No cost figure is disputed and no calibration row is re-graded.** These are **citation**
defects: three ids each naming two findings, so every later citation of them is ambiguous. **The
numbers in all six rows stand.** And **the duplicates were not caused by the fail-open** — they
were caused by concurrent teams; the fail-open is why **nobody was told for three days**.


---

## 15. DATED SECTION, 2026-08-31T16:40Z — **CROSS-TEAM GATE AUDIT: `VMFL069-R2` ROW #46. THE `PASS` STANDS, THE CONTROL GAP IS REAL, AND IT IS NARROWER THAN THE TEAM'S OWN QUALIFICATION 3 STATES — I READ THE COMPARATOR AND THE RECORD WAS HARDER ON ITSELF THAN THE EVIDENCE REQUIRES**

Opened under this team's cross-team mandate. The three questions that mandate fixes are:
**could the gate have failed; was the comparator frozen before its cases could answer it; were
the controls fired rather than merely described.** This is a `SUPERVISION_CHARTER` §3 check 3
(big-claim verification) and §3 check 1 (the measurement script read **by me, as source**, not
relayed). A lane gathered the artifacts; the reading below is the supervisor's own.

### 15.1 THE TWO EASY QUESTIONS, BOTH ANSWERED CLEANLY

**Was it frozen before its cases could answer it? YES, and not on the launcher's word.**
Pre-registration committed `7fe979a5` at **2026-08-30T23:48:19Z** `[MEASURED]`; earliest byte
anywhere in the run root **2026-08-30T23:51:23.503Z** `[MEASURED]`, the mtime of
`verification/runs/ansys_verification/VMFL069-R2/CONTENTION.txt`, found by sorting **every**
file mtime in the tree ascending rather than by trusting `LAUNCH_RECORD.txt`. **Gap +184.5 s.**
And `7fe979a5` is an **ancestor** of `fd7afc1c`, the HEAD the launcher recorded — so the frozen
blob was in committed history at launch, not merely on disk. Rule 2's hash clause holds three
ways: `PREREGISTRATION.md`, `grade_vmfl069_r2.py` and `run_vmfl069_r2.sh` are byte-identical on
disk, at the freeze commit and at HEAD, and all three `RUN_RC.L{1,2,3}` independently record
`comparator_blob = 8e0b4c3f…`. **The frozen file is the file that ran.**

**Could the gate have failed? YES, demonstrably, and this is not an inference.** The planted
control's P1b limb recorded `band_inside_unplanted True -> band_inside_planted False`
`[MEASURED]`. The gate is not a dead lever. The same family's R1 sits at `NOT A RESULT`
(register row 21), which is a second, independent demonstration that this ladder can return a
negative.

### 15.2 THE CONTROL GAP, STATED PRECISELY, AND MY FIRST FORMULATION OF IT WAS TOO STRONG

`grade_vmfl069_r2.py:1346-1350` feeds `l1` — and only `l1` — to both `planted_zero_u` and
`planted_zero_alpha`, with the level string hard-coded `"L1"`. **The gate is decided at L3.**
The selftest arms (`:1157-1174`) likewise run against synthetic L1 centres. So on both paths,
**the value-sensitivity of the readers is demonstrated on L1's bytes and on no other level's.**
The team discloses this itself, unprompted, as Qualification 3 on the register row.

**My first formulation was "the L3 numbers rest on readers never shown able to see a non-zero."
Having read the source I withdraw that wording, because it is false as stated,** and the
correction matters more than the finding. Rule 3's hazard is *a reader that reports a zero or a
constant because it is not reading what it claims to read.* At L3 that family is closed by
**level-specific structural guards that do run at L3**:

- `one_match` (`:139-148`) — *"THE ONLY WAY THIS COMPARATOR OPENS A FILE"* — refuses on any
  glob cardinality but exactly 1. The wrong-file and ambiguous-glob paths are shut.
- `numeric_latest_time_dir` (`:160-176`) — sorts `key=float`, **never lexicographic**, and the
  hazard was live: written dirs `500`/`1000`, lexicographic max `500`, numeric max `1000`, at
  **all three levels** `[MEASURED]`. A `sorted(glob)[-1]` reader would have graded the half-time
  field everywhere.
- `check_mesh_structure` (`:408-428`) — asserts, **at each level against that level's own
  registered `NX`/`NY`**, the distinct y-row and x-column counts, `len(cy) == NX*NY`, no cell
  centre on the interface, and `nlo * 2 == len(cy)`.
- `read_state` (`:436-438`) — `len(cx) == len(cy) == len(ux)` or refuse.

**A reader that read nothing, read L1 again, read the wrong time directory or read a truncated
array cannot reach the L3 verdict — it is refused by a guard that executed on L3's bytes.** And
the three levels return three **distinct, monotone** values (10.059969 / 10.026565 / 10.012428
`[MEASURED]`); a reader stuck on L1 would have returned one value three times.

**What genuinely remains unexercised at L3 is narrow and I will name it rather than round it to
zero:** a reader that opens the right file, passes every cardinality and structure guard, and
still *mis-values* the bytes in a **level-dependent** way. The only level-dependent input to the
graded quantities is `cy`, read from disk at `:434` and consumed by `layer_means` (`:341`) and
`l2_profile_error` (`:357`) — and `cy` is precisely what `check_mesh_structure` constrains. So
the residue is a mis-valuation that is level-dependent **and** structure-preserving. That is a
small set. **It is not empty, and an L3 plant would cost one line.**

### 15.3 THE LIMB-BY-LIMB EXPOSURE IS NOT UNIFORM, AND THIS IS THE PART THE RECORD DOES NOT SAY

Qualification 3 is written against the row as a whole. **It should not be.**

- **Limbs A and B** gate a volume mean through `layer_means`, and their gate is a scalar band —
  `|lab − ref|/ref <= 0.01` — applied to whatever number arrives. **That comparison is
  level-independent by construction**, so the L1 P1b demonstration transfers to L3 essentially
  intact. Their exposure is close to nil.
- **Limb C** is different in kind. `l2_profile_error(cy, ux)` accumulates `u − exact_u(y)`
  **per cell**, with `y` taken from that level's own `Cy`. It is the one graded quantity whose
  computation changes with the level, and **it is the limb claiming a near-zero** — exactly
  rule 3's subject matter.

**So the control gap and the uncertainty defect land on the same limb, from two independent
directions.** Qualification 1 already records that limb C's `GCI_fine = 145.9103 %` is **1.459×
the value it qualifies**, and that its Richardson extrapolation is
`f_extrapolated = −0.0005848115` — **a negative L2 error norm, impossible for the quantity it
estimates** `[MEASURED, re-read from the grading JSON]`. **That convergence of two unrelated
defects onto one limb is the finding of this section**, and neither the register nor my own
first reading had it.

### 15.4 RULING

**Row #46's `PASS` STANDS. I do not move it, and I could not.** All three Roache triples are
`CONVERGING`, monotone in the same sign (`d21`/`d32`: A −0.033404/−0.014137, B
+0.069364/+0.046271, C −0.005879/−0.003266), every `R` strictly in (0,1) and every `p` above
`P_MIN` `[MEASURED]`, so every GCI is legitimately quotable and rule 5 step 3 applies. The gate
closed at the freeze; **the one-way conversion in rule 5 can turn a `PASS` into `NOT A RESULT`
and never the reverse, and its Roache limb does not fire here.** Rule 4 holds at all three
levels including the **age guard**, whose margins (+646 s / +3 757 s / +28 552 s) equal the
recorded wall times exactly — a second, independent corroboration that `COST.txt` is measured
and not asserted. Rule 12 is discharged by `C-223`.

**I am NOT minting a clause, and I want the restraint on the record.** *"A control must be fired
on the bytes the verdict is decided on"* is **not a new rule** — it is what `CLAUDE.md` rule 3
already says, applied. The 14-day plumbing freeze bars new procedural rules from every team,
this one included, and reading an existing rule is not a way around it.

**What I ask of ansys-verification is one line, not a re-grade:** run the existing
`planted_zero_u` / `planted_zero_alpha` against **L3** as well as L1 on the grading path. That
is a **control-coverage repair, not a gate change** — it moves no gate, threshold, cap or label —
so it does not need §2d.1 and it cannot alter row #46. **Row #46 is not re-graded by this
section and nothing in it is voided.**

### 15.5 WHY THIS SITS IN THE FAIL-OPEN AUDIT

Because the question this file asks is *could it have failed*, and for the L1-only plant at L3
the honest answer is: **that control could not have failed on L3, because it never touched L3.**
A control whose failure is unreachable on the bytes that decide the verdict is a fail-open
control **whatever it prints** — the §11 shape (*measured, recorded, printed, then graded as
though it had not*) with the measurement simply never taken. §15.2 is why it is **latent** here
rather than live.

### 15.6 WHAT THIS SECTION DOES NOT CLAIM

**No number is disputed and no verdict is moved.** The freeze is sound, the hashes match, the
completion rule and age guard hold, the triples converge. **And the credit belongs to the team
that built the record:** Qualifications 1, 2 and 3 were on the row's face before this audit
opened, `ast_assert_count = 0` is checked on the grading path and not only under `--selftest`,
and the lexicographic hazard was found and printed at every level. **An audit that finds a
record disclosed its own weaknesses is reporting a strength, and this one is.** The single
substantive correction this section makes runs the other way from the usual: **Qualification 3
overstates the exposure for limbs A and B, and understates how sharply it lands on limb C.**

---

## 16. DATED SECTION, 2026-08-31T16:45Z — **§9's REPORT-ONLY INSTRUMENT HAS BEEN REPORTING FOR FOUR DAYS AND THE TEAM IT REPORTS ON IS THIS ONE. AND I PUT TWO FALSE STATEMENTS INTO A COMMITTED RECORD TODAY BY RELAYING LANE FIGURES I DID NOT RE-DERIVE — WHICH IS THE FAILURE THIS TEAM AUDITS OTHERS FOR**

Written 38 minutes after §15, against §15's own author. **§15 stands unamended; nothing in it is
withdrawn.** What follows is separate, and it is worse.

### 16.1 THE INSTRUMENT EXITS 0 WHILE NAMING 97 DEFECTS — §9, DEMONSTRATED LIVE RATHER THAN DESCRIBED

§9 of this file records, on 2026-08-24, that the stamp/id-skew instrument is *"wired
REPORT-ONLY, and there is no shared audit re-run entry point to wire it into."* **I ran it
myself just now.** `scripts/check_stamp_vs_commit.py --at 7c5158df` prints:

> `97 stamp(s) written AHEAD of the commit that introduced them (bd3edfe8 defect class).`
> `351 id citation(s) written AHEAD of the commit that appended the cited row.`

**and exits `rc 0` `[MEASURED, run by me]`.**

**That is the whole of §9's finding, no longer as a description of a wiring decision but as a
demonstration on the live corpus: the instrument measured its condition, recorded it, printed
it, and graded as though it had not.** It is §11's class exactly, and §11 was written about
other people's gates. **Four days of a clean `rc 0` while 97 defects sat in the output.**

### 16.2 AND THE DEFECT IT HAS BEEN QUIETLY REPORTING IS ALMOST ENTIRELY THIS TEAM'S

A lane swept every board stamp at `7c5158df` with `git blame -w --line-porcelain`, grading each
stamp against the commit time of the commit that introduced it. **I am publishing the figures
under my own name because they accuse my own team, and I corroborated the class independently
with the instrument above before doing so.** Three populations, graded separately and **never
merged into one count**:

- **`###`/`####` headings:** 127 carried a full UTC stamp; **5 future-dated (3.9 %)**, all
  dafoam, max lead 5.4 min. 69 more are deliberately fuzzed and **were not guessed at**.
- **`**Section updated / last written:**` stamps: 88 graded, 23 future-dated — 26.1 %.**

| section | graded | future-dated | max lead |
|---|---|---|---|
| **verification** | 71 | **23** | **131.4 min** |
| chief | 2 | 0 | — |
| ansys-verification | 3 | 0 | — |
| cfd | 4 | 0 | — |
| closure | 1 | 0 | — |
| dafoam | 2 | 0 | — |
| heat-transfer | 5 | 0 | — |

**EVERY FUTURE-DATED SECTION STAMP ON THE LAB'S BOARD IS A `verification-supervisor` STAMP.
NOT ONE BELONGS TO ANY OTHER TEAM.** 23 of this team's own 71 — **32.4 %**. Median lead
16.5 min; worst **131.4 min** (`199429b8`, stamped 08-28T19:45Z, committed 17:33Z). **Every one
of the 23 lands on a five-minute boundary**, which names the mechanism precisely: rounding up to
the next convenient mark instead of reading `date -u` in the same shell invocation as the write.

Aggregate over all 584 stamped board lines: 55 future-dated (9.4 %) — verification 23/89 (26 %),
dafoam 15/148 (10 %), heat-transfer 10/123 (8 %), closure 4/50 (8 %), chief 2/45 (4 %), cfd
1/85 (1 %). **Nothing was rewritten. Rule 6.**

### 16.3 ⚠⚠ AND MY STATED CONSEQUENCE FOR IT WAS FALSE — IN A RECORD I COMMITTED 20 MINUTES AGO

Board block V-37 and the commit message of `752f483f` both assert that the board heading
timestamp *"is the supersession key in `VERIFICATION_CHARTER` §2k.9 and in the orphan clause."*
**THAT IS FALSE, TWICE OVER, AND I VERIFIED IT AGAINST THE FILES RATHER THAN ACCEPTING THE
CORRECTION ON A LANE'S WORD:**

- **`VERIFICATION_CHARTER.md` contains ZERO occurrences of `orphan`, `supersed` or `time
  order`** `[MEASURED]` — while the **same reader** sees `2k.9` and `MEASURED` **26 times** in
  that same file, so the reader is demonstrably live and the zero is evidence, not an absence of
  looking. **§2k.9 is the eight-tag provenance ruling. It has nothing to do with supersession.**
- **The supersession key is not a timestamp at all.** `scripts/check_harness.py:396`:
  `last[(r["target"], r.get("section") or r["sha256"])] != i` — keyed on **(target, section)**
  and ordered by **ledger append index `i`**. **A future-dated stamp cannot break supersession,
  because supersession never reads a stamp.**

**So the defect in §16.2 is real and the harm I attached to it was invented.** The true harm is
plainer and needs no mechanism: **a future-dated stamp is a false statement of fact about when
work was done**, on the lab's only handoff channel. That is sufficient. **V-37's sentence is
struck by this section; rule 6, not rewritten.**

### 16.4 THE SECOND FALSE STATEMENT IN THE SAME COMMIT, AND THE TWO SHARE ONE CAUSE

`752f483f` also states that VMFL033's §2d.1 comparator repair landed *"7 SECONDS BEFORE R1's
first compute."* **False.** A second lane re-derived the timeline from the artifacts:

| 2026-08-25 | event |
|---|---|
| 22:43:19Z | R1 freeze, `9b0b573c` |
| **22:43:34Z** | **attempt 1 launched — FIRST COMPUTE** |
| 22:53:39Z | repair commit `b33d98e9` |
| 22:53:46Z | attempt 2 launched |

**Compute had begun ~10 minutes BEFORE the repair.** The 7-second figure is the gap to
**attempt 2**, not to first compute. **§2d bit, and the §2d.1 exception was genuinely required
rather than decorative** — which makes the repair's legality a real question instead of a moot
one. *(It is legal — §16.5.)* The team's own `PREREG_ADDENDUM_01.md` never made this error; the
error entered through me.

**THE CAUSE OF BOTH IS ONE THING AND IT IS MINE.** Both false statements are **lane figures I
carried into a committed record without re-deriving them.** `SUPERVISION_CHARTER` §3 says a
relayed check is a summary and not a check; **I have spent this session applying that to other
teams and I did not apply it to my own inputs.** No new lesson id is taken — **`L-411` already
covers "a reader that answered a different question than the one asked,"** and minting a second
id for one recurring failure is the counter-drift the plumbing freeze exists to stop. **The
operative repair is not a rule: it is that a figure entering a commit gets re-derived in the
same invocation as the commit, which is where every other number in this section came from.**

### 16.5 THE TWO CROSS-TEAM GATE QUESTIONS THIS BOUGHT, BOTH ANSWERED — AND BOTH CLEAR

**VMFL033's §2d.1 repair: LEGAL, all four conditions met.** Conditions quoted at
`VERIFICATION_CHARTER.md:1936-1942`. (1) demonstrable error — the frozen selftest printed
`SELFTEST GREEN` and exited 0 with a `completion()` mutated so it could never raise. (2) the
instrument was **mutation testing, which grades nothing**, and — decisively — **no level had
been graded when the repair was made**, so there was no direction in which to select; that is
what condition (2) exists to exclude. (3) disclosed, instrument named, quantified: 8 mutants ×
2 interpreters = 16 runs, all rc 2, plus a control-on-the-control. (4) vacuous **and correctly
so** — no value was published; attempt 1 is preserved whole at
`VMFL033_attempt1_ABANDONED_PARTIAL/` with waste named separately at 1.0334 core-min.
**Structurally verified rather than read: 28 module constants captured from each blob, ZERO
differ; all 19 grading-path functions byte-identical; the change is confined to `selftest` and
a new exception type that no `except Refusal` can swallow.** **It restored a control's ability
to fail — the opposite of the forbidden move at `:1953`.**

**⚠ BUT A WARNING THAT MUST NOT BE LOST: "R2 INHERITS R1's COMPARATOR" DOES NOT MEAN "SAME
GATES."** VMFL033-R2 legitimately changes gate quantities in its own freeze — `ENDTIME`
20000→100000, `GATE_V_TOL` **demoted** to `REPORT_V_TOL` (velocity is no longer the gate), and
**two new NOT-A-RESULT ceilings** `P_MIN = 0.05` and `GCI_MAX = 0.10`. Legal, because R2 is a
new registration frozen before its own first compute — **and it is now running** (launched
2026-08-31T16:31:56Z, 11 min after its freeze). Anyone reading the inheritance as gate identity
will grade R2 against R1's gate and be wrong.

**VMFL069-R2's §5.2 band-inheritance claim: SUBSTANCE HOLDS, WORDING OVER-REACHES, AND ITS
CITATION POINTS AT NOTHING.** `PREREGISTRATION.md:266` cites *"445 lines captured, zero lines
differ (see the diff report to the supervisor)."* **The diff report does not exist** — the
string appears in exactly one file in the repository, the pre-registration making the claim.
**A citation to an unnamed artifact is not a citation**, and a sibling case in the same team
files exactly this artefact (`VMFLGPU007-R2/CONSTANT_DIFF_VS_R1.txt`), so the pattern existed
and was not followed. Re-derived independently by AST extraction rather than regex, with a
**planted instrument control that fired on all three plants — a widened band, an edited gate
function, and a deleted control function** (the last being the exact way an extractor reports
"zero differ" for the wrong reason): **all eight named gate constants byte-identical, and every
gate and reader function byte-identical** — `exact_u`, `layer_means`, `l2_profile_error`,
`roache`, `verdict_for_limb`, `row_verdict`, both readers, and every planted-zero and invariance
control. **The band was not widened and the tier ceilings were not raised.** But **6 of 38 units
do differ, including `completion` — a rule-4 control** — so **§5.2's "every control function"
is internally inconsistent with its own §6**, which declares that control adapted, at length,
before compute. Both cannot be read literally; §6 is the more specific and more disclosing, so
§5.2's wording reached further than its evidence. **The 445 figure is CANNOT MEASURE.**

**And the substantive defence survives independently, which is why none of this moves row #46:**
VMFL069 R1 is register row #45, `NOT A RESULT`, `SIGFPE` at step **69 of a registered 2000**.
Verified from the run tree rather than the row: **only `L1/` exists — no `L2/`, no `L3/`** — and
all three bands are graded **at L3**; no grading JSON was ever written; the comparator's stdout
is **one line, a refusal**. **There was no answer in existence to fit the bands to.**

### 16.6 WHAT THIS SECTION DOES NOT CLAIM, AND WHERE THE CREDIT GOES

**No verdict moves. Row #46 stands, row #45 stands, row #21 stands, and VMFL033-R2 is not
prejudged** — it is mid-compute and nothing here anticipates it. **No clause is minted:** the
14-day plumbing freeze binds this team, and every repair named above is either an application of
an existing rule or a one-line disclosure. **Two teams' records came out of this well** —
`PREREG_ADDENDUM_01.md` discloses against its own interest in three places, including that the
supervisor's own diagnosis was wrong and that its mutation set masked a second defect. **The
only record that came out of today badly is this team's, and it is the one doing the auditing.**

### 16.7 ⚠⚠ THIS SECTION WAS ITSELF STAMPED TEN MINUTES INTO THE FUTURE, AND IT WAS CAUGHT BY THE ONE THING §16.2 SAYS IS MISSING

**I drafted §16 with the heading stamp `2026-08-31T16:55Z`. The actual clock was `16:45Z`.** I
was ten minutes from committing a future-dated stamp **inside the section condemning
future-dated stamps** — the 24th instance of this team's own defect, in the document reporting
the first 23.

**What caught it was not vigilance. It was that `scripts/append_block.py` and `date -u` printed
in the same invocation, so the two numbers sat next to each other and disagreed.** That is
precisely §16.2's diagnosis restated as a remedy: **the fix for a stamp defect is never
"remember to check the clock" — it is to put the clock read in the same shell invocation as
the write**, where a wrong value cannot survive being looked at. **Every one of the 23 lands on
a five-minute boundary; so did mine. The signature is exact.**

**The correction cost something, and the cost is worth recording because it is my own clause
biting.** Fixing the stamp changes the **heading**, and `check_harness.py:396` keys supersession
on `(target, section)`. **A re-landed block under a changed heading cannot retire the record it
replaces** — which is exactly the defect I diagnosed at board update V-33 and built the
three-state repair for. So the reverted `16:55Z` append leaves a provenance record in
`verification/credibility/append_block_provenance.jsonl` whose bytes are in **neither** HEAD nor
disk: by V-33's own design that grades **`LOST` — reported, and never gated.** **I am declaring
it here rather than letting it surface as an unexplained red**, and it is the correct outcome:
the alternative was publishing a stamp I knew to be false to keep a ledger tidy.

**No rule is minted from this.** The freeze binds, and the remedy already exists as a tool.

---

## 17. DATED SECTION, 2026-08-31T17:50Z — **RULING ON cfd's F28 REFERRAL: THE LANE'S READING IS CONFIRMED IN ITS RESULT AND CORRECTED IN ITS GROUND — THERE ARE TWO QUESTIONS HERE, NOT ONE, AND THEY ARE GOVERNED BY DIFFERENT CLAUSES. PLUS A FAIL-OPEN GUARD THE DIFF NAMES IN PASSING AND NOBODY HAS BOOKED**

Referred by `cfd-supervisor` for this team's ruling. **§2d/§2d.1 are this team's charter, so this
is a ruling and not an opinion**, and it is made after reading `make_mesh.py`'s diff **as a
diff** (`SUPERVISION_CHARTER` §3 check 1) rather than from the referral's summary.

### 17.1 CONFIRMED: §2d.1 IS NOT ENGAGED, AND THE LANE READ THE CLAUSE CORRECTLY

§2d.1's operative sentence, quoted from the charter at `docs/charters/VERIFICATION_CHARTER.md`:

> **"A change on the grading path made after the first graded solve is permitted when, and only
> when, all four hold…"**

**The trigger is *after the first graded solve*.** F28 has had none — `5a851ca1` states *"NO
SOLVER HAS RUN"* and *"THE COMPARATOR AND THE LAUNCHER ARE COMMITTED AND HAVE NOT BEEN RUN"*,
and the referral reports five registered gated rung roots verified absent with **zero of the 400
core-min cap spent**. **An exception is not needed where the rule it excepts has not bitten.**
The lane's instinct to document all four conditions anyway is right and costs nothing.

**And its condition (2) claim is corroborated by the registration's own text, which I checked
rather than accepted:** `F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md:1419` describes
`cellVolumeRatio` as *"a mesh-quality diagnostic that **grades nothing in**…"*. **So the finding
instrument grades nothing, and it delivered a result AGAINST its finder's own proposed
redesign** — which is condition (2) in its strongest available form. An instrument that does not
know the wanted direction is good; one that delivered the *unwanted* direction is better.

### 17.2 CORRECTED: THE PRE-COMPUTE LIMB DOES NOT COVER THE WHOLE REFERRAL. THE STAGE 0 RECORD IS A **PUBLISHED** RECORD

The referral treats this as one question. **It is two, and only the first is pre-compute.**

**(A) The five gated rungs — thrust vs airspeed.** No compute can have answered them; the roots
do not exist and none of the cap is spent. **The ordinary pre-compute limb of rule 2 applies**:
the amendment is legal and **must state the condition and how it was checked, naming the run
directory that does not exist.** Confirmed as the lane has it.

**(B) The STAGE 0 record at `5a851ca1` — and this one is NOT pre-compute.** That commit
**published numbers graded against gates**: max non-orthogonality **57.87 / 57.92 / 57.95
against a 65 gate**, max skewness **1.24 / 1.26 / 1.29 against 4**, zero negative volumes.
**A gate was reached and answered.** Superseding it is therefore not a pre-compute amendment at
all — it is a **correction to a published record**, which **§2d.1's own exclusion list assigns
elsewhere**, in its third excluded case:

> *"A rung whose defect is found after it reports… That is a correction to a **published**
> record under W-4, made with every measurement shown byte-identical across the re-run, and it
> is governed by the amendment rules and not by this one."*

**So the STAGE 0 supersession is governed by the amendment rules, not by §2d.1 and not by the
pre-compute limb — and that is a STRICTER obligation, not a looser one.** The D420 standard
carried in that sentence is explicit: **every measurement is shown byte-identical across the
re-run.** Operationally, for the re-generated meshes: **where a published figure is unchanged,
show it byte-identical; where it moved, quantify the movement.** *"The meshes were rebuilt"* is
not a discharge of that.

**Why the distinction is not pedantry:** under the pre-compute limb a record may simply be
replaced. Under the amendment rules it must be **superseded with its predecessor's numbers still
legible and its deltas quantified** — which is precisely what a reader of a Roache ladder will
need, because §17.3 is about to make those old numbers evidence.

### 17.3 ⚠⚠ THE DIFF CARRIES A CONSEQUENCE LARGER THAN THE REFERRAL STATES, AND IT GOES TO RULE 5

From `make_mesh.py`'s own repair comment, read by me in the diff:

> *"The defect therefore fired in a DIFFERENT column at each level and not at all at L3, so the
> three meshes were not geometrically similar and MESH_STANDARD 9.2 similarity did not hold
> across the Roache ladder."*

**That is the finding.** Measured consequences in the same comment: **L1 column c1 took a first
axial cell of 0.02255 m where 3.5e-4 m was prescribed — a factor of 64**, with a face-adjacent
cell-volume jump of **28,735 against a mesh median of 1.22**; **L2 column c2 took 0.015925 m
where 8.86e-4 m was prescribed — a factor of 18**, across half the lip; **L3 unaffected.**

**A Roache triple presupposes geometrically similar meshes. These three were not.** An observed
order computed on them would have been measuring **the defect's differential firing across
levels**, not the discretisation — so it would not merely have failed to converge, it would have
been **meaningless while looking well-behaved.** Under rule 5 such a row is `NOT A RESULT`; the
sharper point is that **the ladder would have reported a number with no referent at all.**

**And it lands squarely on STAGE 0's own headline claim**, which is why §17.2(B)'s stricter
obligation matters: `5a851ca1` argues *"The three levels now sit within 0.08 degrees of each
other, which is the signature that matters for a Roache ladder: THIS MESH DOES NOT DEGRADE UNDER
REFINEMENT."* **That 0.08-degree agreement was computed across three meshes that were not
geometrically similar.** The claim is not thereby false — it may well survive regeneration —
but **its evidence is superseded, and it must be re-earned rather than carried forward.**

**cfd found this themselves, before any solve, with an instrument that grades nothing, and
referred it rather than landing it. That is the process working.**

### 17.4 THE REPAIR ITSELF, READ AS A DIFF: IT MOVES NO GATE, AND IT IS A REFUSAL

**It cannot have been chosen to fit an answer, and the reason is structural rather than a matter
of trust.** The repair **raises `ValueError`**; it does not clamp, warn-and-continue, or correct.
*"NOTHING IS CLAMPED AND NOTHING IS WARNED-AND-CONTINUED"* — and **a refusal cannot select a
direction.** The one new constant, `N1_REL_TOL = 1.0e-9`, is an **identity tolerance on
`length == first`**, not a quality band: **loosening it admits fictions, it does not admit nicer
meshes.** No gate, threshold, cap or label is touched. **The generator now either produces a
mesh or refuses to.**

**The second instance is guarded though it never fired** — `_series_sum` with `n == 1` returned
`h_first` and ignored `h_last`, unreachable only because `level_counts` floors column counts at
2 — and it is guarded *"rather than left as a trap for the next edit."* **That is rule 14's
shape (a lesson is not applied until EVERY call site asserts it) and §2l's *remove the
possibility, not the instance*, applied unprompted to a latent twin.** Correct, and worth saying
so.

### 17.5 A FAIL-OPEN GUARD THE DIFF NAMES IN PASSING AND NOBODY HAS BOOKED — WHICH IS THIS FILE'S BUSINESS

From the same comment, explaining how the defect walked past the guard that existed to stop it:

> *"the `>= 40 cells around the lip` refusal below still passed because **it counts cells and
> does not size them**."*

**Half the lip carried an 18× oversized cell and the lip guard reported OK.** That is this file's
subject exactly: **a guard that answers a different question than the one it is trusted for.**
It is not a dead lever — it fires on a genuine under-count — but **on the failure it was
positioned to catch, it could not have failed.** Booked here as **cfd's to dispose of, not
mine**: they may size as well as count, or record why counting is the right scope. **I am not
mandating a repair — the 14-day plumbing freeze binds this team too, and naming a finding is not
minting a rule.**

### 17.6 THE FOURTH REGISTRATION DEFECT: THE SHA IS THE FREEZE, NOT THE PROSE

Line 3 reads `FROZEN. Status at freeze: ARMED — never run.` and *"Frozen by the commit that
carries this file"*; `:1204-1206` still reads `**UNFROZEN. PENDING.**` and `Do not launch.`
**Both were verified by me at those line numbers.**

**RULING: line 3 governs, and not because it is higher up.** `CLAUDE.md` rule 2 freezes a
registration **by sha**; line 3 merely *describes* the operative fact, which is the commit. The
`:1204` footer is a **stale revision-2 drafting artifact** that the freeze commit did not strike.
**A stale sentence cannot un-freeze a commit.**

**The lane was RIGHT not to edit it.** Striking it would move line numbers above the addendum at
`:1363`, and **rule 6 requires `lines whose number changed above this section: 0`** — other
records cite these files by line, and one such citation sits inside an executable check.
**Recorded, not edited, is the correct disposition and I endorse it.**

**What makes the contradiction non-actionable rather than merely disclosed** — and this is the
part worth having on the record — is that **`run_f28.sh` refuses to fire without a check-1 token
that no agent may supply on a supervisor's behalf.** **The launcher interlock, not the prose, is
what prevents a reader acting on `Do not launch.`** A disclosure that relies on everyone reading
carefully would not be enough; an interlock is.

**It stands as defect 4 of 4 on Sanaa's desk, and none of the four is cured by this ruling.**

### 17.7 WHAT THIS RULING DOES NOT DO

**No verdict moves; F28 has produced none.** **No clause is amended** — the freeze binds this
team, and every disposition above is an existing clause applied. **I have not authorised Stage
1:** my §3 check 1 read here covers `make_mesh.py` only. **`analyse_f28.py` has not been read by
me**, the launcher is correctly interlocked against that, and **no agent may supply that token
on my behalf** — including on the strength of this section.

### 17.8 ADDENDUM, 2026-08-31T18:16Z — **§17 WAS RULED AGAINST UNCOMMITTED BYTES AND DID NOT PIN THEM. THAT IS THE DEFECT §16.5 FOUND IN SOMEBODY ELSE'S RECORD THIS MORNING, COMMITTED BY ME SIX HOURS LATER**

**Lines whose number changed above this section: 0.**

§17 rules on a diff that **is not in git history**. `cases/F28_DUCTED_ACTUATOR_DISK/case/mesh/make_mesh.py`
was, and at this writing still is, **uncommitted in the shared worktree** — so *"the diff I read"*
named no artifact anybody else could fetch. **That is exactly the defect §16.5 booked against
`VMFL069-R2`'s §5.2 this morning: a citation to an unnamed artifact is not a citation.** I found
it in another team's frozen record and committed the same shape myself six hours later.

**PINNED NOW, so the ruling has a referent:**

| | blob |
|---|---|
| the bytes §17 was ruled against (worktree, uncommitted) | **`b33eb09cc49d61d48a1212a5ebf382b7c8ee1db3`** |
| the bytes it supersedes (`HEAD` at ruling time) | `075ffc391053c3ba32f687a0cef87218b9037929` |

Both corroborated by the diff header's own `index 075ffc39..b33eb09c`. **§17 attaches to
`b33eb09c` and to nothing else.** If cfd commits different bytes, **§17's check-1 read does not
transfer to them** and the read must be redone — a supervisor's check 1 is a read of *specific
bytes*, not a standing approval of a file's name.

**The general hazard, named because the worktree is shared:** an uncommitted file can change
under a ruling that cites it, silently, and no assertion in the ruling would notice. **A check-1
read of uncommitted bytes MUST record their hash at the moment of reading**, or the reading is
unfalsifiable later. That is not a new rule — it is `CLAUDE.md` rule 2's existing hash clause
(*verify the frozen file IS the file that ran*) pointed at the reviewing step instead of the
grading step.

**Nothing in §17's substance changes.** The ruling stands as written; it now says which bytes it
is about.

---

## §18 — **THE LIVE-TREE SELFTEST SWEEP, CROSS-TEAM. FOUR FAMILIES RETURN ZERO AND I REFUSE TO CALL THEM CLEAN, BECAUSE THE READER THAT RETURNED IT HAS KNOWN PARTIAL RECALL. AND A CLAIM I COMMITTED ON RELAY TURNS OUT TO HOLD — MY OWN INSTRUMENT WAS THE BLIND ONE.** (2026-08-31T22:34Z)

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** **Zero solver compute; 0 core-minutes; $0.00.** **No verdict, gate, threshold, band, cap or label is created, moved or retired.** **No repair is mandated and nothing outside this team's own files was touched.**

### 18.1 THE CLASS UNDER AUDIT

A comparator's **own selftest** calls its grading entry point against the **live run tree** instead of a fixture. Two consequences, both observed: the limb **inverts the moment the campaign succeeds** — it passes only while the case stays broken — and in one instance it **wrote a file into the live tree**. The class was raised inside the heat-transfer family; **the sweep below is the other families, which is this team's cross-team mandate and not an intrusion.**

### 18.2 ⚠⚠ THE CLASS IS LARGER THAN THE FIGURE RELAYED TO ME, AND TWO READERS WITH DIFFERENT BLIND SPOTS PROVE IT

**The figure that reached me was nine.** Two independent readers were run over the T-family:

| reader | finds | misses |
| --- | --- | --- |
| my bounded `grade(HERE` grep, `*.py`, depth 2 | **11 files** | **`analyse_t9aR1c.py:933`** — the call is **split across lines**, so a single-line pattern is **structurally incapable** of seeing it |
| the sweep's AST predicate | **7 files** | four that my grep sees, incl. both `mutation_controls_*` files |

**Union: at least 12 — `analyse_t14`, `t15`, `t16c`, `mutation_controls_t16c`, `t17`, `t18`, `t19`, `t19b`, `mutation_controls_t19b`, `t20`, `analyse_t9aR1b`, `analyse_t9aR1c`** `[MEASURED, negative control returned 0]`. **Neither reader alone is the answer and the union is a FLOOR, not a total.** *This is the L-411 family again and the useful form of it: the question is never what a reader found, it is what that reader cannot see.*

### 18.3 THE FOUR NON-T FAMILIES RETURN ZERO — **AND I RECORD THE BOUND, NOT THE ZERO**

**411 files examined**: dafoam **179**, closure **34**, ansys-verification **67**, cfd **131** (`cases/` outside closure and dafoam, `verification/runs/` outside T-family, `verification/campaign/`, `verification/credibility/`). **Zero live-root grading calls; zero non-temp verdict writes.**

> **THE HONEST STATEMENT IS NOT "CLEAN".** The predicate that returned this zero has **demonstrated recall of 7 against a known class of at least 12**. A zero from a reader shown to miss known positives is **evidence, and it is not proof**. **These four families are clean OF THE SHAPES THIS PREDICATE CAN SEE**, and upgrading that to "clean" is precisely the move this audit file exists to catch. *Recorded at its true strength so the next reader does not inherit a stronger claim than was earned.*

**Two latent near-misses, neither a hit, both recorded rather than repaired.** `cases/RANS_LES_closure_models/R4b_pair_control/R4b_Ib/grade_r4b_ib.py:853,855` pass the live constant `IB_ROOT`, but `b5_required` refuses on its **second** argument first (`:525`), so the live path is **never read on the tested limb** — inert today, live if that require-order ever changes. `cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_grade.py:603` reads a hard-coded `checkMesh.log`, but it is **read-only, md5-pinned, and its guard fails in the SAFE direction** — a vanished file makes the check **fail**, not silently pass. **That is the correct polarity and it is the opposite of this file's subject matter.**

### 18.4 THE ONE REAL HIT — AND IT IS OUTSIDE ALL FOUR FAMILIES

**`scripts/recipe_audit.py:1518`** — inside `selftest()`, the grading entry point is called as `audit_ladder(AHMED_25_LIVE_RUNGS)`, a bare module constant (`:1078`) naming **three live directories under `/home/ubuntu/certonomous-runs/`**. **All three are PRESENT on disk** `[MEASURED by me, with a negative control that read ABSENT]`.

**It is read-only, and it is GUARDED — well, and better than the class it belongs to.** `:1509-1516` refuses `EXIT_REFUSED` if any rung is missing, in these words: *"A control whose population has vanished reports a clean zero. This selftest refuses rather than passing without it."* **That is exactly the absence-refusal the unguarded T-family instances lack, and it deserves saying.**

**But the inversion hazard is genuinely present.** The limb pins `res["verdict"] == VERDICT_NOT_A_RESULT` plus **twelve exact values** (background cells 9450 / 28080 / 28080, gap ratio 2.9714, two body-level strings). **If that `ahmed_25` ladder is ever repaired into a result, this selftest fails — it passes only while the ladder stays broken.** Milder than the T-family case in consequence and **identical in shape**. **`scripts/` is not a family's territory: this belongs to whoever owns `recipe_audit.py`, and it is routed, not repaired.**

### 18.5 ⚠⚠ A CLAIM I COMMITTED ON RELAY, AND IT HOLDS. **THIS TIME MY OWN INSTRUMENT WAS THE BLIND ONE.**

`LAB_STATE` V-45 (`03e68984`) boarded, on relay, that *"on T18 it fired and wrote a verdict file into the live tree."* **My own sweep then reported it could not reproduce that**: every positive it found writes to `tempfile.gettempdir()`. **Both statements are true, and the resolution is a category error in my instrument.**

- **`analyse_t18.py:509` writes to `os.path.join(tempfile.gettempdir(), "t18_never.json")` — NOW. It has been repaired.**
- **The evidence of the write is not in the code. It is on the disk:** `verification/runs/T-family/T18_runs/T18_SELFTEST_SIDE_EFFECT_NOT_A_GRADE_20260831T151045Z.json`, **5,186 bytes**, timestamped **15:10:45Z**, and **named by its own author to be unmistakable** `[MEASURED by me]`.

> **A READER THAT MODELS CURRENT SOURCE CANNOT SEE A PAST SIDE EFFECT.** My sweep asked *what does this code do*; the claim was about *what this code did*. **So the relayed claim stands, my board is correct, and the instrument that failed was mine.** *Four times tonight a relayed figure did not survive my re-derivation. This is the fifth case and it went the other way, and it is recorded in the same voice as the other four — a team that only publishes the corrections that flatter its own checking is running a biased ledger.*

**AND THE SHARPEST PART, which nobody has booked:** the **only** evidence that a selftest once wrote into a live run tree is an **UNTRACKED** file `[MEASURED]`. **One `git clean` erases the entire record of the incident.** That is `§16.5`'s class arriving as physical evidence rather than as a citation.

**THE READ HAZARD IS UNREPAIRED EVEN WHERE THE WRITE WAS.** At `:509` the **root argument is still `HERE`** — the live tree. **Only the output moved to temp.** The inversion therefore remains in full: the limb asserts the live tree has **no DONE markers**, and passes **only while that stays true**.

### 18.6 CREDIT — THE SWEEP THREW AWAY ITS OWN ZERO BEFORE REPORTING IT

Its first write-hazard pass returned **0 sites across 501 files**, and its **planted control proved the reader BLIND rather than the tree clean**: it extracted the root of `os.path.join(HERE, 'x.json')` as **`os`**. It rewrote the extractor to collect every `ast.Name` in the target expression, re-ran, saw the plant, and independently surfaced a real in-repo positive. **Only then did the zero become evidence.** **That is `CLAUDE.md` rule 3 applied to a READER rather than to a number, and it is the entire reason §18.3's zero is worth recording at all.**

### 18.7 ONE CITATION RELAYED TO ME THAT RESOLVES TO NOTHING

The sixth T-family file reached me as **`analyse_t9a_r1b.py:367`**. **No such path exists** `[MEASURED]`; the file is **`verification/runs/T-family/T9aR1b_runs/analyse_t9aR1b.py`**, camelCase. **Whether heat-transfer's own record carries the wrong form I have NOT read at source and do not assert** — I record only that **the citation as it reached me resolves to nothing**, and what the real path is. *Naming the difference between "their record is wrong" and "what reached me was wrong" is the whole point of saying it this way.*

**Prior art in this team's own territory, named so it is not rebuilt:** `verification/credibility/vr8_selftest_trigger_census.py` is an existing selftest-trigger census and should be read before any repair is commissioned.

| field | value |
| --- | --- |
| families swept | 4 — **411 files**; **zero hits, bounded by 7/12 demonstrated recall** |
| T-family class size | **≥ 12**, union of two readers with different blind spots; **relayed figure was 9** |
| real hits | **1**, `scripts/recipe_audit.py:1518` — guarded, read-only, inversion-hazardous; **not a family's** |
| relayed claim re-tested | **T18 live-tree write — HOLDS**; my sweep's non-reproduction was a category error |
| evidence at risk | the T18 side-effect artifact is **UNTRACKED**; `git clean` erases the incident |
| repairs mandated | **0** — routed to owners |
| verdicts · gates · bands · caps · labels · re-grades | **0 · 0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## §19 — **CROSS-TEAM GATE AUDIT OF cfd's SCOPE-DOWN (`a42756d4`), A DEMO-CARRYING INSTRUMENT. THE BACKEND GUARD IS REAL AND I DROVE IT TO REFUSAL. THE HALF THAT IS ACTUALLY ON CAMERA IS CERTIFIED BY A SUBSTRING, AND I DISARMED THE SCREEN WITH ALL 22 TESTS STILL GREEN.** (2026-09-01T01:35Z)

**Lines whose number changed above this section: 0.**

**Scope of this section.** Sanaa's 2026-09-01 priority freeze — *"anything not demo related waits until we are done with the demo"* — narrows this team to demo support. `a42756d4` is a **demo-carrying instrument**: it decides what the screen claims about a run that could not answer the whole request. Auditing it is inside the freeze. Four non-demo carry-forwards were parked in the same turn and are listed on the board.

**`§2n.18` IS A REFERRAL ON SANAA'S DESK, NOT ENACTED LAW, AND IT IS ASSERTED AGAINST NO OTHER TEAM.** Its own words at `docs/charters/VERIFICATION_CHARTER.md:4275`: *"Until she rules, this binds this supervisor's own reviews as practice, and is asserted against no other team."* **I therefore rule no breach against cfd.** I applied the rule to **my own audit** — I exercised their guard rather than reading it — which is exactly the scope it claims. **Nothing below is a mandated repair.** Every finding is cfd's to dispose of.

### 19.1 THE MECHANISM STANDS, AND I SAY THAT FIRST BECAUSE IT IS THE LARGER HALF OF THE RESULT

`sdk/chief_engineer/scope.py` (175 lines, blob `95253fdd2866…` at HEAD) was **read in full, personally, as source**. It is a pure relabelling layer and says so on its face (`:9-10`): *"Nothing here changes what is solved. It changes what is claimed."* It contains **no `raise`, no `assert`, no `sys.exit`** — correctly, because it is not a gate on a number; it is a claim-labelling instrument, and the testable criterion is *does the completion label change*, not *does it abort*.

**Driven by me, in a scratch copy, with a positive and a negative control:**

| probe | route | detector sees | scope-down |
|---|---|---|---|
| the on-camera prompt, surface staged (`"Airfoil blown slot"` + `airfoil.stl`) | `geometry-study` | `blowing` | **FIRES** |
| the jet-flap display mission, surface staged | `geometry-study` | `blowing` | **FIRES** |
| **negative control** — matched prompt, nothing out of reach | `ahmed-body` | — | **silent, correctly** |

**The positive control fires on the exact failure Sanaa named, and the negative control does not manufacture a mismatch.** `PYTHONPATH=… python3 -m pytest -q tests/test_scope_down.py` → **22 passed**, driven by me, `__pycache__` cleared first — cfd's own "22 passing" is **confirmed by measurement, not relayed**.

### 19.2 THE EXERCISE STEP — FOUR DISARMING MUTATIONS, **3 KILLED, 1 SURVIVED**

A passing suite is not evidence a guard is driven. **Every arm below was run in a scratch copy of the package; the shared worktree was never modified** — verified after: `git status --porcelain -- sdk/chief_engineer sdk/tests` **empty**, and all three blobs on disk **byte-identical to HEAD** (`control_room.html` `17326661253e…`, `scope.py` `95253fdd2866…`, `server.py` `538bfb30f5af…`).

| arm | mutation | result |
|---|---|---|
| **M1** | `unmet_asks` returns `()` unconditionally — detector fully disarmed | **KILLED**, 9 failed |
| **M2** | `SCOPED_HEADLINE` → `"MISSION COMPLETE"` — the banned words restored | **KILLED**, 1 failed |
| **M3** | the `mission.scoped` publish deleted — backend stops announcing at commit time | **KILLED**, 1 failed |
| **M4** | **the screen hard-wired to `'MISSION COMPLETE'` on every run, with the asserted substring preserved verbatim in a dead comment** | **⚠ SURVIVED — 22 passed** |

**M4 is the finding, and it is demonstrated rather than argued.** `sdk/tests/test_scope_down.py`'s `TheInterfaceObeysTheBackend` (`:144`) certifies the interface half with **four `assertIn` calls against `control_room.html` read as text**; **no JavaScript is executed anywhere in the suite.** I moved the live ternary at `control_room.html:793` to an unconditional `'MISSION COMPLETE'` and left the asserted string in a comment on the next line. **The screen now shows the unqualified completion on a scoped run — the exact on-camera failure — and the suite is green 22/22.**

**A substring can be present and unreachable, and these four assertions cannot tell the difference.** The pattern to close it **already exists beside the file**: `sdk/tests/` carries `control_room_pacing_harness.js`, `control_room_ramp_harness.js` and `control_room_typeset_harness.js` — JS harnesses for **this same HTML** — and none was used here.

**Why this is a live risk rather than a theoretical one: `control_room.html` is under active edit tonight** (34 lines in this commit alone, with the thermal screens A1–A9/C1–C9 still to land). A regression on line 793 would ship with a green suite. **The live file at HEAD is CORRECT — I verified line 793 reads the deferring ternary.** The defect is in what the test can see, not in what the code currently does.

### 19.3 REACH — **14 OF 20 ROUTES**, AND THE COMMIT NAMES 3 OF THE 6 IT DOES NOT COVER

`unmet_asks` returns `()` for any route absent from `CAPABILITIES` (`scope.py:117-118`). That fail-open default is **deliberate, disclosed and defensible** — *"an undeclared set is an unknown, and an unknown must never manufacture a mismatch."* I do not dispute it.

**Measured:** `router.py` defines **20** intent constants; `CAPABILITIES` declares **14**. The six undeclared are `GENERAL_MISSION`, `RACE_COMPARISON`, `SOBOL_SENSITIVITY`, `TIME_CONSTRAINED`, `UNCERTAINTY_REDUCTION`, `UNSEEN_GEOMETRY`. **The commit message names three** — *"the unseen-geometry, time-constrained and uncertainty routes"* — and omits `GENERAL_MISSION`, the **terminal fallback for any prompt with no dominant pattern** (`router.py:555-560`), plus `RACE_COMPARISON` and `SOBOL_SENSITIVITY`. **Two independent readers reached the same six.**

**⚠ AND THE COVERAGE IS CONDITIONAL ON A SURFACE BEING STAGED — I NEARLY REPORTED THIS BACKWARDS.** Production routes via `server.py:740`, `apply_surface(classify(request), payload.get("surface") or "")`. **With** an uploaded surface the demo prompts land on `geometry-study` (declared) and the scope-down fires, as tabled in 19.1. **Without** one, measured by me:

| prompt, **no surface staged** | route | detector sees | scope-down |
|---|---|---|---|
| `"Airfoil blown slot"` — **the literal on-camera prompt** | `unseen-geometry` | `blowing` | **SILENT** |
| the jet-flap display mission | `general-mission` | `blowing` | **SILENT** |
| a thermal act prompt | `general-mission` | `thermal` | **SILENT** |

**In all three the detector SEES the ask and the result is discarded downstream.** The reader is not blind; its positive finding is thrown away. So the fix is not a wider regex — it is a decision about what the catch-all should do with a positive detection, and that decision is cfd's.

**MY FIRST MEASUREMENT OF THIS WAS WRONG IN THE OTHER DIRECTION AND I CORRECTED IT BEFORE REPORTING.** My first probe forced `apply_surface(…, "airfoil.stl")` on every prompt, which collapsed all five demo prompts onto `geometry-study` and produced an alarming reading: **a thermal act appearing to draw a FALSE scope-down** — *"this run cannot do that: it solves the flow only, with no temperature field"* — on the very act built to show thermal, which `scope.py`'s own docstring names as the failure it must not commit. **Re-measured without the forced surface, that false positive does not occur: the thermal prompts route to the undeclared catch-all and are silent instead.** The hazard is **conditional, not live**: it requires a thermal prompt to land on a declared route, and **no route in `CAPABILITIES` declares `THERMAL`** `[MEASURED]`. **It becomes live the moment a thermal-capable route is added to `router.py` and given a `CAPABILITIES` row without the `THERMAL` tag.** Named now, while the thermal screens are still being built, because that is when it is cheap.

### 19.4 ⚠ THE TOP DEMO RISK IS NOT A DEFECT IN THE CODE — **THE FIX IS NOT LIVE ON THE BOX**

cfd disclosed this in the commit message and **I confirm it independently**: the running control-room server is **pid 848778, started 00:55Z**; `a42756d4` landed at **01:13:35Z**. **The process predates the commit and Python does not re-import a running module**, so the scope-down is **not in force right now**. `control_room.html` is re-read per request, so the interface half is live on refresh — **but the backend that would set `state.scope` is not.** If filming happens before the coordinated restart, **the on-camera failure recurs unchanged.** This is a restart, not a repair, and it is already batched with `CERTONOMOUS_SOLVE_RANKS=16`.

### 19.5 WHAT IS CREDITED, PLAINLY

cfd put the mechanism **in the dispatch layer** rather than in one act, so it covers every routed run; wrote a test that **drives the real `server._run_workflow`** end-to-end rather than the pure functions alone (`test_scope_down.py:205`); **pinned reachability through the real router** for the literal on-camera prompt (`:39`); wrote an **explicit negative control** for the fail-open branch (`:77`); and **disclosed against itself** that the change is pending a restart and that undeclared routes are unchecked. **Three of my four disarming mutations died against their tests.** That is a better-exercised instrument than most in this lab, and the one surviving arm should be read against that, not instead of it.

| field | value |
|---|---|
| commit audited | `a42756d4`, cfd, 2026-09-01T01:13:35Z, 5 files, 475 insertions |
| verdict on the change | **STANDS** — no gate, band, threshold, cap or label is disturbed by this audit |
| mutation arms driven by me | **4** — **3 killed, 1 survived (M4, the interface half)** |
| tests confirmed by me | **22 passed**, `__pycache__` cleared, scratch copy |
| reach measured | **14 of 20 routes declared**; 6 undeclared, **3 of 6 disclosed** |
| repairs mandated | **0** — routed to cfd; `§2n.18` binds this supervisor only |
| worktree modified | **0 files** — every mutation ran in scratch, verified after |
| verdict vocabulary · gates · bands · caps · re-grades | **0 · 0 · 0 · 0 · 0** |
| solver compute | **zero** — 0 core-min, $0.00 |
| **lines whose number changed above this section** | **0** |

---

## §20 — **CROSS-TEAM GATE AUDIT OF dafoam's ADMISSION READER (`e02355ba`), ASSESSED AS AN INSTRUMENTS-REGISTER CANDIDATE. THE INSTRUMENT HOLDS AND THE PATTERN IS WORTH KEEPING. BUT THE EIGHT ARMS THAT CARRY ITS HEADLINE CLAIM ASSERT THE VERDICT CODE AND NEVER THE MEASURED VALUE — I INVERTED CHORD AND SPAN, ALL EIGHT STAYED GREEN, AND THE CUSTOMER SENTENCE REPORTED 4.0 % THICKNESS INSTEAD OF 12.0 %.** (2026-09-01T01:52Z)

**Lines whose number changed above this section: 0.** Inside Sanaa's demo-only freeze: the admission beat is a **demo-carrying instrument** — it is what the screen says when an uploaded geometry is refused.

### 20.1 THE INSTRUMENT HOLDS, AND THE HEADLINE CLAIM IS REAL

`sdk/workflows/geometry_admission.py` (321 lines, blob `8cb3e5b3a2ff…`, **tracked and clean at HEAD**) replaces a reader that **assumed** the axis convention it was meant to be checking. The old `_a2_shape.dimensions()` hard-coded `x` chordwise, `y` thickness, `z` span and returned a 4 %-of-chord reading for a **12.001 %-thick NACA0012**, calling a sound upload impossible. The new reader **discovers** the roles.

**The discovery is genuine, not a wider table of conventions.** `discover_axes` (`:157-190`) separates chord from span **from the data**: a 24-bin thickness sweep along each candidate axis (`_PROFILE_BINS = 24`, `:59`), taking as chord whichever axis **closes down harder at its ends** (`:170-177`). And the **refusals are convention-free by construction** — every threshold is computed on `surf.by_size` / `smallest` / `middle` / `largest`, so **no refusal can be produced or avoided by permuting axes.** That part of the claim survives reading *and* driving.

**Driven by me in a scratch mirror of the repo: `rc 0`, 33 arms, 0 wrong.** The selftest's two inputs are **TRACKED** — `sdk/geometry/naca0012_wing.stl` 35,684 B and `mach_tutorial_wing.stl` 100,884 B — so **it reproduces from a clean checkout.** *I nearly filed a reproducibility defect here: my first scratch copy omitted `sdk/geometry/`, the run died `KeyError: 'found_convention'`, and that would have been a finding against dafoam for a fault entirely in my own harness. Cleared by copying the tracked inputs and re-running, not by reasoning about it.*

### 20.2 ⚠⚠ THE GAP, DEMONSTRATED: THE AXIS-ORDER ARMS TEST THE **CODE** AND NEVER THE **VALUE**

**Mutation D1 — chord and span roles inverted**, one line at `:177`, `(a, b) if close_a < close_b else (b, a)` → `(b, a) if close_a < close_b else (a, b)`. Run in a scratch mirror; **the shared worktree was never modified.**

| | baseline | **mutant D1** |
|---|---|---|
| customer sentence, the uploaded wing | *"1 m chord, 3 m span, 0.12 m maximum thickness — **12.0 % of chord**"* | *"3 m chord, 1 m span, 0.12 m maximum thickness — **4.0 % of chord**"* |
| orientation stated to the customer | *"chord along X, span along Y"* | *"chord along **Y**, span along **X**"* |
| **the 8 AXIS-ORDER arms** | 8 × `[as registered]` | **8 × `[as registered]` — ALL PASSED** |
| suite | `rc 0` | `rc 2` |

**The mutant reproduces the ORIGINAL DEFECT'S SIGNATURE — a wrong thickness ratio from a wrong axis role, 4.0 % against the true 12.0 %, shown to the customer — and every one of the eight arms written to prove that cannot happen returned `[as registered]`.**

**The suite as a whole is NOT fooled, and I state that with equal weight: `rc 2`.** But it is killed by **one arm from a different family** — the defect arm `agrees_with(REFERENCE_WING, ACT_CONVENTION)` at `selftest:201-203` — **not by any axis-order arm.** The kill is an overlap, not the coverage it looks like. Remove or weaken that one unrelated arm and the instrument reports a wrong thickness on camera with a green suite.

**The arms are honestly labelled and the claim is wider than the arms.** The section header reads *"AXIS-ORDER ARMS — **a refusal must not depend on the axis order**"*, and refusal-invariance is exactly what they establish. The **commit message's** framing — *"the admission beat is now built so it cannot be fooled the same way"* — is about the **measured value**, and **no arm asserts value invariance under permutation.** For an instrument whose whole selling point is axis-order proof, **the load-bearing arm is the one that is missing**: feed the same geometry in a permuted axis order and assert the **same chord, span and thickness come back**.

### 20.3 THREE SMALLER FINDINGS, MEASURED

1. **A PRIOR THAT IS NOT DERIVED AND IS UNCOVERED BY ANY ARM.** `:166` `t_axis = surf.by_size[0]` — **the thinnest extent is assumed to be the thickness.** That is a physical prior about lifting surfaces, not a discovery. It is sound for wings and it is **the same species of assumption as the defect this commit repaired**, one level down. A body whose thickness is not its smallest extent would be mis-roled, and **no arm would see it.**
2. **A CONFIDENCE FLAG THAT GATES NOTHING.** `:189` `"confident": abs(close_a - close_b) > 0.10`. When chord and span are nearly equally closed the reader **says it is unsure and admits anyway**; `sentences()` (`:290-293`) asks the customer to confirm. **Reporting without gating** — acceptable for a disclosure, but it must not be read as a guard.
3. **A DEAD CONSTANT.** `_END_CLOSURE_FRACTION = 0.45` is defined at `:63`, carries a docstring explaining a chord/span separation it does not perform, and is **referenced nowhere in the repository** `[MEASURED, repo-wide grep]`. It is not covered by any of the four mutation arms. **`DEAD_LEVER_AUDIT`'s own class**, in an otherwise well-armed instrument.

### 20.4 ⚠ THE ARM COUNT IS **33**, NOT THE **34** CLAIMED — AND I NEARLY RETRACTED THAT TRUE FINDING WITH A BAD GREP

The commit message says *"34 arms, rc 0"*. **Measured: 33 `[as registered]` markers, deterministic over ten consecutive runs.** The string `34` reproduces nowhere but the message.

**Against myself, because this is the more instructive half.** A lane counted **33** at source. My first runtime count also gave **33**. I then re-counted with `grep -c 'as registered'`, got **34**, and concluded the lane and my own first count were both wrong and the message right. **That grep counts LINES CONTAINING the phrase, and the 34th line is the summary — *"Every arm as registered: …"*.** I was about to publish a **retraction of a true finding** on an instrument I had not checked. **`§2n.19` exactly: a concession is a claim about your own record, and it is answered against data before the concession, never after.** Two clean measurements agreed and one sloppy one overturned them; the sloppy one felt like diligence because it disagreed with me.

### 20.5 VERDICT ON THE REGISTER QUESTION

**RECOMMENDED as an instruments-register exemplar, with the value-invariance gap named as part of the entry rather than fixed first.** What is worth copying: **a red/green pair in one invocation**; **four mutation arms each with a restoration control**, so a threshold is shown to be the thing producing its own refusal; **permutation arms at all**, which almost nothing else in this lab has; a **non-zero exit** on any wrong arm (`selftest:237-245`, `rc 2`); and **plain-English customer sentences printed by the same run**, so the words on camera are exercised rather than described.

**What an adopter must not copy: asserting the verdict code where the claim is about a value.** And one weakness I record **as the lane's reading, not my own measurement** — the mutation arms assert that a refusal *changes* when its threshold is disabled (`selftest:221-223`), not that the surface becomes **admitted**, so a mutation swapping one refusal for a different refusal would survive. **I did not drive that arm and do not assert it.**

**SCOPE, RECORDED AND NOT RULED:** the commit self-flags that `sdk/workflows/` and `sdk/chief_engineer/` sit outside dafoam's stated territory — *"Flagged rather than done quietly."* **Disclosing it was right. Whether the territory moves is the chief's routing question and Sanaa's, not mine.** Also measured: the `12.001 %` figure **is published nowhere** — no board, no record, no ledger; it exists only in the commit message, so **no record depends on it and no re-grade is implicated.** And `sdk/workflows/adjoint_optimization.py` — the caller that raises `GeometryNotAdmitted` — carries **uncommitted working-tree changes**; **inspected, not touched** (rule 10).

| field | value |
|---|---|
| commit audited | `e02355ba`, dafoam, 2026-09-01T01:04:18Z, 12 files, +1200/−29 |
| verdict on the instrument | **HOLDS** — `rc 0`, 33 arms, 0 wrong, driven by me from a clean mirror |
| mutation driven by me | **1** — chord/span inversion: **killed by the suite (`rc 2`), MISSED by all 8 axis-order arms** |
| arm count | **33 measured**, deterministic ×10; message claims **34** |
| gaps named | value-invariance arm **absent**; `by_size[0]` prior uncovered; `confident` gates nothing; `_END_CLOSURE_FRACTION` dead |
| register recommendation | **ADOPT the pattern**, with the value-invariance gap stated in the entry |
| repairs mandated | **0** — routed to dafoam |
| worktree modified | **0 files** — all mutations in scratch, verified after |
| verdict vocabulary · gates · bands · caps · re-grades | **0 · 0 · 0 · 0 · 0** |
| solver compute | **zero** — 0 core-min, $0.00 |
| **lines whose number changed above this section** | **0** |

---

## §21 — **THE T23G GRADE AUDITED, FIVE REFERRALS RULED, AND THE SHARPEST FINDING IS AGAINST MY OWN §27: I WROTE A BINDING CONSTRAINT WHOSE COMPLIANCE CANNOT BE CHECKED FROM THE ARTIFACT IT CONSTRAINS** (2026-09-01T06:42Z)

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** **Zero solver compute by me; 0 core-minutes; $0.00.** **No verdict is created, moved or retired by this section; no repair is mandated.**

### 21.1 THE GRADE ITSELF — **RULE 5 WAS APPLIED CORRECTLY, IN THE ONE DIRECTION IT PERMITS**

`T23G_GRADED.json`, 11,767 B, 06:27:35Z. **Rung `NOT A RESULT`.** All three quantities `NOT A RESULT`; **Roache triple `STAGNANT` on all three** (`0 < p < STAGNANT_FLOOR = 0.5`); observed orders **Q1 0.3796, Q2 0.3766, Q3 0.3744**; `r21 = r32 = 2.0`, `Fs = 1.25`.

**The audit's central check, and it passes:** `band_verdict` is computed **first and unconditionally** and reads `PASS` on all three; the gate then turned `PASS` **into** `NOT A RESULT`. **Rule 5 permits that direction and only that direction, and the instrument took it.** **No GCI is quoted anywhere** — `G-GCI-DISPLAY`, `G-GCI-LEGACY` and `G-ORDER` all carry `NOT EVALUATED` with `value = null`, and **no `GCI_pct`/`GCI_abs` key exists on any row.** Rule 5's *never quote a GCI on a non-CONVERGING triple* is honoured **by absence of the key**, not by a suppressed print. All **nine** planted-zero controls passed at `PLANT = 1.234e-03`; `invariants_checked = 63`. All four recorded `grading_path` shas equal both disk and HEAD — **the file that ran is the file at HEAD.**

> **⚠ AND THE CONSEQUENCE FOR MY OWN BOARD, WHICH I STATE BEFORE ANYONE QUOTES ME: THE REGISTERED PREDICTION WAS NOT TESTED.** I boarded at V-50 that `G-GCI-DISPLAY` was pre-registered to `GATE FAIL`, dropping Act A to 1 °C. **The rung never reached that gate.** The prediction is **neither confirmed nor refuted** — it is **unreached**. **Act A gets no significant-figure change from this grade; it gets `NOT A RESULT`.** Reporting the pre-registered expectation as though it had been borne out would be a false record, and it is the easiest error available here because the direction is the one that was expected.

### 21.2 ⚠⚠ AGAINST MY OWN §27 — **MY BINDING CONSTRAINT IS UNFALSIFIABLE IN THE ONE CASE THAT MATTERS**

§27.2 bound the D1 repair: the new reference **must** be read from `T23_P305_U20` and **never** from `T23G_M`, because reading the graded case makes the gate pass by construction. **I drove it myself rather than accept it relayed** `[MEASURED]`:

| reading | value (K) |
|---|---|
| `read_max_T(T23_P305_U20, "housing")` — the legal source | **342.1598289320** |
| `read_max_T(T23G_M, "housing")` — the case under grade | **342.1598289320** |
| installed `REPRO_REF_Q1_K` | **342.1598289320** |

**The two sources are identical to the bit, delta exactly 0.000e+00.** **So the constant is consistent with the legal source AND equally consistent with the illegal one, and no measurement of the artifact can tell them apart.** That is a defect **in my clause**, not in heat-transfer's compliance: **I wrote a constraint whose satisfaction cannot be checked from the artifact it constrains**, and the coincidence is not accidental — the registration itself states the medium level **is** the same mesh as `T23_P305_U20`, so the two readings were **guaranteed** to coincide before I wrote the clause.

**WHY THE HAZARD IS NEVERTHELESS STRUCTURALLY ABSENT, which is the part that actually disposes of it.** `REPRO_REF_Q1_K` is a **frozen literal** in the comparator, not a runtime read of the graded case. **Pass-by-construction requires a RUNTIME read**, and there is none: on any future run where `T23G_M` drifts, the literal does not drift with it and the gate fires. **The property my clause exists to protect is held by the constant's FORM, not by the provenance of its digits.** Compliance is therefore **satisfied on the available evidence, and the evidence does not discriminate** — stated at exactly that strength, neither "verified" nor "unverified".

> **THE LESSON, AGAINST THIS TEAM: A CONSTRAINT THAT CANNOT BE CHECKED FROM THE ARTIFACT IS A CONSTRAINT ON REASONING, NOT ON RECORD.** It was still right to write — it prevents the error at the moment of repair — but it should have demanded a **discriminating** artifact: pin the source file's blob at read time, or record a second reading where the two sources are known to differ. **I will write the next such clause that way.** *A supervisor who only audits other people's unfalsifiable claims is running the same biased ledger this file exists to catch.*

### 21.3 THE `roache_triple.py` WHY-STRING — **RULED: A TRUE VERDICT CARRYING A FALSE REASON, AND TWO READERS OF ONE FACT THAT DISAGREE**

**Confirmed by me at source.** `monotone()` (`:376-382`) tests *both differences nonzero and of the same sign*. The why-string (`:621-633`) tests **`state == "DEGENERATE"` and nothing else**, and its `else` arm asserts *"the three values are not monotone"* for **five of the six** members of `NOT_A_RESULT_STATES`. On all three T23G rows — `STAGNANT`, `monotone = true`, values strictly decreasing with `e21` and `e32` both positive — **the record states a reason that is false.**

**And the file disagrees with itself:** the human-readable renderer at `:700-705` tests `if not row["monotone"]` — **the correct predicate** — so the printed report and the JSON `why` field can give different reasons for the same row.

> **RULED. The VERDICT is correct and stands: a `STAGNANT` triple bars a GCI under rule 5 independently of monotonicity, so nothing about `NOT A RESULT` moves.** **The REASON is wrong, and a wrong reason in a graded artifact is a wrong record** — *a disclosure that misstates a defect is still a wrong record, and the direction of the error does not excuse it.* `T23G_GRADED.json`'s `why` field is precisely what a downstream reader would quote.
>
> **The repair is LEGAL under `§2d.1` and falls in the SAME SAFEST CLASS as `§27.4`'s D5: it corrects a text field and provably cannot alter any verdict.** **I mandate no repair and I order no re-grade.** The correction belongs as a **dated addendum** beside the graded artifact, not as a silent re-issue — **the verdict was right, and bookkeeping never voids physics.**

### 21.4 `check_comparator_freeze.py` AND `§2d.1` — **THE REFERRAL'S PREMISE HAS EXPIRED, AND THE GENERAL ANSWER IS THE OPPOSITE OF WHAT WAS ASKED**

**The premise first, measured:** the checker now reports the T23G comparator as **`AMENDED_AFTER`, not `MODIFIED_AFTER_COMMIT`** — and **`AMENDED_AFTER` is not in `VIOLATING`** (`:139`). `MODIFIED_AFTER_COMMIT` was true of the **uncommitted** edit; committing it moved the row to the `:388` branch. **heat-transfer's disclosure was honest when written and is now stale in its own favour.** Lab-wide the run is 27 FROZEN / 131 NO-MARKERS / 10 UNFROZEN / 5 AMBIGUOUS-SCOPE / 3 AMENDED_AFTER, **and none of the 10 violating rows is T23G.**

**The general question is worth answering anyway, and the answer is no.**

> **RULED: `check_comparator_freeze.py` MUST NOT be taught to see or honour a `§2d.1` grant.** Three grounds. **(1)** `§2d.1` makes a change **LEGAL, not INVISIBLE** — and its own **condition (3) REQUIRES disclosure**, so a checker that suppressed the modification would defeat the condition the grant rests on. **(2)** A checker that can be **silenced by asserting a grant is a dead lever**: every unauthorised edit thereafter hides behind a claimed one. **(3)** Detection and disposition are different offices. **The flag is a DETECTION; the ruling beside it is the supervisor's** — the frozen instrument produces, the supervisor rules. **Confirmed structurally: the file has no waiver, disposition, grant or authorisation channel anywhere in 768 lines** `[MEASURED, full-file]`; its only `exempt` references are `§2d`'s W-4 boundary clause, which is a scope exclusion and not an authorisation.

**⚠ ONE THING NOBODY HAS SAID, AND IT UNDERCUTS THE ROW'S EVIDENTIAL VALUE IN BOTH DIRECTIONS.** The row is dated from an **mtime, not a `finished_utc`** — all three T23G markers contain the single word `done` — so it would read **`UNDATED-MARKER` under `--strict-markers`**. And its −617 s margin is **entirely an artefact of the accidental 06:01Z markers**: **without the incident in §21.5 the tree would have read `NO-MARKERS` and been out of evidence reach altogether.** **The freeze evidence for this comparator exists only because of an accident**, which is not a basis anyone should rely on.

### 21.5 ⚠⚠ THE FLAG FALLTHROUGH — **AN UNRECOGNISED ARGUMENT SILENTLY SELECTS THE MOST DESTRUCTIVE BRANCH, AND THIS IS THE SECOND MEASURED INSTANCE IN THIS LAB**

At **06:01:19Z** a lane ran `analyse_t23g.py --selftest`. **That script implements no `--selftest`.** `main()` (`:1065-1086`) tests only `--root`, `--json` and `--pre-solve`; **an unrecognised flag falls through the `if` chain untouched to `out, code = grade(root)`** — so a flag intended to *test* the instrument **ran a full grade against the live tree**, writing `DONE.T23G_C` and `DONE.T23G_M`.

**This is exactly the class this file exists for: not a guard that fails open, but NO GUARD WHERE EVERY CONVENTION IMPLIES ONE.** The default branch of an argument parser is the **most destructive** action the module offers.

**AND IT IS A PATTERN, NOT AN INCIDENT.** `T10aR2_RESULTS.md:18` records `mark_done_t10aR2.py --help` — **a flag that script also does not implement** — treated as "no case named", evaluating all three levels and writing three markers. **Different script, different flag, same defect class, two measured instances.** **This connects to my own V-49 finding that `analyse_t23g.py` has no `--selftest` at all**: the absence of the convention is *why* a lane reasonably typed it. **Routed to heat-transfer and to `scripts/`'s owner; I mandate no repair under the freeze.** The shape of the fix is not mine to choose, but the property is nameable: **an unrecognised argument must REFUSE, never fall through.**

**Damage, measured and bounded — and the honest reading is that the physics was untouched.** `T23G_F` case-root atime and mtime **unchanged**; `T23G_C` and `T23G_M` byte-identical to pre-incident copies; **no field read, no control run, no JSON, no verdict** — `grade()` refused at `require_done` because `T23G_F` had no STATUS at 06:01Z. **Zero core-minutes wasted.** The markers' **content is not false** — rule 4's six clauses genuinely held for both levels; they were **early, not wrong**, and they were correctly **not deleted**. **The real harm is the one in §21.4: they changed a checker's verdict.**

### 21.6 D3 — **CORROBORATED IN PART, AND I DECLINE THE WIDER READING OFFERED TO ME**

D3 was re-referred **with the fallthrough incident as its evidence**. **The incident passed NO `--root` at all**, so `root == HERE` and **D3's divergence condition was never exercised.**

> **RULED: the incident is CORROBORATING evidence for D3's consequence (1)** — that reaching `grade()` writes markers into the live tree with no way for a caller to redirect them, and that reaching it unintentionally is easy. **It is NOT probative of consequence (2)**, the two-tree staleness refusal, which no measurement here touches. **Offered as proof of D3 entire, it is one step further than the measurement carries** — and I adopt that distinction from the lane that drew it, because it was drawn against the interest of the referral it was gathering. **D3 has no `§2d.1` grant and remains unrepaired; nothing here grants one.**

### 21.7 THE STALE PRE-REGISTRATION BLOB — **THE STALE ROW IS NOT THE DEFECT; THE FALSIFIED SENTENCE IS**

`T23G_PREREGISTRATION.md` §A4 records the grading path's endpoints, naming `e02878a0…` as *"after A1 + A2"*. **That blob still resolves** and was the pre-image of `720eac16`; the current blob is **`9e4a5f2e…`**. **The artifact's own face (`T23G_GRADED.json/grading_path`) carries the correct sha, so the two records disagree and only the registration is wrong.**

**The row being stale is the smaller half.** A4's own sentence — *"this amendment moves it, **once**, before any compute"* — **is now falsified**: the path moved a **second** time, and **after** first compute, under my §27 grant. **An A5 dated addendum should record the new blob and strike that sentence's "once".** It **cannot alter a gate** and is a rule-6 append at the foot. **heat-transfer's document; I mandate nothing and I did not touch it.**

| field | value |
| --- | --- |
| grade audited | rung **`NOT A RESULT`**; triple **`STAGNANT` ×3**; **no GCI quoted, key absent**; 9/9 planted controls; 4/4 grading-path shas equal disk and HEAD |
| rule 5 | **applied in the only permitted direction** — `PASS` turned **into** `NOT A RESULT` |
| ⚠ my own §27 | **binding constraint is UNFALSIFIABLE here**; hazard structurally absent because the reference is a **frozen literal**, not a runtime read |
| rulings | why-string **false reason, verdict stands**; freeze checker **must NOT honour grants**; D3 **corroborated in part only**; A5 addendum **owed, not mandated** |
| verdicts issued | **0** · gates **0** · bands **0** · thresholds **0** · caps **0** · re-grades **0** · repairs mandated **0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## §22 — **cfd's FAIL-OPEN FINDING AGAINST MY OWN INSTRUMENT IS CONFIRMED IN CODE AND NARROWER IN FACT. AND FOUR SPECIMENS IN ONE NIGHT MAKE A CLASS: A DECISION WRITTEN WITH FEWER BRANCHES THAN ITS INPUT HAS STATES** (2026-09-01T19:14Z)

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** **Zero solver compute; 0 core-minutes; $0.00.** **No verdict, gate, threshold, band, cap or label created, moved or retired. No repair mandated. Nothing outside this team's own files touched.**

### 22.1 THE CLASS, NAMED BECAUSE FOUR SPECIMENS TURNED UP IN ONE NIGHT AND THREE ARE IN INSTRUMENTS THIS TEAM OWNS OR AUDITS

**A decision is written with fewer branches than its input has states, and the unhandled state silently takes a definite-sounding answer.**

| # | site | branches | states | the unhandled state becomes |
|---|---|---|---|---|
| 1 | `scripts/check_comparator_freeze.py:386` | 2 | **3** (`True`/`False`/**`None`**) | **`FROZEN`** — *mine* |
| 2 | `scripts/roache_triple.py:621-633` | 2 | **6** (`NOT_A_RESULT_STATES`) | *"not monotone"* — *mine*, ruled `§21.3` |
| 3 | `analyse_t23g.py:917` | 2 | 3 (`PASS`/`GATE FAIL`/**`NOT A RESULT`**) | `NOT A RESULT` **unreachable** |
| 4 | `analyse_t23g.py` `main()` | 3 tested | unbounded argv | **falls through to `grade()`** |

**In three of the four the unhandled state takes the REASSURING answer.** *A guard is not made by the branches you wrote; it is made by the states you did not.*

### 22.2 THE DEFECT IN MY INSTRUMENT — **CONFIRMED BY READING, EXACTLY AS cfd DESCRIBED IT**

`check_comparator_freeze.py:371` initialises `modified = None`. It is only assigned when **all three** of `rc2 == 0`, `disk_sha is not None` and `git cat-file blob` succeeding hold. Then `:386`:

```
row["commit_test"] = "MODIFIED_AFTER_COMMIT" if modified else "FROZEN"
```

**`None` is falsy in Python.** So a tree whose worktree-versus-blob comparison **could not be performed** is reported **`FROZEN`** — the compliant answer — and the row carries **no `worktree_differs_from_HEAD` key** to say the check never happened. **cfd's reading is correct and it is against an instrument this team owns.**

### 22.3 ⚠ BUT IT IS **LATENT, NOT LIVE** — DRIVEN BY ME, AND THE HEADLINE OVERSTATES IT

**I drove the real population rather than reasoning about it** `[MEASURED, read-only; every write in this module is inside `--selftest`, verified before running]`:

| | |
|---|---|
| rows walked | **182** |
| `FROZEN` | **27** |
| of those, blob check **actually performed** | **27** |
| of those, `modified` stayed `None` and fell to `FROZEN` | **0** |

> **RULED: the defect is REAL and it is LATENT. It is producing NO false `FROZEN` verdict today, and no record now standing is wrong because of it.** cfd's subject line states it as a live behaviour — *"turns 'I could not tell' into FROZEN"* — which is true **of the code** and describes **zero rows**. **A disclosure that overstates a defect is still a wrong record, and the direction does not excuse it.** **The finding stands to cfd's credit: they found it by READING, and the reading is exactly right. It is the PREVALENCE that needs the qualifier, not the mechanism.**
>
> **AND IT MUST STILL BE REPAIRED, FOR THE REASON THAT MAKES IT DANGEROUS RATHER THAN ACADEMIC: it fires only when the blob CANNOT BE FETCHED — which is precisely the anomalous case the instrument exists to catch.** A guard that is correct on every ordinary input and blind on the extraordinary one has its coverage exactly inverted. **Repair legal, no exception needed** — this instrument gates nothing that has been graded and the change is `None`-handling, not a threshold. **I mandate nothing under the freeze; the disposition is scheduling, not legality.**

### 22.4 THE COVERAGE HALF IS REAL AND LARGE — **AND HONESTLY REPORTED, WHICH IS THE OPPOSITE OF A FAIL-OPEN**

**137 of 182 rows are `NO-MARKERS`** — **the instrument declines to judge three quarters of its own population** `[MEASURED]`. That is a serious reach limitation and cfd is right to raise it.

**But `NO-MARKERS` sits in `UNJUDGED` (`:140`), NOT in `VIOLATING` and NOT in `FROZEN`.** The instrument **says it cannot tell, and is believed.** **A coverage gap that is DECLARED is a scope limitation; only an UNDECLARED one is a fail-open.** The two halves of cfd's subject line are therefore **different species**, and only `§22.2`'s is the fail-open. **I did not re-derive their 39-of-92 census and I assert nothing about it.**

### 22.5 MY OWN `§21.4` FIGURES — **CHECKED BECAUSE THEY WOULD HAVE BEEN THE CASUALTY, AND THEY HOLD**

`§21.4` published **27 FROZEN / 131 NO-MARKERS / 10 UNFROZEN / 5 AMBIGUOUS-SCOPE / 3 AMENDED_AFTER** and drew comfort from it. Today: **27 / 137 / 10 / 5 / 3** — **identical but for six more `NO-MARKERS` across twelve hours**, consistent with new pre-registrations landing. **No `FROZEN` row was contaminated then and none is now, so nothing I wrote on that count is withdrawn.** *Recorded because the honest thing was to check whether my own published number was the first casualty of a defect I was confirming, and to say so either way.*

### 22.6 ⚠ A FALSE ZERO — **THE FOURTH TONIGHT, AND IT LANDED ON A QUOTATION MY OWN `§28` RESTS ON**

A fact-gathering lane reported the `mark_done_t23.py` sha citation inside `T23G_RESULTS.md` as **`[NOT FOUND]`**, contradicting a passage I had read at source and quoted in `§28.3`. **Re-measured immediately, because a ruling of mine depended on it** `[MEASURED]`: `docs/campaigns/T-family/T23G_RESULTS.md` is a **single copy**, **byte-identical to HEAD** at blob `9f8032802994e313ecd5bb7794c1aad660ae1643`; `ecd457ac87dbdab83498c6a9c0334226c3e66863` occurs **once**; `mark_done_t23` occurs **once**. **`§28` stands on a verified quotation and nothing in it is withdrawn.**

**Credit exactly where it belongs, and it is the whole reason this was cheap:** the lane labelled it as **its own** `[NOT FOUND]`, listed it under *"what I could not verify"*, and did **not** assert the citation was absent. **Had it reported "the citation does not exist", I would have been retracting a true ruling within the hour.** *A zero is a claim about a reader, never about a file — and the fourth specimen tonight is the one that nearly reached a committed record.*

### 22.7 THE `roache_triple.py` REFERRAL AND THE RULING PASSED EACH OTHER — **ROUTED, NOT RE-RULED**

heat-transfer's `ddba373a` (16:17:48Z) refers the why-string defect and states *"no exception has been granted and none is requested here."* **One was granted, at `§21.3`, twelve hours earlier**: the repair is **legal under `§2d.1`**, in the **same safest class as `§27.4`'s D5** — a text field that provably cannot alter a verdict — with the **verdict standing** and the correction to land as a **dated addendum, never a silent re-issue**. **No new ruling is owed; the grant is theirs to use.** **Their diagnosis is independently correct and sharper than mine on one point** — that the false reason *"misdirects a reader toward oscillatory convergence when the signature is clean monotone convergence whose differences shrink too slowly."* **That is the harm, stated better than I stated it, and I adopt their wording.**

| field | value |
| --- | --- |
| cfd's fail-open finding | **CONFIRMED in code; LATENT in fact — 0 of 27 `FROZEN` rows contaminated** |
| coverage gap | **REAL, 137/182 unjudged — and DECLARED, therefore not a fail-open** |
| `§21.4` figures | **HOLD**; only `NO-MARKERS` drifted, 131 → 137 |
| `§28` | **STANDS** — the contested citation re-measured and present |
| new class named | **fewer branches than states**, 4 specimens, 3 in this team's instruments |
| verdicts issued | **0** · gates **0** · bands **0** · caps **0** · re-grades **0** · repairs mandated **0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

---

## §23 — **THE `--allocate-id` REFERRAL IS REFUTED ON ITS OWN TERMS: THE RECONCILERS DO SEE TOOL IDS, AND THE CITED LINE IS A MUTATION FIXTURE. BUT UNDERNEATH IT SITS A WORSE HAZARD NOBODY HAS NAMED — `CLAUDE.md` RULE 11's OWN COMMAND DOES NOT FAIL TO SEE A TOOL ID, IT SEES IT AND MISREADS IT** (2026-09-01T20:55Z)

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** **Zero solver compute; 0 core-minutes; $0.00.** **No verdict, gate, threshold, band, cap or label created, moved or retired. No repair mandated; no code changed by this section.**

### 23.1 THE CENTRAL CLAIM IS FALSE, AND THE CITATION IS A MUTATION-TEST FIXTURE READ AS PRODUCTION CODE

The referral states that a tool-allocated id is *"invisible to the record's own parser and both reconcilers"*, citing `check_record_reconciliation.py:725`. **Driven, not read** `[MEASURED, `__pycache__` cleared first]`:

| arm | result |
|---|---|
| legacy `parse_ids(line, RECORDS[p])` | **`[]`** — zero, **by design** |
| **combined `parse_record_ids(line, p)`** | **`['L-20260901T205031.933588Z-0d2008d8']`** — **SEES IT** |
| `is_tool_id()` | **`True`** |
| `check_record_reconciliation` imports `parse_record_ids` | **yes, `:136`** |
| its call sites **before** the `MUTANTS` list | **10** |
| **`MUTANTS` begins at line** | **722 — so `:725` is INSIDE the fixture** |

**`:725` is a mutation-test tuple**, one of a list whose own comment explains it mutates the pattern to prove it is load-bearing. **It is not a reader, and nothing parses records with it.** **The reconcilers use `parse_record_ids`, which sees both forms** — its docstring says so in terms, naming this team's own fail-open sections 13 and 14 as the reason it exists: *"A writer whose reader cannot see what it writes is a dead lever the day it ships."*

### 23.2 AND THE PROPERTY REPORTED AS THE DEFECT IS A **REQUIRED SAFETY PROPERTY**

The legacy pattern's failure to match a tool id is **deliberate and asserted by the module's own selftest**: *"tool-id/legacy separation proved on all 4 records: each legacy pattern parses ZERO ids from its own record's tool-id form, so no allocated id can enter a historical series' arithmetic."*

**If the legacy pattern DID match, `max_for_series` would compute a maximum over TIMESTAMPS.** **The referred "defect" is the guard working.** *Repairing it in the direction requested would have manufactured the very corruption the separation exists to prevent.*

### 23.3 ⚠⚠ BUT THERE IS A REAL HAZARD UNDERNEATH, IT IS WORSE, AND IT IS THE INVERSE OF WHAT WAS REFERRED

**`CLAUDE.md` rule 11 prescribes its own re-derivation command**, and rule 11 is the rule that assigns every lesson and docket number in this lab:

```
grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n | tail -1
```

**Driven against a file containing three legacy ids and ONE tool-allocated heading** `[MEASURED]`:

| file | rule 11 returns |
|---|---|
| legacy ids only (`L-431`, `L-432`, `L-433`) | **433** — correct |
| **the same file plus one tool-allocated heading** | **20260901** |

**`^## L-[0-9]+` matches the `L-20260901` PREFIX of the timestamp and truncates at the `T`.** The command then returns it as the maximum.

> **THIS IS NOT INVISIBILITY. IT IS THE OPPOSITE, AND IT IS STRICTLY MORE DANGEROUS: the tool id is VISIBLE TO RULE 11's READER AND MISREAD BY IT.** The next lesson would be minted **`L-20260902`**, and **because a maximum only ever rises, every future re-derivation is permanently poisoned** — the number can never come back down to 434. **It fails SILENTLY**: a plausible integer, correctly sorted, no error, no warning, and a `VERDICT: OK` upstream because the allocation itself succeeded.
>
> **AND IT IS UNCATCHABLE FROM INSIDE THE MODULE, WHICH IS WHY NO INSTRUMENT FOUND IT.** `append_record.py` correctly refuses to let tool ids into its own arithmetic; the hazard lives **entirely outside it**, in a command written in the constitution. **An instrument cannot audit the reader its callers are told by law to use.**

### 23.4 LATENT TODAY — **AND THE WORKAROUND IS WHAT KEPT IT THAT WAY**

`[MEASURED]` **Zero tool-allocated ids exist in `docs/LESSONS.md`** (`^## L-[0-9]{8}T[0-9]{6}` matches **0** lines), and rule 11's command on the real file returns **433**, which is correct. **No number in this lab is currently wrong.**

**heat-transfer's `--expect-first-id` workaround with same-invocation max-derivation — which minted `L-433` in LEGACY form — is precisely what has kept this latent.** **Their instinct was right and their diagnosis was aimed at the wrong mechanism, and the instinct is the part that mattered.** Said plainly because it is the second time today a team's caution protected a record while its stated reason did not survive checking, and **the caution deserves the credit regardless.**

### 23.5 RULING ON THE TWO OPTIONS PUT TO ME

**Option 1 — "the minted format matches the record's grammar per-record": REFUSED, and it is the dangerous option.** It would put timestamps into `max_for_series`'s arithmetic (`§23.2`) **and it would make the rule-11 hazard LIVE rather than latent**, because a conforming id is exactly one that rule 11's grep will swallow. **The request, granted, would have converted a latent poisoning into a certain one.**

**Option 2 — "`--allocate-id` refuses on records whose pattern it cannot satisfy": RIGHT IN SHAPE, and for a reason the referral did not give.** Not because the reconcilers are blind — **they are not** — but because **`CLAUDE.md` rule 11 prescribes an EXTERNAL reader that MISREADS the minted form.** The correct predicate is therefore **not** *"can the record's own pattern parse it"* but **"can every reader this record's callers are DIRECTED BY LAW to use survive it"**, which is a strictly wider test.

> **RULED: a refusal for `docs/LESSONS.md` is LEGAL and correct in shape, and I do not enact it tonight.** The demo-only freeze binds this team, this is not a demo-carrying instrument, **nothing is blocked** — the hazard is latent and the safe path is in use. **And the deeper question is ALREADY ON SANAA'S DESK**: whether the id should **carry** `(host, pid, sequence)` rather than hash them. **This measurement STRENGTHENS that item and changes its character: it is no longer an ergonomics preference, it is a correctness question about rule 11.** **Whoever picks the refusal up does not need a further ruling from me.**

**INTERIM CONTROL, costing nothing and already in force by practice:** **for `docs/LESSONS.md`, use `--expect-first-id` with same-invocation max-derivation and mint in the LEGACY form.** That is what landed `L-433`. **No tool-allocated id should land in `docs/LESSONS.md` until the desk item is ruled** — and the reason is now measurable rather than stylistic.

| field | value |
| --- | --- |
| referred claim | **REFUTED** — reconcilers see tool ids; `:725` is a `MUTANTS` fixture, list begins `:722` |
| reported "defect" | a **required safety property**, selftest-asserted |
| real hazard found | **rule 11's own command returns `20260901` instead of `433`** — visible and **misread**, silent, and **permanent once it lands** |
| live today | **NO** — 0 tool ids in `LESSONS.md`; rule 11 returns **433**, correct |
| option 1 | **REFUSED** — would make the hazard live |
| option 2 | **legal and correct in shape; not enacted under the freeze** |
| Sanaa's desk | the id-format item **strengthened** — now a correctness question, not ergonomics |
| verdicts issued | **0** · repairs mandated **0** · code changed **0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

## §24 — **THE F28 CHECK-1 RE-DRIVE I OWED PERSONALLY IS DISCHARGED AND THE INSTALLED DELTA IS SOUND. BUT THE GATE IT LANDED IN GRADES A SYMBOL A LATER ADDENDUM REDEFINED, AND THE TERM IT CANNOT SEE IS A REGISTERED FUNCTION OBJECT SITTING ON DISK.**

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** **Zero solver compute; 0 core-minutes; $0.00.** Rule 12's calibration duty does not attach — no pre-registration, no cap, no compute, and I do not invent a ratio where there is no estimate. **No verdict, gate, threshold, band, cap or label created, moved or retired by this section.** Read personally by the verification supervisor, as a diff, under `SUPERVISION_CHARTER.md` §3 check 1; **no part of it was delegated and no agent supplied a token on my behalf.**

### 24.1 THE PIN, AND WHY IT HAD TO FIRE

`FAIL_OPEN_GATE_AUDIT` §17.8 pinned my earlier check-1 read of the F28 comparator to a blob: check 1 transfers to `analyse_f28.py` **iff** its blob is exactly `1c6b9d53…`. **The pin fired.** `[MEASURED at HEAD `3e3da44f`]`

| object | blob | installed by |
|---|---|---|
| `analyse_f28.py` at HEAD **and on disk** | `5aff1614aff38ccdad0c33a0be9fb17b313fc167` | `eecb17e4`, 2026-08-31T22:40:00Z |
| prior comparator | `f496cc7e6c333d223b7970b896cf7e4c77d161af` | `5a851ca1`, 2026-08-31T16:19:13Z |
| the candidate my read covered | `1c6b9d53…` | **neither file carries it now** |

**`analyse_f28_candidate.py` at HEAD is ALSO `5aff1614`** — the candidate file was brought up to the installed bytes, so the blob my read covered is now reachable only as a loose object. **The transfer condition failed and the delta I owed is `1c6b9d53 → 5aff1614`: 490 insertions, 45 deletions on a grading instrument.** An instrument change without a supervisor's read is an uncalibrated instrument; **that read is now done, in full, and §17.8's pin is DISCHARGED.**

### 24.2 THE DELTA IS SOUND, AND IT IS BETTER THAN THIS LAB'S AVERAGE

The delta wires Addendum 3's floored thrust-stationarity criterion, `ptp <= max(0.001·|T_mean|, T_floor)` over the last 2000 iterations, and strikes the standing refusal that previously stood in `control_6_3`. **Four things carry weight and all four hold on my read:**

- **The floor is DERIVED, and the direction is right.** `assert_floor_derivation` runs at import (`FLOOR_DERIVATION = assert_floor_derivation()`), reproduces the chain from constants frozen above, and asserts the registration's printed figures against the derivation — **never the derivation against the literals**. Three targets from **three different sections** (`A_disk` §4, `42.7257 N` §6.2 control C3, `5.934119457e-04 N` Addendum 3 §4), so one transcription slip cannot satisfy all three. Tolerances are **half the last digit the registration prints** — a stricter test than Addendum 3's own "defensible to 4 s.f.", never a looser one. **A comparator whose floor does not reproduce the registered one is not importable.**
- **The frame is PROVED, not asserted.** `assert_stationarity_frame` requires `T_total == -(last windowed total_x) · WEDGE_SCALE` **bit-exactly**. The sector-versus-full-annulus slip is a factor of **72 in the PERMISSIVE direction** and would have rescued the zero-source arm (`0.020422 N < 0.042726 N`, Addendum 3 §5). The wrong-frame constant is defined **only so refusals can print it**; no criterion compares against it.
- **The reader carries its OWN plant (standing rule 3).** `plant_into_stationarity_window` plants into the **first row of the window** — the one row no other control addresses — with a displacement `(max − min) + PLANT_FO` **chosen to guarantee a new maximum**, so the control's visibility does not depend on the data. **Two arms, and the second is the one that matters:** `ptp` must move, **and `T_mean` must move by exactly `delta/window`** — an arithmetic identity a last-row-only or wrong-length reader cannot satisfy. A negative limb requires exact return after a byte-exact restore, the restore sits in a `finally`, and `verify_unchanged` closes it.
- **The approval's width is enforced IN the criterion.** `FLOORED_QUANTITIES = ("thrust",)` and `stationarity_criterion` **refuses** any other quantity, so the floor cannot reach the unfloored mass-flow row by a caller's copy-paste. **The leak has to defeat a guard, not merely go unnoticed** — `CLAUDE.md` rule 9 applied in the only form that counts.

**And the refusal/verdict boundary is drawn correctly:** an unstationary V(b) is `NOT A RESULT` **through the verdict field**, not through a refusal, because stationarity is a registered criterion with a threshold; the comparator still refuses (exit 2) for **instrument** failures only — blind plant, unprovable frame, floor that does not reproduce, short window. That is standing rule 5's direction constraint respected exactly.

### 24.3 THE LEGALITY CHAIN, VERIFIED AT SOURCE AND NOT ON RELAY

The delta rests on a **gate change on a frozen registration**, which is lawful only by Sanaa's personal approval. **I read her words, not the commit message that describes them** `[MEASURED]`:

| step | artifact | UTC |
|---|---|---|
| **Sanaa's own words** — `> About your questions : queue_runner : deploy it," "§2h.3": exact-PDE rule, "F28 floor": approved` | `etc/sessions/2026-08-31T2016Z_sanaa_three_rulings_runner_2h3_f28floor.md` (`5dd94f4f`) | **20:16:10Z** |
| Addendum 3 registers the floor | `0a62c5c6` | 20:34:29Z |
| Addendum 4 strikes a false **effect-statement**, altering no gate | preregistration §1825 | 2026-08-31 |
| comparator installed | `eecb17e4` | 22:40:00Z |

**The approval PRECEDES the addendum, and the addendum precedes the instrument. The order is correct.** Addendum 4 is lawful on its face and on my read: it declares *"This addendum alters NO gate, threshold, cap or label"*, byte-verifies the preceding blob (`cmp -n 104991`, rc 0), carries `Lines whose number changed above this section: 0`, and **strikes a false claim about the criterion's effect rather than the criterion** — disclosing that the floor is the **binding term on every arm on disk** and **relaxes** the criterion by **1.778×** on the loaded arm, which Addendum 3 had wrongly called inert. **That is a team correcting itself against its own interest, and it is recorded here as such.**

### 24.4 ⚠ THE DEFECT, AND IT IS NOT IN THE DELTA — IT IS IN WHAT THE DELTA LANDED INTO

**`control_6_3` grades §6.3's registered `T_total` as `T_duct` ALONE, and Addendum 7 ruled that `T_total = T_duct + T_hub + T_disk`.**

| fact | measurement |
|---|---|
| frozen §6.3 (`:533-543`) names **`T_total`** | **3 times**; names `forcesDuct` **0 times** |
| Addendum 7 (2026-09-01) rules the composition | *"`T_total` IS RULED TO BE `T_duct + T_hub + T_disk`"* — lawful precisely because it **defines a symbol the frozen text already grades** and moves no gate |
| `forcesHub` is a **registered function object** over patch `(hub)` | `case/system/controlDict.template:74,78` |
| the centrebody is in **every** arm | preregistration `:2232` — *"§7.1 keeps the centrebody in every arm"* |
| `analyse_f28.py`'s `FO_GRADED` (`:374-379`) | **NO `forcesHub` entry** — the term is not dropped, it is **unreadable by this comparator** |
| Addendum 7's **endorsed** implementation `analyse_f28g.py` | references `forcesHub` **4 times** and **REFUSES** on its absence |

**The comparator's own defence is an assertion where this same file's standard is a proof.** `total_thrust`'s docstring says *"on an empty duct with no source the duct force IS the total"* — **that is a claim about `T_hub`'s magnitude, and nobody measured it**, in a file that proves its stationarity frame **bit-exactly** rather than trusting a comment. §6.3 runs at `U_inf` with a solid centrebody in the flow; its x-force is not zero by construction, only by hope.

**Addendum 7 named this exact failure, in its own words, and its parent path is the specimen:** *"A missing `forcesHub` REFUSES — it does not fall back to `T_duct + T_disk` and it does not warn… a missing term is dropped silently only if a comparator lets it be."* **`analyse_f28.py` lets it be.**

**⚠ AGAINST MY OWN FINDING, AND I WILL NOT OVERSTATE IT.** I **cannot** say the verdict was flattered, and I do not. The two §6.3 gates move in **opposite** senses: adding the hub's drag pushes `T_total` **more negative**, making the **sign** gate (*"a positive `T_total` is thrust from nothing"*) **easier**, and the **magnitude** gate (`< 2 %` of the loaded reference) **harder**. **The direction is indeterminate until `T_hub` is measured — and that is precisely the finding.** A registered term of a graded quantity went **unevaluated**, which is the defect class the comparator's own struck refusal named in terms: *"a `GATE REACHED` issued while a REGISTERED channel goes unevaluated is a verdict on a criterion that was never applied."* **The struck refusal was right about the principle and the file then reproduced the principle's violation one symbol over.**

**⚠ AND THIS IS NOT BAD FAITH, WHICH MATTERS TO THE RECORD.** The blob was installed **2026-08-31T22:40Z**; **Addendum 7 landed 2026-09-01** and its §6 endorsed **only** `analyse_f28g.py`. cfd did not install a comparator in defiance of a ruling — **the ruling arrived afterwards and nobody propagated it to the parent path.** That is a **propagation failure**, and it is the same class my own board already carries against T20 (*"§2d.3 grant reached three T20 records but not the pre-registration"*). **A ruling that reaches one of two grading paths has not been applied; it has been half-applied, which reads identically from either path alone.**

### 24.5 THE VERDICT, AND WHAT IT DOES AND DOES NOT DECIDE

**`F28 §6.3 — NOT A RESULT`**, on the ground that a registered term of its graded quantity is unevaluated. **Standing rule 5's direction is respected: this turns a `GATE REACHED` INTO `NOT A RESULT` and could not have turned anything the other way.**

**Two repairs are available and the choice is cfd's, not mine:**

1. **Wire `forcesHub` into `analyse_f28.py`, with a refusal on absence, matching `analyse_f28g.py`.** The stronger path. **It requires re-proving the frame:** `assert_stationarity_frame`'s bit-exact identity binds `T_total` to `forcesDuct`'s column alone, so a composed `T_total` breaks that identity and the stationarity proof must be re-anchored on the duct term explicitly rather than on a symbol whose meaning has moved. **That coupling is the real cost and it is why this is not a one-line fix.**
2. **A dated addendum scoping Addendum 7's composition away from §6.3.** Legal in shape — but it would have to explain **why one symbol means two things inside one registration**, and I record that as the **weaker** path without forbidding it.

**What this section does NOT do.** It does not amend the registration (not mine), does not touch `analyse_f28.py` (**worktree modified: 0 files**; the blob on disk is byte-identical to HEAD, verified after), does not re-grade any F28 arm, and does not disturb Stage 0 or the F28G child. **It does not disturb the delta of §24.2, which stands as sound** — the defect predates it, was neither introduced nor closed by it, and the two questions are separate.

| item | outcome |
|---|---|
| §17.8's blob pin | **FIRED, then DISCHARGED** — check 1 **TRANSFERS** to `5aff1614` on my personal read |
| Addendum 3/4 legality | **LAWFUL**, verified at Sanaa's own words, not on relay |
| F28 §6.3 | **`NOT A RESULT`** — a registered term unevaluated |
| direction of the error | **INDETERMINATE, stated as such** — the two gates move opposite ways |
| repairs mandated | **0** — referred to cfd with both paths named and their costs |
| code changed | **0 files** · verdicts on other teams' rungs re-graded: **0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

## §25 — **I WAS ASKED FOR A STANDING AUDIT AND THE MEASUREMENT SAYS THE HAZARD I WAS ASKED TO GUARD IS ALREADY CLOSED. I AM NOT FILING IT. THE ARROW THAT IS LIVE POINTS THE OTHER WAY AND HAS ONE REAL SPECIMEN.**

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** **Zero solver compute; 0 core-minutes; $0.00.** **No verdict, gate, threshold, band, cap or label created, moved or retired.** **No file created; no standing audit opened.**

### 25.1 THE REQUEST, AND WHY THE ANSWER IS NO

The item routed to me was: the demo acts' screen-set-versus-measured-record split deserves a standing audit shape, *"so screen edits can never silently reach records."* **The deciding measurement refutes the premise, and I report that rather than filing a document to look responsive.**

**ZERO of five demo acts write anything toward a record** `[MEASURED, exhaustive over `sdk/workflows/*_act.py`]`. Every write in all five modules is either a `tempfile` copy used for a standing-rule-3 plant (`dmr_act.py:692`, `motor_thermal_act.py:597`, `battery_module_act.py:288`) or a `shutil.copy2` of a PNG or sidecar into the act's **own** output directory (`jet_flap_act.py:1512`, `adjoint_act.py:1706`). **No act opens any path under `verification/` or `cases/` for writing.** The hazard *"a screen edit reaches a grading record, ledger row, certificate or charter"* is **architecturally closed, not merely unobserved** — and a standing audit on it would book nothing, forever, while reading as coverage. **An audit that cannot find anything is worse than no audit: it is a green light nobody earned.**

For the record, the inventory is clean too: **eight per-act split notes, eight TRACKED, zero untracked.**

### 25.2 ⚠ THE ARROW THAT IS LIVE, AND IT HAS A SPECIMEN I VERIFIED MYSELF

The dependence inverts between the two screen surfaces, and counting acts alone hides it:

| surface | reads the record live | holds its own copy | writes toward the record |
|---|---|---|---|
| **the wire** (5 live acts) | **5 / 5** for every physics number | 2 / 5, both **disclosed divergences** in tracked notes | **0 / 5** |
| **the cut-in sheets** (8 `.tex`) | 2 generated + 1 record-guarded | **5 hand-transcribed, no generator** | n/a |

**THE SPECIMEN — Act D's baseline drag coefficient is printed in two places as two different numbers, against an explicit owner ruling that it be one.** Driven by me personally, not taken on relay `[MEASURED]`:

| side | artifact | value | at `.6f` |
|---|---|---|---|
| **record / wire** | `cases/dafoam/ladder-a/A2_optimization_history.json` → `baseline.CD`, read at every call by `canonical_baseline_cd()` (`sdk/workflows/adjoint_optimization.py:736`) | `0.029619634` | **`0.029620`** |
| **record / sheet** | `cases/dafoam/ladder-a/A2_drag_decomposition.json` → `rows.A0_baseline.CD` | `0.02962051221` | **`0.029621`** |
| **printed on the filmed sheet** | `docs/dafoam/demo/ACT_D_reference_wing_sheet.tex:240` (results table, `Baseline` row) and **again at `:261`** | **`$0.02962051$`** | — |

**Sanaa's 0540Z ruling, quoted inside the wire's own docstring:** *"baseline Cd printed identically everywhere (0.029621 or 0.029620, one choice)."* **The sheet matches NEITHER literal** — it prints eight significant figures where the ruling names two six-decimal candidates, and the value it carries is the one the wire deliberately did **not** pick. `canonical_baseline_cd()` exists precisely to enforce that ruling, and **the sheet is not wired through it.**

**⚠ THE DEFECT I BOOK IS NOT THE NUMBER. Both values are honestly sourced** — they are two real re-solves `4.9e-7` apart, and the wire's docstring says so and says which it picks and why. **The defect is a TRACKED NOTE CARRYING A FALSE COMPLETENESS CLAIM:** `docs/dafoam/demo/ACTD_DEMO_COMPUTE_NOTE.md` §4 item 5 asserts that *"every baseline-C_d cell renders through it."* **That is true of the wire and false of the sheet**, and the note is the artifact a later reader would trust instead of checking. **This is the same species as §24.4 one document over — an assertion standing where the file's own standard is a proof — and the same species as Addendum 4's struck sentence, which that team found in itself and struck.**

**⚠ AGAINST MY OWN FINDING, STATED BEFORE ANYONE ASKS.** **The demos are SHOT.** Nothing here changes what was filmed, and I am not dressing a bookkeeping defect as a camera failure. The sheet's number is not wrong, no verdict moves, and **no grading record, ledger row or certificate is touched by it.** What is live is that the sheet is a **tracked artifact that outlives the shoot** and will be cited as a result sheet, and the note that vouches for it overstates its own coverage.

### 25.3 WHAT ALREADY CHECKS THIS, MEASURED RATHER THAN ASSUMED

- `scripts/check_demo_acts.py` — **1,898 lines, 11 limbs, and it reads ZERO grading records.** Its only record access is a selftest on `figure_provenance.json`.
- `docs/dafoam/demo/check_sheet_wire_parity.py` — the nearest instrument and **deliberately not this one**: its own docstring declares it a *presence check, not a diff*, over four claim classes, **none numeric**, reading zero record files.
- `docs/campaigns/T-family/demo/actC_graded_admission.py` — **the one real limb of this kind that exists**, and the right pattern: a screen numeric token is admissible only if a **committed** graded artifact carries it at the token's own printed precision, with the allowlist read **out of git, not off disk**, and **empty (maximally strict) when the run has not graded**. **Scope: one act, one quantity class.**
- the four `check_actD_*_sheet_face.py` — **zero record reads across all four.**

**One act and one quantity class are covered. Five sheets and every quantity are not.**

### 25.4 THE RULING, AND ITS FALSIFIER

**NO STANDING AUDIT IS OPENED, and no file is created.** The framed hazard is closed; the live one has **exactly one specimen**, and **one specimen is a finding, not a standing audit.** I book the specimen here and refer it. If a **second independent specimen** appears in the five uncovered sheets, that is a class and I will open the file then — **and I record that trigger now, before I know the answer, so opening it later cannot be a decision fitted to a result.**

**THE FALSIFIER, which belongs to §25.2 and not to a future file:** mutate one record value and rebuild every surface printing that quantity. **If every surface moves with it, this entry is booking a duplicate-with-a-generator rather than a detached value, and it is wrong.** That is why the DMR and Act A sheets are excluded here **by measurement** — both are regenerated from their records — **and not by assumption.** A second falsifier: a divergent screen literal that is **fully disclosed, number beside record, in a tracked note** is not a defect at all — which is why the jet-flap and motor literals are **excluded and named as excluded** rather than counted.

**REFERRED TO dafoam, NOT REPAIRED BY ME.** `docs/dafoam/demo/` and `sdk/workflows/` are that team's territory; I measured, I did not touch. **The cheap repair is to render the sheet's two cells through `canonical_baseline_cd()`** — or, if the sheet is meant to carry the decomposition value deliberately, **to correct the compute note's completeness claim**, which is the half that is actually false. **I do not choose between them.**

| item | outcome |
|---|---|
| standing audit as framed | **DECLINED** — screen→record writes **0 of 5**, hazard architecturally closed |
| files created | **0** |
| specimen found and verified personally | **1** — Act D baseline `C_d`, `0.029620` wire vs `0.02962051` sheet |
| the defect booked | a **tracked note's false completeness claim**, not the number |
| coverage measured | **1 act / 1 quantity class** covered; **5 sheets / all quantities** uncovered |
| trigger for opening the file, registered in advance | **a second independent specimen** |
| repairs mandated | **0** — referred to dafoam, both paths named, neither chosen |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

## §26 — **THE BRITTLENESS REFERRAL IS CONFIRMED AS A COUPLING AND REFUTED AS A FAIL-OPEN — A PARAPHRASE DRIVES IT THE SAFE WAY. UNDERNEATH IT THE LIMB NEVER READS THE TABLE IT GRADES, AND THE REPAIR I WAS ASKED FOR WOULD NOT HAVE TOUCHED THAT.**

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** **Zero solver compute; 0 core-minutes; $0.00.** **No verdict, gate, threshold, band, cap or label created, moved or retired.** **`scripts/check_demo_acts.py` NOT modified** — blob `dc4524fb…`, byte-identical to HEAD, verified after every drive. Every mutation ran on in-memory copies of act streams; `__pycache__` cleared before each run.

### 26.1 THE REFERRAL, DRIVEN — AND IT FAILS IN THE SAFE DIRECTION

The referral: the request-vs-lab split limb couples to the literal `"this lab supplies"`, and is therefore brittle. **Both halves are answered, and they answer differently.**

**The coupling is real and total.** Occurrence census over the whole rendered stream, all five acts: **lab side — `this lab supplies` ×1 and every other alternative ×0.** The entire lab side of the gate rests on **one phrase in one rendered string**, in each of adjoint-wing, battery-module, jet-flap, motor-thermal and shock-reflection.

**And of the three occurrences of the phrase in the file, ONE is production** (`:811`); `:796` is a comment and `:1502` is the planted control. **Two-thirds of the citation is not production code** — the same pattern as §23, where a referral cited a mutation fixture. **I record that the pattern recurred and that this time the surviving third was load-bearing.**

**But the failure a paraphrase produces is a REFUSAL, not a pass** `[MEASURED, one verb changed, one rendered string affected, all five acts]`:

| paraphrase | rc | red limbs |
|---|---|---|
| `This lab supplies` → `This lab provides` | **1** | `['discussion']` |
| → `Supplied by this lab is` | **1** | `['discussion']` |
| → `The lab supplies` | **1** | `['discussion']` |

**Baseline is `rc 0`, 793 events, no red limbs**, so these are clean single-cause reds. **VERDICT: the referral is CONFIRMED as a coupling and REFUTED as a fail-open.** A false refusal of a valid act is noise; it costs a re-take, not a wrong verdict. **The file already reasoned this out for the sibling limb at `:1223-1225` — *"could read as absent; that direction is the safe one."*** The referral rediscovered a hazard the author had already priced and accepted.

### 26.2 ⚠⚠ THE REAL DEFECT, AND I ESTABLISHED IT BY READING THE CODE, NOT ONLY BY DRIVING IT

The limb's production logic is nine lines, and they entail the failures rather than merely exhibiting them:

```
user_side = lab_side = False
for event in events:
    for _key, text, _zone in LP._rendered_strings(event):
        if _re.search(r"what the request|...", text, re.I):  user_side = True
        if _re.search(r"this lab supplies|...", text, re.I):  lab_side = True
if not (user_side and lab_side):  problems.append(...)
```

**It sweeps every rendered string of every event, and it sets two booleans. It never reads the assumptions table at all.** Three fail-opens follow **necessarily** from that shape, and all three were also driven `[MEASURED]`:

| # | drive | result |
|---|---|---|
| 1 | **scope** — from the file's own plant (split genuinely blanked), green restored by a figure caption `"Lab-defined colour limits."` and a table cell `"user-defined axis range"` — **two statements about plot formatting** | **rc 0, no red** |
| 2 | **blank attribution** — the `Set by` column blanked on **all 26 rows** of `actd_assumptions`, so the table attributes no quantity to anybody | **rc 0, no red** |
| 3 | **false attribution** — all 26 rows rewritten to `the request`, so the table claims the customer set the free stream, the reference area **and the lift target** | **rc 0, no red** |

**Drive 3 is the one that matters: it is precisely the misattribution the limb exists to prevent, and the limb is green on it.** The two sides need not be on the assumptions screen, in the same event, or on the same screen — one instance of each phrase anywhere on the wire satisfies a boolean.

**A fourth, same class, in the convergence limb (`:1078`):** *"The grid convergence study showed a 2% change in your lift."* — names the study, promises nothing, report bands blanked — passes **`rc 0`** through the `\bin your\b` alternative. **Negative control fires:** the identical sentence with `in your` → `in the` gives **`rc 1`, red `['convergence']`** with the full three-branch refusal, so the green is attributable to that one alternation and nothing else.

**Rule 3 is satisfied — these greens are not vacuous.** The file's own plant `_plant_no_user_lab_split` gives **`rc 1`, red `['discussion']`**. The limb catches; it catches the wrong thing.

### 26.3 ⚠ THE GATE CITES THE AUTHORITY IT UNDER-ENFORCES

**Sanaa's stage 4, read at source and not on relay** (`etc/sessions/2026-09-01T2030Z_sanaa_demo_shooting_protocol.md`, `cfcf766f`), verbatim:

> - Assumptions table: USER-DEFINED (from the prompt) vs LAB-DEFINED (defaults, representative properties), **every quantity** with a value and unit.

**The written property is per-quantity and located IN THE TABLE. The limb requires one instance of each side ANYWHERE ON THE WIRE.** That is strictly weaker on both axes, **and all three measured fail-opens live in exactly that gap.** The limb's own refusal text says *"her stage 4 asks for both"* — **so it names the authority in the same sentence in which it enforces less than that authority says.**

**THAT IS THE THIRD SPECIMEN OF ONE SPECIES IN THIS SESSION, AND THREE MAKE A CLASS.** §24.4: a docstring asserting a composition where the file's own standard is a bit-exact proof. §25.2: a tracked note claiming *"every baseline-C_d cell renders through it"* when one surface does not. §26.3: a gate citing stage 4 while enforcing a weaker reading of it. **In every case the CODE IS HONEST AND THE PROSE ABOUT THE CODE IS WIDER THAN THE CODE.** The prose is what a later reader trusts instead of checking, and it is written by the same author in the same commit, which is why nobody catches it. **I name the class here: A CLAIM WIDER THAN ITS INSTRUMENT. It is not lying and it is not sloppiness — it is the sentence you write about your own work while the reasons are still in your head.**

### 26.4 THE REPAIR I WAS ASKED FOR IS THE WRONG ONE, AND I REFUSE IT WITH A MEASUREMENT

I was asked for **a wording-class pattern** — a wider alternation in place of the brittle literal. **Measured against the three fail-opens, it touches none of them.** They are **scope and semantics** defects: no vocabulary change alters `for event in events`, and no vocabulary change turns a boolean into a per-row check. **A wider alternation makes the limb greener without making it truer**, and it would suppress the one signal the limb currently emits honestly — the safe-direction refusal of §26.1.

**The structural check is the right shape, and the structure already exists at zero cost to the acts** `[MEASURED]`: all five publish a `transcript.table` matching `assum` with headers `['Quantity','Value','Unit','Set by']` and per-row attribution `the request` / `the lab` — **26, 9, 8, 8 and 8 rows.** A predicate that locates the attribution column by header and refuses a missing column, any blank cell, or a single-sided column was prototyped and driven **both ways**: **green on all five acts as published** (no false alarm today), **red** on the blanked column (*"26 row(s) attributed to nobody"*), **red** on the all-`the request` column, and **green** under the §26.1 paraphrases — the fail-closed noise disappears.

**⚠ AND ITS COST IS A CONTROL THAT WOULD SILENTLY STOP FIRING, WHICH IS THE PART I WILL NOT LET PASS QUIETLY.** The structural predicate **returns green on the file's own plant** `_plant_no_user_lab_split`, because that plant rewrites prose and leaves the table intact `[MEASURED]`. **So adopting the structural check REQUIRES extending the plant to blank the attribution column in the same act** — otherwise a planted control stops testing anything and the suite still reports green. **That is standing rule 3 applied to a proposed repair rather than to a result**, and it is the reason the two checks are **complementary and must not be OR-ed**: an OR reopens every false-pass path in §26.2.

**False-positive risk, named rather than waved at.** A value vocabulary is still a vocabulary — the honest claim is only that it is **much smaller and more stable**: two values in a schema field authored once per act, not prose reworked between takes. Headers like `Origin`/`Owner` or values like `Uploaded`/`As given` would be wrongly refused; the spec's own worked example (`ACT_A_GUI_CONTENT_SPEC.md:1049-1057`) uses `Source` with `USER-DEFINED`/`LAB-DEFINED` and **is** covered. **And a legitimately one-sided table** — a request pinning every quantity — **is indistinguishable from fail-open #3 on the wire.** I would keep the both-sides requirement and register the exception in a pre-registration if such an act is ever registered, **rather than weaken the predicate pre-emptively against an act that does not exist.**

### 26.5 REFERRED, NOT REPAIRED — AND WHY THAT IS NOT TIMIDITY

**`scripts/check_demo_acts.py` is a CROSS-TEAM INSTRUMENT under `scripts/`, outside this team's folder scope.** Widening or repairing it is not mine to do alone (rule 9; `ESCALATION`), and this team has taken that position before against its own convenience. **Referred to the chief**, with the prototype's behaviour measured in both directions and the plant-extension stated as a **precondition, not a nice-to-have**.

**The demos are SHOT, so nothing here is urgent — and nothing here is moot either.** This script is the lab's demo gate for any future shoot, and **the three fail-opens would have passed an act that misattributed every assumption to the customer.** That the shoot happened to be honest is not the gate's doing.

| item | outcome |
|---|---|
| the referral, as filed | **CONFIRMED as a coupling · REFUTED as a fail-open** — paraphrase drives it `rc 1`, the safe direction |
| citation quality | **1 of 3 occurrences is production**; the recurrence of §23's pattern is recorded |
| fail-opens found underneath it | **4** — scope, blank attribution, false attribution, and the convergence limb |
| the sharpest | **all 26 rows attributed to `the request` → `rc 0`, no red** |
| written property vs enforced property | **strictly weaker on both axes**; the limb cites stage 4 in the sentence where it under-enforces it |
| the repair requested | **REFUSED with a measurement** — a wider alternation touches none of the four |
| the repair proposed | **structural**, driven green-and-red, **conditional on extending the plant** |
| repairs mandated / code changed | **0 / 0 files** — referred, outside folder scope |
| solver compute | **0 core-min, $0.00** · the audit's own cost **NOT MEASURED** (four single-core driver runs, no budget registered; I do not present a wall-clock impression as a measurement) |
| **lines whose number changed above this section** | **0** |

## §27 — **⚠⚠ AGAINST MYSELF, AND IT IS A DEFECT IN `CLAUDE.md` RULE 10's OWN ASSERTION, NOT ONLY IN MY USE OF IT: THE PRIVATE-INDEX PROTOCOL'S "ONLY YOUR PATHS" CHECK PASSES ON FOREIGN CONTENT INSIDE YOUR OWN PATH. I CAUGHT IT BY NOTICING A NUMBER LOOKED WRONG, WHICH IS NOT AN INSTRUMENT.**

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** **Zero solver compute; 0 core-minutes; $0.00.**

### 27.1 WHAT I DID, STATED PLAINLY BEFORE ANY MITIGATION

**My `§26` commit `54c2a878` carried the heat-transfer team's uncommitted `docs/LAB_STATE.md` board block into my commit, under my commit message, without disclosing it.** `[MEASURED]` Three peer commits (`aa98c56f`, `cfbfa79b`, `0593e91e`) landed between my `§25` and `§26` commits; heat-transfer had written its section **to disk and not to git**; my `update-index --add -- docs/LAB_STATE.md` took **the whole disk copy**, which contained their work as well as mine.

**The damage assessment, and I ran it before writing anything else:** additions **175** lines, deletions **2**, and **the only deleted line is heat-transfer's own superseded stamp line, replaced by their own new one.** **Nothing was lost, nothing was reverted, and their block is byte-intact at HEAD** `[MEASURED, `git diff HEAD~1 HEAD -- docs/LAB_STATE.md`]`. **The effect was benign — arguably helpful, since their work was uncommitted and is now safe.**

**The record is wrong anyway, and that is the part that matters.** `git log` attributes 175 lines of another team's reasoning to a commit whose message describes an audit of a demo checker. **A reader reconstructing who found what would misattribute it**, and my message does not say a word about it. Rule 10's *"say in the message if you left foreign rows uncommitted so somebody can be dispatched to land them"* exists for exactly this species; **the converse duty — say if you LANDED them — is the same principle and I did not discharge it.**

### 27.2 ⚠ THE PROTOCOL'S ASSERTION DOES NOT CATCH THIS, AND THAT IS GENERAL

Rule 10's protocol carries one assertion at commit time:

```
T=$(git write-tree); git diff-tree --stat $H $T   # ASSERT: only your paths
```

**`--stat` reports PATHS. It says `docs/LAB_STATE.md | 175 ++++`, and that path IS mine to write.** The assertion **passes**, correctly and uselessly. **The protocol's per-path targeting defends against foreign FILES; it has no defence against foreign CONTENT inside a shared file** — and `docs/LAB_STATE.md` is **the most-shared file in this lab**, written by six supervisors, mandated by the FIRST-ACTION rule and by every supervisor's board duty, and **never** exclusively anyone's.

**The post-commit verify has the same blind spot for the same reason** — it too reports paths.

**I caught it because 175 insertions for four bullets did not look right.** That is attention, not an instrument, and **attention is exactly what this lab has repeatedly measured itself unable to rely on.** Had my four bullets themselves been long — which on this board they routinely are — the line count would have looked unremarkable and I would have reported a clean commit in good faith.

**Direction of the hazard: PERMISSIVE, and both ways.** A supervisor can silently **land** a peer's half-finished board text under their own name, and — the worse direction — **a supervisor whose disk copy is STALE for a shared file will silently REVERT a peer's committed work while the "only your paths" assertion passes.** That is `c46309f5` and L-223's nine lost files, except that L-223's lesson closed the *stale-parent* case with the CAS and the *foreign-file* case with per-path staging, **and left the stale-content-in-a-shared-file case open.** My commit is the benign half of that hazard. The malign half is the same mechanism.

### 27.3 WHAT WOULD ACTUALLY CLOSE IT

**Referred, not taken:** `CLAUDE.md` rule 10 is the lab constitution and `ESCALATION_CHARTER.md` §9.6 is not this team's to amend. I state the shape and leave the ruling.

The assertion that would have fired costs one command: **diff the committed blob of a shared file against the parent's blob and require every changed hunk to fall inside the committing agent's own section.** For `LAB_STATE.md` the sections are literally delimited (`## verification`, `## heat-transfer`, …), so the check is mechanical and cheap. Failing that, the weaker but still useful form: **assert that the hunks you are committing are the hunks you wrote**, by diffing your pre-edit snapshot against your post-edit disk copy and requiring the committed diff to equal it.

**What I will NOT propose:** that agents stop writing `LAB_STATE.md` directly, or that it be split per team. It is the only handoff channel between sessions (L-186) and its being shared is the point.

### 27.4 THE DISCLOSURE, AND THE FOURTH SPECIMEN OF TODAY'S CLASS

**heat-transfer: your T23G2 board block is at HEAD, byte-intact, inside `54c2a878`, which is my commit and does not mention it.** Nothing of yours was lost. **You do not need to re-land it, and you should not — a second landing would duplicate it.**

**And this is the fourth specimen today of the class I named in §26.3 — A CLAIM WIDER THAN ITS INSTRUMENT — except it is the inverse and therefore the sharper case: §24.4, §25.2 and §26.3 are records claiming MORE than their instrument does; §27 is a record claiming LESS than its artifact contains.** Both are the same failure: **the record and the artifact disagree, and the record is the thing people trust.** I booked three of those against other teams today and produced the fourth myself within the hour, **in the commit that named the class.**

| item | outcome |
|---|---|
| foreign content landed under my message | **175 lines, heat-transfer's board block** — disclosed here |
| content lost or reverted | **0** `[MEASURED]` — the sole deletion is their own superseded stamp |
| rule 10's `only your paths` assertion | **PASSED, correctly and uselessly** — it reports paths, not authorship |
| how it was caught | **a line count that looked wrong.** Not an instrument |
| the general hazard | a **stale** disk copy of a shared file **reverts** a peer's committed work with the assertion still passing |
| referred | rule 10 / `ESCALATION` §9.6 — **not this team's to amend** |
| repairs mandated / code changed | **0 / 0** |
| solver compute | **0 core-min, $0.00** |
| **lines whose number changed above this section** | **0** |

### 27.5 ⚠⚠ IT REPRODUCED INSIDE THE COMMIT THAT DISCLOSED IT, AND THAT PROMOTES §27 FROM A LAPSE TO A STRUCTURAL DEFECT

**The `§27` commit `2a786496` — the one whose entire subject is this hazard — carried `cfd-supervisor`'s uncommitted board block, 88 lines.** `[MEASURED]` **Deletions of real content: 0.** Nothing lost, again; foreign content landed, again.

**I had run the content check. It passed.** In the invocation before the commit I snapshotted `LAB_STATE.md`, proved my own diff was exactly **5 added / 0 removed**, and proved the snapshot **byte-equal to HEAD**. **Every one of those statements was true when I made it, and all three were stale by the time `update-index` ran** — cfd wrote to disk in the gap between two of my tool calls.

**THIS IS L-223's LESSON ONE LEVEL DEEPER, AND THE FIX IS THE ONE ALREADY IN RULE 10.** Rule 10 requires capturing HEAD *"**all in one shell invocation** — a lane can move HEAD between two bash calls (L-223)."* **The same sentence is true of the CONTENT check and rule 10 does not say so.** A check performed in a prior invocation is not a check; it is a memory of one. **The snapshot, the diff assertion and the commit must be a single invocation, or a peer writes into the gap** — which is exactly what happened, twice, in forty minutes.

**Why this matters more than my two benign commits:** I ran the strongest available check, in good faith, with the hazard at the front of my mind, **and it still did not fire** — because it was in the wrong place, not because it was the wrong check. **An agent who had merely read §27 and resolved to be careful would have done precisely what I did.** Care is not the countermeasure; **invocation boundaries are.**

**REVISED REFERRAL to the chief — one clause, not a new instrument:** rule 10's *"all in one shell invocation"* requirement should extend from the HEAD capture to **the shared-file content assertion**, and the assertion should be **hunk-scoped to the committing agent's own `## <team>` section**. **This entry's own commit is the worked demonstration:** snapshot, edit, assert and commit in one invocation, with the assertion printed below.

| item | outcome |
|---|---|
| occurrences in one session | **2** — `54c2a878` (heat-transfer, 175 lines), `2a786496` (cfd, 88 lines) |
| real content lost across both | **0** `[MEASURED]` |
| the check I ran before the second | **ran, passed, and was STALE** — a prior-invocation check is a memory of a check |
| the fix | **not a new instrument** — rule 10's existing *"one shell invocation"* clause extended to the content assertion |
| **lines whose number changed above this section** | **0** |

### 27.6 ⚠⚠⚠ THE THIRD OCCURRENCE, AND IT IS THE WORST BECAUSE MY OWN ASSERT FIRED AND I COMMITTED ANYWAY. I BUILT THE CHECK, IT WORKED, AND I PRINTED IT INSTEAD OF GATING ON IT.

**Commit `5777c759` carried heat-transfer's uncommitted board block a second time, 253 lines.** `[MEASURED]` **Real content lost: 0** — the single deletion is their own superseded stamp line, replaced by their own new one.

**And the check I wrote in `§27.5` DID ITS JOB.** It printed, in the same invocation, immediately before the commit ran:

```
board +2 (foreign:PRESENT)
```

**`foreign:PRESENT`. It detected the exact condition it was built to detect, announced it, and the commit proceeded — because I wrote `echo "$F1"` and never wrote `[ "$F1" = none ] || exit 1`.** The assert was **a report, not a gate.**

**THIS IS THE FAIL-OPEN CLASS OF THIS ENTIRE AUDIT FILE, COMMITTED BY ITS AUTHOR, IN THE INSTRUMENT BUILT TO PREVENT IT.** It is `§26.2`'s finding turned on me exactly — *a limb that catches; it catches and does nothing.* It is the lab's own recorded lesson **"evidence annotated as non-binding"**: *a printed discrepancy is worse than one never computed*, because the printed one buys the feeling of having checked. **I had the feeling. I did not have the gate.**

**§27.5 said the fix was invocation boundaries and that care is not the countermeasure. That was right and INSUFFICIENT.** Same-invocation placement is necessary; **a check must also REFUSE.** Both times I named the requirement and both times I stopped one step short of enforcing it — **which is the third consecutive instance of a claim wider than its instrument, and the instrument was mine each time.**

**⚠ AND REFUSING IS NOT ENOUGH EITHER, WHICH IS WHY THE PREVIOUS TWO ENTRIES WERE INCOMPLETE.** A gate that only refuses would block every commit to `LAB_STATE.md` forever — it is written by six supervisors continuously, so foreign content on disk is the NORMAL STATE, not an exception. **A refusal with no recovery would be retired within a day, and correctly.** The recovery is what makes the gate survivable, and rule 10 already implies it:

> **BUILD THE BLOB, DO NOT STAGE THE DISK COPY.** Take the file **as it is at HEAD**, apply **only your own hunk** to that, and commit **that** object. The peers' uncommitted work stays uncommitted **on disk, untouched, exactly as you found it** — which is the status quo ante and theirs to land — and rule 10's existing duty then applies unchanged: **say in the message that you left foreign rows uncommitted.**

**This entry's own commit is built that way**, and its assert **exits non-zero** rather than printing.

| item | outcome |
|---|---|
| occurrences | **3** — `54c2a878` (175 lines), `2a786496` (88), `5777c759` (253) |
| real content lost, all three | **0** `[MEASURED]` |
| what failed this time | **not the check — the check FIRED.** I printed its result instead of gating on it |
| the corrected rule | same invocation **AND** non-zero exit **AND** a recovery path, or the gate gets retired as unusable |
| the recovery | **build the blob from HEAD + your own hunk**; never stage the shared disk copy |
| **lines whose number changed above this section** | **0** |

## §28 — **THE TAXONOMY IS COMPLETE AT FOUR FACES AND THEY SHARE ONE TELL: THE ABSENCE OF AN ERROR WAS READ AS THE PRESENCE OF A CHECK. THIS IS `§2p`'s CALLER-SIDE TWIN, AND A LAB THAT FIXES ONLY ONE HALF IS STILL EXPOSED** (2026-09-03T18:5xZ)

**Filed on cfd's request, broadcast to every supervisor via the chief. NO CLAUSE IS OWED
AND NONE IS WRITTEN** — nothing is blocked, so under Sanaa's ~20:00Z bar the disposition is a
**lesson**, and **heat-transfer and cfd land it**. **What is filed here is the TAXONOMY**,
because this audit is where the family lives. **Zero compute; 0 core-min; $0.00. No gate,
threshold, band, cap or label created, moved or retired; nothing re-graded.**

### §28.1 AN ATTRIBUTION CORRECTION, BECAUSE I HAVE MADE SIX OF THESE TODAY AND WILL NOT SKIP ONE THAT FLATTERS ME

**The broadcast reached me as *"the fourth face of YOUR `L-466` family."* `L-466` IS NOT MINE.**
`[VERIFIED]` this team landed **`L-464` and no other lesson this session**; `L-465` and `L-466`
are other teams'. **Independence is not verifiable from git — every commit on this box carries
one Ubuntu identity — so I state what IS verifiable: what I landed.**

**What IS mine is the FAMILY, and only by lineage:** this is **`§2p`'s twin**, and `§2p` is this
team's. *An attribution offered generously is still an attribution, and taking it would have
cost nothing and been false.*

### §28.2 THE FOUR FACES, AND THE TELL THAT MAKES THEM ONE THING

| # | face | the mechanism |
|---|---|---|
| 1 | **swallowed refusal** | `L-466` — a `2>/dev/null` turns an instrument's **refusal** into a clean-looking zero |
| 2 | **passing-on-skips** | a suite reports green over cases it never executed |
| 3 | **claim-from-completion** | the process **finished**, therefore the thing was **done** |
| 4 | **dropped-blocked-read** | cfd's new one — a **classifier-blocked** queue read is dropped; **forty minutes blind to idle territory** |

> **THE TELL, AND `L-466` STATES IT BETTER THAN I WOULD HAVE: *"THE READING WAS NOT WRONG. THE
> READER NEVER RAN."* — because *"a swallowed refusal and a genuine zero are the same empty
> string."* In every one of the four, THE ABSENCE OF AN ERROR WAS READ AS THE PRESENCE OF A
> CHECK.**

### §28.3 ⚠ WHY THIS BELONGS IN THIS AUDIT AND NOT BESIDE `§2p`: THEY ARE THE TWO HALVES AND ONLY ONE HAS BEEN WORKED

- **`§2p` IS THE INSTRUMENT-SIDE DEFECT: a check that CANNOT EMIT FAILURE.** VR3's absent
  `GATE FAIL` branch; `G-RLX-0` never implemented; a zero-denominator returning ∞.
- **THIS FAMILY IS THE CALLER-SIDE DEFECT: a CALLER that reads NO-ERROR as PASS**, over an
  instrument that may be perfectly capable of failing — **and never ran.**

> **A LAB THAT REPAIRS ONLY THE INSTRUMENT SIDE IS STILL FULLY EXPOSED.** Every `§2p` control
> this team has ordered — planted inputs, empty-input arms, production-path mutation — proves
> the **instrument** can fail. **NOT ONE of them proves the CALLER ever invoked it.** *The
> planted-zero control asks "can this reader see a non-zero"; this family asks the prior
> question, "did this reader run at all", and I have been ordering the second question's
> answer while assuming the first.*

### §28.4 THE ONE THING THAT IS THIS TEAM'S TO ADD — THE MAPPING INTO THE VERDICT VOCABULARY

The broadcast's rule is *"a classifier-blocked measurement is an UNMEASURED QUANTITY, not a
CLOSED QUESTION."* **That is `CLAUDE.md` rule 1's vocabulary arriving from the caller's side,
and stating it in the lab's own words is this team's job:**

> **A BLOCKED, REFUSED, SKIPPED OR UNRUN MEASUREMENT IS `NOT A RESULT`. It is never
> absence-of-failure, never a silent `PASS`, and never a closed question.** Rule 5's one
> permitted direction already carries this for graded rows; **the four faces are what it looks
> like when the same event happens BELOW the grader, where no verdict vocabulary was ever
> applied to it.**

**AND THE OPERATIONAL TEST, which costs nothing and is the reason this is filed rather than
merely noted:**

> **CAN THIS CODE PATH DISTINGUISH "THE CHECK RAN AND FOUND NOTHING" FROM "THE CHECK DID NOT
> RUN"? If it cannot, its zero is UNINTERPRETABLE and must refuse.** That is rule 3's planted
> control asked one step earlier — **plant the RUN, not only the VALUE.**

### §28.5 SCOPE, HONESTLY

**No sweep is ordered and no class is declared beyond this taxonomy.** Four faces measured in
one day is a strong signal, **but three of the four are other teams' measurements relayed to
me, and I have re-derived none of them at source** — `L-466` I read at source; faces 2, 3 and 4
I have **not**. **They are recorded as REPORTED, and this audit's own frames rule (its header)
requires me to say so rather than let four relayed items read as four measurements of mine.**
*If a fifth face lands, the first thing owed is a re-derivation of the four, not a fifth entry.*


## §28.6 — **THE DEBT IS PAID FIRST: 3 OF 3 RELAYED FACES RE-DERIVED AT SOURCE, AND THE RE-DERIVATION FOUND A DEFECT IN §28's OWN FILING. THEN FOUR NEW MECHANISMS — OF WHICH ONLY TWO ARE FACES, ONE IS NOT THIS TAXONOMY'S AT ALL, AND ONE IS NOT A FACE BUT A MAP OF WHERE THE NEXT ONE WILL BE FOUND** (2026-09-03T21:1xZ)

**Zero compute; 0 core-min; $0.00. No gate, threshold, band, cap or label created, moved
or retired; nothing re-graded. DISPOSITION: REPORTED, NOT GATED. No instrument is
proposed and none is written** — Sanaa's 2026-09-03 `2000Z` ruling makes *reported, not
gated* the default, and §28's own filing note already declines to order a sweep.

---

### §28.6.0 THE DEBT — §28.5 SAYS THE FIRST THING OWED IS A RE-DERIVATION OF THE FOUR, NOT A FIFTH ENTRY. HERE IT IS, AND THE SCORE IS **3 OF 3**

§28.5 records face 1 (`L-466`) as read at source by this team and faces **2, 3 and 4** as
**REPORTED**. Face 1 is therefore not re-owed. The three that were:

| face | re-derived? | specimen I read at source | what I actually verified |
|---|---|---|---|
| **2 — passing-on-skips** | **YES, as a class, on a live specimen** | `scripts/test_auto_stop_liveness.py:428-450` | The file's own docstring records the defect verbatim: *"controls: 12 passed, 0 failed, 12 skipped … every one of the TEN flip pairs printed `[SKIP]`, Z1 included"*, while the suite still printed *"every evaluated pair flipped. The reader was shown able to see both a non-zero and a zero."* Repair present in the same file: **`:449-450`** — skips get their own column and never fold into either other, and a pair with an unwitnessed half **REFUSES, rc 3 `NOT WITNESSED`**. Landed at `6f4fd88a`. |
| **3 — claim-from-completion** | **YES, as a class, on a live specimen** | `docs/campaigns/T-family/T5_RESULTS.md:3` + `verification/runs/T-family/T5_runs/` | `T5_RESULTS.md:3` reads **`Rung verdict: PENDING`** and the comparator's own quoted output says *"No case has run: no rows are graded and no verdict is written."* I counted the completion markers in `T5_runs/` myself: **6 `DONE.*` files, 0 graded rows.** Six completions and no answer, in one directory — *the process finished, therefore the thing was done* is false here by measurement. |
| **4 — dropped-blocked-read** | **YES, on THIS TEAM's OWN second specimen; NOT on cfd's original** | commit **`ef33434c`** | `git show --stat ef33434c` returns **a subject line and no diffstat** — I ran it; the commit is **empty**, and its message asserts content the commit does not contain. This team booked it at `docs/LAB_STATE.md:27478` as *"the FOURTH FACE, dropped-blocked-read, in my own shell"*, struck by disclosure at `b086eaf6`. **cfd's original specimen — "a classifier-blocked queue read dropped, forty minutes blind to idle territory" (`docs/LAB_STATE.md:23048`) — I did NOT re-derive: no artifact path is given for it anywhere, so there is nothing to open.** |

> ⚠ **AND THE RE-DERIVATION FOUND A DEFECT IN §28 ITSELF, WHICH IS WORTH MORE THAN THE
> SCORE.** **Rows 2 and 3 of §28.2's table carry NO artifact path — not a file, not a
> commit, not a line.** Row 4 names a team and a duration and no artifact. I could
> re-derive the *mechanisms* because live specimens exist on this box, but **I cannot
> prove any of them is the specimen §28's author meant**, and neither can anyone else.
> **A taxonomy row without an artifact path is unfalsifiable by construction** — which is
> this audit's own frames rule turned on the audit. **The cheapest repair, and it costs
> nothing: every row of §28.2 carries a path or a sha.** *Reported. Not ordered — the
> section is verification's own and the fix is its author's to make.*

**SCORE: 3 of 3 mechanisms re-derived at a cited artifact. 0 of 3 proven identical to
§28's original specimens, because §28 names none.**

---

### §28.6.1 THE FOUR NEW MECHANISMS, AND THE CLASSIFICATION MATTERS MORE THAN THE COUNT

**Provenance, stated before any of it is read:** items (A)1–3 are **cfd's**, item (B) is
**heat-transfer's**. Everything below is marked **`[RE-DERIVED]`** where I opened the
artifact myself and **`[REPORTED — <team>]`** where I did not. §28.5's discipline: a
relayed measurement is recorded as REPORTED, and I do not launder one into mine.

**Resisting inflation, said up front: of the four, ONE is a new face, TWO are variants of
existing faces, and ONE is not a member of this taxonomy at all.** A variant is more
useful than a fifth entry; a misfiled item is worse than an absent one.

---

#### **M1 — PREMATURE READ OF A LIVE ARTIFACT.** **VARIANT of face 3 (claim-from-completion)**, at the *artifact* level rather than the *process* level

**What it is.** A reader consumes an artifact **while its writer is still writing**. The
partial read is structurally indistinguishable from a complete one: the file parses, the
reader exits 0, and the rows it did not see are indistinguishable from rows that do not
exist. Face 3 says *the process finished, therefore the thing was done*; M1 says **the
file opened, therefore the file is complete** — the same inference, one level down.

**Instances.**
- **Instance 1 `[REPORTED — cfd]`,** `docs/LAB_STATE.md:23045`: *"a background grep read
  while still writing; exit 0, 30 lines, header-only read taken for a completed zero."*
  **No artifact path is given and I could not open it.**
- **Instance 2: my brief names two instances. I searched and could not locate a second,
  and I will not manufacture one.** `[NOT LOCATED]` The nearest independent artifact on
  this box is the **same mechanism handled correctly**, not a second failure: the fd-255
  launcher capture at **`10eb76f4`**, which reads `/proc/<pid>/fd/255` from four live
  solvers, **requires all four copies byte-identical and requires the result to parse
  under `bash -n` "so a partial read is not filed as a script"** `[RE-DERIVED — commit
  message read at source]`. **That is the cure, and it was written before the taxonomy
  asked for one.**

> **DISCRIMINATING TEST — TRUNCATE THE FIXTURE AND SEE WHETHER ANYTHING CHANGES.**
> *Does this reader establish that the writer TERMINATED, by evidence independent of the
> artifact's content — a producer-side rc captured inside the writer, an end-of-stream
> sentinel, a declared byte count, or a whole-file parse that a truncation breaks?*
> **The operational form:** take the reader's own fixture, cut it at a record boundary,
> and run the reader on both. **If the two runs differ only in row count and in no
> explicit field, the mechanism is present.** A sound reader either refuses or flips a
> named field. `bash -n` at `10eb76f4` is the model in its cheapest form: a truncated
> script does not parse, so a partial capture cannot be filed.

**DID IT CHANGE A LANDED VERDICT? NO** — and on instance 1 I cannot say what it touched,
because no artifact is named. **WOULD IT HAVE?** On the fd-255 case, a partial capture
filed as the code of record would have made the **launcher of record for four live runs,
three of them the graded pass, unverifiable against any blob** — a rule-2 provenance
failure, **not a change to any graded number**. Stated as provenance, not as a verdict.

---

#### **M2a — THE READER ANSWERED A DIFFERENT QUESTION (`git diff` vs the poisoned index).** ⚠ **NOT A FACE OF THIS TAXONOMY. I recommend it be recorded as an ADJACENT CLASS with a pointer, and NOT added to §28.2**

**What it is `[RE-DERIVED at the corroborating artifacts; the originating instance is
REPORTED — cfd]`.** `git diff` compares the worktree to the **INDEX**. With this box's
shared index poisoned, it reported **zero changed lines for a file just edited**, and the
assertion built on it printed *"NONE, no changed line touches a gate"* — cfd's own words
at `docs/LAB_STATE.md:23046`: **"A well-formed, completely false proof of exactly what I
wanted proved."**

**Why I am refusing it a face, and this is the substantive call in this draft.** §28's
tell is *"the absence of an error was read as the presence of a check"*, and its
operational test is *"can this code path distinguish 'the check ran and found nothing'
from 'the check did not run'?"* **Here the check RAN. It touched a real object and
returned a true answer — about the wrong proposition.** §28's test comes back **clean**
on this path and the path is still wrong, so **admitting M2a as a fifth face would put
into the taxonomy a specimen the taxonomy's own test cannot detect**, and would quietly
make that test look weaker than it is. **The lab already has the right home for it:**
*an instrument that answers a different question than the one asked, whose WRONG answer
is the well-formed one* — **ruled one class** at `docs/LAB_STATE.md:28544`, hosted by
`L-394`/`L-395`/`L-401`/`L-402` and `§2j`. **File it there; cross-reference it from §28;
do not count it as a face.**

> **DISCRIMINATING TEST — NAME THE REFERENCE, THEN MAKE THE PROOF PRINT WHAT IT *CAN* SEE.**
> *(1) Write down, in words, the proposition this instrument actually evaluates —
> for a diff: **against what?** the INDEX, `HEAD`, or the worktree — and compare it word
> by word with the proposition you meant.* **(2) The runnable half: require the proof to
> print a change it is KNOWN to be able to see.** A diff that reports **zero** changed
> lines for a file you edited thirty seconds ago must **refuse**, not report clean.
> **This is rule 3 pointed at a git reader.** Remedy of record, cfd's own:
> `docs/LAB_STATE.md:23046` — bypass the index and diff against `git show HEAD:<path>`.

**DID IT CHANGE A LANDED VERDICT? NO — CAUGHT.** **AND IT IS THE ONE THAT WOULD HAVE
REACHED FURTHEST.** Two measured corroborations, both re-derived by me at their board
lines:
- `docs/LAB_STATE.md:9382` — *"Nothing relaxed: 110 insertions, 0 deletions, proved
  against the **HEAD blob** rather than `git diff`, which reported **231/0** from the
  poisoned shared index and **would have been the wrong number**."*
- `docs/LAB_STATE.md:31677` (ansys territory, independent) — `git diff HEAD` reported
  *"27 files, 3217 deletions"* on files that **per-path hashing showed all 27 identical**,
  so **Sanaa's own "a pure-deletion diff vs HEAD is the reversion signature" guard FIRES
  FALSELY** on this box. **The only valid discriminator named there: `git hash-object`
  against `git rev-parse HEAD:<path>`.**

⚠ **WHY THIS ONE IS THE DANGEROUS ONE EVEN THOUGH IT CHANGED NOTHING:** the false proof
it produces is *"no changed line touches a gate"* — **the exact assertion rule 2's freeze
discipline rests on.** A reader that cannot see a change **cannot see a gate being
widened**, and rule 2's entire evidentiary content is that the gate could not have been
fitted to the answer. **This mechanism attacks the check that protects every other
check.** It was caught by re-deriving against the HEAD blob, **not by any control.**

---

#### **M2b — `checkMesh`'s ABSENT-LINE VARIANTS, AND THE WITNESS-FIELD DISCRIMINATOR.** **VARIANT of face 2 (passing-on-skips)**, at the *line* level: an absent line is a check that never ran, and it reads as a check that ran clean

**What it is `[RE-DERIVED — I read the reader and its control at source]`.** `checkMesh`
does not print a fixed set of lines. Whether a given quantity appears at all depends on
which branch the tool took. **So a reader keyed to a line's ABSENCE conflates two states
that are not the same: "the condition is absent" and "the check never printed."** The
neighbouring defect is already `L-459` (`docs/LESSONS.md:22040-22064`): `checkMesh` prints
**`Non-orthogonality check OK.`** at **89.7134 / 89.9441 / 89.9985 / 89.983501 degrees**
against a 70-degree gate, with **1,810,108** severely non-orthogonal faces on the same
screen — *the warning and the verdict are two different tests, printed adjacently, and
the verdict is the looser of the two.*

**THE CURE IS THE MODEL FOR THIS WHOLE EXTENSION, AND IT IS ALREADY BUILT AND RUNNING.**
`cases/committee-grids/read_ugrid_identity.py:391-439`:
- **`state`** — set to `"ABSENT"` at **`:398`** when the log is not a file, and to
  `"READ"` at **`:401`** when it is. **The field is present in BOTH cases and its value
  differs.** That is the whole trick.
- **`aspect_ratio_label_form`** — `"="` (**`:418`**, value printed, unflagged), `":"`
  (**`:422`**, `***High aspect ratio` branch taken), `None` (**`:426`**, no aspect-ratio
  line at all). **Three states, so "no high-AR warning" and "no AR line" are
  distinguishable**, which two states could never be.
- The tool's verdict strings are captured into
  `verdict_line_IGNORED_NEVER_A_GATE` (**`:434`**) **solely to show they were discarded**.
- **The control that proves it:** `cases/committee-grids/grade_rung0b.py:282-287`, control
  **B7** — drive the reader on a log that does not exist and require
  `state == "ABSENT"` **and** the number `None`: *"an ABSENT `checkMesh` log reads
  `ABSENT`. IT NEVER READS CLEAN"* (`:65`).

> **DISCRIMINATING TEST — THE WITNESS FIELD. THIS IS THE SHAPE EVERY OTHER TEST IN THIS
> SECTION IS BUILT TO IMITATE.**
> *Is there a field in this reader's OUTPUT that is present in **both** the found and the
> not-found case, and takes **different values** in the two?*
> **If the only difference between "the line was there and clean" and "the line was never
> printed" is an absent key or a `None`, the mechanism is present** — because every
> downstream consumer that tests truthiness collapses the two. **The runnable form:** run
> the reader twice, once on a real artifact and once on a path that does not exist, and
> **diff the two output dicts.** A sound reader differs in a named, non-null field. An
> exposed reader differs only in what is missing.

**DID IT CHANGE A LANDED VERDICT? NO, AND IT WAS EXPLICITLY PREVENTED FROM DOING SO.**
RUNG 0b (`33b77af5`) records, in its own commit message: *"QUALITY REPORTED, NOT GATED,
and no verdict line was read anywhere (L-459) … every value PARSED off its named maximum
while `checkMesh` printed `Non-orthogonality check OK.` beside all four"*
`[RE-DERIVED — commit message read at source]`.

⚠ **BUT THE SAME READER DEFECT DID MOVE A REGISTERED GATE — IN THE OPPOSITE, SAFE
DIRECTION, AND IT IS ON THE RECORD.** `docs/LESSONS.md:19901-19919`: a registration gated
its meshes on `checkMesh` printing **`Mesh OK`**; the finest level instead printed
`***High aspect ratio … Max aspect ratio: 1012.242839, number of cells 2` and
`Failed 1 mesh checks.` — **two cells in 202,180 failed the study**, on a quantity
`docs/standards/MESH_STANDARD.md` §3.3 calls *"advisory at 1000, never a lone rejection"*.
**A false REJECTION, not a false pass.** Worth saying plainly: **the same "read the tool's
verdict line" defect cuts both ways, and the fail-open direction — `OK` at 89.9985° — is
the one nothing catches.**

---

#### **M3 — THE COMMIT-MESSAGE PAIR: "a commit message is a pointer, never a payload."** **VARIANT of face 3 (claim-from-completion)** — *the work was done and the commit landed, therefore the measurement is filed*

**What it is `[RE-DERIVED — both commits opened at source]`.** Two halves of one
mechanism, one per direction:
- **The writing half.** `10ba2567` — I ran `git show --stat`: **exactly one file,
  `CONVERTER_CALLER_SCAN_certonomous_runs.json`, 31 insertions.** The five-copy converter
  manifest and the 13-header byte-budget audit existed **only in that commit's message**.
- **The reading half.** A measurement was later read *out of* a commit message and treated
  as filed.

**The consequence is landed and documented, and it is not hypothetical.** `b78e8858`'s own
message: *"The Rung 0 lane searched the tree for them, could not find them, and had to
mark its RUNG0b amendment's citation **RELAYED NOT VERIFIED**."* The repair landed the
same day — `b78e8858`, **3 files, 637 insertions**, both artifacts **re-measured from
disk** by `verification/runs/RUNG1_M6_runs/M1_ugrid_reimport/audit_converter_and_ugrid_headers.py`
rather than transcribed from the message, **each carrying its own refusal control** (the
manifest refuses unless it finds the known-defective copy and reports it defective; the
header audit refuses unless it observes **both** agreement and disagreement).

> **DISCRIMINATING TEST — RESOLVE THE CITATION, DO NOT READ IT.**
> *For every measurement a record relies on: can a script open it **by path**? Run
> `git rev-parse <commit>:<path>` on the citation and `git diff-tree --stat <commit>` on
> the commit that allegedly filed it.* **If the commit's diffstat does not list a file
> containing the number, the number is not filed — whatever its message says.**
> The asymmetry is exact and cheap: `10ba2567` → **1 file, 31 insertions**, number absent.
> `b78e8858` → **3 files, 637 insertions**, number present and hashable.
> **A measurement that lives only in a commit message cannot be read by a script, cannot
> be hashed as an input, and cannot be cited by path from a frozen `FROZEN PATHS` table.**

**DID IT CHANGE A LANDED VERDICT? NO.** RUNG 0b's `PASS` (`33b77af5`) was graded after
both artifacts were real. **WHAT IT DID DO, AND IT IS NOT NOTHING:** it forced a **frozen
registration's amendment to carry a citation marked `RELAYED NOT VERIFIED`** — the
downgrade stands on the record at `75ad7ef9`. **A citation degraded is not a verdict
changed, and I will not inflate it into one.**

---

#### **M4 — heat-transfer's DOMAIN GAP.** ⚠ **NOT A FACE. It is a map of where the next face will be found, and it is the sharpest item in this set**

**FIRST, A CORRECTION TO MY OWN BRIEF, BECAUSE IT WAS HANDED TO ME AS A VERBATIM QUOTE AND
IT IS NOT ONE.** I was given, as verbatim: *"we plant rigorously into comparators reading
solver logs, and into nothing else."* **That sentence is not on disk in that wording.**  **[⚠ STRUCK IN PLACE 2026-09-03, §28.7.1 — WRONG. The wording IS on disk, TWICE: `T25R6cR2_2D1_RECORD_EMISSION_PETITION.md:293-297`, a REFERRAL TO THIS TEAM, and quoted verbatim in `VERIFICATION_CHARTER.md §2aj`. What I handed down was a PARAPHRASE of a real sentence labelled verbatim — not an invention.]**
The on-disk sentence is `docs/LESSONS.md:22890-22895` (**`L-470`**, heat-transfer's):

> *"This is rule 3 — the planted-zero control — outside the domain the lab planted it in.
> … the lab enforces it rigorously on **comparators reading solver logs**. Nobody plants
> into a git assertion, a shell glob, or a selftest's own coverage. **All three of these
> are exactly the reader rule 3 forbids, in places the rule was never pointed at.**"*

**The paraphrase is faithful in substance and sharper than the original. It is still a
paraphrase, and the landed text must quote the file, not the relay.**

**The census, stated at the number the artifact carries.** `L-470` files **three** guards
measured on the T25R6c-R2 rung and says the same shape was docketed the same day as
**D588** from two other graders — **"which makes five instances in one session across two
teams"** (`docs/LESSONS.md:22843-22844`) `[RE-DERIVED — read at source]`. **My brief says
six. I could not find a sixth and I am not going to round up to it** `[REPORTED —
heat-transfer; the sixth is NOT LOCATED by me]`. The three at source:
1. **A `git` assertion satisfied by the empty set** — the rule-10 protocol's
   *"only my paths"* assertion, with an empty tree. **`diff-tree` printed nothing; nothing
   is a subset of my paths; the guard passed.** Commit **`6d3b6c2d`** is empty and carries
   a message describing a file it does not contain.
2. **A reader whose addressing scheme could not name the object** — a monitor globbed
   `processor0/111.8`; OpenFOAM writes the accumulated float **`111.799999999998`**, so
   **no literal match could ever succeed.**
3. **A selftest that passed 39 checks on a comparator that cannot write its own verdict** —
   `grade_t25R6cR2.py --selftest` reports `PASS (0 failed)` over 39 checks and **never
   calls `finish()`**; the real run then raised `TypeError` at the record-writing step and
   **`T25R6cR2_VERDICT.json` was never written.**

> **DISCRIMINATING TEST — NAME THE OBJECT, THEN LOOK FOR ITS PLANT.**
> *What kind of object does this reader actually consume — a solver log, a directory
> listing, a git tree, a queue entry, a JSON record, its own coverage? Now: does any
> control in this repository **mutate an object of THAT KIND** and require this reader's
> output to change?*
> **If the file's only plant targets a solver log while its load-bearing read is a
> `diff-tree`, a glob, or a queue directory, the reader is UNPLANTED IN ITS OWN DOMAIN** —
> and its zero is exactly the zero rule 3 forbids, in a place rule 3 was never pointed at.
> **The operational form is one line: `grep` the file for its plant, then ask what the
> plant is planted INTO.** A plant in the wrong domain is decoration.

🔴 **DID ANY INSTANCE CHANGE A LANDED VERDICT? NO. DID ONE *WOULD-HAVE*? YES — AND THIS IS
THE SINGLE MOST IMPORTANT SENTENCE IN THIS DRAFT.**

> **`L-470` INSTANCE (2) WOULD HAVE CHANGED A LANDED VERDICT.** The monitor reported
> **`FIELD DIRS at 111.8: 0` on a run that had written that directory**. Under
> `CLAUDE.md` rule 4 — *last time == `endTime`*, fields present, age guard — **a run that
> wrote no field directory at its `endTime` is not complete, and its rows grade
> `NOT A RESULT`.** A false zero there converts a completed, gradeable run into an
> incomplete one. **And `L-470` says the trap was fully baited:** *"The zero was false and
> it looked exactly like the failure the predecessor rung had actually suffered"* —
> T25R6c really did write no directory at its endTime (`docs/LESSONS.md:22861-22863`).
> **It was caught ONLY because a second, independent reading existed** — the frozen
> grader's `abs(float(d) - ENDTIME_B) <= 1e-6` and the `DONE` marker it gates. **It was
> not caught by a control, because in that domain there was no control.**

**I state the governance consequence and do not act on it.** The bar handed to me is
explicit: *nothing here becomes a gate until one would have changed a verdict.* **On my
reading that precondition is now MET, by exactly one instance, and it is heat-transfer's,
not this team's.** **I propose no instrument, write no clause, and change no disposition —
this stays REPORTED, NOT GATED.** Whether a met precondition is acted on is the
supervisor's call and, above that, Sanaa's; **it is not a lane's, and a lane noticing that
a bar is met is not the same as the bar being lifted.**

---

### §28.6.2 THE DOMAIN-GAP COUNT — PART MEASURED, PART EXPLICITLY UNMEASURED, AND I SAY WHICH IS WHICH

The question M4 poses is quantitative: **into how many non-log-reading comparator classes
does this lab actually plant?** I measured what is cheap and refuse to guess the rest.

**MEASURED — the population that plants at all.** Files under `verification/`, `cases/`
and `scripts/` matching `*.py` that define a plant constant (a top-level identifier
containing `PLANT` on the left of an `=`): **261 files.** Method stated so it can be
re-run and disputed; it is a **syntactic census of planters, not of plant targets.**

**MEASURED, AND DECISIVE FOR ONE CLASS — the queue readers.** Applying a proximity test —
a `PLANT` token within 25 source lines of a queue-shaped read (`verification/queue`,
`queue_runner`, `LAUNCH_LOG`) — returns **exactly 1 file of the 261**, and it is
`scripts/test_auto_stop_liveness.py`, **which is not a graded comparator.**
🔴 **THE QUEUE-READING CLASS HAS ESSENTIALLY NO PLANTED CONTROL, AND IT IS THE CLASS FACE
4 WAS FOUND IN.** That is the one number in this section I will defend.

**MEASURED — one genuine non-log planter exists, so the "nothing else" is not literally
true, and the correction sharpens the finding rather than blunting it.**
`scripts/referent_population_screen.py:264-293` **plants into a git-OBJECT reader**: it
writes a loose blob with `git hash-object -w` (`:271`), reads it back through the
production `read_blobs` path, and **refuses (`REFUSED:`, exit 2) if the plant does not
come back** (`:277`, `:289`). **I opened it and read it** `[RE-DERIVED]`.
**So the gap is not "git" as a domain — it is the git INDEX/STATUS domain** (`L-470`
instance 1's `diff-tree` assertion, and M2a's `git diff`), **and the queue domain.**
Naming the gap correctly is what makes it fixable.

**UNMEASURED, AND I WILL NOT GUESS IT.** The counts for the mesh-reading, field-reading
and index-reading classes are **NOT measured by anything I ran.** The proximity test
returns **66** files for mesh-shaped reads and **10** for git/index-shaped reads, but
**proximity is co-occurrence, not targeting**: a comparator may plant faithfully into a
solver log while merely *mentioning* `polyMesh` twenty lines away, and it would score as a
mesh-domain planter. **Those two numbers are proxies and must not be quoted as counts of
planted classes.** The measurement that would settle it is per-file and cannot be
automated honestly: **for each of the 261, read what the plant is written into and what
the load-bearing read consumes, and record the pair.** At a few minutes a file that is
tens of hours of reading. **It is unmeasured. It is not "small" and it is not "probably
fine" — it is unmeasured**, and §28.4's own rule applies to it: *a blocked, refused,
skipped or unrun measurement is `NOT A RESULT`, never absence-of-failure.*

---

### §28.6.3 THE SUMMARY THE NEXT READER ACTUALLY NEEDS

| # | mechanism | classification | discriminating test, in one line | changed a landed verdict? |
|---|---|---|---|---|
| M1 | premature read of a live artifact | **variant of face 3** | truncate the fixture; if the reader's output differs only in row count and in no named field, it is exposed | **no**; would have broken a launcher's provenance, not a number |
| M2a | reader answering a different question (`git diff` vs poisoned index) | ⚠ **NOT this taxonomy** — the ruled class at `LAB_STATE:28544` | name the reference the comparison is against, then require the proof to print a change it is known to be able to see | **no — caught.** ⚠ but it is the one that attacks rule 2's own freeze check |
| M2b | `checkMesh` absent-line variants | **variant of face 2** | **the witness field**: run the reader on a real artifact and on a missing one and diff the outputs — a sound reader differs in a named, non-null field | **no**, and RUNG 0b prevented it by design; the same defect DID move a gate once, in the safe direction |
| M3 | the commit-message pair | **variant of face 3** | resolve the citation with `git rev-parse <commit>:<path>`; a message is not a payload | **no**; it downgraded a frozen amendment's citation to `RELAYED NOT VERIFIED` |
| M4 | the domain gap | ⚠ **not a face — a map** | name the object the reader consumes, then look for a plant into **that kind** of object | **no — but ONE INSTANCE WOULD HAVE**, `L-470` (2), a false zero that rule 4 turns into `NOT A RESULT` |

**NET EFFECT ON §28.2: ZERO NEW FACES.** Two variants (M1, M3 under face 3; M2b under
face 2), one referral out of the taxonomy (M2a), one map (M4). **The taxonomy stands at
four faces**, and the extension's value is that **three separate teams' new findings all
landed inside the existing four** — which is evidence the four are the right four, and
that evidence is worth more than a fifth row would have been.

---

### §28.6.4 DISPOSITION, AND IT IS NOT NEGOTIABLE HERE

**REPORTED, NOT GATED.** No clause is written, no instrument is built, no sweep is ordered,
no threshold is created, moved or retired, and nothing is re-graded. **Sanaa's governance
budget is the binding constraint** — her 2026-09-03 `2000Z` ruling makes *reported, not
gated* the default and `2200Z` says *"I prefer something to be running and watched than too
much governance and no run."* **This section costs zero compute and adds zero enforcement.**

The three cures named above are **already built and already running** — the witness field
at `read_ugrid_identity.py:398/401/418-426` with control B7, the skip-refusal at
`test_auto_stop_liveness.py:449-450`, and the artifact-not-message discipline at
`b78e8858`. **Nothing new is needed to act on any of this; a reader has only to copy a
shape that exists.**

---

### §28.6.5 SCOPE, HONESTLY — WHAT IS MINE AND WHAT IS NOT

**RE-DERIVED BY ME AT SOURCE:** `test_auto_stop_liveness.py:428-450`; `T5_RESULTS.md:3`
and the six `DONE.*` markers in `T5_runs/` (counted by me); `ef33434c` is empty (I ran
`git show --stat`); `10ba2567` is 1 file / 31 insertions and `b78e8858` is 3 files / 637
insertions (both `--stat`, run by me); `read_ugrid_identity.py:391-439` and
`grade_rung0b.py:65,282-287`; `referent_population_screen.py:264-293`; `L-459`, `L-470`
and `docs/LESSONS.md:19901-19919` read at source; the 261-file plant census and the
queue-class count of 1, both run by me in this invocation.

**REPORTED, NOT RE-DERIVED:** cfd's premature-read instance 1 (`LAB_STATE:23045`, **no
artifact path exists to open**); cfd's face-4 queue instance and its *"forty minutes"*
(`LAB_STATE:23048`, **no artifact path**); the originating `git diff` false-proof instance
(**corroborated at two independent board lines, but the instance itself is cfd's**).

**CLAIMED IN MY BRIEF AND NOT LOCATED BY ME:** a **second** premature-read instance; a
**sixth** heat-transfer instance (the artifact says five); and the domain-gap sentence as
a **verbatim** quote (the on-disk wording differs — `docs/LESSONS.md:22890-22895`).

**NOT MEASURED AT ALL:** the per-class planting counts for the mesh, field and
index-reading comparator classes. Proxies exist; **counts do not**, and §28.4 says what an
unrun measurement is.

*A relayed item recorded as mine would have made this section read as four measurements of
this team's, which is the exact defect §28.5 was written to avoid. The relay is named every
time.*

---

### §28.6.6 ⚠⚠ THE SUPERVISOR'S RULING ON THE MET PRECONDITION — **"WOULD HAVE CHANGED A VERDICT" IS A NECESSARY CONDITION FOR GATING, NOT A SUFFICIENT ONE, AND READING IT AS SUFFICIENT IS HOW A GOVERNANCE BUDGET GETS SPENT BY ACCIDENT**

`§28.6.1`'s M4 finds that **`L-470` instance (2) would have changed a landed verdict** — a
monitor's false `FIELD DIRS at 111.8: 0` on a run that **had** written
`111.799999999998`, which under `CLAUDE.md` rule 4 converts a complete, gradeable run into
an incomplete one and its rows into `NOT A RESULT`. **The measurement is sound and I accept
it.** The lane stopped there and said acting on it was not a lane's call. **That was
correct and it is the right instinct; the call is made here.**

**THE BAR AS IT WAS HANDED DOWN READS: *"none becomes a gate until one would have changed a
verdict."*** *Until* is a **gate-permitting** word, not a **gate-triggering** one. It names
a threshold below which gating is **forbidden**; it does not promise gating above it.
**RULED: a met precondition opens the question; it does not answer it.** *The failure mode
this ruling prevents is mechanical and would be invisible: a lab that gates on every met
necessary condition has delegated its governance budget to whoever finds the next
specimen.*

**I DECLINE TO GATE, ON THREE INDEPENDENT GROUNDS, ANY ONE OF WHICH WOULD SUFFICE:**

1. **ONE INSTANCE IS NOT A CLASS.** `§2p.5`: two instances is a **PATTERN**, not a class.
   This is **one**, and this team has refused its own sweeps on two-member populations
   twice this week. **A rule refused against my own findings is not available to me here.**
2. **NOTHING IS BLOCKED, SO SANAA'S BAR DENIES IT A CLAUSE.** The false zero **was caught**
   — by the frozen grader's independent `abs(float(d) - ENDTIME_B) <= 1e-6` reading. **No
   result is blocked today**, and her governance reform is explicit: no result blocked → no
   petition, no clause; the team records the decision and moves on.
3. **⚡ THE STRONGEST GROUND, AND IT IS THE ONE THAT WOULD SURVIVE IF THE OTHER TWO FELL:
   THE CURE IS ALREADY BUILT AND ALREADY RUNNING IN THIS EXACT DOMAIN.** The witness field
   at `read_ugrid_identity.py:398/401/418-426` with control **B7** at
   `grade_rung0b.py:282-287`, and the skip-refusal at
   `test_auto_stop_liveness.py:449-450`. **A new gate would add ENFORCEMENT without adding
   PROTECTION** — it would compel, at lab-wide cost, a shape three teams have already
   adopted voluntarily and are already running. *That is the most expensive kind of rule:
   one whose entire effect is on the people who were already complying.*

**WHAT WOULD MOVE ME, STATED IN ADVANCE SO IT CANNOT BE FITTED LATER — AND THIS IS THE PART
THAT MAKES THE REFUSAL FALSIFIABLE RATHER THAN MERELY CONVENIENT:**

> **(a) A SECOND INSTANCE IN THE SAME DOMAIN** — making it a pattern under `§2p.5`; **or
> (b) ONE INSTANCE THAT WAS NOT CAUGHT**, i.e. a false zero of this shape that reached a
> landed verdict and had to be demoted afterwards, which would put a result in the
> `§2ac` class; **or (c) an instance in a domain where NO independent second reading
> exists**, since ground 2 rests entirely on one having existed here by good fortune.
> **On (c) I note against my own refusal: the second reading that caught `L-470` (2) was
> not a control. It was luck of the same kind `§2ag.6` named — and luck is not a control.**
> **That is the honest weakness of ground 2 and I state it rather than let a successor
> find it.**

**DISPOSITION UNCHANGED: `REPORTED, NOT GATED`.** Zero instruments, zero sweeps, zero
clauses, zero thresholds created, moved or retired, nothing re-graded, zero compute.

---

### §28.6.7 THE DEFECT IN `§28.2` IS ACCEPTED AGAINST MY OWN SECTION, AND THE REPAIR IS A DISCIPLINE, NOT AN INSTRUMENT

`§28.6.0` finds that **rows 2, 3 and 4 of `§28.2` carry no artifact path** — no file, no
commit, no line — so the re-derivation could establish the **mechanisms** and could not
establish that they are **`§28`'s own specimens**. **The score is stated honestly as
`3 of 3` mechanisms re-derived and `0 of 3` proven identical.** *That distinction is worth
more than the score, and it is the kind a lane is under no obligation to volunteer.*

**ACCEPTED. THE ROW WAS MINE AND THE OMISSION WAS MINE.** `§28.5` promised that a relayed
item would be recorded as REPORTED, and it kept that promise; **what it did not do was
record WHAT WAS RELAYED WELL ENOUGH FOR ANYONE TO OPEN IT.** *An attribution without a
citation is a well-labelled dead end — it tells you whose measurement you cannot check.*

> **RULED: A TAXONOMY ROW CARRIES A PATH OR A SHA. A row naming a mechanism, a team and a
> duration, and no artifact, is UNFALSIFIABLE BY CONSTRUCTION — which is this audit's own
> frames rule turned on the audit.** It costs one field at writing time and it is the
> difference between a record and an anecdote.

**THE SPECIMENS NOW ON RECORD FOR FACES 2, 3 AND 4** — `test_auto_stop_liveness.py:428-450`,
`T5_RESULTS.md:3` with the six `DONE.*` markers in `T5_runs/`, and `ef33434c` —
**are cited here and are EXPRESSLY NOT CLAIMED to be the originals.** They are live
specimens of the same mechanisms, found on this box. **`§28.2`'s original three remain
unlocatable and are recorded as such rather than quietly replaced**, because substituting a
findable specimen for an unfindable one and saying nothing is exactly the move that makes a
record look sounder than it is.

**AND cfd's FACE-4 ORIGINAL — the "forty minutes blind to idle territory" — REMAINS
UNRE-DERIVED, with no artifact path in existence.** Under `§28.4`'s own rule, an unrun
measurement is **`NOT A RESULT`**, never absence-of-failure. **It stays REPORTED and it does
not get promoted by the passage of time.**

---

### §28.6.8 THREE ENDORSEMENTS AND TWO CORRECTIONS TO MY OWN BRIEF, WHICH THE LANE CAUGHT AND I DID NOT

**(1) THE `M2a` REFUSAL IS UPHELD AS THE SUPERVISOR'S CALL, NOT MERELY ACCEPTED AS A LANE'S
RECOMMENDATION — AND IT IS THE BEST JUDGEMENT IN THE DRAFT.** `§28`'s test is *"can this
path distinguish 'the check ran and found nothing' from 'the check did not run'?"* **On the
`git diff`-versus-poisoned-index false proof, THE CHECK RAN.** It touched a real object and
returned a **true** answer **about the wrong proposition**, so `§28`'s test comes back
**clean** on a path that is wrong. **Admitting it as a fifth face would place inside the
taxonomy a specimen the taxonomy cannot detect, and would make the test appear weaker than
it is.** It is filed to the ruled class at `L-394`/`L-395`/`L-401`/`L-402` and `§2j`, and
cross-referenced from here. ⚠ **Its danger is recorded rather than diluted by the
reclassification: the false proof it manufactures is *"no changed line touches a gate"* —
the exact assertion rule 2's freeze discipline rests on. It attacks the check that protects
every other check, and it was caught by re-deriving against the `HEAD` blob, not by any
control.**

**(2) ZERO NEW FACES IS THE RIGHT ANSWER AND IS A RESULT, NOT AN ABSENCE OF ONE.** Three
teams' independent findings all landed inside the existing four. **That is evidence the
four are the right four, and it is worth more than a fifth row.** *A taxonomy that grows
by one every time someone looks at it is a list, not a taxonomy.*

**(3) THE DOMAIN-GAP NUMBER I WILL STAND BEHIND IS THE NARROW ONE.** Of **261** files
defining a plant constant, **exactly 1** sits near a queue-shaped read, and it is not a
graded comparator: **the queue-reading class — the class face 4 was found in — has
essentially no planted control.** The mesh, field and index-class counts are **UNMEASURED**;
the proximity figures **66** and **10** are co-occurrence, not targeting, and **must not be
quoted as counts**. *"Unmeasured" is the finding there — not "small", not "probably fine".*

**⚠ TWO CORRECTIONS TO MY OWN BRIEF, BOTH FOUND BY THE LANE, BOTH RECORDED AS MINE:**
- **I handed down as VERBATIM a sentence that is not on disk in that wording.**  **[⚠ STRUCK IN PLACE 2026-09-03, §28.7.1 — WRONG; see there. It IS on disk, in the petition and in `§2aj`.]** *"We plant
  rigorously into comparators reading solver logs, and into nothing else"* is a
  **paraphrase**; the on-disk text is `docs/LESSONS.md:22890-22895`. **The paraphrase is
  faithful and sharper than the original, which is exactly what makes it dangerous** — a
  quotation improved in transit is still a fabricated quotation, and had the lane taken it
  on my authority the landed record would have carried a false quote in quotation marks.
- **I said SIX instances. The artifact says FIVE** (`docs/LESSONS.md:22843-22844`: three at
  source plus `D588`'s two, *"five instances in one session across two teams"*). **The lane
  looked for a sixth, did not find one, and refused to round up to my number.**

*Both are the `§28` family in a brief rather than in code: a number and a quotation that
arrived without an artifact and would have been believed on the strength of who sent them.
**A supervisor's brief is a relay like any other, and it gets no exemption from the audit
it commissions.*** **The lane tested the code instead of my guess, for the second time
today. That is what a lane is for, and it is recorded here rather than absorbed.**

---

## §28.7 — **CORRECTION TO `§28.6`, FILED WITHIN THE HOUR AND AGAINST MYSELF: THE PRIMARY SOURCE FOR THE DOMAIN GAP WAS IN MY OWN CHARTER ALL ALONG, THE REMEDY I WAS ABOUT TO WEIGH WAS ALREADY RULED BY THIS TEAM EIGHT HOURS EARLIER, AND `§28.6.8`'s CORRECTION IS ITSELF WRONG** (2026-09-03T21:3xZ)

**Zero compute; 0 core-min; $0.00. No gate, threshold, band, cap or label created, moved or
retired; nothing re-graded. `REPORTED, NOT GATED`, unchanged.** **Pure append: no line of
`§28.6` is renumbered and none is rewritten** — `§28.6` stands as written and is corrected
**from here**, per `§2ae`, with in-place pointers where the wrong claims are read.

### §28.7.1 ⚠⚠ THE MISS, STATED BEFORE THE CORRECTIONS

**`§28.6` cites `docs/LESSONS.md:22890-22895` as the on-disk home of heat-transfer's
domain-gap sentence, and says the version in my brief *"is not on disk in that wording."*
BOTH HALVES ARE WRONG, AND THE PRIMARY SOURCE IS IN THE CHARTER THIS TEAM OWNS.**

| what `§28.6` says | what is true |
|---|---|
| the sentence's source is `L-470` | the source is **`docs/campaigns/T-family/T25R6cR2_2D1_RECORD_EMISSION_PETITION.md:293-297`**, a **live referral addressed to THIS TEAM BY NAME** |
| the wording *"is not on disk"* | **the petition's wording IS on disk, twice** — in the petition, and **quoted verbatim in `VERIFICATION_CHARTER.md §2aj` (v1.53), by this team, eight hours before `§28.6` was written** |

**THE PETITION'S ACTUAL WORDING, WHICH IS BETTER THAN THE PARAPHRASE AND BETTER THAN MY
BRIEF:** *"the lab plants rigorously into comparators reading solver logs, and into **no git
assertion, no shell glob, and no selftest's own coverage.** That is a **domain gap in rule 3's
application**, not three coincidences."*

**TWO THINGS THE RELAY DESTROYED, AND THE SECOND IS THE EXPENSIVE ONE.** My brief's *"and
into nothing else"* (1) **turned a REFERRAL into an OBSERVATION** — it is a question put to
this team, not a remark overheard about it; and (2) **deleted the three NAMED DOMAINS.**
***"Nothing else" names nothing and therefore cannot be checked; "no git assertion, no shell
glob, no selftest's own coverage" is a measurable claim.*** *A paraphrase that drops the
falsifiable half is not a shorter version of the sentence. It is a different sentence.*

**AND `§28.6.8`'s SELF-CORRECTION IS ITSELF WRONG AND IS STRUCK HERE.** It says I invented a
verbatim quote. **What I actually did was hand down a PARAPHRASE OF A REAL SENTENCE and label
it verbatim** — which is a smaller sin than fabrication and a **different** one, and the
record should say which. **The correction was right that the wording was mine; it was wrong
that no such sentence existed.** *I corrected myself on incomplete evidence and produced a
second false statement in the act of retracting the first.*

### §28.7.2 THE REMEDY WAS NOT PENDING. IT WAS RULED BY THIS TEAM AT `§2aj`, AND I NEARLY WEIGHED IT A SECOND TIME

The petition carries a remedy at `:299-303`, explicitly *"verification's to adopt or
decline"*: require a comparator's selftest to drive a full `grade()` against a synthetic case
root and assert the verdict artifact exists and parses.

**IT IS ALREADY LAW. `VERIFICATION_CHARTER.md §2aj` (v1.53, 2026-09-03) RULES IT ALMOST WORD
FOR WORD:**

> *"A COMPARATOR REGISTERED AFTER 2026-09-03 WHOSE SELFTEST DOES NOT DRIVE `grade()` END TO
> END THROUGH ITS EMISSION PATH — against a synthetic case root, asserting the verdict
> artifact EXISTS and PARSES — IS REGISTERED INCOMPLETE."*

**with `NO BACKFILL, NO SWEEP, NO NEW INSTRUMENT`** and the check placed on the **supervisor
registering the comparator — a person, not a sweep.** `§2aj` also **already accepted the
domain gap as a finding**, in the petition's correct wording, and **already directed that it
be filed as a mechanism family in this audit** — which is what `§28.6` did without knowing it
had been told to.

> **RULED — `§28.7`: NOTHING IS OWED ON THE REFERRAL. It was answered at `§2aj` before it
> reached me a second time. NO new clause, NO new instrument, NO change of disposition.**

**⚡ AND THE NEAR-MISS IS THE FINDING, NOT THE OUTCOME.** Had the second reading not arrived,
**this team would have deliberated a referral it had already granted**, and would have done so
**with the governance budget in hand and a met precondition sitting in the same section** —
the exact conditions under which a lab writes a clause it does not need. *`§28.6.6` refused to
gate on a met precondition; it would have been a poor session in which the rule it saved was
spent on a duplicate of a rule already passed.*

### §28.7.3 `M1`'s LINEAGE — `L-307` ALREADY RULES IT, AND `M1` MUST CITE IT RATHER THAN APPEAR TO DISCOVER IT

**`L-307`** (`docs/LESSONS.md:11767`, `:21837`) already holds that **a figure taken from a
file still being written is void without its instant.** `§28.6`'s M1 states the same mechanism
and **does not cite it.** **Corrected here: M1 is `L-307` at the artifact level, and its
contribution is the DISCRIMINATING TEST, not the observation.**

**AND M1 HAS A SECOND HALF THAT `§28.6` MISSES ENTIRELY — THE READER'S END OF THE PIPE.**
`docs/LESSONS.md:3218-3220`: an auditor took a count from a file still being written because
**its wait condition fired on FIRST BYTES rather than on completion.** `docs/LAB_STATE.md:5370-5378`
(dafoam): ***"two partial reads I had treated as complete"*** — a `PASS` branch seen to
**print** and never checked to **exit** (it does: `a1ze_grade.py:586` is `return 2`), and a
`grep -c … = 5` **whose five hits were never read.**

> **THE GENERALISATION, AND IT IS THE BEST LINE IN THIS EXTENSION: A COUNT, A PRINT, AND A
> FIRST MATCHING LINE ARE THE THREE SHAPES AN UNFINISHED READ TAKES — AND EVERY ONE OF THEM
> LOOKS LIKE AN ANSWER.**
> **In M1 as `§28.6` filed it, THE WRITER had not finished. Here THE READER has not.** Same
> fail-open, opposite end of the pipe — **and the reader-side half is the one NO
> ARTIFACT-LEVEL GUARD CAN CATCH**, because the artifact is complete and correct. **The
> discriminating test must therefore be asked twice: did the WRITER terminate, and did the
> READER consume?**

**M1 is accordingly a THREE-TEAM mechanism** (cfd, heat-transfer, dafoam), **still a variant of
face 3, still not a new face.** cfd's second instance **remains NOT LOCATED and is not
manufactured.**

### §28.7.4 ONE DISCREPANCY NAMED AND NOT RESOLVED BY ASSERTION

**`§2aj` says *"six guard instances in one session"*. `L-470` at source says *"five instances
in one session across two teams"* and `§28.6` reports five.** **Five and six are two different
numbers about the same session and I do not know which is right.** It is **not** resolved here
by preferring my own charter — *that is precisely the move this section exists to correct* —
and **no count in `§28.6` is changed on the strength of it.** **Recorded as an open
discrepancy between two of this team's own records.**

### §28.7.5 WHAT THIS SECTION IS REALLY ABOUT

**`§2p.11`, ruled by this team two hours ago, says an in-place correction is driven from an
enumeration derived BY SEARCH AT CORRECTION TIME and never from the author's recall. `§28.6`
was written from a brief and a lane's first report, and the primary source it needed was in
THE CHARTER THIS TEAM OWNS, landed by this team the same day.** **I did not search my own
charter before writing a section about a referral addressed to my own team.**

***That is the third instance of one shape in one session: v1.55's interrupted correction,
VR3-R2's unmarked summary table, and now this. In all three the missing evidence was already
written down, by me, and not looked for.*** **`§2p.11`'s test is cheap and I have now failed
to run it three times in six hours** — which is a better argument for the discipline than the
clause I wrote to establish it, and it is filed here rather than in a place where it flatters
me less to be found.

---

## §28.8 — **THE VACUOUS PREDICATE: A CHECK SATISFIED BY THE ABSENCE OF WHAT IT WAS MEANT TO EXAMINE. NOT A FIFTH FACE — IT IS `§28`'s TELL RESTATED IN LOGIC INSTEAD OF EPISTEMOLOGY, AND THAT RESTATEMENT BUYS A MECHANICAL TEST THE TELL COULD NOT GIVE** (2026-09-03T22:5xZ)

**Zero compute; 0 core-min; $0.00. No gate, threshold, band, cap or label created, moved or retired; nothing re-graded. DISPOSITION: `REPORTED, NOT GATED`. No instrument is proposed and none is written.**

### §28.8.1 THE MECHANISM, AND WHY IT IS NOT A NEW ENTRY

Distilled by a dafoam lane from three same-night instances in three different artifacts:

> **A CHECK WHOSE PREDICATE IS SATISFIED BY THE ABSENCE OF WHAT IT WAS MEANT TO EXAMINE.**

**I RULE IT IS NOT A FIFTH FACE, AND THE REASON MATTERS MORE THAN THE RULING.** `§28`'s tell
is *"the absence of an error was read as the presence of a check"* — **an epistemic
description of a reader's mistake.** This is the same thing **stated in logic**:

> **A UNIVERSALLY QUANTIFIED PREDICATE IS TRUE ON THE EMPTY SET.** *"Every changed path is
> mine"*, *"every driven pin exists"*, *"every plant read back"* — **each is vacuously TRUE
> when nothing was changed, driven, or read.** The check did not malfunction. **It returned
> the correct answer to a question that had become empty.**

**AND THE RESTATEMENT IS WORTH LANDING BECAUSE IT PAYS.** `§28`'s test — *"can this path
distinguish 'the check ran and found nothing' from 'the check did not run'?"* — requires a
reader to reason about a code path. **The logical form gives a test that can be applied to a
PREDICATE, mechanically, without understanding the code around it.** *An epistemic tell finds
instances when someone is already suspicious; a logical form finds them by inspection.*

**IT SUBSUMES AT LEAST THREE OF THE FOUR FACES**, which is the strongest evidence it is the
general form and not a new member: **face 1** (swallowed refusal — `2>/dev/null` yields empty
output, so *"no errors"* holds vacuously); **face 2** (passing-on-skips — every pair skipped,
so *"every evaluated pair flipped"* holds over an empty set); **face 4** (dropped-blocked-read
— nothing read, so every property of what was read holds). **Face 3** (claim-from-completion)
is **only partly covered** and I say so rather than round up: *"the process finished"* is a
predicate about the **wrong object**, not a vacuous one about the right object. **`§28.6`'s
M2a — the reader answering a different question — is the same partial case, and it is why M2a
was refused a face.** *The vacuous predicate and the wrong-object predicate are cousins, not
one thing, and the taxonomy is more useful for keeping them apart.*

### §28.8.2 THE DISCRIMINATING TEST — MECHANICAL, AND IT FITS ON ONE LINE

> **DOES THE PREDICATE REMAIN SATISFIABLE WHEN THE EXAMINED SET IS EMPTY, OR WHEN THE EXAMINER
> IS BLIND?**
> **The operational form: substitute the empty set — or a reader that can see nothing — and
> evaluate. If the check still passes, ITS PASS CARRIES NO INFORMATION**, and it will pass on
> the day the population it was written for disappears. **A pass that survives its own
> subject's deletion was never measuring its subject.**

### §28.8.3 THE INSTANCES — THREE RELAYED, TWO RE-DERIVED BY ME AT SOURCE

`[REPORTED — dafoam; I did not open these three]`

1. **A pin census printing `driven=4 exist=4 EQUAL` while blind to a fifth pin** — *both sides
   of the equality used the same broken expression*, so **the equality was true AND vacuous.**
   ⚡ *The sharpest of the set: two readers sharing a defect agree perfectly.*
2. **A frozen plant control whose passing signature was BYTE-IDENTICAL to a totally blind
   reader's** — SO-3D's `PLANT-B`, proven by evaluating the frozen expectation for both
   readers on the same bytes. **This is `CLAUDE.md` rule 3's own control failing rule 3's own
   test.**
3. **Rule 10's protocol comment, `CLAUDE.md:114` — `# ASSERT: only your paths`** — **an EMPTY
   `diff-tree` contains only your paths.** Two lanes landed empty commits with the assertion
   satisfied.

`[VERIFIED BY ME AT SOURCE — THIS TEAM'S OWN, AND INSTANCE 3's FOURTH OCCURRENCE]`

4. **`ef33434c` — this team's own empty commit.** `git show --stat` returns **a subject line
   and NO DIFFSTAT**; its tree is **byte-identical to its parent's**, verified by comparing
   `ef33434c^{tree}` with `ef33434c~1^{tree}`. **It carries the full message of an amendment
   it did not make**, and it landed with rule 10's assertion satisfied. Struck by disclosure
   at `b086eaf6`. **Three lanes, three teams, one night, on one line of the constitution.**
5. **The `corrects:` clause-parity claim, `70a8f935`.** A comment asserted coverage was
   preserved across four records. **Made executable at my requirement, the raw sets came back
   UNEQUAL.** The limb that now guards it is explicitly a **NON-EMPTY-BASELINE** limb —
   *because two empty sets agree perfectly* — and it exists **only because the vacuous case
   was anticipated.**

⚠ **AND ONE THING THAT IS NOT AN INSTANCE, SEPARATED BECAUSE LUMPING IT WOULD INFLATE THE
CLASS.** This session's `b1659976`, which destroyed 120 committed lines, was **NOT** a vacuous
predicate: the diff was **non-empty**, the assertion `test -s` **correctly passed**, and the
defect was that **no test consumed the DELETION COUNT** (`L-476`). *A missing test and a
vacuous test are different failures, and `ef33434c` and `b1659976` are the two of them landing
in the same shell three hours apart.*

### §28.8.4 THE CURE GENERALISES, AND IT IS ALREADY IN USE ON THREE TEAMS

> **ASSERT NON-EMPTINESS ALONGSIDE THE PROPERTY.** Never *"every X has property P"* alone —
> always ***"there is at least one X, AND every X has property P."*** **The existential is not
> a nicety; it is the half that can fail.**

**Independently arrived at, three times, by three teams, before this section named it:**
dafoam's **empty-tree guard**; this team's **`test -s` on the diff-tree output** and the
**numstat comparison that replaced it**; this team's **NON-EMPTY-BASELINE limb** in the
clause-parity work. **A cure that three teams reach separately is a cure the lab already
believes in and had not written down.**

**The `ENV-0` closure principle dafoam may bring separately — *every exit states which
registered outcome occurred* — is the same idea at the exit-code layer**, and is noted here as
adjacent rather than adopted, since it has not reached me as a filing.

### §28.8.5 THE CONSTITUTION'S OWN EDGE — ROUTED CORRECTLY, AND NOT TOUCHED BY ME

**`CLAUDE.md:114` carries the vacuous predicate in rule 10's own recipe**, verified by me at
source. **Amending `CLAUDE.md` is Sanaa's alone (rule 9), and the chief has put a one-line
proposal on her desk without asking any team to touch it. THAT ROUTING IS CORRECT AND I
ENDORSE IT EXPLICITLY.** *No team may repair the constitution for her convenience, and a
supervisor who "just fixed the comment" would have done exactly the laundering rule 9
forbids.*

**WHAT THIS TEAM DOES INSTEAD, AND IT NEEDS NO PERMISSION: every private-index commit I have
made since `L-476` asserts the numstat — added, deleted and path — rather than reading a
`--stat`.** *The recipe's text is hers; what I put in my own shell is mine.*

### §28.8.6 DISPOSITION

| item | outcome |
|---|---|
| classification | **NOT a fifth face — the FORMAL STATEMENT of `§28`'s tell** |
| what it buys | **a MECHANICAL test over a predicate, where the tell required reasoning about a code path** |
| coverage | **subsumes faces 1, 2 and 4; face 3 and `§28.6`'s M2a are the WRONG-OBJECT cousin, only partly covered — and kept apart deliberately** |
| the test | **does the predicate remain satisfiable on the EMPTY SET, or with a BLIND examiner?** |
| the cure | **assert the EXISTENTIAL alongside the universal — "at least one X, AND every X has P"** |
| instances | **3 REPORTED (dafoam), 2 RE-DERIVED by me (`ef33434c`, `70a8f935`)** |
| ⚠ not an instance | **`b1659976` — non-empty diff, missing test, not a vacuous one. `L-476`, a different failure** |
| verdicts moved | **ZERO** |
| the constitution | **`CLAUDE.md:114` carries it; ROUTED TO SANAA by the chief; NOT touched by this team, and that routing is endorsed** |
| sweep · backfill · new instrument | **0 · 0 · 0** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

## §28.9 — **THE CALIBRATION RATIO'S PREDICTED VALUE IS NOT PROTECTED, AND THERE ARE NOW TWO WAYS TO DEFEAT IT. THEY ARE DIFFERENT MECHANISMS AND KEEPING THEM APART IS THE POINT. RECORDED, NO INSTRUMENT, NO CLAUSE, NO BACKFILL** (2026-09-03T23:1xZ)

**Zero compute; 0 core-min; $0.00. `REPORTED, NOT GATED`. No gate, threshold, band, cap or label created, moved or retired; nothing re-graded; no team owes migration work.** *This audit is the accumulator by this team's own direction at `VERIFICATION_CHARTER §2aj` — the place a measurement can gather without anyone owing a backfill today.*

### §28.9.1 THE FINDING, VERIFIED AT SOURCE

`CLAUDE.md` rule 12: ***"Every run is costed in its pre-registration; a proposal with no cost is disqualified."***

**`[VERIFIED BY ME AT SOURCE, NOT RELAYED]` `cases/dafoam/ladder-a/A2/curriculum_D6RF2/PREREGISTRATION.md` — the three point estimates `155.70`, `60.07`, `215.77` return `0`, `0`, `0`. The document carries `cap` 15 times.** **The CAPS are frozen; the ESTIMATES are not in the frozen bytes at all.** They exist only in the queue row.

**The referring lane flagged it as possibly wider WITHOUT claiming that**, in their own words — *"generalising from one is the move corrected twice tonight."* **That restraint is correct and I adopt their framing rather than widening it.**

### §28.9.2 ⚠ TWO MEMBERS OF ONE FAMILY, AND TWO DIFFERENT MECHANISMS

The family: **the calibration ledger's `actual / predicted` ratio has no protection on its
DENOMINATOR.** Sanaa's 2026-08-23 directive makes that ratio the payoff of the whole
pre-registration design — *"so we can improve the lab's estimates."* **A ratio whose predicted
value is unprotected cannot serve it.** But the two members fail in **different** ways and
lumping them would lose the distinction that makes each fixable:

| | mechanism | what breaks |
|---|---|---|
| **(a)** recorded at `V-65`, 2026-09-03 — an **INEQUALITY** estimate (*"< 1 core-min"*), live at `SPINE_2D1_GRADING_PATH_PETITION.md:246` | **there is no predicted VALUE to divide by**, so the ratio becomes an upper bound **any small actual satisfies** | ⚠ **UNFALSIFIABLE — a check that cannot fail (`§2p`), squarely this audit's class** |
| **(b)** this one, D6RF2 — **NO estimate in the frozen bytes at all** | the predicted value **carries no freeze**, so it could have been written, or rewritten, **after the actual was known** | ⚠ **FALSIFIABLE BUT UNATTRIBUTABLE — adjacent to this audit, not inside it, and I say so** |

> ⚡ **AND (b) IS WORSE IN THE ONE DIMENSION RULE 2 CARES ABOUT.** An inequality is at least
> **inside the freeze** — it is a weak prediction, honestly frozen. **A number living only in
> a mutable queue row is not a prediction at all in rule 2's sense**, because *"the freeze is
> the document's entire evidentiary content: it proves the gate could not have been chosen to
> fit the answer."* **A predicted cost that is not frozen cannot be shown not to have been
> fitted to the actual.**

*I keep (a) and (b) apart for the same reason I kept the vacuous predicate apart from the
wrong-object predicate an hour ago at `§28.8`: two failures that share a symptom and differ in
mechanism need two cures, and a taxonomy that merges them supplies neither.*

### §28.9.3 THE DISCRIMINATING TEST, COSTING NOTHING

> **CAN THE PREDICTED VALUE BE SHOWN TO HAVE EXISTED, IN FROZEN BYTES, BEFORE THE RUN
> STARTED?** Not *"is there a number in the ledger"* — **`grep` the point estimate against the
> frozen pre-registration's committed blob.** **If its only copy lives in a mutable row, the
> ratio measures the arithmetic and NOT the quality of the prediction**, whatever it prints.

### §28.9.4 DISPOSITION — RECORDED, AND THE INTERIM FORM IS ENDORSED AS THE ANSWER

**NO INSTRUMENT AND NO CLAUSE.** `§2p.5`: **two instances is a PATTERN, not a class** — and
these two are not even the same mechanism, so the population for **(b)** is **ONE**. **Nothing
is blocked, no verdict moved**, and `§28.6.6`'s ruling governs: a met precondition **permits** a
gate and does not **compel** one, and here the precondition is not met at all. **No backfill —
her clause 2. No team is asked to reopen a frozen document.**

> ⚡ **WHAT THE COST ROW ALREADY DID IS THE CORRECT HANDLING AND NEEDS NO RULE TO AUTHORISE IT:
> it cites the queue-row figures AS WHAT THEY ARE and NAMES THE ABSENCE.** **That disclosure
> does the work a gate would do, at zero cost, and it is what any team should do on meeting
> this.** *A number honestly labelled as unfrozen is a usable measurement; the same number
> presented as a frozen prediction is not.*

**WHAT WOULD MOVE ME, STATED IN ADVANCE SO IT CANNOT BE FITTED LATER:** **a SECOND instance of
mechanism (b)**, making it a pattern in its own right; **or** a calibration row whose ratio was
**quoted as evidence of estimate quality** and was wrong because its denominator was written
after the fact. **Until then a freeze-time assert is an instrument for a population of one, and
this team has refused three of those today** — two of them against its own findings.

---

## §28.10 — **THE MIRROR CASE: A CHECK THAT *FIRES* WHEN NOTHING WAS WRONG, AND WHOSE FILENAME ASSERTS A BREACH ITS OWN ARITHMETIC REFUTES. THE FALSE ALARM PROPAGATED INTO A CHIEF-LEVEL STANDING DIRECTIVE AS FACT AND CONSUMED A RULING. AND IT MANUFACTURES THE EXACT AMMUNITION SANAA'S MANDATORY-COMPLETION ORDER PUTS PRESSURE ON. RECORDED — NO INSTRUMENT, NO CLAUSE** (2026-09-04T01:4xZ)

**Two things land here because they are one chain, and separating them would hide the connection:
a RULING that was routed to this team and is hereby discharged, and the MEASURED FACT that the
referral's factual premise does not survive its own artifacts.**

### §28.10.1 THE RULING, WHICH WAS REQUESTED AND IS OWED

Routed to this team by the chief (CHIEF section of `docs/LAB_STATE.md`, *"verification rules"*).
The question: **does a cap overrun void the verdict of a run that nonetheless COMPLETED?**

> **RULED: NO. A BUDGET OVERRUN ON A COMPLETED RUN DOES NOT VOID ITS VERDICT, IN EITHER
> DIRECTION.** It is recorded as **named waste** under `COMPUTE_BUDGET_CHARTER` §6 and as a
> **control failure against the RUNNER**, never against the case.

Three grounds, each verified at source:

1. **THE CHARTER SPEAKS TO BUDGET ONLY, AND SAYS SO EXHAUSTIVELY BY OMISSION.**
   `COMPUTE_BUDGET_CHARTER.md:197` — *"A budget overrun stops the run. It does not get a new
   budget."* Its stated reason is **denominator drift in the charter-1 ranking ratio** — an
   estimating-discipline rationale. **No clause anywhere in that file connects an overrun to a
   verdict, to validity, or to physics**; the word *physics* does not occur in it. The clause is
   **prospective and budgetary**: stop, and re-propose with a corrected `cost_basis`.
2. **THE LAB ALREADY CLASSIFIES THE FIELD, AND IT CLASSIFIES IT AS INFRASTRUCTURE.**
   `scripts/queue_runner.py:598-606` writes into every launched record a `_field_classes` map
   placing `CAP_OVERRUN.txt` and `ESTIMATE_OVERRUN.txt` in **`infrastructure`**, under L-342's
   rule verbatim: *"a missing or inconsistent INFRASTRUCTURE field is a BOOKKEEPING DEFECT
   reported beside the verdict and voids only the cost claim; only a PHYSICS_CRITICAL field may
   produce NOT A RESULT."* `physics_critical` holds the rc, the `End` line, the `endTime` fields
   and the `0/` age guard — **and nothing about money.** This is **Sanaa's own universal
   bookkeeping rule (2026-08-26): bookkeeping never voids physics.**
3. **⚡ THE FOUR EXISTING PRECEDENTS ALL POINT THE SAME WAY, AND THE REASON THEY DO IS THE WHOLE
   DISCRIMINATION.** Four places on disk *do* turn an overrun into `NOT A RESULT` —
   `cases/F23b_HP_WEDGE/run_f23b.sh:507-511`, `cases/dafoam/ladder-a/A1/wall_resolved_alpha_tail/a1wrt_read.py:371-372`,
   `cases/F26_RINGLEB/queue_entry_F26D.json`, `cases/ansys_verification/VMFL007_R2/PREREGISTRATION.md:339-341`.
   **Every one of them is the STOPPED-run path.** F23b states the mechanism exactly: *"A kill
   leaves an INCOMPLETE level, which rule 4 refuses."* ***The `NOT A RESULT` is carried by rule
   4's completion clause, never by the budget.*** A killed run is not a result because it is
   **incomplete**, not because it was **expensive**. A run that completed is not incomplete.

**Interpreting is not altering** — the same distinction this team drew at charter `§2am` tonight.
Nothing is retired, widened or re-graded by this ruling.

### §28.10.2 ⚠ AND THE REFERRAL'S FACTUAL PREMISE DOES NOT SURVIVE ITS OWN ARTIFACTS

The referral named three cases said to have completed over their caps, one at *"4.2× its cap"*.
**None of the three exceeded its registered cap. All three finished well UNDER it.**

| case | registered cap | measured actual | ratio vs **cap** | current verdict |
|---|---|---|---|---|
| `T5_CUBE_c` | **136.8** core-min (`T5_PREREGISTRATION.md:1431`) | **16.083** | **0.118×** | `PENDING` |
| `T4b_IJ_m` | **150** core-min (`T4b_registered.json:35` @ `51618879`) | **86.300** | **0.58×** | `NOT A RESULT` |
| `T4b_IJ_c` | **25** core-min (same, `:22`) | **14.100** | **0.56×** | `NOT A RESULT` |

**`[VERIFIED BY ME AT SOURCE, NOT RELAYED]`** `T5_runs/STATUS.T5_CUBE_c` carries
`wall_s=965 … timeout_s=8208 … capped=0`, and **8208 s IS the 136.8 core-min cap** — the STATUS
file confirms the cap and the underspend in the same four lines. **⚠ My own first read grabbed the
WRONG FILE** — `T5b_runs/STATUS.T5_CUBE_c`, a different rung carrying `cap_core_min=32.8` — and
the referring lane's number was the correct one. *Recorded because a supervisor's misread that the
lane got right is exactly the thing that must not be quietly dropped.*

**WHERE 4.2× CAME FROM.** `T5_CUBE_c/CAP_OVERRUN.txt` reads verbatim: *"CAP OVERRUN REPORTED, NOT
ENFORCED: case T5_C elapsed 11433 s > **1.10 x registered 2736 s (45.6 core-min / 1 ranks)**"*.
**2736 s is 45.6 core-min — the POINT ESTIMATE — and `1.10 x` is the ESTIMATE trigger.** The
registered cap is 8208 s, three times larger and never approached. 11433/2736 = 4.18. **And the
11433 s is not the run's cost either**: it is measured from a **dead 17:41Z launch that crashed at
solver start and never wrote a STATUS**; the graded run is the 965 s relaunch.

***So a file named `CAP_OVERRUN.txt`, whose first three words are `CAP OVERRUN REPORTED`, compared
a dead launch's elapsed time against a POINT ESTIMATE and called the result a cap breach — and the
number refuting it sits in the same sentence.***

### §28.10.3 THE MECHANISM, AND WHY IT IS THE MIRROR OF THIS AUDIT RATHER THAN A MEMBER

**`§28`'s family is checks that PASS when they should FAIL.** This is the reflection: **a check
that FIRES when nothing was wrong, and whose NAME asserts a breach its own body refutes.** It is
filed here, not as a curiosity, but because of what it does downstream.

- **THE HEADLINE OUTLIVES THE REFUTATION.** A reader meets the **filename**. The arithmetic that
  refutes it is one clause later and is not read. *This is `§28`'s tell with the polarity flipped
  — the presence of an alarm read as the presence of a breach.*
- **⚡ IT MANUFACTURES THE AMMUNITION FOR THE MANOEUVRE THIS TEAM WAS ASKED TO RULE ON.** Under
  Sanaa's mandatory-completion order there is standing pressure to reach a gate pass. **A spurious
  `CAP_OVERRUN.txt` sitting beside a clean run is a ready-made, official-looking cost defect
  available to anyone who wishes to void an inconvenient verdict and re-run it.** ***Laundering a
  `GATE FAIL` into a re-run on a bookkeeping technicality is the same family as widening a gate:
  both reach a pass without the physics changing.*** §28.10.1's ruling forecloses it; this
  paragraph records that the raw material exists on disk.
- **AND IT ALREADY COST GOVERNANCE ATTENTION, WHICH IS THE MEASURED HARM.** The false 4.2× entered
  a **chief-level standing directive as fact** and routed a ruling to this team. *The damage of a
  false alarm is not noise; it is the decisions taken on it.*

### §28.10.4 TWO INSTANCES, DIFFERENT TEAMS — AND THE DISCRIMINATOR IS ONE SENTENCE ON DISK

**This is a PATTERN under `§2p.5`, not a singleton, and the two members differ in exactly one
respect that decided the outcome.**

- **cfd / F20 — DEFUSED.** `verification/campaign/F20_ISENTROPIC_VORTEX_RESULTS.md:138` is headed
  *"THE CAP OVERRUN NOTICE — an infrastructure record, and NOT a cap breach"*, and `:154-158`
  names the runner defect exactly — *"comparing elapsed wall time against the estimate while
  calling it a cap"* — records that it *"cannot and does not touch the physics or either
  verdict"*, and states its purpose: ***"Recorded here so no later reader meets the file cold and
  reads `CAP OVERRUN` as a rule-12 breach."*** **No damage.**
- **heat-transfer / T5, T4b — NOT DEFUSED.** Same artifact, same pre-fix trigger, **no note beside
  it.** A later reader met the file cold. **The damage in the bullet above is the whole difference.**

> **THE DISCRIMINATOR IS `§2ae`'s RULE AGAIN, AND IT DECIDED EVERYTHING: the resolution must be
> reachable FROM WHERE THE RECORD IS READ.** cfd made it reachable in the same file. On the
> T-family cases it is not reachable at all. *Same defect, same runner, same week — one cost
> nothing and one cost a chief directive and a ruling.*

**THE UNDERLYING DEFECT IS ALREADY FIXED AND THAT IS WHY THE ARTIFACTS ARE DANGEROUS, NOT SAFE.**
`queue_runner.py` now splits the branches: a real cap crossing writes `CAP_OVERRUN.txt` at
`1.00 x registered CAP`, and the estimate branch writes `ESTIMATE_OVERRUN.txt` whose own text says
*"No cap was crossed by this record"* (`:713-744`; the miscited string `caps report;
COMPUTE_BUDGET_CHARTER` returns **0** at HEAD). ***Because the defect is fixed, these three files
will never be regenerated and will never self-correct. They are fossils that read as current.***

### §28.10.5 DISPOSITION — RECORDED. NO INSTRUMENT, NO CLAUSE, NO BACKFILL

- **NO INSTRUMENT.** This team refused three instruments yesterday for a population of one. **A
  sweep for misnamed fossils would be an instrument for a defect ALREADY FIXED AT SOURCE** — it
  would guard a door nobody can walk through again. `§28.6.6` governs: **a met precondition
  PERMITS a gate, it does not COMPEL one.**
- **THE CURE IS THE ONE cfd ALREADY DEMONSTRATED, COSTS ONE SENTENCE, AND IS NOT THIS TEAM'S TO
  WRITE:** a note beside each stale artifact saying what it is. **The three files sit in
  heat-transfer's run tree and this team does not write in another team's run tree** — relayed,
  not done.
- **NOTHING IS RE-GRADED.** `T4b_IJ_m` and `T4b_IJ_c` keep `NOT A RESULT`; `T5_CUBE_c` keeps
  `PENDING`. **No verdict moves in either direction on cost grounds — that is the ruling applied
  to its own subject.**
- **⚡ AND THE MEASUREMENT LEFT TWO ITEMS THAT MATTER TO HER ORDER MORE THAN THIS AUDIT DOES,
  RELAYED RATHER THAN RULED:** (1) **`T5_CUBE_c` has a clean run on disk that SATISFIES the strict
  completion rule in every limb, at 0.118× its cap, and NO VERDICT** — under a mandatory-completion
  order that is a case which has RUN and not been GRADED, and its `PENDING` is instrument-bound,
  not compute-bound. (2) **`T4b`'s `NOT A RESULT` is PHYSICS, and the failing limbs are named**:
  `C2 U_c/U_bulk 1.1746` outside ±3 % of 1.2245; `C6.1 p_rgh 2.12e-06 > 1e-06`; `C6.2 growth
  1.1366 > 1.05`; `C6.3 field change 2.848e-04` and `8.170e-04 > 2e-04`. **Cost appears nowhere in
  that refusal, and the triples themselves read `CONVERGING`.** *That is a work list, not a
  blocker.*
- **WHAT WOULD MOVE ME, STATED IN ADVANCE SO IT CANNOT BE FITTED LATER: a THIRD instance of a
  misnamed artifact arising from a defect that is NOT already fixed at source; or any record
  citing a cost artifact as the reason a COMPLETED run's verdict was moved, re-run or withdrawn.**
  **Measured today across tracked files: ZERO such records exist** — the reader was shown able to
  see non-zeros first (`CAP OVERRUN REPORTED, NOT ENFORCED` → 10 files; `cap overrun` → 20).
  **Not searched, and stated rather than glossed:** repository history, untracked drafts, and the
  out-of-git roots under `/home/ubuntu/`.

---

## §28.11 — **THE LIKELIHOOD-RATIO-1 CHECK: A CHECK THAT FIRES CORRECTLY, MEASURES A REAL PROPERTY, AND DISCRIMINATES NOTHING — BECAUSE THE OBSERVATION IT GRADES ON IS EQUALLY PROBABLE UNDER BOTH HYPOTHESES. A GATE IN THIS REPOSITORY CAN BE MOVED WITHOUT DELETING A BYTE, AND THE INSTRUMENT COMPUTES THE RIGHT QUANTITY, PRINTS IT, AND DOES NOT GRADE ON IT** (2026-09-04T02:0xZ)

**NOT a fifth face, NOT the vacuous predicate, and I keep it apart from both for the reason `§28.8`
and `§28.9` were kept apart: two failures sharing a symptom and differing in MECHANISM need two
cures, and a taxonomy that merges them supplies neither.**

### §28.11.1 THE STRUCTURAL FACT, MEASURED ACROSS THE WHOLE POPULATION

**398 pre-registrations at HEAD. 263 carry a self-declared freeze commit. 88 were touched after
that freeze. Lines INSERTED after freeze: 16,569. Lines DELETED after freeze: ZERO.**

***Every post-freeze change to a frozen registration in this repository is a pure append.*** That is
not an anomaly — **it is the lawful form**: rule 2 says changes land *"only as dated addenda."*

**⚡ AND THEREFORE THE PROHIBITED ACT AND THE PERMITTED ACT HAVE THE SAME SIGNATURE.** Rule 2's
forbidden act — *"addenda … cannot alter a gate, threshold, cap or label"* — **is itself performed
by appending.** ***A gate in this repository can be moved without deleting a byte.***

### §28.11.2 THE INSTRUMENT, READ BY ME AS SOURCE — IT COMPUTES THE RIGHT QUANTITY AND DISCARDS IT

`scripts/audit_freeze_path_drift.py`, **`[VERIFIED BY ME AT SOURCE, NOT RELAYED]`**:

- **`:68-71`** defines `GATE_LINE` under the comment ***"# lines rule 2 forbids moving after first
  compute"***. The instrument knows exactly what it is hunting.
- **`:256`** computes **both** channels: `gate_lines_lost=moved` and **`gate_lines_new=added`**.
- **`:455-458`** is the verdict, and it reads **only two fields**:
  `"APPEND-ONLY (consistent with a lawful dated addendum)" if d["appended_only"] and not
  d["gate_lines_lost"]`.
- **`:466`** *prints* `gate_lines_new`. **It appears NOWHERE in the verdict expression.**
- **`:353-359`**, the selftest, asserts on `appended_only` and `gate_lines_lost` and has
  ***NO ARM FOR `gate_lines_new` AT ALL***.

> ***The instrument measures the exact quantity that would detect the act, prints it as
> decoration, grades on the one channel the act does not use, and its own selftest never
> exercises the channel that matters.***

**This is `docs/LESSONS.md`'s "evidence annotated as non-binding" in its purest form: a printed
discrepancy that binds nothing is worse than one never computed, because its presence on the page
is read as coverage.**

### §28.11.3 THE MECHANISM, NAMED PRECISELY — AND IT IS NEW TO THIS TAXONOMY

The defect is not that the check is empty (`§28.8`) or that it cannot fail (`§28`'s classic face).
**It fires. It fails sometimes — on deletions. It measures a true property.** The defect is
**evidential**:

> **THE LIKELIHOOD-RATIO-1 CHECK: `P(observation | lawful) ≈ P(observation | unlawful)`.**
> Observing *"append-only"* is **equally probable** whether the addendum lawfully adds prose or
> unlawfully moves a gate — **because rule 2 requires BOTH to be appends.** ***A test whose
> observation is equally likely under both hypotheses transfers no information, however
> correctly it is computed.***

**And the verdict string states the fallacy out loud: `"APPEND-ONLY (consistent with a lawful
dated addendum)"`.** *Consistent with* is exactly right and exactly useless — **the observation is
equally consistent with the unlawful one.** The parenthetical is an **inference presented as a
verdict**.

**THE DISCRIMINATING TEST, MECHANICAL, ONE LINE — the same shape as `§28.8`'s:**
***Ask what the check would print if the prohibited act HAD occurred. If the answer is "the same
thing", the check has no evidential content, whatever it computes.***

**Distinguished from its neighbours, deliberately:** `§28.8`'s vacuous predicate is TRUE ON THE
EMPTY SET — cured by asserting the existential. **This one's set is NON-EMPTY and its predicate is
TRUE OF REAL DATA** — the cure is not an existential but a **DIFFERENT OBSERVABLE**. `§28.9`'s
unprotected denominator is an unfalsifiable *quantity*; this is a *comparison* that is perfectly
falsifiable and simply points nowhere. **Three different cures. Three entries.**

### §28.11.4 ⚠ WHAT I DID **NOT** FIND, STATED PLAINLY BECAUSE IT CUTS AGAINST THE ALARM

**No violation is alleged here, and the two self-declared post-freeze gate changes on the record
are both LAWFUL. I checked the harder one at source rather than assuming it.**

- **`0a62c5c6`** — F28's absolute stationarity floor, whose own subject says ***"A GATE CHANGE ON A
  FROZEN REGISTRATION"***, changing `ptp ≤ 0.001·|T_mean|` to `ptp ≤ max(0.001·|T_mean|, T_floor)`.
  **287 lines added, 0 removed.** **`[VERIFIED BY ME AT SOURCE]`** Sanaa's capture
  `etc/sessions/2026-08-31T2016Z_sanaa_three_rulings_runner_2h3_f28floor.md` records her words
  verbatim — ***`"F28 floor": approved`***. **Retiring or widening a gate is reserved to her, and
  she took the decision herself. LAWFUL, and the approval's WIDTH matches what was done** — the
  rule-9 question asked and answered rather than assumed.
- **`b50cd1ca`** — F28 Addendum 7, ruling that `T_total = T_duct + T_hub + T_disk`. **Also
  appended; also lawful, and on a DIFFERENT ground: it is INTERPRETATION, not alteration.** The
  frozen text *graded* `T_total` and never *defined* it; the definition is derived from the
  document's own registered control volume (§9.6, bounded at `x = 3 D`, `r = 15 D`, enclosing duct,
  centrebody and source) and **independently corroborated** by a second registered identity in the
  same document (§9.5's `T_total/T_disk = 2σ` reducing at `σ = 1` to `T_duct + T_hub = T_disk`,
  which is §3.3's cited source sentence in symbols). ***This is exactly charter `§2am`'s pattern —
  the document names its own reader — and the narrower reading would make §9.6's gate compare a
  partial force against a total flux.***

> **⚡ AND THAT IS THE POINT, NOT AN ASIDE. cfd handled these two DIFFERENTLY AND DREW THE RIGHT
> LINE: the criterion change went to Sanaa and got her word; the definition of an undefined term
> was ruled by the supervisor with derivation plus independent corroboration. THE DISCIPLINE WAS
> CORRECT. THE INSTRUMENT CANNOT SEE THAT IT WAS.** *`audit_freeze_path_drift.py` returns the same
> verdict — `APPEND-ONLY`, clean — for the approved gate change, the lawful interpretation, and a
> hypothetical unlawful widening alike.* **Its discriminating power against the act rule 2 forbids
> is ZERO, and that is true even though every case it has actually met was lawful.**

### §28.11.5 WHY THE OBVIOUS CURE IS THE WRONG ONE — `§28.10` APPLIED TO MYSELF WITHIN THE HOUR

The obvious repair is *"grade on `gate_lines_new`."* **I decline it, and the reason is the finding
I filed one section ago.**

**A gate-carrying line appears in LAWFUL appends constantly** — an approved change, an
interpretation, a results table quoting the gate it was graded against, a cost row naming a cap.
**Grading on the mere presence of a gate line would fire on all of them.** That manufactures
exactly `§28.10`'s pathology: **a stream of official-looking alarms on clean work, which are then
either ignored or available as ammunition to void an inconvenient verdict.** *A false-alarm
generator is not an improvement on a silent instrument; `§28.10` measured what one of those costs.*

> **THE DISCRIMINATOR IS NOT THE PRESENCE OF A GATE LINE. It is a gate line appended with
> NEITHER a disclaimer that no gate moved NOR a cited authorisation.** Rule 2 leaves exactly three
> lawful shapes — the append moves no gate (and lawful addenda say so, in the standard form *"alters
> NO gate, NO threshold, NO cap and NO label"* plus *"lines whose number changed above this section:
> 0"*), or it interprets rather than alters, or it carries Sanaa's approval. **The fourth shape is
> the violation, and ITS SIZE IS TODAY UNKNOWN.**

### §28.11.6 DISPOSITION — RECORDED. NO INSTRUMENT AND NO CLAUSE TONIGHT. THE CENSUS IS COMMISSIONED FIRST

- **NO INSTRUMENT YET, AND NOT FOR THE USUAL REASON.** This is **not** a population of one — the
  structure is repo-wide (88 files, 16,569 post-freeze inserted lines, 0 deletions) and the
  instrument's blindness is verified in its own source. **The reason to wait is that I do not yet
  know the size of the only class that matters**, and building a detector before measuring its
  target population is how a false-alarm generator gets built. **A census of the 88 is commissioned
  and is measurement-only.**
- **NOTHING IS RE-GRADED AND NO VERDICT MOVES.** No violation is alleged; the two examined cases
  are affirmatively **lawful**.
- **NO FROZEN DOCUMENT IS REOPENED AND NO BACKFILL IS ORDERED** (her clause 2).
- **⚠ WHY THIS IS RECORDED TONIGHT RATHER THAN WHEN THE CENSUS RETURNS: Sanaa's mandatory-completion
  order creates standing pressure to reach a gate pass, and the lawful-looking route to one is an
  APPENDED addendum.** **A baseline taken AFTER that pressure acts cannot distinguish a repaired
  case from a moved gate.** *This is the last hour in which the measurement means what it says.*
- **WHAT WOULD MOVE ME TO BUILD, STATED IN ADVANCE SO IT CANNOT BE FITTED LATER: a NON-ZERO count
  in the census's fourth class — a gate-carrying line appended after freeze with neither a
  disclaimer nor a cited authorisation. A count of ZERO closes this as a latent structural hazard
  with no instances, and I will say so in those words and build nothing.**

---

## §28.12 — **I SPECIFIED THE CENSUS'S CLASSIFIER AND SPECIFIED IT WRONG, ONE HOUR AFTER WRITING `§28.11`, IN THE EXACT MANNER `§28.11` DESCRIBES. THE PRE-REGISTERED CLOSURE CONDITION RETURNED ITS ZERO AND I DECLINE TO CLOSE ON IT. AND THE ROOT CAUSE IS THAT RULE 2's FREEZE IS NOWHERE RECORDED IN MACHINE-READABLE FORM** (2026-09-04T02:3xZ)

**This section is filed against this team's own work, by the lane it briefed, against the brief it
was given.**

### §28.12.1 THE DEFECT IN MY OWN SPECIFICATION

`§28.11` commissioned a census whose discriminating class was *"a gate line appended with NEITHER a
disclaimer that no gate moved NOR a cited authorisation."* **I wrote the class-B definition to
accept, via an "and/or", either the sentence *"alters NO gate, NO threshold, NO cap and NO label"*
**or** the sentence *"lines whose number changed above this section: 0."***

> **⚠ THOSE TWO SENTENCES ANSWER DIFFERENT QUESTIONS, AND I TREATED THEM AS INTERCHANGEABLE.**
> *"Lines whose number changed above this section: 0"* is a **RULE 6** assertion — it says **no
> text above moved**. Rule 2 asks whether **a gate was altered**. ***A pure append can move a gate;
> that is the whole content of `§28.11`. So the rule-6 assertion is ORTHOGONAL to the rule-2
> question, and my classifier accepted the first as evidence of the second.***

**`[VERIFIED BY ME AT SOURCE, NOT RELAYED]` The proof is my own calibration commit.** `0a62c5c6` —
whose subject says ***"A GATE CHANGE ON A FROZEN REGISTRATION"*** and which is lawful only because
Sanaa approved it personally — contains `**Lines whose number changed above this section: 0.** This
is a pure append`, and contains **ZERO** rule-2 gate-unchanged assertions. **The count of the
latter is 0, and correctly so: it DID alter a gate.** ***My classifier returned class B —
"disclaimed" — for the one commit on the record that indisputably moved a gate.***

**AND THIS IS `§28.11`'s OWN MECHANISM, COMMITTED BY ME, ONE HOUR AFTER I NAMED IT.** `§28.11`
says: *a check keying on an observable equally probable under both hypotheses transfers no
information.* **The rule-6 assertion is present in lawful and gate-altering appends alike** — it is
a **likelihood-ratio-1 observable**, and I built the census's safe harbour on it. *The taxonomy
caught its author within the hour, which is the only reason it is worth having.*

### §28.12.2 THE SIZE OF THE SINK, MEASURED

- **32 of 286** class-B events carry **both** a disclaimer **and** a cited Sanaa authorisation.
  ***An append that disclaims AND invokes an approval is the signature of a gate change being
  MADE, not one being restated*** — an append that moved nothing needs no approval. **All 32 are
  invisible in the D column under my rule.** Named among them: `0a62c5c6` and `9f7a7488` (F28),
  `440aca3d` (F23b), `07667a58` (A1WR), `2a43ca26` (RUNG0), `75d347f3` (A1WRT), `1af060a9` (ACTD).
- **7 further B events rest on the rule-6 line-count assertion ALONE**, with no gate-unchanged
  assertion anywhere in the append: `8fc1d764` (D6RF), `c1acb8e7` and `0cf8f4f6` (K0f),
  `b925db19` (T9aD), `bbbcdf71` (F25_DUCT3D), plus two.
- **⚠ None of this alleges a violation.** Every one may be entirely lawful — 32 of them cite an
  approval, which is the lawful route. **What is established is only that the census could not
  tell, and that my classifier reported them as clean.**

### §28.12.3 ⚡ THE ROOT CAUSE, AND IT IS DEEPER THAN EITHER CLASSIFIER: THE FREEZE IS NOT RECORDED

**Rule 2 says a registration is *"frozen by sha."* NOTHING IN THIS REPOSITORY RECORDS WHICH SHA.**
Every freeze-drift instrument here must therefore **guess the freeze from commit-message prose**,
and a prose regex fails in both directions. **Measured, and confirmed by me at source:**

- **`FROZEN` matches inside `UNFROZEN`.** Subjects reading *"NOT THE FREEZE COMMIT"*, *"NOT
  FROZEN"*, *"STILL UNFROZEN"* are scored as freezes: **10 files under the newest-match rule, 19
  under the oldest.** **7 of the 11 wider-rule class-D hits sit on such files** — they are artifacts
  of the proxy, not findings.
- **⚠ AND THE DESCRIPTIVE SUBJECT BEATS THE DECLARATIVE ONE. `[VERIFIED BY ME]`** For F28 the
  newest subject matching the regex is **`b50cd1ca`** — *"…THE **FROZEN** TEXT GRADED A QUANTITY IT
  NEVER DEFINED…"*, where the word is **descriptive prose** — while the actual freeze,
  **`76ce0ed5`** *"F28 DUCTED ACTUATOR DISK IS **FROZEN** — ARMED, NEVER RUN"*, ranks **third**.
  ***The proxy therefore zeroes out all seven of F28's genuine post-freeze commits — including BOTH
  of the calibration commits I supplied to validate the census.*** *The instrument was blind to the
  very file I chose to calibrate it with.*
- **147 of 415** prereg-named tracked files carry **no freeze-matching subject at all** and are
  **wholly invisible** to any such census — 55 in `verification/campaign/`, 17 in `cases/dafoam/`,
  11 in F14-cooling-ladder.
- **And post-freeze ≠ post-compute.** Rule 2 closes gates at **first compute**, not at freeze.
  Several hits are pre-compute amendments, which rule 2 **expressly permits**.

> ***THE STRUCTURAL FINDING: rule 2's freeze is real, is load-bearing, and is recorded ONLY IN
> PROSE. No instrument can anchor on it. That — not a weak regex — is why both this lab's
> freeze-drift instruments are blind, and it is why mine was too.***

### §28.12.4 THE PRE-REGISTERED CLOSURE CONDITION RETURNED ITS ZERO AND I DECLINE TO CLOSE ON IT

`§28.11` stated, in advance and in these words: *"A count of ZERO closes this as a latent
structural hazard with no instances and I will say so in those words."*

**The count came back: class D = 2 under the registered rule, 11 under the wider one, and NONE of
the 11 reads as an unauthorised, undisclaimed gate alteration.** By the letter of my own
pre-registration, that is the zero, and closure is available.

> **I DECLINE IT. THE ZERO IS IN A COLUMN MY OWN CLASSIFIER DEFINED WRONGLY, AND A ZERO FROM A
> READER NOT SHOWN ABLE TO SEE A NON-ZERO IS NOT EVIDENCE (rule 3).** The lane's plants prove the
> classifier can see **its own** class D — but `§28.12.1` proves the class was **specified to
> exclude the real instances.** ***The question I REGISTERED was answered. The question I MEANT was
> not. Taking the closure would be grading the observable I happened to measure instead of the one
> the hazard lives in — which is the exact error `§28.11` exists to name.***

**⚠ AND I RECORD THAT THE EXIT WAS AVAILABLE AND PRE-AUTHORISED BY MY OWN HAND, because a
pre-registration that is only honoured when its answer is inconvenient is not a pre-registration.**
*The freeze exists to stop a gate being fitted to an answer; it must equally stop a CLOSURE being
fitted to one.* **`§28.11`'s hazard therefore stays OPEN, with its size still unmeasured.**

### §28.12.5 DISPOSITION — STILL NO INSTRUMENT, AND THE CURE IS ROUTED RATHER THAN IMPOSED

- **NO INSTRUMENT, THIRD REFUSAL IN THIS FAMILY TONIGHT.** **A better regex is not the cure** — the
  defect is the absence of the anchor, and no classifier built on prose can be sound.
- **THE CURE IS A MACHINE-READABLE FREEZE PIN** — the freezing sha recorded in the registration or
  beside it, so an instrument can ask *"has this file changed since ITS OWN freeze"* instead of
  guessing. **It costs almost nothing per registration and it would make both existing instruments
  sound at once.**
- **⚠ AND IT IS NOT MINE TO IMPOSE. A new required field in every team's pre-registrations changes
  six teams' practice**; that is a cross-family convention, and under the lab's running-first
  posture tonight it is **PROPOSED, ROUTED, AND NOT ENACTED.** *This team has spent the night
  ruling that pressure never reaches a gate; it will not answer that by pushing an unrequested
  convention onto every team at 02:30.*
- **NOTHING IS RE-GRADED, NO VIOLATION IS ALLEGED, NO FROZEN DOCUMENT IS REOPENED, NO BACKFILL.**
- **WHAT WOULD MOVE ME TO BUILD, RESTATED AND NARROWED SO IT CANNOT BE FITTED: a gate-carrying line
  appended after a registration's OWN RECORDED FREEZE — anchored on a pin, not on prose — with
  neither a rule-2 gate-unchanged assertion nor a cited authorisation. Until an anchor exists,
  that measurement CANNOT BE TAKEN, and I will not report a number that stands in for it.**

---

## §28.13 — **`§28.11`'s HAZARD IS MEASURED AT LAST, BECAUSE I WAS ANCHORED ON THE WRONG EVENT: RULE 2 TURNS ON **FIRST COMPUTE**, NOT ON THE FREEZE — AND FIRST COMPUTE IS ALREADY MACHINE-READABLE. ZERO VIOLATIONS ON 29.5 % COVERAGE. THE FREEZE-PIN PROPOSAL IS WITHDRAWN FROM SANAA'S DESK. AND THE ANCHOR ITSELF CARRIES A DEFECT THAT IS A REFERRAL IN ITS OWN RIGHT** (2026-09-04T15:5xZ)

### §28.13.1 THE CORRECTION THAT UNBLOCKED IT — AGAINST MYSELF, AGAIN

`§28.12` concluded that `§28.11`'s hazard **could not be measured** without a new lab-wide freeze
pin, and put that pin on Sanaa's desk. **That conclusion was wrong, and wrong in the same way twice:
I anchored on the wrong event.**

**Rule 2 does not turn on the freeze. It turns on FIRST COMPUTE** — *"Before first compute,
amendments are legal … After first compute gates are closed."* **Edits between freeze and first
compute are EXPRESSLY LAWFUL**, so a freeze anchor was measuring a boundary rule 2 does not police.
***And unlike the freeze, first compute is already recorded, machine-readably, by the lab's own
runner.***

> **`§28.12` said the measurement could not be taken. It could — I had simply been asking for the
> wrong timestamp. A proposal to change six teams' practice rested on that error, and it is
> withdrawn below.**

### §28.13.2 THE ANCHOR, AND ITS COVERAGE STATED HONESTLY

**`[VERIFIED AT SOURCE]`** `verification/queue/<team>/launched/*.json` carries `_launch.utc` on
**352 / 352** records, **triple-witnessed**: `_launch.started_epoch` agrees within 90 s on **349/349
with zero disagreements**, and the `_launch.wrapper_out` filesystem mtime is consistent on
**349/349**. *That is a genuinely corroborated timestamp, not a single trusted field.*

**⚠ COVERAGE IS THE LIMIT AND IT IS NOT SMALL: the 352 records resolve to only 123 distinct
pre-registrations out of 417 — 29.5 %. 294 pre-registrations have NO queue launch record and are
INVISIBLE to this route.** *Stated before the counts, not after.*

### §28.13.3 THE COUNTS — AND NONE OF THE FLAGGED ROWS SURVIVES ADJUDICATION

**91 post-first-compute commits across 33 pre-registrations.** Classified with `§28.12`'s correction
applied — **a rule-6 line-count assertion does NOT count as a rule-2 gate-unchanged assertion**:

| class | count |
|---|---|
| **A** no gate line added | 2 |
| **B** gate line + genuine **rule-2** assertion | 32 |
| **C** gate line + authorisation cited | 56 |
| **D** ⚠ gate line, neither | **1** (3 before adjudication) |

**All three flagged rows adjudicated by reading, and none is a violation:** two on `T5` are lawful
**pre-compute** amendments against an anchor shown invalid below; the third, `8fc1d764` on `D6RF`,
**self-labels POST-COMPUTE and carries a substantive rule-2 assertion** — *"may not alter a gate,
threshold, cap or label. **It does not.**"* — which the classifier missed **only on phrasing**
(*"may not alter"* vs *"does not alter"*). **Substantively class B.**

> **RULED: on the 29.5 % of pre-registrations reachable by this anchor, the count of gate-carrying
> lines appended after first compute with NEITHER a rule-2 assertion NOR a cited authorisation is
> ZERO. `§28.11`'s hazard is REAL IN STRUCTURE AND HAS NO INSTANCES WHERE IT CAN BE SEEN.**
> **⚠ AND IT IS NOT CLOSED: 70.5 % of the population is unmeasured, and I will not report a
> measured zero as a population zero.**

**One discipline point kept from the measurement, because it is rule 9:** 44 of the 56 class-C rows
fired on the bare word *"ruling"* — **often a SUPERVISOR's ruling, which is not Sanaa's consent.**
Re-tested without crediting that word, **42 of the 44 carry a genuine rule-2 assertion anyway** and
only 2 fall through. *An authorisation-shaped word is not an authorisation.*

### §28.13.4 ⚠ THE ANCHOR'S OWN DEFECT — AND IT IS A REFERRAL, NOT A FOOTNOTE

**`[VERIFIED AT SOURCE]` `_launch.utc` records that the runner launched a WRAPPER, not that a solver
ran — and a REFUSED launch still writes a launch record AND A FALSE `rc=0` STATUS AT ZERO ELAPSED.**

Specimen, `T5_X_2d`: `log.launch` reads ***"REFUSE: no `0/**/T`, so the age guard has no datum"***,
while `STATUS.T5_X_2d` reads **`rc=0 end=2026-08-26T16:28:57Z`** — the same second as launch. **Real
compute began at 16:44:03** (`0/` written), time dirs 16:47–16:49, `DONE` 16:58:41Z. **All five T5
amendments labelled "pre-first-compute" (16:34–16:38) are therefore CORRECT**, and my anchor
**over-flagged** them — *the safe direction, but it is why every D row is adjudicated individually
rather than reported as a count.*

> **⚡ REFERRED TO cfd AS OWNER OF `queue_runner.py`, AND IT IS `§2ak`'s EXACT SUBJECT: A REFUSAL
> THAT RECORDS `rc=0` IS A REFUSAL WEARING A SUCCESS CODE.** **Rule 4 reads `rc` as
> `physics_critical`**, so a false `rc=0` is not a bookkeeping blemish — ***it is a success code on
> the one field the completion rule trusts most.*** **Not mine to repair; it sits in another team's
> instrument. Reported, with its specimen and its artifacts named.**

### §28.13.5 DISPOSITION

- **⚡ SANAA'S DESK ITEM #2 — THE MACHINE-READABLE FREEZE PIN — IS WITHDRAWN BY THIS TEAM.** It was
  built on `§28.13.1`'s error and would have changed six teams' registration practice to obtain a
  timestamp rule 2 does not use. ***A proposal withdrawn on measurement is worth more than one
  waiting on a busy owner.*** **Nothing replaces it that requires any team to do anything.**
- **THE BETTER ANCHOR, NAMED FOR WHOEVER BUILDS NEXT: the FIRST SOLVER ARTIFACT** — the first time
  directory, or the driver's `begin` line — **not the queue record.** It is immune to
  `§28.13.4`'s defect because a refused launch produces no solver artifact. **Proposed, not built.**
- **STILL NO INSTRUMENT — the fourth refusal in this family.** The measured class is **zero where it
  can be seen**, and `§28.6.6` governs: **a met precondition permits a gate, it does not compel one.**
- **NOTHING RE-GRADED, NO VIOLATION ALLEGED, NO FROZEN DOCUMENT REOPENED, NO BACKFILL.**
- **WHAT WOULD MOVE ME, RESTATED: a class-D row that survives adjudication — a gate-carrying line
  appended after a case's first SOLVER ARTIFACT with neither a rule-2 assertion nor a real
  authorisation. `§28.11`'s hazard stays OPEN at 70.5 % unmeasured, and is recorded as
  structurally real with no instances found.**

---

## §28.14 — **TWO MECHANISMS FROM dafoam, ACCEPTED INTO THE COLLECTION — AND ONE OF THEM COMPLETES A PATTERN WITH `§28.13.4`: TWO INDEPENDENT INSTRUMENTS, IN TWO TEAMS, EACH MANUFACTURING A FALSE `rc=0` ON THE ONE FIELD RULE 4 TRUSTS MOST. THE SYNTHESIS ACROSS ALL THREE IS THAT INSTRUMENTS ARE TESTED ON WHAT THEY COMPUTE AND NOT ON WHAT THEY SAY** (2026-09-04T16:3xZ) — **REPORTED, NOT GATED**

**Both relayed from dafoam citing their `S-58` (`56e9e909`) for the measurements. Recorded as
REPORTED entries: no instrument, no clause, nothing re-graded, no frozen file edited.**

### §28.14.1 THE DISCARDED AUTHORITATIVE SIGNAL — `§28.11`'s MECHANISM WITH AN AGGRAVATING FACTOR

**The measurement, as relayed:** `a1wr_cmd.sh` **captures the producer's `rc` at `:65` and prints it
at `:66`, then never consults it again.** The wrapper's own exit is decided at `:96-102` by
**counting `^AOA_POINT_END` markers — which crashed points also print.** Measured live: a run
printed ***"n_executed=0 -- NOT a completion"*** **and** ***"rc=97"***, **exited 0**, and its ledger
row reads **`rc=0`**.

**RULED — this is `§28.11`'s likelihood-ratio-1 form, and it earns its own name for the aggravating
factor, not for the base mechanism.** The marker count is **non-discriminating**: a completed point
and a crashed point both print `AOA_POINT_END`, so `P(marker | success) = P(marker | crash)` and the
count carries **no information about completion**. That much is `§28.11`.

> ***THE AGGRAVATION, AND IT IS THE SIGNATURE: THE DISCRIMINATING OBSERVABLE WAS IN HAND. It was
> captured at `:65`, PRINTED at `:66` — visible on the screen, in the log, next to the wrong
> answer — and then discarded in favour of a proxy that cannot discriminate.*** **This is not
> reaching for the only observable available; it is holding the right one and grading on the
> wrong one.**

**Distinguished from face 3 (the wrong-object predicate), deliberately:** face 3 asks about the
wrong object **because the right object was never obtained.** Here it was obtained. **The cure is
therefore different, and that difference is why it is filed separately** — face 3's cure is *go get
the right object*; this one's cure is ***consult what you already captured***. **Dafoam's own
formulation, which I adopt: a completion proxy may CORROBORATE a captured `rc`, never REPLACE it.**

**⚡ AND IT COMPLETES A PATTERN WITH `§28.13.4`, FILED BY ME ONE HOUR EARLIER, WHICH I DID NOT
EXPECT.** There, `queue_runner`'s **refused** launch writes `STATUS … rc=0` at zero elapsed while
`log.launch` reads *"REFUSE: no `0/**/T`"*. Here, a wrapper turns a captured **`rc=97`** into an exit
**0** and a ledger **`rc=0`**.

> **TWO INDEPENDENT INSTRUMENTS, IN TWO DIFFERENT TEAMS, FOUND WITHIN ONE HOUR BY TWO DIFFERENT
> ROUTES, EACH MANUFACTURING A FALSE `rc=0`.** **`rc` is `physics_critical` under rule 4 clause 1
> and under L-342's split** — ***it is the single field the completion rule trusts most, and it is
> the field two separate wrappers were quietly synthesising rather than reporting.***
> **`§2p.5`: two instances is a PATTERN, not a class. RECORDED AS A PATTERN. NO INSTRUMENT.**

**Neither instance carries a published verdict** — dafoam's words for theirs, *"that is luck, not
design"*, which I quote because it is the right posture; and `§28.13.4`'s over-flags in the safe
direction. **The frozen instrument is REPORTED, not edited.**

### §28.14.2 THE UNREHEARSED SUCCESS PATH — `§28.8`'s COMPLEMENT, AND IT GENERALISES MY OWN `§2p.3(e)`

**The measurement, as relayed:** three items, two diseases. `SO3aF2` **registered only failure
tokens**, missing the label. `A1WRT` **registered a verdict ceiling and never wrote the emitter** —
`compose_item` **0 hits against 16 `def` sites, zero verified with a live positive control**.
`a1wr_read.py` the third, **0 against 11**, masked because the item failed on other grounds.

**Their lane's generalisation, quoted because it is better than a paraphrase:**

> *"No registration was driven end-to-end against 'what does this instrument print if everything
> goes right?' A selftest suite that only exercises failure paths certifies that an item can
> DECLINE, not that it can ANSWER."*

**RULED — the pairing with `§28.8` is exact and the two are complements, not duplicates:**

- **`§28.8`, the vacuous predicate: the check is TRUE ON THE EMPTY SET.** Cure: **assert the
  EXISTENTIAL on the INPUT side** — *there is at least one X, and every X has P.*
- **`§28.14.2`, the unrehearsed success path: the check NEVER EVALUATES THE FULL SET.** Cure: **the
  EXISTENTIAL on the OUTPUT side** — *the instrument can EMIT a verdict, not merely decline to.*

***One asks whether anything went in; the other asks whether anything can come out.***

**⚠ AND I RECORD HONESTLY THAT IT GENERALISES A CLAUSE I ALREADY OWN, RATHER THAN CLAIMING
PRIORITY.** `§2p.3(e)` requires a **positive control through the production path** — but only for a
**restrictive repair**. **This is the same demand with the qualifier removed: EVERY instrument owes a
rehearsal of its success path, not only a repaired one.** *A team reached by another route the
general form of a rule this charter held in a special case, and the general form is the better one.*

**THEIR REGISTERED CURE IS ENDORSED** (`A1WRT2 §1`): **the no-verdict state is FORBIDDEN BY
CONSTRUCTION**, with an **`EXIT` trap printing `PENDING` and `rc 12` rather than silence** — the
ENV-0 closure principle applied to verdict emission. ***Silence is the one output that must be
impossible*** — because silence is the only outcome consistent with every hypothesis at once, which
is `§28.11`'s defect in its purest form.

### §28.14.3 ⚡ THE SYNTHESIS ACROSS ALL THREE, WHICH IS WORTH MORE THAN EITHER ENTRY

`§28.13.4`, `§28.14.1` and `§28.14.2` are three findings in one day about **the same narrow
interface**: not what an instrument computes, but **the channel through which it reports what
happened** — an exit code, a `STATUS` field, a printed verdict.

> ***INSTRUMENTS ARE TESTED ON WHAT THEY COMPUTE AND NOT ON WHAT THEY SAY.*** A selftest exercises
> the arithmetic, the readers, the guards — and then the result is handed to a reporting path that
> **nothing tests**, because reporting looks like plumbing. **Three of this lab's failures today
> live entirely in that plumbing: a false `rc=0` twice, and a verdict that was never emitted at
> all.** ***The report channel is the least-rehearsed part of every instrument in this lab, and it
> is the only part any reader ever sees.***

**DISPOSITION: REPORTED. No instrument, no clause, no backfill — the fifth refusal in this family.**
**Nothing is re-graded and no frozen file is edited.** **WHAT WOULD MOVE ME, STATED IN ADVANCE: a
THIRD independently-sourced manufactured `rc`, or ANY published verdict shown to rest on one. Both
present instances are explicitly unrested-upon and both were self-reported by the teams that own
the instruments** — *which is the behaviour this audit exists to make ordinary.*

---

## §28.15 — **MY OWN SWEEP GENERATED THE FALSE-ALARM STREAM I REFUSED TO BUILD AN INSTRUMENT FOR THIS MORNING. 4 OF 5 REFUTED. THE ARTIFACT MY CLASSIFIER MISREAD CARRIED A WRITTEN WARNING AGAINST EXACTLY THAT READING — AND THE CURE WAS IN THE CONSTITUTION THE WHOLE TIME** (2026-09-04T19:2xZ)

**This section is filed against this team's own instrument, on a correction from heat-transfer's
artifact-first verification. `[VERIFIED BY ME AT SOURCE where stated; RELAYED where stated.]`**

### §28.15.1 THE CORRECTION

`§2ap.6.4` published eight registrations as **RAN-BUT-UNGRADED** and called them *"operationally
urgent"*, relaying the list to two teams. **Of heat-transfer's five: ONE CONFIRMED (`T19`), FOUR
REFUTED** `[RELAYED]` — `K0eR2` graded at `1b6b710c`; `K0eR3` graded `PASS` today; `T10aVF`'s grader
did run (its gap is a missing rung-level verdict line — **the T9aR1c shape, not the T3d shape**);
and **`K0e` never ran at all.** cfd's three are still being verified by them.

> **⚠ I PUT A LIST OF EIGHT IN FRONT OF TWO TEAMS AND 4 OF THE 5 CHECKED SO FAR WERE WRONG.** The
> hedging was correct in form — *"not a mismatch"*, *"a recommendation, not an order"*, `T10aVF`
> recorded `CANNOT DETERMINE` — **but hedging does not undo the cost of a false alarm, and this
> morning at `§28.10` I refused to build an instrument precisely because it would *"manufacture a
> stream of official-looking alarms on clean work."*** ***I then produced one by hand.***

### §28.15.2 `K0e`, VERIFIED BY ME — AND IT IS WORSE THAN `§28.14.1`

**`[VERIFIED BY ME AT SOURCE]`** `verification/runs/F14-cooling-ladder/K0e_runs/launch/FP_T10/STATUS.queue.K0e_FP_T10`
reads, in its entirety:

```
launcher_rc=1 end=2026-09-03T19:23:02Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc
```

**A failed launch. `launcher_rc=1`. No solver rc at all.** *No manufactured success anywhere — the
artifact is scrupulously honest.*

> ***⚡⚡ THE ARTIFACT CARRIES AN EXPLICIT WRITTEN WARNING AGAINST EXACTLY THE READING MY CLASSIFIER
> MADE*** — `note=exit-status-of-the-launch-argv-NOT-the-solver-rc` — **and the classifier read it
> as evidence of a run anyway, because its predicate was *"a STATUS file exists"*.**

**`§28.14.1`'s aggravated form was *the discriminating observable was in hand, printed, and
discarded*. THIS IS ONE STEP WORSE: the observable was in hand, printed, AND ACCOMPANIED BY A
HUMAN-WRITTEN SENTENCE SAYING "DO NOT READ ME AS THE THING YOU ARE ABOUT TO READ ME AS."**
***Filed hours after I wrote `§28.14.1`, by my own instrument.*** *The taxonomy caught its author
for the second time in one day, which is the second-best outcome available and much better than the
alternative.*

### §28.15.3 ⚡ AND THE PROPOSED CHEAP CURE IS *ALSO* INSUFFICIENT — MEASURED, NOT ARGUED

The refinement offered was: *"'ran' needs a discriminator stronger than a STATUS file existing —
`wall > 0` or a time directory is the cheap one."* **The first half is right. THE TIME-DIRECTORY
HALF WOULD NOT HAVE SAVED THIS CASE, and I checked before adopting it.**

**`[VERIFIED BY ME AT SOURCE]`** `K0e_runs` **does** contain time directories `0` and `5` — under
**`PREFLIGHT/FP_T10/`** and under **`FP_T10.attempt1_MISSING_div_phi_T_FAILED/`**, *a directory
whose own name says `FAILED`*. ***A preflight and a failed attempt both leave time directories, so
"a time directory exists" over-includes exactly as "a STATUS file exists" does.***

> **RULED — AND THE ANSWER WAS LAB LAW BEFORE I ASKED THE QUESTION: THE DISCRIMINATOR FOR *"THIS
> CASE RAN"* IS **RULE 4's STRICT COMPLETION RULE**, WHICH ALREADY DEFINES IT IN SIX CLAUSES WITH AN
> AGE GUARD** — `rc = 0`; an `End` line; **last time == `endTime`**; fields present;
> `ExecutionTime` count == `endTime`; and every field at `endTime` **newer than the case's own
> `0/T`**. ***The age guard exists for precisely the fossil-time-directory case that fooled my
> classifier.***
>
> ***I INVENTED A BESPOKE PREDICATE FOR A QUESTION THE CONSTITUTION HAD ALREADY ANSWERED, AND MY
> BESPOKE ONE WAS WEAKER IN EXACTLY THE DIMENSION RULE 4's AGE GUARD EXISTS TO COVER.***

### §28.15.4 BOTH HALVES OF THE PREDICATE OVER-INCLUDED, IN THE SAME DIRECTION

- **"RAN"** — satisfied by a STATUS file's existence, so a failed launch qualified.
- **"UNGRADED"** — the classifier enumerated a fixed list of grade-artifact shapes, and **grade
  artifacts live in more shapes than that list** `[RELAYED]` — stdout captures, results records.
  **So a graded rung looked ungraded.**

***Both errors run toward FALSE POSITIVES. A predicate built from two over-inclusive halves does not
average out; it compounds.***

**⚠ AND I DECLINE THE CREDIT OFFERED WITH THE CORRECTION.** It was put to me that my coverage caveat
*"was correct in the direction that mattered."* **It was not.** **My caveat was about
UNDER-SCANNING — 29 of 393, the 37 unclassified — and the error that actually bit was
OVER-INCLUSION.** ***I caveated the axis that did not fail.*** *A caveat on the wrong axis is not
foresight, and recording it as foresight is how a team learns the wrong lesson from being right by
accident.*

### §28.15.5 WHAT SURVIVES, AND IT IS NOT NOTHING

- **`T19` IS CONFIRMED and is now driven: a grader-PRODUCED `NOT A RESULT`.** **That is the class's
  SECOND demonstrated known-positive**, after T3d — **`§2ap`'s evidentiary base is strengthened by
  this correction, not weakened.** *The clause was granted on three instances and two are now
  demonstrated end to end.*
- **`T10aVF` is a REAL but DIFFERENT defect** — a missing rung-level verdict line, the **T9aR1c
  shape**. **Correctly separated rather than absorbed**, which is this audit's standing discipline:
  *two failures sharing a symptom and differing in mechanism need two cures.*
- **THE METHOD THAT CAUGHT ME IS THE ONE THIS TEAM KEEPS PRESCRIBING: heat-transfer went to the
  ARTIFACTS, not to my list.** ***A relayed list is a hypothesis; the artifact is the authority.***
  **That is the third time today the artifact beat a routing note** (11,702 → 11,741; `L-486`'s
  figures; now this one) — **and the first time the routing note was mine.**

### §28.15.6 DISPOSITION

- **NO INSTRUMENT — the sixth refusal in this family, and this time the refusal is of my own sweep.**
  **The successor discriminator is not a new tool: it is RULE 4, applied.** *Nothing needs building.*
- **`§2ap.6.4`'s eight-item list is SUPERSEDED as to heat-transfer's five.** `T19` stands confirmed;
  `K0e`, `K0eR2`, `K0eR3`, `T10aVF` are struck from the class. **cfd's `F21`/`F22`/`F24` remain
  UNVERIFIED and must not be treated as confirmed by anyone, including by me.**
- **NOTHING WAS RE-GRADED ON THE STRENGTH OF MY LIST, AND NO VERDICT MOVED** — verified: the list was
  relayed as a recommendation and every team went to its own artifacts.
- **WHAT WOULD MOVE ME TO SWEEP AGAIN: a successor keyed on RULE 4's six clauses rather than on a
  bespoke predicate, run over the 37 unclassified registrations.** **Until then this team has one
  confirmed instance beyond T3d and says so, rather than eight.**

---

## §28.16 — **THE OUTCOME-ENTANGLED CONTROL: A PLANT WHOSE *VALIDITY PREMISE* IS THE VERY PROPOSITION THE GATED LIMB IS TESTING. IT IS INERT EXACTLY WHEN THE ANSWER IS BENIGN AND FIRES SPURIOUSLY EXACTLY WHEN THE ANSWER IS NOT — WHICH IS WHEN YOU MOST NEED IT. AND IT MAKES RULE 3's OWN CURE A THREE-MEMBER FAILURE SURFACE** (2026-09-04T20:0xZ) — **REPORTED, NOT GATED**

**Relayed from ansys-verification's `VMFL046-R2` triage; their record carries the measurements.
`[RELAYED — I have NOT re-derived their numbers, and I say so rather than let a reported entry read
as a verified one.]` No verdict of theirs is touched, nothing is re-graded, no instrument is built.**

### §28.16.1 THE MECHANISM

**Plant C rigidly shifts the Mach field and asserts the peak-to-peak of the interpolated `x_shock`
series is unchanged.** The plant's soundness rests on an unstated premise: ***a rigid field shift
translates the `x_shock` series cleanly ONLY IF the profile SHAPE is identical across samples —
that is, only if the shock is STEADY.***

**And steadiness is precisely what the gated limb is testing.**

| the truth about the case | the premise | what the control does |
|---|---|---|
| **shock STEADY** | holds | **INERT** — it passes, and tells you nothing you did not already assume |
| **shock UNSTEADY** | fails | **FIRES SPURIOUSLY** — and this is the case where the reader most needs to be trusted |

> ***RULED — `§28.16`: A CONTROL WHOSE VALIDITY PREMISE IS A PROPOSITION THE INSTRUMENT GRADES HAS
> NO EVIDENTIAL VALUE ON EITHER BRANCH.*** **On the benign branch it is inert and merely restates the
> assumption; on the adverse branch it fires for a reason that has nothing to do with the reader
> being broken.** ***A control that can only speak when it has nothing to say is not a control.***

### §28.16.2 THE DISCRIMINATING QUESTION — ansys's, ADOPTED VERBATIM BECAUSE IT IS BETTER THAN MINE WOULD HAVE BEEN

> **"Does the control's inertness / validity argument hold INDEPENDENTLY of every outcome the
> instrument can grade?"**

**If the answer is no for even one gradeable outcome, the control is entangled and its silence is
not evidence.** *This is the right question and I record its authorship: it came from the team whose
own case it convicts.*

### §28.16.3 ⚡ AND AN EMPIRICAL TELL THIS TEAM ADDS, BECAUSE THE QUESTION ABOVE REQUIRES REASONING AND THIS ONE DOES NOT

ansys's question is answered by **reasoning about a validity argument** — which finds instances only
when someone is already suspicious. **Their own measurements suggest a test that needs no reasoning
at all:** `L1` **inert exactly**, `L2` **moved 15 % of its own ptp.**

> ***THE TELL: IF A CONTROL'S OWN OUTPUT VARIES ACROSS LEVELS OR ARMS IN A WAY THAT TRACKS THE
> GRADED QUANTITY, ITS VALIDITY IS ENTANGLED WITH THAT QUANTITY.*** **A sound control's behaviour is
> a property of the READER, so it should be flat across arms that differ only in the physics.**
> **Variation across arms is the signature — checkable by inspection, without understanding the
> case.**

*This is the same move `§28.8` made for the vacuous predicate: an epistemic tell finds instances
when someone is already suspicious; a mechanical form finds them by inspection.*

### §28.16.4 KEPT APART FROM ITS NEIGHBOURS, AS EVERY MECHANISM THIS WEEK HAS BEEN

- **`§28.11` (likelihood-ratio-1)** is about the **CHECK's OBSERVABLE** — the thing graded carries no
  information. **Cure: choose a different observable.**
- **`§28.16`** is about the **CONTROL's PREMISE** — the validity argument is conditional on the
  answer. **Cure: establish the premise on grounds independent of every gradeable outcome, or
  replace the plant with one whose premise is unconditional.**
- **`§2d.1`'s circularity** (*"nothing a verdict depends on may be repaired on the authority of the
  verdict it produces"*) concerns **REPAIR**; this concerns **VALIDATION**. ***Adjacent, and not the
  same: one is about who may fix, the other about who may vouch.***

### §28.16.5 ⚡⚡ THE SYNTHESIS, AND IT IS UNCOMFORTABLE: RULE 3's OWN CURE NOW HAS A THREE-MEMBER FAILURE SURFACE

**This is the THIRD distinct PLANT-DESIGN class** `[RELAYED]` — after **cancellation** and
**absorption**. That matters more than any one of them:

**Standing rule 3 is one of this lab's foundational rules — *a zero from a reader not shown able to
see a non-zero is not evidence* — and THE PLANT IS HOW A READER IS SHOWN.** ***So the lab's remedy
for false zeroes now has three catalogued ways of being wrong: a plant that CANCELS, a plant that is
ABSORBED, and a plant whose PREMISE IS ENTANGLED WITH THE ANSWER.***

> **A plant is not self-certifying, and rule 3 is satisfied by a plant that WORKS, never by a plant
> that EXISTS.** *This team has spent the day ruling that presence is not evidence — of a check
> (`§28`), of a disclaimer (`§28.12`), of a run (`§28.15`). **The plant is the same lesson at the
> foundation: `PLANT = 1.234e-03` in a file is not a control; a plant demonstrated to move the
> reader is.***

### §28.16.6 DISPOSITION

- **REPORTED, NOT GATED. No instrument — the seventh refusal in this family today.** **The cure is
  the design question at `§28.16.2`, asked at plant-authoring time; it needs no tool.**
- **NOTHING RE-GRADED. No verdict of ansys's is touched, and their `VMFL046-R2` disposition is
  theirs.** **This entry catalogues a mechanism; it does not review their case.**
- **`[RELAYED, NOT VERIFIED BY ME]` — the `L1` / `L2` measurements and the plant's construction are
  ansys's, in ansys's record.** *A reported entry that reads as a verified one is the defect this
  audit exists to name, so it is labelled at the top and again here.*
- **WHAT WOULD MOVE ME TO BUILD: a FOURTH plant-design class, or any plant whose entanglement was
  discovered only AFTER a verdict rested on its silence.** **Both present instances were found by
  the teams that own the plants, before any verdict rested on them** — *which is the behaviour this
  audit exists to make ordinary.*

---

## §28.17 — **`§2ap`'s OWN REHEARSAL HAS THE SAME FAILURE MODE AS EVERYTHING ELSE IN THIS COLLECTION: *"THEIR REHEARSAL PASSED ALL FOUR LEGS BECAUSE NO LEG ASKED."* THE COVERAGE GAP IS REAL AND I DECLINE TO LAND IT AS A CLAUSE TONIGHT — NOT BECAUSE n=1, BUT BECAUSE THE ONE INSTANCE WAS SELF-CAUGHT AND NO VERDICT WAS HARMED** (2026-09-04T22:0xZ) — **REPORTED, NOT GATED**

**Routed by heat-transfer from their T3e grading; their words, relayed. `[RELAYED — I have not
re-derived their P-3 measurement.]` Nothing re-graded; T3e's `GATE REACHED` is theirs and is not
reviewed here.**

### §28.17.1 THE GAP, AND IT IS REAL

**`§2ap` rehearses BUILDER → GRADER — *can the consumer read the producer's output?* It does NOT
rehearse REGISTRATION → GRADER — *does the grader score every prediction the registration
declares?*** **Measured instance:** T3e registered `P-1`/`P-2`/`P-3`; `analyse_t3e.py` scores `P-1`
and `P-2` only; **`P-3` was measured out-of-band by hand and labelled so in the record — and `P-3`
is the one that is FALSIFIED** (`p_rgh`'s residual maximum 2.0× its seed, tiny and decaying, but F-3
is written over the maximum).

**⚡ AND THE SENTENCE THAT MAKES THIS WORTH FILING IS THEIRS: *"their rehearsal passed all four legs
because no leg asked."*** ***That is this entire collection's mechanism, arriving inside the clause I
wrote this afternoon to prevent it.*** **`§2ap`'s rehearsal is not exempt from `§28.8` and
`§28.14.2`: a rehearsal that passes all its legs has proved that ITS LEGS PASS, and nothing more.**
**I record that against my own clause, because the clause's own §2ap.5 said it proves the pair CAN
agree and not that they ALWAYS will — and this is a third thing it does not prove that I did not
name.**

### §28.17.2 WHY I DECLINE TO LAND IT TONIGHT — AND THE REASON IS NOT THE OBVIOUS ONE

**It is one instance, and that alone would be my usual ground. It is not the ground I am using,
because a plausible selection mechanism exists and I will not wave it away:** a prediction awkward
enough to be left unscored is often awkward because the quantity is marginal or the author was less
certain — **and less-certain predictions fail more often. "The unscored one was the loser" may be a
CORRELATION, not a coincidence.** *I decline to dismiss that, and I decline to act on it at n=1.*

**THE GROUND I AM USING IS THE BAR I SET WHEN I GRANTED `§2ap` THIS AFTERNOON: *would it have
changed a verdict's fate?***

| | T3d (granted `§2ap`) | T3e (this candidate) |
|---|---|---|
| the gap's consequence | **4,723.200 core-min on a run NO outcome of which could be graded** | **P-3 was measured anyway — by hand, out-of-band, and LABELLED SO in the record** |
| verdict's fate | **changed: no verdict was possible** | **unchanged: the falsification was found and disclosed** |

> ***THE INSTANCE WAS SELF-CAUGHT AND HONESTLY LABELLED, SO NO VERDICT WAS HARMED.*** **That is the
> exact condition this team has used all day to decline building — "found by the team that owns it,
> before any verdict rested on it" — and it would be incoherent to invoke it seven times and abandon
> it on the eighth because the story is compelling.** **`§28.6.6`: a met precondition permits a gate,
> it does not compel one; and here the affirmative precondition is NOT met.**

### §28.17.3 WHAT I ADOPT OUTRIGHT, BECAUSE IT COSTS NOTHING AND NEEDS NO CLAUSE

**The proposed leg's IMPLEMENTATION is sound and I want it on the record so it is not re-derived:**
at rehearsal time, **the rehearsal record states, for each prediction the registration declares,
either the grader line that scores it OR the words `reported-only`.**

**⚠ AND NOTE WHAT THAT FORM AVOIDS, because I withdrew a proposal this morning for the opposite
reason:** it requires **NO machine-readable prediction set and NO new convention on any team** — it
is a human-authored sentence in a record `§2ap` already requires, auditable by reading. **My
freeze-pin proposal died precisely because it needed a new convention across six teams. This one
does not, and that is the difference between them.**

**ENDORSED AS PRACTICE, NOT IMPOSED AS LAW.** *`§2ap` itself earned its way in because TWO teams
adopted the cure voluntarily before any clause existed. **heat-transfer should adopt this on their
own registrations if they judge it right — and that adoption, not my signature, is what would make
it law.***

### §28.17.4 DISPOSITION

- **REPORTED. NO CLAUSE, NO INSTRUMENT — the eighth refusal in this family today, and the second of
  an extension to my own clause.**
- **`§2ap` IS NOT AMENDED.** Its scope, requirement and effect are unchanged. **Nothing re-graded;
  T3e's `GATE REACHED` is untouched and is heat-transfer's.**
- **⚡ WHAT WOULD MOVE ME, STATED IN ADVANCE SO IT CANNOT BE FITTED LATER: a SECOND instance of a
  registration-declared prediction going unscored — OR, and this is the one that would move me on a
  population of ONE, an instance where the unscored prediction was NOT caught out-of-band and a
  verdict stood on the gap.** ***The first would show a pattern; the second would show harm, and
  either is sufficient.***
- **AND THE HALF I AM KEEPING REGARDLESS: `§2ap`'s rehearsal is subject to this collection's own
  family, and `§2ap.5`'s list of what it does not prove is one item short. Recorded here rather than
  by amending a clause landed six hours ago on a single further reading.**

### §28.17.5 — **THE ADOPTION DATUM, RECORDED SO IT IS COUNTABLE. AND MY OWN CONDITION WAS UNDER-SPECIFIED, WHICH THIS EXPOSES** (2026-09-05T21:3xZ)

**`[RELAYED]` heat-transfer adopted the registration→grader leg voluntarily on `T3f` (frozen
`685dc0a0`, running).** **No action requested and none taken: `§2ap` is not amended and `§28.17`'s
refusal stands.**

**MY TWO PRE-STATED MOVERS REMAIN UNMET, AND I CONFIRM IT RATHER THAN LET AN ADOPTION SUBSTITUTE FOR
THEM:** no second instance of an unscored registered prediction, and no instance where such a gap
went uncaught and a verdict stood on it. ***An adoption is evidence about a PRACTICE'S VALUE; it is
not evidence about a DEFECT'S FREQUENCY, and the two movers were about frequency and harm.***

### ⚠ AND I UNDER-SPECIFIED MY OWN CONDITION, WHICH IS THE FINDING HERE

`§28.17.3` said: *"heat-transfer should adopt this on their own registrations if they judge it right
— **and that adoption, not my signature, is what would make it law.**"*

> **THAT SENTENCE DOES NOT SAY HOW MANY TEAMS, AND READ LOOSELY IT LETS A SINGLE TEAM LEGISLATE FOR
> THE LAB.** *I did not mean that, and `§2ap`'s own precedent is the proof: it was granted because
> **TWO** teams reached the cure independently, and a third was found afterwards.* **A condition
> stated in advance must be COUNTABLE or it can be fitted later — which is this audit's standing
> complaint about everybody else's conditions, and it was true of mine.**

**RESTATED, COUNTABLY, SO THE NEXT DATUM DECIDES ITSELF: a SECOND team adopting the
registration→grader leg INDEPENDENTLY — not at my suggestion and not at heat-transfer's — makes it
ripe, on `§2ap`'s own two-team precedent. `T3f` IS ADOPTION DATUM ONE OF TWO.** *The frequency and
harm movers of `§28.17.4` are unchanged and remain independently sufficient.*

### ⚡ AND THEIR FORM EXCEEDS MINE, IN THE EXACT DIMENSION I HAVE BEEN AUDITING ALL DAY

**I endorsed a HUMAN-AUTHORED SENTENCE in the rehearsal record** — for each declared prediction,
either the grader line that scores it or the words `reported-only`. **`T3f` does something stronger:
the prediction list is carried AS DATA; the grader checks AT RUNTIME that every registered
prediction produced a verdict and REFUSES, NAMING the unscored one; and rehearsal leg 5 PROVES THE
REFUSAL LIVE by dropping a prediction and driving the grader to exit 2.**

> ***MY ENDORSED FORM IS A DISCLAIMER. THEIRS IS A CHECK PERFORMED, WITH A DRIVEN NEGATIVE
> CONTROL.*** **And a disclaimer asserted in place of a check performed is precisely what I convicted
> at `§28.12`** — where I accepted a rule-6 line-count assertion as though it answered the rule-2
> question. ***I proposed the weaker form of my own lesson, and the team that adopted it fixed that
> without being asked.***

**CONSEQUENCE FOR ANY FUTURE CLAUSE, RECORDED NOW SO IT IS NOT LOST: if this ever lands, it lands in
`T3f`'s form and not in mine** — a runtime refusal with a driven negative leg, **not a sentence in a
record.** ***A sentence can be written by someone who did not check; an exit-2 cannot.***

---

## §28.18 — **A PREDICTION CAN BE FULLY *COVERED* AND STILL BE *VACUOUS* — THIS IS `§28.8` ONE LEVEL DOWN, AT THE SCORER. AND THE PROPERTY WORTH MORE THAN THE INSTANCE: **EACH LAYER'S CURE SHIPPED THE NEXT LAYER'S DEFECT**, TWICE RUNNING — WHICH MEANS A GUARD IS NOT FREE, AND IS AN ARGUMENT FOR THE RESTRAINT THIS AUDIT HAS BEEN EXERCISING BY INSTINCT** (2026-09-06T02:0xZ) — **REPORTED, NOT GATED**

**Routed by heat-transfer from their `T3f` grade (rung verdict `PASS`, uncontaminated by design).
`[RELAYED — I have not re-derived their measurements.]` Nothing re-graded; `§2ap` is not amended; no
clause is minted.**

### §28.18.1 THE INSTANCE, AND IT IS NOT A NEW MECHANISM

**`P-4`'s scorer carried a literal `\w` from heredoc escaping, read ZERO of 48,000 matching lines,
and `max(default=0.0)` scored `HIT`.** Their layer-2 cure (leg 5) verified `P-4` **PRODUCED** a
verdict; ***nothing asked whether the verdict was DERIVED FROM DATA.***

> **RULED: THIS IS `§28.8`, THE VACUOUS PREDICATE, AT A NEW SITE — NOT A NEW MECHANISM.**
> ***`max(default=0.0)` over an empty sequence is literally "true on the empty set."*** **I have spent
> this collection keeping DIFFERENT mechanisms apart; the discipline's other half is RECOGNISING THE
> SAME ONE RECURRING, and this is the same one, one level down.**

*(The proximate cause — a shell heredoc silently changing a regex's meaning — is the family of this
lab's `grep -c` and backticks traps: **quoting that alters a program's meaning without altering its
appearance.** One line, not a new entry.)*

### §28.18.2 THE THREE LAYERS, WHICH ARE HEAT-TRANSFER'S AND ARE WORTH ADOPTING AS THE MAP

| layer | question | guarded by |
|---|---|---|
| **1 · builder → grader** | can the consumer READ the producer's output? | **`§2ap` legs 1-4** |
| **2 · registration → grader** | does the grader SCORE every declared prediction? | **`T3f` leg 5** (`§28.17.5`, adoption datum 1 of 2) |
| **3 · scorer → data** | was the score DERIVED FROM DATA, or from an empty read? | ***nothing*** |

**Their proposed cure is RULE 3 ONE LEVEL DOWN: any scorer that can return a passing value from an
empty read carries a planted control proving it can see a non-zero — as the field readers already
do.** **THE SHAPE IS RIGHT, AND `§28.18.4` says why it is the shape that TERMINATES.**

### §28.18.3 ⚡⚡ THE REGRESS PROPERTY — TWICE RUNNING, AND IT HAS TEETH

**BOTH of heat-transfer's coverage/vacuity defects arose INSIDE THE VERY REPAIR ADDED FOR THE
PREVIOUS LAYER'S DEFECT.** `§2ap`'s rehearsal (curing layer 1) contained the layer-2 gap; `T3f`'s
leg 5 (curing layer 2) contained the layer-3 vacuity.

> ***THE FIX FOR LAYER N SHIPS THE LAYER N+1 INSTANCE. A GUARD IS CODE, AND CODE NEEDS THE
> DISCIPLINE IT ENFORCES.***

**AND THE CONSEQUENCE IS NOT AN APHORISM — IT BEARS DIRECTLY ON WHAT THIS AUDIT DOES ALL DAY:**

- ***A GUARD IS NOT FREE. It adds surface, and the surface it adds is of exactly the kind it was
  built to detect.*** **So the cost of minting a clause that mandates a guard is not zero, and it is
  not merely the labour — it is a NEW INSTANCE of the defect class, arriving inside the cure.**
- **THIS IS THE MECHANISM BEHIND A RESTRAINT I HAVE BEEN EXERCISING BY INSTINCT: eight refusals in
  this family in two days, several against my own findings.** *I justified them on population bars.
  **The regress property is a second, independent justification, and a better one: an instrument
  built for a population of one adds surface for a population of one.***
- **⚠ IT ALSO CUTS THE OTHER WAY AND I SAY SO: it is not an argument for never guarding.** `§2ap` was
  granted on measured harm — 4,723 core-minutes on an ungradeable run — **and a guard whose absence
  costs that much is worth its surface. The property makes the LEDGER honest; it does not close it.**

### §28.18.4 WHY THEIR CURE IS THE ONE THAT TERMINATES THE REGRESS

**If every guard is code needing a guard, the regress is infinite — UNLESS some rung is not an
assertion about code.**

> ***RULE 3 IS EXACTLY THAT RUNG.*** **A planted control is NOT a claim that a reader works. It is an
> EXPERIMENT: plant a known non-zero, read it back off disk, REFUSE if it cannot be seen.** **Its
> correctness is not asserted in code that could itself be wrong — it is DEMONSTRATED by the reader
> moving.** ***That is why heat-transfer's "rule 3 one level down" is the right shape rather than a
> fourth layer: it does not extend the regress, it grounds it.***

**AND IT IS WHY RULE 3 SITS IN THE CONSTITUTION RATHER THAN IN A CHARTER.** *`§28.16` recorded that
rule 3's own cure has three failure modes; this records why it is nonetheless the floor: **every
other rung in this stack is code checking code, and the plant is the only one that checks reality.***

### §28.18.5 DISPOSITION

- **NO CLAUSE, NO INSTRUMENT — the NINTH refusal in this family, and consistent with `§28.17`'s
  precedent on the layer below.** **The instance is SELF-CAUGHT AND LABELLED: `P-4` was excluded from
  the verdict fold BY DESIGN, its true value measured out-of-band WITH A POSITIVE CONTROL, and the
  two AGREE. NO VERDICT WAS HARMED.** *By the bar I set at `§28.17.2` and applied at `§2as`, that is
  the ground — not the population count.*
- **ENDORSED AS PRACTICE, on `§28.17.5`'s stated terms: a SECOND team adopting the scorer-level plant
  INDEPENDENTLY makes it ripe.** **`T3f` is layer-3 adoption datum ONE OF TWO**, tracked separately
  from the layer-2 count.
- **THE REGRESS PROPERTY IS RECORDED AS A FINDING IN ITS OWN RIGHT** — *it is the only thing here that
  is not an instance of something already catalogued.*
- **⚠ WHAT WOULD MOVE ME, RESTATED FOR THIS LAYER: a scorer vacuity that was NOT caught out-of-band
  and a verdict stood on it; or a SECOND independent adopter.** **And a THIRD consecutive
  cure-ships-the-next-defect instance would move me on the REGRESS finding specifically — not toward
  a guard, but toward requiring that any newly-minted guard carry its OWN plant before it lands.**
- **ALSO RECORDED, NOT RULED — heat-transfer's restart-spike margin note (2.00× → 2.3582×, margin
  25 % → 5.7 % IN ONE CONTINUATION), registered forward for the next continuation's threshold
  design.** ***That is a physics observation on their own rung, reported and not gated, and it is
  theirs to design against — this audit notes it only so the forward registration is not the first
  place it appears.***

---

## §28.19 — **"53/53 BEFORE AND AFTER" IS NOT WEAK EVIDENCE FOR A REPAIR — IT IS *ZERO* EVIDENCE FOR IT, AND SIMULTANEOUSLY *STRONG* EVIDENCE ABOUT SOMETHING ELSE. THE MEASUREMENT SHOULD NOT BE DISCARDED; IT SHOULD BE RE-AIMED** (2026-09-06T16:1xZ) — **REPORTED, NOT GATED**

**Referred by dafoam (`be2d1120`) for a ruling. `[RELAYED — their measurements, not re-derived by
me.]` Their reading is RATIFIED IN FULL and I add the inversion they gestured at and did not take.
No clause minted, nothing re-graded, no verdict moved.**

### §28.19.1 THE FINDING, AND THEIR READING IS CORRECT

`w3s_stage_and_run.sh --selftest` returns **53/53, rc 0, on the REPAIRED file** — and **53/53, rc 0,
on the PRE-REPAIR DEFECTIVE file**, the two confirmed to differ at the guard line
(`-newermt "@$AGE_DATUM"` against `-newer "$SENTINEL"`).

**Their words, ratified: *"53/53 before and after is true and is NOT evidence the repair is correct:
it is evidence the repair BROKE NOTHING."***

> **RULED: this is `§28.11`'s LIKELIHOOD-RATIO-1 form applied to a REPAIR.**
> **`P(53/53 | defective) = P(53/53 | repaired) = 1`**, so ***the observation transfers NO
> INFORMATION about the repair — not a little, NONE.*** **A suite that returns the same value under
> both hypotheses has not weakly supported the repair; it has said nothing at all about it.**

### §28.19.2 ⚡⚡ THE INVERSION — THE SAME NUMBER IS WORTHLESS FOR ONE HYPOTHESIS AND DECISIVE FOR ANOTHER

They wrote *"and read the other way, THE DEFECT SHIPPED PAST ALL FIFTY-THREE CONTROLS."* **That
half is the more valuable one and it deserves to be stated as a rule, not as an aside.**

> ***RULED — `§28.19`: AN OBSERVATION THAT IS UNINFORMATIVE ABOUT HYPOTHESIS A CAN BE HIGHLY
> INFORMATIVE ABOUT HYPOTHESIS B. THE 53/53 IS ZERO EVIDENCE ABOUT THE REPAIR AND STRONG EVIDENCE
> ABOUT THE SUITE: it measures, precisely, that the truncation was OUTSIDE THE COVERED SET OF ALL
> FIFTY-THREE CONTROLS.***
>
> **THEREFORE: WHEN A CONTROL SUITE PASSES IDENTICALLY BEFORE AND AFTER A REPAIR, DO NOT DISCARD THE
> MEASUREMENT — RE-AIM IT. IT HAS JUST MEASURED YOUR SUITE, NOT YOUR FIX.** ***The pass is a
> coverage census nobody commissioned, and it comes free with every repair.***

*This is the useful half because a team that reads only the first half throws the number away as
"uninformative", when it has in fact just handed them a measured hole in their own instrument.*

### §28.19.3 WHAT *IS* EVIDENCE FOR A REPAIR — AND IT IS RULE 3's SHAPE FOR THE THIRD TIME

**The evidence for a repair is a control that FAILS ON THE DEFECTIVE FILE AND PASSES ON THE REPAIRED
ONE — a DRIVEN DISCRIMINATOR.** dafoam say the evidence is *"the two-limb drive, not the 53"*, and
that is right.

**⚠ AND NOTE WHERE THIS LANDS, BECAUSE IT IS THE THIRD TIME IN TWO DAYS:** `§28.18` concluded that
the scorer-level answer is *rule 3 one level down*; `§28.18.4` concluded that rule 3 is the rung that
**terminates the regress because it is an experiment rather than an assertion**; and now the
repair-level answer is **the same shape again** — plant the defect, drive the control, require it to
REFUSE. ***The lab keeps rediscovering, from independent directions, that the only evidence which
discriminates is a driven negative.*** **That is not three findings. It is one, meeting the lab in
three places, and `§2p.3(e)` already demands it for restrictive repairs.**

### §28.19.4 THE METHOD DESERVES EXPLICIT CREDIT, BECAUSE IT IS WHAT MADE THE FINDING POSSIBLE

- **THEY DROVE THE SELFTEST INSTEAD OF CITING IT FROM THE DISPATCHING BRIEF.** ***A cited number is a
  claim; a driven number is a measurement*** — and the entire finding exists only because they
  refused the citation. *This team has been convicted twice this week of the opposite.*
- **⚡ THEY RAN THE REPAIRED FILE THE SAME RELOCATED WAY AS A CONTROL, so a relocation artefact could
  not be mistaken for a result.** ***That is a control ON the control***, and it is the step that
  makes the "both 53/53" comparison mean anything at all.
- **THEY CORRECTED TWO OF THEIR OWN COUNTS AGAINST THE FILED INSTRUMENT'S OUTPUT** — 29 of 89, not
  28, *"my scratch figure was computed one repair earlier"* — and **added a SIXTH negative to close a
  gap their own mutation run exposed.** *A count corrected against an instrument rather than against
  recall is the habit `§28.15` convicted me of lacking.*
- **THEY CITED THE INSTRUMENT BY ITS FILED PATH, and recorded that no repository document ever cited
  the scratch path it was drafted in (rule 13).**

### §28.19.5 DISPOSITION

- **NO CLAUSE, NO INSTRUMENT — the TENTH refusal in this family.** **One instance, SELF-CAUGHT,
  CORRECTLY READ BY THE TEAM THAT FOUND IT, and NO VERDICT HARMED.** *By the bar at `§28.17.2`, that
  is the ground.*
- **THEIR READING IS RATIFIED AND NEEDS NO AMENDMENT FROM ME.** ***They asked for a ruling on
  something they had already got right; the ruling is that they got it right, plus `§28.19.2`.***
- **THE ACTIONABLE RESIDUE IS THEIRS AND IS NOT A CRITICISM: the 53-control suite has a MEASURED
  COVERAGE HOLE — the truncation was never in its covered set.** **`§28.19.2` says that hole is the
  free product of their own measurement.** *What they do with it is their rung's business.*
- **WHAT WOULD MOVE ME: a repair accepted on a before-and-after-identical suite pass WITH NO driven
  discriminator, and a verdict standing on it.** **Here the opposite happened, which is why nothing
  is minted.**

## §29 — **THE INSTRUMENT CONTRADICTS ITSELF ON THE SAME FIVE BYTES: `orphan_verdict` DECLARES THEM UN-GATEABLE AND `provenance_verdict` GATES THEM. `check_harness.py` HAS BEEN rc=1 WITH NO CLEARABLE PATH FOR TEN DAYS, AND ITS FOUR *CLEARABLE* FAILS HAVE BEEN RIDING BEHIND THAT RED. PLUS: §16.7 OF THIS DOCUMENT PREDICTED THIS EXACT ROW WOULD NEVER GATE, AND IS MEASURABLY FALSE** (2026-09-10T03:52Z) — **RULED ON THE FACT; REPAIR SPECIFIED, NOT YET LANDED**

**The measurement, made by me personally against the driver's own reader semantics — not relayed.** One ledger, `verification/credibility/append_block_provenance.jsonl`, 89 records, graded by two passes of `scripts/check_harness.py`:

| pass | outcomes | grading today |
|---|---|---|
| `provenance_verdict` (`:351`) | **two** — present → `ok`, absent → **`fail` (gates)** | 81 ok / **5 fail** / 2 skip / 1 superseded |
| `orphan_verdict` (`:422`) | **three** — with an explicit `lost` state, **reported and never gated** | 81 ok / **5 lost** / 3 skip |

**The provenance-GATED set and the orphan-UN-GATEABLE set are IDENTICAL as `sha256` sets. Symmetric difference: empty. n = 5.** Byte-count agreement alone would be a weak identity test, so the sets were matched on the ledger's own `sha256` field: `5c1be22cc224`, `156201d3c292`, `db4646292cc7`, `1c421574fd41`, `5ae72b9d92e0` (targets `docs/COST_CALIBRATION.md` ×3, `docs/LAB_STATE.md`, `docs/FAIL_OPEN_GATE_AUDIT.md`; 5631 / 3177 / 2429 / 3008 / 10923 bytes). All five are absent from the target **both at HEAD and on disk**.

**`orphan_verdict` knows exactly why gating these is wrong. It says so in its own source** (`check_harness.py:493-501`): *"Failing on LOST produces a red THAT NO ACTION CAN CLEAR, and the only way out of an unclearable red is to switch the clause off — so it is REPORTED, loudly and distinctly, and never gated."* `provenance_verdict` has no HEAD/disk distinction and no `lost` state at all, so it gates the very rows its sibling pass exempts, in the same run, on the same bytes.

**The price of clearing them is an act of falsification, which is what makes this un-gateable rather than merely unfixed.** The bytes do still exist, in each row's own `body_b64` — so "restore them" looks available. It is not. The supersession key is `(target, section or sha256)` (`:396`, and the identical key in the orphan pass). The three `COST_CALIBRATION.md` rows carry `section: null`, so the key falls back to **their own sha256**, and the *only* row that can retire them is a **byte-identical re-append** — of rows the lab **deliberately struck as duplicate ids** (`docs/DEAD_LEVER_AUDIT.md:3020-3023`; the substance was re-landed under corrected ids with different bytes, which therefore cannot supersede). The two headed rows carry **timestamps in the heading**, so a re-landed block can never retire them — and row `5ae72b9d92e0` is the `2026-08-31T16:55Z` stamp **its own author refused to publish because he knew it was false** (§16, landed at `16:45Z`). **Every route to making these rows "present" again requires publishing something this lab has already recorded as false to keep a ledger tidy.** That is the correct refusal, and it is precisely why the gate must not demand it.

**§16.7 OF THIS DOCUMENT IS MEASURABLY FALSE, AND IT IS MINE.** At `docs/FAIL_OPEN_GATE_AUDIT.md:1846-1848` this team wrote, of row `5ae72b9d92e0`: *"by V-33's own design that grades `LOST` — reported, and never gated. **I am declaring it here rather than letting it surface as an unexplained red.**"* It is line 5 of today's gating `FAIL provenance` block. It surfaced as **exactly** the unexplained red the section claims to have pre-empted. **Per rule 6 that sentence is NOT edited**: §16.7 stands as written and is corrected here, by this dated section, which supersedes its prediction. The generalisable defect is not the wrong answer — it is that §16.7 predicted an instrument's behaviour **from the design intent of a sibling clause** and never ran the instrument to see. A prediction about a program is checkable in one command, and a prediction about a program that was not run is a belief.

**The selftest passes, and it positively asserts the contradiction.** `--selftest` → rc=0, 55 cases, 0 failures. Its bytes-absent *provenance* limbs (`"heredoc mutation SPEAKS"`, `"one-byte flip SPEAKS"`) assert `["fail"]`; its three `lost` limbs (`:919-928`) run **only** through `orphan_verdict`. So the suite affirms that one physical condition — recorded bytes absent from both HEAD and disk — **must gate in one pass and must not gate in the other**. A green suite is therefore not evidence against this finding; it is the finding, encoded.

**Blast radius — and why it survived ten days.** `scripts/session_log.py:145` runs the check and records `check_harness_exit`/`_fails`/`_warns`; `.claude/skills/form-teams/SKILL.md:114,150` instructs each session to run it and reads a pass as *"the files are right"*; `scripts/queue_runner.sh:24` explicitly declines to gate on it. **The rc is consumed as a session-health signal and nothing anywhere gates on it** — which is exactly how a permanent red sits unremarked. The cost is the four FAILs that *are* clearable and have been invisible behind it: the `ansys-verification` missing `**Section last written:**` board stamp, and the three `numerics-index` divergences (`N-C12`, `N-D43`, `N-X4`).

**THE STRONGEST ARGUMENT AGAINST THIS SECTION, STATED FAIRLY BECAUSE IT IS A GOOD ONE.** The two passes do not grade the same proposition. `provenance_verdict` asks *"are the recorded bytes still in the file on disk today?"*; `orphan_verdict` asks *"is a **committed** row's block at HEAD?"*. The `lost` rationale was authored for the orphan proposition only, and **the provenance FAIL is a TRUE statement** — those bytes genuinely are gone, and saying so is that clause's whole job. Nothing in this repository requires a *true* report to be clearable. **That defence is accepted on the logic and it does not touch the consequence,** which is measured, not argued: five rows are simultaneously declared un-gateable and gated, the instrument is rc=1 with no clearable path, and four clearable FAILs are hidden behind it.

**THE REPAIR — and note that it SHARPENS the clause rather than weakening it, which is why the answer is not "make provenance stop gating".** Today's single provenance `fail` conflates two genuinely different findings. Split it:
- bytes absent from the working file but **PRESENT at HEAD** → **a LIVE WORKING-TREE DESTRUCTION**: somebody destroyed a committed block just now. **This must still FAIL, loudly.** It is the exact event the clause exists to catch, and today it is indistinguishable from the case below.
- bytes absent from the working file **and absent at HEAD** → **`lost`**: destroyed before ever being committed, existing at no sha, unclearable by any act that is not a falsification. **Reported, never gated**, in the orphan pass's own distinct wording.
The clause then gates **more** precisely, and recovers a real signal that is currently drowned. Constraints on the implementation: `provenance_verdict` stays a pure function (its docstring promises this so the selftest can exercise it); the new HEAD reader is a second parameter defaulting to `None`, and with `None` the behaviour must be **byte-for-byte today's**, so no existing caller silently changes meaning; `orphan_verdict` and the ledger are not touched; and the `heredoc_shadow` COMMAND-SUBSTITUTION signature (L-403/L-405) must still fire on the gating case.

**STATUS: the FACT is ruled and final; the REPAIR is drafted and NOT YET LANDED.** It is being implemented by a lane and I read it **as a diff** before it is believed — the author's own testing is evidence, never the supervisor's read (`SUPERVISION_CHARTER` §3 check 1). It lands as its own commit with a plant-drive: a selftest that merely passes proves nothing here, since the current suite passes *while encoding the contradiction*. The plant must show the repaired clause **still gating** a planted live destruction, and **not gating** one of the five known lost rows. If the reader cannot see the planted destruction, the repair is refused.

---

## §30 — **THE COMPLETION RULE'S CLAUSE 5 IS APPLIED BY 124 INSTRUMENTS AND ONLY 4 CHECK WHETHER THE FORM THEY APPLY IS THE RIGHT ONE FOR THE CASE IN FRONT OF THEM. IN `mark_done_k0g.py` — GRADING A RUN THAT IS LIVE RIGHT NOW — THE FACT THAT LICENSES ITS FORM IS ASSERTED IN A SOURCE COMMENT AND NEVER READ FROM THE CASE** (2026-09-10T03:52Z) — **RULING ISSUED; heat-transfer IS UNBLOCKED IN THIS TURN**

**Standing rule 4 clause 5 has two forms**, and which one is correct is a property **of the case**, not of the instrument: a fixed-step run is graded `n_exec == round(endTime/deltaT)`; an adaptive-`deltaT` run is graded `n_exec == steps written` (Sanaa, 2026-09-09). Applying the wrong form is not a style question — the two are not equivalent and one is strictly weaker.

**The coverage census** (lane survey, static classification, reported as a lower bound on guarded instruments): **124 Python instruments** carry an `ExecutionTime`-count comparison. **3 implement the adaptive branch. 4 read `adjustTimeStep` from the case at all.** The other **120 apply a unit-step or fixed-`deltaT` identity to whatever they are pointed at, with nothing establishing that the identity is meaningful for that run.**

**`scripts/mark_done_adaptive.py` is the one that does it right, and it is the standard the others are measured against.** `is_adjust_time_step()` (`:140-143`) reads the case's OWN `system/controlDict`, and `adaptive_step_check()` **REFUSES (exit 2) — never returns** — when the case is not `adjustTimeStep`, with the reason stated in the refusal: *"the adaptive n_exec==n_time check is only valid for a variable-step run; a fixed-deltaT case must be graded by the fixed-deltaT instrument … Refusing rather than silently accepting (fail-closed)."* Ten `adjustTimeStep` occurrences. This is the correct shape and it already exists.

**`scripts/mark_done_k0g.py` — READ BY ME AS SOURCE, and it is grading a LIVE run.** It applies the **identical** adaptive comparison (`:295-299`, `elif n_exec != n_time:`). It contains **zero** occurrences of `adjustTimeStep`. It already has a working `refuse()` (`:98`, used at `:110`, `:115`, `:352`, `:356`) and it **already opens the very file the guard would read** (`system/controlDict`, `:148`, `:263`, for `endTime`). **The fact that licenses the adaptive form — that K0g is transient with an adjustable `deltaT` — is asserted in a source comment at `:280` and is never read from the case.** The guard is one call away, in a function that already has the file open.
- **The direction of harm, stated precisely rather than dramatically.** The adaptive form checks only the *internal consistency of two counters*; it never checks the absolute step count against `endTime/deltaT`. Applied to a fixed-`deltaT` case it is therefore **strictly weaker** than the clause-5 that case is owed, and it can accept a log the prescribed form would reject. The exposure is bounded — clause 3 (last time == `endTime`) and clause 6 (the age guard) remain in force and catch the common truncation — and that bound is stated as the limit of the harm, **not** as a reason to leave it.
- **This instrument was already waiting on me, and the request is sitting inside it.** Its own comment (`:285-293`) records that verification's explicit confirmation *"is being routed via the chief and is the LAST GATE before this instrument is frozen"*, because audit V-143 covered `mark_done_adaptive.py` and not this file. **RULING, issued here so nothing waits another turn: the adaptive clause-5 logic in `mark_done_k0g.py` is CONFIRMED as the correct form for a genuinely `adjustTimeStep` run — it is the same core I audited at `2ae36a1d` — SUBJECT TO ONE CONDITION, which must be met before the instrument is frozen: it must acquire `mark_done_adaptive.py`'s fail-closed guard, reading `adjustTimeStep` from the case's own `controlDict` and REFUSING (exit 2) if it is not set.** Preferably by calling the shared core rather than copying it a fourth time. **The condition does not stop the live K0g run and is not a freeze blocker for anything else; it is a gate on the freeze only.**

**`cases/navier_class/PRD/mark_done_prd.py` is the mirror hazard, and it is grading PRD-E1, also live.** It enforces the **fixed**-`deltaT` form (`:207-208`, `want = int(round(et/dt))`). It contains exactly **one** occurrence of `adjustTimeStep` — **line 37, inside the module docstring** (the docstring opens at line 2), reading *"that path is only for adjustTimeStep runs"*. **The exclusion is prose. It is not a guard.** Its exposure is in the safer direction — a genuinely adaptive case would most likely produce a false *rejection*, not a false DONE — but "wrong in the safe direction by luck" is not a control, and it is the same defect.

**THE RULE THIS SECTION ASKS FOR (referred, not enacted — a completion-rule instrument standard is a standard, and adding one is not mine).** Any instrument applying clause 5 must **read the case's `adjustTimeStep` and refuse the form it is not entitled to apply.** An instrument that selects between two non-equivalent tests on a fact it never reads is not measuring the run; it is measuring its author's belief about the run. `mark_done_adaptive.py` already implements this and can be the shared core for all of them. **Scope honesty: the 124/4 census is a static classification and a lower bound — an individual instrument may carry a guard the pattern missed; the three adaptive-branch files and the two named above were each confirmed by direct read, by me for the two live ones.**

---

## §31 — **CROSS-TEAM FREEZE AUDIT, VMFL063-R3: THE FREEZE HOLDS ON EVERY AXIS THAT DECIDES A VERDICT — ORDER, PINS AND CONDITION. THE ONE DEFECT IS THAT THE LEGAL PRE-COMPUTE AMENDMENT WAS DISCLOSED ONLY IN A COMMIT MESSAGE AND NOT IN THE FROZEN FILE** (2026-09-10T03:52Z) — **PASS, WITH ONE DISCLOSURE REMEDY OWED. NOT A BLOCKER; THE RUN CONTINUES**

Opened because the live reading contradicted the board: `ansys-verification` carried VMFL063-R3 as *"freeze pending"* while a `simpleFoam` for VMFL063-R3 `D0` was at `Time = 40626`. Rule 2 requires the registration frozen by sha **before the solver starts**, so the order question was the whole audit.

**ORDER — CLEAN, by 40 minutes 3 seconds.** Freeze commit `175893cd`, author date **2026-09-09T20:46:56Z**, an ancestor of HEAD. Run start **2026-09-09T21:26:59Z**, taken from the run's own files and not from `ps` — `verification/runs/ansys_verification/VMFL063-R3/LAUNCH_RECORD.txt:1`, corroborated by `D0/0/` mtime 21:26:59.740 and `D0/log.blockMesh` 21:27:02. The two aborted launch attempts (21:00:46Z, 21:09:52Z) also postdate the freeze.

**PINS — ALL FOUR BYTE-IDENTICAL TO THE COMMITTED BLOB**, hashed on disk against HEAD: `PREREGISTRATION.md` `8e25317f…`, comparator `grade_vmfl063_r3.py` `2769e2aa…`, generator `gen_domain_mesh.py` `ee11749c…`, launcher `run_vmfl063_r3.sh` `e390f41e…`. `LAUNCH_RECORD.txt` independently records the same launch-time freeze pin. This is rule 2's *"verify the frozen file **is** the file that ran"* satisfied.

**THE DEFECT, and it is a real one.** The launcher is **inside** the registration's §11 frozen grading path (`cases/ansys_verification/VMFL063-R3/PREREGISTRATION.md:540`) and was modified **after** the freeze commit by `cd84979f` at **21:25:50Z — 69 seconds before the run**. As a **pre-first-compute** repair that is legal under rule 2 / charter §2b, and §2b's substantive condition **was** met: the commit body states the condition and how it was checked (an `rc126` chmod defect and a `set -u`/`WM_PROJECT_DIR` unbound abort; the comparator blob asserted unchanged; the run root *"removed and ABSENT"* — §2b's "name the run directory that does not exist"). **But `PREREGISTRATION.md` carries no `AMENDMENT` or `ADDENDUM` heading at all — zero hits.** The disclosure lives **only** in a commit message.

**RULING. The freeze is SOUND and VMFL063-R3 is NOT BLOCKED — the run continues and grades on its frozen gate.** The order holds, the pins hold, and §2b's condition was stated and checked. What failed is **where the disclosure lives**, not whether it exists: rule 6 requires a departure from a frozen file to be disclosed in a **dated amendment appended at the foot of that file**, and a reader of the registration cannot see `cd84979f` from the registration. A commit message is not part of the record a future grader reads. **REMEDY OWED BY `ansys-verification`, and it is legal now**: append a dated §2b amendment to `PREREGISTRATION.md` recording `cd84979f` — the defect, the check, and the absent run root — **appended at the foot, never an edit above**, with the version bump and the `lines whose number changed above this section: 0` assertion. It alters no gate, threshold, cap or label, so rule 2's post-compute lockout does not bar it.

**ONE THING THIS AUDIT CANNOT SETTLE, named rather than waved through.** Whether the two aborted attempts (21:00:46Z, 21:09:52Z) produced any solver iteration is **unknowable from disk**: the run root was removed. The commit asserts abort at `rc126` (comparator exec) and `launcher_rc=1` (bashrc source), i.e. **before** `simpleFoam` — but that is a claim, not an artifact. It is recorded as a claim. Were it false, first compute would predate the launcher repair and the §2b route would close; nothing in the evidence suggests it is false, and nothing available proves it true.

**ALSO CLEARED THIS TURN, so no team waits on me:** heat-transfer's PRD-E1 / K0g / T23G2Rn2-L3 are all **`PENDING`** with no verdict artifact on disk — all three still running, nothing yet auditable (the live rung is `T23G2Rn2`; its predecessor `T23G2Rn` carries a legal `PENDING (infra-confounded)`, not a softened `GATE FAIL`). cfd's **M6 grid-b** has **no committed registration** — `verification/campaign/M6_LE_RESOLVED_GRIDB_PREREGISTRATION.md` is `??` untracked and in no tree — and **no solve has started** (the only solver-family logs are `plot3dToFoam` mesh conversions; zero numeric time directories), so rule 2's post-compute lockout has not engaged and any change there is still a legal pre-freeze amendment. `cad4dadf` did **not** move a registered spec after compute. **The standing condition on cfd, which is rule 2 and not a new demand: grid-b may not launch until its registration is committed** — a pre-registration that exists only as an untracked file proves nothing about what was frozen, because there is no sha to freeze it by.

### §29.1 ADDENDUM — **A SENTENCE IN §29 ABOVE IS MEASURABLY FALSE, AND SO IS THE SENTENCE `check_harness.py` HAS BEEN PRINTING FOR TEN DAYS. FOUR OF THE FIVE "LOST" BLOCKS EXIST AT A REACHABLE SHA. I CAUGHT IT ONLY BY READING, AS A DIFF, THE REPAIR I HAD MYSELF SPECIFIED** (2026-09-10T04:01Z) — **§29's FACT AND CONSEQUENCE STAND; ITS *GROUND* IS CORRECTED; THE REPAIR IS REFUSED AS SPECIFIED AND RE-SPECIFIED**

**The false sentence, quoted from §29 above so it is not softened in the retelling.** Specifying the repair, I wrote that the third state should be: *"bytes absent from the working file **and absent at HEAD** → `lost`: **destroyed before ever being committed, existing at no sha**, unclearable by any act that is not a falsification."* The clause **"existing at no sha"** is false for four of the five rows. **I did not measure it.** I inherited it from `orphan_verdict`'s own in-source rationale (*"ITS BYTES EXIST AT NO SHA AND NEVER WILL"*) and repeated it — which is **§16.7's defect committed a second time, by the same hand, inside the section correcting §16.7**: a claim about a program's population taken from a sibling clause's stated intent rather than from running the test.

**THE MEASUREMENT.** `orphan_verdict` and my §29 both decide "lost" from a **HEAD-only** reading. HEAD cannot distinguish two cases that present identically — absent on disk, absent at HEAD:

- **(X)** the block was **never committed** → bytes at **no sha** → genuinely unclearable.
- **(Y)** the block **was committed and a later commit removed it** → bytes **at a reachable sha** → recoverable, and possibly the very destruction the clause exists to catch.

Searching **history** rather than HEAD — for each row, `git log --format=%H --all -- <target>`, then `git show <sha>:<target>` testing `want in blob`, first hit wins:

| sha256[:12] | target | bytes | found at a sha? |
|---|---|---|---|
| `5c1be22cc224` | `docs/COST_CALIBRATION.md` | 5631 | **YES — `a4795576`** |
| `156201d3c292` | `docs/LAB_STATE.md` | 3177 | **YES — `7811b943`** |
| `db4646292cc7` | `docs/COST_CALIBRATION.md` | 2429 | **YES — `c31ccdf5`** |
| `1c421574fd41` | `docs/COST_CALIBRATION.md` | 3008 | **YES — `c31ccdf5`** |
| `5ae72b9d92e0` | `docs/FAIL_OPEN_GATE_AUDIT.md` | 10923 | **NO — case (X), genuinely at no sha** |

**Four of five are case (Y). Exactly one is the case both the instrument and I described.** And the one that *is* genuinely lost is `5ae72b9d92e0` — the `16:55Z` stamp of §16 — so §16.7 was right about **its own** row and wrong only in predicting it would not gate. §29 was right about the gating and wrong about the ground.

**WHAT STANDS, AND WHAT DOES NOT.** §29's **fact** is untouched and re-verified: the provenance-gated set and the orphan-un-gateable set are identical on sha256, symmetric difference empty, n = 5. §29's **consequence** is untouched: rc=1 with no clearable path, four clearable FAILs riding behind it. §29's **practical unclearability argument** is untouched and was independently grounded — clearing the three `COST_CALIBRATION.md` rows would re-publish rows the lab **deliberately struck** as duplicate ids, and clearing the `LAB_STATE.md` row would re-insert a dated correction into a board since rebuilt wholesale. **What is corrected is the GROUND: those four are not unclearable because their bytes are at no sha. Their bytes are at a sha, and it is named above. They are rows the lab has decided not to restore.** That is a **judgement about the record**, not a **measurement of the repository**, and the distinction is the entire point: an instrument may report the second and must never assert the first without checking.

**`check_harness.py` HAS BEEN PRINTING THE FALSE SENTENCE FOR TEN DAYS**, on these same four rows, in `orphan_verdict`'s `lost` message. That is a **second finding** and it is **not** repaired here — this addendum touches no code. It is recorded so it is not lost, and it is ruled on separately. **Noted and deliberately not folded in**, because a finding folded into another clause's repair is a finding nobody owns.

**THE REPAIR IS REFUSED AS I SPECIFIED IT, AND IS RE-SPECIFIED.** The lane built exactly what I asked for, faithfully and well: **the defect is in my specification, not in its work**, and it was caught by the one check that cannot be delegated — reading the diff myself. Had I accepted the lane's summary instead, an instrument printing a measurably false sentence on four rows would have landed **inside the very commit reporting that this team caught exactly that failure in someone else's instrument.** The corrected specification is **four states, not three**:

1. absent on disk, **PRESENT at HEAD** → **LIVE WORKING-TREE DESTRUCTION → GATE.** Unchanged; this is the signal the single-reader clause drowned and it is worth recovering on its own.
2. absent on disk, absent at HEAD, **bytes AT a reachable sha** → **`recoverable-from-history` → REPORTED, NOT GATED, AND THE MESSAGE MUST NAME THE SHA.** It may not claim "no sha". Whether restoring is *desirable* is a human judgement no instrument can make, so the message states the fact and stops.
3. absent on disk, absent at HEAD, **at NO sha in history** → **`lost`, truly** — and **only here** may the "exists at no sha and never will" sentence be printed. Today that is exactly one row.
4. **no reading available** (reader unsupplied, or target out of repo) → **GATE**, today's message. **A search that cannot run never buys a downgrade**, and where history was not searched the instrument must say *"not searched"* rather than assert an absence.

The history search arrives as a third optional reader on the same three-valued discipline, keeping the function pure; unsupplied, behaviour is exactly the current one, so the six limbs already written keep passing untouched. The selftest must carry a limb asserting that **with no history reader the "no sha" sentence is ABSENT** — that is the limb which stops an instrument asserting an unmeasured fact, and it is the one I read first. Cost is bounded: the search runs only on rows reaching that branch (five today) and stops at the first hit; my probe scanned 370–1400 commits per row in seconds.

**THE FORM THIS IS THE THIRD INSTANCE OF TONIGHT, FROM ONE HAND.** §16.7 predicted an instrument's behaviour without running it. §29 inherited a population claim without measuring it. And this addendum's own first draft was destroyed in the writing by an **unquoted heredoc** that command-substituted its backtick spans — **L-403/L-405, live, while composing the section about unverified assertions** (caught because the shell printed `command not found`; the committed §29/§30/§31 above escaped every span and are intact, verified at 320 surviving backticks). None of the three was caught by an instrument: one by a lane's falsification attempt, one by a supervisor's diff-read, one by a shell error. **The common form is a statement about a program or its data taken from a neighbouring clause's stated intent instead of from the program, and published.** In every case the check was one command, and `git log --format=%H --all -- <target>` took seconds to move four rows out of a category I had already published them into.

---

## §32 — **THE CHECK THAT CANNOT SEE THE FILE YOU ARE ASKING IT ABOUT: `check_filing.py` GRADES 21,302 PATHS OUT OF 89,353 AND ITS SELFTEST CERTIFIES THE RULE AGAINST THE ONE POPULATION THE REAL RUN EXCLUDES. 16 LIVE `R0` VIOLATIONS ARE HIDDEN BY IT, ALL OF THEM IN THE DEMO RENDER PIPELINE**

**Dated 2026-09-10. Ruled and measured by the verification-supervisor personally (`SUPERVISION_CHARTER.md` §3 check-1, an instrument read, and check-3, a big claim defended against its own evidence). HEAD at this write: `faf4ccfd`. Worktree copy of this file verified byte-identical to its HEAD blob before appending (`§10.0`'s hazard, checked rather than assumed). Solver compute: 0 core-min, $0.00.**

**Origin.** Not this team's own sweep. dafoam raised it in the body of `dd432417`, in a paragraph explicitly addressed *"For the lab, not dafoam"*:

> *"`scripts/check_filing.py` enumerates paths in HEAD, so running it on a NEW file before committing returns a zero that means nothing. A planted control — a filename containing a space — went unflagged."*

**It is not taken on report.** A cross-team claim about an instrument is verified at the instrument or it is not believed (`§3` check-3; `CLAUDE.md` rule 9 — a delegate's test is evidence, not the supervisor's read). What follows is this supervisor's own measurement.

### §32.1 The planted control, first, because §1 gates everything after it

An untracked file named `docs/CONTROL PLANT verification.md` — a space in the basename, which is `R0-PORTABLE-NAME`'s own declared target — was created, `scripts/check_filing.py --root /home/ubuntu/Certonomous` was run, and the plant was removed, **all in one shell invocation** so the window in the shared worktree was milliseconds and no peer could observe or commit it.

**The run reported `FAIL: 59 filing violations across 9 rules`. The planted control was not one of them.**

The control is the right shape and it is worth saying why: the run was **not** a clean `PASS` that a reader might dismiss as an empty repository. The instrument was demonstrably alive, emitting 59 findings across nine rules on the same invocation, **and it still could not see the file planted directly in its path**. A zero from a reader not shown able to see a non-zero is not evidence (standing rule 3); here the reader was shown able to see 59 non-zeros and was still blind to this one, which is the stronger result.

### §32.2 The mechanism, cited by line

`scripts/check_filing.py:86-105`, `_tracked()`:

```
    out = subprocess.run(
        ["git", "-c", "core.quotePath=false", "ls-tree", "-r", "HEAD", "--name-only"],
        cwd=root, capture_output=True, text=True,
    )
```

Its docstring is candid — *"Paths in HEAD. HEAD is the referent, never the index"* — and that choice is **correct and must not be reversed**: it is the private-index protocol's own consequence, since files landed by that protocol have no shared-index entry and `git ls-files` / `git diff --cached` misreport them. **The defect is not the choice of HEAD. The defect is that nothing else was ever added beside it.**

Every naming rule iterates that one list. The `--tracked-only` flag (`:438`) is the only untracked-facing control the script has, and it gates `_loose_root_files()` alone — files sitting **directly at the repository root**. A new file one directory deep is outside both readers.

### §32.3 Why this is FAIL-OPEN and not merely OUT-OF-SCOPE, which is the finding

An instrument that never claimed to grade untracked paths would be out of scope and uninteresting. This one claims it twice.

1. **The rule exists and names this exact character class.** `:162-168`, `R0-PORTABLE-NAME`, whose own comment states the rationale: *"A space in a path breaks every unquoted shell loop in this lab."*
2. **The selftest plants a spaced filename and asserts it is caught.** `:353`, verbatim: `("R0-PORTABLE-NAME", "docs/papers/buoyancy/van gilder_2005_ipack.pdf", True)`.
3. **And then the selftest commits it.** `:395-396`, `git add -A` then `git commit -qm "planted"` into the scratch tree, followed at `:398` by `check(root, include_untracked=False)`.

**So the selftest certifies `R0` against the TRACKED population, and the real run's blind spot is the UNTRACKED population.** The 67 selftest assertions are all true and none of them touches the case a user actually brings to this script. **A green selftest is being read as a warrant over a population the selftest never entered.** This is `§28.19`'s form one turn further out: the pass is not weak evidence for the property, it is *zero* evidence for it, while being strong evidence about the tracked path nobody was worried about.

**This team's own charter already names the class, and the wording fits without adjustment** — `VERIFICATION_CHARTER.md` §2c, *"Where this rule does not reach"*, point 1, verbatim:

> *"A check reporting no violations over a population it could not evaluate has not passed; it has not run."*

### §32.4 The population, measured

| | paths | share |
|---|---|---|
| tracked at HEAD — **graded** | **21,302** | **23.8 %** |
| untracked, not ignored — **ungraded and invisible** | **68,051** | 76.2 % |
| candidate total | 89,353 | |

The `PASS` string at `:447` reads *"PASS: every tracked path follows the filing convention."* **The wording is honest and is not the defect.** The defect is that the script's normal use — the use dafoam put it to, and the use its own `NOT_PASSING_REGISTER` workflow invites — is **pre-commit, where the file under examination is by definition untracked**, and in that use the honest word `tracked` is the word that silently excludes the answer.

### §32.5 What the blindness is hiding RIGHT NOW — 16 live violations, and they are in the demo pipeline

`R0`'s own regex (`:75`, `BAD_CHARS = re.compile(r"[^A-Za-z0-9._/-]")`) was applied by this supervisor to the 68,051 untracked paths. **16 violations, every one of them the same character pair `[` and `]`, every one under `verification/runs/actD_paraview/glyphs/`:**

```
verification/runs/actD_paraview/glyphs/_render_cap_polar_field_alpha18_not_converged[0..3].py
verification/runs/actD_paraview/glyphs/_render_cap_section_grid[0..1].py
verification/runs/actD_paraview/glyphs/_render_cap_section_grid_leading_edge[0..1].py
verification/runs/actD_paraview/glyphs/caption_polar_field_alpha18_not_converged[0..3].png
```
*(ranges collapsed for width; 16 distinct paths, in a directory of 61 files.)*

**These are not cosmetic and `R0`'s stated rationale is the reason.** Square brackets are not merely awkward characters — in shell glob syntax `[0]` is a **bracket expression**, so a pattern written to match the literal file `_render_cap_section_grid[0].py` instead matches `_render_cap_section_grid0.py`, and an unquoted loop over `_render_cap_polar_field_alpha18_not_converged*.py` silently sweeps the base file and all four bracketed variants together. The base file `_render_cap_polar_field_alpha18_not_converged.py` **is present in the same directory**, so the collision is live rather than hypothetical.

**And `actD` is demo Act D.** Under the owner's 2026-09-10 directive the lab's priority is cases running and demos shot; a render pipeline whose script filenames break unquoted globs is a hazard against exactly that priority. **This is recorded as a cross-team finding and is NOT repaired here** — the directory is not this team's territory. It is handed over, not touched.

### §32.6 What is REFUSED, and by this team's own precedent

**The obvious repair — make the default run enumerate untracked paths too — is REFUSED and is not this supervisor's to make.**

`D539`, this team's own ruling: *"a checker that refuses a commit is a GATE ON LAB PROCESS, and ADDING a gate is reserved to Sanaa exactly as retiring one is"*, with clause (a), *"NO AGENT MAY FLIP IT … a measured rate that 'looks acceptable' is not an authorisation."* Extending this check's default population from 21,302 paths to 89,353 would make it **FAIL on files it passes today**, which is new bite by any reading, and it would do so at **3.2× the current population**. That is a threshold move dressed as a bug fix, and the fact that this supervisor believes the extension is *correct* is precisely the reasoning `D539` forbids acting on.

**It is also refused on the merits of the number.** 16 of 68,051 is a 0.02 % hit rate; a default-on extension would put the instrument's cost overwhelmingly into run-output trees that no filing rule was written for, and `§17a`'s over-reach — *"which looks like rigour while it is happening"* — is the predictable outcome.

### §32.7 What is OWED, and by whom

Three items, none of which moves a threshold or adds bite to any existing call site. Recorded here as owed; **none is executed in this section.**

1. **An opt-in reader, default OFF.** A flag that adds `git ls-files --others --exclude-standard` to `_tracked()`'s output for that invocation only. Every existing call site behaves byte-identically. Owner: this team, as the script's auditor; the flag adds a capability, not a gate.
2. **A NEGATIVE control in the selftest, and this is the load-bearing one.** The selftest must plant an **uncommitted** violation and assert the default run does **NOT** see it. That converts the blindness from a surprise into a **tested, documented property of the instrument** — the discipline `§1` of this file already demands of every other checker here, and the one thing that would have caused this to be found by the lab rather than by a dafoam lane tripping over it.
3. **The 16 `actD` paths.** Referred to whichever team owns `verification/runs/actD_paraview/`. **Not renamed by this team** — a rename in a directory this team does not own, against a demo pipeline mid-campaign, is exactly the unreviewed action `CLAUDE.md` rule 10's "inspect, never revert" spirit refuses.

### §32.8 What is and is not claimed

**Claimed:** the mechanism, verified at source by line; the planted control, executed by this supervisor rather than relayed, against an instrument shown simultaneously alive on 59 other findings; the population figures, counted; the 16 `R0` violations, enumerated with the script's own regex.

**Not claimed:** that any published verdict in this lab is wrong because of this. No graded row depends on `check_filing.py`; it is a filing convention check, not a gate on a measured number, and **no verdict is withdrawn by this section**. Nor is it claimed that the 16 paths have actually broken anything yet — the collision is demonstrated as *available*, not as *fired*. That distinction is `§28.15`'s lesson and it is applied here to this team's own finding.

**dafoam's report was accurate in every particular this team was able to test.** It is credited as the origin, and this section adds what a report cannot: the control, the population, and the 16.


---

## §33 — **`append_record.py`'s SELFTEST PRINTS `VERDICT: PASS (0 control failure(s))` WITH A PLANTED `assert False` IN IT, UNDER `python3 -O`. THE TOOL THAT MAINTAINS FOUR OF THE LAB'S REGISTERS HAS 10 BARE ASSERTS; THIS TEAM'S OWN STANDARD FOR THE SAME CLASS IS ZERO. AND MY FIRST CONTROL RETURNED A FALSE NEGATIVE, WHICH IS THE MORE TRANSFERABLE HALF**

**Dated 2026-09-10. Measured and ruled by the verification-supervisor personally (`§3` check-1, an instrument read; check-3, a claim defended against its own evidence). HEAD at this write: `aa38f328`. Solver compute: 0 core-min, $0.00.**

**Origin and status.** `V-153` (this team's own board, 2026-09-10) recorded this as *"Pre-existing, outside the brief, being docketed rather than absorbed."* **The docketing had not happened.** The docket's maximum id at `faf4ccfd` was `D592` — closure's Kaandorp row — and no row anywhere mentioned bare asserts or `append_record.py` under `-O`. **A board line saying an item is "being docketed" is not a docket row**, and the gap between the two is exactly the class this file exists to collect: a stated intention read as a completed control. This section and `D594` close it.

### §33.1 The instrument, counted by AST rather than by grep

`grep -c assert` would over- and under-count (docstrings, the word inside a string, a multi-line statement). The count is taken from the parse tree:

| file | `ast.Assert` nodes |
|---|---|
| `scripts/append_record.py` | **10** — lines `2576, 2707, 2708, 3423, 3446, 3466, 3493, 3494, 3506, 3898` |
| `scripts/check_commit_subjects.py` — **this team's own standard for the same hazard** | **0** |

The contrast is the finding, not the count. `check_commit_subjects.py` was deliberately written with **zero** `ast.Assert` nodes for exactly this reason, and the AST was counted at the time rather than assumed. **The same team then left ten in the tool that maintains `docs/DOCKET.md`, `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md` and `docs/COST_CALIBRATION.md`.** All ten sit in selftest/fixture code — `:2707-2708` `"edge fixture: inside id"` / `"edge fixture: outside id"`, `:3466` `"cross-series form vacuous"`, `:3493` `"C-series rows unreadable"`, `:3898` `"sweep fixture: orphan not planted"` — which is precisely where the damage is, because that is the code whose whole job is to fail.

### §33.2 The mutation control, executed both ways, on a scratch copy

The real script was **never modified**. Two copies were taken into the scratchpad; one was mutated at line `2707`, whose original reads:

```
    assert inside in re.findall(ANY_TOOL_ID, edge), "edge fixture: inside id"
```

replaced by `assert False, "PLANTED MUTATION -- this selftest assertion must fail"`. Both copies were run with `PYTHONPATH=/home/ubuntu/Certonomous/scripts` so the sibling `control_kind` import resolves.

| arm | `python3` | `python3 -O` |
|---|---|---|
| **control** (unmutated) | **rc 0** | **rc 0** |
| **mutated** (`assert False` planted) | **rc 1**, `AssertionError: PLANTED MUTATION` | **rc 0** |

**And `-O` does not merely exit quietly — it publishes an affirmative verdict.** The mutated run under `-O` prints, verbatim:

```
VERDICT: PASS   (0 control failure(s))
```

**A selftest containing `assert False` reports zero control failures and a PASS.** That is a fail-open in a measurement instrument's own control machinery, and it is the `L-332` class (`python3 -O` deletes asserts) landing on the tool that writes the lab's registers.

### §33.3 The bound, stated honestly, because it is not currently producing a false PASS

**The instrument's *scored* control machinery is a dict of booleans and is genuinely `-O`-safe** — which is why today's real runs under `python3` and `python3 -O` agree, and why no register row in this lab is under suspicion because of this. **The fail-open is LATENT, not firing.** It becomes live the moment anyone (a) invokes the selftest under `-O`, which `D539`'s own hardening precedent shows this lab does deliberately, and (b) trusts its verdict. Nothing here withdraws a verdict or a register row.

### §33.4 MY FIRST CONTROL RETURNED A FALSE NEGATIVE, AND THIS IS THE HALF WORTH CARRYING

**The first execution of this test said there was no fail-open.** Run from the scratchpad without `PYTHONPATH`, the arms came back:

| arm | `python3` | `python3 -O` |
|---|---|---|
| control | rc 1 | rc 1 |
| mutated | rc 1 | rc 1 |

**Four identical non-zeros. Read carelessly, that is "the mutation is caught in both modes — no fail-open here", and the defect is cleared.** The true cause was `ModuleNotFoundError: No module named 'control_kind'` at `:421` — the copy could not import its sibling, so **neither arm ever reached the assert**, and the instrument was dead before the experiment began.

**The tell was in the CONTROL arm, and the control arm is why this file's `§1` exists.** A valid control must come out *clean*; mine came out rc 1. **An arm that fails identically to its treatment has not agreed with it — it has failed to run**, and the resulting "no difference between the arms" is the exact signature of a real fail-open being masked. This is the `docs/LESSONS.md` stale-bytecode inversion (a clean control that fails while the mutated case passes) reached by a different road: not stale `__pycache__` this time, but an unresolvable import.

**Recorded as this team's own error, not as a near-miss.** Had the first reading been reported, this section would have said the opposite of the truth, would have cited an executed control in support, and `V-153`'s honest referral would have been *retired* on the strength of it. **The generalisable rule, which is not new law but is worth stating where a future sweep will read it: in any two-arm control, the CONTROL arm's verdict is checked FIRST and independently, and a control that does not come out clean voids the comparison rather than contributing to it.** `§1` of this file already gates every sweep on its positive control; this is that discipline failing once, in one hand, inside an hour of `§32`.

### §33.5 What is OWED, and what is REFUSED

**OWED** — replace the ten bare asserts with a `refuse()` / `sys.exit(2)` form that survives `-O`, matching `check_commit_subjects.py`'s existing shape, and add a selftest arm that runs the selftest **under `-O`** and asserts — by exit code, not by assert — that a planted mutation is still caught. **Owner: whoever owns `scripts/append_record.py` as an instrument.** This team raises and measures it; the repair touches a tool four teams append through, and is not landed unilaterally in the same breath as its discovery.

**REFUSED** — this section does not edit `scripts/append_record.py`. Beyond the ownership point, the ten asserts are inside the **control machinery of a live instrument that four teams are appending through today**, and a repair written by the same hand that just published a false negative about it (`§33.4`) is a repair nobody should accept unreviewed. **The defect is disclosed and docketed; it is not quietly fixed by its discoverer in the same commit.**

### §33.6 What is and is not claimed

**Claimed:** the AST counts, taken from the parse tree; the four-arm mutation control, executed by this supervisor with a valid clean control; the verbatim `VERDICT: PASS (0 control failure(s))` string emitted under `-O` with `assert False` in the file; the latency bound; and the false negative in §33.4, reported against this team's own work.

**Not claimed:** that any docket, lesson, numerics or cost-calibration row is wrong. **No register row is impeached and no verdict is withdrawn.** The scored path is `-O`-safe and was checked before that sentence was written.


## §34 — **THE TIER-2 MESH EXEMPTION IS AUTHORISED BY SANAA IN HER OWN WORDS AND ITS ADMISSION TEST IMPLEMENTS A SUBSET OF THE STANDARD IT CITES. EVERY UNIMPLEMENTED LIMB IS ONE THAT COULD ONLY EVER REFUSE. AND MY OWN FIRST READING OF IT WAS WRONG IN THE DIRECTION THAT FLATTERED MY VIGILANCE**

**Dated 2026-09-12. Measured and ruled by the verification-supervisor personally (`§3` check-1, an instrument read as a diff; check-3, a claim defended against its own evidence). HEAD at this write: `a8f419662`. Solver compute: 0 core-min, $0.00.**

**Origin.** `sdk/chief_engineer/mesh_certificate.py` (+153/−3) and `sdk/chief_engineer/certificate.py` (+135/−0) sit **UNCOMMITTED** in the working tree, introducing a two-tier mesh regime in which the finding `skewness errors` leaves `hard_errors` — the list that decides `verdict`, which decides `certificate_admits()` — for any grid carrying a Tier-2 declaration. They were found by a sweep of uncommitted work near this team's territory, not reported by their author.

### §34.0 WHAT I GOT WRONG FIRST, RECORDED BECAUSE IT IS THE MORE TRANSFERABLE HALF

My first reading, written down before it was checked, was that this is **a gate widening reaching for an authority it does not have** — the permission-laundering shape of rule 9. **That reading is false, and it is false in the direction that made me look careful.** The authority exists, it is the owner's own, and it is broader than the code:

> *"7. Immediate applications, in this order: board migration approved and shared-index deletions frozen until it lands; **skewness quarantine reclassified to reporting**; "reported, not gated" adopted as the standard's default mode; …"*
> — Sanaa, verbatim, `etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md:46-48`, read by me at HEAD.

Her sentence is **unscoped** — no Tier-2 qualifier — and `:5-12` of the same capture says a reporting check *"never block[s] a solve from starting, a mesh from being used, or a hand-off from happening."* **The code applies the reclassification ONLY under a valid Tier-2 declaration (`mesh_certificate.py:229`). It is NARROWER than her ruling, not wider.** The suspicion I arrived with was the wrong suspicion, and had I published it without measuring, this team would have accused another of laundering a permission the owner had granted in writing.

### §34.1 THE CODE CITES THE CLAUSE THAT FORBIDS IT AND NOT THE RULING THAT PERMITS IT

`docs/standards/MESH_STANDARD.md` §15 exists **at HEAD**, `[SANAA-RULED]`, v1.10 (`:1575`) / v1.11 (`:1978`); the file is clean against HEAD. The code cites **§15.3(a)** as its authority — at `mesh_certificate.py:94-96`, `:230`, and in `TIER2_REPORTED_NOT_GATED`'s own docstring. **§15.3(a) does not carry it.** What §15.9 item 2 (`:1920-1931`) carries is the opposite, and it still reads this way at HEAD:

> *"**Sanaa's (a) says quality is reported "not gated"** and names skewness in her own parenthesis, **but she did not name this machinery**, and reading her ruling onto a code path she did not mention is the permission laundering rule 9 forbids. **Referred.**"*

So the file cites, as its licence, the clause that expressly **refuses** that licence and refers the point. The real authority is the 20:00Z capture 2½ hours later, which the code gestures at without naming a path. **The referral is inverted rather than honoured:** `mesh_certificate.py:104` quotes §15.9 item 2 by name and applies its warning to the two findings it *declines* to reclassify (`negative-volume cells`, `wrong-oriented face pyramids`), while doing to skewness precisely the thing that item referred.

**This is the `§2db.2` class — prose inside a delivered output is part of the output — applied to the most load-bearing prose there is, a citation to authority.** An auditor who follows this file's own citation is led to the clause that says no.

**A SECOND-ORDER FINDING, AND IT IS THIS TEAM'S OWN:** `docs/charters/VERIFICATION_CHARTER.md:5535` (`§2y.3`) **already records the answer** — *"She has **reclassified the skewness quarantine to REPORTING**"* — with the table row at `:5575` reading *"`§2r.4` obstacle 1 | **DISSOLVED BY HER**"*. **`MESH_STANDARD` §15.9 item 2 still reads "Referred." Two documents of this lab disagree at HEAD about whether an open referral is open**, and the one left stale is the one the code reads. `MESH_STANDARD.md` is not this team's file; the correction is **raised, not made**.

### §34.2 THE FAIL-OPEN: §15.3 IS A CONJUNCTION OF FIVE AND THE CODE IMPLEMENTS PART OF ONE, PLUS ONE

§15.3 (`:1636`) admits a Tier-2 grid *"when **all five** of (0) and (a)–(d) hold."* `tier2_declaration_valid()` (`mesh_certificate.py:132-164`) is handed the declaration and nothing else — sound and faithful to §15.2, and that much is good engineering — but it tests a **subset of (0)**:

| §15.3 limb | implemented | direction if absent |
|---|---|---|
| (0)(1) named body / workshop / family / level / source | yes (5 fields) | — |
| (0)(2) sha-256 of the **distributed file** | field present, **compared to nothing** | **ADMITS** |
| (0)(2) sha-256 of the **converted `polyMesh`** | **absent** | **ADMITS** |
| (0)(2) converter **and its version** | any non-empty string passes | **ADMITS** |
| (0)(3) **other participants ran this same grid** | **absent** | **ADMITS** |
| (0)(4) **case is a validation against that workshop's own data** | **absent** | **ADMITS** |
| (b) registered solver-side mitigations (§15.4) | **absent** | **ADMITS** |
| (c) Roache triple on the same committee family | **absent** | **ADMITS** |
| (d) literal scope string (§15.5) | **yes**, refuses to issue | — |

**Every unimplemented limb is one that could only ever REFUSE a Tier-2 claim. Not one of them could admit a grid the code currently rejects.** That asymmetry is the definition this file exists to collect: the implemented gate is strictly more permissive than the standard it mechanises, and it is more permissive by exactly the limbs nobody wrote.

### §34.3 NINE STRINGS, NONE OF THEM CHECKED AGAINST ANYTHING

The anti-bypass invariant is real and I verified it holds: the tier is derived from the declaration alone, no measured value reaches the decision, `write_certificate` overwrites a `stats`-smuggled tier, and `certificate_admits` re-checks. **It defends against the wrong adversary.** Its own comment — *"nine provenance facts, none of which a bad mesh can produce for itself"* — is true and beside the point: **the LANE can type all nine in a minute.** `prereg_commit` is never verified to be a real commit object, never checked to be an ancestor, never opened to confirm the declaration is in it; `prereg_path` is never read; `distributed_sha256` is never compared against a file, an archive or the mesh. The predicate is *"nine non-empty strings."*

`certificate_admits`'s re-check calls **that same predicate**, so it catches a `tier` field set without a declaration and is blind to a fabricated one — while its comment claims it can *"re-check the claim rather than take the tier field's word for it."* That sentence overstates what the code does, and is the same defect class as the citation in §34.1.

### §34.4 THE PATH IS DORMANT, WHICH IS WHY THIS IS A PRE-USE FINDING AND NOT A WITHDRAWAL

No live caller passes `tier2_declaration` — not `verification/runs/B52_RUNG6_REPLICATE_runs/run_rung6_replicates.py:167,210`, not `verification/runs/R4_runs/run_c3_replicates.py:153,161`, not `sdk/workflows/backstep_case.py:858,862`. The only caller that does is `sdk/tests/test_mesh_tier2_admission.py`, which is **untracked**. **No mesh in this lab is Tier 2 today, and the `"skewness errors"` literal matches its `_HARD_ERRORS` entry exactly (`:54-55` vs `:107`), so the branch is live code that nothing currently enters.** **No verdict is impeached and none is withdrawn.** The repair is owed before first use, not after.

### §34.5 THE ARTIFACT AND THE BYTES THAT MADE IT ARE NOT BOTH AT HEAD — AND I CORRECTED THIS CLAIM DOWNWARD

343 `birth_certificate.json` exist on disk; **8** carry the new `tier` and `reported_not_gated` fields, all reading `tier-1-in-house` with `reported_not_gated: []`. One sits inside the repository at `verification/runs/ansys_verification/VMFL003_M3/L1_1000x25/constant/birth_certificate.json`, written 2026-09-07 — four days after the uncommitted code.

**The claim reaching me was that this is a TRACKED graded artifact unreproducible from HEAD. I checked it myself and it is NOT tracked** — `git rev-parse HEAD:<that path>` is fatal. **The stronger sentence was available, was in my hand, and is false.** What survives is real and weaker: an **untracked** graded artifact, produced by **uncommitted** code, sitting in a run tree — neither the record nor its producer is at HEAD, and the schema of a certificate a third team has already exercised cannot be reconstructed from the repository.

**This is the same disease as tonight's CRM finding, running the other way.** There, a *frozen pre-registration* exists only as a git blob and the disk holds an unsigned draft; here, a *producer* exists only on disk and the repository holds neither it nor its output. **One clause covers both: an artifact and the bytes that produced it must both be at HEAD, or the record is not reproducible.** `scripts/check_freeze_drift.py` is this team's instrument for the first half.

### §34.6 OWNERSHIP IS CONTESTED IN COMMITTED PROSE — REFERRED, NOT ADJUDICATED

`docs/LAB_STATE.md:38551`, `:38375`, `:38281`, `:38184` (cfd) claim the item — *"`sdk/chief_engineer/mesh_certificate.py` reported-not-gated mode, assigned to me"* — and cfd's **newest** such line, `:36808`, adds *"**not started**"*, written ~7.5 h **after** the files' mtimes. cfd's earlier `:38844` says the opposite: *"that is verification's `sdk/`, not cfd's."* This team's `V-88` (`:45374`) says *"obstacle 3 is the live one and **it is cfd's**."* **Both teams have assigned this file to the other in committed prose and neither has claimed writing the code that exists. Authorship: UNVERIFIED.** Cross-family ownership is the chief's to route and Sanaa's to arbitrate; this section does not settle it, and **the finding stands regardless of who wrote it.**

### §34.7 WHAT IS OWED AND WHAT IS REFUSED

**OWED, before any grid is declared Tier 2:** implement or explicitly register as unimplemented each limb in §34.2's table; verify `prereg_commit` is a real commit whose blob at `prereg_path` contains the declaration; compare `distributed_sha256` against the artifact it names. **Owed separately and by their owners:** `MESH_STANDARD` §15.9 item 2 to be closed against the 20:00Z ruling (cfd's file, raised here); the code's citation corrected from §15.3(a) to `etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md:46-48`; the file's masthead at `:3` still reads *"Version 1.2, dated 2026-08-11"*, nine section-versions stale.

**REFUSED:** this section does not edit either `sdk/` file. They are **uncommitted work belonging to a team that has not claimed them**, and rule 10 inspects rather than reverts; a repair written by the discoverer, over another team's unfinished change, in the same breath as the finding, is a repair nobody should accept unreviewed — and §33.5 refused exactly this for the same reason.

### §34.8 WHAT IS AND IS NOT CLAIMED

**Claimed:** Sanaa's 20:00Z sentence, read by me at that path; §15.9 item 2 still reading *"Referred."* at HEAD, read by me; the charter's contrary `§2y.3` at `:5535`; the literal match between `_HARD_ERRORS`'s `"skewness errors"` and `TIER2_REPORTED_NOT_GATED`; the dormancy of the branch; that the birth certificate named in §34.5 is **not** tracked at HEAD.

**Not claimed:** that any mesh has been wrongly admitted — none has, the path is dormant. That the authors acted without authority — **they did not; the authority is the owner's own and the code is narrower than it.** That §15.3(0)'s unimplemented limbs are unimplementable. **No verdict is withdrawn and no certificate is impeached by this section.**
