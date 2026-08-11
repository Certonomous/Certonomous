# Shipping bundle rebuilt — what changed beyond the stale claims

**Ordered on Ladder V's V14 discovery rung (`d358fd96`), which found the tracked,
shipping `dist/certonomous-demo.zip` stale.** Rebuilt and committed at
`892f11f7`. Zero solver compute.

---

## 1. The four defects, verified gone in the artifact as it will ship

Verified by **extracting the committed zip and grepping the extraction** — not by
inferring from the sources, because that inference is exactly what left it stale
for ten days.

| # | defect (committed artifact) | rebuilt artifact |
| --- | --- | --- |
| 1 | `site/closure.html` hero: **0.0654**, "our entry of record" — round 4 as current | **0.0566** |
| 2 | `site/closure.html` 254–256: **the prior-art sentence struck 2026-08-05**, verbatim | **0 hits anywhere in the bundle** |
| 3 | `site/benchmarks.html` KPI: **0.0676** — round 3 as current | **0.0566** |
| 4 | `snapshot/lab_stats.json`: `our_score` **0.0676**, "across **four** scoring calls" | **0.0566**, "across **six**", "round 5" |

**Precondition checked before rebuilding**, because the discovery rung flagged it:
the live `lab_stats.lifetime_counters()` had to be round-5 itself. It is —
`our_score 0.0566`, `"Entry of record (round 5, 2026-08-07)"`, six scoring calls.
A rebuild against a stale counter would have re-shipped defect 4.

**Historical round values remain and are correct**: `0.0741 → 0.0676 → 0.0654 →
0.0566` in the per-round table, and *"was 0.0654 until round 5, §4"*. The defect
was never the presence of old numbers; it was presenting one as current.

## 2. What changed BEYOND the four defects — and one of it matters a lot

A rebuild regenerates everything. Diffed extraction-against-extraction:

### 2a. All four mission recordings were replaced — and the committed one was the WRONG RUN

`pick_missions()` takes *"the most recently finished COMPLETE mission for each
filmed intent"*, so a rebuild necessarily swaps recordings. All four changed.
**One of those swaps is a correction, not a side effect:**

| | committed bundle | rebuilt bundle |
| --- | --- | --- |
| aircraft-optimization recording | `m-7ef43acf8ff2` | `m-9c67e2638ff1` |
| **`airliner_wing_span52.stl` upload present?** | **NO** | **YES** |
| spans / areas explored | 58 / 64 / 68 at area 300 | 55 / 61 / 67 at areas 360, 420 |

**`LAPTOP_SHOOT.md` names this exact failure** (line 177): *"Upload
`airliner_wing_span52.stl` **with the button, before typing**. Not optional …
a run without it **searches a different span ladder and lands on a different
wing**."*

> **The bundle that has been shipping carried a recording of the run Katie's own
> script warns against — the aircraft act performed without its upload.** The
> rebuild replaces it with a recording that has the upload. **The backup console
> now replays the right act.**

All four acts are `complete` in both bundles, with comparable event counts
(76–541 vs 78–631), so nothing was truncated by the swap.

### 2b. The bundle's SDK copy advanced to the current tree

Five modules **added** — `lever_echo.py`, `mesh_certificate.py`, `exec_bits.py`,
`pce_surrogate.py`, `uncertainty_band.py` — and ten updated (`server.py`,
`lab_stats.py`, `uq.py`, `certificate.py`, `head_engineer.py`, and others). This
is the control-room code the bundle exists to carry; three of the additions are
this week's mesh-certificate and lever-echo work.

### 2c. Derived artifacts followed the recordings

Four `certificate.pdf`s and three plot PNGs differ, and the aircraft act's STL
set changed with its span ladder. All are outputs of the swapped recordings.

**Zip size 1,425,076 → 1,497,848 bytes (+72 KB)**, consistent with five added
modules and a different mission set.

## 3. The guard was NOT blind. It was failing, and nobody acted on it.

`self_audit.check_bundle_drift()` compares the extracted bundle against the tree
for every file the builder copies verbatim — **and `_BUNDLE_PAGES` covers
`closure.html`, `benchmarks.html` and `wall.html` explicitly.**

**Run against the committed bundle it returned FAIL with 18 items**, including:

```
page closure.html:    demo-output/website/closure.html differs from the shipped copy
page benchmarks.html: demo-output/website/benchmarks.html differs from the shipped copy
page wall.html:       demo-output/website/wall/wall.html differs from the shipped copy
```

**It named the two surfaces carrying the stale claims, by name, and it had been
saying so.** This is *not* the day's other pattern — not a check that
structurally could not see its target. **The check worked; its output did not
reach a rebuild for ten days.** That is a different failure and it should not be
filed under the same heading.

**After the rebuild the same check returns PASS with zero items** — which is the
end-to-end verification that the rebuild is complete, not just that four greps
came back clean.

## 4. Ruling on `dist/certonomous-demo/` — it stays, and here is why

