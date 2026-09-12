# D8G R2 (`L1-P`) — GRADING RECORD. **NOT A RESULT** — at a NEW and DEEPER gate. **THE RECORDING PATH WORKS.**

Graded 2026-09-12 by a `lab-lane` of the dafoam team with `d8g_grade.py` **UNCHANGED**,
md5 `12688063e20cbb6fa79cf08d0996d4e1`, against `PREREGISTRATION.md` ADDENDUM 7 + 8 + 9.
Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D8G-R2-a6-grid-triple`.
**SUBMISSIONS PARKED** (rule 7).

---

## 1. THE HEADLINE: **THE LEDGER ROW PARSES.**

This is what the remaining nine arms stood on, and it is now demonstrated on a **real run**
rather than on a planted control:

| check | result |
|---|---|
| row through the frozen `LEDGER_RE` | **PARSES** |
| `ARM` in `ARMS_REQUIRED` | **True** (`L1-P`) |
| `DIGEST == IMG_DIGEST["PATCHED"]` | **True** |
| `cpuset == CPUSET_REGISTERED` | **True** (`0,1,12,15`) |

**ADDENDUM 9's four defects are closed.** The comparator read the row, accepted the arm,
matched the toolchain digest and the placement, and **advanced past the ledger to gate on
the run itself** — which is exactly what it could not do for R1.

## 2. VERDICT

**`NOT A RESULT`** — and at a **different, deeper** gate than R1's:

```
REFUSAL: {"REFUSE": "G1-RUN", "detail": {"arm": "L1-P",
  "endTime_registered": 1000.0, "last_time": 2000.0,
  "note": "rule 4: last time == endTime.  A primal that stopped short is not done,
           however plateaued its tail looks"}} -> NOT A RESULT
```

## 3. **DEFECT 5 — KNOB 5 CONTRADICTS THE FROZEN COMPARATOR. NO LAUNCHER CAN FIX THIS ONE.**

`d8g_grade.py:290`: **`ENDTIME_REGISTERED = 1000.0`** — *"controlDict endTime, section 4.5"*,
frozen. It gates `last_time == ENDTIME_REGISTERED` (`:639`) **and** derives the expected
printed-step count from it (`:624`).

**The R3 repair package's knob 5 sets `endTime 2000`**, carried in the arm's `d8g_of.py`
as `REGISTERED_CONTROLDICT = {"endTime": 2000.0, ...}`.

**ADDENDUM 7 changed `endTime` while asserting the comparator was NOT TOUCHED.** Both
statements are true as written; together they make **the R3 package as registered
ungradeable by D8G's own frozen comparator, by construction**.

This is the same disease as ADDENDUM 9's defects 1–4 — a registration changing something
the untouched instrument gates on — but it is **categorically worse in one respect and
better in another**:

* **Worse:** defects 1–4 lived in the *recording path* and a launcher fixed them.
  Defect 5 lives in the **science configuration**. No launcher change can reach it.
* **Better:** it is **escapable without touching a single frozen threshold** — see §4.

## 4. **THE ESCAPE, AND THIS RUN PAID FOR THE EVIDENCE: KNOB 5 IS UNNECESSARY.**

Read at `Time = 1000` — the value `ENDTIME_REGISTERED` gates on — from this run's own log:

| quantity | at `Time = 1000` | at `Time = 2000` | what the extra 1000 iterations bought |
|---|---|---|---|
| `nuTilda initRes` | **8.283378662708179e-05** | 7.873598471886472e-05 | **4.95 %** further reduction |
| `nuTilda` / 1.0e-04 floor | **0.828× — ALREADY CLEARED** | 0.787× | — |
| `CD` | 0.04380560654313817 | 0.04380537021659878 | Δ = −2.363e-07 (**5.39e-06 relative**) |
| `CL` | 0.3400061037658128 | 0.3400058472405582 | Δ = −2.565e-07 (**7.54e-07 relative**) |

**The fix had already worked by iteration 1000.** `nuTilda` was below its floor, and `CD`
and `CL` agree between 1000 and 2000 **to five significant figures**.

**So knob 5 can be withdrawn as UNNECESSARY — on this run's own evidence — rather than
conceded as a compromise.** A re-run at `endTime 1000`:

* is gradeable by the frozen comparator, **touching no threshold** (rule 2 intact);
* **does not weaken the fix** — the tight inner-solve rule is knobs 7–8, not knob 5;
* costs roughly **half** the compute.

**This is the supervisor's call, not this lane's**, and it is registered here rather than
acted on. The recommendation is (a) withdraw knob 5 in a dated addendum, citing the table
above, and re-run `L1-P` at `endTime 1000`.

## 5. Physics — a true zero on both strings

| quantity | value |
|---|---|
| `did not satisfy the prescribed tolerance` | **0** |
| raw grep `Primal solution failed` | **0** |
| last `nuTilda initRes` | **7.873598471886472e-05** = **0.787×** the 1.0e-04 floor |
| `nuTilda` `finalRes` / `nIters` | 7.031861967269513e-08 / **3** |
| **reduction within the outer step** | **1119.7×** |
| last `p initRes` | 7.868950163491053e-09 |
| `CD` / `CL` | **0.04380537021659878** / **0.34000584724055816** |
| `yPlus` min/max/mean | 48.34 / 563.26 / 141.70 |

**R2 reproduces R1's discriminator exactly — 1119.7× on an independent run.** That is the
fourth point in the reduction-factor table (ADDENDUM 10 §10.2) arriving **on schedule
rather than by hope**, and it is the strongest single piece of evidence the mechanism is
real: the same configuration, launched independently on different cores, lands on the same
reduction factor to four significant figures.

## 6. Cost — rule 12, and the "grade-neutral" departure was **also a 2.23× performance cost**

| basis | figure | ratio to the 35 core-min estimate |
|---|---|---|
| predicted (`PREREGISTRATION.md:88`) | 35.000 core-min | 1.000× |
| actual, **cleaned** (`ExecutionTime 923.98 s × 4`) | **61.599 core-min** | **1.760×** |
| actual, **gross** (ledger, `wall_s 1480 × 4`) | **98.667 core-min** | **2.819×** |

* **MISPREDICTION 1.760×** — the unpriced tighter inner solve (ADDENDUM 10; 13 pressure
  sub-iterations per outer step against the loose rule's 1).
* **CONTENTION 1.602×** (`wall_s / ExecutionTime = 1480 / 923.98`).
* 1.760 × 1.602 = **2.819**, against the measured gross **2.819** — the split closes exactly.
* **WASTE: separately named as ZERO** — no stall, no re-run of this arm, no discarded output.

**THE NEW CALIBRATION FINDING: `--cpuset-cpus=0,1,12,15` ran the SAME work 2.23× faster
than R1's `--cpus=4`** — `wall_s` 1480 against 3293, contention 1.602× against 2.378×.
`LAUNCH_D8G_R1.sh`'s "departure 2" was defended in its own header as harmless; it was
**not grade-neutral (G12) and not cost-neutral either**. A share limit on a loaded box
lets the kernel migrate ranks across contended cores; a pin to free cores does not.

**CAP:** `CAPS["L1-P"] = 46.977` core-min, `CAP_IS_A_STOP = False` (§6.4). Gross 98.667 is
**2.10×** it — **recorded and reported, not a stop** (selftest unit U39). Down from R1's
4.67×.

**$0.084 at $0.0513/core-h on the gross basis — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5).

## 7. What I could not verify

* **Still one arm of ten.** Even with a gradeable row, `g_completion()` walks all ten
  `ARMS_REQUIRED`; this run does not and cannot produce an item verdict — registered in
  advance at ADDENDUM 9 §9.6.
* **No graded number exists for R2.** Every figure in §4 and §5 is a log or artefact
  reading. The comparator refused before reaching G2, G9, G10, G12 or G-M2, so **none of
  those gates has been exercised on real data** — including the DIGEST and cpuset limbs,
  which are shown only to *parse*, not yet to *pass*.
* **The `-S` shipped row has not run**, so nothing here is a verdict about DAFoam.
