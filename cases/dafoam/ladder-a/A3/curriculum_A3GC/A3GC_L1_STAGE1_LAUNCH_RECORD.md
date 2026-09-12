# A3GC L1 STAGE 1 (MESH GENERATION) — LAUNCH RECORD

**2026-09-12, dafoam lane.** `PENDING` — stage 1 is running; no verdict is claimed here.
**SUBMISSIONS PARKED.** Nothing in this record is sent anywhere.

## 1. AUTHORITY — pre-existing, not created tonight

`PREREGISTRATION.md` is **FROZEN at commit `367799db0`** with AMENDMENTS 1–6.
§6 stage 1 registers mesh generation for all three levels; §2.5 registers L1 at
**exactly 6,389,760 cells** and states *"any departure from 99,840 / 798,720 /
6,389,760 is a launch-blocking refusal, not a note."* Compute for L1 stage 1 is
authorised by that existing frozen registration. The `CLAUDE.md` rule-2 check
(pre-registration committed before compute) was discharged **personally by the
dafoam-supervisor** and is not re-litigated here.

**AMENDMENT 3's `G-QUARANTINE` binds ONLY `/home/ubuntu/certonomous-runs/A3GC-meshgen-probe/`.**
This mesh is built under the item's **own run root**, which is what §6 stage 1
requires and the path L3 and L2 both took.

Verified append-only before launch: the working copy differs from the frozen blob
by a **single hunk at line 1000** (`@@ -1000,3 +1000,183 @@`), i.e. AMENDMENT 6 is
appended at the foot and **zero lines changed above it** (`CLAUDE.md` rule 6).

## 2. THE INSTRUMENT, PINNED

| item | value |
|---|---|
| generator | `cases/dafoam/ladder-a/A3/curriculum_A3GC/a3gc_genmesh.sh` |
| md5 | **`9fa240d9643308f5e9a4988614b58884`** — AMENDMENT 5's pin, matched |
| image | `sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46` (by digest, never tag) |
| source surface | `A3-onera-m6-transonic/m6_surfaceMesh_fine.cgns`, md5 `e6c853158d351de3f382ce5afa513997` (§2.1, matched) |
| `AUTOPATCH_ANGLE` | **60** — AMENDMENT 2(d) registered 60 and corrected the earlier 45 instruction. The script's own default is 45, so it is set explicitly in the wrapper. |
| run root | `/home/ubuntu/certonomous-runs/A3GC-L1` — did **not** exist at launch, so the generator's overwrite guard passed |

**The generator was not edited.** Its md5 is re-verified *inside the detached
wrapper*, not only by the launching agent — a check made in a shell that has
since exited is not a check on what actually ran.

## 3. RESOURCES — and the one honest departure in wording

Ordered: single core, `nice -n 19`, container `--memory 4g`. Delivered, and
**read back from the running container**, not assumed:

```
Memory=4294967296  MemorySwap=8589934592  NanoCpus=1000000000  CpuShares=2
```

Because the generator is md5-pinned and may not be edited, the constraints are
injected by a **`docker` PATH shim** (`A3GC-L1-launch/bin/docker`) that adds
`--memory 4g --memory-swap 8g --cpus 1 --cpu-shares 2` to `docker run` and passes
every other invocation through byte-for-byte. No parameter, path, image, user or
argument of the generator is altered.

**PLANTED CONTROL ON THE SHIM** (`CLAUDE.md` rule 3 — a limit not shown able to
read differently is not evidence it is applied). The same image, same command,
read its own cgroup twice:

| | `memory.max` | `cpu.weight` |
|---|---|---|
| real `docker`, no shim | `max` | `100` |
| through the shim | `4294967296` | `1` |

**`nice -n 19` is stated honestly.** `docker run` has no nice flag, and nice on
the client does **not** propagate into the container — the daemon, not the
launching shell, forks the workload. `--cpu-shares 2` (cgroup v2 `cpu.weight` = 1,
the floor) is the faithful analogue and is what was measured above. The host-side
generator process **is** at nice 19.

**Why a 4 GiB ceiling is protection, not a cap.** If a step needs more, the
*container* is killed by its own cgroup and nothing else on the box is touched.
The alternative is the host OOM killer choosing a victim — the ansys process now
3.5 days old, or the live A3GC L2 solve.

## 4. NO CAP, NO TIMEOUT, NO KILL PATH

Sanaa 2026-09-12T01:10Z: *"i dont want any cap on any run."* The wrapper, the
watcher and the shim contain **no `kill`, no signal, no `renice`, no
`docker stop/kill/update`, and no `timeout`**. Audited by grep across all three
files; every match was comment text.

