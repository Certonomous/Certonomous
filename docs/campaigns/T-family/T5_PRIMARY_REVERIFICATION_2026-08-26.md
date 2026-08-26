# T5 — primary re-verification **PASSES**, and the reference's own header carries a binding constraint on the pre-registration

**Written by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26. ZERO COMPUTE.**
**No pre-registration was written and nothing was frozen by this file.** Nothing has been
sent, filed, submitted, uploaded, registered or posted outside this box (`CLAUDE.md`
rule 7).

---

## 0. Verdict on the check I was sent to make

**The T5 primary re-verification PASSES on all three limbs.** The sha256 matches, the
sidecar is present and real, and the title-page verification exists as a record that
names what the title page says. **Nothing here stops T5.**

**But the reference carries a constraint that changes how its pre-registration must be
written, and it is stated in the reference's own provenance header rather than inferred
by me.** §4.

## 1. sha256 — MATCHES

| | |
|---|---|
| path | `docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf` |
| **sha256 on disk, computed 2026-08-26** | **`36c89a548030eae2aac84f2453c7c531632998433da660f4b655624cff6514cb`** |
| `T_FAMILY_INDEX.md` T5 row | `36c89a54…` — **matches** |
| the sidecar's own recorded sha | `36c89a548030eae2…cff6514cb` — **matches in full** |
| size | 15,477,157 bytes; **281 pages** (`pdfinfo`) |

**Three independent records agree**, and the third is the strongest: the sidecar records
the sha of the PDF it was generated from, so a sidecar/PDF mismatch would be visible
here and is not.

## 2. Sidecar — present and REAL, and a historical trap is measured closed

`FILING_CHARTER` R9 requires a PDF and its `.txt` sidecar to travel together. Both are
present. **The sidecar is not a stub:**

| measure | value |
|---|---|
| bytes | **605,484** |
| **non-whitespace characters** | **503,207** |
| lines | 13,220 |

**This matters because this exact file was the lab's known counter-example.**
`THERMAL_REFERENCE_TITLE_PAGE_AUDIT.md` §1.2 names *"the Meinders trap — a 281-byte
sidecar of pure form-feeds that satisfied R9 while holding zero characters."*
**A rule that counts files rather than content passed that sidecar.** The trap is
measured closed here: 503,207 non-whitespace characters, not 0.

## 3. Title-page verification — the RECORD EXISTS, and I read it rather than greping for the words I expected

**Read, not greped — L-337's fourth axis, on the instruction that produced it.**

**The record is inside the sidecar's own provenance header**, and it is better than a
citation elsewhere because it travels with the artifact:

> *"TITLE PAGE, TRANSCRIBED BY READING THE RENDERED PAGE IMAGE BY EYE (not from the OCR
> below), 2026-08-24 UTC, standing rule 15:*
> *Title: Experimental study of heat transfer in turbulent flows over wall-mounted cubes*
> *Type: Proefschrift (doctoral thesis)*
> *Degree: ter verkrijging van de graad van doctor aan de Technische Universiteit Delft,
> op gezag van de Rector Magnificus prof. ir K.F. Wakker*
> *Defence: maandag 2 november 1998 te 13:30 uur*
> *Author: Erwin Rinaldo MEINDERS, werktuigkundig ingenieur"*

**Every element of the filename's claim is discharged by the page itself**:
`meinders` = Meinders; `1998` = defended 2 November 1998; `tudelft` = Technische
Universiteit Delft; `thesis` = Proefschrift; `wall_mounted_cubes` = the title, verbatim.

**Cross-checked against the territory audit, by reading its list rather than searching
for a word:** `THERMAL_REFERENCE_TITLE_PAGE_AUDIT.md` §1.4 enumerates the **nine**
`NOT VERIFIED` papers by name. **Meinders is not among them**, and §1.3 records the
territory at **VERIFIED 10 / NOT VERIFIED 9 / FAILED 0 of 19**. **No thermal PDF has
ever FAILED rule 15.**

## 4. ⚠ THE CONSTRAINT — the PDF is an IMAGE-ONLY SCAN, and its own header forbids the normal path to a band

**This is the finding, and it is not a defect in the reference. It is a property of it
that the pre-registration must be built around.**

The sidecar's header, verbatim:

> **THIS PDF IS AN IMAGE-ONLY SCAN. IT CARRIES NO TEXT LAYER.**
> *Verified 2026-08-24/25 UTC: `pdftotext` over the whole file exits 0 and yields 281
> form-feed characters and ZERO non-whitespace characters; a page-by-page sweep of all
> 281 pages individually also yields zero non-whitespace characters on every page.*

**And the zero was controlled** — the same poppler 24.02.0 binary in the same session read
121,044 non-whitespace characters from the Narumanchi PDF and 32,787 from Bahrami in the
same directory. **A zero from a reader demonstrated able to see a non-zero** (standing
rule 3, applied to a text extractor).

