# A1, A5, A6 — status settlement at HEAD, zero compute

**2026-08-15. Zero solver core-min.** No solver, no DAFoam run, no container, no mesh
generation, no scoring call was launched. Compute authorisation was not given and was not
taken. The ledger stands at 6. Nothing was sent, uploaded, filed or registered.

Anchored at `b241951f` (`main`). Four agents were working concurrently; `git status` was
read before every write and no file this session did not create was reverted or overwritten.

This document **verifies rather than inherits** `dafoam/A1_A5_A6_DIAGNOSIS.md` (2026-08-11,
anchored at `1393b8b4`). Every number below was re-executed from the archive. Where this
session's execution **differs from** or **extends** that document, it is marked
**[NEW]** or **[CORRECTS THE 08-11 DIAGNOSIS]**.

---

## 0. Frames, and the traps that were live

| tag | frame | how enumerated | count |
|---|---|---|---|
| **L6** | logs under `/home/ubuntu/certonomous-runs/A6-crm-wing/` | `/usr/bin/find … -name '*.log' -type f` | **4** |
| **L** | all `*.log` under `/home/ubuntu/certonomous-runs/` | same | **595** (reproduces the 08-11 frame exactly) |
| **Lct** | logs printing a `geometry.rcon' wrt 'dvs.shape'` `check_totals` row | `find -print0 \| xargs -0 /usr/bin/grep -l` | **14** |
| **R6** | `initRes/finalRes/nIters` lines in `A6-crm-wing/run_model_run1.log` | regex parse, count printed before every verdict | **66** (6 fields × 11 write points) |
| **A9** | `act9-crm_wingbody-*` directories | `/usr/bin/find … -maxdepth 1 -type d` | **37**, holding **0** `*.log` |

Traps honoured: every search used `/usr/bin/grep` or `git grep -a`, never the shell's
`grep` (which is `ugrep --ignore-files`, honours `.gitignore` and passes `-I`); every
enumeration used `/usr/bin/find`, never `bfs`; no banded size sweep was used, so the
`-size ±2M` non-complementarity did not arise; `__pycache__` was irrelevant (no repo module
was imported). **No PASS and no zero is reported below from an empty set** — one such
attempt is recorded as a failure in §6.4 rather than hidden.

---

# 1. A1 — the sign flip

## 1.1 What is ESTABLISHED (executed this session)

**E1. The stock failure and its component.** `W5-regrade/a1_unpatched_stock.log:2981-2996`.
`CD wrt shape` reads `Relative Error 1.142743e-01`. Recomputing the vector-relative error
from the two printed 8-component vectors gives **1.142742e-01** — agreement to the printed
precision. Exactly **one** sign disagreement, at **index 6**, analytic `+0.00569076` against
FD `−0.00105334`.

**E2. M1 — the IDWarp rotation guard — is real, and its repair is primal-identical.**
`a1_patched_patched.log:2985-2996`: idx6 moves `+0.00569076 → −0.00106561` while the FD
column is **bit-identical in all eight components**, and the headline falls to
`3.744509e-04` (**0.03745%**; my recompute from the vectors: 3.745247e-04). The two runs'
primal is identical to seventeen digits — `CD: 0.02090808860837286` at line 2726 / 2725 —
and both print `Minimal residual 9.646409714038222e-09 satisfied the prescribed tolerance
1e-08`. **Provenance executed:** the stock arm carries
`IDWARP_IMPORTED_FROM: /home/dafoamuser/dafoam/packages/miniconda3/…/idwarp/__init__.py`
(shipped) at line 3, the patched arm `/patch/idwarp/idwarp/__init__.py`. Single-variable.

**E3. `forceMeshWaveFrozen` is REFUTED as the mechanism — executed, not inherited.**
`/usr/bin/grep -n forceMeshWaveFrozen` returns `forceMeshWaveFrozen 1;` in **both** logs
(`a1_unpatched_stock.log:437`, `a1_patched_patched.log:436`). The lever is identically
active on both sides of the change that removes the flip, and the primal is bit-identical
across it. A mechanism identically active on both sides cannot explain a difference the
change produces. **Refuted.**

**E4. M2 is a second, independent mechanism — the decisive artifact re-executed.** All four
limiter arms carry `IDWARP_IMPORTED_FROM: /patch/idwarp/idwarp/__init__.py` at line 3
(`W4-defect-robustness/{a1fs_np1, a1lim_np1, a1limdef_np1, a1lim_np4scotch}.log`). **M1 was
already patched when M2's flip was measured.** The three-arm ladder, all rows executed from
the logs:

| arm | `CD wrt shape` rel. err | converged CD (line 551) | stops at |
|---|---|---|---|
| `a1fs_np1` (patched, unlimited) | `4.282263e-04` = **0.0428%** | 0.02087031456925589 | `Time = 251` |
| `a1lim_np1` (limiter on) | `9.284586e-01` = **92.85%**, idx6 flipped | 0.01956447711316437 | `Time = 242` |
| `a1limdef_np1` (one-word cure) | `1.213592e-03` = **0.1214%** | 0.01904188196895532 | `Time = 232` |

My recompute of the limiter arm's vector-relative error from its printed vectors:
**9.284586e-01**, exact to all seven digits. One sign disagreement, index 6, analytic
**negative** where FD is positive — the opposite orientation to the stock flip.

**E5. M1 and M2 are NOT a matched pair — and the gap is larger than the 08-11 record states.**
M1's repair moves the primal by **zero** (17 identical digits). M2's cure moves the converged
CD by **2.6711%** (0.01956447711316437 → 0.01904188196895532). **[NEW]** The consequence is
visible in the FD column and has not been stated anywhere: the *finite-difference reference
itself* moves **5.294%** between the two arms (`6.194868e-02 → 6.522800e-02`). So M2's
0.121% is an agreement between an analytic and an FD **that were both computed on a
different converged flow** from the 92.8%. M1's 0.03745% is not — its FD is bit-identical.

## 1.2 What is REFUTED

