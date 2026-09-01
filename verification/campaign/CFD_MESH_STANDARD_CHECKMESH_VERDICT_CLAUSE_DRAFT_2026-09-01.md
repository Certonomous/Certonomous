# DRAFT amendment for `docs/standards/MESH_STANDARD.md` — the 70° gate is read off the REPORTED MAXIMUM, never off `checkMesh`'s own verdict line

> # ⛔ STATUS: **LANDED 2026-09-01 — DO NOT APPLY THIS BLOCK AGAIN.**
>
> This proposal **is now §14 of `docs/standards/MESH_STANDARD.md`**, landed at commit
> **`afedaadcbdd521d3a314d3e3bf7f2585a8e3d26e`** (124 insertions, **0 deletions**, digest
> assertion `434b6ebe…` before against the first 1,436 lines after — **EQUAL**), with one
> addition made at landing that is **not** in the text below: §14.3 gained a second table
> showing the closing `Failed N mesh checks.` line runs **anti-correlated** with §3.1 on this
> pair (admissible mesh `Failed 2`, inadmissible mesh `Failed 1`).
>
> **ORDINAL CORRECTED.** It landed as **§10** and was corrected to **§14**, because the file
> already carried a §10 (paper provenance, v1.5) and its section sequence runs to 13. **The
> cause was conflating the section VERSION with the section ORDINAL** — `v1.9` was derived
> correctly from the highest section *version* `v1.8` and is unchanged, but the two counters
> diverged at §11/v1.6. **The version is not the ordinal.** Corrected and disclosed in the
> section itself; nothing else in the block moved.
>
> **Applying it a second time would give that standard a duplicate section.** This file is
> retained only as the historical record of what was proposed and reviewed. **The live text
> is in the standard; read it there.**

**Status when written: DRAFT, NOT APPLIED.** Prepared by a cfd lane 2026-09-01 for the cfd
supervisor, who owns `docs/standards/MESH_STANDARD.md` and landed it personally after reading
it. **This file edits nothing.** Zero compute.

**RULE-6 FORM, NOT AN IN-PLACE EDIT OF §3.1.** The standard is a frozen file: other records
cite it by line and at least one citation sits inside an executable check, so editing §3.1
in place would break them silently. The block below is **appended at the foot**, with a
version bump and the `lines whose number changed above this section: 0` assertion **measured**
in the file's own established md5 form, not asserted.

**Live path confirmed at read time, because two different documents share a name:**
- `docs/standards/MESH_STANDARD.md` — 88,948 B, 1,436 lines, `# Certonomous Mesh Standard`.
  **The quality gates. This is the target.**
- `docs/MESH_STANDARD.md` — 15,561 B, `# Grid-Convergence Practice — Inherited from
  DPW-8/AePW-4`. **A different document. Not the target.**

**Landing mechanics for the supervisor.** At HEAD as read 2026-09-01 the file is **1,436
lines**, HEAD blob md5 **`434b6ebec1b8f09e4ea276d71456796e`**, worktree identical. **Recompute
both at landing time** — a peer may land in this file first, and a stale digest is exactly the
failure the assertion exists to catch. The append is verified by: md5 of the HEAD blob before
the append, md5 of the first 1,436 lines after the append, and the two being **EQUAL**.

**Highest section version currently in the file is `v1.8`, so this block is `v1.9`.**

---

# THE BLOCK TO APPEND (everything below this rule)

---

## 10. READING THE NON-ORTHOGONALITY GATE — the reported maximum, never `checkMesh`'s verdict line (v1.9, 2026-09-01)

**Lines whose number changed above this section: 0.** Nothing above is edited, reordered,
inserted or deleted. Verified by digest, not by assertion — see the closing table.

**This section changes NO gate value.** The 70° hard gate of §3.1, its 65–70 warning band and
its action clause are untouched, in either direction. Retiring, widening or narrowing a gate
threshold is reserved to Sanaa. **What this section fixes is WHERE the existing gate is read
from.**

### 10.1 The finding, in the form that settles it: the verdict line CANNOT DISCRIMINATE

Two meshes from the same 2026-08-25 ONERA M6 topology study, one **admissible** under §3.1 and
one **inadmissible by 11.6°**, produce the **identical** `checkMesh` verdict line:

| mesh | reported max non-orthogonality | §3.1 verdict | `checkMesh` prints |
|---|---|---|---|
| `CONTROL_nofill_L1` | **51.2554°** | admissible | `Non-orthogonality check OK.` |
| `t1_SHELL` | **81.5834°** | **inadmissible** | `Non-orthogonality check OK.` |

