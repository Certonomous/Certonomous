# SANAA-DIRECT — two-tier mesh standard, Rung 0 rewording, caps, freeze enforcement (2026-09-03, ~17:30Z)

## Sanaa's words, verbatim

> 1. Two-tier mesh standard — this resolves the R12 question. The 70° gate
> is our generation standard: every mesh the lab builds must meet it,
> unchanged. Committee grids are a different object: they exist for
> comparability with the workshop's own results, where every participant
> used the same grids. Ruling: committee grids are admissible for
> validation-against-workshop-data cases without meeting the 70° gate,
> under these conditions: (a) their measured quality (max
> non-orthogonality, skewness, the works) is reported on the certificate,
> not gated; (b) solver-side mitigations (non-orthogonal corrector counts,
> relaxation) are registered before running; (c) the numerical-uncertainty
> band still comes from the grid family; (d) the certificate names the
> grid as "workshop committee family, quality as published" in the
> what-was-checked section. A full certificate IS reachable this way — a
> certificate's honesty is disclosure and verification, not our internal
> birth standard. What committee grids can never do is certify our meshing
> capability — that stays on in-house grids under 70°. 2. Rung 0 wording
> amended: the gate is "import via UGRID with patch identity preserved;
> round-trip verified on cell count, patch names, and per-patch face
> counts; measured quality reported against the grid's own documentation."
> Plot3D is dropped (destroys patch identity). CGNS acquisition is
> deferred — bring it back as its own small registration if a target case
> only exists in CGNS.
>
> 3. Register wording: the mesh-import row certifies fidelity (faithful
> import + honest quality reporting), and says so; admissibility is the
> separate ruling above. 4. Rented instance: do not rent 16 vCPU for a
> serial converter — take the smallest instance that fits memory.
> Parallelizing the converter is approved only if conversion becomes
> recurring; one-off imports don't justify it.
>
> 5. Caps: the $25 blanket stands for all branches inside it; the snappy
> branch is approved at $40 hard cap — in-house meshing is the strategic
> capability behind the whole ladder, it's worth its price.
>
> 6. F5b (Aug 25): restate it to me in one paragraph with its options —
> it's been superseded by three weeks of rulings and I won't rule on a
> stale memory of it. [SANAA-DIRECT] Freeze enforcement: highest lab
> priority after the auto-stop patch. Wiring order: (1) the queue daemon
> refuses to grade any run whose comparator's sha does not match its
> frozen registration — enforcement at the choke point first, primitive is
> fine; (2) coverage measured and reported weekly (graders with reachable
> freeze coverage / total) until it reads 145/145; (3) then a planted
> violation proves the enforcer fires through the real path — the enforcer
> is itself an instrument and gets instrument-tested; (4) a one-line
> honest note goes into the lab record: freeze enforcement was documentary
> until [date]; every certificate issued before then relied on process
> discipline, not tooling. No re-grading of past results unless a specific
> comparator is shown to have moved — but the note is on the record.

## Context (chief's reading, not her words)

- Item 1 RESOLVES the R12 structural question by superseding it: two-tier
  standard — 70° stays the GENERATION gate for lab-built meshes;
  committee grids are admissible for validation-against-workshop cases
  under conditions (a)-(d); a full certificate IS reachable on committee
  grids; meshing-capability certification stays in-house-under-70°.
  Verification codifies in MESH_STANDARD/charter; cfd applies to Rungs 1-3.
- Item 2: Rung 0 gate reworded (UGRID, patch identity, cell/patch-name/
  per-patch-face round-trip, quality reported vs documentation); Plot3D
  dropped; CGNS deferred to its own small registration if ever needed.
- Item 5: snappy branch approved at $40 HARD cap (her explicit per-item
  read above the blanket).
- Item 6a: F5b restatement owed to her — one paragraph, current state +
  options, composed fresh from the records, not memory.
- Item 6b [SANAA-DIRECT]: freeze-enforcement wiring order 1-4 verbatim;
  highest lab priority after the auto-stop patch; the honest documentary-
  until-[date] note lands in the lab record; no retroactive re-grading
  absent a shown-moved comparator.