Cost figures are **calibration only**. The watcher's reference of **450 core-min**
is *derived*, not registered: L2 stage 1 measured **3,376 s wall at np=1 = 56
core-min** (`A3GC-L2/genWingMesh.py` 23:28:47Z → `A3GC-L2/meshgen/logMeshGeneration.txt`
00:25:03Z), and L1 is 8× the cells. It is not a stop, and pyHyp is superlinear in
surface size, so exceeding it is expected and merely recorded as
`OVERRUN-RECORDED-NOT-STOPPED`.

## 5. LAUNCH CONDITIONS, RECORDED

- **2026-09-12T01:36:30Z**, immediately before launch: `MemAvailable` **15,800,276 kB
  = 15.07 GiB** (floor for this launch was 10 GiB), load average `67.41 68.58 67.86`.
- Detached with `setsid`, both processes **parented to init (PPID 1)**.
- **rc is captured INSIDE the wrapper** (`a3gc_L1_stage1.rc`). `setsid timeout cmd`
  exits 0 for every outcome, so rc is never read around the setsid line.

**"LAUNCHED" IS ASSERTED FROM THE GENERATOR'S OWN ARTIFACTS, NOT FROM A COMMAND
RETURNING:** the generator wrote `surfaceMesh.cgns` (uid 1002, i.e. written from
inside the container) and `genWingMesh.py` at 01:37Z, and the pyHyp extrusion
container came up running `python genWingMesh.py &> logMeshGeneration.txt`.

## 6. THE WATCHER — AND WHY A SUB-ITERATION SPIKE IS NOT A STALL

`A3GC-L1-launch/a3gc_L1_stage1_watcher.sh`, armed **before** the container started.
Polls every 120 s to `A3GC_L1_STAGE1_WATCH.txt`; escalates to
`A3GC_L1_STAGE1_ESCALATION.txt`, a **file**, never a signal.

pyHyp's cost is driven by **implicit sub-iteration count, not cell count**.
MEASURED on L2: layer 29 took **10,332** sub-iterations and layer 30 took
**8,146** — and it **recovered**, layers 31/32/33 falling back to 5,690 / 4,159 /
3,162. So **layer and sub-iteration count are recorded as progress indicators**,
and a stall is declared **only on log mtime failing to advance**: WARN at 3,600 s,
STALL at 7,200 s. The widest CPU gap between consecutive L2 rows was ~700 s; L1
has 4× the surface faces and 2× the layers, so rows thousands of seconds apart are
expected progress.

The row parser was proven against L2's real log before launch: it returned
`33 / 3162` for the final row and `29 / 10332` for the spike row.

## 7. WHAT IS NOT VERIFIED, AND IS FLAGGED RATHER THAN DISCOVERED LATE

**The 4 GiB ceiling has not been shown sufficient for the post-extrusion steps.**
pyHyp's own footprint is expected to fit, but `plot3dToFoam`, `renumberMesh` and
`checkMesh -allGeometry -allTopology` at **6,389,760 cells** may well exceed 4 GiB —
OpenFOAM `polyMesh` construction at this size plausibly needs several times that.
This is **not measured**. If it happens, the container dies cleanly and the host is
untouched, and the wrapper's rc will record it. Raising the ceiling for the
post-extrusion steps is the supervisor's call, not this lane's, and there are hours
of extrusion in which to make it.

## 8. NOT TOUCHED

The live **A3GC L2** solve (`--cpus=8`, `primal.log` advancing) and every other
team's process — `splitMeshRegion`, `buoyantBoussinesqSimpleFoam`, `rhoCentralFoam`,
`snappyHexMesh`, `simpleFoam`, and another lane's D8G witness calibration container —
were read only and never signalled.

## 9. PATHS

| what | path |
|---|---|
| run root | `/home/ubuntu/certonomous-runs/A3GC-L1/` |
| launch assets | `/home/ubuntu/certonomous-runs/A3GC-L1-launch/` |
| wrapper | `/home/ubuntu/certonomous-runs/A3GC-L1-launch/a3gc_L1_wrapper.sh` |
| resource shim | `/home/ubuntu/certonomous-runs/A3GC-L1-launch/bin/docker` |
| watcher | `/home/ubuntu/certonomous-runs/A3GC-L1-launch/a3gc_L1_stage1_watcher.sh` |
| watch log | `/home/ubuntu/certonomous-runs/A3GC-L1-launch/A3GC_L1_STAGE1_WATCH.txt` |
| escalation | `/home/ubuntu/certonomous-runs/A3GC-L1-launch/A3GC_L1_STAGE1_ESCALATION.txt` |
| generator stdout | `/home/ubuntu/certonomous-runs/A3GC-L1-launch/a3gc_L1_stage1.log` |
| rc | `/home/ubuntu/certonomous-runs/A3GC-L1-launch/a3gc_L1_stage1.rc` |
| pyHyp log | `/home/ubuntu/certonomous-runs/A3GC-L1/logMeshGeneration.txt` |
