# PETITION — VMFL046-R4, the W1 read-audit counts the comparator's own planted-control scratch files

**Status: PENDING — before the verification referee. Not self-repaired.**
**Filed 2026-09-06 by the ansys-verification supervisor.**
**Predecessor grant: `VERIFICATION_CHARTER` v1.67 §2av (`8bdd5351`) — DISCHARGED, all four
requirements met, commit `8c25032b`.**

---

## 1. What this petition is, in one paragraph

The §2av grant repaired two miscalled plant call sites in `VMFL046-R4`'s frozen comparator.
The repair worked: the `TypeError` is gone and `grade()` now runs past `:1063`. It then
**refuses at a different clause it could never previously reach** — the W1 read audit — because
the audit counts the comparator's **own planted-control scratch files** as centreline samples
read outside the registered window. This is a **second, independent defect, structurally hidden
behind the first**. It is **not covered by §2av** and, unlike the §2av defect, **its repair is
not forced**. So it comes up rather than being fixed.

---

## 2. The refusal, verbatim from the frozen path

Running the committed, repaired comparator over the real run root
`verification/runs/ansys_verification/VMFL046-R4` exits **rc = 2**:

> `REFUSE: L1: W1 VIOLATED -- the comparator opened 19 centreline sample(s) OUTSIDE its
> registered window t in (0.064, 0.08]: /tmp/vmfl046r4_plantA_cpvkw9on/line_T_U.xy,
> /tmp/vmfl046r4_plantB_krp9vm7c/s8.xy, /tmp/vmfl046r4_plantC2_6_luyh36/s0.xy ....`

---

## 3. The triage — MEASURED, not inferred

Driven against the real L1 run directory, instrumenting `_CL_READS` around the plant block
without modifying the frozen file:

| quantity | value |
|---|---|
| registered window | `(0.064, 0.080]` |
| real reads recorded **before** any plant runs | **33** |
| the registered window's own sample count | **33** — they are the same set |
| paths **added** by the four plants | **19** |
| of those 19, how many are under `/tmp` | **19 (all)** |
| of those 19, how many are inside the run root | **0 (none)** |

**The audit's real subject is clean.** The comparator read exactly the 33 samples the
registration entitled it to read, and not one sample more. Every path that trips W1 is a
temporary file the comparator itself wrote in `plant_gate_reader`, `plant_plateau_reducer` and
`plant_field_readback_per_sample`.

## 4. Why no run and no selftest arm could ever have reached this

`grade()` does three things in this order:

- `:1042` `_audit_reset()` — the audit is armed
- `:1062–1066` the five plants run, each writing and re-reading `/tmp` scratch samples through
  `read_centreline_raw`, which appends to `_CL_READS` at `:298`
- `:1069` `audit_window_only(L, bounds, hist)` — the audit is checked

**The shipped code crashed at `:1063`, inside the plant block, before control ever reached
`:1069`.** The audit defect sat behind the crash defect. Repairing the first was the only way to
expose the second.

**And the selftest could not reach it either.** `audit_window_only()` is exercised at `:1317`
in isolation — `_audit_reset()`, then audit. **The plants-then-audit ordering that `grade()`
actually uses is exercised nowhere in 63 arms.**

> **This is the SECOND §2p.3(d) defect in this one file, found the same day, and both have the
> identical shape: THE SELFTEST EXERCISES THE PARTS AND NEVER THE PRODUCTION SEQUENCE.**
> A comparator selftest that never drives `grade()` end-to-end measures its own coverage, not
> the comparator — §28.19, exactly as §2av.5 requirement 4 already said about the first one.

## 5. Why I am NOT self-repairing this under §2av

§2av.4 states its own limit:

> *"WHERE A CRASH ADMITS SEVERAL CORRECT-LOOKING REPAIRS THAT WOULD READ THE DATA DIFFERENTLY,
> THIS TEST FAILS AND §2d.1's ordinary burden returns IN FULL."*

That converse is met here. Four repairs are available and they **audit different sets**:

