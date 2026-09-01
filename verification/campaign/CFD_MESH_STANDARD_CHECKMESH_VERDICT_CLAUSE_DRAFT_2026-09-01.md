# DRAFT clause for `docs/standards/MESH_STANDARD.md` §3.1 — the gate is read off the REPORTED MAXIMUM, never off `checkMesh`'s own verdict line

**Status: DRAFT. NOT APPLIED. The cfd supervisor owns `docs/standards/MESH_STANDARD.md` and
lands this change personally.** Prepared by a cfd lane 2026-09-01 on the supervisor's
instruction. **This file edits nothing.** Zero compute.

**Live path confirmed at read time, because two different documents share a name:**
- `docs/standards/MESH_STANDARD.md` — 88,948 B, `# Certonomous Mesh Standard`. **The quality
  gates. This is the target.**
- `docs/MESH_STANDARD.md` — 15,561 B, `# Grid-Convergence Practice — Inherited from
  DPW-8/AePW-4`. **A different document. Not the target.**

---

## The measured instance, read from the log by this lane and not relayed

`verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study/t1_SHELL/log.checkMesh`,
lines 96–98, **verbatim**:

```
    Mesh non-orthogonality Max: 81.5834 average: 15.5977
   *Number of severely non-orthogonal (> 70 degrees) faces: 516.
    Non-orthogonality check OK.
```

**Three consecutive lines, and the third contradicts the first two against the lab's gate.**
The mesh carries a maximum non-orthogonality of **81.5834°** against the lab's **70° hard
gate**, and 516 faces are flagged severe — yet `checkMesh` prints
**`Non-orthogonality check OK.`**

**Why**: the `70` in `nonOrthThreshold_` that §3.1 already cites drives the *severe-face
warning list* (line 97, with OpenFOAM's `*` warning marker). The **verdict** line 98 is
decided against a separate, much higher internal error limit, so `checkMesh` reports OK on
any mesh it considers merely poor rather than unusable. **The tool is answering its own
question, correctly. It is not answering ours.**

**The overall line at 104 reads `Failed 1 mesh checks.` — and that failure is the
aspect-ratio check, not non-orthogonality.** So even the file-level verdict does not carry
the breach, and a reader who checks only the last line learns the wrong thing about the
wrong metric.

**Corroborating negative control, same study:** the `nofill` variant at
`verification/runs/F13_ONERA_M6_runs/mesh/CONTROL_nofill_L1_checkMesh.log` reports
`Mesh non-orthogonality Max: 51.2554` and the **same** `Non-orthogonality check OK.` line.
**The verdict line reads identically at 51.26° and at 81.58°** — it cannot discriminate the
admissible mesh from the inadmissible one, which is exactly what makes it unusable as a gate.

---

## The proposed clause, for insertion in §3.1

> **Reading the gate — the reported maximum, never the tool's verdict line.**
> The 70° gate is applied by this lab and is read off the **reported maximum
> non-orthogonality** (`Mesh non-orthogonality Max:`), together with the **count of severely
> non-orthogonal faces** where `checkMesh` reports one. **It is never read off
> `checkMesh`'s own `Non-orthogonality check OK.` line, and never off the file's closing
> `Mesh OK.` / `Failed N mesh checks.` line.** Those lines are decided against OpenFOAM's
> internal error limits, which are far above this gate: a mesh with **max 81.5834° and 516
> severe faces prints `Non-orthogonality check OK.`**
> (`verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study/t1_SHELL/log.checkMesh:96-98`),
> and the identical verdict line prints at 51.2554° on the same study's `nofill` control.
> **A tool's pass is not this lab's pass.** Any comparator, admission check or gate script
> that greps a verdict string instead of parsing the reported maximum is reading the wrong
> instrument and its clean result is not evidence.
>
> **Report the severe-face count beside the maximum.** The maximum can asymptote and look
> stable under refinement while the severe-face *fraction* rises an order of magnitude — the
> measured signature recorded at `N-C8`'s neighbour `N-C6` (516 → 7,200 severe faces, 0.158 %
> → 1.694 %, while cells rose only 1.31×). The maximum alone hides that propagation.

---

## Why this belongs in the standard rather than in a lane's habits

**A gate that can be satisfied by reading a different line than the one the gate names is not
a gate.** This lab has already paid for the general form of this once: a reader that returns
a pass because it was asked the wrong question is the planted-zero failure mode (rule 3), and
here the wrong question is asked *by the instrument itself*, in a line that sits two rows
below the right answer and reads as authoritative.

**The exposure is not hypothetical.** Any admission script written against the natural string
— `Non-orthogonality check OK` — passes a mesh at 81.58° silently, and the F13 ladder is the
case where that mattered.

## What this draft does NOT propose

- **It does not change the 70° threshold**, in either direction. Retiring, widening or
  narrowing a gate threshold is reserved to Sanaa.
- **It does not change the 65–70 warning band or the §3.1 action clause.**
- **It does not touch §3.3's aspect-ratio advisory**, which remains advisory and "never a
  lone rejection".
- **It proposes no new gate.** It fixes *where the existing gate is read from*.

## Verification the supervisor may want before landing

1. The three quoted lines are at `t1_SHELL/log.checkMesh:96-98`; the closing verdict is at
   `:104`.
2. The `nofill` control's identical verdict line is at
   `verification/runs/F13_ONERA_M6_runs/mesh/CONTROL_nofill_L1_checkMesh.log:97-98`.
3. `docs/standards/MESH_STANDARD.md` carries a **known version discrepancy already recorded
   at its own line 441** ("recorded rather than silently repaired"). This draft does not
   touch it and any version bump for this clause should be reconciled against that note.
4. §6b/rule 6 discipline: if §3.1 is frozen for citation, this lands as a dated amendment at
   the foot with the `lines whose number changed above this section: 0` assertion, not as an
   in-place edit of §3.1.
