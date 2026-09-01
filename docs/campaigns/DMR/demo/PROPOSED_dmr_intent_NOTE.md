# The shock-reflection routing patch: design note for patches that are NOT applied

**Status: PROPOSAL. NOT APPLIED. NOT LIVE. NO SERVER WAS TOUCHED.**

Rebuilt by a cfd lane, 2026-09-01. Two patch files sit beside this note in this
directory, and neither has been applied to the working tree:

| file | what it does | `git apply --check -p1` |
| --- | --- | --- |
| `PROPOSED_dmr_intent.patch` | routes the shock-reflection intent to the landed act | **passes** at the HEAD named below |
| `PROPOSED_subcent_cost_line.patch` | makes a sub-cent compute cost legible on screen | **passes** at the same HEAD |

**The control-room server was running for the whole of this work and was not
started, stopped, restarted, signalled or bound.** No solver was launched and
no new compute was booked. Nothing under `sdk/` was written.

---

## 0. THE HEAD THESE WERE BUILT AGAINST, AND THE FACT THAT THEY WILL ROT AGAIN

**Built and checked against `75d9705d4be2f17f503c6e6a3d5412af3a1b2dd9`.**

The previous version of this patch **stopped applying**, and that is the normal
outcome rather than an accident: these are context diffs against files that
several teams edit, and this box commits roughly once every two minutes. HEAD
moved twice during the rebuild itself — from `c2aae69b` to `e41055cc` while the
first `apply --check` was running, and on again before the second.

**So re-run the check before believing this note, every time:**

```
git apply --check -p1 docs/campaigns/DMR/demo/PROPOSED_dmr_intent.patch
git apply --check -p1 docs/campaigns/DMR/demo/PROPOSED_subcent_cost_line.patch
```

Exit 0 means it still applies. A non-zero exit means it has rotted again and
needs another rebuild; it does **not** mean anything is wrong with the design
below, which is stable. The routing patch touches only insertion points that
have been stable for weeks, so a rebuild is mechanical.

---

## 1. WHAT CHANGED SINCE THE PREVIOUS VERSION OF THIS PATCH

The previous patch carried **three** files. This one carries **two**, and the
withdrawal is the important half.

**WITHDRAWN: the 326-line `sdk/workflows/dmr_display.py`.** When that patch was
cut, no shock-reflection act existed and the patch had to bring one. It exists
now: `sdk/workflows/dmr_act.py` landed at commit `6f02808a` as a one-line
adoption of `demo_sequencer.make_act_entry`, and it carries its own `main`.
Shipping the old shim as well would have created **a second call site for one
mechanism**, which is precisely what `make_act_entry`'s own docstring says this
campaign has already paid for twice in one night. The dispatch entry in this
patch therefore points straight at `workflows.dmr_act`.

**CHANGED: the scope import is now its own statement.** The previous patch
reflowed the shared `from .router import (...)` tuple in `scope.py`. That is the
line the MERGE NOTE at `router.py` records as having cost a night: the thermal
and jet-flap patches were cut independently against one blob, both appended to
that one list, git could not merge them, and taking either side whole silently
dropped the other act. A one-name `from .router import DOUBLE_MACH_REFLECTION`
on its own line cannot collide with anybody else's addition.

**The result is that both files are now PURE INSERTION.** Measured:

| file | insertions | **deletions** |
| --- | --- | --- |
| `sdk/chief_engineer/router.py` | 81 | **0** |
| `sdk/chief_engineer/scope.py` | 18 | **0** |

Not one existing line is modified or removed in either file.

---

## 2. THE DELEGATION IS LOCAL, AND `server.py` IS UNTOUCHED

The jet-flap act's shape is the precedent and it was followed as far as it goes.
`sdk/chief_engineer/server.py` is **byte-untouched** by this patch, so the
dispatcher through which every team's intent runs is unchanged by construction
rather than by inspection.

`router.py` and `scope.py` **are** touched, and they have to be: they are the
only place an intent can be declared, and the previous patch was wrong to be
described as avoiding them. What is kept is the minimum — a constant, two
regexes, one scoring branch, one spoken sentence, one dispatch entry, one
capability declaration, and the asserts below. The act itself, the sequencer,
the stages and the screen guard are all reached through the existing mechanism
with nothing added to it.

