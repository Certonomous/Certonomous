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
