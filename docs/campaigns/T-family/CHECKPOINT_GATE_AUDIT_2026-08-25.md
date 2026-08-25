# Checkpoint-difference convergence gates — territory audit (2026-08-25)

**Owed by the supervisor's ruling on T8 draft §4b.1.** Scope:
`verification/runs/T-family/`, `verification/runs/F14-cooling-ladder/`,
`verification/runs/THERMAL_K0_runs/`.

**Nothing here re-grades anything and no frozen file was touched.** This is a
census of instruments, read from the code, with line citations.

---

## 0. The three criteria being audited

A convergence gate built on differences between written checkpoints must:

1. use **at least three distinct checkpoint spacings** and pass at all of them;
2. require successive differences to be **non-increasing**, not merely small;
3. **REFUSE (`NOT A RESULT`)** when the quantity is not shown **stationary**.

**Mechanism:** a last-two-checkpoints gate is a **two-point sample** and on an
oscillating quantity it **aliases** — if the two checkpoints land at similar
phases the difference is small, the gate reports converged, and **nothing in
the output signals anything went wrong.**

---

## 1. THE HEADLINE, and it is not the one I expected

**Not one gate in the territory uses more than ONE spacing. Not one requires
non-increasing differences.** On criteria 1 and 2 the territory is **uniformly
non-compliant**.

**But the exposure is NOT uniform**, and lumping these together would be wrong.
There are **three architectures**, and two of them are already largely immune:

| class | architecture | exposure |
|---|---|---|
| **A — tolerance on one spacing** | `rel = dmax/range ≤ 1e-6` between `ts[-2]` and `ts[-1]` | **EXPOSED** — this is the aliasing case exactly |
| **B — EXACT equality on one spacing** | requires `dmax == 0.0` or bit-identical checkpoints | **structurally exposed, practically immune** |
| **C — windowed series statistics** | spread/trend over a registered window of many samples | **NOT a two-point sample; largely compliant** |

---

## 2. CLASS A — the exposed gates (tolerance, one spacing)

| comparator | gate | line | tol | spacings | non-incr | stationarity |
|---|---|---:|---|---:|---|---|
| `T1_runs/analyse_t1c.py` | `iterative_convergence` | **197** | `1e-6` | **1** | **NO** | **NO** |
| `T3_runs/analyse_t3.py` | `iterative_convergence_vector` | **263** | `1e-6` | **1** | **NO** | **NO** |
| `T9a_runs/analyse_t9a.py` | `iterative_convergence` | **191** | `1e-6` | **1** | **NO** | **NO** |
| `T9aH_runs/analyse_t9a.py` | `iterative_convergence` | **191** | `1e-6` | **1** | **NO** | **NO** |
| `T9aH_runs/analyse_t9aH.py` | (inherits) | — | `1e-6` | **1** | **NO** | **NO** |
| `T8_runs/analyse_t8.py` | `check_iterative_convergence` | **506** | `1e-6` | **1** | **NO** | **NO** |

**And five more rungs inherit `analyse_t1c.iterative_convergence` by import**,
so they carry the identical gate without a line of their own:
`T1_runs/analyse_t1b.py` (call site **line 149**, `T1C.iterative_convergence(d)`),
`analyse_t1b_L4.py`, `analyse_dts.py`, `analyse_dts_p.py`, `analyse_pesweep.py`.

**That is eleven comparators on one gate design.**

## 3. CLASS B — exact-equality gates, structurally exposed but practically immune

| comparator | gate | line | requirement |
|---|---|---:|---|
| `T10a_runs/analyse_t10a.py` | `iterative_convergence` | **361**, test at **372** | `dmax == 0.0` — **exactly zero change** |
| `E4_runs/analyse_e4a.py` | `converged` | **411**, test at **416** | `field_signature(a) != field_signature(b)` — **bit-identical checkpoints** |

**These still use one spacing and no non-increasing test, so they fail criteria
1 and 2 on their face.** But an oscillating field will essentially **never**
produce two bit-identical checkpoints, so the aliasing mechanism has almost no
purchase: the gate's failure mode is to refuse a converged run, not to pass an
oscillating one. **That is the safe direction.**

**Recorded honestly, not waved through:** "almost never" is a probabilistic
argument, not a proof, and neither gate would *notice* if it happened.

## 4. CLASS C — windowed series gates, and THE LAB ALREADY HAS THE FIX

**This is the constructive finding: two comparators in this territory already
do substantially what the ruling requires.** The repair for Class A is to adopt
their shape, not to invent one.

