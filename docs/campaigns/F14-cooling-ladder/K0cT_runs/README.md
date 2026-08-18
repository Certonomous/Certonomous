# K0c turbulent rung — run tree. F14 cooling ladder

Nine cases against `../K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` Section 2, the
Betts and Bokhari ERCOFTAC Case 079 tall cavity. The result is
`../K0cT_RESULTS.md`: **GATE FAIL, 8 of 18 graded rows**, 95.0 core-minutes
against a 119.6 estimate and a 150 ceiling.

| file | what it is |
| --- | --- |
| `COST_PROPOSAL.txt` | The compute estimate, **written and timestamped before any graded case ran**, with the two measured pilot rates it is built on, the stated 1.6x contingency, the 140 core-minute hard stop, and the two named ways it could have been blown |
| `CONTROL_PREDICTIONS.txt` | Every control's prediction, its KIND, the thing that would make it vacuous, the attribution rule, the falsifiable directional prediction on the missing buoyancy term, and the convergence criterion — all registered before any result was read, and reproduced verbatim into `gate_k0ct.json` |
| `build_cases.py` | Builds all nine cases. **Parses the geometry, the two differentials and the two Rayleigh numbers out of the specification** and reads the end-wall temperature profiles out of the primary data files; exits 2 if either will not parse. Prints the derived plate levels, the Ra-matched viscosity against a Sutherland value, `beta.dT` against the lab's 0.1 line, and the cell Peclet number that rules out the laminar rung's central scheme |
| `run_cases.sh` | Mesh and solve one case. Carries the laminar rung's two recorded traps unchanged: the OpenFOAM environment is sourced per command, and nothing globs for time directories |
| `continue_cases.sh` | Continue from `latestTime` when the graded-quantity criterion is not met. Stage number derived from what is on disk, after the first version overwrote a log |
| `continue_past_residual.sh` | Removes the `residualControl` stop and runs on. Three cases stopped on their own residuals; this is what checked that the stop had not hidden anything |
| `analyse_k0ct.py` | The comparator. Parses reference values and pass bands out of the specification at run time, **re-derives the specification's own DERIVED table from the primary data files independently and exits 2 if the two have drifted**, and **exits 2 if the specification stops recording the Nusselt reference as NOT OBTAINED**. Grades on the fine mesh, carries the coarse in every row, runs the controls, applies the registered attribution rule, and audits every case on a COPY (L-118) |
| `gate_k0ct.json` | Everything above as data, including both registered files verbatim |
| `GATE_TABLE.md` | The gate table, generated. Nothing in `../K0cT_RESULTS.md` was retyped by hand |
| `write_monitor_tsv.py` -> `<case>/MONITOR.tsv` | The in-pass series the convergence verdict is **actually taken on**, frozen into a committable file. The repository's blanket `**/postProcessing/` ignore rule means the laminar rung's committed archive shows no series at all; a peak-to-peak spread quoted against a series nobody can open is a number with no evidence behind it |
| `write_log_digest.py` -> `<case>/LOG_DIGEST.txt` | The solver logs, distilled. **The full logs are gitignored on this rung and that is a real loss, stated rather than hidden**: they total **511 MB**, because one case ran 140 000 outer iterations to prove it never converges. The digest keeps the entire header verbatim (every control's in-log witness of its plant), the solve counts the controls are graded on, a decimated body, the last 120 lines, and the **SHA-256** of the log it was taken from. What is lost is the per-iteration residual trace between samples; what is not lost is anything the verdicts rest on |
| `BUILD_LOG.txt`, `ANALYSE_LOG.txt` | The build and analysis runs as they happened |

## The nine cases

| case | mesh | model | rung | role |
| --- | --- | --- | --- | --- |
| `T_lo_c` / `T_lo_f` | 40x120 / 64x192 | kOmegaSST | Ra 0.86e6 | **graded pair**, verdict on the fine |
| `T_hi_c` / `T_hi_f` | 40x120 / 64x192 | kOmegaSST | Ra 1.43e6 | **graded pair**, verdict on the fine |
| `M_hi_f_LS` | 64x192 | LaunderSharmaKE | Ra 1.43e6 | model SENSITIVITY twin |
| `B_hi_c_adiabatic` | 40x120 | kOmegaSST | Ra 1.43e6 | boundary-condition SENSITIVITY twin |
| `C1_hi_c_laminar` | 40x120 | laminar | Ra 1.43e6 | control C1, RECOGNITION |
| `C2_hi_c_Ra130` | 40x120 | kOmegaSST | Ra 1.86e6 | control C2, RECOGNITION at the gate's own scale |
| `S_hi_c_seed100` | 40x120 | kOmegaSST | Ra 1.43e6 | control C4, RECOGNITION of a confound |

Time directories, meshes and full solver logs are gitignored and reproducible:
`build_cases.py` regenerates every dictionary **byte-identically** (verified by
running it into a fresh temporary directory and `cmp`-ing all nine cases), and
`run_cases.sh` plus the two continuation scripts regenerate the solves. What
travels with each case is the dictionaries, `0.orig/`, `CASE.txt`, `COST.txt`,
`MONITOR.tsv` and `LOG_DIGEST.txt`.

## Two things a reader should not miss

**The coarse hi-Ra mesh does not reach steady state.** It was run to 140 000 outer
iterations and its peak-to-peak spread did not fall. The fine mesh at the same
Rayleigh number does reach a fixed point. Three cases are REFUSED by the
convergence criterion and are reported as refused; the criterion was not loosened.

**The Nusselt number is measured and ungraded.** Its reference was never obtained.
`analyse_k0ct.py` re-reads that statement out of the specification on every run
and refuses to grade at all if it has been removed.

## The four refusals, exercised from a fresh temporary directory

`analyse_k0ct.py` was copied into a clean tree with a copy of the specification
and driven against four mutations of it. Each refuses and **exits 2**:

| mutation of the specification | refusal |
| --- | --- |
| Section 2.3's stratification row renamed | `REFUSE: Section 2.3 row 'Core stratification S (DERIVED)' not found` |
| the sentence *"Nusselt number, turbulent rung: reference NOT OBTAINED"* removed | `REFUSE: the specification no longer records the turbulent-rung Nusselt reference as NOT OBTAINED` |
| Section 2.3's S value changed without Section 2.4's | `REFUSE: Section 2.4's S target disagrees with Section 2.3's S value` |
| Section 2.3's peak velocity changed to 0.210 | `REFUSE: the specification's DERIVED table has drifted from the primary data files it names: Vup hi: spec 0.21 vs primary 0.19` |

**That exercise found a defect in this analyser and it would otherwise have
shipped.** Every refusal was `raise SystemExit("REFUSE: ...")`, and `SystemExit`
with a string argument exits **1**, not 2 — so a caller could not have told a
REFUSAL from "a graded row failed". It is the same defect L-118 records in
`scripts/heat_balance.py`, six sites of it. Repaired with an explicit `Refusal`
class; the exit codes above are measured, not promised.
