# VMFL046-R9-REGRADE — RESULTS RECORD

**DRAFT, NOT COMMITTED.** Written by an `ansys-lane-opus` 2026-09-10. The supervisor
commits after reading the measurement-script diff personally (`SUPERVISION_CHARTER` §3
check-1).

**Case.** VMFL046 — Supersonic Flow with a Normal Shock in a Converging-Diverging Nozzle,
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 155**. Title-page verified
against the PDF under rule 15 at the R1 registration and carried forward.

**Character of the act.** **GRADING ONLY. ZERO SOLVER COMPUTE.** No mesh generated, no
solver launched, no field written. One invocation of a frozen repaired reader over
artifacts that already existed.

---

## 1. THE VERDICT

> # `NOT A RESULT`
>
> **Ground 1 (rule 5 step 1):** L1, L2 and L3 **all** failed the pre-registered plateau at
> `endTime = 0.080 s` — worst excursion **975.5×** `DELTA_X`.
> **Ground 2 (rule 5 step 2), independent and also sufficient:** the r = 2 grid triple on
> `x_shock` is **`OSCILLATORY`** (R = −2.364), which is `NOT A RESULT` **whatever the
> value**.
>
> **Cost of this act: 0.4000 core-min MEASURED**, against a pre-registered ~3 core-min
> estimate and a 30 core-min cap. **Solver compute: 0 core-min.**

`grade_rc = 1`, with a **printed limb verdict and no Python traceback** — so this is **not**
the pre-registered INSTRUMENT FAULT class, which would also have been `NOT A RESULT` but
for a different reason. The comparator **reached the gate and resolved it against the run**.

Verdict artifact: `verification/runs/ansys_verification/VMFL046-R8/GRADING_VMFL046_R9.log`
(108 lines) and `.../GRADING_VMFL046_R9.json`.

---

## 2. WHAT WAS CHECKED BEFORE ANY NUMBER WAS READ

### 2.1 Rule 2 — the frozen file IS the file that ran

| | |
|---|---|
| pinned grading-path blob (frozen registration §8.3) | `660464f94a2afcbf73c5787e992887233b2b3419` |
| `git hash-object` on disk | `660464f94a2afcbf73c5787e992887233b2b3419` — **equal** |
| blob committed at `faf4ccfd` | `660464f94a2afcbf73c5787e992887233b2b3419` — **equal** |
| `git diff faf4ccfd -- <comparator>` | **empty** |
| pre-registration blob, disk vs `faf4ccfd` | `2634c72e…` == `2634c72e…` — **equal** |
| HEAD at grading time | `faf4ccfdc3796aaac98b7b023cfbd8c1126dcc1a` |

**The hash was re-verified inside the same shell invocation that launched the grade**, with
the comparison asserted before `python3` was called, because a lane can move HEAD between
two bash calls (L-223).

**⚠ WHAT THE ENFORCING INSTRUMENT SAYS, AND A CORRECTION AGAINST MYSELF.**
`scripts/check_comparator_freeze.py` — rule 2's named enforcing instrument — was run and
returned **rc 3, `VERDICT: FAIL`**, over **692 lines** of output and a population of **267
graders, 13 violating** (9 `AMBIGUOUS-SCOPE`, 4 `AMENDED_AFTER`, 30 `FROZEN`, 211
`NO-MARKERS`, 13 `UNFROZEN`).

**This grading path IS in that population.** It appears at output line 470 as:

```
  NO-MARKERS             cases/ansys_verification/VMFL046-R9-REGRADE/grade_vmfl046_r8_repaired.py
      no completion marker in this tree -- out of evidence reach, reported so the gap is countable
```

**78 lines of the output name the `ansys` tree, and every one of the 78 ansys graders is
classified `NO-MARKERS`. NONE of them is in a violating class** — not `UNFROZEN`, not
`AMENDED_AFTER`, not `AMBIGUOUS-SCOPE`. So the instrument **neither faults nor blesses this
grading path**: it reports that this tree carries no completion marker of the form it looks
for, and says so in order that the gap be *countable* rather than silent. Its own
`CANNOT SEE` line is explicit about the limit: *"whether a late edit touched the grading path
or was purely additive; whether a disclosure exists; … a sha witness in a file no longer at
HEAD."* Rule 2's substantive requirement was therefore discharged by the direct
`git hash-object` comparison in the table above, which is the check the charter actually
specifies, and the lab-wide `FAIL` is a pre-existing condition across other teams' trees and
out of this row's scope.

