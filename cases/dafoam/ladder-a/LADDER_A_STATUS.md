# LADDER A — STATUS TABLE

**Compiled 2026-08-21 ~19:10Z, Lane A.** One row per case per toolchain, as the verdict vocabulary
requires. **Nothing here is filed, sent or registered anywhere.** This file edits no frozen record;
every number is copied from the graded record named in its own row, and where a record disagrees with
itself the disagreement is noted rather than resolved silently.

**Toolchain identities.**
**SHIPPED** = `dafoam/opt-packages:latest`, `libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663`.
**PATCHED** = `dafoam-idwarp-rot:v1`, md5 `85f59e87253e0a71a813f64ca6e4c425` — the `getRotationMatrix3d`
degenerate-branch fix. Two rows marked **†** were delivered as *the same patched IDWarp bytes
bind-mounted onto `PYTHONPATH` over the stock image*, not as the image, and state no md5; they are
labelled rather than merged with the image rows.

**Verdict vocabulary.** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
**Grading band** (set by the step-size study): **PASS ≤5% with zero flagged components; CONDITIONAL
5–15%; >15% or ANY sign flip ⇒ FAIL.**

---

## The table

| # | case | scope | tool­chain | np / cells | **verdict** | headline number (exact) | record |
|---|---|---|---|---|---|---|---|
| 1 | **A1** NACA0012 | gradient | SHIPPED | 1 / 4,032 | **GATE FAIL** | `CD wrt shape` **11.4274%** (`1.142740e-01`); **1 sign flip, idx6 at 640.3696%** | `A1/reverify_patched_idwarp_np1/RESULTS.md` §2 |
| 2 | **A1** NACA0012 | gradient | **PATCHED** | 1 / 4,032 | **PASS** | `CD wrt shape` **0.03796%** (`3.795529e-04`); **zero flips**; idx6 now 1.1888%, right-signed — a **301× aggregate improvement** | `A1/reverify_patched_idwarp_np1/RESULTS.md` §2, §4.2 |
| 3 | **A2** MACH tutorial wing | gradient | SHIPPED | 4 / 38,304 | **PASS** | `CD`/`shape` **1.714%** (AN `4.801625e-02` vs FD `4.858158e-02`); zero flagged components | `A2/grading_confirmation/RESULTS.md` §1, §3 |
| 4 | **A2** MACH tutorial wing | gradient | **PATCHED †** | 4 / 38,304 | **PASS** | `CD`/`shape` **0.0506%** — **33.9× tighter**; `CL`/`twist` **115.1× tighter**; `CD`/`twist` the one row that **degrades**, 0.389% → **0.505%** | `A2/grading_confirmation/RESULTS.md` §3 |
| 5 | **A2** MACH wing | **optimisation** | SHIPPED | 4 / 38,304 | **OPTIMISATION RUN, NOT A RESULT** | 47 of ~100 majors; **no `EXIT` line anywhere**; `inf_pr` 1.44e-05 / `inf_du` 9.0e-05 vs `tol` 1e-5; 28.275488% drag cut **at the point the 60-min clock stopped**; **destroyed its own case directory** | `A2/grading_confirmation/RESULTS.md` §4 |
| 6 | **A3** ONERA M6 | **original rung, adjoint** | SHIPPED | 4 and 2 / **399,360** | **BLOCKED** | **8 mitigations exhausted, no gradient ever reached**: OOM at 12g **and** 18g at the identical coloring step; np=2 drove host `MemAvailable` to **1.77 GB** | `A3/grading_confirmation/RESULTS.md` §1c, §3 |
| 7 | **A3** ONERA M6 | original rung, **serial memory plan** | — | **1** / 399,360 | **BLOCKED** | predicted serial peak RSS **66.0–93.6 GiB** (8 models, median 74.0) vs Sanaa's **24 GiB** gate — **2.7×–3.9× over**. Largest mesh that fits 24 GiB: **~102k–137k cells**. **No arm run; $0.00 spent** | `A3/original_memory_plan/PREREGISTRATION.md` **(new, 2026-08-21)** |
| 8 | **A3** ONERA M6 | original rung, primal | SHIPPED | 4 / 399,360 | **GATE REACHED** | CD `0.0229955633492643`, CL `0.3131158872361974`, 1244.2 s | `A3/grading_confirmation/RESULTS.md` §1 |
| 9 | **A3** sweep rung 1 | gradient | SHIPPED-equiv‡ | 4 / 21,840 | **PASS** | `patchV[1]` **0.18%**, `shape[115]` **0.93%** (2 of 4 rows not evaluable) | `A3/grading_confirmation/RESULTS.md` §2b |
| 10 | **A3** sweep rung 2 | gradient | SHIPPED-equiv‡ | 4 / 42,120 | **PASS** | **0.0077% / 0.2740% / 0.0172%**, all three evaluable — the tightest stock numbers on the ladder | `A3/grading_confirmation/RESULTS.md` §2c |
| 11 | **A3** sweep rung 3 | adjoint | SHIPPED-equiv‡ | 4 / 79,560 | **GATE FAIL** | adjoint **4,000 iterations, `reason −3`, 1.31× residual reduction** — and **memory was comfortable at 11.65 of 22 GiB**, so this is a conditioning wall, not a memory one | `A3/grading_confirmation/RESULTS.md` §2d |
| 12 | **A3** all rungs | gradient | **PATCHED** | — | **PENDING — NOT MEASURED** | *"No patched-IDWarp arm was ever run on A3, at any mesh size"* | `A3/grading_confirmation/RESULTS.md` §3, §5.1 |
| 13 | **A4** Ahmed body | gradient @ baseline | SHIPPED | 1 / 2,777 | **PASS** | `dCD/dshape` **1.10%** (AN `2.3965e-01` vs FD `2.4232e-01`, `a4_np1_stock.log`) | `A4_ahmed_body.md:256-264` |
| 14 | **A4** Ahmed body | gradient @ baseline | **PATCHED †** | 4 / 2,777 | **PASS** (diagnostic corroboration, not the graded configuration) | **0.00054%** at np=4 under `simple` 4×1×1 | `A4_ahmed_body.md:196`, `:261` |
| 15 | **A4** Ahmed body | **optimisation** | **PATCHED** | 1 / 2,777 | **PASS** | **`EXIT: Optimal Solution Found.`, 9 majors, NLP error `6.2814e-07` < `tol 1e-6`**; CD `0.15297385` → **`0.14153492`, −7.478%**; `shape` **−0.04999982** at the bound, feasible | `A4/first_optimisation_np1/RESULTS.md` §2 **(new, 2026-08-21)** |
| 16 | **A4** Ahmed body | gradient **@ the optimised design** | **PATCHED** | 1 / 2,777 | **PASS** | **0.4936%** (`4.936157e-03`; AN `2.141012e-01` vs FD `2.151633e-01`), **zero sign flips** — the lab's first gradient graded at a *deformed* design point | `A4/first_optimisation_np1/RESULTS.md` §3 |
| 17 | **A4** Ahmed body | optimisation / endpoint gradient | SHIPPED | — | **NOT MEASURED** | the item registered a single-image design; no claim is made either way about whether the patch mattered to the optimisation | `A4/first_optimisation_np1/RESULTS.md` §5 |
| 18 | **A4** Ahmed body | trivial baseline (`scaler=-1.0`) | **PATCHED** | 1 / 2,777 | **NOT A RESULT** (control behaved as designed) | CD **rose 9.090%** to `0.16687879`; `shape` ran to the **opposite** corner, **`+0.04992374`** | `A4/first_optimisation_np1/RESULTS.md` §4 |
| 19 | **A5** U-bend | gradient | SHIPPED | 1 / 4,800 | **GATE FAIL** | `OBJ.val wrt shapexUpper` **46.840%** (`4.684019e-01`); **2 sign flips** — idx8 at 205.52%, idx17 at 121.86% | `A5/reverify_patched_idwarp_np1/RESULTS.md` §2 |
| 20 | **A5** U-bend | gradient | **PATCHED** | 1 / 4,800 | **PASS on the aggregate band** (per-component caveat, §5 of the record) | **2.768%** (`2.768361e-02`); **0 flips**; 22 of 27 components within ±12%; idx16 **0.90%** | `A5/reverify_patched_idwarp_np1/RESULTS.md` §2 |
| 21 | **A6** CRM wing-alone | **full size, adjoint** | SHIPPED | — / **579,072** | **BLOCKED (memory) — and independently BLOCKED (conditioning)** | predicted peak RSS **94.7–116.0 GiB** across 5 models vs a **30 GiB** box (**3.2×–5.8×** short); and the same solver **stagnates at 79,560 cells** with memory comfortable. **Recorded from prediction; deliberately not run** | `A6/adjoint_feasibility/RESULTS.md` §1 |
| 22 | **A6** CRM wing-alone | full size, adjoint | **PATCHED** | — | **NOT MEASURED** | no A6 adjoint of any kind exists at full size on either image | `A6/adjoint_feasibility/RESULTS.md` |
| 23 | **A6** CRM wing-alone | full size, primal | SHIPPED | 4 / 579,072 | **GATE REACHED** | force-stationary at CD **`0.02090143421526141`**; tolerance never met | `A6_crm_wingbody.md`; `A6/README.md` |
| 24 | **A6** rung **N=16** | adjoint | SHIPPED | 1 / 41,760 | **PASS** | **517 GMRES iterations, `PetscConvergedReason: 2`**, monotone over six decades — **the first A6 adjoint that has ever existed**; A3 rung 2 needed 987 at the same size | `A6/rung_n16_np1/RESULTS.md` §5 **(new, 2026-08-21)** |
| 25 | **A6** rung **N=16** | gradient | SHIPPED | 1 / 41,760 | **GATE FAIL** | `CD/twist` **56.24–341.51%, 3 sign flips**; **8 of 9 components >15%**; vector norm `8.893021e-01` | `A6/rung_n16_np1/RESULTS.md` §6.1, §6.2 |
| 26 | **A6** rung **N=16** | gradient | **PATCHED** | 1 / 41,760 | **GATE FAIL** | `CD/twist` **57.06–340.70%, 3 sign flips**; **8 of 9 >15%**; vector norm **`8.895816e-01`**. Only `patchV` idx1 (AoA) passes, at **3.29%** | `A6/rung_n16_np1/RESULTS.md` §6.2, §9.2 |
| 27 | **A6** rung **N=16** | patch effect (analytic vs analytic) | both | 1 / 41,760 | **PASS** | `CD/patchV` **bit-identical** across images; `CD/twist` moves **0.664% in L2 norm** — vs **97–99.5%** for the same defect on A1/A2/A5 shape rows | `A6/rung_n16_np1/RESULTS.md` §6.4 |
| 28 | **A6** rung **N=29** | adjoint + gradient | — | — / 79,560 | **NOT RUN — GATE NOT MET** | Sanaa approved N=29 **only if N=16 passes on the patched image**. It does not (row 26). **Nothing launched, staged or queued; $0.00 spent** | `A6/rung_n16_np1/RESULTS.md` §9.2; `A6/README.md` |
| 29 | **Step-size study** | FD calibration | SHIPPED | 2 / 4,032 (on A1) | **calibration probe — sets the bands; carries no PASS/FAIL of its own** | **11.43% at step 1e-3** vs **94.95% at 1e-8**; 4.28% at 2e-2 (a coincidental low point); **1e-1 and 5e-2 FAILED to converge**. Recommends **1e-3 to 1e-2, central, `step_calc=abs`** | `A_stepsize_study.md` |
| 30 | **Step-size study** | FD calibration | **PATCHED** | — | **NOT MEASURED** | no step sweep was ever run on a patched image. Nearest patched point is a **single-step control**, not a sweep: A1 arm 3 reads **132.75%** (`1.327522e+00`) at 1e-8 against 0.03796% at 1e-3 | `A1/reverify_patched_idwarp_np1/RESULTS.md` §4.3 |

