# T8 lane status — independent audit of the committed comparator (2026-08-25)

**Status prose. This file freezes nothing, registers nothing and grades
nothing.** The frozen documents are `T8_PREREGISTRATION.md` and the three
files in its §11 freeze set; nothing here amends them.

Lane: `lab-lane` under `heat-transfer-supervisor`. Audit only — **no solver was
launched, no frozen file was edited, nothing was sent.**

---

## 1. The dispatch brief was stale, and this is the first thing to know

The brief sent to this lane stated that `T8_PREREGISTRATION.md` was **written
and NOT committed**, and that `analyse_t8.py` **might be truncated** by the
session-limit kill at ~20:45Z. **Both premises are false at HEAD.**

A sibling lane already landed the work in **one commit**, exactly as the brief
required:

- `96c2fe3c` — *"T8: the pre-registration and its comparator committed in ONE
  commit, so section 11's freeze assertion is TRUE at the moment it binds"* —
  4 files, 2,832 insertions, **verified an ancestor of HEAD**.
- `bbde682c` — the sibling lane's own report,
  `docs/campaigns/T-family/T8_LANE_REPORT_COMPARATOR.md`.

Every T8 path on disk is **byte-identical to its blob at HEAD**, and identical
to its blob at `96c2fe3c`. There was nothing to land and nothing to repair.
The lane therefore did the one thing still worth doing: **audit the instrument
independently, by mutation rather than by reading.**

**Consequence for the supervisor's non-delegable §3 check 1:** the comparator
is already committed and already frozen. The diff read is therefore a read of
`96c2fe3c`, **after** the fact, not before. That ordering cannot now be
repaired, only recorded — and it is recorded here.

---

## 2. `analyse_t8.py` is COMPLETE, not truncated

| test | result |
|---|---|
| `python3 -m py_compile` | rc = 0 |
| file ends in a complete statement | yes — `if __name__ == "__main__": sys.exit(main())` |
| `main()` defined and reachable | yes, line 1774; dispatches `--selftest`, `--check-freeze`, else `grade()` |
| every referenced function defined | yes — 38 defs, no unresolved reference |
| length | 1,793 lines / 84,817 bytes |

`build_t8.py` (484 lines) and `run_one_t8.sh` (78 lines) likewise compile /
parse clean.

---

## 3. The three standing instruments, by line number

| standing rule | instrument | lines |
|---|---|---|
| **3** planted zero | `PLANT = 1.234e-03`, `PLANT_TOL = 1e-9` | 197–198 |
| | `write_internal` / `_substitute_internal` — writes a real OpenFOAM field to disk | 287–317 |
| | `plant_into_T`, `plant_into_Uz` — plant into the **field on disk**, into a temp copy | 862–903 |
| | `_read_centrelines` — read-back through the **full shipped station reader** | 905–923 |
| | `check_planted_zero` — 6 arms (2 registered, 4 supplementary) | 925–999 |
| | the refusal, `exit 2` | 1207–1216 (`refuse` at 213) |
| **4** completion + age guard | `check_completion`, all clauses | 384–504 |
| | the **age guard** proper | 485–497 |
| | the arming guard (`0/` or any time dir already present ⇒ REFUSE) | `run_one_t8.sh` 38–41 |
| | `0/T` touched **last** at arming, so it dates the run | `run_one_t8.sh` 46–52 |
| **5** Roache triple gating | `gci_triple` — EXACT / OSCILLATORY / DIVERGENT / STAGNANT / CONVERGING | 800–843 |
| | `band_verdict` — computed first and unconditionally | 845–858 |
| | `grade_row` — criteria (1), (2), (3) in the fixed order | 1009–1061 |
| | the one-way gate | 1057–1060 |
| **1** verdict vocabulary | `VERDICT_PASS` / `VERDICT_FAIL` / `VERDICT_NAR` only | 204–206 |

The plant is into the **field on disk**, not into a spec or a dict, and the
read-back goes through `read_mesh` → `resolve_planes` →
`read_plane_quantities` → `read_stations` — the same chain that produces the
graded number. **The K0d defect class is absent here.**

`gci_triple` quotes a GCI only on `CONVERGING`, which requires
`ratio = e32/e21 > 0`, i.e. the three values are **monotone**. Rule 5's "never
quote a GCI when the three values are not monotone" is therefore satisfied
structurally, not by care.

---

## 4. Green checks, as numbers

| check | result |
|---|---|
| `analyse_t8.py --selftest` | **52 ok, 0 FAILED**, rc = 0 |
| `scripts/check_grader_self_blindness.py analyse_t8.py` | rc = 0 — *"clean on both probes (NOT a proof of correctness)"* |
| `analyse_t8.py --check-freeze` | rc = 0 — all four freeze-set files **FROZEN** |

