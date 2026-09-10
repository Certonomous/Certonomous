# SUBOFF R1b — RUN VERDICT: `NOT A RESULT`

**Rung:** DARPA SUBOFF bare hull, zero incidence, total-drag parity (gate D1).
**Pre-registration:** `verification/campaign/SUBOFF_R1b_PREREGISTRATION.md`, **FROZEN at `f67bbe14`**
(blob `0ff780e4b823ac06d2b25d510642dd10f35dc29e`; verified byte-identical at disk, at `HEAD` and at
`f67bbe14` — the freeze has not moved and the file has not been edited).
**Launch:** 2026-09-10T05:35:55Z (pid/sid 1170640) → 08:29:14Z. **Spend:** 173.23 core-min of a
registered 400 cap. **Evidence assembled by** cfd `lab-lane`; **rulings by** cfd-supervisor,
2026-09-10. **DRAFT — not committed.**

**VERDICT: `NOT A RESULT`.** No gate was evaluated and **no `CT` value is quoted from this rung.**

---

## 1. THREE INDEPENDENT GROUNDS, EACH ALONE SUFFICIENT, ALL REGISTERED BEFORE COMPUTE

### (i) Rule 5 clause 1 — `fine` and `medium` are not iteratively converged, and they are not plateaued either

Worst final initial residuals at `endTime 2500`, against the registered `1.0e-4` threshold:

| level | worst residual | field | verdict on clause 1 |
|---|---|---|---|
| coarse | `1.301e-05` | `k` | converged |
| **medium** | **`5.483e-04`** | `Uy` | **NOT converged — 5.5× the threshold** |
| **fine** | **`9.551e-04`** | `Uy` | **NOT converged — 9.6× the threshold** |

**And the graded coefficient is still in motion at the cut — measured, and this is worse than the
residuals alone say.** Read directly from each level's `postProcessing/forceCoeffs/0/coefficient.dat`:

| level | `Cd` @1500 | @2000 | @2400 | @2500 | change over final 1000 | change over **final 100** | monotone over final 500? |
|---|---|---|---|---|---|---|---|
| coarse | 0.011286 | 0.011283 | 0.011283 | 0.011283 | **−0.03 %** | −0.00 % | no (settled) |
| **medium** | 0.786650 | 0.561061 | 0.376974 | 0.339200 | **−56.88 %** | **−10.02 %** | no (falling) |
| **fine** | 3.624424 | 3.696723 | 4.477195 | 4.732715 | **+30.58 %** | **+5.71 %** | **yes (rising)** |

**Only `coarse` reached a steady state.** `medium` was falling 10 % per hundred iterations at the
cut and `fine` was rising 5.7 % per hundred iterations, monotonically, over its final 500. These are
not three converged coefficients at three refinements — **they are three snapshots of three
trajectories, one settled and two in active motion in opposite directions.** A grid study of moving
targets is not a grid study.

**The comparator's own `PLATEAUED` flag on `medium` and `fine` is substantively false. See §3b —
it is a second defect in the pinned comparator, and it did not bite here only because the residual
check caught the same two levels independently.**

### (ii) Rule 5 clause 2 — the triple is `DIVERGENT`

Observed order **`−6.4048`**, state **`DIVERGENT`**, `dim = 2`. Under rule 5 a triple that is
`DIVERGENT` is `NOT A RESULT` whatever its value. **No GCI is quotable and none was emitted** — the
values are monotone, so monotonicity is not the disqualifier; the divergence is.

**And the monotonicity that produced `DIVERGENT` may itself be an artifact of the stopping point:**
`medium` is falling toward `coarse` while `fine` climbs away. Three trajectories halted at a common
iteration count do not constitute a grid sequence. This is recorded as an observation, not a
diagnosis.

### (iii) No graded number is of record at all — the frozen launcher's argv omission

`run_suboff_r1b_triple.sh:369` invokes the pinned comparator with `--coarse`, `--medium` and
`--fine` and **omits `--reference`**. `grade_suboff.py:489–490` requires all four and **refused
(exit 2)**:

> `REFUSE (exit 2): need --coarse --medium --fine --reference (or --selftest)`

The comparator behaved exactly correctly — refuse-not-degrade, as designed. The launcher's EXIT trap
then wrote `VERDICT.R1b_triple.txt` with `verdict=NOT A RESULT`. **R1b's verdict guarantee held**: a
launch producing no verdict was not a possible outcome, and it was not the outcome.

### THE ARGV DEFECT IS NOT WHAT SANK THIS RUNG

**Grounds (i) and (ii) would stand in full even had the argv been correct.** A regrade of these three
levels with `--reference` supplied returns exactly `NOT A RESULT` — that is not a prediction; it was
computed (§4a). **A reader must not come away thinking a missing command-line flag cost this rung a
result.** It cost the rung its *registered verdict path*; the physics cost it the result.

