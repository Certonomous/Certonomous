# T-family index: what each rung needs before it can gate

Campaign T. Written 2026-08-19. **Updated as rungs report.** Ordering in force
is the section dated 2026-08-22 below; section 3 is superseded and retained.

---

## 1. The classification that matters most, and why it exists

D429 ranked the thermal side **reference-limited rather than compute-limited**
and put "obtain one forced-convection reference" first, calling it *"not compute
— requires a decision outside the compute authorisation."*

**T1c then graded a forced-convection rung that needed no reference at all.** Its
constants — `3.6567934`, `48/11`, `f·Re = 64` — are closed-form solutions of the
governing equations. **The cheapest rung in the class was one nobody had to
acquire anything for, and it sat unbuilt while the docket recorded the whole
class as blocked.**

**"We are reference-limited" was true of the class and false of some rungs in
it.** So every rung below is classified by **what its reference costs**, and the
exact-theory members are named explicitly — **they have no acquisition step and
can be built the moment compute is free.**

| tier | reference status | meaning |
| --- | --- | --- |
| **EXACT** | a closed-form solution | nothing to obtain; the reference cannot be wrong |
| **FORMULA** | a published correlation stated as an equation | reproducible from the formula; **no paper needed to evaluate it**, though its validity range must be cited |
| **ACQUIRE** | published data or a digitised figure | blocked until obtained |

---

## 2. The rungs

