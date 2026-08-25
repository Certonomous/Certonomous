# SATURATION AUDIT — T12, T2, T5, the rule-15 exposure, and the 24-hour queue

**Heat-transfer lane, 2026-08-25 21:12–21:20Z, for the heat-transfer supervisor.**
**ZERO core-minutes.** No solver, no mesher, no `blockMesh`, no comparator, no case
directory, no MPI rank, no GPU. Nothing was sent, fetched, uploaded, filed or
acquired from outside this box. **No gate, threshold, band, cap, label, tier or
verdict is moved by this document.** It reports; the supervisor rules, and where
the question is what a tier *means*, Sanaa rules.

**Verdict vocabulary is CLAUDE.md rule 1 only.** Where this lane did not check a
thing itself, it writes **VERIFY** rather than borrowing another lane's word.

---

## 0. THE SIX HEADLINES

**1. TASK 4 IS THE BIG ONE AND THE BOARD'S FRAMING OF IT IS WRONG IN BOTH
DIRECTIONS.** The board carries *"only three PDFs in the whole repository carry a
rule-15 title-page verification, all in `forced_convection_heat_transfer/`;
Ampofo, Betts/ERCOFTAC 079 and Nielsen carry none."* The **Ampofo / Betts /
Nielsen** half was true and **this lane has now discharged all three by reading
the rendered title pages — all three VERIFY.** The **"only three"** half was
false even at HEAD: a committed record,
`docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md:20`,
reads *"Title pages verified | 3 of 3, plus `tian_karayiannis_2000_ijhmt_43.pdf`
as a fourth"* — **four, and the fourth is in `buoyant_natural_convection`, not
`forced_convection_heat_transfer`.** §4.

**2. AND THE PAPERS THE FAMILY WAS WORRIED ABOUT WERE NOT THE EXPOSED ONES.** The
exposure was never Ampofo or Betts — both are cited by rungs that were already
going to be re-read. **The unnamed exposure was `gjesdal_wasberg_andreassen_2003`,
which supplies K0c's ENTIRE case specification — geometry, fluid, every boundary
condition, the `Ra` definition, the rung values, all marked "READ IN FULL" — AND
its Table 1 referent values, in a rung that is already GRADED.** It carried no
rule-15 record of any kind. **This lane read its title page. VERIFIED.** §4.4.

**3. TASK 2 IS NOT A T2 QUESTION. It is a TIER-DEFINITION question and therefore
Sanaa's, and the precedent is a rung that has already been graded.** Zukauskas
returns **0 hits across all 96 sidecars** against a planted control of 13 on the
same corpus — the correlation and its validity range are nowhere on disk, exactly
as recorded. **But Dittus–Boelter and Gnielinski return 0 across the same 96
sidecars too** — and **T1b is tiered `FORMULA` and has already returned PASS ×4**
against a band armed from validity ranges that exist only in the lab's own
`correlation_band.py`, with no source cited. **If `FORMULA` requires a source on
disk, T2 is mis-tiered AND T1b's graded rows reopen. If it does not, T2 is
correctly tiered and merely unwritten.** §5.

**4. TASK 3: T5 CANNOT BE PROMOTED AS IT STANDS, and the reason is the
supervisor's own committed ruling, not a missing paper.** Its primary is held and
title-page verified and its sidecar is real (503,207 non-whitespace chars).
`T5_CONFIGURATION_RULING.md` (**at HEAD**) rules T5 onto the **Meinders matrix**
and requires the cell-count ladder to be **re-derived, not rescaled**. The draft
on disk is still the **single cube**. Promoting it would freeze a configuration
the supervisor has already ruled against. **There is also a conflict on record
about who may promote it at all.** §6.

**5. TASK 1: T12 IS STILL BLOCKED, ON BOTH LIMBS. The title page was never the
blocker.** This lane rendered and read it: it **VERIFIES**, every filename token
matching. **And it changes nothing** — the paper carries no data, only a pointer
to a web page; its three measurement primaries are absent from disk under a
sweep with a live planted control; and it states no measurement uncertainty
(0 hits against planted controls of 3 and 9). §3.

**6. TASK 5: "BUCKET A IS EMPTY EXCEPT K0d" IS REFUTED IN BOTH DIRECTIONS.**
**K0d is not in Bucket A at all** — it is `BLOCKED` at HEAD by the heat-transfer
supervisor's own committed ruling, and `K0d_runs/` does not exist. **T8 is**, and
it is frozen, comparator-complete, byte-identical to HEAD and unfired. **Bucket A
contains exactly one rung: T8, three single-rank cases, 335.34 core-min POINT.**
Beyond it the queue is genuinely empty, and this lane manufactures nothing. §7.

---

## 1. WHAT THIS LANE MEASURED, AND WITH WHAT INSTRUMENT

**Every sweep is `find <roots> -print0 | xargs -0 grep …`, not `grep -r`** —
`grep -r` in this repository honours ignore files and is blind to gitignored
archives. Roots: `/home/ubuntu/Certonomous`, `/home/ubuntu/closure-data`,
`/home/ubuntu/closure-challenge-benchmark`, `/home/ubuntu/certonomous-runs`.

**Every zero below is reported beside a planted control on the same instrument,
same binary, same flags** (rule 3). A zero from a reader not shown able to see a
non-zero is not evidence.

**Every title page below was read as a RENDERED PAGE** (`pdftoppm -png`, 120–130
dpi, page 1, then read as an image) — never from the filename, never from the
sha256, and **never from the PDF's embedded metadata**, which §4.6 shows would
have produced two false identifications in this very set.

**Live box reading, 2026-08-25T21:17:57Z** (taken so the queue's occupancy claims
rest on a measurement): 16 cores; load average 3.47 / 4.23 / 4.22; `MemAvailable`
**27.1 GiB**; **three** processes at ≥ 95 % CPU, all `buoyantBoussinesqSimpleFoam`
(pids 2203927 / 2203944 / 2203947, elapsed 04:38:08), which are this team's own
T1b L4 EXT2 arms. **Thermal occupancy 3 of 16 = 18.75 %; 13 cores free.**
**VERIFY before any launch:** `docker ps` is denied to this user and L-41 says a
process sweep is blind to fleet agents, so another team's occupancy could be
non-zero and invisible.

**HEAD moved three times while this lane worked** — `59c3d8f6` at dispatch,
`c10ba764` at 21:14Z, `b530da36` at 21:17Z. Every freeze check below was taken
against the HEAD captured in the same shell invocation, per L-223.

---

## 2. A PROCESS FINDING THE SUPERVISOR NEEDS BEFORE THE FINDINGS

**Two earlier lanes already worked these questions today. One of their documents
is INVISIBLE FROM HEAD, and that is why the brief reads as stale.**

| document | lines | in HEAD? | mtime |
|---|---:|---|---|
| `docs/campaigns/T-family/THERMAL_SATURATION_QUEUE.md` | 529 | **yes** (`2358a650`) | 19:15Z |
| `docs/campaigns/T-family/THERMAL_REFERENCE_TITLE_PAGE_AUDIT.md` | 503 | **NO — UNCOMMITTED** | 19:27Z |
| `docs/campaigns/T-family/THERMAL_SATURATION_QUEUE_2026-08-25b.md` | 642 | **yes** | 20:30Z |

**`THERMAL_REFERENCE_TITLE_PAGE_AUDIT.md` is 503 lines of another lane's finished
work sitting outside HEAD.** The 20:30Z queue lane found the same thing, declined
to commit it for the same reason, and flagged it. **This lane also declines**: it
is a foreign row, that lane may still be live, and committing it would put
another agent's work under this lane's message. **Flagged again so somebody can
be dispatched to land it** (rule 10). It is now the second lane to leave it, which
is itself the finding — *nobody is going to land it by accident.*

