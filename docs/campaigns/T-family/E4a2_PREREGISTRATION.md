# E4a2. fanPressure BC verification — successor rung: the iterative-convergence gate, re-registered

**FROZEN-BY-COMMIT PENDING.** Written 2026-08-24T16:37:15Z (the stamp is `date -u` output
read in the same shell invocation that wrote this file; every stamp in the
freeze record is a command's own dated output, per the supervisor's 2026-08-23
timestamp discipline). **The supervisor commits this freeze BEFORE any case is
built or any solver runs.** The sha256 tables in §6 are the on-disk provisional
reading (`E4a2_runs/FREEZE_CHECK.txt`, machine-captured); they become a freeze
only at that commit, per standing rule 2 and the T10a-R lesson that
hashed-before-compute is weaker than committed-before-compute. **At the freeze
reading the run tree `verification/runs/T-family/E4a2_runs/` contained ZERO
directories of any kind, ZERO numeric time directories and ZERO DONE/STATUS
markers** — the `find` output with its own timestamps is in `FREEZE_CHECK.txt`,
and `build_e4a2.py`, `launch_e4a2.sh` and `run_one_e4a2.sh` each **refuse** to
act on a tree where a case dir, marker or time dir already exists.

Predecessor: **E4a**, pre-registration
`docs/campaigns/T-family/E4a_PREREGISTRATION.md`, sha256
`2ebe2fc89ed7467730310d51630df837fb0f3dd578a05ef702c9b05d32150765`, **frozen by
commit `628e29c4`**; results `docs/campaigns/T-family/E4a_RESULTS.md`, rung
verdict **NOT A RESULT**. Verdict vocabulary fixed by the Verification Charter
§2: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.**

---

## 0. What this rung re-registers, and it is one thing

**Carried over from E4a UNCHANGED — not re-derived, not re-argued, not
re-worded:** the physics; the 2D planar-channel geometry; `nu`; the exact
resistance `R = 12νL/(h³t) = 3.6e5`; the three registered fan curves A, B and
NULL with their exact operating points 1.5e-7, 1.0e-7 and 1.5e-7 m³/s; the
five cases F_c/F_m/F_f/S_f/N_f with their meshes; the §1.5 error derivation
(the `(N²+2)/12` wall term and the bounded entrance term); and rows
**I1, I2, P1, R1, G1, G2, N1, D1, Z1** with their predictions, intervals,
identity tests and falsifiers.

**Re-registered — exactly one item:** the **iterative-convergence gate**.

