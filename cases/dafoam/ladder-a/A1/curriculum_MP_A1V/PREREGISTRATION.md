**FROZEN 2026-09-07 — this commit is the freeze.** Every gate, threshold, cap, band, step and label
below is bound as of this commit (`CLAUDE.md` rule 2) and cannot move; the grading path is hash-locked
by `mpa1v_INSTRUMENT_MD5_TABLE.md` (grader `0a41208e…`). The freeze DECISION and its attribution are the
dafoam-supervisor's (aa9d27fdd1bd4b695), taken after their §3 check-1 on the instrument diffs and the
L-504 pre-freeze checklist (§7 FREEZE RECORD); the mechanical freeze commit is executed by the authoring
lane on the supervisor's explicit go. **No agent message is Sanaa's consent** (rule 9): the compute is
under Sanaa's standing <$25 pre-authorisation (2026-08-21) and the detached-launch permission `bc0e687e`
(Sanaa-boarded). **NOTHING IS FILED, SENT, UPLOADED OR POSTED.** SUBMISSIONS PARKED (rule 7). Authoring
lane: dafoam `lab-lane`; territory `cases/dafoam/ladder-a/A1/`. The §6 open decisions were RULED by the
dafoam-supervisor and are folded in below; the §0.2 premise correction was VERIFIED at source by the
supervisor and adopted throughout.

# CURRICULUM MP-A1V — MP-A1 GRADIENT FD-VERIFICATION SUCCESSOR, BY **DIRECT DESIGN-VARIABLE CENTRAL DIFFERENCE** OVER A 3-MEMBER DV SET, RIDING THE DEMONSTRATED FINAL DESIGN **AND ITS FROZEN ADJOINT**, BOTH TOOLCHAIN ROWS, np = 1. PRE-REGISTRATION (FROZEN 2026-09-07)

**Item id:** `CURRICULUM-MP-A1V`
**Run root (registered, MUST BE ABSENT at freeze):** `/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1V-a1-naca0012-multipoint-fixedlift-fdverify-directDVcentral` — **verified ABSENT at authoring**.
**Case directory:** `cases/dafoam/ladder-a/A1/curriculum_MP_A1V/`
**Predecessor of record:** `CURRICULUM-MP-A1` — graded **NOT A RESULT** on both rows (`/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1-a1-naca0012-alpha-multipoint-fixedlift-optimisation/MPA1_grade_20260907T163958Z.json`).
**Disposition rung:** `VERIFICATION_CHARTER.md` §2ay state **(b)** — the recovering successor (§2ay.3: a defect diagnosed to a mechanism is the FIRST RUNG of state (b), not an entry to "proven unrecoverable").

---

## §0. WHAT MP-A1 ESTABLISHED, AND THE ONE THING IT COULD NOT

### 0.1 The optimisation is DEMONSTRATED and SUCCEEDED on both rows (measured)
From `MPA1_grade_20260907T163958Z.json`: IPOPT **`Optimal Solution Found.`** both rows (SHIPPED 13 majors, PATCHED 17, `converged_to_optimizer_tolerance = true`); `G-CLHOLD` PASS both rows (each `|CLᵢ,final − target|` ≤ 3.4e-07 ≪ `TOL_CL_ABS = 1e-3`, all `CLᵢ > 0`); `G-DRAG` PASS both rows (`J: 0.02180598 → 0.02071194`, **≈ 5.017 %** weighted-drag reduction at HELD lift). **MP-A1V does not re-run and does not re-establish any of this — it rides the frozen final design `mpa1_xopt.json` AND MP-A1's frozen adjoint `mpa1_X.json` at that design (supervisor ruling O-1).**

### 0.2 The ONE reason MP-A1 is NOT A RESULT — and the premise the supervisor verified
The DAFoam bright line (`DAFOAM_CHARTER.md` §2: *a gradient is not a result until an FD table stands beside it*) forces NOT A RESULT because no completeable FD table stands beside the adjoint, for two distinct, both-measured mechanisms:

1. **Forward-mode duality path fails the primal (gate `G6` = NOT MEASURED, both rows).** Grade JSON, verbatim: *"AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on BOTH images."*
2. **The MP-A1 FD table lost 2 of 34 evaluations per F arm (gates `G5J`/`G5C` = NOT A RESULT).** The two failures (`FE-S/mpa1_F.json` `evaluation_failures`) are **`FD shape[3]+0.01`** and **`FD shape[6]+0.01`**, each `AnalysisError("'point2.coupling.solver' ... Primal solution failed!")` — the **largest step (`+1e-2`) diverged the primal at the highest-α point (point2, α = 7.139°)** for `shape[3]` and `shape[6]`. MP-A1's grader requires the **whole** ladder `[1e-2,1e-3,1e-4]` present per pair, so a single failed step excluded those pairs → **2 graded < min 3 → NOT A RESULT**.

**⚠ THE PREMISE CORRECTION, VERIFIED AT SOURCE BY THE SUPERVISOR AND BINDING ON THIS RECORD.** MP-A1's F arm is **ALREADY a direct-DV central difference** (`FE-S/mpa1_F.json` rows carry `plus`/`minus`, `d = (plus − minus)/(2h)`). So **"switch to central difference" is NOT the fix — MP-A1 was central already.** The two honest levers are:
* **(i) Drop the non-functional forward-mode duality path (G6 / AV-2).** The charter bright line requires an **FD table** beside the adjoint, **not** a forward-mode dot-product test — so removing the forward-mode limb **weakens nothing** the charter requires. The forward-mode limitation remains a measured fact and travels (§5); MP-A1V *avoids* it, does not repair it.
* **(ii) Re-size the ladder below the divergent `1e-2` step and adopt the D6RF7-lineage clearance/ratio plateau selector**, so a single primal-diverging coarse step no longer disqualifies the whole verification.

### 0.3 The IDWarp regime dependence MP-A1's grader flagged
`G-OPT9.design_change_note`, verbatim: *"A gradient verified at iteration 0 is not verified at the optimum: the IDWarp rotation defect fires at the undeformed baseline and behaves differently just above threshold (1e-5 rad → 4.1e-08, 1e-6 → 6.7e-05, 5e-8 → 1.2e-02) …"* MP-A1V does the FD **at the ridden final design** (charter §9) and includes a clean interior representative DV clear of the LE/TE branch corners (§1.4).

---

## §1. THE ITEM AS REGISTERED (SUPERVISOR-RULED)

### 1.1 Frame — MULTIPOINT, unchanged; NEITHER the optimisation NOR the adjoint is re-run
Three operating points α = {3.139, 5.139, 7.139}°, equal weights 1/3, `J = Σᵢ wᵢ·CDᵢ`, one shared 8-component `shape` FFD DV, np = 1, `DASimpleFoam` incompressible — carried byte-identical from MP-A1. **MP-A1V registers NO optimisation arm and NO adjoint arm.** It rides:
* the demonstrated final design `mpa1_xopt.json` (per row), applied by `-xopt`; and
* MP-A1's **frozen adjoint** `mpa1_X.json` (SHIPPED `XE-S/`, PATCHED `XE-P/`), which carries the **full 8-component** gradient `d{J, CD_i, CL_i}/d(shape)` at that identical design point (verified present on disk).

`G-DESIGNPOINT` asserts the ridden `mpa1_xopt.json` sha256 the FD arm evaluates at **equals** the design point MP-A1's adjoint was taken at (both artefacts carry `design_point_record`), so the comparison is adjoint-vs-FD **at one point**, not across two designs.

