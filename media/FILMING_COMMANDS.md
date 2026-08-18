# Filming Commands

## Before you start

**Servers:**
- Control room UI: http://127.0.0.1:8765
- Static website: http://127.0.0.1:8080

Start or restart both (idempotent):
```bash
bash /home/ubuntu/Certonomous/scripts/demo_servers.sh
```

Check both are up:
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/
```

From your laptop, this instance's public IP is **16.58.201.228**:
- http://16.58.201.228:8765 — control room, where you type the prompts
- http://16.58.201.228:8080 — static website

(The IP changes if the instance is stopped and started. Re-read it with
`curl -s http://169.254.169.254/latest/meta-data/public-ipv4` after any restart.)

## The surfaces

**No act requires an upload.** Eleven of the thirteen prompts build their own
geometry from the numbers in the prompt. The two that use a surface resolve it
from the words in the prompt automatically: say "B-52" and it finds the B-52.
Uploading is a demo beat you can choose to film, not a dependency — see
`LAPTOP_SHOOT.md` for the upload flow and what each act does with an attached
surface.

Two directories, two different jobs. Do not mix them up:

| directory | what it is |
|---|---|
| `/home/ubuntu/Certonomous/sdk/geometry/` | **the server's** staging area — the only directory the control room reads, and where `/api/geometry/upload` writes what you upload. It changes at run time. |
| `/home/ubuntu/Certonomous/demo-surfaces/` | **your** copy set — the five bodies to scp to the laptop, git-tracked and byte-identical to the staged originals. Copy from here. |

Copy from `demo-surfaces/`, not from `sdk/geometry/`: an upload named
`b52.stl` overwrites `sdk/geometry/b52.stl`, so that directory is not a stable
source. Verified 2026-07-30 — all five files md5-identical in both places.

| Act | Surface file |
|-----|--------------|
| B-52 | `demo-surfaces/b52.stl` (674K, staged as `sdk/geometry/b52.stl`) |
| ONERA M6 | `sdk/geometry/onera_m6_wing.stl` (610K, server-side only) |

Confirm the staged set before you start:
```bash
ls -lh /home/ubuntu/Certonomous/sdk/geometry/*.stl
```

The copy set is also served by the control room itself, on the port you are
already using, so a shut static site cannot leave an act asking for a body it
cannot be given:

```bash
curl http://127.0.0.1:8765/api/surfaces             # names, sizes, digests
curl -O http://127.0.0.1:8765/api/surfaces/b52.stl  # the bytes
```

It serves `demo-surfaces/` for the reason above, and its listing names every
staged surface it does not carry.

**One surface, one launch.** An attached surface is consumed by the launch it
was attached to; the panel resets to "Load a surface (STL / OBJ)" afterwards.
If you want a second act on the same body, attach it again. This matters
because the router reads an attached surface as "run it on this body": leaving
one attached would turn the next act into a generic geometry study.

## The nine acts

Type each prompt into the control room.

Durations below are measured, warm, on this box — three runs each, 2026-07-30,
box at load ~12 of 16. The spread column is max minus min across those runs;
it is what your narration has to absorb. Time from pressing Launch to the
mission reporting complete.

| Act | Prompt | Duration | Spread |
|-----|--------|----------|--------|
| 1 | "Solve vortex shedding behind a circular cylinder at Reynolds 100 and check the Strouhal number." | 2.0 s | — |
| 2 | "Solve the supersonic wedge at Mach 2 with a 15 degree half-angle and check the oblique shock angle." | 1.0 s | 0.0 s |
| 3 | "Solve the supersonic cone at Mach 2.35 with a 10 degree half-angle and check the conical shock angle." | 3.9 s | 0.0 s |
| 4 | "Solve the diamond airfoil at Mach 2 and check the wave drag against shock-expansion theory." | 1.2 s | 0.0 s |
| 5 | "Solve hypersonic flow over a blunt cylinder at Mach 8 and check the shock standoff distance." | 1.0 s | 0.0 s |
| 6 | "Solve the Ahmed body with the 25 degree slant and check the drag against the wind tunnel." | 21.5 s | 0.1 s |
| 7 | "Solve the NASA wall-mounted hump and check separation" | 17.3 s | 0.2 s |
| 8 | "Solve the CRM wing-body and check the drag." | 0.2 s | 0.0 s |
| — | ONERA M6: **removed from the filmed sequence, see below** | — | — |

