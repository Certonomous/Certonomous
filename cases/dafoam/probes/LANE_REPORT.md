# LANE REPORT — the three curriculum capability probes D10, D11, D12

**Lane:** dafoam `lab-lane`. **Supervisor:** `dafoam-supervisor`. **Date:** 2026-08-25.
**This file is this lane's only channel upward** — lane→supervisor messaging is one-way
in this harness. **Nothing here was filed, sent, uploaded or posted** (`CLAUDE.md` rule 7).

---

## 0. Headline, in Sanaa's terms

**Cases run: 8. Gates fired: 3 of 3 capabilities REACHED. Core-hours burned: 0.0897
(5.3836 core-min), $0.004603 DERIVED — under half a cent.**

| probe | verdict | core-min |
|---|---|---|
| D10 thermal-objective reachability | **`NOT A RESULT`** | 0.4167 |
| **D10-P′** the plant re-buy | **`GATE REACHED`** | 0.4168 |
| D11 MRF/rotating-frame adjoint | **`NOT A RESULT`** | 0.7166 |
| D11-D′ the dictionary re-buy | **`NOT A RESULT`** | 0.8334 |
| D11-O′ the omega re-buy | **`NOT A RESULT`** | 0.7167 |
| **D11-F′** the CLI re-buy | **`GATE REACHED`** | 0.7501 |
| **D12 unsteady adjoint** (`DAPimpleFoam`) | **`GATE REACHED`** *(first attempt)* | 0.8500 |
| D12-E′ envelope second point | **`NOT A RESULT`** *(registered branch)* | 0.6833 |

**All three curriculum `PROBE FIRST` prerequisites are discharged.** No probe overran; no
`CAP_CORE_MIN` guard fired; total spend is **0.378×** of the 14.25 core-min predicted
across eight separate freezes.

---

## 1. What I actually did

Eight pre-registrations frozen on the 10-line form, **each committed before its own first
container**, each verified at launch in the same shell invocation by
`git cat-file -e HEAD:<prereg>` **plus** an md5 match of the launcher against its HEAD
blob. Commits: `c2913dcd` (D10, D11, D12) + before-first-compute Amendment 1 `c2ceab24`;
`25c735ff` (D10-P′, D11-D′); `a35ca242` (D11-O′); `57c4a516` (D11-F′); `612c3705`
(D12-E′). Records: `506f3946` (`C-69`) and this commit.