**This lane did not relay that document's conclusions.** A relayed check is a
summary, not a check. Every load-bearing claim below was re-derived from disk by
this lane, and **§4.3 records where this lane's own measurement CONTRADICTS it.**

**Live L-186 evidence, reported because it happened during this audit.** This
lane created a scratch directory, wrote four rendered title pages into it, and
**four minutes later the directory did not exist** — wiped by another agent
sharing the same scratchpad, mid-task. The renders were redone under a second
name. **The scratchpad is not a handoff channel and is not even reliable storage
within a single lane's own task.** This document is in the case directory for
exactly that reason.

---

## 3. TASK 1 — T12. **STILL BLOCKED.** The title page verifies and unblocks nothing.

**The question put:** T12 was recorded as *"possibly unblocked by a zero-compute
title-page read."* **The read was done. The answer is no.**

### 3.1 The title page, read

`docs/papers/data_center_indoor_airflow/nielsen_rong_olmedo_2010_clima_annex20.pdf`
— 457,435 bytes, 9 pages. Page 1 is a bare cover leaf carrying, centre-page, in
this order **as printed on the rendered page**:

- **Authors as printed:** Peter V. Nielsen, Li Rong and Inés Olmedo
- **Title as printed:** *The IEA Annex 20 Two-Dimensional Benchmark Test for CFD Predictions*
- **ISBN as printed:** 978-975-6907-14-6
- **Venue as printed:** Clima 2010, 10ᵗʰ REHVA World Congress

**Rule-15 verdict: VERIFIED.** All six filename tokens — `nielsen` / `rong` /
`olmedo` / `2010` / `clima` / `annex20` — match the printed page. There is no
standalone date line; the year is printed only inside *"Clima 2010"*, and is
recorded here exactly as printed. **No contradiction with the filename or with
any citing record.**

### 3.2 Why that unblocks nothing — three measurements, each with its control

**(a) The paper is a pointer, not the data.** Its own text says so four times —
*"benchmark is defined on a web page"* (sidecar line 21 and again line 195),
*"The benchmark is located together with three other benchmarks on the web
page:"* (line 69), followed by the address. **The measurements live off this box.
Obtaining them is a fetch, and a fetch is Sanaa's alone (rules 7 and 8). This
lane attempted nothing and proposes nothing.**

**(b) The measurement primaries it points at are not on disk.** Read from its
printed reference list (sidecar lines 213–232):

| ref | source as printed | filename sweep, 4 roots |
|---|---|---:|
| [1] | Nielsen, P V. 1990. *Specification of a Two-Dimensional Test Case*, Aalborg University, IEA Annex 20 | — |
| [2] | Restivo, A M. 1979. *Turbulent Flow in Ventilated Rooms*, PhD thesis, Imperial College, London | **`*restivo*` → 0 files** |
| [4] | Schwenke, H. 1975. *Über das Verhalten ebener horizontaler Zuluftstrahlen im begrenzten Raum*, Luft- und Kältetechnik, Nr. 5, Dresden | **`*schwenke*` → 0 files** |

**Planted controls, same instrument, same flags:** `*nielsen*` → **2 files**;
`*ampofo*` → **4 files**. **The reader was shown able to see a non-zero before
either zero was believed.**

**(c) The paper states no measurement uncertainty, and a graded row needs one.**

| corpus | pattern | hits |
|---|---|---:|
| Nielsen sidecar | `uncertain\|accuracy\|error bar`, `grep -ci` | **0** |
| **planted control** — Narumanchi sidecar | same binary, same flags | **3** |
| **planted control** — Ampofo sidecar | `uncertain\|accuracy` | **9** |

### 3.3 Verdict

**T12: STILL BLOCKED, on both limbs.** The **isothermal** limb is blocked on
Nielsen 1990 / Restivo 1979; the **nonisothermal** limb on Schwenke 1975. **None
of the three is on this box.** The record is **not stale**, and the ranking that
called this *"the highest-value zero-compute action on the board"* should come
down — **the door is shut, and this lane has now shut it twice over.** Whether to
strike that ranking is the supervisor's call; this lane reports and does not
renumber.

**What T12 would need:** Sanaa's decision to obtain Nielsen 1990 and Restivo 1979,
or Schwenke 1975, or to authorise a fetch of the benchmark web page. **All three
are sends. Reserved to her (rule 7). Not proposed here, and no route around them
is offered.**

---

## 4. TASK 4 — THE RULE-15 EXPOSURE. Enumerated, counted, and four new title pages read.

### 4.1 Every PDF in this team's territory — 19, enumerated with absolute paths

`docs/papers/forced_convection_heat_transfer/` — **3 PDFs, 3 sidecars**

| # | absolute path | rule-15 record | citation |
|---:|---|---|---|
| 1 | `/home/ubuntu/Certonomous/docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf` | **VERIFIED** | `docs/papers/forced_convection_heat_transfer/SIDECAR_VERIFICATION_2026-08-25.md:32`, `:250` |
| 2 | `/home/ubuntu/Certonomous/docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf` | **VERIFIED** (by eye; image-only scan) | `docs/papers/forced_convection_heat_transfer/SIDECAR_VERIFICATION_2026-08-25.md` §2.3; `docs/THERMAL_CAPABILITY_STATE.md:126` |
| 3 | `/home/ubuntu/Certonomous/docs/papers/forced_convection_heat_transfer/narumanchi_hassani_bharathan_2005_nrel_tp540_38787.pdf` | **VERIFIED** | `docs/papers/forced_convection_heat_transfer/SIDECAR_VERIFICATION_2026-08-25.md:45`, `:251` |

`docs/papers/buoyant_natural_convection/` — **9 PDFs, 9 sidecars**

| # | absolute path | rule-15 record | citation |
|---:|---|---|---|
| 4 | `…/buoyant_natural_convection/ampofo_karayiannis_2003_ijhmt_46.pdf` | **VERIFIED — read by THIS lane, §4.2** | this document §4.2 |
| 5 | `…/buoyant_natural_convection/betts_bokhari_2000_ijhff_21.pdf` | **VERIFIED — read by THIS lane, §4.2** | this document §4.2 |
| 6 | `…/buoyant_natural_convection/tian_karayiannis_2000_ijhmt_43.pdf` | **VERIFIED — committed record, and re-read by THIS lane** | `docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md:20`, `:79`, `:607`; re-read §4.3 |
| 7 | `…/buoyant_natural_convection/gjesdal_wasberg_andreassen_2003_physics0305049.pdf` | **VERIFIED — read by THIS lane, §4.4. Was NOT VERIFIED before today and is K0c's whole case spec** | this document §4.4 |
| 8 | `…/buoyant_natural_convection/han_xie_2019_1903.09506.pdf` | **VERIFIED — read by THIS lane, §4.4** | this document §4.4 |
| 9 | `…/buoyant_natural_convection/vierendeels_merci_dick_2002_wit_afm02.pdf` | **NOT VERIFIED** — **and LOAD-BEARING, §4.5** | no record found |
| 10 | `…/buoyant_natural_convection/sadighi_2020_particles_heating.pdf` | **NOT VERIFIED** | no record found |
| 11 | `…/buoyant_natural_convection/xu_chen_2000_indoor_air_two_layer.pdf` | **NOT VERIFIED** | no record found |
| 12 | `…/buoyant_natural_convection/zhang_chen_2000_les_indoor.pdf` | **NOT VERIFIED** | no record found |

