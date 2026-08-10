# Katie's challenge slate, scoped — 2026-08-07

Zero compute: nothing in this file was solved for it. It takes the owner's
2026-08-07 slate of twenty-one hard cases, maps each against what the lab has
already done, states the capability gaps honestly with the cheapest rung that
unlocks each one, verifies that every entry has a real reference with a real
citation, and ranks the program by the arithmetic that already runs in
`sdk/chief_engineer/agenda.py`:

    rank_value = gain_points(source_kind) / max(est_core_min, 1.0)

with `challenge` 4.0, `measurement`/`gate` 3.0, `capability` 2.0, `report`
1.0 (`GOALS_AND_PROPOSALS_CHARTER.md` §2, the table is closed and an
unrecognised kind is refused at intake). Where an estimate has no measured
history it says so, because the axis is a ratio and a denominator nobody
checks is a denominator that drifts.

Capability availability was **measured on this box, not assumed** — see §2.

---

## 1. Status map

### Already on the record or in flight (10 of 21)

| slate entry | lab identity | status | evidence |
| --- | --- | --- | --- |
| NASA wall-mounted hump | **F6a** | Gate reached: separation x/c 0.6544 vs 0.665 (−1.59%), reattachment 1.2534 vs 1.100 (+13.95%, the documented SST bubble-length bias), 5.25 core-min total. Challenge-conditions run approved at 60 core-min — mispriced by >10× against its own measured rungs; QCR arm (+8) ordered 2026-08-07. | `campaign/F6a_*` , `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` §2 |
| 2D periodic hills | **F6b** | Verdict on OUR mesh: verification PASS (0.043% vs shipped grid), physics FAIL as pre-registered (+72% reattachment vs the Rapp/Breuer/Fröhlich band). Open successor: why the finest rung will not converge (55 core-min, on docket). | `campaign/F6b_ERCOFTAC_{PREREGISTRATION,RESULTS}.md` |
| Backward-facing step | **F5c** | AMENDED 2026-08-10 (see `F5C_STAGE_A_RESULTS.md`): headline WITHDRAWN to unmeasured, and no F5c run has ever converged. Prior text: Diagnosed-open: converged solves land x_r/H 0.49–1.49 vs 6.26±0.10 (4–12× wrong), wandering non-monotonically while residuals converge cleanly. OOM premise refuted in our own record. Supervisor ordered the inlet-audit-then-unsteady sequence 2026-08-07 (0 then ~25 core-min). **Filed by this slate.** | `NOT_PASSING_REGISTER.md` §F5c, supervisor review §5 |
| Deep dynamic stall NACA 0012 | **F5b** | Approved (120 core-min) but reference-blocked: TP-1100 publishes case (e) as scanned strip charts, no machine-readable CL(α) loop. A digitised replot must be found and tiered, or the case re-targeted, before a core-second is spent. | `NEXT_CASES_SLATE.md` item 6 |
| ONERA M6 | **F1 + A3** | F1 done (Cp vs AGARD AR-138, CD 0.02299556). A3 adjoint hard-blocked by conditioning at every mesh size — the M6 story is now an adjoint story, not a primal one. | `campaign/CAMPAIGN_STATUS.md`, `dafoam/R5_ADJOINT_CONDITIONING.md` |
| DrivAer / Ahmed | **Ahmed: done extensively** | A4 adjoint PASS 1.10% (np=1 stock, graded config); the decomposition-defect case file is filing-ready; R4 asymptotic ladders run; 35° ladder approved (27 core-min, measured basis). DrivAer itself: never run — see NEW below. | `dafoam/DAFOAM_CASE_STATUS.md`, product list §4E |
| NASA CRM / DPW | **A6 + scoping** | A6 wing-alone primal converged, CD matches the published tutorial to 0.0067% (provisional). `docs/DPW-CRM-SCOPING.md`: STRONG GO staged, 37 core-hours minimum entry, 135 ch entry-quality, 150–200 ch allocation, priced from the lab's own measured rate. DPW5 hex ladder (400 core-min) and DPW8 OAT15A already on the docket. | `docs/DPW-CRM-SCOPING.md` |
| NACA 4412 trailing-edge separation | **W3 line, partially** | What exists is the finite-wing drag-credential scatter work: five replicate meshes, NOT VALIDATED on all four graded rungs, drag range 1.69× the acceptance half-band; two repair proposals on the docket. **The trailing-edge-separation case per se (Wadcock, high incidence) has never been run** — it is a new regime inside an existing family. | `campaign/W3_NACA4412_LAYERED_REPLICATES.md` |
| Taylor-Green vortex Re=1600 | none | Zero hits repo-wide. Greenfield, cheap, sits on the proven single-phase transient stack. **Filed by this slate.** | this file §5 |
| 2D duct family (context for the 3D supersonic duct) | **F6c + closure line** | AR_1/AR_3/AR_14 are the closure challenge's ducts; QCR2000 built and scored (AR_1 0.0811→0.0455, AR_3 0.0775→0.0400, round-5 rank 1 locally — P(rank 1) = 68%, and the lead is **not statistically decided** against Reissmann or Wu & Zhang, though it is against Liu and Montoya; the standing is two cases wide and AR_1/AR_3 are ties below published precision; internal only, see `campaign/PROBABILITY_OF_RANK_2026-08-10.md`). All incompressible Re_τ 180/360. **The 3D supersonic square duct is genuinely new** — and it is the natural compressible test of the same QCR term. | `CLOSURE_CHALLENGE_STATUS.md` |

