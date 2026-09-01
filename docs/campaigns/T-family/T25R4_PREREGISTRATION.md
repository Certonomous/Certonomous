# T25R4 — 8-cell aviation battery module, resolved channels, transient conjugate: **THE CONVERGENCE RUNG, WITH A MESH-INDEPENDENT PRESSURE CRITERION**. PRE-REGISTRATION

**Drafted 2026-09-01T~17:50Z by a heat-transfer `lab-lane`. NOTHING HAS BEEN RUN
UNDER THIS REGISTRATION. NO SOLVER HAS BEEN LAUNCHED.**

**AUTHORITY.** Sanaa's directive of 2026-09-01 ~15:45Z, `f4c8e466`, §0 and §2 —
unchanged and still governing. **The specific shape of the fix registered here is
the heat-transfer supervisor's ruling 3 of 2026-09-01T~17:31Z**, and this lane
records it rather than re-deciding it.

**THIS DOCUMENT SUPERSEDES `T25R3_PREREGISTRATION.md` (frozen `8cef4791`,
Amendment A1 `e46aa244`, Addendum D1 `6b1f3968`).** That document is **not edited
and not struck**; it stays on disk intact with its results at
`T25R3_RESULTS.md`. §16 of T25R3 closed its gates at first compute and a numerics
change cannot land as an addendum, so this is a **new registration**.

Verdict vocabulary is `CLAUDE.md` rule 1's and is used nowhere loosely.

---

## 0. WHY T25R3 IS SUPERSEDED — **MEASURED, AND THE NUMBER IS ×1.00**

T25R3 registered, at its §4.1, the inherited linear-solver criteria:

```
    "p_rgh.*"    { solver GAMG; tolerance 1e-08; relTol 0.01; }
    p_rghFinal   { $p_rgh;      tolerance 1e-08; relTol 0;    }
```

`tolerance` is an **ABSOLUTE** residual target. The absolute scale of an OpenFOAM
residual moves with cell count, so **an absolute tolerance is a different
physical demand on every mesh.** Measured across the T25R3 leg-A logs:

| | L1 (16,608) | L2 (37,368) | L3 (84,078) |
|---|---|---|---|
| median **initial** `p_rgh` residual | 9.67e-09 | 1.11e-08 | **8.78e-03** |
| median **final** residual reached | 9.67e-09 | 7.41e-09 | 7.94e-05 |
| **median reduction factor ACHIEVED** | **×1.00** | **×1.51** | **×100.94** |
| mean GAMG iterations per solve | **0.31** | **41.64** | **382.20** |
| solves counted | 105,000 | 4,956 | 314 |

> **ON L1 THE PRESSURE SOLVE REDUCES THE RESIDUAL BY A FACTOR OF 1.00. IT DOES
> NOTHING. The residual arrives at 9.67e-09, the absolute threshold of 1e-08 is
> already satisfied, and GAMG exits without iterating.** On L3 the same
> dictionary delivers ×101. **A 1,233× spread in solver effort across a ladder
> whose entire purpose is to compare three levels solved to the SAME standard.**

**The cost blow-up (19–33× above L1) and a noise observed order are the same
defect seen from two ends**, and Sanaa's §0.2 — *"if it is not, the observed
order is noise, not discretisation"* — is the rule that names it.

---

## 1. ⚡ THE FIX — **A FIXED REDUCTION FACTOR ON EVERY LEVEL, WITH A FLOOR THAT NEVER BINDS**

**Registered `system/coolant/fvSolution`:**

```
    "p_rgh.*"
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-13;      // FLOOR ONLY. Chosen so it NEVER binds.
        relTol          0.01;       // the fixed factor: x100 per intermediate solve
    }
    p_rghFinal
    {
        $p_rgh;
        tolerance       1e-13;      // same floor
        relTol          1e-3;       // the fixed factor: x1000 on the FINAL sweep
    }
```

### 1.1 Why this is the fix and not a tighter absolute tolerance

The supervisor's ruling is explicit and this lane agrees on the arithmetic:
**simply tightening `tolerance` would make the fine levels costlier and leave the
coarse level still unsolved** — the defect inverted rather than repaired.

