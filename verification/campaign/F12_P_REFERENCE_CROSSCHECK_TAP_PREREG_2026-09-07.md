# F12 P-reference cross-check — SPOT TAP PRE-REGISTRATION

**PRE-REGISTRATION — FROZEN BY COMMIT, BEFORE THE PRIMARY IS READ AT THESE TAPS.**

**Written 2026-09-07 by a `lab-lane` worker for the cfd team**, executing the
verification ruling `verification/campaign/F12_P_REFERENCE_PROVENANCE_RULING_2026-09-07.md`
(ruling id **d1a55db1**), HEAD `b8066456` at authoring. **Cost: 0 solver core-min, $0.00**
(a read-and-compare task; no solver, no mesh, no case directory).

This file fixes the spot set of Cp taps to be cross-checked, and the fidelity
metric and tolerance, **before** the cross-check numbers are recorded. Its entire
evidentiary content is that the taps are pinned to a **primary-independent
criterion** and committed **before** the AGARD AR-138 primary values are read
back and tabulated at them — so the taps cannot have been chosen to make the
cross-check pass. The cross-check numbers land in a **separate, later** commit
(the dated addendum the ruling requires), which is what the git history proves.

## Scope, and the two obligations it discharges

The ruling holds that F12's honest disclosure of its reference as SECONDARY
(the AFOSR-HTTM/Stanford flow-case-8621 / Melnik 1981 transcription,
`verification/runs/F12_runs/reference/f8621.txt` and the `.dat` files decoded
from it) satisfies **rule 2's freeze** but NOT **rule 15 / L-144's fidelity
requirement**. Both must hold before a P PASS is defensible. This pre-registration
sets up the rule-15 cross-check the ruling mandates: the secondary's Cp values at
a pre-registered spot set of taps — **including the shock-region taps that
dominate the Gate-1 RMS** — read against the on-box AR-138 primary's own printed
RAE 2822 Case 9 pressure-distribution pages (page images, per L-144).

## The two sources

