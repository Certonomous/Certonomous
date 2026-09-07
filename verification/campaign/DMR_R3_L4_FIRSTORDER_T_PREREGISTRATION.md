# DMR R3 L4 — FIRST-ORDER-T RECONSTRUCTION SUCCESSOR — PRE-REGISTRATION

> **STATUS: AUTHORISED — FROZEN — 2026-09-07T21:45:36Z.**
> Prepared to freeze-ready by the cfd `lab-lane`, 2026-09-07. The L4 generator,
> the L4 family driver and the (already-fixed) STEP-0 reader are ON DISK and
> self-tested (§9); the reused grader identity is confirmed on disk. **FROZEN by
> the cfd supervisor after check-1 (the STEP-0 reader diff, read as a diff, PASS)
> and check-4 (generator/driver/prereg gates/lever/root/commit, PASS) taken
> PERSONALLY.** Freeze-time guard re-derivation (this commit): run root
> `verification/runs/DMR_R3_L4_FIRSTORDER_T_runs` ABSENT; `GATEV_TOL = 0.0231` at
> `dmr_locator_v2.py:69`; grader blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`
> == `HEAD:verification/runs/DMR_runs/dmr_locator_v2.py`; generator sha256
> `8d17c1ba22012b68e697b80d89e60089e1a1617e12a8a40cc63e72751e2024d9` and driver
> sha256 `9f0d66df8898bb05e1651da938d74b8c8dd65509070879d04d38542afe345382` match
> on disk; driver `bash -n` clean. No gate, threshold, band, cap or label altered
> at freeze (rule 6). Gate V' tol
> **0.0231** and all bands are held **BYTE-IDENTICAL** to the frozen DMR parent; the
> ONLY registered lever vs the Tadmor successor is `reconstruct(T)` dropped to
> first-order (`upwind`). Heeds L-501: a crash of this family is a MEASURED negative
> result, never a capability inference from one/two SIGFPEs.
>
> **Instruments to be pinned at freeze (sha256 + git blob), by the supervisor:**
> `make_case_l4_firstorder_t.py` sha256 `8d17c1ba22012b68e697b80d89e60089e1a1617e12a8a40cc63e72751e2024d9`,
> git blob `4b5a0da84795fcb9398c9d177a4462249348c8f9`;
> `run_dmr_l4_firstorder_t.sh` sha256 `9f0d66df8898bb05e1651da938d74b8c8dd65509070879d04d38542afe345382`,
> git blob `45a4971e819d28f264cc980e421e909439a499d6`;
> `step0_negativity_reader.py` (fixed) git blob `e1bd47a691762b0ae3aeaaff52e255c86c37c8f2`.
> Reused grader `dmr_locator_v2.py` git blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`
> (`GATEV_TOL = 0.0231` at :69, byte-identical to parent). No gate, threshold, band,
> cap or label is set by this draft to anything other than the parent's frozen values.

---

## 0. §2ay classification

Parent of THIS successor for GATES and OUTPUT identity: the **DMR Tadmor-flux
successor** (`DMR_R3_TADMOR_SUCCESSOR_PREREGISTRATION.md`), which is itself byte-
identical to the DMR positivity successor except `fluxScheme Kurganov→Tadmor`, which
is byte-identical to the frozen DMR parent (`DMR_PREREGISTRATION.md`) except its
registered levers. Gate V' tol `0.0231` traces unbroken to that frozen parent.

**Mechanism, MEASURED (background, not re-decided here):** the DMR-R3 Courant/dt
lever (L2, maxCo probe) is **measured-exhausted**; the failing mechanism is a
**T-positivity failure at the reflecting-wall foot**, T first going negative at
t = 0.150. That is a reconstructed/updated-temperature excursion below zero at the
flux level, so the appropriate our-side lever is **more diffusive T reconstruction**.
§2ay state **(b) NUMERICS-ROBUSTNESS**: "if it's the numerics, change the numerics."
This is that successor: L4 = first-order (piecewise-constant) T reconstruction.

## 1. WHY A NEW FAMILY, NOT A RE-RUN

