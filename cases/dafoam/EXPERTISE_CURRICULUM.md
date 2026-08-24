# DAFoam expertise curriculum — advanced optimization cases, tiered

**Status: RATIFIED 2026-08-23 (see §7 — including the sequencing disclosure and the
conservative reading that binds it). Superseded stamp: PROPOSED (`a721ea6b`).** Every
item here that is ever run gets its own frozen, prediction-first pre-registration with
its own cost prediction before any solver starts (`CLAUDE.md` rules 2 and 12); nothing
below substitutes for that. **Nothing is filed, sent, uploaded or posted anywhere**
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**The directive, verbatim (Sanaa, 2026-08-23, relayed by the chief):**

> DAFOAM we need to think of many advanced optimization cases the dafoam team can run
> so they become an expert.

*Provenance note (`CLAUDE.md` rule 9): the quote reached this supervisor as a chief
relay, and is recorded as a relay. Drafting this proposal is within standing authority;
adopting it — the candidate set, the order, and every over-blanket item — is Sanaa's.*

**Author:** dafoam-supervisor (Fable), session `01ENBw3KPr5gMaj8Vt7rcxSB`, 2026-08-23.
**Companion document:** heat-transfer's analogous `docs/campaigns/T-family/EXPERTISE_CURRICULUM.md`
(their D468) — same directive family, disjoint territory.

---

## 1. Where the team stands — what the ladder already proved, and the gap

Verified expertise on the record: adjoint-gradient verification discipline at nine-rung
depth (A1–A6 two-row shipped/patched verdicts; the mechanical noise-sized step rule of
`ladder-a/A6/rung_n16_remaining_components/RESULTS.md` §3.1); **one** real optimization
run end-to-end (A4 Ahmed, 6 majors, `EXIT: Optimal Solution Found.`, CD −7.4775 %, rows
31–33); field inversion (B-ladder, CBFS/duct FIML); adjoint-conditioning forensics (A3,
W4/W5); five upstream defect classes prepared, all NOT FILED.

The gap this curriculum closes: **the team has verified many gradients and driven one
unconstrained-in-practice optimization.** It has never run a constrained optimization,
a multipoint composite, a parametrization study, an internal-flow or thermal objective,
or an unsteady adjoint. Expertise in optimization is expertise in constraints,
trade-offs and failure modes — that is what the tiers below buy, in order.

**Toolchain rule carried into every case:** shipped and patched are always two rows
(`DAFOAM_CHARTER.md` §6), and R11 adoption is **case-dependent, not global** — A3 rung 2
measured the rotation patch *degrading* a gradient (N-D18). Each case's prereg registers
its toolchain by image hash and, where warp-crossing DVs are graded, either buys the A/B
pair or discloses why not.

**Capability honesty:** capabilities marked **VERIFIED-ON-BOX** have run here
(`DASimpleFoam`, `DARhoSimpleCFoam`, IDWarp/pyGeo FFD, pyOptSparse driving SNOPT-class
majors, np=4 MPI adjoints, field inversion). Capabilities marked **PROBE FIRST** are
asserted by upstream DAFoam documentation but have never run on this box
(`DAPimpleFoam` unsteady adjoint, heat-transfer/CHT objectives, MRF rotating zones,
MPhys/TACS aerostructural): their first registered gate is a cheap reachability probe —
the A6 forward-AD probe precedent (`66f42398`), which found a "supported" feature
returning NaN. **No curriculum case promises a capability before its probe.**

## 2. Cost basis and the estimation rule

`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER (owner-stated
2026-08-21/22), NOT MEASURED` (`COMPUTE_BUDGET_CHARTER.md` §5). Every figure below is
**ESTIMATED**, scaled from these measured anchors, and is never quoted as measured:

