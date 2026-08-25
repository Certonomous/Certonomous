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

---

# APPENDIX — the supervisor's pre-compute rulings, executed (2026-08-25)

Appended after the audit above. **Rulings 1 and 2 are DISCHARGED; rulings 3 and
4 required no action from this lane.** Landed as commit
**`78ee37ae`** — *"T8 PRE-COMPUTE AMENDMENT A1…"*.

## A. The pre-compute condition, checked before anything was touched

`CLAUDE.md` rule 2 requires the condition be **stated and checked**, naming the
run directory that does not exist. Checked by direct `stat` of each path:

- `verification/runs/T-family/T8_runs/T8_MTT_c` — **DOES NOT EXIST**
- `verification/runs/T-family/T8_runs/T8_MTT_m` — **DOES NOT EXIST**
- `verification/runs/T-family/T8_runs/T8_MTT_f` — **DOES NOT EXIST**

The run tree holds **only** the three freeze-set scripts. A repository-wide
search for `STATUS.T8*`, any `T8_MTT_*` directory and any `log.solve` under a
T8 path returned nothing; `docs/COST_CALIBRATION.md` has **no T8 row**. **Zero
core-minutes.** The window was open, and it was **re-checked after the commit
and is still open** — no case directory exists now either.

## B. Rulings 1 and 2 — what was built

Both repairs live in `analyse_t8.py`, **in the selftest and its fixtures only.**

| new artifact | line | role |
|---|---:|---|
| `write_foam_scalar` / `write_foam_vector` | 1473 / 1483 | write real OpenFOAM fields at full double precision |
| `make_synthetic_field_case` | 1493 | a **real** `endTime` dir on disk: `Cx Cy Cz V T U`, `T` and `U_z` exactly quadratic in `r` |
| `mis_weighted_reader` | 1538 | negative fixture — `(7f₁ − f₂)/6` |
| `wrong_column_pair_reader` | 1558 | negative fixture — right weights, columns `idx[1],idx[2]` |
| selftest **(v)** extension | 1834 | **CALLS** `read_mesh`, `resolve_planes`, `read_plane_quantities`, `read_stations` |
| selftest **(x)** | 1952 | **CALLS `check_planted_zero`** on a real case; 6 arms pass, 2 negative arms fire |

The fixture is exactly quadratic in `r` on purpose: cell centres at
`r_j = (j+½)dr` put the two axis-adjacent columns at `r₂ = 3r₁` **exactly**, so
`(9f₁ − f₂)/8` returns the axis value **analytically**. Every expected response
is an exact identity — **no tolerance was fitted to make a fixture pass.**

**The grading path did not move.** Diff vs the previous blob: **+216 / −7 in
three hunks, all at old line 1449 or below.** Lines 1–1451 of the old blob are
**byte-identical** in the new one (verified by md5 of the truncated files, not
by eye). Every instrument line number from §3 of this document **still holds**:
extrapolation **685–686**, `check_completion` 384 / age guard 478–497,
`gci_triple` 800, `band_verdict` 845, `check_planted_zero` 925, `grade_row`
1009. **No gate, threshold, cap or label was altered.**

## C. The mutation suite, re-run — the gap is CLOSED

Same method as §5 above: mutate a scratch copy, re-run `--selftest`. Scratch
baseline is **68 ok** (a copy outside the repo loses the canon differential).

| mutation | before repair | after repair |
|---|---|---|
| `Tc` extrapolation → `(7f₁ − f₂)/6` | **SURVIVED**, 0 FAILED | **CAUGHT** — rc 2, **3 FAILED** |
| `wc` extrapolation → `(7f₁ − f₂)/6` | not testable | **CAUGHT** — rc 2, **3 FAILED** |
| column pair → `idx[1], idx[2]` | not testable | **CAUGHT** — rc 2, **7 FAILED** |
| planted-zero verdict → `good = True` | not testable | **CAUGHT** — rc 2, **3 FAILED** |
| age guard disabled | CAUGHT | **CAUGHT** — rc 2, 1 FAILED |
| `OSCILLATORY` branch disabled | CAUGHT | **CAUGHT** — rc 2, 2 FAILED |

