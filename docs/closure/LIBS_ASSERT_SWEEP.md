# The L-221 libs sweep: every call site that writes a `libs` entry, and what asserts it

**Dated 2026-08-22. H-7 INSTITUTIONALIZATION lane, on Sanaa's directive:** *"the libs
lesson as law — a defect class that bit three call sites gets an assert at every call
site, never a paragraph in a report. Sweep for remaining unasserted call sites of the
same libs defect."*

## 1. The defect class, stated so a call site can be tested against it

A script writes or edits a `libs (...)` entry in an OpenFOAM `system/controlDict` (or
names a model in `constant/turbulenceProperties` that only a loaded library provides) by
a route that can **silently do nothing**: a `str.replace` of a line that is not there, a
regex that does not match, an append whose result nobody reads back. The library is then
not loaded, the solver falls back to the stock model, and the run returns **the
unperturbed field, which looks like a plausible physical answer** (L-221: five eigenspace
re-solves returned `it=0` and the baseline `U_rms`).

**The law.** Every such call site **INSERTS (insert-or-replace)** and then **ASSERTS** the
library name is present in the written text. Python: `assert "<lib>" in s, "libs insert
failed: <path>"`. Shell: `grep -q '<lib>' <file> || { echo "libs insert failed: <file>"
>&2; exit 1; }`.

## 2. Scope swept

