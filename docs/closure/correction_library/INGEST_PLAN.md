# Closure-correction library — INGEST PLAN and GAP REGISTER

**STATUS: v0.1, 2026-09-04. ZERO COMPUTE — nothing here has been run, and no entry has yet been
written. This document is a plan and a register, not a result.** Authority: Sanaa `0910b664`.
Sequenced behind M6/CRM's first rungs; ingest builds as the F6 separated-flow cases come online.

Sources: two read-only survey lanes, 2026-09-04, plus the supervisor's own re-measurement of every
load-bearing claim repeated here. Where a claim is a lane's and was NOT re-measured, it says so.

---

## 1. THE FINDING THAT REDIRECTS HER FIRST TARGET

Sanaa's named first result is **"correction X recovers this flow where SST could not" on a
separated-flow case**, with F6 naming hump, periodic hills and duct. **Measured, those three are
not equally ready, and the hump — the one most likely to be reached for first — is the weakest.**

| Case | Correction literature we hold | Reference data | Correction installable today |
|---|---|---|---|
| **Square / rect. duct** | family (b) is the textbook fix; SST-QCRC challenge paper held | **DUCT at 8 AR/Re combos on disk**; Pinelli 2010 + Vinuesa 2014 title-verified | **YES, ZERO BUILD** — `ShihQuadraticKE`, `LienCubicKE` ship; `kOmegaSSTQCR` already built |
| **Periodic hills** | **9 title-verified papers** with substantive PH content (Xiao 26 hits, Wu2018 22, Schmelzer 8, Kaandorp 5) | `PH_Breuer`, `Parm_PH_29` on disk; Breuer 2009 held | **YES** — `kOmegaSSTSparta` already built |
| **NASA wall-mounted hump** | **"NASA hump" appears ONCE across all 66 sidecars, and it is a reference-list entry.** No held closure-correction paper validates on it, except via family (f) | `NASA_2DWMH` + evaluation points on disk; Greenblatt 2004 held | only via family (f) |

**RECOMMENDATION: the first certified result should target the SQUARE DUCT, not the hump.** Four
reasons, three of them measured on this box:

1. **The failure is QUALITATIVE, not quantitative.** A linear eddy-viscosity model cannot produce
   secondary flow of the second kind at all — the corner vortices require normal-stress anisotropy
   a linear stress-strain relation does not represent. So "recovers this flow where SST could not"
   is a **binary, demonstrable claim** rather than a percentage improvement that needs a band to
   interpret. Every other candidate makes the claim a matter of degree.
   **⚠ THIS ONE IS MY DOMAIN KNOWLEDGE, NOT A MEASUREMENT ON THIS BOX.** It is cheap to establish:
   one SST duct solve against the reference data already on disk. **That solve IS rung 1 of the
   ladder for this case**, so verifying my premise costs nothing that the ladder does not already
   owe. It is registered as an assumption to be tested, not a fact to be relied on.
2. **The correction needs no build.** `ShihQuadraticKE` and `LienCubicKE` ship with OpenFOAM 2606,
   and `kOmegaSSTQCR` is already compiled in `FOAM_USER_LIBBIN` on this box.
3. **The reference data is already here** — 8 aspect-ratio / Reynolds combinations.
4. **It is inside her own F6 list**, so this sequences within her instruction rather than against it.

**Periodic hills is the second target** — strongest literature coverage and SpaRTA already built.
**The hump runs through family (f)**: we hold the method papers of all four top leaderboard entries
plus the case data, but no classical correction validating on it. Reaching for the hump first means
reaching for the case with the thinnest correction literature in our holding.

---

## 2. GAP REGISTER — what the library cannot be built from, per family

Ingest **cannot be scoped to `docs/papers/closure/`**: families (f) and (g) live entirely in
adjacent folders. In-scope for ingest: `closure/`, `data_driven_rans/`, `benchmark_test_cases/`,
`turbulence_models/`, `uncertainty_quantification/`.

| Family | State | Verdict |
|---|---|---|
| (a) analytical / algebraic-stress | Pope 1975 held (the basis). **Gatski 1996 is a 77-byte sidecar for 77 pages** — a scan with no text layer, and it prints only the 2-D quadratic reduction | **CRIPPLED — root without trunk** |
| (b) functional / nonlinear EVM | SST-QCRC challenge paper only. Corpus-wide "quadratic constitutive" = **0 files** | **NEARLY EMPTY on paper — but see §3, the MODELS ship anyway** |
| (c) curvature and rotation | `Hellsten` 0 files, `SST-CC` 0, `Spalart-Shur` 2 (both passing citations) | **ABSOLUTE ZERO. Largest hole against her named families** |
| (d) separation-specific classical fixes | none held as hand-derived corrections | **EMPTY** |
| (e) data-informed | 16 sidecars hit "field inversion"; gaps already tracked as PENDING-MIT | **STRONG** |
| (f) closure-challenge corrections | **method papers of all four top leaderboard entries held and title-verified** | **COMPLETE for the current leaderboard** |
| (g) reference data | hump, hills, duct, rect-duct all held in `benchmark_test_cases/` | **COMPLETE for F6** |

