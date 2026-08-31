# DAFoam toolchain inventory — components, images, patches, and how to run a case

**Owner: Lane A of the DAFoam team. Created 2026-08-21. Nothing here was sent, filed, uploaded or
registered anywhere. No solve was launched to produce this file.**

**Method.** Every version, path and line number below was read out of a *live container* by a
command run for this document; the command and its output are pasted verbatim in §6. Where a
number comes from a lab record instead of from a command, the record is cited. Nothing is from
memory. Every `docker run` in this file is bounded: `--rm`, foreground, no background, no `kill`
needed.

**Host.** 16 cores, 30 GiB RAM (`nproc` → `16`; `free -g` → `Mem: total 30, available 29`,
`Swap: total 15`). Docker requires `sudo -n` (passwordless sudo); a bare `docker` call fails.
**The team caps itself at 8 concurrent cores** across all lanes, so `--cpus` across simultaneous
containers must sum to ≤ 8. `scripts/launch_solve.sh` reserves 2 cores and treats 14 as "usable"
for its own contention warning — that is the launcher's number, not the team's cap; the team cap
of 8 is tighter and binds.

---

## 1. Components, versions, and in-container paths

All three images carry **identical Python-package versions** — they differ only in a C++ source
file and its rebuilt library (§3). Measured 2026-08-21, §6(a).

| component | version | path inside the container |
|---|---|---|
| **DAFoam** | **5.0.0** | `/home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/dafoam` (Python); source tree `/home/dafoamuser/dafoam/repos/dafoam` |
| DAFoam compiled solver library | — | `…/site-packages/dafoam/libs/pyDASolvers.cpython-310-x86_64-linux-gnu.so`; AD variants in `dafoam/libs/ADF/` and `dafoam/libs/ADR/` |
| **IDWarp** | **2.6.2** | `…/site-packages/idwarp` — **binary install, no Fortran source in the image** (see §4) |
| **pyGeo** | **1.13.0** | `…/site-packages/pygeo` |
| **pyHyp** | **2.6.1** | `…/site-packages/pyhyp` |
| **pyOptSparse** | **2.10.1** | `…/site-packages/pyoptsparse` |
| **OpenFOAM** | **v2506** | `/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506`; binaries in `platforms/linux64GccDPInt32Opt/bin` (`simpleFoam`, `decomposePar`, `checkMesh`, …) |
| **PETSc** | **3.15.5** (`PETSC_ARCH=real-opt`) | `/home/dafoamuser/dafoam/packages/petsc-3.15.5` |
| petsc4py | 3.15.5 | `…/site-packages/petsc4py` |
| **MPI** | **Open MPI 4.1.6** | `mpirun` on `PATH` after `loadDAFoam.sh` |
| mpi4py | 4.1.1 | `…/site-packages/mpi4py` |
| **Python** | **3.10.8** (miniconda3) | `/home/dafoamuser/dafoam/packages/miniconda3` |
| **NumPy** | 1.23.5 | `…/site-packages/numpy` |
| **SciPy** | **1.13.1** | `…/site-packages/scipy` |
| OpenMDAO | 3.26.0 | `…/site-packages/openmdao` |
| MPhys | 1.1.0 | `…/site-packages/mphys` |
| pySpline | 1.5.2 | `…/site-packages/pyspline` |
| cgnsUtilities | 2.6.0 | `…/site-packages/cgnsutilities` |
| multipoint | 1.4.0 | `…/site-packages/multipoint` |
| baseclasses | **no dist-info** — `importlib.metadata.version("baseclasses")` raises `PackageNotFoundError`; the module itself is importable | `…/site-packages/baseclasses` |

**Entry point.** The environment is *not* active in a bare shell. Every command must
`source /home/dafoamuser/dafoam/loadDAFoam.sh` first (1,100 bytes, mode 755). A `bash -lc` login
shell alone is not sufficient.

**Two things worth knowing before writing any run command:**

1. **`DASimpleFoam` is not an executable.** `which DASimpleFoam` returns nothing (§6c). It is a
   DAFoam *solver class* selected by `daOptions["solverName"]` and dispatched inside
   `pyDASolvers…so`. The case is always driven by `python runScript.py -task <task>`, never by
   invoking a `DA*Foam` binary.
2. **Every case run leaves root-owned `processorN/` directories on the host bind mount**, and a
   later task that redecomposes from `0/` collides with them
   (`ladder-a/A1_naca0012_incompressible.md`, "Blocker" and "Lesson" sections;
   `A2_mach_tutorial_wing.md` §7.2). `sudo rm -rf processor*` before every invocation.

---

## 2. Hard-coded solver settings in the shipped adjoint linear solver

Read in-container from `/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DALinearEqn/DALinearEqn.C`
(507 lines in the stock image; `src/adjoint/lnInclude/DALinearEqn.C` is a symlink to it):

| line | statement | consequence |
|---|---|---|
| 137–138 | `// First, KSPSetFromOptions MUST be called` / `KSPSetFromOptions(ksp);` | every `-ksp_*` / `-pc_*` runtime option is applied here and then overwritten by the setters below |
| 142, 144 | `KSPType kspObjectType = KSPGMRES;` … `KSPSetType(ksp, kspObjectType);` | Krylov method hard-coded to **GMRES** |
| 158 | `KSPGMRESSetRestart(ksp, restartGMRES);` | restart from `daOptions`, not from `-ksp_gmres_restart` |
| 212 | `PCSetType(MLRGlobalPC, PCASM);` | global preconditioner hard-coded to **additive Schwarz** |
| **266–267** | **`PCType localPCType = PCILU;`** / `PCSetType(MLRsubpc, localPCType);` | **ASM sub-block PC hard-coded to ILU** |

The supervisor's standing picture says *"PETSc GMRES + ILU(k), PCILU hard-coded in DALinearEqn.C"* —
**CONFIRMED**, with the line numbers above. Note the defect record
`DEFECT_CANDIDATE_ksp_options_override.md` §2 cites these as lines 138 / 212 / 286 against a
different build of the file; in the image on this box today the sub-PC line is **266**, not 286.

**Decomposition default.** `dafoam/pyDAFoam.py:597–604` ships
`self.decomposeParDict = {"method": "scotch", "simpleCoeffs": {"n": [2, 2, 1], "delta": 0.001}, …}`.
`scotch` is the shipped default and is the configuration under which the decomposition defect fires
(`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`, "Exposure" bullet).

---

## 3. Container images: what exists and what they differ by — **SUPERSEDED 2026-08-31: THIS IMAGE LIST IS STALE and is not the live record. See Amendment 4 (§A4), Amendment 3 (§A3.2), Amendment 2 (§A2.1) and Amendment 1 §A1.1–A1.3. Original heading text preserved verbatim above this marker; no line was inserted, moved or renumbered.**

`sudo -n docker images` (2026-08-21):

```
IMAGE                        ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine:latest                28bd5fe8b56d         13MB         3.93MB
dafoam-kspopts:v1            d9d2aed02e36         10GB         2.12GB
dafoam-subpclu:v1            ba2d16ab9d57       9.97GB         2.11GB
dafoam/opt-packages:latest   9d45679d55fd       9.93GB          2.1GB
```

`sudo -n docker history <image> --no-trunc | head` gives the layer chain — the two patched images
are thin layers on the stock one, in a strict line:

