# PPTC VP1304 — a published **snappyHexMesh** setup exists after all. Its background mesh is a CARTESIAN BOX, and that is the whole answer to our axis rod.

**Team:** cfd. **Lane:** lab-lane under `cfd-supervisor`. **Date:** 2026-09-13.
**Third in the series.** Companions: `PUBLISHED_SETUP_INGEST_SIKIRICA_2019.md` (commit `99cacfb12`)
and `PUBLISHED_OPENFOAM_SETUP_INGEST_SMP11.md` (commit `074d702bf`).

**Applying Sanaa's §G classification as relayed by `cfd-supervisor`:** numerics and domain practice
may be taken from any finite-volume source; **the mesher recipe must come from an OpenFOAM source.**
This file supplies the **mesher half** for the first time. The ruling itself is Sanaa's; nothing
here re-decides it (CLAUDE.md rule 9).

**Nothing left the box** (rules 7, 8). No solver launched. Frozen pre-registration untouched at blob
`6a27740da10c77d813bbe94db564d0fbee5b03b4`. Nothing paid for, no account created, nobody contacted.

---

## 1. THE SOURCE, TITLE-PAGE VERIFIED (CLAUDE.md rule 15)

`docs/papers/propeller_rotating_machinery/cheng_2024_omae2024_125991_pptc_les_snappyhexmesh.pdf`
4,939,950 bytes, sha256 `902d40c277b69c83672e157c0167782ab65f521170a7d8ccc2149305a6817739`, 12 pages,
`.txt` sidecar filed alongside (FILING_CHARTER R9).

Page 1 was rendered at 120 dpi and **read as a page**. Quoted as printed:

- Header: **"Proceedings of the OMAE 2024 / 43rd International Conference on Ocean, Offshore &
  Arctic Engineering / OMAE2024 / June 9–14, 2024, Singapore"**
- Paper number: **"OMAE2024-125991"**
- Title: **"MODELING OF HYDROACOUSTIC NOISE FROM MARINE PROPELLERS WITH TIP VORTEX CAVITATION"**
- Authors: **"Zhi Cheng¹·*, Suraj Kashyap¹, Brendan Smoker², Giorgio Burella², Rajeev Jaiman¹·*"**
- Affiliations: **"¹Mechanical Engineering, The University of British Columbia, 2329 West Mall,
  Vancouver, British Columbia, V6T 1Z4, CANADA"**; **"²Robert Allan Ltd. — Naval Architects and
  Marine Engineers, 250 Howe St #400, Vancouver, British Columbia, V6C 3R8, CANADA"**
- Side rail: **"arXiv:2405.15133v1 [physics.flu-dyn] 24 May 2024"**. Footer: **"Copyright © 2024 by ASME"**.

**Identity: CONFIRMED.** Retrieved from `https://arxiv.org/pdf/2405.15133` (open).

**Is it OpenFOAM? YES. Is it snappyHexMesh? YES**, stated in the paper's own words, p. 4:
> *"we use the SnappyHexMesh utility implemented in OpenFOAM. SnappyHexMesh generates high quality
> hexahedral or split-hexahedral meshes from triangulated surface geometries."*

Token counts: `OpenFOAM` 4, `snappy` 2, `PPTC` 6, `VP1304` 6, `Potsdam` 6.

**Is it our propeller? YES.** Table 1, p. 4, transcribed: D = **0.25 m**, pitch ratio at r/R 0.7 =
**1.635**, chord at r/R 0.7 = **0.417**, skew **18.837°**, hub ratio **0.300**, **5 blades** — every
value matches Sanaa's §B.2 geometry table for VP1304.

---

## 2. THE ROW THAT MATTERS MOST: THEIR BACKGROUND MESH IS A CARTESIAN BOX

**This is the finding, and it closes the axis-rod question.**

| claim | source | ours |
|---|---|---|
| computational domain is a **rectangular box**: streamwise **10 D**, cross-stream **2.4 D × 2.4 D** | p. 4 | **72° cylindrical wedge** closed by two cyclic patches (`make_blockmesh.py`) |
| propeller hub centre sits **2 D downstream of the inlet** → **8 D of domain downstream** | p. 4 | **6 D** downstream (`make_blockmesh.py:57`) |
| four side patches are **symmetry** boundaries, *"applied to four side patches to avoid blockage effects"* | p. 4 | outer boundary **slip**, radius 4 D |
| **full 360° propeller** with a rotor/stator **sliding interface** | p. 4, Fig. 1b | 72° single passage, MRF |
| the geometry carries a physical **cylindrical shaft** — Fig. 1b caption: *"propeller (accompanied by rod) surface"* | p. 4 | physical shaft **plus** a 2 mm **numerical** `axisRod` |

