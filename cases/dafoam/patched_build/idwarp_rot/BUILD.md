# `dafoam-idwarp-rot:v1` — reproducible patched-IDWarp build

**Moved 2026-08-21 (same day) from `cases/dafoam/patched_build/` into `cases/dafoam/patched_build/idwarp_rot/`,
to match the per-image subdirectory convention already used by `subpclu/` and `kspopts/`. The
build command in §5.1 is quoted with the post-move path; the image built on 2026-08-21 was built
with the identical Dockerfile at the pre-move path and is unaffected.**

**Built 2026-08-21, Lane A. Local image only: nothing pushed, nothing filed, no registry involved.**

## 1. Why this image exists, and what it fixes about how we work

Every "patched toolchain" number this lab has published was produced by bind-mounting a host scratch
clone into the stock image and prepending it to `PYTHONPATH`:

```bash
sudo docker run --rm -v /home/ubuntu/certonomous-runs/W5-patch:/patch ... \
    dafoam/opt-packages:latest bash -lc \
    "source loadDAFoam.sh && export PYTHONPATH=/patch/idwarp:\$PYTHONPATH && ..."
```

That makes the patched stack a property of **the command line**, not of an artifact. A run that
dropped the `-v` or the `export` would silently produce **stock numbers under a patched label**, and
the only tell was the `IDWARP_IMPORTED_FROM:` line each script had to remember to print. This image
turns the patched stack into an artifact with an image ID.

## 2. **The md5 of `libidwarp.so` is the identity. Nothing else is.**

This is the single most important line in this document.

| property | stock | patched | discriminates? |
|---|---|---|---|
| `importlib.metadata.version("idwarp")` | **2.6.2** | **2.6.2** | **NO** |
| `idwarp/*.py` file sizes (2558 / 36443 / 1035 / 42475 / 1024 / 265) | identical | identical | **NO** — the patch is entirely in Fortran |
| `libidwarp.so` **size** | **491,344 bytes** | **491,344 bytes** | **NO** — same size to the byte |
| `libidwarp.so` **md5** | `f0fcb488e0e98156575cd19548e91663` | `85f59e87253e0a71a813f64ca6e4c425` | **YES — this is the only thing that does** |

**Any verification that checks the version string is checking nothing.** Any verification that
checks the file size is checking nothing. A future run that wants to prove which stack it used must
hash the `.so` it actually loaded, from inside the process that loaded it — which is what §5 does.

## 3. What is patched

Two Tapenade-generated files inside IDWarp 2.6.2:

* `src/adjoint/outputReverse/vectorUtils_b.f90`
* `src/adjoint/outputForward/vectorUtils_d.f90`

supplying the analytic limit that the `sqrt(eps)` guard at `src/utils/vectorUtils.f90:58` discards:

```
v2b += ( axial(mib - mib^T) x v1 ) / (|v1| |v2|)
```

**The primal is untouched** — `vectorUtils.f90` is unchanged and `warpMesh` output is md5-identical
patched vs unpatched (`../../PATCH_getRotationMatrix3d.md` §9.5, md5
`8fafe12f848af490a5041c865112b5fb`, max|diff| = 0.0). Derivation and acceptance tests:
`../../PATCH_getRotationMatrix3d.md`. Root cause: `../../ROOTCAUSE_getRotationMatrix3d.md`.

**This is a proof-of-concept hand-edit of generated code.** Upstream should fix the primal's
parameterisation and regenerate with Tapenade, not merge a hand edit. **Nothing has been filed.**

## 4. Provenance of the copied package — actual output

