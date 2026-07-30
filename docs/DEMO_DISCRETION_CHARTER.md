# Certonomous Demo Discretion Charter

Version 1.0, dated 2026-07-30. Standing policy, not a one-off pass over the
current acts. It governs everything a camera can see: act narration, the
control room, the closing report, certificates, plot titles and labels, and
the static pages.

The owner's requirement, in her own words: *"never give too much detail about
exactly how you got somewhere, stay vague, bc i will also show these demos to
engineers and we dont want them stealing stuff. Do not show failures in the
demos, this is all for promotion."*

## 1. The line

> **The demo may withhold METHOD. It may never misstate RESULT.**

That is the whole charter. Everything below is the working out.

Two failure modes sit on either side of that line, and only one of them is
recoverable. Saying too much costs the lab its recipe. Saying something untrue
costs the lab its credibility, which is the only asset it has. When the two
pull against each other, say less and stay true. Never the reverse.

The safety of this policy rests entirely on section 5. We are choosing not to
teach. We are not choosing to mislead.

## 2. WITHHOLD on camera

Anything that reads as a recipe a competitor could follow:

- **Solver settings and schemes.** Linear-solver choices, preconditioners and
  fill levels, restart counts, relaxation factors, Courant and CFL numbers,
  residual tolerances, discretization schemes by name.
- **Tuning parameters.** Step sizes, perturbation sizes, iteration caps chosen
  by hand, anything whose value was found rather than derived.
- **Mesh construction recipes.** How the grid was built is the most copyable
  thing in the lab: feature-edge extraction, background meshes, snapping,
  layer addition, refinement levels, extrusion steps, named meshing tools.
- **Convergence tricks.** Initialization strategies, staged startups, ramping,
  anything that exists to make a hard case start.
- **The sequence of things tried.** What was attempted first, what was
  attempted after that, what the fix turned out to be. This is method twice
  over, and it usually breaks the no-failures rule as well (section 6).
- **Library, toolchain and version specifics.** The supporting stack around
  the solver, its container, its version numbers. See the exception in
  section 4 for the solver itself.
- **Internal file paths and module names.** Repository paths, artifact
  filenames, script names, dictionary filenames, study identifiers.
- **Prompt and routing internals.** How the lab decides what to run is not
  part of any claim it makes.
- **Rank counts and decomposition.** How many processes the solve was split
  across says nothing about the answer and everything about the setup.

## 3. ALWAYS KEEP on camera

These are the claim. Vagueness about method must never become vagueness about
what was measured or how well it did.

- **The measured value.**
- **Its uncertainty band**, and the channels behind it.
- **The fidelity tier chip** (VALIDATED, SOLVER-BACKED, RESEARCH MODEL,
  UNCONVERGED).
- **What it was compared against, and that reference's identity.** The name of
  the experiment, the correlation, the publication, the benchmark, the
  standard. A comparison against an unnamed reference is not a comparison.
- **Whether the gate passed**, and what the gate was.

Nothing in this charter is ever a reason to remove one of these five. A hit
from `scripts/audit_camera_discretion.sh` that lands on one of them is a false
positive by definition, and the fix is the audit rule, not the surface.

## 4. NEVER

- State or imply a result the lab did not measure.
- Present a replay as a live measurement, or a live measurement as a replay.
- Imply validation against experiment where there was none. "Solver-backed"
  and "validated" are different words and they are not interchangeable.
- Inflate a tier, widen a gate after the fact, or quietly drop the row that
  did not clear it.
- Remove a number, a band, a tier or a reference identity in the name of
  discretion.

**The solver is named.** This is an existing standing rule and it survives
here: "Solver of choice: VSPAERO", not "a vortex-lattice method". The solver
is the credential. Its supporting toolchain is the recipe, and that stays off
camera.

**A cited standard is a reference identity, not a library mention.** "The
gates are the standard acceptance band, per OpenFOAM mesh-quality guidance"
names the published threshold the gate cites, and it stays. "Meshed with
snappyHexMesh, refinement level 3, four prism layers" is the recipe, and it
goes. The test is what the name is doing in the sentence: identifying what we
were graded against, or telling the viewer how to reproduce our setup.