**†** patched IDWarp delivered by **bind-mount onto `PYTHONPATH`** over the stock image, not as
`dafoam-idwarp-rot:v1`; no md5 is stated in those records.
**‡** A3's sweep rungs ran on `dafoam-subpclu:v1` with `DAFOAM_SUBPC_TYPE` **unset** and **stock
IDWarp** — described in the record as *SHIPPED-equivalent*, which is not the same thing as the stock
image and is labelled here rather than merged.

---

## What the table says when read down the columns

**1. The rotation patch is the single largest effect on this ladder, and it is not uniform.**
Every A/B pair that has been measured improves: A1 **11.4274% → 0.03796%** (301×), A5 **46.840% →
2.768%** (16.9×), A2 **1.714% → 0.0506%** (33.9×). **Two sign flips on A5 and one on A1 disappear
entirely.** But on A6's `twist` the same patch moves the derivative by **0.664%**, and on A2's
`CD/twist` it moves the answer the *wrong* way (0.389% → 0.505%). **The defect's reach is
objective-dependent, not DV-class-dependent** — A6 row 27 settles that, because `twist` there
provably crosses the warp chain (its analytic derivative moves) and still only shifts 0.66%.

**2. The FD-invariance control held on every A/B pair ever measured.** A1 8 of 8 raw components
bit-identical, A5 27 of 27 (`max |FD_stock − FD_patched| = 0.0`), A2 all 18 rows, A6 all 9.
**`dafoam-idwarp-rot:v1` is validated as derivative-only**, and every stock-vs-patched comparison on
this ladder is a comparison of two derivatives of the *same* function.

