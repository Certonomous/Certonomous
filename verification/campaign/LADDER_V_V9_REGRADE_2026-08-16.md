# Ladder V — V9 re-graded by a non-author: the verdict holds, the certification that reached it did not

**Verdict: `PASS`.** All three of V9's declared clauses were met and were verified here by execution,
and the struck prior-art sentence is genuinely absent from the shipping archive — established with a
recogniser validated on eight paraphrases and an in-archive positive control that fired.

**But the certification of record was not earned, and the exposure the dispatch named is real.** It
swept 90 archive members for **two literal substrings**, got zero, and cleared a positive control on
the token `Closure`. `Closure` is unrelated to the prior-art claim: it proved the sweep could *open*
the files. **Absence of two literals was measured; absence of a claim was concluded.** Two
independent measurements below show that gap is not theoretical — and **a live instance of the exact
misattribution is standing unstruck in a tracked file**, in a paraphrase one inflected word away from
the fragments that were searched for.

**Independence.** This grader wrote none of `CLOSURE_CHALLENGE_PRIOR_ART.md`, none of the
`d84b649f` correction, none of the archive rebuild, and none of the certification recorded in
`campaign/LADDER_V_D227_ENTITLEMENT_2026-08-16.md` §8. Independence rests on the untracked dispatch
record, not git authorship (D130).

---

## 1. V9's declared scope, stated before anything was touched

`LADDER_V_TRIPLE_VERIFICATION.md:382-385`:

> **V9. Prior-art completeness**: the §7.4 split carried verbatim into the description (identify
> vs control papers correctly separated); the Buchanan-coefficients firewall stated as a
> compliance fact; a final check that nothing in the entry's history warm-started from, calibrated
> against, or compared during development to that model's hump behavior.

**Three clauses, and the claim class is not the two fragments.** Derived from the 2026-08-05
correction `d84b649f` that created the rung: the defect is **crediting papers that only IDENTIFY or
CLASSIFY** — Ling & Templeton (2015), Wu, Wang, Xiao & Ling (2017) — **with a mechanism that CONTROLS
or GATES where a data-driven correction is allowed to act**, which only the CONTROL papers, Steiner
et al. (2022) and Buchanan et al. (2025), reported. The two fragments are one wording of that claim.
They are not the claim.

The ledger also records V9 as **already flipped once** — the prior finding *"wrong for five days"*,
in the direction that made the lab look worse. A rung wrong in both directions earns a recogniser
that survives paraphrase.

---

## 2. The recognition control, with readbacks

Eight variants of the claim, written in the claim's **own vocabulary**, each printed back before the
run, plus a struck negative control.

| variant | recognised |
|---|---|
| V1 verbatim (the struck sentence) | yes |
| V2 inflected — *controlled where … was allowed to act* | yes |
| V3 **wrapped across two line breaks mid-phrase** | yes |
| V4 reordered passive — *where … is allowed to act is controlled by* | yes |
| V5 synonym — *gates where … may apply* | yes |
| V6 synonym — *decides which cells the correction fires in* | yes |
| V7 synonym — *determines whether the closure may intervene* | yes |
| V8 hyphenation/casing drift — *CONTROLS WHERE a Data-Driven Correction…* | yes |
| **negative control**, the same sentence inside `~~ ~~` | **silent, correct** |

**8 of 8 positive, 0 of 1 negative.** Readback of V3, the wrap case, exactly as planted:

```
L1: 'A classifier that reads only the uncorrected solve and controls where a'
L2: 'data-driven correction is allowed'
L3: 'to act has been published repeatedly - Ling and Templeton 2015.'
```

**The control caught a real defect in my own recogniser before the run, which is the only reason its
zeros are worth anything.** The first pass scored **7 of 8** — V4 failed. The cause was that the word
gaps were written `(?:\w+\s+){0,N}`, and **`\w` does not match a hyphen**, so `data-driven` broke
every gap it sat in. The mechanism detector had therefore been silently failing on the *actual target
phrasing* and only the *"published repeatedly"* co-occurrence was rescuing V1–V3. Widened to
`(?:\S+\s+){0,N}`, all eight fire. **A recogniser that cannot find a paraphrase the grader wrote
himself cannot certify absence — and this one could not, until it was made to.**

**In-archive control.** The wrapped variant was planted into a real archive member
(`certonomous-demo/START-HERE.md`): unplanted **0 hits**, planted **2 hits**, gain **+2**. The control
fired *inside the archive*, so the archive zeros below are measurements.

