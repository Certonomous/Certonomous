# T5b — RESULTS. The instrument was repaired, it fired, and it refused the ladder at the admission gate: **0 of 6 graded rows PASS, all six `NOT A RESULT`**

> **THE ROWS WERE GRADED AND THEY ALL FAILED.** `0 of 6` on this rung is **not**
> "ungraded". The frozen comparator ran to completion, read three complete converged
> levels end to end, exercised its planted-zero control, and returned a verdict on
> every one of the six graded rows. Every verdict is `NOT A RESULT`, and every one of
> them fires at the **first** clause of the registered §7 order — the `y+` gate — before
> any grid triple is reached. A reader who takes `0 of 6` for "nothing ran" has the
> record exactly backwards.

**This record TRANSCRIBES a verdict. It does not produce one.** Every figure below is
taken from the landed
`verification/runs/T-family/T5b_runs/T5B_GRADE_OUTPUT.txt` and the artifacts that file
cites. Nothing was re-run, re-graded or recomputed to write it.

**Why this record exists at all.** Until it was written, T5b's verdict lived in exactly
one place a reader would never look for it: a **cost-ledger cell** —
`docs/COST_CALIBRATION.md:291`, row `C-209` — which states a rung verdict in prose while
no results document existed. **A verdict living in the cost ledger is an asymmetry to be
closed deliberately rather than left to accrete.** This closes it. `C-209` stands
untouched; this record cites it.

---

## 1. THE VERDICT, WITH ITS NUMBERS

Source: `verification/runs/T-family/T5b_runs/T5B_GRADE_OUTPUT.txt`, lines as cited.

| row | quantity | wall | verdict | ground |
|---|---|---|---|---|
| `G1a` | face-averaged `h` | `cube_front` | **`NOT A RESULT`** | §7 clause 1, `y+` gate not MET on level `f` (`:11`) |
| `G2a` | face-averaged `h` | `cube_top` | **`NOT A RESULT`** | as above (`:12`) |
| `G3a` | face-averaged `h` | `cube_rear` | **`NOT A RESULT`** | as above (`:13`) |
| `G5a` | area-mean `T_sur` | `cube_front` | **`NOT A RESULT`** | as above (`:14`) |
| `G5b` | area-mean `T_sur` | `cube_top` | **`NOT A RESULT`** | as above (`:15`) |
| `G5c` | area-mean `T_sur` | `cube_rear` | **`NOT A RESULT`** | as above (`:16`) |

**The ground, quoted verbatim from `:11`–`:16`** — the same sentence on all six rows:

> `y+ gate not MET on level(s) f: y+ exceeds 2.0x the level target 1.00 on: cube_front=2.310 -- the ladder is not the registered ladder`

**TALLY (`:18`), verbatim:**

> `TALLY: 0 of 6 graded rows PASS. The 7 REPORTED rows (G1, G2, G3, G4, R1, R2, R3) are a ROW CLASS, not a verdict, and are EXCLUDED from this census (ruling D534, Sanaa APPROVED 2026-08-27).`

**The gate fired on ONE level and ONE wall.** Levels `c` and `m` read `y+: MET`
(`:4`, `:5`); level `f` reads `y+: NOT A RESULT` (`:6`). The single failing statistic is
`cube_front = 2.310` against the fine level's registered target `1.00` at the registered
`2.0 ×` ladder tolerance (`T5b_PREREGISTRATION.md` §5), i.e. a bound of 2.00. It is the
**ladder** clause that fires, not the sublayer clause: 2.310 is comfortably inside
`y+_max ≤ 5.0`. The ladder claim — that the three meshes are a refinement family in the
near-wall sense the rung registered — is what fails, and the registered §7 order stops
there. **§6's prediction P2 is recorded as FALSIFIED on the fine level**, and the
registration named that risk in advance (`T5b_PREREGISTRATION.md` §6, §12) rather than
discovering it afterwards.

**The seven REPORTED rows (`G1 G2 G3 G4 R1 R2 R3`) are excluded as a ROW CLASS**, under
ruling D534 (Sanaa APPROVED 2026-08-27). They are **not counted as failures** and they
are not counted at all: the census denominator is six because six rows are graded.

