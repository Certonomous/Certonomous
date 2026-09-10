# DrivAerML geometry retrieval — provenance record (DRIVAER / Case 7)

Status: INBOUND retrieval complete. This is a paper-fetch-class inbound (nothing
leaves the box); NOT a rule-7 send and NOT a rule-8 export.

This record is the durable handoff artifact for the DRIVAER_R1 geometry blocker.
It is NOT the pre-registration and it does NOT freeze the gate: which run pins the
baseline reference Cd/Cl is a freeze-time decision reserved to the supervisor
(check-4, HELD behind mesh+smoke and M6).

## Source

| Field | Value |
|---|---|
| Dataset | `neashton/drivaerml` on HuggingFace (dataset repo) |
| Title (dataset card) | DrivAerML: High-Fidelity Computational Fluid Dynamics Dataset for Road-Car External Aerodynamics |
| Paper | Ashton et al. 2024, arXiv:2408.11969 (v2 title-verified upstream by supervisor) |
| License | CC-BY-SA-4.0 (`cardData.license`, `LICENSE.txt` = "Attribution-ShareAlike 4.0 International") |
| Gated / private | no / no (`gated:false`, `private:false`) |
| Revision (commit sha) fetched | `7a5c0948ce27be709b1116a3a190f806e7a8f79f` |
| CFD solver used upstream | OpenFOAM v2212 + UpstreamCFD mods (scale-resolving) |
| Retrieval mechanism | HTTPS via `curl -L` against `resolve/<sha>/<path>` (Xet CDN redirect); no auth |
| Date fetched (UTC) | 2026-09-10T02:45Z |

## What the dataset is

500 parametrically morphed variants of the DrivAer notchback (`run_1`..`run_500`;
484 present, 16 held back). `geo_parameters_all.csv` holds the per-run morph
deltas from the nominal notchback. There is **no un-morphed nominal geometry** in
the top-level per-run tree of this revision: `run_0` (the AutoCFD4 workshop
nominal baseline) exists only under `openfoam_meshes/run_0/` and is absent from
`force_mom_all.csv`. Consequently the gate must compare our OpenFOAM solve of a
chosen morph against **that same morph's** DrivAerML coefficients (a matched
STL + force pair).

## Baseline candidate selected for retrieval: run_466

run_466 is the run with the **smallest morph-delta L2 norm** (‖delta‖=114.96)
among all 484 available runs — i.e. the geometry closest to the nominal notchback
that is actually downloadable with matched force data. This is a *candidate*; the
supervisor pins the final reference run at freeze. Any other run is one 142 MB
curl away.

Dataset coefficient population (484 runs, `force_mom_all.csv`, varying-ref):
- Cd: mean 0.2774, median 0.2769, min 0.2370, max 0.3401, sd 0.0175
- Cl: mean 0.0283, median 0.0316, min -0.1553, max 0.2151, sd 0.0670

## Pinned reference values (run_466, from force_mom_466.csv — matches aggregate row)

| Coeff | Value | Ref basis |
|---|---|---|
| Cd | 2.758368e-01 | varying frontal area/wheelbase |
| Cl | -5.357145e-02 | varying frontal area/wheelbase |
| Clf | -1.803103e-01 | |
| Clr | 1.267388e-01 | |
| Cs | 2.565178e-02 | |

Reference quantities (`geo_ref_466.csv`): lRef=2.79 m, aRef=2.298 m²,
forcesCoR=(1.402 0 -0.3176). Constant-ref variant available in
`force_mom_constref_466.csv` (aRefRef=2.17, lRefRef=2.78618).

Gate reminder (pre-registration, not set here): V1 Cd within +/-10% (primary),
V2 Cl within +/-0.05 abs (secondary), vs the pinned DrivAerML run.

## Files staged (outside git)

Root: `/home/ubuntu/certonomous-runs/navier_class/DRIVAER/drivaerml_r7a5c094/`
Total 142,523,535 B (136 MiB).

| Path (relative to root) | Bytes |
|---|---|
| `run_466/drivaer_466.stl` | 142,346,740 |
| `run_466/force_mom_466.csv` | 84 |
| `run_466/force_mom_constref_466.csv` | 84 |
| `run_466/geo_parameters_466.csv` | 420 |
| `run_466/geo_ref_466.csv` | 111 |
| `meta/force_mom_all.csv` | 33,942 |
| `meta/force_mom_constref_all.csv` | 33,947 |
| `meta/geo_parameters_all.csv` | 77,574 |
| `meta/README.md` (dataset card) | 10,495 |
| `meta/LICENSE.txt` | 20,138 |

STL sha256: `9fd0eec1f436e336044c3abebe552e106acd273f63d96d9780c1441cc4c1a3b2`
STL upstream `x-linked-size`: 142,346,740 B (matches on-disk size).

Deliberately NOT fetched (multi-GB per run): `boundary_466.vtp` (~660 MB),
`volume_466.vtu.*.part` (~49 GB), slices/, images/, and all other runs.

## RULE-15 provenance verdict: PASS

Identity confirmed from the file's own content + dataset card, not filename/hash:
- ASCII STL, 49 named solids that are unmistakably a road car (BodyA-Pillar,
  BodyFender, BodyHeadlamps, BodyHood, BodyRoof, BodyWindowSide, BrakeDiscfront,
  ClosedGrill*, ...); 753,238 facets.
- Bounding box: x 4.572 m, y 2.004 m (with mirrors), z 1.546 m — full-scale
  DrivAer notchback passenger car.
- Ground plane z=-0.320 m coincides with geo_ref CoR z=-0.3176; CoR x=1.402
  sits inside the body x-range (-0.793..3.780) — internally coherent.
- Dataset card cites arXiv:2408.11969 with matching title and Ashton et al.
  authorship.

## Handoff to meshing (behind M6 — do NOT build yet)

- Mesh the single ASCII STL `run_466/drivaer_466.stl` with snappyHexMesh using
  the motorBike/external-aero template (surfaceFeatureExtract on the multi-solid
  STL, then snappy castellated+snap+layers).
- STL is in millimetres? NO — bbox is in metres (car ~4.6 m); use as-is, no scale.
- Domain, refinement boxes and y+ target per MESH_STANDARD.md; reference values
  for force post-processing: aRef=2.298 m², lRef=2.79 m, CofR=(1.402 0 -0.3176).
- Freeze (supervisor check-4) still HELD behind geometry (now cleared) -> mesh +
  smoke -> M6. This record does not lift any hold.
