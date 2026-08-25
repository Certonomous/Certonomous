# Curriculum D7 — ONERA M6 lift-constrained transonic drag minimisation

**PRE-REGISTRATION — SHORT FORM.** Sanaa authorised the 10-line form on 2026-08-25 for standard
verification/validation cases. D7 is a standard case on a **proven mesh** — A3 rungs 1–2 both
`PASS`. **Her rigor standard is explicitly unchanged**, so every gate, threshold, cap and label
below is frozen at this commit and is closed to change once the first container starts
(`CLAUDE.md` rule 2; `VERIFICATION_CHARTER.md` §2b, §2d).

**STATUS: DRAFTED AND FROZEN. NOT LAUNCHED.** No container has started for this item. Nothing
fires until the dafoam-supervisor has personally read that this pre-registration is committed —
that check is the supervisor's and is not delegated (`SUPERVISION_CHARTER.md` §3).

**Nothing here is sent, filed, uploaded, posted or commented. SUBMISSIONS ARE PARKED and sending
is Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

---

## 1. Case

ONERA M6 wing, transonic, **the A3 rung-2 case and mesh, unchanged**.

| item | value |
|---|---|
| mesh | **42,120 cells** — the A3 sweep rung-2 mesh (`n28`), staged by copy, never edited in place |
| solver | **`DARhoSimpleCFoam`**, `primalMinResTol` 1e-8, `primalMinResTolDiff` 1e4 |
| adjoint | `transonicPCOption 1`, stock ILU(0) (`pcFillLevel 0`), `jacMatReOrdering natural`, `gmresRestart 200`, `gmresRelTol 1e-4`, `gmresMaxIters 2000`, `DAFOAM_SUBPC_TYPE` **unset** — **A3 rung 2's own adjoint configuration, quoted not chosen** |
| ranks | **np = 4** |
| design variables | `twist` **5**, `shape` **120** (FFD), `patchV` **2** (`U0` fixed at both bounds, so AoA is the only free component) — the A3 rung-2 DV set, whose sizes are read from that rung's own record (`patchV[1]` of 2, `twist[1]` of 5, `shape[115]` of 120) |
| objective | `CD`, minimise |
| constraint | `CL` equality at the rung-2 baseline `CL`, plus `volcon` ≥ 1.0 and `thickcon` in [0.5, 3.0] — **the target `CL` value is read from the baseline primal at run time and written to a file BEFORE the driver starts; it is not typed into this document from memory** |
| optimiser | IPOPT via pyOptSparse, `tol` 1e-5, `constr_viol_tol` 1e-5, **`max_iter` 30** (see §8 — this is a COST-DERIVED cap and its consequence is registered in §7), `mu_strategy` adaptive, L-BFGS history 10 |
| run root | `/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/` |

## 1a. Scope fences — registered, not discovered later

* **The 399,360-cell campaign stays `BLOCKED` and THIS CASE DOES NOT TOUCH IT.** No arm of D7
  reads, writes, stages or references that mesh. Scope drift toward it is a defect of this item,
  not an opportunity.
* **A3 rung 3's conditioning `GATE FAIL` STANDS as the known boundary and is NOT re-opened.**
  D7 runs at rung 2 (42,120 cells) precisely because rung 3 is where the adjoint conditioning
  failed. Nothing in D7 may be read as evidence about rung 3, in either direction.
* D7 is an **optimisation**. A3 rung 2 was a **gradient verification**. No verdict of A3 rung 2
  is inherited as an optimisation result.

## 2. Reference and cost anchors — ALL from THIS mesh at THIS rank count

**Every anchor is A3 rung 2's own measurement at 42,120 cells, np=4.** `DAFOAM_CHARTER.md` §5:
an FD reference is part of a **configuration**, not a property of a case. **No price is invented
across case classes** — in particular D4's A2 anchors (38,304 cells, incompressible wing) are
**NOT used**, because this case has its own.

| anchor | value | source |
|---|---|---|
| A3 rung-2 verdict | **`PASS` / `PASS`**, both rows | `cases/dafoam/ladder-a/A3/rung2_patched_idwarp_np4/RESULTS.md` |
| arm P-A `fd3`, np=4 | **955 s wall = 63.667 core-min** | same, §8 ledger |
| arm P-B `fd1wrong`, np=4 | **152 s wall = 10.133 core-min** | same |
| **adjoint (one `compute_totals`)** | **≈ 204 s = 13.60 core-min** | same, §5 note: *"The adjoint is ~204 s of the fd3 cost"* |
| **one primal** | **≈ 50.7 s = 3.38 core-min** | **DERIVED**, and the derivation is stated: arm P-B's 152 s covers 1 cold primal + a central FD at 1e-8 on `patchV[1]` = **3 primals**, so 152 ÷ 3. **The three-primal count is an ASSUMPTION read from that arm's task definition, not a measured per-primal timing** — it is labelled as such here and arm **P2 re-measures it directly** before the big buy |
| rung-2 total | 85.950 core-min of a 120.0 ceiling, waste 12.150 (14.1 %) | same, §11 |

### 2a. THE CONSEQUENCE THE CURRICULUM'S OWN ESTIMATE DID NOT CONFRONT

`EXPERTISE_CURRICULUM.md` §3 Tier 3 prices D7 at **~600–900 core-min**. Against the anchors
above that range is **not a 100-major budget**, and this is registered **before** any compute
rather than discovered during it:

> per major ≈ **1 adjoint + ~1.5 primals** = `13.60 + 1.5 × 3.38` ≈ **18.7 core-min/major**,
> rounded to **19.0** for prediction.

At 19.0 core-min/major, **600–900 core-min buys 31–47 majors, not 100.** A `max_iter` of 100
would price the optimisation arm at **~1,900 core-min**, more than twice the curriculum's top.

**`max_iter` is therefore registered at 30, derived from the cap and not from taste**, and the
consequence is registered with it in §7 and §11: **D7 is EXPECTED to cap-stop, so its ceiling
verdict is `GATE REACHED`.** A `PASS` would require IPOPT to print `EXIT: Optimal Solution
Found.` within **30** majors on a shock-dominated transonic problem, and **that is registered
here as UNLIKELY, in advance** — so that if it does not happen, nobody may present the cap-stop
as an expectation that was met, and if it does happen it is a genuine surprise on the record.

