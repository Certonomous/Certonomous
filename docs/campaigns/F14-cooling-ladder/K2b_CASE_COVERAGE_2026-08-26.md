# K2b — per-case registration coverage, **read end to end, not greped**

**Written by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26. ZERO COMPUTE.**
**Nothing is graded, struck or amended by this file. No case directory was touched.**
Nothing has been sent, filed, submitted, uploaded, registered or posted outside this box
(`CLAUDE.md` rule 7).

---

## 0. THE QUESTION AS POSED CONTAINS THE ERROR IT WAS ASKED TO AVOID

The task was: *"Are the other fifteen K2b cases described BY CLASS in the two
2026-08-18 pre-registrations?"*

**Only four of the fifteen were ever supposed to be in those two documents.** They
register the **unsteadiness diagnosis** — Test A, Test B, Control M, Test D — and nothing
else. **The nine pilot cases are registered elsewhere**, and `K2b_PILOT_RESULTS.md:3-5`
says so in its own opening lines:

> *"Executed 2026-08-18 against `K2a_RACK_ROW_MODULE_SPEC.md` **section 6** under three
> authorisations: 60 core-minutes for the 2D pilot, then 1.4 for a 3D coarse cost probe
> and 20 to finish control C3."*

**Had this been answered by greping the two named documents, the result would have been
"eleven of fifteen uncovered" — a catastrophic false finding, produced by searching the
wrong documents.** That is **L-337's PLACE axis for the second time**, and it was avoided
only because both documents were read end to end and their own scope statements were
taken seriously.

> **A COVERAGE QUESTION MUST FIRST ESTABLISH WHICH DOCUMENT IS SUPPOSED TO COVER WHAT.
> Asking "is X in document Y" when Y never claimed X is not a coverage check — it is a
> guaranteed false negative wearing the clothes of diligence.**

## 1. The population, re-derived

Sixteen `K2b*` case names exist at HEAD ∪ disk. **Fifteen hold consumed compute** (a
non-zero time directory and/or a `buoyant*Foam` solver log). **`K2bU3_D` has tracked case
inputs and NO consumed compute** — consistent with `COVERAGE_MATRIX.md:858`, which
records K2bU/K2bU3 as *"cannot be tiered at all… no results record and no sub-row"*.

## 2. THE COVERAGE TABLE — 14 of 15 covered, 2 uncovered, and the counts do not overlap the way they look

