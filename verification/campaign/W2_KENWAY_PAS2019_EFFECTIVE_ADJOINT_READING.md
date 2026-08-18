# W2 reading — Kenway, Mader, He & Martins 2019, the effective-adjoint survey: the only published verification of DAFoam's matrix-free operator was serial, on purpose

Date: 2026-08-04 (UTC). **Zero compute** — paper fetched and read; no solver
ran. Read for exactly one question: how the Jacobian-free (matrix-free,
reverse-AD) adjoint — the ancestor of DAFoam v5's `calcJacTVecProduct` path,
where the lab's decomposition defect lives — was verified in print.

---

## 0. The artifact

Kenway, G. K. W., Mader, C. A., He, P., and Martins, J. R. R. A., "Effective
Adjoint Approaches for Computational Fluid Dynamics," Progress in Aerospace
Sciences, DOI `10.1016/j.paerosci.2019.05.002` (citation read off the
preprint header, which says "2019 (In press)"; the volume/paper citation
Vol. 110, 100542 is from the journal's page via search, not this artifact).
**Tier: READ IN FULL** — mdolab preprint
(`https://websites.umich.edu/~mdolaboratory/pdf/Kenway2019a.pdf`, fetched
this session), held at
`docs/papers/kenway_mader_he_martins_pas2019_effective_adjoint_100542.pdf`
with text extraction alongside. Section/table numbers are the preprint's.

Standing of this paper for our question: it is where the **Jacobian-free
adjoint with reverse-mode AD transpose matrix-vector products** is described
and benchmarked for DAFoam — the DAFoam project's own publications list
names no other method paper for it, and the v2.2 release note that shipped
the Jacobian-free adjoint cites no paper at all (both checked this session).
This survey is therefore the entire published verification record of the
operator family our defect lives in.

---

## 1. The headline: serial by design

§5.1 (ADODG Case 3, the only case in the survey where DAFoam's Jacobian-free
adjoint runs at all), verbatim:

> "For this case, we run all the simulations on Stampede 2 by using one CPU
> core on one Skylake node."

and the stated reason:

> "Moreover, running the cases using one CPU core allows us to isolate the
> impact of parallel communication on the performance."

and §6 (Conclusions), verbatim:

> "We do not have scalability data for the Jacobian-free (operator
> overloading) and the full-code AD (operator overloading) options because
> we run the adjoint computation only in serial in the ADODG Case 3
> (Sec. 5.1)."

The DAFoam Jacobian-free accuracy result — Table 4, dCD/dγ at eight spanwise
stations matching a full-code-AD reference (Towara & Naumann's
`adjointSimpleShapeCheckpointingFoam`) to **10 significant digits** — is a
**np=1** result on a **102 912-cell coarse structured mesh** (y+ 1.2). The
reverse tape's inter-processor recording — the subsystem our cross-residual
instrument convicts — was never executed in any accuracy measurement this
survey publishes, and the authors say so themselves in the conclusions.

The parallel Jacobian-free numbers in the survey belong to **ADflow**, a
different code in every relevant respect: Fortran, multiblock structured and
overset meshes, source-code-transformation AD (Tapenade), and — decisive for
our question — **hand-assembled parallel differentiation** (§A.4): the
differentiated subroutines are manually composed *"by using specific
properties of the code structure that the AD code cannot, in general, safely
assume"*, precisely because *"even with the most advanced AD tools currently
available, some code structures remain a challenge to differentiate,
including pointers and MPI calls."* ADflow's parallel accuracy is then
genuinely verified in parallel: Case 4 (CRM wing, 3 604 480 cells, 48 cores)
matches complex step to 11 digits (Table 6); Case 5 (wing-body-tail overset,
10 358 373 cells, 96 cores) to 6 digits (Table 9). Block-structured
partitioning throughout; no graph partitioner, no refinement interfaces, and
decomposition is never a varied axis there either.

## 2. Two sentences worth carrying whole

- The MPI acknowledgment (§A.4, quoted above): the survey's own authors state
  that MPI calls are what AD tools cannot in general safely differentiate,
  and that ADflow's parallel derivative correctness rests on manual assembly
  under code-specific assumptions. This is the corpus's honest statement of
  where the hazard is. DAFoam's operator-overloading path gets no equivalent
  discussion — its parallel behavior is simply outside the survey's data.
- §5.1, on why the machine-precision agreement holds, verbatim: *"We achieve
  machine-precision accurate adjoint derivatives because we do not make any
  approximations (e.g., ignore and simplify terms or use the frozen
  turbulence assumption) in our adjoint formulations. Moreover, we use AD to
  accurately compute all the partial derivatives. Finally, our adjoint code
  is bug-free."* — a correctness-by-construction argument, offered in the
  serial section, with no parallel counterpart for the operator-overloading
  code.

