# Curriculum D4 — MACH wing constrained drag minimisation at fixed CL

**PRE-REGISTRATION — SHORT FORM.** Sanaa authorised the 10-line form on 2026-08-25 for
standard verification/validation cases: *"Prereg goes template-speed: standard
verification/validation cases use the 10-line prereg form (case, reference, quantities,
bands, ladder, decomposition seed, criteria) — minutes to freeze, not sessions."* D4 is a
standard case on a proven mesh. **Her rigor standard is explicitly unchanged**, so every
gate, threshold, cap and label below is frozen at this commit and is closed to change once
the first container starts (`CLAUDE.md` rule 2; `VERIFICATION_CHARTER.md` §2b, §2d).

**Nothing here is sent, filed, uploaded, posted or commented. SUBMISSIONS ARE PARKED and
sending is Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

---

## 1. Case

MACH Tutorial Wing, aero-only variant — **the A2 case, unchanged**.

| item | value |
|---|---|
| mesh | `38,304` cells, `40,209` points, staged by copy from `/home/ubuntu/certonomous-runs/A2-mach-wing/constant/polyMesh` |
| patches | `wing`, `inout`, `sym` |
| solver | `DARhoSimpleFoam`, `primalMinResTol` 1e-8, `primalMinResTolDiff` 1e3 |
| ranks | **np = 4** |
| design variables | `twist` 7 (root twist held), `shape` 96 (FFD 6×2×8 local), `patchV` 2 (`U0` fixed at both bounds, so AoA is the only free component) — **105 declared, 104 free** |
| constraints | `CL = 0.5` equality; `thickcon` 10×10 in [0.5, 3.0]; `volcon` ≥ 1.0; `lecon` and `tecon` linear equalities |
| objective | `CD`, minimise |
| optimiser | IPOPT via pyOptSparse, `tol` 1e-5, `constr_viol_tol` 1e-5, `max_iter` 100, `mu_strategy` adaptive, L-BFGS history 10 |
| run root | `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/` |

The producer is the **tutorial's own `runScript_AeroOnly.py`, byte-identical** — verified by
`cmp` and by md5 against `/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing/runScript_AeroOnly.py`.
It is the script A2 ran. **No line of it is edited by this item**, which is why the `max_iter`
cap, the tolerances and the DV set below are quoted rather than chosen.

## 2. Reference and cost anchors

| anchor | value | source |
|---|---|---|
| A2 two-row gradient verdict | `PASS` / `PASS` with the idx46 caveat **RECORDED** | `cases/dafoam/ladder-a/A2/per_component_table/RESULTS.md` |
| A2 **optimisation** | **`NOT A RESULT`** — 47 majors in a 3600 s box, `converged_to_optimizer_tolerance: false`, **no `EXIT` line anywhere in `opt_IPOPT.txt`** | `DAFOAM_CHARTER.md` §9; verified this session by `grep -a EXIT /home/ubuntu/certonomous-runs/A2-mach-wing/opt_IPOPT.txt` returning nothing |
| A2 baseline `CD` | `2.9619634e-02` at `inf_pr` `4.16e-08` (iteration 0) | `/home/ubuntu/certonomous-runs/A2-mach-wing/opt_IPOPT.txt` |
| A2 reached | `CD` `2.1244538e-02` at major 47, `inf_pr` `1.44e-05`, `inf_du` `9.00e-05` | same file |
| **per-major cost anchor** | **5.106 core-min/major** = 3600 s wall × 4 ranks ÷ 60 ÷ 47 majors | `.opt_start_epoch` `1785209179` and `opt_run_driver.log` mtime `1785212779` in the A2 run root |
| **cold `compute_totals` anchor** | **32.7 core-min** = 490 s × 4 ÷ 60 | `.adjoint_start_epoch` `1785198052`, `compute_totals_run1.log` mtime `1785198542` |
| **per-FD-primal anchor** | **≈ 0.90 core-min** = 3153 s × 4 ÷ 60 ÷ 211 primals | `.checktotals_start_epoch2` `1785205914`, `check_totals_run1.log` mtime `1785209067` |

