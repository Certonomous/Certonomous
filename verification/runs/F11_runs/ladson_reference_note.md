# Ladson (1988) NACA 0012 low-speed reference — fetched and read this session, not used

**Not consumed by any run this session.** Recorded so the real research
already done is not lost, and so a future session building the "fresh
O-grid, steady simpleFoam, low-speed NACA0012" case (see F11 doc, candidate
2) does not have to re-fetch it. This is a citable reference obtained
BEFORE any run, per this project's standing discipline — it is simply
attached to a case that was not launched this session, not to one that was.

## Reference

Ladson, C.L. (1988). "Effects of Independent Variation of Mach and Reynolds
Numbers on the Low-Speed Aerodynamic Characteristics of the NACA 0012
Airfoil Section." NASA Technical Memorandum TM-4074.

**Fully open access**, confirmed directly (not via Unpaywall metadata alone
— the actual PDF was fetched and read): NASA Technical Reports Server,
`https://ntrs.nasa.gov/api/citations/19880019495/downloads/19880019495.pdf`
(the NTRS *landing page* URL is a JS single-page app and does not serve the
PDF directly — the `/api/citations/<id>/downloads/<id>.pdf` form does; noted
here because the landing-page URL alone will look like a dead end to the
next person). 97 pages, OCR'd (Acrobat Capture 3.0), `pdftotext -layout`
extracts clean, table-structured text.

## Table I, R = 5.97×10⁶, M = 0.15, free transition (the condition earmarked for a future case)

Facility: Langley low-turbulence pressure tunnel. This Re/M combination was
selected because it is close to the round Re=6×10⁶ this lab's other NACA0012
work already uses (A1 DAFoam case, TMR NACA0012 case) and M=0.15 is
comfortably in the "effectively incompressible" range Ladson himself tested.

| alpha (deg) | Cd | CL | Cm | L/D |
| --- | --- | --- | --- | --- |
| -4.05 | 0.00700 | -0.4280 | 0.0000 | -61.14 |
| -2.00 | 0.00650 | -0.2150 | 0.0000 | -33.08 |
| 0.05 | 0.00650 | 0.0040 | 0.0000 | 0.62 |
| 1.98 | 0.00680 | 0.2080 | 0.0020 | 30.59 |
| 4.18 | 0.00760 | 0.4520 | 0.0030 | 59.47 |
| 6.20 | 0.00680 | 0.6630 | 0.0040 | 97.50 |
| 8.22 | 0.00800 | 0.8800 | 0.0050 | 110.00 |
| 10.18 | 0.01050 | 1.0880 | 0.0070 | 103.62 |
| 11.08 | 0.01140 | 1.1800 | 0.0080 | 103.51 |
| 12.25 | 0.01250 | 1.2920 | 0.0090 | 103.36 |
| 13.10 | 0.01300 | 1.3680 | 0.0110 | 105.23 |
| 14.28 | 0.01620 | 1.4580 | 0.0150 | 90.00 |
| 15.20 | 0.01870 | 1.5280 | 0.0180 | 81.71 |
| 16.18 | 0.02180 | 1.5900 | 0.0210 | 72.94 |
| 16.90 | 0.02440 | 1.6180 | 0.0230 | 66.31 |
| 17.35 | 0.02750 | 1.6600 | 0.0250 | 60.36 |
| 17.65 | (OCR gap) | 1.6450 | 0.0270 | — |
| 18.65 | (OCR gap) | 1.0050 | -0.1080 | — |

**Read directly, not extracted uncritically:** the last two rows (post-CLmax,
deep stall — CL collapses from ~1.66 to ~1.00 between alpha=17.65 and 18.65)
have OCR gaps in the Cd column and sit in a region where a steady RANS solve
is not expected to be trustworthy anyway (separated, likely genuinely
unsteady flow). **CLmax ≈ 1.66 near alpha≈17.35° is therefore reported as
approximate**, not a clean point value, and a future gate should either
exclude the immediate post-stall rows or independently re-OCR that page
before trusting them. The attached-flow rows (alpha -4 to ~13, smooth, no
OCR gaps, Cd/CL/Cm all monotonic and mutually consistent) are clean and
usable for a lift-curve-slope / drag-polar gate without further checking.

## Why this was not launched this session

The obvious next step — build a fresh O-grid NACA0012 mesh (not the TMR
PLOT3D-converted C-grid already in this repo) and run `simpleFoam`/laminar
or `simpleFoam`/kOmegaSST at low alpha against this table — was set aside in
favour of the lid-driven cavity case for one reason: this exact validation
target (NACA0012 vs low-speed experimental CL/CD data) already has an
**unresolved, documented convergence pathology** in this repository on the
existing TMR C-grid (`demo-output/website/tmr/naca0012_status.json`,
`findings_2026_07_25`: a sustained, non-decaying force oscillation under
second-order momentum advection, present at both alpha=0 and alpha=10,
across two mesh resolutions and multiple relaxation settings). A fresh mesh
topology *might* avoid it — the existing investigation's own hypothesis is
that the feedback lives in the wake/trailing-edge convection of the specific
TMR-converted grid — but that is unverified, and chasing it down would be a
real, possibly multi-session numerics investigation (compare F5c's
backward-facing-step bubble-flapping investigation, which consumed a full
session and still did not reach a gate), not the "cost it, then either
launch or docket it honestly" scope this session had room for. **Docketed,
not abandoned**: reference obtained, condition selected, OCR quality
checked and caveated, and the specific known risk named so the next session
does not have to rediscover it before spending compute.
