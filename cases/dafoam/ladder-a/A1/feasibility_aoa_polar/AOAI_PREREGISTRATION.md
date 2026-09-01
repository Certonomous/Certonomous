# AOAI — NACA0012 INCOMPRESSIBLE ANGLE-OF-ATTACK POLAR, α = 0…18° (FEASIBILITY)

**Item:** `AOAI` · **Arm:** incompressible · **Ladder:** A1 · **Family:** dafoam
**Producer:** `aoa_runScript_incomp.py` · **Run root:**
`/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible`
**Written:** 2026-09-01 · **Frozen before compute; no run root existed at freeze.**

---

## 0. ORIGIN

SANAA-DIRECT, captured verbatim at commit `48b33813`:

> "Since the multipoint passed, let us do a sweep over all angles of attack from
> 0 to 18. Both compressible and incompressible cases. Both should be launched
> on the box."

This document is the incompressible half. `AOAC_PREREGISTRATION.md` is the
compressible half; they are frozen and committed separately so each carries its
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
| **Points** | **19** (with AOAC's 19: **38 across the two sweeps**) |
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
- **Nothing about compressibility.** See the AOAC disclosure in §6.3 — the two
  arms are **not** a matched compressible/incompressible comparison.

---

## 6. SOLVER SETTINGS — THE SO-3 GROUND, UNCHANGED

**The whole value of using the anchor is that the polar is comparable to the
graded items. Nothing here is re-tuned for this sweep.**

| | |
|---|---|
| Solver | `DASimpleFoam` |
| U | 10.0 m/s |
| ν | **1.5e-5 m²/s** *[VERIFIED against `constant/transportProperties`, not taken from the brief]* |
| Re (c = 1) | **≈ 6.67e5** |
| Turbulence | **Spalart–Allmaras** *[VERIFIED against `constant/turbulenceProperties`]* |
| Wall treatment | `useWallFunction: True` |
| `primalMinResTol` | 1.0e-8 |
| `endTime` cap | 1000 SIMPLE iterations |
| Mesh | A1's 4,032-cell NACA0012 *[VERIFIED: `checkMesh.log` reads `cells: 4032`]* |
| ranks | **np = 1** |
| Mesh source | `CURRICULUM-SO2a-…/MESH`, **staged by copy; the source is never written** |

### 6.1 The producer, and what is claimed about it

`aoa_runScript_incomp.py` is **generated by substitution** from
`feasibility_SO3a_alpha/so3af_runScript.py` — itself `curriculum_SO2a`'s producer
with one line changed — so that **every byte of physics is carried across rather
than retyped.** The generator asserts both edit anchors are unique. **The diff is
exactly two edits:**

1. `aoa0` sourced from `AOA_ALPHA0` instead of `SO3AF_AOA`;
2. an **additive** `-task sweep` branch. Every pre-existing task branch,
   including `run_model`, is byte-untouched.

So the primal path is the verified one — the path on which three alphas reached
DAFoam's own tolerance-satisfied line — and not a new harness.

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

### 6.3 ⚠ THE TWO ARMS ARE NOT A MATCHED COMPARISON

AOAI runs at **Re ≈ 6.67e5**; AOAC runs at **Re ≈ 6.54e6** — an **order of
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

I was handed two anchors: compressible **4.250 s/primal** and incompressible
**2.642 s/primal**, both correctly labelled warm-start floors. **I measured them
and they do not transfer in that form.** Three findings, on the face:

1. **Per-primal is the wrong unit.** D19M's FE-S sweep contains **6 primals
   converging in under 10 iterations** and 9 more under 100 — FD perturbations so
   small the solver barely moves. Averaging those into a per-primal figure makes
   it a floor **for the wrong reason**: not "warm vs cold", but "infinitesimal
   perturbation vs a 1° step in α".
2. **The transferable quantity is seconds per SIMPLE iteration**, and I measured it
   on both sides:
   - **incompressible 0.011024 s/iteration** *[MEASURED — SO3aF's three cold
     primals: 4.80/443, 4.79/435, 4.76/424]*
   - compressible 0.011500 s/iteration *[MEASURED — D19M FE-S: 352.16 s solver
     wall over 30,622 iterations]*
3. **The claimed 1.6086× compressible/incompressible primal ratio does not survive
   as a per-iteration statement** — the two rates agree to **4.3 %**. That ratio is
   an artefact of differing *iteration counts*, not differing per-iteration cost.
   It is a sound basis for what D19M used it for and an unsound one here.

**A fourth correction, in the honest direction:** SO3aF's own note records that no
cold primal on this case had ever been timed, so its cold adjustment was
`[EXTRAPOLATED]`. **It has now been timed** — its three cold primals are on disk at
424–443 iterations and 4.76–4.80 s. **The cold anchor is upgraded from
EXTRAPOLATED to MEASURED**, and this item prices α = 0 and the three cold controls
from it.

### 7.2 The iteration budget

| points | iterations each | basis |
|---|---|---|
| α = 0 (cold) | 450 | **MEASURED** — SO3aF cold: 424–443 at α = 3–7°; 450 for headroom |
| α = 1…12 (12, continued) | 350 | **EXTRAPOLATED** — D19M's warm primals averaged 337.9 iterations across the 90 non-trivial ones. A 1° α step is a **larger** perturbation than an FD step, so this is the nearest defensible figure and is **not** a measurement of a 1° step |
| α = 13…18 (6) | **1000** | **priced AT THE CAP** — where they land if they do not converge (§4.3) |
| cold control α = 4 | 440 | MEASURED, as above |
| cold controls α = 14, 17 | **1000 each** | priced at the cap |

**Total 13,090 iterations.**

### 7.3 The figures

| line | value | label |
|---|---|---|
| solver time | 13,090 × 0.011024 s = **144.3 s** | **EXTRAPOLATED** (measured rate × predicted iterations) |
| container start + `loadDAFoam.sh` | ~15 s | EXTRAPOLATED, bounded above by D14M's MEASURED 11 s |
| `DASolver` init × 4 processes | ~20 s | EXTRAPOLATED from SO3aF's 35 s total against 14.35 s solver |
| staging (two case trees) | ~5 s | EXTRAPOLATED |
| **POINT ESTIMATE** | **≈ 184 s × 1 rank = 3.07 core-min** | **EXTRAPOLATED** |
| **REGISTERED ESTIMATE** | **3.2 core-min** | headroom on an extrapolated figure |
| **BAND** | **[2.0, 12.0] core-min** | |
| **PER-POINT CAP** | **1000 SIMPLE iterations** | the `endTime` cap — the physical per-point stop |
| **PER-ARM CAP** | **20.0 core-min** = the **1200 s `timeout -k 60`** inside the container | what actually stops it |
| **ITEM CEILING (both arms)** | **40.0 core-min** | |

**Absolute worst case, checked:** all 22 solves at the 1000-iteration cap =
22,000 × 0.011024 = 242 s + 40 s overhead = **282 s = 4.7 core-min** — well inside
the 20.0 cap. The cap is ~4× the worst case: **honest headroom, not a blank
cheque.**

**AN OVERRUN STOPS THE RUN. IT DOES NOT GET A NEW BUDGET.**

**Dollars — DERIVED, NEVER MEASURED.** At the owner-reported c7a.4xlarge rate of
**$0.0513/core-h** (Sanaa 2026-08-21/22): **$0.0027** at the point estimate,
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
| **cpuset** | **14** (AOAC takes **15**, so both sweeps run concurrently, as ordered) |
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
| `aoa_runScript_incomp.py` | `727c41e46dc242628a77f70817cecb39` |
| `aoa_read.py` | *pinned at commit; see `AOAI_MD5.txt` written by the freeze* |
| `aoa_cmd.sh` | *as above* |
| `aoa_run_arm.sh` | *as above* |
| D19M physics block (AOAC only) | `c66504acc57bd9ef009599e883d2ef3b` |

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
| G-PHYS | 9 | **yes — one byte of `nuTilda0` moved, md5 diverges** (AOAC) |
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

---

## 11. AMENDMENT RECORD

Before first compute, amendments are legal and must state the condition and how it
was checked. After first compute this document is closed; changes land only as
dated addenda that cannot alter a gate, threshold, cap or label.

**At freeze:** the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible`
**did not exist** — asserted by execution immediately before launch, and G-ROOT
refuses at exit 6 if it does.