### 2.1 Why this settles it

Our defect (`verification/campaign/PPTC_PRISM_A1_PREREGISTRATION.md:26–36`):
`hexRef8::getLevel0EdgeLength()` returns the **global minimum** level-0 edge; on our mesh that is
the azimuthal chord of the 2 mm axis rod, `2·0.002·sin(π/60) = 2.09343825e-04 m`, making every
relative layer thickness **95.5× too small**.

**A Cartesian box background mesh has no such edge.** Every level-0 cell is a cube; the global
minimum level-0 edge *is* the base cell size, which is exactly what `relativeSizes true` is meant to
measure against. **There is nothing for the minimum to collapse onto.**

Their "rod" is the **physical propeller shaft**, a geometry surface snappy snaps to — not a
numerical body inserted to let a wedge close. Ours exists only because a 72° `blockMesh` wedge
cannot close on a collapsed axis edge (`make_blockmesh.py:11–38`, `R_AXIS = 0.002` at `:63`).

**So the published snappyHexMesh practice on this exact propeller avoids our defect by not using a
wedge at all.** Three independent published setups — Klerebrant (ANSA, full 360°), Gaggero
(unstructured, full 360°) and Cheng (snappyHexMesh, full 360° in a box) — **none of them meshes a
periodic passage.** Sikirica's 72° passage is the lone exception, and it is block-structured, where
a wedge closes on a collapsed edge legally.

**The generalisable lesson — and it is not PPTC-specific:** an **octree mesher wants a Cartesian
background**; forcing one onto a wedge domain requires an axis body whose azimuthal chord then
silently redefines the level-0 length that every relative size is measured against. This is the
lesson `cfd-supervisor` says is being filed; the evidence for it is this row.

### 2.2 What it does NOT say

`relativeSizes` appears **zero** times in the paper; so do `nSurfaceLayers`, `expansionRatio`,
`finalLayerThickness` and `minThickness`. **They publish that they used snappyHexMesh and what it
produced — not the dictionary.** No published `snappyHexMeshDict` for PPTC has been found by this
lane in any source. **Our layer-control values remain unsourced at the keyword level**, and that
gap should be stated on the certificate rather than papered over.

---

## 3. WHAT IS PUBLISHED: claim → source → ours → proposed registered value

Laid out so each row lifts straight into the new configuration `cfd-supervisor` will freeze.
**Proposed values are this lane's proposals only; the supervisor freezes, and no gate moves here.**

### 3.1 Mesher half (OpenFOAM-sourced, per Sanaa's classification)

| # | claim | source | ours | proposed |
|---|---|---|---|---|
| 1 | mesher is **snappyHexMesh**, OpenFOAM | p. 4 | snappyHexMesh | **unchanged** — now sourced |
| 2 | background mesh: **Cartesian box**, 10 D × 2.4 D × 2.4 D | p. 4 | 72° wedge + 2 mm `axisRod` | **for the supervisor:** the only published snappy background on this case is a box. A box + full 360° removes the rod, the tiny level-0 edge and the cyclic patches in one move — at ~5× the cells. A decision, not a lane's call. |
| 3 | grid family, **full propeller**: **18.0 M / 26.9 M / 40.4 M** cells (rotor region 15.0 / 22.5 / 33.7; stator 3.0 / 4.5 / 6.7) | **Table 2, p. 5** | 0.8 / 2.7 / 9 M per 72° passage ≈ 4 / 13.5 / 45 M full-propeller equivalent | our fine level ≈ their finest; **our coarse is 4.5× below their coarsest** |
| 4 | refinement is controlled by **"changing the base cell scale on the input/output patches"** | Table 2 caption, p. 5 | uniform ratio 1.5 on refinement levels and surface size | compatible in spirit |
| 5 | **achieved y+ per level: 92 → 40 → 19** | **Table 2, p. 5** | registered window 30–60; amended 30–300 for the smoke; prediction 50–200 | **their y+ falls as the grid refines, crossing our whole registered window.** A snappy grid family on this propeller spans y+ 19–92. |
| 6 | tip-vortex cell size `x̂_tv = x_tv/S`: **0.004 / 0.006 / 0.009** | Table 2, p. 5 | tip-vortex cylinder refinement 1 D downstream (prereg §5) | their normalised tip-vortex size is a directly checkable number for our tip band |
| 7 | mesh 3 cost: **~4.5 hours on 4×40 G resources** for 40.4 M cells | p. 4 | — | context for our meshing budget |
| 8 | `relativeSizes`, `nSurfaceLayers`, `expansionRatio`, `finalLayerThickness`, `minThickness` | **absent — 0 occurrences** | our values | **STILL UNSOURCED.** Disclose on the certificate. |

