# Curriculum item D13 — basin/restart robustness on the D1 problem: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the item it registers is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or on completion**
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**NOT YET LAUNCHED.** This file is frozen **before any container starts** (`CLAUDE.md` rule 2;
`SUPERVISION_CHARTER.md` §3 check 4). Filed 2026-08-25 by a `lab-lane` of the DAFoam team for
curriculum item **D13** (`cases/dafoam/EXPERTISE_CURRICULUM.md`, Tier 5). `RESULTS.md` is written
afterwards, in this directory, and **does not revise this file**; departures land as dated
amendments at the foot, never by editing above.

**SHORT FORM.** Written on the 10-line pre-registration form Sanaa authorised 2026-08-25, verbatim:
*"Prereg goes template-speed: standard verification/validation cases use the 10-line prereg form
(case, reference, quantities, bands, ladder, decomposition seed, criteria) — minutes to freeze, not
sessions. Bespoke frozen documents are reserved for novel or contested cases only."* D13 is
standard: it reuses a proven producer on a closed case. **Her rigor standard is unchanged**, and
every non-negotiable below is carried in full.

---

## 0. THE TWO-ROW RULE, AND WHAT THIS ITEM DOES NOT BUY — read first

`DAFOAM_CHARTER.md` §6: a DAFoam verdict is **TWO ROWS — shipped and patched — or it is not a
verdict about DAFoam.**

**The dafoam-supervisor's ruling, carried here verbatim as the supervisor's and not this lane's:**

> D13 buys the **PATCHED row only**; the **SHIPPED row is NOT BOUGHT**. The reason: D13's claim is
> about **basin structure conditioned on a fixed toolchain**, and D1-C′ already measured the
> shipped-vs-patched delta on this exact case — finding: the stock IDWarp `warpDeriv` defect is
> **design-point dependent**, 640 % plus a sign flip at baseline but ≤ 2.80e-06 at the converged
> point; **mechanism UNTESTED, HYPOTHESIS ONLY**. The consequence, stated plainly: **D13 cannot
> claim a toolchain-independent basin result.**

Every number this item produces is a statement about `dafoam-idwarp-rot:v1` and about nothing else.

---

## 1. CASE

**A1 NACA0012, D1's exact problem, unchanged.** `DASimpleFoam`, 4,032 cells, **np = 1**.
Minimise `CD` subject to the equality constraint `CL = CL* = 0.500000` and the case's own
DVGeo/DVConstraints geometric constraints — `thickcon ≥ 0.5×` baseline, `volcon ≥ 1.0×` baseline,
`rcon ≥ 0.8×` baseline. Design variables: the **8 FFD shape-function modes** (`shape`) plus angle
of attack carried as `patchV[1]`; `patchV[0]` (`U0`) is pinned `lower = upper = 10.0` and inert.
Optimiser **IPOPT**, `tol 1e-5`, `constr_viol_tol 1e-5`, **`max_iter 40`**, `mu_strategy adaptive`,
`nlp_scaling_method none` — all inherited byte-identically from D1's producer.

**What is new, and it is the whole item:** the run starts from **five perturbed design vectors**
instead of the undeformed one, each **cold-started** from a pristine `base/`, and the five optima
are compared against a **band frozen here, before any start runs**.

## 2. REFERENCE / ANCHOR

**D1 is CLOSED, PATCHED row `PASS`.**
`cases/dafoam/ladder-a/A1/curriculum_D1/{PREREGISTRATION.md,RESULTS.md}`.
Measured there: `EXIT: Optimal Solution Found.` in **11 majors**, Overall NLP error
**4.0871293161759560e-07**, constraint violation **1.9421312102974042e-07**,
`CD 0.020943920630946831 → 0.017527899854535338` = **−16.310321 %** at
**|CL − 0.5| = 1.879064e-07**, **24/24** constraint rows in bound, endpoint FD **≤ 0.2553 %** on
**4/4** named components with **zero sign flips**. Cost **7.000 core-min gross**, **0.533 core-min
named waste**, **0.304×** of its own 23.0 core-min estimate.