`docs/papers/data_center_indoor_airflow/` — **7 PDFs, 7 sidecars**

| # | absolute path | rule-15 record | citation |
|---:|---|---|---|
| 13 | `…/data_center_indoor_airflow/nielsen_rong_olmedo_2010_clima_annex20.pdf` | **VERIFIED — read by THIS lane, §3.1** | this document §3.1; also `THERMAL_SATURATION_QUEUE_2026-08-25b.md` §4.1 (committed) |
| 14 | `…/data_center_indoor_airflow/wibron_ljung_lundstrom_2018_en11030644.pdf` | **VERIFIED — read by THIS lane, §4.4. Was NOT VERIFIED before today and K2c-A digitised off it** | this document §4.4 |
| 15 | `…/data_center_indoor_airflow/zou_zhao_chen_2018_building_simulation.pdf` | **NOT VERIFIED** — **and LOAD-BEARING, §4.5** | no record found |
| 16 | `…/data_center_indoor_airflow/kayne_agarwal_2013_mixed_convection.pdf` | **NOT VERIFIED** — cited as a K0d Blay secondary (report-only) | no record found |
| 17 | `…/data_center_indoor_airflow/hamann_klein_2012_osti_1044604.pdf` | **NOT VERIFIED** | no record found |
| 18 | `…/data_center_indoor_airflow/vangilder_schmidt_2005_ipack.pdf` | **NOT VERIFIED** | no record found |
| 19 | `…/data_center_indoor_airflow/wibron_ljung_lundstrom_2019_en12081473.pdf` | **NOT VERIFIED** | no record found |

**Sidecar census: 19 PDFs, 19 sidecars, `FILING_CHARTER` R9 clean in all three
folders.** Measured, not assumed.

### 4.2 The three papers the brief named — ALL THREE VERIFY

Read as rendered pages by this lane at 21:12Z.

**`ampofo_karayiannis_2003_ijhmt_46.pdf` — VERIFIED**

- **Title as printed:** *Experimental benchmark data for turbulent natural convection in an air filled square cavity*
- **Authors as printed:** F. Ampofo, T.G. Karayiannis (corresponding, `karayitg@sbu.ac.uk`, tel. +44-207-815-7628)
- **Affiliation as printed:** Division of Environmental, Energy and Building Services Engineering, **Faculty of Engineering, Science and Technology**, South Bank University, 103 Borough Road, London SE1 0AA, UK
- **Journal as printed:** *International Journal of Heat and Mass Transfer* **46** (2003) 3551–3572; Pergamon / Elsevier; doi `10.1016/S0017-9310(03)00147-9`
- **Dates as printed:** received 11 September 2002; revised 19 March 2003
- **Abstract as printed:** cavity 0.75 m high × 0.75 m wide × 1.5 m deep giving 2D flow; hot and cold walls isothermal at **50 and 10 °C**; **Ra = 1.58 × 10⁹**; local and average Nusselt numbers, wall shear stress, turbulent kinetic energy and temperature-variance dissipation rate all presented

**Filename check:** `ampofo` / `karayiannis` / `2003` / `ijhmt` / `46` — every
token matches. **Citation check:** K0c and the K0cP/Q/R/S/X arms call it the
square-cavity benchmark; the printed title says *square cavity* and the printed
abstract says *benchmark data*. **No contradiction.**
*(One precision against the uncommitted audit, which recorded the affiliation as
"Faculty of Engineering" — the printed page reads "Faculty of Engineering,
Science and Technology". Immaterial to the identification; recorded because a
title-page record that is approximate is not a title-page record.)*

**`betts_bokhari_2000_ijhff_21.pdf` — VERIFIED**

- **Title as printed:** *Experiments on turbulent natural convection in an enclosed tall cavity*
- **Authors as printed:** P.L. Betts (corresponding), I.H. Bokhari
- **Affiliation as printed:** Department of Mechanical Engineering, UMIST, PO Box 88, Manchester M60 1QD, UK; Bokhari's present address printed as Nuclear Engineering Division, Pakistan Institute of Nuclear Science and Technology, P.O. Nilore, Islamabad, Pakistan
- **Journal as printed:** *International Journal of Heat and Fluid Flow* **21** (2000) 675–683; Elsevier; PII `S0142-727X(00)00033-3`
- **Dates as printed:** received 29 June 1999; accepted 10 April 2000
- **Abstract as printed:** cavity **2.18 m high × 0.076 m wide × 0.52 m deep**; plate temperature differentials **19.6 °C and 39.9 °C**; **Rayleigh numbers based on width 0.86 × 10⁶ and 1.43 × 10⁶**; partially conducting top and bottom walls with outer guard channels

**Filename check:** `betts` / `bokhari` / `2000` / `ijhff` / `21` — every token
matches. Both printed ΔT values are the `lo`/`hi` split the F14 reference manifest
describes.

**THE PRECISION ON "ERCOFTAC 079", AND IT MATTERS.** The family cites this as
*"Betts / ERCOFTAC case 079"*. **The printed title page carries no "ERCOFTAC" and
no "079."** Case 079 is the ERCOFTAC Classic Collection's label for the
experiment, applied by the database, not printed on the paper. **The citation
names two artifacts, not one:**

| artifact | what it is | how it is verified |
|---|---|---|
| `betts_bokhari_2000_ijhff_21.pdf` | the journal paper | **rule 15, rendered title page, VERIFIED here** |
| `…/F14-cooling-ladder/reference-data/betts_bokhari/*.dat`, 22 files | the ERCOFTAC Case 079 data subset | archive sha256 + fetch record in its `MANIFEST.md`. **Not a paper — rule 15's title-page test cannot be applied to a data archive** |

**Both check out and the paper corroborates the archive.** Recorded so that
nobody later reads *"ERCOFTAC 079 is rule-15 verified"* and believes a data
archive was title-page checked, **which is not a thing that can be done to a data
archive.** The archive's own provenance rests on its fetch record, and this lane
did not and could not re-derive it — re-fetching is a send.

**`nielsen_rong_olmedo_2010_clima_annex20.pdf` — VERIFIED.** §3.1.

### 4.3 A CORRECTION to the uncommitted audit — Tian was ALREADY verified, in a COMMITTED record

`THERMAL_REFERENCE_TITLE_PAGE_AUDIT.md:100` lists
`tian_karayiannis_2000_ijhmt_43` as `NOT VERIFIED` and as **"LOAD-BEARING …
has never been title-page verified."** **That is false, and the record that
refutes it is committed and eight days old.**

`docs/papers/forced_convection_heat_transfer/PAPER_INTAKE_2026-08-24.md` (in HEAD):

- line **20**: *"Title pages verified | 3 of 3, plus `tian_karayiannis_2000_ijhmt_43.pdf` as a fourth"*
- line **21**: *"Filename mismatches | none — all four printed identities match their filenames"*
- §**1.4** (line 79 ff.): *"`tian_karayiannis_2000_ijhmt_43.pdf` — Part I or Part II?"*, with the authors read off the page at line 85
- line **607**: *"the file present is **Part I**, verified by title page"*

**This lane re-read the page anyway rather than trusting the record**, since the
uncommitted audit had put it in doubt:

- **Title as printed:** *Low turbulence natural convection in an air filled square cavity — **Part I: the thermal and fluid flow fields***
- **Authors as printed:** Y.S. Tian, T.G. Karayiannis
- **Affiliation as printed:** School of Engineering System and Design, South Bank University, 103 Borough Road, London SE1 0AA, UK
- **Journal as printed:** *International Journal of Heat and Mass Transfer* **43** (2000) 849–866; PII `S0017-9310(99)00199-4`
- **Dates as printed:** received 18 May 1998; revised 4 June 1999
- **Abstract as printed:** cavity 0.75 m × 0.75 m × 1.5 m; hot and cold walls at **50 and 10 °C**; **Ra = 1.58 × 10⁹**

