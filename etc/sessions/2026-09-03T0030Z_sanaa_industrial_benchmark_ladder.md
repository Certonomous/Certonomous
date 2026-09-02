# SANAA-DIRECT — industrial benchmark ladder, standing order for cfd (2026-09-03, ~00:30Z)

## Sanaa's words, verbatim

> tasks for the cfd team : [SANAA-DIRECT] Industrial benchmark ladder —
> standing order for the CFD team. Purpose: move the register from
> section-class to industry-class cases. One held DPW-class result in our
> certificate format outweighs ten toy cases; that is the target, not
> volume.
>
> Rung 0 — Mesh import is the enabling capability. Before any case: build
> and verify the committee-grid import lane (CGNS/UGRID/Plot3D → our solver
> format). Gate: import a published grid, verify cell count, patch names,
> y+ and quality against the grid's own documentation, and re-export
> losslessly. Every case below uses this lane; a case never starts until
> its grids pass import verification. This flips the register's "mesh
> import" line to Held on its own.
>
> Rung 1 — ONERA M6 (already ordered, option 1). Public grid family,
> transonic, AGARD AR-138 pressure taps. Feasibility-first: coarse-grid
> probe with registered predictions before the family runs. Deliverable:
> surface pressures at the published sections against tunnel data,
> grid-triple band from the family, full certificate with
> what-was-not-checked. This is the compressible-3D validation line.
>
> Rung 2 — NASA CRM, Drag Prediction Workshop configuration. The industry
> yardstick: full wing-body transport. Use the workshop's committee grid
> family — the grid-triple prerequisite comes free. Sequence: (a) single
> cruise point (the workshop's design condition), drag and moment against
> the workshop's data envelope — we grade against the scatter band of
> participants, honestly stated; (b) the drag-rise sweep only after (a) is
> held. Budget: registered per-solve estimate before launch; expect tens of
> core-hours per fine-grid solve; rent the node size to the grid, never
> crop the grid to the node. Freeze criteria before the first solve, as
> always.
>
> Rung 3 — High-Lift Prediction Workshop case, only after Rung 2 is held.
> Flaps and slats, separation-dominated, the hardest respected benchmark.
> Registered expectation must be honest about known RANS limits here; a
> characterized miss with the failure classified is an acceptable outcome
> and publishable in our format. Do not schedule before CRM is held.
>
> Parked until their verticals open: DrivAer (automotive), Rotor 37
> (turbomachinery, behind rotating-frame capability). Listed on the
> register as Planned with this ladder as the sequence; no compute until
> unparked.
>
> Rules that do not bend at scale: feasibility probe before family;
> predictions registered before runs; criteria frozen before compute; grid
> family from the committee where it exists, and where only two levels are
> affordable the registered-order fallback is used and disclosed;
> conservation and np-invariance checks on every gated solve; certificates
> carry the reference, the tolerance, the band, and the not-checked list.
> Budget caps per rung set by me on the cost estimates you return — send
> the Rung 0 and Rung 1 estimates first.

## Context (chief's reading, not her words)

- Standing order, cfd territory. The existing M6 work (option 1, and the
  frozen option-3 pyHyp probe blocked on the docker socket) folds into
  Rung 1. Rung 0 gates every case. Rung 2 after Rung 1; Rung 3 only after
  Rung 2 is held; DrivAer/Rotor 37 register as Planned, no compute.
- "Rent the node size to the grid" authorizes proposing separate rented
  instances for fine-grid DPW solves — proposals costed per rule 12; her
  caps come back per rung. First deliverable to her: Rung 0 + Rung 1 cost
  estimates.
- "Publishable in our format" changes nothing about rule 7: SUBMISSIONS
  PARKED; prepared artifacts stay on the box.
