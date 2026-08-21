# `dafoam-subpclu:v2` — reproducible build of the sub-LU adjoint unblock

**Written 2026-08-21 by DAFoam team Lane B, Phase 1 task 1.** Nothing here is filed,
sent, uploaded or pushed; the image is local to this box, as `v1` was.

Purpose: `cases/dafoam/subpclu_patch/` holds only a `.patch`. The image that produced
every recorded sub-LU number — `dafoam-subpclu:v1` — was built by a hand-run
`docker run` / `docker commit` sequence in a session whose scratch tree no longer
exists. This directory turns that sequence into a `Dockerfile` that anyone can re-run.

---

## 1. How `v1` was built, reconstructed from the frozen records

`cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §4 is the only recipe on the record:

```
docker run -d --name dafoam-build dafoam/opt-packages:latest sleep infinity
# patch src/adjoint/DALinearEqn/DALinearEqn.C (see repo diff in this commit)
# then, inside the container, for each of the three AD modes:
source /home/dafoamuser/dafoam/loadDAFoam.sh          # original
cd repos/dafoam && wmakeLnInclude src/adjoint && (cd src/adjoint && wmake -j 8)
# ADR and ADF: sed WM_AD_MODE in OpenFOAM-AD/etc/bashrc, re-source, wmake again
docker commit dafoam-build dafoam-subpclu:v1
```

Facts the records fix, each cited:

| fact | value | source |
|---|---|---|
| file patched | `src/adjoint/DALinearEqn/DALinearEqn.C`, at line 266 `PCType localPCType = PCILU;` | `W4_ADJOINT_PC_UNBLOCK.md` §4; `docs/dafoam/TOOLCHAIN_INVENTORY.md` §"What each patch does" |
| in-container repo root | `/home/dafoamuser/dafoam/repos/dafoam` | patch file header |
| build targets | **three** AD modes — original, ADR, ADF; `Make/` carries `linux64GccDPInt32Opt`, `…OptADR`, `…OptADF` | measured in-image this session |
| compile time | *"~40 s of compile"*; *"All three `libDASolver*.so` relink in seconds"*; *"Compile time (~2 min of container CPU across three wmake targets)"* | `W4_ADJOINT_PC_UNBLOCK.md` §4, §7 |
| ordering trap | *"`set -e` before sourcing the OpenFOAM environment kills the shell — source first."* | ibid. §4 (a lost first attempt) |
| all three libs were rebuilt | *"All three `libDASolver*.so` … contain the `DAFOAM_SUBPC_TYPE` string, so all three were rebuilt from the patched source."* | `VERIFICATION_cbfs_unblock_supervisor_sweep.md` §1 |
| nothing else moved | *"An md5 sweep of **every** `.C`/`.H` under `repos/dafoam/src` in both images shows exactly two changed files: `DALinearEqn.C` and its `lnInclude` copy."* | ibid. |
| image never pushed | *"the image is local only, nothing pushed"* | `W4_ADJOINT_PC_UNBLOCK.md` §4 |

Measured in-image this session (`sudo -n docker run --rm dafoam/opt-packages:latest …`):
libraries live at `/home/dafoamuser/dafoam/OpenFOAM/sharedLibs/` — `libDASolver.so`
(9,111,056 B), `libDASolverADR.so` (11,415,712 B), `libDASolverADF.so` (9,534,464 B),
all dated Jul 12. `loadDAFoam.sh` sources `OpenFOAM-v2506/etc/bashrc`, which sets
`WM_AD_MODE=""`; `OpenFOAM-AD/etc/bashrc:111` sets `WM_AD_MODE=ADF`. The ADR/ADF
builds therefore need `OpenFOAM-AD/etc/bashrc` sourced **on top of** `loadDAFoam.sh`,
with `WM_AD_MODE` sed to the wanted mode — which is what the Dockerfile does.

## 2. Cost estimate, made and recorded BEFORE the build ran

| line | value | basis |
|---|---|---|
| compile, three `wmake` targets | ~120 s container CPU | W4 §7, *"~2 min of container CPU across three wmake targets"* |
| patch + verify layers | ~20 s | trivial file ops |
| docker layer materialisation | ~60 s | RUN layers write only the changed files (~30 MB of `.so`/`.o`/`lnInclude`), not a 10 GB copy; the stock image is 9.93 GB disk / 2.1 GB content |
| docker overhead, pull-free (image already local) | ~60 s | — |
| **predicted wall** | **~260 s ≈ 4.3 min** | sum |
| **predicted billed cost** | **4 cores × 4.3 min = 17.3 core-min** | lab convention: cores × wall, full occupancy for the whole clock |
| **with 100 % contingency for one failed layer** | **35 core-min** | first-attempt risk on the ADR/ADF env |
| **in dollars** | 35 core-min = 0.583 core-h × \$0.0513 = **\$0.030** | supervisor's cost basis |

**35 core-min < the 60 core-min bar, and \$0.03 ≪ \$25 → BUILD.** Cores capped at 4
via `--cpuset-cpus 0-3` (Lane A holds 4–7). Foreground, bounded by `timeout`. No
background process; nothing to kill.

## 3. The verification gates, fixed before the build

**G1 — the build completes and all three libraries relink.** Each `wmake` layer prints
its `ls -la` of the produced `.so`.

**G2 — md5 equality with `v1` is PREDICTED TO FAIL, by construction, and that is a
PASS of the corrected gate.** The patch file on disk carries its own provenance header:

> **NEXT-REBUILD DELTA (finding B-1):** the `else if` warn block for unrecognized
> non-empty `DAFOAM_SUBPC_TYPE` values is NEW in this patch and is **NOT** in the
> currently built `dafoam-subpclu:v1` library.

So `v2 = v1 + the B-1 warn block`. Lane A's `TOOLCHAIN_INVENTORY.md` §6e measured
`v1` at md5 `89e71ca2db5d80c06b1eda070ffc7a1b`, **526 lines**, 3 `DAFOAM_SUBPC_TYPE`
occurrences; stock at `f6a89e33b0f4772a0563cb0c8633ac48`, **507 lines**, 0.
The substitute gates, fixed now:

- **G2a** `v2` line count = **539** (507 stock + 32 added lines; counted directly from the patch body — 19 lines in the v1 block, 13 in the B-1 warn block).
- **G2b** `v2` `DAFOAM_SUBPC_TYPE` occurrence count = **4** (v1's 3, plus the warn line).
- **G2c** `diff v1 v2` on `DALinearEqn.C` shows **only** the 13-line B-1 warn block —
  nothing else. This is the real reproducibility statement: the numeric path is
  byte-identical to the image that produced every recorded sub-LU number.
- **G2d** applying the same patch to the stock file **on the host** yields an md5 equal
  to the in-image `v2` md5 — i.e. the image is exactly stock + this patch file.

**G3 — `DASimpleFoam` loads** in `v2`, in the real (non-AD) mode.

**G4 — behaviour-neutral by default**: with `DAFOAM_SUBPC_TYPE` unset, `v2` must
reproduce the `-9` at iteration 0 with the recorded 13-digit residual
`7.091590452305e-04`. This is arm S of the re-verification and is graded in
`cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md`, not here.

---

## 4. Actual build output

*(appended after the build; see below)*
### 4.1 The build command and its result

```
$ uptime
 16:02:40 up 41 min,  1 user,  load average: 0.16, 0.17, 0.27          # load 0 < 10, proceed

