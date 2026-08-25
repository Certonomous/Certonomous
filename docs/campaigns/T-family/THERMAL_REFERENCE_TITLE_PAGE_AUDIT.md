# Thermal reference audit — rule-15 title-page verification, sidecar census, and four rung findings

**Heat-transfer lane, 2026-08-25.** CONSOLIDATION WEEK assignment §5.
**ZERO core-minutes. No solver, no mesher, no case directory, no MPI rank.
Nothing was sent, filed, uploaded or acquired from outside the box.**

No rung tier and no rung verdict is edited by this document. It reports; the
supervisor rules.

---

## LANDING NOTE — added at commit time by a later heat-transfer lane, 2026-08-25

**This document was drafted uncommitted and sat outside HEAD; two lanes declined
to land it. It is landed here with corrections made BEFORE landing, and nothing
else in it altered.** The three title-page readings in §2 are the drafting lane's
own and stand exactly as written.

1. **The Tian row was FALSE and is corrected.** The draft listed
   `tian_karayiannis_2000_ijhmt_43.pdf` as `NOT VERIFIED` and as *"has never been
   title-page verified"*. A committed record dated 2026-08-24 says otherwise:
   `docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md:20`
   reads *"Title pages verified | 3 of 3, plus `tian_karayiannis_2000_ijhmt_43.pdf`
   as a fourth"*, and `:79`–`:92` of that same file carry the printed title page
   — *Low turbulence natural convection in an air filled square cavity, **Part I:
   the thermal and fluid flow fields***, IJHMT **43** (2000) 849–866, Y.S. Tian
   and T.G. Karayiannis. **That line was read at HEAD by the landing lane before
   this correction was written.** Tian is **VERIFIED**.
2. **The counts are reconciled** to `docs/campaigns/T-family/SATURATION_AUDIT_2026-08-25.md`
   (committed, `f782d9bc`), whose lane read six rendered title pages on
   2026-08-25. Territory verification stands at **10 of 19 VERIFIED, 9 NOT
   VERIFIED, 0 FAILED** — not the 6 / 13 / 0 this document was drafted with. No
   title page was re-rendered to land this correction; repeating finished work
   wastes the box.
3. **The two remaining load-bearing gaps are named OPEN**, in §1.4 and again in
   §7: `vierendeels_merci_dick_2002_wit_afm02` and
   `zou_zhao_chen_2018_building_simulation`. **Neither was read by the landing
   lane and neither is verified by this document.**
4. **Two things the record must not omit are added:** the ERCOFTAC-079
   two-artifact distinction is sharpened in §2.2, and §2.4 is new — rule 15
   vindicated twice inside this very set, by PDF metadata that would have named a
   Word filename as a title and `pvn` as an author.

**Nothing else was touched.** No gate, threshold, band, cap, label, tier or
verdict is edited by this landing; no paper was fetched, acquired or searched for
outside the box.

---

## 0. The headline, stated before the evidence

1. **The previous lane's narrow claim was TRUE and is now DISCHARGED.** Ampofo,
   Betts/ERCOFTAC 079 and Nielsen/Rong/Olmedo carried **no** rule-15 title-page
   verification record. This lane opened all three title pages. **All three
   VERIFY.** Nothing FAILED.
2. **The previous lane's broad claim was FALSE and is corrected here.** "Only
   three PDFs in the whole repository carry a title-page verification record" is
   wrong — §6 names FIVE counter-examples, three of them committed within two
   days, and **one of them inside this very territory** — the Tian record this
   document was drafted not knowing about. (The lane marked its statement
   `VERIFY`, so this is a correction, not an impeachment.)
3. **T12's block is NOT stale. It stands, on both limbs, and the "highest-value
   zero-compute action on the board" unblocks nothing.** Nielsen 2010 verifies as
   a document and **does not carry the reference data**. §3.
4. **Blay 1992 is genuinely absent**, under any filename, by content search with a
   live planted control. **K0d's §0 ceiling stands: V and G reachable, P NO, not
   `HOLDS`.** §4.
5. **T2 is mis-tiered, confirmed.** Zukauskas is nowhere on disk in any spelling.
   **T2 behaves as ACQUIRE, not FORMULA.** §5.
6. **Nine of the nineteen thermal PDFs still carry no rule-15 record** — and
   **two of them are load-bearing today**: `vierendeels_merci_dick_2002`, which
   carries K0c's stated applicability limit, and `zou_zhao_chen_2018`, which
   supplies K0d's case inside a frozen re-registration. §1.4. This is the finding
   the family should be least comfortable with. *(Drafted as "thirteen";
   corrected at landing — see the LANDING NOTE and §1.3.)*

---

## 1. CENSUS

### 1.1 Instrument, stated because an absence claim from a blind instrument is worthless

`grep -r` in this repository honours ignore files and is blind to gitignored
archives. **No claim below rests on it.** Every sweep is
`find <roots> -type f … -print0 | xargs -0 grep …`, which honours nothing, over
four roots: `/home/ubuntu/Certonomous`, `/home/ubuntu/closure-data`,
`/home/ubuntu/closure-challenge-benchmark`, `/home/ubuntu/certonomous-runs`.