### Retrieval register — NOT HELD, needed, for Sanaa's desk
Institutional pull is hers; §4 of the manifest is the existing channel (and is **14 outstanding,
not 16** — see Addendum 4). Priority order follows §1's recommendation.

**Priority 1, family (c), the absolute-zero hole:** Spalart & Shur 1997 (Aerosp. Sci. Tech.
1(5):297); Smirnov & Menter 2009 (J. Turbomach. 131:041010) — **this one IS SST-CC, the exact
option her family (c) names**; Shur et al. 2000 (AIAA J. 38(5):784, SARC); Hellsten 1998 (AIAA
98-2554); Wallin & Johansson 2002 (IJHFF 23:721); Arolla & Durbin 2013 (IJHFF 39:78).

**Priority 2, family (a):** Wallin & Johansson 2000 (JFM 403:89) — **the single most-cited absent
paper in our own corpus, 7 files cite it**; Gatski & Speziale 1993 (JFM 254:59, already PENDING-MIT
row 1); Speziale, Sarkar & Gatski 1991 (JFM 227:245, SSG); Girimaji 1996; Rodi 1976; Menter,
Garbaruk & Egorov 2012. **Plus a re-retrieval of Gatski 1996 with a text layer, or an OCR pass.**

**Priority 3, family (b):** Shih, Zhu & Lumley 1995 (CMAME 125:287) — **the paper behind the
`ShihQuadraticKE` that already ships**; Craft, Launder & Suga 1996 (IJHFF 17:108) — **behind
`LienCubicKE`**; Mompean et al. 1996 (Phys. Fluids 8:1856, duct secondary flow); Apsley &
Leschziner 1998. **Also: confirm whether `Spalart2000_strategies_turbulence_modelling.pdf` actually
contains the QCR2000 formulation — its sidecar shows 0 hits for "quadratic constitutive" and the
lane did not read the paper. DO NOT let an entry cite it as the QCR source until someone has.**

**Priority 4, family (d):** Durbin 1996 (IJHFF 17:89, stagnation-point limiter); Menter, Kuntz &
Langtry 2003; Wilcox 2008 (AIAA J. 46:2823); Rumsey et al. 1998; Bardina et al. 1997 (NASA
TM-110446).

**Priority 5, provenance for data already on our disk:** Xiao, Wu, Laizet & Duan 2020 (Comput.
Fluids 200:104431) — **the provenance paper for the `Parm_PH_29` data we already use and cannot
cite**; Rapp & Manhart 2011; Greenblatt et al. 2006; Gessner & Jones 1965; Bentaleb et al. 2012
(the CBFS reference); McConkey, Yee & Lien 2021 (curated dataset).

---

## 3. THE INSTALL SURFACE — measured, and it is better than the paper holding suggests

