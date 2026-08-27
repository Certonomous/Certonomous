# T5 AMENDMENT 10 — DRAFT — the grading driver

**STATUS: DRAFT. NOT ADOPTED, NOT PROMOTED, NOT FROZEN.** Nothing in this file has
been sent, filed, submitted, uploaded, registered or posted anywhere outside this
box (`CLAUDE.md` rule 7). `analyse_t5.py` is **untouched** and remains blob
`9c2c1d44`. The proposed driver is held beside the case as
`verification/runs/T-family/T5_runs/analyse_t5.A10_PROPOSED.py` and **has been run
on no real T5 case**.

Drafted by lab-lane `64b13819` (heat-transfer, lane 4) on the heat-transfer
supervisor's standing ruling of 2026-08-27, at 2026-08-27T16:52Z.

---

## The two labels this amendment must state in its own words, before anything else

Every verdict the proposed driver can ever write carries **both** of the
following, and they are printed by the instrument itself at the head of its own
report, not only recorded here:

1. **Graded by an instrument written AFTER compute to text frozen BEFORE it.**
   The bands, floors, gates, gate order, row definitions and controls are quoted
   from §7 and §16 of a document frozen before the first solve. The *driver that
   applies them* did not exist when the solver ran. That is a weaker evidentiary
   position than the one §2 of the charter is written to produce, and no wording
   here improves it.

2. **The author of this driver had already read the reference values.** §10
   registers the opposite ordering in terms — *"the answer for T5 must be that
   the comparator's author had never seen a Meinders `h` value"* — and for this
   section that ordering is **BROKEN and unrepairable**: lane `64b13819` is the
   lane recorded in `T5_reference_primary.json`'s own provenance block as the
   digitiser (AMENDMENT 7). It is stated here rather than discovered later.

   **The one auditable mitigation, and it is a property a reader can check in
   thirty seconds, not a promise:** *no reference value is hard-coded in the
   driver.* Every reference number is read from the frozen JSON at run time. The
   audit, re-run at commit: each of `83.654`, `55.224`, `59.286`, `55.995`,
   `60.294`, `58.502`, `65.840`, `65.728`, `65.308`, `1.2605`, `0.592`, `4442.5`,
   `0.866`, `0.958` occurs **0 times** in the driver's source. The only numeric
   constants in it are quoted from §7/§16 with their citation on the same line.

   **The supervisor may reasonably rule that this is not enough** and assign the
   driver to a lane that has not read the reference. That decision is his; this
   draft exists so it can be taken on the facts.

---

## (a) Condition (`CLAUDE.md` rule 2), and how it was CHECKED — this is POST-compute and it is stated plainly

**Document version 1.9 -> 1.10. Lines whose number changed above this section: 0
— and, per the chief's fleet stop-order of 2026-08-27T16:58Z, that assertion is
NOT sufficient on its own and is not offered on its own: the 1 610 lines of
`T5_PREREGISTRATION.md` above the insertion point are asserted BYTE-IDENTICAL to
the same span of the file's blob at HEAD, checked in the same shell invocation as
the write. A line-count assertion passes on a substituted file of the right
length.**

**The pre-compute window is CLOSED and this amendment does not pretend otherwise.**
Checked at 2026-08-27T16:52Z by reading the run tree, not by assertion:

| case | `STATUS` | core-min | `DONE` marker |
| --- | --- | ---: | --- |
| `T5_CUBE_c` | rc=0, capped=0, note=clean | 16.083 | present |
| `T5_CUBE_m` | rc=0, capped=0, note=clean | 75.650 | present |
| `T5_CUBE_f` | rc=0, capped=0, note=clean | 319.167 | **ABSENT** (see finding F5) |
| `H_c` | rc=0, capped=0, note=clean | 16.567 | present |
| `P_m` | rc=0, capped=0, note=clean | 68.883 | present |
| `L_m` | rc=0, capped=0, note=clean | 54.933 | **ABSENT** (F5) |
| `X_2d` | rc=0 (UNGRADED precursor, AMENDMENT 1) | 5.217 | present |
| `S_m` | built, never run | 0 | — |