**VERIFIED, and it is Part I.** The committed record was right; the uncommitted
audit was wrong. **This is why the uncommitted audit must not be landed
unread** — §2 asks for it to be committed, and this is the row a committer must
fix on the way in.

### 4.4 FOUR TITLE PAGES READ THAT NOBODY ASKED FOR — including the one that mattered most

The brief named three papers. This lane read three more after the census showed
that **the papers filed as "secondary" include K0c's entire case specification**.
Zero core-minutes; the scope widening is disclosed rather than silent.

**`gjesdal_wasberg_andreassen_2003_physics0305049.pdf` — VERIFIED. THIS IS THE ONE.**

- **Title as printed:** *Spectral element simulations of buoyancy-driven flow*
- **Authors as printed:** Thor Gjesdal, Carl Erik Wasberg, and Øyvind Andreassen
- **Affiliation as printed:** Norwegian Defence Research Establishment, NO-2027 Kjeller (`thg@ffi.no`)
- **Identifier as printed on the spine of the page:** `arXiv:physics/0305049v1 [physics.comp-ph] 13 May 2003`
- **Abstract as printed:** a spectral element method for incompressible Navier–Stokes, extended to buoyant flows under the Boussinesq approximation; *"Free convection in closed two-dimensional cavities are computed and the results are in very good agreement with the available reference solutions"*

**Filename check:** `gjesdal` / `wasberg` / `andreassen` / `2003` /
`physics0305049` — every token matches. **Citation check:**
`docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md:56`
names it *"Spectral element simulations of buoyancy-driven flow.
arXiv:physics/0305049"* — **exact match to the printed title. No contradiction.**

**Why this was the family's real exposure.** In that same gate file, **lines
70–78**, Gjesdal 2003 marked **"READ IN FULL"** is the cited authority for
**every single line of K0c's case specification** — geometry, fluid, left wall,
right wall, top and bottom walls, gravity direction, the `Ra` definition, and the
rung values `Ra = 1e3…1e6` — and at **lines 60 and 85** its **Table 1** supplies
the referent `Nu` values K0c graded against. **K0c is a graded rung, and until
21:16Z today its entire case definition and half its referent rested on a
document nobody in this lab had opened the title page of.** It now verifies, and
**nothing about K0c's numbers moves** — but the check that could have moved them
had never been made.

**`han_xie_2019_1903.09506.pdf` — VERIFIED**

- **Title as printed:** *Robust globally divergence-free weak Galerkin finite element methods for natural convection problems*
- **Authors as printed:** Yihui Han, Xiaoping Xie (corresponding, `xpxie@scu.edu.cn`)
- **Affiliation as printed:** School of Mathematics, Sichuan University, Chengdu 610064, China
- **Identifier as printed:** `arXiv:1903.09506v1 [math.NA] 22 Mar 2019`; footer *Global Science Preprint*

**Filename check:** `han` / `xie` / `2019` / `1903.09506` — every token matches.

**An observation, not a ruling, and it is about referent class rather than rule
15.** Both Gjesdal and Han & Xie are **numerical-methods papers** — a spectral
element solver and a weak-Galerkin FEM. Their tables are **computed** values, not
measurements. K0c already discloses this: its line 228 records the referent as
*"de Vahl Davis 1983 **via** Han and Xie 2019 Table 3 (**SECONDARY**,
triple-corroborated for Nu); Gjesdal 2003 Table 1; INL/EXT-09-15333 Table 3."*
**So the referent lineage is a secondary quotation of de Vahl Davis, disclosed on
the record and triple-corroborated.** That is honest and it is already written
down. **Whether a triple-corroborated secondary quotation can supply a P column
is a `RESULT_PRIORITY` question and is NOT this lane's to answer** — it is raised
only because the title-page work put it in front of this lane.

**`wibron_ljung_lundstrom_2018_en11030644.pdf` — VERIFIED**

- **Title as printed:** *Computational Fluid Dynamics Modeling and Validating Experiments of Airflow in a Data Center*
- **Authors as printed:** Emelie Wibron (corresponding, `emelie.wibron@ltu.se`, tel. +46-920-493-539), Anna-Lena Ljung and T. Staffan Lundström
- **Affiliation as printed:** Division of Fluid and Experimental Mechanics, Luleå University of Technology, SE-971 87 Luleå, Sweden
- **Journal as printed:** *Energies* **2018**, *11*, 644; MDPI; doi `10.3390/en11030644`
- **Dates as printed:** received 24 February 2018; accepted 12 March 2018; published 14 March 2018
- **Abstract as printed:** compares `k–ε`, the Reynolds Stress Model and Detached Eddy Simulations in ANSYS CFX 16.0 against experimental values; concludes RSM is recommended and that `k–ε` fails to predict low-velocity regions

**Filename check:** `wibron` / `ljung` / `lundstrom` / `2018` / `en11030644` —
every token matches. **This closes the K2c-A digitisation exposure**: K2c-A
digitised Figs 6a/6b and 7a–7e off this PDF, whose sha256 matched the manifest —
**and rule 15 says a hash is not verification.** The title page now says it is.

**`tian_karayiannis_2000_ijhmt_43.pdf` — VERIFIED.** §4.3.

### 4.5 What is STILL not verified, and which of it is load-bearing

**9 of 19 carry no rule-15 record. Two of the nine are load-bearing and are named
rather than buried in a list.**

| paper | why it is load-bearing |
|---|---|
| **`vierendeels_merci_dick_2002_wit_afm02`** | `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md:228` cites it **"Table 1, READ IN FULL"** as the authority for K0c's **applicability limit** — *"Nu = 8.687 at Ra 1e6 with epsilon = 0.6, a 1.3 percent shift from Boussinesq at identical Ra."* **A graded rung's stated limit of applicability rests on it.** |
| **`zou_zhao_chen_2018_building_simulation`** | `K0d_REREGISTRATION.md:174-187` records it as one of two **secondaries that SUPPLY THE CASE** for K0d. It sits inside a **frozen** re-registration. It may never supply a graded reference value — the re-registration says so explicitly — but the case geometry is read from it. |

The remaining seven — `sadighi_2020`, `xu_chen_2000`, `zhang_chen_2000`,
`kayne_agarwal_2013`, `hamann_klein_2012`, `vangilder_schmidt_2005`,
`wibron_ljung_lundstrom_2019` — are cited in inventories, READMEs and the K2c
validation search, and none was found supplying a case specification or a graded
value. `kayne_agarwal_2013` is cited as a **report-only** Blay secondary and can
never supply P.

**Each of the nine is one reading and zero core-minutes. This lane stopped at
six** — three named in the brief and three the census showed were load-bearing —
rather than widening indefinitely.

### 4.6 THE COUNT

| state | at HEAD before this lane | **after this lane** |
|---|---:|---:|
| **VERIFIED** | **4** (bahrami, narumanchi, meinders, tian) | **10** |
| **NOT VERIFIED** | 15 | **9** |
| **FAILED** | **0** | **0** |
| total territory PDFs | 19 | 19 |

**No thermal PDF has ever FAILED rule 15 — 0 of 19, across ten now read.** A
check never made is recorded as `NOT VERIFIED` throughout and is never written up
as a clean result.

**The board's sentence, restated against measurement:**

