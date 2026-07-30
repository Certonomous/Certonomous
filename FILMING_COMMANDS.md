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

**You do not upload or pick a file on camera for any act.** Eleven of the
thirteen prompts build their own geometry from the numbers in the prompt. The
two that use a surface resolve it from the words in the prompt automatically:
say "B-52" and it finds the B-52.

Staged surfaces live in `/home/ubuntu/Certonomous/sdk/geometry/`. That is the
only directory the control room reads. All 21 surfaces are present and were
verified staged on 2026-07-30:

| Act | Surface file |
|-----|--------------|
| B-52 | `sdk/geometry/b52.stl` (674K) |
| ONERA M6 | `sdk/geometry/onera_m6_wing.stl` (610K) |

Confirm they are all there before you start:
```bash
ls -lh /home/ubuntu/Certonomous/sdk/geometry/*.stl
```

## The nine acts

Type each prompt into the control room.

| Act | Prompt | Duration |
|-----|--------|----------|
| 1 | "Solve vortex shedding behind a circular cylinder at Reynolds 100 and check the Strouhal number." | 5 s |
| 2 | "Solve the supersonic wedge at Mach 2 with a 15 degree half-angle and check the oblique shock angle." | 5 s |
| 3 | "Solve the supersonic cone at Mach 2.35 with a 10 degree half-angle and check the conical shock angle." | 10 s |
| 4 | "Solve the diamond airfoil at Mach 2 and check the wave drag against shock-expansion theory." | 5 s |
| 5 | "Solve hypersonic flow over a blunt cylinder at Mach 8 and check the shock standoff distance." | 5 s |
| 6 | "Solve the Ahmed body with the 25 degree slant and check the drag against the wind tunnel." | 25 s |
| 7 | "Solve the NASA wall-mounted hump and check separation and reattachment." | 25 s |
| 8 | "Solve the CRM wing-body and check the drag." | 1 s |
| — | ONERA M6: **removed from the filmed sequence, see below** | — |

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

| Demo | Prompt | Duration |
|------|--------|----------|
| Adjoint wing | "Cut the drag on the wing with the discrete adjoint and verify the gradient against finite differences." | 1 s |
| B-52 | "Solve the external aerodynamics of the supplied B-52 geometry." | 51 s |
| Heart valve | "Find the valve opening angle that minimizes pressure loss over the cardiac cycle." | 8 s |
| Airliner | "Optimize the L/D of an airliner for 300 passengers, 6000 km range." | 17 s |
| Monte Carlo vs reduced-order | "Race a Monte Carlo uncertainty study against a reduced-order model." | 194 s |

## The adjoint act — what you can and cannot say

This is the **only** act in the control room that is a genuine adjoint. The
cylinder `shape-optimization` act is a surrogate-gradient study; **do not call
that one adjoint on camera.** This one you can.

Routes to `adjoint-optimization` at confidence 0.79. Replays in about 1 second.

**What it puts on screen:**

- Discrete adjoint gradient of drag and lift over **105 design variables**
  (96 shape control points, 7 twist stations, 2 flow-state).
- The finite-difference verification, all six physical groups: worst is
  **CD/shape at 1.71%**, best is **CL/patchV at 0.00145%**. Every geometric
  constraint derivative at machine precision. **Gate passes.**
- **28.3% drag reduction at matched lift** (C_d 0.029620 → 0.021245, both at
  C_L 0.5), after **47 major iterations**.
- The stopping condition, as its own table: stopped by a **60-minute wall
  clock**, no convergence statement printed, both first-order measures still
  about an order of magnitude above the 1e-5 tolerance.

**Say this:** "a real discrete adjoint, finite-difference verified, and we
stopped it on a clock before it converged — so that 28% is a partial result."

**Do not say:** that it converged, that it is an optimum, or that 28.3% is a
validated number. It is measured against our own baseline at the same lift,
not against a wind tunnel. The act says all of this on its own face, so the
honest framing is already on screen if you let it run.

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

Confirm the acts still reproduce their numbers:
```bash
bash scripts/verify_warm_replay.sh
```

Rebuild the archive:
```bash
bash scripts/package_caches.sh
```

Archive already built: `/home/ubuntu/certonomous-cache.tar.gz` — 346 MB, md5 d8857f35df9d458fa67e9934324feb1b
