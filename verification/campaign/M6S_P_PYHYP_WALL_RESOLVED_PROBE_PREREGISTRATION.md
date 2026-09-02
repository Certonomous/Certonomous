# M6S-P — pyHyp wall-resolved feasibility probe, ONERA M6

**Label: FEASIBILITY PROBE. NO GATE, NO THRESHOLD, NO VERDICT of the fixed vocabulary
(`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`) attaches to
any number this probe produces, with the single exception of `BLOCKED` in §6, which describes
the probe's own inability to run and grades nothing about the M6.**

**It decides nothing about the ONERA M6 and commits the lab to no route.** It scores nothing,
counts toward no result column, enters no birth certificate, and supersedes, amends and reopens
nothing. In particular it does **not** touch `M6I` (`GATE FAIL` at R0), `F13` (`GATE FAIL` at
R0, case `BLOCKED`), or `F1`. Its entire purpose is to tell Sanaa **whether route option 3 is
possible at all**, before she chooses a direction. Nobody may later quote a verdict from this
document.

**FROZEN by the commit that lands this file.** Written 2026-09-02, **before any pyHyp
invocation under this registration** and before the mesh it registers exists on disk (§0.2
names the directories that do not exist). Team: cfd. v1.0.

---

## 0. PRE-FREEZE CHECKS

### 0.1 Register search before the freeze (L-427)

**Searched:** `docs/NUMERICS_KNOWLEDGE.md`, `docs/LESSONS.md`, `docs/standards/MESH_STANDARD.md`,
`docs/MESH_STANDARD.md` and `verification/campaign/` for `pyhyp`, `hyperbolic`, `marching level`,
`min quality`, `marchDist`, `grid ratio`, `first cell`, `achieved`.

**It returned, and each return changed something below:**

