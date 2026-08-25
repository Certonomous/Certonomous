# Curriculum D8 — A6 CRM wing, N=16, twist-only constrained drag minimisation — PRE-REGISTRATION

**Filed 2026-08-25, DAFoam team lane D8, BEFORE any solver arm launched.** Short form, under Sanaa's
2026-08-25 authorisation: *"Prereg goes template-speed: standard verification/validation cases use
the 10-line prereg form (case, reference, quantities, bands, ladder, decomposition seed, criteria) —
minutes to freeze, not sessions. Bespoke frozen documents are reserved for novel or contested cases
only."* D8 runs a **proven case** (A6 N=16, five independent reproductions of its cold baseline) at a
**known memory boundary** (9.787 GiB measured): standard, so the short form applies. Her rigor
standard is unchanged and every gate, band, cap and label below is frozen here before compute.

`RESULTS.md` will not revise this file. Departures land as dated amendments there.
**Nothing is filed, sent, uploaded, posted or pushed. SUBMISSIONS ARE PARKED and sending is Sanaa's
alone** (CLAUDE.md rule 7; `DAFOAM_CHARTER.md` §10).

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/`.

---

## 0. Ordering disclosure — what was read before this file was written, and at what cost

No solver arm has been launched and none will be until this file is committed and
`git cat-file -e HEAD:<this path>` succeeds (`SUPERVISION_CHARTER.md` §3 check 4; CLAUDE.md rule 2).
Everything below quoted as measured was read from artefacts already on disk:
`../rung_n16_np1/RESULTS.md`, `../rung_n16_fixed_reference/RESULTS.md`,
`../rung_n16_remaining_components/{PREREGISTRATION,RESULTS}.md`, `../README.md`,
`/home/ubuntu/certonomous-runs/{P2-a6-n16,P3-a6-n16-ref,P3-a6-n16-rem}/` (ledgers, logs, harness),
and `cases/dafoam/ladder-a/A1/curriculum_D2/d2_run_arm.sh`.

**One container was started before this file was written, and it is billed here, not hidden.** A
13 s `dafoam-idwarp-rot:v1` invocation read the source of `OptFuncs.findFeasibleDesign` out of the
image so the trim loop could be costed honestly (rule 12 disqualifies an uncosted proposal). **No
case field, objective, derivative or mesh was computed; no OpenFOAM solver ran.** Billed in §8 at
**0.217 core-min**, measured (13 s × 1 rank ÷ 60).

**A correction to the curriculum line, entered before compute.** `EXPERTISE_CURRICULUM.md` Tier 3
calls D8 a **wing-body**. It is not. `../README.md` opens: *"Ladder A6 — CRM wing-alone (not a full
wing-body)"*. The case graded here is the **CRM wing-alone**, coarsened to N=16 (41,760 cells). The
curriculum's wording is wrong and this item does not adopt it.

---

## 1. Case

**A6 CRM wing-alone**, coarsened FFD/mesh rung **N = 16**, **41,760 cells**, `DARhoSimpleCFoam`,
transonic (U0 = 295 m s⁻¹, p0 = 101325 Pa, T0 = 300 K), **np = 1**. Objective **CD**, minimised.
**Design variables: `twist` (7 components, degrees) and `patchV` (2 components: U0 and AoA).**
The tutorial's `shape` local-FFD group is **removed** — that is what *twist-only* means here, and it
is the choice that makes the item gradeable: **`shape` has never been graded by any item in this
family** (`../rung_n16_remaining_components/RESULTS.md` §5.1 carries it `PENDING`), whereas every
component of `twist` and `patchV` is either graded PASS or flagged by name. `patchV` is retained
because it is the CL trim variable and because both its components are graded.
Constraints: **CL = 0.5** (equality), **thickness ≥ 0.5** (25 × 30), **volume ≥ 1.0**. The LE/TE
linear constraints are removed with `shape`, since they constrain local FFD DVs that no longer exist.

## 2. Reference and measured anchors

| anchor | value | source |
|---|---|---|
| A6 N=16 graded FD-vs-adjoint, 8 of 9 components | **1.0432 %** aggregate, **0 sign flips** | `../rung_n16_remaining_components/RESULTS.md` §4.2 |
| worst graded component | **1.817 %** (`twist` idx3) | ibid. §4.1 |
| `twist` idx6 | **NOT A RESULT**, FD-ungradeable, plateau 83.53 % | ibid. §4.1 row 9, §5.1 |
| cold primal, np=1, 41,760 cells | **102.1 s = 1.70 core-min** | ibid. §2.3 (commit `9d5029e8`) |
| whole graded FD item | **63.166 core-min** | commit `66f42398` |
| adjoint peak RSS | **9.787 GiB** | `../rung_n16_np1/RESULTS.md`; `../ADJOINT_MEMORY_ENVELOPE.md` |
| adjoint solve, `transonicPCOption 1` | **517 GMRES iters**, `PetscConvergedReason: 2`, ≈ **570 s** | `P2-a6-n16/patched.log:775` and its ExecutionTime trace |
| cold baseline CD, five independent reproductions | **0.03506349413916734** | `../rung_n16_remaining_components/RESULTS.md` §1 |
| CD noise floor η, last-200 peak-to-peak at `printInterval 10` | **1.0910e-05** | N-D13; reproduced to ratio 1.000, ibid. §2.2 |

**A6 overall is `BLOCKED`. N=16 is `GATE FAIL` (shipped) / `PASS` at 8 of 9 (patched).
N=29 HAS NEVER RUN, its wording is Sanaa's (D464), and NOTHING in this item touches it, stages it,
queues it or costs it.**

## 3. Quantities measured

Final **CD**; final **|CL − 0.5|**; **major count** and the optimiser's termination string; the
**active-constraint set**; the **endpoint FD-vs-adjoint table on the 8 gradeable components**;
**peak RSS** and the cgroup `memory.peak`; endpoint **η**; core-minutes per arm.

## 4. Bands — FROZEN BEFORE COMPUTE

| gate | band | where the number comes from |
|---|---|---|
| **G2 CL feasibility** | `\|CL_final − 0.5\| ≤ 5.0e-3` → PASS, else GATE FAIL | IPOPT's own `constr_viol_tol` is 1e-5; the registered band is set 500× looser because a **3-major cap does not guarantee** the optimiser has driven feasibility to its own tolerance, and because CL carries this case's limit-cycle scatter (CD peak-to-peak 9.0e-6 measured) |
| **G3 drag reduction** | PASS iff `CD_start − CD_final ≥ 10 η = 1.0910e-04`; **GATE FAIL otherwise, including a change that lies inside ±10 η** | thresholded on **this case's own measured noise floor**, not on a wished-for percentage. 10 η is 0.311 % of the 0.0350635 baseline: a drop this instrument can resolve ten times over. An unresolvable change does not support a drag-reduction claim and is graded GATE FAIL, not softened |
| **G4 endpoint FD-vs-adjoint** | aggregate vector-relative error **≤ 5.0 %**; **per component ≤ 10.0 %**; **zero sign flips** | the **start-design** measurement on this exact rung is **1.0432 % aggregate, worst 1.817 %**. The endpoint band is ~5× looser because (i) the endpoint design is warped away from the FFD reference and exercises the warp Jacobian harder, (ii) the step rule sizes steps from `\|J_adj\|` at a design never previously measured, (iii) **5 % is `DAFOAM_CHARTER.md` §2's own aggregate bar** — registering tighter would invent a standard, looser would be unfalsifiable |
| **G5 plateau** | `\|d(s_hi) − d(s_lo)\| / \|d(s_hi)\| ≤ 10.0 %` per component | the identical registered tolerance of `../rung_n16_remaining_components/PREREGISTRATION.md` §4.3, which separated the graded population (worst **3.651 %**) from flagged `twist` idx6 (**83.53 %**) without ever being adjusted |
| **G5 escalation** | **more than 2 of 8** components failing the plateau ⇒ **G4 as a whole is NOT A RESULT** | the endpoint FD reference is then not trustworthy and no aggregate may be quoted from it |
| **G7 clearance** | `C = 2·\|J_fd\|·s / η ≥ 5` at the graded step, on the **measured** `\|J_fd\|` | the rem item's registered bar, re-stated against the measurement rather than the proxy |
| **G6 memory** | predicted peak RSS **≤ 11.0 GiB**; hard cgroup cap **12 GiB** | 9.787 GiB measured for a single adjoint; +12 % for the optimiser's own state. 12 GiB is the cap `P2-a6-n16` and `P3-a6-n16-rem` both ran under |
| **P-BASE** | cold CD **exactly** `0.03506349413916734` | five independent reproductions. **If it misses, the twist-only edit is not numerically inert, the stored gradient column no longer describes this configuration, and G4 is NOT A RESULT** |
| **P-η endpoint** | measured endpoint η within **±50 %** of 1.0910e-05 | if it falls outside, clearances are re-stated at both η and any component clearing at one and not the other is **NOT A RESULT** — the rem item's own registered consequence branch, carried unchanged |

### 4.1 The step ladder — mechanical, registered, and a function of `|J_adj|` and η only

Carried from `../rung_n16_remaining_components/PREREGISTRATION.md` §4.2, unchanged in form:

> `C(s) = 2·|J_adj|·s / η`, η = **1.0910e-05**. **`s_lo`** = the smallest ladder rung with `C ≥ 5`.
> **`s_hi`** = the smallest ladder rung with `s_hi ≥ 2·s_lo`. The registered pair is `{s_lo, s_hi}`;
> **the graded step is `s_hi`, and it is NOT selected on agreement.** A component for which no rung
> reaches `C ≥ 5`, or for which no `s_hi` exists, is **NOT A RESULT** — no reference exists at any
> registered step — and is excluded **by name**, never rescued by a step at which it happens to cross.

**Two ladders are extended for D8, and the reason is registered here, before the endpoint gradients
exist:** near an optimum the reduced gradient shrinks, so a ladder sized for the start design can
run out of rungs at the endpoint and manufacture a NOT A RESULT out of the *instrument*, not the
case. Registered ladders:

* `twist` (degrees, DV bounds ±10): `{3e-2, 5e-2, 1e-1, 2e-1, 3e-1, 5e-1, 1e0}` — 1e0° is **5 %** of
  the design range and geometrically small; the rem ladder's top rung 3e-1 is retained inside it.
* `patchV` idx0 (U0, m s⁻¹, base 295.0): `{3e-2, 1e-1, 3e-1, 1e0, 3e0}` — 3e0 is **1.0 %** of base.
* `patchV` idx1 (AoA, degrees): `{1e-2, 3e-2, 1e-1, 3e-1, 1e0}`.

**The extension is proved not to be a rescue.** `d8_stepplan.py --selftest` reproduces the rem item's
registered `{s_lo, s_hi}` pairs **exactly** on all four of its twist components from their stored
adjoints, so the arithmetic frozen here is the arithmetic that produced the published plan. And the
extension is **explicitly declined as a rescue for `twist` idx6**: on the D8 ladder idx6's stored
`|J_adj| = 1.3619e-04` would nominally reach `C ≥ 5` at `3e-1`, and **it is excluded anyway, by
name, before compute** (§6). Extending a ladder and then keeping the component it now reaches would
be exactly the failure L-233's corollary names; and *a flag honoured only when it is cheap is not a
flag* (`../rung_n16_remaining_components/RESULTS.md` §4.2).

**The plan is not a human choice.** `d8_stepplan.py` (md5 §9) is the sole producer of `fdplan.json`
from the logged `ADJ_DERIV` values and the registered η. `RESULTS.md` will re-derive the plan from
the logged adjoints and assert it equals the plan that ran.

**Registered limitation, carried verbatim** (`../rung_n16_remaining_components/RESULTS.md` §3.1):
> *"The rule has not been tried where the proxy `|J_adj|` is itself wrong — which is the case it
> would be worst at, since it sizes the step from the very quantity under test."*

and (that item's `PREREGISTRATION.md` §9 item 9):
> *"The step-selection rule of §4.2 is registered, not validated."*

**This limitation bites harder here than there**, and it is registered as such: at the endpoint the
adjoint has *not* been verified before the step is sized from it — the verification is the thing this
item buys. A cleanly-passing G4 is therefore partly self-referential and §10 says so.

## 5. Ladder / decomposition

**`np = 1`. No decomposition. `numberOfSubdomains 1`; `nProcs : 1` asserted by the arm from its own
log.** Stated rather than left blank: **with np = 1 the parallel-determinism question does not
arise** — there is no decomposition seed, no rank-order reduction, no partition-boundary term, and
the ×4 `cores × wall` billing ambiguity that a multi-rank arm must disclose does not exist because
`--cpus=1` makes `ranks × wall` and `cores × wall` the same number. No `decomposeParDict` is written
and no `processor*` directory may exist at launch (asserted by `d8_run_arm.sh`, G8).

## 6. `twist` idx6 — NAMED `NOT A RESULT` IN ADVANCE

> **`twist` idx6 is `NOT A RESULT` for this item, registered here before any solver arm runs.**
> **Reason:** it is FD-ungradeable on this rung — **no finite-difference reference exists at any
> feasible step**; its plateau disagreement is **83.53 %** against a 10 % bar and its best clearance
> **2.42×** against a bar of 5 (`../rung_n16_remaining_components/RESULTS.md` §4.1 row 9, the row 37
> the curriculum names). It is excluded **by name** from every table, every aggregate and every
> average in this item, and it is **not measured**, not merely omitted.
>
> **Consequence, stated plainly: the endpoint gradient verification of this item is 8-of-9 BY
> CONSTRUCTION. This item cannot and does not claim a 9-of-9 gradient on A6 N=16, and no reader may
> take its G4 verdict as one.** The flagged-component gap is a registered boundary of the case, not a
> defect of this run and not something this run repairs.
>
> The grader enforces it mechanically: `d8_grade.py` **refuses (exit 2)** if `twist` idx6 appears in
> the FD table at all, and its negative control proves that refusal fires.

## 7. Criteria and gates

* **G0 identity/activity.** `IDWARP_SO_MD5 == 85f59e87253e0a71a813f64ca6e4c425` printed by the arm
  itself; image **ID** `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`
  asserted by the launcher; `transonicPCOption 1;` in the option dump (**activity proof**);
  `nProcs : 1`; `Mesh region0 size: 41760`. **Any failure ⇒ the arm is VOID and nothing below is
  graded** — the grader refuses rather than grading a void arm.
* **G1 termination.** `EXIT: Optimal Solution Found.` **and** the arm's own `D8_OPT_ARM_COMPLETE`
  marker ⇒ **PASS**. Stop at the registered 3-major cap (`Maximum Number of Iterations Exceeded`)
  ⇒ **GATE REACHED**, *never* `PASS` — **a stop is not a measurement** (`DAFOAM_CHARTER.md` §7).
  An adjoint `-9`-class exit / `Adjoint solution failed` / `AnalysisError` ⇒ **`BLOCKED`, recorded and
  triaged, never skipped and never silently retried.** Anything else ⇒ **NOT A RESULT**.
* **G2, G3, G4, G5, G7** per §4.
* **The bright line.** `DAFOAM_CHARTER.md` §2: *a DAFoam gradient is not a result until a
  finite-difference table stands beside it at a step proved to lie in the plateau.* **The endpoint
  adjoint of this item is not a result until arm `fd` returns.** If arm `fd` does not run or does not
  complete, **G4/G5/G7 are `PENDING`** — named, priced, never absorbed — and the item claims no
  gradient at the endpoint.
* **Completion rule, all clauses** (CLAUDE.md rule 4): `rc = 0`; the arm's `D8_*_ARM_COMPLETE`
  marker present; `ASSERT_MD5 OK` in the ledger; the launcher's **G8 cold-start guard refuses to
  launch into a directory holding a written time directory, a `processor*` or a `reports/`**. The
  grader **refuses (exit 2) rather than degrades**.
* **Planted-zero control** (CLAUDE.md rule 3) on **every** gate that reads a number. `d8_grade.py`
  runs 18 checks including **six negative controls** and **will not grade unless its selftest passes
  in the same invocation**. The FD gate **asserts the parsed component count is exactly 8, prints the
  count, and refuses on any other value**; its negative controls prove the refusal fires on a
  7-component set, on a 0-component set, on a 1-step component and on an idx6 leak. This is aimed at
  a live defect in this family: `curriculum_D3/d3_grade.py`'s G3+G4 returns **`PASS` at 0.0000 % with
  zero sign flips over an EMPTY component set**, because a present-but-unparseable FD block leaves
  the dict key present with an empty list and the refusal tests key presence, never non-emptiness —
  **a partial plant reads on the page exactly like a complete one** (L-302). Peak RSS is
  **initialised** and a missing / empty / unparseable sample file **refuses**, never prints `0.000`
  — the `A3/*/drive.sh` defect that already fired for real at
  `curriculum_D3_attempt2/RESULTS.md:76` (`peak_rss_GiB=11` against a true 0.5973 GiB).

### 7.1 Memory envelope — registered as a gate, with the censoring rule written in advance

* Hard **cgroup cap 12 GiB**, `--memory=12g --memory-swap=12g --oom-score-adj=500` — a **kernel-only
  stop**; no watcher process kills anything, and the RSS sampler **records only**. `--rm` is **not**
  used so `docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}'` survives the arm; at a
  9.787 GiB basis that read is the only thing separating a cap-kill from a genuine failure.
* **`MemAvailable ≥ 12 GiB` is checked from `/proc/meminfo` immediately before the launch and the
  launcher aborts if it is not met** — the standing floor on Sanaa's desk. An arm that never launches
  on this condition is **`BLOCKED`, never `GATE FAIL`**. Both the pre- and post-arm readings are
  written to the ledger. Reading at filing: **MemAvailable 26.88 GiB**, no peer container running.
* **THE CENSORING RULE, registered in advance and in my own words: a cap-kill is not a measurement of
  failure — it is a measurement of the cap.** If the arm returns `rc = 137`, or
  `OOMKilled = true`, or `memory.peak` lands at or above the registered 12 GiB cap, the peak-RSS
  observation is **right-censored**: the true requirement is somewhere above the cap and the run
  never got to say where. The registered verdict for that outcome is **`PENDING`, NOT `GATE FAIL`**.
  Precedent: W4's O2 re-buy registered a 20.0 GiB cap, `splu` hit it, `rc 137`, `memory.peak` exactly
  **21,474,836,480 B**, and the frozen rule mapped that to `PENDING`. **A `GATE FAIL` would assert a
  fact the measurement cannot support**, and a `PASS` would be worse. The same rule binds here.
* **Only ONE arm holding an adjoint runs at a time.** Two concurrent A6 adjoints would need
  2 × 9.787 = **19.6 GiB**, leaving under 9 GiB and breaching the 12 GiB floor. This is also the
  registered reason the shipped row is not bought in parallel (§10).

## 8. Cost — core-minutes, priced honestly, with the direction of the error named

| line | predicted | ceiling | basis |
|---|---|---|---|
| pre-registration image read (already spent, **measured**) | — | — | **0.217** |
| arm **`opt`**: trim (≤ 4 Newton iters × 2 primals + 1 closing primal) | 15.8 | | 105 s/primal |
| arm **`opt`**: **3 IPOPT majors** × (1 primal + 2 flow adjoints) | 62.3 | | 105 s + 2 × 570 s |
| arm **`opt`**: endpoint re-evaluation + **1** CD adjoint | 11.2 | | `compute_totals(of=[CD])` — one adjoint, not two |
| **arm `opt` subtotal** | **89.3** | **135.0** | container `timeout 10800 s` as a backstop |
| arm **`fd`**: 1 baseline primal + 8 components × 2 steps × 2 signs = 32 primals | 57.8 | **75.0** | 105 s/primal, `timeout 7200 s` |
| **TOTAL** | **147.3 core-min** | **215.0 core-min** | |

**$ derived at $0.0513/core-h: predicted $0.126, ceiling $0.184.**
`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED` — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Well inside the $25 pre-authorisation; the
authorisation is not treated as a ceiling of its own (CLAUDE.md rule 9).

**AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET. The stop threshold is 215.0 core-min
across both arms**, read from the ledger's `core_min` column. If arm `opt` alone exceeds 135.0
core-min the item stops there and G4/G5/G7 are `PENDING`, priced and named.

**Which way this estimate errs, and why.** It errs **conservative (high)**, deliberately, in three
places: it prices **two** flow adjoints per major with **no** PC reuse between the CD and CL solves;
it prices every primal at the cold 105 s when majors restart warm (measured warm restarts run
~59 s of solver time); and it prices IPOPT line-search primals as if a full step were not taken.
**The named precedent for erring the other way is D1**, which came in at **0.304×** its prediction
because IPOPT took full steps on all 11 majors and the line-search primals priced into every major
were never bought. D8 therefore expects to **undershoot**, and `docs/COST_CALIBRATION.md` will carry
the ratio and its attribution at completion (CLAUDE.md rule 12).

**The curriculum's own figure is departed from, before compute, with the reason.**
`EXPERTISE_CURRICULUM.md` prices D8 at **80–120 core-min / $0.07–0.10**. That figure prices the
primals and **does not price the adjoint**: at 570 s each and two per major, three majors alone are
57 core-min of adjoint. The registered prediction is **147.3 core-min / $0.126** and the departure
is recorded here rather than discovered in the results.

## 9. Toolchain — pinned by IMAGE ID, and the instruments frozen by md5

`DAFOAM_CHARTER.md` §11: **the hash is the identity; the version string is not.**

| | value |
|---|---|
| image (this item's ONLY row) | `dafoam-idwarp-rot:v1` |
| **image ID** | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` |
| IDWarp rotation patch, asserted **by the running container** | `IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425` |
| stock image, **not run here** | `dafoam/opt-packages:latest`, ID `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`, `IDWARP_SO_MD5 f0fcb488e0e98156575cd19548e91663` |

**Noted, because it is easy to get wrong: the IDWarp rotation patch is in NO stock container image.**
`dafoam-subpclu:v1` and `dafoam-kspopts:v1` both carry **stock** IDWarp. Only
`dafoam-idwarp-rot:v1` carries the patch, and the arm proves it ran by printing the `.so` md5 from
inside the container and asserting it — an arm whose log lacks `ASSERT_MD5 OK` is **VOID**.

**Frozen instruments, in this directory, by md5 at this commit:**

| file | md5 | role |
|---|---|---|
| `d8_gen_arm.py` | `0b8a8b3449363287237e8136aaf13128` | producer: 8 anchored edits to `base/runScript.py`, each asserting anchor count == 1 |
| `d8_run_arm.sh` | `cd66ead4b0dc1a26e460ea6bcc719551` | launcher: memory floor, image ID, G8 cold start, kernel-only stop, record-only RSS |
| `d8_stepplan.py` | `8be156d5cff3ef373d3bf359eddcb317` | the mechanical step rule → `fdplan.json` |
| `d8_grade.py` | `04bba79c2a303bc3cf70af723da81dce` | grader: 18 selftest checks, 6 negative controls, refuses (exit 2) rather than degrades |

**The grading path is fixed at this commit** (CLAUDE.md rule 2). `RESULTS.md` will verify the frozen
files **are** the files that ran by hashing the working copies against these committed blobs.

**Producer inputs:** `base/` copied file-for-file from `P3-a6-n16-rem/base/`;
`runScript.py` md5 `0de915d21166a91a9a54b37ab11214cf`,
`constant/polyMesh/points.gz` md5 `11b84f0de5fdf2d3e947fee8cea412a9` — both equal to the
fixed-reference tree. Arm parameters: `endTime 1000`, `primalMinResTolDiff 1.0e4`,
`primalMinIters 1000`, `printInterval 10`, IPOPT `max_iter 3`.

**Why `primalMinResTolDiff` is load-bearing and not cosmetic:** the A6 primal stops **556×** short of
`primalMinResTol`, and `DASolver::checkPrimalFailure()` (`DASolver.C:2744-2752`) converts that into a
hard `AnalysisError` against a shipped cap of 100. Without this edit **every primal in the
optimisation dies** — measured, `../rung_n16_np1/RESULTS.md` §3. `primalMinIters == endTime` closes
`DASolver.C:188`'s `-1e10` false-convergence exit (N-D17).

## 10. The two-row rule — ONE ROW IS BOUGHT, AND THE OTHER IS NAMED UNBOUGHT

`DAFOAM_CHARTER.md` §6: **a DAFoam verdict is two rows, shipped and patched, or it is not a verdict
about DAFoam.** A6 N=16's gradient row is already `GATE FAIL` (shipped) / `PASS` at 8 of 9 (patched),
and **`twist` DVs cross the IDWarp warp**, so the distinction is live here, not academic.

> **This item buys the PATCHED row only** — `dafoam-idwarp-rot:v1`.
> **The SHIPPED row is NOT BOUGHT and is named unbought.**
>
> **Why.** (i) **Memory:** two adjoint-bearing arms cannot run concurrently — 2 × 9.787 GiB = 19.6 GiB
> would leave under 9 GiB and breach the standing 12 GiB `MemAvailable` floor — so a second row is
> strictly sequential and doubles a ~2.5 h item. (ii) **Grading:** the endpoint FD table's step rule
> is seeded from the patched adjoint column, and the 8-of-9 graded reference this item measures
> against is itself a patched-image row (`../rung_n16_remaining_components` §0). A shipped row would
> need its own seeded plan and its own reference.
>
> **CONSEQUENCE, stated plainly: this item CANNOT claim a toolchain-independent result.** Whatever
> G4 returns is a statement about DAFoam **with the IDWarp rotation patch applied** and about nothing
> else. The shipped row for this configuration is **`PENDING`** — named, not absorbed — and its price
> is the same ~147 core-min again.

## 11. Verdict vocabulary

`PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING` — the six tokens
(`DAFOAM_CHARTER.md` §8; CLAUDE.md rule 1). No other word grades an arm here, and no adjective
softens one. A verdict is valid only against a falsifier written in this file before the run.
An arm that never launches on the §7.1 memory condition is **`BLOCKED`**. A component not reached at
the ceiling is **`PENDING`**, by name and with its price. A cap-stop is **`GATE REACHED`**, never
`PASS`. A right-censored memory observation is **`PENDING`**, never `GATE FAIL`.
**A stop is not a measurement.**

## 12. What this item is NOT for

It does not touch **A6 N=29** (never run; its wording is Sanaa's, D464), the 399,360-cell **A3**
campaign, or **D16a**. It does not re-grade, revise or merge any existing A6 row. It does not repair
`twist` idx6 and does not claim a 9-of-9 gradient. It grades the `shape` group not at all —
`shape` is removed from the problem, and remains **`PENDING`** for this family exactly as before.
