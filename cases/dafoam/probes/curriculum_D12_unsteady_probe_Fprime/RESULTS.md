# D12-F′ — THE FD PAIRS FOR THE D12 PROBE'S UNSTEADY ADJOINT — RESULTS

Dated **2026-08-25**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing here was filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

---

## 1. VERDICT

# `NOT A RESULT`

**On BOTH components.** Neither `shape[3]` (the headline max-|·| component) nor `shape[0]`
produced a plateau: the longest run of consecutive FD steps agreeing to the pre-registered
**1.0e-2** was **one step** on each. `DAFOAM_CHARTER.md` §3 — *"the step is proved to lie in the
plateau by a sweep"* — is **not satisfied**, so no FD estimate here is an admissible reference
and **no relative error from this arm is a graded quantity.**

**All twenty-four stages returned `rc=0` and `OOMKilled false`. Every control PASSED.** This is
not a failed run. **It is a measured negative, and it is the more useful outcome**, because it
names a quantity nobody in this family had measured and that D12-proper's pre-registration does
not currently buy — see §5.

Pre-registration frozen at **`120dddd2`**, committed **before any container started**. Grading
path `d12f_grade.py` md5 **`3331c66408c2e680ec52d26a9f1a002e`**, re-verified against the
committed HEAD blob immediately before grading. **No amendment, no addendum.**

### THE SCOPE FENCE HELD

**The D12 probe's reachability verdict DID NOT MOVE and could not have.** `GATE REACHED` stands
exactly as before. **`NOT A RESULT` here is a verdict about THIS FD TABLE, not about the probe,
not about the adjoint, and not about DAFoam.** It says the sweep cannot adjudicate — not that
the gradient is wrong.

**AND IT IS NOT A LICENCE TO ASSUME THE GRADIENT IS RIGHT EITHER.** After this arm, D12's
unsteady adjoint is **still unverified**, and `DAFOAM_CHARTER.md` §2's bright line is **STILL
NOT SATISFIED** for it. The disclaimer in the probe's §4 therefore **stands and is now backed by
a measurement rather than by prose.**

---

## 2. THE TWO FD TABLES — every registered step printed, including the ones that failed

`VERIFICATION_CHARTER.md` §7: a sweep that hides its failed steps is reporting a plateau it did
not measure. **Ten of ten FD pairs ran; none is omitted.**

### Component 3 — the headline. Adjoint `d(obj)/d(shape[3]) = −1.1622935279513776e-01`

| tag | h | obj(+h) | obj(−h) | central FD | rel err vs adjoint |
|---|---|---|---|---|---|
| `s1` | 1.000e-06 | 8.9903816376983886e-02 | 8.9900742536077521e-02 | **+1.5369204532e+00** | 1.422317e+01 |
| `s2` | 1.000e-05 | 8.9902893661845840e-02 | 8.9901847271527890e-02 | **+5.2319515897e-02** | 1.450140e+00 |
| `s3` | 1.000e-04 | 8.9892351815080748e-02 | 8.9914242102105135e-02 | −1.0945143512e-01 | 5.831503e-02 |
| `s4` | 1.000e-03 | 8.9782676386811339e-02 | 9.0025880886749746e-02 | −1.2160224997e-01 | 4.622668e-02 |
| `s5` | 1.000e-02 | 8.8742613225319844e-02 | 9.1259695062014187e-02 | −1.2585409183e-01 | 8.280816e-02 |

Adjacent agreement: s1→s2 **2838 %**, s2→s3 **148 %**, s3→s4 **10.0 %**, s4→s5 **3.4 %**.

### Component 0 — bought because the probe's own plant already disagreed. Adjoint `+3.5023163495e-02`

| tag | h | obj(+h) | obj(−h) | central FD | rel err vs adjoint |
|---|---|---|---|---|---|
| `s1` | 1.000e-06 | 8.9903982554932510e-02 | 8.9903895620315172e-02 | 4.3467308669e-02 | 2.411017e-01 |
| `s2` | 1.000e-05 | 8.9904374158894781e-02 | 8.9901529583539988e-02 | 1.4222876774e-01 | 3.060991e+00 |
| `s3` | 1.000e-04 | 8.9908983681866644e-02 | 8.9895983155560188e-02 | 6.5002631532e-02 | 8.559897e-01 |
| `s4` | 1.000e-03 | 8.9949452551001438e-02 | 8.9858414752867502e-02 | 4.5518899067e-02 | 2.996798e-01 |
| `s5` | 1.000e-02 | 9.0574391736178289e-02 | 8.9552595920791150e-02 | 5.1089790769e-02 | 4.587429e-01 |