**Consequently: `R1c` as a zero-solver-compute regrade is CANCELLED** — cfd-supervisor's ruling,
2026-09-10. Regrading buys nothing, because the levels are not gradeable into a result by any
comparator.

---

## 2. STRICT COMPLETION (CLAUDE.md rule 4) — VERIFIED FIRST-HAND

Every clause re-derived from the run artifacts, independently of `STATUS.R1b_*` and
`PROGRESS.R1b_triple.txt`. **All three levels satisfy every clause. No clause fails.**

| clause | `r1b_coarse` | `r1b_medium` | `r1b_fine` |
|---|---|---|---|
| (a) `rc = 0` (from each `rc` sidecar) | `rc=0` | `rc=0` | `rc=0` |
| (b) `End` line | 1 | 1 | 1 |
| (c) last time `== endTime` | 2500 == 2500 | 2500 == 2500 | 2500 == 2500 |
| (d) fields at `endTime` | `U k nut omega p phi` | same | same |
| (e) `ExecutionTime` count `== round(endTime/deltaT)` | 2500 == 2500 | 2500 == 2500 | 2500 == 2500 |
| (f) **age guard** | **PASS, +1174 s** | **PASS, +2512 s** | **PASS, +6707 s** |

`endTime 2500`, `deltaT 1` read from the shared `system/controlDict` blob, so clause (e)'s target is
`round(2500/1) = 2500` — the unit-step case, no adaptive `deltaT`.

**Clause (d), field list.** This is **incompressible `simpleFoam`**: the thermal family's
`T U p_rgh alphat nut k omega phi` list does not apply and was **not assumed**. The set present at
`2500/` is enumerated above and matches the comparator's registered incompressible set
`FIELDS = ("p", "U", "k", "omega", "nut", "phi")` at `grade_suboff.py:148`, plus
`2500/uniform/{time,cumulativeContErr}`. Nothing registered is missing.

**Clause (f), by mtime, strictest available reading** — oldest field at `endTime` vs newest in `0/`:

| level | `0/` mtime (all five) | launcher `zero_dir_epoch` | oldest at `2500/` | margin |
|---|---|---|---|---|
| coarse | 1789018559 | 1789018559 — **Δ = 0 s** | `2500/U` @ 1789019733 | **+1174 s** |
| medium | 1789019733 | 1789019733 — **Δ = 0 s** | `2500/nut` @ 1789022245 | **+2512 s** |
| fine | 1789022246 | 1789022246 — **Δ = 0 s** | `2500/U` @ 1789028953 | **+6707 s** |

No margin is marginal; the smallest is 1174 s. Levels ran strictly sequentially — the shared seconds
1789019733 and 1789022246 are the signature of a serial chain, not an anomaly.

**What this establishes, and what it does not.** It establishes that the run is **complete** and
that its artifacts date from the launch that was allowed to produce them. **It does not make the
levels gradeable into a result** — §1 governs that, and it says they are not.

---

## 3. THE PINNED COMPARATOR CARRIES TWO DEFECTS. NO SUBOFF `PASS` IS ISSUABLE ON IT.

**This is a hard blocker on the whole SUBOFF family, not an R1c footnote** — cfd-supervisor's
ruling, 2026-09-10, on his own confirmation of both defects at the source. **They are ordered by
danger: `:368` first.**

### 3a. `grade_suboff.py:368` — the plateau test is a two-point test and cannot see a drift

```python
plateaued = abs(ct_series[-1] - ct_series[-2]) <= PLATEAU_TOL_REL * abs(ct)
```

`PLATEAU_TOL_REL = 0.005` (`:65`). It compares **only the final two writes**. Measured against the
trajectories of §1(i):

| level | last-step Δ, relative | comparator flag | substance |
|---|---|---|---|
| coarse | 0.0000 % | `PLATEAUED` | **correct** — settled to 1e-10 |
| medium | 0.0998 % | `PLATEAUED` | **FALSE** — falling 10.02 % per 100 iterations |
| fine | 0.0535 % | `PLATEAUED` | **FALSE** — rising 5.71 % per 100 iterations, monotone over 500 |

**A two-point test cannot distinguish a plateau from a steady drift**, and a false `PLATEAUED` is a
**false green on a rule-5 clause-1 gate**. It caused no harm here only because the residual check
caught the same two levels independently — but had the residuals fallen under `1.0e-4` while the
coefficient drifted like this, the comparator would have declared the levels plateaued and admitted
them to a grid claim.

**This is a rule-3-shaped hole: a plateau detector never shown able to see a non-plateau.** The
comparator's two planted-zero controls cover the `coefficient.dat` value reader and the field
reader; **neither covers the plateau classifier.** The `--selftest` does drive a non-plateaued limb,
but through a synthetic series handed straight to the shared Roache instrument — not through this
two-point test on a real drifting file. **This is the more dangerous of the two defects. Blocker.**

### 3b. `grade_suboff.py:369` reports faces as cells

```python
ncells = len(parse_owner(case))
```

