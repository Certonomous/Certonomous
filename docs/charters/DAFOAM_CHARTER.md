# Certonomous DAFoam Charter

Version 1.0c, dated 2026-08-22. Governs every discrete-adjoint CFD result this lab produces
with DAFoam, IDWarp, pyGeo, pyOptSparse and the OpenFOAM builds under them: gradient
verification, adjoint linear-solver failures, patched-toolchain rebuilds, mesh-warp
derivatives, decomposition effects, and any optimisation driven by one of those gradients.
It binds `cases/dafoam/` in full — Ladder A, Ladder B, the S1/W4/W5 wells, `patched_build/`
and the defect and liaison records — the run trees under `/home/ubuntu/certonomous-runs/`
that feed them, and any DAFoam number that reaches a record, a report or a camera surface.

It is the **twelfth** charter — the eleventh was `CLOSURE_MODELLING_CHARTER.md`, adopted
2026-08-20. It exists because the DAFoam ladders have now produced, across three weeks, a
published 11.43 % gradient error that a step-size sweep had to be bought to defend; a
verification clearance for A5 that was retracted when an arbitrary random seed was replaced
by the objective's own and two components moved 160×; a "PASS" that was really a decomposition
artefact and an 8.95 %-versus-0.00054 % split nobody had looked for; a 47-iteration IPOPT run
whose own log carries no convergence statement; a `-9` that four different upstream defect
classes now describe and **none of which has been filed**; and an unblocking image built by
`docker commit` in a scratch tree that no longer exists. Every clause below names the thing
that earned it.

## 1. The line

> **A DAFoam gradient is not a result until a finite-difference table stands beside it at a
> step proved to lie in the plateau, and a DAFoam verdict is two rows — shipped and patched —
> or it is not a verdict about DAFoam.**

Two clauses because this charter guards two different failures, and the lab has committed
both. The first is the gradient believed because the adjoint converged: `PetscConvergedReason: 2`
is a statement about a Krylov solve, not about a derivative, and A4's scotch arm converged at
true-residual **1.7e-07** on an operator that is **328.8× ‖b‖** away from the transpose Jacobian
(`docs/dafoam/PRIOR_WORK_INVENTORY.md` §1e; `cases/dafoam/DISCRIMINATORS_A4_decomposition_mechanism.md`).
The second is the patched number quoted as the toolchain's: every unblocked adjoint on Ladder B
ran on a locally rebuilt library that **has never been filed upstream and ships nowhere**, and a
reader given one row cannot tell which library produced it.

---

# PART I — WHAT MAKES A DAFOAM GRADIENT A RESULT

## 2. Every adjoint gradient ships a finite-difference table, and it is graded on the band the verification charter fixes

> **No DAFoam gradient enters a record, a report or an optimisation without a finite-difference
> table beside it. The table is graded PASS at ≤ 5 % aggregate with zero flagged components,
> CONDITIONAL between 5 % and 15 % and then only with a per-component breakdown, and FAIL above
> 15 % or on any sign-flipped component regardless of the aggregate. The aggregate is named as a
> statistic — this lab's is the vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` as printed — and
> the per-component flags are reported beside it, never instead of it.**

**Cross-reference, not duplication.** `VERIFICATION_CHARTER.md` §7 owns the band, the five-step
reporting protocol and the harness floor, and `FAMILY_SUPERVISION_GUIDELINES.md` §4.2–4.3 owns the
operational half (`check_totals`, central differences, `step_calc="abs"`, one error convention
throughout). This clause adds the two things neither can say for DAFoam.

**First: the statistic is not the one the toolchain's own authors use, and the two must never be
compared.** All three DAFoam/ADflow method papers were read in full
(`cases/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`). **No paper uses a vector-norm relative
error.** He, Mader, Martins & Maki (C&F 168, 2018) §3.1 Tables 4–5 and (AIAA J, DOI
10.2514/1.J058853) §2.4.2 Table 3 report **per-component and per-row** relative error and quote
*"the average relative error is less than 0.1 %"*; Kenway, Mader, He & Martins (PAS 2019) §5.1
reports **agreement in significant digits** and explicitly declines finite differences as a
reference, using **complex step** for ADflow and full-code AD for DAFoam. Every headline
percentage in this lab's ladder records is a vector norm. **A vector norm and an average
per-component error are different statistics, and quoting one against the other is forbidden.**

**Second: where a complex-step or forward-AD reference is available, it is the reference.**
PAS 2019 §5.1 measures the Jacobian-free adjoint to **10 digits** (DAFoam) and **12 digits**
(ADflow) against a non-FD reference, while the **FD-Jacobian** option in the same table reaches
only **3–4 digits, ~0.1 % average**. The images on this box ship `libDASolverADF.so` — a forward-AD
build — in all three tags (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §6a;
`cases/dafoam/patched_build/subpclu/BUILD.md` §4.2 G1). **A record that reports only an FD table
where a forward-AD or complex-step reference was reachable states that it did not reach for it,
and why.** No lane has yet done this, and saying so is the point of the clause.

