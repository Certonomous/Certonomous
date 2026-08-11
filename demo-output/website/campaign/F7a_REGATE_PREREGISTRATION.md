# F7a re-gate — pre-registration

**Written 2026-08-11, frozen before any new solver run exists.** No new mesh has
been generated, no new `interFoam` has been launched, no new field exists. This
agent held no compute authorisation and spent none.

**Governing definition:** `F7a_REGATE_SPEC.md` §2, frozen the same day. This
file does not restate the definition — it cites it (docket C3: one home per
fact). If §2 changes, this pre-registration is void and must be re-issued.

**Frame:** repo `/home/ubuntu/Certonomous`, tracked tree at `c05a03e0`;
exhibit script landed at `38d05c40`.

---

## 1. What is already known at the time of writing

Declared so this document cannot later be accused of following the answer.

Everything in `F7a_REGATE_SPEC.md` §1 and §3 was computed **before** this
pre-registration was written, from field data already tracked in the repo:

- The old front definition's readings span up to **78 percentage points** and
  change sign; on the original gate case, reading A gives **+13.4%** (reproducing
  the published +13.6%) and reading B gives **−16.1%**.
- The spread across readings **collapses with vertical resolution** — 78.2 pts at
  a/8, 1.7 at a/32, 0.4 at a/64.
- Under §2, `res32y128_base` grades **FAIL**, max deviation **+11.03%** at
  T = 7.72, metric uncertainty ≤ 0.68% of Z.
- `res16_papermodel` — comparator physics, comparator mesh, comparator domain —
  sits **+23.3%** ahead of the comparator's own published curve.

**Therefore the gate verdict is not what any new compute would settle.** It is
already taken, and it is FAIL. This pre-registration governs the *diagnostic*
runs that remain genuinely open, and its predictions are about those.

**What has NOT been computed at the time of writing:** any run at dy finer than
a/256; any run with a transition-capable turbulence model; any run at
dx = a/64 with dy = a/256; any reading of the comparator paper's front-extraction
method beyond what R1 recorded.

---

## 2. Predictions, fixed now

Each is falsifiable and each names what would falsify it.

| # | Prediction | Falsified by |
|---|---|---|
| P1 | A dy = a/512 rung at dx = a/32 lands in **+7.0% to +9.5%** mean over the six graded stations — i.e. it does **not** reach the 5% tolerance. | A mean outside that band. A mean ≤ 5% falsifies it *and* passes the gate. |
| P2 | The y-ladder increments (a/64→a/128→a/256→a/512) remain **non-geometric**, so no Richardson value becomes quotable. | Three successive increments in constant ratio to within 20%. |
| P3 | The `res32y256_base` early-time outlier at T = 3.90 (+18.1%) is an **aspect-ratio artifact** (dx/dy = 16). A dx = a/64, dy = a/256 run (aspect 4) removes it, landing that station within 3 points of its neighbours. | The outlier persisting at aspect 4. |
| P4 | A transition-capable model on the film **worsens or leaves unchanged** the front deviation, because the film is 2–7 cells thick and the model is outside its calibration. | A deviation improvement > 3 points. |
| P5 | **The comparison-basis item dominates all of the above.** Any run in this list changes the deviation by less than the **23.3%** code-to-code offset already measured in spec §3.1. | Any single run closing more than 23.3 points. |

**P5 is the prediction this pre-registration most wants tested, and it is the
one that argues against spending the compute at all.**

---

## 3. Thresholds and decision rules, fixed now

- **Gate verdict** is taken **only** by `F7a_REGATE_SPEC.md` §2. Three-valued:
  PASS / FAIL / UNGRADEABLE. PASS iff max|d_k| ≤ 5% over the six frozen
  stations at h\* = 0.02a.
- **Verdict floor:** no verdict on any mesh with dy > a/128 (§2.5). Diagnostic
  rungs coarser than that are labelled *diagnostic*, never *gate*.
- **Metric uncertainty:** threshold spread > 1.0% of Z at any graded station ⇒
  UNGRADEABLE for the whole run, not FAIL.
- **Monotonicity guard** (§2.2) is mandatory on every extraction, including
  re-grades of existing cases. Any number derived from `grade_f7a.py`'s
  unrestricted mean line is void until re-derived.
- **No post-hoc selection.** Threshold set, station set, axis and mesh are
  frozen in §2. Changing any is a new spec version that re-grades every case.

