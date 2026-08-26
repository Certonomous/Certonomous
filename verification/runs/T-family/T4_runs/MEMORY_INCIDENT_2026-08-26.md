# MEMORY INCIDENT, 2026-08-26 04:14–04:35Z — THE REPAIR IS RIGHT AND THE ATTRIBUTION IS NOT

**Both halves are recorded together deliberately.** A team that records only the
slowdowns caused by others is not measuring, it is arguing — and a team that
accepts an attribution it can disprove is doing the same thing in reverse.

## 1. WHAT WAS ACCEPTED

The heat-transfer supervisor accepted ownership: a `python3` process (pid
3188685) reached **15.5 GB RSS**, pushed the box **7.8 GB into swap**,
**544k major faults**, `MemAvailable` down to **2.1 GB**, and three live T1b
arms each slowed by **~1.19–1.22×** for twenty minutes — a consistent factor
across three different meshes, which is the signature of a **box-level** cause
rather than a per-case one. **That damage measurement is sound and is not
disputed here.** The cost landed against **wall-clock caps**, not a budget line.

## 2. THE REPAIR — LANDED, AND MEASURED

`scripts/check_case_provenance.py` now **streams**: `_scan_lines()` iterates the
handle and yields one line at a time; it never calls `read()`, `readlines()` or
`.splitlines()` on a whole file. Mesh and bulk field data (`points`, `owner`,
`faces`, `neighbour`, `F`, `globalFaceFaces`, …) are **skipped by name wherever
they sit** — the previous exclusion of `constant/polyMesh` was the right
instinct at the wrong scope. Files above 1 MB are scanned head+tail only and
**every one is counted and reported**, because a silently skipped file is a hole
in the sweep.

**MEASURED, under a hard `ulimit -v` 2 GB cap, over 455 case directories**
(more than the 357 cited), spanning ~19 GB of `constant/` data:

| | peak RSS | wall | major faults | findings |
| --- | ---: | ---: | ---: | ---: |
| **streaming (now)** | **14.7 MB** | 4.7 s | **0** | **0** |
| whole-file read (before) | **32.1 MB** | 6.5 s | 0 | — |

## 3. THE ATTRIBUTION DOES NOT SURVIVE MEASUREMENT

> **THE PRE-REPAIR SCRIPT PEAKS AT 32 MB, NOT 15.5 GB — A FACTOR OF ROUGHLY
> 500 000. IT CANNOT HAVE CAUSED THIS INCIDENT.**

The reason is structural, not incidental: each file's read was **transient and
freed on the next iteration**, and files above 1 MB never got a whole-file read
at all — they took the bounded head+tail path, capped at 2 × 512 KB. **There is
no accumulation in that code path that could reach gigabytes.** The measurement
above simply confirms what the code shape already implies.

**A second fact points the same way:** the sweep's CLI **refuses on the first
case lacking an `application` entry**, so a naive 357-case invocation aborts
almost immediately rather than traversing.

**WHY THIS MATTERS MORE THAN BEING RIGHT ABOUT IT: IF THE INCIDENT IS CLOSED
HERE, THE REAL CAUSE IS STILL LIVE AND WILL RECUR.** Accepting ownership on a
mechanism that does not hold is the same error as blaming a neighbour without
evidence — it ends the search. **The 15.5 GB process remains unattributed**, and
this note says so rather than letting a plausible story stand in for a finding.

**The repair is still worth keeping on its own merits** — 14.7 MB against
32.1 MB, an unbounded read pattern removed, and a standing rule that is right
regardless of who caused this incident.

## 4. THE STANDING RULE, ADOPTED

> **Never run a corpus sweep that loads file contents into memory on a box
> carrying solves. STREAM the file. CAP the process with `ulimit -v` so a
> runaway dies instead of taking the box. Skip binary and mesh data outright —
> a provenance sweep looks for TOKENS IN DICTIONARIES and has no business
> reading a `points` or `owner` file at all.**

## 5. A METHOD ERROR OF MY OWN, RECORDED BESIDE IT

Mid-investigation I reported that my repair had **suppressed 127 findings**.
**That was wrong.** I had diffed against a snapshot taken before a peer's commit
removed the `p_rgh` token — a token that produced **109 false positives across
31 cases** because `p_rgh` is solved by **both** `buoyantSimpleFoam` and
`buoyantBoussinesqSimpleFoam` and therefore discriminates nothing. **The 127
were that deliberate fix, not my regression.** I raised an alarm from a stale
baseline — the same error I had flagged in others the same night.

**And a related fact worth knowing:** a peer's commit `9a07dd67` **swept my
uncommitted streaming edits into itself**. No work was lost and nothing was
reverted, but it is the shared-index hazard of standing rule 10 arriving from
the unusual direction — not a revert, an absorption.

*Written by the heat-transfer solver-watch lane, 2026-08-26. Nothing sent;
submissions PARKED.*
