# T5 `y+` RECOVERABILITY — DIAGNOSTIC, **NOT A GATE INPUT**

**Date: 2026-09-03. Team: heat-transfer. Rung: `T5`. Solver compute: 0 core-min.**

> ## ⚠ THIS DIRECTORY IS EVIDENCE, NOT A MEASUREMENT THE RUNG MAY USE.
>
> **Nothing here is read by `analyse_t5.py`, and nothing here may be moved, copied,
> renamed or converted into a path that it reads.** The frozen comparator reads
> **`<case>/yPlus.json`** (`verification/runs/T-family/T5_runs/analyse_t5.py:156`).
> **That file does not exist in any T5 case directory and was deliberately NOT
> created by the work recorded here.** `T5_PREREGISTRATION.md` §16.3.1 registers
> its absence as **`NOT A RESULT`**, before compute, and `gate_yplus` returns that
> at `analyse_t5.py:166-168`.
>
> **No file in this directory is named `yPlus.json`, and no file in this directory
> sits inside a case directory.** Every filename carries the `DIAG_` prefix so that
> no future glob, reader or lane can mistake one for the registered gate input.
>
> **T5's landed `NOT A RESULT` is untouched by this directory.** Whether the
> measurement recorded here may ever be used is a `§2d.1` question that
> **verification has not been asked and has not ruled on** as of this file's date.
> `T5b_PREREGISTRATION.md` §2 (`:86`) records a heat-transfer ruling in the other
> direction — *"`postProcess` may NOT be re-run on T5's completed cases to recover
> `y+`"* — and that ruling stands unless and until verification says otherwise.

---

## 1. WHAT THIS DIRECTORY ESTABLISHES

**One thing, and it is a capability claim, not a verdict:** the `y+` measurement
that T5's inline `yPlus` function object never produced is **recoverable at zero
solver compute** from the `endTime` fields already frozen on disk — and the
obvious way of recovering it **silently fabricates zeros**.

The two runs below are **each other's live control** (`CLAUDE.md` rule 3). Same
case, same fields, same time directory; one reader blind to the quantity, one not.
**That pairing is the whole reason the non-zero numbers are evidence.** A lane that
had run only Run A would have obtained a well-formed table of zeros with `rc = 0`
and no error, and grading on it would have been grading on fabricated data.

## 2. THE ENVIRONMENT

| item | value |
|---|---|
| OpenFOAM | **v2606**, build `_481094f-20260618`, `OPENFOAM=2606` |
| Arch | `LSB;label=32;scalar=64` |
| host | `ip-172-31-43-247` (the lab box) |
| date of both diagnostic runs | **2026-09-03**, 21:00:12Z and 21:00:24Z |
| ranks | 1 (serial) each |
| solver binary | `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/chtMultiRegionSimpleFoam` |
| solver compute | **0 core-min** — neither run advances a timestep; both read `5000/` and exit |

**Both runs were executed on a SCRATCH COPY of `T5_CUBE_m`, never on the case
itself.** No file in `verification/runs/T-family/T5_runs/T5_CUBE_c`, `T5_CUBE_m`,
`T5_CUBE_f` or `S_m` was created or modified. Measured before and after: **zero
files under `T5_runs/` newer than 2026-09-01**, other than this directory.

## 3. THE TWO RUNS, AND THE EXACT COMMANDS

The scratch copy sat at a path under the session scratchpad; the scratchpad is temp
only and is never a handoff channel (`CLAUDE.md` rule 13, L-186), so **the path is
deliberately not reproduced here.** To repeat the pair, copy a completed T5 case to
a scratch location `<SCRATCH>` and run, in this order:

### Run A — the BLIND reader. **Writes six well-formed rows of ZEROS and exits 0.**

```
postProcess -case <SCRATCH> -func yPlus -region air -time 5000
```

`postProcess` constructs no turbulence model, so `yPlus::execute()`
(`/usr/lib/openfoam/openfoam2606/src/functionObjects/field/yPlus/yPlus.C:173`)
finds none in the registry, emits