```
dafoam/opt-packages:latest
  sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc   5 weeks ago   7.83GB   Imported from -

dafoam-subpclu:v1
  sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517   2 weeks ago   30.6MB   sleep infinity
  sha256:9d45679d55fd…                                                       5 weeks ago   7.83GB   Imported from -

dafoam-kspopts:v1
  sha256:d9d2aed02e3615c0c282de45da8d30b8835d2a111ee1a2cb93a16dbbd8af8be2  10 days ago   30.7MB   sleep infinity
  sha256:ba2d16ab9d57…                                                      2 weeks ago   30.6MB   sleep infinity
  sha256:9d45679d55fd…                                                      5 weeks ago   7.83GB   Imported from -
```

The stock image's digest `sha256:9d45679d55fd…90f07fc` is the same digest the root-cause record
pins IDWarp 2.6.2 to (`ROOTCAUSE_getRotationMatrix3d.md` §1.1) — the image on this box **is** the
image every published number was measured on.

**Measured difference between the images** (in-container `md5sum` + `wc -l`, §6e):

| image | `src/adjoint/DALinearEqn/DALinearEqn.C` md5 | lines | `DAFOAM_SUBPC_TYPE` occurrences | `KSPSetFromOptions` at |
|---|---|---|---|---|
| `dafoam/opt-packages:latest` | `f6a89e33b0f4772a0563cb0c8633ac48` | 507 | 0 | line 138 (top) |
| `dafoam-subpclu:v1` | `89e71ca2db5d80c06b1eda070ffc7a1b` | **526** (+19) | 3 | line 138 (top) |
| `dafoam-kspopts:v1` | `96f5762819e33efbdaad34181a214082` | **534** (+8) | 3 | **line 351 (end)** |

The +19 lines in `subpclu` match exactly the "19-line `DAFOAM_SUBPC_TYPE=lu` block" the patch file
claims is deployed, and the **absence** of the later `else if` warning block is confirmed by the
occurrence count of 3 — exactly what the patch file's own "NEXT-REBUILD DELTA (finding B-1)" note
predicts (`subpclu_patch/DALinearEqn_subpclu.patch`, provenance header). **The patch file on disk
is one hunk ahead of the built image, as its own header says.**

### What each patch does

| patch file (host) | in-image target | image that carries it | effect |
|---|---|---|---|
| `cases/dafoam/subpclu_patch/DALinearEqn_subpclu.patch` (3,841 B) | `src/adjoint/DALinearEqn/DALinearEqn.C`, after line 266 `PCType localPCType = PCILU;` | `dafoam-subpclu:v1` | env var `DAFOAM_SUBPC_TYPE=lu` switches the ASM sub-block PC from ILU to complete LU (`PCLU`). **Off by default — env unset ⇒ stock behaviour.** Prints `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` when active; the absence of that banner is the standing proof the run was stock (`A3_TPC1_ARM_PREREGISTRATION.md` §2). |
| `cases/dafoam/kspopts_patch/DALinearEqn_kspopts.patch` (1,396 B, "one call relocated, 28 diff lines") | same file, moves `KSPSetFromOptions(ksp)` from line 138 to after `KSPSetTolerances` | `dafoam-kspopts:v1` | PETSc runtime options (`-ksp_type`, `-pc_type`, `-sub_pc_type`) become *overrides* of `daOptions` instead of being silently discarded. Measured behaviour-neutral with no options set: ONERA M6 21,840 cells returns CD 368 / CL 383 iterations, `PetscConvergedReason: 2`, bit-identical to the unpatched image (`DEFECT_CANDIDATE_ksp_options_override.md` §8; `A3_KSPOPTS_PATCH_PREREGISTRATION.md` §6 Gate A). |
| `cases/dafoam/rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch` (4,061 B, 2 files, +44 lines) | IDWarp `src/adjoint/outputReverse/vectorUtils_b.f90` and `src/adjoint/outputForward/vectorUtils_d.f90` | **NO IMAGE** — see §4 | supplies the analytic limit `v2b += (axial(mib − mibᵀ) × v1)/(‖v1‖‖v2‖)` that the `sqrt(eps)` guard at `src/utils/vectorUtils.f90:58` discards |

Nothing else differs between the images: the Python package set, OpenFOAM, PETSc, MPI and Python
versions are identical across all three (§6a).

---

## 4. The IDWarp rotation patch is NOT in any container image — **SUPERSEDED 2026-08-31: TRUE OF THE PATCH *SOURCE* ONLY. `dafoam-idwarp-rot:v1` DOES carry a rebuilt `libidwarp.so` (md5 `85f59e87253e0a71a813f64ca6e4c425`, digest `sha256:2927768a16ac…`). Do not quote this heading without this clause. See Amendment 4 (§A4), Amendment 3 (§A3.1–A3.2) and Amendment 1 §A1.3. Original heading text preserved verbatim above this marker; no line was inserted, moved or renumbered.**

This is the most operationally important fact in this file, and it is easy to get wrong.

`idwarp` ships into the image as a **built Python package with no Fortran sources**:
`find /home/dafoamuser/dafoam -path '*outputReverse/vectorUtils_b.f90'` returns **nothing** in all
three images (§6d). There is therefore no image in which the rotation fix could have been applied,
and none was.

The patched IDWarp exists only as a **host-side scratch clone with a locally compiled shared
library**:

```
/home/ubuntu/certonomous-runs/W5-patch/idwarp/                       # git clone at tag v2.6.2 (647fd8fc…)
/home/ubuntu/certonomous-runs/W5-patch/idwarp/idwarp/libidwarp.so    # locally built
/home/ubuntu/certonomous-runs/W5-patch/idwarp/src/adjoint/outputReverse/vectorUtils_b.f90
        :29   ! HAND FIX 2026-07-31: axial vector of (mib - mib^T), used by the
        :144  axialmib(1) = mib(3, 2) - mib(2, 3)
        :147  v2b(1) = v2b(1) + (axialmib(2)*v1(3)-axialmib(3)*v1(2))/(magv1*magv2)
```

It is injected into a **stock** container at run time by bind-mounting the clone and prepending it
to `PYTHONPATH`. Verified working today (§6f): the import resolves to `/patch/idwarp/…` and still
reports version `2.6.2`, so the version string alone **cannot** tell a patched run from a stock one —
which is why every regrade log prints `IDWARP_IMPORTED_FROM:` as its provenance stamp
(`W5_GRADIENT_REGRADE.md` §0).

**Consequence for planning:** any lane wanting patched-warp numbers must mount `W5-patch` and set
`PYTHONPATH`; it cannot just pick a different image tag. Conversely `dafoam-subpclu:v1` and
`dafoam-kspopts:v1` carry **stock IDWarp**, so the A3 ONERA M6 results measured on them are
stock-warp results.

---

## 5. Patch-directory contents (host)

