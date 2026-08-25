# F12 grading record — RAE 2822, AGARD AR-138 Case 9

**Graded 2026-08-25 by a `lab-lane` worker for the cfd team, on a
supervisor-directed ZERO-COMPUTE task.** No solver was launched, no mesh was
built and no case directory was created in producing this record. Every number
below was read from an artifact on disk by this lane and re-derived here; where
a figure could **not** be reproduced, this record says so in those words rather
than repeating it.

Frozen pre-registration: `verification/campaign/F12_PREREGISTRATION.md`,
**v1.2, blob `41ec748a06b513414101dca9780107f08a25ddec`**, read from the HEAD
blob (`git show HEAD:`), not from the worktree. Gates are **CLOSED** — F12 has
fired, so nothing in this record alters a gate, threshold, cap or label
(CLAUDE.md rule 2).

---

## 0. THE VERDICT AND THE TIER, SIDE BY SIDE

| | **VERDICT** | **TIER** |
|---|---|---|
| **F12** | **`GATE FAIL`** | **`NOT HELD`** |
| **Grades** | what the **gate** did | what the **case establishes for the lab** |
| **On what** | admission gate A at **all three** mesh levels, and admission gate B | the case establishes nothing about RAE 2822 Case 9; it establishes a **fact about its own ladder** |
| **Vocabulary** | CLAUDE.md rule 1; `VERIFICATION_CHARTER.md` §2 | Sanaa, 2026-08-25, quoted verbatim in `docs/campaigns/T-family/THERMAL_TIERING_DIRECTIVE.md` §1 |

**These are two different vocabularies and they are never conflated.** They
overlap at exactly one word — `GATE REACHED` — and nowhere else. Both are
written here, side by side, as the directive requires. The directive is written
down by the heat-transfer team and owned by them; **Sanaa's own sentence quoted
in its §1 names the cfd team**, which is why F12 carries a tier at all.

**The tier does not flatter the verdict.** It is not `SURVEYED` — the evidence
here is *gated*, not breadth. It is not `GATE REACHED` — that word names a row
missing **exactly one** of V / G / P, and this row's admission gate failed
outright, so no V, G or P column was ever opened. `NOT HELD` is the honest FAIL
and it is recorded rather than skipped (directive §3.2).

**Spend on F12, complete:** **0.4617 core-min MEASURED** (27.7 s driver wall ×
1 rank ÷ 60), **$0.000395 DERIVED, NOT MEASURED** at $0.0513/core-h
(c7a.4xlarge, reported-by-owner; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5). That is **0.38 % of the frozen 120 core-min
cap** for rung 1. The calibration row is **`C-50`** in
`docs/COST_CALIBRATION.md` and is not restated here.

---

## 1. WHAT WAS FIRED

**Rung 1 only** — `coarse_workshop_M0.734_a2.79`, the pre-registration's
designated rate-calibration rung (2026-08-23 COSTED ADDENDUM §5). Launched
**2026-08-25T01:03:06.630Z**, aborted itself **01:03:34.350Z**
(`verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/result.json`,
`started_utc` / `ended_utc`). Commits `cd1ac21a` (the rung) and `6b462592`
(the three-level mesh audit).

**Rungs 2, 3, 4 and 5 were never launched** and their run directories do not
exist. F12 is now **FIRED**; nothing further launches on this pre-registration.

### 1.1 The freeze held, and this is worth stating positively

Rule 2 requires that the frozen file **is** the file that ran, verified by hash.
The driver `verification/runs/F12_runs/run_f12_rung.py` records the blobs it ran
against, and **all four still resolve at HEAD**, verified by this lane with
`git rev-parse HEAD:<path>`:

| what | blob recorded in `result.json` | HEAD |
|---|---|---|
| `verification/campaign/F12_PREREGISTRATION.md` | `41ec748a06b513414101dca9780107f08a25ddec` | identical |
| `sdk/workflows/rae2822_case9.py` | `a18314f77160b7a58f443073850a44b4d8fada7d` | identical |
| `sdk/workflows/tmr_verification.py` | `404ce4323127d1cb24836d67720d94ba9f5d401e` | identical |
| `scripts/roache_triple.py` | `8dee0d31e94d3f59d28658f88a4cd6df80ae8e39` | identical |

**And the three pre-launch blockers the frozen MESH-SIMILARITY AMENDMENT §7
named were all closed before first compute**, in commit order:

1. `03c35817`, **2026-08-25T00:23:00Z** — the amendment itself (pre-compute, legal).
2. `b0c0db35`, **2026-08-25T00:38:46Z** — the grading-path repair: per-level
   first cell threaded through `build_case`/`run_case`/`blockmesh_dict`, and the
   `r_y_far` branch flip of amendment §5 closed. **ZERO COMPUTE.**
3. **01:03:06Z** — first compute, 24 minutes after the repair was committed.