**What actually changes is which criterion BINDS.** `relTol 0.01` was *already
registered* on the intermediate solves in T25R3 — and it never bound on L1 or L2,
because the absolute `1e-08` short-circuited it. **Lowering the floor does not
tighten the demand; it stops the floor from cancelling the demand that was
already there.** And `p_rghFinal` had `relTol 0` — no relative demand at all —
which is repaired by giving it one.

### 1.2 ⚠ THE FLOOR IS PROVED NOT TO BIND, ON EVERY LEVEL, FROM MEASURED DATA

If the floor binds on one level and the relative criterion on another, the
levels are **still** solved to different standards and the fix is cosmetic. So
the floor is checked against the measured initial residuals of §0:

| level | median initial | × 1e-3 (the final-sweep target) | floor 1e-13 | binds? |
|---|---|---|---|---|
| L1 | 9.67e-09 | **9.67e-12** | 1e-13 | **NO** — target is 97× above the floor |
| L2 | 1.11e-08 | **1.11e-11** | 1e-13 | **NO** — 111× above |
| L3 | 8.78e-03 | **8.78e-06** | 1e-13 | **NO** — 8.8e7× above |

**The relative criterion binds on all three levels and the floor binds on none,
so all three are solved to the same standard.** The floor exists only to stop the
solver chasing double-precision noise if a residual ever arrives near zero.

### 1.3 What is NOT changed, and why — `h`, `U`, `k`, `omega`

Their `Final` variants carry the same structural flaw (`relTol 0` with an
absolute `tolerance 1e-10`). **They are left alone, on evidence:**

| equation | L1 | L2 | L3 | reading |
|---|---|---|---|---|
| `h` | 1.00 | 1.00 | 1.00 | **already perfectly comparable** |
| `k` | 0.01 | 0.17 | 1.00 | tiny absolute counts; spread is 1 iteration |
| `omega` | 0.00 | 0.13 | 1.00 | same |

**One lever per rung.** `p_rgh` is the measured defect at 1,233×; `h` is at
1.00× and needs nothing. Changing four criteria at once would make the probe of
§2 unattributable. **The structural flaw in the `h`/`k`/`omega` `Final` keys is
recorded here as a KNOWN, UNREPAIRED item** so a successor finds it stated rather
than discovers it — and §2.3 will detect it if it ever starts to matter.

---

## 2. ⛔ THE PROBE, AND ITS **PRE-COMPUTE ACCEPTANCE GATE** — the centre of this registration

> The supervisor's ruling, and it is the part that makes this rung differ from
> its predecessor in kind rather than in degree: **register the VERIFICATION of
> the fix, not just the fix.** *A fix whose success is only observable after the
> expensive run is not a fix this lab can afford twice.*

### 2.1 The probe

**Three runs, one per mesh level, leg A only, `endTime 2.0 s` (100 steps at
dt = 0.02).** Same everything else as the full rung: same meshes, same ramp
(the probe therefore covers the t = 0→1 s ramp, the hardest part of the
transient), same `nOuterCorrectors 15`, same 2-rank manual decomposition.

| id | mesh | steps | purpose |
|---|---|---|---|
| `P1` | L1 | 100 | comparability + rate |
| `P2` | L2 | 100 | comparability + rate |
| `P3` | L3 | 100 | comparability + rate |

### 2.2 `G-P` — **THE GATE THAT DECIDES WHETHER THE LADDER LAUNCHES AT ALL**

Let `I(level)` = mean GAMG iterations per `p_rgh` solve over the probe.

> **`G-P` PASSES iff `max(I) / min(I) ≤ 3.0` across `{P1, P2, P3}`.**

- **`G-P` PASS → the full ladder launches.**
- **`G-P` FAIL → THE LADDER DOES NOT LAUNCH.** The criterion is still
  mesh-dependent, the rung is `NOT A RESULT` before it starts, and the successor
  re-registers the criterion. **No amount of the ladder is run "to see".**

**WHY 3.0, AND IT IS REGISTERED BEFORE THE PROBE EXISTS.** The supervisor's
instruction is *"if the iteration counts still differ by an order of magnitude,
the criterion is still mesh-dependent"* — so the bar is at most 10. **3.0 is
chosen tighter than that**, because a factor of 10 in solver effort is already
enough to make one level's iterative error a different size from another's, and
because the measured defect being repaired is 1,233× — a fix that only reaches
9× has not really worked. **A perfectly mesh-independent criterion would give
1.0; 3.0 admits the genuine variation in conditioning between a coarse and a fine
mesh at equal relative convergence, and nothing more.**

