# Building the lab's custom OpenFOAM solvers and turbulence libraries

Four compiled artifacts sit outside this repository, in the OpenFOAM *user*
directory, and published results name them by name. Until 2026-08-17 no
procedure for rebuilding them was written down anywhere: a search for
`WM_PROJECT_USER_DIR` or `OpenFOAM/ubuntu-v2606` across `sdk/`, `scripts/` and
`docs/` returned zero hits. This page is that procedure.

This is **not** the OpenFOAM *adapter* (the Python-driven cylinder missions).
That is `docs/OPENFOAM.md`, and nothing here is needed to run it.

---

## 1. What gets built, and from which source

| Artifact | Kind | Source directory | Build command |
|---|---|---|---|
| `rhoCentralFoamBounded` | executable | `demo-output/website/campaign/F4_runs/swbli_cylflare/rhoCentralFoamBounded_src/` | `wmake` |
| `libspartaTurbulenceModels.so` | library | `sdk/openfoam/sparta/spartaTurbulenceModels/` | `wmake libso` |
| `libkOmegaSSTQCRTurbulenceModels.so` | library | `sdk/openfoam/qcr/kOmegaSSTQCR/` | `wmake libso` |
| `kCorrectiveFrozenFoam` | executable | `sdk/openfoam/sparta/kCorrectiveFrozenFoam/` | `wmake` |

All four sources are tracked in this repository. Read each one's `Make/files`
for the authoritative target name; the table above is derived from them.

**Two ordering constraints, both read out of `Make/options` rather than assumed:**

1. `kCorrectiveFrozenFoam/Make/options` contains `-I../spartaTurbulenceModels`
   — a **relative** include. The two directories must stay siblings, exactly as
   they are under `sdk/openfoam/sparta/`.
2. It also links `-lspartaTurbulenceModels` out of `$(FOAM_USER_LIBBIN)`, so
   **`spartaTurbulenceModels` must be built before `kCorrectiveFrozenFoam`.**

`kOmegaSSTQCR` and `rhoCentralFoamBounded` have no ordering constraint against
anything else.

---

## 2. Where the artifacts land, and why that path is load-bearing

`wmake` writes to `$(FOAM_USER_APPBIN)` and `$(FOAM_USER_LIBBIN)`, which on this
box resolve to:

```
/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin
/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/lib
```

Those are not configurable in the case files. `etc/bashrc` line 190 of the
installation sets

```sh
export WM_PROJECT_USER_DIR="$HOME/$WM_PROJECT/${USER:-user}-$WM_PROJECT_VERSION"
```

**unconditionally** — it overwrites any value you export beforehand. So the only
lever on the destination is `$HOME`. Verified by measurement: exporting
`WM_PROJECT_USER_DIR` to a scratch path and running
`openfoam2606 -c 'echo $WM_PROJECT_USER_DIR'` still printed
`/home/ubuntu/OpenFOAM/ubuntu-v2606`.

Published cases reach these binaries by name, so the path must not move:

- `…/F4_runs/swbli_cylflare/rhoCentralFoamBounded_src/Make/files` sets
  `EXE = $(FOAM_USER_APPBIN)/rhoCentralFoamBounded`
- `…/swbli_cylflare/warmup20_bounded/system/controlDict` and
  `…/warmup20_bounded_realtime/system/controlDict` both name
  `application rhoCentralFoamBounded;`
- run-tree studies `w3-qcr-duct/` and `w3-qcr-rank1/` load
  `libkOmegaSSTQCRTurbulenceModels`

---

## 3. Prerequisites