- **`docs/standards/MESH_STANDARD.md:14-19` and `docs/LESSONS.md:1826-1830`** (the born-clean
  companion rule in `L-40`'s block): the lab's **one registered born-broken mesh** is the
  **A3 vcoarse pyHyp M6** — *"23 negative-volume cells, aspect ratio 2.08e95, pyHyp tip
  collapse — the same generator pathology as TMR NACA 0012, now cross-geometry."* **That mesh is
  the 390-wing-face level of the very surface ladder option 3 would use, and it is what §5 turns
  into this probe's planted control.** The lab already owns a known-bad specimen; the control is
  therefore free and is not a synthetic.
- **`docs/standards/MESH_STANDARD.md:528-538`** (§9.2's read-back clause): *"Every cfd mesh
  ladder must record, per level, the ACTUAL VALUE of every grading and first-cell parameter its
  generator used — read back from the written dictionary or the built mesh, never from the
  parameter that was requested… **The requested value is the thing that lied. Only the returned
  value tells the truth.**"* **This is why §2 reading 3 exists and why the requested `s0` is
  registered as an input, never as a measurement.**
- **`docs/NUMERICS_KNOWLEDGE.md:698`**: pyHyp appears only inside a methodology-adoption note.
  **No `N-*` entry governs hyperbolic extrusion quality.** This probe does not create one.
- **`cases/dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md`**: the only direct measurement of
  pyHyp under **simultaneous** surface and wall refinement (NACA0012 pair) — max
  non-orthogonality **22.75° → 26.96°, +18.5 %**, max aspect ratio **97.87 → 167.50**, while
  every average metric improved. Its own closing note records that the proposed smoothing
  ablation was never run because *"pyHyp is not installed on the 4G host (`import pyhyp` →
  `ModuleNotFoundError`)"* — **still true on this box today, measured in §6.**
- **`verification/campaign/M6I_PREREGISTRATION.md`**: supplies the read-only discipline over
  `/home/ubuntu/certonomous-runs/` copied verbatim into §8, and the `ABSENT`-never-clean rule
  copied into §4.

**It returned nothing that pre-registers, gates or forbids this probe.**

### 0.2 The condition — no compute has occurred, checked by naming directories that do not exist

`test -e` at the moment of writing:

| path | state |
|---|---|
| `verification/runs/M6S_runs` | **ABSENT** |
| `verification/runs/M6S_runs/P_pyhyp_wall_resolved_probe` | **ABSENT** |
| `cases/M6S` | **ABSENT** |
| `verification/campaign/M6S_P_PYHYP_WALL_RESOLVED_PROBE_PREREGISTRATION.md` | **ABSENT** (this file, before its first write) |

**No pyHyp log, no grid and no mesh exists for `M6S`.**

---

## 1. WHY THIS PROBE EXISTS, AND WHAT IT ALONE CAN SETTLE

The ONERA M6 rebuild has three candidate routes. Option 1 (imported grid, `M6I`) is finished and
is **`GATE FAIL`** at 86–88° against `MESH_STANDARD.md` §3.1's hard 70° gate. Option 2
(snappyHexMesh) cannot produce a node-nested family. **Option 3 (pyHyp, wall-resolved) is the
only surviving route that can produce an exactly similar family**, because the surface ladder
already exists on disk and coarsens exactly ×4 per level. Verified on disk from the `Total Faces`
line of three independent pyHyp logs under `/home/ubuntu/certonomous-runs/` (read-only):

| level | wing faces | log |
|---|---|---|
| coarse | **390** | `A3-onera-m6-adjoint-vcoarse/logMeshGeneration.txt:6` |
| medium | **1,560** | `A3-onera-m6-adjoint-coarse/logMeshGeneration.txt:6` |
| fine | **6,240** | `A3-onera-m6-transonic/logMeshGeneration.txt:6` |

**The one thing that could kill option 3 outright, and it is cheap to test.** Every existing
pyHyp M6 mesh was extruded at `s0 = 1.0e-4` and sits at `y⁺ ≈ 33`. Wall-resolving needs roughly
**76× finer** first-cell spacing, which pushes the layer count from 64 to ~92. The risk, as put
by the cfd supervisor and recorded here as **the motivation, not as this lane's measurement**:
the worst face today sits **0.0072 m** off the wall at the **WING TIP**, which is marching layer
**15.5 of 64**; at the tighter spacing that same physical station sits at layer **42.8 of 92** —
nearly three times as many accumulated hyperbolic marching steps to reach the place that is
already worst.

**The two axes point in opposite directions and nobody has moved both on the M6.**
Surface refinement **alone**, on this geometry, moved max non-orthogonality 61.4938° → 61.1581°
— slightly **better** — and cured the 135.318° pathology at 390 faces. Wall refinement
**together with** surface refinement, on the only geometry where it has been measured
(NACA0012), moved it **+18.5 %**, which extrapolated would breach 70° in one level and reach
~86° in two — **the same place option 1 died.**

**pyHyp announces this class of failure itself, before any `checkMesh` and before any solver.**
It prints a **Min Quality** column per marching level. The 390-face mesh announced its own death
in that column, and the announcement is on disk:

> `A3-onera-m6-adjoint-vcoarse/logMeshGeneration.txt:19` —
> `2 0.0 2 5 0 0.175 1.00282 0.35806 -0.34602 0.214E-10 ...`
> **`Min Quality = -0.34602` at marching level 2**, falling to **`-1.00000`** with **negative
> `Min Volume`** at levels 3–9.

That is the same mesh `MESH_STANDARD.md:14-19` registers as born broken with 23 negative-volume
cells. **Two independent instruments — pyHyp's own march log and `checkMesh` — agree on that
specimen**, which is what makes it usable as this probe's control.

### 1.1 THE ASYMMETRY, STATED ON THE FACE OF THIS DOCUMENT

**This probe can kill option 3. It cannot clear it.**

- A **negative Min Quality** is decisive against the frozen parameter set: the coarse level is
  born broken and no `checkMesh` is needed to know it.
- A **positive Min Quality throughout** says only that the march did not self-destruct. **It
  says NOTHING about whether max non-orthogonality will clear 70°**, because pyHyp's Min Quality
  and OpenFOAM's non-orthogonality are **different instruments measuring different quantities**,
  and this probe **does not run `plot3dToFoam` and does not run `checkMesh`** (§3). Nobody may
  read a positive Min Quality as evidence that option 3 clears `MESH_STANDARD` §3.1.

---

## 2. THE READINGS — REGISTERED BEFORE THEY CAN BE READ OFF AN ANSWER

**The probe runs pyHyp ALONE, once, at the coarse ladder level: 1,560 wing faces,
`N = 93`, `s0 = 1.319e-06`, `marchDist = 12.0`, and EVERY OTHER OPTION BYTE-IDENTICAL to
`/home/ubuntu/dafoam-tutorials/Onera_M6_Wing/genWingMesh.py` as it stands** — `fileType CGNS`,
`unattachedEdgesAreSymmetry True`, `outerFaceBC farfield`, `autoConnect True`, `families wall`,
`ps0 -1.0`, `pGridRatio -1.0`, `cMax 0.1`, `epsE 1.0`, `epsI 2.0`, `theta 3.0`, `volCoef 0.25`,
`volBlend 0.0005`, `volSmoothIter 100`, `kspreltol 1e-4`. `N = 93` is pyHyp's node count and
gives **92 cell layers**, against the stock `N = 65` giving 64.

**Three parameters move from the stock file and no others: `N` 65 → 93, `s0` 1.0e-4 → 1.319e-06,
and the input surface is the 1,560-face coarsening rather than the 6,240-face fine surface.**
The smoothing parameters are deliberately **left at their stock values**, because the whole
question is what the stock recipe does at wall-resolved spacing — and because
`GENERATOR_FINDING_pyhyp_aspect_ratio.md` names exactly that unscaled smoothing as the
best-supported hypothesis for the refinement pathology. Scaling them would answer a different
question.

Every reading below is taken **from the probe's own log and grid**, never typed and never
inferred.

### Reading 1 — `Min Quality`, per marching level (table column 9)

**Read at EVERY level from 2 to 93, not only the last.** Reported as: the **minimum over all
levels**, the **level index at which it occurs**, and the full column retained in the log.
Read alongside it: **`Min Volume` (column 10)**, whose sign is the second instrument on the same
failure.

**What it means, fixed now:**

- **Any negative value ⇒ the mesh is BORN BROKEN at that level**, and the level index localises
  the failure inside the march. On the registered ladder geometry a failure at a low level is a
  **tip-collapse** signature (`MESH_STANDARD.md:14-19`); it is reported with its level index and
  is **not** averaged, smoothed or summarised away.
- **All values positive ⇒ the march completed without self-destructing, and NOTHING MORE**
  (§1.1). No claim about 70°, about `checkMesh`, or about option 3's admissibility follows.

### Reading 2 — achieved `Grid Ratio`, i.e. did the march actually close on `marchDist`

**Two readings, because the header line alone is a symptom and not the proof:**

- **(a)** the header `Grid Ratio:` value printed before the table;
- **(b)** the **last marching level's `March Distance` (column 12)** — the cumulative distance
  actually marched. **This is the authoritative reading.** Closure means it equals **`0.120E+02`
  = 12.0** at the printed precision.

**Why this reading is registered at all, and it is not hypothetical: pyHyp CLAMPS its grid ratio
at 4.0000 and DOES NOT ERROR.** Measured on disk, `A3-onera-m6-sweep-n8_10920/logMeshGeneration.txt`:
header `Grid Ratio:  4.0000` (line 13), and the last level's `March Distance` is **`0.546E+00`**
— **4.6 % of the requested 12.0**. That is exactly how the existing n8 mesh ended up with a
~0.6-chord farfield while its log printed a ratio and no error. **A silently under-marched grid
is a wrong answer that looks like a right one, and reading (a) alone would have missed it on
the one case where it mattered.**

### Reading 3 — achieved first-cell height

**Read (a) the level-2 `March Distance` — the cumulative distance after the first step, which is
the first cell height — and (b), if a grid is written, the read-back from the written grid.**

**The requested value is registered here as an INPUT and is never reported as a measurement**,
per `MESH_STANDARD.md` §9.2:528-538. The requested value is known to overshoot, and it does not
overshoot by a constant: measured on disk, both from a requested `s0 = 1.0e-4`,

| surface | achieved level-2 `March Distance` | miss | log |
|---|---|---|---|
| 1,560 faces | **`0.108E-03`** = 1.08e-04 m | **+8 %** | `A3-onera-m6-adjoint-coarse/…:19` |
| 6,240 faces | **`0.123E-03`** = 1.23e-04 m | **+23 %** | `A3-onera-m6-transonic/…:19` |

**The miss depends on the surface level, so no correction factor is applied and none is
registered.** The probe reports what it achieved. **No target, band or tolerance is registered
for this reading — it has no gate**; it exists so that a later route decision is taken against
the achieved `y⁺`, not the requested one.

### Reading 4 — pyHyp serial CPU time (table column 2, last level)

Read for the `docs/COST_CALIBRATION.md` row required by rule 12, and for no other purpose.

### There is no fifth reading

Anything else the log prints is retained but is **not** a registered reading and may not be
promoted into one after the fact.

---

## 3. WHAT THE PROBE DOES NOT DO

1. **It does not run `plot3dToFoam`.** No OpenFOAM mesh is produced.
2. **It does not run `checkMesh`.** **No non-orthogonality, skewness or aspect-ratio number
   exists in this probe's outputs, and none may be attributed to it.**
3. **It does not run a solver**, and produces no force, residual or `y⁺` field.
4. **It does not build the medium or fine ladder levels**, and says nothing about them.
5. **It does not modify `genWingMesh.py`, pyHyp, the container, or anything under
   `/home/ubuntu/dafoam-tutorials/` or `/home/ubuntu/certonomous-runs/`** (§8).

---

## 4. COMPLETION AND REFUSAL

### 4.1 What counts as the probe having run at all — all clauses, or it did not run

- pyHyp **exits `rc = 0`** (captured **inside** the detached wrapper, never around a `setsid`
  line, which returns 0 for every outcome);
- the grid file `hyp.writePlot3D` names **exists and is non-empty**;
- the log contains the header **`Grid Ratio:`** line;
- the log contains the **`Min Quality`** column header;
- the log contains **one table row for every marching level from 2 to 93 inclusive — 92 rows.**
  **A log that stops short is INCOMPLETE, not clean**: pyHyp can and does die mid-march, and a
  truncated table whose surviving rows are all positive is the single most misleading artifact
  this probe can produce.

**A run failing any clause is reported as incomplete and its readings are not used.** The reader
**refuses (exit 2) rather than degrade.**

### 4.2 Refusals

- **AN ABSENT LOG READS `ABSENT`. IT NEVER READS CLEAN.** The reader `test -e`s the log path and
  emits `ABSENT` — not silence, not a pass — and grades nothing.
- **The launcher REFUSES a pre-existing run root.** If
  `verification/runs/M6S_runs/P_pyhyp_wall_resolved_probe/` already exists, the probe does not
  run and does not overwrite. Every artifact read must be newer than the run root's own creation.
- **A reader that cannot see its planted control (§5) exits 2 and grades nothing.**

---

## 5. PLANTED CONTROLS — rule 3, one per reader, run BEFORE the probe

**A zero from a reader not shown able to see a non-zero is not evidence.** Both controls are
**real known-bad logs already on disk**, not synthetics, and both are read **read-only**.

### Control A — the Min Quality reader must catch a known-bad mesh

**Specimen:** `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-vcoarse/logMeshGeneration.txt`
— the 390-face M6, the lab's registered born-broken mesh (`MESH_STANDARD.md:14-19`, 23
negative-volume cells).

