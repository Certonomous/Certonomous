# T24 — RESULTS: the twelve points T23 deferred, graded against the PHYSICALITY TIER and nothing else

**RUNG VERDICT: `PASS` — twelve of twelve graded rows `PASS`, zero flags.**

**AND THE REGISTRATION SAYS, IN ITS OWN WORDS BEFORE COMPUTE, THAT THIS IS WEAK
EVIDENCE.** `T24_PREREGISTRATION.md` §1 line 4: *"B1 is therefore predicted to
PASS on all twelve, unflagged, and a clean sweep of twelve B1 passes is WEAK
EVIDENCE, not a strong result."* **That sentence was frozen before the solver
started and it is the honest headline of this rung.** The tightest predicted B1
margin on the whole set was **+118.2 K**; the tightest measured margin is
**+118.2156 K**. A gate cleared by 118 K discriminates nothing.

**WHAT THE RUNG ACTUALLY EARNS is §6.5's deliverable: the twelve measured `T_max`
values, and the 16-point map they complete** (§4 below). And what it earns
beyond that is §3 — **a registered, falsifiable, exactness-claiming predictor
that survived twelve independent tests at a worst departure of 0.985 %** against
a 2 % contingency it could have tripped on any row.

Pre-registration: `docs/campaigns/T-family/T24_PREREGISTRATION.md`.
Run root: `verification/runs/T-family/T24_runs/`.
Machine record: `verification/runs/T-family/T24_runs/gate_t24.json`.
All values below re-read from that artifact at this writing.

---

## 0. Rule 2 — the freeze precedes first compute, measured

| | |
|---|---|
| registration frozen at | **`b9057489`**, 2026-08-31 **19:55:46 Z** |
| first compute | `T24_P080_U10` `start_utc` **2026-08-31T20:01:19Z** |
| margin | **5 min 33 s** |

`gate_t24.json` names its own `"frozen_at": "b9057489"` and
`"frozen_document": "docs/campaigns/T-family/T24_PREREGISTRATION.md"`.

**The grading path IS the file that ran.** Disk bytes hashed against their own
`HEAD` blobs in one invocation: `T24_PREREGISTRATION.md` `45c19ac9`,
`analyse_t24.py` `fecc077b`, `build_t24.py` `76506d32`, `mark_done_t24.py`
`89b907de`, `mutation_controls_t24.py` `a4f29c55` — **five of five MATCH, no
drift, no frozen file edited.**

## 1. THE TWELVE ROWS

All twelve: `chtMultiRegionSimpleFoam`, OpenFOAM v2606, three regions
(fluid / housing / core), 2-D axisymmetric wedge θ = 5.0°, `kOmegaSST` in the
fluid, `g = (0 0 0)`, radiation OFF, 1 rank, `endTime` 10000, `writePrecision 12`.

| case | P_loss, W | U_inf, m/s | **Q1 `T_max` housing, °C** | Q2 areaAvg iface, °C | Q1 − Q2, K | B3 | B2 | B1 (bound 200.0 °C) | **VERDICT** | core-min |
|---|---:|---:|---:|---:|---:|---|---|---|---|---:|
| `T24_P080_U10` | 80 | 10 | **38.137427** | 37.571445 | +0.565983 | PASS | PASS | PASS, margin **+161.8626 K** | **`PASS`** | 37.524 |
| `T24_P080_U20` | 80 | 20 | **29.079491** | 28.600983 | +0.478509 | PASS | PASS | PASS, margin **+170.9205 K** | **`PASS`** | 37.639 |
| `T24_P080_U30` | 80 | 30 | **25.546237** | 25.117818 | +0.428420 | PASS | PASS | PASS, margin **+174.4538 K** | **`PASS`** | 38.340 |
| `T24_P080_U40` | 80 | 40 | **23.589696** | 23.197397 | +0.392299 | PASS | PASS | PASS, margin **+176.4103 K** | **`PASS`** | 37.259 |
| `T24_P155_U10` | 155 | 10 | **59.960914** | 58.864256 | +1.096658 | PASS | PASS | PASS, margin **+140.0391 K** | **`PASS`** | 38.489 |
| `T24_P155_U20` | 155 | 20 | **42.389609** | 41.462195 | +0.927415 | PASS | PASS | PASS, margin **+157.6104 K** | **`PASS`** | 38.775 |
| `T24_P155_U30` | 155 | 30 | **35.510433** | 34.679616 | +0.830817 | PASS | PASS | PASS, margin **+164.4896 K** | **`PASS`** | 39.085 |
| `T24_P155_U40` | 155 | 40 | **31.674728** | 30.913206 | +0.761522 | PASS | PASS | PASS, margin **+168.3253 K** | **`PASS`** | 37.763 |
| `T24_P230_U10` | 230 | 10 | **81.784366** | 80.157033 | +1.627332 | PASS | PASS | PASS, margin **+118.2156 K** | **`PASS`** | 38.062 |
| `T24_P230_U20` | 230 | 20 | **55.699737** | 54.323414 | +1.376323 | PASS | PASS | PASS, margin **+144.3003 K** | **`PASS`** | 38.195 |
| `T24_P230_U30` | 230 | 30 | **45.474634** | 44.241419 | +1.233215 | PASS | PASS | PASS, margin **+154.5254 K** | **`PASS`** | 38.364 |
| `T24_P230_U40` | 230 | 40 | **39.759767** | 38.629022 | +1.130745 | PASS | PASS | PASS, margin **+160.2402 K** | **`PASS`** | 37.581 |

