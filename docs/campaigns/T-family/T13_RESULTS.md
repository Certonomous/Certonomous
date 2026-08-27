# T13 results — natural convection in a vertical slot, conduction regime (Batchelor 1954 parallel flow), EXACT tier

Graded 2026-08-27 by the frozen comparator at three levels.
**RUNG VERDICT: `PASS` — four of four graded rows PASS.**

Pre-registration: `docs/campaigns/T-family/T13_PREREGISTRATION.md`.
Run root: `verification/runs/T-family/T13_runs/`.
Comparator stdout retained at `verification/runs/T-family/T13_runs/log.analyse_t13.20260827T163830Z.txt`;
machine record at `verification/runs/T-family/T13_runs/gate_t13.json`.

---

## 1. The freeze set, hashed before it was believed

All six §10 freeze-set files verified on disk against the registered values,
**on both channels** (git blob AND sha256 prefix) — a manifest can be internally
consistent and externally false, so neither channel is taken alone.

| file | registered blob | on disk | registered sha256₁₆ | on disk | |
| --- | --- | --- | --- | --- | --- |
| `exact_t13.py` | `e730a915` | `e730a915` | `bdc0d2c5faae445a` | `bdc0d2c5faae445a` | MATCH |
| `build_t13.py` | `e1e8894b` | `e1e8894b` | `25825620285134ae` | `25825620285134ae` | MATCH |
| `analyse_t13.py` | `127ae6d3` | `127ae6d3` | `d69cff74cea8ba18` | `d69cff74cea8ba18` | MATCH |
| `mark_done_t13.py` | `02f43ea7` | `02f43ea7` | `fbd78fd5daacc0a8` | `fbd78fd5daacc0a8` | MATCH |
| `run_one_t13.sh` | `cc88b1fe` | `cc88b1fe` | `a4a5ca72bac800d6` | `a4a5ca72bac800d6` | MATCH |
| `T13_registered.json` | `aecd9682` | `aecd9682` | `f53d44929c48dbcf` | `f53d44929c48dbcf` | MATCH |

**No drift. No frozen file was edited.** `__pycache__` was cleared before running
so no stale bytecode could stand in for a frozen source — the frozen `.py` files
themselves were not touched.

## 2. Completion — the strict rule (rule 4), three of three

`mark_done_t13.py` (frozen, `02f43ea7`): **`DONE T13_VS_c`, `DONE T13_VS_m`,
`DONE T13_VS_f`**, rc 0. All three `STATUS.*` read `rc=0 … capped=no
checkmesh_rc=0 note=clean`; last time == `endTime` on each (10 000 / 20 000 /
40 000). Per the registration, `capped` is an **INFRASTRUCTURE** field and is
never a completion conjunct (L-342).

## 3. The analytic reference, verified before any comparison

The comparator verifies its own exact solution before using it:
`phi'' = xi − 1/2` to worst 2.6e-10; `phi(0) = phi(1) = 0`; `∫phi = −2.0e-19`;
`A == B` to 2.9e-17; `xi* = 0.2113248654`, `phi_max = 8.0187537387e-03`;
antisymmetric. Its two readers (`lagrange4`, `cubic_max_location`) are **exact on
the analytic cubic** at N = 20/40/80.

## 4. Gate (1) controls — every level, all clear

| level | C_CONV worst final-10 % initial residual | C_PLAT | W0 | W1 |
| --- | --- | ---: | ---: | ---: |
| c | Uy 1.00e-12, T 9.88e-13, p_rgh 1.16e-10 | 3.266e-12 | 2.467e-12 | 6.738e-07 |
| m | Uy 1.75e-13, T 9.99e-13, p_rgh 1.96e-10 | 1.115e-11 | 1.877e-12 | 6.203e-07 |
| f | Uy 3.03e-12, T 4.35e-12, p_rgh 1.95e-09 | 7.542e-11 | 1.877e-12 | 6.014e-07 |

`Ux` is a degenerate (~0) channel and is **REPORTED, never gated** (L-338):
3.15e-11 / 3.77e-12 / 1.01e-11.

**`C_RA` operand identity (L-331) holds on all three levels**: `nu`, `Pr`,
`beta`, `TRef`, `g`, `T_hot`, `T_cold`, `L`, `N` were **read from each case's own
files** and `Ra_L` recomputed from them reads **100.00000000004** against the
registered 100 — inside the 1e-9 floor. The rung graded the case it actually ran.

