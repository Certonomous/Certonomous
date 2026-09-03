# A1ZE — SUPERSEDED DRAFT. **DO NOT READ THIS AS THE REGISTRATION.**

**This draft is superseded by `A1ZE_PREREGISTRATION.md` in this directory, frozen 2026-09-03.**
It is kept, not deleted, so the corrections have something to be corrections *of*.

**Three of its statements were load-bearing and wrong.** The frozen document's §0 and §11 carry
the full register with the artifact line establishing each.

1. **Its registered prediction that removing `U2` restores convergence is FALSIFIED.** `U2` is
   not in the quantity the solver declares convergence on: D19T `T10` declared 22 times at
   ~9.04e-11 while `U2`'s best value over its whole run was 1.716383e-10, and all 14 A1WR `sweep_I`
   α points miss 1e-8 **even with `U2` excluded**. A gate on that effect would have condemned a
   correct commit for failing to do something it cannot do. Removed and split into two REPORTED
   channels.
2. **Its drift anchor (`CL` 3.310e-03 / `CD` 5.735e-04) is α = 13's**, a 26-print `SIGTERM`-
   truncated segment, not the α = 12 operating point it grades — a band 6.85× / 5.14× too wide.
   The α = 12 anchors are `CL` 4.830552e-04 / `CD` 1.116421e-04.
3. **Its cost anchors are mislabelled.** `0.5614 it/s` is **6-way**, not 8-way, and lives in
   `cold_I_4/out/sweep.log`, not in the `CHAIN_LEDGER.tsv` it cites; `2.36 it/s at 3-way` has no
   artifact anywhere and is not used by the frozen document.

Beyond those: the arms are now defined relative to HEAD (since `d3f47bfa` the templates are
`empty`, so the **control** is the mutated arm), the condemnation clause stands at both ends and
states narrowly what it condemns *for*, and the cap table is rebuilt on anchors that cite an
artifact.

**Nothing in this file is frozen and nothing in it may be cited.**
**SUBMISSIONS PARKED.**