The fourth row matters as much as the first: forcing the control's **own
verdict** to `True` is now caught, so `check_planted_zero` is tested on its
refusal, not merely on its arithmetic.

## D. THE FINDING — §9's registered arm is not sufficient on its own

Produced by the new negative arm, and it is about **the pre-registration**, not
the code.

§9 registers **one** arm: plant into **both** axis-adjacent columns, expect a
shift of exactly `PLANT`, because `(9P − P)/8 = P`. **That arm cannot see a
`(7f₁ − f₂)/6` mis-weighting** — because `(7P − P)/6 = P` **as well.**

Measured, not argued. Under that mutation **both registered arms PASS**, and it
is the comparator's **supplementary arm (a)** — innermost column only, expect
exactly `9P/8` — that **FAILS** and forces the refusal. Selftest (x) asserts
this split explicitly, so the claim is checked on every run rather than
believed once.

**The supplementary arms are load-bearing, not decoration.** §9's registered
text is not weakened, widened or reinterpreted — it binds exactly as written,
and the supplementary arms were already in the frozen comparator. What is new
is the **disclosure**, so that no future rung copies §9's wording believing one
arm suffices.

## E. Rulings 3 and 4 — no action, recorded

- **Ruling 3** (`epsilon` not `omega`): registered form **stands**. No change
  made. The general wording point was referred upward by the supervisor.
- **Ruling 4** (plateau conjunct): **not decided locally**, does not block T8,
  referred to the chief for the verification team. `grade_row` is unchanged.

## F. Re-freeze, and the numbers at the amending commit

| check | result |
|---|---|
| `--check-freeze` | **rc = 0, FROZEN** — all four blobs match `HEAD` |
| `--selftest` | **69 ok, 0 FAILED**, rc = 0 (was 52 ok) |
| `check_grader_self_blindness.py` | **rc = 0**, clean on both probes |

| freeze-set path | blob at `78ee37ae` |
|---|---|
| `T8_PREREGISTRATION.md` | `93a9f1fe8189` — amended, v1.0 → v1.1 |
| `build_t8.py` | `376a41da268c` — unchanged |
| `analyse_t8.py` | **`f04f9a674e03`** — was `d82c98ae2caf` |
| `run_one_t8.sh` | `70a37aa634d6` — unchanged |

The rule-6 assertion in the amendment — **`lines whose number changed above
this section: 0`** — was **verified, not asserted**: prereg lines 1–477 are
byte-identical to the pre-amendment blob.

## G. The freeze instrument's own limitation, now on the record

`check_freeze_set` (224–256) hashes against **`HEAD:`**, not a pinned sha, so
it detects an **uncommitted** edit to the grading path but **not a committed
one**. It is **not lying today** — the blobs coincide, verified. Recorded in
amendment §A1.5 as a named limitation. **Not closed by this lane**: pinning the
sha would be a change to the grading path's own guard, and that is the
supervisor's call.

## H. Verdict and what remains

**PENDING.** The comparator is re-frozen, its two blind spots are closed, and
every instrument is now demonstrably able to fire. **No level has been fired.**

**Cost: 0 core-minutes of solver compute.** No solver ran at any point.

**STOPPED AS INSTRUCTED.** The supervisor reads
`verification/runs/T-family/T8_runs/analyse_t8.py` and `build_t8.py` as diffs
personally before the fire order. **This time the ordering is correct: the
repair is committed and frozen, and no compute has started.**

**What this lane still could not verify:** anything about T8 physics — no
solver ran; and `build_t8.py` is **unchanged and unaudited by mutation** — this
lane audited the comparator, not the case builder.

---