* `forceMeshWaveFrozen` as the idx6 mechanism (E3).
* "A1 is fully root-caused" read as *one mechanism is the whole story* (E4).
* M1 and M2 as equivalent repairs (E5).

## 1.3 What is MERELY ASSERTED, and what NOBODY HAS CHECKED

* **M2 has no operator-level evidence.** It is established at gradient level (92.8% vs
  step-stable FD) and at one-sided-slope level. Whether the limiter tape is an *operator*
  defect of A4's kind, or an FD-visible tape inconsistency only, is unmeasured in serial.
  → priced as **C-3** in §7.
* **M2's cure is not shown to be a repair.** Because it moves the flow, `0.121%` establishes
  that *the unlimited-gradient tape is differentiable*, not that *the limited one was fixed*.
  Nobody has checked whether any edit exists that repairs the limited tape at fixed flow.
* **Whether the two mechanisms interact** — i.e. whether stock IDWarp + limiter is worse
  than either — has no arm in the archive. Not proposed: see §7.4.

## 1.4 Verdict at HEAD

**A1: FAIL against the shipped toolchain stands and is not in doubt. The root cause is
INCOMPLETE, not wrong.** Two independent mechanisms produce a sign flip at the same
component 6 of the same 4,032-cell case: M1 (IDWarp 2.6.2's degenerate-rotation guard) and
M2 (the `cellLimited` slope limiter's min/max selection on the reverse tape). M1 is
root-caused to a source line and confirmed by a primal-identical repair. M2 is
**characterised, not root-caused**, and its one-word cure is not a repair of the same
problem. **The upstream filing must not go out describing M1 as the whole story.**

---

# 2. A5 — internal-flow adjoint (U-bend)

## 2.1 What is ESTABLISHED (executed this session)

**E6. The failure and the patch response.** `W5-regrade/a5pl_stock_checktotals.log:13551-13556`:
`OBJ.val wrt shapexUpper`, analytic `1.938364e+01` vs FD `3.340851e+01`,
`Relative Error 4.663773e-01` = **46.638%**. Patched
(`a5pl_patched_checktotals.log:13550-13555`): analytic `3.350432e+01` against an **FD that
is bit-identical to the stock run's** (`3.340851e+01`), `Relative Error 2.237182e-02` =
**2.2372%**. **M1's repair is primal-identical on A5 too** — the clean contrast with M2.

**E7. The bisection, and its real reach.** Executed on `dafoam/a5_dobjdxv_np1_run1.log`:

* **FFD/DVGeo link exact**: `A5DXSDSHAPE` at idx 8, 17, 2 and two step sizes reads
  `max_rel` between `2.788343e-12` and `6.442476e-12`. Nothing upstream of the warp is broken.
* **Warp-bypass link at idx8 clean and step-converging**: `A5DOBJDXV_RESULT idx=8` reads
  `rel_err=8.805855e-03 sign=agree` at h=1e-4 and `1.676034e-03` at h=5e-5 — tightening by
  5.3× when the step halves, the signature of FD truncation, not a defect.
* **And it does not reach further.** idx17: `6.665968e-03 → 5.668893e-01`. idx2:
  `3.900445e+00 → 2.677540e+00`, with `sign=FLIPPED` at the smaller step. `||delta_Xv||` is
  2.64–3.13 at these components — the direct-`Xv` FD is outside its linear regime there.

## 2.2 Verdict at HEAD

**A5: FAIL against the shipped toolchain stands at 46.638%, attributed to M1, and the
attribution is stronger than A1's because A5's chain was bisected by executed probes rather
than argued.** The **2.2372% surviving the patch is genuinely open** and must not be
described as root-caused. The bisection is decisive at idx8 **only**; extending it to the
27-component vector is unmeasured.

**Merely asserted:** that A5 is decomposition-invariant. `W4-a5-decomp/run.sh:28` sets
`PYTHONPATH=/patch/idwarp`, so the cited measurement covers the **patched** gradient, not
the stock one it is cited for. Unchanged from 08-11 and re-confirmed here as still live.

---

# 3. A6 — the CRM wing-alone case

**Naming hazard honoured.** `A6` names two objects in this archive: a NASA-hump sub-LU
adjoint run, and the CRM wing-alone case. **Everything below is the CRM object** at
`/home/ubuntu/certonomous-runs/A6-crm-wing/`. No hump evidence is mixed in.

## 3.1 There is no primal failure — confirmed, and the case is larger than the record says

`run_model_run1.log` (914 lines) reaches `Time = 1000`, prints
`CD: 0.02090143421526141`, `CL: 0.5000146055201552`, `ExecutionTime = 403.99 s`, and `End`.
`/usr/bin/grep -c "FOAM FATAL\|SEGV\|Out of memory\|PETSC ERROR"` → **0**. The only
`Floating point exception` string is the `trapFpe:` startup banner at line 31. The crash in
the archive is `run_model_run2.log`, whose first error is
`Case is already decomposed with 4 domains` followed by every rank failing to read
`processorN/250/p` — a restart against a truncated checkpoint, a named defect class with a
prior instance in A1's own Lesson. **Not a finding about CRM physics.**

**[NEW] The case size, read from the log rather than from any record**
(`run_model_run1.log:225-230`): `Global Cells: 579072`, `Global Faces: 1770408`,
`Global Xv: 1838706`, `Undecomposed points: 593865`, **`Global Adjoint States: 5244840`**,
over the 5 registered adjoint states `U, nuTilda, phi, p, T`.

## 3.2 Statement 1 — "CONVERGED below 1e-8" — WRONG, and the gate that passed it is an identity-gate

**Executed.** `/usr/bin/grep -c "satisfied the prescribed tolerance"` on
`run_model_run1.log` → **0**. `/usr/bin/grep -c "Minimal residual"` → **0**.
**Positive control:** the same pattern on `W5-regrade/a1_unpatched_stock.log` → **21**; on
each of the three `W4-defect-robustness` A1 arms → **17**. The search finds the line when it
is present. **A6 never triggered its own convergence test.** It stopped at `endTime 1000`
(`SIMPLE: no convergence criteria found. Calculations will run for 1000 steps.`, line 232).

**The published gate reads the wrong column, and it could not have read otherwise.**
See §5.1 — this is identity-gate **IG-1**.

## 3.3 Statement 2 — "matches the published tutorial to 0.0067%" — WRONG, recomputed

Reference: DAFoam's tutorial `0.02090`, four significant figures.

| instrument | value | vs the claim |
|---|---|---|
| claimed deviation, recomputed `(0.02090143421526141 − 0.02090)/0.02090` | **0.006862%** | the claim |
| reference resolution, half of the last printed digit `0.000005/0.02090` | **0.023923%** | **3.5× coarser** |
| the run's own CD, peak-to-peak over the last four write points (t=700…1000) | `1.530635e-06` = **0.007323%** of CD | **coarser than the claim** |

Both instruments are coarser than the figure. `0.0067%` is not a measurement. The honest
statement — *A6 reproduces the published tutorial baseline to within the reference's own
precision* — is a real and creditable result and is what the case earned.

## 3.4 Statement 3 — the "~8.5e8 temperature-residual signature" — REFUTED, executed three ways

The claim (`docs/PRODUCT_LIST.md:251`) is *"temperature-residual ~8.5e8 signature (same
precursor as A4's field collapse)"*. Source, `run_model_run1.log:894-903`:
`T Residual Norm2: 850899542.2772245`.

**(a) A validated case reads the same order.** `A3-onera-m6-sweep-n28_42120/run_opt5_onera_n28_42120.log:809`
reads `T Residual Norm2: 591446472.1805154` against `Total 591522970.1945837` — same solver
class, same transonic-wing class, T at 99.99% of Total, and that case's primal is graded
**DONE and validated**. A6's 8.5e8 is **1.44×** a number the lab already accepts as healthy.

**(b) A4 — the case the "same precursor" points at — has no temperature residual at all.**
Executed: `/usr/bin/grep -c "T Residual Norm2" W5-regrade/a4_stock_checktotals.log` → **0**.
Its statistics block (`:4258-4274`) prints `U, p, omega, k, phi, Total` and no `T`. A4 is
`DASimpleFoam` (`:344`), incompressible. A4's collapse was in **omega**
(`omega Residual Norm2: 1848.2911` of `Total 1848.3467`). The two phenomena share a *shape*,
not a mechanism.

**(c) The trace the register said could not be taken.** `/usr/bin/grep "^he initRes"` returns
all 11 write points; the energy variable is named `he` per-iteration and `T` in the
end-of-run statistic, which is why a `T initRes` grep found nothing. `he initRes` falls
`1.000 → 4.659e-08`, **strictly decreasing at all ten steps, 7.33 decades**, still falling
3.34× per 100 iterations at the last step. No plateau in the energy equation.

**Statement 3 is refuted. The item `NOT_PASSING_REGISTER.md:613-619` opens is closable at
zero core-min**, and its own stated resolution condition is met.

## 3.5 [CORRECTS THE 08-11 DIAGNOSIS] The primal will NOT reach its tolerance — and the record says the opposite

The 08-11 diagnosis traced `he` alone and concluded *"nothing in the log suggests it would
not have continued closing."* **That is true of `he` and false of the run.** All six fields,
executed (`initRes`, 11 write points each, 66 lines parsed, count printed before the verdict):

| field | t=600 | t=700 | t=800 | t=900 | t=1000 | last-step rate |
|---|---|---|---|---|---|---|
| U0 | 2.227e-6 | 5.587e-7 | 1.778e-7 | 5.257e-8 | 2.329e-8 | 2.26×/100 |
| U1 | 5.299e-6 | 1.650e-6 | 6.185e-7 | 1.720e-7 | 3.004e-8 | 5.73×/100 |
| U2 | 3.691e-6 | 9.558e-7 | 3.362e-7 | 9.737e-8 | 2.381e-8 | 4.09×/100 |
| he | 7.690e-6 | 2.073e-6 | 6.514e-7 | 1.555e-7 | 4.659e-8 | 3.34×/100 |
| p | 7.163e-6 | 3.670e-6 | 1.582e-6 | 4.303e-7 | 1.009e-7 | 4.26×/100 |
| **nuTilda** | **1.318e-7** | **1.265e-7** | **1.218e-7** | **1.201e-7** | **1.182e-7** | **1.02×/100** |

**`nuTilda` is the binding field and it stopped decaying at t≈600.** Over the last 400
iterations it moves from 1.318e-7 to 1.182e-7 — a factor of **1.115 in 400 iterations**,
against `he`'s factor of 165 over the same span. At the measured rate, `nuTilda` needs
**15,573 further iterations** to cross 1e-8.

At the run's own cost basis — `ExecutionTime = 403.99 s` for 1000 iterations at np=4 =
**26.93 core-min per 1000 iterations** — that is **≈419 core-min**, and it assumes a plateau
that has shown no sign of breaking will break.

**A6's primal is force-stationary with a turbulence-variable plateau. On this configuration
it does not reach `primalMinResTol = 1e-8`.** That is a stronger and more useful statement
than "not converged", it costs nothing, and it kills a priced experiment (§6.2).

## 3.6 [NEW] Statement 4 — "memory wall" — the label is wrong at its source

**Executed, with a validated positive control (my first control failed; see §6.4).**
Pattern `Main iteration|KSP Residual|dRdWT|Adjoint States|Solving the adjoint`:

| log | hits | what they are |
|---|---|---|
| `a5_dobjdxv_np1_run1.log` (control) | **16** | includes `Main iteration` + `KSP Residual` |
| `a5pl_stock_checktotals.log` (control) | **18** | same |
| `a1_unpatched_stock.log` (control) | **17** | same |
| `A6-crm-wing/run_model_run1.log` | **5** | `Adjoint States:` ×2, `Global Adjoint States: 5244840` ×2, **`dRdWT Jacobian Free created!`** (line 666) |
| `A6-crm-wing/run_model_run2.log` | 0 | — |
| `A6-crm-wing/{decomposePar,preproc_stdout}.log` | 0 | — |

`Main iteration` and `KSP Residual` — the two markers that fire 16–18 times in every log
that actually solves an adjoint — appear **zero** times in all four A6 logs. **No adjoint
linear solve was attempted on A6.** But the run **did** register 5,244,840 global adjoint
states and **create the matrix-free transposed-Jacobian operator** (`dRdWT Jacobian Free
created!`) on this host, at np=4, without distress, and then completed 1000 SIMPLE
iterations and exited `End`.

**And the case the wall is inherited from does not have one.** The chain is
`A6 memory wall ← same structural reason as A3`. Executed on
`A3-onera-m6-adjoint-probe80k/run_opt4_probe80k.log`: `Global Cells: 79560`,
`Global Adjoint States: 724609`, `dRdWT Jacobian Free created!` at line 589, then
`Main iteration 0/100/200 KSP Residual …` **twice**, each ending
`**Completed**! Total iterations: 200. PetscConvergedReason: -5`, and `Finalising parallel
run`. **No OOM, no kill, no allocation failure — the adjoint ran and diverged.**
`docs/PRODUCT_LIST.md:176-179` says so itself: A3 is *"`DIVERGED_BREAKDOWN` at every mesh
size incl. 21,840 cells with >20 GB free — **conditioning, not memory**"*.

**So `docs/PRODUCT_LIST.md` contradicts itself between line 179 and line 251**: the A3 entry
says the blocker is conditioning and explicitly not memory; the A6 entry seventy lines later
calls the same inherited blocker a *memory wall*. This is the same self-contradiction shape
the lab caught once before at `PRODUCT_LIST.md:22`. **A fourth wrong published statement
about A6, and it is free to fix.**

*Stated against myself:* successful `dRdWT` creation does **not** prove an A6 adjoint would
fit — the matrix-free operator is the cheap half, and A3's documented death point is in
preconditioner/Jacobian assembly. What is established is narrower and still decisive: the
attribution is **projected from a case whose own record names a different cause**, and it
is projected past a step that demonstrably did not fail.

## 3.7 Verdict at HEAD

**A6: there is no primal failure. Four published statements about it are wrong, all four
correctable at zero compute, and all four still LIVE at HEAD** (see §4). The primal is
force-stationary at CD = 0.02090143421526141, reproduces the published tutorial to within
the reference's own precision, has a monotonically decaying energy residual, a plateaued
turbulence residual, no temperature anomaly, and no adjoint attempt of any kind.

---

# 4. Where the corrections have and have not propagated

The 08-11 diagnosis corrected these claims in detail. Four days later, **the correction has
propagated to exactly one downstream line** — `docs/PRODUCT_LIST.md:210`'s A1 entry, via its
`[AMENDED 2026-08-11]` block. Everything below is **LIVE and uncorrected at HEAD**. This is
an inventory for the owners of those files; nothing in this section was edited by me.

**A1 — `forceMeshWaveFrozen` still standing as the mechanism:**
* `demo-output/website/dafoam/ladder-a/A1_naca0012_incompressible.md:166-169` — *"traced
  (candidate mechanism, not proven) to `forceMeshWaveFrozen=True`"*, reinforced at `:171`
  with *"same case, same mechanism"*. **Zero strike, zero amendment marker in the file.**
  This is the case's own primary document.
* `demo-output/website/dafoam/ladder-a/A1_naca0012_incompressible.json:198` — same claim.

**A1 — root cause stated as one mechanism:** `docs/PRODUCT_LIST.md:209` (section header) and
`:357`; `campaign/NOT_PASSING_REGISTER.md:636` (*"one cause for both entries"*, and the token
`cellLimited` appears nowhere in that file); `dafoam/DAFOAM_CASE_STATUS.md:50, 62, 106, 256`;
`ACTIVE_RESEARCH.md:66`.

**A6 — "converged below 1e-8":** `docs/PRODUCT_LIST.md:250`;
`dafoam/DAFOAM_CASE_STATUS.md:111`; `dafoam/ladder-a/A6_crm_wingbody.md:1, 121-123, 126,
206-207`; `dafoam/ladder-a/A6_crm_wingbody.json:165` (`"all_below_primalMinResTol_1e-8": true`)
and `:216`; `campaign/NOT_PASSING_REGISTER.md:331`;
`campaign/DPW8_AEPW4_SCOPING.md:248` / `.json:244`.

**A6 — "0.0067%":** `demo-output/website/benchmarks.html:178` (a public KPI tile) and `:209`
(a public table row **graded PASS**), plus the built copy at
`dist/certonomous-demo/site/benchmarks.html:165, 196`; `docs/PRODUCT_LIST.md:200, 250`;
`dafoam/ladder-a/A6_crm_wingbody.md:150, ~153, 208` / `.json:188, 216`;
`dafoam/DAFOAM_CASE_STATUS.md:111`; `ACTIVE_RESEARCH.md:146`;
`campaign/NOT_PASSING_REGISTER.md:331, 615`; `campaign/CHALLENGE_SLATE_2026-08.md:34`;
`campaign/DPW8_AEPW4_SCOPING.md:248` / `.json:7, 244`; and
`campaign/DEAD_LEVER_AUDIT_2026-08-08.md:218`, where it is **affirmatively re-certified `V`**.

**A6 — the 8.5e8 "signature":** `docs/PRODUCT_LIST.md:251`;
`campaign/NOT_PASSING_REGISTER.md:613, 616, ~618`; `ACTIVE_RESEARCH.md:146`; and
`agenda/proposals/weekly-numerics-clinic-theory-first-on-one-open-anomaly.json:4, 16, 20`,
where it is **still a live agenda item**.

**A6 — "memory wall":** `docs/PRODUCT_LIST.md:251`; `dafoam/DAFOAM_CASE_STATUS.md:112`;
`campaign/NOT_PASSING_REGISTER.md:329, 332, 754`;
`dafoam/ladder-a/A6_crm_wingbody.md:4-6, ~186` / `.json:6`; `ACTIVE_RESEARCH.md:146`; and
**`sdk/workflows/crm_wingbody.py:386`** — shipped SDK code.

**Nobody claims an A6 primal failure.** Sweeps for that returned zero hits with the commands
stated, so the framing of the standing task ("A6 CRM failures") is itself the error, not a
record defect.

---

# 5. Identity-gates found on this line (owner's rule W-2)

A gate whose quantity is derivable by construction from its own inputs **may be reported and
must never be gated on**. Two were found; both were tested by executed measurement rather
than argued.

## 5.1 IG-1 — A6's convergence gate is the linear solver's own stopping rule

`A6-crm-wing/system/fvSolution` sets, for **every** solved field:

```
"(p|p_rgh|G)"                       { solver GAMG;         relTol 0.1;  tolerance 0; }
"(U|T|e|h|nuTilda|k|omega|epsilon)" { solver smoothSolver; relTol 0.1;  tolerance 0; }
```

`relTol 0.1` with absolute `tolerance 0` means the inner solver stops the moment it has cut
the residual by one decade. **Therefore `finalRes ≤ 0.1 × initRes` on every field, at every
outer iteration, of every run — by construction.**

**Executed across all 66 residual lines in the run:** violations of the bound = **0**;
`max(finalRes/initRes) = 0.099617` (field `p`, line 796 — within 0.4% of the bound);
`min = 0.008440`. The bound is never violated and is repeatedly approached. `finalRes` is
not a free measurement; it is a readback of `relTol`.

`dafoam/ladder-a/A6_crm_wingbody.md:121-123` gates convergence on *"All six field `finalRes`
values at t=1000 are below 1e-8 … this satisfies `primalMinResTol=1e-8` on every field"*.
At t=1000:

| field | initRes | finalRes | ratio | `finalRes < 1e-8`? | `initRes < 1e-8`? |
|---|---|---|---|---|---|
| U0 | 2.329009e-08 | 1.742194e-09 | 0.0748 | **yes** | no |
| U1 | 3.004163e-08 | 1.823764e-09 | 0.0607 | **yes** | no |
| U2 | 2.380869e-08 | 1.539276e-09 | 0.0647 | **yes** | no |
| he | 4.658549e-08 | 3.552059e-09 | 0.0762 | **yes** | no |
| p | 1.009351e-07 | 9.878745e-09 | 0.0979 | **yes** | no |
| nuTilda | 1.181681e-07 | 7.485783e-09 | 0.0633 | **yes** | no |

**All six pass the gate; all six fail the condition the gate claims to test.** The gate
returns PASS whenever `initRes < 1e-7` — it is a **1e-7 gate wearing a 1e-8 label**, and its
sole input is the other number printed on the same line. It could not have returned
anything else, and it would read identically on a run four times further from convergence.

**Worst of all, it passes loudest on the field that is provably never going to converge:**
`nuTilda` has the largest `initRes` (1.182e-7, plateaued, §3.5) and one of the *smallest*
`finalRes` (7.486e-9, comfortably "below 1e-8").

**W-2 disposition:** `finalRes` may be reported. **The 1e-8 convergence verdict must be
withdrawn from it and re-derived from `initRes`, or from the presence of DAFoam's
`satisfied the prescribed tolerance` line — which is absent (§3.2).**

## 5.2 IG-2 — the geometric-constraint rows cannot move under the IDWarp patch

`W5_GRADIENT_REGRADE.md` §1 and the 08-11 diagnosis §1.2 row 4(a) kill the
"summation over patches" mechanism partly on the observation that `volcon`, `thickcon` and
`rcon` *"read 4.37e-12%, 1.27e-11% and 1.36e-08% and **do not move** under the patch."*

**Executed over frame Lct — all 14 archived logs carrying these rows:**

| quantity | distinct values across 14 logs |
|---|---|
| `geometry.rcon` wrt `shape` | **3** |
| `geometry.thickcon` wrt `shape` | **3** |
| `geometry.volcon` wrt `shape` | **3** |
| `CD` wrt `shape` | **13** |

The three constraint rows take exactly **three value-triples**, and the partition is by
**case and FD step size only**:

* `1.363491e-10 / 1.265004e-13 / 4.366597e-14` — **11 logs**, the A1 case at default step.
  That set spans **stock and patched IDWarp**, **np=1 and np=4-scotch**, and **limiter-on,
  limiter-off and limiter-default**. Every lever this line tests.
* `3.917950e-07 / 1.972430e-12 / 7.459069e-14` — 3 logs, the sail case, **stock and patched
  alike**.
* `1.227131e-09 / 2.149984e-14 / 1.004041e-14` — 1 log, A1 limiter at FD step `h = 3e-3`.

Meanwhile `CD wrt shape` takes 13 distinct values across the same 14 logs — it moves under
every lever. **The constraint rows are a function of (case geometry, FD step) and nothing
else**, because they are pure FFD/DVGeo surface functions with no volume warp and no CFD in
their chain, and the four-line patch lives entirely inside `warpDeriv`. The same identity
holds for `CD`/`CL` wrt `patchV`, which are bit-identical stock↔patched in both case
families (`2.316770e-03`, `2.315520e-03`; sail `1.722189e-04`).

**W-2 disposition:** the *values* are informative — 1e-12 to 1e-14 agreement genuinely
validates the shared FFD/DVGeo Jacobian, and that half stands. **Their invariance under the
patch is not evidence and must not be gated on**: it would read identically if the patch had
done nothing, and identically again if the patch had destroyed `warpDeriv` outright.

---

# 6. What was killed at zero compute, and how

## 6.1 The 0.0067% question — no run can buy it (confirmed by recompute)

The limit is the *reference*, not our measurement: `0.02090` at four significant figures
resolves agreement to **±0.023923%**. No amount of compute on our side makes a
four-significant-figure reference into a five-significant-figure one. Independently, the
run's own CD is still moving by 0.007323% peak-to-peak, larger than the 0.006862% being
claimed. **Any experiment proposed to "confirm the 0.0067%" is non-discriminating by
construction and must not be proposed.** The fix is documentary and free.

## 6.2 P-2 (A6 restart to `endTime 1250`, quoted ~7 core-min) — KILLED. Do not buy it.

The 08-11 pricing reads: *"the observed 3.3×-per-100-iterations decay puts the crossing ~250
iterations out."* **That decay is `he`'s, and `he` is not the binding field.** §3.5 shows
`nuTilda` — the field with the largest `initRes` — has been flat at 1.01–1.02× per 100
iterations for the last 400 iterations.

* At `endTime 1250` (250 further iterations) `nuTilda` lands at ≈**1.13e-7**, still **~11×
  above** the tolerance. The experiment **cannot** produce the outcome it was bought for.
* Its second stated purpose — *"re-verifies CD at a genuinely converged state, which is what
  the 0.0067% claim needed"* — is refuted by §6.1 and by the 08-11 document's own §5.
* Reaching the tolerance at the measured `nuTilda` rate needs **15,573 iterations ≈ 419
  core-min**, sixty times the quoted price, and only if a 400-iteration plateau breaks.

**Every outcome of P-2 as scoped leaves belief unmoved.** The question it was bought to
answer is already answered on disk, in the opposite direction: A6 does not converge to its
own criterion on this configuration. **Killed at zero compute.**

## 6.3 The A6 adjoint attempt — must not be proposed, and its premise is wrong

An A6 adjoint attempt is the 760–1,520 core-min class. It should not be bought, for the
reason the lab already applies to that class: a zero-cost analysis decides the same question.
Here the zero-cost analysis is §3.6 — the "memory wall" is inherited from a case whose own
product-list entry says the blocker is **conditioning, not memory**, with >20 GB free, and
whose 79,560-cell probe **ran the adjoint to 200 KSP iterations twice and returned
`PetscConvergedReason: -5`**. The correct action is documentary: apply the lab's own existing
instrument — *"NOT EVALUABLE ON THIS HOST"* — instead of naming a cause that was never
measured on this case and is misnamed on the case it came from. **Free.**

## 6.4 A negative I could not report, and did not

My first adjoint sweep used the pattern
`Solving the adjoint\|adjoint equation\|dRdWTPsi\|Main iteration.*KSP Residual` and returned
**0 hits on A6 — and 0 hits on its own positive control.** Under this lab's rule that is
**UNKNOWN, not a clean**, and I did not report it. Rebuilding the pattern from strings that
actually occur (`Main iteration`, `KSP Residual`, `dRdWT`, `Adjoint States`) gave controls
of 16/18/17 and the result in §3.6 — which also surfaced **five A6 lines the original
pattern could never have found**, including the `5,244,840` state registration and
`dRdWT Jacobian Free created!`.

The 08-11 diagnosis ran essentially that same pattern, reported the 0, and concluded there
is nothing adjoint-shaped in the A6 logs. **It committed the exact error it had documented
sixty lines earlier as L-84** (§1.4: *"Its positive control passed and proved the grep can
fire. It did not prove that what the grep looked for was the only evidence available."*).
`dRdWTPsi` and `Solving the adjoint` occur nowhere in this archive; the control's 2 hits came
entirely from the `Main iteration.*KSP Residual` leg. Recorded as a live recurrence of L-84.

---

# 7. What genuinely needs compute — with the discriminating outcome for each

Every item states what result would change belief **and** what result would leave it
unmoved. Nothing here was executed; all of it is a request for the lab owner's authorisation.

### C-1 (rank 1) — `-ksp_view` readback, two arms of the existing hump rung-4 configuration, one `natural`, one `rcm`. **~8 core-min.**

Price carried unchanged from `DEAD_LEVER_AUDIT.md` M-A; not re-derived here.

* **Moves belief:** the readback prints `matrix ordering: rcm` ⇒ DAFoam's
  `jacMatReOrdering` key reaches PETSc's ordering and **257 archived runs** inherit a
  validated lever, including A5's P6.
* **Moves belief the other way:** the readback prints `natural`, or is absent ⇒ the key
  changes the preconditioner by some other route (it demonstrably does: 86 vs 79 GMRES
  iterations on a matched single-change pair) and **every "rcm arm" label in the archive is
  mis-named**, which is a bigger finding than the pass.
* **Leaves belief unmoved:** nothing — both branches are consequential. This is why it is
  rank 1 at the smallest price on the line.

### C-2 (rank 2) — patched A5 pressure-loss `check_totals`, one arm, `useRotations=False`. **~16 core-min.**

Basis: `W5_GRADIENT_REGRADE.md` §0 measured the a5pl stock+patched **pair** at 235 s + 250 s
at 4 ranks = 32.3 core-min contended; one arm is half.

* **Moves belief:** the surviving **2.2372%** collapses ⇒ regime 2 (the ill-conditioned band
  above the guard threshold) is the carrier, and A5's residual is the same defect's tail.
* **Moves belief the other way:** it survives ⇒ regime 2 is not the carrier, and the
  CFD-adjoint link — which the bypass probe already reads at 0.168–0.88% at idx8, the same
  order as 2.24% — moves to rank 1. A5 then has a second open mechanism.
* **Leaves belief unmoved:** only a null between roughly 1.5% and 2.0%, which the archive
  gives no reason to expect. Acceptable.

### C-3 (rank 3) — operator-level cross-residual on A1 **serial** with the limiter: the A4 instrument applied to M2. **~2 core-min.**

Basis: `ledger_r7.txt` records `a1lim_np1` at 192 s at `cpus_cap=2` = 6.4 core-min for a full
17-primal `check_totals`; an operator probe needs one adjoint, not 17 primals.

* **Moves belief:** cross-residual ≫ the serial floor ⇒ M2 is an **operator** defect of A4's
  kind, in a case with no processor boundary in it. The upstream filing gains a second
  operator-level exhibit and a single-process reproducer, and §1.3's open question closes.
* **Moves belief the other way:** cross-residual at the floor ⇒ M2 is a tape inconsistency
  visible only to the FD, the filing must say so explicitly, and "the branch defect is an
  operator defect" narrows to A4.
* **Leaves belief unmoved:** nothing. This is the cheapest open question on the whole line
  and it is currently unranked anywhere.

### C-4 (rank 4, **re-scope before buying**) — the `A5DOBJDXV` warp-bypass probe extended from 3 components to all 27, np=1. Quoted ~25 core-min.

* **Moves belief:** it partitions A5's 2.24% between IDWarp and the CFD-adjoint link across
  the whole vector rather than at one component.
* **Leaves belief unmoved — and this is a live risk, not a hypothetical:** §2.1 shows the
  probe's own step-refinement already **fails at idx17 and idx2** (`||delta_Xv||` 2.6–3.1,
  outside the linear regime, with a sign flip appearing between steps). Run as-is at one step
  on 27 components, most components would return numbers whose own instrument is out of band,
  and no outcome would be interpretable. **It must be re-scoped to two steps per component
  with a per-component linearity acceptance criterion registered in advance, or not bought.**
  Its price is also the least well-based number in the 08-11 table, by that table's own
  admission. **Do not buy it before C-2**, whose result may make it unnecessary.

### 7.4 Not proposed, and why

* **P-2 as scoped** — §6.2. Cannot produce its own target outcome.
* **Any A6 tutorial-agreement re-verification** — §6.1. The reference bounds it.
* **An A6 adjoint attempt** — §6.3. The zero-cost analysis decides the same question, and
  the premise is misnamed.
* **A stock-IDWarp + limiter interaction arm for A1** (§1.3). It would be a real measurement,
  but no current claim turns on it: M1 and M2 are each established independently and the
  graded FAIL is M1's. Filed as an idea, not priced, so it does not compete with C-1..C-3.

---

# 8. The defect report — currency, line by line, for its owner

`demo-output/website/latex/dafoam_defect_report.tex` and its PDF. **I did not edit either
file.** This section is an inventory for the designated owner.

## 8.1 How I read each artifact — stated, because the sibling failed exactly here

* **`.tex`** — `/usr/bin/grep -n` and `git grep -a -n` over the full 3,922 lines; also read
  directly at lines 80-125, 1055-1100, 1168-1230, 1420-1452.
* **Build currency by timestamp** — `.tex` `2026-08-11 03:24:39`, `.pdf` `2026-08-11
  03:26:38`. The PDF is **newer than** its source: consistent with a build from the current
  `.tex`. **Contrast with the sibling:** `closure_challenge_report.tex` is
  `2026-08-12 17:54:12` against a `.pdf` of `2026-08-11 03:26:36` — the source is **a day and
  a half newer than the PDF**, which is the known stale-artifact pattern. That sibling
  carries **zero** A6/CRM claims (`/usr/bin/grep -c "0.0067\|CRM\|crm_wing"` → 0), so its
  staleness is not on this line, but it is real and is filed as **D205**.
* **PDF text layer** — `pdftotext -layout`, 71 pages. Every string checked reproduces the
  current `.tex` exactly.
* **PDF read VISUALLY** — and this is the step a text extract cannot substitute for, because
  `\sout{}` is strike-**and-keep**: a withdrawn line sits in the text layer of a correctly
  repaired report exactly as in a stale one. I rendered **page 1** and **page 20** with
  `pdftoppm -png -r 130` and read the images. **Result: no strikethrough rules appear on
  either page, and `/usr/bin/grep -c "sout" dafoam_defect_report.tex` returns 0 — this
  report contains no withdrawn content at all.** Every claim below is therefore live in the
  PDF in ordinary roman type, not struck-and-kept.
* Title page, read visually: dated **2026-08-10**. It predates the 08-11 diagnosis entirely.

## 8.2 What is already correct — stated first, because most of it is

The report is **structurally right and better than the surfaces in §4.** It documents both
mechanisms, in separate sections, and names them separate defects:

* `:1420-1429` opens *"The IDWarp rotation guard"* with *"This defect is independent of
  Section~\ref{sec:decomp} in code and in provenance"*, and `:344` calls it *"the independent
  defect of Section~\ref{sec:idwarp}"*.
* `:1178` and `:3620` **name component 6** as the limiter-flipped component
  (*"Component 6 --- the sign-flipped one"*, *"One of the eight components (index 6) is
  sign-flipped"*), and `:1624` names `idx6 (leading-edge combo)` for the rotation guard.
* `forceMeshWaveFrozen` appears **zero** times. The refuted mechanism is not in this document.
* `:230` states the M1 patch is **`primal md5-identical`** — verified true (§1.1 E2).
* Table 7's caption (`:1069`, read visually on p20) states every one of the 17 primal solves
  reached `primalMinResTol 1e-8` with *"worst final residual 9.99e-9"*. **Verified sound
  for A1** — unlike A6, these logs contain the `satisfied the prescribed tolerance` line 17
  times each, and the worst is `Minimal residual 9.993942762461952e-09`. IG-1 does **not**
  bite here.
* **No A6/CRM claim of any kind exists in this document.** The only `CRM` token is `:1260`,
  a literature row about *ADflow, PAS 2019*. **The defect report is not a carrier of any of
  the four wrong A6 statements.** Its owner has nothing to do about A6.

## 8.3 What would need to change — three items, all about A1

**(1) `:100-101` (abstract, page 1) and `:225` (D1s summary row) and `:1133`.**

> *"the limiter drives the serial adjoint to 92.8% against its own step-stable finite
> difference, with one of eight gradient components sign-flipped — **and the identical
> one-word edit returns 0.121%**."*

The word *identical* and the verb *returns* read as a repair of the same problem. **It is
not.** Executed (§1.1 E5): the one-word edit moves the converged primal CD by **2.6711%**
(`0.01956447711316437 → 0.01904188196895532`, line 551 of each log), and **the report's own
Table 8 prints the consequence** — the FD reference moves from `6.194868e-02` to
`6.522800e-02`, **5.294%**. That is **15× the 0.35% FD wobble** that R7f1 induced with a pure
instrument change, and R7f1's small wobble is what the section uses to argue *"the FD
reference is essentially resolved; the discrepancy lives in the analytic."* The 0.121% is a
real and valuable result — it establishes that the unlimited tape is differentiable — but it
is measured on a different converged flow.
**Suggested minimum change: one sentence after `:1133`**, e.g. *"R7f2's cure is not
primal-neutral: the converged \(C_D\) moves 2.67% and the FD reference with it by 5.29%, so
0.121% is an agreement on a different converged flow, not a repaired derivative of the same
one — unlike the rotation-guard patch of Section~\ref{sec:idwarp}, which is primal
md5-identical."*

**(2) `:223-230` (the D1s / D2 summary table).** These two rows sit adjacent. D2's says
**`primal md5-identical`**; D1s's says *"The same one-word edit reads 0.121%"* and says
nothing about the primal. A reader comparing them will take the two cures to be the same
kind of object. **Suggested change: add `primal moves 2.67%` to the D1s row**, which makes
the contrast self-evident at a glance and costs four words.

**(3) The strongest available fact is absent, and the report already owns the instrument
that states it.** The report never says that **D1s and D2 flip the same component of the
same case**, nor that **the D1s arms ran with the rotation guard already patched.**
Executed (§1.1 E4): all four limiter arms carry
`IDWARP_IMPORTED_FROM: /patch/idwarp/idwarp/__init__.py` at line 3 — and `:3499` of this very
document documents that stamp as the device that distinguishes a patched arm from a stock
one. So the report is **one sentence away** from stating, on its own instrument, that a
4,032-cell NACA0012 carries **two independent defects flipping the same gradient component**,
one of which survives the other's repair. That is the single most publishable fact on this
line and it is currently unstated.
**Suggested change: one sentence in `sec:branch` or `sec:idwarp`**, e.g. *"Both defects flip
component 6 of the same case. The serial-limiter arms were run against the patched IDWarp
(`IDWARP_IMPORTED_FROM: /patch/idwarp/…`, line 3 of each log), so the 92.8% is measured with
the rotation guard already removed: the two mechanisms are independent, and the four-line
patch does not account for the limiter flip."*

**Nothing else in the report requires change on this line, and nothing in it needs to be
withdrawn.** Items (1)–(3) are additions and one four-word table edit; no existing sentence
is false. Once edited the PDF must be rebuilt — the sibling in the same directory is a live
example of a `.tex` repaired while its PDF was not.

---

# 9. Docket rows filed

**D201, D202, D203, D204, D205** in `docs/DOCKET.md` §D.

IDs were asserted free **inside the write**, against the union of the working tree and
`git show HEAD:docs/DOCKET.md`. **Two assertions failed and aborted the write before one succeeded**: the
first block D184–D188 (a concurrent session had taken D184–D196), then D197–D201 (the same
session took D197–D200 in the intervening minutes). The block **D201–D205** was asserted free
against a high-water mark of **D200** and taken. **D188 is a gap in the sequence and was
deliberately NOT filled** — under concurrency a gap may be a row mid-write rather than a free
number. Nothing was reused or renumbered.

| id | subject |
|---|---|
| D201 | IG-1 — A6's `finalRes < 1e-8` convergence gate is forced by `relTol 0.1` |
| D202 | IG-2 — the geometric-constraint and `patchV` rows cannot move under the IDWarp patch |
| D203 | A6's `nuTilda` plateau; P-2 killed and re-priced at ~419 core-min |
| D204 | "memory wall" misnamed at source; `PRODUCT_LIST.md` contradicts itself |
| D205 | The `latex/` sibling PDF is stale against a `.tex` a day and a half newer |

---

# 10. Summary

| | graded symptom | at HEAD | still open |
|---|---|---|---|
| **A1** | `CD wrt shape` 11.43%, idx6 flip | **FAIL stands. Root cause INCOMPLETE, not wrong** — two independent mechanisms at the same component; `forceMeshWaveFrozen` executed-refuted; M2's cure moves the primal 2.67% and the FD 5.29%, so it is not M1's counterpart | M2 has no operator-level measurement (**C-3, ~2 core-min**); the two ladder-A records still name the refuted mechanism with no strike |
| **A5** | `OBJ.val wrt shapexUpper` 46.638%, idx8+idx17 flips | **FAIL stands, attributed to M1, bisection re-executed.** FFD link exact to 3e-12; warp-bypass at idx8 clean and step-converging; M1's repair primal-identical (FD bit-identical stock↔patched) | the **2.2372%** residual (**C-2, ~16 core-min**); the bypass probe is out of its linear regime at idx17/idx2; decomposition-invariance cited from a patched-stack run |
| **A6** | *no primal failure exists* | **FOUR published statements wrong, all still live, all free to fix**: never reached `primalMinResTol` (0 hits, controls 21/17/17/17); 0.0067% is finer than both instruments (0.023923% / 0.007323%); the 8.5e8 T-residual is a units artifact a validated ONERA run shows at 5.9e8 and A4 has none of; **"memory wall" is inherited from a case whose own entry says conditioning, not memory** | nothing needing compute. **P-2 killed** — `nuTilda` plateaued at 1.02×/100 iterations, 15,573 iterations from tolerance |

**Two identity-gates** (§5): A6's `finalRes < 1e-8` verdict is forced by `relTol 0.1`
(0 violations in 66 lines, max ratio 0.099617); the geometric-constraint and `patchV`
`check_totals` rows cannot move under the IDWarp patch (3 distinct value-triples across 14
logs, partitioned by case and FD step alone, against 13 distinct values for `CD wrt shape`).
Both are reportable under W-2; **neither may be gated on.**

**Killed at zero compute:** one priced experiment (P-2, ~7 core-min as quoted, ~419 core-min
as correctly priced), one experiment class that must never be proposed (any 0.0067%
re-verification), and one 760–1,520 core-min item whose premise is misnamed.