**The machine-readable anchor, and the 6th member of this item's comparison:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO/endpoint_20260824T160552Z_1399954.json`,
**md5 `e63f57710cee6e2170f2e9cef39f8b2a`** — verified present and byte-unchanged by this lane
before this file was frozen. Its `CD`, `shape` and `patchV` are asserted against `D1_REF` in
`d13_basin.py` and a drift refuses (exit 2).

**Toolchain anchor:** patched image `dafoam-idwarp-rot:v1`, image id
**`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`** (re-read on this box
2026-08-25), in-process `IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425`.
`DAFOAM_CHARTER.md` §11 — **the hash is the identity, the version string is not.**

## 3. QUANTITIES

Per start, all at the design point the optimiser actually reached:
final **`CD`**; final **`|CL − CL*|`**; **major count** and IPOPT's own **`EXIT:`** statement;
the **active-constraint set** (all 23 geometric rows, per family, never aggregated); and the
**endpoint FD table** — per named component: `J_adj`, FD at both rungs, relative error at the
graded rung, sign flip, two-step plateau agreement, measured clearance `C`.
Cross-start: the **pairwise** `ΔCD`, `‖Δshape‖_∞` and `ΔAoA` over all pairs of graded members.

## 4. BANDS — THE OPTIMUM-EQUIVALENCE BAND, FROZEN BEFORE ANY START RUNS

**This is the whole item, and the band is sized from measured artifacts, not chosen.**
The curriculum's own named failure mode for D13 is *"declaring one basin from optima that differ
inside FD noise."* The band therefore has **two edges and three cells**, all frozen here and all
implemented in `d13_basin.py` §2, which derives the proxy tolerances from the measured inputs
rather than restating a typed constant.

**Edge 1 — `ε`, the SAME-OPTIMUM edge. Below it, two optima are not distinguishable by any
instrument this case possesses.**

| channel | `ε` | what MEASURED it |
|---|---|---|
| `\|ΔCD\|` | **`1.957349804806996e-08`** | **η**, A1's *own* measured CD plateau noise — peak-to-peak of the last 5 samples at `printInterval 10`, D1 arm E run 2, on this exact case and mesh |
| `‖Δshape‖_∞` | **`1.0e-4`** | `SHAPE_FLOOR` in the frozen `d1_fd_endpoint.py`, described there as **"A1's own measured roundoff branch"** |
| `\|ΔAoA\|` (deg) | **`1.0e-3`** | `PATCHV_FLOOR` in the same frozen file |

*Why `ε_CD` is allowed to be that tight:* the first-order objective consequence of a DV difference
at `ε` is bounded by D1's **measured** endpoint dual infeasibility `4.0871293161759560e-07` times
`‖Δx‖ ≤ sqrt(8·(1e-4)² + (1e-3)²) = 1.039e-3`, i.e. **4.25e-10** — **46× below `ε_CD`**. `ε_CD` is
therefore dominated by the measured primal noise floor, which is the correct thing for it to be
dominated by.

**Edge 2 — `Δ_FD`, the FD-NOISE PROXY, the upper edge of the unresolvable window.**
`Δ_FD,rel = 0.2553 %` — D1's **measured** worst endpoint FD agreement over 4/4 named components
(`curriculum_D1/RESULTS.md` §5.2, worst component `patchV[1]`). Applied per channel as
`Δ_FD,rel × |reference|`, giving `Δ_FD,CD = 4.474873e-05`, `Δ_FD,shape = 1.205754e-04`,
`Δ_FD,AoA = 2.881409e-03` deg.