**Every anchor above is from THIS CASE at THIS rank count.** No price is invented across case
classes. The curriculum's A4 (2,777 cells, np=1) and A3 (42,120 cells, np=4) anchors are
**not used**, because A2's own driver run is the nearest anchor there is.

### 2a. INTEGRITY FLAG carried forward, and what this item does about it

`cases/dafoam/ladder-a/A2/grading_confirmation/RESULTS.md` **§1 is FALSIFIED at PATCHED
idx46** — it states *"no component is flagged … no sign flip anywhere in A2, at either
toolchain"*, and the per-component extraction disproves it. **No §1 claim is carried forward
into this pre-registration or into D4's results.** Every idx46 fact used below is re-derived
from the per-component artifact `cases/dafoam/ladder-a/A2/per_component_table/RESULTS.md` §3,
and that is stated as the derivation:

> `CD` wrt `dvs.shape`, **PATCHED**: aggregate `5.0591140e-04` (0.0506 %), **1 sign flip of
> 96 — idx46**, analytic `+2.27367571e-06` against FD `−2.52460969e-06`, **+190.06 %**;
> 95 of 96 within 5 %, 1 beyond 15 %.
> **SHIPPED**: aggregate 1.7138 %, **0 sign flips**, 79 of 96 within 5 %, **7 beyond 15 %**,
> worst **idx18 at −360.75 %**.

## 3. Quantities measured

Final `CD`; per-major `|CL − 0.5|`; major count; the IPOPT `EXIT` line verbatim; the
active-constraint picture via `inf_pr`; the endpoint FD table over the five components named
in §6; peak container memory and the kernel's `OOMKilled` bit; wall seconds, ranks and
core-minutes per arm from the launcher's own ledger.

## 4. Bands — FROZEN BEFORE COMPUTE