`.py`, `.sh`, `.bash` and Makefile-like scripts under `cases/` (closure cases **and**
`cases/dafoam`, `cases/hlpw6`, `cases/committee-grids`) and under `verification/`.
**Not edited, by instruction:** `verification/runs/T-family/` (another supervisor's),
`cases/RANS_LES_closure_models/R4_sparta_build/` (the R4 lane is writing there), and the
two files a reconcile lane owns. All four are listed below with their classification.

Population: **92** grep hits for `libs` in scripts in scope; **75** of them are lines that
actually write a `libs` entry (the remaining 17 are comments and argument plumbing).
Those 75 split into **8 library-load call sites** (§3) and **67 function-object template
lines** (§4).

## 3. Library-load call sites — the defect class. 8 found

| # | path:line | library | before | action | check run + result |
|---|---|---|---|---|---|
| 1 | `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/setup_case.py:104-115` | `libspartaTurbulenceModels.so` | **already-asserted** (`:115`) | **none — owned by the reconcile lane**, read-only here | read only; `lint_foam_libs.py` reports it INFO |
| 2 | `cases/RANS_LES_closure_models/Xiao2016_EnKF/tau_forward.py:71-80` | `libspartaTurbulenceModels.so` | **already-asserted** (`:80`) | none | `python3 -m py_compile` OK |
| 3 | `cases/RANS_LES_closure_models/NASA_hump_gate/run_gate.py:34-42` | `libspartaTurbulenceModels.so` | **already-asserted** (`:42`) | none | `python3 -m py_compile` OK |
| 4 | `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/frozen_R.py:69` → now `:69-79` | `libspartaTurbulenceModels.so` | **UNASSERTED, and the defect was LIVE** — a bare `str.replace` of `libs ( "libfrozenIncompressibleTurbulenceModels.so" );` | insert-or-replace + `assert` at `:79`, the `setup_case.build` idiom | `py_compile` OK. Sandbox replay on the two real controlDicts: on `DUCT/AR_1_Ret_360` the new text is **byte-identical to the old behaviour**; on the `Parm_PH_29` hill the old code produced **no sparta entry at all** and the new code inserts one — the no-op is measured, not argued |
| 5 | `cases/RANS_LES_closure_models/Wu2018_PIML_RF/aposteriori/build_cases.sh:54,69` | `libspartaTurbulenceModels.so` | **unasserted** — strips every `^libs.*$` then conditionally appends | `assert` inside the embedded python at `:71`; shell guard at `:74-77`, fired only when `$LIBS` is non-empty so the deliberate `stock` arm is untouched | `bash -n` OK; all three embedded python blocks compile; block executed on a real controlDict for **corrected** (lib present) and **stock** (lib correctly absent); **negative control**: append sabotaged → `AssertionError: libs insert failed` |
| 6 | `cases/RANS_LES_closure_models/Wu2018_PIML_RF/aposteriori_frozenk/build_cases.sh:48,58` | `libspartaTurbulenceModels.so` **and** `libwu2018FrozenK.so` | **unasserted** — same strip-then-append | `assert` on **both** names at `:61-62`; shell loop guard at `:65-68` | `bash -n` OK; block executed → both libs present; **negative control**: append sabotaged → assert fires |
| 7 | `verification/runs/F14-cooling-ladder/K0cQ_runs/build_cases.sh:59` | `libkOmegaSSTQCRTurbulenceModels.so` | **unasserted** — blind `printf … >> controlDict` | guard added here and then **SUPERSEDED IN THE WORKING TREE, mid-sweep, by a concurrent lane** routing the site through `scripts/foam_libs.py ensure` (insert-or-replace, re-read from disk, assert). **Their version is stronger and is left standing; this lane did not commit the file** | my guard was tested positive **and** negative before supersession; the site is asserted either way. Their helper also catches what a `grep -q` cannot: a second top-level `libs` entry is a duplicate dictionary key, not a longer list |
| 8 | `verification/runs/W2_sparta_runs/setup_sparta_case.sh:22-47` | `libspartaTurbulenceModels.so` (**inherited, never written**) | **unasserted** — rewrites `turbulenceProperties` wholesale naming `kOmegaSSTSparta`, whose library it inherits from the copied source `system/` | **assert only**, at `:52`. No insert added: inserting a library the source did not name would be a behaviour change, and the failure here is loud (unknown RAS model) rather than silent. Recorded as the one place the law is applied in half | `bash -n` OK; guard **passes** on a real built case (`cbfs_mdisc`) and **fires** on a controlDict without the entry. All built W2 cases were checked and every one carries the entry, so the guard changes no existing outcome |

**Counts for §3: 8 sites found; 3 already asserted; 4 newly asserted by this lane
(#4, #5, #6, #8); 1 asserted by the concurrent helper lane after this lane's guard
(#7).**

## 4. Not the defect class — 67 lines, 25 scripts

Every remaining `libs` write in scope is a **function-object loader**
(`libs (fieldFunctionObjects);`, `libs (sampling);`, `libs (forces);`) sitting as a
**literal inside a whole-file template** that the script writes with a single
`open(path,"w").write(...)` or heredoc.

**Classification: n-a, and an assert after the write is NOT warranted.** There is no
merge and no search: the file did not exist a moment before, so no silent no-op is
reachable — a failed write raises. The written files were verified on disk anyway rather
than reasoned about: e.g. every `K0cT_runs/*/system/controlDict` carries **10** such lines
against the template's 10, and `K0cS_runs/*` carry **8**. Scripts: `K0cT/K2e/K0c/K0cS/
K0cG/K2b(×4)/K0cX/KV1` builders, `F5 cylinder_ladder.py`, `F3 wedge/cone/diamond`,
`F4 run_cylinder_case.py`, `F6b write_case_dicts.py`, `F11 cavity_ladder.py`,
`FPE_DIAG run_fpe_diag.py`, `DPW8_V2 make_case.py`/`run_case.py`,
`cases/hlpw6/make_hlpw6_case.py`, `cases/committee-grids/make_dpw5_case.py`,
`cases/dafoam/f6d_random_matrix_uq/build_ensemble.py` and `build_signdemo.py`.

## 5. Observed and deliberately not edited

| Where | What is there | Classification |
|---|---|---|
| `verification/runs/T-family/` (T1, T3, T9a, T10a) | **Zero `libs` call sites of any kind.** `build_t1b.py`, `build_t1c.py`, `build_t9a.py`, `build_d_ts*.py`, `build_diag*.py` write `system/controlDict` and `constant/turbulenceProperties` **wholesale from templates that contain no `libs` line at all** — their solvers use built-in models | **n-a**, and nothing to add. Another supervisor's tree; listed, not touched |
| `cases/RANS_LES_closure_models/R4_sparta_build/` | 16 `libs` lines, all inside `r4_lib.set_libs()` — **the law already implemented in a shared helper**: insert-or-replace, then `assert "libspartaTurbulenceModels" in s`, with the Parm_PH_29 hills named in its docstring | **already-asserted**. The R4 lane is writing there concurrently; not touched |
| `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/setup_case.py` | The canonical asserted call site (§3 row 1) | **already-asserted**; **owned by the reconcile lane** |
| `cases/RANS_LES_closure_models/_common/features/make_feature_library.py` | **No `libs`, no `controlDict`, no `turbulenceProperties` reference anywhere in the file** | **n-a — not a call site**; **owned by the reconcile lane** |

## 6. Two lanes institutionalized the same law tonight, and the overlap is stated

While this sweep ran, another lane created `scripts/foam_libs.py` (an `ensure_libs`
helper) and `scripts/lint_foam_libs.py` (a linter that FAILs any `libs` write not routed
through it), and rewrote the K0cQ call site through the helper. **That is the same law
with a stronger mechanism, and it is welcome.** Run as an independent check of this sweep:

```
python3 scripts/lint_foam_libs.py verification/runs cases/RANS_LES_closure_models \
        cases/dafoam cases/hlpw6 cases/committee-grids --include-closure
→ 0 FAIL, 3 INFO
```

Three observations about that instrument, filed for its owner and **not repaired here**:

1. **`--include-closure` does not widen the walk.** It only lifts a skip for roots the
   caller passes explicitly (`:196` takes `roots or [DEFAULT_ROOT]`, `:203` skips a passed
   closure root unless the flag is set). Run bare with the flag it still walks
   `verification/runs` only and prints `closure tree: INCLUDED` — the label says audited
   and the walk is not. The closure root must be named on the command line, as above.
2. **It does not see the canonical asserted idiom as a write.** `setup_case.py:109` is
   reported as *"libs mentioned, no write route matched"*, and `frozen_R.py`'s
   insert-or-replace is not reported at all, so a `re.sub`-based site — the exact shape
   L-221 prescribes — is invisible to the WRITES rule rather than passed by it.
3. Its default exclusion of `cases/RANS_LES_closure_models` is deliberate and is why the
   four sites fixed here keep the closure tree's own in-file idiom rather than importing
   the new helper. A second reason to keep them self-contained: at the time of this
   sweep `scripts/foam_libs.py` is **untracked**, so a closure builder that imported it
   would break for anyone who checked the tree out.

## 7. What this sweep cannot see

* **It reads scripts, not runs.** A case whose `controlDict` was hand-edited, or built by
  a script since deleted, is outside it.
* **It does not prove any library exists on this machine**, only that its name reaches the
  written file. `libfrozenIncompressibleTurbulenceModels.so` is named by four benchmark
  cases and exists nowhere here — that absence is what made the original no-op silent.
* **No solver was run.** Every check above is a syntax check, a sandbox replay on a copied
  dictionary, or a `grep` of a file already on disk. Zero compute.
