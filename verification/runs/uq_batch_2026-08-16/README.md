# UQ refinement-ladder batch, 2026-08-16

Two logs from a UQ refinement-ladder batch over `naca4412_wing`, run 02:09-02:38
on 2026-08-16. They sat loose at the repository root until 2026-08-18, when the
filing charter's R1 rule (`scripts/check_filing.py`) reported them and they were
moved here. **The move is the only thing that changed; neither file was edited.**

- `uq_batch.log` — the batch transcript. Its closing line reads
  *"[02:38:58] batch finished, 4 failed stage(s)"*.
- `uq_batch.err` — one line, and it is the interesting one:
  *"57447 Floating point exception   openfoam2606 simpleFoam"*.

**No run tree for this batch was found under `verification/runs/`** (searched
2026-08-18 for `naca4412_wing` across run directories and for any `*uq*` run
directory; both returned nothing). So these logs are currently the only surviving
record of the batch, which is why they were filed rather than discarded.

**Nothing here is graded.** Four failed stages and a floating-point exception are
recorded, not diagnosed. A rung that wants to use this batch re-runs it.

These files are cited by bare name in four MOVE_MAP records under
`verification/campaign/`, and once by the root path they no longer occupy. Those
records are append-only and were not edited; this page is the forwarding address.
