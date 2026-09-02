# SANAA-DIRECT — battery comments, second batch (2026-09-02, ~07:05Z)

## Sanaa's words, verbatim

> more battery comments : 28.7 vs 27.8 — the numbers disagree across
> surfaces. The report says "28.7 °C hottest cell at the end of the record,"
> but the monitor panel's axis tops out at 27.8 with the endpoint dot
> essentially at it. One of them is wrong (or digits transposed somewhere).
> This is exactly the kind of two-numbers-one-quantity slip an engineer
> catches — resolve it from the run's fieldMinMax file and make every
> surface print that value.
> The uncertainty line conflates two different causes. "No discretisation
> band exists for this run and none is drawn; the refused check is the
> reason" — no: the discretisation band is absent because no grid family was
> run; the refusal came from the sweep-dependence check (23.2 vs 12.3 mK).
> Two separate facts. Say: "Single grid, so no discretisation band; and the
> sweep convergence check refused certification of the values themselves."
> (The staged 6-case study fixing both is fine as-is.)
> Units mix across figures: field caption "T (K), t = 60 s" vs monitor plot
> "T (°C)" vs results in °C. Pick °C everywhere on screen.
> The requested spread is never reported. The prompt asks peak / spread /
> settle. Peak: given. Settle: honestly deferred ("longer record"). Spread:
> the hottest-and-coolest traces are on the monitor panel, so the
> as-computed spread number exists — report it with the same "as computed,
> no band" caveat, or the act visibly answers two of three without saying
> why the third is absent.
> Small: figure list prints "T at the end of takeoff" twice (same dedupe
> bug); and per your own standard the compute table (Workers | Core-min per
> run | Wall) is missing — it's a two-arm act, the table is two rows.
>
> Everything else is internally consistent: 23.2-vs-12.3 refusal ↔
> no-certificate slot ↔ "reported as computed" ↔ corrected study staged; two
> arms (10/20 sweeps) ↔ what the check compares; 19.8 vs 20.5 forecast; 900
> s ↔ "iteration 170 of 1,800" (dt 0.5 s ✓); resolved coolant ↔
> outlet-average monitor existing at all.