**20 incompressible RAS models ship with this OpenFOAM (api 2606) and need NO BUILD**, read two
independent ways that agree (source instantiation file, and the built library's symbol table).
Including, relevant to the thin families: **`ShihQuadraticKE`** and **`LienCubicKE`** (family (b),
nonlinear EVM), **`LRR`**, **`SSG`**, **`EBRSM`** (Reynolds-stress transport), **`GEKO`**.
**ABSENT and therefore a build item: any EARSM (no Wallin-Johansson), and EVERY curvature/rotation
correction — nothing ships, and this GEKO exposes no `Ccurv`.**

**So family (b) and family (a)-adjacent options are installable TODAY even though the papers are
thin.** The bottleneck for (b) is provenance, not capability — we can run the model and cannot yet
cite the paper that defines it. **An entry may not be `REGISTERED` on capability alone: the schema
requires the paper.** That is the correct order and it is why the retrieval register is priority 1
work rather than a nicety.

**Four user libraries are already built on this box**, model names read from the symbol table:
`kOmegaSSTCorrected`, `kOmegaSSTFrozen`, `kOmegaSSTSparta` (libspartaTurbulenceModels),
`kOmegaSSTFrozenV2`, `kOmegaSSTQCR`, `kOmegaSSTCorrectedFrozenK`. **A SpaRTA-class implementation
exists and is built. NO GP-based turbulence model exists anywhere on this box** — rung 4, the rung
Sanaa has made closure's own, is currently **capability-absent**, and that is an honest
`BLOCKED`-shaped fact to carry, not a gap to paper over.

### Two install-surface traps that go straight into the schema

1. **`GEKO` with `machineLearning true;` reads `Ck` and `Comega` as `volScalarField`s from the case
   time directory with `READ_IF_PRESENT`.** This is a spatially-varying, data-driven, in-the-
   equations correction installable **by dictionary plus a field file, with no compile** — a real
   asset. **But a missing or misnamed field SILENTLY BECOMES ZERO and the run completes looking
   like a plausible baseline.** That is exactly rule 3's planted-zero failure, built into a shipped
   model. **Any GEKO-ML entry must plant a non-zero `Ck`/`Comega` and demonstrate the solve moves
   before its result is believed.**
2. **`fvOptions` cannot modify the momentum equation's Reynolds-stress term** — it adds sources
   only. So anisotropy corrections (the `b_ij` / nonlinear-stress shape, i.e. SpaRTA and TBNN) are
   **NOT** installable by that route and require a compiled library. Only scalar-transport
   corrections (k/omega source terms) can use it. An entry claiming `fvOptions-source` for an
   anisotropy correction is wrong on its face and the schema should make that unwriteable.

---

## 4. INGEST ORDER

**Phase 0 (now, zero compute)** — schema frozen; flow-class vocabulary promoted (§5 of
ARCHITECTURE); retrieval register to Sanaa's desk; `MODEL.json`'s field vocabulary adopted as
`library.json`'s starting point rather than inventing a rival.
**Phase 1 (zero compute)** — `REGISTERED` entries for what we hold AND can install: family (f)'s
four leaderboard corrections, family (b)'s shipped models once their papers land, SpaRTA from the
existing `R4_sparta_build/MODEL.json`.
**Phase 2 (compute, behind M6/CRM)** — the reproduction gate, per entry, cheapest first: duct
family (b) before hills family (e). Each carries its own cost estimate under rule 12.
**Phase 3** — the first ladder record, on the duct, per §1.

---

## 5. WHAT THIS PLAN CANNOT SEE

- Whether `Spalart2000` contains QCR2000 — **unresolved, and no entry may cite it until read.**
- Whether the four built `.so` files still build against v2606, and whether the on-disk sources are
  the sources that produced them — **not verified; mtimes span Aug 1-22 and a rebuild is compute.**
- GEKO's k-equation ML branch was read by symmetry with the omega branch, **not line by line.**
- The flow-class negative (no controlled vocabulary exists) is a **search result over four file
  types and four phrase patterns, not a proof of absence** — a vocabulary filed under "regime" or
  "canonical case set" would not have been caught.
- **`docs/closure/LIBS_ASSERT_SWEEP.md` has NOT been read** and must be, before the `libs_route`
  field is frozen — it is the existing record of every `libs` call site and may already carry the
  exception list reconstructed from source.
- The 33 canonical closure PDFs were **not** independently re-title-page-verified; the manifest's
  recorded strings were relied on for those. Only the two Addendum-3 files were verified afresh.

---

## 6. CORRECTION TO §2 AND §5 OF THIS DOCUMENT, 2026-09-04 — I OVERSTATED WHAT WE HOLD ON THE LEADERBOARD

**Struck, quoted from §2:** ~~"(f) closure-challenge corrections | **method papers of all four top
leaderboard entries held and title-verified** | **COMPLETE for the current leaderboard**"~~ and from
§1's hump row: ~~"only via family (f)"~~ read as though family (f) were four usable corrections.

**What is actually true, measured by the supervisor with a live positive control.** The rank-1
paper we hold — `reissmann_fang_ooi_sandberg_gpem2025_2409.07369.pdf`, correctly retrieved and
title-page verified as *"Constraining Genetic Symbolic Regression via Semantic Backpropagation"* —
**contains no turbulence closure at all.** Over 83,859 extracted characters: `Reynolds` **0**,
`anisotrop` **0**, `eddy visc` **0**, `Navier` **0**, `turbulen` **0**. **The zero is evidence, not
a broken reader:** the same reader in the same invocation returns `Reynolds` **16** and `anisotrop`
**7** on Schmelzer. Its sections are Symbolic Regression, Semantic Backpropagation, and a
**Feynman-lectures** benchmark. It is a *symbolic-regression methods* paper; the turbulence
application is a different paper.

**McConkey's leaderboard cites rank 1 as [17, 18].** [17] is the held methods paper. **[18] is
Weatheritt & Sandberg 2016, JCP 325:22–37 — the stress–strain modification — and IT IS NOT HELD.**

**And the file that appears to be it is a different field entirely.**
`docs/papers/closure/_WRONG_RETRIEVALS/Weatheritt2016_evolutionary_rans.pdf` prints, on page 1,
*"On the Distinction of Functional and Quality Requirements in Practice"*, Eckhardt, Vogelsang &
Méndez Fernández, arXiv:1611.08830 **[cs.SE]** — a software-engineering requirements survey.
**Right author string, right year, right-looking filename, wrong discipline. L-144 in its purest
form**, and it is why "we hold the top four" was wrong: the corpus contains a plausible-looking
file for the missing half.

**Consequences, and none of them are cosmetic:**
1. **Family (f) is NOT complete.** Rank 1's closure half is missing. **Retrieval priority is raised:
   Weatheritt & Sandberg 2016 (JCP 325:22–37) joins Priority 1 of §2's register.**
2. **The rank-1 entry is BLOCKED, not written.** `equation_form`, `claimed_effect`,
   `validation_cases`, `install_stanza` and `model_type_name` are all unsourceable from [17];
   `validation_cases` has no honest value in the §3 vocabulary at all, because [17]'s validation
   set is **Feynman equations**. Filed as `ENTRY_BLOCKED_f_gpsr_reissmann2025.md`, one level above
   `entries/` so the builder cannot parse it into the library. **An entry was not made to fit.**
3. **The hump gets weaker again, not stronger.** §1 already measured the hump as the thinnest of the
   three F6 cases; its only route was family (f), and family (f) has now lost its top entry.
   **The duct-first recommendation is strengthened by this correction, which is exactly why I am
   recording the correction rather than the convenience.**

## 7. TWO §5 ITEMS DISCHARGED — AND THE DUCT PREMISE IS NOW CITED RATHER THAN ASSERTED

**Struck from §5:** ~~"Whether `Spalart2000` contains QCR2000 — unresolved, and no entry may cite
it until read."~~ **It does.** Verified by the supervisor: the nonlinear constitutive relation is
carried as an unnumbered displayed equation, printed **p. 253**, with `cnl1 = 0.3` and a
square-channel demonstration. **The acronym "QCR" never appears** — the paper's own phrase is
*"nonlinear constitutive relation"* — which is why the sidecar search for "quadratic constitutive"
returned zero, **and why that zero was not absence.** The prohibition is lifted; entries may cite it.

**And this converts §1's reason 1 from my domain knowledge into a citation.** §1 flagged, in
capitals, that the qualitative duct premise was **MY DOMAIN KNOWLEDGE, NOT A MEASUREMENT ON THIS
BOX**. Spalart states it himself, p. 253, verbatim: with the nonlinear term *"flow is induced
towards the corners, and the skin friction is much closer to experiment (Gessner et al., 1991)."*
**It remains an untested premise ON THIS BOX — a citation is not a measurement, and rung 1 still
owes the SST duct solve — but it is no longer uncited.**

**Its contraindication, quoted from the same page, and it goes straight into the entry:**
*"However, other flows such as 3D wall jets have led to negative results (A.N. Secundov, personal
communication, 1999)."* **A correction library without contraindications is a footgun; this is what
one looks like when the author supplies it.**

## 8. THE TRAP THAT WOULD HAVE MANUFACTURED A FALSE LADDER RESULT

**`kOmegaSSTQCR` is built on this box and its symbol is registered — and it is NOT SST-QCRC.** It
implements the constitutive relation only, **not the field-inversion ω correction that is the "C"
in QCRC** and that produced the challenge result. **Running it and recording the outcome as
SST-QCRC would report a ladder verdict for a model that never ran** — ARCHITECTURE §0's failure
(ii), reached not by a bug but by a plausible name match. The entry therefore carries
`model_type_name: none`.

**The same shape applies to SpaRTA:** `kOmegaSSTSparta` is built, but carries **this lab's own
R4-discovered coefficients** (`R4_sparta_build/MODEL.json`, frozen 2026-08-22), **not Schmelzer's**.
Running it cannot advance the Schmelzer entry toward `REPRODUCED`.

> **THE RULE THIS GENERALISES TO: a built library whose NAME matches an entry is not that entry's
> implementation until its EQUATIONS and COEFFICIENTS are checked against the entry's own paper.
> The symbol table proves a model is loadable; it proves nothing about which model it is.**
