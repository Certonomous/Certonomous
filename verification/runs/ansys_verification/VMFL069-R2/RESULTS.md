# RESULTS — VMFL069-R2: Two Phase Poiseuille Flow (VM2026R1, printed p. 205 = PDF p. 219)

**DRAFT FOR THE `ansys-verification-supervisor`. NOTHING HERE IS LANDED.** The
register row and the calibration row are drafted beside this file and are **not**
committed: the supervisor reads the grade personally before any row enters
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`.

Graded by `ansys-lane-opus` (Opus 5) on **2026-08-31**, from a run that completed
**unattended** at `2026-08-31T09:00:42Z` and was ungraded for 5 h 53 m. **No solver
was launched by this lane. No frozen file was edited, patched or re-run.**

Every number below carries its tag: **MEASURED** / **DERIVED** / **EXTRAPOLATED** /
**REGISTERED** / **REPORTED-BY-OWNER** / **TRANSCRIBED**.
(`VERIFICATION_CHARTER` §2k.9 closes the set at eight; **BORROWED** and **ASSUMED**
are not used in this record, because nothing here is either.)

---

## 1. THE FREEZE, RE-VERIFIED BY THIS LANE WITH ITS OWN TIMESTAMP

Re-run at **`2026-08-31T14:52:56Z`**, repository HEAD
`76ce0ed5acf6fddf39ab05e15f3b2911f55fb489`. The supervisor's own check is **not
cited as this lane's evidence**; these are this lane's commands and this lane's clock.

| frozen file | `git hash-object` on disk | blob at `7fe979a5` | blob at HEAD | |
|---|---|---|---|---|
| `cases/ansys_verification/VMFL069-R2/PREREGISTRATION.md` | `7c209caf41c7183a8e43b707036535c3b55dd976` | identical | identical | **MEASURED** |
| `cases/ansys_verification/VMFL069-R2/grade_vmfl069_r2.py` | `8e0b4c3f80d6f97d391427536d049dcf75c4d114` | identical | identical | **MEASURED** |
| `cases/ansys_verification/VMFL069-R2/run_vmfl069_r2.sh` | `f03d771e8bce8fc11dea84e7021650d7e84c5e58` | identical | identical | **MEASURED** |

`git merge-base --is-ancestor 7fe979a5 HEAD` returns **0** — the freeze commit
`7fe979a59c9111fdda726a1cd84d94790a5be3fc`, dated **`2026-08-30T23:48:19Z`**, is an
ancestor of HEAD (**MEASURED**). The run's first write is `CONTENTION.txt`
`sampled_utc = 2026-08-30T23:51:23Z` (**TRANSCRIBED**, `CONTENTION.txt` line 1),
**3 m 04 s after the freeze**: pre-registration committed before compute, confirmed
independently.

Corroborating, from the run's own records rather than from this lane's git calls:
all three `RUN_RC.<level>` files carry `prereg_blob = 7c209caf…` and
`comparator_blob = 8e0b4c3f…` (**TRANSCRIBED**, `RUN_RC.L1`/`L2`/`L3`) — the launcher
hashed the same bytes at launch that this lane hashes now.

The comparator's own `--verify-frozen` arm agrees: `disk == head` **OK** for the
pre-registration and the comparator, rc 0 (**MEASURED**). It does not check the
launcher; the launcher was checked by this lane's `git hash-object` above.

---

## 2. THE MANUAL, READ FIRST AND INDEPENDENTLY

`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
printed **p. 205–206**. Read by this lane before anything else on this item.

**The page is FIGURE-ONLY and that is correct, not a defect.** p. 206 carries
*"Results Comparison for Ansys Fluent — Figure .69.2: Comparison of Velocity Profile
for Two Phase Flow"* and **no Target table and no numeric column** (**MEASURED** —
this lane's own read of the sidecar). The gate is therefore the closed-form solution
of the same continuum model, never the figure; **no Ansys number appears anywhere in
this record**, and the figure was not read, digitised or compared against.

Every setup quantity the registration declares was checked against the manual page by
this lane (all **TRANSCRIBED**, manual p. 205): *"the same density"*; *"Kinematic
Viscosity Fluid-1 = 0.1, Fluid-2 = 0.02"*; *"2m X 4m"*; *"Periodic Boundary is used
with a Pressure Gradient = -0.5 Pa/m"*; *"The flow is steady. Deformation of the
interface is not modeled."*; and the interface *"located at half of the height of the
channel"*. The frozen case files match all six.

The manual's own spelling of the title is **"Poiseulle"** (p. 205 heading). It is
reproduced here as the manual prints it and is not corrected.

---

## 3. STRICT COMPLETION — `CLAUDE.md` RULE 4, EVERY CLAUSE, ALL THREE LEVELS

