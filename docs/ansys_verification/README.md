# ansys-verification — the team's map

Created 2026-08-24 on Sanaa's directive (verbatim in the charter §1). This team
runs the Ansys Fluid Dynamics Verification Manual case by case as
pre-registered lab verdicts, in the lab's own solvers, and keeps the register
that becomes the lab's credentials.

| What | Where |
|---|---|
| Charter (directive, roster, models, reading rule, case protocol, register rules, record duty, archive inspection) | `docs/charters/ANSYS_VERIFICATION_CHARTER.md` |
| The manual — read it FIRST (supervisor and opus lanes) | `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.pdf` + `.txt` sidecar (title-page verify, rule 15) |
| The archives (untracked; canonical home is the supervisor's first ruling, D-6) | `VM2026R1_Fluids/` at the repo root (complete, 123 files, 2.5 GB); `docs/papers/verification_validation/VM2026R1_Fluids/` (dead partial, 10 files, one truncated) — see charter §9 |
| The verification team's D-6 memo | `docs/VM2026R1_FILING_ANALYSIS.md` |
| Validation register — every case run, every verdict; only PASS rows are credentials | `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` |
| Case definitions and pre-registrations | `cases/ansys_verification/<CASE>/PREREGISTRATION.md`, `.../RESULTS.md` |
| Run outputs (never beside the prose) | `verification/runs/ansys_verification/<CASE>/` |
| Team prose (curricula, memos, notes) | `docs/ansys_verification/` |
| Board section | `docs/LAB_STATE.md` `## ansys-verification` |
| Roster as data | `harness/teams.yaml` (team `ansys-verification`; lanes `ansys-lane-opus`, `ansys-lane-opus48`, `ansys-lane-haiku`) |
| Generated definitions | `.claude/agents/ansys-verification-supervisor.md`, `ansys-lane-opus.md`, `ansys-lane-opus48.md`, `ansys-lane-haiku.md` |
| Cost calibration rows at every completion | `docs/COST_CALIBRATION.md` |
| Audit of this team's verdicts | the verification team, `docs/CROSS_TEAM_GATE_AUDIT.md` |

Case ids follow the manual: `VMFL001`–`VMFL078` (Fluent), `VMFRT001`–`VMFRT007`
(Forte), `VMFLGPU` set. A case directory is named by its id, e.g.
`cases/ansys_verification/VMFL001/`.
