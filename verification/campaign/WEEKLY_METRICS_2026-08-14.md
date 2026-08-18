# Weekly Metrics — ending 2026-08-14

**Reporting period:** 2026-08-07 to 2026-08-14 (7 calendar days)

**Observed commit counts by day:** See distribution below. Days with zero commits: 08-09, 08-13. 
**Reported power-off window:** 08-12 evening through 08-14 20:22 UTC.

**Actual commit distribution by day:**
```
git log --since='2026-08-07' --until='2026-08-15' --pretty=format:'%cd' --date=format:'%m-%d' | sort | uniq -c
    34 08-07
   105 08-08
     0 08-09
   231 08-10
   275 08-11
    24 08-12
     0 08-13
     4 08-14
```

**Calculation conventions:** 
- **Per calendar day** (7 days): 672 / 7 = ~~96 commits/day~~ [2026-08-14: THIS FIGURE DIVIDES BY CALENDAR DAYS, NOT ACTIVE DAYS; SEE NEXT LINE]
- **Per active day** (6 days with any commits: 08-07, 08-08, 08-10, 08-11, 08-12, 08-14): 672 / 6 = ~~≈ 134 commits/day~~ [2026-08-14: MISMATCH FIXED — PREVIOUS CALCULATION INCLUDED 08-12's 24 COMMITS IN NUMERATOR BUT EXCLUDED THE DAY FROM DENOMINATOR] = **112 commits/day**

**Note on 08-12 collapse:** Commit count dropped from 275 on 08-11 to 24 on 08-12, an order-of-magnitude collapse on the day of the lab's largest autonomous fleet. The cause is undetermined. To settle it would require: (1) session transcripts under `/home/ubuntu/.claude-sanaa/sessions/` for 08-12, and (2) whether the auto-stop gate fired that day. This observation is factual; no cause is asserted here.

---

## Git-based Metrics

### 1. Commits (week ending 2026-08-14)

```
git log --since='2026-08-07' --until='2026-08-15' --oneline | wc -l
```

**Result:** 672 commits (see Calculation conventions section above for per-day breakdown)

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

**Activity metrics** (volume, not quality): Commits: 672 over 7 calendar days (112/day on days with any work: 08-07, 08-08, 08-10, 08-11, 08-12, 08-14). Files touched: 5,678 unique. Docket changes: 43 commits.

**Improvement-relevant metrics** (quality or capability advancement): Test files added: 12. Calibration scorecard pairs: 11 total, 3 passing (27%), 8 undeterminable.

**Note:** Commits and unique files touched measure activity volume. A 7-day period with 5,678 files touched is not obviously good or bad without context on change size and purpose. These metrics track that work happened, not that it improved the lab's capability. Test addition and calibration pair progress are improvement metrics — they track capability increase or system maturity.

