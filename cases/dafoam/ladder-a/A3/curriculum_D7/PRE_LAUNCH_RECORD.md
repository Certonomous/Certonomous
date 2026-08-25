# Curriculum D7 — PRE-LAUNCH RECORD

**Written and committed BEFORE the first container.** Its purpose is that a session kill costs
nothing: everything needed to resume, audit or refuse this item is on disk and in git before any
compute exists.

**Nothing here is sent, filed, uploaded, posted or commented. SUBMISSIONS ARE PARKED and sending is
Sanaa's decision alone** (`CLAUDE.md` rule 7).

**Status at the moment of writing: NOT LAUNCHED.** Zero containers, zero core-minutes, no ledger.

---

## 1. Freeze verified BY HASH, not by reading

`CLAUDE.md` rule 2 requires that the frozen file **is** the file that runs, proved by hashing it
against the committed blob.

| file | HEAD blob | worktree `git hash-object` | |
|---|---|---|---|
| `PREREGISTRATION.md` (at Addendum 2) | committed this session | `c8a4af6115a0021ac99b7df8d13c2a3076dd57bd` | **the blob this record describes** |

**Read this row correctly.** The pre-registration now carries **two** appended addenda, so its blob
hash is NOT the one frozen at `337d4d84`. What is unchanged, and what the freeze rests on, is the
**body**: the first **361 lines** are **byte-identical to the `337d4d84` blob**, verified by
`diff` against `git show`, and both addenda are pure appends at the foot carrying
`lines whose number changed above this section: 0`. **No gate, threshold, cap or label has moved.**

Frozen at **`337d4d84`** — *"D7 ARMED: pre-registration FROZEN and NOT LAUNCHED"*. The body is
unmodified; Addendum 1 is appended at the foot with `lines whose number changed above this
section: 0`, verified by byte-comparing the first 361 lines against the HEAD blob.

`scripts/check_comparator_freeze.py` **does not apply to this item** — it enforces the comparator
freeze for the T-family/closure comparator pattern, and D7's equivalent is the launcher's per-launch
md5 re-assertion on the staged copies plus the FD producer's exec-the-frozen-producer construction.
Stated rather than silently skipped.

## 2. Instruments, frozen and committed before the first container

| instrument | md5 |
|---|---|
| `d7_opt_runScript.py` | `e43902ed2cfc99022c6e21e075f88695` |
| `d7_extract_endpoint.py` | `651d40c78cc52288a856934c108d1334` |
| `d7_fd_endpoint.py` | `92b3fa8d20a41da029590ed3bdde4203` |
| `d7_run_arm.sh` | `c55b2cdeaf8a0975641b491b24912d63` |
| `d7_grade.py` | **`10eb6d0928addc56272854f017e01538`** — re-registered at Addendum 2 |

Grader: **65 selftest units, all passing; gate coverage 14 of 14 emitted gates, 0 unexercised**
(15 groups, `DEF2` added); demonstrated able to **fail** against **sixteen** deliberately broken
graders, **all exit 3**, while the unmutated grader exits 0.

**Two corrections to what an earlier draft of this record asserted, both measured:**

* `check_grader_self_blindness.py` reports **1 ERROR, not 0** — and reported it on the pre-repair
  grader too, so it is a mis-statement being corrected, not damage from the repairs. It also
  **exits 0 while printing `[ERROR]`**, so its exit code does not gate. Every read site it flags
  is inside the selftest's own fixtures; the production path was probed directly instead.
* The grader carried **two further defects**, both found by running it rather than reading it:
  **`D7-GRADER-DEF-2`**, the D4-DEF-3 uncaught-crash class, live in **four** places — including
  inside `g6_plant`, the gate Addendum 1 presents as defended, where `rows` given as a JSON
  **object** passed the truthy `.get()` guard and raised `AttributeError`; and
  **`D7-GRADER-DEF-3`**, `g11_oom` returning **`pass=True` for an arm that never ran**. Both are
  repaired, both refuse by name, and both repairs are mutation-tested.

