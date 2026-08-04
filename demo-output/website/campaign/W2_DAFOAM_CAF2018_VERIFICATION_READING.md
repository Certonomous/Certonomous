# W2 reading — He, Mader, Martins & Maki 2018, the Computers & Fluids paper: the one snappy-mesh gradient verification in the corpus, and the interprocessor sentence

Date: 2026-08-04 (UTC). **Zero compute** — paper fetched and read; no solver
ran. Read for exactly one question: verification protocol of the parallel
adjoint, against the lab's decomposition defect
(`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`).

---

## 0. The artifact

He, P., Mader, C. A., Martins, J. R. R. A., and Maki, K. J., "An aerodynamic
design optimization framework using a discrete adjoint approach with
OpenFOAM," Computers & Fluids, 168 (2018) 285–303, DOI
`10.1016/j.compfluid.2018.04.012` (citation read off the preprint header).
**Tier: READ IN FULL** — mdolab preprint
(`https://websites.umich.edu/~mdolaboratory/pdf/He2018b.pdf`, fetched this
session), held at
`docs/papers/he_mader_martins_maki_caf2018_discrete_adjoint_openfoam.pdf`
with text extraction alongside. Preprint warns the published article may
differ; section/table numbers below are the preprint's. This is DAFoam v1's
foundation paper and one of the two citations the `mdolab/dafoam` README asks
users to cite. Stack verified on: OpenFOAM 2.4.x, PETSc 2.7.6 (§3.1).

---

## 1. What was verified, on what mesh, against what

The verification case is **an Ahmed body** — the same geometry family as our
A4 defect case — 25° ramp, half-body, Re 1.4e6, on an **unstructured snappy
hexahedral mesh of ~1 million cells** (y+ 60, wall functions), generated with
snappyHexMesh (§3.1). This is the **only refinement-interface-class mesh that
ever carries a gradient-accuracy check anywhere in the four method papers.**

- Table 4: dCD/du0 (far-field velocity DV), adjoint vs FD reference
  (central difference, step 1e-5, with step-size studies): best partials step
  1e-8 gives **−0.00049%**; the partials-step sweep 1e-5..1e-10 spans
  26.4% → −0.05%.
- Table 5: dCD/dx for **four FFD points on the ramp**: errors −0.031%,
  −0.006%, 0.019%, 0.252%; *"Overall, the average error is less than 0.1%."*
- Adjoint architecture verified: the same explicit coloring-accelerated **FD
  Jacobian** as the 2020 paper — [∂R/∂w]^T assembled from perturbed parallel
  residual evaluations and stored in PETSc (§2.5–2.9). Not the reverse-AD
  tape of v2+/v5.

**Decomposition: never stated.** "scotch" appears nowhere; no
decomposeParDict, no method, no rank count for the accuracy runs. What the
paper does state (§3.1, memory): *"we require at least 2 and 10 nodes for the
1- and 10-million-cell cases"* — so the verified 1M-cell adjoint could not
have run on one KNL node, and the inference (ours, not theirs) is that the
Table 4/5 verification was a parallel run at an unstated decomposition.

## 2. The interprocessor sentence — the closest thing to an acknowledgment in the whole corpus

§2.9, on assembling the FD Jacobian, verbatim:

> "Note that the boundary conditions must be updated for each state-variable
> perturbation. For example, when we perturb the velocity of a cell
> immediately next to an interprocessor boundary patch, we need to
> interpolate the perturbed velocity onto this boundary patch. This is done
> by calling U.correctBoundaryConditions() in OpenFOAM. We need similar
> updates for all flow variables. Note that updating the boundary condition
> is essential for accurately computing the adjoint derivative."

That is the authors naming, in 2018, the exact coupling — state updates
across interprocessor boundary patches inside the derivative path — as the
thing that must be handled or the adjoint derivative is wrong. In v1 it is
handled by *executing* `correctBoundaryConditions()` per perturbation; in
v5's Jacobian-free path the same coupling must be *recorded on the reverse
tape* (`initializeGlobalADTape4dRdWT` registers state →
`updateStateBoundaryConditions` → `calcResiduals`), and the lab's
cross-residual evidence localizes the defect to interface-cell rows of
exactly that recorded coupling. **It is not a caveat about the tape** — the
tape did not exist yet — so it does not convert our report from "bug" to
"known limitation". It does set the tone: the defect sits in a region the
authors themselves flagged as essential-and-delicate, handled correctly in
the architecture they verified and differently in the one they did not.

