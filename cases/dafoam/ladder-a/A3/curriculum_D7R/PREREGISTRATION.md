# CURRICULUM D7R — PRE-REGISTRATION v1.0

**ONERA M6, lift-constrained transonic drag minimisation. A RE-REGISTRATION of curriculum D7.**

**Date frozen: 2026-08-25. Lane: dafoam `lab-lane`. Authorised by the dafoam-supervisor's second
ruling `bdb1f03d`** (`../curriculum_D7/SUPERVISOR_D7_RERULING.md`).

**NOT LAUNCHED AT THIS COMMIT.** No `D7R` run root exists, no arm directory exists, no container
named `d7r_*` has ever been created. Verified by the four commands in §12.

---

## 0. WHY THIS ITEM EXISTS, AND WHAT IT DOES NOT DO TO ITS PREDECESSOR

**D7's pre-registration is SUPERSEDED, CITED, AND NEVER REWRITTEN** (`CLAUDE.md` rule 6). Its
verdicts stand exactly as recorded on that frozen document:

| D7 arm | verdict, standing |
|---|---|
| `P1` | **PASS** |
| `P2` | **GATE REACHED** — cap-stop at the registered 60.0 core-min |
| `O` | **BLOCKED** |
| `F-S`, `F-P` | **BLOCKED** |

**Nothing in this document alters, reinterprets or softens any of them.**

**Why D7 could not continue.** Three facts, each verified independently by the supervisor against
the launcher and the ledger, are **jointly unsatisfiable**: arm `O` requires the inherited colouring
(`stage_coloring` called unconditionally, no fallback); the cache publishes **only** on `P2`
`rc = 0`; and `P2` cannot reach `rc = 0` because its cap is a hard `timeout` kill, which the
supervisor **correctly refused to move** — the cap is the **third of rule 2's four protected items**
and first compute had happened. **No order of operations on the frozen document reaches arm `O`.**
The cap-extension question and the arm-`O` question were always the same buy.

---

## 1. THE FOUR BINDING REQUIREMENTS FROM THE RULING, AND HOW EACH IS DISCHARGED HERE

### R1 — the cap is a RUNAWAY GUARD THAT REPORTS, not a hard `timeout` kill

**D7's launcher wrapped the container in `timeout $TMO`, so the cap was a `SIGKILL`.** `P2` was
killed at 901 s with its adjoint **three orders down and still falling** (KSP
`1.839e-01 → 4.841e-04` over 800 iterations, monotone). **A converging solve was destroyed by a
budget the lab no longer imposes.**

**This item registers TWO thresholds and they do different jobs.** This is a design choice on the
supervisor's instruction *"halts and reports to me; I decide"*, read together with *"a converging
solve is never `SIGKILL`ed by its own budget again"* — **the two sentences pull in opposite
directions if a single threshold both reports and stops, so they are separated. This reading is
declared here rather than assumed, and is the supervisor's to overrule.**

| threshold | what happens when crossed | purpose |
|---|---|---|
| **CAP** (per arm, §4) | **`D7R_CAP_CROSSED` is written to the ledger and the run CONTINUES.** Nothing is signalled, nothing is killed | the reporting threshold — the supervisor decides |
| **CEILING** = **4 × CAP** (per arm) | **hard stop** | the actual runaway guard: a genuine runaway is still bounded |

**A converging solve therefore reports and continues. A runaway is still stopped.** The CEILING is
deliberately far above any predicted spend so that reaching it means something is wrong, not merely
slow.

### R2 — the colouring term is PRICED WITH A NUMBER

**This is `C-89` made binding.** D7's basis read *"13.60 (adjoint) + 2 × 3.38 (primals) + coloring
build"* — **the colouring carried no figure**, and it was essentially the entire 1.915 overrun.

**MEASURED from D7 `P2`'s own log**, which is the whole point of having spent it:

