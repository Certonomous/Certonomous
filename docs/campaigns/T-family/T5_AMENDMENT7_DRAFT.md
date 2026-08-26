# T5 — AMENDMENT 7 (DRAFT, NOT APPENDED): the digitiser reads the closed-box figures; the reference is produced

**This file is a DRAFT for the supervisor's personal check-1 read. It is NOT
appended to `docs/campaigns/T-family/T5_PREREGISTRATION.md`; the supervisor
appends it after reading `verification/runs/T-family/T5_runs/digitise_t5.A7.diff`
as a diff.** Nothing here has been sent, filed, submitted, uploaded, registered
or posted anywhere outside this box (`CLAUDE.md` rule 7).

Drafted by lab-lane `64b13819` (heat-transfer), the T5 reference lane, on the
heat-transfer supervisor's ruling of 2026-08-26T17:02Z. Decisions
`[lab-attributed]` under Sanaa's standing order (silence is approval).

---

## AMENDMENT 7 — 2026-08-26 (POST-FIRST-GRADED-COMPUTE): the digitiser reads the closed-box, inward-tick, line-connected figures; `T5_reference_primary.json` is produced; §16.7's measured increment is superseded

**Document version 1.7 -> 1.8. Lines whose number changed above this section: 0.**

**Disclosure only: no gate, no threshold, no band rule, no cap and no label
moves.** §7.3's combination rule (`sqrt(stated² + digitisation²)`), §7.4's floors,
§7.5's triple gate and its six-branch order, §7.2's row list and §16.4's ruling
that the FACE-AVERAGED set is the graded `h` set all stand unaltered. What lands
is the quantity §10 registered the digitiser to **measure** — its own increment —
and the values it reads. `analyse_t5.py` stays blob `9c2c1d44`; `run_one_t5.sh`
stays `313df45c`; `build_t5.py` is untouched by this lane.

### 7.1 Condition (`CLAUDE.md` rule 2), and how it was checked — this is POST-first-graded-compute and it is stated plainly

**Five of the six graded cases hold a numeric time directory at this write.**
`ls -d <case>/[0-9]*` over `T5_CUBE_c H_c T5_CUBE_m P_m L_m T5_CUBE_f` at
**2026-08-26T22:39:29Z**:

| case | time directories present |
|---|---|
| `T5_CUBE_c` | `0/ 3000/ 4000/ 5000/` (DONE 21:16:56Z) |
| `H_c` | `0/ 3000/ 4000/ 5000/` (DONE 21:16Z) |
| `T5_CUBE_m` | `0/ 3000/ 4000/ 5000/` |
| `P_m` | `0/ 3000/ 4000/` (running at this write) |
| `L_m` | `0/ 1000/` |
| `T5_CUBE_f` | `0/` only |

**So the pre-compute window is CLOSED and this amendment does not pretend
otherwise.** It is admissible under §2's post-compute rule *only* because it is a
dated addendum that alters no gate, threshold, cap or label: it lands on the
**reference-extraction path**, which §10 registered as a task to be performed
*after* the comparator freeze and *before* grading, and which was still owed
(§16.11 item 2: *"The reference values are NOT YET DIGITISED"*). **The lane that
did it read no T5 solver output** — §10's separation — and **did not touch
`build_t5.py`**.

**The separation of §10, restated and met.** §10 requires the digitiser to be a
T-family `lab-lane` that is neither the comparator's author nor `build_t5.py`'s
author. The frozen reference of 16:27Z recorded that this was **NOT** met (its
own `provenance.digitiser` says so). It **is** met here: lane `64b13819` wrote
neither file and opened no case's solver output.

### 7.2 What was tried first, and why it was not enough — PATH 1, the table search