---

## 2. RULE 4 — ALL SIX CONJUNCTS, ON ALL THREE CASES, FROM ARTIFACTS

**Not from `DONE.` markers.** The completion state below was re-derived by this lane
directly from each case's `log.solve`, `STATUS.<case>` and field mtimes, and it agrees
with the comparator's own reading.

**The comparator computes rule 4 itself** — `analyse_t5b.py:418-485`
(`check_completion`) reads the log, the fields and the mtimes, and it classifies
`marker_mtime` as **INFRASTRUCTURE** at `:181`. **It does not trust a marker.** That
matters and it is worth naming: a comparator that trusts a `DONE.` marker inherits
whatever the marker's author decided rule 4 meant. T5b's comparator inherits nothing —
it re-reads the six conjuncts every time it grades.

| conjunct | `T5_CUBE_c` | `T5_CUBE_m` | `T5_CUBE_f` |
|---|---|---|---|
| `rc = 0` | **0** | **0** | **0** |
| exactly one `End` line in `log.solve` | **1** | **1** | **1** |
| last `Time =` == `endTime` | **5000 == 5000** | **5000 == 5000** | **5000 == 5000** |
| `ExecutionTime` count == `endTime` | **5000** | **5000** | **5000** |
| `T U p_rgh alphat nut k omega` at `5000/air` | **all 7 present** | **all 7 present** | **all 7 present** |
| **age guard** | **PASS** | **PASS** | **PASS** |

No `log.solve` carries a `FOAM FATAL` or a signal token (the comparator's first refusal,
`:424-425`). All three `STATUS` files record `capped = 0` and `ranks = 1`.

**The age guard, re-run and passing.** `0/` was **not** archived on any level — each case
directory still holds its own `0/` beside `0.orig/` and the numeric time directories
`3000/ 4000/ 5000/` — so the datum the guard needs is the run's own, not a reconstruction.

| level | `0/air/T` mtime | `0/epoxy/T` mtime (the later datum) | earliest `5000/air` field mtime | newer? |
|---|---|---|---|---|
| `c` | 2026-08-27T22:31:09Z | 2026-08-27T22:31:10Z | 2026-08-27T22:47:57Z | **yes, by ~17 min** |
| `m` | 2026-08-28T00:07:36Z | 2026-08-28T00:07:39Z | 2026-08-28T01:35:10Z | **yes, by ~1 h 27 m** |
| `f` | 2026-08-28T02:14:24Z | 2026-08-28T02:14:30Z | 2026-08-28T08:01:58Z | **yes, by ~5 h 47 m** |

Both datums are given because `check_completion` takes the first `0/**/T` an `os.walk`
returns and the case holds two regions; **the later of the two (`0/epoxy/T`) is the
stricter datum and every `endTime` field clears it on every level.** The solid region is
recorded too: **`5000/epoxy/T` is present on all three levels and is newer than `0/T`**
(c 22:47:57Z, m 01:35:11Z, f 08:02:01Z).

---

## 3. RULE 5 — NO TRIPLE WAS COMPUTED. NO GCI AND NO OBSERVED ORDER IS QUOTED.

**The registered §7 order stops at clause 1.** A `y+` gate that is not MET returns
`NOT A RESULT` before `classify_triple` is ever reached. No grid triple was classified on
this rung, no observed order was computed, and no GCI exists to quote. This record quotes
none, and a later reader must not supply one.

**The measured refinement ratios are printed and nothing was computed with them.**
`T5B_GRADE_OUTPUT.txt:7` records

> `MEASURED refinement ratios r21 = 1.6060, r32 = 1.5929 (NEVER the r = 2.0 default: that is wrong by 46 % in log r on this ladder)`

They are derived from the levels' own `log.checkMesh` cell counts (52,684 / 212,942 /
882,024, `:4`–`:6`) and they are printed because the comparator prints its inputs. **They
are inputs that were never consumed.** A printed ratio is not a classification, and the
distinction is stated here so that nobody later mistakes one for the other.

---

## 4. RULE 3 — THE PLANTED-ZERO CONTROL WAS EXERCISED AND PASSED

`T5B_GRADE_OUTPUT.txt:8`, verbatim:

> `planted-zero control: both plants seen: constant offset 0.001234 through the MEAN reader and single-cell spike 987.6 through the RANGE reader`

The control runs on the **fine** level and on a real graded patch (`cube_front`), and it
runs **before any value is read** — `analyse_t5b.py:781-788`; a failure of either arm is a
**refusal, exit 2**, at `:786`, not a degraded run. The two constants are frozen at
`:163-164` (`PLANT_OFFSET = 1.234e-03`, `PLANT_SPIKE = 9.876e+02`). The plants are written
into a **temp copy** of the real `endTime/air/T` (`plant_and_read_back`, `:545-590`:
`tempfile.mkdtemp`, `shutil.copy2`, `shutil.rmtree` in a `finally`) and read back
**through the production readers** — `face_mean_T_C` for the mean arm, `read_patch_field`
for the range arm. **The run tree is never written.**

**Why there are two shapes and not one, and this is the substance rather than the
ceremony: a constant offset cannot test a range reader.** Add the same number to every
face value and the maximum moves by exactly that number — a max reader that is entirely
broken and a max reader that is perfect are indistinguishable under a uniform shift. The
offset arm proves the **area-mean** reader (`:571-573`: the mean must move by
`PLANT_OFFSET` to within 10 %); the single-cell spike proves the **range/max** reader
(`:580-582`: the maximum must move by at least 0.9 × `PLANT_SPIKE`), and its own comment
says so — *"exactly the shape a constant offset cannot test (L-340)."* Planting one shape
would have certified one reader and left the other's zeros unearned.

---

## 5. THE FREEZE POSITION — PREDICTION-FIRST, BY 4 h 58 m

**Registration committed `35df9762` at 2026-08-27T17:32:55Z.** The earliest artifact of
the *run* is `T5_CUBE_c/0/air/T` at **2026-08-27T22:31:09Z** — the arming of the coarse
case; `C-209` fixes the same instant from `T5_CUBE_c/log.checkMesh`. **The freeze precedes
first compute by 4 h 58 m 14 s.** (The built case *directories* predate the freeze by
design: `T5b_PREREGISTRATION.md` §13 registers all three cases as **built and unarmed**,
holding no `0/` and no numeric time directory, a condition the comparator's `--selftest`
printed at freeze time.)

**Every frozen file is byte-identical to its HEAD blob**, verified by hashing the disk
bytes rather than recalling them. Freeze-commit blob, HEAD blob and `git hash-object` of
the working file agree on all six:

| frozen file | blob (freeze == HEAD == disk) |
|---|---|
| `docs/campaigns/T-family/T5b_PREREGISTRATION.md` | `e57ce5803f8ae884bf4d390438567952b634f124` |
| `verification/runs/T-family/T5b_runs/build_t5b.py` | `af6c6ebf54f34bfefdb964bc5036ba30a0357203` |
| `verification/runs/T-family/T5b_runs/analyse_t5b.py` | `552f7472f3ded7575256f877867cb076c6aab2e3` |
| `verification/runs/T-family/T5b_runs/run_one_t5b.sh` | `8351ce08e7d6097b0935013100eeba913731a794` |
| `verification/runs/T-family/T5b_runs/T5B_CAPS.txt` | `c1da6d1743eedb6d3eb53a489ef7b49046ced7ce` |
| `verification/runs/T-family/T5_runs/T5_reference_primary.json` | `04dfd7e2e56adf1cd0924046500904af2243b747` |

**The file that graded is the file that was frozen.** The gate that refused the ladder at
`cube_front = 2.310` against 2.00 was written before the mesh was ever solved on.

---

## 6. RULE 12 — THE CALIBRATION IS ALREADY LANDED, AND NOTHING FURTHER IS OWED

The estimate-versus-actual comparison for this rung is **row `C-209` at
`docs/COST_CALIBRATION.md:291`**. It is not restated here and it is not amended here; this
section cites it and carries forward the one thing it left open.

