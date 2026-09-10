# Navier-class and 3D case status — cfd territory, 2026-09-10

**Author:** cfd-supervisor (Opus 5). **For:** Sanaa, via the chief.
**Requested:** *"yes the status report should also include report on the navier cases"* (Sanaa, 2026-09-10 ~20:05Z).

**How every "3D?" cell in this table was decided.** From the `Mesh has N geometric (non-empty/wedge)
directions` line of `log.checkMesh`, matched **explicitly**, per level. This matters: `checkMesh`
prints a **second** line four lines later, `Mesh has N solution (non-empty) directions`, which
**counts a wedge direction as present and will certify a wedge case as 3D**. A grep on `directions`
or on `Mesh has` is not a dimensionality test. Where a second instrument was available the
cell-count ratio was used as an independent falsifier (a 3D family steps r³ — 8× at r = 2 — a 2D one
steps r²). **Both instruments agree everywhere in this table; no case rests on one reading.**

**Verdicts use the fixed vocabulary only** — `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING` — and every one names the `verification/campaign/` record that owns it.
Verdicts live there, **not** in run directories; most run directories carry no marker at all.

---

## The table

| # | case | registered | frozen | mesh levels built | 3D? (geometric line) | runs complete | triple state | verdict | blocker | tonight |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **PRD — porous radiator** `verification/runs/navier_class/PRD/us{0.25,0.50,1.00,2.00,4.00}_L{1,2,3}` | `verification/campaign/PRD_E1_PREREGISTRATION.md` | **DRAFT** — grader's own pin reads `PIN-AT-FREEZE` | **3 of 3** — 18,432 / 147,456 / 1,179,648; ratios **8.00× / 8.00×** | `(1 1 1)` all levels | **15 of 15** — `simpleFoam`, `Time=3000`/endTime 3000, `End` | **6 of 15 levels PLATEAUED, 9 NOT** | **`PENDING`** | plateau limb: every L1 fails and the oscillation is **not decaying** | one registered `us1.00_L1` continuation as a **diagnostic** |
| 2 | **MRF — stirred tank / Rushton impeller** `verification/runs/navier_class/MRF/{coarse,medium,fine}` | `verification/campaign/MRF_R1_PREREGISTRATION.md` | **DRAFT** — `904de5c67`, no freeze block | **3 of 3** — **154,715 / 448,972 / 1,273,803** | `(1 1 1)` all three; six real wall patches, zero `empty`/`wedge` | **1 of 3** — coarse `simpleFoam` 50/50 `End` (exercise smoke) | not formed | **`PENDING`** | three pre-freeze corrections, below | freeze, then launch the triple |
| 3 | **ONERA M6 — M6CP1** `verification/runs/M6CP1_runs/{L2,L1,L0}` | `verification/campaign/M6CP1_PREREGISTRATION.md` | **FROZEN** `852e77ff8`, blob `543ffe29` | **3 of 3** — 71,760 / 574,080 / 4,592,640; ratios **8.00× / 8.00×** | `(1 1 1)` all levels, all-hex, zero `empty`/`wedge` | **0 of 3** — three stage-3 smokes only, no stage-4 run | not formed | **`NOT A RESULT`** — same record, Amendment 2 | **collapsed trailing edge, 60.9° cusp, zero cells across it** | none — parked |
| 4 | **ONERA M6 — other families** `M6SR_runs`, `M6I_runs`, `M6_OWN_FAMILY_runs`, `F13_ONERA_M6_runs`, `RUNG1_M6_R2_runs`, `M6S_runs` | several | mixed | many, up to **1,597,440** | `(1 1 1)` | **0** — **every `End` line belongs to a MESHER** | not formed | `PENDING` | same cusp — M6SR wraps the same surface | none |
| 5 | **NASA CRM / DPW5 wing-body** `verification/runs/RUNG2_CRM_runs/M2_snapshot_admission/B1` | `verification/campaign/RUNG2_CRM_M2_PREREGISTRATION.md` | **FROZEN**, prereg `f76948410`; grader `a2996ed07`, sha256 pin verified | **1 of 3** — 638,976 hex | `(1 1 1)`; internal faces **2.967/cell** (2D would give ≈2.0) | **1 of 1** — `rhoSimpleFoam`, 50/50, `End`, all six rule-4 limbs PASS | **single grid — no triple** | **`PASS`** on admission gates G0–G4 **only** | see the caveat below — it is large | needs 2 more levels of the **same topology** |
| 6 | **SUBOFF** `verification/runs/navier_class/SUBOFF/*` | `SUBOFF_R1_/R1b_PREREGISTRATION.md` | committed | 121,600 / 202,014 | **`(1 1 0)` — 2D.** Carries `wedge` + `empty` patches | `simpleFoam` r1b 2500/2500; `reg_coarse` 1445/2500 and `reg_medium` 311/2500 **no `End`** | DIVERGENT | **`NOT A RESULT`** — `SUBOFF_R1b_RESULTS.md` | **it is an axisymmetric wedge, not a 3D case** | none — a 3D SUBOFF is a new mesh family |
| 7 | **SUP_BOOSTER — supersonic booster** `verification/runs/navier_class/SUP_BOOSTER/*` | `SUP_BOOSTER_E1_/E2_PREREGISTRATION.md` | E2 verdict issued | 13,500 (medium) | **`(1 1 0)` — 2D**, 5° wedge | `rhoCentralFoam` 15000, `End` | — | **`PASS`** — `SUP_BOOSTER_E2_VERDICT.md` | 2D | none |
| 8 | **Ahmed body — blunt body** `verification/runs/R4_runs/{c1..c4b,c5}` | `verification/campaign/R4_PREREGISTRATION.md` (`6cdf8a41`) | frozen | **6 levels** 79,439 → 834,351 | `(1 1 1)` at c4, c4b, c5 | `simpleFoam`, c1–c4b converged (2σ 0.01–0.10 % of value) | c1–c4b usable; **c5 refused** | **c5 `NOT A RESULT`** — `R4_ASYMPTOTIC_RESULTS.md`; converged levels rebase inside the ±15 % band | c5 unconverged: 2σ **6.31 %** vs a 5 % ceiling | none |
| 9 | **B-52** `/home/ubuntu/certonomous-runs/study-b52-*-uq` (10 meshes) | `B52_RUNG6/7/8_PREREGISTRATION.md` | RESULTS exist; **turn claim WITHDRAWN** `B52_TURN_WITHDRAWAL_2026-08-10.md` | 10 meshes, 255,358 → 836,136 — **not a clean r-family** | `(1 1 1)`, zero `empty`/`wedge` | **YES** — `simpleFoam` 300/300 `End`, all ten | no clean triple | **`PENDING`** | needs a **frozen new pre-registration**; blocker is paperwork, not compute | — |
| 10 | **B-52 (graded tree)** `verification/runs/B52_RUNG6_REPLICATE_runs` | as above | — | mesh only, 193,880 | `(1 1 1)` | **NO — `checkMesh` only.** A sibling scratch tree has a `300/` dir whose only `Exec` is `simpleFoam -postProcess -func yPlus` — **a post-processor, not a solve** | — | `PENDING` | **the M6 trap in a new costume: fields with no solve log** | — |
| 11 | **motorbike** `/certonomous-runs/validation-scratch/motorBike`, `.solve-cache/motorBike-c353688-i300` | **NONE** | — | 353,688 | `(1 1 1)`, zero `empty`/`wedge` | **NO solve log.** One tree has `300/` + `log.yPlus` (`-postProcess` only); the cache has `300/` + `DONE` and **no log at all** | — | **not a case under rule 2** | **unregistered, and the geometry is the OpenFOAM tutorial body** | enters the protocol as a **new registration**, mesh family and all; the existing solve is **not** graded |
| 12 | **DrivAer** `verification/runs/navier_class/DRIVAER/` | `DRIVAER_R1_PREREGISTRATION.md` | **DRAFT** | **0** — no STL on disk | n/a | NO | — | **`BLOCKED`** — geometry | the geometry does not exist on this box | acquire geometry |
| 13 | **F25 — square duct** `verification/runs/F25_DUCT3D_runs/{coarse,medium,fine}` | `F25_DUCT3D_PREREGISTRATION.md` | frozen `12def6b5`; all 5 grading-path blobs verified | **3 of 3** — 32,768 / 262,144 / 2,097,152; ratios **8.00× / 8.00×** | `(1 1 1)` all three; patches cyclic/cyclic/wall | **3 of 3** — `simpleFoam` 4000/4000; **all six rule-4 limbs PASS at every level** | **CONVERGING**, both gates | **`PASS` ×2** — `F25_DUCT3D_RESULTS.md` | none | none — **done** |
| 14 | **scrubber** | **no case on disk** | — | — | — | — | — | **absent** | never built in cfd territory | — |

