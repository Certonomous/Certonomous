# T5 reference path — attempt record, 2026-08-26

Lane: `lab-lane 64b13819` (heat-transfer), the T5 reference lane, under the
heat-transfer supervisor's ruling of **2026-08-26T17:02Z** (PATH 1 → 2 → 3, stop
at the first that yields a reference with a passing planted control). Decisions
`[lab-attributed]` under Sanaa's standing order (silence is approval). Nothing
here has been sent, filed, submitted, uploaded, registered or posted anywhere
outside this box (`CLAUDE.md` rule 7).

**Outcome: PATH 2 yielded.** `T5_reference_primary.A7_PROPOSED.json` (blob
`04dfd7e2e56a`), 9 rows, `digitised: true`, produced by
`digitise_t5.A7_PROPOSED.py` (blob `9a465d7bacb0`) with **three closed-frame
planted controls passing in the same run**. The amendment text is drafted, NOT
appended, at `docs/campaigns/T-family/T5_AMENDMENT7_DRAFT.md`; the unified diff
for the supervisor's personal check-1 read is `T5_runs/digitise_t5.A7.diff`
(2 399 lines, +2 392 / −2, blob `357d96936486`).

---

## 1. LEGALITY — this is POST-FIRST-GRADED-COMPUTE, and it is disclosure-only

`ls -d <case>/[0-9]*` over the six graded cases at **2026-08-26T22:39:29Z**:
`T5_CUBE_c` `0/ 3000/ 4000/ 5000/`; `H_c` `0/ 3000/ 4000/ 5000/`; `T5_CUBE_m`
`0/ 3000/ 4000/ 5000/`; `P_m` `0/ 3000/ 4000/`; `L_m` `0/ 1000/`; `T5_CUBE_f`
`0/` only. **Five of six graded case directories hold a numeric time directory,
so the pre-compute window is closed.**

**The reference amendment touches no gate, no band rule, no threshold, no cap and
no label.** It lands on the **reference-extraction path** that §10 of the frozen
pre-registration registered to happen *after* the comparator freeze and that
§16.11 item 2 recorded as still owed. §7.3's combination rule, §7.4's floors,
§7.5's triple gate and §16.4's ruling stand unaltered; `analyse_t5.py` stays blob
`9c2c1d44` and `run_one_t5.sh` stays `313df45c`. **It is disclosure-only for the
reference-extraction path and is stated as such, not as a pre-compute amendment.**
§10's separation is met: this lane wrote neither `analyse_t5.py` nor
`build_t5.py`, touched `build_t5.py` at no point, and **opened no T5 solver
output**.

## 2. PATH 1 — a TABLE in the thesis: DOES NOT EXIST

- Title page verified by this lane per L-144 (PDF page 5 rendered and read by
  eye): *Experimental study of heat transfer in turbulent flows over
  wall-mounted cubes*, Proefschrift, TU Delft, **Erwin Rinaldo MEINDERS**,
  2 November 1998. PDF `sha256` `36c89a54…6514cb`, identical to §7.6's
  registered value.
- **0** occurrences of `Table <n>` and **0** of `TABLE` across the 281-page OCR
  sidecar, against **172** figure captions in the same file (the reader is
  demonstrated able to see caption words — it is not a blind zero). No *List of
  Tables* in the contents. The two `tabulat` hits are prose (p. 22 sample-count
  criteria; Appendix A epoxy properties).
- Every graded quantity is published **only as a plotted figure** (5.41, 5.42,
  5.45, 5.37, 5.38, 5.39). **PATH 1 cannot produce a transcription because there
  is nothing to transcribe.** No increment-0 double transcription was attempted.

## 3. PATH 2 — AMENDMENT 7: RESUMED, not restarted; what was already there and what this lane added

The work-in-progress `digitise_t5.A7_PROPOSED.py` (blob `001d81bc`, 131 KB,
21:20Z, survivor of two lane deaths) was **resumed**. As found it already
carried: the closed-box frame finder, inward-tick finder, registered-anchor
calibration, the template symbol reader with `explain_away`, the points and path
closed-frame controls, `produce_reference`, and a selftest of 3 frozen arms +
2 controls + 12 driven refusals — **all passing**. It could read **Fig. 5.45**
and **refused Figs 5.37 and 5.39**.