| figure | value | basis |
|---|---|---|
| POINT | **419.2 core-min** (419.118 unrounded) | `T5b_PREREGISTRATION.md` §9, frozen |
| CAP | **838.4 core-min** | `T5B_CAPS.txt`, frozen (32.8 / 154.4 / 651.2) |
| ACTUAL | **451.833 core-min**, basis **gross** | `STATUS.T5_CUBE_{c,m,f}`: 16.783 + 87.533 + 347.517, at ranks = 1 |
| ratio actual/predicted | **1.078** | 1.0778 against the printed 419.2; 1.0781 against the unrounded 419.118 |
| cap use | **53.9 %** | 451.833 / 838.4; worst level `m` at 56.7 % |
| overrun | **none.** No level capped, killed or truncated | `capped = 0` on all three |
| waste | **0.000 core-min**, named separately | `C-209`, charter §6 sense; not folded into the ratio |

**THE OPEN QUESTION `C-209` REFERS TO THE SUPERVISOR AND TO VERIFICATION, CARRIED
FORWARD HERE AND NOT ANSWERED.** `C-202` of that ledger named an entire 194.73 core-min
spend as charter-§6 **waste** because its rung (F23) returned `NOT A RESULT`. T5b also
returned `NOT A RESULT` on every graded row — **and the two cases are not alike.** F23's
levels were **not converged**: there was nothing for a gate to read. T5b's three levels
each produced a complete, converged, comparator-read `y+` field, and the `NOT A RESULT` is
the **admission gate refusing a fully converged ladder on a statistic** — which is itself
the measurement that produced docket rows D557 and D566 and the successor rung `T5c`.
**Whether an admission-gate refusal on a fully converged ladder is charter-§6 waste is
REFERRED, and it is not answered by this record.** Zero is what `C-209` entered, with the
question named beside it rather than absorbed.

---

## 7. HOW T5b RESOLVED `y+` LAWFULLY — ITS OWN FUNCTION OBJECTS, PROVEN TO FIRE BEFORE THE FREEZE

**No T5 artifact was read, reconstructed or written by this rung.** T5's `NOT A RESULT`
stands, un-reopened (`T5b_PREREGISTRATION.md` §2, and Sanaa's standing directive of
2026-08-27T16:54Z §3 quoted there). The `y+` this rung graded on is a **new measurement
made by a new run**, not a recovery of an old one.

**The registered configuration** — `T5b_PREREGISTRATION.md` §4, `:167-174`, the one
substantive change from T5, applied to **both** function objects:

```
executeControl  timeStep;
executeInterval 1;
writeControl    timeStep;
writeInterval   1000;
```

**Its firing was proven PRE-FREEZE, by a planted-failure pair** (§3, four 20-iteration
arms on a scratch copy of the coarse case, 0.337 core-min total, on no registered case):
the **CONTROL** arm preserved T5's `writeControl writeTime` verbatim and produced
**0 `yPlus.dat` data rows**; the **FIX** arm changed one keyword and produced **12**. A
guard shown able to fail before it is believed when it passes.

**The comparator reads what the solver writes.** `read_yplus_dat` at
`analyse_t5b.py:336-337` opens `postProcessing/air/yPlus/<t0>/yPlus.dat` and its docstring
names the defect it exists to avoid — *"not a `yPlus.json` that no producer in this
repository has ever written."* **`yPlus.json` is never read by this rung.**

**MEASURED on the landed run — the instrument prediction P1 holds:**

| level | `yPlus.dat` data rows (all write times) | rows at `Time = 5000` | walls at `Time = 5000` | `yPlus` field at `5000/air` |
|---|---:|---:|---|---|
| `c` | **30** | **6** | `floor roof cube_front cube_rear cube_top cube_side_n` | **present** |
| `m` | **30** | **6** | same six | **present** |
| `f` | **30** | **6** | same six | **present** |

30 = 5 write times × 6 walls, and the six are exactly the registered `YPLUS_WALLS` with
`cube_side_s` correctly absent from the half domain. `wallHeatFlux` is present at
`5000/air` on every level — the local field D1's third consequence made necessary. **The
instrument worked. The ladder did not.**

---

## 8. T5c HAS SINCE RE-GRADED THESE SAME ARTIFACTS — THIS RECORD IS NOT THE LAST WORD

