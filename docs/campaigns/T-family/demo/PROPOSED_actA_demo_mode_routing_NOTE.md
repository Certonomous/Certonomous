# Routing Act A through DEMO MODE — handover note for the cfd team

**Status: PROPOSAL. NOT APPLIED.** Nothing was written under `sdk/`. No file was
deleted. No server was restarted or signalled. No solver was launched. All
verification was done in throwaway copies.

Prepared by the heat-transfer team, 2026-09-01. `sdk/` is cfd territory; both
patches are yours to apply, and the ordering in §2 is the part that matters
most.

- Patch: `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/PROPOSED_actA_demo_mode_routing.patch`
- Companion, apply first: `PROPOSED_actA_demo_mode_act.patch` and its note.
- **`git apply --check` passes against the real tree** for both.

---

## 1. THE ARGUMENT, FIRST, BECAUSE IT IS THE STRONGEST ONE HERE

**Routing Act A through the sequencer puts every string it publishes through
`check_demo_language`, so a phrase from Sanaa's never-list fails at authorship
instead of on camera.**

Three of her banned phrases are on the live Act A path right now. This is not a
reading of the prose; it is the checker in `demo_mode` run over the strings that
module actually emits:

| where | string | checker |
|---|---|---|
| `thermal_display.py:793` | "the screens come from that run's own fields" | **BANNED** |
| `thermal_display.py:806` | "Reference body received" | **BANNED** |
| `thermal_display.py:459` | "not recorded in this bundle" | **BANNED** |

Measured, by driving the routed path and counting every string it publishes
against the same phrases:

| phrase | on the routed Act A path | in the module Act A uses today |
|---|---:|---:|
| "the screens come from" | **0** | 1 |
| "Reference body" | **0** | 1 |
| "not recorded in this bundle" | **0** | 4 |
| "reference shape" | **0** | 1 |
| "neither meshed nor solved" | **0** | 1 |

136 published strings on the routed path, none of them a hit. That is not
because the act was careful. It is because `demo_sequencer` wraps `emit` once
and every payload passes `assert_screen_safe` before publication, so a banned
phrase cannot be published at all.

**Two of the three are not fixed by rewording — they are removed.** `:793` and
`:806` sit in `thermal_display.main`, which Act A stops calling. We deliberately
do NOT propose new wording for them, because the honest replacement for `:806`
is not a phrase: that block exists to say the uploaded file is neither meshed
nor solved, and DEMO MODE's answer to that situation is to make the displayed
surface BE the solved geometry rather than to describe the gap more nicely.
Rewording would let the banned *situation* persist under better words.

They remain live for Act C, which still goes through `thermal_display`. Act C is
off screen by Sanaa's order and is blocked in our act module, so that is not
urgent — but it is not fixed either, and this note does not claim it is.

`:459` is a fallback string. The already-pending `PROPOSED_actA_module_unblock`
patch stops it *reaching the screen* for Act A (5 occurrences to 0) but keeps
the literal in the module as a per-field fallback. Under this routing Act A does
not execute that code path at all.

---

## 2. ⛔ THE ORDERING REQUIREMENT — DO NOT APPLY THIS PATCH ON ITS OWN

**Applied today, this patch makes Act A FAIL its mission instead of showing the
wrong body.** Measured, driving the routed entry end to end:

    ACT A STOPPED: SequencerRefused
    the solving stage has no cases to read; an act with no cases must say
    how its logs are read before it can be shown
    events published before the stop: 29

29 events go out — prompt, restatement, assumption, geometry, meshing,
feasibility, and the wall-resolution table — and then `_run_workflow` publishes
`mission.failed`. That is the honest outcome of an act whose logs the shared
reader cannot open, and it is exactly what the previous note's §4 predicted.

**So this patch lands WITH the replay-reader work, not before it.** The reader
gap is unchanged from that note: `replay_history` opens `log.simpleFoam` by a
hard-coded name at `:224`, requires a `RUN_STATUS.*.txt` at `:463`, and reads
lift and drag columns; this run writes `log.solve`, had its launcher status file
destroyed and re-derived, and has no force coefficients.

