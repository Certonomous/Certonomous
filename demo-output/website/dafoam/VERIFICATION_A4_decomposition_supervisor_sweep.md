# Supervisor verification sweep — A4's CONDITIONAL→PASS on the decomposition finding

**2026-08-04. Adversarial verification of the 2026-08-02 claim (`PROOF.md` §25.5,
`W5_GRADIENT_REGRADE.md` §2 update, `DAFOAM_CASE_STATUS.md` §A4,
`campaign/NOT_PASSING_REGISTER.md`): that A4's published 10.04% adjoint-vs-FD error
was an artifact of DAFoam's default `scotch` decomposition, and that A4 is a PASS.**
Doctrine applied: the claim was assumed wrong until it survived attack. It survived.
The defects found are in the documentation surface, not in the measurement, and they
are listed before the confirmations because they are the part a reader cannot see
from the published tables.

**Headline: CONFIRMED on all five axes, including an independent re-run of one table
cell that reproduces it to every printed digit. Two documentation defects and two
wording over-reads found; none touches a number in the claim.**

---

## Defects found (the reason this sweep ran)

**D-1. A4's own ladder record was never updated, and it now contradicts the verdict
in both directions.** `ladder-a/A4_ahmed_body.md:158` still reads "**The 10.04%
gradient figure below is graded CONDITIONAL**, not PASS" with no supersession note,
while `:207` still carries the *old, wrong-reason* "Verdict: PASS, under this host's
own calibration" that the CONDITIONAL regrade itself called out as unreconciled.
`A4_ahmed_body.json` likewise still says "PASS under the calibration band — 10.04%
relative error is within the documented-normal band" — the retired band, the wrong
reason. Every satellite document moved (`PROOF.md`, `DAFOAM_CASE_STATUS.md`,
`NOT_PASSING_REGISTER.md:339`, `ACTIVE_RESEARCH.md:98,112`); the case's primary
record did not. A reader who goes to the case file — the natural place — gets a
verdict that is wrong twice. Filed as **LESSONS L-32**.

**D-2. One misprinted magnitude in `PROOF.md` §25.5.** "The converged baseline CD is
0.15296979–0.15297237 … a spread of **1.7e-06 relative**." The spread is 2.58e-06
**absolute**, which is **1.7e-05 relative** — a factor-of-10 slip. The substantive
claim it decorates ("invariant to five significant figures") is correct: both
endpoints print 0.15297. Verified against all nine logs (baseline CDs re-extracted
below).

**W-1 (wording).** The A5 decomposition-invariance sentence — "worst single component
0.75%, and zero components differ by more than 1% in any group" — is true only for
the three **Upper** DV groups it names. Recomputing all six groups from the logs'
own printed Jacobians: `shapeyLower` idx6 differs by **11.64%** between `scotch` and
`simple`. It is a noise-floor entry (6.7e-04 of its group's largest component;
3.9e-05 of the group norm), and all six group-norm differences are ≤3.8e-04, so A5
**is** decomposition-invariant in substance — but the "any group" phrasing over-reads
the evidence by a factor of eleven at one component.

**W-2 (provenance hygiene).** The W4 sweep logs (`W4-a4-stepsweep/a4_np*.log`) do
**not** carry the `IDWARP_IMPORTED_FROM:` stamp that W5's own protocol established;
stock-vs-patched provenance for the headline table rests on the driver scripts
(`run_np.sh` line-by-line, mount + `PYTHONPATH` only in the `patched` arm), not on
in-log evidence. Mitigated two ways: the W5 np=4 pair *is* stamped
(`W5-regrade/a4_{stock,patched}_checktotals.log`) and reproduces the same two
numbers, and this sweep's own stamped re-run (below) reproduces the np=2 patched
cell exactly.

**W-3 (presentation).** The PASS is quoted at **0.76%** (np=4 `simple`, stock) in
`W5_GRADIENT_REGRADE.md` §2 and `NOT_PASSING_REGISTER.md:339`, but at **1.10%**
(np=1, stock) in `DAFOAM_CASE_STATUS.md:64` and `PROOF.md` §25.5's verdict paragraph.
Both are real logged numbers on the shipped toolchain; no single graded configuration
is named as *the* graded one. Recommend the records converge on one (np=1, 1.10%, is
the defensible choice: it involves no decomposition at all), with the other stated
as corroboration.

---

## Axis 1 — PROVENANCE: **CONFIRMED**