Act 1 was broken and is now fixed. The server that cron starts at boot did not
export the solver launcher, so the wake solve could not run and the act failed
on camera with "the wake solve did not complete". The launcher is now exported
where the servers are started, so a boot-started server picks it up too.

**Verified through the control room on 2026-07-30 at 17:24 UTC**, after a
restart: St 0.1578 against the correlation's 0.1590, 0.77%, and the act
reproduces IDENTICAL on a repeat run. The 4 s figure below is that run.

Still restart the control room before filming. It is what loads the current act
code, and several acts changed today.

**Expected results:**

1. St 0.1578 vs 0.1590, 0.77%, PASS
2. Shock angle 44.693 deg vs 45.344 exact, 1.44%, PASS
3. 27.309 vs 26.737, 2.14%, PASS
4. Cd 0.03624 vs 0.03633, 0.26%, PASS
5. Standoff 0.4181 vs 0.4152, 0.70%, PASS
6. Cd 0.3041 vs 0.285 published, 6.7%, tier SOLVER-BACKED
7. Separation 0.6544 vs 0.665 (-1.6%), reattachment 1.2534 vs 1.100 (+13.9%), tier VALIDATED
8. Cd 0.020901 vs 0.02090, +0.007%, tier VALIDATED
## Why ONERA M6 is no longer act 9

The control room is promotional and carries no failures. The M6 act was a
documented failure (unconverged), so its scoring was removed from the control
room's routing on 2026-07-29. **Do not type the old M6 prompt on camera.** It
no longer runs the AGARD grading act; it now falls through to a generic
geometry study on the M6 surface, and that path has never been timed or
rehearsed. An untimed run is the one thing you do not want live.

The M6 result still exists in the permanent record and in the gate table below
as an honest UNCONVERGED row. That is the right place for it.

**There are now eight filmed acts, not nine.** Every one of them passes.

## The other demos

Measured the same way, 2026-07-30.

| Demo | Prompt | Duration | Spread |
|------|--------|----------|--------|
| Adjoint wing | "Cut the drag on the wing with the discrete adjoint and verify the gradient against finite differences." | 0.7 s | 0.2 s |
| Adjoint wing, conditions stated (attach `mach_tutorial_wing.stl`) | "Cut the drag on the attached wing. Continue as long as reduction <20% but don't go over 50 its." | 0.7 s | 0.2 s |
| B-52 (with `b52.stl` uploaded) | "Solve the external aerodynamics of the supplied B-52 geometry." | 26.9 s | 0.7 s |
| Heart valve | "Find the valve opening angle that minimizes pressure loss over the cardiac cycle." | 7.5 s | 0.0 s |
| Airliner | "Optimize the L/D of an airliner for 300 passengers, 6000 km range." | 11.7 s | 0.0 s |
| Airliner, requirements typed out (attach `airliner_wing_span52.stl`) | "Optimize lift drag coefficient of the attached twin airliner. Constraints: 300 passengers, Range: 6000 km, take off speed: 80 m/s landing speed: 70 m/s. Don't use all of my workers" | 14 s | 1 s |
| Monte Carlo vs reduced-order | "Race a Monte Carlo uncertainty study against a reduced-order model." | 172.1 s | 1.3 s |

The race is the one act that is not a replay: it solves 93 wings live every
time, and its wall clocks are the measurement the act exists to show. Its
duration therefore tracks how busy the box is — the figure above is for a box
running the demo and nothing else. Its **physics** is fixed: the ensemble draws
from a stated seed, so the peak, the band and the two-path agreement are the
same on every take. Only the measured cost and the speedup move, by roughly
half a turn in the last digit (17.0x, 17.5x across runs).

The airliner's second prompt is the same act with the requirements typed out
and a wing attached. It routes to the airliner at confidence 0.73, the surface
rides in as the search's starting geometry, and the measured span re-centres
the span ladder on it, so the search runs 96 wings from 37 m to 67 m rather
than the standing prompt's 112 from 34 m to 68 m. Both prompts work; only this
one exercises the upload path, the stated take-off and landing speeds, and the
worker-headroom ask. Its figure above was taken on a box carrying other work,
so treat it as an upper bound rather than the quiet-box time the rows above
carry.

## The adjoint act — what you can and cannot say

This is the **only** act in the control room that is a genuine adjoint. The
cylinder `shape-optimization` act is a surrogate-gradient study; **do not call
that one adjoint on camera.** This one you can.