**`E4a2_runs/analyse_e4a2.py:300` `gate_converged`** — the closest thing to
compliant in the territory. Its own docstring: *"C1 sustained floor AND C2 not
growing AND C3 graded-quantity stationarity."*

- **C1** — floor sustained over the **last `SUSTAIN` intervals**, not one.
- **C2** — a **trend fit** over a window, rejecting a *growing* series. This is
  the non-increasing criterion in substance.
- **C3** — **explicit stationarity of the graded quantity.** The only gate in
  the territory that uses the word.

**`K0cX_runs/analyse_k0cx.py:644` `convergence`** — peak-to-peak spread over a
registered **400-iteration window sampled every 50**, and it **REFUSES** when
fewer than nine samples are available, in terms: *"The criterion is not loosened
to fit the data available."* Its docstring says explicitly *"not residuals, not
an endpoint difference"*.

Also series-based, not audited in detail here: `K0cS_runs/analyse_k0cs.py:403`,
`K0cT_runs/analyse_k0ct.py:609`, `K2b_runs/analyse_k2bU.py:18` (`steady_series`).

## 5. RUNGS ALREADY GRADED UNDER A CLASS-A GATE — the exposed verdicts

**Reported separately and prominently, as ruled.** These are the rungs where a
verdict may rest on a two-point sample:

| rung | comparator | gate class | RESULTS file exists |
|---|---|---|---|
| **T1b** | `analyse_t1b.py` → `T1C.iterative_convergence` | **A** | `T1b_RESULTS.md` |
| **T1c** | `analyse_t1c.py` | **A** | `T1c_RESULTS.md` |
| **T9a** | `analyse_t9a.py` | **A** | `T9a_RESULTS.md` |
| **T9aH** | `analyse_t9aH.py` | **A** | `T9aH_RESULTS.md` |
| **T9aD** | `analyse_t9aD.py` | **A** (inherits) | `T9aD_RESULTS.md` |
| **T3** | `analyse_t3.py` | **A** | `T3_RESULTS.md` — carries `NOT A RESULT`; a rung already refused is **not** at risk from a falsely-lenient gate |
| T10a | `analyse_t10a.py` | **B** (exact) | `T10a_RESULTS.md` |
| T10aR | `analyse_t10aR.py` | B/C — not resolved here | `T10aR_RESULTS.md` |
| E4a | `analyse_e4a.py` | **B** (bit-identical) | `E4a_RESULTS.md` |
| E4a2 | `analyse_e4a2.py` | **C** (windowed) | `E4a2_RESULTS.md` |

**The direction of the risk, stated precisely.** A falsely-lenient convergence
gate reports `CONVERGED` for a level that is not. Standing rule 5 order (1) then
**fails to fire**, and a row that should have been `NOT A RESULT` is instead
graded — becoming `PASS` or `GATE FAIL`. **So both PASS and GATE FAIL rows on a
Class-A rung are affected**, not only the passes. A `PASS` is the more damaging
outcome; a `GATE FAIL` is a wrong label in a less dangerous direction.

**T8 is the demonstration and is already `BLOCKED`** — its level `f` met the
registered `1e-6` for exactly 228 consecutive iterations and never again.

## 6. What this audit did NOT establish

- **It is not a census of graded ROWS.** I counted verdict *words* in the
  RESULTS prose, which mixes narrative uses with table cells. **I therefore give
  no row counts**, only which rungs carry a RESULTS file and which gate class
  graded them. Anyone acting on this must count rows from the tables themselves.
- **It does not show that any specific verdict is wrong.** It shows which
  verdicts rest on an instrument that **cannot distinguish convergence from
  aliasing**. Whether any actually aliased requires re-reading each rung's
  checkpoints, which **was not done and would be re-grading**.
- **`T10aR` was not resolved** into a class; its gate needs a closer read than
  this sweep gave it.
- **`THERMAL_K0_runs/analyse.py`** carries no convergence-function signature
  this sweep recognised. That is a **negative result from a pattern match**, not
  a positive finding that it has no gate — it needs a direct read.

## 7. Recommendation this lane offers, and does not decide

**The cheapest compliant repair for Class A is to adopt Class C's shape, which
already exists in this territory and is already registered and frozen
elsewhere** — `E4a2`'s sustained-floor + not-growing + stationarity triad, or
`K0cX`'s windowed spread with a registered minimum sample count and a refusal.

**Criterion 1 is nearly free where checkpoints already exist**: a rung writing
10 checkpoints can be tested at spacings `Δ`, `2Δ`, `3Δ` **with no new compute
at all** — the files are already on disk.

**What follows is the supervisor's to rule.**

---

