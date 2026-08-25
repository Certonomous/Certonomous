# VMFL045-R2 — Oblique Shock Over an Inclined Ramp: RESULTS (re-run of run 1)

**NOT FILED ANYWHERE. Nothing here is sent, emailed, uploaded, filed, posted,
registered or commented outside this box** (CLAUDE.md rules 7, 8). The manual is
proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**This file records the R2 run and does NOT revise the frozen pre-registration**
(`PREREGISTRATION.md`, blob `592e872b5738f33cbbbb5eac6440e7174cbed95e` after the dated
pre-compute AMENDMENT 1; grading path `grade_vmfl045_r2.py` blob
`382ff4975801c5911277fb463076d1a14dd813c6`, freeze commit `946bbf24`). Written by the
run-and-grade lane (`ansys-lane-opus48`, Opus 4.8). **It cites run 1's `NOT A RESULT`
and does not remove, re-label or soften it** — R2 is a new rung.

## 1. Verdict, as the frozen comparator printed it (unmodified)
**`PASS`.** `--verify-frozen HEAD` exit 0 before grading. Lab value **M₂ =
1.874779041082** at the finest level L3_360x304; deviation **+0.041571 %** against the
manual printed target **1.874** (Tables .45.1/.45.2, p. 154; analytic oblique-shock,
White 1994), band **±1.0 %** — inside by a factor of 24. `GRADING_VMFL045_R2.json`,
`GRADING_VMFL045_R2.stdout.txt`.

## 2. THE FINDING THAT THE `PASS` DOES NOT CONVEY — the observed order is SUSPICIOUS
**Observed order p = 3.3862**, from the Roache triple on the post-shock Mach number
(r = 2.0, Fs = 1.25): coarse 1.871975737, medium 1.874534336, fine 1.874779041;
d32 = −2.5586e−03, d21 = −2.4471e−04, **R = 0.095640**, state **`CONVERGING`**,
GCI_fine **0.0017 %**, Richardson extrapolate **1.8748049198**.

**This is the pre-declared suspicious condition, surfaced not stamped.** The
pre-registration and the supervisor expected **p ≈ 1** and declared **p ≈ 2 already
suspicious** ("a suspiciously good order is the failure mode nobody reports").
**p = 3.39 is well beyond even that.** Mechanistically it is super-convergence: the
medium→fine change (d21) is ~10× smaller than coarse→medium (d32), so the apparent
order is inflated and the triple is **very likely NOT in the asymptotic range** — which
means the GCI_fine (0.0017 %) probably **understates** the true discretisation
uncertainty rather than bounding it. The post-shock Mach is set largely by the
shock-jump relations once the shock is captured, so it can look grid-independent between
medium and fine for a reason other than clean asymptotic convergence.

**TIER: `GATE REACHED` — the `ansys-verification-supervisor`'s ruling** (recorded after
the supervisor read the grading JSON). The rule-1 verdict `PASS` and the tier
`GATE REACHED` are different vocabularies and stand side by side; the tier never
flatters the verdict. **`GATE REACHED`, not `HOLDS`, because the G column is not clean,
and the pre-registration named in advance what would make it unclean:**
- **Observed order p = 3.3862** is **measured but NOT trusted**. It is **above the
  shock-capturing scheme's formal order**, so it is not a measurement of discretisation
  order — a sign the triple is **not in the asymptotic range** or that differences are
  cancelling. §6 declared p ≈ 1 expected and p ≈ 2 already suspicious; 3.39 is well past.
- **d21 = −2.4470535e−04 is only ~3× L3's plateau ptp (7.77e−05)** — the medium→fine
  difference sits within a small factor of the residual-unsteadiness floor. This is the
  same diagnostic that condemned VMFL051 (there the ratio was ~1; here ~3 — better, and
  still not comfortable).
- **Therefore GCI_fine = 0.0017 % is NOT a discretisation-uncertainty statement** — it is
  computed from a non-credible order on a difference near the noise floor. `N-AV7` in its
  second form: **a small GCI licenses nothing.**
- **V is strong and is said so:** the exact oblique-shock reference was derived here to
  full double precision and matched to **0.0106 %**. **G is the single limb held back,
  and this row names it** — the rubric requires a `GATE REACHED` row to say which column
  is missing. The order is recorded honestly as **measured but not trusted**, with the
  reason; it was **not** re-run toward a better order and the verdict was **not** softened.

