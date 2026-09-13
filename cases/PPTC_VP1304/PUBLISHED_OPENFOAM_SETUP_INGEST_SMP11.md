# PPTC VP1304 — the published **OpenFOAM** setup, found. Two of them. And still no published snappyHexMesh recipe.

**Team:** cfd. **Lane:** lab-lane under `cfd-supervisor`. **Date:** 2026-09-13.
**Companion to:** `cases/PPTC_VP1304/PUBLISHED_SETUP_INGEST_SIKIRICA_2019.md` (commit `99cacfb12`),
which established that Sanaa's named source is a Fluent/STAR-CCM+ paper and that rule G was
therefore **not discharged**. This file is the follow-up fetch, authorised by `cfd-supervisor`.
**The fetch decision was the supervisor's; the ruling on rule G remains Sanaa's** (CLAUDE.md rule 9).

**Nothing left the box** (rules 7, 8). No solver launched. No frozen file edited — the open-water
pre-registration is untouched at blob `6a27740da10c77d813bbe94db564d0fbee5b03b4`.

---

## 0. HEADLINE

**A published OpenFOAM setup for PPTC VP1304 EXISTS and is now in the knowledge base — two
independent ones, both from the smp'11 workshop, both freely hosted, both title-page verified.**

**But `snappyHexMesh` appears in NONE of them.** Both built the mesh in a commercial mesher and
ran it in OpenFOAM. Across every PPTC document the lab now holds — five papers, 60+ pages of
participant questionnaire — the token `snappyHexMesh` occurs **zero** times.

So rule G divides cleanly, and the supervisor should carry the division upward rather than a
single yes/no:

| rule G element | published for PPTC in OpenFOAM? |
|---|---|
| solver and rotating-frame method | **YES** — `MRFSimpleFoam`, steady RANS |
| turbulence model and **wall treatment** | **YES** — high-Re k-ω SST **with wall functions** |
| **layer settings** (count, growth, first height) | **YES** — 5 layers, growth 1.2, first layer **0.5 mm absolute** |
| **achieved y+** | **YES** — a measured table, 25–34 |
| schemes | **YES** — 2nd-order upwind U, **1st-order** turbulence |
| convergence criterion | **YES** — all residuals < **1e-5** |
| domain extents | **YES** — and both published setups are **longer downstream than ours** |
| **mesh recipe as a snappyHexMesh dictionary** | **NO. Does not exist in the literature we can reach.** |

---

## 1. SOURCES RETRIEVED AND TITLE-PAGE VERIFIED (CLAUDE.md rule 15)

Each PDF was rendered to an image and **page 1 read as a page**. All three are now filed in
`docs/papers/propeller_rotating_machinery/` with `.txt` sidecars (FILING_CHARTER R9).

### 1.1 `klerebrant_klasson_huuva_2011_smp11_pptc_openfoam.pdf` — **the primary find**

1,337,164 bytes, sha256 `b6716a8ad6a8620d37c5982a3e90f1e97add121307a632452cd56648b7840699`, 7 pages.

Read on the title page, verbatim: **"Second International Symposium on Marine Propulsors /
smp'11, Hamburg, Germany, June 2011 / Workshop: Propeller performance"**; title **"Potsdam
Propeller Test Case (PPTC)"**; authors **"Olof Klerebrant Klasson¹, Tobias Huuva²"**;
affiliation **"Core Competence Team, Berg Propulsion AB, Hönö, Sweden"**; keywords
**"OpenFOAM; PROCAL; Pressure side cavitation; Validate; Grid dependence"**. The abstract states
**"The y+ in the near wall region was larger than 30 for all CFD setups."**

Token counts: `OpenFOAM` **9**, `Fluent` 0, `STAR-CCM` 0, `CFX` 0, **`snappy` 0**, `blockMesh` 0.

Source: `https://www.marinepropulsors.com/smp/files/downloads/smp11_workshop/smp11_workshop/II-2.1_Klerebrant_Klasson.pdf`