The grid triple `T5_CUBE_c/m/f` is **complete for the first time**: 410.900
core-min across the three levels, each holding `0/ 3000/ 4000/ 5000/`.

**This amendment is therefore admissible under §2's post-compute rule only as a
dated addendum that alters no gate, threshold, cap or label — and §(d) below
demonstrates that it does not, rather than asserting it.** It lands on the
**grading path**, which §16.11 recorded as owed and which §10 registered as a
task to be performed after the comparator freeze.

---

## (b) The defect this repairs, stated as it actually is

**The frozen comparator contains no grading driver at all.**
`verification/runs/T-family/T5_runs/analyse_t5.py` (blob `9c2c1d44`, 415 lines)
has a `main()` that prints three completion lines and then the fixed sentence

> `No case has run: no rows are graded and no verdict is written.`

**unconditionally.** `grade_row`, `band_verdict`, `gci_triple` and `gate_yplus`
exist and are reachable **only from `--selftest`**. There is no row extraction
from the fields and no reference loader. Three separate runs of it have now
printed that same fixed sentence with a complete triple on disk
(`log.analyse_t5.20260826T211657Z.txt`, `…T221331Z.txt`, `…T223248Z.txt`).

**The registration discloses this nowhere.** §16.10's instrument discipline
records the selftest arm count and the `-O` behaviour — both true — and neither
of those facts is a statement that the file can grade a row. AMENDMENT 7's
closing paragraph named the defect for the `P` rows in passing; this amendment
names it as what it is: **a registration defect on the grading path**, found by
the heat-transfer supervisor's personal read on 2026-08-27.

---

## (c) What changes — the driver, and the shape of the change

A NEW file `verification/runs/T-family/T5_runs/analyse_t5.A10_PROPOSED.py`,
descending from the frozen `9c2c1d44`. The unified diff is preserved for the
supervisor's `SUPERVISION_CHARTER.md` §3 check 1 at
`verification/runs/T-family/T5_runs/analyse_t5.A10.diff`.

**The shape of the diff is the point, and it is auditable in one line:**

- **The first 390 lines are BYTE-IDENTICAL to the frozen blob** — asserted by
  `cmp` against `git cat-file blob 9c2c1d44 | head -390`, in the same invocation
  as the write, not carried forward from an earlier one.
- **7 lines are deleted, and they are the entire body of the frozen `main()`**:
  the three-line completion loop, its `print`, and the fixed sentence. Nothing
  else is removed. The full list of deleted lines is short enough to read in the
  diff and is reproduced there.
- Everything else is **addition below the frozen prefix**.

`gci_triple`, `band_verdict`, `grade_row`, `gate_yplus`, `check_completion`,
`gate_converged`, `classify_series`, `read_status`, `read_yplus`, `refuse` and
the frozen `selftest()` are **called, never rewritten**. The frozen `selftest()`
is invoked first by the new `selftest_a10()` and its 16 arms still run and still
print their own line.

---

## (d) THE DEMONSTRATION THAT NO GATE, THRESHOLD, CAP OR LABEL MOVES

Not asserted — enumerated, with the frozen text beside each.