> **CORRECTION AGAINST MYSELF, RECORDED RATHER THAN TIDIED AWAY.** An earlier reading by this
> lane reported that the instrument gives **"zero coverage"** of this grading path and that
> the string `ansys` appears **zero times** in its output, and proposed *"an enforcement
> instrument blind to a whole team's trees"* as a finding. **THAT WAS FALSE, IT IS WITHDRAWN,
> AND THE MECHANISM IS WORTH MORE THAN THE CLAIM WAS.** The first run was invoked as
> `… check_comparator_freeze.py 2>&1 | tail -20`, so the captured artifact held **the last 20
> of 692 lines**, and the grep for `ansys` was run against that 20-line window and returned
> 0. The pipeline's exit status was **`tail`'s 0, not the script's rc 3**, which removed the
> second signal that would have contradicted the reading. **A zero was reported from a reader
> that had never been shown able to see a non-zero — rule 3's own principle, applied to a
> grep instead of a field, and this lane failed it.** The withdrawn claim was caught by the
> supervisor, and the accurate version above was then re-measured here from a full-output
> capture with the real rc taken inside the invocation rather than from a pipeline.
> **The transferable rule: never assert a global absence from a `head`/`tail`-narrowed
> artifact, and never read a pipeline's exit status as the exit status of the command that
> matters** — capture rc inside the invocation, as the lab already learned for
> `setsid timeout`.

### 2.2 Rule 2 — the freeze conditions the registration set for itself (§8)

| condition | how it was checked | result |
|---|---|---|
| §8.3 grading path pinned, disk == committed | `git hash-object` vs `git rev-parse faf4ccfd:<path>` | **HOLDS** |
| §8.4 frozen R8 comparator untouched (rule 6) | re-hashed `cases/ansys_verification/VMFL046-R8/grade_vmfl046_r8.py` | **`f89114bb6ff81f683c6c6718460040cab305a8ce`, unchanged** |
| §8.5 "before" artifacts intact, not overwritten | `GRADING_VMFL046_R8.{log,json}` present; R9 written to distinct filenames | **HOLDS** |
| §8.6 no R9 grading artifact exists at freeze | `find` for `*VMFL046_R9*` / `*VMFL046-R9*` under the runs tree | **ABSENT — the pre-compute test discharged BY NAME** |
| §8.7 run root unmodified since 2026-09-10T04:25:31Z | `find <run root> -newermt '2026-09-10 04:25:32'` | **ZERO files** |
| §8.1, §8.2, §8.8 | the supervisor's, taken separately (check-1 diff-read, P1–P6, the §2d.1 ruling) | **not this lane's to certify** |

### 2.3 Rule 4 — the strict completion rule, verified independently by this lane

Checked with the lane's own reader **before** the comparator ran, so the completion finding
does not rest on the instrument whose repair is under review.

`system/controlDict` at every level: `endTime 0.08`, `deltaT 1e-08`, `maxDeltaT 1e-04`,
**`adjustTimeStep yes`**. Rule 4 clause 5 therefore takes its **adaptive-`deltaT`** form —
`n_exec == steps written` (Sanaa 2026-09-09). `round(endTime/deltaT) = 8 000 000` is **not**
the applicable arithmetic for this case and quoting it would be a category error; the
comparator's declared N2 departure implements a strictly stronger four-limb replacement
(`n(ExecutionTime) == n(Time =)`; last `Time` == `endTime` within `maxDeltaT`;
`n(Time) ≥ floor(endTime/maxDeltaT)`; the `Time` sequence strictly increasing).

| clause | L1 | L2 | L3 |
|---|---|---|---|
| `RUN_RC` | **0** | **0** | **0** |
| `End` line present | **yes** | **yes** | **yes** |
| `FOAM FATAL` | absent | absent | absent |
| last `Time` | **0.08** | **0.08** | **0.08** |
| `endTime` | 0.08 | 0.08 | 0.08 |
| `\|last − endTime\|` ≤ `maxDeltaT` | 0 ≤ 1e-04 | 0 ≤ 1e-04 | 0 ≤ 1e-04 |
| n(`Time =`) | 30 885 | 64 105 | 125 473 |
| n(`ExecutionTime`) | 30 885 | 64 105 | 125 473 |
| counts equal (clause 5, adaptive form) | **yes** | **yes** | **yes** |
| `n_min = floor(endTime/maxDeltaT)` = 800 ≤ n(`Time`) | yes | yes | yes |
| `Time` strictly increasing (no restart splice) | **yes** | **yes** | **yes** |
| last time dir | `0.08` | `0.08` | `0.08` |
| fields at `0.08` | `T U p phi rho uniform` | same | same |
| **AGE GUARD** — every field at `endTime` newer than the case's own `0/T` | **OK** (`0/T` 2026-09-09T18:31:31Z → fields 18:38:55Z) | **OK** (18:38:55Z → 19:34:43Z) | **OK** (19:34:43Z → 2026-09-10T04:24:43Z) |

