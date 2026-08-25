# Certonomous Run-Log Standard

**Version 1.0, 2026-08-25.** Adopted by the cfd supervisor and offered lab-wide under Sanaa's
desk-item disposal rule of 2026-08-25: referred with recommendation and reasoning, **ADOPTED unless
she rules otherwise within one day**, recorded `[lab-attributed]`. **Overrulable.**

This standard governs **what happens to a solver log after the run**. It changes no gate, no
threshold, no cap and no label, and it does not touch how a number is read — that is
`MONITOR_STANDARD.md`, and rule **S17** in particular.

---

## 1. THE RULE, in four clauses

> 1. **EXTRACT THE SERIES.** Before anything is compressed, the residual series — and any other
>    per-iteration quantity a record will cite — is extracted into a **small, citable artifact**
>    (`.csv` or `.jsonl`) that lives beside the run and is **committed**.
> 2. **THEN gzip the raw log.** The raw solver log is compressed in place. It is evidence and is
>    never deleted.
> 3. **NEVER gzip anything a gate reads, or anything a frozen document names by path.** No
>    exceptions, no "it still decompresses". See §3 — this clause is the one that has teeth.
> 4. **DO NOT REWRITE WHAT IS COMMITTED.** A committed log is history. If it is wrong, the
>    correction is a new artifact beside it that says so.

## 2. WHY CLAUSE 1 COMES FIRST, and why the order is not cosmetic

A gzipped log is *technically* readable and *practically* unread. Every downstream consumer — a
grader, a sweep, a `grep` across the campaign, a future agent reconstructing a verdict — either
grows a decompression path or silently skips it. **`grep -r` in this repository does not read
gzip**, and this lab has already measured what a sweep that cannot see a file does: it returns a
confident zero (L-186's neighbours; the planted-zero rule, standing rule 3, exists for exactly this).

So the extracted series is not a convenience copy. **It is the artifact the lab will actually cite**,
and the raw log becomes what it should always have been: the primary evidence you go back to when
the citation is challenged. Compressing before extracting inverts that, and the inversion is
invisible until somebody needs the number.

## 3. CLAUSE 3 IS THE ONE THAT HAS TEETH

Two categories are **absolutely excluded** from compression:

**(a) Anything a gate reads.** A comparator that opens a path and finds `path.gz` does not degrade
gracefully — it either errors (good) or reads nothing and reports a zero (catastrophic). Under
standing rule 3 a zero from a reader not shown able to see a non-zero **is not evidence**, and a
comparator whose input was compressed out from under it produces exactly that zero. **Compressing a
gate's input is a way to fabricate a passing control without touching the control.**

**(b) Anything a frozen document names by path.** Standing rule 2 fixes the grading path at the
pre-registration commit, and standing rule 6 forbids editing a frozen file. A frozen document that
names `log.rhoSimpleFoam` **cannot be amended to say `log.rhoSimpleFoam.gz`** — the amendment would
be legal only as a dated addendum, and an addendum may not alter what the gate reads. **So
compressing that file does not create a paperwork problem. It creates an unrepairable one:** the
frozen document now names a path that does not exist, and the only lawful fix is to put the file
back.

**Before compressing any log, the compressor must establish that no frozen document and no
comparator names it.** Search the campaign and case trees for the basename. If that search cannot
be shown able to find a planted reference, it has not been performed.

## 4. WHAT COUNTS AS A SMALL CITABLE ARTIFACT

- **Per-iteration, machine-readable, and self-describing.** Column names or JSON keys, units, and
  the field each series belongs to.
- **The solve position stated**, per `MONITOR_STANDARD.md` S17. A residual series extracted from a
  field solved more than once per outer iteration must say whether it carries the **first** solve
  (what the solver's own criterion reads) or the last. **A residual series without its solve
  position is incomplete and may not be cited.**
- **Windowed summaries beside the raw series, never instead of it.** A floor, a rise ratio or a
  median-of-window is a derived claim; the series it came from must be present so the derivation
  can be checked.
- **Small enough to commit.** If it is not, the run is emitting a summary problem, not a storage
  problem — say so rather than compressing your way out of it.

## 5. WHAT THIS STANDARD DOES NOT DO

It does not authorise deleting any log, ever. It does not permit editing a committed artifact. It
does not change what a monitor may read or what a gate may require. It is **not retroactive**: logs
already compressed are not un-compressed by this document, but **if one of them is named by a
frozen document or read by a gate, restoring it is mandatory and immediate** — that is clause 3
operating, not a retroactive application of clause 2.

## 6. Provenance

The four clauses are cfd's interim log policy, carried through the F3, F5b, F11 and F12 campaigns
of 2026-08-25 and generalised here. Clause 3's second limb was written after this team measured the
shared index staging a frozen pre-registration **2,773 lines short**, which sharpened a standing
lesson: **the documents a gate depends on are exactly the documents most easily broken by routine
hygiene.** Compression is routine hygiene. That is what makes it dangerous here.
