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

## 3. Container images: what exists and what they differ by

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

## 4. The IDWarp rotation patch is NOT in any container image

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
