# Aged-FAIL Triage Sweep
Date: 2026-08-14

## CORRECTION (2026-08-14 post-publication)

**First pass coverage was incomplete.** This document initially reported "10 (100%) uncovered" by matching check names against DOCKET.md text only. Subsequent review found three FAILs explicitly covered by docket entries:

1. **rank claims carry their probability** — **COVERED by D56** (explicitly names the zip and the stale figures)
2. **bundle drift vs tree** — **COVERED by D56** (the bundle itself is the finding)
3. **non-conclusive band readers** — **COVERED** (recorded 2026-08-02 as "precisely the defect the check was written for", uncleared 12 days)
4. **ladder rungs share one recipe** — **COVERED** (explicitly excluded from carve-out in same check)

The remaining 6 FAILs may have additional coverage not found in this mechanical sweep. See reach notes below.

## Executive Summary

The self-audit identified **10 FAILs** and **8 WARNs**. This sweep inventories every FAIL by age, severity, and docket coverage. Audit exit status: 1 (FAILs present).

**Revised Coverage:** 6 uncovered, 4 covered (at minimum by D56 and dated 2026-08-02 entries).  
**Count: 10 FAILs, 8 WARNs, 3 INFOs**

## All FAILs, sorted by age of source file (descending)

| Check | Severity | Files Implicated | Source File Age | Docket Row | Note |
|-------|----------|------------------|-----------------|-----------|------|
| gate table vs transcripts | FAIL | Ahmed body, 25 deg: verdict 'SOLVER-BACKED' vs re-derived 'see record' | ~4 days* | ? | Check added 2026-08-12; condition onset unknown |
| cited evidence paths | FAIL | 5 citations to non-existent files (rans_identity_baseline.py, check_converge_rule.py, analyze_fd.py, benchmarks.html) | 4 days | NONE | Files not in git history |
| **non-conclusive band readers** | **FAIL** | **sdk/scripts/run_uq_studies.py:518** | **~4 days*** | **COVERED (2026-08-02)** | **Recorded as "precisely the defect the check was written for"** |
| **rank claims carry their probability** | **FAIL** | **dist/certonomous-demo.zip (3 files); 14 campaign documents** | **3 days** | **D56** | **Covered: zip falsified figures documented, check now reports WARN not FAIL** |
| **bundle drift vs tree** | **FAIL** | **exec_bits.py, head_engineer.py, closure.html, benchmarks.html (1 file remains after e9144bcb rebuild)** | **3 days** | **D56** | **Critical: bundle rebuilt 2x today (e9144bcb 21:08, bd3da3a1 21:17) but re-stales in 7 min when sources change** |
| declared fleet vs work | FAIL | ahmed_body.py:424, geometry_study.py:1934 | 3 days | ? | Workflow declarations on no-op paths |
| **ladder rungs share one recipe** | **FAIL** | **cube, motorBike, naca0015_sail** | **~3 days*** | **COVERED (explicit carve-out)** | **Excluded from check as known-acceptable shape** |
| studies carry what the fit records | FAIL | b52 study missing asymptotic field | 2 days | ? | 13 of 14 fields stored |
| wall credentials vs results | FAIL | 5 credentials fail re-derivation (cube, flat_plate, naca0012_wing, naca4412_wing x2) | 2 days | ? | Measured vs stored values |
| FD grades vs current standard | FAIL | 7 grades in ACTIVE_RESEARCH.md, MORNING_REPORT | 2 days | ? | Retired grading standard |

\* Age of source file modification, not of FAIL condition onset. Audit checks added 2026-08-12; cannot determine when underlying conditions first appeared.

## Reach of This Sweep

**What this sweep saw:**
- All 34 audit checks and their results from `python3 scripts/self_audit.py`
- Git history for key implicated files (campaigns, wall.json, bundle, workflows)
- Docket.md rows cross-referenced against FAIL names and implicated files (first pass only)
- File existence verification for cited-evidence paths

**Critical finding (post-publication):** Bundle drift is a recurring defect, not a static one. The bundle was rebuilt at e9144bcb (2026-08-14 21:08) clearing 3 of 4 drift files, then re-staled 7 minutes later when another agent (D53 G-RULE) edited sdk/chief_engineer/exec_bits.py at 21:10:56. The bundle has no automated build trigger and must be manually rebuilt whenever bundled sources change. `check_bundle_drift` will FAIL again within hours unless ownership and automation are added.

**What this sweep could NOT see (first pass):**
1. **Docket coverage by file path or indirect reference.** Swept DOCKET.md by check name only. D56 explicitly covers bundle drift but was found only after the initial report. DOCKET entries covering other FAILs may exist under different terminology. Three additional FAILs (non-conclusive band readers, ladder rungs) were identified as covered only by manual review.
2. Whether FAILs existed before the audit checks were added (checks added 2026-08-12; cannot definitively determine when underlying conditions first appeared).
3. Untracked files outside repo scope (e.g., run logs, archived fields under certonomous-runs/ as noted in docket D9).
4. Precise commit when a condition first became true vs. when it was first observed (git log shows file modification, not condition onset; e.g., rank-claims surfaces written without intervals may predate the documents' commit date if pulled from archived runs).
5. Whether repair history exists in other branches or work-in-progress branches not visible to `git log --all`.
6. Archive members inside zip files (D56 finding came from manual extraction, not from this sweep).

## Files Examined

- scripts/self_audit.py (last modified 2026-08-12, 2 days ago)
- dist/certonomous-demo.zip (last rebuilt 2026-08-14 21:17:35 by e9144bcb then bd3da3a1; previous build 2026-08-11)
- demo-output/website/wall/wall.json (last modified 2026-08-12, 2 days ago)
- Campaign documents: 2026-08-10 to 2026-08-11 (3-4 days ago)
- Workflow files: 2026-08-11 (3 days ago)
- docs/DOCKET.md: 396 lines, text search only (not exhaustive re: file paths)

## Remedies (from audit output, verbatim "NO COMPUTE" directives)

All 10 FAILs are marked in the audit output as `NO COMPUTE`, indicating no solver runs are needed to clear them. Remedies involve:
- Rebuilding the distribution bundle from corrected tree copies
- Restating published numbers with correct calculations or sources
- Correcting Python code to read additional flags
- Editing prose to include missing fields or corrected values
- Removing unreachable code paths declaring work that doesn't execute

---

**Sweep completed by:** HAIKU-A mechanical inventory agent  
**Audit script exit status:** 1 (FAILs present)  
**Output from:** `python3 scripts/self_audit.py` (full output in scratchpad/audit_output.txt)