### 1.2 `gaggero_villa_brizzolara_2011_smp11_pptc_unigenova_openfoam.pdf`

3,789,520 bytes, sha256 `608129f54fbbf7930d84d985db6f8a90e0a9573d75d634610bc82e8c2be053a6`, 14 pages.

Title page, verbatim: same smp'11 header; title **"SMP Workshop on Cavitation and Propeller
Performances: The Experience of the University of Genova on the Potsdam Propeller Test Case"**;
authors **"Stefano Gaggero¹, Diego Villa¹, Stefano Brizzolara¹"**; affiliation **"University of
Genova, Department of Naval Architecture, Marine and Electrical Engineering, Genoa, Italy"**.

Token counts: `OpenFOAM` **20**, `StarCCM+` present, **`snappy` 0**, `blockMesh` 0.

**This is the Gaggero/Villa OpenFOAM work the supervisor asked for.** The 2017 journal paper
(*Proc. IMechE Part M* 231:411–440, doi 10.1177/1475090216644280) is **CLOSED** — see §4 — but
the same group's PPTC workshop paper is freely hosted and is on this exact propeller.

### 1.3 `sva_2011_smp11_questionnaire_on_viscous_flow_methods.pdf`

1,012,106 bytes, sha256 `06e1460a89ee77c2efe7cb5200e4e658fb8e9b99299b5efa532dfcd23a003e20`, 13 pages.

A **filled comparison matrix of all 14 workshop participants' viscous-flow setups** — domain
topology, grid type, wall-boundary-layer type, cells across the boundary layer, y+ at three radii,
cells per blade, convection schemes, turbulence models. Column headers name the participants
(`01_BERG`, `02_CRADLE`, `03_CSSRC`, `04_HSVA`, `07_MARIC`, `08_SSPA`, `09_TUHH`, `10_UniGenua`,
`11_UniTriest`, `12_VICUS`, `13_VOITH`, `14_VTT`).

Source: `https://www.sva-potsdam.de/wp-content/uploads/2016/03/Questionnaire_on_viscous_flow_methods.pdf`

**Honest limitation:** the participant-name header sits on page 1 and the numeric rows on page 3;
**this lane did not resolve the column-to-participant mapping** and therefore attributes **no row
to any named participant**. Only the *envelope* is quoted below, which needs no mapping.

---

## 2. THE PUBLISHED OpenFOAM RECIPE — claim → source → ours

Source column = page of `klerebrant_klasson_huuva_2011_smp11_pptc_openfoam.pdf` unless marked.

### 2.1 Solver, turbulence, wall treatment — **where we AGREE, and it matters**

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 1 | CFD package **OpenFOAM 1.6**, solver **`MRFSimpleFoam`**, steady RANS | p. 2 | `simpleFoam` + `MRFProperties`, steady (prereg §6) | **AGREE.** `MRFSimpleFoam` is the 1.6-era name for exactly our scheme; modern `simpleFoam` absorbed MRF. **Our solver choice is published practice on this case.** |
| 2 | turbulence: **high-Reynolds-number k-ω SST**; *"To model the boundary layer, wall functions were needed"* | p. 2 | k-ω SST + `nutkWallFunction` (prereg §6) | **AGREE, exactly.** This is the corroboration Sikirica could not give: Sikirica ran wall-resolved y+≈1, we run wall functions — and **the published OpenFOAM practice on this propeller runs wall functions too.** |
| 3 | rotation modelled with **MRF** | p. 2 | MRF (prereg §5, §6) | **AGREE.** |
| 4 | convergence: *"all residuals of pressure, velocity and turbulent quantities were below 10⁻⁵"* | p. 3 | residuals < **1e-5** on p and U (prereg §6) | **AGREE on the threshold.** Ours is looser only in that it names p and U, not turbulence. Sikirica's Fluent criterion was 1e-6; **the published OpenFOAM criterion is 1e-5, ours.** |
| 5 | KT, KQ, η definitions | Eqs. 6–8, p. 3 | identical (Sanaa B §3) | **AGREE.** Third independent corroboration. |
| 6 | gap at blade root **and** hub/shaft intersection **filled** | p. 1, Fig. 1 | 0.3 mm root gap closed (Sanaa B §2a) | **AGREE.** Note they also close the **hub/shaft** intersection gap — we should confirm ours does. |

