# RESULTS - Schmelzer, Dwight & Cinnella (2020), SpaRTA

Preregistration: `PREREGISTRATION.md`, written 2026-08-20 before any fit.
**Amended 2026-08-20 in a dated "Departures" section at the end of this file, not
by editing the preregistration.**

## VERDICT: **PASS** at the ceiling gate and **PASS** on the discovered-model gate — reported from an EXISTING lab reproduction, not from a new run

**The headline finding of this task is not a number. It is that this
reproduction had already been done.** Before running anything I searched the
repository and found a complete, pre-registered SpaRTA reproduction dated
**2026-08-01**, three weeks before this preregistration was written:

| Artefact | Path |
|---|---|
| solver, `kOmegaSSTFrozen` + `kOmegaSSTCorrected` | `sdk/openfoam/sparta/` (`kCorrectiveFrozenFoam`, `spartaTurbulenceModels`) |
| ceiling reproduction (their Table 1) | `verification/campaign/W2_SPARTA_FROZEN_CBFS.md` / `.json` |
| discovery + a-posteriori (their Table 2) | `verification/campaign/W2_SPARTA_REGRESSION.md` / `.json` |
| its own preregistrations | `W2_SPARTA_PREREGISTRATION.md`, `W2_SPARTA_REGRESSION_PREREGISTRATION.md` |
| run artefacts, 20 case directories | `verification/runs/W2_sparta_runs/` |
| a *later* record noting the same collision | `verification/campaign/W5_SPARTA_GATE_STATUS.md` (2026-08-04) |

`W5_SPARTA_GATE_STATUS.md` records that **two approved docket items had already
been filed asking for work that was already complete**, and states the cause:
"nothing links a gate to the record that satisfies it". This task is the **third**
occurrence of the same collision. See `docs/LESSONS.md`, L-177.

I therefore did **not** re-run the campaign. What I did instead: read the record,
verify the artefacts are on disk, and **independently re-derive one of its central
quantities from the written fields** (section 3). Cost: **0.04 core-hours**,
against the 20 core-hours authorised.

## 1. Ceiling gate - their Table 1, `eps(U)/eps(U_0)`

Both cases are the *same* cases as ours (`PHLL10595`, `CBFS13700`), so these are
directly quotable numbers, not analogues.

| Case | Paper (Table 1, preprint p. 5) | Lab, primary convention | Lab, volume-weighted | Grade recorded |
|---|---|---|---|---|
| **PH10595** | **0.00165** | **0.003331** | 0.001253 | **HIT** of the pre-registered one-sided band (< 0.005) |
| **CBFS13700** | **0.22703** | **0.39753** | 0.27634 | **PASS** the binding factor-2 gate [0.1135, 0.4541]; **NEAR MISS** of the tighter +/-25% band |

**Ceiling gate: PASS.** My own preregistration set Gate A at "below 0.05 of
baseline on PH10595"; the recorded 0.003331 clears it by a factor of 15, so
Stage B was never blocked.

The `eps(tau)` rows land far *below* the published values (CBFS 0.02617 against
0.4949; PH 0.000337 against 0.1495) and the campaign ships that as a **convention
finding**, not as an improvement: a controlled diagnostic there shows the
published CBFS stress value is recovered only if `b^Delta_ij` is *excluded* from
the reconstructed stress, i.e. the paper's `tau` norm is not identifiable from
its text. That is a finding about the paper, and it stands.

## 2. Discovery and a-posteriori - their Table 2, `eps(U)/eps(U_0)`