The parent DMR triple prereg names as a **disqualifier** "any difference in scheme,
constants, boundary conditions, maxCo, write times or rank count between rungs — the
triple requires one numerics family and a difference invalidates it." Therefore the
T-reconstruction change is applied **uniformly to all three levels** of a **fresh,
self-contained three-level family** — R1 (1/60, 240×60), R2 (1/120, 480×120), R3
(1/240, 960×240), nested exactly 2:1 — graded as its OWN Gate V' and its OWN
grid-convergence triple. The Tadmor, Minmod-positivity and original `vanLeer`
families are all **untouched**.

## 2. THE SPECIFIC NUMERICS CHANGE, AND WHY IT SHOULD RECOVER

**Single lever, uniform across R1/R2/R3:** `system/fvSchemes`
`reconstruct(T)  Minmod;` → `reconstruct(T)  upwind;`. Everything else is byte-
identical to the Tadmor successor: `fluxScheme Tadmor` RETAINED, `maxCo 0.1`
RETAINED (dt is measured-irrelevant to the mechanism — the cheaper value is used),
`reconstruct(rho) Minmod` and `reconstruct(U) MinmodV` RETAINED, Euler ddt,
`div(tauMC) Gauss linear`, all BCs, write times and 4-rank layout unchanged.
**Proven exactly one line** (§5, §9): the L4 generator's N=60 output tree differs
from the Tadmor generator's N=60 output tree by EXACTLY `system/fvSchemes` line 16
(`reconstruct(T)  Minmod;` → `reconstruct(T)  upwind;`) and nothing else; the two
file sets are identical.

**Why `upwind` IS first-order / most-diffusive T reconstruction (verified in the
v2606 source, not asserted):** in `rhoCentralFoam` the `reconstruct(T)` scheme
governs the +/- face interpolation of `rPsi`, `e` AND the cell-centre sound speed
`c` (`rhoCentralFoam.C:109-113, 140, 146`, all keyed on `T.name()`) — the exact
positivity-critical path of the measured mechanism. `Foam::upwind<Type>`
(`src/finiteVolume/interpolation/surfaceInterpolation/limitedSchemes/upwind/upwind.H`)
is a `limitedSurfaceInterpolationScheme<Type>` — the SAME base class and
construction path as `Minmod`, so it is a drop-in reconstruct-scheme with no code
change — whose `limiter()` returns **Zero** and whose `weights()` return
`pos0(faceFlux)`: the reconstructed face value is exactly the upwind CELL-CENTRE
value (piecewise-constant, no reconstructed slope). That is the most-diffusive,
first-order T reconstruction, entirely in-solver: **NO solver build.** Damping the
reconstructed-T slope removes the below-zero face/updated-T undershoot driving the
crash, at no dt cost.

**Honest caveat, stated before the run (rule 2):** first-order T reconstruction is
**strictly more diffusive** than Minmod. This family may **run to completion and
then GATE FAIL on accuracy** — the shock could smear past tol 0.0231, or the triple
could STAGNATE as the added diffusion masks the formal order. **That is a legitimate
robustness-vs-accuracy trade finding — a REAL result, not a process failure** — and
NOT a widening of the gate: the tolerance is held byte-identical (§4). And R3 may
**still SIGFPE** — then the first-order-T lever is MEASURED insufficient (a negative
result), which under fix-until-runs CONTINUES the ladder as a further dated
successor (L5 bounded-energy solver build), reported not softened — **never a
capability finding from one or two SIGFPEs (L-501).**

## 3. STEP-0 READER (measurement script) — FIXED, FLAGGED FOR CHECK-1

The STEP-0 negativity reader `verification/runs/DMR_runs/step0_negativity_reader.py`
was fixed in this prep to key `first_negative` and the mechanism attribution on
**T and rho only** (`POSITIVITY_SCALARS = ("T","rho")`); `e` (reference-relative
sensible internal energy, legitimately negative from the first step) and `p` are
retained as diagnostic context but NO LONGER drive first_negative — removing the
FALSE-EARLY `e` signal that masked the physical T signal. Its two-sided planted-zero
control (rule 3) is unchanged and still fires both ways (§9). **This is a
measurement-script change; it is FLAGGED for the cfd supervisor's §3 check-1 — the
diff must be read as a diff before belief.** Post-fix git blob
`e1bd47a691762b0ae3aeaaff52e255c86c37c8f2`.

## 4. GATES — NO THRESHOLD WIDENED