| registered quantity | frozen text | in the driver | moved? |
| --- | --- | --- | --- |
| band rule | §7.3 "`sqrt( stated² + digitisation² )`" | `band_for()`, that expression, both components printed separately per §16.7.2 | no |
| G5 band | §7.3 "0.4 °C" ⊕ measured increment | read from the JSON: `sqrt(0.4² + 0.592²) = 0.7145 °C` | no |
| G1a–G3a band | §7.3 10 % ⊕ measured increment | read from the JSON | no |
| intrinsic floor | §7.4 "1.7 % on every `h` row" | `FLOOR_PCT` = 1.7 for G1a/G2a/G3a, **`None` for G5** — §7.4 names no floor for a `T_sur` row and inventing one would be adding a threshold | no |
| y+ sublayer bound | §16.3.1 `y+ ≤ 5.0` | frozen `YPLUS_MAX`, untouched | no |
| y+ ladder tolerance | §16.3.1 2.0× the level target | frozen `YPLUS_TARGET_TOL`, untouched | no |
| y+ wall set | §16.3.1 as amended by AMENDMENT 3 | frozen `YPLUS_WALLS`, untouched | no |
| gate ORDER | §7.5 (1)(2)(3)(4)(5)(6) | applied in that order; see §(e) | no |
| GCI safety factor | §7.5 `Fs = 1.25` | frozen `FS`, untouched | no |
| observed-order floor | §16.10 `P_MIN = 0.05` | frozen, untouched | no |
| convergence | §5.5 1e-6 of the field's range between `endTime−1000` and `endTime` | `CONV_TOL_FRAC = 1.0e-6`, `CONV_BACK = 1000` | no |
| completion | rule 4 / the frozen `check_completion` | called unmodified, `ENDTIME = 5000` | no |
| MB / HB | §6 0.1 % / 0.5 % | `MB_TOL_PCT`, `HB_TOL_PCT` | no |
| increment forecast | §10 "more than 50 %"; §7.3's forecasts 1.3 / 0.05 / 0.5 | `INCREMENT_FORECAST`, `INCREMENT_FORECAST_TOL = 1.5` | no |
| h̄_cube cross-check | §7.3 "more than 8 %" | `HBAR_CROSSCHECK_PCT = 8.0` | no |
| identity margin | §3 "at least 5 K from both bounds" | `IDENTITY_MARGIN_K = 5.0`, bounds `T_REF_K = 293.65`, `T_CORE_K = 348.15` | no |
| `T_ref` | §7.1 / INTERPRETATION 9 "293.65 K" | `T_REF_K` | no |
| central window | §7.1 "the central 80 % … excluding 0.1 H at each end" | `CENTRAL = (0.10, 0.90)` | no |
| graded set | §16.4 face-averaged `h` + G5 | `GRADED_ROWS` | no |
| plant constant | §9 `1.234e-03` | `PLANT` | no |
| cap | §11 / AMENDMENT 2 | the driver launches nothing and costs nothing | no |

**No threshold is added. None is widened. None is narrowed.** Where §7 states no
band for a row, the driver labels the row **`UNGRADED BY REGISTRATION`** and
says why, in those words.

---

## (e) §7.5's SIX branches, and the three the frozen instrument does not implement

§7.5 registers six branches. The frozen `grade_row` implements the y+
precondition, (1) iterative convergence and (2) the triple, then the band
verdict. **It implements no branch 3 (reference absent → `BLOCKED`), no branch 4
(the §3 identity guard → `NOT A RESULT — identity`) and no branch 5 (the
intrinsic floor → `GATE REACHED`).**

The driver applies those three **around** the frozen function, in §7.5's order:
`grade_row` is called unmodified — so the triple gating and the one-way
invariant are the frozen code's, not a reimplementation — and if it returns
`NOT A RESULT` from (0)/(1)/(2) that verdict stands untouched. Only if it did
not are branches (3), (4) and (5) consulted, in that order, before (6)'s band
verdict is allowed to stand.

**AMBIGUITY A4 below records that branch 5 and the frozen instrument's own
one-way invariant are in direct conflict.** That is not resolved here.

---

## (f) THE AMBIGUITY LIST — twelve items, left for the supervisor's call

**None of these is resolved by this draft.** Where the driver had to run at all
it carries a provisional reading, and every provisional reading is named here
with the line that produced it. A driver that quietly picks a reading is worse
than one that stops; this one picks loudly.

### A1 — the central-80 % window: CLIP the boundary cell, or keep WHOLE cells?
> §7.1: *"the arc-length-weighted mean of `h` over the **central 80 %** of each
> mid-line, excluding `0.1 H` at each end."*

**(a)** each face's weight is clipped to the window; **(b)** whole faces whose
centre lies inside the window are kept at full weight.
**Consequence:** under (b) the integration length depends on the mesh, so the
three levels of a Roache triple integrate over three *different* lengths — a
refinement-dependent bias inside the very construct that is supposed to isolate
refinement. **Driver: (a). Both are computed and both are printed on every row.**
**Recommendation: (a).**

