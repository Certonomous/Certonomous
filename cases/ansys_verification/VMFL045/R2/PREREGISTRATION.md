# VMFL045-R2 — Oblique Shock Over an Inclined Ramp: PRE-REGISTRATION (re-run of run 1)

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or on
completion** (CLAUDE.md rules 7, 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The manual is
proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**NOT YET RUN. ZERO SOLVER EXECUTION OF ANY KIND FOR R2.** This file is frozen
**before any R2 solver starts** (CLAUDE.md rule 2). What HAS fired with zero solver
compute: the R2 comparator's `--selftest` (**45 checks, 0 failures**, no run tree
touched), identical in every check to run 1's because the grader is byte-identical
except its three path constants (§4).

**The condition, CHECKED and not asserted** (`VERIFICATION_CHARTER.md` §2b.1): at the
time this file is written, read with `date -u` in the same invocation,
**`verification/runs/ansys_verification/VMFL045/R2/` does not exist** — the R2 run tree
is absent, no `blockMesh`/`topoSet`/`rhoCentralFoam` has run for R2, and no mesh exists
for R2. **Run 1's tree at `verification/runs/ansys_verification/VMFL045/L1_90x76/` is
LEFT IN PLACE** — it is the evidentiary core of run 1's `NOT A RESULT` and is never
deleted; R2 runs in its own fresh directory and the run-1 tree is not touched.

**Launch authorisation comes from the `ansys-verification-supervisor`** after its own
freeze verification, and **no agent message is Sanaa's consent** (CLAUDE.md rule 9).
**R2 is NOT launched by the drafting lane; the supervisor unlocks compute personally.**

**Drafted 2026-08-25 by `ansys-lane-opus48` (Opus 4.8).** This is **VMFL045-R2, a new
rung and a re-run of run 1**, following this team's own VMFL001 R1→R2 precedent
(`VERIFICATION_CHARTER.md` §6): a new pre-registration and a new register row **citing
run 1, which is NOT removed, re-labelled or softened.** Run 1 is recorded `NOT A
RESULT` / tier `NOT HELD` in `cases/ansys_verification/VMFL045/RESULTS.md` and register
row #5.

---

## 0. Why R2 exists — run 1's finding, in one paragraph

