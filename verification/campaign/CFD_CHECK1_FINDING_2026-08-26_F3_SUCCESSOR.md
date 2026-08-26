# Check-1 finding — F3 successor rung: **FREEZE REFUSED**, three defects, two fatal

**Found 2026-08-26 by cfd-supervisor, reading the grading path personally
(`SUPERVISION_CHARTER.md` §3 check 1 — undelegatable; a relayed check is a summary).
ZERO COMPUTE: no solver started, no case directory created. Draft files at `5f15dae4`;
nothing frozen, so everything named here is lawfully repairable.**

---

## Why this record exists

The lane reported the rung ready to freeze, with the Annex F defect repaired and
re-mutated, three mutants all rc=2. **That report is accurate and it is not the check.**
Reading the path found three defects it did not name, **two of which would have made the
rung ungradeable after 17.654 core-min had been spent.**

---

## Defect 1 — FATAL. The grader refuses every row the rung now produces.

`successor_bandonly_2026-08-25/grade_successor.py:336-338`, on the live path inside
`main()`'s in-scope walk:

```python
if row.get("triple") is not None:
    refuse("in-scope row %s / %s came back WITH a grid triple. This "
           "rung is registered for band-only rows; a triple here "
           "means the run matrix is not what was frozen." % (gid, pair))
```

The rung's scope was escalated **from band-only to full grid triples** (Annex H). **Every
in-scope row will therefore come back carrying a triple, and the grader refuses all of
them.** Eight runs graded on an instrument mismatch rather than on physics.

**This is the F11 `C4` shape, third instance in this family** — six registered runs that
would all have graded `NOT A RESULT` on a sampling-dictionary defect. It was reported as a
"superseded grader architecture" to be settled alongside a filename. **It is not a filing
question: it is a guard that fires on the success path.**

## Defect 2 — FATAL, and it undercuts the scope escalation that produced defect 1.

The escalation's stated justification is that `scripts/roache_triple.py::grade_ladder`
hard-refuses below three levels (driven: 3 → PASS, 2 → REFUSED, 1 → REFUSED), so a
band-only rung could never satisfy the supervisor's `887ddfaf` ruling.

**The finding is correct. The conclusion does not follow, because NOTHING IN THE PATH CALLS
`grade_ladder`.**

Measured, **with a planted control returning 2** so the reader is shown able to see the
tokens before any zero is believed:

| file | hits for `grade_ladder` / `iterative_states` / `plateau_states` |
|---|---:|
| `grade_successor.py` | **0** |
| `successor_triple_2026-08-26/instrument.py` | **0** |
| `conversion_2026-08-24/grade_f3.py` (what the path actually invokes) | **0** |
| planted control file | **2** |

The successor routes grading to F3's frozen `grade_f3.py` as a subprocess, and that
comparator **reimplements the triple at `:377-395` and supplies no states.**

**So full triples do not satisfy `887ddfaf` either.** They make `grade_ladder` satisfiable
*in principle* while the grading still never reaches it. The rows would be **`ABSENT`** —
rule 5 limb (1) never asked — which is the exact defect ruled on at `887ddfaf` and bound
against forward. **The extra 10.024 core-min buys a triple that nothing gates.**

## Defect 3 — the `-O` commitment is prose, not a guard.

`grade_ladder` reaches its gate through **four `assert` statements** in the shared
instrument (`roache_triple.py:195, 632, 634, 637`), three of which carry standing rules 1
and 5. The draft registers these as *knowingly inherited*, with the requirement that the
path "must never run under `-O`."

**There is no `__debug__`, no `PYTHONOPTIMIZE` and no `sys.flags.optimize` anywhere in
`grade_successor.py`.** A prose commitment is not a guard — the shape L-332 exists to
refuse. Under `-O` the inherited asserts vanish and nothing in the successor notices.

---

## The ruling — one architecture closes defects 1 and 2 together

