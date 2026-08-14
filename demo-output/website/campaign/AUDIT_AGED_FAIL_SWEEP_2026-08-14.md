# Aged-FAIL Triage Sweep
Date: 2026-08-14

## Executive Summary

The self-audit identified **10 FAILs** and **8 WARNs**. This sweep inventories every FAIL by age, severity, and docket coverage. All 10 FAILs are at FAIL severity; none are currently tracked in docs/DOCKET.md.

**Exit status:** 1 (FAILs present)  
**Count: 10 FAILs, 8 WARNs, 3 INFOs**

## Uncovered Aged FAILs (sorted by age, descending)

| Check | Severity | Files Implicated | Age (days) | Docket Row |
|-------|----------|------------------|-----------|-----------|
| gate table vs transcripts | FAIL | Ahmed body, 25 deg slant: verdict published 'SOLVER-BACKED', re-derived 'see record' from mission-output/ahmed-body/transcript.txt | 4+ | NONE |
| non-conclusive band readers | FAIL | sdk/scripts/run_uq_studies.py:518 b52_fourth_rung() reads band_abs without checking conclusive flag | 4 | NONE |
| cited evidence paths | FAIL | demo-output/website/campaign/LADDER_V_PASS1_2026-08-11.md:453 → demo-output/benchmarks.html (missing); demo-output/website/campaign/LADDER_V_PASS3_COLD_2026-08-11.md:161 → scripts/rans_identity_baseline.py (missing) | 4 | NONE |
| rank claims carry their probability | FAIL | 3 files in dist/certonomous-demo.zip (benchmarks.html, closure.html, lab_stats.json) carrying rank 1 without 0-97% at 95% interval; 14 campaign files with similar claims | 3 | NONE |
| bundle drift vs tree | FAIL | dist/certonomous-demo.zip 4 files behind tree: sdk/chief_engineer/exec_bits.py differs, sdk/chief_engineer/head_engineer.py differs, demo-output/website/closure.html differs, demo-output/website/benchmarks.html differs | 3 | NONE |
| declared fleet vs work | FAIL | sdk/workflows/ahmed_body.py:424 declares workers in restored-path branch that dispatches nothing; sdk/workflows/geometry_study.py:1934 same pattern | 3 | NONE |
| ladder rungs share one recipe | FAIL | cube: compares rungs through refinement fit that declined to fit order, fallback band carries no recipe audit; motorBike: publishes observed order 7.298 with no recipe audit; naca0015_sail: publishes observed order 1.696 with no recipe audit | 3 | NONE |
| studies carry what the fit records | FAIL | b52.json: numerical block missing asymptotic field (fit records 14 fields, study carries 13) | 2 | NONE |
| wall credentials vs results | FAIL | 5 credentials do not re-derive: cube '1.104' vs '1.1042'; flat_plate '0.03238' vs '0.0324'; naca0012_wing '0.01205' vs '0.0121'; naca4412_wing '0.01826' vs '0.0183' (2 issues) | 2 | NONE |
| FD grades vs current standard | FAIL | 7 FD entries carry grades the current standard does not give: demo-output/website/ACTIVE_RESEARCH.md (6 entries: 10.04% PASS vs CONDITIONAL, 8.953%, 0.232%, 0.232%, 1.67%, 11.43%); demo-output/website/campaign/reports/MORNING_REPORT_2026-08-04.md and 2026-08-07.md (2 entries) | 2 | NONE |

## Summary of Coverage

- **Total FAILs:** 10
- **Uncovered FAILs:** 10 (100%)
- **Docket rows covering FAILs:** 0

## Reach of This Sweep

**What this sweep saw:**
- All 34 audit checks and their results from `python3 scripts/self_audit.py`
- Git history for key implicated files (campaigns, wall.json, bundle, workflows)
- Docket.md rows cross-referenced against FAIL names and implicated files
- File existence verification for cited-evidence paths

**What this sweep could NOT see:**
1. Whether FAILs existed before the audit checks were added (checks added 2026-08-12; cannot definitively determine when underlying conditions first appeared)
2. Untracked files outside repo scope (e.g., run logs, archived fields under certonomous-runs/ as noted in docket D9)
3. Whether a FAIL has a "silent" docket row (one using different terminology) — sweep matched on check name, file names, and keywords but manual review may find implicit coverage
4. Precise commit when a condition first became true vs. when it was first observed (git log shows file modification, not condition onset; e.g., rank-claims surfaces written without intervals may predate the documents' commit date if pulled from archived runs)
5. Whether repair history exists in other branches or work-in-progress branches not visible to `git log --all`

## Files Examined

- scripts/self_audit.py (last modified 2026-08-12, 2 days old)
- dist/certonomous-demo.zip (last rebuilt 2026-08-11, 3 days old)
- demo-output/website/wall/wall.json (last modified 2026-08-12, 2 days old)
- Campaign documents: 2026-08-10 to 2026-08-11 (3-4 days old)
- Workflow files: 2026-08-11 (3 days old)
- docs/DOCKET.md: 396 lines, full row search completed

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
