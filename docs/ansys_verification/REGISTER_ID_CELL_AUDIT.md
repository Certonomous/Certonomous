# REGISTER ID-CELL AUDIT — before row `#52` is written

**Team:** ansys-verification. **Date:** 2026-08-31. **Zero compute.**
**Subject file:** `/home/ubuntu/Certonomous/verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`

> **THE ANSWER TO THE QUESTION THAT PROMPTED THIS: ONE namespace, rows `1..51`, COMPLETE — no gaps, no
> duplicates. THE NEXT ROW ID IS `**#52**`, in hash format.**
>
> **AND THE REASON THE AUDIT WAS WORTH DOING IS THE SECOND FINDING, NOT THE FIRST: six `**#N**` cells in this
> file are NOT row ids at all, and the obvious extraction regex therefore reads the register as 57 rows with a
> maximum of 43.**

---

## 1 — The namespace

There is **one** register namespace and it is **complete**: rows **1 through 51**, every integer present
exactly once. No gaps. No duplicates.

## 2 — Two id-CELL formats, and there is no third

The row-id column uses two literal spellings, and the format switched **at row 44**:

| rows | id-cell format | example | first/last line |
|---|---|---|---|
| 1–43 | **bare** `**N**` | `**43**` | ends at line 662 |
| 44–51 | **hash** `**#N**` | `**#44**` | begins at line 725 |

**"Hash format" in commit `08818770` means the literal `#` prefix on the number, and nothing whatever to do
with a commit hash.** This is worth saying because the word invites the wrong reading in a file whose other
citations *are* commit shas.

**NEXT ROW ID: `**#52**`, hash format.**

---

## 3 — THE FINDING: six `**#N**` cells are citations, not ids

Six cells in this file match the id-cell shape and are **not** row ids. They are **citations of existing rows,
inside dated addenda**, in tables whose first column happens to hold a row reference:

| lines | cells | addendum heading they sit under | rows actually cited |
|---|---|---|---|
| 193–196 | `#1`, `#2`, `#3`, `#4` | line 160 — *"Dated addendum — 2026-08-25 — TIER back-filled onto rows #1–#4"* | 1, 2, 3, 4 |
| 716–717 | `#42`, `#43` | line 691 — the 2026-08-28 planted-control re-grade | 42, 43 |

The addenda are **legal and correctly written**. Nothing about them is a defect. The defect is that their
citation style is byte-identical to an id cell.

### The consequence, stated as a number

The obvious id-extraction regex over this file returns **57 cells for 51 rows** — a false count of 57, a
**false maximum of 43**, and **apparent duplicates that are not duplicates** (`#1`–`#4` against rows 1–4,
`#42`/`#43` against rows 42/43).

> **THE FILE'S ID COLUMN IS NOT MACHINE-EXTRACTABLE BY THE OBVIOUS PATTERN.**

---

## 4 — This is not hypothetical. The hazard fired on this team's own lane, tonight.

**A haiku lane ran exactly that regex tonight and reported the register as "57 rows, maximum id 43, no
duplicates across formats."** That report was **wrong on the count** (57, not 51), **wrong on the maximum**
(43, not 51), and **wrong on the duplicates** (it asserted none across formats; there are six apparent ones).
**It missed `#42` and `#43` entirely.**

**Stated without softening, because softening it would destroy the only real evidence here:** the audit found
its hazard by the hazard firing on this team's own lane. That is the most direct evidence available, and it is
**worth more than the clean answer would have been.** Had the extraction happened to come out right, this
document would record a tidy `1..51` and would not have found the thing that matters.

The failure mode is the dangerous shape: it does not error, it does not warn, and it returns a plausible
number. A lane asking "what is the next row id?" gets **44** instead of **52** and writes a duplicate into a
credential file.

---

## 5 — Recommendation — a RECOMMENDATION, not a ruling, and NOT APPLIED

Either of these would close it; neither is done here and neither is decided here:

1. **Anchor any future id extraction on the register's own row table and exclude addendum tables** — by
   section boundary, not by cell shape; or
2. **Change the addendum citation style** to something that cannot be mistaken for an id cell (an inline
   `row 42` reference rather than a leading `| **#42** |` cell).

**Changing the register's existing bytes is NOT proposed.** The register is **append-only** and the addenda
are legal as written. Option 2, if ever taken, applies to *future* addenda only.

---

**Verified by re-measurement, not relayed:** the 57 id-shaped cells and their line numbers, the format switch
at row 44 (line 662 → line 725), the completeness of `1..51`, and both addendum headings at lines 160 and 691
were read from the file itself and agree with the supervisor's measurements in every particular.