**Every clause holds at every level. The solve is not what failed.** Row #71 was able to
say this of L1 only; L2's and L3's `check_completion` had **never** run against this data
before, because the frozen reader refused at L1 upstream of them. This record closes that
gap.

Note on the age-guard chain: each level's `0/T` is dated at that level's launch, and the
launches were sequential, so L2's `0/T` (18:38:55Z) coincides with L1's field write. The
guard is **per level against its own `0/T`**, which is the clause as written, and it holds
in that form at all three.

### 2.4 Rule 3 — the planted-zero control fires, and its refusal path is exercised

The comparator carries **five** planted controls. Each writes a known perturbation into a
**scratch copy on disk**, reads it back **through the same reader the gate uses**, and
**refuses (exit 2)** if the reader cannot recover it.

Plant magnitudes, from the frozen source: **`PLANT_DX = 1.000e-02 m`**,
**`PLANT_DX_SMALL = 6.250e-04 m`** (exactly `DELTA_X` — the quantum-discrimination plant),
**`PLANT_K_T = 1.0e-3`** relative into the `T` field, with `PLANT_C2_TOL = 0.25` of the
plant.

**Against this run's real data, for the first time ever, all five passed at all three
levels:**

| control | subject | L1 | L2 | L3 | tol |
|---|---|---|---|---|---|
| A | the `x_shock` reader | err **6.924e-05** | **2.415e-04** | **6.601e-05** | 2.500e-03 m |
| B | the plateau **reducer**, planted into the window's **maximum** | ptp 1.0094e-01 → **1.1094e-01** | 4.1806e-02 → **5.1791e-02** | 6.0972e-01 → **6.1967e-01** | recovers the +1.000e-02 m plant |
| C1 | translation invariance | inert **0.000e+00**, live **+1.000000e-02** | same | same | — |
| C2 | per-sample independent read-back | worst **7.390e-04** (spread 8.083e-04) | **2.415e-04** (3.906e-04) | **2.133e-04** (4.099e-04) | 2.500e-03 m |
| D | the `T`-field reader | err **4.989e-08** | **4.989e-08** | **4.999e-08** | 1e-6 relative |

**The refusal path is not merely present in the source — it is exercised and green.** The
comparator's `--selftest`, run at the pinned blob by this lane, reports **90 ok / 0 FAILED,
rc 0** (matching the count the frozen registration §2 recorded pre-freeze), and among those
arms:

- `A refuses a dead reader` → `REFUSES(2)`
- `A refuses the node-snapping reader at plant = DELTA_X` → `REFUSES(2)`
- `B refuses a dead reader` → `REFUSES(2)`
- `C1 refuses a DEAD reducer (constant)` → `REFUSES(2)`
- `C1 refuses a NON-TRANSLATION-INVARIANT reducer (relative spread)` → `REFUSES(2)`
- `C2 refuses a dead reader (constant)` → `REFUSES(2)`
- `C2 refuses a half-scale (biased) reader` → `REFUSES(2)`
- `C2 refuses R1's node-snapping reader at plant = DELTA_X` → `REFUSES(2)`
- `D refuses a T internalField that is not a nonuniform scalar list` → `REFUSES(2)`

**This is the whole content of rule 3: a reader shown able to see a non-zero, and shown to
refuse when it cannot.** The controls' pass here is therefore evidence, not decoration.

