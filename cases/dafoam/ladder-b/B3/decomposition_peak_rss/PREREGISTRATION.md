# B3 decomposition chain — PEAK RSS, measured: PRE-REGISTRATION

**Written 2026-08-23, BEFORE any arm of this item ran.** DAFoam team, `lab-lane` under
`dafoam-supervisor`. Run root **`/home/ubuntu/certonomous-runs/B3-decomposition-peakrss/`**.

**Nothing is filed, sent, uploaded, registered, posted or pushed anywhere. Every dollar figure
below is an estimate at an owner-stated rate, never a measurement.**

---

## 0. The freeze condition, checked and named

Standing rule 2 requires the condition be stated and how it was checked. At the moment this file
was written, **the run root named above did not exist**:

```
$ ls -d /home/ubuntu/certonomous-runs/B3-decomposition-peakrss
ls: cannot access '/home/ubuntu/certonomous-runs/B3-decomposition-peakrss': No such file or directory
$ ls -d /home/ubuntu/Certonomous/cases/dafoam/ladder-b/B3/decomposition_peak_rss
ls: cannot access '.../decomposition_peak_rss': No such file or directory     (before this file)
$ date -u
Sun Aug 23 19:40:28 UTC 2026
```

**No compute has been spent on this item.** Amendments are legal until the first container starts
and must themselves name the condition. After that, addenda only, and no addendum may move a
band, a gate, a cap or a label.

---

## 1. What this item is, and what it is not

`cases/dafoam/ladder-b/B3/decomposition_np4/RESULTS.md` §5 and §9 carry an explicit hole:

> *"6.156 GiB is a `docker stats` sample taken during the linear solve, **not a true peak** — no
> per-arm high-water mark was recorded, because the chain did not carry the 5 s memory watcher
> the ILU-shift chain used. The honest statement is that the cap was never approached at any
> moment observed, not that the peak was 6.156 GiB … the exact peak is **NOT MEASURED**."*
> — `decomposition_np4/RESULTS.md:129-134`, and §9's closing bullet *"The true peak RSS of any
> arm"*.

**This item re-runs that chain, unchanged, with an instrument attached, and produces one thing: a
measured peak-memory number for each arm.**

**It changes no verdict about B3.** G1/G2/G3 stay `PASS`, G4 stays `GATE FAIL`, G5 stays `PASS`,
B3 Stage 4 stays `BLOCKED` under R11. Nothing here is a re-grading of the decomposition question
and nothing here may be read as one. The gradients are not re-scored; `analyse_decomp.py` is not
re-run and is not in this item's grading path.

**It is a re-run and not a fresh study**, so the item's own first gate (**M0**) is that the
re-run reproduces the graded arms' archived digits. A memory number from a run that is not the
graded run is a number about a different run.

---

## 2. The chain being reproduced, reconstructed from what is on disk

The chain driver (`chain5b.sh`) **is gone** — it lived in a scratch directory and was wiped;
that is L-186 acting exactly as the lesson describes, and it is disclosed here rather than
papered over. What survives, and what the reconstruction rests on:

| artefact | path | what it fixes |
|---|---|---|
| driver stdout, verbatim, all four arms | `/home/ubuntu/certonomous-runs/B3-decomposition-np4-chain5b.out` | the gate lines, the `decomposeParDict` read-back, the per-arm `rc`/wall/core-min, the printed convergence lines |
| ledger, six rows incl. both void arms | `…/B3-decomposition-np4/ledger.csv` | image, np, env, decomp, rc, wall_s, core_min, finish time per arm |
| the arms' own run scripts, byte-preserved | `…/B3-decomposition-np4/D_serial/runScript.py`, `…/D_simple2/runScript.py` | the case, the DV, the task, the `daOptions` partitioner override |
| the same lane's sibling chain, same day | `…/B3-adjoint-unblock-reproduce/chain3.sh`, `run_arm.sh` | the exact `docker run` form, the load and `MemAvailable` guards, the ledger format |
| the same lane's ILU chain, same day | `…/B3-ilu-shift-runtime/chain4.sh` | the 5 s watcher precedent this chain omitted |

