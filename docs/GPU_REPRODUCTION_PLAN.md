
---

## Addendum A1 — 2026-08-24: first run graded; driver self-shutdown is a standing rule

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.**
Written 2026-08-24T16:11:46Z by the closure supervisor.

1. **Item 1 (Ling 2016) ran and is graded NOT A RESULT** on its frozen gates —
   `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/RESULTS.md`, commit
   `353925c7`; 10.7054 GPU-h actual against the 12–52 GPU-h registered range
   (ledger C-16). The §2 row for item 1 stands as written; this addendum is
   its outcome, not a rewrite.
2. **Self-shutdown is now a standing mechanism for every GPU run**, on Sanaa's
   ruling of 2026-08-24 (verbatim in `docs/GPU_CAPABILITY_STATE.md` §10). The
   frozen driver's final step — after results are written, `spend.json` is
   flushed and a completion marker the lab box can pull exists — is
   `sudo shutdown -h now`. A failure to halt must be visible: the marker and
   the shutdown-intent record are written BEFORE the call, never after.
   **Precondition, VERIFY-by-Sanaa-in-console before first reliance:** the
   instance's shutdown-behaviour attribute reads **stop**, not terminate.
3. **Standing line for every future GPU pre-registration** (drafts 2–5 inherit
   it when they are next revised; it is not edited into them retroactively):
   *"The driver ends with `sudo shutdown -h now` after writing its completion
   marker and `spend.json`; the instance's shutdown-behaviour attribute is
   VERIFY-by-Sanaa = stop; idle time between completion and halt is waste,
   reported separately."*
4. **Lesson carried:** L-267 (a rate is not an optimiser — register updates,
   not epochs) and L-268 (the completion→stop path must not need a live
   agent). Item 1's arm 2 is the first pre-registration written under both.