> **DISCLOSURE, MADE HERE AND REPEATED IN `RESULTS.md`: `Δ_FD` IS A PROXY, NOT A MEASUREMENT OF
> EITHER QUANTITY IT BOUNDS.** 0.2553 % is an agreement between an **adjoint** and a **finite
> difference** on a **gradient component**. Reusing it as a tolerance on a **design vector** and on
> an **objective** is a proxy. It is used because it is the only endpoint-noise figure measured on
> this case, and because sizing the unresolvable window from nothing would be worse. This is exactly
> the fallback the supervisor's brief authorised, and this is this lane saying so.

**The three cells, per channel; the pair takes the WORST channel:**
`d ≤ ε` → **SAME**;  `ε < d ≤ Δ_FD` → **UNRESOLVED**;  `d > Δ_FD` → **DIFFERENT**.

**The item's basin verdict, and its precedence, frozen before any start ran:**

| condition | basin verdict |
|---|---|
| any pair **DIFFERENT** | **`GATE FAIL`** on the same-optimum claim — measurably distinct optima. A falsification is a result. |
| else any pair **UNRESOLVED** | **`NOT A RESULT`** — the difference sits inside the FD-noise proxy; the instruments cannot tell *two optima* from *one optimum measured twice*. **This is the curriculum's own named failure mode, and it is registered as an outcome rather than left available as an excuse.** |
| else all pairs **SAME** | **`PASS`** — one optimum, to below this case's own measured noise floor |

**DIFFERENT dominates UNRESOLVED** because a DIFFERENT pair is *resolved* by the instrument, and a
falsified claim is not made unfalsified by a second pair the instrument cannot see.

**Members of the comparison:** D1 arm O (from its committed artifact, at zero compute) plus every
start whose own per-start verdict is `PASS`. A start that is not `PASS` **does not enter the basin
comparison** and its exclusion is printed. **Fewer than two graded starts beside D1 → the grader
refuses (exit 2); a basin claim from one pair is not a basin claim.**

## 5. LADDER / DECOMPOSITION

**`np = 1`, `numberOfSubdomains 1`, no decomposition, on every start.** Stated explicitly rather
than left blank: **with `np = 1` the parallel-determinism question does not arise**, so nothing in
this item's basin claim can be attributed to, or defended by, decomposition. `nProcs : 1` is read
back from each arm's own log and a different value refuses. There is no grid ladder here and
therefore **no Roache triple and no GCI is claimed** — `CLAUDE.md` rule 5 is not engaged, and this
file does not borrow its vocabulary.

## 6. PERTURBATION SEED — the start set, registered and regenerable

**Seed `13`.** Generator: `numpy 2.5.1`, `rng = numpy.random.default_rng(13)` (PCG64), then, in
this exact order:
`dshape = rng.uniform(-1.0e-2, +1.0e-2, size=(5, 8))` **drawn first**;
`daoa = rng.uniform(-1.0, +1.0, size=5)` **drawn second**.
Start *k* is `shape = dshape[k−1]`, `patchV = [10.0, 5.13918623195176 + daoa[k−1]]`.

**Registered magnitudes: `DELTA_SHAPE = 1.0e-2` (absolute, per mode), `DELTA_AOA = 1.0` degree.**
Bounded deliberately so the perturbed starts stay in the neighbourhood of the geometric constraint
set; the start's own constraint rows are **REPORTED, NOT GATED** — a start that begins outside the
feasible set is data, and IPOPT restoring feasibility is the behaviour under test, not a fault.

**THE LITERAL TABLE IN `d13_basin.py` §1 IS THE AUTHORITY**; the seed documents how it was made. A
start set whose identity depends on an RNG implementation detail is not a registered experiment.
The producer regenerates from the seed and **prints the deviation for the record**, and it **never
uses the regeneration to set a design variable**. `d13_basin.py starts` prints the five vectors.

Measured separation of the start set, computed before the freeze: pairwise `‖Δshape‖₂` between
starts **2.043e-02 … 3.443e-02**; distance from each start to D1's optimum **8.754e-02 … 9.780e-02**.
**The starts are separated by ~200–340× the `ε_shape` band they will be judged against.**