The built ladder confirms the repair took effect. From
`verification/runs/F12_runs/mesh_audit_2026-08-25/mesh_audit.json`, the
per-level wall-normal first cell is **2e-06 / 1e-06 / 5e-07 chord** and the
wake-outlet first cell **0.3 / 0.15 / 0.075 chord**; the wall-normal total
expansion ratios are **4.4011e6 / 4.5989e6 / 4.7020e6**, matching the
amendment's own "similar family" column to five figures, and the far-side
ratios are **3.7472 / 3.7527 / 3.7555** instead of the amendment §5's
3.747 / 1.084 / **1.000** branch flip. **The ladder that fired is the
geometrically similar, coarse-anchored ladder the amendment resolved to.**

This matters for reading everything below: **the gate-A failure is not an
artifact of an unrepaired ladder.** The repaired, similar ladder fails gate A
at every level.

---

## 2. ADMISSION GATE A — MESH — `GATE FAIL` AT ALL THREE LEVELS

Frozen threshold (§"Gates, declared now"): *max non-orthogonality <= 70 degrees
and max skewness <= 4, boundary faces included, per
`docs/standards/MESH_STANDARD.md`. Aspect ratio is advisory there and is
recorded with its alignment justification, not gated.*

Read by this lane from three real `checkMesh` logs, OpenFOAM v2606
(`_481094f-20260618`), under
`verification/runs/F12_runs/mesh_audit_2026-08-25/<level>/log.checkMesh`:

| level | cells built | **max non-orthogonality** | faces > 70° | max skewness | max aspect ratio (advisory) | gate A |
|---|---|---|---|---|---|---|
| coarse | 23,040 | **70.64625857** | 892 | 0.8270270496 | 10,606.65276 on 16 cells | **`GATE FAIL`** |
| medium | 92,160 | **70.86145203** | 3,598 | 0.8273655771 | 962.7865634 | **`GATE FAIL`** |
| fine | 368,640 | **72.54215374** | 14,399 | 0.8273339689 | 2,767.113299 on 25 cells | **`GATE FAIL`** |

**The breach is on non-orthogonality alone. Skewness passes with 4.8× margin at
every level.** The coarse mesh in the audit tree is byte-identical in its
quality figures to the mesh the solver actually ran on
(`verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/log.checkMesh`:
70.64625857, 892 faces, skewness 0.8270270496, aspect ratio 10,606.65276) — the
audit graded the same mesh, not a lookalike.

**The failure WORSENS UNDER REFINEMENT.** Non-orthogonality rises
70.646 → 70.861 → **72.542** and the count of severely non-orthogonal faces rises
**892 → 3,598 → 14,399**, i.e. ×4.03 and ×4.00 — the offending faces are a fixed
*fraction* of the mesh, not a fixed *set*. This is a property of the block
topology and the wall-normal grading recipe, and refinement does not cure it.

**The consequence is the primary finding of this record.** §"Gates, declared
now" grades Gates 1–4 *"on the finest mesh at the workshop condition"*. **The
fine mesh fails gate A by 2.54°.** **F12 has no admissible mesh anywhere in its
ladder** — not the one that ran, not the one it would have been graded on, not
the one in between.

**This finding does not depend on the solve.** It was measured on three
`checkMesh` logs from three built meshes, independently of any solver, and it
would stand unchanged had rung 1 completed cleanly.

**Two honest qualifications.**

- **checkMesh's own verdict disagrees with the lab's gate, and the lab's gate is
  the stricter one.** Each log prints `Non-orthogonality check OK.` because
  checkMesh's own pass threshold is 80°, and the medium log prints `Mesh OK.`
  outright. The lab gates at **70°** (`MESH_STANDARD.md` §3.1, hard gate 70,
  warning band 65–70). A reader who takes `Mesh OK.` at face value would grade
  this ladder admissible. It is not.
- **Aspect ratio is advisory and is not a lone rejection** (`MESH_STANDARD.md`
  §3.3). But that section also says *"aspect ratio above 1000 together with
  non-orthogonality above 60 degrees or skewness above 2 is a flag for
  investigation"*, and this ladder trips both halves at coarse and fine
  (10,606 / 2,767 with max non-orthogonality 70.6 / 72.5). **The flag is
  recorded as tripped at the mesh level. This lane did NOT verify that the
  high-aspect-ratio cells and the >60° faces are the same cells** — that
  co-location was not measured and is not claimed.

---

## 3. ADMISSION GATE B — CONVERGENCE — `GATE FAIL`

Frozen threshold: *The solver must print its own convergence statement. A small-
looking residual is not a substitute (LESSONS L-14, L-15). A run that does not
converge is not a result and is not graded.*

`rhoSimpleFoam` **aborted at iteration 180 of the registered 6,000 (3.0 %)**
with

> `--> FOAM FATAL ERROR: (openfoam-2606)`
> `Negative initial temperature T0: -1.72234834`