| # | repair | effect on W1's coverage |
|---|---|---|
| (a) | `_audit_reset()` after the plants | audit becomes **EMPTY** → the file's own `:1354` arm refuses an empty audit. **Self-defeating; eliminated by the file's own logic.** |
| (b) | arm the audit after the plants instead of before | coverage collapses from **33 real reads to 1** (only `cl_last`). The 33 reads that actually produce the value go unaudited. **Materially weakens W1.** |
| (c) | audit only paths inside the run root | keeps all **33**, drops the **19** synthetic. |
| (d) | snapshot `_CL_READS` before the plants, restore after | same set as (c) here, but would also mask a plant that read a **real** out-of-window sample. |

I have a view — (c) reads as the correct semantic, because W1 asks whether the comparator
consumed **run data** outside its window and a `/tmp` scratch file is not run data. **I record
that as a recommendation and not as an action.** Choosing among (b), (c) and (d) while holding
the run data is precisely the degree of freedom §2av's narrowness exists to deny me.

### 5.1 The honest qualification, stated against my own interest and in my favour

The freedom here is **real but orthogonal to the value**. None of (b), (c) or (d) touches
`shock_series`, `plateau`, the gate (`1.250 m, ±5 %`) or the plateau threshold
(`DELTA_X = 6.250e-04 m`). Whichever is chosen, **x_shock and the plateau statistic are
byte-identically computed**. The freedom is over *whether the comparator refuses or proceeds*,
not over *what number it reports*.

That is weaker than §2av's forced repair and stronger than an ordinary §2d.1 petition, and the
referee should have it in those terms rather than in mine.

### 5.2 ⚡ I HAVE NOT LOOKED AT THE ANSWER, DELIBERATELY

**I do not know what verdict VMFL046-R4 would return, and I have not tried to find out.** No
local patch, no bypass, no "just to see".

State this precisely, because the precise version is the stronger one: `plateau()` runs at
`:1045`, **before** the audit is checked at `:1069`, so the level value `pl["x_level"]` **was
computed inside the process** — and the comparator refused before printing it. **I could have
printed it with one line and did not.** The number has not been read, by me or by any lane.

The referee therefore rules this petition **without the petitioner being able to know — or to be
suspected of knowing — which way the repair moves the verdict.** That is the strongest evidence
available that this petition is not aimed, and it is why it was written before the number rather
than after.

### 5.3 What the run itself demonstrated on the way to the refusal

For L1 the frozen comparator passed, **in order and before refusing**: `check_completion` (the
rule-4 strict completion transliteration), `assert_refining_sampler`, `check_limiters_nonbinding`
(N4), `centreline_history` (160 samples), `registered_window`, `shock_series`, `plateau` — **and
all five planted controls fired**, `pa`, `pb`, `pc1`, `pc2`, `pd`.

**Two of those five — `pb` and `pc2` — had never once executed in production before this
repair**; they are the sites §2av repaired. They fire. **The §2av repair is vindicated as a
repair.** What stops the grade is the audit's scope, and nothing else.

---

## 6. What is asked

1. A ruling on **which of (b), (c) or (d)** repairs the W1 audit's scope, made by the referee
   and not by this team.
2. Under the same four requirements §2av carried: shas and diff, the refusal reproduced,
   the repair confined to the audit's path-selection, **and a driven control that exercises the
   plants-then-audit ordering** — the coverage gap that produced both defects.
3. Separately, and larger than this case: a view on whether a comparator selftest that never
   drives `grade()` end-to-end on a synthetic run root should continue to count as a freeze
   qualification. Two defects in one file in one day says it should not. `check_freeze_ready.py`
   (`181cd921`) does not catch this class either — its C3 declares that it checks the
   comparator, and it does not check the comparator's **production ordering**.

## 7. What lands regardless of this ruling

Register row **#61** records what the frozen path returned, which is a **refusal**, and it lands
now rather than waiting on this petition. The 489 core-min is **not vindicated and not written
off**; it is held, with the reason named.