`parse_owner` (`:124–135`) parses `constant/polyMesh/owner` and returns the owner list, which carries
**one entry per face**. Its length is `nFaces`, not `nCells`. The polyMesh headers say so directly —
`r1b_coarse`'s `owner` header reads `"nPoints:80672  nCells:39904  nFaces:160020  nInternalFaces:79348"`.
The cell count is `max(owner) + 1`.

| level | what `ncells` reports | **true `nCells`** | registered (§4a, prereg 160–162) |
|---|---|---|---|
| coarse | 160,020 | **39,904** | 39,904 |
| medium | 359,742 | **89,784** | 89,784 |
| fine | 808,965 | **202,014** | 202,014 |

**It feeds the refinement ratio.** True cell ratios are **exactly 2.250000** at both steps →
`r = 1.5000000` exactly in `dim = 2`, the **equal-ratio** Roache branch. Face ratios are 2.248106 /
2.248737 → `r = 1.4993687 / 1.4995788` and a spurious `ratio_gap = 2.101e-04` that drives the
comparator into its **`unequal`** branch. The registered family is *"exactly 2.25× per level"*
(prereg line 29) — **in cells, and it is exactly that.** The comparator cannot see it.

**Any GCI this comparator ever quotes on a `CONVERGING` triple is perturbed by this.** Here it
changes nothing reported (recomputing the order at exact `r = 1.5` gives `−6.4013` against
`−6.4048`, and rule 5 disqualifies the triple regardless), but on a triple that passes, the observed
order and the GCI at `Fs = 1.25` both depend on `r`. **Blocker.**

### 3c. NOT A DEFECT — the `Aref` comparison exists. It is *conditionally armed*, and that is worth hardening.

**A withdrawn finding, recorded because withdrawing it correctly matters.** An earlier draft of this
record named a third blocker: that `assert_forcecoeffs_constants` (`:246–266`) checks `Aref` for
presence only — `want` there is `{magUInf, lRef, rhoInf}` and `Aref` gets a bare `None` test — and
so never compares it to the registered value. **That reading of the helper is correct but the
conclusion was wrong: it stopped at the helper and missed the call site.** At `grade_suboff.py:361–365`,
immediately after `fc = assert_forcecoeffs_constants(case)`:

```python
if "Aref" in ref and ref["Aref"]:
    if abs(fc["Aref"] - ref["Aref"]) > A_REF_TOL_REL * abs(ref["Aref"]):
        refuse(...)
```

**The comparison does exist, it ran on this rung, and it passed.** `A_REF_TOL_REL = 0.03` (`:73`,
*"hull-patch area must match the registered Aref within 3%"*). **Struck as a blocker** —
cfd-supervisor's refutation, verified at the source by this lane. **A record that names a defect the
instrument does not have is itself a defect in the record**, and it would send a successor hunting a
repair that is not needed.

**What survives, in a smaller form: the comparison is CONDITIONALLY ARMED.** It sits behind the
truthiness guard `if "Aref" in ref and ref["Aref"]`. With `Aref` absent, `null` or `0` in the
reference JSON, **the comparison is skipped silently and the comparator would produce a verdict
having never checked the normalisation at all.** It is armed here only because the value was pinned
precisely in order to arm it. **A second reason to harden it:** the tolerance is **3 %**, and because
`CT ∝ 1/Aref` a 3 % normalisation error is a 3 % `CT` error — **nearly a third of the ±10 % gate
band.** Even armed, the check would admit a normalisation error consuming a third of the band.
**Worth hardening in a successor — unconditionally armed, and tightened — but NOT a missing check
and NOT a blocker.**

**Two corrections to the arithmetic that came with the refutation, so the record does not
mis-attribute a measurement:**

1. **The tolerance is 3 %, not ±0.1 %.** `A_REF_TOL_REL = 0.03`.
2. **The triple −0.1649 / −0.0520 / +0.0063 % is NOT this check's output and must not be attributed
   to it.** This check compares **one** disk value against **one** reference value: `system/controlDict`
   is a single blob across all three levels, so `fc["Aref"]` is `0.08317033628` at every level, and
   the comparison yields the **same** deviation three times — `1.673e-11` relative — never three
   distinct percentages. Those three figures are a **different quantity**: the per-level **built
   sector area** against the pinned `Aref`, which is exactly the *"monotone ~0.171 % normalisation
   drift"* the reference JSON's own `Aref_note` discusses and which the builder records in each
   level's birth certificate. −0.1649 % sits right on that 0.171 %. **Different instrument, different
   measurement, and it belongs to the birth certificates, not to this check.**

**The `Aref` exclusion for the §4 anomaly therefore stands, confirmed two independent ways** — by
the comparator's own check at `:362` (passed, 3 % tolerance) and by hand measurement: disk
`0.08317033628` in all three single-blob `controlDict` files against registered
`0.0831703362813915`, **relative difference `1.673e-11`**, a decimal truncation and nothing more. An
exclusion confirmed twice is stronger than one, and neither reading is presented as filling a gap in
the instrument, because there is no gap.