**Every zero below is reported beside a planted control on the same instrument.**
A zero from a reader not shown able to see a non-zero is not evidence (rule 3).

**One instrument defect, disclosed rather than buried.** This lane's first Blay
sweep used the bare token `blay` and returned 30+ hits. Every one was the word
**"su-blay-er"**. The first Zukauskas sweep used the flag cluster `grep -lieE`,
in which `-e` consumes the rest of the cluster, so **the pattern was literally
`E`** and matched nearly every file. Both instruments were rebuilt with word
boundaries and separated flags, and **only the rebuilt results are reported.**

### 1.2 Sidecars — `FILING_CHARTER` R9 is clean in all three folders

| folder | PDFs | sidecars | R9 violations | smallest sidecar (non-whitespace chars) |
| --- | ---: | ---: | ---: | --- |
| `forced_convection_heat_transfer` | 3 | 3 | 0 | 32,787 (bahrami) |
| `buoyant_natural_convection` | 9 | 9 | 0 | 12,023 (vierendeels) |
| `data_center_indoor_airflow` | 7 | 7 | 0 | 11,776 (nielsen) |
| **total** | **19** | **19** | **0** | — |

**All 19 sidecars carry real text.** Content was measured, not assumed — the
Meinders trap (a 281-byte sidecar of pure form-feeds that satisfied R9 while
holding zero characters) does not recur in these folders. The smallest is
Nielsen at 11,776 non-whitespace characters, which is a genuine 9-page paper.

### 1.3 Title-page verification state — three states, never merged

`VERIFIED` = a record exists naming what the title page says.
`NOT VERIFIED` = **no record; the check was never made.**
`FAILED` = a record exists and the title page contradicts the filename's claim.

**Corrected at landing.** This table was drafted `3 → 6`. **Both figures were
wrong.** The baseline omitted `tian_karayiannis_2000_ijhmt_43`, already title-page
verified in a committed record
(`docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md:20`, `:79`),
and three further title pages were read the same day by the lane that wrote
`docs/campaigns/T-family/SATURATION_AUDIT_2026-08-25.md` (committed, `f782d9bc`).

| state | at HEAD before 2026-08-25 | after this document's three reads | **territory state at landing** |
| --- | ---: | ---: | ---: |
| **VERIFIED** | 4 | 7 | **10** |
| **NOT VERIFIED** | 15 | 12 | **9** |
| **FAILED** | 0 | 0 | **0** |
| total territory PDFs | 19 | 19 | **19** |

**No thermal PDF has ever FAILED rule 15 — 0 of 19, across ten now read.** A
check never made is recorded as `NOT VERIFIED` throughout and is never written up
as a clean result.

**VERIFIED (10):**

| paper | record | by |
| --- | --- | --- |
| `bahrami_2005_nasa_tm_212841` | `docs/papers/forced_convection_heat_transfer/SIDECAR_VERIFICATION_2026-08-25.md` §2.1 | prior lane |
| `narumanchi_hassani_bharathan_2005_nrel_tp540_38787` | same, §2.2 | prior lane |
| `meinders_1998_tudelft_thesis_wall_mounted_cubes` | same, §2.3 (by eye; image-only scan) | prior lane |
| `tian_karayiannis_2000_ijhmt_43` | `docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md:20`, `:79`, `:607` — **Part I: the thermal and fluid flow fields**, IJHMT 43 (2000) 849–866; re-read at `SATURATION_AUDIT_2026-08-25.md` §4.3 | prior lane, 2026-08-24 |
| `ampofo_karayiannis_2003_ijhmt_46` | **§2.1 of this document** | this lane |
| `betts_bokhari_2000_ijhff_21` | **§2.2 of this document** | this lane |
| `nielsen_rong_olmedo_2010_clima_annex20` | **§2.3 of this document** | this lane |
| `gjesdal_wasberg_andreassen_2003_physics0305049` | `docs/campaigns/T-family/SATURATION_AUDIT_2026-08-25.md` §4.4 — *Spectral element simulations of buoyancy-driven flow*, arXiv:physics/0305049v1 | concurrent lane, same day |
| `wibron_ljung_lundstrom_2018_en11030644` | same, §4.4 — *Energies* **2018**, *11*, 644 | concurrent lane, same day |
| `han_xie_2019_1903.09506` | same, §4.4 — arXiv:1903.09506v1 | concurrent lane, same day |

**Both papers this document drafted as load-bearing rule-15 gaps are closed.**
`tian_karayiannis_2000_ijhmt_43` was never a gap at all — the check had been made
and committed a day earlier. `wibron_ljung_lundstrom_2018_en11030644` — the PDF
K2c-A digitised Figs 6a/6b and 7a–7e from, on a matching sha256 that rule 15 says
is **not** verification — was read on 2026-08-25 and **VERIFIES**. **Neither is
open.** The gaps that remain open are a different pair, and they are §1.4's first
two rows.

### 1.4 NOT VERIFIED (9) — and TWO OF THEM ARE OPEN AND LOAD-BEARING