All values **MEASURED**, from `GRADING_VMFL069_R2.json` and `RUN_RC.<level>`.

| clause | L1 | L2 | L3 |
|---|---|---|---|
| `rc` (`rc_status`) | **0** MEASURED | **0** MEASURED | **0** MEASURED |
| `End` lines | 1 | 1 | 1 |
| last `Time` == `endTime` 1000 | **1000 == 1000** | **1000 == 1000** | **1000 == 1000** |
| `Time` lines / `ExecutionTime` lines (**clause 5 as ADAPTED**) | **84 765 / 84 765** | **170 395 / 170 395** | **341 828 / 341 828** |
| fields at `endTime` (`U`, `p_rgh`, `alpha.fluid1`, `Cx`, `Cy`) | present | present | present |
| numerically-latest time dir == log's last `Time` | 1000 | 1000 | 1000 |
| **AGE GUARD** | all 5 fields at 1000 newer than `0/U` | same | same |
| **PLATEAU** (t=500 vs t=1000, tol 1e-6) | 2.737e-07 / 3.246e-07 | 2.923e-07 / 3.487e-07 | 3.036e-07 / 3.633e-07 |
| **INTERFACE STATIONARITY** (tol 1e-9) | **0** | **0** | **0** |
| **STREAMWISE INVARIANCE** (tol 1e-6) | **0** | **0** | **7.500e-13** |
| `adjustTimeStep` / `maxCo` / `maxAlphaCo` | yes / 1.0 / 1.0 | yes / 1.0 / 1.0 | yes / 1.0 / 1.0 |
| fvOptions markers (source WAS read) | 4/4 | 4/4 | 4/4 |
| mesh structure (cells, cells below interface) | 256 / 128, 8×32 | 1024 / 512, 16×64 | 4096 / 2048, 32×128 |

**THE CLAUSE-5 ADAPTATION HOLDS EXACTLY, NOT APPROXIMATELY.** `PREREGISTRATION` §6.1
replaced R1's `ExecutionTime count == endTime` — unsatisfiable under `adjustTimeStep
yes` — with `ExecutionTime count == Time count`. The two counts are **equal to the
unit at all three levels** (84 765; 170 395; 341 828, **MEASURED**), and this lane
re-derived them independently of the comparator by a line-anchored stream of each log
(`^Time = ` and `^ExecutionTime = `), getting the same three pairs. **The anchoring
matters: an unanchored `Time =` pattern also matches inside `ExecutionTime = ` lines
and would double every count.**

**THE LEXICOGRAPHIC HAZARD WAS LIVE AND THE COMPARATOR CLEARED IT.** At every level
`lexicographic_would_have_misread = True`: the written directories are `500` and
`1000`, whose lexicographic maximum is **`500`** and whose numeric maximum is
**`1000`** (**MEASURED**). A `sorted(glob)[-1]` reader would have graded the
half-time field at all three levels. The comparator sorts `key=float` and
cross-checks against the log's last `Time`.

Mesh, from `birth_certificate.json` (**TRANSCRIBED**): `mesh_ok true`,
`failed_checks 0`, max non-orthogonality **0.0**, max aspect ratio **2.0**, max
skewness 2.13e-14 / 2.84e-14 / 7.11e-14. **Mesh is not implicated in anything below.**

---

## 4. THE GRADE — THROUGH THE FROZEN COMPARATOR, EXACTLY AS §12 SPECIFIES

Invocation run, verbatim from `PREREGISTRATION` §12, unmodified:

```
python3 cases/ansys_verification/VMFL069-R2/grade_vmfl069_r2.py \
  --run-root verification/runs/ansys_verification/VMFL069-R2 \
  --out verification/runs/ansys_verification/VMFL069-R2/GRADING_VMFL069_R2.json