Every cell of the §25.5 table traces to a run artifact on disk, timestamps 2026-08-02
06:07–07:13 UTC, one directory per cell, each staged fresh from
`/home/ubuntu/certonomous-runs/A4-ahmed-body/coarse` (whose `0/` is byte-identical to
`0.orig/` — pristine). Re-extracted from the logs' own OpenMDAO rows
(`/home/ubuntu/certonomous-runs/W4-a4-stepsweep/`):

| cell | log | analytic | FD | rel. err | claimed |
|---|---|---|---|---|---|
| np=1 stock | `a4_np1_stock.log` | 2.3965e-01 | 2.4232e-01 | 1.1032e-02 | 1.10% ✓ |
| np=1 patched | `a4_np1_patched.log` | 2.4150e-01 | 2.4232e-01 | 3.3929e-03 | 0.34% ✓ |
| np=2 patched | `a4_np2_patched.log` | 2.4118e-01 | 2.4182e-01 | 2.6250e-03 | 0.26% ✓ |
| np=3 patched | `a4_np3_patched.log` | 2.5641e-01 | 2.4178e-01 | 6.0518e-02 | 6.05%, high ✓ |
| np=4 scotch patched | `a4_np4_patched.log` | 2.2086e-01 | 2.4258e-01 | 8.9531e-02 | 8.95% ✓ |
| np=4 scotch, tol 1e-10 | `a4_np4_tol1.0e-10.log` | 2.2086e-01 | 2.4258e-01 | 8.9531e-02 | unchanged ✓ (811 GMRES iters, `PetscConvergedReason: 2`) |
| np=4 simple 4x1x1 patched | `a4_np4_simple4x1x1.log` | 2.4220e-01 | 2.4220e-01 | 5.4291e-06 | 0.00054% ✓ |
| np=4 simple 1x4x1 patched | `a4_np4_simple1x4x1.log` | 2.4379e-01 | 2.4265e-01 | 4.7034e-03 | 0.47% ✓ |
| np=4 simple stock | `a4_np4_simple411_stock.log` | 2.4037e-01 | 2.4220e-01 | 7.5935e-03 | 0.76% ✓ |
| np=4 scotch stock (2x2 corner) | `a4_h1e-3_stock.log` | 2.1821e-01 | 2.4258e-01 | 1.0044e-01 | 10.04%, = published ✓ |

"Only the decomposition varied" verified by `diff` of every run directory against the
source case: the np runs carry a **byte-identical `runScript.py`**; the `simple` runs
differ by exactly one inserted `decomposeParDict` daOption line; the tolerance run by
exactly the `gmresRelTol` value. The logs' own `Decomposition method` lines read back
`scotch [2]`/`[3]`/`[4]` and `simple [4]` as claimed — the check that catches the
inert-`decomposeParDict` trap the record itself documents. Baseline CDs re-extracted:
0.15296979–0.15297237 across all configurations, exactly the claimed span (five
significant figures; see D-2 for the misprinted relative spread). FD column span
(2.4178–2.4265)e-01 = 0.36% ✓. Colour counts (1087/1393/1387/1343/1294/1327) and
GMRES iterations (542/561/753/719/671/598) all match §25.5's non-discrimination
table to the digit. The `dCD/dXv` probe numbers (0.54%/0.47%, hand-composition
5.70e-09/8.51e-10, baseline diff 8.9e-07) match `a4_dcddxv.log`'s `A4P_*` lines
exactly.

## Axis 2 — SCRIPT PROOFREAD: **CONFIRMED**

Drivers read end-to-end (`run_np.sh`, `run_decomp2.sh`, `run_tol.sh`,
`stage_and_run.sh`, `run_decomp.sh`, `W4-a4-decompcut/run.sh`). No wrong column
pairing: the table rows are OpenMDAO's own `check_totals` output line
(`calc mag. | check mag. | a(cal-chk) | r(cal-chk)`), one instrument, one formula
(`|calc−chk|/chk`), uniform across rows. **The FD is computed per run, inside each
run's own `check_totals`** — not once and reused — which is why the FD column
legitimately varies by 0.36% across decompositions; each row's error is measured
against its own decomposition's FD, the correct pairing, and no shared-FD bias
exists. Each script stages a fresh copy, makes one `sed`/Python edit, and
**greps the edit back before running** (exit 2 on failure). The one genuine trap in
this experiment class — `system/decomposeParDict` edits being silently regenerated
by `pyDAFoam` — is handled by editing the daOption instead and reading the log's
`Decomposition method` line back.

## Axis 3 — LOGIC AUDIT: **CONFIRMED, with the caveats in D-1/W-3**