**3. Three cases are blocked, and the three blockers are different.**
A3-399k is **memory** (rows 6, 7). A3-rung-3 at 79,560 cells is **conditioning with memory
comfortable** (row 11). A6-full is **both, independently** (row 21). Conflating them produces a false
statement, and the A3 record says so explicitly.

**4. The patched column is emptier than it looks.** Rows 12, 17, 22 and 30 are **NOT MEASURED**:
A3 has never been run on a patched image at any size; A4's optimisation has no shipped counterpart;
A6 full size has no adjoint on either image; and no FD step sweep has ever been run patched.

**5. Two cases now have a converged optimisation-grade result, and only one of them counts.**
A2's 47-iteration run is **NOT A RESULT** — no `EXIT` line, first-order metrics an order of magnitude
above their own tolerance, stopped by a wall clock, and it destroyed its own case directory (row 5).
A4's stops on `Optimal Solution Found.`, re-verifies its gradient at the endpoint, and both case
directories survive (rows 15, 16, 18).

**6. The newest and least comfortable finding: a converged adjoint can outrun its own FD reference.**
A6's N=16 rung produced a genuine, first-of-its-kind converged adjoint (row 24) and then **GATE
FAILED its verification on both images** (rows 25, 26) — because the primal stopped 556× short of
tolerance, leaving a derivative noise floor of 4.5e-3 that 8 of 9 FD magnitudes never cleared. The
same test applied to A4 the same afternoon gives **453× clearance** and a clean 0.4936% PASS.
**The discriminator between the two is whether the primal converged — not the toolchain, not the DV
class, not the mesh size.**

