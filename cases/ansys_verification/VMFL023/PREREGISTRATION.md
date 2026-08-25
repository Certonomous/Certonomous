# VMFL023 — Oscillating Laminar Flow Around a Circular Cylinder — PRE-REGISTRATION

**Frozen 2026-08-25T21:48:12Z, BEFORE any graded solver run.** Built from
`docs/ansys_verification/PREREG_TEMPLATE.md` (all three amendments applied).

## THE CONSISTENCY CHECK, DONE FIRST AND REPORTED WHICHEVER WAY IT FELL

VMFL036's page was found internally inconsistent, so the same check was run here
**before anything else**, from the manual's **own stated properties**:

| From the manual p.89 | Value |
|---|---|
| Density | 1 kg/m3 |
| Viscosity | 0.02 kg/m-s |
| Cylinder diameter D | 2 m |
| Freestream U | 1 m/s |
| **Re = rho·U·D/mu** | **1 × 1 × 2 / 0.02 = 100.0** |
| Re stated in the page's own text and in both result tables | **100** |

**THE PAGE IS INTERNALLY CONSISTENT. NO REPAIR ARM IS NEEDED.** This is the
opposite finding to VMFL036 and it is reported as such rather than assumed either
way.

The target **St = 0.165** was then checked against the published 2D-shedding
correlations at Re = 100:

| Correlation | St(Re = 100) |
|---|---|
| Williamson 1988 (parabolic fit) | 0.16434 |
| Roshko 1954 | 0.16706 |
| Fey et al. 1998 | 0.16484 |
| Williamson & Brown 1998 | 0.16663 |

The spread **[0.16434, 0.16706]** brackets the manual's 0.165 — the target is
**0.4% from the mid-spread**. The reference is sound.

**A CORRECTION TO THE FORM THIS LANE WAS HANDED.** The brief supplied the
Williamson relation as `St ≈ 0.1644 − 1.5619/Re`. Evaluated at Re = 100 that
gives **0.1488**, which does **not** match 0.165 and would have read as a failed
consistency check. The accepted Williamson (1988) parabolic fit is
`St = −3.3265/Re + 0.1816 + 1.6e−4·Re`, which gives **0.16434**. The supplied
form appears to be a mis-transcription; **the check was re-derived from the
literature form rather than run on the supplied one**, and all four correlations
above agree. This is stated so a reader can check the arithmetic rather than take
it on trust.

Both facts are wired into the comparator as an executable **reference-consistency
control** that REFUSES if the derived Re ever disagrees with the stated Re, or if
the printed target ever falls outside the correlation spread.

---

## THE TEN-LINE FORM

