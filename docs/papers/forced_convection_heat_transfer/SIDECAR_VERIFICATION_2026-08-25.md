# Sidecar verification and OCR remediation — forced convection heat transfer, 2026-08-25

Heat-transfer lane, standing rule 15 (title-page verification) and rule 3
(planted-zero control). **Zero solver compute. No gate was graded. Nothing was
sent, filed or submitted.**

This record supersedes nothing in `PAPER_INTAKE_2026-08-24.md` except the single
claim identified in §3, which it corrects.

---

## 1. Inventory, as measured on disk

| File | Bytes | Sidecar non-whitespace chars |
| --- | ---: | ---: |
| `bahrami_2005_nasa_tm_212841.pdf` | 175,139 | — |
| `bahrami_2005_nasa_tm_212841.txt` | 38,690 | 32,787 |
| `narumanchi_hassani_bharathan_2005_nrel_tp540_38787.pdf` | 1,724,624 | — |
| `narumanchi_hassani_bharathan_2005_nrel_tp540_38787.txt` | 181,564 | 121,044 |
| `meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf` | 15,477,157 | — |
| `meinders_1998_tudelft_thesis_wall_mounted_cubes.txt` **(before)** | 281 | **0** |
| `meinders_1998_tudelft_thesis_wall_mounted_cubes.txt` **(after, this record)** | 605,484 | **501,467** |

---

## 2. Title-page verdicts (standing rule 15)

Each was verified by **opening the printed title page** — not by file type,
filename or hash. sha256 is recorded as an identifier, never as the
verification.

### 2.1 `bahrami_2005_nasa_tm_212841.pdf` — **VERIFIED**

- sha256 `0cd29adb20c0f6c21c07f37f101f0f8d3f3a7f85a81a95abc023da25a66f8be6`
- **Title as printed:** *Heat Transfer on a Flat Plate with Uniform and Step Temperature Distributions*
- **Author as printed:** Parviz A. Bahrami, Ames Research Center, Moffett Field, California
- **Report number as printed:** NASA/TM–2005-212841
- **Date as printed:** May 2005
- **Method:** text-layer extraction of PDF pages 1 and 3, **plus** an independent
  render of PDF page 3 read as an image. Both agree, and both agree with the
  first 60 lines of the pre-existing sidecar.
- **Sidecar state:** genuine. Byte-identical to a fresh `pdftotext` regeneration;
  16 form-feeds against pdfinfo's 16 pages.

### 2.2 `narumanchi_hassani_bharathan_2005_nrel_tp540_38787.pdf` — **VERIFIED**

- sha256 `e922da4f40af610b4afa5dc98534853801451e4739e38b4041904767d1a2b556`
- **Title as printed:** *Modeling Single-Phase and Boiling Liquid Jet Impingement Cooling in Power Electronics*
- **Authors as printed:** S.V.J. Narumanchi, V. Hassani, and D. Bharathan
- **Report number as printed:** NREL/TP-540-38787, Technical Report
- **Date as printed:** December 2005
- **Institution as printed:** National Renewable Energy Laboratory, 1617 Cole
  Boulevard, Golden, Colorado 80401-3393; operated for the U.S. DOE by Midwest
  Research Institute / Battelle, Contract No. DE-AC36-99-GO10337; prepared under
  Task No. FC05.7000
- **Method:** text-layer extraction of PDF pages 1–3, **plus** an independent
  render of PDF page 2 read as an image.
- **Sidecar state:** genuine and complete, and this was tested rather than
  assumed. It is **byte-identical** to a fresh `pdftotext -layout` regeneration;
  it carries **71 form-feeds against pdfinfo's 71 pages**; and a distinctive long
  line drawn from the sidecar's page blocks 5, 20, 35, 50, 65 and 71 was found in
  an independent single-page extraction of **that same PDF page** in all six
  cases.

### 2.3 `meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf` — **VERIFIED, BY EYE**

The PDF has no text layer (§3), so this one could only be verified by rendering
the pages and reading them.

- sha256 `36c89a548030eae2aac84f2453c7c531632998433da660f4b655624cff6514cb`
- **Title as printed:** *Experimental study of heat transfer in turbulent flows over wall-mounted cubes*
- **Author as printed:** Erwin Rinaldo MEINDERS, *werktuigkundig ingenieur, geboren te Hengelo (Ov.)*
- **Type as printed:** *Proefschrift* (doctoral thesis)
- **Degree as printed:** *ter verkrijging van de graad van doctor aan de
  Technische Universiteit Delft, op gezag van de Rector Magnificus prof. ir
  K.F. Wakker*
- **Defence as printed:** *op maandag 2 november 1998 te 13:30 uur*
- **Promotor as printed:** Prof. dr Dipl.-Ing. K. Hanjalić
- **ISBN as printed:** 90 - 9012103 - x; copyright © 1998 E.R. Meinders, Veldhoven
- **Method:** PDF pages 1, 3, 5 and 6 rendered at 160 dpi and **read as images**.
  Page 5 is the formal title page, page 6 its verso (promotor, committee, ISBN,
  funding); page 1 is the loose *Stellingen* leaf and page 3 the half-title, both
  of which independently carry title and author. A TU Delft library stamp
  (Prometheusplein 1, 2628 ZC Delft) and a handwritten "TR 3213" appear on the
  early leaves.
