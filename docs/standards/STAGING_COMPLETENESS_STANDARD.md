# Staging completeness standard — cfd

**Version 1.0, 2026-08-25.** Territory: cfd. Binding artifact:
`scripts/staging_completeness.py` (`--selftest`).

> **A HASH CAN ONLY EVER ANSWER "IS THIS THE SAME AS BEFORE". IT CAN NEVER
> ANSWER "IS THIS ENOUGH".**

---

## 1. The failure this standard was paid for

dafoam's **D12 arrest**. Its launcher staged a field directory, hashed whatever
was there, and re-asserted that manifest faithfully before all 23 stages —
**passing every time**. The directory held **four** fields; the solve needed
**eleven**. Every stage died on `cannot find file 0/nut`. **Internally perfect,
externally false.**

A comparator-side md5 of the same directory would not have caught it either:
**both readers agree on the same four files.** That is L-321's shape — fixture
and checker sharing an assumption — applied to a manifest. The manifest and its
verifier share the assumption that *what was staged is what was needed*.

## 2. The rule

**DERIVE THE REQUIRED SET FROM THE CONSUMER, NEVER FROM THE PRODUCER.**

- **Fields**: parse the case's own `controlDict` (application), `fvSolution`
  (matrices assembled), `fvSchemes` (what is transported),
  `turbulenceProperties` (closure) and `thermophysicalProperties` (whether
  energy is solved). **Never a list of what happens to be in `0/`.**
- **Functions**: walk the grading path's **call graph** and assert every
  function it *calls* is pinned. **Not** that every pinned function still hashes
  the same.
- **Files**: enumerate what the comparator actually *reads*.

A guard that iterates the pinned set answers *"is this the same"*. Only a guard
that iterates the **called/required** set answers *"is this enough"*.

### 2.1 The field that proves the rule

For a compressible RAS case, **`alphat` appears in no `divScheme` and no
`fvSolution` solver block.** It is demanded by the compressible wall functions
and is derivable only from *"compressible application + turbulence on"*. A
dictionary-only reader misses it; a producer-side hash never asks. The
instrument's consumer derivation reproduces F12 attempt-2's real staged set
**exactly** — `{T, U, alphat, k, nut, omega, p}`, seven for seven.

## 3. No `assert` may carry a refusal

**Binding cfd ruling, 2026-08-25.** No `assert` anywhere in a cfd instrument may
carry a refusal, a guard, a control or a gate. `python3 -O` strips `assert`, and
a guard was measured vanishing under it and proceeding to act on the shared
tree. **Use `raise` or `sys.exit`.**

Every guard ships a **planted control that makes it FIRE**, and the suite is
**re-executed under `-O`** and refuses to report success unless every control
still fires with assertions stripped. **A completeness check never seen to
refuse is the same defect one level up.**

## 4. Field resolution — registered vs inherited

`writeCompression on` makes fields `U.gz`, so an age guard keyed on `0/U` never
finds its datum.

- **Every cfd age guard resolves a field by the name the case ACTUALLY WRITES** —
  check both `f` and `f.gz`, and **refuse if neither exists**. An unreadable
  datum is never a pass.
- **Where a launcher relies on a default, assert the default.** A *registered*
  setting and an *inherited* one are different safety positions and the record
  must not blur them.

## 5. Anchor on the quantity name, never on a shared token

D12's third finding: a frozen pre-registration specified *"the LAST `average:`
value"* where the solver prints `average:` on **two** lines, so the frozen
reader **read CL instead of CD — 93.9 % off against a 1e-12 tolerance**, a gate
that could never have passed.

**The pattern to copy** is `grade_f4.py`'s `read_xy`, which **refuses any sample
file whose basename does not declare the field order `T_p_rho`** — closing the
`coefficient.dat` positional-read trap **by construction rather than by
assumption**.

---

## 6. cfd's measured exposure, 2026-08-25

Scans reconciled narrow against deliberately over-broad, per the two-scan rule.
Population: **147 instruments** on disk under `verification/runs/` outside the
T-family, `F14-cooling-ladder` and `THERMAL_K0_runs` (141 tracked at HEAD
`6de564d1`, **6 on disk but untracked**, 0 tracked-but-missing).

### 6.1 Completeness of the pin set — **EXPOSED, and unrepairable in place**

`verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/launch_f12_rung.py`
computes `got_h = hashlib.sha256(inspect.getsource(fn).encode()).hexdigest()`
and compares against `GRADING_FN_SHA256`. **It iterates the PINNED set, not the
set the grading path actually CALLS.**

Measured by AST call-graph walk: **26 pinned, 15 called, and two called
functions are NOT pinned** —

| Unpinned but called | Call site | What it does |
|---|---|---|
| `tmr_verification._foam` | `launch_f12_rung.py:555` | **runs the solver** |
| `tmr_verification._foam_header` | `launch_f12_rung.py:450` | **writes `decomposeParDict`** |

Both are on the graded path. Neither has its bytes checked. A 27th function
added to that path would likewise never be checked. Two further cross-module
calls — `lever_echo.echo_if_solver` (`:574`) and `openfoam.host_run_prefix`
(`:568`) — are in **no** pin dict at all.