### 2.2 Layers — **the rows rule G was written for**

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 7 | **"Five prism layers with 1.2 as growth ratio and a starting length of 0.5 mm were applied."** | **p. 2, verbatim** | `nSurfaceLayers` **6**, `expansionRatio` **1.2**, `finalLayerThickness 0.5` **relative**, `minThickness 0.05` relative (`make_snappy.py:48,49,165,169,170`) | **growth ratio 1.2 AGREES EXACTLY.** Layer count 5 vs our 6 — close. **The sizing basis DISAGREES: theirs is an absolute 0.5 mm first-layer height; ours is relative.** |
| 8 | prism-layer cell counts: coarse **503,000** layer elements on 100,000 surface triangles; fine **605,000** on 151,000 | p. 2 | — | context |
| 9 | cells across the boundary layer, across all 14 participants: **0 to 34** | questionnaire row **C7**, p. 3 | 6 | our 6 sits low-mid in the published envelope |

**0.5 mm is 0.002 D** on this 250 mm propeller. That is the published first-cell height, stated as
an absolute length, for a wall-function k-ω SST run on this exact geometry.

### 2.3 Achieved y+ — **a measured table, which Sikirica did not publish**

| # | claim | source | ours |
|---|---|---|---|
| 10 | **Table 2, y+ achieved** — J 0.6: coarse **34**, fine **30**; J 0.8: **26 / 31**; J 1.0: **25 / 34**; J 1.2: **25 / 34** | p. 4, Table 2 | registered window **30–60**, amended **30–300** for the smoke; registered prediction **50–200** (prereg §A4.1b, §A4.2) |
| 11 | abstract claim: *"The y+ in the near wall region was larger than 30 for all CFD setups"* | p. 1 | — |
| 12 | y+ envelope across all 14 participants at r/R = 0.4 / 0.7 / 0.9: values from **<1** to **160**, with a visible cluster at **30–50** | questionnaire row **C8**, p. 3 (columns not attributed — see §1.3) | our 30–60 window sits inside the cluster |

**Note a tension inside the source itself, recorded rather than smoothed:** the abstract says y+ was
*"larger than 30 for all CFD setups"*, while Table 2 lists **25, 25 and 26**. The table is the
measurement; the abstract is the rounding. **We cite the table.**

**Direct use for us:** a 0.5 mm first layer with 5 layers at 1.2 delivered **y+ 25–34** on this
propeller. Our registered window is 30–60. That is the published anchor for our first-cell height,
and it says **our target is reachable at a first-cell height near 0.5–1.0 mm, not at the sub-0.1 mm
our poisoned relative sizing would have produced.**

### 2.4 Schemes — **where we disagree with published OpenFOAM practice**

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 13 | velocity: **second-order upwind** | p. 2 | `linearUpwind` for U (prereg §6) | **AGREE.** |
| 14 | turbulence (k, ω, ν_t): **"first order accurate schemes were used"** | **p. 2, verbatim** | `limitedLinear 1` — second-order — for turbulence (prereg §6) | **DISAGREE.** Published OpenFOAM practice on this case ran **first-order** turbulence convection. Ours is second-order. Not necessarily wrong — but it is a departure from the published recipe and must be disclosed, not assumed superior. |
| 15 | workshop-wide momentum convection: **high-order upwind** dominant across participants | questionnaire row, p. 9 | `linearUpwind` | **AGREE with the field.** |
| 16 | workshop-wide turbulence convection: **1st-order upwind** and **high-order upwind** both common | questionnaire, p. 10 | second-order | our choice is inside the field's spread, outside Berg's |

