# GRADER BLINDNESS SWEEP — 2026-08-25

## Executive Summary

Executed `check_grader_self_blindness.py` on all 16 ansys-verification comparators. All files returned exit code 0 (clean on both probes). The selftest verifies both probes can fire correctly and stay silent on clean code. Two frozen graders verified unchanged at sweep end.

---

## Script Invocation and Exit Codes

**Usage:**
```
python3 scripts/check_grader_self_blindness.py --selftest
python3 scripts/check_grader_self_blindness.py <file.py> [<file.py> ...]
```

**Exit codes:**
- `0`: No findings (clean on both probes, or selftest passed)
- `1`: WARN level finding(s) detected
- `2`: ERROR level finding(s) detected

**Selftest validation:** PASSED — both probes shown able to fire on planted defects and stay silent on clean counterparts.

---

## Defect Shapes (from script docstring)

### Defect Shape A (L-322): Unrepresentable Outcome

A grader that cannot REPRESENT an outcome its own registered rules MANDATE. Example: `grade_f3.py` built `report["runs"][key]` at two sites with different key sets — the `PENDING` branch (run directory absent) omitted `core_s`, but the summary then read `v["core_s"]` across every entry. When the budget cap fired (exactly as registered), the grader crashed on it.

**Probe A flags:** Two or more `dict(...)` assignments to the SAME subscript target whose keyword-key sets DIFFER, where any consumer reads a key that some branch does not write.

### Defect Shape B (L-321): Fixture and Checker Share Assumption

A fixture that constructs its artifact by the SAME route the reader resolves it shares one wrong assumption with the checker, so the two agree and their agreement carries no information. Example: `analyse_f5b_physics.py` resolved the endTime directory by string-matching `END_TIME_STR` and its `_synthetic_run` fixture CREATED that directory from the same constant — so every selftest passed while `case/21.9440/` never existed on a real run (OpenFOAM writes `case/21.944/`).

**Probe B flags:** A module-level uppercase constant used BOTH to BUILD a path in a fixture/synthetic AND to RESOLVE/match a path in checked code.

---

## Comparators Swept

**Grade files in cases/ansys_verification/ (13 files):**
1. `cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py`
2. `cases/ansys_verification/VMFL001/grade_vmfl001.py`
3. `cases/ansys_verification/VMFL003/grade_vmfl003.py`
4. `cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2.py`
5. `cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2_omega.py`
6. `cases/ansys_verification/VMFL005/grade_vmfl005.py`
7. `cases/ansys_verification/VMFL007/grade_vmfl007.py`
8. `cases/ansys_verification/VMFL007_R2/grade_vmfl007_r2.py`
9. `cases/ansys_verification/VMFL010/grade_vmfl010.py`
10. `cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py`
11. `cases/ansys_verification/VMFL045/grade_vmfl045.py`
12. `cases/ansys_verification/VMFL051/grade_vmfl051.py`
13. `cases/ansys_verification/VMFL059/grade_vmfl059.py`

**Other comparators in verification/runs/ansys_verification/ (3 files):**
14. `verification/runs/ansys_verification/append_guards.py`
15. `verification/runs/ansys_verification/check_case_map_glance.py`
16. `verification/runs/ansys_verification/reaudit_landed_blocks.py`

**Total: 16 comparators swept.**

---

## Sweep Results

| File | Exit Code | Status | Finding |
|------|-----------|--------|---------|
| cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL001/grade_vmfl001.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL003/grade_vmfl003.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2_omega.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL005/grade_vmfl005.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL007/grade_vmfl007.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL007_R2/grade_vmfl007_r2.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL010/grade_vmfl010.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL045/grade_vmfl045.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL051/grade_vmfl051.py | 0 | CLEAN | None |
| cases/ansys_verification/VMFL059/grade_vmfl059.py | 0 | CLEAN | None |
| verification/runs/ansys_verification/append_guards.py | 0 | CLEAN | None |
| verification/runs/ansys_verification/check_case_map_glance.py | 0 | CLEAN | None |
| verification/runs/ansys_verification/reaudit_landed_blocks.py | 0 | CLEAN | None |

**Summary:** All 16 comparators returned exit code 0. All files are CLEAN on both probes.

---

## Frozen Grader Verification

Per supervisor directive, re-verified the two frozen graders mentioned as byte-identical to specific commits with solver RUNNING RIGHT NOW.

**grade_vmfl003_m2.py:**
- File exists: `/home/ubuntu/Certonomous/cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2.py`
- Size: 47993 bytes
- SHA256 (working tree): `58a5c3fb13f68916c811f99c26f9143b7347ac0f428195e480d171fd6e54edaa`
- SHA256 (HEAD): `58a5c3fb13f68916c811f99c26f9143b7347ac0f428195e480d171fd6e54edaa`
- Status: No working tree changes. Working tree matches HEAD exactly.

**grade_vmfl003_m2_omega.py:**
- File exists: `/home/ubuntu/Certonomous/cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2_omega.py`
- Size: 48158 bytes
- SHA256 (working tree): `6167aaf8e0d54e94845de29c5b3f7fa70a00a8d78b9e62d1ec96ba915276e6e5`
- SHA256 (HEAD): `6167aaf8e0d54e94845de29c5b3f7fa70a00a8d78b9e62d1ec96ba915276e6e5`
- Status: No working tree changes. Working tree matches HEAD exactly.

**Conclusion:** Both frozen graders are unchanged. The sweep introduced no modifications.

---

## Sweep Execution Details

- Sweep date/time: 2026-08-25
- Script location: `/home/ubuntu/Certonomous/scripts/check_grader_self_blindness.py`
- Script version: Checked via `git show HEAD:scripts/check_grader_self_blindness.py`
- Selftest run before production sweep: PASSED
- Solver PIDs checked (preserved): 2324887, 2324888 in `verification/runs/ansys_verification/VMFL003_M2/C_RNGkEpsilon/L2_500x5` — not touched.
- Files modified during sweep: None (read-only scan only).

---

## Notes

- Neither probe is a proof of correctness — they are cheap static smells for two high-cost shapes.
- A clean report is not a guarantee of safety; a flag is a thing to look at.
- The supervisor noted that CLAUDE.md rule 5 speaks of `PASS` and mandates `NOT A RESULT` gates remain reachable. The team returns `GATE REACHED` in-band by declared tier ceiling. Probe A is live-relevant to this pattern: if the tool flags an unrepresentable outcome on any of these graders, that would be a finding requiring full detail.
- Three live instances of these defects were found across the lab on 2026-08-25 before this sweep.

