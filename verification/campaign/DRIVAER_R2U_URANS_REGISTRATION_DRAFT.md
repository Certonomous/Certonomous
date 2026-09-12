# DRIVAER R2u — TRANSIENT (URANS) ARM. **DRAFT. NOT FROZEN. NOT LAUNCHED. HELD.**

> **STATUS: DRAFT / UNFROZEN. NO COMPUTE HAS RUN UNDER THIS DOCUMENT. NOT A GATE.**
> Drafted by a cfd `lab-lane` 2026-09-12 at the cfd-supervisor's direction. **HELD UNLAUNCHED
> PENDING THE MESH ROUTE** (§0). Until a freeze commit exists every gate, threshold, cap and
> label below is amendable and carries **no evidentiary weight** (`CLAUDE.md` rule 2). The
> supervisor's check 4 and check 1 have **not** been done. **This banner is struck whole at the
> freeze, if there is one.**

---

## 0. 🔴 **WHAT THIS ARM CANNOT DELIVER. READ THIS BEFORE ANYTHING ELSE IN THE DOCUMENT.**

**THIS IS NOT THE FIX FOR DRIVAER, AND A LATER READER MUST NOT BE ABLE TO MISTAKE IT FOR ONE.**

DrivAer's `Cd` is blocked on **two independent things**
(`DRIVAER_R2C_B2_RESULTS_2026-09-12.md` §9.5):

| # | blocker | does THIS arm touch it? |
|---|---|---|
| 1 | **Mixed wall treatment (Y1).** 16.3 % of boundary faces carry no usable layer — `Rimsfront` and `Rimsrear` at **0.000** mesh layers, `Tiresrear` 0.027, `Tiresfront` 0.107. Layered-group y⁺ area-weighted median **481.565** against unlayered **1940.998**. | **NO. NOT AT ALL.** |
| 2 | **Unconverged solution** — a coherent limit cycle a steady solver cannot converge. | **Plausibly. That is the whole point of this arm, and it is untested.** |

**BLOCKER 1 IS A MESH PROBLEM AND IT TAKES A MESH FIX.** It is not touched by running unsteady, it
is not touched by running longer, and **B2 has now established it is not rescuable by a blended
wall treatment either** — that was precisely the hypothesis B2 tested, and B2 read `INACTIVE` for
the measured reason that the entire body sits above the y⁺ ≈ 30 crossover where the two wall
functions coincide (layered minimum y⁺ **34.235**, unlayered minimum **56.062**).

> **A PERFECTLY CONVERGED, PROPERLY TIME-AVERAGED UNSTEADY `Cd` PRODUCED BY THIS ARM IS STILL
> `NOT A RESULT` AS A DRIVAER DRAG COEFFICIENT, ON THE Y1 CAP ALONE.** Nothing in §§1–8 changes
> that, and no figure from this arm may be captioned as a validated DrivAer drag.

**Every gate below is therefore a gate on UNSTEADINESS, not on drag accuracy.**

---

## 1. WHAT IT **CAN** DELIVER, STATED JUST AS PLAINLY

1. **A measured physical shedding period and Strouhal number** — which the lab **does not have**
   and **cannot get from the steady runs**. §2.3 is decisive that the flow is unsteady, but its
   period is measured in **ITERATION space** (33 and 30 iterations), and **a steady solver's
   iteration index is not physical time**. It evidences unsteadiness; it yields **no frequency,
   no Strouhal number and no physical period**. Only a transient run does.
2. **A time-averaged `Cd` over an integer number of shedding periods** — the statistic a
   massively separated bluff-body wake actually has, as against the instantaneous endpoint
   sample the steady arms were forced to report.
3. **A genuine 3-D unsteady result, showable**, with an honest caption: *the shedding is measured;
   the drag magnitude is not validated on this mesh.*
4. **A test of the local-equilibrium caveat** left undischarged by B2
   (`DRIVAER_R2C_B2_INTERPRETATION_ADDENDUM.md`): a separated rear end can decouple the two wall
   functions regardless of y⁺, and a time-resolved run is where that would show.

**THE JUDGEMENT CALL THIS DOCUMENT EXISTS TO MAKE DECIDABLE, NOT TO MAKE:** is a measured shedding
period plus an honestly-capped unsteady `Cd` worth ~70–180 core-min while blocker 1 stands? **The
lane's view is that §1.1 alone is worth it and that §0 must be on every figure. The decision is
the cfd-supervisor's, and this arm stays HELD until it is taken.**

---

## 2. THE EVIDENCE THAT MOTIVATES IT — ALREADY MEASURED, FROM RUNS ALREADY ON DISK