```

**Exit status 0** (**MEASURED**). It did not refuse. Full stdout captured at
`verification/runs/ansys_verification/VMFL069-R2/GRADING_STDOUT_2026-08-31T1455Z.txt`;
grading record at `.../GRADING_VMFL069_R2.json`.

**THE COMPARATOR MUTATED NOTHING.** Verified by mtime sweep after the run: the only
files in the run root newer than the grading start are the two the grading path
wrote. Every solver-written field at `L1/1000` still carries `2026-08-31T00:02:09Z`
and at `L3/1000` `2026-08-31T09:00:41Z` (**MEASURED**). The planted-zero control
plants into a `tempfile.mkdtemp` **copy** of the real bytes (`grade_vmfl069_r2.py:460`,
`:519`), never into the run's own files.

### 4.1 The three limbs

| limb | quantity | L1 | L2 | L3 (finest, the gated level) | reference | deviation at L3 | band | limb verdict |
|---|---|---|---|---|---|---|---|---|
| **A** | volume-mean `u_x`, lower layer (ν = 0.1), m/s | 10.059969190 | 10.026565232 | **10.012428204** | **10** exact | **0.124282 %** | 1.0000 % | **`PASS`** |
| **B** | volume-mean `u_x`, upper layer (ν = 0.02), m/s | 16.497029049 | 16.566392592 | **16.612663668** | **50/3** exact | **0.324018 %** | 1.0000 % | **`PASS`** |
| **C** | normalised L2 profile error, — | 0.0126401550 | 0.0067614720 | **0.0034959460** | **0** exact | **0.349595 %** | 1.0000 % | **`PASS`** |

All limb values **MEASURED**. References **REGISTERED** (`PREREGISTRATION` §5.1),
re-derived independently inside the comparator and cross-checked in `--selftest`.

### 4.2 The Roache triples — all three CONVERGING, and all three MONOTONE

`FS = 1.25`, `RATIO = 2.0`, `P_MIN = 0.05` (**REGISTERED**,
`grade_vmfl069_r2.py:80–82`). All **MEASURED**.

| limb | d21 | d32 | **R** | **state** | **observed order p** | **GCI_fine (relative)** | Richardson f_extrapolated |
|---|---|---|---|---|---|---|---|
| **A** | −0.033403958 | −0.014137028 | **0.423214** | **`CONVERGING`** | **1.240540** | **0.0012950 = 0.1295 %** | 10.002055221 |
| **B** | +0.069363542 | +0.046271076 | **0.667081** | **`CONVERGING`** | **0.584067** | **0.0069762 = 0.6976 %** | 16.705378427 |
| **C** | −0.005878683 | −0.003265526 | **0.555486** | **`CONVERGING`** | **0.848178** | **1.4591035 = 145.9103 %** | **−0.000584812** |

**Monotonicity, checked before any GCI is quoted** (`CLAUDE.md` rule 5: *never quote a
GCI when the three values are not monotone*): limb A decreases monotonically toward
the exact value from above, limb B increases monotonically toward it from below,
limb C decreases monotonically toward zero. Every `R` lies strictly in (0, 1) and
d21, d32 share a sign on every limb. **All three GCIs are therefore legitimately
quotable, and are quoted.**

**Rule 5 is ONE-WAY and it did not fire here.** No triple is `DIVERGENT`, `STAGNANT`,
`OSCILLATORY` or `EXACT`, and no `p` is below `P_MIN = 0.05`. The gate could only have
turned a `PASS` into `NOT A RESULT`; it had no occasion to.

### 4.3 THE ROW VERDICT AS THE FROZEN COMPARATOR RETURNED IT

> ## `PASS`

Worst limb governs; all three limbs carry the `PASS` ceiling ruled settled by
`ANSYS_VERIFICATION_CHARTER` §11.1 (**REGISTERED**, `PREREGISTRATION` §3.1), because
the reference is the **exact solution of the same continuum model the solver
discretises**, so model-form error is zero by construction and the residual is
discretisation error.

**This lane does not rule on the verdict and does not soften it.** It is reported as
the frozen instrument returned it, with §5 below stating in full what qualifies it.

---

## 5. THE THREE THINGS A READER MUST NOT MISS — STATED BEFORE ANYONE CELEBRATES

### 5.1 **LIMB C's GCI IS 145.91 % — IT IS LARGER THAN THE VALUE IT QUALIFIES, AND THE RICHARDSON EXTRAPOLATION IS NEGATIVE**

`GCI_fine = 1.459103` on a finest value of `0.003495946`. In absolute terms the
discretisation-uncertainty band is **±0.00510095** about a value of **0.00349595**
(**DERIVED** from the comparator's own MEASURED `gci_fine` and `f_fine`) — the band
is **1.459× the value it is attached to**.

**This is worse than the precedent the register already carries.** Row #44
(VMFL063) is written down as weaker than rows #42/#43 partly for a GCI of 120.62 %.
**Limb C's is 145.91 %.**

**And there is a second, independent tell that is arguably louder than the first:**
the comparator's own record gives limb C's Richardson-extrapolated value as
**`f_extrapolated = −0.0005848115`** (**MEASURED**,
`GRADING_VMFL069_R2.json:/limbs/C/triple/f_extrapolated`). **That is a NEGATIVE L2
error norm, which is impossible for the quantity it estimates.** A norm cannot be
below zero; the extrapolation has run past the physical floor of its own quantity.

**The honest reading, and its limits.** Limb C's reference is exactly **0**, and a
*relative* GCI on a quantity converging to zero inflates without bound as the value
shrinks — that is arithmetic, not evidence of a bad solve. **But it means limb C's
`PASS` is carried by the point value alone and its stated uncertainty does not
support it.** Two facts sit on the other side and are stated rather than suppressed:
the absolute band `0.003496 ± 0.005101` has an upper edge of **0.008597**, which is
still inside the frozen **0.01** band (**DERIVED**); and limb C's triple is genuinely
monotone and converging at `p = 0.848178`. **Neither fact makes a 145.91 % GCI
small, and this lane does not present them as if it did.**

### 5.2 **LIMB B's DEVIATION PLUS ITS OWN GCI EXCEEDS THE FROZEN BAND**

Deviation at L3 **0.324018 %**; GCI_fine **0.697621 %**; **sum 1.021639 %** against
the frozen band of **1.000000 %** (**DERIVED** from two MEASURED quantities).

**Limb B's point value is inside the band and the frozen gate — which tests the point
value, as registered — returns `PASS`. But limb B's `PASS` does not survive the
addition of its own discretisation uncertainty.** The GCI alone consumes **69.8 %**
of the band width. This lane does not change the verdict: the gate was frozen on the
point value before compute and `CLAUDE.md` rule 2 closed it at the freeze. **It is
recorded here because a credential that would not survive its own error bar should
say so on its face.**

Limb A, by contrast, is comfortable: deviation 0.124282 % + GCI 0.129501 % =
**0.253783 %**, a quarter of the band (**DERIVED**). Worth noting positively: limb A's
absolute GCI (**0.0129662**) slightly **exceeds** its absolute deviation from the
exact solution (**0.0124282**) — the exact answer lies **inside** limb A's own
uncertainty band, which is what a well-behaved GCI should do (**DERIVED**).

### 5.3 **THE PLANTED-ZERO CONTROL FIRED AT L1 ONLY — THE SAME WEAKNESS ROW #44 CARRIES**

`CLAUDE.md` rule 3 was satisfied, on **both** registered channels, and the refusal is
in the captured stdout. **But it was exercised at one level of three.**

**What actually ran on the graded path** (`grade_vmfl069_r2.py:1347–1350`, which
hard-codes `"L1"`):

| channel | file the plant was taken from | plant | read-back error | gate response | fired? |
|---|---|---|---|---|---|
| `U_x` | `L1/1000/U` (**256 cells**) | +0.666666666667 (sized, `K_PLANT_U × REF_WHOLE`, every internal cell) | **1.110e-15** | limb A moved by **exactly** the plant, 10.059969 → 10.726636, and **left the frozen band** (`band_inside_unplanted = True` → `band_inside_planted = False`); limb C's error rose 0.012640 → 0.046640 | **YES** |
| `alpha.fluid1` | `L1/1000/alpha.fluid1` (**256 cells**) | +0.05, every cell | **4.163e-17** | the interface-stationarity clause **REFUSED (exit 2)**: *"INTERFACE MOVED: max \|alpha − alpha_0\| = 0.05 at y = 0.0625, above the frozen 1e-09"* — line 1 of the captured stdout | **YES** |

All **MEASURED**, from `GRADING_VMFL069_R2.json:/planted_zero[0..1]`. Both plants were
**written to disk** (into a tempdir copy of the real solver bytes) and **read back
through the production readers** `read_internal_vector_x` / `read_internal_scalar` —
not through a parsed in-memory list, which is precisely the defect the register's
2026-08-28 addendum found in rows #42/#43.

**THE LIMITATION, NAMED PLAINLY:**

1. **The plant never touched L2 or L3.** The grading path plants at L1 only. **The
   readers that produced the L3 numbers the gate is actually decided on were never
   shown able to see a non-zero on L3's own bytes.** L3 is the gated level.
2. **No blind (negative) arm ran against the real data on the graded path.** The
   blind-writer arms exist and are green — this lane re-ran `--selftest` at grading
   time: **70 checks, 70 PASS, 0 FAIL, rc 0 under both `python3` and `python3 -O`**
   (**MEASURED**, matching §12's registered figure of 70 exactly), including *"planted
   zero REFUSES against a BLIND writer on the VELOCITY channel"*, the same on the
   ALPHA channel, and *"the blind-writer arm and the cardinality arm refuse for
   DIFFERENT reasons"*. **But those arms ran against SYNTHETIC fields under
   `/tmp/vmfl069_selftest_*/`, not against this run's bytes.**
3. **This is the row-#44 shape.** VMFL063's row is written down as weaker than
   #42/#43 because its plant fired at L1 only. **The same sentence is owed here, and
   it is not softened by the fact that both channels fired rather than one.**

What the L1 plant *does* establish, and it is not nothing: the reader/gate chain is
demonstrably sensitive on both independent channels, at a plant sized to cross the
frozen threshold rather than merely to be visible, with a gate-functional stage
(P1b) that refuses a plant the raw reader sees but the deciding clause does not.

---

## 6. THE COURANT DISCLOSURE — MEASURED FROM THE LOGS, GATING NOTHING

**The realised Courant number is UNMEASURED BY THE FROZEN GRADING PATH.** The
comparator gates on the controlDict's **declared** `maxCo == 1.0` and reads no
Courant number from the log — disclosed before compute at `PREREGISTRATION` §A1.5
clause 1, and ruled by the supervisor to stand. **The comparator was not changed and
is not to be changed.** Everything in this section was computed **outside** the frozen
comparator, by a streaming pass over each complete log, and **gates nothing**.

Probe artifact: `/…/scratchpad/vmfl069r2_courant.awk` (scratch — cited only as
disclosure; **no repository document depends on that path**, L-186). Logs streamed,
never loaded: 226 MB / 455 MB / 912 MB.

| | L1 (84 765 steps) | L2 (170 395 steps) | L3 (341 828 steps) |
|---|---|---|---|
| **convective Courant, max over the WHOLE run** | **1.174942652** at t ≈ 1.987 s | **1.172501395** at t ≈ 1.385 s | **1.140559048** at t ≈ 0.962 s |
| overshoot above the registered `maxCo = 1.0` | **+17.494 %** | **+17.250 %** | **+14.056 %** |
| **interface Courant, max** | **0** | **0** | **0** |
| **interface Courant, min** | **0** | **0** | **0** |
| **interface-Courant reports that were non-zero** | **0 of 84 765** | **0 of 170 395** | **0 of 341 828** |
| `Min(alpha.fluid1)` over the whole run | **0 exactly** | **0 exactly** | **0 exactly** |
| `Max(alpha.fluid1)` over the whole run | **1 exactly** | **1 exactly** | **1 exactly** |
| alpha reports with `Min ≠ 0` | **0 of 339 060** | **0 of 681 580** | **0 of 1 367 312** |
| alpha reports with `Max ≠ 1` | **0 of 339 060** | **0 of 681 580** | **0 of 1 367 312** |
| Phase-1 volume fraction, min and max | **0.5 / 0.5** | **0.5 / 0.5** | **0.5 / 0.5** |
| final `deltaT` | 0.011385631 s | 0.005662129 s | 0.002821957 s |
| largest `deltaT` taken | 0.295732475 s | 0.211636229 s | 0.148214459 s |

All **MEASURED**.

### 6.1 **THE REGISTRATION'S CENTRAL PHYSICAL ARGUMENT IS NOW TESTED OVER COMPLETE RUNS FOR THE FIRST TIME, AND IT HOLDS**

`PREREGISTRATION` §6.2 argues that with equal densities, zero surface tension and a
flat interface parallel to `U`, the alpha field is an exact steady state of the VOF
system and the wall-normal flux is identically zero — so the interface Courant should
be **identically zero**, not merely small.

**Over 596 988 time steps and 2 387 952 alpha reports across three complete runs,
the interface Courant was exactly 0 at every single step, and `alpha` was exactly 0
and exactly 1 at every single report, with zero departures at either bound.**

Before this, the claim was supported by **2 005 steps of L1 in a scratch probe, 5 %
of one level's physical time** (`PREREGISTRATION` §A1.3). It is now supported by three
complete solves at three mesh densities. **The bit-exactness survives mesh refinement**
— L3, with 16× the cells and 4× the steps of L1, is just as exactly zero.

**The contrast with R1 is the point of the whole R2 registration.** R1 held interface
Courant exactly 0 through step 64, then reached 141.7 at step 65, and `Min(alpha)`
reached **−2.37e23** by step 68 before `SIGFPE` (**TRANSCRIBED**, register row #45).
R2 never departs from 0 or from [0, 1] at any of 596 988 steps. **R1's blow-up was a
numerical CFL instability, not a physical two-layer instability** — `PREREGISTRATION`
§1 line 10 and §11 named both branches in advance and declined to predict which.
**Branch (a) is what happened**, and outcome 4 did not land.

### 6.2 The overshoot, and why it is not alarming

+17.5 % above the declared ceiling, and it is **expected OpenFOAM behaviour**:
`deltaT` for the next step is set from the *previous* step's Courant, so the realised
value overshoots while the field is still accelerating. Every level's maximum occurs
in the **first two seconds of a 1 000 s run** (**MEASURED**), i.e. in the startup
transient, and the overshoot *shrinks* with refinement (17.49 → 17.25 → 14.06 %).
Against R1's 1 802 → 2.87e9, the control is working as designed.

**Two honest notes.** First, the pre-freeze probe's figure of **1.17487** over L1's
first 2 005 steps was, it now turns out, **already the global maximum for the entire
L1 run** (whole-run max **1.174942652**, differing in the sixth significant figure) —
the probe's 5 % window happened to contain the peak, which was luck rather than
design, and is worth knowing before anyone trusts a 5 % window again. Second,
**nothing in this section gated anything.** A registration that wished to gate the
realised Courant would have to register the clause before compute; §A1.5 referred
exactly that to the supervisor for a future registration, and this record does not
convert a disclosure into a gate.

### 6.3 The registered `deltaT` asymptote, now measurable

`PREREGISTRATION` §8 registered `deltaT_∞ = Δx·maxCo/u_max = 0.011250 s` at L1;
§A1.4 declined to call it confirmed and bracketed it **0.01044 – 0.01176 s**
(**EXTRAPOLATED**, at the freeze). **Measured final `deltaT` at L1: 0.011385631 s** —
**inside the registered bracket**, and **+1.206 %** above the sec.8 formula figure
(**DERIVED**). §A1.4's refusal to write "confirmed" was the right call and the
formula is now corroborated to about 1 %.

---

## 7. RULE-12 CALIBRATION — ESTIMATE VERSUS ACTUAL

**Unit: core-minutes = wall_s × RANKS / 60. `RANKS = 1` (serial) at all three levels**
(**MEASURED**, `RUN_RC.*` and `COST.txt`).

### 7.1 The headline

| | core-min | source |
|---|---|---|
| **REGISTERED point estimate** | **822** | `PREREGISTRATION` §A1.1 table |
| **REGISTERED bracket** | **76 – 890**, 890 the conservative end | `PREREGISTRATION` §A1.1 |
| superseded drafting estimate (sec.8, pre-Amendment 1) | ~2 160 | `PREREGISTRATION` §8/§9 |
| **ACTUAL, MEASURED** | **549.2501** | `COST.txt` `total_core_min`; = Σ `RUN_RC.<level>` `core_min` |
| **REGISTERED cap** | **5 000** running total | `PREREGISTRATION` §9 |

> ### **RATIO actual / predicted = 549.2501 / 822 = 0.6682** (**DERIVED**)
> The run cost **two-thirds** of its registered point estimate. **The registered
> bracket 76 – 890 CONTAINED the answer**; the point estimate was **49.66 % high**.

Cap: **4 450.7499 core-min unspent**, **10.985 % of the cap used**, margin **9.10×**
(**DERIVED**). The cap never came near firing, and `endTime` was never reduced.

### 7.2 Per level — and the registered mechanism is CONFIRMED

| level | cells | REGISTERED est. (core-min) | **ACTUAL (core-min)** | **ratio** | wall (h) | ms/step | **µs/cell/step** |
|---|---|---|---|---|---|---|---|
| **L1** | 256 | 11.3 | **10.7667** | **0.9528** | 0.179 | 7.6211 | **29.770** |
| **L2** | 1 024 | 90.1 | **62.6167** | **0.6950** | 1.044 | 22.0488 | **21.532** |
| **L3** | 4 096 | 721.1 | **475.8667** | **0.6599** | 7.931 | 83.5274 | **20.392** |
| **total** | | **822** | **549.2501** | **0.6682** | 9.154 | | |

Estimates **REGISTERED**; actuals **MEASURED**; ratios and per-step figures **DERIVED**.

**§A1.1 PREDICTED THIS, IN WRITING, BEFORE COMPUTE, AND IT IS CONFIRMED.** The
amendment stated: *"an appreciable share of the L1 step is fixed per-step overhead …
which does not grow with cells — so linear extrapolation OVER-estimates L3."*

**Measured:** the per-cell-per-step cost **falls** with refinement, 29.770 →
21.532 → 20.392 µs (**DERIVED**), which is only possible if a fixed per-step term
dominates the small case. Fitting `per-step = a + b·cells` to L1 and L3 gives

> **`a` = 2.5606 ms fixed per step, `b` = 0.019767 ms per cell** (**DERIVED**)
> — the fixed term is **33.60 % of L1's step** and only **3.07 % of L3's step**.

The fit, built from L1 and L3 alone, predicts L2 at 22.8023 ms/step against a measured
22.0488 — **3.42 % high** (**DERIVED**), so the two-term model is a fair description
and the mechanism is real, not a curve fitted to two points.

Linear-in-cells extrapolation from L1's **measured** per-step cost over-predicts
**L2 by 38.26 %** and **L3 by 45.98 %** (**DERIVED**). **The over-estimate grows with
level, exactly as registered.**

### 7.3 Attribution of the 272.75 core-min gap — three named causes, no residue

| cause | share | evidence |
|---|---|---|
| **1. MISPREDICTION — linear-in-cells scaling** (the assumption §A1.1 flagged as unmeasured) | **~264 core-min**, essentially all of it: L2 27.48 + L3 245.23 = **272.71 core-min** of the 272.75 total gap | the fixed-overhead fit above; ratios 0.695 and 0.660 versus L1's 0.953 |
| **2. MISPREDICTION — the L1 anchor**, two errors of similar size in opposite directions | **0.53 core-min** (L1 only) | the probe's **wall** figure of 7.97 ms/step over-predicted the realised 7.6211 by 4.38 %, while the probe's **CPU** figure of 7.28 ms/step under-predicted the realised CPU 7.5987 by 4.38 % (**DERIVED**) |
| **3. STEP-COUNT EXTRAPOLATION** | **≈ 0**, it was nearly exact | see §7.4 |
| **CONTENTION** | **≈ 0 — and this is a correction to the registered expectation** | see §7.5, named separately and **never absorbed into the ratio** |
| **WASTE** | **0 core-min** | see §7.6, named separately per `COMPUTE_BUDGET_CHARTER` §6 |

### 7.4 The step-count predictions — the probe's extrapolation was nearly exact; the formula was not

| level | **REGISTERED / EXTRAPOLATED prediction** | **MEASURED** | error of the prediction |
|---|---|---|---|
| L1, `PREREGISTRATION` §8 formula | **≈ 88 900** (REGISTERED) | **84 765** | **+4.878 % high** |
| L1, §A1.1 probe anchor | **84 817** (EXTRAPOLATED) | **84 765** | **+0.061 % high** |
| L2, §A1.1 | **169 634** (EXTRAPOLATED) | **170 395** | −0.447 % low |
| L3, §A1.1 | **339 268** (EXTRAPOLATED) | **341 828** | −0.749 % low |

**§A1.4's honest bracket for L1 was 82 182 – 91 825; the measured 84 765 is inside
it.** The probe-anchored 84 817 landed within **52 steps** of the truth — better than
the bracket's width by two orders of magnitude, which is fortunate rather than
demonstrated, and §A1.4 was right to refuse to call it confirmed.

**A small registered assumption is falsified and it does not matter.** §A1.1 assumed
steps **double exactly** per level. Measured ratios: **L2/L1 = 2.01020**, **L3/L2 =
2.00609** (**DERIVED**). Steps grow slightly *faster* than 2×, contributing about
+0.75 % to L3's cost — a rounding error against the 46 % scaling misprediction, but
recorded because it is a registered assumption that did not hold exactly.

### 7.5 Contention — MEASURED over the whole run, and it corrects the launch-time snapshot

`CONTENTION.txt` sampled at launch reads `loadavg 7.56 8.54 13.02` on `nproc 16` with
**6 `simpleFoam` processes live** (**TRANSCRIBED**). That snapshot predicts inflated
wall time. **It did not materialise, and the logs measure it directly** — final
`ExecutionTime` (CPU) against final `ClockTime` (wall):

| level | CPU (s) | wall (s) | **wall/CPU** | inflation |
|---|---|---|---|---|
| L1 | 644.10 | 646 | **1.00295** | **+0.295 %** |
| L2 | 3 754.75 | 3 757 | **1.00060** | **+0.060 %** |
| L3 | 28 549.64 | 28 552 | **1.00008** | **+0.008 %** |

All **MEASURED**. **Contention over the graded runs is effectively nil** — at most
0.295 %, on the shortest level, falling to 0.008 % on the level that dominates the
bill. Compare the pre-freeze probe, which ran at `loadavg 36.88` with a wall/CPU ratio
of **1.0948** (**TRANSCRIBED**, §A1.1) — a 9.5 % inflation the amendment deliberately
carried into its projection as conservatism. **That conservatism is a real and
identified component of the L1 over-estimate**, and it is named here rather than
absorbed into the ratio, per `COMPUTE_BUDGET_CHARTER` §6.

**The rule-12 stall heuristic is cleared by measurement, not by assertion.** Rule 12
says a row over 3 600 wall s is a stall; **L2 (3 757 s) and L3 (28 552 s) both exceed
it.** Neither is a stall: a stalled process shows wall ≫ CPU, and these show wall/CPU
of 1.00060 and 1.00008 — the processes were computing for essentially every second
they were alive. Both are legitimate single continuous solves.

### 7.6 Waste, named separately and never absorbed

> **WASTE WITHIN VMFL069-R2: 0 core-min** (**MEASURED**).

Nothing was computed and discarded. Three levels launched, three completed, `rc = 0`
at each, no restart, no re-mesh, no abandoned partial. `overall_rc = 0`,
`smoke_mode = no` (**TRANSCRIBED**, `COST.txt`).

Two adjacent items, named because they are real and neither is R2 solver spend:

1. **The pre-freeze scoping probe** (L1, 2 005 steps, scratch) bought the measured
   cost basis of §A1.1. **Its cost is NOT MEASURABLE now: the scratch directory is
   gone** — this lane looked and it is not on disk. Recorded as **NOT MEASURED**, not
   estimated. (This is L-186 behaving exactly as the lesson says: the scratchpad was
   wiped, and had any repository document depended on that path it would now be
   broken. None does.)
2. **5 h 53 m of grading latency, not compute waste.** The run finished unattended at
   `2026-08-31T09:00:42Z`; grading began at `2026-08-31T14:53:28Z` (**MEASURED**),
   after a session limit killed the fleet at ~00:55Z and the box rebooted at 14:35Z.
   **No compute was lost and no artefact was damaged** — the solver had finished
   5 h 34 m before the reboot, and every field, log and `RUN_RC` survived intact.
   It is a scheduling finding, not a spend, and it is not folded into any ratio.

### 7.7 Dollars — DERIVED, NEVER MEASURED

Rate **$0.0513/core-h**, c7a.4xlarge, **REPORTED-BY-OWNER** (Sanaa, 2026-08-21/22).
**The box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER` §5), so every
dollar figure here is **DERIVED**, not measured.

