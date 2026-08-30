# T17 results — axisymmetric transient conduction in a finite cylinder (T11d), Robin surfaces, EXACT tier

**Document version 1.0.** Rung `T17`, pre-registration
`docs/campaigns/T-family/T17_PREREGISTRATION.md`, frozen at commit
**`b8ebddfef2f0d1c64450b8b93cf42709d485511f`** (2026-08-27T19:35:11Z). Run root
`verification/runs/T-family/T17_runs/`. Graded 2026-08-28T16:29:18Z by the frozen
`analyse_t17.py`. Drafted by a heat-transfer lane 2026-08-30.

**RUNG VERDICT: `PASS` — three of three graded rows `PASS`, all three triples
`CONVERGING`.**

**And the rung's registered ceiling is `GATE REACHED`, not higher.**
`T17_registered.json` `ceiling` reads *"GATE REACHED at best — the reference is
EXACT, so this rung scores V and never P; it can never reach HOLDS."* That was
registered before compute. **The three `PASS` rows are gate verdicts; they are
not a capability claim**, and nobody may read this record as one.

This record was written **two days after the verdict was produced**. The verdict
sat on disk from 2026-08-28T16:29:18Z and had never reached the campaign record;
nothing about it was re-derived here, and every figure below was re-read from the
artifacts it cites. Two figures in the brief this lane worked from did **not**
reproduce and are boarded in §10 rather than transcribed.

---

## 1. Freeze verification — six of six, agreeing FOUR ways

Each grading-path file was hashed on disk with `git hash-object`, compared
against `git rev-parse HEAD:<path>`, against the freeze blob recorded in the
pre-registration's own table at `T17_PREREGISTRATION.md:365-370`, and against
that table's registered sha256-first-16 and line count.

| file | git blob (worktree = `HEAD:`) | registered sha256₁₆ | lines | |
|---|---|---|---:|---|
| `analyse_t17.py` | `9a5a409adbd307bb35dde4da0926029586dbfb66` | `baa053900e58c2a5` | 646 | MATCH |
| `exact_t17.py` | `c07487e70909344accfc9ae6cb45bdb9143db99c` | `29c5e0975885b26f` | 380 | MATCH |
| `mark_done_t17.py` | `a9260b42ee997219017206bbeda638e5965dd3b1` | `adf2cbafd140804d` | 219 | MATCH |
| `build_t17.py` | `5b76ef3bfea248f0b68a8554f4978aebe24d1f5d` | `d321df6e682b0016` | 319 | MATCH |
| `run_one_t17.sh` | `9afde791a795b2bffa09e87ba3b56ce53eaadf11` | `adf7436a740a6e54` | 193 | MATCH |
| `T17_registered.json` | `542e55b5f903c49e866a5d523d2f168f65628ef2` | `b77fd3acbd72d7a2` | 161 | MATCH |

**6 of 6 MATCH on every one of the four channels.** The files that ran are the
files that were frozen, and the freeze commit is an ancestor of `HEAD`.
`git log b8ebddfe..HEAD -- <path>` returns **zero commits on every one of the six
instruments**, so nothing drifted and was then restored.

**The pre-registration's entire git history is ONE commit** — `b8ebddfe`,
2026-08-27T19:35:11Z. It was never modified, so no gate, band, threshold, cap or
label in it can have been moved after the fact.

**Pre-registration preceded compute by 6 h 50 min.** Freeze 2026-08-27T19:35:11Z;
first compute `STATUS.T17_CY_c` `started_utc=2026-08-28T02:25:17Z`. Rule 2 is met
by the clock, not by assertion. There is no registration-after-compute finding on
this rung.

---

## 2. Completion — rule 4, four of four

Four cases landed. All four carry `rc=0`, `capped=no`, `checkmesh_rc=0`,
`note=clean` in their wrapper-written `STATUS.*`, and all four carry
`DONE.T17_CY_*` written by the rung's own registered marker `mark_done_t17.py`.
The `Time` and `ExecutionTime` counts equal `endTime/deltaT` on every level
(20 000 / 20 000 / 20 000 / 40 000) and the fields at time `2` are present.