E4a registered that gate as **bit-identity**: every parsed value of `p`, `U`
and `phi` value-for-value identical between the last two written checkpoints
(`E4_runs/analyse_e4a.py:411-418`, no tolerance, `writePrecision 12`). It did
not close on any of the five cases. The fields still moved in their last
written digit after 20 000 iterations while residuals sat at 1e-10 to 1e-14, so
rule 5 order (1) voided **five registered rows** — R1, G1, G2, N1, D1 — and the
rung returned **NOT A RESULT** (E4a_RESULTS.md §1, §5). E4a's I1/I2/P1 passed
(the BC's own equation held to 3.794e-11 m²/s², mass to 7.082e-10) and its
planted-zero control Z1 held on all three readers in all five cases.

`endTime` and `writeInterval` also change, and **only** to make the new gate
measurable (§2.4). Nothing else in the case inputs changes, and that is
enforced by construction rather than asserted: `build_e4a2.py` **imports the
frozen `build_e4a.py`'s own field, mesh, schemes, solution, transport and
turbulence functions** and writes only `system/controlDict` locally (§4).

### 0.1 The carry-over is executable, not editorial

`E4a2_runs/E4a2_registered.json` carries the blocks `geometry`, `nu`,
`R_exact`, `R_exact_note`, `p_out`, `grid`, `curves`, `cases`, `patches`,
`convergence_fields`, `rows` and `planted_control`. **Every one of them is
asserted DEEP-EQUAL to `E4_runs/E4a_registered.json` at every invocation of
`analyse_e4a2.py`, `build_e4a2.py` and `mark_done_e4a2.py`; a mismatch is a
REFUSAL (exit 2).** The frozen file's own sha256
(`bb363d0232683f50a8f75ecbd15aef436bd72762686764c56027aac6f0401b05`, the blob
committed at `628e29c4`) is verified on disk in the same check. That assertion
— not this paragraph — is the carry-over's provenance.

### 0.2 E4a's measured Q values are NOT predictions here

E4a's comparator printed five deviations beside `converged=False`:
**F_c +1.3699 %, F_m +0.5255 %, F_f +0.1438 %, S_f +0.2387 %, N_f +0.2876 %**
(E4a_RESULTS.md §3). They agreed with §1.5's registered central predictions to
within ~0.07 pp. **They are not used as predictions anywhere in this rung.**
The registered predictions for R1/G1/G2/N1/D1 are §1.5's arithmetic, carried
over unchanged; **no threshold, interval or gate in this file is a function of
E4a's measured numbers.** A match to them is *expected* — same meshes, same
BCs, same solver, same settings, only `endTime` differs — and earns no verdict.

So that the expectation is not merely annotated (the lab's standing complaint
about evidence labelled non-binding), it is armed as a **control**:

**Row X1 — reproduction control.** `|dev(E4a2) − dev(E4a)| ≤ 0.01 pp` per case.
**X1 grades nothing and can produce no verdict; it can only REFUSE (exit 2)**,
exactly like Z1. Its threshold is calibrated so that it cannot fire on the
question this rung is about: iteration drift large enough to move Q by 0.01 pp
(1e-4 relative) between 20 000 and 60 000 would need `r ≈ 2.8e-8` sustained
over twenty intervals, which is **above** the registered floor and trips **C1
first**. X1 can therefore only fire on gross non-reproduction — a wrong mesh, a
wrong curve, a wrong case.

---

## 1. Why the old gate failed, stated before the new one is defended

**It was not a solver failure.** All five E4a cases returned rc=0 with an `End`
line, reached `endTime` 20 000, and met the strict completion rule 5/5. The
gate asked for a property the arithmetic cannot deliver: **exact equality of
every written digit between two checkpoints of a fixed-point iteration whose
linear solves run to a tolerance of 1e-10.**

Three lab lessons name the failure mode from both sides, and both sides bind
this design:

* **T1c §3** — the fine constant-flux case was still moving `T` by 4.081 K
  between checkpoints while its residual read an unremarkable 4e-05, and
  grading it converged put `Nu` at 4.622 against an exact 4.364. **Residuals
  are not the control; the written fields are, and `endTime` is the control.**
  This rung keeps that: `endTime` is fixed, identical for all five cases, and
  **the gate never stops a run** — it is read after the fact.
* **T3 ext1 §2** — *"a flat residual is a floor, not slow decay."* A
  change-sequence that has stopped moving must be read as a floor, and a
  criterion that extrapolates it to zero at infinity is registering an
  impossibility. E4a's bit-identity gate is exactly that criterion.
* **L-243** — a change-based settle criterion cannot tell convergence from
  damping; the cure is to gate on **the targets written**, with a tolerance
  derived from a **field-space distance**. §2.3's clause **C3** is that cure,
  and it is the reason this gate is not merely a looser settle bar.

---

## 2. The new gate — registered, bounded, and derived before any case exists

### 2.1 The measured quantity

For each field `f ∈ {p, U, phi}` and each consecutive pair of retained
checkpoints `(t_{k−1}, t_k)`:

```
V_k(f) = the ordered flat vector of EVERY parsed value of f at t_k
         (internalField first, then every boundary patch carrying a 'value'
          entry, patches in sorted order, vector components flattened)
D_k(f) = max_i | V_k(f)[i] − V_{k−1}(f)[i] |
S(f)   = max_i | V_K(f)[i] |          (peak magnitude at the LAST checkpoint)
r_k(f) = D_k(f) / S(f)
r_k    = max over f of r_k(f)
```

A structural mismatch in vector length between two checkpoints is a **REFUSAL**,
not a degraded reading. `S(f) = 0` is a refusal. Normalising by peak magnitude
rather than range is **conservative**: peak ≤ range, so this reading is never
smaller than the T3-family form (*"at most 1e-6 of that field's range"*,
T3_PREREGISTRATION §5).

### 2.2 The three clauses

| clause | statement | registered constant |
| --- | --- | --- |
| **C1 sustained floor** | `r_k ≤ FLOOR` for **each** of the last **3** consecutive-pair intervals | `FLOOR = 1e-8`, `sustained_intervals = 3` |
| **C2 not growing** | the least-squares fit of `log10(r_k)` against iteration over the last third of the series is **not GROWING**, i.e. NOT (`R² ≥ 0.90` AND slope `≥ +0.01` decades per 1 000 iterations) | `fit_r2_min = 0.90`, `fit_slope = 0.01 dec/1000` |
| **C3 graded-quantity stationarity** | `\|Q(t_K) − Q(t_half)\| / \|Q(t_K)\| ≤ CUM_TOL`, `Q(t) = −Σφ` over the fan patch, `t_half` = the retained checkpoint nearest `endTime/2` | `CUM_TOL = 1e-7` |

**A case is CONVERGED iff C1 AND C2 AND C3.** An unconverged case makes every
row that needs it **NOT A RESULT** (rule 5 order (1)); the gate can only turn a
PASS or GATE FAIL **into** NOT A RESULT, never the reverse.

**C1 is sustained** so that one lucky interval cannot pass the gate. **No
interval-to-interval growth ratio is gated**, and that is deliberate: E4a's own
F_c series grew **1.54×** across its last three intervals (7.707e-10, 4.919e-10,
1.189e-9) while sitting three decades *inside* this floor. A strict
non-growth-between-intervals requirement would void the rung for **bounce at a
floor** — E4a's defect in a new costume. Growth is read from the fitted trend
over the last third, never from one bounce.

### 2.3 Why C3 exists, and why C1+C2 alone would not be enough

C1 and C2 are **change** criteria, and L-243 is explicit that change bounds
nothing about distance to the fixed point: a more strongly damped iteration
reaches a change bar earlier and further from the answer. C3 is a **field-space
distance on the graded target itself**, measured across half the run.

The selftest constructs precisely the trap: a `Q(t)` marching at **9e-9 per
interval** — *inside* the floor, so C1 and C2 both pass — which accumulates to
**1.35e-7** across half the run and **fails C3**. That case is registered as
reading (iv) in §3.3.

### 2.4 Run length and retained checkpoints

| entry | E4a | **E4a2** | why |
| --- | ---: | ---: | --- |
| `endTime` | 20 000 | **60 000** | 3× the iterations, so the floor's stationarity is tested over three times the span |
| `writeInterval` | 5 000 | **2 000** | **30 checkpoints, 29 intervals**: enough series for the C2 fit window (9 intervals) and for the **first crossing** of the floor to be measurable |
| `purgeWrite` | 0 | **0** | retain **all** — the T3 ext1 lesson that `purgeWrite 2` left exactly one measurement and made over-shoot unmeasurable |
| `writePrecision` | 12 | **12** | unchanged: the floor sits 3 decades above the 12-significant-digit last-place quantum, so no precision change is needed |

`writeInterval` **strictly** < `endTime` (L-140), asserted in the comparator's
own refusal set. **No `residualControl` in any case (L-141)** — the frozen
`build_e4a.fv_solution()` is imported unchanged and carries none.

**Restart is not allowed.** `startFrom startTime; startTime 0` and
`runTimeModifiable false`; `run_one_e4a2.sh` re-copies `0/` from `0.orig` at the
start of the run allowed to answer (the strict rule's age guard dates every
field against that `0/U`); guard **G3** refuses any pre-existing numeric time
directory, in both the launcher and the runner. Nothing in this rung can run
twice and nothing can run first.

### 2.5 The floor, derived — the arithmetic, not a preference

**Upper bound — the floor must not be able to move a graded row.**

`Q` is read as `−Σφ` over the fan patch, so

```
|ΔQ| ≤ n_fan · D(phi) = n_fan · r · S(phi),   and   S(phi) ≤ |Q|
⇒ |ΔQ|/|Q| ≤ n_fan · r ≤ 18 × 1e-8 = 1.8e-7  =  1.8e-5 percentage points of dev
```

(`S(phi) ≤ |Q|` because each face flux is a same-signed part of the total.)
The p-route is weaker and does not bind: `Δp ≤ r·p_peak = 1e-8 × 0.054 =
5.4e-10`, and `dQ/d(drive) = 1/(R + 2k₂Q*) = 1/7.2e5 = 1.389e-6`, giving
`ΔQ/Q ≤ 5.0e-9` — **36× smaller than the φ-route**, so φ binds.

Against the carried-over intervals:

| row | half-width to the nearer edge | movement the floor allows | decades |
| --- | ---: | ---: | ---: |
| G1 | 0.199 pp | 1.8e-5 pp | 4.04 |
| G2 | 0.187 pp | 1.8e-5 pp | 4.02 |
| N1 | 0.277 pp | 1.8e-5 pp | 4.19 |
| D1 | **0.117 pp** (narrowest) | 1.8e-5 pp | **3.81** |
| **R1** (order, **binding**) | **0.40** | **3.32e-4** | **3.08** |

**R1 binds**, because an observed order is a function of the triple's
*differences*. From the **carried-over §1.5 arithmetic** — the registered net
central deviations 1.366 / 0.497 / 0.111 %, **not** from any measurement:

```
e21 = 1.5e-7 · (0.497 − 0.111)/100 = 5.790e-10
e32 = 1.5e-7 · (1.366 − 0.497)/100 = 1.3035e-9
e32/e21 = 2.2513,  p = ln(2.2513)/ln(1.5) = 2.0013     ← reproduces the registered 2.00
|∂p/∂Q_c| + |∂p/∂Q_m| + |∂p/∂Q_f|
    = [1/e32 + (1/e32 + 1/e21) + 1/e21] / ln(1.5)
    = 1.892e9 + 6.151e9 + 4.259e9 = 1.2303e10  per (m³/s)
δQ  ≤ 1.8e-7 × 1.5e-7 = 2.7e-14
|δp| ≤ 1.2303e10 × 2.7e-14 = 3.32e-4   against a half-width of 0.40  →  1 204×  =  3.08 decades
```

**The largest floor that still clears three decades on R1 is 1.204e-8.**
`FLOOR = 1e-8` is registered: the floor sits at the top of its admissible
window, and the selftest asserts that a floor of 1.3e-8 would **not** clear
three decades — the choice is bounded from above by arithmetic, not by taste.

**Lower bound — the floor must sit above the write/iteration floor.** At
`writePrecision 12` the last-place quantum of a written value is between
**1e-12 and 1e-11** of that value (leading digit 9 down to 1). The worst case,
**1e-11**, is the ascii resolution floor of `r`. `FLOOR = 1e-8` sits **3.0
decades above it**, so the gate cannot be reading write-precision flicker —
which is the open question E4a_RESULTS.md §5 left on the supervisor's desk and
which this rung's floor is constructed to sit clear of rather than answer.

**Feasibility — cited, and NOT the derivation.** Measured read-only on E4a's
five completed case trees under exactly the §2.1 definition (E4a's tree was not
written to, and no `__pycache__` was created in it):

| case | worst `r(p)` | worst `r(U)` | worst `r(phi)` | **case worst** | `r` at the last interval |
| --- | ---: | ---: | ---: | ---: | ---: |
| F_c | 2.461e-10 | 2.980e-10 | **1.189e-9** | **1.189e-9** | 1.189e-9 |
| F_m | 1.024e-10 | 3.225e-10 | 5.786e-10 | 5.786e-10 | 2.150e-10 |
| F_f | 4.822e-11 | 4.909e-11 | 4.211e-10 | 4.211e-10 | 4.118e-10 |
| S_f | 1.669e-11 | 8.694e-11 | 1.624e-10 | 1.624e-10 | 1.624e-10 |
| N_f | 1.852e-12 | 4.456e-12 | 5.348e-11 | 5.348e-11 | 5.348e-11 |

The worst reading anywhere is **1.189e-9** (F_c, `phi`); `FLOOR` is **8.41×
above it**. **The floor is not derived from this number** — it is derived from
the two bounds above, and E4a's measurement is cited only to show the floor is
reachable, with the achieved value sitting an order of magnitude *inside* it
rather than at it. For scale: this floor is **two decades tighter** than the
T-family's existing registered convergence gate (T3's 1e-6 of the field range).