## 5. The permanent record stays COMPLETE and unredacted

**This charter governs the promotional surface only.** It has no authority
anywhere else, and it is never a reason to change a record.

Complete and unredacted, always:

- `demo-output/website/campaign/`, every campaign record.
- `LESSONS.md`.
- `NOT_PASSING_REGISTER.md`.
- The solve registry and the fleet ledger.
- Certificate evidence trails and the primary logs they cite.
- The source of the acts themselves, including the comments explaining why a
  detail was withheld.

If applying this charter would require editing any of those, stop. The
requirement was misread. Withholding a detail from the narration is in scope;
deleting it from the record is falsification, and it is the one thing the
lab cannot do.

Where a value is dropped from the narration but kept in the source, say so at
the definition, so the next reader knows it was a discretion call and not an
oversight.

## 6. Cross-reference: no failures on camera

The companion rule, already in force and unchanged by this document:

- The control room is promotional and carries no failures. An act that failed
  its gate does not get filmed. The ONERA M6 act was removed from the filmed
  sequence for exactly this reason, and its UNCONVERGED result stays on the
  permanent record and in the full gate table, which is where it belongs.
- Narrating a failed attempt breaks both rules at once: it is method (the
  order things were tried) and it is a failure.

**An honest limit on a result is not a failure.** "Stopped by a 60 minute wall
clock, no convergence statement printed, so this is a partial result" is the
result stated accurately, and section 4 requires it to stay. "The optimizer
cut its step back four times on evaluation errors" is the narration of a
struggle, and section 2 removes it. The difference is whether the sentence
describes *what we got* or *what we went through*.

## 7. How to be vague without weaseling

The registered voice preference is plain, confident declarative sentences.
Discretion is exercised by **saying less**, never by saying it mushily. A
hedged sentence reads as doubt about the result, which is the one thing this
charter must never cause.

Fine, and stays:

> We solved it with the discrete adjoint and checked the gradient against
> finite differences.

A recipe, and comes out:

> We set the GMRES restart to 200 with ILU fill level 2 after the first three
> attempts diverged.

Rules of thumb:

1. **Cut the clause, not the sentence.** Most hits are a trailing qualifier.
   "Graded against 210 finite-difference primal solves at a central step of
   0.001" loses four words and keeps its whole meaning.
2. **Name the method, not its settings.** "Discrete adjoint", "central finite
   difference", "steady RANS with k-omega SST" are the physics and the
   fidelity, and they stay. Their tuning does not.
3. **Never replace a specific with a hedge.** "An interior-point optimizer"
   becomes "the optimizer", not "some optimization approach".
4. **If a sentence exists only to show the work, delete it.** Do not rewrite
   it shorter.
5. **When in doubt, ask what the sentence buys the viewer.** If the answer is
   "they could rebuild our setup", it goes. If it is "they know what we
   measured and how well it did", it stays.

## 8. Enforcement

- `scripts/audit_camera_discretion.sh`. The method half. Flags recipe-level
  disclosure across every camera surface, prints the rule and the reason with
  each hit. It is a review aid, not an auto-edit: every hit needs a human
  judgement, and false positives are expected and normal.
- `scripts/audit_transcripts.sh`. The reuse vocabulary and the machinery
  leak, plus the no-failures rule.

Run both before filming, with the camera off. A clean run is not a
certificate; a noisy run is not a failure.

Neither audit inspects a measured value, a band, a tier or a reference
identity, and neither may ever be used to remove one.

## Related

- `docs/standards/MESH_STANDARD.md`, `docs/standards/MONITOR_STANDARD.md`,
  `docs/standards/INNOVATION_STANDARD.md`: the lab's other standing
  standards.
- `docs/UNCERTAINTY-DOCTRINE.md`: what the bands mean and how they are
  computed. Nothing in this charter touches them.
- `FILMING_COMMANDS.md`: the filmed set, and the acts withheld from it.
