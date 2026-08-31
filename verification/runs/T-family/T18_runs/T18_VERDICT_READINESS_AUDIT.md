# T18 — verdict-readiness audit against the three standing instruments

**FINDINGS ONLY. NO VERDICT IS DECLARED HERE, AND NONE MAY BE READ OUT OF THIS
FILE.** This document measures whether T18's already-computed result would
survive CLAUDE.md rules 3, 4 and 5. Declaring T18's rung verdict, and stating
its ceiling, is the heat-transfer supervisor's act. Written by a heat-transfer
`lab-lane`, 2026-08-31, `[lab-attributed]`.

**VOCABULARY NOTICE.** The fixed verdict words — PASS / GATE REACHED / GATE FAIL
/ NOT A RESULT / BLOCKED / PENDING (rule 1) — appear in this file **only inside
quotation marks, as strings read out of an artifact**. For this audit's own
clause-level findings the words used are **HOLDS** and **DOES NOT HOLD**, which
are deliberately not verdict vocabulary. A clause that HOLDS is a clause, not a
rung.

**HEADLINE, BLOCKERS FIRST: NO CLAUSE OF (a), (b), (c) OR (d) DOES NOT HOLD.**
Every clause of the strict completion rule holds on all four cases; all three
triples are independently monotone with recomputed orders and GCIs matching the
artifact to the last printed digit; every band resolves to the frozen
pre-registration by line number; and all three readers — not one — carry a
two-armed planted-zero control. The one open item is (e), and it is an
instrument-coverage gap, not a defect in any graded number: see §E.

---

## Provenance of everything cited

| artifact | state, measured this session |
|---|---|
| `docs/campaigns/T-family/T18_PREREGISTRATION.md` | frozen at commit **`add2c788`**, blob `ffa5b145398900827fcb67b77bdf7c03a6b93958`. `git hash-object` on the working-tree file returns the **same blob**, and `diff` against `git show add2c788:<path>` is empty. The working tree **is** the frozen document. |
| `verification/runs/T-family/T18_runs/analyse_t18.py` | blob `66477e3945f4a622c014613e941d671e0e5525b8`, sha256(16) `2372422cde2e47f8`, 539 lines — identical to the freeze table at `T18_PREREGISTRATION.md:315`. |
| `exact_t18.py`, `build_t18.py`, `mark_done_t18.py`, `run_one_t18.sh`, `T18_registered.json` | all five match their frozen blobs at `T18_PREREGISTRATION.md:313–318` exactly. **Six of six freeze-set files MATCH; zero DRIFT.** |
| `verification/runs/T-family/T18_runs/gate_t18.json` | 5186 bytes, mtime 2026-08-31T15:11:44.670072566Z, sha256 `335bbec520a20ff461398c0b7135e451b994459a7bc7f1dfdd63700afdd7e099`. |

Rule 2's grading-path clause is therefore satisfied by hash, not by assertion:
the file that ran is the file that was frozen.

**One extra provenance fact, measured, because it corrects a sentence already in
this directory.** `gate_t18.json` is **byte-identical** to the sealed artifact
`T18_SELFTEST_SIDE_EFFECT_NOT_A_GRADE_20260831T151045Z.json` — same size, same
sha256, same md5 `bba51110b76b6f0763a46e68c2c170ba`, `cmp` returns 0. Their
mtimes differ by 323.105 s and are not nanosecond-shared, so they are two
independent writes, not a copy. The companion note's sentence *"none of its
numbers are this rung's values"* is false **as written**: the numbers are the
same numbers to the last bit. The true statement is about **provenance** — the
selftest artifact is not the registered grade — while being numerically
indistinguishable from it. Read positively this is a determinism datum: see §E4,
where a **third** independent reproduction is measured.

---

## (a) STRICT COMPLETION RULE — CLAUDE.md rule 4, six clauses, four cases

