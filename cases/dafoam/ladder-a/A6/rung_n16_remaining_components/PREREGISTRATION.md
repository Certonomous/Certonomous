# A6 CRM wing-alone, rung N=16 (41,760 cells), np=1: THE REMAINING FIVE COMPONENTS — PRE-REGISTRATION

**Filed 2026-08-22, DAFoam team LANE D, BEFORE any arm launched.** Predictions, gates, ceilings and
falsifiers are committed first. `RESULTS.md` will not revise this file; departures go to a dated
Amendments section there. **Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and
is Sanaa's alone** (`DAFOAM_CHARTER.md` §10; `FAMILY_SUPERVISION_GUIDELINES.md` §3.6).

**This is a PATCHED-IMAGE row.** The single arm below runs on `dafoam-idwarp-rot:v1`
(`IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425`), the image Sanaa's N=29 gate was written against.
Per `DAFOAM_CHARTER.md` §6 a patched row never replaces a shipped row and the two are never merged.
No shipped-toolchain arm is run here; the shipped row for this rung already exists at
`../rung_n16_np1/RESULTS.md` §6 and stands unchanged.

**Run root:** `/home/ubuntu/certonomous-runs/P3-a6-n16-rem/`.
**Fixed-reference item (frozen, never edited by this one):** `../rung_n16_fixed_reference/{PREREGISTRATION,RESULTS}.md`,
commits `8028d9ab` (pre-registration) and `66f42398` (results).
**Predecessor rung (frozen):** `../rung_n16_np1/{PREREGISTRATION,RESULTS}.md`.

---

## 0. Ordering disclosure — what was read before this file was written, and at what cost

**No solver arm has been launched for this item, and none will be until this file is committed**
(`SUPERVISION_CHARTER.md` §3 check 4). Everything quoted below as "measured" was read out of
artefacts that already existed on disk before this file was opened, at **zero new compute**:

* `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/{ledger.txt,queue_stage1.out,gen_arm.py,run_arm.sh,
  preflight.sh,analyse.py,fdplan_*.json}` — the fixed-reference item's machinery and its cost record;
* `/home/ubuntu/certonomous-runs/P2-a6-n16/patched.log:4995-5021` — the stored adjoint column,
  re-read from the raw log rather than from any table (the fixed-reference item's §3.3 did this
  check first; it is repeated here because this item grades five components that check did not cover);
* `../rung_n16_fixed_reference/RESULTS.md` in full, `../rung_n16_np1/RESULTS.md` §6;
* `docs/LESSONS.md` L-229, L-230, L-232, L-233; `docs/NUMERICS_KNOWLEDGE.md` N-D10..N-D17;
* four `cat`/`md5sum`/`/proc` reads of the box's own state. **No container was started.**

**Billed in §7 as 0.0 core-min.** No `docker run` of any kind has been issued by this item, not even
an inspection one — the fixed-reference item already bought the image inspections (its §7 line 0,
0.4 core-min) and this item inherits them rather than re-buying them.

## 1. What this item is for, in one paragraph, and what it is NOT for

The fixed-reference item verified **three** of the rung's nine graded components — `patchV` idx1 at
**0.940%**, `twist` idx0 at **1.706%**, `twist` idx3 at **1.817%**, aggregate **1.0099%**, zero sign
flips — and **flagged `twist` idx6** as FD-ungradeable at any step this rung can run (maximum
clearance 2.42×, plateau disagreement 83.53%). It left **five components never re-measured**:
`twist` idx **1, 2, 4, 5** and `patchV` idx **0**, which still stand where the predecessor left them,
at the noise-dominated step 1e-3, with relative errors **57.62%, 67.93%, 57.06%, 90.17%** and
**82.79%** and clearances of **0.32×, 0.27×, 0.12×, 0.07×** and **0.13×**. Its own §9 says why that
matters: *"A gate that says 'N=16 passes' cannot be read as met while the majority of the graded row
is untouched."* **This item buys exactly those five, with the same machinery, the same registered
noise rule and the same grading rule, and then computes the nine-component picture.**

**It is NOT for:** re-measuring the three already-verified components (their stored values are used,
not re-bought); re-opening `twist` idx6 (it is flagged, by name, and no step rescues it — that is
`DAFOAM_CHARTER.md` §3 and L-233, and this item does not attempt it); grading `shape` (~10²
components, excluded on cost by all three pre-registrations in this family); running, staging or
queueing anything at N=29. **Sanaa's N=29 stays NOT RUN regardless of what this item measures.**

### 1.1 The one thing this item adds to the method, and it is small

The fixed-reference item chose its four components for a **calibration triangle** and sized their
steps by hand from the clearance table. This item has five components spanning **4.6×** in `|J|`
(1.751e-03 down to 3.797e-04), and a single step pair cannot clear the noise floor on all of them.
**§4.2 registers a mechanical per-component step-selection rule instead of a hand-picked pair**, so
that the steps are a function of the stored `|J|` and the registered `η` and of nothing else — in
particular not of any FD value, none of which exists yet. That is the only methodological change.

---

## 2. Case as constructed — unchanged, and asserted at run time