> **The narrow half was TRUE and is now DISCHARGED.** Ampofo, Betts and Nielsen
> carried no rule-15 record. All three have been read by this lane. **All three
> VERIFY.**
>
> **The broad half was FALSE, and false in a specific way worth recording:** the
> committed count was **four**, not three, and **the fourth sits in
> `buoyant_natural_convection`, not `forced_convection_heat_transfer`** — so the
> sentence was wrong about the number *and* about the folder. Title-page records
> also exist outside this territory (Roshko 1954 at
> `docs/EXTERNAL_REFERENT_AUDIT.md:930`; Greenblatt et al. and Breuer et al. at
> `verification/campaign/MATRIX_CONTRIBUTION.md` §11.2–§11.3; the Ansys manual per
> `docs/ansys_verification/README.md`) — **VERIFY**, cited from those records,
> not re-opened by this lane.
>
> **And the sentence pointed at the wrong papers.** Ampofo and Betts were never
> the exposure. **Gjesdal was**, and it was not on the list.

**Rule 15 vindicated twice in this very set, by measurement.** Embedded PDF
metadata for two of these files reads:

| file | metadata `Title` | metadata `Author` |
|---|---|---|
| `nielsen_rong_olmedo_2010_clima_annex20.pdf` | `Microsoft Word - 100128 Full paper.doc` | `pvn` |
| `ampofo_karayiannis_2003_ijhmt_46.pdf` | `doi:10.1016/S0017-9310(03)00147-9` | *(absent)* |

**A manifest built from metadata would have recorded the Nielsen paper's title as
a Word filename and its author as "pvn", and the Ampofo paper as having no author
at all.** The rendered page is the paper. This is exactly L-144.

---

## 5. TASK 2 — T2's TIER. **The evidence is unambiguous. The QUESTION is a tier definition, and that is Sanaa's.**

### 5.1 What the record claims

`docs/campaigns/T-family/T_FAMILY_INDEX.md` §2 records:

> | **T2** | tube bank vs Zukauskas | **FORMULA** | needs the correlation's **stated validity range** cited, not just its algebra |

and §1 defines the tier:

> | **FORMULA** | a published correlation stated as an equation | reproducible from the formula; **no paper needed to evaluate it**, though its validity range must be cited |

### 5.2 What the evidence supports — this lane's own sweep, with three controls

| sweep | corpus | hits |
|---|---|---:|
| `zukausk` \| `zhukausk` \| `ukausk`, case-insensitive | 4 roots, `.txt`/`.md`/`.dat`/`.csv`/`.json`/`.py` | **6 files** |
| same pattern | **the 96 sidecars under `docs/papers/`** | **0** |
| **planted control** `nusselt` | **the same 96-sidecar corpus, same binary, same flags** | **13** |
| **planted control** `Hanjali` (literal, non-ASCII reader path) | same corpus | **4** |

The `ukausk` variant was included deliberately so a non-ASCII initial `Ž` — which
`-i` does not fold — could not hide a hit; the `Hanjali` control proves that
reader path returns non-zero. **All 6 hits are lab prose — the lab talking about
the missing correlation, never the correlation itself:** `docs/LAB_STATE.md`,
`T_FAMILY_INDEX.md`, `MATRIX_CONTRIBUTION.md`, both saturation queues, and the
uncommitted audit.

**Neither half is on disk. Not the algebra, not the range.** The evidence agrees
exactly with what the two prior lanes measured, on an independently built
instrument.

### 5.3 THE EXACT DISCREPANCY — and why it is NOT this supervisor's to rule

**Stated plainly: the discrepancy turns on what `FORMULA` MEANS, not on which
tier T2 meets. Per the brief's own constraint, that changes who decides.**

The tier definition contains two clauses that pull opposite ways:

- *"no paper needed to evaluate it"* — **T2 satisfies this.** Zukauskas is a
  published correlation; nobody disputes that it exists in the literature.
- *"its validity range must be cited"* — **T2 does not satisfy this**, on any
  reading, because nothing on disk states it.

**Reading A (tier = what class of reference the rung needs):** `FORMULA` is
correct for T2. The validity-range clause is a **precondition to gating**, not to
tiering, and T2's own state cell already records it as outstanding. Under this
reading **T2 is correctly tiered and simply unwritten** — the index promises
nothing false.

**Reading B (tier = whether an acquisition step exists):** `FORMULA` is
over-claimed. An acquisition **is** needed — a source stating the correlation and
its range — so T2 behaves as `ACQUIRE`. Under this reading the index **promises
that no acquisition is needed when one is.**

### 5.4 THE PRECEDENT THAT MAKES THIS SANAA'S AND NOT A HOUSEKEEPING FIX

**Reading B does not stop at T2. It reaches a rung that has already been graded.**

`T1b` is tiered **`FORMULA`** in the same index table, against **Dittus–Boelter +
Gnielinski**, and has already **returned PASS ×4**. This lane swept for its two
correlations on the same instrument:

| pattern | corpus | hits |
|---|---|---:|
| `gnielinski` | **the 96 sidecars** | **0** |
| `dittus` | **the 96 sidecars** | **0** |
| `gnielinski` | 4 roots | 18 files — **all lab prose and lab code** |
| `dittus` | 4 roots | 17 files — **all lab prose and lab code** |

*(All four-root counts in this document are stated **excluding this document
itself**, which now contains every token it sweeps for. Re-running any of them
after this file lands returns one more.)*

**Neither correlation appears in a single paper on this box.** T1b's band is armed
entirely from `verification/runs/T-family/T1_runs/correlation_band.py`, whose
header block reads the algebra and the ranges directly:

```
  Dittus-Boelter  Nu = 0.023 Re^0.8 Pr^n,  n = 0.4 heating
                  stated validity 0.6 <= Pr <= 160, Re >~ 1e4, L/D >~ 10
  Gnielinski      Nu = (f/8)(Re-1000)Pr / [1 + 12.7 (f/8)^0.5 (Pr^(2/3) - 1)]
                  stated validity 0.5 <= Pr <= 2000, 3000 <= Re <= 5e6
```

encoded at lines 32–33 as `DB_VALID` and `GN_VALID` and **checked, not assumed**,
at lines 66–79, which `REFUSE` a row outside either range. **The instrument is
disciplined. What it does not carry is a citation** — the phrase *"stated
validity"* names no source, and no source on this box states it.

**So the two readings decide different things:**

- **Under Reading A:** T2 keeps `FORMULA`, T1b keeps `FORMULA`, both are
  consistent, and T2's gap is a document nobody has written yet.
- **Under Reading B:** T2 moves to `ACQUIRE` — **and so does T1b, whose four PASS
  rows then rest on a band with no source on disk.** That is not a tier edit; it
  is **reopening a graded rung.**

**This lane rules nothing and recommends nothing.** It records that the choice
between those readings is a **tier-definition interpretation**, that it is
**reserved to Sanaa**, and that **whoever answers it should be told about T1b
before they answer, because T2 is the cheap consequence and T1b is the expensive
one.** A ruling made on T2 alone would silently decide T1b.

---

## 6. TASK 3 — T5's PROMOTION. What it needs, and what is on disk.

### 6.1 State at HEAD, verified by blob hash rather than by `git diff`

| file | in HEAD? | HEAD blob | worktree | |
|---|---|---|---|---|
| `docs/campaigns/T-family/T5_PREREGISTRATION_DRAFT.md` | **yes** | `d56018d18fef1ed4cedefdf54da19631026c98b3` | `d56018d1…` | **identical** |
| `docs/campaigns/T-family/T5_CONFIGURATION_RULING.md` | **yes** | — | — | committed |