`chain5b.out`'s per-arm banner lines (`GATE OPEN load=… mem_kB=…`, then a `decomposeParDict ->`
read-back, then `== <arm> rc=… wall=…s core_min=…`) match `chain3.sh`'s `run()` structure line for
line, and its ledger header is byte-identical to `chain4.sh`'s. **The reconstruction is therefore
of a driver whose shape is attested by two surviving siblings and whose per-arm effect is
attested by its own stdout — not a guess.** Where it is a reconstruction rather than a copy, this
file says so.

### 2.1 The graded arms

| arm | np | decomposition | image | env | task | timeout | measured 2026-08-21 |
|---|---|---|---|---|---|---|---|
| **`D_serial`** | **1** | none; one ASM block over the whole 210,592² operator | `dafoam-subpclu:v2` | `DAFOAM_SUBPC_TYPE=lu` | `compute_totals` | 2400 s | rc 0, **1266 s**, **21.10 core-min**, reason 2, **163** iters |
| **`D_simple2`** | 4 | `simple`, `n (4 1 1)`, set **through `daOptions`** | `dafoam-subpclu:v2` | `DAFOAM_SUBPC_TYPE=lu` | `compute_totals` | 2100 s | rc 0, **301 s**, **20.07 core-min**, reason 2, **766** iters |

**`D-scotch` is not re-run here either.** It was never re-run in the graded item — it is arm Pβ of
`../adjoint_unblock_reproduce/`, and **its peak already has the best figure the lab holds for it:
9.044 GiB** (`../adjoint_unblock_reproduce/RESULTS.md:277`, `:290`), from a 5 s `docker stats`
watcher, attributed to the named container `priceless_jepsen`. Re-running it would cost 27.60
core-min to improve an instrument, not to fill a hole, and it is **out of scope** — but §5 uses
it as the prediction basis, and §8 records that this item therefore leaves `D-scotch`'s peak on a
weaker instrument than the two arms it does measure.

### 2.2 Image identity — by content, never by tag

`docs/dafoam/TOOLCHAIN_INVENTORY.md:124-129` identifies these images by the **md5 of the patched
source file inside them**, not by their tag — three images that differ only in one `.C` file and
its rebuilt library. For this item:

| identity | value | where read |
|---|---|---|
| image sha256 | **`8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46`** | `docker inspect dafoam-subpclu:v2 --format '{{.Id}}'`, run 2026-08-23 for this file |
| created | `2026-08-21T16:07:24.720254434Z` | same command |
| in-image `src/adjoint/DALinearEqn/DALinearEqn.C` md5 | **`5b3159f88dbefcf7c52bd888401d097f`** | `cases/dafoam/patched_build/subpclu/BUILD.md:128` (gate G2d, host-patched stock md5 == in-image v2 md5) |
| the graded item's recorded image | `dafoam-subpclu:v2` (`8352629516bb`) | `decomposition_np4/RESULTS.md:5` |

**The image ID matches the one the graded chain recorded**, so the tag has not been re-pointed
since 2026-08-21. **Registered as a phase-2 assertion:** the launch script re-reads
`docker inspect -f '{{.Id}}'` and **refuses to launch** unless it equals the sha256 above, and the
first container in the chain prints the in-container `md5sum` of `DALinearEqn.C` and the run is
**void** unless it equals `5b3159f88dbefcf7c52bd888401d097f`. A tag is not an identity; these two
values are.

### 2.3 The run scripts, frozen by hash

The re-run stages the **byte-identical** run scripts from the graded arms:

```
cb4abffa143855971d1612d42e5bde4997269a8edf5751526ab4296622e95c25  D_serial/runScript.py
0d26390dca0db2d8fa08c5a71c9e6043286f891e46b5dd58a5695be9184e9a22  D_simple2/runScript.py
```

They differ by exactly one 15-line block (`diff` run for this file): `D_simple2` sets
`daOptions["decomposeParDict"] = {"method": "simple", "simpleCoeffs": {"n": [4,1,1], …}}` and
prints `T3 DECOMP OVERRIDE: simple [4, 1, 1]`. **Editing `system/decomposeParDict` does nothing** —
`pyDAFoam._writeDecomposeParDict()` (`pyDAFoam.py:2212`, called from `:1463`) overwrites it at
startup, which is the trap that voided the first `simple` arm
(`decomposition_np4/RESULTS.md:140-166`). **Phase 2 asserts both sha256 values after staging and
refuses to launch on a mismatch.**

