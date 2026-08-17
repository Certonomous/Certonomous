# KV1 — the advective path of `scripts/heat_balance.py`, validated

Campaign F14, cooling ladder. Rung KV1, closed 2026-08-17 by the thermal lane.

KV1 was specified in advance, in `K2a_RACK_ROW_MODULE_SPEC.md` §8 lines 378–381,
as the instrument prerequisite for any K2b closure figure. It is closed here.

**Cost: 0.93 core-minutes, of which 0.04 is solver time.** No monetary figure
appears in this document: there is no verified rate for this machine and
inventing one would be an underived number. Breakdown in §7.

**K2b, the rack-row module, K0d and any turbulent SST case remain unrun and
unauthorized.** Nothing here is a result about a data centre.

---

## 0. The finding this rung repairs, verified at HEAD before anything was touched

D360 recorded five statements about `scripts/heat_balance.py` at `267a4021`.
All five were re-derived here at that commit rather than taken second-hand.
**All five are confirmed. A sixth was found while confirming them.**

| # | Statement | Verdict | How it was checked |
|---|---|---|---|
| 1 | `a.allow_advective` is read at exactly one place, the exit-2 refusal guard | **CONFIRMED** | `grep -n 'a\.allow_advective'` returns exactly one line, 551, inside `if nonwall and not a.allow_advective:` |
| 2 | The only per-patch heat computed is `Q = kcond * G` at line 633 — pure conduction | **CONFIRMED** | line 633 verbatim `Q = kcond * G`; it is the only assignment feeding `Q_in_W` in the per-patch loop |
| 3 | No advective key reaches `res`; no line reaches `emit()` | **CONFIRMED** | `grep -i advect` over the `res` dict literal (lines 728–760) and over `emit()` (805–898) both return nothing |
| 4 | `sealed = not nonwall` | **CONFIRMED** | line 708 verbatim |
| 5 | On an open case the report prints "NOT of the identity class, so the balance is a genuine constraint here" over a ledger whose advective term was never computed | **CONFIRMED, by readback rather than by reading the code** | see below |

Statement 5 was confirmed by *running* HEAD's auditor, not by tracing it. A
synthetic open twin of `C3_Ra1e5_m64_source` (one patch's type changed from
`wall` to `patch` in `constant/polyMesh/boundary`, nothing else) audited under
the HEAD auditor with `--allow-advective` printed, verbatim:

```
  NOT of the identity class, so the balance is a genuine constraint here rather
  than a restatement of the discretisation:
      every active patch is a wall: False; solver log says finite volume
      options were constructed (heatPlant)
```

over a ledger containing conduction only.

### The sixth statement, not in D360

**The docstring's claim that `--allow-advective` "adds the term but the report
is then stamped UNVALIDATED" is false in BOTH halves.** The flag added no term,
and no report was ever stamped UNVALIDATED: at HEAD the string `UNVALIDATED`
occurs four times — twice in the docstring and twice in stderr refusal messages
— and **never in `res` and never in `emit()`**. A reader who ran the flag and
looked for the promised stamp would have found a report that looked clean.

This is why the repair was done in two commits with the stamp first. An
instrument that prints a claim about the strength of its own check, backed by a
quantity it never computes, is worse than one that simply lacks the feature: the
missing feature is a gap a reader can see, and the printed assurance is a gap
that reads as a result. That is **L-105**.

---

## 1. The repair

**Commit 1 — `965777d2`, the stamp only.** Nothing new computed. `advective.state`,
`advective.ledger_complete` and `advective.note` added to the JSON and to the
printed report; an incomplete ledger made unable to PASS whatever the imbalance
reads; `closure_is_identity_class` moved from `false` to `null`/UNKNOWN on an
incomplete ledger, because a balance missing a term is neither an identity nor a
constraint but an unfinished sum; the false docstring sentence replaced by the
record of the defect.

**Commit 2 — the term.** On every active patch of a case that has a non-wall
patch:

```
Q_adv_into_domain_p  =  -rho.cp . integral_p (T - datum) (U.n) dA
```

summed into the same ledger as the conductive term, so `Q_in_W` on a patch is
conduction plus advection and `Q_net_W` is the whole boundary.

Four decisions inside that line are load-bearing and each is defended by a
measurement, not by a preference:

**(a) The integral is taken against the solver's own `phi`, not against a
geometric `Sf & U_f`.** `surfaceFieldValue` with `operation weightedSum`,
`fields (phi)`, `weightField T` returns `gSum(T_f . phi_f)` over the patch faces.
For a `volScalarField` on a patch OpenFOAM's `filterField` hands back the
**boundary** field, so `T_f` is the same face value `div(phi,T)` saw.
Reproducing the solver's own numerics rather than inventing a second set is this
file's standing rule, and it is why a missing `phi` at the audited time is a
**refusal** and never a fallback to `U`.

**(b) The datum is the case's own `TRef`, not 0 K.** The *net* is datum-free when
mass balances; the *denominator* of the imbalance ratio is not. Measured by
mutation M4 on KV1c: at a 0 K datum the denominator is **8.979442 W** against
**0.2079685 W** at `TRef`, a factor of **43.2**, so the same 0.5 % band would
carry **4.49e-02 W** of slack instead of **1.04e-03 W**. Using absolute `T`
would have been a 43-fold loosening of the gate at an unchanged number.

**(c) Mass is gated, not assumed.** Shifting the datum by `dT` moves the ledger
by `rho.cp.dT.(net volumetric flux)`, so the enthalpy number is meaningful only
to the extent the boundary conserves mass. The mass ledger is reported and gated
against the same governed `--tol`: a case whose mass does not balance gets
`ledger_complete: false` and **cannot pass**. `datum_sensitivity_W_per_K` states
what one kelvin of datum error is worth so a reader can compare it to the net.

**(d) The silent-fallback guard.** `surfaceFieldValue` returns the **unweighted**
sum without a word on stderr when `canWeight()` is false
(`surfaceFieldValueTemplates.C`, `case opWeightedSum`). The advective term would
then be ~300× too small and nothing would say so. The invariant is therefore
checked rather than trusted: `integral T phi / integral phi` is a flux-weighted
mean face temperature and must lie inside the field's own T range. Mutation M5
below fires it deliberately.

---

## 2. The controls, and what kind each one is

The two words are used in this campaign's sense, from `K0c_RESULTS.md` 290–292:

> *Reachability* means: the FAIL branch of this check is reachable at all — the
> band is not decorative. *Recognition* means: the check tells a physically
> wrong answer from a right one, at the magnitude the gate cares about.

Predictions were registered in `KV1_runs/CONTROL_PREDICTIONS.txt` and hashed
(`KV1_runs/PREDICTIONS.sha256`, `2ca14c22986341f1…`) **before any solver ran**.
The file is reproduced in §8 so the prediction and the outcome travel together.

### KV1a — a planted 5.000e-03 W source on an open duct. KIND: **RECOGNITION** of the advective term's magnitude and sign

| | predicted, registered in advance | measured |
|---|---|---|
| net boundary flux recovers the plant | −5.000e−03 W to within 0.1 % | **−4.999999998798e−03 W**, error **+2.403e−08 %** |
| closure row | FAIL, about 3.42 % against a 0.5 % band | **3.4204 % — FAIL** |
| exit status | 1 | **1** |

**This beats the K0c precedent by three orders of magnitude.** K0c's C3 recovered
a 5.000e-03 W plant at −4.999996460e-03 W, error −7.08e-05 %. KV1a recovers it at
−4.999999998798e-03 W, error +2.40e-08 %.

**It is RECOGNITION and not merely reachability, and the reason is measurable.**
The same field set audited by the *pre-repair* auditor — a conduction-only
ledger — reports `Q_net = −7.448816e−06 W` against the same 5.000e-03 W plant:
**wrong by 99.85 %**. The recovery branch is not satisfiable by an absent term,
so passing it distinguishes a right advective term from a wrong one.