## 5. Planted-zero controls (rule 3) — five readers, five PASS

Every graded reader was shown able to see a non-zero **before** its zero was
believed, and the plant was sized per L-340:

| reader | plant | field | cells | recovered | |
| --- | ---: | --- | ---: | ---: | --- |
| G1 | 1.304e-04 | `U` | 1 | 8.214e-04 | PASS |
| G1b | 1.304e-04 | `U` | 1 | 7.591e-03 | PASS |
| G2 (RMS reader) | 1.495e-04 | `T` | **80 (ALL-ROW)** | 1.234e-03 | PASS |
| G3 | 1.495e-04 | `T` | 1 | 1.974e-01 | PASS |
| W1_max | 1.304e-04 | `U` | 1 | 1.539e-01 | PASS |

Demonstrated detection floor **1e-07 × scale** on every reader. **The G2 plant is
an ALL-ROW plant, not a point plant** — a point plant into an RMS reader over 80
cells is attenuated by √80 and would have understated the reader's blindness;
the registration sizes it correctly.

## 6. THE FOUR GRADED ROWS — 4 of 4 `PASS`

**Two Roache-triple rows, both `CONVERGING` at the derived order:**

| row | fine value | reference | deviation | band | triple | state | p | GCI | verdict |
| --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | --- |
| **G1** `v(ξ*)/u_ref` | 8.0243919252e-03 | 8.0187537387e-03 | +5.638e-06 (rel **+7.031e-04**) | ±1.5e-3 rel | (8.108965e-03, 8.041306e-03, 8.024392e-03) | **CONVERGING** | **2.0000** | 8.7829e-02 % | **PASS** |
| **G1b** `ξ_max` | 2.1125721509e-01 | 2.1132486541e-01 | **−6.765e-05** (rel −3.201e-04) | ±1.5e-4 abs | (2.102444e-01, 2.110544e-01, 2.112572e-01) | **CONVERGING** | **1.9975** | 4.0103e-02 % | **PASS** |

Both triples are monotone, so the GCI at Fs = 1.25 is quoted; the Richardson
extrapolant is carried `REPORTED_ONLY` and is not a graded value.

**Two EXACT-class rows, graded by ABSOLUTE FLOOR — and this needs saying plainly:**

| row | fine value | floor | triple | state | verdict |
| --- | ---: | ---: | --- | --- | --- |
| **G2** RMS of (T − T_lin)/dT | 6.2626e-11 | ±1e-06 | (4.1028e-12, 3.3543e-12, 6.2626e-11) | OSCILLATORY | **PASS** |
| **G3** `\|Nu_L − 1\|` | 1.9896e-10 | ±2e-04 | (4.8801e-11, 1.0136e-10, 1.9896e-10) | DIVERGENT | **PASS** |

**A `DIVERGENT` triple beside a `PASS` is not a rule-5 breach here, and the
reason is pre-registered rather than invented after the fact.** Both rows carry
`exact_class: true` in `gate_t13.json`. The registration states the ground in
terms: *"a linear T is in the null space of the scheme's truncation error, so its
triple is EXACT/DEGENERATE by construction and rule 5 (2) would return NOT A
RESULT for a row that cannot be wrong by discretisation; the triple states are
PRINTED, the verdict is the floor."* The triples are printed exactly as rule 5
requires and **no GCI is quoted on either** (`gci_pct: null`). The measured
values sit **four to six orders of magnitude inside their floors** — the
"divergence" is round-off wandering at 1e-11, not a physical trend.
**Flagged for the verification supervisor as a standing-rule-5 boundary case**,
because a reader who sees only the triple state and the verdict could reasonably
ask; the answer is the registration, and it was written before compute.

## 7. THE SIX REGISTERED PREDICTIONS, SCORED — five HIT, one MISS

- **P1 — HIT.** G1 and G1b triples `CONVERGING` with p in [1.5, 2.5]; derived
  expectation 2.000/2.000. Measured **2.0000** and **1.9975**.
- **P2 — HIT, on both clauses.** G1 relative deviation at f predicted in
  [+4.9e-4, +9.1e-4] and POSITIVE: measured **+7.031e-04**, positive, and it lands
  on the derived value +7.03e-04 essentially exactly. The second clause — *"c and
  m OUTSIDE the ±1.5e-3 band"* — also holds: c 8.108965e-03 and m 8.041306e-03
  both sit above the band's upper edge 8.030782e-03.