| | core-min | core-h | **$ DERIVED** |
|---|---|---|---|
| **actual** | 549.2501 | 9.154168 | **$0.46961** |
| registered estimate | 822 | 13.70 | $0.70281 |
| registered cap | 5 000 | 83.33 | $4.27500 |

Well inside the under-$25 pre-authorisation. CPU only; **no GPU**, so the 2026-08-21
blanket applies and nothing here touches the separate GPU regime.

---

## 8. WHAT THIS LANE DID NOT VERIFY — stated plainly, not presumed

- **The manual's Figure .69.2 was never read, digitised or compared against.** No
  statement in this record is a comparison with Ansys, and none is a statement about
  Ansys. The box has no Ansys solver.
- **Marchandise & Remacle (2006) is not on this box and was not read.** It is named
  for provenance only, exactly as the registration says.
- **The plant was not exercised on L2 or L3 bytes** (§5.3). This lane did **not**
  construct an out-of-comparator plant on L3 to fill that gap: doing so would be
  grading through an instrument that is not the frozen one, and §5.3 reports the gap
  rather than papering over it.
- **The realised Courant gates nothing** (§6). It is a disclosure computed outside the
  frozen comparator, and this lane did not and will not convert it into a gate.
- **`ExecutionTime` is OpenFOAM's own CPU accounting, not an independent measurement
  of CPU time.** §7.5's contention figures inherit whatever bias that accounting has.