`T5c` re-graded **these three completed levels**, at **zero solver compute**, having moved
the `y+` ladder gate off the point maximum onto an area-weighted statistic. Its verdicts,
from `verification/runs/T-family/T5c_runs/T5C_GRADE_OUTPUT.txt` and
`docs/campaigns/T-family/T5c_RESULTS.md`:

| row | T5b verdict | T5c verdict |
|---|---|---|
| `G1a` | `NOT A RESULT` (`y+` clause 1) | **`NOT A RESULT`** — grid triple `OSCILLATORY`; fine value 76.9543 printed, not graded |
| `G2a` | `NOT A RESULT` (`y+` clause 1) | **`GATE FAIL`** — fine **39.4023** vs reference **55.224**, band **± 5.66404**, **GCI 4.3550 %** |
| `G3a` | `NOT A RESULT` (`y+` clause 1) | **`NOT A RESULT`** — grid triple `OSCILLATORY`; fine value 65.8707 |
| `G5a` | `NOT A RESULT` (`y+` clause 1) | **`NOT A RESULT`** — grid triple `DIVERGENT`; fine value 55.9394 |
| `G5b` | `NOT A RESULT` (`y+` clause 1) | **`NOT A RESULT`** — grid triple `DIVERGENT`; fine value 59.45 |
| `G5c` | `NOT A RESULT` (`y+` clause 1) | **`NOT A RESULT`** — grid triple `DIVERGENT`; fine value 55.6857 |

**T5c: 1 `GATE FAIL`, 5 `NOT A RESULT`, 0 of 6 graded rows PASS.** Under T5c's statistic
the `y+` gate reads **MET on all three levels**, so the rows advance to clause 2 and are
refused on their **grid triples** instead. The failure moved; it did not disappear.

**Both halves of what that means, stated plainly:**

- **T5b is NOT superseded as a MEASUREMENT.** Its three solves — 451.833 core-min of
  `chtMultiRegionSimpleFoam` on 52,684 / 212,942 / 882,024 cells — **are the artifacts
  T5c re-graded.** T5c launched no solver. Everything T5c says about this cube rests on
  the runs recorded here, and their rule-4 completion (§2) is the ground under both
  rungs' verdicts.
- **T5b's VERDICT is behind a successor's.** A reader who needs the lab's current
  standing on these six rows should read `docs/campaigns/T-family/T5c_RESULTS.md`. What is
  recorded here is what the **frozen T5b comparator** returned on the **frozen T5b gate**,
  and it is preserved exactly because a superseded verdict that quietly disappears is how
  a gate comes to look as though it were never registered.

---

## 9. WHAT THIS RECORD DOES NOT DO

- **It does not re-grade anything.** No comparator was run to write it; every graded
  number is transcribed from `T5B_GRADE_OUTPUT.txt` and the artifacts that file cites.
- **It does not reopen T5.** T5's `NOT A RESULT` stands (`T5b_PREREGISTRATION.md` §2).
- **It edits no frozen file.** `T5b_PREREGISTRATION.md`, `analyse_t5b.py`, `T5B_CAPS.txt`,
  the T5 registration and every T5 amendment are read-only to this record.
- **It amends no cost row.** `C-209` stands as filed; this record cites it and carries its
  open question forward unanswered.
- **It quotes no GCI and no observed order for T5b** (§3), because none was computed.
- **Nothing here was sent, filed, uploaded, registered, posted or commented outside this
  box** (`CLAUDE.md` rule 7).

---

**Artifacts this record cites, all on disk at the time of writing:**
`verification/runs/T-family/T5b_runs/T5B_GRADE_OUTPUT.txt`;
`verification/runs/T-family/T5b_runs/analyse_t5b.py`;
`verification/runs/T-family/T5b_runs/T5B_CAPS.txt`;
`verification/runs/T-family/T5b_runs/STATUS.T5_CUBE_{c,m,f}`;
`verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}/log.solve`;
`verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}/postProcessing/air/yPlus/0/yPlus.dat`;
`docs/campaigns/T-family/T5b_PREREGISTRATION.md`;
`docs/campaigns/T-family/T5c_RESULTS.md`;
`verification/runs/T-family/T5c_runs/T5C_GRADE_OUTPUT.txt`;
`docs/COST_CALIBRATION.md` row `C-209` at `:291`.