---

## Known internal inconsistencies, listed rather than silently resolved

1. **A1's aggregate is quoted two ways in its own record**: §2's verdict table reads `3.795529e-04`,
   §4.2's header reads `3.795511e-04`. Both round to 0.03796%. Row 2 uses §2's.
2. **A6 has two distinct scopes that must not be merged** — full size 579,072 cells (BLOCKED, no
   adjoint on either image) and the N=16 rung at 41,760 cells (GATE FAIL on both). Rows 21–28 keep
   them separate.
3. **A3's "1.26% ONERA M6" figure is not an A3 result** — it is IDWarp's own `onera_m6` test mesh
   under `verifyWarpDeriv`, with no DAFoam, OpenFOAM or CFD in it. Graded **NOT A RESULT for Ladder
   A3** and deliberately absent from this table.
4. **A3 has two campaigns on two mesh families** (rows 6–8 vs 9–11); the record states that merging
   them "produces a false statement".
5. **A4's graded shipped PASS does not live in a `RESULTS.md`** — it is in the 2026-08-04 supersession
   note inside the frozen `A4_ahmed_body.md`. Row 13 cites it by line.
6. **A6 rung N=16's `RESULTS.md` §5 contains a superseded peak-RSS figure (7.396 GiB)**, corrected in
   the same file's §6.6 to **9.787 GiB** and corroborated independently at 9.786 GiB by Lane B's
   watcher. The original sentence is preserved with an inserted pointer, per the no-deletion rule.