### A2 — does the central-80 % truncation apply to G5 (`T_sur`) at all?
§7.1 defines *"Mid-line mean"* for `h`; §7.2's G5 row reads *"mid-line mean
`T_sur`"*. The two reasons §7.1 gives for the truncation are both `h`-specific
(the thesis's 10 % edge uncertainty; the base-plate conduction worth 5 %).
**(a)** yes — the defined term governs; **(b)** no — the rationale does not
transfer, so the full line is the row.
**Evidence for (a), and it is decisive on like-for-like grounds:** the frozen
digitiser took the reference through `PATH_CENTRAL = (0.10, 0.90)`, commented in
its own source *"S7.1: central 80 % of each partition"*, and the G5 values in
the frozen JSON are its `mean_central80`. A full-line CFD mean against a
central-80 % reference is not the same quantity.
**Driver: (a). Recommendation: (a), high confidence.**

### A3 — the SCALE on which G5's band is applied: °C or K?
> §7.3 header: *"Every band is `sqrt( stated² + digitisation² )` **in relative
> terms**"* — while the same table's G5 row is stated entirely in absolute °C,
> and §16.4 calls `0.4 °C` *"a stated **absolute** accuracy from printed p. 55,
> not a percentage inferred from a figure."*

**The frozen `band_verdict` is percentage-only**, so a scale must be chosen and
the registration never chooses one explicitly. `0.7145 °C` is **1.276 %** of
55.995 °C but **0.217 %** of 329.145 K.
**(a)** absolute in °C, expressed as a percentage of the reference *in °C* — the
identical test; **(b)** a percentage taken on kelvin.
**Driver: (a).** **Recommendation: (a) — (b) would narrow the band 5.9×, which
after compute is forbidden outright, so this is recorded as a trap the frozen
instrument creates rather than as a genuinely open choice.**

### A4 — §7.5 branch 5 registers `GATE REACHED`; the frozen instrument REFUSES it
> §7.5: *"5. deviation below the applicable intrinsic floor (§7.4) → **GATE
> REACHED**"*

against `analyse_t5.py:304`:
> `if rec["verdict"] not in (band, VERDICT_NAR): refuse("THE GATE TURNED A %s
> INTO A %s -- forbidden by CLAUDE.md rule 5. …")`

whose own comment cites *"analyse_t8.py under -O returns GATE REACHED where rule
5 forbids it."* **The registration's branch 5 and the frozen instrument's
invariant contradict each other.**
**(a)** branch 5 is applied outside `grade_row`, so the invariant is never asked
about `GATE REACHED` (what the driver does); **(b)** the invariant supersedes and
no floor may ever change a verdict.
**Live consequence for this rung: none.** §7.4 states a floor only for `h` rows,
and no `h` row is evaluable (finding F2), so the conflict is latent.
**Driver: (a). Recommendation: (a), and REFER the conflict — it is a
cross-family question about rule 5's scope and belongs on the verification
supervisor's desk, not this rung's.**

### A5 — a row whose reference VALUE is null in a PRESENT, DIGITISED file
> §7.5: *"3. reference file absent **or its `digitised` flag false with no
> values`** → **BLOCKED**"*

G1/G2/G3 carry `"value": null` in a file whose `digitised` flag is `true`.
Neither disjunct of branch 3 literally holds.
**(a)** `BLOCKED`, extending branch 3 to per-row absence; **(b)** `REPORTED` —
§16.4 already moved G1–G3 out of the graded set, so no verdict is owed and the
null is disclosed rather than adjudicated; **(c)** `NOT A RESULT`.
**Driver: (b) for G1–G3; branch (3) is implemented and selftested and would fire
on any GRADED row whose value was null.**
**Recommendation: (b).**

### A6 — §5.5's CONVERGED criterion versus the frozen `gate_converged`
> §5.5: *"**CONVERGED** means: the largest change of any cell value of `T` in
> either region, and separately of `U` in the fluid, between the checkpoints at
> `endTime − 1000` and `endTime`, is at most **1e-6 of that field's range**."*

The frozen file's `gate_converged(series, floor, sustain)` is a **residual-series**
criterion (C1 sustained floor + C2 not growing) and is wired to nothing.
**(a)** implement §5.5 and leave `gate_converged` frozen and unused; **(b)** grade
convergence on residuals through `gate_converged`.
**(b) is barred by §5.5 itself**: *"`residualControl` is not written (L-141: in
T1c a genuinely unconverged case sat at residual 4e-05, and in T3 the residual
was again not the instrument)."*
**Driver: (a).** `gate_converged` and `classify_series` are left byte-identical
and still exercised by the frozen selftest's three arms.
**Recommendation: (a). This is the largest single design decision in the driver
and it is flagged as such.**

### A7 — §5.5's *"that field's range"*: which checkpoint, and what is a vector's range?
**(a)** the range at `endTime`; **(b)** at `endTime−1000`; **(c)** the union. And
for `U`: **(i)** the max magnitude of the difference against the range of `|U|`;
**(ii)** componentwise.
**Driver: (a) + (i).** The two checkpoints differ by ~1e-6 of the range when the
criterion is met, so the choice cannot flip a verdict except exactly on the
boundary; the arithmetic is printed either way. **Recommendation: as implemented.**

### A8 — *"any cell value"*: internal field only, or boundary values too?
**Driver: internal field only** — `internalField` is what "cell value" names;
boundary faces are not cells. Recorded, low consequence. **Recommendation: as
implemented.**

### A9 — the GCI refinement ratio
> §7.5: *"unequal-ratio fixed-point form on the **effective** ratios from the
> actual cell counts"*

The frozen `gci_triple(f_c, f_m, f_f, r=2.0)` implements the **equal-ratio** form
and carries a **default `r = 2.0`**. The measured cell counts are 52 684 /
212 942 / 882 024, giving **r32 = 1.5929, r21 = 1.6060**, disagreeing by
**0.81 %** — and confirming §5.4's registered `r = 1.6` ladder on the actual
meshes.
**(a)** call the frozen function with `r = r21` and print both ratios and their
disagreement beside every GCI; **(b)** with the geometric mean; **(c)** implement
the unequal-ratio fixed point as new code.
**Driver: (a).** **Recommendation: (a). (c) is new grading code written after
compute and I do not recommend it without an explicit ruling. Leaving the default
`r = 2.0` in place would be wrong by 25 % in `log r` and would understate the
observed order everywhere — which is worth stating because it is what a driver
written without reading this line would have done.**

### A10 — I1/I2 UNMEASURED versus MISSED
§6 registers a consequence for a **miss** (*"carry the flag … and are REPORTED,
not graded"*), not for absence. §16.3.1 registers, **for the y+ gate
specifically**, *"a wall not reported → NOT A RESULT — an unmeasured
precondition is not a satisfied one."*
**(a)** unmeasured is reported as unmeasured and does not itself flag the rows;
**(b)** §16.3.1's principle generalises and unmeasured I1/I2 flags every row
REPORTED.
**Driver: (a), printed.** It changes no verdict here (finding F1 already does).
**Recommendation: supervisor's call; it becomes live only if y+ is ever
recovered.**

### A11 — two REGISTERED REFUSALS whose inputs were never produced
§7.3 registers that the comparator *"**refuses** if the reconstruction disagrees
with a direct read of Fig. 5.41 by more than 8 %"*, and §10 registers that *"the
comparator asserts that the front-face partition's `h` maximum sits in its upper
half"*. **Both read D5 / D2, and AMENDMENT 7 recorded that D5 and Fig. 5.39 were
not digitised.**
**(a)** print `UNMEASURABLE` and do not refuse, since both guard the G1–G3 scale,
which §16.4 made REPORTED; **(b)** a registered refusal that cannot run is an
unmeasured precondition and the run refuses.
**Driver: (a).** **Recommendation: (a) while G1–G3 are REPORTED; (b) the moment
anything is graded off `h̄_cube`.**

### A12 — may `postProcess` be re-run on the COMPLETED cases?
**This is not a §7 ambiguity. It is a compute-and-registration decision, and it
is the one that decides whether this rung can ever produce an `h` verdict at
all** (findings F1 and F2). Re-running the *registered* function objects
(`yPlus`, `wallHeatFlux`) over the existing `5000/` fields would recover both the
gate's input and the graded row's input without re-solving anything. It is still
compute on a case whose gates are closed, and the fields it writes would feed a
gate and a graded row.
**Reserved to the supervisor, and the registration half may be Sanaa's.** The
driver neither does it nor assumes it.

---

## (g) What the driver grades, and what it declares UNGRADED

**GRADED — the rows whose quantity is on disk and whose band is registered:**
`G5a`, `G5b`, `G5c` — mid-line mean `T_sur` on front / top / rear. The per-face
surface temperature is present in every `5000/air/T` as the `value` list of the
`compressible::turbulentTemperatureRadCoupledMixed` patches; the mid-line, its
arc lengths and the central-80 % window are computed from `constant/air/polyMesh`
(ASCII), by OpenFOAM's own fan decomposition for face centres and areas.

**NOT EVALUABLE — and this is NOT `NOT A RESULT`:** `G1a`, `G2a`, `G3a`. See F2.
`NOT A RESULT` is a verdict on a row that was evaluated and gated. These rows
were never evaluated, because the quantity their own definition names is not on
disk. The driver says exactly that and writes no verdict.

**UNGRADED BY REGISTRATION, stated rather than invented:** `G4` (§7.2: *"none —
the thesis states no uncertainty"*); `G1`–`G3` (REPORTED by §16.4, and their
reference values are null); `R1`, `R2`, `R3` (REPORTED, §7.2); `DS`, `DH`
(comparisons, REPORTED); `DP` and `DC` (their criteria are written on G1a–G3a and
on the face-averaged front-face `h`, so both are UNMEASURABLE while F2 stands —
`DC` is `UNMEASURED`, per §8's own boundary clause, not "satisfied").

---

## (h) FINDINGS — what reading the run tree established

**F1 — THE y+ GATE FIRES ON EVERY LEVEL BY CONSTRUCTION, AND NO y+ WAS EVER
MEASURED.** `yPlus.json` is **absent** in `T5_CUBE_c`, `T5_CUBE_m` and
`T5_CUBE_f`. `postProcessing/air/yPlus/0/yPlus.dat` carries **two header lines
and zero data rows** on all three levels, and **no `yPlus` field exists in any
time directory**. §16.3.1 registers *"`yPlus.json` absent → NOT A RESULT"* and
*"a wall not reported → NOT A RESULT"*. **Consequence: branch (0) fires on every
graded row on every level, so every graded row of this rung is `NOT A RESULT`
until y+ is recovered.** *Cause, measured rather than guessed:* the function
object is registered `writeControl writeTime; writeInterval 1000;` and the case
has three write times, so it never executed — while `wallHeatFlux`, under the
**identical** control, appended its `.dat` on every iteration (30 000 rows). Two
`fieldFunctionObjects` behaved differently under the same dictionary, and that
difference is itself worth recording.

**F2 — THE GRADED `h` SET CANNOT BE EVALUATED FROM THE ARTIFACTS ON DISK.** §7.1
defines the face average as *"the area-weighted mean of `h` over the whole face"*
with `h = φ″_conv/(T_sur − T_ref)` **per face**. The local `φ″_conv` is not on
disk: `wallHeatFlux` wrote per-patch **min / max / integral** to a `.dat` and
never wrote its field. Two things the driver deliberately does **not** do:
reconstruct the wall flux from `T` and `alphat` (that is a **new heat-flux
instrument** written after compute), and substitute the flux-weighted average
(`integral/area` over an area-averaged `ΔT`) — a **different quantity**, the one
§9's B2 registers as differing from the mean-of-local by 1–3 %.

**F3 — §9's boring prediction B2 is UNMEASURABLE** for the same reason: one of
its two averages *is* the mean-of-local. §9 required both to be computed from the
conjugate fine case. Recorded, not quietly dropped.

**F4 — §6's HB guard is UNMEASURABLE.** The conjugate heat balance needs a wall
flux on the air faces **and** on the epoxy inner surface; the `wallHeatFlux`
object is registered `region air` only, so the epoxy side was never instrumented
at all. **Neither half of the balance is on disk.**

**F5 — two completed cases carry no `DONE` marker.** `DONE.T5_CUBE_f` and
`DONE.L_m` do not exist at the `T5_runs` root although `STATUS.T5_CUBE_f` reads
rc=0 / capped=0 / note=clean / 319.167 core-min and `STATUS.L_m` reads rc=0 /
note=clean / 54.933. `mark_done_t5.py` has not been run for either. The driver
reads `STATUS` and the logs and applies rule 4 itself, so this does not block it
— it is an open bookkeeping item, and under the *bookkeeping-never-voids-physics*
rule it voids nothing.

**F6 — `T5_CUBE_c` carries an unactioned overrun.** `CAP_OVERRUN.txt`: elapsed
11 433 s against a registered 2 736 s (45.6 core-min), *"REPORTED, NOT ENFORCED …
The run was NOT killed"*; `ESTIMATE_OVERRUN.txt` records the same against the
estimate and notes the entry carried no registered cap. `CLAUDE.md` rule 12 says
an overrun **stops** the run. Surfaced for the supervisor; not this lane's to
adjudicate, and it bears on whether the coarse level's 16.083 core-min figure and
the queue's cost model are consistent.

**F7 — the registered ladder is confirmed on the actual meshes**: 52 684 /
212 942 / 882 024 cells give effective linear ratios 1.5929 and 1.6060 against
§5.4's registered `r = 1.6`.

**F8 — §10's increment-forecast refusal does NOT fire on the frozen reference**,
checked rather than assumed: Fig. 5.45 measured 1.2605 W/m²K against §7.3's
forecast 1.3 (ratio 0.970); Fig. 5.37 measured 0.592 °C against forecast 0.5
(ratio 1.184, inside the registered 1.5).

**F9 — §3's identity guard is satisfied by all three G5 reference values**,
computed by the driver at grade time and reproduced here only so the reader can
see the margins: 55.995 / 60.294 / 58.502 °C sit 35.50 / 39.79 / 38.00 K above
the inlet bound and 19.00 / 14.71 / 16.50 K below the imposed core bound, against
a registered margin of 5 K.

---

## (i) CONTROLS, and the evidence for each

**Planted zeros (`CLAUDE.md` rule 3), sized to each reader's shape (L-340).** A
constant offset is invisible to a dispersion reader *by construction*, so a plant
a reader cannot detect by construction is not a control. Each plant is written to
a **copy on disk** and read back **through the same function the graded row
uses**; each refuses `exit 2` on failure.

| reader | plant shape | why that shape | refuses |
| --- | --- | --- | --- |
| mid-line mean `T_sur` | constant offset `1.234e-03` | a MEAN reader sees an offset exactly | yes |
| §5.5 change reader | **single-cell spike** | a constant offset applied to both checkpoints CANCELS and is invisible by construction | yes |
| §5.5 range reader (the denominator) | spike on the extremal cell | a constant offset is invisible to a RANGE by construction — L-340 exactly | yes |
| reference loader | value offset in a JSON copy written and re-read | a comparator whose reference path nobody perturbed can be reading a cached zero | yes |
| y+ gate | the frozen four arms (compliant MET; `roof` at 30 fires; an unreported wall fires; an absent file fires) | unchanged from the freeze | yes |

**Selftest.** `--selftest` runs the **frozen 16 arms unmodified** and then 28 A10
arms: **16 + 28 arms, 0 FAILED, rc 0 under `python3` and under `python3 -O`, with
byte-identical output under both.** The synthetic case is a written-and-re-read
ASCII `polyMesh` plus fields; **the driver has touched no real T5 case.** The
synthetic patch uses **13 cells** deliberately, so the central-80 % window
boundaries fall *inside* cells and the clipping branch is actually exercised; the
synthetic profile is **quadratic**, because a linear one has the same mean over
the full line and over the central 80 % and could not tell a broken window from a
working one.

**`0 ast.Assert` nodes** (L-332), re-derived at commit, not recalled.

**Negative controls — 9 mutations, all caught, `rc != 0` under both
interpreters**, `__pycache__` cleared between the control and every mutant:

| | mutation | caught |
| --- | --- | --- |
| N1 | the central-80 window widened to the full line | rc 1 |
| N2 | the K→°C conversion removed | rc 1 |
| N3 | the mid-line plant read-back blinded | rc **2** (a refusal, as designed) |
| N4 | the y+ gate made to pass an absent `yPlus.json` | rc 1 |
| N5 | the §5.5 tolerance loosened by ONE decade | rc 1 |
| N6 | the identity-guard margin set to zero | rc 1 |
| N7 | §10's increment tolerance made infinite | rc 1 |
| N8 | **both** copies of the one-way invariant removed | rc 1 |
| N9 | the clipped mid-line mean swapped for the whole-cell one | rc 1 |

**Two of these controls initially failed to fire, and both failures are recorded
because they are the reason the arms are now worth anything:**

- **N1 survived** because the arm computed its expected value from `CENTRAL`
  itself, so mutating `CENTRAL` moved *both* sides of the comparison. The
  expectation is now a literal. **A test whose expectation is derived from the
  constant under test cannot fail.**
- **N1 then survived again** because the mutation's anchor text
  `CENTRAL = (0.10, 0.90)` is a **substring of the comment**
  `PATH_CENTRAL = (0.10, 0.90)` two lines above the real constant — so the
  mutation edited a comment and the executable value survived, while the control
  reported a clean "not caught" with no error. Every anchor is now newline-bound.
- **N8 survived** because `_drive_oneway_violation` carries its **own** copy of
  the invariant, so removing `grade_row`'s left the driven arm passing. N8 now
  removes both. **Recorded honestly: `grade_row`'s copy alone is UNCATCHABLE by
  any selftest, because it fires only on a state `grade_row` cannot itself
  produce.** It is a defensive invariant, not a tested one, and calling it tested
  would have been false.

**What is NOT verified, stated plainly.** The readers have **never been run
against a real OpenFOAM `polyMesh` or a real field file** — only against
synthetic ones this file wrote itself. That is the brief's instruction and it is
honoured. The design property that makes the gap acceptable is that **every
reader refuses (`exit 2`) rather than degrades**: a reader that cannot parse the
real mesh will stop, not return a wrong number. It is still a gap, and the first
run on `--root` is where it closes.

---

## (j) Cost

**This amendment launched no solver and consumed no rung compute.** The selftest,
the `-O` selftest and the negative controls together ran on 1 rank for well under
two minutes of wall time — **≈ 2 core-min of scratch**, not charged to the rung's
solve budget, on the AMENDMENT 8 / AMENDMENT 9 precedent. The rung's spend is
unchanged at **410.900 core-min** for the triple plus 141.383 for `H_c`, `P_m`,
`L_m` and `X_2d` (16.567 + 68.883 + 54.933 + 5.217) = **552.283 core-min gross**.
No estimate-versus-actual calibration row is owed yet: **no rung has been graded**
and none can be until this amendment is ruled on.

---

## (k) Not done by this amendment

`analyse_t5.py` is **NOT touched** and stays blob `9c2c1d44`. `digitise_t5.py`
stays `9a465d7b`; `T5_reference_primary.json` stays `04dfd7e2`; `run_one_t5.sh`
stays `313df45c`; `mark_done_t5.py` stays `a74ce20d`; `build_t5.py` stays
`9d7be1cb`. **§16.9 is not amended and no freeze-set row moves** — promotion of
the driver into the freeze set, if it happens at all, is a separate act on the
AMENDMENT 3 pattern and is the supervisor's after his personal read of
`analyse_t5.A10.diff` (`SUPERVISION_CHARTER.md` §3 check 1). Every band, floor,
gate and gate order of §7 stands. Fig. 5.39, D4, D5 and D6 remain undigitised. No
row of this rung has a verdict, and **this draft asserts none**.

No permission setting, `CLAUDE.md` or `.claude/` config was touched (rule 9).
Nothing has been sent, filed, submitted, uploaded, registered or posted anywhere
outside this box (rule 7).
