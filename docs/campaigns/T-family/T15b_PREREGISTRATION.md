# T15b — successor to T15: a normalised-dispersion negative control with a real two-sided margin, and T15's four ungraded rows re-registered

> **STATUS: FROZEN BY COMMIT. NOT ENQUEUED.**
> This document is frozen by the commit that first lands it, per standing rule 2:
> the gate, threshold, cap and label are committed BEFORE any compute. **It is
> deliberately NOT enqueued** — dropping T15b into the run/re-grade queue is the
> heat-transfer supervisor's decision and is explicitly withheld from the lane
> that wrote this. Nothing here is sent anywhere (rule 7).
>
> **OPENING DISCLOSURE, REQUIRED BEFORE ANY READER GOES FURTHER — THE GRADED
> VALUE OF ROW S1 WAS ALREADY KNOWN WHEN THIS DOCUMENT WAS DRAFTED.**
> **`S1 = 1.9909386169553251e-04`.** It was computed on `T15_UP_f` because
> diagnosing the `analyse_t15.py:501` defect is impossible without computing the
> very quantity `ref` that the defective guard is written in terms of — `ref`
> **is** S1. It lies inside the frozen band `[0, 0.020]`, which was frozen on
> 2026-08-26 in `T15_PREREGISTRATION.md`, **before** the run that produced it.
> **T15b therefore MAY NOT BE PRESENTED AS A BLIND RE-GRADE OF S1**, and the
> band's freeze provenance must be cited from T15's commit, never from this
> document. This disclosure is repeated in §5 where the band is tabled; it is
> placed here because a reader who stops at the abstract must still meet it.
>
> **THE BIRTH REQUIREMENT (Sanaa, 2026-08-28) BINDS EVERY CONTROL ARM IN §4.**
> Verbatim: *"A control defined in terms of the thing it controls is not a
> control. A planted control must travel the real production path — written by
> the real producer's code, read through the real reader — and prove the
> instrument sees a non-zero the same way reality would deliver one. A control
> that empties the tuple it tests, or writes a schema the producer never emits,
> tests nothing and certifies blindness."* Companion rule: *"no instrument
> grades anything until that answer is yes, demonstrated."* This requirement did
> not exist when §4 was drafted. **§9 is the section that discharges it and it
> is binding on T15b's comparator: no row of T15b is graded until §9's table of
> positive and negative arms has run and printed PASS on every line.**
>
> **This document does not edit, amend or supersede `analyse_t15.py`.** That file
> is frozen and post-compute; rule 2 bars a gate change after first compute and
> rule 6 bars editing a frozen file at all. The repair lives here, in a
> successor, or nowhere.

Drafted 2026-08-28 by a heat-transfer `lab-lane` on the supervisor's diagnosis
brief. Every number below was measured by driving the frozen module's own
`read_probe_series` / `window_stats` / `_plant_probe_file` / `_s1_of`, never a
reimplementation.

---

## 0. Why a successor exists

`T15_UP_f` completed cleanly — `verification/runs/T-family/T15_runs/STATUS.T15_UP_f`
records `rc=0`, `wall_s=71749`, `ranks=1`, `core_min=1195.817`, `note=clean`,
and `DONE.T15_UP_f` is present. The rung is nevertheless **ungraded on all four
rows**: the frozen grader refuses (exit 2) inside its own planted-zero control,
before any row is printed. The refusal is recorded verbatim at
`verification/runs/T-family/T15_runs/T15_GRADE_OUTPUT.txt`, whose last line is
the `S1(FLUCTUATION)` constant-offset refusal and which contains **no `S1`,
`V1`, `V2` or `V3` row**.

The refusing arm is `analyse_t15.py:501`:

```
if d_const > 0.5 * ref:
```

registered in prose at `T15_PREREGISTRATION.md` §5 as *"the control refuses if
`σ/mean` moves under it by more than half its own value"*, under the stated
intent *"a working fluctuation reader must be nearly blind to a constant
offset"*.

**The defect is in the registered invariant, not only in the code.** That is
why no addendum to T15 can reach it and a successor is required.

## 1. The defect, measured