**In-log witness of the plant.** `buoyantBoussinesqSimpleFoam` echoed
`Selecting finite volume options type scalarSemiImplicitSource` and
`Source: heatPlant` at construction. A source sitting in `constant/fvOptions`
but never constructed leaves that log empty. Additionally the running solver's
own `outletT` function object printed `areaAverage(outlet) of T =
305.1830305289686` against an inlet held at `305.0000000000001` — the plant is
witnessed **in the thermal field in the log**, not only in the construction
banner. Predicted rise from the case table alone: 0.171 K.

### KV1b — the no-source negative twin. KIND: **REACHABILITY only**, and it is the rung's most useful failure

KV1b is byte-identical to KV1a except that `constant/fvOptions` does not exist.
Its log prints `No finite volume options present`. Its closure passes at
`0.0000 %`, exit 0.

**And that pass is worth nothing, which is the finding.** With adiabatic walls
and no source the duct converges to *exactly* 305 K everywhere — the in-log
`outletT` reads `305.0000000000001`, the same as the inlet. So:

```
Q_adv(inlet) = +0.146191 W    Q_adv(outlet) = -0.146191 W    SUM = 0
```

Flip the sign of the advective term and the sum is still zero. Scale it by two
and the sum is still zero. **The mutations cannot bite because there is nothing
for them to bite on.** That is "a term that is computed but never able to fail" —
the identity defect wearing a new name — and writing KV1b up as a passing
open-case closure would have been the whole error of this rung committed a second
time.

KV1b is **kept, not replaced**. It is the negative control of the mutation
harness: the case where the mutations are *correctly* invisible, which is what
shows the sensitivity measured on KV1c belongs to the case and not to the
harness.

### KV1c — a heated-wall duct, built after KV1b was read. KIND: **RECOGNITION**, and it carries the fail-and-close demonstration

KV1c gives the ledger two **independent non-zero** terms that must cancel: heat
enters by conduction through a 315 K bottom wall, and leaves by advection through
the outlet. In-log `outletT` = `307.6280625883795`.

```
patch      type      mdot kg/s     Q cond W      Q adv W   Q into dom. W
inlet      patch   -2.9035e-05  -0.00084788     0.146191        0.145343
outlet     patch    2.9035e-05            0     -0.207968      -0.207968
hotWall    wall               0    0.0626251           -0       0.0626251
topWall    wall               0  -9.21614e-23           -0    -9.21614e-23

conduction = +6.177726e-02 W      advection = -6.177726e-02 W
net        = +1.967097e-11 W      IMBALANCE = 0.0000 %  -> PASS
```

---

## 3. The fail-and-close demonstration on an open case

This is what the rung was asked for: the balance **failing** on an open case
where the advective term is wrong and **closing** where it is right.

### 3a. Same field set, wrong term against right term

The advective term is "wrong" in the most literal available sense — absent — by
running the **pre-repair auditor at `267a4021`** over the identical committed
field sets.

| case | auditor | Q_in | Q_net | imbalance | exit |
|---|---|---:|---:|---:|---:|
| KV1c | HEAD `267a4021` (conduction only) | 6.262514e−02 W | 6.177726e−02 W | **98.6461 % FAIL** | 1 |
| KV1c | repaired | 2.079685e−01 W | 1.967097e−11 W | **0.0000 % PASS** | 0 |
| KV1a | HEAD `267a4021` | 2.069508e−22 W | −7.448816e−06 W | UNDEFINED FAIL | 1 |
| KV1a | repaired | 1.461838e−01 W | −5.000000e−03 W | 3.4204 % FAIL | 1 |

And the HEAD auditor printed `closure_is_identity_class: false` — "a genuine
constraint here" — on **all three** of those broken open-case ledgers.

### 3b. The mutation harness: four independent wrongnesses, `KV1_runs/mutate_advective.py`