**The harness floor, and the trap in reading it.** `VERIFICATION_CHARTER.md` §7 step 4 states a
**floor** of 2.5–5 % vector-norm relative error on this stack and warns that *"a number below that
is a claim about the harness."* Every S1 CBFS field-inversion FD number sits one to two orders
**below** it — 0.085 % / 0.059 % / 0.199 % (`ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §5d), 0.032 % /
0.115 % / 0.009 % (`S1_CBFS_REINVERSION_PREREGISTRATION.md` Amendment 1 §C), 0.0211 % on a cell the
lab never published (`VERIFICATION_cbfs_unblock_supervisor_sweep.md`). **That floor is calibrated on
shape derivatives through IDWarp; a per-cell field DV has no mesh warp in its chain at all**
(`S1_FIML_FIELD_INVERSION.md` §1: `WARP PROBE: {"warper_init": 0, "warper_jacvec": 0}`). **The two
are not the same instrument, and this charter records that so §7 step 4 is not read as an
accusation against the S1 numbers.** A DAFoam record states which instrument it is on.

**What is forbidden.** Quoting an adjoint gradient with no FD table. Reporting an aggregate with
the flagged components dropped and not saying so. Comparing this lab's vector norm against a
published per-component average. Calling a `PetscConvergedReason: 2` a verified gradient.

## 3. The step is proved to lie in the plateau by a sweep, and a flat curve is per component or it is not flat

> **The sweep is run at the primal tolerance the graded run uses, and the plateau is read per
> component, not off the vector. A component whose FD estimate does not stabilise anywhere in the
> sweep is flagged and excluded by name from any aggregate quoted as agreement — never dropped
> silently, and never rescued by a step at which it happens to cross.**

**Cross-reference, not duplication.** `VERIFICATION_CHARTER.md` §7 already requires the sweep and
already fixes its table shape — `| step | rel err | rel err (excl. flagged) | cosine | status |`
with the failed steps as rows, because *"a sweep that hides its failed steps is reporting a plateau
it did not measure"* (`:882-891`), and `REPORTING_CHARTER.md` §7 rule 2 repeats the duty on the
reporting side. **This clause adds the two things a DAFoam sweep gets wrong that neither can see:
the tolerance the sweep runs at, and the level the plateau is read at.**

**The measurement that earned it.** `ladder-a/A_stepsize_study.md` — twelve invocations on A1,
4,032 cells, np=2, one step varying and nothing else. The full 8-vector error against step reads
**94.95 % / 52.88 % / 17.64 % / 12.27 % / 11.52 % / 11.43 % / 10.47 % / 8.94 % / 4.28 % / 9.83 %**
from 1e-8 to 3e-2, and the primal itself **fails** at 5e-2 and 1e-1. **The 4.28 % dip at 2e-2 is
not a minimum**: it is one component, idx6, whose estimate is sign-flipped and unstable at every
other step, crossing the adjoint's magnitude once on its way to +110 % at 3e-2. Excluding idx0,
idx1 and idx6 the curve is **dead flat at 2.5–3.0 % from 1e-4 to 3e-2, cosine 0.99998** — the real
plateau, and it belongs to five of eight components, not to the vector.

**Two more incidents make this a bright line rather than advice.** (i) `S1_CBFS_REINVERSION_PREREGISTRATION.md`
Amendment 1 §B: at `primalMinResTol 1e-6` the cold primal stops at its **first** tolerance crossing
(iterations 383–458) and central FD misses the adjoint by a systematic `fd/adj ≈ 0.7` on all three
cells — **25.9 % / 32.0 % / 32.2 %**. One pair re-run at 1e-8 moves the same cell from **25.9 % to
0.032 %**. **The step was never the problem; the primal's stopping rule was.** A step sweep at a
loose primal tolerance defends nothing, so the sweep is run at the tolerance the graded run uses.
(ii) `VERIFICATION_CHARTER.md` §7's closing caution — *"do not prescribe 'converge harder' before
checking whether convergence is available"* — has its DAFoam instance in A5, where tightening
solver tolerances 1–2 orders and running 10× more iterations moved the aggregate **46.64 % → 46.21 %
and made the sign flips worse, 2 → 3** (`ladder-a/A5_ubend_internal.md`).

**What is forbidden.** Quoting an FD number from a single step. Reporting an aggregate computed
with unstable components silently removed. Selecting the step after seeing which one agrees.

## 4. The registered trivial baseline for a DAFoam FD gate is the same probe at a deliberately wrong step

> **A finite-difference gate whose verdict is counted as evidence names its trivial baseline in
> the preregistration, before its own run. For a DAFoam FD gate that baseline is the same probe
> at a step chosen to be wrong — an order of magnitude off the registered one. If the wrong step
> also passes, the gate is not measuring what it claims and the verdict it produced is withdrawn.**

**This is `VERIFICATION_CHARTER.md` §2c instantiated for this lane**, exactly as
`CLOSURE_MODELLING_CHARTER.md` §3 instantiates it for anisotropy by naming the train-mean tensor.
§2c's reach-limit 3 says *"what counts as the trivial baseline is a judgement, not a datum"* and
requires it registered before its own run; this clause fixes the judgement so no DAFoam
preregistration has to re-derive it.

**The incident, and it is this lane's own.** `S1_SENSITIVITY_VS_ERROR.md` §3 measured gate G2 —
a GRADE row carried by two full inversion campaigns — **scored on the baseline gradient alone, an
array with no inversion result in it: 35.38 %**, against the inversion's achieved 26.86 %, and
reproduced at 31.19 % from a second independent baseline gradient. **The trivial baseline beat the
hypothesis.** The record's own conclusion is §2c in this lane's words: *"G2 as currently defined is
therefore scoring the adjoint's sensitivity map, not the closure's error location."*
`docs/dafoam/PRIOR_WORK_INVENTORY.md` §7 Tier 0 item 0.5 carries the open action; this clause
closes it for FD gates and names `|g(β = 1)|` scored under the same rule as the standing trivial
baseline for a **field-inversion** gate.

**Worked example, 2026-08-21.** `cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/PREREGISTRATION.md`
§"The Charter-2c trivial baseline" registered cell 5491 at **h = 0.5**, ten times the registered
step, predicting **> 2 %** against the real probes' < 1 % bar, before any arm ran. Its measured
outcome is in that item's `RESULTS.md` §5. **The baseline was registered in writing before its own
run, which is the whole of the rule.**

## 5. Serial before parallel, and every parallel gradient discloses its decomposition

> **A DAFoam gradient measured at np > 1 states the decomposition method and, for `simple`, the
> subdivision, in the same table as the number. A new case's first FD verification is run at
> np = 1 before any parallel figure is graded, and where both exist both are reported. A gradient
> verified at one np is a statement about that np and is never carried to another.**

**The measurement that earned it.** A4 Ahmed-25, 2,777 cells, one scalar FFD shape DV, patched
IDWarp, everything else held: **np=4 `scotch` 8.95 %; np=4 `simple` 4×1×1 0.00054 %** — a factor of
**16,600 between two decompositions of the same mesh**. The effect is np-dependent as well —
np=1 0.34 %, np=2 0.26 %, **np=3 6.05 %**, np=4-scotch 8.95 % — and the hanging-node explanation is
refuted backwards: scotch cuts **4 of 456** refinement-interface faces and `simple` 4×1×1 cuts
**68**, and the 68-cut arm is the clean one (`docs/dafoam/PRIOR_WORK_INVENTORY.md` §1e, §5.4;
`cases/dafoam/DISCRIMINATORS_A4_decomposition_mechanism.md`). A4's published 10.04 % stood for two
days as a gradient defect before the decomposition was varied; the graded configuration is now
**np=1 against the shipped toolchain, 1.10 %**.

**The carrying failure, stated because it is subtler than the first.** `W4_IDX16_IS_THE_REFERENCE.md`
records that A5's stored FD reference for component idx16 is **np=4-specific**, and A5's claimed
decomposition-invariance is cited from a run whose `PYTHONPATH` pointed at the patched IDWarp —
so it covers the patched gradient, not the stock one it is cited for
(`docs/dafoam/PRIOR_WORK_INVENTORY.md` §1f, "what remains open"). **An FD reference is part of a
configuration, not a property of a case.**

**The parent rule, which this instantiates rather than invents.** `VERIFICATION_CHARTER.md` §6
(`:766-770`): *"anything a surface states about how a number was produced is subject to the
evidence record. Ranks, wall time, cell count, solver name, iteration count. If the run did not do
it, the surface does not say it."* **The decomposition is such a statement and is the one this
lane has repeatedly left out**, so it is named: method, `numberOfSubdomains`, and for `simple` the
subdivision.

**Why the papers cannot help here.** *"No paper ever varies the decomposition of anything — not at
fixed np, not across np"*; the words "decompose", "processor" and "scotch" are absent from the AIAA J
paper entirely (`DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`; inventory §7 consequence 2). The lab ran
the papers' own C&F 2018 Table-4 acceptance check on the defect's own case at np=1 and np=4-scotch
and got **3.55 % and 3.68 %** — it passes on both sides. **A single-decomposition protocol cannot see
this defect even in principle**, and the pre-registered prediction that it would was REFUTED.

**What is forbidden.** A parallel gradient table with no decomposition column. Carrying an FD
reference across np. Describing a case as decomposition-invariant from one arm.

---

# PART II — WHAT MAKES A DAFOAM RUN REPORTABLE

## 6. Shipped and patched are always two rows, and toolchain identity is an image ID and a library hash, never a version string

> **Every DAFoam verdict is recorded as two rows — one against the shipped toolchain, one against
> whatever was patched — and a patched row never replaces a shipped row. Both rows carry the
> identity of the thing that produced them: the container image tag **and** its image ID, plus the
> md5 and line count of the patched source or the built `.so` where a patch is involved. A version
> string is not an identity.**

**Why the version string is not an identity, measured.** The IDWarp rotation patch changes the
reverse-mode derivative by seven orders of magnitude on the defect's own DOFs — issue-57 DOF 0 goes
**210.16 % → 8.56e-06 %** — and **the version string still reads `2.6.2` either way**, because the
patch is a hand-edit of Tapenade output injected by bind-mount and `PYTHONPATH` with **no container
image at all** (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §4; `PATCH_getRotationMatrix3d.md` §10). That
is why every regrade log prints `IDWARP_IMPORTED_FROM:` as its provenance stamp. On the DAFoam side
the same holds: all three images report DAFoam **5.0.0**, OpenFOAM **v2506**, PETSc **3.15.5**, and
differ only in `DALinearEqn.C` — md5 `f6a89e33…` / 507 lines (stock), `89e71ca2…` / 526
(`dafoam-subpclu:v1`), `96f57628…` / 534 (`dafoam-kspopts:v1`), `5b3159f8…` / 539
(`dafoam-subpclu:v2`) — `TOOLCHAIN_INVENTORY.md` §3, `patched_build/subpclu/BUILD.md` §4.3.

**The incident that earned the hash.** `dafoam-subpclu:v1` produced **every recorded sub-LU number
in this lab** and was built by a hand-run `docker run` / `docker commit` in a session whose scratch
tree no longer exists. The patch file on disk was **one hunk ahead of the built image** and said so
only in its own provenance header (`TOOLCHAIN_INVENTORY.md` §3, finding B-1). The repair was a
`Dockerfile` and four substitute gates, because md5 equality with `v1` was **predicted to fail by
construction and did**; what `patched_build/subpclu/BUILD.md` §4.2 gate G2c establishes instead is
stronger — `diff v1 v2` is **13 added lines, all inside an `else if` branch entered only for a
`DAFOAM_SUBPC_TYPE` value that is neither unset nor `lu`**, so **the numeric path of `v2` is
byte-identical to the image that produced `reason 2 / 667 iterations`**. **The named images are
`dafoam-idwarp-rot:v1` and `dafoam-subpclu:v2`; a DAFoam record naming a patched result names one of
them, or the host clone and the `IDWARP_IMPORTED_FROM:` stamp.**

**The second incident, and it is about silence.** `strcmp(subPCTypeEnv, "lu")` is an exact match, so
`LU`, `Lu`, `lu ` with a trailing space or `superlu` **all run stock ILU with no message**, and *"a run
believed patched can be stock"* (`SUPERVISOR_FAMILY_REVIEW_2026-08-07.md` finding B-1). **The in-log
banner `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` is asserted in the log before any
sub-LU result is trusted, and its absence is the standing proof a run was stock.** Likewise the cold
start: pyDAFoam writes the primal end state back into the time-0 directory at run end, so the second
run of a case directory silently warm-starts — the staged-copy pattern or a checked first
`Time step continuity errors` value is mandatory (`FAMILY_SUPERVISION_GUIDELINES.md` §8;
`WARMSTART_AUDIT.md`).

**A third identity fact, measured inside another charter and worth carrying here.**
`VERIFICATION_CHARTER.md` §13 (`:1168-1171`) records that the host runs OpenFOAM **v2606** while
the DAFoam container ships **v2506** — *"two different OpenFOAM versions in one lab"* — and B2's
own reproduction measured the consequence: a fork gap of **10–13 % in iteration count** and
**0.02–0.09 % in the fields** between OpenFOAM-7 and v2606 on the same cases
(`ladder-b/B2_duct_baseline.md`). **A DAFoam number and a plain-OpenFOAM number are not on the same
toolchain even when both are "OpenFOAM".**

**R11 is the grading rule this clause serves and does not restate**: a patched grade replaces a
shipped grade only if the fix ships upstream or Sanaa adopts a forked toolchain, and that is her
call, not a session's (`FAMILY_SUPERVISION_GUIDELINES.md` §3.4, and `SUPERVISOR_RULINGS.md:195` in the same words —
*"grade against the shipped toolchain; patched numbers sit beside them"*). **B3 is `BLOCKED` against
the shipped toolchain today and `PASS` against `dafoam-subpclu:v2`, and both sentences are true.**

## 7. The memory envelope is predicted, stated and checked before any adjoint launches

> **A preregistration that launches an adjoint states its predicted peak memory and the host
> headroom it needs, before the run. A run that stops because the host ran out of memory is
> recorded as stopped by memory and is NOT A RESULT about convergence. A run that stops because a
> human or a watchdog intervened on a shared box records that too, by name, and claims nothing
> about the envelope.**

**The incident, A3 campaign 1, 2026-07-28.** The ONERA M6 adjoint at 399,360 cells died of memory
under **eight** mitigations — two memory caps (12g, 18g), two rank counts, `gmresRestart` 1000→200,
`pcFillLevel` 1→0 — OOM at 399,360 **and** at 99,840, and `decomposePar` SEGV twice at 24,960. The
root cause is structural and worth stating once: OpenMDAO's reverse sweep builds
`d[residuals]/d[vol_coords]` for **any** requested total derivative, so restricting `wrt=patchV`
does not avoid a mesh-sized matrix (`ladder-a/A3_onera_m6.md`; inventory §1d).

**The second incident, A6, is the reason the prediction must precede the launch.** A6 CRM-wing,
**579,072 cells**, `Global Adjoint States: 5244840`: the memory envelope for a full adjoint is
predicted at **95–116 GiB against a 30 GiB box**, so the adjoint is `BLOCKED` and **no adjoint was
ever attempted** — `Main iteration` and `KSP Residual` appear **zero** times in all four A6 logs
(`ladder-a/A6/adjoint_feasibility/RESULTS.md`; `S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §3.7).
**The prediction is what makes the BLOCKED honest**, and it cost nothing to make.

