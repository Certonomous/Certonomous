# `dafoam-team:v1` — Ladder B's pinned image

**Written 2026-08-21 by DAFoam team Lane B**, against the supervisor's relay of Sanaa's
2026-08-21 approvals (item 3). Nothing here is filed, sent, uploaded or pushed; the image is
local to this box, as every other patched image in this lab is.

**Purpose.** Ladder B's recorded numbers come from three tags whose relationship is recoverable
only by reading `docs/dafoam/TOOLCHAIN_INVENTORY.md` §6e, and two of the three were built by a
hand-run `docker commit` in sessions whose scratch trees no longer exist. This directory builds
the **union of both DAFoam patches from the stock image in one committed `Dockerfile`**, so the
team image's provenance is this file plus the two `.patch` files beside it and nothing else.

---

## 1. What it is, and what it is not

| | |
|---|---|
| **base** | `dafoam/opt-packages:latest`, digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` — the image every published number in this lab was measured on |
| **patch 1** | `DALinearEqn_subpclu.patch` — `DAFOAM_SUBPC_TYPE=lu` switches the ASM sub-block PC from ILU to complete LU. **Off by default** |
| **patch 2** | `DALinearEqn_kspopts.patch` — relocates `KSPSetFromOptions(ksp)` from line 138 to the end of `createMLRKSP`, so PETSc runtime options act as overrides of `daOptions` instead of being silently discarded. **Inert with no options set** |
| **what it is NOT** | It does **not** carry the IDWarp rotation fix — that lives only at `/home/ubuntu/certonomous-runs/W5-patch/idwarp` and in `dafoam-idwarp-rot:v1`, and IDWarp ships with no Fortran sources in any DAFoam image (`TOOLCHAIN_INVENTORY.md` §4). It does **not** touch the `cellLimited` limiter or the decomposition defect. **This is not "the fixed toolchain"; it is two defects made reachable** |

## 2. Cost, estimated BEFORE the build

Basis: the `subpclu` build's own measured figures on this box — **284 s wall, 18.93 core-min**
for three `wmake` targets from the same base (`../subpclu/BUILD.md` §4.1) — which came in at
54 % of its own estimate.

| line | value | basis |
|---|---|---|
| patch + verify layers | ~25 s | two `patch` calls instead of one |
| compile, three `wmake` targets | ~120 s container CPU | W4 §7, *"~2 min of container CPU across three wmake targets"* |
| layer materialisation + docker overhead | ~120 s | measured on the `subpclu` build |
| smoke test: B3 arm P, one adjoint solve | ~280 s | arm P measured 279 s |
| **predicted wall** | **~545 s** | sum |
| **predicted billed** | 4 cores x 545 s = **36.3 core-min** | cores x wall, full occupancy for the whole clock |
| **with 100 % contingency on the build half** | **55 core-min** | first-attempt risk on applying two patches in sequence |
| **in dollars** | 55 core-min = 0.917 core-h x \$0.0513 = **\$0.047** | supervisor's cost basis |

**55 core-min < the 60 core-min bar, and \$0.047 << \$25 -> BUILD.** Cores capped at 4 via
`--cpuset-cpus 0-3`, `--memory=12g`, foreground, `timeout`-bounded. No background process;
nothing to kill.

## 3. Gates, fixed before the build

| gate | prediction, fixed now |
|---|---|
| **G1** | Build completes; all three libraries relink — `libDASolver.so`, `libDASolverADR.so`, `libDASolverADF.so`, each larger than stock by the added string literals |
| **G2a** | `DALinearEqn.C` line count = **547**. Arithmetic: stock **507**, + **32** for the subpclu v2 block (19 lines of the v1 block + 13 of the B-1 warn block, measured: `subpclu:v2` is 539), + **8** for kspopts (measured: `subpclu:v1` 526 -> `kspopts:v1` 534) |
| **G2b** | `DAFOAM_SUBPC_TYPE` occurrence count = **4** — `subpclu:v2`'s 4; the kspopts patch adds none |
| **G2c** | Exactly **one** `KSPSetFromOptions` site, and it is **after** the `PCASMGetSubKSP` block loop, not at line 138 |
| **G2d** | **The cross-check that makes this a union and not a third lineage:** the in-image md5 of `DALinearEqn.C` must equal the md5 produced by applying the same two patches in the same order to the stock file **on the host**. If they differ, the image contains an undocumented edit |
| **G3** | `libDASolver.so` `dlopen`s, `pyDAFoam` imports, `DASimpleFoam` symbol present, and both the PCLU banner string and the B-1 warn string are present in the library |
| **G4** | **Behaviour-neutral by default.** `DAFOAM_SUBPC_TYPE` unset and no `PETSC_OPTIONS`: B3's exact configuration returns `-9` at iteration 0 with residual **`7.091590452305e-04`** to all 13 digits, cold-start continuity error **`9.30211816115683e-06`**, primal **1580** iterations, and **no sub-LU banner** |
| **G5** | **Smoke test, the one the supervisor named:** with `DAFOAM_SUBPC_TYPE=lu`, B3 arm P reproduces **`PetscConvergedReason: 2`**, **667** iterations, and iteration-0 residual `7.091590452305e-04` bit-identical. One adjoint solve |

**G4 and G5 are the whole argument**, and they are two rows on purpose: an image that carries
two patches has to be shown to change nothing until it is asked to, and then to change exactly
the recorded thing.

## 4. Actual build output

*(appended after the build; nothing has been appended yet)*

**Status at writing: NOT BUILT.** The build is registered, costed and gated above, and it did
not launch because this lane's four cores were held by a still-running bounded chain and the
host carried 20 unpinned `simpleFoam` processes from another family at load average 12.4. A
`docker build` under those conditions would have measured contention, not compile time, and
would have made the 36.3 core-min estimate meaningless. **The launch condition is load average
< 10 and `MemAvailable` >= 12 GiB, checked in a bounded loop.**

## 5. Reproduce it

```
cd cases/dafoam/patched_build/team
sudo -n docker build --cpuset-cpus 0-3 -t dafoam-team:v1 -f Dockerfile .
```

Requires `dafoam/opt-packages:latest` present locally at the digest above. Nothing is pulled
and nothing is pushed. **Record the resulting image ID in `docs/dafoam/README.md` §5's images
table before quoting any number measured on it** (`DAFOAM_CHARTER.md` §6: a version string is
not an identity).