Whether "refuses mid-mission" is better or worse on camera than "shows the
retired body under three banned phrases" is a judgement for the chief and for
Sanaa, not for this lane. We are stating the trade plainly rather than choosing
it: **this patch is safe to apply the moment the reader can read a conjugate
run, and not before.**

---

## 3. ⛔ A DEPENDENCY THAT IS NOT AT HEAD

`workflows/thermal_demo_entry.py` imports `demo_sequencer.make_act_entry`.
**That function does not exist at HEAD.** Measured:

| | `make_act_entry` defined | `jet_flap_display` uses it |
|---|---:|---:|
| HEAD `sdk/workflows/demo_sequencer.py` | **0** | **0** |
| worktree copy | 1 | 3 |

    demo_sequencer.py   worktree 221b04b9…   HEAD d9766297…   index d9766297…

So the whole DEMO MODE dispatch mechanism — including jet-flap's own adoption of
it, the only act wired through demo mode today — lives in **uncommitted** cfd
work. A fresh checkout of HEAD has neither. **This patch applies cleanly to HEAD
and its module will not import until that work is committed.** Landing that
commit is step zero.

Our own act patch has no such dependency: those three files are additions that
import only from `demo_mode`, which is at HEAD.

---

## 4. (1) THE ROUTER HUNK, AND EXACTLY HOW IT MAKES THE SURFACE AUTHORITATIVE

**The mechanism is cfd's own, already written down.** `make_act_entry`'s
docstring, `demo_sequencer.py:697-703`:

> **`params` IS DROPPED, and that is a property of the design rather than an
> oversight** — and it is the safer half. The served geometry comes from the
> ACT's own `served_stl` by way of `_stage_geometry`, never from what an
> operator happened to upload, so the picture on screen and the grid behind the
> numbers are bound structurally instead of by convention. Threading an uploaded
> filename in is exactly what would break that bind.

The chain, once routed:

1. `make_act_entry` calls `run_act(key, emit=…, script=…, typed_prompt=request)`
   and **passes no `params` at all**.
2. `demo_sequencer._stage_geometry` (`:342-351`) calls
   `announce_geometry(emit, name=g.served_stl.name, label=g.display_label)` —
   the name comes from the ACT.
3. `workflows.announce_geometry` emits `url: /api/geometry?name=<that name>`.
4. `server._serve_geometry` resolves it under `sdk/geometry`.

There is no step at which an operator's upload can enter. **Demonstrated, not
asserted** — the routed Act A run announced:

    /api/geometry?name=t23_solved_geometry.stl

and `_stage_geometry` renders `Solved on this geometry, 39,680 cells.` only
after `Geometry.solved_geometry_sentence` confirms every measured comparison
against the solved case agrees.

### The hunk itself

One row of `router.WORKFLOWS` (`router.py:918`) plus one new module.

**Why a dispatcher module rather than changing the row to point straight at the
act entry:** the thermal intent covers TWO acts. `router.py:246-258` maps the
request to screen set `"A"` (motor in a duct) or `"C"` (battery module), and
`:708` puts that in `params["thermal_screens"]`. Pointing the row at
`make_act_entry("motor-thermal", …)` would send Act C's requests to Act A's
screens. `workflows.thermal_demo_entry` reads that one key and dispatches: `"A"`
walks the nine stages, **everything else keeps today's path byte for byte**.

It reads exactly one key and never `surface`, and it does not forward `params`
to the DEMO MODE entry — forwarding is precisely what would put an uploaded
filename back in the path.

Measured:

| `thermal_screens` | where it goes |
|---|---|
| `"A"` | the nine DEMO MODE stages |
| `"C"` | `thermal_display.main(request=…, params=…, emit=…)`, unchanged |
| `""` | `thermal_display.main`, unchanged |
| `"a"` | Act A (the key is upper-cased before the comparison) |