| case | level | N | cells | steps | wall s | started → ended (UTC) |
|---|---|---:|---:|---:|---:|---|
| `T17_CY_c` | c | 50 | 2 500 | 20 000 | 14 | 02:25:17 → 02:25:31 |
| `T17_CY_m` | m | 100 | 10 000 | 20 000 | 55 | 16:15:56 → 16:16:51 |
| `T17_CY_f` | f | 200 | 40 000 | 20 000 | 281 | 16:17:01 → 16:21:42 |
| `T17_CY_f_CT` | f_CT | 200 | 40 000 | 40 000 | 531 | 16:18:06 → 16:26:57 |

The comparator refuses to grade a partial rung: `analyse_t17.py:327-328` —
*"no `DONE.<case>` — the whole rung is graded or none of it is; `mark_done_t17.py`
rules"*. It did not have to fire.

**Gate (1) passed on all three graded levels.** `gate_t17.json` `gate1.ok = true`,
worst final linear residual 9.965e-13 / 9.943e-13 / 9.994e-13 against the PCG/DIC
tolerance 1e-12, and `W0 = 0.0` on every level. No row was stopped by rule 5
order (1).

---

## 3. THE THREE GRADED ROWS — all `PASS`

Triple is (c, m, f) at N = 50 / 100 / 200, refinement ratio **r = 2 exact**,
`dim = 2`, `Fs = 1.25`. All three triples are **strictly monotone decreasing** and
**`CONVERGING`**. The **fine value is the graded value** on every row; the
Richardson extrapolate is reported beside it and is gated on never
(`T17_registered.json` `cases.T17_CY_f.role`).

| row | c | m | f | triple | observed p | GCI | verdict |
|---|---:|---:|---:|---|---:|---:|---|
| **G1** | 0.611903421 | 0.611886048 | 0.611881704 | **CONVERGING** | 1.9999 | 2.96e-04 % | **`PASS`** |
| **G2** | 0.827285020 | 0.827224973 | 0.827212468 | **CONVERGING** | 2.2636 | 4.97e-04 % | **`PASS`** |
| **G3** | 0.542195585 | 0.542109598 | 0.542088237 | **CONVERGING** | 2.0091 | 1.63e-03 % | **`PASS`** |

Bands and where the fine value sits inside them — bands registered at
`T17_PREREGISTRATION.md:191` and in `T17_registered.json` `graded_rows.*.band_rel`,
band edges re-derived here as `reference × (1 ∓ band_rel)`:

| row | reference | band_rel | band | fine value | margin to NEAREST edge |
|---|---:|---:|---|---:|---:|
| **G1** | 0.6118851822 | 5e-05 | [0.611854588, 0.611915776] | 0.611881704 | **2.712e-05** (lower) |
| **G2** | 0.8272239909 | 3e-05 | [0.827199174, 0.827248808] | 0.827212468 | **1.329e-05** (lower) |
| **G3** | 0.5420823169 | 4e-05 | [0.542060634, 0.542104000] | 0.542088237 | **1.576e-05** (upper) |

Observed orders 1.9999 / 2.2636 / 2.0091 against the second-order scheme the
registration expects — G1's 1.9999 is the cleanest available evidence that the
grid family is behaving as designed.

---

## 4. WHY THESE `PASS`ES ARE BELIEVABLE — the substance

A `PASS` inside a band is worth exactly what the reader that produced it is
worth. Five independent facts stand behind these three.

### 4.1 The planted-zero control has a MEASURED zero, not an assumed one

Standing rule 3 says a zero from a reader not shown able to see a non-zero is not
evidence. **T17's control establishes its own visibility threshold at ZERO, and
measures it.** `analyse_t17.py:242-246` re-runs the reader on **identical bytes**
and refuses outright if the two reads differ:

> `refuse("planted-zero control NEGATIVE ARM FAILED: %.17g on identical bytes -- the reader is NOISY" % dneg)`

The measured negative arm is **exactly `0.0` on all three rows**
(`gate_t17.json` `planted_zero_controls.*.negative_arm`). Only after that is
`d > 0.0` used as signal at `:262-265`. **This is the construction T3's defective
control lacked**: the reader's own noise floor is not assumed to be zero, it is
demonstrated to be zero on the same data, and a noisy reader is refused rather
than tolerated.

The single sizing tolerance, at `:270`, is **relative** — `0.1 × PLANT` =
1.234e-04 — and `d` is an `abs()`, so the **sign** of any drift cannot decide the
control. Measured margins against that tolerance:

| row | plant | cells planted | recovered | margin vs 0.1×PLANT |
|---|---:|---:|---:|---:|
| G1 | 1.234e-03 | 40 000 | 1.234000e-03 | **10.00×** |
| G2 | 1.234e-03 | 1 | 3.239250e-03 | **26.25×** |
| G3 | 1.234e-03 | 1 | 2.775729e-03 | **22.49×** |

### 4.2 An eight-magnitude ladder, linear over seven decades

Each control drives the plant through eight magnitudes, 1 down to 1e-07, and
records the response (`gate_t17.json` `planted_zero_controls.*.ladder`). Every
row is linear across the whole ladder to twelve significant figures, and the
**demonstrated detection floor is 1e-07** on all three. **The registered plant of
1.234e-03 therefore sits four decades above the floor the control proved it can
see** — the reach was not asserted, it was measured, and measured with four
decades of headroom.

### 4.3 The two amplification factors were independently re-derived

G2 and G3 read a single planted cell through a separable linear extrapolation, so
the recovered value is the plant times a product of interpolation weights. Those
weights are a property of the registered stations, not of the answer, so they can
be predicted from the geometry alone:

| row | predicted from weights | observed (ladder at plant = 1) | relative agreement |
|---|---:|---:|---:|
| G2 | 1.500000000 × 1.750000000 = **2.625000000** | 2.6250000000000009 | **3.4e-16** |
| G3 | 1.500000000 × 1.499583340 = **2.249375010** | 2.2493750105191257 | **2.3e-10** |

**A coin flip does not produce an analytically predicted linear response across
seven decades on two rows at once.** This is the strongest single item in the
record: the control is not merely *responsive*, its response has the numerical
value the geometry says it must have.

### 4.4 The gate was proved able to fail

Two mutation limbs establish that the instrument can return something other than
`PASS`. A **BLIND-reader mutant** drives the planted-zero control and the control
refuses, as `analyse_t17.py:611` records; and mutating the registered `P_MIN` to
0.5 fires the floor-disagreement refusal at `:62-65`. A gate that has never been
shown able to fail is not a gate.

### 4.5 The Roache floors are IMPORTED, not redefined, and disagreement is refused

`analyse_t17.py:42` imports `STAGNANT_FLOOR`, `P_MIN`, `FS`, `gci_equal` and
`PLANT` from `scripts/roache_triple.py`. **No local floor definition exists in the
comparator.** `:62-65` then refuses if the floors carried in `T17_registered.json`
disagree with the imported ones — *"one name, one number"*. The registered pair in
`gate_t17.json` `floors` reads `STAGNANT_FLOOR 0.5`, `P_MIN 0.05`,
`source: scripts/roache_triple.py (imported)`.

---

## 5. THE BANDS WERE DEMONSTRABLY NOT FITTED TO THE ANSWER — and prediction P5 did not cleanly win

This is reported honestly because the honest version is the stronger evidence.

Prediction **P5** (`T17_PREREGISTRATION.md:302-309`) committed in advance that
**every** fine-level deviation would be **negative**, from a `sec²(h)` wedge-bias
derivation: G1 near −2.2e-05, G2 near −5.9e-06, G3 near −1.28e-05. Measured:

| row | predicted fine deviation | measured fine deviation | |
|---|---:|---:|---|
| G1 | −2.200e-05 | **−5.684e-06** | right sign, 0.26× the magnitude |
| G2 | −5.900e-06 | **−1.393e-05** | right sign, 2.36× the magnitude |
| G3 | −1.280e-05 | **+1.092e-05** | **SIGN-FLIPPED against the prediction** |

**G3 came out with the opposite sign to what the registration predicted, and the
row still `PASS`es.** That is only possible because the bands were sized before
compute to contain *both* outcomes, which the pre-registration states in those
words — *"the bands were sized to contain both outcomes"* — and backs with a
**P5-LOSES CONTROL** in the comparator's selftest that drives the no-wedge-bias
field through the whole grade and requires `PASS` ×3, *"so the gate cannot become
a test of P5"*.

**A prediction that did not cleanly win is evidence the gate was not
reverse-engineered.** Had the bands been chosen after seeing the answer, G3's
sign flip is the last thing they would have been built to tolerate.

---

## 6. `f_CT` is a temporal-bias control — REPORTED, never gated, and correctly excluded from the triple

