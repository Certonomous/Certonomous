# T9a-H. The composite wall and fin re-graded under `Gauss harmonic`

Campaign T, tier 4, rung **T9aH** — the successor rung to T9a, run under the
interface scheme T9a-D identified as the whole of T9a's 2.41 mK miss. Written
2026-08-23, **before any T9aH case exists and before any T9aH run directory
exists** (§9 pastes the check). Run tree
`verification/runs/T-family/T9aH_runs/` — **not yet created.**

Basis: `T9a_PREREGISTRATION.md`, `T9a_RESULTS.md` (D442),
`T9aD_PREREGISTRATION.md`, `T9aD_RESULTS.md` (D454, L-227).

---

## 0. What this rung is, and the four things it may not do

**T9a GATE FAILED on R1** — the composite wall's first interface temperature,
2.41 mK below exact against a 0.92 mK GCI band (`T9a_RESULTS.md` §1). **T9a-D
proved the whole of that 2.41 mK is the interface scheme**: its A1 arm PASSED
with `laplacian(DT,T) Gauss harmonic corrected` dropping the R1 level error to
round-off at every level, drop factor **8.15e+08** at level f against a
registered threshold of 3 (`T9aD_RESULTS.md` §1, §10). T9a-D was a **diagnosis**
and graded nothing as a rung. **This document registers the rung.**

Four prohibitions, registered before anything is built:

1. **It does not re-open T9a.** T9a's verdict stands exactly as its frozen
   comparator returned it: **GATE FAIL on R1**, R0 and R2 PASS, R3/R4 GATE
   REACHED, four controls MET. No T9a case is re-solved, no T9a number moves,
   no T9a row is re-labelled. T9aH is a **new rung with its own rows**.
2. **It weakens no gate and no threshold.** Every threshold the frozen T9a
   comparator carries — the Roache triple rule, the GCI at `Fs` = 1.25, the
   0.025 % fin one-dimensionality floor, the three controls — applies here
   unchanged and unweakened, on the T9aH cases. **Where the frozen rule returns
   an unfavourable verdict on a T9aH row, that verdict is published as
   returned.** §4.1 registers, in advance, that this is the *expected* outcome
   for the wall rows and why.
3. **It may not widen a band because numbers looked wrong** (Charter §2d.1:
   *"a band is not an instrument; it is the hypothesis's own scoring rule"*).
   Every threshold below is a number fixed in this document before any case
   exists.
4. **It may not edit a frozen file.** `analyse_t9a.py`, `exact_t9a.py`,
   `T9a_registered.json`, `check_t9a_mesh.py`, `mark_done_t9a.py`,
   `run_one_t9a.sh` and `run_chain_t9a.sh` are **copied byte-identical** into
   the new tree and their sha256 verified against the committed blobs at
   analysis time (§6.1). Where a reader needs a different conductivity (§4.4),
   the change is made **in memory** for one call and restored, exactly as
   T9a-D did, and the restoration is asserted.

---

## 1. GRADING PATH — SPLIT. READ THIS BEFORE BELIEVING ANY OUTPUT

> **Rows FR0–FR4 and controls C1–C3 are graded by the FROZEN T9a comparator,
> BYTE-IDENTICAL — no new code, no modified code.**
>
> **Path:** `verification/runs/T-family/T9aH_runs/analyse_t9a.py`, a byte copy of
> `verification/runs/T-family/T9a_runs/analyse_t9a.py`
> **sha256 `dd2d6bf0ac690fdcca90719cb6586168763d311ea3b5a7ad937fdf054ecac9da`**,
> verified today identical to the blob committed at **`239ed2b8`**
> (*"T9a: freeze comparator before any case exists (Charter 2d)"*, 2026-08-20
> 19:02:01 Z), together with
> `exact_t9a.py` **`d3f2558c1471ab3debd6e2804f58552e27b5708e18b81d219a2fe6d017d3d0b8`**
> and `T9a_registered.json`
> **`66b03c7de15ceeba500dded8c496346023053ed2d0746de8749c324e1edb40ed`**,
> both also identical to their `239ed2b8` blobs. The comparator is
> `HERE`-anchored (`analyse_t9a.py:57`) and its case list is fixed
> (`ALL_CASES`, line 68), so a byte copy in a new tree grades the new tree with
> **no argument, no flag and no edit.**
>
> ---
>
> **Rows H1–H6 and controls HC1–HC4 are graded by a NEW INSTRUMENT,
> `analyse_t9aH.py`, WHICH DOES NOT YET EXIST.**
>
> **`SUPERVISION_CHARTER.md` §3 check 1 applies and may not be delegated: the
> supervisor must read `analyse_t9aH.py` personally — as source, and as a
> `diff -u` against the frozen `analyse_t9a.py` for every reader it claims to
> import unmodified — BEFORE any H-row or HC-control output is believed.** A
> relayed check is a summary, not a check.
>
> The new instrument exists because the frozen comparator **cannot grade an
> exact scheme**: its only band is a Roache GCI on differences that, under
> `Gauss harmonic`, are round-off (§4.1). It imports the frozen readers
> (`measure_wall`, `measure_fin`, `iterative_convergence`, `read_internal`,
> `read_points`, `cell_centres`, `latest_time`, `boundary_blocks`, `refuse`)
> **unmodified**, and grades **absolute** distances from the full-precision
> closed form. It carries **no GCI band and arms none** (§5.2), so it cannot
> repair, widen or replace any frozen band.
>
> **Also new, and also to be read before belief:** `build_t9aH.py` (builder),
> `run_chain_t9aH.sh` (the three extra cases; it invokes the byte-identical
> `run_one_t9a.sh`). **Not new:** everything in the box above, plus
> `run_one_t9a.sh` **`163c4345199cc8f2cfa1eb9406fedb8c44d3ff9f4d037f6b0d07eb495f8f2761`**,
> `run_chain_t9a.sh` **`cbf3b957f5cd7d7a18f799112ca7936b824c2e37532515447fca575634999e7d`**,
> `check_t9a_mesh.py` **`cb7fa05ab05d4751f0254419a199931f1d7cd7334d94075418ecad41c86688bc`**,
> `mark_done_t9a.py` **`0feff87e148e1f69436a39f505f8fa8f49273f4c4669b41ad5bd9f4c6a7da669`**
> — all copied byte-identical and re-hashed at analysis time.