### 2.4 Staging, per arm, and why the two arms are staged differently

Staged into the **new** run root from the graded arm directories, excluding everything the graded
run produced: `processor*/`, the numeric time directories, `cbfs_beta_grad.npy`, `reports/`.

- **`D_serial`**: `dRdWColoring_1.bin` **is carried in** (it is dated `16:43`, before the graded
  arm's `19:25` start — the graded arm reused it and did **not** regenerate).
- **`D_simple2`**: **no** coloring file is carried in. The graded arm regenerated its own
  (`dRdWColoring_4.bin` dated `19:57`, inside the arm's `19:55:52`–`20:00:53` window) because the
  stale `scotch` coloring aborts on `DAColoring.C:1021` — `RESULTS.md:168-187`.

**This asymmetry is deliberate and is part of the chain.** Coloring generation has its own memory
and wall cost; reproducing the graded arms' coloring state is what makes the measured peak the
peak *of the graded arm* rather than of a variant. **Registered: if `D_simple2` regenerates
coloring, that is expected; if `D_serial` regenerates coloring, the staging failed and the arm is
void.**

### 2.5 The launch command, per arm

Reconstructed from `chain3.sh` / `chain4.sh`, with departures marked `[D-n]` and justified in §4.3:

```bash
R=/home/ubuntu/certonomous-runs/B3-decomposition-peakrss
timeout <2400|2100> sudo -n docker run --rm --name b3rss_<ARM>            # [D-1]
  --cpuset-cpus 0-3 --memory=12g -e DAFOAM_SUBPC_TYPE=lu \
  -v "$R":/mnt -w "/mnt/<ARM>" dafoam-subpclu:v2 bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
   mpirun --allow-run-as-root -np <1|4> python runScript.py -task compute_totals ; \
   rc=\$? ; echo CGROUP_PEAK_BYTES=\$(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo 0) ; \
   exit \$rc"                                                             # [D-2]
  > "$R/logs/<ARM>.log" 2>&1
```

**The `mpirun` invocation is byte-identical to the graded chain's.** `[D-2]` executes only after
`mpirun` has exited and preserves `mpirun`'s exit status; it cannot affect the solve.

---

## 3. The launch gate, unchanged, and the preflight reading

**Registered threshold: host `MemAvailable` above 12 GiB before each container starts**, in a
bounded wait loop. The graded chain implements it as `[ "$M" -gt 12582912 ]`, i.e. **strictly
greater than 12,582,912 kB** — `chain3.sh:29` (60 × 10 s) and `chain4.sh:19` (90 × 20 s). This
item uses the same comparison with a **60 × 20 s = 20 min** bound; **the threshold itself is
identical and is not moved by this item.** A MemAvailable launch-gate ruling is
on Sanaa's desk; until she rules, 12 GiB stands, and **an agent may not move it** (standing rule 9;
`CLAUDE.md` FIRST-ACTION RULE, reserved matters). If the gate never opens within 20 minutes the
item is **`BLOCKED`**, not launched, and that is the reported verdict.

**Preflight reading taken 2026-08-23 19:40:28 UTC, with nothing launched:**

| reading | value | gate |
|---|---|---|
| `MemAvailable` | **28,371,460 kB = 27.06 GiB** | **>= 12 GiB: would be OPEN** |
| `MemTotal` | 32,132,604 kB = 30.64 GiB | — |
| `loadavg` 1/5/15 | **5.47 / 4.70 / 4.46** | load guard is `<= 10`: would be OPEN |
| running containers | **none** (`docker ps` empty) | — |
| peer activity | a live **W4 M1+M2** lane in `/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning` (files touched within 30 min, its own `w4_m1m2_memguard.sh` self-tested at 19:26:09Z) | **the box is shared; §4.2 and §5.3 depend on this** |

**Nothing was launched to produce this table.** A gate reading taken now is not a gate reading
taken at launch, and phase 2 re-takes it.

### 3.1 Mid-run enforcement, wired rather than declared

L-239 / D462: *a registered 8 GiB host floor with a record-only watcher, nothing connecting them,
breached for 52.6 % of the graded arm with no stop firing* (`DAFOAM_CHARTER.md` v1.0c). This item
does not repeat that. Two enforcement paths, both real:

1. **The kernel**: `--memory=12g` is a cgroup v2 limit. Exceeding it is an OOM-kill, not a
   warning. **An arm ended this way is recorded as stopped by memory and is `NOT A RESULT` about
   convergence** (`DAFOAM_CHARTER.md` §7), and it is *not* re-run at a larger cap inside this
   item — a larger cap is a new registration with its own price.
2. **The host floor**: `b3_rss_watch.sh` carries a **hard floor of host `MemAvailable`
   < 4,194,304 kB (4 GiB) → `docker kill` the named container**, on the same code path as the
   sampling, kill decision taken *before* any sampling that can block. The trigger path is
   self-tested by `--selftest` against a sentinel file and the item **refuses to proceed** if it
   does not fire. The floor is set at 4 GiB rather than 12 because the 12 GiB figure is a
   *launch* gate; a mid-run kill at 12 GiB would kill a healthy arm on a shared box the moment a
   peer starts.

---

## 4. The instrument, and what each of its numbers is

**Frozen with this commit. The grading path is fixed here (standing rule 2) and nothing in it is
edited after the first container starts.**

| file | sha256 |
|---|---|
| `b3_rss_watch.sh` | `e9db593ee5932a1b9bb16bf40560ddf38d1836ad34c4a7c281217d3d463dac29` |
| `analyse_peak_rss.py` | `c4db08fcf7a3e5d23327943d9093feb3b5983ec655083f50a103e30f9c6951eb` |

### 4.1 What is sampled, every 2 s (registered requirement: <= 5 s)

Resolved **by container name → container id → cgroup v2 path**, and only that cgroup:

| quantity | what it is | why it is here |
|---|---|---|
| **`memory.peak`** | cgroup v2 kernel high-water of `memory.current`. **Monotone non-decreasing**, so a reading at time *t* is the exact peak up to *t*. Includes page cache and kernel memory. | **This is the quantity `--memory=12g` is enforced against.** It is the number that answers "does this fit". |
| `memory.current` | instantaneous | the trajectory |
| **tree RSS** | sum of `VmRSS` over every pid in the container cgroup | resident process memory, **no page cache** — the number people mean by "RSS" |
| **per-pid `VmHWM`** | kernel per-process high-water | answers **which process**, which no container-level number can |
| host `MemAvailable` | | the floor decision, and the shared-box context |

**The two headline numbers are not the same quantity and both are reported.** `memory.peak`
>= tree RSS by construction. **Neither is `docker stats` `MemUsage`** (= `memory.current` −
`inactive_file`), which is the instrument every earlier B3 memory figure came from — and whose
field-position parse bug turned 9.787 GiB into 7.396 GiB on the record
(`ladder-a/A6/rung_n16_np1/RESULTS.md:366-381`). **This instrument parses no human-formatted size
string at all**: every number is raw bytes from sysfs or kB from `/proc/<pid>/status`.

### 4.2 Attribution, which is the failure this box has already had

`../adjoint_unblock_reproduce/RESULTS.md:286-292`:

> *"`docker stats` reports **every** running container on the box, and the watcher's raw maximum
> … is **9.786 GiB** — which belongs to `p2a6_stock`, **Lane A's container**, not to this lane.
> … A peak-RSS number from a shared-box watcher is a claim about a named container or it is not a
> measurement."*

**A W4 lane is live on this box right now** (§3). The instrument therefore takes a container
**name**, resolves it to a cgroup, and reads **only** that cgroup; it cannot see a peer's
container, and it **refuses (exit 2)** if it never resolves the container it was given. That is
why `[D-1]` adds `--name` — the graded chain let docker generate names like `priceless_jepsen`,
which is exactly how the misattribution above became possible.

### 4.3 Disclosed departures from the graded chain

| # | departure | effect on the solve | why |
|---|---|---|---|
| **D-1** | `--name b3rss_<ARM>` added | none | §4.2: a peak is attributable or it is not a measurement |
| **D-2** | after `mpirun` exits, the container prints `CGROUP_PEAK_BYTES=$(cat /sys/fs/cgroup/memory.peak)` and re-raises `mpirun`'s status | none — runs only after the solve, exit status preserved | the external sampler can only see the peak up to its last tick before teardown (<= 2 s of exposure); this line is **exact at exit**. If it is unreadable the sampler's value stands and the grader says which was used |
| **D-3** | new run root; **the graded run root is not written to** | none | the 2026-08-21 evidence stays untouched |
| **D-4** | the watcher process itself (a `bash` loop, 2 s cadence) | negligible, and it is **outside** `--cpuset-cpus 0-3` | it is the point of the item |
| **D-5** | the box carries a live peer lane; the 2026-08-21 chain ran with `load ≈ 11–15` | **wall time may differ, and therefore core-minutes** | disclosed rather than hidden. **M0 grades on iteration counts and printed digits, which are load-independent**; §5.3 registers what a wall-time difference does and does not mean |

**No other difference is intended. If phase 2 discovers one, it is an addendum, and it cannot
move a band.**

### 4.4 The planted control — standing rule 3

> *A zero from a reader not shown able to see a non-zero is not evidence.*

The memory analogue: **a peak from an instrument not shown able to see a known peak is not
evidence.** Before any graded arm, `b3_rss_watch.sh --selftest` runs a container **of the same
image** which allocates **2 GiB of anonymous memory and touches every page**, and the watcher must
read it back:

| instrument | must read back | band |
|---|---|---|
| tree RSS peak | the planted 2.00 GiB | **2.00 – 2.60 GiB** |
| `memory.peak` | the planted 2.00 GiB plus image/interpreter overhead | **2.00 – 3.50 GiB** |

**Outside either band, the self-test exits 2 and the item does not launch a graded arm.**
`analyse_peak_rss.py` **refuses (exit 2)** if `selftest/selftest_verdict.txt` is absent or does not
say `PASS` — demonstrated before this commit against the not-yet-existing run root:

```
$ python3 analyse_peak_rss.py /home/ubuntu/certonomous-runs/B3-decomposition-peakrss
analyse_peak_rss: REFUSE: no planted-control verdict at …/selftest/selftest_verdict.txt --
the watcher was never shown able to see a peak it did not choose; every number below would be
uncontrolled
exit=2
```

The trigger path of the kill is separately self-tested against a sentinel (§3.1).

---

## 5. Predictions, with bands, fixed now

### 5.1 The basis, every figure read for this file

| measurement | value | path:line | comparability to this item |
|---|---|---|---|
| **D-scotch, np=4, this exact case/image/DV** — the adjoint | **9.044 GiB** | `../adjoint_unblock_reproduce/RESULTS.md:277`, `:290` | **closest basis there is.** Same 21,000-cell CBFS, same `dafoam-subpclu:v2`, same beta DV, same `compute_totals`, np=4, 12 GiB cap. Differs only in partitioner. **Instrument: 5 s `docker stats` max — a lower bound on the true peak** |
| **D-serial, np=1, this item's own arm** | **6.156 GiB** | `decomposition_np4/RESULTS.md:120`, `:132` | same arm, but **one `docker stats` sample mid-solve**, explicitly *"not a true peak"* |
| FD point, primal-only, same case/image | 1.444 GiB | `../adjoint_unblock_reproduce/RESULTS.md:290` | primal only; bounds how much of the peak is the adjoint |
| A6 N=16 CRM adjoint, 41,760 cells, np=1 | 9.787 GiB | `ladder-a/A6/rung_n16_np1/RESULTS.md:373`, `:390` | **different case and 2× the cells** — a scale reference only |
| A6 N=16 primal-only arms, largest of any arm | 1.252 GiB | `ladder-a/A6/rung_n16_fixed_reference/RESULTS.md:97`, `:695` | **primal-only; the record itself says the 9.787 adjoint figure "does not transfer"** (`rung_n16_fixed_reference/PREREGISTRATION.md:433`). Cited to bound the primal share, not to predict an adjoint |
| offline `splu` of the whole `dRdWTPC` | `nnz(L+U)` 3.22e+08–3.90e+08, *"roughly 3 GB"* | `PROOF.md` §25.3, via `decomposition_np4/PREREGISTRATION.md:69` | **the basis that missed high last time** — it predicted D-serial at 10–14 GiB against a 6.156 GiB sample, because in-solver `PCLU` on one ASM block is not SuperLU's object (`decomposition_np4/RESULTS.md:123-127`) |

### 5.2 The bands

**`memory.peak` is predicted to read HIGHER than tree RSS and higher than the `docker stats`
figures above**, because it includes page cache charged to the cgroup (mesh and field reads over
the bind mount, the log, the coloring file) which `docker stats` MemUsage subtracts as
`inactive_file`. **Both bands are set wide because this lab has never taken either measurement on
this case, and a narrow band invented from a different instrument would be a band chosen to be
hit.**

| row | quantity | band, fixed now | basis |
|---|---|---|---|
| **M2a** | `D_simple2` (np=4) **peak tree RSS** | **6.0 – 11.0 GiB** | D-scotch's 9.044 GiB is a `docker stats` max, an upper-ish proxy for tree RSS and itself an undersample; `simple 4×1×1` block sizes are comparable to `scotch`'s |
| **M2b** | `D_simple2` **`memory.peak`** | **8.0 – 12.0 GiB** | >= M2a by construction; >= 9.044 expected since the 5 s watcher undersamples and `memory.peak` counts cache. **Upper edge is the cap: a value at 12.0 is a cap-limited peak, not a free one, and M5 catches it** |
| **M3a** | `D_serial` (np=1) **peak tree RSS** | **5.5 – 9.0 GiB** | the 6.156 GiB sample is a lower bound; the peak sits in the whole-matrix LU factorisation, which the mid-solve sample may or may not have caught |
| **M3b** | `D_serial` **`memory.peak`** | **6.0 – 11.0 GiB** | >= M3a; the primal+colouring phase alone ran 1064 s and pulls the mesh through cache |
| **M4** | **ordering**: peak(np=4) > peak(np=1) on **both** instruments | **PASS = strictly greater on both** | D-scotch 9.044 vs D-serial 6.156 on the same instrument. Four ranks each holding an ASM-block LU against one rank holding one whole-matrix block LU. **This is the falsifiable claim in the item**: if the serial LU is the larger object, M4 fails and the "np=1 is the arm at risk" reasoning of `decomposition_np4/PREREGISTRATION.md:69` is vindicated a run too late |
| **M5** | rc=0 both arms; `memory.peak` **strictly** below 12 GiB; no watcher abort; max inter-sample gap <= 5 s; >= 30 samples per arm | **PASS = all** | an OOM or a cap-limited peak makes the number a statement about the cap, not about the run |
| **M0** | **identity**: each arm reproduces `reason`, iteration count, 16-digit `OBJ`, the full `GRAD n=/norm=/min=/max=` line, the iteration-0 residual, and the sub-LU banner | **PASS = every digit identical** | §5.4 |

**Registered directional prediction, stated so a miss is a miss:** the true peaks come out
**above** the `docker stats` figures now on the record — i.e. `D_serial` **above 6.156 GiB** and
`D_simple2` **above 9.044 GiB** — because a 5 s `docker stats` maximum undersamples and excludes
cache. If either lands *below* its predecessor's figure, that is a **MISS** and is reported as
one, and it would mean the earlier figures were not the underestimates this file assumes.

### 5.3 What a wall-time difference means, registered in advance

The box carries a live peer lane (§3, D-5). **If an arm's wall time differs from 2026-08-21's,
that is a load artefact and is NOT a finding**, provided M0 holds — iteration counts and printed
digits are load-independent, and the precedent is on the record: arms S and R performed the
identical computation and took **342 s and 89 s** from a cold versus warm page cache
(`../adjoint_unblock_reproduce/RESULTS.md:294-300`). **Core-minutes are charged as measured
regardless**, and a wall-time overrun is charged against §6's ceiling, not excused by the peer.

**A cold page cache is, however, a real difference for `memory.peak`**, which counts cache. This
is registered now: if `D_serial`'s `memory.peak` far exceeds its tree RSS, the gap is cache, and
**the tree-RSS number is the one to carry into a sizing decision** while the `memory.peak` number
is the one to carry into a cap decision. Neither is "the" answer alone.

### 5.4 M0, and what a failure of it does

M0 checks, per arm, against digits frozen in `analyse_peak_rss.py`:

| arm | reason | iters | `OBJ varianceU` | `GRAD` line | iter-0 residual |
|---|---|---|---|---|---|
| `D_serial` | 2 | **163** | `1.5279275989724403e-02` | `n=21000 norm=1.4557054356e-05 min=-4.694385e-07 max=1.915505e-06` | `7.091589775454e-04` |
| `D_simple2` | 2 | **766** | `1.5279278602317540e-02` | `n=21000 norm=1.4558490322e-05 min=-4.694298e-07 max=1.915990e-06` | `7.091590381747e-04` |

(from `decomposition_np4/RESULTS.md:49-51` and `…/B3-decomposition-np4/grading.json`.)

**If M0 fails, the re-run is a variant of the graded chain and its peak does not attach to the
graded row.** The item then returns **`NOT A RESULT`** for the attachment question, the measured
peak is reported as belonging to the re-run arm alone, and every band row is reported as
`NOT A RESULT` too. **A gate may only turn a PASS or GATE FAIL into NOT A RESULT, never the
reverse**, and the grader implements exactly that ordering.

**The one M0 clause with a known innocent explanation, registered now so it is not waved through
later:** `D_simple2`'s iteration count could move if the coloring is regenerated differently.
`decomposition_np4/PREREGISTRATION.md:37` registered that ASM block boundaries move the count and
that *"a different count is expected and is not a finding"* — **but that was for a different
partitioner. Here the partitioner is identical, so 766 is expected exactly, and anything else is
an M0 failure, not a shrug.**

---

## 6. Strict completion — an arm is done only if all of it holds

Per arm, all clauses, no degradation:

1. `rc = 0` from the `timeout … docker run` (recorded in `ledger.csv`).
2. The log carries `**Completed**! Total iterations: N. PetscConvergedReason: 2.` — the `End`-line
   analogue for this solver.
3. `N` equals the arm's archived iteration count (§5.4).
4. `OBJ varianceU:` and `GRAD n=21000 norm=… min=… max=…` both present, and every digit matches.
5. The sub-LU banner `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` present —
   **its absence means the arm ran stock and the arm is void** (`TOOLCHAIN_INVENTORY.md:142`).
6. `<arm>/cbfs_beta_grad.npy` exists and is **NEWER than the staged `<arm>/runScript.py`** — the
   **age guard**: staging touches the run script last, so the artefact must postdate the run that
   was allowed to produce it. A guard refuses an arm directory that already holds
   `cbfs_beta_grad.npy`, `processor*/` or a numeric time directory at staging time.
7. The watcher log for the arm holds **>= 30 samples** with **max inter-sample gap <= 5 s**, and
   its first sample precedes the container's first resolvable moment and its last follows the
   container's disappearance. **A peak from a watcher that was not running for the whole arm is
   not a peak**, and the grader refuses rather than reporting a partial maximum.
8. `selftest/selftest_verdict.txt` says `PASS` (§4.4). **Absent or failing, the grader refuses and
   nothing below is reported as a measurement.**

**Any clause failing makes the arm not done. Not "mostly done".**

---

## 7. Cost, registered before the runs

Unit: **core-minutes = wall s × ranks ÷ 60** (`CLAUDE.md` rule 12). `D_serial` is charged at
**1 rank** although its container is given `--cpuset-cpus 0-3`; that is the charter's definition
and it is what the graded ledger used (1266 s × 1 ÷ 60 = 21.10).

| item | ranks | basis | est. wall | **est. core-min** |
|---|---|---|---|---|
| planted-control self-test | 1 | 2 GiB allocation + 25 s hold + image start | ~60 s | **1.0** |
| `D_serial` | 1 | measured 1266 s on 2026-08-21 | ~1300 s | **21.7** |
| `D_simple2` | 4 | measured 301 s on 2026-08-21 | ~320 s | **21.3** |
| watcher + staging + grading | 1 | bash loop, `rsync`, one python run | ~120 s | **2.0** |
| **estimate** | | | **~30 min wall** | **46.0** |

**Hard ceiling: 182 core-min**, and it is enforced *by construction* rather than by intention:
both arms are `timeout`-bounded and run **sequentially**, so the worst case is
`2400 × 1 ÷ 60 = 40.0` (`D_serial`) `+ 2100 × 4 ÷ 60 = 140.0` (`D_simple2`) `+ 2.0` = **182.0
core-min**, and no path exists to exceed it.

**No retries.** If an arm fails, it is reported failed. **An overrun stops the run; it does not
get a new budget** (rule 12), and a retry is a new registration with its own price — which is
also why the §6a/§6b traps of the graded item (`RESULTS.md:140-187`) are pre-empted by the
staging assertions of §2.4 rather than by a budget for re-running.

**`cost_basis`:** 46.0 core-min = 0.767 core-h × **$0.0513/core-h** = **$0.039**; the 182 core-min
ceiling = 3.033 core-h = **$0.156**. The rate is **owner-stated 2026-08-21/22 and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`**. **This box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so **every dollar figure here is reported-by-owner, not
measured.** Nothing approaches the $25 bar and nothing goes on a Sanaa list for cost. **This is
CPU on the existing box: no GPU, so the 2026-08-21 blanket applies and rule 12's GPU carve-out
does not.**

---

## 8. What this item cannot establish

- **Nothing about B3's verdicts.** G1/G2/G3 `PASS`, G4 `GATE FAIL`, G5 `PASS`, Stage 4 `BLOCKED`
  under R11 — untouched. This item measures memory and nothing else.
- **Nothing about `D-scotch`'s true peak.** It is not re-run (§2.1); its 9.044 GiB stays a 5 s
  `docker stats` maximum, i.e. a **lower bound on a lower bound**, and it remains the weakest of
  the three arms' memory figures after this item completes.
- **Nothing about a different cap.** Every number here is measured **under `--memory=12g`**. A
  cgroup limit changes reclaim behaviour, so `memory.peak` under a 22 GiB cap is not predictable
  from `memory.peak` under 12 GiB — and W4's original 22 GiB figure was never measured at all
  (`../adjoint_unblock_reproduce/RESULTS.md:280-283`).
- **Nothing about other partitionings, other `np`, other cases, or scaling.** Two points on one
  21,000-cell case. `A3/original_memory_plan/PREREGISTRATION.md:38` **already excludes** the B3
  arm Pβ figure from every scaling model it builds; these numbers do not earn it a place.
- **Nothing about whether the gradient is right.** Memory is orthogonal to correctness, and
  `decomposition_np4/RESULTS.md:243-247` stands: *"invariance is necessary, never sufficient."*
- **Nothing about the MemAvailable launch-gate question itself.** This item produces an input to
  that ruling — what the arms actually use — and **the ruling is Sanaa's**. No agent may move the
  12 GiB threshold on the strength of these numbers (rule 9).
- **Nothing about peak memory of anything the watcher was not pointed at.** By design (§4.2), it
  sees one named container's cgroup and nothing else on this shared box.

---

## 9. Phase-2 launch sequence, registered

Nothing below has run. **It runs only after the supervisor has verified this pre-registration's
commit** — the four §3 checks are the supervisor's and are not delegated to this lane.

1. `mkdir -p $R/{logs,selftest}`; assert `$R` did not previously exist.
2. Assert `docker inspect -f '{{.Id}}' dafoam-subpclu:v2` == the §2.2 sha256, else **refuse**.
3. Stage `D_serial` and `D_simple2` per §2.4; assert the two `runScript.py` sha256 of §2.3, and
   assert no `processor*`, no numeric time dir, no `cbfs_beta_grad.npy` in either — else refuse.
4. `b3_rss_watch.sh --selftest $R/selftest` — trigger path **and** planted 2 GiB. Its plant
   container is the **first** container of the chain and runs the graded image, so it also carries
   the content assertion: it prints `md5sum …/src/adjoint/DALinearEqn/DALinearEqn.C` into
   `selftest/selftest_plant.log` and the item **stops** unless it equals
   `5b3159f88dbefcf7c52bd888401d097f` (§2.2). **Stop the item on anything but PASS.**
5. Gate: `MemAvailable >= 12 GiB` and `load <= 10`, bounded 20 min, else **`BLOCKED`**.
6. Start `b3_rss_watch.sh b3rss_D_serial $R/logs/D_serial_rss.log 1300 4194304` in background;
   launch `D_serial` (§2.5, `timeout 2400`, `-np 1`) in the foreground; append the ledger row.
7. Repeat 5–6 for `D_simple2` (`timeout 2100`, `-np 4`, watcher max-ticks 1100).
8. `python3 analyse_peak_rss.py $R` → `peak_rss.json` and the graded table.
9. Write `RESULTS.md` beside this file. **Nothing is filed, sent or pushed.**

---

*Nothing below this line existed when this file was written. No container has been started for
this item. The arms launch only after this file lands and the supervisor says go.*