**Nothing was edited.** `grade_suboff.py` is a §11-pinned comparator; rules 2 and 6 forbid touching
it, and a post-compute comparator repair is a `VERIFICATION_CHARTER` §2d.1 question. **Both
blockers — `:368` and `:369` — plus the `:362` hardening note are referred to the cfd-supervisor.**

---

## 4. OPEN ANOMALY — THE `CT` MAGNITUDES. NOT DIAGNOSED, AND NOT ABSORBED INTO "NOT CONVERGED".

`CT` reads **0.011283 / 0.339200 / 4.732715** against a registered band of **[0.00324, 0.00396]**.
**The fine level is roughly 1,300× the band, and roughly 420× the coarse level on a mesh 5.06× its
size.**

**This is an anomaly in its own right and it is recorded as OPEN.** A residual of `5.5e-04` is
unconverged, but unconverged-ness alone does not obviously buy three orders of magnitude in a force
coefficient, and this record does not claim it does.

### THE LEADING CANDIDATE, AND WHAT IT COSTS THE GRID CLAIM

**These are not three coefficients at three refinements. They are three snapshots of three
trajectories, two of them in active motion in opposite directions when the runs were stopped** —
`fine` rising monotonically (+30.58 % over its final 1000 iterations, +5.71 % over its final 100),
`medium` falling (−56.88 % / −10.02 %), only `coarse` settled (§1(i)).

**The consequence, stated plainly because a reader must not carry the wrong thing away: on this
evidence the `DIVERGENT` classification and the observed order `−6.4048` are properties of WHERE THE
RUNS WERE STOPPED, not established properties of the discretisation.** Three moving targets halted
at a common iteration count will produce a spread, and a spread ordered by mesh size will read as a
divergent grid sequence whether or not the discretisation diverges. **"SUBOFF diverges under
refinement" is NOT a physics finding of this rung and must not be quoted as one.**

This does not change the verdict — **`NOT A RESULT` stands on rule 5 clause 1 alone**, and clause 2
adds a second sufficient ground on the numbers as they are. It changes what a successor should
conclude: **the grid behaviour of this case is not yet observed at all**, because it has never been
observed at a converged state.

**This reading is the leading candidate for the `CT` magnitudes and it is still a candidate, not an
assertion.** It says the numbers are not converged coefficients; it does **not** say why the fine
trajectory climbs, and it does not by itself account for three orders of magnitude.

**Excluded, by direct measurement:**

- **The `Aref` normalisation — excluded two independent ways.** The comparator's own check at
  `grade_suboff.py:362` ran and passed (3 % tolerance), and by hand: identical across all three
  levels (one `controlDict` blob) and equal to the registered pinned value to **`1.673e-11`** (§3c).
  It cannot produce a level-dependent factor of 420.
- **`magUInf`, `lRef`, `rhoInf`.** Verified by the comparator against registered values at `1e-6`
  relative, all three levels: `2.893`, `4.356`, `1000.0`.
- **A wrong mesh.** 15/15 sha256 mesh pins match §4a at all three levels (§5a). The mesh that ran is
  the registered mesh.
- **Incomplete or stale fields.** All six clauses of rule 4 pass with age-guard margins ≥ 1174 s (§2).
- **A misreading comparator.** Both rule-3 planted-zero controls passed on the real artifacts: the
  gate reader `read_CT(coefficient.dat)` saw a planted `1.234e-03` exactly, and the field reader saw
  a planted `500.0 Pa` to within `8e-15` of expectation.

**Named as candidates, none asserted:**

1. *(The leading candidate — three halted trajectories rather than three coefficients — is stated
   above rather than repeated here.)*
2. **A refinement-dependent instability rather than a refinement-dependent solution.** Worst
   residuals *rise* with refinement — `1.3e-05` → `5.5e-04` → `9.6e-04` — the opposite of the usual
   ordering, and `medium` and `fine` move in *opposite* directions. Whatever is happening is
   getting worse with refinement.
3. **Hull-patch pressure.** Diagnostic mean pressure on the hull owner-cells grows and flips sign:
   `−0.125 Pa` (60 cells) → `+11.503 Pa` (90) → `−180.981 Pa` (135). `CT` tracks it. Whether this
   is cause, symptom or coincidence is not established here.
4. **Wall treatment at the refined levels.** The family refines 1.5× per direction; whether the
   `nut` wall function remains inside its valid `y+` range at the fine level was not measured by
   this rung and no `y+` figure is on record. **Stated as absent, not approximated.**
5. **Boundary-condition adequacy on the 5° wedge at the finer meshes.** Not investigated.

**Not diagnosed, deliberately.** No compute is being spent on this — cfd-supervisor's ruling. **This
is the FIRST thing a successor must resolve**: a convergence criterion alone will not settle a
1,300× discrepancy, and a successor that converges the residuals without resolving this will produce
a converged wrong answer.