**The third, and it is the one this clause most exists to prevent.** The NASA-hump sub-LU attempt
ran to ~900 iterations and was ended by a `docker stop` this lab issued because a **shared** box had
fallen to `MemAvailable` **1.62 GB**. The record's own correction is unambiguous: *"the memory
envelope was never shown to be binding … no PETSc memory error is on the record for this run"*, and
headline 3 was **WITHDRAWN as a causal claim**, leaving *"the NASA-hump adjoint boundary is
uncharacterised"* (`W4_ADJOINT_PC_UNBLOCK.md` §5b.1). **A stop is not a measurement, and this lane
has already published one as if it were.**

**And the clause must not become the opposite error, which the compute charter already names.**
`COMPUTE_BUDGET_CHARTER.md:183-188` carries **L-15** for exactly this reason: an adjoint that works
at 63,920 cells and breaks at 79,560 **with over 4 GB of headroom unused is bound by convergence,
not by RAM**, and *"a hardware recommendation was once made in the wrong direction on exactly that
confusion."* A3 rung 3 is the same shape — `reason -3` at a **peak of 11.65 GiB against a 22 GiB
cap**. **A6 is BLOCKED twice over, and the record says both**: memory at 94.7–116 GiB against a
30 GiB box, and conditioning independently, since the same solver family stagnates at 79,560 cells
with memory comfortable and A6 is **7.3×** larger than the largest rung that converges. **Naming
only the memory blocker would have been the L-15 error again.**

**Cross-reference.** `COMPUTE_BUDGET_CHARTER.md` §4 owns the auto-stop contract and the three-number
session budget (core-minutes, cores, memory, container-enforced with explicit `--cpus`/`--memory`);
this clause adds only that the **prediction is written down before the launch** and that a
memory-ended run is graded as such.

## 8. The verdict vocabulary is the six tokens, and this lane uses all six

> **The permitted verdicts are `PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`,
> `PENDING`. No other word grades a DAFoam run. A verdict is valid only against a falsifier that
> was in the preregistration before the run.**

**All six are defined in exactly one place — `CLOSURE_MODELLING_CHARTER.md` §12** — and this charter
adopts that table by reference rather than restating it. **The conflict is disclosed rather than
inherited**: `VERIFICATION_CHARTER.md:95-96` and `REPORTING_CHARTER.md:210-211` both fix the vocabulary and
both list **five** tokens, omitting `PENDING`, and neither defines any of them. §12's own wording is
*"no other word grades a **closure** run"*, so it does not reach this lane by its own text —
**this clause adopts it for DAFoam explicitly, which is why the adoption is written down rather
than assumed.** `docs/DOCKET.md`
uses `PENDING` **36 times**; `LESSONS.md` L-180 recommends it as the honest verdict where
`GATE FAIL` was written. **The five-token lists are treated here as the incomplete ones**, and the
repair is proposed, not taken — see §14.1. `docs/dafoam/PRIOR_WORK_INVENTORY.md` §7 Tier 0 item 0.5
raised this as an open action; this clause answers it for DAFoam and nowhere else.

**Two tokens this lane has misused, both named so they are not repeated.** (i) **`GATE REACHED`
after the deviation was read.** `docs/DOCKET.md:748` (D383) names F6a's `+13.9 %` reattachment row:
*"there is no miss large enough to have failed it."* A token chosen after the number is not a
verdict. (ii) **`PASS` on an unfinished optimiser** — §9. Two adjacent labels are **not** verdicts
and are not to be used as ones: `NOT OBTAINED` is a statement about a document
(`VERIFICATION_CHARTER.md` §6b) and `UNPRICED` is a statement about a cost
(`COMPUTE_BUDGET_CHARTER.md` §390–395).

**A stop at a cap is recorded budget-capped, not converged.** `S1_CBFS_REINVERSION_RESULT.md` is the
worked example that does it right: 424.80 of 450 core-min, *"recorded budget-capped, not
converged"*, with `G1 PASS, G2 FAIL` stated separately.

## 9. An optimiser stopped by wall clock or iteration cap is GATE REACHED or NOT A RESULT, never PASS

> **An optimisation run is graded PASS only if the optimiser itself printed a convergence
> statement against its own tolerance. A run stopped by a wall clock, an iteration cap or a
> budget is `GATE REACHED` where a registered intermediate threshold was met and `NOT A RESULT`
> otherwise — never `PASS`, and never described by the size of the improvement it reached. Every
> optimisation reports a finite-difference check of the gradient **at its final design point**,
> not only at the baseline.**

**This is `VERIFICATION_CHARTER.md` §4 lifted one level.** §4 (`:528-531`) already owns the
solver's iteration cap: *"an iteration cap is a budget, not a settle criterion … a rung that
reaches it has not converged, it has run out of money, and the two are recorded differently or the
ladder inherits the guess as if it were a measurement."* **No charter says the same about an
optimiser's major-iteration limit** — `SNOPT`, `IPOPT` and `pyOptSparse` appear nowhere under
`docs/charters/` — and this lane is the only one that runs optimisers.

**The incident, A2, 2026-07-28.** `ladder-a/A2_optimization_history.json` is a genuine 48-row
extraction of a real **IPOPT 3.13.5 (pyOptSparse) / MUMPS / limited-memory BFGS** run: `tol=1e-5`,
`max_iter=100`, **47 major iterations completed in a 60-minute box**, drag reduced **28.275488 %**
from CD 0.029619634 to 0.021244538 at matched CL ≈ 0.5. The extraction is sound — `_primary_sources`
names `opt_IPOPT.txt` with its sha256. **What the log does not contain is a result:**
`converged_to_optimizer_tolerance: false`, `convergence_statement_in_log: null`, and *"IPOPT prints
no EXIT line and no convergence statement anywhere in `opt_IPOPT.txt`; the table simply stops after
iteration 47"* (`docs/dafoam/PRIOR_WORK_INVENTORY.md` §5.1). The standing-picture entry that said no
optimiser had ever run was corrected; **the true statement is the weaker one — no optimiser run has
ever converged** — and a 28 % drag reduction reached inside a wall clock is `GATE REACHED`.

**Why the final-point FD check is mandatory and not a nicety.** Every FD verification this lab holds
was measured at or near a **baseline** design. The IDWarp defect that flips A1's idx6 and A5's
idx8/idx17 is **guaranteed to fire at the undeformed baseline** — `axisMag = 1e-15 < tol = sqrt(eps)`
makes branch 0 certain at every non-corner surface node — and its second regime, D-A2, behaves
differently just **above** the threshold: measured error against angle reads 1e-5 rad → 4.1e-08,
1e-6 → 6.7e-05, 5e-8 → 1.2e-02 (`ROOTCAUSE_getRotationMatrix3d.md` §1.6, §6.4). **A gradient verified
at iteration 0 is not verified at iteration 47**, and the two regimes are on opposite sides of the
guard. A4's registered first optimisation (`ladder-a/A4/first_optimisation_np1/PREREGISTRATION.md`)
is the next opportunity to do this correctly.

**What is forbidden.** Grading an optimisation from the size of its improvement. Reporting a design
change as validated without an FD check at the design point that produced it. Using the word
converged of a run whose optimiser printed no convergence statement.

---

# PART III — HOW THE LANE OPERATES

## 10. Upstream filing is Sanaa's alone, and every defect record says so on its first screen

> **Nothing in this lane is filed, sent, posted, uploaded, registered or commented upstream by
> any agent, ever. Defect notes and bug reports are written to be filing-ready and are marked
> **NOT FILED** in their opening lines, with the marker at the top of the file and not in a
> closing paragraph. Preparing a report is work an agent does; filing it is a decision only
> Sanaa takes.**

