# M6I RUNG 8 — THE MODEL RUNG: k-ω SST. PRE-REGISTRATION.
# **AND THE TERMINAL RUNG OF THE M6I MECHANISM LADDER.**

**Item:** `M6I_R8_SST`
**Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.
**Predecessors:** R5 `27a491e77` → `NOT A RESULT`; R6 `49c4d39a4` → `NOT A RESULT`, §7 did
not fire; R7 `1d9433a84` + addendum `0bfe11259` → `NOT A RESULT`, §5 returned
**NEITHER PATTERN**.

## 🔴 STATUS: **DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS DOCUMENT.**

Pre-compute condition, checked by this lane: **`verification/runs/M6I_runs/L2_SST/` does not
exist.**

---

## 🔴 §0 — THE EXHAUSTION CLAUSE, WRITTEN FIRST SO IT CANNOT BE MISSED

**IF R8 DIVERGES WITH THE §6 TRAILING-EDGE SIGNATURE, THE MODEL RUNG IS SPENT, THE M6I
MECHANISM LADDER IS EXHAUSTED, AND M6I PARKS.** No fourth rung. No fifth variant. By anyone.
Sanaa's rule 13: two stops on one cause means climb, and there is nothing left above this.

**PARKING IS AN HONEST OUTCOME AND THIS DOCUMENT DRAFTS IT AS ONE, NOT AS A FAILURE.**
M6I already holds a graded result — **L1 `GATE FAIL`, 12 of 12 B1 rows monotone under
refinement, the first row in band at RMS 0.0494** — and the entire mechanism hunt has cost
**42.54 core-minutes against L1's 1,098, under 4 % of one graded level.** A family that
produced a defensible verdict and then spent 4 % of one level establishing **by measurement**
that the missing shock is **not resolution, not the shock-window mesh, not the tip-cap mesh,
and not the pressure discretisation** has wasted nothing. What it must not do is continue by
inventing rungs.

On parking, §9 is written into the record **including its own limits**, which are against us.

---

## 1. WHY THE MODEL RUNG IS WHAT REMAINS

| rung | status | the measurement that closed it |
|---|---|---|
| **Resolution** | closed | 12/12 B1 rows monotone L3→L2→L1, but shock rise ×1.528 per halving ⇒ **8.0 × 10¹¹ cells** to reach the experiment. Not reachable. |
| **Mesh — shock window** | **dead** | **Zero** >70° faces in the x/c 0.30–0.70 upper-surface window at **all six** graded stations. |
| **Mesh — tip cap** | **dead, and anti-correlated** | 81.0 % of the L2 grid's >70° faces sit at η ≥ 0.99, where failure density is **4.96 %**; at η 0.20–0.65 the mesh is clean and failure density is **27.63 %**. **5.6× less dense where the mesh is worst. Spearman ρ = −0.800 over nine spanwise bands.** |
| **Numerics / pressure term** | **spent in substance** | Three configurations, three divergences: `limitedLinear` (R5), `vanLeer` + engaged floor (R6), `vanLeer` unclipped (R7). Scheme and floor only modulated how one runaway expressed itself. |
| **MODEL** | **this document** | |

**The floor is not merely unproven — R7 inverted it.** R7's 0.05 floor was **never engaged**
(`vol_floor = 0` at every iteration until the final one; `vol_below_old_0p2_floor` peaked at
**594 of 122,880 = 0.48 %**), so R7 is the **unclipped** trajectory and it died on the
**ceiling** at 1,216 iterations — R5's signature. R6, whose 0.2 floor **was** engaged (33 wing
/ 3,377 volume cells), survived **278 iterations longer**. **The floor was masking a ceiling
divergence and prolonging the run, not causing the failure.** R6 and R7 began from
sha256-identical partitions and sha256-identical 5000 fields, so this is not partition
non-determinism.

**🔴 THE PRE-DECLARED MODEL RUNG WAS NOT THIS ONE, AND THAT IS DISCLOSED.** `M6I_R1_SOLVE_
PREREGISTRATION.md` ADDENDUM 5 §A5.4 pre-declared **SA-neg (`SpalartAllmarasNeg`)** as the
model rung; §A6.2 then established by enumeration of the installed tree that **it does not
exist in OpenFOAM 2606** and that implementing it "is a solver-development task, not a run".
**k-ω SST is a different model rung, not the pre-declared one.** It is chosen because it is
shipped, is the standard transonic-wing alternative to SA, and is available today.

