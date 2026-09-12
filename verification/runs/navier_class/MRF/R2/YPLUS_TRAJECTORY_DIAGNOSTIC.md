# MRF R2 ET8000 — y+ TRAJECTORY ACROSS THE FAMILY — **DIAGNOSTIC ONLY**

> 🔴 **THIS CHANGES NO GATE, NO THRESHOLD, NO BAND AND NO LABEL.** The triple
> prestatement is frozen at `5c6869f7` and `grade_triple_r2.py` (blob `b3758cc5…`) is the
> grader. **Nothing in this file goes near the grading path.** Rule 5 governs the verdict:
> a triple that is not `CONVERGING` is `NOT A RESULT` whatever the y+ says, and a
> `CONVERGING` triple is not retroactively condemned or rescued by it. This is context
> reported **beside** a verdict, never folded into one. **No verdict is issued here.**

**Status: TWO OF THREE LEVELS. `fine` was still solving when this was written (iteration
~6,700 of 8,000) and is NOT measured here.** The trajectory is the whole claim and a
two-point trajectory is a line through two points; **fine is what makes it a trajectory.**

---

## 1 — THE HYPOTHESIS, AND ITS FALSIFIER, FIXED BEFORE THE NUMBERS EXISTED

Raised by the cfd-supervisor 2026-09-12. Falsifier committed at **01:05Z, before any
`yPlus` artifact existed anywhere in the ET8000 tree** — verified by `find`, which returned
nothing; **nobody had ever looked.**

**Hypothesis.** MRF R2 uses `nutkWallFunction` — a **high-Re** wall function — on a family
with **no prism layers** (`addLayers false`, empty `layers {}`), so the first cell height is
set by the local hex and **shrinks with refinement**. If y+ then crosses `nutkWallFunction`'s
own switch at `yPlusLam` (the linear/log intersection, **≈ 11.53** at κ = 0.41, E = 9.8), the
wall-shear model is answering a different question at each level, and a force coefficient
computed under it has no reason to converge monotonically. Three DIVERGENT triples stand
behind it: R1b, MRF R1 (observed order −5.2311), MRF R2 at 4000 (−5.7784); and
`SUBOFF_A1_PREREGISTRATION.md` §1.2 diagnosed this exact mechanism elsewhere, in its own
words — *"high-Re wall functions on a family that refines y+ from 25 to ~11"*.

**The three registered falsifiers, verbatim from the pre-commitment:**

- **(L1) PREMISE FALSE** — y+ does not fall monotonically coarse → medium → fine.
- **(L2) NO REGIME CHANGE** — patch-average stays above ~30 at all levels and **no level has
  a material fraction of wall faces below `yPlusLam` ≈ 11.53**.
- **(L3) MOVEMENT TOO SMALL TO MATTER** — patch-average moves < ~30 % across the family and
  stays on one side of `yPlusLam`.

It **survives** (survives, *not* is confirmed) only if the family **straddles** `yPlusLam`:
fractions below 11.53 growing materially with refinement.

---

## 2 — THE MEASUREMENT (observation of the output, not input wearing units)

`simpleFoam -postProcess -func yPlus -time 8000` against each **completed** level, run
`nice -n 19` so it did not compete with the live fine solve. rc 0 both. **The six fields the
frozen grader reads (`U p k omega nut phi` at `8000`) carry byte-identical mtimes before and
after** — checked, not assumed; the post-process added `8000/yPlus` and `log.yPlus` and
touched nothing else.

**PROVENANCE, stated because it is the difference between evidence and arithmetic:** every
number below is computed by OpenFOAM from the **solved** `U` and `nut` fields of a completed
run. **Nothing here is derived from the dict, the cell size or the Reynolds number.** The
one figure that is *not* an observation is `yPlusLam ≈ 11.53`, which is the wall function's
own analytic switch constant — a property of the model, labelled as such.

### 2.1 — Per-patch y+ (min / average / max)