**The selector fork is not weakened, because it is not touched.**
`make_act_entry`'s fork — a selector naming no act falls through to `fallback`
unchanged, and with no fallback it raises `SequencerRefused` rather than showing
the wrong act — lives in `demo_sequencer.py`, and this patch does not modify that
file. `dmr_act.py` passes neither `use_act` nor `fallback`, which is the
single-act case: the entry always walks the stages.

### 2a. L-221/L-222 — the entries are inserted with an assert, and the assert already earned its keep

Both `WORKFLOWS` and `CAPABILITIES` are **dict literals**, where a second entry
under an existing key is not an error: the later value silently wins, that act's
module is swapped, and nothing raises anywhere. Each insertion therefore carries
a two-line assert that it displaced nothing — one naming this route, one naming
the jet-flap route.

**That assert caught a real defect in this patch before it left the lane.** The
first build inserted the `WORKFLOWS` assert but not the `WORKFLOWS` *entry*; the
patch compiled and the import died immediately on `KeyError:
'double-mach-reflection'`. Without the assert the route would have been
half-wired and would have failed at dispatch, on camera, instead of at import.

The asserts are deliberately **narrow** — this route and the act being filmed,
nothing else. An assert enumerating the whole table would fail the next time a
peer adds a route, and an assert that stops the control room from importing is a
worse failure than the one it guards against.

---

## 3. PROOF THAT JET-FLAP IS UNAFFECTED

Sanaa is filming jet-flap. Two independent lines of evidence, one by
construction and one by measurement.

### 3a. By construction: the act path never imports the patched modules

Measured from `sys.modules` after importing the whole jet-flap act path in a
fresh interpreter, not inferred from a grep. Importing
`workflows.jet_flap_display` pulls in eight `chief_engineer` modules —
`chief_engineer`, `.adapters`, `.api`, `.events`, `.fleet`, `.models`,
`.openfoam`, `.uncertainty` — and **neither `chief_engineer.router` nor
`chief_engineer.scope` is among them.** The two files this patch edits are not
in the act's import closure at all, so no edit confined to them can reach the
act's behaviour by any path.

### 3b. By measurement: the event stream is byte-identical

The jet-flap act was driven end to end twice on this box, once with the repo's
own `router`/`scope` and once with the patched pair loaded in their place. The
patched pair was compiled against the **real repo path**, so `Path(__file__)`
inside `router.py` resolved exactly as in production.

| | before | after |
| --- | --- | --- |
| return code | 0 | 0 |
| events published | 1,281 | 1,281 |
| printed transcript | 167 bytes | **byte-identical** |
| event stream, `at` removed | `sha256 91ed98c0e761bd0a59e0a97e06bfae79057bbc265ba0acfc37ce34ae2c388f2c` | **same sha256** |

**The only key that differed across all 1,281 events was `at`**, the wall-clock
stamp — the two runs were two minutes apart. Every other field of every event
matched. This is the standard the namespace fix set and it is met.

**A first attempt at this comparison was wrong and was thrown away.** It copied
the package to a scratch directory, which moved `Path(__file__).resolve()`
inside `router.py` — the path by which it finds the staged surface catalogue —
and two unrelated prompts then differed. The harness was rebuilt rather than the
difference explained away.

### 3c. Nothing was written to the repository

A write guard was run across `demo-output/`, `mission-output/`, `sdk/` and
`verification/runs/`, with `CERTONOMOUS_OUTPUT` redirected to scratch. **The
guard's first form returned a false zero** — `find` on this box is `bfs`, which
rejects a relative `-newermt` argument and reported nothing modified anywhere. A
planted control caught it: a file was touched and the guard failed to see it.
Rebuilt with an ISO timestamp and re-planted, the guard demonstrably sees a
known-new file.

Under the working guard: **zero files written** in `demo-output/`,
`mission-output/`, `sdk/` and `verification/runs/DMR_runs/`. The 43 files that
did move under `verification/runs/JF1_jet_flap/` are OpenFOAM time directories
appearing on a ~35-second write interval from a live solver, still arriving
after this lane's processes had exited; `jet_flap_act.py` contains no write call
of any kind.

---

## 4. WHAT THE ROUTER DOES AFTER THE PATCH

94 routing decisions were compared before and after — every act's registered
on-camera prompt, plain-language probes for every routed intent, and eight
shock-reflection probes, each evaluated with and without an uploaded surface.