```
1. CASE            : VMFL023 — Oscillating Laminar Flow Around a Circular Cylinder
                     — manual p.89.  pimpleFoam (OpenFOAM v2606), TRANSIENT
                     laminar, 2D.  NOT YET RUN;
                     verification/runs/ansys_verification/VMFL023/ is ABSENT
                     at 2026-08-25T21:48:12Z.
2. REFERENCE       : Strouhal number St = 0.165 (dimensionless), source = F.M.
                     White, Fluid Mechanics 3e (McGraw-Hill 1994) and S.J. Kim &
                     C.M. Lee, KSME Int. J. 16, 363-375 (2002), as printed in
                     manual Tables .23.2 / .23.3.
                     Ansys Fluent reported 0.178 (ratio 1.1) and Ansys CFX 0.167
                     (ratio 1.01) — BOTH CONTEXT ONLY, never a gate.
3. REFERENCE KIND  : CORRELATION.  0.165 is a value read from the
                     experimentally-established St-Re curve as White's textbook
                     presents it — not a single measurement with a stated
                     uncertainty — and it is corroborated by a NUMERICAL study
                     (Kim & Lee 2002).  Per the template's mapping a correlation
                     BUYS V, NEVER P.  It is NOT treated as measured/experimental,
                     because no specific experiment with an uncertainty can be
                     pinned to the number from the manual + archive.
4. TIER CEILING    : GATE REACHED.  Fixed by line 3.  HOLDS is NOT AVAILABLE: a
                     correlation cannot buy P, so no value of St can make this a
                     validation credential.  Not upgraded, and the comparator
                     hard-codes GATE REACHED as the best obtainable label.
5. QUANTITIES      : St = D / (T * U), where T is the SHEDDING PERIOD of the lift
                     force on the `cylinder` wall patch, measured from
                     postProcessing/forces/0/force.dat column total_y READ BY NAME,
                     over the SETTLED WINDOW t in [180, 300] s declared on line 8.
                     METHOD, FROZEN HERE:
                       PRIMARY  — upward zero-crossings of the detrended lift,
                         located by linear interpolation between samples, then a
                         LEAST-SQUARES LINE through (crossing index, crossing
                         time).  Its slope IS the period.  At least 8 crossings
                         required or the comparator REFUSES.
                       SECONDARY — the manual's own FFT method, reported beside it
                         WITH ITS BIN WIDTH (see DISCLOSURE 1).
                     St is a FREQUENCY, so NO reference area enters the gate.
6. BANDS (THE GATE): |St_lab - 0.165| / 0.165 <= 0.03 at the FINEST level.
                     JUSTIFICATION, none of it from any run of this case:
                     (a) the four published correlations span [0.16434, 0.16706],
                         i.e. +/-0.83% about their mid-point, so 3% is ~3.6x the
                         spread of the literature the reference itself comes from;
                     (b) the manual's own acceptance practice is a 3% goal, and
                         this is the same band frozen for VMFL036;
                     (c) the target is printed to 3 decimals, so rounding alone is
                         ~0.3% — a band tighter than ~1% would be gating on the
                         printing.
                     NOTE, STATED IN ADVANCE: Ansys Fluent's OWN entry (0.178,
                     +7.9%) WOULD FAIL THIS BAND, and the manual prints its ratio
                     as 1.1.  This lab's band is therefore TIGHTER THAN THE
                     MANUAL'S OWN ACCEPTED RESULT for this case.  That is
                     deliberate and it is not softened after the fact.
7. LADDER          : pimpleFoam in PISO mode (nOuterCorrectors 1, nCorrectors 2,
                     nNonOrthogonalCorrectors 1); laminar; ddt `backward` (2nd
                     order implicit); div(phi,U) Gauss linear (2nd-order central,
                     appropriate for a laminar 2D solve); laplacian Gauss linear
                     corrected.  Mesh: a full 360-degree O-grid in four 90-degree
                     blocks, cylinder r = 1 m (D = 2 m, manual), OUTER RADIUS
                     60 m = 30 D — A DECLARED MODELLING CHOICE, because THE MANUAL
                     STATES NO DOMAIN.  Birth-certified at every level (cell count
                     == 4*NT*NR, checkMesh Mesh OK, bounding box and quality
                     metrics recorded).  0/U carries a FROZEN symmetry-breaking
                     kick, internalField (1 0.2 0) — see line 9's second paragraph.
8. DECOMPOSITION   : r = 2 IN SPACE, BY CONSTRUCTION.  The radial stretching is
   SEED              the FIXED map r(xi) = r_in + L*(K^xi - 1)/(K - 1), xi = i/N,
                     K = 200 frozen; the expansion ratio is computed PER LEVEL as
                     R(N) = K^((N-1)/N), so every L2 node at even index coincides
                     EXACTLY with an L1 node.  Azimuthal is uniform.
                       L1_96x32    96 azimuthal x  32 radial =  3 072 cells
                       L2_192x64  192 azimuthal x  64 radial = 12 288 cells
                       L3_384x128 384 azimuthal x 128 radial = 49 152 cells
                     TIME IS **NOT** REFINED WITH SPACE, DELIBERATELY.
                     deltaT = 0.005 s is FIXED AT EVERY LEVEL and adjustTimeStep
                     is OFF.  REASON: refining dt with h would make the triple
                     measure TWO refinements at once, and its observed order would
                     be uninterpretable.  Temporal truncation error is O(dt^2) and
                     INDEPENDENT of h, so a fixed dt puts the SAME temporal error
                     on all three levels, where it cannot enter d21 or d32.  At
                     dt = 0.005 s there are ~2 424 steps per shedding period, so
                     that common temporal error is negligible against the 3% band.
                     THE VERDICT IS THEREFORE A SPATIAL-REFINEMENT VERDICT AT A
                     FIXED, DECLARED TIME STEP — stated, not implied.
                     Max Courant number is required < 1 at every level (asserted
                     by the comparator from the log; >= 1 anywhere -> NOT A RESULT).
                     SERIAL (ranks = 1); no domain decomposition, no RNG.
9. PRINCIPAL RISK  : THE ONE named failure mode, predicted before compute —
                     THE OUTER DOMAIN AT 30 D IS NOT REFINED AWAY, AND St IS
                     KNOWN TO BE BLOCKAGE-SENSITIVE.  The Roache triple refines the
                     MESH only; the outer radius is held at 60 m at every level.
                     A residual confinement bias is therefore IDENTICAL at all
                     three levels, cannot appear in d21 or d32, and the GCI will
                     UNDERSTATE the true error.  The triple can read CONVERGING
                     with a tight GCI while St sits outside the band for a reason
                     the triple is blind to.  If that is what happens, THAT is the
                     reading and it will be stated — not a solver defect.
                     A SECOND, SUBORDINATE risk is handled as a CONTROL rather
                     than left to judgement: the settled window may not be settled.
                     The comparator splits [180, 300] s in half, compares the lift
                     peak-to-peak amplitude of the two halves, and returns NOT A
                     RESULT if they differ by more than 5%.
10. EXPECTED ORDER : formal p_f = 2 (backward in time, Gauss linear in space).
                     Expected observed p_obs ~ 1.5-2.0.  p_obs > 2.3 is declared
                     SUSPICIOUSLY HIGH IN ADVANCE — a WARNING of error
                     cancellation, a lucky mesh or the fixed-dt floor, never a win.
11. WEDGE/GEOM BIAS: N/A — not axisymmetric.  This is a PLANAR 2D case with an
                     `empty` front/back pair, so no sin(t)/t sector deficit exists.
                     Separately, and unlike a drag case, St IS A FREQUENCY: it
                     carries NO reference area at all, so even a geometric area
                     error could not reach the gate quantity.
12. COST + CAP     : ESTIMATE from a MEASURED throughput of 3.07e5 cell-steps/s
                     (machinery check, scratch, no gate quantity read):
                       L1  3 072 cells x 60 000 steps ->  600 s ->  10 core-min
                       L2 12 288 cells x 60 000 steps -> 2 400 s ->  40 core-min
                       L3 49 152 cells x 60 000 steps -> 9 600 s -> 160 core-min
                       TOTAL ~ 210 core-min.
                     CAPS: PER LEVEL 20 / 70 / 260 core-min, TOTAL 350 core-min —
                     runaway guards at ~1.7x the estimate.  ENFORCED IN THE
                     EXECUTABLE PATH: one budget (the sum of the caps of the
                     levels an invocation runs) is drawn down across them, and
                     each level's grant is
                       timeout_s = min(remaining_total, level_cap) * 60 / RANKS
                     with running accounting core_minutes = wall_s * RANKS / 60,
                     REFUSING at zero.  AN OVERRUN STOPS THE RUN.
                     cost_basis: core-minutes MEASURED from each level's own
                     RUN_RC.txt.  Any dollar figure is DERIVED at the recorded
                     c7a.4xlarge rate $0.0513/core-h (owner-stated) and is
                     REPORTED-BY-OWNER, NOT MEASURED — this box cannot read its
                     own billing (COMPUTE_BUDGET_CHARTER §5).
13. CONTROLS       : grade_vmfl023.py --selftest GREEN, run by the launcher at
                     every launch.  It fires, with ZERO compute:
                       - PLANTED FREQUENCY (rule 3): a sinusoid at f = 0.0825 Hz,
                         which is St = 0.165 EXACTLY by construction, is planted
                         into a COPY of the finest level's real force.dat; the
                         estimator must return it to 1e-6 or the comparator
                         REFUSES (exit 2).  An estimator not shown able to see a
                         KNOWN frequency has not been shown able to see any.
                       - FLAT-SIGNAL CONTROL (rule 3, the refusal direction): a
                         lift series set IDENTICALLY TO ZERO must be REFUSED, not
                         reported as some St.  An estimator that reports a
                         frequency for a dead signal reports one for anything.
                       - DC-OFFSET CONTROL: a deliberate 1.7 offset must be
                         detrended to within the analytic partial-cycle bound
                         amp/(pi * n_cycles), which is COMPUTED, not hand-set.
                       - ROACHE CLASSIFIER CONTROL: triples constructed to be
                         CONVERGING / DIVERGENT / OSCILLATORY / STAGNANT / EXACT
                         must each be classified correctly, and the exactly-
                         second-order triple must return p_obs = 2 to 1e-9.
                       - REFERENCE-CONSISTENCY CONTROL (the VMFL036 lesson made
                         executable): Re derived from the page's own properties
                         must equal the Re the page states, and the printed target
                         must lie inside the published correlation spread, or the
                         comparator REFUSES — the gate would be mis-specified.
                         The LAUNCHER carries the same assert, so a wrong
                         viscosity dies AT LAUNCH, before any compute.
                       - STRICT COMPLETION (rule 4): rc = 0; an `End` line; last
                         time == endTime; U and p present at endTime; and the
                         count clause in its LITERAL transient form,
                         ExecutionTime count == endTime/deltaT = 60 000; and every
                         field at endTime NEWER than the case's own 0/ (age guard).
                         NO DEPARTURE IS DECLARED.  The launcher refuses a level
                         directory that already exists.
                       - ROACHE GATING (rule 5): not settled, or max Courant >= 1,
                         -> NOT A RESULT; triple not CONVERGING -> NOT A RESULT
                         with the value and both differences printed; GCI at
                         Fs = 1.25, NEVER quoted when the three values are not
                         monotone.
                       - LAUNCHER FREEZE CHECK (rule 2; template Amendments 2+3):
                         PREREGISTRATION.md and grade_vmfl023.py on disk are each
                         hashed against this commit's blobs at launch, each gating
                         with || { echo ABORT; exit 1; }, and the resolved shas are
                         written into the run root's LAUNCH_RECORD.txt.
```