| paper | folder | exposure |
| --- | --- | --- |
| **`vierendeels_merci_dick_2002_wit_afm02`** | buoyant | **OPEN. LOAD-BEARING.** `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md:228` cites it *"Table 1, READ IN FULL"* as the authority for **K0c's stated applicability limit** — Nu 8.687 at Ra 1e6 with epsilon = 0.6, a 1.3 % shift from Boussinesq at identical Ra. **A graded rung's stated limit of applicability rests on a document nobody in this lab has opened the title page of.** One reading at zero core-minutes; **not done here** |
| **`zou_zhao_chen_2018_building_simulation`** | data-centre | **OPEN. LOAD-BEARING.** `K0d_REREGISTRATION.md:174-187` records it as one of two secondaries that **SUPPLY K0d'S CASE**, inside a **frozen** re-registration. It may never supply a graded reference value — the re-registration says so explicitly — but the case geometry is read from it. One reading at zero core-minutes; **not done here** |
| `sadighi_2020_particles_heating` | buoyant | secondary |
| `xu_chen_2000_indoor_air_two_layer` | buoyant | secondary |
| `zhang_chen_2000_les_indoor` | buoyant | secondary |
| `hamann_klein_2012_osti_1044604` | data-centre | secondary |
| `kayne_agarwal_2013_mixed_convection` | data-centre | **named as a K0d Blay secondary** (`THERMAL_SATURATION_QUEUE.md:378`) — report-only, so it can never supply P, but it is cited |
| `vangilder_schmidt_2005_ipack` | data-centre | secondary |
| `wibron_ljung_lundstrom_2019_en12081473` | data-centre | secondary |

**Stated at full strength, because this is the unflattering half.** Seven of the
nine are secondaries and carry little weight. **Two are not**, and they are the
two named first above. Each is one reading at zero core-minutes to settle.
**Neither is settled by this document, and neither was read by the landing lane
— they are OPEN, and the supervisor schedules them.**

**Struck at landing:** rows for `tian_karayiannis_2000_ijhmt_43`,
`wibron_ljung_lundstrom_2018_en11030644`,
`gjesdal_wasberg_andreassen_2003_physics0305049` and `han_xie_2019_1903.09506`
stood in this table when it was drafted. ~~All four `NOT VERIFIED`.~~ **All four
are VERIFIED** — §1.3. Sources: `PAPER_INTAKE_2026-08-24.md:20` for Tian;
`docs/campaigns/T-family/SATURATION_AUDIT_2026-08-25.md` (`f782d9bc`) §4.3–§4.4
for the other three.
### 1.5 One stale line found in passing, reported not repaired

`docs/campaigns/F14-cooling-ladder/reference-data/MANIFEST.md`, the
`betts_bokhari/` block, records the publication of record and then adds
*"paper itself paywalled, Unpaywall `is_oa: false`, checked 2026-08-17"*. **The
paper reached this box on 2026-08-18 and is now held and verified** (§2.2). The
line was true when written and reads today as though the paper is not held. **The
22 `.dat` files are untouched by this and their provenance is unaffected.** Not
edited by this lane — it is a frozen reference manifest.

---

## 2. THE THREE TITLE PAGES, READ

Method: the printed first page of each PDF was **read as a rendered page**, which
is what a human reader sees. The `.txt` sidecar was used only as secondary
corroboration, never as the primary evidence. sha256 is recorded as an
identifier, **never as the verification** — rule 15 is explicit that a manifest
can be internally consistent and externally false.

### 2.1 `ampofo_karayiannis_2003_ijhmt_46.pdf` — **VERIFIED**

- sha256 `c193d79e3eb8cba5d1fd6af085c3a8c4c9497df80f90292287282694ed64ffaf`, 22 pages
- **Title as printed:** *Experimental benchmark data for turbulent natural convection in an air filled square cavity*
- **Authors as printed:** F. Ampofo, T.G. Karayiannis (corresponding; tel. +44-207-815-7628, karayitg@sbu.ac.uk)
- **Affiliation as printed:** Division of Environmental, Energy and Building Services Engineering, Faculty of Engineering, South Bank University, 103 Borough Road, London SE1 0AA, UK
- **Journal as printed:** *International Journal of Heat and Mass Transfer* **46** (2003) 3551–3572; Pergamon / Elsevier; doi `10.1016/S0017-9310(03)00147-9`
- **Dates as printed:** received 11 September 2002; received in revised form 19 March 2003
- **Abstract, as printed:** cavity 0.75 m high × 0.75 m wide × 1.5 m deep giving 2D flow; hot and cold walls isothermal at **50 and 10 °C**; **Ra = 1.58 × 10⁹**; local and average Nusselt numbers, wall shear stress, turbulent kinetic energy and temperature-variance dissipation rate all presented

**Filename check:** `ampofo` / `karayiannis` / `2003` / `ijhmt` / `46` — **every
token matches the printed page.** **Citation check:** the citing rungs (K0c,
K0cP/Q/R/S/X) call it the square-cavity benchmark; the printed title says
*square cavity* and the printed abstract says *benchmark data*. **No
contradiction. Nothing to report as a major finding.**