| directory | contents |
|---|---|
| `cases/dafoam/rotation_branch/` | the patch (`idwarp_v2.6.2_degenerate_branch_fix.patch`); reproducers `repro_issue57_inflate_cube.py`, `repro_geometries.py`, `diag_rotation_ubend.py`; 8 stock diagnostic logs `D1a…D6_*`; 8 five-mesh logs `geom_{o,co,sym}_mesh_{on,off}.txt`, `geom_onera_m6_{on,off}.txt`; upstream anchors `issue57_rot_{on,off}.txt`; subdirs `patched/` (post-patch acceptance logs), `patch_unittest/` (standalone Fortran driver + 3 logs), `independent_check/`, `supervisor_sweep/` |
| `cases/dafoam/kspopts_patch/` | one file: `DALinearEqn_kspopts.patch` |
| `cases/dafoam/subpclu_patch/` | one file: `DALinearEqn_subpclu.patch` (with a provenance header stating it is one hunk ahead of the built image) |
| `cases/dafoam/upstream_repro/` | self-contained reproducer bundle: `README.md`, `run_repro.sh`, `repro_warpderiv_ubend.py`, `repro_warpderiv_airfoil.py`, and 4 execution logs. README states **"Nothing here has been sent anywhere."** |
| `cases/dafoam/work/`, `work_refined/`, `work_sail/`, `work_wing/` | **live OpenFOAM case trees, not documentation.** No README in any of them. `work/NACA0012_Airfoil_Incompressible` (A1 tutorial + ~15 diagnostic probe scripts: `probeWarpDerivRealSeed.py`, `probeHandComposition.py`, `diagnose_chain{,2}.py`, `stepStudy2.py`, `probeWallBranch.py`, …); `work_refined/` (`…_refined` = the 3.65× refinement arm, `…_probe` = probe copy); `work_sail/` (naca0015 sail at `coarse`/`medium`/`full` + `naca4412_wing_check`); `work_wing/naca4412_wing_coarse`. All carry populated `processor*/` directories — clear them before reuse. |

---

## 6. Commands actually run, with verbatim output

All run 2026-08-21 on this host. Every one is `--rm`, foreground, bounded.

### (a) Core package versions — all three images

```
$ sudo -n docker run --rm dafoam/opt-packages:latest bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh && python -c "import importlib.metadata as m; print(m.version(\"dafoam\"), m.version(\"idwarp\"), m.version(\"pygeo\"))"'
5.0.0 2.6.2 1.13.0

$ sudo -n docker run --rm dafoam-subpclu:v1 bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh && python -c "import importlib.metadata as m; print(m.version(\"dafoam\"), m.version(\"idwarp\"), m.version(\"pygeo\"))"'
5.0.0 2.6.2 1.13.0

$ sudo -n docker run --rm dafoam-kspopts:v1 bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh && python -c "import importlib.metadata as m; print(m.version(\"dafoam\"), m.version(\"idwarp\"), m.version(\"pygeo\"))"'
5.0.0 2.6.2 1.13.0
```

Note the adaptation the task anticipated: `import dafoam; dafoam.__version__` **fails** —
`AttributeError: module 'dafoam' has no attribute '__version__'`. `importlib.metadata.version` is
the working route. `stderr` also carries three TensorFlow banner lines and a
`WARNING 7: VSPAERO Viewer Not Found` from `loadDAFoam.sh`; both are benign and are filtered above.

### (b) Full package inventory (stock image; identical set in the other two)

```
$ sudo -n docker run --rm dafoam/opt-packages:latest bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh; python -c "
import importlib.metadata as md
for p in [\"dafoam\",\"idwarp\",\"pygeo\",\"pyhyp\",\"pyoptsparse\",\"mphys\",\"openmdao\",\"numpy\",\"scipy\",\"mpi4py\",\"petsc4py\",\"cgnsutilities\",\"baseclasses\",\"pyspline\",\"multipoint\"]:
    try: print(p, md.version(p))
    except Exception: print(p, \"NOT-FOUND\")
import sys; print(\"python\", sys.version.split()[0])"'
dafoam 5.0.0
idwarp 2.6.2
pygeo 1.13.0
pyhyp 2.6.1
pyoptsparse 2.10.1
mphys 1.1.0
openmdao 3.26.0
numpy 1.23.5
scipy 1.13.1
mpi4py 4.1.1
petsc4py 3.15.5
cgnsutilities 2.6.0
baseclasses NOT-FOUND
pyspline 1.5.2
multipoint 1.4.0
python 3.10.8
```

### (c) PETSc version, OpenFOAM version, MPI

```
$ sudo -n docker run --rm dafoam/opt-packages:latest bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh; echo "WM_PROJECT_VERSION=$WM_PROJECT_VERSION"; echo "WM_PROJECT_DIR=$WM_PROJECT_DIR"; echo "PETSC_DIR=$PETSC_DIR  PETSC_ARCH=$PETSC_ARCH"; grep -E "PETSC_VERSION_(MAJOR|MINOR|SUBMINOR)\b" $PETSC_DIR/include/petscversion.h; mpirun --version | head -1; which DASimpleFoam simpleFoam decomposePar checkMesh'
WM_PROJECT_VERSION=v2506
WM_PROJECT_DIR=/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506
PETSC_DIR=/home/dafoamuser/dafoam/packages/petsc-3.15.5  PETSC_ARCH=real-opt
#define PETSC_VERSION_MAJOR      3
#define PETSC_VERSION_MINOR      15
#define PETSC_VERSION_SUBMINOR   5
mpirun (Open MPI) 4.1.6
/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/simpleFoam
/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/decomposePar
/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/checkMesh
```

(`DASimpleFoam` produces no line — it is not a binary. See §1.)

### (d) IDWarp Fortran source is absent from the images

```
$ sudo -n docker run --rm dafoam/opt-packages:latest bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh; python -c "import idwarp,os;print(os.path.dirname(idwarp.__file__))"; F=$(find /home/dafoamuser/dafoam -path "*outputReverse/vectorUtils_b.f90" | head -1); echo "F=$F"; G=$(find /home/dafoamuser/dafoam -path "*utils/vectorUtils.f90" | head -1); echo "G=$G"'
/home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/idwarp
F=
G=
```

Identical empty result on `dafoam-subpclu:v1` and `dafoam-kspopts:v1`.

### (e) What the two patched images actually changed

```
$ for img in dafoam/opt-packages:latest dafoam-subpclu:v1 dafoam-kspopts:v1; do
    sudo -n docker run --rm $img bash -lc 'F=/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DALinearEqn/DALinearEqn.C; md5sum $F; grep -c "DAFOAM_SUBPC_TYPE" $F; grep -n "KSPSetFromOptions" $F; wc -l $F'; done

f6a89e33b0f4772a0563cb0c8633ac48  …/DALinearEqn.C
0
137:    // First, KSPSetFromOptions MUST be called
138:    KSPSetFromOptions(ksp);
507 …/DALinearEqn.C

89e71ca2db5d80c06b1eda070ffc7a1b  …/DALinearEqn.C
3
137:    // First, KSPSetFromOptions MUST be called
138:    KSPSetFromOptions(ksp);
526 …/DALinearEqn.C

96f5762819e33efbdaad34181a214082  …/DALinearEqn.C
3
137:    // PATCHED 2026-08-10 (Certonomous): KSPSetFromOptions relocated to the END of
346:    // PATCHED 2026-08-10 (Certonomous): KSPSetFromOptions moved from the TOP of this
351:    KSPSetFromOptions(ksp);
534 …/DALinearEqn.C
```

### (f) Patched IDWarp injected into a stock image (proof the mount route works)

```
$ sudo -n docker run --rm -v /home/ubuntu/certonomous-runs/W5-patch:/patch:ro dafoam/opt-packages:latest bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh; export PYTHONPATH=/patch/idwarp:$PYTHONPATH; python -c "
import idwarp; print(\"IDWARP_IMPORTED_FROM:\", idwarp.__file__)
import importlib.metadata as m; print(\"idwarp version:\", m.version(\"idwarp\"))"'
IDWARP_IMPORTED_FROM: /patch/idwarp/idwarp/__init__.py
idwarp version: 2.6.2
```