## 3. Quantities measured

Final `CD`; per-major `|CL − CL_target|`; major count; the IPOPT `EXIT` line verbatim; `inf_pr`
and `inf_du` per major; **the adjoint's own convergence per major** (`PetscConvergedReason` and
the terminal KSP residual, from the arm log); the endpoint FD table over the five components of
§6, **on BOTH toolchain rows**; peak container memory and the kernel's `OOMKilled` bit; wall
seconds, ranks and core-minutes per arm from the launcher's ledger; delivered cores per MPI arm.

## 4. Bands — FROZEN BEFORE COMPUTE

| id | band | value |
|---|---|---|
| **A** | `CL` feasibility, **every** major | `\|CL − CL_target\| ≤ 5.0e-4` |
| **B** | `CL` feasibility, **final** major | `\|CL − CL_target\| ≤ 1.0e-5` (IPOPT's own `constr_viol_tol`) |
| **C** | drag reduction `(CD₀ − CD_f)/CD₀` | **[3 %, 25 %]**, prediction **10 %** |
| **D** | endpoint FD agreement, **per graded component** and **in aggregate** | **≤ 5.0 %**, and **zero sign flips** among graded components |
| **E** | plateau, per component | `\|d(s_hi) − d(s_lo)\| / \|d(s_hi)\| ≤ 10 %` |
| **F** | adjoint health, **every** major | `PetscConvergedReason > 0`; **any `-9`-class reason is `BLOCKED`, never skipped** |

**Band C's basis, and why it is far below D4's.** D4's A2 band was [25, 45] % because A2 is an
incompressible wing at fixed `CL` with 104 free DVs and a 47-major precedent reaching 28.275 %.
**M6 is a transonic shock-dominated case being given 30 majors, not 100**, and shock-driven wave
drag does not yield to twist-and-shape the way induced drag does. **[3, 25] is wide on purpose,
it is frozen here, and a result outside it is reported as a MISS, never re-banded.**

## 5. Ladder, decomposition, seed and placement — PINNED BEFORE COMPUTE

**Decomposition: `scotch`, `numberOfSubdomains 4`**, from the case's own `system/decomposeParDict`
staged unchanged from A3 rung 2 — so this run's partition is the configuration under which that
rung's FD reference was measured.

**Honest statement of what "seed" means here.** OpenFOAM's `scotchDecomp` exposes **no seed
parameter**; there is no number to pin, and determinism is **not by construction and is not
asserted**. Gate **G8** DEMONSTRATES it: arm P1 runs `decomposePar -force` twice on the same
staged mesh and compares the four `processorN` cell counts, which must be identical and must sum
to **42,120**. **If they differ, G8 is `GATE FAIL` and every np=4 number in this item is
`NOT A RESULT`** — registered here, before the run.

**Registered limitation, not a discovery.** `DAFOAM_CHARTER.md` §5 requires a *new* case's first
FD verification at np=1 before any parallel figure is graded. **A3 rung 2 is not a new case** —
its np=4-`scotch` FD reference exists and is graded. **This item does not buy an np=1 arm**, and
the consequence is stated in advance: **D7's endpoint FD table is a statement about
np=4-`scotch` and is never carried to another np.** §5's own measurement is why: on A4, np=4
`scotch` read 8.95 % and np=4 `simple` 4×1×1 read 0.00054 % — a factor of **16,600**.

**CPU placement — PINNED, and MEASURED afterwards.** `mpirun` inside a `--cpus=N` container binds
rank 0 to the first core of the host topology; concurrent containers collide there and throughput
collapses as `1/N` while the box reports itself idle (MEASURED, D13 lane, 2026-08-25: 0.250 cores
against a 1.0-core quota, host 61 % idle). **`--cpus=4` does NOT hand out four distinct cores.**
**The cpuset is pinned at launch time from a fresh core census, recorded in the launcher's ledger,
and gate G12 then MEASURES it**: four per-rank `sched_getaffinity` FILES (refusing **by count** on
fewer than four), affinity union inside the pinned set, all four ranks on **distinct** single
cores, and **≥ 3.0 of 4 cores delivered** by the passive cgroup sampler. **An absent sample file
is `NOT_MEASURED`, never a passing placement gate.**

**Registered consequence — the false finding this gate exists to prevent.** A slow adjoint at np=4
reads **exactly** like GMRES stagnation, which is a real failure mode **measured on this very
ladder at N=52**. **No adjoint-conditioning finding may be recorded by this item until G12 has
ruled out core contention.** Contention is attributed **separately** from waste and from
misprediction in the calibration row and is **never absorbed into the ratio** (`CLAUDE.md` rule
12; `COMPUTE_BUDGET_CHARTER.md` §6).

**FD step ladder** (§7 selects from it mechanically; no step is hand-picked). **Anchored on A3
rung 2's own measured usable step of `h = 1e-2` with `2h = 2e-2` on this mesh** — NOT on A2's
`1e-3`, which belongs to a different case:

| DV family | ladder |
|---|---|
| `shape` | `3e-3, 1e-2, 3e-2, 1e-1` |
| `twist` | `3e-3, 1e-2, 3e-2, 1e-1, 3e-1` |
| `patchV` | `3e-3, 1e-2, 3e-2, 1e-1, 3e-1` |

**A step that fails to produce a converged primal is recorded as a failed-step row**
(`DAFOAM_CHARTER.md` §3), never dropped. Shock-induced primal fragility at deformed shapes is a
named failure mode for this case, so failed steps are **expected** and their rows are evidence.

## 6. The five components — NAMED IN ADVANCE, with reasons

| # | component | why this one |
|---|---|---|
| 1 | **`shape[115]`** | the component A3 rung 2 graded on **both** rows, and **the one the rotation patch DEGRADED 9.208×** (`0.0172 % → 0.1586 %`). It crosses the mesh-warp chain |
| 2 | **`twist[1]`** | graded on both rows at rung 2 and **degraded 3.39×** by the patch (`0.2740 % → 0.9279 %`); twist is a `rot_z` on the reference axis and crosses the IDWarp rotation path **directly** |
| 3 | **`patchV[1]`** | AoA — the DV the `CL` equality is carried by, and **the control that does NOT cross the warp chain**: at rung 2 it was **bit-identical between the two rows** |
| 4 | **`shape[0]`** | an unflagged control, **chosen by index position (first of 120), not by any prior flag or measured value** |
| 5 | **`shape[119]`** | the second unflagged control, **last of 120** — same mechanical rule |

Components 4 and 5 exist so the set is not composed only of components already known to move.
**Their selection rule is stated so it cannot be re-chosen after seeing the answer.**

### 6a. The consequence, registered before the run

**A component whose measured clearance `C = |J_adj|·s/η` fails to reach 5 at EVERY rung of its
ladder is `NOT A RESULT` for that component.** It is excluded from the aggregate and from the
coverage count, and coverage is reported as **`k of 5`** — never as a percentage over a shrunken
denominator.

**Registered caveat carried VERBATIM from the step-selection rule's own record**
(`A6/rung_n16_remaining_components/RESULTS.md` §3.1):

> *"One item, five components, one case, one eta. The rule has not been tried where the proxy
> `|J_adj|` is itself wrong — which is the case it would be worst at, since it sizes the step
> from the very quantity under test."*

**On a rung whose adjoint is wrong, the `|J_adj|` proxy sizes steps from a wrong number.** That is
the standing limitation and **D7 does not repair it.**

**Registered second-order caveat.** D1-C′ measured that the stock IDWarp `warpDeriv` defect is
**design-point dependent** — 640 % and sign-flipped at the undeformed baseline, unresolvable at
the converged point. **A rung-2 baseline flag therefore predicts nothing about D7's endpoint**,
and this item must not read a clean endpoint as a retraction of the rung-2 finding.

## 7. Criteria and gates

| gate | what it reads | mapping |
|---|---|---|
| **G1** | `rc`, the launcher ledger, the **age guard** | `rc = 0`; the producer's own output FILE terminal; **every graded artifact strictly newer than the case's own `0/U`**, whose mtime the launcher writes to `.d7_age_datum` at stage time. Any stale artifact → **`NOT A RESULT`**. Rule 4's thermal field list is the T-family's and does not apply; it is not pretended to |
| **G2** | `d7_major_history.json` (from `OptView.hst`) | bands A and B → `PASS` else `GATE FAIL` |
| **G3** | `opt_IPOPT.txt` — IPOPT's **own** output file | `EXIT: Optimal Solution Found.` → `PASS`-eligible. **Cap-stop (wall clock, `max_iter`, or budget) → `GATE REACHED` if band C and band A both hold, else `NOT A RESULT`. NEVER `PASS`** (`DAFOAM_CHARTER.md` §9) |
| **G4** | same two files | band C. **On a cap-stop the best available verdict is `GATE REACHED`**, and the item is never graded from the size of its improvement |
| **G5** | `d7_fd_endpoint.json`, **one per toolchain row** | bands D and E. **REFUSES BY COUNT, WITH THE COUNT PRINTED**, on an empty, short, long or reordered component set |
| **G6** | the FD artifact on disk | **planted zero** (rule 3): plant a known perturbation into a graded row, re-read through the SAME reader, refuse if any consumed channel cannot see it |
| **G6b** | — | **negative control**: a blind reader that ignores the path it is handed **must be REFUSED**. A control that cannot refuse is not a control |
| **G7** | — | **count control**: four deliberate mutations — `rows` emptied, shortened to 2, reversed, key removed — each must produce a **NAMED** refusal |
| **G8** | `d7_decomp_A.json`, `d7_decomp_B.json` | decomposition determinism, §5 |
| **G9** | ledger + arm logs | image **digest** and the imported IDWarp `.so` md5 (`DAFOAM_CHARTER.md` §11) — **and, D7 being a two-row item, the TWO rows must show TWO DISTINCT `.so` md5s. Identical md5s across the rows means the A/B never happened and the item is `NOT A RESULT`** |
| **G10** | ledger | **enforced cap == registered cap**, per arm, read back from the ledger the launcher wrote — not from the launcher's claim; and actual ≤ cap |
| **G11** | `docker inspect .State.OOMKilled` | `DAFOAM_CHARTER.md` §7: OOM-killed → **`NOT A RESULT` about convergence**, recorded as stopped by memory |
| **G12** | `d7_placement_rank*.json` (per-rank FILES) + the ledger's delivered-cores column | §5. Refuses **by count** on fewer than 4 rank files. `GATE FAIL` → every np=4 cost figure is **contention-contaminated** and no conditioning finding may be drawn |
| **G13** | **adjoint health per major**, from the arm log | band F. Every major's adjoint solve must report `PetscConvergedReason > 0`. **A `-9`-class reason → `BLOCKED`, RECORDED, NEVER SILENTLY SKIPPED.** A major whose adjoint did not converge cannot contribute a graded gradient, and an optimisation built on one is `NOT A RESULT` |

**Step selection (G5's input) is mechanical**: `s_lo` = smallest ladder rung with
`C = |J_adj|·s/η ≥ 5`; `s_hi` = smallest rung with `s_hi ≥ 2·s_lo`; `η` = `|CD(baseline) −
CD(baseline repeated)|`, measured in the same invocation.

**Why G5's count refusal is written this way.** `A4/curriculum_D3/d3_grade.py` returned `PASS` at
0.0000 % with zero sign flips **over an EMPTY COMPONENT SET**: the refusal tested key presence
and never non-emptiness, and the plateau loop iterated zero times. **A partial plant reads on the
page exactly like a complete one.** So G5 refuses by count first, prints the count, and asserts
its plateau loop's trip count equals the graded-row count. **L-302:** *an instrument that cannot
say "I measured nothing" will report a number it did not measure.*

**A symptom must distinguish its causes.** `rc = 1` and `rc = 2` are different failures, and an
exit code from the harness is not an exit code from the solver. Launcher preflight failures use
**reserved codes 4, 5, 64, 65** and never 0, 1 or 2; the container's exit and `OOMKilled` are read
from **`docker inspect`**, the kernel's own record. **No verdict above is reachable from a
preflight abort** — a preflight abort produces no ledger row, and G1 refuses on
`arm_absent_from_ledger` rather than grading an absence.

## 8. Cost — and the cap is asserted, not copied

| arm | task | cap (core-min) | memory cap | prediction (core-min) | basis |
|---|---|---|---|---|---|
| **P1** | decomposition determinism ×2 + per-rank placement | **8.0** | 4g | 1.5 | two `decomposePar` on 42,120 cells |
| **P2** | cold `compute_totals` + 2 primals — the §7 memory-envelope check **and the calibration probe that GATES the big buy** | **60.0** | 12g | 30.0 | 13.60 (adjoint) + 2 × 3.38 (primals) + coloring build |
| **O** | `run_driver`, IPOPT, **`max_iter` 30**, **SHIPPED row** | **600.0** | 12g | 570.0 | **19.0 core-min/major × 30 majors**, §2a |
| **F-S** | endpoint FD, 5 components, **SHIPPED** | **130.0** | 12g | 95.0 | 22 primals × 3.38 + one cold `compute_totals` |
| **F-P** | endpoint FD, 5 components, **PATCHED** | **130.0** | 12g | 95.0 | same |
| | **ITEM** | **CEILING 928.0** | | **PREDICTION 791.5** | |

`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED` — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
Predicted **791.5 core-min = $0.677 DERIVED, not measured**. Ceiling **928.0 core-min = $0.793
DERIVED**. Both are far inside the 2026-08-21 pre-authorisation; **a blanket is not a per-item
read** (`CLAUDE.md` rule 9), and this row is costed here regardless.

**Disclosed delta to the curriculum.** `EXPERTISE_CURRICULUM.md` prices D7 at `~600–900 core-min`
/ `$0.51–0.77`. **The prediction 791.5 sits inside it. The ceiling 928.0 sits 3.1 % above its
top**, because the curriculum's range priced neither the `DAFOAM_CHARTER.md` §7 memory-envelope
probe (arm P2) nor the **second toolchain row** (arm F-P) that §9's two-row rule requires. That is
stated here, **before compute**, not reconciled afterwards.

**An overrun STOPS the run; it does not get a new budget** (`CLAUDE.md` rule 12). Enforcement:
the launcher holds the cap table **as constants, not as arguments**, derives the wall timeout as
`cap × 60 ÷ 4`, then **inverts the arithmetic and asserts the result equals the registered cap to
within 0.02 core-min**, aborting before the container starts if it does not. **G10 re-reads the
enforced value out of the ledger and compares it to the cap registered in this file.** There is no
second number anywhere that could drift from the first.

**Calibration gate, registered.** **Arm P2 runs first and its measurement GATES arm O**: if P2's
measured core-minutes exceed **60.0**, or the kernel reports `OOMKilled true`, **or G12's placement
check fails on P1 or P2**, **arm O is not launched** and the item is reported at that point rather
than spent through. **P2 also re-measures the per-primal cost that §2 could only DERIVE**; if the
measured per-major basis implies arm O would exceed its 600.0 cap at `max_iter` 30, **that is
reported and arm O is not launched at a raised cap** — the cap does not move to fit the estimate.

## 9. Toolchain — TWO ROWS, BY IMAGE DIGEST, never by tag

`DAFOAM_CHARTER.md` §11: the hash is the identity, the version string is not; **there is no such
thing as "the fixed toolchain."** A3 rung 2 recorded `idwarp` reading version `2.6.2` on the
patched stack — **the version string discriminates nothing.**

| row | image | note |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | **the row the OPTIMISATION is bought on** |
| **PATCHED** | `dafoam-idwarp-rot:v1` (`libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425`) | **bought at the ENDPOINT FD table** |

The launcher resolves the digest of whatever tag it is handed and **aborts unless it equals the
digest registered at freeze time**; the exact digests are resolved and written into the launcher
before the first container and are part of the frozen instrument set.

### 9a. WHY THE OPTIMISATION BUYS **SHIPPED** — and this is the opposite of D4's choice

**R11 adoption is CASE-DEPENDENT, not global**, and D7 is the case that proves it. On **this exact
mesh**, A3 rung 2 measured the rotation patch making the gradient **WORSE**:

| component | SHIPPED | PATCHED | effect of the patch |
|---|---|---|---|
| `shape[115]` | **0.0172 %** | **0.1586 %** | **9.208× WORSE** |
| `twist[1]` | **0.2740 %** | **0.9279 %** | **3.39× WORSE** |
| `patchV[1]` | 0.0077 % | 0.0077 % | **bit-identical** — does not cross the warp |

That is `N-D18`: the first row on Ladder A where the rotation patch **degrades a gradient the
shipped toolchain already got right**. **D4 bought PATCHED on A2 for exactly the mirror-image
reason** — there the shipped row read 1.7138 % aggregate with 7 of 96 components beyond 15 %, and
patched read 0.0506 %. **Two items, two opposite choices, each anchored on its own case's
measurement. Neither is a global adoption of R11, and this document does not make one.**

**Driving a 30-major optimisation with the row measured to be 9.2× worse on this mesh would be a
worse item at the same price.** So the optimisation buys **SHIPPED**.

### 9b. Why the endpoint FD table buys BOTH rows

`DAFOAM_CHARTER.md` §6: **a DAFoam verdict is two rows, shipped and patched, or it is not a verdict
about DAFoam.** Twist and shape DVs both cross the warp, so shipped/patched is **live here, not
academic**. **The gradient claim is where the two-row rule bites**, so both rows are bought at the
endpoint (arms F-S and F-P) at a combined 190.0 core-min predicted.

**THE CONSEQUENCE, STATED PLAINLY: the OPTIMUM is a ONE-ROW (shipped) statement.** Any optimum or
drag reduction D7 reports is a **shipped-IDWarp** statement, and **D5, D6 and D14 must not read
D7's optimum as toolchain-independent.** The **endpoint gradient table is two-row and therefore is
a verdict about DAFoam**; the **optimum is not**, and it is labelled that way wherever it appears.
The patched-row optimisation is **`PENDING`** — not run, not failed — and its re-buy is a separate
registered item.

## 10. Frozen instruments

The launcher, the producer, the endpoint extractor, the endpoint FD producer and the grader are
committed **before any container starts**, each with its md5 recorded here at freeze time. The
launcher re-asserts those md5s on the STAGED copies before **every** launch, and after the run the
frozen files are hashed against the committed blobs of the freeze commit to prove the frozen file
**is** the file that ran.

**Parse-from-files discipline, registered.** MPI log splicing is **MEASURED on this ladder** — four
ranks interleave on one stdout and sever arrays mid-number (`A2/per_component_table/RESULTS.md`
§2.2, commit `79679a84`). **Every graded number in D7 is read from a FILE** — `opt_IPOPT.txt`
(written by IPOPT), `OptView.hst` (written by pyOptSparse rank 0), `d7_fd_endpoint.json` and
`d7_major_history.json` (written by rank 0 with `fsync`). **The grader refuses when a file it
expects is absent; it never falls back to stdout.** Stdout is read only for the container-uid and
IDWarp-`.so`-md5 provenance markers — short lines whose corruption makes them fail to match rather
than silently mis-read.

**The grader carries a REAL, WIRED `--selftest`** with a distinct exit path, per the D4-DEF-1
repair (`A2/curriculum_D4/d4_grade_D4DEF1_REPAIR.diff`). **D4's grader advertised a selftest it did
not have**; D7's must not repeat that, and the selftest must be shown able to FAIL against a
deliberately broken grader before its output is believed.

## 11. Predictions — scored afterwards as HIT or MISS, never adjusted

| id | prediction |
|---|---|
| P1 | IPOPT does **NOT** print `EXIT: Optimal Solution Found.` within `max_iter` 30 — **D7 cap-stops**, and its verdict ceiling is `GATE REACHED` |
| P2 | drag reduction lands in [3, 25] %, near 10 % |
| P3 | `\|CL − CL_target\| ≤ 5.0e-4` at every major |
| P4 | arm O costs 450–600 core-min (prediction 570) |
| P5 | **every** major's adjoint reports `PetscConvergedReason > 0` — no `-9`-class exit at rung 2 |
| P6 | at least **4 of 5** named components are graded and inside band D on the **SHIPPED** row |
| P7 | decomposition determinism holds — the two `processorN` cell-count maps are identical and sum to 42,120 |
| P8 | peak memory stays inside the 12 GiB container cap with no `OOMKilled` |
| P9 | the four ranks land on four **distinct** cores inside the pinned cpuset |
| P10 | delivered cores ≥ 3.0 of the 4-core quota, mean over each MPI arm |
| P11 | arm P2 costs ≤ 60 core-min, so arm O is authorised by its own calibration gate |
| P12 | **`patchV[1]` is bit-identical between the two endpoint rows**, as it was at rung 2 — it does not cross the warp chain |
| P13 | **`shape[115]` and `twist[1]` differ between the two endpoint rows, with SHIPPED closer to FD** — the rung-2 direction reproduces at the endpoint. **If it does NOT, that is a registered FINDING about design-point dependence, not a failure discovered afterwards** |

## 12. Freeze

This document is committed **before any container starts**. No gate, threshold, cap or label above
may change after the first compute; a departure lands only as a dated addendum at the foot, which
cannot alter a gate, threshold, cap or label, and the original is struck, never rewritten
(`CLAUDE.md` rules 2 and 6).

**NOT LAUNCHED. Nothing fires without the dafoam-supervisor's own read that this is committed.**

---

## Addendum 1 — 2026-08-25, PRE-COMPUTE. Instrument freeze, digests, and the launch gate.

**Version 1.0 → 1.1.** `lines whose number changed above this section: 0`.

**CONDITION, AND HOW IT WAS CHECKED** (`CLAUDE.md` rule 2: before first compute, amendments are
legal and must state the condition and how it was checked). **No compute has occurred for this
item.** Verified, at the moment this addendum was written, by three independent readings:

| check | reading |
|---|---|
| `/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/ledger.txt` | **does not exist** — the launcher writes it, and it has never run |
| arm directories `P1 P2 O F-S F-P` under the run root | **0 of 5 exist** |
| `docker ps -a` containers named `d7_*` | **0** — no container has ever been created for this item |

The run root itself **does** exist: it was created by the staging step, which copies the case and
writes no solver output. Stated exactly this way because "the run directory does not exist" is the
rule's shorthand for "no compute", and here the more precise statement is available.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Bands A–F, gates G1–G13, the
cap table of §8, `max_iter` 30 and the `GATE REACHED` ceiling of §7/§11 are exactly as frozen at
`337d4d84`. Nothing above this section is rewritten.

### A1.1 The gap this addendum closes

§10 states that the launcher, producer, endpoint extractor, endpoint FD producer and grader are
committed before any container starts, **"each with its md5 recorded here at freeze time"**. **No
md5 was recorded, because no instrument existed at the freeze commit** — §10 was a forward
commitment, not a record. The instruments are written now, before the first container, and their
md5s are recorded below. **This is disclosed as a gap in the frozen document rather than presented
as a plan that was followed.**

### A1.2 Frozen instruments — md5 at freeze

| instrument | role | md5 |
|---|---|---|
| `d7_opt_runScript.py` | producer (M6 optimisation model) | `e43902ed2cfc99022c6e21e075f88695` |
| `d7_extract_endpoint.py` | endpoint + per-major history extractor | `651d40c78cc52288a856934c108d1334` |
| `d7_fd_endpoint.py` | endpoint FD table producer | `92b3fa8d20a41da029590ed3bdde4203` |
| `d7_run_arm.sh` | launcher | `c55b2cdeaf8a0975641b491b24912d63` |
| `d7_grade.py` | grader | `f77a84c64c632af478c3dc4885143ed9` |

The launcher re-asserts the first three md5s on the **staged** copies before **every** launch and
aborts (exit 4) on a mismatch. **The producer's md5 is also embedded in `d7_fd_endpoint.py`**, which
refuses (exit 2) unless the producer it execs is byte-identical to the frozen one — the FD producer
does not carry a **copy** of the model, it execs the producer's own bytes up to the literal anchor
`# OpenMDAO setup`, so the two cannot drift.

### A1.3 Image digests, resolved from the local store 2026-08-25T20:26Z

§9 requires the digests be resolved and written into the launcher before the first container.

| row | tag | digest |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` |
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` |

Both are byte-identical to the digests `A2/curriculum_D4/d4_run_arm.sh` registered at its own
freeze. The launcher aborts (exit 4) unless the resolved digest equals the registered one, and
**enforces §9a's row assignment**: arms P1/P2/O are SHIPPED-only, F-S is SHIPPED, F-P is PATCHED.

### A1.4 The launch gate — an OPERATIONAL threshold, and it grades nothing

**This is a launch gate, not a grading gate. It cannot change any verdict**, and no band above
depends on it.

| arm class | container cap | **MemAvailable floor, stated before the reading it gates** |
|---|---|---|
| P2, O, F-S, F-P | 12g | **≥ 16.0 GiB** |
| P1 | 4g | **≥ 6.0 GiB** |

Basis: container cap + ~4 GiB host headroom. A3 rung 2 measured peak container RSS **9.263 GiB** at
np=4 on this mesh inside a 12 GiB cap. **Enforced with a real refusal path** (launcher exit 5,
before any rank is claimed).

**Honest disclosure about the ordering.** A `MemAvailable` reading of **28.21 GiB** was taken at
lane start (2026-08-25T20:23Z) as part of the box-state sweep, **before** these numbers were
written down. The thresholds were not chosen to clear that reading — they are the container cap
plus headroom — but the reading did precede them and saying so is cheaper than being asked.

**A3 rung 2's §9.1 mistake is not repeated.** That rung registered a host-memory stop rule as a
**record-only** watcher with nothing connecting rule to kill path, and its own record calls it what
it was: *"A stop rule with no enforcement path is a preference, not a control."* Here the
**pre-launch gate is the control**, and the in-run host-memory sampler is **record-only and is
declared record-only**, with no threshold and no stop condition attached. **No mid-run memory stop
is registered**, because killing a running 30-major optimisation to protect a number would destroy
the run it protects.

### A1.5 CPU placement — the census this cpuset came from

Census 2026-08-25T20:25Z, `mpstat -P ALL` over 5 s on 16 cores:

* cores **5, 14, 15** — **0.0 % idle**, three heat-transfer `buoyantBoussinesqSimpleFoam` solvers
  (pids 2203927 / 2203944 / 2203947). **Not touched, not signalled** — another team's live custody.
* core **0** — the default landing core the `--cpus=N` placement defect names.
* cores **2, 3, 4, 6** — **99.2 % idle each**. **CPUSET = `2,3,4,6`**, pinned at launch.

G12 then **measures** the placement rather than trusting the flag.

### A1.6 The colouring cache — read of §8, stated before it is acted on

§8 prices a **colouring build in arm P2's basis and in no other arm's**: arm O's basis is
`19.0 core-min/major × 30 majors` and each F arm's is `22 primals × 3.38 + one cold compute_totals`.
**That is only arithmetically consistent if the colouring is built once, in P2, and inherited by O,
F-S and F-P.** This item therefore builds it once and inherits it, and the launcher **refuses to
stage the inherited cache until arm P1 has demonstrated G8** — without a demonstrated-deterministic
partition the inherited colouring would not be a colouring *of this partition*. A3 rung 2 records
the same inheritance as a disclosed departure and measures a fresh build at **+28.0 core-min**.

### A1.7 A defect found in this item's own grader, before the freeze

Recorded because the lab's rule is that instruments are shown to work, not asserted to.

**`D7-GRADER-DEF-1`: G11, the OOM gate, could not fail.** The ledger reader's generic
`(\w+)=(...)` pattern **cannot match the key `inspect(exit,oomkilled)`** — `\w+` matches only the
trailing `oomkilled` — so `rec.get("inspect(exit,oomkilled)")` returned `None`, `oom` computed
`False`, and **G11 would have passed on a row the kernel marked `OOMKilled=true`**. Found by this
grader's own coverage unit `G11_OOMKilled_true_fails`, **repaired before the first container** with
an explicit parenthesised-key capture, and the repair is demonstrated by mutation `m8` (reinstating
the blindness → selftest exit 3).

**Attribution corrected before it was committed.** This lane first recorded that
`A2/curriculum_D4/d4_grade.py` shares the defect, having tested only that file's *generic* regex.
**It does not**: D4's G11 reads a separate dedicated structured parser (`d4_grade.py:551`) that
captures the key correctly. **The defect was this lane's alone.** A false defect attribution
against a peer's committed instrument is worse than the defect it alleges.

### A1.8 Grader selftest — WIRED, and its COVERAGE measured, not its size

`d7_grade.py --selftest` is wired from the first commit with a **distinct exit path** (3, used by
nothing else; a graded run exits 0 or 2) and writes no `--out`. **D4-DEF-1 — a `--selftest` flag
declared at argparse and never read, which silently ran a full grade — is not repeated.**

**Per the dafoam-supervisor's ruling of 2026-08-25 that unit count measures a selftest's SIZE and
not its COVERAGE**, the selftest prints both lists on every run:

* **gates the grader can emit: 14** — G1, G2, G3, G4, G5, G6, G6b, G7, G8, G9, G10, G11, G12, G13
* **gates the selftest exercises: 14**
* **UNEXERCISED: 0**

48 units, all passing. An earlier version scored 19/19 while exercising only G5–G8 and the verdict
mapping — **nine gates had no unit at all**, and the count concealed it. The banner exists so that
gap cannot silently reopen.

**The selftest is demonstrated able to FAIL**, against ten deliberately broken graders, each
breaking exactly one thing; **all ten produce exit 3**: count refusal deleted (m1), cap-stop mapped
to `PASS` (m2), planted-zero reader blinded (m3), plateau band removed (m4), order refusal deleted
(m5), sign-flip check removed (m6), hard-gate block bypassed (m7), G11 blindness reinstated (m8),
G9 forced to pass (m9), G12 count refusal deleted (m10).

**Two of those mutants originally ESCAPED** (m1 and m10) and the escape is the reusable part: with
the *count* refusal deleted, a short component set was still refused — by the *order* check — so
*"the gate refused"* was **not evidence that the count refusal existed**. That is the D3 defect
wearing another gate's clothes. Both refusals are now **named** (`COUNT_EMPTY`, `COUNT_MISMATCH`,
`ORDER_MISMATCH`, `KEY_ABSENT`, `PLACEMENT_COUNT`) and the selftest asserts **the name**, not merely
that something refused. **An empty-component-set unit is present specifically**, that being the
exact defect that made `d3_grade.py` return `PASS` at 0.0000 % over nothing.

`scripts/check_grader_self_blindness.py` reports **0 ERROR** on the frozen grader. Its own known
blind spot stands unrepaired and is not relied on: probe B fires on `os.path.join` and is silent on
`pathlib` and f-strings. **Clean is not proof.** Noted separately: that script **exited 0 while
printing `[ERROR]` lines**, so its exit code does not gate and was not treated as if it did.

### A1.9 What is staged, and the identity of the mesh

Staged **by copy, never edited in place**, from `/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1`:
`0/`, `0.orig/` (byte-identical to `0/` on all six fields), `FFD/`, `system/`,
`constant/{polyMesh,thermophysicalProperties,turbulenceProperties,birth_certificate.json}`.

| identity | value |
|---|---|
| `constant/polyMesh/owner.gz` md5 | `7e847a4f94e8855c89320c784bed96e6` — **byte-identical to A3 rung 2's** |
| `system/decomposeParDict` md5 | `1dbd9ead3f40a29f483444dc5fa1288b` — **byte-identical to A3 rung 2's**; `method scotch`, `numberOfSubdomains 4` |
| birth certificate | `cells: 42120`, verdict `clean`, generator pyHyp N=28 |

Nothing hot was staged: no `processor*`, no time directory, no `reports/`, no colouring cache, no
`OptView.hst`. The launcher re-verifies all of that per arm and aborts (exit 5) on any of them.

---

## Addendum 2 — 2026-08-25, PRE-COMPUTE. Two further grader defects, MEASURED; two corrections to Addendum 1; grader md5 re-registered.

**Version 1.1 → 1.2.** `lines whose number changed above this section: 0`.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Bands A–F, gates G1–G13, the
cap table of §8, `max_iter` 30 and the `GATE REACHED` ceiling of §7/§11 stand exactly as frozen at
`337d4d84`. Nothing above this section is rewritten. What changes is the **grader's md5**, because
the grader was repaired, and two statements in Addendum 1 that this lane measured to be false.

### CONDITION, AND HOW IT WAS CHECKED (`CLAUDE.md` rule 2)

**No compute has occurred for this item**, re-verified at **2026-08-25T21:22:10Z**, immediately
before this addendum was written, by four readings:

| check | reading |
|---|---|
| `/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/ledger.txt` | **does not exist** — the launcher writes it and it has never run |
| arm directories `P1 P2 O F-S F-P` | **0 of 5 exist** |
| `docker ps -a --filter name=d7_` | **0 containers** — none has ever been created for this item |
| any `*.log` beneath the run root | **0** |

**The run root itself DOES exist**, created by the staging step, which copies the case and writes
no solver output. Addendum 1 stated this correctly and this addendum repeats it: the rule's
shorthand "the run directory does not exist" would be **FALSE** here, and the truthful statement
is the narrower one — **no container has started and no arm directory exists**, checked by the
four commands above. Amendments therefore remain legal.

### A2.1 `D7-GRADER-DEF-2` — the D4-DEF-3 class was LIVE in this grader, in FOUR places

**D4-DEF-3**, recorded against `A2/curriculum_D4/d4_grade.py`: with `rows` absent from the FD
artifact, its G7 mutators indexed `d["rows"][:2]` and raised an **uncaught `KeyError`** — rc=1
with a traceback and **no verdict file written at all**, on the gate whose entire purpose was to
prove that malformed input is refused **by name**.

**This grader carried the same shape.** Found by **measurement, not by reading**: four
well-formed JSON artifacts — each of which parses cleanly, so `read_json`'s absent/empty/
unparseable guards all pass them through — were handed to `g6_plant` and `g7_count_control` in the
order the grader calls them.

| artifact | `g6_plant` (before repair) | `g7_count_control` (before repair) |
|---|---|---|
| `rows` key absent | refused cleanly | **uncaught `KeyError`** |
| `rows: []` | refused cleanly | **returned `pass=True`** |
| `rows: null` | refused cleanly | **uncaught `TypeError`** |
| `rows: {"a": 1}` (object, not list) | **uncaught `AttributeError`** | **uncaught `KeyError(slice)`** |

**The fourth row is the one that matters and is the reason this was measured rather than
reasoned about.** Addendum 1 presents `g6_plant` as the defended gate — it opens
`orig.get("rows") or []` and refuses on a falsy result. **A non-empty dict is truthy.** It passed
straight through, `enumerate` then yielded the dict's *keys* as strings, and `r.get(...)` raised
`AttributeError` on a `str`. **The gate the document called defended was the one that crashed
first.** Reading the code would have confirmed the `.get()` guard and stopped there; only running
it found this.

**Why a crash is not a refusal, stated plainly:** a gate that dies writes **no verdict file**, so
the malformed input it exists to catch goes **unrecorded** — strictly worse than a gate that never
existed, because the record shows an instrument that was supposed to look.

**REPAIRED** by a shared structural validator `require_rows(doc, where, row_label)`, called by
both gates before any subscript, refusing **by name**: `DOC_NOT_OBJECT`, `ROWS_KEY_ABSENT`,
`ROWS_NOT_A_LIST`, `ROWS_EMPTY`, `ROW_NOT_AN_OBJECT`. **All eight crash sites now refuse cleanly
(exit 2).**

**Also repaired, and it is the D3 shape:** `g7_count_control`'s verdict was
`n == 4 and n_refused == 4`. Over a baseline of **zero** rows all four mutations refuse trivially
and the gate reads `PASS` — **indistinguishable on the page from a complete control over the full
registered component set**, which is exactly the defect that let `d3_grade.py` return `PASS` at
0.0000 % over an empty component set. The verdict now additionally requires
`n_baseline == N_COMPONENTS_REGISTERED`, and the count is printed beside it.

### A2.2 `D7-GRADER-DEF-3` — the OOM gate reported a clean bill of health for a container that never ran

`g11_oom` computed `pass = not any_oom`. With an arm **absent from the ledger** the loop `continue`s,
`any_oom` stays `False`, and **the gate returns `pass=True`** — a clean OOM verdict on a container
that was never created. **Measured** by handing `g11_oom` an empty ledger; it returned `pass=True`.

A second instance one level up: `insp` empty — the kernel bit **never recorded** — was read as
`False`, i.e. as *not OOM-killed*. **An unread bit is not a clean bit.** This is `D7-GRADER-DEF-1`
(Addendum 1 §A1.7) repeating one level higher in the same function.

**REPAIRED.** `g11_oom` now counts arms read versus arms expected, emits
`status: NOT_MEASURED` and `pass = False` if any expected arm is absent or its OOM bit unrecorded,
and marks the unrecorded case `OOM_BIT_NOT_RECORDED` with `oom_killed: null`, never `false`.
**`NOT_MEASURED` is not health.**

Sibling gates were checked for the same shape in the same sweep and **do not have it**: `g10_caps`,
`g13_adjoint_health` and `g9_toolchain` all return `pass=False` over an absent arm.

### A2.3 A defect this lane did NOT report, named because a false attribution is worse than the defect

An initial probe raised `TypeError` from `g12_placement` on an absent arm. **That was the probe's
error, not the grader's** — `g12_placement(base, work_by_arm, ledger)` takes three positional
arguments and the probe passed them in the wrong order. **`g12_placement` is not defective and is
not reported as such.** Recorded because Addendum 1 §A1.7 had to make the identical correction
against a peer's committed instrument, and the rule it drew is worth keeping: *a false defect
attribution is worse than the defect it alleges.*

### A2.4 CORRECTION to Addendum 1 §A1.8 — the self-blindness checker does NOT report 0 ERROR

Addendum 1 states: *"`scripts/check_grader_self_blindness.py` reports **0 ERROR** on the frozen
grader."* **That is false and is struck.** The checker reports **1 ERROR**, and it reported it on
the **pre-repair** grader too — verified by running it against a byte-copy of the pre-repair file —
so this is a correction of a mis-statement in Addendum 1, **not** damage introduced by this
addendum's repairs.

The ERROR concerns `out['arms']` being written with differing key sets across branches, with four
keys (`actual_within_cap`, `overrun_core_min`, `rc`, `status`) read elsewhere. **Every read site it
flags is inside the selftest's own hand-built fixtures, not on the grading path**, and the
production path was probed directly rather than argued about — see §A2.2, where that probe found a
real defect in `g11` and cleared three sibling gates.

Addendum 1's own caveat stands and is reinforced: the checker **exits 0 while printing `[ERROR]`
lines**, so its exit code does not gate and was not treated as if it did; and its known blind spot
is unrepaired — probe B fires on `os.path.join` and is silent on `pathlib` and f-strings
(`3dc99590`). **Clean is not proof, and in this case it was not even clean.**

### A2.5 CORRECTION to Addendum 1 §A1.8 — the selftest counts have moved

| | Addendum 1 | **now** |
|---|---|---|
| units | 48 | **65**, all passing |
| gate groups exercised | 14 of 14, `UNEXERCISED=0` | **15** (`DEF2` added), 14 of 14 emitted gates still exercised, `UNEXERCISED=0` |
| mutants demonstrated to force exit 3 | 10 | **10 + 6 = 16** |

The six new mutants, each breaking exactly one repair, **all produce exit 3** while the unmutated
grader exits 0: `m11` G6's validator removed, `m12` G7's validator removed, `m13` G7's baseline-count
clause dropped, `m14` the validator itself blinded, `m15` G11's empty-set pass reinstated, `m16`
G11's unrecorded-bit-as-`False` reinstated. `m13` is the instructive one — it reports
`n_refused=4 baseline=2 registered=5 pass=True`, the D3 shape reproduced exactly, and the unit
catches it on the **baseline count**, not on the refusal count.

### A2.6 On the FD component count — a misreading corrected on the record

An instruction to this lane stated that *"the prereg registers `twist` 5, `shape` 120, `patchV` 2 —
assert the exact registered count"* against the grader's FD component set. **Those are two
different quantities and conflating them would break the grader.**

* `twist` **5**, `shape` **120**, `patchV` **2** are the **design-variable vector sizes** — 127 DVs
  total — registered at §1 of this document.
* §6 registers the **FD spot-check set** as **exactly 5 components**: `shape[115]`, `twist[1]`,
  `patchV[1]`, `shape[0]`, `shape[119]`, each with its stated reason for selection.

`COMPONENTS_REGISTERED` in the grader is the second of these and its 5 entries are **correct as
written**; asserting 5/120/2 there would make the grader refuse every correct artifact. The
sampled indices are consistent with the DV sizes (`shape` indices 0, 115, 119 all < 120;
`twist[1]` < 5; `patchV[1]` < 2). **No gate is changed by this paragraph** — it records that the
existing constant was checked against the frozen document and found right.

**A GAP IS NAMED AND NOT CLOSED.** Nothing in the grader asserts that the optimisation actually
carried **127** design variables. A truncated DV vector would not be caught by any registered gate.
This is recorded as a **known, unclosed gap** rather than repaired, because closing it would add a
gate after the freeze, which is not permitted. It is stated so a reader does not infer coverage
that does not exist.

### A2.7 Instrument md5s — RE-REGISTERED at this addendum

| instrument | md5 at Addendum 1 | **md5 now** | changed? |
|---|---|---|---|
| `d7_opt_runScript.py` | `e43902ed2cfc99022c6e21e075f88695` | `e43902ed2cfc99022c6e21e075f88695` | unchanged |
| `d7_extract_endpoint.py` | `651d40c78cc52288a856934c108d1334` | `651d40c78cc52288a856934c108d1334` | unchanged |
| `d7_fd_endpoint.py` | `92b3fa8d20a41da029590ed3bdde4203` | `92b3fa8d20a41da029590ed3bdde4203` | unchanged |
| `d7_run_arm.sh` | `c55b2cdeaf8a0975641b491b24912d63` | `c55b2cdeaf8a0975641b491b24912d63` | unchanged |
| **`d7_grade.py`** | `f77a84c64c632af478c3dc4885143ed9` | **`10eb6d0928addc56272854f017e01538`** | **CHANGED — §A2.1, §A2.2** |

The launcher asserts the first three on the staged copies before every launch (exit 4). **The
grader is not one of the three the launcher asserts**, so its md5 is fixed by this commit and the
grading path is verified against the committed blob at grade time, per `CLAUDE.md` rule 2.

**Nothing above §A2 has been edited. The four unchanged md5s are the proof of that for the
instruments, and the pre-Addendum-1 body of this document is byte-unchanged from `337d4d84`.**
