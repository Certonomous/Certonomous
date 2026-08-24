# Thermal Buildup Directive

**Sanaa's directive, recorded verbatim 2026-08-22 by the T-family supervisor.**

Recorded, not paraphrased. The blockquote below is the directive as issued; the
ledger beneath it is this lane's report of what state each item is in, and
nothing in the ledger amends the directive.

---

## The directive

> "THERMAL BUILDUP DIRECTIVE (DC-cooling is the destination; capacity priority behind only R4's CPU-minutes)
>
> H-1. Sanaa's pulls, named: Vogel & Eaton (1985) unblocks T3's gate rows tonight — that's the single highest-leverage PDF on the board. Confirm T5's primary status in the same report.
>
> H-2. The DC spine gets priority inside the T-family: T3 (separated thermal) → T5 (heated cubes = the rack physic) → T8 (plume/stratification = the aisle physic) → T12 (room-scale validation) → K2 rack row. Everything else interleaves; this chain is the product path.
>
> H-3. T10a follow-through, two arms: (a) the ceiling miss gets a refinement arm (discretization finding, cheap); (b) the view-factor quadrature defect gets the characterization treatment (mesh-family sweep, geometry sweep, reproducer from clean case) and joins the upstream queue as candidate #4 — filing remains Sanaa's call.
>
> H-4. T9a's 2.4 mK interface miss: diagnosis arm (interface scheme vs mesh vs property jump), one change per run.
>
> H-5. Tier completion order after the spine: T4 impinging jet (the band-containment flagship — now sharpened by the shelf-D finding: test whether eigenspace bands contain the documented stagnation-Nu bias), T6 Rayleigh–Bénard scaling, T7 mixed-convection map, T2 tube bank, T9b/c conjugate, T10b combined convection+radiation cavity, T11 transients.
>
> H-6. Every thermal gate feeds the DC certificate spec: as each rung passes, its quantity class (inlet T, recirculation, stratification height, transient response) gets its line in the ASHRAE certificate template, so the product artifact grows with the validation instead of after it.
>
> H-7. Two institutionalizations from tonight: the bands-vs-corrections caveat into the charters verbatim; and the libs lesson as law — a defect class that bit three call sites gets an assert at every call site, never a paragraph in a report. Sweep for remaining unasserted call sites of the same libs defect."

---

## Execution ledger (2026-08-22)

Verdict vocabulary only: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.**