---

## The three things that must change before MRF is frozen — and none of them is optional

MRF is the closest case to a genuine 3D triple, and building the levels exposed three defects in its
own registration. All three are **pre-compute** and therefore legally amendable (rule 2); after the
freeze they would be gates and could not move.

1. **THE GRADER WILL REFUSE THE FAMILY AS REGISTERED.** The background block scales by exactly 1.5
   (32×32×36 → 48×48×54 → 72×72×81) but the *delivered* mesh does not, because `nCellsBetweenLevels`
   is measured in **cells, not physical thickness**, so the refinement shell shrinks with the base
   cell. Delivered ratios are **r32 = 1.426359, r21 = 1.415667**, a gap of **1.07e-02** against
   `roache_triple.py`'s `EQUAL_RATIO_TOL = 1.0e-9` — **seven orders of magnitude over.** `mode="equal"`
   **REFUSES**; only `mode="auto"`/`"unequal"` grades, via the Celik fixed-point path. **If this is
   left unset the ladder refuses at grading time, after the compute is spent.** Both ratios clear
   Celik's r ≥ 1.3 minimum, so the triple *is* gradeable — cross-checked by a volume-based
   h = (V/N)^(1/3) that agrees to four in the fifth digit.
2. **THE REGISTERED CELL TARGETS ARE WRONG BY ~1.6×.** §4/§7 register ~250 k / 0.85 M / 2.9 M. The
   coarse that exists is **154,715** — 62 % of its target — and the family built from it lands at
   **448,972 / 1,273,803**.