- **Filename match:** `meinders` / `1998` / `tudelft` / `thesis` /
  `wall_mounted_cubes` all correspond to the printed identity.

**No record in this repository contradicts any of the three readings.** The
sha256 values agree with `docs/campaigns/T-family/T_FAMILY_INDEX.md:45`,
`docs/campaigns/T-family/THERMAL_BUILDUP_DIRECTIVE.md:39` and
`docs/DOCKET.md:795`; the titles agree with
`docs/THERMAL_CAPABILITY_STATE.md:186`,
`docs/campaigns/F14-cooling-ladder/K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md:28`
and `PAPER_INTAKE_2026-08-24.md` §1.1–§1.3.

---

## 3. A CORRECTION to `PAPER_INTAKE_2026-08-24.md` §7

**The claim, as written** (`PAPER_INTAKE_2026-08-24.md:645-650`): *"the Meinders
sidecar was regenerated by **OCR** (`tesseract` 5.3.4, `-l eng`, over `pdftoppm
-r 300 -gray` renders of all 281 pages), with a `=== [PDF page N] ===` marker
before each page"*, under the heading **"Remediation applied to the artifact
itself"**.

**That remediation had not been applied to the artifact.** Until this record,
the sidecar on disk was **281 bytes, every one of them byte 0x0C (form feed),
zero characters of text** — a plain `pdftotext` output, not OCR, carrying no page
markers.

**The evidence, which is timing and is not a matter of opinion:**

1. `meinders_...txt` mtime **19:05:46.140** and `narumanchi_...txt` mtime
   **19:05:46.376** — **236 milliseconds apart**. That is one `pdftotext` sweep
   over the directory. OCR of 281 pages cannot complete in 236 ms; the run
   performed for this record took **3,079 seconds**.
2. The file's **ctime equals its mtime**, so nothing modified, renamed or
   re-permissioned it after 19:05:46.
3. `PAPER_INTAKE_2026-08-24.md` mtime **19:20:58** — written **15 minutes after**
   the sidecar it describes as remediated.
4. **No OCR artifact exists anywhere on the box**, including the four
   prior-session scratchpad directories under `/tmp/claude-1000/`.
5. The Meinders PDF's **atime is 19:15:32**, ten minutes after the sidecar was
   written — consistent with pages being rendered and read by eye, which is what
   §7 says was done for the quoted numbers, but nothing from that reached the
   sidecar.

**Assessment, stated as a finding and not as an accusation.** The reading work in
that record is sound: every §1.3 title-page field has been independently
reproduced here by eye, and §5's quotations check out. What happened is that a
remediation the lane **intended** was written up as one it had **performed**. The
lesson is narrow and worth keeping: *a record describing an artifact must be
checked against the artifact, because the record was internally consistent and
externally false* — which is standing rule 15's own warning, applied to a sidecar
rather than to a paper.

**Nothing else in `PAPER_INTAKE_2026-08-24.md` is impeached by this**, and its §7
defect report against `scripts/check_filing.py` R9 is independently **correct**
(§5).

---

## 4. Remediation actually applied

The Meinders sidecar has been regenerated and now holds real text.

| Quantity | Value |
| --- | ---: |
| PDF pages | 281 |
| Pages with OCR output | **281 of 281** |
| Pages with no OCR output | 0 |
| `=== [PDF page N] ===` markers | 281 |
| Bytes | 605,484 |
| Non-whitespace characters, whole file | 501,467 |
| Non-whitespace characters, OCR body excluding header | **499,083** |

- **Engine:** `tesseract` 5.3.4 (leptonica-1.82.0), `-l eng`, `--psm 1`
- **Renders:** `pdftoppm -png -gray -r 300`, in 20-page chunks, renders deleted
  per chunk to bound peak disk
- **Header:** the file opens with a provenance block stating that the PDF is an
  image-only scan, that the body is unproofread OCR, and — the operative clause —
  that **no number read from the file may be used as a value a gate depends on,
  quoted as a printed value, or entered into a pre-registration.** Any number
  that matters must be taken by rendering the page. The header also carries the
  by-eye title-page transcription of §2.3.

**Two refusal guards were armed before writing, and both are recorded because a
guard that never reports is indistinguishable from one that never ran:**

1. **Do not clobber a peer's work** — refuse unless the file on disk is *still*
   exactly 281 form-feeds at the moment of writing. **PASSED** (it was).
2. **Do not replace one useless sidecar with another** — refuse if the OCR body
   holds fewer than 100,000 non-whitespace characters. **PASSED**, at 499,083,
   which is 4.99× the threshold.

