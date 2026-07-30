| act | gate | reference | measured | deviation | verdict | artifact |
| --- | --- | --- | --- | --- | --- | --- |
| Cylinder vortex shedding, Re 100 | Strouhal vs Roshko-Williamson correlation | 0.1590 | 0.1578 | 0.77% | PASS | `mission-output/cylinder-vortex-shedding/transcript.md` |
| Supersonic wedge, M 2.0, 15 deg | Oblique-shock angle vs theta-beta-M relation | 45.344 | 44.693 | 1.44% | PASS | `mission-output/supersonic-wedge/transcript.md` |
| Supersonic cone, M 2.35, 10 deg | Conical shock angle vs Taylor-Maccoll | 26.737 | 27.309 | 2.14% | PASS | `mission-output/supersonic-cone/transcript.md` |
| Diamond airfoil, M 2.0, 7.125 deg | Wave drag vs shock-expansion theory | 0.03633 | 0.03624 | 0.26% | PASS | `mission-output/diamond-airfoil/transcript.md` |
| Hypersonic cylinder, M 8 | Shock standoff vs Billig correlation | 0.4152 | 0.4181 | 0.70% | PASS | `mission-output/hypersonic-cylinder/transcript.md` |
| Ahmed body, 25 deg slant | Drag vs Ahmed/Ramm/Faltin SAE 840300 (frontal basis) | Cd 0.285 | Cd 0.3041 | 6.7% | SOLVER-BACKED | `mission-output/ahmed-body/transcript.txt` |
| NASA wall-mounted hump | Separation / reattachment x/c vs NASA experiment | sep 0.665, reatt 1.100 | sep 0.6544, reatt 1.2534 | -1.6% / +13.9% | VALIDATED | `mission-output/nasa-hump/transcript.txt` |
| ONERA M6 wing | Primal residual vs its own tolerance (intended gate, Cp at 7 spanwise stations vs AGARD AR-138, NOT evaluated) | 1e-08 | 1.02e-06 | did not satisfy | UNCONVERGED | `mission-output/onera-m6/transcript.txt` |
| CRM wing-body | Drag vs DAFoam CRM_Wing tutorial, Cd 0.02090 +/-2% | 0.0209 | 0.020901 | +0.007% | VALIDATED | `mission-output/crm-wingbody/transcript.txt` |

9 of 9 acts have run; 9 carry a graded number.

**Ahmed body row — read `campaign/AHMED_BODY_RECONCILIATION.md` before
narrating it.** The act's Cd 0.3041 is the **79,439-cell (refinement 3)**
production mesh. The A4 ladder record's 0.3219 is the **45,753-cell
(refinement 2)** baseline — the same case, one rung down the act's own
grid-refinement ladder, and reproduced by the act itself at 0.0898 planform.
They do not disagree; the ladder's own band (±0.072 on frontal Cd) is five
times the gap. Two things must **not** be said over this footage: A4's
**10.04%** figure (an adjoint-vs-FD gradient check on a separate 2,777-cell
mesh, graded CONDITIONAL — not a drag number), and **0.2510** (A4's DAFoam
primal, withdrawn). The act's own SOLVER-BACKED verdict — "inconclusive
refinement study, not enough to call it validated" — is correct and should be
kept.