All values **MEASURED**, read from `gate_t24.json`. Q1 from the `internalField`
of `<10000>/housing/T`; Q2 as the **area-weighted** average of the `value` list of
the `housing_to_fluid` patch in the `boundaryField` of the same file, with face
areas computed from the housing region's own `constant/housing/polyMesh`.

**TWELVE PASS, ZERO FLAGS — and the registration is explicit that zero flags was
never the requirement of this tier** (§1 line 4, verbatim: *"Zero flags was never
the requirement of this tier and must not be engineered for"*). `gate_t24.json`
records `"flag": null` on all twelve.

### 1.1 B3, the anti-degeneracy control, is the gate that could actually have bitten

B3 requires `Q1 ≥ Q2` **and** `Q1 ≠ Q2` — the check that Q1 and Q2 are two
readers of the same solution on **different code paths** (`internalField` vs
`boundaryField`) and not the same object read twice. Its failure branch is
`NOT A RESULT`, not `GATE FAIL`.

**The measured separation ranges from +0.392299 K to +1.627332 K and is
monotone in both swept variables in the physically correct sense** — it grows
with `P_loss` at fixed `U_inf` and shrinks with `U_inf` at fixed `P_loss`. The
tightest row is (80 W, 40 m/s) at **+0.392 K**, still four orders above the
`writePrecision 12` floor. **B3 is the only one of the three bands that carried a
real risk of firing, and it is the one this record would name first if a reader
asked what was actually tested.**

## 2. ROACHE TRIPLE GATING — there is no triple here, by registration

`T24_PREREGISTRATION.md` §1 line 5, verbatim: **"NONE IN THIS RUNG. There is no
grid triple here and none may be inferred."** §4.2 records the map's Roache
triple as **DEFERRED and BLOCKED**, and §2 registers a **prohibition** on using
T23's falsified level-selection instrument for anything.

**Standing rule 5 clauses (2) and (3) therefore have no operand on this rung.**
No triple state, no observed order, no GCI, no Richardson extrapolate and no
discretisation uncertainty appears in this record, and none may be derived from
it. **§3.4 of the registration is equally explicit that the directive's own
Richardson check is VACUOUS on this case and is disclosed as such rather than
reported as passing.**

**Clause (1) — a level not iteratively converged — was tested and passed** (§5).
All twelve cases used the **identical mesh**, verified per case by
`points_sha256` on all three regions (`core`
`703c126e…b678e8`, `fluid` `a49d67c1…f21f61`, `housing` `e5f797f9…da4f19`,
**byte-identical across all twelve and to T23's**), and `gate_t24.json` records
`"mesh_identical_to_T23": true` on every row. **A single mesh cannot produce a
triple, and this rung does not pretend otherwise.**

## 3. THE REGISTERED PREDICTOR — an exactness claim about a linear PDE, tested twelve times, and it held

§2.4 registered, before compute, that the energy equation of this case is
**linear in the source power** and the flow field **fully decoupled** from
temperature (`rhoConst`, constant `mu`/`Cp`/`Pr`, `g = 0`, radiation off,
`constIso` solids). The predictor:

    T_max(P, U) − T_inf  =  (P / 305) × [ T_max(305, U) − T_inf ]_MEASURED-AT-T23

with `T_inf` = 288.0 K = 14.85 °C and the four bracketed T23 rises
**88.758 / 54.160 / 40.589 / 32.995 K**.

**REPORTED, NEVER GATED.** The registered contingency: a departure above **2 % of
the predicted rise falsifies the linearity argument** and *"changes B1, B2 and B3
not at all"*.

| case | predicted rise, K | **solved rise, K** | predicted `T_max`, °C | departure, % of predicted rise |
|---|---:|---:|---:|---:|
| `T24_P080_U10` | 23.280787 | **23.287427** | 38.130787 | **+0.0285 %** |
| `T24_P080_U20` | 14.205902 | **14.229491** | 29.055902 | **+0.1661 %** |
| `T24_P080_U30` | 10.646295 | **10.696237** | 25.496295 | **+0.4691 %** |
| `T24_P080_U40` | 8.654426 | **8.739696** | 23.504426 | **+0.9853 %** |
| `T24_P155_U10` | 45.106525 | **45.110914** | 59.956525 | **+0.0097 %** |
| `T24_P155_U20` | 27.523934 | **27.539609** | 42.373934 | **+0.0570 %** |
| `T24_P155_U30` | 20.627197 | **20.660433** | 35.477197 | **+0.1611 %** |
| `T24_P155_U40` | 16.767951 | **16.824728** | 31.617951 | **+0.3386 %** |
| `T24_P230_U10` | 66.932262 | **66.934366** | 81.782262 | **+0.0031 %** |
| `T24_P230_U20` | 40.841967 | **40.849737** | 55.691967 | **+0.0190 %** |
| `T24_P230_U30` | 30.608098 | **30.624634** | 45.458098 | **+0.0540 %** |
| `T24_P230_U40` | 24.881475 | **24.909767** | 39.731475 | **+0.1137 %** |

**THE CONTINGENCY DID NOT FIRE ON ANY ROW.** `gate_t24.json` records
`"linearity_contingency_fired": false` twelve times. **Worst departure
+0.9853 %**, at (80 W, 40 m/s) — **half the registered 2 % tolerance, and the
only row that came within a factor of 2 of it.**

### 3.1 The residual departure has a STRUCTURE, and it is reported as a finding rather than as noise

**Every departure is POSITIVE — twelve of twelve, the solved rise exceeding the
predicted rise. That is a one-signed residual, not scatter.** Its magnitude
orders cleanly:

- **it grows monotonically with `U_inf`** at every fixed power
  (0.029 → 0.166 → 0.469 → 0.985 % at 80 W; 0.010 → 0.057 → 0.161 → 0.339 % at
  155 W; 0.003 → 0.019 → 0.054 → 0.114 % at 230 W);
- **it shrinks monotonically with `P_loss`** at every fixed airspeed;
- so it is **largest where the rise itself is smallest** (8.65 K at 80 W /
  40 m/s) and **smallest where the rise is largest** (66.93 K at 230 W / 10 m/s).

**The obvious candidate is TESTED HERE AND IT FAILS.** An approximately CONSTANT
absolute offset, expressed as a percentage of a shrinking rise, would produce
this pattern. Measured in kelvin the departures are:

| P_loss, W | U = 10 | 20 | 30 | 40 |
|---:|---:|---:|---:|---:|
| **80** | +0.0066 | +0.0236 | +0.0499 | +0.0853 |
| **155** | +0.0044 | +0.0157 | +0.0332 | +0.0568 |
| **230** | +0.0021 | +0.0078 | +0.0165 | +0.0283 |

**They are not constant. They span 0.002103 to 0.085270 K — a factor of 40.5,
against the solved rise's own range of only 7.66** (8.7397 to 66.9344 K). **So an
additive offset is refuted, and refuted by a wider margin than the percentage
reading suggested.** The departure is neither proportional to the rise (which
would give a constant percentage) nor independent of it. **THE MECHANISM IS NOT
IDENTIFIED HERE AND NO EXPLANATION IS ASSERTED.**
It is bounded: whatever it is, it is under 1 % of the rise everywhere on this map,
and it is one-signed. **A one-signed residual with a monotone ordering in both
swept variables is the kind of thing that is worth a successor's registered
question; it is not a defect finding and nothing in this record treats it as
one.**

## 4. THE 16-POINT MAP, with each row's provenance rung named

**Registered at §6.5: a map that does not say which rung measured which row is
not auditable.** `T_max` on the housing, °C.

| P_loss, W \ U_inf, m/s | 10 | 20 | 30 | 40 | rung |
|---:|---:|---:|---:|---:|---|
| **80** | **38.137427** | **29.079491** | **25.546237** | **23.589696** | **T24** |
| **155** | **59.960914** | **42.389609** | **35.510433** | **31.674728** | **T24** |
| **230** | **81.784366** | **55.699737** | **45.474634** | **39.759767** | **T24** |
| **305** | **103.6078** | **69.0098** | **55.4389** | **47.8448** | **T23** |

The T23 row is quoted from `T23_RESULTS.md` §1 and is **not re-graded here**;
those four rows carry T23's own verdicts (four `PASS`, zero flags) under T23's own
frozen registration `fe666fd5`. **All sixteen points sit on the byte-identical
mesh** — `points_sha256` matches across T24's twelve and T23's four.

**WHAT THE MAP IS AND IS NOT.** It is sixteen solved `T_max` values on one mesh,
one closure, one geometry, with the declared scope limits carried unchanged from
T23 §1: nose and tail cones **removed**, duct wall **adiabatic**, radiation
**OFF**, `g = (0 0 0)`. **It is not a grid-converged map, it carries no
discretisation uncertainty, it has no external referent, and the 200 °C bound it
is graded against is an engineering number from directive §3.6 and not a
measurement of anything.** §1 line 2 of the registration says so in terms:
*"REFERENCE. NONE, and that is the point of this tier."*

## 5. Completion and controls

**Strict completion (standing rule 4, steady form).** Twelve `DONE.T24_*` markers
on disk, written by `mark_done_t24.py`. `gate_t24.json` records
`"convergence_assertion": true` on every row. §3.5a registered **in advance** that
`rc` is derived from the log because the queue runner destroys `STATUS`, and
§3.5b registered the `START.<case>` file — both are registered decisions, not
post-hoc accommodations.

**Iterative convergence — the assertion set and the ONE excluded channel.**
Asserted over `Uy`, `Uz`, `h`, `p_rgh`, `k`, `omega` at 1e-06 on the last
`Time = 10000` block. **Worst asserted residual across all twelve rows and all
six channels: 1.273e-08** (`p_rgh`, `T24_P080_U10`) — **78× inside the
threshold.**

**`Ux` IS EXCLUDED, AND THE EXCLUDED VALUE IS PRINTED, NEVER SUPPRESSED.** In this
5° wedge `x` is circumferential, the mesh is one cell thick between `wedge`
patches, and `Ux` is identically zero by geometry, so its normalised residual is
noise of order one. **The final `Ux` initial residuals are 0.0310 to 0.1400
across the twelve rows** — a reader who greps the last `Ux` residual and stops
there reports every run of this family as unconverged. **The exclusion is
justified PER CASE by that case's OWN measured ratio, never recited from T23:**
`max|Ux|/max|Uz|` measures **1.561e-16 to 2.189e-16** across the twelve, against
a registered refusal threshold of 1e-12 — **four orders inside it on every row.**
`max|Ux|` itself is 2.31e-15 to 6.48e-15 m/s. **The exclusion changes no gate,
because T24 registers no residual gate at all.**

**Planted-zero control (standing rule 3), on BOTH readers, twelve times.** Plant
**1.234e-03 K**; recovered **1.2340000000108e-03** (Q1) and
**1.2340000000108e-03** (Q2) on the majority of rows and
**1.2339999999540e-03** on the remainder — **agreement with the plant to 11
significant figures on every row**, against a registered floor of **1e-06 K**.
**Both readers were shown able to see a non-zero before either was credited with
reading a value.**

**y+ on the housing — MEASURED AND REPORTED, NEVER GATED, and its breach was
already known before compute** (§4.4). Max y+ on `fluid_to_housing`:
**0.4037** (10 m/s), **0.7515** (20), **1.0790** (30), **1.3970** (40) —
identical across the three power levels at each airspeed, **which is itself the
confirmation of §2.4's decoupling argument**: the flow field does not depend on
`P_loss`, and the y+ figures show it, three times over. **The registered
y+ ≤ 1 requirement is BREACHED at 30 and 40 m/s, on all six of those rows.** It
is reported, it gates nothing, and it was registered as breached-and-ungated
before the solver started. **It is the one honest weakness of the upper half of
this map and a reader must carry it.**

## 6. Cost — rule 12, estimate against actual

| | figure | basis |
|---|---:|---|
| SUBSET POINT, registered | **360.4 core-min** | `T24_PREREGISTRATION.md` §1 line 8 |
| SUBSET CAP, registered | **540.0 core-min** hard | same |
| per-case CAP, registered | **45.0 core-min** hard, enacted as `timeout 2700 s` at 1 rank | same |
| **ACTUAL, MEASURED** | **457.075 core-min**, summed from the twelve `core_min` fields | `gate_t24.json` |
| **ratio actual/predicted** | **1.268×** | |
| fraction of the SUBSET CAP | **84.6 %** of 540.0 core-min | |
| worst per-case | **39.085 core-min** (`T24_P155_U30`) = **86.9 %** of the 45.0 per-case cap | |
| dollars, **DERIVED, NOT MEASURED** | **$0.3908** actual vs **$0.3081** predicted, at $0.0513/core-h | owner-stated rate; the box cannot read its own billing |

**NO OVERRUN. No cap was reached, no run was stopped, no new budget was sought.**
The subset came in **96.7 core-minutes over its POINT and 82.9 core-minutes under
its CAP** — the CAP did its job as a hang guard without ever binding.

**ATTRIBUTION OF THE 26.8 % OVERSPEND — CONTENTION, registered before the fact and
measured after it, not misprediction.** §5.3 registered contention as *"the
residual cost risk"* of this rung, with the saturation threshold
`loadavg_1min > nproc` (16). The `START.<case>` load readings, written **before**
each solver line, rise monotonically through the launch sequence:

| launch order | case | `loadavg` 1-min at start | `execution_time_s` |
|---:|---|---:|---:|
| 1 | `T24_P080_U10` | **5.40** | 2251.46 |
| 4 | `T24_P080_U40` | **3.42** | 2235.52 |
| 5 | `T24_P155_U10` | 3.81 | 2309.34 |
| 7 | `T24_P155_U30` | 6.02 | **2345.12** |
| 9 | `T24_P230_U10` | 7.63 | 2283.71 |
| 10 | `T24_P230_U20` | 8.66 | 2291.68 |
| 11 | `T24_P230_U30` | **9.76** | 2301.87 |
| 12 | `T24_P230_U40` | **11.15** | 2254.89 |

**AND THE HONEST READING OF THAT TABLE IS THAT IT DOES NOT SUPPORT THE
ATTRIBUTION.** The load rose **3.3×** across the sequence (3.42 → 11.15) while
`execution_time_s` moved over a range of only **2235.52 to 2345.12 s — a 4.9 %
spread with no monotone relation to load at all.** The cheapest row started at
loadavg 3.42 and the second-cheapest at 11.15. **Contention was registered as the
risk, it was measured, and the measurement does not find it.** The 1.268× is
therefore a **MISPREDICTION OF THE PER-CASE RATE**, uniform across the twelve
(every case landed in a 4.9 % band), and it is named as such rather than
attributed to a mechanism the data does not show. **This is the calibration
finding this rung owes the lab, and softening it into "contention" would have
destroyed it.**

**WASTE: 0.000 core-minutes.** No failed run, no re-run, no capped arm, no
abandoned case. Gross = cleaned; no row approached the 3,600 wall-second stall
marker (worst 2,345 s).

**A `docs/COST_CALIBRATION.md` row is OWED and is NOT YET LANDED**, per §5.5 and
standing rule 12's calibration clause. Its id is re-derived from the ledger's tail
at commit.

## 7. Disclosures

- **The verdict rests on twelve rows of a WEAK gate**, and the registration said so
  before compute. **B1's tightest margin is +118.2156 K against a 200 °C bound.**
  **A reader must not convert twelve `PASS` cells into a capability claim.**
- **NO TRIPLE, NO GCI, NO DISCRETISATION UNCERTAINTY** (§2), by registration. The
  map's Roache triple is DEFERRED and BLOCKED (§4.2). **This map is not
  grid-converged and nothing here bounds its mesh error.**
- **y+ ≤ 1 is BREACHED on six of the twelve rows** (30 and 40 m/s), measured,
  reported, ungated, and registered as such before compute (§4.4).
- **Radiation is OFF, the duct wall is adiabatic, the nose and tail cones are
  REMOVED, and `g = (0 0 0)`** — four declared scope limits carried unchanged from
  T23 §1, and `g = 0` is the one that voids the directive's own Richardson check
  (§3.4).
- **There is no external referent** (§1 line 2). The 200 °C bound and the 120 °C
  isotherm are Sanaa's numbers from directive §3.6 and are not measurements.
- **The Nusselt correlation tier, the heat-balance gate, the 120 °C isotherm trace
  and the radiation upper bound are all DEFERRED** (§4.1, §4.3, §4.5, §4.6), each
  with its reason recorded in the registration.
- **T23's lumped series-resistance model was FALSIFIED and is used here for
  nothing** (§2 of the registration): no level, gate, threshold, cap or prediction
  in this rung derives from it.
- **The one-signed 12-of-12 positive departure from the linearity predictor
  (§3.1) has no identified mechanism** and is reported as an open question, not as
  a defect.
- No frozen file edited (rule 6). No compute run for this record. **Nothing sent,
  filed, uploaded, posted or registered outside this box** (rule 7).
