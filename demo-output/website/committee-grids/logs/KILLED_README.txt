These four runs were launched at 4 ranks x 4 concurrent at 08:29Z and were
killed at 08:32Z, before any of them completed, because at that concurrency the
box delivered about 30 s per iteration and 200 iterations per run would have
taken over an hour and a half per group. They reached 4 to 7 iterations only.
They are NOT results and none of their numbers appears in the write-up. They
are kept only so the record shows what was launched and what was stopped.
The same variants were re-run from scratch at 14 ranks; those are the runs that
carry the finding.
Killed 2026-08-01T08:33:33Z.

The first `potinit` run (08:39-08:41Z) is also NOT a result. Its potentialFoam
pre-step aborted with "Entry 'div(div(phi,U))' not found in dictionary
stream/divSchemes" and exited 1, so the RANS solve that followed started from a
uniform freestream after all -- exactly the thing the variant existed to
change. It has been renamed INVALID_ and the variant re-run once the missing
scheme entry was added. Renamed 2026-08-01T08:45:35Z.

The first `wdpois` run (08:49Z) is also NOT a result: it aborted in 0.72 s with
"Entry 'yPsi' not found in dictionary stream/solvers" -- the Poisson wall-
distance method needs its own linear-solver entry, which the generator did not
write. Renamed INVALID_ and requeued. 2026-08-01T08:58:31Z