- **Whether the case has a stable laminar steady state at these parameters beyond
  `t = 1000 s`** is not established by anything here. Three runs reached `t = 1000`
  with a bit-exactly stationary interface; that is what is claimed, and nothing more.
- **This lane did not rule on the verdict.** The `PASS` above is what the frozen
  instrument returned. The supervisor rules.

---

## 9. ARTIFACT PATHS — every number above cites one of these

| artifact | path |
|---|---|
| grading record (JSON) | `verification/runs/ansys_verification/VMFL069-R2/GRADING_VMFL069_R2.json` |
| comparator stdout, captured | `verification/runs/ansys_verification/VMFL069-R2/GRADING_STDOUT_2026-08-31T1455Z.txt` |
| comparator `--selftest`, 70/70 | `verification/runs/ansys_verification/VMFL069-R2/SELFTEST_2026-08-31T1500Z.txt` |
| cost / contention / status | `.../COST.txt`, `.../CONTENTION.txt`, `.../STATUS.VMFL069-R2` |
| completion records | `.../RUN_RC.L1`, `.../RUN_RC.L2`, `.../RUN_RC.L3` |
| solver logs (226 / 455 / 912 MB) | `.../L1/log.interFoam`, `.../L2/log.interFoam`, `.../L3/log.interFoam` |
| mesh birth certificates | `.../L{1,2,3}/birth_certificate.json` |
| frozen pre-registration | `cases/ansys_verification/VMFL069-R2/PREREGISTRATION.md` (`7c209caf…`) |
| frozen comparator | `cases/ansys_verification/VMFL069-R2/grade_vmfl069_r2.py` (`8e0b4c3f…`) |
| frozen launcher | `cases/ansys_verification/VMFL069-R2/run_vmfl069_r2.sh` (`f03d771e…`) |
| draft register row (**NOT LANDED**) | `.../DRAFT_REGISTER_ROW.md` |
| draft calibration row (**NOT LANDED**) | `.../DRAFT_CALIBRATION_ROW.md` |