**The reader must return, before the probe runs:**

| quantity | required value |
|---|---|
| minimum `Min Quality` over all levels | **`-1.00000`** |
| the **first** negative `Min Quality`, and its level | **`-0.34602` at marching level 2** |
| minimum `Min Volume` | **negative** (`-0.330E-08`) |
| header `Grid Ratio:` | **`1.1674`** |
| level-2 `March Distance` | **`0.108E-03`** |

**If the reader returns a clean result on this file, it is broken and the probe is not read.**

### Control B — the march-closure reader must catch a silently clamped, under-marched grid

**Specimen:** `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n8_10920/logMeshGeneration.txt`.

**The reader must return:** header `Grid Ratio:` = **`4.0000`** (the clamp) **and** last-level
`March Distance` = **`0.546E+00`**, and must report the march as **NOT closed on 12.0**.
A reader that reports this grid as closed cannot see the failure mode reading 2 exists to catch.

### Control C — the completeness reader must catch a truncated table

The reader is run over Control A's file **with its trailing table rows removed**, and must
report **INCOMPLETE**, not clean. (Control A's file is read-only and is **copied** into the
probe's own run root before truncation; **nothing under `/home/ubuntu/certonomous-runs/` is
written, truncated or modified.**)

**A control that fails is a finding and stops the probe.** It is not repaired by loosening the
reading.