### Genuinely new (11 of 21)

Turek-Hron FSI3, Hysing rising bubble Case 2, shock-bubble interaction,
Rayleigh-Taylor, double Mach reflection, NASA Rotor 37, NASA Juncture Flow,
KCS/KVLCC2, DLR-F6 WBNP, Caradonna-Tung, CRM-HL. One asterisk: CRM-HL is
greenfield in compute but not in paper — `hlpw6-testcase1-coarse-grid-entry`
already sits on the docket at 6,390 core-min (pre-schema, no hard_criterion
field, and its `challenge` source_kind predates the closed gain table; the
closure challenge is the only challenge the lab is entered in, so on today's
table it prices as `measurement`).

### Two corrections to the slate's own premises, caught while mapping

1. **The F7a "sign flip" is retracted, and the prerequisite must be stated in
   its current form.** The 2026-07-30 re-measurement withdrew both the
   coarse-mesh sign flip and the interface-compression finding as metric
   artifacts: under the depth-integrated front metric all five rungs
   overpredict with the same sign (+11.1 to +13.5%). The standing record is a
   mechanism-diagnosed FAIL — wall friction on the sub-millimetre dry-bed
   film, wall-normal refinement takes it to +8.2%, a slip floor undoes the
   gain — against a declared 5% tolerance, at 389.8 core-min spent. The
   prerequisite for every ship entry is therefore not "diagnose the sign
   flip" but **"make the free-surface stack pass its cheapest case"**, which
   it still does not. Loose end folded in here: the untracked
   `F7_runs/F7a_R1/res16_alphaco/` time directories are the completed
   alpha-Courant sub-cycling arm (its result is committed in
   `m_res16_alphaco.json`); adopt-or-prune before anything overwrites them.
2. **The Juncture Flow dataset is LDV-led, not tomo-PIV.** NASA's reference
   data are laser-Doppler velocimetry (v6, with Reynolds stresses) plus
   surface pressures and PIV posted 2020, per NASA TMR's own data page.
   The correction changes nothing about the case's value; it changes what a
   proposal may claim to grade against.

---

## 2. Capability gaps, measured on this box

Inventory, measured 2026-08-07: native `openfoam2606` (v2606) carries
simpleFoam, pimpleFoam, rhoCentralFoam, rhoSimpleFoam/rhoPimpleFoam,
sonicFoam, **interFoam, interIsoFoam, compressibleInterFoam (+DyM),
multiphaseEulerFoam, twoPhaseEulerFoam**, the overset family
(overPimpleDyMFoam etc.), SRFSimpleFoam, and cyclicAMI as a core mesh
capability. Docker holds only the two DAFoam images and alpine.
**solids4Foam, preCICE, blastFoam: zero hits repo-wide, not installed, no
image.** Per the charter, capabilities enter via pre-registered capability
rungs, not by leaping to the hardest case.