| rung | subject | reference tier | state |
| --- | --- | --- | --- |
| **T1c** | laminar pipe, `Nu` 3.657 / 48/11, `f·Re` 64 | **EXACT** | **REPORTED — GATE FAIL**, 3 of 4 rows pass |
| **T1b** | turbulent pipe vs Dittus–Boelter + Gnielinski | **FORMULA** | **PASS ×4 as returned by the frozen comparator, every grid triple DIVERGENT or STAGNANT** — D440, `T1b_RESULTS.md`. **L4 arms `R_*_x` running since 2026-08-21**: `R_10k_x` ETA 2026-08-23 ~01:40Z, `R_30k_x` / `R_100k_x` / `R_300k_x` ~2026-08-26 06–08Z. Until they land, the four Nu rows carry no mesh-converged value |
| **T1a** | turbulent flat plate (= K0e) | ACQUIRE *(obtained)* | **BLOCKED** — reference held, but **no band can be armed from one correlation** |
| **T9a** | 1D composite wall, fin efficiency | **EXACT** | **REPORTED — GATE FAIL**, 2 of 3 graded rows pass (interface 1 fails by 2.4 mK against a 0.9 mK GCI band), 2 fin rows GATE REACHED below the 0.025 % O(Bi) floor, 4 controls MET — D442, `T9a_RESULTS.md`. **T9a-D diagnosis arm (H-4) REPORTED 2026-08-22: interface scheme is the whole 2.41 mK; `Gauss harmonic` registered for the conjugate ladder; D454, L-227; `T9aD_RESULTS.md`** |
| **T10a** | view-factor enclosures vs analytic S2S | **EXACT** | **REPORTED — GATE FAIL**, 3 of 4 graded box rows pass (ceiling fails at 0.125 % against a 0.077 % GCI band); both sphere rows NOT A RESULT on DIVERGENT triples — the outer-sphere row-sum defect (4.3–4.8 %, non-converging under fixed quadrature) dominates, so the grey graded claim stays open (ε = 1 verified to 0.005 %); 12 controls MET, 6 UNMEASURED; one 2d.1 zero-referent repair disclosed, graded rows byte-identical across it — D447, `T10a_RESULTS.md`. **T10a-VF (H-3b) REPORTED 2026-08-22: viewFactorsGen alpha-regularisation defect, closed form, upstream candidate #4 NOT FILED (novelty search pending); D457, L-231**; `T10aVF_RESULTS.md` |
| **T2** | tube bank vs Zukauskas | FORMULA | needs the correlation's **stated validity range** cited, not just its algebra |
| **T3** | heated backward-facing step, Vogel & Eaton 1985 | ACQUIRE | **State 2026-08-24: ext1 COMPLETE 8/8 under the two-segment rule (`R_f` 14:53Z, 78 000 its). NOT A RESULT 4/4, now at gate (1) alone of prereg §7.1 — `R_m` and `R_f` are CONVERGED (9.7e−08, 7.8e−08), and it is `R_c` that stops the ladder, in a limit cycle at the 80 000 cap (prereg §11's registered alternative: the rung says so and does not average). G2 `x_peak/H` returns a CONVERGING triple (`p` 4.304, GCI 0.019 %) and is NOT A RESULT anyway, because gate (1) fires before the triple is consulted. St ladder now monotone in mesh; G3/G4 moved DIVERGENT→STAGNANT. Registered response: a fourth mesh level (`R_m`,`R_f`,`R_ff`), PROPOSED and NOT RUN, needing its own costed pre-registration (rough bound 150–200 core-h, USD 8–10 derived). Primary (Vogel & Eaton 1985) still NOT OBTAINED — necessary, not sufficient, and gate (3) is still downstream. ext1 cost 79.97 core-h / USD 4.10 derived, 1.005× its prediction; rung 120.29 core-h / USD 6.17. Scored: `T3_EXT1_AMENDMENT.md` §15, `T3_RESULTS.md` §14.** The primary is NOT OBTAINED (ASME closed; every open archive checked and named in `T3_PREREGISTRATION.md` §2) and its absence remains disqualifying, but it is not today's binding constraint — the ladder is: `gate_t3.json` returns `NOT A RESULT` ×4 on gates (1)/(2) of §7.1, which fire ahead of gate (3). Design frozen, comparator frozen at `628ef452` with the binding triple gate; open secondary (Smirnov 2016, CC-BY) digitised as REPORT-ONLY referent |
| **T4** | impinging jet, Martin lineage + jet data | ACQUIRE *(partial 2026-08-21)* | **OPEN**: ERCOFTAC case025 tabulated `Nu(r/D)` at `Re` 23k/70k, `H/D` 2/6 (kept in `reference-data/ercoftac_case025/`, one mislabeled header noted) + Martin correlation with stated validity from an open NREL report; **the Nu uncertainty is second-hand (2.4 %, KB Wiki quoting Baughn & Shimizu)** — graded rows need the closed ASME primaries; report-only enabled today |
| **T5** | heated cube(s), Meinders & Hanjalic | ACQUIRE *(obtained 2026-08-21)* | **PRIMARY HELD**: Meinders 1998 TU Delft thesis, OPEN, title-page verified, sha256 36c89a54…, stated uncertainty 5 % mid-face / 10 % edges in local `h`; data are digitisable figures, no tabulated appendix; single cube `Re_H` 2500–5000, matrix 2380–5280 — spend approved 2026-08-21; 3D cost to be registered before build. **Primary HELD — sha256 re-verified on disk 2026-08-22 under H-1; cost registration pending, and it is next after the cheap arms.** **`T5_PREREGISTRATION_DRAFT.md` written 2026-08-22 (unfrozen, 12 INTERPRETATIONs on Sanaa's desk)**: `Re_H` 4440, conjugate `chtMultiRegionSimpleFoam`, ladder 5.4e4 / 2.2e5 / 9.0e5 cells, cost **3.72–7.16 USD** under two rate models; **G4 recirculation REPORTED only** (thesis states no uncertainty); **inlet-T class needs the matrix chapters (separate rung)**. |
| **T6** | Rayleigh–Bénard `Nu`–`Ra` scaling | ACQUIRE | 3–4 decades of published scaling data; **transient, far over $25** |
| **T7** | mixed-convection regime map | ACQUIRE | generalises K0d; per-run cheap, **aggregate may exceed $25** |
| **T8** | buoyant plume, stratified room | ACQUIRE + partial EXACT | **plume entrainment theory (Morton–Taylor–Turner) is closed form**; the room data is not |
| **T9b/c** | conjugate flat plate; conjugate cube | ACQUIRE | 3D for T9c, **likely over $25** |
| **T10b** | natural convection + radiation | ACQUIRE | combined-mode data |
| **T11** | transient conjugate module | partial **EXACT** | **lumped and 1D transient solutions are closed form**; the published transient data is not |
| **T12** | room-scale ventilation (Nielsen / IEA class) | ACQUIRE | **over $25** |
| **T13** | rack row | inherits everything | **far over $25** |

---

## Ordering under the Thermal Buildup Directive (2026-08-22)

**This is the order of attack in force.** It comes from Sanaa's directive of
2026-08-22, recorded verbatim in `THERMAL_BUILDUP_DIRECTIVE.md`. Section 3 below
is the ordering this index recommended on 2026-08-19; it is **superseded
2026-08-22 by `THERMAL_BUILDUP_DIRECTIVE.md`, retained** — retained because the
reasoning in it is what produced the T9a and T10a pulls that have since
reported, and a superseded recommendation that is deleted cannot be checked
against what happened.

**1. Cheap arms first**, run while T1b's L4 arms finish (`R_*_x`, started
2026-08-21; `R_10k_x` ETA 2026-08-23 ~01:40Z, the other three ~2026-08-26
06–08Z):

| # | arm | directive | why it is first |
| --- | --- | --- | --- |
| 1 | **T10a ceiling refinement** | H-3a | a discretisation finding on a rung that has already reported; cheap |
| 2 | **T9a interface diagnosis** (interface scheme vs mesh vs property jump, one change per run) | H-4 | the 2.4 mK miss against a 0.92 mK band, on an EXACT rung; cheap |
| 3 | **T10a view-factor quadrature characterisation** (mesh-family sweep, geometry sweep, reproducer from clean case) | H-3b | joins the upstream queue as candidate #4; **filing remains Sanaa's call** |

**2. The DC spine**, which is the product path and takes priority inside the
T-family behind only R4's CPU-minutes:

**T3 → T5 → T8 → T12 → K2 rack row.**

| rung | the DC physic it carries | state entering the spine |
| --- | --- | --- |
| **T3** | separated thermal | **NOT A RESULT 4/4** — 2026-08-24, ext1 complete 8/8, now at **gate (1) alone** of prereg §7.1: `R_m`/`R_f` CONVERGED, `R_c` in a limit cycle at the 80 000 cap. G2 triple CONVERGING (`p` 4.304, GCI 0.019 %) but ungradeable — gate (1) fires first. Fourth mesh level (`R_m`,`R_f`,`R_ff`) **proposed, NOT run**. Primary (Vogel & Eaton 1985) still NOT OBTAINED — necessary, not sufficient. `T3_RESULTS.md` §14 |
| **T5** | heated cubes = the rack physic | **primary HELD**; cost registration pending |
| **T8** | plume / stratification = the aisle physic | partial EXACT entry rung available (Morton–Taylor–Turner) |
| **T12** | room-scale validation | ACQUIRE, over $25 |
| **K2 rack row** | the rack row itself (campaign F14) | inherits the four above |

**3. Tier completion, after the spine** (H-5, in this order):

**T4 → T6 → T7 → T2 → T9b/c → T10b → T11.**

T4 is the band-containment flagship and is sharpened by the shelf-D finding:
the registered question is whether eigenspace bands contain the documented
stagnation-`Nu` bias. Charter §2e of 2026-08-22 governs how that band may be
armed, and requires `Nu_stag` to be classified as forcing-class in the
pre-registration.

**T13 is unplaced.** It is not in the spine, not in the H-5 completion order,
and inherits everything above it; nothing is scheduled for it here.

---

## 3. What this changes about the order of attack — SUPERSEDED

**Superseded 2026-08-22 by `THERMAL_BUILDUP_DIRECTIVE.md`, retained.** Nothing
below is in force; it is kept as the record of the recommendation that produced
the T9a and T10a pulls.

The brief's default order is
**T1 → T3 → T5 → T9a → T4 → T6 → T7 → T10a → T2 → T8 → T11 → T10b → T12 → T13.**

**Three of the first five entries are ACQUIRE-blocked** (T3, T5, T4) while
**two rungs that need nothing sit at positions 4 and 8** (T9a, T10a).

**The recommendation, which is Sanaa's call and not taken unilaterally: pull
T9a and T10a forward to run alongside T1b.** They cost almost nothing, they are
unblockable by construction, and each opens a capability tier — T9a is the entry
to the whole conjugate ladder, T10a to radiation. **Nothing is reordered without
approval; the ordering above is recorded, not applied.**

**Partial-EXACT rungs are worth noticing too.** T8's plume entrainment theory and
T11's lumped/1D transient solutions are closed form, so **each has an
exact-theory entry rung that can be built before its data arrives** — the same
shape as T1c sitting available inside a class recorded as blocked.

---

## 4. What is NOT claimed here

**No rung above is a capability until it has reported.** T1c has, and it **GATE
FAILED**. T1b is running. Everything else in this table is a plan, and **naming a
plan as a capability is the error this campaign exists to avoid.**

---

# 5. REFRESH, 2026-09-03 — §2's STATE COLUMN HAS BEEN STALE SINCE 2026-08-24 AND IS SUPERSEDED BY THIS SECTION. THE FAMILY IS ~40 RUNGS, NOT 15

**Written by a heat-transfer `lab-lane` on the supervisor's record-integrity
brief, 2026-09-03. Zero core-minutes — nothing was run, re-graded or
re-launched. Every verdict below was read from the rung's own record or grading
artifact at `HEAD`; none was taken from `LAB_STATE.md`, from the docket, or from
§2 above.**

## 5.0 WHY NOTHING ABOVE THIS LINE WAS EDITED — measured, not assumed

**§2's `state` column is stale.** Its last substantive update was
`3dd28411`, **2026-08-24T16:18:52Z**. It records fifteen rungs; the family now
holds roughly forty. It still shows T1b's L4 arms as "running", T3 as the newest
result, and it knows nothing of T11 and T13–T25.

**It is not corrected in place, and the reason is a measurement.** At least
**seven records cite this file BY LINE NUMBER**, and an insertion anywhere above
them would silently redirect every one (`L-304` — the "lines whose number changed
above this section: 0" assertion certifies the lines *above*, and every citation
from elsewhere points *below*):

| citing record | cites |
|---|---|
| `docs/LAB_STATE.md:11815` | `T_FAMILY_INDEX.md:38` (T1b's tier and state) |
| `docs/campaigns/T-family/T6_CANNOT_BE_REGISTERED_2026-08-26.md:20` | `:29` (the tier legend) |
| the same record, `:26` | `:46` (the T6 row) |
| `docs/campaigns/T-family/THERMAL_SATURATION_QUEUE_2026-08-25b.md:429` | `:42` (the T2 row) |
| `docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md` `:397`, `:490`, `:532` | `:45` (the T5 row) |
| `docs/papers/forced_convection_heat_transfer/SIDECAR_VERIFICATION_2026-08-25.md:90` | `:45` |
| `docs/upstream/UPSTREAM_QUEUE.md:18` | `:75` |
| `docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md:124` | `:84` |

**So the refresh is appended, exactly as §3 was superseded-and-retained rather
than deleted, and for the same reason: a superseded statement that is deleted
cannot be checked against what happened. `lines whose number changed above this
section: 0`.**

## 5.1 ⚠ AN ID WAS REUSED, AND A READER OF §2 WILL BE MISLED BY IT

**§2's `T13` row reads *"rack row | inherits everything | far over $25"*. The
`T13` that now has a record is a DIFFERENT RUNG.**
`docs/campaigns/T-family/T13_RESULTS.md:1` is *"T13 results — natural convection
in a vertical slot, conduction regime (Batchelor 1954 parallel flow), EXACT
tier"*, and it **PASSES 4 of 4 graded rows**. **The rack row is not this rung and
has not run.** It survives in the spine table above as *"K2 rack row (campaign
F14)"*.

**Not corrected here, and not adjudicated:** which rung owns the id `T13` is a
naming call above a lane's authority, and §2's row is quoted rather than struck
because it is somebody else's registered id. **It is flagged so no reader
silently credits the rack row with T13's `PASS`.**

The same shape, benignly: **T11 spawned a family.** `T14` is *"T11b"*, `T18` is
*"T11c"*, `T17` is *"T11d"* by their own titles, and all four are EXACT-tier
transient conduction. §2's T11 row (*"transient conjugate module, partial
EXACT"*) is the ancestor of these, not a contradiction of them.

## 5.2 REPORTED — a rung verdict exists, read from the record named beside it

**Verdict vocabulary is `CLAUDE.md` rule 1's. Where a record's own verdict is
conditional or split, it is reproduced conditional or split rather than
flattened.**

| rung | subject | **verdict of record** | read from |
|---|---|---|---|
| **T1b** | turbulent pipe vs Dittus–Boelter / Gnielinski | **`PASS`** ×4 as returned by the frozen comparator — **and all four grid triples are `DIVERGENT` or `STAGNANT`, so none is a mesh-converged value; under §8's amendment candidate all four read `NOT A RESULT`** | `T1b_RESULTS.md:12`–`:15` |
| **T1c** | laminar pipe, closed form | **`GATE FAIL`** — 1 of 4 graded rows failed | `T1c_RESULTS.md:6` |
| **T1cU** | T1c uncertainty arm | **NO VERDICT FROM THE FIXED VOCABULARY APPLIES** — *"DIAGNOSTIC, NOT GRADED. No band, cannot PASS or GATE FAIL"* | `T1cU_RESULTS.md:3`, `:8` |
| **T3** | heated backward-facing step | **`NOT A RESULT`** — 4 of 4 graded rows, on gates (1)/(2), ahead of the missing primary | `T3_RESULTS.md:14`, `:22` |
| **T4** | impinging jet | **`NOT A RESULT`** on all three graded rows; the `Nu` rows remain **`BLOCKED`** (no closed primary) | `T4_RESULTS_2026-08-26.md:53` |
| **T4b** | impinging-jet successor | **`NOT A RESULT`** — 3 of 3 graded rows, all at gate (1) | `T4b_RESULTS.md:4` |
| **T5** | heated cube (Meinders) | **`PENDING`** — the frozen comparator wrote **no verdict**; no case had run at that writing | `T5_RESULTS.md:3`, `:58` |
| **T5b** | cube ladder | **`NOT A RESULT`** — **0 of 6 graded rows `PASS`**, all six failing the y+ gate (`cube_front` 2.310 against a level target of 1.00) | `verification/runs/T-family/T5b_runs/T5B_GRADE_OUTPUT.txt` (TALLY line) |
| **T8** | buoyant plume | **`NOT A RESULT`** — explicitly *"Not `BLOCKED`. Not `GATE FAIL`. Not `PENDING`"*, on two independent grounds | `T8_VERDICT_2026-08-26.md:1`, `:9`–`:10` |
| **T9a** | composite wall + fin, closed form | **`GATE FAIL`** — 1 of 3 graded rows failed | `T9a_RESULTS.md:13` |
| **T9aD** | interface-scheme diagnosis arm | **DIAGNOSIS COMPLETE — 3 `PASS`, 1 `GATE FAIL`, 3 `NOT A RESULT`** of 7 registered rows | `T9aD_RESULTS.md:11`–`:31` |
| **T9aH** | T9a re-graded under `Gauss harmonic` | **SPLIT BY GRADING PATH AND NEVER MERGED.** Frozen path: **FR0/FR1/FR2 `NOT A RESULT`, FR3/FR4 `GATE REACHED`** | `T9aH_RESULTS.md:365`ff |
| **T9aR1b** | | **`NOT A RESULT`** — its 1 graded row (R1 `T_i1`) is `NOT A RESULT` on its Roache limb. **The `PASS` this cell used to read is SUPERSEDED** by `VERIFICATION_CHARTER.md` **§2g** (v1.16, 2026-08-27, `:2590`), which refused the pre-registered floor exception on standing rule 5's one-way sentence; the remedy is at `:2643`. **The measurement is REPORTED and not discarded** (`:2644`): deviation **2.899e-12 K** against a registered **1.000e-06 K** floor, triple `EXACT`, order and GCI both `null` and correctly refused. **The frozen `gate_t9aR1b.json` still reads `"verdict": "PASS"` and was NOT edited** (rule 6) | `T9aR1b_RESULTS.md` AMENDMENT 1 (2026-09-03); companion record `verification/runs/T-family/T9aR1b_runs/T9aR1b_R1_COMPANION_RECORD_2026-09-03.md`; superseded cell at `T9aR1b_RESULTS.md:4` |
| **T10a** | view-factor enclosures | **`GATE FAIL`** — box 3 of 4 `PASS`, ceiling fails; both sphere rows `NOT A RESULT` | `T10a_RESULTS.md:32`–`:38` |
| **T10aR** | T10a ceiling refinement arm | graded **against this arm's own rows only**; *"This arm grades NOTHING against T10a's band. T10a is closed at `GATE FAIL` and stands unchanged"* | `T10aR_RESULTS.md:19`–`:20` |
| **T10aR2** | second refinement arm | **2 `PASS`, 5 `GATE FAIL`, 2 `NOT A RESULT`**; the B1 2LI triple is `OSCILLATORY` | `T10aR2_RESULTS.md:3` |
| **T10aVF** | `viewFactorsGen` α-regularisation defect | **VF-1 `PASS`, VF-2 `PASS`, VF-3 `GATE FAIL`** | `T10aVF_RESULTS.md:100`, `:113`, `:129` |
| **T11** | transient conduction, plane wall, EXACT | **`PASS`** ×3 (G1, G2, G3), every triple `CONVERGING`, planted-zero control `PASS` | `T11_RESULTS.md:3` |
| **T13** | vertical-slot natural convection, EXACT ⚠ see §5.1 | **`PASS`** — 4 of 4 graded rows | `T13_RESULTS.md:4` |
| **T14** | 2-D transient conduction, square (T11b), EXACT | **`PASS`** — 3 of 3 graded rows, all triples `CONVERGING` at p ≈ 2 | `T14_RESULTS.md:4` |
| **T16** | developing laminar mixed convection | **rung `PENDING`** (1 of 3 levels landed); **case `T16_MC_c` `BLOCKED`** — the run meets all six completion limbs and the frozen marker refuses every real OpenFOAM log | `T16_RESULTS.md:7`, `:11` |
| **T17** | axisymmetric transient cylinder (T11d), EXACT | **`PASS`** ×3 — **and the rung's registered ceiling is `GATE REACHED`, not higher** | `T17_RESULTS.md:9`, `:12` |
| **T18** | 3-D transient conduction, cube (T11c), EXACT | **`PASS`** — G1, G2, G3 — **registered ceiling `GATE REACHED`** | `T18_RESULTS.md:11`, `:19` |
| **T23** | Case 3 motor-in-duct CHT, rescaled map | **`PASS`** ×4, zero flags | `T23_RESULTS.md:44`–`:49`, `:60` |
| **T23G** | T23 grid arm | **`NOT A RESULT`** — all three graded quantities | `T23G_RESULTS.md:3`–`:5` |
| **T23G2** | second grid arm | **`NOT A RESULT`. CLOSED, RECORD FINAL** — three independent grounds, all established before and independently of eight granted repairs | `T23G2_RESULTS.md:3`–`:13` |
| **T25R2** | module outer-loop arm | **`GATE FAIL` on O3, and under the propagation registered before compute EVERY ROW OF THE RUNG IS `NOT A RESULT`** | `T25R2_RESULTS.md:1`, `:16` |
| **T25R3** | module ladder arm | **NO GRADEABLE ROW. No gate was evaluated and no physics number exists** — an absolute `p_rgh` criterion made the convergence standard tighten as the mesh refined (~955× spread in solver effort). The record declines to force a one-word label and says why | `T25R3_RESULTS.md:13`–`:24`, `:46`–`:56` |
| **T25R4** | module probe arm | **`NOT A RESULT`** | `verification/runs/T-family/T25R4_MODULE_runs/GP_VERDICT.json` (`verdict`) |
| **T25R5** | linear-solver tuning probe | **CLOSED.** `G-T5` **`PASS` on `C4`** at 60.109097× against a frozen 5.00× gate; **`P-2` LOSES** and **`P-3` LOSES**, both registered as the better outcome; `C2`/`C3` **DISQUALIFIED** (rc 124) | `verification/runs/T-family/T25R5_LINSOLVER_runs/GT5_VERDICT.json` |
| **E4a** | | **`NOT A RESULT`** — 3 rows `PASS`, 5 `NOT A RESULT` | `E4a_RESULTS.md:12` |
| **E4a2** | E4a successor | **`PASS`** — all eight registered rows | `E4a2_RESULTS.md:18` |

**`CASE3_MAP_RESULTS.md` is not a rung.** It *"assigns no verdict of its own"*;
its **16 of 16 `PASS`** is quoted from grading artifacts that already recorded it
(`CASE3_MAP_RESULTS.md:5`–`:6`, `:39`).

## 5.3 GRADED BUT NO RUNG VERDICT LOCATED — stated plainly rather than omitted

**These have grading output on disk and I could not find a rung-level verdict
line in any record. I am not supplying one; a lane does not invent a verdict.**

> **UPDATE 2026-09-03 — TWO OF THE THREE ARE NOW SETTLED, and settled by reading
> their artifacts rather than by inventing a verdict.** `T24_RESULTS.md` and
> `T15_RESULTS.md` were written on 2026-09-03. **`T24` is `PASS`, 12 of 12.
> `T15` is `NOT A RESULT` on all four graded rows** — its comparator refused
> before grading, which is exactly the case this section's caution was protecting
> against and is why the missing record mattered. **`T9aR1c` remains open.**
> The struck rows below are kept in place; nothing is renumbered or removed.

| rung | what exists | what is missing |
|---|---|---|
| **~~T15~~ CLOSED 2026-09-03** | `T15_runs/T15_GRADE_OUTPUT.txt` — **B1, B2, B3, B4 each `PASS`** (ODE residuals, flux identities, similarity solution, independent RK4 route) | **SETTLED: `T15_RESULTS.md` written 2026-09-03. RUNG VERDICT `NOT A RESULT` on all four graded rows** (`S1`, `V1`, `V2`, `V3`). **B1–B4 are the `C_REF` reference-route checks, not graded rows** — the frozen comparator **REFUSED (exit 2) at `analyse_t15.py:501`** in the planted-zero control's constant-offset arm, before any graded row was reached, so no value of S1/V1/V2/V3 exists. The run itself is COMPLETE on all six conjuncts of rule 4 (1,195.817 core-min measured) |
| **T9aR1c** | `T9aR1c_runs/W1c_GRADE_OUTPUT.txt` — planted-zero **P1/P2/P3 `PASS`**, floor demonstration **F1 `PASS`**, N1–N4 REPORTED; `gate_t9aR1c.json` written | **no `*_RESULTS.md`; no rung verdict.** STILL OPEN — and it is the successor `VERIFICATION_CHARTER.md` §2g.3 names for T9aR1b's refused floor limb (`:2800` rules that `PASS` **is** available to it), so its missing verdict is now load-bearing for two rungs |
| **~~T24~~ CLOSED 2026-09-03** | `T24_runs/gate_t24.json` — per-case rows with `B1`/`B2`/`B3` booleans and margins | **SETTLED: `T24_RESULTS.md` written 2026-09-03. RUNG VERDICT `PASS` — 12 of 12 graded rows `PASS`, zero flags.** Twelve `T_max` values 23.589696–81.784366 °C completing the 16-point map with T23's four rows. **B1's tightest margin is +118.2156 K against a 200 °C bound, and the registration itself calls a clean sweep WEAK EVIDENCE before compute.** No triple, no GCI — registered as having none (§1 line 5). y+ breached on 6 of 12 rows, reported and ungated |

## 5.4 REGISTERED, NOT REPORTED — a pre-registration exists and no results record does

**Fifteen. None of these carries a verdict, and none should be cited as a
capability (§4 above).**

`T15b` · `T16b` · `T16c` · `T19` · `T19b` · `T20` · `T21` · `T3c` · `T3_R_FF` ·
`T5c` · `T25R` · `T25R6a` · `T1_FORCED_CONVECTION_CANON` · `T1b_L4_EXT2` ·
`T1b_L4_PLANTED_ZERO_CONTROL`

- **`T25R6a`** is **in flight at this writing** — a lane is live on it; its run
  tree `T25R6a_C5_OUTER_runs/` holds `grade_t25R6a.py` and no verdict.
- **`T3_R_FF`** is the fourth mesh level §2's T3 row records as *"PROPOSED and
  NOT RUN"*. **It is now registered** (`T3_R_FF_PREREGISTRATION.md`, comparator
  frozen and hashed at `:333`) and still has no results record. `DONE.R_ff`
  exists in `T3_runs/` dated 2026-08-30.
