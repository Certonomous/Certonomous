# VR10 — PAPER SIDECAR FIDELITY

**Repair-registration. Frozen before any work under it. Written 2026-08-31.**

## 1. The finding this measures

`CLAUDE.md`'s filing table requires each paper to be
`docs/papers/<topic>/author_year_identifier.pdf` **plus a matching `.txt` sidecar**.

The sidecar is not decoration: **it is the only thing a text sweep can see.** A team asking *"do we
already hold a reference for X"* greps the sidecars. A PDF with no sidecar is **invisible** to that
question, and a *"no"* over it is a **false negative**, not an answer.

**Standing rule 15 is the sharper half:** *"Title-page verification of every retrieved paper
(L-144). Never by file type, filename or hash — a manifest can be internally consistent and
externally false."* **A sidecar that exists but belongs to a different document passes every
presence check and satisfies rule 15 not at all.** So this item gates on **agreement**, not
existence.

## 2. WHAT IS MINE, AND WHAT IS EXPLICITLY NOT

The **measurement** is mine. The papers sit in six teams' topic folders and **extracting a missing
sidecar is the owning team's act.** This item extracts nothing into the repository.

### 2a. ⚠ THE 34 % GAP IS ON SANAA'S DESK. THIS ITEM DOES NOT RULE ON IT.

The sidecar gap is already a **referred item on Sanaa's desk**. This item does **not** rule on it,
propose a remedy, or re-open the referral. **It measures**, and it exists because **the record and
the disk disagree**: the 2026-08-30 board entry records the gap as *"closed by extracting"*, and
the disk on 2026-08-31 still shows **48** PDFs with no sidecar. **A discrepancy between the record
and the disk is verification's own business whatever else is referred.**

### 2b. Rule-2 condition, and how it was checked

No compute has been spent under this document. The run artefacts —
`STATUS.VR10_PAPER_SIDECAR_FIDELITY` and `launcher.queue.out` under the registered cwd
`/home/ubuntu/Certonomous/verification/runs/verification/VR10_PAPER_SIDECAR_FIDELITY/` — **do not
exist**, checked by direct `ls` before this file was written.

### 2c. Disclosed: the driver was DRIVEN before enqueue, and ITS COMPARATOR WAS WRONG FIRST

`verification/credibility/vr10_paper_sidecar_fidelity.py` was driven with `--selftest`: **7 cases,
0 failures, rc 0**. It reached that state by **failing on its own discrimination limb**, and the
failure is disclosed because it decided the gate's shape:

**The first comparator scored the fraction of page-1 CONTENT TOKENS present in the sidecar.**
Driven on real bytes it scored **0.985 for a faithful pairing** and **0.481 FOR A DELIBERATELY
WRONG ONE.** Two unrelated CFD papers share half their vocabulary, **because that is what a shared
field is.** A comparator that cannot separate 0.985 from 0.481 **cannot verify a title page**, and
rule 15 is not met by a number that high for a document the sidecar does not belong to.

**The repair is structural, not a tuned threshold.** A faithful sidecar is an *extraction* of the
PDF, so its opening reproduces page 1 **nearly verbatim**. The comparator now matches **8-word
verbatim phrases**: unrelated papers in the same field share vocabulary but **essentially never
share long exact phrases.** Re-driven on the same real bytes — and on a **hard** pairing, two
papers by *the same authors* — it scores **faithful 0.859 vs wrong 0.094, a separation of 0.765**
across a 0.30 threshold. **Limb X3 asserts that separation rather than assuming it**, so a future
corpus in which the threshold stopped discriminating would fail the control rather than pass the
gate.

## 3. Gate (frozen)

A committed driver that:

- **G1** enumerates every PDF under `docs/papers/`.
- **G2** classifies each **MISSING** (no sidecar), **STUB** (< 200 bytes — the corpus holds a real
  77-byte specimen, which is what makes the threshold demonstrable rather than arbitrary),
  **MISMATCH** (sidecar disagrees with the PDF's own page 1), **UNREADABLE**, or **OK**.
- **G3** obtains page-1 text with **`pdftotext`, the real production extractor**, invoked exactly
  as an extraction pass invokes it — not a re-implementation and not a fixture.
- **G4** controls, both limbs, **on real bytes** (§2j): the reader must be shown seeing a real
  MISSING, a real STUB, and a real faithful sidecar reading OK; **and** a real PDF's page 1
  cross-paired against a **different real paper's** sidecar must **DISAGREE with clear
  separation**.
- **G5** **REFUSES (exit 2)** when the extractor is absent or `docs/papers` is unreadable. A PDF
  the extractor cannot read is **REPORTED AND NOT GATED** — *"I cannot read it"* is not *"it is
  wrong."*

## 4. Threshold / label

- **PASS** = every paper carries a sidecar that agrees with its own first page.
- **GATE FAIL** = any paper is MISSING, STUB or MISMATCH.
- **NOT A RESULT** = a control limb misbehaves, including X3's separation collapsing.
- **BLOCKED** = no extractor, or `docs/papers` unreadable.

Only `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` may be emitted.

## 5. PREDICTED OUTCOME — stated as a prediction, before the run

**I predict GATE FAIL.** Measured during drafting and disclosed under §2c: **144** PDFs, of which
**48** have no sidecar and **1** has a 77-byte stub — **49 already failing on presence alone,
before a single agreement check.**

**I make NO prediction about the MISMATCH count**, which is the part of this gate that has never
been measured on the full corpus. That number is the item's actual news, and it may be zero.

## 6. Cap and cost

**Registered estimate: 0.2 core-minutes. Cap: 2.0 core-minutes.**

The one expensive operation is page-1 extraction, and it was **measured, not guessed**, on the
contended box:

```
pdftotext page-1, sampled over 8 real PDFs   : 0.183 s / 8       = 0.0229 s per PDF
projected full pass over the 144-PDF corpus  : 0.0229 x 144      = 3.3 s wall
                                               3.3 s x 1 rank / 60 = 0.055 core-min
registered estimate, ~3.3x for heavier
  contention (VR6's measured busy/quiet tax) :  12 s wall x 1 rank / 60 = 0.2 core-min
cap, ~10x the registered estimate            : 120 s wall x 1 rank / 60 = 2.0 core-min
```

**Costed on the CONTENDED box:** load average 7.8–15.0 over 16 cores at measurement; the box was at
**28.5** earlier the same day, which is why the registered estimate carries the 3.3× tax rather
than the raw sample.

Dollars **DERIVED, NOT MEASURED** at $0.0513/core-h, itself **reported-by-owner**
(`COMPUTE_BUDGET_CHARTER` §5):

```
estimate : 0.2 core-min / 60 x $0.0513 = $0.000171   DERIVED-NOT-MEASURED
cap      : 2.0 core-min / 60 x $0.0513 = $0.00171    DERIVED-NOT-MEASURED
```

**Zero solver compute.** An overrun **stops the run** (rule 12).

## 7. Not claimed

No sidecar is written, no PDF is re-fetched, and **the referred 34 % item is not ruled on.** No
verdict is withdrawn: a missing sidecar is a defect in the **library's visibility**, never in any
result that cited the paper. A paper the extractor cannot read is reported, never graded.