**Plant design, worth carrying forward.** The comparator's own comments record three
paid-for plant-design defects that this design avoids: **CANCELLATION** (a plant covering
the whole reduction set is a rigid translation the reducer cannot see), **ABSORPTION**
(measured on real data: a 1.0e-02 m plant into an *interior* window member left the ptp
**unchanged** where the window already spread 1.1066e-01 m — which is why PLANT B plants the
window's **maximum**), and the node-snapping mutant. Note that L1's and L3's *unplanted*
plateau spreads (1.0094e-01 and 6.0972e-01 m) are of the same order as, and larger than, the
1.0e-02 m plant, so **PLANT B's argmax targeting is doing real work on this data** — an
interior plant would have been absorbed here exactly as the comment predicts.

### 2.5 The W1 read audit

Passed at all three levels: exactly **33 distinct** centreline sample files opened inside
each level's run root, **all** inside the registered window `t ∈ (0.064, 0.080] s`, which
holds 33 of the 160 written samples — matching the frozen W3 arithmetic (160 samples, 17
per window, two windows sharing one boundary sample for 33 distinct). The 19 excluded paths
per level are the plants' own `/tmp/vmfl046r4_plant{A,B,C2}_*` scratch copies, excluded
under `§2aw(c)` as **not run data** and **enumerated by full path in the log** rather than
filtered silently — so the exclusion is auditable rather than asserted.

---

## 3. THE MEASUREMENTS

### 3.1 The gate — carried byte-identical from R8; nothing moved

| | |
|---|---|
| gate quantity | **`x_shock`** |
| reference | **1.250 m** (F. M. White, *Fluid Mechanics*, quasi-1D **inviscid**) |
| band | **±5 %** = half-width ±0.0625 m → **[1.1875, 1.3125] m** |
| reader | interpolating **last downward Mach = 1 crossing** |
| registered window | `t ∈ (0.064, 0.080] s`, 33 of 160 samples |
| plateau threshold | `DELTA_X = 6.250e-04 m` — ptp over two adjacent `W = endTime/10` windows **and** their mean drift |
| triple | r = 2: L1 3 200 → L2 12 800 → L3 51 200 cells |
| GCI factor | `Fs = 1.25` |
| ceiling | **`GATE REACHED`** — `PASS` unreachable |

**Gates created / moved / retired: 0. Bands moved: 0. Thresholds moved: 0. Caps lifted: 0.
Labels changed: 0.**

### 3.2 The level values

| level | cells | steps | `x_shock` (window-A mean — **THE LEVEL VALUE**) | deviation vs 1.250 m | inside band? | `x_shock` final sample |
|---|---|---|---|---|---|---|
| **L1** | 3 200 | 30 885 | **1.260863658 m** | **+0.8691 %** | *would be inside* | 1.303061746 m |
| **L2** | 12 800 | 64 105 | **1.181161685 m** | **−5.5071 %** | outside | 1.156016742 m |
| **L3** | 51 200 | 125 473 | **1.369600526 m** | **+9.5680 %** | outside | 1.414690237 m |

### 3.3 Plateau — the first gating limb, and all three levels fail it

| level | P1 (ptp win-A) | P2 (ptp win-B) | P3 (mean drift) | vs `DELTA_X` 6.250e-04 m | state |
|---|---|---|---|---|---|
| **L1** | 1.0094e-01 | 1.2522e-01 | 2.0919e-02 | worst **200.3×** over | **NOT PLATEAUED** |
| **L2** | 4.1806e-02 | 4.2993e-02 | 1.6613e-02 | worst **68.8×** over | **NOT PLATEAUED** |
| **L3** | 6.0972e-01 | 3.0216e-01 | 9.2269e-02 | worst **975.5×** over | **NOT PLATEAUED** |

These are not marginal misses. **The shock has not settled at `endTime = 0.080 s` at any
level**, and at L3 it misses by three orders of magnitude. Rule 5 step 1 makes this
`NOT A RESULT` **before a band comparison is permitted at all**.

### 3.4 Roache triple gating (rule 5) — `OSCILLATORY`

```
triple on x_shock: L1=1.260864  L2=1.181162  L3=1.369601
state = OSCILLATORY   R = -2.364   p = n/a   GCI = n/a
```

**Both triples and the orders, printed as rule 5 requires:**

| | L1 → L2 → L3 |
|---|---|
| **value triple** | 1.260864 → 1.181162 → 1.369601 m |
| **plateau triple** (worst of P1/P2/P3 per level) | 1.2522e-01 → 4.2993e-02 → 6.0972e-01 m |
| **convergence ratio** | **R = (f₃−f₂)/(f₂−f₁) = (+0.188439)/(−0.079702) = −2.364** |
| **observed order p** | **`n/a`** — not computable on a non-monotone triple, and not fabricated |
| **GCI at `Fs` = 1.25** | **`n/a` — DELIBERATELY NOT QUOTED** |
| **iterative convergence / plateau at each level** | **FAILED at all three** |

**R < 0 is oscillatory; |R| = 2.364 > 1 means the oscillation GROWS under refinement.** The
sequence goes up, then down, then further up: the middle level sits **below** both its
neighbours, and the L2→L3 swing (+0.188 m) is 2.36× the L1→L2 swing (−0.080 m). There is no
monotone trend for an order to be fitted to.

**Why no GCI is printed, stated so nobody adds one later.** Rule 5's own sentence: *never
quote a GCI when the three values are not monotone.* A Richardson extrapolation on this
triple would produce a finite number with **no referent** — it would report a discretisation
uncertainty for an asymptotic range the data does not demonstrate. `Fs = 1.25` is the
registered factor and is **not applied**.

**⚠ THE NUMBER THAT LOOKS LIKE SUCCESS IS THE COARSEST ONE.** L1, at **+0.87 %**, sits
comfortably inside the ±5 % band. It is the **least refined** level of the three, and the
band it sits inside is the one the finer levels leave. This lab has already written the
lesson on this exact case — `ANSYS_VERIFICATION_CHARTER` §24.6: *"an agreement obtained at
the coarsest level is the least trustworthy number in the set, and it is the one that looks
most like success."* **L1's +0.87 % is not a partial pass, not a `GATE REACHED` at L1, and
not evidence of anything.** Rule 5's ordering is one-way: the gate can turn a would-be
`GATE REACHED` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse.

**Relation to the §24.5 prior, which gates nothing.** Register row #54 (a **different rung**
of this case) recorded a triple moving monotonically away from the reference,
1.25763 → 1.19260 → 1.15258 m. This rung's triple is **not** that: it is non-monotone. The
prior was cited in the registration to set the expectation of difficulty and **explicitly
gates nothing here**; it is recorded in that role and no further.

