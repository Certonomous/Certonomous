# The DAFoam method papers, read in full: what mesh, what decomposition, and which operator every published gradient verification actually covered

Date: 2026-08-04 (UTC). **Zero compute** — four fetch attempts, three papers
read in full, three W2 reading notes filed; no solver ran. This note is the
synthesis the upstream report's "why unnoticed" section was waiting on.

Reading notes behind every claim here (each with its own
claim/source/where-it-applies table):

- `demo-output/website/campaign/W2_DAFOAM_AIAAJ2020_VERIFICATION_READING.md`
- `demo-output/website/campaign/W2_DAFOAM_CAF2018_VERIFICATION_READING.md`
- `demo-output/website/campaign/W2_KENWAY_PAS2019_EFFECTIVE_ADJOINT_READING.md`

Artifacts held, PDF + extraction pairs in `docs/papers/`:

| Paper | Tier | File stem |
| --- | --- | --- |
| He, Mader, Martins, Maki, "DAFoam: An Open-Source Adjoint Framework for Multidisciplinary Design Optimization with OpenFOAM," AIAA Journal, DOI 10.2514/1.J058853 (preprint; header says "2019, in press") | READ IN FULL | `he_mader_martins_maki_aiaaj2020_dafoam_J058853` |
| He, Mader, Martins, Maki, "An aerodynamic design optimization framework using a discrete adjoint approach with OpenFOAM," Computers & Fluids 168 (2018) 285–303, DOI 10.1016/j.compfluid.2018.04.012 | READ IN FULL | `he_mader_martins_maki_caf2018_discrete_adjoint_openfoam` |
| Kenway, Mader, He, Martins, "Effective Adjoint Approaches for Computational Fluid Dynamics," Progress in Aerospace Sciences, DOI 10.1016/j.paerosci.2019.05.002 (preprint; header says "2019, in press") | READ IN FULL | `kenway_mader_he_martins_pas2019_effective_adjoint_100542` |

Availability record (charter §2: attempts are reported, never assumed):