### (g) A4 Ahmed case — dry listing, no solve launched

```
$ ls -la /home/ubuntu/certonomous-runs/A4-ahmed-body/
drwxrwxr-x  coarse        # 2,777 cells — the adjoint / FD-verification mesh
drwxrwxr-x  fine          # 45,760 cells — the primal-comparison mesh

$ ls -la /home/ubuntu/certonomous-runs/A4-ahmed-body/coarse/
0/  0.orig/  FFD/  constant/  system/  reports/
check_totals_run1.log      1197232
compute_run_model_par4.log  409622
compute_totals_run1.log     411857
dRdWColoring_4.bin          209200      # coloring cache, reused across runs
dRdWColoring_4.bin.info         22
log.blockMesh  log.checkMesh  log.renumberMesh  log.snappyHexMesh  log.surfaceFeatureExtract
mphys.html                  981611
preProcessing.sh               398
runScript.py                  5364
```

`runScript.py` takes `-task {run_driver|run_model|compute_totals|check_totals}` (lines 24–26,
126–148) and sets `primalMinResTol: 1.0e-4`, `primalMinResTolDiff: 1.0e5`, `solverName:
"DASimpleFoam"`, `designSurfaces: ["body"]`, `U0 = 40.0`, `Aref = 0.401696`, `lRef = 1.044`.
Note the loose `1.0e-4` primal tolerance — it is a named unseparated co-ingredient candidate for
the decomposition defect (`DEFECT_ROBUSTNESS_mesh_and_setup.md`, R3b).

**The exact invocation previously used** (verbatim from
`/home/ubuntu/certonomous-runs/W5-regrade/run_a4_checktotals.sh`, the script that produced the
regrade's stock and patched A4 rows). **NOT RUN in this phase:**

```bash
# stock toolchain
sudo docker run --rm --cpus=4 --memory=8g \
    -v /home/ubuntu/certonomous-runs/W5-regrade:/mnt -w /mnt/a4_stock \
    dafoam/opt-packages:latest bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     python -c 'import idwarp; print(\"IDWARP_IMPORTED_FROM:\", idwarp.__file__)' && \
     mpirun --allow-run-as-root -np 4 -x PYTHONPATH python runScript.py -task check_totals"

# patched-IDWarp toolchain: adds the mount and the PYTHONPATH prefix
sudo docker run --rm --cpus=4 --memory=8g \
    -v /home/ubuntu/certonomous-runs/W5-regrade:/mnt \
    -v /home/ubuntu/certonomous-runs/W5-patch:/patch -w /mnt/a4_patched \
    dafoam/opt-packages:latest bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     export PYTHONPATH=/patch/idwarp:\$PYTHONPATH && \
     python -c 'import idwarp; print(\"IDWARP_IMPORTED_FROM:\", idwarp.__file__)' && \
     mpirun --allow-run-as-root -np 4 -x PYTHONPATH python runScript.py -task check_totals"
```

Measured cost of that pair: 47 s + 58 s wall at 4 ranks = **7.0 core-min**
(`W5_GRADIENT_REGRADE.md` §5).

**Before running either:** `sudo rm -rf <case>/processor*`. **After:** `sudo chown -R ubuntu:ubuntu`
the log, because the container writes as root onto the bind mount.

For long solves the lab's sanctioned launcher is `scripts/launch_solve.sh --name <tag> --case <dir>
--item <docket-id> --ranks <n> --est <core-min> -- <command…>`; it runs `scripts/case_preflight.sh`
as a hard gate, launches detached with the real PID, and arms a collector that writes a completion
record. It does **not** bound the container — `--cpus`/`--memory` must still be passed to
`docker run`, and the Bash tool's own `timeout` parameter must be set generously or the container
is orphaned (`ladder-a/A6_crm_wingbody.md` §2 and §5.1).

---

## 7. Reference: which toolchain produced which published result

| result family | image | IDWarp | notes |
|---|---|---|---|
| Ladder A1/A2/A3(original)/A4/A5/A6 as first published (2026-07-28) | `dafoam/opt-packages:latest` | stock 2.6.2 | the "SHIPPED toolchain" verdicts |
| W5 regrade "patched" columns; `rotation_branch/patched/` | `dafoam/opt-packages:latest` + `-v W5-patch` + `PYTHONPATH` | **patched** clone | the "PATCHED toolchain" numbers; not installable by any reader |
| A3 ONERA M6 sweep rungs 1–3 (TPC1, control, FD3, triage levers, sub-LU) | `dafoam-subpclu:v1` (`DAFOAM_SUBPC_TYPE` **unset** ⇒ stock behaviour) | stock 2.6.2 | stock-equivalent unless the sub-LU banner appears in the log |
| A3 Stage-2 unreachable-class arms (`-ksp_type lgmres`, `-pc_type gamg`) | `dafoam-kspopts:v1` | stock 2.6.2 | only image where PETSc runtime options take effect |
| A4 SIMPLEC activity proof | `dafoam-subpclu:v1` | stock 2.6.2 | `A4_SIMPLEC_ACTIVITY_PROOF_PREREGISTRATION.md` §5 |

---

*Lane A, Phase 0. No solve was run. Nothing filed, sent or registered.*

---

## AMENDMENT 1 — 2026-08-26. THE PATCHED ROW'S IDENTIFIERS, AND THIS FILE WAS MEASURED INCOMPLETE.

**Appended at the foot. `lines whose number changed above this section: 0` — nothing above is
edited, reordered or renumbered** (`CLAUDE.md` rule 6). This amendment **adds identifiers and a
disclosure**; it retires no statement, moves no threshold and creates no gate.

**Why it exists.** `DAFOAM_CHARTER.md` §11 makes **the hash the identity and the version string
never**, and `DAFOAM_CHARTER.md` §6 makes a DAFoam verdict **two rows**. This file was measured, on
2026-08-26 during the D7R grading, to name **`dafoam-idwarp-rot:v1` nowhere at all** and to carry
neither its digest nor its `libidwarp.so` md5 — so **the family's own toolchain record could settle
only half of a two-row charter.** A record that cannot identify one of the two rows it exists to
distinguish is incomplete, and it is named here rather than quietly patched into §3.

### A1.1 The two rows, by hash, each with where it was MEASURED

| row | image | digest | `libidwarp.so` md5, printed from inside the process that loaded it |
|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`**, 491,344 B |
| **PATCHED-ROT** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **`85f59e87253e0a71a813f64ca6e4c425`**, 491,344 B |

**Where each figure was measured, cited rather than asserted:**

* **Both digests, re-measured live for this amendment on 2026-08-26**, by
  `sudo -n docker inspect --format '{{.Id}}'` on each tag. Both returned exactly the values above.
* **Both `.so` md5s** are recorded at `cases/dafoam/MATRIX_CONTRIBUTION.md:113` (SHIPPED) and `:114`
  (PATCHED-ROT), with the patch that produced the second named beside it
  (`cases/dafoam/rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch`, 4,061 B, 2 files,
  +44 lines).
* **The PATCHED md5 printed from inside the loading process**, which is the only reading that
  identifies what a run actually imported:
  `cases/dafoam/ladder-a/A1/curriculum_D1/RESULTS.md:361-363` — three containers (armE run 1, armE
  run 2, armO) each printed `85f59e87253e0a71a813f64ca6e4c425`, against `:364` where armC printed
  `f0fcb488e0e98156575cd19548e91663`. **The same file's F2 falsifier — "any arm's printed
  `IDWARP_SO_MD5` ≠ §3's row → that arm void" — did not fire on any of the four containers**
  (`:635`).
* **The SHIPPED md5 printed from inside the loading process**, most recently:
  `D7_IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663` on all three D7R arms
  (`/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin/ledger.txt`).

> **THE VERSION STRING DISCRIMINATES NOTHING AND IS NOT USED HERE.** §4 above already measures that
> **both** libraries report IDWarp `2.6.2` and **both are 491,344 bytes**. The md5 is the only
> reading that separates them, which is precisely `DAFOAM_CHARTER.md` §11's point.

### A1.2 §3's image list is STALE, and by more than the row this amendment adds

§3 was measured 2026-08-21 and lists **four** images. `sudo -n docker images --no-trunc` on
2026-08-26 returns **seven**:

| present in §3 | absent from §3 |
|---|---|
| `alpine:latest`, `dafoam-kspopts:v1`, `dafoam-subpclu:v1`, `dafoam/opt-packages:latest` | **`dafoam-idwarp-rot:v1`** (`sha256:2927768a16ac…f6d35`), **`dafoam-subpclu:v2`** (`sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46`), **`dafoam-team:v1`** (`sha256:0b3c94c33a15cc9b6be48ff1c7e8fa50e870f53d7626bd56b7e173bfd7e9dc1d`) |

**The three absent images are recorded here by digest and NOT characterised.** This amendment did
not run a container to establish what `dafoam-subpclu:v2` or `dafoam-team:v1` contain, so it says
nothing about them beyond their existence and their hash. **An identifier is not a description, and
inventing one would be the defect this amendment exists to close.**

### A1.3 What this amendment does NOT change

* **§4's statement stands as written for what it was about.** §4 says the IDWarp rotation **patch
  source** is in no container image and that `idwarp` ships as a built package with no Fortran
  sources — that remains true. `dafoam-idwarp-rot:v1` is an image carrying a **rebuilt
  `libidwarp.so`**, which is a different claim from carrying the patch source, and §4 is not
  contradicted by it. The two statements are separated here so neither is read as retiring the
  other.
* **§7's row** *"W5 regrade 'patched' columns … `dafoam/opt-packages:latest` + `-v W5-patch` +
  `PYTHONPATH` … not installable by any reader"* describes the **bind-mount route** and stays
  correct for the results it names. The image route recorded in A1.1 is a **later, separate** way of
  reaching a patched IDWarp, and rows measured on it cite `2927768a16ac`, not the mount.
* **Nothing here was sent, filed, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).
  **No image was pushed anywhere and none is installable by any reader** — every PATCHED-ROT row in
  this lab carries that qualifier and this amendment does not weaken it.