### 3.5 The off-gate limbs — both passed, and neither had ever seen this data

- **LIMB (b), the `fvOptions limitTemperature [150, 2000] K` clamp is NON-BINDING.** `T`
  over the graded window spans **[229.5, 634.39] K** (L1), **[227.74, 641.64] K** (L2),
  **[223.57, 666.53] K** (L3). Interior of the clamp at every level, with no approach to
  either bound. **The clamp whose bounds the frozen reader could not parse never bit.**
- **LIMB (c), washout / shock-stand guard.** `x_shock` stands in **[1.1812, 1.3176]**,
  **[1.1544, 1.1974]** and **[1.0855, 1.6953]** m, interior of the exit at 1.998 m. No
  washout, no spurious upstream crossing.
- **Diagnostic, not gated: R1's node-snapping reader on the same bytes** gives 1.305638 /
  1.152819 / 1.417913 m, with quanta 6.2375e-03 / 3.1187e-03 / 1.5594e-03 m — i.e.
  **9.98× / 4.99× / 2.50× `DELTA_X`**. The snapping reader's own resolution is coarser than
  the plateau threshold it would be asked to test, which is why R2/R3/R4 interpolate. Printed
  as a cross-check on the interpolating reader, and gated on nothing.

### 3.6 Independent corroboration of the §2d.1 condition-(2) instrument, re-measured here

The registration's Instrument A is the solver's own `limitTemperature` fvOption reporting.
Re-counted by this lane directly from the three logs rather than relayed:

| level | `limitTemperature=limitT` report lines | lines with bounds ≠ `Tmin=150`/`Tmax=2000` | lines with `LimitedCells ≠ 0` |
|---|---|---|---|
| L1 | 185 310 | **0** | **0** |
| L2 | 384 630 | **0** | **0** |
| L3 | 752 838 | **0** | **0** |
| **total** | **1 322 778** | **0** | **0** |

The total matches the registration's figure exactly. **The clamp was present, active, at
exactly the frozen bounds `[150, 2000]`, and limited not one cell in 1.32 million report
lines** — established by an instrument inside the solver that grades nothing, cannot know
what `x_shock` is, and cannot know which direction any verdict wants. The frozen reader's
refusal was the reader's fault, not the case's, and that is now measured twice
independently.

---

## 4. COST AND CALIBRATION (rule 12)

### 4.1 This act