`T17_CY_f_CT` is the same mesh as `f` (N = 200, 40 000 cells) with `deltaT`
halved, 1.0e-4 → 5.0e-5, running 40 000 steps instead of 20 000. Its registered
role is **"C-T temporal-bias control, REPORTED never gated"**
(`T17_registered.json` `cases.T17_CY_f_CT.role`).

**It is not in the Roache triple and must not be**: a triple is a *spatial*
refinement family at fixed r, and `f_CT` refines in time at constant N. Including
it would have produced a number with no defensible order. `gate_t17.json` `C_T`
reports it beside the grade: `G1_fine` 0.6118817042, `G1_ct` 0.6118799262, a move
of **−2.906e-06 relative — 5.8 % of the G1 band**. Temporal discretisation is
therefore a small fraction of the band, reported and gated on nothing.

The reader's separability defect is likewise **reported only**:
1.184e-07 / 1.182e-07 / 1.183e-07 across c/m/f
(`gate_t17.json` `separability_defect_REPORTED_ONLY`).

---

## 7. DISCLOSURE 1 — `analyse_t17.py --selftest` FAILS TODAY, exit 1

**Stated at the top of the disclosures because anything gating on "the
comparator's selftest passes" currently fails for T17.**

`T17_PREREGISTRATION.md:285` records `analyse_t17.py` as **"PASS (0 failed)"**.
**That was true at the freeze and is NOT reproducible today.** The selftest exits
**1**, reported by the adversarial re-verification of 2026-08-30 (this lane did
not re-run the comparator; §11).

**The failing limb, and it is one limb.** `analyse_t17.py:615-621`:

```
    try:
        grade(HERE, os.path.join(tempfile.gettempdir(), "t17_never.json"), reg)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] live tree, no DONE markers -> exit 2 REFUSE" % ("ok " if fired else "FAIL"))
```

The limb grades the **live run tree** and asserts it is refused for want of DONE
markers. **The `DONE.T17_CY_*` markers now exist**, so `grade()` proceeds instead
of refusing and the limb reports FAIL.

**It is SELF-CONSUMING, and the clock says so exactly.** The four DONE markers
were written at **2026-08-28T16:28:47Z**; `gate_t17.json` and
`T17_GRADE_OUTPUT.txt` were written at **2026-08-28T16:29:18Z**. **The limb has
been failing since 31 seconds BEFORE the graded artifact existed.** The runs
completing is what falsified it.

**This is NOT a gate defect, on four measured grounds:**

1. **Every physics limb passes.** The failure is the one limb that asserts a
   property of the *filesystem*, not of the numerics.
2. **The limb cannot have touched the verdict.** It writes only to
   `tempfile.gettempdir()/t17_never.json`. It did not write, and could not have
   written, `gate_t17.json`.
3. **The grade reproduces byte-for-byte.** `gate_t17.json` is **6 126 bytes**
   (confirmed on disk by this lane) and reproduced identically across three
   independent runs in the re-verification.
4. The freeze identity of the comparator is intact six ways over (§1), so the
   file that fails today is the file that graded.

**It is the seventh instrument in a family sharing one defect** — a selftest limb
asserting the live run tree is still empty, true when written and falsified by
the runs completing. This lane measured the family's extent directly rather than
accepting a list (see §10 for where that measurement diverged from the brief):
**nine T-family comparators carry the limb, and eight of the nine are already
falsified.**

| comparator | DONE markers on disk | limb status |
|---|---:|---|
| `analyse_t13.py` | 3 | FALSIFIED |
| `analyse_t14.py` | 4 | FALSIFIED |
| `analyse_t15.py` | 1 | FALSIFIED |
| `analyse_t16.py` | 2 | FALSIFIED |
| **`analyse_t17.py`** | **4** | **FALSIFIED** |
| `analyse_t18.py` | 1 | FALSIFIED |
| `analyse_t9aR1b.py` | 3 | FALSIFIED |
| `analyse_t9aR1c.py` | 3 | FALSIFIED |
| `analyse_t19.py` | 0 | still true — **only because T19 has not run** |

**T19 is the control that proves the diagnosis.** Its limb still passes, and the
only thing distinguishing it is that no run has landed. The moment T19's first
case completes, its selftest joins the other eight. **A limb whose truth is
destroyed by the success of the campaign it guards is mis-designed as a limb**,
whatever it was worth as a one-time check.