---

## 3. The travelling arm: 90 members, swept for the class

`dist/certonomous-demo.zip`, sha256 `34b8feed8301d91a8aa36d506326c89d74cf4b8ac42c2eb19a2948af1c00ba33`,
**90 file members** + 13 directory entries, **0 unreadable**. Strike spans blanked in place before
recognising.

**One class hit, and it is the CORRECT split, not the defect** — `certonomous-demo/site/closure.html`:

> *"Classifiers that read only the uncorrected solve and **identify** where the baseline is
> unreliable are established: Ling and Templeton in 2015, who classify RANS results point by point
> as high or low uncertainty **and control nothing**, and Wu, Wang, Xiao and Ling in 2017, an* a
> priori *confidence measure. **Using such a classifier to control where a data-driven correction is
> fitted and applied is established separately: Steiner, Dwight and Viré in 2022, and Buchanan,
> Lăcătuş, West and Dwight in 2025.** Two of those authors wrote the benchmark we are entering."*

The recogniser flags it because the corrected wording necessarily puts both halves in adjacent
sentences — a true positive for the class model and a **non-defect** on reading. **The struck
sentence is absent. V9's fix is durable in the archive**, and that is now established by recognition
rather than by two substrings.

### The PDF measurement, which the certification of record could not have made

Four archive members are PDFs. Their text is reachable, but **phrase** search of the bytes is not:

| member | printed 9-word phrase present in RAW BYTES |
|---|---|
| `geometry-study/certificate.pdf` | **no** |
| `nasa-hump/certificate.pdf` | **no** |
| `race-study/certificate.pdf` | **no** |
| `aircraft-optimization/certificate.pdf` | **no** |

Measured directly: single words survive in the byte stream, phrases break wherever PDF text
operators break for layout and kerning — in one file a 2-word phrase was already invisible, in
another a 6-word phrase survived and a 9-word one did not. **V9's discriminating fragment is 9 words
long.** So for all four PDF members the zero of record was not a measurement of absence at all. Here
they were **text-extracted with `pdftotext`** instead, and `nasa-hump/certificate.pdf` — the member
whose subject matter sits inside V9's third clause — was additionally **rendered to PNG at 130 dpi
and read visually**, because `\sout{}` is strike-and-keep and a text layer cannot tell repaired from
stale. It is a solve certificate: separation `0.6544 ± 0.2200`, k-ω SST, mesh validity. **No
prior-art claim, no citation of any of the four papers, no struck content.**

---

## 4. The three clauses, each executed

**Clause 1 — the split carried verbatim into the description: MET.**
`closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` carries it, separated exactly as
mandated: *"Classifiers on RANS-only inputs that **identify** where the baseline is unreliable are
established — **Ling & Templeton (2015)**, which classifies RANS results point by point … **and
controls nothing**, and **Wu, Wang, Xiao & Ling (2017)** … **Using such a classifier to control where
a data-driven correction is fitted and applied** is established separately — **Steiner, Dwight & Viré
(2022)** and **Buchanan, Lăcătuş, West & Dwight (2025)**."* Followed by *"Two of those authors wrote
this benchmark"* and *"No sentence in this package presents confidence-gated correction as novel."*

**Clause 2 — the Buchanan-coefficients firewall as a compliance fact: MET**, and stated unprompted:
*"**A compliance fact you are entitled to, stated unprompted.** Buchanan et al. (2025) train on the
**NASA wall-mounted hump**, which is one of your scored test cases … their published coefficients are
off limits to us, because borrowing or calibrating against them would make our entry *indirectly*
trained on a test case."*

**Clause 3 — the final check on warm-start / calibration / comparison: MET in substance**, and tested
here rather than accepted:

* *"No coefficient or artifact of that model exists in any executable file we hold"* — swept `*.py`,
  `*.sh`, `*.json`, `*.yaml` for `Lăcătuş`, `Buchanan` coefficient forms and hump-coefficient names:
  **no executable hit**. The only tracked mentions are prose records.
* Byte-identity of the prediction: `NASA_2DWMH.csv` is **identical** across the round-4 and round-5
  submission directories (sha256 prefix `cf8e023c7b8fcb05`). The round-3 directory is not tracked at
  that path, so the *"rounds 3, 4 and 5"* phrasing is verifiable here for two of the three.