| item | value | how it is asserted |
|---|---|---|
| mesh | the fixed-reference item's `base/`, 41,760 cells | copied file-for-file; `md5sum base/constant/polyMesh/points.gz` = `11b84f0de5fdf2d3e947fee8cea412a9` and `base/runScript.py` = `0de915d21166a91a9a54b37ab11214cf`, both **equal to the fixed-reference tree**; `Mesh region0 size: 41760` grepped from the log |
| image | **`dafoam-idwarp-rot:v1`** | `IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425` printed by the arm itself and asserted; anything else ⇒ **arm void** |
| solver | `DARhoSimpleCFoam`, `primalMinResTol 1e-8` (unchanged, **not** loosened) | grepped |
| decomposition | **NONE — np=1, serial, undecomposed** (`DAFOAM_CHARTER.md` §5) | `nProcs : 1`; absent ⇒ **arm void** |
| `transonicPCOption` | **1** — the only live value for `DARhoSimpleCFoam` | **activity proof:** `transonicPCOption 1;` must appear in the `DAFoam option dictionary:` dump in the log; reads `2`, or absent ⇒ **arm void** |
| `endTime` | **1000**, the value the graded adjoint run used | `Time = 1000` present, and the `ExecutionTime` block count reaches it |
| cold start | fresh staged copy of `base/`; `rm -rf processor* dRdWColoring_*.bin` before launch | first `Time step continuity errors … cumulative` must read **`-0.00504349133910657`**; a different value ⇒ warm-start contamination, **arm void** |
| **baseline objective** | **`FD_BASELINE_CD` must read `0.03506349413916734`** | this exact value has now been produced **four** times on this case — cold on the shipped image, cold on the patched image, by `s1d` `REPEAT_CALL 0` and by `s2bpv` (`../rung_n16_fixed_reference/RESULTS.md` §3.6, §6.4). A fifth reproduction proves in one number that the start was cold, that the primal state is the one the stored adjoint was linearised about, and that registered Edit 5 (§3) is numerically inert. **A different value ⇒ arm void** |
| harness | `gen_arm.py` md5 `ff85f67c304079349d378383ef46e67c`, `run_arm.sh` md5 `5e2d0724a2a2b07ad1c92bdc40b896dc`, both taken **unmodified** from the fixed-reference tree | md5s re-taken and recorded in the ledger at launch |

**`dRdWColoring_*.bin` is irrelevant at np=1 for an FD-only arm — no adjoint is computed and no
colouring is built — and it is removed anyway**, because a cold-start rule that is applied only when
it is believed to matter is not a rule (`FAMILY_SUPERVISION_GUIDELINES.md` §8; L-232 records that the
file is np-keyed).

## 3. The registered edits — five, and no more

**Edit 1 — `transonicPCOption: 2 → 1`.** Inherited from both predecessor items, same justification.
Asserted in the log as an activity proof, not merely set.

**Edit 2 — `endTime 1000`.** The archived value, and the configuration the stored adjoint column
belongs to (`DAFOAM_CHARTER.md` §5: an FD reference is part of a configuration, not a property of a
case). No arm here runs a different `endTime`.

**Edit 3 — `primalMinResTolDiff: 1.0e2 → 1.0e4`. THE VALUE IS DISCLOSED AND SO IS THE REASON.**
`1.0e4` is **exactly** what the fixed-reference item registered for its measurement arms (its §3
Edit 3) and exactly what its graded arms ran at (`P3-a6-n16-ref/ledger.txt`: `s2bpv` and `s2btw` both
print `primalMinResTolDiff 10000`). Its Amendment 3's `1.0e12` applied **only** to the two
10-iteration forward-AD probes and is **not** inherited here.
**Why `1.0e4` and not the shipped `1.0e2`:** A6 N=16's primal is a residual limit cycle (N-D14), so
`primalMaxRes` ends at 5.909e-06 against `primalMinResTol` 1e-8 — a ratio of **591**, against a
shipped cap of 100. `DASolver::checkPrimalFailure()` (`DASolver.C:2744-2752`) therefore raises
`AnalysisError("Primal solution failed!")` **before any function value is returned**, so no FD
reference of any kind can be measured with the guard at its default. **This is a widening and it is
registered as one, not inherited silently** — which is precisely what `../rung_n16_np1/RESULTS.md`
§7.2 warned against. **The guard's own verdict is already on this family's record and it is not
re-bought:** the fixed-reference item ran arm `s1a` at the shipped `1.0e2` for 6,000 iterations and
the guard fired at `rc=1`, correctly (its §3.5, N-D14). **The guard is right, the widening does not
make it wrong, and nothing in this item claims the primal converged.** Every number this item
produces is a derivative of an objective evaluated on a limit-cycling primal, and that is the whole
reason §4.2's noise rule exists.

**Edit 4 — `primalMinIters: 1000` (= `endTime`).** Registered so that the `-1e10` false-convergence
exit of **N-D17** cannot fire. `DASolver.C:188` exits on
`(primalMaxRes < primalMinResTol) && (timeIndex > primalMinIters)` with `primalMaxRes` re-initialised
to `-1e10` at `DASolver.C:222` and `primalMinIters` defaulting to **1**; where `primalMaxRes` is not
updated on a step, `-1e10 < 1e-8` is true and the run announces *"Minimal residual -10000000000
satisfied the prescribed tolerance 1e-08"* at iteration 2. With `primalMinIters = 1000` the second
clause requires `timeIndex > 1000`, which never holds inside `endTime 1000`, **so the exit is closed
for every one of the 21 primals.** **It is numerically inert on this case**: the real tolerance is
never met either (N-D14), so the setting can only remove a spurious stop, never a genuine one — and
the `FD_BASELINE_CD` assertion of §2 is what proves the inertness rather than asserting it.
**Disclosed as an edit the fixed-reference item's own FD arms did not carry**, so the two are not
byte-identical harnesses and this file says so rather than implying they are.

**Edit 5 — `printInterval: 10`.** Numerically inert — `DASolver.C:124` calls
`calcAllFunctions(printToScreen_)` every iteration and the flag gates only the `Info` output (N-D13).
It buys a **20-sample** peak-to-peak on this arm's own baseline primal at zero compute, which is the
control of §5 P-η. **It does not change the registered `η`** (§4.1).