**It is committed as a `DRAFT`, and a draft is not a pre-registration.** Its own
line 3 reads **"DRAFT — NOT FROZEN — NOT COMMITTED — NOT BUILT — NOT RUN. Zero
compute spent."** `verification/runs/T-family/` holds no T5 directory of any kind
— checked on disk, not asserted. **Rule 2's pre-first-compute state therefore
still holds and amendments are still legal.**

### 6.2 The evidence for T5, and it is genuinely good

| requirement | state | evidence |
|---|---|---|
| primary held | **YES** | `docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf`, 15,477,157 B |
| **rule-15 title page** | **VERIFIED** (by eye; the PDF is an image-only scan) | `SIDECAR_VERIFICATION_2026-08-25.md` §2.3; `docs/THERMAL_CAPABILITY_STATE.md:126` |
| sidecar real, not a form-feed shell | **YES — 503,207 non-whitespace characters**, measured by this lane | OCR-remediated 2026-08-25 from 0 characters |
| stated uncertainty | **YES — 5 % mid-face / 10 % edges in local `h`**, a printed propagation (Eq. 3.19, p. 59) | `T5_CONFIGURATION_RULING.md` §5.2 |
| data form | **digitisable figures, NO tabulated appendix** — every graded row must be digitised | `T_FAMILY_INDEX.md` §2, T5 row |

**T5 is the only queued rung whose reference is held, verified, and carries a
stated uncertainty. It is not reference-blocked. It is document-blocked.**

### 6.3 WHAT ACTUALLY BLOCKS PROMOTION — the supervisor's own committed ruling

**`T5_CONFIGURATION_RULING.md` is at HEAD and it makes the existing draft
un-promotable as written.** Its §1:

> **T5 is built on the MEINDERS MATRIX configuration — `S_x/H = S_z/H = 4`, a
> spatially periodic domain of one cube — and NOT on the single cube.**
> … **The cell-count ladder DOES move**, because the domain changes from a channel
> with a development length to one spatial period. It must be **re-derived, not
> rescaled**, and that re-derivation belongs in the pre-registration.

**The draft on disk is still the single cube.** Promoting it unchanged would
freeze a configuration the supervisor has already ruled against, and would carry
forward a cell ladder (5.4e4 / 2.2e5 / 9.0e5) and a cost (USD 3.72–7.16 under two
rate models) derived for a domain T5 is no longer being built on. **The `r = 1.6`
refinement ratio is explicitly RETAINED by that ruling (§1, §4) and does not
move.**

**Four further things the ruling binds into the rewritten pre-registration:**

1. **§5.3 — the Nusselt degree of freedom must be FORMED and FROZEN before
   compute.** *"The thesis does not report a Nusselt number at all"* — it reports
   `h` in W/m²K and `h/h̄`. A rung wanting `Nu = hH/λ_air` must form it, and the
   paper does not fix the temperature at which `λ_air` is evaluated. With a 75 °C
   core, ~19–21 °C inlet and a 43–62 °C surface **the film-temperature choice is a
   real freedom**, and the ruling requires it stated with the `λ_air` it produces,
   *"never inherited from a secondary and never chosen after a deviation is seen."*
2. **§5.2 — two error channels, REPORTED SEPARATELY, NEVER SUMMED**: the paper's
   own 5 %/10 % propagation, and the digitisation error. They share a
   mid-face/edge pattern for **independent reasons** — the digitisation's because
   *"Fig. 8.26's abscissa is not numeric"*, carrying only corner landmarks A, B,
   C, D.
3. **§5.2 — NO ROW GRADED AT OR NEAR AN EDGE OR CORNER.** Edge behaviour is
   `REPORTED`.
4. **§3 remains OPEN** — the ruling did not establish whether the matrix chapter
   carries a reattachment or recirculation diagnostic.

### 6.4 A CONFLICT ON RECORD ABOUT WHO MAY PROMOTE IT

**Two committed documents disagree, and this lane does not resolve it.**

- `T5_PREREGISTRATION_DRAFT.md` **line 5**: *"It freezes on Sanaa's reading **or
  on the supervisor's promotion of this file** to `T5_PREREGISTRATION.md`, and
  not before."* → **the supervisor may promote it.**
- `T5_CONFIGURATION_RULING.md` **§6**, written three days later by the supervisor:
  *"`T5_PREREGISTRATION_DRAFT.md` is still unfrozen and its **12 INTERPRETATIONs
  are still on Sanaa's desk, unanswered — they are hers**."* → **twelve open
  questions are Sanaa's.**

`THERMAL_SATURATION_QUEUE_2026-08-25b.md` §5.1 row 3 reads the first and
concludes *"the supervisor can promote it."* **That reading is at least
incomplete**: the supervisor's own later ruling says twelve decisions inside the
document belong to Sanaa. **Whether "promotion" means freezing the
INTERPRETATIONs as drafted, or requires her answers first, is unsettled on the
record.** Given the brief's constraint — *tier-definition interpretation is
reserved to Sanaa* — and given that T5's tier is `ACQUIRE (obtained)` and several
of the twelve bear on what "obtained" buys, **this lane flags the conflict and
rules nothing.**

### 6.5 T5 in one line

**T5 is `PENDING` — not `BLOCKED`.** Its reference is held, verified, and carries
a stated uncertainty; nothing about it needs Sanaa's *permission to acquire*. What
stands between it and Bucket A is **a rewritten pre-registration on the matrix
configuration with a re-derived ladder and a re-derived cost** — writing work, not
compute — **plus a ruling on who may freeze it.**

---

## 7. TASK 5 — THE 24-HOUR QUEUE. Bucket A holds exactly one rung.

### 7.1 The claim under test, and the verdict on it

**Claim:** *"Bucket A is EMPTY except K0d — no second committed pre-registration
with unrun compute anywhere in the territory."*

**Verdict: REFUTED, in both directions.**

- **K0d is NOT in Bucket A.** It is **`BLOCKED`** at HEAD by the heat-transfer
  supervisor's own committed ruling,
  `docs/campaigns/F14-cooling-ladder/K0d_FIRE_RULING_2026-08-25.md`, whose verdict
  line reads: *"**Verdict: `BLOCKED`.** Zero core-minutes spent against a
  registered POINT of 829.36. K0d remains **FROZEN, ARMED, UNFIRED**;
  `K0d_runs/` does not exist."* **Confirmed from disk by this lane: a `find` over
  `verification/runs` for any `*K0d*` directory returns nothing.** K0d supplies
  **0 cores now and for the whole 24-hour window.**
- **T8 IS in Bucket A.** It was committed at 20:25Z today, after the board's
  sweep, in one commit carrying **both** the pre-registration and its comparator.

**So the sentence is wrong about its one member and wrong about the set being
otherwise empty — but it is RIGHT about the thing that matters: the queue holds
one rung and then stops.**

### 7.2 The census, re-derived at HEAD by this lane

`git ls-tree -r` over the two campaign folders at HEAD returns **29 committed
`*PREREGISTRATION*` / `*REREGISTRATION*` documents**. Each was resolved against a
run directory on disk. **Every one has fired except four, and none of the four is
idle fireable compute except T8:**

| # | item | state |
|---:|---|---|
| 1 | **`T8_PREREGISTRATION`** | **BUCKET A — committed, frozen, comparator on disk, UNFIRED** |
| 2 | `K0d_PREREGISTRATION` / `K0d_REREGISTRATION` | **`BLOCKED`** — §7.1 |
| 3 | `K2b_3D_UNSTEADINESS` (`K2bU3_D`) | **built, never run, BY REGISTERED DESIGN.** Its control gate did not pass, so the test was correctly not run — `K2bU_TIERING_DETERMINATION_2026-08-25.md:44`, *"NEVER RUN, BY REGISTERED DESIGN"*. **The empty directory is the instrument working, not an opportunity. Firing it would break the registered gate order.** |
| 4 | `T5_PREREGISTRATION_DRAFT` / `T8_PREREGISTRATION_DRAFT` | **drafts, not pre-registrations** |