**`analyse_t9aH.py` is a NEW INSTRUMENT, not a repair (Charter §2d.1).** It is
written for a new rung before any T9aH case exists; nothing frozen changes, no
published number moves, and T9a's `gate_t9a.json`
(`7c4c6826283f98d31e0c313cd713412b969bb2a4486b78ea31617eb1b3a5f4f8`) is read
and never written. §2d.1's four-condition repair exception is **not invoked and
not needed**.

**Its own freeze, registered here as the condition of launch:** it must be
written, `--selftest`ed, **sha256-recorded in a dated addendum to this
document, and that addendum committed, BEFORE any T9aH case directory
exists** — the ordering T9a-D got wrong and recorded as its own rule forward
(`T9aD_RESULTS.md` §A.6: *"Commit the pre-registration before launching what it
registers, not after"*). **Every threshold it grades against is fixed in §4 of
this document, which is committed now.** `T9aH_registered.json` is a
transcription for the machine; **where it and this document disagree, this
document governs, and the instrument must refuse rather than grade.**

---

## 2. The cases, and the single change

Ten cases. The seven frozen names are used **verbatim** so the byte-identical
comparator grades them with no edit.

| case | kind | cells | `laplacian(DT,T)` | `k` of layer 2 | graded by |
| --- | --- | ---: | --- | ---: | --- |
| `W_c` | wall, level c | 35 (10/20/5) | **`Gauss harmonic corrected`** | 0.04 | frozen + new |
| `W_m` | wall, level m | 56 (16/32/8) | **`Gauss harmonic corrected`** | 0.04 | frozen + new |
| `W_f` | wall, level f | 90 (26/51/13) | **`Gauss harmonic corrected`** | 0.04 | frozen + new |
| `W_C3` | uniform-solid control (both faces 350 K) | 90 | **`Gauss harmonic corrected`** | 0.04 | frozen + new |
| `F_c` | fin, level c | 500 (50×10) | **`Gauss harmonic corrected`** | — | frozen + new |
| `F_m` | fin, level m | 1280 (80×16) | **`Gauss harmonic corrected`** | — | frozen + new |
| `F_f` | fin, level f | 3328 (128×26) | **`Gauss harmonic corrected`** | — | frozen + new |
| `RL_f` | **replica / null arm**: level f, **`Gauss linear`** | 90 | `Gauss linear corrected` | 0.04 | new only |
| `H40_f` | contrast 40×, harmonic | 90 | **`Gauss harmonic corrected`** | **0.4** | new only |
| `H4000_f` | contrast 4000×, harmonic | 90 | **`Gauss harmonic corrected`** | **0.004** | new only |

**The single change from T9a is the `laplacian(DT,T)` entry.** Mesh ladder,
geometry, conductivities, temperatures, solver (`laplacianFoam`), `endTime`
1000, `writeInterval` 100 (L-140), `purgeWrite` 2, absent `residualControl`
(L-141) and the `DICPCG` tolerance are the frozen T9a values, rebuilt to the
same `T9a_registered.json`. `RL_f`, `H40_f` and `H4000_f` are **extra
directories the frozen comparator does not know** (`ALL_CASES`, line 68) and
therefore cannot touch; they are graded only by the new instrument.

**`RL_f` carries two registered jobs** (§6.3 and §4.5): it is the **builder
control** — the new builder must reproduce the frozen `W_f` — and it is the
**registered trivial baseline of the hypothesis** under Charter §2c: "harmonic
is exact" has an obvious null, *the same case without harmonic*, and it is
registered here, before its own run, with the record that registered it.

**If ESI v2606 refuses `Gauss harmonic corrected`** the exact error text is
recorded verbatim, the affected rows are **BLOCKED**, and **no substitute is
improvised.** T9a-D established acceptance (`T9aD_RESULTS.md` §10), so a
refusal here would itself be a finding.

---

## 3. The exact references, at all three contrasts

Closed form, `ΣR = Σ L/k`, `q″ = 50 / ΣR`, `T_i1 = 350 − q″·L₁/k₁`,
`T_i2 = 300 + q″·L₃/k₃`. Re-derived at every comparator run by the **frozen**
`exact_t9a.py` along its two independent routes (series resistance versus a
harmonic-face FV solve by the Thomas algorithm), which must agree or the run
refuses; for the 40× and 4000× cases `WALL_LAYERS` is overridden **in memory**
and restored, and the restoration is asserted (§0 prohibition 4).

| quantity | **400×** (`k₂` 0.04) | **40×** (`k₂` 0.4) | **4000×** (`k₂` 0.004) |
| --- | ---: | ---: | ---: |
| `ΣR` [m²K/W] | 2.56375 | 0.31375 | 25.06375 |
| `q″` [W/m²] | **19.502681618722573** | **159.3625498007968** | **1.9949129719216** |
| `T_i1` [K] | **348.7810823988298** | **340.0398406374502** | **349.8753179392549** |
| `T_i2` [K] | **300.0243783520234** | **300.199203187251** | **300.0024936412149** |

The 400× and 40× columns reproduce, digit for digit, the values already
published in `T9a_RESULTS.md` §1 and `T9aD_RESULTS.md` §1.1. The 4000× column
is new and is derived here, before any case exists, by the same arithmetic;
**the comparator re-derives it and refuses if the two routes disagree.**

**The registered constants in the frozen `T9a_registered.json` are transcribed
to six decimals** (`q` 19.502682, `T_i1` 348.781082, `T_i2` 300.024378). The
distance from those transcriptions to the full-precision closed form is
**1.955e-06 %, 1.143e-07 % and 1.173e-07 %** respectively. **That distance is
the whole subject of §4.1** and it is registered here, before the run, so it
cannot later be produced as an excuse.

---

## 4. Registered rows, thresholds, predictions and falsifiers

**Fixed before any case exists.** Each threshold is a number. Each row carries
Charter §2a's two questions answered on its face.

### 4.1 FR0–FR4 — the frozen rule, on the T9aH cases

These are the frozen comparator's own rows R0–R4, run on T9aH's cases. **In
this rung's records they are named FR0–FR4 and are never presented as T9a's
R0–R4.** Their thresholds are the frozen ones and are not touched: the value
graded is the finest level, the band is that row's own Roache GCI at
`Fs` = 1.25 on nominal `r` = 1.6, and the fin rows carry the 0.025 % floor.

| row | quantity | reference (frozen transcription) |
| --- | --- | ---: |
| FR0 | wall `q″` [W/m²] | 19.502682 |
| FR1 | wall `T` interface 1 [K] | 348.781082 |
| FR2 | wall `T` interface 2 [K] | 300.024378 |
| FR3 | fin efficiency `η` | 0.8332367 |
| FR4 | fin tip ratio | 0.7523781 |

> **REGISTERED PREDICTION, AND IT IS UNFAVOURABLE TO THIS RUNG'S OWN
> HYPOTHESIS. NO FROZEN WALL ROW CAN COME BACK `PASS`.**
>
> Under `Gauss harmonic` the three wall levels reproduce the closed form to
> round-off — T9a-D measured `|e1|` = 0 / 3.2e-12 / 3.0e-12 K on the identical
> meshes (`T9aD_RESULTS.md` §1.1) — so the differences the GCI is built from
> are round-off, and **every branch of the frozen rule lands on a verdict that
> is not PASS:**
>
> | branch, decided by `gci()` (`analyse_t9a.py:219`) | what the frozen rule does | registered verdict |
> | --- | --- | --- |
> | `f_m − f_f == 0.0` → **EXACT** | band = **0.0**; a zero band grades only a literally exact match | **GATE FAIL** at the transcription distance of §3 (1.955e-06 % / 1.143e-07 % / 1.173e-07 %) |
> | `e32/e21 < 0` → **OSCILLATORY** | no band armed | **NOT A RESULT** |
> | `p ≤ 0` **DIVERGENT** / `p < 0.5` **STAGNANT** | no band armed | **NOT A RESULT** |
> | `p ≥ 0.5` → **CONVERGING** on round-off differences | band ≈ 1e-13 %, far below the transcription distance | **GATE FAIL** |
>
> **The most likely single outcome is OSCILLATORY → NOT A RESULT**, because
> T9a-D's harmonic level errors (0, −3.2e-12, −3.0e-12 K) are not monotone.
> **This is registered as the prediction, not discovered as an excuse.** The
> frozen verdict is published exactly as returned and is **not** re-labelled,
> softened or repaired; the rung's accuracy claim rests on H1–H6, which are
> graded against the **full-precision** closed form and are stated separately.
>
> **FR3 and FR4 are predicted GATE REACHED** — reported, not graded — with
> bands ≈ 0.00077 % and 0.00011 %, unchanged from T9a to within 1e-9, because
> the fin has uniform `k` = 200 and harmonic interpolation of a constant is
> that constant.
>
> **Registered consequence for the frozen controls, so it is not read later as
> a defect:** `analyse_t9a.py:541` forms `c1_met = b0 is not None and
> c1_dev > b0`, and lines 570–575 do the same for C3-wall. **If a wall row arms
> no band, C1 and C3-wall come back `NOT MET` mechanically**, the comparator
> prints *"the rung is unsound"* and exits 1. **That line is reproduced
> verbatim in the results and is not explained away**; the controls' substance
> is separately re-graded, against absolute thresholds, as HC1 and HC3 (§4.5).
> No frozen threshold is changed to avoid this.
>
> *Identity test (§2a).* **What makes FR0–FR2 fail?** Any deviation above a
> band that will be zero or unarmed — so they are, under this scheme, rows that
> almost cannot pass. **Could a wrong treatment pass them?** Under the EXACT
> branch, only a treatment reproducing the six-decimal transcription bit for
> bit; under the no-band branch, nothing passes at all. **They are reported as
> the frozen rule's honest output on an exact scheme and are the reason H1–H6
> exist.**

### 4.2 H1–H3 — exactness at 400×, the rung's substantive rows

Graded by the new instrument against the **full-precision** references of §3,
at **every** level c/m/f, not only the finest.

| row | quantity | threshold — **PASS** if | **GATE FAIL** if | predicted (basis: `T9aD_RESULTS.md` §1.1, `D_A_*`) |
| --- | --- | --- | --- | ---: |
| **H1** | `\|T_i1 − 348.7810823988298\|` at c, m, f | **max ≤ 1.0e-08 K** | any level above it | 0 / 3.2e-12 / 3.0e-12 K |
| **H2** | `\|q″ − 19.502681618722573\| / q″_exact` at c, m, f | **max ≤ 1.0e-08** | any level above it | ≤ 3e-11 (nine printed digits identical) |
| **H3** | `\|T_i2 − 300.0243783520234\|` at c, m, f | **max ≤ 1.0e-08 K** | any level above it | +0.0000000 mK at every level |

**Why 1.0e-08 K, fixed before the run.** It is **3 333×** above the largest
residual T9a-D measured under this scheme (3.0e-12 K) and **240 918×** below
the 2.41 mK the rung exists to remove. A threshold inside that gap cannot be
met by a scheme that merely *improves* the interface treatment; it can only be
met by one that is exact to round-off.

*Identity test (§2a).* **What makes H1–H3 fail?** Any interface treatment whose
residual survives at the 1e-8 K level — including `Gauss linear`, whose level-f
residual is 2.41e-03 K, five orders above the bar (this is HC4, §4.5).
**Could a wrong treatment pass?** Two ways, and both are wired shut: a case
that silently ignored the fvSchemes entry (**refused** by the scheme readback,
§6.2), and a **measurement reader that cannot see anything**, which would
report `|e| ≈ 0` while broken (**refused** by the planted-error control on the
measurement path, §6.5 — the instrument that matters most in a rung whose
headline is a zero). **These rows establish exactness on a 1-D orthogonal mesh
with the interface on a face, and nothing more** (§7).

### 4.3 H6 — fin invariance (specificity)

**H6.** The fin rows under harmonic must reproduce T9a's published fin values.
**PASS if, at every level c/m/f, `|η_T9aH − η_T9a| ≤ 1.0e-09` and
`|tip_T9aH − tip_T9a| ≤ 1.0e-09`**, T9a's values read from
`T9a_runs/gate_t9a.json` (on disk since 2026-08-20, hash in §6.1) and **not
re-solved**. **GATE FAIL otherwise.**

*Identity test (§2a), stated bluntly.* **This row is close to an identity and
is declared as one.** The fin's `k` is uniform, so the harmonic and arithmetic
face conductivities are the same number to within one ulp; agreement is
arithmetic. **It is therefore evidence about the BUILD and the SCHEME'S
SPECIFICITY — that the change did nothing where it must do nothing — and is
never counted as evidence that harmonic is correct.** It is reported in the
rung's tally as a specificity row and is excluded from any statement of the
form "N of M rows support harmonic."

### 4.4 H4–H5 — contrast, the falsifier C1 earned

T9a-D's **C1 GATE FAILED in the direction opposite to its directive**: under
`Gauss linear`, weakening the contrast 400× → 40× **grew** the R1 error 27–31×,
to −168.06 / −104.16 / −64.99 mK, because the untouched second interface then
supplies 83.2 % of the missing resistance and the flux-continuous
reconstruction's cancellation collapses from 89 % to 26 %
(`T9aD_RESULTS.md` §2.3). **So contrast is a live axis on which an interface
treatment can behave non-monotonically, and a claim of exactness that has been
tested at one contrast only is untested.**

| row | case | threshold — **PASS** if both hold | **GATE FAIL** if | predicted |
| --- | --- | --- | --- | ---: |
| **H4** | `H40_f` (40×) | `\|T_i1 − 340.0398406374502\| ≤ 1.0e-08 K` **and** drop `= \|e1(D_C_f)\| / \|e1(H40_f)\| > 1.0e+06`, with `e1(D_C_f) = −64.99408 mK` **read from `gate_t9aD.json`, not re-solved** | either fails | `\|e1\| ~ 1e-11 K`, drop ~1e+09 |
| **H5** | `H4000_f` (4000×) | `\|T_i1 − 349.8753179392549\| ≤ 1.0e-08 K` **and** `\|q″ − 1.9949129719216\|/q″_exact ≤ 1.0e-08` | either fails | `\|e1\| ~ 1e-11 K` |

**Falsifier 1 (C1-informed).** *Any* growth of the harmonic residual with
weakened contrast falsifies exactness. Concretely: **H4 GATE FAILS if
`|e1(H40_f)| > 1.0e-08 K`**, and the C1 pattern reproduced under harmonic —
the 27–31× growth — would put it at ~1e-10 K, still inside the bar, so the row
deliberately also carries the **drop** threshold against the measured linear
value: a harmonic residual that failed to beat `Gauss linear` by six orders at
40× fails H4 even while sitting under the absolute bar.

**Falsifier 2 (the opposite direction).** **H5 GATE FAILS if the residual grows
with a 10× *stronger* contrast.** 4000× has no linear counterpart in this rung
and **no drop factor is claimed there** — only absolute exactness. If the
mechanism is what §2.1 of `T9aD_RESULTS.md` says it is (`k_f/d` is the exact
series conductance of the two half-cells for any spacing ratio and any jump),
the residual is contrast-independent; if it is not, 4000× is where it shows.

**Falsifier 3 (coarse mesh).** H1–H3 are graded at **every** level including
the 35-cell coarse mesh. **A scheme that is exact only once the mesh is fine
fails H1–H3 at level c**, which is a claim T9a's own band machinery could never
have made.

*Identity test for H4–H5 (§2a).* **Fail if** the residual moves with contrast.
**Could a wrong treatment pass?** A treatment exact on this 1-D geometry for
reasons peculiar to it — which is exactly what §7 refuses to generalise from.

### 4.5 Controls, each of which MUST FAIL

The frozen C1/C2/C3 run unchanged inside the frozen comparator (§4.1 registers
what a missing band does to them). The new instrument re-grades their substance
against **absolute** thresholds, which no band can void:

| control | realisation | must | predicted |
| --- | --- | --- | ---: |
| **HC1** wrong resistance rule | finest wall `q″` against `k̄·ΔT/L`, `k̄` the arithmetic mean of the three `k` | **FAIL H2's 1.0e-08 bar** | dev 98.80 % |
| **HC2** perfect fin | finest `η` against `η = 1` | **FAIL H6's 1.0e-09 bar** | dev 16.68 % |
| **HC3** trivial baseline (Charter §2c) | the **solved** uniform solid `W_C3` pushed through the identical pipeline | **FAIL H1, H2 and H3** on all three quantities | `q″` ≈ 0, `T_i1` = `T_i2` = 350 K |
| **HC4** the hypothesis's null arm (Charter §2c) | **`RL_f`** — same mesh, same `k`, **`Gauss linear`** | **FAIL H1, H2 and H3** | `e1` = −2.40918e-03 K, 2.4e+05 × the bar |

**HC4 is the discrimination test and it is the one that makes H1–H3 evidence.**
A row that returns the same verdict for the hypothesis and for its registered
trivial baseline may be reported and may not be counted (§2c). Here the null
arm — the identical case without harmonic — **misses H1's threshold by five
orders of magnitude**, so the set of rows the hypothesis passes that its
absence also passes is **empty**. The null is registered here, before its own
run, with the record that registered it.

---

## 5. Roache triple gating, STAGNANT, and the collapse floor

### 5.1 The frozen rule, unchanged

**A row whose grid triple is not `CONVERGING` is `NOT A RESULT`, whatever its
value.** Order of application, unchanged from T9a and from CLAUDE.md rule 5:
(1) any level not iteratively converged or not plateaued → NOT A RESULT;
(2) triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → the frozen
comparator's registered handling (`EXACT` arms a literal zero band, the other
three arm none); (3) `CONVERGING` → PASS inside the band else GATE FAIL, GCI
printed at `Fs` = 1.25. **The gate can only turn a PASS or GATE FAIL into NOT A
RESULT, never the reverse.** **No GCI is ever quoted where the three values are
not monotone.**

