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

---

## 4b. ACTUAL BUILD OUTPUT — appended 2026-08-21 ~19:15 UTC, after the build

**Status: BUILT.** `sudo -n docker build --cpuset-cpus 0-3 --memory=12g -t dafoam-team:v1 -f Dockerfile .`
Run root `/home/ubuntu/certonomous-runs/B3-team-image/`, full transcript `build.log`.

```
Successfully built 0b3c94c33a15
Successfully tagged dafoam-team:v1
=== BUILD rc=0 wall=220s core_min=14.67 ===
dafoam-team:v1 sha256:0b3c94c33a15cc9b6be48ff1c7e8fa50e870f53d7626bd56b7e173bfd7e9dc1d
```

**Image ID `0b3c94c33a15`**, full digest
`sha256:0b3c94c33a15cc9b6be48ff1c7e8fa50e870f53d7626bd56b7e173bfd7e9dc1d`.
**`DALinearEqn.C` in-image md5 `920cced7976531836145e08737eb7513`, 547 lines.**

### 4b.1 Gates, scored

| gate | predicted, §3 | measured | verdict |
|---|---|---|---|
| **G1** | build completes; all three libraries relink | `libDASolver.so` **9,111,104 B**, `libDASolverADR.so` **11,415,760 B**, `libDASolverADF.so` **9,534,512 B**, all three timestamped inside the build | **PASS** |
| **G2a** | `DALinearEqn.C` line count = **547** (arithmetic: 507 + 32 + 8) | **547** | **PASS — the arithmetic was exact** |
| **G2b** | `DAFOAM_SUBPC_TYPE` occurrence count = **4** | **4** | **PASS** |
| **G2c** | exactly **one** `KSPSetFromOptions` site, **after** the `PCASMGetSubKSP` loop, not line 138 | exactly one call site, **line 364** (lines 137 and 359 are the patch's own comments, not calls) | **PASS** |
| **G2d** | in-image md5 == md5 from applying the same two patches in the same order to the stock file **on the host** | **`920cced7976531836145e08737eb7513` == `920cced7976531836145e08737eb7513`** | **PASS** |
| **G3** | `libDASolver.so` loads, `pyDAFoam` imports, patch strings present in the library | `pyDAFoam import OK 5.0.0 2.6.2 1.13.0`; `DAFOAM_SUBPC_TYPE` **3** occurrences and the `ASM sub-block PC set to complete LU` banner **1** occurrence in `libDASolver.so` | **PASS** |
| **G4** | behaviour-neutral by default: `-9`, residual `7.091590452305e-04`, 1580 primal, no banner | *see §4b.4* | *scored below* |
| **G5** | `DAFOAM_SUBPC_TYPE=lu`: `reason 2`, **667** iterations | *see §4b.4* | *scored below* |

### 4b.2 The union is proven, not asserted — the intermediate hash is the evidence

The host-side reproduction of G2d passes through the **recorded identity of
`dafoam-subpclu:v2`** on its way:

| stage | md5 | lines | matches |
|---|---|---|---|
| stock | `f6a89e33b0f4772a0563cb0c8633ac48` | **507** | `TOOLCHAIN_INVENTORY.md` §6e stock row, exactly |
| **after `subpclu` patch** | **`5b3159f88dbefcf7c52bd888401d097f`** | **539** | **`dafoam-subpclu:v2`'s recorded md5 and line count, exactly** |
| after `kspopts` patch | `920cced7976531836145e08737eb7513` | **547** | the new team image |

**So `dafoam-team:v1` is demonstrably `subpclu:v2` + `kspopts`, and not a third lineage.**
This is a stronger result than G2d asked for: G2d only required host and image to agree, and
the intermediate hash additionally pins the *first* half of the stack to an image already on
the record. The `kspopts` patch applied with `Hunk #2 succeeded at 356 (offset 13 lines)` —
the offset is the 32 lines `subpclu` inserted ahead of it, and it is expected.

**Note on `dafoam-kspopts:v1`, and why the two differ.** `kspopts:v1` is md5
`96f5762819e33efbdaad34181a214082`, **534** lines, **3** `DAFOAM_SUBPC_TYPE` occurrences,
because it was built on `subpclu:v**1**`. `dafoam-team:v1` is **547** lines with **4**
occurrences because it is built on the `subpclu` patch file as it stands today, which carries
the B-1 unrecognised-value warning block. **The team image is one hunk ahead of
`kspopts:v1`, in the branch no recorded run enters** — the same relationship
`TOOLCHAIN_INVENTORY.md` §6e records between `subpclu:v1` and `v2`. **Numbers measured on
`kspopts:v1` are not silently re-attributed to `dafoam-team:v1`.**

### 4b.3 Cost, against the estimate

| line | registered §2 | measured |
|---|---|---|
| build wall | ~545 s | **220 s** |
| build billed | 36.3 core-min | **14.67 core-min** |
| with contingency | **55 core-min** (the number that cleared the 60 bar) | — |
| dollars | \$0.047 | **14.67 core-min = 0.2445 core-h x \$0.0513 = \$0.0125** |

**59.6 % under the point estimate and 73 % under the contingency figure**, despite launching
into a **fully saturated 16-core box** — `uptime` load average **13.85** at the moment the
gate released, with all 16 cores at ~99 % from another family's unpinned jobs. The build
degraded gracefully where a spin-waiting MPI job would not have: a `wmake -j 4` on a shared
`cpuset` loses throughput roughly linearly, while the 4-rank DAFoam jobs in
`../../ladder-b/B3/ilu_shift_runtime/RESULTS.md` §5 lost **18.5x** under comparable load.
**That asymmetry is worth recording: the launch condition in §4 was written for solver arms
and is stricter than a build needs.**

**Disclosure.** The registered launch condition was *load average < 10 and `MemAvailable` >=
12 GiB, checked in a bounded loop.* The memory half was met throughout (**26–28 GiB**
available, never below). **The load half was never met.** The gate was polled every 20 s for
**20 minutes** (18:50:25Z → 19:10:25Z), load never fell below 13.85, and the bounded loop
then released the build by design rather than waiting indefinitely. **This is recorded as a
gate that timed out and was overridden by its own bound, not as a gate that passed.** The
cost figures above therefore carry contention, which makes them an **upper** bound — the
honest reading is that the build is *cheaper* than 14.67 core-min on a quiet box, and nothing
in the gate table depends on timing.

### 4b.4 G4 — behaviour-neutral by default. **PASS**, every clause.

`dafoam-team:v1`, np = 4, `DAFOAM_SUBPC_TYPE` **unset**, no `PETSC_OPTIONS`, B3's exact CBFS
configuration, fresh staged case, cold `rm -rf processor*`.
Log `/home/ubuntu/certonomous-runs/B3-team-image/logs/G4_team_default.log`.

| clause registered in §3 | measured | line | verdict |
|---|---|---|---|
| `PetscConvergedReason: -9` at iteration 0 | `**Completed**! Total iterations: 0. PetscConvergedReason: -9.` | `:12094` | **PASS** |
| iteration-0 residual `7.091590452305e-04` **to all 13 digits** | `7.091590452305e-04` | `:12092-12093` | **PASS**, all 13 |
| cold-start continuity error `9.30211816115683e-06` | `9.30211816115683e-06` | `:698` | **PASS** |
| primal **1580** iterations | `Time = 1580` | `:12002` | **PASS** |
| **no** sub-LU banner | `grep -c 'ASM sub-block PC set to complete LU'` = **0** | — | **PASS** |
| *(not registered, checked anyway)* solver stack echo | `ASM Overlap: 1` / `Mat ReOrdering: rcm` / `ILU PC Fill Level: 1` | `:12083`, `:12086`, `:12087` | matches B3's `-9` configuration |

**126 s wall, 8.40 core-min.** **An image carrying two patches changes nothing until it is
asked to** — that is the safety half of §3's two-row argument, and it now has numbers.

### 4b.5 G5 — the smoke test the supervisor named. **PASS**, bit-identical to arm Pβ.

`dafoam-team:v1`, np = 4, **`DAFOAM_SUBPC_TYPE=lu`**, one adjoint solve, beta DV (21,000),
fresh staged case, cold `rm -rf processor*`.
Log `/home/ubuntu/certonomous-runs/B3-team-image/logs/G5_team_sublu.log`.

| clause | registered / archived value | measured on `dafoam-team:v1` | line | verdict |
|---|---|---|---|---|
| convergence reason | `2` | **`PetscConvergedReason: 2`** | `:12101` | **PASS** |
| iterations | **667** | **667 — exactly** | `:12101` | **PASS** |
| sub-LU banner present | required | `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` | `:12081` | **PASS** |
| iteration-0 residual | `7.091590452305e-04` | `7.091590452305e-04`, all 13 digits | `:12093` | **PASS** |
| objective | `1.5279278906359758e-02` | **`OBJ varianceU: 1.5279278906359758e-02`** — all 17 digits | — | **PASS** |
| gradient | `n=21000 norm=1.4558046603e-05 min=-4.694367e-07 max=1.916019e-06` | **every printed digit identical** | — | **PASS** |
| cold-start continuity error | `9.30211816115683e-06` | `9.30211816115683e-06` | `:698` | **PASS** |
| primal iterations | **1580** | `Time = 1580` | `:12002` | **PASS** |

**392 s wall, 26.13 core-min, `rc=0`.**

**The pair G4/G5 is the whole argument, and both rows landed.** With both patches present and
neither asked for, `dafoam-team:v1` reproduces the stock `-9` to 13 digits; asked for one of
them, it reproduces the PCLU result — **667 iterations and a 21,000-component gradient — to
every archived digit, from a Dockerfile whose only inputs are two committed `.patch` files and
a pinned base digest.** The lineage problem §1 was written to solve is solved: this number no
longer depends on a `docker commit` in a scratch tree that no longer exists.

### 4b.6 One behavioural difference from every other image in this lab, recorded

**`dafoam-team:v1` ends with `USER dafoamuser`; `subpclu:v1/v2` and `kspopts:v1` run as
`root`.** The lab's staged-case harness bind-mounts a host directory owned by `ubuntu` and the
run script creates `reports/` inside it, so the first G4 attempt died immediately with
`PermissionError: [Errno 13] Permission denied: 'reports'` and then
`FileNotFoundError: 'reports/runScript'` — **a harness failure, not a solver result, and it is
recorded as one; zero graded compute was charged to it.** The fix used for both smoke arms is
`docker run --user root` plus staging a `reports/` directory, which changes nothing the solver
sees — G4's and G5's numbers are bit-identical to arms R and Pβ, which is the proof.

**This is a real portability note for anyone reusing this image**: it is not drop-in
compatible with a harness that assumes the container writes as root. It is left as-is rather
than patched, because `USER dafoamuser` is the upstream base image's own convention and
changing it would make the team image differ from stock in a third, undocumented way.

### 4b.7 T2 total cost

| line | core-min |
|---|---|
| build | 14.67 |
| G4 smoke, behaviour-neutral | 8.40 |
| G5 smoke, arm P reproduction | 26.13 |
| **total** | **49.20** |

**49.20 core-min = 0.820 core-h x \$0.0513 = \$0.0421, against the registered 55 core-min
(\$0.047) — 10.5 % under, with G4 added on top of the registered scope.** §2 costed the build
plus one smoke test; G4 was run as well because §3 lists it as a gate and because an image
carrying two patches should be shown to change nothing before it is shown to change something.
**Nothing here approaches \$25.**