All from `DRIVAER_R2C_B2_RESULTS_2026-09-12.md` §9 (commit `d2185c333`), on the completed
`r2_coarse_R2` and `r2c_coarse_blended_R2`:

**2.1 The excursion does not decay.** Trailing-200 excursion at eight stopping points 600→2000:
power-law fit **control `N^(−0.069)`, blended `N^(+0.000)`**.

**2.2 The amplitude is stationary.** Mean-removed rms over four consecutive 250-iteration blocks:
control 1.811 / 1.802 / 1.767 / 1.773e-03; blended 1.986 / 2.001 / 1.945 / 2.011e-03. **Constant
to ~2 % over a thousand iterations. A transient shrinks; this does not.**

**2.3 It is a coherent periodic oscillation.** Autocorrelation of mean-removed `Cd`:

| | control | blended |
|---|---|---|
| fundamental period | **33 iterations** | **30 iterations** |
| r(T) | +0.959 | +0.936 |
| r(T/2) | −0.845 | −0.940 |
| r(2T) | +0.970 | +0.965 |

**Sanaa's run instruction item 12 routes this case by name:** *"coherent oscillation in the graded
quantity → mark 'physics voting unsteady' > unsteady"*. **This registration is that route taken.**

---

## 3. THE ONE CHANGE — STEADY TO TRANSIENT, ON THE **SAME MESH**, NOTHING ELSE MOVED