# AMENDMENT A — 2026-08-25. **The aliasing alarm is WITHDRAWN. No rung is shown harmed. Status: `UNJUDGED`.**

**Appended, not edited. §1–§7 above stand as written except where this
amendment says otherwise.**

## A.1 What was withdrawn, and by whom

The supervisor ran the Δ/2Δ/3Δ test and it **first printed `ALIASED` against
nine cases including T1b's graded `_f` arms. Both defects were in the test, not
the rungs**, and the supervisor withdrew it:

- **the checkpoints are not evenly spaced**, so the "2Δ" comparison spanned a
  gap that is not 2Δ at all;
- the duplicate check **md5'd whole files** while the gate reads only
  `internalField`, so a differing `location "58000"` header read as differing
  data.

## A.2 Independently re-verified by this lane, through the comparators' own reader

Driven through `analyse_t1c.read_internal` — the reader the gate itself uses —
with `dmax` and `rng` reported **separately** so the `rng == 0` fallback cannot
hide inside `rel`:

| case | checkpoints compared | `dmax` | `rng` | `rel` |
|---|---|---|---|---|
| `R_100k_f` | 56000 → 58000 | **0.000e+00** | 1.089e-01 | 0.000e+00 |
| `R_300k_f` | 66000 → 68000 | **0.000e+00** | 4.055e-02 | 0.000e+00 |
| `R_30k_f` | 38000 → 40000 | **0.000e+00** | 3.220e-01 | 0.000e+00 |
| `R_10k_f` | 18000 → 20000 | 1.821e-07 | 8.699e-01 | 2.093e-07 |

**`rng > 0` in every case — the `rng == 0` fallback did NOT fire anywhere.** The
fields are **genuinely identical** between the last two checkpoints on three of
the four `_f` arms.

> **That is the strongest convergence evidence available, not the weakest.
> There is NO positive evidence of aliasing anywhere in the territory.**

**Spacing, confirmed:** `R_100k_f` holds `0, 18000, 20000, 56000, 58000` — gaps
of **2,000 / 36,000 / 2,000**. `R_300k_f` and `R_30k_f` have the same shape.
`purgeWrite` and run extensions leave a hole. **Among the non-zero checkpoints,
only `R_10k_x` (18000, 20000, 22000, 24000) is uniformly spaced**; every other
case either has two checkpoints only or a hole.

## A.3 The correct status is `UNJUDGED` — not clean, not exposed

**§1's structural finding stands untouched: the Class A design cannot
distinguish convergence from aliasing.** But **structural exposure is not
demonstrated harm.**

**§5 must not be read as showing that five graded rungs are wrong. They were
not shown to be wrong, and the evidence available points the other way.**

| | |
|---|---|
| **Class A design** | **structurally incapable** of separating convergence from aliasing — unchanged |
| **T1b, T1c, T9a, T9aH, T9aD** | **`UNJUDGED`** — not shown clean, not shown exposed |
| **Positive evidence of aliasing** | **NONE, anywhere in the territory** |

**With the demonstration withdrawn, §6's caution is now the whole of the
claim.** The audit counted **verdict words in prose, not rows**; it gives **no
row counts**; and it shows **no specific verdict is wrong** — only which rest on
an instrument that cannot tell convergence from aliasing.

## A.4 "Criterion 1 is nearly free" — WITHDRAWN, and it was mine

§7 of this audit said the Δ/2Δ/3Δ test costs no compute because the checkpoints
already exist. **That was wrong**, and the error is this lane's as much as the
supervisor's: it requires **uniformly spaced** checkpoints, and on this corpus
**most cases do not have them.**

> **On the territory as it sits, the Δ/2Δ/3Δ test is mostly UNRUNNABLE.**

## A.5 `THERMAL_K0_runs/analyse.py` — RESOLVED

Read directly by the supervisor. **241 lines. No convergence gate, and it emits
no verdict vocabulary at all** — not one of `PASS`/`GATE REACHED`/`GATE FAIL`/
`NOT A RESULT`/`BLOCKED`/`PENDING`. It reports physics measurements and residual
histories, using `latest_time()` to pick a directory.

**It is a measurement and reporting script, not a grader, so it is out of scope
for the A/B/C taxonomy.** §6's negative pattern match was right in substance.

**One property worth carrying, and it is not a defect in the script:** it
reports **residual histories with no gate**, so any convergence judgement on K0
is made by **a human reading a residual summary** — which is **the point-sample
failure in human form.**

## A.6 Still open

**`T10aR` is NOT resolved into a class.** It needs a closer read than this sweep
gave it, and it is stated here plainly rather than left to be inferred from
silence.