| | |
|---|---|
| solver compute | **0 core-min. $0.00.** No mesh, no solver, no field written. |
| grading wall | **24 s** (2026-09-10T15:46:15Z → 15:46:39Z) |
| ranks | **1** |
| **actual** | **0.4000 core-min MEASURED** (24 × 1 ÷ 60), from the wrapper's own clock |
| pre-registered point estimate | **~3 core-min** |
| pre-registered cap | **30 core-min** — **no overrun**; used 1.3 % of the cap |
| **ratio actual / predicted** | **0.133×** |
| dollars | **$0.000342 — DERIVED, NOT MEASURED**, at c7a.4xlarge $0.0513/core-h, owner-stated / reported-by-owner (`COMPUTE_BUDGET_CHARTER` §5: the box cannot read its own billing) |
| box state at launch | load average **13.14** on 16 vCPU |

**Attribution of the 0.133× gap — misprediction, in the conservative direction, with two
named mechanisms.** (a) The estimate was built on the *frozen* comparator's 10 s L1-only
pass and extrapolated to 912.1 MB of solver logs across three levels; the actual read of all
three at 24 s implies the log parse is **not** the bottleneck the estimate assumed — the
`re.findall` passes ran against a **warm page cache**, the same logs having been read by the
R8 grading pass and by this lane's own independent rule-4 check minutes earlier. **A cold
read would cost more, and this figure should not be carried forward as a cold-cache basis.**
(b) The 30 core-min cap was set deliberately wide because the box carried load average
**29.6** at drafting time; at launch it carried **13.14**, so the contention headroom the cap
was paying for was not needed. **No waste.** **This is an over-estimate and it cost the lab
nothing** — but it is recorded so the next grading-act estimate for this family starts from
0.4 core-min warm / an unmeasured cold figure, rather than from 3.

### 4.2 The underlying VMFL046-R8 SOLVER run — estimate versus actual

**This is the calibration of the solve that produced the artifacts, NOT of this grading
act, and its cost is NOT re-charged to this row.** It is recorded at Row #71 and is
restated here because rule 12 requires the comparison at process completion, and the process
— a rung graded — completed only now.

All three levels ran **serial (1 rank)**: no `decomposeParDict`, no `processor*`
directories, verified on disk.

| level | pre-registered estimate | per-level cap | **actual (ExecutionTime basis)** | actual (ClockTime, gross) | ratio actual/est | within cap? |
|---|---|---|---|---|---|---|
| L1 | ~7.7 core-min | 24 | **7.3295** (439.77 s) | 7.4000 (444 s) | **0.952×** | yes |
| L2 | ~45 core-min | 140 | **55.3393** (3 320.36 s) | 55.8000 (3 348 s) | **1.230×** | yes |
| L3 | ~345 core-min | 1 040 | **528.0725** (31 684.35 s) | 529.9833 (31 799 s) | **1.531×** | yes |
| **total** | **~398 core-min** | **1 200** | **590.7413** | **593.1833** | **1.484×** | **yes** |

- **Basis, stated because the two differ.** The **590.7413 core-min** figure carried at Row
  #71 is the **`ExecutionTime` (CPU-time) basis**. The **ClockTime (wall) gross** is
  **593.1833 core-min**. The difference, **2.4420 core-min (0.412 %)**, is I/O and OS
  overhead.
- **Dollars: actual $0.5051, predicted $0.3400 — both DERIVED, NOT MEASURED**, at
  $0.0513/core-h. Under the $25 pre-authorisation.
- **Stall rule.** `COMPUTE_BUDGET_CHARTER` §2's 3600-s figure is exceeded by L2 (3 348 s is
  below it) — only **L3, at 31 799 s wall**, is above. It is **not a stall**, and the test is
  the same one other rows on this ledger used: `ExecutionTime/ClockTime` = **0.99047 /
  0.99174 / 0.99640**, so the process held 99 %+ of one core throughout, and `Time` advanced
  strictly monotonically through all 125 473 steps to `endTime`. A descheduled or hung
  process does not hold CPU time at wall time. **Cleaned = gross = 590.7413** on the
  `ExecutionTime` basis.

**ATTRIBUTION OF THE 1.484× GAP — MISPREDICTION, AND CONTENTION IS MEASURABLY RULED OUT.**

- **Contention: ~0, and this is measured rather than assumed.** The
  `ExecutionTime/ClockTime` ratios of 0.99047 / 0.99174 / 0.99640 leave at most **0.412 %**
  of the total spend in the descheduling channel. **Contention cannot account for a 48 %
  miss and is not named as a contributor.**