# APPENDIX 2 — T8 FIRED, AND IT CANNOT GRADE (2026-08-25, 21:32–21:45Z)

**Read §2.1 first. It invalidates the grading of all three levels, it is a
defect in the FROZEN pre-registration rather than in any code, and my own
amendment-A1 fixtures could never have caught it.**

## 1. The fire, as ordered

**Step 1 — pre-compute condition re-verified 21:32:49Z.** `T8_MTT_c`,
`T8_MTT_m`, `T8_MTT_f` all **ABSENT**; run tree held only the three freeze-set
scripts; no `STATUS.T8*`, no `log.solve` under any T8 path.

**Step 2 — freeze re-verified via `git cat-file -p HEAD:<path>`** (not
`git diff`): `analyse_t8.py` = `f04f9a674e03773b34ac0b511611414c33204773`,
`build_t8.py` = `376a41da268c7a97e59cb284f77ec54027652992` — **both match the
supervisor's shas exactly**; `run_one_t8.sh` = `70a37aa634d6…`.

**Mesh.** `build_t8.py` writes `0.orig/` only; `blockMesh` + `checkMesh` were
run per level. **`Mesh OK` on all three**, cells **6400 / 25600 / 102400**
exactly as registered, ratios exactly **4.0000 = r^dim**.

*(A reader bug of mine here: I first grepped lowercase `cells:` against
`nCells:` in the blockMesh log and got an empty string, which I nearly read as
a mismatch. Re-read from `checkMesh` and required three **distinct non-zero**
values before believing any of them.)*

**Step 3–4 — launched 21:34:54Z**, `setsid nohup`, serial, `ranks = 1`.

| level | solver pid | `timeout` | registered cap | case |
|---|---:|---:|---:|---|
| c | 2635183 | **900 s** | 15 core-min | `…/T8_runs/T8_MTT_c` |
| m | 2635190 | **4800 s** | 80 core-min | `…/T8_runs/T8_MTT_m` |
| f | 2635179 | **30000 s** | 500 core-min | `…/T8_runs/T8_MTT_f` |

Registered total **335.3 core-min** point estimate against a **595 core-min**
cap. `timeout = cap × 60 ÷ ranks` in every case, as registered.

**Step 5 — contention at launch.** loadavg **5.80 / 4.87 / 4.36** on 16 cores,
27 GB of 30 GB available. Foreign solvers, untouched: **pids 2203927
(`T1_runs/R_10k_x`), 2203944 (`R_100k_x`), 2203947 (`R_300k_x`)** — the T1b
arms, 4 h 56 m elapsed at launch — plus a dafoam D10F docker probe. Load rose
to **10.65** with T8's three added.

*(My first process census used `pgrep -x buoyantBoussinesqSimpleFoam`, which
**silently matched nothing** — the name exceeds 15 characters. My second
classified by `cwd` and labelled **my own solvers "foreign"**, because the
solver runs from the launcher directory and takes the case as a `-case`
argument. Both corrected; the table above classifies by the `-case` argument.)*

## 2. Outcomes

| level | result |
|---|---|
| **c** | `rc=0`, reached `endTime` 8000/8000, wall 229 s, **3.817 core-min** |
| **m** | **`rc=136` — CRASHED (SIGFPE)** at `Time = 1086` of 12000, wall 150 s |
| **f** | still running at last check (823 of 20000) |

### 2.1 THE FINDING — §12 S3's extrapolation precondition is FALSE on the mesh §5 registers

`resolve_planes` enforces, as a refusal condition, that the two axis-adjacent
cell-centre radii satisfy **`r₂ = 3·r₁`** — the precondition for §12 S3's
registered axis extrapolation `(9f₁ − f₂)/8`.

**Measured on the real, completed level-c mesh** (the frozen instrument, run on
the live case at its `endTime`, geometry written by OpenFOAM itself):