**The body of the sidecar is therefore OCR** (tesseract 5.3.4, `-l eng --psm 1`, 300 dpi
grey renders), **and it is marked `Proofread: NO`.** Its header states the binding rule:

> **"this is a 1998 print scan and OCR of it is NOT TRUSTWORTHY AT THE LEVEL OF A DIGIT…
> NO NUMBER READ FROM THIS FILE MAY BE USED AS THE VALUE A GATE DEPENDS ON, quoted as a
> printed value, or entered into a pre-registration. Any number that matters must be
> taken by rendering the page and READING THE PAGE IMAGE."**

**I confirmed the OCR is that bad by looking at it**: equation (3.9) in §3.2.4 comes
through as `2 Fly rey A Peg 92` / `dea T? b ? 2 had ? 2`. **Unusable, exactly as
advertised.**

## 5. THE LOAD-BEARING NUMBER, TAKEN THE WAY THE HEADER DEMANDS — rendered and read as an image

The T5 row's `P` column rests on *"stated uncertainty 5 % mid-face / 10 % edges in local
`h`"*. **I did not take that from the index, and I did not take it from the OCR.** The
OCR was used only for what its header says it is for — *"so that a grep can FIND a
page"* — and the page was then rendered at 150 dpi and **read as an image**.

**PDF page 61 (printed page 59), section heading "Overall accuracy of the heat transfer
coefficient", read from the rendered image:**

> *"From the above analysis of the different contributions to the experimental
> uncertainty it is concluded that the accumulation of errors results in approximately
> **5% accuracy in the local heat transfer coefficient for the mid-region of the five
> faces of the cube**. The heat transfer coefficients at the edges have a somewhat higher
> **uncertainty of about 10 %** due to, among others, mapping inaccuracies."*

**The index's claim is CONFIRMED.** Two precisions it elides, and both belong in a
pre-registration that cites this number:

1. **"the five faces of the cube"** — the cube is wall-mounted, so the mounting face is
   excluded. A band written as though six faces are covered would overstate the
   reference.
2. **Both figures are hedged in the source** — *"approximately 5%"* and *"about 10 %"* —
   and both are on the **LOCAL** `h`, not on an average. **A band that treats
   "approximately 5%" as an exact ±5.000 % is reading a precision the author did not
   claim.**

**Corroboration of the sidecar's own warning, in passing:** it states the PDF-page to
printed-page offset drifts to about +2 by Chapter 3. **Measured: PDF page 61 is printed
page 59 — offset exactly +2.** The header is accurate about itself.

## 6. WHAT THIS MEANS FOR THE T5 PRE-REGISTRATION — and it is why I stopped here

`T_FAMILY_INDEX.md` records that T5's *"data are digitisable figures, no tabulated
appendix"*. Combined with §4, that gives the honest shape of the work:

> **EVERY REFERENCE VALUE T5 GRADES AGAINST MUST BE DIGITISED FROM A FIGURE IN AN
> IMAGE-ONLY SCAN. There is no table to read and no text layer to extract. The
> pre-registration's `P` column cannot be written by quoting the paper — it can only be
> written by digitising rendered page images and registering the digitisation itself as
> an instrument.**

That is a materially heavier and more error-prone step than reading a tabulated
appendix, and this lab has a live record of exactly how it goes wrong: T3's digitiser
carries its axis calibration in **two `assert` statements** (`digitise_t3_secondary.py:190`,
`:191`) that `python3 -O` deletes — disclosed this morning as Class A instances A5 and A6,
because **a mis-calibrated digitiser produces a silently wrong reference and surfaces as
nothing at all.**

**So the digitisation is not a preliminary to the pre-registration — it is part of the
instrument the pre-registration must freeze**, and it needs:

- the figures identified by page and figure number, rendered at a stated dpi;
- an axis calibration with a **refusal**, never an `assert` (`exit 2`, driven under `-O`);
- a **planted control with a measured detection floor** (L-334) — for a digitiser, a
  known point placed at a known data coordinate and recovered;
- the digitised values committed as a data file **with the render provenance beside
  them**, so a later reader can re-render the same page and check;
- and the **hedged** uncertainty of §5 carried through as hedged.

**This is the point at which I stop and report, as instructed.** Not because a check
failed — all three passed — but because **the reference's own header rules out the way a
pre-registration normally cites a primary**, and choosing how T5's `P` column is
constituted under that constraint is a design decision above a lane.

## 7. What I did NOT do

- **No pre-registration was written and nothing was frozen.**
- **No tier was interpreted, redefined or extended.** T5's promotion is the supervisor's;
  the tier *definition* is reserved to Sanaa, and nothing here touches it.
- **No number from the OCR entered any record.** The only numbers quoted from the
  reference in this file are from a **rendered page image**.
- **No solver was launched and nothing is queued. Zero core-minutes.**