The selftest carries genuine negative arms: the completion checker is shown
**firing** on rc ≠ 0, ranks ≠ 1, missing `End` line, `ExecutionTime` count ≠
`endTime`, last time ≠ `endTime`, and the **age guard**, alongside a positive
case that must pass.

---

## 5. MUTATION TEST — the part that is not just re-reading a green light

A green selftest is the K0d trap. Six mutations were applied to **scratch
copies** of `analyse_t8.py` (never the tracked file) and the selftest re-run.
Baseline is 52 checks; a scratch copy loses exactly one — the canon
differential against `scripts/roache_triple.py`, which needs the repo path —
so **51 is the comparable denominator for every mutated run.**

| # | mutation | selftest response | verdict |
|---|---|---|---|
| 1 | age guard `<= t0` → `<= -1.0` (guard never fires) | rc = 2, **1 FAILED** | **CAUGHT** |
| 2 | `ExecutionTime` count check → `True` | rc = 2, **1 FAILED** | **CAUGHT** |
| 3 | `End` line check → `True` | rc = 2, **1 FAILED** | **CAUGHT** |
| 4 | `if ratio < 0.0:` → `if False:` (OSCILLATORY undetectable) | rc = 2, **2 FAILED** | **CAUGHT** |
| 5 | one-way-gate `assert` → `assert True` | rc = 0, 51 ok, 0 FAILED | **SURVIVED — benign** |
| 6 | centreline extrapolation `(9·T[i1] − T[i2])/8` → `(7·T[i1] − T[i2])/6` | rc = 0, 51 ok, 0 FAILED | **SURVIVED — a real gap** |

### 5.1 Mutation 5 is benign, and saying otherwise would be inflation

The `assert` at 1057 is redundant, not load-bearing. The one-way property is
covered **behaviourally and exhaustively** at lines 1659–1668, which sweeps
every reachable (convergence-state × triple) combination and requires the
verdict to be the band verdict or `NOT A RESULT`. Removing the assertion
cannot change grading. One true caveat: assertions vanish under `python3 -O`,
so the assertion must never be the only guarantee — and it is not.

### 5.2 Mutation 6 is a REAL COVERAGE GAP, and it lands on the rule-3 channel

The production centreline extrapolation lives at **lines 685–686**:

```
Tc = (9.0 * T[i1] - T[i2]) / 8.0
wc = (9.0 * Uz[i1] - Uz[i2]) / 8.0
```

Selftest section (v), lines 1693–1705, verifies the identity by **re-writing
the arithmetic inline** — `(9.0 * f1 - f2) / 8.0` at line 1698 — instead of
calling `read_plane_quantities`. The shipped formula can therefore be changed
to a different one and **every one of the 51 checks still passes.**

This compounds with a second, independently confirmed fact:

- **`check_planted_zero` has exactly one call site — line 1209, inside
  `grade()` — and is NEVER invoked by `--selftest`.**
- `read_mesh`, `resolve_planes`, `read_plane_quantities` and `read_stations`
  are likewise **never called from `selftest()`**; they need a real case with
  `Cx/Cy/Cz/V` on disk.

**Therefore: the standing-rule-3 instrument has never been shown able to fire.**
It is well written — this audit read it and found the correct channel — but
"read and found correct" is precisely the standard the lab does not accept
elsewhere. Its first execution will be on the real fine case at grade time,
and its refusal path is untested.

**This is not a reason to withhold the fire order.** The instrument's first
live run *is* its test, it refuses rather than degrades, and its expected
responses (`P`, `9P/8`, `0`) are exact arithmetic identities that cannot be
satisfied by accident. It **is** a reason to require that the section-9 block
of the grading output be read line by line before any T8 number is believed,
and to treat a green section 9 as the first evidence that the reader works —
not as a formality.

**Cheapest full repair, if the supervisor wants it before firing:** build one
tiny synthetic case on disk in `selftest()` (a handful of cells with `Cx/Cy/Cz/V`
and a quadratic-in-r `T`), then call `check_planted_zero` on it and require all
six arms to pass, plus one negative arm where the extrapolation is deliberately
mis-weighted and the control must FIRE. That closes gap 5.2 and gap 6 together.
**It is a change to a FROZEN file** and so is governed by rule 6 / rule 2 — a
dated amendment, or the §2d.1 four-condition repair exception, at the
supervisor's call. **This lane did not make it.**

---

## 6. §11 is TRUE, verified independently of the script that says so

