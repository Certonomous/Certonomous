# ARM P1B — RESULTS. **`GATE FAIL`.** The tolerance correction WORKED; a DIFFERENT gate fails, and it is not mine to move.

**Arm registered:** `verification/campaign/CRM_WINGALONE_FLOW_PREREGISTRATION.md` **ADDENDUM 1**,
landed `851def1cedaeaac8ed020fb77cf3c175c19db091`, **check 4 discharged personally by the
cfd-supervisor before this arm ran.** Authorised by the supervisor's ruling of 2026-09-12 under its
four conditions.

---

## 1. VERDICT

> ## **P1B — `GATE FAIL`. Reported, NOT adjusted.**

**All three counts hit the registered prediction EXACTLY. One geometric assertion still fails.**
Per the supervisor's ruling, quoted before the run and honoured after it: *"If the counts come right
and the radius assertions still fail, THAT IS A FINDING ABOUT THE RADIUS BAND AND NOT A LICENCE TO
MOVE IT."* **The band is not moved.**

---

## 2. THE ORDERING EVIDENCE — STRONGER THAN PRE-REGISTRATION USUALLY GETS

**The falsifier was written before the instrument that could produce a number existed.** Three
mtimes, cited as the supervisor directed:

| artifact | mtime (UTC) |
|---|---|
| `PREDICTION_BEFORE_SWEEP.md` | **2026-09-12 02:05:36.671655956** |
| `band_sweep.py` | 2026-09-12 02:07:34.604656558 |
| `log.band_sweep_L2` | 2026-09-12 02:08:16.362006206 |

**The prediction predates the instrument by 117.9 s and the result by 159.7 s.** A prediction written
before the code that could produce the number exists cannot have been shaped by that number.

---

## 3. WHAT CHANGED, AND WHAT DID NOT

`P1B/split_patches_p1b.py` is derived from P1's frozen `P1/split_patches.py`. **The diff is one
docstring line and one constant.** `EXPECT` (11,136 / 11,136 / 14,144), `WING_R_MAX` (4.3) and
`FARFIELD_R_MIN` (80.0) are **byte-identical** — the frozen gates are untouched.

| | P1 (struck, legible) | **P1B** |
|---|---|---|
| `Y_SYMM_TOL` | 1e-9 | **1.0e-3** |
| wing | 11,908 ✗ | **11,136 MATCH** |
| farfield | 11,196 ✗ | **11,136 MATCH** |
| symmetry | 13,312 ✗ | **14,144 MATCH** |
| total | 36,416 | 36,416 |
| max wing \|r\| (gate ≤ 4.3) | 38.3271 **FAIL** | **4.9810 FAIL** |
| min farfield \|r\| (gate ≥ 80.0) | 40.9425 **FAIL** | **80.4423 PASS** |
| planted control | passed | passed (face 3808, farfield \|r\| 80.465 → wing \|r\| 1.609 → restored) |

**The tolerance correction is vindicated on its own terms:** three counts moved from wrong to exact,
`max wing |r|` improved **7.7×** (38.3271 → 4.9810), and `min farfield |r|` crossed from FAIL to
PASS. **It did not make the arm pass, and it was never registered to.**

---

## 4. 🔴 THE FINDING ABOUT THE RADIUS BAND — SUBSTANTIATED, NOT ASSERTED

`P1B/diagnose_radius.py` imports the **same** classifier object that produced the graded number, so
it cannot silently differ from a re-implementation. Output: `log.diagnose_radius_L2`.

