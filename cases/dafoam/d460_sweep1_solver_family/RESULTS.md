# RESULTS — D460 sweep 1, solver family

> **NOT FILED ANYWHERE.** Nothing in this file has been sent, posted, emailed, uploaded,
> registered or commented outside this box, and nothing in it authorises a send. Filing is
> Sanaa's decision alone (`CLAUDE.md` rule 7). The D460 upstream defect draft remains
> **NOT FILED**.

| | |
|---|---|
| **Item** | **D460** sweep 1 — `cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md` §7 |
| **Question** | Is D460's class **conditioning / diagnosability** or **AD correctness**? |
| **Pre-registration** | `cases/dafoam/d460_sweep1_solver_family/PREREGISTRATION.md`, FROZEN at `538c9f51` (+AMENDMENT 1), AMENDMENT 2 at `f0448fab` (before first compute), ADDENDUM 3 at `a7abde10` (after first compute, harness repair, exception SPENT) |
| **Run root** | `/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/` |
| **Graded** | 2026-08-24T16:09:30Z (first invocation) / 16:12Z (captured transcript) |
| **VERDICT** | **`PASS`** |
| **CLASS** | **CONDITIONING / DIAGNOSABILITY** (§7 row 5) |
| **Written by** | DAFoam team, lab-lane, 2026-08-24, on the dafoam-supervisor's brief |

---

## 1. Grading path — the hash check, quoted

`CLAUDE.md` rule 2 requires that the file which grades **is** the file frozen at the
pre-registration commit. Checked twice: once before the F-SM arm was built, and again in the
same shell invocation as the grading run, immediately before the comparator executed.

| | sha256 |
|---|---|
| registered in `PREREGISTRATION.md` §8 | `239c1764c6b2ff8db5736c45f0f5f00f0debba0a4a93e745b080e1e641be7e94` |
| `sha256sum cases/dafoam/d460_sweep1_solver_family/analyse_sweep1.py` (disk) | `239c1764c6b2ff8db5736c45f0f5f00f0debba0a4a93e745b080e1e641be7e94` |
| `git show HEAD:cases/dafoam/d460_sweep1_solver_family/analyse_sweep1.py \| sha256sum` (committed blob) | `239c1764c6b2ff8db5736c45f0f5f00f0debba0a4a93e745b080e1e641be7e94` |

**All three equal. The grading is not void.** The comparator was not edited at any point in this
lane's work; ADDENDUM 3 §3g(1) had already asserted the same identity and it still holds.

Invocation, exactly as §8 registers it:

```
python3 analyse_sweep1.py <F-SM arm dir> <F-SM rc> <P-SM arm dir> <P-SM rc>
python3 analyse_sweep1.py /home/ubuntu/certonomous-runs/D460-sweep1-solver-family/fsm 0 \
                          /home/ubuntu/certonomous-runs/D460-sweep1-solver-family/psm 0
```

Exit code **0** (graded). Not 2 (refused), not 3 (usage). Full transcript preserved at
`/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/GRADE_sweep1.txt`.

### 1a. Planted controls (§8a, `CLAUDE.md` rule 3) — all three read back, on this invocation

The comparator runs them before it grades anything and exits 2 if any is invisible.

| plant | planted | read back |
|---|---|---|
| 1 | `he finalRes` × (1 + 1.234e-03): `0.06128001402295498` → `0.061355633560259304` | reader saw `rel = 1.2340e-03`, **OK** |
| 2 | a literal `nan` appended to a disk copy of the log | **detector fired**, OK |
| 3 | `cumulative` × 3 | reader saw **`3.000000x`**, OK |

**The zero reported in §4 below (`NaN_F = False`) comes from a reader shown, on this same
invocation and on disk, to see a non-zero.** Both polarities also stand on real files: the
detector reads `True` on `s1b.log` (F-GAMG, on record) and `False` on `patched.log`.

**A second planted zero, new to this lane and worth recording.** The A4-complement of §4 —
"`libDASolverADF` must NOT appear in P-SM's loaded-library set" — was a bare zero until this
run. The maps watcher reported for ARM P-SM:

```
LOADED_DASOLVER: libDASolver.so libDASolverADR.so
```

and for ARM F-SM, from the identical reader in the identical launcher:

```
LOADED_DASOLVER: libDASolver.so libDASolverADF.so
```

**F-SM is the positive control the pre-registration §4 anticipated.** The reader that reported
ADF absent in the control is now shown able to report ADF present. The A4-complement did **not**
degrade to the `useAD`-absent check of A1, and the degradation clause of §4 is not invoked.

---

## 2. Arms as built — the identity assertions

### 2a. ARM P-SM (control) — built and run by the previous lane, 2026-08-23; re-verified here