**It is a build output.** `.gitignore:72` says so in its own words: *"Laptop
bundle build output (the .zip is committed; the extracted tree is not)"*. It is
the builder's default `--out`; the zip is written beside it. Nothing deploys
from it — `scripts/laptop_bundle/START-HERE.md` tells the user to extract the
**zip**.

**On the chief's framing that a build output does not belong in the tree, the
answer is nevertheless KEEP IT, for a reason that outranks the general rule:**

> **`self_audit.check_bundle_drift()` compares against that directory.** Remove
> it and the check degrades to `WARN: "no bundle at dist/certonomous-demo to
> compare"` — the drift detector for the only artifact that leaves this box
> would go dark. **Deleting the stale copy would remove the one thing that was
> correctly reporting the staleness.**

**What actually let it drift invisibly was not its existence but its
gitignoring** — this lab's `grep` wrapper honours `.gitignore`, so no text
search could reach it, which is why no hand-maintained list ever contained it.
**The directory is the drift check's eyes; the `.gitignore` entry is the
blindfold on everything else.**

**Action taken:** regenerated in place alongside the zip, so the tree's copy and
the shipped artifact now match byte-for-byte and the drift check is green.

**Recommended, not taken** (it touches a shoot-critical script and the shoot
surface is Katie's): teach `check_bundle_drift` to fail — not warn — when the
bundle directory is **absent**, since an absent bundle now means the drift
detector is off rather than merely uninformative. Filed rather than applied,
three days before a shoot.

## 5. Not touched

**`LAPTOP_SHOOT.md`** — Katie's script, public-facing by design, surfaced to her
by the chief. **Read only**, to establish whether the recording swap desynced it
(§2a); it did not, and the swap moves the bundle *toward* what the script
describes. Ranks 4 and 6–11 of the discovery rung's stale list are records work
and are untouched here.

---

# ADDENDUM, 2026-08-11 — the absence verification was re-done with a wrap-proof instrument

**Chief-ordered, after §5's own finding (a line-bounded grep can report a false
absence) was pointed at the check where it mattered most.** The struck prior-art
sentence had been verified gone by `grep` three times. **`grep` is line-bounded.**

## The positive control — this is what makes the result knowledge rather than hope

The struck sentence was planted into a scratch copy of the shipped
`closure.html`, **wrapped across five lines and split by `<b>` tags**, exactly as
a real one could be:

| instrument | on the planted file (sentence demonstrably PRESENT) |
| --- | --- |
| **line-bounded `grep`** — the method used in all three prior passes | **0 hits** |
| **normalised search** (whitespace collapsed, tags stripped, accents/dashes folded) | **all 7 fragments found** |

> **The old instrument returns zero on a file that contains the sentence.**
> The three prior zeros were therefore **unsound**, not merely unconfirmed.

## The result on the real artifact — the defect is genuinely absent

Run against the extracted committed zip, the current source, **and the bytes
served over HTTP**, all agreeing:

| fragment | verdict |
| --- | --- |
| `controls where a data-driven correction is allowed to act` + `has been published repeatedly` (the struck sentence's core) | **ABSENT** |
| `Steiner, Dwight and Viré in 2022` | present — **and correct** |
| `Buchanan, Lăcătuş, West and Dwight in 2025` | present — **and correct** |
| `Wu, Wang, Xiao and Ling in 2017` | present — **and correct** |
| `Two of those authors wrote the benchmark we are entering` | present — **and correct** |

**Bundle-wide sweep: 78 text files, 23 binary skipped, core-defect hits 0** — with
the sweep's own positive control passing 2 of 2 on the planted file, so the zero
is an absence and not a broken pipe.

**Why four fragments are present and it is right that they are.** The correction
of 2026-08-05 was a **two-part split, not a deletion**. As shipped, the paragraph
now reads:

- *"Classifiers that read only the uncorrected solve and **identify where the
  baseline is unreliable** are established: Ling and Templeton in 2015, **who
  classify RANS results point by point … and control nothing**, and Wu, Wang,
  Xiao and Ling in 2017…"*
- *"**Using such a classifier to control** where a data-driven correction is
  fitted and applied is established **separately**: Steiner, Dwight and Viré in
  2022, and Buchanan, Lăcătuş, West and Dwight in 2025."*

**The struck version credited all four groups with the control mechanism
"repeatedly". The shipped version credits the control mechanism only to the two
groups that reported it, and says explicitly that Ling and Templeton control
nothing.** That is the defect fixed, not merely removed.

**A flaw in my own fragment design, recorded:** four of the seven fragments were
author names that the *corrected* text legitimately contains, so they read
PRESENT and meant nothing. **A fragment shared by the defect and its fix is
evidence of neither.** Only the mechanism clause and `published repeatedly`
distinguish the two, and those are the ones that came back absent.

## Standing

**V10 closes on sound evidence.** The general form is now §9 of this family's
guidelines: *an absence claim requires an instrument that cannot produce a false
absence, and a positive control proving it.*