**No other edit.** In particular `primalMinResTol` stays `1e-8`; loosening it is the
`S1_CBFS_REINVERSION` Amendment-1 incident (`DAFOAM_CHARTER.md` §3), where a primal stopped at its
first tolerance crossing missed the adjoint by `fd/adj ≈ 0.7` on all three cells. **No forward-AD
arm is registered**: N-D16 measures that the ADF build does not reproduce the plain build's primal on
this solver and returns `nan`, so there is no forward-AD reference to reach for here — the
`DAFOAM_CHARTER.md` §2 duty to reach for one was discharged by the fixed-reference item, at cost, and
its answer was **NOT AVAILABLE**. **This item states that it did not reach again, and why: because
the reach was already made and measured, not because it was not considered.**

## 4. The one arm, and the FD plan

**One arm, `rem`**, task `fdsub`: `dafoam-idwarp-rot:v1`, np=1 (`mpirun -np 1 -x PYTHONPATH`),
`--cpus=1 --memory=12g --rm`, **foreground under `timeout`**, record-only RSS watcher reading field
`$3`, one ledger line. **Baseline + 5 components × 2 steps × 2 signs = 1 + 20 = 21 primals**, central
differences throughout, `(CD⁺ − CD⁻)/(2s)`. The hand-written FD driver in `gen_arm.py` is used
unmodified — **not** `prob.check_totals`, which cannot be restricted to individual DV indices.
**No adjoint is computed by this arm.**

### 4.1 The noise rule — REGISTERED, and it is the fixed-reference item's rule verbatim

> **`η` = 1.0910e-05** — the within-run CD peak-to-peak over the last 200 iterations of the baseline
> primal at `endTime 1000`, measured at `printInterval 10` (20 samples) by the fixed-reference item's
> arm `s1a` (its §3.2 NOTE, N-D13). **This value is fixed here, before the run, and governs every
> clearance and every verdict in this item whatever this arm's own baseline measures** (§5 P-η).
> **Derivative noise floor at step `s`** := `η / (2s)` (central difference).
> **Clearance** `C(s) := |J| · 2s / η`, using the **stored adjoint magnitude** `|J_adj|` as the proxy
> for `|J_fd|` in this file because no FD value exists yet — **stated as a proxy, not as a
> measurement**; `RESULTS.md` re-states every clearance against the measured `|J_fd|`.
> **A component is GRADED only where `C ≥ 5` at the graded step AND its two steps agree within the
> registered plateau tolerance of §4.3. A component failing either test is FLAGGED and excluded BY
> NAME from every aggregate** (`DAFOAM_CHARTER.md` §3), **never rescued by a step at which it happens
> to cross.**

**The 2.47× sensitivity is declined in advance, by name.** The fixed-reference item's §8.3 discloses
that an alternative denominator — `2 × δ_repeat` = 4.4208e-06, the solve-to-solve figure of N-D15 —
would raise every clearance by 2.47×. **It is NOT adopted here.** Under it `twist` idx5 would clear
at `s = 3e-2` (C = 5.16) instead of needing `s = 2e-1`, and `twist` idx4 at 8.53×. **Registering the
looser denominator after seeing that it shortens this item's step ladder is the same failure as
adopting it after seeing that it rescues idx6**, and L-233's corollary names it. The conservative
within-run definition is used, and the cost of using it — larger steps, more truncation exposure on
the two smallest components — is carried by this item rather than argued away.

### 4.2 The step-selection rule — mechanical, and a function of `|J_adj|` and `η` only

> **REGISTERED RULE.** For each component: let the **ladder** be `{3e-2, 5e-2, 1e-1, 2e-1, 3e-1}` for
> `twist` (degrees) and `{3e-2, 1e-1, 3e-1, 1e0}` for `patchV` idx0 (m s⁻¹). Let **`s_lo`** be the
> **smallest** ladder rung with predicted `C ≥ 5`. Let **`s_hi`** be the smallest ladder rung with
> `s_hi ≥ 2 · s_lo`. The registered pair is `{s_lo, s_hi}`. **The graded step is the one with the
> higher clearance among those with `C ≥ 5`, i.e. `s_hi`, and it is NOT selected on agreement.**

**Why a ratio of at least 2.** A plateau read across two steps a factor 1.25 apart is satisfied by
construction and measures nothing. The fixed-reference item's step ratios were 3.33× (`twist`) and
3× (`patchV`) and produced plateau disagreements of 0.58–4.17% on the components that graded and
83.53% on the one that did not — the test discriminated. A ratio ≥ 2 preserves that.