Act C's path is preserved with all three keyword arguments intact.

---

## 5. (2) THE `motor_in_duct.stl` DELETION — AN INSTRUCTION, NOT A HUNK

**Delete `/home/ubuntu/Certonomous/sdk/geometry/motor_in_duct.stl`**
(sha256 `131aab8e17242415364d2f1147a76cfbdc7fe5f48287a0996c2318249857db5f`,
314,484 bytes).

**It cannot be expressed as a patch.** The file is **untracked** — `git status`
shows it as `??`, unlike almost every other surface in that directory — so there
is no blob for a hunk to remove. It has to be an instruction, and it is one we
will not carry out ourselves: it is an untracked file in cfd's territory.

**It is necessary and it is not sufficient, and on its own it is cosmetic.**
`server._accept_surface` writes every upload into `sdk/geometry/` under the
uploader's own filename, so the next upload of a file with that name recreates
it. Deleting it makes `/api/geometry?name=motor_in_duct.stl` return 404 today
and buys nothing tomorrow.

**Only change (1) closes the hole**, because only routing removes the operator's
filename from the path entirely. If you apply just one of the two, apply (1).

---

## 6. Verification, and what to run before restarting

| check | result |
|---|---|
| `git apply --check`, act patch | **passes** against the real tree |
| `git apply --check`, routing patch | **passes** against the real tree |
| `validate_act(motor_thermal_act.ACT)` | **empty list** |
| Act A routed, end to end | 29 events, then `SequencerRefused` at solving (§2) |
| Act C dispatch preserved | yes, all three keyword arguments |
| banned phrases on the routed path | 0 of 5, over 136 published strings |
| `sdk/tests/test_certificate_withdrawal.py` + `test_demo_mode_contract.py` | 94 passed with the new modules present |

**Before you restart anything, run the `sdk/` suite.** And read this first,
because the worktree is not clean:

- `sdk/workflows/demo_mode.py`, `demo_sequencer.py`, `adjoint_act.py`,
  `jet_flap_display.py` all read `MM`, and `_jf1_numbers.py` and
  `jet_flap_act.py` read ` M`. The DEMO MODE mechanism this patch depends on is
  in that uncommitted work (§3).
- **`sdk/tests/test_demo_sequencer_guard.py` carries a STAGED DELETION** against
  HEAD while the file is present on disk and untracked. **A bare `git commit` by
  anybody removes the guard test for the very mechanism this patch routes
  through.** Inspected, not touched — the index is chief's call.
- `sdk/geometry/motor_in_duct.stl` and `battery_module_8cell.stl` are untracked.
- `sdk/chief_engineer/router.py` is **clean** across worktree, index and HEAD
  (`94faf8cb…`), so the hunk in §4 has a stable base.

**Restart scope.** Both patches are Python inside packages the control-room
server imports, so neither takes effect until the server restarts. Batch them
into the single coordinated restart rather than bouncing a server Sanaa is
sitting in. Nothing here touches a bundle, a figure or a `.tex` sheet.

---

## 7. What we could not verify

- **That Act A completes on camera.** It cannot until the replay reader can open
  a conjugate run. Everything above the solving stage was driven and measured;
  the solving stage was never exercised.
- **That Act C's screens are byte-identical after the dispatcher.** We proved
  the dispatch reaches `thermal_display.main` with the same three keyword
  arguments, and the call is unchanged. We did not render Act C end to end and
  diff its output, because doing so puts the run Sanaa ordered off screen
  through a renderer, and we judged that not worth doing to prove a call we can
  read. If cfd wants that arm run, it is a short job and it is yours.
- **Whether "refuses mid-mission" is preferable to today's screen.** That is a
  judgement about what Sanaa should see, not a measurement. Stated in §2, not
  decided.
- **`expected_seconds = 30.0` in the act's mesh plan remains CHOSEN, NOT READ.**
  The case's `log.blockMesh` carries no timing line. It is the only number in
  the act not taken from an artifact, it reaches no screen, and nothing
  validates it.
