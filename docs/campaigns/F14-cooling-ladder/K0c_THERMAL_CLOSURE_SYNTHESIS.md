# K0c. Thermal closure synthesis: how the buoyant failures relate to the aerodynamic ones

Campaign F14, gate K0c. Written 2026-08-18 at **zero compute**. No solver was
launched, no case was built, and every number below was read out of a record or a
paper already in this repository. **Frame: HEAD at `d9475c07`**, which is where
every figure and every file measurement below was read. **HEAD moved repeatedly
while this was written and this record's own commit therefore has a later
parent**; the frame is stated separately from the parent for that reason, and any
re-derivation should use the frame.

**This document grades nothing.** It is not a gate, not a rung and not a
verification record, so it carries **no verdict token of its own**. Where a
verdict word appears it is quoted from the rung that issued it, named and dated,
and the quotation marks are doing real work. `VERIFICATION_CHARTER.md` line 95
fixes that vocabulary for gates, and borrowing it loosely for a reading would put
a grade on a page that measured nothing.

**Quotation conventions, stated once because three of the sources below are
optical character recognition of scanned pages.** Greek letters, superscripts,
typographic ligatures, mathematical operators and primes inside a quotation are
transliterated to ASCII in square brackets or by an obvious equivalent, because
`FILING_CHARTER.md` R0 and this lab's own record style keep these files ASCII.
Words the scan corrupted into non-words, and hyphens the scan dropped at a line
break, are restored. **A transliteration never changes a numeral, a subscript or
a word's identity.** Where the source text was destroyed by the scan rather than
merely non-ASCII, the sentence is **cut, or the gap is marked in place, and
either way the fact is stated**, never reconstructed: a symbol recovered by
inference is a character not read off the artifact, and
`LITERATURE_CHARTER.md` section 1 names that as fabrication. Section 4.3 carries
the two places this rule bit.

**The question is structural, and it is the only question this document tries to
answer:** are the turbulence-model failures the F14 cooling ladder measured in
buoyant cavities the same defects the aerodynamic literature and this lab's aero
record already know about, wearing different clothes, or are they a distinct
class that the aerodynamic problems cannot reach?

---

## 0. The answer, before the evidence

**Neither, cleanly. The buoyant record splits into three groups, and the split is
the finding.**

| group | the failures in it | relation to the aero side |
| --- | --- | --- |
| **A. The same defect, no thermal content** | compensating errors; grid refinement moving a quantity away from the reference | **Generic verification pathologies.** They were found here because this ladder ran a mandatory mesh pair and graded more than one quantity per model, not because the flow was buoyant. Nothing about them is thermal |
| **B. Known aerodynamic defect, new trigger** | LaunderSharmaKE relaminarising under mesh refinement | **The mechanism is a low-Reynolds-number damping function and knows nothing about buoyancy, and the aerodynamic literature in this library records it three separate times.** Spalart and Allmaras named spurious relaminarisation as a k-epsilon-family property in 1992 and designed against it. What has no precedent anywhere in this library, on either side, is the trigger: **a mesh refinement, at fixed physics and fixed coefficients** |
| **C. A distinct class** | the turbulent heat flux closure, and every quantity that depends on it | **The argument is about representation, not about what anyone measured.** Every closure-diagnosis instrument in this library is defined on the Reynolds stress or on the eddy viscosity. None of them has a turbulent-heat-flux counterpart, so none of them can express the error, let alone find it |

**The empirical fact that carries group C**, and the single most transferable
result on this page:

> **On both cavity geometries the momentum error and the thermal error were not
> slaved to one another, and the model ranking INVERTED between them.**

| geometry | graded velocity quantity | graded heat quantity | which model is nearer on velocity | which model is nearer on heat |
| --- | --- | --- | --- | --- |
| Square, Ra 1.58e9 (`K0cS_RESULTS.md` 5.1, 5.2) | peak mid-height velocity: kEpsilon **7.595 %**, kOmegaSST **19.976 %** | Nu hot wall: kEpsilon **20.548 %**, kOmegaSST **13.383 %** | **kEpsilon** | **kOmegaSST** |
| Tall, Ra 1.43e6 (`K0cT_NUSSELT_REGRADE.md` 5.1) | mid-height peak vertical velocity: kOmegaSST **+16.4 %**, LaunderSharmaKE **-33.3 %** | Nu average: kOmegaSST **-24.7 %**, LaunderSharmaKE **+5.5 %** | **kOmegaSST** | **LaunderSharmaKE** |

Two geometries, three Rayleigh decades apart, three closures between them, and
the ordering reverses on both. A benchmark that scores velocity alone would have ranked these
models one way; a benchmark that scores wall heat transfer alone ranks them the
other. **That is not a subtlety about weighting. It is a statement that the two
closure errors are independent on this case class**, and independence is exactly
the property a momentum-only benchmark cannot test, because it holds only one of
the two quantities.

---

## 1. The evidence base, stated as narrowly as it is

**The whole buoyant record behind this document is TWO cavity geometries, and
this lab ran neither experiment.** Both references are other people's published
measurements. There is no third geometry, no mixed-convection rung, no rack-row
comparison and no unsteady leg. Anything below that reads as a general statement
about buoyant flows should be read against this table instead.

| rung | geometry | Ra | reference | what the rung recorded | file |
| --- | --- | ---: | --- | --- | --- |
| K0c laminar | square cavity | 1e3 to 1e6 | de Vahl Davis via Han and Xie (2019) Table 3, tier SECONDARY | "GATE PASS. 0 of 24 graded rows failed", largest deviation 1.139 % | `K0c_RESULTS.md` |
| K0cT turbulent | tall cavity, AR 28.7 | 0.86e6, 1.43e6 | Betts and Bokhari, ERCOFTAC Case 079 primary files; Table 1 read in full 2026-08-18 | "GATE FAIL. 8 of 18 graded rows failed", plus two Nusselt rows added later | `K0cT_RESULTS.md`, `K0cT_NUSSELT_REGRADE.md` |
| K0cS turbulent | square cavity | 1.58e9 | Ampofo and Karayiannis (2003); Tian and Karayiannis (2000) Part I | "GATE FAIL", 14 of 20 graded rows; one model "REFUSED" | `K0cS_RESULTS.md` |

**Three things this table is doing that a summary would lose.**

**(a) The laminar rung is the control for everything below it.** Same solver
family, same geometry class, same schemes, same mesh-pair discipline, same
comparator architecture, same lab. Zero of twenty-four rows failed, and the worst
deviation anywhere was 1.139 percent. **The one thing that changed between that
result and the turbulent rungs was the closure.** That is the strongest single
argument on this page that the turbulent failures are modelling failures rather
than numerics, and it costs nothing to make because both rungs were already run.

**(b) The two geometries are three Rayleigh decades apart and one of them is
short of an experiment the other has.** `K0cS_RESULTS.md` section 11 states
outright that the square rung "does not transfer to the tall cavity", and section
7.1 gives a worked instance of a quantity that demonstrably does not.

**(c) One closure was not graded against the experiment at all.** LaunderSharmaKE
on the square cavity was recorded as "REFUSED": it left its own validity domain
before it could lose to the data. That distinction is section 3 below and it is
the sharpest result the ladder has produced.

### 1.1 The measured buoyant failure modes, in one place

| # | what was measured | where |
| --- | --- | --- |
| **F1** | kOmegaSST under-predicted the tall cavity's average Nusselt by **-16.79 %** (Ra 0.86e6) and **-24.75 %** (Ra 1.43e6), at **3.09** and **4.57** times the validation uncertainty of 5.43 / 5.41 % | `K0cT_NUSSELT_REGRADE.md` 3 |
| **F2** | The error **grew with Rayleigh number**, "which is the shape of a model that is not producing enough turbulent mixing and falls further behind as more is required" | same, 3 |
| **F3** | Grid refinement moved the square cavity's stratification parameter **AWAY** from the experiment for two of three closures: kOmegaSST 0.6738 -> 0.7541 against 0.481, LaunderSharmaKE 0.6199 -> 0.7784. kEpsilon moved toward it by 0.004 and was grid-converged | `K0cS_RESULTS.md` 3 |
| **F4** | LaunderSharmaKE **relaminarised on the finer mesh**: `nu_t/nu` domain maximum 17.3 -> **6.1e-4**, damping function maximum 0.887 -> **0.034**, peak Reynolds shear stress **3.89e-17**, and **25 996 `bounding k` events in 40 000 iterations** against **0** for kEpsilon on the same mesh | `K0cS_RESULTS.md` 4 |
| **F5** | LaunderSharmaKE's near-hit on tall-cavity Nusselt (**+5.50 %**, `\|E\|/u_val` **1.02**) sat beside stratification **-80.4 %** and velocity **-33.3 %**: "wrong in two directions that partly cancel in one integral" | `K0cT_NUSSELT_REGRADE.md` 5.1 |
| **F6** | kEpsilon on the square cavity reproduced the flow (stratification to 0.008, velocity to 7.6 %, Reynolds stress to 15 %) and got the wall heat transfer wrong by 20 % on the vertical walls and 38-39 % on the horizontal: "It moves the right amount of fluid and the wrong amount of heat" | `K0cS_RESULTS.md` 5.2 |
| **F7** | Moving Prt from 0.85 to 1.28 moved hot-wall Nusselt by **1.75 %**, against a registered 5-20 % and against a rung that is wrong by 20 % | `K0cS_RESULTS.md` 7.1 |
| **F8** | Two graded rows could not distinguish a turbulence model from no turbulence model. kOmegaSST passed exactly those two, and **the set of rows it passed that a laminar solve did not also pass was empty** | D411; `K0cS_RESULTS.md` 1 |
| **F9** | Neither model reached the measured eddy viscosity anywhere in the tall cavity: domain maximum `nu_t/nu` **-60.4 %** (kOmegaSST) and **-27.5 %** (LaunderSharmaKE) against a centre-line measurement of 55, a comparison deliberately built to be unfavourable to that conclusion | `K0cT_NUSSELT_REGRADE.md` 5.1 |
| **F10** | Every closure, **and no closure at all**, mis-predicted the square cavity's near-wall temperature field by the same **6.1 to 6.3 K rms**. The models differed from each other far less in the boundary layer than each differed from the experiment | `K0cS_RESULTS.md` 6.4 |