- **He, Mader, Martins, Maki, AIAA SciTech 2019-1210** ("An Object-oriented
  Framework for Rapid Discrete Adjoint Development using OpenFOAM") — the
  conference precursor of the AIAA J paper, listed by the DAFoam
  publications page as a method paper. The mdolab preprint mirror returns
  403/Cloudflare for exactly this file (both `websites.umich.edu` and
  `public.websites.umich.edu` hosts, retried with a browser user agent);
  Semantic Scholar reports `openAccessPdf: CLOSED`; OpenAlex reports
  `oa_status: closed`, no repository fulltext. **Not read; nothing is
  asserted from it.**
- **DAFoam v4/v5 release paper or JOSS paper: none exists.** Checked this
  session: the DAFoam publications page lists no framework paper after 2020;
  the `mdolab/dafoam` README's citation section names exactly the two
  He et al. papers above, tied to no version; a JOSS search finds nothing;
  Zenodo records 15636000 (v4.0.2) and 20045081 (v5.0.0) are software
  deposits, not papers. **The v4/v5 rewrite the lab measured has no
  archival method paper at all** — the citation trail for the shipped
  matrix-free adjoint ends at papers describing other architectures. The
  v2.2 release note that shipped the Jacobian-free adjoint cites no paper
  for it either.

---

## 1. The verification-protocol answer, in one table

Every gradient-accuracy verification in the method-paper corpus:

| Paper | Adjoint operator verified | Case | Mesh class | Cells | Decomposition | Components checked | Reference | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C&F 2018 | **v1: explicit FD-coloring Jacobian** (assembled from parallel residual evaluations) | Ahmed body 25° | **snappyHexMesh** (refinement interfaces) | ~1M | **unstated** (≥2 KNL nodes implied by the paper's own memory statement — our inference) | 1 (dCD/du0) + 4 FFD | FD, step studies | −0.00049% best; avg <0.1%, worst 0.252% |
| AIAA J 2020 | **v1: explicit FD-coloring Jacobian** (Jacobian-free explicitly deferred to "future work") | ADODG Case 3 wing (+ Rotor 67 solid, flange Laplacian) | structured hex (Rotor 67: unstructured tri, solid solver) | 102 912 | **unstated**; "decompose"/"processor"/"scotch" absent from the paper | 1 shown per solver/model (dCD/dγ40%), 14 flow rows | brute-force FD, step studies | avg <0.1%, worst flow row 0.195% |
| PAS 2019 | **Jacobian-free reverse-AD (operator-overloading, dco/c++)** — the v2+/v5 architecture family | ADODG Case 3 wing | structured hex | 102 912 | **serial. np=1, stated twice, by design** | 8 (dCD/dγ) | full-code AD (Towara & Naumann) | 10-digit agreement |
| PAS 2019 | Jacobian-free source-transformation AD — **ADflow, not DAFoam** (manually assembled MPI differentiation) | CRM wing / wing-body-tail | multiblock structured / overset | 3.6M / 10.4M | block-based, fixed (48 / 96 cores) | 8 / 9 (dCD/dγ) | complex step | 11 / 6 digits |

Three facts fall straight out:

1. **No paper ever varies the decomposition of anything.** Decomposition is
   not an experimental axis anywhere in the corpus — not at fixed np, not
   across np. The two papers that verify DAFoam's v1 operator in (implied)
   parallel never state what the decomposition was.
2. **The operator our defect lives in — the matrix-free reverse-AD
   transpose-product path — has exactly one published accuracy measurement,
   and it is serial.** The survey states the reason in §5.1 ("running the
   cases using one CPU core allows us to isolate the impact of parallel
   communication") and confirms the gap in its conclusions.
3. **No verification anywhere in the corpus combines a
   refinement-interface mesh with a stated graph partitioning.** The one
   snappy-mesh verification (C&F 2018, Ahmed body — our defect's geometry
   family) is of the v1 explicit-FD-Jacobian operator at an unstated
   decomposition. The one verification of the matrix-free operator family is
   serial on a structured mesh.

## 2. Does anything contradict the going theory? Checked for, and no

The brief required this flagged as the headline if found. It was looked for
directly and is not there: **no paper verifies any adjoint on a
refinement-interface + graph-partitioned configuration**, and no paper
verifies the reverse-AD tape operator in parallel at all. The nearest
candidate — C&F 2018's snappy-mesh Ahmed verification, decomposition
unstated — is of the explicitly FD-assembled Jacobian, built from executions
of the true parallel residual with halo exchanges performed natively, an
architecture in which a tape-recording defect cannot exist. If those 2018
runs were scotch-partitioned, the result is *consistent* with our
measurements, which show the primal and the FD columns decomposition-robust
while only the v5 tape operator moves.

## 3. Why our decomposition defect went unnoticed upstream — now citable line by line

- **The liaison memo's "<0.1% at 1536 cores" was never one measurement.**
  AIAA J 2020's abstract joins two disjoint experiments with an "and": the
  1536 cores is Table 2, runtime-only, on a 10.1M-cell structured mesh; the
  <0.1% is Table 3, a ~103k-cell accuracy study at an unstated processor
  count. No accuracy number at any stated core count exists in that paper.
- **Both <0.1% figures attach to the v1 explicit-FD-Jacobian architecture**,
  which the 2020 paper pairs with "Implementing the Jacobian-free approach
  in DAFoam ... will be conducted in the future work." The 0.1% scale is
  the FD-partials error floor (Kenway §5.1/§6 says so directly), not a
  parallel-consistency scale.
- **The sharpest citable sentence for the upstream report** (Kenway, Mader,
  He, Martins, PAS 2019, Conclusions, READ IN FULL): *"We do not have
  scalability data for the Jacobian-free (operator overloading) and the
  full-code AD (operator overloading) options because we run the adjoint
  computation only in serial in the ADODG Case 3 (Sec. 5.1)."* Paired with
  §5.1's reason: *"running the cases using one CPU core allows us to
  isolate the impact of parallel communication on the performance."* The
  operator family v5's `calcJacTVecProduct` descends from entered the
  literature with its parallel behavior explicitly outside the data.
- **A single-decomposition test cannot see this defect even in principle**,
  and every parallel verification in the corpus is single-decomposition.
  This is the papers'-protocol form of what our own record already
  established measurement-side (`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`,
  "Why existing verification did not catch this"): a gradient consistent
  under the tested decomposition passes any test that never varies the
  partition.

## 4. Was the defect class acknowledged? Two quotes, neither a tape caveat

Fetched for exactly this question; both quoted in full in the reading notes:

1. **C&F 2018 §2.9** names interprocessor boundary-patch state updates as
   *"essential for accurately computing the adjoint derivative"* — for the
   v1 FD path, where they are handled by executing
   `U.correctBoundaryConditions()` per perturbation. The v5 tape must
   *record* that same coupling, and its interface-cell rows are where our
   cross-residual concentrates.
2. **PAS 2019 §A.4** acknowledges that *"some code structures remain a
   challenge to differentiate, including pointers and MPI calls"*, and that
   ADflow's parallel derivative correctness rests on manual assembly using
   properties *"that the AD code cannot, in general, safely assume."* That
   is a statement about AD-across-MPI as a hazard class, made about ADflow's
   development choices.

**Verdict for the upstream report's tone: it stays a bug report, not a
known-limitation report.** No paper states a halo-exchange tape caveat or a
partition-consistency assumption for DAFoam's operator-overloading path —
there is no sentence a maintainer could point to as prior disclosure. What
the quotes support is gentler and more useful: the hazard class was known to
the authors, the delicate region was named in their own 2018 paper, and the
published protocol simply never reached the configuration where the tape's
handling of that region is tested. Recommended framing: *the defect sits in
a subsystem whose verification the papers explicitly scoped out, in a region
their own earlier work flagged as accuracy-critical.*

## 5. Corrections our own record now owes (named, not silently fixed)

- `demo-output/website/dafoam/UPSTREAM_BUG_REPORT_decomposition_adjoint.md`
  header: "the toolchain's journal paper reports average adjoint derivative
  error under 0.1% at up to 1536 cores — this report, if filed, contradicts
  that published claim on a measured case." Wrong twice, per section 3: the
  two numbers were separate measurements, and both belong to the v1
  explicit-Jacobian architecture, not the matrix-free operator measured. The
  report does not contradict a published measurement; it fills a hole the
  survey's own conclusions declare. This *strengthens* the report — it no
  longer needs to argue against a peer-reviewed number.
- `demo-output/website/agenda/proposals/w4-three-discriminators-for-the-decomposition-dependent-adjoint.json`
  citation "DAFoam journal paper, adjoint derivative error under 0.1 percent
  at 1536 cores, tier SEARCH-EXCERPT via the liaison memo, abstract only" —
  upgradeable to READ IN FULL and correctable to the two-claims reading.
- `demo-output/website/dafoam/LIAISON_RESEARCH_adjoint_conditioning.md` —
  the origin of the abstract-tier citation; same correction applies.

The amendment work is filed as
`demo-output/website/agenda/proposals/w4-upstream-report-why-unnoticed-from-the-papers-own-protocols.json`
(this reading's charter-§6 obligation), which also carries the one cheap
compute arm this reading motivates: run the 2018 paper's own published check
(dCD/du0 against FD) on the A4 case at np=1 and np=4-scotch, so the upstream
report can state that the toolchain's own protocol passes at a fixed
decomposition and fails the moment the axis the papers never varied is
varied.

## Related

- `docs/charters/LITERATURE_CHARTER.md` — governing discipline; §6 trigger
  accounting is in each reading note.
- `demo-output/website/dafoam/VERIFICATION_A4_mechanism_supervisor_sweep.md`,
  `DISCRIMINATORS_A4_decomposition_mechanism.md`, `PROOF.md` §25.5 — the
  measurement record these papers were read against.
