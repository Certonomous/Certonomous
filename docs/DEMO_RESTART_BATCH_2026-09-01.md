# Coordinated control-room restart batch — 2026-09-01

STATUS: **STAGED AND VERIFIED. THE SERVER HAS NOT BEEN RESTARTED.**

Prepared by the cfd integration lane. The running control-room server
(pid 848778, port 8765) was never signalled, never touched and never
restarted by this lane. Sanaa is sitting in it. The restart belongs to the
chief and happens only after she is told.

---

## 1. What is in the batch

| # | Item | Owner | State |
|---|---|---|---|
| 1 | scope-down fix | cfd | committed earlier, already in the tree |
| 2 | caption wiring | cfd (other lane) | committed at `9994c5b6` |
| 3 | thermal display mission | heat-transfer | **applied by this lane** |
| 4 | jet-flap display mission | cfd | **applied by this lane** |
| 5 | GUI curation (`control_room.html`) | cfd (other lane) | in flight, NOT touched here |
| — | DMR display mission | cfd | **DEFERRED out of this batch** |

The DMR patch (`docs/campaigns/DMR/demo/PROPOSED_dmr_intent.patch`) remains
committed and UNAPPLIED. The DMR act is shootable from its committed sheet
and figure without any server change, so it buys nothing tonight and it was
the third colliding insert into the same two tables. It is deferred, not
withdrawn.

## 2. The collision, and how it was resolved

Both patches were cut independently against the same base blobs —
`router.py` at `40521daec147bf19d2f2ee8dfe059bd4da8cae5e` and `scope.py` at
`95253fdd2866563444bbdee68b1f1c53f72a4053` — and both were still at those
blobs when this merge was made. Each applies cleanly ALONE. **Applied in
sequence, the second is refused.**

Resolution was a three-way merge against the shared base, not a forced
apply. `scope.py` merged with no conflict. `router.py` produced **one**
conflict, and it was the dangerous one:

- **`_SURFACE_KEEPS_ROUTE`** — both patches append a *different* member to
  the *same* tuple. Taking either side whole silently drops the other act's
  entry, and the failure is invisible until an operator uploads a surface on
  camera and the act reroutes to a geometry study. Resolved by hand as the
  union of both members and both rationales, neither reworded. The merged
  tuple carries `THERMAL_DISPLAY` and `JET_FLAP_DISPLAY`.

Completeness was then checked line by line: every line each patch added is
present in the merged file except the two tuple-closing lines that were
deliberately rewrapped into the union, and both symbols were confirmed
present by parsing the file rather than by grepping it.

## 3. Regression sweep — the point of the exercise

Two new intents entering a scoring router move the denominator for every
prompt (confidence is `scores[intent] / total`), so an existing act can
silently change route or confidence. Prompts were driven through the real
`classify()` on both trees and compared on intent, confidence AND rationale.

| Corpus | Prompts | Identical | Changed |
|---|---|---|---|
| Curated — one positive arm per pre-existing route, plus negative arms | 39 | 35 | 4 |
| Uncurated — English sentences harvested from repo prose | 1200 | 1198 | 2 |

**Every change is an intended new-route capture. No pre-existing route moved
in intent, confidence or rationale — the drift count with unchanged intent
is zero on both corpora.**

Negative arms that were checked and held: shock vocabulary belonging to the
steady compressible acts (oblique shock on a wedge, bow-shock standoff on
the hypersonic cylinder, shock-expansion on the diamond airfoil); `flap`,
`wing` and `slot` as section words *without* blowing physics; thermal
vocabulary naming a body the lab has not landed a run for (rocket nozzle,
turbine blade); and the uncertainty, race, Ahmed and valve prompts.

### The shooting sheet

| Prompt | Before | After |
|---|---|---|
| motor-in-duct thermal | `unseen-geometry` @0.58 | `thermal-display` @0.67 |
| battery-module thermal | `general-mission` @0.30 | `thermal-display` @0.99 |
| jet-flap blown wing | `unseen-geometry` @0.99 | `jet-flap-display` @0.74 |
| generic blown slot on a car body | `unseen-geometry` @0.58 | `unseen-geometry` @0.58 |

The fourth does not route to the jet act — correct. It also produces no
scope-down line, because `unseen-geometry` is one of the six routes that
declare no capabilities and `unmet_asks` treats an undeclared route as an
unknown rather than a mismatch. **That is unchanged from HEAD**, not a
regression, but it does mean the expectation that this prompt "still
produces the scope-down line" is not met and was not met before either.

## 4. Capability coverage

| | Routes | Declared | Uncovered |
|---|---|---|---|
| Before | 20 | 14 | 6 |
| After | 22 | 16 | 6 |