Detail: `PREREGISTRATION.md` Addendum 1 §A1.7–§A1.8 and **Addendum 2 §A2.1–§A2.5**.

## 3. Staged configuration — by copy, never edited in place

Run root **`/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin`**, staged from
`/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1`.

| identity | value |
|---|---|
| mesh `constant/polyMesh/owner.gz` md5 | `7e847a4f94e8855c89320c784bed96e6` — byte-identical to A3 rung 2 |
| cells (birth certificate) | **42,120**, verdict `clean`, pyHyp N=28 |
| `system/decomposeParDict` md5 | `1dbd9ead3f40a29f483444dc5fa1288b` — byte-identical to A3 rung 2 |
| **decomposition, PINNED** | `method scotch`, `numberOfSubdomains 4` |
| cold state | no `processor*`, no time dir, no `reports/`, no colouring cache, no `OptView.hst` |

**On "seed".** OpenFOAM's `scotchDecomp` exposes **no seed parameter**. There is no number to pin,
and determinism is **not asserted** — what is pinned is the *method* and the *subdomain count*, in a
file byte-identical to the one under which A3 rung 2's FD reference was measured. **Gate G8
DEMONSTRATES determinism** by running `decomposePar -force` twice and comparing the four cell
counts, which must be identical and must sum to 42,120. **If they differ, every np=4 number in this
item is `NOT A RESULT`** — registered in `PREREGISTRATION.md` §5, before the run.

## 4. Age datum

The launcher touches `0/*` **last** at stage time and writes `stat -c %Y 0/U` to
`<arm>/.d7_age_datum`. Every graded artifact must be **strictly newer** than that datum or G1
returns `NOT A RESULT`. `CLAUDE.md` rule 4's thermal field list is the T-family's and does not
apply here; `PREREGISTRATION.md` §7 G1 says so and this item does not pretend to it.

## 5. Memory: threshold stated, then measured

**Threshold, written before the reading it gates** (Addendum 1 §A1.4): **MemAvailable ≥ 16.0 GiB**
for the 12g arms (P2, O, F-S, F-P), **≥ 6.0 GiB** for the 4g arm P1. Enforced in the launcher with a
real refusal path (**exit 5**, before any rank is claimed).

**Measured at 2026-08-25T20:47:26Z, immediately before launch: MemAvailable = 27.49 GiB, load1 = 3.15.**
Headroom above the 16.0 GiB floor: **11.49 GiB.** **Gate is open.**

**The D4 arm O ranks the brief told me to wait for (pids 2359929–2359932) are GONE** — absent from
the process table at lane start (20:23Z) and at every reading since. **I never touched, killed or
signalled them.** The only solvers on the box are heat-transfer's three
`buoyantBoussinesqSimpleFoam` (pids 2203927 / 2203944 / 2203947) on cores 5, 14, 15 — **not
touched**, and the chosen cpuset `2,3,4,6` is disjoint from them.

**No mid-run memory stop is registered**, and that is deliberate: A3 rung 2 registered one with no
enforcement path and its own `RESULTS.md` §9.1 records that it did not fire — *"A stop rule with no
enforcement path is a preference, not a control."* The in-run host-memory sampler here is
**record-only and declared record-only**.

## 6. Arm order, and the gates between arms