---

## 5. §11 RE-HASH AND PRECONDITIONS — DISCHARGED

§11 line 470: *"Before any grade, re-hash and refuse on drift."* The four-row table gives **git blob
shas** — checked with `git hash-object` against disk, `git show HEAD:<path>`, and the freeze commit
`f67bbe14`. The lower checklist rows give **sha256** — checked with `sha256sum`. All agree. Nothing
drifted.

| §11 pinned git blob | path | disk | `HEAD` | `f67bbe14` |
|---|---|---|---|---|
| `9ab71b156d395d1e040851c524f0b81bb0e82ae1` | `cases/navier_class/SUBOFF/grade_suboff.py` | **PASS** | **PASS** | **PASS** |
| `dcddfe727ea9b85109f2000ea674add80de256c5` | `cases/navier_class/SUBOFF/build_suboff.py` | **PASS** | **PASS** | — |
| `86343dfc303cf639e267ac428007ea150401309f` | `cases/navier_class/SUBOFF/run_suboff_r1b_triple.sh` | **PASS** | **PASS** | **PASS** |
| `d893378817c823605c793e849d2800a1f4a28b5a` | `verification/runs/navier_class/SUBOFF/suboff_reference_ReL1p2e7.json` | **PASS** | **PASS** | **PASS** |

`grade_suboff.py` sha256 `5bb14d9b7d37a92288026b676607eb4292e24eb83ed8749c49a64e258a043766`.

**`HEAD` moved three times under this lane while it worked** — peers landed `a1e57706` (dafoam),
`3b1b4cae` (dafoam) and `b5750d99` (closure). **All four pins were re-verified at both `faf4ccfd`
and `b5750d99` and match at each.** None of those commits is this lane's: **the lane committed
nothing and did not touch the shared index.**

**The comparator predates the freeze, and the freeze predates compute.** `grade_suboff.py`'s last
commit `58595cb2` is an ancestor of `f67bbe14`, itself an ancestor of the 05:35:55Z launch. Rule 2's
requirement that the grading path be fixed at the pre-registration commit holds **on the git
record**, not by assertion.

### 5a. The §11 preconditions table

| §11 row | result |
|---|---|
| **fifteen mesh files vs the launcher `PIN` table** (sha256) | **15 / 15 PASS**, all five `constant/polyMesh/{points,faces,owner,neighbour,boundary}` at all three levels, against `run_suboff_r1b_triple.sh:97–112`. **The mesh that ran is the registered mesh.** |
| **the three `system/` dictionaries are one blob each** (sha256) | **PASS.** `controlDict f002ab4a10625dbb…`, `fvSolution f9a35242200934b3…`, `fvSchemes 62fc76f764ad4ac4…` — byte-identical across all three roots, each equal to its pin at `:118–120`. |
| **`endTime 2500`, `deltaT 1`, no `residualControl`** | **PASS** on disk: `endTime 2500`, `deltaT 1`, `startFrom startTime`, `stopAt endTime`, `writeControl timeStep`, `writeInterval 2500`; **no `residualControl` block** — which is precisely why the rung ran to a fixed iteration count instead of gating on convergence (§7). |
| **§7 caps transcribed without drift** | **PASS.** `SUBCAP_COREMIN = 46 / 103 / 231` (`:89`), `TIMEOUT_S = 2760 / 6180 / 13860` (`:90`), `CAP_COREMIN_REGISTERED = 400` (`:78`), against §7.4 (prereg 320–325: Σ 380 + 20 reserve = 400). Every figure matches. |
| **queue entry carries `grading_freeze` and the real freeze sha; `queue_entry_check.py --require-binding`** | **PASS on the queued copy.** `verification/queue/cfd/SUBOFF-R1B-TRIPLE.json` (blob `e18b8b7f`, landed by `3772c70f`) is **`ACCEPTED`** with `--require-binding`: `TEAM-BINDING: bound to cfd/`, `team=cfd case=SUBOFF-R1b-TRIPLE ranks=1 est=216.2 core-min`, `prereg_commit = f67bbe146ecb…`, and `_grading_freeze.paths` stamping `frozen_sha == disk_sha` for both comparators — independently confirmed above. **Caveat, stated:** the post-launch copy under `launched/` returns `REFUSED`, and the tool says why itself — *"not in `verification/queue/<team>/`, so TEAM-BINDING could NOT be checked. **This refusal is the ABSENCE of a check, not a failed one.**"* The two copies differ only by runner-appended `_launch` / `_field_classes` metadata. |
| **§4a run roots do not exist** | **NOT APPLICABLE POST-LAUNCH, correctly so.** A *pre-launch* precondition; the roots exist because the registered launch created them. Recorded so inapplicability is not mistaken for failure. Its purpose — that the age guard could hold — is discharged by §2, measured. |
| **the launcher cannot be run without grading** (§9 arms A/B/C) | **Not re-exercised by this lane** (requires running the launcher on a scratch copy). The queue entry records the 2026-09-10 exercise: arm A `--grade` → exit 2, `verdict=BLOCKED`; arm B SIGTERM mid-preflight → exit 143, verdict from the trap; **arm C, negative control**, trap removed → no verdict file. **Relayed from the entry, not re-measured.** |