### 2.2 `betts_bokhari_2000_ijhff_21.pdf` — **VERIFIED**, with one precision the citation elides

- sha256 `905cce61e84bc485b086f9215277fd94bf823f3ffc12453084ab580423baeb94`, 9 pages
- **Title as printed:** *Experiments on turbulent natural convection in an enclosed tall cavity*
- **Authors as printed:** P.L. Betts (corresponding), I.H. Bokhari
- **Affiliation as printed:** Department of Mechanical Engineering, UMIST, PO Box 88, Manchester M60 1QD, UK. Bokhari's present address printed as Nuclear Engineering Division, Pakistan Institute of Nuclear Science and Technology, P.O. Nilore, Islamabad, Pakistan
- **Journal as printed:** *International Journal of Heat and Fluid Flow* **21** (2000) 675–683; Elsevier; PII `S0142-727X(00)00033-3`
- **Dates as printed:** received 29 June 1999; accepted 10 April 2000
- **Abstract, as printed:** cavity **2.18 m high × 0.076 m wide × 0.52 m deep**; plate temperature differentials **19.6 °C and 39.9 °C**; **Ra based on width 0.86 × 10⁶ and 1.43 × 10⁶**; partially conducting top and bottom walls with outer guard channels

**Filename check:** `betts` / `bokhari` / `2000` / `ijhff` / `21` — **every token
matches.** Geometry and both Rayleigh numbers match `MANIFEST.md`'s `lo`/`hi`
description exactly (`dT = 19.6 C` / `39.9 C`).

**The precision, and it is a precision rather than a defect.** The citation in
this family is *"Betts / ERCOFTAC case 079"*. **The title page carries no
"ERCOFTAC" and no "079".** Case 079 is the ERCOFTAC Classic Collection's label
for the experiment, applied by the database, not printed on the paper. So the
citation names **two artifacts, not one**:

| artifact | what it is | how it is verified |
| --- | --- | --- |
| `betts_bokhari_2000_ijhff_21.pdf` | the journal paper | **rule 15, title page, VERIFIED here** |
| `…/reference-data/betts_bokhari/*.dat`, 22 files | a byte-identical subset of the ERCOFTAC Case 079 archive | archive sha256 `4cd931c0c13a0ed5f898c39d94ea9f3b2ccd5dfc9cec75c00e37a818d7906dde` + fetch record in `MANIFEST.md`. **Not a paper — rule 15's title-page test cannot be applied to it at all** |

**Both check out, and the paper corroborates the archive**: the paper's printed
ΔT values are the archive's own `lo`/`hi` split. **This is not a title-page
contradiction and is not reported as one.** It is recorded so that nobody later
reads "ERCOFTAC 079 is rule-15 verified" and believes a data archive was
title-page checked, which is not a thing that can be done to a data archive.

### 2.3 `nielsen_rong_olmedo_2010_clima_annex20.pdf` — **VERIFIED as a document**

- sha256 `a9e9b7346361d979441fd305817652b507bde18c4c1757f0ec6536140e18b7c1`, 9 pages
- **Page 1 is a bare cover leaf**, printed centre-page, in this order:
  - **Authors as printed:** Peter V. Nielsen, Li Rong and Inés Olmedo
  - **Title as printed:** *The IEA Annex 20 Two-Dimensional Benchmark Test for CFD Predictions*
  - **ISBN as printed:** 978-975-6907-14-6
  - **Venue as printed:** Clima 2010, 10ᵗʰ REHVA World Congress
- **Page 2 repeats the title with affiliations as printed:** ¹Aalborg University, Denmark; ²Córdoba University, Spain; corresponding email `pvn@civil.aau.dk`
- **Year:** printed only as part of *"Clima 2010"*. There is no standalone date line. Recorded exactly as printed.

**Filename check:** `nielsen` / `rong` / `olmedo` / `2010` / `clima` / `annex20` —
**every one of the six tokens matches the printed page.** **No contradiction
between the title page and the filename or the citation.**

### 2.4 RULE 15 VINDICATED TWICE INSIDE THIS VERY SET — added at landing

**A metadata-built manifest would have got two of these three papers wrong**, and
that is L-144's exact failure mode caught inside this team's own corpus. The
embedded PDF metadata reads:

| file | metadata `Title` | metadata `Author` |
| --- | --- | --- |
| `nielsen_rong_olmedo_2010_clima_annex20.pdf` | `Microsoft Word - 100128 Full paper.doc` | `pvn` |
| `ampofo_karayiannis_2003_ijhmt_46.pdf` | `doi:10.1016/S0017-9310(03)00147-9` | *(absent)* |

**A manifest built from metadata would have recorded a word-processor filename as
the Nielsen paper's title and `pvn` as its author, and would have recorded the
Ampofo paper as having no author at all.** Both printed title pages say something
entirely different — §2.1 and §2.3 above, read as rendered pages. **The rendered
page is the paper.** This is precisely why rule 15 forbids verification by file
type, filename or hash: a manifest can be internally consistent and externally
false.