## 3. The controls (CLAUDE.md rule 3) — all three FIRED
- **PZ-1** dat reader: plant 0.001234, seen 0.001234 (base 1.87478).
- **PZ-2** field reader: plant 0.0777, seen 0.0777 (109 440 cells, field_mean 2.26744).
- **PZ-3** reference: plant 5° into β, seen Δβ 5.94251°.
A zero from a reader not shown able to see a non-zero is not evidence; each reader was
shown able to see its plant before any value was trusted.

## 4. Per-level values and strict completion (CLAUDE.md rule 4)
| level | cells | zone cells | Ma (zone) | plateau ptp | rc | End | last time | fields | age guard |
|---|---|---|---|---|---|---|---|---|---|
| L1_90x76 | 6 840 | 252 | 1.8719757370 | 3.842e−04 | 0 | 1 | 0.0069995039 | Ma T U p rho | PASS |
| L2_180x152 | 27 360 | 1 005 | 1.8745343357 | 6.140e−05 | 0 | 1 | 0.0069997326 | Ma T U p rho | PASS |
| L3_360x304 | 109 440 | 4 025 | 1.8747790411 | 7.769e−05 | 0 | 1 | 0.0069997885 | Ma T U p rho | PASS |

**Strict completion holds at all three levels**, with one honest note: the case uses
`adjustTimeStep yes`, so the last written time is ~0.0069998 s, not literally the
`endTime` 0.007 s. The frozen comparator reads the last time directory and accepted it
(exit 0); the value is the physical `endTime` reached to 5 significant figures. rc=0, an
`End` line, fields present, and every `endTime`-dir field newer than that level's own
`0/` (age guard) hold at each level. Both frozen sampling zones non-empty at every level.

## 5. The repair, confirmed by the run rather than by argument
Run 1 died on its first timestep: `Entry 'e' not found in dictionary
system/fvSolution/solvers` — the frozen `fvSolution`, cloned from the **inviscid**
VMFL051, provided a solver named `h` and no `e`, but VMFL045 is **viscous** (μ = 1e-8,
the manual's own value, p. 153), so `rhoCentralFoam` entered the implicit viscous energy
corrector and aborted. **R2's one input change was `h` → `"(h|e)"` in `fvSolution`.**
The R2 run confirms the fix: the **pre-flight smoke test passed** (rc=0, 1 s) on the
coarsest mesh, and L3's log shows `smoothSolver: Solving for e` stepping cleanly. The
`"(h|e)"` widening genuinely carries the viscous energy path. A comparator `--selftest`
(45/0) could not have caught the run-1 defect — it proves the grader, not the case; the
pre-flight smoke test is the generalisable fix.

## 6. Context only — never the gate (ANSYS_VERIFICATION_CHARTER §2)
Ansys's own reported values, for context and NEVER as the gate: **Fluent Mach 1.902**
— which **would FAIL our 1 % gate at +1.494 %** — and **CFX Mach 1.871**, which would
pass at −0.160 %. **A near-Fluent value is a `GATE FAIL` and is never narrated as
agreement with Ansys.** This box has no Fluent and no CFX; nothing here is a statement
about Ansys. Diagnostics beside the gate: exact as-modelled M₂ = 1.8749769577 (dev
−0.010556 %); T 382.1123 K (vs manual 382.0, +0.029 %); ρ 2.278042 (vs manual 2.277,
+0.046 %).

## 7. Cost (CLAUDE.md rule 12)
**26.6667 core-min measured** (serial, RANKS=1; L1 0.3667 + L2 2.6667 + L3 23.6333;
total wall 1600 s), of a **48 core-min cap** — 55.6 % used, no `CAP_EXCEEDED`. Predicted
point estimate **20.4**; **ratio actual/predicted = 1.307×**. A peer ansys-verification
job (VMFL003) ran concurrently the whole solve at box load ~3–4 on 16 cores (LIGHT);
contention on a serial job at that load is negligible, so the gap is **misprediction of
L3's cost, not contention or waste** — waste 0. **$0.02280 derived** at $0.0513/core-h
(reported-by-owner, not measured). Calibration row in `docs/COST_CALIBRATION.md`.

## 8. Verdict vocabulary (rule 1)
`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, nothing
else. The rule-1 verdict is `PASS`; the **tier is a separate vocabulary and is the
supervisor's**, ruled **`GATE REACHED`** (§2, G column named). This is the team's first
compressible `PASS` and its third credential. R2 makes no claim about Ansys or the
manual's correctness beyond what is measured, and cites run 1's `NOT A RESULT`, which stands.