| # | arm | image row | np | cap (core-min) | mem | what it must produce before the next arm may run |
|---|---|---|---|---|---|---|
| 1 | **P1** | SHIPPED | 4 | 8.0 | 4g | `d7_decomp_{A,B}.json` for G8; four `d7_placement_rank*.json` for G12 |
| 2 | **P2** | SHIPPED | 4 | 60.0 | 12g | `d7_baseline.json` (**the measured CL the driver's constraint is set from**) and the colouring cache |
| 3 | **O** | SHIPPED | 4 | 600.0 | 12g | `opt_IPOPT.txt`, `OptView.hst` |
| 4 | **F-S** | SHIPPED | 4 | 130.0 | 12g | `d7_fd_endpoint.json` (shipped row) |
| 5 | **F-P** | **PATCHED** | 4 | 130.0 | 12g | `d7_fd_endpoint.json` (patched row) |

**Item ceiling 928.0 core-min; prediction 791.5.** Cost constraints are **LIFTED** (Sanaa,
2026-08-25) and **the caps are RUNAWAY GUARDS**: the launcher writes `cap_exceeded=YES|no` into
the ledger, and a crossing is **reported to the dafoam-supervisor, who decides**. This lane does not
silently continue and does not silently stop.

**Arm P2 GATES arm O** (`PREREGISTRATION.md` §8): if P2 exceeds 60.0 core-min, or the kernel
reports `OOMKilled true`, or G12's placement check fails on P1 or P2, **arm O is not launched**,
and it is **never launched at a raised cap** — the cap does not move to fit the estimate.

**The CL target is derived, never typed.** The launcher reads `P2/d7_baseline.json` — the CL the
baseline primal actually produced — and writes `O/d7_cl_target.json` **at stage time, before the
driver container starts**. The producer **refuses to run `run_driver` at all** if that file is
absent (exit 2). `PREREGISTRATION.md` §1 forbids the typed-in value, and A3 rung 2's own script
carries `CL_target = 0.270` as a literal — precisely the thing not done here.

## 7. Scope fences, restated because they bind this lane

* **The 399,360-cell campaign stays `BLOCKED` and D7 DOES NOT TOUCH IT.** No arm reads, writes,
  stages or references that mesh. Scope drift toward it is a **defect of this item**, not an
  opportunity.
* **A3 rung 3's conditioning `GATE FAIL` STANDS and is NOT re-opened.** D7 runs at rung 2 precisely
  because rung 3 is where the adjoint conditioning failed. **Nothing in D7 may be read as evidence
  about rung 3, in either direction.**
* **D7 is an OPTIMISATION; A3 rung 2 was a GRADIENT VERIFICATION. No verdict of A3 rung 2 is
  inherited** as an optimisation result.
* **The optimum is a ONE-ROW (shipped) statement.** The endpoint gradient table is two-row and is
  therefore a verdict about DAFoam; **the optimum is not**, and D5, D6 and D14 must not read it as
  toolchain-independent. The patched-row optimisation is **`PENDING`** — not run, not failed.

## 8. Registered expectation, so it cannot be re-told afterwards

`PREREGISTRATION.md` §11 P1 registers **in advance** that IPOPT will **not** print
`EXIT: Optimal Solution Found.` within `max_iter` 30, i.e. **D7 is EXPECTED to cap-stop, and its
ceiling verdict is `GATE REACHED`** (`DAFOAM_CHARTER.md` §9: a cap-stop is `GATE REACHED` or
`NOT A RESULT`, **never `PASS`**).

Both directions bind: **if it cap-stops, nobody may present that as an expectation met** — it was
predicted, and a prediction is scored, not celebrated. **If it converges, that is a genuine surprise
and must be reported as one.** The grader emits the `SURPRISE` field on the converged branch for
exactly that reason, and the mapping is exercised by selftest units
`CAPSTOP_never_PASS` and `CONVERGED_is_PASS_and_flagged_a_SURPRISE`.

## 9. What this record cannot tell you

* **Nothing has been measured yet.** Every number above is an identity, a threshold or a
  prediction. There is **no result in this file** and none may be quoted from it.
* Whether the colouring inheritance is sound rests entirely on **G8**, which has not run.
* Whether the four ranks actually land on four distinct cores rests on **G12**, which has not run.
  Until it does, **no adjoint-conditioning finding may be drawn from this item** — a slow adjoint at
  np=4 reads exactly like GMRES stagnation, which is a real failure mode measured on this ladder at
  N=52.