**F10 is listed and then set aside for the rest of this document.** A quantity on
which three closures and the absence of any closure agree to within 0.2 K rms is
not measuring closure. Whatever it is measuring, no argument about turbulence
models can be built on it, and this document builds none.

---

## 2. Question 1. Relaminarisation under refinement is a low-Re damping-function failure. Does that mechanism have an aerodynamic analogue, and did anyone in this library observe it there?

**Answer: YES on the mechanism, and it is old news on the aerodynamic side. This
library carries three independent aerodynamic records of a turbulence model
laminarising as an artefact. What has no precedent anywhere in this library, on
either side, is the TRIGGER: mesh refinement at fixed physics and fixed
coefficients.**

### 2.1 The mechanism, closed at zero compute against the installed source

`K0cS_RESULTS.md` section 4 attributed the collapse to "the model's own
low-Reynolds-number damping". That attribution is checkable exactly, because the
damping function is two lines of code. Read in the installed source at
`/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/turbulenceModels/RAS/LaunderSharmaKE/LaunderSharmaKE.C`,
lines 45 and 61:

```
fMu = exp(-3.4/sqr(1 + sqr(k)/(nu*epsilon)/50))          // line 45
nut = Cmu*fMu()*sqr(k)/epsilon                            // line 61
```

`fMu` depends on the turbulent Reynolds number `Re_t = k^2/(nu*eps)` **and on
nothing else**. It carries no temperature, no gravity, no density and no length
scale of the geometry. Its limit as `Re_t` goes to zero is `exp(-3.4)`.

| | value |
| --- | ---: |
| `exp(-3.4)`, the function's own zero-turbulence floor | **0.033373** |
| Measured `fMu` maximum on the fine mesh (`K0cS_RESULTS.md` 4) | **0.034** |
| `Re_t` implied by `fMu = 0.034`, by inverting line 45 | **0.137** |
| `Re_t` implied by the coarse mesh's `fMu = 0.887` | **216** |

**The reported maximum equals the model's zero-turbulence asymptote to two
significant figures.** The fine mesh did not merely reduce the damping; it drove
the domain-maximum turbulent Reynolds number to 0.137, where `fMu` has nothing
left to fall to. "Relaminarised" was the right word and the model was sitting on
its own floor. That converts a plausible attribution into an arithmetic identity,
and it cost no compute.

**Nothing in those two lines is buoyant.** A damping function of `Re_t` alone
collapses in any flow whose turbulent Reynolds number falls far enough, whatever
drives it. `K0cT_RESULTS.md` section 1.2(b) said so in advance, on a different
geometry, as a reason for its model choice:

> "Low-Re k-[eps] variants damp with functions of Re_t = k^2/([nu][eps]); at the
> very low turbulent Reynolds numbers of this cavity those functions sit in their
> steepest region, where the model becomes mesh- and seed-sensitive."

### 2.2 The aerodynamic analogue exists and is stated in the founding paper of the aero standard model

Spalart and Allmaras (1992), `docs/papers/turbulence_models/spalart_allmaras_1992_turbulence_model.pdf`,
tier READ IN FULL this session (pages 9 and 18 of the PDF read directly; the file
has no `.txt` sidecar, see section 6.2). Printed **p. 8**, section "Laminar Region
and Tripping":

> "On no account should the turbulence model be trusted to predict the transition
> location. This is true of all the models we know. Some models, including k-e,
> predict relaminarization. In situations that should induce relaminarization,
> this one tends to drop the eddy viscosity to low levels, but without 'snapping'
> to 0. We may be able to improve on this using the f_t2 function below."

**Spalart and Allmaras named spurious relaminarisation as a property of the
k-epsilon family in 1992, in an aerodynamic paper, and designed against it.**
LaunderSharmaKE is in that family. The buoyant rung did not discover a new defect;
it exhibited a documented one.

Two pages later they describe why the laminar state is an attractor at all
(printed p. 8):

> "therefore, v~ = 0 is an unstable solution of (9) (going in the direction of
> D/Dt). In a boundary-layer code the zero solution is easily maintained, but in a
> Navier-Stokes code exactly-zero values are rarely preserved, so that the model
> is 'primed' by numerical errors upstream of the trip. It then transitions at a
> rate that depends on numerical details and has little to do with the boundary
> layer's true propensity to transition [...] We verified this behavior, and it is
> not acceptable."

and, on an algebraic model's damping function doing exactly what LaunderSharma's
did, printed **p. 17** (RAE 2822 Case 10 discussion):

> "Note that a similar behavior has been observed with algebraic models: if the
> skin friction approaches zero smoothly enough, the Van Driest damping can,
> erroneously, 'shut down' the eddy viscosity across the whole layer. This is not
> what is happening here."

**Read that quotation exactly as far as it goes.** Spalart and Allmaras report the
Van Driest shut-down as a known behaviour of algebraic models and then **rule it
out** for their own case. It is a statement that the aerodynamic community had
already seen a damping function switch off an eddy viscosity across a whole
layer. It is not a measurement made in that paper, and nothing is claimed here as
if it were.

**A third, independent instance, and it is recent.** Schaefer, Cary, Mani and
Spalart (2017), `docs/papers/uncertainty_quantification/schaefer_2017_uq_sa_model.pdf`,
p. 5 of 22, tier READ IN FULL this session:

> "In the previous works by Schaefer et al.,1,3 eleven coefficients were
> originally varied in the UQ analysis for SA. In the latter work, the authors
> discovered an unwanted laminarization problem involving c_t3 and c_t4, and
> recommended removing these coefficients from the analysis by setting f_t2 = 0"

A spurious laminarisation on transonic wall-bounded aerodynamic cases, severe
enough that two closure coefficients were **removed from an uncertainty study** to
avoid it. **Three aerodynamic records, three different mechanisms of the same
class, none of them buoyant.**

### 2.3 What has no precedent: mesh refinement as the trigger

Every aerodynamic instance above is triggered by something other than the mesh:

| instance | trigger |
| --- | --- |
| Spalart and Allmaras p. 8, k-epsilon | a flow situation "that should induce relaminarization" |
| Spalart and Allmaras p. 8, the `v~ = 0` attractor | numerical noise priming an unstable zero solution |
| Spalart and Allmaras p. 17, Van Driest | skin friction approaching zero |
| Schaefer 2017 p. 5 | perturbation of two closure coefficients |
| **K0cS, LaunderSharmaKE** | **a 1.6x uniform mesh refinement, at identical physics, identical coefficients and identical boundary conditions** |

**A library-wide search found no aerodynamic statement that low-Reynolds-number
damping functions are mesh-sensitive.** The nearest passage is a list of sources
of non-smooth behaviour that spoil grid-convergence estimation, in
`docs/papers/verification_validation/eca_hoekstra_2014_numerical_uncertainty.pdf`
p. 3, which names "damping functions and switches" alongside flux limiters. That
is a statement about the error estimator, not about a damping function being
grid-sensitive, and it supports nothing further. The Spalart and Allmaras paper
itself asserts the **opposite** for its own variable and offers no grid study of
it (printed p. 7): "Therefore, the model will not require a finer grid than an
algebraic model would."

**And this lab has never looked.** A sweep of `verification/` and `docs/` found
**no aerodynamic record in this lab that measures `nu_t`, `k` or `nuTilda` as a
function of grid refinement at all.** The only such measurement the lab owns is
buoyant (`K0cT_NUSSELT_REGRADE.md` 5.1, and `K0cS_RESULTS.md` 1 for kOmegaSST's
12.1 to 6.1 fall). **That is an absence of instrumentation, not an absence of the
phenomenon**, and the two must not be conflated: the aerodynamic side of this
lab's record could not have found this defect, because nothing there was watching
for it.

### 2.4 The nearest aerodynamic thing this lab did measure, and why it is not the same thing

`verification/campaign/MODEL_FORM_H_EXTENSION_PREREGISTRATION.md` records
SpalartAllmaras converging on the periodic hills to a solution with **0 of 120
bottom-wall faces in reversed flow, attached everywhere**, where kOmegaSST
produces a bubble. That reads like a model failing to sustain turbulence. **The
record itself rules that reading out**: "mean nut 0.61x the SST field's - NOT an
over-diffusive blob; the attachment is a property of the distribution, not the
magnitude". It is also a single mesh with no refinement ladder, and the record
flags an unresolved confound (a cyclic domain gives SA's `nuTilda` no sustaining
inflow). **Not the same phenomenon**, and recorded here so the next reader does
not adopt it as one.

### 2.5 One connection considered and REJECTED