## 7. CRITERIA / GATES

**Per start**, in order. A start's verdict is the worst cell reached.

* **G0 — strict completion, all of it (`CLAUDE.md` rule 4), mapped onto an optimisation arm and the
  mapping registered rather than a clause silently dropped:** `rc = 0`; container
  `.State.ExitCode = 0` **and** `.State.OOMKilled = false` read **before** the container is removed;
  IPOPT's own `EXIT:` statement present **(the `End`-line analogue)**; majors **<** the registered
  `max_iter 40` cap **(the `last time == endTime` analogue — the run stopped on its own criterion,
  not on the cap)**; the endpoint JSON's **full key set asserted BY NAME (the fields-present
  analogue)**; the log's `.ok.<STAMP>` sentinel present; and the **AGE GUARD** — the endpoint JSON
  **newer than this arm's own `0/U`**, which the launcher touches last at staging so it dates the
  run allowed to produce the answer. **Any clause failing → `NOT A RESULT`.**
  Cold start (**G8**) is asserted **before** each launch: no `0.0001`, no `processor*`, no
  `reports/`, no stale `opt_IPOPT.txt` or `endpoint_d13.json`, `0/` populated. **This is the
  "restart discipline" half of D13**: five cold starts, no directory reuse, no primal state
  inherited between starts — which is what makes the basin comparison mean anything at all, given
  `A4/shipped_optimisation_np1/RESULTS.md` §3.2's measured finding that **the endpoint FD reference
  is a property of the optimisation path, not only of the design point.**
* **G1 — termination.** `EXIT: Optimal Solution Found.` with majors `< 40` → `PASS`.
  Majors `≥ 40`, a timeout, or the cost ceiling → **`GATE REACHED`** (or `NOT A RESULT` if G0 also
  fails). **A cap-stop is NEVER a `PASS`.** Any other exit → `GATE FAIL`.
* **G2 — feasibility.** `|CL − 0.5| ≤ 1.0e-5`; IPOPT's own `Constraint violation ≤ 1.0e-5`;
  **every** constraint row in bound (`thickcon ∈ [0.5−1e-6, 3.0+1e-6]`, `volcon ≥ 1.0−1e-6`,
  `rcon ≥ 0.8−1e-6`), printed per family, **never aggregated**. An **empty** constraint family
  refuses (exit 2).
* **G3 — the endpoint FD table.** `DAFOAM_CHARTER.md` §2, this family's bright line: *a DAFoam
  gradient is not a result until a finite-difference table stands beside it at a step proved to lie
  in the plateau.* **≥ 3 of the 4 named components** (`shape[6]`, `shape[1]`, `shape[5]`,
  `patchV[1]`) must **grade** — plateau (two-rung) agreement `≤ 10 %` **and** measured clearance
  `C = |fd|·2s/η ≥ 5`, which is the plateau proof — and every graded component must agree with the
  adjoint to **≤ 5 %** with **zero sign flips**. Steps are chosen inside the container by the frozen
  `d1_fd_endpoint.py` from `|J_adj|` and η **alone**; no FD value ever enters the choice of a step.
  **`graded` is RE-DERIVED by the gate from the raw numbers, and a disagreement with the producer's
  own boolean REFUSES** — an instrument that trusts its producer's verdict is not an instrument.
* **G4 — trivial baseline.** `shape[6]` at `1e-8`, a step A1's own roundoff branch is known to
  destroy. Recorded per start. The instrument must be able to fail.