The two numbers cohere: **1.10%** is np=1 on the **stock** toolchain — the graded
number, because the lab grades against what ships — and **0.34%** is the same
configuration under the local IDWarp patch, recorded as diagnosis, not as the grade.
Grading at np=1/`simple` while the *default* configuration (np=4 `scotch`) still
reads 8.95–10.04% is defensible **only with the caveat attached**, and the caveat
is attached where it matters: `PROOF.md` §25.5 closes with "A4 has a correct
gradient under a decomposition that can be chosen, and an unexplained one under the
default", `DAFOAM_CASE_STATUS.md:64` names the 10.04% "an artifact of DAFoam's
default `scotch` decomposition" with "Mechanism NOT identified", and the
NOT_PASSING_REGISTER entry survives (for the fine-mesh adjoint) rather than being
deleted. The verdict language matches the evidence on those surfaces. Where it does
**not** match is the case's own ladder record (D-1), and until that is reconciled
the PASS is one `ladder-a/` read away from being contradicted by its own file.

## Axis 4 — INDEPENDENT DIAGNOSTIC: **CONFIRMED, to every printed digit**

One cell re-run from scratch by this sweep with its own driver, own staging, own
container invocation: np=2, patched IDWarp, `check_totals`, 2026-08-04 15:09–15:11 UTC
(`/home/ubuntu/certonomous-runs/VERIFY-a4-np2-20260804/`, `run.log`). Staged inputs
verified byte-identical to the archived run's (`0/`, `constant/`, `runScript.py`
diff-clean). Result:

```
IDWARP_IMPORTED_FROM: /patch/idwarp/idwarp/__init__.py
Decomposition method scotch [2] (region region0)
CD wrt dvs.shape | 2.4118e-01 | 2.4182e-01 | 6.3477e-04 | 2.6250e-03
baseline CD: 0.15297195   GMRES: 561 iterations, PetscConvergedReason: 2
```

Analytic, FD, absolute error, relative error, baseline CD, and GMRES iteration
count all identical to `a4_np2_patched.log` to every printed digit — and this run
carries the `IDWARP_IMPORTED_FROM` stamp the archived one lacks (W-2), closing that
gap for the one cell it covers. Cost: **86 s wall at `--cpus=2` ≈ 2.9 solver
core-min**, against the ~30 budgeted.

## Axis 5 — A1/A5 INVARIANCE + the hanging-node refutation: **CONFIRMED** (artifacts only)

* **A1** (`W4-a1-rank/a1_np{1,4}.log`): CD/shape relative error **3.795529e-04**
  (np=1) vs **3.807681e-04** (np=4), exactly as claimed. Decomposition-invariant.
* **A5** (`W4-a5-decomp/a5_{scotch,simple}.log`): all six 27-component gradient
  groups re-extracted from the logs and the norms recomputed independently by this
  sweep: shapexUpper 2.3576e-04, shapeyUpper 2.9973e-04, shapezUpper 3.4623e-04 —
  the three published values reproduced to the digit — and the three unpublished
  Lower groups at 3.0e-04/3.8e-04/3.7e-04. Invariant at norm level in all six; see
  W-1 for the one noise-floor component the published sentence glosses.
* **Hanging-node hypothesis, refuted backwards — independently recomputed.** This
  sweep re-classified all 7,843 internal faces itself (own Python, from
  `owner`/`neighbour`/`cellLevel` and the archived `cellDecomposition` maps in
  `W4-a4-decompcut/`): 456 refinement-interface faces; `scotch` cuts **4** (0.88%),
  `simple` 4x1x1 cuts **68** (14.91%). Identical to the claim. The decomposition
  that cuts seventeen times more refinement interfaces is the accurate one; the
  hypothesis is refuted, not merely unconfirmed.

---

## Verdict

**The A4 CONDITIONAL→PASS claim is CONFIRMED on the evidence and survives
independent re-measurement.** The published 10.04% is a `scotch`-decomposition
artifact; the gradient itself verifies at 1.10% stock/np=1 (0.26% at this sweep's
own re-run of np=2 patched, 5.4e-06 at np=4 `simple` patched). Required follow-ups,
none of which reopens the verdict: reconcile `ladder-a/A4_ahmed_body.{md,json}`
(D-1, the blocking one), fix the §25.5 spread misprint (D-2), scope the A5
invariance sentence (W-1), and name a single graded configuration (W-3).

Sweep cost: **2.9 solver core-min** (one np=2 `check_totals`) plus zero-solver
recomputation. Verified by: supervisor verification sweep, 2026-08-04, per
`ACTIVE_RESEARCH.md`'s "pending supervisor verification sweep (2026-08-04)" gate.