**NOT REPAIRED HERE.** `analyse_t17.py` is frozen at `b8ebddfe` and rule 6
forbids editing it; a measurement-script change is additionally read as a diff by
the supervisor personally (`SUPERVISION_CHARTER` §3 check 1) and that check is not
delegable. This lane changed no frozen file and proposed no patch.

---

## 8. DISCLOSURE 2 — the planted control ran on the FINE LEVEL ONLY

`analyse_t17.py:384` passes **`dirs["f"]`** to `planted_zero_control`. **Levels
`c` and `m` were never blindness-tested.** `read_field` is N-parameterised, so an
N-specific indexing fault on the coarse or medium level would not have been
caught by any control in this rung.

**This bounds the grade; it does not invalidate it.** Two things limit the
exposure, and both are measured:

- **The graded value on every row is the FINE level's**, which is the level the
  control did cover. `c` and `m` enter only through the triple state and the
  observed order.
- **Unlike the T18 trap, T17's control demonstrably executed on REAL data.** It
  `copytree`s the real case and plants into the copy's `2/T`, then reads it back
  from disk — the 40 000 cells planted on G1 are the fine case's own cells, not a
  synthetic fixture.

**What the shape still costs:** an indexing fault confined to `c` or `m` would
corrupt the triple — and therefore `p`, the `CONVERGING` state, and the GCI —
without any control firing. The observed orders 1.9999 / 2.2636 / 2.0091 sitting
where second-order theory puts them is *consistent with* no such fault, and it is
not a substitute for the control that was not run. **Stated as a bound, not
waved away.**

---

## 9. Cost — rule 12, and it is ALREADY DISCHARGED

**No new calibration row is minted by this document.** The rule-12 comparison for
this rung landed as **`C-200`** at `docs/COST_CALIBRATION.md:283` on 2026-08-28
(heat-transfer, *"T17_CY … COMPLETE FOUR-LEVEL RUNG, GRADED"*), confirmed present
at that line by this lane. Writing a second row would re-mint exactly the
`C-179`/`C-170` duplication this team withdrew via `C-180` on 2026-08-27. The
figures are reproduced here for the reader, not re-derived and not re-filed.

| | |
|---|---|
| **predicted** | POINT **7.244** core-min (`T17_registered.json` `cost.point_total_core_min`) |
| **actual, MEASURED** | **14.683** core-min, basis **gross**, from the four `STATUS.*` as `wall_s × ranks ÷ 60` at ranks = 1 |
| **ratio actual/predicted** | **2.027×** |
| gross vs cleaned | **gross == cleaned.** Longest wall is `f_CT` at 531 s — **14.8 %** of the 3 600-s stall convention, so the rule matches no row |
| **WASTE** | **0.000 core-min**, named separately per `COMPUTE_BUDGET_CHARTER` §6 and folded into neither column nor the ratio. No level capped (`capped=no` ×4), none killed, re-run or discarded |
| caps | per-level **2 / 8 / 30 / 60** core-min; total use **14.7 %** of the 100 core-min rung cap; worst per-level **15.6 %** (`f`) |
| dollars | $0.006194 predicted, **$0.012554** actual — **DERIVED, NOT MEASURED**, at the owner-stated $0.0513/core-h (`COMPUTE_BUDGET_CHARTER` §5: the box cannot read its own billing) |

Per level, and the ratios are strikingly uniform:

| level | POINT core-min | actual core-min | ratio |
|---|---:|---:|---:|
| c | 0.137 | 0.233 | **1.701** |
| m | 0.547 | 0.917 | **1.676** |
| f | 2.187 | 4.683 | **2.141** |
| f_CT | 4.373 | 8.850 | **2.024** |

**Attribution: misprediction of a BORROWED rate, and the coarse level rules
contention out by itself.** The registered rate 1.64e-07 core-s per cell-step is
T14's, measured on a scratch copy of `T14_SQ_c` and declared borrowed in
`cost.rate_provenance`. **`T17_CY_c` ran ALONE** — 02:25:17Z to 02:25:31Z,
**13 h 50 min before any other T17 case started** (`m` began 16:15:56Z) — and it
still came in at **1.701×**. **A ~1.7× underprediction on an uncontended box is
not contention; it is the borrowed rate being wrong for this solver on this mesh
topology.**

