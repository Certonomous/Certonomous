# K0cQ. Constitutive anisotropy on both cavities: pre-registration

Campaign F14, gate K0c. Written 2026-08-18, **before any graded case was
solved**. This is experiment **X2** of `K0c_THERMAL_CLOSURE_SYNTHESIS.md`
section 8, which named it *"the only experiment on the list whose result could
falsify this document's own central reading"* and *"the cheapest decisive
experiment on the list"*.

Run tree: `verification/runs/F14-cooling-ladder/K0cQ_runs/`.

---

## 1. The question, and why it is not already answered

`K0c_THERMAL_CLOSURE_SYNTHESIS.md` rejection **R3** — *the buoyant failure is the
square-duct anisotropy failure in another guise* — was **rejected for want of
evidence in both directions**. The duct failure is a structural zero, 6.1e-16
against 2.22 %; the cavity's Reynolds shear stress is wrong by 56 % and 15 %,
which is a mis-scaling. **No anisotropy measurement exists on either cavity in
this lab's record.** The row that would have tested it was withdrawn before
compute because *"no two-equation model can answer it without an isotropy
assumption that Ampofo p. 3559 measured to be false"* (`K0cS_RESULTS.md` §9).

**This rung answers it with a constitutive model rather than an assumption.**
Spalart's QCR2000 replaces the Boussinesq stress with a rotation-corrected one,
so it can carry Reynolds-stress anisotropy that a linear eddy-viscosity model
cannot represent at all, while leaving `k` and `omega` transport untouched.

**The synthesis's own central reading is at risk here and that is the point.**
Its group-C reading places the buoyant failure with the hump and the hills — an
eddy-viscosity *magnitude* deficit — and not with the ducts, where the defect is
*structural*. A large QCR effect on these cavities would put them with the
ducts and make Pope's target live.

---

## 2. Instrument

QCR2000 **does not ship** with OpenFOAM v2606 or v2506, verified by
`W3_QCR_DUCT_FALSIFIER.md` §2 by `grep -rli qcr` over both source trees, zero
hits. The lab wrote its own: `sdk/openfoam/qcr/kOmegaSSTQCR/`, ~180 lines
deriving from stock `kOmegaSST`, compiled to
`libkOmegaSSTQCRTurbulenceModels.so`, registered for **incompressible
transport**.

**The cavity solver is `buoyantBoussinesqSimpleFoam`, which is an
incompressible solver with a body-force term and uses `transportProperties`, so
the existing library applies without modification.** The library is used exactly
as the duct campaign used it, and **no line of it was changed for this rung**.

`k` and `omega` transport are inherited unchanged. `Ccr1 = 0.3` is Spalart's
2000 published value, not tuned here.

### 2.1 One setup change from the baseline cases, and why the control absorbs it

Both cavities' `fvSchemes` carry `default none;` — explicit schemes only. The
QCR term enters momentum as `fvc::div(alpha*rho*qcrStress())`, so the QCR arms
require one added line:

    div(qcrStress) Gauss linear;

placed beside the existing `div((nuEff*dev2(T(grad(U))))) Gauss linear;`, the
other stress-divergence term, and given **the same scheme it already uses**.
This is the only difference between a QCR arm and its baseline apart from the
model name and the library load.

**The `Ccr1 = 0` control absorbs this change completely**: with the coefficient
zero, `qcrStress` is identically zero, its divergence is zero, and the scheme
attached to it cannot act. So the control isolates the **QCR term**, not the
scheme addition.

---

## 3. Case set — 6 cases

Every QCR arm is a twin of an **already-solved, already-recorded** baseline. No
baseline is re-run and no baseline case directory is written to.

| Case | Geometry | Mesh | Baseline twin | `Ccr1` |
| --- | --- | --- | --- | --- |
| `Q_sq_c` | square, Ampofo | 14 400 | `K0cS_runs/S_SST_c` | 0.3 |
| `Q_sq_f` | square, Ampofo | 36 864 | `K0cS_runs/S_SST_f` | 0.3 |
| `Q_tl_c` | tall, Betts hi Ra | 4 800 | `K0cX_runs/X_hi_c_SST` | 0.3 |
| `Q_tl_f` | tall, Betts hi Ra | 12 288 | `K0cX_runs/X_hi_f_SST` | 0.3 |
| `Z_sq_c` | square | 14 400 | `K0cS_runs/S_SST_c` | **0** |
| `Z_tl_c` | tall, hi Ra | 4 800 | `K0cX_runs/X_hi_c_SST` | **0** |

Mesh, boundary conditions, `endTime`, `residualControl`, relaxation and every
other dictionary are **copied byte-for-byte from the baseline** apart from the
three changes named in Section 2.1 and the model name.

---

## 4. The registered decision rule, fixed before compute

The measured quantity is the **difference between a QCR arm and its own
baseline twin**, on two quantities the synthesis named:

- **hot-wall Nusselt number**, as percent of the baseline value
- **core stratification `S`**, as an absolute difference