**THIS GATE CAN LOSE, AND THIS LANE'S PREDICTION IS AT §7.**

### 2.3 Reported by the probe, gating nothing

Mean iterations per solve for `h`, `k`, `omega` per level, with their own
max/min ratios — so §1.3's decision to leave them alone is **checked by
measurement each time**, not assumed once. **A ratio above 10 on any of them is
a REPORTED finding and a successor's item; it does not gate `G-P`**, because
`G-P` was registered against `p_rgh` before the probe ran and widening a gate
after seeing data is exactly what a freeze forbids.

### 2.4 Cost of the probe, priced separately as ordered

Priced off **S1's own measured rate** — 0.1988 s/step at 2 ranks on L1 at
`nOuterCorrectors 15`, which came in at **×1.02** against its pre-registered
POINT. **That rate was measured on a run whose pressure solve was doing nothing,
so it is a LOWER BOUND and is registered as one.**

| id | mesh | steps | POINT core-min (2 ranks) | HARD CAP | `timeout_s` |
|---|---|---|---|---|---|
| P1 | L1 | 100 | 0.66 | **8** | 240 |
| P2 | L2 | 100 | 1.49 | **18** | 540 |
| P3 | L3 | 100 | 3.36 | **40** | 1,200 |
| **probe total** | | | **5.51** | **66** | |

**The cap margin is ×12, not ×4, and the reason is stated:** the whole point of
the probe is that the new criterion's cost **is not known** — L1's pressure solve
goes from 0.31 iterations per solve to something unmeasured. **A ×4 margin sized
on a rate measured with the solver switched off would be a cap chosen to be
breached.** 66 core-min is $0.056 at cap.

---

## 3. THE FULL LADDER — **REGISTERED, BUT NOT PRICED UNTIL THE PROBE LANDS**

The run set, the mesh family, the ramp, the time-step schedule, the
decomposition, the field tuple, the gates and the Roache machinery are **carried
forward from T25R3 unchanged** and are restated here only where a reader needs
the number.

| id | mesh | cells | ladder | dt (legA/legB) | steps | `nOuterCorrectors` |
|---|---|---|---|---|---|---|
| S1 | L1 | 16,608 | space coarse | 0.02 / 0.1 | 11,800 | 15 |
| S2 | L2 | 37,368 | space **middle** | 0.02 / 0.1 | 11,800 | 15 |
| S3 | L3 | 84,078 | space **finest** | 0.02 / 0.1 | 11,800 | 15 |
| T2 | L2 | 37,368 | time dt/2 | 0.01 / 0.05 | 23,600 | 15 |
| T4 | L2 | 37,368 | time **dt/4** | 0.005 / 0.025 | 47,200 | 15 |
| W30 | L2 | 37,368 | iterative (`G-I`) | 0.02 / 0.1 | 11,800 | **30** |

**⛔ THE LADDER'S POINT AND CAP ARE DELIBERATELY LEFT UNSET IN THIS DOCUMENT AND
ARE FIXED BY A DATED AMENDMENT AFTER THE PROBE AND BEFORE THE LADDER'S FIRST
COMPUTE.** That amendment is legal precisely because it lands **before first
compute on the ladder** (rule 2), and it must state the condition and name the
run directories that do not yet exist.

**This is not a way of avoiding rule 12's costing requirement; it is the only
honest way to satisfy it.** T25R3's POINT was wrong by 19–33× because it
extrapolated a rate measured on a solver that was not running. **Pricing this
ladder before the probe would repeat that error knowingly.** The probe exists to
produce the number, and 66 core-min is the registered cost of finding it out.

### 3.1 Carried forward, unchanged, and each verified on disk

- **Mesh family 24/36/54 cells across the gap** — 16,608 / 37,368 / 84,078,
  ratio **2.2500 exactly** at both steps, **r_eff = 1.5000**, in Sanaa's
  [1.5, 2.0] band at its lower edge; growth ratios 1.14991 / 1.09520 / 1.06151;
  `checkMesh` OK, maxNonOrth **0**, on all three. **All three meshes are already
  built.**
