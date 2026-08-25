# D11-F′ — THE CLI RE-BUY of the D11 MRF probe — PRE-REGISTRATION

**Form:** the 10-line mini-prereg. **Frozen at the commit that adds this file; no
container of D11-F′ has run.**
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

### 0. The hard stop I wrote, read against what actually happened

D11-O′ §0 registered this, and it binds me before it binds anyone else:

> **THE HARD STOP, registered before the run.** If the `omega = 30.0` primal also fails
> to converge, the verdict is **`NOT A RESULT`** and **D11 goes to the supervisor
> UNPRICED with a named blocker … THERE IS NO FOURTH ATTEMPT.** Reducing omega again
> until something converges would be tuning an instrument against an answer, and this
> clause exists so that the temptation is refused in writing before it can be felt.

**The clause is a conditional, and its antecedent is FALSE. The `omega = 30.0` primal
converged.** Measured, from the D11-O′ ledger and JSON on disk:

| stage | omega | task | rc | `TPIn` |
|---|---|---|---|---|
| `omegaP` | **30.0** | `compute_totals` (primal **and adjoint**) | **0** | `1.1859858226134654` |
| `omega0` | 0.0 | `compute_totals` | **0** | `1.183671978501559` |
| `clean` | 0.0 | `run_model` | **0** | — |
| `fdp` | **30.0** | `run_model`, `uOffset +1.0e-3` | **0** | `1.1862164207660815` |
| `fdm` | 30.0 | `run_model`, `uOffset −1.0e-3` | **2** | — |

Four of five stages reached `rc = 0`, **including both MRF-active ones that had to
solve**. D11-O′ still graded **`NOT A RESULT`**, correctly, because its frozen grader
refused on the missing `fdm` artifact, and that verdict is not revised.

**The clause's stated reason is `Reducing omega again`. THIS DOCUMENT DOES NOT REDUCE
OMEGA. `omega` stays at `30.0 rad/s`, byte-identical.** Both the antecedent and the
reason fail to reach this re-buy, and the reading is checkable on the page rather than
asserted: the `OMEGA_PLANT` constant and the whole case directory are unchanged, so
there is no move available here that could tune an instrument toward an answer.

### 0.1 The single defect, triaged
`fdm` exited **2** — not `1`. `rc = 1` is DAFoam's `AnalysisError`; `rc = 2` is
`argparse` refusing the command line. From the log, verbatim:

> `usage: d11o_run_script.py`
> `d11o_run_script.py: error: argument -uOffset: expected one argument`

`argparse` treats `-1.0e-3` as an **option flag**, not a value: its negative-number
matcher accepts `-1` and `-0.001` but **not exponent notation**. The negative FD half-
step was therefore never passed, in **all three** D11 attempts — it is the reason `fdm`
read `rc = 2` every time, including in attempt one where it sat unexamined beside four
`rc = 1`s and was not separately triaged. **That miss is recorded, not smoothed over.**

**THE ONE CHANGE:** the launcher passes `-uOffset=$UOFF` instead of `-uOffset $UOFF`.
The `=` form is unambiguous to `argparse`. **Nothing else in this probe differs from
D11-O′ by a byte** — not the run script, not the case, not the mesh, not `omega`, not a
single gate or threshold.

### 1–5. Capability, image, gates, mapping, plant
**Carried over from D11-O′ unchanged, to the digit.** Capability: MRF/rotating-frame
adjoint reachability, cell-zone formulation. Image
`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`. Gates G11-1,
G11-2a, G11-2b, G11-3, G11-4, G11-5 with plant floor `1.0e-6`, clean tolerance
`1.0e-12`, derivative floor `1.0e-12`, FD band `5.0e-2`, FD step `h = 1.0e-3 m/s`
central. Plant: `omega = 30.0 rad/s` against an inert `0.0`, read back off disk,
refusing if the reader cannot see it. Mapping: absent capability `BLOCKED`; NaN
`GATE FAIL`; all-zero derivative `GATE FAIL`; bit-identical MRF-on/off `GATE FAIL`;
G11-5 outside band `GATE FAIL`; blind plant, stalled primal or a fatal in this lane's
own files `NOT A RESULT`; all six `GATE REACHED`.
**Proven able to refuse:** `python3 d11f_grade.py --selftest` — 7/7 green before this
commit.

**Registered hard stop, carried forward and narrowed to this document's own risk:** if
`fdm` fails again for any reason, the verdict is **`NOT A RESULT`**, D11 goes up
**UNPRICED with the blocker named**, and **this lane runs no further D11 attempt**. The
`omega` value is not available to be changed by this lane at all.

### 6. Cost
- **Predicted: 0.85 core-min.** Measured basis: D11-O′ ran the identical five stages for
  **0.7167 core-min** with `fdm` dying instantly in `argparse`; `fdm` completing costs
  about what `fdp` cost, **0.1167**.
- **Registered cap: 5.0 core-min**, same guard, same 240 s per-stage timeout.
  **An overrun STOPS the probe.**
- `$0.00073` derived — **DERIVED, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED`.
- **The D11 chain's prior spend — 0.7166 + 0.8334 + 0.7167 = 2.2667 core-min — is named
  separately in `docs/COST_CALIBRATION.md` and is NOT absorbed into this row's ratio.**

### 7. np and decomposition
`np = 1`, `numberOfSubdomains 1`. **With np = 1 the parallel-determinism question does
not arise.**

### 8. What this probe does NOT establish
D11-O′ §8 verbatim, and the sentence that matters most is carried forward unchanged:
**it establishes nothing about MRF at engineering rotational rates.** Whatever it
returns is a statement about a 30 rad/s zone on a 720-cell channel. **The measured fact
that a 300 rad/s zone STALLS this steady substrate stands and must be carried into
D11's own pre-registration**, which will need a rotating-frame-appropriate case or an
unsteady formulation.

### 9. Frozen instruments (md5 at this commit)
| file | md5 | note |
|---|---|---|
| `d11f_run_script.py` | `2975373099a6125a1c028a935b145e73` | **byte-identical across all four attempts** |
| `d11f_case/constant/MRFProperties.template` | `e7d601ae02d9a3bc1c9f221b6792dea5` | **byte-identical to D11-D′ and D11-O′** |
| `d11f_stage_and_run.sh` | `9d137db3572885fbef1fae3da83043bd` | `-uOffset=` and paths — the whole change |
| `d11f_grade.py` | `0618094c0f63a94e23d9dfc1ecc2fa6b` | paths and labels only; `OMEGA_PLANT = "30.0"` unchanged |