* **G5 — planted-zero controls (`CLAUDE.md` rule 3), mandatory on every gate that reads a number.**
  `PLANT = 1.234e-03` into **every consumed channel** — `CD`, `shape`, `patchV`, `fd_adj`,
  `fd_value` — in a **copy of a REAL endpoint JSON, never a synthetic fixture**, read back through
  the **same** reader, source md5 asserted before and after, **refuse (exit 2)** unless every
  channel moved by exactly the plant. Plus **four controls that prove the refusal works**:
  * **negative control** — a deliberately blind reader must be REFUSED;
  * **EMPTY-SET control** — `fd = {}` handed to G3 must be REFUSED **by name**;
  * **SHORT-SET control** — only 1 of 4 components able to grade must be REFUSED **by count**;
  * **key-set control** — `CD` renamed to `CD_final` must be REFUSED **by name**, not raise
    `KeyError` (L-273; the exact defect that killed D1 arm C at 14 s of container time).

  **Why the two set-size controls exist, named here so the repair is on the record.** Last session
  the supervisor found that `curriculum_D3/d3_grade.py`'s G3+G4 returns **`PASS` at 0.0000 % with
  zero sign flips over an EMPTY COMPONENT SET**: a present-but-unparseable FD block yields
  `by_step[s] = []` with the key present, the refusal tests **key presence and never
  non-emptiness**, the plateau loop iterates zero times, and a plateau step is selected without one
  comparison. **A PARTIAL PLANT READS ON THE PAGE EXACTLY LIKE A COMPLETE ONE.** D13's G3 therefore
  **refuses on an EMPTY or SHORT component set explicitly, BY COUNT, WITH THE COUNT PRINTED**
  (marker `D13_G3_COMPONENT_COUNT`), and the two controls above prove it does.
  **L-302: an instrument that cannot say "I measured nothing" will report a number it did not
  measured.**
* **G6 — launch gate**, re-run as its own command immediately before **each** launch and read
  before the launch is issued: `free_cores = nproc − load1 ≥ 4` **and** `MemAvailable ≥ 12 GiB`.
  **No departure may be taken on any agent's authority.** No watcher process is started.
* **G7 — image identity.** In-process `IDWARP_SO_MD5` must read `85f59e87253e0a71a813f64ca6e4c425`
  and `nProcs : 1`. A mismatch refuses.

**Then the cross-start basin verdict of §4, against the frozen band.**

## 8. COST — AND THE PRICE MOVED

**The curriculum's registered figure is STRUCK, and restated, and here is why.**

> ~~**D13: ~350 core-min, $0.30**~~ — STRUCK 2026-08-25, before any D13 compute. The 350 was
> scaled from an **assumed per-major line-search cost**. D1 measured the truth on this exact
> problem: **7.000 core-min gross for 11 majors plus the whole endpoint FD suite**, `0.304×` its own
> 23.0 core-min estimate, **because IPOPT took a full primal step (`alpha_pr = 1.00e+00`, `ls = 1`)
> on all 11 majors and the line-search primals the estimate priced in were never bought.**

**Restated, on that measured anchor.** D1's own decomposition: `D1_DRIVER_WALL_S 278.04` s ÷ 11
majors = **25.28 s/major**; feasibility step + endpoint FD suite + startup = 361 − 278 = **83 s**.
A perturbed start must first restore feasibility, so more majors are expected than D1's 11.

| | value | derivation |
|---|---|---|
| predicted majors per start | **15** (point), band **[8, 40)** | D1's 11 from an unperturbed feasible start, plus restoration |
| predicted per start | **7.7 core-min** | `15 × 25.28 + 83 = 462` s ÷ 60, np = 1 |
| **predicted total, point** | **40.0 core-min** | 5 starts |
| **predicted total, band** | **≤ 80.0 core-min** | |
| **HARD CEILING / STOP THRESHOLD** | **100.0 core-min** | **an overrun STOPS the run; it does not get a new budget** (`CLAUDE.md` rule 12) |
| per-start ceiling | **25.0 core-min** | |
| per-start `timeout` | **2700 s** | D1 arm O's own, inherited |
| peak RSS ceiling | **2.0 GiB** (kernel cap `--memory=6g --memory-swap=6g`) | D1 measured 1.6964 GiB |