---

## DISCLOSURES

### DISCLOSURE 1 — the manual's own method cannot resolve this lab's band, and that explains the manual's own Fluent entry
The manual states its method explicitly: *"An FFT analysis of the lift coefficient
on the cylinder wall is presented to determine the frequency of oscillations. The
Strouhal number corresponding to the maximum magnitude of oscillations is
presented."*

An FFT's frequency resolution is one bin, `Δf = 1/T_record`. Over this case's
120 s settled window that is `Δf = 1/120 Hz`, i.e.

> **ΔSt = Δf · D/U = 0.01667 — which is 10.1% of the target 0.165.**

**A method whose resolution is 10% cannot resolve a 3% band.** This is measured,
not asserted: the comparator's selftest runs an FFT on a synthetic series
constructed at St = 0.165 exactly and recovers **0.16667** — off by exactly one
bin — while the zero-crossing regression recovers **0.165000**.

That is why the PRIMARY estimator on line 5 is the zero-crossing regression, whose
resolution is set by `deltaT` and the number of cycles rather than by a bin width.
The FFT is still reported beside it, with its bin width printed, so the manual's
method is reproduced and its limitation is visible.

**And it is a candidate explanation for the manual's own numbers, offered as a
prediction rather than a conclusion:** Ansys Fluent's entry is 0.178, which is
0.165 + 0.013 — **within one bin-width of the target**, and the manual prints its
ratio as 1.1. Ansys CFX's entry is 0.167, and the manual's CFX note says the
record length *"was chosen to accommodate FFT calculations"* with the bin size
chosen deliberately — i.e. **the one solver whose record was sized for the FFT is
the one that landed at 1.01.** If this lab's zero-crossing St lands near 0.165
while its own FFT lands near 0.1667, that reading is supported.