---

## 2. 🔴 THREE EXECUTION OBSTACLES. NONE IS OPTIONAL AND NONE IS THE LANE'S TO WAIVE.

**(a) `k` AND `ω` DO NOT EXIST ANYWHERE IN THIS FAMILY.** Measured: `L2/0.orig/` holds
`T U alphat nuTilda nut p`; `L2/processor0/5000/` holds `T U alphat nuTilda nut p phi rho`.
**Neither carries `k` or `omega`.** SST cannot start without both, with boundary conditions.
**"Everything else byte-identical" is therefore impossible** — two new fields and their BCs
must be created, and their freestream values are a registered decision with physical
consequences (§4).

**(a2) AND SST'S TWO EXTRA TRANSPORT EQUATIONS ARE NOT PROVISIONED ANYWHERE EITHER.**
Measured, not assumed: `divSchemes` carries **`default none;`** and only `div(phi,nuTilda)`;
`solvers` carries only **`p`** and **`"(U|e|nuTilda)"`**; `relaxationFactors.equations` carries
`nuTilda 0.7` (and `nuTilda 0.5` in the startup dictionary). **With `default none`, a missing
`div(phi,k)` is a hard solver failure, not a silent default** — and the same gap exists in the
**startup** dictionaries the cold-start ramp runs through. **Six locations need `k` and `omega`
added:** `fvSchemes` (div), `fvSchemes.startup` (div), `fvSolution` (solvers + relaxation),
`fvSolution.startup` (solvers + relaxation).

🔴 **EVERY ONE OF THOSE VALUES IS INHERITED FROM SA'S WORKING VARIABLE, NOT CHOSEN**, so the
model rung introduces no free numerics parameter: `div(phi,k)` and `div(phi,omega)` take
**exactly** `div(phi,nuTilda)`'s scheme in each file (`bounded Gauss limitedLinear 1`
registered, `bounded Gauss upwind` startup); the solver key becomes
`"(U|e|nuTilda|k|omega)"` with **identical** settings; relaxation becomes `k 0.7; omega 0.7;`
registered and `k 0.5; omega 0.5;` startup, **matching `nuTilda` in each.** A departure from
inheritance anywhere would be a second change and is not registered.

**(b) THE LAUNCHER WILL REFUSE THIS RUN — ON TWO SEPARATE ASSERTS.** `launch_m6i_v3.sh:85` reads `grep -qE 'RASModel +SpalartAllmaras;'
constant/turbulenceProperties || fail "model is not SpalartAllmaras"`. **And line 88 asserts
the relaxation line literally** — `'\{ p 1; U 0.7; e 0.7; nuTilda 0.7; \}'` — which
**(a2)'s required `k 0.7; omega 0.7;` necessarily breaks.** Either abort happens before the
solver starts. Changing it is a change to a
measurement/launch script and is **the supervisor's to read as a diff**
(`SUPERVISION_CHARTER.md` §3), exactly as `evaluate_m6i_level.sh` was. **This lane will hand
the diff and will not apply it.** The diff must *widen* the assert to the registered model
set, never delete it — a launcher that asserts nothing would run whatever happens to be on
disk (rule 14: insert with an assert, never replace).

**(c) R1 REGISTERED `SpalartAllmaras` AND THIS SUPERSEDES IT.** `M6I_R1_SOLVE_
PREREGISTRATION.md` records **"REGISTERED: `SpalartAllmaras`, carried from the primal the
bands were written against so the family and the frozen comparison stay on one model… a
carry-over, not a free choice."** R8 departs from that. **The AGARD bands are unaffected —
the reference does not care which model we use — but the family no longer stays on one
model, and that is a disclosure that travels with every R8 number.**

---

## 3. THE ONE CHANGE, AND A DEPARTURE FROM THE DISPATCH THAT THIS LANE FLAGS RATHER THAN MAKES SILENTLY

**THE REGISTERED CHANGE:** `constant/turbulenceProperties`: `RASModel SpalartAllmaras;` →
**`RASModel kOmegaSST;`**

