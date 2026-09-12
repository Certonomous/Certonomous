# QUEUE ENTRY DRAFTS — DELIBERATELY **OUTSIDE** THE RUNNER'S SEARCH PATH

**NOTHING HERE IS QUEUED AND NOTHING HERE HAS LAUNCHED.**

`scripts/queue_runner.py` globs **`verification/queue/<team>/*.json`** (see its
`for p in sorted(d.glob("*.json"))` at `:292` and `:700`). This directory is under
`verification/runs/`, which that glob **cannot reach**. The files here are drafts for the
cfd-supervisor's check 4. Enqueuing is the act of **copying one into
`verification/queue/cfd/`**, and that is a supervisor decision, not a lane's.

Per Sanaa's directive item 19: *"The runner is the only thing that launches. Nothing launched
by hand counts as a case."* A draft that sits here cannot be launched by accident.