Assertions re-read by this lane before it relied on the arm:

| assertion | reading |
|---|---|
| **A1-P** (AMENDMENT 2 §2b) | `diff psm/runScript.py s1b/runScript.py` shows **exactly the four permitted differences and no others**: (1) added `    "printInterval": 1,`; (2) removed `"useAD": {...}`; (3) removed the Edit-4 `add_dvgeo` block; (4) the one changed `fwdad`-branch print, `("", "-9999", v)` where `s1b` has `("patchV", "1", v)`. **PASS** |
| **A2** | `diff psm/system/fvSolution s1b/system/fvSolution` = line 28 `GAMG` → `smoothSolver`, plus `nSweeps 1` inserted after line 31. Exactly §3's five lines. **PASS** |
| **A3** | `diff psm/system/controlDict s1b/system/controlDict` **empty** (`endTime 10`). **PASS** |
| **IDWARP md5** | `IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425`, `ASSERT_MD5 OK`. **PASS** |
| **A4-complement** | `LOADED_DASOLVER: libDASolver.so libDASolverADR.so` — no ADF. **PASS**, and now positively controlled (§1a) |

### 2b. ARM F-SM (discriminator) — built and run by this lane, 2026-08-24

Staged `cp -r /home/ubuntu/certonomous-runs/P3-a6-n16-ref/base → <run root>/fsm` at
2026-08-24T16:07:11Z, then `P3-a6-n16-ref/gen_arm.py` — **the same generator that built `s1b`** —
with `s1b`'s parameters plus the registered `printInterval`:

```
gen_arm.py <run root>/fsm fwdad endTime=10 tolDiff=1.0e12 useAD_dv=patchV useAD_idx=1 \
           minIters=1000000 printInterval=1
→ GEN OK arm=.../fsm task=fwdad endTime=10 tolDiff=1.0e12 useAD=patchV/1
```

then the §3 edit applied by an anchored replacement that **asserts the anchor count is 1 and
refuses otherwise** (`assert n == 1, "PREREG s3 anchor count %d -- EDIT REFUSED"`); the anchor
count was 1 and the edit applied.

| assertion | reading |
|---|---|
| **guard** (§11 / rule 4) | `fsm/` did not exist before staging; after staging the only time directories are `0/` and `0.orig/`, both from `base/`. No numeric time directory existed at launch. **PASS** |
| **A1-F** (AMENDMENT 1 §1a) | `diff fsm/runScript.py s1b/runScript.py` = **exactly one added line**, `    "printInterval": 1,`. Nothing else. **PASS** |
| **A2** | `diff fsm/system/fvSolution s1b/system/fvSolution` = exactly §3's five lines. Cross-checked: `diff psm/system/fvSolution fsm/system/fvSolution` is **empty** — the two arms' `fvSolution` files are **byte-identical**, which is the one-variable comparison asserted directly rather than inferred. **PASS** |
| **A3** | `diff fsm/system/controlDict s1b/system/controlDict` **empty**. **PASS** |
| **IDWARP md5** | `IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425`, `ASSERT_MD5 OK`. **PASS** |
| **A4** (§4 + AMENDMENT 1 §1c) | in-container `find / -name 'libDASolverADF.so' -type f \| xargs -r md5sum` returned **one** file: `44538ed4ac157ecb5dbb6850cf4bde64  /home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADF.so`. `ASSERT_A4_ADF_MD5 PRESENT`, `A4_FIND_LINES: 1`. **PASS — the arm is not VOID.** |

**A4's in-container path is now established by measurement, not guess:**
`/home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADF.so`. §4 deliberately declined to
state it because no container had been opened at the pre-registration commit; the `find` form
resolved it, and the md5 matches D460 §4's byte-identity to `dafoam/opt-packages:latest`.

### 2c. Launcher

`run_arm.sh` in the run root carries the ADDENDUM 3 §3f repaired body, verified by this lane
before launch: `bash -n` passes; `exit 91` / `exit 92` / `exit 93` each present once; source, the
IDWarp assert and the A4 `find` are newline-separated in the FOREGROUND; the only `&` inside the
container body is on the watcher subshell (line 35). sha256
`0e0b37a5732e002dfd7785420e0a38772470322b03f1d695931d90158a5b940e`. No further repair was made
and none was needed — the harness-repair exception (ADDENDUM 3 §3d) remains SPENT and unused by
this lane.

### 2d. Two departures, disclosed rather than discovered later

**(i) The two arms ran different `-task` arguments.** ARM P-SM ran `-task probe`; ARM F-SM ran
`-task fwdad`. The pre-registration registers the arm *files* (A1–A4) and never registers the
task string, so this is not an assertion failure — but it is a difference between the arms and is
named here.