The same self-consistency holds for the launcher's mesh-substitution assertion
against a pinned sha and its HEAD blob: **both check what exists; neither checks
what is needed.**

> **NOT REPAIRED IN PLACE, deliberately.** This launcher has **FIRED** — rung 1
> at 17:06:57Z, rc = 134; `RC.txt`, `log.rhoSimpleFoam` and `grade.json` all
> present under `verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/`.
> Standing rule 2 closes the grading path at the pre-registration commit and the
> launcher asserts its own bytes against its HEAD blob. **Editing it is a
> supervisor/owner call, not a lane's.** Recorded here as an exposure.
>
> F12 rungs 2–5 are `BLOCKED` on an open crash mechanism and the rung-1–3 triple
> is void under standing rule 5. **Nothing here unblocks them, and rung 2's
> interlock was not read around, invoked or edited.**

### 6.2 `writeCompression` — **NOT EXPOSED**, on two different footings

Verified on disk: **zero non-log `.gz` field files** anywhere under
`verification/runs/F12_runs` or `verification/runs/F4_runs`.

| Case family | Position | Footing |
|---|---|---|
| F4 | `writeCompression off` **registered explicitly** in `controlDict` | a registered setting |
| F12 | **no `writeCompression` entry at all**; `rae2822_case9.control_dict` emits `writeFormat ascii` and nothing more | an **inherited version-dependent default that nothing asserts** |

**These are different safety positions and this record does not blur them.**
F12's immunity is real today and is not guaranteed by anything in the
repository.

`grade_f4.py`'s age guard iterates `REQUIRED_FIELDS = ("T","U","p","rho")` by
**exact name** (`os.path.isfile`) and would not find a `.gz` form.

> **NOT REPAIRED IN PLACE.** `grade_f4.py` is **blob-pinned by the frozen
> `F4_CONVERSION_PREREGISTRATION.md`** at
> `f51961435729558dc768d89e429c1818e8ae1da6` (disk == blob, verified), and it
> **has already graded** — `F4_CONVERSION_GRADE.json`. Editing it would break
> the freeze the grade rests on (standing rules 2 and 6). The repair lives in
> `staging_completeness.resolve_field()` for every future guard.

### 6.3 Shared-token anchoring — **NOT EXPOSED**

Reconciled scan over all 147: **3 candidates** carried both a colon-token regex
and a last-match idiom. All three adjudicated **clean**:

| Instrument | Reader | Why it is safe |
|---|---|---|
| `build_ladder_attempt2.py:493` | `re.search("severely non-orthogonal (> 70 degrees) faces:")` | first match on a fully quantity-qualified token; its `[-1]` uses are numpy geometry indexing |
| `analyse_terminal.py:214` | `re.search("Negative initial temperature T0:")` | quantity-named; `series[-1]` is a time-series endpoint |
| `run_gen_alt.py:51` | `re.search(r"^\s*cells:")`, `coeffs.get("Cd")[-1]` | line-anchored quantity name; the `[-1]` is the endpoint of a **name-keyed** series |

The two `average:` readers in cfd — `analyse_l4_diag.py:123`
(`bounding k, min: … average:`) and `analyse_f13.py:49`
(`Mesh non-orthogonality Max: … average:`) — both **anchor on the quantity
name**, not on the bare shared token. `tmr_verification.final_coefficient`
resolves its column **by header name**, not by position.

**cfd carries zero instances of the D12 shared-token defect.**

### 6.4 Repairability — every cfd launcher has FIRED

All 66 launcher-like instruments in cfd's territory were classified by fired
state and **every one has fired**, including all four named for repair
(`launch_f12_rung.py`, `rerun_f4.py`, `rerun_f3.py`, `rerun_f11.py` — each with
`RC.txt`/`run_rc.txt`, a `runs/` tree or a solver log, and a grade JSON).

**Adding an assertion in place to any of them is therefore forbidden** by
standing rule 2. That is why this standard's binding artifact is a **new,
unfired, shared instrument** rather than 66 edits, and why §6.1 and §6.2 are
recorded as exposures rather than fixed.

> **A note against my own instrument.** The first fired-state classifier
> reported `launch_f12_rung.py` as UNFIRED. It was wrong: it assumed run
> artifacts sit under the launcher's own directory, while that launcher writes
> to `RUN_ROOT` one level up. **A classifier that misses what the broad scan
> flagged is the instrument, not the territory.** Likewise the first "broad"
> token scan was not a superset of the narrow one — `run_gen_alt.py` was flagged
> narrow and missed broad — and was replaced before the result above was
> trusted. Both were caught only by running two scans and reconciling them.

---

## 7. What a new cfd launcher must do

1. `require_staged_complete(case_dir)` **before** the solver starts.
2. `require_pinned_callgraph(...)` if it pins grading-function bytes.
3. `resolve_field(...)` in every age guard — never a bare name.
4. `require_write_compression(...)` if it relies on the setting.
5. Read every quantity **by name**; never by a token two quantities share.
6. **No `assert` carries any of it**, and each guard ships a control that fires
   under `-O`.