**78 of 94 decisions are identical.** The 16 that changed are exactly the eight
shock-reflection probes in their two surface states, and nothing else. Every
jet-flap phrasing, every thermal prompt, every steady compressible body, the
searches, the race, the valve, the empty request and the out-of-scope request
all keep the intent, the confidence, the evidence list and the spoken sentence
they have today, to the byte.

Reaching the act: `double Mach reflection`, `the Mach 10 shock reflection
benchmark`, `show me the Mach stem and the triple point`, `Woodward Colella
shock interaction benchmark`, `irregular reflection of a strong shock`, `a shock
reflecting off a wall too steeply to stay attached`, `the shock reflects from
the ramp`, `shock reflection off a wedge` — all at confidence 0.99.

**Deliberately NOT reaching it:** `the shock reflected at the corner of the
wedge` keeps the route it has today. The surface pattern requires a named
surface, and "corner" is a word written about the steady wedge.

### 4a. A GAP, NAMED RATHER THAN PAPERED OVER: an uploaded surface reroutes this act

`_SURFACE_KEEPS_ROUTE` is **not** touched by this patch, so a shock-reflection
prompt that arrives **with an uploaded surface** becomes a geometry study — the
incompressible chain, on an unrelated body. That is the same failure the MERGE
NOTE describes for the thermal and jet-flap acts, and it is why both of them are
on that list.

It was left out on purpose and the decision belongs to the supervisor:

- **For adding it:** the act starts no solver, and rerouting a shock-reflection
  prompt into a geometry study is plainly the wrong answer.
- **Against adding it:** `make_act_entry` **drops `params`** by design, so the
  act would never see the upload and could not announce it. Jet-flap earns its
  place on that list by stating on screen that the uploaded surface was not
  meshed or solved; this act has no such sentence, so keeping the route would
  silently ignore an upload.
- **It does not affect the shoot.** With no surface uploaded, `apply_surface`
  returns the route unchanged, so the filmed path is unaffected either way.

If the supervisor rules that it should be added, it can be done as a **pure
insertion after the tuple** rather than an edit to it —
`_SURFACE_KEEPS_ROUTE = _SURFACE_KEEPS_ROUTE + (DOUBLE_MACH_REFLECTION,)` with
an assert — which is exactly the shape that would have avoided the merge note's
night.

---

## 5. A BOUNCE IS REQUIRED. MEASURED, WITH THE MECHANISM

**HTML needs no bounce.** `server._serve_control_room` calls
`(HERE / "control_room.html").read_bytes()` **per GET**, so a saved HTML change
is live on the next refresh.

**This patch needs one.** `server.py` reaches the router at line 738 with
`from .router import WORKFLOWS, apply_surface, classify`, and `scope` at line
778 with `from . import scope`. Both are **function-local** imports, which looks
like a re-read and is not: `import` consults `sys.modules` first and returns the
cached module without touching the file. There is **no `importlib.reload` and no
reload machinery anywhere** in `server.py`, `router.py` or `scope.py`.

Demonstrated rather than asserted, with a planted control:

| step | result |
| --- | --- |
| first call to a function-local `from pkg.m import VALUE` | `ORIGINAL` |
| the file on disk is then rewritten, and read back | `VALUE = "PATCHED"` |
| second call, **same process**, after that edit | **`ORIGINAL`** |

The middle row is the control: the file demonstrably changed, and the import
still returned the stale value.

**So: the act cannot go live without a restart, and the restart is the chief's
to schedule, not this lane's and not the supervisor's.** Sanaa is mid-shoot.

**What should ride the same bounce, since a restart is a coordinated cross-team
event and should not be spent twice:**

1. This routing patch (`router.py`, `scope.py`).
2. The sub-cent cost-line patch (`demo_mode.py`), if it is accepted — it is
   import-time for the same reason.
3. Any other pending Python change to `sdk/` from any team. Every `.py` under
   `sdk/` is import-time; only `control_room.html` is not.

**One thing does NOT need the bounce for its own sake:** `workflows.dmr_act` is
imported lazily by `importlib.import_module(workflow["module"])` at
`server.py:794`, on the first mission that routes to it. It has never been
imported in the live process, because no route reaches it. It ships with the
bounce only because the router change it depends on does.

