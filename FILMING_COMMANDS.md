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

From your laptop, substitute your EC2 public IP:
- http://<IP>:8765
- http://<IP>:8080

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
| 9 | "Solve the ONERA M6 wing and grade the surface pressure against AGARD." | about 10 min |

**Expected results:**

1. St 0.1578 vs 0.1590, 0.77%, PASS
2. Shock angle 44.693 deg vs 45.344 exact, 1.44%, PASS
3. 27.309 vs 26.737, 2.14%, PASS
4. Cd 0.03624 vs 0.03633, 0.26%, PASS
5. Standoff 0.4181 vs 0.4152, 0.70%, PASS
6. Cd 0.3041 vs 0.285 published, 6.7%, tier SOLVER-BACKED
7. Separation 0.6544 vs 0.665 (-1.6%), reattachment 1.2534 vs 1.100 (+13.9%), tier VALIDATED
8. Cd 0.020901 vs 0.02090, +0.007%, tier VALIDATED
9. **DOCUMENTED FAILURE** — tier UNCONVERGED. This one takes about ten minutes and then
   reports that it did not converge. That is the expected outcome, not a fault on the day.
   Only film it if you want the failure on camera; it is a strong segment but a slow one.

## The other demos

| Demo | Prompt | Duration |
|------|--------|----------|
| B-52 | "Solve the external aerodynamics of the supplied B-52 geometry." | 51 s |
| Heart valve | "Find the valve opening angle that minimizes pressure loss over the cardiac cycle." | 8 s |
| Airliner | "Optimize the L/D of an airliner for 300 passengers, 6000 km range." | 17 s |
| Monte Carlo vs reduced-order | "Race a Monte Carlo uncertainty study against a reduced-order model." | 194 s |

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

The nine-act gate table, every row citing the artifact it came from:
```bash
cd /home/ubuntu/Certonomous && python3 scripts/gate_table.py --md
```

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
