| act | gate | referent and its class | band, as the act declared it | reference | measured | deviation | verdict | artifact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cylinder vortex shedding, Re 100 | Strouhal vs Roshko-Williamson correlation | PUBLISHED CORRELATION, AND NOT THE ONE THE ACT CITES. St = 0.198(1-19.7/Re) (sdk/workflows/_exact_theory.py:260). Roshko 1954, NACA TR-1191 p. 11 eq (2a) gives St = 0.212(1-21.2/Re) for 50<R<150, which is the range Re 100 sits in; neither 0.198 nor 19.7 occurs anywhere in that report (docs/papers/roshko_1954_naca_tr_1191.txt) | gate 0.70% | 0.1590 | 0.1578 | 0.77% | PASS | `mission-output/cylinder-vortex-shedding/transcript.md` |
| Supersonic wedge, M 2.0, 15 deg | Oblique-shock angle vs theta-beta-M relation | EXACT THEORY. theta-beta-M relation, own solver checked against NASA GRC oblshk.f | none declared by the act; graded here against the table's own +/-5% screen (scripts/gate_table.py:_tolerance_verdict) | 45.344 | 44.693 | 1.44% | PASS | `mission-output/supersonic-wedge/transcript.md` |
| Supersonic cone, M 2.35, 10 deg | Conical shock angle vs Taylor-Maccoll | EXACT THEORY. Taylor-Maccoll, own shooting solver | none declared by the act; graded here against the table's own +/-5% screen (scripts/gate_table.py:_tolerance_verdict) | 26.737 | 27.309 | 2.14% | PASS | `mission-output/supersonic-cone/transcript.md` |
| Diamond airfoil, M 2.0, 7.125 deg | Wave drag vs shock-expansion theory | EXACT THEORY. shock-expansion theory, cross-checked against Ackeret | none declared by the act; graded here against the table's own +/-5% screen (scripts/gate_table.py:_tolerance_verdict) | 0.03633 | 0.03624 | 0.26% | PASS | `mission-output/diamond-airfoil/transcript.md` |
| Hypersonic cylinder, M 8 | Shock standoff vs Billig correlation | PUBLISHED CORRELATION. Billig 1967 via Anderson, Hypersonic and High-Temperature Gas Dynamics, Eq. 5.37 | none declared by the act; graded here against the table's own +/-5% screen (scripts/gate_table.py:_tolerance_verdict) | 0.4152 | 0.4181 | 0.70% | PASS | `mission-output/hypersonic-cylinder/transcript.md` |
| Ahmed body, 25 deg slant | Drag vs Ahmed/Ramm/Faltin SAE 840300 (frontal basis) | PUBLISHED EXPERIMENT, EXTRACTION ROUTE NOT RECORDED. Ahmed, Ramm and Faltin 1984, SAE 840300. No record states which table, figure or page Cd 0.285 came from (models/curriculum/ahmed_25/reference.yaml, one commit 5336dd57) | acceptance band ±15% | Cd 0.285 | Cd 0.3041 | 6.7% | see record | `mission-output/ahmed-body/transcript.txt` |
| NASA wall-mounted hump | Separation / reattachment x/c vs NASA experiment | PUBLISHED EXPERIMENT. NASA Turbulence Modeling Resource, 2D wall-mounted hump validation case; noflow_cp.exp.dat / noflow_cf.exp.dat fetched and retained | separation gate ±5%; reattachment model-form band ±20% | sep 0.665, reatt 1.100 | sep 0.6544, reatt 1.2534 | -1.6% / +13.9% | VALIDATED | `mission-output/nasa-hump/transcript.txt` |
| ONERA M6 wing | Primal residual vs its own tolerance (intended gate, Cp at 7 spanwise stations vs AGARD AR-138, NOT evaluated) | SELF-REFERENTIAL, AND IT SAYS SO. the primal's own residual tolerance. The external gate, Cp at 7 spanwise stations vs AGARD AR-138, was NOT evaluated | primal residual gate 1e-08 | 1e-08 | 1.02e-06 | did not satisfy | UNCONVERGED | `mission-output/onera-m6/transcript.txt` |
| CRM wing-body | Drag vs DAFoam CRM_Wing tutorial, Cd 0.02090 +/-2% | ANOTHER SOLVER, CODE-TO-CODE. DAFoam's own CRM_Wing tutorial documentation, same code, same downloaded mesh, same unmodified daOptions. sdk/chief_engineer/lab.py:182 and :224-225 reserve VALIDATED for a published experiment; the chip on this row is assigned at sdk/workflows/crm_wingbody.py:330 without passing through that path | gate ±2% | 0.0209 | 0.020901 | +0.007% | VALIDATED | `mission-output/crm-wingbody/transcript.txt` |