### 1.2 The lever — DIRECT DESIGN-VARIABLE CENTRAL DIFFERENCE
At `x = x_opt`, for each registered member `shape[k]` (§1.4): `d(Q)/d(shape[k]) ≈ (Q(x_opt + h·e_k) − Q(x_opt − h·e_k))/(2h)`, `Q ∈ {J, CL0, CL1, CL2}`, each `Q(x_opt ± h·e_k)` from **setting the real DV** and running the **ordinary multipoint primal** (no tangent-linear seed) then post-processing. Compared to MP-A1's frozen adjoint at `x_opt`.
* **Why it sidesteps AV-2:** the direct-DV path never seeds the forward mode — the exact `solve_linear`-forward / duality path AV-2 measured to crash the primal is not exercised (§0.2 lever i).
* **Why it recovers from the 2/34 loss:** the ladder (§1.5) lies below the measured-divergent `1e-2`; the clearance/ratio selector (§1.6) grades the plateau-selected step pair rather than a fixed full ladder (§0.2 lever ii).

### 1.3 The arm program — THREE arms (`N_DECLARED = 3`)
| arm | row | kind | terminal statement |
|---|---|---|---|
| `MESH` | shared | `preProcessing.sh && checkMesh` | — |
| `FV-S` | SHIPPED | **direct-DV central-difference** table at the ridden `x_opt` (SHIPPED) | `MPA1V_F_WRITTEN` |
| `FV-P` | PATCHED | **direct-DV central-difference** table at the ridden `x_opt` (PATCHED) | `MPA1V_F_WRITTEN` |

Both rows always run (`DAFOAM_CHARTER.md` §6). No `O` arm (ride `mpa1_xopt.json`), no `X` arm (ride `mpa1_X.json`) — supervisor ruling O-1.

### 1.4 The DV SET — THREE MEMBERS, registered a priori, NO SUBSTITUTION (supervisor ruling O-2)
`COMPONENTS = { shape[3], shape[6], shape[2] }`. **The `FFD → shape` map is now READ** (`mpa1_runScript.py:453-462`) and the members are pinned by it. The 8 shape functions map: an interior loop `for i in (1,2,3): for j in (0,1)` builds `shape[0..5]`, then an LE/TE loop `for i in (0,4)` builds `shape[6]=LE`, `shape[7]=TE`. Chordwise stations are **x = {−0.010 (i=0, LE), 0.245 (i=1), 0.500 (i=2, MID), 0.755 (i=3), 1.010 (i=4, TE)}**. Therefore:

| member | (i, j) | chordwise x | position | role |
|---|---|---|---|---|
| **`shape[3]`** | (i=2, j=1) | **0.500** | **mid-chord interior** | fragile: FD diverged at 1e-2 (point2). NOT branch-adjacent — its divergence is high-α large-step primal robustness, not branch geometry |
| **`shape[6]`** | LE (i=0) | **−0.010** | **AT the LE branch corner** | fragile: FD diverged at 1e-2 (point2). Branch-adjacent — sits exactly where `getRotationMatrix3d`'s degenerate branch fires |
| **`shape[2]`** (`k_clean`) | (i=2, j=0) | **0.500** | **mid-chord interior, max-distant from LE/TE** | the clean representative — the j=0 partner of the fragile `shape[3]`, maximally distant from both branch corners |

**Report the supervisor asked for (delivered):** `shape[3]` is mid-chord interior (branch-clear); `shape[6]` is the LE shape function, **branch-adjacent** — the coarse-step divergence of `shape[6]` is consistent with the IDWarp rotation defect, while `shape[3]`'s is a high-α large-step effect. `k_clean` is pinned to **`shape[2]`** by the mid-chord geometric criterion (**not** by any MP-A1 FD agreement); MP-A1's frozen adjoint carries a strong non-zero sensitivity there (`CL0` adjoint at `shape[2]` = 1.126), so it clears NEAR_ZERO — **corroborating, not determining**, the geometric pick.
* **NEAR_ZERO (charter §3):** if **any** member's ridden **adjoint** at `x_opt` fails the clearance floor (`|d_ref|·s/η < CLEARANCE_FLOOR` at every ladder step), that member's row is **NOT A RESULT** and a further successor re-registers a different component — the member is **never** re-chosen after seeing which agrees.