$ cd cases/dafoam/patched_build/subpclu
$ timeout 1500 sudo -n docker build --cpuset-cpus 0-3 -t dafoam-subpclu:v2 -f Dockerfile .
...
Successfully built 8352629516bb
Successfully tagged dafoam-subpclu:v2

=== rc=0 wall=284s core_min=18.93 ===
```

**Measured 284 s wall / 18.93 core-min against the 35 core-min estimate — 54 % of it,
inside the un-contingency'd 17.3 figure to 9 %.** At \$0.0513/core-hour: **\$0.016.**

### 4.2 Gate results

| gate | predicted (before the build) | measured | verdict |
|---|---|---|---|
| **G1** build completes, three libraries relink | 3 × `.so` | `libDASolver.so` 9,111,104 B; `libDASolverADR.so` 11,415,760 B; `libDASolverADF.so` 9,534,512 B — each **+48 B** over stock, the added string literals. `WM_OPTIONS` echoed `linux64GccDPInt32OptADR` and `…OptADF` in the two AD layers | **PASS** |
| **G2a** `v2` line count | **539** | **539** | **PASS** |
| **G2b** `DAFOAM_SUBPC_TYPE` occurrences | **4** | **4** | **PASS** |
| **G2c** `diff v1 v2` = only the 13-line B-1 warn block | 13 added lines, nothing else | `285a286,298`, **13 added lines**, all inside the `else if` warn block; **zero other differences** | **PASS** |
| **G2d** host-patched stock md5 = in-image `v2` md5 | equal | both `5b3159f88dbefcf7c52bd888401d097f` | **PASS** |
| **G3** `DASimpleFoam` loads | loads | `libDASolver.so dlopen: OK`; `PYDAFOAM import: OK`; `DASimpleFoam symbol present: True`; PCLU banner and B-1 warn strings both present in the library | **PASS** |
| **G4** behaviour-neutral by default | `-9`, residual `7.091590452305e-04` | graded in `ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md` arm S | see there |

### 4.3 The md5 table, extended

Lane A's `TOOLCHAIN_INVENTORY.md` §6e values reproduced exactly this session, and `v2` added:

| image | `DALinearEqn.C` md5 | lines | `DAFOAM_SUBPC_TYPE` |
|---|---|---|---|
| `dafoam/opt-packages:latest` | `f6a89e33b0f4772a0563cb0c8633ac48` | 507 | 0 |
| `dafoam-subpclu:v1` | `89e71ca2db5d80c06b1eda070ffc7a1b` | 526 | 3 |
| **`dafoam-subpclu:v2`** | **`5b3159f88dbefcf7c52bd888401d097f`** | **539** | **4** |

### 4.4 What this establishes, stated at the precision the evidence supports

**The reproducibility claim that matters is G2c, not md5 equality.** `v2` is not
bit-identical to `v1` and was predicted not to be. What G2c shows is stronger than a
hash match would have been on its own: the only code `v2` adds beyond `v1` is an
`else if` branch that is entered **only when `DAFOAM_SUBPC_TYPE` is set to a non-empty
value other than `lu`** — a condition false in both arms of every sub-LU run ever
recorded (`unset` for the regression control, `lu` for the treatment). **The numeric
path of `v2` is byte-identical to the image that produced `reason 2 / 667 iterations`
and the FD-verified gradient.**

G2d closes the other half: the image is exactly `dafoam/opt-packages:latest` plus the
committed patch file, with no undocumented edit — the thing a `docker commit` from a
long-gone scratch tree could not previously demonstrate.

**What this does NOT establish.** It does not show `v2` reproduces `v1`'s *numbers* —
that is arm S and arm P of the re-verification, and it is a separate measurement.
It does not touch the IDWarp rotation patch (Lane A's, `patched_build/`), and it does
not build a `v2` of anything else.

### 4.5 Reproduce it

```
cd cases/dafoam/patched_build/subpclu
sudo -n docker build --cpuset-cpus 0-3 -t dafoam-subpclu:v2 -f Dockerfile .
```

Requires `dafoam/opt-packages:latest` present locally
(digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`).
Nothing is pulled and nothing is pushed.