- **The 1 s ramps** at t = 0 and t = 60, `volumeMode specific`, 1e5 → 2.5e4 W/m³;
  ∫ = 2.698750e+07 J/m³, adiabatic bound **10.7950 K**, **647,700 J** — the
  figure C1 gates against.
- **The two-leg schedule** (dt 0.02 to t = 70, then 0.1) with the leg-A-only
  launch guard, and every breakpoint an exact multiple of every registered dt.
- **Addendum D1's decomposition** — `manual`, shared plane **x = 0.050 m**, both
  regions, 2 ranks, identical on every run. `simple` is **refused**: it cuts each
  region at its own bounding-box midpoint (0.0500 vs 0.0750) and tears the
  `useImplicit` conjugate interface.
- **The field tuple** — module `T, p`; coolant `T, U, p, p_rgh, alphat, nut, k,
  omega`. **NOT `h`** (solved, never written). **NOT `epsilon`** (kOmegaSST).
- **`G-I`, `G-S`, `G-T`**, τ = 1.000e-01 K, the reported second tier
  1.234e-02 K, and **Amendment A1's composition: the binding iterative
  requirement is 1.000e-02 K**, 2.32× tighter than the 2.315190e-02 K that failed
  T25R2.
- **Roache triple gating** on both ladders, `p ∈ [0.5, 1.5]` (Euler in time,
  upwind in space — **formal order 1**), GCI at Fs = 1.25, and rule 5's clause
  order.
- **The strict completion rule** and its age guard, per leg, per §9 of T25R3.
- **`analyse_t25R3.py` and `mark_done_t25R3.py`** carry forward as
  `analyse_t25R4.py` / `mark_done_t25R4.py` with **two changes only**: the frozen
  document path, and **the unguarded `_UNIFORM_RE.match(...).group(1)` at
  `patch_values` becomes a `refuse()`** — the supervisor's hardening item, which
  was correctly not allowed to delay the T25R3 launch and is landed here.

---

## 4. `--bind-to none` IS REGISTERED AS A LAUNCH REQUIREMENT

Not an operational detail. **Every independent `mpirun` numbers cores from zero**,
so N concurrent `mpirun -np 2` jobs pin all their ranks to the same 2 cores.
Measured in T25R3: twelve ranks on CPUs 0 and 1, ten cores 100 % idle
(`taskset -pc`, `mpstat -P ALL`). **`L-431`.** It changes no number — rank count,
decomposition and arithmetic are identical — so **only wall time moves**, and the
probe's rate measurement is meaningless without it.

**The launcher's registered invocation is:**

```
setsid nohup bash run_one_t25R4.sh <RUN> </dev/null > launch.<RUN>.out 2>&1 &
disown
```

`</dev/null` is load-bearing: without it the solvers inherit the caller's stdin
and are `SIGKILL`ed when the caller exits, leaving **no rc file and no trap
output** (T25R3 §6.3).

---

## 5. THE STRICT COMPLETION RULE, AND THE MONITORING READER

Rule 4 as registered at T25R3 §9, per leg, unchanged.