* Ordering: the 2025 paper is first mentioned in the repository at `92840d8c`,
  **2026-07-31T23:13:49Z** (probes `Lăcătuş` and `Buchanan, L` agree). The earlier `Buchanan` string
  at `08007253` is the **benchmark** paper's author list, not this one — checked, because taking it
  at face value would have manufactured a false finding.

**One precision caveat, filed rather than failed.** The description dates the prediction *"16 hours
before that paper is first mentioned anywhere in our repository."* In the tracked record the
prediction's file first lands at `4c2f3562`, **2026-07-31T23:11:30Z — 2 minutes 19 seconds** before
the paper's first mention, not 16 hours. The two are not contradictory: the claim is about when the
prediction was **written**, and git records only when it was **committed**. But the 16-hour figure
rests on a write time **no tracked artifact carries**, while the margin the record can actually
demonstrate is two minutes. The direction flatters us. The clause asks for a check, the check exists
and its substantive core holds, so this does not fail the rung — it is `D285`.

---

## 5. The finding that is out of scope, and is filed, not appended

**`demo-output/website/agenda/docket.json:1594` carries the rolled-together sentence, unstruck:**

> *"a classifier reading only the uncorrected solve and **controlling where a data-driven correction
> may act** is published prior art in **Ling and Templeton 2015, Wu, Wang, Xiao and Ling 2017**,
> Steiner, Dwight and Vire 2022, and Buchanan, Lacatus, West and Dwight 2025"*

This is exactly the misattribution `d84b649f` struck — all four papers rolled into one mechanism,
crediting the two identify-papers with control. **It reads *"may act"* where the certified fragment
reads *"is allowed to act"*: one reworded phrase, and both literal sweeps pass straight over it.**
The class recogniser found it, which is the strongest validation available — an unplanted, real
instance, not one this grader wrote.

**It is filed and not appended, because it is outside V9's declared scope.** V9 names *the
description*; `docket.json` is neither the description document nor an archive member — the archive's
JSON members are mission and snapshot files only, and `docket.json` does not ship. Filed as `D286`. *(Both IDs were reassigned after a race: the grade as landed at `27295b9b` named D272 and D273, which had been taken between writing and landing — D272 by this grader's own earlier renumbered row. Corrected here rather than silently renumbered.)*

---

## 6. What this instrument still cannot see — its blind class, named

* **Claims made without a sentence.** A bibliography or table that groups all four papers under a
  heading like *"gating methods"* asserts the misattribution by layout and contains no verb. The
  recogniser needs a predicate and would return zero.
* **Text inside images.** The archive's **8 PNG members were not OCR'd**, and no figure text anywhere
  was read. This is the same blind class the PDF measurement above exposes, one step further out.
* **Vocabulary outside the synonym set** — *arbitrates*, *gatekeeps*, *adjudicates*, *supervises*
  would all pass. The set covers control/gate/govern/decide/determine/restrict/limit/dictate/switch-on.
* **Non-English wording**, and citation-only forms with no paper names spelled as searched.
* **Frame limits by instruction**: `demo-output/website/latex/` and the rest of `dist/` were out of
  frame; untracked files are invisible to the tracked-tree arm.

**The honest summary of the method finding:** a positive control on an unrelated token proves the
sweep can *reach* a file. Only a control planted in the claim's own vocabulary proves the sweep can
*recognise* the claim. V9's certification had the first and not the second, and this pass's own
recogniser needed its controls to catch a hyphen bug before it had the second either.

---

## 7. Verdict

**V9: `PASS`, 2026-08-16.** The three declared clauses are met and verified by execution; the struck
sentence is genuinely absent from all 90 archive members under a recogniser validated on eight
paraphrases with an in-archive control that fired; the PDF members were text-extracted and one was
read visually.

**The verdict of record was right. The certification that produced it would not have detected the
defect had it been present in any other wording, and could not have seen it at all in the four PDF
members.** Two findings are filed rather than appended: `D286` (the live rolled-together sentence in
`docket.json`) and `D285` (the unverifiable 16-hour figure).

---

*Non-author re-grade of rung V9. Nothing graded here was repaired — the `docket.json` sentence is
filed for its owner and deliberately left standing. No scoring call was made and the ledger stands at
6; no solver was launched; nothing was submitted, uploaded, registered or sent. `dist/` was read and
not written; `demo-output/website/latex/` was not opened.*
