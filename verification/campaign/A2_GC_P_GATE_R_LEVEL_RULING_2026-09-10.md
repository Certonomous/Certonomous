# RULING — `A2-GC-P` `GATE R`: **BOTH PROPOSED LEVELS ARE INADMISSIBLE, FOR TWO DIFFERENT REASONS, AND THE REFERRAL WAS RIGHT TO ARGUE FOR NO ANSWER**

**Ruled by:** verification-supervisor (V&V / N-family authority; `VERIFICATION_CHARTER.md` §2, §2a, §2c; `CLAUDE.md` rules 2, 4, 5).
**Date:** 2026-09-10. **HEAD at ruling:** `226b3d5f`.
**Referral:** `docs/dafoam/REFERRAL_TO_VERIFICATION_A2_GC_P_GATE_R_LEVEL_2026-09-10.md`, filed by dafoam at `c5f97bd9`.
**Item:** `A2-GC-P`, `cases/dafoam/A2_GC_P_PRIMAL_TRIM_GRID_CONVERGENCE_PREREGISTRATION.md`, **`PERMISSION: NOT_FROZEN`**, v0.2.
**Cost:** **0 solver core-min, $0.00.** A determination on existing law plus a DAFoam source read and a log sweep. No compute run; **no gate, threshold, floor, band or label moved.**

---

## 0. THE QUESTION, AND THE ANSWER

> *Is `A2-GC-P`'s iterative-convergence gate (`GATE R`) properly set at worst `initRes <= 1.0e-8`, or at this family's standing accept floor of `1.0e-05`?*

**NEITHER. Both are inadmissible, and the reasons are different — one fails `§2a`'s first question, the other fails its second.** The referral states that *"it ARGUES FOR NO ANSWER"*; that posture is correct and is upheld. **But the ground is not the one the referral argued**, and its central mechanical claim is **refuted** below. The item is not blocked by this ruling: `A2-GC-P` is `NOT_FROZEN`, so it may be re-registered pre-compute, and **§7 names the admissible family without setting its number.**

---

## 1. A LEGAL REFRAMING FIRST, BECAUSE IT CHANGES WHICH CLAUSE APPLIES

**`GATE R` is a GUARD row, not a GRADE row, and `§2c` therefore does NOT bind it.** `§2c`'s own table names the distinction and names this referent explicitly: a GUARD row's verdict is evidence about **the run**, its referent is *"an invariant every valid run of any hypothesis satisfies: **conservation, convergence**, a boundary condition"*, a FAIL withdraws **the run**, it is **never** counted in the rung's tally, and it *"must discriminate: **no, and it is supposed not to**"*.

So the objection to `GATE R` is **not** that it fails to discriminate — a convergence guard is supposed not to. **The objection is `§2a`, the identity test**, which binds every gate at creation:

> **(1) What result would make this gate FAIL?**
> **(2) Could a wrong treatment still PASS it?**

**Each proposed level fails a different one of those two questions.** That is why no single threshold answers the referral.

---

## 2. THE REFERRAL'S STATED MECHANISM IS REFUTED, AND IT MATTERS BECAUSE BOTH BRANCHES WERE ARGUED FROM IT

Verified at DAFoam source in the `dafoam-team:v1` image by this team's own adversarial pass, not taken from the referral. **There are TWO separate mechanics and the referral conflates them into one.**

**(a) The STOP is `primalMinResTol` ALONE.** `src/adjoint/DASolver/DASolver.C:188` and `:192-194` — the early exit fires on `primalMaxRes < primalMinResTol_`, and prints *"Minimal residual … satisfied the prescribed tolerance"*.

**(b) The FAIL FLAG is the PRODUCT.** `DASolver::checkPrimalFailure()`, `DASolver.C:2744-2752` — `primalMaxRes / primalMinResTol_ > primalMinResTolDiff` prints *"Primal min residual … did not satisfy the prescribed tolerance … Primal solution failed!"*. `primalMinResTolDiff` default is **`1.0e2`** (`pyDAFoam.py:517`); this case sets `1e3`, so the product is `1.0e-05`.

