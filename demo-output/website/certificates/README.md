# Certificate redesign — old vs new (B-52), for sign-off

Two renders of the SAME B-52 record:

- `b52-certificate-current.pdf` — the current default (`build_certificate`).
- `b52-certificate-redesign.pdf` — the redesign proposal (`build_certificate_v2`).

**The redesign is NOT the default.** `build_certificate` is untouched; the new
layout is an additive `build_certificate_v2` and becomes default only on
sign-off.

## What changed in the redesign
- Serif/sans pairing; generous margins.
- Masthead carries a human **Certificate No. C-2026-NNNN** (deterministic from
  the seal); the mission slug is demoted to the provenance footer, never the title.
- Subject block leads with the geometry **display name** ("B-52
  Stratofortress-class airframe"); the filename is small metadata.
- Result block: value ± 95% CI with a **fidelity chip** (SOLVER-BACKED /
  CONCEPTUAL MODEL / VALIDATED).
- Complete **three-channel** V&V-20 uncertainty table.
- Provenance footer: SHA-256 seal (truncated + full), mission id small,
  "Reproducible from the sealed evidence bundle".

## Substitution note
Requested mission **M-C13431539C15** is not in this repo's records, and no B-52
geometry-study mission is persisted here. The record is built from the project's
DOCUMENTED real B-52 solve (193,880 cells, Cd 0.0471, ~8 core-min, TREND ONLY).
Regenerate against a live B-52 mission when one exists on this branch.