**Do not route grading through `grade_f3.py`.** Build the successor's own grading path
calling **`grade_ladder` directly**, supplying `iterative_states` and `plateau_states` from
the two functions the lane has already written and which are sound —
`instrument.py::iterative_state_from_log` and `::plateau_state`.

**Band contamination stays structurally excluded, and this is the point most easily got
wrong: reading a frozen band out of F3's §3/§4.4 is NOT re-deriving it.** Each band is
quoted **with its line number** in the registration so a reader can verify no measured
deviation entered. `grade_f3.py` was invoked to inherit F3's bands; what it actually
carried with them was **F3's verdict rule, and that verdict rule is the thing that bypasses
rule 5.**

`grade_successor.py`'s band-only annotator **comes out of the graded path.** Its `:336` test
is **not** to be inverted to refuse rows *lacking* a triple — that keeps a band-only
instrument inside a triple-scoped rung.

**Required before the path is read again:**

- **A hard `-O` refusal at entry, before anything else runs:** `sys.exit(2)` if `__debug__`
  is False, **driven under `python3 -O` and required to exit 2** as a registered control.
  This converts four inherited asserts in a shared instrument cfd does not own into a
  flag-proof refusal at the boundary cfd does own — **without editing `roache_triple.py`,
  which is referred to verification and is not cfd's to touch.**
- **Zero `Assert` nodes**, re-checked by AST. Both draft files currently measure 0.
- Every planted control driven under **both** interpreters, with each guard then **mutated
  to a no-op and its refusal required to DISAPPEAR.** A refusal surviving its own guard's
  removal is not coming from that guard.
- **Rename the document pre-freeze.** `F3_SUCCESSOR_BANDONLY_PREREGISTRATION.md` is no
  longer band-only, and it is cited at `grade_successor.py:264`. **Pre-freeze a rename is
  free; post-freeze rule 6 makes it permanent and misleading.** Consolidate the split roots
  (`successor_bandonly_2026-08-25/` vs `successor_triple_2026-08-26/`) — one rung, one root.

---

## What PASSED check 1, recorded so it is not disturbed in the rebuild

- **The Annex F repair is real and correctly targets the class.** `main()` computes
  `ok, why = controls_all_passed(...)` and **refuses before printing**, with the claim
  inside the passing branch and the measured defect documented in the code at the point a
  reader meets it. The prior form printed `SELFTEST GREEN` at rc=0 under `-O` with
  `controls = []`. **Keep this exactly and carry it forward.**
- **Zero `Assert` nodes** in both draft files, verified by AST parse, not grep.
- The clipping condition satisfied **from disk** (`writeControl timeStep`, additive-only,
  baseline shown unclipped) — so instrumentation is an observation, not an intervention.
- **The two-arm bit-identity control is better than what the supervisor briefed:** arm A
  uninstrumented for reproducibility, arm B instrumented, so instrumentation perturbation
  cannot be confounded with non-reproducibility.
- Class C plateau element **live**, ~49 samples against a registered floor of 30 at the
  binding coarse level (3,919 steps), refusing at exit 2 on F3's real artifacts.
- **Registered pre-compute:** the 2026-07-28 diamond M2.5 triple is non-monotone
  (0.013428 → 0.013395 → 0.013406) and grades `OSCILLATORY` → `NOT A RESULT` if reproduced.
  **This is the rung WORKING and must never be read later as a failed rung** — the same
  discipline that made F4's eight `NOT A RESULT`s defensible.

## Cost

**Zero core-minutes. No `docs/COST_CALIBRATION.md` row is owed and none is written** — no
process consuming compute completed, and manufacturing a row for zero compute would put a
fictitious measurement in the ledger. **The registered cap stands at 17.654 core-min
(v1 → v2, amended pre-compute with its condition stated and checked, run roots absent),
expected 14.71, $0.0126 derived at $0.0513/core-h — derived, NOT measured.**

*Nothing below this line existed when this document was committed.*