> `--> FOAM Warning : ... Unable to find turbulence model in the database: yPlus will not be calculated`

on stderr, and returns `false`. **`yPlus::write()` then runs anyway** and writes a
complete, well-formed table in which every `min`, `max` and `average` is exactly
`0.0000000000e+00`. **Exit code 0.** The warning is the only signal, and it is not
in the data file.

### Run B — the SIGHTED reader. **Writes six rows of genuine non-zero `y+`.**

```
chtMultiRegionSimpleFoam -case <SCRATCH> -postProcess -func yPlus -region air -time 5000
```

The solver's own `-postProcess` mode constructs the thermophysical and turbulence
models, so the registry lookup succeeds and `y+` is computed from the frozen
`endTime` fields.

**Recovered per-patch `y+` at `Time = 5000`, level `m`:**

| patch | min | **max** | average |
|---|---:|---:|---:|
| `cube_front` | 0.1492881454 | **2.960969226** | 1.275375915 |
| `floor` | 0.06760916785 | **2.389443862** | 0.7473188351 |
| `cube_top` | 0.158997996 | **1.903105528** | 0.9037585379 |
| `cube_side_n` | 0.08149651499 | **1.732353011** | 0.7656388027 |
| `cube_rear` | 0.2476717199 | **1.443516718** | 0.8190484404 |
| `roof` | 0.2352078469 | **1.212625584** | 0.5640505831 |

The recovered patch set is **exactly** the frozen `YPLUS_WALLS`
(`analyse_t5.py:53-54`): `cube_front`, `cube_top`, `cube_rear`, `cube_side_n`,
`floor`, `roof` — six patches, `cube_side_s` correctly absent on the registered
half domain.

**These numbers are recorded here as a CAPABILITY MEASUREMENT and are graded by
nothing.** They are stated so that any future ruling has the pre-repair figures in
front of it, per `§2d.1`(3)/(4). They have not been passed through `gate_yplus`,
and this file draws no conclusion about what verdict they would produce.

## 4. WHY THE INLINE FUNCTION OBJECT NEVER FIRED — the root cause, measured

T5's `system/controlDict` gives **both** function objects the identical control
(preserved verbatim as `DIAG_asrun_T5_CUBE_m_controlDict.txt`):

```
writeControl    writeTime;
writeInterval   1000;
```

**One identical setting means two different things**, because the two objects emit
their `.dat` rows from **different lifecycle phases**:

| object | rows emitted from | governed by | rows written in T5's `T5_CUBE_m` |
|---|---|---|---:|
| `wallHeatFlux` | `execute()` | `executeControl` — **unset, so every timestep** | **30,000** |
| `yPlus` | `write()` (`yPlus.C:219`, inside `write()` at `:191`) | `writeControl`/`writeInterval` | **0** |

Under `ocWriteTime` the fire condition (`timeControl.C:197-205`) is `writeTime`
**and** `executionIndex % 1000 == 0`. T5's run had **five** write times, so the
condition was never met and **`write()` never executed once**.

**Confirmed by mtime, not by reasoning.** In the real
`T5_CUBE_m`, `postProcessing/air/yPlus/0/yPlus.dat` is stamped **2026-08-26
20:57:25** — at function-object construction — while `log.solve` and
`postProcessing/air/wallHeatFlux/0/wallHeatFlux.dat` are stamped **2026-08-26
22:13:03**, at the end of the solve. **The `yPlus` file was never touched again
after it was created.** Its byte content, preserved here as
`DIAG_asrun_T5_CUBE_m_yplus_table_ZERO_ROWS.dat`, is two header lines and **zero
data rows**, 114 bytes. The same holds on `c` (20:54:09) and `f` (22:22:45).

**The transferable form of this is filed as a lesson in `docs/LESSONS.md`**, with
an executable check under `scripts/`.

## 5. THE FILES