**And the change is FLAT, not decaying** — which is why the prediction in §3.2
does not depend on further decay. F_f's `p` difference reads **2.600e-12 at all
three of its intervals, identically**; N_f's reads **1.000e-13 at all three**.
That is a floor in T3 ext1 §2's sense, not slow decay.

### 2.6 `CUM_TOL`, derived

```
1e-7 relative in Q  =  1e-5 pp of dev      vs D1's 0.117 pp   →  4.07 decades
|δp_order| ≤ 1.2303e10 × (1e-7 × 1.5e-7) = 1.845e-4  vs 0.40  →  3.34 decades   (R1 binds again)
```

Feasibility, measured read-only on E4a: the worst
`|Q(t) − Q(endTime)|/|Q(endTime)|` over all five cases and all four retained
checkpoints is **3.886e-10** (F_c at 5 000), and `Q` shows **no systematic
drift** — it bounces in the eleventh to twelfth significant digit (N_f moves
**0.000e+00** between 10 000 and 20 000). `CUM_TOL` is **257× above** that
worst reading, and E4a2's C3 window (30 000 → 60 000) is twice the widest E4a
span, so even a doubling leaves >100×.

### 2.7 Disclosed consequence for carried-over row I1 — registered before any solve

E4a's `why_tol` for I1 argued its `8.1e-8 m²/s²` tolerance sat **≥3 decades**
above the last-iteration flux-lag floor **because the gate was bit-identity**.
Under this floor that argument weakens and the weakening is registered here
rather than discovered later:

```
flux-lag bound = |d(dp)/dQ| · ΔQ = 2·k₂·Q* · 2.7e-14 = 3.6e5 × 2.7e-14 = 9.72e-9 m²/s²
                 → 8.3× below I1's carried-over tolerance, not 3 decades
```

**I1's tolerance is NOT changed** — it is carried over. What the row exists to
catch is unaffected: the static-vs-total convention signature `½U_m² = 1.125e-4`
remains **4.06 decades above** the flux-lag bound, and E4a measured I1 at
**3.794e-11**, three decades inside the tolerance. The honest cost is stated:
if I1 were to land between 1e-8 and 8.1e-8 in this rung, this pre-registration
has *already* said that a flux-lag floor of 9.7e-9 is admissible there, and
such a reading would be a **PASS with the headroom argument spent**, not a
clean one.

### 2.8 Reported diagnostics — they grade nothing

* the full `r_k` series per case, all 29 intervals;
* the **first crossing** of the floor (the first `t_k` with `r_k ≤ FLOOR`);
* the T3-ext1-style **classification** of the last-third fit: `DECAYING` /
  `GROWING` / `LIMIT CYCLE` (p95/p05 spread > 3) / `FLOOR`, with slope in
  decades per 1 000 iterations and `R²`;
* the `Q(t)` distance-to-`endTime` series, C3's input;
* per-field `r_K(p)`, `r_K(U)`, `r_K(phi)` and each field's peak magnitude.

