# SUBOFF R1 — bare hull, zero incidence, total-drag parity (campaign prose)

**STATUS: DRAFT / UNFROZEN. No compute has run.**

DARPA SUBOFF (Groves/Huang/Chang 1989 DTRC/SHD-1298-01), bare-hull axisymmetric Model
5470. R1 is the cheapest defensible gate of the Navier-class Case-1 ladder: the
zero-incidence **total drag coefficient** `CT` at `Re_L = 1.2×10⁷`, graded ±10% against
a manifest reference, through a CONVERGING Roache triple.

- **Pre-registration (the authority):** `verification/campaign/SUBOFF_R1_PREREGISTRATION.md`
- **Grader:** `cases/navier_class/SUBOFF/grade_suboff.py` (rule-3 planted control,
  rule-4 completion, rule-5 triple via the shared instrument; refuse-not-degrade)
- **Reference:** `verification/runs/navier_class/SUBOFF/suboff_reference_ReL1p2e7.json`
  (manifest-only; CODE-VERIFIED/BOUNDED-AGREEMENT, **NOT experiment-validated** — no
  title-verified SUBOFF PDF on disk as of 2026-09-09)

Later rungs (named in the prereg §8): surface Cp vs Huang 1992 (R2), at-incidence
forces/moments → stability derivatives Z_w, M_w, neutral point (R3, the 3-D rung),
wall-resolved re-grade (R4).