| Outcome | Condition | Reading |
| --- | --- | --- |
| **SMALL** | `abs(dNu) < 1 %` **and** `abs(dS) < 0.02` on **both** geometries | Anisotropy route **ruled out**. The cavities sit with the hump and the hills. The synthesis's group-C reading **survives** |
| **LARGE** | `abs(dNu)` at or above the geometry's own gate band — **10 %** square (`K0cS` G1), **5.41 %** tall hi Ra (`K0cX` R10 `u_val`) | Anisotropy route **live**. The cavities sit with the ducts and **Pope's target becomes live**. **This falsifies the synthesis's central reading** |
| **INTERMEDIATE** | anything between | **Registered as its own outcome and named in advance so that it cannot be reported as either of the other two.** It would mean the term acts but does not dominate, and it settles nothing on its own |

**The two thresholds do not meet.** The gap between 1 % and 5.41 / 10 % is the
INTERMEDIATE band, and it is registered deliberately rather than closed by
choosing a single cut, because a single cut would force a binary reading onto a
measurement that may not support one.

### 4.1 Direction is registered separately from size

Size decides the structural question. **Direction decides nothing on its own and
is registered so it cannot be read as if it did.** For each arm, whether QCR
moved the quantity **toward** or **away from** the experiment is recorded. The
baseline `kOmegaSST` under-predicts Nusselt on both cavities — by 13.4 % square
(`K0cS` G1), 24.75 % tall hi Ra (`K0cX` R10) — so a QCR effect that is large
**and** toward the experiment, and one that is large **and** away from it, are
both LARGE and both falsify the group-C reading equally.

### 4.2 The null arm, and what makes it a §2c control

**The `Ccr1 = 0` arms are the registered trivial baseline**, in the exact sense
`VERIFICATION_CHARTER.md` §2c requires: the same binary, the same library, the
same case, the same added scheme, with the hypothesis's own term switched off.

**Registered requirement, from the `W3_QCR_DUCT_FALSIFIER.md` precedent, which
achieved it on the ducts:**

    max abs( U(Ccr1 = 0) - U(stock kOmegaSST) ) == 0.0   exactly

**If either control returns anything other than machine zero, the corresponding
geometry's arm is NOT A RESULT** and no difference from it is reported as
evidence. A nonzero control would mean the library changed something other than
the QCR term, and every difference measured would be uninterpretable.

---

## 5. What this rung cannot do, stated before it runs

- **It does not measure the Reynolds-stress anisotropy against data.** Neither
  cavity has a measured anisotropy tensor in this lab's library. It measures
  what a constitutive model that *can* carry anisotropy does to the two
  quantities the gates grade.
- **A SMALL result does not prove the stress tensor is isotropic.** It bounds
  how much this particular constitutive correction changes these particular
  integrals. QCR2000 is one closure of a family, and a null from it is a null
  from it.
- **It grades nothing against experiment.** Every number is a difference from a
  baseline twin. The gate verdicts of `K0cS` and `K0cX` are untouched by this
  rung and are not re-opened by it.
- **The tall coarse baseline `X_hi_c_SST` MISSED its convergence criterion**
  (`K0cX_RESULTS.md` §7). The `Q_tl_c` and `Z_tl_c` comparisons inherit that
  defect. **The tall cavity's primary comparison is therefore the FINE mesh**,
  and the coarse pair is reported with the defect attached.

---

## 6. Cost, estimated before compute

Baselines, measured from each solve's own `ExecutionTime`: `S_SST_c` 696.76 s,
`S_SST_f` 2170.42 s, `X_hi_c_SST` 384.98 s, `X_hi_f_SST` 923.17 s.

A factor of **1.25** is carried for the QCR term's per-iteration cost. Iteration
counts are fixed by each baseline's `endTime`, so the factor is per-iteration
work only, and it is an **estimate that this rung will measure**.

| Case | Baseline s | x1.25 |
| --- | ---: | ---: |
| `Q_sq_c` | 696.8 | 871 |
| `Q_sq_f` | 2170.4 | 2713 |
| `Q_tl_c` | 385.0 | 481 |
| `Q_tl_f` | 923.2 | 1154 |
| `Z_sq_c` | 696.8 | 871 |
| `Z_tl_c` | 385.0 | 481 |
| **Total** | | **6571 s = 109.5 core-min = 1.825 core-h** |

At $0.0513/core-hour: **$0.094**, against the synthesis's $0.087 estimate and a
standing $25 authorisation.

### 6.1 Pilot charged here, which produced a rate and no case value

One scratch solve of **5 iterations** was run outside this tree before this
document was written, to establish that the QCR library loads into
`buoyantBoussinesqSimpleFoam` at all. It failed first on the missing
`div(qcrStress)` scheme — which is how Section 2.1 came to be written — and then
ran clean, `ExecutionTime = 0.12 s`, printing `Ccr1 0.3`. **It produced no case
value used anywhere in this rung**, and its case directory is scratch and is not
part of the run tree.

---

## 7. Falsifier for this document

**A large QCR effect on either cavity falsifies the synthesis's group-C
reading**, which is the reading this lab currently holds. That is the outcome
this rung is built to be able to produce, and it is registered here, before
compute, as the result that would overturn the position of the document that
commissioned it.