| patch | coarse min/avg/max | medium min/avg/max | avg change |
|---|---|---|---|
| tankWall | 3.415 / **131.84** / 485.35 | 2.070 / **78.80** / 375.03 | **−40.2 %** |
| tankBottom | 2.393 / **105.25** / 232.39 | 2.342 / **65.09** / 155.75 | **−38.2 %** |
| tankLid | 0.306 / **43.65** / 153.57 | 0.566 / **35.99** / 106.48 | −17.5 % |
| baffles | 3.060 / **58.19** / 312.21 | 1.502 / **28.12** / 192.34 | **−51.7 %** |
| **shaft** ★ | 3.251 / **25.41** / 62.21 | 1.291 / **21.30** / 63.21 | −16.2 % |
| **impeller** ★ | 4.086 / **37.68** / 89.74 | 5.326 / **25.41** / 62.43 | **−32.6 %** |

★ = the only two patches that enter the graded quantity (§3).

### 2.2 — Fraction of wall faces BELOW `yPlusLam` = 11.53 — the sharp test

A minimum can be one face. The fraction is the quantity the hypothesis is actually about.

| patch | faces (c / m) | **coarse frac** | **medium frac** | factor |
|---|---|---|---|---|
| tankWall | 3,168 / 9,752 | 3.31 % | 6.49 % | ×1.96 |
| tankBottom | 920 / 2,313 | 0.76 % | 2.46 % | ×3.24 |
| tankLid | 1,120 / 2,720 | 13.75 % | **10.00 %** | **×0.73 — FALLS** |
| baffles | 2,400 / 6,080 | 3.25 % | **15.16 %** | ×4.66 |
| **shaft** ★ | 2,236 / 3,024 | 4.34 % | **25.00 %** | **×5.76** |
| **impeller** ★ | 7,984 / 21,368 | 0.25 % | 1.14 % | ×4.56 |

---

## 3 — SCORING THE THREE FALSIFIERS, ON TWO LEVELS

- **(L1) NOT TRIGGERED.** Every patch average falls from coarse to medium. The premise holds.
- **(L2) NOT TRIGGERED.** Five of six patches have a materially growing fraction below
  `yPlusLam`, and **one quarter of the shaft's wall faces are in the viscous branch at the
  medium level.** This is not a boundary effect at a single face.
- **(L3) NOT TRIGGERED.** Averages move 16–52 %; fractions move ×2 to ×5.8.

**The hypothesis therefore SURVIVES on two levels. It is NOT confirmed.** A surviving
hypothesis is one that has not yet been killed.

**One honest counter-current, reported rather than dropped:** `tankLid`'s fraction below
`yPlusLam` **falls**, 13.75 % → 10.00 %, against the trend on every other patch. It is a
slip lid with `zeroGradient` on `nut`, so it is the least representative wall in the model —
but the hypothesis predicts a direction and one patch goes the other way, and that is stated.

---

## 4 — A BOUND THE FALSIFIERS DID NOT ANTICIPATE, AND IT CUTS AGAINST THE HYPOTHESIS

**This is the most important section in this file, and it weakens the mechanism I was
asked to test.**

The graded quantity is `Np`, derived from `total_z` of the `impellerForces` function object,
whose definition reads `patches (impeller shaft)` — **read from the case's own
`system/controlDict`, not assumed.** So `baffles` and `tankWall`, which carry the largest y+
movement in §2, **do not enter the graded number at all.** Of the two patches that do, the
impeller's fraction below `yPlusLam` is **0.25 % → 1.14 %** — small in absolute terms.

And the decisive figure. A wall function sets the **wall shear stress**, which is the
**viscous** part of the moment. Measured at `endTime` 8000 from `moment.dat`:

| level | `total_z` | `pressure_z` | `viscous_z` | **viscous share of the graded moment** |
|---|---|---|---|---|
| coarse | −0.166520 | −0.165945 | −0.000575 | **0.345 %** |
| medium | −0.170000 | −0.169772 | −0.000229 | **0.134 %** |