| gap | blocks | what exists today | cheapest unlocking rung |
| --- | --- | --- | --- |
| **Coupled FSI** | Turek-Hron FSI3 | Nothing. No solids solver, no coupling library, anywhere. | Capability rung (2.0 pts): build solids4Foam against openfoam2606 (it targets OpenCFD versions; build risk is the real cost) and pass its own shipped FSI tutorial as the instrument check. Only then does FSI3 — which has exact published benchmark values — become a gateable case. preCICE+CalculiX is the fallback, strictly heavier. |
| **Compressible multiphase under shocks** | shock-bubble (Haas-Sturtevant) | compressibleInterFoam is in-image but has never been exercised here, and a pressure-based VOF solver under a Ms=1.22 shock is a claim, not a fact. No blastFoam-class capability. | Capability rung (2.0 pts, ~15 core-min): a two-gas shock tube with an interface, graded against the exact Riemann solution — it either qualifies the solver for the bubble or refuses it at one rung's cost. |
| **Trusted free surface** | KCS/KVLCC2, Wigley (F7b/F7c), and honestly Hysing and Rayleigh-Taylor too | interFoam runs but its cheapest case FAILS its gate: F7a at +8.2% best vs the declared 5%, mechanism named (dry-bed film friction), sign-flip framing retracted. | **Prerequisite, already the lab's own rule: F7a-fix passes before any hull.** The two-phase benchmarks are the honest intermediate rungs: Hysing Case 2 has benchmark-grade quantitative references and no dry bed, so it separates "interFoam interface capture is broken generally" from "the dam-break film mechanism is specific". KVLCC2 has a double-body variant (no free surface, criterion 1 via the aft-body vortex) that dodges the gap entirely and is a legitimate separate rung. |
| **Rotating machinery, transient** | Rotor 37, Caradonna-Tung, F8 transient branch | MRF exists and F8 bounds what we know: steady-MRF closed three ways on evidence (geometry exonerated, frame terms clean, initialisation trap named — potentialFoam baked the frame sweep into the zone). AMI named in the record as the next qualitatively different step, never run. SRF and overset are in-image, unexercised. | Caradonna-Tung hover IS the rung: steady in the rotating frame, tip Mach moderate, tabulated Cp in a NASA report — the first external-reference rotating gate, directly inheriting F8's initialisation lessons. Rotor 37 additionally needs a transonic blade-passage mesh with tip gap and performance-map boundary conditions; it stays behind both this rung and a meshing capability nobody has priced. |
| **Big-grid 3D throughput** | CRM-HL (2.66M coarse grid), Juncture Flow, DPW fine levels | 16 cores, 30 GB. DPW scoping's own arithmetic: coarse 7.2M = 18–24 core-hours; the HLPW6 docket item prices 6,390 core-min. | Not a solver gap, a budget gap: these enter only through the compute-budget charter's rung caps with escalation, and the DPW committee-grid route (grids on disk, hashes recorded) stays the cheapest 3D-credential path because it removes mesh-generation risk entirely. |

Double Mach reflection needs **no new capability**: rhoCentralFoam is the
proven F3/F4 line, run natively.

---

## 3. Reference data per entry

Verification here means: the canonical source exists, the citation is real,
and fetchability is stated. Nothing was bulk-fetched.