3. **THE 420 CORE-MIN CAP WILL TRIP.** From the coarse smoke's measured 6.427e-6 core-s per
   cell-iteration, the pinned `endTime 4000` projects **~66 / ~192 / ~546 = ~804 core-min, roughly
   1.9× the cap, with the fine level alone exceeding the whole cap.** The projection is *optimistic*:
   it assumes perfect scaling, and 16-rank decomposition of a 155 k-cell level is latency-bound.
   Under rule 12 an overrun **stops the run**, so as frozen the fine level would trip its sub-cap and
   the gate would never receive a fine value.

**Disclosed, not waved:** all three MRF levels report `Failed 1 mesh checks` — `***Concave cells
(using face planes) found`, 2.73 % / 2.01 % / 1.35 %. It is an `-allTopology` check, is **not** one of
the registration's two hard gates (max non-orthogonality ≤ 70° and max skewness ≤ 4, both passed with
margin at every level), and the fraction **falls monotonically with refinement**. It is a standing
property of this snappyHexMesh geometry — the already-clean coarse level carries it too.

---

## The CRM caveat, stated plainly because the word `PASS` is doing less work than it looks

The CRM's `PASS` is on **admission gates only** — G0 reproduction control, G1 writer liveness, G2 warm
start, G3 rule-4 admission, G4 planted controls (15/15 fired). The pre-registration says in its own
words that **"NO FORCE, NO DRAG, NO LIFT, NO MOMENT, NO CRM CLAIM may be read out of this probe"**.
Three further facts:

- **It did not run the DPW5 condition.** `0/U` gives |U∞| = 68.06 m/s, α = 2.11°, **Mach 0.196**. The
  famous CRM condition is **M = 0.85**. The `forceCoeffs` block's `magUInf 295.0` is inherited from the
  seed and **contradicts the field that actually ran**, so its coefficients are meaningless.
- **It is not converged.** p initial residual **7.33e-3** at iteration 50 against a `residualControl`
  target of **1e-9**. It stopped on `endTime`, not on convergence.
- **It is a single grid**, so it is **not Roache-gated** and nothing may imply that it is.

---

## Two corrections this document makes to earlier reporting