`S1 = σ/mean`. The arm adds a constant `+|mean(w)|` to every windowed sample.
For a series with **positive** mean this leaves `σ` unchanged and doubles the
mean, so the perturbed statistic is **exactly `ref/2`** and

```
d_const  ==  |ref/2 − ref|  ==  0.5 * ref      (an identity, not an approximation)
```

The guard therefore applies a **strict `>` at the exact boundary of an
identity**, and which side it lands on is decided entirely by floating-point
recomputation noise. Measured on `T15_UP_f` through the frozen module's own
readers:

| quantity | value |
|---|---|
| window samples | 1201 over `[120, 240] s` |
| `mean(w)` | `0.71159797387638801` m/s |
| `σ(w)` | `0.00014167478859376676` m/s |
| `ref = S1 = σ/mean` | `1.9909386169553251e-04` |
| `d_const` | `9.9546930847767328e-05` |
| `0.5 × ref` | `9.9546930847766257e-05` |
| `d_const / (0.5 × ref)` | `1.0000000000000107` |
| **excess above the boundary** | **+79 ulp** |

**It is a coin flip, not a one-sided margin.** Over 300 randomised positive-mean
synthetic series driven through the same readers (means `1e-4`–`1e4`,
`σ/mean` `1e-8`–`1`, `n ∈ {60,121,301,601,1201}`, gaussian / sine / square /
spike), **117 (39 %) would refuse**. Restricted to the non-degenerate subset
`ref ≥ 1e-6`: **85 of 222 (38 %)**.

**The excess is not bounded to "a few ulp".** It scales as the cancellation
amplification of recomputing `σ` after adding a constant of size `mean`, i.e.
as `ε·mean/σ = ε/ref`. For `T15_UP_f`, `mean/σ = 5023`, giving a predicted
`1.1e-12` relative and a measured `1.07e-14` — same regime. Measured excursions
across the synthetic set reached **6 827 ulp** at `ref ≈ 2e-4` (square wave),
**1 327 727 ulp** at `ref ≈ 1e-8`, and up to `8.8e7` ulp in the degenerate
corner where `σ` sits at the roundoff of `mean`. The failure is therefore
**worse the finer the fluctuation being measured** — the same inversion
`T8_STEADINESS_MEASUREMENT_2026-08-26.md` §7.2 named, reappearing in the
control rather than in the statistic.

**Two regimes the original account did not cover, found by driving the code:**

1. **A negative window mean makes the arm refuse unconditionally.** The plant is
   `+|mean|`, so for `mean < 0` it annihilates the mean; `σ/mean` explodes.
   Measured: a `mean = −0.6`, `σ/mean = 2.0e-04` series gives
   `d_const = 1.33e+12` against `0.5·ref = 1.01e-04`. Any probe station whose
   windowed mean is negative — a downdraft, a recirculation, a return flow —
   is refused deterministically, not by a coin flip.
2. **A perfectly dead reader passes.** For `σ = 0` exactly, `ref = 0` and the
   guard is `0 > 0` → false. The arm is **vacuous** on a constant series.

## 2. Was it catchable at freeze? Yes — and the selftest's own evidence line records the tell

`python3 analyse_t15.py --selftest` from
`verification/runs/T-family/T15_runs` reports **`SELFTEST PASS (0 failed)`**,
exit 0, 15 checks.

**The arm IS exercised, five times**, inside every `_run_forged` call. It
survives for two different reasons, both measured by instrumenting each forgery
at line 501:

| selftest forgery | `ref = σ/mean` | `d_const` | `0.5·ref` | excess | why it passes |
|---|---|---|---|---|---|
| default (`value-control`) | `0` | `0` | `0` | — | **vacuous**: `σ = 0`, guard is `0 > 0` |
| `co_max=1.9` (`courant`) | `0` | `0` | `0` | — | **vacuous** |
| `alpha=0.20` (`v3-fail`) | `0` | `0` | `0` | — | **vacuous** |
| `drift=0.20` (`stat`) | `5.25301086e-02` | `2.62650543e-02` | `2.62650543e-02` | **+0.0 ulp** | exactly on the boundary; strict `>` gives a free pass |
| `noise=0.10` (`s1-fail`) | `7.36649224e-02` | `3.68324612e-02` | `3.68324612e-02` | **+0.0 ulp** | exactly on the boundary; strict `>` gives a free pass |