---

## 6. ACCESS RISK, DISCLOSED ON THE FACE OF THIS DOCUMENT

**pyHyp is not importable on this host, and the container that holds it is not reachable by this
lane. Both measured today, 2026-09-02, at the time of writing:**

| check | result |
|---|---|
| `python3 -c "import pyhyp"` on the host | **`ModuleNotFoundError: No module named 'pyhyp'`** |
| `docker images` | **`permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`** |

pyHyp lives only inside the docker image **`dafoam-idwarp-rot:v1`**. A previous lane found the
same docker-socket permission denial, and `GENERATOR_FINDING_pyhyp_aspect_ratio.md` records the
identical `ModuleNotFoundError` blocking its own proposed ablation.

**If the probe cannot run for this reason the honest label is `BLOCKED`** — the one place in
this document where a fixed-vocabulary word applies, and it grades the **probe's ability to
run**, never the M6 and never option 3.

**What would unblock it:** docker socket access for the executing account (group membership or
an equivalent grant). **That is a permission change and is Sanaa's alone; no agent message
authorises it and this document does not request it as an action** (CLAUDE.md rule 9).

**`BLOCKED` here is itself a finding worth having**, and it is the reason this probe is worth
running before the route is chosen: it would mean **option 3 cannot even be tested without an
escalation**, which is a material fact about a route being weighed against two others.

