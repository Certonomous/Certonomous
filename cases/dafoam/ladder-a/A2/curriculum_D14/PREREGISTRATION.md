# CURRICULUM D14-M — pyHyp MESH REGENERATION OF THE MACH WING (D4's MESH), WITH THE GENERATOR'S ASPECT-RATIO FINDING AS A NAMED CONTAMINANT WHOSE CHECK RUNS FIRST — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-26**. Lane: dafoam `lab-lane` (Q2). Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).
Curriculum row: `cases/dafoam/EXPERTISE_CURRICULUM.md:125` (D14 — *mesh-regeneration interaction*). Permission for the detached launch: Sanaa's own words at **`bc0e687e`**; queue-first order `7def3c6b` / `0b041d1a`.

---

## 0. SCOPE — THE FIRST RUNG OF D14, CUT SO IT RUNS TONIGHT

The curriculum row is *"pyHyp re-mesh at D4's optimum, re-verify gradient, re-optimize"* at ~1,000–1,500 core-min. **This document registers ONLY its first rung, D14-M: regenerate D4's baseline MACH-wing mesh with D4's own generator, inside the SHIPPED image, and grade the regenerated mesh against D4's baseline `checkMesh` record and `MESH_STANDARD.md`.** It answers the question every later rung of D14 presupposes and nobody has measured: **does this lab's pyHyp toolchain reproduce D4's mesh, and does the generator finding contaminate it?** It also produces the first measured pyHyp timing anchor for this wing (the uncommitted draft `PREREGISTRATION_DRAFT.md` in this directory, another lane's, records that none exists; that draft is the successor rungs' draft and is neither frozen nor superseded by this document). The re-mesh at the optimum, the gradient re-verification and the re-optimisation are **a later registration** that will cite this rung's measured numbers as its anchors.