### 5.2 What a STAGNANT triple does to each row — registered in advance

T9a-D found the m/f/**x** triple **STAGNANT at `p` = 0.130** and showed that a
band armed there would have been **17.21 mK against a 1.54 mK error, 11× too
wide** — the exact inverse of T9a's 2.6×-too-narrow band on the same quantity
(`T9aD_RESULTS.md` §2.2). **So a fourth level is NOT added to this rung**, and
the following is fixed before the run:

| row family | STAGNANT (`p` < 0.5) | OSCILLATORY | DIVERGENT (`p` ≤ 0) | EXACT |
| --- | --- | --- | --- | --- |
| **FR0–FR4** (frozen) | **NOT A RESULT**, no band, three values and the state printed beside it | **NOT A RESULT** | **NOT A RESULT** | frozen rule: zero band; verdict as returned (§4.1) |
| **H1–H6** (new) | **unaffected** — they carry no band and make no order claim; the state is printed beside every H row | unaffected | unaffected | unaffected |
| **HC1–HC4** | unaffected — absolute thresholds | unaffected | unaffected | unaffected |

**And the rung may not quote an order.** **Registered collapse floor: 1.0e-06 K
on the wall temperature levels and 1.0e-06 relative on `q″`.** If all three
level errors of a quantity fall below its floor, **no observed order, no
Richardson extrapolate and no GCI derived from that triple is quoted anywhere
in the rung's records** — the differences are round-off and an order read from
them measures the last bits of a double. The floor is **1000× below** the
1e-3 K scale of the effect being removed and **300 000× above** the 3e-12 K
residual expected, so it fires on a collapsed triple and on nothing else.

**The floor governs only what the rung may SAY about orders and bands. It
cannot turn a frozen verdict into anything else**, and it is registered here,
before the run, precisely so that it cannot later be read as an escape invented
to rescue a prediction — the discipline T9a-D's A2 row used
(`T9aD_PREREGISTRATION.md` §2.1).

**Richardson sign, disclosed and not repaired.** The frozen `gci()` prints a
sign-reversed extrapolate (`T9a_RESULTS.md` §8.1). It stays as it is; the
frozen comparator is not edited. The new instrument **prints no Richardson
extrapolate at all**, because §5.2's floor will have voided every wall triple
it could have been computed from.

---

## 6. Instruments armed, each named

### 6.1 Frozen-file hash refusal

At every analysis run, the seven copied files are hashed and compared to the
values in §1. **Any mismatch refuses (exit 2) — the rung produces no numbers.**
Additionally, `T9a_runs/gate_t9a.json` must still hash
`7c4c6826283f98d31e0c313cd713412b969bb2a4486b78ea31617eb1b3a5f4f8` and
`T9a_runs/gate_t9aD.json`
`96e0dce0ea8b57c069aa0f48060ebc9605c0ee3314ba7abf228de6440dc19993` at the end
of the rung. **`T9a_runs/` is READ-ONLY for this rung**: the only files read
are those two JSONs. If either moved, **every T9aH row is NOT A RESULT** and
the movement is reported rather than corrected.

### 6.2 Scheme readback refusal

The frozen comparator **does not read `fvSchemes`** — it verifies geometry and
the per-cell `DT` map only. So the new instrument reads
`system/fvSchemes` **back off disk** from each of the ten cases and **refuses**
unless `laplacian(DT,T)` is literally `Gauss harmonic corrected` on the nine
harmonic cases and `Gauss linear corrected` on `RL_f`. Without this, a case
that silently ignored the entry could return anything (§4.2's identity test).

### 6.3 Replica refusal — the builder as a controlled variable

`RL_f` must reproduce `gate_t9a.json`'s `W_f` to **1e-9 K** on `T_i1` and
`T_i2` and **1e-7 W/m²** on `q″`. **If it does not, every T9aH row is NOT A
RESULT**, because the rung's single-change claim would then be a statement
about a new builder rather than a measurement. A control that cannot fail
informatively is wired as a **refusal**, never as a green light — T9a-D's
`D_R_f` precedent, which reproduced `W_f` to 0.000e+00 K.

### 6.4 Strict completion rule, with the age guard

`mark_done_t9a.py` (byte-identical copy) applies the six tests of
`T1b_L4_AMENDMENT.md` §7 to the seven frozen cases, and the new instrument
imports its `check()` **unmodified** to apply the same six to `RL_f`, `H40_f`
and `H4000_f`: **rc = 0; an `End` line in `log.solve`; last written time ==
`endTime` (1000); the fields the comparator reads (`T`, `DT`) present at that
time; `ExecutionTime` line count == 1000; and every field at `endTime` NEWER
than the case's own `0/T`** — the age guard, `0/` being re-copied from `0.orig`
at the start of the run allowed to answer (`run_one_t9a.sh`). **A case short of
any clause gets no marker, and the frozen comparator refuses the rung as
PENDING.** The builder refuses to write into a case directory that already
holds `0` or a time directory.

### 6.5 Planted zeros — two of them, and the second is the load-bearing one

**A zero from a reader not shown able to see a non-zero is not evidence.** This
rung's headline is a set of zeros, so it plants twice. **Both plants are made on
scratch copies OUTSIDE the run tree; the case tree is not touched.**

1. **Convergence reader.** +1.234e-03 K planted into one cell of `900/T` in a
   scratch copy of `W_f` **and** of `H40_f`. The frozen
   `analyse_t9a.iterative_convergence` must return `max_change` =
   **1.2340000e-03 K** and state **NOT_CONVERGED** on both. **If it cannot see
   the plant, every row depending on a convergence zero is NOT A RESULT.**
2. **Measurement reader — the one this rung actually needs.** In a scratch copy
   of `W_f`, the cell adjacent to interface 1 in `1000/T` is perturbed by
   **+1.234e-03 K**, and the frozen `measure_wall` must move `T_i1` by
   **|ΔT_i1| ≥ 1.0e-05 K** (expected ≈ 1.18e-03 K, since the flux-continuous
   reconstruction puts 95.3 % of its weight on the layer-1 cell at this
   contrast — `T9aD_RESULTS.md` §2.3). **If `T_i1` does not move, the near-zero
   H1/H2/H3 errors are not evidence and every H row is NOT A RESULT.** The
   registered floor is 1000× above H1's own threshold, so a reader that can see
   the plant is a reader that could have seen a failure.

### 6.6 Mesh verification, read from the mesh

`check_t9a_mesh.py` (byte-identical copy) over the seven frozen cases; the new
instrument drives its `check_wall()` **unmodified** over `RL_f`, `H40_f` and
`H4000_f` (with the layer-`k` map overridden in memory and restored, asserted).
**Every geometric constant is read from `constant/polyMesh/points`, never
assumed** — the T1c lesson that cost 9 % of a Nusselt number. `checkMesh` rc
and `Mesh OK` recorded per case in `STATUS.*`. The frozen comparator carries
the same checks on its grading path as refusals.

---

## 7. What this rung cannot show, registered in advance

- **It cannot make T9a pass, and does not try.** T9a's GATE FAIL on R1 is
  frozen. T9aH is a different rung on different cases.
- **It cannot establish that `Gauss harmonic` is correct for a conjugate
  rung.** It can establish exactness for **piecewise-constant `k` with the
  interface on a mesh face, on a 1-D orthogonal mesh, with a fixed-temperature
  or Robin boundary**. T9b's coupled interface, a non-orthogonal mesh, a graded
  or temperature-dependent `k`, and contact resistance are all outside it.
- **It cannot show harmonic is safe to adopt everywhere.** Nothing here
  measures it on any advective term, on any turbulent thermal diffusivity, or
  on any quantity beyond this wall's `q″`, `T_i1`, `T_i2` and the fin's two
  rows.
- **It measures no fluid, no turbulence model and no thermal closure.** Both
  fluids are boundary conditions.
- **It cannot rescue the GCI band.** T9a-D showed the Roache band on this
  quantity lands 2.6× too narrow on one triple and 11× too wide on the next
  (`T9aD_RESULTS.md` §2.2). This rung does not fix that; it steps around it by
  grading absolute distances from an exact reference, **which is only available
  because this is an EXACT-tier rung** and is not a method any rung with a
  merely experimental reference can borrow.
- **H6 is a specificity row, close to an identity, and supports nothing.**
- **It produces no fidelity chip.** The rows grade a solver's discretisation
  against closed-form theory, not physics against the world.

---

## 8. Cost, registered before launch

**Unit: core-minutes (wall s × ranks ÷ 60).** `nProcs` 1 on every case; the
chain is **serial**, so peak occupancy is **1 core of 16**. Other lanes' solver
processes on this box are **not touched** (four were reported running to this
lane at the time of writing: pids 442445, 450274, 488219, 757934); wall times
therefore include contention, and that is stated rather than absorbed.

**Basis, and where it is read.** `T9a_RESULTS.md` §10's cost table — seven
cases, 8.18 core-seconds of per-case wrapper wall, `F_f` (3328 cells) dominant
at 5.85 s — and §5's provenance table, whose chain runs 19:08:20.0 →
19:08:30 Z, i.e. **≈ 10 s of chain wall clock at 1-second resolution on the
finish stamp**. `T9aD_RESULTS.md` §9 — eight small wall cases, **chain wall
clock 6.60 s = 0.825 s per case** — and its registered lesson, quoted: *"The
registered figure was a solver-time ceiling described as a core-second ceiling;
that is the error, and the next arm should register the chain wall clock."*
**This document registers the chain wall clock.**

| item | basis | predicted |
| --- | --- | ---: |
| chain of the seven T9a-shaped cases | T9a's own chain, §5 | 10.0 core-s |
| chain of `RL_f`, `H40_f`, `H4000_f` | T9a-D's 0.825 s/case | 2.5 core-s |
| **solver chains, total** | | **12.5 core-s = 0.208 core-min = $1.78e-04** |
| `blockMesh` ×10, `postProcess` (`writeCellCentres` at t0 and t=1000, `writeCellVolumes`) across two comparators, and the comparators themselves | T9a-D §9's disclosure that these are non-zero OpenFOAM, ~1.2 s per invocation | ≤ 77.5 core-s |
| **REGISTERED TOTAL PREDICTION** | | **≤ 90 core-s = 1.50 core-min = $1.28e-03** |
| **REGISTERED CAP** | 3.3× the prediction | **300 core-s = 5.00 core-min = $4.28e-03** |

**Rate: c7a.4xlarge at $0.0513/core-h. `cost_basis`: reported-by-owner, not
measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure above is
owner-stated, corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`, and is
**not** a measurement.

**The overrun rule: an overrun STOPS THE RUN; it does not get a new budget.**
Accumulated core-seconds are read from the `STATUS.*` wall figures plus the
chain clock. **On exceeding 300 core-seconds the chain is stopped**, what has
completed is reported with its verdicts, the remainder is **PENDING**, and the
overrun is reported as waste rather than absorbed. **A row over 3600 wall s is
a stall** and is reported as such.

$4.28e-03 is **five thousand times** under the $25 per-run pre-authorisation.
Registering it is not optional: a proposal with no cost is disqualified.

---

## 9. Launch discipline — registered, NOT executed

**This lane launches nothing.** No case is built, no mesh is generated, no
solver is started, no compute is spent by this document. **Launch
authorisation is the supervisor's**, after the supervisor has personally
checked this pre-registration is committed (`SUPERVISION_CHARTER.md` §3
check 4) and personally read `analyse_t9aH.py` (§1).

**The condition of the freeze, CHECKED and not asserted** (Charter §2b(1): the
amendment/registration rule requires naming the run directory that does not
exist and showing the check):

```
$ date -u +%FT%T.%3NZ && ls -d verification/runs/T-family/T9aH_runs; echo "rc=$?"; \
  find verification/runs/T-family -maxdepth 1 -name 'T9aH*' -print | wc -l
2026-08-23T19:45:57.814Z
ls: cannot access 'verification/runs/T-family/T9aH_runs': No such file or directory
rc=2
0
```

**`verification/runs/T-family/T9aH_runs/` does not exist**, and no path
matching `T9aH*` exists anywhere under `verification/runs/T-family/`. There is
no answer on disk to tune any threshold in §4 to, and that is demonstrated
above rather than claimed.

**The registered order of operations, which is the rule T9a-D took forward
after breaching it** (`T9aD_RESULTS.md` §A.6):

1. **This document is committed.** ← the only step this lane performs.
2. The run tree is created; the seven frozen files are copied byte-identical
   and re-hashed against §1.
3. `analyse_t9aH.py` and `build_t9aH.py` are written, `--selftest` run, and
   **their sha256 recorded in a dated addendum to this document, committed,
   while the tree still holds no case directory** — the freeze condition
   re-checked with a timestamped command and pasted, not asserted.
4. The supervisor reads `analyse_t9aH.py` personally (§1) and authorises.
5. Only then: build, `blockMesh`, mesh check, the two serial chains, markers,
   both comparators.

**Amendments to this document are legal only while step 2 has produced no case
directory**, and any such amendment must state the condition and how it was
checked. **After the first solver starts, gates are closed**: changes land only
as dated addenda that cannot alter a gate, a threshold, a cap or a label, and
originals are struck, never rewritten.

---

## 10. Status

**NOT BUILT, NOT RUN, NOT LAUNCHED. Zero compute spent.** Every number in this
document comes from a record already on disk (`T9a_RESULTS.md`,
`T9aD_RESULTS.md`, `gate_t9a.json`, `T9a_registered.json`, the file hashes of
§1) or from closed-form arithmetic in §3 that involves no solver and no case.

**Registered verdict vocabulary for every row above: PASS / GATE REACHED /
GATE FAIL / NOT A RESULT / BLOCKED / PENDING, and nothing else.**

---

## Addendum A (2026-08-23) — steps 2 and 3 executed: the tree, the instruments, their hashes and their selftest

**Lines whose number changed above this section: 0.** This addendum is appended
at the foot; §§1–10 are byte-identical to the text committed at
`0078fe9c25ac58e7ef1fda0cd97bab8884d4c5d2` (sha256
`84af4208157418efcb41457f346e54a5f41e6360e5a5d7855bb8acd5ff629f0b`).

**It alters no gate, no threshold, no band, no cap and no label.** Every number
in §4, §5, §8 stands exactly as committed. **Nothing has been built and nothing
has been run**: no case directory, no `blockMesh`, no `checkMesh`, no solver,
zero core-seconds spent against the 300 core-second cap.

Authorised by the heat-transfer supervisor to perform **steps 2 and 3 of §9
only**, after the supervisor's own check of the committed pre-registration.
**Steps 4 and 5 — the supervisor's personal read of `analyse_t9aH.py`, and
launch — have not happened and are not this lane's to take.**

### A.1 Step 2 — the run tree, and the copies verified against the committed blobs

`verification/runs/T-family/T9aH_runs/` created. Copy hashes, compared file by
file — the three grading-path files against the blobs at **`239ed2b8`**, the
support files against **HEAD**:

```
2026-08-23T19:55:16.928Z
--- copy vs 239ed2b8 committed blob (3 grading-path files) ---
analyse_t9a.py         dd2d6bf0ac690fdcca90719cb6586168763d311ea3b5a7ad937fdf054ecac9da  IDENTICAL
exact_t9a.py           d3f2558c1471ab3debd6e2804f58552e27b5708e18b81d219a2fe6d017d3d0b8  IDENTICAL
T9a_registered.json    66b03c7de15ceeba500dded8c496346023053ed2d0746de8749c324e1edb40ed  IDENTICAL
--- copy vs HEAD blob (4 support files) ---
check_t9a_mesh.py      cb7fa05ab05d4751f0254419a199931f1d7cd7334d94075418ecad41c86688bc  IDENTICAL
mark_done_t9a.py       0feff87e148e1f69436a39f505f8fa8f49273f4c4669b41ad5bd9f4c6a7da669  IDENTICAL
run_one_t9a.sh         163c4345199cc8f2cfa1eb9406fedb8c44d3ff9f4d037f6b0d07eb495f8f2761  IDENTICAL
run_chain_t9a.sh       cbf3b957f5cd7d7a18f799112ca7936b824c2e37532515447fca575634999e7d  IDENTICAL
--- case directories in the new tree ---
0
```

**AMENDMENT, made before any compute and with its condition checked, not
asserted (Charter §2b(1)): an EIGHTH frozen file was copied.**
`build_t9a.py`, sha256
`516fee581ecfaa25ffddefbb286de6b78c13b7bb9e9b635581958e4e9a2659e9`, verified
IDENTICAL to the blob at HEAD, copied at **2026-08-23T20:01:37.030Z** with the
tree holding **0** case directories at that moment (the command and its output
are in the commit that carries this addendum). **Why:** so that
`build_t9aH.py` **overrides** the frozen builder rather than re-deriving it —
re-deriving the mesh, fields and dictionaries would have made "the single change
is the interface scheme" a claim about a script instead of a measurement.
**It changes no gate, threshold, cap, band, reference or label**, and
`analyse_t9aH.py` hashes it with the other seven.

### A.2 Step 3 — the new files and their sha256, recorded before any case exists

| file | sha256 | what it is |
| --- | --- | --- |
| **`analyse_t9aH.py`** | **`8107ed38578fcade0196c6458cb2e8e0f3d1af620c1a4d2c1dd444cea97f2870`** | **the NEW instrument — rows H1–H6, controls HC1–HC4. Arms no band, quotes no GCI. §1's box applies: read it as source and as a diff before believing its output.** |
| **`build_t9aH.py`** | **`c7a742f298cbd6be95e2a5077afd3d66048c676c14503b2b6f84132d787104a4`** | NEW builder; imports the frozen `build_t9a` generators unmodified and changes only the scheme entry |
| `run_chain_t9aH.sh` | `77c580255e1337b90cdaae6cafa1df6e04d018f64d1e47255e577f9eac39aade` | NEW chain for the three extra cases; invokes the byte-identical `run_one_t9a.sh` |
| `T9aH_registered.json` | `2a5ee67c78ad572380b8eb2577b76b142868f3864ab07af9fd6966def30151b8` | the machine transcription of §4 |

**The two transcriptions.** Every threshold now exists twice: in
`T9aH_registered.json` and hard-coded in `analyse_t9aH.py`'s `REGH_CODE`. The
instrument compares them at every run and at every selftest and **refuses
rather than grades** on any disagreement — §1's rule that this document
governs, made executable. The selftest proves it by feeding a **widened** H1
threshold and confirming it is refused, not adopted.

### A.3 The selftest — 53 checks, 0 failed, and it caught three of my own errors

```
selftest: 53 checks passed, 0 failed        (exit 0)
```

Forged inputs only: **no case, no mesh, no OpenFOAM, no solver.** The three
checks the supervisor required are present and named in the output:

| required check | how it is forged | result |
| --- | --- | --- |
| **planted measurement-path error invisible → refusal** | a plant that moves `T_i1` by **0.0 K**, and one that moves it by 1e-09 K | refusal fires on both; a 1.18e-03 K shift is accepted |
| **HC4 null that MEETS H1 → empty-discrimination fires** | a forged null-arm error of 1e-12 K, and one meeting all three rows | HC4 NOT MET; the affected rows are marked **reported, not counted** |
| **fvSchemes readback mismatch → refusal** | a case whose `laplacian(DT,T)` reads `Gauss linear` where harmonic is registered, and one with **no** explicit entry | refusal fires on both; the null arm's own linear entry is accepted as linear |

Also exercised, each in **both** directions: the seven (now eight) frozen
hashes; the transcription cross-check and its widened-threshold mutation; the
exact references at all three contrasts through both frozen routes, with the
`WALL_LAYERS` and `REG` restorations asserted; H1 at the T9a-D residuals, at the
frozen linear residual, one level above the bar, and exactly at the bar; the
frozen `gci()` over EXACT / OSCILLATORY / STAGNANT / DIVERGENT / first-order /
second-order triples and over **T9a-D's own m/f/x triple, which still reads
STAGNANT**; the collapse floor firing on harmonic residuals and not on T9a's
linear errors; H4's two clauses including a corrupted-baseline case that fires
the drop clause alone; the replica refusal; the builder's guard refusing a case
that already holds a time directory; the round trip from what the builder writes
to what the instrument reads back; and `T9a_runs/gate_t9a.json` and
`gate_t9aD.json` still hashing what §6.1 registered.

> **Three checks FAILED on the first run, and all three were defects in my own
> forged fixtures, not in the frozen code. Recorded rather than tidied.**
> (1) A boundary case forged as `348.7810823988298 + 1.0e-08` does not carry an
> error of 1e-08 K — the nearest double sits **1.0000008e-08** away, above the
> bar — so the row correctly GATE FAILED and the *test* was wrong; the boundary
> is now forged where the error is exactly representable, and a second check
> covers 10× the bar on the 348 K field. (2) My "STAGNANT" triple had
> `e32/e21` = 0.05, i.e. `p` = −6.37, which the frozen classifier correctly
> called **DIVERGENT**. (3) My "DIVERGENT" triple had opposite-signed
> differences, which it correctly called **OSCILLATORY**. Each was diagnosed by
> an independent calculation before anything was edited. **The frozen classifier
> was right three times out of three and not one line of it moved.**

### A.4 Two things found while writing the instrument, disclosed now rather than at grading time

1. **H4's drop clause is not the binding one at the registered numbers.** A
   drop below 1e+06 requires `|e1|` > 6.5e-08 K, which already fails H4's
   1.0e-08 K absolute bar. **The absolute bar binds; the drop clause binds only
   if the baseline read from `gate_t9aD.json` is not the registered
   −64.99408 mK**, and it is therefore a cross-check on that read rather than an
   independent falsifier. §4.4's threshold is **unchanged** — this is a
   statement about which clause does the work, not a change to either. The
   selftest includes a corrupted-baseline case in which the drop clause fires on
   its own.
2. **The registered consequence of an unmet HC4, made explicit.** §4.5 registers
   that HC4 must fail; Charter §2c fixes what follows if it does not, and the
   instrument implements exactly that: **any row whose threshold the null arm
   also meets is REPORTED and NOT COUNTED toward the hypothesis.** This can only
   **remove** rows from the hypothesis's tally, never add one, and it changes no
   threshold.

### A.5 The freeze condition, RE-CHECKED after every new file was written

```
$ date -u +%FT%T.%3NZ; find .../T9aH_runs -mindepth 1 -maxdepth 1 -type d | wc -l; ls .../T9aH_runs/0
2026-08-23T20:02:53.680Z
0
ls: cannot access '.../T9aH_runs/0': No such file or directory
rc=2
```

**The tree holds no case directory, no `0/`, no time directory and no mesh at
the moment these hashes were taken and this addendum was written.** There is no
answer on disk to tune any threshold to, and it is demonstrated rather than
claimed — the artifact `T9aD_RESULTS.md` §A.3 identified as the thing that
carries the evidentiary weight when the git clock does not.

### A.6 What has NOT happened

- **`analyse_t9aH.py` has not been read by the supervisor yet** (§9 step 4).
  Until it has, **no H-row or HC-control output may be believed**, and none
  exists.
- **Nothing is built and nothing is run** (§9 step 5), and step 5 needs the
  supervisor's explicit authorisation.
- **No T9a file was written**, and `T9a_runs/gate_t9a.json` still hashes
  `7c4c6826…b3a5f4f8`, `gate_t9aD.json` `96e0dce0…0dc19993` — asserted by the
  selftest, twice.
- **No other lane's process was touched.**