**Two prompts reach this act.** The one that names the method routes at
confidence 0.79. The one that states conditions instead, "Cut the drag on the
attached wing. Continue as long as reduction <20% but don't go over 50 its.",
routes at 0.74 and takes the attached wing as its subject. Attach
`mach_tutorial_wing.stl` for that take: the act confirms the wing it was handed
by measuring it, and reports 28.3% and 47 major iterations against the two
conditions the prompt stated. Either prompt plays the same beats below.

The act paces itself now, so the mission takes **about 38 seconds** and
**plays for about 55 seconds on screen**: it is a design optimization you
watch, not a page of tables. Time your narration against the playback, not the
mission.

**The visual beats, in order:** baseline wing → the adjoint gradient painted on
the skin (~18 s) → the wing morphing across 48 frames with the drag trace
descending beside it (~20-24 s) → a root close-up of the same morph where the
section change is legible (~27-32 s) → the optimized wing held.

Everything is at **true scale**. The act cannot exaggerate: the scaling code was
removed outright. The shapes were reconstructed by replaying the optimizer's own
recorded design variables through the same FFD map it used, verified linear to
7.4e-15 — a replay of what the optimizer did, not a model of it.

If the change looks subtle, that is the honest answer: nothing on screen is
scaled, and the act says so on its own face. The amplification arithmetic it
used to quote is no longer narrated, so do not quote it either.

**What it puts on screen:**

- Discrete adjoint gradient of drag and lift over **105 design variables**
  (96 shape control points, 7 twist stations, 2 flow-state).
- The finite-difference verification, all six physical groups: worst is
  **C_d/shape at 1.71%**, best is **C_L/patchV at 0.00145%**. Every geometric
  constraint derivative at machine precision. **Gate passes.**
- **28.3% drag reduction at matched lift** (C_d 0.029620 to 0.021245, both at
  C_L 0.5), after **47 major iterations**, against the untwisted baseline.
- On the conditions prompt, those two numbers put beside the two the prompt
  asked for: 20% and 50 major iterations.

**Say this:** "a discrete adjoint, finite-difference verified, and 28.3% below
the untwisted baseline at matched lift after 47 major iterations."

**Do not say:** that it converged, that it is an optimum, or that 28.3% is a
validated number. It is measured against our own baseline at the same lift,
not against a wind tunnel. Do not narrate how or why the run stopped; the act
does not, and the owner has ruled that it should not. The act says everything
it claims on its own face, so the honest framing is already on screen if you
let it run.

Verified numbers came from the run's own primary logs (the optimizer's
iteration table and its history database), not from a summary document.

## The D9 segment

Read the talking points:
```bash
cat demo-output/website/campaign/D9_TALKING_POINTS.md
```

Then show:
```
http://<IP>:8080/benchmarks.html
```

The uncertainty band predicted a known NASA error in writing before the run.

## If something looks wrong

- If a page will not load, re-run:
  ```bash
  bash /home/ubuntu/Certonomous/scripts/demo_servers.sh
  ```

- The control room shows a routing confidence number. It can read low (0.43 for CRM, 0.49 for M6). This is the winner's share of all matched patterns, not a doubt about the answer. All thirteen prompts were verified to route correctly.

## Checks you can run on camera

These two are safe to show. Nothing else in this section is.

Both servers responding — both should return 200:
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/
```

The gate table, every row citing the artifact it came from. Use `--filmed` on
camera: it shows the eight acts that met their gate, and names the one it
withheld in a footer rather than pretending it does not exist.
```bash
cd /home/ubuntu/Certonomous && python3 scripts/gate_table.py --filmed --md
```

Drop `--filmed` for the full nine-row table including the honest UNCONVERGED
row. That version is a strong segment if you want a "we grade ourselves"
beat; it is the wrong one mid-highlight-reel. Your call on the day.

## Run these with the camera OFF

Not because anything is wrong with them — their output is internal
housekeeping and names machinery, file paths and timings that do not belong
in a shot.

Wording check across every act:
```bash
bash scripts/audit_transcripts.sh
```

Recipe check across every camera surface, transcripts, closing reports and the
static pages (`docs/DEMO_DISCRETION_CHARTER.md`: the demo may withhold method,
it may never misstate result). A review aid, so read the hits rather than
counting them; false positives are expected and a reference's identity always
stays:
```bash
bash scripts/audit_camera_discretion.sh
```

Confirm the acts still reproduce their numbers:
```bash
bash scripts/verify_warm_replay.sh
```

Rebuild the archive:
```bash
bash scripts/package_caches.sh
```

Archive already built: `/home/ubuntu/certonomous-cache.tar.gz` — 346 MB, md5 d8857f35df9d458fa67e9934324feb1b
