# CASE_MAP AUDIT — Manual vs. Repository Records
## Date: 2026-08-25 | Auditor: ansys-lane-haiku

---

## 1. MANUAL SIDECAR: Complete Case Identifier List

**Source file:** `/home/ubuntu/Certonomous/docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`

**Extraction method:** `grep -oE 'VMFL(GPU)?[0-9]+[A-Z]?|VMFRT[0-9]+'` sorted unique.

### 1.1 Full Sorted Unique List from Manual

**VMFL family (base, no suffix):**
VMFL001 VMFL002 VMFL003 VMFL004 VMFL005 VMFL006 VMFL007 VMFL008 VMFL009 VMFL010 VMFL011 VMFL012 VMFL013 VMFL014 VMFL015 VMFL016 VMFL017 VMFL018 VMFL019 VMFL020 VMFL021 VMFL022 VMFL023 VMFL024 VMFL025 VMFL026 VMFL027 VMFL028 VMFL029 VMFL030 VMFL031 VMFL032 VMFL033 VMFL034 VMFL035 VMFL036 VMFL037 VMFL038 VMFL039 VMFL040 VMFL041 VMFL042 VMFL043 VMFL044 VMFL045 VMFL046 VMFL047 VMFL048 VMFL049 VMFL050 VMFL051 VMFL052 VMFL053 VMFL054 VMFL055 VMFL056 VMFL057 VMFL058 VMFL059 VMFL060 VMFL061 VMFL062 VMFL063 VMFL064 VMFL065 VMFL066 VMFL067 VMFL068 VMFL069 VMFL070 VMFL071 VMFL072 VMFL073 VMFL074 VMFL075 VMFL076 VMFL077 VMFL078

**VMFL family (with letter suffix):**
VMFL002B VMFL003B VMFL005B VMFL007B VMFL008B VMFL012B VMFL021B VMFL023B VMFL032B VMFL040A

**VMFLGPU family:**
VMFLGPU001 VMFLGPU002 VMFLGPU003 VMFLGPU004 VMFLGPU005 VMFLGPU006 VMFLGPU007 VMFLGPU008 VMFLGPU009 VMFLGPU010

**VMFRT family:**
VMFRT001 VMFRT002 VMFRT003 VMFRT004 VMFRT005 VMFRT006 VMFRT007

### 1.2 Counts by Family

| Family | Count | Note |
|--------|-------|------|
| VMFL (base, 001–078) | 78 | No gaps; sequential 001–078 |
| VMFL (letter suffix A or B) | 10 | 002B, 003B, 005B, 007B, 008B, 012B, 021B, 023B, 032B, 040A |
| VMFLGPU | 10 | Sequential 001–010 |
| VMFRT | 7 | Sequential 001–007 |
| **TOTAL MANUAL** | **105** | 78 + 10 + 10 + 7 |

### 1.3 Gaps in VMFL Sequential Range (001–078)

**Result:** NO GAPS. All integers from 001 through 078 present (continuous range).

### 1.4 VMFL Cases with Letter Suffix

Listed explicitly (10 total):
1. VMFL002B
2. VMFL003B
3. VMFL005B
4. VMFL007B
5. VMFL008B
6. VMFL012B
7. VMFL021B
8. VMFL023B
9. VMFL032B
10. VMFL040A

---

## 2. CASE_MAP.md from HEAD: Structure and Content

**Source:** `git show HEAD:docs/ansys_verification/CASE_MAP.md`

### 2.1 Case Row Count and Marker

**Count marker used:** Rows matching regex `^| VMFL|^| VMFRT` (case data rows, excluding header/separator rows).

**Result:** 96 case rows total
- VMFL: 78 rows (base cases 001–078 only; **no letter-suffix variants**)
- VMFLGPU: 10 rows (001–010)
- VMFRT: 7 rows (001–007)

**Total: 78 + 10 + 7 = 95 cases listed in CASE_MAP**

(The grep initially returned 96 including one summary line; excluding summary: 95 data rows.)

### 2.2 Exact Case ID Set in CASE_MAP

**VMFL (base only, no suffixes):**
VMFL001 through VMFL078 (78 cases, no variants)

**VMFLGPU:**
VMFLGPU001 through VMFLGPU010 (10 cases)

**VMFRT:**
VMFRT001 through VMFRT007 (7 cases)

**Complete set: 95 unique case identifiers**

### 2.3 Column Headers (Exact Quote)

```
| Case | Pg | Title | Dim | Regime / physics (Physics-Models line) | Ref | Quantity & N targets | Lab solver (OpenFOAM v2606) | Arch | Cost | Ladder |
```

**Column count:** 11 columns

### 2.4 RUN STATUS Field