| file | what it is |
|---|---|
| `DIAG_asrun_T5_CUBE_m_controlDict.txt` | byte copy of the real `T5_CUBE_m/system/controlDict` as it ran — the two function objects under the identical control |
| `DIAG_asrun_T5_CUBE_m_yplus_table_ZERO_ROWS.dat` | byte copy of the real `T5_CUBE_m/postProcessing/air/yPlus/0/yPlus.dat` **as the solve left it**: headers, zero data rows, 114 bytes |
| `DIAG_runA_postProcess_blind.log` | full stdout/stderr of **Run A**, carrying the `yPlus.C:173` warning and the six zero rows |
| `DIAG_runA_yplus_table_ZEROS.dat` | **Run A's** output table — six well-formed rows, every value exactly `0.0000000000e+00`. **THE FABRICATED ZEROS.** OpenFOAM wrote this as `yPlus_0.dat` because a `yPlus.dat` already existed |
| `DIAG_runB_solver_postProcess.log` | full stdout/stderr of **Run B**, carrying the thermophysical/turbulence model construction and the six non-zero rows |
| `DIAG_runB_yplus_table_NONZERO.dat` | **Run B's** output table — the six genuine `y+` rows tabulated in §3 |
| `DIAG_runB_yplus_field_5000_air.foam` | **Run B's** `yPlus` volScalarField at `5000/air/yPlus`, 116,813 bytes. Its maximum boundary value is `2.960969226`, matching `cube_front` in Run B's table, which is how it is attributed to Run B rather than to Run A |

**Provenance caveat, stated rather than glossed:** Run A also writes a `yPlus`
field, and Run B overwrote it. The preserved field is attributed to Run B **by its
values matching Run B's table**, not by file ordering. Run A's field is not
preserved because it no longer exists.

### sha256, at the moment of filing

```
e2ca397645f8371ae9d5e27f6ac6cd409aec4bf11d0b32f5e4d5876cffa05772  DIAG_asrun_T5_CUBE_m_controlDict.txt
0d913b6cb3f7fc059ba5df474848d7e15c961d93716b068cbb8ea28eaa06f82d  DIAG_asrun_T5_CUBE_m_yplus_table_ZERO_ROWS.dat
9b974f45cb57b2ebc92771ed778228201f8b0f5aba97babca371fe13d00ff282  DIAG_runA_postProcess_blind.log
e0a43f6c7c813456b75eec7cbbfe43af3e468af3f030ce63332c959eeb607501  DIAG_runA_yplus_table_ZEROS.dat
c6af4c3c706fea16ba4802841f914ddf13a8628ffaad60cfb0f4d8fb7cefb804  DIAG_runB_solver_postProcess.log
de25a3b0845716f8fcc59a85e13225065365be781d8be96cec6658a9e8448102  DIAG_runB_yplus_field_5000_air.foam
8e9b3f5af5c0789711898788e2c16644b26db3abdbfb5fec5d5f05d2a756e5e6  DIAG_runB_yplus_table_NONZERO.dat
```

`0d913b6c…` is **identical to the live file** at
`verification/runs/T-family/T5_runs/T5_CUBE_m/postProcessing/air/yPlus/0/yPlus.dat`,
verified by `sha256sum` against the case directory at filing time. That is the
whole evidentiary value of that copy: a preserved artifact that differs from what
it preserves is worthless.

## 6. WHAT THIS DIRECTORY DOES **NOT** DO

- It does **not** create, and does not authorise creating, `<case>/yPlus.json`.
- It does **not** re-grade, reopen, restate or relax T5's `NOT A RESULT`.
- It does **not** claim the recovered numbers may be used. That is a `§2d.1`
  question for verification.
- It does **not** claim the recovered numbers would produce a `PASS`. **Nobody has
  run them through the gate and this record makes no prediction about the outcome.**
- It does **not** speak for `T5b`, the successor rung, which repaired the defect by
  configuration and reads `postProcessing/air/yPlus/0/yPlus.dat` directly
  (`T5b_runs/analyse_t5b.py:337-345`) rather than a `yPlus.json`.
