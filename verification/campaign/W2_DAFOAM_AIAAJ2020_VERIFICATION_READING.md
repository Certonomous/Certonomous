# W2 reading — He, Mader, Martins & Maki, the DAFoam AIAA Journal paper: what "<0.1% at 1536 cores" actually measured

Date: 2026-08-04 (UTC). **Zero compute** — paper fetched and read; no solver
ran. Read for exactly one question: how is the parallel adjoint claimed to be
derived and verified, and does the verification protocol explain why the lab's
decomposition defect (`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`) went
unnoticed upstream.

---

## 0. The artifact

He, P., Mader, C. A., Martins, J. R. R. A., and Maki, K. J., "DAFoam: An
Open-Source Adjoint Framework for Multidisciplinary Design Optimization with
OpenFOAM," AIAA Journal, DOI `10.2514/1.J058853`. **Tier: READ IN FULL** — the
mdolab preprint (`https://websites.umich.edu/~mdolaboratory/pdf/He2020b.pdf`,
fetched this session), held at
`docs/papers/he_mader_martins_maki_aiaaj2020_dafoam_J058853.pdf` with text
extraction alongside. The preprint's own header says "AIAA Journal, 2019 (in
press)" and warns the published article may differ; the volume/page citation
the project README gives — AIAA Journal 58:1304–1319, 2020 — is from the
`mdolab/dafoam` README (fetched this session), not read off this artifact.
Section and table numbers below are the preprint's.

This is the paper the liaison memo cited at abstract tier ("average adjoint
derivative error under 0.1% at up to 1536 cores",
`LIAISON_RESEARCH_adjoint_conditioning.md`, carried into
`UPSTREAM_BUG_REPORT_decomposition_adjoint.md` and the W4 proposal's citation
list as SEARCH-EXCERPT).

---

## 1. The headline, filed first: the 0.1% and the 1536 cores were never one measurement

The abstract sentence is: *"We achieve excellent adjoint speed and
scalability, with up to 10 million cells and 1536 CPU cores, and an average
error in the adjoint derivatives of less than 0.1%."* Two claims, one "and".
In the body they are two disjoint experiments:

- **Speed/scalability (§2.4.1, Table 2):** ADODG Case 3 wing, fine
  **structured** mesh, 10 141 696 cells, 192 → 1536 cores on Stampede 2
  Skylake. The table contains **runtimes only** (flow 810→156 s, adjoint
  1809→262 s, parallel efficiencies). **No derivative accuracy is measured at
  any of these core counts.**
- **Accuracy (§2.4.2, Table 3):** ADODG Case 3 with a **coarse mesh of
  102 912 cells** (average y+ 32.6, wall functions), plus Rotor 67
  (unstructured triangular, 91 475 cells, solid solver) and a flange (5712
  cells, Laplacian solver). The paper never states the core count or the
  decomposition used for these accuracy runs — the words "decompose",
  "processor" and "scotch" do not appear anywhere in the paper (grep over the
  full extraction, this session).

So "<0.1% at 1536 cores" — the reading our own upstream report currently
carries — is a conflation the abstract invites but the body does not support.
The 0.1% was measured on a ~103k-cell case at an unstated (and probably
small or serial) processor count; the 1536 cores measured wall-clock only.

## 2. The second headline: this paper verifies a different adjoint than the one our defect lives in

§2.2: *"DAFoam uses the FD Jacobian approach [33] to implement the discrete
adjoint, i.e., the partial derivatives are computed using the
coloring-accelerated finite-difference method"* — the transpose state Jacobian
is **explicitly assembled from finite differences of the residual and stored
in PETSc**, then handed to GMRES. The Jacobian-free reverse-AD operator — the
architecture of v2+ and of v5's `calcJacTVecProduct` global tape, where the
lab localized its defect — is explicitly **not in this paper**: §2.4.1 closes
with *"Implementing the Jacobian-free approach in DAFoam and optimizing its
performance will be conducted in the future work."*

