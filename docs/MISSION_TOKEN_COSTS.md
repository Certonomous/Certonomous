# What a mission costs, in tokens and wall-clock

Chief supervisor, 2026-08-11. Katie's §4 item 7 — *token instrumentation per mission class*.

**This is history, and it is marked as history.** Every figure below is a measurement of
one night, one session, one set of brief shapes. It is not regenerable — the harness
reports a subagent's token total once, in its completion notification, and that number
dies with the session unless someone writes it down. So this file is a stamped record
rather than a generator, which is the *other* half of the L-79 rule: a figure is either
regenerated at read time **or** carries the moment it was taken. This one carries it.

**Frame.** Subagent token totals as reported by the harness at completion, for agents
dispatched by session `64b13819` between roughly 16:20 and 17:45 UTC on 2026-08-11, on a
repo at commits `b5402675` through `d6d1184f`. Tool-use counts and durations are from the
same notifications. **Two process exits occurred during this window**, so several agents
were resumed from transcript; their totals include the resumed continuation and are
therefore *upper* bounds on what an uninterrupted run of the same brief would cost.

---

## The measurements

| Mission | Tokens | Tool uses | Wall-clock |
|---|---:|---:|---:|
| **Cold-start memory test** — read a reading-order, answer 12 questions with citations | **88k** | 2 | 1.4 min |
| **Capability audit** — does the installed toolchain have wave BCs, with controls | **103k** | 4 | 2.1 min |
| **Reference-data research** — verify 4 open datasets, fetch and parse them | **160k** | 5 | 2.2 min |
| **Single-question code audit** — what does F8's MRF actually do, plus a schema survey | **157k** | 5 | 3.0 min |
| **B3 absolutes checker** — build a checker, hand-label 75 records, measure its FP rate | **164k** | 33 | 17.2 min |
| **S1 research spine** — verify a premise from files, then spec Stage 2 | **168k** | 39 | 17.4 min |
| **Dead-lever audit** — derive a lever vocabulary, sweep 1,635 logs, 3 controls | **185k** | 66 | 17.2 min |
| **V16 author round** — close 5 scope items with executed evidence | **196k** | 36 | 27 min* |
| **V16 continuation** | **197k** | 35 | 62 min* |
| **B1 sweep helper** — build a helper + 26 tests, re-run 17 published sweeps | **228k** | 47 | 15.0 min |
| **B2 fail-open sweep** — scan 475 files, demonstrate defects by injection, fix 12 | **249k** | 42 | 22.4 min |
| **Naval H1** — reconstruct an ambiguity, pin a gate spec, file 3 proposals | **309k** | 72 | 20.2 min |

\* interrupted and resumed; wall-clock includes dead time.

## What it says, and the pattern is sharper than I expected

**There are two mission classes here, not a spectrum.**

- **Bounded-question missions — 88k to 160k tokens, 2 to 5 tool calls, under 3 minutes.**
  These *answer* something: does the toolchain have X, what does this code do, what do the
  files say. The tool-call count is the tell — a handful of well-chosen reads, then a
  report. **They are the cheapest useful thing this lab can dispatch**, and three of the
  four above produced findings that changed a downstream decision.
- **Build-and-verify missions — 164k to 309k tokens, 33 to 72 tool calls, 15 to 22 minutes.**
  These *make* something and then have to prove it works: a checker plus its
  false-positive measurement, a sweep plus its positive control, a spec plus its
  reconstruction. Roughly **2× the tokens and 10× the tool calls** of a bounded question.

**The 10× gap in tool calls against a 2× gap in tokens is the interesting part.** Building
is not mostly *writing*; it is mostly *checking* — running the thing, reading what it
said, adjusting. That matches what these agents actually reported: the expensive steps
were controls and re-runs, not authorship.

**Practical consequence for dispatch.** A question that can be posed as a bounded question
should be, even when the underlying subject is large. The wave-BC audit settled a
capability question over an entire OpenFOAM installation for 103k tokens and four tool
calls, because it was asked as *"does this exist, with controls"* rather than *"build me a
capability map"*. The same subject phrased as a build would have cost triple.

## What this does NOT support

- **It is not a per-family cost model.** These are agent-brief costs, not compute costs, and
  they say nothing about core-min. `docs/CAPABILITY_STRATEGY.md` §4's cost model is about
  solver time; this is about supervision overhead. Do not conflate them —
  `scripts/calibration_scorecard.py` measures the other one.
- **The sample is one session and one dispatcher.** Brief quality is a large uncontrolled
  variable, and every brief here was written by the same chief in the same style. A
  different dispatcher would move these numbers by an unknown amount.
- **Interrupted runs inflate two rows** and are marked.
- **There is no baseline for a failed mission.** Every agent above produced a usable
  result, so this table prices success and says nothing about the cost of a mission that
  goes nowhere — which is exactly the number a budget wants and the one hardest to get,
  since a fleet that reports only its wins has no denominator.

## Related

- `scripts/calibration_scorecard.py` — the *compute* half: forecast core-min against
  measured core-min. Scored 0 of 3 within 20% at the time of writing, and blocked mainly
  by 16 closed proposals that recorded no actual cost.
- `docs/CAPABILITY_STRATEGY.md` §4 — the cost-model item this feeds.
- `LESSONS.md` L-79 — why this file is stamped rather than quoted as current.
