# S1 FD PLATEAU — result: **`NOT A RESULT`**, and the reason is the registration's own falsifier clause, which fired exactly as written

**Pre-registration:** `cases/dafoam/ladder-b/S1_FD_PLATEAU_PREREGISTRATION.md`, frozen at
commit `a1727bd01c4012e1350cd7138460606a3d103338`, blob md5
`4c40181966d39acc39489b094e4b824a` — **verified from `git show <sha>:<path>`, never from
the working tree.**
**Grading path:** `cases/dafoam/ladder-b/S1_fd_plateau/analyse_s1_fd_plateau.py`, md5
`00617ba89ea5e64861b3d0f78b0d1e81`, **committed at `5f55c7427ee35fe2998fab6f20604b18531f2cbf`
BEFORE any compute** and byte-unchanged at grading.
**Run root:** `/home/ubuntu/certonomous-runs/S1-fd-plateau`.
**Artefacts:** `S1FDP_GRADE.out`, `S1FDP_GRADE.json`, `ledger.csv`, `log.<tag>` ×8,
`fields_<tag>/processor{0..3}/2500/` ×8.
**SUBMISSIONS PARKED.**

---

## 1. THE VERDICT, AND IT WAS NOT COMPOSED BY HAND

> ## ITEM TOKEN: **`NOT A RESULT`**
>
> **The registered falsifier at `h = 0.5` PASSED `P1`'s bar, so `P1`'s verdict is
> WITHDRAWN for every component** — pre-registration §2.5, verbatim: *"if the
> deliberately wrong step **passes** `P1`'s bar, **`P1`'s verdict is WITHDRAWN for every
> component**, because the gate would then be shown not to discriminate step quality at
> all. This consequence is registered now so it cannot be argued away later."*

The comparator applied that clause mechanically at `S1FDP_GRADE.out` step [6]. **It is not
argued away here either.** Every cell is `NOT A RESULT`.

## 2. THE MEASUREMENT UNDERNEATH IS EXCELLENT, AND THAT IS THE UNCOMFORTABLE PART

§2.4's third bullet registers these as **reported with no gate attached**, so they survive
the withdrawal as measurements even though the gate verdict does not:

| cell | `d(0.05)` | `d(0.025)` | `P1` move | rel. err @0.05 | rel. err @0.025 | sign |
|---|---|---|---|---|---|---|
| 5363 | 4.076105013940e-05 | 4.076863698620e-05 | **0.0186 %** | 0.0321 % | **0.0135 %** | match |
| 5428 | 2.679847905604e-05 | 2.676987844938e-05 | **0.1067 %** | 0.1149 % | **0.0081 %** | match |
| 5491 | 2.825074702834e-05 | 2.824329617208e-05 | **0.0264 %** | 0.0086 % | **0.0178 %** | match |

**The plateau is not marginal — it is tight by two to three orders of magnitude against
its own 10 % bar.** All six new primals stopped at iteration **2500**, the `endTime` cap,
identically; none satisfied `1e-8`, so the tolerance argument functions on this case as
*"run the full 2500 iterations"* and every primal took the same number, which removes the
stopping-point channel of S1's original contamination by construction.

**Clearance, at BOTH registered noise floors, neither of which moved:**

| cell | `C(0.025)` at `η = 3.907091e-12` | `C(0.025)` at `η_cons = 2.751958e-11` | bar |
|---|---|---|---|
| 5363 | 5.218e+05 | 7.408e+04 | `C ≥ 5` |
| 5428 | 3.426e+05 | 4.863e+04 | `C ≥ 5` |
| 5491 | 3.615e+05 | 5.132e+04 | `C ≥ 5` |

Satisfied by four to five orders of magnitude at both, exactly as §2.3 registered it would
be, and **no verdict here turns on the window choice** — which was the point of registering
two.

**Second-order convergence, reported with no gate attached.** Mean rel. err falls
0.0518 % → 0.0131 % for a 2× step reduction, a ratio of **3.958** against O(h²)'s ideal
4.000. **Honest caveat: this does not hold per cell** — 5363 and 5428 improve, **5491 gets
worse (0.0086 % → 0.0178 %)**. At `h = 0.025` the errors are down at the level where the
primal's own state error competes with truncation, so the aggregate agreement with O(h²)
is better than the per-cell evidence supports. It is an observation, not a finding.