**PRD is `PENDING`, not `GATE FAIL`.** An earlier survey row read a `GATE FAIL` out of
`PRD_E1_GATE_RULING_2026-09-09.md`. **That document is a PRE-COMPUTE gate ruling** — it says so in its
title and authorises *"the gate DESIGN, not un-read code"* — and it contains no verdict on any run. It
states the opposite: *"No `BLOCKED` verdict is admissible without measured exhaustion evidence. A
terminal GATE FAIL / NOT A RESULT needs the §2bc exhaustion ladder."* The tokens in it are the gate
**hierarchy**, not outcomes.

**The Ahmed demo entry pointed at the one refused level.** An earlier cfd inventory listed
`R4_runs/c5` as the Ahmed case. c5 is `NOT A RESULT`. The usable levels are c1–c4b. See
`AHMED_BODY_RECONCILIATION.md` Addendum 1 for the **factor-3.586571** planform-to-frontal rebase that
must accompany any R4 number.

---

## Honest gaps in this document

- The **frozen?** column for B-52 and the wider M6 family is read from record titles and one commit
  sha, **not** from a per-file freeze-block audit. Treat those two rows as indicative.
- **PRD's freeze state** is inferred from the grader's own `PIN-AT-FREEZE` placeholder rather than
  from a freeze-block audit of the pre-registration.
- Rows 9–11 live **outside git** under `/home/ubuntu/certonomous-runs/`; their dimensionality readings
  come from existing logs, not from a `checkMesh` re-run by this survey.
- **`scrubber`** and a distinct **"blunt body"** beyond the Ahmed have no case on disk in cfd
  territory. They are rowed as absent rather than omitted, because an absent case is a finding.

---

# ADDENDUM 1 — 2026-09-10T~20:50Z, cfd-supervisor. **TWO ROWS ABOVE ARE WRONG. THEY ARE MINE.**

**lines whose number changed above this section: 0.** The rows above are **struck by this addendum,
not rewritten** — a reader who was given the original must be able to see what changed.

**Both errors have the same shape, and it is the shape that has now caught this lab three times in
one day: a census that reads tracked paths is structurally blind to data that lives outside git.**
`/home/ubuntu/certonomous-runs/` is enumerated in `docs/LOCATIONS.md` precisely because nothing is
invisible merely because it is big — and I still missed it twice.

## C1 — 🔴 **ROW 12 (DrivAer) IS FALSE. THE GEOMETRY EXISTS. `BLOCKED` IS WITHDRAWN.**

Row 12 reads *"0 — no STL on disk"*, verdict *"`BLOCKED` — geometry"*, blocker *"the geometry does not
exist on this box"*. **All three are wrong.** Verified by the supervisor personally, by opening the
file rather than by listing a directory:

    /home/ubuntu/certonomous-runs/navier_class/DRIVAER/drivaerml_r7a5c094/run_466/drivaer_466.stl
    142,346,740 bytes · ASCII STL · first line `solid BodyA-Pillar` · last line `endsolid WheelSupportrear`
    753,238 facets

Beside it: `force_mom_466.csv`, `force_mom_constref_466.csv`, `geo_parameters_466.csv`,
`geo_ref_466.csv`. Dataset `neashton/drivaerml`, revision `7a5c0948ce27be709b1116a3a190f806e7a8f79f`,
CC-BY-SA-4.0; provenance at `cases/navier_class/DRIVAER/DATA_PROVENANCE_drivaerml.md`; grader
`cases/navier_class/DRIVAER/grade_drivaer.py` committed `c17e03c37`.

**Why the row was wrong:** it looked in `verification/runs/navier_class/DRIVAER/`, which holds one
`.json`. The geometry lives outside git. **`BLOCKED` was the wrong verdict and I withdraw it.**

| | struck | **corrected** |
|---|---|---|
| mesh levels | ~~0 — no STL on disk~~ | 0 built, **but the geometry is present: 753,238-facet STL** |
| verdict | ~~`BLOCKED` — geometry~~ | **`PENDING`** |
| blocker | ~~geometry does not exist~~ | **mesh the family, then freeze** |

**This promotes DrivAer materially.** A DrivAer is a full production automotive body with reference
force and moment data shipped alongside it — **on Sanaa's "more 3D industry cases" axis it outranks
most of this table**, and its blocker is now ordinary work rather than an absent asset.

## C2 — **ROW 11 (motorbike) — "NO solve log" IS WRONG. THE RULING IS UNCHANGED.**

