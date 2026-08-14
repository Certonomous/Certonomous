# Weekly Metrics — ending 2026-08-14

**Reporting period:** 2026-08-07 to 2026-08-14 (7 calendar days)

**Power outage:** Reported period 2026-08-12 evening (UTC) to 2026-08-14 20:22 UTC.
Approximately 2 days of the 7-day week were idle.

**Convention for rates:** All metrics computed over the full calendar week including the idle period.
This means any per-day average includes the power-off days as zero-activity days. Where a per-day
rate is given, it reflects the ratio of activity to calendar days, not to active days.

---

## Git-based Metrics

### 1. Commits (week ending 2026-08-14)

```
git log --since='2026-08-07' --until='2026-08-15' --oneline | wc -l
```

**Result:** 672 commits

**Per-day average:** 672 / 7 = 96 commits/day (includes idle days)

---

### 2. Files Touched (unique files modified)

```
git log --since='2026-08-07' --until='2026-08-15' --name-only --pretty=format: | sort -u | grep -v '^$' | wc -l
```

**Result:** 5,678 unique files modified

**Per-commit average:** 5,678 / 672 = 8.45 files per commit

---

### 3. Test Files Added

```
git log --since='2026-08-07' --until='2026-08-15' --diff-filter=A --name-only --pretty=format: | grep -E '(test_|_test\.py|tests\.py)' | wc -l
```

**Result:** 12 test files added

**Existing test suite:** 62 test files in repository (state: not executed, read-only diagnostic)

---

### 4. Docket Activity

```
git log --since='2026-08-07' --until='2026-08-15' --oneline -- docs/DOCKET.md | wc -l
```

**Result:** 43 commits touching docs/DOCKET.md

**Current docket size:** 396 lines, ~83 active items (from table row count)

---

### 5. Calibration Scorecard

Related metric (not strictly this week, but current state):

```
python3 scripts/calibration_scorecard.py
```

**Result:** 11 scoreable pairs (proposals with both est_core_min and measured_core_min)
- Hit rate: 27% (3 of 11 within 20% tolerance)
- 8 proposals marked done with no measured cost available (undeterminable)
- Rule runnable but not satisfied (needs 3-for-3 hits within 20%)

**Brought current this week:** 8 proposals updated with measured_core_min from campaign records

---

## Summary

**Commits:** 672 over 7 days (includes 2-day outage period)
**Files touched:** 5,678 unique
**Test files added:** 12
**Docket changes:** 43 commits to docket during week
**Calibration pairs:** 11 total, 3 passing (27%), 8 undeterminable