Measured and recorded at `docs/campaigns/T-family/SATURATION_AUDIT_2026-08-25.md`
§4.6 (committed, `f782d9bc`); reproduced here because a reader of this audit
should not have to find it elsewhere. **§6 below records the same failure mode a
third time, outside this territory** — the Greenblatt PDF's metadata author reads
`Administrator`.

---

## 3. T12 — SETTLED, AND THE ANSWER IS NO

**Question put to this lane:** does T12's primary exist and verify, yes or no?

**Answer: NO. The primary does not exist on this box. T12's BLOCKED record is
NOT stale — it stands, on both the isothermal and the nonisothermal limb.**

`THERMAL_SATURATION_QUEUE.md` §B-6 ranks this **"rank 1 among zero-compute
actions"** and **"the highest-value zero-compute action on the board"**, on the
hypothesis that if the title page verified, spine position 4 would move from
ACQUIRE to armable. **The title page verified. The hypothesis is still refuted**,
because the block was never the title page.

### 3.1 The paper is a pointer to the data, not the data

Read page by page, all 9 pages. **The document contains no table of any kind and
no tabulated measurement.** Every measured quantity appears only as **plotted
symbols** in Figures 4, 5 and 6; Figures 8, 9 and 10 are pure CFD with no
measurements at all. The paper states its own architecture on page 3, printed:

> *"The benchmark is located together with three other benchmarks on the web
> page: **www.cfd-benchmarks.com**"*

and in the SUMMARY on page 2: *"The benchmark is defined on a web page."* **The
data lives off this box, and obtaining it is a fetch, which is Sanaa's alone
(rules 7 and 8). This lane attempted nothing.**

### 3.2 The measurement primaries it points at — none held

From the printed reference list (page 9), the sources of the actual measurements:

| ref | source as printed | on disk? |
| --- | --- | --- |
| [1] | Nielsen, P V. 1990. *Specification of a Two-Dimensional Test Case*, Aalborg University, IEA Annex 20 | **NO** |
| [2] | Restivo, A M. 1979. *Turbulent Flow in Ventilated Rooms*, PhD thesis, Imperial College, London | **NO** |
| [3] | Nielsen, P V. 1974. *Strømningsforhold i luftkonditionerede lokaler*, PhD thesis, Technical University of Denmark | **NO** |
| [4] | Schwenke, H. 1975. *Über das Verhalten ebener horizontaler Zuluftstrahlen im begrenzten Raum*, Luft- und Kältetechnik, Nr. 5, Dresden | **NO** — already recorded `NOT OBTAINED` |

### 3.3 The sentence the queue leaned on describes the benchmark, not this paper

`THERMAL_SATURATION_QUEUE.md:316-318` quotes the SUMMARY: *"Laser-Doppler
measurements and hot-wire measurements are given for comparison with the obtained
CFD predictions both for isothermal flow and for nonisothermal flow."*

**That sentence is true of the benchmark. It is not a description of this
document's contents.** Reading the printed pages: **there is no nonisothermal
figure anywhere in the paper.** Figure 3 shows *"Position of measurement points
for temperature distribution in the benchmark test"* — the **positions** a4, a3,
a2, a1, **not their values**. Page 3 states plainly that the nonisothermal case
2D2's *"measurements are based on Scwenke's experiments [4]"* — i.e. Schwenke
1975, which is already `NOT OBTAINED`.

**This is exactly the failure rule 15 exists to name, one level up:** the queue's
reading was internally consistent and externally wrong, because it was taken from
a sidecar's front matter rather than from the pages.

### 3.4 No stated uncertainty — measured, with a planted control

A graded row needs a stated uncertainty. **The paper states none.**

| sweep | instrument | result |
| --- | --- | --- |
| `uncertain` \| `accuracy` \| `±` on the Nielsen sidecar | `grep -c -i` | **0** |
| **planted control:** `uncertain` on the Narumanchi sidecar, **same binary, same flags** | `grep -c -i` | **2** |

**The reader was shown able to see a non-zero before its zero was believed.**

### 3.5 What this means for the record

- The **rule-15 gap** on Nielsen 2010 is **closed** — the document is VERIFIED.
- The **T12 block** is **unchanged**: `ACQUIRE`, and the index's *"over $25"* cost
  note is untouched by anything here.
- The saturation queue's §3 cell **"nonisothermal P NO; isothermal `VERIFY`"**
  now resolves, on this lane's reading, to **isothermal P NO as well** — the
  isothermal data are Nielsen 1990 / Restivo 1979, neither held. **That cell is
  the supervisor's to move. This lane does not move it.**
- **The queue's ranking should come down.** B-6 is currently rank 1 of the
  zero-compute actions and item 5 of the next-actions list. It is now spent, and
  it unblocked nothing. Reported so the board does not keep paying attention to a
  door that is shut.

---

## 4. K0d's Blay 1992 — GENUINELY ABSENT

**`BLOCKED` on the primary. Confirmed from disk. K0d's §0 ceiling stands: V and G
are reachable, P is NO, and K0d therefore cannot be `HOLDS`.**