- **Waste: named separately and unabsorbed (`COMPUTE_BUDGET_CHARTER` §6), as Row #71
  recorded it — 590.7413 core-min yielded no gradeable answer.** It stays named. **But this
  re-grade reclassifies WHY, and that reclassification matters:** the spend was originally
  named waste because an **instrument** refused. The re-grade shows the run would have
  graded **`NOT A RESULT` on physics** — on the plateau limb at L1, before the triple was
  ever assembled — even had the frozen reader parsed its own case file. **The instrument
  defect therefore cost the lab a READING, not an ANSWER.** That is not an excuse for the
  defect and does not reduce the waste figure by one core-minute; it does mean the successor
  rung's problem is `endTime`, not the regex. **The waste figure is NOT absorbed into the
  1.484× ratio.**
- **The misprediction, located precisely.** The R8 estimate applied a flat **~2.0×
  start-from-rest factor** to R5's measured impulsive-start L2/L3 costs. The measured
  factors are **not constant and grow with refinement**: L2 **2.449×**, L3 **3.078×**. L1,
  which was estimated from a same-configuration start-from-rest smoke rather than a factor,
  came in at **0.954×** of its basis — **the smoke basis was accurate and the factor was
  not.**
- **THE MECHANISM, MEASURED, AND IT IS NOT THE PER-CELL RATE.** The per-cell-step cost is
  nearly **flat** across the triple: **4.4497e-06 / 4.0465e-06 / 4.9320e-06 s per
  cell-step** (spread only 1.22×, non-monotone, consistent with cache-residency effects
  rather than a modelling error). The miss is entirely in the **cell-step count**:
  - cells grow **exactly 4×** per level (2-D r = 2: 2 × 2) → 3 200 / 12 800 / 51 200;
  - steps grow **2.076×** then **1.957×** (≈ 2×, since `Δt ∝ Δx` under a fixed `maxCo`
    with `adjustTimeStep yes`) → 30 885 / 64 105 / 125 473;
  - so **cell-steps grow ≈ 8× per level** (measured **8.30×** then **7.83×**) →
    9.883e7 / 8.205e8 / 6.424e9;
  - **the estimate's implied per-level growth was 5.84× and 7.67×**, against measured cost
    growth of **7.55×** and **9.54×**. The under-prediction **compounds**: 1.29× then 1.24×,
    multiplying into the 1.531× miss at L3.
- **THE TRANSFERABLE CALIBRATION LESSON, and it is checkable.** Price an adaptive-`Δt`
  transient by **cells × steps at a measured per-cell-step rate**, where the step count is
  derived from `Δt ∝ Δx` under the registered `maxCo` — never by applying a flat
  "start-from-rest factor" to a predecessor's **total**, which silently assumes the factor is
  mesh-independent when the step count is not. Retrodicted: a flat 4.5e-06 s/cell-step model
  over the measured cell-step counts predicts **7.41 / 61.5 / 481.8 = 550.8 core-min**, i.e.
  **0.93× of actual** — within 7 %, against the registered model's **1.484×**. **A method
  that was available before the run would have predicted it to 7 %.**

### 4.3 Ledger

Both rows — the grading act and the solver run — are drafted for
`docs/COST_CALIBRATION.md` in
`cases/ansys_verification/VMFL046/DRAFT_CALIBRATION_ROWS_VMFL046_R9_REGRADE.md`, to be
appended under that file's append rules and the rule-10 private-index protocol by the
supervisor.

---

## 5. WHAT THIS RECORD REFUSES TO CLAIM

| | |
|---|---|
| that the run is now graded sound | **NO.** The physics limbs ran and the run **failed** them. |
| that L1's +0.87 % is a partial pass or a per-level `GATE REACHED` | **NO.** Rule 5 forbids it; §24.6 names it as the least trustworthy number in the set. |
| a GCI, or an observed order | **NEITHER EXISTS.** The triple is non-monotone; both are `n/a` and neither is estimated. |
| that the repair recovered 590.74 core-min | **NO.** It recovered a **reading**. Row #71's waste stands unerased. |
| that this row and Row #71 are two confirmations | **NO. One solve, two readings.** |
| a `PASS` | **UNREACHABLE for this case on two independent grounds (§24.4).** |
| four-condition `§2d.1` support | **NO — one condition plus the freeze-before-run ordering.** |
| that `scripts/check_comparator_freeze.py` blessed this grading path | **NO.** It classifies this grading path `NO-MARKERS` — neither faulted nor blessed. Rule 2 was discharged by direct `git hash-object` comparison instead, which is the check the charter specifies. See §2.1, including the withdrawn "zero coverage" claim. |
| that the 0.4000 core-min figure is a cold-cache basis | **NO.** The logs were warm. A cold read is **not measured** and is left as an absence. |
| that a successor rung will grade | **NOT PREDICTED.** `endTime = 0.080 s` is demonstrably too short; what a longer clock costs and whether it settles are matters for a new pre-registration. |