| item | owner | state |
| --- | --- | --- |
| **H-1 (a) Vogel & Eaton 1985** | T-family supervisor | **NOT on disk as of 2026-08-22.** Searched `docs/papers/` (all subdirectories), `docs/campaigns/T-family/reference-data/`, and repo-wide by filename and by tracked path; zero hits on `vogel` or `eaton`. The two upstream commits named in the pull, `ddd2d75b` and `c99bce64`, are other PDFs — closure and UQ papers, listed in the merge row below — and a third, `ad110f9d`, arrived during this session and is also not it. **State 2026-08-24: T3 is NOT A RESULT 4/4, ext1 COMPLETE 8/8 (`R_f` 14:53Z), now at gate (1) alone of prereg §7.1 — `R_m`/`R_f` CONVERGED, `R_c` in a limit cycle at the 80 000 cap (prereg §11's registered alternative). G2 `x_peak/H` triple CONVERGING (`p` 4.304, GCI 0.019 %) and ungradeable anyway, gate (1) firing first. Fourth mesh level (`R_m`,`R_f`,`R_ff`) PROPOSED and NOT RUN. Primary (Vogel & Eaton 1985) still NOT OBTAINED — necessary, not sufficient. Scored in `T3_EXT1_AMENDMENT.md` §15, `T3_RESULTS.md` §14.** The missing primary is necessary and not sufficient, and it is not today's binding constraint |
| **H-1 (b) T5 primary status** | T-family supervisor | **HELD.** `docs/papers/forced_convection_heat_transfer/meinders_1998_tudelft_thesis_wall_mounted_cubes.pdf`, sha256 `36c89a54…` re-verified on disk 2026-08-22, obtained under commit `4cc8c22c`. Open, title-page verified, stated uncertainty 5 % mid-face / 10 % edges in local `h` |
| **H-2 spine ordering** | T-family supervisor | **Index reordered (this commit).** `T_FAMILY_INDEX.md` carries a dated ordering section; the old order is marked superseded and retained, not deleted |
| **H-3a T10a ceiling refinement arm** | T10a lane | **PENDING** — pre-registration not yet written; lane dispatched |
| **H-3b view-factor quadrature characterization** | T10a lane | **PENDING** — pre-registration not yet written; lane dispatched. Filing as upstream candidate #4 remains Sanaa's call and is not taken here |
| **H-4 T9a interface diagnosis arm** | T9a lane | **PENDING** — pre-registration not yet written; lane dispatched. One change per run is the registered constraint |
| **H-5 tier completion order** | T-family supervisor | **Queued behind the spine.** Recorded in the index ordering section; no rung in H-5 is started ahead of the spine |
| **H-6 DC certificate spec** | T-family supervisor | `docs/product/DC_CERTIFICATE_TEMPLATE.md` **created (this commit)** |
| **H-7 (a) bands-vs-corrections caveat** | T-family supervisor | **Charter §2e appended (this commit)** at the foot of `docs/charters/VERIFICATION_CHARTER.md`, version bumped 1.9 → 1.10, L-219 and L-220 quoted verbatim, zero lines moved above the clause |
| **H-7 (b) libs lesson as law** | libs lane | **done** — `scripts/foam_libs.py` + `scripts/lint_foam_libs.py`, K0cQ builder patched, K0cT continue scripts post-checked, `verification/runs/F14-cooling-ladder/K0cQ_runs/LIBS_AMENDMENT_2026-08-22.md` |

**One discrepancy recorded rather than smoothed.** H-1 asserts Vogel & Eaton
unblocks T3 "tonight". The paper is not held, so the assertion is recorded as
issued and the state is reported against it — and the reported state is not the
one this ledger first anticipated. T3 returns **NOT A RESULT 4/4 (gates (1)/(2)
of prereg §7.1: no case at 1e-6, triples DIVERGENT/OSCILLATORY); primary
(Vogel & Eaton 1985) still NOT OBTAINED — necessary, not sufficient; ext1
extension launched 2026-08-22 (`T3_EXT1_AMENDMENT.md`)**. The rows never get far
enough down §7.1 for the missing primary to be what stops them: gates (1) and
(2) fire ahead of gate (3). The primary's absence remains true and remains
disqualifying, and obtaining it is necessary and not sufficient — but it is not
today's binding constraint. The ladder is. The word **BLOCKED** is therefore
withdrawn from T3's state here in favour of what the frozen comparator returned,
rather than the comparator's word being edited to match the ledger's.

**Update 2026-08-24, and the paragraph above is left as written.** The ext1
extension it names has completed, 8 of 8, and the rung was re-graded by the same
frozen comparator: still **NOT A RESULT 4/4**. The paragraph's argument is not
weakened by the extension but sharpened by it — the rows now stop at **gate (1)
alone**, and on a single case. `R_m` and `R_f` are iteratively CONVERGED; `R_c`
sits in a limit cycle at the 80 000 cap, which `T3_PREREGISTRATION.md` §11
registered in advance as an outcome the rung reports rather than averages. One
triple, G2 `x_peak/H`, is now CONVERGING (`p` 4.304, GCI 0.019 %) and is
**NOT A RESULT anyway**, because gate (1) fires before a triple is consulted —
the gate turning a gradeable row *into* NOT A RESULT, never the reverse. So the
distance between this rung and the missing primary has grown, not shrunk: gate
(3) is further downstream than it was on 2026-08-22, and the registered response
is a fourth mesh level, **proposed and not run**. Scored in
`T3_EXT1_AMENDMENT.md` §15; evidence in `T3_RESULTS.md` §14.
