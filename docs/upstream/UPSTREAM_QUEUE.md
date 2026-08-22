# Upstream defect queue — everything drafted, nothing filed

**SUBMISSIONS ARE PARKED. Every entry below carries `NOT FILED` in its own
opening lines. No issue has been opened against any project, no maintainer has
been contacted, nothing has been posted or pushed. Filing any of them is
Sanaa's call alone** (`docs/LAB_STATE.md:451`, `:319`, `:66-67`).

This file was created by the **T10a-VF** lane on 2026-08-22 as the lab-level
index, because directive **H-3(b)** required the view-factor defect to "join
the upstream queue as candidate #4" and **no queue file existed**. The
candidates were, and still are, free-standing documents in their own campaign
trees; the only prior enumeration of them was prose in `docs/LAB_STATE.md`.
**Nothing was moved, renamed or edited to make this index** — every row points
at the document where it already lived.

## Numbering, unresolved — flagged for the supervisor, not decided here

`THERMAL_BUILDUP_DIRECTIVE.md:19`, `T_FAMILY_INDEX.md:75`,
`docs/LAB_STATE.md:50` and `docs/product/DC_CERTIFICATE_TEMPLATE.md:89` all
name the view-factor defect **candidate #4**. But `docs/LAB_STATE.md:319`
enumerates **four** DAFoam drafts already (`D-A/D-A2`, `D-B/D-B2`, `D-C`,
`D-E`), which would make the view-factor defect #5. The table below uses the
numbering the directive gave, and records the conflict rather than resolving
it. **If the DAFoam ILU note (`D-E`) counts as its own candidate, every number
below shifts by one.**

## The queue

| # | defect | target project | document | size | status | novelty search |
| ---: | --- | --- | --- | ---: | --- | --- |
| **1** | `mesh.warpDeriv` disagrees with a finite difference of the warp it differentiates, by up to 207 % and with the sign flipped, on two official tutorials | `mdolab/idwarp` (cross-linked `mdolab/dafoam`); intended as a comment on open issue `mdolab/idwarp#57` | `cases/dafoam/UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` | 49 K | **NOT FILED**; submission-ready, includes a verified four-line fix with before/after | recorded |
| **2** | the v5 matrix-free adjoint operator depends on the mesh decomposition; GMRES converges to 1e-6 on an operator that is not the transpose Jacobian, gradient error reaches 10 % at np=4 | `mdolab/dafoam` (v5, JacobianFree adjoint) | `cases/dafoam/UPSTREAM_BUG_REPORT_decomposition_adjoint.md` | 39 K | **NOT FILED** | recorded — 63 searches across 10 venues, all negative (`LIAISON_NOVELTY_SWEEP_decomposition_defect.md`) |
| **3** | the adjoint KSP silently discards `KSPSetFromOptions`, closing PETSc's standard escape hatch (class: diagnosability, not a wrong answer) | `mdolab/dafoam` | `cases/dafoam/DEFECT_CANDIDATE_ksp_options_override.md` | 12 K | **NOT FILED**; marked filing-ready | recorded |
| **4** | **`viewFactorsGen` view factors do not sum to 1 over a closed enclosure — up to +4.4 % on a concave patch, and the error does not shrink with mesh refinement.** Cause: the 2LI coincident-edge regularisation `r -> alpha*\|s_i\|` is exact only at `alpha = exp(-3/2) = 0.223130`, against a shipped default of `0.21` | **OpenFOAM (ESI / openfoam.com)**, `applications/utilities/preProcessing/viewFactorsGen`, v2606 build `_481094f-20260618` | `docs/upstream/T10a_viewFactorsGen_rowsum_NOT_FILED.md` | 12 K | **NOT FILED**; evidence complete, reproducer runs in ~15 core-seconds, **but NOT submission-ready** | **NONE — this is the blocker.** Candidates #1–#3 each carry one; this one has never been checked against the issue tracker, the forum or the mailing list |
| (—) | DAFoam's adjoint ASM sub-block ILU hits an exact zero pivot on wall-resolved separated cases, and the sanctioned PETSc remedy is unreachable | `mdolab/dafoam` | `cases/dafoam/ladder-b/B3/DEFECT_NOTE_ilu_zero_pivot.md` | 27 K | **NOT FILED** | — |

The unnumbered last row is the `D-E` item that creates the numbering conflict
above. It is listed so the index is complete.

## Candidate #4 — what a supervisor needs to know before deciding

* **The evidence is done.** Pre-registered before any compute
  (`docs/campaigns/T-family/T10aVF_PREREGISTRATION.md`, frozen at commit
  `7ed70d6b88922ee6b3f3aea88e0d833a269c7f9d`), 34 clean-room cases across five
  geometries and four resolutions, results and all gate failures in
  `docs/campaigns/T-family/T10aVF_RESULTS.md`, reproducer at
  `verification/runs/T-family/T10aVF_runs/reproducer/`.
* **The one blocker is novelty.** Nobody has checked whether this is already
  reported or already fixed upstream. Roughly the same effort as the
  `LIAISON_NOVELTY_SWEEP` that backs candidate #2.
* **It differs in kind from #1–#3.** Those are DAFoam/IDWarp — a research
  toolchain, a small maintainer group. This one is OpenFOAM ESI, a much larger
  and more conservative project, and the report touches a shipped default in a
  utility that has been in the tree for years. That argues for the novelty
  search being *more* thorough, not less.
* **No fix is offered.** Two dictionary-level workarounds are documented and
  both are qualified; no patched binary was built or tested.