- **Gate V' (kinematics vs exact theory):** PASS iff
  `|x_measured − x_exact_at_row| ≤ **0.0231**`, applied at each of R1/R2/R3.
  **BYTE-IDENTICAL to the parent** — asserted (§9): `GATEV_TOL = 0.0231`
  (`dmr_locator_v2.py:69`) equals the literal `0.0231` in the frozen parent
  `DMR_PREREGISTRATION.md` (:88, :91) and the positivity/Tadmor successor preregs.
  No band moved.
- **Gate T' (grid-convergence triple, rule 5 in full):** self-convergence triple of
  the Gate V position error across R1/R2/R3 (Roache no-exact form, exact 2:1
  nesting). A non-CONVERGING triple is **NOT A RESULT**; a CONVERGING triple is
  graded against its band; GCI at Fs = 1.25, never quoted on a non-monotone triple.
  No band loosened.
- Controls carried over from the grader: planted 7-whole-cell density displacement
  (rule 3), planted-absence refusal, and the regression reproducing the 2026-08-07
  R1/R2 Gate V positions to 1e-12.

## 5. GRADING PATH — FIXED AT FREEZE, INSTRUMENTS ON DISK

Grading is by the frozen method-agnostic
`verification/runs/DMR_runs/dmr_locator_v2.py` (git blob
`52aacf9669bcf23e88a0bf7984b299fa8aaf286e`, `GATEV_TOL = 0.0231` at :69) — it grades
shock POSITION and reads NO scheme file, so it grades the first-order-T family
unchanged; the driver **hashes it against the frozen blob before grading each level
and refuses on mismatch** (rule 2). The planted-zero controls of §4 are mandated
before any verdict (rule 3). The grader is REUSED UNCHANGED and is NOT edited
(rule 6).

**Instruments authored and self-tested (on disk), cited by sha256 + git blob:**

| instrument | path | sha256 | git blob |
|---|---|---|---|
| L4 generator | `verification/runs/DMR_runs/make_case_l4_firstorder_t.py` | `8d17c1ba22012b68e697b80d89e60089e1a1617e12a8a40cc63e72751e2024d9` | `4b5a0da84795fcb9398c9d177a4462249348c8f9` |
| L4 family driver | `verification/runs/DMR_runs/run_dmr_l4_firstorder_t.sh` | `9f0d66df8898bb05e1651da938d74b8c8dd65509070879d04d38542afe345382` | `45a4971e819d28f264cc980e421e909439a499d6` |
| STEP-0 reader (MEASUREMENT SCRIPT — check-1) | `verification/runs/DMR_runs/step0_negativity_reader.py` | — | `e1bd47a691762b0ae3aeaaff52e255c86c37c8f2` |
| reused grader (UNCHANGED) | `verification/runs/DMR_runs/dmr_locator_v2.py` | — | `52aacf9669bcf23e88a0bf7984b299fa8aaf286e` |
| parent Tadmor generator (identity anchor) | `verification/runs/DMR_runs/make_case_tadmor.py` | `f08ddd6884f16ef89146723ba2ae79ba8efff639935b0a0dc1ac5b29b23bb0bc` | — |

> **The sha256/blob values above are frozen at the pre-registration commit.** The
> supervisor verifies at check-4 that these are the files that will run; the driver
> re-hashes the grader against its blob at grade time (rule 2).

## 6. COST — rule 12 (measured anchor: the L2 Courant probe at N=240)

4 ranks per level. **Measured basis:** the L2 Courant probe reached ~75 % of endTime
at N=240 for ~57.5 core-min → full N=240 at maxCo 0.1 ≈ **77 core-min**. First-order
T reconstruction shares the same dt (maxCo 0.1 unchanged) and step count, and
`upwind` is if anything marginally CHEAPER per step than `Minmod` (no limiter
evaluation), so 77 core-min is a conservative N=240 estimate. Coarse levels scale
~1/8 and ~1/64 of the fine.

| item | h | grid | basis | core-min |
|---|---|---|---|---|
| R1 | 1/60 | 240×60 | ~1/64 of R3 fine solve | ~1.5 MEASURED-ANCHORED |
| R2 | 1/120 | 480×120 | ~1/8 of R3 fine solve | ~10 MEASURED-ANCHORED |
| R3 | 1/240 | 960×240 | L2 probe 57.5 cm @ 75 % → 100 % | ~77 MEASURED-ANCHORED |
| mesh/init/reconstruct/locator overhead | | | | ~1.5 |
| **family estimate total** | | | | **≈ 90 core-min** |
| **HARD CAP (the ONE registered family cap)** | | | | **100 core-min** |

