# M6 OWN-MESH FAMILY — FINE TRIPLE {L2, L1, L0} STABILIZED SOLVE registration (transonic cold-start FPE crash repair; ONERA M6 surface Cp vs AGARD AR-138)

> ## 🟠 THIS FILE IS A **DRAFT** — NOT FROZEN, NOT AUTHORISED, NOTHING RUN.
> It is the FRESH pre-registration that carries the **stabilized** rhoSimpleFoam config as a
> **documented crash repair**, because the frozen config change **cannot be an edit** of the
> frozen prereg (rule 2 / T25). It transcribes Gate P and Gate G **byte-identical** from the
> frozen prereg `M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md` (v1.1, freeze commit
> **dddca8ba**) and **widens nothing** — widening a gate threshold/band/cap/label is reserved
> to Sanaa (rule 9).
>
> **LEFT FOR THE cfd-supervisor (check-4, undelegated — SUPERVISION_CHARTER §3):** the gate
> **literals** in §5 and §6 and the **FREEZE BLOCK** (§12) are the supervisor's to set/sign by
> hashing the frozen source registration (rule 2). This DRAFT sets no gate number of its own
> and does not freeze itself.
>
> Drafted by a cfd `lab-lane` on the cfd-supervisor's fix-until-runs brief (rule 16). No
> message from this lane, or from any agent, is Sanaa's consent (rule 9). **SUBMISSIONS
> PARKED (rule 7). The SOLVE is daemon-routed only (§8); no direct launch, no launch until the
> supervisor's freeze commit.**

---

## 0. WHY THIS FRESH PRE-REGISTRATION EXISTS — THE FROZEN CONFIG DID NOT COMPLETE A SOLVE

The frozen prereg `M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md` (freeze commit **dddca8ba**)
registered the own-family fine triple with the rhoSimpleFoam configuration **byte-identical to
RUNG1_M6_R2** (its §5, §10). That configuration **CRASHED** on the first flow solve (§1
below). The frozen prereg was validated only at the **checkMesh** gate; it was **never shown
to complete a flow solve**, and no M6 rhoSimpleFoam log anywhere carries an `End` line.

A frozen config is **never edited** (rule 6), and a config change is a **gate-relevant change
of the solve path** that a frozen document cannot absorb (rule 2 / T25: after first compute the
gates are closed and only dated addenda that cannot alter a gate/threshold/cap/label are
legal). The correct instrument is therefore a **fresh pre-registration** carrying the
stabilized config as a **documented crash repair**, with the **same gates** transcribed
byte-identical and **the same grader pinned unchanged**. This is that document. The frozen
prereg stands as the record of the crash; this one is its stabilized successor.

---

## 1. THE FINDING — SIGFPE AT Time=1 IN SUTHERLAND TRANSPORT (the cfd-supervisor's §3 crash triage, settled)

The frozen fine-triple **L2** solve crashed with **SIGFPE (signal 8)** inside
`Foam::hePsiThermo<Foam::psiThermo, Foam::pureMixture<Foam::sutherlandTransport<...perfectGas...>,
sensibleInternalEnergy>>::calculate()` called from `::correct()`, at **Time = 1**, immediately
after the **first energy (e) solve**:

- `verification/runs/M6_OWN_FAMILY_runs/L2/solve/log.rhoSimpleFoam` — the last solver line
  before the trap is `Solving for e, Initial residual = 0.9999999976, Final residual =
  0.0173775081` (line 129); the FPE stack trace (lines 130–219) resolves to
  `sutherlandTransport<...>::calculate()` → `correct()` in `libfluidThermophysicalModels.so`,
  with the innermost frame in `libm.so` (the `sqrt`), and `trapFpe: Floating point exception
  trapping enabled (FOAM_SIGFPE)` is on (line 29). `mpirun noticed that process rank 1 …
  exited on signal 8 (Floating point exception)` (line 219).
