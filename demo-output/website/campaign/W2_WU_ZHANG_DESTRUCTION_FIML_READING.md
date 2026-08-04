# W2 reading — Wu, Zhang & Zhang, conditioned field inversion: the destruction-term paper, and what the rank-2 entry actually is

Date: 2026-08-04 (UTC). **Zero compute** — the reading, a 4-page entry
description fetched from the benchmark's own repository, and source files copied
out of the DAFoam container image. No solver ran.

This is the reading the docket item `w3-beta-on-omega-destruction-model-patch`
was waiting on, and it returns with the patch spec (section 5) and with one
correction the lab's record needs (section 1).

---

## 0. The artifacts — there are two, and the lab's record has been citing them as one

**Artifact A, the method paper.** Wu, C., Zhang, S., and Zhang, Y.,
"Development of a Generalizable Data-driven Turbulence Model: Conditioned Field
Inversion and Symbolic Regression," arXiv:2402.16355, DOI `10.2514/1.J064416`.
**Tier: READ IN FULL** — held at `docs/papers/wu_zhang_zhang_2402.16355.pdf`
with text extraction alongside (fetched 2026-07-30; read in full this session,
2026-08-04). The arXiv abstract page (fetched this session) lists versions v1–v4
(v4 dated 14 Nov 2024) and a journal reference of "AIAA Journal 2024"; the held
PDF carries no arXiv version stamp, so which of v3/v4 it is could not be read
off the artifact and is recorded as unresolved. The volume/issue/page citation
the lab uses — AIAA Journal 63(2), 2025, pp. 687–706 — appears verbatim in
Artifact B's reference [3], and that is where it is confirmed from, not from
Artifact A itself.

**Artifact B, the rank-2 challenge entry's own description.** Wu, C., and
Zhang, Y., "The Training of the SST-QCRC Model," 4 pp., the description
document the benchmark leaderboard links for its rank-2 row. **Tier: READ IN
FULL** — fetched this session from the benchmark repository
(`submissions/wu/description_document.pdf`, linked from the README this lab
already holds a clone of), now held at
`docs/papers/wu_zhang_sst_qcrc_challenge_description.pdf` with text extraction
alongside. Note the extracted text garbles the typeset equations; the equation
claims below were read from the PDF's rendered pages, and the entry's final
expression from the PySR console listing in its Figure 2, which survives
extraction intact.

The duct scores 0.0455 / 0.0399 attributed to this entry come from the
leaderboard table in `/home/ubuntu/closure-challenge-benchmark/README.md`
(**INTERNAL, already read** — verified by C2's addendum and re-read this
session). Neither artifact contains a duct case.

---

## 1. The correction, filed first because it is the headline

The lab's record (`closure_challenge_C2_error_decomposition.md`, "The
reproduction target and the targeting answer are the same paper";
`ACTIVE_RESEARCH.md` "Top pick" paragraph) characterizes the rank-2 method as:
*invert beta on the SST omega-destruction term via DAFoam's own adjoint, train
only on public CBFS, zero-shot generalize to DUCT at 0.0455/0.0399* — cited to
Artifact A. Claim by claim:

1. **Beta on the omega-destruction term: HOLDS, for both artifacts.** Paper
   Eq. (2) (classic) and Eq. (5) (conditioned); entry Eq. (2). Details in
   section 2. The R6 correction and the w3 docket item were aimed at the right
   term.
2. **DAFoam's own discrete adjoint: HOLDS.** Paper §2.1: *"The entire framework
   for carrying out FI-CLS and FI-CND is built upon the open-source discrete
   adjoint solver DAFoam."* Entry §2 says the same.