- **3,374 of 11,136 wing faces (30.298 %) exceed \|r\| = 4.3.**
- **Every one of them lies at y ≥ 3.1724** — the outboard 16 % of the semispan, against a tip at
  **y = 3.7666681523** (§2's own measured figure).
- Their centres occupy **x 2.6077…3.2471, z 0.2310…0.3460**. The maximum is at
  **(3.2470, 3.7614, 0.3450) → \|r\| = 4.9810.**

**THE MECHANISM, AND IT IS ARITHMETIC.** `classify()` computes `r = sqrt(cx² + cy² + cz²)` —
**distance from the ORIGIN**. §2's prose registers the gate as *"within \|r\| ≤ 4.3 mesh-units **of
the body axis**"*. **Those are different quantities, and on a wing swept 30° at the leading edge they
diverge exactly where the exceedance is.** At the tip trailing edge x ≈ 3.25 and y ≈ 3.77; neither
exceeds 4.3, but `sqrt(3.25² + 3.77² + 0.35²) = 4.98` does.

**THE CONFIRMING NUMBER:** distance from the **span axis**, `sqrt(x² + z²)`, over the very same
3,374 exceeding faces has a maximum of **3.2654** — **all of them clear 4.3 comfortably when measured
the way §2's prose describes.**

**So the 4.3 threshold appears to have been derived from the spanwise extent alone (tip y = 3.7667
plus margin), which bounds a span coordinate and does NOT bound a distance from the origin for a
swept planform.**

🔴 **THIS IS RECORDED AS A FINDING AND THE GATE IS NOT TOUCHED.** The threshold and the classifier
are frozen; ADDENDUM 1 cannot alter them and does not. **Whether §2's prose or `classify()`'s
arithmetic is the registered intent is the supervisor's to rule on, not this lane's** — and the two
disagreeing is itself the finding. **A number that passes under one reading of a gate and fails under
the other is not a number to adjudicate from the run that produced it.**

---

## 5. COMPLETION AND COST (rule 12)

`P1B_RC.txt`: **`P1B_RC=1`** (the instrument's registered `GATE FAIL` exit), **`WALL_S=22`**, 1 rank.

| | figure |
|---|---|
| **predicted** | **5 core-min** — §8's *"P1 patch split + verification"*, 1 rank, ~300 wall s. Frozen at `51e5cd32`, before this arm existed. |
| **actual, graded arm** | **0.3667 core-min MEASURED** (22 wall s × 1 rank ÷ 60), timed around the invocation. |
| **ratio** | **0.073×** — **13.6× FASTER than estimated.** |

**Supporting drives, named rather than folded in.** Bounded from mtime deltas, and the inequality is
deliberate: band sweep **≤ 41.76 wall s**, radius diagnostic **≤ 21.08 wall s**. **Two drives are NOT
TIMED and are therefore excluded rather than estimated:** the first, REFUSED band-sweep run, and the
`split_patches_p1b.py --selftest`. Whole chain that produced committed evidence: **≤ 1.414 core-min**.
**No invocation is within two orders of magnitude of the 3,600 wall-s stall rule** — the longest is
22 wall s, so gross and cleaned coincide.

**DERIVED, NOT MEASURED: $0.00031** at $0.0513/core-h, c7a.4xlarge, reported-by-owner — **the box
cannot read its own billing** (`COMPUTE_BUDGET_CHARTER` §5).

**GAP ATTRIBUTION — MISPREDICTION OF SCOPE, NOT CONTENTION.** §8 priced a *patch split*; the
instrument does not split — it **classifies and grades, and writes no boundary file**. **Contention
argues the other way and is therefore excluded rather than assumed:** the box stood at load average
**59.89 on 16 cores** during the run, so a quiet box would be faster still, not slower. **WASTE:
0.000 core-min.** The refused band-sweep run is **not waste** — it produced the plant defect and its
repair, which is evidence, and it is named separately per `COMPUTE_BUDGET_CHARTER` §6 rather than
absorbed into the ratio.

---

## 6. WHAT THIS ARM DOES NOT DO

- **It does not make P1 pass.** P1's `GATE FAIL` is struck-but-legible in ADDENDUM 1 §A1.1 and is not
  rehabilitated.
- **It does not authorise the solve.** §7's gates are untouched and are reached in registered order.
- **It does not move `WING_R_MAX`, `FARFIELD_R_MIN` or §2's counts.**
- **It makes no flow claim and no grid-convergence claim of any kind.**

---

*Arm P1B run and graded 2026-09-12 by a cfd `lab-lane`, after check 4 on `851def1c` was discharged by
the cfd-supervisor. Submissions parked. No agent's message is Sanaa's consent.*