`$` **DERIVED, NOT MEASURED**: point **$0.0342**, ceiling **$0.0855**.
`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED.`
The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
Actual-versus-predicted lands as a row in **`docs/COST_CALIBRATION.md`** on completion, with waste
**separately named and never netted into the ratio** (§6 of that charter).

## 9. TOOLCHAIN AND THE FROZEN FILES — BY HASH

**Image, by hash and not by tag** (`DAFOAM_CHARTER.md` §11):
**`dafoam-idwarp-rot:v1` = `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`**.
The shipped image `dafoam/opt-packages:latest` = `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`
is **NOT RUN by this item** (§0).

**Frozen at this commit. The grading path is fixed here; `RESULTS.md` re-hashes each file against
this table and refuses on a mismatch.**

| file | md5 | role |
|---|---|---|
| `d13_basin.py` | **`e96d77ff53e356d67f54a4cc46338c0e`** | start table, bands, readers, G3 count gate, all five controls |
| `d13_opt_runScript.py` | **`bf6500c7ef89f7f5c8be02292e274181`** | producer |
| `d1_fd_endpoint.py` | **`7e454d2f1830a40086465d9b5c57a941`** | FD instrument — **byte-identical to D1's frozen file, imported unchanged** |
| `d13_grade.py` | **`f0b2ccfd0271d1301eec70df820d32e3`** | grader |
| `d13_run_arm.sh` | **`5f75787d48a7f217130d983dc65a95a9`** | arm launcher |
| `d13_preflight.sh` | **`4ae10df0cbe38b0c8d579772b45289c9`** | G6 launch gate |
| `d13_script.diff` | **`d60a598ebf969cd59b38d984525ed8b1`** | proof the producer differs from D1's by **exactly 3 hunks** |

**`CLAUDE.md` rule 6 is honoured, not worked around.** D1's producer
`curriculum_D2/d1_opt_runScript.py` (md5 `4c9811d16f344bc23136981cd6092d8f`) is **frozen and is not
edited**. `d13_opt_runScript.py` is a **separate file** derived from it with exactly three hunks —
the header block, `"d13_start"` added to the task guard tuple, and one new
`elif args.task == "d13_start":` branch. **Every line of the case setup, `daOptions`, `meshOptions`,
DV and constraint definition, IPOPT settings and the whole `_fd_suite` instrument is byte
identical.** `d13_script.diff` carries the proof and `RESULTS.md` asserts the hunk count.

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart/`, mode 0777 (L-251),
`base/` copied from D1's run root with its three registered md5s re-asserted:
`points.gz 38a486d29a540ecd1b06e006e66475e7`, `wingFFD.xyz 6ddf378b028d03d8a18270488bee1759`,
`runScript.py 0557da51f6f179f6de865144343c499f`. **`base/` is copied FROM and never run IN.**

## 10. WHAT THIS ITEM CANNOT CLAIM — registered in advance

1. **No toolchain-independent basin result** (§0). Patched row only.
2. **`Δ_FD` is a proxy** (§4), not a measurement of design-vector or objective noise.
3. **η was measured at the BASELINE design** (D1 arm E), not at any of these five endpoints. The
   registered mitigation is the **two-rung plateau test at each endpoint**; it is a mitigation, and
   this item does not upgrade it into a measurement of any endpoint's own noise floor.
4. **Five starts is five starts.** A `PASS` says these five perturbed starts, at these magnitudes,
   reached the same optimum. It says **nothing** about starts outside `±1.0e-2` in `shape` or
   `±1.0°` in AoA, and it is **not** a claim that the problem has one basin.
5. **No Roache triple, no GCI** (§5). No grid ladder was run and none is claimed.

---

*Ends. Frozen before any container started. Amendments below this line only, dated, never by
editing above.*