3. **"Train only on public CBFS": TRUE of the entry, FALSE of the paper it is
   cited to.** The paper's models (SR-CLS, SR-CND) are trained on **mixed NASA
   hump + CBFS** field-inversion data — abstract, §3 opening, and §3.2 ("By
   mixing the field inversion results of the NASA hump case and the CBFS
   case"). The entry reused **only the CBFS** conditioned-inversion data
   (Artifact B §2: *"We performed field inversion on the curved backward facing
   step (CBFS) case. In fact, the data obtained in Ref. [3] using the
   conditioned field inversion is directly used"*).
4. **"Zero-shot generalize to DUCT": stated by neither artifact.** The paper
   contains no duct case; its transfer suite is periodic hills, NLR-7301, SAE
   notchback, Ahmed body, ZPG plate, NACA0012. The entry document shows only
   CBFS and the ZPG flat plate. What is true: the entry's training touched no
   duct data, so its leaderboard duct scores are zero-shot **as an inference
   this lab makes** from Artifact B plus the leaderboard — it is a sound
   inference, but the record should carry it as ours, not as their claim.
5. **The omission that changes the reproduction plan: the rank-2 model is
   SST-QCRC, not SST-plus-beta.** Artifact B Eq. (1): the entry **also adds a
   quadratic constitutive correction** to the Reynolds stress, QCR2000-form,
   `tau_ij = tau^l_ij − c_r (O_ik tau^l_kj − tau^l_ik O_kj)` with `c_r = 0.3`
   *"directly adopted"* from Spalart 2000 — **untrained, no data-driven step**.
   No lab document mentions this term. A beta-on-destruction patch alone
   therefore reproduces the paper's inversion capability, **not the deployed
   rank-2 model**; like-for-like parity with the 0.0455/0.0399 duct scores
   needs the QCR term as well.

**Documents needing correction (not fixed here, per the brief):**
`demo-output/website/closure_challenge_C2_error_decomposition.md` (the
paragraph above the R6 correction block) and
`demo-output/website/ACTIVE_RESEARCH.md` lines 384–390 — both attribute the
entry's CBFS-only/duct-zero-shot protocol to the paper and both omit QCR. The
R6 correction block itself, and `S1_FIML_FIELD_INVERSION.md`'s preamble, are
accurate as written.

**And one in-sample landmine, worth stating while it is cheap:** the paper's
own models train on the **NASA hump**, and `NASA_2DWMH` is one of the closure
challenge's eight scored cases. Reproducing the *paper's* SR-CND (hump+CBFS
training) and scoring it would be in-sample by construction — exactly
verification charter §11 / literature charter §7's last NEVER. The *entry's*
CBFS-only choice is what keeps a reproduction clean, and it is the entry, not
the paper's full protocol, that any scored reproduction must copy.

---

## 2. Claim / source / where-it-applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| **Classic FI multiplies beta into the omega-destruction term**: omega equation reads `∂(ρω)/∂t + ∂(ρu_j ω)/∂x_j = (γ/ν_t)P − β(x)·θρω² + diffusion + cross-diffusion`. Their `θ` **is** the SST constant conventionally written β (F1-blended); they renamed it to dodge the symbol clash. | Paper Eq. (2), READ IN FULL. | The w3 patch target: the coefficient of the `−θρω²` sink. Sign convention: β>1 **increases** destruction, lowers ω, **raises** ν_t = k/ω. | The production term. DAFoam's stock `betaFIOmega_` hook (production, `DAkOmegaSST.C:743`) is not this and no score from it may be set beside theirs — R6 stands. |
| **Conditioned FI (what the entry used) multiplies destruction by `[(β(x)−1)f_d + 1]`**, with `f_d = 1 − tanh((8 r_d)³)`, `r_d = (ν + ν_t)/(κ²d²√(u_i,j u_i,j))`, κ=0.41; f_d≈0 in the boundary layer, ≈1 outside. | Paper Eqs. (5)–(6); entry Eq. (2) declares itself *"identical to the formulation used in the work of Wu et al. [3]"*. Both READ IN FULL. | The patch must implement **this** form to be like-for-like with the inversion that produced the entry's training data. f_d is state-dependent and must be computed inside the model so the adjoint sees it. | The bare Eq. (2) form (FI-CLS) — also in the paper, but not what the entry deployed, and the paper's own §4.5 shows FI-CLS breaking the log layer (its Eq. 3–4 argument). |
| **Objective and prior**: `J = λ_QoI Σ_{i=1..K}[d_i − h_i(β)]² + λ_L2 Σ_j (β_j − 1)²`; `λ_QoI ≈ [Σ(d_i − h_i(1))²]⁻¹` so J≈1 at β=1; `λ_L2 ≈ 1e-5 to 1e-4`, tuned so the penalty is *"10%~20% of the error of QoI after optimization"*; initial β = 1 uniform. **No spatial smoothing term** — the prior is a plain per-cell L2 pull to 1. | Paper Eq. (7) and surrounding text, Eq. (18), READ IN FULL. | The inversion runScript for any reproduction: two scalars and a normalization, all stated. | λ_L2 needs *"some trial and error"* by their own admission — the 1e-5–1e-4 band is theirs, our band on our mesh must be re-tuned and disclosed. |
| **Optimizer: SLSQP driving the DAFoam discrete adjoint; the NASA hump inversion converged in ~140 SLSQP iterations** (both FI-CLS and FI-CND). Objective reductions: hump −61.7% (CLS) / −66.7% (CND); CBFS −88.3% (CLS) / −74.7% (CND). | Paper §2.1, §3.1.1–3.1.2, READ IN FULL. | Budgeting a reproduction: ~1.4e2 gradient evaluations per inversion. | **CBFS iteration count is not stated in the text** (figure only) — omission recorded. And the paper's own citation for SLSQP, its ref [41], is the Gill–Murray–Saunders **SNOPT** paper — the named optimizer and its citation disagree; recorded, not resolved by guessing. |
| **The inversion bounded β above at 4.** The entry caps its deployed β below 4 *"consistent with the upper bound used in the conditioned field inversion process."* | Entry §2, READ IN FULL. | Box bounds for the reproduction's design variables. This is stated **only** in the entry document — the paper never mentions bounds. | The lower bound is stated **nowhere** in either artifact — omission recorded; any lower bound we use is our choice and must be disclosed as such. |
| **CBFS training configuration**: Re_h = 13,700 (h = 1 m, inlet-center velocity 1 m/s); loss data = LES x-velocity at **30 randomly placed points** in the separation region (Bentaleb et al. 2012 LES); FI-CLS and FI-CND share the objective. | Paper §3.1.1, Eq. (18), Fig. 3, READ IN FULL. | What enters the loss for a like-for-like CBFS inversion: sparse x-velocity only — not Cf, not full fields. | **Mesh cell count for the inversion is not stated** — omission recorded (B3's 21,000-cell CBFS is our nearest stand-in, not theirs). Hump config (Re_c = 0.936e6, 40 points) is the paper's other training case — using it walks into the NASA_2DWMH in-sample trap above. |
| **Paper feature set: five features** — λ1 = tr(Ŝ²), λ2 = tr(Ω̂²), λ5 = tr(Ω̂²Ŝ²) with Ŝ = S/(β*ω), Ω̂ = Ω/(β*ω), β* = 0.09 (invariants 3–4 dropped as zero in 2D); Re_Ω = \|Ω\|d²/ν; P_k/ε = τᴿ_ij u_i,j/(β* k ω); plus the composite η = λ2λ5/Re_Ω carried from their ref [29]. **The entry uses only three: λ1, λ2, P_k/ε.** | Paper §2.2 Table 2; entry §2. Both READ IN FULL. | Inputs to the β(features) regression, all computable from local RANS state + wall distance. | The paper says "five" while Table 2 lists six named quantities (η being composite) — counted, recorded. Feature sets differ between paper and entry, one more reason the two models are not the same model. |
| **Learned expressions.** Paper SR-CLS: `β − 1 = −(3/500)λ5·tanh(−0.092λ2)`. Paper SR-CND: `β − 1 = min(0.00435·λ2², 3.806)`. **Entry (SST-QCRC): `β_CND = max(−0.1157, 0.0058525·λ2)·λ2`**, capped below 4 at deployment, complexity 15 of a PySR hall-of-fame (pop. 20×80, 1000 iterations, C_max 16 in the paper's runs). | Paper Table 4, §3.2; entry Eq. (3) as garbled text but read cleanly from Fig. 2's console listing, line `15: (max(-0.1157, lambda2 * 0.0058525) * lambda2)`. READ IN FULL. | Deploying any of the three models forward needs no adjoint at all — the expression is evaluated per cell per iteration (+10–15% runtime, paper §3.2). | Three different expressions from three different training sets. Quoting "the Wu–Zhang model" without saying which is how the next conflation starts. |
| **Paper training data handling**: samples = cells; mixed hump+CBFS datasets downsampled to ~3000 samples balancing trivial (\|β−1\|<0.05) vs nontrivial, with loss weights γ restoring the original ratio. | Paper §3.2, Eqs. (16), (19), (20), READ IN FULL. | Reproducing the regression step. | The entry's CBFS-only dataset size is not stated in Artifact B — omission recorded. |
| **The entry's second modification, QCR**: `τ_ij = τ^l_ij − c_r(O_ik τ^l_kj − τ^l_ik O_kj)`, `O_ij = (∂_j U_i − ∂_i U_j)/√(∂_n U_m ∂_n U_m)`, c_r = 0.3, untrained. | Entry Eq. (1), READ IN FULL. | Parity with the rank-2 duct scores. This term acts on the **Reynolds stress in the momentum equation**, not on the ω equation. | Not in Artifact A at all. Not covered by the w3 patch or its gate — follow-up proposal filed (section 6). |
| **Paper transfer protocol (what their "generalization" means)**: models frozen, then run on periodic hills (Xiao et al. parameterized geometries, Re_hill = 5600, α = 0.5/0.8/1.0, 3 grid levels, Δy+<1), NLR-7301 two-element airfoil (Re 2.51e6, **compressible, CFL3D** — a different solver entirely), SAE notchback (Re 2.3e6, up to 3.3e7 cells), Ahmed body 25° (Re 2.78e6), ZPG plate (Re_L 1e7), NACA0012 (Re_c 6e6). | Paper §4, READ IN FULL. | Evidence the closed-form β(features) survives solver and regime changes — the portability claim that makes a symbolic model worth patching a solver for. | **No ducts anywhere in the paper.** The challenge's α-parameterized periodic hills are the same Xiao et al. family the paper tests on — their hills overlap the challenge's *training-family* geometry, one more reason scored-case hygiene needs the entry's protocol, not the paper's. |

---

## 3. What the two-artifact split means for the reproduction, stated as a plan

- **The inversion to reproduce is the paper's CBFS FI-CND** (conditioned, β on
  destruction, Eq. (18) objective, SLSQP, DAFoam adjoint, β ≤ 4) — because that
  is the inversion whose output the entry's regression consumed.
- **The model to reproduce for duct parity is the entry's SST-QCRC** — the
  three-feature expression above **plus** the untrained QCR term.
- **The w3 patch is the precondition for the first and half of the second.**
  Its gate (FD-verified per-cell beta on destruction, 2.67%-order agreement on
  the tutorial case) is unchanged and correct; what changes is what landing it
  may be *claimed* to buy. It does not buy the rank-2 model.
- **The standing adjoint blocker is untouched by any of this.** CBFS inversion
  on this stack still dies in the adjoint linear solve (`-9`/`-3`, singular
  ILU(0) without pivoting — S1 §4 addendum, W4). The patch makes the equation
  right; it does not make the linear solve converge on CBFS. The gate case
  (5,000-cell ramp tutorial) is where the adjoint is known to converge, and
  that is where the gate is scored.

---

## 4. Charter section 6 — which trigger fired

- **Trigger 1 (a number on a case we can build): FIRED.** CBFS at Re_h 13,700
  with public Bentaleb LES data and a stated objective is buildable here (B3
  already built the case; the blocker is the adjoint, not the case). The
  proposal this obligates already exists —
  `w3-beta-on-omega-destruction-model-patch` — and this reading's section 5 is
  filed into it as its spec.
- **Trigger 2 (method admissibility as thresholds): FIRED, narrowly.** The QCR
  half of the entry is a one-constant constitutive change with no training;
  reproducing it is a capability item, filed as
  `w3-qcr-constitutive-term-for-rank2-parity` (section 6).
- **Trigger 3 (disagrees with one of our results): did not fire.** Nothing here
  contradicts a lab measurement; the correction in section 1 is to our
  *characterization*, which is what this reading exists to check.
- **Trigger 4 (limit case checkable at zero compute): fired trivially and was
  checked.** Both learned expressions reduce to β = 1 (baseline SST) where
  their features vanish: SR-CND's `min(0.00435λ2², 3.806)` → 0 as λ2 → 0, and
  the entry's `max(−0.1157, 0.0058525λ2)·λ2` → 0 as λ2 → 0, so quiescent and
  irrotational limits return the baseline model. The conditioned form
  additionally returns baseline wherever f_d = 0 regardless of β — that is its
  entire point.

---

## 5. The patch spec for `w3-beta-on-omega-destruction-model-patch`

Read from the installed source, not from documentation: DAFoam **v5.0.0**
(`pyDAFoam.py:14`), image `dafoam/opt-packages:latest`, source tree shipped in
the image at `/home/dafoamuser/dafoam/repos/dafoam/`. Files were copied out of
the image and read directly this session.

### 5.1 What changes, exactly

The omega equation is assembled in **two places**, and both carry the identical
destruction term. Both must be patched or the preconditioner assembles a
different equation than the residual:

| site | function | destruction line (verbatim) |
| --- | --- | --- |
| `DAkOmegaSST.C:745` | `calcResiduals()` — residuals AND primal solve (`solveTurbState_` both paths) | `- fvm::Sp(phase_() * rho() * beta * omega_(), omega_)` |
| `DAkOmegaSST.C:870` | `getFvMatrixFields()` — the `dRdWTPC` preconditioner rows | same line |

Here the local `beta` is `volScalarField::Internal beta(this->beta(F1))` — the
F1-blended SST constant (lines 736 / 861). The production hook for comparison
sits at lines 743 / 868: `... * GbyNu(...) * betaFIOmega_()`.

The patched term, conditioned form (paper Eq. (5), entry Eq. (2)):

```cpp
// member field (new), computed multiplier (local):
// betaMult = (betaFIOmegaDestr - 1) * fd + 1
- fvm::Sp(phase_() * rho() * betaMult() * beta * omega_(), omega_)
```

with `fd` computed **from the current state inside both functions** (it must be
inside the differentiated path — it depends on ν_t, so the adjoint must see
it):

```cpp
volScalarField magGradU(mag(fvc::grad(U_)));   // Frobenius norm = sqrt(u_i,j u_i,j)
volScalarField rd((this->nu() + nut_)
    / (sqr(scalar(0.41)) * sqr(y_) * max(magGradU, dimensionedScalar("SMALL", magGradU.dimensions(), SMALL))));
volScalarField fd(scalar(1) - tanh(pow3(scalar(8) * rd)));
volScalarField::Internal betaMult((betaFIOmegaDestr_() - scalar(1)) * fd() + scalar(1));
```

`tgradU` is already formed in both functions and can be reused. `y_` is the
registered `yWall` field (`DAkOmegaSST.C:125`) — wall distance is already a
class member. A `daOption` switch selecting classic (`betaMult =
betaFIOmegaDestr_` bare, paper Eq. (2)) vs conditioned is cheap and lets one
build serve both forms; the conditioned form is the one the entry's training
data came from.

`Qsas(S2, gamma, beta)` also receives `beta` but returns a **zero matrix**
(`DAkOmegaSST.C:280–289`) — inert, no patch needed.

### 5.2 Registration — mirror of the production hook, and it is name-only

`betaFIOmega_` is declared at `DAkOmegaSST.H:179` and constructed at
`DAkOmegaSST.C:137–146`:

```cpp
betaFIOmega_(
    IOobject("betaFIOmega", mesh.time().timeName(), mesh,
             IOobject::READ_IF_PRESENT, IOobject::AUTO_WRITE),
    mesh,
    dimensionedScalar("betaFIOmega", dimensionSet(0,0,0,0,0,0,0), 1.0),
    "zeroGradient")
```

A whole-repo sweep for `betaFIOmega` (every `.C`, `.H`, `.py`, excluding build
products) finds **no other registration point**: the name appears only in the
turbulence-model classes themselves (`DAkOmegaSST`, `DAkOmegaSSTLM`,
`DAkOmega`) plus one commented-out example in `pyDAFoam.py:470`. The
design-variable plumbing resolves the field **purely by name at runtime**:
`DAInputField::run()` does
`mesh_.thisDb().lookupObject<volScalarField>(fieldName_)`
(`DAInputField.C:107`) and writes the DV array into it; `fieldName` is
free-form in `daOptions["inputInfo"]` (no allowed-name list on the Python
side). The `DARegression` deployment path (for running the learned model
in-solver) resolves its `outputName` the same way.

**Therefore the entire patch is:**

1. `DAkOmegaSST.H`: add `volScalarField betaFIOmegaDestr_;` beside line 179.
2. `DAkOmegaSST.C` constructor: clone the initializer above with name
   `"betaFIOmegaDestr"`, default 1.0. `READ_IF_PRESENT` + default 1.0 means
   every existing case reduces to the unpatched model — backward compatible by
   construction.
3. The two destruction lines, section 5.1, plus the `fd`/`betaMult` blocks.
4. Rebuild `libDASolver` — **all three build variants**:
   `linux64GccDPInt32Opt`, `...OptADF` (forward AD), `...OptADR` (reverse AD).
   The AD variants compile this same source under operator-overloading scalar
   types, which is why **no per-term adjoint registration exists or is needed**
   — any term written in standard OpenFOAM field algebra is differentiated
   automatically. That is also how the production hook gets its derivative;
   there is nothing else to mirror.
5. runScript side: `"inputInfo": {"beta": {"type": "field", "fieldName":
   "betaFIOmegaDestr", "fieldType": "scalar", ...}}` — identical shape to S1's
   working production-hook script but for the name.

On the docket item's one unpriced question — *"it may not be doable inside the
shipped image at all"* — the answer is now measured in kind: the image ships
the full source tree **with its Make directories and objects**, and this box
already carries `dafoam-subpclu:v1`, a locally modified DAFoam image built
previously, so the patch-and-rebuild path exists in precedent. Build wall-time
remains unmeasured and is still the honest risk on the 30 core-min estimate.

### 5.3 Gate (unchanged) and where it runs

Per-cell beta on destruction driven through the discrete adjoint on the
5,000-cell ramp tutorial (the case where the SST field-inversion adjoint is
known to converge — S1 §3), directional FD against the real objective
direction, agreement of S1's order (2.67%). Protocol: S1's, at
`printInterval 1` per S1's own protocol-defect note.

### 5.4 Risks

- **R1 — wrong f_d constant by reflex.** OpenFOAM's own `kOmegaSSTDDES` shield
  uses `Cd1 = 20` for SST; the paper states **8** (the Spalart 2006 SA-DDES
  value) explicitly in Eq. (6), and the entry repeats it. A reproducer reaching
  for the built-in DDES shield silently gets 20. Use 8, from the paper's
  equation, and say so in the runScript.
- **R2 — preconditioner inconsistency.** Patch site 2 (`getFvMatrixFields`) is
  easy to forget; miss it and `dRdWTPC` no longer matches the residual — on a
  stack whose standing blocker is already a singular ILU(0) factorization of
  exactly that matrix, an inconsistent PC would be a new confound
  indistinguishable from the old one. Patch both, diff-check both.
- **R3 — positivity of the implicit sink.** `fvm::Sp` with coefficient
  `betaMult·beta·ω` needs `betaMult > 0`. With f_d ∈ [0,1],
  `betaMult = (β−1)f_d + 1 > 0` for all β ≥ 0; the inversion should bound β in
  [0, 4] — upper bound theirs (entry §2), lower bound **ours by choice** since
  neither artifact states one, disclosed as such.
- **R4 — the CBFS adjoint blocker is not addressed.** Landing this patch does
  not converge the CBFS adjoint (`-9`/`-3`, singular ILU without pivoting, S1
  §4 / W4). The gate deliberately lives on the tutorial case. Any plan that
  prices "patch lands → CBFS inversion runs" is pricing through a wall this
  lab has already mapped.
- **R5 — parity scope.** This patch alone is **not** the rank-2 model — the
  QCR term (section 1, item 5) is a momentum-equation stress modification, a
  structurally different change (the linear `nut_`-based stress divergence in
  the solver's UEqn, not the ω equation), and is filed separately. Any score
  from a beta-destruction-only model must not be set beside 0.0455/0.0399 as
  like-for-like — the same discipline R6 imposed on the production hook, one
  level up.
- **R6 — f_d state-dependence enters the Jacobian.** The conditioned multiplier
  couples the ω destruction row to U (through `mag(grad U)`) and to nut. That
  is physics, not a bug — but it densifies `dRdW` coloring relative to the
  production hook and the first adjoint run should expect a longer coloring
  step than S1's 68.6 s hump figure.
- **R7 — sibling models drift.** `DAkOmegaSSTLM` and `DAkOmega` carry the same
  production-hook pattern and are untouched by this patch. Scope is
  `DAkOmegaSST` only; the others keep stock behavior, recorded here so nobody
  infers otherwise from the shared name.

---

## 6. Proposal obligations discharged

- `w3-beta-on-omega-destruction-model-patch`: progress_note added pointing at
  section 5 of this reading; gate unchanged; status stays `proposed`.
- `w3-qcr-constitutive-term-for-rank2-parity`: **new**, filed by this reading —
  the untrained QCR2000 term (c_r = 0.3) the rank-2 entry carries in addition
  to the beta hook, without which no duct-score comparison is like-for-like.

---

## Related

- `docs/papers/wu_zhang_zhang_2402.16355.pdf` / `.txt` — Artifact A.
- `docs/papers/wu_zhang_sst_qcrc_challenge_description.pdf` / `.txt` — Artifact B.
- `demo-output/website/dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md` — the
  production-hook capability record, the R6 restatement, and the FD protocol
  the gate reuses.
- `demo-output/website/closure_challenge_C2_error_decomposition.md` — the
  record section 1 corrects.
- `demo-output/website/campaign/W2_CFD_DRIVEN_TRAINING_READING.md`,
  `W2_POPE_1975_INTEGRITY_BASIS.md` — the reading series this joins; the
  feature set here is Pope's invariant basis again, λ1/λ2/λ5 being the 2D
  survivors the Pope reading already catalogued.