---

## AMENDMENT 2 — 2026-08-27, dafoam lane C — §3's IMAGE LIST IS STALE; A1.1/A1.2 ARE THE LIVE RECORD. Plus four freeze-time reads from FADR.

**Appended at the foot, never in place: other records cite this file by line
(`cases/dafoam/ladder-a/A2/curriculum_D14/PREREGISTRATION_DRAFT.md`,
`cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md`,
`cases/dafoam/ladder-b/B3/decomposition_peak_rss/PREREGISTRATION.md`).
**Lines whose number changed above this section: 0.** Zero compute; every reading below is a file
read or a `docker inspect`. **No gate, threshold, band or label moves, and nothing is retired.**

### A2.1 THE CORRECTION

**§3's image list was measured 2026-08-21 and is STALE.** This is not new — **Amendment 1 §A1.2
already said so**, and named three images §3 omits. It is restated here as a **pointer at the top
level** because §3 is the section a reader reaches for first, and it does not itself say it is out
of date. **The live record is A1.1 (:405–:410) for the two graded rows, and A1.2 (:435 ff.) for the
fuller image list.** A reader wanting a digest should go there, not to §3.

**Why a stale digest list is more dangerous here than a stale prose section.** §11's rule is that
**the DIGEST is the identity and the version string is not** — the IDWarp rotation patch moves a
reverse-mode derivative by seven orders of magnitude while the version string reads `2.6.2` either
way. A reader who takes §3 as live can therefore pin a row to a **tag**, and a tag is exactly the
thing that can come to resolve elsewhere. The stale list quietly re-admits the failure mode §11
exists to close.

### A2.2 BOTH GRADED DIGESTS RE-MEASURED LIVE, a second independent confirmation of A1.1

Read **2026-08-27T19:03:34Z** with `sudo -n docker inspect --format '{{.Id}}' <tag>`:

| row | tag | digest returned |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` |
| **PATCHED-ROT** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` |

**Both are exactly A1.1's values.** A1.1 was measured 2026-08-26 and now stands re-confirmed on a
second date by a second lane. `cases/dafoam/curriculum_FADR/fadr_chain_driver.sh` re-reads both at
launch and **refuses (exit 2)** on any difference, so this is a live check and not only a record.

### A2.3 FOUR READS FROM FADR'S FREEZE THAT BELONG IN THE INVENTORY

All four were measured inside the images at zero compute while registering
`cases/dafoam/curriculum_FADR/` (freeze `eaa8061347bc6dce3e6d4a4d0563c7576e9e9e5d`):

1. **The DAFoam test harness is md5-IDENTICAL on both images** —
   `tests/runRegTests_DASimpleFoamForward.py` `e03630f44a016c3a8b23bcbc8b4b8128`,
   `tests/testFuncs.py` `fb11e90630aeba07c62c14afc5ed2ceb`,
   `tests/refs/DAFoam_Test_DASimpleFoamForwardRef.txt` `ac46aca2f10e68da43dbe74be0dd3c29`.
   **Consequence for every two-row item that runs the shipped tests: a divergence between the rows
   is located in the toolchain and can never be in the test.**
2. **The regression FIXTURE is absent from both images.** `tests/reg_test_files-main` does not exist
   on either; `tests/Allrun:9-14` fetches
   `https://github.com/DAFoam/reg_test_files/archive/refs/heads/main.tar.gz` **at run time**. The
   reference file (1) **ships in the image and cannot drift**; the **fixture is upstream's moving
   `main` branch and can**. FADR's retrieval is pinned by sha256 in
   `cases/dafoam/curriculum_FADR/FIXTURE_PROVENANCE.md`.
3. **The containers' default user is `uid 0`** — measured with `id`, not chosen — and **`bash -lc`
   as root does NOT source `/home/dafoamuser/dafoam/loadDAFoam.sh`**, which lives in `dafoamuser`'s
   tree. Without it `$WM_PROJECT` is unset and `python` (the conda interpreter at
   `/home/dafoamuser/dafoam/packages/miniconda3/bin/python`) is **not on `PATH`**, and `mpirun`
   dies with `Executable: python … 4 total processes failed to start`. **Measured both ways on a
   3-core cpuset at np = 4: without the source, 4 of 4 ranks fail to start; with it, 4 of 4 come
   up.** `tests/Allrun:3-6` refuses outright when `$WM_PROJECT` is unset, so the source is a
   **precondition of the shipped recipe**, not an addition to it. **Any driver here that runs
   `bash -lc` as uid 0 and does not source it will fail silently in the launcher rather than
   loudly in the solver.**