| Row | Paper | Lab | Lab, volume-weighted | Grade recorded |
|---|---|---|---|---|
| **discovered model on CBFS13700** | 0.32062 (their M3) | **0.36051** | 0.33799 | **HIT** (tightened +/-25%); factor-2 PASS |
| **discovered model on PH10595** | 0.19737 (their M3) | **0.14292** | 0.08383 | **NEAR MISS — better than published**; factor-2 PASS |
| M1 as published, on PH | 0.17166 | 0.16578 | -- | -3.4% |
| M1 as published, on CBFS | 0.30861 | 0.33316 | -- | +8.0% |
| M3 as published, on PH | 0.19737 | 0.20301 | -- | +2.9% |
| M3 as published, on CBFS | 0.32062 | 0.47077 | -- | +46.8% |
| M2 as published, on PH | 0.32683 | 0.40912 | -- | not settled (cap-stop, oscillating) |
| M2 as published, on CBFS | 0.48244 | 0.73824 | -- | the paper itself reports both corrections detrimental on CBFS |

**Model discovery** (their eqs. 22-24): the recovered functional form for `R` is
`T1` on both cases — **G1 HIT**. The PH coefficient is **1.39917** against the
published **1.39**, a **0.66%** match. The CBFS coefficient is **0.544787**
against the published **0.93**, graded NEAR MISS, with a hard falsifying rider
recorded in the campaign JSON: *"0.93 unreachable at any `lambda_r >= 0` from
these fields (OLS bound 0.594)"*. That is the strongest result in the whole
record — it is not a tuning shortfall, it is a statement that the published CBFS
coefficient cannot be produced from the paper's own procedure applied to these
fields.

For `b^Delta`, the sparsest recovered form is `T2` on PH (**G4 HIT**) and `T2`
then `T2 + T3` on CBFS (**G4 MISS as worded**: `T3` enters only at the two-term
form).

## 3. Independent verification performed in THIS task

The campaign's own implementation check (IC1) reports solver-versus-Python
agreement of `5.96e-15` on `kDeficit` and `2.47e-15` on `bijDelta`. That is the
campaign checking itself. I re-derived the defining identity of the frozen
extraction from the **written fields alone**, using this directory's own reader:

```
b_data_ij  ==  -(nu_t/k) S_ij  +  b^Delta_ij            (their eq. 3)

                                  relative L2     median cellwise   max cellwise
PH10595    15,600 cells            8.771e-14        9.769e-15         1.538e-12
CBFS13700  21,000 cells            1.708e-13        1.481e-14         1.396e-12
```

**Both training cases verify to machine precision**, from
`verification/runs/W2_sparta_runs/{ph_frozen/1492, cbfs_frozen/354}`.

using OpenFOAM's own written `grad(U)` from the same directory. With this
directory's finite-difference gradient instead (`of_read.structured_gradient`)
the same identity closes to `3.7e-3` relative L2 — which is the gradient
reconstruction error, not a defect in the extraction, and is consistent with the
0.47-0.96% figure quoted in `BASELINES.md` sec. 1.

Field magnitudes for the record:

| Case | RMS `\|\|b^Delta\|\|_F` | RMS `\|\|b_data\|\|_F` | ratio | RMS `R` | mean `R` |
|---|---|---|---|---|---|
| PH10595 | 0.27919 | 0.29699 | **0.94** | 0.05883 | 0.02230 |
| CBFS13700 | 0.32781 | 0.35332 | **0.93** | 0.00658 | 0.00153 |

**The correction is 93-94% of the size of the anisotropy it corrects.** It is not
a perturbation of k-omega SST, and no argument that treats the discovered model
as a small algebraic tweak survives those two ratios.

Run artefacts confirmed present: `ph_frozen/1492/{U,k,nut,omega,bijData,bijDelta,kDeficit,grad(U),tauij,phi}`,
`cbfs_frozen/354/`, with `log.frozen` reporting `ExecutionTime = 11.97 s` on PH,
matching the campaign's recorded 12.0 s.

## 4. Compute

| Item | Core-time |
|---|---|
| existing frozen campaign (both cases, plus sign experiments and propagations) | **27.7 core-min** measured, 60 approved |
| existing regression/discovery campaign | **137 core-min** of 180 approved |
| **this task: search, read, artefact check, independent identity re-derivation** | **~2.4 core-min (0.04 core-hours)** |
| authorised for this task | 20 core-hours |