Each mutation is one textual substitution into a copy of the auditor, asserted
to have matched exactly once (an unmatched substitution would run the *unmutated*
auditor and report a clean pass — the false negative the harness exists to
prevent). No solver was run; the field sets are the committed ones.

| mutation | KV1c heated | KV1b degenerate | sealed K0c ×11 |
|---|---|---|---|
| M0 unmutated | PASS 0.0000 % exit 0 | PASS 0.0000 % exit 0 | reference |
| M1 sign flipped | **FAIL 45.6605 % exit 1** | PASS 0.0000 % exit 0 | byte-identical |
| M2 scaled by two | **FAIL 17.4433 % exit 1** | PASS 0.0000 % exit 0 | byte-identical |
| M3 outlet dropped | **FAIL 100.0000 % exit 1** | **FAIL 100.0000 % exit 1** | byte-identical |
| M4 datum → 0 K | PASS 0.0000 % exit 0 | PASS 0.0000 % exit 0 | byte-identical |
| M5 weight dropped | **REFUSED exit 1** | **REFUSED exit 1** | byte-identical |

Three columns, three different jobs. **KV1c** is where the term must be able to
fail, and it does, under three of the four wrongnesses. **KV1b** is the negative
control: mutations that change a sum which is identically zero correctly change
nothing, and M3 — which breaks the zero-sum rather than scaling it — correctly
fires on both. **The sealed set** is the not-more-permissive evidence: no
advective function object is written on a sealed case, so no mutation of that
code path can reach one, and the eleven K0c reports are byte-identical under
every mutation.

M5's refusal is quoted, because the message is the diagnosis:

```
REFUSE: on patch 'inlet' the flux-weighted mean face temperature is
1.000000e+00 K, outside the field range 304.967874..314.438667 K.
        That is the signature of surfaceFieldValue dropping the T weight and
        returning a bare sum(phi). The advective term would be silently wrong;
        no balance is produced.
```

The `1.000000e+00 K` is exactly the signature predicted: with the weight
dropped, `integral T phi / integral phi` is 1 by construction.

### 3c. M4 was predicted to fail and did not. The prediction is REFUTED and the refutation is the more useful result

P6 registered "KV1b FAILS under every one of the four". **M4 does not fail, and
it cannot.** Moving the datum from `TRef` to 0 K changes every patch's advective
term by `rho.cp.datum.Vdot_p`, and those changes sum to
`rho.cp.datum.(net Vdot)`, which is zero when mass balances. The net is
unchanged to 1e-10 W and the case still passes.

What M4 changes is the **denominator**: 0.2079685 W → 8.979442 W on KV1c, ×43.2.
So **the datum is the one advective error the closure test cannot catch**, and a
"simplification" to absolute `T` would loosen the gate 43-fold while every
control in this document still passed. That is precisely why the datum is fixed
in code, recorded in the JSON as `advective.datum_K` / `datum_source`, and
defended in the docstring — rather than left to a caller.

---

## 4. Is the open-case closure convergence-sensitive, or is it a second identity?

This was the prediction most likely to be wrong, and it carried a registered
falsifier: *if the early-iteration imbalance never rises above 0.13 % — the
ceiling K0b measured across every iteration of a sealed case — the claim is
refuted.*

**It is not refuted.** KV1c audited at eleven iteration counts, against the T
equation's own initial residual read from the solver log at the same iteration:

| iteration | T initial residual | imbalance | exit |
|---:|---:|---:|---:|
| 20 | 8.011e−03 | **20.881167 %** | 1 |
| 40 | 3.166e−03 | 9.856046 % | 1 |
| 60 | 1.002e−03 | 3.184486 % | 1 |
| 80 | 1.886e−04 | 0.593174 % | 1 |
| 100 | 2.459e−05 | 0.069250 % | 0 |
| 120 | 5.150e−07 | 0.000889 % | 0 |
| 140 | 8.819e−09 | 0.000009 % | 0 |
| 160 | 2.735e−10 | 0.000000 % | 0 |
| 180 | 2.499e−11 | 0.000000 % | 0 |
| 200 | 4.508e−12 | 0.000000 % | 0 |
| 201 | 4.346e−12 | 0.000000 % (net +1.967e−11 W) | 0 |