- **Secondary (F12's reference of record).** `rae2822_case9_cp_upper.dat`,
  HEAD blob `44f6f0c8dfc845174202ea9df5e3134cdda5c50c`, consumed by the F12
  grader `load_experiment_cp()` at `sdk/workflows/rae2822_case9.py:173`. Its Cp
  values were **frozen 2026-07-30** and are immutable; nothing in this task can
  choose them.
- **Primary.** `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`
  (17,588,425 B, 612 pp), title-page-verified this session per L-144: PDF p1
  "AGARD-AR-138 / EXPERIMENTAL DATA BASE FOR COMPUTER PROGRAM ASSESSMENT /
  AGARD Advisory Report No.138", p2 "Published May 1979 / ISBN 92-835-1323-1".
  RAE 2822 contribution (Cook, McDonald, Firmin) opens at PDF p182 (A6-1). The
  **Case 9 surface-pressure table is Table 6.7, PDF p201 (A6-20)**, header
  "CASE 9 M=0.730 ALPHA=3.19 RE=6500000". Test-case conditions are Table 6.2,
  PDF p191 (A6-10).

## Honest disclosure of read order (rule 15 / rule 9)

During location and title-page verification this session, PDF p201 was rendered
and viewed **as a whole page**, so the primary's Case 9 Cp column has been seen
before this commit. This does **not** compromise the freeze, and the reason is
recorded here rather than glossed:

1. The tap-selection criterion below is **primary-independent** — it is fixed by
   (a) the frozen Gate-1 RMS definition and (b) the shock location, which is a
   feature of the flow already visible in the **frozen** secondary and named in
   F12's own **frozen prediction 4**. It does not reference any primary value, and
   in particular it does not reference the primary-minus-secondary difference.
2. The secondary values are frozen (2026-07-30); the primary values are a fixed
   1979 printed table. Neither source can be edited to fit.
3. What this commit still proves in git history: the tap list is pinned **before**
   the cross-check *tabulation* is filed, so the reported agreement cannot have
   been reverse-engineered by dropping taps that disagreed.

## Tap-selection criterion (primary-independent)

Gate-1 (F12 pre-registration §"Gate 1, surface pressure") grades the **unweighted
RMS** of CFD-minus-experiment Cp over the upper-surface taps interpolated onto the
tap stations (`cp_deviation`, `sdk/workflows/rae2822_case9.py:1051`,
`rms = sqrt(mean(diff**2))`, equal weight). In an unweighted RMS the dominant
contributors are the taps with the largest |CFD − experiment|. For this
shock-bearing transonic case those are the taps straddling the upper-surface
shock recompression: the reference Cp there falls steeply (≈ −1.31 at x/c 0.525
to ≈ −0.76 at x/c 0.575), so a linear-eddy-viscosity RANS's shock-position /
smearing error (frozen prediction 1: shock 0.01–0.03c downstream) yields O(0.2–0.5)
Cp errors at fixed x across those taps versus O(0.02–0.05) elsewhere — ~10²× per
tap squared. This is exactly F12's **frozen prediction 4** ("Upper-surface Cp RMS
will be dominated by a small number of taps inside the shock foot"). The spot set
therefore **must** include the shock-foot taps, and adds a spread of chordwise
taps so the cross-check is representative, not shock-only.

## THE PRE-REGISTERED SPOT TAP SET — 12 upper-surface taps

Locations given as the secondary's x/c (its stored value) with the matching
primary Table-6.7 x/c station. **Shock-region dominators are taps 4–10.** No Cp
value is recorded here.

| # | secondary x/c | primary x/c (Table 6.7, p201) | role |
|---|---|---|---|
| 1  | 0.049974 | 0.0500 | forward suction plateau (spread) |
| 2  | 0.100047 | 0.1000 | mid-forward (spread) |
| 3  | 0.300038 | 0.3000 | mid-chord (spread) |
| 4  | 0.500030 | 0.5000 | **shock region — pre-shock** |
| 5  | 0.524967 | 0.5250 | **shock region — peak suction / shoulder** |
| 6  | 0.550003 | 0.5500 | **shock region — shock onset** |
| 7  | 0.575039 | 0.5750 | **shock region — steepest recompression (top RMS contributor)** |
| 8  | 0.599976 | 0.6000 | **shock region — post-shock** |
| 9  | 0.619647 | 0.6196 | **shock region — post-shock** |
| 10 | 0.650048 | 0.6500 | **shock region — recovery** |
| 11 | 0.749994 | 0.7500 | aft (spread) |
| 12 | 0.900013 | 0.9000 | trailing-edge approach (spread) |

## Fidelity metric and tolerance (from the ruling)

- **Metric.** Per tap, `d = Cp_secondary − Cp_primary`, both read at the matched
  station; report `d` per tap and `max|d|` over the set.
- **Read tolerance.** The primary Table 6.7 prints Cp to **4 decimal places**, so
  its own rounding half-width is **±0.00005** and the transcription-vs-print
  difference is expected within **±0.0001** (one print unit). The ruling directs
  that the plot/table read error be folded into the reported **digitisation-
  uncertainty channel**, against the experiment's own quoted tap uncertainty of
  **Cp ±0.0026** at Re = 6.5e6 (F12 pre-reg §"The reference"; AR-138 tape item 10).
- **Decision.** The cross-check **MEETS** fidelity if every tap agrees within the
  read tolerance and thus far within the ±0.0026 tap uncertainty; it **FAILS**
  (P stays BLOCKED) if any tap disagrees beyond the tap uncertainty, or if a
  systematic offset appears that a print/rounding difference cannot explain.

## Gate-neutrality

This is a reference-provenance cross-check. It alters **no gate, threshold, cap,
label or verdict** of F12. F12's frozen Gate-1 band (upper RMS ≤ 0.08, lower
≤ 0.04) is **not re-opened** (rule 2): the cross-check establishes reference
fidelity, not a new band. F12's own row stands as `GATE FAIL` / `NOT HELD`
(`verification/campaign/F12_RESULTS.md`) — its mesh failed admission gate A at
all three levels, so no Gate-1 value was ever computed. This cross-check does not
change that; it discharges the ruling's rule-15 condition on the secondary
reference of record.

## What this file does NOT do

It does not declare F12 P `PASS`. It fixes taps and a metric. The cross-check
result is filed in a separate dated addendum, and the P disposition is owed the
cfd supervisor's personal check-3 (big-claim verification of the tap numbers and
gate-neutrality) and check-1 (any comparison script read as a diff), after which
verification audits. No agent message authorizes anything here (rule 9).

*Written 2026-09-07 by a `lab-lane` worker for the cfd team. No solver was
launched, no mesh was built and no case directory was created in producing it.*