Only the `GROWING` flag gates (it is C2). An exactly-zero interval change is
floored at **1e-16** for the log fit and the spread denominator — 5 decades
below the ascii quantum — and is reported and gated as 0.

---

## 3. Registered predictions

### 3.1 Carried-over rows, unchanged

| row | case(s) | registered prediction | interval (PASS) | falsifier |
| --- | --- | ---: | --- | --- |
| **I1** | all 5 | **0** | `≤ 8.1e-8 m²/s²` | any face over tolerance; ~1.125e-4 names the static-vs-total convention error |
| **I2** | all 5 | **0** | `≤ 1e-4` | over tolerance (leak or reader defect shows at O(1)) |
| **P1** | all 5 | **0** outflow faces | `= 0` | any outflow face voids the analytic referent: G1/G2/N1/D1 → NOT A RESULT |
| **R1** | F triple | **2.00** | `[1.6, 2.4]` | outside → GATE FAIL; triple not CONVERGING → NOT A RESULT, no GCI quoted |
| **G1** | F_f | **1.500167e-7** (+0.111 %) | dev `[−0.11, +0.31] %` | outside the interval |
| **G2** | S_f | **1.002130e-7** (+0.213 %) | dev `[−0.02, +0.40] %` | outside; a G1-PASS with G2-FAIL says the machinery fits one curve |
| **N1** | N_f | **1.503345e-7** (+0.223 %) | dev `[−0.12, +0.50] %` | outside; the null's wall term is 2× the fan case's by derivation |
| **D1** | F triple | **1.497045e-7** (−0.197 %) | dev `[−0.35, −0.08] %` | outside; Richardson at ~0 dev falsifies the §1.5 entrance model low |
| **Z1** | all 5 | recovered change == `fl(old+plant) − old` **exactly** | exact-float, no tolerance | any mismatch is a **REFUSAL (exit 2)** |

The comparator asserts, in its selftest, that **every one of these intervals
contains its own prediction**.

### 3.2 The new registered prediction — the gate closes

**Registered before any solve: the convergence gate CLOSES at `endTime` 60 000
for ALL FIVE cases — C1, C2 and C3 all hold for F_c, F_m, F_f, S_f and N_f.**

*Basis:* E4a's `r`-series is already 8.4× to three decades inside `FLOOR` at
20 000 under identical settings, and it is **flat**, so the prediction does not
depend on further decay — only on the floor staying where it is over three
times the iterations. E4a's `Q` is stationary to 3.886e-10 across its whole
retained span, 257× inside `CUM_TOL`.

*Falsifier:* **any** case failing C1, C2 or C3 makes R1/G1/G2/N1/D1
**NOT A RESULT** again and the rung **NOT A RESULT**.

### 3.3 The four readings, registered in advance so the outcome discriminates

Registered now (L-244: register the branches before the run, so the result
discriminates rather than confirms). **None of these is a gate and none changes
a verdict — the rung is NOT A RESULT in all four.**

| reading | supported iff | discriminating measurement |
| --- | --- | --- |
| **(i) the criterion is still too tight** for this solver's achievable floor | the failing case classifies `FLOOR` (\|slope\| < 0.01 dec/1000 or `R²` < 0.90), p95/p05 ≤ 3, and its `r` sits within one decade above `FLOOR` | the classification and the spread |
| **(ii) the solver has a limit cycle** at this precision | the series classifies `LIMIT CYCLE` (p95/p05 > 3), or C2 fails with a `GROWING` fit | the spread, and the fitted slope with its `R²` |
| **(iii) `endTime` was simply too short** | the series classifies `DECAYING` (`R² ≥ 0.90`, slope ≤ −0.01 dec/1000) and still sits above `FLOOR` | the fit; T3 ext1's rule then gives the iterations still needed, `N = 1000·log10(r/FLOOR)/\|slope\|` |
| **(iv) the iterate is stationary in change but not in the graded target** | C1 and C2 hold while **C3 fails** | the `Q(t)` series against the `r_k` series — this is L-243's damping trap showing itself, and only C3 can produce this reading |

---

## 4. Instruments — imported frozen, or declared new

**Imported, never copied, never edited, sha256-verified against the blob
committed at `628e29c4`, refusing on mismatch:**