**This is the sharper finding.** The two non-vacuous forgeries carry
`ref ≈ 5.3e-02` and `7.4e-02` — **265× and 370× more dispersive than the real
run's `1.99e-04`** — and at that conditioning the identity is numerically
*exact*, so the excess is 0 ulp and the strict `>` always passes. Measured fire
rate as a function of the regime, 60 seeds each, `n = 1201`:

| `ref = σ/mean` | fire rate |
|---|---|
| `1e-1` (the selftest's regime) | **7 %** |
| `1e-2` | 55 % |
| `1e-3` | 42 % |
| `2e-4` (**the real run's regime**) | 57 % |
| `1e-4` | 53 % |
| `1e-5` | 62 % |
| `1e-6` | 45 % |

**The negative control was exercised only in the one regime where it cannot
fail.** Worse, both non-vacuous forgeries produce `S1` values (`0.0525`,
`0.0737`) that sit **outside** the rung's registered PASS band `[0, 0.020]`:
**no forgery ever drove the arm at a dispersion level the rung was designed to
call PASS.** T15b's forgeries must span the band.

`T15_PREREGISTRATION.md` §5 already prints the evidence without reading it:
*"a constant offset of one whole mean moves it 0 to 0.037"* — the three zeros in
that range are the three vacuous forgeries.

**Second, unrelated selftest observation, reported not concealed.** Check (vii),
*"live tree, no DONE marker → exit 2 REFUSE"*, still prints `[ok]` — but
`DONE.T15_UP_f` now exists, so the refusal it observes comes from the S1 arm,
**not** from a missing marker. The check is currently passing for the wrong
reason. It is a masked negative control, not a false verdict, and it does not
touch any graded row.

## 3. The correct invariant for a normalised dispersion reader

> **A `σ/mean` reader is a NORMALISED dispersion. It is blind to a change of
> SCALE and it MUST see a change of MEAN. Demanding blindness to a constant
> offset asks it to be a `σ` reader, which it is not.**

| perturbation | a bare `σ` reader | a `σ/mean` reader | what a control may demand |
|---|---|---|---|
| constant offset `+c` | invisible | `ref → ref·mean/(mean+c)` — **fully visible, by construction** | it MUST move, in a **predicted direction and magnitude** |
| uniform scaling `×k` | `σ → kσ` | **invariant** | it must **not** move — this is the blindness arm |
| alternating `±p` | `√(σ²+p²)` | `√(σ²+p²)/mean` | it must move (already registered, and correct) |

The T15 arm tested the wrong invariant. The lab had already written the right
one down: `analyse_t5.A10_PROPOSED.py:1080` states *"a constant offset is
invisible to a dispersion reader BY CONSTRUCTION"* and routes the constant
offset to the **mean** reader instead; `analyse_t5b.py:539` and
`analyse_t16.py:82,435` do the same. T15 is the one file in the family that
routed a constant offset **into** a normalised dispersion reader and then
demanded blindness of it.

## 4. The replacement arms — each with a real two-sided margin

T15b replaces the single boundary-identity arm with three arms. **No arm may sit
at an identity, and every threshold is a factor, never an exact equality.**

**Arm C-1 — SCALE BLINDNESS (the true invariant).** Multiply every windowed
sample by `k = 1.5`. Predicted: `σ/mean` unchanged. Refuse if
`|ratio − 1| > 1e-6`. *Margin: the tolerance is ~10⁶ × the `~1e-12`
recomputation noise measured in §1. Two-sided and nowhere near an identity.*

**Arm C-2 — MEAN SENSITIVITY, with a PREDICTED response.** Add a constant
`c = +mean` and compare against the **closed-form prediction** `ref/2` rather
than testing a one-sided inequality against it:

```
predicted = ref * mean / (mean + c)        # = ref/2 for c = mean
refuse unless   0.90 <= d_const_signed / (ref - predicted) <= 1.10
```

*Margin: ±10 %, against a measured recomputation noise of `~1e-12` relative —
a margin ~10⁸× the noise, and the test now fails for a reader that is genuinely
broken (one that does not move, or moves the wrong way) instead of for one that
is exactly right.* The registered wording changes from **"must be nearly blind
to a constant offset"** to **"must respond to a constant offset by the amount a
normalised dispersion must respond by"**.

**Arm C-3 — NON-DEGENERACY, closing the `σ = 0` vacuum.** Refuse if
`ref == 0.0` before C-1 and C-2 run: a control whose reference is zero has not
been driven. (Measured need: three of the five T15 selftest forgeries had
`ref = 0` exactly.)

**Arm C-4 — SIGN PRECONDITION.** Refuse, with the value printed, if the window
mean is not bounded away from zero: `|mean| <= 10 * σ` → refuse. `σ/mean` is not
a meaningful dispersion measure across a sign change, and §1's negative-mean
regime must be refused **as an unusable statistic**, never mistaken for a reader
defect.

The existing and correct arms — exact-zero negative arm on identical bytes,
visible alternating plant, the measured detection ladder and floor, the
quadrature prediction recorded rather than asserted — are **carried over
unchanged** from `T15_PREREGISTRATION.md` §5.

**Selftest obligations on T15b's comparator, registered here:** the forgeries
must drive the arms at `ref ∈ {2e-4, 2e-3, 2e-2}` — spanning **inside** the
registered band and straddling its edge — and must include a **negative-mean**
series (expecting a C-4 refusal) and a **σ = 0** series (expecting a C-3
refusal). A mutation that makes the reader ignore the plant must be refused; a
mutation that makes it respond at half the predicted rate must be refused by
C-2. **No forgery may leave any arm's operand at zero.**

## 5. The four rows, re-registered

**The bands are carried over VERBATIM from the frozen `T15_PREREGISTRATION.md`
§3 and MAY NOT BE CHANGED.** The run already exists; a successor that re-chose a
band would destroy exactly the evidentiary content rule 2 exists to protect.

| row | quantity | reference | band (unchanged) |
|---|---|---|---|
| **S1** | `σ(w)/mean(w)` at the axis probe, `z = 3.0 m`, over `[120, 240] s` | 0 | **[0, 0.020]** |
| **V1** | `n_w`: OLS of `ln(w_axis)` on `ln(z − z₀)` | −1/3 | **[−0.383333, −0.283333]** |
| **V2** | `n_T`: OLS of `ln(T_axis − TRef)` on `ln(z − z₀)` | −5/3 | **[−1.716667, −1.616667]** |
| **V3** | `db/dz` of the top-hat radius `b = Q/√(πM)` | 0.144 | **[0.132, 0.156]** |

Gate order, controls (`C_CO`, `C_STAT`, `C_OP`, `C_GEOM`, `C_Z0`, `C_BOUND`,
`C_REF`), the S2/S3 reported readings, the one-mesh / no-triple / no-GCI rule
and the L-342 field classes are all carried over unchanged.

> **DISCLOSURE, OWED AND MADE BEFORE ANY FREEZE.** Diagnosing the arm required
> computing `ref`, and `ref` **is** S1. **S1 = `1.9909386169553251e-04` is
> therefore now known**, and it lies inside the frozen band. This does not
> corrupt the pre-registration — the band was frozen on 2026-08-26, before the
> run — but it does mean **T15b may not be presented as a blind re-grade**, and
> the band's freeze provenance must be cited from T15's commit, not from this
> draft. **Whether re-grading the existing `T15_UP_f` artifacts under a
> successor comparator is permissible at all, or whether a fresh run is
> required, is NOT this lane's call**: it is the supervisor's, and on the
> reading of `VERIFICATION_CHARTER.md` §2d.1's four-condition repair exception,
> plausibly the verification team's. **Flagged, not decided.**

## 6. The launcher must invoke the completion marker

`run_one_t15.sh` never invokes `mark_done_t15.py`. This is **not** a T15
oversight: **0 of 28 paired `run_one_*.sh` launchers in the T-family invoke
their `mark_done_*.py`** (§7 of this draft's companion measurement; the full
table is in the lane's report to the supervisor). The marker is a registered
completion step that no automated path in the T-family runs — neither the
launchers nor `scripts/queue_runner.py` / `scripts/queue_runner.sh`, which
contain no reference to it. It has been run by hand; only three T-family
`log.mark_done*.txt` records exist against ~140 `DONE.*` markers on disk.

**T15b's launcher registers the marker as its final step**, with the marker's
`rc` captured inside the wrapper (`setsid`'s parent returns 0 for every
outcome), logged to `log.mark_done.<UTC>.txt` beside the run, and the launcher's
own exit code carrying it. The one working precedent in the repository is
`verification/runs/F14-cooling-ladder/K0d_runs/.completion_watch/watch.sh:9`.

## 7. Cost — rule 12

**No new solver compute is proposed by this draft.** If the supervisor rules
that re-grading the existing artifacts is permitted, T15b's cost is **comparator
time only: < 1 core-min**, on `T15_UP_f` as it stands on disk.

If a fresh run is ruled necessary, the registered figures are T15's, re-derived
and **not** inherited by assertion: POINT **1 307 core-min**, CAP **2 600
core-min**, `timeout = 156 000 s`, `ranks = 1` — with the **actual** now
measured at **1 195.817 core-min** (`STATUS.T15_UP_f`), giving
**actual/predicted = 0.915**. That calibration row is owed to
`docs/COST_CALIBRATION.md` under rule 12 regardless of which way the re-grade
question is ruled, and is **not** discharged by this draft.

## 8. What this document does not do

- It **does not** edit, amend or supersede any frozen file, `analyse_t15.py`
  included.
- It **does not** enqueue anything. It **is** frozen and committed — that is
  rule 2's requirement and the whole of this document's evidentiary content —
  but the drop is the supervisor's separate act and has not been taken.
- It **does not** grade `T15_UP_f`. Every T15 row remains **PENDING** —
  a queue state, not a softened verdict.
- It **does not** touch **D389** (S13's peak-to-peak spread normalised by an
  absolute temperature). D389 is open, unowned, and re-grades the thermal
  corpus; it is not this team's to settle unilaterally. **Kinship, stated and
  stopped there:** both defects descend from *a statistic normalised by a mean
  that is not a natural zero*. D389 is a **GATE-WIDTH** defect — the divisor
  makes the band ~24× looser than it reads, so the *verdict* is wrong. The S1
  item is a **NEGATIVE-CONTROL** defect — the divisor makes the control's stated
  invariant false, so the *instrument refuses* and no verdict is produced at
  all. Same ancestor, opposite failure modes: one publishes a verdict it should
  not, the other withholds one it should give. They must be repaired
  separately and must not be bundled.


---

## 9. THE BIRTH REQUIREMENT, DISCHARGED ARM BY ARM — binding, and no row grades until it prints

Sanaa's 2026-08-28 directive 1 landed **after** §4 was drafted. §4's four arms
were specified as mathematics; this section specifies **how each is
demonstrated**, and it is the binding half. **Every arm below is driven on the
REAL, SOLVER-WRITTEN probe artifact, through the REAL production reader, and
every arm carries BOTH a POSITIVE limb that must be seen AND a NEGATIVE limb
that must not fire.** An arm that produces only one of the two is not a control.

### 9.0 The artifact, the producer and the reader — named, and verified on disk

| element | identity | verified how |
|---|---|---|
| **producer** | OpenFOAM `probes` function object under `buoyantBoussinesqPimpleFoam` (`STATUS.T15_UP_f`: `solver=buoyantBoussinesqPimpleFoam`, `rc=0`, `wall_s=71749`, `note=clean`) | the run's own status record |
| **artifact** | `verification/runs/T-family/T15_runs/T15_UP_f/postProcessing/axisProbes/0/U` and `.../0/T` | present on disk; the `U` file opens with the producer's own probe-station header block `# Probe 0 (0.0015625 0 2)` … `# Probe 3 (0.0015625 0 5)` followed by `# Time` and parenthesised 3-vectors — **the producer's schema, not a schema invented for the control** |
| **reader** | `read_probe_series` → `window_stats` → `rel_sd`, i.e. the identical call chain the graded row S1 travels (`_s1_of`) | the reader under test IS the reader that grades |
| **write path** | `_plant_probe_file`, writing into a **scratch copytree** of the run directory; the run tree is never written | the frozen module already refuses if the scratch copy resolves inside the case tree |

**T15b's comparator MUST re-assert all four rows of that table at grade time and
refuse if any fails.** In particular it must assert that the file it plants into
carries the producer's `# Probe` header block — a control that plants into a
file it wrote itself is the exact failure the directive names.

### 9.1 The arms

| arm | POSITIVE limb — must be SEEN | NEGATIVE limb — must NOT fire | why this pair is two-sided |
|---|---|---|---|
| **C-1 scale blindness** | The arm must be shown ABLE to fire: the same `k = 1.5` multiplication driven through a **mutant** reader that normalises by a FIXED constant instead of by the window mean (a bare `σ` reader) must give `\|ratio − 1\| = 0.5`, i.e. ~5×10⁵ times the `1e-6` tolerance — **C-1 fires.** | The **real** reader on the **real** probe file, same `k = 1.5`: `\|ratio − 1\| ≤ 1e-6` — **C-1 does not fire.** | A blindness arm that has never been shown to fire is indistinguishable from a `return True`. |
| **C-2 mean sensitivity** | Plant `c = +mean(w)` into the copied real probe file through `_plant_probe_file`; the real reader's signed move divided by the closed-form `ref − ref·mean/(mean+c)` must land in `[0.90, 1.10]` — **the instrument is shown to respond by the predicted amount, on the producer's bytes.** | **(i)** A half-response mutant (normalising by `mean + c/2`) and a no-response mutant (bare `σ`) must each be **REFUSED** by C-2. **(ii) SPECIFICITY, the W1c-P3 shape:** the same plant applied ONLY to samples with `t ∉ [120, 240] s` — outside the registered window — must move `S1` by **EXACTLY 0.0**. A reader that has quietly become a whole-series statistic is refused. | Without (ii) the arm proves only that *something* moved; (ii) proves the reader moved *because of the window it claims to read*. |
| **C-3 non-degeneracy** | Driven on the **real file with no byte changed at all**, handing the real `window_stats` a window containing a SINGLE sample — a window the producer's own output legitimately supports. `σ = 0` exactly, `ref = 0`, and **C-3 must fire.** (Second positive limb, optional and reported: a constant series written through `_plant_probe_file` in the producer's schema — a dead solve is a thing the producer really does emit — must also fire.) | On the real file over the registered window `[120, 240] s`, `ref = 1.9909386169553251e-04 ≠ 0` and **C-3 must not fire.** | The primary positive limb changes **zero bytes**, so it cannot be accused of writing a schema the producer never emits. |
| **C-4 sign precondition** | Offset the copied real series by `−(mean − 5σ)` so the window mean sits at `\|mean\| = 5σ`, inside the `\|mean\| ≤ 10σ` refusal region: **C-4 must fire.** | Offset by `−(mean − 20σ)` so `\|mean\| = 20σ`, outside the region: **C-4 must NOT fire.** And on the untouched real file, `mean/σ = 5023`: **C-4 must not fire.** | The two limbs **straddle the registered threshold from both sides**, three-quarters of a decade apart — the arm is proven to have an edge, not merely an output. |

### 9.2 What this lane concedes about C-4 and the second limb of C-3, so verification rules on the real question

C-4's limbs, and C-3's optional second limb, **write values the solver did not
produce**. This lane does not hide that. What it asserts is narrower and is the
distinction the directive draws: the bytes are written **by the frozen module's
own `_plant_probe_file`, into a copy of the producer's own file, in the
producer's exact schema (`# Probe` header, `# Time` header, parenthesised
3-vectors), and are read back by the production reader**. Nothing is emptied —
every tuple the reader consumes remains populated — and no schema is invented.
**A negative window mean is not a synthetic pathology: it is a downdraft, a
recirculation or a return flow, and §1's measurement showed the frozen arm
refuses such a station deterministically.** C-4 exists to name that as an
**unusable statistic** rather than a reader defect.

**Where this lane could be wrong, stated plainly:** if verification reads the
birth requirement as demanding that the non-zero arrive *only* by a physical
mechanism the solver itself produced in this run, then C-4's positive limb is
non-compliant and T15b needs a real negative-mean probe station — which
`T15_UP_f` does not contain, and which would force a fresh run. **That is a
verification ruling, not a heat-transfer one, and it is not presumed here.**

---

## 10. Registration under `VERIFICATION_CHARTER.md` §2d.1 — written for verification to rule, NOT ruled here

T15b re-grades artifacts that **already exist**. Whether that is a permitted
repair or whether a fresh run is required is **not this lane's call and not its
supervisor's**; §2d.1 is verification's clause. This section states the case in
the clause's own four conditions and stops.

| §2d.1 condition | T15b's claim | this lane's honest assessment |
|---|---|---|
| **(1) repairs a DEMONSTRABLE ERROR, not a preference** | `d_const ≡ 0.5·ref` is an **algebraic identity** for a positive-mean `σ/mean` reader under a `+\|mean\|` offset: `σ` is unchanged, the mean doubles. The frozen guard `d_const > 0.5*ref` is therefore a strict inequality evaluated **at the exact boundary of an identity**, decided by floating-point recomputation noise. §1 measures the consequence: a **39 %** refusal rate over 300 randomised positive-mean draws, plus a deterministic refusal on any negative-mean window and a **vacuous pass** at `σ = 0`. | **Strong.** An identity is not a preference. |
| **(2) established by an instrument INDEPENDENT OF THE HYPOTHESIS** | The instrument is the **closed-form algebra of §3's invariance table**, which grades nothing and does not know which direction any verdict would move; corroborated by the lab's own three independent precedents that route a constant offset to a MEAN reader and never to a normalised dispersion (`analyse_t5.A10_PROPOSED.py:1080`, `analyse_t5b.py:539`, `analyse_t16.py:82,435`). | **This is the load-bearing condition and verification must weigh it.** The favourable reading: the identity was derived from the reader's definition, not from S1's value, and it condemns the arm for **every** input, including inputs that would have made S1 fail. The unfavourable reading: this lane already knows S1 sits inside the band (opening disclosure), so it cannot claim personal ignorance of the direction. **Both readings are put on the table; neither is adopted here.** |
| **(3) the record discloses it, names the instrument, and QUANTIFIES what moved** | §0–§2 disclose; §1 names the instrument and quantifies: `d_const/(0.5·ref) = 1.0000000000000107`, **+79 ulp**, excursions to **6 827** and **1 327 727 ulp** in finer regimes; §2 quantifies that **3 of 5 selftest forgeries had `ref = 0` exactly** and the other 2 sat at **+0.0 ulp**. | **Met.** |
| **(4) pre-repair values recorded beside the published ones** | The pre-repair state is **a refusal, not a value**: `T15_GRADE_OUTPUT.txt` ends on the S1 constant-offset refusal and contains **no S1, V1, V2 or V3 row**. That file is cited, not restated, and T15b must print `PRE-REPAIR STATE: REFUSED (exit 2) — no row existed` beside every row it publishes. | **Met, and unusually cleanly**, because there is no prior number that a repaired number could be accused of having been steered toward. |

**THE SUPERVISOR'S STANDING RULING, CARRIED HERE AS A REFERRAL AND NOT AS A
DECISION.** The heat-transfer supervisor's position is that T15b may re-grade the
existing `T15_UP_f` artifacts rather than force a fresh run, **provided**:

- **(a)** the S1 / V1 / V2 / V3 bands carry over **VERBATIM** — discharged in §5,
  where the four bands are reproduced unchanged and marked MAY NOT BE CHANGED;
- **(b)** every new control threshold is derived from **that arm's own
  closed-form mathematics and NEVER from any `T15_UP_f` value**, with the
  derivation stated beside it — discharged in §11 below;
- **(c)** T15b declares **in its opening lines** that `S1 = 1.9909386169553251e-04`
  was already known at drafting — discharged in the opening disclosure above;
- **(d)** T15b registers under §2d.1's four-condition repair exception — this
  section.

**The supervisor states explicitly that (d) is VERIFICATION'S CLAUSE TO APPLY
AND NOT THEIRS.** This document is therefore written so verification *can* rule;
it does not presume the ruling, and **no row of T15b may be graded until
verification has ruled on §2d.1.** If verification rules against the re-grade,
§12's costed fresh run is the fallback and it is not a blocker.

---

## 11. Every control threshold, with the closed-form derivation it comes from — and none of them from `T15_UP_f`

Condition (b) above, discharged line by line. **No number in this table was read
off the run.**

| threshold | value | closed-form derivation |
|---|---|---|
| **C-1 tolerance** | `\|ratio − 1\| ≤ 1e-6` | `σ/mean` is homogeneous of degree 0 under `x → kx`, so the exact answer is `1` and the tolerance need only exceed IEEE-754 recomputation noise. The noise scales as `ε·mean/σ`; `1e-6` admits `mean/σ` up to ~`4.5e9`, i.e. `σ/mean` down to `2e-10` — far finer than any regime this rung can occupy. **Derived from the reader's homogeneity, not from any measurement.** |
| **C-2 acceptance band** | `0.90 ≤ moved/predicted ≤ 1.10` | The prediction is exact: `predicted = ref − ref·mean/(mean+c)`, which for `c = mean` is `ref/2`. ±10 % is chosen as the widest band that still refuses a **half-response** reader (ratio 0.5) and a **no-response** reader (ratio 0), the two mutants §9.1 requires it to catch; the nearest failing mutant sits **5 tolerance-widths away**. **Derived from the mutants it must catch.** |
| **C-3 refusal condition** | `ref == 0.0` exactly | A control whose reference is identically zero has not been driven; there is no free parameter to choose. |
| **C-4 refusal condition** | `\|mean\| ≤ 10σ` | `σ/mean` loses meaning as the mean approaches zero; `10σ` is the standard ~10 % coefficient-of-variation ceiling, i.e. the point at which the normaliser is no longer large against the dispersion it normalises. **Derived from the statistic's own definition.** It is not tuned to `T15_UP_f`, whose `mean/σ = 5023` sits **502 times** clear of it — a distance this lane records as an incidental *consequence* of the choice, never as its *justification*. |
| **selftest forgery regimes** | `ref ∈ {2e-4, 2e-3, 2e-2}` | Chosen to span **inside** the registered band `[0, 0.020]` and to straddle its edge, because §2 measured that all five T15 forgeries sat outside the band. **Derived from the registered band, which predates the run.** |

**The one honest exception, and it is only an exception in appearance.** `2e-4`
is the order of `T15_UP_f`'s S1. It is in the list because it is the **band's
own lower-middle decade**, and because §2 established that the frozen selftest
never drove the arm below `5e-2`. Were `T15_UP_f` deleted tomorrow the same
three regimes would still follow from the band alone.

---

## 12. The costed fallback if verification rules a fresh run is required — affordable, and not a blocker

Recorded now so that the ruling in §10 is never taken under cost pressure.

| item | figure | basis |
|---|---|---|
| fresh `T15_UP_f` run | **1 195.817 core-min** | **MEASURED**, `verification/runs/T-family/T15_runs/STATUS.T15_UP_f` (`wall_s=71749`, `ranks=1`) — the actual of the run that already exists, not an estimate |
| in dollars | **$1.0224** | **DERIVED, NOT MEASURED** — `1195.817 / 60 × $0.0513/core-h` at the rule-12 rate for c7a.4xlarge, which is **reported-by-owner**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| registered POINT / CAP | 1 307 / 2 600 core-min, `timeout = 156 000 s`, `ranks = 1` | carried from `T15_PREREGISTRATION.md`, re-derived rather than inherited by assertion |
| calibration | **actual/predicted = 0.915** | 1 195.817 / 1 307; owed as a row in `docs/COST_CALIBRATION.md` under rule 12 **regardless of which way §10 is ruled**, and **not** discharged by this document |
| re-grade cost, if permitted | **< 1 core-min** | comparator time only, on `T15_UP_f` as it stands |

**$1.02 does not buy a ruling.** The fresh run is affordable and is explicitly
**not** a blocker; §10 must be decided on the evidentiary question alone.
