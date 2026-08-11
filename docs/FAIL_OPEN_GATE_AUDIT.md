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
2. **No site in this sweep was cleared BY injection.** The 13 out-of-scope
   sites were cleared by tracing whether a published verdict exists and whether
   the handler's writes can reach its status — a static argument, stated
   per site in §5 so it can be disagreed with. The 7 candidates are recorded as
   *not shown to fire*, which is the opposite of a clean bill. Injection was
   used only in the positive direction, to **confirm** the two defects.
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