9 of 9 acts have run; 9 carry a graded number.
A verdict here carries the thing it was checked against and the band it was checked to, per VERIFICATION_CHARTER.md 6a. Where the band column says none was declared, the verdict cell was decided by the table's own +/-5% screen (scripts/gate_table.py:_tolerance_verdict), which is this script's screen and not the act's.

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

**Verdict cell corrected 2026-08-14, tree at `13b965dd`.** ~~The verdict cell
on the Ahmed row read `SOLVER-BACKED`.~~ It now reads `see record`, because
that is what the artifact the row cites supports. **The tier itself has not
moved and is not in doubt**: `SOLVER-BACKED` is re-derived today by
`chief_engineer.lab.displayed_credential` from
`models/curriculum/results/ahmed_25.json`, is what
`demo-output/website/wall/wall.json` carries for `ahmed_25`, and is printed on
the act's own `mission-output/ahmed-body/certificate.pdf` as
"Fidelity: SOLVER-BACKED". What is not true is that the CITED artifact states
it. `mission-output/ahmed-body/transcript.txt` carries no tier line at all:
its conclusion phase writes pipe-delimited rows (`Quantity ... | Verdict
Pass`), and `scripts/gate_table.py:_verdict_line` looks for the act's own
one-word tier as `Verdict: <tier>.`, which appears nowhere in that file — so
the generator falls through to `see record` and the published cell disagreed
with the artifact under it. This column publishes what the cited artifact
states and nothing else; the tier is on the record named above. Found by
self_audit `gate table vs transcripts`; the act's having stopped writing its
tier into its transcript is filed separately on the docket. The narration
guidance above is unaffected — the sentence in quotes is still the right one
to say.

---

## Two columns added 2026-08-18, tree read at `cccf7a9f`: the referent, its class, and the band

`VERIFICATION_CHARTER.md` section 6a: *"A verdict label (VALIDATED, PASS,
verified, confirmed, reproduces) carries the thing it was checked against, on
every surface it appears on. Where there is no external referent, the label
says so."* **This table is the surface two of that clause's own three worked
examples were drawn from, and it was the surface that did not carry it.** The
declarations existed; they stayed in the case records and in the act
transcripts and did not travel here. Nothing below changed a verdict, a tier or
a number. Two columns were added and they are generated, not written:
`scripts/gate_table.py` now emits `referent and its class` from a per-act table
that cites the file settling each class, and `band, as the act declared it`
**parsed back out of the act's own transcript**, because a band this generator
supplied would have been the generator's band wearing the act's name.

**Row 9, CRM wing-body, was the category error.** The row now states that its
referent is another solver, code-to-code: DAFoam's own `CRM_Wing` tutorial
documentation, the same code, the same downloaded mesh and the same unmodified
`daOptions`, agreeing to +0.007 percent. `sdk/chief_engineer/lab.py:182` defines
VALIDATED as *"graded against a published experiment and inside its band"* and
`:224-225` states *"VALIDATED is earned only against a published experiment"*.
**The chip on this row never passed through that path**: it is assigned
directly at `sdk/workflows/crm_wingbody.py:330`, in the act's own module, on a
`abs(deviation) <= GATE_TOLERANCE` test against `PUBLISHED_CD = 0.02090`. The
correct qualifier was always in the case record, `cases/dafoam/ladder-a/A6_crm_wingbody.md`
line 154 onwards, which calls the act *"essentially an exact reproduction of
the tutorial's own stated result"* and *"**not** evidence about DPW-VI
wing-body drag-prediction accuracy"*. It now travels. **The chip itself was not
removed, because a verdict change is the owner's**; filed on the docket.

**Row 7, NASA wall-mounted hump, had a band all along.** The published claim
that no band existed is half right and the half that is wrong matters. No band
was printed **here**, and that is now repaired. But the act pre-registered two,
in its own `[What would falsify this, fixed before the solve]` block, before
the solve: `mission-output/nasa-hump/transcript.txt:14-17` commits a separation
station of x/c 0.665 falsified outside x/c 0.632 to 0.698 (a plus or minus 5
percent gate), and a reattachment station of x/c 1.100 falsified outside x/c
0.880 to 1.320, *"plus or minus 20 percent of the published station ... the
documented closure bias"*. Measured reattachment 1.2534 is +13.9 percent, which
is inside plus or minus 20 percent, and **a miss past x/c 1.320 would have
crossed it.** So the row is a gate that could have failed and did not, rather
than a chip with no threshold under it. `docs/VALIDATION_INVENTORY.md` row 7
and section 7.2 say *"no threshold exists that a larger miss would have
crossed"*; that sentence is corrected by the artifact, and the reason the sweep
could not see it is its own section 1.3, which states that the raw evidence for
nearly every gate sits off-repo under a gitignored path.