`T9aD` looks like unrun compute and is not: its pre-registration registers, at its
own lines 9–10, that the arm runs inside `T9a_runs/` under the prefix `D_`. Those
case directories and their `DONE.`/`STATUS.` markers are on disk and
`T9aD_RESULTS.md` grades seven rows. **Fired.**

`T1b_L4_EXT2` is **RUNNING NOW** — the three `buoyantBoussinesqSimpleFoam`
processes in §1, at 04:38:08 elapsed. **Not to be touched.**

### 7.3 THE RANKED QUEUE

**Row 1 is the only row that may legally fire. Every row below it needs a
document first, and a document is not compute.**

| rank | rung | **prereg COMMITTED at HEAD (rule-2 freeze)?** | **comparator EXISTS on disk?** | **est. core-min** | **est. cores** |
|---:|---|---|---|---:|---:|
| **1** | **T8** — `T8_MTT_c` / `_m` / `_f`, MTT plume, DC spine position 3 | **YES** — `T8_PREREGISTRATION.md`, HEAD blob `dd008248f60c2fa351d103f3be199d9e660e36d0`, **worktree byte-identical** | **YES** — `verification/runs/T-family/T8_runs/analyse_t8.py`, HEAD blob `d82c98ae2caf5cf2eb1c01140061cc92295ea82b`, **identical**, 84,817 B, **committed in the SAME commit as the prereg** | **335.34 POINT** (7.13 / 42.81 / 285.40), **cap 595** | **3** (`ranks = 1` each) |
| 2 | T3 fourth mesh level (`R_m`/`R_f`/`R_ff`) | **NO** — needs its own costed pre-registration | reuses `analyse_t3.py` — **VERIFY** | **9,000–12,000** (registered rough bound, not a costed figure) | 3 |
| 3 | T5 heated cubes, matrix configuration | **NO** — committed only as a DRAFT, and §6.3 makes it un-promotable as written | **VERIFY** — no T5 comparator located on disk | **unregistered — VERIFY.** The draft's 1,300–2,900 is for the **superseded single-cube** ladder and must be **re-derived, not rescaled** | 4 / 4 / 8 as drafted — **also superseded** |
| 4 | T11 transient conjugate entry arm (EXACT) | **NO — no `T11_*` document of any kind exists** | **NO** | ~300–600 — **VERIFY**, this is a bound, not a registration | 3 |
| 5 | T4 impinging jet, **flow rows only** | **NO** | **NO** | **VERIFY** | **VERIFY** |
| — | **K0d** | committed, but **`BLOCKED`** | registered | **0** | **0** |
| — | T12 | no | no | **0 — `BLOCKED`, §3** | 0 |
| — | T2 | no | no | **0 — `BLOCKED` on its reference, §5** | 0 |

**T8's supporting numbers, read off the frozen document** (`§8`, `§6`), so the
supervisor need not re-open it:

| case | cells | `endTime` | ranks | POINT core-min | cap | `timeout = cap × 60 ÷ ranks` |
|---|---:|---:|---:|---:|---:|---:|
| `T8_MTT_c` | 6,400 | 8,000 | 1 | 7.13 | 15 | 900 s |
| `T8_MTT_m` | 25,600 | 12,000 | 1 | 42.81 | 80 | 4,800 s |
| `T8_MTT_f` | 102,400 | 20,000 | 1 | 285.40 | 500 | 30,000 s |
| **total** | | | **3** | **335.34** | **595** | |

**Derived, not measured:** POINT 335.34 core-min = 5.589 core-h = **$0.287**; cap
595 core-min = 9.917 core-h = **$0.509**, at the recorded c7a.4xlarge rate
$0.0513/core-h. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). **Reference tier: partial EXACT** —
Morton–Taylor–Turner plume theory is closed form, **so T8 is the one rung on this
board with no acquisition step and nothing blocked on a paper.**

**T8 is UNFIRED, verified on disk:** `T8_runs/` holds the three scripts and a
`__pycache__` and **no case directory of any kind**, so the freeze condition's
*"zero core-minutes have been spent on this rung"* is true as measured. *(The
`__pycache__` mtime is 21:09Z, consistent with a `--selftest` import; it is not a
solve, and no case directory exists.)*

**Registered exposure carried forward, not smoothed over (prereg R6):** T8's rate
`1.196e5 cell·steps/(core·s)` is borrowed from `K2bU3_L025`, a **transient
PIMPLE** case, while T8 is **steady SIMPLE-family**. The arithmetic is exact; the
**rate** is the exposure and the direction of the error is not predicted. **At
completion this must be attributed as `misprediction` in the
`docs/COST_CALIBRATION.md` row, never absorbed into the ratio** (rule 12).

### 7.4 Occupancy — and the honest answer is that the box stays mostly idle

Assumptions stated so they can be checked: non-thermal occupancy **0** at 21:17Z
(**VERIFY** — `docker ps` denied, L-41); one core left unallocated for the session,
git and the instruments; `ranks = 1` throughout, so core-minutes and wall-minutes
coincide.

| t | event | cores / 16 | utilisation |
|---|---|---:|---:|
| **0** | **fire all three T8 cases at once** — 13 cores free, **no staging needed** | **6** | **37.5 %** |
| ~7 min | `T8_MTT_c` retires | 5 | 31.3 % |
| ~43 min | `T8_MTT_m` retires | ~4 | ~25 % |
| ~1–1.5 h | the three EXT2 arms retire | ~1 | ~6 % |
| ~4.8 h | `T8_MTT_f` retires | **0** | **0 %** |

**Peak thermal occupancy is 37.5 %, reached at t = 0, and it only falls. Sanaa's
80–90 % band is not reachable today by any legal means available to this team,
and this lane will not write a schedule implying otherwise.** T8 is a **long
pole, not a wide one** — one warm core for 4.8 hours.

**Memory is not the constraint.** `MemAvailable` 27.1 GiB at 21:17Z; T8's three
levels need ~0.50 GB at the measured 2.386 kB/cell; the family's standing launch
floor is `MemAvailable` < 12 GiB. **Re-read `MemAvailable` immediately before
launch anyway** — the binding memory risk is another team's container, not this
one.

**The measurement-integrity constraint, preserved because it is a MEASUREMENT
argument and not a cost argument, and so survives Sanaa's cost directive
untouched:** T8's cap is enforced as a wall-clock `timeout`, admissible **only**
because `ranks = 1` makes core-minutes and wall-seconds coincide. **Under
contention wall inflates and core-minutes do not**, so a contended case can be
killed by its timeout while still under its core-minute cap — and **a level
killed by its cap is `PENDING`, a right-censored measurement, never `GATE
FAIL`.** At 6 of 16 the timing basis stays clean; `T8_MTT_f` at 11 % contention
would need ~19,008 s against a 30,000 s timeout, **1.58× headroom. No core
reservation is needed for T8.** Any future rung capping wall-clock at `ranks > 1`
inherits this hazard **without** the numerical coincidence that makes it
admissible.

### 7.5 THE QUEUE IS EMPTY AFTER T8, AND THIS LANE SAYS SO PLAINLY

**Total legally fireable thermal compute in the next 24 hours: three single-rank
cases, 335.34 core-minutes POINT, 3 of 16 cores. The box has 13 free.**

