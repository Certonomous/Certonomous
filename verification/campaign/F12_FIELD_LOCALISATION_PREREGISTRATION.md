# F12 — FIELD-LOCALISATION PROBE: PRE-REGISTRATION

**cfd lane, 2026-08-25. Registered BEFORE the compute it covers.**
Commissioned by `verification/runs/F12_runs/RUNG2_DISPOSITION_AND_CRASH_TRIAGE_2026-08-25.md` §3.4.
**This probe GRADES NOTHING.** It moves no gate, threshold, cap or label. Rung 1 stands
`NOT A RESULT`; rung 2 stands `BLOCKED`; neither is regraded here and the rung-2 interlock
is not touched. No verdict from the fixed vocabulary is due to this probe and none will be
issued. Its output is a location and an iteration number.

---

## 0. DISCLOSURE, IN THE OPENING LINES — THIS PROBE HAS ALREADY BEEN RUN ONCE, UNFROZEN

Before writing a line of this document I found the commissioned probe **already executed**,
at `verification/runs/F12_runs/field_observation_2026-08-25/` (run 18:20:07Z, results
18:30Z, `evidence/RC.txt` = 0, `evidence/WALL_S.txt` = 2.995 s). **Every file of it is
UNTRACKED — `git ls-files` returns nothing for that directory and it has no commit.**
Its own `PROBE_PREREGISTRATION.md` was therefore **never frozen by sha**, so standing rule 2
was not satisfied for it, and I cannot verify from disk that it preceded its own compute
(prose and evidence share an mtime of 18:28:52, the archival copy-in).

**I have therefore NOT back-dated a freeze over it, and this document does not cover it.**
Registering a "pre-registration" for a run already on disk is the precise fraud rule 2 exists
to prevent. What follows registers a **frozen, independent replication that has not yet run**.

**What this freeze does and does not prove.** It is NOT blind: I read the prior arm's results
before writing this. So it does **not** carry rule 2's usual evidentiary content that the
criterion could not have been chosen to fit the answer. It carries the weaker, real claim:
**the replication's criterion is fixed before the replication runs, so the replication cannot
be graded to fit its own outcome, and the §4 predictions below can FAIL.** The departure
thresholds in §3 are anchored in the frozen case's own registered values and in the solver's
own admissibility checks — **not** in any number from the prior arm.

---

## 1. THE QUESTION, STATED FALSIFIABLY

Where in the domain, and at which iteration, does the F12 rung-1 field first depart from its
uniform initial state — and does the departure originate at a **boundary/patch** (`inflow`,
`outflow`, `aerofoil` wall), at a **geometric feature** (leading edge, trailing edge, shock
band), in the **far field**, or in the **interior**?

**The discriminator is the ORDER in which regions depart** (§3, D3). Aerofoil/wall first
indicts the geometry, the near-wall mesh or the wall BC. Inflow/outflow first indicts a
boundary condition. All regions together indicts the initial state or the relaxation.

## 2. THE RUN — PHYSICS AND MESH UNCHANGED

Copy of `verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/`, executed
outside the repository under `/home/ubuntu/certonomous-runs/`.

**The ONLY permitted delta is `system/controlDict` output controls:**
`endTime` 6000 → 15; `writeControl timeStep` (already so); `writeInterval` 6000 → 1;
`purgeWrite` 1 → 0; `writeCompression off`.

**NOT changed, and asserted byte-identical before the run:** `system/fvSolution`,
`system/fvSchemes`, `system/blockMeshDict`, `system/decomposeParDict`, every `0/` field
(`T U p k omega nut alphat`), `constant/thermophysicalProperties`,
`constant/turbulenceProperties`, and all five of `constant/polyMesh/{points,faces,owner,
neighbour,boundary}`. No solver, smoother, preconditioner, tolerance, `relTol`,
`residualControl` entry, `nNonOrthogonalCorrectors`, `pMinFactor`, `pMaxFactor`, relaxation
factor, scheme or boundary condition is touched.

**CHANGING ANYTHING ELSE VOIDS THIS PROBE**, because a probe of a different case answers a
different question — and every arm on this line to date has been a lever swap. This is an
**observation** arm. If it cannot run without changing a lever, it STOPS and that fact is
itself the finding, reported unchanged.