*Why it is numerically inert, from `gen_arm.py`'s own injected source:* the `probe` branch is
`prob.run_model()` then a print of `scenario1.aero_post.CD`; the `fwdad` branch is
`prob.run_model()` then a print of the same `scenario1.aero_post.CD`. **One `run_model()` call
each, the same quantity read, the branch differing only in the print statement and a rank guard.**

*And it is inert by measurement, not only by code-reading:* gate **G0 held bit-identically for
ARM P-SM (`probe`) against P-GAMG, whose log `patched.log` ran a finite-difference driver task
entirely different from either** — a genuine cross-task pair, agreeing to the last printed digit
on all five G0 quantities. F-SM (`fwdad`) matches F-GAMG (`s1b`, also `fwdad`). The task branch
demonstrably does not perturb the primal.

`fwdad` was chosen for F-SM because it is the task that produced F-GAMG (`s1b.log`), F-SM's own
G0 reference under §6, and because its `FWDAD_*` line is the direct successor of the NaN on
record.

**(ii) `fsm/` was staged with `cp -r`, which reset the copied files' mtimes to 16:07:11Z.** The
`psm/` arm carries `base/`'s original mtimes, so the previous lane preserved them. The age guard
of §6a compares the `10/` fields against the arm's own `0/T`; a *newer* `0/T` makes that guard
**stricter**, never laxer, and the guard passed anyway (§3 below). No registered assertion reads
an mtime other than through that guard. Recorded because a silent difference in staging between
two arms of a one-variable comparison should never be left for a later reader to find.

---

## 3. Strict completion, §6a, clause by clause

The comparator prints these; both arms were also checked by this lane by hand before the
comparator ran, and the two readings agree.

| clause (§6a) | ARM F-SM | ARM P-SM |
|---|---|---|
| `rc == 0` | **OK** (ledger `rc=0`) | **OK** (ledger `rc=0`) |
| an `End` line | **OK** | **OK** (1 occurrence, `psm.log:697`) |
| last `Time =` == `endTime` (10) | **OK** (`Time = 10`) | **OK** (`Time = 10`) |
| `ExecutionTime` line count == 10 | **OK** (10) | **OK** (10) |
| `10/` directory exists | **OK** | **OK** |
| fields `T U p nut nuTilda alphat` present | **OK** (all six, as `.gz`) | **OK** (all six, as `.gz`) |
| **age guard** — every `10/` field NEWER than the arm's own `0/T` | **OK** | **OK** |

Age-guard evidence, measured to the nanosecond:

| arm | `0/T(.gz)` mtime (epoch) | earliest `10/` field mtime (epoch) | margin |
|---|---|---|---|
| P-SM | `1787519603.742696953` | `1787519609.610729299` (`meshPhi.gz`) | +5.87 s |
| F-SM | `1787587716.285096111` | all `10/` fields written 16:08 after it | positive for every field |

**Both arms are strict-complete. §7 row 1 does not fire.**

The comparator's own reader resolves `0/T` through the candidate list `0/T` then `0/T.gz`
(`analyse_sweep1.py:249`); in both arms the container wrote the time-0 fields compressed, so the
guard read `0/T.gz`. That is the registered reader's own behaviour, not a relaxation by this lane.

---

## 4. Gates — G0, G1, G2, G3

### G0 — validity. Bit-identical, 10 of 10, both arms.

Compared as printed strings against the **frozen** reference values of §6.

| quantity | ARM F-SM | frozen F-GAMG ref | | ARM P-SM | frozen P-GAMG ref | |
|---|---|---|---|---|---|---|
| `U0 finalRes` | `0.07283048716260687` | `0.07283048716260687` | **=** | `0.07283048716260687` | `0.07283048716260687` | **=** |
| `U1 finalRes` | `0.003381492464613624` | `0.003381492464613624` | **=** | `0.003381492464613624` | `0.003381492464613624` | **=** |
| `U2 finalRes` | `0.07283327010584476` | `0.07283327010584476` | **=** | `0.07283327010584476` | `0.07283327010584476` | **=** |
| `he initRes` | `0.9999999999746546` | `0.9999999999746546` | **=** | `0.9999999999746546` | `0.9999999999746546` | **=** |
| `he finalRes` | `0.06128001402295498` | `0.06128001402295498` | **=** | `0.06128002514528321` | `0.06128002514528321` | **=** |

**G0 HOLDS for both arms. §7 row 2 does not fire.** The reference logs themselves were re-read
from disk by the comparator and confirmed still on their frozen values (`[1]` of the transcript,
both `OK`) — a reference log that had moved would have been a refusal.

Note the two `he finalRes` columns still differ from each other in the 8th significant figure
(`...01402295498` vs `...02514528321`) — **the D460 difference is still present under
`smoothSolver`.** It has not been removed; §5 below is about what it does, not whether it exists.