| anchor | measured figure | record |
|---|---|---|
| A4 Ahmed optimization, 2,777 cells, np=1 | **13.616 core-min for 6 majors** (~2.27 core-min/major) | `LADDER_A_STATUS` rows 31–33 |
| A3 ONERA M6 rung 2 gradient item, 42,120 cells, np=4 | **85.950 core-min** (primal+adjoint+FD probes) | `A3/rung2_patched_idwarp_np4/RESULTS.md` |
| A6 CRM N=16 primal, 41,760 cells, np=1 | **102.1 s ≈ 1.70 core-min**; adjoint peak RSS 9.787 GiB | `9d5029e8`; envelope in `ADJOINT_MEMORY_ENVELOPE.md` |
| A6 N=16 whole graded FD item | **63.166 core-min** | `66f42398` |

Estimation rule: cost ≈ majors × (primal + adjoint + line-search primals), scaled by
cells and ranks from the nearest anchor; a case with no near anchor is marked UNPRICED
until its own calibration run (a price is never invented across case classes,
`COMPUTE_BUDGET_CHARTER.md:375-395`).

## 3. The tiers

Sixteen candidates, D1–D16. Ordering rationale: constraints before multipoint;
incompressible before transonic; steady before unsteady; every case ends with an
endpoint-gradient FD spot-check at noise-sized steps (the lab's own mechanical rule) so
optimization expertise never detaches from verification discipline.

### Tier 1 — Constrained-optimization fundamentals (cases already verified on the ladder)

| id | case | expertise built | prerequisites | est. cost | prereg gates on | known failure modes |
|---|---|---|---|---|---|---|
| **D1** | NACA0012 lift-constrained drag min (A1 case, `DASimpleFoam`; FFD shape + AoA DV; CL=target, thickness, volume constraints) | DVConstraints, KKT reading, feasibility restoration | A1 PASS (patched) — **met** | ~70 core-min, **$0.06** | constraint satisfaction \|CL−CL*\| ≤ registered tol; §9 termination (cap-stop is GATE REACHED/NOT A RESULT, never PASS); endpoint FD spot-check ≥3 components | FFD self-intersection at large steps; IDWarp degenerate branch (D-A class); optimizer stall at active thickness bounds |
| **D2** | Optimizer A/B on D1: two pyOptSparse optimizers, identical frozen prereg | optimizer/trust-region behavior as a *measured* comparison | D1 | ~140 core-min, **$0.12** | same gates per arm; A/B comparison bands registered before either runs | optimizer-dependent constraint violation paths read as physics |
| **D3** | Ahmed drag min + volume/rear-slant constraints (A4 case) | 3D constraints on separation-dominated flow | A4 PASS — **met** | ~70 core-min, **$0.06** | as D1; separation-onset monitor registered | wake bistability making the objective noisy (η measured first, per N-D15's δ_repeat discipline) |

**Tier 1 subtotal ≈ 280 core-min ≈ $0.24. Pre-authorised class (<$25).**

### Tier 2 — 3D wing constrained design and parametrization

| id | case | expertise built | prerequisites | est. cost | prereg gates on | known failure modes |
|---|---|---|---|---|---|---|
| **D4** | MACH wing CD min at fixed CL (A2 case, 38,304 cells, np=4; twist+shape ~100 DVs; volume, thickness, LE/TE constraints) | the canonical DAFoam constrained wing problem; supersedes A2's optimisation NOT A RESULT properly | A2 PASS + idx46 caveat — **met** | ~500–750 core-min, **$0.43–0.64** | CL-feasibility per major; §9 termination; endpoint FD spot-check with the idx46-class near-zero components named in advance | near-zero component sign flips (A1 idx6 / A5 idx16 / A2 idx46 class); MPI log splicing (measured, `79679a84`) — parse from files, not stdout |
| **D5** | FFD parametrization study: 3 FFD densities on D4's problem, same everything else | parametrization-dependence of optima; "optimizer exploits the parametrization" pathology | D4 | ~1,500–2,250 core-min, **$1.3–1.9** | pre-registered cross-density comparison metric; per-density gates as D4 | optimum differences below FD-verifiable resolution — bands must be sized from measured η first |
| **D6** | Multipoint cruise: 3 CL targets, weighted composite objective on D4's case | multipoint composites, weight sensitivity | D4 | ~1,500 core-min, **$1.3** | weights frozen in prereg; per-point AND composite gates | single-point dominance hiding a degraded off-design point — per-point verdicts mandatory |

**Tier 2 subtotal ≈ 3,500–4,500 core-min ≈ $3.0–3.9. Pre-authorised class per item.**

### Tier 3 — Transonic (compressible adjoint under shocks)

| id | case | expertise built | prerequisites | est. cost | prereg gates on | known failure modes |
|---|---|---|---|---|---|---|
| **D7** | ONERA M6 lift-constrained transonic drag min (A3 rung-2 mesh, 42,120 cells, `DARhoSimpleCFoam`) | shock-dominated design; adjoint conditioning under shocks | A3 rungs 1–2 PASS — **met**; rung-3 conditioning GATE FAIL stands as the known boundary | ~600–900 core-min, **$0.51–0.77** | adjoint convergence per major (a `-9`-class exit is BLOCKED, not skipped); §9; memory envelope §7 | adjoint GMRES stagnation (measured on this ladder at N=52); shock-induced primal fragility at deformed shapes; **the 399,360-cell campaign stays BLOCKED — this case does not touch it** |
| **D8** | CRM wing-body N=16 twist-only constrained min (A6 case, np=1, inside the 30 GiB envelope) | full-configuration handling at the memory boundary | A6 N=16 8-of-9 PASS — **met** | ~80–120 core-min, **$0.07–0.10** | twist idx6 named NOT A RESULT in advance (FD-ungradeable, row 37); memory envelope §7 with the measured 9.787 GiB adjoint basis | the flagged-component gap — endpoint verification is 8-of-9 by construction; **N=29 and its D464 gate are untouched by this case** |

**Tier 3 subtotal ≈ 700–1,000 core-min ≈ $0.6–0.9. Pre-authorised class.**

### Tier 4 — Internal flow and thermal objectives

| id | case | expertise built | prerequisites | est. cost | prereg gates on | known failure modes |
|---|---|---|---|---|---|---|
| **D9** | U-bend pressure-loss minimization (A5 case) | internal-flow objectives, near-wall FFD | A5 PASS (patched) — **met** | ~200–400 core-min, **$0.17–0.34** (coarse; A5 has no per-major anchor — calibration major registered first) | calibration-major cost gate before the full buy; endpoint FD spot-check incl. idx16-class components | bend separation making η large — measure δ_repeat before sizing FD steps |
| **D10** | U-bend two-objective: heat-transfer vs pressure-loss, 3 registered weightings | thermal-fluid trade-off design; the lab's first multi-objective front | D9 + **PROBE FIRST**: thermal-objective reachability on the installed images (zero/cheap probe, ≤5 core-min) | ~600–1,200 core-min, **$0.51–1.03** after probe | probe gate; per-weighting gates; front monotonicity check registered | "supported" thermal objective failing the probe (the ADF NaN precedent); wall-function sensitivity swamping the trade-off. *Territory note: objective design coordinated with heat-transfer at the chief's table; execution stays DAFoam* |
| **D11** | Rotating/MRF case (ducted fan or swirl passage) | rotating-frame adjoints | **PROBE FIRST** (MRF+adjoint reachability, ≤5 core-min); case selection after probe | **UNPRICED until probe** | probe gate, then its own prereg | MRF interface derivatives silently zero — a planted-perturbation control on the interface is mandatory (rule 3 analogue) |

**Tier 4 subtotal (priced part) ≈ 800–1,600 core-min ≈ $0.7–1.4 + two probes. Pre-authorised class; D11 NEEDS COSTING after probe.**

### Tier 5 — Unsteady adjoint and optimization methodology

| id | case | expertise built | prerequisites | est. cost | prereg gates on | known failure modes |
|---|---|---|---|---|---|---|
| **D12** | Unsteady adjoint, 2D cylinder time-averaged drag (`DAPimpleFoam`) | checkpointing, time-averaged objectives, unsteady verification | **PROBE FIRST** (unsteady-adjoint reachability, ≤5 core-min); Tier 1 done | ~1,000–3,000 core-min, **$0.9–2.6** after probe | probe gate; checkpoint-storage envelope (disk AND RAM) registered §7-style; FD verification on time-averaged objective with window length frozen | checkpoint storage explosion; limit-cycle phase noise (N-D15's lesson at its worst — δ_repeat on a time-average must be measured first); NEEDS COSTING refinement after probe |
| **D13** | Robustness study: 5 perturbed starts × D1's problem | basin structure, restart discipline, "same optimum?" as a measured claim | D1 | ~350 core-min, **$0.30** | per-start gates; optimum-equivalence band registered before any start runs | declaring one basin from optima that differ inside FD noise |
| **D14** | Mesh-regeneration interaction: pyHyp re-mesh at D4's optimum, re-verify gradient, re-optimize | mesh-dependence of optima; ties Roache discipline into design claims | D4; `GENERATOR_FINDING_pyhyp_aspect_ratio.md` carried as a known generator finding | ~1,000–1,500 core-min, **$0.9–1.3** | regenerated-mesh quality gates (`MESH_STANDARD`); gradient re-verification before re-optimization | the generator's aspect-ratio finding contaminating the comparison — its check runs first |
| **D15** | Verification-at-scale institutionalization: the A6 mechanical step rule + measured-η protocol applied as the standard endpoint check of every curriculum case | makes gradient verification a fixed overhead of design work, not a separate campaign | none — folds into each prereg | ~0 standalone | n/a (it IS a gate template) | the rule's own registered limitation: on a rung whose adjoint is wrong, the \|J_adj\| proxy sizes steps from a wrong number (RESULTS.md §7 limitation 8) — carried verbatim into the template |

**Tier 5 subtotal ≈ 2,400–4,900 core-min ≈ $2.1–4.2. Pre-authorised class per item; D12 NEEDS COSTING after probe.**

### Tier 6 — Sanaa-gated: instance changes and beyond-blanket capability

| id | case | expertise built | why it is Sanaa's | rough scale |
|---|---|---|---|---|
| **D16a** | CRM full-size constrained optimization | full-scale aircraft design | **BLOCKED twice** (94.7–116 GiB vs 30 GiB box; conditioning, `DAFOAM_CHARTER.md` §7): needs a ≥128 GiB instance — an instance change is reserved to Sanaa (`CLAUDE.md` first-action rule) | NEEDS COSTING on the target instance's own rate |
| **D16b** | Aerostructural (MPhys/TACS) coupled optimization | the coupled-adjoint frontier | build + probe unpriced; adoption of a new stack is hers | UNPRICED |
| **D16c** | GPU-resident adjoint arms | GPU solver capability | GPU quota granted but **a GPU is a separate instance and GPU spend is OUTSIDE the 2026-08-21 blanket** (`CLAUDE.md` rule 12): per-run console-priced cost_basis, her approval per item | NEEDS COSTING from console |

## 4. Cumulative cost and authorization classes

| tier | est. core-min | est. $ | class |
|---|---|---|---|
| 1 | ~280 | ~$0.24 | pre-authorised (<$25) |
| 2 | ~3,500–4,500 | ~$3.0–3.9 | pre-authorised per item |
| 3 | ~700–1,000 | ~$0.6–0.9 | pre-authorised |
| 4 | ~800–1,600 + probes | ~$0.7–1.4 | pre-authorised; **D11 NEEDS COSTING after probe** |
| 5 | ~2,400–4,900 | ~$2.1–4.2 | pre-authorised; **D12 NEEDS COSTING after probe** |
| 6 | — | — | **NEEDS COSTING + Sanaa's per-item approval** (instances/GPU outside blanket) |
| **1–5 total** | **~7,700–12,300** | **~$6.6–10.6** | every item still gets its own frozen prereg + cost before launch — a blanket is not a per-item read (rule 9) |

## 5. Coordination and holds — unchanged by this document

- **Two dafoam sessions are live**; the claim ledger on `docs/LAB_STATE.md ## dafoam`
  governs. This curriculum executes nothing now; when ratified, items dispatch under
  the claim ledger current at that time.
- **Untouched holds:** A6 N=29 and its two-reading gate (D464 — Sanaa's); the ~5
  core-min GAMG→PBiCGStab ADF sweep and the `useMeanStates` arm; B3 Stage 4
  fork-adoption; `DAFOAM_CHARTER.md` §13 PROPOSAL (unratified); the five upstream
  defect drafts, all **NOT FILED**; the MemAvailable 12 GiB floor.
- W4 M1+M2 (in flight under `c8254a4a`) is prior work, not a curriculum item; its M3–M8
  successors remain gated exactly as `W4_M1M2_PREREGISTRATION.md` §10 registers them.

## 6. Ratification asks on Sanaa's desk — ANSWERED, see §7

*(Original asks, retained unedited below the ratification that answered them.)*

1. The candidate set D1–D16 and the tier order (or her re-ordering).
2. Tier 1 as the starting block (three items, ≈ $0.24 total).
3. The three cheap capability probes (D10, D11, D12 reachability, ≤15 core-min total)
   — probes only, each under its own mini-prereg.
4. Tier 6: whether any instance/GPU item is opened for costing at all.

---

## 7. RATIFICATION — 2026-08-23, Sanaa, verbatim via the chief's session record

> YOU have my approval also for the heat transfer and dafoam proposals. SO... dafoam
> team can start working on their dafoam tasks from the dafoam proposal. Per usual,
> each team must formally update their respective .md files accordingly with the
> knowledge, the lessons, the processes, the summaries etc, and update the general
> lab's logic/knowledge and expertise if there is new knowledge that the entire lab
> must have.

**Sequencing disclosure, recorded before execution and never to be smoothed over:**
the approval was relayed without confirmation that Sanaa had read the committed text.
This document was committed PROPOSED at `a721ea6b` shortly *before* the relay arrived,
and her words name "the dafoam proposal" generically. **The approval is therefore read
conservatively (`CLAUDE.md` rule 9 — an approval is only as wide as what was
approved):**

1. It authorizes **starting execution** of this curriculum in the recommended
   sequence, with every item under its own frozen, costed pre-registration, and only
   **pre-authorised-class items (<$25) run on it**.
2. It is **NOT** read as: a per-item cost reading (rule 9 — the blanket is not one);
   approval of Tier 6 (instances/GPU stay NEEDS COSTING + her explicit per-item
   approval, GPU outside the 2026-08-21 blanket); the D464 **N=29 gate reading** (the
   chief's relay states this explicitly — N=29-gated arms stay parked); or approval of
   anything a future prereg finds unusual — **anything unusual, above pre-authorised
   cost, or outside these pages goes back to Sanaa costed, not read into the blanket.**
3. Her standing requirement binds every executed item: **formal .md updates**
   (knowledge, lessons, processes, summaries — this lab's per-verdict records
   discipline: `LADDER_A_STATUS`/case records per item, L/N-D/D rows via
   `append_record.py`), and **lab-wide propagation** of any knowledge the entire lab
   must have, routed through the chief for `CLAUDE.md`/charter-level changes.

**Execution state ledger (append rows here as items start and close):**

| date | item | state | record |
|---|---|---|---|
| 2026-08-23 | **D1** NACA0012 lift-constrained drag min (Tier 1) | prereg dispatched (Lane Y), phase-split — no compute until the supervisor verifies the freeze | this row; prereg path registered in it when committed |
| 2026-08-24 | **D1** NACA0012 lift-constrained drag min (Tier 1) | **prereg FROZEN `f07256fb` + Amendments 1–2 (`a659bd22`, `f4b51b24`) + after-first-compute Addendum §16 (supervisor-landed). Launch authorised 2026-08-23 ~21:16Z after personal freeze verification. Arm E COMPLETE** (η 1.957350e-08, P7 HIT; run 1 VOID under §4.2(c) after a §2d.1-eligible driver repair, run 2 graded); **arms O and C NOT RUN** — Lane Y killed at arm O's preflight. Item **`PENDING`**; spend 0.75 core-min gross / 0.30 named waste; calibration row owed at completion. Continuation (arms O + C, execution only) dispatched under the frozen file as amended | `cases/dafoam/ladder-a/A1/curriculum_D1/PREREGISTRATION.md` §16; docket D489 |