**Reference state, from the frozen case:** `p_ref` = 101325 Pa, `T_ref` = 300 K (both uniform
initial fields), `U∞` = (254.55661283, 12.40536100, 0) m/s, |U∞| = 254.8587101 m/s,
`Cp` = 1004.5, `molWeight` = 28.96 → γ = 1.400, M∞ = 0.734. Patches: `aerofoil`, `inflow`,
`outflow`, `frontAndBack`. 23,040 cells.

## 3. WHAT IS READ, AND THE DEPARTURE THRESHOLDS — FIXED NOW, NUMERICALLY (L-284)

Per iteration `n` = 1…15, for every written field, the reader reports min, max, the **cell
index** of each extreme, that cell's **centre coordinates**, and its **nearest patch**.

Three departure criteria, all anchored in the frozen case, none in the prior arm's numbers:

- **D1 — `p` admissibility.** A cell is DEPARTED at `n` iff its **pre-clip** `p` lies outside
  `[pMinFactor·p_ref, pMaxFactor·p_ref]` = **`[10132.5, 202650]` Pa** — the case's own
  registered `fvSolution` `SIMPLE` bounds. **First departure `N_p` = the smallest `n` with
  count ≥ 1.** `p` on disk is censored by `pressureControl::limit()`, so the pre-clip extreme
  is taken from the solver's own `pressureControl:` print, which emits only on exceedance.
- **D2 — `T` admissibility.** A cell is DEPARTED at `n` iff `T ≤ 0` K or `T > 2·T_ref` = 600 K.
  The floor is **the solver's own range check**, `thermoI.H:56-60`
  (`if (T0 < 0) { FatalErrorInFunction << "Negative initial temperature T0: " << T0 <<
  abort(FatalError); }`) — **verified by me at source** in
  `/usr/lib/openfoam/openfoam2606/src/thermophysicalModels/specie/thermo/thermo/thermoI.H`.
  The ceiling mirrors `pMaxFactor`'s factor-2 convention.
- **D3 — ONSET, region-resolved, and this is the discriminator.** Seven registered regions:
  `aerofoil` wall cells; near field `r < 1.5c`; mid `1.5c ≤ r < 6c`; outer `6c ≤ r < 20c`;
  far `r ≥ 20c`; `inflow` patch; `outflow` patch (`c` = 1.0 m, `r` measured from `(0.25,0,0)`).
  A region is DEPARTED at `n` iff **`max|T − 300 K| > 0.5 K`** within it. The region's
  first-departure iteration is the smallest such `n`; **the reported answer is the ORDERED
  LIST of the seven regions by first-departure iteration.**
  **Why 0.5 K:** fields are written ascii at `writePrecision 10` from a uniform 300 K start,
  so an undeparted region reads exactly `300.000000`; 0.5 K sits ~6 orders above the write
  resolution. D3 asserts only that a region **has left its initial condition** — it makes no
  claim that 0.5 K is physically inadmissible, and must not be read as one.

If no criterion fires by `n` = 15, the registered answer is **"no departure within the
15-iteration window"**, which is a reading and directs an extension — not a null.

## 4. PRE-REGISTERED PREDICTIONS — THESE CAN FAIL, AND FAILURE IMPEACHES THE PRIOR ARM

- **P1 (faithfulness, and it gates everything else).** The replication's first-solve initial
  residuals must equal the **registered rung 1's own log** for all 15 iterations, every field.
  Registered check values from
  `verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam`:
  `p` = `1` (`n`=1), `0.009554815904` (`n`=5, the minimum), `0.2006112477` (`n`=10),
  `0.07671622987` (`n`=15). **Agreement required to 0 ulp** (same case, same binary, 1 rank).
  **If P1 fails, the probe case is not the rung-1 case and this arm is VOID** — no location is
  reported from it.
- **P2.** `N_p` (D1) **= 1**. If no `p` bound violation occurs at iteration 1, the prior arm's
  headline is impeached and this arm says so.
- **P3.** Under D3 the `aerofoil` wall and near-field regions depart **strictly before** the
  `inflow` and `outflow` patches. If a patch departs first or all seven depart together, the
  aerofoil-anchored reading is impeached.