**The standing instruction this restates for the record, not invents.** `FAMILY_SUPERVISION_GUIDELINES.md`
§3.6 — *"Nothing is filed upstream by anyone in this family, ever. Both reports and the tex carry
NOT FILED status; filing is Katie's call alone."* Both existing upstream reports comply at the source:
`UPSTREAM_BUG_REPORT_decomposition_adjoint.md:3-4` and `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md:3-4`
both open **"Status: NOT FILED ANYWHERE."**

**Four defect classes are prepared and none is filed**, which is the state this clause exists to keep
legible rather than to change:

| class | record | where it would go |
|---|---|---|
| **D-A / D-A2** IDWarp `getRotationMatrix3d` degenerate-rotation branch, and the near-threshold `acos` regime | `ROOTCAUSE_getRotationMatrix3d.md`, `PATCH_getRotationMatrix3d.md`, `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` | a comment on `mdolab/idwarp#57` — open since 2021-07-14, `bug` label applied 8 seconds after creation, **zero comments in five years** — not a new issue |
| **D-B / D-B2** parallel reverse-AD adjoint is not the transpose Jacobian under decomposition; and the `cellLimited` limiter breaking the tape in **serial** too | `UPSTREAM_BUG_REPORT_decomposition_adjoint.md`, `DISCRIMINATORS_A4_decomposition_mechanism.md` | `mdolab/dafoam`. Submission readiness: tutorial reproducer **NOT DONE**, mechanism-to-a-line **NOT DONE** |
| **D-C** `KSPSetFromOptions` silently discarded by 13 later override call sites | `DEFECT_CANDIDATE_ksp_options_override.md` | `mdolab/dafoam`, class **diagnosability** |
| **D-E** ASM sub-block ILU exact zero pivot on wall-resolved separated cases | `ladder-b/B3/DEFECT_NOTE_ilu_zero_pivot.md` | `mdolab/dafoam`; adjacent open threads **#1002**, **#1011** |

**`VERIFICATION_CHARTER.md` §15 already records the state and declines to make the rule**
(`:1338-1345`): *"a repair proves a cause; it does not license reporting the repaired numbers as
the lab's own results. The patch above lives in a scratch clone, **nothing upstream has been
filed**, and every figure in this section is labelled as a patched-versus-unpatched comparison
rather than as a validated gradient."* This clause supplies what §15 left open — who may file, and
what state a prepared report is held in — and nothing more.

**63 recorded searches across 10 venues** found no upstream report of the ILU-singularity class
(`LIAISON_NOVELTY_SWEEP_decomposition_defect.md` §3), so the novelty question is answered and only
the filing decision is open. **A record that says "should be filed" is stating a recommendation; a
record that files is breaking this clause.**

## 11. Lessons continue from L-186, and numerics facts are inserted at the end of the N-B block, not at the end of the file

> **A DAFoam lesson is drafted to the scratchpad and the supervisor appends it to `docs/LESSONS.md`;
> no lane appends to that file itself. The next number is derived with the period-anchored regex the
> file mandates, never by incrementing a remembered maximum. A numerics fact goes to
> `docs/NUMERICS_KNOWLEDGE.md` as the next **`N-D`** entry — the DAFoam family — appended at the
> end of the existing `N-D` block. `N-D` exists because this lane's first five facts were filed as
> `N-B21..N-B25` and collided within the hour with a concurrent closure-team append of the same
> numbers.**

**Measured 2026-08-21** (`docs/dafoam/PRIOR_WORK_INVENTORY.md` §4.0). `LESSONS.md` holds **185 lesson
blocks spanning 184 distinct numbers**: **L-52 does not exist**, **L-43 is duplicated**, and the file
is **not in monotonic order on disk** — L-4 sits at `:220`, after L-5, L-6 and L-7. The highest is
**L-185** at `:8261`. **There is no L-186 or higher, so L-186 is next** — and block count, distinct
count and highest number are three different figures, exactly as `docs/charters/README.md` §5 warns
about the same file.

**The trap, stated because it is invisible and destructive.** `NUMERICS_KNOWLEDGE.md`'s `N-B` family
runs **N-B1 (`:2078`) to N-B20 (`:2238`) with no gaps and no duplicates**, and **the block ends at
`:2249`**. A **later, entirely unnumbered** section — the Kaandorp 2020 TBRF closure-repro block —
follows at `:2252` and runs to the file's end at `:2401`. **An append at end-of-file therefore lands
in the wrong section. `N-B21` goes at line ~2249.** The prefix means **Lane B**, not a topic letter;
there is no `N-A` family anywhere in the repo.

**Cross-reference.** `CLOSURE_MODELLING_CHARTER.md` §17 owns the drafting-and-supervisor-append
mechanism; this clause adds only the two numbering facts a DAFoam lane would otherwise get wrong.

> **The numbers above are stale by design and are not the rule. The rule is the re-derivation.**
> Other teams commit to `main` concurrently: `L-186` was written into `LESSONS.md` by the closure
> team **within an hour of this charter naming L-186 as next**, which made this lane's first
> lesson `L-187`. **Re-derive immediately before appending, paste the command's output into the
> record, and append with `cat >>` (lessons) or a single anchored in-place insertion at the end of
> the `N-B` block (numerics), so a concurrent edit is not clobbered:**
>
> ```
> grep -o '^## L-[0-9]*' docs/LESSONS.md | tail -1
> grep -o 'N-B[0-9]*\.' docs/NUMERICS_KNOWLEDGE.md | tail -1
> ```
>
> This is `docs/charters/README.md` §5's own warning applied to this clause: **a count carried in
> a document schedules its own next correction.** The commands are the authority; the figures in
> the paragraph above are the reading at 2026-08-21 and nothing more.

## 12. Every run discloses its cost from its own ledger, in core-minutes and dollars, and a prediction is made before the spend

> **A DAFoam record states the cost of the compute it reports: core-minutes from its own ledger,
> the cores-and-wall basis they were computed on, and the dollar figure at the lab's stated rate.
> The estimate is written down **before** the runs and the miss is reported as a miss. Anything
> whose estimate exceeds \$25 is not run: it is listed for Sanaa with its price and its
> discriminating outcome.**

**Cross-reference.** `COMPUTE_BUDGET_CHARTER.md` owns the unit (**core-minutes**), the honesty rule
(*"no cost is ever presented as measured unless a record backs it"*), the gross-versus-cleaned
distinction, the iteration-count rule and the overrun rule (*"a budget overrun stops the run. It does
not get a new budget"*). This clause adds three DAFoam-specific things.

**First, the basis is stated because this lane's is unusual.** DAFoam runs bill **cores × wall for
the whole clock**, not measured CPU time, because a `docker run` holds its `--cpuset-cpus` whether the
solver saturates it or not. `patched_build/subpclu/BUILD.md` §2 states it explicitly — *"lab
convention: cores × wall, full occupancy for the whole clock"* — and the rate in use is
**\$0.0513/core-hour**.

**Second, the prediction and the miss.** The subpclu `v2` build predicted **35 core-min** with 100 %
contingency and measured **18.93** — *"54 % of it, inside the un-contingency'd 17.3 figure to 9 %"*
(`BUILD.md` §4.1). **A prediction that lands is only evidence if the misses are on the record too**,
and this lane has them: the discriminators item measured **56.77 core-min against 45 budgeted, a 26 %
overrun**, and the mechanism sweep caught **two arithmetic slips inside that same ledger** — a
subtotal recorded as 12.63 that is 12.80, and one arm's `cpus_cap` recorded as 1 against a hardcoded
2 (`docs/dafoam/PRIOR_WORK_INVENTORY.md` §5.4).

**Third, a price never crosses from a primal to an adjoint, or between solver families.**
`COMPUTE_BUDGET_CHARTER.md:375-395` is explicit — *"a repricing crosses solver families only from
that case's own record. Where no such record exists, the item is reported UNPRICED rather than
given a number"* — and this lane's records comply, carrying **UNPRICED** on the
omega-destruction-term patch and on the duct streamwise-profile deficit rather than inventing
figures for them (`docs/dafoam/PRIOR_WORK_INVENTORY.md` §7 Tier 2).

**Fourth, the \$25 list is a deliverable, not a refusal.** The unbought DAFoam items are priced in
`docs/dafoam/PRIOR_WORK_INVENTORY.md` §7 with their discriminating outcomes — M1 + M2 at **40 core-min**
answer the hump's singular-or-not question and supply the negative control the programme never ran;
M4 needs **≥ 64 GB** *"or it does not produce the measurement it is bought for"*; an A6 adjoint attempt
at **760–1,520 core-min** *"must NOT be proposed"* because a zero-cost analysis decides the question.
**A costed item that is not run is a result of this clause working, and it is written down as one.**

---

# 13. Enforcement

**Written from what exists, not from intent.** Where nothing checks a clause this section says so.

| Clause | What checks it today |
|---|---|
| §2 FD table required | **Nothing automatic.** `VERIFICATION_CHARTER.md` §7 states the band; a reviewer checks the table is present. A grep for an `FD` heading in `cases/dafoam/**/RESULTS.md` would catch an omission and does not exist. |
| §2 statistic named | **Nothing.** The vector-norm-versus-per-component confusion is caught only by reading. **Proposed, not built.** |
| §3 step sweep | **Partly** — `ladder-a/A_stepsize_study.{md,json}` is the worked instance and `analyse_fd.py`-class helpers recompute it, but no check requires a sweep before a graded FD number. |
| §4 trivial baseline | `scripts/check_row_discrimination.py` (rules `D1-HOLLOW-PASS`, `D2-INERT-ROW`, `D3-GUARD-GRADED`) is the closure lane's instrument. **It has never been run against `cases/dafoam/`**, and whether its row schema fits this tree is unmeasured. |
| §5 decomposition disclosed | **Nothing.** A column-presence check on parallel gradient tables is buildable and does not exist. |
| §6 two rows, image identity | **Partly** — `patched_build/*/BUILD.md` gates G2a–G2d are real, reproducible and were run. Nothing enforces that a *record* carries both rows. The sub-LU banner assertion is manual (`FAMILY_SUPERVISION_GUIDELINES.md` §8). |
| §7 memory envelope | `COMPUTE_BUDGET_CHARTER.md` §4's auto-stop cron is installed and real, and its `pgrep -f` busy-test **includes `dafoam`**, so a long solve is safe by construction. The **prediction** is honoured by hand. |
| §8 vocabulary | **Nothing**, and the same gap `CLOSURE_MODELLING_CHARTER.md` §20 records for §12. A grep for the six tokens across `cases/dafoam/**/*.md` would catch a stray word and does not exist. |
| §9 optimiser grading | **Nothing.** A check that an optimisation record carries a convergence statement or the token `GATE REACHED` is buildable; the A2 case was caught by reading a JSON field that a human had filled in honestly. |
| §10 not filed | **No technical control, and it is not stated as one.** It is the standing instruction; both upstream reports carry the marker at `:3-4`. |
| §11 numbering | `python3 scripts/check_filing.py` covers paths and names (R7) and **says nothing about lesson or numerics numbering** — grepped for `index`, `frozen`, `append-only`: zero hits. Numbering is re-derived by command each time. |
| §12 cost | Ledgers are written by the run scripts themselves (`ledger.csv` per run root). **Nothing checks that a record quotes its ledger**, and nothing checks a \$25 item was listed rather than run. |

**Seven clauses have no automatic enforcement and are marked so.** A clause nobody can fail is a
preference, and this table is where that gets admitted rather than discovered.

**Dated note, 2026-08-22 (v1.0c, additive — no clause weakened, no threshold moved).** This table
audits **this charter's** clauses for enforceability. **Nothing audits a pre-registration's own
registered thresholds for it**, and a pre-registration can invent a guard that no existing check
covers.

> **PROPOSAL.** Nobody has ruled on this. Written so there is something to argue with.
> **Every threshold a pre-registration registers names, in the same sentence, the process that can
> execute it — or states in that same sentence that the instrument is record-only and enforces
> nothing.** The incident: A3 rung 2 (`cases/dafoam/ladder-a/A3/rung2_patched_idwarp_np4/`)
> registered "host `MemAvailable` < 8 GiB → stop" and armed a **record-only** watcher, with nothing
> connecting them. The graded arm held the host below that floor for **52.6 % of its samples** and
> the arm's own container was the cause (r = −0.999, 156 samples); **no stop fired, and the
> pre-registration gave no way to tell that none could.** The lane reported it against itself
> (L-239); the numbers survived on independent evidence and no co-tenant process was killed. This
> is §13's own admission — *a clause nobody can fail is a preference* — arriving one layer down,
> inside a document written under this charter. **Not ratified, and deliberately not written as a
> clause:** turning it into one adds an obligation to every future pre-registration, and that is
> the owner's call (`CLAUDE.md` rule 9; retiring or adding a gate threshold is Sanaa's).