- first four cell-centre radii in plane 0: `0.016650804, 0.038851875,
  0.063273054, 0.088011391`
- **`r₂/r₁ = 2.333333333333` = 7/3, not 3.**
- `resolve_planes` → **REFUSAL**: *"the section 12 S3 centreline extrapolation
  is not applicable"*.

**Cause, and it is not a bug in anyone's code.** OpenFOAM's cell centre is the
**volume centroid**. On a wedge, the axis-adjacent cell is a collapsed
triangular prism whose centroid sits at `(2/3)dr`, and the next cell — an
annular sector over `[dr, 2dr]` — has its centroid at
`(2/3)(r_b³−r_a³)/(r_b²−r_a²) = (14/9)dr`. The ratio is
`(14/9)/(2/3) = 7/3` **exactly**, and the predicted radii `0.016667` and
`0.038889` match the measured `0.016651` and `0.038852` to 0.1 % (the residual
is the flat-sided wedge correction, which cancels in the ratio).

`r₂ = 3r₁` is what you get from cell centres at **arithmetic mid-radius**. That
is not what a wedge mesh produces. **The pre-registration registered a formula
whose precondition its own registered mesh cannot satisfy.**

For `r₂ = k·r₁` the quadratic axis extrapolation is `(k²f₁ − f₂)/(k² − 1)`:
`k = 3` gives the registered `(9f₁ − f₂)/8`; **`k = 7/3` gives
`(49f₁ − 9f₂)/40`.**

**Consequence: `analyse_t8.py` will REFUSE (exit 2) on all three levels.** T8
**cannot grade as frozen.** The direction is safe — it refuses rather than
returning a wrong number — but no T8 verdict is reachable under this document.

**Nothing was changed to accommodate this.** §12 S3 is frozen and **compute has
started**, so rule 2 closes it: altering the extrapolation now would change the
grading instrument after first compute. That is the supervisor's and Sanaa's
call, not this lane's.

### 2.2 My own amendment-A1 fixtures shared the false assumption

This is the part I most need on the record. `make_synthetic_field_case` places
cell centres at **`r_j = (j+½)dr`** — arithmetic mid-radius — which makes
`r₂ = 3r₁` **true by construction**. The fixture and the instrument agreed
because **they share one wrong assumption**, which is the L-321 shape the
comparator's own docstrings warn about.

So the 69-check selftest, the two negative arms and the closed mutation gap are
all real **and none of them could ever have caught this**. A fixture that
reproduces the instrument's premise tests the implementation, not the premise.
**The defect was found by running the frozen instrument against a real mesh —
which is the one thing no selftest had done.**

### 2.3 Level m crashed — a finding, not a triage verdict

`rc=136` = 128+8 = **SIGFPE**. The stack terminates in
`PBiCGStab::scalarSolve` called from `libincompressibleTurbulenceModels` — a
floating-point exception in a **turbulence scalar equation** (`k` or
`epsilon`). Crashed at `Time = 1086`; `writeInterval` is 1200, so **no time
directory was ever written** and level m has **no fields on disk**.

**Crash triage is the supervisor's non-delegable §3 check.** Evidence recorded,
verdict withheld. Level c reached `endTime` on the same physics with the same
schemes, so a bare "finer mesh, smaller effective step" story does not
自-evidently hold and should not be assumed.

### 2.4 Level c completed but its residual is not small

At `endTime` the `T` equation's initial residual is **7.32e-04**, four
decades above the registered `1e-6` iterative-convergence tolerance. The
registered gate is a last-two-checkpoint field change, not a residual, so this
is **not** itself a gate result — but it is a signal that the run had not
settled, and it is recorded now rather than discovered at grading.

### 2.5 The running level f was NOT killed

`f` was still inside its 30000 s cap and not overrunning. Killing a solver
destroys evidence, and whether `f` crashes near the same step as `m` is
diagnostic information about the case setup. **Cost is trivial** ($0.29 derived
for the whole rung) and the supervisor has removed cost as a ground. Left
running, deliberately, and flagged rather than decided.