The word "relaminarisation" appears five times in the `docs/papers/` sidecars in
a non-model sense: the physical threshold Reynolds number of a duct flow
(`pinelli_uhlmann_sekimoto_kawahara_jfm2010_square_duct.txt:88,99`;
`vinuesa_et_al_jot2014_duct_aspect_ratio.txt:522`), a measured flow feature on the
NASA hump ("indicate relaminarization close to the leading-edge, followed
immediately downstream by re-transition", `greenblatt_et_al_cfdval2004_hump.txt:374`),
and a case description (`liu_wang_zhao_xiao_2509.17189.txt:3817`).

**Every one of those is relaminarisation of a fluid. The buoyant one is
relaminarisation of a model, on a fixed flow, caused by refining the mesh.** They
share a word and not an object. **REJECTED** as an analogue, and recorded rather
than omitted, because it is the easiest false connection on this page to draw.

---

## 3. Question 2. Does the stratification error point at the buoyancy production term and the turbulent heat flux closure, and is the buoyant case therefore testing a piece of the model the aero benchmarks cannot exercise?

**The premise and the conclusion have to be separated, because this record
supports the second and REFUTES the first.**

### 3.1 The buoyancy production term. REJECTED as the explanation, by the rung's own registered prediction

`K0cT_RESULTS.md` section 1.3 registered a falsifiable directional prediction
before the solver ran. It is quoted in full because the falsification is the
result:

> "**No buoyancy production or destruction term in k.** [...] So `G_b = -beta
> g.grad(T) . nu_t/Pr_t` is absent from every case here. In a stably stratified
> core that term is a **sink**.
>
> A falsifiable directional prediction was therefore registered before the run:
> *omitting a sink over-predicts core turbulence, over-mixes the core, and biases
> S LOW.*"

It was falsified twice over. Stratification came out **above** the reference for
kOmegaSST (0.2353 against 0.095), not below; and the two models, which **lack the
same term**, landed on opposite sides of the reference (0.0186 and 0.2353). A
term absent from both cannot explain a 0.217 difference between them.

**So the day order's premise does not hold on this record.** The stratification
error growing under refinement (F3) is a separate observation from the missing
`G_b`, and nothing measured here connects them. Saying otherwise would be
inventing a mechanism to fit a conclusion that turns out to be defensible on
other grounds.

**One thing the exoneration does NOT establish, stated because it is easy to
over-read.** The model twin shows that `G_b` cannot explain the difference
**between** the two models. It does not measure the term's own magnitude, and it
cannot: both cases lack it, so the comparison is blind to whatever it would have
done to both of them equally. The term's size on this flow has never been
measured in this lab. That is experiment **X5** in section 8.

### 3.2 The conclusion nevertheless holds, and the argument is about representation

The strong claim in the day order was that the buoyant case tests a piece of the
model the aero benchmarks **cannot** exercise. **The evidence supports it, by a
different route than the day order proposed: not because a specific term was
caught, but because the aerodynamic instruments in this library have no place to
put the quantity at all.**

Four instruments, each read this session, each defined on the momentum closure and
on nothing else:

| instrument | what it is defined on | the quotation |
| --- | --- | --- |
| **The Closure Challenge score** (`data_driven_rans/mcconkey_et_al_closure_challenge_2603.28884.txt`) | mean velocity, on three isothermal cases | Test cases are "Periodic hills", "Square duct", "NASA wall-mounted hump" (lines 75-86); the score is built from "`U~_i - U_true,i`" and "can be interpreted as the average fractional velocity error across all test cases" (lines 100-133) |
| **Pope's general effective-viscosity hypothesis** (`turbulence_models/pope_jfm1975_effective_viscosity_hypothesis.txt`) | the Reynolds stress tensor | "An effective-viscosity hypothesis relates the Reynolds stresses solely to the rates of strain of the fluid and to scalar quantities" (p. 331) |
| **Emory and Iaccarino's componentality contours** (`turbulence_models/emory_iaccarino_ctr2014_componentality_contours.txt`) | the Reynolds stress anisotropy tensor | the whole method is built on "the Reynolds stress anisotropy tensor" `a_ij = u'_i u'_j / 2k - delta_ij/3` (p. 123, eq. 1.1) |
| **Dow and Wang's structural uncertainty** (`uncertainty_quantification/dow_wang_aiaa2011_1762_komega_structural_uncertainty.txt`) | the turbulent viscosity field | "Throughout the process of constructing the statistical model, we only consider the output of the turbulence model, namely the turbulent viscosity field. Since all eddy viscosity models use the turbulent viscosity to relate the Reynolds stresses to the mean rate of strain, our approach applies independent of the method by which the turbulent viscosity field is computed" |

**Dow and Wang's sentence is the sharpest of the four and it cuts the way this
document needs it to.** Their method is deliberately general: it spans **every**
eddy viscosity model, linear and nonlinear alike, because it works on `nu_t`
rather than on how `nu_t` was made. That generality is bought by defining the
whole uncertainty space on the stress-strain relation. **A turbulent heat flux
error is not inside that space, not because the method is weak but because the
space has no axis for it.** The same is true of the other three: an anisotropy
tensor has no thermal component, a tensor polynomial in the velocity-gradient
tensor produces no scalar flux, and a velocity-error score is indifferent to
every Nusselt number in this campaign.

**And the same authors route buoyancy elsewhere.** Dow and Wang's own
introduction hands stratified and mixed-convection flows to other work
(Venayagamoorthy et al. for stratified k-epsilon coefficients, Kim et al. for
mixed convection) and closes "Comparisons like these shed significant light on
the uncertainties in RANS models, but typically must be performed on a case by
case basis". **Nothing is claimed here about Kim et al. or Venayagamoorthy et
al.** Per `LITERATURE_CHARTER.md` section 4, another paper's characterisation of
a third paper is not a source. What is claimed is only what Dow and Wang's own
text does: it treats buoyancy as living outside the method it is about to build.

### 3.3 The two hypotheses are separate, and the primary experiment for one of our own cases says so

The cleanest statement of the structure is in the paper the K0cS rung was graded
against. Ampofo and Karayiannis (2003), section 3.5, p. 3568, tier READ IN FULL
this session:

> "In the eddy viscosity model, one gives up the modeling of turbulent heat flux,
> u'_i T', and Reynolds stress, u'_i u'_j, equations and adopts the generalized
> Boussinesq eddy viscosity model."

and then, having written the two hypotheses as separate equations (16) and (17):

> "These hypotheses (Eqs. (16) and (17)) are valuable concepts, whose limitations
> should always be borne in mind. The turbulent diffusion hypothesis (Eq. (16))
> implies that the scalar flux vector (in the present study temperature) is
> aligned with the mean scalar gradient vector. Even in simple turbulent flows
> this is found not to be the case. For example, in an experiment on homogeneous
> turbulent shear flow [25] the angle between grad T and u'_i T' was measured to
> be 65 degrees. Similarly, the turbulent viscosity hypothesis (Eq. (17)) implies
> that the anisotropy tensor, a_ij, is aligned with the mean rate of strain
> tensor."

**Three things follow, and the third is the one that matters most.**

1. There are **two** alignment hypotheses, not one. The eddy-viscosity assumption
   and the gradient-diffusion assumption are separate assertions about separate
   quantities, and a model can violate either without violating the other. F5 and
   F6 are the two halves of that on this lab's own record.
2. The scalar one was measured wrong by **65 degrees** in **homogeneous turbulent
   shear flow**. That is not a buoyant flow, not a stratified flow, and not a
   complex geometry. **The gradient-diffusion hypothesis fails in the simplest
   turbulent flow there is**, and it fails there for reasons that have nothing to
   do with buoyancy.
3. Therefore the thermal closure is **not** a buoyancy-specific defect at all. It
   is a general defect of RANS closure that **momentum-only benchmarks have no
   way to see**, because they carry no scalar to misalign. Buoyant flows are
   simply the place where it stops being invisible, because there the scalar
   feeds back into the momentum equation and an error in it cannot be reported as
   a small correction to a passive field.

**That is the argument for the thermal ladder existing, and it is stronger than
the one the day order proposed.** The ladder is not justified by having caught a
specific missing term. It is justified because the quantity it grades is one that
four of this library's central closure instruments cannot represent, that the
field's own standard benchmark does not score, and that the primary experiment for
one of our own cases records as violated by 65 degrees in a flow far simpler than
ours.

### 3.4 The buoyant experiments supply a reference for the thermal closure. No aerodynamic benchmark in this library does

| source | what it reports | tier |
| --- | --- | --- |
| Betts and Bokhari (2000) Table 1, p. 682, via `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` A1.6(b) | centre-line `nu_T/nu` of **35** and **55**, `alpha_T/alpha` of **23** and **30**, giving a **measured Prt of 1.071 and 1.283** against the 0.85 the rung used, 21 and 34 percent low | READ IN FULL 2026-08-18 (the paper), INTERNAL (the derivation) |
| Ampofo and Karayiannis (2003) Fig. 11, p. 3569 | `alpha_t/nu`, `nu_t/nu` **and** `Prt` near the hot wall at mid-height of the square cavity, plotted against distance from the wall | READ IN FULL this session |

**Both experiments measured an eddy diffusivity.** That is a direct reference for
the thermal closure, of a kind that periodic hills, the square duct and the NASA
hump cannot supply at any mesh resolution, because none of them has a temperature.

### 3.5 A correction to this campaign's own record, found while doing this

`K0cS_RESULTS.md` section 9 filed the following under NOT OBTAINED:

> "**Turbulent Prandtl number for the square cavity** | Neither paper reports an
> eddy diffusivity or eddy viscosity for this cavity. Prt was an ungrounded
> modelling input; C3 measured its influence rather than its correctness"

**That entry is wrong, and the paper it is about contains the refutation.**
Ampofo and Karayiannis (2003) section 3.5 reports exactly those quantities for
exactly this cavity. Figure 11, p. 3569, is captioned "Turbulent diffusivity,
turbulent viscosity and turbulent Prandtl number", and the prose carries a value
without any need to digitise the figure at all (p. 3569):

> "In the comparatively wide region (X = 0.015-0.03 of Fig. 11), turbulent
> viscosity and turbulent diffusivity have a similar profile and so the turbulent
> Prandtl number takes a value of about unity."

`LITERATURE_CHARTER.md` section 2 states that "Figures count as text", so the
figure was always in scope, and here the prose alone would have been enough.

**What the correction does to C3's conclusion: it strengthens it, and that is
worth saying because the opposite would have been more newsworthy.** C3 swept Prt
from 0.85 to 1.28 and moved hot-wall Nusselt by 1.75 percent. The square cavity's
measured value of about unity lies **inside** that swept interval and much nearer
the 0.85 end, so the correction that the measurement actually calls for is
**smaller** than the 1.75 percent C3 measured. The reading that constant Prt is
not where the square cavity loses its 20 percent stands, and now it stands
against a measured value rather than against an arbitrary one.

**A second discrepancy in the same control, recorded because it was registered in
advance.** `K0cS_PREREGISTRATION.md` line 176 set the closure criterion as "If Nu
moves by under 1 %, the constant-Prt assumption is not where this case class is
losing accuracy and the day order's third named failure mode is closed negative".
The measured move was **1.75 percent**. `K0cS_RESULTS.md` section 7.1 nevertheless
headed the finding "a named failure mode CLOSED NEGATIVE", reasoning against the
5-20 percent prediction rather than against the 1 percent criterion. **The
registered criterion was not literally met, by a factor of 1.75.** The
substantive conclusion is unaffected, because 1.75 percent is under a tenth of
the error the rung is trying to explain, but the sentence a reader can safely
carry forward is the quantitative one and not the verdict-shaped one: **Prt at
this magnitude accounts for under a tenth of the square cavity's Nusselt error.**

### 3.6 The representation argument, extended to the aerodynamic model itself and to the data-driven literature

Section 3.2 covered four diagnosis instruments. The same audit was run over the
aerodynamic **model** and over the data-driven closure literature, and it returns
the same answer everywhere.

**Spalart and Allmaras (1992), read in full this session.** A search of the whole
paper for `buoyan`, `temperatur`, `Nusselt` and `enthalp` returns **zero
occurrences of each**. There is no thermal transport equation, no calibration
against any heat-transfer data, and the paper's **entire** thermal content is one
line in the appendix constants list, printed p. 21:

> "Turbulent heat transfer obeys a turbulent Prandtl number (not to be confused
> with sigma) equal to 0.9."

**The standard aerodynamic turbulence model's whole thermal closure is a
constant, asserted once, in an appendix, calibrated against nothing in the
paper.** That is not a criticism of the model: its stated calibration set is
"2-D mixing layers, wakes, and flat-plate boundary layers, which we consider to
be the building blocks for aerodynamic flows" (printed p. 1), and the paper says
plainly "The model is not intended to be universal" (printed p. 5). It is a
statement about what the aerodynamic tradition puts on the record and therefore
about what any amount of aerodynamic benchmarking can be expected to have
disciplined.

**The four data-driven RANS papers in this library, each read for its target.**

| paper | what the method targets | models a heat or scalar flux? |
| --- | --- | --- |
| Ling, Kurzawski and Templeton (JFM 2016) | "a model for the Reynolds stress anisotropy tensor from high fidelity simulation data" (abstract) | **No.** Zero occurrences of "heat flux", "scalar flux", "temperature" or "Nusselt" |
| Singh, Medida and Duraisamy (1608.03990) | "a spatially-varying term beta(x) is introduced as a multiplier of the production term" of the SA equation | **No.** Inference data are lift coefficients; outputs lift and surface pressure |
| Wu, Zhang and Zhang (2402.16355) | "adjusts the corrective factor beta (used by FIML) in the shear-stress transport (SST) model", on the omega destruction term | **No.** Zero occurrences of any thermal term |
| Liu, Wang, Zhao and Xiao (2509.17189) | "The transport equations and constitutive relation are modified simultaneously by formulating the coefficients beta and g^(i) in both relations as function of local features q" | **No.** Thermal words appear only as background motivation and in journal titles |

**Four papers, four methods, four momentum-only targets, and not one turbulent
heat flux among them.**

**The Schaefer coefficient-UQ papers, both read this session.** The 2017 SA-model
paper varies nine SA coefficients on a subsonic flat plate, the RAE 2822 and the
NASA Common Research Model, with quantities of interest "Integrated force
coefficients, loads reports, pressure coefficient distributions, and skin friction
coefficient distributions" (p. 1). The 2017 transonic-closure paper varies SA,
Wilcox 2006 k-omega and SST coefficients on the Bachalo-Johnson bump and the RAE
2822, with "drag coefficient, pressure coefficient, skin friction coefficient, and
separation bubble size" and "lift coefficient, pressure and skin friction
components of drag coefficient, and pressure coefficient" (p. 2 / printed 196).
**Neither varies `Pr_t`. Neither carries a heat-transfer quantity of interest. The
flat plate's wall is labelled "adiabatic solid wall".**

**And this lab has already read the ceiling of the eddy-viscosity UQ approach and
written it down.** `verification/campaign/W2_DOW_STRUCTURAL_UQ_READING.md:98`
records that an inferred eddy-viscosity field absorbs **70.5 to 92.1 percent** of
the **velocity** discrepancy across eight geometries, and comments that the
residual includes "the Boussinesq alignment assumption itself. That last one is
the part no eddy-viscosity band can ever cover, and it is the honest ceiling on
this whole approach." **There is no figure of that kind anywhere in this
repository for a temperature discrepancy, because nothing in the aerodynamic
record has ever produced one.**

---

## 4. Question 3. The eddy-viscosity hypothesis is Pope's target and the closure challenge's target. Does the buoyant evidence bear on it, or is it orthogonal?

**Answer: it bears on it, and on a DIFFERENT CLAUSE than Pope's. This lab has
already measured that the eddy-viscosity hypothesis fails in two separable ways,
and the buoyant record lands squarely on the second one, which is the clause
Pope's remedy does not repair.**

### 4.1 The lab has already separated the two failure modes, on aerodynamic cases, with a control

The separation was made by applying one constitutive correction, QCR2000, across
three aerodynamic flow classes and reading the sign of the result:

| case class | what QCR2000 did | source |
| --- | --- | --- |
| **Square ducts** | benchmark score 0.0811 -> **0.0455** and 0.0775 -> **0.0400**; in-plane secondary flow **3.16e-16 -> 0.6239** percent of U_bulk against a reference 0.7570 | `verification/campaign/W3_QCR_DUCT_FALSIFIER.md` 2, 3 |
| **NASA hump** | reattachment moved **+0.0022 x/c**, against a 0.010 materiality bar, and **away** from the experiment | `verification/campaign/W1_HUMP_CHALLENGE_RESULTS.md:32-37` |
| **Periodic hills** | reattachment 7.6472 -> **7.6814**, delta **+0.0342**, **away** from the band, bar 0.10 | `verification/campaign/F6b_QCR_RESULTS.md:21-29` |

The lab's own summary sentence, from `W1_HUMP_CHALLENGE_RESULTS.md`:

> "QCR2000 repairs what Boussinesq structurally cannot represent (normal-stress
> anisotropy driving secondary flow) and does nothing for what Boussinesq
> mis-scales (turbulent shear stress in a separated layer)."

The duct measurement behind the first half is the cleanest structural result the
lab owns (`verification/campaign/RANS_MODEL_COMPARISON.md`, results table):
**five linear eddy-viscosity models produce secondary flow of 6.1e-16 to 9.2e-16
percent of U_bulk against a DNS value of 2.22 percent** - "floating-point noise,
not 'small'". A cubic model gives 0.174 percent and three Reynolds-stress models
give 1.16 to 4.59 percent (`verification/campaign/D5_RSM_RESULT.md:14-25`).

### 4.2 The buoyant record lands on the magnitude side, and the numbers say so

| evidence | value | which side |
| --- | --- | --- |
| Neither cavity model reaches the measured eddy viscosity anywhere: `nu_t/nu` domain maximum **-60.4 %** (kOmegaSST) and **-27.5 %** (LaunderSharmaKE) against a measured centre-line 55 | F9 | **magnitude** |
| Nusselt error grows with Rayleigh number, -16.79 % to -24.75 %, "the shape of a model that is not producing enough turbulent mixing and falls further behind as more is required" | F1, F2 | **magnitude** |
| kOmegaSST's square-cavity `nu_t/nu` domain maximum FELL from 12.1 to 6.1 under refinement | D411 | **magnitude** |
| Graded Reynolds shear stress, square cavity fine mesh: kOmegaSST **4.71e-4** (-56.3 %) and kEpsilon **1.25e-3** (+15.4 %) against a reference **1.08e-3** | `K0cS_RESULTS.md` 5.1, 5.2 | **magnitude** |

**The last row is the decisive one and it is worth stating in the sharpest form
available.** On the square duct the linear models are wrong by **fifteen orders
of magnitude** and the answer is a structural zero. On the buoyant cavity the
same model class is wrong by **56 percent in one direction and 15 percent in the
other**. Those are not the same kind of error. **The buoyant cavity's Reynolds
stress is mis-scaled; the duct's is structurally absent.**

### 4.3 Pope's own algebra says his remedy would leave the buoyant record's failing quantity untouched

Pope (1975), `docs/papers/turbulence_models/pope_jfm1975_effective_viscosity_hypothesis.txt`,
tier READ IN FULL this session. His two-dimensional result, printed p. 336:

> "It may be seen that G1 does not influence the normal stresses and that G0 and
> G2 do not influence the shear stress."

and, three sentences later on the same page:

> "Clearly, if G0 and G2 are set to zero, as is the case in an isotropic-viscosity
> hypothesis, then the observed differences between the normal stresses cannot be
> predicted. This inherent deficiency in isotropic-viscosity hypotheses suggests
> that they will provide an inadequate closure for more complex flows, where more
> than one component of the Reynolds stress is required to close the mean momentum
> equations."

**The sentence between those two was NOT quoted, and the reason is a sourcing
rule rather than an editorial one.** The `.txt` sidecar's optical character
recognition destroyed the tensor subscripts in it - it reads "A finite value of G2
causes a,, and aZ2 t o differ and Go enables a,, to depart from zero" - and a
subscript recovered by inference is a number not read off the artifact.
`LITERATURE_CHARTER.md` section 1 names that as fabrication. The two quotations
above survive because neither depends on a subscript. Subscript-free tokens such
as `G0` are normalised from the sidecar's `GO`, and the two sentences quoted carry
the whole load of the argument below.

Immediately after them, on the same page:

> "The choice of G1, and consequently C[.], is of paramount importance as it
> dictates the predicted shear-stress level."

**The scan lost the subscript on that `C` and it is left as a marked gap.** The
argument below does not need it: the sentence says in words that `G1` is the
coefficient which dictates the shear-stress level, and that is the whole of what
is used.

**Read those two sentences against the buoyant record.** The extra terms Pope's
generalisation adds - the ones carrying `G0` and `G2` - are by his own algebra the
terms that repair **normal-stress anisotropy** and that **do not influence the
shear stress**. The buoyant rungs' one graded Reynolds-stress row is the **shear
stress** `u'v'`, and it is the quantity in error. **The part of Pope's
formulation that bears on the buoyant record is `G1`, the coefficient that sets
the shear-stress level, and not the tensor polynomial's additional terms.** In the
two-equation models this campaign actually ran, that coefficient is `Cmu`, read in
the installed source at `LaunderSharmaKE.C:61` and its default of 0.09 at
`:118-125`. **The identification is made from the code rather than from Pope's
scanned subscript**, so nothing here rests on the gap marked above.

So: **not orthogonal, but pointed at a different clause.** The buoyant evidence
speaks to the level of the eddy viscosity, which is what that coefficient sets.
Pope's
headline contribution - "the whole velocity-gradient tensor affects the predicted
Reynolds stresses", "(i) the complete Reynolds-stress tensor is realistically
modelled and (ii) the influence of streamline curvature on the Reynolds stresses
is incorporated" (abstract, p. 331) - is aimed at the anisotropy, which this
record has never measured on either cavity.

### 4.4 The precondition of the whole approach is violated, and two independent sources say so

Pope's section 2 states the domain of validity of an effective-viscosity approach
in one sentence, printed p. 333:

> "The restrictions, assumptions and conclusions of the above argument may be
> stated thus: for a high Reynolds number nearly homogeneous flow, the Reynolds
> stresses are uniquely related to the rates of strain and two independent scaling
> parameters, provided that all macroscales are proportional and that the boundary
> conditions affect only the scaling parameters."

with the reasoning behind each half on pp. 332-333:

> "It is readily seen, from the transport equations, that the triple correlation
> (which accounts for turbulent convection) will be zero only when the Reynolds
> stresses and consequently the rates of strain are homogeneous. Thus homogeneity
> of the rates of strain is a necessary condition for the effective-viscosity
> approach to be valid."

> "Two scaling parameters are sufficient provided that all macroscales of
> turbulence are proportional; this assumption can be justified only at high
> Reynolds numbers, when any influence of the laminar viscosity may be excluded."

**A weakly turbulent differentially heated cavity is neither high Reynolds number
nor nearly homogeneous.** Section 2.1 of this document measured the first half
directly: the domain-maximum turbulent Reynolds number on the K0cS fine mesh fell
to 0.137 for one of the three closures.

**And the experimentalist for that very cavity attributes the model spread to
exactly the second half.** Ampofo and Karayiannis (2003), p. 3569, section 3.6:

> "numerical results from various k-e models are not identical because the
> two-equation models cannot account correctly for the non-homogenous flow
> characteristics."

Two independent sources, one theoretical and one experimental, neither written
about the other, naming the same precondition and the same violation.

### 4.5 The eddy viscosity is not merely inaccurate in this flow, it is undefined at a point

Ampofo and Karayiannis, p. 3569, from the measured fields:

> "In the natural convection boundary layer, as shown in Fig. 10, Reynolds stress
> takes a very small value of almost zero near the wall, in the presence of a
> large mean velocity gradient and has a positive value at the maximum velocity
> location (dv/dx = 0) without u'v' becoming zero. Therefore, the distribution of
> turbulent viscosity for momentum has a discontinuity at the maximum velocity
> location. On the other hand, turbulent diffusivity for heat shows a continuous
> profile. As a consequence, the distribution of turbulent Prandtl number defined
> as a ratio of turbulent viscosity and turbulent diffusivity also has a
> discontinuity at the maximum velocity location."

**This is measured, not argued.** A differentially heated cavity has an interior
velocity maximum where the mean strain vanishes while the Reynolds shear stress
does not. At that point `nu_t = u'v' / (dv/dx)` is singular. An attached
aerodynamic boundary layer has no such interior point; a duct and a hill and a
hump are all sheared monotonically away from their walls. **This is a structural
defect of the eddy-viscosity hypothesis that the cavity geometry exposes and the
aerodynamic geometries in this library do not.**

**And the same sentence contains the cleanest statement of this document's
thesis, in the experimentalist's own words:** the turbulent viscosity is
discontinuous there and **the turbulent diffusivity for heat is continuous**. The
two closures do not merely carry independent errors, as section 0 measured. They
have different regularity in the same flow at the same point.

### 4.6 What this section does NOT establish

- **No anisotropy measurement exists on either cavity in this lab's record.** The
  row that would have tested it, peak rms vertical velocity, was **withdrawn
  before compute** and recorded in the open, because "no two-equation model can
  answer it without an isotropy assumption that Ampofo p. 3559 measured to be
  false" (`K0cS_RESULTS.md` 9). So the duct-class hypothesis is **unrefuted as
  well as unsupported** on this case class. It is experiment **X2** in section 8,
  and it is the cheapest decisive experiment on the list.
- **The aerodynamic and buoyant gates are not commensurately graded**, so nothing
  here compares "how badly" a model fails on the two sides.
  `docs/VALIDATION_INVENTORY.md:308-309` records the NASA hump reattachment row as
  "GATE REACHED" at **+13.9 percent** with the failability column reading "NO, as
  posed. A +13.95 percent miss reads GATE REACHED with no threshold that a larger
  miss would have crossed." The K0c gate rows all carry bands and all twenty were
  shown flippable in both directions. **A comparison of severity across the two
  sides would be a comparison of two different grading regimes**, and this
  document does not make one.

---

## 5. Question 4. Compensating errors are a known aerodynamic pathology. Is the LaunderSharma tall-cavity result the same phenomenon?

**Answer: YES, without qualification, and this lab owns an aerodynamic instance of
its own. This one belongs in group A and carries no thermal content whatever.**

### 5.1 The three instances side by side

| | what agreed | what was wrong underneath | ratio or size |
| --- | --- | --- | --- |
| **Buoyant, this lab** (`K0cT_NUSSELT_REGRADE.md` 5.1) | average Nusselt **+5.50 %**, inside the experiment's own 5.41 % uncertainty | core stratification **-80.4 %**, peak vertical velocity **-33.3 %** | the integral is inside the noise floor while two fields are wrong by a third and a factor of five |
| **Aerodynamic, this lab** (`research/closure/closure_eval/closure_eval_master_table.md` section C) | benchmark velocity score **0.1320 -> 0.0501** and **0.2049 -> 0.1011** on two periodic hills | continuity error **0.18 % -> 10.46 %** and **0.08 % -> 9.67 %** | **58x and 124x** |
| **Aerodynamic, literature** (Cappelli and Mansour on the NASA hump, quoted in `verification/campaign/LITERATURE_REPRODUCTION_REVIEW.md:75-81`) | k-epsilon's near-exact reattachment | a coarser mesh's numerical viscosity standing in for an under-predicted eddy viscosity | the paper's own words below |

The lab's own comment on its aerodynamic instance is the sentence that generalises:

> "On the two hills the correction is applied to, the score improves by 0.082 and
> 0.104 while the field's continuity error goes from 0.18% and 0.08% of its own
> velocity-gradient scale to 10.5% and 9.7% - a factor 58 and 124. [...] **The
> scoring metric never sees any of this.**"

and, from the same section, the sentence that makes it a compensating error rather
than merely a bad field:

> "**The two declined cases are the only submissions that are both competitive and
> clean.** [...] The part of the entry that does nothing is the part that survives
> a physics check."

**So the phenomenon is identical in structure across the two sides: a single
scored number improves while the field it was computed from becomes less
physical, and the scoring instrument is blind to the trade.** The buoyant instance
is the purer one only in that both of its compensating quantities are physical
fields rather than one physical field and one numerical property.

### 5.2 F3, grid refinement moving a quantity AWAY, is the same defect and the aero literature named its mechanism first

`K0cS_RESULTS.md` section 3 recorded that for kOmegaSST and LaunderSharmaKE "the
coarse mesh sat closer to the experiment than the converged answer does. Their
coarse agreement was cancellation between a model error and a discretisation
error". Cappelli and Mansour, on the NASA wall-mounted hump, as quoted in this
lab's own literature review:

> "results obtained using a coarse mesh are closer to experimental data than those
> obtained with a fine mesh; this is a clear indication that the eddy viscosity is
> under-predicted by the models... the numerical viscosity of a coarse mesh causes
> an increase in mixing, so that the results are closer to the experiments, for
> the wrong reason."

**Same defect, same direction, same named mechanism: an under-predicted eddy
viscosity, propped up on the coarse mesh by numerical diffusion, exposed when the
numerical diffusion is refined away.** And the buoyant record carries the
corroborating half independently: kOmegaSST's square-cavity `nu_t/nu` domain
maximum **fell from 12.1 to 6.1** under the same 1.6x refinement (D411), which is
the under-prediction Cappelli and Mansour infer, measured directly.

**This closes F3 into group A**, and it is worth noticing that the closure moves
in the direction that costs the buoyant case its novelty. The mesh-pair rule that
`K0cS_RESULTS.md` section 3 calls its own justification is a verification rule and
its justification is aerodynamic as well as buoyant.

### 5.3 F8's aerodynamic twin

D411 recorded that two square-cavity gate rows could not distinguish a turbulence
model from no turbulence model, and that a laminar solve outperformed kOmegaSST
four rows to two. The aerodynamic side of this lab has the same shape, on its own
benchmark entry: `research/closure/closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`
records that on two of the eight test cases the **supplied baseline RANS beats all
four published entries**, and "Every entrant made those two cases worse by
touching them"; `docs/VALIDATION_INVENTORY.md:380` records "**Best-on-board
individual cases: 2 of 8, both of them declined rows. Cases won by the lab's own
model: 0 of 8.**"

**Two records, two flow classes, the same result: the modelling contributed
nothing, or less than nothing, on the rows where it was measured against doing
nothing.** F8 is group A.

**And D411's two rows turn out not to be special.** A concurrent lane audited
row discrimination across six registered rungs on 2026-08-18 and reports
**"PASS cells that the trivial baseline also passed: 8 of 17"**, that is 47
percent of the passes it could evaluate, with 14 of 35 cells "carrying no
evidence about the hypothesis in either direction". That document
(`K0cS_ROW_DISCRIMINATION_AUDIT.md`) was **untracked in the working tree at the
time of this reading and is cited as work in progress**, not as a committed
record; its figures should be re-read from its committed form before anything is
built on them. What it changes for this section is the scope of the claim, not
its direction: **the non-discriminating row is a property of how this lab builds
gates, not a curiosity of one buoyant rung.**

---

## 6. Connections considered and REJECTED, each with its reason

A synthesis that reads as though everything connects is worth nothing. These were
drawn, tested against the record, and dropped. They are listed because the reason
for dropping each is more transferable than the connection would have been.

| # | connection considered | why it was REJECTED |
| --- | --- | --- |
| **R1** | The missing buoyancy production term `G_b` explains the stratification error | Falsified by the rung's own registered directional prediction. `S` came out **above** the reference, not below, and two models lacking the **same** term landed on opposite sides of it (0.0186 and 0.2353). `K0cT_RESULTS.md` 1.3 |
| **R2** | Constant turbulent Prandtl number is what the square cavity is losing accuracy to | Measured: Prt 0.85 -> 1.28 moved hot-wall Nusselt by **1.75 %** on a rung that is wrong by 20 %. Weakened further by section 3.5: Ampofo's measured square-cavity Prt is "about unity", **inside** the swept interval and nearer 0.85, so the correction the measurement calls for is smaller still. **Does NOT transfer to the tall cavity**, whose measured Prt is 21-34 % above what its rung used |
| **R3** | The buoyant failure is the square-duct anisotropy failure in another guise | **Rejected for want of evidence in both directions.** The duct failure is a structural zero, 6.1e-16 against 2.22 %; the cavity's Reynolds shear stress is wrong by 56 % and 15 %, which is a mis-scaling. And **no anisotropy measurement exists on either cavity in this lab's record** - the row that would have tested it was withdrawn before compute. Unrefuted as well as unsupported. Experiment X2 |
| **R4** | The physical relaminarisation in the NASA hump experiment is the aerodynamic analogue of LaunderSharma's collapse | Greenblatt's is a **measured feature of a fluid**; the buoyant one is a **model artefact under mesh refinement at fixed physics**. Same word, different objects. Section 2.5. The real analogue is Spalart and Allmaras p. 8 and Schaefer 2017 p. 5, and neither of those has the mesh trigger either |
| **R5** | The 6.1-6.3 K rms near-wall temperature error is a closure failure | It is **invariant across three closures and across no closure at all** (`K0cS_RESULTS.md` 6.4), so nothing about turbulence closure is being measured by it. Whatever it is, no closure argument can stand on it |
| **R6** | kOmegaSST fails buoyantly for the same reason it over-predicts hump reattachment by +13.9 % and hills reattachment by +63 to +66 % | **No shared mechanism was identified and no measurement links them.** Both are eddy-viscosity magnitude deficits by their records' own attributions, which is a family resemblance and not a mechanism. The one isothermal kOmegaSST structural failure in this library - Nielsen, Rong and Olmedo (2010) on the Annex 20 room, "The predictions with the SST model show especially a large recirculating flow in the occupied zone below the supply slot 0 < x/H < 1.5 [...] it does not corresponds to the Laser-Doppler measurements in the benchmark", on a grid "identical in all four cases" - is a **different symptom on a different flow**, and is recorded here as a live aerodynamic-side kOmegaSST failure rather than as a connection |
| **R7** | The tall cavity's 40 percent model-to-model Nusselt spread resolves in LaunderSharma's favour | Already rejected by the regrade that measured it, and rejected again here. `\|E\|/u_val = 1.02` means the error and the noise floor are the same size, and section 5.1 shows the near-hit is compensating. `K0cT_NUSSELT_REGRADE.md` 5, 5.1 |
| **R8** | The lab's aerodynamic record shows models do not relaminarise under refinement | **Not a finding, an absence of instrumentation.** No aerodynamic record in this lab measures `nu_t`, `k` or `nuTilda` against grid refinement at all. The aerodynamic side could not have found this defect. Section 2.3 |

---

## 7. What could not be sourced, and two defects found while writing this

**An omission is a finding.** `LITERATURE_CHARTER.md` section 3.

| item | consequence |
| --- | --- |
| **Durbin, "Near-wall turbulence closure modeling without damping functions"** | Cited in the reference lists of three papers here and **NOT OBTAINED**. The title supports a statement about what a community treats as a liability and supports **no number**. It is the obvious next acquisition if the damping-function line is pursued |
| **Any aerodynamic study of damping-function grid sensitivity** | **NOT FOUND** in this library. The Spalart and Allmaras paper asserts the opposite for its own variable and offers no grid study of it |
| **Tian and Karayiannis Part II** (turbulence quantities) | Still NOT OBTAINED. Every turbulence statistic on the K0cS rung is single-source (Ampofo Table 2 only), which is why G10 carries that gate's widest band |
| **Any anisotropy or normal-stress reference for either cavity that a two-equation model could be graded against** | The graded row was withdrawn before compute for a stated reason, and no substitute was found |
| **A temperature-discrepancy analogue of Dow and Wang's 70.5-92.1 percent** | Does not exist anywhere in this repository. There is no published figure here for how much of a **thermal** field error an eddy-diffusivity field can absorb |

### 7.1 Defect: this campaign filed a quantity as NOT OBTAINED that its own source reports

Recorded in full at section 3.5. `K0cS_RESULTS.md` section 9 states "Neither paper
reports an eddy diffusivity or eddy viscosity for this cavity", and Ampofo and
Karayiannis (2003) section 3.5 and Fig. 11, p. 3569, report `alpha_t/nu`,
`nu_t/nu` and `Prt` for exactly that cavity, with a prose value of "about unity"
that needs no digitisation. **The conclusion the entry was supporting survives and
is strengthened; the provenance was wrong.** This is docket-shaped and is left for
whoever owns the K0cS record, per W-4: nothing above was edited into
`K0cS_RESULTS.md`.

### 7.2 Defect: R8's sidecar rule is enforced in prose only, and thirteen in-scope PDFs are missing sidecars

`FILING_CHARTER.md` R8 states that papers are "author_year_identifier.pdf with a
matching .txt sidecar" and that "**a PDF and its sidecar always travel
together**". Read in `scripts/check_filing.py` line 240, the implemented rule is
`if base.endswith((".pdf", ".txt")) and not PAPER_NAME.match(base)` - it tests the
**name** and never the sidecar's **existence**. Measured on the tree at
`d9475c07`: **14 PDFs under `docs/papers/` have no `.txt` sidecar, 13 of them in
topic directories the rule covers** and one in `unsorted/`, which lines 238-239
exempt by name. The 13 include
`turbulence_models/spalart_allmaras_1992_turbulence_model.pdf` and both Schaefer
papers. `check_filing.py` reports **zero** of them; the two R8 violations it does
report at this frame are a naming fault on one paper, counted once for its PDF
and once for its sidecar.

**This document paid the cost.** Three of its four load-bearing aerodynamic
quotations came out of sidecar-less PDFs and had to be read page by page; a
sidecar-based sweep of the library for "relaminar" returned five hits and **missed
all three of the aerodynamic model-artefact statements in section 2.2**, which is
the exact error the sidecar rule exists to prevent. The check's own selftest
plants `docs/papers/buoyancy/Paper1.pdf` and `no_year_in_this_name.pdf` - both
naming faults - and plants no missing-sidecar control at all, so the population
for that half of R8 has always been empty. **A check that ran over nothing has not
passed.** Also left as docket-shaped rather than repaired here: repairing a filing
check inside a reading task would be grading the edit.

---

## 8. What would settle each open question, costed

**The basis of every estimate, stated because the estimate is an instrument.**
Rates are the **measured** per-case core-minutes of this campaign's own executed
rungs, not guesses: K0cS coarse 120x120 at 11.17 to 11.88, K0cS fine 192x192 at
36.17 (kOmegaSST) to 50.93 (kEpsilon); K0cT coarse 40x120 at 7.16, K0cT fine
64x192 at 11.14 (`K0cS_RESULTS.md` 8, `K0cT_RESULTS.md` Cost). Contingency is
**1.2x**, which is the figure `K0cS_RESULTS.md` section 8 recommended for the next
rung on this case class after its own estimate overshot by 2.3x. The rate is
**$0.0513 per core-hour**. **None of these was run and none is authorized by this
document.**

| # | question it settles | design | core-min | core-h | cost | what would be decisive |
| --- | --- | --- | ---: | ---: | ---: | --- |
| **X2** | **Is the buoyant eddy-viscosity failure structural (anisotropy) or a mis-scaling?** Section 4; rejection R3 | `kOmegaSSTQCR` against the recorded `kOmegaSST` twins: square cavity both meshes, tall cavity hi-Ra both meshes, plus the `Ccr1 = 0` bit-for-bit control that `W3_QCR_DUCT_FALSIFIER.md` already established on the ducts | **101.6** | 1.69 | **$0.087** | QCR moving hot-wall Nusselt by **under 1 %** and `Sp` by **under 0.02** puts the cavity with the hump and the hills and rules the anisotropy route out. QCR moving Nusselt by **more than the 10 % gate band** puts it with the ducts and makes Pope's target live. **Falsifier for the document's own group-C reading:** a large QCR effect |
| **X1** | **Is the damping-function collapse triggered by mesh refinement alone, or does it need the low-Re_t core?** Section 2.3 | LaunderSharmaKE and kEpsilon on the TMR flat plate the `MODEL_FORM_runs` tree already carries, over a **three-point near-wall spacing ladder**, instrumented for `fMu` domain maximum, `Re_t` and the `bounding k` count. 6 cases | **86.4** | 1.44 | **$0.074** | `fMu(max)` falling to `exp(-3.4)` and `bounding k` firing at any spacing on an attached fully turbulent plate means the trigger is the mesh alone and the buoyant record adds nothing about it. No collapse at any spacing means the trigger needs the cavity's low-Re_t core, and section 2.3's claim becomes a measurement. **Falsifier:** exhibit any spacing at which `fMu(max)` falls below 0.1 |
| **X4** | **Is the constant-Prt failure mode geometry-dependent?** F7, section 3.5 | Two arms on both cavities: (a) Prt at the **measured** value - 1.071 and 1.283 from Betts Table 1, about unity from Ampofo p. 3569; (b) a generalised gradient-diffusion `alphat` through `fvOptions`, with its own planted control. 12 cases. **Arm (a) on the TALL cavity is already registered elsewhere as `S-PRT` and must not be run twice - see section 8.1** | **202.3** | 3.37 | **$0.173** | Arm (a) closing the tall cavity's -16.8 / -24.8 % Nusselt gap while the square cavity stays flat at 1.75 % is a **measured geometry dependence** of a named failure mode, and it is the first one this ladder would own. A null in arm (a) and a large move in arm (b) points past constant Prt to the gradient-diffusion **form**, which is Ampofo's 65-degree statement made local |
| **X5** | **How large is the buoyancy production term on this flow?** R1's residue | `buoyantSimpleFoam` with `buoyantKEpsilon` and with `kEpsilon` on the tall cavity hi-Ra, coarse and fine, so the term is isolated from the solver change; plus a zeroed-coefficient control that must reproduce plain `kEpsilon`. 6 cases. `buoyantKEpsilon` re-verified this session as compressible-only at `/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/compressible/RAS/buoyantKEpsilon` | **114.2** | 1.90 | **$0.098** | `\|dSp\|` against the gate's own 0.05 band. The K0cT model twin exonerated the term as the explanation of the **difference between two models**; it is blind to the term's own size, because both cases lacked it. This measures the size |
| **X8** | **Do the cavity closures fail on an aerodynamic case the same way, measured by ONE instrument?** The whole document's question, put directly | The three cavity closures - `kOmegaSST`, `kEpsilon`, `LaunderSharmaKE` - on the lab's existing periodic-hill case, with the K0c gate's mesh-pair, mutation-control and both-directions discipline. **`LaunderSharmaKE` has never been run on any aerodynamic case in this lab.** 6 cases | **288.0** | 4.80 | **$0.246** | The ranking of the three closures on the hills against their ranking on the cavities. **Known risk carried in the estimate rather than hidden:** `MODEL_FORM_H_EXTENSION_PREREGISTRATION.md` records kEpsilon dying in an S1 floating-point exception at iteration 13 on the hills and realizableKE not converging by 30,000, so a two-of-three completion is the realistic outcome |
| **X3** | **Is the residual defect the stress closure or the heat flux closure?** The document's central split | **SSG first**, not LRR: `D5_RSM_RESULT.md` and `F6a_DIFFUSION_RESULTS.md` record SSG converging on both the duct and the hump while LRR over-predicted the duct by 207 % and entered a characterised limit cycle on the hump. Both cavities, mandatory coarse/fine pair | **759.6** | 12.66 | **$0.650** | **SSG fixes the tensorial stress form and keeps a simple gradient-diffusion heat flux.** Both stratification and Nusselt closing means the defect was the stress closure. **Velocity improving while the Nusselt error stays** is the result that would justify a thermal-closure research direction outright, and it is the single most informative outcome on this list |
| **X6** | Every K0cS turbulence statistic is single-source | Obtain Tian and Karayiannis Part II | **0** | 0 | **$0** | G10 becomes two-source and the widest band on that gate can be re-derived |
| **X7** | The square cavity has no reference for its own thermal closure | Digitise Ampofo Fig. 11, p. 3569: `alpha_t/nu`, `nu_t/nu`, `Prt` near the hot wall. Carries the digitisation reading uncertainty per `LITERATURE_CHARTER.md` section 2 | **0** | 0 | **$0** | Converts C3 from a sensitivity into a comparison, gives F9 a square-cavity twin, and corrects section 7.1's NOT OBTAINED entry with a number rather than an argument |
| | **TOTAL** | | **1552.2** | **25.87** | **$1.327** | |

**The two zero-cost rows should run first, and X2 should run before anything
else that costs a core-minute.** X2 is $0.087, uses an instrument the lab has
already built and controlled bit-for-bit, and is the only experiment on the list
whose result could **falsify this document's own central reading**. X3 is half the
total cost of the list and should not be scheduled until X2 has said which
hypothesis it is testing.

**On the whole list against precedent:** the total is 25.87 core-hours and
$1.327, against the K0cS rung's actual 3.44 core-hours and $0.177, and against a
standing $25 authorisation. Wall clock rather than cost is the binding constraint
on this hardware, as `K0cS_RESULTS.md` section 8 recorded, and X3's Reynolds-stress
legs are the ones that would test it: the aerodynamic RSM runs needed 118,424 to
251,703 iterations against SST's few thousand, which is why X3's estimate carries
a factor of three on iteration count before its contingency.

### 8.1 Overlap with work another lane registered the same day, and what this list must NOT duplicate

**`K0cX_PREREGISTRATION.md` was in the working tree while this document was
written, and it registers the transfer question directly.** It takes the same
three closures plus a laminar control to the tall cavity and asks of each K0cS
failure "does it travel?", with a total estimate of **500.6 core-minutes**. Its
registered arms include `S-PRT`, a turbulent-Prandtl-number sensitivity on the
tall cavity, and `S-MESH`, a third mesh level.

**Read at the working-tree state of this session, and it was modified in both
the index and the worktree at that moment**, so its content may have moved. It is
cited here as concurrent registered work rather than as a committed record, and
the overlap is stated so it is not paid for twice:

| this list | what K0cX already covers | what is left for this list |
| --- | --- | --- |
| **X4 arm (a)**, Prt at the measured value | **The tall-cavity half, as `S-PRT`.** F7's non-transfer is exactly what K0cX registered | The **square-cavity** half against Ampofo's measured "about unity", and **arm (b)** entirely - the gradient-diffusion **form**, which K0cX does not touch |
| **X1**, the damping-function trigger | K0cX tests whether LaunderSharmaKE's collapse **travels to another buoyant geometry** | X1 asks a different question: whether it happens on a **non-buoyant** flow at all. The two are complementary and neither substitutes for the other |
| **X2, X3, X5, X6, X7, X8** | nothing | all of it |

**The costed total in the table above is therefore an over-estimate of the
marginal cost by whatever K0cX's `S-PRT` legs come to.** It was not netted off,
because K0cX had not executed and its case list was still moving; netting an
estimate against a document that may change is how two lanes end up each assuming
the other ran something.

### 8.2 Two setup traps every RSM leg on this list must carry, both found on aerodynamic cases

Recorded here because they are the difference between X3 costing $0.65 and X3
costing $0.65 twice.

1. **`residualControl` naming fields the model does not transport.**
   `D5_RSM_RESULT.md` records that all three duct RSM cases named fields an RSM
   does not transport in `residualControl`, so the criterion could never be
   satisfied and all three ground toward `endTime` while already converged. This
   is D407's shape - a convergence warrant that no run could contradict - one
   level along. **This one is already instrumented against and the experiment
   should use the instrument rather than re-derive it:** the same record states
   that `scripts/case_preflight.sh` "now catches `residualControl` naming a field
   the selected turbulence model does not transport *before* a run starts, rather
   than after it grinds to a" stop. Running it is a preflight step of X3, not an
   optional check.
2. **A Reynolds-stress initial condition built from a linear eddy-viscosity
   field is not realizable.** `F6a_DIFFUSION_RESULTS.md` records that the `0/R`
   field six hump attempts were initialised from, built by `postProcess -func R`
   on a converged kEpsilon field, carried **negative normal stresses in 12.39
   percent of cells** (`Rxx` minimum -20.5), and concludes "**None of the six
   attempts above was actually testing the turbulence model.**" Six diverged or
   falsely converged runs were spent before that was found.

---

## 9. What this document does NOT establish

- **It grades nothing and carries no verdict of its own.** Every verdict word on
  this page is quoted from the rung that issued it.
- **The buoyant evidence is TWO cavity geometries, both differentially heated,
  and this lab ran neither experiment.** There is no mixed-convection rung, no
  rack-row comparison, no third geometry and no unsteady leg. Group C's argument
  rests on what the aerodynamic instruments can represent, which is a durable
  claim, and on an inversion measured on two geometries, which is not a
  population.
- **It does not identify which term is wrong.** `G_b` was exonerated as an
  explanation of the model-to-model difference and never measured for its own
  size (X5). Constant Prt was measured small on one geometry and never varied on
  the other (X4). The eddy-viscosity level is short by 27 to 60 percent on the
  tall cavity and the reason is unmeasured (X2, X3).
- **It establishes no anisotropy result on either cavity**, because none exists.
  R3 is unsupported and unrefuted, and X2 is what would decide it.
- **It does not compare severity across the two sides.** The aerodynamic and
  buoyant gates in this lab are not commensurately graded; section 4.6 gives the
  instance.
- **Section 7.2's filing defect was not repaired here** and section 7.1's
  provenance error was not edited into `K0cS_RESULTS.md`. Both are left as dated
  findings, per W-4.
- **Nothing here was submitted, sent, filed, uploaded or registered.**
  Submissions are PARKED.

---

## Dated addendum, 2026-08-18 — three of the eight experiments have reported, and two of this document's own claims did not survive them

**Nothing above is edited.** W-4. This records what the experiments this
document commissioned have returned, including where they contradict it.

### A1. Status of the section 8 list

| # | State | Result |
| --- | --- | --- |
| **X7** | **DONE**, $0 | Ampofo Fig. 11 digitised. `K0cS_FIG11_DIGITISATION.md`, D417 |
| **X2** | **RUNNING**, $0.094 est. | Pre-registered as `K0cQ_PREREGISTRATION.md`; comparator landed before any case completed |
| **X1** | **HYPOTHESIS SPACE NARROWED before it ran** — see A3 | by `K0cX`, D416 |
| **X4 arm (a)** | **tall-cavity half DONE** as `K0cX`'s `P_` arm | see A2 |
| X3, X5, X6, X8 | not started | |

### A2. Section 8's X4 registered the wrong outcome as the informative one

X4 named *"arm (a) closing the tall cavity's -16.8 / -24.8 % Nusselt gap"* as
the measured geometry dependence this ladder would own. **`K0cX` ran that arm
and the gap did not close — it widened.** At the measured `Prt`, `kOmegaSST`
went from -16.79 % to **-19.71 %** and from -24.75 % to **-29.56 %**.

**The geometry dependence is real and larger than X4 anticipated** — 1.75 % on
the square cavity against up to **14.21 %** here — but its sign depended on
which side of the experiment the model already sat on. `kEpsilon`, which
over-predicts, improved from +29.92 % to **+11.45 %** under the same correction
and carried its stratification row from FAIL to inside the band.

**So constant `Prt` is a knob trading against whatever else is wrong, and this
document should not have registered gap-closing as the informative outcome.**
The informative outcome was the one that occurred: a correction that is right on
the physics and wrong on the answer, which is evidence about the rest of the
model.

### A3. Section 2.3 named two candidates for the damping-function trigger and X1 was to separate them. Both are now ruled out

Section 2.3 read the LaunderSharma collapse as possibly triggered by **mesh
refinement alone**, and X1 was registered to separate that from **refinement
plus a low turbulent-Reynolds-number core**.

`K0cX` ran `LaunderSharmaKE` on the tall cavity over **three** mesh levels, to a
first cell **finer** than the square cavity's, with `Re_t` at the first cell
falling to **0.0278** — *lower* than where the square cavity collapsed. The
damping function's implied maximum held at **0.951 to 0.968** and `bounding k`
fired **zero** times in every case.

**Refinement alone did not trigger it, and a low `Re_t` core did not trigger it
either.** Whatever distinguishes the square cavity is neither of the two things
section 2.3 named.

**X1 is not superseded and should still run** — it asks whether the collapse
happens on a *non-buoyant* flow at all, which no case here addresses. But **its
registered outcomes no longer exhaust the possibilities, and its
pre-registration must say so before it runs.**

### A4. Section 3.5 and section 7.1 are strengthened on the value and overtaken on the form

X7 digitised the square cavity's `Prt`. Section 3.5 read Ampofo's *"about
unity"* as sitting inside C3's swept interval and nearer 0.85, so that the
correction the measurement calls for is smaller still.

**That reading holds for the outer layer and fails for the inner one.** Measured
`Prt` is **0.21 at the wall and 0.00 at X = 0.0067**, so C3's swept range of
0.85 to 1.28 **does not contain the measurement in the region that sets the wall
heat flux.**

**And the outer-layer unity is not usable the way section 3.5 uses it.** Over
X = 0.018-0.030 both `alpha_t` and `nu_t` are **negative**, about -1.4 at
X = 0.0225; `Prt` is near 1 there because it is the ratio of two negative
numbers of nearly equal size. A model with `nu_t = Cmu k^2 / epsilon >= 0`
reproduces that ratio and gets the sign of both transports wrong. **The
measurement is outside the range this ladder's three models can produce, rather
than a value they get wrong.**

### A5. What this addendum does not change

- **The central group-C reading still stands and is still untested.** X2 is the
  experiment that could falsify it and it had not reported when this was
  written.
- **R3 remains unsupported and unrefuted.** No anisotropy measurement exists on
  either cavity. A2, A3 and A4 are about `Prt`, the damping function and the
  reference, and none of them bears on the anisotropy question.
- **No verdict in any rung moves.** `K0cS`, `K0cT` and `K0cX` keep their
  recorded verdicts.
- **Submissions remain PARKED.**

---

## Dated addendum 2, 2026-08-18 22:45Z — X2 reported, and this document's central reading survived the experiment built to falsify it

**Nothing above is edited.** W-4. Addendum 1 §A5 recorded that X2 had not
reported when it was written. It has.

**VERDICT: SMALL.** `K0cQ_RESULTS.md`, D418.

`kOmegaSSTQCR` at Spalart's published `Ccr1 = 0.3`, against its own `kOmegaSST`
twins on both cavities and both meshes, moved hot-wall Nusselt by **-0.194 %,
-0.083 %, +0.022 % and +0.043 %** and stratification by at most **0.0124**.
The registered falsifier was 10 % (square) and 5.41 % (tall). **The
measurements fall short of it by a factor of 50 to 250.**

Both `Ccr1 = 0` controls returned **exact machine zero** over 14 400 and 4 800
cells, reproducing `W3_QCR_DUCT_FALSIFIER.md` on a different solver and two new
geometries.

### What it settles

- **Section 6's rejection R3 was rejected for want of evidence in both
  directions. It now has evidence and is rejected on it.** The buoyant failure
  is not the square-duct anisotropy failure in another guise.
- **Section 0's group-C reading survives the only experiment on the section 8
  list that could have falsified it**, and it survived on a measurement rather
  than on the absence of one.
- **Section 4's placement of the cavities with the hump and the hills, and not
  with the ducts, is now measured.** The force of it is the contrast: the same
  library and coefficient take the ducts' in-plane secondary flow from
  **5.5e-16 to 0.705** against a 0.813 reference, and leave the cavities' graded
  integrals alone. **This correction is decisive where the failure is
  structural and inconsequential where it is a mis-scaling.**
- **Section 9's "it establishes no anisotropy result on either cavity" is
  discharged in one direction only.** A constitutive anisotropy correction of
  the family a two-equation model can carry does not move the graded integrals.
  **Ampofo p. 3559's measurement that the isotropy assumption is false stands
  untouched**, and no anisotropy tensor has been measured on either cavity.

### What it opens

**X3 was registered as not to be scheduled until X2 had said which hypothesis
it is testing. X2 has said.** A constitutive correction is ruled out; a
Reynolds-stress **transport** model is a different instrument and is not.
X3's registered decisive outcome — *velocity improving while the Nusselt error
stays* — is now the outcome that would separate the two halves of this
document's central split, and X2's null makes that split the live question
rather than one of several.

**X2 says nothing about the heat-flux closure**, which is the other half. The
section 8 rows that bear on it are X4 arm (b), X5 and X7, and X7 has since
reported (addendum 1 §A4).
