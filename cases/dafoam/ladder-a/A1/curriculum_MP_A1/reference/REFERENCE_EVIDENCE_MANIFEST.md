# SO-3 — REFERENCE EVIDENCE MANIFEST

**Purpose.** The two OpenFOAM logs in this directory are the **real bytes** every reader-side leg of the SO-3 comparator is driven against. They are excluded from version control by **`.gitignore:270`, pattern `cases/dafoam/**/*.log`** — a **lab-wide** rule that this family does not get to widen for its own convenience. This manifest is the committed, non-`.log` artefact that stands in for them: it carries each file's identity and **every extracted value the pre-registration relies on**, so that a claim resting on those bytes has something in git protecting it.

**What this manifest is NOT.** It is not the logs and it does not reproduce them. If both logs were lost, `--selftest` would still be un-drivable; what would survive is the ability to **detect** the loss and to state exactly which published numbers had lost their artefact. That is a smaller thing than preservation and it is the honest description of it.

**Measured 2026-09-01 by `so3_grade.py`'s own units** — its compiled regexes and its own reader functions, imported and called, not re-implemented here and not read off a prior record.

---

## 1. FILE IDENTITY

| file | bytes | lines | md5 | sha256 |
|---|---|---|---|---|
| `REAL_SO1a_X-S_arm.log` | 24500 | 690 | `c6d9c8e6976095682292fa32224c602a` | `0d6da8f7cc8ea7833a87fc37b5dddf3c21303ab75bf3682a4fb6c3e1cd116421` |
| `REAL_SO1a_MESH_checkMesh.log` | 3568 | 99 | `22aa9cfa6725eb904123aefaebf63cfd` | `192b267e49f6c0075b32b5e189f1da0a68beb1064333f08a4a3bb26199b50023` |

**Provenance.** Both are real OpenFOAM/DAFoam output from `CURRICULUM-SO1a`, on this same A1 NACA0012 case, carried into `curriculum_SO3/reference/` by `so3_derive_from_so3ar2.sh:105-106`.

---

## 2. THE EXTRACTED VALUES `PREREGISTRATION.md` RELIES ON

### 2.1 `REAL_SO1a_X-S_arm.log` — the banner discriminator (`PREREGISTRATION.md` §3)

**This log is from a run that CONVERGED.** That is the whole point of it: it is the counter-example that stops three naive readers from being written.

| reading | unit used | **value** | what it means |
|---|---|---|---|
| `SIMPLE: no convergence criteria found` | `so3_grade.SIMPLE_BANNER_RE` | **4** | OpenFOAM's SIMPLE banner, on a **converged** run. A naive convergence limb reads **four declarations of non-convergence on a converged run**, because DAFoam applies its own `primalMinResTol` and stops the solve regardless of what the banner announced. |
| `Minimal residual <r> satisfied the prescribed tolerance <tol>` | `so3_grade.CONVERGED_RE` | **1** | **the real statement.** Captured groups: residual **`9.822715611394694e-09`**, tolerance **`1e-08`**. |
| `Time step continuity errors :` | `BENIGN_LINE_PATTERNS[2]` | **5** | a per-iteration **residual report**. A naive `grep -i error` limb reports **five crashes per success**; the word `errors` here names a residual, not a failure. |
| `trapFpe:` | `BENIGN_LINE_PATTERNS[0]` | **0** | **NOT EXERCISED ON THESE BYTES.** See §3. |
| any of `so3_grade.FATAL_TOKENS` | `FATAL_TOKENS` | **none present** | the log carries no fatal token, consistent with a converged run. |

### 2.2 `REAL_SO1a_MESH_checkMesh.log` — the mesh reader (`PREREGISTRATION.md` §3, `G-M2`)

| reading | unit used | **value** |
|---|---|---|
| cell count | `so3_grade.read_mesh_cells()` | **4032** — equal to `CELLS_EXPECTED = 4032`, so `G-M2` reads `PASS` on these bytes |

---

## 3. AN HONEST GAP FOUND WHILE MEASURING: THE `trapFpe:` EXCLUSION IS NOT EXERCISED HERE

`so3_grade.py`'s docstring section (III) names **three** benign per-line exclusions — `trapFpe:`, the SIMPLE banner, and the continuity-error line — and its own header presents them together as measured against these reference bytes.

**Measured: `trapFpe:` appears 0 times in `REAL_SO1a_X-S_arm.log`.** Two of the three exclusions are demonstrated on these real bytes; **the third is not.** The `trapFpe:` exclusion is registered and implemented, and the comparator's C5 plant control drives it on a constructed line, but **it has no demonstration on this reference log** and this manifest says so rather than letting a reader infer that all three counts came from the same file.

**Stated at its true size.** The exclusion is not wrong and nothing depends on it having fired here — `trapFpe:` genuinely is an OpenFOAM **enablement notice** rather than a report that the handler fired. What is corrected is the impression that all three exclusions were measured on these bytes. **Two were.**

---

## 4. HOW TO RE-DERIVE EVERY NUMBER ABOVE

Every value in §2 is produced by importing the frozen comparator and calling its own units against the two files in this directory — `SIMPLE_BANNER_RE.findall`, `CONVERGED_RE.findall`/`.search`, the `BENIGN_LINE_PATTERNS` line regexes, `FATAL_TOKENS` membership, and `read_mesh_cells()`. **Nothing here re-implements a reader**, because a manifest that re-implements the reader it is documenting can agree with itself while disagreeing with the instrument.

**If a file's md5 in §1 no longer matches the bytes on disk, every value in §2 is void** and the pre-registration's §3 readings lose their artefact. That is the failure this manifest exists to make detectable.

---

## 5. STATUS

**The grading path does not read this directory.** `REFDIR`, `REAL_CHECKMESH` and `REAL_ARMLOG` at `so3_grade.py:2648-2650` are **path joins that open nothing**; the only sites that open these files are `_fix()` at `:2815` and `:2820` and `selftest()` at `:3304`, all reachable only under `--selftest` (`:3527`). **SO-3 can cold-start, run and grade from a clean checkout of its freeze commit with this directory absent.** What a clean checkout cannot do is re-drive `--selftest`.

**`.gitignore:270` is not changed by this manifest**, and changing it is not this family's call.

*Cited by `PREREGISTRATION.md` Amendment 1 (residual R8) and Amendment 2.*
