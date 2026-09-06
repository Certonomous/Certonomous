# Paper acquisition — the two primaries this team is blocked on, with their **content verification criteria fixed BEFORE arrival**

**Written 2026-09-06 by `heat-transfer-supervisor`.** Retrieval approved by Sanaa
(capture `b7c56371`, *"everything approved"*).

**WHY THE CRITERIA ARE WRITTEN FIRST.** `L-144`: a retrieved paper is verified by its **title page
and content**, never by file type, filename or hash — *a manifest can be internally consistent and
externally false.* The lab has been burned **twice this week** by right-author-right-year-**wrong-
paper**. **Criteria written after a PDF arrives are rationalisation; criteria written before it are
a test.** These are drawn from the citing registrations' own descriptions of what the blocked rows
compare against, and **an arriving file that fails them is REJECTED however well its metadata
matches.**

**SUBMISSIONS PARKED is untouched by this file.** Acquisition is **inbound**. Nothing here sends,
files, posts or contacts anyone, and rule 7 is unaffected.

---

## 1. VOGEL & EATON 1985 — blocks **G1, G3, G4** of the T3 ladder

**Citation, from `T3_PREREGISTRATION.md` §2 verbatim:** Vogel, J. C. and Eaton, J. K. (1985),
*Combined Heat Transfer and Fluid Dynamic Measurements Downstream of a Backward-Facing Step*,
**ASME J. Heat Transfer 107(4), 922–929, DOI 10.1115/1.3247522**.

**Equally acceptable companion:** Vogel and Eaton, **Stanford Thermosciences Division Report MD-44**
(August 1984, 191 pp., NSF grant MEA-81-08189).

### 1.1 CONTENT CRITERIA — ALL THREE MUST HOLD, AND METADATA ALONE SATISFIES NONE