- `verification/runs/M6_OWN_FAMILY_runs/L2/solve/STEP_RC.txt` — `rhoSimpleFoam … inner_rc=136`
  (= 128 + 8), and `STOPPED.txt` records the failed step.
- **CONFIRMED config-level and mesh-independent:**
  `verification/runs/M6SR_runs/L3/log.rhoSimpleFoam` shows the **IDENTICAL** FPE at Time = 1 on
  a **different mesh**. The crash is not a property of any one mesh.
- **No M6 rhoSimpleFoam log anywhere carries an `End` line:** the frozen config was proven only
  at the checkMesh gate, never validated to complete a flow solve.

**Mechanism.** `sutherlandTransport` computes `mu = As·sqrt(T)/(1 + Ts/T)`. rhoSimpleFoam's
first SIMPLE iteration produces a nonphysical temperature (energy transient from a uniform
cold start at M∞ = 0.84), which drives `sqrt(T)` into a domain error in `libm`; with
`FOAM_SIGFPE` trapping enabled that becomes a fatal signal. This is the **transonic
rhoSimpleFoam cold-start instability** — **NOT** a mesh defect, **NOT** a wall-time shortfall,
**NOT** a capability rule-out. The pre-repair state is a crash at Time = 1 (`log.rhoSimpleFoam`
carries `No finite volume options present`, line 93 — no bounding was active).

---

## 2. THE STABILIZATION CONFIG — THE DOCUMENTED CRASH REPAIR (solve-path only; no gate touched)

The repair is implemented as a **NEW case-writer overlay**
`verification/runs/M6_OWN_FAMILY_runs/write_m6_own_family_case_stabilized.py`, which **imports**
the base own-family writer `write_m6_own_family_case.py` (which in turn reuses the pinned M6SR
writer `cases/M6SR/write_m6sr_case.py` **verbatim**) and **layers two documented deltas on
top**. **`write_m6sr_case.py` is NOT edited; `write_m6_own_family_case.py` is NOT edited.**
Each delta is a **solve-path robustness choice**, not a gate change, and each is **INACTIVE or
VANISHING at the converged solution**, so **no Gate-P surface Cp is biased**:

### DELTA A — bounded temperature (`limitTemperature` fvOption): the primary FPE fix
A **new `system/fvOptions`** with a `limitTemperature` fvOption clamping T to
**[Tmin = 100 K, Tmax = 1000 K]**, `selectionMode all`, `active true`.

- **Where it fires:** rhoSimpleFoam's `EEqn.H` calls `fvOptions.correct(he)` **after** the
  energy solve and **before** `thermo.correct()`. `limitTemperature::correct(he)` clamps the
  energy field `he` to `[he(Tmin), he(Tmax)]`, evaluating those bounds with the thermo's own
  `he(p,T) = Cv·T` (which does **not** call `sqrt`). When `thermo.correct()` then derives T
  from the bounded `he`, T stays in **[100, 1000] K**, so `sutherlandTransport`'s `sqrt(T)` is
  always in domain and the SIGFPE cannot occur.
- **Why it does not bias Gate P:** at the converged M∞ = 0.84 M6 field every cell's T lies
  well inside [100, 1000] K (T∞ = 288.15 K; stagnation ≈ 288.15·(1 + 0.2·0.8395²) ≈ 328 K;
  the strongest upper-surface expansion at M∞ = 0.84 stays far above 100 K). The limiter is
  therefore **inactive at convergence** and cannot move a graded Cp. It binds only during the
  cold-start transient. This is the transfer of the DMR bounded-e idea to this pressure-based
  (hePsiThermo) solver.

