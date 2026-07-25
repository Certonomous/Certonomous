# Certonomous Innovation Standard

Version 1.0, dated 2026-07-25. Produced by the overnight reading program (R1).
Codifies, descriptively, how a new method enters this lab. The path below is
not aspirational: it is written from what the lab actually did to admit the
quasi-steady (multi-point cycle decomposition) valve method, traced through
`sdk/workflows/valve_study.py`, the `womersley` section of
`docs/physics_rules.yaml`, the Chief Researcher's closure-approval protocol
(`sdk/chief_engineer/chief_researcher.py`), and the mission lessons the valve
runs recorded.

## The path

### Stage 1. Proposal with a literature basis

A method arrives as a written proposal naming what it approximates and on
whose authority. For the valve: the Womersley number compares transient
inertia to viscous diffusion over a cycle; below alpha near 1 the profile
follows the instantaneous pressure gradient and each instant is a steady
problem (the textbook quasi-steady limit). The proposal also named what it is
not: at aortic alpha near 17 the flow is inertially unsteady, so a multi-point
decomposition could only ever be a screening approximation. Proposals now
arrive as JSONs in the agenda inbox with citations as display titles and
`source_kind` saying where the idea came from.

### Stage 2. Offline evidence on a benchmark

Before touching a surface, the method runs offline where its output can be
judged. For the valve: the decomposition screened eleven opening angles with
three steady phase points each, cycle-weighted; the ranking came out monotone
toward the widest admissible orifice, exactly what orifice physics predicts,
and the minimum-area floor still marked the tight openings infeasible. A
Monte-Carlo envelope over the flow and discharge-coefficient spreads priced
the input uncertainty. The evidence standard is behavioral: the method must
reproduce what is already known before it is trusted to say anything new.

### Stage 3. Gate criteria through the governed file

Admissibility becomes numbers in `docs/physics_rules.yaml`, never constants in
workflow code, so a ruling on camera can point to a stated criterion. For the
valve, two deliberately separated thresholds: `strict_quasi_steady_max: 1.0`
(the textbook limit where each instant is a steady problem) and
`multipoint_screening_max: 25.0` (the ceiling above which the transient jet
structure reorganizes within a cycle and a steady-per-phase picture stops
being even a useful screen). Every threshold carries its reasoning in the file
beside the number.

### Stage 4. Adoption with admissibility conditions

The method ships wearing its conditions:

- A fidelity ceiling: the valve screen is graded RESEARCH MODEL and its
  results are a ranking, never a validated pressure magnitude.
- Named model-form limitations: the analytic orifice model, dropped
  phase-interaction (history and added-mass terms), fixed leaflets, Newtonian
  blood; each is carried as a listed limitation, not absorbed into an error
  bar.
- A marked upgrade point: `_phase_pressure_loss` is the single place a real
  steady internal-flow solve plugs in, so the promotion path is executable,
  not rhetorical.
- Rulings at run time: the workflow reads the yaml thresholds and the ruling
  names the criterion; outside an envelope the Chief Researcher's answer is
  no, with orders to run coarse and state the uncertainty loudly.

### Stage 5. Lessons close the loop

Every mission using the method records what held and what stayed open through
the lessons machinery (`record_learned`), and the debriefs repeat the same
verdict the gates enforce: the angle ranking is trustworthy, the pressure
magnitude is not, and the next steps (full internal-flow plug-in,
harmonic-balance cycle solve, unsteady FSI) are named in the record.

## The rule, stated once

A new method is admitted when and only when it has: a literature basis on the
record, offline evidence on a benchmark the lab already understands, its
admissibility written as cited thresholds in the governed physics file, a
fidelity ceiling and named dropped physics at adoption, and a marked path to
the higher-fidelity version. Any method that cannot state what it drops does
not enter.

## Sources

- Valve workflow and its module docstring, `sdk/workflows/valve_study.py`.
- Governed thresholds, `docs/physics_rules.yaml`, section `womersley`.
- Closure approval protocol, `sdk/chief_engineer/chief_researcher.py`.
- Mission lessons recording the valve admissions,
  `sdk/chief-engineer-runs/mission-state/lessons`.
- Verification and Validation in Computational Fluid Dynamics, Oberkampf and
  Trucano, Sandia report SAND2002-0529, for the benchmark-first evidence
  discipline the path mirrors.