**SCHEMES RETURN TO THE L2 BASELINE — `limitedLinear`, NOT `vanLeer`.** `vanLeer` was a
numerics-rung change; carrying it forward would confound the model rung with a spent one.
`div(phid,p) Gauss upwind` and `div((phi|interpolate(rho)),p) bounded Gauss upwind`, exactly
as L2 ran them. `pMinFactor 0.2`, `pMaxFactor 2.0`, both as L2.

**🔴 DEPARTURE: COLD START FROM t = 0, NOT A RESTART FROM 5000.** The dispatch said *"on L2,
from the same 5000 baseline."* **This lane registers a cold start instead and gives the
reason, for the supervisor to accept or overrule before freezing.**
Restarting SST from the SA field at 5000 would require inventing `k` and `ω` on a developed
mean field — **resetting the turbulence field while retaining the mean one.** That injects a
transient of unknown length, and **if the run then diverged, no measurement could separate
"SST is worse here" from "the turbulence reset destabilised it".** That ambiguity would
destroy §6, which is the whole point of the run. **A cold start through the launcher's own
two-stage ramp reproduces exactly the procedure L2-SA followed (0 → 200 first-order ramp →
5000), so L2-SA and L2-SST differ in the model and in nothing else.** It costs ~73
core-minutes instead of ~34; the family has spent 42.54 to date and the extra 39 buys the
only clean comparison available.

**ALSO NECESSARILY ADDED** (the §2(a) and §2(a2) obstacles, named rather than buried, and
enumerated so the pre-launch assertion can be written against a number rather than a hope):

| what | where | value |
|---|---|---|
| new field `k` | `0.orig/k` | internal/farfield uniform **0.127404**; `wing` **`kLowReWallFunction`**; `symmetry` (§4a) |
| new field `omega` | `0.orig/omega` | internal/farfield uniform **6382.5**; `wing` **`omegaWallFunction`**; `symmetry` (§4a) |
| `div(phi,k)`, `div(phi,omega)` | `fvSchemes` | `bounded Gauss limitedLinear 1` (= `div(phi,nuTilda)`) |
| `div(phi,k)`, `div(phi,omega)` | `fvSchemes.startup` | `bounded Gauss upwind` (= startup `div(phi,nuTilda)`) |
| solver key | `fvSolution`, `fvSolution.startup` | `"(U\|e\|nuTilda)"` → `"(U\|e\|nuTilda\|k\|omega)"`, settings unchanged |
| relaxation | `fvSolution` | `k 0.7; omega 0.7;` (= `nuTilda 0.7`) |
| relaxation | `fvSolution.startup` | `k 0.5; omega 0.5;` (= startup `nuTilda 0.5`) |
| instrument | `controlDict` + `system/clipCount.fo` | `clipCount`, carried from R7, verdict-inert |

**Expected diff against L2, recomputed from this table rather than asserted:** `constant/`
**one** differing file (`turbulenceProperties`, one changed line); `system/` **five**
differing files (`fvSchemes`, `fvSchemes.startup`, `fvSolution`, `fvSolution.startup`,
`controlDict`); **three** new files (`0.orig/k`, `0.orig/omega`, `system/clipCount.fo`).
**Nothing launches if the staged case does not match this table exactly.**

**DOES NOT CHANGE:** the grid and the rest of `constant/`; `nNonOrthogonalCorrectors 2`;
`limited corrected 0.33`; `transonic yes`; every `relaxationFactors` entry that exists for a
field SST also solves; `pMinFactor 0.2`; `pMaxFactor 2.0`; `constant/fvOptions` including
`limitTemperature`; `writeInterval 200`; `purgeWrite 2`; `decomposeParDict`; `endTime 5000`.
**`endTime` IS in this list and belongs here: a cold start to 5000 is L2's own endTime, and
nothing is being extended.** (R5 addendum 1 `1ba860253` records why this list is checked
explicitly.)

---

## 4. THE FREESTREAM TURBULENCE — DERIVED IN THE OPEN, AND THE JUDGEMENT LABELLED