---

# 14. Changes to other charters

**No other charter's text is edited by this one.** Two items: one repair to `docs/charters/README.md`
that this charter's own adoption requires and that has been made, and one **PROPOSAL** about a
conflict this charter found and deliberately did not settle.

## 14.1 `VERIFICATION_CHARTER.md:95-96` and `REPORTING_CHARTER.md:210-211` — the five-token lists

Both files fix the verdict vocabulary and both list **five** tokens — `PASS`, `GATE REACHED`,
`GATE FAIL`, `NOT A RESULT`, `BLOCKED` — **omitting `PENDING`**, and neither defines any of them.
All six are defined in exactly one place, `CLOSURE_MODELLING_CHARTER.md` §12. Meanwhile
`docs/DOCKET.md` uses `PENDING` **36 times** and `LESSONS.md` **L-180** recommends it as the honest
verdict in a case where `GATE FAIL` had been written. `docs/DOCKET.md` already records this **class**
of defect twice — **D249** (`:614`) and **D338** (`:703`), for the tokens `PASS WITH EXCEPTIONS` and
`DELIVERED`, both of which occur **zero** times under `docs/charters/`. **`PENDING` is the same
defect with the sign reversed — a token in wide use and absent from two of the three lists that
claim to fix the set — and it is unrecorded.** `REPORTING_CHARTER.md` uses `PENDING` as a live
token in rule 3 (`:204-207`), **two rules above the list at `:210-211` that omits it**, and its
checker reads the token at `:539-541`.

> **PROPOSAL.** Nobody has ruled on this. Written so there is something to argue with.
>
> **(a)** `VERIFICATION_CHARTER.md:95-96` and `REPORTING_CHARTER.md:210-211` add `PENDING` to their
> lists and point at `CLOSURE_MODELLING_CHARTER.md` §12 for the definitions, so one table defines
> the set and the other two cite it. **(b)** Or `CLOSURE_MODELLING_CHARTER.md` §12's table moves to
> `VERIFICATION_CHARTER.md`, which is where "what counts as done" already lives, and the other two
> cite it there. **(a) is preferred** — it is two lines and no renumbering, and
> `VERIFICATION_CHARTER.md` §2b's line-stability disclosure exists precisely because other records
> cite that file by line number and one citation sits inside an executable check.
>
> **Neither is taken here.** This charter is not the owner of either file, and a lane editing
> another lane's charter is the failure `docs/charters/README.md` §4.4 forbids: *"contradictions get
> surfaced, not resolved locally."* §8 above adopts the six-token set **for DAFoam** and discloses
> the conflict; it changes nothing outside `cases/dafoam/`.

## 14.2 `docs/charters/README.md` §1 — the count becomes twelve, and it has been updated

`ls docs/charters/*_CHARTER.md | wc -l` returned **11** before this file was written and returns
**12** with it — pasted, not remembered:

```
$ ls docs/charters/*_CHARTER.md | wc -l
12
```

**`README.md` §1 has been updated**: the heading now reads "The twelve", **row 12 for this charter
has been added to the table**, and a dated note in the same voice as the 2026-08-20 one records the
change. That note is the second time in two days that §1's hand-maintained count has needed a dated
correction, which is the finding worth keeping and is §5 of that same file arriving at §1 again:
**a count in an index schedules its own next correction**, and the re-derive command was correct
throughout.

---

# 15. Related

| Document | What it owns that this charter does not |
|---|---|
| [`VERIFICATION_CHARTER.md`](VERIFICATION_CHARTER.md) | What counts as done; gate versus reference (§2); the identity test (§2a); preregistration amendment and strike-in-place (§2b); the discrimination test and registered trivial baselines (§2c); **the FD band and the five-step reporting protocol (§7)**; `NOT OBTAINED` (§6b). |
| [`COMPUTE_BUDGET_CHARTER.md`](COMPUTE_BUDGET_CHARTER.md) | The core-minute unit and the cost-honesty rule; gross versus cleaned spend; per-rung defaults and the iteration-count rule; the three-number session budget; the overrun rule; the auto-stop contract. |
| [`SUPERVISION_CHARTER.md`](SUPERVISION_CHARTER.md) | Who supervises what; the four checks a supervisor performs personally; **§3 check 4 — no family compute launches without its pre-registration committed**. |
| [`FILING_CHARTER.md`](FILING_CHARTER.md) | Where files go and what they are called; **R7, `<RUNG>_<PURPOSE>.md` for campaign records and `lower_snake.py` for helper code**; `scripts/check_filing.py` as the binding artifact. |
| [`ESCALATION_CHARTER.md`](ESCALATION_CHARTER.md) | The approval bands (§4, itself marked PROPOSAL and unratified); the git prohibitions — never `reset --hard`, `stash`, `checkout --` or `clean`, and an unexpected uncommitted change is inspected, never reverted. |
| [`LITERATURE_CHARTER.md`](LITERATURE_CHARTER.md) | Zero fabricated citations; provenance tiers; the in-sample intake rule. Every method-paper number this charter cites is title-verified under it. |
| [`CLOSURE_MODELLING_CHARTER.md`](CLOSURE_MODELLING_CHARTER.md) | **§12, the only definition of all six verdict tokens**; §17, how lessons and numerics facts are filed; the closure side of Ladder B's science, which this charter does not grade. |
| [`REPORTING_CHARTER.md`](REPORTING_CHARTER.md) | The six report sections and their fixed heading strings. |
| `cases/dafoam/FAMILY_SUPERVISION_GUIDELINES.md` | **The family's binding operational guidance**: R11 two-row grading, §3.6 nothing filed, §4.2–4.3 the FD protocol's operational half, §8 the cold-start and staged-copy rules. Issued 2026-08-07 and binding on every agent in this family. |
| `docs/dafoam/PRIOR_WORK_INVENTORY.md` | The 83-record map of what has been measured, by whom, and what each record cannot see. Parts A and B. |
| `docs/dafoam/TOOLCHAIN_INVENTORY.md` | The images, their md5s and line counts, what each patch does, and the commands that measured them. |
| `docs/dafoam/README.md` | The lane's map: what exists, in what order to read it, the standing verdict table and the unfiled-defect table. |
| `cases/dafoam/INDEX.md` | Where every case, log and work tree actually lives today, and the proposed names for new directories. |