---

## 6. CAMERA ITEM ONE — "about $0.00" READS AS "FREE"

`demo_mode.cost_line` renders `about ${usd:,.2f}`. At the shock-reflection
magnitude the derived figure is $0.0016, which prints as **`about $0.00`**.

Sanaa has ruled that **cost transparency is a rule and the compute line is
KEPT**, so the repair makes the number legible and never removes it.
`PROPOSED_subcent_cost_line.patch` renders the same derived figure in cents
below one cent:

> Compute used: 2.4 processor-minutes (gross), **about 0.2 cents**, derived at
> the recorded rate.

**This is shared code that jet-flap also renders, so the threshold was chosen so
that jet-flap cannot move.** Measured: **every run at or above 5.85 core-minutes
renders byte-identically to what it renders today.** Jet-flap's measured cost is
**117.5 core-minutes** and its sentence is
`Compute used: 117.5 processor-minutes (gross), about $0.10, derived at the
recorded rate.` — **byte-identical under the patch**, 20x above the crossover.
The only acts that can move are those costing under 5.85 core-minutes, and the
shock-reflection act is the only one of those.

**On present tense, and why this patch does not chase it.** The line reads
"Compute used", which is not present tense. Making it so — "This run costs 2.4
processor-minutes…" — would change **jet-flap's rendered sentence too**, mid
shoot, and that is exactly the unilateral change to shared behaviour this lane
was told not to make. **Recommendation: take the sub-cent fix now, defer the
tense of the shared sentence until after the shoot.** The shock-reflection act's
own lines are already present tense.

---

## 7. CAMERA ITEM TWO — 1.9 IS THE FLATTERING FIGURE. THE RIGHT ONE IS ~2.4

The act computes its cost as
`sum(_wall_seconds(key) for the two grids) * RANKS / 60`, which is **the two
solves and nothing else**. The graded record, `verification/campaign/
DMR_RESULTS.md`, files this at lines 135–138:

| line | figure |
| --- | --- |
| res120 solve | 1.67 core-min (25.09 s × 4) |
| res60 solve | 0.22 core-min (3.35 s × 4) |
| mesh/init/reconstruct/locator | < 0.5 core-min |
| **item total** | **~2.4** |

1.67 + 0.22 = **1.89**, which is the 1.9 on screen. **The record's item total is
~2.4, and the screen should say ~2.4.** Three reasons:

1. **The comparison is against a whole-item estimate.** The act shows the price
   set aside — 20 — beside what was used. That 20 covered meshing,
   initialisation, reconstruction and the locator as well as the two solves.
   Comparing a complete numerator against an incomplete denominator is a
   category error, **and it always errs in the flattering direction.**
2. **The record grades the estimate against ~2.4**, explicitly: *"filed 20,
   measured ~2.4 — off by ~8× on the cheap side"*. A screen quoting 1.9 implies
   a ratio of 0.095 where the record filed 0.12, putting the demo out of step
   with its own evidence.
3. **It is this act family's recurring defect**, now at seven instances and
   counting, and every one of them has been in the same direction.

**The honest counter-argument, stated because it is real:** 1.89 is the only
figure the act can *measure at display time*. Both wall clocks are parsed from
the two solver logs and cross-checked against the graded record before either is
shown. The `< 0.5 core-min` for meshing and post-processing is a **bound**, not
a measurement, and no log carries it — so quoting ~2.4 means reading the item
total from the graded record rather than deriving it.

**That is the right trade and the act already reads that record** for its
cross-check. **Recommendation: quote the graded item total, ~2.4, cited to
`DMR_RESULTS.md:138`.** If the supervisor prefers the parsed figure instead, then
the line must *say* it covers the two solves only — leaving 1.9 unlabelled beside
an estimate of 20 is the flattering error, whichever number is chosen.

---

## 8. WHO HAS TO READ THIS BEFORE ANYTHING LANDS

The cfd supervisor reads both patches **as diffs** (`SUPERVISION_CHARTER.md` §3
check 1): `router.py` and `scope.py` are shared control-room tooling whose
routing table governs every team's prompts, and `demo_mode.py` is shared act
code that jet-flap renders from.

Applying either patch is a decision above this lane. **Restarting the server is
a separate decision again, is a coordinated cross-team event, and is the
chief's.** Neither was taken here.