**What was measured on the two refusing figures (this lane).** On the real
`fig537_lower_crop.png` the symbol reader returns **66 circles (correct), 1
square of 66, 3 triangles of 66**: consecutive printed squares *touch* (side
10 px at 11–12 px pitch) so their edges merge and a ring template reads recall
0.68 against the required 0.82, while the thin-armed `+`/`×` templates over-fire
(**385** and **360** candidates for 66 true markers) and `explain_away` then
removes the real triangles as claimed by those spurious neighbours. Scans over
symbol size 9–13 px, ring tolerance 0.75–1.5 px and ink dilation 1–2 px did not
recover the squares (best: 30 of 66). **Threshold-turning against the real page
until it read was refused as fitting the reader to the answer.**

**What this lane added: a RANK reader** — no symbol identification at all;
column-wise ink groups merged at one symbol height, a column *resolved* only at
exactly five groups, the registered series taken by rank from the top (legend,
PDF p. 151: `T_co = 80` uppermost, **75 second**), tracked column by column from
a resolved seed with a hard **anchor self-check** (the track must still be the
rank-2 curve at every resolved column, within 3.0 px, else exit 2). Detail and
provenance in `docs/campaigns/T-family/T5_AMENDMENT7_DRAFT.md` §7.3(c).

**Measured separation of the two path figures** (deskewed, in-frame columns,
merge gap 12 px): **Fig. 5.37 560 of 905 columns resolve into exactly 5 curves
(0.619)**; **Fig. 5.39 0 of 907 (0.000)**. Fig. 5.39's series overlap and cross —
§7.3 of the frozen text predicted this in advance — so no rank is registered for
it and the reader **exits 2**.

### 3.1 The three planted controls, all in the same channel as the artifact

Channel measured, not assumed (`pdfimages`, PDF p. 162: 1926 × 2816, bpc = 1,
CCITT G4, 301 × 300 ppi); every control is rendered at 300 dpi, skewed by the
measured 0.1006°, hard-thresholded to 1 bit, speckled at the measured 4.40 % from
a fixed seed and round-tripped through CCITT G4.

| control | plant | recovered vs planted | verdict |
|---|---|---|---|
| closed-frame **POINTS** (5.45 shape) | 20 gated markers + 30-marker low-`Re` pile-up, 5 symbol series | 20/20, 0 spurious; **y MAX 0.1453 W/m²K = 0.1615 % of span**, RMS 0.0970; x MAX 8.11 = 0.1352 % | **PASS** |
| closed-frame **PATH**, symbol reader (5.37 shape) | 66 markers, 53 in the central windows, at the page's pitch | 52/53, 0 spurious; per-marker **y MAX 0.0533 °C = 0.1776 %**, RMS 0.0249; partition-mean MAX **0.0188 °C = 0.0628 %** | **PASS** |
| closed-frame **RANK** (5.37 shape; **the reader that produces `G5a-c`**) | **the whole curve** — 66 line-connected markers; 570/906 columns resolve; 250 usable columns per window | partition means planted/recovered 58.5241/58.4279, 60.1491/60.0508, 58.5380/58.4258 → **MAX mean error 0.1122 °C = 0.3740 % of span (GATED)**; per-column MAX 0.5920 °C = 1.9732 %, RMS 0.1671 (reported) | **PASS** |

**L-340 compliance, explicitly.** `G5a-c` are delivered by an **averaging**
reader (a mean over 250 columns). A point plant would be diluted ~1/√N and would
refuse a working reader — L-340's measured failure. **The plant is therefore the
entire curve**, and a shift of it moves the recovered mean one for one; the
selftest drives a 5 %-of-span shift and requires rc 2. A **mutation control**
tracks rank 1 (`T_co = 80`) against the rank-2 plant and requires rc 2, so a
reader returning anything rank-independent cannot pass.

**Instrument discipline.** `--selftest`: **3 frozen arms + 3 closed-frame
controls + 16 driven refusals, 0 FAILED, rc 0 under BOTH `python3` and
`python3 -O`**. `ast.Assert` nodes: **0**.

### 3.2 The reference produced