Adjacent agreement: s1→s2 **69 %**, s2→s3 **119 %**, s3→s4 **43 %**, s4→s5 **11 %**.

**No aggregate over the two components is formed anywhere** (`DAFOAM_CHARTER.md` §3: a flat
curve is per component or it is not flat). The arm verdict is the **worst** per-component
verdict; the aggregate never rescues a component.

---

## 3. THE VERDICT IS NOT AN ARTIFACT OF MY TOLERANCE — AND I CHECKED THAT AGAINST MYSELF

The registered plateau tolerance is **1.0e-2**, chosen before the data. A tight tolerance that
manufactures its own `NOT A RESULT` would be a defect in this arm, not a finding, so the
question is answered rather than left to a reader's trust:

| tolerance | longest consecutive run, component 3 | component 0 | plateau (needs ≥ 3)? |
|---|---|---|---|
| **1 %** *(registered)* | 1 | 1 | **no** |
| 2 % | 1 | 1 | **no** |
| 5 % | 2 | 1 | **no** |
| 10 % | 3 | 1 | component 3 only |
| 20 % | 3 | 2 | component 3 only |
| 50 % | 3 | 3 | both |

**Neither component plateaus at ANY tolerance a verification charter could accept.** Component 3
needs **10 %** and component 0 needs **50 %** — the latter being wider than
`DAFOAM_CHARTER.md` §2's entire FAIL threshold. **The verdict survives a 5× relaxation of my own
registered number, and it also survives D12-proper's own 2 % choice.** This table is a
post-hoc robustness check of the *instrument*; it changes no verdict and none of its rows is
offered as a graded quantity.

---

## 4. WHY THERE IS NO PLATEAU — THE MECHANISM, MEASURED

**δ_repeat is EXACTLY ZERO.** Two `run_model` runs at the unperturbed DV both returned
`obj = 8.9903939103816721e-02`, to the last digit. The solver is bit-deterministic at np=1 on
byte-identical inputs.

**AND δ_repeat = 0 IS NOT A CLEARANCE FOR ANY FD STEP. THAT IS THE HEADLINE OF THIS ARM.**

The objective's response to a **perturbed** input carries a floor that repeating an
**identical** input cannot see. Read directly off the signal column, with no reference to the
adjoint at all:

| h | `\|obj(+h) − obj(−h)\|`, component 3 |
|---|---|
| 1e-06 | 3.0738e-06 |
| 1e-05 | **1.0464e-06** |
| 1e-04 | 2.1890e-05 |
| 1e-03 | 2.4320e-04 |
| 1e-02 | 2.5171e-03 |

**The signal at h = 1e-5 is SMALLER than at h = 1e-6.** A linear response cannot do that. From
`h = 1e-4` upward the signal scales cleanly by 10× per decade — the linear-response regime —
and below it the difference is **noise, not response**. **That non-monotonicity is a
model-free demonstration of the floor: it needs no assumption about the adjoint being right.**

**Sizing the floor** (this step *does* use the adjoint, so it is a **diagnostic, not a graded
quantity**): at `h = 1e-6` the measured difference is `+3.073841e-06` where the adjoint predicts
`−2.324587e-07` — an excess of `3.31e-06`, i.e. **≈ 1.65e-06 absolute per evaluation, 1.8e-05
relative to `obj`.** The same calculation on component 0 gives **≈ 8.4e-09**, roughly **200×
smaller**, so **the floor is COMPONENT-DEPENDENT.**

**A component-dependent floor points at the mesh warp** — different FFD modes warp different
cells and can change the PIMPLE inner-iteration counts, and the linear-solver tolerances then
set the objective's reproducibility under perturbation. **THAT IS A HYPOTHESIS AND IS LABELLED
ONE. This arm did not test it**, and the test it would need — re-running the sweep with tightened
`fvSolution` tolerances and seeing whether the floor moves — was not bought.

**Why the window is closed at both ends.** At `h = 1e-4` the noise contributes
`1.65e-6 / 2.19e-5 ≈ 7.5 %` of the signal; at `h = 1e-2` the FD is still drifting by 3.4 % per
decade, so truncation is not spent. **The noise-limited error and the truncation error cross at
roughly 5 %, which leaves no `h` at which this objective supports a 1 %-consistent estimate.**
**On this 5-step cold-start window, an FD verification of the unsteady adjoint could not have
done better than about 5 % even in principle** — right at the charter's PASS boundary.

### WHAT I WILL NOT SAY

