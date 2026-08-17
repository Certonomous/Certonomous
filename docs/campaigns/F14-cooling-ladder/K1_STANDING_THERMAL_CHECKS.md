# K1a and K1c — the thermal checks made standing, and verified by execution

F14 cooling ladder. Executed 2026-08-17 against HEAD `3af826ed`.

**K1a** takes the four thermal checks that K0a, K0b and K0c each rebuilt for
themselves and puts them where the next solve inherits them. **K1c** does not
read them; it runs them against planted defects and reports what fired.

Nothing here is a solver campaign. Every case below is K0c's committed
`C3_Ra1e5_m64_source` rebuilt from its own dictionaries with one thing changed,
and the committed case is untouched. Total compute is recorded in *Cost*.

---

## Verdict

| | |
| --- | --- |
| Standing documents extended | `docs/physics_rules.yaml` (new `thermal` block), `docs/standards/MONITOR_STANDARD.md` (v1.9, signatures S13–S15) |
| Checkers wired to them | `scripts/heat_balance.py`, `scripts/check_convergence.py` |
| Controls run | 5 planted, 1 identity probe, 13 paired audits |
| Controls proving **recognition** | 3 (KC2, KC3a/KC3b as a pair, S15's own misfire) |
| Controls proving **reachability** only | 1 (KC1) |
| Proposal P1 | **CLOSED — REJECTED as proposed**, replaced by an explicit diagnostic |
| Verdicts moved by any change | **0 of 13**, proved by paired execution |

---

## 1. What each standing document gained

### `docs/physics_rules.yaml`, new block `thermal`

Extended in that file's established form: a comment carrying the reasoning and
the measurement it rests on, then the keys. Four areas, eleven keys.

| key | value | what it encodes |
| --- | ---: | --- |
| `monitor_peak_to_peak_max_pct` | 0.02 | the criterion K0c's gate actually ran on |
| `monitor_window_iterations` | 400 | fixed window, not a fraction of the run |
| `monitor_sample_interval_iterations` | 50 | the in-pass function-object interval |
| `monitor_min_samples` | 9 | below this the check REFUSES rather than scores |
| `boussinesq_beta_dT_max` | 0.1 | the small-temperature-difference limit, warned when violated |
| `boussinesq_dT_max_K_at_TRef_300` | 30.0 | what that limit is in kelvin, which is the number a rung controls |
| `turbulent_prandtl_default` | 0.85 | used only when the case is silent, and the report says which |
| `heat_balance_tol_pct` | 0.5 | closure pass band |
| `heat_balance_closure_is_evidence_on_sealed_case` | **false** | K0b's finding, carried on the threshold's face |
| `heat_balance_source_recovery_tol_pct` | 0.1 | the band on the part that *is* a measurement |
| `heat_balance_undefined_ratio_fails` | true | the P1 disposition |

**The temperature-residual criterion, and why the obvious one is refused.** The
block states the criterion as a peak-to-peak spread over a fixed window and
refuses three alternatives in writing:

- **Not the residuals.** K0c's four fine meshes all met their own
  `residualControl` and missed the graded criterion by two to three orders of
  magnitude — 2.19, 3.98 and 4.67 percent of drift in Nu_avg against 0.02
  percent, and 14.65 percent on the g = 0 twin. An under-relaxed SIMPLE outer
  loop moves the smooth modes at a rate falling off like 1/N², so doubling the
  mesh needs about four times the iterations while the residuals go quiet on
  schedule. Graded on residuals, K0c's Ra = 1e3 pair would have reported a
  **fine mesh further from the benchmark than its own coarse mesh**, 1.0940
  against 1.1191.
- **Not the endpoint difference.** K0c's `Ra1e6_m192` approaches steady state as
  a decaying oscillation of period about 400 iterations — the window length — so
  an endpoint test aliases against it.
- **Not a fraction of the run.** A last-quarter window loosens as a run is
  extended: the same case passes by being run longer.

**Boussinesq, and it is not academic.** Re-derived from the case dictionaries,
not taken from any brief: K0a's `constant/transportProperties` carries
`beta 3.333333e-03` and its `0.orig/T` carries 310 K against 300 K, so
**beta·dT = 3.333333e-02** — satisfied, by a factor of 3. For an ideal gas
beta = 1/TRef, so at TRef = 300 K the limit beta·dT = 0.1 is reached at
**dT = 30.0000 K exactly** (30.000003 K at the case's own rounded beta), and a
40 K rise gives 0.1333. *K0a is a capability rung and this figure is used here
only to calibrate a threshold; it is not a result and does not travel.* What it
implies for later rungs is stated in the block and repeated here: **any rung on
this ladder run at a realistic temperature rise crosses this line and must
either justify Boussinesq explicitly or move to a compressible thermo solver.**

**Turbulent Prandtl number.** Recorded per solve with its provenance, not
merely defaulted. On a laminar solve it does not enter the answer and is still
recorded, because "it did not matter here" is a fact about this case.

**Heat-balance closure, carrying K0b's finding on its face.** The threshold key
sits beside `heat_balance_closure_is_evidence_on_sealed_case: false` and a
comment stating why: on a sealed impermeable steady case the discrete equation
conserves at every iteration, converged or not; K0b predicted over 20 percent
on an unconverged snapshot and measured 0.0128 percent. A passing closure
number is not evidence the physics is right. A quantity derivable by
construction is an identity and cannot gate anything.

### `docs/standards/MONITOR_STANDARD.md`, version 1.9

Three signatures in the standard's own `### Sn` form — detection, severity,
action, status, and the replay line its section 4 rule 6 requires — preceded by
a single corpus-reach statement, because all three share one corpus and section
3.1's standing complaint is that rules get adopted on corpora nobody named.

| | fires | corpus | motivating case |
| --- | --- | --- | --- |
| **S13** converged residuals over a graded quantity still moving | 1 of 11 | committed K0c logs | K0c's fine meshes; **and this rung's own six controls** |
| **S14** a closure number quoted as evidence on a sealed case | 1 of 6 | K1c controls | K0b's C3 prediction failure |
| **S15** a plant witnessed in the dictionary and not in the log | 1 of 6 *at first attempt* | K1c controls + K0c logs | K0b's C3b |

All three are **wired**, not proposals: S13 is `classify_monitor()` in
`scripts/check_convergence.py`; S14 and S15 are `closure_is_identity_class` and
`fvoptions_witness()` in `scripts/heat_balance.py`.

---

## 2. The checkers, and what changed in them

### `scripts/check_convergence.py` — signature 5, mode `--monitor-regex`

The existing four signatures are properties of a **log**. This one is a property
of a **quantity the caller nominates**, because no log says which of its numbers
a rung is graded on. So it is a separate mode and `classify()` is untouched.

It reproduces K0c's own published convergence table **to six decimal places on
all eleven rows, from the committed logs alone** — which is the check that it is
the same criterion and not a new one wearing its name:

```
python3 scripts/check_convergence.py \
    docs/campaigns/F14-cooling-ladder/K0c_runs/Ra1e3_m32/log.buoyantBoussinesqSimpleFoam \
    docs/campaigns/F14-cooling-ladder/K0c_runs/Ra1e3_m32/log.buoyantBoussinesqSimpleFoam.stage2 \
    docs/campaigns/F14-cooling-ladder/K0c_runs/Ra1e3_m32/log.buoyantBoussinesqSimpleFoam.stage3 \
    --monitor-regex 'areaNormalIntegrate\(hotWall\) of k0cGradT = ([-\d.eE+]+)'
```

| case | gated peak-to-peak % | K0c_RESULTS.md | endpoint % (NOT GATED) | last-quarter % (NOT GATED) | exit |
| --- | ---: | ---: | ---: | ---: | :---: |
| Ra1e3_m32 | 0.000936 | 0.000936 | 0.000198 | 0.000249 | 0 |
| Ra1e3_m64 | 0.002813 | 0.002813 | 0.002813 | **2.164275** | 0 |
| Ra1e4_m40 | 0.001999 | 0.001999 | 0.001894 | 0.009805 | 0 |
| Ra1e4_m80 | 0.003590 | 0.003590 | 0.000750 | 0.796851 | 0 |
| Ra1e5_m64 | 0.002039 | 0.002039 | 0.001874 | 0.001446 | 0 |
| Ra1e5_m128 | 0.000904 | 0.000904 | 0.000309 | 0.717580 | 0 |
| Ra1e6_m128 | 0.000258 | 0.000258 | 0.000145 | 0.001980 | 0 |
| Ra1e6_m192 | 0.000219 | 0.000219 | 0.000044 | 0.013712 | 0 |
| C1_Ra1e5_m128_g0 | 0.008403 | 0.008403 | 0.008403 | 0.956998 | 0 |
| C2_Ra1e5_m128_dT110 | 0.001479 | 0.001479 | 0.001065 | 0.600015 | 0 |
| C3_Ra1e5_m64_source | 0.123720 | 0.123720 | 0.123720 | 0.514945 | **1** |

The last-quarter column is printed to be argued with, not used: on `Ra1e3_m64`
it reads **2.164275 percent** where the gated window reads 0.002813 percent,
because the last quarter of that case's concatenated two-stage history reaches
back into stage 1. That is the "fraction of the run" statistic failing on this
lab's own data, in the same table as the one that works.

`C3_Ra1e5_m64_source` fires. K0c did not grade it — it is the energy-balance
control and its Nusselt convergence was never load-bearing — but the standing
check flags it and this record says so rather than quietly excluding it.

### `scripts/heat_balance.py`

1. **Thresholds governed.** `--tol` and the Boussinesq limit now default from
   `docs/physics_rules.yaml`. Measured before changing it: **all 7 existing
   invocations across both callers** (`analyse_k0c.py` line 576, and
   `THERMAL_K0_runs/run_controls.sh` lines 36, 47, 59, 67, 78, 107, 154) pass
   `--tol` explicitly, so no committed workflow can be moved by the changed
   default. The built-in fallback is deliberately the pre-K1a 1.0 rather than a
   copy of the governed 0.5, so a missing rules file is visible rather than
   silently harmless, and the report always names which source it used.
2. **Prt recorded per solve**, with provenance, in the JSON and the printed
   report, and stating whether it enters the answer on this solve.
3. **S14 stamp.** `closure_is_identity_class`, three-valued: true, false, or
   null for UNKNOWN. On a sealed source-free case the report prints, in words,
   that the number is not evidence about the physics.
4. **S15 witness.** `fvoptions_witness()` reads the *solver's own log*, not
   `constant/fvOptions`, and reports `constructed` / `none` / `disagreement` /
   `no_log`.
5. **P1.** See section 4.

---

## 3. Controls

*Reachability* means the FAIL branch of the check is reachable at all — the band
is not decorative. *Recognition* means the check tells the defect class from a
sound case **in forms other than the exact literal planted**. A control that
only shows the harness could run earns nothing.

Every plant below is witnessed **in the solver's log**, never in the dictionary,
and each case's own convergence is gated by S13 before its number is read.

### KC0 — no source. KIND: **negative control** (recognition's other half)

The guard against a check so loose it fires on anything. `constant/fvOptions`
removed outright; the solver's log says `No finite volume options present` at
line 64, an explicit in-log negative witness rather than an absence.

| | expected | measured |
| --- | --- | --- |
| Q in / Q out | equal and opposite | +1.298877965e-03 / −1.298877965e-03 W |
| net leak | ~0 | **−5.960965236e-14 W** |
| imbalance | far below 0.5 % | **0.000000005 %** |
| exit status | 0 | **0 — PASS** |
| S14 identity stamp | fires: sealed, no source | **true** — the only case in the set |
| S13 peak-to-peak | passes | 0.000000e+00 % over 400 iterations, 80 samples |

**And S14 firing here is the point of S14.** That 0.000000005 % is not an
achievement; it is what a sealed box does. The report says so on its face.

### KC1 — the K0c literal, re-run. KIND: **REACHABILITY**

`constant/fvOptions` byte-identical to the committed case (verified with `cmp`).
Plant **+5.000000000001e-03 W**, derived as rho·cp·S = 1.1614 × 1007 ×
4.275222401345e-06.

| | K0c precedent | measured here |
| --- | --- | --- |
| net boundary flux | −4.999996460e-03 W | **−5.000000000120e-03 W** |
| recovery error | −7.08e-05 % | **+2.387621e-09 %** |
| imbalance | `nan` | **UNDEFINED, with a stated reason** |
| exit status | 1 | **1 — FAIL** |
| plant in the solver log | presence only | `Selecting finite volume options type scalarSemiImplicitSource` / `Source: heatPlant`, lines 66–67 |

**Precedent beaten by four orders of magnitude**, and the reason is S13: K0c's
C3 and this case's own first attempt both stopped on `residualControl`, where
the recovery error is ~8e-05 %. Run to the standing convergence criterion it
falls to 2.4e-09 %.

**Why this is only REACHABILITY.** It plants the same defect, in the same
mechanism, at the same magnitude and sign as the control it is matching. It
shows the FAIL branch is reachable. It says nothing about whether the check
would see a defect it was not already shaped around. That is what KC2 and KC3
are for.

### KC2 — the same defect with the sign reversed. KIND: **RECOGNITION**

Plant **−5.000000000000e-03 W**: a sink, not a source. This is a form no check
tuned to KC1's literal would see, because it inverts the very signature KC1
produces — every patch carries heat **in** instead of **out**.

| | predicted before the run | measured |
| --- | --- | --- |
| sign of the net | positive (into the domain) | **+5.000000000005e-03 W** |
| recovery error | within 0.1 % | **+1.050722e-10 %** |
| exit status | 1 | **1 — FAIL** |
| plant in the solver log | constructed | lines 66–67, `Source: heatPlant` |

**And KC2 is the empirical refutation of P1, at no extra cost.** With every
patch inward, `Q_out` is exactly zero and the *existing* denominator prints
**exactly 100.000000000 %** — not approximately, exactly, because
|Q_net| / Q_in = 1 identically when no patch is outward. P1 proposed making the
mirror case behave the same way. Section 4.

### KC3a / KC3b — magnitude, as a pair straddling the threshold. KIND: **RECOGNITION**

Two plants three orders of magnitude below KC1, in ratio exactly 2, chosen so
one falls either side of the 0.5 % tolerance. This is the control that shows the
check **measures** rather than merely detects, and it locates the threshold.

| | KC3a | KC3b |
| --- | ---: | ---: |
| planted | +1.000000000000e-05 W | +5.000000000000e-06 W |
| net boundary flux | −9.999999937997e-06 W | −4.999999885695e-06 W |
| recovery error | **−6.200268e-07 %** | **−2.286105e-06 %** |
| imbalance | **0.772869044 %** | **0.385689808 %** |
| exit status | **1 — FAIL** | **0 — PASS** |

Plant ratio 2.000000; measured imbalance ratio **2.003862**. The check is linear
in the defect it is looking at across three orders of magnitude below the form
it was built against.

**The blind spot this control exposes, stated because it is the useful half.**
KC3b carries a real, log-witnessed, correctly recovered 5 µW source and the
check **passes it**. Nothing is wrong: 5 µW is 0.386 % of the heat crossing this
boundary and the tolerance is 0.5 %. But it means plainly that **a passing
closure number does not mean there is no unaccounted source — it means there is
none larger than the tolerance times the boundary traffic.** On this case that
floor is about 6.5 µW. Any rung quoting a closure pass should quote that floor
beside it.

### KC-S15 — the control that caught itself. KIND: **RECOGNITION**, unplanned

Not designed. On the first attempt the five control cases were copied from the
committed C3 case and inherited its `.stage2` and `.stage3` logs; the fresh
solve overwrote only `log.buoyantBoussinesqSimpleFoam`. So **the no-source
negative control held one log saying `none` and two saying `constructed`.**

Before the disagreement branch existed, `fvoptions_witness` would have taken the
positive reading and the negative control would have reported as planted —
silently worthless, in exactly the way this lab's first false zero was
worthless. With the branch, the audit reported:

```
fvOptions in the SOLVER LOG: disagreement
IDENTITY CLASS UNKNOWN:
    the solver logs in this case DISAGREE about whether finite volume
    options were constructed ({'log.buoyantBoussinesqSimpleFoam': 'none',
    'log.buoyantBoussinesqSimpleFoam.stage2': 'constructed',
    'log.buoyantBoussinesqSimpleFoam.stage3': 'constructed'}).
```

The cases were rebuilt with foreign logs removed and re-run. After the rebuild
S15 fires **0 of 6** on the controls and **0 of 11** on the committed K0c cases,
whose staged logs agree by construction. This is recognition and not
reachability because the defect was not planted: it was made by accident, in a
form nobody had written down, and the check found it.

### KC4 — the identity probe. KIND: **RECOGNITION of the distinction K1a rests on**

The claim K1a puts in `physics_rules.yaml` is that the sealed-case closure is an
identity while the planted-source recovery is a measurement. That is testable,
and it is tested here rather than asserted: the same plant audited at eight
iteration counts against the T equation's own initial residual at each.

| iteration | T initial residual | recovery error | imbalance |
| ---: | ---: | ---: | :---: |
| 100 | 4.511e-03 | **−24.139 %** | UNDEFINED |
| 200 | 5.546e-04 | −4.2034 % | UNDEFINED |
| 300 | 8.456e-05 | −0.66860 % | UNDEFINED |
| 400 | 1.321e-05 | −0.10497 % | UNDEFINED |
| 500 | 2.101e-06 | −1.6706e-02 % | UNDEFINED |
| 1000 | 2.218e-10 | −1.7593e-06 % | UNDEFINED |
| 2000 | 2.574e-12 | +3.6348e-09 % | UNDEFINED |
| 4000 | 3.486e-12 | **+2.3876e-09 %** | UNDEFINED |

The error tracks the residual across **seven decades**. Set that beside K0b's
sealed no-source case — 0.0128 % at iteration 10 and never above 0.13 % at any
iteration — and the two quantities are visibly different kinds of thing. One
measures the solution; the other measures the discretisation. **That contrast
is the whole warrant for `heat_balance_closure_is_evidence_on_sealed_case:
false`, and it is now a measurement rather than an argument.**

---

## 4. Proposal P1 — CLOSED, and rejected as proposed

**P1 as filed by K0c:** *"Give `heat_balance.py` a defined imbalance when all
patches are outward. Normalising by `max(sum(Q>0), |sum(Q<0)|)` would give C3 a
real percentage instead of `nan` without changing any existing answer, since
the two are equal whenever both signs are present."*

**Disposition: the diagnostic is adopted; the normalisation is REJECTED.**

**Why the normalisation is refused.** With no inward patch, `sum(Q<0)` **is**
the net, so the proposed ratio is |net| / |net| = 1 **exactly** — 100.0000 %
for every such case, whatever the source size, forever. It is not a real
percentage. It is a second identity, and P1 would have replaced an honest
refusal with a number that reads like a measurement — the precise failure W-2
exists to prevent, arrived at while trying to remove a `nan`.

**This is measured, not predicted.** The mirror case already does it: KC2 plants
a sink so that every patch carries heat **in**, `Q_out` is exactly zero, and the
existing denominator prints **100.000000000 %**. The arithmetic is symmetric and
so is the emptiness. P1 asked to make the other half behave the same way.

**A second defect the same measurement turned up, which P1 did not anticipate.**
The failure is not confined to the single point where `Q_in == 0`. At
intermediate iterations of the planted case, one adiabatic patch carried pure
floating-point residue — measured at **+7.94e-24, +1.63e-22 and +8.18e-23 W** at
iterations 300, 400 and 500 — so `Q_in > 0` was *true* and the old script
reported imbalances of **6.25e+22 %, 3.07e+21 % and 6.11e+21 %**. A denominator
of residue is not a denominator. The ratio is therefore declared undefined
whenever `Q_in <= 0` **or** `Q_in < |Q_net|`.

**What was adopted instead.** `imbalance_defined` and
`imbalance_undefined_reason` in the JSON; the printed report says `UNDEFINED`,
gives the named reason, and states the net leak in watts. `passed` is written
explicitly as `imbalance_defined and imbalance_pct <= tol` rather than relying
on `nan` losing its own comparison, so the verdict no longer depends on an
accident of IEEE 754 that a reader has to know about.

### The proof that it is not more permissive

Two arguments, one algebraic and one by execution, because the brief asks for
the failing case to still fail and the algebra alone is a claim.

**Algebraic.** A case that passed before satisfied `100·|Q_net|/Q_in ≤ tol` with
`tol` far below 100, hence `|Q_net| < Q_in`, hence the new test finds the ratio
DEFINED and the verdict is unchanged. The new branch can only turn a printed
number into a refusal; it can never turn a FAIL into a PASS.

**By execution.** HEAD's `scripts/heat_balance.py` (extracted with
`git show 3af826ed:scripts/heat_balance.py`) and the patched one were run over
**the same 13 sets of fields** — five controls and the probe at eight times —
and every pre-existing JSON key compared:

```
audits compared            : 13
exit-code (verdict) changes: NONE
pre-existing keys that move: NONE
```

The only value that moves anywhere is `imbalance_pct`, on the three audits where
the old script printed a residue-denominator number:

| audit | old `imbalance_pct` | new | Q_in | \|Q_net\| | verdict |
| --- | ---: | :---: | ---: | ---: | :---: |
| t300 | 6.254437256517308e+22 | UNDEFINED | 7.940874e-24 W | 4.966570e-03 W | FAIL → FAIL |
| t400 | 3.068127085440238e+21 | UNDEFINED | 1.627948e-22 W | 4.994751e-03 W | FAIL → FAIL |
| t500 | 6.111168117238912e+21 | UNDEFINED | 8.180375e-23 W | 4.999165e-03 W | FAIL → FAIL |

**And the failing case still fails, with its plant witnessed in the log:** KC1,
plant `+5.000000000001e-03 W`, `Selecting finite volume options type
scalarSemiImplicitSource` / `Source: heatPlant` at lines 66–67 of its solver
log, imbalance UNDEFINED, **exit status 1**.

---

## 5. Regime numbers — every thermal claim above carries these

| | KC0 / KC3a / KC3b | KC1 / KC2 / KC4 |
| --- | --- | --- |
| Rayleigh Ra_L | 1.000000e+05 | 1.799639e+05 |
| Prandtl Pr | 0.710000 | 0.710000 |
| Turbulent Prandtl Prt | 0.85, from `constant/transportProperties` | 0.85, from `constant/transportProperties` |
| L | 0.10 m | 0.10 m |
| dT used | 1.088162 K | 1.958300 K |
| **Boussinesq beta·dT** | **3.627207e-03** | **6.527666e-03** |
| Boussinesq status | satisfied; limit reached at dT = 30.0000 K | satisfied; limit reached at dT = 30.0000 K |
| Richardson Ri | not defined independently — Gr/Re² = 1 by construction with no imposed velocity scale | same |
| **Heat-balance closure** | KC0 0.000000005 % (identity class); KC3a 0.772869 %; KC3b 0.385690 % | KC1 UNDEFINED; KC2 100.000000 % (both by construction — see §4) |
| Solver | `buoyantBoussinesqSimpleFoam`, OpenFOAM v2606 | same |
| Laminar | alphat = 0 everywhere | alphat = 0 everywhere |

Ra rises on the planted 5 mW cases because the source raises the field's own
temperature range, which is the quantity `heat_balance.py` builds Ra from. It is
reported rather than normalised away.

---

## 6. Cost

Single core per solve, run in parallel. No monetary figure: there is no verified
rate for this machine.

| pass | what | core-seconds |
| --- | --- | ---: |
| 1 | five controls, first attempt — **discarded**, foreign logs (S15) | 33.738 |
| 2 | six controls rebuilt clean, stopped on `residualControl` — **superseded** by S13 | 41.178 |
| 3 | six controls run to 4000 iterations, the set reported above | 106.640 |
| | **total** | **181.556 s = 3.026 core-minutes** |

Two of the three passes were thrown away by this rung's own new checks. That is
the intended behaviour and the cost is recorded rather than netted out. Audits
and convergence checks are postProcess and file reads; their cost is seconds and
is not itemised.

---

## 7. Reproducing this

Written against HEAD `3af826ed` **and then followed literally before being
called done**, because K0c's own run-tree README told a reader to rebuild its
hardest case with the command that had to be killed and abandoned — it had been
written while the case was still running (repaired at `3af826ed`).

From a clean checkout, with OpenFOAM v2606 available:

```bash
# 1. Build a control from the committed case. Nothing under K0c_runs is edited.
W=$(mktemp -d)
cp -r docs/campaigns/F14-cooling-ladder/K0c_runs/C3_Ra1e5_m64_source "$W/KC1_src_5mW"
cd "$W/KC1_src_5mW"
rm -f log.* system/controlDict.stage1 system/fvSolution.stage1 CASE.txt COST.txt
cp -r 0.orig 0
sed -i 's/^startFrom       latestTime;/startFrom       startTime;/;
        s/^endTime         [0-9]*;/endTime         4000;/;
        s/^writeInterval   [0-9]*;/writeInterval   500;/' system/controlDict
# residualControl stops this case at ~790 iterations with the graded quantity
# still moving by 0.57 percent (signature S13). Disarm it and let the standing
# criterion decide when the run is done.
python3 - system/fvSolution <<'PY'
import re,sys
p=sys.argv[1]; t=open(p).read()
open(p,"w").write(re.sub(r"(residualControl\s*\{)[^}]*\}",
    r"\1\n        p_rgh           0;\n        U               0;\n        T               0;\n    }",
    t, flags=re.S))
PY

# 2. Solve. About 19 s on one core.
. /usr/lib/openfoam/openfoam2606/etc/bashrc
blockMesh > log.blockMesh 2>&1 && checkMesh > log.checkMesh 2>&1
buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1

# 3. Gate the convergence BEFORE reading any number off the case.
cd -    # back to the repository root
python3 scripts/check_convergence.py "$W/KC1_src_5mW/log.buoyantBoussinesqSimpleFoam" \
    --monitor-regex 'areaNormalIntegrate\(hotWall\) of k0cGradT = ([-\d.eE+]+)'
echo "convergence exit = $?"      # 0 = CONVERGED. Read THIS status, never a pipeline's.

# 4. Audit. Capture the output; never pipe it into head and read the exit code.
out=$(python3 scripts/heat_balance.py "$W/KC1_src_5mW" --length 0.10 --tol 0.5); rc=$?
printf '%s\n' "$out"; echo "audit exit = $rc"     # expect 1: the plant is detected
```

For the other controls, change only `constant/fvOptions`: the `T` source value
is the plant in watts divided by rho·cp = 1.1614 × 1007 = 1169.5298. KC2 uses
`-4.27522240134454e-06`, KC3a `8.550444802689081e-09`, KC3b
`4.275222401344541e-09`; KC0 has the file deleted outright.

**Followed literally on 2026-08-17 in a clean detached worktree at `3af826ed`,
into a fresh `mktemp -d`, after this document was written.** Every command above
was executed as printed. The recipe produced `status: CONVERGED` with
convergence exit **0**, audit exit **1**, `IMBALANCE = UNDEFINED`, and a net
boundary flux of **−5.000000000120e-03 W** — the same twelve digits as the
control table in §3. The solver reported `ExecutionTime = 18.17 s`, against the
"about 19 s" the recipe claims. The temporary case was then removed.

The one thing the recipe cannot reproduce bit-for-bit is the mesh path:
`constant/polyMesh` is gitignored by design and rebuilt by `blockMesh`, which is
why step 2 is not optional. That is stated because a recipe with a known
irreproducible step, named, is honest, and a recipe nobody has run is a guess.

---

## 8. What this rung does NOT establish

- **Nothing about turbulent thermal cases.** Every case here is laminar with
  alphat identically zero. `heat_balance.py`'s turbulent path remains
  UNVALIDATED behind `--allow-turbulent`, and Prt is recorded rather than
  exercised.
- **Nothing about through-flow.** The advective enthalpy term is still
  uncomputed and still refused with exit 2. The one regime where the closure
  balance is genuinely *not* an identity is the one regime not tested here.
- **Nothing about the Boussinesq threshold in use.** The 0.1 limit is recorded
  and warned on; no case on this ladder has yet been run near it. The warning
  branch of that check has been read, not fired.
- **S13's corpus is one solver, one case class, one mesh family, one regime.**
  No rate from it transfers to the registry at large.
- **K0a and K0b remain capability rungs.** Their figures are cited here only to
  calibrate thresholds and to state what a check is worth. They are not results.

---

## 9. Where each finding was written down, and why there

A finding that lives only in a rung record is lost to anyone not reading that
rung. Filed by kind:

| Kind | Where | What went there |
| --- | --- | --- |
| Binds future runs | `docs/physics_rules.yaml`, block `thermal` | the eleven governed thresholds, each with the measurement it rests on |
| Binds future runs | `docs/standards/MONITOR_STANDARD.md` v1.9 | signatures **S13**, **S14**, **S15**, with replay lines and one shared corpus-reach statement |
| How to work | `LESSONS.md` | **L-88** a quantity the discretisation forces cannot gate anything, and the proposed fix that would have installed a second identity; **L-89** residuals measure change per iteration, not distance to the answer, and the gap widens with the mesh; **L-90** documentation written before its run has finished is a forecast; **L-91** a control copied from another case inherits that case's evidence |
| Domain knowledge | `docs/NUMERICS_KNOWLEDGE.md` | seven tables on buoyant steady solves, each row VERIFIED or RECALLED to that file's standing citation standard |
| Specific defect, specific place | `docs/DOCKET.md` | **D350** the K0c energy-balance control fails the criterion K0c itself established; **D351** a planted defect moves the Rayleigh number the auditor reports |

Lesson IDs were claimed by comparing the **ID set** before and after, not counts,
under the regex `^## L-([0-9]+)\.` — period-anchored, because
`## L-43, second corollary.` is a real heading in that file and an unanchored
pattern reads it as a second L-43.

**And the check earned itself on this very commit.** The set was first read at
`3af826ed` — 84 IDs, highest 85, L-52 absent (a known, already-documented gap) —
and blocks were drafted as L-86 to L-89. By the time the commit was built HEAD
had moved to `c09d1b68`, where a peer had already landed **L-86 and L-87** and
docket rows **D348 and D349**. A count would have said "two more lessons"; the
ID set said *which* two, and that both of the first IDs claimed here were taken.
Re-read at the new HEAD: 86 IDs, highest 87, no duplicates. Blocks renumbered to
**L-88 to L-91** and docket rows to **D350, D351**, and every shared blob
rebuilt from `c09d1b68` rather than from the stale parent — which is the half
the compare-and-swap does not cover, because a CAS asserts the parent, never
that your content does not collide with what landed on it.

## 10. Lane

This rung is the thermal lane, F14 only. Two findings outside K1's declared
scope were filed to the docket rather than repaired here (§9). Nothing in this
rung touches repository organisation, other ladder rungs, closure-package
documents or health-check failures.

The two shared checkers this rung edits, `scripts/heat_balance.py` and
`scripts/check_convergence.py`, are edited because making the thermal checks
standing is what K1a *is* — the first exists only for thermal solves, and the
second is extended by an additive, mode-gated path that leaves `classify()` and
its four existing signatures untouched. Backward compatibility was checked by
execution, not by reading: the pre-existing residual mode still returns
`CONVERGED: solver printed 'SIMPLE solution converged in 685 iterations'` with
exit 0 on a one-log invocation, and all 7 existing invocations of
`heat_balance.py` across both of its callers pass `--tol` explicitly, so the
newly governed default cannot move a committed workflow.