- **P2b — HIT.** `ξ_max` error at f predicted in [−8.8e-5, −4.7e-5] and NEGATIVE:
  measured **−6.765e-05**, again on the derived value.
- **P3 — HIT.** `|Nu − 1| < 1e-4` at f: measured **1.99e-10**, six orders inside.
- **P4 — MISS, and it is the one worth keeping.** It predicted *"witness W1 <
  1e-7 on every level (a priori bound ~1e-9 relative at 8L from the ends)"*.
  **Measured 6.738e-07 (c), 6.203e-07 (m), 6.014e-07 (f) — about 6× the
  prediction and roughly 600× the a priori bound.** The control still **passes**:
  its registered floor is 1e-6 and every level is inside it. But the margin is
  **1.5×, not the 1 000× the a priori estimate implied**, and W1 is the control
  that decides whether a level is in the parallel-flow regime at all. The
  breakdown shows where it comes from: at ±1L and ±2L the agreement is 1e-11 to
  1e-9, and **the whole of W1 is the ±4L stations** (v 4.5–4.8e-07, T 5.7–6.7e-07).
  It is also **almost level-independent** — it barely moves from c to f — which
  says it is a genuine end-effect at ±4L, not discretisation error. **Carry
  forward: a taller slot or witness stations no further out than ±2L would
  restore the margin; the a priori 1e-9 bound at 8L should not be reused.**
- **P5 — HIT.** G2 RMS at f < 1e-7: measured **6.26e-11**.
- **P6 — HIT.** All three levels met C_CONV and C_PLAT inside their registered
  `endTime`; none was capped.

## 8. Cost — rule 12, and the estimate missed by 3.17×

- **Predicted:** the registration names the **scratch rate** as the POINT the
  ledger compares against — **139.308 core-min** (1.908 + 15.267 + 122.133). The
  ceiling-rate figure is **215.892**; the cap total is **572**.
- **Measured: 442.167 core-min** = (91 + 1 233 + 25 206) wall s × 1 rank ÷ 60,
  from the three `STATUS.*` `wall_s` fields.
- **Gross = cleaned.** `T13_VS_f` is over the 3 600 wall-s stall figure at
  25 206 s and **is not a stall**: rc 0, `capped=no`, C_CONV and C_PLAT met, last
  time == `endTime` 40 000. **WASTE: 0.000 core-min**, named separately — no
  re-fire, no abandoned case, **no level reached its cap** (worst `VS_f` at 84.0 %
  of its 500; the total at 77.3 % of 572).
- **Ratio actual/POINT 3.174** (2.048 against the ceiling-rate figure).
- **Attribution: rate-versus-mesh misprediction, not contention and not waste —
  and the fine level BROKE THROUGH THE CEILING RATE that was supposed to bound
  it.** Measured core-s per cell-iteration: **c 1.4219e-06, m 2.4082e-06, f
  6.1538e-06** — a **4.33× rise across a 16× cell increase**. Against the three
  registered rates: c is **0.795×** the scratch rate (cheaper than predicted),
  m **1.346×**, and **f is 3.440× the scratch rate, 2.220× the K0f point rate,
  and 1.048× the T4 CEILING rate**. A ceiling that is exceeded is not a ceiling.
