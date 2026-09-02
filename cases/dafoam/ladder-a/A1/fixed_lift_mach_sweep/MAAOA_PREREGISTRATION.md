# MAAOA — FIXED-LIFT (Ma, AoA) SWEEP ON THE WALL-RESOLVED FINE MESH, BOTH ARMS — PRE-REGISTRATION

**Item:** `MAAOA` — NACA0012, A1WR mesh family level **L3** (130,304 cells,
wall-resolved), each operating point **trimmed to fixed lift**, incompressible
(`DASimpleFoam`) control + compressible (`DARhoSimpleFoam`) Mach axis.
**Team:** dafoam **Lane:** lab-lane (this order) **Written:** 2026-09-02
**Status at freeze: NO COMPUTE HAS BEEN SPENT ON THIS ITEM.** Checked, not
asserted: `/home/ubuntu/certonomous-runs/MAAOA` **does not exist**.
**Verdict class:** `FEASIBILITY`. **Verdict ceiling:** `GATE REACHED` — this
mesh family's grid convergence is PENDING (A1WR §1.3), so no value from this
item may be graded `PASS` against a physics band.

## 0. THE ORDER, VERBATIM, AND THE REGISTERED READING OF "LIFT MUST BE KEPT FIXED"

Sanaa, 2026-09-02 ~19:00Z (`etc/sessions/2026-09-02T1900Z_sanaa_fine_sweeps_launch_order.md`):

> Once that is launched, DAFOAM launches (Ma,AoA) sweep for both with fine as
> well. These runs must either be launched or queued, such that even if the
> fleet dies, they still run. … They need to run in parallel … Also, for all
> of these cases, lift must be kept fixed.

and her ~19:40Z addendum: fine mesh; **the PATCHED build** (parallelization
transpose fix); immediate.

**REGISTERED READING of "lift must be kept fixed" (the chief's interpretation,
being confirmed with Sanaa; her correction lands as a PRE-COMPUTE AMENDMENT to
this document):** at every operating point of this item the wing is **TRIMMED
in angle of attack to the lab's fixed lift target CL = 0.5** (the D19-family
target, `CL_target = 0.5` in every D19/A1 run script), so the Mach sweep
reports the **trim angle α(Ma)** and the **drag at fixed lift CD(Ma; CL = 0.5)**.
A free two-axis (Ma × AoA) grid with lift *also* fixed would be
overdetermined: fixing CL **consumes** the AoA axis — AoA becomes the trim
variable, which is exactly how the (Ma, AoA) pair remains meaningful under her
constraint. **"For both" = both solver arms**, with the **incompressible arm
running its fixed-lift trim at its single regime (U0 = 10 m/s) as the
control** — a Mach sweep is physically meaningful only in the compressible
arm, and **no incompressible Mach axis is fabricated**; that would be a
made-up number wearing an axis.

## 1. WHAT RUNS