**AND A REGISTERED MONITORING RULE, because a false zero did damage in T25R3:**
live solvers are counted by **`readlink /proc/<pid>/exe`**, never by
`ps -o comm` (**truncates at 15 characters** — it reported zero while twelve
ranks ran) and never by `pgrep -f` (**matches the matcher's own command line**).
**A known-live process is planted in the target directory to prove the reader can
see a non-zero before any zero from it is believed.** `CLAUDE.md` rule 3 is a rule
about **any** zero, process counts included. **`L-432`.**

---

## 6. THE REGISTERED CEILING — unchanged from T25R3 §13, and it must not drift

**BEST REACHABLE:** `PASS` on `G-P`, `G-I`, `G-S` and `G-T`, with `CONVERGING`
Roache triples, observed orders inside [0.5, 1.5], and a GCI band on every
reported number. **A VERIFICATION result.**

> **`P` — validation against a public primary — IS NOT REACHABLE BY THIS RUNG OR
> ANY SUCCESSOR ON THIS CASE.** The geometry is a construction; the loads are
> Sanaa's ruling; no public dataset exists for this configuration.

The band is **numerical only** and contains **no model-form uncertainty**: not the
2-D idealisation, not the isotropic solid, not `kOmegaSST` at `Re_Dh = 3200`
where it is weakest, not first-order upwind. Four unquantified assumptions, named
here because naming them costs nothing here and is impossible later.

---

## 7. THE PREDICTION — **REGISTERED SO THAT IT CAN LOSE**

1. **`G-P` PASSES.** Ground: with the floor proved non-binding on all three levels
   (§1.2), every level is asked for the same relative reduction, and GAMG's
   iteration count at fixed relative reduction varies weakly with mesh size.
   **This lane predicts `max(I)/min(I)` lands in [1.3, 2.5].**
2. **The ladder gets CHEAPER at L3 relative to L1, not more expensive overall
   than T25R3's measured rates.** Ground: L1's per-step cost must rise (it was
   doing nothing), while L3 already performed ×101 and is asked for ×1000 on one
   sweep in thirty. **The 19–33× spread should collapse toward the ~2.25× and
   ~5.06× cell-count ratios.** *If instead the total ladder cost rises above
   T25R3's projection, this prediction has lost and the rung is re-priced, not
   re-explained.*
3. **`G-S` FAILS on Q1 (the outlet history) and PASSES on Q2 (the solid peaks)** —
   carried forward from T25R3 §14 unchanged, and still the claim this lane
   expects to lose the rung on.
4. **`G-I` PASSES.**

**Claim 1 is the one this rung turns on.** If `G-P` fails, nothing else is
evaluated and the 66 core-min of probe is the whole spend — **which is the
registration working, not failing.**

---

## 8. ORDER OF OPERATIONS — REGISTERED, AND NOT NEGOTIABLE

1. **This document is committed.**
2. **The supervisor reads this registration and the two-line comparator diff AS A
   DIFF.** Undelegable. **No solver launches before this step completes.**
3. Stage `P1`, `P2`, `P3`; `verify_mesh_t25R4.py` refuses on any mismatch,
   **including that `tolerance 1e-13` and the two `relTol` values are exactly as
   registered** — a swapped tolerance would make `G-P` meaningless while leaving
   every other check green.
4. **Run the probe.** 66 core-min at cap.
5. **Evaluate `G-P`. If it FAILS, STOP.** The ladder does not launch and the rung
   is `NOT A RESULT` before it starts.
6. **If `G-P` PASSES: a dated amendment fixes the ladder's POINT and CAP from the
   probe's measured rates**, before the ladder's first compute, naming the run
   directories that do not yet exist.
7. Launch the six. Then grade in the registered order: `G-I`, the Roache
   classification, `G-S`/`G-T`, C1–C3.

---

## 9. FREEZE

Frozen at this document's commit. **Before first compute** amendments are legal
and must state the condition and how it was checked; **after first compute the
gates are closed** and changes land only as dated addenda that cannot alter a
gate, threshold, cap or label. `analyse_t25R4.py` hashes this document against
the committed blob and **REFUSES on a mismatch**.

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

---

## 10. WHAT THIS LANE COULD NOT VERIFY

1. **The new criterion has never been run.** Every number in §1 is measured on
   T25R3's logs under the OLD criterion. §1.2's proof that the floor does not bind
   uses **old** initial residuals; the new criterion changes the iterate the next
   solve starts from, so those residuals will move. **The probe is what settles
   it, and that is why the probe gates the ladder.**
2. **The cost of the new criterion is unknown**, which is why §3 declines to price
   the ladder and why the probe's cap margin is ×12.
3. **`G-P`'s threshold of 3.0 is a judgement**, tighter than the supervisor's
   "order of magnitude" and looser than the ideal 1.0. It is registered before the
   probe exists and this lane cannot claim it is the right number, only that it is
   frozen and reasoned.
4. **S1 had not finished at drafting** (leg B 1,219/8,300), so §2.4's rate is
   leg-A only and is a **lower bound** in two independent ways: the pressure solve
   was doing nothing, and leg B's coarser step has not been observed.
5. **The `h`/`k`/`omega` `Final` keys still carry the structural flaw** (§1.3).
   Left unrepaired deliberately, reported by §2.3, and stated here so it is a
   known item rather than a discovery.

---

**NOTHING IN THIS DOCUMENT HAS RUN. THE NEXT ACTION IS THE SUPERVISOR'S DIFF-READ,
NOT A LAUNCH.**

<!-- END OF T25R4 PRE-REGISTRATION v1.0 -->