7. **Two np=4 measurements at 79,560 cells disagree by 1.48×** (17,603.8 MiB in the memory envelope's
   fit vs 11.65 GiB in `A3_RUNG3_N52_RESULT.md`), unreconciled anywhere. Carried into row 7's
   prediction band deliberately.

---

## Compute spent on the rows dated 2026-08-21 (this lane)

| item | core-min | $ @ $0.0513/core-hour |
|---|---|---|
| A6 rung N=16 — calibration, attempt 1 (gate fail), interrupted attempt 2, **and both graded arms** | **76.653** | **$0.0655** |
| A4 first optimisation — arms (a)+(b)+(c) | **13.150** | **$0.0112** |
| A3 serial memory plan — **prediction only, no arm** | **0** | **$0.00** |
| A6 rung N=29 — **gate not met, not run** | **0** | **$0.00** |
| **TOTAL** | **89.803** | **$0.0768** |

Of the A6 figure, **17.95 core-min (23.4%) is waste** — one contaminated calibration primal, one
gate-fail attempt, one run interrupted by a session loss. Registered ceilings were 160 core-min (A6,
used 47.9%) and 60 core-min (A4, used 21.9%); **neither was reached and no arm was dropped for cost.**

---

*Last updated 2026-08-21 ~19:10Z. Rows 7, 15, 16, 17, 18, 24, 25, 26, 27 and 28 are new today.
Ladder B is a separate lane and a separate table; nothing here describes it.*

---

## Addendum 2026-08-22 (supervisor) — rows added by the day's items; the table above is not edited

| # | case | scope | toolchain | np / cells | **verdict** | headline number (exact) | record |
|---|---|---|---|---|---|---|---|
| 31 | **A4** Ahmed body | **optimisation** | SHIPPED | 1 / 2,777 | **PASS** | `EXIT: Optimal Solution Found.`, **6 majors**, NLP error `6.9114020645938298e-08` < 1e-6; CD `0.1529738469354696` → `0.14153518384107486`, **−7.4775 %**; same optimum as row 15 to 7 s.f. | `A4/shipped_optimisation_np1/RESULTS.md` §1-2 |
| 32 | **A4** Ahmed body | gradient **@ the optimised design** | SHIPPED | 1 / 2,777 | **PASS** | **0.3112 %** (`3.111803e-03`; AN `0.21410204`, FD `0.21477037`), zero flips. Not a toolchain comparison against row 16: analytic gradients agree to 3.9e-06, the FD references differ by 1.83e-03 (L-229) | §3 |
| 33 | **A4** Ahmed body | gradient @ baseline | **PATCHED** (image, hash-certified) | 1 / 2,777 | **PASS** | **0.33929 %** (`3.392911e-03`; AN `0.24149949`, FD `0.24232166`), zero flips — fills row 14's "not the graded configuration" gap | §4 |
| 34 | **A2** MACH wing | gradient, **per-component** | SHIPPED | 4 / 38,304 | **PASS (aggregate) — 7 of 96 CD components beyond 15 %** | CD idx18 **−360.75 %**, idx46 −326.14 %; CL idx15 −80.20 %; zero flips | `A2/per_component_table/RESULTS.md` |
| 35 | **A2** MACH wing | gradient, **per-component** | **PATCHED †** | 4 / 38,304 | **PASS (aggregate) with a per-component caveat — 1 sign flip, CD idx46** | AN `+2.27367571e-06` vs FD `−2.52460969e-06`; CL 96/96 within 5 % | same, §3.2 |

Rows 3-4's "zero flagged components" and `A2/grading_confirmation/RESULTS.md` §1's "no sign flip
anywhere in A2" are superseded by rows 34-35; the frozen files are not edited. Cost of the day's
A4 item: **13.616 core-min = $0.0116** (34 % of a 40 ceiling); A2 item **$0.00**.