Seven operating points, **each cold, each its own case directory, each np = 1,
all in parallel** (her explicit parallel order — trim points are independent,
so parallelism costs nothing here, unlike A1WR's continued sweeps):

| point | arm | solver | U0 (m/s) | M = U0/347.1904 | α0 guess | justification from the ladder's records |
|---|---|---|---|---|---|---|
| `MA288` | C | DARhoSimpleFoam | 100.0 | 0.2880 | 4.0 | **the D19-family operating point** — D19M/D19R/D19O and the coarse AOAC sweep all ran U0 = 100; the anchor every compressible number in this family already stands on |
| `MA400` | C | DARhoSimpleFoam | 138.8762 | 0.4000 | 4.0 | bridge, registered to resolve where compressibility begins to move CD at fixed lift between the two record-anchored regimes |
| `MA500` | C | DARhoSimpleFoam | 173.5952 | 0.5000 | 4.0 | bridge, same purpose |
| `MA600` | C | DARhoSimpleFoam | 208.3142 | 0.6000 | 3.0 | bridge; approaching the regime D16 reached |
| `MA650` | C | DARhoSimpleFoam | 225.6738 | 0.6500 | 3.0 | refinement point below D16's Mach — where steady-solver behaviour is expected to start degrading at CL = 0.5 |
| `MA685` | C | DARhoSimpleFoam | 237.8254 | 0.6850 | 2.0 | **D16's operating point** (`curriculum_D16/RESULTS.md`: M 0.685). **Honest caveat, registered:** D16 ran `DARhoSimpleCFoam`, the transonic variant. This sweep holds ONE frozen solver across its axis (changing solver with Mach would confound the axis), so `MA685` runs `DARhoSimpleFoam` beyond that solver's recorded envelope — **a failure to converge there is a REGISTERED OUTCOME and a finding about the steady subsonic formulation, never retried and never re-solvered inside this item.** A `DARhoSimpleCFoam` arm is a successor rung, not this one. |
| `INCOMP` | I | DASimpleFoam | 10.0 | n/a | 4.0 | the fixed-lift control at the incompressible regime — the coarse AOAI/A1 operating point |

a = √(γRT) with the **READ** constants (A1WR amendment 1): γ = 1.4
(`perfectGas`), R = 8314.47/28.97 = 287.0028, T0 = 300 K → **347.1904 m/s**.
The mesh is **A1WR L3 exactly as built** (Stage-0 record), **contingent on the
A1WR Stage-1 y+ probe** — §3.

**Trim mechanism, frozen:** DAFoam's own Newton trim,
`OptFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"],
targets=[0.5], designVarsComp=[1])`, `maxIter = 10`, `tol = 1e-4` (the shipped
defaults, named rather than recalled) — the same call every D19-family
`run_driver` uses before optimisation. Primal numerics frozen as A1WR Stage 2:
`primalMinResTol 1.0e-8`, endTime cap 4000, SA, `useWallFunction: False`
(wall-resolved), **PATCHED image `dafoam-idwarp-rot:v1`
(`sha256:2927768a16ac…f6d35`)** per her order, `OMP_NUM_THREADS=1`. **No point
is retried, relaxed, re-tuned or dropped**; a trim that raises is recorded
with its exception and reported.

**y+ is measured on every point** (DAFoam's per-print `yPlus min/max/mean`
line, last in the log, ≤ printInterval = 100 iterations stale — the channel
A1WR Addendum C §15.4 registers, with the same G-YPLUS rule). Predicted y+max
at `MA685` ~0.4–0.5 (Re scaling from the 0.203 prediction at M 0.288) —
**EXTRAPOLATED, a prediction, not evidence.**

## 2. WHAT THIS ITEM MAY CONCLUDE, AND WHAT IT MAY NOT

It reports α(Ma) and CD(Ma) at fixed CL = 0.5, trim quality |CL − 0.5|,
convergence classification and measured y+ per point. **It may NOT report:** a
drag-divergence Mach number (`G-MDD` refuses at exit 2, mirror of `G-STALL`),
a stall angle, any grid-converged value or band (`G-NOBAND` — no Roache triple
exists on this family), or any claim about `DARhoSimpleCFoam` (not run here).
Registered outcomes: (A) all seven points trim and converge — the fixed-lift
drag axis exists on this mesh; (B) high-Mach points fail to trim/converge —
the steady subsonic formulation's boundary in Mach at fixed lift, a finding,
never a physics inference; (C) `G-YPLUS` fails at high Mach — the
wall-resolved claim is withdrawn for those points, mesh NOT re-cut.

## 3. THE DEPENDENCY — ENCODED IN THE CHAIN, NOT IN AGENT HANDS

`maaoa_chain_driver.sh` launches **no solver** until
`/home/ubuntu/certonomous-runs/A1WR/STAGE12/stage1_gate.json` exists and reads
`"verdict": "PASS"` (poll 60 s, bound 43,200 s). On upstream `GATE FAIL` or
`REFUSED` it exits **`BLOCKED`**, nothing launched, spend 0.0 — because "fine
grid" means *the level the y+ probe validates*, and if the probe withdraws the
wall-resolved claim this item's premise is gone. The wait, the gate read and
the launches all live inside one detached OS process started by the queue
daemon: **fleet death does not touch them.**

## 4. GATES

| gate | rule |
|---|---|
| `G-GATEDEP` | no solver before the A1WR stage-1 gate reads PASS; upstream fail ⇒ `BLOCKED`, spend 0 |
| `G-FREEZE` | instruments must match `MAAOA_MD5.txt` at launch (driver, exit 4) |
| `G-IMG` | the PATCHED image by id, `2927768a16ac…` (driver, exit 4) |
| `G-TRIM` | \|CL − 0.5\| ≤ 1.0e-3 ⇒ `TRIMMED`; else `NOT TRIMMED` and that point's CD **is not a fixed-lift drag** — reported as such, never quoted on the axis |
| `G-YPLUS` | y+max ≥ 1.0 on any point ⇒ `GATE FAIL` there, wall-resolved claim withdrawn (mesh not re-cut); blind/all-zero channel ⇒ refuse exit 2 (rule 3) |
| `G-WALLTREAT` | every point log carries `BCType=nutLowReWallFunction` and never the Spalding line; else exit 2 |
| `G-STALL` / `G-MDD` | no stall angle; no drag-divergence Mach — reader refuses at exit 2 on its own output, plants driven |
| `G-CAPS` | per-point deadline 7,200 s **inside the container** (= 120 core-min at np 1); item cap 900 core-min enforced prospectively by the driver (a point is **not launched** if spend + 120 could breach it) — a cap-stop is `NOT A RESULT` on that point |
| `G-NOBAND` | nothing grid-converged, nothing in a band; ceiling `GATE REACHED` |

**Planted controls:** reader selftest M1–M5 (parse/flip/blind/y+ plant/claim
plants), every mutation asserted to land, **driven PASS before this freeze**;
the driver's G-ROOT/G-SRC/G-FREEZE/G-IMG refusal branches are the same
patterns A1WR's driver carries.

## 5. COST — REGISTERED BEFORE COMPUTE

Anchors **MEASURED** (A1WR §7.2/§13.2): 0.37163 s/iter compressible, 0.35625
s/iter incompressible at 130,304 cells, np 1. Trim primal count
**EXTRAPOLATED** (named as the term most likely to be wrong): first cold
primal ~2,500 iterations + up to 9 warm Newton primals ~600 each ⇒ ~7,900
iterations ≈ **45 core-min per point**; 7 points ≈ **315 core-min
estimate**. **Caps: 120 core-min per point (in-container deadline), 900
core-min item ceiling.** Derived dollars at the recorded rate (c7a.4xlarge
$0.0513/core-h, **owner-stated, reported-by-owner, NOT measured** — the box
cannot read its own billing): 900 core-min = 15.0 core-h = **$0.77 derived,
not measured** — under the pre-authorisation, and costed anyway because a
proposal with no cost is disqualified (rule 12). Estimate-vs-actual
calibration row **OWED** to `docs/COST_CALIBRATION.md` at completion,
contention attributed separately (the box carries A1WR Stage 2 and Sanaa's
filming while this runs — disclosed now).

**Layout:** pool of SIX one-core cpusets **{2–7}** (A1WR holds 8–15; **cores
0–1 carry no pin from either item — the filming headroom**); containers 3 GiB
hard cap; **MemAvailable floor 6.0 GiB before every launch**, so this item
self-staggers behind A1WR's 8-unit peak hour instead of overcommitting the
measured-30-GiB box; scheduler bound 24 h, running out of patience is an
error, not a pass.

## 6. FREEZE

Gates, thresholds, caps and label above are committed **before any compute on
this item**. Instruments frozen by the commit landing this document, md5s in
`MAAOA_MD5.txt` (enforced at launch): `maaoa_runScript_comp.py` (derived from
frozen `a1wr_runScript_comp.py` `fe0135fb…` — sole physics departure: U0 from
`MAAOA_U0`; + the trim task), `maaoa_runScript_incomp.py` (from
`623013b7…`; + the trim task), `maaoa_cmd.sh`, `maaoa_chain_driver.sh`,
`maaoa_read.py`. The queue entry cites this document's commit; the driver
hash-checks the instruments against the manifest before anything runs.

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---
---

# AMENDMENT 1 — 2026-09-02 — PRE-COMPUTE — DRIVER RE-PIN AFTER THE STAGING-GLOB REPAIR

**`lines whose number changed above this section: 0`**

**Condition: no compute has been spent on this item — checked, not asserted.**
The first fire's driver (daemon launch 18:10:20Z) reached only its
**gate-wait loop**: `MAAOA_WAIT_BEGIN` is the last line of its
`launcher.queue.out`, `/home/ubuntu/certonomous-runs/MAAOA` **does not
exist**, no container was created and no solver ran. Spend: 0.0 core-min.
The freeze window is therefore open and this amendment is legal under rule 2.

**What moves, and why:** `maaoa_chain_driver.sh` carried the same staging
defect A1WR ADDENDUM D records — the stale-time-dir cleanup glob `[0-9]*`
matches `0.orig` (it starts with a digit) and would have deleted it from
every staged point, aborting each on its own `test -d 0.orig`. Repaired with
`case "$d" in 0.orig) continue ;; esac`, proven on a planted fixture
(`0.orig 0 1000 0.0001` → only `0.orig` survives). The waiting driver was
terminated (`launcher_rc=143`, an infrastructure record, L-342) and the
entry re-armed. **Driver md5 re-pinned: `fdf184ecf0cde5df59c219b7a23d72a1`**
(§6's pin superseded). `MAAOA_MD5.txt` is unchanged — the driver is
deliberately outside it, exactly so the runtime G-FREEZE check cannot be
satisfied by the file that performs it. **No gate, threshold, cap or label
moves; the registered points, reading, costs and caps stand.**

---
---

# AMENDMENT 2 — 2026-09-02 — PRE-COMPUTE — RUN-SCRIPT RE-PINS AFTER A1WR's SECOND-FIRE FINDINGS

**`lines whose number changed above this section: 0`**

**Condition: still no compute on this item — checked.** The second fire's
driver reached the gate wait, read A1WR's `REFUSED` verdict and took its
registered `BLOCKED` branch: `STATUS.MAAOA_chain` reads
`phase=BLOCKED-BY-A1WR-GATE … spend_core_min=0.0`;
`/home/ubuntu/certonomous-runs/MAAOA` still does not exist. The freeze
window remains open.

**What moves** (both defects found by A1WR's probes, disclosed in its
ADDENDUM E, repaired identically here): (1) all MAAOA run scripts gain
`"checkMeshThreshold"` with **only `maxAspectRatio` raised to 5.0e5** (the
other three keys at the shipped defaults) — without it DAFoam's internal
mesh gate refuses the wall-resolved family's dispositioned single-cell-span
aspect ratio and no point can run; (2) the compressible script's physics
self-assert split literals now name `A1WR_PHYSICS`, and the repaired script
was driven in the PATCHED image against a scratch case on the real L3 mesh
to its task dispatcher (`AOAC_PHYSICS_MD5_PASS`, model built, no solve).
**Re-pins:** `maaoa_runScript_incomp.py` → `944dc9e0f9e396b79977b19a352ea429`,
`maaoa_runScript_comp.py` → `bd22df020be42fbd2eef14cbc25182f7` (block md5
`cc2e3aba1861bcf17a09965e03cc956b`), `MAAOA_MD5.txt` regenerated, `md5sum -c`
clean. **No gate, threshold, cap or label of this item moves.**