---

## 6. COMPUTE — AND WHAT THE 173.23 CORE-MIN ACTUALLY BOUGHT

**Registered cap 400 core-min. Registered projection 216.2 core-min. Measured actual 173.23
core-min — 43.3 % of the cap. No sub-cap exceeded; no cap fired; no overrun.**

| level | wall s | ranks | core-min | sub-cap | timeout | vs sub-cap |
|---|---|---|---|---|---|---|
| coarse | 1174 | 1 | **19.567** | 46 | 2,760 s | 42.5 % |
| medium | 2513 | 1 | **41.883** | 103 | 6,180 s | 40.7 % |
| fine | 6707 | 1 | **111.783** | 231 | 13,860 s | 48.4 % |
| | | | **173.233** | **400** | | **43.3 %** |

**Corroborated by two independent instruments, not copied from the launcher.** Solver final
`ClockTime` 1169 / 2513 / 6707 s = **173.150 core-min**, agreeing to **0.083 core-min (0.05 %)** —
the difference is 5 s of coarse staging outside the solver. And the age-guard mtime margins of §2
(1174 / 2512 / 6707 s) reproduce the same wall times from file timestamps alone. **173.23 is
confirmed.**

**Basis: gross = cleaned = 173.23 core-min.** Cleaning rule **named**: `scripts/self_audit.py:175`,
`STALL_SECONDS = 3600.0`, applied by `check_ledger_stalls`, which that file's comment at `:170–174`
scopes to **night-ledger** rows that *"land in two tight wall-clock clusters and are shared across
independent solver families, which no per-solver cost mechanism can produce."* **No row here matches
it.** `fine`'s 6707 s is a single measured per-solver run: 2500 of 2500 iterations, `rc = 0`, largest
gap between consecutive `ExecutionTime` samples **5.15 s** (coarse 0.80 s, medium 1.84 s). Progress
was continuous; there is no stall to clean. **Flagged for the supervisor** — a literal reading of
3600 s would strip 111.78 of 173.23 core-min of genuine solver work.

### 6a. WHAT IT BOUGHT — a finding, and the word "recoverable" is struck

**The 173.23 core-min is NOT recoverable into a gradeable result by any regrade.** An earlier draft
of this record used "spent-but-recoverable"; **that framing was formed before the convergence
numbers were in hand and is withdrawn — cfd-supervisor, 2026-09-10.** Rule 5 clause 1 disqualifies
`fine` and `medium` on residuals, clause 2 disqualifies the triple as `DIVERGENT`, and §1(i) shows
two of three levels were still in motion at the cut. **Regrading with the correct argv returns
exactly `NOT A RESULT`** — computed, not predicted (§4a).

**What it did buy: a registered-in-advance truncation-and-convergence finding**, and that is a real
product. §10.1 of the frozen pre-registration stated *in advance* that `endTime 2500` was *"not a
prediction that convergence happens by 2500"* and that a `NOT_CONVERGED` at 2500 *"is a finding,
reported, never fixed by adding iterations after the fact."* The rung delivered exactly that
finding, at three refinements, with the residual ordering and the coefficient trajectories measured —
plus the open `CT` anomaly of §4 and two comparator defects (§3) that block the whole SUBOFF
family. **That is more than R1's 22.35 core-min purchased**, which produced no gradeable state and
no finding about convergence at all. **It is still not a result, and it is not recoverable into
one.**

**Waste, named separately (`COMPUTE_BUDGET_CHARTER` §6): 0 core-min.** No level was capped, no level
re-run, no solver compute discarded, and the argv defect cost **0 core-min** to discover — the
comparator refused on argv parsing before opening a case. **Waste is not laundered into the ratio.**

**Cost: $0.148 — DERIVED, NOT MEASURED.** 173.233 core-min = 2.8872 core-h at $0.0513/core-h
(c7a.4xlarge, **owner-stated**). The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Well inside the under-$25 pre-authorisation; no GPU compute.

### 6b. Rule-12 calibration: `actual / predicted = 0.802`

| level | §7.3 projected core-min | actual core-min | ratio |
|---|---|---|---|
| coarse | 26.02 | 19.567 | **0.752** |
| medium | 58.52 | 41.883 | **0.716** |
| fine | 131.67 | 111.783 | **0.849** |
| **triple** | **216.21** | **173.233** | **0.802** |

**Attribution: MISPREDICTION in the conservative direction.** §7.3 modelled
`wall_s = cells × 2500 × D + setup` at `D = 1.556056e-05` s/(cell·iter), the R1 **CONTENDED** rate.
Achieved `D` was `1.1768e-05` / `1.1196e-05` / `1.3281e-05` — 0.756× / 0.719× / 0.853×.