`T5_reference_primary.A7_PROPOSED.json`, 9 rows, `digitised: true`:
`G1a` **83.654**, `G2a` **55.224**, `G3a` **59.286** W/m²K (increment
**1.2605** W/m²K, forecast 1.3, **−3.0 %**); `G5a` **55.995**, `G5b` **60.294**,
`G5c` **58.502** °C (increment **0.5920** °C, forecast 0.5, **+18.4 %**); both
inside §10's registered 50 %-over-forecast refusal. `G1`–`G3` **ABSENT** with
Fig. 5.39's refusal text carried in the file (REPORTED-only rows under §16.4).
`h̄_cube` = **65.840 W/m²K** from the five faces of Fig. 5.45.

Two checks from the thesis's own prose, neither used to select a value, both
hold: the **front** face is the largest of the five (impinging flow, printed
p. 157) and the **top** face is the lowest (*"the top face has the lowest
averaged heat transfer coefficient"*, printed p. 157).

**The frozen `T5_reference_primary.json` (blob `0ee14235`) is UNTOUCHED and still
reads `digitised: false`. The frozen `digitise_t5.py` is `e55d6208`, unedited.**

## 4. A §16.9 FREEZE-SET FILE HAD DRIFTED ON DISK — restored, drift preserved

Reported by the grading lane at 22:2xZ and acted on first.
`T5_runs/digitise_t5.py` carried worktree blob **`ea789ea64d63`** (mtime 16:48Z,
+929/−1 vs HEAD) — an earlier dead A7 lane had edited a **frozen** file in place.
Preserved as `T5_runs/digitise_t5.WORKTREE_DRIFT_1648Z.py` (`mv`, never deleted);
frozen bytes restored from HEAD; the file now hashes **`e55d6208c511`**, the
§16.9 value. `digitise_t5.A7_PROPOSED.py` descends from the **FROZEN** file, not
from the drift (first 600 lines: 97 diff lines vs frozen, 387 vs drift). The
drift carries one capability the A7 file lacks — `pair_labels`, a `tesseract` OCR
pairing of printed tick **labels** against tick positions with its own refusals —
preserved for a possible later amendment, **not adopted here**.

## 5. WHAT REMAINS BLOCKED, and what would unblock it

| item | state | what would unblock it |
|---|---|---|
| `P` rows in `analyse_t5.py` | **BLOCKED** | `analyse_t5.py` (blob `9c2c1d44`) contains **no reference reader at all**: its `main()` prints the completion lines then the fixed *"No case has run…"*. The `P` rows are blocked by the comparator's own construction as much as by the reference. Gates are closed (§2), so this lane may not repair it. **Supervisor's decision: a new registration for a comparator that grades against the reference, or a dated ruling on how the `P` rows are produced.** |
| `G1`–`G3` (`h/h_tot`, Fig. 5.39) | **ABSENT** (REPORTED-only under §16.4) | Fig. 5.39's five series do not separate (0 of 907 columns). Would need either a higher-resolution source for that figure or a reader that separates crossing series — neither of which this instrument claims. |
| §10 D4, D5, D6 (Figs 5.38, 5.41, 5.2, 5.3) | **NOT DIGITISED** | `R1`, the ±8 % `h̄_cube` cross-check and the `I1`/`I2` inflow checks. Not required to unblock the `P` rows; still owed. |
| Adoption of AMENDMENT 7 | **PENDING** | The supervisor's personal check-1 read of `T5_runs/digitise_t5.A7.diff`, then appending `docs/campaigns/T-family/T5_AMENDMENT7_DRAFT.md` to the frozen pre-registration and pointing the grading path at `T5_reference_primary.A7_PROPOSED.json`. |

## 6. SHARED-INDEX HAZARD, inspected and NOT reverted (`CLAUDE.md` rule 10)

At this lane's commit time the **shared index carried 1 431 staged DELETIONS**
(234 of them under `T-family/T5_runs/`) against 40 staged non-deletions. A bare
`git commit` would have landed them. This lane committed under the private-index
protocol and verified afterwards that only its own paths landed. **The staged
deletions were inspected and left exactly as found — the index is the chief's
call.**

## 7. Cost

Zero compute owed and none consumed: no solver, no case, no queue entry. The work
is reader development and figure digitisation on the lane's own process.
