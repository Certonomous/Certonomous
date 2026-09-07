# DMR R3 L2 COURANT PROBE — FINE-ONLY dt lever — PRE-REGISTRATION

> **STATUS: AUTHORISED — FROZEN — 2026-09-07 — NO COMPUTE RUN YET.**
> Authored by a cfd `lab-lane`, 2026-09-07. This becomes a frozen pre-registration
> ONLY when the cfd supervisor takes **check-1** (the L-339 guarded source region of
> the driver) and **check-4** (generator / driver / prereg gates) PERSONALLY and
> freezes it by sha. None of that has happened here. The banner flip DRAFT ->
> AUTHORISED is the freeze; until then the gate, threshold, cap and label below are a
> proposal, not a commitment. Rules 2, 3, 4, 6, 10, 12, 13 apply.
>
> This is a **ROBUSTNESS PROBE, NOT A ROACHE TRIPLE** (§1, §3): ONE level (N=240)
> only, no grid-convergence triple, **no GCI, no Gate T'**. Heeds L-501: a SIGFPE of
> this probe is a MEASURED negative result diagnosed answer-blind by the check-1'd
> reader, never a capability inference from one crash.
>
> **FREEZE STAMP — 2026-09-07 (cfd supervisor).** check-1 (the L-339 guarded
> source region of the driver) and check-4 (generator / driver / prereg gates)
> taken PERSONALLY: both PASS. Frozen by sha against four pinned instruments
> verified on-disk at freeze:
> - generator `make_case_tadmor_co05.py` sha256 `da5e5d0036bf540058c910c4b2fee4ca6dd94fdc08403e9b3b146d3b1a9543ed`
> - driver `run_dmr_l2_courant_probe.sh` sha256 `f244e54c5394739a3f822e7d693c337acaa60bdd49f379c2543d20ea2e839d5d`
> - grader `dmr_locator_v2.py` git blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`
> - reader `step0_negativity_reader.py` sha256 `c7da80cee99b5d7143d28beb8af51e02d819e67050c8dbc730a244e3db1e02e3`
> Run root `verification/runs/DMR_R3_L2_COURANT_PROBE_runs` ABSENT at freeze. No
> gate / threshold / cap / label altered by this freeze — banner + this stamp only.

---

## 0. Lineage and the measured mechanism this probe tests

- **Parent family:** the DMR **Tadmor-flux successor** (freeze `08efee1a` line; prereg
  `DMR_R3_TADMOR_SUCCESSOR_PREREGISTRATION.md`), which applied lever **L1** — flux
  Kurganov → Tadmor at maxCo 0.1 — uniformly to a three-level triple.
- **Measured L1 result at the finest level (R3t, N=240):** Tadmor **delayed but did
  not cure** the energy-positivity collapse. The R3t solve reached **t = 0.15005683**
  and then `rhoCentralFoam` SIGFPE'd (rc=136), versus the earlier positivity-successor
  R3p crash at **t = 0.116**. The crash moved forward but **did not reach endTime
  t = 0.2**. (`verification/runs/DMR_R3_TADMOR_SUCCESSOR_runs/R3t/log.rhoCentralFoam`,
  `PROGRESS.txt`.)
- **STEP-0 measured mechanism (answer-blind, N=240):** internal energy `e` goes
  negative at the **cell centre** (reader line 136) — an energy-positivity collapse,
  not a boundary artefact. This is the field the dt lever must protect.

The **L2 lever isolated here:** hold the Tadmor flux and **halve the time step**
(controlDict `maxCo 0.1 -> 0.05`) at the finest level only, and measure whether the
smaller Courant step keeps `e` positive all the way to t = 0.2.

## 1. FALSIFIABLE PROPOSITION

> **Does N=240, Tadmor flux, `maxCo 0.05` reach endTime t = 0.2 WITHOUT a SIGFPE?**

The probe answers yes/no by running exactly that one case to t = 0.2 (or to its
crash) and recording the solver rc and the last solver time. It is falsifiable in one
run: a clean `End` at t = 0.2 confirms the dt lever works at fine; a SIGFPE before
t = 0.2 falsifies it.

## 2. INSTRUMENTS — ON DISK, CITED BY HASH, ROOT ABSENT

- **Generator (new, single-lever):**
  `verification/runs/DMR_runs/make_case_tadmor_co05.py`, sha256
  `da5e5d0036bf540058c910c4b2fee4ca6dd94fdc08403e9b3b146d3b1a9543ed`. It is
  `make_case_tadmor.py` (sha256
  `f08ddd6884f16ef89146723ba2ae79ba8efff639935b0a0dc1ac5b29b23bb0bc`) with the SINGLE
  change `controlDict maxCo 0.1 -> 0.05`. PROVED (§9): `diff -r` of the two N=240
  output trees differs by **EXACTLY** `system/controlDict:21` `maxCo 0.1;` ->
  `maxCo 0.05;` and nothing else.
- **Probe driver:** `verification/runs/DMR_runs/run_dmr_l2_courant_probe.sh`, sha256
  `f244e54c5394739a3f822e7d693c337acaa60bdd49f379c2543d20ea2e839d5d`. FINE-ONLY (N=240),
  endTime 0.2, `set -u` with the **L-339 guarded source** (export USER; `set +u`;
  source openfoam2606 bashrc; `set -u`), a `fieldMinMax` functionObject on `(T e p rho U)`
  `location yes` `writeControl timeStep`, its **own hard cap** (§6), **rc captured inside
  the wrapper** per step, the **rule-4 ABSENT guard** on the fresh root, and a branch: IF
  it reaches t=0.2 it hashes the grader against `52aacf9669…` and grades the single-level
  Gate V' (informative); IF it SIGFPEs it runs the reader to diagnose the negative field/site.
  `bash -n` clean (§9).
- **Grader (REUSED UNCHANGED, pinned, rule 6):**
  `verification/runs/DMR_runs/dmr_locator_v2.py`, git blob
  `52aacf9669bcf23e88a0bf7984b299fa8aaf286e` (`GATEV_TOL = 0.0231` at :69). The driver
  hashes it against this blob at grade time and refuses on mismatch (rule 2). Used
  ONLY IF the probe reaches t=0.2.
- **Diagnostic reader (REUSED UNCHANGED, pinned, rule 6):**
  `verification/runs/DMR_runs/step0_negativity_reader.py`, sha256
  `c7da80cee99b5d7143d28beb8af51e02d819e67050c8dbc730a244e3db1e02e3` (the cfd supervisor
  check-1'd it for the Tadmor successor). Carries a two-sided planted-zero control (rule 3):
  refuses (exit 2) if it cannot read back a planted negative extremum. Used IF the probe SIGFPEs.
- **Run root:** `verification/runs/DMR_R3_L2_COURANT_PROBE_runs` — **DECLARED ABSENT on
  disk at authoring** (§9). A fresh full run from t=0; there is no restart seed, so the
  rule-4 ABSENT guard applies in full and the driver refuses if the root exists.

## 3. THIS IS A ROBUSTNESS PROBE, NOT A ROACHE TRIPLE

Explicitly: this pre-registration runs **ONE level (N=240)**. It produces **no
grid-convergence triple, no GCI, and no Gate T'**. Rule 5 is not invoked. The single
Gate V' grade (§4), if the probe reaches t=0.2, is **INFORMATIVE kinematics only** —
it does not and cannot certify grid convergence. A CONVERGING triple, if the dt lever
survives, is a SEPARATE future rung (see the outcome map §5), pre-registered on its own.

## 4. GATE V' — BYTE-IDENTICAL, GRADED ONLY IF t=0.2 IS REACHED

- **Gate V' (kinematics vs exact theory):** IF (and only if) the probe reaches t=0.2,
  the single level is graded PASS iff `|x_measured − x_exact_at_row| ≤ **0.0231**`.
  **BYTE-IDENTICAL to the parent** — `GATEV_TOL = 0.0231` (`dmr_locator_v2.py:69`)
  equals the `0.0231` literal in `DMR_PREREGISTRATION.md`, the positivity successor
  prereg and the Tadmor successor prereg. No band moved, no threshold widened.
  This grade is INFORMATIVE (single level, §3), not a triple verdict.
- **Controls (rule 3):** the grader's planted 7-whole-cell density displacement,
  planted-absence refusal, and the 1e-12 regression; the reader's two-sided
  planted-zero control (used on a SIGFPE).
- **No gate / threshold / band / cap / label is altered by this probe** relative to
  the parent — asserted (§9).

## 5. OUTCOME MAP — the probe decides the next rung, not the gate

| Measured outcome | Reading | Next rung (a SEPARATE pre-registration) |
|---|---|---|
| **Reaches t=0.2 (clean `End`)** | the **dt lever works at fine**: halving the Courant step cures the energy-positivity collapse Tadmor only delayed. | a **uniform maxCo-0.05 THREE-level Roache triple** (its own prereg, its own ~90 core-min cap, its own Gate T'), to certify convergence. |
| **Still SIGFPEs before t=0.2** | the **dt lever is EXHAUSTED at fine**: neither the more-diffusive flux (L1) nor halving the step (L2) keeps `e` positive at N=240. The reader records which field/site (expected `e` at cell centre). | **escalate to L5 (bounded-energy solver patch)** as a COSTED proposal to the chief — the capability/tooling boundary, chief's research-direction call (rule 9). |

Neither branch changes any gate, threshold, cap or label of THIS probe. The probe
only measures; the outcome selects a future proposal.

## 6. COST — measured-anchored estimate, honest cap, derived-$ labelled derived

- **Measured anchor:** R3t (N=240, Tadmor, maxCo 0.1) reached **t=0.15** with a solve
  cost of **29.1 core-min** (437 wall s × 4 ranks ÷ 60; measured from
  `DMR_R3_TADMOR_SUCCESSOR_runs/R3t/log.rhoCentralFoam` and `PROGRESS.txt`).
- **Projection:** to full t=0.2 at maxCo 0.1 ≈ 29.1 × (0.2/0.15) ≈ **38.8 core-min**.
  **maxCo 0.05 halves the step, doubling the step count** ≈ 2 × 38.8 ≈ **~77.7 core-min**
  for the solve; pre-solve (blockMesh/checkMesh/setExprFields/decomposePar) ≈ 0.4
  core-min (R3t measured). **ESTIMATE ≈ 78 core-min.**
- **Registered hard cap: ~90 core-min** (headroom over the ~78 estimate for the extra
  steps a smaller step accrues; rule 12 STOPS the run on breach — no new budget). One
  accumulator across all steps, enforced in the driver.
- **Derived dollars (DERIVED, NOT MEASURED — the box cannot read its own billing,
  COMPUTE_BUDGET_CHARTER §5):** at $0.0513/core-h, ~78 core-min ≈ **$0.067**; at the
  ~90 core-min cap ≈ **$0.077**. **Well under the $25 pre-authorised ceiling** (rule 12).
- **Rule-12 calibration** (est vs actual) is owed at process completion into
  `docs/COST_CALIBRATION.md`.

## 7. WHAT WOULD FALSIFY / WHAT WOULD NOT COUNT

- A SIGFPE before t=0.2 falsifies the proposition (dt lever insufficient at fine).
- A **CAP BREACH** (rule 12) STOPS the run and is **NOT** a physics result — it is
  `BLOCKED` on cap, reported not absorbed.
- A pre-solve step failure (rc≠0 on blockMesh/checkMesh/setExprFields/decomposePar) is
  a broken-case abort, **NOT** a physics finding.
- A single Gate V' PASS at t=0.2 is **informative, not a convergence certificate** (§3).

## 8. NO SEND (rule 7)

Nothing here is sent, filed, uploaded, registered, posted or commented. This is a
DRAFT parked pending the cfd supervisor's check-1 and check-4.

## 9. SELFTESTS TAKEN AT AUTHORING (2026-09-07)

1. **Generator one-line proof:** `diff -r` of `make_case_tadmor_co05.py` N=240 output
   vs `make_case_tadmor.py` N=240 output = EXACTLY one hunk, `system/controlDict:21`
   `maxCo 0.1;` -> `maxCo 0.05;`. Nothing else differs. ✔
2. **Driver `bash -n`:** CLEAN (rc=0). ✔
3. **Driver L-339 dry-source proof (driver uses `set -u`):** in isolation,
   `set -u; export USER=…; set +u; source …/openfoam2606/etc/bashrc; set -u; echo REACHED`
   printed **REACHED** and `command -v rhoCentralFoam` resolved to
   `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/rhoCentralFoam`
   — the guarded block survives `set -u` and the solver is on PATH. ✔
4. **Grader blob unchanged:** `git hash-object dmr_locator_v2.py` =
   `52aacf9669bcf23e88a0bf7984b299fa8aaf286e` (frozen). ✔
5. **Reader sha256 unchanged:** `step0_negativity_reader.py` =
   `c7da80cee99b5d7143d28beb8af51e02d819e67050c8dbc730a244e3db1e02e3` (check-1'd). ✔
6. **Run root ABSENT:** `verification/runs/DMR_R3_L2_COURANT_PROBE_runs` does not exist. ✔
7. **Gate V' 0.0231 byte-identical** to the parent literal (grader `:69`). ✔

**NO GATE / THRESHOLD / BAND / CAP / LABEL ALTERED — asserted.** Gate V' tol **0.0231**;
cap **~90 core-min**; label DRAFT / NOT AUTHORISED. The freeze (check-1 + check-4 by the
cfd supervisor, banner flip by sha) is the only act that may change the banner.