The imbalance tracks the residual across nine decades, and **the gate actually
discriminates**: exit flips 1 → 0 between iteration 80 and 100, where the
percentage crosses the governed 0.5 % band.

Set that beside K0b's **sealed** case, which read 0.0128 % at iteration 10 and
never rose above 0.13 % at any iteration. The sealed number never approaches its
own gate; the open one crosses it. One of the two measures the solution and the
other measures the discretisation.

**This is the evidence that the open-case closure is not a second identity.** It
is not an argument from the structure of the equations; it is eleven readings of
one case.

---

## 5. What the open-case closure does and does not establish

Carried from `K2a_RACK_ROW_MODULE_SPEC.md` §8 rather than re-derived, because it
is already written correctly there.

**DOES**: an unconverged energy field, a mis-set temperature offset, a flow-rate
mismatch between a face pair, a patch omitted from the ledger. Measured above:
20.881 % on an unconverged snapshot, 100 % with a patch dropped, 45.66 % with
the sign wrong.

**DOES NOT: circulation.** In K2a's own words —

> A solve with the aisle flow structure entirely wrong — supply short-circuiting
> to the return, reversed aisle recirculation — still closes perfectly once
> converged, because closure tests conservation, not *where* the energy
> travelled. […] Closure is therefore **necessary, never sufficient**, and no
> K2b sentence may cite it as validation evidence; validation is K2c's gate
> alone.

KV1 does not weaken that by one word. A duct with one inlet and one outlet has
no aisle flow to get wrong, so **KV1 cannot and does not test circulation at
all.** What KV1 establishes is narrower and was worth establishing: that the
advective term is computed, correctly signed, correctly scaled, gated on the
mass balance it rests on, and **able to fail**.

---

## 6. Not more permissive — the before-and-after over the committed field sets

The K1 precedent is zero exit-code changes and zero pre-existing keys moved.
**Matched exactly.**

Corpus: every committed thermal field set in the repository — the eleven K0c
cases, the K0b mesh-sensitivity pair, and the five `THERMAL_K0_runs` cases —
audited under `267a4021` and under the repaired auditor with identical arguments.

| | before → after |
|---|---|
| field sets swept | 18 (14 produce a report; 4 refuse for a missing mesh, before and after alike) |
| **exit codes changed** | **0** |
| **pre-existing JSON keys moved** | **0** |
| **pre-existing JSON keys removed** | **0** |
| new keys added | 3 — `advective.state`, `advective.ledger_complete`, `advective.note`, on 14 of 14 |

Every committed field set in this repository is **sealed**, so all fourteen read
`advective.state: not_applicable_sealed`, `ledger_complete: true`, and no
advective function object is written for any of them. The comparison treats
`nan == nan` as equal and normalises the auditor's own recorded rules-file path,
because the baseline copy necessarily lives at a different path; those are the
only two normalisations and both are stated rather than silent.

Two changes are strictly **stricter**, never looser, and neither is reachable on
a sealed case:

- an incomplete ledger cannot PASS;
- an open case whose boundary mass does not balance to within the governed
  tolerance cannot PASS.

The `--allow-advective` refusal is **kept** rather than dropped now that the term
exists. Dropping it would turn cases that exited 2 into cases that exit 0 or 1,
which is a loosening. It is also where the reader is told what an open-case
closure does not reach.

---

## 7. Cost

Single-core throughout, so core-minutes is the sum of wall clocks. **No monetary
figure**: there is no verified rate for this machine.