### 3.2 Numerics half — **and check `n` before using any of it**

| # | claim | source | ours | usable as a band? |
|---|---|---|---|---|
| 9 | **n = 25.0 s⁻¹**, **J = 1.019**, σ_n = 2.024, **cavitating** | Table 1, p. 4 | **n = 15 s⁻¹**, J 0.7985–1.4594, non-cavitating | **NO.** Third source, third rotation rate — Sikirica n=10, Klerebrant n unstated, Cheng n=25. **Its KT/KQ is NOT a comparator for our act.** |
| 10 | turbulence: **standard dynamic LES** (Smagorinsky-type), not RANS | p. 2 | steady RANS k-ω SST | different class entirely |
| 11 | cavitation: **Schnerr–Sauer**; acoustics: **Ffowcs Williams–Hawkings** | p. 1 | not modelled (later rungs, Sanaa §B.9) | out of scope |
| 12 | rotation: **sliding interface** (rotor/stator), transient | p. 4 | **MRF**, steady | theirs is our §B.10 next rung |
| 13 | non-dimensional time step **t·U₀/D = 2.55e-5** | p. 7 | n/a (steady) | context |
| 14 | KT, KQ definitions: **K_T = T/(ρ_l n²D⁴)**, **K_Q = Q/(ρ_l n²D⁵)**, **J = U₀/(nD)** | Eqs. 19–20, p. 4 | identical | **AGREE.** Fourth independent corroboration of our non-dimensionalisation. |
| 15 | BCs: Dirichlet velocity inlet (single upstream patch), Neumann outlet, **symmetry** on four sides | p. 4 | fixed velocity inlet, fixed-pressure outlet, slip outer | comparable |

### 3.3 Their validation, recorded as context only

Table 2, p. 5 — at J = 1.019, n = 25 s⁻¹, cavitating:

| case | KT,rms | 10KQ,rms | y+ | cells (M) |
|---|---|---|---|---|
| **Experiments [18]** | **0.374** | **0.9698** | — | — |
| Other simulation [37] | 0.380 | 0.9680 | — | — |
| Mesh 1 | 0.361 | 1.0398 | 92 | 18.0 |
| Mesh 2 | 0.375 | 0.9710 | 40 | 26.9 |
| Mesh 3 | 0.378 | 0.9648 | 19 | 40.4 |

Mesh 3 lands **+1.1 % on KT** and **−0.5 % on 10KQ** against experiment. Encouraging for
snappyHexMesh on this geometry — **but at n = 25 s⁻¹ in cavitating conditions with LES, so it sets
no band for us** (row 9). Note also the **non-monotone** KQ (1.0398 → 0.9710 → 0.9648 against a
rising-then-falling KT): under CLAUDE.md rule 5 this triple would need checking before any GCI were
quoted from it. **No GCI is quoted here, by them or by us.**

---

## 4. RETRIEVAL LEDGER FOR THE SUPERVISOR'S SIX-ITEM LIST

*(The brief said "ALL SIX", listed five numbered items, and then referred to "items 1, 3, 4, 5 and 7".
This lane treated the five numbered entries as the list and flags the numbering mismatch rather than
guessing at a sixth or seventh.)*

