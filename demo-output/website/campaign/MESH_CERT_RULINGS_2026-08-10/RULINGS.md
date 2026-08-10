# Seven refused certificate rows — rulings

**Chief-routed 2026-08-10 from the Infra family's minting pass (`30566ade`),
which refused 10 of 105 rows the 2026-08-08 mesh audit marked
`CERTIFIED (pre-existing record)`. Seven are mine.** ≈0.5 core-min (seven
`checkMesh` runs, serial).

---

## 0. The frame of everything below — stated first, because that is now twice-earned

**What this ruling covers:** exactly the **seven** meshes named below, **as they
exist on disk at 2026-08-10 19:19 UTC**, judged by **re-running `checkMesh` on
each and comparing the fresh parse against the log the audit row cites.**

**What it does NOT cover, and must not be read as covering:**
- the other **three** refusals (`rae2822-meshcheck/og-coarse`,
  `hlpw6-memory-probe/case_HLPW6`, and the third) — **not mine, not examined**;
- the **95 rows the pass minted** — untouched here;
- the **~73 audit rows outside the 105** — never in this frame;
- any claim about meshes **not on this box**.

**What the discriminator can and cannot decide.** A fresh `checkMesh` decides
whether the *current mesh on disk* has the errors its cited log describes. It
cannot decide whether the mesh was different when the row was written. Where
fresh and cited agree, the stale-log hypothesis is **eliminated for the mesh as
it now stands**, which is the question the certificate answers.

## 1. The correction I must not re-introduce

The chief propagated a stronger claim verbally and corrected it in the record.
**The refusal finding was: *seven cited logs contradict their rows.* It was NOT:
*seven meshes are broken.*** Nobody had re-run `checkMesh`; the rows were refused
at the verdict gate before the cross-check.

**This ruling supplies the missing measurement.** What follows is a fresh
`checkMesh` result, not a re-parse of the same log — and it is stated as such.

## 2. The measurement — fresh `checkMesh` against the cited log

| mesh | cited log | **fresh `checkMesh`** | agree? |
| --- | --- | --- | --- |
| `rae2822-meshcheck/og-fine` | broken, 327 680 cells | **broken, 327 680** | **YES** |
| `rae2822-meshcheck/og-medium` | broken, 81 920 | **broken, 81 920** | **YES** |
| `rae2822-meshcheck/ogrid-coarse` | broken, 20 480 | **broken, 20 480** | **YES** |
| `tmr-bump-finer` | broken, 225 280, AR 2 230 928.97 | **broken, 225 280, AR 2 230 928.97** | **YES** |
| `w1-bump-nasa-grids/coarse` | flagged, 3 520, AR 4 844.49 | **flagged, 3 520, AR 4 844.49** | **YES** |
| `w1-bump-nasa-grids/medium` | flagged, 14 080, AR 5 210.25 | **flagged, 14 080, AR 5 210.25** | **YES** |
| `w1-bump-nasa-grids/fine` | flagged, 56 320, AR 5 277.68 | **flagged, 56 320, AR 5 277.68** | **YES** |

**All seven agree exactly** — verdict, cell count, aspect ratio and the full hard-error
list. **The stale-log hypothesis is eliminated on all seven.** The cited logs
describe these meshes as they stand.

## 3. The rulings

### 3a. `rae2822-meshcheck/og-fine`, `og-medium`, `ogrid-coarse` — **THE ROWS ARE WRONG**

Fresh `checkMesh` reproduces, on all three: **negative-volume cells**,
wrong-oriented face pyramids, non-orthogonality errors, skewness errors.

**These three meshes are broken, and the 2026-08-08 audit marked them
`CERTIFIED`.** That is a row error, not a log error.

**Action: none, deliberately.** No `broken` certificate is written. **An absent
certificate already quarantines the mesh**, so writing one buys no protection and
would assert a verdict the standard does not need me to assert. The conservative
action and the honest one coincide — which is why Infra left the ruling here.
**The audit rows need correction; that is the chief's to order.**

### 3b. `tmr-bump-finer` — **THE ROW IS WRONG, with the mechanism named precisely**

Fresh AR = **2 230 928.97**, above the 1e6 pyHyp-pathology threshold, and far
above the 6.6e4–7.4e4 NASA-grid signature the audit itself documents as a *flag*
rather than an *error*.

**Stated carefully:** this mesh is `broken` **by the standard's own aspect-ratio
threshold**, not by a geometric error — it has no negative volumes. That is a
weaker failure than 3a's and it is not worth blurring: the threshold is doing the
work, and the threshold is the standard's, applied to its own documented ranges.

**Action: none.** Same reasoning as 3a.

### 3c. `w1-bump-nasa-grids` coarse / medium / fine — **EXONERATED and CERTIFIED**

These three were refused for a **different reason**: the mesh states no `nCells`
in its `polyMesh/owner` header, so the minting pass's log-vs-mesh cross-check
could not run. **Verified: the header genuinely has no `nCells` note** — expected,
since these are `plot3dToFoam` conversions of NASA's grids rather than
OpenFOAM-generated meshes.

> **Re-running `checkMesh` performs that cross-check a different way — by
> counting the mesh directly rather than reading a note about it.** Fresh counts
> are 3 520 / 14 080 / 56 320, **matching the cited logs exactly.**