## 3. Builder mutation audit — 6 CAUGHT, 5 SURVIVED

Method as before: mutate `build_t8.py` on **copies**, build into a scratch
root, `blockMesh` + `checkMesh`, then run the **frozen comparator's own**
structural instruments (hash-verified identical to `f04f9a674e03`) against the
result. Level `c` only, for cost. `PYTHONDONTWRITEBYTECODE=1` throughout.

**The first run of this suite was VOID: the unmutated control FAILED**, on the
same `r₂/r₁` refusal — every row read "CAUGHT" for a reason that had nothing to
do with the mutation. That is how §2.1 was found. The table below is the re-run
**with the `r₂/r₁` precondition corrected to 7/3 in the scratch copy of the
instrument**, so the control passes and the remaining instruments can be judged.

| id | category | verdict | caught by |
|---|---|---|---|
| **B0 control (unmutated)** | control | **SURVIVED** ✓ | *(as required — the control must pass)* |
| B1 radial divisions 8→9 | mesh generation | **CAUGHT** | `grade()`: mesh 6560 cells, registered 6400 |
| B2 wedge half-angle 2.5→3.0° | mesh generation | **CAUGHT** | `check_scale_against_mesh`: 1.662e-01 relative > 1e-6 |
| B3 radial grading 1→2 | mesh generation | **CAUGHT** | `resolve_planes`: r₂/r₁ = 2.5667 |
| B4 `EXPECT_CELLS` 6400→6401 | registered constant | **CAUGHT** | `grade()`: mesh 6400, registered 6401 |
| B5 `CASE.txt` nz doubled | registered constant | **CAUGHT** | `resolve_planes`: 320 planes × 40 ≠ 6400 |
| B6 `CASE.txt` endTime +1 | registered constant | **CAUGHT** | `check_completion`: CASE.txt ≠ controlDict |
| **B7 `R_STATIONS` 0.1→0.15** | mesh generation | **SURVIVED** | — |
| **B8 source `w0` 0.6→0.9** | field initialisation | **SURVIVED** | — |
| **B9 source `dT0` 21.14→30** | field initialisation | **SURVIVED** | — |
| **B10 outlet `patch`→`wall`** | boundary assignment | **SURVIVED** | — |
| **B11 outlet U BC → `fixedValue`** | boundary assignment | **SURVIVED** | — |

**The survivors, said plainly, because a survivor named is worth more than a
green suite.** Every structural instrument T8 has is **geometric or
bookkeeping**. Not one of them looks at **what was initialised or what the
boundaries do**:

- **B8/B9 move the source Richardson number** away from the registered pure-plume
  `Ri₀ = 0.192`, turning the plume into a forced plume or jet — which moves
  `n_w`, `n_T`, `n_Q` **toward the jet values the ±0.05 bands exist to
  discriminate against**. Invisible.
- **B10/B11 confine or fix the outlet**, changing entrainment — the physics the
  exponents measure. Invisible.
- **B7 changes near-axis resolution on one level only**, breaking the geometric
  similarity the Roache ladder assumes, while leaving cell count, plane count
  and total volume untouched. Invisible.

**At least four of the five survivors can move a graded value**, which is the
condition the supervisor pre-declared. **They were not observed — they were
demonstrated to be undetectable**, which is the weaker and more useful claim:
this is a statement about the instrument's blind spots, not an allegation about
the shipped builder. `build_t8.py` on disk is the frozen, hash-verified file
and none of these mutations is present in it.

The gap is real: T8 registers **no control that reads the initialised fields or
the boundary conditions back and checks them against the registered case
constants**, though `CASE.txt` carries `w0`, `dT0`, `T_source`, `F0`, `k0` and
`epsilon0` precisely so that such a control could exist.

## 4. Cost — estimate vs actual (rule 12)

