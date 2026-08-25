# THERMAL RECIPE-FORK AUDIT — supervisor's ruling, 2026-08-25

**Ruled under the cfd team's ruling, cited as THEIRS:** *an observed order
computed across a **recipe-forked** gap is `NOT A RESULT`* — a slope fitted
across a **change of experiment** rather than a change of grid. They found **7 of
14 ladders lab-wide** recipe-forked. This document applies that test to every
ladder in heat-transfer territory, **before this team claims any G**.

Audited by a lane; **the two load-bearing findings re-verified personally by the
supervisor.**

---

## 0. THE HEADLINE, in two parts

**Part one, and it is good news: `T1b-L4` — the ladder about to be graded — is
RECIPE-CLEAN.** Exhaustively: `fvSchemes`, `fvSolution`, `constant/{g,
transportProperties, turbulenceProperties}` and every `0.orig` field are
**identical** across `_c`, `_m`, `_f` and `_x` at all four Reynolds numbers. All
four levels `kOmegaSST`, **`wall_treatment resolved`, no wall-function switch
anywhere** — the classic thermal fork is absent. The first cell shrinks by
**exactly 1.6 per level** (Re 3e4: 3.924543e-04 → 2.452839e-04 → 1.533025e-04 →
9.581404e-05, three ratios of 1.60000). The only non-mesh difference is
`endTime`, **and it is pre-registered before any `_x` case solved**
(`T1b_L4_AMENDMENT.md` §1 and §4, whose protocol says *"registered now so that no
`endTime` is ever chosen with a `Nu` in view"*). **No unregistered `endTime` was
found anywhere in the pool.**

**Part two, and it is not: the ONE observed order this family has been quoting
outside T1b is fitted across a fork, and so is the order it was borrowed from.**

---

## 1. RULING 1 — T3's ladder is NOT GEOMETRICALLY SIMILAR, so `p = 4.304` is NOT AN OBSERVED ORDER

**Verified personally.** `verification/runs/T-family/T3_runs/build_t3.py:72`:

    X_STEP_CELL = 0.03 * H    # finest x cell touching the step, both sides

**It is a module-level constant. It carries no level index**, and it is consumed
at lines 439–440 for **both** `nx_up` and `nx_down`. Confirmed by reading the
file myself.

**Consequence:** on this ladder the wall-normal first cell refines by exactly 1.6
per level (1.121324e-04 → 7.008276e-05 → 4.380172e-05), and the cell counts by
1.6 per direction — **but the streamwise spacing at the step lip is the SAME
PHYSICAL SIZE on all three grids**, an effective local **r = 1.000**
(`MESH_CHECK_2026-08-21.txt` records the step x-cell at the design value on
`R_c`, `R_m` and `R_f` alike). The effective streamwise `r` recovers to ~1.6 only
several step heights downstream; **within ~1.3 H of the step the three grids
share one spacing.**

**RULING: the three grids are not geometrically similar, so a slope fitted across
them is a mixed refinement, and `T3 G2`'s `p = 4.304464` (GCI 0.018800 %) is
`NOT A RESULT` as an observed order.** It may not be quoted as one.

**It is DISCLOSED, and disclosure is not sufficiency.** `T3_PREREGISTRATION.md:155-157`
registers *"first `x` cell `0.03 H` at the step on both sides"* before any case
existed, and `:159-161` registers the totals-based ratios 1.600/1.599.
**Registering a non-similar family makes the fork honest; it does not make the
order meaningful.** A pre-registration can freeze a mistake as easily as a
method.

**`p = 4.304 on a second-order scheme is itself the tell**, and it was visible
before this audit. An order roughly twice the formal order of the discretisation
is the standard symptom of a slope fitted across something other than grid
spacing. **The lab had the diagnostic and did not read it.**

**No verdict moves.** T3's four rows already read `NOT A RESULT` at rule 5 clause
(1) — `R_c` sits in a limit cycle at the 80 000 cap, registered in advance
(`T3_PREREGISTRATION.md` §11). **What moves is that `MATRIX_CONTRIBUTION.md:29`
and `:244` carry the `p` and the GCI as if they meant something.** Corrected by
quote-and-strike; the numbers stay visible, struck, with this ruling cited.

---

## 2. RULING 2 — K0b's ORDERS ARE FITTED ACROSS AN ITERATION-COUNT FORK WHOSE EFFECT IS 8× THE GRID STEP

**This is the most consequential finding in the audit, and it was verified
personally, because it compounds the K0c ruling rather than merely adding to it.**

K0b's 32/64/128 triple grades its three legs at **three different iteration
counts: t = 1386 (m32), t = 4000 (m64), t = 16000 (m128).** The dictionaries are
otherwise clean — `build_and_run.sh` refuses if any dictionary differs
byte-for-byte.

**The lane that built it measured the alternative and left BOTH readings on
disk.** Read personally from the two artifacts:

| artifact | `Nu_avg_hot` |
|---|---|
| `measured_L128a_endTime4000.json` — m128 at t = 4000 | **4.325464885013862** |
| `measured_L128b_endTime16000.json` — m128 at t = 16000 | **4.528816741169209** |

**A 4.5 % swing on the graded quantity from the ITERATION COUNT ALONE, against
the 0.552 % m→f GRID step the `p = 1.94` is fitted on. The iteration-count
sensitivity is roughly 8× the effect being measured.** `stratification_S` swings
**11.69 %**. **Read at a common count of 4000, the m→f step REVERSES SIGN.**

**The plateau instrument is itself forked:** `Nu_drift_write_gap_iterations` is
**6** for m32, **10** for m64 and **2000** for m128. *A 0.0063 % drift measured
over 2000 iterations is not the same statement as 3.9e-06 % over 6.*

**RULING: K0b's observed orders are `NOT A RESULT`.**

**Iterating each level to its own convergence is defensible practice, and this
ruling does not condemn it.** What is not defensible is **quoting the resulting
order without stating that the finest level's value moves 8× the fitted step
under the choice that was made** — especially when **both choices are sitting on
disk**, which means the lab measured the thing that invalidates its own number
and filed it.

### 2.1 THIS COMPOUNDS THE K0c RULING — the borrowed number was never a result to borrow

`THERMAL_TIER_AUDIT_RULING_2026-08-25.md` §2 established that **K0c has no
Roache triple** (four mesh pairs; `gate_k0c.json` carries `gci` 0 / `richardson`
0 / `triple` 0 / `observed_order` 0, against a positive control of 4 / 2 / 17 on
`gate_t3.json`) and that the orders quoted for it are **K0b's**, whose own record
disclaims them at `K0c_RESULTS.md:335`.

**This ruling establishes the second half: those K0b orders are not a result
either.** So the defect is **two layers deep, not one**:

1. an order was **borrowed from a different experiment** (different `div` schemes
   — `linearUpwind`/`limitedLinear` vs plain `linear` — and a different `Pr`,
   0.706814 vs 0.710000), **against that experiment's own written prohibition**;
2. **and the borrowed order was itself `NOT A RESULT`**, fitted across an
   iteration-count fork with an 8× effect;
3. **and it was narrowed in the borrowing** — quoted as *"1.94–2.33"* where K0b's
   own table runs **1.75 to 2.98**.

**A number can be wrong in three independent ways at once, and each way was
individually discoverable from artifacts already on disk.** That is the finding
worth carrying, more than any single row's tier.

---

## 3. THE OTHER FORKS — real, recorded, and none of them moves a verdict

### 3.1 K0cT — the two levels of the pair stop on different residual criteria

`T_hi_c/system/fvSolution` vs `T_hi_f/system/fvSolution` (identically
`T_lo_c`/`T_lo_f`), inside `residualControl`:

    coarse:  p_rgh 1e-07;  U 1e-08;  T 1e-08;  "(k|omega|epsilon)" 1e-08;
    fine:    p_rgh 1e-30;  U 1e-30;  T 1e-30;  "(k|omega|epsilon)" 1e-30;

**The textbook thermal recipe fork: the two levels stop on different criteria.**
Provenance is visible — `K0cT_runs/README.md:15` describes
`continue_past_residual.sh`, and the **fine** levels are exactly the ones that
stopped early (`T_hi_f` at 6688, `T_lo_f` at 6237, `M_hi_f_LS` at 10185). **The
repair was applied to the fine levels only; the coarse dictionaries were left.**

**Mitigation, stated because it matters:** both coarse levels reached their
`endTime` anyway (`T_hi_c` 140000 = endTime; `T_lo_c` 60000 = endTime), **so the
looser criterion never fired.** The fork is **real in the dictionary and nil in
these runs.** K0cT is a **pair** regardless, so no order rests on it.

**BINDING FORWARD: no future triple may borrow a K0cT level without re-running it
under one criterion.**

**The downstream campaign already absorbed the lesson** —
`K0cX_runs/build_cases.py:497-501`: *"`residualControl` is DELIBERATELY ABSENT.
K0cT Section 4 measured that it stopped three cases at 6-10k iterations, well
before the graded quantities were steady."* **Recorded because a lesson that was
applied is evidence the process works, and it belongs beside the failures.**

### 3.2 K0c Ra1e6 — the pair's two members were produced by different procedures

`Ra1e6_m128`: three solver stages, `controlDict.stage1` endTime 12000,
**`writePrecision 10`**, then a stage-3 rewrite at precision 16.
`Ra1e6_m192`: two stages, endTime 4000, **`writePrecision 16` from the first
write**, no stage 3. **Final fields are at precision 16 on both, so the graded
numbers are read at the same precision — the fork is in how they got there.**
`README.md:54-58` names `Ra1e6_m192` as *"the exception, in three ways"*. **A
pair, so nothing rests on it.** Its `r` is also **1.5** where the other three
pairs are **2.0**.

### 3.3 T10a-S — `r` is NOT constant, and the comparator uses a single value

Radiating-face edge **1.600 / 1.625**; **shell thickness 1.500 / 1.667**; cells
**1.5657 / 1.6386**. `analyse_t10a.py:76,610` applies a single registered
`R_REFINE = 1.6` to both steps.

**RULING: the registered denominator governs, because it was frozen before
compute.** `T10a_registered.json` defines the ladder on **radiating-face edge
count**, where the ratios are 1.600 / 1.625 — a **1.6 % inconsistency, not the
4.7 % the cell counts suggest.** This is a **disclosed near-similarity, not a
fork**, and it does not send T10a's orders to `NOT A RESULT`.

**BINDING FORWARD: any future claim resting on T10a's orders must carry that
1.6 % drift as a stated uncertainty on `p`, not silently assume `r = 1.6`.**
S22's tier has already fallen to `GATE REACHED` (missing P), so **no tier moves
on this.**

### 3.4 T1b-L4's two quantified caveats — neither is a fork

- **The grid family is NEAR-similar, not exactly similar.** Because both `n` and
  δ₁ scale by 1.6, the wall-to-axis expansion ratio drifts: at Re = 3e5,
  **206.057 (c) → 212.419 (x), +3.09 %** over the ladder; at Re = 1e4 it drifts
  only **+0.15 %** and is **non-monotone**. Same class as T3's y-grading (~1.4 %)
  and K0cX's (~3.7 %). **Small, but not zero, and a Roache order assumes zero.**
  **To be carried as a stated uncertainty when L4 is graded.**
- **The 1.6008 radial ratio at the `x` level** (205 = round(204.8)) is
  **disclosed and costed** in `T1b_L4_AMENDMENT.md:60-67`: it moves an observed
  order by **ln 1.6 / ln 1.6008 = 0.9995**. Negligible and registered.

**The residual exposure the brief anticipated:** within the graded `(m, f, x)`
triple at Re = 3e4 the three levels ran **20000 / 40000 / 80000** iterations —
**superficially K0b's failure.** It is **legitimate here and was not there** for
one reason: `analyse_t1b_L4.py` **gates iterative convergence and plateau PER
LEVEL as step (1), before the triple is formed** (`T1b_L4_AMENDMENT.md` §2).
**That is the protection K0b lacked**, and it is why the same-shaped difference
is benign on one ladder and fatal on the other.

---

## 4. LADDER-BY-LADDER

| ladder | levels | measured r | verdict |
|---|---|---|---|
| **T1b-L4** `R_*_{c,m,f,x}` | 4 | 1.6000 / 1.6000 / 1.6008 | **RECIPE-CLEAN** (§3.4) |
| **T1c** `L_Ts`, `L_q`, `D_*` | 3 each | 1.6000 / 1.5981 | **RECIPE-CLEAN** |
| **T3** `R_c/R_m/R_f` | 3 | 1.6000 / 1.5986; **step x 1.000 / 1.000** | **RECIPE-FORKED** — §1 |
| **T9a** `F_*`, `W_*`; T9aD, T9aH | 3 each | 1.600 / 1.594–1.625 | **RECIPE-CLEAN** |
| **T10a** `B_*` | 3 | 1.6250 / 1.6154 | **RECIPE-CLEAN**, r not constant |
| **T10a** `S_*` | 3 | 1.5657 / 1.6386 | **RECIPE-CLEAN**, r NOT constant — §3.3 |
| **T10a-R** 4th level | 3 | 1.6154 / 1.6190 | **RECIPE-CLEAN** |
| **T10aR** `R_q`, `R_s` | — | — | **NOT A LADDER** — quadrature and tolerance arms |
| **E4 / E4a2** `F_*` | 3 each | **1.5000 / 1.5000 exactly** | **RECIPE-CLEAN** — the only exactly-constant-r ladder in the territory |
| **K0c** Ra1e3–1e6 | **2 each** | 2.0, 2.0, 2.0, **1.5** | **NO ORDER POSSIBLE**; Ra1e6 also forked — §3.2 |
| **K0b** m32/m64/m128 | 3 | 2.0 / 2.0 | **FORKED on iteration count** — §2 |
| **K0cS + K0cG** `_c/_f/_x` | 3 | 1.600 / 1.5990 | **RECIPE-CLEAN** |
| **K0cS, K0cP, K0cQ, K0cR** | 2 each | 1.600 | **PAIRS** — no order |
| **K0cT** `T_{hi,lo}_{c,f}` | 2 each | 1.600 | **PAIRS, and FORKED** — §3.1 |
| **K0cX** `X_hi_*` | 3 each | 1.6000 / 1.5964 | **RECIPE-CLEAN** |
| **K0cX** `X_lo_*`, `*_LAM` | 2 each | 1.600 | **PAIRS** — no order |
| **K2b** `K2bP_*` | 2 | 1.500 | **PAIR** — no order |
| **K2bU3** `M`/`L050`/`L025` | 3 | 2.000 / 2.000 | ladder exists; comparator computes **no order** |
| **K2e** m48/m96 × 4 dT | 2 each | 2.000 | **PAIRS** — no order |
| **KV1**, **THERMAL_K0** | 1 mesh | — | **NOT A LADDER** |

**Count: of the ladders that could carry an order, T3 and K0b are forked; K0c's
Ra1e6 pair is forked but carries no order. Everything else that has three levels
is recipe-clean.**

---

## 5. NOT VERIFIED — stated plainly

- **No comparator was re-run.** Every state word (`CONVERGING`, `STAGNANT`, …) is
  read from committed gate artifacts, not recomputed.
- **`constant/polyMesh/points` was not read directly** for the T-family ladders —
  the mesh trees are gitignored and rebuilt. T3 used the committed
  `MESH_CHECK_2026-08-21.txt`, which **is** a points-based measurement; T1b used
  builder-written `CASE.txt`, **cross-checked** against `T1b_L4_AMENDMENT.md` §6's
  points-based table (wall cell within **0.095 %** of design on all four `_x`
  meshes).
- **Whether T10a-S's non-constant `r` actually biases its reported `p`
  (0.954 / 0.853 / 0.825) was NOT established** — only that the comparator uses
  one `r` where the two steps differ. §3.3 rules on which denominator governs;
  it does not measure the bias.
- **`K0cX` levels were NOT confirmed individually plateaued.** `writeInterval ==
  endTime` on every K0cX case means **exactly one checkpoint exists per case**;
  convergence is judged from a `hotFlux` history in `postProcessing`
  (`analyse_k0cx.py:644-704`). **The instrument exists; that it passes was not
  confirmed.** The finest levels ran the **fewest** iterations (60000 / 50000 /
  30000 for c / f / x) — **the direction that warrants the check.** Docketed.

---

## 6. WHAT THIS RULING DOES NOT DO

- **It moves no gate verdict.** T3 was already `NOT A RESULT ×4`; K0b's rung is
  `SURVEYED`; K0c's `PASS` stands as its frozen comparator returned it.
- It creates, retires and moves **no gate, threshold, band, cap or label**.
- It does **not** re-run or repair any ladder. K0c wanting a third level and K0cG
  wanting a finest-level plateau monitor **each want a NEW pre-registration,
  never an edit to a frozen one.**
- It authorises **no send. SUBMISSIONS REMAIN PARKED.**

## 7. FOLLOW-UP

1. **`MATRIX_CONTRIBUTION.md:29` and `:244`** — strike T3's `p = 4.304` / GCI
   0.0188 % as an observed order, citing §1. **Quote-and-strike; the numbers stay
   visible.**
2. **K0b's orders** — mark `NOT A RESULT` wherever quoted, citing §2. **This is
   the same act as removing the ground under K0c's borrowed range.**
3. **T3** — a similar ladder needs `X_STEP_CELL` to scale with the level. That is
   a **new pre-registration and a re-run**, not an edit. Relates to **D495**
   (fourth level `R_ff`, NOT AUTHORIZED, on Sanaa's desk).
4. **K0cX** — confirm per-level plateau at the finest levels, which ran fewest
   iterations.
5. **When T1b-L4 is graded** — carry the **+3.09 %** expansion-ratio drift as a
   stated uncertainty on `p`. Do not assume exact similarity.
