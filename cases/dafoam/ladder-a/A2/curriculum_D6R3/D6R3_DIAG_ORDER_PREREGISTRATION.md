# D6R3 — DIAGNOSTIC PRE-REGISTRATION: ARM `DIAG_ORDER1` (the order test)

DRAFT. Nothing here is sent, filed, uploaded or registered anywhere outside this box (rule 7).
Written and committed **before** any compute for this arm (rule 2). Frozen at the commit that
carries it; the predictions below are the whole evidentiary content of this file.

- Item: D6R3 (`cases/dafoam/ladder-a/A2/curriculum_D6R3/`)
- Run root: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/DIAG_ORDER1`
- Producer: `d6r3_diag_order.py`, md5 `5d6ce829a3d552669e708a6ebf2ea7a2`
- Launcher: `d6r3_diag_order_arm.sh`
- The frozen D6R3 producer `d6r3_opt_runScript.py` md5 `efc3e62699690edd32e4ee910aad09c8`
  is **NOT edited by this diagnostic** and the launcher refuses if it has moved.
- Task: `run_model`. Ranks: 28. `primalMinResTol` and `primalMinResTolDiff`: UNCHANGED (1e-8 / absent).
  `endTime` UNCHANGED at the published 2000. No convergence criterion is loosened anywhere.

## 1. What is already established, and is NOT re-derived here

`P00` (the published `CRM_Wing` tutorial, run as shipped in its own process, 28 ranks) and the
`cl04` scenario of arm `P0` agree **bit-for-bit at every printed step**, including step 1
(`p initRes 0.9999999999942178 finalRes 0.09743304254827717 nIters 24`) and the final
`CD 0.02090109066417552`, `CL 0.5000136952243076`, `nuTilda` plateau `1.194718885139746e-07`.
Toolchain, mesh build and physics are exonerated. `cl05`, the SECOND scenario in the same process,
plateaus at `1.76e-06` and raises `Primal solution failed!`.

## 2. What this lane measured read-only before proposing any run (no compute)

All from `P0_20260913T190426Z.log` and the on-disk arm `P0`:

- The divergence is **not** at step 100. It is at **step 1, inside the pressure linear solve**.
  `U0`, `U1`, `U2` and `he` initRes AND finalRes are identical to all 16 printed digits between
  `cl04` and `cl05`; `p` initRes is identical (`0.9999999999942178`) and `p` **finalRes/nIters are
  not**: `0.09743304254827717 / 24` for `cl04`, `0.09727830036032596 / 21` for `cl05`.
- The three condition directories are byte-identical on disk: decomposed mesh **and** decomposed
  initial fields, 392 files per condition, aggregate md5 `f2a8925f112e27569f53355e5265d5d6` for both
  `mp04` and `mp05` (`mp06` differs in `0/U.gz` only, because it never ran and so never had its
  patch-velocity U written back). The hash reader was shown able to distinguish (planted byte).
- `decomposeParDict` is `scotch`, 28 subdomains, and the decomposition is identical per processor.
- DAFoam's own resolved `DAFoam option dictionary:` dump is **byte-identical** for all three
  instances (log lines 1000–1289 vs 2255–2544 vs 3510–3799, `diff` empty).
- The `Checking mesh quality for time = 0` block printed immediately before each primal is
  byte-identical between `cl04` and `cl05` (bounding box, cell openness, max aspect ratio, total
  volume `1318339.423133024`, non-orthogonality `70.44640458676524`, skewness `3.323214959708735`).
- The `forces` observer is active in **both** instances (4000 writes = 2 instances x 2000 steps) and
  fires after the residual print, so it cannot be the step-1 cause.

## 3. The question this arm answers, and only this

**Is the divergence ORDINAL (the second primal in a process differs) or POINT-SPECIFIC (something
about `cl05`/`mp05`)?**

The producer differs from the frozen one by exactly the diff recorded in section 6: the point list
is reordered so **`cl05` runs first**, plus a rank-0 print of the daOptions/meshOptions signature
with a planted control. No option, field, threshold, mesh or equation changes.

## 4. PREDICTIONS — frozen before the run

- **H-ORDINAL** (this lane's leading hypothesis): with `cl05` first, `cl05` reproduces the control
  signature exactly — step 1 `p finalRes 0.09743304254827717 nIters 24`, `CD 0.04113505209953232`,
  `CL 0.008857601366306839`; and converges to `CD 0.02090109066417552`, `CL 0.5000136952243076`,
  `nuTilda` max res `1.194718885139746e-07`. `cl04`, now second, shows step 1
  `p finalRes 0.09727830036032596 nIters 21` and fails with `Primal solution failed!`.
  Reading: the defect is carried by **process-global state left by the first primal**, not by any
  per-point input. Every point-specific explanation is then excluded.
- **H-POINT**: `cl05` first still shows `nIters 21` and still fails. Reading: something about
  `mp05` itself — which would **falsify** the byte-identity measurements in section 2, and this
  lane must say so loudly and re-open them.
- **H-NOISE**: `cl05` first yields a THIRD signature matching neither. Reading: the solve is not
  bit-reproducible on this box, which would **falsify** the established `P00` = `cl04` bit-identity
  as evidence of determinism. Reported loudly, and the arm is `NOT A RESULT`.
- **H-MUTATION** (the supervisor's handed hypothesis, tested independently by the probe): the
  `D6R3_DIAG_OPTSIG_BEFORE/AFTER` md5 of `daOptions` or of the shallow `meshOptions` copy CHANGES
  across builders. Predicted **dead**, because the resolved DAOption dumps already match byte for
  byte; the probe prints a PLANTED variant alongside so a match is only believed once the reader has
  been shown able to report a difference (`plant_visible` must print `true`).

## 5. Gate, label and cost

This arm produces **no physics verdict**. It is a diagnostic; its only output is the assignment
above. It can therefore be `GATE REACHED` (the order question is answered by one of H-ORDINAL /
H-POINT), or `NOT A RESULT` (H-NOISE, or the run does not complete).

- Cost, pre-registered: 28 ranks. Expected wall 640 s if the run aborts after the second primal
  (setup ~120 s + 2 x ~260 s), 900 s if all three run. **Predicted 299 core-min** (640 s x 28 / 60),
  upper bound 420 core-min. Derived dollars at the owner-stated c7a.4xlarge rate $0.0513/core-h:
  **$0.26 predicted** — derived, not measured; the box cannot read its own billing.
- Directive #17: no run is stopped by a time or budget cap. A crossing is REPORTED, and the arm is
  graded `NOT A RESULT` if it crosses.
- Cores: `min(free, 96 - 48 - 20) = 28`, with per-core idle measured at launch (>=85% idle over a
  5 s window) and the reserved 48-core propeller lane and 20-core DrivAer lane not overlapped.
  The launcher REFUSES to start if fewer than 28 cores measure that idle.
- Estimate-vs-actual calibration is owed to `docs/COST_CALIBRATION.md` at completion (rule 12).

## 6. The diff, in full — frozen producer -> diagnostic producer

```
3a4,5   import json as _dj / import hashlib as _dh
131c133 POINTS = ["cl04","cl05","cl06"]  ->  POINTS = ["cl05","cl04","cl06"]
183     + the rank-0 D6R3_DIAG_OPTSIG_BEFORE/AFTER probe with its planted control
```

Nothing else. No threshold, no tolerance, no `endTime`, no mesh, no boundary condition.

---

## ADDENDUM 1 — 2026-09-13 — RESULT. `GATE REACHED`: H-ORDINAL, with H-POINT, H-NOISE and
## H-MUTATION all dead. No gate, threshold, cap or label above is altered by this addendum.

Arm `DIAG_ORDER1`: `rc=1`, wall 546 s, 28 ranks, **254.800 core-min**
[`ledger.txt`, `D6R3_DIAG_ROW arm=DIAG_ORDER1 rc=1 wall_s=546 ranks=28 core_min=254.800`],
log `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/DIAG_ORDER1_20260913T195136Z.log`.

**The result, stronger than the prediction asked for.** The 189 printed residual / `CD` / `CL` /
`yPlus` lines of all 21 printed steps were extracted per instance from both arms and diffed:

- **position 1**: `P0`'s `cl04` and `DIAG_ORDER1`'s `cl05` — **BIT-IDENTICAL, all 189 lines.**
- **position 2**: `P0`'s `cl05` and `DIAG_ORDER1`'s `cl04` — **BIT-IDENTICAL, all 189 lines.**
- planted control: a one-character edit to one extracted file is reported by the same `diff`
  reader, so the silence above is a reader that was shown able to speak.

The entire 2000-step trajectory is a function of the **position in the process** and of nothing
else. The point, its `CL_TARGETS` entry, its run directory and its files do not enter.

**What actually fails, corrected.** The failing field is **`p`, not `nuTilda`**. At `Time = 2000`:
position 1 max residual `nuTilda 1.194718885139746e-07` = 11.95x tol -> pass; position 2 max
residual `p 1.757696578179007e-06` = **175.8x** tol -> fail, the criterion being
`primalMaxRes / primalMinResTol > primalMinResTolDiff` with the published default 100
(`repos/dafoam/src/adjoint/DASolver/DASolver.C:2743-2753`). The same log line appears verbatim in
both arms: `Primal min residual 1.757696578179007e-06 did not satisfy the prescribed tolerance 1e-08`.
Position 2 also needs `p nIters: 7` at `Time = 2000` where position 1 needs `2`.
**`CD` and `CL` still agree to 5-6 figures between the two positions**
(`0.02090262569125358` vs `0.02090109066417552`; `0.5000149858695342` vs `0.5000136952243076`) —
this is a residual-FLOOR difference set by the pressure linear solve, not a different answer.

**H-MUTATION dead, with a live plant.** `daOptions` md5 `f129ca31c6f85a782192ec0a8d505a46` before
AND after every builder's `initialize()`, all three builders, one shared object id
`129049504701248`; each `meshOptions` md5 unchanged before/after; `plant_visible: true` on every
line. The shallow `dict()` copy in `mesh_options_for()` is not mutated and neither is the shared
`daOptions`.

**Cost calibration (rule 12).** Predicted 299 core-min, actual 254.800 core-min,
**ratio 0.852**. Gap attribution: the run aborted after the second primal as predicted, and the
wall per primal came in under the P0-based estimate because the box was less contended than when
`P0` ran — misprediction in the conservative direction, no waste. Derived dollars 4.24667 core-h
x $0.0513/core-h = **$0.2179, derived not measured**. Row owed to `docs/COST_CALIBRATION.md`.
