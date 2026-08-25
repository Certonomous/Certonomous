# F4 checkpoint-aliasing diagnostic — 2026-08-25

**THIS GRADES NOTHING AND MOVES NO VERDICT.** F4's nine gate rows are closed at
`verification/runs/F4_runs/conversion_2026-08-25/F4_CONVERSION_GRADE.json`
(eight `NOT A RESULT`, one `CONVERGING` — `G-F4-3-M8.0`). Nothing in this
directory re-grades them, nothing here is a pre-registration, and no file in
either graded tree (`verification/runs/F4_runs/cyl/`,
`conversion_2026-08-25/runs/`) was written, moved or touched.

* `checkpoint_aliasing.py` — the diagnostic. It **imports** the frozen
  `conversion_2026-08-25/grade_f4.py` (HEAD blob `f5196143`) and calls its
  `find_shock`, `read_xy`, `control_p1` and `_plant_spike` unchanged. The frozen
  file is not edited and not copied. `grade_all` is never called, so the
  frozen grader's production-tree guard is not touched or worked around.
* `checkpoint_aliasing.json` — the output.

The reading is written up in
`verification/campaign/CFD_CONVERGENCE_GATE_CLASSIFICATION_2026-08-25.md` §3.