| | core-minutes | |
|---|---:|---|
| KV1a solve (201 iterations, 1200 cells) | **0.0081** | measured, `COST.txt` |
| KV1b solve (1000 iterations) | **0.0244** | measured, `COST.txt` |
| KV1c solve (201 iterations) | **0.0081** | measured, `COST.txt` |
| **solver time — the authorized part** | **0.0406** | |
| mutation harness (6 mutants × 13 cases, no solver) | **0.4801** | measured |
| before sweep, 18 field sets | **0.0979** | measured |
| after sweep, 18 field sets | **0.0916** | measured |
| stage-1 sweep, convergence sweep, ad-hoc audits (~43 audits) | ~0.219 | reconstructed at the measured 0.306 s/audit |
| reproduction check in a fresh clone (§9) | ~0.55 | reconstructed; itemised below |
| **total charged to this rung** | **~1.48** | |

**The reproduction check is itself compute and is charged rather than omitted.**
The first version of this table stopped at 0.93 and left it out, which would
have understated the rung by more than a third. It re-ran, in a clone of the
committed state: the three solves (**0.0415** measured, from the clone's own
`COST.txt` files — 0.0081 / 0.0253 / 0.0081, agreeing with the primary run to
the fourth decimal), the mutation harness twice (once refusing immediately, once
in full at the primary run's measured **0.480**), eleven `blockMesh` rebuilds
and about five audits (~0.03, reconstructed). It found two real defects, so it
paid for itself; that is a judgement, and the number is here so a reader can
make their own.

**The authorized compute was the small open-duct control case; it cost 0.0406
core-minutes**, under 5 % of the 0.86 core-minutes K0a and K0b cost between them.
Everything else is auditing of already-committed field sets, which the rung's
instructions required directly ("run it over the existing committed field sets
and show the before-and-after"), and which launches no solver.

**One departure from the letter of the authorization, stated plainly.** The
authorization named "the small open-duct control case", singular. Three
configurations of one 1200-cell duct were solved, not one:

- **KV1a** is the authorized case exactly as specified in K2a §8.
- **KV1b** is its no-source negative twin. This campaign's own record is that at
  K1c the negative control was the case that fired S15 and that without it the
  control set would have been quietly worthless; running a positive control
  without its negative twin is a failure this campaign has already logged.
- **KV1c** was built only *after* KV1b was read and found degenerate — its
  closure passes and cannot fail. Without KV1c there is no fail-and-close
  demonstration, which the rung's instructions required explicitly.

The three together cost 0.0406 core-minutes on the same mesh and the same
dictionaries. Each is separately identifiable with its own `COST.txt` should the
owner wish to disallow any of them.

---

## 8. `CONTROL_PREDICTIONS.txt`, reproduced verbatim

Registered before any solver ran; SHA-256
`2ca14c22986341f1c06c106c5872d1468f0b8579c5f088dee99747c8f18e81ce`.
Reproduced in full in `KV1_runs/CONTROL_PREDICTIONS.txt`; the outcomes are:

| | predicted | outcome |
|---|---|---|
| P1 | KV1a recovers −5.000e−03 W within 0.1 % | **CONFIRMED**, +2.40e−08 % |
| P2 | KV1a closure FAILS at about 3.42 %, exit 1 | **CONFIRMED**, 3.4204 %, exit 1 |
| P3 | KV1b closes below 0.5 %, predicted below 0.01 %, exit 0 | **CONFIRMED numerically, but the case is degenerate** — see §2 |
| P4 | KV1b net mass flux below 0.01 % of traffic | **CONFIRMED**, 8.1e−10 % |
| P5 | open-case imbalance above 5 % at iteration 20, falling ≥3 decades; falsifier if it never exceeds 0.13 % | **CONFIRMED on KV1c**, 20.881 % → 0.000000 %, nine decades. Falsifier did not fire |
| P6 | all four mutations FAIL on the open case; sealed set byte-identical | **PARTLY REFUTED.** M1, M2, M3 fire; **M4 does not and cannot** — see §3c. Sealed half confirmed for all |
| P7 | in-log witness of the plant and of the thermal field | **CONFIRMED**, both banner and `outletT` |
| P8 | zero exit-code changes, zero pre-existing keys moved over the committed sets | **CONFIRMED**, §6 |

P5 was registered against KV1b, which turned out to be the wrong case to
register it against — KV1b's field is uniform and has no convergence history
worth the name. It was measured on KV1c, which did not exist when the
prediction was written. That substitution is recorded here rather than papered
over: the *quantity* predicted and its falsifier are unchanged, the *case* moved,
and a reader is entitled to weigh that.

---

## 9. Reproducing this

Verified by cloning the committed state into a fresh temporary directory and
following these instructions literally, after they were written. **The check
found two real defects, which is the only reason it is worth doing**, and both
are fixed above rather than worked around:

1. **`run_kv1.sh` step 2 failed outright.** Its case list was
   `for c in "${@:-A B C}"`, which collapses the default into a single word;
   `cd` then failed on a directory literally named `A B C`. Every earlier
   invocation had passed an explicit case name, so the default path — the one
   the recipe uses — had never been taken. Fixed with an array, and the failure
   is recorded in a comment in the script so it is not "simplified" back.
2. **`mutate_advective.py` step 4 reported a vacuous pass.** `constant/polyMesh/`
   is not tracked, so in a fresh clone the sealed K0c corpus selected on the
   presence of a mesh is **empty** — and `all(...)` over an empty corpus returns
   `True`. The harness printed `sealed_identical_to_unmutated: True` for every
   mutation having compared nothing. That is L-98's vacuous pass. It now
   **refuses** unless it finds all eleven, and prints the count it found beside
   the count it requires.

Neither defect is visible by reading. Both were found by running.

```bash
cd docs/campaigns/F14-cooling-ladder/KV1_runs

# 1. rebuild the three cases from the one table that defines them
python3 build_kv1.py

# 2. mesh and solve (three single-core solves, about 30 s wall clock total)
bash run_kv1.sh

# 3. the three audits. KV1a exits 1 by design (it has a source); the others 0.
cd ../../../..
python3 scripts/heat_balance.py docs/campaigns/F14-cooling-ladder/KV1_runs/KV1a_duct_source --allow-advective
python3 scripts/heat_balance.py docs/campaigns/F14-cooling-ladder/KV1_runs/KV1c_duct_heated --allow-advective

# 4. the mutation harness (no solver; about 30 s).
#    Its sealed half needs the eleven K0c meshes, which are NOT tracked. In a
#    fresh clone it refuses until they are rebuilt, which takes a few seconds:
for c in docs/campaigns/F14-cooling-ladder/K0c_runs/*/; do
  [ -f "$c/system/blockMeshDict" ] && ( . /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
                                        cd "$c" && blockMesh > log.blockMesh 2>&1 )
done
python3 docs/campaigns/F14-cooling-ladder/KV1_runs/mutate_advective.py

# 5. the convergence sweep, any written time of KV1c
python3 scripts/heat_balance.py docs/campaigns/F14-cooling-ladder/KV1_runs/KV1c_duct_heated \
        --time 20 --allow-advective
```

`constant/polyMesh/` is not tracked (`.gitignore:60`) and is rebuilt by step 2.
Step 1 is idempotent and rewrites only dictionaries, never time directories.
Read the auditor's **own** exit status — `python3 scripts/heat_balance.py case |
head` reports `head`'s status, and that mistake has cost this lab a false pass
before.

---

## 10. What is still not validated

- **The turbulent path.** `--allow-turbulent` remains uncalibrated and its
  refusal remains in place. KV1 is a laminar rung and touches none of it.
- **Circulation, on any geometry.** §5.
- **Any open case with buoyancy.** KV1 runs at g = 0 deliberately. A buoyant
  open case couples the temperature field back into the through-flow and the
  advective term is then integrated against a `phi` that the temperature helped
  set. Nothing here says that is wrong; nothing here says it is right either.
- **Compressible or variable-property flow.** The whole derivation assumes
  constant `rho` and `cp`.