- **`T19`, `T20`, `T16c`** carry registered JSON and/or comparators in their run
  trees; `check_comparator_freeze.py` reports each as `NO-MARKERS` — out of
  evidence reach, not graded.

## 5.5 RUN TREES WITH NEITHER A PRE-REGISTRATION NOR A RESULT

- **`T22_runs/`** — a feasibility note, a failed-launch triage, a launcher repair
  diff and one launch directory. **No pre-registration. No verdict.**
- **`T25RF_runs/`** — empty beside `T25RF_FEASIBILITY_NOTE.md`. **No verdict.**

## 5.6 IN §2 AND STILL NOT REGISTERED AT ALL

**`T2` · `T7` · `T9b` · `T9c` · `T10b` · `T12`** — named in §2, no
pre-registration, no run tree, no verdict. `T2`'s state cell is additionally the
subject of a live tier dispute referred to Sanaa (`LAB_STATE.md:11815`: the
`FORMULA` tier definition, not its application, is what is disputed, and **T1b is
in identical standing**).

**`T6` is different and is settled**: ruled **CANNOT BE PRE-REGISTERED OR FIRED,
`BLOCKED` at `ACQUIRE`**, with zero compute spent —
`T6_CANNOT_BE_REGISTERED_2026-08-26.md:1`.

## 5.7 WHAT THIS REFRESH DOES NOT DO

- **It changes no verdict, reopens no rung and grades nothing.** Every verdict
  above is transcribed from a record or a grading artifact, with the path beside
  it, and where two records disagree the disagreement is reproduced rather than
  resolved (T1b, §5.2).
- **It does not re-order the campaign.** The ordering in force remains the
  2026-08-22 Thermal Buildup Directive section above. **The spine table there is
  itself stale** — T3 and T8 have both since reported `NOT A RESULT` and T5 is
  `PENDING` — but re-ordering is the supervisor's and Sanaa's, not a lane's.
- **It does not adjudicate the `T13` id collision** (§5.1) or the `FORMULA`-tier
  dispute (§5.6). Both are flagged and left where they belong.
- **It does not claim completeness of the ~40-rung census.** It was built by
  enumerating `docs/campaigns/T-family/*_{PREREGISTRATION,RESULTS}.md` and
  `verification/runs/T-family/*/` at `HEAD` on 2026-09-03. **A rung filed
  somewhere else would not appear**, and no reader should treat the absence of a
  row here as proof a rung does not exist.

*Appended at the foot per `L-304`; nothing above edited. Nothing sent (rule 7).*