### DISCLOSURE 2 — the outer domain is this lab's choice, not the manual's
The manual's geometry cell for VMFL023 gives **only** the cylinder diameter. The
outer radius of 30 D is a **declared modelling choice** made by this lane, frozen
on line 7, and named as the **principal risk on line 9**. It is not refined away
by the grid triple and any confinement bias will be invisible to the GCI. Nothing
in this document claims otherwise.

### DISCLOSURE 3 — the symmetry-breaking kick
A perfectly symmetric O-grid with a perfectly symmetric initial field has no
mechanism to begin shedding except round-off, and 2D cylinder flow at Re = 100 can
sit symmetric for a long time before numerical noise breaks it. `0/U` therefore
carries `internalField uniform (1 0.2 0)` — a transverse component that breaks the
symmetry deterministically at t = 0 and decays well before the settled window
opens at t = 180 s. It is **frozen, identical at all three levels, and asserted by
the launcher**, so it gives every level the same start-up and cannot contaminate
the Roache triple. It is a modelling choice and it is disclosed as one.

### DISCLOSURE 4 — no pre-freeze value of the gate quantity was seen
Unlike VMFL036, **no partial St was visible to this lane before this freeze.** The
machinery check for this case ran 200 time steps in scratch purely to measure
throughput and confirm `checkMesh` reports `Mesh OK`; 200 steps is 1 s of physical
time against a 12.1 s shedding period, so no oscillation existed to read. The
launcher's smoke test opens the gate channel with `--dryrun-reader`, which prints
structure and no value.