An FD-assembled Jacobian is built column-by-column from evaluations of the
actual parallel residual (halo exchanges included, executed, not
tape-recorded), so the defect class we measured — a reverse tape that records
inter-processor coupling wrongly — cannot exist in the architecture this
paper verifies. The <0.1% figure is true of v1's operator and carries no
information about v5's.

---

## 3. Claim / source / where-it-applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| Abstract joins two disjoint measurements: scalability "up to 10 million cells and 1536 CPU cores" and "an average error in the adjoint derivatives of less than 0.1%". | Abstract; Table 2 vs Table 3, READ IN FULL (preprint). | Correcting our upstream report's framing: the paper publishes **no** accuracy number at 1536 cores, or at any stated core count. | Any sentence of ours that cites "<0.1% at 1536 cores" as one published measurement — that sentence must be retired. |
| Accuracy protocol: brute-force FD totals as reference, step-size sweeps 1e-5..1e-2 (totals) and 1e-9..1e-4 (partials), most common steps 1e-3 and 1e-7; one representative component dCD/dγ at 40% span shown per solver/model; 14 flow-solver rows across M = 0.15/0.5/0.7; average error <0.1%, worst flow row 0.195% (kOmegaSST, M 0.5). | §2.4.2, Table 3, READ IN FULL. | What "verified" meant upstream at v1: single-component FD agreement on one structured-mesh case family, fixed (unstated) decomposition. | Multi-decomposition invariance — no experiment in the paper varies the decomposition of anything, at fixed np or otherwise. |
| Adjoint linear tolerance 1e-6 was deemed sufficient because *"the adjoint total derivatives are accurate only up to four significant digits (Table 3) due to the errors in the finite-difference-based partial derivative computation."* | §2.4.1, READ IN FULL. | The v1 error floor is the FD partials, not the linear solve — consistent with our own finding that tolerance does not move a converged-wrong-operator answer. | v5's Jacobian-free path, whose partials are AD-exact; its error floor is whatever the tape records. |
| The verified meshes are: ADODG3 structured hex (accuracy + scaling), Rotor 67 unstructured triangular (solid), flange (Laplacian). snappyHexMesh appears only in the CRM **optimization demo** (872 404 cells, §3.2) with no FD gradient verification. | §2.4, §3.2, READ IN FULL. | The verification corpus of this paper contains **no refinement-interface mesh**. | Claiming the paper verified nothing unstructured — Rotor 67 is unstructured, but it is the solid solver, one DV, and not a flow adjoint. |
| Memory: explicit [∂R/∂w]^T + preconditioner storage cost 1146.2 GB against 73.2 GB for the flow at 10.1M cells — the stated motivation for moving to Jacobian-free later. | §2.4.1, READ IN FULL. | Why v2+ switched architectures: memory, not accuracy. The successor operator was adopted for cost reasons and (per the Kenway reading) never re-verified in parallel in print. | — |

---

## 4. Charter section 6 — which trigger fired

- **Trigger 3 (paper disagrees with one of our results): FIRED, and the
  disagreement dissolves under reading.** Our measured 8.95% at np=4-scotch
  does not contradict any measurement this paper actually made: the <0.1% was
  (a) a different adjoint architecture (explicit FD Jacobian, v1) and (b) at
  an unstated decomposition on a structured mesh. What our measurement
  contradicts is only the *abstract-tier conflation* of the two claims. The
  proposal this obligates —
  `w4-upstream-report-why-unnoticed-from-the-papers-own-protocols` — is filed
  by the synthesis note this reading feeds
  (`demo-output/website/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`).
- Triggers 1, 2, 4: checked, did not fire on this paper alone (the buildable
  verification number lives in the 2018 paper's reading; no thresholds; no
  zero-compute limit case).

## Related

- `docs/papers/he_mader_martins_maki_aiaaj2020_dafoam_J058853.pdf` / `.txt`
- `demo-output/website/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` — the
  synthesis across all four readings, and the corrections list.
- `demo-output/website/dafoam/UPSTREAM_BUG_REPORT_decomposition_adjoint.md` —
  the report whose "why unnoticed" section this reading arms.