**Why the twist ladder stops at 3e-1 and the `patchV` idx0 ladder at 1e0.** `twist` is in **degrees**
with design bounds `[-10, 10]`; `2e-1` is **1.0%** of the design range and `3e-1` is 1.5% —
geometrically tiny, and the A1 sweep's primal failures at 5e-2 and 1e-1 were on **FFD shape
coordinates in length units**, a different variable in different units
(`A_stepsize_study.md`; the fixed-reference item's §4.2 makes the same distinction). `patchV` idx0 is
the **freestream velocity magnitude**, `U0 = 295.0 m s⁻¹` (`base/runScript.py:24`, and
`runScript.py:193` sets `patchV = [U0, aoa0]`), so `3e-1 m s⁻¹` is **0.10%** of the base value —
smaller in relative terms than any twist step registered here. **The asymmetry is in the units, not
in the method.**

**Applying the rule now, with `η = 1.0910e-05` and the stored patched adjoint of
`P2-a6-n16/patched.log:4995-5021` — this is the arithmetic, done before the run:**

| DV, idx | stored adjoint `J_adj` | `C(3e-2)` | `C(5e-2)` | `C(1e-1)` | `C(2e-1)` | `C(3e-1)` | **registered `{s_lo, s_hi}`** | **graded step** | **C at graded step** |
|---|---|---|---|---|---|---|---|---|---|
| `twist` 1 | `-1.750730e-03` | **9.63** | 16.05 | 32.09 | 64.19 | 96.28 | **{3e-2, 1e-1}** | **1e-1** | **32.09** |
| `twist` 2 | `-1.469450e-03` | **8.08** | 13.47 | 26.94 | 53.88 | 80.81 | **{3e-2, 1e-1}** | **1e-1** | **26.94** |
| `twist` 4 | `-6.277000e-04` | 3.45 | **5.75** | 11.51 | 23.01 | 34.52 | **{5e-2, 1e-1}** | **1e-1** | **11.51** |
| `twist` 5 | `-3.797300e-04` | 2.09 | 3.48 | **6.96** | 13.92 | 20.88 | **{1e-1, 2e-1}** | **2e-1** | **13.92** |
| `patchV` 0 | `+7.334000e-04` | 4.03 | — | **13.44** | — | 40.33 | **{1e-1, 3e-1}** | **3e-1** | **40.33** |

**Every registered step on every component has predicted `C ≥ 5`**, which is the condition the brief
sets and which the rule produces rather than being fitted to. The predecessor's `1e-3` datum is
carried in for each component at **zero cost** as a third point, so every component's sweep has three
steps — what `DAFOAM_CHARTER.md` §3 requires — with the noise-dominated branch visible on all five
(clearances 0.07×–0.13× there).

**FD plan, in the registered priority order** (`fdplan_rem.json`, 10 entries, 20 perturbed primals):

```
patchV 0 @1e-1, patchV 0 @3e-1,
twist  1 @3e-2, twist  1 @1e-1,
twist  2 @3e-2, twist  2 @1e-1,
twist  4 @5e-2, twist  4 @1e-1,
twist  5 @1e-1, twist  5 @2e-1
```

**Priority, so a stop at the ceiling is principled and not arbitrary.** `patchV` idx0 runs first: it
is the only one of the five outside the `twist`→`DVGeo`→`warpDeriv` chain, and the fixed-reference
item's §9 singles it out (*"the most interesting of them"* — its FD read 4.26e-03 against an adjoint
of 7.334e-04, a **5.8× disagreement and not a sign flip**). The four `twist` components then follow
in **descending `|J|`**, i.e. descending predicted clearance, so a truncation at the ceiling drops
the components least likely to have graded anyway. **Components not reached are reported `PENDING`
by name with their price, never absorbed.**

### 4.3 The plateau tolerance — registered as a number, before any estimate exists

> **REGISTERED: two steps agree if `|d(s_hi) − d(s_lo)| / |d(s_hi)| ≤ 10%`.**

**Basis, and it is measured rather than chosen for convenience.** In the fixed-reference item's §6.8
the three components that graded had two-step disagreements of **0.58%, 4.17% and 0.78%**, and the
one that was flagged had **83.53%**. **10% sits 2.4× above the worst graded precedent and 8.4× below
the failure**, so it separates the two populations that exist without being tuned to either. It is
deliberately **looser** than the 5% PASS band, because the plateau test asks whether the estimate is
step-independent — that it is in the window between noise and truncation — and not whether it is
accurate; a component may sit on a clean plateau and still disagree with the adjoint, and that
outcome must be reportable as a disagreement rather than converted into a flag.

## 5. Predictions and falsifiers — bands, committed before any launch

**All five components are predicted to keep the sign of the stored adjoint** (`twist` 1/2/4/5
negative, `patchV` 0 positive). **None of the five was sign-flipped at 1e-3 either** — the flips in
the predecessor's table were idx 0, 3 and 6, all now resolved — so a flip appearing *here*, at a step
with 27–40× clearance where the noisy step did not produce one, would be a far stronger signal than
the flips L-233 explains, and is registered as a falsifier for that reason.

### P1 — `patchV` idx0, freestream velocity. **PREDICTED ≤ 5%, graded at `s = 3e-1`.**

> **Predicted:** graded, plateau ≤ 10%, sign **positive**, relative error `|J_adj − J_fd| / |J_fd|`
> in **[0%, 5%]** with a central expectation near **2%**.
> **Basis:** `C = 40.33` at the graded step, against the **49.13×** at which the sibling component
> `patchV` idx1 measured **0.940%** on the same arm class in the fixed-reference item. Same DV array,
> same absence of any mesh warp in the chain (`../rung_n16_np1/RESULTS.md` §6.4 proved `patchV` never
> touches `DVGeo`), same driver.
> **FALSIFIERS:** (a) > 5% ⇒ P1 REFUTED and `patchV` idx0 does **not** behave like idx1 despite
> sharing its chain — the most surprising outcome available to this item, and it would mean the
> velocity-magnitude derivative has a defect the AoA derivative does not. (b) Sign negative ⇒ a flip
> appearing at 40× clearance where 0.13× produced none ⇒ **the adjoint is wrong on this component**.
> (c) Plateau > 10% ⇒ FLAGGED, and the prediction of "graded" is a MISS.

### P2 — `twist` idx1. **PREDICTED ≤ 5%, graded at `s = 1e-1`.**