Component 0's central FD sits **30–46 % away from its adjoint at every step**, and at
`h = 1e-3` the central estimate `4.5519e-02` nearly coincides with the one-sided estimate
`4.5682e-02` that the probe's plant stage implied — **so the 30 % gap this arm was bought to
examine is NOT explained by the curvature that a one-sided difference would carry.**

**I am not converting that into a claim, and it does not appear in any verdict.** Without a
plateau I cannot separate a wrong gradient from an unconverged FD, and the registered rule says
`NOT A RESULT`. **What the observation IS good for is naming the next purchase, and that is the
only use made of it here** (§5). **A discrepancy printed and then waved off as non-binding is
worse than one never computed; this one is printed and carried into a concrete recommendation.**

---

## 5. THE FINDING THAT MATTERS FOR D12-PROPER — AND A GAP IN ITS PRE-REGISTRATION

D12-proper (`cases/dafoam/curriculum_D12/PREREGISTRATION.md`) sizes its FD step from
**`δ_eff := max(δ_repeat, δ_window)`** (gates G12R-2, G12R-3, G12R-4). Both terms are measured
from **unperturbed** runs:

- **`δ_repeat`** — three identical `run_model` runs. Its own §G12R-2 already predicts, correctly,
  that this will be **0 to machine precision**, and already warns in advance that a zero
  `δ_repeat` is not a clearance. **THIS ARM CONFIRMS THAT PREDICTION BY MEASUREMENT: 0.000000e+00.**
- **`δ_window`** — the spread of `W`-step block averages over **one** diagnostic series. This is
  a **phase** quantity: it measures how much a finite window's average depends on **where in the
  limit cycle it starts.**

**NEITHER TERM MEASURES WHAT THIS ARM MEASURED.** The floor found here is the objective's
irreproducibility **under a perturbed input on a warped mesh** — a solver-tolerance quantity,
not a phase quantity and not a repeat quantity. It was **three-plus orders of magnitude above
`δ_repeat`** on component 3, and it is what closed the small-step end of the window.

**Whether `δ_window` at `W = 300` on a developed limit cycle happens to be larger than this
perturbation floor is NOT KNOWN, by me or by anyone**, and this arm cannot settle it: its window
is a 5-step cold start where `δ_window` is not even defined. **If `δ_window` dominates, D12-proper's
`δ_eff` is adequate as written. If it does not, `h_min` is computed against a floor that is too
small and G12R-4's registered `h_min > h_max` branch — the branch that exists precisely to
return `NOT A RESULT` when no admissible step exists — could fail to fire when it should.**

**RECOMMENDED REPAIR, and it is a repair that can only make the gate STRICTER:** add a third
term `δ_pert`, measured from the sweep's own smallest steps by exactly the model-free
non-monotonicity test in §4, and take **`δ_eff := max(δ_repeat, δ_window, δ_pert)`**. No
threshold, band, cap or label changes; a term is added to a maximum, so `h_min` can only rise
and the `NOT A RESULT` branch can only become easier to fire. **Amendments to D12-proper are
still legal at the time of writing because its run root does not exist** (`CLAUDE.md` rule 2).

---

## 6. THE CONTROLS — every one PASSED

| control | result |
|---|---|
| **C1** instrument identity, **BIT-FOR-BIT** | all **four** adjoint components, `obj` and `nShapes` reproduced the committed probe values **exactly**, threshold **ZERO**. The four-delta run script **is** the probe's instrument. |
| **C2** planted zero, physical | `shape[0] = 1.234e-03` → `obj_plant = 8.9960310069169713e-02`, **response `6.270133e-04`** against floor `1.0e-9` |
| **C3** planted zero, reader-level, **per component** | **+3.719e-04** into a **COPY** on disk, **re-read from disk**: moved `1.8594999999999722e+00` against predicted `1.8594999999999999e+00` on **both** components |
| **C4** non-emptiness by count, printed, per component | **5 of 5** on each, registered minimum 4 |
| **C5** δ_repeat | **`0.000000e+00`** — see §4 |
| **C6** DV read-back | every one of the 20 FD stages' `shape` vector read from **its own JSON**, never from the directory name: `shape[idx] = ±h` and **every off-component exactly `0.0`** |

**`d12f_grade.py --selftest`: fourteen mutants, ALL flip the verdict as registered** — including
a **deliberately blinded reader** for C3, a **leaked off-component** for C6, and single-component
40 % mutants proving the worst-of rule bites from either side.
`scripts/check_grader_self_blindness.py`: **clean on both probes — NOT a proof of correctness**
and not offered as one (probe B is silent on `pathlib` and f-strings, `3dc99590`).