**Contention is excluded by direction, not by evidence — and that is the stronger argument.**
**Contention can only make a run slower, never faster. The run came in UNDER prediction at 0.802.
Therefore contention cannot explain the gap**, and no measurement of the box's load is needed to
establish it.

**CONTENTION WAS IN FACT PRESENT, and an earlier draft's disproof of it was wrong.** ANSYS **pid
316601**, started **2026-09-08T12:19:24Z**, still alive, with `log.rhoCentralFoam` at **346 MB** and
mtime **2026-09-10T15:58Z**, **ran through the whole of R1b's window** — measured by the
cfd-supervisor directly from the process. An earlier draft reported *"zero `log*` files modified
under `verification/runs/ansys_verification/` in the 05:35:55Z–08:30:00Z window"* and treated that
as disproof. **It is not disproof, and the instrument could not have done the job** — see the lesson
below. Contention was real; the favourable ratio is explained by the base rate having been
conservative, not by an idle box.

**NAMED INSTRUMENT LESSON — mtime is not a window probe.** *A continuously appended log has an mtime
equal to its LAST write, so a file written right through a window of interest shows an mtime of
`now`, outside the window, and a `find -newermt X ! -newermt Y` sweep reports it as absent.* An
mtime window sweep can prove a file **was** touched in a window; it **cannot** prove a process was
idle during one. To establish concurrency, read the **process** — start time and liveness — not file
timestamps. **This will recur** and is recorded here for the successor and for the lessons file.

**A genuine calibration finding, and it survives all of the above.** §7.3 rests on §2 Finding 1,
per-cell cost *"flat to 0.3 % across a 2.25× increase in cell count"*. Measured here, `D` **fell
4.9 %** coarse→medium then **rose 18.6 %** medium→fine. **Finding 1's flatness does not extend to
202,014 cells**, and the flat-`D` model **under-predicts** the fine level. The projection came in
under only because its base rate was conservative. **Any successor projecting beyond ~90k cells
should carry a growing-`D` term rather than inherit Finding 1 unexamined.**

The ledger row is drafted at `cases/navier_class/SUBOFF/SUBOFF_R1b_COST_CALIBRATION_ROW_DRAFT.md`
and is **not committed**.

---

## 7. WHAT A GENUINE SUCCESSOR MUST CARRY — AND THE TRAP IN IT

**The trap, first, because it is the one this rung is most likely to be walked into.** R1's own
freeze registered that a truncation finding is *"answered by a re-registered successor, never by
extending `endTime` after seeing residuals."* **A successor may therefore NOT simply pick a bigger
`endTime` because we have now seen where the residuals got to.** That is choosing a parameter to fit
an observed outcome, which is exactly the shape rule 2 forecloses — and it is the more tempting for
looking like straightforward engineering.

**A genuine successor must instead:**

1. **Gate on convergence, not on iteration count.** Register a **`residualControl`** criterion — a
   convergence threshold the solver itself enforces — with a **generous `endTime` as a cap only**,
   and an **explicit `NOT A RESULT` if the cap is reached.** The registered quantity is then "the
   converged state", which no amount of hindsight about residuals can tune.
2. **Resolve the open `CT` anomaly of §4 first.** A 1,300× discrepancy is not a convergence
   question. A successor that converges the residuals without resolving this produces a **converged
   wrong answer**, which is worse than this rung's honest `NOT A RESULT`.