### 2.5 Domain and MRF zone — **our downstream extent is short against BOTH published setups**

D = 250 mm throughout.

| # | quantity | Klerebrant (p. 2) | Sikirica (p. 6) | **ours** | verdict |
|---|---|---|---|---|---|
| 17 | domain diameter | 1261 mm = **5.04 D** (radius 2.52 D) | **5 D** (radius 2.5 D) | radius **4 D** (`make_blockmesh.py:58`) | **ours 1.6× wider than both.** Two independent published setups agree on ≈2.5 D radius. |
| 18 | upstream | 1261 mm = **5.04 D** | **3.5 D** | **3 D** (`:56`) | **ours the shortest of the three.** |
| 19 | **downstream** | 3000 mm = **12.0 D** | **10 D** | **6 D** (`:57`) | **ours is 0.5× and 0.6× of the two published values.** Sikirica's own survey (p. 6) says *"values larger than 7D are usually adequate"*. **Our 6 D is below every published figure and below the stated envelope.** |
| 20 | MRF zone diameter | radius = R_prop + 59 mm = 184 mm → **1.47 D** | n/a (SRF, whole domain rotates) | **1.3 D**, sensitivity at 1.6 D (prereg §5) | **their 1.47 D lies between our baseline and our sensitivity point.** Our registered sensitivity pair brackets published practice — that is a good sign for the check, and worth saying on the certificate. |
| 21 | MRF zone axial extent | **69 mm upstream (0.28 D)**, **2442 mm downstream (9.77 D)** — the zone *is* the slipstream | n/a | **±0.5 D** (prereg §5) | **DISAGREE strongly downstream: 9.77 D vs 0.5 D.** Theirs carries the whole slipstream inside the rotating frame. A material modelling difference; flag it, do not copy it blind (a 9.77 D MRF zone changes what the wake means). |

### 2.6 Topology, mesher, and force bookkeeping

| # | claim | source | ours | agreement |
|---|---|---|---|---|
| 22 | mesher: **ANSA 13.10**; surfaces meshed with triangles 1–10 mm; interior **hexahedral**; prism layers; *"minimal amount of tetras and pyramids in the transition"* | pp. 1–2 | **snappyHexMesh** | **NO PUBLISHED SNAPPY RECIPE.** Theirs is a commercial hex-dominant unstructured mesher. |
| 23 | Gaggero: **unstructured**, **1.4 M cells, entire propeller** (OpenFOAM); prism-layer thickness and discretisation tuned *"in order to reach satisfactory values for the [y+] parameter (generally lower than 30)"* | Gaggero pp. 2–3 | — | **also absolute prism tuning; also no snappy** |
| 24 | full **360° propeller**, not a periodic passage | p. 2 (*"for all four blades"*) | **72° cyclic passage** (`SECTOR_PHASE_DEG = 21.2830`) | **DISAGREE.** Sikirica used a 72° passage; Klerebrant and Gaggero ran the whole propeller. Our registered full-360 cross-check (Sanaa B §7 item 4) is the right instrument for this. |
| 25 | grid sizes: coarse **4.5 M**, fine **11 M** (whole propeller) | p. 2 | 0.8 / 2.7 / 9 M **per 72° passage** → ≈4 / 13.5 / 45 M full-propeller equivalent | **ours is finer than published practice** at medium and fine. |
| 26 | **forces integrated on the BLADES ONLY** | **p. 2, verbatim** | thrust and torque on **blades + hub + shaft** (Sanaa B §3) | **DISAGREE — and it changes the comparator.** See §3.2. |

**An internal error in the source, recorded not smoothed:** Klerebrant repeatedly writes *"for all
four blades"* (pp. 2, 3). **VP1304 has five blades** (SVA Report 3752 Table 1; Sikirica p. 4). Their
cell counts are therefore **not safely divisible per blade**, and this lane uses them only as
whole-propeller totals. Flagged because a per-blade count derived from it would be wrong by 25%.