| Requirement | Value on this box | How to check |
|---|---|---|
| OpenFOAM | v2606, `openfoam2606-common` (dpkg), at `/usr/lib/openfoam/openfoam2606` | `dpkg -S /usr/lib/openfoam/openfoam2606/etc/bashrc` |
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` | `g++ --version` |
| Build target | `linux64GccDPInt32Opt` | `openfoam2606 -c 'echo $WM_OPTIONS'` |
| Stock `rhoCentralFoam` BCs headers | `…/applications/solvers/compressible/rhoCentralFoam/BCs/lnInclude` must exist | `ls` that path |
| Stock `librhoCentralFoam.so` | shipped with the package | `ls $FOAM_LIBBIN/librhoCentralFoam.so` |

The last two matter only for `rhoCentralFoamBounded`, whose `Make/options`
hard-codes an absolute `-I` into the installation's `rhoCentralFoam/BCs/lnInclude`
and links `-lrhoCentralFoam`. Both ship with `openfoam2606`; neither needs to be
built.

`openfoam2606` is a launcher, not a shell you stay in: `openfoam2606 -c '<cmds>'`
runs `<cmds>` in a fully configured OpenFOAM environment and exits.

---

## 4. The procedure

Run it exactly as written. `REPO` is this repository's root.

```sh
REPO=/home/ubuntu/Certonomous
USERDIR="$HOME/OpenFOAM/ubuntu-v2606"

# --- 1. rhoCentralFoamBounded ---------------------------------------------
mkdir -p "$USERDIR/applications/solvers/compressible"
cp -R "$REPO/demo-output/website/campaign/F4_runs/swbli_cylflare/rhoCentralFoamBounded_src" \
      "$USERDIR/applications/solvers/compressible/rhoCentralFoamBounded"

# --- 2. the sparta pair (siblings) and the QCR library --------------------
mkdir -p "$USERDIR/src"
cp -R "$REPO/sdk/openfoam/sparta"           "$USERDIR/src/sparta"
cp -R "$REPO/sdk/openfoam/qcr/kOmegaSSTQCR" "$USERDIR/src/kOmegaSSTQCR"

# --- 3. discard any build products carried in with the copies -------------
/usr/bin/find "$USERDIR/src" -type d -name linux64GccDPInt32Opt -exec rm -rf {} + 2>/dev/null
rm -rf "$USERDIR/src/sparta/spartaTurbulenceModels/lnInclude"

# --- 4. build, in this order ----------------------------------------------
openfoam2606 -c 'set -e
  cd "$WM_PROJECT_USER_DIR/applications/solvers/compressible/rhoCentralFoamBounded" && wmake
  cd "$WM_PROJECT_USER_DIR/src/sparta/spartaTurbulenceModels"                       && wmake libso
  cd "$WM_PROJECT_USER_DIR/src/kOmegaSSTQCR"                                        && wmake libso
  cd "$WM_PROJECT_USER_DIR/src/sparta/kCorrectiveFrozenFoam"                        && wmake
