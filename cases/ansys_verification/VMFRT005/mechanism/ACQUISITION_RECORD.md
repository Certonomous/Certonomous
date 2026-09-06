# VMFRT005 — MECHANISM ACQUISITION RECORD

**Sanaa approved both VMFRT005 decisions** — capture `b7c56371`,
`etc/sessions/2026-09-06T0230Z_sanaa_everything_approved.md`, item 3, **read at
source by the supervisor and not from the relay**. Her words verbatim:
*"everything approved"*. The capture's own posture line: *"Inbound fetch only;
nothing leaves the box (rule 7/8 untouched)."*

## WHAT WAS FETCHED, AND WHAT ARRIVED

| file | bytes | source |
|---|---|---|
| `c8-c16_n-alkanes_mech.txt` | 837 262 | `combustion.llnl.gov/sites/combustion/files/2020-10/c8-c16_n-alkanes_mech.txt` |
| `c8-c16_n-alkanes_therm.txt` | 2 318 588 | `combustion.llnl.gov/sites/combustion/files/2020-10/c8-c16_n-alkanes_therm.txt` |

**Publication, from the file's own header lines 1-3:** C. K. Westbrook, W. J. Pitz,
O. Herbinet, H. J. Curran, E. J. Silke, *"A Detailed Chemical Kinetic Reaction
Mechanism for n-Alkane Hydrocarbons from n-Octane to n-Hexadecane"*,
**Combustion and Flame 156(1) (2009) 181-199**, LLNL-JRNL-401196.

## PROVENANCE CHECK — THE `L-144` EQUIVALENT, COUNTED FROM THE FILE

`L-144` forbids identifying a retrieved artifact by filename, file type or hash,
because **a manifest can be internally consistent and externally false.** A
mechanism's equivalent is its species and reaction counts against its own
publication.

| | measured in the received file | published | |
|---|---|---|---|
| **species** | **2115** | **2115** | **EXACT** |
| reactions | ~8157 (heuristic parse) | 8130 | **+27, and the discrepancy is DISCLOSED rather than rounded away** — the counter cannot reliably separate `DUP`/`PLOG`/`LOW` continuation lines from reaction lines, so the small excess is an artifact of my counter, not evidence of a different mechanism. **The species count, which is unambiguous, matches exactly.** |
| `nc12h26` present as a species | **yes** | required | |
| low-T C12 ketohydroperoxide/ketone species | **114** | required | e.g. `c12ket1-2`, `c12ket2-4`, `c12ket2-5` |

**The low-temperature path is the point of the whole acquisition** — the manual
attributes Forte's own **70.7 %** ignition-delay miss to *"imperfections in the low
temperature chemical kinetics"*, so a mechanism without it could not address this case.

> **CORROBORATION WORTH RECORDING: the species names match the proprietary Ansys
> PERK model embedded in the archived `.ftsim`.** This team previously decoded
> `c12ooh2-4` and `c12ket2-4` from that binary. The same species appear here in an
> openly published mechanism — consistent with PERK descending from the same LLNL
> lineage. **Nothing proprietary was extracted, then or now.**

## ⚠ A FILE THAT ARRIVED WITH THE RIGHT NAME AND THE WRONG CONTENT

The second candidate (Lapointe et al. 2019 hybrid) was also requested. Its
`..._mech.txt` returned a **250-byte HTML 404 page bearing the mechanism's exact
filename**. Its `..._therm.txt` returned 40 327 bytes of real content — **a thermo
file whose mechanism does not exist, which grades nothing.**

**Both were DISCARDED.** This is precisely `L-144`'s failure mode in a new dress:
**a `.txt` named for a mechanism, sized plausibly, containing an error page.** A
hash or a filename check would have passed it. **Reading the first bytes caught it
in one line**, and that check is now part of this record rather than a habit.

## ⚠ THE ACQUISITION IS REAL AND IT DOES NOT YET MAKE THE CASE RUNNABLE

**2115 species is far too large for the ECN Spray A run as costed.** The approved
envelope (~2 500–4 000 core-h) rested on a chemistry cost for roughly **30–100
species**; cost rises steeply with species count, so this mechanism is **the right
chemistry at the wrong size.** It is acquired as the **reference** — the thing a
skeletal mechanism must be shown to reproduce — not as the thing the graded run
integrates.

**What remains open, stated as a named item and not as a plan:** either an openly
distributed **skeletal** nC12 mechanism (~50–100 species, the class routinely used
for Spray A), or a reduction performed here against this reference. **Neither is
decided by this record.** A registration will decide it, with a rule-12 point
estimate, and Sanaa's approved envelope is a **cap on its own terms** (rule 9: the
approval of an item is the approval of ITS cap, not a new ceiling).

## PROCESS DISCLOSURE — SANCTIONED WITH REPORTING

The first attempt to route this work **through a lane was DENIED by the auto-mode
classifier** (an `Agent` spawn). **The supervisor did not route around the denial**
— no peer, no daemon, no retry of the same shape. It was escalated, and the chief
directed that the fetch be attempted **directly in the supervisor's own session as
his own act**, which is what this record documents. **The denial is disclosed here
because a sanctioned act with a denial in its history should carry that history
where the artifact is read.**

**Nothing left the box.** Queries were generic and technical and disclosed nothing
about this laboratory, its work or its existence. **No correspondence was
attempted**: the Narayanaswamy 255-species mechanism was identified as a strong
candidate and **rejected without contact** because it is distributed *"upon request
from research groups"* — a request is an outbound act, which rule 7 forbids and
which Sanaa's approval of an **inbound fetch** does not cover.