| level | predicted | actual | ratio | note |
|---|---:|---:|---:|---|
| c | 7.13 core-min | **3.817** | **0.54** | completed |
| m | 42.81 core-min | **2.50** | — | **crashed; not a calibration point** |
| f | 285.40 core-min | in progress | — | — |

Level c came in at **54 % of prediction**, i.e. the §8 cross-mode rate borrow
(PIMPLE rate applied to a SIMPLE run) **over-predicted**, in the direction §8
declined to guess. A `docs/COST_CALIBRATION.md` row is **owed at rung
completion**, not now — the rung is not complete and one level crashed.
**Derived spend so far: well under $0.05.**

## 5. Verdict

**BLOCKED.** The solves ran, but the frozen comparator **cannot grade this
mesh**: §12 S3's `r₂ = 3r₁` precondition is false for the OpenFOAM wedge the
document itself registers, measured at **7/3** on the real level-c mesh. Level
**m crashed (SIGFPE)** and wrote no fields. No T8 gate verdict is reachable
under this pre-registration, and **nothing may be adjusted to reach one** —
compute has started and rule 2 has closed §1–§10 and §12.

**On the supervisor's desk, and reserved to the supervisor and Sanaa:** whether
T8 is re-registered fresh with the corrected extrapolation `(49f₁ − 9f₂)/40`;
the triage of the level-m SIGFPE; and whether level f is allowed to finish.

**What I could not verify:** whether level f completes or crashes; whether the
level-m crash is mesh-related or setup-related (triage is not mine); and
whether `(49f₁ − 9f₂)/40` is right for the **flat-sided** wedge — I derived it
for the exact annular centroid ratio, and the 0.1 % flat-sided correction on
the radii themselves has **not** been carried through that derivation.

---

# APPENDIX 3 — the `m` configuration diff: the setup hypothesis is REFUTED (2026-08-25)

Ruling 2 named a hypothesis with a mechanism: a **level-specific initialisation
or boundary error in `m`** — the defect class the builder audit (B7–B11) showed
the instruments cannot see. **It was tested and it is refuted.** No compute.

## 1. Method

Every file in `0.orig/`, `constant/` and `system/` compared **by md5 across all
three levels**, `polyMesh` excluded (it is generated from `blockMeshDict`).

## 2. Result — identical everywhere it could have differed

| file | c vs m vs f |
|---|---|
| `0.orig/T`, `U`, `alphat`, `epsilon`, `k`, `nut`, `p_rgh` | **IDENTICAL (all 7)** |
| `constant/g`, `transportProperties`, `turbulenceProperties` | **IDENTICAL (all 3)** |
| `system/fvSchemes` | **IDENTICAL** |
| `system/fvSolution` | **IDENTICAL** |
| `system/controlDict` | differs |
| `system/blockMeshDict` | differs |

Both differences are **registered per-level values and nothing else**:

- **`controlDict`** — the *complete* diff is `endTime` (8000 / 12000 / 20000)
  and `writeInterval` (800 / 1200 / 2000). Both are §5 registered values. **No
  other line differs**, in either comparison.
- **`blockMeshDict`** — normalising every `hex … (NR NZ 1)` division triple
  gives **md5 `edd58933141d4cf6abecc1ef160b40e9` for all three levels**.
  Identical vertices, identical boundary block, identical patch names and
  **types**, identical `simpleGrading (1 1 1)`. The only differences are the
  division counts, each exactly doubled: `(4,12,16,8)×160` →
  `(8,24,32,16)×320` → `(16,48,64,32)×640`.

**There is no level-specific initialisation, boundary type, scheme, relaxation
or transport difference in `m`. The hypothesis is refuted.**

This does **not** retract the builder audit: B7–B11 remain genuinely invisible
to every instrument T8 has. It says that **this particular blind spot is not
what happened to `m`** — which is exactly what a discriminating measurement is
for, and it came out negative.