| entry | canonical reference | fetchable? |
| --- | --- | --- |
| Turek-Hron FSI3 | Turek, S. & Hron, J. (2006), "Proposal for numerical benchmarking of fluid-structure interaction…", LNCSE 53, Springer | Yes — exact benchmark values (tip-displacement mean/amplitude/frequency, drag, lift) tabulated; mirrored on the FeatFlow benchmark pages |
| Hysing bubble Case 2 | Hysing, Turek, Kuzmin, Parolini, Burman, Ganesan, Tobiska (2009), IJNMF 60:1259–1288 | Yes — quantitative benchmark quantities (circularity, centroid, rise velocity) from three codes, tabulated |
| Shock-bubble | Haas, J.-F. & Sturtevant, B. (1987), JFM 181:41–76; Quirk & Karni (1996), JFM 318:129–163 | Paywalled originals; interface-velocity tables widely reproduced in open literature — tier the relay |
| Dynamic stall 0012 | McAlister, Carr & McCroskey (1978), NASA TP-1100 | On disk, parsed — and the known problem: case (e) loads are strip charts, no machine-readable loop; a tiered digitised replot is the unblocking artifact |
| Wall-mounted hump | Greenblatt et al. (2006), AIAA J 44(12); NASA TMR 2DWMH | On disk (benchmark clone + TMR fetches) |
| Rayleigh-Taylor | Liska & Wendroff (2003), SIAM J Sci Comput 25(3):995–1017; Tryggvason (1988), JCP 75:253–282 | Yes — but code-comparison only, no experiment: anchor-2-class at best, and the proposal must say so |
| 2D periodic hills | Rapp & Manhart (2011), Exp Fluids 51; Breuer et al. (2009), Comput & Fluids 38:433–457; ERCOFTAC UFR 3-30 | On disk, already graded against |
| NACA 4412 TE separation | Coles & Wadcock (1979), AIAA J 17(4):321–329; Wadcock (1987), NASA CR-177450; NASA TMR carries the validation case | Yes — TMR page + NTRS |
| Backward-facing step | Driver & Seegmiller (1985), AIAA J 23(2):163–171 | Digitised in our record (x_r/H 6.26±0.10) |
| Double Mach reflection | Woodward & Colella (1984), JCP 54:115–173 | Yes — the reference IS the benchmark computation; grading is against its self-similar structure, stated as such |
| CRM-HL | AIAA High-Lift Prediction Workshops (HLPW-3/4); NASA/QinetiQ CRM-HL wind-tunnel campaigns | Yes — committee grids and geometry public; the docket's HLPW6 item names the 2.66M coarse grid |
| CRM / DPW | DPW-VI: Tinoco et al. (2018), J Aircraft 55(4); NTF/Ames CRM tests (Rivers) | Committee grids ON DISK with hashes; scatter bands in `docs/DPW-CRM-SCOPING.md` (median 257 counts, IQR ±4–5) |
| Rotor 37 | Reid & Moore (1978), NASA TP-1337; Suder (1996), NASA TM-107276; Dunham (1998), AGARD AR-355 blind test | Yes — NTRS; the AGARD blind-test scatter is the honest grading context |
| Juncture Flow | Rumsey et al. (2022), "NASA Juncture Flow CFD Validation Experiment", AIAA J (doi 10.2514/1.J061600); data at NASA TMR | Yes — LDV v6 + pressures + PIV (not tomo-PIV; see §1 correction) |
| KCS / KVLCC2 | Gothenburg 2010 workshop (Larsson, Stern, Visonneau, eds., Springer 2014); KCS towing data Kim et al. (2001), MOERI; SIMMAN for manoeuvring | Partly — workshop data typically behind registration; KVLCC2 wind-tunnel double-body wake data published openly |
| DLR-F6 WBNP | DPW-II/III: Laflin et al. (2005), J Aircraft 42(5):1165–1178; ONERA S2MA experiment | Yes — geometry and grids on the NASA DPW site |
| ONERA M6 | Schmitt & Charpin (1979), AGARD AR-138 | On disk, already graded against (F1) |
| DrivAer / Ahmed | Heft, Indinger & Adams (2012), SAE 2012-01-0168; Ahmed, Ramm & Faltin (1984), SAE 840300 | Ahmed on disk; DrivAer geometry open (TUM), experimental Cd published |
| Taylor-Green Re=1600 | Brachet et al. (1983), JFM 130:411–452; van Rees et al. (2011), JCP 230:2794–2805; HiOCFD workshop reference data (Wang et al. 2013, IJNMF 72:811–845; DeBonis, AIAA 2013-0382) | Yes — tabulated spectral dissipation histories distributed with the workshop case |
| 3D supersonic square duct | Davis & Gessner, "Experimental and numerical investigation of supersonic turbulent flow through a square duct", AIAA J (doi 10.2514/3.9473) — Mach 3.9, D=25.4 mm, x/D≤50; NASA TMR hosts it as the 3D Supersonic Square Duct validation case | Yes — TMR page, verified 2026-08-07 |
| Caradonna-Tung | Caradonna, F.X. & Tung, C. (1981), NASA TM-81232, hover rotor, tabulated blade Cp | Yes — NTRS |