1. **It must contain `St(x/H)` data for a HEATED backward-facing step** — the Stanton-number
   distribution downstream of the step, **as a table or a figure**. *This is the single criterion
   that the near-misses fail: the ERCOFTAC backward-facing-step cases (031 Driver & Seegmiller,
   053 Makiola & Ruck, 056 Tsai & Yang, and Le & Moin's DNS) are **UNHEATED** and therefore carry
   no Stanton data at all.* **A backward-facing-step paper by the right authors that reports only
   velocity or skin friction is the WRONG PAPER for these rows.**
2. **It must state the authors' own measurement uncertainty.** The registration requires it because
   the comparison bands depend on it. **A copy that omits it is incomplete, not merely inconvenient.**
3. **Conditions must match:** air, single-sided step, **`Re_H` ≈ 28,000** on the step height and the
   core velocity at `x = −3.3 H`, with `St` and `C_f` defined on that core velocity and the inlet
   temperature.

**Corroborating figures already held in a SECONDARY source**, usable as a cross-check on arrival:
the UKHTC 2021 P-2-1 paper (Jardine, Iacovides, Craft, Cioncolini) plots the Vogel & Eaton `St` and
`C_f` symbols against `x/H` from **0 to 20** in its Figure 9, and attributes **`x_R/H = 6.67`** to
them. **An arriving primary whose `St(x/H)` curve disagrees in shape or magnitude with that
secondary's Figure 9 is the wrong paper and must be rejected**, not reconciled.

> ⚠ **AND A NUMBER THAT IS NOT A CRITERION.** `H = 0.038 m` is **a scale choice of this lab's
> design**, explicitly *"not from any held source"* (`T3_PREREGISTRATION.md`). **Do NOT verify an
> arriving paper against 38 mm** — finding that number would be a coincidence, and not finding it
> is not a rejection.

### 1.2 ROUTES ALREADY EXHAUSTED — DO NOT REPEAT THEM

Documented in `T3_PREREGISTRATION.md` §2: **ERCOFTAC** (49 BFS records, none heated, Vogel & Eaton
not held) · **NASA NTRS API** (no Vogel, no Eaton, no heated step — the MD series was **NSF**-funded,
not NASA) · **Stanford SearchWorks** (MD-44 is a **physical holding at SAL3, no PURL, no digital
copy**) · **OSTI** (1983 conference abstract only) · **DTIC** (bot-walled) · **CORE**, **Google**.

### 1.3 THE ROUTES THAT COULD STILL WORK — AND THEY REQUIRE SANAA, NOT COMPUTE

- **ASME Digital Collection**, DOI `10.1115/1.3247522` — **paywalled**; needs a subscription or a
  single-article purchase.
- **Interlibrary loan / scan request for MD-44** at Stanford SAL3 — it exists physically and is
  191 pp.
- **A university library proxy** with ASME JHT 1985 holdings.

**All three are acquisitions from outside the box. None is a search this box can complete, and
approval does not change that.**

---

## 2. BLAY, MERGUI & NICULAE 1992 — blocks all ten graded rows of **K0d**

**Attribution as the citing records carry it:** Blay / Mergui / Niculae (1992), the confined
mixed-convection cavity experiment with a horizontal buoyant wall jet (ASME HTD volume,
*Fundamentals of Mixed Convection*). `K0d_PREFLIGHT_EXECUTABILITY_FINDING.md`: **all ten graded rows
`BLOCKED`, zero core-seconds spent.**

### 2.1 CONTENT CRITERIA

1. **It must contain the confined-cavity mixed-convection measurements with a horizontal buoyant
   wall jet** — the velocity and temperature profiles K0d's rows compare against, **as tables or
   figures**.
2. **The cavity geometry and boundary conditions must be stated numerically** — dimensions, jet
   inlet conditions, wall temperatures — since K0d's case is built from them.
3. **Air, confined cavity.** *A Blay paper on a different configuration is the wrong paper.*

**⚠ THE CITING RECORD ITSELF FLAGS THE NEAR-MISS RISK:** it records searches returning
*"Blay 1992 and none of them the primary."* **Author-and-year matching has already produced false
hits for this exact reference. Criterion 1 is the discriminator; metadata is not.**

### 2.2 ROUTE

ASME HTD conference volumes are **not open-access**; acquisition is a purchase or a library holding.
A prior record states plainly that obtaining Blay 1992 **"is from OUTSIDE THE BOX, is Sanaa's
alone."**

---

## 3. THE VERIFICATION PROTOCOL TO RUN ON ARRIVAL — L-144, IN ORDER

1. **Read the title page** and record author list, exact title, journal/report, volume, pages, year
   **as they appear on the document**, not as the filename claims.
2. **Locate the content criterion** (§1.1.1 / §2.1.1) **inside the document** and record the page or
   figure number where it appears. **This step is the test. If it cannot be located, the paper is
   REJECTED regardless of a matching title page** — that is exactly the failure mode that burned the
   lab twice this week.
3. **Cross-check against the held secondary** where one exists (§1.1, Figure 9). **A disagreement is
   a rejection, not a reconciliation.**
4. **Generate the `.txt` sidecar** — `pdftotext <file.pdf> <file.txt>` — per `FILING_CHARTER`;
   a PDF without a sidecar is invisible to every text sweep of the library.
5. **File** as `docs/papers/<topic>/author_year_identifier.{pdf,txt}`; run
   `scripts/check_filing.py`.
6. **Record the verification** — what was read, on which page, and against which criterion — so a
   successor can audit the acceptance and not merely inherit it.

**Only after step 6 do the blocked rows unblock**, and the unblocking is a **separate graded act**:
the T3 ladder's `G1`, `G3`, `G4` are re-run through the frozen `analyse_t3g.py` against the arrived
primary, under a registration that must state the comparison bands **before** the numbers are seen.
**The grid triple is already measured and frozen (`gate_t3g.json`); the reference is the only
missing operand.** ⚠ **That ordering matters: the triple values are ALREADY KNOWN, so any band
registered after this date must be justified from the paper's own stated uncertainty and NOT from
the values it will be compared against.**

---

## 4. RETRIEVAL ATTEMPTED 2026-09-06 UNDER SANAA'S APPROVAL — OUTCOME

**Neither primary is openly available. Approval removed the permission barrier; it did not remove
the access barrier, and that distinction is the finding.**

### 4.1 ONE REAL GAIN — BLAY's CITATION IS NOW PRECISE

The citing records carried only *"Blay 1992"* and *"Blay / Mergui / Niculae"*. **Now resolved:**

> **Blay, D., Mergui, S., Niculae, C. (1992), *Confined turbulent mixed convection in the presence
> of a horizontal buoyant wall jet*, in *Fundamentals of Mixed Convection*, ASME **HTD Vol. 213,
> pp. 65–72**, ASME Winter Annual Meeting, Anaheim, California.**

**That is an acquisition-grade citation where before there was an author-and-year**, and it is
exactly the specificity that defeats the near-miss risk §2.1 flags. **Volume and page range are now
verifiable on the title page of anything that arrives.**

### 4.2 VOGEL & EATON — CONFIRMED, NOT OBTAINED

The 1985 journal article is confirmed at **ASME JHT 107(4), 922–929, DOI 10.1115/1.3247522** and is
indexed (a Semantic Scholar record exists). **No open-access full text was found.** **MD-44 was not
locatable online at all** — consistent with `T3_PREREGISTRATION.md` §2's finding that it is a
physical holding at Stanford SAL3 with no digital copy. A related Stanford Thermosciences report,
**MD-43** (Adams, Johnston & Eaton, 1984, *Experiments on the structure of turbulent reattaching
flow*), surfaced instead — **it is a DIFFERENT report and is NOT a substitute: it is the unheated
structural study, and criterion §1.1.1 rejects it for carrying no Stanton data.**

### 4.3 ⚠ A ROUTE FOUND AND DELIBERATELY NOT TAKEN

Search results included **a document-sharing-site upload of the entire *J. Heat Transfer* 1985
Vol. 107 No. 4 issue.** **It was not fetched and no link to it is recorded as an acquisition route.**

> **FINDABLE IS NOT LAWFULLY ACQUIRABLE.** A copyrighted ASME journal issue re-uploaded to a
> document-sharing site is not a licensed copy, and taking it would substitute an infringing source
> for an absent one. **The lab's problem is that it does not hold this paper; it is not that it
> cannot locate a file.** Recorded explicitly so that a successor running the same search sees the
> hit, sees that it was considered, and sees why it was refused — rather than rediscovering it and
> assuming nobody looked.

### 4.4 OPEN SECONDARIES THAT USE BLAY 1992 AS A VALIDATION CASE

Several openly-available modelling papers use the Blay cavity as a validation case and reproduce its
profiles. **They are recorded here as CROSS-CHECK material for step 3 of §3's protocol** — the same
role UKHTC 2021 Figure 9 plays for Vogel & Eaton.

⚠ **Whether any of them may serve as a SECONDARY REFERENT in its own right is a REGISTRATION
decision and is NOT taken here.** T3 did exactly that with its secondary and handled it under a
declared secondary-referent rule; K0d has taken no such decision, and **a referent adopted casually
in an acquisition note would be a gate change made in the wrong document.**

### 4.5 WHAT WOULD ACTUALLY UNBLOCK EACH — FOR SANAA, BECAUSE ONLY SHE CAN DO THESE

| paper | route | what it needs |
|---|---|---|
| **Vogel & Eaton 1985** | ASME Digital Collection, DOI `10.1115/1.3247522` | subscription or single-article purchase |
| **Vogel & Eaton MD-44** | Stanford SAL3 interlibrary loan / scan request | a request placed from outside the box |
| **Blay et al. 1992** | ASME HTD Vol. 213, pp. 65–72 | purchase or a library holding of the 1992 WAM volume |

**None is a search this box can complete.** The blocked rows stay blocked, honestly, with the
missing capability named — and it is a **paper**, not a solver, so under Sanaa's 2026-09-04 order
**neither case is in the OpenFOAM-exemption class.**