Verdict `flagged` on all three (AR 4.8e3–5.3e3) — **an accepted verdict**;
aspect ratio is never a lone rejection under Mesh Standard 3.3, and these sit in
the same range the audit documents as a flag on NASA-grid families.

**Action taken: certificates minted from the FRESH run** — three meshes move from
quarantined to admitted. `certificate_admits` → `True` on all three. This is a
new measurement, not a parse of the old log, which is why it is permitted where
3a and 3b are not.

## 4. What this says about the audit's `BORN BROKEN: 1`

The chief's note is right and this sharpens it. That headline was **a statement
about the subset the audit re-parsed itself**, sitting beside 105 rows it took on
trust. **Within my seven alone, four meshes fail the audit's own verdict rule** —
three on negative volumes.

**What moved is the coverage the headline implied, not a verified count.** I am
not restating `BORN BROKEN: N` for the corpus, because **my frame is seven
meshes** and a corpus count from a seven-mesh frame would be exactly the error my
own recipe sweep made twice today — concluding about a population from a sample
chosen by a pattern.

**What is established:** of the 7 rows routed to me, **4 are wrong** (3a, 3b) and
**3 are right and now certified** (3c). Nothing follows from that about the other
98 rows, and the honest next question — whether the untouched 95 minted rows
deserve the same fresh-`checkMesh` treatment — is priced at roughly 0.07 core-min
per mesh on this evidence, ≈7 core-min for all 95. **Flagged, not proposed.**

## 5. Artifacts

All seven fresh `checkMesh` logs are archived under `recheck_logs/`, and the
three minted certificates beside them. No mesh, case, or audit row was modified.

---

# ADDENDUM, 2026-08-10 — the 95 fresh re-checks (chief-approved, ~7 core-min)

## Frame, first

**Every retrospectively-minted certificate on this box — all 95 — re-checked by
re-running `checkMesh` on its mesh and comparing the fresh parse against the
certificate.** Not the meshes without certificates; not the ~73 audit rows
outside the 105; not any mesh off this box.

## Result

> **AGREE 95 · DRIFT 0 · checkMesh-did-not-run 0 · points-hash mismatch 0.**
> **3.49 core-min against ~7 approved.**

**The six carrying the log-older-than-points ordering flag were run FIRST**, as
ordered, because they were the subset where staleness could hide:

| mesh | certificate | fresh | |
| --- | --- | --- | --- |
| `.mesh-cache/b52` | clean, 193 880, AR 6.5204 | clean, 193 880, AR 6.5204 | no drift |
| `.mesh-cache/motorBike` | clean, 353 688, AR 41.0967 | clean, 353 688, AR 41.0967 | no drift |
| `W4-defect-reach/a35_np1` | clean, 2 777 | clean, 2 777 | no drift |
| `W4-defect-robustness/a4conf_np4scotch` | clean, 2 336 | clean, 2 336 | no drift |
| `W5-regrade/a4_stock` | clean, 2 777 | clean, 2 777 | no drift |
| `r2-plate-uq/_probe` | flagged, 13 056, AR 66 642.5 | flagged, 13 056, AR 66 642.5 | no drift |

They were clean, so the remaining 89 were finished. **The corpus of retrospective
certificates now stands on fresh measurement rather than inherited paper**, and
every points hash still matches the mesh beside it.

## Two defects found in the running, both mine, both reported

**1. `parse_check_log` returns `verdict: "clean"` on a checkMesh FATAL ERROR.**
Found when my first harness for the two bare `.mesh-cache` entries omitted
`system/fvSchemes`; checkMesh fatal-errored, produced no cell count, and the
parser reported `clean` — because it looks for error *patterns* and a log with no
patterns has none. **The only thing standing between that and a false clean
certificate is `write_certificate`'s refusal when `cells` is `None`.** That guard
is load-bearing and was doing invisible work. The re-check harness therefore
treats *"did checkMesh actually run"* as a separate condition from *"do the
verdicts agree"*, and reports `checkMesh_did_not_run` as its own column — it came
back 0, but it could not have been read off the verdict. **`sdk/chief_engineer/mesh_certificate.py`
is the Infra family's file; this is reported, not patched.**

**2. My own three exonerated certificates carried a FALSE provenance.**
`write_certificate` defaults to `provenance: "at-creation"`, and I did not
override it — so the three `w1-bump-nasa-grids` certificates (and the
`study-motorBike-f8b4a2` one minted earlier today) claimed to have been written
when the mesh was made. **They were not: the verdict comes from a re-run on
2026-08-10.** Corrected to `fresh-recheck-of-existing-mesh`, with the reason on
each certificate's face.

Neither existing constant is honest for this case — `at-creation` is false, and
`retrospective-from-archived-log` is false too because the verdict came from a
fresh run rather than a stored log. **A third constant belongs in the module, and
that is Infra's file to change**; the string is accurate in the meantime and
nothing in the codebase branches on the value.

## What is established, and what is not

**Established:** of 95 retrospective certificates, **95 agree with a fresh
`checkMesh` and all 95 points hashes match.** Of the 7 refused rows routed here,
**4 are wrong and 3 are right and now certified.**

**Not established:** anything about the ~73 audit rows outside the 105, the three
refusals belonging to another family, or any mesh not on this box. **No corpus
`BORN BROKEN: N` is restated here** — the frame is 95 certificates plus 7 rows,
and a corpus figure from that frame would be the error this family has now
corrected in its own work twice today.
