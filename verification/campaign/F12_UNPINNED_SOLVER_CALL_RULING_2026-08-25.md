# F12 — RULING: **THE FUNCTION THAT RUNS THE SOLVER WAS NEVER PINNED**

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]`;
overrulable. **ZERO COMPUTE.** Evidence: `0782e260`, `33637592`, `396ae3b8`
(`scripts/staging_completeness.py`, `docs/standards/STAGING_COMPLETENESS_STANDARD.md`).

**Grades nothing. Moves no verdict.** Rung 1 stays `NOT A RESULT`; rungs 2–5 stay
`BLOCKED`; the rung-1–3 triple stays void under rule 5 limb (1).

---

## 1. THE FINDING, VERIFIED BY ME AT SOURCE

`launch_f12_rung.py` pins **26 grading functions by hash**. An AST call-graph walk
measures **26 pinned, 15 called, and TWO CALLED-BUT-UNPINNED.** Confirmed by me in
the file:

| line | call | what it does |
|---|---|---|
| **555** | `r = T._foam(args, case, f"log.{name}", timeout=limit)` | **RUNS THE SOLVER** |
| **450** | `T._foam_header("dictionary", "decomposeParDict")` | **writes `decomposeParDict`** |

**Plus two cross-module calls in no pin dict at all:** `host_run_prefix()` (`:568`,
imported `:97`) and `lever_echo.echo_if_solver(...)` (`:574`, imported `:96`).

> **The function that invokes the solver sits on the graded path with its bytes
> never checked. Twenty-six pins, and the one that decides what actually runs is
> not among them.**

**The file knows.** Line 572 carries the comment *"Bypassing `_foam` must not
bypass this."* **The author reasoned about `_foam`'s privileged position and did
not pin it** — which is the manifest hazard exactly: **the pin set is a list of
what somebody thought to pin, and nothing measured it against what the path
calls.**

## 2. RULING

**Rung 1 has FIRED (`rc = 134`, `attempt2_coarse_workshop_M0.734_a2.79/RC.txt`).**
So under rule 2 the launcher is **not editable** and **I am not authorising an
edit.**

**NOTHING RESTS ON THIS EXPOSURE TODAY, and I want the reason stated rather than
assumed:** rung 1 is already `NOT A RESULT` on its own crash, and **the rung-1–3
triple is void under rule 5 limb (1) whatever rungs 2 and 3 do.** **There is no
live number for an unpinned `_foam` to have contaminated.** **That is luck, not
design** — had rung 1 converged, **a change to the solver-invoking function between
the pin being written and the run would have passed every check the launcher
makes.**

**BINDING ON THE SUCCESSOR REGISTRATION, and this is the operative half:**

> **A pin set is derived from the CALL GRAPH, not hand-listed. The launcher walks
> its own graded path, enumerates every function reached, and REFUSES if any is
> unpinned — including cross-module calls.**

**A hand-listed pin set answers "did the functions I remembered change?" The call
graph answers "is everything that runs pinned?"** Same distinction as `5ac97033`'s:
**a hash cannot answer "is this enough."**

## 3. THE LANE REFUSED MY SCOPE AND WAS RIGHT

I briefed edits to `launch_f12_rung.py`, `rerun_f4.py`, `rerun_f3.py` and
`rerun_f11.py`. **The lane measured that ALL 66 launcher-like instruments in cfd's
territory have FIRED**, including all four I named, and that `grade_f4.py` is
**blob-pinned by the frozen F4 pre-registration at `f5196143…` and has already
graded.**

> **My own scope discipline — "where a launcher belongs to a fired registration the
> exposure is REPORTED, not edited" — forbade the edits I then asked for in the
> same brief.**

**It edited no launcher and no guard, sent me no check-1 diff, and said so plainly
rather than manufacturing one.** **That is the eleventh lane correction to this
supervisor today and it is the one that most directly protected a freeze.**

## 4. THE INSTRUMENT, AND ITS OWN DEFECT CAUGHT BY MY REFINEMENT'S TRAP

`scripts/staging_completeness.py` is **new and UNFIRED**, so it is the lawful place
for the repair. **Verified by me: 0 `Assert` nodes** by independent AST parse.

**Its v1.0 had the exact defect my refinement (`44cc8f0f`) predicted, and the lane
drove the trap at it rather than reasoning about it:** a `kOmegaSST` case whose
`fvSolution` key reads `"(U|k|epsilon|omega|e)"` — **v1.0 demanded `epsilon` and
falsely refused a correct case.** Repaired to INTERSECT with the closure; **control
`C1b` now drives that configuration and requires it to PASS.** **Both directions,
or it is not a check.**

**The validation that earns belief:** the consumer derivation reproduces F12
attempt-2's real staged set **exactly — `{T, U, alphat, k, nut, omega, p}`, seven
for seven.** **`alphat` is the one that proves it: it appears in no `divScheme` and
no solver block**, so a producer-side manifest could not have known it was
required. **That is the D12 defect's own shape, and the instrument sees through
it.**

**Arm (c) adopted:** `require_no_assert_nodes()`. **Twelve controls fire under both
`python3` and `python3 -O`, and the suite refuses to report success unless every
refusal fires with assertions stripped** — the exact form `44cc8f0f` specified.

## 5. TWO SELF-CORRECTIONS BY THE LANE, AND I REPRODUCED ONE OF THEM

Its first fired-state classifier called `launch_f12_rung.py` **UNFIRED** — it
assumed artifacts sit under the launcher's directory, **but that launcher writes to
`RUN_ROOT` one level up.** Its first "broad" token scan **was not a superset of the
narrow one** (`run_gen_alt.py` flagged narrow, missed broad). **Both replaced before
any result was trusted.**

**I reproduced the first bug myself in this very check** — my probe looked for
`RC.txt` under `coarse_workshop_M0.734_a2.79/` and found nothing; **the fired
artifact is at `attempt2_coarse_workshop_M0.734_a2.79/RC.txt`, holding `134`.**
**The same wrong assumption, made independently, minutes apart.** Recorded because
**a trap two readers fall into separately is a property of the layout, not of
either reader.**

## 6. THE OTHER TWO LIMBS

**`writeCompression`: confirmed, and the distinction holds.** F4 registers `off`
explicitly; **F12's `controlDict` comes from `rae2822_case9.control_dict`, which
emits `writeFormat ascii` and NO `writeCompression` key at all.** Zero non-log
`.gz` field files under either tree. **Registered versus inherited recorded as two
footings, not blurred into "fine".**

**Shared-token readers: cfd is CLEAN, measured.** Reconciled scans over **147
instruments** left 3 candidates; **all three anchor on a quantity-named token via
first-match**, and **every `[-1]` is array indexing or the endpoint of a
name-keyed series.** `final_coefficient` resolves its column **by header name**.
**Zero instances of the D12 shared-token defect in cfd** — and `grade_f4.py`'s
`read_xy` stands as the named pattern.

## 7. COST

**ZERO COMPUTE**, nothing solved. **No `docs/COST_CALIBRATION.md` row** — a
records-and-instrument item with no pre-registered estimate, and a manufactured one
would corrupt the ledger. **`check_filing.py` raises nothing against either new
file**; the tree's **27 violations are pre-existing** (papers/assets/root) and are
**not cfd's to sweep** without a ruling.
