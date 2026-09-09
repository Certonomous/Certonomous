# DRIVAER R1 — notchback drag/lift parity vs DrivAerML (campaign prose)

**STATUS: DRAFT / UNFROZEN. No compute has run. BLOCKED-geometry (a lead) — no DrivAer
STL on disk yet.**

The DrivAer step of the vehicle-external-aero ladder the lab holds on the Ahmed body.
Geometry = Ford OCDA DrivAer **notchback**, static wheels, sealed cooling, detailed
underbody (DrivAerML baseline). R1 grades vehicle **Cd** (primary, ±10%) and **Cl**
(secondary, ±0.05 absolute) at `Re_L = 7.19×10⁶`, `U∞ = 38.889 m/s`, `Aref = 2.17 m²`,
against the **DrivAerML** scale-resolving CFD reference through a CONVERGING Roache
triple.

- **Pre-registration (the authority):** `verification/campaign/DRIVAER_R1_PREREGISTRATION.md`
- **Grader:** `cases/navier_class/DRIVAER/grade_drivaer.py` (rule-3 planted control,
  rule-4 completion, rule-5 triple, refuse-not-degrade)
- **Reference:** `verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json`
  (Ashton et al. 2024, arXiv:2408.11969v2, DrivAerML; **title-page verified 2026-09-09**;
  tier **CODE-VERIFIED**, NOT experiment-validated)

Geometry lead and meshing (snappyHexMesh on the STL, motorBike template) are a
retrieval/meshing lane. Later rungs named in the prereg §8: wall-resolved (R2), AutoCFD
experimental parity (R3), moving ground + rotating wheels (R4).