**Row 6, Ahmed 25 degree, states what is missing rather than implying it is
there.** The referent is real and uniquely identified, Ahmed, Ramm and Faltin
1984, SAE 840300, and the band the act committed to is plus or minus 15
percent. What no record anywhere states is **which table, figure or page**
`cd: 0.285` came from, or how it was taken:
`models/curriculum/ahmed_25/reference.yaml` carries the number, the source and a
`confidence: high`, and `git log --follow` on it returns one commit, the initial
import `5336dd57`. The column now says so on the surface. The verdict cell is
untouched and still reads `see record`.

**Row 1, cylinder vortex shedding, is the row NACA Report 1191 settles, and it
settles it against the act.** The report was fetched from the NASA Technical
Reports Server and is retained at `docs/papers/roshko_1954_naca_tr_1191.pdf`,
SHA-256 `7f395ab8ba11f21007dc6f7a84504a2c7ce542c2ed54674d07540ce21db008b4`, 28
pages. On its printed page 11 (PDF page 13), under *"Relation of Shedding
Frequency to Drag"*, Roshko gives two Strouhal forms and states the range of
each: **(2a) `S = 0.212(1 - 21.2/R)` for `50 < R < 150`** and **(2b)
`S = 0.212(1 - 12.7/R)` for `300 < R < 2,000`**, corresponding to the
straight-line fits (1a) `F = 0.212R - 4.5` and (1b) `F = 0.212R - 2.7` plotted
in his figures 9 and 10. Re 100 falls in the stable range, so **(2a) governs,
and (2a) is the form `sdk/workflows/cylinder_vortex_shedding.py:22` already
cites.** The form the gate actually uses, `St = 0.198(1 - 19.7/Re)` at
`sdk/workflows/_exact_theory.py:260`, **is not in NACA Report 1191 in any
range**: `grep -c '0\.198\|19\.7' docs/papers/roshko_1954_naca_tr_1191.txt`
returns **0**, and the positive control on the same file and the same
instrument, `grep -c '21\.2\|0\.212'`, returns **8**, so the zero is an
absence in the report rather than a dead text layer. Against
(2a), `0.212 * (1 - 21.2/100) = 0.167056`, the act's measured 0.1578 sits at
**-5.54 percent**. Against the form used, `0.198 * (1 - 19.7/100) = 0.158994`,
it sits at -0.75 percent from the printed four-digit values and is reported as
0.77 percent from the unrounded solve. **The reference cell and the citation
name two different curves that disagree by 4.83 percent at this Reynolds
number, and the row passes against the one with no source.** Filed on the
docket; the number was not changed, because changing which correlation a
published act was graded against is a verdict change and it is the owner's.

**And the band column made a second thing visible on that row.** The act's own
gate, `mission-output/cylinder-vortex-shedding/transcript.md:5`, is *"Strouhal
number against the Roshko and Williamson correlation, **within 0.70%**"*. The
deviation printed is **0.77 percent**. The act's transcript carries no
`Verdict:` line, so `scripts/gate_table.py:_tolerance_verdict` fell through to
its own default limit of 5.0 percent and printed PASS. **Against the band the
act declared for itself, this row does not pass.** That is stated here and the
cell was left as generated, for the same reason as above. Four other rows
(wedge, cone, diamond airfoil, hypersonic cylinder) declared no band at all and
now say so, naming the generator's screen as the thing that decided them.

**One more defect, found while fetching.** The NTRS link in
`sdk/workflows/cylinder_vortex_shedding.py:22`,
`https://ntrs.nasa.gov/citations/19930091905`, **does not resolve to NACA Report
1191.** It resolves to NACA Report 828, Stowell, Schwartz and Houbolt 1945,
*"Bending and Shear Stresses Developed by the Instantaneous Arrest of the Root
of a Moving Cantilever Beam"*, confirmed both by fetching the record and by
downloading the PDF and reading its title page. Roshko's report is NTRS
`19930092207`. The comment cites a real report by name and links a different
one, and nothing in the repository was in a position to notice.