### G1 — control. `NaN_P == False`, P-SM strict-complete.

**G1 HOLDS. §7 row 3 does not fire.** The separate finding §6 contemplated — "`smoothSolver` on
`p` destabilises even the plain primal" — is **not** made: the control completed 10 iterations,
`rc=0`, no NaN anywhere in `psm.log`, and printed a finite `PROBE_CD: 0.025518939045363655`.

### G2 — discriminator. `NaN_F == False`.

**No NaN anywhere in `fsm.log`**, over the whole run, by the registered detector
(`RE_NAN`, the explicit non-letter-boundary form). The forward-AD arm printed a finite value
where the GAMG forward-AD arm on record printed `nan`:

| | F-GAMG (`s1b.log`, on record) | **F-SM (this run)** |
|---|---|---|
| final `FWDAD_*` line | `FWDAD_DV: patchV FWDAD_IDX: 1 FWDAD_DERIV: nan` | `FWDAD_DV: patchV FWDAD_IDX: 1 FWDAD_DERIV: 0.002552003248356442` |
| NaN tokens in log | 14 | **0** |

**§7 row 4 does not fire.**

### G3 — band. `r = |cum_F| / |cum_P|` at `Time = 1`, threshold 2.0.

| | `cumulative` at `Time = 1` |
|---|---|
| ARM F-SM | `-0.08515074416090457` |
| ARM P-SM | `-0.08794505498506013` |
| **`r`** | **`0.968227`** |
| GAMG pair on record | `r = 10.029307311562496` |

**`r = 0.968227 ≤ 2.0`. Inside the registered band.**

---

## 5. Verdict

Evaluated in §7's frozen order: row 1 no (both strict-complete) → row 2 no (G0 holds) → row 3 no
(`NaN_P == False`) → row 4 no (`NaN_F == False`) → **row 5 fires**.

> ## VERDICT: `PASS`
> ## CLASS: CONDITIONING / DIAGNOSABILITY

**§7 row 5**, verbatim from the frozen table: *`NaN_F == False` and `r ≤ 2.0` → `PASS`,
CONDITIONING / DIAGNOSABILITY.*

**What it buys D460**, per §7's own table: the upstream ask is a **documentation + warning
change**, and the report attaches to `DAFoam/OpenFOAM-AD` issue #2 as a second,
**opposite-polarity** instance — GAMG being the configuration that fails here, where #2 names
GAMG/GaussSeidel as the one that works. **The more serious AD-correctness reading (row 4) is not
reached.** Nothing about this is filed, sent or prepared for sending; see the banner.

### 5a. The mechanism behind `r`, stated because the ratio alone flatters the result

`r` is a **ratio between builds**, and it fell for a reason that the ratio hides. Both cumulative
continuity magnitudes at `Time = 1` **grew** when `GAMG` was replaced by `smoothSolver`:

| | GAMG (on record) | `smoothSolver` (this run) | change |
|---|---|---|---|
| `\|cum_F\|` (forward-AD) | `0.05058272456310364` | `0.08515074416090457` | **×1.683** |
| `\|cum_P\|` (plain) | `0.00504349133910657` | `0.08794505498506013` | **×17.437** |
| `r = \|cum_F\|/\|cum_P\|` | `10.029307` | `0.968227` | **÷10.36** |

**The amplification collapsed mainly because the CONTROL's own continuity error grew 17.4×, not
because the forward-AD arm's error fell — it rose.** The registered band gates the ratio, the
ratio is inside it, and `PASS` stands exactly as frozen (a gate may not be re-argued after the
fact). But the honest reading of the *mechanism* is narrower than "the amplification collapsed":
under `smoothSolver` the two builds' first-iteration continuity errors **converge on each other
at a worse absolute level**, and the 8th-figure AD difference stops being the dominant term
because a larger common term now dominates both. That is still a conditioning story — the AD
difference is not amplified into a NaN — but it is not a story about the solver being better.

### 5b. Not registered, not gated, recorded for the supervisor and not interpreted

- **Neither arm is a converged solve.** `endTime 10`, `primalMinIters 1000000`: both arms are
  10-iteration probes by construction. Final `Total Residual Norm2` is `5.78e11` (F-SM) and
  `1.33e10` (P-SM). Large, finite, and **outside every registered observable** — recorded, not
  read as a finding. Nothing in §5–§7 depends on them.
- **Pressure sweeps exploded under `smoothSolver`**, which is the expected price of dropping
  multigrid and is the same in both builds: `p nIters` at `Time = 1` is 206 (F-SM) and 425
  (P-SM), against 5 (F-GAMG) and 7 (P-GAMG); summed over the ten iterations, 878 (F-SM) and
  5021 (P-SM).
