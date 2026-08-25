# DRAFT — NOT COMMITTED, NOT APPLIED

Companion to `run_lane_banner_test_PROPOSED.diff`. Written 2026-08-25 by a
closure lane at the closure supervisor's direction. **Nothing was applied,
nothing was committed, no solver ran, zero core-minutes.**

---

## 1. The site, re-derived at HEAD `af2b23b0`

There is exactly **one** `run_lane.py` in closure territory:
`cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/run_lane.py`
(349 lines; disk == HEAD, sha256 first 16 `454e37f426296581`).

The call site is at **line 175**, inside `parse_log()`, and the older board
line number is correct:

```
   168	    diverged = False
   169	    for line in open(os.path.join(case, "log.run"), errors="replace"):
   ...
   175	        if "Floating point exception" in line or "FOAM FATAL" in line:
   176	            diverged = True
   177	    out = dict(iterations=it, diverged=diverged, ended="End" in
```

## 2. The mechanism, and what the call site currently does

Every OpenFOAM log **opens** with the banner

```
trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
```

which contains the substring `Floating point exception`. Line 175 tests for that
substring, so the test matches the header of **every** log, healthy or not, and
`diverged` is set `True` on the first line of every run before any solve output
is read. It is a constant `True`, not a measurement.

**What it was supposed to do:** flag a solve that actually failed. The signature
of a trap that fired is the handler frame the runtime prints in its stack trace,
`Foam::sigFpe::sigHandler`. Note `FOAM_SIGFPE` (the banner's env-var name, upper
case) does not collide with `Foam::sigFpe` — the correct test is unambiguous.

**This is a rule-14 half-application.** The lesson is applied at two of three
call sites in closure territory and not at the third:

| call site | HEAD line | predicate | status |
|---|---|---|---|
| `Kaandorp2020_TBRF/aposteriori/run_lane.py` | 175 | `"Floating point exception" in line or "FOAM FATAL" in line` | **DEFECTIVE** |
| `Kaandorp2020_TBRF/aposteriori/summarise.py` | 29–31 | `"FOAM FATAL" in txt or "Foam::sigFpe" in txt or "End" not in txt[-400:]` | correct, with the hazard documented in a comment |
| `R4_sparta_build/score_aposteriori.py` | 65–70 | `"Foam::sigFpe::sigHandler" in txt` (OR'd with a continuity blow-up test) | correct, with a five-line comment explaining exactly this trap |

`score_aposteriori.py` uses the **narrower** `Foam::sigFpe::sigHandler`;
`summarise.py` uses the broader `Foam::sigFpe`. The diff adopts the broader form,
matching `summarise.py` in the same directory. Harmonising `score_aposteriori.py`
to the same string is a further one-line change in a different case directory and
is **named here, not made**.

## 3. Can this change alter a MEASURED NUMBER? — argued from the code

**It cannot alter any measured number. It can alter one recorded boolean, and
that boolean is gate-facing in the frozen text.** Both halves matter.

**Why no measured number moves.** Traced through the file:

1. `diverged` is assigned only at line 176 and read only at line 177, where it is
   packed into `out`. `grep` over the whole file returns exactly three
   occurrences (168, 176, 177). **No branch in `run_lane.py` reads it** — not
   `main()`, not `score()`, not `g0()`. It steers no control flow, gates no row,
   and skips no solve.
2. Every metric — `U_rms`, `U_mae`, `k_rms`, `b_rms_total`, `unrealisable_frac`,
   `divU_rms_over_gradscale`, `divU_rms_over_UbulkL`, `Umax`,
   `inplane_pct_bulk`, `x_sep`, `x_reatt` — is computed in `score()`
   (lines 201–254) from fields read off disk. `score()` never sees `parse_log`'s
   output; `main()` calls them independently at lines 321–322 and merges the two
   dicts. **The diff does not touch `score()` at all.**
3. `summarise.py`, which renders the cross-lane table, **does not read
   `v["diverged"]`**. It recomputes the state independently at `state()` using
   the already-correct predicate (`:31`). So `table.json`'s `state` column is
   unaffected in either direction.
4. The `converged` / `converged_iteration` fields are computed from the residual
   history at lines 183–196, on a code path the diff leaves untouched.

**Why it is nevertheless gate-facing.** The frozen pre-registration registers
divergence as a verdict trigger, twice:

* `PREREGISTRATION.md`:231 — *"**GATE FAIL** iff `mean(U_rms | ML) ≥` the gate,
  or any ML seed **diverges** or fails to converge (sec. 6)."*
* `PREREGISTRATION.md`:291–294 — *"**Divergence is a result, not an error.** A
  configuration whose residuals rise monotonically, or that ends on a
  floating-point exception, is recorded … and graded **GATE FAIL**."*

So if anything had graded H1 off `results.json`'s `diverged` column, the repair
would flip a registered GATE FAIL trigger from armed to disarmed on six rows —
a **label change after first compute**, which rule 2 forbids.

**Nothing did.** Established from the record, not assumed:

* `RESULTS.md` §A.2 (line 461) is headed *"The grading path: no script is
  registered, so this is a hand grade"*, and docket D492 says the same.
* `RESULTS.md` §A.4 (lines 572–587) diagnoses the artifact by name, counts
  `FOAM FATAL` = **0** and `Foam::sigFpe` = **0** directly in all six
  `CBFS13700` logs, and rules: *"The `diverged` field in `results.json` must not
  be read as a result; the defect is in the flag, not in the solves."*
* The defect's direction is a **false positive**: it can only add a spurious
  GATE FAIL, never remove a real one. The recorded verdicts (H0 GATE FAIL, H1–H3
  NOT A RESULT by the H0 cascade, H5 GATE FAIL ×6) all rest on other registered
  routes and are unaffected.

**Conclusion for the supervisor's read:** the repair changes no number and moves
no verdict, but it **does** change what a registered gate trigger reads on a
closed campaign, in the direction that removes a failure flag. That is precisely
the shape the previous lane declined to land (`RESULTS.md`:869–871: *"it is a
frozen mid-campaign instrument and a lane does not edit one to make a record read
better"*). This lane makes the same call and does not land it.

## 4. Freeze status, and whether this is legal to land

**Not frozen by rule-6 machinery; frozen by the supervisor's own
characterisation of record.** Both facts, plainly:

* `run_lane.py` carries **no version line and no amendment record**. Its
  docstring (lines 2–7) is descriptive only.
* The pre-registration **does not name it** as the grading path and fixes no
  sha for it. D492 states outright that no grading script is registered.
* It is in **no freeze manifest**; `git grep run_lane` over `scripts/`,
  `verification/` and `docs/` returns only `docs/DOCKET.md` and
  `docs/LAB_STATE.md`, both prose.
* It has **already been edited after first compute**, at `074f60da` — the
  `RowBlocked` path, +26 lines, landed after the 2026-08-21 duct rows ran. So a
  post-compute edit to this file has precedent on the record.
* But `RESULTS.md`:869 calls it *"a frozen mid-campaign instrument"*, and that
  sentence is in a committed record with a rule-6 assertion at its foot.

**Legality under rule 2, stated as a recommendation, not a ruling.** The campaign
is closed out (D492) and first compute is long past. Because the repair alters a
registered GATE FAIL trigger's behaviour — even though no grading used it — the
honest reading is that this is **not a plain edit**, and it should land, if at
all, in the shape below:

1. As a **forward-looking repair only**, with the diff's own
   `diverged_test` key making every future `results.json` self-identify which
   instrument produced its `diverged` column.
2. With a **dated addendum at the foot of `RESULTS.md`** — version bump, the
   assertion `lines whose number changed above this section: 0` proved by a
   prefix hash against the HEAD blob — recording that the instrument was
   repaired on 2026-08-25, that §A.4's counts are unchanged, and that **no
   verdict in §1 or §A.5 moves**.
3. **Not re-running anything.** Re-running the lane to regenerate
   `results.json` with the repaired flag would be a re-grade of a closed
   campaign and is not proposed.

If the supervisor reads the registered-trigger point as decisive against a
post-compute instrument change at all, then **leaving line 175 as it is, with
§A.4's disclosure standing, is a defensible outcome** and this diff should be
kept as a record of the analysis rather than landed. That is a legitimate answer
and the lane says so rather than pushing a diff.

## 5. Was any already-committed number produced by the defective code?

**No number. One boolean, on every scored row, and it does not move any verdict.**

* The affected value is `diverged: true` in
  `/home/ubuntu/closure-data/aposteriori/kaandorp/results.json`, on every scored
  row. It is **false in fact**: `FOAM FATAL` = 0 and `Foam::sigFpe` = 0 in all
  six `CBFS13700` logs, counted directly and recorded at `RESULTS.md`:579–581 and
  again at :1009.
* `results.json` is **not tracked in git** (it lives under
  `/home/ubuntu/closure-data/`), so no committed file carries the false flag as a
  figure. The committed records that mention it — `RESULTS.md` §A.4, §A.7 item 3,
  docket D492 — all describe it **as an artifact**, correctly.
* **Nothing needs re-running.** Every graded metric is independent of the flag
  (§3 above), and the record already carries the correct divergence count.

This item is therefore **housekeeping on an instrument**, not a correction to a
result — with the one caveat of §3's closing paragraph, which is why it is
ordered second rather than first in the lane's report.

## 6. What the diff adds beyond the one-line fix

Three things, each cheap to read:

1. **One definition, `line_is_divergence()`**, with the trap documented in the
   comment above it, so a fourth call site has something to import rather than
   re-derive (rule 14).
2. **A planted control (rule 3)**, run at import: the reader is handed a literal
   banner line and a literal handler frame and must classify both correctly, or
   the driver refuses with `sys.exit(2)` before parsing any log. Both fixtures
   are string literals, so it cannot fire on any property of the data and cannot
   fire spuriously. `sys.exit(2)`, not `assert` — an assert vanishes under
   `python -O` (the same principle as the FS5 §31.3 item).
3. **A `diverged_test` key** in `out`, naming the predicate and dating the
   repair, so any `results.json` says for itself which instrument wrote its
   `diverged` column and an old file can never be silently compared with a new
   one.

`python3 -m py_compile` on the patched file: clean. `import sys` is already
present at line 9, so no import change is needed.