---

## 3. THEIR RESULTS, AND HOW FAR WE MAY USE THEM

### 3.1 The published OpenFOAM open-water numbers

Table 1, p. 4 (the `Kq` column is 10·KQ):

| J | KT coarse | KT fine | 10KQ coarse | 10KQ fine | η coarse | η fine |
|---|---|---|---|---|---|---|
| 0.6 | 0.624 | 0.623 | 1.431 | 1.415 | 0.416 | 0.421 |
| 0.8 | 0.504 | 0.505 | 1.190 | 1.189 | 0.540 | 0.541 |
| 1.0 | 0.392 | 0.397 | 0.970 | 0.984 | 0.643 | 0.643 |
| 1.2 | 0.287 | 0.289 | 0.770 | 0.778 | 0.712 | 0.710 |

Grid dependence is **small** — KT changes by ≤0.005 between a 4.5 M and an 11 M mesh. Their own
abstract: *"the grid dependence in the used CFD setup was small"*, and at max efficiency
**J_ηmax = 1.2, η_o = 0.71** (p. 1).

### 3.2 Against SVA — stated two ways, because the bookkeeping decides it

Our registered comparator is Report 3752 p. 2.11, *"corrected with idle torque and gap force …
including the hub"*, at **n = 15 s⁻¹** (Sanaa B §3).

| J | SVA measured (incl. hub, n=15) | Klerebrant fine | difference |
|---|---|---|---|
| 0.7985 / 0.8 | KT 0.5052, 10KQ 1.1836 | KT 0.505, 10KQ 1.189 | **KT +0.04 %**, 10KQ **+0.5 %** |
| 1.2021 / 1.2 | KT 0.2797, 10KQ 0.7676 | KT 0.289, 10KQ 0.778 | KT **+3.3 %**, 10KQ **+1.4 %** |

**But their forces are blades-only (row 26), and Sanaa's §3 records that the blades-only SVA table
differs from the including-hub table by about 0.01 in KT at J = 1.2.** Read against blades-only
measured (≈0.270), their J=1.2 KT of 0.289 is **≈ +7 %**, not +3.3 %.

**Therefore: this is a cross-check, not a band.** Their rotation rate is not stated for the open-water
case in the text this lane read, their force bookkeeping differs from ours, and their J grid
(0.6–1.2) only partly overlaps ours (0.7985–1.4594). **No gate may be set from these numbers.**
What they legitimately give us is a **direction and magnitude prediction**: a wall-function k-ω SST
OpenFOAM MRF run on this propeller lands within a few percent on KT and slightly **over** on KQ —
which is exactly the systematic direction Sanaa already registered as a prediction in §B.4.

---

## 4. GAGGERO & VILLA 2017 — CLOSED, FOUR INDEPENDENT CHECKS

The supervisor's first-priority target, *"Steady cavitating propeller performance by using OpenFOAM,
StarCCM+ and a boundary element method"*, doi `10.1177/1475090216644280`:

| check | result |
|---|---|
| OpenAlex | `is_oa: false`, **no OA location** |
| Semantic Scholar | `isOpenAccess: false`, `openAccessPdf.status: "CLOSED"` |
| Unpaywall | `is_oa: False`, **no `oa_locations`** |
| **IRIS UniGe** (the authors' own institutional repository), record `handle/11567/831911` | title matches; **"Accesso chiuso"**; **no bitstream** |

**Not retrievable without payment or an account. Neither was attempted** — the supervisor's
instruction and CLAUDE.md rules 7–8 forbid both, and nobody was contacted.

**It is also moot for rule G:** the same authors' PPTC OpenFOAM work is in §1.2, freely hosted.

### 4.1 Other routes attempted and blocked (recorded so nobody repeats them)

| target | host | outcome |
|---|---|---|
| MDPI PDFs (JMSE 11/2199, 9/351) | `www.mdpi.com` | **HTTP 403**, Akamai edge "Access Denied" |
| Lidtke 2015 acoustic-analogy paper | `eprints.soton.ac.uk` | **HTTP 403**, Anubis bot wall |
| IOP 2021 *"Numerical modelling of freestream cavitating flow through ship propeller using OpenFOAM"* | `iopscience.iop.org` | **HTTP 200 but HTML** — Radware Bot Manager captcha |
| Hindawi, preprints.org | various | **HTTP 403** |
| Polish Maritime Research 2016 | `content.sciendo.com` | **fetched, 18 MB PDF** — not yet title-page verified; **not ingested, not relied on** |

**The IOP 2021 paper remains an unchecked OpenFOAM PPTC candidate** and is the obvious next fetch
if anyone finds a route. It is named here so the gap is visible, not so it can be cited.

---

## 5. WHAT THIS CHANGES, AND WHAT IT DOES NOT

### 5.1 `relativeSizes` — the published practice is now on the record

**No published OpenFOAM setup of this propeller uses relative layer sizing.** Klerebrant states an
**absolute 0.5 mm starting length** (p. 2); Gaggero tunes **"prism layer thickness"** to hit a y+
target (p. 3). Neither expresses layer thickness as a fraction of a background cell.

This does **not** overturn and does **not** rescue anything — `relativeSizes` is a snappyHexMesh
keyword and neither paper uses snappyHexMesh, so neither is evidence about the keyword (rule 3:
silence is not a reading). **What it does is remove the last reason to prefer relative sizing:**
the practice we were told to start from specifies a first-cell height in millimetres. **PRISM-A2's
`relativeSizes false` is now aligned with published practice rather than merely with our own
diagnosis of `hexRef8::getLevel0EdgeLength()`.**

And the 2 mm axis rod remains ours alone: Klerebrant and Gaggero meshed the **full 360° propeller**,
so no wedge had to close on an axis and no rod was ever needed.

### 5.2 What rule G can and cannot now be said to require

**Dischargeable from what is now on disk:** solver, rotating-frame method, turbulence model, wall
treatment, layer count, growth ratio, first-layer height, achieved y+, convergence threshold,
schemes, domain extents, force definitions.

**Not dischargeable at all:** a published `snappyHexMeshDict` for this case. It does not appear to
exist. **If rule G is read to require one, PPTC cannot proceed in snappyHexMesh at all** — which
would be a ruling about our mesher, not about our diligence. **That reading is Sanaa's to make.**

### 5.3 Not established here

- No gate, threshold, cap or label is changed. Any departure lands as a dated addendum at the foot
  of the frozen pre-registration with a version bump and `lines whose number changed above this
  section: 0` (CLAUDE.md rule 6).
- The questionnaire's column-to-participant mapping (§1.3).
- Klerebrant's open-water rotation rate `n`, not found in the text this lane read.
- Whether our geometry closes the **hub/shaft** intersection gap as well as the root gap (row 6).
- The IOP 2021 OpenFOAM PPTC paper (§4.1).

---

## 6. COST

No solver launched. PDF fetches, `pdftotext`, five `pdftoppm` page renders, three metadata API
lookups (OpenAlex, Semantic Scholar, Unpaywall — read-only; the Unpaywall email parameter was a
throwaway placeholder, **never the user's address**), single-threaded on one core.

- **Measured: 11.3 core-minutes** cumulative for this lane across both ingests (4.1 + 7.2), from
  the command timeline. Cleaned; no stalls.
- **Derived, not measured:** 11.3 core-min = 0.188 core-h × \$0.0513/core-h ≈ **\$0.0097**.
  `cost_basis`: rate **owner-stated** (rule 12); the box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Estimate vs actual:** no pre-registered estimate exists for a retrieval task; no calibration
  ratio is claimable. Stated rather than fabricated.
- **Network:** retrieval only. Nothing sent, posted, registered, submitted or filed; nobody
  contacted; no account created; nothing paid for (rules 7, 8).