> **Predicted:** graded, plateau ≤ 10%, sign **negative**, relative error in **[0%, 5%]**, central
> **~2%**. **Basis:** `C = 32.09`, bracketed by the two `twist` components already measured on this
> exact arm class — idx0 at `C = 39.18` → **1.706%** and idx3 at `C = 18.20` → **1.817%** — and idx1
> lies between them in `|J|` (1.751e-03, against 2.101e-03 and 1.011e-03). It is the interpolation,
> not an extrapolation.
> **FALSIFIERS:** > 5%; a positive sign; plateau > 10% ⇒ FLAGGED.

### P3 — `twist` idx2. **PREDICTED ≤ 5%, graded at `s = 1e-1`.**

> **Predicted:** graded, plateau ≤ 10%, sign **negative**, relative error in **[0%, 5%]**, central
> **~2%**. **Basis:** `C = 26.94`, also inside the idx0/idx3 bracket. **FALSIFIERS:** as P2.

### P4 — `twist` idx4. **PREDICTED ≤ 8%, graded at `s = 1e-1`.**

> **Predicted:** graded, plateau ≤ 10%, sign **negative**, relative error in **[0%, 8%]**, central
> **~3%**. **Basis:** `C = 11.51` at the graded step is **below** both measured `twist` precedents
> (39.18 and 18.20) and its plateau partner sits at 5.75×, the lowest clearance any step in this item
> is graded or compared against. The band is widened from 5% to 8% for that reason, before the run.
> **FALSIFIERS:** > 8%; a positive sign; plateau > 10% ⇒ FLAGGED.

### P5 — `twist` idx5. **PREDICTED ≤ 15%, graded at `s = 2e-1`. The most exposed of the five.**