## 3. Smaller facts the record should hold

- The survey names DAFoam's operator-overloading tool at the time as
  **dco/c++** (§4.4: "SU2 uses the CoDiPack [152] ... whereas DAFoam,
  piggySimpleFoam, and reverseAccSimpleFoam use dco/c++ [151]"). The v5
  container the lab measured records its global tape with **CoDiPack**
  (`initializeGlobalADTape4dRdWT`, read from installed source —
  `DISCRIMINATORS_A4_decomposition_mechanism.md`, INTERNAL). The shipped AD
  machinery is therefore not even the same tool the survey benchmarked —
  one more degree of separation between the published verification and the
  operator we measured.
- The survey's "1536 CPU cores" (abstract and conclusions) is an ADflow
  Case 4 scaling datum (32 nodes at 48 cores/node, Jacobian-free parallel
  efficiency 30.1%, §5.2) — runtime, ADflow, not DAFoam, not accuracy.
- FD Jacobian accuracy across both codes: "average error is around 0.1%"
  (§5.1) / "an average error of O(0.1)%" (§6) — this is where the 0.1%
  figure of the DAFoam papers natively lives: it is the *FD-partials* error
  scale, not a parallel-consistency scale.
- Oddity recorded, not resolved: this survey's Case 3 mesh (102 912 cells,
  y+ 1.2) and the AIAA J 2020 paper's accuracy mesh (102 912 cells, y+ 32.6
  with wall functions) share a cell count but not a y+; whether they are the
  same mesh cannot be read off either artifact.

---

## 4. Claim / source / where-it-applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| The only published accuracy verification of DAFoam's Jacobian-free reverse-AD operator is serial (np=1), on a 102 912-cell structured mesh, 8 twist components, 10-digit agreement with a full-code-AD reference. | §5.1, Table 4, §6, READ IN FULL (preprint). | **The sharpest citable answer to "why unnoticed":** the operator family our defect lives in has zero published parallel accuracy measurements. Verbatim quotes in section 1. | Any reading in which "the toolchain's paper reports <0.1% at 1536 cores" refers to this operator — it does not, on either number. |
| Parallel accuracy at 48/96 cores (11 and 6 digits vs complex step) is ADflow: Tapenade source transformation with manually assembled MPI differentiation, block-structured/overset meshes. | §5.2–5.3, Tables 6 and 9, §A.4, READ IN FULL. | Shows genuinely parallel adjoint verification existed in the group — for the code whose parallel derivative path is hand-assembled and can be reasoned about. | Transferring that assurance to DAFoam's operator-overloading tape. The survey itself keeps the two separate; so must we. |
| "...some code structures remain a challenge to differentiate, including pointers and MPI calls." with parallel correctness resting on assembly "using specific properties of the code structure that the AD code cannot, in general, safely assume." | §A.4, READ IN FULL. | The upstream report's tone paragraph: the hazard class (AD across MPI) is acknowledged in the group's own survey. Cite as the survey's general statement about AD tooling. | Reading it as a DAFoam-specific caveat or a known-limitation admission for the v5 tape — it is about ADflow's development choices; DAFoam's parallel tape gets no caveat anywhere. "Bug" stands. |
| At the survey's date, DAFoam's operator-overloading tool was dco/c++; the lab's measured v5 uses CoDiPack. | §4.4 READ IN FULL; v5 tool from installed source, INTERNAL (`DISCRIMINATORS_A4_decomposition_mechanism.md`). | Upstream report accuracy: the shipped tape is not the benchmarked tape. | Claiming the tool swap caused the defect — nothing read this session speaks to that. |

---

## 5. Charter section 6 — which trigger fired

- **Trigger 3 (paper disagrees with one of our results): FIRED in the
  useful direction.** No published number here contradicts our measurement;
  instead the paper's own conclusions state the absence of parallel data for
  the operator we measured — which converts our upstream report's framing
  from "contradicts a published claim" to "fills a hole the survey itself
  declares". Proposal obligation discharged via
  `w4-upstream-report-why-unnoticed-from-the-papers-own-protocols` (filed
  with the synthesis note).
- Triggers 1, 2, 4: checked, did not fire (the survey's cases are ADflow's
  or already covered by the other readings; no thresholds; no zero-compute
  limit case).

## Related

- `docs/papers/kenway_mader_he_martins_pas2019_effective_adjoint_100542.pdf` / `.txt`
- `demo-output/website/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` — synthesis.
- `demo-output/website/dafoam/UPSTREAM_BUG_REPORT_decomposition_adjoint.md` —
  the report whose evidence standard this reading was fetched to serve.