**THE CONTROLS PASSING IS WHAT MAKES THIS `NOT A RESULT` WORTH ANYTHING.** A non-plateau from an
instrument that had not been shown able to see a plant would be indistinguishable from a broken
reader. This one is not.

---

## 7. WHAT THIS ARM DOES **NOT** ESTABLISH

Registered before the data, unchanged:

- **It does NOT establish that D12's unsteady adjoint is wrong.** A sweep that cannot adjudicate
  adjudicates nothing.
- **Nothing about a developed limit cycle.** 5 steps, cold start. **`obj = 0.0899` is not a
  physical drag coefficient and is never to be quoted as one.**
- **Nothing about D12-proper's `δ_repeat`, `δ_window`, window length or checkpoint envelope at
  300 steps.** §4's floor is a statement about **this** window.
- **Nothing about components 1 and 2** beyond the bit-for-bit identity check.
- **Nothing about any np other than 1**, and nothing about any decomposition.
- **NOTHING ABOUT THE PATCHED TOOLCHAIN — THE ROW IS UNBOUGHT AND NAMED AS UNBOUGHT.** The
  consequence is **sharper here than for D10-F′**: D12's DV is a **shape** DV, so
  `OM_DVGEOCOMP → pyGeo FFD → IDWarp volume warp` **is** in this derivative's chain, and that is
  exactly the class `ROOTCAUSE_getRotationMatrix3d.md` and `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`
  (**both NOT FILED**) describe. **A reader may not carry anything here to `dafoam-idwarp-rot:v1`.**
  Buying that row means re-running the probe's `compute_totals` on the patched image first — a
  different arm with its own pre-registration.
- **NO FORWARD-AD OR COMPLEX-STEP REFERENCE WAS REACHED FOR**, and `DAFOAM_CHARTER.md` §2 requires
  a record to say so and why: standing up an ADF reference for an **unsteady** adjoint is a
  separate instrument with its own pre-registration. Kenway et al. (PAS 2019) §5.1 **decline** FD
  as a reference and reach 10 digits with a non-FD one. **§4 has now measured a concrete reason
  why that matters here: on this objective, FD cannot resolve better than ~5 % at any step.**
- **Nothing about `reduceIO: False`.**
- **The §4 mechanism hypothesis (mesh-warp-driven solver-tolerance floor) is UNTESTED.**

---

## 8. COST — ACTUAL vs PREDICTED (`CLAUDE.md` rule 12)

| | |
|---|---|
| **predicted** | **4.3544 core-min** (25 containers) |
| **actual gross** | **3.2504 core-min** — 24 solver stages summing 3.2004 + mesh 0.0500 |
| **ratio actual/predicted** | **0.747×** |
| runaway guard | **15.0 core-min**; spend was **0.217×** of it; **the guard never fired** |
| **derived dollars** | **$0.002779** at $0.0513/core-h, c7a.4xlarge, reported-by-owner — **DERIVED, NOT MEASURED** |
| **waste** | **0.000 core-min.** All 24 stages `rc=0`, `OOMKilled false`, every one produced a graded artifact. **A `NOT A RESULT` from a sweep that ran correctly is a PURCHASE, NOT WASTE** — the sweep is what established §4, and §5's recommendation is bought with it. |

**Attribution of the 25 % gap: MISPREDICTION.** `run_model` was predicted at the probe's
`plant` anchor of 0.1667 core-min (10 s) and measured mostly **7–8 s**. **No contention penalty
appeared.** **Waste is separately zero and is not absorbed into that ratio**
(`COMPUTE_BUDGET_CHARTER.md` §6).

**CONTENTION IS NOT CLAIMED TO BE ZERO.** Peer lanes were live throughout. `--bind-to none` was
carried on every stage; **avoiding a known mechanism is not measuring the residual, and no
uncontended control was bought. Residual contention here is UNMEASURED.**

**MEMORY.** `MemAvailable` read immediately before launch: **27.32 GiB**, against the standing
hold of **12 GiB**. `OOMKilled false` on all 24 stages.

Calibration row: **C-86** in `docs/COST_CALIBRATION.md`.

---

## 9. ARTIFACTS

Run root **`/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D12F/`**, outside git.
`ledger.txt` (per-stage `rc`, `wall_s`, `core_min`, `docker inspect`, `du_delta_B`, asserted
image id), `GRADE_OUTPUT.txt` (the frozen comparator's full output), and 24 stage directories
each with its JSON, container log and `.ok` sentinel. Toolchain asserted before any spend:
`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`.

**A number whose artifact is gone is not a result. None of these is gone.**