**AGARD AR-138 publishes no freestream turbulence for TEST 2308**, and the NASA TMR material
on this box (`tmr_release/`) is the **grid-generation** release and carries no flow
conditions — checked, not assumed. **These values are therefore the lab's declared choice,
not a reference-derived quantity, and this document says so rather than dressing a judgement
as a derivation.** Arithmetic, every step, from the case's own freestream block:

- `U_inf = 291.437693 m/s`, `rho_inf = 1.176819`, `Re_c = 1.46e7`, `c_root = 1.0`
- `mu = rho·U·c/Re = 2.349106e-05 Pa·s`; **`nu = mu/rho = 1.996149e-05 m²/s`**
- **CHOSEN: turbulence intensity `I = 0.1 %`, eddy-viscosity ratio `nut/nu = 1`**
- **`k = 1.5·(U·I)² = 1.5 × (0.291438)² = 0.127404 m²/s²`**
- **`omega = k/(nut) = 0.127404 / 1.996149e-05 = 6382.5 s⁻¹`**

`I = 0.1 %` and `nut/nu = 1` are standard external-aerodynamic freestream values chosen to be
low enough not to contaminate the boundary layer and high enough to avoid laminar decay to
zero. **They are not measured and are not from the reference.**

---

## 4a. 🔴 THE WALL CONDITIONS FOR `k` AND `omega` — CHOSEN, NOT INHERITED, AND SAID SO

The six §2(a2) provisioning values were **inherited** from SA's working variable, so the model
rung introduced no free numerics parameter. **`k` and `omega` at the wall cannot be inherited
and this document will not pretend otherwise.** `nuTilda` is zero at a wall; `omega` goes to a
large finite value there and `k` to zero. **There is no SA analogue to copy.**

**Why this is not bookkeeping:** R7's own measurement puts the failure exactly where this
condition governs — **79.9 % of clipped volume cells within 0.20 c of the surface, 100 % of
clipped wing cells at x/c ≥ 0.885.** If `omega`'s wall condition is wrong, **SST's result is
uninterpretable in precisely the region the rung is asking about**, and a divergence would be
indistinguishable from the thing §7 exists to detect. That would spend the exhaustion clause
on a confounded run.

**REGISTERED: `wing { type omegaWallFunction; }` and `wing { type kLowReWallFunction; }`.**

**The basis, and the reason this is the minimal-choice option.** `omegaWallFunction` does not
take a value from this lane — **it computes one per face, from the case's own `nu` and its own
wall distance.** Read from the installed source
`omegaWallFunctionFvPatchScalarField.C:213-219`:

> `omegaVis = 6.0*nuw[facei]/(beta1_*sqr(y[facei]))`

with `beta1_` defaulting to **0.075** (`:364`, `:403`). It blends that viscous branch with a
log branch, so it is correct in both regimes rather than only the one we believe we are in.
**Choosing the shipped wall function instead of hand-entering a `fixedValue` is the same
discipline as inheriting the six: the number comes from the code and the mesh, not from a
preference.** `kLowReWallFunction` is the direct analogue of the `nutLowReWallFunction`
already on this patch and is correct on a resolved mesh.

🔴 **A CORRECTION TO THE FORM THIS WAS DISPATCHED IN.** The asymptotic was given to this lane
as `omega_wall = 60*nu/(beta1*y1^2)`. **OpenFOAM 2606 uses `6.0`, not `60`** — read from the
source above, not from recall. The two conventions differ by 10× and both appear in the
literature; **this case will use whatever the shipped wall function computes**, and the
constant is recorded here so the value can be checked rather than trusted.

**Measured on the L2 mesh so the computed value can be sanity-checked (disclosure, not a
gate).** Wall-adjacent cell-centre distance `y1` over the 1,920 wing faces:
**min 4.8246e-07, median 6.0863e-07, max 6.8151e-07 m.** With `nu = 1.996149e-05` and
`beta1 = 0.075`, the viscous branch gives `omega_wall` between **3.44e+09 and 6.86e+09 s⁻¹**,
median **4.31e+09** — about 675,000× the freestream 6382.5 s⁻¹, which is the right order for a
wall value and is the check this disclosure exists to permit.