**No acquisition was attempted and none is proposed here.** Obtaining Blay 1992 is
a send and is Sanaa's alone (rule 7); the repository is permanently private
(rule 8). `K0d_PREREGISTRATION.md:17-18` already records *"Sanaa has purchased the
ASME volume carrying Blay 1992; the PDF is not yet on disk"* — **still true as of
this reading.**

### 4.1 Searched by content, not only by name

| check | instrument | result |
| --- | --- | --- |
| **filename**, four roots, non-ignoring | `find … \| grep -iE '(^\|[^a-z])blay([^a-z]\|$)'` | **0 files** |
| **content**, token `\bBlay\b`, four roots, `.txt`/`.md`/`.dat`/`.csv` | `find … -print0 \| xargs -0 grep -lE` | **25 files** |
| **front matter** — `\bBlay\b` in the first 30 lines (the title/author zone) of every `.txt` in the repository | `head -30 \| grep -qE` | **0 files** |
| **planted control**, identical instrument, token `\bAmpofo\b` | `find … \| xargs -0 grep -lE` | **48 files** |

**The 25 content hits are all citations of Blay inside other documents, never Blay
itself.** 17 are lab prose (K0d records, `DOCKET.md`, `LAB_STATE.md`,
`THERMAL_CAPABILITY_STATE.md`, `VALIDATION_INVENTORY.md`, the F14 files,
`THERMAL_K0_*`); 8 are reference lists and body text inside other papers. The two
already-named secondaries read, as printed in their sidecars:

- `oulghelou_beghein_allery_2020_2009.06724.txt:1046` — *"[31] D. Blay, S. Mergui,
  and C. Niculae, 'Confined turbulent mixed convection in the presence of a
  horizontal buoyant wall jet,' ASME Heat Transfer Division, vol. 213, pp. 65–…"*
- `kayne_agarwal_2013_mixed_convection.txt:921` — *"[8] Blay, D., Mergui, S. and
  Niculae, C., 1992, 'Confined Turbulent Mixed Convection in the…'"*

**Both are citations of an absent document. Both remain REPORT-ONLY and neither
can ever supply P** — a digitised secondary is one tier below a primary.

### 4.2 The honest caveat on this absence claim

**76 PDFs in this repository have no `.txt` sidecar and are therefore invisible to
a content grep.** All 76 were enumerated and every one is identified by name:
mission-output and B-52 certificates, `UserGuide.pdf` / `ProgrammersGuide.pdf`,
the closure `_WRONG_RETRIEVALS/` and `_DUPLICATES/` sets, Menter, Pope, Spalart,
Gatski, `kussoy_horstman_TM101075.pdf`, `urop_summer_2026.pdf`. **None is a
candidate for a 1992 French ASME HTD-213 conference paper.**

**That exclusion is by filename, and rule 15 says a filename is not
verification.** It is stated as a caveat, not as proof. It would take rendering
76 title pages to close it absolutely, and this lane did not do that. **The
combination — zero filename hits, zero front-matter hits across every sidecar,
and 76 named non-candidates — supports `NOT OBTAINED` and does not prove it to
the standard rule 15 sets for a positive identification.**

---

## 5. T2 / Zukauskas — MIS-TIERING CONFIRMED

**The correlation is nowhere on disk, in any spelling. T2's recorded tier
`FORMULA` is over-claimed; T2 behaves as `ACQUIRE`.**

**The index tier is NOT edited by this lane.** An over-claimed tier is the
supervisor's ruling to make.

### 5.1 The sweep, with two planted controls and the non-ASCII case handled

| sweep | instrument | result |
| --- | --- | --- |
| `zukausk` \| `zhukausk`, case-insensitive, four roots, non-ignoring, `.txt`/`.md`/`.dat`/`.csv`/`.py`/`.json` | `find … -print0 \| xargs -0 grep -l -i -E` | **4 files** |
| literal `Žukausk` / `žukausk` / `Zukausk` / `ZUKAUSK` — because `-i` does **not** fold a non-ASCII `Ž` | `grep -l -e … -e …` | **the same 4 files, no others** |
| **restricted to the 96 sidecars in `docs/papers/`** | same | **0** |
| **planted control 1:** `Gnielinski`, same instrument, four roots | `grep -l -i -E` | **13 files** |
| **planted control 2:** `Nusselt`, same instrument, **the 96-sidecar corpus only** | `grep -l -i -E` | **13 sidecars** |
| **planted control 3** for the non-ASCII reader: `Hanjali` (a diacritic name known present) | `grep -l -e` | **4 files** |
| `tube bank` \| `tube bundle` across the 96 sidecars | `grep -l -i -E` | **1** — the Meinders thesis, incidental |

**The reader was shown able to see a non-zero on the whole corpus (13), on the
sidecar corpus specifically (13), and on the non-ASCII path (4), before any zero
was believed.**