3. **Repair the comparator, both blockers of §3**, and pin the repaired reader **before it is
   ever run** — the route the lab already has at `HEAD` in commit `faf4ccfd` (*"pre-registration +
   repaired comparator in ONE commit … the reader was committed BEFORE it was ever run"*).
   Specifically: `:369` cells-not-faces; `:368` the two-point plateau test, which needs a criterion
   over a window and a planted control that can see a drift. **And harden `:362`**, the `Aref`
   comparison, which exists and passed but is *conditionally armed* behind `if "Aref" in ref and
   ref["Aref"]` at a loose 3 % tolerance (§3c) — arm it unconditionally and tighten it.
4. **Repair the launcher argv** — `run_suboff_r1b_triple.sh:369` and
   `run_suboff_r1_triple.sh:305` both omit `--reference`. In a successor, not in place.
5. **Cost it against a growing-`D` model**, not Finding 1's flat `D` (§6b).
6. **Register `y+` at the hull as a reported quantity**, since candidate 4 of §4 cannot presently be
   assessed at all — no `y+` figure is on record for any level.

**This record does not write that registration.** Naming its requirements is as far as a results
record goes; the successor pre-registration is the cfd-supervisor's to write and freeze.

---

## 8. DISCLOSURE — AN OUT-OF-REGISTRATION GRADING INVOCATION OCCURRED

**On 2026-09-10, before the cancellation instruction reached it, a cfd `lab-lane` executed the
pinned comparator by hand with `--reference` supplied**, writing
`verification/runs/navier_class/SUBOFF/grade.R1b_triple.REPAIRED.out` and `…out.stdout`. The
comparator's `--selftest` was run first and returned `SELFTEST OK`; both rule-3 planted-zero
controls passed inside the grade, read back off disk; the invocation returned `rc = 0`. **No frozen
file was edited, no solver was launched, and the refusal evidence at `grade.R1b_triple.out` was
preserved byte-identical** (sha256 `f7dddab6…`, checked before and after).

**The numbers that invocation produced are NOT of record.** They are cited **nowhere in this
document as a result**, and they were reported to the cfd-supervisor **only because a supervisor's
ruling needed them** — specifically, the ruling that struck "recoverable" from §6a and the ruling
that `R1c` be cancelled. Both of those rulings are *against* the lab's interest in a tidy outcome
and could not have been made without the numbers.

**The invocation was nonetheless outside any registration.** The correct argv is fully determined by
the frozen document — §11 pins the reference file, so there was no free choice to exploit — but an
argv supplied **after** seeing that the registered one refused is still an argv chosen with
knowledge of the outcome, and rule 2 exists to foreclose that shape.

**The file remains on disk, untracked, at
`verification/runs/navier_class/SUBOFF/grade.R1b_triple.REPAIRED.out`. The cfd-supervisor chose NOT
to quarantine it**, on the ground that **deleting evidence of an out-of-registration read is worse
than disclosing it.** That choice is the cfd-supervisor's and is attributed to him.

**One residual exposure, recorded rather than argued away.** No successor can now claim its reader
was frozen before anyone had seen its output on these levels. **The mitigating fact:** gate D1, the
±10 % band, the `CT_ref = 3.6×10⁻³` anchor and the label were **inherited unchanged and frozen at
`f67bbe14` before compute** — there is no gate, threshold, cap or label left to choose, so the
specific harm rule 2 guards against has no purchase. **The exposure is to the reader's repair, not
to the gate**, and §7 item 3 is where it must be addressed.

---

## 9. WHAT IS AND IS NOT CARRIED FORWARD

**Carried forward:** a **registered-in-advance truncation-and-convergence finding** at three
refinements, on a mesh proven registered by 15/15 sha256 pins, from three runs complete under all
six clauses of rule 4 at 43.3 % of the registered cap. **R1's cap defect is closed** — a cap that
could not reach its own `endTime` has been replaced by one that did, at all three levels. Plus the
open `CT` anomaly (§4), two comparator blockers (§3), a compute calibration at 0.802 with a
measured refutation of Finding 1's flat `D` (§6b), and the mtime-as-window-probe instrument lesson
(§6b).

**Not carried forward:** any `CT` value, any observed order, any triple classification, any GCI, and
any statement whatever about SUBOFF drag. The rung reads `NOT A RESULT`; nothing quantitative
escapes it. **`R1c` as a zero-solver-compute regrade is cancelled** and is not carried forward
either.

**Nothing here is sent, filed, uploaded or posted (rule 7). Nothing was committed by the lane that
assembled it. No frozen file was edited. No solver was launched. The shared index was not touched.**

---

**Artifacts this record cites, all on disk:**

- `verification/campaign/SUBOFF_R1b_PREREGISTRATION.md` — frozen at `f67bbe14`
- `verification/runs/navier_class/SUBOFF/VERDICT.R1b_triple.txt` — the launcher's verdict artifact
- `verification/runs/navier_class/SUBOFF/grade.R1b_triple.out` — the **refusal** evidence, preserved
- `verification/runs/navier_class/SUBOFF/PROGRESS.R1b_triple.txt` — the per-level launch record
- `verification/runs/navier_class/SUBOFF/r1b_{coarse,medium,fine}/` — `log.simpleFoam`, `rc`, `STATUS.R1b_*`, `GRADE_PATH.txt`, `0/`, `0.orig/`, `2500/`, `constant/`, `system/`, `postProcessing/forceCoeffs/0/coefficient.dat`
- `verification/queue/cfd/SUBOFF-R1B-TRIPLE.json` (blob `e18b8b7f`, landed by `3772c70f`) and its post-launch copy under `verification/queue/cfd/launched/`
- `cases/navier_class/SUBOFF/grade_suboff.py` — the pinned comparator, blockers at `:368` and `:369`; the conditionally-armed `Aref` comparison at `:362`
- `cases/navier_class/SUBOFF/run_suboff_r1b_triple.sh` — the pinned launcher, argv defect at `:369`
- `verification/runs/navier_class/SUBOFF/grade.R1b_triple.REPAIRED.out` and `…out.stdout` — the out-of-registration output disclosed at §8, **not of record**
- `cases/navier_class/SUBOFF/SUBOFF_R1b_COST_CALIBRATION_ROW_DRAFT.md` — the rule-12 row, uncommitted