| # | case | covering clause, quoted | verdict |
|---|---|---|---|
| 1 | `K2bP_under` | **K2b-U §2** tabulates it by name; §3 Tests A and B both operate on it | **COVERED — named** |
| 2 | `K2bP_URelax` | **K2b-U §3 Test A**: *"Re-run `K2bP_under` from `0.orig` with every under-relaxation factor cut: p_rgh 0.3 → 0.15, U 0.5 → 0.25, T 0.5 → 0.25, (k\|omega) 0.5 → 0.25"* | **COVERED — class** |
| 3 | `K2bU_trans` | **K2b-U §3 Test B**: *"`buoyantBoussinesqPimpleFoam`, same mesh, same BCs, started from `K2bP_under/5000` (the oscillating state), adjustable time step at maxCo 2"* | **COVERED — class** |
| 4 | `K2bU3_M` | **K2b-U3 §2 Control M**: *"the same 2D slice, same 70 % provisioning, same transient solver, **at the 3D test's own 100 mm resolution**"*. `CASE.txt` reads `cell size 0.1 m`, `cells 725`; §3 predicts *"≈725"* | **COVERED — class, and the cell count matches the prediction exactly** |
| 5 | `K2bU3_D` | **K2b-U3 §3 Test D**: *"full module, N = 4 racks, h = 0.1 m"*, ≈28,700 cells, row ends *"open, 0.60 m each"*. **Its `CASE.txt` names the pre-registration BY SHA256 (`91a26fc9…`) and states its own gate** — *"K2bU3_M must show the limit cycle surviving at this same"* resolution | **COVERED — class, and the strongest form on the board: the case cites its own frozen registration** |
| 6 | `K2bP_coarse` | **K2a §6**: *"A 2D vertical-slice pilot… is specified alongside as **K2b-pilot**: same BCs collapsed to the slice, **42 k / 95 k cell pair**"*. `CASE.txt`: 46,400 cells | **COVERED — class (the coarse half of the registered pair)** |
| 7 | `K2bP_fine` | **K2a §6**, same clause (the fine half of the registered pair) | **COVERED — class** |
| 8 | `K2bP_C1_g0` | **K2a §8**: *"**Pre-registered controls for K2b**… **C1 gravity-off twin** (θ becomes pure forced transport; predicted direction: cold-aisle stratification collapses)"* | **COVERED — class, with a pre-registered predicted direction** |
| 9 | `K2bP_C2_dT13` | **K2a §8**: *"**C2 ΔT-plant** (+10 % on one rack's offset; predicted: that rack's outlet ledger row moves by 10 %, its θ unchanged to first order — the discriminating pair)"* | **COVERED — class** |
| 10 | `K2bP_C3_plant` | **K2a §8**: *"**C3 planted volumetric source** (KV1's plant in the room)"*; and *"S15's fvOptions witness runs wherever a plant exists"* | **COVERED — class** |
| 11 | `K2bP_C3b_noplant` | **Entailed by C3, not additional to it.** `CASE.txt`: *"kind RESTART TWIN of `K2bP_under`"*. **Standing rule 3 makes the twin part of the control, not an extra case: a plant read back with no no-plant comparison is not a planted-zero control at all.** Registering C3 registers the pair | **COVERED — entailed** |
| 12 | `K2b3D_probe` | **K2a §10** states its own gap: *"derated for 3D + turbulence by an **assumed factor** — the derate is an **engineering assumption, stated, not a measurement**"*. `CASE.txt`: *"kind **COST PROBE ONLY — 200 iterations, not converged, grades nothing**; purpose measure the 3D+SST derate K2a section 10 assumed at 2.7 and never measured"* | **COVERED — it discharges a gap the spec named, and it grades nothing, so rule 2 does not reach it** |
| 13 | `K2bP_WSpalding` | **K2a §6**: *"Wall treatment: wall functions; target y+ in the log-law band (30–300, RECALLED as the standard wall-function band; **to be measured by the mesh-report function object and reported per case, not assumed**)"*. `CASE.txt` differs from the pilot only in `nut wall treatment nutUSpaldingWallFunction`, same 46,400 cells | **COVERED — registered precondition; JUDGEMENT STATED at §3** |
| 14 | `K2bP_WLowRe` | **K2a §6**, same clause; `nutLowReWallFunction`, same 46,400 cells — the second arm | **COVERED — registered precondition; JUDGEMENT STATED at §3** |
| 15 | **`K2bU3_L050`** | **NONE FOUND.** `CASE.txt`: `cell size 0.05 m`, 2,900 cells. K2b-U3 §2 registers Control M at **one** resolution — *"at the 3D test's own **100 mm** resolution"* — and §5 confirms *"100 mm is coarser than the spec's 60 mm 3D coarse mesh"*. **50 mm is neither** | **NOT COVERED** |
| 16 | **`K2bU3_L025`** | **NONE FOUND.** `CASE.txt`: `cell size 0.025 m`, 11,600 cells. Same reasoning | **NOT COVERED** |

**14 covered / 2 uncovered**, of sixteen names. Of the **fifteen with consumed compute**,
**13 covered / 2 uncovered** (`K2bU3_D` is covered but has no compute).

## 3. THE TWO JUDGEMENTS I MADE, STATED SO THEY CAN BE OVERRULED

**Neither is a grep result. Both are readings, and a reading is a thing a supervisor may
disagree with.**