Run 1 crashed on its first timestep: `FOAM FATAL IO ERROR: Entry 'e' not found in
dictionary "system/fvSolution/solvers"`. Root cause, reached independently by the first
lane, the run-and-grade lane and the supervisor: the frozen `thermophysicalProperties`
declares `energy sensibleInternalEnergy` (energy field **`e`**), but the frozen
`fvSolution`, cloned from the **inviscid** VMFL051, provided a solver named **`h`** and
no `e`. VMFL045 is **viscous** (μ = 1e-8, the manual's own value, p. 153), so
`rhoCentralFoam` entered its implicit viscous energy-diffusion corrector — a path
VMFL051's μ = 0 never touched — and aborted for want of an `e` entry. The proof is the
count of `smoothSolver: Solving for Ux` lines: VMFL051's entire run **0**, VMFL045
before death **1**. Full triage in `RESULTS.md` §2 and the first lane's `LANE_REPORT.md`.

## 1. THE ONE CHANGE, and why it is a WIDENING not an addition

**Exactly one thing changes from run 1: the `fvSolution` `solvers` energy key is
widened from `h` to the regex `"(h|e)"`.** The entry keeps its existing sensible
setup (`$U` — smoothSolver/GaussSeidel, tolerance 1e-10, tighter than U's 1e-9), so it
is a good solver for the energy variable; only the key it matches is widened.

The diff, verbatim (`case/system/fvSolution`):

```
-    h
+    "(h|e)"
```
plus a one-line comment update so the file's prose is not self-contradictory
(`// diffusive correctors U and h` → `// diffusive correctors U and the energy
variable`). **The only FUNCTIONAL change is the key.**

**Why a widening rather than adding a separate `e` entry** (supervisor's ruling,
adopting the first lane's recommendation over a bare add): a single key `"(h|e)"`
serves **whichever** energy variable the thermo selects, so the dictionary stops being
silently specific to the `energy` setting. A future case that switches between
`sensibleInternalEnergy` and `sensibleEnthalpy` cannot reopen this hole. This is the
L-221/L-222 shape — **fix the class, not the instance.** (The `h`-only entry was the
instance fix that would have left the hole open for the next viscous clone.)

## 2. EVERYTHING ELSE IS UNCHANGED FROM RUN 1 — listed so the freeze's evidentiary value carries over

The gate could not have been chosen to fit an answer, because it is **the same gate,
frozen before run 1, and run 1 produced no answer.** Each item below is byte-for-byte
or value-for-value identical to run 1's freeze (`PREREGISTRATION.md`, blob
`7a7f9d52…`), and R2 changes none of them:

| unchanged item | value (from run 1's freeze) |
|---|---|
| **Gate G-VMFL045** | at L3_360x304, **\|M_lab − 1.874\| / 1.874 ≤ 0.010 (1.0 %)**; inside ⇒ gate met, outside ⇒ `GATE FAIL` |
| **reference the gate is against** | the manual's printed target Mach **1.874** (Tables .45.1/.45.2, analytic oblique-shock, White 1994) |
| **exact-Mach diagnostic** (never the gate) | M₂_EXACT = **1.8749769576810524** (as-modelled velocity BC → M₁ = 2.501814636762496, γ = 1.4), band **0.5 %** |
| **T / ρ diagnostics** (never the gate) | 382.0 K / 2.277 kg/m³, band **1 %** each, printed against T₂/ρ₂ exact |
| **three mesh levels, r = 2 by construction** | L1_90x76 (6 840) / L2_180x152 (27 360) / L3_360x304 (109 440) |
| **endTime** | **7.0e−3 s at every level** (same physical time; 8.6 flow-throughs) |
| **solver** | OpenFOAM v2606 **`rhoCentralFoam`**, serial, Kurganov flux + vanLeer, `adjustTimeStep yes`, maxCo 0.4 |
| **gas** | γ = 1.4 (declared; no Cp in the manual), Cp = 1004.8565342807, R = 287.1018669373429 |
| **frozen sampling zones** | `gateZone` x∈[0.34,0.46], y∈[0.15325662851831645, 0.22549435995186401]; `gateZoneInner` δ=0.045 m — absolute coords, identical at every level (`case/system/topoSetDict` UNCHANGED) |
| **Roache quantity** | volume-average post-shock Mach `volAverage(Ma)` over `gateZone` at endTime; ratio 2.0, Fs 1.25 |
| **verdict order** | CLAUDE.md rule 5 in order: plateau (ptp of last 20 % ≤ **1.0e−3** in Mach) + inner-zone clause → triple `CONVERGING`? → PASS/GATE FAIL |
| **cost cap** | **48 core-min** (point estimate 20.4), serial, `timeout` per §9; overrun STOPS the run |
| **strict completion + two declared departures** | rule 4 with DEPARTURE 1 (adaptive-step last-time tolerance) and DEPARTURE 2 (transient ExecutionTime-count invariant), and C6 stricter age guard — all as run 1's §8 |

**Carried forward unchanged, and NOT softened:**

- **The Fluent-would-fail declaration.** This 1 % gate would **`GATE FAIL`** Ansys
  Fluent's own reported Mach (1.902, point-sampled, +1.494 %) and **pass** Ansys CFX's
  (1.871, −0.160 %). A lab value landing near Fluent's is a **`GATE FAIL`** and is
  **not narrated as agreement with Ansys.** This box has no Fluent and no CFX; nothing
  here is a statement about Ansys.
- **The expected observed order:** **p ≈ 1** (shock-capturing is first-order near the
  discontinuity). **p ≈ 2 would be SUSPICIOUS** and is reported as a finding, not as a
  reason to move any band.
- **§7's plateau mitigation** (the four measures against VMFL051's plateau failure:
  8.6 flow-throughs, per-level plateau clause as arbiter, tolerance 19× tighter than
  the gate, volume average) — unchanged.

## 3. The comparator, unchanged in every threshold, band, reference, plant and classifier

The R2 comparator is `grade_vmfl045_r2.py`. It is **byte-identical to run 1's
`grade_vmfl045.py` except three path constants** that retarget it at R2's own run tree
and its own file — verified by `diff`, only these three lines differ:

- `SELF_REL` → `cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py`
- `RUN_ROOT` → `verification/runs/ansys_verification/VMFL045/R2`
- `OUT_JSON` → `GRADING_VMFL045_R2.json`

**No threshold, band, reference value, plant constant or classifier is settable from
the command line, and none was changed.** `EPS_ABS`, `STAG_TOL`, `RATIO`, `FS`,
`TOL_GATE`, `PLATEAU_TOL_MA`, `ZONE_CONSISTENCY_TOL`, the reference literals and the
three planted-zero controls are the same module-level constants. `--selftest`: **45 ok,
0 FAIL** (run before this freeze, zero compute). `--verify-frozen <commit>` re-hashes
the file's own bytes against the committed R2 blob and refuses (exit 2) on any
mismatch, exactly as run 1's did.

## 4. THE PRE-FLIGHT SMOKE TEST — the generalisable fix, added to the R2 launcher

**This is the fix for the CLASS of failure run 1 exposed:** a comparator `--selftest`
proves the **grader**, not the **case**, so nothing in run 1's pre-compute checks
exercised the actual OpenFOAM solver dictionary set against the solver. `run_vmfl045_r2.sh`
adds, **before any graded level runs**, a smoke test that:

1. builds the **coarsest** mesh (L1, 90×76) and its `topoSet` zones in a **scratch
   directory made with `mktemp -d /tmp/…`, OUTSIDE `verification/runs/`**, so it never
   creates or touches a directory the age guard or the launcher's guard-1 depend on;
2. runs `rhoCentralFoam` for a handful of timesteps (`endTime 1e-7 s`, so a dictionary
   error fires on step 1 exactly as in run 1);
3. **aborts the entire run (`refuse`, exit 2)** if the smoke `rc ≠ 0`, copying the
   fatal log to `${RUN_ROOT}/smoke.log.rhoCentralFoam` and writing `SMOKE.txt`;
4. deletes the scratch directory on success.

Had this existed for run 1, it would have caught the missing `e` entry **in seconds,
in scratch**, before any graded compute. **Cost: a few core-seconds of overhead,
inside the 48 core-min cap** — it is not deducted from the per-level budget accounting,
which is identical to run 1's; `SMOKE.txt` records the smoke's own wall.

## 5. Cost (CLAUDE.md rule 12) — unchanged from run 1, plus a few core-seconds of smoke

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s / 60 |
| **point estimate** | **~20.4 core-min** (run 1's §9.1 estimate, unchanged: L1 ~15 s, L2 ~117 s, L3 ~937 s, + meshing/FO ~150 s) |
| **+ pre-flight smoke** | **a few core-seconds** (coarsest mesh, ~a handful of steps), recorded in `SMOKE.txt`, well inside the cap |
| **CEILING (enforced cap)** | **48 core-min**, `timeout` = cap × 60 (serial), overrun STOPS the run |
| dollars at point estimate | **$0.01745** (DERIVED, $0.0513/core-h, c7a.4xlarge, owner-stated — NOT measured, the box cannot read its own billing) |
| dollars at ceiling | **$0.04104** (DERIVED) |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; a blanket is not a per-item read (rule 9) |

At completion the team appends one calibration row to `docs/COST_CALIBRATION.md`
comparing the 20.4 core-min estimate against the measured actual, ratio, contention
named separately as waste, dollars derived. (Run 1's calibration row states the ratio
**undefined** — the run never executed.)

## 6. The grading path, frozen (VERIFICATION_CHARTER §2d)

The R2 case tree, comparator and launcher are committed **BEFORE this file**, at commit
**`3467dd25f9f2bc71021de5cf4ea76497105941ea`** ("VMFL045-R2: case inputs + comparator +
launcher — NO COMPUTE HAS RUN, pre-registration not yet frozen"), which precedes any R2
solver. At analysis time the grading path is re-hashed against the committed blob shas
below; R2 runs its own `--verify-frozen` against the freeze commit.

| what | path under `cases/ansys_verification/VMFL045/R2/` | committed blob sha |
|---|---|---|
| **comparator (THE GRADING PATH)** | `grade_vmfl045_r2.py` | **`a282f00d267119f55f3f6a39b69cb693309595e7`** |
| run script (with smoke test) | `run_vmfl045_r2.sh` | **`2da8a6d8fa47e1b7e68a45f5cdbf6f3d10cd00e0`** |
| **fvSolution (THE ONE CHANGE)** | `case/system/fvSolution` | **`9010f183560743b67467493c64d5e02d1e90d592`** |
| topoSetDict (unchanged frozen sampling rule) | `case/system/topoSetDict` | **`ffaeb57898a4db6b6b7465597aaa2bfaa6c0fb0b`** — byte-identical to run 1's frozen sampling rule (git dedups; same blob) |
| blockMeshDict template / controlDict template / fvSchemes / 0/* / constant/* | `case/…` | same content as run 1's frozen blobs (verified: `diff -rq` shows R2/case differs from run 1's frozen case ONLY in `fvSolution`) |

**Run outputs go to `verification/runs/ansys_verification/VMFL045/R2/<level>/`**, never
beside this prose. **The grading JSON is
`verification/runs/ansys_verification/VMFL045/R2/GRADING_VMFL045_R2.json`.**

## 7. What CANNOT be verified before the R2 freeze — stated plainly

Same five open items as run 1's §11 (the mesh builds; `topoSet` fills both zones;
the live `volFieldValue.dat`/`Ma` on disk; every level plateaus within 7.0e−3 s; the
observed order and shock position), **plus one now improved:** the smoke test will,
for the first time, exercise the solver dictionary set before the graded levels — so
run 1's failure mode is caught pre-compute rather than mid-run. Everything the smoke
does not cover (convergence, plateau, order, the gate value) remains a finding to be
measured, whatever it is.

## 8. Verdict vocabulary (rule 1)

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else. R2 makes **no claim about Ansys, about the manual's correctness beyond
run 1's recorded findings, about a γ the case does not fix, or about the domain the
manual left open.** Only a `PASS` is a credential; a `GATE FAIL` or `NOT A RESULT` is a
finding that is never removed, re-labelled or softened, and it cites run 1.

---

## AMENDMENT 1 (dated pre-compute amendment — CLAUDE.md rule 2) — 2026-08-25T02:20:06Z

**Version:** freeze v1.0 → **v1.1**. This amendment is appended at the foot; **lines
whose number changed above this section: 0.** No original text above is rewritten;
where a prior sentence is now inaccurate it is **struck and corrected here**, not
edited in place.

**Status:** STILL PRE-COMPUTE. **The condition, CHECKED and not asserted**
(`VERIFICATION_CHARTER.md` §2b.1): at the moment this amendment was written, read with
`date -u` in the **same shell invocation** as the append, **2026-08-25T02:20:06Z**,
`verification/runs/ansys_verification/VMFL045/R2/` **does not exist** — the R2 run
tree is ABSENT (verified with date -u in this same invocation), no `blockMesh`/`topoSet`/`rhoCentralFoam` has run for R2, and
no R2 solver is running. Run 1's tree at
`verification/runs/ansys_verification/VMFL045/L1_90x76/` is left in place, untouched.

**What changed, and only this:** one line of the R2 comparator
`grade_vmfl045_r2.py` — the `--verify-frozen` **success message** — plus the four
docstring usage lines. The success line previously printed the literal
`grade_vmfl045.py` (the run-1 filename) while `SELF_REL` and the file itself are
`grade_vmfl045_r2.py`; a freeze-verification sentence must not misname its own
subject. It now prints `os.path.basename(SELF_REL)`, so the name is **derived** from
the path constant and cannot go stale on a future retarget (fixed as a CLASS, not an
instance). The four docstring usage lines now name the real R2 file.

**This is the FOURTH path-related change in the R2 comparator** (`SELF_REL`,
`RUN_ROOT`, `OUT_JSON` were the first three). **Correction to §3 (and the summary at
the head, line 12):** the statements that the comparator is "byte-identical to run 1's
`grade_vmfl045.py` **except three path constants**" and that "**only these three lines
differ**" are hereby **STRUCK**. The correct statement is: the R2 comparator differs
from run 1's by **four path-related changes** — the three path constants above **and**
the `--verify-frozen` success message (now derived from `SELF_REL`, with the four
docstring usage lines corrected to match). No logic, no threshold and no numeric
constant differs.

**What did NOT move — asserted:** NO gate, band, level, `endTime`, solver, zone,
Roache quantity, plant constant, classifier, reference literal, cost cap or label is
changed by this amendment. `EPS_ABS`, `STAG_TOL`, `RATIO`, `FS`, `TOL_GATE`,
`PLATEAU_TOL_MA`, `ZONE_CONSISTENCY_TOL`, the reference literals and the three
planted-zero controls are untouched. The Fluent-would-fail declaration, the p≈1
expectation with p≈2 declared suspicious, the three grid levels, the 48-core-min cap
and every verdict-vocabulary rule stand exactly as frozen.

**New frozen grading path (supersedes the §6 table's comparator row only):**

| what | path | committed blob sha | commit |
|---|---|---|---|
| **comparator (THE GRADING PATH)** | `grade_vmfl045_r2.py` | **`382ff4975801c5911277fb463076d1a14dd813c6`** | `d52143aedb2c78956c33563fea1799664217154a` |

The run script, `fvSolution`, `topoSetDict` and all other case blobs in the §6 table
are **unchanged** and keep their frozen shas.

**Checks run at amendment time, zero solver compute:** `--selftest` → **45 ok, 0
FAIL**; `--verify-frozen HEAD` → **exit 0**, and its success line now names
`grade_vmfl045_r2.py` on both sides (defect fixed). The grading path is re-hashed
against blob `382ff4975801c5911277fb463076d1a14dd813c6` at analysis time.

**No launch is authorised by this amendment.** Compute remains locked pending the
supervisor's personal re-verification of the changed grading path (their check).