> **The line reads the same on the mesh that passes and the mesh that fails. It carries no
> information about this lab's gate, and a check built on it cannot fail.**

That is the whole argument, and it is a **discrimination test** rather than a claim about
OpenFOAM's internals: a reader that returns the same answer for a known pass and a known fail
has been shown unable to see the difference, which is the planted-control standard this lab
already applies to every comparator (CLAUDE.md rule 3). **Here the reader is the instrument
itself.**

*Artifacts:*
`verification/runs/F13_ONERA_M6_runs/mesh/CONTROL_nofill_L1_checkMesh.log:97-98`;
`verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study/t1_SHELL/log.checkMesh:96-98`.

### 10.2 Three consecutive lines, the third contradicting the first two

`t1_SHELL/log.checkMesh`, lines 96–98, **verbatim**:

```
    Mesh non-orthogonality Max: 81.5834 average: 15.5977
   *Number of severely non-orthogonal (> 70 degrees) faces: 516.
    Non-orthogonality check OK.
```

A maximum of **81.5834°** against a 70° gate, **516 faces** flagged severe with OpenFOAM's `*`
warning marker — and then **`OK`**, three lines apart. The `70` in `nonOrthThreshold_` that
§3.1 cites drives the *severe-face warning list*; the **verdict** line is decided against a
separate and far higher internal error limit. **The tool is answering its own question
correctly. It is not answering ours.**

### 10.3 The file-level verdict does not carry the breach either

The same log closes at line 104 with **`Failed 1 mesh checks.`** — and **that failure is the
aspect-ratio check, not non-orthogonality.** So a reader who checks only the last line learns
the wrong thing about the wrong metric: the file says "failed" for a reason §3.3 explicitly
calls **advisory and never a lone rejection**, while the actual gate breach of 11.6° is
reported nowhere in any verdict string.

### 10.4 THE CLAUSE

> **The §3.1 gate is read off the reported maximum — `Mesh non-orthogonality Max:` — together
> with the count of severely non-orthogonal faces where `checkMesh` reports one.**
>
> **It is NEVER read off `checkMesh`'s `Non-orthogonality check OK.` line, and never off the
> file's closing `Mesh OK.` / `Failed N mesh checks.` line.** Those strings are decided
> against OpenFOAM's internal error limits, which sit far above this gate, and they have been
> **measured unable to discriminate** an admissible mesh from one 11.6° outside the gate
> (§10.1). **A tool's pass is not this lab's pass.**
>
> **Any comparator, admission check, gate script or lane report that greps a verdict string
> instead of parsing the reported maximum is reading the wrong instrument, and its clean
> result is not evidence.**
>
> **Report the severe-face count beside the maximum.** The maximum can asymptote and look
> stable under refinement while the severe-face *fraction* rises an order of magnitude — the
> measured signature at `N-C6` in `docs/NUMERICS_KNOWLEDGE.md` (516 → 7,200 severe faces,
> 0.158 % → 1.694 %, while cell count rose only 1.31×). **The maximum alone hides that
> propagation.**

### 10.5 A version discrepancy NAMED, and deliberately NOT resolved here

This file's header (line 3) reads `Version 1.2, dated 2026-08-11`, while the highest section
version is **`v1.8`** before this block and **`v1.9`** with it. **The header has been stale
since §8 landed and is recorded as such at line 441.** It is **not** repaired here, and not
merely because editing line 3 would move every line number above — **a version bump that
quietly resolves a pre-existing inconsistency is a second, undisclosed change riding inside a
disclosed one.** The authoritative version of this document remains the **highest section
version**. Repairing the header stays a separate, disclosed edit for whoever takes it.

### 10.6 What this section does NOT do

- It does **not** change the 70° threshold, the 65–70 warning band, or §3.1's action clause.
- It does **not** touch §3.3's aspect-ratio advisory, which remains advisory and never a lone
  rejection.
- It proposes **no new gate** and moves no existing one.
- It does **not** claim `checkMesh` is defective. `checkMesh` is correct about its own
  thresholds; the defect is in reading its answer as though it were ours.

| assertion | value |
|---|---|
| gate values changed by this section | **0** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's HEAD blob before the append | *(recompute at landing)* |
| md5 of this file's first 1,436 lines after the append | *(recompute at landing)* |
| the two digests | *(must be **EQUAL — assertion MEASURED**)* |