### 1.5 The step ladder `[H-SET]` — re-sized from MP-A1's MEASURED divergence threshold
`LADDER["shape"] = {1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3}` — four steps, **all strictly below** MP-A1's measured-divergent `1.0e-2` and **above** the measured repeatability floor `η ≈ 2.21e-08` (`FE-S/mpa1_F.json` `eta_raw`). Sizing an **instrument parameter** from the predecessor's *measured* divergence threshold is the lineage practice (D6RF7 §10.2). `TB_STEP = 1.0e-8` (charter §4 trivial baseline, at/below `η`; must fail band).

### 1.6 The plateau selector — D6RF7-lineage clearance/ratio, PINNED
The selector is imported from the D6RF7 lineage (`d6rf7_fd_endpoint.py:86-88, 419-434`; `d6rf7_grade.py:2279-2352`) to **replace** MP-A1's rigid full-ladder `_pair`, so a single divergent or below-clearance step no longer disqualifies the member. Algorithm, per member, per quantity, over the ladder (§1.5) with `η` = the F-arm's own **measured** `eta_raw`:
* **clearance** per step: `C(s) = |d_ref|·s / η` (predicted FD signal over noise, using the ridden adjoint `d_ref`); `usable = { s : C(s) ≥ CLEARANCE_FLOOR AND the FD step evaluated ok }`. Empty `usable` → **NO_CLEARANCE → Branch B** (this is the NEAR_ZERO case for that member).
* `s_lo = min(usable)`; `hi = { s ∈ usable : s ≥ RATIO_MIN·s_lo }`; empty `hi` → **NO_S_HI → Branch B**; else `s_hi = min(hi)`.
* graded **at `s_hi`** (D6RF7 one-sided-fine convention, coarse side stated): `rel_err_pct = |d(s_hi) − d_ref| / |d(s_hi)|·100`; `plateau_pct = |d(s_hi) − d(s_lo)| / |d(s_hi)|·100`; `sign_flip = d(s_hi)·d_ref < 0`; **PASS iff `rel_err_pct ≤ FD_BAND_PCT` AND `plateau_pct ≤ PLATEAU_TOL` AND not sign_flip**, else GATE FAIL.

**PINNED CONSTANTS — carried from the D6RF7 frozen lineage, a-priori, NOT tuned to any MP-A1V answer:**
| constant | value | source / why it transfers |
|---|---|---|
| `CLEARANCE_FLOOR` | **5.0** | D6RF7 byte. Requires the predicted FD signal to exceed the measured repeatability floor `η` by 5×. With MP-A1's measured `η ≈ 2.21e-08` and the ridden adjoints (`|J_adj|~5e-3`, `|CL_adj|~1`), every ladder step `≥1e-4` clears comfortably — the floor is a **noise guard**, not a tuned threshold. |
| `RATIO_MIN` | **2.0** | D6RF7 byte. Forces `s_hi ≥ 2·s_lo` so the plateau pair spans a real factor-2 in step; dimensionless, case-independent. |
| `PLATEAU_TOL` | **10.0 %** | D6RF7 byte = `VERIFICATION_CHARTER.md` §7 plateau tolerance, the SAME value MP-A1 used (`PLATEAU_TOL_PCT = 10.0`). Charter-anchored, not re-derived. |
| `FD_BAND_PCT` | **5.0 %** | charter §2 / VERIFICATION §7 band D/E, unchanged from MP-A1. |
| `η` | **F-arm `eta_raw`** (MEASURED) | the operative repeatability floor is the run's own measured two-baseline `eta_raw` (MP-A1's was `2.213211985901964e-08`); `ETA_FLOOR = 1e-14` only if `eta_raw` underflows. |

**Why they transfer:** none of these is fit to a target — `CLEARANCE_FLOOR`/`RATIO_MIN` are dimensionless signal/noise and step-spacing guards, `PLATEAU_TOL`/`FD_BAND_PCT` are charter bands MP-A1 already carried, and `η` is measured per run. A member with **no** clearance-and-ratio-satisfying plateau pair at any step **≤ 3e-3** is Branch B (§2.1).