## 3. What the crash actually looks like, measured

With the setup identical, the divergence is **numerical**. All three levels
enter the same `k`–`epsilon` startup transient; only `m` fails to leave it.

| level | cells | `bounding epsilon` | `bounding k` | steps | rate | outcome |
|---|---:|---:|---:|---:|---:|---|
| c | 6,400 | 305 | 232 | 8,000 | **3.8 %** | contained, max stays **O(5e-2)**; `T` residual **7.32e-04** |
| m | 25,600 | 419 | 360 | 1,085 | **38.6 %** | **escalates to 4.6e+64, SIGFPE** |
| f | 102,400 | 103 | 51 | 1,224 | **8.4 %** | contained, max **O(1e6)**; `T` residual **5.11e-06** |

- **`epsilon` goes negative on every level from the very start** — `m`'s first
  bounding is at **`Time = 24`**, at a benign `min −5.8e-07, max 0.070`.
- `m`'s escalation once established is roughly **seven orders per iteration**:
  `5.1e+03 → 7.0e+11 → 1.7e+43 → 4.6e+64`, terminating in SIGFPE inside
  `PBiCGStab::scalarSolve` from `libincompressibleTurbulenceModels`.
- **The bounding rate is non-monotone in resolution** — 3.8 % / 38.6 % / 8.4 %.
  Supervisor's reading confirmed: **the finest mesh is the healthy one.**
- `T` never bounds on any level. **The turbulence closure diverged; the
  momentum and thermal fields did not.**

**Mechanism candidate, named and NOT asserted:** `fvSolution` is identical
across levels and applies **fixed relaxation with no ramp** (`p_rgh 0.3`;
`U`, `T`, `k`, `epsilon` 0.5), and the case carries **no `epsilon` limiter or
`limitT` fvOption**. An un-damped `k`–`epsilon` startup transient escaping at
one resolution and not others is consistent with that, but this lane has **not
measured it** and does not claim it. **Triage remains the supervisor's.**

## 4. Verdict on this appendix

**`m` is `NOT A RESULT`** (supervisor's ruling 2), and the crash is a
**finding about the case setup's numerics**, recorded as one.

**`f` runs for DIAGNOSTIC value and CANNOT be graded.** §12 S3's weights are
wrong under this pre-registration and nothing may be adjusted to reach a
verdict. **`f` reaching `endTime` is not a result and must never be recorded as
one.** At last check `f` was alive at `Time = 1225` with `T` initial residual
**5.11e-06** and still inside its 30,000 s cap.

**`BLOCKED` stands, on two independent grounds** — the extrapolation
precondition (§2.1) and rule 5 order (1), under which no triple was ever
gradeable because `c` never converged and `m` wrote no fields.

## 5. The re-registration draft

Drafted at
**`/home/ubuntu/Certonomous/docs/campaigns/T-family/T8_REREGISTRATION_DRAFT_2026-08-25.md`**
— **DRAFT, NOT A REGISTRATION, NOT FROZEN, no rung id claimed.** It carries the
disk-read weights (`w1 = k²/(k²−1)`, `w2 = −1/(k²−1)` from radii read off
disk, asserting `r₂ > r₁ > 0` and never a ratio), the annular-centroid fixture,
the third-ratio selftest arm, and a proposed read-back control for the
initialisation and boundary constants that closes four of the five surviving
builder mutations.

**One general result fell out of writing it, and it strengthens A1.3:** since
`w1 + w2 = 1` identically **for every `k`**, the both-column plant shifts the
axis value by exactly `PLANT` **at any ratio whatsoever**. The registered §9
arm is therefore **blind to a weight error in general** — not merely to the
`(7f₁−f₂)/6` case that exposed it. **The innermost-only arm must be registered
as load-bearing, not carried as supplementary.**

**Authorisation to re-register is Sanaa's and the chief's. This lane drafted
and did not register.**