The supervisor's ruling put a **thesis TABLE** ahead of any digitiser. It does
not exist. **Meinders 1998 contains no numbered table at all:** the 281-page OCR
sidecar
(`docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.txt`)
carries **0** occurrences of `Table <n>` or `TABLE` against **172** figure
captions, the contents pages carry no *List of Tables*, and the only two hits for
`tabulat` are prose (*"tabulated criteria"* for sample counts, p. 22; *"tabulated
properties of epoxy"*, Appendix A). The reader is not blind: the same grep sees
172 caption words in the same file. Every quantity T5 grades against — Figs 5.41,
5.42, 5.45, 5.37, 5.38, 5.39 — is published **only as a plotted figure**.

**Title-page verification (`CLAUDE.md` rule 15 / L-144), done by this lane, not
inherited.** PDF page 5 was rendered and read by eye: *"Experimental study of
heat transfer in turbulent flows over wall-mounted cubes / Proefschrift / ter
verkrijging van de graad van doctor aan de Technische Universiteit Delft … op
maandag 2 november 1998 te 13:30 uur / door Erwin Rinaldo MEINDERS,
werktuigkundig ingenieur, geboren te Hengelo (Ov.)"*. `sha256` of the PDF is
`36c89a548030eae2aac84f2453c7c531632998433da660f4b655624cff6514cb`, identical to
the value §7.6 registers.

### 7.3 The instrument: `digitise_t5.A7_PROPOSED.py`, and what it adds

The frozen `digitise_t5.py` (blob `e55d6208`) **refused all three registered
figures** and its refusals were correct: it looks for an **open L-frame with
outward ticks**, and the thesis plots are **closed boxes with inward ticks**,
with Figs 5.37/5.39 carrying **five line-connected symbol series** over a path
`A|B|C|D` with full-height partition lines. The frozen file's first 506 lines —
the open-frame reader, its raster control and its three selftest arms — are
carried **verbatim and unedited**; everything else is added below them.

| path | blob |
|---|---|
| `T5_runs/digitise_t5.py` (FROZEN, §16.9, untouched) | `e55d6208c511` |
| `T5_runs/digitise_t5.A7_PROPOSED.py` (this amendment) | `9a465d7bacb0` |
| `T5_runs/digitise_t5.A7.diff` (2 399 lines: **+2 392 / −2**) | `357d96936486` |
| `T5_runs/T5_reference_primary.json` (FROZEN, untouched) | `0ee14235bc8f` |
| `T5_runs/T5_reference_primary.A7_PROPOSED.json` (this amendment) | `04dfd7e2e56a` |
| `T5_runs/analyse_t5.py` (unchanged) | `9c2c1d44cfeb` |

**(a) A closed-frame reader.** `find_frame` takes the two outermost long
horizontal and two outermost long vertical ink lines as the frame and any
internal full-height vertical line as a path partition; `find_inward_ticks`
follows runs of ink leaving the frame lines *into* the plot; `calibrate_closed`
matches the found ticks to the **registered anchor VALUES** (never inferred from
the image) and refuses on a missing major, an ambiguous major/minor split, a
non-uniform spacing, a fit residual over tolerance, or an axis line that does not
sit on its first tick.

**(b) A symbol reader** for Fig. 5.45 — ring/interior/exclusive-recall template
matching with an `explain_away` separation rule for touching and overlapping
symbols.

**(c) A RANK reader, new in this amendment, for Fig. 5.37 — and it exists
because the symbol reader is MEASURED to fail on that figure.** On the real
`fig537_lower_crop.png` the symbol reader returns **66 circles (the true count),
1 square of 66, and 3 triangles of 66**: the printed squares of consecutive
points *touch* (side 10 px at an 11–12 px pitch, read off the deskewed raster),
their edges merge into single runs, and a ring template over a merged glyph reads
recall 0.68 where 0.82 is required; the thin-armed `+` and `×` templates then
over-fire on the dense ink (**385** and **360** candidates for 66 true markers)
and `explain_away` removes the real triangles as "claimed" by those spurious
neighbours. **A reader that returns 3 of 66 markers of the registered series is
not a reader, and turning its thresholds against the real page until it read
would have been a reader fitted to the answer, not a measurement.**

The rank reader uses a property of the **page**, registered before any value was
taken: Fig. 5.37 plots the same path for `T_co` = 60, 65, 70, 75, 80 °C, `T_sur`
rises monotonically with `T_co`, and the five line-connected curves **never
cross** — the thesis says so (printed p. 148: *"the temperature profiles are more
or less congruent"*) and the page shows it. So the reader **identifies no symbols
at all**. It scans the frame column by column, merges ink groups closer than one
symbol height (`RANK_MERGE_GAP_PX = 12`) into one curve, and calls a column
*resolved* only at exactly five groups; the registered series is taken by its
**rank from the top**, which the legend on PDF page 151 fixes (`T_co = 80`
uppermost, **`T_co = 75` second**). Because the in-frame `REAR`/`TOP`/`FRONT`
labels sit in the top eighth of the frame and the hottest series runs *through*
them, a pure rank read loses a band of columns (measured: a 0.174 path-unit hole
in the control's `TOP` window), so the reader **tracks** the curve column by
column from a resolved seed, taking the group nearest the previous centre and
stopping when the nearest is further than `RANK_MAX_JUMP_PX = 25 px`.

> **The self-check is the point.** At **every** column that does resolve into
> exactly five groups, the tracked centre must still be that column's rank-2
> centre within `RANK_ANCHOR_TOL_PX = 3.0 px`, else **exit 2**. A track that has
> slid onto a neighbouring series is caught the moment the series separate again.
> On the real crop the track disagrees at **0 of 146 / 182 / 134** resolved
> columns in `AB` / `BC` / `CD`.

**The track is bounded to §7.1's central-80 % window exactly, with no margin**,
and that bound was not chosen to make the reader work: with a 0.05-unit margin
the track ran into the corner dip at `B`, where all five curves plunge and merge,
and slid onto a neighbour — **the anchor check caught it and refused**
(*"at column 394 all 5 curves resolve and the tracked curve sits 22.4 px from the
rank-2 curve"*, rc 2). The margin that was removed was never part of §7.1's
registered window.

**(d) Fig. 5.39 REFUSES, and that refusal is the answer.** Its five
Reynolds-number series overlap and cross — §7.3 of the frozen text says so in
advance (*"a small scanned plot carrying five overlapping Reynolds-number symbol
series"*) — and the measurement agrees: **0 of 907** in-frame columns resolve
into exactly five curves, against the registered `RANK_MIN_USABLE_FRAC = 0.50`.
**No rank is registered for 5.39** and the reader exits 2 on it. Rows `G1`–`G3`
are therefore **absent** in the produced reference, with the refusal text carried
in the file. Under §16.4 those rows are **REPORTED**, not graded, so no graded
row depends on them.

### 7.4 THE PLANTED CONTROLS — three of them, and the plant is SIZED TO THE READER (L-340)

Every control **travels the same channel as the real artifact**, measured, not
assumed: `pdfimages` on PDF page 162 gives 1926 × 2816, **bpc = 1, CCITT G4,
301 × 300 ppi**; each control raster is rendered at 300 dpi, skewed by the
measured 0.1006°, hard-thresholded to 1 bit, speckled at the measured 4.40 %
from a fixed seed and round-tripped through **CCITT Group 4**.

**L-340 is the reason the third control exists in the shape it does.** `G5a-c`
are delivered by an **averaging** reader — the path-weighted mean over the
central 80 % of a partition, here over **250 columns**. A single-point plant
against such a reader is diluted by ~1/√N and would refuse a *working* reader:
that is L-340's measured failure (VMFL011, a 1.234e-3 point plant moving an
RMS over 401 points by 3.68e-7). **So the plant is the whole curve**: five
line-connected series of known values are rendered through the channel, and the
recovered curve is compared to the planted one **both** per column (a point read)
**and** as the partition mean (the averaged read the row actually uses). A shift
of the planted curve moves the recovered mean **one for one**, and the selftest
drives exactly that: a 5 %-of-span shift breaks the tolerance and returns rc 2.

| control | what is planted | recovered vs planted | verdict |
|---|---|---|---|
| **closed-frame POINTS** (Fig. 5.45 shape) | 20 markers at `Re ≥ 3000` of five symbol series in a closed box with inward ticks, plus a 30-marker low-`Re` pile-up | **20 / 20** recovered, 0 spurious of a graded series near the registered abscissa, 20 candidates rejected; **y MAX 0.1453 W/m²K = 0.1615 % of span**, RMS 0.0970; x MAX 8.11 = 0.1352 % of span | **PASS** |
| **closed-frame PATH, symbol reader** (Fig. 5.37 shape) | 66 markers of the registered series, 53 inside the central windows, at the page's measured pitch | **52 / 53** in-window recovered, **0 spurious**, 956 candidates rejected; per-marker **y MAX 0.0533 °C = 0.1776 % of span**, RMS 0.0249; partition-mean MAX err **0.0188 °C = 0.0628 % of span** | **PASS** |
| **closed-frame RANK** (Fig. 5.37 shape, the reader that produces `G5a-c`) | the same raster; **the whole planted curve**, 66 markers line-connected | **570 of 906** in-frame columns resolve into exactly 5 curves (0.629); **250 usable columns per window**; partition means planted/recovered **58.5241/58.4279**, **60.1491/60.0508**, **58.5380/58.4258** → **MAX mean error 0.1122 °C = 0.3740 % of span (GATED)**; per-column **MAX 0.5920 °C = 1.9732 % of span**, RMS 0.1671 (**REPORTED, never gated**) | **PASS** |

**Why the rank control gates the MEAN and reports the per-column error.** The
row takes the mean; no row takes a single column. A column cuts the polyline
vertically, so where the curve steepens the ink in one column spans a large range
and its centre is the midpoint of that span — a property of a column read, not a
defect. The per-column MAX is nevertheless carried **into** the digitisation
increment, which makes the increment **larger, never smaller**.

**Driven refusals, all of them, under `python3` AND `python3 -O`.** `--selftest`:
**3 frozen arms + 3 closed-frame controls + 16 driven refusals, 0 FAILED, rc 0**
under both interpreters; `ast.Assert` nodes in the file: **0**. Among the sixteen:
the planted curve shifted 5 % of span → rc 2; **the mutation control — track rank
1 (`T_co = 80`) and grade it against the rank-2 plant → rc 2**, so a reader
returning anything rank-independent cannot pass; a raster with no five-curve
structure → rc 2; no registered rank (the 5.39 case) → rc 2.

### 7.5 §16.7's MEASURED INCREMENT IS SUPERSEDED — struck, not deleted

**Struck from §16.7:** ~~`h` digitisation error, MAX = `0.2263 W/m²K` =
**`0.2514 %`** of the 0–90 span; RMS `0.1374`; `Re_H` MAX `7.07` = `0.1178 %`;
planted/recovered 6/6~~ — measured on the **open-frame** control of the frozen
instrument, i.e. on a channel shape the printed page does not have (open L-frame,
outward ticks, isolated markers). **The words stay on the page; the number no
longer governs.** §16.7.1's stated limit — that the figure is *"the error of an
ISOLATED marker"* and that **marker overlap is the largest un-modelled error
source** — is the reason it had to be superseded, and it is carried forward
below in a stronger form.

**REGISTERED IN ITS PLACE, from the closed-frame controls of §7.4:**

| | measured |
|---|---|
| `h` (Fig. 5.45) digitisation error, **MAX** | **`0.1453 W/m²K` = `0.1615 %` of the 0–90 span** |
| `h` (Fig. 5.45) digitisation error, RMS | `0.0970 W/m²K` |
| `Re_H` error, MAX | `8.11` = `0.1352 %` of span |
| planted / recovered, gated abscissae | **20 / 20**, 0 spurious |
| `T_sur` (Fig. 5.37) partition-mean error, **MAX** | **`0.1122 °C` = `0.3740 %` of the 40–70 span** |
| `T_sur` (Fig. 5.37) per-column error, MAX / RMS | `0.5920` / `0.1671 °C` (reported) |

**§16.7.2 stands unchanged: the EXPERIMENTAL (~5 % mid-face, ~10 % at edges,
both hedged in the source) and the DIGITISATION components are named separately
and never merged.**

### 7.6 The increments actually written into the reference, against §7.3's forecasts

§10 registers `digitisation_increment = max(symbol radius, blind-repeat spread)`
and requires the comparator to **refuse if the measured increment exceeds §7.3's
forecast by more than 50 %.** This amendment **widens the rule and never narrows
it**: the increment is `max(closed-control MAX error, symbol radius in data
units, blind-repeat spread)`.

| rows | forecast (§7.3) | measured increment | components (control MAX / symbol radius / blind-repeat spread) | vs forecast |
|---|---:|---:|---|---:|
| `G1a-G3a` (`h`, Fig. 5.45) | 1.3 W/m²K | **1.2605 W/m²K** | 0.1453 / **1.2605** / ≤ 0.32 | **−3.0 %** |
| `G5a-c` (`T_sur`, Fig. 5.37) | 0.5 °C | **0.5920 °C** | 0.1122 (mean) and **0.5920** (column) / 0.388 / 0.071 | **+18.4 %** |

**Both are inside the registered 50 % refusal.** The 5.45 increment is dominated
by the plotted **symbol radius**, not by the reader; the 5.37 increment is
dominated by the **per-column** control error, which is the conservative choice
described in §7.4.

### 7.7 The reference produced

`verification/runs/T-family/T5_runs/T5_reference_primary.A7_PROPOSED.json`
(blob `04dfd7e2e56a`, 9 rows, `digitised: true`). **The frozen
`T5_reference_primary.json` (blob `0ee14235`) is UNTOUCHED and still says
`digitised: false`; nothing is overwritten. The supervisor decides which file
`analyse_t5.py` is pointed at.**

| row | quantity | value | stated unc. | digitisation increment | source |
|---|---|---:|---:|---:|---|
| `G1a` | face-averaged `h`, **front** | **83.654 W/m²K** | 10 % = 8.365 | 1.2605 | Fig. 5.45, printed p. 160 (PDF 162), marker nearest `Re_H` 4440 |
| `G2a` | face-averaged `h`, **top** | **55.224 W/m²K** | 10 % = 5.522 | 1.2605 | as above |
| `G3a` | face-averaged `h`, **rear** | **59.286 W/m²K** | 10 % = 5.929 | 1.2605 | as above |
| `G5a` | mid-line mean `T_sur`, **front** (partition `CD`) | **55.995 °C** | 0.4 °C | 0.5920 | Fig. 5.37, printed p. 149 (PDF 151), `T_co = 75` curve, 250 columns |
| `G5b` | mid-line mean `T_sur`, **top** (`BC`) | **60.294 °C** | 0.4 °C | 0.5920 | as above, 250 columns |
| `G5c` | mid-line mean `T_sur`, **rear** (`AB`) | **58.502 °C** | 0.4 °C | 0.5920 | as above, 249 columns |
| `G1`,`G2`,`G3` | mid-line mean `h/h_tot` | **ABSENT** | — | — | Fig. 5.39 **REFUSED** (0 of 907 columns resolve); REPORTED-only under §16.4 |

`h̄_cube` reconstructed from the five faces of Fig. 5.45 (§7.3's registered
route, not Fig. 5.41's log-log): **65.840 W/m²K** from front 83.654, top 55.224,
rear 59.286, side (N) 65.728, side (S) 65.308.

**Two independent checks the thesis's own prose supplies, and both hold.**
(i) *"The high heat transfer coefficient at the front face … is indicative for
the impinging flow"* — the front face is the largest of the five, by 27 %.
(ii) *"Among these faces, the top face has the lowest averaged heat transfer
coefficient"* (printed p. 157) — **the top face is the lowest of the five**.
Neither check was available to the reader and neither was used to select a value;
they are stated because a symbol-to-face assignment that had been rotated would
have failed both.

**Blind repeats (§10's registered repeatability measurement), five perturbed
re-reads each:** `G5a` 55.963–56.034 (spread 0.071 °C), `G5b` 60.259–60.325
(0.066), `G5c` 58.475–58.546 (0.071).

### 7.8 What this amendment does NOT bound, stated where it cannot be missed

- **`G1`–`G3` are absent.** Fig. 5.39 does not separate and this instrument
  refuses on it. Under §16.4 they are REPORTED rows, so no graded row is lost;
  but the rung's `h/h_tot` shape comparison **cannot be made** from the
  registered reference.
- **The rank reader assumes what it can check and no more.** It checks that
  exactly five curves resolve on 62 % of columns and that its track agrees with
  the resolved rank at every resolved column. It **cannot** check that the legend
  order it was given (80 top … 60 bottom) is the page's; that order is registered
  from the legend on PDF page 151 and from the physics, and it is stated here so
  a reviewer can reject it.
- **`side (N)` and `side (S)` of Fig. 5.45 are read but not graded.** They enter
  only `h̄_cube`. Their symbols (`+`, `×`) overlap at low `Re_H` and the points
  control plants that overlap twice, but denser overlap than the plant is not
  bounded.
- **The comparator does not read this file.** `analyse_t5.py` (blob `9c2c1d44`)
  contains no reference reader at all: its `main()` prints the completion lines
  and then the fixed sentence *"No case has run: no rows are graded and no
  verdict is written."* **The `P` rows are blocked by the comparator's own
  construction, not only by the reference's absence**, and this amendment does
  not and may not repair a frozen comparator after first graded compute. That is
  a finding for the supervisor's desk, recorded and not finessed.

### 7.9 A §16.9 freeze-set file had DRIFTED in the worktree; restored, the drift preserved

Reported by the grading lane and acted on by this lane before any other work.
`T5_runs/digitise_t5.py` — a §16.9 freeze-set file — carried **unfrozen bytes on
disk** (worktree blob `ea789ea64d63`, mtime 16:48Z, +929/−1 against HEAD),
written by an earlier, now-dead A7 lane. **No frozen file may carry unfrozen
bytes on disk while a grade could read it.** Action, and nothing was deleted:

1. worktree copy hashed and confirmed `ea789ea64d63fd5d78364f4782974a6163351fce`;
2. **preserved** as `T5_runs/digitise_t5.WORKTREE_DRIFT_1648Z.py` (`mv`, never `rm`);
3. frozen bytes restored from HEAD; `git hash-object` reads
   **`e55d6208c511274a01d44b2a8ec0e9d979261fce`** — the §16.9 value.

**Descent, stated in one line:** `digitise_t5.A7_PROPOSED.py` descends from the
**FROZEN** `e55d6208`, not from the drift — its first 600 lines differ from the
frozen file by 97 diff lines and from the drift by 387 — and the drift carries
**one capability this amendment's file lacks**: `pair_labels`, an OCR
(`tesseract`) pairing of each printed tick **label** against the tick positions,
with refusals on an unpairable label, two labels sharing an anchor, and a paired
count that is not the registered count. `digitise_t5.A7_PROPOSED.py` instead
matches the found inward ticks to **registered anchor VALUES** and never runs OCR.
The drift is preserved so the supervisor can lift `pair_labels` into a later
amendment if wanted; it is **not** adopted here.

### 7.10 Not done by this amendment

1. **`analyse_t5.py` is not touched** and cannot be: gates are closed. It has no
   reference reader (§7.8).
2. **Fig. 5.39 is not read**; `G1`–`G3` stay absent.
3. **Figs 5.38, 5.41, 5.2, 5.3** (§10's D4, D5, D6 — `R1` mid-line, the ±8 %
   `h̄_cube` cross-check, and the `I1`/`I2` inflow checks) are **not digitised**;
   they were not required to unblock the `P` rows and remain owed.
4. **Nothing is sent, filed, submitted, uploaded, registered or posted anywhere
   outside this box** (`CLAUDE.md` rule 7).