**ONE registered hard cap: 100 core-min** (a single accumulator across all steps of
all three levels, `run_dmr_l4_firstorder_t.sh`; modest ~11 % margin over the ~90
estimate). R3 dominates. An overrun **STOPS the run** and writes `CAP_BREACH.txt`;
no new budget (rule 12). Per-level figures are advisory rule-12 watermarks, NOT
per-level caps.

**Dollars — DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5; the box cannot
read its own billing): at c7a.4xlarge $0.0513/core-h — grand estimate 90 core-min =
1.5 core-h × $0.0513 = **$0.0770 DERIVED**; the 100-core-min cap = 1.667 core-h =
**$0.0855 DERIVED**. Well under the $25 pre-authorised ceiling. A calibration row
(estimate vs actual) is owed in `docs/COST_CALIBRATION.md` at completion (rule 12).

## 7. WHAT THIS SUCCESSOR CAN AND CANNOT SETTLE

- **Can:** whether first-order (piecewise-constant) T reconstruction carries the DMR
  to t = 0.2 at 1/240 and yields a CONVERGING Gate V' triple; and quantify the
  robustness-vs-accuracy trade of dropping T to first order at Mach 10.
- **Cannot:** claim capability exhaustion — that requires the full measured lever
  chain (Courant/dt exhausted + Tadmor + first-order-T measured insufficient, then
  L5 solver build). Cannot alter the Tadmor, Minmod or original `vanLeer` families'
  standing.

## 8. RUN ROOTS — DECLARED ABSENT (rule 2 / rule 4)

`verification/runs/DMR_R3_L4_FIRSTORDER_T_runs` — **confirmed ABSENT at
2026-09-07T21:37Z**. The driver's own rule-4 guard refuses each level whose case dir
already exists (exit 90); the family writes into a fresh self-contained root only.

## 9. SELFTESTS RUN AT AUTHORING (recorded; the supervisor re-checks personally)

All run 2026-09-07 by the authoring lane; verdicts recorded, not the transcripts:
1. **STEP-0 reader two-sided planted control fires both ways (post-fix).**
   `step0_negativity_reader.py --selftest` → planted negative **SEEN**, clean data
   no false negative, **exit 0**. `--selftest-blind` → detector blinded, planted
   negative **NOT SEEN**, control **CORRECTLY REFUSES, exit 2**. Same under
   `python3 -O` (the control is explicit refusal logic, not assert-based, so `-O`
   does not defeat it). **(FLAGGED for the supervisor's §3 check-1 — read the diff.)**
2. **Generator change is exactly one line.** Whole-tree `diff -r` of the L4
   generator's N=60 output vs the Tadmor generator's N=60 output returns EXACTLY:
   `system/fvSchemes` line 16 `reconstruct(T)  Minmod;` → `reconstruct(T)  upwind;`,
   nothing else; the two file sets are identical.
3. **Driver `bash -n` clean** — `run_dmr_l4_firstorder_t.sh`.
4. **Grader identity unchanged.** `git hash-object dmr_locator_v2.py` =
   `52aacf9669bcf23e88a0bf7984b299fa8aaf286e` (== frozen blob; grader NOT edited).
5. **Gate V' 0.0231 byte-identical** to the parent literal (`dmr_locator_v2.py:69`
   vs `DMR_PREREGISTRATION.md:88,:91`).
6. **Run root ABSENT at authoring:** `DMR_R3_L4_FIRSTORDER_T_runs` confirmed to not
   exist (2026-09-07T21:37Z).

---

**Nothing is sent, filed, uploaded, registered or posted (rule 7). FROZEN and
AUTHORISED 2026-09-07T21:45:36Z by the cfd supervisor, after check-1 (the STEP-0
reader diff, read as a diff) and check-4 (generator/driver/prereg gates/lever/root/
commit) were taken PERSONALLY (both PASS). No gate, threshold, band, cap or label
was altered at freeze (rule 6).**
