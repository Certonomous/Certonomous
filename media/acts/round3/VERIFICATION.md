# Round-3 backend verification (BACKEND-3)

End-to-end run on the Certonomous server, port 8768 (8765 untouched),
2026-07-23. Every act launched through the real `/api/missions` route; events
streamed to durable JSONL and pulled back via `/api/missions/<id>/events.json`.
The three sealed certificate PDFs were then fetched from `/api/certificate/<dir>`.

Solver note: WSL Ubuntu was Stopped and VSPAERO was not installed on this box,
so the airliner ran its (real) conceptual sizing screen and was honestly graded
CONCEPTUAL MODEL rather than SOLVER-BACKED. On a solver-live box the same wiring
names "OpenVSP VSPAERO, vortex lattice" and lifts the finalists to SOLVER-BACKED.
The valve act is entirely reduced-order (no external solver) so it is fully real
here. The NACA geometry study resolved and certified the NACA wing from cached
mesh/reference; the point verified here is the routing fix, not a fresh solve.

## Item 2 - P0 named-body resolution (the reported bug)
Directive typed WITHOUT a file upload:
  "Solve the external aerodynamics of the supplied NACA 4412 finite-wing
   geometry at cruise Reynolds number. ..."
- route: geometry-study, params.surface = **naca4412_wing.stl** (was motorBike)
- report title: "Geometry study: NACA 4412 finite wing"
- geometry label: "NACA 4412 finite wing, as supplied"
- zero occurrences of motorcycle/motorbike in the whole event stream
- certificate C-2026-7069 SUBJECT "NACA 4412 finite wing",
  source geometry naca4412_wing.stl
See naca.events.json, naca_certificate.pdf / .txt.

## Item 1 - a certificate for every act
- Airliner (Act 1): certificate.ready fired -> C-2026-7080, seal
  a07a58fb00c401c2..., subject "300-passenger twin-aisle airliner, planform
  study", headline "Best feasible cruise L/D 18.5 +- 0.5 (95%)", full
  three-channel table (input 0.46 quantified; numerical grid-discrete; model
  from the UQ airliner-anchors study). airliner_certificate.pdf / .txt.
- Valve (Act 3): certificate.ready -> C-2026-8945, seal e79cc1185d9d720a...,
  subject "Idealized trileaflet aortic valve, systolic configuration", headline
  "Cycle-weighted pressure loss 1345 Pa +- 441 Pa (95%)" (RSS-combined band;
  input alone is 421, numerical 81 from the phase-quadrature ladder k=3/5/9,
  model 105 correlation-family), winner 80 deg. valve_certificate.pdf / .txt.
- Race (Act 4): wired identically (speedup + agreement as results, subject
  NACA 4412); asserted green under the stubbed-solver race test. Not run here
  because the race needs live VSPAERO on both lanes.
Every certificate is wrapped: a failing seal never takes down a good mission.

## Item 3 - valve visuals
- CANDIDATE_ANGLES 4 -> 11 (30..80 deg): 11 landscape points, 12 geometry.ready
  (11 candidates cycling + winner). See valve.events.json.
- Systolic waveform PNG emitted via plot.ready and copied here as
  valve_systolic_waveform.png (the figure Katie likes); it leads the report.
- Winner stays 80 deg / 1345 Pa; min-orifice still marks 30 and 35 deg
  infeasible.
- UQ fingerprint unchanged: the candidate set is not a fingerprint field, so the
  stored aortic-valve study still matches (verified in-code and on this run).

## Files
- summary.json - machine summary of all three runs
- <act>.events.json - full event stream per act
- <act>_certificate.pdf - the sealed certificate served by the API
- <act>_certificate.txt - the certificate's rendered text (content proof)
- valve_systolic_waveform.png - the waveform figure

Note: a plain rasterizer/browser-capture pipeline was not available in this
session, so the certificate CONTENT is captured as extracted text plus the PDFs
themselves rather than page bitmaps; sdk/scripts/capture_video.py is the tool
for producing on-camera stills and every event it captures is emitted by these
runs.