| # | target | retrieved | title-page verified | OpenFOAM | mesher rows |
|---|---|---|---|---|---|
| 1a | **Gaggero & Villa 2017**, *IMechE Part M* 231:411–440, doi `10.1177/1475090216644280` | **NO — CLOSED** | — | (claims OpenFOAM in its title) | — |
| 1b | **Gaggero & Villa "2018"** | **NOT IDENTIFIED** — no such PPTC/OpenFOAM record surfaced; **already delivered in substance** by `gaggero_villa_brizzolara_2011_smp11_…` (commit `074d702bf`) | ✔ (the 2011 one) | **YES** | prism thickness tuned to y+ < 30; **no snappy** |
| 2 | **JMSE 2024, 12, 2134** (AmgX GPU propeller CFD) | **NO — host-blocked.** Unpaywall/OpenAlex: **is_oa TRUE**, only two locations — `www.mdpi.com` (**HTTP 403**, Akamai "Access Denied") and a DOAJ record that redirects back to MDPI | — | — | — |
| 3 | **arXiv:2405.15133** | **YES** | **YES** | **YES** | **YES — §2, §3.1. The snappyHexMesh source.** |
| 4 | **IOP Conf. Ser. 1109 012048** — "Numerical modelling of freestream cavitating flow through ship propeller using OpenFOAM", Truong Van Ngoc, Mai Ngoc Luan, Ngo Khanh Hieu, 2021 | **NO — host-blocked.** OA per Unpaywall/S2 (**GOLD**), single location `iopscience.iop.org`, which returns **HTTP 200 with a Radware Bot Manager captcha** instead of the PDF | — | — | — |
| 5 | **The BKASM paper** — "Propeller simulation in open-water condition with BKASM — A user interface based on SnappyhexMesh/OpenFOAM" | **NO** — the only host located is **ResearchGate**, which requires an account. **Not attempted** (supervisor's instruction and rules 7–8) | — | — | — |

### 4.1 Blocked but confirmed to exist — worth one more attempt by any route

Items 2, 4 and 5 are all **open-access or openly posted** and all three are blocked by **bot walls,
not paywalls**. **Item 5 (BKASM) is by its title a snappyHexMesh interface paper and is the most
likely remaining source of an actual dictionary.** Item 4 is confirmed to be on **VP1304**.

**On item 4 I ran one WebFetch of the IOPscience landing page purely to triage.** It returned the
title, the three authors, the venue, and "VP1304" — and **no mesh settings, because the landing page
carries only the abstract.** **That is triage, not verification: no title page was read, nothing was
ingested, and no claim in this file rests on it.** Recorded so the next lane does not repeat it.

### 4.2 Two candidates fetched, checked, and DISCARDED rather than stretched

Both were open, both were OpenFOAM, and **neither is this case** — so under the supervisor's
standing instruction they were deleted rather than filed:

| candidate | tokens |
|---|---|
| Curtin University thesis, *"Analysis of Flow around a Ship Propeller using OpenFOAM"* (Colley, 2012) | `snappy` 10, `blockMesh` 7 — but **`VP1304` 0, `PPTC` 0, `Potsdam` 0** |
| KTH DiVA thesis, *"Simulating propeller and Propeller-Hull Interaction in OpenFOAM"* | `snappy` 1 — **`VP1304` 0, `PPTC` 0, `Potsdam` 0** |

Rule G asks for a published setup **of that case**. A snappy recipe for a different propeller is not
one, however tempting the `blockMesh` hit count.

---

## 5. WHAT THIS DOES NOT ESTABLISH

- **No published `snappyHexMeshDict` for PPTC has been found** — §2.2. The layer keywords remain
  unsourced across all six PPTC sources now on disk.
- No gate, threshold, cap or label is changed. The act pre-registration is frozen and has had first
  compute; the re-registration is a **new configuration**, drafted by the supervisor and frozen
  before it runs (CLAUDE.md rule 2, `VERIFICATION_CHARTER` §2b/§2d).
- Their results set **no band** for us — three sources, three different rotation rates (row 9).
- Items 2, 4, 5 of the retrieval list are **PENDING**, not absent: they exist and are open, and the
  obstacle is a bot wall this lane could not pass without an account.

---

## 6. COST

No solver launched. arXiv fetch, two discarded thesis fetches, `pdftotext`, page renders, and
read-only metadata lookups (OpenAlex, Semantic Scholar, Unpaywall — the Unpaywall email parameter
was a throwaway placeholder, **never the user's address**), single-threaded on one core.

- **Measured: 19.6 core-minutes** cumulative for this lane across all three ingests (4.1 + 7.2 + 8.3),
  from the command timeline. Cleaned; no stalls.
- **Derived, not measured:** 19.6 core-min = 0.327 core-h × \$0.0513/core-h ≈ **\$0.0168**.
  `cost_basis`: rate **owner-stated** (rule 12); the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Estimate vs actual:** no pre-registered estimate exists for a retrieval task; no calibration
  ratio is claimable. Stated rather than fabricated.