Verified personally at `mission-output/geometry-study/study-motorBike/log.simpleFoam`:
**`Exec   : simpleFoam -parallel`**, last **`Time = 300`**, exactly **one `End`**, 353,688 cells,
`Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)`. **That is a genuine solve log.** The row
contradicted a finding I had already made myself and then failed to carry into the table.

**The ruling does not move: the motorbike is still not a case under rule 2** — it has **no
pre-registration**, so nothing about it is gradeable and the existing solve is **not** graded. **Only
the REASON changes**, and the distinction matters because the two reasons imply different work:

> struck: ~~"no solve log; the trees hold `-postProcess` output only"~~
> **corrected: "unregistered, and living outside `verification/runs/` — a solve exists but no gate,
> no band and no freeze were ever committed before it ran."**

The trees the original row cited (`validation-scratch/motorBike`, `.solve-cache/…`) **do** hold only
`log.yPlus` from `simpleFoam -postProcess` and a bare `DONE`. The real solve is in a third tree the
row never reached.

## C3 — THE VERIFICATION REFERRAL ON THE CRM'S GRADER — **ANSWERED: FOUND, PINNED, FREEZE-JUDGED**

- Owning record: `verification/campaign/RUNG2_CRM_M2_PREREGISTRATION.md`
- **Grading artifact: `cases/committee-grids/grade_r2_m2.py` — FOUND**, committed `a2996ed07`
- **Its name DOES match `grade_*`**, so the name pattern is *not* why the census missed it. The census
  walked **the run tree**; this grader lives under `cases/`. **That is the population gap
  `scripts/check_comparator_freeze.py` documents in its own source at lines 58–64** — *"Walking
  `verification/` alone left eleven graders under `cases/`"*.
- **It IS pinned and freeze-judged:** on-disk sha256 `7f8089d81f…f9c089` == the pre-registration's
  pinned sha256, and git blob `b40e7dfd…` == the frozen blob.

**So the answer is reassuring about this case and worrying about the census**: a grader-name walk of
run trees will keep reporting absent graders that are present, pinned and clean.

## C4 — "PASS ON FOUR GATES" IS A RECORDING ARTIFACT, NOT A MISSING GATE

The CRM pre-registration defines **five** gates; `STATUS.R2_M2` persists **four**.
`grep -c 'R2M2_G4'` on the status file = **0** (planted control: the same reader on a copy with the
line appended returns 1). `grade_r2_m2.py` emits `R2M2-G4` only via `print()` on its `--selftest`
branch and **never writes it to the status file**; the only persisted trace is `selftest_rc=0`,
written by the driver rather than the grader. Re-derived independently:
**`R2M2-G4: PASS — 15/15 controls fired`.** **The gate ran and passed; it was never recorded.**

## C5 — A DISTINCT BLUNT BODY DOES EXIST AS A RECORD

`verification/campaign/F4_hypersonic_blunt_body.{md,json}` exists **with no case on disk** — distinct
from the Ahmed body that row 8 maps "blunt body" onto. Rowed here so the mapping is explicit.
**`scrubber` remains not found — and "I could not find it" is not "it does not exist"**, which is why
row 14 says absent rather than nonexistent.

## C6 — THE LEGAL ROUTE TO A PASS ON PRD, NAMED SO NOBODY REACHES FOR THE ILLEGAL ONE

PRD-E1's fine level reproduces the Ergun law to **≤ 0.035 %** against a **±3 %** band at all five
velocities (supervisor's check-1 read; the ×ρ conversion is load-bearing — the raw kinematic series
reads 16.8 % low and would look like a GATE FAIL). **The only thing between that and a PASS is the
plateau limb**, and **loosening `PLATEAU_REL_TOL` or switching to a window-averaged Δp is gaming and
will not be done** — rule 5 is one-way, and a beautiful value on a level that never settled is
`NOT A RESULT`.

**The legal route is a SUCCESSOR REGISTRATION**, never a retrofit onto E1: run the §2bc exhaustion
ladder with the `us1.00_L1` diagnostic as its **L0 diagnose** step; if that shows a genuine
grid-dependent limit cycle (N-AV15's class, not N-AV17's domain-artifact class), register a successor
**frozen before its own compute**, disclosing E1's limit cycle on its face and registering a plateau
criterion **fit for a steady solve that limit-cycles on coarse grids**. **The diagnostic's answer
decides whether that successor is worth registering at all.**