raised from `thermoI.H:57`
(`verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam`;
the same text is preserved inside git in `result.json`'s `traceback` field,
because the log itself is gitignored).

**No convergence statement exists.** The frozen grading path's own detector is
`solver_converged(log_text)`, which tests for the literal string
`"SIMPLE solution converged"` (`sdk/workflows/rae2822_case9.py`). That string
occurs **zero** times in the log; the single `converg` hit in the whole file is
`SIMPLE: convergence criteria` at line 462, which is the solver **echoing its
criteria at startup** and is not a statement that they were met. Checked by this
lane, not inferred.

**Gate B: `GATE FAIL`.**

---

## 4. THE STRICT COMPLETION RULE — LIMB BY LIMB

CLAUDE.md rule 4. **A run is done only if all of it holds.** F12 rung 1 fails
**every** limb, and each is recorded separately rather than collapsed into one
sentence:

| limb | required | measured | |
|---|---|---|---|
| **rc = 0** | 0 | non-zero — `result.json` `"status": "RuntimeError"`; the driver returned 1 | **FAIL** |
| **an `End` line** | present | **0 occurrences** of `^End` in `log.rhoSimpleFoam` | **FAIL** |
| **last time == `endTime`** | 6000 | last `Time = 180`; `system/controlDict` carries `endTime 6000; stopAt endTime;` | **FAIL** |
| **fields present at `endTime`** | `T U p alphat nut k omega` | **no time directory past `0/` exists** — `ls -d [0-9]*` returns `0` alone. The seven fields exist at `0/` only, as inputs | **FAIL** |
| **`ExecutionTime` count == `endTime`** | 6000 | **179** | **FAIL** |
| **age guard** (every field at `endTime` newer than the case's own `0/T`) | holds | **UNREACHABLE — there is no `endTime` field to date.** The guard cannot be evaluated, and an unevaluable guard is not a passed guard | **FAIL** |

**The completion rule is all-or-nothing and F12 rung 1 fails it six ways.**

*Recorded in F12's favour, since it is the one limb of the guard family that
worked:* the driver **did** carry the rule-4 ABSENT guard the frozen `run_case`
lacks. `run_f12_rung.py` refuses to start if any of the five registered run
directories already exists, because `run_case` `shutil.rmtree`s an existing case
directory and would have destroyed evidence. That refusal is why the coarse
tree survives to be graded here.

---

## 5. GATES 1, 2, 3 AND 4 — NO VALUES EXIST

| gate | quantity | frozen threshold | measured |
|---|---|---|---|
| 1 | Cp RMS, upper / lower | ≤ 0.08 / ≤ 0.04 | **does not exist** |
| 2 | shock location, sonic crossing | ≤ 0.020 chord | **does not exist** |
| 3 | CN vs 0.803 | ≤ 5 % | **does not exist** |
| 4 | CD vs 0.0168 | ≤ 20 % | **does not exist** |
| — | CM vs −0.099 (reported, not gated) | — | **does not exist** |

`result.json` carries no `record`, no `grade` and no `measured_core_min` key,
because the driver only writes them when `run_case` returns; it raised instead.
**No CN, CD, CM, shock measure or Cp RMS was ever computed for F12, at any mesh
level.** Gates 1–4 are **ungraded**, and they are ungraded for two independent
reasons either of which alone suffices: the mesh was inadmissible, and the run
neither converged nor completed.

**The four frozen predictions are therefore neither confirmed nor falsified.**
Prediction 1 (*"the shock will sit downstream of the measured position, by 0.01
to 0.03 chord"*) stands as written and untested, and any future F12 must test it
as written rather than re-registering it.

---

## 6. CRASH TRIAGE — THE CFD SUPERVISOR'S, DONE PERSONALLY

A crash is a finding until triage says otherwise (`SUPERVISION_CHARTER.md` §3;
CLAUDE.md TEAM ROSTER). **This triage is the supervisor's own, performed
personally and not delegated.** It is recorded here with its limits, and the
limits are as load-bearing as the conclusion.

### 6.1 ELIMINATED by measurement: the angle of attack DOES reach the flow

This is the mechanism a reader suspects first in a lifting-aerofoil case that
diverges, and it is **ruled out**, positively, from the built dictionary. The
supervisor read `0/U` and this lane re-read and re-derived it:

`internalField uniform (254.55661283 12.40536100 0)`, and the `freestreamVelocity`
inflow/outflow patches carry the identical vector in both `freestreamValue` and
`value`.

- `atan(12.40536100 / 254.55661283) = **2.790000°**` — **exactly the registered
  α = 2.79°**, to six figures.
- `|U| = **254.858710 m/s**`. With `0/T` at `uniform 300` K and
  `a = sqrt(1.4 × 287.058 × 300) = 347.2238 m/s`, **M = 0.733990** — the
  registered workshop M = 0.734 to five figures.

**The case setup is not the cause.** The incidence and the Mach number are both
in the initial and boundary conditions, correct to the registered values.

### 6.2 A READING THIS SUPERVISOR EXPLICITLY DECLINES

The predecessor lane observed `Cl` sitting at **−6.66e−4** at α = 2.79° and read
it as *"essentially no circulation ever developed"*. **The supervisor does not
accept that as diagnostic, and the record must not carry it as one.**

Iteration 178 of a planned 6,000 — **3 % of the registered schedule** — started
from a uniform freestream, is **far too early to expect developed circulation**.
The simultaneous `Cd` decay from 1.455 to 0.01653 over the same window is the
signature of a **startup transient still washing out**, not of a converged
aerodynamic state. **A near-zero Cl at 3 % of the registered iterations is not
evidence of a lift defect.**

The Cl and Cd values are recorded here as **observed and explicitly not read as
a finding**. Any future reader who wants to revive the circulation reading owes
a run that reached a plateau.

### 6.3 CONSISTENT BUT **NOT DEMONSTRATED**: the gate-A breach as the cause

A negative temperature in a compressible solver is the canonical symptom of
**corrupted gradient and diffusion terms**, and the coarse mesh carries **892
faces above 70° non-orthogonality** — the exact condition under which the
non-orthogonal correction to the Laplacian becomes unreliable
(`MESH_STANDARD.md` §3.1). That the gate-A breach caused the divergence is
therefore **consistent with the evidence**.

**It is NOT demonstrated, and this record does not claim it.** Demonstrating it
requires a **counterfactual mesh** — repairing the topology and re-running — and
that is *repairing and running in one breath*, which the predecessor lane was
**right** to refuse under a zero-compute brief and closed gates. It is written
here as **consistent-but-unproven**, never as the cause.

### 6.4 The primary finding does not depend on this triage at all

§2's gate-A failure was measured on three `checkMesh` logs from three built
meshes, **independently of any solve**. Were §6.3 disproved tomorrow, gate A
would still fail at all three levels and the verdict would still be `GATE FAIL`.

---

## 7. THE GEOMETRIC ERROR FLOOR — SETTLED, ONE CLAIM STRUCK, ONE NUMBER NOT REPRODUCED

Verification's concern was that F12's three levels discretise the **same**
surface polygon, so refinement cannot reduce the geometry error and G is
compromised. This section settles it **from the built dictionaries and the built
`polyMesh` point sets**, with live planted controls, and corrects the record in
two directions.

### 7.1 The polygon IS identical across the ladder — and the reader was shown able to see a difference

Measured by this lane with its **own** brace-matching extractor, on
`verification/runs/F12_runs/mesh_audit_2026-08-25/<level>/system/blockMeshDict`:

| level | polyLine entries | points per entry | total points | **unique (x, y) at z = 0** |
|---|---|---|---|---|
| coarse | 8 | 239 each | 1,912 | **956** |
| medium | 8 | 239 each | 1,912 | **956** |
| fine | 8 | 239 each | 1,912 | **956** |

**coarse == medium == fine, exactly**, as ordered de-duplicated (x, y) lists.
That is the generator's own construction: `surface_points(..., n = 240)` returns
239 interior points, called four times — upper 0→0.5, upper 0.5→1.0, lower
0→0.5, lower 0.5→1.0 — with **no level argument anywhere in the call**.

**Standing rule 3 — a zero from a reader not shown able to see a non-zero is not
evidence — applied to an "identical", which is the same claim in a different
coat.** Two perturbations were planted into dictionaries on disk and read back
by the **same** extractor:

| control | artifact | what was planted | what the reader saw |
|---|---|---|---|
| **PLANT_A** | `mesh_audit_2026-08-25/PLANT_A_thinned_blockMeshDict` | every 2nd polyLine point dropped | **480 unique (x, y)**, against 956 — the thinning is seen |
| **PLANT_B** | `mesh_audit_2026-08-25/PLANT_B_one_point_blockMeshDict` | one `y` moved by **1e−6 chord** | **956 unique, with exactly ONE differing point** — a 1e−6 perturbation is seen |

**The "they are identical" result comes from a reader demonstrated able to see
both a gross and a 1e−6 difference.** It is evidence.

**Verification's statement — "the fine level discretises the same polygon as the
coarse" — is TRUE AS STATED.**

### 7.2 STRUCK: this supervisor's relay of it as a G-compromising defect was too strong

**The cfd supervisor relayed verification's finding upward as a defect that
compromises G. That relay was too strong and is struck here, by the supervisor's
own direction.** The polygon being frozen across the ladder is a **floor**, not a
defect, and whether it bites depends entirely on how it compares with the
mesh's own sampling of that polygon — which nobody had measured.

### 7.3 What this lane measured — and where it PARTS COMPANY with the figures it was handed

Measured from the **built `constant/polyMesh` point sets** of all three meshes
(the aerofoil patch, z = 0 plane), against the generator's own spline
`rae_section()`, evaluated at 1,500 samples per chord:

| quantity | coarse | medium | fine | polygon floor |
|---|---|---|---|---|
| surface points on the patch | 192 | 384 | 768 | 956 |
| max surface segment length (chord) | 4.1700e−02 | 2.1082e−02 | 1.0599e−02 | — |
| **max PERPENDICULAR deviation from the spline (chord)** | **1.3924e−04** | **3.7039e−05** | **1.6575e−05** | **6.2527e−06** |
| — worst at x/c | 0.402 | 0.999 | 0.998 | 0.0024 |
| **max VERTICAL (Δy at fixed x) deviation (chord)** | 2.3196e−04 | **1.4974e−04** | **1.4974e−04** | **1.4974e−04** |

**Reproduced exactly:** the polygon's own worst chord-height deviation on the
**vertical** metric is **1.497394e−04 chord**, matching the figure this lane was
handed to four figures. The metric is now pinned: it is Δy at fixed x, not
perpendicular distance.

**NOT REPRODUCED, and this record will not carry them:** the mesh-faceting triple
**3.516e−03 / 2.461e−03 / 1.700e−03 chord**, and the derived margins
**23.5× / 16.4× / 11.4×**. This lane measured the built meshes directly and got
neither triple under either metric, and **cannot say what quantity those figures
are.** They are struck from this record rather than repeated.

### 7.4 What follows, honestly, from the numbers this lane can defend

- **On the perpendicular metric — the geometrically meaningful one, since Δy at
  fixed x is degenerate at a near-vertical leading edge — the polygon IS finer
  than the mesh sampling it, at all three levels.** The margins are
  **22.3× / 5.92× / 2.65×**, not 23.5× / 16.4× / 11.4×. **The direction of
  §7.2's correction survives: the floor is not what limits the answer at these
  three levels, so the concern was indeed overstated and the strike stands.**
- **But the margin is far tighter than the figures this lane was handed, and it
  is closing far faster.** It falls by **3.76× then 2.24×** per refinement — not
  ~1.4× — and at the fine level it is **2.65×, not 11.4×**. **One further
  factor-two refinement beyond the current fine level would put the mesh's
  faceting at or below the polygon's own floor.** For the current ladder that is
  a caution; for any **extended** ladder it is a live constraint, and the next
  F12 pre-registration should size the polygon to the finest level it intends to
  build.
- **On the vertical metric the floor is already exactly binding at medium and
  fine**, at 1.4974e−04 chord on both — and not by coincidence. The mesh's
  leading-edge chords at those levels are **shorter than the polygon's own first
  segment** (mesh 1.50e−05 and 7.53e−06 chord against the polygon's 2.14e−05),
  so they lie *inside* a straight polygon segment and inherit its full deviation.
  This lane does not treat that metric as the governing one, but it records it
  rather than choosing the flattering half.

**Net: the strike in §7.2 stands, on this lane's own arithmetic. The margin
justifying it is 2.65× at the fine level, not 11.4×, and the record says so.**

---

## 8. THE TIER, ARGUED — WHY `NOT HELD` AND NOT THE OTHER THREE

Under the "triple crown" columns of `THERMAL_TIERING_DIRECTIVE.md` §5:

**V — code verification. F12 CARRIES NO V, AND COULD NOT HAVE, EVEN HAD EVERY
GATE PASSED.** This is the most useful thing this record can tell the next
reader, and it was verified twice by this lane against the HEAD blob of the
frozen document:

- occurrences of `exact solution`: **0**
- occurrences of `manufactured`: **0**
- occurrences of `MMS`: **0**
- occurrences of `code verification`: **0**
- occurrences of `correlation`: **3** — at lines **567**, **596** and **735**,
  and **all three are flat-plate y+ correlations**, not comparisons to an exact
  solution. Line 596–597 labels its own column *"ESTIMATED, from a flat-plate
  correlation with an assumed edge velocity; it is not measured and **it is not
  a gate**"*, and line 735 labels the whole y+ block *"all of it is ESTIMATED and
  none of it is measured"*. Under §5's own defeater — *"the 'correlation'
  supplies no band"* — none of the three can carry V.

**Gates 1, 2, 3 and 4 are, every one of them, validation against experiment.**
F12 was never designed to carry V. **A hypothetical F12 that passed all four
gates on an admissible mesh would have reached `GATE REACHED` — V missing — and
never `HOLDS`.** Any future F12 that wants `HOLDS` must add a code-verification
element, and adding it after the fact to this pre-registration is not available.

**G — grid convergence. Not held, and not close.** No Roache triple exists: one
level was launched, it produced no graded quantity, and the other two were never
solved. The ladder is *geometrically similar* (§1.1) — that repair worked — but
similarity is a precondition for G, not G itself. Separately, **the ladder is
inadmissible at every level** (§2), so even a completed triple on it could not
have carried G.

**P — validation against a public primary source, with the pre-registration on
disk.** The pre-registration is on disk and frozen — that half holds. The
reference half does not resolve here, and **this lane does not decide it**:

> F12's reference values are taken from the **AFOSR-HTTM/Stanford digitisation,
> flow case 8621, evaluator R. E. Melnik (1981)**, retained at
> `verification/runs/F12_runs/reference/f8621.txt` with the decoder that produced
> the graded `.dat` files beside it. That artifact is **secondary**, it is
> **title-page-verified against nothing**, and **Cook, McDonald and Firmin,
> AGARD AR-138 (1979) — the primary it transcribes — is not held by this lab and
> has not been opened by it.**

Standing rule 15 title-page verification of F12's primary is therefore currently
**IMPOSSIBLE**, because the primary is not held. **Whether a secondary
transcription can support a P at all is `VERIFICATION_CHARTER.md`'s rubric and a
verification-team ruling.** It is neither this lane's call nor the cfd
supervisor's, it is **not decided here**, and no wording above should be read as
having decided it. It is moot for this row — no P column opens on a row whose
admission gate failed — but it is **not moot for the next F12**, and it should be
ruled before that pre-registration is frozen.

**Therefore `NOT HELD`.** Not `SURVEYED`: nothing was surveyed, the evidence is
gated. Not `GATE REACHED`: that word requires **exactly one** of V/G/P missing,
and here none is held. Not `PENDING`: `PENDING` is a queue state for a row not
yet run, and it is **never** used to soften a `GATE FAIL` (CLAUDE.md rule 1).

---

## 9. REPORTED, NOT REPAIRED

Four defects were found while grading. **None was repaired in this dispatch**;
each is reported with what was verified and what was not.

### 9.1 The frozen pre-registration's line citations into the grading path are ALL STALE

The frozen document cites `sdk/workflows/rae2822_case9.py` at
`:254 :269 :577 :692 :892 :894 :903 :925 :927 :929 :930 :957`. **This lane
checked every one against the current blob. Not one lands where the document
says.** A sample, verified by reading the line:

| cited | the document says it holds | what line actually holds now |
|---|---|---|
| `:254` | `FIRST_CELL = 2.0e-6`, the module constant | `n: int = 240)`, the `surface_points` signature |
| `:269` | `blockmesh_dict(..., first_cell=FIRST_CELL)` | `@dataclass(frozen=True)` |
| `:577` | `application     rhoSimpleFoam;` | a bare closing `""")` |
| `:929` | `run_case`'s `ranks: int = 1` | `out: dict[str, Any] = {"failed_checks": []}` |

**The cause is not drift or neglect — it is the repair the frozen document
itself demanded.** Commit `b0c0db35` implemented MESH-SIMILARITY AMENDMENT §7's
pre-launch blockers 15 minutes after the amendment was frozen, and in doing so
moved every line the amendment and the earlier COSTED ADDENDUM cite. The
constant was also **renamed**: `FIRST_CELL` became `FIRST_CELL_ANCHOR`
(now at `:336`), so the amendment's §3 is a description of a **superseded** state
of the code. `application rhoSimpleFoam;` is now at `:772`; `build_case` at
`:1087`; `run_case` at `:1140`; `blockmesh_dict` at `:430`.

**This touches CLAUDE.md rule 6** — the rule exists because other records cite
frozen files by line, and one such citation sits inside an executable check.
Rule 6 protects a frozen file's **own** line numbers, which held: both addenda
assert `lines whose number changed above this section: 0` and both are true
appends. What failed is the **outbound** citation — a frozen document citing a
*live* file by line number. **That is a distinct defect class from the one rule 6
names, and it is reported as such.**

**Not repaired, and deliberately so:** the frozen document must not be edited to
fix its line numbers (rule 2, gates closed). The disposition is for the
supervisor: either a dated post-compute addendum recording the re-resolution
table, or a standing convention that a frozen document cites a live file by
**symbol and blob**, never by line. This lane did not choose between them.

### 9.2 `run_case` computes `mesh_gate` and launches the solver anyway

`sdk/workflows/rae2822_case9.py:1168` computes `gate = mesh_gate(quality)`
immediately after `checkMesh`, and **`gate` is never read again until it is
stored in the returned record at `:1217`**. The solver launches at `:1175`
(parallel) or `:1180` (serial) with no reference to it. **20.5 s of solver wall
went into a mesh already known, by the code's own arithmetic three lines
earlier, to fail gate A.**

This is **not a departure from the frozen text**, which gates admission of
*evidence* and not the act of launching. It is a **refuse-never-degrade gap**
(CLAUDE.md rule 4: comparators refuse rather than degrade). Reported to the
supervisor; **no code was changed in this dispatch.**

*Recorded in the code's favour:* `mesh_gate` itself is **fail-closed** — a
`None` non-orthogonality or `None` skewness is counted a breach, not waved
through. The defect is in what the caller does with the answer, not in the gate.

### 9.3 `parse_check_mesh` returns `max_aspect_ratio = None` at all three levels

The parser matches aspect ratio only on a line that
`startswith("Max cell openness")` **and** contains `"aspect ratio"` — the
combined line older OpenFOAM releases printed. **On v2606 the two are separate
lines**, so the branch never fires:

- at medium the log prints `Max aspect ratio = 962.7865634 OK.` — matched by no branch;
- at coarse and fine the value appears only inside the failed-check string
  `***High aspect ratio cells found, Max aspect ratio: 10606.65276, ...`, which
  is captured as **text** into `failed_checks` and never parsed as a **value**.

Confirmed in `mesh_audit.json`: no `max_aspect_ratio` key at any level. The
three ratios in §2 (10,606.65276 / 962.7865634 / 2,767.113299) were read by this
lane from the logs' own lines, not from the parser.

**Aspect ratio is ADVISORY under `MESH_STANDARD.md` §3.3, never a lone
rejection**, so this defect **changed no verdict** — gate A already fails on
non-orthogonality. Reported; not repaired.

### 9.4 The mesh audit's polygon extractor mis-counts, though its conclusion holds

`mesh_audit.json` records `n_polylines: 1`, `n_points_z0: 960`,
`n_unique_xy: 960` at every level. **The dictionaries in the same directory carry
8 polyLine entries, 1,912 points and 956 unique (x, y)** (§7.1). The cause is in
`build_and_audit_meshes.py`'s `extract_polylines`, whose pattern
`polyLine\s+(\d+)\s+(\d+)\s*\(([^;]*)\)\s*$` uses a **greedy `[^;]*`** that
spans across all eight entries and collapses them into one match.

**Its conclusion — all three levels identical — is independently corroborated by
this lane's own extractor (§7.1), and its planted control did demonstrate
sensitivity within its own counting.** But **its counts are not reproducible**,
and the figures in §7.1 of this record are this lane's, not its. Reported; not
repaired.

---

## 10. RULINGS CARRIED

### 10.1 The cap-enforcement defect — LEGAL as a post-compute addendum, and landed

The finding that a wall-clock `timeout` is not a core-minute cap **belongs to
the `ansys-verification` team and is cited as theirs**
(`cases/ansys_verification/VMFL051/RESULTS.md` §7.1). It is recorded against
F12's grading path in a dated post-compute addendum at the foot of the frozen
pre-registration, because it **derives from the existing frozen caps, adds no row
definition, and moves no gate, threshold, cap or label**. **No lesson is assigned
from it here** — it is not this team's finding to number.

### 10.2 The plateau row definition — NOT LEGAL for F12, and it goes to the next pre-registration

The supervisor's ruling, recorded here with its reasoning:

**F12 has fired, so gates are closed, and a row definition added now is added
after compute.** The predecessor lane was **right** to refuse it, and right to
record the counter-argument alongside: **rung 1 produced no number, so nothing
could have been fitted to a plateau clause even if one had been added.** The
refusal costs the lab nothing and preserves the freeze's entire evidentiary
content.

**Ruling: the plateau clause is NOT added to F12's frozen pre-registration.** It
belongs in the **next** F12 pre-registration, where it is a legitimate
**pre-compute** choice — the same disposition verification gave F4's event
ordinal.

**And F12 needs a fresh pre-registration regardless.** Its mesh fails admission
gate A at all three levels; the ladder as frozen is **inadmissible**, and no
addendum to a closed document can make it admissible. A next F12 re-registers
the ladder — block topology and wall-normal recipe both — with the plateau clause
in it from the start, and with §7.4's polygon-resolution constraint sized to the
finest level it intends to build.

---

## 11. COST — CALIBRATION AT COMPLETION (CLAUDE.md rule 12)

F12 is a **completed process** — a case closed — so the estimate-versus-actual
comparison is owed. **It has already landed as row `C-50` in
`docs/COST_CALIBRATION.md`** (commit `cd1ac21a`) and is **not restated here**;
this section records only the headline and the one figure the tier depends on.

| | |
|---|---|
| frozen cap, rung 1 | **120 core-min** (2026-08-23 COSTED ADDENDUM §5) |
| frozen estimates | Basis A **11.9 core-min**, Basis B **109.4 core-min**, both labelled ESTIMATED |
| **actual** | **0.4617 core-min MEASURED**, = **$0.000395 DERIVED, NOT MEASURED** |
| **fraction of cap** | **0.38 %** |
| the comparable ratio | **not the total** — the run stopped at 3.0 % of the registered iterations, so 0.4617 against 11.9 is an interruption, not a calibration. The rung's registered purpose was a **rate**: measured **4.8301e−6 s per cell-iteration**, **1.027× Basis A** (confirmed to +2.7 %) and **0.105× Basis B** (falsified by 9.5×) |
| **waste** | **0.4617 core-min — the whole of it**, named in full and netted off neither column nor the ratio. The spend went into a mesh inadmissible under the pre-registration's own gate A |
| overrun | **none.** No cap was approached, and no run was stopped by a cap |

**One spend is NOT in `C-50` and is recorded here so it is not lost:** the
three-level mesh audit (`6b462592`) cost **11.48 s = 0.191 core-min** at 1 rank,
from `mesh_audit.json`'s own `timings` (coarse 2.493 s, medium 2.091 s, fine
6.898 s, summing dictionary write, `blockMesh` and `checkMesh`). It is
**meshing, not solving**; the frozen §4 folds meshing into headroom rather than
giving it its own cap, so no cap was breached. **F12's total measured spend is
therefore 0.4617 + 0.191 = 0.653 core-min**, still **0.54 % of rung 1's cap**.
Whether that 0.191 core-min needs a calibration row of its own is the
supervisor's call, not this lane's.

**No "40 core-minute" figure appears anywhere in this record.** That figure
originated with the chief and was echoed back; it is not Sanaa's and it is
struck.

---

## 12. ARTIFACTS — every number above cites one, and all are on disk

| artifact | what it carries |
|---|---|
| `verification/campaign/F12_PREREGISTRATION.md` (blob `41ec748a`) | the frozen gates, thresholds, caps, labels and predictions; read from the HEAD blob |
| `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/result.json` | the run record — timestamps, `status`, the four frozen blobs, the FOAM FATAL ERROR text preserved inside git |
| `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam` | the divergence, the iteration count, the absent `End` line. **Gitignored** (`.gitignore:260`) — on-disk only |
| `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/log.checkMesh` | the run mesh's gate-A quality. **Gitignored** |
| `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/0/{U,T}` | the incidence and Mach of §6.1. **Gitignored** |
| `verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/system/controlDict` | `endTime 6000` |
| `verification/runs/F12_runs/mesh_audit_2026-08-25/{coarse,medium,fine}/log.checkMesh` | **the three logs §2 is graded on.** Gitignored |
| `verification/runs/F12_runs/mesh_audit_2026-08-25/{coarse,medium,fine}/system/blockMeshDict` | the polygon of §7.1 |
| `verification/runs/F12_runs/mesh_audit_2026-08-25/{coarse,medium,fine}/constant/polyMesh/` | the built point sets §7.3 measures |
| `verification/runs/F12_runs/mesh_audit_2026-08-25/mesh_audit.json` | per-level first cells, expansion ratios, gate-A verdicts, timings |
| `verification/runs/F12_runs/mesh_audit_2026-08-25/PLANT_{A,B}_*_blockMeshDict` | the two planted controls of §7.1 |
| `verification/runs/F12_runs/reference/f8621.txt` | the **secondary** reference of §8, title-page-verified against nothing |
| `verification/runs/F12_runs/run_f12_rung.py` | the driver, its rule-4 ABSENT guard, and its cap arithmetic |
| `docs/COST_CALIBRATION.md` row `C-50` | the full estimate-versus-actual comparison |
| commits `03c35817`, `b0c0db35`, `cd1ac21a`, `6b462592` | amendment, grading-path repair, the rung, the mesh audit |

**Several load-bearing artifacts are gitignored and live on disk only** — the
three `checkMesh` logs above all of them. They are named here with their paths
so that a future reader knows exactly what to look for and knows, if it is gone,
that the number no longer has an artifact.

---

## 13. WHAT THIS LANE COULD NOT VERIFY

Stated plainly, because an honest gap is worth more than a confident guess.

1. **The mesh-faceting triple 3.516e−03 / 2.461e−03 / 1.700e−03 chord and the
   margins 23.5× / 16.4× / 11.4×** — not reproduced under either metric this
   lane measured, and this lane cannot say what quantity they are (§7.3). Struck
   from this record; §7.4 carries what could be defended instead.
2. **That the gate-A breach CAUSED the divergence** — consistent, not
   demonstrated, and demonstrating it needs a counterfactual mesh (§6.3).
3. **That the high-aspect-ratio cells and the >60° faces are the same cells** —
   `MESH_STANDARD.md` §3.3's compound flag is recorded as tripped at the mesh
   level; the co-location was not measured (§2).
4. **Whether a secondary transcription can support a P** — verification's rubric,
   referred and not decided (§8).
5. **Whether the 0.191 core-min mesh-audit spend needs its own calibration row** —
   the supervisor's call (§11).

---

*Written 2026-08-25 by a `lab-lane` worker for the cfd team, on a
supervisor-directed **ZERO-COMPUTE** task. No solver was launched, no mesh was
built and no case directory was created in producing this record. Every value in
§2, §3, §4, §6.1, §7.1, §7.3, §8 and §9 was re-derived from the named artifact
by this lane rather than inherited from a brief; the two figures that failed to
reproduce are named as such in §7.3 and §13 rather than repeated.*