**The bottleneck is not cores, not memory, and — since Sanaa's directive — not
cost. It is COMMITTED PRE-REGISTRATIONS, and rule 2 makes that non-negotiable:
the gate is frozen before the solver starts.** This team cannot spend its way out
of it and cannot fire its way out of it. **It can only write its way out of it.**

**What this lane would put in front of Sanaa, in priority order — reported as
material for the supervisor's message to her, not as a request this lane makes:**

1. **Lane-shifts for pre-registration WRITING, not compute.** Four documents
   stand between this team and a full box: the **T3 fourth-mesh-level** prereg
   (the only item large enough to hold cores for *days* — 9,000–12,000 core-min);
   a **T11 EXACT entry-rung** prereg (**cheapest new compute on the board, no
   acquisition step, no document exists yet**); a **T4 flow-rows** prereg; and
   the **T5 matrix rewrite** (§6.3) — plus a **K0d re-registration** resolving its
   over-determined `Ra`. **Three lanes writing in parallel would convert ~10
   cores of work within a shift.**
2. **A decision on the missing primaries — every one is a send, and sends are
   hers alone (rule 7).** **Blay 1992** (K0d's P column — `K0d_PREREGISTRATION.md`
   already records that she has purchased the ASME volume and *the PDF is not yet
   on disk*, so **this may be the cheapest P column on the board to close: it
   needs no money, only the file**); **Vogel & Eaton 1985** (T3); **Nielsen 1990 /
   Restivo 1979 / Schwenke 1975** or the benchmark web page (T12); **a Zukauskas
   source stating its validity range** (T2); **Tian & Karayiannis Part II** (K0cS's
   single-source caveat). **This lane attempted none of them and proposes no route
   around rule 7.**
3. **Her offer of more cases, taken up specifically.** The T-family and the DC
   spine are **reference-starved, not compute-starved.** The most useful new work
   she could hand this team is **rungs whose reference is closed-form or already
   on disk** — the T1c / T8 / T11 shape, which graded a rung the whole class was
   recorded as blocked on. **A new rung needing an unobtainable paper adds a
   document and zero core-minutes.**
4. **A tier-definition ruling** on §5.3, told about T1b before it is made.

**And the two things needing no permission at all:** the **two remaining
load-bearing unverified PDFs** (§4.5 — Vierendeels, which carries K0c's stated
applicability limit, and Zou/Zhao/Chen, which supplies K0d's case inside a frozen
document), each **one reading and zero core-minutes**; and **landing the
uncommitted 503-line audit** (§2), with its Tian row corrected on the way in.

---

## 8. COST, AND THE RULE-12 CALIBRATION

**Pre-registered: ZERO core-minutes. Actual: ZERO core-minutes. Ratio 1.00.**

No solver, no mesher, no case directory, no MPI rank, no GPU. The work was PDF
page rendering, `find`/`grep`/`git hash-object` sweeps and reading — single-rank
interactive filesystem work the lab does not meter in core-minutes, and **this
lane does not invent a figure for it.** **Derived dollar cost $0.00 — derived,
not measured**, because the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

**No row is added to `docs/COST_CALIBRATION.md`.** There is no compute row to
calibrate, and a calibration row built from an invented baseline is worse than an
absent one. **Flagged rather than absorbed**, per the same judgment
`SIDECAR_VERIFICATION_2026-08-25.md` §6 recorded for its own uncosted OCR run.

---

## 9. WHAT THIS LANE COULD NOT VERIFY — stated plainly

1. **The nine `NOT VERIFIED` PDFs in §4.5 were not verified here.** Six title
   pages were read; nine remain. **Vierendeels and Zou/Zhao/Chen are the two that
   matter**, and both are still open. Each is one reading and zero core-minutes.
2. **Other teams' live occupancy.** `docker ps` is denied to this user and **L-41**
   says a process sweep is blind to fleet agents. No non-thermal solver was
   visible at 21:17Z. **The whole of §7.4 assumes their occupancy is zero.
   VERIFY before any launch.**
3. **The repo-wide title-page record count outside this territory** (Roshko,
   Greenblatt, Breuer, the Ansys manual) is **cited from other records, not
   re-opened by this lane. VERIFY.**
4. **Whether `analyse_t3.py` can serve T3's fourth mesh level unmodified. VERIFY.**
   Note the defect registered in T8's own pre-registration: `analyse_t3.py:384`
   and `analyse_t1c.py:337` both compute the **inverted** Richardson form
   `f_fine + e21/den`, survivable only because it is display-only there.
5. **T5's and T11's core-minute figures in §7.3 are rough bounds, not registered
   numbers. VERIFY** — neither has a costed pre-registration, which is precisely
   why neither may fire. **T5's drafted figures are additionally SUPERSEDED** by
   the configuration ruling and must be re-derived, not rescaled.
6. **`analyse_t8.py` was not read as a diff by this lane.** Its blob matches HEAD
   and it was committed with its pre-registration; **whether it discharges every
   §11/§9/§7/§12 obligation the frozen text places on it is a measurement-script
   review, and `SUPERVISION_CHARTER.md` §3 reserves that to the supervisor
   personally. NOT DONE HERE.**
7. **Whether the ERCOFTAC Case 079 `.dat` archive is what it says it is** was not
   independently re-derived — its sha256 and fetch record are cited from its
   manifest. This lane **could not** re-derive it, since re-fetching is a send.
8. **Whether any of the nine remaining PDFs would FAIL if opened is unknown.**
   Zero have failed, across ten thermal papers now read. **That is a reason to
   expect them to pass. It is not evidence that they will** — L-144 exists
   because a journal-and-year sanity check once passed on the wrong document, and
   the lab was burned again this week when `High_order_grid_convergence.pdf`
   turned out to be Ekaterinaris 2005 on high-order low-diffusion schemes,
   carrying zero Roache, zero GCI and zero Richardson.
9. **The Blay 1992 absence** rests partly on a filename exclusion over PDFs with
   no sidecar, and **rule 15 says a filename is not verification.** `NOT
   OBTAINED` on strong evidence; **not proven to rule 15's positive standard.**

---

## 10. WHAT THIS DOCUMENT DOES NOT DO

- **It launches nothing and authorises nothing.** Every fire order is the
  supervisor's.
- **It creates, moves and retires no gate, threshold, band, cap or label**, and it
  edits **no tier** — not T2's, not T5's, not T12's — and **no verdict**.
- **It edits no frozen document.** Every figure quoted from `T8_PREREGISTRATION.md`,
  `K0d_REREGISTRATION.md`, `T5_CONFIGURATION_RULING.md` and
  `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` sits **beside** the frozen text,
  never in place of it. **No amendment was appended to anything.**
- **It did not commit another lane's uncommitted 503-line audit** (§2), flagged
  so somebody can be dispatched to land it — with its Tian row corrected (§4.3).
- **It sends nothing. SUBMISSIONS REMAIN PARKED** (rule 7). Acquiring Blay 1992,
  Vogel & Eaton 1985, Nielsen 1990, Restivo 1979, Schwenke 1975, a Zukauskas
  source or Tian & Karayiannis Part II is a **send**, and sending is Sanaa's
  alone. **No search for any of them outside this box was made or is proposed.**
- **No agent's message was treated as Sanaa's consent** (rule 9). The two
  questions this lane found to be tier-definition questions are marked as hers and
  are not answered here.

---

*Written by a heat-transfer lane, 2026-08-25, 21:12–21:20Z. Zero core-minutes. No
solver ran, no gate was graded, no tier or verdict was edited, nothing was
acquired from outside the box, and nothing was sent, filed or submitted.*
