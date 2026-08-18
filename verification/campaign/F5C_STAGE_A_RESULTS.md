# F5c Stage A — regenerate the −10.5% with provable levers: results

Pre-registration: `F5C_UNSTEADY_PROBE_PREREGISTRATION.md`, commit **`3734270d`**
(pre-launch correction `d64565c1`). **Chief approval 2026-08-10: Stage A alone,
15.5 core-min; Stage B NOT approved and not run.** Driver committed at `f0e1fef2`
before launch. Record: `F5c_runs/stage_a_record.json`.

---

## 1. The verdict

| bar | branch | |
| --- | --- | --- |
| **M1 — does −10.5% regenerate?** | **NOT REGENERATED** | A2 returns x_r/H = **6.996**, which is **1.396 H** from the 5.6 headline against a pre-registered bar of 0.81 H |
| **M2 — is the algorithm attribution provable?** | **PROVEN** (as written — see §4, the bar was too weak) | the two legs echoed **different** `system/fvSolution` sha256 values and their answers differ by 1.313 H |
| **M3 — is the wander real?** | **RECORDED, NOT SCORED** | chief policy: no wander verdict from a `coarse` detector |

> ### Outcome **O3** fires, as pre-registered:
> **"the ≈5.6 lives only in a committed docstring; if it does not come back from
> the configuration it is attributed to, the −10.5% retracts to *unmeasured* and
> F5c's status reverts to open with no headline number. Stage B does not run."**
>
> **The −10.5% is withdrawn to *unmeasured*.** F5c has no headline reattachment
> number.

This is the outcome the charter made regeneration the first act to find, and the
chief pre-named it a success rather than a wasted arm. It cost **16.4 core-min**.

## 2. The three numbers

| leg | algorithm | relax p/U | iterations | **x_r/H** | independent near-wall U check | vs 6.26 ± 0.10 | converged? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **A1** | SIMPLEC | 0.3 / 0.6 | 2 000 | **5.564** | 5.527 | −11.1% | **no** |
| **A2** | SIMPLEC | 0.3 / 0.6 | 8 000 | **6.996** | 6.961 | **+11.7%** | **no** |
| **A3** | SIMPLE | 0.15 / 0.4 | 2 000 | **6.876** | 6.843 | +9.8% | **no** |

The two detectors agree with each other everywhere to within 0.04 H — the wall-Cf
crossing and the convention-free near-wall U_x sample give the same answer, so
none of this is a sign-convention or detector-implementation artifact. That
question is settled and stays settled.

## 3. Why "but A1 gives 5.564, so the number *did* come back" is wrong

**A1 — SIMPLEC on the coarse mesh at 2 000 iterations — lands at 5.564, within
0.036 H of the 5.6 headline.** It would be easy, and wrong, to call that a
regeneration.

**M1 was pre-registered to be scored on A2, and it is scored on A2.** Per L-44,
written this morning: *a pre-registration is frozen against improvement too — an
edit that makes it better after the outcome makes it worthless as proof.* I will
not move the goalposts to the leg that flatters the record.

**But the real reason is in the data, not the rulebook.** The x_r history the
pre-registration required each leg to sample says what that 5.564 is:

| leg | samples | x_r/H range over the **second half** of the run | peak-to-peak |
| --- | --- | --- | --- |
| A1 | 40 | 3.530 → 10.089 | **6.560 H** |
| A2 | 40 | 6.408 → 7.669 | **1.262 H** |
| A3 | 40 | 4.298 → 6.876 | **2.578 H** |

**A1's "5.564" is one sample of a quantity that was swinging over 6.56 H at the
moment the solver was told to stop.** It is not a measurement of this case's
reattachment length; it is a measurement of where iteration 2 000 happened to
fall. That the same configuration run four times longer lands at 6.996 is the
same fact stated twice.

**And the sign is wrong for the excuse the record has been leaning on.** kOmegaSST
is documented — in this module's own header — to *under*-predict BFS reattachment,
landing near 5–6 H. A2 **over**-predicts by +11.7%. A number that under-predicts
at 2 000 iterations and over-predicts at 8 000 is not the linear-eddy-viscosity
deficiency being observed; it is a solve that has not finished.

## 4. M2 scores PROVEN, and I set the bar too low

**What was achieved, and it is a first.** The two legs echoed different
`system/fvSolution` sha256 values —

