# DRAFT — DATED AMENDMENT FOR `CRM_WINGALONE_PREREGISTRATION.md`

**UNSIGNED. Drafted by lab-lane at cfd-supervisor's instruction; the freeze block is signed
personally by the supervisor and this lane does not sign it.** The text below is what would be
**APPENDED AT THE FOOT** of the frozen file. **No line above it is touched (rule 6)** — proof of that
is in `S12_AMENDMENT_PROOF.md`, computed by construction, not asserted.

🔴 **FIRST COMPUTE HAS NOW OCCURRED** (`verification/runs/CRM_WINGALONE_runs/`, three levels built
and graded). **Rule 2 has therefore CLOSED this document's gates.** What follows is a **dated
addendum**, and it **alters no gate, no threshold, no cap and no label** — that is asserted item by
item below, not in general.

---

## ── TEXT TO APPEND BEGINS ──

---

## 13. AMENDMENT 1 — 2026-09-11, POST-COMPUTE. **Establishes version 1.1.**

*(This document carried **no version field** when frozen. This addendum does not "bump" one — it
**establishes** the field, with the frozen original designated **v1.0** and this amended state
**v1.1**. Stated rather than glossed, because a bumped version and an invented one are not the
same claim.)*

**lines whose number changed above this section: 0** — **PROVED, NOT ASSERTED.** The first
**37,613 bytes** of this file (its complete v1.0 content, 595 lines) hash under `git hash-object` to
**`1fa5fb725e6298d99dc4ab2207f55f11e575b285`**, which is byte-identical to the blob committed at
**`d2629d326`**. Every line of §1–§12.2 therefore holds its original number.

### 13.1 §12's HEADING CONTRADICTS THE BLOCK BENEATH IT. **The heading is NOT edited.**

§12 reads **"FREEZE BLOCK — BLANK"** while the table beneath it is **filled**, dated
**2026-09-11T18:51:47Z**, and carries §12.2's check 4 signed by the supervisor personally. **The
block is filled and committed; the heading is stale.**

**Rule 6 forbids editing it**, and other records cite this file by line, so the heading stays exactly
as written and **this addendum is the correction of record**:

> **§12's heading word "BLANK" is superseded. THE FREEZE BLOCK IS FILLED, SIGNED AND COMMITTED
> (`d2629d326`), and compute was legally launched under it.**

🔴 **This is the defect class of the day, committed into a frozen file with a signature on it:
the fix landed where the *instrument* reads the value — the block was filled — and the stale claim
survived where a *human* reads it, in the heading.** Recorded here in those terms because the
pattern, not the word, is the finding.

**Alters no gate, threshold, cap or label:** it changes a heading's meaning only, and §10's gate
table is untouched.

### 13.2 §6 AND §7 MISIDENTIFY THE PROBE'S SURFACE. Both anchors are 4.00× high, both SAFE.

*(Offered as a second item; the supervisor may strike it and keep 13.1 alone. It is included because
leaving it unaddendumed reproduces 13.1's own defect — a known-false statement surviving where the
next reader reads it.)*

§7 states the `59dfc5232` probe *"ran at `N` 53 on the **`A6`** surface (579,072 cells)"*. **It ran on
`ACT9` — L3's surface — at 44,544 faces**, identified two independent ways: the probe's
`work/surfMesh.cgns` is **md5-identical** to `ACT9_CRM_surfMesh.cgns`, and the probe's own log header
prints **`Total Nodes 46762 / Unique Nodes 44681 / Total Faces 44544`**, matching `ACT9`'s census
exactly and matching `A6`'s (12,258 / 11,205 / 11,136) not at all. It marched **2,316,288** cells.

`44,544 / 11,136 = 4`, so **both** §6 anchors are high by exactly **4.00×**:

| §6 anchor | as registered | **measured** |
|---|---|---|
| extrusion rate | 12.952 core-min/Mcell | **3.246** |
| Plot3D disk rate | 282.5 bytes/cell | **70.62** |

**Alters no gate, threshold, cap or label. The registered cap of 1,464 core-min STANDS UNCHANGED**
and is merely more conservative than it read; the §6.1 disk precondition likewise. **Both errors are
over-estimates, so nothing this document gated was ever loosened.** Actual spend was **20.0
core-min, 1.37 % of cap**.

🔴 **The consequence that is not bookkeeping:** §7 registered the risk as *"`N` 105 and 209 are
untested regimes"*, reasoning from a probe believed to sit near L1. **Corrected, the probe sat on
L3's surface, and L1's 2,784-cell surface had never been marched by anything.** **The measured
failure landed on L1** (G-M4, min quality −0.05046 at layer 3). **§7's conclusion — "the probe's
exact configuration has never been run" — was correct and load-bearing; its premise pointed the
registered risk at the wrong end of the ladder.**

### 13.3 WHAT THIS AMENDMENT DOES NOT DO

- **It does not alter §10.** G-M1..G-M5, their thresholds and their breach verdicts are exactly as
  frozen, and the ladder was graded against them as frozen.
- **It does not rescue L1.** L1 is `GATE FAIL` on G-M4 and `BLOCKED` per §10's own verdict column.
- **It does not register `s0` or `pGridRatio`.** Both are build parameters chosen by the building
  lane and disclosed in `verification/runs/CRM_WINGALONE_runs/BUILD_PARAMETERS.md` and
  `PGRIDRATIO_FINDING.md`. **Neither is a registered quantity and this addendum does not make one.**
- **It makes no flow claim.** §10A's successor still owns every O1–O5 decision.

| field | value |
|---|---|
| amended by | *(UNSIGNED — cfd-supervisor to sign; drafted by lab-lane)* |
| date | 2026-09-11 |
| version | **v1.0 → v1.1** |
| lines whose number changed above this section | **0, proved by hash** |
| gates/thresholds/caps/labels altered | **NONE** |

---

## ── TEXT TO APPEND ENDS ──