**Contention IS present at the fine levels, and it is bounded rather than
assumed.** `f` ran 16:17:01–16:21:42Z and `f_CT` ran 16:18:06–16:26:57Z, so they
**overlapped for 216 s of `f`'s 281 s wall — 76.9 %**, beside foreign solvers.
That plausibly covers the extra 0.3–0.44× separating the fine levels' 2.02–2.14×
from the coarse level's uncontended 1.70×. `C-200` carries the full attribution
and the two dead hypotheses it had to kill first; it is not restated here.

---

## 10. Spot-check reconciliation — what did NOT reproduce

Every figure in this document was re-read from its artifact before being written.
**Two items in the brief this lane worked from did not reproduce, and the
measured values are used above rather than the transcribed ones.**

1. **The G3 amplification agreement is TIGHTER than reported, not looser.** The
   brief gave observed 2.249375000 against predicted 2.249375011, "match to
   1.1e-8". The value in `gate_t17.json`
   `planted_zero_controls.G3.ladder["1"]` is **2.2493750105191257**, and
   `recovered / PLANT` gives **2.2493750105190351**. Against the weight product
   1.500000000 × 1.499583340 = 2.249375010 the relative agreement is **2.3e-10**,
   about 50× better than stated. The brief's "observed" figure appears to be a
   truncation. **The conclusion is unaffected and strengthened.**

2. **The named membership of the self-consuming-selftest family did not
   reproduce.** The brief named *"a family of six already boarded (T13, T14,
   T9aR1b, T9aR1c, T5b, T8)"*. Measured over
   `verification/runs/T-family/*/analyse_*.py`: **`analyse_t5b.py` and
   `analyse_t8.py` carry NEITHER the `live tree` limb NOR any `no DONE` selftest
   string** — they are not members on this criterion. Three comparators the brief
   did not name — **`analyse_t15.py`, `analyse_t16.py`, `analyse_t18.py`** — do
   carry it, as does **`analyse_t19.py`**. The measured set is **nine
   comparators, eight already falsified**, tabulated in §7. **T17 is a member;
   the family it belongs to is larger and differently composed than reported.**
   Whether T5b and T8 were boarded under a *different* self-consuming defect is
   not established here and is not claimed either way.

Everything else reproduced exactly: all six freeze hashes on all four channels;
`C-200` present at `docs/COST_CALIBRATION.md:283`; the three band edge pairs
re-derived from `T17_registered.json` `reference × (1 ∓ band_rel)`; the three
nearest-edge margins; `gate_t17.json` at **6 126 bytes**; the planted-control
margins 10.00× / 26.25× / 22.49×; the G2 amplification 2.625000000; the freeze
commit as an ancestor of `HEAD` with a one-commit pre-registration history and
zero post-freeze commits on any instrument; the 6 h 50 min freeze-to-compute gap;
and the 216 s / 76.9 % `f`–`f_CT` overlap.

---

## 11. Disclosures

- **The rung verdict is `PASS`; the rung's registered ceiling is `GATE REACHED`.**
  Those are different words for different facts and neither substitutes for the
  other. This rung scores V and can never reach HOLDS, by its own registration.
- **`analyse_t17.py --selftest` fails today, exit 1** (§7). Anything gating on
  "the comparator's selftest passes" currently fails for T17. The failure is one
  self-consuming filesystem limb, it wrote nothing the verdict rests on, and the
  grade reproduces byte-for-byte.
- **The planted-zero control covered the fine level only** (§8). Levels `c` and
  `m` were never blindness-tested. This bounds the grade.
- **Prediction P5 was not a clean win** (§5). G3's fine deviation is sign-flipped
  against the registration's prediction, and the row `PASS`es because the bands
  were pre-registered to contain both outcomes.
- **The comparator was NOT re-run by this lane.** The selftest exit code and the
  three-run byte-for-byte determinism finding are carried from the adversarial
  re-verification of 2026-08-30 and are attributed, not claimed as this lane's
  measurement. Everything read here was read from artifacts already on disk.
- **No frozen file was edited** (rule 6); no comparator or marker was patched; no
  solver was launched; nothing was placed in `verification/queue/`.
- **No calibration row was minted** (§9); `C-200` already discharges rule 12 for
  this rung.
- **Nothing was sent, filed, uploaded, posted, registered or commented outside
  this box** (rule 7).