* `E4_runs/analyse_e4a.py` — the exact-operating-point solver
  (`exact_operating_point`), the curve evaluator (`curve_dp`), the identity
  (`identity_I1`), the `p`/`U`/`phi` readers (`patch_values`,
  `internal_values`, `boundary_nfaces`, `_parse_value`, `_patch_block_opt`,
  `_text`), `mesh_readback`, `read_patch_set`, the planted-zero planters and
  `planted_zero_control` (**Z1 is the frozen control, unchanged**),
  `grade_interval`, `grade_triple`, `dev_pct`, `richardson_corrected`,
  `with_ratio`, `time_dirs`/`tdir`, and `_tri_solve` for the selftest's
  discrete-channel law.
* `E4_runs/build_e4a.py` — `p_field`, `u_field`, `block_mesh`, `fv_schemes`,
  `fv_solution`, `transport`, `turbulence`, `header`, `g`, `fan_curve_entry`,
  and the frozen `guard()` and `verify()` (the one-change-per-case structural
  check).
* `E4_runs/mark_done_e4a.py` — `check()`, the strict completion rule's six
  tests, reused verbatim.
* `T1_runs/analyse_t1c.py` — `gci` at `Fs = 1.25`, reached through the frozen
  E4a module with its declared in-process `R_REFINE` 1.6 → 1.5 redirect.

**Declared departure, registered here rather than discovered later.** Several
frozen functions resolve case paths from their module-level `HERE`. They are
reused through a restoring context manager **`in_dir`** that redirects that
module attribute **in this process only**, for the duration of the call — the
precedent is E4a's own `with_ratio` and T10a-R's `in_tree`. **The frozen files
on disk are never touched**; the selftest proves restoration, and every entry
point additionally refuses if `HERE` resolves to E4a's own run tree or if a
redirect fails to restore.

**`run_one_e4a2.sh` and `launch_e4a2.sh` are not importable** — bash has no
import mechanism. They are produced by a **mechanical rename** of the frozen
originals (`s/_e4a/_e4a2/g; s/\bE4a\b/E4a2/g`) and the claim is verified rather
than asserted: applying the inverse rename returns files **byte-identical** to
`E4_runs/run_one_e4a.sh` and `E4_runs/launch_e4a.sh`. The complete textual
delta — six lines, all of them instrument names in comments and refusal
messages — is recorded in `FREEZE_CHECK.txt`. Guards **G1** (atomic lock),
**G2** (`/proc` cwd scan) and **G3** (no stray numeric time dir) are therefore
the frozen ones.