**The zero this replaces was a controlled zero, not a blind reader** (rule 3).
`pdftotext` was shown able to see a non-zero before its zero on Meinders was
believed: the same poppler 24.02.0 binary, in the same session, read **121,044**
non-whitespace characters from the Narumanchi PDF and **32,787** from the Bahrami
PDF. A page-by-page sweep of **all 281 Meinders pages individually** returned
zero non-whitespace characters on every one.

**Proof the remediation does the thing it exists to do.** Before, a sweep of
`docs/papers/` for the thesis's own uncertainty statement returned a clean zero.
It now returns the sentence *"accuracy in the local heat transfer coefficient for
the mid-region of the five faces"*, and a sweep for `ERCOFTAC` returns three
hits. That is precisely the failure R9 was written to prevent, no longer failing
for this file.

**OCR quality, stated honestly.** The title page transcribes cleanly and confirms
the identity independently of the by-eye reading. But the promotor's name comes
out as `Hanjali¢` and `Hanjalié` for **Hanjalić** on the very first body page —
the diacritic failure the header warns about, visible immediately. This is a grep
aid. It is not evidence, and it was not proofread.

---

## 5. The R9 defect stands, and is not fixed here

`scripts/check_filing.py` R9 tests only that a `.txt` **exists** beside the
`.pdf`. A sidecar of 281 form-feeds satisfied it while carrying zero characters —
reproducing exactly the failure R9's own source comment records it was written to
prevent (*"the sweep returned a clean zero and the zero meant nothing"*).

Remediating this one artifact **does not fix the rule**. R9 should test a
**content** property, with a planted control built from a text-free scan so the
rule is shown able to fire. **This lane did not edit the checker** — it is not
this lane's territory. Docket and lesson numbers are assigned at commit from the
tail (rule 11) and are **not** assigned here.

For context, `scripts/check_filing.py` currently reports **26 violations across 4
rules** repository-wide (R1×1, R5×4, R8×12, R9×9). **None of them are in
`docs/papers/forced_convection_heat_transfer/`**; all nine remaining
R9-SIDECAR-MISSING hits are PDFs sitting in the `docs/papers/` root. Those are
pre-existing and were not touched.

---

## 6. Cost

**Measured:** wall **3,079 s** (51.3 min) for the OCR run, on the 16-core
c7a.4xlarge.

**Derived, and stated as an upper bound rather than a measurement:** at full
16-core occupancy that is **821.1 core-minutes**. The true figure is **lower**,
because the `pdftoppm` render phase of each chunk is single-threaded while only
the tesseract phase is 16-way parallel; the lane did not instrument the split, so
the tighter number is not available and is not guessed. At the recorded rate of
$0.0513/core-h this is **≤ $0.70, derived and not measured** — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Comfortably inside the $25
pre-authorisation.

**Estimate-versus-actual calibration cannot be computed for this item, and that
is itself the finding.** Rule 12 requires the comparison at every process
completion, but **no pre-registered estimate for this work exists** — the task was
briefed as text extraction under zero compute, and the OCR was authorised as a
mid-task course correction without a costed pre-registration. **No ratio is
therefore stated, and none is invented.** No row was added to
`docs/COST_CALIBRATION.md`, because a calibration row with a fabricated baseline
would be worse than an absent one. Flagged to the supervisor as a real gap: work
of this size should have carried an estimate before it started.

---

## 7. Verdicts

| Paper | Verdict |
| --- | --- |
| `bahrami_2005_nasa_tm_212841.pdf` | **VERIFIED** — title page read, matches filename and every repository record |
| `narumanchi_hassani_bharathan_2005_nrel_tp540_38787.pdf` | **VERIFIED** — title page read; sidecar independently confirmed genuine, complete and page-traceable |
| `meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf` | **VERIFIED** — title page read as an image; image-only scan confirmed; sidecar regenerated by OCR with both guards passed |

**No `PASS` / `GATE FAIL` is claimed.** Those words belong to pre-registered
gates, and this record grades none.

---

## 8. What this lane could not verify

1. **The OCR was not proofread.** 499,083 characters of unchecked machine
   transcription of a 1998 scan. The `Hanjalić` failure on page one is the
   visible tip. It is a grep aid; the page image remains the evidence.
2. **Why the earlier record described an unperformed remediation** is not
   determinable from disk. The timing establishes **that** it did not happen, not
   **why** it was written as though it had.
3. **The tighter core-minutes figure** (§6) was not instrumented and is not
   guessed.
4. **The R9 fix was not written or tested** — not this lane's territory.
5. **The other 26 filing violations** were observed and left alone.
6. **Whether OCR sidecars should exist for image-only scans as lab policy** is a
   standards question above this lane. This lane produced one because it was
   directed to and because the alternative was a file that greps to nothing; the
   header is written so a reader cannot mistake it for a text layer.

---

*Written by a heat-transfer lane, 2026-08-25. No solver ran, no gate was graded,
nothing was sent, and no submission was prepared or filed.*