**⚠ MECHANISM vs VERDICT — binding on all framing.** The selector was exercised on MP-A1's *own* frozen data (a dry-run on the overlapping steps 1e-4/1e-3, independently reproduced by the supervisor) and shape[3]/shape[6] agreed with the ridden adjoint to 0.003–0.78 %. **That dry-run validates the selector MECHANISM only — it is NOT the verdict.** The dry-run's plateau pair is (1e-4, 1e-3); the fresh 4-step ladder selects (1e-4, 3e-4), so the graded VERDICT can come **only** from the fresh MP-A1V run at the registered ladder. No record (prereg, RESULTS, report) may state the dry-run numbers as the MP-A1V verdict.

### 1.7 np and toolchain
np = 1 every arm (charter §5). Both rows under their frozen images (`libidwarp.so` md5 `f0fcb488…` SHIPPED / `85f59e87…` PATCHED), asserted from inside the container (`G9`). cpuset PROVISIONAL (ruling O-3); re-read live occupancy and pin disjoint at freeze; `G12` gates it.

---

## §2. GATES, THRESHOLDS AND LABELS — SIX-TOKEN VOCABULARY ONLY

| gate | reads | threshold | verdict on miss |
|---|---|---|---|
| `G1_completion` | per arm: rc = 0, terminal statement, no fatal token, **age guard** (fields newer than the case's own `0/U`; run root ABSENT at cold start) | all of it | `GATE FAIL` |
| `G-M2` | mesh cell count | **4032** exactly | `GATE FAIL` |
| `G-ALPHA` | the three α read back | §1.1 to **1e-12** | `GATE FAIL` |
| `G-DESIGNPOINT` | FD `x_opt` sha256 == ridden adjoint's design point (`mpa1_X.json` `design_point_record`) | exact | `GATE FAIL` |
| `G-NOOPT` | no optimiser, no adjoint solve, ran in MP-A1V (both ridden) | zero such evidence | `GATE FAIL` |
| `G-CLEAR` (per row, per member, per Q) | ridden adjoint magnitude clears `η` | `\|d_ref\| ≥ 5.0·η` | **NEAR_ZERO → NOT A RESULT** (member), no substitution |
| **`G-FDCD`** (per row, per member ∈ {shape[3], shape[6], shape[k_clean]}, per Q ∈ {J, CL0, CL1, CL2}) | central-diff vs **ridden adjoint** at the plateau-selected step | agreement **≤ 5.0 %** (charter §2 band D/E) AND a step plateaus (`PLATEAU_TOL = 10 %`) AND no sign flip | `GATE FAIL` (out of band); no plateau / sign flip → `NOT A RESULT` (member) |
| `G-TB` (per row, per member, per Q) | same probe at `TB_STEP = 1e-8` | PASS iff it **fails** band there | passes band → that member's `G-FDCD` **WITHDRAWN to NOT A RESULT** |
| `G-CLHOLD` (per row) | each `CLᵢ` at the ridden design (FD baseline) | `\|CLᵢ − target\| ≤ 1e-3` AND `CLᵢ > 0` | `GATE FAIL` (re-confirmed at ridden design) |
| `G-DRAG` (per row) | `J_final` (FD baseline) vs `J_baseline` | `J_final < J_baseline` | `GATE FAIL` (re-confirmed; magnitude reported, never gated) |
| `G-OPT9` (per row) | **carried** from MP-A1's frozen grade (`Optimal Solution Found.`) | carried PASS-eligibility | carried label |
| `G-EVALFAIL` | per FD arm: declared vs failed evaluations | reported (a failed eval is gradable) | census input; feeds §2.1 fork |
| `G9` / `G10` / `G12` / `G-STAGES` (=3) / `G-PROV` | toolchain / caps / cpuset / declared-vs-executed / travelling SO-3aR2·SO-1a `GATE FAIL` chain | as MP-A1 | `GATE FAIL` / `NOT A RESULT` / refusal exit 2 |

**No GCI / Roache triple** — single-grid verification.

### 2.1 THE GATE FORK — PER MEMBER (supervisor ruling)
* **Branch A — a member RECOVERS.** For a member: plateau-proved, in-band (5 %), no-sign-flip agreement of the **frozen adjoint** vs the direct-DV central difference, with `G-TB` failing its band, **for `J` and each `CLᵢ`** → that member's `G-FDCD = PASS`.
* **Branch B — a member ALSO fails.** If a member cannot form a **completeable plateau table at any step ≤ 3e-3** (every candidate step diverges the primal at some operating point; or no pair plateaus; or `η` never cleared) → that member is a **MEASURED** verification-limitation finding, composed only from the measured census (`G-EVALFAIL`, per-step `ok`, primal-divergence tags), **REPORTED never asserted** — never "the gradient is wrong", only "the gradient could not be FD-verified at this member".

### 2.2 Item verdict composition (registered before the run)
1. `G-STAGES = NOT A RESULT`, or `G-PROV` refusal → as stated.
2. Any of `{G-M2, G-ALPHA, G-DESIGNPOINT, G-NOOPT, G9, G10, G12}` = `GATE FAIL` → **`GATE FAIL`**.
3. Any member `G-CLEAR = NEAR_ZERO`, or `G-FDCD = NOT A RESULT` / `G-TB` withdrawal / Branch B is the binding obstacle → **`NOT A RESULT`** (Branch-B measured finding attached for that member).
4. Any member `G-FDCD = GATE FAIL` (out of band), or `G-CLHOLD`/`G-DRAG` re-confirmation = `GATE FAIL` → **`GATE FAIL`**.
5. **Otherwise — ALL three members PASS on both rows, with `G-CLHOLD`/`G-DRAG` re-confirmed and `G-PROV` travelling** → **`PASS`**: MP-A1's FD-verification NOT A RESULT is lifted and the multipoint drag-min-at-fixed-lift stands VERIFIED **on the patched toolchain only** (§5).

### 2.3 Controls (carried from MP-A1, registered before compute)
Planted-zero (rule 3) on the FD reader and on the **ridden-adjoint** reader (`plantᵢ = PLANT_K·(band/100)·|d_ref|`, `PLANT_K = 3.0`, separate copy under `grader_controls/`, must flip `G-FDCD`; proven sufficient by `PLANT_K_INSUFF = 0.2`; birth register). Strict completion + age guard (rule 4).

---

## §3. WHAT MP-A1V MAY NOT CONCLUDE
Absolute lift-neutral-drag claim (SO-3aR2/SO-1a `GATE FAIL` travels, `G-PROV`; only *"on the patched toolchain `dafoam-idwarp-rot:v1`, …"*); a sub-floor verification (2.5–5 % harness floor, VERIFICATION §7); anything at np ≠ 1; a grid-converged optimum; absence of the IDWarp defect; a compressible/transonic or aoa-trimmed result. **Branch B is a verification-capability limitation, NOT a statement that the gradient is wrong.** It may not re-establish MP-A1's optimisation, `G-CLHOLD` or `G-DRAG` as new results.

---

## §4. COST — CORE-MINUTES (3-MEMBER SET, RIDE ADJOINT + OPTIMISATION)

Unit core-minutes (wall s × ranks ÷ 60), np = 1, **1 rank per arm** (`CLAUDE.md` rule 12).

### 4.1 Evaluation count per FD arm (3 members, 4-step ladder)
```
ladder:   3 members × 4 steps × 2 sides = 24 multipoint evaluations
TB:       3 members × 1 step  × 2 sides =  6
baseline: baseline + baseline_repeat    =  2
                                   total = 32 multipoint evaluations per FD arm
```
(MP-A1's F arm was 34: 4 members × 3 steps × 2 + 8 TB + 2.) Each evaluation is a 3-point multipoint solve.

### 4.2 Per-evaluation cost — MEASURED from MP-A1 (`arm_census`)
`FE-S = 5.05` core-min / 34 = **0.1485 core-min/eval**; `FE-P = 6.3` / 34 = **0.1853 core-min/eval**; `MESH = 0.933` (MEASURED).

### 4.3 The per-leg cost table
| arm | ranks | **est core-min** | basis | **cap core-min** |
|---|---|---|---|---|
| `MESH` | 1 | 0.93 | MEASURED — MP-A1 MESH 0.933 | **5.0** (floor, carried) |
| `FV-S` | 1 | 4.75 | DERIVED — 32 evals × 0.1485 | **14.0** (carry MP-A1 FE cap; divergence headroom) |
| `FV-P` | 1 | 5.93 | DERIVED — 32 evals × 0.1853 | **14.0** |
| **item ESTIMATE** | | **11.61** | | |
| **ITEM CEILING = Σ(caps)** | | | | **33.0** |

**Item point estimate 11.61 core-min; ceiling 33.0 core-min (≈ 2.8× est).** An overrun STOPS the run; hard-stop per-arm at cap and at the ceiling.

### 4.4 Dollars — DERIVED, NOT MEASURED
At **$0.0513/core-h = $0.000855/core-min**, reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5):
* estimate: 11.61 × $0.000855 = **$0.0099**
* ceiling: 33.0 × $0.000855 = **$0.0282**

**Both far under the $25 pre-authorisation — confirmed.** GPU 0 GPU-h. Riding the adjoint (not re-running it) is what keeps this at 3 arms; re-running the adjoint would add ~5.24 core-min (the two `XV` arms) for no verification gain, and was ruled out (O-1).

### 4.5 Calibration at completion is owed (rule 12)
At completion the predicted-vs-actual comparison lands in `docs/COST_CALIBRATION.md`. Named quantities: the DERIVED per-eval rate (0.1485 / 0.1853), the 32-eval count (completed vs declared), and any waste (a diverging eval that hit its cap) named **separately**, never folded into the ratio.

---

## §5. WHAT TRAVELS
SO-3aR2 (`G5J` 31.5 % SHIPPED / 2.68 % PATCHED) / SO-1a is `GATE FAIL` and **travels** (`G-PROV`, carried from MP-A1 §2d) — the only licensed sentence is *"on the patched toolchain `dafoam-idwarp-rot:v1`, …"*. The forward-mode-AD limitation (AV-2) is a measured fact MP-A1V *avoids*, not repairs, and is reported as a standing capability limitation.

---

## §6. OPEN DECISIONS — RULED BY THE DAFOAM-SUPERVISOR (2026-09-07)
1. **O-1 — RIDE MP-A1's frozen adjoint** (`mpa1_X.json`) and final design; do NOT re-run adjoint or optimisation. Est 11.61 / ceiling 33.0. **RULED.**
2. **O-2 — SMALL DV SET of THREE**: `shape[3]`, `shape[6]` (the divergent components) + one clean interior representative (mid-chord, max distance from LE/TE branch). Pin `k_clean` and report where `shape[3]/shape[6]` sit at freeze against the FFD→shape map. NEAR_ZERO on any member → that member NOT A RESULT, no substitution. **RULED.**
3. **O-3 — cpuset** PROVISIONAL; pin disjoint at freeze; `G12` gates. **RULED.**
4. **Gate** — per-member PASS (plateau, in-band, no-sign-flip, J + each CLᵢ); item PASS only if ALL members PASS + `G-CLHOLD`/`G-DRAG` re-confirmed + `G-PROV` travels; a member with no completeable plateau at any step ≤ 3e-3 → Branch B measured finding; if that is the binding obstacle the item stays `NOT A RESULT` on the measured census. **RULED.**

---

**NOTHING IS FILED, SENT, UPLOADED OR POSTED. SUBMISSIONS PARKED.**

---

## §7. FREEZE RECORD — 2026-09-07, dafoam-supervisor (aa9d27fdd1bd4b695) deciding; mechanically committed by the authoring lane

This commit is the freeze. Every gate, threshold, band (FD 5.0 %, plateau 10.0 %, clearance 5.0,
ratio 2.0), cap (per-arm MESH 5.0 / FV-S 14.0 / FV-P 14.0; item ceiling 33.0 = Σcaps), the 3-member set
{shape[3], shape[6], shape[2]}, the ladder {3e-3,1e-3,3e-4,1e-4}, cpuset 12, the ride design and every
label are bound as of this commit and cannot move (rule 2). **No gate/threshold/cap/label moved between
the DRAFT and this freeze**; the only changes since check-1 were two stale-string reconciliations
(comment/usage strings) and the cpuset pin, none of which alters grading logic.

**The grading path is hash-locked** (`mpa1v_INSTRUMENT_MD5_TABLE.md`): `mpa1v_grade.py` md5
`0a41208ee834df2b413b944938587a67`, `mpa1v_xf.py` `ea53c04314f20c438de233101d5ce84d`,
`mpa1v_runScript.py` (the PRODUCER, staged as `mpa1_runScript.py`) `bb3ba3a61b19dc8564e247cdb11e9147`;
launcher `mpa1v_run_arm.sh` `eaf76e1b994f6209df784a82ed51c2cd`, driver `mpa1v_chain_driver.sh`
`96156dc58456eeece10ba3bee98c7454`; carries stall `5d112800…`, age_guard `7fe4352d…`, stop_marker
`5063f90b…`, aggregate_memory `709ab0b9…`, decomposeParDict `e6f1b006…`.

**L-504 PRE-FREEZE CHECKLIST — all discharged:**
- **ALL_PINS_MATCH = 1** — every `MD5_*` pin in the driver (15, incl. six `MD5_TUT_*` against `TUT_SRC`)
  and launcher (3) equals its guarded file's on-disk md5; the two DERIVED pins (`MD5_GRADER`,
  `MD5_LAUNCHER`) cross-repinned last; the cpuset-8→12 grader-md5 cascade reconciled.