🔴 **AND A CORRECTION TO THE y+ FIGURE THIS WAS JUSTIFIED WITH.** The wall-resolved claim was
made on **L1's** y+ max of **0.356** — verified exactly from L1's own field. **But R8 runs on
L2, whose converged y+ is min 0.068, mean 0.367, max 1.138 — 3.2× L1's.** L2 is still inside
the viscous sublayer and the low-Re treatment is still right, but **the margin is 1.138, not
0.356**, and the run is on L2.

**`nut` carries over unchanged and needs no decision:** `0.orig/nut` reads
`wing { type nutLowReWallFunction; }`, `symmetry`, `farfield { type calculated; }` — verified
by this lane from the file. `nutLowReWallFunction` is a `nut` wall function and is
model-agnostic. **One disclosure travels with it:** that same wall function is a legitimate
route to a zero y+ reading, so **any y+ number this case reports must come from the solver's
own output, not from `postProcess`.**

---

## 5. THE PREDICTION — D1, D2 AND D3 UNCHANGED

Transcribed from R5 §4.2 and unchanged through R6 and R7, **kill-only**:
**D1** `cfd_cp_rise_at_shock` at η 0.65 **≥ 0.1401**; **D2** CFD `Cp` rise across the
experiment's own shock interval at η 0.65 **≥ 0.0880**; **D3** `x_shock_cfd` must leave
**0.8851**.
**Cure gate, frozen elsewhere, re-invented nowhere:** **S1** ≥ 0.212 / ≥ 0.320; **S2**
< 0.85; **B1** ≤ 0.050 on 12 rows; **B2** ≤ Δ_local.

---

## 6. 🔴 THE NAMED ALTERNATIVE, REGISTERED BEFORE THE RUN — THIS MAY NOT BE A CLOSURE PROBLEM AT ALL

**R7's own chordwise data points away from turbulence closure**, and registering that now is
what stops a divergence being read as "SST is also bad at shocks":

- **100 % of ceiling-clipped wing cells at x/c ≥ 0.885**, median **0.997** — the trailing edge.
- **79.9 % of clipped volume cells within 0.20 c of the surface** — near-wall, not farfield.
- **Upper/lower symmetry 0.063** — near-symmetric, not a suction-side event.
- **Span-wide**, and anti-correlated with the mesh defect.

**A trailing-edge-initiated, near-wall, upper/lower-symmetric, span-wide pressure runaway at
a BLUNT trailing edge** — and this lab established the M6 trailing-edge bluntness from the
reference geometry — **looks at least as much like a STEADY solver failing on a base-flow
region that is not steady as like a turbulence closure.** A blunt-base wake sheds; a
steady-state SIMPLE solver has no admissible answer there and can only diverge or smear.

**THIS READING IS REGISTERED AS AN ALTERNATIVE, NOT AS A CONCLUSION.** It is not tested by
R8 and R8 cannot confirm it. Its consequence is fixed in §7: if SST reproduces the signature,
**the ladder is exhausted and the case parks with this alternative named in the record as the
first thing a successor should examine** — not as a fourth rung to be run tonight.

---

## 7. THE DISCRIMINATOR — NUMERIC, WITH THE ESCAPE HATCH KEPT

**The trailing-edge signature, defined from R7's measured values:** met when **all three**
hold at the first written time where ceiling-clipped wing cells exceed **5 %** of the patch:

1. **≥ 90 %** of ceiling-clipped wing cells lie at **x/c ≥ 0.80**; *(R7: 100 % at x/c ≥ 0.885)*
2. upper/lower symmetry **≤ 0.15**; *(R7: 0.063)*
3. **< 50 %** of them lie at **η ≥ 0.95**. *(R7: 18.9 %)*

- **SIGNATURE MET → MODEL RUNG SPENT → LADDER EXHAUSTED → M6I PARKS** under §0, with §9's
  record written.
- **RUN COMPLETES** (rc = 0, `End`, last time 5000, age guard) **→ a real finding about
  closure.** D1/D2/D3 and §5's cure gate are read as written. **A completed run that fails
  D1 and D2 also spends the rung** and parks by the other road.