- **P4.** D2 is **NOT** reached within `n` ≤ 15. Rung 1's `T ≤ 0` abort is at iteration 148.

## 5. PLANTED-ZERO CONTROL (STANDING RULE 3) — REGISTERED WITH ITS REFUSAL

No location and **no "no departure found"** may be reported by a reader not first shown able
to find a departure that is really there. Before any number is read, and **on a field written
by THIS arm's own run** (not a stored field), the reader plants into a copy on disk:
`PLANT_INTERNAL = -7.654321e+09` at **cell index 12345**, and `PLANT_PATCH = -1.357911e+09`
on a named patch. It reads the copy back **through the same code path** and requires five arms:
**POSITIVE** (the planted value is returned), **LOCALISATION** (reported at *exactly* cell
12345, not a neighbour), **PATCH** (a patch plant is reported on *that* patch), **PATCH
SPECIFICITY** (it does not leak to other patches), **NEGATIVE** (re-reading the *unplanted*
original returns no plant value, so "no departure here" is a reading and not a blind spot).

**Refusal behaviour: any arm not firing → the reader exits 2, and every number it produced is
WITHDRAWN.** The reader's sha256 is recorded at use, beside its output.

## 6. COST, RANKS, CONTENTION

- **Ranks: 1.** The registered rung 1 itself ran serial (`log.rhoSimpleFoam`, `nProcs : 1`),
  despite `decomposeParDict` naming 4 subdomains. **Rank count is part of the case**:
  decomposing would change GAMG agglomeration and would be a lever change voiding §2.
  Within the 2-core budget. **No clean-timing core reservation is taken.**
- **Cost basis — MEASURED**, from rung 1's own log
  (`.../attempt2_coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam`): `ExecutionTime = 1.64 s` at
  `Time = 15`, serial → **0.0273 core-min** for the 15-iteration solve, excluding field writes.
  Per-iteration cost 0.0898 s (13.29 s / 148 iterations, same log). Field writes, reader
  selftests and the `writeCellCentres` pass are **estimated** at ≤ 0.08 core-min.
  **Expected total ≈ 0.11 core-min.**
- **HARD CAP: 6.0 core-minutes** at 1 rank (= 6 wall minutes serial). ~55× expected, sized to
  cover the five reader selftests, one utility pass, and one permitted re-run should P1 fail
  for an environmental reason. **An overrun STOPS the run; it does not get a new budget.**
- **Derived, not measured:** 6.0 core-min = 0.1 core-h × $0.0513/core-h = **$0.005**. The box
  cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Contention:** `uptime` recorded at start and at end, into the run directory. At
  registration the box reads load 8.77 / 8.83 / 9.21 on 16 cores — heat-transfer and dafoam
  are live. Estimate-vs-actual is compared at completion per standing rule 12 and lands in
  `docs/COST_CALIBRATION.md`.

## 7. COMPLETION CLAUSES — AND THE EXPECTED OUTCOME IS `End`, NOT AN ABORT

**A correction to the commissioning brief, made before compute:** this probe is expected to
reach a **normal `End` with `rc = 0`**, *not* to abort. Rung 1's abort is at **iteration 148**,
far outside the 15-iteration window. Checked afterwards:

1. `rc = 0`; 2. an `End` line; 3. last time == `endTime` == **15**; 4. time directories
`1`…`15` all present; 5. fields present per written time — **`T U p k omega nut alphat`
plus `rho` and `phi`** (this case's list; **the thermal-family list does not apply here**);
6. **age guard** — every written field newer than the probe case's own `0/T`;
7. the registered rung-1 directory's sha256-of-sha256-list **unchanged before and after**;
8. rungs 2–5 asserted absent before and after.

**If it aborts before iteration 15, that is DATA, not instrument failure** — the fields up to
the abort are the evidence and are retained, and the abort iteration is itself reported. Such
an abort must not later be read as a failure of the probe.

## 8. WHAT IS NOT TOUCHED

`verification/campaign/F12_PREREGISTRATION.md` (frozen), `launch_f12_rung.py` and its rung-2
interlock, rung 1's own outputs, `cases/RANS_LES_closure_models/`, `cases/dafoam/`,
`scripts/analyse_f5b_physics.py`. Nothing is sent, filed or uploaded (standing rule 7).