**Substrates.** D10/D11: a purpose-built 720-cell 2D channel (`blockMesh`, and for D11 a
`topoSet` MRF cell zone `rotor` of 144 cells), so cost is deterministic and the
capability question is image-level. D12: **the upstream DAFoam `Cylinder` tutorial**,
2,450 cells — which *is* the curriculum's D12 case — at two registered probe reductions
(5 steps instead of 300; cold start from `0_orig` instead of the tutorial's spin-up).

**Container discipline**, inherited from `curriculum_D2/d2_run_arm.sh`: `--user 0:0`
(L-251), per-invocation `STAMP` and `.ok` sentinel (L-252), `--memory == --memory-swap`
with `--oom-score-adj=500` and a per-stage `timeout`, and **no `--rm`**, so
`docker inspect .State.OOMKilled` survives — which is D12's own named failure mode. All
np=1, `numberOfSubdomains 1`; **with np=1 the parallel-determinism question does not
arise.** Stock image throughout, `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`.

Full artifact trail: eight `RESULTS.md` beside their pre-registrations; run roots and
`ledger.txt` under `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/`.

---

## 2. What I measured

**D10-P′ — thermal objective reaches the adjoint.** `HFX = 2.8462869283e+03`;
`d(HFX)/d(patchV) = [1.9771502962e+02, −3.7575031648e+01]`; **plant response
`2.056667e-02`** relative to a `+1.234 K` change on a `353.15 K` wall; clean copy
reproduces base to `0.000e+00`.

**D11-F′ — MRF cell-zone adjoint is non-zero AND FD-consistent.**
`TPIn(ω=30) = 1.1859858226e+00` vs `TPIn(ω=0) = 1.1836719785e+00`; **MRF-zone plant
response `1.954802e-03`**; `d(TPIn)/d(patchV) = [2.3058711101e-01, −1.3660119098e-04]`;
and the load-bearing one — **adjoint vs central FD with MRF ON, `h = 1.0e-3 m/s`:
`2.3058711101e-01` against `2.3058707170e-01`, relative error `1.704895e-07`** against a
`5.0e-2` band. **The curriculum's named failure mode — "MRF interface derivatives
silently zero" — did NOT occur.**

**D12 — unsteady adjoint returns a number.** Time-averaged `CD = 8.9903939104e-02`
(**not a physical drag coefficient** — cold start, 5 steps — and never to be quoted as
one); `d(obj)/d(shape) = [3.5023163495e-02, 2.8868992750e-02, 5.2337196550e-02,
−1.1622935280e-01]`; plant response `6.270133e-04`; `End` line present, `endTime` dir
`0.05` present, `rc = 0`, `OOMKilled false`.

**Two registered terminology/API corrections the curriculum should absorb:**
1. **MRF is a CELL-ZONE formulation in this build, not an interface.** There is no MRF
   interface object (`IOMRFZoneListDF`, `MRFZoneListDF`; `DAResidualSimpleFoam.C:39–40,
   :144 MRF_.DDt(U_), :183 makeRelative, :199 constrainPressure, :246
   correctBoundaryVelocity`). The mandatory plant therefore went on the zone's own
   rotational rate. An interface treatment would be AMI — a different capability, not
   probed.
2. **DAFoam reads a scalar `omega` in rad/s, NOT `rpm`** (`MRFZoneDF.C:217`), and its
   `MRFProperties` is a **single top-level `MRF { … }` sub-dictionary**, not OpenFOAM's
   named-zone list. Also: **DAFoam 5.0.0 ships no `DAInput` class for MRF**
   (`src/adjoint/DAInput/` enumerated), so rotational rate is **not available as a design
   variable** — D11's case must vary geometry, not speed.

---

## 3. Verdicts and cost

Verdicts as tabled in §0, all from the fixed vocabulary. **5.3836 core-min gross =
$0.004603 DERIVED, NOT MEASURED**, at $0.0513/core-h, c7a.4xlarge,
**reported-by-owner** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Gross and cleaned coincide: the longest single
container wall in the whole item is **39 s**, 92× below the 3600-s stall rule.
Calibration row **`C-69`**, committed `506f3946`.

**Waste, named separately per `COMPUTE_BUDGET_CHARTER.md` §6 and netted off nothing:
2.6834 core-min — 49.8 % of the entire spend — produced no graded quantity, and all of it
was this lane's own instrument defects.** Detail in §5.

---

## 4. The costings the probes were blocking

### D12 — `NEEDS COSTING`: **ANSWERED**

A **two-point measured wall fit**, from D12 (5 steps, 29 s) and D12-E′ (10 steps, 39 s)
on the same case with a byte-identical run script:

    wall(n) = 19.0 + 2.000 · n   seconds, per compute_totals invocation, np=1, 2,450 cells

Component anchors, from the base log — **the first this lab holds for an unsteady
adjoint**: primal **0.195 s/step**; unsteady adjoint **2.158 s/step**, i.e. **≈ 11× the
primal**; `dRdWTPC` assembly **≈ 3.92 s** at 317 colours; python/OpenMDAO/IDWarp startup
**≈ 7.7 s** per invocation.

At the tutorial's own 300-step window: **10.32 core-min per major**, ≈ **11.3** with one
line-search primal. With spin-up (≈ 4.0), the curriculum's required FD verification on
the time-averaged objective (≈ 7.8) and a `δ_repeat` measurement (≈ 2.9):

> **D12 ≈ 127.6 core-min (10 majors) to 240.5 core-min (20 majors) = $0.109–$0.206
> DERIVED**, at np=1 on the 2,450-cell tutorial mesh with a 300-step window.

**The curriculum's `~1,000–3,000 core-min, $0.9–2.6` is 4–23× HIGH for this mesh and
window.** The anchor is legitimate — same case, same mesh, same solver, same box, same
rank count; only the window length and the optimization loop are extrapolated, and the
window extrapolation rests on **two measured points**, not one.

**One caveat, and it is not small: the RAM envelope is UNRESOLVED, and D12's own prereg
must close it before committing to a 300-step window.** See §6.

### D11 — `UNPRICED until probe`: **still `UNPRICED`, and here is why**

The probe reached the capability but **cannot price the case, because the case does not
exist yet** — the curriculum defers D11's case selection to after the probe. The
substrate that ran is a 720-cell 2D channel with an MRF zone in a through-flow; the
candidates are a **ducted fan or swirl passage** — 3D, rotating walls, a different case
class. **`COMPUTE_BUDGET_CHARTER.md:375-395` and the curriculum's own §2 estimation rule
forbid inventing a price across case classes**, and the honest output is therefore
`UNPRICED`.

**What the probe DID deliver toward that costing — the lab's first anchor in the MRF case
class:** at 720 cells, np=1, MRF-active `DASimpleFoam` + Spalart-Allmaras — primal
**0.1167 core-min**, primal+adjoint **0.2000 core-min**, **adjoint increment ≈ 0.083
core-min**. D11's own pre-registration should buy a calibration run on its selected mesh
and scale from that, not from this.

**And a named blocker on the case selection itself:** a **300 rad/s** zone **STALLS** a
steady `DASimpleFoam` primal on a simple through-flow substrate — continuity plateauing
at `≈ 2.5e-4`, never reaching `primalMinResTol 1e-10`, then
`AnalysisError: Primal solution failed!`. It stalls; it does not diverge and it does not
NaN. **D11's case must therefore be either physically appropriate to a rotating frame
(zone bounded by rotating walls, as in the `UAV_Propeller` / `Rotor37` tutorials) or
unsteady.** A 30 rad/s zone in a through-flow converges; 300 does not.

---

## 5. What went wrong, plainly

**Half the spend was mine.** Four probes produced no graded quantity:

| probe | defect | core-min |
|---|---|---|
| D10 | plant on the **initial internal field** of `0/T` — a converged steady solve is independent of its initial guess **by construction**, so the refusal was guaranteed before the container started. `HFX` moved by **exactly `0.000000e+00`**; base, plant and clean agreed to the last digit | 0.4167 |
| D11 | `MRFProperties` in OpenFOAM's named-zone layout; DAFoam wants a single top-level `MRF` sub-dict — `FOAM FATAL IO ERROR: Entry 'MRF' not found` | 0.7166 |
| D11-D′ | 300 rad/s stalls the steady primal (§4) | 0.8334 |
| D11-O′ | `argparse` treats `-1.0e-3` as an **option flag** — its negative-number matcher accepts `-1` and `-0.001` but **not exponent notation** — so the negative FD half-step was never passed | 0.7167 |

**The most expensive single mistake was a TRIAGE failure, not a defect.** `fdm` exited
**2** while its four siblings exited **1**, in **all three** D11 attempts. `rc = 1` is
DAFoam's `AnalysisError`; `rc = 2` is `argparse`. I read that distinct exit code as part
of the same failure, so it survived two further re-buys and cost **1.5501 of the 2.6834
core-min**. **A distinct exit code beside a cluster of others is a distinct finding.**

**A second, smaller instrument defect, disclosed:** D12-E′'s pre-registration registers a
cap of **3.0** core-min and its launcher enforced **6.0**
(`d12e_stage_and_run.sh:33`, copied forward from D12's launcher; the substitution list
that rewrote every path and the `endTime` assertion did not include the cap, and no
assertion checked it). The run cost 0.6833, so **no verdict, number or gate is
affected** — but a cap that is not the cap you registered is not a cap. **I audited the
other seven launchers; their caps match their pre-registrations.** Same defect class as
`C-51` item (8), by a different route.

---

## 6. What I could NOT verify — read this before quoting anything above

1. **The D12 RAM envelope is UNRESOLVED, and I nearly published an alarm on it.** D12's
   single-point envelope extrapolates to `0.1065 GiB/step` and hence **≈ 32 GiB at a
   300-step window — above this 30 GiB box.** D12-E′ was registered to buy the second
   point with the fit frozen in advance and returned `per_step_GiB = −0.000262`:
   **negative**, firing its registered `NOT A RESULT` branch. ΔR is `0.532536 GiB` at 5
   steps and `0.531223` at 10 — **doubling the window did not measurably change resident
   memory**, so the rise is dominated by the fixed `dRdWTPC` term and **the 32 GiB alarm
   is NOT SUPPORTED**. But **"the envelope is flat" is NOT established either**: the
   1.3 MiB difference is below the run-to-run RSS noise scale (the two primal figures
   alone differ by 4.9 MiB), and with **one run per point that floor is unmeasured**. A
   non-positive slope means either `reduceIO: True` is not holding per-step state in RAM
   **or** the allocator is not returning it to `ru_maxrss`, and **I cannot tell those
   apart.** *Disk is settled and tiny: the adjoint adds `177,009 B ≈ 0.169 MiB` over 5
   steps.* **My D12 costing in §4 is a TIME costing and does not carry a memory
   clearance.** The arm that would close it — two window lengths an order apart (50 and
   100 steps) with repeats to measure the RSS noise floor, plus a `reduceIO: False` arm —
   is **proposed, not run, not costed as authorised.**
2. **No probe establishes correctness, accuracy or sign of any derivative.** D11-F′'s
   `1.70e-07` adjoint-vs-FD agreement is one component, one configuration, **30 rad/s**,
   720 cells. **Nothing here says anything about MRF at engineering rotational rates.**
3. **Contention is not zero and I did not measure it.** Peer lanes were live throughout
   (D8's A6 container, D13's arms; loadavg 9.19 on 16 cores at launch). A peer measured
   and committed the mechanism mid-session at `ab89210f` — `mpirun -np 1` in a container
   binds **every** rank to CPU 0, `--cpus=1` being a CFS **quota, not a placement**;
   4 containers at 0.2504 of a core on a 61 %-idle box, 0.9994 after correction, **3.99×
   for one token**. I applied `--bind-to none` by a **before-first-compute amendment**
   (`c2ceab24`; condition stated and checked — the run root did not exist), so the
   collision was avoided, **but no uncontended control was run and the residual is
   unmeasured.**
4. **D12's `obj` is not physics.** Cold start, 5 steps, no limit cycle. It is a number
   the adjoint differentiated, nothing more.
5. **The D10/D11 substrates are mine, not the curriculum's cases.** D10-P′ says a thermal
   objective reaches the adjoint **on this image**; it says nothing about the U-bend at
   scale, CHT coupling, or `DAHeatTransferFoam`.
6. **Lane wall is a FLOOR, not a value: ≥ 27 lane-min**, because `C-40`'s standing
   one-line fix — *a dispatched lane should `date -u` into a uniquely-named scratch file
   as its FIRST action* — **was again not applied**; my first clock read came after the
   reconnaissance and the case authoring.

---

## 7. For the supervisor — what I think needs your call

None of this is acted on by me; **proposing is not authorising** (`CLAUDE.md` rule 9).

1. **The finding with the longest reach, and it is a V&V finding, not a DAFoam one.**
   D11's frozen §4 mapped *"`MRFProperties` rejected → `BLOCKED` (capability absent from
   this build)"*. **The antecedent fired — for a reason the mapping did not contemplate**
   (my own dictionary defect). **Reporting `BLOCKED` would have been FALSE**: it would
   have told D11's costing that this box cannot do MRF adjoints, when the capability was
   never reached and therefore never shown absent. **`BLOCKED` requires reaching a
   capability and finding it gone.** I refused that verdict and re-bought instead, and
   every successor carries the distinction as a gate clause. **Generalised: a gate whose
   antecedent can be tripped by the instrument that tests it is not measuring what its
   label says.** This looks to me like a lesson for the whole lab, and whether it becomes
   one is above a lane.
2. **A launcher should assert its own `CAP_CORE_MIN` against the value its
   pre-registration names**, exactly as these launchers already assert the plant landing
   and `endTime`. Changing a family's launcher idiom is not a lane's call.
3. **The curriculum's D12 estimate is 4–23× high** and its D11 row needs the two
   corrections in §2 (cell-zone not interface; `omega` not `rpm`; no MRF `DAInput`).
   Amending a ratified document is yours.
4. **D11's case selection is now constrained by measurement** (§4) and should not be made
   without it.
5. **The four `NOT A RESULT` probes are on the record as this lane's own defects.** I have
   not softened any of them, and the 49.8 % waste figure is in `C-69` where a reader
   looking for the lab's estimate quality will find it.