### DELTA C — bounded |U| (`limitVelocity` fvOption)
A `limitVelocity` fvOption in the same `system/fvOptions`, capping |U| to **600 m/s**
(~2.1× the 285.68 m/s freestream, ~1.5× the strongest physical M6 transonic overspeed ≈ 400
m/s), `selectionMode all`, `active true`. Rationale: it protects the
`nutUSpaldingWallFunction` `u_tau` Newton solve (`calcUTau`, whose `exp()` overflows on a
runaway near-wall |U|) — the SECOND cold-start FPE observed in smoke run 1 (§11). Same
justification structure as DELTA A: at the converged field max |U| < 600 m/s everywhere, so the
limiter is inactive at convergence and biases no Gate-P Cp. **DROPPED (supervisor direction,
§11):** in the smoke tests `limitVelocity` limited **0 cells** — the divergence is energy-led,
not a velocity runaway — so this delta is not evidenced necessary and is removed from the final
minimal config. (It remains in the writer only until the config is finalized after the §11
decision fork; the record here reflects that it is dropped.)

### DELTA B — conservative STARTUP under-relaxation
The `relaxationFactors` `equations` block only: **U 0.7 → 0.2, e 0.7 → 0.1, (k|omega) 0.7 →
0.3**. The `fields` block (**p 0.3, rho 0.05**) is **UNCHANGED**.

- **Why it does not bias Gate P:** relaxation factors change only the **path** to steady
  state, never the steady solution — the relaxation contribution is proportional to
  `(φ_new − φ_old)`, which → 0 as residuals → 0, so the converged Cp is
  relaxation-independent. Gentler startup keeps the first-iteration temperature excursion small
  so DELTA A's limiter is not pinned to its bound every iteration and the residual descent is
  monotone.

### DELIBERATELY NOT CHANGED (a physics-honest refusal, T25)
- **`divSchemes` UNCHANGED.** `div(phi,e)` is **already** `bounded Gauss upwind` (first order
  on energy convection) in the frozen config — there is no second-order energy scheme to fall
  back FROM. `div(phi,U)` stays `bounded Gauss linearUpwind grad(U)` — the shock-resolving
  second-order momentum scheme **Gate P is graded on**. Smearing it to first order would move
  the shock position and **bias Gate P**; a scheme that changes the graded observable is a
  physics change, not a stabilization, and is **refused** as a "fix".
