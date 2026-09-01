# AOAC — NACA0012 COMPRESSIBLE ANGLE-OF-ATTACK POLAR, α = 0…18° (FEASIBILITY)

**Item:** `AOAC` · **Arm:** compressible · **Ladder:** A1 · **Family:** dafoam
**Producer:** `aoa_runScript_comp.py` · **Run root:**
`/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-a1-naca0012-alpha-polar-compressible`
**Written:** 2026-09-01 · **Frozen before compute; no run root existed at freeze.**

---

## 0. ORIGIN

SANAA-DIRECT, captured verbatim at commit `48b33813`:

> "Since the multipoint passed, let us do a sweep over all angles of attack from
> 0 to 18. Both compressible and incompressible cases. Both should be launched
> on the box."

This document is the compressible half. `AOAI_PREREGISTRATION.md` is the
incompressible half; they are frozen and committed separately so each carries its
own sha.

---

## 1. TAG: `FEASIBILITY`, NOT GATED — AND THE REASON IS HER OWN DOCTRINE

**This rung is registered `FEASIBILITY` and produces READINGS, NOT VERDICTS.**

Fifteen minutes before the sweep order, Sanaa issued the convergence-prerequisite
doctrine (`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`,
her §0, captured at commit `f4c8e466`):

> "Every gated case runs its grid convergence study automatically; a case
> without one is not a result."

**A 19-point polar on a single 4,032-cell grid has no grid triple.** It therefore
**cannot be registered as gated without contradicting that doctrine.** Registering
it `FEASIBILITY` is not a lowered bar and not a hedge — it is the only reading
under which the two directives are consistent. `scripts/queue_entry_check.py:114`
encodes the tag lab-wide as
`UNREGISTERED_PREREG_TAGS = frozenset({"FEASIBILITY", "PHYSICS"})`, exact-match
and case-sensitive.

**REGISTERED IN ADVANCE: THE BAND FROM THE WING CONVERGENCE LADDER ATTACHES TO
THIS POLAR WHEN THAT LADDER LANDS.** That ladder (Sanaa's §5: L2 ≈ 100k, L3 ≈ 300k
from the same script as the 38k baseline, p and GCI) is being pre-registered in
parallel. Until it lands, **every number in this item travels without a
discretisation band and none may be quoted as a verdict.**

Nothing here is filed, sent, submitted or posted outside this box (rule 7).

---

## 2. THE SWEEP