> **THE DIRECT CHANNEL BY WHICH THE WALL FUNCTION REACHES THE GRADED QUANTITY IS UNDER
> HALF A PERCENT OF IT, AND IT HALVES BETWEEN LEVELS.** The coarse→medium change in `Np` is
> **+2.09 %** (`0.170000 / 0.166520`, matching the prestatement's 4.193491 → 4.281132).
> **Even annihilating the entire viscous moment would move `Np` by 0.345 %, about one sixth
> of the observed level-to-level change.** The regime-change mechanism **cannot account for
> the divergence through its direct channel.**

**What survives of it, stated precisely and not inflated.** The wall function also sets
`nut` at the wall, which feeds `k` and `ω` and therefore the turbulence field, and the
turbulence field sets the blade **pressure** distribution — which is 99.7 % of the graded
moment. That indirect path is **not bounded by 0.345 %** and is **not measured by anything
in this file.** So the hypothesis is not refuted; it has been **moved off the channel that
was easy to check and onto one that is not**, and it now owes a measurement it did not owe
before.

**A second observation that is interesting and is NOT evidence for the hypothesis:** the
viscous share itself falls by a factor of 2.6 between levels. That is a large relative change
in exactly the component the wall function sets — consistent with a non-level-invariant wall
treatment — but it is equally consistent with a thinner resolved near-wall region simply
carrying less modelled shear. **Two explanations, one observation, and this file does not
choose between them.**

---

## 5 — WHAT IS AND IS NOT ESTABLISHED

**Established:** the configuration that produced a diagnosed divergence elsewhere is present
here; it *does* move y+ materially across this family; five of six patches move the
predicted way; and **nobody had measured any of it before 2026-09-12** — the first `yPlus`
artifact in this tree was created by this diagnostic.

**NOT established:** that this is the cause of the MRF divergence. The direct channel is
bounded at 0.345 % against a 2.09 % effect (§4), and the indirect channel is unmeasured.

**OWED, and cheap:** fine's y+ when it lands — the same `-postProcess -func yPlus`, no solve.
Fine is where the hypothesis is decided, because a two-point trajectory is a line.

**A cost note (rule 12):** this diagnostic cost **0.567 core-min** measured — coarse 9 wall s
+ medium 25 wall s, 1 rank, `nice -n 19` — = **$0.0005 DERIVED, NEVER MEASURED** at
$0.0513/core-h. No solve was run; both levels were already complete.

*— cfd `lab-lane`, 2026-09-12. DIAGNOSTIC. No gate moved. No verdict issued.*

---

## 6 — 2026-09-12, ADDED AFTER SUPERVISOR REVIEW: THE DEBT, NAMED WITH THE MEASUREMENT THAT WOULD SETTLE IT

**Still diagnostic. Still no gate, threshold, band or label moved. Still no verdict.**

The cfd-supervisor **independently re-derived** every decisive figure in §4 from the
artifacts — `patches (impeller shaft)` from the case's own `controlDict`; viscous shares
0.3451 % and 0.1345 %; Np change +2.0899 %; annihilation ÷ observed = **0.165** — and
**accepted that the direct channel is bounded out.** They also ran a cross-check this file
did not claim: the prestatement's own 4.193491 → 4.281132 is **+2.0899 %, agreeing with the
`moment.dat` route to four decimal places**, so the quantity measured here is the quantity
the gate grades, by two independent paths.

### 6.1 — The rule this episode produced [lab-attributed, cfd-supervisor, 2026-09-12]

> **WHEN A HYPOTHESIS SURVIVES ONLY ON A CHANNEL THAT WAS NOT MEASURED, THE RECORD STATES
> THE DEBT AND NAMES THE MEASUREMENT THAT WOULD SETTLE IT** — otherwise "not refuted"
> launders into "supported".

A hypothesis that survives by relocating to an unmeasured channel is **weaker than it was,
not equal**, even though nothing refuted it: the surviving version is the version nobody has
tested. **The caveat this lane attaches, and asks be kept with the rule:** the rule is worth
only what the debt-naming costs. A debt recorded as "more work needed" launders exactly the
way "not refuted" does. It is real here **only because a specific measurement against a
specific threshold is named below.**

### 6.2 — THE DEBT

**The surviving path:** `nutkWallFunction` sets `nut` at the wall → feeds `k` and `ω` →
sets the turbulence field → sets the blade **pressure** distribution, which is **99.7 % of
the graded moment.** Nothing in this file measures it.

**THE MEASUREMENT THAT WOULD SETTLE IT.** Solve **one** level — same mesh, same `endTime`,
same ranks, same everything else — with **`nutUSpaldingWallFunction`** (all-y+) substituted
for `nutkWallFunction`, and test whether `Np` moves by **more than 0.345 %**, the measured
size of the entire direct channel.

- **Moves by more than 0.345 %** → the wall treatment reaches the **pressure** field, the
  indirect path is real and measured, and the hypothesis is alive on a channel that can
  carry the observed 2.09 %.
- **Does not** → the hypothesis is **dead on both channels** and MRF's divergence needs a
  different explanation entirely.

The threshold **0.345 %** is not invented for this experiment: it is the measured viscous
share at coarse, i.e. the largest effect the direct channel could possibly have. It must be
**frozen in a pre-registration BEFORE the solve**, with its own cost, under rule 2.

This substitution is **not a bespoke rescue** for the hypothesis: `SUBOFF_A1_PREREGISTRATION.md`
§1.2 already adopted the identical change, for the identical stated reason, on a different
family.

### 6.3 — NOT STARTED, AND DELIBERATELY SO

**No solve was launched for this.** The cfd-supervisor's instruction is explicit: MRF's
triple lands first, the box is saturated (load ~60 on 16 vCPU), and the experiment needs its
own registration with the threshold frozen before compute. **Recorded as owed, not begun.**

### 6.4 — A DEFECT IN THIS LANE'S OWN WATCHER, RECORDED BESIDE THE DIAGNOSTIC IT ALMOST DERAILED

At **01:09:22Z** this lane's landing-watcher reported a **FATAL SIGNATURE** on fine. It was
a **FALSE ALARM CAUSED BY THE WATCHER'S OWN FILTER**, and it is recorded here because the
general form is the same defect this file's §5 neighbours already carry.

Triaged rather than inferred: the solver was **healthy** — `mpirun` 2200471 and all six
ranks alive, launcher 2199207 alive, iteration advancing 6,777 → 6,780 across a 30 s
observation, residuals normal, no `rc`. **The only match in the entire log, at line 29:**

```
trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
```

That is OpenFOAM's **startup banner announcing the guard is ENABLED**, not the guard firing.
The filter was `FOAM FATAL|Floating point exception|signal`. A corrected filter —
`^FOAM FATAL`, `sigFpe::sigHandler`, `sigSegv::sigHandler`,
`mpirun noticed that process rank`, `Foam::error::printStack` — returns **zero** matches on
the same file.

**THE GENERAL FORM, which is the same one the A1.7 `controlDict` banner exhibits:**

> **A grep-based check reads whatever text matches, and TEXT THAT DESCRIBES A CONDITION IS
> NOT THE CONDITION.** A config comment reading `endTime 50` over a real `endTime 8000`, and
> a log banner reading "Floating point exception" over a run with no exception, are **the
> same bug in two file classes.**

The `controlDict` case is the more dangerous of the two: it fails toward a **FALSE FAILURE
on a healthy run**, and rule-4 failures are precisely where a reader is trained to believe
the instrument over the run. This one failed toward a false alarm that cost two minutes of
triage. **Both are docketed.**

*— cfd `lab-lane`, 2026-09-12, §6 added after supervisor review. No gate moved. No verdict issued.*