---

# 16. Amendment record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-21 | First issue. Written after three weeks of DAFoam ladder work produced the step-size defence bought after publication (§3, `A_stepsize_study.md`), the retracted A5 clearance and its 160× seed effect (§2, §5), the A4 decomposition split of 8.95 % against 0.00054 % (§5), the 47-iteration IPOPT run with no convergence statement (§9), the `docker commit` image whose scratch tree is gone (§6), the hump run ended by a `docker stop` on a shared box and reported as a boundary (§7), and four prepared upstream defect reports of which **none has been filed** (§10). Clauses cite `cases/dafoam/` records and `docs/dafoam/PRIOR_WORK_INVENTORY.md` throughout; no `LESSONS.md` number is cited because **no DAFoam lesson has yet been filed — the next is L-186** (§11), and a clause without a lesson number says so. Records one conflict it does not settle: the five-token verdict lists at `VERIFICATION_CHARTER.md:95-96` and `REPORTING_CHARTER.md:210-211` (§14.1, **PROPOSAL**). Updates `docs/charters/README.md` §1 from eleven to twelve (§14.2). |
| 1.0c | 2026-08-22 | **§13 gains a dated note and a PROPOSAL, additive; no clause weakened, no threshold moved, no verdict affected.** §13 audits this charter's clauses for enforceability; nothing audits a *pre-registration's* own registered thresholds, and A3 rung 2 proved a prereg can invent an unenforceable guard that no existing check covers — a registered 8 GiB host-memory floor, a record-only watcher, nothing connecting them, breached for 52.6 % of the graded arm by the arm's own container with no stop firing (L-239, D462, `27ce5799`). Recorded as a **PROPOSAL** rather than a clause because making it one adds an obligation to every future pre-registration, which is the owner's decision and not a supervisor's. Surfaced by the lane that caused the breach, in a report whose headline was good news. |
| 1.0b | 2026-08-21 | **§11 opens the `N-D` family, additive, no clause weakened.** This lane's numerics facts were filed as `N-B21..N-B25` and **the closure team committed its own `N-B22..N-B25` at 17:52 the same day (`79a73944`)**, so two disjoint sets of facts carried four identical ids. Resolution, touching only this lane's lines: the five entries are renumbered **`N-D1..N-D5`** in place, with a dated note above `N-D1`; no closure-team text was edited and their `N-B22..N-B25` stand. **The next DAFoam numerics fact is `N-D6`, re-derived with `grep -o 'N-D[0-9]*\.' docs/NUMERICS_KNOWLEDGE.md | tail -1`.** The incident is the clause's own warning arriving inside the hour it was written: a shared append-only file with one number space and several concurrent writers will collide, and a per-team prefix is the only thing that prevents it. |
| 1.0a | 2026-08-21 | **Editorial amendment to §11, additive, no clause weakened.** Adds the re-derivation block: the `L-` and `N-B` figures in §11 are a dated reading, not the rule, and the rule is the two `grep` commands run immediately before appending. Earned the same day: the closure team committed **L-186** while this charter was being written, so this lane's first lesson became **L-187**, and this lane's numerics entries were filed at the end of the `N-B` block (before the unnumbered closure-repro section) rather than at end-of-file. Recorded here rather than by editing §11's prose, because the prose was correct when written. |

# 17. Amendment record, continued: silent-background convention (2026-08-23)

**Dated addendum, 2026-08-23, appended at the foot; append-only. One standing
convention added on the owner's directive. No clause above is altered, widened
or narrowed; no line above this section changed number; the header's version
line is deliberately left untouched, because this addendum inserts nothing and
edits nothing above itself.**

Sanaa's directive, verbatim (2026-08-23): "There needs to be added to all
the .md convention files that all agents must always act in a silent way on
the background without showing bash or ssh on the screen, the screen must
always remain clean with only discussion and results."

In force for every agent this charter binds, and recorded lab-wide as
`CLAUDE.md` rule 16: all heavy work (bash, ssh, compute, file surgery) runs
inside background lanes or subagents, never as top-level tool calls in the
user-facing session when avoidable; user-facing reports carry discussion,
numbers and verdicts only, never pasted terminal output, raw logs or command
transcripts (quote the specific value with its artifact path, not the dump it
came from); supervisors enforce this on their lanes, condensing a transcript
before relay rather than forwarding it raw. Honest caveat: the Claude Code UI
renders whatever tool calls the top-level session makes, so the convention is
kept by pushing work into background agents; that delegation, not a display
setting, is what keeps the screen clean.

| what the amendment did | figure |
| --- | --- |
| standing conventions added | 1 |
| clauses altered, widened or narrowed | 0 |
| lines whose number changed above this section | 0 |

# 18. Amendment v1.0d — 2026-08-30: three additive clauses, on the cost anchor, the cache-state term and the instrument table's dependencies