- **thermophysicalProperties, turbulenceProperties, controlDict, sampleDict,
  decomposeParDict, 0/** are written **byte-identical** to the base writer (W's writers reused
  verbatim). The solver (`rhoSimpleFoam`, k-ω SST, `nutUSpaldingWallFunction`), the flow state
  (M∞ = 0.8395, α = 3.06°, Re = 11.72 × 10⁶) and the seven span stations are unchanged.

The overlay's planted-delta selftest (rule 3) passes under `python3` and `python3 -O`: DELTA A's
`limitTemperature[100,1000]` is written (and absent on a bare case); DELTA B's base `0.7` block
is **seen** then replaced by `U 0.3 / e 0.1 / (k|omega) 0.3`.

---

## 3. GATE P — surface pressures against AGARD AR-138 (BYTE-IDENTICAL to the frozen prereg §5)

**Every threshold below is transcribed byte-identical from the frozen prereg
`M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md` §5 (itself byte-identical to
`RUNG1_M6_R2_PREREGISTRATION.md` "Gate P"). NOTHING is invented or widened.** Widening is
reserved to Sanaa (rule 9); pinning the exact frozen literal at freeze is the supervisor's
check (rule 2; §12).

- **Solver (RUNG1_M6_R2:144):** `rhoSimpleFoam` (steady compressible SIMPLE), **k-ω SST**,
  fully turbulent, **`nutUSpaldingWallFunction`**.
- **Momentum `divSchemes` (RUNG1_M6_R2:164):** `bounded Gauss linearUpwind grad(U)` — second
  order with a gradient limiter (first order would not resolve the shock position Gate P is
  graded on). **[Unchanged by the stabilization — §2 keeps this scheme.]**
- **Flow (test 2308):** M∞ = 0.8395, α = 3.06°, Re = 11.72 × 10⁶.
- **Span stations (RUNG1_M6_R2:231):** `C_p` at the seven published sections
  `y/b = 0.20 / 0.44 / 0.65 / 0.80 / 0.90 / 0.96 / 0.99` against the 271 tapped values, with
  the grid-family band on every station.

### Gate P literal
- **reference accuracy (RUNG1_M6_R2:237):** `ΔCp = ±0.02` at `Mo = 0.84` — AR-138 B1-4 §6.1,
  published.
- **grading window (RUNG1_M6_R2:244):** Gate P is graded on `x/c ≤ 0.90` and the rear 10 % is
  plotted and reported, never graded.
- **ordering (RUNG1_M6_R2:246):** Gate P sits behind Gate G. A `PASS` on a family that is not
  `CONVERGING` is `NOT A RESULT`.

The exact gate literal at freeze is pinned by the supervisor hashing the frozen source
registration (§12). This DRAFT sets no number of its own.

---

## 4. GATE G — the rule-5 Roache triple on {L2, L1, L0} (BYTE-IDENTICAL to the frozen prereg §5)

- Grid refinement factor **r = 2**; the three-level own-mesh family (frozen prereg §4) must be
  `CONVERGING` for a band to exist. Cells `71760 / 574080 / 4592640` (cell ratio **8.00**),
  `points` sha256 all distinct — a genuine r = 2 nested family.
- **Observed order `p`** measured from the three levels; **GCI at `Fs = 1.25`**, printed on
  every number, **never quoted when the three values are not monotone** (rule 5).
- **Rule-5 ordering UNMODIFIED:** (1) any level not iteratively converged / not plateaued →
  `NOT A RESULT`; (2) triple `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` → `NOT A RESULT`,
  value + both triples + orders printed beside it; (3) `CONVERGING` → `PASS` inside the
  pre-registered band else `GATE FAIL`, GCI printed. The gate can only turn a `PASS` or
  `GATE FAIL` INTO `NOT A RESULT`, never the reverse.

---

## 5. HONEST-LABELLING LAW (BYTE-IDENTICAL to the frozen prereg §6)

The **credential-grade family band is the {L2, L1, L0} triple** (it varies the discretisation
in all three directions: surface ×4 and wall-normal layers ×2 per level, cell ratio 8 = 2³, so
`r = 2.000` is the genuine isotropic 3-D refinement ratio and `p` is an OBSERVED order). The
**{L2, L1} pair stands only as a LOWER-BOUND band** (assumed `p = 2`, M6SR L-HONEST style) and
NEVER as the gated result (the b44a0376 ruling). The rule-5 term `CONVERGING` may be applied
only to the triple, never to the pair. This law is transcribed unchanged; the supervisor pins
its literal at freeze.

---

## 6. RULES 3/4/5 CARRIED UNCHANGED

- **Rule 3 (planted zero):** the grading path plants a known tap perturbation and **refuses**
  if the reader cannot see it, and refuses on a `case_2308.dat` reference-hash mismatch — the
  same pinned controls as the frozen prereg (§7). The stabilized case writer additionally
  carries its own planted-delta control (§2), passing under `python3` and `python3 -O`.
- **Rule 4 (strict completion + age guard):** a level is done only if `rc = 0`, an `End` line,
  last time == `endTime`, fields present (`T U p alphat nut k omega phi`), `ExecutionTime`
  count == `endTime`, and every field at `endTime` NEWER than the case's own `0/T`. The
  stabilized writer writes `0/` last (and `0/U` last within it), and both the writer and the
  driver **refuse** a solve case where `0/` or any time directory already exists. The comparator
  **refuses (exit 2) rather than degrade**.
- **Rule 5 (Roache triple gating):** as §4. A non-`CONVERGING` triple is `NOT A RESULT`
  whatever the value; no GCI on a non-monotone triple; GCI at `Fs = 1.25`.

---

## 7. GRADING PATH — PINNED UNCHANGED FROM THE FROZEN PREREG (no check-1 diff arises)

**The grader is byte-unchanged from the frozen prereg's freeze (dddca8ba / addendum §13.2),
so no measurement-script diff (the supervisor's undelegated §3 check-1) arises from this
stabilized registration.** The stabilization is entirely in the **solver input** (the case
writer overlay, §2); the **grading path is identical**.

| grading-path artifact | path | pinned identity |
|---|---|---|
| own-family Gate P + Gate G grader (measurement core reused UNCHANGED) | `verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py` | git blob **`da0df95c81ded5833821cfd8a1f711d7f849f93c`** (VERIFIED byte-unchanged on disk at this draft; `git hash-object` = `da0df95c…`) |
| imported MEASUREMENT CORE (Cp + Roache/GCI + planted controls), reused verbatim | `cases/M6SR/analyse_m6sr.py` | git blob `8007b23da5bb3173dacb6eda1d67ca5d90ce9139` (frozen prereg §12.3/§13.2) |
| reference — 271 AR-138 tapped values | `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/case_2308.dat` | sha256 `020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0` (hash-refused inside the imported reader) |
| own-family patch-name source `{wing, symmetry, farfield}` | `verification/runs/M6_OWN_FAMILY_runs/L{2,1,0}/case/system/createPatchDict` | sha256 `3e235b4d1324f4eb3f3986dc6e136ca621e39feb6b091aa2c9bf23cc892b368f` (re-hashed by the grader's Section-7 name screen at run time) |

The supervisor confirms these blob pins at freeze (rule 2, `scripts/check_comparator_freeze.py`).
This DRAFT asserts the grader on disk already hashes `da0df95c…` (verified) and names no new
grading artifact.

---

## 8. LAUNCH — DAEMON-ROUTED ONLY (chief directive; frozen prereg §8)

On the supervisor's freeze commit (§12), the solve is enqueued for the queue daemon
(`scripts/queue_runner.py --daemon`, pid 1887) — the drop of the queue JSON **is** the launch
(survives fleet death). No direct solver launch; **no launch until the supervisor's check-4
freeze.** The queue row carries the one registered hard cap (§9) as a single accumulator
across all three levels, the rule-4 age/absent guard per level, and the grading-path pin (§7).
A DETACHED `setsid` autograder is re-armed (pattern
`verification/runs/M6_OWN_FAMILY_runs/autograde_watch_m6_own_family.sh`) so a verdict — not raw
fields — is what returns.

**Wiring note for the launch target (for the supervisor):** the graded solve must invoke the
**stabilized** case writer (§2). A stabilized solve driver
`verification/runs/M6_OWN_FAMILY_runs/run_m6_own_family_triple_stabilized.sh` (to be committed
alongside this prereg) mirrors the frozen driver `run_m6_own_family_triple.sh` (blob 63ce12b9)
exactly — same pinned image/solver/grader hashing and cap limbs — differing ONLY in the case
writer it delegates to. This is a solver-input wiring change, not a grading change.

---

## 9. COST (rule 12) — RE-DERIVED FROM THE MEASURED RATE

**Rate:** c7a.4xlarge at **$0.0513/core-h** (owner-stated; the box cannot read its own
billing, so any dollar figure is **DERIVED, NOT MEASURED** — `COMPUTE_BUDGET_CHARTER` §5).
**Measured rate 3.40e-8 core-min / cell / iteration**, on this exact geometry and solver class
(frozen prereg §7.2).

**The stabilization does not change per-iteration cost.** Relaxation factors and a
`limitTemperature` fvOption change the SIMPLE **path**, not the per-iteration work; cost ∝
cells × iterations × rate is unchanged at a given `endTime`. The only cost-relevant question
is whether gentler relaxation needs **more iterations to plateau** — which the frozen prereg's
**×2 cap margin already budgets for** (its §7.3: "the ×2 margin covers a restart / extra-
iteration allowance if L0 needs more than ~6,000 iterations to plateau").

### 9.1 Estimate at endTime = 6000 per level (frozen §7.2 basis, transcribed)
| level | cells | core-min = cells × 6000 × 3.40e-8 | derived $ |
|---|---|---|---|
| L2 | 71,760 | **14.6** | $0.0125 |
| L1 | 574,080 | **117.1** | $0.100 |
| L0 | 4,592,640 | **936.9** | $0.801 |
| **{L2, L1, L0} single α** | — | **≈ 1,068 core-min** | **≈ $0.913** |

Each per-level solve is far under the $25 pre-auth ceiling (L0, the largest, ≈ $0.80).

### 9.2 ONE REGISTERED HARD CAP (rule 12: an overrun STOPS the campaign)
**Single hard cap for the stabilized fine-triple SOLVE campaign: 2,136 core-min** (= 2× the
1,068 core-min estimate; derived **≈ $1.83**), a **single accumulator across all three
levels**. Identical to the frozen prereg §7.3 because per-iteration cost is unchanged; the ×2
margin now covers **both** a finer-mesh slow plateau **and** the gentler-relaxation slower
descent. An overrun **STOPS the campaign; it does not get a new budget** (rule 12). Far inside
the $1,000 IBL envelope.

### 9.3 Convergence-headroom OPTION for the supervisor (if a higher endTime is preferred)
If the supervisor judges 6,000 iterations too few for the gentler relaxation to plateau, a
higher `endTime` re-costs linearly and stays well under $25/level. For reference at
endTime = 8,000 per level:

| level | core-min = cells × 8000 × 3.40e-8 | derived $ |
|---|---|---|
| L2 | 19.5 | $0.017 |
| L1 | 156.2 | $0.134 |
| L0 | 1,249.2 | $1.068 |
| **triple single α** | **≈ 1,425 core-min** | **≈ $1.22** |

A cap at 2× this basis would be **≈ 2,850 core-min (≈ $2.44)**. **The supervisor sets the
final endTime and cap at freeze (§12); this DRAFT recommends retaining endTime = 6,000 / cap
2,136 core-min (§9.2) and relying on the ×2 margin, and offers §9.3 as the headroom option.**
The endTime and cap are compute-budget parameters (re-cost), NOT Gate-P/Gate-G literals.

### 9.4 Estimate/actual calibration (rule 12)
On completion of each level and of the campaign, the pre-registered estimate (§9.1/§9.2) is
compared against the actual incurred core-min from the solver logs; the ratio actual/predicted
and the gap attribution (contention vs waste vs misprediction, waste named separately per
`COMPUTE_BUDGET_CHARTER` §6) land as a row in `docs/COST_CALIBRATION.md`. Dollars are labelled
DERIVED at the recorded rate, not measured.

---

## 10. RUN ROOTS — ABSENT (rule 2)

The stabilized SOLVE run roots do not exist and are declared ABSENT so the age guard (rule 4)
and the "no pre-existing time dir" refusal hold at launch:
- `verification/runs/M6_OWN_FAMILY_runs/L2/solve/` — carries the **crashed** frozen-config run;
  the stabilized run MUST use a **distinct, absent** run root (the supervisor names it at
  freeze; suggested `.../L{2,1,0}/solve_stabilized/`), never overwriting the crash evidence.
- `verification/runs/M6_OWN_FAMILY_runs/L1/solve_stabilized/` — **ABSENT**.
- `verification/runs/M6_OWN_FAMILY_runs/L0/solve_stabilized/` — **ABSENT**.

The MESH run roots (`.../L{0,1,2}/case/`, mesh + checkMesh) exist and are unchanged; the
ungraded smoke run (§11) lives at `.../L2/smoke_stabilized/` and is invisible to the grader
(which discovers `.../L{2,1,0}/solve_stabilized` only).

---

## 11. SMOKE TEST — UNGRADED METHOD VALIDATION (produces NO verdict, reads NO gate)

Ungraded smoke tests of the stabilized L2 config (serial, `python3 -O`-parity writer selftest
passed; `verification/runs/M6_OWN_FAMILY_runs/smoke_stabilized_L2.sh` and the diagnostic patches
under `.../L2/smoke_*`). Development compute (method validation), NOT graded runs — no gate read,
nothing planted, no verdict. **The smoke result is PARTIAL and is reported honestly:**

- **DELTA A CLEARS the documented Time=1 Sutherland FPE — CONFIRMED.** With bounded T the solve
  advanced from crashing at iteration 1 to running to iteration 49 (`limitTemperature` active and
  clamping cells; no Sutherland `sqrt(T)` FPE). This is the exact crash the §3 triage named, and
  it is fixed.
- **A RESIDUAL, ENERGY-LED cold-start divergence remains OPEN.** The `e` (energy) equation is the
  sole diverging field: in the best run k/omega residuals are small and converging (~1e-4 / 1e-6)
  and velocity/continuity are reasonable, but `e` spikes (0.10–0.37) and Tmax **overheats to 644 K**
  (contained only by DELTA A's 1000 K cap). The FPE migrates between solvers as fields are bounded
  (Sutherland → `nutUSpaldingWallFunction::calcUTau` → `GAMGSolver` pressure), crashing at iteration
  ~17–49. **Full lever ledger (all ungraded L2 serial smokes, `.../L2/smoke_*`):**

  | lever | outcome |
  |---|---|
  | DELTA A bounded-T (`limitTemperature`) | **CLEARS the documented Time=1 Sutherland FPE** (iter 1 → 49); proven, retained |
  | DELTA C bounded-\|U\| (`limitVelocity`) | limited **0 cells** — a non-cause; dropped |
  | first-order `div(phi,U)` | no help (crashed iter 17) — 2nd-order momentum is NOT the cause |
  | `transonic yes` | **worse** (iter-1 failure) |
  | potentialFoam init (U only) | marginal (iter 38), continuity grew to ~4e-3 — incompressible init is mass-inconsistent at M=0.84 |
  | **LTS `localEuler`** | **UNAVAILABLE** — pinned `rhoSimpleFoam` binary has 0 rDeltaT/LTS strings (rhoPimpleFoam has 5); enabling it aborts on `failed lookup of rDeltaT` |
  | SIMPLEC (`consistent yes`) | **worse** (SIGFPE iter 2) |

  Lower relaxation crashed EARLIER than higher — an inversion showing this is not a classic
  under-resolved-transient. **Crux context:** no M6 `rhoSimpleFoam` log anywhere carries an `End`
  line — the frozen RUNG1_M6_R2/M6SR config was validated only at checkMesh and has **never** been
  shown to complete a flow solve; this is a pre-existing frozen-config issue, not introduced here.
- **DECISION FORK — escalated to the supervisor / Sanaa (§12).** The authorized solve-path
  stabilization levers are exhausted and the highest-confidence one (LTS) is blocked by the pinned
  solver. The remaining options each touch the frozen registration: **(A)** switch the pinned solver
  to an LTS-capable `rhoPimpleFoam` pseudo-transient-to-steady (a §5 byte-identity break — Gate-
  relevant, reserved to the supervisor/Sanaa); **(B)** review the frozen energy setup (the unbounded
  `div(phi,K)` scheme, the adiabatic-wall energy accumulation, or the back-solved Sutherland/thermo —
  a case-physics change to frozen registered values); **(C)** escalate the whole M6-Cp solver
  strategy to Sanaa. **The stabilized config is NOT yet a completed-solve config; the prereg is not
  ready to freeze until a smoke shows a clean descent-to-plateau.**

---

## 12. FREEZE BLOCK — LEFT FOR THE cfd-supervisor (check-4, undelegated)

*(This section is intentionally left for the supervisor. The supervisor: (a) hashes the frozen
source prereg `M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md` at commit dddca8ba and asserts the
§3/§4/§5 Gate P / Gate G / honest-label literals here are byte-identical to it; (b) confirms
the grader blob `da0df95c…` and the imported M6SR core blob `8007b23d…` are byte-unchanged, so
no check-1 diff arises; (c) sets the final endTime and cost cap (§9); (d) names the stabilized
run roots (§10); (e) records the smoke result (§11); (f) flips the DRAFT banner to FROZEN and
commits. Only then is the lane authorized to enqueue the daemon-routed solve.)*