---

## 4. Caps

- **Hard cap on this line: 400 core-min**, and no single run above 200 core-min
  without a separate authorisation naming that run.
- All runs foreground or `launch_solve.sh`-registered, collector armed, nothing
  left running. `MemAvailable` checked before any run above 150,000 cells.
- Rank count ≤ 8, checked against `uptime` before each launch.
- **Stop rule:** if two consecutive runs move the six-station mean by less than
  1.5 points, the line stops and reports, rather than buying a third.

---

## 5. The compute request — priced, and recommended against in its expensive half

Prices are extrapolated from the R1 campaign's own `log.interFoam` `ClockTime`
× rank count, read from the tracked logs at `c05a03e0`:

| case | cells | ranks | ClockTime | core-min |
|---|---|---|---|---|
| `res16_base` | 4,800 | 4 | 7 s | 0.5 |
| `res32_base` | 19,200 | 6 | 44 s | 4.4 |
| `res32y64_base` | 38,400 | 6 | 78 s | 7.8 |
| `res32y128_base` | 76,800 | 6 | 239 s | 23.9 |
| `res64_base` | 76,800 | 8 | 330 s | 44.0 |
| `res64y128_base` | 153,600 | 8 | 645 s | 86.0 |
| `res32y256_base` | 153,600 | 6 | 1,902 s | 190.2 |

Halving dy doubles cells **and** halves the Courant-limited timestep, so cost
scales at least 4×. The measured a/128 → a/256 step was **8.0×**.

### The request

| # | Run | Cells | Basis | **est. core-min** | Recommendation |
|---|---|---|---|---|---|
| **R0** | *Comparator front-definition recovery* — read arXiv:2108.08769 and its references for the extraction method behind the Fig. 7 simulation curve; if unstated, contact-free bound it by re-deriving their curve's implied threshold from our own field data | — | literature only | **0** | **BUY. Highest information per unit cost in the whole brief.** |
| R1a | dx = a/32, **dy = a/512** (307,200 cells) — tests P1, P2 | 307,200 | 190.2 × 4 to × 8 | **760 – 1,520** | **Do not buy now.** 2–4× the entire R1 campaign to settle the shape of a sequence, while a 23.3% offset sits unexplained. |
| R1b | dx = a/64, **dy = a/256** (307,200 cells) — tests P3, the aspect-ratio outlier | 307,200 | 86.0 × 4 | **≈ 344** | Buy only if R0 comes back empty. Exceeds the 200 core-min single-run cap and needs its own authorisation. |
| R1c | dx = a/32, dy = a/128, transition-capable model — tests P4 | 76,800 | 23.9 × ≈ 1.5 | **≈ 36** | Cheap, but R1 §6 doubts it is well-posed on a 2–7 cell film. Buy only after R0. |

**Recommended purchase: R0 only, at 0 core-min.**
**If Katie wants a solver run on this line regardless, the cheapest informative
one is R1c at ≈ 36 core-min — not the re-run of the gate, which would re-derive
a number already held.**

**Total if the whole list were bought: 1,140 – 1,900 core-min**, against the R1
campaign's 387.4 for fifteen cases. That ratio is the argument.

---

## 6. Labels

Every artifact produced under this pre-registration carries:

- `spec: F7a_REGATE_SPEC.md v1.0 @ c05a03e0`
- `prereg: F7a_REGATE_PREREGISTRATION.md, 2026-08-11`
- the run's own `CASE_PROVENANCE.txt` generator arguments, per R1's convention
- a mesh birth certificate per `docs/standards/MESH_STANDARD.md` §6
- verdict as one of PASS / FAIL / UNGRADEABLE, never a bare percentage
- the threshold-sweep uncertainty beside every deviation

---

## 7. What this pre-registration deliberately does not do

- It does not re-run the gate to produce a verdict. §3 of the spec produced one
  from tracked data; buying compute to reproduce it would be theatre.
- It does not unblock rungs (b) Wigley or (c) DTMB 5415 / KCS. Those remain
  blocked by the standing ladder rule, and R1 §7's scoping question — whether a
  dry-bed contact-line failure should block a wave-resistance case at all —
  is Katie's, not the fleet's.
- It does not propose a tolerance change. 5% is anchored to the comparator's
  demonstrated −4.3% to +1.8%; moving the gate to meet the result is the one
  repair this lab must never make.