| leg | `system/fvSolution` sha256 | |
| --- | --- | --- |
| A1 | `2569808326111612…` | `consistent yes;` readable **inside the archived log** |
| A3 | `94150fe67f56a6e5…` | different bytes, provably |

— and `consistent yes;` is now literally readable inside the gzipped, archived
`log.simpleFoam`, hash-bound to the bytes that ran. **For the first time in this
lab's history the F5c algorithm setting is provable from a runtime artifact**,
which is exactly what the charter-§9 caveat demanded and what it said was
"unverifiable forever" from the old logs. That gap is closed permanently.

**Two limitations, both mine, both stated rather than glossed:**

1. **The lever is not isolated.** A1 and A3 differ in `consistent` **and** in the
   relaxation factors (0.3/0.6 vs 0.15/0.4), because those are the two
   configurations the record carries. The hash proves *a different fvSolution
   ran*; it does not separate SIMPLEC from relaxation. Isolating it needs a
   fourth run (SIMPLE at 0.3/0.6, or SIMPLEC at 0.15/0.4) at ≈2.0–2.4 core-min.
2. **The second limb of my bar was too weak, and the data shows it.** I required
   |Δx_r| > 0.81 H, one face spacing. The measured Δ is 1.313 H — which passes,
   **but is a fifth of A1's own 6.56 H iteration-history swing.** A difference
   smaller than either run's internal wander cannot be attributed to the thing
   that differs between them. The bar should have been "Δx_r exceeds each run's
   own second-half spread." **M2 = PROVEN as pre-registered; the scientific
   attribution of the number to SIMPLEC is NOT supported by this pair**, and I am
   recording that as a defect in my pre-registration, not rescoring it after the
   fact.

## 5. M3 — recorded, not scored

**Chief policy, 2026-08-10, honored:** no wander verdict may be claimed from any
`coarse` run. The wall faces near the crossing are 0.55–0.81 H apart against a
0.20 H materiality bar. **No wander verdict is claimed here, in either
direction.** The numbers in §3 are reported as data.

One factual observation, offered without a verdict attached: the measured
peak-to-peak values (6.56, 2.58, 1.26 H) are **3 to 8 times the detector's own
face spacing**, so whatever they are, they are not a detector-resolution
artifact. What they *mean* is Stage B's question and remains Stage B's question.

## 6. What Stage A actually bought — the case has never converged

This is the finding the arm returns with, and it was not one of its bars.

**None of the three legs reached `residualControl`. Neither did any run before
them.** Measured SIMPLE *initial* residuals at the cap:

| leg | iterations | p (gate 1e-5) | Uy (gate 1e-6) | Ux (gate 1e-6) | k (gate 1e-6) |
| --- | --- | --- | --- | --- | --- |
| A1 | 2 000 | 2.48e-3 — **248×** off | 2.35e-3 — **2 352×** off | 1.08e-4 | 5.44e-4 |
| A2 | 8 000 | 6.63e-4 — **66×** off | 8.47e-4 — **847×** off | 2.75e-5 | 1.12e-4 |
| A3 | 2 000 | 7.72e-3 — **772×** off | 1.75e-3 — **1 752×** off | 2.40e-4 | 4.06e-4 |

Quadrupling the iterations from A1 to A2 cut the residuals by ~4× and left them
**two orders of magnitude** short of the gate. And the archived 20 000-iteration
extended run (`solve_registry/f5c_extended_simplec20k`, 31.1 core-min) never
printed `SIMPLE solution converged` either. **This case has not converged in any
run this lab has ever done, at any iteration count up to 20 000.**

The original F5c record states the opposite — *"Solver runs to deep numerical
convergence (p, U, k, omega residuals 10⁻⁵–10⁻⁹) at every configuration tested"*
— which is a reading of the **linear solver's final** residuals, not SIMPLE's
**initial** residuals. `backstep_case.py`'s own `control_dict` docstring already
names this exact trap. **Stage A is the first run to measure how far off it is.**

**Everything downstream of "converged solves that wander" inherits this.** The
whole F5c narrative — including review entry 5's framing, and including the
premise of the unsteady-probe arm — rests on the word *converged*, and the word
was never earned.

## 7. Recommendation to the chief — I have not acted on any of this

**On the docket item `f5c-unsteady-probe-run`:** its filed premise was *"a −10.5%
steady miss with wander."* **The first half is withdrawn** (§1). The second half
is not dead — it is better measured than ever — so I do **not** recommend the item
retires as premise-dead. I recommend it is **re-posed**, because it is now asking
the wrong question in the wrong order:

> You cannot ask whether a flow is unsteady until you can show the steady solve
> would have converged if it could. **This one has never converged, and nobody
> measured that until today.**

**Recommended next arm — and it is not Stage B as filed, and not the unsteady
probe:** characterize convergence on a detector that can see the answer. One
`xr-coarse` run (28 300 cells, ≤0.05 H faces through the closure region) taken to
whatever iteration count it needs, with the x_r history sampled throughout, asking
one question: **does x_r settle at all?** If it settles, F5c has a number for the
first time and the unsteady question is answered *no*. If it does not settle at a
cost the lab will bear, that is the evidence-based case for the unsteady branch —
and it is a far stronger case than the one the arm was filed on.

**Priced honestly, and the honest price is uncomfortable.** Stage B's B1 was
priced at 35–39 core-min for `xr-coarse` at 8 000 iterations. **We now know 8 000
is not converged even on the 3× cheaper coarse mesh**, so that figure is a floor,
not an estimate. At 20 000 iterations `xr-coarse` is ≈88–97 core-min, and 20 000
is measured *insufficient* on coarse. **I am not able to price the arm that
answers the question, and saying so is the honest report.** What I can price:
a 20 000-iteration `xr-coarse` run at ≈88–97 core-min buys the x_r history and a
convergence-rate curve from which the real cost becomes estimable. That is the
decision I recommend the chief take, and it is his to take.

**Also recommended, cheap:** the fourth run in §4.1 (≈2.0–2.4 core-min) that
isolates `consistent` from the relaxation factors, so the record's long-standing
"SIMPLEC moved the number" claim gets a clean answer instead of a confounded one.

**Record corrections ordered by this result** (not made by me):
`F5bc_unsteady_statistics.md`'s 2026-08-08 amendment carries the −10.5% headline
on its face and now needs a second, dated amendment retracting it to *unmeasured*;
so does review entry 5's outcome block; so does `ZERO_COMPUTE_DIAGNOSTICS_2026-08-08.md`
Task 1, which states the corrected reading as x_r/H ≈ 5.6.

## 8. Cost, measured against the bases

| leg | basis (identical configuration) | predicted | measured | ratio |
| --- | --- | --- | --- | --- |
| A1 | F5bc row 3, 142.6 s | 2.38 | **2.39** | 1.00 |
| A2 | F5bc row 4, 672.4 s | 11.21 | **11.93** | 1.06 |
| A3 | F5bc row 1, 115.3 s | 1.92 | **2.11** | 1.10 |
| **total** | | **15.51** | **16.44** | **1.06** |

Against the chief's approved 15.5 core-min: **16.44, a 6% overrun**, and the
cause is the one the pre-registration declared in advance — the bases were
measured with `sample_every = 0` and these legs sample the wall profile 40 times
each. The declared departure is the whole of the overrun.

## 9. Machinery — both gates fired, and one of them was built for this arm

- **Mesh birth certificate.** `backstep_case.py` ran `checkMesh` but **never
  certified**, which is why no F5c mesh-quality record survived anywhere in the
  archive — the pre-registration's correction (`d64565c1`) named this before
  launch. Certificates are now written **at creation** and admitted at entry
  (`f0e1fef2`); all three legs read **`flagged`** (near-wall aspect ratio only,
  accepted under Mesh Standard 3.3). **The pre-registration recorded `flagged` as
  a scored prediction because it could not be checked; it scores TRUE.**
- **Lever echo.** Fired on all three legs; `levers_verified_active` is built
  mechanically from each log. §4 is what it bought.
- **Archived.** Each leg's `system/`, `0/`, `constant/`, `log.checkMesh`,
  `birth_certificate.json`, gzipped `log.simpleFoam`, `record.json`,
  `wall_shear_profile.json`, `xr_history.json` and raw evidence samples are under
  `F5c_runs/stage_a_{A1,A2,A3}/`. `postProcessing/` is gitignored — the original
  six runs were lost exactly this way, and these are not.

## 10. What is NOT claimed

- No gate is passed. F5c's status stays `GATE NOT REACHED`, now with no headline
  number rather than a withdrawn one.
- No wander verdict, in either direction (§5).
- No claim that SIMPLEC does or does not move x_r (§4).
- No claim that the flow is or is not unsteady. Stage A cannot address it and did
  not try.
- The 6.26 ± 0.10 reference is untouched.