## 3. WHY THE FALSIFIER PASSED — AND IT WAS ARITHMETICALLY BOUND TO, ON THE REGISTRATION'S OWN NUMBERS

Arm F measured, at cell 5363, `h = 0.5`: `d(0.5) = 3.754018779951e-05`, **rel. err
7.9313 %**.

**§2.5's prediction has two limbs, and they were pre-registered together. One MET, one NOT:**

| limb | registered | measured | |
|---|---|---|---|
| 1 | rel. err against the anchor8 gradient **> 2 %** | **7.9313 %** | **MET** |
| 2 | the `h = 0.5` estimate **FAILS `P1`'s 10 % plateau bar** against `d(0.05)` | **7.9018 %**, i.e. **PASSES** | **NOT MET** |

**Limb 2 could not have held, and this is visible at zero compute from §2.5's own basis
paragraph.** That paragraph predicts `d(0.5)`'s error as *"5363's 0.032 % scales to
≈ 3.2 %"*. `P1` applied to the pair (0.05, 0.5) is `|d(0.05) − d(0.5)| / |d(0.05)|`, and
because `d(0.05)` is itself within 0.032 % of the anchor, that quantity is numerically
almost the rel. err of `d(0.5)` — **≈ 3.2 % predicted, against a bar of 10 %.**

> **A falsifier can only falsify a gate if it FAILS that gate. This one was sized against
> the ADJOINT-COMPARISON criterion (`> 2 %`) and then asserted to fail the PLATEAU bar
> (`10 %`) as well. Those are two different tests, and 3.2 % clears 10 % comfortably.**
> On its own predicted number the withdrawal clause was guaranteed to fire before a single
> primal ran.

The measurement did not rescue limb 2 either: truncation grew **247×** for a 10× step
(effective order **2.39**, steeper than O(h²)'s 100× and consistent with W4's measured
5.4-for-2× on cell 5491), but 247 × 0.032 % = 7.93 % — still short of 10 %. **The
withdrawal is therefore robust, not a near miss:** it fires on the predicted value and on
the measured one.

**This is not a defect in the physics and it is not a defect in the run. It is a defect in
the gate structure, and it is reported rather than repaired**: the registration is frozen,
the consequence is registered, and `CLAUDE.md` rule 2 closes the gates. **Neither the bar
nor the falsifier step may be moved to rescue this item.** Any repair is a NEW
registration, and naming which one is the supervisor's call, not this lane's.

## 4. WHAT WAS PROVEN BEFORE ANYTHING WAS SPENT

1. **The planted zero was SEEN** (`CLAUDE.md` rule 3, §2.7). `PLANT = 1.234e-03` relative
   into the `+` leg of **5428 only**, by line index in the parsed objective list, applied
   to a **copy**, re-read from disk: `d` moved `2.676987844938e-05 → 4.196647264192e-05`;
   observed delta `1.519659419254e-05` equals the implied delta **to all printed digits**;
   **5363 and 5491 unchanged to the last digit**; the run artefacts were untouched.
2. **The refusal is live, not decorative.** Exercised pre-compute against the archive: a
   reader that grades the planted pass off the *original* directory observes delta exactly
   `0.0` and trips §2.7's hard exit.
3. **The reader reproduces a number it did not compute** — all three published §C rel.
   errs, 0.0321 / 0.1149 / 0.0086 % against 0.032 / 0.115 / 0.009 %.
4. **The age guard has teeth.** Margin **1648.2 s** between the newest `0/` file and the
   earliest `endTime` field; mutated so `0/` is newer, the clause flips to `False` and the
   primal reads INCOMPLETE; restored exactly.

## 5. RULE 4, ALL EIGHT PRIMALS