- **Rows 13–14 (`WSpalding` / `WLowRe`).** K2a §6 registers a **precondition** — y+ must
  be *measured and reported per case, not assumed* — not a two-arm comparison. I read a
  two-arm wall-treatment comparison as the discharge of that precondition, and
  `K2b_PILOT_RESULTS.md` §12 is titled *"The wall-treatment precondition, discharged"*.
  **A stricter reading is available: a precondition to measure y+ is not by itself a
  registration of two alternative wall functions.** If the supervisor takes the stricter
  reading, these two move to NOT COVERED and the count becomes 12/4.
- **Row 11 (`C3b_noplant`).** I read the no-plant twin as entailed by registering a
  planted-source control, because standing rule 3 makes a plant without a twin
  evidentially empty. **A stricter reading would require the twin to be named.** I think
  the stricter reading is wrong — it would make rule 3 unimplementable without listing
  every control's own control — but it is available.

## 4. THE FINDING — `K2bU3_L025` AND `K2bU3_L050` ARE UNCOVERED, AND WHAT THAT DOES AND DOES NOT MEAN

**What is established.** Two 2D slices at 50 mm and 25 mm were built and solved
(2,900 and 11,600 cells; 4 non-zero time directories each;
`buoyantBoussinesqPimpleFoam`, `endTime 80.0`). **Neither resolution appears, by name or
by class, in either 2026-08-18 pre-registration**, which register Control M at 100 mm
and Test D at 100 mm and nothing else.

**What they most likely are, and this is a reading, not a claim.** Together with
`K2bU3_M` (100 mm) and the pilot's 12.5 mm `K2bP_under`, they form a **coarsening
ladder** — 12.5 → 25 → 50 → 100 mm — which is precisely the question K2b-U3 §2 poses:
*"does the 6.000 s limit cycle survive coarsening alone?"* **A ladder is a stronger
instrument than the single-point control that was registered.**

> **AND THAT IS EXACTLY WHY IT MATTERS. A control strengthened after registration is
> still a control that was not registered.** §2's design turns on Control M being a
> **pass/fail gate** — *"Control M shows the oscillation surviving → proceed; Control M
> shows it damping → Test D cannot answer the question, outcome P3."* **A three-point
> ladder does not have a pass/fail reading fixed in advance**, and choosing which rung of
> it to treat as "the control" after seeing all three is the move pre-registration
> exists to prevent.

**What this is NOT.** It is **not** a finding that any number is wrong; I make no claim
about the physics. It is **not** grounds to re-grade anything — no K2bU3 row reaches any
ledger, `COVERAGE_MATRIX.md:858` already records the family as untierable, and nothing
here is re-graded on anyone's say-so. And it is emphatically **not a licence to write a
retrospective freeze**: a pre-registration written after its compute is not a
pre-registration.

**Brought to the supervisor as a finding. This lane rules nothing.**

## 5. WHAT THE RECORD ALREADY SAID, WHICH IS WHERE THIS SHOULD HAVE STARTED

`VALIDATION_INVENTORY.md:247` files the K2b pilot with gate **`none`**, quoting the
rung's own *"capability case in the K0a/K0b sense, never a result"*, and names **D378**
and **D379**. `:657` files the **S13 monitor defect** found in this rung — a signature
that *"returns its best possible score on a field that has not moved"*.

**The rung's headline is a split that was on the board the whole time:** the case that
shows recirculation is the one that fails the S13 convergence signature, and the case
that passes S13 never closes its heat balance. **Two docket items are already open
against it.** The real exposures were filed; the registration-coverage question was the
smaller one, and of the sixteen cases it reaches two.

## 6. Cost

**Zero core-minutes.** Two pre-registrations and one specification read end to end;
sixteen `CASE.txt` files and their `blockMeshDict`/`controlDict` inputs read directly.
`docs/COST_CALIBRATION.md` gains no row: there is no compute to calibrate.