| id | band | value |
|---|---|---|
| **A** | CL feasibility, **every** major | `\|CL − 0.5\| ≤ 5.0e-4` |
| **B** | CL feasibility, **final** major | `\|CL − 0.5\| ≤ 1.0e-5` (IPOPT's own `constr_viol_tol`) |
| **C** | drag reduction `(CD₀ − CD_f)/CD₀` | **[25 %, 45 %]**, prediction **30 %** |
| **D** | endpoint FD agreement, **per graded component** and **in aggregate** | **≤ 5.0 %**, and **zero sign flips** among graded components |
| **E** | plateau, per component | `\|d(s_hi) − d(s_lo)\| / \|d(s_hi)\| ≤ 10 %` |

Band C's basis: A2 reached **28.275 %** at major 47 without converging, on the SHIPPED
toolchain. A converged run on a mesh and NLP this size is expected to land near but not far
beyond that. **[25, 45] is wide on purpose and it is frozen here; a result outside it is
reported as a MISS, never re-banded.**

## 5. Ladder, decomposition and seed — PINNED BEFORE COMPUTE

**Decomposition: `scotch`, `numberOfSubdomains 4`**, from the case's own
`system/decomposeParDict` (staged unchanged from A2, so this run's partition is the same
configuration A2's np=4 FD reference was measured under — `DAFOAM_CHARTER.md` §5: *an FD
reference is part of a configuration, not a property of a case*).

**Honest statement of what "seed" means here.** OpenFOAM's `scotchDecomp` exposes **no seed
parameter**; there is no number to pin. Determinism is therefore **not by construction** and
is **not asserted**. Gate **G8** demonstrates it: arm P1 runs `decomposePar -force` twice on
the same staged mesh and compares the four `processorN` cell counts, which must be identical
and must sum to 38,304. **If they differ, G8 is `GATE FAIL` and every np=4 number in this
item is `NOT A RESULT`** — that consequence is registered here, before the run.

**Registered limitation, not a discovery.** `DAFOAM_CHARTER.md` §5 requires a *new* case's
first FD verification at np=1 before any parallel figure is graded. A2 is **not** a new case
— its np=4-`scotch` FD reference exists and is graded. **This item does not buy an np=1 arm.**
Consequence, stated in advance: **D4's endpoint FD table is a statement about np=4-`scotch`
and is never carried to another np.** §5's own measurement is why this matters: on A4, np=4
`scotch` read 8.95 % and np=4 `simple` 4×1×1 read 0.00054 % — a factor of **16,600** between
two decompositions of one mesh.

### 5b. CPU PLACEMENT — pinned before compute, and MEASURED afterwards

**The defect, MEASURED, not hypothesised.** `mpirun` inside a `--cpus=N` container binds rank 0
to the **first core of the host topology**. Concurrent containers all land on that same host
core and throughput collapses as `1/N` **while the box reports itself idle**. The D13 lane
measured it on this box on 2026-08-25 at np=1: `affinity=0` on all three concurrent arms,
**0.250 cores delivered against a 1.0-core quota**, 0.45 % of periods throttled, **host 61 %
idle**; the control changed only the sibling count and throughput moved **4×**. **`--cpus=4`
does NOT hand out four distinct cores.** D4 is the first np=4 D-item today and this hits it
hardest.

**Why it is registered here and not merely noted.** D4 prices a 620 core-min buy off a
calibration probe. **A calibration taken against colliding siblings is wrong by up to 4× and
looks measured** — which is worse than no calibration at all. Placement is therefore part of
the deterministic-execution claim the parallel-gate doctrine asks for, and is pinned with the
decomposition, not after it.

**PINNED: `--cpuset-cpus=5,6,7,9`.** The choice is a measurement, taken at freeze time
(2026-08-25 ~17:45Z) and recorded here:

| core | state at freeze | note |
|---|---|---|
| 0 | 1.0 % busy | **the default landing core the defect names — deliberately avoided** |
| 1, 2 | 76.6 %, 23.9 % | native peer load |
| 3, 4, 12, 14 | 100 % | native peer load |
| 8 | 100 % | the live sibling container `d8_opt` (A6 CRM, 1.0-core quota, host affinity mask **8–15**) |
| **5, 6, 7** | **idle** | **outside the only live container's affinity mask** — chosen |
| **9** | **idle** | inside 8–15, so a `d8_opt` migration onto it is possible; disclosed, and its cost would show in the delivered-cores measurement |
| 10, 11, 13, 15 | idle | inside 8–15; held in reserve |

`mpirun` is additionally invoked with **`--bind-to core --report-bindings`** on every MPI arm.
**This is a registered deviation from A2's own invocation**, made for the reason above; its
consequence is stated: **A2's 5.106 core-min/major anchor is used for PREDICTION only**, and
D4's per-major cost is measured from D4's own ledger, never inherited.

**Gate G12 — placement is measured, not inferred.** Arm P1 runs `mpirun -np 4 --bind-to core`
and **each rank writes its own `sched_getaffinity` mask to its own file**; G12 refuses **by
count** on fewer than 4 such files, exactly as G5 refuses on a short component set, and
requires: the affinity union inside `{5,6,7,9}`; **all four ranks on distinct single cores**;
and **not** the defect's signature of every rank pinned to one shared core. Separately, a
passive sampler polls the container's own cgroup `cpu.stat` throughout each arm and writes
**delivered cores** to a file; **an arm delivering under 3.0 cores of its 4-core quota is
`GATE FAIL` on G12**. The sampler starts nothing and kills nothing, and **an absent sample
file is reported `NOT_MEASURED`, never as a passing placement gate.**

**The conditioning variable is CONCURRENT CONTAINERS, not `loadavg`** — `uptime` lies for
containerised MPI. The launcher censuses live non-D4 containers **before and after every arm**
and writes both into the ledger; the census is reported in RESULTS and in the cost-calibration
row.

**Registered consequence — a false finding this gate exists to prevent.** A slow adjoint at
np=4 reads **exactly** like GMRES stagnation, which is a real failure mode measured on this
ladder at N=52. **No adjoint-conditioning finding may be recorded by this item until G12 has
ruled out core contention.** Contention is attributed **separately** from waste and from
misprediction in the calibration row and is **never absorbed into the ratio**
(`CLAUDE.md` rule 12; `COMPUTE_BUDGET_CHARTER.md` §6).

**FD step ladder** (§7 selects from it mechanically; no step is hand-picked):

| DV family | ladder |
|---|---|
| `shape` | `1e-3, 3e-3, 1e-2, 3e-2` |
| `twist` | `1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1` |
| `patchV` | `1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1` |

`shape` stops at `3e-2` because a local FFD displacement is a length and a larger step risks
a warp failure rather than a noisier derivative. **A step that fails to produce a converged
primal is recorded as a failed-step row** (`DAFOAM_CHARTER.md` §3), never dropped.

## 6. The idx46-class near-zero components — NAMED IN ADVANCE

Five components are bought. Each is named here, with its reason, **before any compute**.

| # | component | why this one |
|---|---|---|
| 1 | **`shape` idx46** | **THE idx46-class component.** The A1 idx6 / A5 idx16 / A2 idx46 family. On the PATCHED toolchain at the BASELINE it is the single sign flip of 96, `+2.27367571e-06` vs `−2.52460969e-06`, +190.06 % |
| 2 | `shape` idx18 | the worst SHIPPED component at the baseline, `−360.75 %`; inside 5 % on PATCHED. Bought to see whether the endpoint moves it |
| 3 | `shape` idx0 | a component with **no** prior flag — the control against a set selected only from known-bad components |
| 4 | `twist` idx0 | twist is a `rot_z` on the reference axis and therefore crosses the IDWarp rotation path **directly**; it is the DV family the patch exists for |
| 5 | `patchV` idx1 | AoA — the DV the `CL` equality is carried by, and the component D1-C′ used to measure this lab's cross-run noise floor |

### 6a. The consequence, registered before the run

**A component whose measured clearance `C = |J_adj|·s/η` fails to reach 5 at EVERY rung of
its ladder is `NOT A RESULT` for that component.** It is excluded from the aggregate and from
the coverage count, and coverage is reported as **`k of 5`** — never as a percentage over a
shrunken denominator.

**Prediction, registered:** `shape` idx46 is the component most likely to be `NOT A RESULT`
under this rule at the endpoint, because a near-zero analytic is what makes a ratio blow up.
**If it is instead gradeable and flips sign, that is a registered FINDING of this item, not a
failure discovered afterwards and then explained.** Either outcome is reported as registered.

**Registered second-order caveat:** D1-C′ measured that the stock IDWarp `warpDeriv` defect is
**design-point dependent** — 640 % and sign-flipped at the undeformed baseline, unresolvable
at the converged point. **A baseline flag therefore predicts nothing about the endpoint**, and
this item must not read a clean endpoint as a retraction of the baseline finding.

## 7. Criteria and gates

| gate | what it reads | mapping |
|---|---|---|
| **G1** | `rc`, the launcher ledger, the **age guard** | rule 4's DAFoam analogue: `rc = 0`; the producer's own output FILE terminal; **every graded artifact strictly newer than the case's own `0/U`**, whose mtime the launcher writes to `.d4_age_datum` at stage time. Any stale artifact → **`NOT A RESULT`**. Rule 4's thermal field list does not apply and is not pretended to |
| **G2** | `d4_major_history.json` (from `OptView.hst`) | bands A and B → `PASS` else `GATE FAIL` |
| **G3** | `opt_IPOPT.txt` — IPOPT's **own** output file | `EXIT: Optimal Solution Found.` → `PASS`-eligible. **Cap-stop (wall clock, `max_iter`, or budget) → `GATE REACHED` if band C and band A both hold, else `NOT A RESULT`. NEVER `PASS`** (`DAFOAM_CHARTER.md` §9). An adjoint `-9`-class exit → **`BLOCKED`, not skipped** |
| **G4** | same two files | band C. **On a cap-stop the best available verdict is `GATE REACHED`**, and the item is never graded from the size of its improvement |
| **G5** | `d4_fd_endpoint.json` | band D and band E. **REFUSES BY COUNT, WITH THE COUNT PRINTED**, on an empty, short, long or reordered component set (see §7a) |
| **G6** | the FD artifact on disk | **planted zero** (rule 3): plant `1.234e-03` into a graded row, re-read through the SAME reader, refuse if any consumed channel cannot see it |
| **G6b** | — | **negative control**: a blind reader that ignores the path it is handed **must be REFUSED**. A control that cannot refuse is not a control |
| **G7** | — | **count control**: four deliberate mutations — `rows` emptied, `rows` shortened to 2, `rows` reversed, `rows` key removed — each must produce a **NAMED** refusal |
| **G8** | `d4_decomp_A.json`, `d4_decomp_B.json` | decomposition determinism, §5 |
| **G9** | ledger + arm logs | image **digest** and the imported IDWarp `.so` md5 (`DAFOAM_CHARTER.md` §11) |
| **G10** | ledger | **enforced cap == registered cap**, per arm, read back from the ledger the launcher wrote — not from the launcher's claim; and actual ≤ cap |
| **G12** | `d4_placement_rank*.json` (per-rank FILES) + the ledger's delivered-cores column | §5b: affinity union inside `{5,6,7,9}`, four ranks on **distinct** cores, no shared-core collision, **≥ 3.0 of 4 cores delivered**. Refuses **by count** on fewer than 4 rank files. `GATE FAIL` → every np=4 cost figure in this item is reported as **contention-contaminated** and no conditioning finding may be drawn |
| **G11** | `docker inspect .State.OOMKilled` | `DAFOAM_CHARTER.md` §7: OOM-killed → **`NOT A RESULT` about convergence**, recorded as stopped by memory |

**Step selection (G5's input) is mechanical**, from `A6/rung_n16_remaining_components/RESULTS.md`
§3.1: `s_lo` = smallest ladder rung with `C = |J_adj|·s/η ≥ 5`; `s_hi` = smallest rung with
`s_hi ≥ 2·s_lo`; `η` = `|CD(baseline) − CD(baseline repeated)|`, measured in the same
invocation. **That rule's own registered limitation is carried VERBATIM:**

> *"One item, five components, one case, one eta. The rule has not been tried where the proxy
> `|J_adj|` is itself wrong — which is the case it would be worst at, since it sizes the step
> from the very quantity under test."*

**On a rung whose adjoint is wrong, the `|J_adj|` proxy sizes steps from a wrong number.**
That is the standing limitation and D4 does not repair it.

### 7a. Why G5's count refusal is written the way it is

Last session this family found that `cases/dafoam/ladder-a/A4/curriculum_D3/d3_grade.py`
returned **`PASS` at 0.0000 % with zero sign flips over an EMPTY COMPONENT SET**: a
present-but-unparseable FD block yielded an empty list *with the key present*; the refusal
tested key presence and never non-emptiness; the plateau loop iterated zero times so a step
was "selected" without one comparison; and the discrimination control **fired correctly and
certified a result it had not measured**. **A partial plant reads on the page exactly like a
complete one.** So G5 refuses by count first, prints the count, asserts its plateau loop's
trip count equals the graded-row count, and G7 proves each refusal fires. L-302: *an
instrument that cannot say "I measured nothing" will report a number it did not measure.*

### 7b. A symptom must distinguish its causes

`rc = 1` and `rc = 2` are different failures, and an exit code from the harness is not an exit
code from the solver. The launcher's own preflight failures use **reserved codes 4, 5, 64, 65**
and never 0, 1 or 2; the container's exit is read from **`docker inspect .State.ExitCode`**,
the kernel's own record, not from the harness's `$?`. `OOMKilled` is read from the same place.
**No verdict in §7 is reachable from a launcher preflight abort** — a preflight abort produces
no ledger row, and G1 then refuses on `arm_absent_from_ledger` rather than grading an absence.

## 8. Cost — and the cap is asserted, not copied

| arm | task | cap (core-min) | memory cap | prediction (core-min) | basis |
|---|---|---|---|---|---|
| **P1** | decomposition determinism, ×2 | **5.0** | 4g | 1.0 | two `decomposePar` on 38,304 cells |
| **P2** | `compute_totals` — the §7 memory-envelope check and the calibration probe | **55.0** | 12g | 33.0 | A2 cold `compute_totals`, 32.7 |
| **O** | `run_driver`, IPOPT, `max_iter` 100 | **620.0** | 12g | 511.0 | 5.106 core-min/major × 100 majors |
| **F** | endpoint FD, 5 components | **120.0** | 12g | 53.0 | 22 primals × 0.90 + one cold `compute_totals` |
| | **ITEM** | **CEILING 800.0** | | **PREDICTION 598.0** | |

`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED` — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
Predicted **598.0 core-min = $0.511 DERIVED, not measured**. Ceiling **800.0 core-min =
$0.684 DERIVED**. Both are far inside the 2026-08-21 pre-authorisation; **a blanket is not a
per-item read** (`CLAUDE.md` rule 9), and this row is costed here regardless.

**Disclosed delta to the curriculum.** `EXPERTISE_CURRICULUM.md` prices D4 coarsely at
`~500–750 core-min`. The prediction 598 sits inside it. **The ceiling 800 sits 6.7 % above its
top**, because the curriculum's range did not separately price the `DAFOAM_CHARTER.md` §7
memory-envelope probe (arm P2) that this item runs before the big buy. That is stated here,
before compute, not reconciled afterwards.

**An overrun STOPS the run; it does not get a new budget** (`CLAUDE.md` rule 12). Enforcement:
`d4_run_arm.sh` holds the cap table **as constants, not as arguments**, derives the wall
timeout as `cap × 60 ÷ 4`, and then **inverts the arithmetic and asserts the result equals the
registered cap to within 0.02 core-min**, aborting with code 65 before the container starts if
it does not. **G10 then re-reads the enforced value out of the ledger and compares it to the
cap registered in this file.** There is no second number anywhere that could drift from the
first — which is the failure mode a peer lane hit today, registering 3.0 and enforcing 6.0 by
copy-forward with no assertion.

**Calibration gate, registered.** This is the largest single buy this family has made in a
while, so arm **P2 runs first and its measurement gates arm O**: if P2's measured core-minutes
exceed **55.0**, or the kernel reports `OOMKilled true`, **or G12's placement check fails on P1 or P2**, **arm O is not launched** and the
item is reported at that point rather than spent through. The family's live calibration lesson
runs in the other direction — **D1 came in at 0.304×** because IPOPT took full steps on all 11
majors and the line-search primals priced into every major were never bought — so an actual
far *below* 511 is expected as readily as one above, and both are reported as misses if they
fall outside.

## 9. Toolchain — BY IMAGE DIGEST, never by tag

`DAFOAM_CHARTER.md` §11: the hash is the identity, the version string is not; **there is no
such thing as "the fixed toolchain."**

| row | image | digest |
|---|---|---|
| **PATCHED — BOUGHT** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` |
| SHIPPED — **NOT BOUGHT** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` |

The launcher resolves the digest of whatever tag it is handed and **aborts (code 4) unless it
equals the registered digest**. Each arm additionally prints the md5 of the `libidwarp.so` it
actually imported, and G9 records it — so the run proves what it ran, rather than the record
asserting it.

### 9a. Frozen instruments

| file | md5 |
|---|---|
| `d4_opt_runScript.py` (producer; **byte-identical** to the tutorial's `runScript_AeroOnly.py`) | `2906d52a5dbed2bacbaeaf85a37d3fe8` |
| `d4_run_arm.sh` (launcher, holds the cap table) | `399957c616215c8f1ae078abe2e97958` |
| `d4_extract_endpoint.py` (endpoint + per-major history, from `OptView.hst`) | `ee7d3c99fd716da23779cb651961918e` |
| `d4_fd_endpoint.py` (endpoint FD producer) | `c6112b0ec3bfdb5287345e350500f64a` |
| `d4_grade.py` (grader) | `f162ef69a7385e5d0586ef5f27657cbb` |

The launcher re-asserts the first three md5s on the STAGED copies before **every** launch.
After the run, the frozen files are hashed against the committed blobs of this commit to prove
the frozen file **is** the file that ran.

**Parse-from-files discipline, registered.** MPI log splicing is **MEASURED on this exact
case** — four ranks interleave on one stdout and sever arrays mid-number, and of four printed
copies of `CD wrt shape` in A2's published log **one** was usable and of four copies of
`CL wrt shape` **none** was (`per_component_table/RESULTS.md` §2.2, commit `79679a84`).
**Every graded number in D4 is read from a file** — `opt_IPOPT.txt` (written by IPOPT),
`OptView.hst` (written by pyOptSparse rank 0), `d4_fd_endpoint.json` and
`d4_major_history.json` (written by rank 0 with `fsync`). **The grader refuses when a file it
expects is absent; it never falls back to stdout.** Stdout is read only for the container-uid
and IDWarp-`.so`-md5 provenance markers, single short lines whose corruption makes them fail
to match rather than silently mis-read.

## 10. The two-row rule, and what this item does NOT claim

`DAFOAM_CHARTER.md` §6: a DAFoam verdict is **two rows, shipped and patched**, or it is not a
verdict about DAFoam. **Twist and shape DVs both cross the warp, so shipped/patched is live
here, not academic** — the idx46 caveat is itself a patched-row finding.

**ONE ROW IS BOUGHT: PATCHED.** Named, with the reason and the consequence, before compute.

* **Why PATCHED.** At the baseline the shipped toolchain's `CD` wrt `shape` gradient reads
  **1.7138 % aggregate with 7 of 96 components beyond 15 % and idx18 at −360.75 %**; patched
  reads **0.0506 % with 95 of 96 within 5 %**. An optimisation driven by a gradient known to
  be wrong on seven of its search directions is a worse item at the same price.
* **Why not both.** Both rows are ~1,200 core-min against a curriculum row of 500–750 and a
  ceiling of 800, and ~6 wall-hours at np=4 on a box already carrying two peer dafoam lanes
  and one cfd lane.
* **THE CONSEQUENCE, stated plainly: this item CANNOT claim a toolchain-independent result.**
  Any optimum, drag reduction or endpoint FD table D4 reports is a **patched-IDWarp**
  statement. **D5, D6 and D14 inherit that qualifier** and must not read D4's optimum as
  toolchain-independent. The SHIPPED row is **`PENDING`** — not run, not failed — and its
  re-buy is a separate registered item.

## 11. Predictions, scored afterwards as HIT or MISS, never adjusted

| id | prediction |
|---|---|
| P1 | IPOPT prints `EXIT: Optimal Solution Found.` within `max_iter` 100 |
| P2 | drag reduction lands in [25, 45] %, near 30 % |
| P3 | `|CL − 0.5| ≤ 5.0e-4` at every major |
| P4 | arm O costs 400–620 core-min (prediction 511) |
| P5 | `shape` idx46 is **`NOT A RESULT` (near-zero)** at the endpoint under §6a |
| P6 | of the four remaining named components, **at least 3** are graded and inside band D |
| P7 | decomposition determinism holds — the two `processorN` cell-count maps are identical |
| P8 | peak memory stays inside the 12 GiB container cap with no `OOMKilled` |
| P9 | `shape` idx18 is inside band D at the endpoint (patched was inside 5 % at the baseline) |
| P10 | arm P2 costs ≤ 55 core-min, so arm O is authorised by its own calibration gate |
| P11 | the four ranks land on four **distinct** cores inside `{5,6,7,9}` — the D13 shared-core collision does **not** reproduce under `--cpuset-cpus` |
| P12 | delivered cores ≥ 3.0 of the 4-core quota, mean over each MPI arm |

## 12. Freeze

This document, the four producers and the grader are committed **before any container starts**.
No gate, threshold, cap or label above may change after the first compute; a departure lands
only as a dated addendum at the foot, which cannot alter a gate, threshold, cap or label, and
the original is struck, never rewritten (`CLAUDE.md` rules 2 and 6).