## 3. Does the snappy-mesh verification contradict our going theory?

**No, and the reason is the operator, not the mesh.** Our theory (A4
mechanism sweep, commit 8e0a08bc) is that v5's *recorded reverse tape*
mis-handles inter-processor coupling on jagged partition boundaries. The 2018
verification passed <0.1% on a snappy Ahmed mesh — possibly under a graph
partitioner, unstated — but the operator it verified is an FD-assembled
matrix built from evaluations of the true parallel residual, halo exchanges
executed natively. A tape-recording defect has no analogue there. If anything
the 2018 result is *consistent* with our measurements: our own FD columns and
primal solves are decomposition-invariant; only the v5 tape operator moves.
Flag checked, no contradiction to soften or headline.

---

## 4. Claim / source / where-it-applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| The only refinement-interface-mesh gradient verification in the DAFoam method corpus: Ahmed 25°, ~1M-cell snappyHexMesh, dCD/du0 to −0.00049% and 4 FFD components averaging <0.1% against FD. | Tables 4–5, §3.1, READ IN FULL (preprint). | The upstream report's "why unnoticed": mesh class alone did not hide the defect — the v1 operator on this mesh class verified clean. The discriminating axis is the operator (FD-assembled vs tape) and the decomposition, which this paper never varies or names. | Any claim that the papers "never touched a snappy mesh" — they did, once, for v1. Precision here protects the report's credibility. |
| Verification decomposition and rank count: unstated; ≥2 KNL nodes implied for the 1M adjoint by the paper's own memory statement. | §3.1, READ IN FULL; the ≥2-node inference is ours. | Recording the omission: single-decomposition verification, identity unstated. A wrong-but-consistent operator would pass it; the paper's protocol cannot see a decomposition dependence even in principle, because decomposition is never a variable. | Claiming they verified serially — the memory figure argues otherwise; claiming they used scotch — nowhere stated. |
| The interprocessor boundary-patch update is "essential for accurately computing the adjoint derivative" (full quote in section 2 above). | §2.9, READ IN FULL. | Tone of the upstream report: the defect region was known-delicate; v1 handled it by executing the update per perturbation. | Reading it as a v2+/tape caveat — the Jacobian-free path postdates this paper. "Bug", not "known limitation", stands. |
| Scaling claims (10M cells, 1024 cores, Fig. 7/Table 2) are runtime and coloring-count measurements; the accuracy tables are a separate 1M-cell experiment. | §3.1, READ IN FULL. | Same conflation-hygiene as the 2020 paper: cores-numbers and accuracy-numbers never co-occur in one measurement. | — |

---

## 5. Charter section 6 — which trigger fired

- **Trigger 1 (a number on a case we can build): FIRED.** dCD/du0 =
  0.03042447 on a snappy Ahmed mesh is the papers' own protocol on our
  defect geometry family, and a far-field-velocity DV variant of it runs on
  the lab's existing 2,777-cell A4 case for a few core-minutes. Folded into
  the filed proposal
  `w4-upstream-report-why-unnoticed-from-the-papers-own-protocols` as its
  one cheap compute arm: run the papers' own published check across np=1 /
  np=4-scotch and record that it passes at the decomposition the protocol
  fixes and fails the moment the never-varied axis is varied.
- Trigger 3: checked — no disagreement; section 3 above records why the
  snappy result does not contradict the going theory.
- Triggers 2, 4: checked, did not fire (no thresholds to extract; no
  zero-compute limit case beyond what section 3 already states).

## Related

- `docs/papers/he_mader_martins_maki_caf2018_discrete_adjoint_openfoam.pdf` / `.txt`
- `demo-output/website/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` — synthesis.
- `demo-output/website/dafoam/DISCRIMINATORS_A4_decomposition_mechanism.md` —
  the interface-cell localization the §2.9 quote speaks to.