**The 4 hits are all lab prose — the lab talking about the missing correlation,
never the correlation itself:** `docs/LAB_STATE.md`,
`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md`,
`docs/campaigns/T-family/THERMAL_SATURATION_QUEUE.md`,
`docs/campaigns/T-family/T_FAMILY_INDEX.md`.

### 5.2 Why this is a tier defect and not a paperwork nicety

`T_FAMILY_INDEX.md` §1 defines `FORMULA` as *"a published correlation stated as an
equation; reproducible from the formula; **no paper needed to evaluate it**,
though its validity range must be cited"*, and T2's own state cell requires *"the
correlation's **stated validity range** cited, not just its algebra."*

**Neither half is on disk.** Not the algebra, not the range. **Algebra with no
stated validity range arms no band** — the identical defect that blocks T1a/K0e,
where a held and verified correlation still cannot arm a band on its own.

**Recommended correction, for the supervisor to rule on:** T2's tier moves
`FORMULA` → `ACQUIRE` until a source stating the Zukauskas correlation **and its
validity range** is obtained **and title-page verified**. Under the H-5 completion
order T2 sits after T4, T6 and T7, so this changes no schedule — **it changes
what the index promises.** Recording a rung as needing no acquisition when it
needs one is precisely the class of error §1 of the index was written to catch,
running in the opposite direction: **the index found a rung that was cheaper than
recorded (T1c), and this one is dearer than recorded.**

---

## 6. THE OVER-BROAD CLAIM, CORRECTED

**Struck** — `THERMAL_SATURATION_QUEUE.md:390-393` and `:322-325`, quoted as they
stand and left standing there so a reader can see what changed:

> ~~"Only **three** PDFs in this repository carry a title-page verification record
> on disk, all three in `forced_convection_heat_transfer`."~~
>
> ~~"The only two title-page verification records in this repository are
> `PAPER_INTAKE_2026-08-24.md` and `SIDECAR_VERIFICATION_2026-08-25.md`."~~

**Restated, from a repo-wide non-ignoring sweep for `title.page (verifi|VERIFIED|read)`:**

> **The narrow claim was true; the repo-wide claim was false.** Ampofo, Betts and
> Nielsen carried no record — that half is correct and is discharged by §2. But
> title-page verification records exist elsewhere in the repository, including:
>
> - **Roshko (1954), NACA Report 1191** — `docs/EXTERNAL_REFERENT_AUDIT.md:930`,
>   *"title-page verified (L-144), from NTRS 19930092207"*, and reproduced by
>   rendering page 1 in `verification/campaign/F5a_MMS_SCOPING_MEMO.md`
> - **Greenblatt et al., AIAA-2004-2220** — `verification/campaign/MATRIX_CONTRIBUTION.md` §11.2, **committed 2026-08-25**, verified by rendering page 1 at 150 dpi
> - **Breuer, Peller, Rapp & Manhart, *Computers & Fluids* 38 (2009) 433–457** — same file, §11.3, same day
> - **The Ansys Fluid Dynamics Verification Manual** — `docs/ansys_verification/README.md` and the ANSYS charter, *"title-page verified against the PDF (rule 15)"*
> - **`tian_karayiannis_2000_ijhmt_43.pdf`, IJHMT 43 (2000) 849–866** — and this
>   one is **inside this territory**, which is why it is the counter-example that
>   matters most here: `docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md:20`,
>   *"Title pages verified | 3 of 3, plus `tian_karayiannis_2000_ijhmt_43.pdf` as a
>   fourth"*, with the printed page at `:79`–`:92`. **Committed 2026-08-24, a day
>   before this document was drafted, and this document was drafted not knowing
>   it.** *(Added at landing.)*

**The previous lane marked its statement `VERIFY` and did not assert it as a
defect, so this is a correction of scope, not an impeachment.** The correction
matters because the sentence was being read as a lab-wide indictment, and the
lab-wide picture is better than that sentence implies — while the **thermal**
picture, §1.4, is worse than the sentence implies, because it stops at three
papers and there are nine. *(Drafted as "thirteen" — corrected at landing; see
the LANDING NOTE. The nine are §1.4's rows, of which two are load-bearing and
OPEN.)*