`declared 8 == executed 8 + blocked 0`. Every primal: `rc = 0`, an `End` line, last time
`== 2500 == endTime`, objective printed, all 24 field files present
(`U p k omega nut phi` across `processor{0..3}/2500` — the DASimpleFoam analogue of rule
4's thermal list, substituted explicitly and not silently), and the age guard satisfied.
**No success-reading token is emitted over a short program; none was needed.**

## 6. RULE 12 — ESTIMATE VERSUS ACTUAL

**Registered 60.711 core-min · HARD CAP 75.0 · ACTUAL 62.330 · ratio 1.0267 · cap
respected.** Derived **$0.0533** at the owner-stated c7a.4xlarge rate $0.0513/core-h —
**DERIVED and reported-by-owner, NOT MEASURED**; the box cannot read its own billing.

**Waste: 0.000 core-min, argued both ways rather than asserted.**
*The case for calling Arm F waste:* 16.83 core-min — 27 % of the spend — bought a step
nobody wanted to use, and it is what turned an otherwise clean plateau into `NOT A RESULT`.
*The case against, which is the one that holds:* Arm F is a **registered arm of the
program**, not a failure; it **returned the fact it was launched for**; it MET its own
primary prediction; and it is the reason this item cannot report a plateau it did not
actually discriminate. **Compute that buys a refusal you would otherwise have missed is
the opposite of waste.** No primal was killed, restarted, re-run or discarded; nothing was
netted off.

**Gap attribution: contention, measured rather than guessed.** The 2.67 % overrun is
front-loaded in Arm F, which ran while **eight foreign `buoyantBoussinesq` ranks held half
the box at ~100 % CPU** (heat-transfer's T-family): those two primals cost 8.43 and 8.40
core-min against the 7.5889 basis (**+11 %**), while the six Arm P primals, run as that
load eased, cost 7.70 / 7.60 / 7.70 / 7.53 / 7.50 / 7.47 — a mean of **7.583, within
0.08 % of the basis.** **The estimator was essentially exact; the miss is entirely
contention on two of eight primals.** No row approached the 3600-s stall rule (longest
253 s), so **gross == cleaned == 62.330**.

## 7. WHAT THIS ITEM DOES NOT ESTABLISH

- **It does not defend `S1_CBFS_REINVERSION_RESULT.md:92`'s `PASS`.** §2.4's first bullet
  made that defence conditional on `P1` landing, and `P1`'s verdict is withdrawn. The
  disposition of that `PASS` is unchanged and remains the supervisor's.
- **It does not show any published value wrong.** Nothing here contradicts §C's numbers;
  the h=0.025 measurements agree with them closely.
- **No in-item control proves the environment reproduces the archive bit-identically.**
  `P1` compares an **archived** `d(0.05)` against a **new** `d(0.025)`, and §2.8 budgeted
  no new baseline primal, so the registered bit-identity check on an unperturbed control
  had no new primal to fire on and is **vacuously satisfied, not verified.** What WAS
  established, at zero compute: all 16 staged case files are bit-identical to the archive;
  `0/`, `constant/`, `system/controlDict`, `fvSchemes`, `fvSolution` and `runScript.py`
  all predate the archived sweep; the container image `dafoam-subpclu:v1` (`ba2d16ab9d57`,
  2026-08-04) predates it; and the one file that does **not** — `system/decomposeParDict`,
  modified 2026-08-08 01:56, **after** the sweep — was cleared **by measurement**, the
  archived and post-edit logs decomposing identically (scotch, 4 subdomains, cells
  5254/5204/5262/5280, same shared-face counts). **That is strong provenance. It is not
  the same as a reproduced floating-point control, and it is not claimed to be.**
- **Arm W4 is untouched.** Registered separately (§3, §6.1) at 116.400 core-min, cap
  150.0; it runs only on the supervisor's read of this result.
- **Cell 6490 remains a named gap** (§3.5) — the supervisor sweep's own probe is the
  auditor's to re-open.

## 8. A DIVERGENCE FOUND IN THE WORKING TREE, INSPECTED AND NOT REVERTED

The on-disk copy of the frozen pre-registration is **not the frozen document**: it hashes
`3b563a865b8b5ea5259de56527d417ec` and **its §6 FREEZE section is absent** — the disk holds
the **pre-freeze draft**. The committed blob `b2cfb38d` is byte-identical at `a1727bd0` and
at HEAD, and everything in this item was graded against it. Per `CLAUDE.md` rule 10 the
divergence is **inspected and reported, never reverted**, and this lane did not touch the
file. Had the freeze been verified from disk, §6.1 item 5's own warning would have landed:
*"a freeze-time hash taken from disk would hash the pre-freeze document, which this family
measured on 2026-09-04."*