| phase | wall | **core-min at np=4** | evidence |
|---|---|---|---|
| container start → colouring start | 35.17 s | **2.34** | `Calculating dRdW Coloring... 35.17 s` |
| **the colouring build itself** | **366.47 s** | **24.43** | start `35.17 s` → `Calculating dRdW Coloring... Completed! 401.64 s`; **1,314 `ColorSweep` iterations** |
| validation + 2 primals | 280.4 s | **18.69** | `401.64 s` → `Solving Linear Equation... 682.02 s` |
| adjoint KSP (INCOMPLETE — killed) | 219.0 s | **14.60** | `682.02 s` → kill at 901 s |

**THE COLOURING ALONE, AT 24.43 CORE-MIN, IS LARGER THAN D7'S ENTIRE 30.0 CORE-MIN PREDICTION FOR
THE ARM THAT CONTAINED IT.** That is what an unpriced term costs.

### R3 — cache reuse: **BUILD FRESH.** The refusing control the ruling asked for IS NOT DESIGNABLE, AND THAT IS MEASURED

**The ruling names the `.bin.info` sidecar as "the natural candidate" for a control that can refuse.
IT WAS MEASURED AND IT CANNOT WORK.**

```
$ wc -c dRdWColoring_4.bin.info        22
$ cat  dRdWColoring_4.bin.info         -vecload_block_size 1
```

**The entire sidecar is a PETSc vector-load option string.** It carries **no mesh identity, no cell
count, no DV set, no discretisation stencil, no colour count — nothing about the configuration the
colouring was built for.** Two colourings built for two completely different meshes would produce
byte-identical sidecars.

> **A control keyed on `.bin.info` would PASS ON ANY COLOURING FILE WHATSOEVER. It is a control
> that cannot refuse — which is exactly the `D7-GRADER-DEF-3` shape this lane repaired earlier
> today: a gate that certifies absence as success.** Registering it would have been worse than
> registering nothing, because the record would then claim a validity check had been performed.

**The md5-rebuild control is decisive and self-defeating as an acceleration**: to compare a rebuild
by md5 you must first do the rebuild, which costs the 24.43 core-min the reuse was meant to save.
It is available as a *verification* and worthless as an *optimisation*.

**RULING, taken under the ruling's own fallback clause — *"if no control that can refuse is
designable cheaply, BUILD IT FRESH"*: THIS ITEM BUILDS THE COLOURING FRESH.** The price is
registered above at **24.43 core-min**, which is the entire point of `C-89`.