---

## 4. The ranked program

Ranked by the charter's arithmetic. Kind and points per the closed gain
table; estimates anchored to measured history where it exists and flagged
`unknown` where it does not. Wall predictions are for this 16-core, 30 GB
box.

| # | entry | kind (pts) | est core-min (basis) | rank | HARD | predicted wall | first rung |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | F6a hump at challenge conditions | challenge (4.0) | 6 (measured: own rungs cost 5.25 total) | **0.667** | 6 | ~2 min | Already approved; its first task is the re-pricing from 60, per the standing slate |
| 2 | Double Mach reflection | measurement (3.0) | 20 (anchored: F4 rungs, single-digit each) | **0.150** | 2 | ~5 min at 4 ranks | **FILED** — pre-register locator increment before any solve |
| 3 | Two-gas shock tube (unlocks shock-bubble) | capability (2.0) | 15 (estimate) | 0.133 | instrument-check | ~4 min | Only pays if the compressible-multiphase line is opened — a program call for the docket, not this file |
| 4 | F5c inlet audit, then unsteady probe | gate (3.0) | 25 (audit 0; probe sized on the measured 26.9 for six runs) | **0.120** | existing-family | 0, then ~6 min | **FILED** — supervisor wording binding |
| 5 | Rayleigh-Taylor single-mode | measurement (3.0) | 30 (estimate, unknown) | 0.100 | 4 | ~8 min | Blocked soft: reference is code-comparison only, and it rides the interFoam stack that fails F7a |
| 6 | NACA 4412 trailing-edge separation | measurement (3.0) | 30 (estimate vs hump-class 2D RANS) | 0.100 | existing-family | ~8 min | New regime, existing family; Wadcock is TMR-hosted |
| 7 | Hysing bubble Case 2 | measurement (3.0) | 40 (estimate) | 0.075 | 4 | ~10 min | The first filing when the two-phase line opens: benchmark-grade reference, no dry bed — doubles as the F7a stack discriminator |
| 8 | Shock-bubble main rung | measurement (3.0) | 40 (estimate) | 0.075 | 2+4 | ~10 min | Contingent on rung 3 passing |
| 9 | Taylor-Green Re=1600, first rung | measurement (3.0) | 50 (estimate, no family history) | 0.060 | 3 | ~6 min at 8 ranks | **FILED** — see §5 for why it was filed over rows 5–7 |
| 10 | F6b finest-hill successor | gate (3.0) | 55 (on docket) | 0.055 | existing-family | ~15 min | Already on docket |
| 11 | FSI3 capability rung (solids4Foam build + shipped tutorial) | capability (2.0) | 60 compute (install wall-hours dominate, unknown) | 0.033 | instrument-check | half a day, install-bound | Unlocks the only slate entry with exact published FSI values |
| 12 | F5b pitching 0012 | gate (3.0) | 120 (approved) | 0.025 | 3 | ~30 min/period | Reference-blocked: find a tiered digitised TP-1100 loop first, or re-target |
| 13 | Caradonna-Tung hover | measurement (3.0) | 150 (unknown) | 0.020 | 5 | ~40 min | The rotating-line unlocking rung; inherits F8's initialisation lessons verbatim |
| 14 | DrivAer | measurement (3.0) | 250 (estimate vs Ahmed history) | 0.012 | 1 | ~1 h | Geometry fetch + snappy recipe transfer from Ahmed |
| 15 | 3D supersonic square duct | measurement (3.0) | 300 (unknown) | 0.010 | 2 | ~1–2 h | blockMesh-trivial geometry; the real content is QCR under compressibility vs Davis-Gessner — the F6c structural-limit story's compressible sequel |
| 16 | KVLCC2 double-body | measurement (3.0) | 300 (unknown) | 0.010 | 1 | ~1–2 h | The ship entry that dodges the free-surface gap; full KCS stays blocked on the F7a gate |
| 17 | DPW5 hex three-level ladder | gate (3.0) | 400 (on docket; reconcile vs core-hour scoping first) | 0.0075 | 2+1 | hours | Committee grids on disk |
| 18 | DLR-F6 WBNP | measurement (3.0) | ~1,200 (scoping-rate anchored) | 0.0025 | 2+1 | overnight | Behind the CRM/DPW line, same machinery, adds nacelle-pylon separation |
| 19 | Juncture Flow | measurement (3.0) | ~1,800 (unknown) | 0.0017 | 1 | 1–2 days | Corner-flow mesh + LDV stations; the honest 3D-separation credential |
| 20 | Rotor 37 | measurement (3.0) | ~2,000+ (unknown, meshing-blocked) | 0.0015 | 5+2 | days + unpriced meshing | Behind Caradonna-Tung and a passage-meshing capability rung |
| 21 | CRM-HL (HLPW) | measurement (3.0) | 6,390 (docket item) | 0.0005 | 1 | ~4+ days — over any rung cap, escalation required | The docket's pre-schema `challenge` kind does not survive the closed table unless the lab enters HLPW, which is Katie's call |