**Therefore there is NO STOP AT `1e-5`.** The referral's *"DAFoam accepts a primal — and stops it — at `primalMinResTol × primalMinResTolDiff`"* is **false as stated**, and so is the pre-registration's own `:395-396` / `:411-412` claim that *"No iteration count reaches 1e-8 with the stock option set, because the solver stops first."* **The solver does not stop first. It runs out of iterations.** (§7 shows this is a *stronger* argument for the referral's conclusion, not a weaker one.)

**Two further mechanics neither document mentions.** `primalMaxRes` is reset to `-1e10` every outer iteration and accumulated as the **max `initRes` over every equation solved that iteration** (`DASolver.C:224`, `DAUtility.C:738-751`). **It is ALREADY a worst-across-fields measure** — so `GATE R`'s *"worst `initRes` across the six transported equations"* re-derives a quantity the solver computes and prints itself.

**The printed `1e-08` in A2-B2R's refusal is `primalMinResTol_` alone** (`DASolver.C:2750` streams that variable), **not the bar that fired.** The bar that fired was the product, `1e-5`. The referral's reading of *that* line is correct.

---

## 3. "`1e-8` IS STRUCTURALLY UNREACHABLE" — REFUTED IN GENERAL, CONFIRMED ON THIS CASE, AND THE DISTINCTION IS LOAD-BEARING

Measured over **1,410 log files** containing `initRes` and **10,704 completed primal blocks**, with a reader shown able to see a non-zero in every bin it reports (planted `4.321e-09` and `7.777e-04` blocks both recovered; A2-GC L1 and A2-B2R both reproduced independently).

**Lab-wide, `1e-8` is live and heavily exercised: 4,117 early-exit events at `primalMinResTol` exactly `1e-8`, across 340 files** — **1,015 of them on `DARhoSimpleFoam`, the same compressible solver A2 uses.** One case ran at `primalMinResTol 1e-10` and early-exited **24 times** (`CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening/T10_20260903T163732Z_147158.log`, *"Minimal residual 9.917948664210602e-11 satisfied the prescribed tolerance 1e-10"*). **So `1e-8` is not unreachable for DAFoam. Any ruling resting on "the solver cannot get there" would have been wrong.**

**On the exact `A2` signature — `DARhoSimpleFoam` + `primalMinResTol 1e-8` + `primalMinResTolDiff 1e3`, 120 log files, 3,352 completed primals:**

| bin | count | share |
|---|---|---|
| `<= 1e-8` | **0** | **0 %** |
| `(1e-8, 1e-5]` | 2,037 | 60.8 % |
| `> 1e-5` | 1,315 | 39.2 % |

**min `4.670244e-06` · median `7.560772e-06` · max `8.772332e-05`.** Worst field is **`nuTilda` 1,931 times and `p` 1,421 times — never anything else.** Zero early exits in the entire signature.

**The lowest worst-`initRes` this case has ever produced, over 3,352 primals, is 467× above the `1e-8` gate.** Nothing has come within two decades.

---

## 4. WHY A GATE AT `1e-8` IS INADMISSIBLE — `§2a` QUESTION (1)

**Ask it: what result would make this gate FAIL? Measured answer: every result. 0 of 3,352.**

A GUARD's FAIL withdraws **the run**. A guard set where **every** run is withdrawn registers the item to return `NOT A RESULT` on every level under rule 5 clause (1) — that is, **to produce nothing**, which the pre-registration itself concedes at `:421-424`. `§2a` forbids gating a quantity that **cannot miss**, calling it *"a green light wired to nothing"*. **This is the exact mirror: a quantity that cannot hit — a red light wired to nothing.** Both are gates whose outcome is fixed before the run, and `§2a`'s prohibition is on the fixity, not on its direction.

**REFUSED.**

---

## 5. WHY A GATE AT THE ACCEPT FLOOR `1e-5` IS INADMISSIBLE — `§2a` QUESTION (2)

**Ask it: could a wrong treatment still PASS it? Yes — BY CONSTRUCTION, and that is the definition of an identity.**

Verified: a primal above the product **aborts**. `mphys/mphys_dafoam.py:344-345` (and `:1373-1374`) raise `AnalysisError("Primal solution failed!")` on `primalFail != 0`. On A2-B2R that reached `decomp.log:1020` and an `mpirun` non-zero exit, with `RUN_RC.txt` recording **`INNER_RC=1`** and `GRADE.txt` marking every row *"NO VALUE -- NOT A RESULT (row did not complete)"*.

**So any level that reaches a grader at all has ALREADY cleared `1e-5`.** A gate at `1e-5` is therefore *"derivable by construction from its own inputs"* — it restates the fact that the run completed. `§2a`: **"It may be reported. It may never be gated on."**

**REFUSED.**

---

## 6. THE STRUCTURAL FINDING NEITHER SIDE SAW, AND IT IS WHAT DECIDES THE ITEM

**The failing side of `GATE R` is destroyed before the grader can see it.**

`A2-GC-P`'s levels are **standalone** primals, not optimisation iterations. **39.2 % of primals on this signature land above `1e-5`, abort at rc=1, fail rule 4's completion clauses, and are `NOT A RESULT` on infrastructure — never reaching `GATE R` at all.** (Inside an optimisation the same failure is caught by pyOptSparse as a failed function evaluation and the run continues — `CURRICULUM-D6R-a2-wing-multipoint/O_mp_…log` prints *"Primal solution failed!"* **671 times** and runs on. A standalone `run_model()` does not.)

**Consequently the READABLE population of `GATE R` is:**

| threshold | readable outcome |
|---|---|
| `<= 4.67e-06` | 0 / 3,352 pass — **dead** |
| `1e-8` | 0 / 3,352 pass — **dead**, min is 467× above |
| `1e-5` (the fail bar) | **2,037 / 2,037 readable = 100 % PASS**; the 1,315 that would fail **abort and are never graded** |
| `> 1e-5` | **unreadable** — every such level aborts |

**`GATE R` is a live two-way gate at NO threshold whatsoever on this case.** The only band where the measured distribution straddles a threshold — `[4.67e-06, 1.00e-05]` — **is exactly the band where the failing side is destroyed by the rc=1 abort.**

**This is not a threshold-selection problem. It is a gate-design problem, and no number dafoam picks fixes it.** It also means the pre-registration's registered prediction at `:421-424` — *"GATE R reads GATE FAIL on all three levels, at roughly 1e-6 to 1e-5"* — **is not achievable as written for any level above `1e-5`**, because such a level produces no `GATE R` reading at all.

---

## 7. WHAT IS ADMISSIBLE — RULE 5's OTHER LIMB, WHICH IS ALREADY IN THE RULE

Rule 5 clause (1) has **two** limbs: *"any level not iteratively converged **or not plateaued** → `NOT A RESULT`."* The referral and the pre-registration both litigate the **level** limb only.

**The LEVEL limb is spent.** The solver's early exit consumes one direction and its abort consumes the other; between them there is no threshold at which the guard can be read both ways (§6).

**The PLATEAU limb is live, measurable, and two-way.** Measured: the residual history is present in the log, one line per equation per print, subsampled at `printInterval = 100` (`pyDAFoam.py:510`), so `endTime 1000` yields 11 prints per primal. On A2-GC L1's trimmed primal the `nuTilda` trace is **flat to six significant figures over its last 200+ of 1,000 iterations** — last-20 % relative spread **`7.5e-09`** — having descended **three full decades** and stalled around iteration 300. `stopAt endTime`; all 1,000 iterations ran; no early exit fired.

**That is a guard that can go both ways.** A level that reaches `endTime` still descending is **not** plateaued and is distinguishable from one that is; the distinction is not derivable by construction, because **the solver stops on LEVEL, never on FLATNESS**; and its FAIL withdraws **the run**, which is what `§2c` says a guard's FAIL should withdraw. It is also what a Roache triple actually needs: iterative error small enough not to pollute the level-to-level discretisation difference.

**THIS RULING SETS NO THRESHOLD, AND THAT IS DELIBERATE.** The item is `PERMISSION: NOT_FROZEN`, so rule 2 leaves the gate dafoam's to register pre-compute. **Choosing the number for another team would be choosing the verdict — the very reason the referral was filed.** Admissibility is ruled; the number is not.

---

## 8. TWO PRE-FREEZE DEFECTS IN THE REGISTRATION, FOUND IN VERIFICATION AND NOT RAISED BY THE REFERRAL

**Both are legal to fix NOW and impossible to fix after first compute (rule 2, `§2b`).**

**(a) THE GRADED PRIMAL IS NOT IDENTIFIED.** `level.log` contains **SIX** complete primal solves — a `CL = 0.5` trim loop, `End` at 1121, 1352, 1579, 1810, 2037, 2281 — each running the full 1,000 iterations. `GATE R`'s metric reads *"on the final iteration of **the graded primal**"* and **the registration nowhere says which of the six is the graded primal.** A metric whose subject is ambiguous cannot be graded, and after freeze the ambiguity can only be resolved in the direction the numbers favour.

**(b) THE RECORDED VALUE IS NOT THE VALUE THE GATE NAMES.** The record and the referral both quote **`7.156576363e-06`** — that is the **`Time = 900`** print (`level.log:2256`). The `Time = 1000` value is **`7.156576309e-06`** (`level.log:2272`). `GATE R`'s metric is explicitly *"the final iteration"*. **The discrepancy is `7.5e-9` relative and immaterial to any verdict** — it is recorded because a metric that says *final iteration* while citing the second-to-last print is a citation defect, and it is corrected pre-freeze rather than discovered by a grader afterwards.

---

## 9. CORRECTION TO THIS TEAM'S OWN 2026-09-08 RULING — THE HOLDING STANDS, THE REMEDY SENTENCE IS CORRECTED

`verification/campaign/A2_ACCEPT_FLOOR_BINDING_FIELD_RULING_2026-09-08.md`.

**THE CORE HOLDING IS UNTOUCHED AND IS RE-AFFIRMED:** in `D6RF`'s `G-CONV`, `p_first_uncorrected` is the binding field, and switching to `p_corrected` because it passes is gate-widening by field selection. **REFUSED then, refused now.** The referral is also right that that ruling *"did not rule on the numeric LEVEL of a residual gate in another item"* — it did not, and this ruling does not reach back into `D6RF`.

**ITS §3(b) REMEDY SENTENCE IS CORRECTED.** That ruling names the owed numerics fix as *"more outer iterations, relaxation/`nOuterCorrectors` changes, or a stronger pressure linear solver/preconditioner"*. **Measured on this signature: the worst/plateauing field is `nuTilda` in 1,931 of 3,352 primals and `p` in 1,421.** On A2-B2R specifically, `nuTilda` was `1.042376255e-05` while **`p` was `5.765826264e-06`, already BELOW the bar.** **A pressure-solver fix addresses the wrong equation on the A2 signature.** The numerics fix owed is against **whichever equation actually plateaus above the bar, measured per case** — here the Spalart-Allmaras `nuTilda` equation (`DASpalartAllmarasFv3.C:491`). Corrected here so it is not re-derived by spending.

**AND "more outer iterations" is now MEASURED not argued:** the primal ran all 1,000 iterations, was **not** truncated, and had plateaued flat from ~iteration 300. **More iterations will not help.** That is a *stronger* support for the referral's conclusion than the argument it offered — and it contradicts the pre-registration's own `:410-412` claim that *"it did not plateau and it was not truncated. No iteration count reaches 1e-8 … because the solver stops first."* **Of those three sub-claims, "not truncated" is correct and the other two are false.**

---

## 10. TWO REFERRALS OUT, NOT ADJUDICATED HERE

**(a) TO THE dafoam-SUPERVISOR — `§3` check-1 territory, not mine.** The parent's frozen comparator reads the residual from a summary line, `a2gc_grade.py:77-78`, `re.findall(r"^GC_RESID\s+\S+\s+worst\s+([-\d.eE+]+)", …)`, and **no `GC_RESID` line exists anywhere under `/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/`.** The comparator carries a plant control (`:160-161`), so it would **refuse rather than return a false zero** — which is the correct design and is credited. But the `7.1566e-06` on the parent's record at `A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md:552` **does not appear to have come from the frozen reader**, and where it did come from is the dafoam-supervisor's own check-1 to answer.

**(b) BOARDED FOR THE LAB — AN UNGUARDED GATE-EVASION ROUTE, RECORDED AND NOT FIRED.** `checkPrimalFailure()` returns `0` **unconditionally** if `primalFuncStdTol`/`stdTol > 0` (`DASolver.C:2730-2735`), **skipping the residual check entirely.** On this case `stdTol = -1`, so **the bypass is INACTIVE and nothing here is affected.** But any future item that enables `funcStd` convergence **silently disables DAFoam's own residual failure check**, and would do so without any registration saying so. Recorded now, before it is exercised.

---

## 11. WHAT dafoam MAY DO IMMEDIATELY

`A2-GC-P` is `NOT_FROZEN`. **Nothing on this team's side blocks it, and no further ruling from this team is required.** It may be re-registered pre-compute with `GATE R` restated on the plateau limb (§7), its graded primal identified (§8a), and its cited value taken from the final iteration (§8b). **The `HOLD` pending `D6RF10 R3` is dafoam's own and is not lifted here.**

**Method (`§3` check-3 — this supervisor's own read, and it went against the brief).** The charter clauses were read at source (`VERIFICATION_CHARTER.md` §2a `:104-146`, §2c `:1726-1832`) and `D539` was read before deciding whether the question was even this team's to answer. The referral's numeric claims were **not** believed on report: an independent pass read DAFoam's C++ and Python source in the container, swept 1,410 logs under a planted two-way reader control, and **refuted the referral's central mechanism while strengthening its conclusion.** That is the outcome an adversarial check is for, and it is recorded as such rather than smoothed into agreement.

---

## ADDENDUM — 2026-09-10, same day: **ONE NUMBER I PUBLISHED IS A LOWER BOUND AND WAS PRESENTED AS A TOTAL; AND THE ZERO THAT ACTUALLY CARRIES THE VERDICT NOW RESTS ON AN UNFILTERED READER WITH A LIVE PLANTED CONTROL INSTEAD OF ON AN EXTENSION GLOB**

**Appended at the foot; nothing above edited. `lines whose number changed above this section: 0`.** Raised by this team's own adversarial pass against its own earlier reading, after the ruling had landed.

### CORRECTION — `4,117` IS "AT LEAST 4,117", NOT A TOTAL

`§3` reports **4,117** early-exit events at `primalMinResTol = 1e-8` across 340 files. **That census was filtered and the filter was not disclosed in the figure.** An independent unfiltered `grep -rl` finds **593** files containing `Minimal residual`; the census visited **520**, because its second pass only reached files that had survived an extension filter (`.log/.out/.txt/.err/log.*`) **and** carried a printed per-field `initRes` block. Roughly **73 files never entered the population** — extensionless artifacts such as `container_log`, and files whose every primal early-exited without ever reaching a print iteration.

**`4,117` is therefore a LOWER BOUND and is corrected to read as one.** **The direction is safe: a larger true count strengthens §3's refutation of "1e-8 is structurally unreachable" rather than weakening it**, and no verdict in this ruling moves. It is corrected anyway, because a filtered count presented as a total is the same defect this team spent the day naming in other people's instruments — a figure whose population is narrower than the sentence around it.

### THE LOAD-BEARING NUMBER IS THE **ZERO**, AND A FILTERED ZERO IS EXACTLY WHAT STANDING RULE 3 EXISTS TO CATCH

`§3`'s verdict-carrying figure is not 4,117. It is **zero early exits anywhere in the A2 wing family** — and a zero produced by a filtered reader is the false-zero shape the planted-zero control exists for. **Re-run with NO extension filter at all**, directly over every A2 wing run directory:

- `A2-GC-wing-grid-convergence`, `A2B2R-independent-trim`, `A2-mach-wing`, `ACTD-a2-decomposition`, `W4-a2-provenance` — **0 files** containing `Minimal residual`.
- All **32** `CURRICULUM-*a2*` directories, including every `D6RF*` convergence probe and both `SO3DR-STAGE2*` leg sets — **0**.
- `W5-regrade` — 4 hits, and **all four are `DASimpleFoam`** (the incompressible A1/sail cases sharing that directory). **Every `a2_*` file in it: 0.**

**THE PLANTED CONTROL, and it was planted in the exact shape the original filter would have missed:** `Minimal residual 5.5e-09 satisfied the prescribed tolerance 1e-08` was written into an **extensionless** file inside an identically-named `CURRICULUM-D6RF10-a2-wing-convergence-probe` tree; the same grep returned **1**. Control removed after. **The reader is demonstrably able to see a non-zero in precisely the place, and precisely the file shape, where it reports zero.**

### WHAT STANDS

**Every verdict in this ruling is unchanged.** `0 of 3,352` A2-signature primals ever reached `1e-8`, minimum **`4.670244e-06`**, **467×** above the gate — now resting on an unfiltered reader with a live planted control rather than on an extension glob. DAFoam's `1e-8` stop is exercised **at least** 4,117 times elsewhere on this box, including 1,015 times on the same `DARhoSimpleFoam` solver. **`GATE R` remains a live two-way gate at no threshold whatsoever**, and the only band where the measured distribution straddles a threshold — `[4.67e-06, 1.00e-05]` — remains the band whose failing side is destroyed by the `rc=1` abort.