| freeze-set path | on disk | blob == HEAD | blob == `96c2fe3c` |
|---|---|---|---|
| `docs/campaigns/T-family/T8_PREREGISTRATION.md` | yes | yes | yes |
| `verification/runs/T-family/T8_runs/build_t8.py` | yes | yes | yes |
| `verification/runs/T-family/T8_runs/analyse_t8.py` | yes | yes | yes |
| `verification/runs/T-family/T8_runs/run_one_t8.sh` | yes | yes | yes |

The registered grading path **is** the file that would run. §11's superseded-draft
cross-reference was also checked and is true: `T8_PREREGISTRATION_DRAFT.md` on
disk hashes to `2adcf2ec…`, the blob §11 names, unedited.

**One weakness in the freeze instrument, named rather than waved past.**
`check_freeze_set` (lines 224–256) hashes each file against **`HEAD:`**, not
against the pre-registration commit. Rule 2's third clause fixes the grading
path *at the pre-registration commit*. Today the two coincide — verified in the
table above — so `--check-freeze` is not lying. But a later commit that
modified `analyse_t8.py` would move `HEAD` with it and the check would still
print `FROZEN`. The instrument detects an **uncommitted** edit, not a
**committed** one. Registering the pinned sha `96c2fe3c` instead of `HEAD`
would close it.

## 6.1 Cost, gate, threshold, cap, label — all four present (rule 12)

- **Cost, in core-minutes:** §8 registers **335.3 core-min predicted**
  (c 7.13 / m 42.81 / f 285.40), from a stated rate of 1.196e5 cell·steps/(core·s)
  derived from `K2bU3_L025`. **$0.287 at $0.0513/core-h, labelled derived, not
  measured.**
- **Registered misprediction risk:** §8 names, before the run, that the rate is
  borrowed from a **transient PIMPLE** case while T8 is **steady SIMPLE**, and
  declines to predict the direction of the error. This is the honest form.
- **Cap:** **15 / 80 / 500 core-min per level, 595 total**, enforced as
  `timeout = cap × 60 ÷ ranks` = 900 / 4,800 / 30,000 s at 1 rank — and the
  document says explicitly that a wall-clock timeout is not a core-minute cap
  and only coincides at `ranks = 1`.
- **Threshold:** §4, **±0.05 absolute** on each exponent —
  `n_w [−0.383333, −0.283333]`, `n_T [−1.716667, −1.616667]`,
  `n_Q [+1.616667, +1.716667]` — with band utilisation reported either way.
- **Label:** a level killed by its cap is **`PENDING`**, right-censored,
  **never `GATE FAIL`**. Vocabulary is clean throughout.
- **Calibration:** §8 pre-commits the `docs/COST_CALIBRATION.md` row at completion.

---

## 7. Two items for a supervisor ruling, neither of them blocking

**(a) The plateau conjunct.** Rule 5 criterion (1) is *"not iteratively
converged **or not plateaued**"*. `grade_row` gates on iterative convergence
only (line 1035); the plateau conjunct is **declared** to have no separately
registered content in T8, printed in the grading output as such (lines
1302–1309), and asserted in selftest section (ix). That is disclosure, not a
silent skip — but **the lab canon conflicts with it**: `analyse_e4a.py:346`
treats converged/plateaued as one test (agreeing with T8), while
`analyse_t1b_L4.py:225` treats the plateau as a **separate spatial test**
(disagreeing). T8's own §7 registered no separate criterion, so the comparator
is faithful to its frozen document. The conflict is a **canon-level question**
for the verification team, not a T8 defect.

**(b) `epsilon`, not `omega`.** `FIELDS_REQUIRED` (line 149) is
`("T","U","p_rgh","alphat","nut","k","epsilon")`. Rule 4's thermal-family list
names `omega`. **This is disclosed, not silent** — §7 lines 248–249 state
*"`epsilon`, not `omega`, because the registered closure is `kEpsilon`"*, and
`build_t8.py:337` sets `RASModel kEpsilon`. Requiring `omega` on a k-ε run
would demand a field that cannot exist. Recorded so no later auditor reads it
as a deviation.

---

## 8. Verdict

**PENDING** — the T8 comparator is frozen, complete, selftested at 52 ok / 0
FAILED, clean on both self-blindness probes, and its §11 freeze assertion is
true. **No level has been fired**, so there is no gate verdict to give.

**Cost of this lane: 0 core-minutes of solver compute.** No solver ran. The
mutation harness and selftests are sub-minute Python on the login box and are
not charged as campaign compute.

**What this lane could not verify:**

1. That `check_planted_zero` **fires** — it has no test, by construction (§5.2).
2. That the shipped centreline extrapolation is the registered one — the
   selftest re-derives it rather than calling it (§5.2, mutation 6).
3. Anything about T8 physics. No solver ran.
4. That the supervisor's §3 check-1 diff read happened before `96c2fe3c`. It
   is not this lane's check to make and the ordering is now historical (§1).