**Duplicating the campaign would have consumed roughly 2.7 core-hours of compute
and several hours of agent time to produce a second, less-validated answer.**

## 5. What is still NOT done, and is genuinely open

The campaign is explicit that the **cross-validation rung has not been run**, and
holds it behind two declared prerequisites (`W2_SPARTA_REGRESSION.md` sec. 10):

1. a pre-registered **form-pruning rule** — the discovery produced 77 distinct
   forms for `R` on CBFS and 206 on PH from a 48-candidate library, and choosing
   among them without a pre-registered rule is where overfitting would enter;
2. **CD12600 data sourcing** — the converging-diverging channel is the paper's
   third case and is not on this machine.

Neither is a compute problem. Item 1 is a half-day of writing; item 2 is a data
retrieval. **That is where the next SpaRTA effort should go**, not into
re-running the ceiling.

Also open, and named here so it is not rediscovered a fourth time: the
`eps(tau)` convention finding (sec. 1) is unresolved and is a question for the
paper's authors, not for another solve.

## 6. What this result cannot see

* **It is not my run.** Every number in sections 1 and 2 is read from
  `W2_SPARTA_FROZEN_CBFS.json` and `W2_SPARTA_REGRESSION.json`, which carry their
  own preregistrations and gates. What I verified myself is section 3 only: the
  frozen extraction satisfies its defining identity to machine precision, and the
  artefacts and timings on disk match the record. I did not re-derive the
  propagation ratios.
* **No test case was opened.** PH10595 and CBFS13700 are both benchmark
  *training* cases. Nothing here measures generalisation; the cross-validation
  rung that would is the open item in sec. 5.
* **The `eps(tau)` rows are not gradeable** until the norm convention is settled.
* **The CBFS coefficient discrepancy is unexplained.** "0.93 unreachable at any
  `lambda_r >= 0`" says the published number does not follow from the published
  method on these fields; it does not say which of the two is wrong.

---

## DEPARTURES from `PREREGISTRATION.md` — dated amendment, 2026-08-20

The preregistration is frozen and was not edited. These are the departures.

* **D-1. Stages A, B and C were not executed as new runs.** The preregistration
  assumed no prior art. A repository search performed before any solve found a
  complete, pre-registered reproduction of exactly Stages A-C dated 2026-08-01
  (paths in the header above). Re-running it would have duplicated ~2.7
  core-hours of validated work to produce a second, weaker answer. **Reason for
  the departure: the work already existed.** The pre-registered acceptance bands
  are reported against the existing result unchanged, and the ceiling gate
  (Gate A, "< 0.05 of baseline on PH10595") is cleared by the recorded 0.003331.
* **D-2. I built and then deleted a duplicate solver.** Before finding the prior
  art I wrote and successfully compiled an OpenFOAM application `spartaFreeze`
  implementing the same frozen-omega extraction. On discovering
  `sdk/openfoam/sparta/kCorrectiveFrozenFoam` — which is validated to `6e-15`
  against an independent Python implementation and has 20 run directories behind
  it — I **deleted my duplicate**, source and binary, rather than leave a second,
  unvalidated frozen-RANS solver in the tree for someone to pick up by mistake.
  Recorded here because a deleted artefact that is not recorded is a hidden
  action.
* **D-3. The independent check in sec. 3 was not pre-registered.** It was added
  because reporting someone else's numbers without any independent handle on them
  would not be a result. It is a check of the artefact, not of the campaign's
  conclusions, and it is labelled as such.
* **D-4. The staged Gate A/B/C structure is superseded** by the existing
  campaign's own gate structure (G1-G5, factor-2 and +/-25% bands), which is
  stricter and was pre-registered earlier. Where the two disagree in wording, the
  earlier preregistration governs, because it was written first.
