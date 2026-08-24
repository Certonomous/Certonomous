# Closure line restart doctrine

**Ruled by Sanaa on 2026-08-18, and amended by her the same day.** Relayed by the coordinator on
2026-08-20. Recorded here by the closure team after Phases 1-4 closed and were committed
(`b8ba7460`, `9e567786`, `20666e97`).

**This recording is documentation only.** No R2 shortlist was drawn, no feature-selection run was
made, and no repository was created by writing this file. **R3 is Sanaa's decision, never the
lab's.**

**Sole source.** Every rule below traces to the coordinator's verbatim relay of the ruling. Nothing
has been added, inferred, softened or extended. Where this file annotates a rule with the corpus
status of a paper, or with the `PAPER_CATALOGUE.md` category a shelf maps onto, the annotation is
marked as such and **is a status note, not a rule.**

The binding rules are folded into `docs/charters/CLOSURE_MODELLING_CHARTER.md` §22.

---

## The ruling

> **The round-5 heterogeneous Closure Challenge entry is NOT SENT.**

The closure line restarts with:

1. **ONE closure model applied uniformly to all eight cases.**
2. **Physically consistent — corrections live inside the solved equations: re-solve, not
   post-hoc.**
3. **Aimed at a future scoring round and publishable work.**
4. **The round-5 record stays internal R&D with full honest documentation.**
5. **External surfaces drop leaderboard claims, or keep only the internal-scoring phrasing Sanaa
   approves.**

---

## Part 1 / 1b — The library

Eight shelves. The **Status** column is an annotation against
`docs/papers/closure/MANIFEST.md`: **on disk** means a title-verified PDF is in the canonical
corpus; **PENDING-MIT** means it is one of the 16 titles in `MANIFEST.md` §4 awaiting institutional
access, and **no number from it appears anywhere in the lab's documents.** The **Catalogue**
column is an annotation giving the `docs/closure/PAPER_CATALOGUE.md` category the item is
catalogued under, which is not always the same letter as its shelf.

### Shelf A — Foundations

| Item | Status | Catalogue |
|---|---|---|
| Pope 1975 | on disk | A |
| Spalart 2000 | on disk | A |
| Gatski & Speziale 1993 | **PENDING-MIT** | — (the 1996 handbook chapter is on disk as a substitute; it is a scan with no text layer) |
| Menter 1994 | on disk | A |
| Duraisamy, Iaccarino & Xiao 2019 | on disk | R |

### Shelf B — Data-driven RANS

| Item | Status | Catalogue |
|---|---|---|
| Ling 2016 TBNN | on disk | B |
| Wang, Wu & Xiao 2017 | on disk | B |
| Wu, Xiao & Paterson 2018 | on disk | B |
| Schmelzer 2020 SpaRTA | on disk | B |
| Weatheritt & Sandberg 2016 GEP | **PENDING-MIT** | — |

### Shelf C — FIML

| Item | Status | Catalogue |
|---|---|---|
| Parish & Duraisamy 2016 | **PENDING-MIT** | — |
| Singh & Duraisamy 2016 | **PENDING-MIT** | — |
| Singh, Medida & Duraisamy 2017 | on disk | C |
| Holland, Baeder & Duraisamy 2019 FIML-C embedded | **PENDING-MIT** | — |

### Shelf D — Model-form UQ

| Item | Status | Catalogue |
|---|---|---|
| Emory 2013 | **PENDING-MIT** | — |
| Xiao 2016 | on disk | D |
| Mishra & Iaccarino lineage | Iaccarino 2017 is **PENDING-MIT** | — |

> **FABLE selects the canonical implementation paper for this shelf.** Recorded as an **open
> action**; the selection is not made in this document. See "Open actions" below.

### Shelf E — LES SGS