'
```

Step 3 is not cosmetic. `sdk/openfoam/sparta/*/Make/linux64GccDPInt32Opt/` and
`spartaTurbulenceModels/lnInclude/` are tracked build leftovers; copied forward
they make `wmake` reuse objects built against a different tree and the outcome
stops being reproducible.

### Verify

```sh
openfoam2606 -c 'rhoCentralFoamBounded -help' | head -2
ls -l "$USERDIR/platforms/linux64GccDPInt32Opt/bin" \
      "$USERDIR/platforms/linux64GccDPInt32Opt/lib"
```

---

## 5. Rebuilding without overwriting the published binaries

The procedure in §4 **overwrites** the four artifacts behind published results.
To rebuild and compare instead, redirect `$HOME` — the one lever §2 established
— and nothing under `/home/ubuntu/OpenFOAM` is touched:

```sh
SCRATCH=$(mktemp -d)
HOME="$SCRATCH" <the whole of §4, with USERDIR="$SCRATCH/OpenFOAM/ubuntu-v2606">
cmp "$SCRATCH/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin/rhoCentralFoamBounded" \
    "/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin/rhoCentralFoamBounded"
```

---

## 6. Measured: all four rebuild bit-identical

Run 2026-08-17 by the §5 method, from the tracked sources, against the four
binaries then in place. `cmp` reported no difference on any of them.

| Artifact | Bytes | MD5 (rebuilt **and** published) |
|---|---:|---|
| `rhoCentralFoamBounded` | 970,456 | `ee83ca590752bd34265d306faf3ad660` |
| `kCorrectiveFrozenFoam` | 673,856 | `d9b2920d4797c1ccd274b84c005eb0a1` |
| `libspartaTurbulenceModels.so` | 1,574,800 | `0244df9b8447e94eedfdc90541ede0fb` |
| `libkOmegaSSTQCRTurbulenceModels.so` | 1,389,504 | `fae5bceecde6e078726be1af3ea82d32` |

This answers the question that was open on `AWS_TREE_PLAN.md` ASK-2 — "is a
bit-identical binary required for any published claim, or is rebuildable-from-
tracked-source sufficient?" — by removing the trade-off: on this box, with this
toolchain, rebuilding from tracked source **is** bit-identical, so the two
options coincide.

**State the limit.** This is one measurement on one box: OpenFOAM v2606 from
`openfoam2606-common`, g++ 13.3.0, `linux64GccDPInt32Opt`. Bit-identity is a
property of that combination, not a guarantee about any other. A different
compiler version or build target will very likely differ, and the claim above
should be re-measured rather than quoted if any of them changes.

---

## 7. The repository's `rhoCentralFoamBounded` source was incomplete until 2026-08-17

`rhoCentralFoamBounded_src/` tracked only the three files the lab had written or
changed. Five headers the solver `#include`s were absent, so the tracked copy
could not build and `~/OpenFOAM/…/rhoCentralFoamBounded/` was the only complete
copy of a solver behind published results — an untracked directory on a machine
with no off-box replica.

The five were added on 2026-08-17. Each is **byte-identical to the stock v2606
file of the same name** shipped in
`/usr/lib/openfoam/openfoam2606/applications/solvers/compressible/rhoCentralFoam/`
(GPL-3.0-or-later, OpenCFD Ltd. — headers unchanged), so nothing lab-authored
was recovered by adding them; what was recovered is the ability to build.

| File | MD5 | Same as stock v2606 `rhoCentralFoam`? |
|---|---|---|
| `centralCourantNo.H` | `3a6048492be9d55f4793dc52a2ffdaf6` | yes |
| `createFieldRefs.H` | `f25ebd4153fc19a33126ab37299a7a3c` | yes |
| `directionInterpolate.H` | `ddaeaec20848af5e81028520e4788d21` | yes |
| `readFluxScheme.H` | `b7d7f58fa3b8e0685ef8c7cda008b799` | yes |
| `setRDeltaT.H` | `28a778a8dac9e904d4438ca4366aca33` | yes |

The three that were always tracked are the lab's own work and differ from stock:
`rhoCentralFoamBounded.C` (`b2d49a388a791da7830a03c7487b08db`), `createFields.H`
(`a7f08e8fa7c069a82f8b5e21f20c27b7`, against stock's
`2de52e2ce1464c3d6bf75662d4b61242`) and `boundE.H`
(`3c30480673b4b443ccc5ce7cceb53671`, which has no stock counterpart).

After the addition, `diff -rq --exclude=linux64GccDPInt32Opt` between the
repository copy and `~/OpenFOAM/…/rhoCentralFoamBounded/` reports no
differences.

---

## 8. Correction to `AWS_TREE_PLAN.md` §6.3

That table gives the rebuild command for `libkOmegaSSTQCRTurbulenceModels.so` as
"`wmake libso` from the same sparta source tree". It is not built from the sparta
tree. `sdk/openfoam/qcr/kOmegaSSTQCR/Make/files` reads

```
makeKOmegaSSTQCR.C

LIB = $(FOAM_USER_LIBBIN)/libkOmegaSSTQCRTurbulenceModels
```

and `sdk/openfoam/sparta/spartaTurbulenceModels/Make/files` names a different
library. Following the plan's instruction would rebuild the wrong target.