- **DIVERGES WITH A DIFFERENT SIGNATURE → returns to the supervisor undecided.** This
  document does not pre-authorise a reading of an outcome it did not anticipate. *(R6's and
  R7's equivalent clauses both fired; the hatch is kept deliberately.)*

---

## 8. COST (rule 12)

Measured basis: **L2-SA cold-started under this identical procedure cost 73.07 core-minutes**
— 3.20 (200-iteration ramp) + 69.87 (4,800 iterations) at 4 ranks.
- **Predicted: 5,000 iterations → 73.1 core-minutes, ≈ 18 min wall at 4 ranks.**
  SST solves two transport equations where SA solves one, so the true cost may run higher;
  the cap absorbs it.
- **Cap: 219.2 core-minutes** (3 × 73.07). A crossing grades the row `NOT A RESULT`; the cap
  is never raised; **nothing is killed on spend or clock** (Sanaa directive #17).
- `cost_basis`: **MEASURED** in core-minutes from the run's own logs. Dollars **DERIVED, NOT
  MEASURED** at $0.0513/core-h → ≈ $0.062.
- **Family to date: 42.54 core-minutes across R5+R6+R7, 0 results, 3.9 % of one graded level
  (L1 = 1,098).** With R8 at prediction the mechanism hunt reaches **115.6 core-minutes,
  10.5 % of one graded level.** Estimate-vs-actual lands in `docs/COST_CALIBRATION.md`.

---

## 9. WHAT THE PARKING RECORD MUST CONTAIN, IF §7 SENDS US THERE

Registered now so it cannot be written to flatter the outcome:

1. **The graded result stands and leads:** L1 `GATE FAIL`, 12/12 B1 rows monotone,
   η 0.65-lower in band at 0.0494, span-averaged RMS 0.3328 → 0.2045 → 0.1423.
2. **What was ruled out, each with its measurement**, per §1's table.
3. **The full cost**, gross and per rung, waste named separately and never absorbed.
4. **§6's alternative**, named as the first thing a successor should examine.
5. **🔴 THE LIMITS OF WHAT WAS RULED OUT, WHICH ARE AGAINST US:**
   - the tip-cap exoneration is **spanwise only**. A mesh defect that is not
     spanwise-localised **would be invisible to that test** — and `checkMesh` reports
     **max cell aspect ratio 873.8 on L2 and 1578.6 on L1, with 1,200 high-aspect cells on
     L1**, never examined. **That is the first thing a successor should look at.**
   - ρ = −0.800 rests on **nine spatially contiguous, non-independent bands**; the honest
     headline is the raw density contrast 27.63 % against 4.96 %, not the p-value.
   - **">70°" is a threshold, not an angle.** Severity was never measured, only membership.
   - **the freestream eddy viscosity was a judgement (§4), and a transonic shock's
     location is not insensitive to it.** `I = 0.1 %` and `nut/nu = 1` were never varied.
     **This is the second thing a successor should examine, beside the aspect-ratio limit.**
   - **`k` and `omega` wall conditions were chosen, not inherited (§4a)**, in the region
     where 79.9 % of the failure lives.
   - the locus readings are **single snapshots of single runs**.
   - `clipCount` closed the **count** blindness and left the **locus** blindness open: the
     η/x distribution still comes only from a written field.
6. **A lesson** for `docs/LESSONS.md`, assigned at commit from the maximum existing number.

---

## 10. PRECONDITIONS, CONTROLS, AND WHAT THIS DOCUMENT DOES NOT DO

Graded by **`scripts/grade_m6_agard_cp.py`, blob `e9d5c04b` at `4c931d97c`**, unchanged,
**hash-verified against the committed blob in the same shell invocation as the run.** Its §7
planted control must print `reader_saw_the_plant: true` or the result is `NOT A RESULT`. The
strict completion rule applies in full **including the age guard**; P4's `End` line is read
from the terminating stage log via the driver fix at `0bc8fd09d`.

**DOES NOT:** compute a grid triple, observed order or GCI (one grid); change `pMinFactor`,
`pMaxFactor`, the `fvOptions` bounds or any relaxation factor; carry `vanLeer` forward;
register any rung beyond this one (§0); claim §6's alternative is correct; claim the
freestream turbulence values are reference-derived (§4); or revive either dead mesh
hypothesis.

*Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN — NOT COMMITTED — NO RUN AUTHORISED.
Alters no existing gate, threshold, band, cap or label. No agent's message is Sanaa's
consent. Submissions parked.*
