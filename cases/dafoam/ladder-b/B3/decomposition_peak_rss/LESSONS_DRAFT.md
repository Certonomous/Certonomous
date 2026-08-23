# DRAFT proposed records — B3 decomposition peak RSS

**DRAFT. NOT APPENDED.** These are proposals for `docs/LESSONS.md`, `docs/DOCKET.md` and
`docs/NUMERICS_KNOWLEDGE.md`. **The append is the supervisor's, through
`scripts/append_record.py`.** Nothing here is filed, sent or numbered by this lane.

**Numbers are deliberately left blank.** Standing rule 11: lesson and docket numbers are assigned
**at commit, from the tail — the maximum existing number, never a count**, and re-derived in the
same shell invocation because peers commit constantly:

```
grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n | tail -1
```

---

## Proposed lesson A — `docker stats` has now failed this lab twice as a memory instrument

**Both failures are on the record, in different teams, and neither was a mistake of arithmetic:**

1. **Field-position parse.** `ladder-a/A6/rung_n16_np1/RESULTS.md:366-381`: the sample format is
   `<ts> <arm> 9.787GiB / 12GiB` and **field 3 is the used figure**; a reader taking a different
   field turned **9.787 GiB into 7.396 GiB** — a 24 % understatement of a number that was being
   used to size a memory envelope.
2. **Cross-container misattribution.** `ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md:286-292`:
   `docker stats` reports **every** container on the box, and the watcher's raw maximum
   **9.786 GiB belonged to another lane's container** (`p2a6_stock`), not to the lane reading it.
   Caught before publication, and only because the lane checked.

**The instrument that is immune to both**, measured in this item 2026-08-23:

- **cgroup v2 `memory.peak`** — kernel high-water of `memory.current`, monotone non-decreasing,
  read as **raw bytes** from the container's own cgroup. No formatted size string to mis-parse,
  and it is per-cgroup, so cross-container attribution is impossible by construction.
- **per-pid `VmHWM`** from `/proc/<pid>/status` — kernel per-process high-water, which answers
  *which process*, a question no container-level number can answer.

**Accuracy, measured against a planted control rather than asserted.** A container of the graded
image allocated and **touched** 2.00 GiB; the instrument read back **2.0083 GiB** tree RSS
(+0.42 %) and **2.0118 GiB** `memory.peak` (+0.59 %).
Artefact: `/home/ubuntu/certonomous-runs/B3-decomposition-peakrss/selftest/`.

> **The generalisable claim:** a peak-memory figure from `docker stats` is a claim about a
> *formatted string* on a *shared box*. A figure from `memory.peak` is a claim about one cgroup,
> in bytes, from the kernel. Prefer the second, and when quoting the first, name the container.

---

## Proposed lesson B — staging a case into a container must reproduce the graded directory MODES, not just the file list

**Cost when learned: 20.4 core-min, two dead arms, zero graded numbers** (this item, 2026-08-23).

The container runs as **`uid=1002(dafoamuser)`**; the run root is owned by **`ubuntu` (uid 1000)**.
The 2026-08-21 graded arm directories were **`drwxrwxrwx` (777)**. Staging by `cp` under the
default umask 022 produced **`drwxr-xr-x` (755)**, and OpenMDAO's `Problem.setup()` →
`get_reports_dir()` (`openmdao/core/problem.py:2186`) does an unconditional
`pathlib.mkdir(parents=True)` for `reports/` in the working directory. Result:
`PermissionError: [Errno 13] Permission denied: 'reports'`, **before any solver work**.

**A staging checklist that lists files and not modes is incomplete.** The item's own
pre-registration §2.4 registered exactly which files to stage, asserted their sha256, asserted the
absence of run products — and said nothing about modes, so the assertion suite passed on a
directory the solver could not run in.

**The diagnosis was taken with a positive control, and that is the transferable part.** One
container, two directories differing only in mode: `m755` → `mkdir reports` **FAILED**, `m777` →
**SUCCEEDED**. A bare permission-denied is consistent with a broken test; a reader shown to
succeed on 777 proves the mode is the cause. *(Related in spirit to the planted-zero rule: a
failure from a reader not shown able to succeed is not a diagnosis.)*

---

## Proposed lesson C — a rank-0 exception under `mpirun` does not abort the job, and a `timeout`-bounded chain then burns `ranks x timeout` core-minutes

**This is a budget trap, not just an annoyance, and it is the more valuable of the two harness
findings here.**

When rank 0 raised `PermissionError` inside `prob.setup()`:

| np | what happened | wall | core-min if left to `timeout` |
|---|---|---|---|
| **1** (`D_serial`) | clean: `mpirun detected that one or more processes exited with non-zero status`, rc 1 | **7 s** | 0.12 |
| **4** (`D_simple2`) | **hung.** Log frozen, **no** `mpirun detected` line, rank 0 at 5.7 % CPU post-exception, **ranks 1–3 spinning at 99.8 % CPU each** in a collective waiting on a rank that will never arrive | stopped at **302 s** | **would have been 140.0** at `timeout 2100` |

**140.0 core-min is 77 % of this item's entire registered 182.0 core-min ceiling, spent on a run
that could not produce a result** — and three spinning ranks steal cores from peers on a shared
box the whole time.

**The detection signature, all three together:**
1. the log stops growing;
2. **no** `mpirun detected …` abort line, where the serial arm has one;
3. ranks at **~100 % CPU** with flat RSS.

**Proposed practice:** a chain that runs `np > 1` arms should carry a **progress watchdog**, not
only a `timeout` — the `timeout` is an upper bound on damage, not a detector. A watcher that
already samples per-pid RSS every 2 s (this item's `b3_rss_watch.sh`) has the data to notice a
flat-RSS/high-CPU stall and could stop it; **it does not do so today**, and that is the gap this
lesson names. *(Kin to L-239: a bound that nothing is wired to act on is not a guard.)*

---

## Proposed docket rows

| item | proposed status | note |
|---|---|---|
| B3 decomposition peak RSS | **PENDING** | pre-registration + frozen instruments committed `d062aace` before any compute; first attempt lost to the §A1.2 staging defect; **repair PROPOSED, not taken** — awaiting the supervisor's crash-triage ruling under §7's "no retries" clause |
| Progress watchdog for `np > 1` chains | **PROPOSAL** | lesson C; no owner assigned by this lane |

**Spend to record against the item: 21.0 core-min = \$0.018**, **reported-by-owner, not
measured** (`COMPUTE_BUDGET_CHARTER.md` §5). **100 % waste, 0 graded numbers**, 161.0 core-min of
the registered ceiling unspent.

---

*Nothing in this file has been appended to any repository record. Nothing was sent, filed or
uploaded. Numbering and the append are the supervisor's.*