**Result:** **NO RUN STATUS FIELD PRESENT** in CASE_MAP.md.

The table has no column for run status, verdict, completion, or execution state. The table is a **mapping document only** (per its opening prose: "Zero compute. This is a reading of the manual index..."). No example row provided because the field does not exist.

---

## 3. DIFF: Manual vs. CASE_MAP

### 3.1 Case IDs in MANUAL but MISSING from CASE_MAP

**Count:** 10 missing

These are the VMFL letter-suffix variants present in the manual sidecar but absent from CASE_MAP:

1. VMFL002B
2. VMFL003B
3. VMFL005B
4. VMFL007B
5. VMFL008B
6. VMFL012B
7. VMFL021B
8. VMFL023B
9. VMFL032B
10. VMFL040A

### 3.2 Case IDs in CASE_MAP but NOT Found in Manual Sidecar

**Count:** 0 (none)

All 95 case identifiers listed in CASE_MAP are present in the manual sidecar. Every VMFL base case (001–078), every VMFLGPU (001–010), and every VMFRT (001–007) that appears in CASE_MAP also appears in the manual grep extract.

---

## 4. Cases Actually Run by the Lab

**Evidence sources (all from HEAD or live disk):**

### 4.1 Case Directories in Git-Tracked `cases/ansys_verification/`

**Command:** `git ls-tree -r --name-only HEAD cases/ansys_verification/`

**Result (case IDs extracted):** 3 unique case directories

- VMFL001
- VMFL005
- VMFL051

**Artifact path:** `cases/ansys_verification/<CASE_ID>/`

### 4.2 Run Directories on Disk at `verification/runs/ansys_verification/`

**Command:** `ls -1 /home/ubuntu/Certonomous/verification/runs/ansys_verification/`

**Result (case IDs extracted):** 3 unique run directories

- VMFL001
- VMFL005
- VMFL051

**Artifact path:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/<CASE_ID>/`

### 4.3 Validation Register Rows

**Source:** `git show HEAD:verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`

**File path:** `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`

**Table row structure:** 13 columns; first column `#`, second column `Case`.

| # | Case | Verdict |
|---|------|---------|
| **1** | VMFL001 | NOT A RESULT |
| **2** | VMFL001-R2 | PASS |
| **3** | VMFL005 | PASS |

**Total register rows:** 3

**Distinct case IDs in register:** 2 (VMFL001, VMFL005)
- VMFL001 has 2 rows (row 1 `NOT A RESULT`, row 2 rerun `PASS`)
- VMFL005 has 1 row (`PASS`)

**Credential rows (PASS verdicts):** 2
- VMFL001-R2 (row 2)
- VMFL005 (row 3)

---

## Summary Table: Lab Run State

| Artifact Type | Count | Case IDs |
|---|---|---|
| **Case directories** (git-tracked) | 3 | VMFL001, VMFL005, VMFL051 |
| **Run directories** (disk) | 3 | VMFL001, VMFL005, VMFL051 |
| **Register rows** (total) | 3 | VMFL001 (2×), VMFL005 (1×) |
| **Distinct cases with runs** | 2 | VMFL001, VMFL005 |
| **Cases with PASS verdicts** | 2 | VMFL001-R2, VMFL005 |

**Note:** VMFL051 appears in case and run directories but has NO register row (not yet graded or results not committed to register).

---

## Artifact Paths — All Measurements

| Measurement | Artifact Path | Count/Value |
|---|---|---|
| Manual case IDs (unique) | `/home/ubuntu/Certonomous/docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt` | 105 |
| VMFL base (001–078) from manual | (same file, grep pattern) | 78 |
| VMFL letter variants from manual | (same file, grep pattern) | 10 |
| VMFLGPU from manual | (same file, grep pattern) | 10 |
| VMFRT from manual | (same file, grep pattern) | 7 |
| CASE_MAP rows | `git show HEAD:docs/ansys_verification/CASE_MAP.md` | 95 rows |
| Case directories | `git ls-tree -r HEAD cases/ansys_verification/` | 3 directories |
| Run directories | `/home/ubuntu/Certonomous/verification/runs/ansys_verification/` (disk) | 3 directories |
| Register rows | `git show HEAD:verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | 3 rows |
| Register PASS count | (same register file) | 2 rows |

---

## Findings: No Interpretation, Numbers Only

- Manual sidecar identifies **105 unique case identifiers**.
- CASE_MAP lists **95 unique identifiers** — all present in manual, but **10 letter-suffix variants are omitted**.
- Lab has run directories and register entries for **2 distinct cases** (VMFL001 with 2 runs, VMFL005 with 1 run).
- Lab case directory also present for VMFL051 with no register entry yet.
- CASE_MAP carries **no RUN STATUS field**.