---

## 6. THE FINDINGS, FOR THE SUPERVISOR TO ROUTE

1. **`endTime = 0.080 s` is too short for this case, measured.** The plateau misses by
   68.8×–975.5× of `DELTA_X` at every level, and at L3 the shock is still moving downstream
   at the final sample (window-A mean 1.3696 m → final sample 1.4147 m, +0.045 m inside the
   last window). **This is the physics finding the frozen reader's refusal was hiding.** It
   is a **registration-design finding for a successor rung**, and it is emphatically **not**
   a licence to widen `DELTA_X` or extend the clock inside this closed registration.
2. **A successor's cost is now predictable from a measured basis.** The per-cell-step rate is
   flat at **≈ 4.0–4.9e-06 s**, cells × steps scales at **≈ 8× per r = 2 level**, and a
   longer `endTime` scales the step count linearly at fixed mesh. A rung at, say,
   `endTime = 0.24 s` would cost **≈ 3× of 590.74 ≈ 1 772 core-min** at the same triple —
   which is a budget question for the supervisor before any registration, not an assumption
   to bury in one.
3. **All 78 of this team's graders sit in `scripts/check_comparator_freeze.py`'s population
   and every one of them is classified `NO-MARKERS`** — including this grading path, at that
   run's output line 470. **None is in a violating class**, so the instrument reports the gap
   as *countable* rather than adjudicating it: *"no completion marker in this tree — out of
   evidence reach."* Rule 2 names this script as the enforcing instrument, so **a whole
   team's graders sitting permanently out of its evidence reach is worth a docket entry** —
   not because the instrument is blind to the tree (it is not; it lists every file), but
   because it can never move any ansys grader from `NO-MARKERS` to `FROZEN` until the tree
   carries the completion markers it reads. Independent of this case, and **actionable: the
   fix is a marker convention in `cases/ansys_verification/`, not a change to the script.**
   *(This item supersedes an earlier, false version of itself — see the withdrawal in §2.1.)*
4. **A candidate `LESSONS` entry, for the supervisor's read, not filed by this lane:** *a
   repaired reader can vindicate the repair and still return a negative verdict, and the two
   facts must be reported together — the instrument defect of Row #71 cost a reading, not an
   answer, and saying so is neither an excuse for the defect nor a demotion of the re-grade.*
5. **A candidate `NUMERICS_KNOWLEDGE` entry, likewise unfiled:** *for an adaptive-`Δt`
   transient under a fixed `maxCo`, per-level cost growth on an r = 2 2-D refinement is
   ≈ 8× (4× cells × 2× steps), and a "start-from-rest factor" applied to a predecessor's
   total is mesh-dependent — measured 2.449× at L2 and 3.078× at L3 where 2.0× was
   registered.*
6. **A candidate `LESSONS` entry earned by this lane's own error, unfiled, and the one it
   would most want written down:** *a global absence must never be asserted from a
   `head`/`tail`-narrowed artifact, and a pipeline's exit status is the exit status of the
   LAST command in it, not of the one whose verdict matters.* This lane reported that the
   string `ansys` appeared **zero times** in `check_comparator_freeze.py`'s output; the
   capture was `… | tail -20`, so the grep ran against **20 of 692 lines**, and the recorded
   exit code was **`tail`'s 0, not the script's rc 3** — which removed the one other signal
   that would have contradicted the reading. The measured truth is **78 lines**. **This is
   rule 3's own principle applied to a grep: a zero from a reader not shown able to see a
   non-zero is not evidence, and this lane did not ask what its window could not see.**
   Sibling instances already on the lab's record: `setsid timeout` returning 0 for every
   outcome (capture rc *inside* the wrapper), and `grep … log.* | tail -1` being a coin flip
   (read one named artifact). The correction was made by the supervisor, not caught here, and
   it is recorded in §2.1 rather than quietly repaired.
