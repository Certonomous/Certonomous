# S6 re-scored on a held-out partition — provenance, two numbers, and the negative side

**Written 2026-08-11 by an agent that produced none of the work it is checking.**
Measurement only: no detector code, pre-registration, standard or lesson was
modified. Every number below was produced by importing the **shipped** helpers
`chief_engineer.head_engineer._residual_controls` and `._solver_tolerances` and
applying them to the archive — no second implementation of the relation exists
anywhere in this check, because a reimplementation agreeing with itself would
prove nothing about the one that ships.

Prompted by **L-63**: the detector's docstring names its motivating sentinel as
`p 1e-15;//1e-4;`, and that byte sequence is present inside the corpus the
135-of-135 was scored against. The question is not whether the rule is right.
It is whether the number still means what it has been quoted to mean.

---

## 0. Reproduction first

Before partitioning anything, the shipped helpers were replayed over the 222
gated logs recorded in `demo-output/website/monitor/replay_s1_s6.json`. Every
shipped figure reproduces **exactly**:

| shipped figure | reproduced |
|---|---|
| sentinel-excluded (target ≤ its own field's solver tolerance) | **135** |
| structurally reachable, gated | **81** |
| tolerance unreadable, fail open | **6** |
| fires among the gated | **35** (43%) |
| campaign / dafoam / mega-batch fire rate | **16/33, 12/13, 7/35 = 48% / 92% / 20%** |
| excluded-class members carrying a `1e-15` target | **135 of 135** |
| excluded-class members NOT carrying one ("nothing else") | **0** |

So the arithmetic under examination is sound. What follows is entirely about
what it is evidence *for*.

---

## 1. Provenance, from the record

### 1.1 What the git record establishes

Four commits on 2026-08-10, in this order:

| time (UTC) | commit | what it did |
|---|---|---|
| 21:16:02 | `07472cf2` | **Refused** the S6 wiring. Records that the then-current S6 replay was **37 fires over 46 gated logs**, and that *"all 46 recovered targets are the same value, `p: 1e-15`, a run-to-the-cap sentinel from **one case family** that no solve reaches."* |
| 21:38:28 | `b69cd45e` | Fixed the corpus (`*.log` glob → content-derived), 449 files → **1,375 run logs**, S6-gated 46 → **222**. Separation still by the **literal value** `1e-15`: "41 fires over 87 logs". |
| 21:42:11 | `ab0c8d76` | **Pre-registration**, before any wiring code. First appearance of the constant-free relation (target ≤ that field's own solver tolerance), together with its 135 / 81 / 6 validation table. |
| 21:49:36 | `1471b8f3` | Wiring + the shipped docstring. |

**The identity of the "one case family" is recoverable.** The superseded replay
artifact `demo-output/website/monitor/superseded_20260810T212525Z_replay_s1_s6.json`
still carries its own `s6_target_sources`. All 46 gated logs came from exactly
four case directories:

```
demo-output/website/dafoam/ladder-b/B3_work/CBFS            11 logs
demo-output/website/dafoam/ladder-b/B3_work/fixA_kbounds    12 logs
demo-output/website/dafoam/ladder-b/B3_work/fixB_SA         12 logs
demo-output/website/dafoam/ladder-b/B3_work/fixC_empty      11 logs
```

All four of those `system/fvSolution` files carry the docstring's byte sequence
`p               \t1e-15;//1e-4;` at line 110, and declare `p` a linear-solver
`tolerance` of `1e-12` — the exact pair the docstring cites.

**This is establishable:** at the moment the sentinel was first named in the
record (21:16), the author's entire S6 evidence base was those four cases, and
those four cases carry the cited specimen. The docstring cites a case that was
demonstrably in view.

### 1.2 What the record does NOT establish

- **Which of the 18 archive files carrying the byte sequence the docstring means.**
  The sequence is not unique: it appears in 13 `W2_sparta_runs/cbfs_*` cases,
  the 4 `B3_work` cases, and `ladder-b/duct_baseline/CBFS`. L-63 reads it as
  `W2_sparta_runs/cbfs_prop`; the git record points at `B3_work`. Both readings
  are consistent with the text. The partition below is computed **both ways** so
  the answer does not depend on resolving it.
- **That the relation was *derived* from that specimen** rather than merely
  illustrated by it. Nothing in the record shows the derivation. "The docstring
  cites this case" is established; "the rule was derived from this case" is not,
  and on this record it is not establishable.
- **The relation was, however, not blind to the full corpus.** The commit that
  introduced it (21:42) also contains its 135 / 81 / 6 table over all 222 gated
  logs, under the heading *"Validated on the corrected corpus … before adoption"*.
  By its own words that table is **retrospective**. The pre-registration's
  genuinely forward-looking predictions are the *post-wiring fire rate* and the
  *family spread* — and those, as section 3 shows, are held-out in full. The
  135-of-135 is not one of them.

---

## 2. The two partitions, sized before any score

Two nested definitions of in-sample, because §1.2 leaves the docstring
ambiguous. Sizes are in **run logs** (the unit the 135 counts), over the 222
gated logs:

| partition | definition | logs | of which carry a `1e-15` target |
|---|---|---|---|
| **In-sample (narrow)** | the four `ladder-b/B3_work` cases — the *entire* S6 evidence base at 21:16 | **22** | 22 |
| **In-sample (wide)** | narrow **+** every other case carrying the exact byte sequence (13 × `W2_sparta_runs/cbfs_*`, `duct_baseline/CBFS`) | **33** | 33 |
| **Held-out (vs narrow)** | the remaining 200 logs | **200** | 113 |
| **Held-out (vs wide)** | the remaining 189 logs | **189** | 102 |

The wide in-sample set is deliberately over-generous: it treats every case in
the archive that could possibly be the docstring's referent as if it were, which
is the least favourable assumption available to the shipped headline. All scores
below are reported against the **wide** partition; the narrow partition only
moves 11 logs from held-out to in-sample and changes no conclusion.

---

## 3. The two scores

### 3.1 Capture ("135 of 135")

| partition | logs | sentinels present | captured | rate | "nothing else" violations |
|---|---|---|---|---|---|
| **In-sample (wide)** | 33 | 33 | **33** | **100%** | **0** |
| **Held-out (wide)** | 189 | 102 | **102** | **100%** | **0** |
| in-sample (narrow) | 22 | 22 | 22 | 100% | 0 |
| held-out (vs narrow) | 200 | 113 | 113 | 100% | 0 |

**Family spread of the capture, held-out partition:**

| family | held-out logs | sentinels | captured |
|---|---|---|---|
| dafoam | 112 | 95 | **95 / 95** |
| campaign | 42 | 7 | **7 / 7** |
| mega-batch | 35 | 0 | — (no sentinel in this family) |

**Family spread of the capture, in-sample partition:** dafoam 22/22, campaign
11/11, mega-batch 0 present.

### 3.2 Fire rate ("92 / 48 / 20") — fully held-out

The pre-registered family spread is a rate over the **81 gated** logs. Every one
of the 81 is in the held-out partition under both definitions: the in-sample
partition contains **zero** gated logs (all 33 are sentinel-excluded).

| family | gated | fires | rate | in-sample members |
|---|---|---|---|---|
| dafoam | 13 | 12 | **92%** | 0 |
| campaign | 33 | 16 | **48%** | 0 |
| mega-batch | 35 | 7 | **20%** | 0 |

**The 92 / 48 / 20 spread is clean.** It was pre-registered before the wiring
existed, it is measured on logs the rule's specimen has no membership in, and it
reproduces exactly with the shipped helpers.

---

## 4. Does the gap change a conclusion?

**No — the direction L-63 feared is not the direction the data goes.** Held-out
capture is 102 of 102 with zero false captures, identical to in-sample. There is
no in-sample/held-out gap to speak of, and the fire-rate half of the headline
never had an in-sample member at all.

**But the held-out partition is weaker evidence than its size suggests, for a
reason neither the shipped record nor L-63 states.** An archive-wide sweep of
all 239 `fvSolution` files carrying a `residualControl` block, using the shipped
helpers, finds that **every unreachable target in the entire archive is the same
value**:

| unreachable (target, its own tolerance) | files |
|---|---|
| `(1e-15, 1e-12)` | 132 |
| `(1e-15, 1e-14)` | 4 |

So on this archive the constant-free relation `target ≤ that field's own
tolerance` and the bare constant `target == 1e-15` are **extensionally the same
predicate** — they agree on all 239 files, in both directions. The 102 held-out
captures are 102 further copies of one specimen propagated by template reuse
across families, not 102 independent instances of the defect class.

The margin is correspondingly untested. The tightest ratio of target to its own
tolerance anywhere in the **gated** class is **50×** (`f` in `D5_rsm_runs/EBRSM`),
median **1000×**; the excluded class sits at **0.001×** throughout. No case in
the archive comes within 50× of the boundary from above or nearer than 1000×
from below — a gap of ~4.7 decades. That is strong evidence the
partition is robust *on this archive* and no evidence at all about where the
boundary actually falls.

**Verdict on the headline: it survives, with its scope corrected — not
withdrawn.** The claim it can carry is a claim about propagation, not about
generalisation to unseen defect shapes.

### Restate it in exactly these words

> On the corrected 1,375-log replay corpus, the relation captured **135 of 135**
> `residualControl` targets that sit at or below their own field's linear-solver
> tolerance, and nothing else — **102 of those 135 on cases outside the family
> the rule's cited specimen belongs to** (33 in-sample, 102 held-out, both
> 100%, zero false captures). The pre-registered fire-rate spread of
> **92% / 48% / 20%** is measured entirely on held-out logs. **Every unreachable
> target in the archive is the same value, `p 1e-15`**, so the score measures
> how far one sentinel propagated, not how the rule behaves on a defect of a
> different shape, which the archive cannot test.

Drop the phrase "evidence the rule generalises" wherever it appears. Replace it
with "evidence the rule tracks the sentinel wherever the template was copied."

---

## 5. The negative side, re-derived

"And nothing else" is a claim about the 1,240 logs the exclusion did **not**
flag. Split by what can be said about each:

| not-flagged group | logs | does any in fact carry the defect? |
|---|---|---|
| gated (a reachable target found) | 81 | **No.** Zero of the 81 has *any* field whose target sits at or below its own tolerance — checked per field, not per log. The classes are disjoint, not merely ordered. |
| fail open (no tolerance resolvable) | 6 | **No** — read by hand: targets `5e-7`/`5e-6` against tolerances `1e-8`. All reachable. |
| steady, but no case archived beside the log | 186 | **Unknowable from the log.** The target is not printed; the detector is not at fault, but the corpus cannot adjudicate these. |
| transient / no residual block | 967 | Out of scope by construction (S6 is a steady-state rule). |

And independently of logs, an archive-wide sweep of case dictionaries:

- **239** `fvSolution` files carry a `residualControl` block; **136** carry the
  defect; **94** are clean; **9** fail open.
- **21** of the 136 defect-carrying cases have **no run log** in the gated
  corpus, so they were never counted by the 135 — including
  `dafoam/f6b_periodic_hills/case_breuer_re10595`, all 16 `f6d_option_a/*` cases,
  `W2_sparta_runs/{cbfs_baseline_post,cbfs_ic1,ph_baseline_post}` and
  `ladder-b/duct_baseline/CBFS`. Applying the shipped helpers directly to each,
  **all 21 are caught**. These are not misses; they are defect-bearing cases
  outside the scored corpus's reach.
- **Zero** cases anywhere in the archive declare a `1e-15` `residualControl`
  target and escape the exclusion.

The negative side therefore holds with no exception found — and, unlike the
positive side, it is tested against a genuinely varied population: the 94 clean
cases span every family and five decades of declared target.

---

## 6. Reach of this result — including what it does not establish

- **Established.** The four `ladder-b/B3_work` cases were the *whole* of the
  S6 evidence base when the sentinel was first named in the record, and they
  carry the docstring's cited byte sequence and its `1e-12` tolerance.
- **Established.** Held-out capture 102/102, in-sample 33/33, zero false
  captures in either; fire-rate spread 92/48/20 entirely held-out. All
  reproduced with the shipped helpers, matching the shipped figures exactly.
- **NOT established — that the rule was *derived* from the cited case.** The
  record shows citation and co-presence, not derivation. This check cannot close
  that, and neither can the archive.
- **NOT established — that the rule generalises.** Every defect instance in the
  archive is one value. A held-out partition made of copies of the in-sample
  specimen is held-out in provenance and in-sample in content. **This is the
  real limit on the headline, and it is not the limit L-63 identified.**
- **NOT established — behaviour near the boundary.** ~4.7 decades separate the
  two classes everywhere in the archive. No case tests the relation where it
  would be hard.
- **NOT tested here.** Whether S6 *should* fire on the runs it fires on;
  whether the pre-registered ±15pp band was well chosen; anything about S8.
- **Scope.** 1,375 archived run logs under `demo-output/` as of this commit.
  Static dictionary reads only. No solver was run and no compute was spent.

---

## 7. Found while not looking for it

1. **The shipped `_solver_tolerances` cannot resolve OpenFOAM regex-group field
   keys, and this silently disarms S6.** A case may declare
   `residualControl { "(U|p)" 5e-7; }` against `solvers { "(U|k)" { tolerance 1e-8; } }`.
   Both are legal OpenFOAM and both are *self-describing* in exactly the sense
   the rule relies on, but the helper matches keys by string equality, so the
   pair never meets. All 6 fail-open logs are this, not a missing declaration —
   and `D5_rsm_runs/EBRSM` is worse: it is scored as **gated on a single field**
   (`f`) while its other three declared controls are silently unresolved, so its
   arming target is chosen from a third of what the case declares. The rule's
   own premise — "both numbers are declared by this same file" — is true of
   these cases; only the parser cannot see it. Fails safe, but the fail-open
   count of 6 is a parser artefact reported as a property of the archive.

2. **The pre-registration's sentinel table is retrospective and reads as
   prospective.** It sits under "**Written 2026-08-10, BEFORE any wiring code
   exists**", and the RESULT section later lists "sentinel-excluded, by
   construction | 135 | **135** | met" in the same table as the genuinely
   forward predictions. A number computed in the same commit that states it
   cannot be "met"; it can only be restated. The forward predictions in that
   file are real and were met — this one is a measurement wearing a
   prediction's row. That is L-63's failure mode reproduced *inside* the
   document L-63 is about.

3. **The corpus fix changed the number the classes are cut by, not the cut.**
   At 21:38 the separation was the literal `1e-15` (41 fires / 87 non-sentinel
   logs); at 21:42 the constant-free relation gave 35 fires over 81 gated plus 6
   fail-open — and `35 + 6 = 41`. The relation reproduced the constant's
   partition exactly and moved 6 logs from "gated" to "fail open". The move to a
   constant-free rule was a genuine improvement in *justification*; on this
   archive it was a change of **zero** in *classification*.

4. **`superseded_20260810T212525Z_replay_s1_s6.json` is why any of this is
   answerable.** The lab's habit of retaining superseded artifacts rather than
   overwriting them is what made the 46-log corpus identifiable eleven hours
   later. Without it, §1.1 would have been "not establishable".