```
$ cd /home/ubuntu/certonomous-runs/W5-patch/idwarp && git log --oneline -1 && git status --short
647fd8f version update (#102)
 M src/adjoint/outputForward/vectorUtils_d.f90
 M src/adjoint/outputReverse/vectorUtils_b.f90
?? src/f2py/libidwarp-f2pywrappers.f

$ git rev-parse HEAD
647fd8fc2c06fc61b31cc07a7b63ffd4fbaf65ce

$ md5sum idwarp/libidwarp.so
85f59e87253e0a71a813f64ca6e4c425  idwarp/libidwarp.so

$ ls -la idwarp/libidwarp.so
-rwxr-xr-x 1 root root 491344 Aug  1 00:04 idwarp/libidwarp.so

$ md5sum /home/ubuntu/Certonomous/cases/dafoam/rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch
5d5afd856760c19f03e8c363f0c3ac3d  .../idwarp_v2.6.2_degenerate_branch_fix.patch
```

The working tree carries **exactly the two modified files the patch touches** — no third file, no
drift. `git rev-parse HEAD` matches upstream tag `v2.6.2`. The `.so` was built 2026-08-01 00:04 UTC,
**after** the `.f90` edits of 2026-07-31 23:59, so it is a build *of* the patched sources.

**The `.so` was already built, so no Tapenade or gfortran run was required and the build is a
COPY.** (The supervisor's stop condition — "if the clone has no built `.so` and a rebuild needs
Tapenade/gfortran, STOP and report the cost instead" — did not fire.)

## 5. Build and verification — exact commands, actual output

### 5.1 Build

The **build context is the clone itself**, so no binary enters the git repo:

```bash
$ sudo -n docker build \
      -f /home/ubuntu/Certonomous/cases/dafoam/patched_build/idwarp_rot/Dockerfile \
      -t dafoam-idwarp-rot:v1 \
      /home/ubuntu/certonomous-runs/W5-patch/idwarp
...
Step 19/19 : LABEL org.certonomous.filed_upstream="no"
 ---> Running in c92f5c0b5d5f
 ---> Removed intermediate container c92f5c0b5d5f
 ---> 2927768a16ac
Successfully built 2927768a16ac
Successfully tagged dafoam-idwarp-rot:v1

real    3m27.958s
```

**3m28s**, inside the <10 min expectation. Foreground, bounded by `timeout 550`. Most of that is
the daemon re-materialising the 7.83 GB base layer, not the 648 KB copy; a second build of the same
Dockerfile is near-instant from cache. The daemon was concurrently serving another lane's build,
which is why it ran longer than a COPY suggests.

```
$ sudo -n docker images
IMAGE                        ID             DISK USAGE   CONTENT SIZE
dafoam-idwarp-rot:v1         2927768a16ac       9.93GB          2.1GB
dafoam/opt-packages:latest   9d45679d55fd       9.93GB          2.1GB
```

### 5.2 Verification inside the image

```bash
$ sudo -n docker run --rm dafoam-idwarp-rot:v1 bash -lc \
  'source /home/dafoamuser/dafoam/loadDAFoam.sh; python -c "
import idwarp, importlib.metadata as m, hashlib, os
p = idwarp.__file__
print(\"IDWARP_IMPORTED_FROM:\", p)
print(\"idwarp version    :\", m.version(\"idwarp\"))
so = os.path.join(os.path.dirname(p), \"libidwarp.so\")
print(\"loaded .so path   :\", so)
print(\"loaded .so md5    :\", hashlib.md5(open(so,\"rb\").read()).hexdigest())
print(\"loaded .so bytes  :\", os.path.getsize(so))
stock = \"/home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/idwarp/libidwarp.so\"
print(\"stock  .so md5    :\", hashlib.md5(open(stock,\"rb\").read()).hexdigest())
print(\"stock  .so bytes  :\", os.path.getsize(stock))
"'

IDWARP_IMPORTED_FROM: /opt/idwarp_patched/idwarp/__init__.py
idwarp version    : 2.6.2
loaded .so path   : /opt/idwarp_patched/idwarp/libidwarp.so
loaded .so md5    : 85f59e87253e0a71a813f64ca6e4c425
loaded .so bytes  : 491344
stock  .so md5    : f0fcb488e0e98156575cd19548e91663
stock  .so bytes  : 491344
```

**Four things this proves, and one it deliberately shows.**

1. Python resolves `idwarp` to `/opt/idwarp_patched/idwarp/` — the patched copy, ahead of
   site-packages.
2. The `.so` actually adjacent to the loaded package hashes to `85f59e87…` — **the clone's patched
   `.so`, byte for byte.**
3. The stock `.so` is **still present and untouched** at its site-packages path, hashing to
   `f0fcb488…`. The image adds; it does not overwrite. Anyone can recover stock behaviour inside
   this image by clearing `PYTHONPATH`.
4. The two hashes differ.
5. **And the version string reads `2.6.2` on the patched stack** — the demonstration of §2, produced
   by the image itself rather than asserted.

## 6. How to use it

```bash
# patched — no mount, no export, no IDWARP_IMPORTED_FROM discipline required
sudo -n docker run --rm --cpus=2 --memory=8g -v <case-parent>:/mnt -w /mnt/<case> \
    dafoam-idwarp-rot:v1 bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     mpirun --allow-run-as-root -np 1 -x PYTHONPATH python runScript.py -task check_totals"

# stock — unchanged
sudo -n docker run --rm --cpus=2 --memory=8g -v <case-parent>:/mnt -w /mnt/<case> \
    dafoam/opt-packages:latest bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     mpirun --allow-run-as-root -np 1 python runScript.py -task check_totals"
```

`-x PYTHONPATH` is retained on the patched form: `ENV` reaches the launching shell, but Open MPI
does not reliably forward the parent environment to every rank, and a rank that silently fell back
to site-packages would produce a mixed-stack run. Keeping the flag costs nothing and closes it.

Two hooks are set on purpose (`Dockerfile`): `ENV PYTHONPATH=/opt/idwarp_patched` covers a bare
`docker run … python`, and an appended line in `loadDAFoam.sh` covers anything that sources the lab
environment. `loadDAFoam.sh` never touches `PYTHONPATH` itself — verified by reading it in-image —
so the append cannot clobber anything.

## 7. Limits of this artifact, stated plainly

1. **Reproducible *given the clone*.** The Dockerfile COPYs a pre-built `.so`; it does not compile
   from source. If `/home/ubuntu/certonomous-runs/W5-patch/idwarp` is lost, this exact image cannot
   be rebuilt from this file alone. Reconstructing the clone is fully specified — clone
   `mdolab/idwarp` at `647fd8fc2c06fc61b31cc07a7b63ffd4fbaf65ce`, apply
   `idwarp_v2.6.2_degenerate_branch_fix.patch` (md5 `5d5afd856760c19f03e8c363f0c3ac3d`), rebuild —
   but that rebuild needs a Fortran toolchain and **would not be expected to reproduce md5
   `85f59e87…`**, since compiler version, flags and build paths all enter the binary. A
   from-source image is a separate, larger piece of work and is **not** what this is.
2. **It fixes regime 1 only.** The near-threshold ill-conditioned regime survives the patch by
   design and by prediction — ~1.26% on IDWarp's own `onera_m6` test mesh
   (`../../ROOTCAUSE_getRotationMatrix3d.md` §6.4, `../../PATCH_getRotationMatrix3d.md` §6, §9.4). An
   optimiser leaves the baseline at iteration 1 and spends the rest of the run in regime 2.
3. **It does not touch DAFoam**, so the decomposition defect and the `cellLimited` limiter defect
   are entirely unaffected. This image is not "the fixed toolchain"; it is one defect removed.
4. **It is not layered onto `dafoam-subpclu:v1` or `dafoam-kspopts:v1`.** Those carry `DALinearEqn.C`
   changes and this one does not; a combined image does not exist and would need its own build.

## 8. Ledger

| item | value |
|---|---|
| build wall time | 3 min 28 s |
| solver core-minutes | **0.00** (no solve; a COPY and one verification container) |
| dollars | **≈$0.00** |
| pushed anywhere | **no** |
| filed upstream | **nothing** |
