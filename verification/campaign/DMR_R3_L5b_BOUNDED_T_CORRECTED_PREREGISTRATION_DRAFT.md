# DMR R3 L5b — BOUNDED-T CORRECTED (field-anchored positivity clip) SUCCESSOR — PRE-REGISTRATION

> ## STATUS: **DRAFT — NOT FROZEN, NOT LAUNCHED.**
>
> The chief has APPROVED L5b as the fair test of the bounded-energy clip after L5
> graded **NOT A RESULT** on a miscalibrated instrument
> (`DMR_R3_L5_BOUNDED_T_RESULTS.md`). This DRAFT authors the CORRECTED solver, its
> build provenance, the generator/driver, and this pre-registration. **It does NOT
> freeze and it does NOT launch the graded family.** The cfd supervisor's §3
> **check-1** (the solver diff read AS A DIFF, this time verified **AGAINST THE
> ACTUAL FIELD**) and **check-4** (gate/lever/root/commit clean, protected binaries
> untouched, rebuild bit-identical, run root absent, Gate V' tolerances inherited
> byte-identical) are **OWED** before any freeze or launch. Nothing is sent, filed,
> uploaded, registered or posted (rule 7).
>
> **AUTHORISATION BASIS (unchanged from L5, recorded verbatim).** The solver-build
> boundary was chief-authorised 2026-09-08 as within standing lab capability with
> direct precedent (the F4 `rhoCentralFoamBounded` solver was built the same way for
> published results) — NOT root, NOT an instance change, does NOT leave the box, so
> the chief's call and NOT on Sanaa's reserved list. **This is the chief's ruling
> recorded by the cfd supervisor, NOT Sanaa's words (CLAUDE.md rule 9): no agent
> message is Sanaa's consent.** The solve is a sub-$25 CPU run (≈$0.03 derived; §6)
> pre-authorised under Sanaa's standing 2026-08-18 authorisation and routes through
> the detached queue daemon per Sanaa's 2026-08-26 ruling — not a direct launch.
> L-501 honoured: a crash of this family is a MEASURED negative result, never a
> capability inference from one/two SIGFPEs.
>
> **Gates are transcribed BYTE-IDENTICAL from the frozen DMR parent and NOT widened**
> (§3). The single registered lever vs the L4 first-order-T successor remains the
> **solver binary**; the ONLY change vs the L5 solver is that the positivity floor is
> now DERIVED FROM THE ACTUAL INITIAL FIELD (not an assumed reference) and a mandatory
> t=0 zero-clip assertion is added.

---

## 0. WHY L5b, AND WHY L5 WAS NOT A RESULT (background, not re-decided here)

L5 (`rhoCentralFoamBoundedDMR`, frozen `26823d9f`) graded **NOT A RESULT** on two
grounds (`DMR_R3_L5_BOUNDED_T_RESULTS.md`): its finest level R3 cap-stopped at
`Time = 0.19032384`, and — the ROOT CAUSE — its bounded-energy clip fired on **100 %
of cells from the first timestep at all three resolutions**, corrupting the field.

