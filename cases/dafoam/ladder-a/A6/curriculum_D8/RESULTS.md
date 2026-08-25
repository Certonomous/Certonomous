# Curriculum D8 — A6 CRM wing-alone, N=16, twist-only constrained drag minimisation — RESULTS

**Graded and closed 2026-08-25 by the DAFoam team's D8 CLOSE lane.**
Grades against `PREREGISTRATION.md`, frozen at commit `70d1a3d4` **before either solver arm launched**.
This file does not revise that document; departures are dated sections here (§9).

**Nothing in this item is filed, sent, uploaded, posted, registered or pushed anywhere.
SUBMISSIONS ARE PARKED and sending is Sanaa's decision alone** (CLAUDE.md rule 7; `DAFOAM_CHARTER.md` §10).

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/`.

---

## 0. THE VERDICT

> ## `GATE REACHED`
>
> **The rung is graded and closed. Every physics and gradient gate PASSES. The rung as a whole is
> `GATE REACHED`, not `PASS`, and the reason is `G1`: the optimiser stopped at its registered
> 3-major cap with `EXIT: Maximum Number of Iterations Exceeded.`, not at `EXIT: Optimal Solution
> Found.`**
>
> `PREREGISTRATION.md` §7 fixed that mapping before compute — *"Stop at the registered 3-major cap
> ⇒ **GATE REACHED**, never `PASS` — a stop is not a measurement"* — and it is honoured here even
> though every other gate cleared with room. **The design this item verifies a gradient at is a
> 3-major waypoint, not an optimum, and no reader may take it for one.**
>
> **The bright line is satisfied.** `DAFOAM_CHARTER.md` §2: *a DAFoam gradient is not a result until
> a finite-difference table stands beside it at a step proved to lie in the plateau.* The table is
> §2 below, the plateau is **measured** in §1 and not asserted, and the endpoint adjoint of this
> item is therefore a result — **for 8 of 9 components, by construction, on the patched toolchain
> only.**

| gate | band, frozen before compute | measured | verdict |
|---|---|---|---|
| **G0** identity / activity | image ID, `IDWARP_SO_MD5`, `nProcs : 1`, `transonicPCOption 1;`, 41,760 cells | all six checks OK | **PASS** |
| **G1** optimiser termination | `EXIT: Optimal Solution Found.` ⇒ PASS; 3-major cap ⇒ GATE REACHED | `EXIT: Maximum Number of Iterations Exceeded.`, `D8_OPT_ARM_COMPLETE`, rc 0, not OOM-killed | **GATE REACHED** |
| **G2** CL feasibility | `\|CL−0.5\| ≤ 5.0e-03` | **1.142427e-05** — 438× inside the band | **PASS** |
| **G3** drag reduction | drop ≥ 10 η = **1.0910e-04** | **+1.113404e-04** (−0.2871 % of CD) | **PASS** |
| **G4** endpoint FD-vs-adjoint | aggregate ≤ 5.0 %, per-component ≤ 10.0 %, zero sign flips | **0.6852 %** aggregate, worst **2.6497 %**, **0** flips | **PASS** |
| **G5** plateau | `\|d(s_hi)−d(s_lo)\|/\|d(s_hi)\| ≤ 10.0 %` per component | worst **6.78 %**, **zero** failures of 8 | **PASS** |
| **G6** adjoint memory envelope | peak RSS ≤ 11.0 GiB, cap 12 GiB | **9.970 GiB** over 327 samples, **uncensored** | **PASS** |
| **G7** clearance | `C = 2·\|J_fd\|·s/η ≥ 5` on the **measured** `\|J_fd\|` | min **16.09×** | **PASS** |
| **P-BASE** | cold CD **exactly** `0.03506349413916734` | `0.03506349413916734`, exact to all 17 digits | **PASS** |
| **P-η endpoint** | within ±50 % of `1.0910e-05` | **1.0795e-05**, ratio **0.989** | **PASS** |
| **`twist` idx6** | named FD-ungradeable **in advance** (§6 of the pre-registration) | **not measured**, excluded by name from every table and aggregate | **NOT A RESULT** |
| **shipped toolchain row** | registered **NOT BOUGHT** (§10 of the pre-registration) | not run | **PENDING** |

**Machine-readable:** `/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/d8_grade.json`.

### 0.1 `twist` idx6 — NOT A RESULT, and the rung is NOT downgraded for it

`PREREGISTRATION.md` §6 named `twist` idx6 `NOT A RESULT` **before any solver arm ran**, because it
is FD-ungradeable on this rung: no finite-difference reference exists at any feasible step, its
plateau disagreement is **83.53 %** against a 10 % bar and its best clearance **2.42×** against a bar
of 5 (`../rung_n16_remaining_components/RESULTS.md` §4.1 row 9 — the row 37 the curriculum names).

It is **not measured**, not merely omitted: `fdplan.json` contains no entry for it and no perturbed
primal was ever spent on it. It appears in §2's table **by name, with its adjoint value and an
explicit "not measured"**, so it is neither quietly dropped nor smuggled into an average.

**The endpoint gradient verification of this item is therefore 8-of-9 BY CONSTRUCTION. This item does
not claim a 9-of-9 gradient on A6 N=16 and no reader may take G4 as one.** The flagged-component gap
is a registered boundary of the case; this run neither repairs it nor is penalised for it.

**It was offered a rescue and refused one.** §4.1 of the pre-registration extended the twist ladder
to `{3e-2 … 1e0}` for legitimate reasons (near an optimum the reduced gradient shrinks), and on that
extended ladder idx6's stored `|J_adj| = 1.3619e-04` would nominally reach `C ≥ 5` at step `3e-1`.
It was **excluded anyway, by name, before compute**. Keeping a component the ladder extension had just
brought into reach is exactly the failure L-233's corollary names, and *a flag honoured only when it
is cheap is not a flag*.

---

## 1. The plateau — MEASURED, not asserted

`DAFOAM_CHARTER.md` §2 requires the step be **proved** to lie in the plateau, and
`VERIFICATION_CHARTER.md` §7 protocol step 1 requires a two- or three-point mini-sweep, *"not
assumed"*. Every one of the 8 gradeable components was evaluated at **two** registered steps —
16 plan entries, 32 perturbed central-difference primals — and the sweep is reported in full,
including the step that is **not** graded. **No component was graded at a step it was the only
measurement of.**

### T1 — the plateau, MEASURED: the two-point mini-sweep every graded step rests on

| DV, idx | `s_lo` | `J_fd(s_lo)` | `s_hi` (**graded**) | `J_fd(s_hi)` | plateau `\|Δ\|/\|J_fd(s_hi)\|` | bar | verdict |
|---|---|---|---|---|---|---|---|
| `patchV` 0 | 0.1 | `+8.766295e-04` | **0.3** | `+8.652197e-04` | **1.32 %** | 10 % | PASS |
| `patchV` 1 | 0.01 | `+1.048831e-02` | **0.03** | `+1.050520e-02` | **0.16 %** | 10 % | PASS |
| `twist` 0 | 0.03 | `-2.341835e-03` | **0.1** | `-2.301362e-03` | **1.76 %** | 10 % | PASS |
| `twist` 1 | 0.03 | `-1.999274e-03` | **0.1** | `-1.926549e-03` | **3.77 %** | 10 % | PASS |
| `twist` 2 | 0.03 | `-1.818252e-03` | **0.1** | `-1.729390e-03` | **5.14 %** | 10 % | PASS |
| `twist` 3 | 0.03 | `-1.293520e-03` | **0.1** | `-1.276781e-03` | **1.31 %** | 10 % | PASS |
| `twist` 4 | 0.05 | `-8.180548e-04` | **0.1** | `-8.775162e-04` | **6.78 %** | 10 % | PASS |
| `twist` 5 | 0.1 | `-5.412680e-04` | **0.2** | `-5.280005e-04` | **2.51 %** | 10 % | PASS |

**The graded step is `s_hi`, and it was NOT selected on agreement.** `PREREGISTRATION.md` §4.1 fixes
the rule mechanically: `s_lo` is the smallest ladder rung reaching clearance `C ≥ 5`, `s_hi` the
smallest rung with `s_hi ≥ 2·s_lo`, and `s_hi` is graded. `d8_stepplan.py` is the sole producer of
`fdplan.json` from the logged adjoints and the registered η — **a human chose no step here.**

**Re-derived and verified at grading time.** I rebuilt the adjoint column from `opt.log`'s nine
`ADJ_DERIV` lines (not from the stored `d8_adj.json`; the rebuild is byte-equal to it) and re-ran the
frozen `d8_stepplan.py` on it. The re-derived plan is an **exact match** to the `fdplan.json` that
drove the arm — 16 entries, 32 perturbed primals, `PLANNED_COMPONENTS 8 of 8 gradeable`,
`EXCLUDED_BY_NAME_IN_ADVANCE [('twist', 6)]`. **The plan that ran is the plan the frozen arithmetic
produces.** Its own selftest reproduces the rem item's registered `{s_lo, s_hi}` pairs exactly and
refuses a negative control at `J = 1e-9`.

**What this plateau evidence does and does not establish.** Two points bound the step-sensitivity of
the FD reference; they do not demonstrate an asymptotic truncation regime, and this record does not
claim one (`VERIFICATION_CHARTER.md` §3.4's distinction, applied to a step sweep rather than a mesh
ladder). The registered bar is a 10 % two-point agreement and every component clears it; the largest
disagreement, `twist` idx4 at **6.78 %**, is the one closest to the bar and is named rather than
averaged away.

## 2. The bright line — the FD table BESIDE the adjoint gradient

### T2 — the bright line: endpoint FD table BESIDE the endpoint adjoint

| DV, idx | adjoint `J_adj` | FD `J_fd` @ graded step | abs error | rel error `\|J_adj−J_fd\|/\|J_fd\|` | clearance `C` | sign |
|---|---|---|---|---|---|---|
| `patchV` 0 | `+8.7228404434e-04` | `+8.6521973925e-04` @ 0.3 | `7.064e-06` | **0.816 %** | 47.58× | SAME |
| `patchV` 1 | `+1.0564077197e-02` | `+1.0505198960e-02` @ 0.03 | `5.888e-05` | **0.560 %** | 57.77× | SAME |
| `twist` 0 | `-2.3148087247e-03` | `-2.3013615171e-03` @ 0.1 | `1.345e-05` | **0.584 %** | 42.19× | SAME |
| `twist` 1 | `-1.9664348694e-03` | `-1.9265489358e-03` @ 0.1 | `3.989e-05` | **2.070 %** | 35.32× | SAME |
| `twist` 2 | `-1.7271445367e-03` | `-1.7293895778e-03` @ 0.1 | `2.245e-06` | **0.130 %** | 31.70× | SAME |
| `twist` 3 | `-1.2841462263e-03` | `-1.2767806310e-03` @ 0.1 | `7.366e-06` | **0.577 %** | 23.41× | SAME |
| `twist` 4 | `-8.5846864405e-04` | `-8.7751616035e-04` @ 0.1 | `1.905e-05` | **2.171 %** | 16.09× | SAME |
| `twist` 5 | `-5.4199076613e-04` | `-5.2800054482e-04` @ 0.2 | `1.399e-05` | **2.650 %** | 19.36× | SAME |
| `twist` **6** | `-1.9671544286e-04` | — **not measured** | — | — | — | — |

**Aggregate vector-relative error over the 8 gradeable components = `0.6852 %`** (band 5.0 %). Worst component `2.6497 %` (band 10.0 %). Sign flips **0**. Min clearance **16.09×** (bar 5×).

**Definitions, as the frozen grader computes them** (`d8_grade.py::gate_fd`), stated because a
denominator is a choice: per-component `rel = |J_adj − J_fd(s_hi)| / |J_fd(s_hi)|`; aggregate
`= ‖J_adj − J_fd‖₂ / ‖J_fd‖₂` over the 8 gradeable components; clearance `C = 2·|J_fd(s_hi)|·s_hi/η`
on the **measured** FD derivative, not on the adjoint proxy. **The finite difference is the reference
and the adjoint is the quantity under test**, so the FD value is the denominator throughout.

**The two independent sources.** The adjoint column comes from arm `opt`'s final `compute_totals`
(container `d8_opt_20260825T165153Z_2230005`); the FD column from arm `fd`'s 32 perturbed primals in
a **separate container** (`d8_fd_20260825T182022Z_2376204`) that reads only `fdplan.json` and the
endpoint design. Neither column is computed from the other.

**Referent, per `VERIFICATION_CHARTER.md` §6a:** this verdict is **SELF-REFERENTIAL to the DAFoam
stack** — a finite-difference of the same `DARhoSimpleCFoam` primal that the adjoint linearises,
inside the same image. It is a check that DAFoam's discrete adjoint is consistent with DAFoam's own
primal. **It is NOT a comparison against an external solver, an analytic gradient or a published
value, and it must not be read as one.**

## 3. Physics and the optimisation, stated as the waypoint it is

| quantity | start | endpoint | artifact |
|---|---|---|---|
| cold baseline CD (twist-only edit inert) | `0.03506349413916734` | — | `opt.log`, `D8_COLD_CD` |
| trimmed start CD | `0.03877565033718443` | — | `d8_start_dvs.json` |
| **CD** | `0.03877565033718443` | **`0.03866430994135252`** | `opt.log`, `D8_FINAL_CD` |
| **CL** (target 0.5) | `0.4998809292514875` | **`0.49998857573476463`** | `opt.log`, `D8_FINAL_CL` |
| `twist` (deg) | all zero | `[+0.4515, +0.1427, −0.1810, −0.5388, −0.6959, −0.6284, −0.2127]` | `d8_dvs.json` |
| `patchV` (U0, AoA) | `[295.0, 2.4916°]` | `[295.0, 2.4292°]` | `d8_dvs.json` |

**G3 passes and its margin is small enough to state as an interval rather than a headline.** The drop
is `+1.113404e-04` against a threshold of `1.0910e-04`, a margin of **0.2054 η** — about one fifth of
the same-design CD spread this item independently measured (§4). The verdict is `PASS`; the interval
says how much room it has, and a reader should take the drag reduction as *resolvable by this
instrument*, not as a large aerodynamic gain. **0.2871 % on a 3-major stop is a waypoint, not an
optimised wing.**

**P-BASE is the sharpest single check in this item.** The twist-only edit removed the `shape` FFD
group and its LE/TE linear constraints from the tutorial problem. If that edit had perturbed the
primal at all, the stored gradient column would no longer describe this configuration and G4 would be
`NOT A RESULT` by registration. The cold CD reproduced `0.03506349413916734` — **exact to all 17
digits, against five prior independent reproductions.** The edit is numerically inert, demonstrated.

## 4. η independently corroborated across a container boundary

CD has now been evaluated **three times at the identical endpoint design**, twice inside the `opt`
container and once in a fresh `fd` container: `0.03866430994135252` (`D8_FINAL_CD`),
`0.03865796797318573` (`D8_ADJPOINT_CD`), `0.03865353428107418` (`FD_BASELINE_CD`). The spread is
**1.0776e-05 = 0.988 η**, and the grader's independent endpoint reading of the last-200 peak-to-peak
is **1.0795e-05 = 0.989 η**. The registered noise floor `1.0910e-05` (N-D13) is therefore reproduced
to **ratio 0.988–0.989 across a container boundary** — a genuine independent check of η, not a
restatement of it.

## 5. Arm completion — the strict rule, clause by clause, on BOTH arms

| clause | arm `opt` | arm `fd` |
|---|---|---|
| `rc = 0` | **0** | **0** |
| `End` line | present | **33** — exactly one per primal |
| last time == `endTime` (1000) | yes | yes; highest written dir `1000/` |
| fields present at `endTime` | `DARhoSimpleCFoam` set | `T U p nut nuTilda alphat rho phi` |
| `ExecutionTime` count == `endTime` *(generalised)* | — | **3,333** = 33 × (1000/10 + 1) at `printInterval 10`, **exact** |
| **age guard** | — | newest `0/` file vs **oldest** `endTime` field: **+87 s** |
| arm marker | `D8_OPT_ARM_COMPLETE` | `D8_FD_ARM_COMPLETE` |
| `ASSERT_MD5 OK` | present | present |
| G8 cold-start guard | fired OK | `G8 OK (fd): no written time dirs, no processor*, no reports/, 0/ present` |
| OOM / cap-kill | `inspect=[0 false]`, `peak_rss 9.97 GiB` | `inspect=[0 false]`, `peak_rss 0.658 GiB` |

**Two clauses are stated in generalised form and the generalisation is disclosed rather than
assumed.** CLAUDE.md rule 4 is written for a single OpenFOAM solve; arm `fd` is **33 primals in one
container** (1 baseline + 8 × 2 steps × 2 signs). The `ExecutionTime` count is the strongest check
here: **3,333 is not a number reachable by accident** — a primal that stalled short, or a 32nd
perturbation that never launched, moves it off 3,333. It landed exactly.

**One age-guard subtlety, disclosed rather than glossed.** `fd/0/U.gz` carries mtime `19:02`, later
than its five siblings at `18:20`, because the FD loop rewrites the inlet BC in `0/U` for each
`patchV` perturbation. The guard is satisfied **strictly**: I compared the **newest** `0/` file
against the **oldest** `endTime` field, not the convenient pair, and the margin is +87 s.

**Neither arm was cap-stopped by its container.** Arm `fd` ran under `timeout 4500` and finished in
**2,602 s — 57.8 % of the cap, with 1,898 s unspent.** The hard kill at ~19:35Z was never approached.
The `GATE REACHED` verdict comes from the **registered 3-major IPOPT cap**, an optimiser stop, not
from a wall-clock stop.

## 6. THE TWO-ROW RULE — one row is bought, the other is named unbought

`DAFOAM_CHARTER.md` §6: **a DAFoam verdict is two rows — shipped and patched — or it is not a verdict
about DAFoam.** Both rows are printed here. The second is `PENDING`, and `PENDING` is a named,
priced state, never an absence.

| row | toolchain | image ID | IDWarp `.so` md5 | G4 result | verdict |
|---|---|---|---|---|---|
| **PATCHED — BOUGHT** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425`, printed **by the running container** and asserted (`ASSERT_MD5 OK`) | aggregate **0.6852 %**, worst **2.6497 %**, **0** sign flips, 8 of 9 | **PASS** |
| **SHIPPED — NOT BOUGHT** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` (**stock** IDWarp, no rotation patch) | **not run** | **PENDING** — price **~147 core-min / ~$0.126 derived** |

**This row is live, not academic, and that is exactly why it must be printed.** `twist` DVs cross the
IDWarp warp, which is the component the rotation patch changes, and A6 N=16's existing gradient row
is already **`GATE FAIL` (shipped) / `PASS` at 8 of 9 (patched)**. The two toolchains are known to
disagree on this configuration.

**Why it was not bought, registered in advance** (`PREREGISTRATION.md` §10): (i) **memory** — two
adjoint-bearing arms cannot run concurrently, `2 × 9.787 = 19.6 GiB` would leave under 9 GiB and
breach the standing 12 GiB `MemAvailable` floor, so a second row is strictly sequential and doubles a
~2.5 h item; (ii) **grading** — the endpoint FD step rule is seeded from the patched adjoint column
and the 8-of-9 reference this item measures against is itself a patched-image row, so a shipped row
needs its own seeded plan and its own reference.

> **CONSEQUENCE, STATED PLAINLY: THIS ITEM CANNOT AND DOES NOT CLAIM A TOOLCHAIN-INDEPENDENT RESULT.**
> G4's `PASS` is a statement about DAFoam **with the IDWarp rotation patch applied**, and about
> nothing else. It says nothing about stock DAFoam on this configuration, where the existing evidence
> points the other way.

**Levers verified ACTIVE, not merely configured** (`VERIFICATION_CHARTER.md` §9, L-40):
`transonicPCOption 1;` in the runtime option dump of both arms; `nProcs : 1`; `Global Cells: 41760`
in the runtime log **and** `Mesh region0 size: 41760` in the mesh-generation record;
`primalMinResTolDiff 10000;` in the option dump — load-bearing, because the A6 primal stops 556×
short of `primalMinResTol` and without this edit `DASolver::checkPrimalFailure()` kills every primal
in the optimisation.

## 7. Instrument verification — and D8-DEF-2, a defect found BEFORE grading

**The instruments were verified before anything was graded, and the verification earned its keep.**

Three of the four frozen instruments hash **exactly** to `PREREGISTRATION.md` §9, in the working tree
and in the HEAD blob: `d8_gen_arm.py` `0b8a8b3449363287237e8136aaf13128`, `d8_run_arm.sh`
`cd66ead4b0dc1a26e460ea6bcc719551`, `d8_stepplan.py` `8be156d5cff3ef373d3bf359eddcb317`.

`d8_grade.py` differs from its §9 md5 **by its committed amendment (`b8039512`) and by nothing else**,
and that was established mechanically rather than read off the commit message: `diff` against the
untouched v1.0 copy in the run root (md5 `04bba79c2a303bc3cf70af723da81dce`, the §9 value) is **a
single purely-additive hunk `@@ -403,3 +403,182 @@`** — 0 lines removed, 179 appended at the foot —
and `head -405` of the amended file hashes to `04bba79c2a303bc3cf70af723da81dce`. The amendment's own
assertion *"lines whose number changed above this section: 0"* is therefore **arithmetic, not a
claim**, and rule 6 is honoured to the letter.

### 7.1 D8-DEF-2 — AMENDMENT 1 was INERT. Demonstrated, not asserted.

The frozen v1.0 body's last eight lines are its `if __name__ == "__main__":` entrypoint at line 397.
Python executes a module body top to bottom, so running `d8_grade.py` as a script fires that
entrypoint while `main` is **still bound to the v1.0 body**, and `sys.exit(main(sys.argv[1]))` raises
`SystemExit` before the amended `def main` at line 429 is ever evaluated.

**`python3 d8_grade.py <run-root>` exits `rc = 2` with `G0 Mesh region0 size: 41760  FAIL` and
`REFUSE: G0 failed -- the arm is VOID on identity/activity; nothing below is graded`.** That is the
v1.0 label and the v1.0 string — **the exact string AMENDMENT 1 was written to remove**, because no
DAFoam runtime log ever emits it. As committed, the D8 grader **refuses to grade a healthy, completed
rung.** The amendment repaired the gate's *text* and never its *reachability*, and nothing in the
commit demonstrated that the repaired code path executes.

**This is the L-221/L-222 shape one level up: a lesson is not applied until every call site asserts
it — and an amendment is not applied until something proves the amended path is the path that runs.**

### 7.2 The repair edits the frozen instrument by ZERO bytes

The graded quantities now exist, so `VERIFICATION_CHARTER.md` §2d.1 fences repairing the grader:
*nothing a verdict depends on may be repaired on the authority of the verdict it produces.*
**I therefore did not repair the grader.**

`d8_grade_entry.py` imports `d8_grade.py` under a module name that is **not** `__main__`, which skips
the v1.0 entrypoint, lets the module body run to completion, and resolves `main` to the amended v1.1
body — **the same bytes frozen at 17:00Z on 2026-08-25, before either arm had produced a graded
quantity** (arm `opt` ran 16:51:53Z–18:19:24Z; arm `fd` 18:20:22Z–19:03:44Z). **No gate, threshold,
band, cap or label is touched by anything written today; every number above comes out of the
committed blob.**

Three controls, which refuse rather than degrade:

* **C1** — `d8_grade.py` on disk must hash to the HEAD blob `0b1907a994b626d5d869ce159bd181df`.
  An unverified instrument does not grade.
* **C2** — the bound `main` must be defined **below line 405**, i.e. it must be the AMENDMENT 1 body.
  This is the **planted control on the defect itself**, and it is shown able to see the non-zero: the
  direct `python3 d8_grade.py` invocation *is* the v1.0 case, and it fails at G0 with `rc = 2`.
* **C3** — the frozen 405-line prefix must still hash to `04bba79c…`, re-proving AMENDMENT 1's
  append-only property at grading time rather than trusting it.

All three pass, and the tell is in the output: G0 prints the **v1.1 labels** `Global Cells: 41760
(runtime)` and `Mesh region0 size: 41760 (generation record)` where the v1.0 run printed the single
failing `Mesh region0 size: 41760`. **Which labels appear is which `main` ran.**

**Pre-repair values beside the published ones**, as §2d.1 requires: pre-repair the grader produces
**no graded quantity at all** — it refuses at G0 and exits 2. Post-repair it produces the table above.
Nothing moved, because nothing had been produced.

**The planted-zero discipline is intact.** The grader's 18-check selftest with its six negative
controls runs as the amended `main`'s first statement and passes in the same invocation: the FD gate
refuses on a 7-component set, a 0-component set, a 1-step component and an `idx6` leak (the L-302
defect that lets an empty component set report `PASS` at 0.0000 %), and the RSS reader refuses on
missing / empty / unparseable input rather than printing `0.000`.

## 8. THE AGGREGATE SITS BELOW THE CHARTER'S HARNESS-SOUND FLOOR — flagged, not celebrated

`VERIFICATION_CHARTER.md` §7 item 4: *"The harness-sound floor on this stack, for a case with no
flagged components, is 2.5 to 5 percent vector-norm relative error. **A number below that is a claim
about the harness.**"*

**D8's aggregate is 0.6852 %. That is below the floor, and this record does not upgrade it into a
stronger claim about DAFoam.** Stating it plainly rather than presenting a small number as a triumph:

* The excursion is **not new and not specific to D8**. The start-design measurement on this exact
  rung returned **1.0432 %** (`../rung_n16_remaining_components/RESULTS.md` §4.2), also below the
  floor. Two independent measurements, at two different designs, both under 2.5 %.
* **What I can name:** this item grades **only global DVs** — `twist` (rigid section rotation) and
  `patchV` (freestream `U0` and AoA). The tutorial's local `shape` FFD group, which exercises the
  IDWarp warp Jacobian hardest, was **removed** from the problem. `patchV` idx0/idx1 do not warp the
  mesh at all. A gradient chain with less mesh-warp content in it is a plausible reason for tighter
  FD-adjoint agreement than a floor calibrated on a stack containing local shape DVs.
* **What I cannot verify, and say so rather than guess:** the provenance and transferability of the
  2.5–5 % figure are not established anywhere I read in this item, so I cannot demonstrate that it
  was calibrated on a comparable configuration, nor that it is inapplicable here. **The mechanism
  above is an inference, explicitly labelled, and is not upgraded to a statement of fact** (L-22's
  standing wording, applied to a favourable finding rather than a crash).
* **Flagged upward** to the DAFoam supervisor and to the verification team as an open item: either
  the §7 floor needs a configuration qualifier, or this family's agreement needs an explanation.
  **It is not resolved by this rung and this rung does not pretend to resolve it.**

**What this does not do.** It does not withdraw G4. The gate was registered at ≤ 5 % before compute,
the measurement is 0.6852 %, and the verdict is `PASS`. The claim being fenced off is the one nobody
made and every reader is one sentence away from making: that a very small number is very strong
evidence.

**A second, registered self-reference, carried forward verbatim rather than left for a reader to
find** (`PREREGISTRATION.md` §4.1): the graded step is sized from `|J_adj|` — *"the rule has not been
tried where the proxy `|J_adj|` is itself wrong, which is the case it would be worst at, since it
sizes the step from the very quantity under test."* At the endpoint the adjoint had **not** been
verified before the step was sized from it. **A cleanly-passing G4 is therefore partly
self-referential, by registration, and this is stated here as it was stated there.** The partial
mitigation is that G7's clearance is graded on the **measured** `|J_fd|`, not on the proxy, and the
minimum measured clearance is 16.09× against a bar of 5.

## 9. Departures from the frozen pre-registration — dated, and none touches a gate

Three, all disclosed. **None alters a gate, threshold, band, cap or label.**

1. **Arm `fd` container timeout set to 4500 s, not the frozen §8 backstop of 7200 s.** §8 gives arm
   `fd` both a `timeout 7200 s` backstop and a registered ceiling of **75.0 core-min**; at 1 rank
   those disagree, since 7200 s is 120 core-min — **45 core-min above the arm's own registered cap.**
   Running to the backstop would let the arm outlive its budget, and CLAUDE.md rule 12 is explicit
   that an overrun stops the run. The timeout was set to **4500 s = exactly the registered 75.0
   core-min**, making the frozen budget stop mechanical. **This cannot make any gate easier to pass:**
   a shorter arm can only produce a *shorter* FD table, and `gate_fd` refuses on a component count
   ≠ 8. In the event the arm used 57.8 % of it. *(Disclosed by the prior lane, LANE_REPORT §12.)*
2. **The grader was invoked through `d8_grade_entry.py` rather than directly.** §7.2 above; a
   dispatch fix that edits the instrument by zero bytes.
3. **The registered step ladder departs from `VERIFICATION_CHARTER.md` §7 item 5's nominal
   `1e-3 … 1e-2`, and the departure is quantified rather than waved through.** The DVs here are in
   **degrees and m s⁻¹**, not normalised, so the charter's nominal range is not merely different —
   **on this case it is unusable.** At the top of that range, `s = 1e-2`, the *strongest* graded twist
   component reaches clearance **4.22×**, below the bar of 5, and the weakest reaches **0.97×**; at
   `s = 1e-3` they reach **0.42×** and **0.10×**. The CD change would be buried in this case's own
   measured noise floor. The pre-registration therefore froze a **mechanical clearance-driven ladder**
   (§4.1), whose steps are a function of `|J_adj|` and η alone, and whose selftest reproduces the
   prior item's published pairs exactly. **The departure buys measurability, not agreement**, and the
   plateau evidence of §1 is what stands in for the charter's nominal range.

## 10. Cost — measured from the ledger, and calibrated against the frozen prediction

| line | predicted (core-min) | **actual (core-min)** | ratio | basis |
|---|---|---|---|---|
| pre-registration image read | — | **0.217** | — | 13 s × 1 rank, no solver ran |
| arm **`opt`** | 89.3 | **87.517** | **0.980** | 5,251 wall s × 1 rank ÷ 60 |
| arm **`fd`** | 57.8 | **43.367** | **0.750** | 2,602 wall s × 1 rank ÷ 60 |
| **WHOLE RUNG** | **147.3** | **131.101** | **0.890** | ceiling 215.0 — **not breached** |

**$ DERIVED, NOT MEASURED: $0.1121** actual against **$0.1259** predicted, at
`c7a.4xlarge $0.0513/core-h`, **REPORTED-BY-OWNER**. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure in this lab is a measurement.

**Attribution of the 16.2 core-min gap — misprediction, and in the direction the pre-registration
predicted it would err.**

* **Arm `opt`, ratio 0.980:** essentially on prediction. Nothing to attribute.
* **Arm `fd`, ratio 0.750 — the whole gap, and it is one cause.** §8 priced all 33 primals at the
  **cold** 105 s. They ran **warm**: the arm restarts from the converged endpoint field, and the
  measured mean is **78.50 s/primal** (2,590.64 s of solver clock over 33 primals). `78.50 / 105 =
  0.748`, which reproduces the arm ratio 0.750 to three figures. **The gap is one identified
  mechanism, not a residual.** The pre-registration named this exact error in advance: *"it prices
  every primal at the cold 105 s when majors restart warm"*, and cited D1's 0.304× as the precedent
  for erring that way.
* **WASTE: 0.000 core-min, named separately and not absorbed into the ratio** (`COMPUTE_BUDGET_CHARTER.md`
  §6). No arm was relaunched, no arm crashed, no container was killed, no perturbation was recomputed.
  Both arms are `rc = 0` on their first and only launch, and the run root contains exactly two solver
  logs. **The 0.890 ratio is misprediction only.**
* **CONTENTION: none affecting these arms.** The `fd` solver (pid 2376667) held **99.4 %** of its CPU
  with peer containers pinned to other cores; **99.56 %** of its 2,602 wall s is solver-accounted
  (2,590.64 s of `ExecutionTime`), leaving 11.4 s for container start, IDWarp import, mesh read and
  teardown. Core-minutes are reported **gross**, with that check named.

**The mechanical 3600-second stall rule mis-classifies arm `opt` and the row is NOT cleaned by it.**
`COMPUTE_BUDGET_CHARTER.md` §2 defines one cleaning rule — *a ledger row over 3600 wall seconds is an
infrastructure stall, not solver cost* — and `opt` is **5,251 wall s**, so a mechanically-cleaned
figure would be **0.000 core-min**, which is demonstrably false: the container's own solver clock
reaches **5,020.30 s**, so **95.6 %** of the wall is solver-accounted. **The gross figure 87.517 is
the one with evidence behind it.** The rule was calibrated on short OpenFOAM rows; a DAFoam
optimisation arm is one long row by construction. Arm `fd` at 2,602 s is under the threshold and is
not flagged. **Flagged upward, not silently worked around.**

The calibration row is appended to `docs/COST_CALIBRATION.md` under CLAUDE.md rule 12.

## 11. What remains PENDING, and what this item is not

* **The shipped-toolchain row** — `PENDING`, priced at ~147 core-min / ~$0.126 derived (§6).
* **`twist` idx6** — `NOT A RESULT`, FD-ungradeable on this rung, named in advance (§0.1). Not
  repaired here and not claimed.
* **The `shape` local-FFD group** — removed from this problem and **`PENDING` for this family exactly
  as before.** It has never been graded by any item in the A6 line.
* **A6 overall remains `BLOCKED`.** This item does not lift it, does not re-grade, revise or merge any
  existing A6 row, and does not touch **A6 N=29**, which has never run.
* **It does not touch** the 399,360-cell A3 campaign or D16a.
* **The optimisation is a 3-major waypoint, not an optimum** (§0, §3).

**Nothing here is filed, sent, uploaded, posted or registered anywhere. SUBMISSIONS ARE PARKED.**