| | |
|---|---|
| **Angles** | α = 0, 1, 2, …, 18 degrees **inclusive** |
| **Increment** | 1.0° |
| **Points** | **19** (with AOAI's 19: **38 across the two sweeps**) |
| **Direction** | **ASCENDING, 0 → 18** |
| **Initialisation** | **CONTINUATION** — each point starts from the previous point's converged solution |
| **Cold controls** | **3** — α = 4, 14, 17, re-run from freestream |
| **Total primal solves, this arm** | **22** (19 + 3) |

The 1° increment and the inclusive endpoints are the natural read of "all angles
from 0 to 18" and are registered as a **lane-implemented instruction from Sanaa**,
not a lane choice.

---

## 3. CONTINUATION — THE INSTRUMENT, AND ITS LIMITS

**The technique is Sanaa's own**, prescribed in §3 of the same directive:

> "Continuation: initialise each Cmu case from the converged solution of the
> next-lower Cmu (0 -> 0.05 -> 0.1 -> 0.2 -> 0.4) instead of from freestream."

**Mechanism, registered precisely.** All 19 points run in **ONE process**. `0/` is
reset from `0.orig` **once**, before the process starts, so **α = 0 is cold**. Then
for each point the driver calls `prob.set_val("patchV", [U0, α])` and
`prob.run_model()`. The `DASolver` is **not torn down between points**, so each
point begins from its predecessor's converged state **in memory**. This is the same
mechanism an optimiser's primal sequence uses — which matters for §7, because it
is the regime in which the warm per-primal anchors were measured.

*Verified on disk before freezing:* pyDAFoam renames the converged solution back
into `0/` when a primal finishes (the SO3aF case's `0/` holds solved
`U/p/nuTilda/nut` after its run, beside the numbered time directories). **So a
"cold" start that does not reset `0/` is not cold.** The reset is load-bearing and
is executed for α = 0 and before every cold control.

### ⚠ CAVEAT, REGISTERED IN ADVANCE

**A SINGLE UPWARD SWEEP DOES NOT TEST HYSTERESIS OR PATH DEPENDENCE, AND NONE IS
CLAIMED.** No descending sweep is run. Nothing in this item may be read as a
statement about hysteresis loops, multiple solution branches, or the history
dependence of the polar.

### THE INSTRUMENT IS CHECKED — AN UNCHECKED INSTRUMENT IS NOT EVIDENCE

**Three cold control points, registered in advance: α = 4, 14, 17**, each re-run
from freestream (`0/` reset from `0.orig`) in a **separate case tree** so they
cannot disturb the swept tree.

- **α = 4** — low, inside the expected-attached range. Both branches should
  converge and agree there, which is what makes the instrument check
  *interpretable*.
- **α = 14, 17** — high, inside the range where §5 registers that steady
  convergence may fail. This is where path dependence would bite.

**They test two things, and both are registered before the numbers exist:**

1. **IS THE CONTINUATION INSTRUMENT LIVE?** If continuation is working, the
   continued point reaches tolerance in **fewer iterations** than the cold point
   at the same α. **Equal iteration counts would mean the warm start is not
   actually being inherited** — i.e. the instrument is dead, and the whole
   "continued" label on this polar would be false.
2. **IS THE ANSWER PATH-DEPENDENT?** Agreement in CL/CD means the continued polar
   is reproducible from freestream at that α.

### ⚠ WHAT DISAGREEMENT WOULD MEAN — REGISTERED BEFORE IT CAN HAPPEN

**If the continued and cold results disagree at the same α, that is a FINDING
ABOUT PATH DEPENDENCE. It is not a bug to be tuned away.** Neither branch is
preferred over the other; neither is discarded; the solver is not adjusted until
they agree. Both values are published side by side with the relative difference.
A steady RANS problem admitting two different converged states at one operating
point is a **result about the problem**, and this item will report it as one.

---

## 4. THE HONEST HANDLING OF HIGH α

### 4.1 The per-point steady-convergence criterion, fixed here, before any run

**A point is CONVERGED if and only if DAFoam emits its own statement**

```
Minimal residual <r> satisfied the prescribed tolerance <tol>
```

**before the `endTime` cap of 1000 SIMPLE iterations** (`system/controlDict`,
`endTime 1000`), with `primalMinResTol = 1.0e-8`. Three outcomes, and only three:

| condition | reading |
|---|---|
| the line is present | **CONVERGED** |
| the line is absent **and** last time ≥ 1000 | **NOT CONVERGED** — the cap stopped it |
| the line is absent **and** the cap was not reached | **NOT MEASURED** — a named null |

**A null is `NOT MEASURED`, never `False`.** A `False` there would silently
downgrade "I could not tell" into "it failed".

**WHY THE CRITERION IS A QUOTED DAFOAM STRING AND NOT A REMEMBERED PHRASE.**
The predecessor rung `feasibility_SO3a_alpha` grepped for `"Primal solution
converged"` — **a string DAFoam never prints.** Its archived table reported
`converged=False` on three solves that had **all** reached 1e-8 at iterations
443/435/424. Re-running its repaired reader on the same bytes returns
**CONVERGED 3/3**. That dead detector is the reason this criterion is a quoted
string carrying a **mutation control** (C5: disable the pattern and the positive
control must flip), and the reason §4.4's trap is registered so emphatically: a
broken convergence reader plus an inference from convergence to stall would have
manufactured a stall angle out of a typo.

### 4.2 A point that does not converge steady is a FINDING

**It is reported with its residual history, per the `f4c8e466`-pattern §3.4 form.**

- **NEVER forced.**
- **NEVER tuned until it converges.** No relaxation change, no scheme change, no
  solver change is applied to make a point converge. The settings are frozen in §6.
- **NEVER dropped from the polar.** The reader keeps a point whose `BEGIN` marker
  is present even if its `END` never arrived, and marks it truncated.
- **NEVER silently replaced by a transient.** No pseudo-transient, no `pimpleFoam`
  fallback, no time-averaged substitute is admitted into this polar.

**A MISSING POINT ON A POLAR IS A LIE BY OMISSION.** The driver therefore does not
stop the sweep when a point fails: it records the failure, flags every subsequent
point `after_exception=TRUE`, and continues.

### 4.3 THE REGISTERED EXPECTATION, WRITTEN DOWN BEFORE THE ANSWER EXISTS

**I expect points above roughly 12–14° may not converge steady.** 2-D steady RANS
with Spalart–Allmaras on NACA0012 past stall is the standard place for the steady
solver to stop settling.

Writing this here means a non-converged high-α point is a **confirmed prediction**,
not an excuse invented afterwards. It also means the opposite outcome is
informative: if every point to 18° converges, **that too is a result against a
registered expectation**, and it will be reported as one rather than quietly
accepted.

**One arm-specific note, registered rather than discovered later:** at M ≈ 0.288
the peak suction on a NACA0012 at high incidence can carry the local Mach number
substantially above the freestream value. **No transonic claim is made or tested
here** — this rung neither measures nor reports local Mach, and the possibility is
registered only so that a non-converged high-α point in this arm is not
attributed to incidence alone without evidence.

### 4.4 ⚠⚠ THE TRAP, NAMED ON THE FACE, AND BUILT OUT OF THE GRADER

**THE STALL ANGLE MUST NOT BE INFERRED FROM WHERE THE SOLVER STOPPED CONVERGING.**

A non-converged point is evidence that **the steady solver stopped converging**.
It is **NOT** evidence of stall. These are two different claims, and conflating
them would throw away the entire finding.

**NO OUTPUT OF THIS ITEM MAY REPORT A STALL ANGLE DERIVED FROM CONVERGENCE
FAILURE.** This is enforced structurally, not by discipline:

- **No function in `aoa_read.py` computes a stall angle, a CLmax, or a separation
  onset.**
- **`G-STALL`** scans the reader's **own finished output** for a stall/separation
  word bound to a numeric angle and **REFUSES at exit 2** if it finds one. It is
  **fail-closed**: if a successor adds a stall limb, the reader stops publishing
  rather than publishes the inference.
- **Control C7** plants `"the stall angle is 13.0 deg"` and proves the guard fires;
  **C7b** proves it does *not* fire on this item's own honest caveat, because a
  guard that fires on everything gets turned off.
- The lift-slope table is published as an **indicator only**, with the statement
  that a real separation claim needs wall shear on a mesh that could resolve it.

### 4.5 ⚠ THE MIRROR OF THAT TRAP — MY ADDITION, AND THE ONE SUBSTANTIVE THING I ADD

The trap above is named in one direction. **It has two, and the second is the one
that would bite a reader who took this polar at face value:**

**A HIGH-α POINT THAT *DOES* CONVERGE IS NOT THEREBY TRUSTWORTHY EITHER.**

This is a **4,032-cell wall-function mesh** — `useWallFunction: True`, with y+
measured at **16.7–92.4** on this exact family. **It cannot resolve a separated
boundary layer at any angle.** Convergence and correctness are independent here.

So: a converged CL at 16° is a converged solution *of a model that cannot
represent the flow at 16°*. Reporting the non-converged points honestly while
letting the converged high-α points pass as physics would be the same error
wearing the opposite sign. **This item reports CONVERGENCE ONLY**, and the reader
prints that scope statement on every run.

---

## 5. WHAT THIS ITEM DOES **NOT** ESTABLISH

- **No grid triple, no observed order, no GCI, no band.** Not gradable (§1).
- **Nothing about stall, separation, or CLmax** (§4.4).
- **Nothing about hysteresis or path dependence** beyond the three cold controls
  (§3).
- **Nothing about gradients, adjoints, optima or weights.** Primal only.
- **Nothing at np ≠ 1.**
- **Nothing about transonic behaviour, shocks, or local Mach** (§4.3).
- **Nothing about compressibility as an effect.** See §6.3 — the two arms are
  **not** a matched comparison.

---

## 6. SOLVER SETTINGS — THE D19M GROUND, UNCHANGED

**The whole value of using the anchor is that the polar is comparable to the
graded items. Nothing here is re-tuned for this sweep.**

| | |
|---|---|
| Solver | `DARhoSimpleFoam` |
| U₀ | 100.0 m/s |
| p₀ / T₀ | 101325 Pa / 300 K |
| ρ | `p0/T0/287` = **1.17683 kg/m³** |
| μ | **1.8e-5 Pa·s** *[VERIFIED against `constant/thermophysicalProperties`, not taken from the brief]* |
| `nuTilda0` | 4.5e-5 |
| Re (c = 1) | **≈ 6.54e6** |
| M | **≈ 0.288** |
| Turbulence | **Spalart–Allmaras** *[VERIFIED against `constant/turbulenceProperties`]* |
| Wall treatment | `useWallFunction: True` |
| `primalMinResTol` | 1.0e-8 |
| `endTime` cap | 1000 SIMPLE iterations |
| Mesh | A1's 4,032-cell NACA0012 *[VERIFIED: `checkMesh.log` reads `cells: 4032`]* |
| ranks | **np = 1** |
| Mesh source | `CURRICULUM-D19M-…/MESH`, **staged by copy; the source is never written** |

### 6.1 The producer — what IS and is NOT claimed, stated the way D19M stated it

**NOT CLAIMED: header identity.** D19M's producer is a **MULTIPOINT** model with
three `DAFoamBuilder`s, three run directories and an `ExecComp`. This is a
**SINGLE-point** model. **It cannot be that file and does not pretend to be.**
D19M itself refused the inherited reproduction claim for exactly this reason, and
that refusal is inherited here rather than quietly dropped.

**CLAIMED, ON BYTES: the physics.** The block between
`# ---- D19M_PHYSICS_BEGIN ----` and `# ---- D19M_PHYSICS_END ----` — `U0`, `p0`,
`T0`, `nuTilda0`, `A0`, `rho0` and the whole of `daOptions` — is **D19M's,
character for character**. It was **extracted programmatically**, never retyped.

**md5 = `c66504acc57bd9ef009599e883d2ef3b`** — verified at three separate points:

1. at extraction, against D19M's own file;
2. by the generated producer's **own import-time self-assert**, which reads
   `__file__`, re-hashes its copy, and **raises `SystemExit` before the model is
   built** if a byte has drifted — this is the "assert it before the header
   executes" requirement, discharged inside the producer itself;
3. by **G-PHYS** in the host arm, which refuses at **exit 9** before launch.

**G-PHYS is DRIVEN, not asserted:** moving one byte (`nuTilda0` 4.5e-5 → 4.6e-5)
takes the md5 to `ea2c79b0df7a41e0b8f04c3f90710c8f` and both the self-assert and
G-PHYS fire; the clean file passes both.

The **model** half — mesh options, `Top`, the FFD/constraint construction, the
driver — is the incompressible producer's, i.e. SO-2a's verified single-point
structure, byte-asserted unchanged by the generator.

### 6.2 ⚠ A REGISTRATION FACT A READER MUST NOT HAVE TO DISCOVER

**SWEEPING TO 18° GOES OUTSIDE THE GROUND'S OWN REGISTERED ALPHA BRACKET.**

`curriculum_D19M/d19m_runScript.py:59-60` records of its three alphas that they
are all *"inside the tutorial's own `[0.0, 10.0]` aoa bound and well below stall
for NACA0012 at this Reynolds number."* That bound is literally present in this
producer too, as
`add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)`.

**It is deliberately left in place** — the settings are not re-tuned, and leaving
it makes the disclosure self-evidencing rather than a claim about an absent line.
It binds the optimiser only, and **no optimiser runs on this path**; but the fact
stands: **points 11 through 18 are outside the bracket the ground registered for
itself.** This is a further reason the item is `FEASIBILITY` and not gated.

Note also that D19M's centre α was **4.787333582°**, its own measured trimmed
angle; this sweep's integer grid does not reproduce that point exactly, and **no
number here is comparable to a D19M row without that being stated.**

### 6.3 ⚠ THE TWO ARMS ARE NOT A MATCHED COMPARISON

AOAC runs at **Re ≈ 6.54e6**; AOAI runs at **Re ≈ 6.67e5** — an **order of
magnitude apart**. They are two separate polars on the same mesh at different
Reynolds numbers, **not** a compressible-versus-incompressible comparison at
matched conditions.

This follows directly from keeping both D19-family grounds unchanged, which is
the right call and is registered as a **disclosed consequence, not a defect to
fix**. **Any side-by-side reading of the two polars as "the effect of
compressibility" would be wrong**, and this line exists so nobody has to discover
that by inference.

---

## 7. COST — RULE 12 IN FULL

**"Cost is not a constraint" removes the APPROVAL barrier, not the COSTING
obligation.**

### 7.1 The basis, and a correction to the anchors I was handed

I was handed two anchors: compressible **4.250 s/primal** (D19 S1, 51 s / 12
primals) and incompressible **2.642 s/primal**, both correctly labelled warm-start
floors. **I measured them and they do not transfer in that form.** Three findings,
on the face:

1. **Per-primal is the wrong unit.** D19M's FE-S sweep contains **6 primals
   converging in under 10 iterations** and 9 more under 100 — FD perturbations so
   small the solver barely moves. Averaging those into a per-primal figure makes
   it a floor **for the wrong reason**: not "warm vs cold", but "infinitesimal
   perturbation vs a 1° step in α".
2. **The transferable quantity is seconds per SIMPLE iteration**, and I measured
   it on both sides:
   - **compressible 0.011500 s/iteration** *[MEASURED — D19M FE-S: 352.16 s solver
     wall over 30,622 SIMPLE iterations across 105 primals]*
   - incompressible 0.011024 s/iteration *[MEASURED — SO3aF's three cold primals]*
3. **The 1.6086× compressible/incompressible primal ratio recorded in
   `D19M/COST_ESTIMATE.txt` does not survive as a per-iteration statement** — the
   two rates agree to **4.3 %**. That ratio is an artefact of differing *iteration
   counts*, not differing per-iteration cost. It is a sound basis for what D19M
   used it for (a per-major cost) and an unsound one here.

**A note on `ExecutionTime`, because it is the trap in this measurement:** OpenFOAM's
`ExecutionTime` is a **cumulative process clock**, not a per-primal figure. Dividing
the last value by the primal count gives a meaningless "mean" of a running total —
which is why the rate above is taken as *total solver wall ÷ total iterations*.

### 7.2 The iteration budget

| points | iterations each | basis |
|---|---|---|
| α = 0 (cold) | 550 | **EXTRAPOLATED** — above D19M's observed **max of 542**; no cold compressible primal at these α has been timed |
| α = 1…12 (12, continued) | 350 | **EXTRAPOLATED** — D19M's warm primals averaged **337.9** iterations across the 90 non-trivial ones. A 1° α step is a **larger** perturbation than an FD step, so this is the nearest defensible figure and is **not** a measurement of a 1° step |
| α = 13…18 (6) | **1000** | **priced AT THE CAP** — where they land if they do not converge (§4.3) |
| cold control α = 4 | 550 | as above |
| cold controls α = 14, 17 | **1000 each** | priced at the cap |

**Total 13,300 iterations.**

### 7.3 The figures

| line | value | label |
|---|---|---|
| solver time | 13,300 × 0.011500 s = **153.0 s** | **EXTRAPOLATED** (measured rate × predicted iterations) |
| container start + `loadDAFoam.sh` | ~15 s | EXTRAPOLATED, bounded above by D14M's MEASURED 11 s |
| `DASolver` init × 4 processes | ~20 s | EXTRAPOLATED from SO3aF's 35 s total against 14.35 s solver |
| staging (two case trees) | ~5 s | EXTRAPOLATED |
| **POINT ESTIMATE** | **≈ 193 s × 1 rank = 3.22 core-min** | **EXTRAPOLATED** |
| **REGISTERED ESTIMATE** | **3.4 core-min** | headroom on an extrapolated figure |
| **BAND** | **[2.0, 12.0] core-min** | |
| **PER-POINT CAP** | **1000 SIMPLE iterations** | the `endTime` cap — the physical per-point stop |
| **PER-ARM CAP** | **20.0 core-min** = the **1200 s `timeout -k 60`** inside the container | what actually stops it |
| **ITEM CEILING (both arms)** | **40.0 core-min** | |

**Absolute worst case, checked:** all 22 solves at the 1000-iteration cap =
22,000 × 0.0115 = 253 s + 40 s overhead = **293 s = 4.9 core-min** — well inside
the 20.0 cap. The cap is ~4× the worst case: **honest headroom, not a blank
cheque.**

**AN OVERRUN STOPS THE RUN. IT DOES NOT GET A NEW BUDGET.**

**Dollars — DERIVED, NEVER MEASURED.** At the owner-reported c7a.4xlarge rate of
**$0.0513/core-h** (Sanaa 2026-08-21/22): **$0.0029** at the point estimate,
**$0.0171** at the per-arm cap, **$0.0342** at the item ceiling. **The box cannot
read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure here
is a measurement and none is presented as one. **GPU: 0 GPU-h.**

**Calibration row owed at completion** (rule 12): actual/predicted in core-minutes
into `docs/COST_CALIBRATION.md`, with the gap attributed and waste named
separately. The per-point `wall_s` written into `out/LEDGER.tsv` makes the actual
**measured per point**, not just per arm.

---

## 8. PLACEMENT, MEMORY, AND THE DETACHED PATH

| | |
|---|---|
| **cpuset** | **15** (AOAI takes **14**, so both sweeps run concurrently, as ordered) |
| **G-CPUSET** | refuses at **exit 3** on collision with any **live** container |
| **Container memory** | **4g** |
| **MEM floor** | 6.0 GiB, bounded poll on live `MemAvailable`, **bounded at 3600 s and terminating non-zero** |

**MEM_LIMIT is sized from a measured peak, not the inherited `20g`.** Two anchors
exist: **D12R2's MEASURED 1.3461 GiB** and **D13's MEASURED 1.70 GiB peak RSS on
this exact 4,032-cell case at np = 1**. **The larger, case-specific anchor
governs**; 4g is 2.35× it. The inherited `20g` is not used.

**Detached path (Sanaa's 2026-08-26 detached-queue ruling).** The container is
launched `docker run -d` with the deadline **inside** the container, so the
compute survives a fleet kill. The arm itself is launched under `setsid`, and

> **`rc` is captured INSIDE the detached wrapper, never around the `setsid`
> line — `setsid timeout cmd` exits 0 for every outcome**, which has burned this
> lab before.

**A ledger row per point** is appended, flushed and `fsync`'d to
`out/LEDGER.tsv` on the host bind mount **as each point completes**, so a kill
loses **at most the single point in flight** and never a finished one. `rc` at the
end is read from the kernel's own record (`docker inspect .State.ExitCode`), never
from a shell's exit status.

---

## 9. GRADING PATH, PINNED

| instrument | md5 |
|---|---|
| `aoa_runScript_comp.py` | `f86eaa10fc945c79ec94f48737ed4caf` |
| D19M physics block inside it | **`c66504acc57bd9ef009599e883d2ef3b`** |
| `aoa_read.py` | *pinned at commit; see `AOAC_MD5.txt` written by the freeze* |
| `aoa_cmd.sh` | *as above* |
| `aoa_run_arm.sh` | *as above* |

### Rule 3 — planted-zero controls, live at grade time

`aoa_read.py` runs **11 controls, both directions, before it reads anything**, and
**refuses at exit 2** if any fails. Born against a **real run artefact** when one
exists (a converged segment cut from this run's own bytes) and against a declared
`WRITER_BUILT` fixture before that — **which it is, is stated in the output**.

| control | direction | what it proves |
|---|---|---|
| C1 | + | unmodified artefact → CONVERGED |
| C2 | + | sentinel `1.234567e-09` planted → reader reports **it**: the read is off the bytes |
| **C3** | **−** | **tolerance line removed, ran to cap → NOT CONVERGED** — the zero-passing control: **the non-convergence channel is shown able to fire**, without which a polar of all-CONVERGED proves nothing |
| C4 | − | truncated → **NOT MEASURED**, not False |
| C5 | ! | **mutation**: disable the pattern and C1 must flip |
| C6 / C6b | + / − | the two CL/CD channels can disagree audibly, and do not disagree falsely |
| **C7 / C7b** | **!** | **G-STALL fires on a planted stall claim; does not fire on the honest caveat** |
| G1 | ! | `SigFpe` startup banner does not become a crash (L-312) |
| G2 | ! | ten lines containing "error" do not become a crash |
| G3 | ! | `Total Residual Norm2` is a post-`End` diagnostic, not the criterion |

**Two independent channels on CL and CD** — the solver's own printed `CL:`/`CD:`
lines and the driver's `prob.get_val()` — are compared per point. **A disagreement
is reported, never resolved silently in favour of one.**

### The guards, all DRIVEN rather than asserted (`aoa_run_arm_selftest.sh`)

| guard | refuses with | driven |
|---|---|---|
| usage | 2 | yes — no argument, and an unknown arm |
| G-ROOT | 6 | **yes — sacrificial root, both arms** |
| G-SRC | 5 | at the point of use, not only at startup |
| **G-PHYS** | **9** | **yes — one byte of `nuTilda0` moved, md5 diverges** |
| G-IMG | 4 | digest `9d45679d` |
| G-CPUSET | 3 | live-container scan |
| MEM wait | 7 | bounded 3600 s, terminating non-zero |
| **G-STALL** | **2** | **yes — planted claim fires it; honest caveat does not** |

---

## 10. WHAT WOULD MAKE THIS ITEM WRONG

Registered so the failure modes are named before they can be explained away:

1. **The cold controls show equal iteration counts to the continued points** →
   the continuation instrument is dead and the "continued" label is false.
2. **The cold and continued results disagree** → a path-dependence finding (§3);
   neither branch is discarded.
3. **Every point to 18° converges** → §4.3's registered expectation is refuted,
   and that is reported as a refutation.
4. **The reader refuses at exit 2** → **NOT A RESULT**, whatever the table says.
5. **Fewer than 19 segments are present** → the polar is truncated and is reported
   as truncated, never quietly shortened.
6. **The physics md5 drifts** → **NOT A RESULT**: the entire comparability claim
   to the D19 family rests on those bytes.

---

## 11. AMENDMENT RECORD

Before first compute, amendments are legal and must state the condition and how it
was checked. After first compute this document is closed; changes land only as
dated addenda that cannot alter a gate, threshold, cap or label.

**At freeze:** the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-a1-naca0012-alpha-polar-compressible`
**did not exist** — asserted by execution immediately before launch, and G-ROOT
refuses at exit 6 if it does.

---

## 12. AMENDMENT — 2026-09-01, BEFORE ANY AOAC COMPUTE

**Rule 2 permits amendment before first compute, and requires the condition and
how it was checked to be stated.**

### The condition, and how it was checked

**THE CONDITION: `/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-a1-naca0012-alpha-polar-compressible`
DOES NOT EXIST.**

**How it was checked:** by execution, not by assertion. The first AOAC launch
attempt **refused at G-PHYS (exit 9) before the container was started**, so no
run root was ever created and no AOAC compute has occurred. The refusal is on
record in
`/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-…-compressible.launch.out`:

> `AOA_ABORT G-PHYS physics block md5 'MARKERS' != D19M's c66504acc57bd9ef009599e883d2ef3b`

and the run root's absence was re-checked with `ls -d` immediately before this
amendment. **No gate, threshold, cap or label changes below.**

### What changed, and why

**`aoa_runScript_comp.py` is regenerated. Its md5 moves from
`f86eaa10fc945c79ec94f48737ed4caf` to `8dbba88c465e80b526a0f10c744e9458`.**
`AOAC_MD5.txt` is rewritten to match. **The physics block is untouched and still
hashes to `c66504acc57bd9ef009599e883d2ef3b`.**

**THE DEFECT WAS MINE AND G-PHYS CAUGHT IT.** The generated producer embedded the
marker strings as **whole literals** inside its own import-time self-assert, so
`# ---- D19M_PHYSICS_END ----` occurred **twice** in the file (line 98, the real
marker; line 105, inside the self-assert). G-PHYS's first limb requires each
marker to appear **exactly once**, because a second occurrence makes the split
ambiguous — and it refused. **The refusal was correct.** The fix splits the
marker literals across an implicit concatenation so the contiguous string appears
only at the real marker.

### The second, larger finding: a guard is not tested until every limb is driven

**`aoa_run_arm_selftest.sh` drove G-PHYS's md5 limb and not its marker-count
limb.** The clean producer passed the md5 limb, so the selftest reported the
guard healthy — **while the producer would have been, and was, refused by the
limb that was never driven.** A partial selftest that reports PASS is worse than
no selftest, because it buys confidence it has not earned.

**`aoa_phys_marker_selftest.py` is added** and drives **both limbs in both
directions**, five cases: the clean producer must PASS; a moved `nuTilda0` byte,
a **duplicated END marker** (the real defect's shape), a removed BEGIN marker,
and a vanished block must each REFUSE. **All five pass.**

`aoa_run_arm_selftest.sh` is **left byte-untouched** — it is on AOAI's pinned
grading path and **AOAI is running** — so this limb gets its own instrument
rather than an edit to a file another arm is being graded against.

### What is NOT changed

`aoa_read.py`, `aoa_cmd.sh` and `aoa_run_arm.sh` are byte-identical to their
frozen state. **AOAI's pinned grading path is entirely unaffected**: it does not
list `aoa_runScript_comp.py`, and AOAI's own producer is untouched.