- **Ten-iteration `CD`-channel values**: F-SM's `FWDAD_DERIV` field prints
  `0.002552003248356442`, P-SM's `PROBE_CD` prints `0.025518939045363655`. In this harness the
  `FWDAD_DERIV` label carries whatever `scenario1.aero_post.CD` returns
  (`gen_arm.py`'s injected `fwdad` branch), so the two are not necessarily the same quantity in a
  forward-AD build. Flagged as an unregistered observation; **this lane does not interpret it**,
  and no verdict here rests on it.

---

## 6. Predictions, scored

| # | prediction | registered | measured | confidence | **score** |
|---|---|---|---|---|---|
| **P1** | G0 holds — exact string equality on `U0/U1/U2 finalRes`, `he initRes`, `he finalRes` | equality | **10 of 10 identical**, both arms | 0.95 | **HIT** |
| **P2** | the control completes 10 iterations with no NaN | `NaN_P == False` | `False`; P-SM strict-complete | 0.90 | **HIT** |
| **P3** | **THE DISCRIMINATOR** — F-SM does not reach NaN | `NaN_F == False` | `False`; 0 NaN tokens vs 14 in `s1b.log` | **0.55** | **HIT** |
| **P4** | the iteration-1 continuity amplification collapses | `r ≤ 2.0` vs GAMG's `10.029307` | **`r = 0.968227`** | 0.50 | **HIT** |
| **P5** | `p nIters` differs between F-SM and P-SM by **fewer** sweeps than the GAMG pair's 7 vs 5 | not gated, recorded | GAMG pair differ by **2**; the SM pair differ by **219** (206 vs 425) | — | **MISS** |

**4 HIT, 1 MISS.** P5 is the miss and it is not a near miss: the registered expectation was that
removing multigrid would bring the two builds' sweep counts closer together, and instead it drove
them two orders of magnitude further apart. P5 was deliberately left ungated, so it changes no
verdict — but it is the one place the lane's model of the mechanism was wrong, and it is the
finding most worth carrying forward. It also sits oddly beside §5a: the two builds' *continuity
errors* converged while their *sweep counts* diverged.

The two low-confidence registrations, P3 at 0.55 and P4 at 0.50, both came in. The reason the
confidence was low — `OpenFOAM-AD` #2's opposite polarity (§5 of the pre-registration) — is
**untouched by this result**; see §8(3).

---

## 7. Cost — `CLAUDE.md` rule 12

Unit: **core-minutes** = wall s × ranks ÷ 60. Both arms np = 1, `--cpus=1`, `--memory=12g`.

### 7a. Per arm, gross and cleaned

| arm | wall s | ranks | **core-min** | peak RSS GiB | predicted (§9) | ratio actual/predicted |
|---|---|---|---|---|---|---|
| P-SM attempt 2 (graded) | 230 | 1 | **3.833** | 0.0718457 | 1.5 | **2.56×** |
| F-SM (graded) | 52 | 1 | **0.867** | 0.794629 | 3.5 | **0.248×** |
| **graded-arm total** | 282 | 1 | **4.700** | — | **5.0** | **0.940** |
| *P-SM attempt 1 — VOID, **WASTE*** | 1 | 1 | ***0.017*** | unmeasured | — | — |
| **charged to the item** | 283 | 1 | **4.717** | — | — | — |

**Cleaned = gross.** The `COMPUTE_BUDGET_CHARTER` §2 stall rule removes rows over 3600 wall s;
the longest row here is 230 s, so **no row is removed and cleaned equals gross for every line
above**. Stated explicitly rather than left implied.

**Waste is named, never absorbed** (`CLAUDE.md` rule 12, charter §6): **0.017 core-min**, ARM
P-SM attempt 1, `rc=134` in 1 s, void by its own registered assertions
(`PREREGISTRATION.md` ADDENDUM 3 §3a, §3e). It is charged against the §9 ceiling and is **kept
out of the ratio**, whose denominator prices arms that were expected to grade.

**Ceiling.** §9 registers a **HARD CEILING of 20.0 core-min**. Charged: **4.717**, i.e. 23.6% of
the ceiling; **15.283 core-min remain unspent**. **No overrun occurred and no budget was
re-requested.**

### 7b. Dollars — derived, not measured

Rate **$0.0513/core-h**, c7a.4xlarge, **owner-stated 2026-08-21/22 and therefore
reported-by-owner, NOT measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

| | core-min | core-h | **$ derived** |
|---|---|---|---|
| P-SM attempt 2 | 3.833 | 0.063883 | **$0.003277** |
| F-SM | 0.867 | 0.014450 | **$0.000741** |
| graded-arm total | 4.700 | 0.078333 | **$0.004019** |
| waste (attempt 1) | 0.017 | 0.000283 | **$0.0000145** |
| **item total** | **4.717** | 0.078617 | **$0.004033** |

Every figure in this table is **derived** at a reported-by-owner rate. Far under the $25
pre-authorisation; **and a blanket authorisation is not a per-item read (`CLAUDE.md` rule 9) —
this item was costed individually in §9 before it ran, and its ceiling was this item's ceiling,
not a floor for anything else.** No GPU was involved.

### 7c. Estimate-versus-actual, with the gap attributed

**Ratio actual/predicted = 4.700 / 5.0 = 0.940** on the graded arms (0.943 if the void attempt is
folded in — quoted only so the reader can see both; the 0.940 figure is the calibration number).

The aggregate is within 6% of prediction, and **that agreement is a coincidence of two large
errors in opposite directions.** The per-arm ratios, 2.56× and 0.248×, are the informative
numbers. Attribution:

1. **Misprediction, P-SM, +2.333 core-min (the dominant term).** §9 priced P-SM from `s1a`'s
   measured 0.95 s/iter × 10 iterations × a ~9× inflation for `smoothSolver` sweeps. **The solve
   was never the cost.** Measured from the arm's own log: `ExecutionTime = 6.92 s`,
   `ClockTime = 7 s` for **all ten iterations**. The other **223 s of the 230 s wall is
   non-solver harness time** — container start, `loadDAFoam.sh`, the IDWarp import and md5, the
   A4 **whole-container-filesystem `find /`**, OpenMDAO/mphys setup, and the `mphys.html` +
   `reports/` writes. **The estimate was wrong in structure, not in magnitude: it modelled a
   10-iteration arm as iteration-dominated when a 10-iteration arm is startup-dominated.**
   §9's per-iteration basis assigned zero cost to fixed overhead that turned out to be ~97% of
   the bill.
2. **Misprediction, F-SM, −2.633 core-min.** §9's F-SM figure was explicitly a **two-branch
   maximum**: *"if healthy, as P-SM; if NaN-contaminated, the measured `s1b` cost … 5.383
   core-min"*. It was therefore conditioned on the very outcome the experiment existed to
   determine, and it resolved to the cheap branch. This is **not** a modelling error and should
   not be counted as one — a conditional estimate that names both branches is the honest form
   when the branch is what is under test. What it does mean is that the **pre-registered total
   of 5.0 was an upper bound presented as a point estimate**, and future two-branch items should
   register the interval, not the max.
3. **Contention — inferred from two readings, NOT measured, direction only.** P-SM ran at
   `load1 = 14.50` (ADDENDUM 3 §3c) with the heat-transfer family's solvers live; F-SM ran at
   `load1 = 4.31` (§10 preflight, 16:07:59Z). Non-solver phase: P-SM 223 s, F-SM
   52 − 18 = 34 s — a **6.6× gap on a 3.4× load difference**, with both arms `--cpus=1` and
   running the byte-identical launcher. Some part of item 1's overhead is therefore contention
   rather than intrinsic cost. **No per-phase instrumentation exists in this harness, so the
   split cannot be measured and is not claimed.** Item 1's structural finding stands either way:
   whatever its cause, the overhead is real and §9 priced it at zero.
4. **Waste, 0.017 core-min**, named at §7a and excluded from the ratio.

**Transferable calibration rule this item earns:** *for a short DAFoam arm (order 10 iterations),
estimate fixed harness overhead FIRST — measured here at 34–223 s per container — and add the
solve second; a per-iteration basis borrowed from a 1,000-iteration arm under-prices a
10-iteration arm by roughly the overhead, which dominates it.*

Landed as row **C-22** in `docs/COST_CALIBRATION.md`, commit `f62ec7ed`.

> **Disclosed defect in that commit's own subject line.** The id was re-derived from the tail of
> `git show HEAD:docs/COST_CALIBRATION.md` **inside the commit's shell invocation**, as
> `CLAUDE.md` rule 11 requires, and came back **C-22** — four peer rows (C-18 closure,
> C-19 closure, C-20 verification, C-21 heat-transfer) had landed between this lane's earlier
> read of the file and its commit. **The row is correct: it is `C-22` and carries no other id.**
> But the commit's *subject line* was composed before that re-derivation and says `C-18`, which
> is now another team's row. **The subject of `f62ec7ed` is wrong; the row it landed is right.**
> No correction row is filed in the ledger, because rule 2 of that file's append rules calls for
> a correction row only when a *row's data* is wrong, and this row's data is not. The commit
> message is left unrewritten rather than amended — history is not rewritten to hide a mistake,
> it is annotated here.
>
> *This is the rule-11 hazard behaving exactly as the rule anticipates: re-deriving at commit
> time caught a four-row collision that a pre-computed id would have silently collided with.
> The lesson is narrower — re-derive the id for the **commit message** in the same invocation
> too, not only for the row.*

---

## 8. What this sweep does NOT establish — §13, re-affirmed against what was measured

§13 of the pre-registration is restated here **as it now reads against real numbers**, because a
`PASS` is the moment a scope limit is most likely to be quietly dropped.

1. **The scope is one case, one solver, one mesh, np = 1, ten iterations.** D460 §7 sweep 2 (case
   family, ~10 core-min) is unrun and **is not authorised by this document**. Nothing here
   generalises to another case or to a converged solve — see §5b, neither arm converged, by
   design.
2. **Which build is *right* is untouched.** D460 §10.4 stands. The 8th-significant-figure
   `he finalRes` difference is **still present** under `smoothSolver` (§4, G0 table); this sweep
   measured what that difference *does*, never which side of it is correct.
3. **`OpenFOAM-AD` #2 is excluded as a CONFOUND, not connected or disconnected as a MECHANISM.**
   The arm avoided PBiCGStab/DILU by construction, so #2 cannot explain this result. The
   opposite-polarity puzzle that §5 of the pre-registration registered as the reason P3's
   confidence was only 0.55 — the maintainer naming GAMG/GaussSeidel as the configuration that
   *works* — **is exactly as unresolved after this run as before it.** P3 coming in does not
   dissolve it.
4. **Nothing about parallel behaviour.** Every arm np = 1, undecomposed (`DAFOAM_CHARTER.md` §5).
5. **No performance or memory claim.** A NaN-contaminated wall time is not an AD cost factor
   (D460 §10.7), and the wall times in §7 are dominated by harness overhead and host contention —
   they are a *budget* record, not a solver-performance measurement. The peak-RSS figures
   (0.0718 GiB P-SM, 0.795 GiB F-SM) are `docker stats` samples at 20-s intervals: P-SM's is
   **almost certainly an under-sample**, not a real 72 MiB peak, since the identical case in F-SM
   sampled 0.795 GiB and `s1b` measured 0.636 GiB. Recorded as unreliable rather than quoted.
6. **The §8 `-1e10` false-convergence finding is untouched** by this sweep.
7. **New to this results file:** §5a's mechanism reading means this sweep does **not** establish
   that `smoothSolver` is a better pressure solver for this case. It establishes that the
   *forward-AD/plain divergence* is not amplified under it. Those are different claims and only
   the second is graded.

---

## 9. Candidate records — DRAFTS for the dafoam-supervisor, not landed by this lane

This lane does not write `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/DOCKET.md` or
`docs/LAB_STATE.md`. The following are drafted here for the supervisor to assign numbers to and
land, per `CLAUDE.md` rule 11 (ids re-derived from the tail at commit time, never counted).

### 9a. Lesson candidate — a short solver arm is startup-dominated, and a per-iteration cost basis prices it at zero

> A cost estimate built from a long arm's seconds-per-iteration under-prices a short arm by
> roughly the whole fixed overhead. D460 sweep 1's ARM P-SM was priced at 1.5 core-min from a
> 1,000-iteration neighbour's 0.95 s/iter and cost 3.833 — but its *solver* ran 6.92 s
> (`ExecutionTime`, all ten iterations) of a 230 s wall. **223 s, 97% of the bill, was container
> start, environment load, an IDWarp md5, a whole-filesystem `find /`, OpenMDAO setup and report
> writing** — none of which a per-iteration basis can see. Estimate fixed harness overhead first
> and the solve second whenever the arm is order-10 iterations.
> *Artifacts:* `certonomous-runs/D460-sweep1-solver-family/{psm.log,fsm.log,ledger.txt}`;
> `cases/dafoam/d460_sweep1_solver_family/RESULTS.md` §7c.

### 9b. Lesson candidate — a two-branch prediction registered as its maximum is an upper bound wearing a point estimate's clothes

> D460 sweep 1 §9 priced ARM F-SM at 3.5 core-min as *"if healthy, as P-SM; if NaN-contaminated,
> 5.383"* — an estimate conditioned on the outcome the experiment existed to determine. It came
> in at 0.867 (0.248×). Naming both branches was the honest move; collapsing them into one
> number in the total was not. **Register the interval, and let the total carry both ends.**
> *Artifact:* `RESULTS.md` §7c item 2.

### 9b-ii. Lesson candidate — re-derive an append-only id for the COMMIT MESSAGE too, not only for the row

> `CLAUDE.md` rule 11 is kept for the row and dropped for the subject line. This lane re-derived
> the next `docs/COST_CALIBRATION.md` id inside the commit's own shell invocation and got
> **C-22**, four higher than the C-18 it had read minutes earlier — peers had landed C-18…C-21 in
> between, exactly as the rule warns. The row is right; the commit subject, composed before the
> re-derivation, says C-18 and is wrong (`f62ec7ed`). **Compose the subject from the same shell
> variable that numbers the row, or leave the id out of the subject entirely.**
> *Artifact:* `RESULTS.md` §7c, disclosure block.

### 9c. Numerics candidate — `smoothSolver`/`GaussSeidel` on `p` for `DARhoSimpleCFoam` transonic

> Replacing `GAMG` with `smoothSolver`/`GaussSeidel`/`nSweeps 1` in the `"(p|p_rgh|G)"` block of
> this transonic `DARhoSimpleCFoam` case (CRM wing, `transonicPCOption 1`), holding everything
> else fixed: pressure sweeps at `Time = 1` rise from 5→206 (forward-AD build) and 7→425 (plain
> build); the first-iteration cumulative continuity magnitude rises ×1.68 and ×17.4 respectively;
> and the forward-AD primal that reached `nan` under `GAMG` completes ten iterations with no NaN.
> **The 8th-significant-figure `he finalRes` difference between the two builds persists
> unchanged** — it is not amplified, not removed.
> *Artifacts:* `GRADE_sweep1.txt`, `fsm.log`, `psm.log` in
> `/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/`.

### 9d. Numerics candidate — A4's in-container path, measured

> `libDASolverADF.so` lives at `/home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADF.so`
> in `dafoam-idwarp-rot:v1`, md5 `44538ed4ac157ecb5dbb6850cf4bde64`, one file on the whole
> container filesystem. The pre-registration declined to guess this path and wrote the assertion
> as a `find`; the `find` resolved it. Sibling `libDASolverADR.so` and `libDASolver.so` sit in
> the same directory, and `/proc/<pid>/maps` sampling distinguishes which a live arm loaded —
> ADR for a plain build, ADF for a forward-AD build.

### 9e. Docket candidate

> **D460 sweep 1 (solver family) — CLOSED, `PASS`, class CONDITIONING / DIAGNOSABILITY.**
> 4.717 core-min of a 20.0 ceiling. D460's class question is answered for this case: the upstream
> ask is documentation + warning, not an AD fix. **D460 sweep 2 (case family) remains unrun and
> unauthorised.** The upstream draft stays **NOT FILED**. Open and unresolved: the
> `OpenFOAM-AD` #2 opposite-polarity puzzle (§8 item 3), and P5's miss (§6) — removing multigrid
> drove the two builds' sweep counts 219 apart where the registered expectation was fewer than 2.

### 9f. For the supervisor's judgement, flagged not decided

The §5a mechanism reading — that `r` fell mainly because the *control's* continuity error grew
17.4× — is a caveat this lane believes belongs in any downstream statement of the D460 class,
including the upstream draft if it is ever revised. **Whether the D460 record gets a dated
addendum saying so is the supervisor's call**, and D460 is a frozen committed record that this
lane does not edit (`CLAUDE.md` rule 6).

---

## 10. Provenance of every number in this file

| number | artifact |
|---|---|
| verdict, class, gates, `r`, NaN readings, G0 strings, completion clauses | `/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/GRADE_sweep1.txt` |
| `rc`, wall s, core-min, peak RSS, `ASSERT_MD5`, `ASSERT_A4_ADF_MD5`, `LOADED_DASOLVER` | `/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/ledger.txt` (append-only; the void attempt-1 row stands above the graded rows) |
| `ExecutionTime`, `ClockTime`, `p nIters`, `FWDAD_DERIV`, `PROBE_CD`, residual statistics, A4 `find` output | `.../fsm.log`, `.../psm.log` |
| field lists and mtimes for the age guard | `.../fsm/{0,10}/`, `.../psm/{0,10}/` |
| frozen reference values | `PREREGISTRATION.md` §6, and the reference logs `/home/ubuntu/certonomous-runs/P2-a6-n16/patched.log`, `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/s1b.log`, both re-read from disk and confirmed on their frozen values by the comparator |
| launch gate reading | `preflight.sh` output, quoted verbatim immediately below |

**§10 launch gate, ARM F-SM, taken as its own command at 2026-08-24T16:07:59Z:**

```
PREFLIGHT OK load1=4.31 MemAvailableGiB=26 tries=0
```

**MemAvailable 26 GiB against the registered `≥ 12 GiB` floor — SATISFIED.** `load1 = 4.31`
**recorded and not gated**, per §10's registered decision; `preflight.sh` was invoked with
`LOADCAP=60`, the same effectively-open load setting §10 describes and the same one under which
ARM P-SM launched. The memory gate is the binding one and it was met with a 14 GiB margin.

---

**Nothing in this file has been sent, filed, posted, uploaded or pushed.**