**That §11 amendment also demonstrates the method this lane followed.** The
Greenblatt PDF's embedded metadata reads `Title: Microsoft Word -
PortlandPaperPart1.doc`, `Author: Administrator`. **A manifest built from metadata
would have recorded that paper as authored by "Administrator."** The rendered page
is the paper.

---

## 7. VERDICTS

Verdict vocabulary only. **No gate is graded by this document and no `PASS` or
`GATE FAIL` is claimed** — those words belong to pre-registered gates.

| item | verdict |
| --- | --- |
| Sidecar census, 19 PDFs / 19 sidecars, R9 clean in all three folders | **measured** |
| `ampofo_karayiannis_2003_ijhmt_46.pdf` rule-15 | **VERIFIED** |
| `betts_bokhari_2000_ijhff_21.pdf` rule-15 | **VERIFIED** |
| `nielsen_rong_olmedo_2010_clima_annex20.pdf` rule-15 | **VERIFIED** |
| Any thermal PDF FAILING rule 15 | **none — 0 of 19** |
| 9 thermal PDFs with no rule-15 record | **NOT VERIFIED** (the check was never made; not a failure) |
| `tian_karayiannis_2000_ijhmt_43` rule-15 | **VERIFIED** — committed record `PAPER_INTAKE_2026-08-24.md:20`, `:79`. This document was drafted calling it NOT VERIFIED; **corrected at landing** |
| `gjesdal_wasberg_andreassen_2003`, `wibron_ljung_lundstrom_2018`, `han_xie_2019` rule-15 | **VERIFIED** — `SATURATION_AUDIT_2026-08-25.md` §4.4 (`f782d9bc`), cited not re-read |
| **`vierendeels_merci_dick_2002_wit_afm02`** — carries K0c's stated applicability limit (Nu 8.687 at Ra 1e6) | **NOT VERIFIED — OPEN.** One reading at zero core-minutes. Read by no lane to date; **the supervisor schedules it** |
| **`zou_zhao_chen_2018_building_simulation`** — supplies K0d's case inside a frozen re-registration | **NOT VERIFIED — OPEN.** One reading at zero core-minutes. Read by no lane to date; **the supervisor schedules it** |
| ERCOFTAC Case 079 `.dat` archive, 22 files | **not a rule-15 subject at all** — the title-page test cannot be applied to a data archive. Its identity rests on sha256 + the `MANIFEST.md` fetch record. §2.2 |
| **T12 primary** | **BLOCKED** — does not exist on this box; the block is **not** stale |
| **K0d / Blay 1992** | **BLOCKED** — genuinely absent; K0d cannot reach P, therefore not `HOLDS` |
| **T2 tier `FORMULA`** | **NOT A RESULT as a tier claim** — the correlation and its validity range are nowhere on disk; T2 behaves as `ACQUIRE`. **Correction referred, not applied** |
| Index tier edits, verdict edits, queue-cell moves | **none made — reserved to the supervisor** |

---

## 8. COST, AND THE RULE-12 CALIBRATION

**Pre-registered: ZERO core-minutes. Actual: ZERO core-minutes. Ratio 1.00.**

No solver, no mesher, no case directory, no MPI rank, no GPU. The work was PDF
page rendering, `find`/`grep`/`sha256sum` sweeps and reading — single-rank
interactive filesystem work that the lab does not meter in core-minutes and that
this lane does not invent a figure for. **Derived dollar cost: $0.00**, which is
derived and not measured, because the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

**No row is added to `docs/COST_CALIBRATION.md`.** There is no compute row to
calibrate, and a calibration row built from an invented baseline would be worse
than an absent one. **Flagged rather than absorbed**, per the same judgment
`SIDECAR_VERIFICATION_2026-08-25.md` §6 recorded for its own uncosted OCR run.

---

## 9. WHAT THIS LANE COULD NOT VERIFY — stated plainly

1. **The 9 `NOT VERIFIED` thermal PDFs were not verified here.** The brief named
   three papers and this lane read those three rather than silently widening its
   scope. **`vierendeels_merci_dick_2002` and `zou_zhao_chen_2018` are the two
   that matter and they are still OPEN** — the first carries K0c's stated
   applicability limit, the second supplies K0d's case inside a frozen
   re-registration. Each is one reading and zero core-minutes. *(Drafted as
   "Tian & Karayiannis Part I and Wibron 2018"; both of those are VERIFIED —
   LANDING NOTE and §1.3.)*
2. **The Blay absence rests partly on a filename exclusion for 76 unsidecared
   PDFs** (§4.2). Rule 15 says a filename is not verification. The claim is
   `NOT OBTAINED` on strong evidence, **not proven to rule 15's positive
   standard.**
3. **Whether the ERCOFTAC Case 079 `.dat` archive is what it says it is** was not
   independently re-derived. Its sha256 and fetch record are cited from
   `MANIFEST.md`; this lane did not re-download or re-hash the upstream archive,
   and **could not, since fetching is Sanaa's alone.**
4. **Whether Nielsen 2010's plotted symbols could be digitised** was not tested —
   the figures were not opened for extraction. **It would not change the verdict:**
   the paper states no measurement uncertainty (§3.4), so a digitised row could
   only ever be REPORT-ONLY and could never supply P.
5. **Whether any of the 9 would FAIL if opened** is unknown. Zero have failed so
   far, across ten thermal papers and the repo-wide records in §6. **That is a
   reason to expect them to pass, and it is not evidence that they will.** L-144
   exists because a journal-and-year sanity check once passed on a wrong
   document.
6. **The `MANIFEST.md` paywall line** (§1.5) was left unrepaired — a frozen
   reference manifest is not this lane's to edit.
7. **Whether the saturation queue's B-6 ranking should be struck** rather than
   merely noted is a supervisor's call. This lane reports that the door is shut;
   it does not renumber the queue.

---

*Written by a heat-transfer lane, 2026-08-25. Zero core-minutes. No solver ran,
no gate was graded, no tier or verdict was edited, nothing was acquired from
outside the box, and nothing was sent, filed or submitted.*