4. **`OMPI_ALLOW_RUN_AS_ROOT=1` and `OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1` are required** for any
   `mpirun` under `--user 0:0`. Exporting them leaves the command line unmodified, which matters
   when the requirement is to run an upstream recipe **verbatim**.

**Nothing here was sent, filed, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).
The only outbound act in the item that produced these readings was an **inbound** retrieval of
public upstream test material; **no image was pushed anywhere and none is installable by any
reader.**

---

## AMENDMENT 3 — 2026-08-31, dafoam lane. §3 AND §4 ARE STALE TO A COLD READER; §4's HEADING IS THE SENTENCE MOST LIKELY TO BE QUOTED AGAINST THE TRUTH. NO IN-PLACE BANNER WAS PLACED, AND THE SWEEP THAT DECIDED THAT IS RECORDED HERE.

**NOT FILED ANYWHERE.** Nothing in this amendment was sent, emailed, filed, uploaded, registered,
posted or commented (`CLAUDE.md` rule 7). No image was pushed to any registry; none is installable
by any reader. Zero compute: no solver, no container started. The only commands run for this
amendment were file reads, `git grep` / `grep` over the working tree, and two
`sudo -n docker inspect` reads of image **metadata**.

**Appended at the foot, never in place. `lines whose number changed above this section: 0`.**
This is *proved*, not asserted: the file was snapshotted before the append
(538 lines, 33,564 B, sha256 `9c0609832a6dc91ec2e9ae9cf88a31e7f14107c24c67d9a205c4ffca5f916ed1`,
byte-identical to the HEAD blob `905af3af` at `d680c0d3`), and after the append the first 538 lines
were re-hashed and compared against that snapshot. The comparison was itself controlled: a copy of
the snapshot with **one byte altered on non-blank line 151** (§4's heading) was fed to the same
reader, which reported DIFFERENT — so the "identical" reading below is a reading a live instrument
produced, not a no-op (`CLAUDE.md` rule 3).

**Version.** This file carries **no semantic version string anywhere** — not in its header, not in
Amendment 1, not in Amendment 2. Its only version marker is the **amendment ordinal**, and the bump
this amendment carries is therefore **Amendment 2 → Amendment 3**. No `vN.N` is invented here.

### A3.1 WHAT §3 AND §4 WERE TRUE OF, AND WHEN

**§3** (`:91`–`:147`) was measured **2026-08-21** from `sudo -n docker images` and lists **four**
images. **§4** (`:151`–`:181`) was measured the same day, and its heading reads, in full:

> `## 4. The IDWarp rotation patch is NOT in any container image`

On 2026-08-21 that heading was true of the box in every sense a reader could take it. It is **no
longer true as a plain reading**, and it has not been for some time: `dafoam-idwarp-rot:v1` exists
and carries a rebuilt IDWarp library. The heading survives only under the narrow reading §A1.3
already fixed — *the patch **source** is in no image* — and that reading is three sections below the
heading, in an amendment a cold reader has no reason to reach.

**The defect is therefore not self-contradiction. This file is internally consistent.** §A1.2
(`:435` ff.) and §A2.1 (`:476` ff.) both already declare §3 stale, and §A1.3 (`:449` ff.) already
separates the patch source from the rebuilt binary so that §4 is not contradicted. **The defect is
that a reader who reads §3 and §4 and stops concludes the exact opposite of the truth**, and §4's
heading is the single sentence in this file most likely to be lifted and quoted out of its context.

### A3.2 WHAT IS TRUE NOW — by digest and by library md5, the only discriminator that works

| row | image | digest | `libidwarp.so` md5 | size |
|---|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` | 491,344 B |
| **PATCHED-ROT** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` | 491,344 B |

**Both digests re-read live for this amendment at 2026-08-31T21:36:24Z** with
`sudo -n docker inspect --format '{{.Id}}' <tag>` — image metadata only, **no container started**.
Both returned exactly the values above. This is the **third** independent dated reading of the same
pair: A1.1 on 2026-08-26, A2.2 on 2026-08-27T19:03:34Z, this one on 2026-08-31.

**The two `libidwarp.so` md5s are NOT re-measured here and that is stated rather than glossed:**
reading the library inside an image requires **starting a container**, which this amendment's
zero-container scope forbids. They are inherited by citation from §A1.1 (`:409`–`:410`), which
records where each was measured — `cases/dafoam/MATRIX_CONTRIBUTION.md:113` and `:114`, and, printed
from inside the loading process, `cases/dafoam/ladder-a/A1/curriculum_D1/RESULTS.md:361-363`
(PATCHED, three containers) against `:364` (SHIPPED).

**Why the md5 and nothing else.** Both libraries report IDWarp **`2.6.2`** and both are **491,344
bytes**. The version string discriminates nothing and the file size discriminates nothing. §A1.1's
note at `:431`–`:433` already says this; it is repeated here because it is the reason §4's heading
misleads rather than merely dates.

### A3.3 WHY NO BANNER WAS PLACED AT THE HEAD OF §3 OR §4 — THE CITATION SWEEP

The obvious repair is a "STALE — see Amendment 1" banner at the head of §3 and §4. **It was
considered and rejected on measured evidence**, because it shifts every line number below it and
`CLAUDE.md` rule 6 exists precisely because other records cite this file **by line**.

A sweep for every reference to `TOOLCHAIN_INVENTORY.md` anywhere in the repository — tracked,
untracked and gitignored, across `cases/`, `docs/`, `scripts/`, `sdk/`, `verification/` and
`harness/` — found **74 tracked hits in 43 files** plus untracked hits in
`cases/dafoam/ladder-a/A2/curriculum_D14/PREREGISTRATION_DRAFT.md` and `docs/lab_state/dafoam.md`.
The reader was controlled with a positive plant (a file known to contain the token, fed to the same
reader, which returned it), so the sweep is not an uncontrolled zero.

**Of those, the citations that pin a LINE NUMBER — each target verified to resolve to what its
citing record says it resolves to:**

| citing record | cites | the cited line actually holds |
|---|---|---|
| `cases/dafoam/ladder-a/A2/curriculum_D14/PREREGISTRATION_DRAFT.md:41` | `:32` | §1's **pyHyp 2.6.1** row |
| `cases/dafoam/ladder-b/B3/decomposition_peak_rss/PREREGISTRATION.md:94` | `:124-129` | §3's *"Measured difference between the images"* md5/line-count table |
| `cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md:277` | `:128-129` | §3's stock and `subpclu:v1` md5 rows |
| `cases/dafoam/ladder-b/B3/decomposition_peak_rss/PREREGISTRATION.md:386` | `:142` | §3's `subpclu` patch row — **the sub-LU banner whose absence voids an arm** |
| `docs/LAB_STATE.md:4836` | `[:151]` | **§4's heading itself** |
| `cases/dafoam/ladder-a/A1/curriculum_SO1b/PREREGISTRATION.md:261` | `:409-410` | §A1.1's two digest rows |
| `docs/LAB_STATE.md:4774` | `:410`, `:409-410`, `:432` | the PATCHED row, both rows, the version-string note |
| **this file, Amendment 2** (`:481`) | `A1.1 (:405–:410)`, `A1.2 (:435 ff.)` | its own internal pointers |

**A banner at the head of §3 would break seven of these eight.** Only `:32` sits above §3 and would
survive. Two of the seven are load-bearing beyond bookkeeping: `:142` is cited by a
pre-registration as the authority for a **falsifier** (*absence of the sub-LU banner ⇒ the arm ran
stock ⇒ the arm is void*), and `:409-410` is the pair a registered toolchain freeze reads its
digests from. **Routing around a real citation to obtain a tidier document is not a repair**, and
this amendment does not do it.

**On executable checks, an honest negative.** `CLAUDE.md` rule 6 states that for frozen files
generally *"one citation sits inside an executable check."* **For THIS file the sweep found no such
check, and that is reported as a measured absence rather than assumed either way.** No script, test,
comparator or selftest in the repository reads `TOOLCHAIN_INVENTORY.md` at all — the sweep over
`*.py` and `*.sh` returns nothing. The nearest executable touch is `harness/teams.yaml:179`, which
names the file in the dafoam team's reading list; `harness/generate_agents.py:55-56` renders that
path and its `why` string into `.claude/agents/dafoam-supervisor.md:55`, and
`scripts/check_harness.py` regenerates and diffs. That check consumes the **path string only** — never
the file's content, never a line number — so it is unaffected by an append and would have been
unaffected by a banner too. `cases/dafoam/sweep_assert_under_O.py` and
`cases/dafoam/sweep_claim_prints_under_O.py` scan the dafoam folder scope but filter to `.py`/`.sh`,
so this `.md` is outside their population. **The line-number citations alone decide the repair; the
absent executable check neither strengthens nor weakens that.**

### A3.4 THE COLD-READER PROBLEM IN §4's HEADING IS **UNRESOLVED**, AND IS ABOVE THIS LANE'S LEVEL

**This amendment does not fix the defect it documents.** §4's heading still reads *"The IDWarp
rotation patch is NOT in any container image"*, and a reader who stops before the amendments will
still conclude the opposite of the truth. The only repairs that would fix it at the point of reading
— rewording the heading, or inserting a banner above it — are **edits to a frozen file that shift
lines other records cite**, and `CLAUDE.md` rule 6 forbids the lane from making that call.

**What is referred upward, and to whom.** The choice between (a) leaving §4's heading standing with
this amendment as its only correction, (b) amending the heading in place and re-pointing all seven
line-number citations in the same commit, or (c) some third instrument — is a supervisor's decision
at least, and arguably a charter question, since it trades rule 6's freeze against a record that
misleads a cold reader. **Until it is decided, the standing reading of this file is: §3's image list
is stale (§A1.2, §A2.1); §4's heading is true only of the patch SOURCE (§A1.3); and §A3.2 above is
the live two-row record.**

### A3.5 WHAT THIS AMENDMENT DOES NOT CHANGE

* **No gate, threshold, band, cap or label moves.** Nothing is retired. No statement above is
  struck, edited, reordered or renumbered.
* **§A1.3 stands exactly as written.** The distinction it draws — no image carries the patch
  **source**; `dafoam-idwarp-rot:v1` carries a **rebuilt binary** — is what keeps §4 technically
  true, and this amendment relies on it rather than replacing it.
* **§7's row for the W5 bind-mount route stands.** The image route is a later, separate way of
  reaching a patched IDWarp; rows measured on it cite `2927768a16ac`, not the mount.
* **`docs/dafoam/README.md:21`'s "388 lines" is not invalidated.** It describes this file's
  original body, which ends at `:388`; every line at and below `:389` is amendment material appended
  after that count was taken, and this append adds only below `:538`.
* **The three images §A1.2 recorded but did not characterise — `dafoam-idwarp-rot:v1`,
  `dafoam-subpclu:v2`, `dafoam-team:v1` — are still not characterised here beyond their hashes.**
  An identifier is not a description, and inventing one would be the defect §A1.2 exists to close.

---

## AMENDMENT 4 — 2026-08-31, dafoam lane, UNDER THE SUPERVISOR'S RULING. §3's AND §4's HEADINGS CARRY AN IN-PLACE SUPERSESSION MARKER APPENDED TO THE END OF THE EXISTING HEADING LINE. TWO LINES CHANGED, ZERO LINES MOVED, AMENDMENT 3's REFERRAL IS CLOSED.

**NOT FILED ANYWHERE.** Nothing in this amendment was sent, emailed, filed, uploaded, registered,
posted or commented (`CLAUDE.md` rule 7). Zero compute: no solver, no container, no image read — the
only commands run were file reads, `git grep` over tracked files, `sha256sum`, and the byte-level
comparison described below.

**Version.** This file still carries **no semantic version string anywhere**. Its only version marker
is the **amendment ordinal**, and the bump is therefore **Amendment 3 → Amendment 4**. No `vN.N` is
invented here (§A3 made the same finding and it is re-affirmed, not re-derived).

### A4.1 THE RULING THIS AMENDMENT EXECUTES, AND WHAT IT CHANGED

§A3.4 referred a decision upward: §4's heading misleads a cold reader, and the two obvious repairs
— rewording the heading, or inserting a banner above it — either destroy the original wording or
shift every line number below. **The supervisor ruled a third instrument**, which §A3.4 anticipated
as option (c): **append a supersession marker to the END of the existing heading line itself**, so
the original words survive byte-for-byte as a prefix, the line remains exactly one line, and **every
line number in the file is unchanged**. This is a strike-and-mark, not a rewrite.

**Exactly two lines were modified — `:91` and `:151` — and no others.**

**Line 91, BEFORE** (59 bytes):

````
## 3. Container images: what exists and what they differ by
````

**Line 91, AFTER** (344 bytes; the 59 bytes above are bytes 1–59 of it, unaltered):

````
## 3. Container images: what exists and what they differ by — **SUPERSEDED 2026-08-31: THIS IMAGE LIST IS STALE and is not the live record. See Amendment 4 (§A4), Amendment 3 (§A3.2), Amendment 2 (§A2.1) and Amendment 1 §A1.1–A1.3. Original heading text preserved verbatim above this marker; no line was inserted, moved or renumbered.**
````

**Line 151, BEFORE** (61 bytes):

````
## 4. The IDWarp rotation patch is NOT in any container image
````

**Line 151, AFTER** (485 bytes; the 61 bytes above are bytes 1–61 of it, unaltered):

````
## 4. The IDWarp rotation patch is NOT in any container image — **SUPERSEDED 2026-08-31: TRUE OF THE PATCH *SOURCE* ONLY. `dafoam-idwarp-rot:v1` DOES carry a rebuilt `libidwarp.so` (md5 `85f59e87253e0a71a813f64ca6e4c425`, digest `sha256:2927768a16ac…`). Do not quote this heading without this clause. See Amendment 4 (§A4), Amendment 3 (§A3.1–A3.2) and Amendment 1 §A1.3. Original heading text preserved verbatim above this marker; no line was inserted, moved or renumbered.**
````

**Why the correction is inside the marker and not merely a pointer.** §4's heading is quoted
elsewhere in the repository **by line** — `docs/LAB_STATE.md:4836` lifts it verbatim as `[:151]`.
A marker that said only *"see Amendment 3"* would leave the misleading sentence intact as the thing
a reader copies. Putting the narrow reading **in the same line** means the correction travels with
any future quotation of that line.

### A4.2 `lines whose number changed above this section: 0` — PROVED, NOT ASSERTED

The file was snapshotted before the edit: **684 lines, 44,436 B, sha256
`40d06340d692c1f50afaa8b05e92d77c20ae8853b27df3bfe87d8a7907a6a1c1`**, confirmed **byte-identical to
the HEAD blob `4174ca41` at `30d92060` by content comparison** (`git show HEAD:<path>` piped to a
file and `cmp`-ed — no index was consulted, so a stale or foreign index could not have produced a
false clean).

After the two markers were appended, the snapshot and the working file were compared **line by line
on raw bytes**. The result:

| quantity | before | after |
|---|---|---|
| total lines | **684** | **684** |
| lines differing, expected (`:91`, `:151`) | — | **2** |
| lines differing, unexpected | — | **0** |
| non-exempt lines compared | — | 683, of which 546 non-blank and identical |
| `:91` embedded newline / CR | — | none; exactly one line |
| `:151` embedded newline / CR | — | none; exactly one line |
| file still ends in LF | yes | yes |

So lines `1`–`90`, `92`–`150` and `152`–`684` are **byte-identical**, and the amendment material
below is appended at the foot, below `:684`. **`lines whose number changed above this section: 0`.**

**The comparison reader was controlled before its clean reading was believed** (`CLAUDE.md` rule 3).
A copy of the snapshot with **exactly one byte altered on non-blank line `:409`** — the `SHIPPED`
digest row, inside the very population being certified clean — was fed to the same reader, which
reported **`differing, UNEXPECTED: [409]` → DIFFERENT**. An unmodified copy read **IDENTICAL**, and
a copy with one line inserted above `:91` read **LINE COUNT DIFFERS**. Only then was "identical"
accepted as evidence.

**An honest note on a control that first misfired.** The initial plant flipped bit 0x20 of byte 12
of `:409`, which happened to be `*` (`0x2A`) — and `0x2A ^ 0x20 = 0x0A`, a **newline**. That plant
therefore split the line and was caught by the *line-count* path, proving nothing about the
*per-line byte* path it was meant to exercise. It was re-planted as a printable single-byte
substitution (`SHIPPED` → `SHIPPEE`) with three asserts — same length, exactly one byte differing,
no `0x0A` introduced — and only that second control licenses the table above. A control that passes
for the wrong reason is not a control.

### A4.3 WHY AN IN-PLACE SAME-LINE MARKER AND NOT A BANNER — THE SEVEN CITATIONS

§A3.3 swept the repository and found **eight line-number citations into this file, seven of them
below §3's heading at `:91`**. A banner line inserted at the head of §3 shifts all seven. Two are
load-bearing beyond bookkeeping: **`:142`** is cited by
`cases/dafoam/ladder-b/B3/decomposition_peak_rss/PREREGISTRATION.md:386` as the authority for a
**falsifier that voids an arm** (absence of the sub-LU banner ⇒ the arm ran stock ⇒ the arm is
void), and **`:409-410`** is where a registered toolchain freeze
(`cases/dafoam/ladder-a/A1/curriculum_SO1b/PREREGISTRATION.md:261`) reads its digests. The same-line
marker shifts none of them, which is its entire virtue.

**All eight targets were re-verified after the edit and every one still resolves to what its citing
record claims:**

| cites | still holds |
|---|---|
| `:32` | §1's **pyHyp 2.6.1** row — unchanged |
| `:124-129` | §3's md5 / line-count table — unchanged |
| `:128-129` | stock and `dafoam-subpclu:v1` md5 rows — unchanged |
| `:142` | the `subpclu` patch row and its **sub-LU banner falsifier** — unchanged |
| `:151` | §4's heading — **unchanged as a prefix, plus the supersession marker** |
| `:409-410` | §A1.1's two digest rows, both sha256s and both md5s — unchanged |
| `:432` | the "both report `2.6.2`, both 491,344 B" note — unchanged |
| `:481` | Amendment 2's internal pointers `A1.1 (:405–:410)`, `A1.2 (:435 ff.)` — unchanged |

**`:151` is the one target whose bytes changed, and it changed in the strictly informative
direction.** `docs/LAB_STATE.md:4836` cites it for the proposition *"§4's heading literally reads …
which is true only of the patch SOURCE"*. That citation is **more** true after the edit than before:
the line now carries both the heading it quotes and the correction the citing record supplies from
outside. No citing record is invalidated; one is made self-contained.

**The absent executable check, re-measured, not inherited.** §A3.3 reported as a measured negative
that no script, test, comparator or selftest reads this file. **This lane re-ran that check rather
than inheriting it**, because the safety of the edit depends on it: `git grep -ln TOOLCHAIN_INVENTORY
-- '*.py' '*.sh'` returns **nothing**, and the same reader run over `docs/*` returns six files — so
the zero is a **live zero from an instrument shown able to return hits**, not an uncontrolled one.
No executable consumer exists; nothing can break on the heading string.

### A4.4 A CONSEQUENCE THAT IS DISCLOSED RATHER THAN QUIETLY FIXED

**§A3.1 block-quotes §4's heading verbatim at `:568`**, introduced by the words *"its heading reads,
in full"*. After this amendment that quotation records the heading's **pre-marker** text. **Line 568
is NOT edited** — Amendment 3 is itself frozen material and `CLAUDE.md` rule 6 forbids rewriting it;
originals are struck, never rewritten. It stands as the dated historical record of what `:151` read
between 2026-08-21 and 2026-08-31, and this section is the strike that marks it as such. A reader
comparing `:568` with `:151` sees exactly the change this amendment made, which is the intended
behaviour of an append-only record.

### A4.5 WHAT THIS AMENDMENT DOES NOT CHANGE

* **No gate, threshold, band, cap, label or verdict moves.** Nothing is retired, re-graded or
  re-scored. No run, arm or row changes status. This is a documentation repair with no numerical
  consequence anywhere in the lab.
* **No original wording is deleted or reworded.** Both headings survive byte-for-byte as the prefix
  of their own line. Nothing above `:684` is struck, edited, reordered or renumbered except the two
  appends recorded in §A4.1.
* **§A1.3 stands exactly as written** and remains the section that makes §4's heading technically
  true; `:151`'s marker restates its distinction rather than replacing it.
* **§A3.2 remains the live two-row record**, and its digests are not re-measured here — this
  amendment started no container and inherits them by citation.
* **`docs/dafoam/README.md:21`'s "388 lines" is still not invalidated.** It describes the original
  body ending at `:388`; this append adds only below `:684`, and the two markers add no lines at all.

### A4.6 AMENDMENT 3's REFERRAL IS CLOSED

§A3.4 referred upward the choice between (a) leaving §4's heading standing, (b) amending it in place
and re-pointing all seven citations, and (c) some third instrument. **The supervisor chose (c), and
this amendment executes it.** Option (b) — the one that would have required re-pointing seven
citations — was **not** taken, and no citation needed re-pointing.

**The referral opened at §A3.4 is hereby CLOSED.** The cold-reader defect it recorded as
**UNRESOLVED** is **RESOLVED at the point of reading**: a reader who reads §3 or §4 and stops now
reads the supersession marker in the same line as the heading, and cannot take away the opposite of
the truth. **The standing reading of this file is now: §3's image list is stale (§A1.2, §A2.1,
and the marker at `:91`); §4's heading is true only of the patch SOURCE (§A1.3, and the marker at
`:151`); and §A3.2 is the live two-row record.**
