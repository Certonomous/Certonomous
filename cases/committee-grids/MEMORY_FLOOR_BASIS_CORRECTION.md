# CORRECTION OF RECORD — the `memory_floor_gb` basis in the DPW5 committee-grid queue rows is **HEX-SCOPED**, and its own description is wider than its selection

> **This is a RECORD, not a repair. No placed artifact is edited.**
>
> Ruled by the cfd supervisor, 2026-09-06: R2-M0's row is a placed artifact of a completed,
> graded run, and editing it would put today's hand on a record that has already done its work —
> the reasoning that kept this team out of JF1G's comparator. **The correction is recorded where a
> reader meets the basis; the artifact is left exactly as it stands.**
>
> *Found by a cfd `lab-lane` while staging the R2-M1 row, 2026-09-06, by re-deriving the figure
> from source instead of copying it forward. Zero compute.*

---

## 1. What the rows say

`verification/queue/cfd/launched/RUNG2-CRM-M0.json` (**placed**) and its draft-of-record
`cases/committee-grids/QUEUE_ROW_R2M0_READY_NOT_PLACED.json` both carry `memory_floor_gb: 4.0`,
derived, in their own words, from

> *"`/home/ubuntu/certonomous-runs/dpw5-committee-probe/measurements.jsonl`, **the four
> `*_a2.11` rows**: `sum_vmhwm_mib` 2020.3 (incompressible, 200 iterations, exit 0), 2147.1,
> 2172.2, 1868.9 (the three compressible arms). **LARGEST MEASURED = 2172.2 MiB = 2.121 GiB.**"*

## 2. What is actually there

`measurements.jsonl` carries **thirty** rows tagged `*_a2.11`, not four. The four the row used are
the four **hex** rows — `hex_base_incompressible`, `hex_base_compressible`, `hex_trans_compressible`
and `hex_transu1_compressible`. **The selection is right for the probe. The description of it is
wider than the selection.**

There are **four** compressible (`rhoSimpleFoam`) `a2.11` rows, not three. The fourth is:

| tag | app | `sum_vmhwm_mib` | `peak_sum_rss_mib` | exit |
|---|---|---|---|---|
| **`hybrid_base_compressible_a2.11`** | `rhoSimpleFoam` | **5069.1 MiB = 4.950 GiB** | 4797.4 | 136 |
| `hex_trans_compressible_a2.11` | `rhoSimpleFoam` | 2172.2 = 2.121 GiB | 2064.2 | 136 |
| `hex_base_compressible_a2.11` | `rhoSimpleFoam` | 2147.1 | 2056.4 | 136 |
| `hex_transu1_compressible_a2.11` | `rhoSimpleFoam` | 1868.9 | 1868.8 | 136 |

**The hybrid row sits ABOVE the 4.0 GB floor both queue rows carry.**

This is corroborated independently, and was never hidden: `COMMITTEE_GRID_NUMERICS.md:221` already
records **peak memory at death 4,870 MiB for the DPW5 hybrid** arm (a different run and a different
metric — peak RSS, 08:06Z — but the same order), against 2,866 MiB for prism. The larger figure was
in the case documentation the whole time. **What the queue row did was select correctly and then
describe the selection loosely.**

## 3. ⚠ The part that makes this a finding rather than pedantry

**It is HARMLESS for R2-M0 and R2-M1, and MISLEADING to anyone reusing the basis off hex.**

- Both probes run the **hex** L1.T grid. Both peak near **2.1 GiB**. A 4.0 GB floor gives ~1.9×
  headroom and neither run came close to it. **No verdict, cost or scheduling decision is affected.**
- But a reader who takes *"the four `*_a2.11` rows"* at face value — as the whole population rather
  than a hex-scoped selection — and reuses `memory_floor_gb: 4.0` **for a hybrid or prism arm would
  be setting a floor BELOW a figure already measured on this box.**

**If a probe on this grid family ever moves off hex, 4.0 GB is not the floor.** Re-derive it, scoped
to the topology being run, and say which topology in the derivation.

## 4. What was done instead of editing anything

`cases/committee-grids/QUEUE_ROW_R2M1_READY_NOT_PLACED.json`:

- re-derives its floor **from source**, not by copying M0's forward — which is the only reason this
  surfaced at all;
- keeps **4.0 GB** but states the **hex scope** explicitly in the derivation;
- names the excluded `hybrid_base_compressible_a2.11` row and **why** it is excluded, in a field
  called `memory_floor_caveat_that_M0_S_ROW_DOES_NOT_CARRY`, **so the exclusion is visible rather
  than silent**;
- keeps M0's honest caveat that the hex compressible arms **aborted at iteration ≤ 2**, so their
  footprint is a **lower bound**, not what a 50-iteration arm would reach. The nearest long-run
  figure on this grid is the hex incompressible arm at **2020.3 MiB over 200 iterations**.

## 5. The general point, for the next row

**A derivation should name the population it selected from, not just the rows it kept.** Both figures
here were correct; only the sentence around them was wide. That is `L-490`'s family — a key that also
matches its neighbours — reappearing in **prose about a measurement** rather than in code, and it is
caught the same way: by **re-deriving from source instead of copying a number forward**.

**Related:** `L-496` (a guard that crashes reports the wrong failure) and the R2-M1 dry run's stale
`b1_warmstart_note`. All three are artifacts that are **wrong in a quotable way while nothing
crashes** — the class that survives any check asking *"did it fail?"* rather than *"did it do the
thing?"*