The uncovered six are unchanged: `GENERAL_MISSION`, `RACE_COMPARISON`,
`SOBOL_SENSITIVITY`, `TIME_CONSTRAINED`, `UNCERTAINTY_REDUCTION`,
`UNSEEN_GEOMETRY`.

Both new routes declare. `JET_FLAP_DISPLAY` declares `{blowing}` — so the
real act does **not** scope itself down on camera; verified directly.
`THERMAL_DISPLAY` declares `{thermal, unsteady}`, carrying the
heat-transfer supervisor's recorded ruling verbatim.

Checked in both directions: none of the seven on-camera arms fires a false
scope-down, and six deliberate mismatches (asking either act to optimise, to
blow where it cannot, or for a temperature it does not hold) all scope down
correctly.

## 5. THE EXACT RESTART COMMAND — NOT RUN BY THIS LANE

The three variables live **only** in the running process's environment.
Without them every solve drops to one rank. They were read from
`/proc/848778/environ`, not from recall.

```bash
# 1. Stop the old server and CONFIRM it is gone before starting anything.
#    Port 8765 permits a second binder: if the old process survives, IT KEEPS
#    ANSWERING and the new screens never appear, with no error shown.
kill 848778
for i in $(seq 1 30); do [ -d /proc/848778 ] || break; sleep 1; done
if [ -d /proc/848778 ]; then
    echo "pid 848778 STILL ALIVE -- do NOT start a second server"; exit 1
fi

# 2. Start, with all three variables exported.
cd /home/ubuntu/Certonomous/sdk
export CHIEF_ADAPTER=openfoam
export OPENFOAM_RUN_PREFIX=openfoam2606
export CERTONOMOUS_SOLVE_RANKS=16
setsid nohup python3 -u -m chief_engineer.server \
    >> /home/ubuntu/logs/control_room.log 2>&1 &

# 3. Verify the new process holds all three, and that only ONE thing listens.
sleep 3
ss -ltnp | grep 8765
NEW=$(pgrep -f 'chief_engineer.server')
tr '\0' '\n' < /proc/$NEW/environ | \
    grep -E 'CHIEF_ADAPTER|OPENFOAM_RUN_PREFIX|CERTONOMOUS_SOLVE_RANKS'
```

`setsid` matters: a server started in an agent's foreground shell is killed
when that agent ends.

## 6. Test suite

410 passed, **1 failed**, 43 subtests passed across the routing and scope
suites on the merged tree.

The single red is
`tests/test_scope_down.py::TheMismatchIsDetected::test_the_blowing_prompt_really_does_route_to_the_generic_study`,
and **it is the tripwire firing as designed**. Its own docstring says: *"If
routing ever improves, this fails loudly rather than leaving the scope-down
above testing nothing"*, and it names the exact historical failure —
*"which is how 'Airfoil blown slot' became an unblown 3D baseline"* — that
the jet-flap patch exists to end.

Measured, so the change is precise rather than assumed:

- `"Airfoil blown slot"` + `airfoil.stl` — was `geometry-study` with a
  blowing scope-down, is now `jet-flap-display` with none. **This is the
  intended fix.** It is the assertion that fails.
- The suite's fuller `_BLOWING_PROMPT` is **unchanged** — still
  `geometry-study`, still scoped down on blowing.

**This test is NOT edited by this lane.** Altering a guard to match new
behaviour is a supervisor's call, and this guard was written to demand
exactly that decision. It is reported, not resolved.

A separate pre-existing red, `tests/test_autostop_gate.py`, fails on the
untouched tree at HEAD and is unrelated to this batch. Reds in
`_a2_shape.py` and `geometry_admission.py` belong to dafoam and were not
touched.

## 7. Two defects found in the jet-flap patch, neither introduced by this merge

Both were confirmed against the jet-flap patch applied **alone**, with no
thermal patch and no merge, so neither is a merge artifact.

1. **The "both are required" guard does not hold for the `blown slot`
   phrasing.** `_JET_FLAP_SECTION` matches the bare word `slot`, which is
   the same word that satisfied `_JET_FLAP_PHYSICS` in `blown slot`. So a
   blowing prompt naming no aerofoil at all reaches the act: `"blown slot on
   my car"` routes to `jet-flap-display`. The patch's own comment claims
   physics and a section are both required; for this phrasing they are
   satisfied by one word. Latent — no shooting-sheet prompt hits it.

2. **The physics vocabulary is narrower than the phrasing people use.**
   `"Run a blowing sweep on this airfoil: vary the jet slot momentum
   coefficient and give me lift against C-mu."` does **not** reach the act —
   `_JET_FLAP_PHYSICS` carries `jet momentum coefficient` but not `jet slot
   momentum coefficient`, nor `C-mu` alone. The registered demo prompt
   works; this near-neighbour does not.

Neither blocks the batch. Both are referred to the cfd supervisor.