**Capability-grid cell (Sanaa's taxonomy, `068c2bf0`):** D4's case is **3D · steady · subsonic-compressible** — `DARhoSimpleFoam` at `U0 = 100 m/s`, `T0 = 300 K` (`/home/ubuntu/certonomous-runs/A2-mach-wing/runScript.py:28-39`; `a = √(1.4·287·300) ≈ 347 m/s`, Mach ≈ 0.29). **D14-M DEEPENS that cell and MOVES NO gradient verdict**: it computes no gradient and runs no optimiser; what it can retire is the cell's *"single mesh only"* caveat's premise, by measuring whether the mesh is reproducible by its own generator, and what it can add is the *"generator finding contaminates the re-mesh"* caveat if G14-4 fails. The verdicts "gradients computed + FD-verified" and "optimization converged" for this cell stay where D4/D4-SHIPPED's records put them.

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh` DOES NOT EXIST.**

`test -e` returned false at **2026-08-26T17:36:36Z**, immediately before this document was written, and again inside the selftest (§5) before and after every leg. The driver **refuses with exit 6** if it exists (A5). After the first container, gates are **CLOSED**.

## 2. THE NAMED CONTAMINANT RUNS FIRST — G14-0, A REFUSING GATE

`cases/dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md` measured that this lab's pyHyp extrusion lets the **maximum cell aspect ratio worsen under a refinement** in which the resolution parameters change while pyHyp's smoothing parameters (`epsE, epsI, theta, volCoef, volBlend, volSmoothIter`) stay unscaled (97.87 → 167.50 on the airfoil generator; cross-checked 2026-07-30). D14-M regenerates a mesh with the same tool, so the finding is a contaminant of this item **by name**, and its check runs **before any container starts**:

**`d14m_contaminant_check.py` (G14-0)** reads the generator FILE that will be staged and **REFUSES (rc 2, nothing launched)** if (i) its md5 is not the registered `dab5e959187ab2e2bfb4e2c0ded0feb6` — the generator that made D4's mesh, byte-identical to the tutorial's; (ii) any resolution parameter departs from the registered `N=39, s0=1.0e-3, marchDist=300.0, cMax=0.1`; (iii) any smoothing key is active (the registered generator leaves all six at pyHyp's defaults). **Planted control, driven before every launch and in the selftest:** a copy with `N` doubled and `s0` halved — the finding's own recipe — **must be REFUSED by the same reader while the staged file PASSES**, else the driver aborts (rc 2). The gate is a refusal, not a warning; a gate never shown able to refuse is ceremony (rule 3). It carries no `assert` and counts its own `ast.Assert` nodes (L-332).

**What G14-0 protects:** the comparison in §6 is only meaningful if the regenerated mesh was made by the SAME generator at the SAME resolution as the baseline; a silently refined generator would turn "the generator drifted" into "pyHyp is non-deterministic" and the contaminant would be read as a finding about the tool.

## 3. THE PIPELINE — ONE ARM, ONE CONTAINER, np = 1

| step | where | what |
|---|---|---|
| guards | host, driver | G-ROOT.1–.5, A5, **G14-0 + planted control**, instrument/input md5s, image digest, H5 window (45 samples / 60 s, floor **14.0 GiB**), aggregate memory wait-and-retry (caps + this cap + host RSS < **30.6 GiB**, poll 30 s, bound 14,400 s) |
| stage | host, copies only | `mdolab_wing_surface_mesh.cgns.tar.gz` (md5 `92956aa0e4cb9b17fa063bd95e8f78ba`) and `genWingMesh.py` from `/home/ubuntu/certonomous-runs/A2-mach-wing` (D4's baseline root, **never written**), `system/` + `constant/` from `/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing`; `AGE_DATUM` touched last |
| **MESH** | container `d14m_MESH_<stamp>`, `--cpuset-cpus=14 --cpus=1 --memory=4g --memory-swap=4g --oom-score-adj=500 --user 0:0`, **`docker run -d`, NO `--rm`**, deadline **`timeout -k 30 900` INSIDE the container** | `tar xzf` → `cgns_utils coarsen` (×1, as `preProcessing.sh`) → `python genWingMesh.py` → `plot3dToFoam -noBlank` → `autoPatch 60` → `createPatch` → `renumberMesh` → `checkMesh` (plain, as the baseline record) → `checkMesh -allGeometry -allTopology`; `date +%s` stamps between steps; step rcs are fatal except `checkMesh`, whose rc is recorded (a failed check is a GATE FAIL, not a crash) |
| record | host, driver | polls `docker inspect .State.Running`; then **`rc` = `.State.ExitCode`, `OOMKilled`, `StartedAt/FinishedAt`** → `STATUS.MESH` and one `ARM=MESH` ledger row; `docker logs` → `MESH_<stamp>.log`; `.ok` marker; the container is **not removed**; then the frozen comparator runs on the artifacts (its rc is INFRASTRUCTURE) |

**cpuset 14** is disjoint from every live and registered set on the box (W2R `12`; D4-SHIPPED `5,6,7,9`; D7FR `2,3,4,6`; D5 draft `8,10,11,13`) and avoids core 0 (the D13 first-core landing). **Toolchain identity = image digest** `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` (SHIPPED row; `DAFOAM_CHARTER.md` §6/§11), asserted by the driver; pyHyp **2.6.1**, cgnsutilities 2.6.0, OpenFOAM v2506 in that image (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §2; probed 2026-08-26T17:10Z: `import pyhyp` OK, `__debug__ True`, all six utilities on PATH). **The PATCHED row is not bought** — mesh generation does not touch IDWarp — and no toolchain-independence is claimed.

## 4. INSTRUMENTS, FROZEN BY BLOB AND MD5 AT THIS COMMIT

| file | git blob | md5 | role |
|---|---|---|---|
| `d14m_driver.sh` | `7caba9d00428c13bdcb7c4dadbb3fdcea7daa87d` | `0dc3e2470937233eda8903b919216264` | driver + launcher (§3); asserts the four md5s below before launch |
| `d14m_contaminant_check.py` | `521f6a47b1af34d20e4cc6ea6dd1a05cea524e82` | `28ce514d6683948f0883e4a5278c7f5a` | G14-0 (§2) |
| `d14m_grade.py` | `2835b729219cd23d8827b21a494c7f4a2f7b07db` | `c2a8cadb3d7863697412e6741cdea51e` | the comparator (§6); `EXPECTED_UNITS = 14` frozen |
| `d14m_aggregate_memory.py` | `8f7022b563888d19707554c5cdecf5849408d342` | `709ab0b98ef0302a3a3a318588f9493f` | byte-identical copy of `curriculum_D4_SHIPPED/d4s_aggregate_memory.py` (Addendum 2, `8b91be2b`) |
| `d14m_selftest.sh` | `48cd5fdd1980d73c6371b43d753dfa859e1385f2` | — | §5 |
| inputs | — | tarball `92956aa0e4cb9b17fa063bd95e8f78ba`; `genWingMesh.py` `dab5e959187ab2e2bfb4e2c0ded0feb6` | D4's own inputs, staged by copy |

## 5. GUARDS DEMONSTRATED BEFORE FREEZE — `d14m_selftest_evidence.txt`

`d14m_selftest.sh` drives, against a sacrificial root `_d14m_selftest_<stamp>`, a sacrificial `sleep` container and a sacrificial pid, with a BOGUS image name so no staging is reachable: `bash -n`/`py_compile`; G14-0 clean PASS and planted refinement REFUSED (the control fires) and a directly halved `s0` → rc 2 naming both the md5 and the parameter; grader selftest **14/14 under `python3` AND `python3 -O`** with `ast.Assert = 0` over both instruments; the driver's guard block clear → exit 40 with nothing staged; **G-ROOT.5 (a)** live `d14m_` container → rc 3; **G-ROOT.5 (b)** live pid whose cwd is the root → rc 3; stale pidfile ignored; **G-ROOT.3** foreign ITEM → rc 3; **G-ROOT.4** ALREADY_BOUGHT → rc 3; **G-ROOT.1** a non-sacrificial root (the baseline's) → rc 3; usage → 64; the registered root absent before and after; no container survives. **16 of 16** at the stamp in the evidence file. (The first run of the selftest caught a defect in this lane's own G-ROOT.4 pattern — `^ARM=MESH .* rc=0 ` could not match the row the driver itself writes — repaired before freeze and recorded here because a guard that cannot see its own row is the shape rule 3 exists for.)

## 6. GATES, THRESHOLDS AND LABELS — `d14m_grade.py`

The reference is D4's baseline mesh record `/home/ubuntu/certonomous-runs/A2-mach-wing/checkMesh.log` (2026-07-28, stock `checkMesh`, image of that day not recorded): **cells 38,304; points 40,209; faces 116,756; internal 113,068; max aspect ratio 684.4022128; max non-orthogonality 66.96543422 (avg 11.48508811); max skewness 1.339283343; `Mesh OK.`**; `points.gz` sha256 `260e9db7f5a021080a5bc48cacc0874af511fee82e59d33b7832cefde52cbd4e`. These are **recorded, not imported**: every number below is re-measured on this item's own regenerated mesh.

| gate | reads | verdict rule |
|---|---|---|
| **G14-1 completion** (refusal) | ledger row `rc` (= `docker inspect` ExitCode), `oom`, `Mesh OK.` line, `checkMesh.log` newer than `AGE_DATUM` (rule 4) | any clause fails → **`NOT A RESULT`**, comparator exit 2 |
| **G14-2 identity** | cells, points | == 38,304 and == 40,209 → `PASS`, else `GATE FAIL` (a different mesh is a different item) |
| **G14-3 `MESH_STANDARD` §3** | max non-orthogonality **< 70°** hard (65–70 warning band **reported** — the baseline sits in it at 66.97°); max skewness **< 4** hard; aspect ratio **advisory at 1000**, flagged only with non-ortho > 60° or skew > 2 (§3.3) | each hard gate `PASS`/`GATE FAIL` |
| **G14-4 reproduction / the contaminant** | max aspect ratio, max non-orthogonality, max skewness vs the baseline | all three within **1e-6 relative** → `PASS` (same generator, same inputs, same image); else `GATE FAIL`, and a max-aspect-ratio departure **> +10 % is named as the GENERATOR_FINDING class** in the record |

**Item verdict** (composition registered here, not chosen after): any refusal → `NOT A RESULT`; all of G14-2/3/4 `PASS` → **`PASS`**; else **`GATE FAIL`** — and a `GATE FAIL` on G14-4 is **the finding** ("this toolchain does not reproduce D4's mesh"), not a defect. **No grid family, so standing rule 5 has no row and NO GCI IS QUOTED.** Field classes (L-342, `d4d0c29d`): `rc`/`oom`/`Mesh OK.`/numbers/age are physics-critical; wall, core-min, MemAvailable, container name and driver pid are infrastructure — an unparseable wall voids only the cost claim (driven: grader unit U12).

**Planted controls in the comparator (rule 3), all fired in §5:** aspect ratio 1500 → G14-4 `GATE FAIL` + drift named; non-ortho 71° → G14-3 `GATE FAIL`; skew 4.5 → `GATE FAIL`; cells 38,305 → G14-2 `GATE FAIL`; a 1e-6-relative departure → `GATE FAIL` without drift naming; `rc=1`, `OOMKilled`, no `Mesh OK.`, stale log → refusals.

## 7. PREDICTIONS — scored HIT/MISS by the comparator, never adjusted

| # | prediction | value / band |
|---|---|---|
| **P1** | the regenerated mesh has D4's cell and point counts exactly | **38,304 / 40,209** |
| **P2** | max aspect ratio reproduces | **684.4022128 ± 1e-6 relative** |
| **P3** | max non-orthogonality reproduces | **66.96543422 ± 1e-6 relative** (inside the 65–70 warning band) |
| **P4** | max skewness reproduces | **1.339283343 ± 1e-6 relative** |
| **P5** | pyHyp march cumulative CPU at level 39 | **[2.0, 10.0] s**, point 4.2 (the baseline log's own last-level column) |
| **P6** | container wall (`StartedAt → FinishedAt`) | **≤ 120 s**, point 40 s |

**The falsifier of this rung's premise:** P2 MISS with a departure > +10 % — the generator finding reaching a mesh that was NOT refined — would be a new finding about the toolchain, registered here as a possible outcome so it cannot later be read as an instrument defect.

## 8. COST — DERIVED FROM NAMED ANCHORS, NOT MEASURED

Anchors: (i) the baseline's own `logMeshGeneration.txt` — pyHyp cumulative CPU **4.2 s** at level 39, OpenFOAM utilities **00:18:10 → 00:18:12** (~3 s), `renumberMesh` 0.52 s; (ii) D12R §8's `S0` mesh stage (pyHyp + checkMesh in-container, 2,450 cells) **0.05 core-min measured**; (iii) container start + `loadDAFoam.sh` ≈ 10–20 s on this box (D12R2W2R S0 stage wall). **Point: 40 s wall × 1 rank = 0.67 core-min; band [0.3, 2.0] core-min.** Guards: **cap 15.0 core-min** = the 900 s in-container deadline (what stops it), **ceiling 30.0** (report-only). Dollars **$0.0006 point / $0.0128 at cap**, derived at $0.0513/core-h, c7a.4xlarge, **REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5). Calibration row owed at completion, id re-derived by hand in the committing invocation.

## 9. WHAT THIS RUNG WILL NOT ESTABLISH

Nothing about the optimum (the re-mesh at D4's endpoint is the successor rung); nothing about gradients or CD; nothing about pyHyp's internal mechanism (the finding's own "not established" stands); nothing at `np > 1`; nothing about the PATCHED row; **no grid family, no GCI**; nothing about `St`. One regenerated mesh against one baseline is a reproduction test, not a convergence study, and the record says so.

## 10. QUEUE

Entry `verification/queue/dafoam/D14M.json`: argv `["bash", ".../curriculum_D14/d14m_driver.sh", "MESH"]`, cwd this directory, ranks 1, cost 0.67 core-min, memory floor 14.0 GiB, `precondition_artifact` none (independent of every other item; the driver's own guards are its preconditions), permission `bc0e687e`. The runner's `setsid nohup` line is not the rc path: `STATUS.MESH` in the run root carries `rc=<n> … source=docker_inspect_ExitCode`.
