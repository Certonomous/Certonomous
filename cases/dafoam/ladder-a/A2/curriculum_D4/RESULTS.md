# Curriculum D4 — RESULTS

**RUNG VERDICT: `BLOCKED`.** Arm O — the optimisation — is **complete and converged**, and
nine of the fourteen registered gates are met. **The bright line is uncrossed:** arm F, the
endpoint finite-difference table, has not run, so `DAFOAM_CHARTER.md` §2 and §9 are not
satisfied and **no optimum, drag reduction or gradient in this file is a validated result.**
What unblocks it is named in §9 below.

Graded 2026-08-25 by the D4 custody/grade lane. Every number below cites an artifact still on
disk, by path. **Nothing here is sent, filed, uploaded, posted or commented — SUBMISSIONS ARE
PARKED and sending is Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

---

## 1. What ran, and the completion rule applied in full

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/`.
Ledger `.../ledger.txt` — the launcher's own file, and the source of every cost and kernel
figure below.

| arm | task | rc | kernel `ExitCode`/`OOMKilled` | wall s | core-min | cap | verdict |
|---|---|---|---|---|---|---|---|
| **P1** | decomposition determinism ×2 + placement | 0 | `0 false` | 5 | **0.333** | 5.0 | complete |
| **P2** | `compute_totals`, the calibration probe | 0 | `0 false` | 546 | **36.4** | 55.0 | complete |
| **O** | `run_driver`, IPOPT | 0 | `0 false` | 7667 | **511.133** | 620.0 | complete |
| **F** | **endpoint FD, 5 components** | — | — | — | — | 120.0 | **NOT LAUNCHED** |

**Arm O satisfies every clause of the completion rule** (`CLAUDE.md` rule 4, in the DAFoam
analogue prereg §7 G1 registers):

* `rc = 0`, and the **kernel's** own record — not the harness's `$?` — reads
  `inspect(exit,oomkilled)=[0 false]`, read from `docker inspect` before the container was
  removed (prereg §7b).
* The producer's **own output file** terminates: `.../O/opt_IPOPT.txt` ends
  `EXIT: Optimal Solution Found.`
* The solver log ends with an `End` line and `ExecutionTime = 7634.64 s`
  (`.../O_20260825T181237Z_2359354.log`), with the L-252 provenance sentinel
  `.log.ok.20260825T181237Z_2359354` present.
* **Age guard:** the case's own datum `.../O/.d4_age_datum` reads epoch **1787681557**
  (2026-08-25 18:12:37 UTC), written by the launcher from `0/U` at stage time. `opt_IPOPT.txt`,
  `OptView.hst` and the `processor*` trees all carry mtimes of 20:20 UTC — **strictly newer**.
  No graded artifact predates the run allowed to produce it.

**Frozen-instrument identity re-verified against the committed blobs** (`CLAUDE.md` rule 2 —
the frozen file must be shown to *be* the file that ran). Worktree, committed blob and the
copy staged in the run root agree, md5 for md5:

| file | md5 | worktree = committed = run-root |
|---|---|---|
| `d4_opt_runScript.py` | `2906d52a5dbed2bacbaeaf85a37d3fe8` | identical |
| `d4_run_arm.sh` | `399957c616215c8f1ae078abe2e97958` | identical |
| `d4_extract_endpoint.py` | `ee7d3c99fd716da23779cb651961918e` | identical |
| `d4_fd_endpoint.py` | `c6112b0ec3bfdb5287345e350500f64a` | identical |
| `d4_grade.py` | `f162ef69a7385e5d0586ef5f27657cbb` | worktree = committed; **not staged to the run root by design** — the launcher stages only the three producers |

---

## 2. THE TERMINATION — and it was PREDICTED, not a surprise

`.../O/opt_IPOPT.txt`, IPOPT's own output file:

```
Number of Iterations....: 80
Objective...............:   2.1125978108239574e-02
Dual infeasibility......:   5.4196651597211676e-06
Constraint violation....:   7.3747727757922377e-08
Overall NLP error.......:   5.4196651597211676e-06
EXIT: Optimal Solution Found.
```

125 objective evaluations, 81 gradient evaluations, 6898.483 CPU s in NLP function evaluations.
**The optimiser converged against its own registered tolerance (`tol` 1e-5); it did not
cap-stop**, and `max_iter` 100 was never reached.

**This is prediction P1 of §11, and it is a HIT.** The pre-registration registered
*"IPOPT prints `EXIT: Optimal Solution Found.` within `max_iter` 100"* **before compute**.
Convergence is therefore the registered expectation met, **not a surprise**, and it is recorded
that way. Prereg §7 G3 makes a converged run `PASS`-eligible; §9's cap-stop clause
(`GATE REACHED` or `NOT A RESULT`, never `PASS`) is **not engaged** here.

**What must NOT be claimed from it.** `DAFOAM_CHARTER.md` §9's incident record states this
lab's standing position as *"no optimiser run has ever converged"*. **That prose is stale and
this lane does not amend it** — retiring or amending a charter clause is reserved to Sanaa
(`CLAUDE.md` FIRST-ACTION RULE). A sweep of `/home/ubuntu/certonomous-runs/*/opt_*.txt` finds
`EXIT: Optimal Solution Found.` already present in **D1 `armO`, D2 `armA`, D13 `s2`/`s4`/`s5`,
`P2-a4-opt/opt` and `P3-a4-opt-shipped/opt`**. So arm O is **not** the lab's first converged
optimiser run. The narrower true statement is that it is the first convergence recorded on the
**A2 MACH wing at 38,304 cells with 104 free design variables** — a far larger NLP than the
A4 cases (2,777 cells) that carry most of the prior EXIT lines. **That narrower claim is the
only one this file makes.**

---

## 3. Gate-by-gate

The grader was run as the pre-registration fixes it. **Run with the registered arm set
`P1,P2,O,F`, the frozen `d4_grade.py` REFUSES, rc = 2:**

```
D4_GRADER REFUSED G1: {"arm_absent_from_ledger": "F"}
```

**That refusal is the item's verdict, and it is the correct behaviour** — prereg §7b registers
that G1 refuses on `arm_absent_from_ledger` *"rather than grading an absence"*. The instrument
refused rather than degraded.

A **second, explicitly DIAGNOSTIC** invocation over the arm subset `P1,P2,O` was made to
recover the gates that do not depend on arm F. **This subset is a departure from the registered
arm set and its output is not the item's grade**; it is recorded because a grader-emitted
verdict is worth more than a lane's hand reading of the same artifact. It too refuses, one gate
later, on the FD-independent half being exhausted:

```
D4_GRADER REFUSED G2: {"absent": ".../O/d4_major_history.json"}
```

Its output — verdicts emitted **before** the refusal — is committed at
`cases/dafoam/ladder-a/A2/curriculum_D4/d4_grade_partial_20260825.json`.

| gate | verdict | value, and the artifact it cites |
|---|---|---|
| **G1** completion + age guard | **PASS** (arms P1,P2,O) / **refuses on the registered set** | age datum 1787681557; all graded artifacts newer. `ledger.txt`, `.d4_age_datum` |
| **G2** CL feasibility, bands A and B | **`BLOCKED`** | `d4_major_history.json` does not exist — it is written by `d4_extract_endpoint.py`, which runs only in arm F. See §4 |
| **G3** termination | **PASS** | `EXIT: Optimal Solution Found.` at 80 majors. `O/opt_IPOPT.txt` |
| **G4** drag reduction, band C | **PASS** | **28.6758 %**, band C **[25, 45] %**, prediction 30 %. `CD₀ = 2.9619634e-02` (major 0) → `CD_f = 2.1125978e-02` (major 80), both from `O/opt_IPOPT.txt` |
| **G5** endpoint FD, bands D and E | **`BLOCKED`** | `d4_fd_endpoint.json` does not exist. **THE BRIGHT LINE.** See §4 |
| **G6** planted zero | **`BLOCKED`** | no FD artifact to plant into |
| **G6b** negative control | **`BLOCKED`** | as G6 |
| **G7** count refusal control | **`BLOCKED`** | as G6 |
| **G8** decomposition determinism | **PASS** | `d4_decomp_A.json` and `d4_decomp_B.json` are **identical** — `{processor0: 9504, processor1: 9600, processor2: 9608, processor3: 9592}`, summing to **38,304**, the registered cell count. `scotch`, `numberOfSubdomains 4`, from `P1/system/decomposeParDict`. **Prediction P7 HIT** |
| **G9** toolchain identity | **PASS** | one distinct image digest across all three arms, `sha256:2927768a…f6d35`, equal to the registered PATCHED digest; one distinct IDWarp `.so` md5, `85f59e87253e0a71a813f64ca6e4c425`, in all three arm logs. `ledger.txt` |
| **G10** cap discipline | **PASS** | enforced == registered for every arm (5.0/5.0, 55.0/55.0, 620.0/620.0), and actual ≤ cap in every case, **read back out of the ledger**, not from the launcher's claim |
| **G11** memory envelope | **PASS** | `OOMKilled false` on all three arms, from `docker inspect`. Peak stayed inside the 12 GiB cap; `MemAvailable` moved 17.46 → 27.63 GiB across arm O. **Prediction P8 HIT** |
| **G12** CPU placement | **PASS** | affinity union **{5, 6, 7, 9}** — exactly the registered cpuset; **four ranks on four DISTINCT single cores** (rank0→5, rank1→6, rank2→7, rank3→9), from `P1/d4_placement_rank{0,1,2,3}.json`. **No shared-core collision** — the D13 defect did not reproduce. Delivered cores **3.9880** (arm O, n=508) and **3.9867** (arm P2, n=36) of a 4-core quota, both far above the 3.0 floor. **Predictions P11 and P12 HIT** |

**G12 carries a registered consequence and it is discharged.** Prereg §5b: *"No adjoint-
conditioning finding may be recorded by this item until G12 has ruled out core contention."*
G12 passes at 99.7 % of quota delivered, so **core contention is ruled out** and D4's cost
figures are **not** contention-contaminated. Arm P1's delivered-cores cell reads
`NOT_MEASURED` — the arm ran 5 s, shorter than the sampler's 15 s poll. Per prereg §5b that is
reported as `NOT_MEASURED` and **never as a passing placement gate**; the registered mapping
excludes an unmeasured arm from the floor test rather than failing on it, and the floor is
carried by P2 and O, which are the MPI arms that matter.

### 3a. Band A is NOT established, and an available bound does not establish it

`O/opt_IPOPT.txt` carries an `inf_pr` column, and because `inf_pr` is the maximum violation over
**all** constraints, `|CL − 0.5| ≤ inf_pr` always. That gives one band for free and **refuses to
give the other**:

* **Band B (final major, `|CL − 0.5| ≤ 1.0e-5`) HOLDS by that bound** — final `inf_pr` is
  **7.370e-08**, three orders inside the band. Corroborated, but **not graded**, by the rank-0
  OpenMDAO summary in the arm log printing `CL = 0.49999993`; that line is **stdout**, and
  prereg §9a's parse-from-files discipline is why it is corroboration and never the number.
* **Band A (every major, `|CL − 0.5| ≤ 5.0e-4`) is NOT established.** The maximum `inf_pr` over
  all 81 majors is **1.080e-02, at major 4** — above band A's bound. **This does not mean band A
  failed:** `inf_pr` at that major may be a `thickcon`, `volcon`, `lecon` or `tecon` violation and
  not the `CL` equality at all, and `opt_IPOPT.txt` cannot tell the two apart. **The bound is
  one-sided and it is not evidence in the failing direction.** Band A needs G2's registered
  instrument, `d4_major_history.json`, which separates `CL` per major. **Prediction P3 is
  therefore UNSCORED, not missed.**

---

## 4. THE BRIGHT LINE — arm F did not run, and what that costs

`DAFOAM_CHARTER.md` §2: *"No DAFoam gradient enters a record, a report or an optimisation
without a finite-difference table beside it."* §9: *"Every optimisation reports a finite-
difference check of the gradient **at its final design point**"*, and among the things §9
forbids outright is *"reporting a design change as validated without an FD check at the design
point that produced it."*

**`d4_fd_endpoint.json` does not exist.** Neither does `d4_endpoint_dvs.json` or
`d4_major_history.json`. The reason is structural, not a failure: the producer
`d4_opt_runScript.py` is **byte-identical to the tutorial's `runScript_AeroOnly.py`** (that
byte-identity is the point of prereg §1) and therefore writes none of them. All three are
written by arm **F**, which the launcher dispatches as
`python d4_extract_endpoint.py && mpirun -np 4 … python d4_fd_endpoint.py`. **Arm F is a
separate registered arm with its own 120 core-min cap and it has not been launched.**

**Consequence, stated plainly.** The 28.6758 % drag reduction and the converged design point
are **`BLOCKED`, not validated**. The five components named in advance in prereg §6 — `shape`
idx46, `shape` idx18, `shape` idx0, `twist` idx0, `patchV` idx1 — are ungraded, and
**predictions P5, P6 and P9 are PENDING, none of them scored.** No gradient claim is made by
this file.

**Why this lane did not run it — recorded, not worked around.** Arm F was staged and launched
by this lane and **both actions were denied by the session's auto-mode permission classifier**:
first the launch, then the bare `d4_stage_F.sh` copy. This lane did not attempt to route around
either denial. Preconditions were otherwise verified and all hold: `F/` does not yet exist,
`MemAvailable` is 27.5 GiB against a 12 GiB cap, **no sibling containers are live**, the run
root is mode 777, and the local image tag resolves to exactly the registered PATCHED digest.
**Arm F is ready to run and is blocked only on permission.**

---

## 5. Two rows — ONE is bought, and the item cannot claim toolchain independence

`DAFOAM_CHARTER.md` §6 and prereg §10: **PATCHED is bought, SHIPPED is not.**

| row | image | digest | status |
|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a…f6d35` | **RUN** — arms P1, P2, O; IDWarp `.so` md5 `85f59e87…c425` |
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d…f07fc` | **`PENDING`** — not run, not failed; a separately registered re-buy |

**Everything in this file is a patched-IDWarp statement.** D5, D6 and D14 inherit that
qualifier and **must not read D4's optimum as toolchain-independent.** That consequence was
registered before compute, and it is repeated here rather than discovered afterwards.

---

## 6. Grader instrument state — what was selftested, and what was NOT

**The FROZEN grader `d4_grade.py` has NEVER been selftested, and that is D4-DEF-1.** Its
`--selftest` flag is declared and **never read**, so passing it beside a full invocation
silently ran a complete grade and exited clean. **No grader selftest was run for D4's frozen
instrument**, and no reading of this file may describe D4 as "grader selftested".

The repair lives in **`d4_grade_SUPPLEMENT.py`**, which reproduces the frozen grader's body and
wires the flag to a real selftest with a distinct exit path (rc 3, no `--out` written). It is
**not** the grading instrument — swapping a grader after compute would breach the prereg §2/§9a
freeze regardless of the supplement's quality.

**Selftest, extended 2026-08-25 by this lane: 29 units, 29/29.** The eight units added are
`G5-EMPTY-component-set`, `G5-SHORT-component-set`, `G5-REORDERED-component-set`,
`G5-rows-key-ABSENT`, `G5-per-component-beyond-band-D`, `G5-sign-flip`, `G5-plateau-violation`
and `G6-control-cannot-run-must-not-pass`. Before them the FD fixture graded clean and was
**never mutated**, so G5 — this family's bright line — was the one emitted gate with no
end-to-end unit behind it. Full account in
`cases/dafoam/ladder-a/A2/curriculum_D4/LANE_REPORT_custody_grade.md` §3.

**D4-DEF-2 did NOT materialise.** It was registered in advance as *"if the empty-component-set
unit does not fire, that is D4-DEF-2, the D3 defect reproduced, and D4 is `NOT A RESULT`
pending repair"*. **The unit fired**, with a named count refusal printing the count:
`{"COUNT_REFUSAL": "empty component set", "n_rows": 0, "n_registered": 5}`. **D4 is not
`NOT A RESULT` on that ground.**

**D4-DEF-3 was found — a NEW defect, and it is in the FROZEN grader too.** With `rows` absent
from the FD artifact entirely, the G7 count-control mutators index the source document
(`d["rows"][:2]`) and raise an **uncaught `KeyError`**: the grader exits **rc = 1 with a
traceback and writes no verdict file at all**, on the very gate whose purpose is to prove a
malformed component set is refused *by name*. Prereg §7b requires `rc = 1` and `rc = 2` to be
different, named failures; an unhandled exception is neither. **Repaired in the supplement, by
a named `G7` refusal raised before any mutation runs. `d4_grade.py` carries it UNREPAIRED and
was not edited** (`CLAUDE.md` rule 6; prereg §9a) — md5 re-verified `f162ef69a7385e5d0586ef5f27657cbb`
after all work.

`scripts/check_grader_self_blindness.py` reports the supplement **clean on both probes**. That
is **not a proof of correctness**, and the checker says so itself: probe B fires on
`os.path.join` and is **silent on `pathlib` and f-strings** (commit `3dc99590`).

---

## 7. Cost — estimate versus actual (`CLAUDE.md` rule 12)

`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED` — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **All dollar figures are DERIVED, not
measured.** Core-minutes are measured, from `ledger.txt`.

| arm | predicted | actual | ratio | cap |
|---|---|---|---|---|
| P1 | 1.0 | **0.333** | 0.333 | 5.0 |
| P2 | 33.0 | **36.4** | 1.103 | 55.0 |
| O | 511.0 | **511.133** | **1.0003** | 620.0 |
| F | 53.0 | **not run** | — | 120.0 |
| **item (P1+P2+O)** | **545.0** | **547.866** | **1.0053** | ceiling 800.0 |

547.866 core-min = **$0.468 DERIVED**. Gross equals cleaned: **no waste is identified** — three
arms, all `rc = 0`, no failed arm, no restart, no stall.

**Arm O's 1.0003 is a COINCIDENCE OF TWO COMPENSATING ERRORS and must not be read as a good
estimate.** Decomposed against the pre-registration's own arithmetic (5.106 core-min/major ×
100 majors = 510.6):

* **major count: 80 actual against 100 predicted — a factor 0.800.** The run converged rather
  than exhausting `max_iter`.
* **per-major cost: 511.133 ÷ 80 = 6.389 core-min/major against the A2 anchor's 5.106 — a
  factor 1.2513**, a **25.1 % underestimate** of what a major costs on this case.
* 0.800 × 1.2513 = **1.0010**, which is the ratio observed.

**The lesson is the one the ratio hides:** an item-level actual/predicted of 1.000 concealed a
25 % per-major misprediction and a 20 % major-count misprediction that happened to cancel.
**A calibration ledger read at item level would have recorded this buy as perfectly estimated.**
The per-major figure — **6.389 core-min/major on A2 at np=4 `scotch`, patched** — is the number
a future item should inherit, not the item total.

**Attribution, with contention and waste named separately and never absorbed into the ratio**
(`COMPUTE_BUDGET_CHARTER.md` §6):

* **Misprediction:** the whole of the 1.2513 per-major gap and the 0.800 major-count gap.
* **Contention:** **≈ 0.30 %**, bounded by measurement, not assumed — delivered cores 3.9880 of
  a 4.0 quota over n = 508 samples, so at most ≈ 1.5 core-min of arm O. One sibling container
  (`d8_opt`) was live at arm O's start and gone by its end; `max_nr_throttled` reached 22,359,
  yet delivered cores held at 99.7 % of quota.
* **Waste: none.**

**A disclosed heuristic that does NOT apply.** `CLAUDE.md` rule 12 notes *"a row over 3600 wall
s is a stall"*. Arm O ran **7667 wall s**. It is **not** a stall: the arm is a registered
optimisation with a 9300 s enforced timeout that terminated on IPOPT's own convergence
statement with `rc = 0`, 1633 s inside its timeout. The heuristic is disclosed rather than
silently passed over.

**Arm F, unrun, is predicted at 53.0 core-min against a 120.0 cap**; the item ceiling of 800.0
has 252.1 core-min of headroom, so arm F fits with room to spare and **no cap needs to move.**

---

## 8. Predictions scored — HIT / MISS / UNSCORED, never adjusted

| id | prediction | outcome |
|---|---|---|
| P1 | IPOPT prints `EXIT: Optimal Solution Found.` within `max_iter` 100 | **HIT** — at 80 majors |
| P2 | drag reduction in [25, 45] %, near 30 % | **HIT** — 28.6758 % |
| P3 | `|CL − 0.5| ≤ 5.0e-4` at every major | **UNSCORED** — needs G2's instrument (§3a) |
| P4 | arm O costs 400–620 core-min (prediction 511) | **HIT** — 511.133 |
| P5 | `shape` idx46 is `NOT A RESULT` (near-zero) at the endpoint | **PENDING** — arm F |
| P6 | ≥ 3 of the 4 remaining components graded and inside band D | **PENDING** — arm F |
| P7 | decomposition determinism holds | **HIT** — the two maps are identical |
| P8 | peak memory inside 12 GiB, no `OOMKilled` | **HIT** — `false` on all arms |
| P9 | `shape` idx18 inside band D at the endpoint | **PENDING** — arm F |
| P10 | arm P2 ≤ 55 core-min, so arm O is authorised | **HIT** — 36.4; arm O was authorised by its own calibration gate |
| P11 | four ranks on four **distinct** cores inside {5,6,7,9} | **HIT** — 5, 6, 7, 9 |
| P12 | delivered cores ≥ 3.0 of the 4-core quota | **HIT** — 3.9880 (O), 3.9867 (P2) |

Eight HIT, zero MISS, one UNSCORED, three PENDING. **No prediction was adjusted.**

---

## 9. What is BLOCKED, and exactly what unblocks it

**`BLOCKED`: arm F, and with it G2, G5, G6, G6b, G7 and predictions P3, P5, P6, P9.**

What unblocks it is one command pair, run with permission to launch a container, from the run
root, with the frozen launcher unmodified:

```
bash d4_stage_F.sh                      # copies O/ -> F/, asserting no answer file pre-exists
bash d4_run_arm.sh F dafoam-idwarp-rot:v1
```

Everything else is in place: preconditions verified, image digest matched, ranks free, memory
free, cap and memory limits held internally by the launcher, and 252.1 core-min of item
headroom. **Until arm F runs, D4's rung verdict stays `BLOCKED` and its optimum is not a
validated result.**