Reading the table honestly: the top of the program is not a new case at all —
it is a re-pricing (row 1) and two filings on families the lab already owns
(rows 2 and 4). The genuinely-new entries that clear 0.05 are exactly the
cheap canonical 2D/periodic cases; every 3D marquee entry prices below 0.012
on today's box, which is the arithmetic saying what the DPW scoping already
said: 3D credentials are bought in core-hours, through staged gates, or not
at all.

---

## 5. What was filed, and where the arithmetic disagreed with the brief

Three proposals, schema-complete, intake-validated (zero violations through
`agenda.proposal_violations` on 2026-08-07), in
`demo-output/website/agenda/proposals/`:

1. `double-mach-reflection-woodward-colella` — measurement, criterion 2,
   20 core-min, rank 0.150. Highest-ranked new case; proven solver line;
   detector-first gate per the F3 shock-locator lesson.
2. `f5c-inlet-audit-then-unsteady-probe` — gate, existing-family,
   25 core-min, rank 0.120. Carries the supervisor's two ordered FILE items
   verbatim in their conditional order, plus the slate's zero-cost
   nondimensionalisation check ahead of both.
3. `taylor-green-re1600-first-rung` — measurement, criterion 3, 50 core-min,
   rank 0.060.

**The disagreement, stated rather than smoothed over:** the raw ratios put
Rayleigh-Taylor (0.100) and Hysing (0.075) above Taylor-Green (0.060), so
the brief's expected third filing is not the arithmetic's third row. But all
three denominators are unmeasured estimates within a factor of two of each
other, inside the noise band of a charter that only grades cost predictions
at a factor of three — so the ratio does not actually decide, and pretending
it does would be inventing precision. The tie was broken on instrument
grounds instead: Taylor-Green runs on a stack every piece of which is proven
(pimpleFoam, native, no closure model in the loop) against a tabulated
spectral reference, and it is the instrument the already-approved F5b and
the F8 transient branch inherit. Rayleigh-Taylor and Hysing both ride
interFoam while its cheapest case fails its own gate at +8.2% with the
mechanism still open — starting a new family on a stack with a standing FAIL
entangles two questions, which is the exact shape L-26 warns about: a
control that cannot distinguish the answers is not a control. When the
two-phase line is opened deliberately, **Hysing Case 2 should be its first
filing, ahead of Rayleigh-Taylor** — benchmark-grade quantitative reference
against code-comparison-only — and it doubles as the discriminator for
whether the F7a failure is general or film-specific.

Not filed, and why: the two-gas shock tube (row 3) outranks F5c on paper but
its 2.0 points exist only if the compressible-multiphase line is opened,
which is a program decision the docket should make with Katie's priority
line, not a scoping file. The hump re-pricing (row 1) is already an approved
item's first task, and filing it again would be the `no-case` distinction
the charter exists to keep clean.

---

*Written 2026-08-07 by the campaign-scoping agent. Sources: the two
charters, `docs/PRODUCT_LIST.md`, `NEXT_CASES_SLATE.md`,
`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`, `docs/DPW-CRM-SCOPING.md`,
`CLOSURE_CHALLENGE_STATUS.md`, the campaign records named per row, the
openfoam2606 binary inventory and docker image list measured on this box, and
NASA TMR pages for the square-duct and Juncture Flow datasets (verified
2026-08-07).*