- **The transferable correction, and it is the third independent sighting.** The
  scratch rate was measured on **400 iterations of the 6 400-cell coarse case**
  and then applied to a 102 400-cell level. Per-cell-iteration cost is **not
  mesh-independent** for this solver: it grows roughly as cells^0.5 over this
  range. The same direction is already on the ledger at **C-143** and **C-150**
  (T5, Model B's c→m scaling) and in **K0f** (§6: L3 rate 1.73–1.78× the basis
  against L1's 1.21–1.28×). **A POINT rate measured at the coarse level must be
  scaled with cell count before it is applied to a fine level, or it will
  under-predict by 2–3× at the top of a three-level ladder.**
- **Dollars, DERIVED, NOT MEASURED** at the owner-stated $0.0513/core-h
  (`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing):
  **$0.3781** against a POINT of $0.1191.
- Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit from the tail.

## 9. Disclosures

- **The rung verdict `PASS` rests on two Roache rows and two floor rows**, and the
  floor rows are the ones whose triples are degenerate. Anyone quoting T13 as a
  four-row grid-convergence result would be overstating it: **G1 and G1b are the
  grid-convergence evidence**, and both are clean at p ≈ 2.
- **W1's margin is 1.5×, not the ~1 000× the a priori bound implied** (§7, P4).
  The control passed on its registered floor and is reported here as the
  narrowest thing in the rung.
- `__pycache__` was removed before the run. No frozen file was edited (rule 6).
- **Nothing was sent, filed, uploaded, posted or registered outside this box**
  (rule 7).

---

# APPENDED 2026-08-27T18:55Z — DISCLOSURE: `G2` and `G3` are `PASS` ON AN ABSOLUTE FLOOR WITH NON-CONVERGING TRIPLE STATES PRINTED BESIDE THEM, and the comparator's exactness bypass is UNGUARDED

**Document version 1.0 -> 1.1**; 1.0 is the text above, which carried no version
line and is not edited by this section. **Lines whose number changed above this
section: 0.** No gate, band, threshold, floor, cap, label or verdict moves.
Drafted by a heat-transfer grading lane at the supervisor's direction, on the
supervisor's own check-3 finding; every number below was re-read by the drafting
lane from `gate_t13.json` and from the comparator source rather than relayed.

## 10. What a reader of `gate_t13.json` will see, and why it is not the T1b defect

**Opening that file shows `"triple_state": "DIVERGENT"` next to `"verdict": "PASS"`.**
That pairing is exactly the shape `CLAUDE.md` rule 5 exists to forbid, and a
reader is entitled to an explanation without having to reconstruct one.

**THE TWO ROWS, AS MEASURED.**

| row | quantity | triple `c` / `m` / `f` | state | order | registered band | margin |
|---|---|---|---|---|---|---|
| `G2` | RMS over the mid-height row of `(T - T_lin)/dT` | 4.1028e-12 / 3.3543e-12 / 6.2626e-11 | **OSCILLATORY** | — | ±**1e-06** | **1.60e4 ×**, 4.20 orders |
| `G3` | `Nu_L` from the half-cell wall gradient | 4.8801e-11 / 1.0136e-10 / 1.9896e-10 | **DIVERGENT** | **-0.8931** | ±**2e-04** | **1.01e6 ×**, 6.00 orders |

**BOTH VERDICTS STAND, AND WHAT SAVES THEM IS THE ABSOLUTE FLOOR, NOT THE
BYPASS.** The registration's premise for these two rows is that the linear `T`
profile lies in the null space of the scheme's truncation error, so the
discretisation error should be zero. **The measurement CONFIRMS that premise:**
every one of the six values is at round-off. The `OSCILLATORY` and `DIVERGENT`
labels are the Roache classifier reading round-off noise — `G3`'s observed order
of **-0.8931** is a slope fitted through three numbers that are all of order
1e-10 — and a sign pattern in noise is not a convergence behaviour. **No GCI is
quoted for either row** (`gci_pct` is `null` in both), which is correct and is
what rule 5 requires when the three values are not monotone.

**THE READERS WERE DEMONSTRATED ABLE TO SEE A BAND VIOLATION, WHICH IS THE
THING THAT ACTUALLY MAKES A FLOOR PASS TRUSTWORTHY.** All five planted-zero
controls PASS with a **demonstrated detection floor of 1e-07** (§5), `G2` and
`G3`'s own readers included. That floor sits **an order of magnitude below
`G2`'s ±1e-06 band and 2 000× below `G3`'s ±2e-04 band** — so any value large
enough to fail either gate would have been visible to the reader that reported
it. The measured values (1e-11 … 1e-10) lie *below* the demonstrated detection
floor and are therefore **indistinguishable from zero by this instrument**,
which is precisely the registered prediction and not a defect in it. Standing
rule 3 is satisfied in the way that matters here: the reach that had to be
established is reach down to the **band**, and it was established.

## 11. THE DEFECT — an exactness DECLARED is not an exactness MEASURED

`analyse_t13.py:405` reads

```
if not exact_class and tr["state"] != "CONVERGING":
```

and `exact_class` arrives as a **literal `True`** in the `specs` tuple at
`:485` (`G2`) and `:486` (`G3`), consumed by the loop at `:488`. **It is
therefore a blanket bypass of the whole of rule 5's gate (2), not an
EXACT-specific exception.** The flag is never confronted with the triple state
that was actually measured, and nothing anywhere checks that the values are at
round-off before the gate is skipped.

**The consequence is not visible in this rung's numbers and is real anyway:
the same flag would have passed a genuinely divergent row carrying an O(1)
error just as silently.** What protects `G2` and `G3` is that their values
happen to be at round-off — a property of the answer, not of the code. A gate
whose correctness depends on the answer coming out right is not a gate.

**The correct construction already exists in this family, twenty-three minutes
later.** `analyse_t9aR1b.py:217-225` **DERIVES** the state instead of
declaring it:

```
if max(abs(e21), abs(e32)) < roundoff_K:
    return dict(state="EXACT", e21=e21, e32=e32, ...)
```

— exactness is a **measured** property of the triple against a registered
round-off floor, and both `e`s are carried in the record either way. **T13
DECLARES what T9a-R1b MEASURES**, and the T9a-R1b form is the pattern of record.

**Not repaired.** `analyse_t13.py` is frozen; rule 6 forbids editing it, and a
measurement-script diff is the supervisor's own non-delegable read
(`SUPERVISION_CHARTER` §3 check 1). No `_PROPOSED` file was written. Docketed.

## 12. CORRECTION TO A DESK ITEM — `T13` and `W1b` are NOT the same question

The board has carried the item *"rule 5's EXACT clause met a registered-floor
exception TWICE today (T13 G2/G3, W1b R1)"*. **That framing is withdrawn: it is
accurate for `W1b` and NOT accurate for `T13`.**

| | `W1b` `R1` | `T13` `G2` / `G3` |
|---|---|---|
| triple state | **`EXACT`** — **DERIVED FROM THE MEASUREMENT** | **`OSCILLATORY`** / **`DIVERGENT`** — measured, and non-converging |
| evidence | `e21` -2.842e-13, `e32` 3.240e-12, deviation **2.899e-12 K** vs a **1e-06 K** floor | values at 1e-11 … 1e-10 vs floors 1e-06 / 2e-04 |
| how exactness was established | `analyse_t9aR1b.py:217-225` **tests** `\|e21\|,\|e32\| < roundoff_K` | `analyse_t13.py:485-486` **asserts a literal `True`** |

**`W1b` is a genuine EXACT triple that met a registered floor. `T13` is a
NON-CONVERGING triple whose row passed on an absolute floor with the gate
bypassed.** Both verdicts stand, but **the argument that rescues an EXACT row
does not on its face rescue a DIVERGENT one**, and the two must not be cited
together as one precedent. The corrected form is the one to carry forward.

## 13. WHETHER A T1b-PATTERN REPAIR IS OWED — the drafting lane's reading, PROPOSED and NOT APPLIED

**Reading: a retrofit amendment to this rung is NOT owed. Concur with the
supervisor's provisional view, and for a reason that can be stated as a test
rather than a preference.**

1. **No value and no verdict here is wrong.** The band verdict is computed
   **first** (`analyse_t13.py:402`) and the gate is one-way (`:403-405`), so
   the recorded `PASS` **is** the band verdict, and the band verdict is correct
   on the measured values. A repaired comparator re-run on this data would
   reproduce every number at relative difference 0.000e+00 **and every verdict
   unchanged** — because a measured-exactness test on values 4 to 6 orders
   below their floors returns `EXACT`, which passes gate (2) legitimately.
2. **That is the substantive difference from T1b.** T1b's defect changed an
   answer, which is what obliged a retrofit that reproduced the frozen values.
   Here the defect changes no answer on this data, so a retrofit would purchase
   **disclosure only** — and disclosure is exactly what §10-§12 deliver, at zero
   risk to the frozen bytes.

**ONE THING THE LANE WOULD ADD TO THE SUPERVISOR'S FRAMING, AND IT IS NOT A
DISAGREEMENT.** "Fix it in the next registration" is right but is not
sufficient on its own, because **the hazard here is REUSE, not this rung.** The
bypass is unscoped: `exact_class=True` disables gate (2) at any magnitude, so
the moment `analyse_t13.py`'s `specs` pattern is lifted into an extension rung,
a different `Ra_L`, or a re-run on a repaired mesh, it becomes capable of
passing a genuinely divergent O(1) row — and lifting a sibling comparator's
`specs` block is the normal way this family builds a new rung. **The lane
therefore proposes, for the supervisor's decision and not as an action taken:
that this comparator be marked NOT-FOR-REUSE in its own results record, and
that `analyse_t9aR1b.py:217-225` be named the pattern of record for any future
exact-class row.** That costs nothing, touches no frozen file, and closes the
only route by which this defect could ever produce a wrong verdict.

**Nothing in §13 has been applied.** No comparator was changed, no `_PROPOSED`
file written, no solver launched. Nothing was sent, filed, uploaded, posted or
registered outside this box (rule 7).
