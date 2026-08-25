# VMFL003 — Pressure Drop in Turbulent Flow Through a Pipe: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the run it records is sent,
emailed, uploaded, filed, posted, registered or commented outside this box
(CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The manual is
proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**Run 1 of VMFL003.** Graded 2026-08-25T02:40:33Z by `ansys-lane-opus` (Opus 5) with the frozen
comparator, **unmodified**. This file does not revise `PREREGISTRATION.md`.

---

## 1. THE VERDICT

> # `NOT A RESULT`
>
> printed by `grade_vmfl003.py` (blob `15b14d40f166cc31770ead452c27905332670c97`,
> byte-identical to HEAD, `--verify-frozen HEAD` rc=0, `--selftest` **60 checks,
> 0 failures** re-run as a gate on this grading).

**Why, in the frozen order of §6.** Step 1 fired before the triple was formed:
**all three levels failed the registered iterative-convergence residual leg**
(final *initial* residuals of p, Ux, k, ε each < 1.0e−8).

| level | p | Ux | k | ε | gated verdict |
|---|---|---|---|---|---|
| L1_250x5 | 6.798e−08 | 2.451e−06 | 2.061e−06 | 1.678e−06 | **fails, 4 of 4** |
| L2_500x5 | 7.316e−08 | 8.882e−07 | 1.203e−06 | 1.417e−06 | **fails, 4 of 4** |
| **L3_1000x5** | 2.361e−10 ✓ | 4.624e−09 ✓ | 1.954e−09 ✓ | **2.523e−08 ✗** | **fails on ε alone, by 2.5×** |

`Uy`/`Uz` are **printed, not gated**, exactly as frozen (§6) — their wedge
normalisation is degenerate in the developed region. They are not the reason.

**This outcome was pre-registered.** §4.5 declared the iteration counts
6000/8000/12000 **estimates**, and §11 item 5 registered this exact branch before any
compute: *"If a level misses either convergence leg it is `NOT A RESULT` and re-runs
at a longer endTime as a NEW RUNG."* **No gate, threshold, cap or label moved.**

## 2. THE GATE AND THE COLEBROOK DIAGNOSTIC — REPORTED WITH EQUAL PROMINENCE

**Both are given the same weight here, as the supervisor's binding condition
requires. Neither is relegated to a footnote.**

| | value | reference | deviation | band | met? |
|---|---|---|---|---|---|
| **THE GATE** (§3.1) | **Δp = 20800.824487444752 Pa** | manual target **21744 Pa** | **−4.337635727351215 %** | 2.5 % | **NO** |
| **THE COLEBROOK DIAGNOSTIC** (§3.2) | same | exact **21792.879830032474 Pa** | **−4.552199389548252 %** | 2.0 % | **NO** |
| **f_dev, developed region** (§3.3) | **0.027147309070475995** | Colebrook **0.028464169573919965** | **−4.626379490974265 %** | 2.0 % | **NO** |

`gate_verdict_before_rule5` = **`GATE FAIL`**. Rule 5 then turned it into
`NOT A RESULT` — **the permitted direction, and only that direction.**

**SAY IT PLAINLY, AND IT MATTERS MORE THAN THE PROCEDURAL VERDICT: the deviation is
NOT a convergence artefact and a longer run will not rescue it.** L2→L3 moved Δp by
**0.161 Pa on 20 800 Pa — 7.8 parts per million.** The answer is converged to five
significant figures and sits **4.34 % below the target**. A re-run at a longer endTime
would clear the ε clause and would then, on this evidence, return **`GATE FAIL`**, not
`PASS`. **Nothing here should be read as a `PASS` awaiting paperwork.**

**The band declaration of §3.4 stands and is restated as instructed.** The 2.5 % band
was declared in advance to **pass both Ansys solvers** (Fluent −1.214 %, CFX −0.018 %),
and **that declaration is why it is acceptable**: a band tighter than **1.210428 %**
would be gating the manual's own inter-code disagreement rather than this lab's
accuracy. **The lab missed a band built to be passable by both commercial codes, by
3.6× the band.** That is the finding.

## 3. WHAT THE DEVIATION IS — the model, not the mesh, and the numbers separate them

**§7a named the wall treatment as the real risk before the run. It was right.**

- **Axial discretisation channel: 7.8 ppm.** d21 = −0.161 Pa, d32 = −2.006 Pa on
  20 800 Pa. The triple is `CONVERGING`, monotone, R = 0.0804.
- **Wall-treatment channel: 1.7356 %.** The §4.4 ladder — N_r = 3/4/5/6 at fixed
  N_x = 500, spanning y⁺ 60.02 → 31.66 — moves Δp across a **1.74 % spread.**
- **These differ by a factor of ~2200.** The channel the GCI can see is negligible; the
  channel it structurally **cannot** see is **70 % of the whole gate band**. §4.2's
  declared honest cost — *"a small GCI will NOT license calling the remaining deviation
  numerical"* — is now **measured**, not argued.
- **f_dev is the clean model statement**, free of entrance and BC effects:
  **this lab's `kEpsilon` + `nutkWallFunction` under-predicts developed turbulent pipe
  friction by 4.63 % at Re = 13 692.**

**An internal cross-check that came out right, and it constrains the story.**
f_dev deviates −4.626 % while Δp deviates −4.338 %; the difference is **+0.29 %**, which
lands inside §3.4's independently-budgeted entrance excess of **+0.28 … 0.70 %**. The
entrance term behaved as predicted, so it is not hiding the discrepancy either.

**The residual after every declared systematic is removed is ≈ −4.3 %, one-signed, and
unexplained by anything this pre-registration budgeted.** The systematics budget totted
to ≈ 0.98 % worst case; the miss is **4.4× that**. This is not attributed here.

## 4. y⁺, AND THE FIXED-N_r DECISION — the design call of this case

**Declared one-way `NOT A RESULT` band: mean wall y⁺ ∈ [25, 65]. ACHIEVED and HELD.**

| level | y⁺ average | y⁺ min | y⁺ max | predicted | vs prediction |
|---|---|---|---|---|---|
| L1_250x5 | **37.60534067864** | 29.453 | 37.785 | 40.835033970764385 | −7.91 % |
| L2_500x5 | **37.60077854753** | 25.503 | 37.787 | 40.835033970764385 | −7.92 % |
| **L3_1000x5** | **37.60014411059** | **23.812** | 37.788 | 40.835033970764385 | **−7.92 %** |

**The clause held; it was not close to firing** (37.60 sits mid-band, 12.6 above the
floor). The prediction rested on u_τ from the *Colebrook* f; the lab's f came in 4.6 %
low, so y⁺ landed 7.9 % low — **§11 item 4 forecast exactly this arithmetic**, including
that it would stay well inside the band.

**An honest caveat, volunteered.** The **minimum** wall y⁺ at L3 is **23.812**, below
the band's lower edge. The frozen clause (§5) is declared on the **average**, so the
clause held as written and the comparator is correct. But the band's *purpose* is
wall-function validity, and a few near-inlet faces sit below y⁺ = 25. This is disclosed,
not buried; it is **not** offered as an explanation of the 4.3 % deviation, whose
magnitude the developed-region f_dev already fixes far from the inlet.

**THE FIXED N_r = 5 DECISION HELD, EXACTLY AS DESIGNED.** y⁺ average across the three
Roache levels: **37.60534 / 37.60078 / 37.60014** — a relative spread of **1.4e−4**.
The wall treatment was **identical at every level**, so the axial triple measured
discretisation and **not** a wall-function regime change. §4.2's R⁺ = 408 constraint —
that a ratio-2 *radial* triple cannot fit inside [30, 0.2R⁺] below Re ≈ 21 252 — was
sound, and the design it forced worked.

## 5. THE ROACHE TRIPLE — reported, and NOT trusted, for a stated reason

`CONVERGING`, monotone, **R = 0.08041546433725018**, **observed order p = 3.6364**.
**GCI and Richardson extrapolate are `null`: the comparator refuses to quote a GCI on a
`NOT A RESULT` row**, which is the frozen discipline (rule 5) and not an omission.

**§6 registered a warning about a suspiciously *good* order in [1.90, 2.10] and said it
would be a coincidence to interrogate, not a confirmation. p = 3.64 is not in that
window — it is far ABOVE it, and that is worse, not better.** A formally second-order
scheme cannot deliver p = 3.64 on a smooth problem. The mechanism is visible in the
numbers: **d21 = 0.161 Pa is 7.8 ppm of the answer**, so the triple is differencing
values that agree to five significant figures. **An observed order extracted from
differences this small is not a measurement of convergence rate, and this lane does not
present it as one.** §6 expected p ≈ 1; it got 3.64; **the honest reading is that the
axial error had already collapsed below the level where an order can be extracted**,
which is §6's `STAGNANT`-adjacent reading rather than a genuine high-order result.

## 6. CONTROLS AND COMPLETION — every one fired

**Planted-zero controls (rule 3), all three, both arms, against the real artifacts:**

| control | plant | expected move | seen | agreement |
|---|---|---|---|---|
| **1. Δp AND the ρ conversion** | 1.234 kinematic | **1.5116500000000002 Pa** | 1.5116500000003725 Pa | 3.7e−13 |
| **2. y⁺ reader** | 7.77 | 7.77 | 7.770000000000003 | 3e−15 |
| **3. f_dev slab reader** | 2.345 | 9.38e−06 | 9.379999999996336e−06 | 3.7e−15 |

**Control 1 is simultaneously a live test that ρ = 1.225 is applied** — a ρ-blind
reader would have seen 1.234 and been refused. It was not refused; the conversion is live.

**Strict completion (rule 4), all six clauses, all three levels: C1 rc=0 · C2 End ·
C3 last time == endTime · C4 fields `U p k epsilon nut` · C5 ExecutionTime count ==
endTime · C6 age guard (strictest form) — ALL OK.** The §4.4 ladder-spread clause
(≤ 5.0 %) did **not** fire at 1.7356 %. The plateau leg passed at every level
(L3 peak-to-peak **5.39e−06 Pa** against a 1.0e−2 Pa tolerance).

**A prediction that missed, recorded because it was load-bearing.** §4.3/§6 predicted
level-to-level Δp differences of **6–45 Pa** and used that to argue the plateau
tolerance sat 600–4500× below the signal. **The actual differences were 0.16 and
2.01 Pa** — 3× to 280× smaller than predicted. The separation argument still holds by a
wide margin (measured L3 plateau ptp is 30 000× below d21), but **the reasoning that
justified the threshold was wrong about the signal size**, and the triple paid for it
in an unextractable order (§5).

## 7. THE LAUNCHER DEFECT — found before any graded compute, and what it cost

The first launch, **02:15:36Z**, aborted at the pre-flight smoke test. `mesh_case()`'s
zone-non-empty guard searched `topoSet`'s log for `Selected N cell`, **a string
OpenFOAM v2606 never prints**; measured, `grep -c` returns **0** while the real lines
(`cellZoneSet slabA now size 26`, `slabB now size 24`) are present and correct. **The
launcher as frozen was unrunnable.** Repaired, disclosed and committed **before any
level ran** — see `PREREGISTRATION.md` **ADDENDUM 1** and the launcher's own foot
amendment; launcher blob **`5ed5ff81…` → `dd5dc0f0…`**, comparator **untouched**.

**Cost of the defect: zero.** No level directory was created, no budget consumed, and
the evidence is preserved at `SMOKE_ABORT_0215Z/`.

**The smoke test earned its keep on its first use**, and the reason generalises: the
comparator's `--selftest` passed **60 checks, 0 failures** and **could not have seen
this** — the defect was in the **launcher**, on a code path no selftest of the *grader*
reaches. The repair was also a **strengthening**: the frozen guard read its counts
**positionally** (`head -1`, `sed -n 2p`) in a case whose own §5 states *"located by
header name, never by position"*. **The lesson had been applied to the comparator and
not to the launcher — L-221/L-222's exact shape.**

## 8. COST — actual against pre-registered (rule 12, Sanaa's 2026-08-23 directive)

| | predicted (§9.1) | **actual** | ratio |
|---|---|---|---|
| solver wall | 488 s | **810 s** | **1.660** |
| total incl. meshing + FOs | 577 s = **9.6 core-min** | **810 s = 13.5 core-min** | **1.406** |
| cap | **24 core-min** | 13.5 | **56 % of cap — NOT exceeded** |
| $ (DERIVED, not measured) | $0.008208 | **$0.011543** | |

**Attribution: MISPREDICTION, essentially none of it contention.** wall/ExecutionTime
was **0.9985–1.0055** at every level (`CONTENTION.txt`) — the run was uncontended
despite concurrent VMFL045-R2 and two heat-transfer jobs. **Waste: none** — no level
was re-run, nothing was discarded, and the aborted smoke test consumed no budget.

**THE FIGURE THIS CASE WAS RUN TO CALIBRATE — §9.3 said the k-ε multiplier of 1.6 was
"the single largest uncertainty in this budget", and it was.** Measured aggregate
**5.806e−06 s/(cell·iter)** against VMFL005's laminar 2.18e−06 ⇒ an implied multiplier
of **2.66, not 1.6 — under-predicted by 1.66×.**

**But that number must NOT be reused as a clean k-ε multiplier, and here is why.** The
per-level rates are **not stable**: 1.427e−05 (1250 cells) · 6.950e−06 (2500) ·
5.717e−06 (5000) · 5.583e−06 (1500) · 3.500e−06 (2000) · 4.083e−06 (3000) — a **4.1×
scatter** with no monotone trend in cell count. Per-iteration cost (7.0–28.6 ms) is
dominated by fixed overhead at these mesh sizes, not by cells. **The 2.66 is therefore
confounded between the k-ε physics and a small-mesh overhead floor, and this lane
reports it as confounded rather than banking it for the other 29 turbulent cases.**
The defensible reusable statement is the **asymptotic** L3 rate, **5.72e−06
s/(cell·iter) at 5000 cells**, and the warning that **below ~5000 cells a
per-cell-iteration rate is not a cost predictor here.**

## 9. WHAT THIS ROW DOES **NOT** CLAIM

- **Nothing about Ansys.** Fluent 21480 Pa and CFX 21740 Pa are context, never the
  gate; this box has no Fluent and no CFX and neither archive was opened.
- **No credential.** `NOT A RESULT` is not a credential and is never softened to
  `PENDING`. The register's credential count does not move.
- **No claim of radial grid independence.** The GCI bounds the axial channel only, and
  §3 above shows the radial/wall channel is ~2200× larger.
- **No attribution of the −4.3 %.** The wall treatment is the named suspect (§7a,
  §3 above) and f_dev localises it to developed-region wall friction, but **no
  mechanism is claimed** and no second model was run.
- **Nothing about the manual's correctness.** The six §1a findings stand as drafted.

## 10. ARTIFACTS

| what | path |
|---|---|
| grading JSON (the verdict of record) | `verification/runs/ansys_verification/VMFL003/GRADING_VMFL003.json` |
| the three Roache levels | `verification/runs/ansys_verification/VMFL003/{L1_250x5,L2_500x5,L3_1000x5}/` |
| the wall-treatment ladder | `verification/runs/ansys_verification/VMFL003/{D_500x3,D_500x4,D_500x6}/` |
| cost | `verification/runs/ansys_verification/VMFL003/COST.txt` |
| contention (live sampler + wall/exec ratios) | `verification/runs/ansys_verification/VMFL003/CONTENTION.txt` |
| loadavg series, 82 rows @ 10 s | `verification/runs/ansys_verification/VMFL003/loadavg_series.txt` |
| launcher transcript | `verification/runs/ansys_verification/VMFL003/LAUNCHER.log` |
| the aborted first smoke test (the defect) | `verification/runs/ansys_verification/VMFL003/SMOKE_ABORT_0215Z/` |
| pre-registration (frozen `9195d25e`, + ADDENDUM 1) | `cases/ansys_verification/VMFL003/PREREGISTRATION.md` |
| comparator (frozen, unmodified) | `cases/ansys_verification/VMFL003/grade_vmfl003.py` blob `15b14d40…` |