**The registered field tuple is `('T',)`, and it was read from the frozen
document, not assumed.** `T18_PREREGISTRATION.md:187–194` registers the tuple
explicitly and says why: the registered closure is NONE, `laplacianFoam` solves
for `T` alone, and the document states in terms that the tuple is **"not copied
from T1b's thermal-family tuple `T U p_rgh alphat nut k omega`"** because
requiring `omega` here would make completion impossible. The thermal-family
default was **not** used in this audit, and neither was T20's tuple. The
completion row itself is `T18_PREREGISTRATION.md:172` — *"`mark_done_t18.py`,
rule 4 in full including the age guard"*.

Every clause below was re-derived **from the raw artifacts** — `log.solve`,
`system/controlDict`, the time directories, and filesystem mtimes — by a reader
written for this audit. The `DONE.*` markers were **not** consulted as evidence
for any clause; they are reported only as a separate row.

| clause | `T18_CU_c` | `T18_CU_m` | `T18_CU_f` | `T18_CU_f_CT` |
|---|---|---|---|---|
| 1. `rc = 0` | 0 — HOLDS | 0 — HOLDS | 0 — HOLDS | 0 — HOLDS |
| 2. an `End` line | line 100042 of 100043 — HOLDS | line 100042 of 100043 — HOLDS | line 100042 of 100043 — HOLDS | line 200042 of 200043 — HOLDS |
| 3. last time == `endTime` | 2.0 == 2.0 — HOLDS | 2.0 == 2.0 — HOLDS | 2.0 == 2.0 — HOLDS | 2.0 == 2.0 — HOLDS |
| 4. registered tuple `('T',)` present at `endTime` | `T` present — HOLDS | HOLDS | HOLDS | HOLDS |
| 5. `ExecutionTime` count == `endTime`/`deltaT` | 20000 == 2/1e-4 — HOLDS | 20000 — HOLDS | 20000 — HOLDS | 40000 == 2/5e-5 — HOLDS |
| 6. **AGE GUARD**: field at `endTime` newer than that case's own `0/T` | **+31.544 s** — HOLDS | **+328.577 s** — HOLDS | **+2724.947 s** — HOLDS | **+4444.602 s** — HOLDS |
| (`DONE.<case>` marker, reported, not used as evidence) | `done` | `done` | `done` | `done` |

**THE AGE GUARD WAS NOT SKIPPED, AND IT IS THE STRONGEST CLAUSE HERE.** Per
case, `0/T` mtime → `2/T` mtime:

| case | `0/T` (UTC) | `2/T` (UTC) | margin | `STATUS.wall_s` |
|---|---|---|---:|---:|
| `T18_CU_c` | 2026-08-28T16:29:56.801548 | 2026-08-28T16:30:28.345735 | +31.544 s | 32 |
| `T18_CU_m` | 2026-08-28T17:35:12.943108 | 2026-08-28T17:40:41.520092 | +328.577 s | 329 |
| `T18_CU_f` | 2026-08-30T23:57:36.477704 | 2026-08-31T00:43:01.424633 | +2724.947 s | 2725 |
| `T18_CU_f_CT` | 2026-08-31T00:06:16.572006 | 2026-08-31T01:20:21.174314 | +4444.602 s | 4445 |

