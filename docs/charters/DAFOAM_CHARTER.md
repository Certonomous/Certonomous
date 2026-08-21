# Certonomous DAFoam Charter

Version 1.0a, dated 2026-08-21. Governs every discrete-adjoint CFD result this lab produces
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
> `docs/NUMERICS_KNOWLEDGE.md` as the next `N-B` entry, **inserted at the end of the existing N-B
> block**, because an append at end-of-file lands inside a different, unnumbered section.**

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
| 1.0a | 2026-08-21 | **Editorial amendment to §11, additive, no clause weakened.** Adds the re-derivation block: the `L-` and `N-B` figures in §11 are a dated reading, not the rule, and the rule is the two `grep` commands run immediately before appending. Earned the same day: the closure team committed **L-186** while this charter was being written, so this lane's first lesson became **L-187**, and this lane's numerics entries **N-B21 to N-B25** were inserted at the end of the `N-B` block (before the unnumbered closure-repro section) rather than at end-of-file. Recorded here rather than by editing §11's prose, because the prose was correct when written. |
