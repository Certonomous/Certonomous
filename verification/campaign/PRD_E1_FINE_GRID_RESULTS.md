# PRD-E1 — RESULTS ON THE FINE GRID ONLY

**Rung:** PRD-E1 (Porous Radiator Duct, EXACT-tier rung 1; Navier-spine Case 3).
**Author:** cfd `lab-lane`, at the cfd-supervisor's dispatch, 2026-09-12.
**Compute in this record:** 2.567 core-min (the grading run only; no solver launched).
**Status of the ladder:** post-compute, previously **UNGRADED**. This is its first grading.

---

## 0 — THE AUTHORITY FOR GRADING ON ONE GRID, AND ITS EXACT EXTENT

The registered gate needs a three-level `CONVERGING` Roache triple per `U_s`
(`PRD_E1_GATE_RULING_2026-09-09.md` §1.4, §3; registration amendment elements 1–5), and
`verification/campaign/PRD_E1_GATE_RULING_2026-09-09.md` §1.2 additionally requires an
L4 at any `U_s` whose L3 GCI reaches 2 %. **Sanaa relaxed that requirement herself, in
her own words, 2026-09-10T20:40Z:**

> **"prd/ NOPE ITS FINE WE CAN SEE THE RESULT on the fine grid only."**

Only Sanaa can move a gate requirement (`CLAUDE.md` rule 9; `ESCALATION_CHARTER` §8) and
she did. That quotation is the whole authority for §4 below, and this record cites no
other.

**WHAT SHE RELAXED, AND WHAT SHE DID NOT.** She relaxed the **grid** requirement — the
triple and the L4. She did not touch, and this record does not treat as touched:

- **`CLAUDE.md` rule 5 step (a)** — *any level not iteratively converged or not plateaued
  → `NOT A RESULT`*. That clause is about **iterative** convergence of the level being
  read, not about the grid. A fine-grid number read off a level that has not settled is
  not a measurement of anything, on any grid. **It is applied below at full strength and
  it removes two of the five points.**
- **Rule 3**, the planted-zero contract.
- The **rule-4** strict completion rule.
- The **y+** and **checkMesh** gates, which may only turn a PASS into `NOT A RESULT`.