The mechanism, MEASURED: L5's floor `eMin_bound = -532.4097` was derived from a HAND
e-formula `e = Cv·(T − 298.15)` (an ASSUMED `Tref = 298.15`, `eref = 0`), which
predicts ambient `e(T=1.0) = -530.626`. But OpenFOAM's ACTUAL `hConst
sensibleInternalEnergy` assigns ambient `e ≈ -743.58928 J/kg` — a value the L5 run
reported byte-identically at its first step across all three grids (the smoking gun:
a per-grid-invariant worst-`e` is a thermo-reference constant, not a flow feature).
The `-532.4097` floor therefore sat **above the entire physical `e` field** and
floored every physical cell. The clip lever **never got a fair test**: the instrument
was miscalibrated. Under **L-501** no capability inference is drawn from a
miscalibrated instrument. L5b is the correctly-calibrated re-run.

**Parent for GATES and OUTPUT identity** is unchanged: the DMR **L4 first-order-T
successor** (`DMR_R3_L4_FIRSTORDER_T_PREREGISTRATION.md`, frozen `3c202ab1`), whose
Gate V' tol `0.0231` traces unbroken to the frozen DMR parent
(`DMR_PREREGISTRATION.md:88,:91`). L5b keeps L4's numerics byte-identical and changes
**only the solver binary**, applied UNIFORMLY to all three levels of a fresh,
self-contained three-level family R1'/R2'/R3' (240×60, 480×120, 960×240; nested 2:1),
graded as its OWN Gate V' and its OWN Roache triple.

## 1. THE ONE LEVER CHANGE vs L5 — the corrected floor + the t=0 assertion

The L5b solver is `rhoCentralFoamBoundedDMRb`
(`verification/runs/DMR_runs/rhoCentralFoamBoundedDMRb_src/`, tracked). Its change set
vs the L5 solver is EXACTLY three items (`diff -rq`, build provenance §6):

1. **Field-anchored `eMin_bound`/`eMax_bound` derivation** (`createFields.H`). The
   hConst T-inversion is exact and linear (`de/dT = Cv` everywhere), so a floor at
   temperature `TMin` is exactly
   `eMin_bound = e_min_initial − Cv·(T_min_initial − TMin)`, where `e_min_initial`
   and `T_min_initial` are the MEASURED global minima (`gMin`) of the initial `e` and
   `T` fields, and `Cv = 2.5 − 8314.47/11640.3 = 1.785717` is the DMR case's own value.
   `eMax_bound = e_max_initial + Cv·(TMax − T_max_initial)`, anchored symmetrically on
   the measured maxima. **NO assumed `Tref`/`eref` appears** — this is the exact
   correction of the L5 defect. By construction the floor sits
   `Cv·(T_min_initial − TMin)` BELOW the coldest physical cell, so it CANNOT sit above
   the field. `TMin = 1e-2` (1 % of ambient `T = 1.0`), `TMax = 1e4`, read from
   `controlDict`.
2. **Mandatory t=0 zero-clip startup assertion** (`createFields.H`). On the physical
   initial field, the solver counts cells with `e < eMin_bound` (reduced across ranks)
   and, if `> 0`, `FatalError`s with a clear message and exits non-zero
   ("REFUSE: clip fires on N cell(s) at t=0 — eMin_bound miscalibrated above the
   physical field"). A correctly-calibrated floor is inert at t=0 by construction;
   this assertion is the durable, self-verifying guard that would have caught L5
   before a core-minute was spent (plant-the-zero discipline, in the solver).
3. **`Make/files` / `.C` rename** `rhoCentralFoamBoundedDMR` → `rhoCentralFoamBoundedDMRb`.

`boundE.H` (the clip line `e = min(max(e, eMin_bound), eMax_bound)` and its per-fire
`BOUND:` diagnostic) is **byte-identical to L5** and stays as in L5. All L4/L5
numerics (Tadmor flux, `maxCo 0.1`, Euler ddt, `reconstruct(rho) Minmod`,
`reconstruct(U) MinmodV`, `reconstruct(T) upwind`, all BCs, states, thermo, mesh,
write times, 4-rank layout) are byte-identical; the ONLY generated-case change vs the
L5 generator is `controlDict` `application → rhoCentralFoamBoundedDMRb` and
`TMin 1e-3 → 1e-2` (verified: generator diff is exactly those two lines).

### 1.1 PROOF the calibration is now correct — t=0 assertion vs the ACTUAL R3 field

A serial startup-assertion probe against the ACTUAL R3 (N=240, 960×240) initial
physical field (a build-verification probe, NOT the graded family; scratch case, run
root never created) reports (build provenance §7,
`rhoCentralFoamBoundedDMRb_src/build_provenance/t0_assertion_probe_R3.txt`):

- `eMin_bound = -745.35714 J/kg` (L5b) — anchored on measured field min
  `e = -743.58928 J/kg`, which is BYTE-IDENTICAL to L5's reported first-step worst-`e`
  (so L5b reads OpenFOAM's ACTUAL hConst `e`, the very quantity L5's hand formula
  missed). `eMin_bound` sits `1.768 J/kg` BELOW the field min.
- `eMax_bound = 17111.794 J/kg`.
- **STARTUP ASSERT PASS: bounded-e clip fires on 0 cell(s) at t=0** (L5 clipped 100 %).
  No BOUND fire in the first steps; rc=0; no FatalError.

## 2. SOLVER-BUILD PROVENANCE (per `docs/OPENFOAM_SOLVER_BUILD.md`) — pin at freeze

Recorded in `verification/runs/DMR_runs/rhoCentralFoamBoundedDMRb_src/build_provenance/`:

- **Binary** `$(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDMRb`, 974800 bytes,
  md5 `9729eb8f61f0097ff0ec7a49a7bf5780`,
  sha256 `5b40e616b9861a053721c492251a1e3005e6601cef88970a5380ea81714122d5`.
- **Env**: OpenFOAM v2606, g++ 13.3.0, target `linux64GccDPInt32Opt`, built via
  `openfoam2606 -c '… wmake'` with **`USER=ubuntu`** (the daemon USER-trap;
  `OPENFOAM_SOLVER_BUILD.md` §2). Full `wmake` log captured (rc=0, no warnings).
- **Rebuild-verify**: rebuilt from tracked source under a redirected `$HOME`,
  **BIT-IDENTICAL** (`cmp`), md5 match.
- **Protected binaries UNTOUCHED** (hash+mtime): stock `rhoCentralFoam`
  (`5b1be223…`), F4 `rhoCentralFoamBounded` (`ee83ca59…`), L5
  `rhoCentralFoamBoundedDMR` (`4159e374…`) — `diff before/after` EMPTY.
- **Change set** vs stock and vs L5: build provenance §6.
- **Tracked source commit / generator sha256 / driver sha256**: PINNED AT FREEZE
  (this DRAFT records provisional generator sha256
  `45cf337b88601287895cfe81e5223a4d8272c3ee3d28c81da2603cbe6aae3005`
  `make_case_l5b_bounded_t_corrected.py`, driver sha256
  `3af3ebd99d8bdc1690de0931e5a9682e9f719fde646e02978af744fb22a58497`
  `run_dmr_l5b_bounded_t_corrected.sh`; re-hash and pin at freeze after commit).

## 3. GATES — NO THRESHOLD WIDENED (BYTE-IDENTICAL transcription proof)

- **Gate V' (kinematics vs exact theory):** PASS iff
  **`|x_measured − 2.99568| ≤ 0.0231`**, applied at each of R1'/R2'/R3'.
  **BYTE-IDENTICAL to the frozen parent**, proven by quotation:
  - frozen parent `DMR_PREREGISTRATION.md:91` reads verbatim
    `PASS iff |x_measured − 2.99568| ≤ 0.0231 at both rungs`, and `:88` `(±0.0231 in x)`;
  - the grader literal on disk, `verification/runs/DMR_runs/dmr_locator_v2.py:69`,
    reads verbatim **`GATEV_TOL = 0.0231`** (git blob
    `52aacf9669bcf23e88a0bf7984b299fa8aaf286e` == `HEAD:…dmr_locator_v2.py`, confirmed
    2026-09-08);
  - the L4 and L5 successors carried the same `0.0231` byte-identical.
  **No band moved. `x_exact = 2.99568` and tol `0.0231` are transcribed byte-identical
  and NOT widened** — a clip that displaces the shock past `0.0231` GATE FAILs honestly.
- **Gate T' (grid-convergence triple, rule 5 in full):** self-convergence triple of
  the Gate V' position error across R1'/R2'/R3' (Roache no-exact form, exact 2:1
  nesting). A non-`CONVERGING` triple is **NOT A RESULT**; a `CONVERGING` triple is
  graded against its band; GCI at `Fs = 1.25`, never quoted on a non-monotone triple.
  A run failing the strict completion rule (rule 4: `rc=0`, `End`, last time ==
  `endTime`, fields present, age guard) is not a completed level. No band loosened.
- **Controls (from the grader, unchanged):** planted whole-cell density displacement
  (rule 3), planted-absence refusal, the regression reproducing the 2026-08-07 R1/R2
  Gate V positions to 1e-12. **T25 (the triple-convergence band) is unmoved.**

## 4. GRADING PATH — REUSED UNCHANGED, HASHED AT GRADE TIME (pinned by symbol)

Grading is by the frozen method-agnostic
`verification/runs/DMR_runs/dmr_locator_v2.py` — it grades shock POSITION and reads
no scheme or solver file, so it grades the bounded-solver family unchanged. Pinned:
**git blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`** (`GATEV_TOL = 0.0231` at `:69`),
confirmed 2026-09-08 to equal `HEAD:verification/runs/DMR_runs/dmr_locator_v2.py`. The
driver re-hashes the grader against this blob before grading each level and refuses on
mismatch (rule 2). The grader is REUSED UNCHANGED and NOT edited (rule 6). The
planted-zero controls of §3 are mandated before any verdict (rule 3).

## 5. COST — rule 12 (core-minutes; dollars DERIVED, not measured)

4 ranks per solve. **Measured anchor: the L4 family's own figures**
(`DMR_R3_L4_FIRSTORDER_T_RESULTS.md`), because L5b keeps L4's numerics and step count
and adds only a per-step element-wise `min/max` over cells (marginal, sub-few-%).

| item | grid | basis | core-min |
|---|---|---|---|
| R1' | 240×60 | L4 R1 MEASURED (`R1.coresec.txt`=59) | **0.983 MEASURED-ANCHORED** |
| R2' | 480×120 | L4 R2 MEASURED (`R2.coresec.txt`=269) | **4.483 MEASURED-ANCHORED** |
| R3' | 960×240 | L4 R3 spent 24.6 core-min to t=0.15464 (77.3 %), crash-truncated; extrapolate to completion 24.6/0.773 ≈ 32, +clip overhead | **~33 ADVISORY (extrapolated)** |
| mesh/init/reconstruct/locator overhead | | | ~1.5 |
| **family point estimate (solves + overhead)** | | | **≈ 40 core-min** |
| **HARD CAP (the ONE registered family cap)** | | | **100 core-min** |

**HONEST UNCERTAINTY (rule 12).** The ~40 core-min point estimate is anchored on L4's
measured R3 rate, but **L5's own R3 measurement is NOT a usable anchor**: L5 spent its
full 100-core-min cap on a CORRUPTED field (the clip fired on 100 % of cells and
energy-pumped), so its cost measured the instrument defect, not the intended physics.
**No correctly-clipped N=240 DMR has ever run** — the final ~23 % of sim-time
(t=0.155→0.2) is unmeasured territory, and with the corrected floor the clip should be
INERT on physical cells (proven inert at t=0, §1.1), so the honest expectation is that
R3' behaves like L4's vanilla R3 up to where L4 crashed and then continues to
completion at a similar per-step rate. Retaining the cap at **100 core-min** (not
raising it above L4's 100, not tightening it) absorbs that extrapolation risk while
giving no room for an unbounded overrun.

**ONE registered hard cap: 100 core-min** — a single accumulator across all steps of
all three levels. An overrun STOPS the run and writes `CAP_BREACH.txt`; no new budget
(rule 12). Per-level figures are advisory rule-12 watermarks, NOT per-level caps.

### 5c. Dollars — DERIVED, NOT MEASURED
At c7a.4xlarge **$0.0513/core-h** (owner-stated; the box cannot read its own billing —
`COMPUTE_BUDGET_CHARTER.md` §5):
- family point estimate 40 core-min = 0.667 core-h × $0.0513 = **$0.0342 DERIVED**;
- the 100-core-min cap = 1.667 core-h × $0.0513 = **$0.0855 DERIVED**.

All well under the $25 CPU pre-authorised ceiling. A calibration row (estimate vs
actual, `docs/COST_CALIBRATION.md`) is owed at completion (rule 12). The one-time
`wmake` build (~2 core-min, already done) is a compile, separate from the solve cap.

## 6. FALSIFIABLE PROPOSITIONS — stated before any run (rule 2)

A "completing" level means the strict completion rule (rule 4) holds: `rc=0`, an `End`
line, last time == `endTime = 0.2`, required fields present, age guard satisfied.

1. **WORKS.** R1'/R2'/R3' all complete to t = 0.2 AND the triple is `CONVERGING` AND
   every level PASSES Gate V' inside `0.0231`. → A bounded-energy positivity clip,
   correctly calibrated, cures the DMR crash while preserving shock-position accuracy;
   the lab has a defensible 1/240 Mach-10 DMR result. **Measured-capability answer: YES.**
2. **GATE-FAIL-on-accuracy.** The triple completes but exceeds tol `0.0231`, or is
   non-monotone / `STAGNANT`. → A REAL robustness-vs-accuracy trade result (completion
   bought at the cost of the clip's local non-conservation), **NOT a widening** —
   the tolerance was held byte-identical. Motivates a conservative positivity scheme
   as a further rung.
3. **STILL-CRASHES.** R3' SIGFPEs again (rc=136) despite the corrected clip. → The
   fault is not (solely) a cell-centre post-update negative-`e` at line 136 — it may
   live on a reconstructed FACE, or the clip induces a limit-cycle. The MEASURED
   insufficiency of the cell-`e` clip (a negative result) → next rung a face-level
   positivity-preserving reconstruction/flux. **Under L-501 NEVER a
   capability-exhaustion finding from one or two SIGFPEs**; reported not softened.

**On capability exhaustion.** Only after L5b AND any face-level successor are MEASURED
can a tooling finding about the vanilla `rhoCentralFoam` v2606 numerics-robustness
levers become defensible. L5b is a NECESSARY rung, not itself the finding.

## 7. RUN ROOTS — DECLARED ABSENT (rule 2 / rule 4)

`verification/runs/DMR_R3_L5b_BOUNDED_T_runs` — **confirmed ABSENT at
2026-09-08** (this lane). The driver's rule-4 guard refuses each level whose case dir
already exists; the family writes into a fresh self-contained root only. The
startup-assertion probe of §1.1 ran in a SCRATCH case and did NOT create this root.
The daemon queue row for the driver MUST set **env `USER=ubuntu`** (the USER-trap;
the driver also exports it defensively).

## 8. WHAT IS AND IS NOT DONE IN THIS DRAFT

- **DONE:** the corrected `rhoCentralFoamBoundedDMRb` source authored, built
  (`wmake` rc=0), rebuild-verified bit-identical, protected binaries confirmed
  untouched; the t=0 zero-clip assertion VERIFIED against the ACTUAL R3 field (0 cells
  clip); the generator/driver authored; this pre-registration drafted; the run root
  confirmed absent.
- **NOT DONE (OWED before freeze/launch):** the cfd supervisor's §3 **check-1**
  (solver diff read as a diff, **against the actual field**) and **check-4**; the
  freeze (banner + grading-path freeze stamp; re-hash generator/driver/source commit);
  the queue row (env `USER=ubuntu`); and any launch of the graded family. **The graded
  L5b family was NOT launched; no core-minute of the registered 100-core-min cap was
  spent** (the only compute was the ~2-core-min build and a sub-minute startup probe).

---

**DRAFT — NOT FROZEN, NOT LAUNCHED. Nothing is sent, filed, uploaded, registered or
posted (rule 7). No gate, threshold, band, cap or label is set by this draft to
anything other than the frozen parent's values; Gate V' tol `0.0231` and
`x_exact 2.99568` are transcribed byte-identical and NOT widened.**