---

## 7. THE SECOND RISK, NAMED BUT NOT TESTED HERE

**Registered so it is on the record and so a successor does not rediscover it as a surprise.
This probe does NOT test it and produces no evidence about it.**

`plot3dToFoam` is **serial** and must hold the whole mesh in one process. The conversion chain
has **never been exercised above 399,360 cells on this box** — that is the
`A3-onera-m6-transonic` mesh (6,240 faces × 64 layers), and its `plot3dToFoam` invocation is
visible in `A3-onera-m6-sweep-n8_10920/logMeshGeneration.txt`. **Option 3's fine level is
~9.2 M cells — 23× larger — on a 30 GiB box.** The 9.2 M figure is the cfd supervisor's route
costing and is **carried here as stated, not measured by this lane.**

**There is no basis on this box from which to cost that conversion**, and none is invented here.
If option 3 survives this probe, the conversion feasibility is a **separate** registered
question with its own cost registration; a cap is not a ceiling that grows on its own (rule 9).

---

## 8. TERRITORY — WHAT THIS PROBE MAY TOUCH

- **pyHyp, the `dafoam-idwarp-rot:v1` image and `/home/ubuntu/dafoam-tutorials/` are the dafoam
  team's.** This probe **reads** `/home/ubuntu/dafoam-tutorials/Onera_M6_Wing/genWingMesh.py`
  as the byte-identical parameter source and **writes nothing** there. Its own driver script is
  a **copy** under the probe's run root.
- **`/home/ubuntu/certonomous-runs/` is READ-ONLY to this lane**, exactly as
  `M6I_PREREGISTRATION.md` §9 registers: *"NOTHING is written under
  `/home/ubuntu/certonomous-runs/`… It is read from and never written to, meshed into, pruned or
  repointed at."* The surface file `m6_surfaceMesh_fine.cgns` and the three
  `logMeshGeneration.txt` specimens are **copied out** before use.
- **Writes are confined to** `verification/runs/M6S_runs/P_pyhyp_wall_resolved_probe/`.

---

## 9. COST — rule 12

**Unit: core-minutes. Dollars are DERIVED at the recorded c7a.4xlarge rate of $0.0513/core-h and
are labelled derived-not-measured; the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). This is reported-by-owner, never measured.**

### 9.1 Basis — MEASURED ON THIS BOX, ON THIS GEOMETRY, AT THIS SURFACE DENSITY

pyHyp's own cumulative serial CPU time at the last marching level, read from column 2 of
`logMeshGeneration.txt` in five run directories under `/home/ubuntu/certonomous-runs/`
(read-only), all at **1,560 wing faces**:

| `N` (nodes) | cell layers | last-level CPU s | run dir |
|---|---|---|---|
| 8 | 7 | **1.1** | `A3-onera-m6-sweep-n8_10920` |
| 15 | 14 | **6.4** | `A3-onera-m6-sweep-n15_21840` |
| 28 | 27 | **5.6** | `A3-onera-m6-sweep-n28_42120` |
| 52 | 51 | **5.4** | `A3-onera-m6-adjoint-probe80k` |
| 65 | 64 | **5.3** | `A3-onera-m6-adjoint-coarse` |