**AND THE PRICE OF THE RELAXATION, STATED ONCE AT FULL VOLUME.** A single-grid value
carries **no discretisation uncertainty whatsoever**. There is no GCI in this document,
there is no observed order in this document, and there is no Richardson extrapolation in
this document — **not because they were omitted but because none of them exists for this
ladder** (§5 proves that independently of Sanaa's instruction). `G-ASYMP`, the registered
asymptotic gate, is therefore **not evaluated at all**, and since the registered `PASS`
requires `G-ERGUN` **and** `G-ASYMP` on a `CONVERGING` triple, **nothing in §4 is the
registered PASS of PRD-E1.** §4 reports the fine-level band test and says so in every row.

---

## 1 — RULE-2 IDENTITY: THE FROZEN FILE IS THE FILE THAT GRADED

Hashes, not assurances. Re-runnable by anyone.

| what | value | check |
|---|---|---|
| frozen registration body (lines 1–688), blob | `65dc864325e665a4cfdb7c34bf5af5aa59765f5c` | reproduced by `git hash-object` on `head -688` of the worktree file |
| `head -688 … \| sha256sum` | `792c3917194b1a23068e14dba1a344d11306f725966344c40e5bd8831ff4e375` | **equals** the value Amendment 1 §P1.0 recorded → nothing above line 688 moved |
| registration file at HEAD (793 lines = body + Amendment 1), blob | `5255e4f8743a59ddfb6aa76aff867a5265797e13` | worktree blob **identical** to `HEAD:` blob |

**A trap worth recording, because it will catch the next reader.** Amendment 1 §P1.0
tabulates `git show HEAD:<path> | sha256sum` = `792c3917…`. That was true when the
amendment was written and it is **false now**, because the amendment then appended itself
to the file it was hashing. The surviving, still-true assertion is the **third row of
that table** — `head -688 | sha256sum` — and it reproduces exactly. The frozen body is
intact; only the whole-file hash moved, and it moved for a legal reason.

**FREEZE.1 grading-path members — worktree blob vs `HEAD:` blob:**

| member | blob (worktree == HEAD) | matches pin |
|---|---|---|
| `cases/navier_class/PRD/build_prd.py` | `4ec9e9c440bf50b7e88ab0c9f041cdd21df7ab0c` | FREEZE.1 ✓ |
| `cases/navier_class/PRD/mark_done_prd.py` | `be40d0f3342a2da7f7a13476c4eef51455d27b06` | FREEZE.1 ✓ |
| `cases/navier_class/PRD/autograde_prd.py` | `b9b841f556d9cbed60f32a846a84860772677387` | FREEZE.1 ✓ |
| `scripts/roache_triple.py` | `23afaee32f770f9f38a827e38ac963b9368b7707` | **Amendment 1 §P1.3 re-pin** ✓ (FREEZE.1's `78e56a3b…` is superseded) |
| `cases/navier_class/PRD/analyse_prd.py` (SELF member) | `428535d6f8c295b478b03d7cb732222ee161db2e` | **equals the `FREEZE-PIN:` line in pin commit `a257ddf67`** ✓ (FREEZE.2 grade-time byte-identity) |

The comparator's own `verify_self()` printed its running blob as `428535d6…` against
freeze pin `724356ecb6d8da8fe4b777fbcce3a7cb81d28838` during the grading run.

---

## 2 — A DEFECT IN THE FROZEN GRADING PATH, RECORDED BECAUSE IT IS LOAD-BEARING

**The frozen comparator `analyse_prd.py` cannot grade.** Its `main()`, with no
`--selftest`, calls `verify_self()` and then **unconditionally refuses**:

```
    verify_self()
    refuse("PRD-E1 has not been run: verification/runs/navier_class/PRD/ does not "
           "exist. This comparator grades on-disk artifacts; there are none. "
           "(STOP-BEFORE-FREEZE: authored + self-tested, not yet graded.)")
```

It never reads `RUNS`. The refusal is hardcoded on a condition — the run home not
existing — that has been **false since 2026-09-09 22:47** (Amendment 1 §P1.1). Frozen
into the comparator is a sentence that was true at freeze and is now simply wrong, and
because it is a `refuse()` and not a check, **it cannot notice.**

This is not fatal, and it is why the ladder is gradable at all: the **driver** lives in
the other FREEZE.1 member, `autograde_prd.py`, whose `grade_all()` walks the run tree and
calls `analyse_prd`'s frozen readers, controls, band constants and `grade_us()`. **That is
what was run**, and every number in this record comes out of it. No new comparator was
written for PRD-E1 and none was needed.

**Consequence for the record:** the FREEZE.1 table names a member that, invoked as a
grader, refuses; the member that actually grades is `autograde_prd.py`. That is a
disclosure, not a repair — **this record changes nothing on the grading path.** It is
referred to verification and to the supervisor.

---

## 3 — RULE-4 COMPLETION, LIMB BY LIMB, ON THE FIVE FINE (L3) RUNS

Delegated to the frozen `mark_done_prd.py` (which returned `DONE`, rc 0, for all fifteen
cases), **and independently re-derived limb by limb from the run artifacts** rather than
believed off the marker.

**THE FIELD SET AND THE AGE ANCHOR, NAMED FOR THIS FAMILY.** PRD is **not** the thermal
family. `simpleFoam` here is steady, incompressible and **isothermal** — there is no
energy equation, no `T`, no `p_rgh` and no `alphat`. The registered field set is
**`{U, p, k, omega, nut, phi}`** (registration §7 clause 5; ruling §4.5; enforced at
`mark_done_prd.py` as an explicit list). The age guard cannot anchor on `0/T` because
**`0/T` does not exist**; it anchors on **`0/U`**, which the launcher touches **last** at
launch and which therefore dates the run allowed to produce the answer — the identical
role `0/T` plays in the thermal family, carried by the field this solver actually has
(`mark_done_prd.py:65`, `AGE_REF = ("0", "U")`).

| case | rc | `End` | last `Time` | `endTime` | `deltaT` | `ExecutionTime` count | `round(endTime/deltaT)` | fields at `3000` | every field newer than `0/U` |
|---|---|---|---|---|---|---|---|---|---|
| `us0.25_L3` | 0 | 1 | 3000 | 3000 | 1 | 3000 | 3000 | U p k omega nut phi | YES |
| `us0.50_L3` | 0 | 1 | 3000 | 3000 | 1 | 3000 | 3000 | U p k omega nut phi | YES |
| `us1.00_L3` | 0 | 1 | 3000 | 3000 | 1 | 3000 | 3000 | U p k omega nut phi | YES |
| `us2.00_L3` | 0 | 1 | 3000 | 3000 | 1 | 3000 | 3000 | U p k omega nut phi | YES |
| `us4.00_L3` | 0 | 1 | 3000 | 3000 | 1 | 3000 | 3000 | U p k omega nut phi | YES |

`deltaT` = 1 throughout, so this is the fixed-`deltaT` clause-5 path (V-136), not the
adaptive one. **All five fine runs are COMPLETE on every limb.** No run is excluded from
§4 on completion grounds.

*Caveat stated rather than buried:* `mark_done_prd.py` reported `rc_source=READ-FROM-STATUS`
— the return code is read from the launcher's `STATUS.<case>` sidecar, not from a separate
`rc` file. The sidecars carry `rc=0 … note=clean` with start and end UTC stamps, and the
`End` line in each `log.simpleFoam` corroborates a clean solver exit. The rc limb is
therefore evidenced, but by the launcher's record of the exit rather than by the exit
itself.

---

## 4 — THE FINE-GRID RESULT

Mesh: **L3 = 64 × 64 cross-section, 96/96/96 streamwise, 1,179,648 cells.**
Quantity: core Δp in Pa = `RHO × (area-avg p at x=0.200 m − area-avg p at x=0.300 m)`,
`RHO = 1.2` — the ×ρ kinematic→Pa conversion, read by the frozen `analyse_prd.read_dp_pa`
from `postProcessing/dp_{inlet,outlet}_plane/0/surfaceFieldValue.dat`.
Reference: the frozen analytic `ergun_dp(U_s) = 168.75·U_s + 656.25·U_s²`.
Band: the frozen `ERGUN_BAND_REL = 0.03` (±3 % relative), ruling §1.1.

| `U_s` [m/s] | L3 Δp [Pa] | Ergun Δp [Pa] | relative | ±3 % band [Pa] | L3 iterative | L3 plateau | **verdict** |
|---|---|---|---|---|---|---|---|
| 0.25 | 83.212072 | 83.203125 | +0.010753 % | [80.7070, 85.6992] | **NOT_CONVERGED** | **NOT_PLATEAUED** | **NOT A RESULT** |
| 0.50 | 248.402585 | 248.437500 | −0.014054 % | [240.9844, 255.8906] | **NOT_CONVERGED** | PLATEAUED | **NOT A RESULT** |
| 1.00 | 824.796341 | 825.000000 | −0.024686 % | [800.2500, 849.7500] | CONVERGED | PLATEAUED | **PASS** (`G-ERGUN`, fine level) |
| 2.00 | 2961.569106 | 2962.500000 | −0.031423 % | [2873.6250, 3051.3750] | CONVERGED | PLATEAUED | **PASS** (`G-ERGUN`, fine level) |
| 4.00 | 11171.091991 | 11175.000000 | −0.034971 % | [10839.7500, 11510.2500] | CONVERGED | PLATEAUED | **PASS** (`G-ERGUN`, fine level) |

### 4.1 — `U_s` = 0.25 m/s — **NOT A RESULT**

The fine run is complete (§3) but its fine level is neither iteratively converged nor
plateaued. Final `Ux` initial residual **9.958e-05** against the frozen
`IT_RESID_TOL = 1.0e-5` — a factor of 10 short. The last four monitored Δp writes are
83.200593, 83.178050, 83.220324, 83.212072 Pa, a relative spread of **4.089e-04** against
the frozen `PLATEAU_REL_TOL = 1.0e-4` — a factor of 4 short. Rule 5 step (a) fires.
**This is a single-grid value with no grid-convergence uncertainty quantified, reported
on the owner's explicit instruction** — and it is not a graded value at all, because the
level it sits on has not settled. Its distance from Ergun (+0.0108 %) is printed above as
information and **is not a verdict and must not be quoted as one.**

### 4.2 — `U_s` = 0.50 m/s — **NOT A RESULT**

Plateaued (spread 2.975e-05, comfortably inside 1.0e-4), but **not iteratively
converged**: final `Ux` initial residual **1.107e-05** against `IT_RESID_TOL = 1.0e-5`.
**That is a miss by 11 %, and a near miss is a miss.** The temptation to wave this one
through is exactly what the criterion exists to resist; the threshold was frozen before
the run and it is not moved afterwards to admit a value that is otherwise attractive.
**This is a single-grid value with no grid-convergence uncertainty quantified, reported
on the owner's explicit instruction.** Its distance from Ergun (−0.0141 %) is information,
not a verdict. **What would clear it:** re-run this case to a lower `Ux` residual; nothing
else. The case is cheap (220 core-min at L3).

### 4.3 — `U_s` = 1.00 m/s — **PASS** on `G-ERGUN` at the fine level

Δp **824.796341 Pa** against Ergun **825.000000 Pa**, relative **−0.024686 %**, inside the
pre-registered ±3 % band [800.2500, 849.7500] by a factor of 122. Fine level CONVERGED
(`Ux` 9.041e-06, `p` 1.834e-09) and PLATEAUED (spread 2.267e-06). **This is a SINGLE-GRID
value with NO grid-convergence uncertainty quantified, reported on the owner's explicit
instruction.** No GCI is quoted, no observed order is quoted, no Richardson extrapolation
is quoted, and `G-ASYMP` is not evaluated; the registered `PASS` of PRD-E1 requires
`G-ERGUN` **and** `G-ASYMP` on a `CONVERGING` triple and **this is not that.**

### 4.4 — `U_s` = 2.00 m/s — **PASS** on `G-ERGUN` at the fine level

Δp **2961.569106 Pa** against Ergun **2962.500000 Pa**, relative **−0.031423 %**, inside
±3 % [2873.6250, 3051.3750]. CONVERGED (`Ux` 7.875e-06, `p` 1.971e-09), PLATEAUED (spread
2.483e-06). **This is a SINGLE-GRID value with NO grid-convergence uncertainty
quantified, reported on the owner's explicit instruction.** No GCI, no order, no
extrapolation, `G-ASYMP` not evaluated.

### 4.5 — `U_s` = 4.00 m/s — **PASS** on `G-ERGUN` at the fine level

Δp **11171.091991 Pa** against Ergun **11175.000000 Pa**, relative **−0.034971 %**, inside
±3 % [10839.7500, 11510.2500]. CONVERGED (`Ux` 7.276e-06, `p` 9.632e-09), PLATEAUED
(spread 2.952e-07). **This is a SINGLE-GRID value with NO grid-convergence uncertainty
quantified, reported on the owner's explicit instruction.** No GCI, no order, no
extrapolation, `G-ASYMP` not evaluated.

**What this point is worth, stated because it is the one that matters.** At `U_s` = 4 the
viscous fraction is **6.0 %** and the Δp is **94 % inertial** — the regime the ½ρ
Forchheimer factor dominates, and registration §4 loss mode (a) names a missing factor of
2 there as "the single most likely silent error". A missing ½ρ would halve the inertial
term and land Δp near **6100 Pa** against 11175. The measured **11171.09 Pa** is
0.035 % low. **The `3.5 = 2 × 1.75` factor in `build_prd.py` is doing its job, and this
point is the evidence.** That is a statement about the coefficient chain, on one grid; it
is not a grid-converged verdict.

---

## 5 — THE REGISTERED (TRIPLE) GRADING, WHICH IS THE PRIMARY RECORD, AND THE ROACHE STATE

**Run in full, as registered, on all 15 solves. Artifact:
`verification/runs/navier_class/PRD/gate_prd_e1.json`, written 2026-09-12T00:39:06Z.**

> **ALL FIVE `U_s` ARE `NOT A RESULT` UNDER THE REGISTERED GATE. 0 of 5 PASS.
> `credential = false`.**

**AND THE ROACHE STATE IS NOT `CONVERGING` AT ANY `U_s` — IT WAS NEVER REACHED.** Every
triple stopped at rule 5 **step (a)**, before any triple character was computed:

| `U_s` | plateau L1 / L2 / L3 | iterative L1 / L2 / L3 | why |
|---|---|---|---|
| 0.25 | NOT / NOT / **NOT** | NOT / NOT / **NOT** | levels L1,L2,L3 not converged or not plateaued |
| 0.50 | NOT / PLAT / PLAT | NOT / CONV / **NOT** | levels L1,L3 |
| 1.00 | NOT / PLAT / PLAT | NOT / CONV / CONV | level L1 |
| 2.00 | NOT / NOT / PLAT | NOT / NOT / CONV | levels L1,L2 |
| 4.00 | NOT / NOT / PLAT | NOT / NOT / CONV | levels L1,L2 |

**SAID LOUDLY, BECAUSE IT IS THE THING A READER WILL OTHERWISE ASSUME AWAY: there is no
`CONVERGING` triple for PRD-E1, there is no observed order, and THERE IS NO GCI — not one,
at any `U_s`.** `grade_ladder` returned `order = None`, `GCI_pct = None`,
`richardson = None`, `asymp_rel = None` for all five. No number in this document may be
accompanied by a grid-convergence claim, and none is. **`L4` is not indicated either** —
`l4_required_for` is empty, because the pre-asymptotic guard is downstream of a
`CONVERGING` triple that never arrived.

**THE MECHANISM, NAMED: THE COARSE LEVELS WERE UNDER-ITERATED, NOT THE FINE ONES.** All
five L1 runs and three of five L2 runs fail step (a); four of five L3 runs pass it. The
ladder ran every level to the same `endTime` 3000 with the same `residualControl`, and the
coarse meshes — which converge *faster* per iteration in wall time but were given the same
iteration count — did not settle their monitored Δp to 1e-4. **This is a campaign design
finding, not a numerics failure**, and the fix is an iteration budget per level rather
than one shared `endTime`. It is a **finding and is not written off**: it is why PRD-E1 has
no triple and therefore why Sanaa's fine-grid-only instruction is the only thing that
makes the ladder readable at all.

**This ordering is one-way and was not reversed.** Rule 5 permits a gate to turn a PASS or
GATE FAIL **into** `NOT A RESULT`, never the reverse. §4's three PASS rows are the
fine-level band test under Sanaa's relaxation; they do **not** overturn §5's five
`NOT A RESULT` rows, which remain the registered verdict of PRD-E1.

---

## 6 — CONTROLS, AND ONE THAT IS MISSING

**Rule 3, control 3 — the planted perturbation, PASSED at all five `U_s`.** The frozen
`control_dp_reader` copies the fine level's own `dp_outlet_plane/0/surfaceFieldValue.dat`,
adds `PLANT_DP / RHO` to the last data row, re-reads through the **real** reader, and
requires the reported Δp to shift by exactly **−3.210 Pa** to within 1e-6 Pa; it refuses
otherwise. `plant_control_passed = true` for 0.25, 0.50, 1.00, 2.00 and 4.00. The reader
is wired to the field the solver wrote. The control has a demonstrated failing branch: the
comparator's own selftest drives it with a blind constant reader and it does not pass.

**Rule 3, controls 1+2 — the visibility pair — ABSENT. Say it plainly.**
`visibility_pair = null` at every `U_s`, because **no INERT (`D = f = 0`) case exists in
the run tree**. Registration §6 registered three controls and **only one of them ran for
the graded ladder.** The §2bb pre-flight exercised the ACTIVE/INERT pair in scratch before
the freeze, and that scratch evidence is not in the run home and is not cited here as if
it were. **What this does and does not cost us:** the gated quantity here is a large
non-zero Δp, and the failure the pair guards against — trusting a *zero* from a reader
never shown able to see a non-zero — is not the failure mode in play, since the plant
control positively demonstrated non-zero sensitivity on each graded artifact. But the
registered control set was not fully executed, the shortfall is on the record, and
**closing it costs one coarse `D = f = 0` solve (~2 core-min).**

**y+ gate (≤ 200, continuous/Menter treatment) — PASSED at all five, with its own planted
control passing:** max y+ at L3 = **3.643 / 5.203 / 7.552 / 11.476 / 18.598** for
`U_s` = 0.25 / 0.50 / 1.00 / 2.00 / 4.00. Registration prediction **P-YPLUS** put L3 at
`U_s` = 1 in ~10–20; measured **7.55**, so P-YPLUS is **low by about 25–50 %** and is
scored as a miss in the conservative direction, not quietly ignored.

**checkMesh gate — PASSED at all five:** non-orthogonality max **0.0**, mean **0.0**,
skewness **2.13e-13**, against the registered < 70 / < 20 / < 4. An all-hex blockMesh
duct, exactly as §5 predicted.

Both gates passed, so neither turned anything into `NOT A RESULT`; §5's verdicts come from
step (a) alone.

---

## 7 — COST (rule 12)

Unit = core-minutes = wall s × ranks ÷ 60, read from each run's own `STATUS.<case>`
sidecar. Every dollar figure is **DERIVED at $0.0513/core-h, c7a.4xlarge, reported-by-owner,
NEVER MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
All fifteen solves ran **serial, ranks = 1**.

| level | per-`U_s` core-min (0.25 / 0.50 / 1.00 / 2.00 / 4.00) | level total |
|---|---|---|
| L1 | 1.750 / 2.150 / 1.900 / 2.133 / 2.833 | **10.766** |
| L2 | 19.633 / 20.417 / 17.100 / 20.150 / 19.433 | **96.733** |
| L3 | 196.033 / 220.450 / 207.183 / 193.867 / 182.650 | **1000.183** |
| | **LADDER TOTAL** | **1107.682 core-min** = 18.4614 core-h = **$0.9471 DERIVED** |

Plus the grading run in this record: **2.567 core-min** (154 wall s × 1 rank; the frozen
`autograde_prd.py --grade`, which produced the five `log.yPlus` files via
`simpleFoam -postProcess -func yPlus -latestTime`). Grand total **1110.249 core-min =
$0.9493 DERIVED**.

**Against the pre-registration.** Two point estimates are frozen and they differ by
topology, so both are scored rather than the flattering one chosen:

| frozen estimate | where | value | ratio actual/predicted |
|---|---|---|---|
| serial-topology point | FREEZE section, *"full ladder ≈ 1245 core-min (serial) ≈ $1.07 DERIVED"* | 1245 core-min | **0.890** |
| 16-rank design point | §9 POINT | 4160 core-min | 0.266 |
| CAP | §9 | 9000 core-min | 0.123 |

The operative comparison is the **serial** one, because serial is the topology that ran:
**ratio 0.890, an 11 % under-run.** No per-case cap was breached (each L3 run carried a
300 core-min cap and the worst, `us0.50_L3`, used 220.450). **No overrun, no stop.**
**Waste: 0.000 core-min, named separately per `COMPUTE_BUDGET_CHARTER.md` §6 and never
folded into the ratio** — every one of the fifteen solves ran once, to `endTime`, rc 0,
`note=clean`; nothing was abandoned or re-run. Not carried into the ratio: the pre-freeze
L-514 sensitivity pair (2.417 core-min, scratch, recorded in the registration's own
addendum) and the §2bb pre-flight, which ran in scratch and whose figure is **not in any
record I can cite and is therefore left out rather than approximated**.

**Stall check:** the three L3 runs at `U_s` = 0.25, 0.50 and 1.00 ran 11762, 13227 and
12431 wall s, all **above** the 3600 wall s figure in `CLAUDE.md` rule 12 /
`COMPUTE_BUDGET_CHARTER.md` §2. They are **not stalls** — they are single 1.18 M-cell,
3000-iteration solves running serial on one core, and their `ExecutionTime` advances
monotonically to `End`. This row therefore **touches the open literal-reading referral**
carried by the T26 `L3ABS` and M6C2 `L2` rows on the calibration ledger, and reaches the
same answer they did: the 3600 s figure, read literally, flags healthy long serial solves.
The referral stays open; this lane does not settle it.

The calibration row is filed separately in `docs/COST_CALIBRATION.md`.

---

## 8 — WHAT I COULD NOT VERIFY

1. **`G-ASYMP` is unevaluated and unevaluable from this evidence.** It needs a
   `CONVERGING` triple and there is none. The registered credential — PASS at all five
   `U_s` — is therefore **not earned and is not claimed.**
2. **No grid-convergence uncertainty exists for any number in this document.** Not
   estimated, not bounded, not approximated. Absent.
3. **The visibility pair (§6) was never executed in the run home.** One control of three.
4. **`rc` is read from the launcher's `STATUS` sidecar, not from an independent `rc`
   file** (§3 caveat).
5. **The §2bb pre-flight cost is not in any citable record** and is omitted from §7 rather
   than guessed.
6. **Personal check 4 is not discharged by this record.** The registration's FREEZE
   section reserves it to the supervisor, and Amendment 1 §P1.5 states that a lane's
   amendment is not an authorisation to grade. This lane graded on the cfd-supervisor's
   dispatch and reports; **the acceptance of these verdicts is the supervisor's, not
   mine.**
7. **The §2 defect in `analyse_prd.py` is disclosed, not repaired.** No file on the
   grading path was modified by this record.

---

## 9 — FILES

- Verdict artifact: `verification/runs/navier_class/PRD/gate_prd_e1.json`
- Run tree, 15 cases: `verification/runs/navier_class/PRD/us{0.25,0.50,1.00,2.00,4.00}_L{1,2,3}/`
- Per-case completion + cost sidecars: `.../<case>/STATUS.<case>`, `.../DONE.<case>`
- Δp source artifacts: `.../<case>/postProcessing/dp_{inlet,outlet}_plane/0/surfaceFieldValue.dat`
- y+ artifacts (produced by this grading run): `.../us*_L3/log.yPlus`
- Registration: `verification/campaign/PRD_E1_PREREGISTRATION.md` (frozen body blob `65dc8643…`)
- Gate ruling: `verification/campaign/PRD_E1_GATE_RULING_2026-09-09.md`
- Earlier watch that correctly refused to grade: `verification/runs/navier_class/PRD/autograde_prd.watch.log`

**SUBMISSIONS PARKED.** Nothing here is sent, filed or registered anywhere outside this box.

*— cfd `lab-lane`, 2026-09-12.*

---

# ADDENDUM 1 — 2026-09-12 — THE ABSENT VISIBILITY PAIR IS EXECUTED RATHER THAN EXPLAINED

**Dated addendum appended at the foot. Version: v1.0 → v1.1.**
**`lines whose number changed above this section: 0`** — the 391 lines above are
byte-identical to the blob committed at `5b494e4bd`, and the proof is a hash, not an
assurance: `head -n 391 <this file> | sha256sum` =
`ec4bc8a7ea8b75640b55e53d26519a4d88ea2df507b6fd867fdd9110deeda9e2`, equal to
`git show 5b494e4bd:verification/campaign/PRD_E1_FINE_GRID_RESULTS.md | sha256sum`.
Re-runnable by anyone.

**This addendum alters NO gate, threshold, band, cap or label.** `G-ERGUN` stays ±3 %,
`G-ASYMP` stays ±1.5 %, `Fs` stays 1.25, the five Ergun targets are untouched, and **the
registered verdict stays 0 of 5 PASS, `credential = false`.** It executes one registered
control that §6 recorded as **absent**, and it records what that execution showed.

**Why.** §6 of this record stated that `visibility_pair = null` at every `U_s` because no
INERT (`D = f = 0`) case exists in the run tree — **one registered control of three ran
for the graded ladder** — and priced the closure at one coarse solve, about 2 core-min.
The cfd-supervisor accepted the record and directed that the control be run rather than
explained, on the ground that an explanation is only good until someone cheap can just
run it. **That is right, and the reasoning in §6 is not retracted:** the pair guards
against trusting a *zero* from a reader never shown able to see a non-zero, and the gated
quantity is a large non-zero whose plant control positively demonstrated sensitivity.
This is a registered control being **executed**, not a broken result being repaired.

## A.1 — THE PREDICTION, WRITTEN AND COMMITTED BEFORE THE SOLVER STARTS

**Committed before any compute for this control. The run directory
`verification/runs/navier_class/PRD/us4.00_L1_INERT/` does not exist at the moment of
this commit — that is the condition, and it is checked, not asserted.**

**The case.** `build_prd.py --emit --level L1 --us 4.0 --inert` — the **frozen builder**,
whose `fv_options(active=False)` sets `d = f = (0, 0, 0)`; identical geometry, mesh,
boundary conditions, turbulence model, solver settings and `endTime` 3000 to the graded
`us4.00_L1`, differing **only** in the two porosity coefficients. Launched by the frozen
`run_prd.sh` (blob `356ab36e…`, worktree == `HEAD:`), serial, 1 rank. `U_s = 4.00` chosen
because it is the point where the porous term contributes most — 94 % inertial — so it is
the widest separation the pair can be asked to resolve.

**The registered criterion is NOT chosen now. It is frozen.** `analyse_prd.py` carries
`INERT_DP_MAX_PA = 1.0` and `visibility_pair()` passes only when
`|Δp_inert| < 1.0 Pa` **and** `Δp_active > 1.0 Pa`, both read through the same
`read_dp_pa` in the same grading invocation. That constant was committed at the freeze,
before any PRD compute, and this addendum does not touch it.

**My physical prediction, which is new and is therefore stated so it can lose.** The
inert duct still has wall friction and a developing boundary layer between the two
measurement planes, so **the falsifier is not "exactly zero".** Between `x = 0.200 m` and
`x = 0.300 m` — one hydraulic diameter of smooth square duct at
`Re_Dh = U·D_h/ν = 4 × 0.1 / 1.5e-5 = 26,667` — the fully-developed Blasius estimate is

  `Δp = f_D · (L/D_h) · ½ρU² = 0.316·Re^(−1/4) × 1.0 × 0.5 × 1.2 × 16 = 0.02473 × 9.6 = 0.237 Pa`,

about 10 % lower for a square section than the circular correlation, and **higher** than
fully-developed here because at 2–3 `D_h` from a uniform inlet the boundary layer is thin,
the wall shear is above its asymptote, and the accelerating core adds a profile-change
term. **Predicted `Δp_inert` ∈ [0.15, 0.90] Pa, positive** (pressure falling downstream),
centred near 0.25 Pa.

**WHAT RESULT WOULD HAVE FAILED THIS TEST — each branch, and what it would mean:**

| observed | frozen pair | meaning |
|---|---|---|
| `|Δp_inert| ≥ 1.0 Pa` | **FAILS** | the sink is not actually inert — `fvOptions` not disabled, or the cellZone still resisting — or the reader is on the wrong case |
| `Δp_inert` within two orders of 11171 Pa | **FAILS** | catastrophic: the reader is reading the ACTIVE case's artifacts |
| `Δp_inert < 0` beyond solver noise | **FAILS** the physics | pressure rising across the core: a sign error in `dp_pa`, or the two plane faceZones swapped |
| `Δp_active ≤ 1.0 Pa` | **FAILS** | the active arm cannot see a non-zero, which is the whole licence the pair provides |
| `Δp_inert` **exactly** 0.000000 with both plane samples non-zero | frozen arithmetic **passes** | **and I would report it as a FAILURE anyway.** A real duct with wall friction cannot produce an exact zero; an exact zero would mean the two plane samples are the same value or the same file. `read_dp_pa` refuses only when **both** planes read 0.0, so this branch slips past the frozen guard and is caught here by the prediction instead |
| `Δp_inert` outside [0.15, 0.90] Pa but under 1.0 Pa | frozen pair **passes** | **my physics estimate loses and is reported as a miss**, separately, and the control's pass is not allowed to hide it |

**Cost, pre-registered (rule 12).** POINT **2.9 core-min** (anchored on the measured
2.833 core-min of the ACTIVE `us4.00_L1`, same mesh, same iteration count, one rank);
**CAP 10 core-min**, wall timeout 900 s. An overrun **stops the run**. Under the $25
pre-authorisation; **$0.0025 DERIVED, NEVER MEASURED** at $0.0513/core-h. Box at launch:
load average 55.41 on 16 vCPU, driven by heat-transfer's `splitMeshRegions` and dafoam's
8-rank A3GC — **neither of them ours and neither touched**; one serial 18,432-cell solve
is small enough to proceed and is held to one rank.

*A.2 — the result — is appended after the run, in its own commit.*

## A.2 — THE RESULT: THE PAIR PASSES, AND THE PHYSICS PREDICTION WINS TOO

**`lines whose number changed above this section: 0`** — lines 1–473 are byte-identical
to the blob committed at `6c26de967`, `sha256 =
c2e81f91d7aee3927703d797589e32660e8a2031ea558434c3d762db002c0865` on both sides. The
prediction in A.1 was committed **before** the solver started and is not edited here.

### A.2.1 — Rule-4 completion of the inert run, limb by limb

Case `us4.00_L1_INERT`, 18,432 cells, serial 1 rank, `started_utc 2026-09-12T00:50:36Z`,
`ended_utc 2026-09-12T00:52:27Z`.

| limb | value |
|---|---|
| rc | **0** (`note=clean`, `capped=no`) |
| `End` line | 1 |
| last `Time` | 3000 == `endTime` 3000 |
| `deltaT` | 1 → `ExecutionTime` count **3000** == `round(endTime/deltaT)` |
| fields at `3000` | **U p k omega nut phi** — the registered incompressible set |
| age guard vs `0/U` | oldest field `1789174347` > `0/U` `1789174238` → **OK** |
| frozen `mark_done_prd.py` | **DONE**, rc 0 |
| `blockMesh` / `topoSet` / `checkMesh` rc | 0 / 0 / 0 |

**COMPLETE on every limb.**

### A.2.2 — The measured pair

Read through the frozen `analyse_prd.read_dp_pa` — the same reader, the same ×ρ Pa
conversion, in the same grading invocation as the active arm:

| arm | Δp [Pa] | plane samples (kinematic) |
|---|---|---|
| **INERT** `us4.00_L1_INERT` (`d = f = 0`) | **0.335506535** | `p_in` 0.743542838, `p_out` 0.463954059 |
| **ACTIVE** `us4.00_L1` | **11158.478737476** | `p_in` 9299.449650000, `p_out` 0.717368770 |
| ACTIVE at the fine level `us4.00_L3` | 11171.091991 | (the value `visibility_pair` is given in `gate_prd_e1.json`) |

> **`visibility_pair` → `passed = True`.** `|Δp_inert| = 0.3355 Pa < INERT_DP_MAX_PA = 1.0`
> **and** `Δp_active = 11171.09 Pa > 1.0`. **The registered control set of §6 is now
> fully executed: all three controls of the registration's §6 have fired and passed.**

The separation is a factor of **33,293**. The same reader, on the same day, through the
same code path, reported a number four and a half decades apart on two cases that differ
**only** in two coefficients. That is precisely the licence the pair exists to grant: the
reader has been shown able to see both a near-zero and a large non-zero.

### A.2.3 — The physics prediction is scored, and it wins — but it could have lost

A.1 predicted `Δp_inert ∈ [0.15, 0.90] Pa`, positive, centred near 0.25. **Measured
0.3355 Pa: inside the band, positive, and 1.41× the Blasius fully-developed floor of
0.237 Pa** — the right direction and about the right magnitude for a thin developing
boundary layer 2–3 `D_h` from a uniform inlet, which is the mechanism A.1 named in
advance.

**This is scored separately from the control's pass, exactly as registered, because the
two could have disagreed.** Had the inert Δp landed at, say, 0.05 Pa it would have been
comfortably under the frozen 1.0 Pa limit — the control would still have passed — and my
physical estimate would have lost. Reporting only "the pair passed" would have hidden
that. None of the six failing branches in A.1 fired.

### A.2.4 — A GUARD WITH A HOLE IN THE SHAPE OF THE THING IT GUARDS AGAINST

**This finding stands independently of tonight's number and outlives this rung.**

A.1's fifth branch registered it before the run and the run did not exercise it, so it is
recorded on its own merits. The frozen `read_dp_pa` refuses a reader-wired-to-nothing
like this:

```
    if p_in == 0.0 and p_out == 0.0:
        refuse("... both plane samples read a PERFECT 0.0. A zero from a reader "
               "not shown able to see a non-zero is not evidence (rule 3).")
```

It refuses only when **both** planes read exactly zero. But the gated quantity is the
**difference**, and `visibility_pair` is handed that difference. **A case whose two
planes read equal non-zero values yields `Δp = 0.000000` exactly, passes the perfect-zero
guard (neither plane is zero), and passes `visibility_pair` (0.0 < 1.0).** The one
configuration that would prove a reader cannot resolve a difference is the one
configuration that slips through the guard built to catch exactly that.

**It was caught here by a physical prediction, not by the guard** — and that is the
carryable lesson: **an arithmetic guard on a computed difference cannot substitute for
knowing what the physical answer must look like.** A real duct with wall friction cannot
produce an exact zero, and only the physics says so.

**The frozen reader is NOT edited.** It is frozen, and the repair is this disclosure plus
a docket item, not a change. Referred to verification and to the supervisor. **Nothing in
this record depends on the hole**, because the measured inert Δp is 0.3355 Pa and not
zero.

### A.2.5 — The grade re-run, and what did NOT move

The frozen `autograde_prd.py --grade` was re-run with the inert case present.
`verification/runs/navier_class/PRD/gate_prd_e1.json` now carries
`visibility_pair` for `U_s = 4.00`. **Every verdict and every `dp_by_level` value is
byte-identical to the previous grade**, checked field by field rather than assumed:

> **The registered result is UNCHANGED: 0 of 5 `U_s` PASS, all five `NOT A RESULT`,
> `credential = false`.** The three fine-grid `G-ERGUN` PASS rows of §4 are unchanged.
> **This addendum moved no gate, threshold, band, cap or label, and it moved no verdict.**

`visibility_pair` remains `null` at `U_s` = 0.25, 0.50, 1.00 and 2.00 — one inert case was
built, at 4.00, and the other four points are honestly still without one. **What the
single inert case does and does not license:** it licenses the *reader*, which is shared
across all five `U_s` and all three levels, and that is the object the control is about.
It does **not** claim a per-`U_s` inert measurement that was not made.

### A.2.6 — Cost of this addendum (rule 12)

| item | core-min | note |
|---|---|---|
| inert solve `us4.00_L1_INERT` | **1.850** MEASURED | `wall_s` 111 × 1 rank ÷ 60, from its own `STATUS` sidecar; `capped=no` against the 900 s timeout and the 15.000 core-min cap the launcher recorded |
| re-grade (`autograde_prd.py --grade`) | **0.333** MEASURED | 20 wall s × 1 rank; the y+ logs already existed, so no `postProcess` re-ran |
| **total** | **2.183** | = 0.0364 core-h = **$0.0019 DERIVED, NEVER MEASURED** at $0.0513/core-h |

**Against the A.1 POINT of 2.9 core-min: ratio 0.638 — 36 % UNDER, and that is a MISS,
reported as one.** The anchor was the ACTIVE `us4.00_L1`'s measured 2.833 core-min on the
identical mesh and iteration count. The inert case ran **1.53× faster** for the same work,
and the cause is named rather than left as slop: **with `d = f = 0` the momentum equation
loses a large implicit diagonal source, and the linear systems the same 3000 SIMPLE
iterations produce are easier** — the porous sink is not free, and the active case was
paying for it. Anchoring an inert run on an active run of the same size over-prices it by
about half again. Box load at launch was 55.41 on 16 vCPU, i.e. **contention pushed the
actual UP**, so removing it would make the under-run **larger**, not smaller — contention
is ruled out by direction and is not the explanation. **No cap approached, no overrun, no
stop. Waste 0.000 core-min**, named separately per `COMPUTE_BUDGET_CHARTER.md` §6: the run
that produced the control is the run that was needed.

*Addendum 1 ends. Nothing above line 473 was edited; A.2's opening proves it by hash.*