**New instruments, declared:** `numeric_signature` (a *numeric* field signature
where E4a's was textual, so a magnitude can be taken from it),
`rel_change_series`, `q_series`, `gate_c3`, `gate_converged`,
`classify_series`, `_linfit`, the `in_dir` redirect, and the X1 reproduction
control.

**`--selftest`: 95/95 at the freeze reading** (stamped inside
`FREEZE_CHECK.txt`; synthetic in-memory data, zero case trees, no `__pycache__`
anywhere), covering: the frozen contract and both redirects with their
restoration; the carried-over deep equality on every carried key; every frozen
instrument's sha256; the three exact operating points; the curve clamp; the
`(N²+2)/12` discrete-channel law at all three ladder levels; the identity exact
on constructed data and **flipped by a mutation, both in memory and through the
file readers**; the `neg()` outflow branch; I2 flipped by a mutated outlet φ;
every verdict path (PASS, GATE FAIL high and low, boundary-inside, NOT A RESULT
on an OSCILLATORY triple **with no GCI key present**, rule 5's order); frozen
vs corrected Richardson; **the new gate's PASS path, its C1 failure, its
"one lucky interval is not a sustained floor" failure, its C2 failure on a
growing series that never leaves the floor, and its C3-only failure on a target
still marching**; all four classification paths including an all-zero series;
**E4a's own measured F_c bounce passing the gate**; the planted-zero exact-float
rule on all three readers plus the exactly-zero unplanted control; a planted
relative change of 1e-9 recovered by the `r_k` reader **and** a planted 1e-7
shown to exceed the floor (rule 3's principle applied to the new gate); the
floor and `CUM_TOL` arithmetic recomputed from the registered numbers,
including the assertion that a floor of 1.3e-8 would **fail** the three-decade
requirement; and that every registered interval contains its prediction.

**Mutation control on the selftest itself** (recorded in `FREEZE_CHECK.txt`):
loosening `FLOOR` to 1e-6, shortening the sustained window to 1, loosening
`CUM_TOL` to 1e-3, disabling the C2 growing flag, and stubbing C3 to always
pass each make the selftest **FAIL and exit 2**. The suite is not vacuous.

---

## 5. Cost — measured basis, prediction, and the empty actuals column

Rate **$0.0513/core-h**, owner-stated 2026-08-21/22 (rule 12; the box cannot
read its own billing — `COMPUTE_BUDGET_CHARTER.md` §5 — so every dollar below
is **derived, not measured**). Serial, `nice 15`, one case at a time, nProcs 1,
so core-s equals wall s.

**Measured basis, from E4a's own completion record** (`E4a_RESULTS.md` §7;
`E4_runs/STATUS.F_f` `wall=45`; `log.solve` `ExecutionTime` 44.56):
**5.50e-7 s per cell-iteration** = 44.56 s / (4 050 cells × 20 000 iterations).
E4a's *registered* basis of 7.5e-6 s/cell-iteration, borrowed from
`buoyantBoussinesqSimpleFoam` T1c replicates, over-predicted this solver class
by **13.6×** and **is not used here** — that is E4a's calibration finding
applied, which is what the calibration ledger is for.

| case | cells | iterations | basis 5.50e-7 → core-s | 3× E4a measured wall | **registered core-s** | **actual core-s** |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| F_c | 800 | 60 000 | 26.4 | 39 | **39** | *(empty — filled at completion)* |
| F_m | 1 800 | 60 000 | 59.4 | 69 | **69** | *(empty)* |
| F_f | 4 050 | 60 000 | 133.7 | 135 | **135** | *(empty)* |
| S_f | 4 050 | 60 000 | 133.7 | 135 | **135** | *(empty)* |
| N_f | 4 050 | 60 000 | 133.7 | 129 | **134** | *(empty)* |
| blockMesh + checkMesh ×5 | — | — | — | — | **3** | *(empty)* |
| extra checkpoint I/O (26 further ascii writes per case) | — | — | — | — | **30** | *(empty)* |
| comparator (5 × 30 checkpoints × ~24 700 parsed floats) | — | — | — | — | **120** | *(empty)* |
| **total** | | | | | **665 core-s = 11.083 core-min = 0.18472 core-h ≈ $0.0095 derived** | *(empty)* |

Per case the registered figure is the **larger** of the two estimates,
disclosed rather than averaged; E4a's per-case measured bases ranged 5.36e-7
(N_f) to 7.93e-7 (F_c), the coarse case being dearer per cell-iteration because
fixed per-iteration overhead does not scale with cell count. Meshing: E4a
measured **2 core-s** across five cases against a registered 15; **3** is
registered here.

**10× stop-and-investigate threshold: 1.8472 core-h (≈ $0.0948)** for the rung.
Per case, any run exceeding 10× its predicted wall is **stopped** and
investigated, not waited out: F_c 390 s, F_m 690 s, F_f 1 350 s, S_f 1 350 s,
N_f 1 340 s — every one of them below rule 12's 3 600 wall-s stall rule, so the
per-case threshold binds first. Disk: ~360 MB of retained checkpoints across
the five cases against 298 GB free.

**The actuals column is filled at process completion only, never at
registration** (Sanaa's 2026-08-23 estimate-vs-actual law, rule 12): the
completion report states actual core-minutes from the `STATUS`/`log.solve`
records, the ratio actual/predicted with the gap attributed (contention, waste
and misprediction named separately, waste never absorbed into the ratio), and
lands a row in **`docs/COST_CALIBRATION.md`** under that file's append rules
and the rule-10 private-index protocol.

---

## 6. Freeze set — provisional until the supervisor's commit

`E4a2_runs/FREEZE_CHECK.txt` (machine-captured; every stamp inside it is
`date -u` output from the capturing invocation) records **zero directories of
any kind, zero numeric time directories, zero DONE/STATUS markers** in the run
tree, the selftest line, the five mutation controls, the shell-script
round-trip identity, and these tables.

**This rung's own instruments:**

| file | sha256 (provisional until commit) |
| --- | --- |
| `E4a2_runs/E4a2_registered.json` | `c8877e6ca376a04300eebd3c69d906ba06a5b8dec30c5747d701a23718471d6b` |
| `E4a2_runs/build_e4a2.py` | `f788ba740938777f60621e9bf6bcacbb7e0682ef5192657f49fdb866ab9a2c9b` |
| **`E4a2_runs/analyse_e4a2.py`** | **`26a10ef4d55319b8de01988a2d24631f15a680ae91dc066d6aab9e1096cf7261`** |
| `E4a2_runs/mark_done_e4a2.py` | `48c01195f10bd6d97ddde69f5ace586cf4a9e4953f93e4fa9b6299ac937d4aae` |
| `E4a2_runs/run_one_e4a2.sh` | `9c01d3d70453c5698f74c709ae150a96134b4c024ba84e9824f4a30f6245c09d` |
| `E4a2_runs/launch_e4a2.sh` | `2444d9644e9065d0afcbb5f3929674ed85f89ddc174fab6c206bc9567dbd9659` |

**Frozen imports (the blobs committed at `628e29c4`; re-verified on disk at
every invocation, refusing on mismatch):**

| file | sha256 |
| --- | --- |
| `E4_runs/E4a_registered.json` | `bb363d0232683f50a8f75ecbd15aef436bd72762686764c56027aac6f0401b05` |
| `E4_runs/build_e4a.py` | `451eae3682bff7f89f31147c1d2d74fe1badc4c2af2c0e0f40e76ca665e46956` |
| `E4_runs/analyse_e4a.py` | `a9f31c3f569181f27b17bcaca318ce1f1a0a3f0e85e788a4214c8d8d5d63ff4b` |
| `E4_runs/mark_done_e4a.py` | `b152ed0071bfe8cea060fc8164587ffeec7ca02ab0c6ce259565935d4b10fbe6` |
| `E4_runs/run_one_e4a.sh` | `226fd26b019a7fe73b559dda36451ca328ee371bcb1c8fb6b776d024f12ffe19` |
| `E4_runs/launch_e4a.sh` | `0e2b893fd134cba67975792d3defefb453ed929ca4d122f22022e4cad9c81274` |
| `T1_runs/analyse_t1c.py` | `60893b28e284127f61b41842c520897a2202cb024d5a4d260272c6ee7e6c5135` |

**Order of operations, binding.** (1) The supervisor commits this file,
`FREEZE_CHECK.txt` and the six instruments (private-index protocol, rule 10)
and verifies the committed blobs hash identical to the table above; (2) only
then `build_e4a2.py` writes the five case dictionaries — importing the frozen
builder's functions for everything except `system/controlDict`, and running the
frozen `verify()` one-change-per-case check; (3) only then `launch_e4a2.sh`
runs cases, serially. The builder, launcher and runner each refuse a tree where
any case dir, marker or time dir already exists — **nothing in this rung can
run twice, and nothing can run first.** Amendments before the commit are legal
and must name the condition checked (the case directories that do not exist);
after first compute, gates are closed and changes land only as dated addenda
that cannot alter a gate, threshold, cap or label.

---

## 7. What this rung cannot see, whatever it returns

Written now, while zero numbers exist, so it cannot be trimmed to fit them.

**Carried over from E4a §6, unchanged and still true:**

* **Nothing about any real fan** — no datasheet, no digitised curve, no
  measurement uncertainty; stage (b)'s subject, on Sanaa's desk.
* **Nothing about `direction out`** — only the `in` branch is exercised.
* **Nothing about the `nonDimensional` path**, the tableFile legacy path or
  `outOfBounds` handling.
* **Nothing about the mass-flux or compressible branches** — simpleFoam pins
  the volumetric/incompressible pair by construction.
* **Nothing about the `max(Q,0)` clamp under reversed flow** — P1 predicts no
  outflow face, so the clamp is never armed.
* **Nothing about MRF or actuation-disk fans**, and **nothing about
  turbulence** — laminar by registration.
* **The entrance term is bounded, not verified**; only D1 probes it, weakly.
* **I2's generosity** (1e-4) means sub-1e-4 conservation defects pass unseen.

**New to this rung, and these are the ones that matter here:**

* **The gate certifies a STATIONARY ITERATE, not a proven fixed point.** C1 and
  C2 are change criteria; L-243 is explicit that change bounds nothing about
  distance to a fixed point without a contraction estimate, and at a floor the
  contraction factor approaches 1 so the implied distance bound diverges. C3
  narrows this — it is a field-space distance on the graded target across half
  the run — but a systematic drift **slower than 1e-7 over 30 000 iterations**
  is invisible to all three clauses, and this rung has no instrument that would
  see it. What is registered is the weaker, honest claim: *whatever motion is
  left cannot move a graded row by as much as a thousandth of its interval.*
* **The gate cannot distinguish a write-precision floor from a genuine
  iteration floor.** It is constructed to sit three decades clear of the ascii
  quantum rather than to answer the question E4a_RESULTS.md §5 left open. If
  the answer to that question matters later, it needs a rung with
  `writePrecision` as its variable, and this is not it.
* **Damping is not controlled for.** Relaxation factors are carried over
  unchanged (`p 0.3`, `U 0.7`), so this rung says nothing about where the change
  bar would land under different damping — L-243's actual finding. All five
  cases share the settings, so the comparison *between* them is clean; the
  absolute stopping point is not characterised.
* **A single `endTime` for all five cases is a choice, not a measurement.**
  60 000 is registered from E4a's flat floor, not from a convergence-rate model.
  If a case turns out to be `DECAYING` rather than at a floor, reading (iii)
  fires and the rung is NOT A RESULT — this rung deliberately has **no
  extension arm**, because an extension chosen after seeing the numbers is the
  thing rule 2 exists to prevent.
* **X1 cannot distinguish "E4a and E4a2 agree because both are right" from
  "both share a defect."** It is a reproduction control on identical inputs and
  it is blind to any error common to both rungs — every carried-over instrument
  is common to both by design.
* **A `NOT A RESULT` here is not a diagnosis.** The four readings in §3.3 name
  which measurement supports which explanation; naming is not proving, and the
  choice between them, and any successor rung, is the supervisor's.