> **Predicted:** graded, plateau ≤ 10%, sign **negative**, relative error in **[0%, 15%]**, central
> **~5%**. **Basis, and the exposure is stated rather than hidden:** idx5 has the smallest `|J|` of
> the five (3.797e-04, only 2.8× above the flagged idx6's 1.362e-04), so the noise rule forces the
> largest step in the item, `2e-1`, and that step carries the most **truncation** error — a term the
> clearance rule does not measure at all. From the fixed-reference item's own numbers, moving `twist`
> idx0 from `3e-2` to `1e-1` changed its estimate by 4.17% and moved it **closer** to the adjoint, so
> truncation at `1e-1` is below ~2% there; scaling as `s²`, truncation at `2e-1` is of order 4× that.
> **The band is set at 15% — the CONDITIONAL/FAIL boundary — because a component that needs the
> largest registered step is the one most likely to be reported CONDITIONAL, and predicting ≤5% here
> would be predicting the convenient answer.**
> **FALSIFIERS:** > 15% ⇒ FAIL on this component regardless of the aggregate; a positive sign;
> plateau > 10% ⇒ FLAGGED. **A flag on idx5 is an expected-enough outcome that it is registered as
> the second-most-likely single-component result after "graded ≤ 5%".**

### P6 — the nine-component picture. **PREDICTED: 8 graded, 1 flagged, aggregate [0.8%, 3.0%].**

> **Predicted:** all five new components GRADE, giving **8 graded components** — the three stored
> (`patchV` 1 → 0.940%, `twist` 0 → 1.706%, `twist` 3 → 1.817%, values taken from
> `../rung_n16_fixed_reference/RESULTS.md` §6.8 and **not** re-bought) plus these five — with
> **`twist` idx6 flagged and excluded BY NAME** and **zero sign flips** anywhere in the nine.
> **The aggregate — named as the statistic it is, this lab's vector-relative error
> `‖J_an − J_fd‖ / ‖J_fd‖` over the graded components, and NEVER to be compared against the DAFoam
> papers' per-component average** (`DAFOAM_CHARTER.md` §2) — is predicted in **[0.8%, 3.0%]** with a
> central expectation of **1.3%**.
> **Basis, computed now:** the stored three give **1.0099%** exactly (verified by recomputation from
> the §6.8 values, so the arithmetic this item will use is the arithmetic that reproduced the
> published number). Because `patchV` idx1 at 9.017e-03 dominates the norm — the five new components
> have `|J|` between 3.8e-04 and 1.75e-03 — the aggregate is anchored near it. Adding all five at a
> uniform per-component error of 1% / 2% / 5% / 10% / 15% gives **1.010% / 1.108% / 1.639% / 2.816% /
> 4.091%**. **The registered band [0.8%, 3.0%] therefore corresponds to per-component errors of
> roughly 0–11%, which is the honest width of what is known.**
> **FALSIFIERS:** (a) aggregate > 5% ⇒ the rung leaves the PASS band and P6 is REFUTED; (b) any sign
> flip among the nine ⇒ **FAIL regardless of the aggregate** (`DAFOAM_CHARTER.md` §2); (c) more than
> **one** of the five flagged ⇒ the step-selection rule of §4.2 does not do what it was registered to
> do, and that is a finding about the rule, reported as one; (d) aggregate < 0.8% ⇒ the five new
> components agree *better* than the three already verified, which would be a pleasant surprise and
> is reported as a MISS, not quietly absorbed.

### P-η — the noise control. **PREDICTED: this arm's own baseline reproduces `η` within ±20%.**

> **Predicted:** the CD peak-to-peak over the last 200 iterations of **this arm's** baseline primal,
> at `printInterval 10` (20 samples), lies in **[8.7e-06, 1.31e-05]**, i.e. within ±20% of the
> registered `1.0910e-05`. **Basis:** the cold baseline primal is bit-reproducible on this case
> across items, images and days (N-D15), so the same window of the same trajectory must give the same
> number; the ±20% band exists only because this arm is a different container run and the assertion
> is worth making falsifiable.
> **REGISTERED CONSEQUENCE, so it cannot be chosen later.** `η` **stays 1.0910e-05** for every
> clearance and every verdict in this item whatever this control measures. If the control lands
> outside the band, the disagreement is reported, all clearances are **re-stated at both values**, and
> — registered now — **any component that clears `C ≥ 5` at the registered `η` but not at the
> measured one is FLAGGED, not graded.** That is the conservative branch, and it is the branch this
> family already took at `twist` idx6 (fixed-reference §8.3).

### P-RSS — peak memory. **PREDICTED ≤ 1.5 GiB. Ceiling 12 GiB (`--memory=12g`).**

> **Basis, measured:** every FD arm in the fixed-reference item peaked at **0.657–0.705 GiB**
> (`P3-a6-n16-ref/ledger.txt`), and the largest peak of any arm there was **1.252 GiB** — a
> 6,000-iteration primal. **This arm computes no adjoint**, so the primal envelope binds; the
> predecessor's 9.787 GiB is an **adjoint** figure and does not transfer
> (`DAFOAM_CHARTER.md` §7 requires this prediction before launch, and L-15 requires that a memory
> blocker not be named where none is binding).
> **FALSIFIER: any sample above 12 GiB** ⇒ over budget, the observation is recorded, the arm is
> **stopped**, and the item reports **stopped by memory**, which is `NOT A RESULT` about the
> derivatives and claims nothing about the envelope beyond the sample (`DAFOAM_CHARTER.md` §7:
> *"a stop is not a measurement"*).

### P-COST — **PREDICTED 36.8 core-min, registered 46.0 with contingency. Ceiling 60.0 HARD.** §7.

> **FALSIFIER: > 60.0 core-min.** The overrun **stops the run**; it does not get a new budget
> (`COMPUTE_BUDGET_CHARTER.md`; CLAUDE.md rule 12). **No self re-price.**

## 6. Grading, and the N=29 gate reading — both registered before the run

### 6.1 The grading rule

Per component, the reference is **central FD at the registered graded step of §4.2**, and the
component is **GRADED** iff `C ≥ 5` there **and** the two-step plateau of §4.3 holds; otherwise it is
**FLAGGED**, named, and excluded from every aggregate. No forward-AD reference is available on this
case (N-D16), so FD carries the reference alone and this file says so rather than omitting it
(`DAFOAM_CHARTER.md` §2).

Band, unchanged: **PASS ≤ 5% / CONDITIONAL 5–15% with a mandatory per-component breakdown / FAIL
> 15% or on any sign-flipped component regardless of the aggregate.** The aggregate is the
vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` over the graded components, named as such, with the
flagged components reported **beside** it and never instead of it.

### 6.2 The trivial baseline — **DECLINED BY NAME, with the citation, not omitted**

`DAFOAM_CHARTER.md` §4 fixes the trivial baseline for a DAFoam FD gate as **the same probe at a step
chosen to be wrong**, registered before its own run. **This item does not re-buy it, and names it:**

> **`patchV` idx1, central difference, `step = 1e-8`, patched image, same driver, same case.**
> **Already bought and reported** by the fixed-reference item (its §6.5, prediction **P9**, commit
> `66f42398`): `FD_DERIV dv=patchV idx=1 step=1e-08 deriv=152.94101058174746` against a stored
> adjoint of `9.01684e-03` — **99.9941%**, against a registered prediction of > 50%. **HIT.**

**Why it transfers, stated as a condition rather than as an assurance.** The baseline tests whether
**the harness can return a large number** — not whether a particular component can. The harness here
is the same one, and that is assertable rather than assumed: `gen_arm.py` md5
`ff85f67c304079349d378383ef46e67c` and `run_arm.sh` md5 `5e2d0724a2a2b07ad1c92bdc40b896dc` are taken
**unmodified** from the tree that produced that number, the staged `base/` is byte-identical (§2), the
image and its `IDWARP_SO_MD5` are the same, and the only thing that differs is which DV index the
plan perturbs. **If any of those md5s differs at launch the decline is void and the baseline is
re-bought** — registered now, so the escape is not available after the fact.
**Price not spent: 2 primals, ≈ 3.5 core-min, \$0.0030.**

### 6.3 THE N=29 GATE READING — registered before the measurement, and BOTH readings are stated

Sanaa's condition as held by this lane: **N=29 is approved ONLY if N=16 passes on the patched image.**
The phrase "passes" admits two readings and **this file fixes both now**, so that neither can be
selected after the numbers are seen:

* **READING 1 — the charter's text, and the one this lane holds.** `DAFOAM_CHARTER.md` §2 grades a
  table **PASS at ≤ 5% aggregate with ZERO FLAGGED COMPONENTS**. `twist` idx6 is flagged, and the
  fixed-reference item established that it is **structurally** FD-ungradeable on this rung — maximum
  clearance 2.42× at the largest defensible step, plateau disagreement 83.53%, and the only lever
  left is `η` itself, which is the unbought `useMeanStates` item on Sanaa's desk. **Under Reading 1
  the gate is `NOT MET`, and no arm this item could run would change that**, because this item does
  not touch idx6 and could not rescue it if it did.
* **READING 2 — subset-complete.** The gate is met when **every** component of the nine is either
  graded inside the band or **flagged by name with a measured reason**, with none left merely
  un-measured — the state the fixed-reference item's §9 gave as its reason for declaring the gate
  unmet (*"a gate that says 'N=16 passes' cannot be read as met while the majority of the graded row
  is untouched"*). Under Reading 2 the outcome **depends on this arm** and is unknown as this file is
  committed.

> **REGISTERED: `RESULTS.md` reports the gate under BOTH readings, states Reading 1 as the charter
> text, and does not choose between them — the gate is Sanaa's and its reading is hers.**
> **AND, under either reading: `N=29` is `NOT RUN`.** Nothing is staged, queued or costed for it by
> this item. A lane does not launch a rung because a gate it graded came out favourably; that is
> `CLAUDE.md` rule 9 (*approval of an item is approval of its cap, not a new ceiling*) and rule 7.

## 7. Cost — registered before the spend, ceiling 60 core-min HARD

**Basis, measured, from the fixed-reference item's own `s2btw` arm** (`P3-a6-n16-ref/ledger.txt`):
**1,365 s wall for 13 primals at np=1**, `--cpus=1`, under host `load average` ~20–24.

> **Per-primal figure: 1,365 / 13 = 105.0 s per primal, setup-inclusive.**

**Corroboration from the sibling arm, so the figure is not a single point:** `s2bpv` ran **738 s for
7 primals = 105.4 s per primal** on the same box in the same hour, on `patchV` perturbations (no mesh
warp) rather than `twist` (with warp). **The two agree to 0.4%**, so the warp is not a material term
at this mesh size and one figure serves both DV classes. This item's 21 primals are 16 `twist` and
4 `patchV` perturbations plus one baseline, so the mix is inside the measured envelope.

**Contention assumption, stated because it is billed.** The 105.0 s figure is **contention-inclusive
at load ~20–24**, which is the state the box was in when it was measured and the state it is in as
this file is written (`/proc/loadavg` 16.19, 17–18 runnable, T-family `buoyantSimpleFoam` at 12.0 GB
RSS, Lane A's `p3_a3_patched` up at `--cpus=4`). **It is not an idle-box figure and is not presented
as one.** N-D10 measures np=1 inflation at load ~20 as **1.104×** on an identical work marker, so an
idle box would give ≈ 95 s per primal and this item's estimate is ~10% conservative. **If load rises
above the basis — for instance if Lane A's A3 np=4 arm and the T-family are both saturating — the
per-primal figure rises with it, and the ceiling is what absorbs that: 60.0 / 36.8 = 1.63×
headroom over the measured basis.** Beyond 1.63× the run stops and the shortfall is reported.

| # | item | basis | wall (predicted) | core-min |
|---|---|---|---|---|
| 0 | pre-launch reading (`cat`, `md5sum`, `/proc`; **no container started**) | — | 0 s | **0.0** |
| 1 | **arm `rem`**, `fdsub`, 21 primals | 21 × 105.0 s | **2,205 s** | **36.8** |
| | **subtotal** | | | **36.8** |
| | contingency: one restage / one preflight-expired relaunch, +25% | | | **9.2** |
| | **REGISTERED TOTAL** | | | **46.0** |
| | **HARD CEILING** | | | **60.0** |

**Billing basis.** `ranks × wall` at np = 1, with `--cpus=1`, so the `ranks × wall` and
`cores × wall` readings **coincide** and there is no ambiguity to disclose (the fixed-reference
item's §2 records that its Amendment 1 produced this simplification; this item inherits `--cpus=1`
from the start rather than as a departure).

**\$ at \$0.0513/core-hour** (owner-stated, CLAUDE.md rule 12): registered **46.0 core-min = 0.767
core-h = \$0.0393**; predicted **36.8 core-min = \$0.0315**; ceiling **60.0 core-min = \$0.0513**.
All far below the \$25 line of `DAFOAM_CHARTER.md` §12, so no Sanaa listing is required **on cost
grounds**. **This item's compute has been approved by the chief and is costed here anyway, which is
the rule** (CLAUDE.md rule 12; rule 9 — a blanket approval is not a per-item reading).

**How the ceiling is enforced, mechanically.** At np = 1 with `--cpus=1`, **60 core-min is exactly
3,600 s of wall**, so the arm's `timeout` is set to **3600** and the timeout *is* the ceiling rather
than a backstop above it. **If it fires, the run stops, the FD entries already printed are graded and
the rest are reported `PENDING` by name with their price, and there is no re-price** — the priority
order of §4.2 exists so that what survives a truncation is the highest-value part.

## 8. Bounded execution — the gate is a separate command, and it is denominated in cores

* **Iteration caps are the bound, not a timer.** `endTime 1000` caps every one of the 21 primals; the
  arm terminates on its own. The `timeout 3600` is the budget ceiling (§7), not the mechanism.
* `--rm`, `--cpus=1`, `--memory=12g`, foreground, np=1, **`-x PYTHONPATH`**, `--name p3a6rem_rem`.
* **RSS monitoring is record-only. It never kills anything.** `docker stats --no-stream` samples to
  `rss_rem.txt`; the peak extractor reads field **`$3`**, not `$4` — `$4` is the literal `/` in
  `<ts> <arm> 0.705GiB / 12GiB` and reading it is why two ledger lines in the predecessor read
  `peak_rss=unmeasured`.
* **Cold start:** fresh `cp -a` of `base/`, then `rm -rf processor* dRdWColoring_*.bin`, then the
  continuity assertion and the `FD_BASELINE_CD` assertion of §2.
* One ledger line: `ARM IMG rc wall_s ranks core_min peak_rss`, plus the asserted `IDWARP_SO_MD5`,
  `transonicPCOption`, `primalMinResTolDiff`, `nProcs` and `Mesh region0 size` greps.

### 8.1 THE LAUNCH CONDITION — registered

> **The arm launches only when BOTH hold:**
> **(a) `MemAvailable` ≥ 12 GiB**, read from `/proc/meminfo`; **and**
> **(b) `free_cores` ≥ 1**, where **`free_cores` = 16 − (median of 5 samples of the runnable count)**
> and the runnable count is the numerator of field 4 of `/proc/loadavg`, sampled 1 s apart.
> **Polled every 60 s for at most 240 tries (4 hours).** The gate runs as **its own command** and the
> launch branches on its exit status — a gate that shares a line with the launch cannot gate (L-230).
> **If the window does not open in 4 hours the arm is NOT launched, the item records `BLOCKED` on
> host contention with the measured load, memory and the owner of them, and no cap is quietly
> raised.** Any departure is a dated Amendment in `RESULTS.md` with the measured numbers, or it does
> not happen.

**The memory floor stays at 12 GiB and this lane does not move it.** The fixed-reference item's §6.3
recommends a lower floor on measured grounds (its largest arm peaked at 1.252 GiB against a 12 GiB
floor calibrated on a 9.787 GiB *adjoint*), and a departure to 6 GiB was drafted there and **not
taken**. **That recommendation is Sanaa's to rule on and it is not taken here either.** This item
will very probably wait longer than it runs because of it, and that is the correct trade.

**Why the core half is denominated in cores.** L-230's second limb and L-232's corollary: *"gate on
the resource the container consumes — free cores ≥ ranks — not on `load1`, which never measured it."*
This arm consumes exactly **one** core (`--cpus=1`, np=1), so the gate asks for exactly one. The
median of five samples is used rather than a single read because the runnable count on this box
oscillates by ±1 between consecutive reads (measured while writing this file: 17, 18, 18, 17, 18).

### 8.2 THE QUEUEING RULE — Lane A's A3 arm has the older claim

**Lane A's A3 np=4 arm (`p3_a3_patched` / `p3_a3_control`) has the older claim on the box.** It is
running as this file is written (`docker ps`: `p3_a3_patched`, up 10 minutes, `--cpus=4`,
`--memory=12g`). **Registered rule:**

1. **This item never starts while `free_cores` < 1**, whether or not A3 is running. That is §8.1(b)
   and it is not overridable by this lane.
2. **A3 running is NOT by itself a reason to wait.** The team core cap is **8**; A3 holds **4**; this
   arm takes **1**; 4 + 1 = 5 ≤ 8. So at 1 core this item is inside the team cap alongside A3 and may
   run concurrently with it **provided §8.1 passes on its own terms**.
3. **This item does not stop, throttle, pause or `docker stop` any A3 container, for any reason.**
   If the two contend, the older claim wins and this item waits or reports `BLOCKED`.
4. **This item never raises its own rank count to reclaim time lost to contention.** L-232: a
   rank-count change is a re-pricing of the whole arm, not a re-slicing of it.

## 9. What this item will NOT be able to see — stated before it runs

1. **It is not N=29 and it is not 579,072 cells.** Nothing here re-opens the full-size `BLOCKED`
   verdict (`DAFOAM_CHARTER.md` §7: memory at 94.7–116 GiB against a 30 GiB box, **and** conditioning
   independently). It can only change the *input* to Sanaa's N=29 decision, never take it.
2. **`twist` idx6 is not touched and is not rescuable here.** This item adds no instrument that could
   grade it. It remains flagged on the fixed-reference item's measurement, by name.
3. **`shape` (~10² components) is still not graded**, by all three pre-registrations in this family,
   on cost. **A nine-component table is not the whole gradient and this file says so.**
4. **The adjoint column is INHERITED, not re-run.** Every verdict here is against the stored patched
   adjoint of `P2-a6-n16/patched.log:4995-5021`, printed by OpenMDAO at numpy's default **6
   significant figures**, which caps any agreement claim at about that precision. An error in that
   transcription would propagate; the source lines are cited so it is checkable, and §0 records that
   it was re-read from the raw log rather than from a table.
5. **No forward-AD or complex-step reference is available on this case** (N-D16), so FD carries the
   reference alone. `DAFOAM_CHARTER.md` §2's duty to reach for a non-FD reference was discharged, at
   cost, by the fixed-reference item; this item states that it did not reach again **because the
   reach was already made and its answer was NOT AVAILABLE**, not because it was not considered.
6. **`np = 1` only.** The decomposition axis is absent by construction (`DAFOAM_CHARTER.md` §5), and
   an FD reference is a property of a configuration including its rank count (N-D12, L-229).
7. **It cannot separate FD truncation from FD noise** at the two largest steps (`2e-1`, `3e-1`). Two
   steps plus the inherited `1e-3` give a three-point sweep with the noise branch visible; they do
   **not** give a truncation branch, so a component that plateaus across `{s_lo, s_hi}` is evidence
   of step-independence in that window and nothing about a window above it.
8. **It cannot say whether the primal's limit cycle biases the derivative**, only how much it scatters
   it. `η` measures scatter. A systematic offset common to every FD step would be invisible to every
   instrument in this item, and the only thing that would have caught it — forward AD — does not run
   (N-D16).
9. **The step-selection rule of §4.2 is registered, not validated.** This item is its first use. If
   more than one component is flagged, that is a finding about the rule as much as about the case.

## 10. Verdict vocabulary

`PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING` — the six tokens, adopted
for DAFoam by `DAFOAM_CHARTER.md` §8 from `CLOSURE_MODELLING_CHARTER.md` §12. No other word grades an
arm here. A verdict is valid only against a falsifier written in this file before the run.
An arm that never launches on the §8.1 condition is `BLOCKED`, never `GATE FAIL`. A component not
reached at the ceiling is `PENDING`, never absorbed. A component that is flagged is `NOT A RESULT`
for that component and is named. **A stop is not a measurement** (`DAFOAM_CHARTER.md` §7).

**This is a PATCHED-image row and it says so. It does not replace, merge with, or re-grade the
shipped-toolchain row at `../rung_n16_np1/RESULTS.md` §6.2.**

**Nothing is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**