The guard does not merely pass — **each margin reproduces that case's
independently recorded `wall_s` to better than one second**. `0/T` is touched
last at launch, so the margin *is* the solve duration, and the launcher's
`wall_s` was written by a different mechanism (the wrapper's own clock) in a
different file. Two unrelated instruments agree on four numbers. A field
inherited from an earlier run cannot produce that coincidence.

Also observed and reported rather than absorbed: each `endTime` directory holds
`DT`, `flux`, `gradTx`, `gradTy`, `gradTz`, `uniform` beside `T`. These are
`laplacianFoam` write-time extras and are **outside** the registered tuple;
their presence is neither required nor forbidden by rule 4, and no clause above
depends on them.

**(a) FINDING: all six clauses HOLD on all four cases. Nothing here blocks.**

---

## (b) ROACHE TRIPLE GATING — CLAUDE.md rule 5, verified from the values, not the label

The artifact prints `triple_state` `"CONVERGING"` on all three rows. That label
was **not trusted**. The triples were re-analysed from `gate_t18.json`'s own
`triple` blocks by an independent implementation of `p = ln|d21/d32| / ln r` and
`GCI = Fs · |(f−m)/f| / (r^p − 1)`, with `r = 2` and `Fs = 1.25`.

| row | `c` | `m` | `f` | monotone? | `d21/d32` | `p` recomputed | `p` in artifact | Δ |
|---|---|---|---|---|---:|---:|---:|---:|
| G1 | 0.617762316345 | 0.617635439403 | 0.617603711650 | **yes**, strictly decreasing | 3.998926 | 1.999612671719 | 1.999612671719 | **0.000e+00** |
| G2 | 0.860257031950 | 0.859397830881 | 0.859183115911 | **yes**, strictly decreasing | 4.001589 | 2.000573005839 | 2.000573005839 | **0.000e+00** |
| G3 | 0.582617282125 | 0.581737283951 | 0.581519262001 | **yes**, strictly decreasing | 4.036282 | 2.013027140186 | 2.013027140186 | **0.000e+00** |

`d21` and `d32` carry the same sign on every row (`(c−m)·(m−f) > 0`), so no
triple is OSCILLATORY; `|d21| > |d32|` on every row, so none is DIVERGENT;
`d21 ≠ 0`, so none is EXACT; and every `p` is far above both imported floors —
`STAGNANT_FLOOR = 0.5` and `P_MIN = 0.05`, taken from `scripts/roache_triple.py`
lines 170 and 171 and recorded in `gate_t18.json`'s `floors` block with
`"source": "scripts/roache_triple.py (imported)"`. **No row's triple would fail
the CONVERGING gate**, and the CONVERGING label is earned by the values.

**Observed orders are sane, and sane in a specific sense**: the ratio `d21/d32`
is 3.999 / 4.002 / 4.036 against the theoretical 4.000 for a second-order
scheme on `r = 2`. The registered scheme set is `Euler` in time with
`Gauss linear corrected` in space (`T18_PREREGISTRATION.md:96`), and the
pre-registration's own prediction **P2** (`:233`) required all three `p` in
**[1.7, 2.3]** — measured 1.9996, 2.0006, 2.0130, all inside. G3 is the outlier
at 2.013 and that is the row the grade-output note flagged in advance as
extrapolated at the boundary; the deviation from 2 is 0.65 %, well inside P2.

| row | GCI recomputed | GCI in artifact | Δ | `Fs` backed out of the artifact's own `gci_pct` |
|---|---:|---:|---:|---:|
| G1 | 0.0021412809 % | 0.0021412809 % | 0.000e+00 | **1.2500000000** |
| G2 | 0.0104072353 % | 0.0104072353 % | 1.7e-18 | **1.2500000000** |
| G3 | 0.0154349049 % | 0.0154349049 % | 1.7e-18 | **1.2500000000** |

`Fs = 1.25` is confirmed **three independent ways**: `factor_of_safety: 1.25` in
the artifact; `FS = 1.25` at `scripts/roache_triple.py:168`, which
`analyse_t18.py:44` imports and does not redefine; and — the strongest form —
**inverting the artifact's own published `gci_pct` for `Fs` returns 1.2500000000
on each of the three rows.** Monotonicity holds everywhere, so quoting a GCI is
legitimate on all three rows.

The `richardson_REPORTED_ONLY` values reproduce to 0.000e+00 as well, and are
noted only to confirm they are what `T18_PREREGISTRATION.md:158–162` says they
are — display-only, with no verdict a function of them.

**PLANTED CONTROL ON THIS AUDIT'S OWN TRIPLE READER (rule 3).** A zero from a
reader not shown able to see a non-zero is not evidence, and "no row fails" is a
zero. The same reader was driven on two deliberately broken triples built from
G1: pushing `m` below `f` returns `monotone = False`; making `|d32| > |d21|`
returns `p = −2.3243`. The unperturbed G1 control returns `monotone = True`,
`p = 1.9996`. **The reader that found no failing triple is demonstrably able to
find one.**

**(b) FINDING: all three triples are independently CONVERGING-compatible; every
recomputed order and GCI matches the artifact to the last printed digit; `Fs` is
1.25 by inversion. Nothing here blocks.**

---

## (c) THE BANDS — resolved by line number in the frozen blob, not by matching the artifact

This is the failure mode that matters: a band that agrees with the artifact but
not with the frozen document. It was checked in that direction — **document
first, artifact second.**

The band chain has two frozen links, both committed in `add2c788`:

1. `docs/campaigns/T-family/T18_PREREGISTRATION.md` **lines 118, 119, 120** —
   the §3 graded-rows table, giving relative half-widths **±5.0e-05 (G1)**,
   **±2.5e-04 (G2)**, **±3.0e-04 (G3)** against references 0.6175896496,
   0.8591137894, 0.5814449853.
2. `verification/runs/T-family/T18_runs/T18_registered.json` **lines 99, 106,
   113** — `band_rel` `5e-05`, `0.00025`, `0.0003`, the values the comparator
   actually reads (`analyse_t18.py:323–324`), against references at lines 98,
   105, 112.

The two frozen links **agree with each other**, and both are inside the freeze
commit.

The comparator does not take the reference from the registered JSON. It derives
it from `exact_t18.py` at full precision and **refuses** (`analyse_t18.py:320`)
if the derived value differs from the registered one by more than 1e-9. Measured
gaps: **1.423e-11 (G1), 2.489e-11 (G2), 5.034e-12 (G3)** — all roughly three
orders inside the refusal threshold, and explained entirely by the registered
values being the derived ones rounded to 10 decimal places.

Rebuilding each band from **the frozen document's relative half-width × the
artifact's full-precision reference**:

| row | band rebuilt from the frozen prereg | band in `gate_t18.json` | Δlo | Δhi | `value_fine` | inside rebuilt band? | half-band consumed |
|---|---|---|---:|---:|---|---|---:|
| G1 | [0.6175587701033, 0.6176205290683] | [0.6175587701033, 0.6176205290683] | 0.000e+00 | 0.000e+00 | 0.6176037116500 | **yes** | 0.4554 |
| G2 | [0.8588990109775, 0.8593285678722] | [0.8588990109775, 0.8593285678722] | 0.000e+00 | 0.000e+00 | 0.8591831159110 | **yes** | 0.3228 |
| G3 | [0.5812705518094, 0.5816194188006] | [0.5812705518094, 0.5816194188006] | 0.000e+00 | 0.000e+00 | 0.5815192620009 | **yes** | 0.4258 |

Relative deviations recomputed as `(value_fine − reference)/reference` reproduce
the artifact's `rel_deviation` exactly: **+2.276927e-05 (G1), +8.069535e-05
(G2), +1.277450e-04 (G3)**. The pre-registration predicted **+2.06e-05,
~+1.2e-04, ~+1.45e-04** at `:118–120` and `:231` — every measured deviation has
the predicted sign and the predicted order of magnitude, and each is at or
inside the prediction. No band is more than 46 % consumed.

**PLANTED CONTROL ON THIS AUDIT'S OWN BAND READER (rule 3).** "The bands agree"
is a zero. Mutating the registered `band_rel` by **0.1 %** and re-deriving moves
the endpoint by 3.088e-08 (G1), 2.148e-07 (G2), 1.744e-07 (G3), and the reader
reports a mismatch on all three. **The reader that found no band discrepancy can
see one a thousand times smaller than the band itself.**

**(c) FINDING: every band in the artifact is the band registered in the frozen
pre-registration, endpoint for endpoint at 0.000e+00, and every `value_fine`
lies inside it. The prereg has not moved since `add2c788`. Nothing here blocks.**

---

## (d) THE PLANTED-ZERO CONTROL — CLAUDE.md rule 3, per reader

**The dispatch asked whether a control exists for every reader or only for G1.
Measured answer: ALL THREE READERS HAVE ONE. The concern is not borne out.**
`gate_t18.json`'s `planted_zero_controls` block carries G1, G2 **and** G3, each
with `"status": "PASS"` (quoted from the artifact), and the grade output prints
three control lines, not one.

| reader | cells planted | plant | recovered | gain | negative arm | demonstrated detection floor |
|---|---:|---:|---:|---:|---:|---:|
| G1 (`mean_of`, averaging) | 512 000 | 1.234e-03 | 0.0012339999999999574 | **1.000** | **0.0** exactly | **1e-07** |
| G2 (`theta_at(0,0,0)`, point) | 1 | 1.234e-03 | 0.004164749999999828 | **3.375** | **0.0** exactly | **1e-07** |
| G3 (`theta_at(1,0,0)`, point) | 1 | 1.234e-03 | 0.004164749999999939 | **3.375** | **0.0** exactly | **1e-07** |

**No reader is without a control, so no reader is unshown.** Both arms are
present on each: the negative arm requires **exactly 0.0** on identical bytes
(`analyse_t18.py:186` refuses a NOISY reader) and returned exactly 0.0 on all
three; the positive arm walks a descending ladder 1 → 1e-07 and refuses if no
magnitude is visible (`:208`) or if the registered plant moves the read by less
than 0.1 × plant (`:210`). Every ladder in the artifact is visible at every rung
down to 1e-07, four orders below the plant.

**The G2/G3 gain of 3.375 is not an anomaly — it is a structural confirmation
that the point readers are what the pre-registration says they are.** 3.375 =
1.5³ exactly. `theta_at` (`analyse_t18.py:123`) is separable **linear
extrapolation**, weights 1.5 on the nearest cell centre and −0.5 on the next
(summing to 1) in each of three directions; a plant in the single nearest cell
is therefore amplified by 1.5 per direction, 1.5³ = 3.375 across the product.
The measured ladder shows exactly that: plant 1.0 → 3.375, plant 0.1 → 0.3375,
and so on down. A control that read back the plant unchanged on a point reader
would in fact have been the suspicious result. This independently corroborates
the extrapolation property that the grade-output companion note disclosed in
advance, and it is why G1's gain is 1.000 while G2/G3's is 3.375.

Rule 3's containment requirements are met in the code rather than by assertion:
the control copies the case to `mkdtemp` and **refuses if the copy resolves
inside the case tree** (`:179`), restores the original bytes after every ladder
rung, and never writes into the case. §E4 below measures, on the live tree, that
it did not.

**(d) FINDING: three readers, three controls, two arms each, detection floor
1e-07 demonstrated on all three, negative arm exactly zero on all three. Nothing
here blocks.**

---

## (e) THE INSTRUMENT'S OWN STATE — the dead control arm at `analyse_t18.py:509`

The supervisor's reading offered for test: *the inverted arm does not bear on
(a)–(d), because it tests a refusal precondition and not any graded quantity.*
**That reading is confirmed, by four measurements rather than by adoption — and
it needs one qualification the reading did not state.**

**E1 — the selftest was run, not relayed.** `python3 analyse_t18.py --selftest`
executed this session: **rc = 1**, wall **46.60 s** at 1 rank = **0.777
core-min**, and **16 units `[ok ]`, 1 unit `[FAIL]`**. The failing unit is the
sixteenth printed line, `"live tree, no DONE markers -> exit 2 REFUSE"` — unit
(v). The 16/1 figure is therefore this lane's own measurement.

**E2 — what unit (v) can touch, from source.** Unit (v) is the call at
`analyse_t18.py:509`: `grade(HERE, os.path.join(tempfile.gettempdir(),
"t18_never.json"), reg)`. Two facts bound it completely. (i) `grade()`'s **only**
JSON write is `:354`, `json.dump(out, open(json_out, "w"), indent=2)`, to the
`json_out` parameter — so unit (v) can write only into `tempfile.gettempdir()`,
never `gate_t18.json`. (ii) The single assertion the unit makes is that
`SystemExit(EXIT_REFUSE)` is raised by the DONE-marker guard at `:266–268`.
**It asserts nothing about a value, an order, a GCI, a band or a control.**

**E3 — clause by clause, does the inversion reach (a)–(d)?** Every other unit
that touches a graded quantity routes through `run_forged`, which grades a
`mkdtemp` forgery, and every one of those is in the 16 that passed:

| audit clause | which unit covers it | in the 16 that passed? |
|---|---|---|
| (a) completion | not covered by the comparator's selftest at all — completion is `mark_done_t18.py`'s instrument (10 forged clauses incl. the age guard, `T18_PREREGISTRATION.md:214`), and is re-derived from raw artifacts in §(a) above | n/a |
| (b) rule-5 gating | the nine-case ladder at `:437` — healthy p=2, p=0.51, p=0.49 STAGNANT, p=0.01 DEGENERATE, oscillatory, divergent, exact, outside-band, gate (1) — plus `run_forged(resid=1e-8)` and `run_forged(asym=1e-6)` | **yes, all** |
| (c) bands | `run_forged(err=3.0)` at `:483`, which drives G1 outside its band and requires the string `"GATE FAIL"` | **yes** |
| (d) planted-zero | the blind-reader mutant at `:503`, which requires the control to REFUSE a reader that ignores the plant; plus the value control at `:466`, which requires all three controls `"PASS"` | **yes** |

**No clause of (a)–(d) depends on unit (v).** The supervisor's reading holds.

**THE QUALIFICATION, stated because an honest gap is worth more than a clean
line.** Unit (v) is the **only** test of the DONE-marker guard at `:266–268`.
Its inversion means that limb is now **uncovered**: if the four `DONE.*` markers
were forged or stale, the comparator's own refusal would no longer be under
test. That gap is real, and it is **closed for this grading run specifically**
by §(a) of this audit, which re-derived all six completion clauses from
`log.solve`, `controlDict`, the time directories and filesystem mtimes **without
consulting the DONE markers at all**. The fact the guard exists to protect is
established here by direct measurement rather than by the guard. It remains a
coverage gap for any *future* run of this comparator, and repairing it belongs
to a successor registration — `T18_PREREGISTRATION.md` is frozen and rule 2 bars
editing it. The arm is inverted for a structural reason with no clean state:
completing the marker set is a precondition of grading, and it is exactly what
removes the condition unit (v) asserts on.

**E4 — the live tree was fenced across the selftest, and the numbers reproduced
a third time.** Before running the selftest, all 148 files under the four case
trees were snapshotted by mtime, size and path; after the run, the snapshot was
retaken and **diffed: zero changed lines.** The selftest's live-tree arm wrote
nothing into any case. *Planted control on that fence reader (rule 3):* a single
mtime in a copy of the snapshot was altered and the same diff reports a
difference — **the reader that saw no change can see one.** `gate_t18.json`'s
sha256 is unchanged across the run. And the side-effect file unit (v) wrote this
session, `/tmp/t18_never.json`, is 5186 bytes with sha256
`335bbec520a20ff4…` — **`cmp` against `gate_t18.json` returns 0.** That is the
**third** independent execution of the frozen comparator on this tree
(15:06:21Z, 15:11:44Z, and this session's 22:50Z), and all three produced
byte-identical output. The instrument is deterministic on this tree to the last
bit, including through the arm that fails.

**(e) FINDING: the supervisor's reading is confirmed by source and by
measurement — the inverted arm bears on none of (a)–(d). One qualification: it
leaves the comparator's completion-refusal limb uncovered for future runs, which
§(a) closes for this run by independent measurement and which a successor
registration must repair.**

---

## Cost — CLAUDE.md rule 12, actual against pre-registered

Recorded here because rule 12 requires the comparison at process completion and
the numbers were in hand. `T18_PREREGISTRATION.md:270–276` registers POINT and
cap per case; actuals are `core_min` from each `STATUS.<case>`.

| case | actual core-min | POINT core-min | ratio | cap core-min | under cap? | `capped` |
|---|---:|---:|---:|---:|---|---|
| `T18_CU_c` | 0.533 | 0.437 | 1.220 | 3 | yes | `no` |
| `T18_CU_m` | 5.483 | 3.499 | 1.567 | 20 | yes | `no` |
| `T18_CU_f` | 45.417 | 27.989 | 1.623 | 120 | yes | `no` |
| `T18_CU_f_CT` | 74.083 | 55.977 | 1.323 | 240 | yes | `no` |
| **total** | **125.516** | **87.902** | **1.428** | **383** | yes | |

**Attribution: misprediction, not contention and not waste.** No case is
`capped`, no `wall_s` is over 3600 except `T18_CU_f_CT` at 4445 s, which is a
registered 40 000-step run and not a stall. The overall 1.428× is *inside* the
direction and well inside the magnitude the pre-registration predicted for
itself at `:259–268`: the rate was **borrowed** from T14 across a 2-D → 3-D
dimension change and a 2 500 → 512 000 cell jump, and the document named an
expected one-sided **under-prediction of up to about 3×**. The realised miss is
1.43×, so the named risk materialised at under half its predicted size. Derived
cost at $0.0513/core-h: actual **$0.1073**, predicted **$0.0752** — **derived,
not measured; reported-by-owner** (`COMPUTE_BUDGET_CHARTER` §5).

**This audit does not append the calibration row.** A draft already exists at
`verification/runs/T-family/T18_runs/COST_CALIBRATION_ROW_C224_DRAFT_20260831T151113Z.txt`
and it carries a live rule-11 warning: the `C-` tail moved from 223 to 224
inside a single task while it was being written, so its proposed `C-225` must be
re-derived in the same shell invocation as the append. The append is the
supervisor's.

**One spend disclosed rather than absorbed**: this audit's own selftest run cost
**0.777 core-min** (46.60 s × 1 rank), which is an instrument check, not a
solve, and carries no pre-registered cap of its own. It is named here rather
than folded into any rung figure. Derived: $0.0007.

---

## What this audit did NOT do, and what it could not verify

- **It declares no verdict.** The words PASS / GATE REACHED / GATE FAIL / NOT A
  RESULT appear above only as quoted artifact strings. `T18_RESULTS.md` does not
  exist and this audit did not create it.
- **The rung's ceiling is not adjudicated here.** `gate_t18.json` and
  `T18_PREREGISTRATION.md:29–32` both record a ceiling; whether it applies, and
  what the rung is worth, is the supervisor's ruling.
- **The pre-registration's §5 comparator diff-read is the supervisor's §3 check
  1 and is not delegable.** `T18_PREREGISTRATION.md:218–227` records it as **not
  yet done** at freeze time. This audit hashed the instruments against their
  frozen blobs — that is an identity check, **not** a diff read, and it does not
  discharge check 1.
- **`build_t18.py`'s mesh outputs were not re-derived.** The `polyMesh`
  directories are excluded from git by design (`:320–324`) and were not rebuilt;
  mesh quality rests on the committed `log.checkMesh.build` and `BUILD.txt`,
  read by neither arm of this audit.
- **The 148-file count under the four case trees differs from the 196 cited in
  commit `bc17c5f2`.** Both are this repository's own measurements taken days
  apart; the discrepancy is most likely regenerable `polyMesh` content present
  then and absent now, but that was **not** confirmed and is flagged rather than
  explained. It does not touch any clause above, all of which cite named files.
- **Nothing was sent, filed, uploaded, registered or posted. SUBMISSIONS REMAIN
  PARKED** (`CLAUDE.md` rule 7).