**Dated addendum, appended at the foot; append-only. Three clauses ADDED as §18.1, §18.2 and §18.3 — new numbers, so nothing above renumbers. NO existing gate, threshold, band, cap or label is altered, widened, narrowed or retired; no clause above is edited or struck; no verdict is affected. THE AMENDMENT IS ADDITIVE ONLY: every clause below makes MORE pre-registrations refusable and NONE makes any item pass that would previously have failed.** Retiring or widening a gate, threshold or charter clause is reserved to Sanaa (`CLAUDE.md` rule 9 and the FIRST-ACTION rule's reserved list); nothing here does either. Written under Sanaa's directive of 2026-08-30, verbatim: *"each teams updates their own charters and stanrdards"* (`etc/sessions/2026-08-30T2247Z_sanaa_directive_continuous_overnight.md`) — which authorises this team to amend ITS OWN charter, and nothing more.

**Version: v1.0c → v1.0d.** As in §17 and in the `ADJOINT_VERIFICATION_STANDARD.md` v1.0a/v1.0b/v1.0c precedent, the version is carried in THIS heading and the `Version 1.0c` line at `:3` is deliberately NOT edited: editing it would renumber nothing but would rewrite a frozen line, and this addendum inserts nothing and edits nothing above itself.

**Lines whose number changed above this section: 0 — PROVED ON BYTES, not asserted.** Before the append a copy of the file was taken: **53,078 bytes, 653 lines, md5 `d7faef41fe3a3b320322cc3433cfc1ea`**, verified byte-identical to `git cat-file blob HEAD:docs/charters/DAFOAM_CHARTER.md` by `cmp` at the moment of copying. After the append the first 53,078 bytes of the amended file were compared against that copy with `cmp -n 53078`, byte for byte, exit 0. **A line whose number changed is a byte that moved, and no byte below offset 53,078 moved.** The append itself was made by `scripts/append_block.py`, which reads this body from a FILE as bytes so that no shell ever sees it, and which re-reads the landed tail and compares it byte-for-byte against the intended bytes, reverting the write on any difference — a second, independent proof by a different instrument. **No heredoc was used anywhere on this path** (`L-405`: an unquoted heredoc command-substituted `GATE FAIL` out of `docs/LAB_STATE.md` at `e779bdc7` on 2026-08-28, and a charter is a worse place to lose a verdict than a board).

**Why all three clauses land in this charter and none in `docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md`, stated because the choice was made rather than defaulted.** That standard owns the five adjoint checks — FD-vs-adjoint with its plateau proof, the dot-product/duality test, np-invariance, complex-step, and the verdict mapping with the two-row rule — and every band in it is a band on a *derivative*. **None of the three clauses below is about a derivative or its band.** §18.1 and §18.2 are cost-anchor and estimate duties and belong beside §12; §18.3 is a freeze duty and belongs beside §2 and §13, whose 2026-08-22 PROPOSAL — that a pre-registration's registered threshold should name the process that can execute it — is the same shape one layer out. Putting a cost rule or a freeze rule inside a standard about adjoint bands would hide it from the readers who need it: **every DAFoam item is costed and frozen; only some measure a gradient.** `ADJOINT_VERIFICATION_STANDARD.md` is NOT edited by this amendment.

**§13's PROPOSAL is neither ratified nor retired by §18.3.** That proposal binds *every registered threshold* to name, in the same sentence, the process that can execute it — which is broader than anything taken here. §18.3 binds only the enumeration and the existence of files the frozen code executes. **The narrower duty is taken; the broader one remains a PROPOSAL, remains unratified, and remains Sanaa's.**

---

## 18.1 A cost anchor names the program it prices, and asserts that the program it is pricing matches

> **A pre-registration that prices an arm from a prior measurement — a `docs/COST_CALIBRATION.md` row, another item's ledger row, or any earlier arm — states, in the cost table itself, WHAT PROGRAM that measurement priced: the rank count, whether an adjoint solve is included, whether a Jacobian colouring is included, and whether the tree was cold or already decomposed. It then asserts that the program being priced MATCHES on all four terms. Where they differ, the difference is quantified and the anchor adjusted, or a second anchor is cited. A cost anchor that cites a prior row without a program statement is a REFUSABLE pre-registration, and the arm does not launch.**

**Why those four terms and not a general instruction to estimate carefully.** They are the four on which this family's two recorded mis-anchorings actually differed. Each is knowable before the run and checkable by a reader who has never seen the case, which is what makes the clause a check rather than an exhortation.

**The first incident, `D5-PREREG-DEF-1`, 2026-08-26 — found, named and classed.** `docs/COST_CALIBRATION.md:215` (row `C-139`) records D5 arm `ACC48`: §4 priced `ACC48`/`ACC192` at **3.000 core-min, cap 10.0**, on *"D4 ACC, C-94"*. And `C-94` (`:170`) is **a 45-second acceptance primal at np=4 on a tree staged `cp -a` from a finished arm and therefore ALREADY DECOMPOSED** — `decomposePar` refused, the setup was warm, the primal itself was 24.3 s of the 45 s wall, and the row's own lesson reads *"a tree staged from a finished arm is not a cold arm and must not be priced as one."* **One primal; no adjoint; no colouring.** The registered `ACC48` program was `compute_totals` on a **cold** staged copy at np=4, which must colour the Jacobian first. The container was cut by its 150 s deadline at 162 s with the log tail `Global ColorSweep: 0 135.64 s / Number of Uncolored: 98959 4` — **the total-derivative step never started** — and every one of the **10.8** measured core-minutes is recorded as WASTE. `C-139` classes the mechanism **`PRE-REGISTRATION MIS-ANCHORING`**, explicitly *"not misprediction of the registered program and not contention"* (`delivered_cores_mean` 3.9792 of 4), and it wrote the remedy down in its own prose: *"a cost row names the PROGRAM it prices and the mesh it was measured on; a cap under one colouring's wall is a cap that will fire."*

**The second incident, `D6R-PREREG-DEF-1`, 2026-08-30 — the same defect four days later, in an item that had NAMED the class it was repeating.** D6R's cost table (`cases/dafoam/ladder-a/A2/curriculum_D6R/PREREGISTRATION.md:270`) registers arm `ACC_mp` at a predicted **14.7 core-min, cap 30.0, in-container deadline 360 s**, from an anchor cell reading in full: **`9.0 × 1.6308` (the same ×3 model, measured short by 63 %)**. Two independent measurements agreeing to **4.7 %** put the registered program at **≈112 core-min**: **112.399**, summed from `ACC_mp`'s own log and `O_mp`'s three colouring and three adjoint segments — six of seven segments MEASURED, the seventh labelled INTERPOLATED and not measured — and **107.40**, from D5's `ARM=ACC48 rc=0 wall_s=537 ranks=4` ledger row taken three times (`cases/dafoam/ladder-a/A2/curriculum_D6RACC2/PREREGISTRATION.md` §2a–§2c). **The arm needed 3.75× its cap and 4.68× its deadline and COULD NOT HAVE FINISHED** — not on a slow day, not on an empty box, never. It died **46.3 % through the FIRST of three colourings**.

**Two precisions, recorded because a clause must rest on what the documents say and not on the shape of the story.**

**(i) D6R's pre-registration does not cite `C-94` at all** — the string occurs **zero** times in it. The `C-94` trace is D5's, quoted inside `C-139`; what D6R inherited is the unrepaired *practice*, not a citation. **That is the worse case and not the milder one.** D5 at least named the row it priced from and could therefore be audited against it; D6R's anchor cell names a bare `9.0` with no row, no program and no provenance, and there is nothing in the table to audit it against. **A clause that only required citing a calibration row would not have caught D6R.** This clause therefore binds the PROGRAM STATEMENT, not the citation.

**(ii)** D6R §4 at `:275` carries the heading *"THE `max_iter` ARITHMETIC, SHOWN (the `D5-PREREG-DEF-1` class, named and avoided)"* — and the arithmetic shown beneath it is `O_mp`'s, whose anchor `80 × 31.258` **is** measured on the same program on the same configuration. **The class was named, the guard was applied to one arm of four, and the three arms priced by a multiplier carried over from a different arm were not covered by the sentence that claimed to avoid it.** A defect named in prose in one paragraph is not a defect repaired in the table two lines below.

**This is rule 14 at the estimate level, and it is why the answer is a clause and not a third ledger row.** `C-139` recorded the correct lesson in the correct words on 2026-08-26, and the identical failure landed on 2026-08-30 — because **a lesson written in a ledger row has no call site**: nothing reads it, nothing asserts it, and the only mechanism by which it can act is a lane remembering it. This clause moves it into the one document every future item must pass through.

**CALL SITE — what a check asserts, stated so it is buildable and so a reviewer can refuse an item today.** In the pre-registration's cost table, for every arm whose anchor is a prior measurement: the anchor cell — or a note it points to by name — contains a program statement carrying all four terms (ranks; adjoint yes/no; colouring yes/no; tree cold or already-decomposed) and a match assertion against the arm's own registered program. **Refusal conditions, any one sufficient:** an anchor naming a `C-` row with no program statement; an anchor that is a bare number with no provenance at all (the D6R shape); a stated program differing from the registered program on any of the four terms with neither a quantified adjustment nor a second anchor. **NOT BUILT at this commit** — no script performs this, and §13's rule holds: *a clause nobody can fail is a preference.* It is refusable by a reviewer today on four named, mechanical terms, which is more than *"price it carefully"* could ever be, and the supervisor's §3 check 4 is where that read already lands.

**What is forbidden.** Pricing an arm from a prior row without saying what that row measured. Carrying a multiplier measured on one arm onto arms running a different program without saying that this is what is being done. Treating a class named in prose as a class repaired in the table.

**What this clause does NOT change.** No cap moves. No estimate is licensed to be larger. **Rule 12 stands unaltered in every part** — the unit is core-minutes, every run is costed in its pre-registration, and an overrun stops the run and does not get a new budget. §12 of this charter is untouched; this clause adds a required disclosure ahead of it and removes nothing.

---

## 18.2 An instrument-only estimate carries a cache-state term

> **An instrument-only item — one that reads preserved artefacts and runs no solver — states in its cost table whether its estimate assumes a COLD or a WARM page cache, and sizes its dominant term from the file count and the copy count rather than from an operation count. An instrument-only estimate with no cache-state term is INCOMPLETE, and the item is refusable on that ground alone.**

**Paid for twice in three days, by this family, on the same shape.** `C-212` (`docs/COST_CALIBRATION.md:295`, AVWC) measured **the identical selftest at 75.24 s cold and 3.74 s warm — a 20.1× spread on byte-identical work** — on the first read of three preserved run roots (≈1,887 files) after a 32-hour shutdown and a reboot. Its registered estimate's basis was an operation count (*"≈12 `cp -a` copies, ≈24 md5 manifests, ≈12 frozen `grade()` calls, two selftests"*) **with no cache-state term at all**, and it drew the lesson in its own words: *"a manifest-heavy re-grade estimate built from an operation count is incomplete without a cache-state term."* `C-214` (`:297`, D6RG) then registered **1.50 core-min** and measured **0.320 — a ratio of 0.213×** — and states that **the whole 4.7× over-estimate is that one term**: a cold manifest of the 14,546-file D6R root measured **14.34 s** against a warm ≈**2 s**, and the cache was already warm from the pre-freeze drive of the frozen grader. `C-214` says it against itself: *"`C-212` recorded a 20.1x cold/warm spread on the same shape two days earlier and drew the lesson…; this estimate STILL DID NOT CARRY ONE, and missed by 4.7x in the same direction."* **That is rule 14 again — the lesson existed, in the right words, in the ledger, and had no call site.**

**The sizing figures, and exactly how far they may be trusted.** `C-214`'s carry-forward gives **≈1.0 s per 1,000 files COLD** (14.34 s / 14,546 files) and **≈0.15 s per 1,000 files WARM** (≈2 s / 14,546 files). **These are THIS FAMILY'S OWN MEASUREMENTS, on ITS OWN preserved run roots, on THIS box, from two roots — and they are NOT constants and NOT a lab-wide rate.** They are cited as `C-212` and `C-214` wherever they are used, never presented as universal, and a third measurement is expected to move them. Two conditions they silently carry, named so a later reader does not have to rediscover them: `C-212`'s cold figure was taken after a reboot, which is the coldest state available on this box, and `C-214`'s warm figure was taken minutes after a full manifest of the same root, which is close to the warmest. **The dominant cost of an instrument-only item is I/O, not CPU, so the sizing variables are the file count and the copy count** — an operation count prices the arithmetic, and the arithmetic is not where the time goes.

**What the two rows agree on, and what they do not.** They agree on the direction, on the mechanism and on the remedy. They do **not** agree on the magnitude — 20.1× against ≈7× — and this clause does not pretend they do. What is required is the statement of WHICH STATE the estimate assumes, because *"an estimate that does not say is unfalsifiable by roughly an order of magnitude"* (`C-214`). **Naming the state is what makes the estimate falsifiable; the two figures only make it sharper**, and they are offered as sizing guidance carrying their own provenance, never as a band.

**CALL SITE.** The cost table of any item registering zero solver compute contains the token `COLD` or `WARM` against its dominant term, together with a file count and a copy count. **Refusal conditions:** no cache-state token anywhere in the cost section; a dominant term sized from an operation count with no file count; a cold assumption sized at a warm rate or the reverse. **NOT BUILT at this commit** — a grep over a zero-solver-compute item's cost section for the token would catch the omission and does not exist. It is refusable by a reviewer today.

**What this clause does NOT change.** No cap moves, and no estimate is permitted to be larger or smaller than it otherwise would be. **The overrun rule binds on the CAP exactly as before** (`CLAUDE.md` rule 12; `COMPUTE_BUDGET_CHARTER.md`), and stating a cache-state term is not a licence to miss: `C-212` and `C-214` were both comfortably inside their caps and both are recorded as MISPREDICTIONS, which is what the calibration ledger is for. Waste stays separately named and is never absorbed into the ratio (`COMPUTE_BUDGET_CHARTER.md` §6). Rule 12's estimate-versus-actual calibration duty is unchanged; this clause adds a field the estimate must carry BEFORE the run, which is the only point at which the miss is preventable.

---

## 18.3 An instrument table enumerates every file the item EXECUTES or IMPORTS, and existence is asserted before any md5

> **An item's frozen instrument table enumerates every file its launcher, driver and comparator execute or import — not merely the files the author thinks of as instruments. The freeze asserts that each enumerated file EXISTS before it asserts any md5, and existence is checked first and separately: an md5-agreement control over a subset can read agreement on every pin it holds while a dependency the frozen code executes is absent. A registered gate whose implementing file is not in the instrument table is not frozen — it is unimplemented — and the item does not launch.**

**The incident, `SO2a-DRIVER-DEF-1`, 2026-08-30 — a gate frozen without its implementation, caught only by a supervisor stopping a launched run five minutes in.** `cases/dafoam/ladder-a/A1/curriculum_SO2a/PREREGISTRATION.md:161` REGISTERS an aggregate-memory gate: **ceiling 30.6 GiB, wait-and-retry, poll 30 s, bound 4 h**, every wait a line in `STATUS.<arm>`, refuse-and-BLOCK at the bound with the series named. Its §7 instrument table freezes **eight files** by md5 — `so2a_xg.py`, `so2a_grade.py`, `so2a_run_arm.sh`, `so2a_chain_driver.sh`, `so2a_runScript.py`, `so2a_decomposeParDict`, and two real reference logs — **and does not list the script that implements that gate.** The frozen driver executes it by name, inside the poll loop at `so2a_chain_driver.sh:142-153`:

```
AGG=$(python3 "$HERE/so2a_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
```

**`so2a_aggregate_memory.py` was ABSENT from the freeze commit `5f0e083e` (2026-08-28T17:37:19Z)** — `git cat-file -e 5f0e083e:<path>` fails on that tree — **and the §7 md5-agreement control nevertheless read `eight of eight AGREE`**, because the eight pins it compared (five in the chain driver, three in the launcher) did not include the file the driver executes. **A gate was frozen without its implementation, and every control the item held reported that all was well.**

**What would have happened, read from the frozen bytes rather than supposed.** With the script absent, `python3` fails, `AGG` is the empty string, the `json.load` at `:145` cannot return `ok`, and the loop never breaks: **`AGGREGATE_WAIT` written every 30 s until `AGG_BOUND_S`, then `rc=6 … AGGREGATE_BLOCKED_AT_BOUND` and `chain=BLOCKED_AGGREGATE` at the FIRST arm** — four hours of polling an empty result, holding its reservation, producing no gradient, no verdict and nothing to grade.

**Stated in the past tense deliberately, and the tense is load-bearing.** The file exists now: it was written and landed as the repair at `84c0a769` (2026-08-30T23:36:22Z), and it is present in HEAD. **What is legislated here is the FREEZE, which did not contain it** — not a present-tense claim of absence, which would be false and would age badly inside a charter.

**The nuance that makes this a clause and not a note, and it is the sharpest thing in this amendment.** SO2a's pre-registration **already carries §7.3, `WHAT IS NOT DRIVEN, NAMED`**, which honestly declares a *different* absent file — `so2a_groot5_selftest.sh` *"IS NOT PRESENT"* — and says what must happen before enqueue. **The item had exactly the right instinct, wrote a whole section to serve it, and still missed the dependency its own driver executes.** The reason is structural: a prose section names what its author thought of, and the author thought of the selftest they had decided not to run, not the helper they had decided to write and had not yet written. **An enumeration derived from the code cannot have that failure mode; a list written from memory always can.** That is why this clause binds the EXTRACTION and not the diligence.

**Why existence must be asserted FIRST and SEPARATELY.** An md5 control answers *"do the files I pinned still hash to what I pinned?"* It is a **correct** answer to that question, and here it passed correctly. The unasked question was *"is everything the frozen code runs actually present?"* **These are different questions, and the second cannot be inferred from the first at any level of agreement — not at 8 of 8, not at 800 of 800.** This is `L-405`'s structure arriving one document up: a check can pass, correctly, on the question it asks, while the thing that mattered is broken.

**CALL SITE — directly checkable, and the extraction is mechanical.** From every script the instrument table freezes, extract every `$HERE/`, `$BASE/` and `$LAUNCHER`-style path reference and every import of a local module; resolve each against the item directory; assert the target **exists in the freeze commit's tree**. **Refusal conditions:** an extracted target absent from the instrument table; an extracted target absent from the freeze commit's tree; any md5 asserted before existence is. **NOT BUILT at this commit** — the extraction is a short script over the frozen file set and it does not exist. It is refusable by a reviewer today, and `so2a_chain_driver.sh:143` is the worked instance a first version should be born on: **it must flag `so2a_aggregate_memory.py` against the `5f0e083e` tree and must NOT flag it against HEAD** — the planted control for the check itself, so that a check reporting zero findings has been shown able to report a non-zero (`CLAUDE.md` rule 3, applied to the checker rather than to a comparator).

**What is forbidden.** Registering a gate whose implementing file is not in the instrument table. Reporting an md5-agreement figure as evidence that the instrument set is complete. Inferring completeness from any count of agreeing pins.

**What this clause does NOT change.** The md5 freeze requirement is unchanged and unrelaxed — this clause adds an existence assertion **before** it and removes nothing from it. Rule 2's freeze, §2's grading-path fixing, §13's enforcement audit and §6's two-row rule are untouched. **Nothing here permits an item to launch that could previously have launched.**

---

## 18.4 Enforcement, in §13's own voice: what checks these three today

**Written from what exists, not from intent** — §13's own rule, applied to §13's own additions.

| Clause | What checks it today |
|---|---|
| §18.1 cost anchor names its program | **Nothing automatic.** The four terms are refusable by a reviewer at the pre-registration commit, and the supervisor's `SUPERVISION_CHARTER.md` §3 check 4 is where that read already lands. A check over a cost table's anchor cells is buildable and does not exist. |
| §18.2 cache-state term | **Nothing automatic.** A grep of a zero-solver-compute item's cost section for `COLD`/`WARM` plus a file count would catch the omission and does not exist. |
| §18.3 instrument-table dependencies | **Nothing automatic, and this is the one most nearly built.** The extraction is mechanical, and both the worked instance and its planted control are named above. Nothing performs it. |

**Three clauses added, three with no automatic enforcement, and it is stated here rather than discovered later.** §13's sentence stands and now covers three more rows: *a clause nobody can fail is a preference.* **The difference between these three and a preference is that each names a specific, mechanical assertion over a specific artefact**, so a check CAN be written and an item CAN be refused on a stated ground — which is exactly what `C-139`'s and `C-212`'s ledger-row lessons could not offer, and why both were repeated within days of being written.

---

## 18.5 PROPOSAL, NOT ENACTED — a rule-3 control that did not FIRE is reported NOT EXERCISED

**This is a proposal and it is not a clause. Nothing in this section is in force.** It is surfaced to the verification team via the chief and is deliberately **NOT taken here**: it reaches every family's comparators, not this family's alone, and a team amending another team's instrument doctrine is the failure `docs/charters/README.md` §4.4 forbids — *"contradictions get surfaced, not resolved locally."* Adopting it would add an obligation to every comparator in the lab, which is the owner's call (`CLAUDE.md` rule 9), and no agent's message is her consent.

**The finding that motivates it, established 2026-08-30.** `CLAUDE.md` rule 3 requires every comparator to plant a known perturbation, read it back from disk, and refuse if the reader cannot see it. D6R's frozen grader short-circuits `g_price` when an arm did not run — so on that data **the planted-zero control never executed at all, and nothing in the output reported that it had not.** The control's silence and the control's success are indistinguishable in the record. That is the planted-zero doctrine's own hazard turned back on itself: rule 3 exists because *a zero from a reader not shown able to see a non-zero is not evidence*, and **a control that did not run is the limiting case of a reader shown nothing.**

> **PROPOSED TEXT, for verification to weigh.** Every rule-3 planted control reports one of three states — `EXERCISED-PASS`, `EXERCISED-FAIL`, `NOT EXERCISED` — and `NOT EXERCISED` is printed beside the verdict it accompanies and is **never counted as a pass, never omitted, and never inferred from the absence of a failure**. A comparator that can short-circuit a graded quantity states, for every control that quantity carries, whether that control ran on the data actually graded.

**Why it is worth someone's time.** It would be additive if adopted, it costs no compute, and it converts a silent absence into a printed token — the same move `NOT OBTAINED` and `UNPRICED` already make for a document and for a cost (§8). **On this desk it is a proposal and nothing more. Adopting it is verification's to weigh and Sanaa's to rule.**

---

| what this amendment did | figure |
| --- | --- |
| clauses ADDED (§18.1, §18.2, §18.3) | **3** |
| gates, thresholds, bands, caps or labels altered, widened, narrowed or retired | **0** |
| clauses above weakened, edited or struck | **0** |
| items that would previously have failed and would now pass | **0** |
| proposals recorded and NOT enacted (§18.5) | **1** |
| other charters or standards edited by this amendment | **0** |
| solver core-minutes spent to establish it | **0.000** |
| lines whose number changed above this section | **0 — proved on BYTES by `cmp -n 53078` against a pre-append copy, exit 0** |