`simpleFoam` → **`pimpleFoam`**, `constant/polyMesh` **symlinked to the identical files** the
steady arms read. Turbulence model, schemes (convected to their transient forms), BCs, decomposition,
reference constants (`magUInf` 38.889, `lRef` 2.79, `Aref` 2.298, `rhoInf` 1 — **asserted from the
case's own `system/forceCoeffs`, not recalled**) and the 47-patch forceCoeffs list: **unchanged**.

**Initialised from the steady solution at `t = 2000`**, not from uniform flow — the limit cycle is
already established there and the transient-discard window (§5) is shorter for it. **This is a
legitimate initialisation, not a restart**: it is a different solver and a different registration,
and its own `endTime` and completion clauses are judged wholly within this document.

---

## 4. TIME STEP — **DERIVED, AND ITS WEAKEST LINK NAMED**

| quantity | value | basis |
|---|---|---|
| `magUInf` | 38.889 m/s | case `system/forceCoeffs` |
| `Aref` | 2.298 m² | same |
| area-equivalent height `√Aref` | 1.5159 m | derived |
| convective time `lRef/U` | 0.071743 s | derived |
| **assumed St** (on `√Aref`) | **0.25** | **ASSUMED, NOT MEASURED — §8** |
| predicted `f` | 6.413 Hz | derived |
| **predicted `T_shed`** | **0.15592 s** | derived |
| steps per period | 40 | chosen |
| **`deltaT`** | **3.8981e-03 s** | derived |

**THE STROUHAL NUMBER IS AN ASSUMPTION AND IT IS THE WEAKEST LINK IN THIS DOCUMENT.** St 0.20–0.30
spans `T_shed` 0.19490–0.12994 s, i.e. **±25 %** on the time step. The assumption is **safe in the
direction that matters**: the run *measures* the true period (§1.1), and `deltaT` chosen for St 0.25
still gives **31 steps/period at St 0.20 and 47 at St 0.30** — inside any reasonable resolution
band across the whole assumed range. **If the measured period falls outside 0.13–0.195 s, `deltaT`
is wrong and the run is `NOT A RESULT`; that is registered here, before it runs, as G-U3.**

**Courant number is NOT registered as a threshold because it has not been measured** and a
`maxCo` guess would be a number pretending to be evidence. `pimpleFoam` is implicit; the run writes
Courant per step and it is **reported**, not gated. A first short probe would fix it — see §8.

---

## 5. AVERAGING WINDOW — AN **INTEGER** NUMBER OF PERIODS, DECIDED BEFORE THE RUN

| stage | periods | seconds | steps |
|---|---:|---:|---:|
| transient discard | 10 | 1.5592 | 400 |
| **averaging** | **20** | **3.1184** | **800** |
| **`endTime`** | **30** | **4.6777** | **1200** |

**The average is taken over a whole number of periods** — a partial period biases the mean by the
waveform, which is exactly the error a time-average is supposed to remove. **The window is
re-stated in terms of the MEASURED period once it is known, and if the measured period changes the
integer count, the averaging window is re-derived and the run re-run — never re-cut after the fact
to a window that flatters the answer.** That clause is the whole reason the window is registered
now.

`fieldAverage` accumulators are checkpointed with the fields (**Sanaa item 3**, verbatim: *"Every
transient writes fields at an interval that gives at most 30 minutes of loss; time-averaging
accumulators are checkpointed with the fields"*).

---

## 6. GATES — **ALL ON UNSTEADINESS. NONE ON DRAG ACCURACY (§0).**

| gate | statement | failure |
|---|---|---|
| **G-U1** | `Cd(t)` autocorrelation shows a coherent period: `r(T) ≥ 0.8` **and** `r(T/2) ≤ −0.5`, the same structure §2.3 measured in iteration space | not coherent → the steady-run finding is **not reproduced in time** and that is itself a finding, reported, not hidden |
| **G-U2** | the **time-averaged** `Cd` over the registered integer window is stable to `≤ 0.005` relative between the **first and second halves** of the averaging window — the same 0.005 the steady plateau limb uses, **carried unchanged, not relaxed** | → `NOT A RESULT` |
| **G-U3** | the **measured** `T_shed` lies inside **0.13–0.195 s** (the St 0.20–0.30 span §4 assumed) | outside → `deltaT` was wrong → `NOT A RESULT`, re-derive and re-run |
| **G-U4** | rule 4 completion: `rc=0`, `End`, last time == `endTime`, fields present, step count == `round(endTime/deltaT)`, **age guard** | any clause → `NOT A RESULT` |
| **REPORTED, NOT GATED** | Courant per step; measured St; per-patch y⁺ from the saved fields; `Cl(t)` | — |

🔴 **NO GATE HERE PRODUCES A CITABLE `Cd`. §0 IS NOT SUSPENDED BY A `PASS` ON ANY OF G-U1…G-U4.**

---

## 7. COST — IN CORE-MINUTES, BEFORE IT RUNS (rule 12)

Basis: the **measured** steady rate from these very runs — **0.4405 s wall/iteration at 4 ranks**
= 0.02937 core-min/iteration (`r2_coarse_R2`, `RUN_META.txt`). **NOT the registered 1.904 s/it/rank
figure, which the calibration rows `C-20260912T202941…` established was measured on the CONTENDED
old box and is ~4× too high.**

| PIMPLE outer-corrector cost, as a multiple of one steady iteration | total for 1,200 steps |
|---|---:|
| 2× | **70 core-min** |
| **3× (the planning figure)** | **106 core-min** |
| 5× | **176 core-min** |

**Registered estimate: 106 core-min. Registered cap: 318 core-min (3×).** **The multiplier is
DERIVED and is the estimate's weakest link** — no `pimpleFoam` run on this mesh exists to measure
it. **$0.091 DERIVED, NOT MEASURED** at $0.0513/core-h (the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER` §5). **NO CAP KILLS THIS RUN** (Sanaa 2026-09-12): the cap is a rule-12
prediction scored at completion, and the estimate-vs-actual row is owed to
`docs/COST_CALIBRATION.md`.

**Checkpoints:** `writeInterval` set so no write exceeds 30 minutes at the measured rate, with
`purgeWrite 2` and `fieldAverage` accumulators written alongside. At 3× the steady rate one step is
~0.088 core-min, so **250 steps ≈ 22 core-min ≈ 5.5 min wall at 4 ranks** — comfortably inside.

---

## 8. WHAT THIS DRAFT HAS **NOT** ESTABLISHED

- **That the flow is unsteady in physical time.** §2 measures a limit cycle in **iteration space**.
  Steady-solver iteration oscillation is *strong evidence* of physical unsteadiness and is **not
  proof of it** — it can also be a numerical limit cycle of the SIMPLE algorithm. **G-U1 is the
  test, and it can fail.** This is stated because it is the honest weakness of the whole motivation.
- **The Strouhal assumption** (§4) — assumed, not measured; G-U3 is its falsifier.
- **The PIMPLE cost multiplier** (§7) — derived, not measured.
- **The Courant number** — unmeasured, reported not gated. A ~50-step probe would fix both this and
  §7's multiplier for ~5 core-min, and **is the cheapest thing to do first if this arm is approved.**
- **That URANS resolves this wake at all.** A k-ω SST URANS on a massively separated notchback rear
  end may damp the shedding it is meant to capture. **Not a reason to skip the arm; a reason not to
  promise its outcome.**
- **Anything whatever about blocker 1** (§0).

*Drafted by a cfd `lab-lane`, 2026-09-12. NOT FROZEN, NOT LAUNCHED, HELD pending the mesh route.
Submissions parked. No agent's message is Sanaa's consent.*