| Item | Status | Catalogue |
|---|---|---|
| Germano 1991 | **PENDING-MIT** | — |
| Nicoud & Ducros 1999 | on disk | E (filed in the catalogue's A section) |
| Vreman 2004 | **PENDING-MIT** | — |
| Maulik & San 2017 | on disk | E |
| Beck, Flad & Munz 2019 | on disk | E |
| Sirignano, MacArt & Freund 2020 DPM | on disk | E / G |
| Duraisamy 2021 | on disk | R |
| Smagorinsky 1963 | on disk | E (filed in the catalogue's A section) |
| Bardina 1980 | **PENDING-MIT** | — |
| Park & Choi 2021 | **PENDING-MIT** | — |

### Shelf F — WMLES

| Item | Status | Catalogue |
|---|---|---|
| Piomelli & Balaras 2002 | on disk | F |
| Bose & Park 2018 | **PENDING-MIT** | — |
| Yang 2019 | **PENDING-MIT** | — |
| Bae & Koumoutsakos 2022 | on disk | F |
| Larsson 2016 | on disk | F |
| Lozano-Duran & Bae 2023 | on disk | F |

### Shelf G — Modern DL / differentiable

| Item | Status | Catalogue |
|---|---|---|
| Kaandorp & Dwight 2020 | on disk | B |
| Stroefer & Xiao 2021 | on disk | G |
| Um 2020 Solver-in-the-Loop | on disk | G |
| Kochkov 2021 | on disk | G |
| List, Chen & Thuerey 2022 | on disk | G |
| Beck & Kurz 2021 | on disk | R |
| Sanderse 2024 | on disk | R |
| Guan 2022 CNN-SGS 2-D turbulence | on disk | E |
| Zanna & Bolton 2020 ocean closures | **PENDING-MIT** | — |

### Shelf H — Mixtures

| Item | Status | Catalogue |
|---|---|---|
| Edeling, Cinnella & Dwight 2014 BMSA | **PENDING-MIT** | — |
| Cinnella-group space-dependent aggregation = de Zordo-Banliat 2023 | on disk | H |

**Cross-links, as ruled:** **shelf D as the uncertainty envelope around any mixture**, and
**FIML-C as the training mechanism for mixture weights.**

### The note on shelf H

> **A mixture applied UNIFORMLY — the same mixture law everywhere, learned once — satisfies the
> one-model doctrine. Per-case manual switching does not. The mixture law itself is the single
> model.**

### The doctrine, as sharpened

> **The lab acquires expertise FIRST from this literature, and only then mixes models or designs a
> new one. Invention is downstream of mastery, never parallel to it.**

### Corpus-coverage annotation

**Annotation, not a rule.** Of the 16 PENDING-MIT titles in `MANIFEST.md` §4, **15 are named on a
shelf above**; the sixteenth, **Ling & Templeton 2015**, is not named on any shelf. Four
title-verified papers in the canonical corpus are likewise not named on any shelf: **Maulik, San,
Rasheed & Vedula 2019**, **Wu, Xiao, Sun & Wang 2019** (the ill-conditioning paper), **Guyon &
Elisseeff 2003** (which the ruling names in FS3 rather than on a shelf), and the **Gatski 1996**
handbook chapter held as the substitute for Gatski & Speziale 1993. Recorded so the difference
between the shelves and the corpus is visible; **the shelves are as ruled and are not amended
here.**

---

## Part 2 — Ingestion

- **PDFs via scp, never git.**
- **HAIKU indexes title -> shelf -> file -> status.**
- **FABLE writes, per paper, one structured note** carrying:
  - what it corrects — **coefficient / anisotropy / SGS flux / wall stress**;
  - **inputs-outputs**;
  - **training data**;
  - **generalization evidence SHOWN, not claimed**;
  - **solver-embedding requirements**;
  - **implementability in our stack (OpenFOAM + DAFoam adjoint)**;
  - **the one number the paper validates against**.
- **Quote-or-cut.**
- **SONNET second-reader spot-checks 20% of extracted claims against the PDFs.**

---

## Part 3 — Rebuild program

### R1 — Doctrine, pre-registered before any training

- **One model, uniform, all eight cases.**
- **Corrections inside the solved equations.**
- **Continuity by construction.**
- **Zero-shot transfer discipline: train on training flows only; test families touched once per
  scoring round, nothing per-case.**
- **Every prediction ships the model-form band (shelf D).**

### R2 — Candidate shortlist

**FABLE ranks 3 model classes** by:

1. **(a)** can our stack train and embed it;
2. **(b)** literature evidence of cross-geometry generalization;
3. **(c)** fit to duct + hill + hump — **needs anisotropy; the F6c/QCR lesson says linear won't**.

**Expected finalists: TBNN-class, FIML-C on our adjoint engine, SpaRTA-class — argued, not
assumed.**

### R3 — Sanaa picks the class

> **SANAA PICKS THE CLASS**, as a docket decision with the shortlist memo. **The lab does NOT
> pick.**

**RATIFICATION — 2026-08-24. R3 IS RATIFIED, AND THE DECISION THIS ENTRY RESERVED TO SANAA IS CLOSED.**

*(Appended 2026-08-24 by the closure team. The R3 text above is reproduced nowhere and rewritten
nowhere; lines whose number changed above this section: 0.)*

Sanaa ruled this week. Her words, verbatim:

> R3 is ratified (SpaRTA-class, TBNN fallback) — R4's CPU-minutes run in parallel; they never displace consolidation work.

and, from her standing section, verbatim:

> R4 (SpaRTA build) runs in parallel on its CPU-minutes; FS gates apply.

**What this closes.** The decision reserved to Sanaa alone by
`docs/charters/CLOSURE_MODELLING_CHARTER.md` §22.7 — *"SANAA picks, as a docket decision"*,
*"The lab does NOT pick the model class"* — and by this Part 3 R3 entry — *"SANAA PICKS THE
CLASS ... The lab does NOT pick"* — is **CLOSED**. The class is **SpaRTA-class**, with **TBNN as
the fallback class**. Open action 3 of this document is closed by the same ruling; that row stands
unedited, with the dated closing note appended beneath the table.

**What is new on 2026-08-24, and what is not. The class did NOT change.** Sanaa's 2026-08-21 word
— *"R3: Sparta"* — was already on record: appended to `docs/closure/R2_SHORTLIST_MEMO.md`,
docketed as **D443** / **D444**, and carried on `docs/LAB_STATE.md` as *"R3 = SpaRTA / DECIDED"*.
What the 2026-08-24 ruling adds is three things, and only these three:

1. **It is stated as a ratification**, closing §22.7 and this Part 3 R3 entry.
2. **It names TBNN as the FALLBACK class explicitly**, which the 2026-08-21 record did not.
3. **It sets the parallel-capacity rule** for R4's CPU-minutes, with the clause that they **never
   displace consolidation work**; FS gates apply to the SpaRTA build.

**What this ratification does NOT do.** It does **not** re-open R2's ranking; it does **not**
authorise the one pre-registered zero-shot scoring call that R4 ends in — that remains Sanaa's
separate word; and it does **not** lift **SUBMISSIONS PARKED** (`CLAUDE.md` rule 7).

Docket: **D510**. Recording it cost **0.0 core-minutes** — zero compute, a records task only.

### R4 — Build ladder

**Implement -> verify on training flows a-priori AND a-posteriori (the re-solved field) ->
validation gates -> ONE pre-registered scoring call when Sanaa says so.**

**S1's FD-verified adjoint engine and the leakage/freeze apparatus carry over unchanged.**

### R5 — Round-5 diagnostics feed the build as constraints

- **duct feature degeneracy**;
- **`Re_y` extrapolation trap**;
- **vortex-structure failure — structure metrics in OUR validation.**

### R6 — Surfaces updated

- **Leaderboard claims removed, or reduced to approved internal-scoring phrasing.**
- **The one-model doctrine stated on the closure page.**

---

## Part 4 — Feature selection program

> **The named mistake, never again: a feature set was selected once and treated as the only
> possible set.**

> **Feature selection is a FIRST-CLASS RESEARCH CAPABILITY.**

### FS1 — Maximal feature library first

**Wu-Xiao-Paterson comprehensive invariant basis + normalization variants. Start maximal, select
down.**

### FS2 — Degeneracy audit, as a standing gate

**Per family: per-feature variance, range coverage, feature-matrix rank. Anything algebraically
zero or near-constant is flagged BEFORE training. A coverage report ships with every model.**

### FS3 — Selection methods applied and compared, prediction-first

**Mutual information, permutation importance, L1/sparse, forward/backward with cross-family
validation** (**Guyon & Elisseeff 2003**; B3/G1 practice).

### FS4 — Joint iteration

**Features are selected PER MODEL CLASS, under a pre-registered protocol using training and
validation families only, frozen before any scoring.**

### FS5 — Extrapolation-coverage check

**Every feature's test-family range against its training range. Beyond a declared factor ->
retrain-coverage expansion, or explicit documented acceptance.**

### FS6 — Comparative feature document

**FABLE mines every paper's feature table into one comparative document with page cites.**

---

## Part 5 — Two-repo doctrine

### Repo 1

**`Certonomous_closure_challenge` stays PRIVATE, full history, nothing removed.**

### Repo 2

**A NEW public repo** — name proposal **`closure-model`**, or the model's name — **PURE SCIENCE
ONLY**:

- **model formulation / architecture / trained parameters**;
- **training spec: data, features with FS coverage reports, loss, hyperparameters, seeds**;
- **evaluation: metrics, tables, uncertainty bands**;
- **conclusions to paper register**.

### The absolute content boundary

> **No agent names or roles. No docket, rung or charter references. No session or process
> narrative. No orchestration language. No internal paths.**
>
> **A reader must not be able to tell HOW, only WHAT and WHY.**

### Enforcement

- **SONNET cold-reader gate before any push**: the science stands alone; **a leakage-vocabulary
  grep plus a human-register read returns zero.**
- **HAIKU maintains the leakage vocabulary list.**
- **Nothing lands in Repo 2 except through a release gate Sanaa approves.**
- **History squashed release-by-release.**
- **DO NOT create or push Repo 2.** Recording the doctrine is the task; **creation is a Sanaa
  release decision.**

---

## Open actions

| # | Action | Owner, as ruled |
|---|---|---|
| 1 | **Select the canonical implementation paper for shelf D** (Mishra & Iaccarino lineage). Not selected in this document. | **FABLE** |
| 2 | **R2 candidate shortlist** — rank 3 model classes on criteria (a), (b), (c). Not started. | **FABLE** |
| 3 | **R3 — pick the model class**, as a docket decision with the shortlist memo. | **SANAA** |
| 4 | **Approve the internal-scoring phrasing** for external surfaces, or confirm leaderboard claims are dropped. | **SANAA** |
| 5 | **Repo 2 creation and every release into it.** | **SANAA** |

**Row 3 — CLOSED 2026-08-24.** Sanaa ratified R3 on 2026-08-24 (SpaRTA-class, TBNN fallback); the
row above is left standing and unedited, and this dated note beside it records its closure. See the
**RATIFICATION — 2026-08-24** block under Part 3 R3, `docs/closure/R2_SHORTLIST_MEMO.md`
Addendum 2026-08-24, and docket **D510**.

---

## What this document does not do

- **It draws no R2 shortlist**, and ranks no model class.
- **It makes no R3 pick.** R3 is Sanaa's decision, never the lab's.
- **It runs nothing** — no training, no feature-selection run, no scoring call.
- **It creates no repository** and pushes nothing. Repo 2 does not exist because this file was
  written.
- **It selects no canonical implementation paper for shelf D**; that is open action 1.
- **It adds no rule.** Where a sentence above is not a quotation of the ruling, it is a status
  annotation against `MANIFEST.md` or `PAPER_CATALOGUE.md`, and says so.