**Footnote to row 12 (A3, patched column), added 2026-08-22 by the supervisor; the row is
unchanged at PENDING — NOT MEASURED.** First attempt 2026-08-22
(`A3/rung2_patched_idwarp_np4/PREREGISTRATION.md`, `a5605f54` + Amendment 1 `a94e8317`): the
np=4 arms never launched (host core gate, min `load1` 18.28 over 12 polls); the np=1 arm was
stopped inside the `dRdW` colouring on a measured projection. **12.150 core-min, $0.0104, no
gradient.** The np=1 re-price is refuted by its own measurement (colouring 3.03× bigger at one
rank — L-232, N-D11); the item reverts to the frozen np=4 configuration.

**Addendum row 36, added 2026-08-22 by the supervisor.**

| # | case | scope | toolchain | np / cells | **verdict** | headline number (exact) | record |
|---|---|---|---|---|---|---|---|
| 36 | **A6** rung **N=16** | gradient, **fixed FD reference** | **PATCHED** | 1 / 41,760 | **PASS on a 3-component graded subset**; `twist` idx6 **NOT A RESULT** (flagged) | aggregate **1.0099 %**, zero sign flips: `patchV`1 **0.940 %**, `twist`0 **1.706 %**, `twist`3 **1.817 %** — against rows 25-26's 3.29 % / 341.51 % FLIP / 159.35 % FLIP. `twist`6 excluded by name (clearance 2.42×, plateau 83.53 %). Adjoint **verified on those three and no others**; 5 of 9 components never re-measured | `A6/rung_n16_fixed_reference/RESULTS.md` |

Rows 25-26's three sign flips are **superseded as FD-reference artefacts, not adjoint defects** — the
frozen files are not edited; the analytic column is unchanged and provably so (one fixed analytic
value per component reproduces the error at both steps). **Row 28 stands: N=29 remains NOT RUN, gate
NOT MET** — a subset PASS is not a rung PASS while five of nine components sit unmeasured. Cost of
the item: **63.166 core-min = $0.0540**.

---

## Addendum 2026-08-22 (supervisor) — row 12 splits, and one reading of this file is struck

Row 12 as written spans *"A3 all rungs"* and quotes *"No patched-IDWarp arm was ever run on A3, at
any mesh size."* **That sentence is now false, so the row cannot simply be flipped — it splits.**
The original rows are not edited.

| # | case | scope | toolchain | np / cells | **verdict** | headline number (exact) | record |
|---|---|---|---|---|---|---|---|
| 12 | **A3** sweep rung 2 | gradient | **PATCHED** | 4 / 42,120 | **PASS** | `patchV[1]` **0.0077 %** (analytic bit-identical to stock), `twist[1]` **0.2740 % → 0.9279 %**, `shape[115]` **0.0172 % → 0.1586 %** — the patch is applied and **every warp-crossing row gets worse**; patch effect **1.469586 %** in L2, 3 analytic sign flips (idx 12, 13, 24, no FD there) | `A3/rung2_patched_idwarp_np4/RESULTS.md` §2, §5 |
| 12b | **A3** rungs 1, 3 and the 399,360 campaign | gradient | **PATCHED** | — | **PENDING — NOT MEASURED** | rung 2 is now measured; no patched arm exists at any other A3 size | same, §10.6 |
| 12c | **A3** sweep rung 1 | gradient | **PATCHED** | 4 / 21,840 | **PASS** (per-component rule) **/ FAIL pending investigation** (aggregate band) — **DUAL READING, NOT FINAL UNTIL SANAA RULES** | `patchV[1]` **0.1816 %**, analytic bit-identical to shipped; **`shape[115]` 0.9273 % → 0.3826 %, i.e. 2.42× BETTER** — **the identical unchanged library that made this row 9.2084× worse at rung 2 makes it better at rung 1**, because the shipped signed error `analytic − FD` is `+2.2401e-05` at rung 2 and `-1.141009e-03` at rung 1; patch effect **0.940327 %** in L2, 120 of 120 components differing, **0** analytic sign flips; `twist[1]` and `shape[5]` **FLAGGED before the run**, **NOT A RESULT** in the FD column on every arm | `A3/rung1_patched_idwarp_np4/RESULTS.md` §1–§3 |
| 12d | **A3** sweep rung 3 | adjoint | **PATCHED** | 4 / 79,560 | **NOT A RESULT — stopped by memory** | killed at **85 s of a 2600 s budget** by its own registered guard on the **HOST FLOOR** limb (`MemAvailable 7.3944 GiB < 8.0`, 3 consecutive samples) while its **own** RSS sat at **9.202 of 15.0 GiB** — the arm did not exceed its budget, the box did. **0 of 11 identity checkpoints reached**, no adjoint, no gradient, **no claim in any direction**; cap not raised, no second budget. Re-registration proposed | `A3/rung3_patched_idwarp_np4/RESULTS.md` §1–§3 |