**Provenance of the cache that is NOT being reused, stated in plain words as the ruling requires:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/P2/dRdWColoring_4.bin`, 3,076,152 bytes,
written 2026-08-25 21:43, **built by an arm that returned `rc=124` and was cap-killed about eight
minutes later.** It is probably valid — a colouring is a structural property of the Jacobian
sparsity and does not depend on the adjoint converging — **and "probably valid" is not this lab's
standard, so it is not used.**

### R4 — `d7_grade.py` HAS NEVER RUN ON A REAL ARM. Registered as an OPEN CONDITION.

Every claim about the grader rests on its **65-unit selftest** and **16 mutants**, all of which
exercise **synthetic fixtures built by the selftest itself**. **It has never been handed a real
arm's artifacts.**

**Three times on 2026-08-25 a gate that read correct on the page failed on contact with a real
artifact** — `D4-DEF-1`, `M3` on the D12 comparator, and this lane's own `D7-GRADER-DEF-2`, which
sat **inside `g6_plant`, the gate D7's Addendum 1 called defended**.

**REGISTERED PREDICTION:** the grader's first invocation on real arm artifacts is **an event to
watch, not a formality.** If it refuses, **the refusal is a finding about the grader or the
artifacts and is recorded as such before any regrade is attempted** — never quietly worked around.
**No verdict from this item is final until the grader has run on real artifacts and its behaviour
there is recorded.**

---

## 2. THE OBJECTIVE, UNCHANGED FROM D7

Lift-constrained transonic drag minimisation on the ONERA M6 wing.

| | |
|---|---|
| mesh | the A3 rung-2 pyHyp mesh, **42,120 cells**, `max non-orthogonality 61.4935°`, `Mesh OK` — measured and committed at `b530da36` (`../curriculum_D7/MESH_ADMISSION_MEASUREMENT.md`) |
| flow | `U0 = 291.6` m/s (M 0.84), `aoa0 = 3.06°`, `primalMinResTol = 1e-8` |
| design variables | `twist` **5**, `shape` **120**, `patchV` **2** — **127 DVs** |
| objective | `CD`, minimised |
| constraint | `CL` equality at the **measured** baseline, never typed in |
| decomposition | `scotch`, `numberOfSubdomains 4`, np=4 — **pinned and disclosed** (`DAFOAM_CHARTER.md` §5) |

**Baseline, inherited as a MEASURED number from D7 `P2` and cited as such** —
`CURRICULUM-D7-a3-m6-cdmin/P2/d7_baseline.json`:
**`CD = 0.03311805865399452`**, **`CL = 0.2876130251655752`**.
**This item re-measures its own baseline in `P2` and REFUSES if the two disagree by more than
1e-6 relative** (gate `H2`, §5). An inherited number that is not re-derived is a number on trust.

---

## 3. ARMS

| arm | task | row |
|---|---|---|
| `P1` | decomposition determinism ×2 + per-rank placement | SHIPPED |
| `P2` | **fresh colouring build** + cold `compute_totals` + 2 primals | SHIPPED |
| `O` | `run_driver`, IPOPT, `max_iter` **30** | SHIPPED |
| `F-S`, `F-P` | endpoint FD, 5 components | **REGISTERED BUT GATED — see §6** |

---

## 4. CAPS, CEILINGS AND COST — every term priced with a number

| arm | **prediction (core-min)** | basis, every term numbered | **CAP (reports)** | **CEILING (hard stop)** |
|---|---|---|---|---|
| `P1` | **0.30** | D7 `P1` **measured 0.267** | 8.0 | 32.0 |
| `P2` | **60.1** | **2.34** setup + **24.43 colouring** + **18.69** validation+2 primals + **14.60** adjoint — all four MEASURED from D7 `P2`, and the adjoint term is a **FLOOR, not an estimate**: it is what an INCOMPLETE solve had consumed when killed | 120.0 | 480.0 |
| `O` | **570.0** | 19.0 core-min/major × 30 majors, carried from D7 §2a | 900.0 | 3600.0 |
| `F-S`, `F-P` | 95.0 each | 22 primals × 3.38 + one cold `compute_totals` | 130.0 | 520.0 |
| | **ITEM 630.4** (arms fired) | | | |

**`P2`'s adjoint term is registered as a FLOOR and named as one.** D7's adjoint was killed
incomplete at 14.60 core-min with its residual still falling. **How much more it needs is NOT
KNOWN, and this document does not pretend to know it.** That is precisely why the cap reports
instead of killing: **the unknown is the reason for R1, not an oversight in R2.**

**Throttling, carried forward per the ruling.** D7 `P2` recorded
`delivered_cores_mean=[3.9910 n=59 max_nr_throttled=3467]` with `siblings_pre` and `siblings_post`
both **empty**. **Sibling contention is excluded; the container hitting its own cgroup quota
ceiling 3,467 times is NOT.** Those are different claims and only the first was supported in the
relay. **This item records `max_nr_throttled` in every ledger row**, and a run throttled thousands
of times is one whose core-minutes and wall seconds tell slightly different stories.

**Cost basis:** $0.0513/core-h, **owner-stated, and any dollar figure is DERIVED, not measured** —
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Cost constraints are lifted
(Sanaa, 2026-08-25); caps are runaway guards reported to the supervisor and NO RIGOR IS TRADED TO
GO FASTER.**

---

## 5. GATES

Gates `G1`–`G13` are **inherited unchanged** from D7's frozen §5 and graded by the **committed
`d7_grade.py`**, md5 `10eb6d0928addc56272854f017e01538` — subject to R4's open condition. Two gates
are **added** by this item and they are new, not restatements:

| gate | threshold | refusal |
|---|---|---|
| **`H1`** | the colouring used by `O` was **built by an arm of THIS item that returned `rc = 0`** | **`COLOURING_PROVENANCE`** — refuses on an inherited or unattributed cache |
| **`H2`** | `P2`'s re-measured baseline agrees with D7's inherited `CD`/`CL` to **≤ 1e-6 relative** | **`BASELINE_DISAGREEMENT`** — refuses; an inherited number that is not re-derived is a number on trust |

**`H1` exists specifically so that the cache this item declines to reuse cannot re-enter by
accident.** A registered refusal to reuse is worth nothing without a gate that can catch the reuse.

---

## 6. `F-S`/`F-P` ARE GATED ON THE `D4-DEF-4` REPAIR, WHICH THIS ITEM DOES NOT AUTHOR

**`D7-DEF-4` stands** (`../curriculum_D7/D7_DEF4_SCALER_BLOCKER.md`, `5551db3d`): `shape` scaler
**10.0**, `twist` and `patchV` **0.1**, extractor on the inert `scale=False`, and **zero occurrences
of `scaler` in either read-path instrument.**

**The registered falsifiable prediction is carried forward UNCHANGED and remains UNTESTED:**

> When an `OptView.hst` first exists, `d7_extract_endpoint.py` will read `patchV[0]` as
> **`291.6 × 0.1 = 29.16`**, not `291.6`. `patchV[0]` is pinned (`lower[0] == upper[0] == U0`), so
> no optimiser can move it. **Reads `29.16` → confirmed. Reads `291.6` → this lane's finding is
> REFUTED BY ITS OWN TEST and will be recorded as plainly as the finding.**

**`O` produces the first `OptView.hst`. THE PREDICTION IS TESTED THE MOMENT IT EXISTS, BEFORE ANY
NUMBER DOWNSTREAM OF THE EXTRACTOR IS BELIEVED.**

**This item does NOT author a repair.** Per the supervisor's ruling, **D7 inherits D4's**, and two
instruments would mean two chances to reintroduce a units error that is invisible to every count-,
plant- and order-based control. **`F-S`/`F-P` remain `BLOCKED` until that repair lands and is
verified on D4's own terms, including its Limit 1: not frozen until one primal at the corrected
point reproduces the optimiser's own objective.**

---

## 7. TOOLCHAIN — two rows, by digest, never by tag

| row | image | digest |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` |
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` |

`P1`/`P2`/`O` are **SHIPPED-only**; `F-S` SHIPPED, `F-P` PATCHED. **The PATCHED row is bought
only by `F-P`, which is gated by §6 — so if this item completes with `F-P` blocked, IT IS NOT A
TWO-ROW DAFOAM VERDICT and must say so** (`DAFOAM_CHARTER.md` §6).

---

## 8. LAUNCH GATE — memory, stated before the reading it gates

| arm class | container cap | **MemAvailable floor** |
|---|---|---|
| `P2`, `O`, `F-S`, `F-P` | 12g | **≥ 16.0 GiB** |
| `P1` | 4g | **≥ 6.0 GiB** |

**Absolute floor: MemAvailable never below 12 GiB**, per the supervisor's standing instruction.
Enforced with a real refusal path **before any rank is claimed**. **The in-run host-memory sampler
is record-only and is declared record-only** — no mid-run memory stop is registered, because killing
a converging optimisation to protect a number destroys the run it protects.

**Honest disclosure about ordering:** MemAvailable was **16 GB** when this section was written, with
two peer dafoam containers live and load 15.49/16. **That reading is BELOW this item's own 12g floor,
so the thresholds above were NOT chosen to clear it** — they are the container cap plus headroom,
carried unchanged from D7 §A1.4. **This item will WAIT for capacity rather than lower the floor.**

---

## 9. STRICT COMPLETION AND THE AGE GUARD

`CLAUDE.md` rule 4, registered: `rc = 0`; an `End` line; fields present; **every field at the
endpoint NEWER than the case's own launch datum**. A guard refuses a case whose arm directory
already holds a time directory, `processor*`, `reports/`, an `OptView.hst` or a colouring cache.
**A guard that refuses is the guard working and is never disabled to get past it.**

---

## 10. INSTRUMENTS

| instrument | md5 at freeze | status |
|---|---|---|
| `d7_opt_runScript.py` | `e43902ed2cfc99022c6e21e075f88695` | inherited from D7, **byte-identical** |
| `d7_extract_endpoint.py` | `651d40c78cc52288a856934c108d1334` | inherited, **carries `D7-DEF-4`** (§6) |
| `d7_fd_endpoint.py` | `92b3fa8d20a41da029590ed3bdde4203` | inherited, **carries `D7-DEF-4`** (§6) |
| `d7_grade.py` | `10eb6d0928addc56272854f017e01538` | inherited, **R4 open condition** |
| `d7r_g8_token.py` | **`9cb743e5439252c1a733eae5124590e7`** | **NEW** — the `9eaddfe4` architecture the supervisor directed be carried forward, retargeted to this item's run root and its own token `.d7r_g8_pass`. **It imports and calls the COMMITTED `curriculum_D7/d7_grade.py`'s own `g8_decomp`** — the gate is still evaluated by the instrument that owns it, never by a reading of a log |
| `d7r_run_arm.sh` | **`716b927fc8fcfd3cb7f1284b4a6a0a82`** | **NEW — the runaway-guard launcher, R1** |

**`d7r_run_arm.sh` IS A SURGICAL TRANSFORMATION OF D7's LAUNCHER, NOT A REWRITE, AND THE DIFF IS
THE REVIEWABLE ARTIFACT.** `diff -u` against `curriculum_D7/d7_run_arm.sh` is **7 hunks, 70 changed
lines**: the run root; the `d7r_` container-name prefix; this item's caps; **the `timeout` SIGKILL
replaced by the detached-run + CAP-reports/CEILING-stops loop (R1)**; the ledger's new
`cap_reported`/`ceiling_hit` fields; **gate `H1`**; and the fresh-colouring provenance record.

**The producer command blocks are BYTE-IDENTICAL to D7's**, verified by `diff` over the whole
`case "$ARM" in … esac` region — so nothing about *what the solver is asked to do* has changed, and
`bash -n` passes. Retyping 436 lines would have risked a transcription error in exactly the part
that must not change.

**Instrument md5s are re-asserted by the launcher against the staged copies before every launch,
and it aborts on a mismatch.**

---

## 11. WHAT WOULD MAKE THIS ITEM A FAILURE

Registered in advance so it cannot be reinterpreted afterwards:

* `H2` refuses — the re-measured baseline disagrees with D7's. **That would mean D7's `P2` number
  is not reproducible and is a finding about D7, recorded as such.**
* `O` reaches `max_iter` 30 without converging → **`GATE REACHED`, never `PASS`**, because 30 is a
  cost-derived cap. **Convergence inside 30 majors would be a genuine surprise and is recorded as
  one.**
* Any `G8` failure → **every np=4 number in this item is `NOT A RESULT`.**
* The grader refuses on real artifacts → **a finding under R4, recorded before any regrade.**

---

## 12. CONDITION AT FREEZE, AND HOW IT WAS CHECKED

**No compute has occurred for this item.** Checked at the freeze commit by four readings:

| check | reading |
|---|---|
| run root `/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin` | **does not exist** |
| arm directories `P1 P2 O F-S F-P` | **0 of 5** |
| `docker ps -a --filter name=d7r_` | **0 containers** |
| any `*.log` under the run root | **0** |

**Unlike D7, the run root genuinely does not exist yet, so the plain form of the statement is true
here** — and it is checked rather than asserted.

**FROZEN. Nothing fires before this document and `d7r_run_arm.sh` are committed.**