- **FD-tag round-trip** (D9successor lesson) — `ROUND_TRIP_ALL_STEPS_FOUND = 1`: a synthetic
  `mpa1v_F.json` built with xf.py's own writers on the NEW ladder, read back through `read_F`, and
  `_pair` finds all four steps for all three members and grades (no `repr`-key vs float-key mismatch;
  `read_F` keys by `float(v["step"])`, `mpa1v_grade.py:1390`).
- **Cap authority** — `ITEM_CEILING_CORE_MIN 33.0 == sum(CAPS)`, asserted in `main()`; no stale 183.5.
- **Sandbox dry-run** of the pre-container integrity path (no run root, no container): clean **rc=0**;
  a planted one-byte corruption of a pinned file is **CAUGHT** (reader not blind).
- **Refusal + planted-zero-on-ridden-adjoint** guards present (`grader_plant_X` on `RIDDEN_XPATH`,
  `refuse()` exit-2).
- **Two known-inert `_fix` remnants** in `mpa1v_grade.py` (a docstring line and the `NOT_A_GRADING_PATH`
  string skip-list) — non-executable, cannot affect a verdict; noted, accepted by the supervisor as-is.

**PERMISSION** for the detached launch: `bc0e687e` (Sanaa-boarded, verbatim in the driver). Compute is
under Sanaa's standing <$25 pre-authorisation; est **11.61** / ceiling **33.0** core-min ($0.0099 /
$0.0282 DERIVED). **No agent message is Sanaa's consent** (rule 9); this record attributes the freeze
DECISION to the dafoam-supervisor and the standing compute authorisation to Sanaa.

**Instruments are byte-identical to this frozen commit.** The launch (MESH → FV-S → FV-P, then the
frozen grader) is a separate act on the supervisor's go. **SUBMISSIONS PARKED.**