**Row 12b is superseded in part, and not edited.** Its **rung-1** cell is answered by row **12c**
and its **rung-3** cell by row **12d**. Its **399,360-cell** cell stands unchanged at
**PENDING — NOT MEASURED**, BLOCKED for reasons neither item touches.

**Two findings from those items are ROUTED, not actioned here, and no row above is edited for
them.** (a) The fresh literal-`dafoam/opt-packages:latest` arm at rung 1 reproduced the archived
SHIPPED-equivalent ‡ row **bit-for-bit** — analytic, FD, baselines and drift. That ‡ equivalence
assertion carries every SHIPPED-equivalent row on this ladder (rows 9–11 among them) and **had
never been tested directly at any A3 rung**; it is now tested at one, and **row 9's grade is left
exactly as it is** (R11: a patched number never moves a shipped grade, and this is a shipped-column
finding for the supervisor to route). (b) At rung 3 the registered launch gate's memory limb
(**16 GiB**) is arithmetically incapable of protecting the registered neighbourliness floor
(**8 GiB**) for an arm peaking at **≥ 9.2 GiB**: `16.0 − 9.2 = 6.8 < 8.0`. **Both numbers are
frozen and neither was changed.**

**Reading 1 of this file is struck as falsified.** The sentence at line 67 — *"Every A/B pair that
has been measured improves"* — was true of A1, A2 and A5 and is **not** true of A3 rung 2, the first
measured pair that **degrades** (N-D18). The line is left in place, unedited, and struck here.
**Reading 2 gains a fifth confirming case:** the FD column is bit-identical across images on every
A/B pair measured to date, A3 rung 2 included.

**Addendum row 37, added 2026-08-22 by the supervisor — the A6 N=16 table is complete.**

| # | case | scope | toolchain | np / cells | **verdict** | headline number (exact) | record |
|---|---|---|---|---|---|---|---|
| 37 | **A6** rung **N=16**, all nine components | gradient, fixed FD reference | **PATCHED** | 1 / 41,760 | **8 of 9 GRADED — aggregate PASS at 1.0432%**, `twist` idx6 **NOT A RESULT** (flagged by name) | `patchV`0 **0.569%**, `patchV`1 0.940%, `twist`0 1.706%, `twist`1 **1.359%**, `twist`2 **1.733%**, `twist`3 1.817%, `twist`4 **1.032%**, `twist`5 **0.389%**; zero sign flips. The five bought here read **57.62 / 67.93 / 57.06 / 90.17 / 82.79%** at the predecessor's noise-dominated step — the adjoint never moved | `A6/rung_n16_remaining_components/RESULTS.md` |

**Row 28 (N=29) is superseded in its reasoning but not in its verdict: N=29 remains NOT RUN.** The
gate's two readings are registered and **the choice between them is Sanaa's** (D464): charter-verbatim
→ NOT MET (one flagged component, unreachable by any FD arm on this rung); subset-complete → GATE
REACHED. The gap is one component and one unbought ~5 core-min arm. Cost of this item: **39.15
core-min = $0.0335**, 34.8% under a 60 ceiling, zero waste, nine registered predictions all HIT.