> **Cost is nearly INDEPENDENT of layer count — 5.3–6.4 s across 14 to 64 layers — and is
> driven by SURFACE density instead: the same `N = 65` recipe costs 81.7 s at 6,240 faces
> (`A3-onera-m6-transonic`), 15× more for 4× the faces.** The probe holds the surface at 1,560
> faces and raises only the layer count, which is the cheap axis. **~93 nodes at this surface
> density is therefore the same order: ≈ 6 s serial.**

**Disclosure, not absorbed into the estimate:** all five basis figures were recorded at
`s0 = 1.0e-4`, **not** at the probe's 1.319e-06. Tighter initial spacing can change the
sub-iteration and KSP counts the log also prints, so the basis constrains the **order**, not the
digit. **The cap below carries that uncertainty explicitly rather than silently.**

### 9.2 Estimate and cap

| item | value |
|---|---|
| **estimate** | **0.11 core-min** (≈ 6.4 s × 1 rank ÷ 60), **$0.0001 derived** |
| **CAP** | **15.0 core-min**, **$0.013 derived** |

**The cap is enforced STRUCTURALLY, not by intention:** pyHyp is invoked serially under
`timeout 900`, so **1 rank × 900 s ÷ 60 = 15.0 core-min is the worst the launcher can spend.**
That is ~140× the measured basis — generous against a basis recorded at a different `s0`, and
still trivial in absolute terms.

**AN OVERRUN STOPS THE RUN. It does not get a new budget.** A timeout kills the probe, the
result is reported as incomplete under §4.1, and **the cap is not raised** — a re-run at a
larger cap would be a new registration. Well under the pre-authorised $25 blanket; **a blanket
is not a per-item reading** (rule 9), which is why the figure is registered here rather than
assumed.

### 9.3 Calibration — rule 12's estimate-versus-actual

At completion the actual core-minutes are read from reading 4, the ratio actual/predicted is
stated, the gap is attributed (contention / waste / misprediction, **waste named separately and
never absorbed**), and **a row is filed to `docs/COST_CALIBRATION.md`** under that file's append
rules and the rule-10 private-index protocol. **A completion report without that comparison is
incomplete.**

---

## 10. FROZEN PATHS

- parameter source, **read-only**: `/home/ubuntu/dafoam-tutorials/Onera_M6_Wing/genWingMesh.py`
- surface input, **read-only, copied out before use**:
  `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/surfaceMesh.cgns` (1,560 faces),
  derived from `m6_surfaceMesh_fine.cgns` by the `cgns_utils coarsen` ×4 sequence
  390 → 1,560 → 6,240
- control specimens, **read-only, copied out before use**:
  `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-vcoarse/logMeshGeneration.txt` (Control A,
  Control C) and `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n8_10920/logMeshGeneration.txt`
  (Control B)
- run root, **the only place this probe writes**:
  `verification/runs/M6S_runs/P_pyhyp_wall_resolved_probe/`
- **the extruded grid is NOT committed to git** — it is named, not hidden: at 1,560 faces × 92
  layers it is ~12 MB by scaling from the 964,805-byte n8 grid. **The log and the readings are
  the committed artifacts**; the grid is retained on disk beside them and its path is recorded
  in the readings.

---

## 11. WHAT THIS REGISTRATION DOES NOT CLAIM

1. **It does not claim option 3 is viable.** §1.1: this probe can kill option 3 and cannot clear
   it.
2. **It does not claim option 3 will clear `MESH_STANDARD` §3.1's 70° gate.** It produces no
   `checkMesh` number at all (§3).
3. **It does not claim the probe will run.** §6 records a measured import failure and a measured
   docker permission denial; **`BLOCKED` is a live outcome.**
4. **It does not claim the ~9.2 M conversion is possible.** §7 names that risk and tests none of
   it.
5. **It does not recommend a route.** The route choice is Sanaa's, and this document exists to
   put one fact in front of it, not to make it.
6. **It does not reopen `M6I`, `F13` or `F1`**, and no number produced under it may be cited
   against their verdicts.
