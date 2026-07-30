# Shooting from your laptop

Everything here was verified live on 2026-07-30. Where something is unverified
it says so.

---

## 1. Getting a picture on your laptop

The two servers already run on the EC2 box and both listen on all interfaces
(verified: `0.0.0.0:8765` and `0.0.0.0:8080`), so nothing on the box needs
changing.

Instance public IP: **16.58.201.228**

### Test this TONIGHT, not tomorrow morning

Open a browser on your laptop and go to:

    http://16.58.201.228:8765

**If the control room loads, you are done — you need no commands at all on your
laptop. Skip to section 2.**

I could not verify this from the box (the AWS CLI is not installed here, so I
cannot read the security group). The instance uses the `launch-wizard-2`
security group. If ports 8765 and 8080 were never opened in it, the page will
hang. That is the single most likely thing to go wrong tomorrow, which is why
it is worth thirty seconds tonight.

### If it does NOT load: the SSH tunnel

This works whether or not the firewall is open, and it is what I would use
anyway — the demo then runs on `localhost`, so nothing is exposed publicly and
the IP changing does not matter.

**Use Git Bash** (PowerShell also works; the difference is only the key-file
path and permissions, covered below).

```bash
ssh -i ~/.ssh/your-key.pem -L 8765:localhost:8765 -L 8080:localhost:8080 ubuntu@16.58.201.228
```

Leave that window open for the whole shoot. Then in your browser:

    http://localhost:8765     <- control room, where you type the prompts
    http://localhost:8080     <- static website

**PowerShell version** — same command, Windows-style path:

```powershell
ssh -i C:\Users\<you>\.ssh\your-key.pem -L 8765:localhost:8765 -L 8080:localhost:8080 ubuntu@16.58.201.228
```

**The one Windows gotcha:** if SSH refuses the key with
"UNPROTECTED PRIVATE KEY FILE" or "bad permissions", the file is too readable.

- In Git Bash: `chmod 600 ~/.ssh/your-key.pem`
- In PowerShell: `icacls C:\path\to\your-key.pem /inheritance:r /grant:r "$($env:USERNAME):(R)"`

### DO NOT restart the servers mid-act

Found the hard way during rehearsal: restarting the control-room server while a
mission is running kills that mission on the spot. It reports

    Mission interrupted by a service restart.

The Monte Carlo race runs about 172 seconds, so it is the one most exposed.
Start the servers before you roll and leave them alone. If you must restart,
do it between acts, never during one.

### If the servers themselves are down

Only if a page 404s or refuses. In the SSH session, on the box:

```bash
bash /home/ubuntu/Certonomous/scripts/demo_servers.sh
```

Idempotent — safe to run twice.

---

## 2. THE UPLOAD RULE — read this before you shoot

You wanted to attach the STL/OBJ files. You can: the control room has a
**"Load a surface (STL / OBJ)"** button under the prompt box. It accepts
`.stl` and `.obj` up to 200 MB, and parses the file the moment it lands, so a
bad file is refused immediately instead of failing halfway through a mesh.
Verified end to end today: a 712-triangle NACA0012 uploaded, parsed, and came
back with its bounding box.

**The rule, and it matters:**

> Attach the file with the BUTTON. Do NOT type the filename into the prompt.

Typing a filename like `naca0012_wing.stl` into the prompt text **changes which
act runs**. The Monte Carlo race becomes a generic geometry study. The button
and the prompt travel separately: the button says *which body*, the prompt says
*what question*. Naming a file in the prompt overrides the question.

Verified today:

| what you do | what actually runs |
|---|---|
| upload NACA + type the plain race prompt | **race comparison, on your wing** — correct |
| type `...on naca0012_wing.stl` instead | geometry study — **wrong act** |
| upload airliner wing + plain airliner prompt | aircraft optimization, your wing as the start |
| upload B-52 + plain B-52 prompt | geometry study on the B-52 — correct, that IS the act |

Four acts keep their own identity when you attach a surface: the **airliner
optimization**, the **Monte Carlo race**, the **valve study**, and the **shape
optimization**. Everything else with a file attached becomes a geometry study.

### An upload used to leak into the acts that followed it — fixed

Worth knowing, because it would have been invisible on camera. An uploaded
surface never cleared: after you uploaded `b52.stl`, **every later mission in
that tab silently carried the B-52**. Your NASA hump act would have run as a
generic geometry study on a bomber, and nothing on screen would have said why.

The surface is now released when a mission launches and the panel visibly
resets. Fixed and verified on 2026-07-30. You do not have to do anything, but if
you ever see an act announce a body you did not just attach, that is the symptom
to recognise.

### On durations

Every duration in this guide was measured on this box, and they move with how
busy the machine is — the same act measured 17 s on a quiet box and 26 s under
heavy load. Nothing else about the act changes; only the wall clock. If you are
timing narration tightly, run the act once on the day and trust that number over
this page.

### Where the files are

On the box, in `/home/ubuntu/Certonomous/demo-surfaces/`. **Copy these to your
laptop before the shoot** — you upload from the laptop, not the box:

```bash
scp -i ~/.ssh/your-key.pem ubuntu@16.58.201.228:/home/ubuntu/Certonomous/demo-surfaces/* ./
```

That gives you `b52.stl`, `naca0012_wing.stl`, `naca0015_sail.stl`,
`naca4412_wing.stl`, and `motorBike.obj`.

The larger surfaces (CRM wing-body, ONERA M6, airliner wing) live in
`/home/ubuntu/Certonomous/sdk/geometry/` — same `scp`, different directory, if
you want those too.

---

## 3. The acts you asked for

All typed into the control room prompt box.

### Airliner — unchanged, reshoot as-is

Upload `airliner_wing_span52.stl` (optional; the act runs without it).

> Optimize the L/D of an airliner for 300 passengers, 6000 km range.

**~12 s measured** (the old 17 s figure was stale). The compute numbers it shows
are **read live** — no rebuild needed, it will pick up the current figures on
the day. As of now the lab ledger stands at **208,102 solver evaluations** and
**239.3 core-hours**.

### Monte Carlo race vs reduced-order — unchanged

Upload `naca0012_wing.stl` with the button, then type **only**:

> Race a Monte Carlo uncertainty study against a reduced-order model.

**Rehearsed end to end on 2026-07-30 and measured at 172 s** (+/- 1.3 s over
four runs) — upload, launch, 88 Monte-Carlo samples, complete, certificate
issued. The uploaded wing was confirmed present in the mission's own event log,
so the file genuinely drives the run rather than decorating it.

This is the longest act. Plan your talking track around three minutes.

**The numbers no longer move between takes.** They used to: the Monte Carlo lane
seeded its draw from the clock, so the peak, the band and the agreement shifted
on every run. The seed is now fixed and stated on the record. It still solves 93
wings live and every clock on screen is genuinely measured — only the *randomness*
was pinned, which is ordinary practice for a Monte Carlo study.

What you can now rely on saying: **peak L/D 18.08 +/- 0.07, reduced-order 18.14,
agreement 0.3%.** Identical every take. The one number that still moves is the
measured speedup (17.0x to 17.5x), which is exactly the number that *should*
move, because it is a live timing.

### B-52 — unchanged act, updated numbers

Upload `b52.stl` with the button, then:

> Solve the external aerodynamics of the supplied B-52 geometry.

**~27 s measured**, upload included (the old 51 s figure was stale).

### NASA wall-mounted hump

> Solve the NASA wall-mounted hump and check separation and reattachment.

**~17 s measured** (the old 25 s figure was stale). Separation x/c 0.6544 vs
0.665 experiment (−1.6%); reattachment 1.2534 vs 1.100 (+13.9%). The reattachment error is the *point* of this segment — it
is a known, published RANS weakness, and our uncertainty band predicted it in
writing before the run. Talking points: `demo-output/website/campaign/D9_TALKING_POINTS.md`.

### Adjoint design optimization — READY, and it is now a design optimization you WATCH

No upload. Type:

> Cut the drag on the wing with the discrete adjoint and verify the gradient against finite differences.

The act runs in about 1 second, but it **plays for about 47 seconds on screen**.
Plan your talking track around three quarters of a minute, not one second.

**What appears on screen, in order:**

- The baseline wing.
- The finite-difference verification, all six groups. Worst is **1.71%**, which
  clears this lab's **5% pass threshold by a factor of 2.9**. Best is 0.00145%.
  Geometric constraints at machine precision. **Gate passes.**
- **The adjoint gradient painted on the wing skin** (lands ~18 s in). This is
  the shot. It is the real recorded gradient, mapped onto the surface through
  the FFD's own map.
- **The wing morphing across 48 frames** of the optimization (~20-24 s), with
  the drag trace descending step-for-step alongside it. Then a **root close-up**
  of the same morph (~27-32 s), where the section change is legible: the
  baseline is a slim near-symmetric section, the final is visibly fatter and
  cambered.
- **28.3% drag reduction at matched lift**, after **47 major iterations**.
- A separate table, *How the optimization stopped*: a 60-minute wall clock, no
  convergence statement printed, both first-order measures about an order of
  magnitude above tolerance, status **Partial**.

**Every shape on screen is at TRUE SCALE.** Nothing is exaggerated, and the act
cannot exaggerate — the scaling code was removed outright. The wing was
reconstructed by replaying the optimizer's own recorded design variables through
the same FFD map it used, verified linear to 7.4e-15. It is a replay of what the
optimizer did, not a model of it.

Real magnitudes, if anyone asks: max displacement **185.9 mm**, which is 3.72%
of the 5 m root chord; biggest twist change **-3.03 deg** at the outboard
station.

**A good beat to have ready.** The act states that it *could* have amplified the
shape by at most x1.995 before the wing passes through itself — because this
optimizer drove the wing onto its own thickness constraint, thinnest station
0.4988 against a limit of 0.5. It declined to amplify at all. If someone asks
why the change looks subtle, that is the answer, and it is a better answer than
a bigger picture would have been.

**Say:** "a real discrete adjoint, finite-difference verified, and we stopped it
on a clock before it converged — so that 28% is a partial result."

**Do not say** it converged, that it is an optimum, or that 28.3% is validated.
It is measured against our own baseline at the same lift, not a wind tunnel.
The act states all of this itself, so just let it run.

**Do not call the cylinder `shape-optimization` act adjoint.** That one is a
surrogate-gradient study — a differentiable model fitted to four solver runs.
Real design optimization, genuinely good, but a technical audience knows the
difference and the distinction is not worth losing.

Every number came from the optimizer's own iteration table and history
database, not from a summary: 28.3% reproduces as 28.275%, matched lift holds
to 0.003%, and the 60-minute box was exactly 3600 seconds. Non-convergence was
confirmed by the absence of the optimizer's own EXIT string.

### Closure challenge — READY

Put this on screen and talk over it:

    http://localhost:8080/closure.html

Built to be read on camera — 46px headline, 52px numerals, and the whole point
lands above the fold with no scrolling. It carries an **UNSUBMITTED** banner and
states in plain text that we hold no rank, because we do not.

**Every number on it was recomputed from the raw benchmark JSON, not copied
from a summary.** I re-derived them a second time myself: the round-3 mean
reproduces 0.0676 exactly, the baseline floor 0.1036, the round-2 entry 0.0741,
and the refused shortcut 0.067462. They are right.

**The 60-second track:**

> Turbulence is the last big unsolved problem in engineering fluid dynamics.
> The cheap simulation every engineer runs is systematically wrong exactly
> where it matters. This is the public benchmark that measures who can fix it:
> eight flows, one strict rule — train or validate on a test case and your
> submission is automatically withdrawn.
>
> The standard uncorrected solve scores 0.1036. Ours scores 0.0676, about 35%
> closer to reality. That is our entry of record. It is not submitted and we
> hold no rank.
>
> Here is the part worth showing. Our round-two entry scored 0.0741, and our
> own audit found that on three of the eight cases our correction was making
> things worse than doing nothing. Switching it off on those three would have
> scored 0.0675 — one line of code, ahead of third place. But we only knew
> which three because the benchmark had just told us. That is reading the
> answer key. Our own audit wrote at the time that taking it would invalidate
> the entry.
>
> So we left it on the table. We built a gate that looks only at the cheap
> simulation and never at the answer, fitted on 21 training cases, checked
> against 4 it had never seen. Four out of four. Then we froze it and turned it
> loose blind on the test flows. Four out of four again.
>
> Final score 0.0676 — one ten-thousandth *worse* than the shortcut we refused.
> That difference is the whole reason the number is worth anything.

**If you have longer**, the closer: we lead the board on five of eight cases,
but two of those five we "won" by our model declining to run at all, and we are
last on the ducts. We can now prove why — two of the seven inputs the model
reads are mathematically zero on every duct, so it learned nothing about them.

**If someone technical presses on the gate:** its validation AUC is 1.0, but on
n=4 with one positive label that is roughly one-in-four by luck. Say "four out
of four, twice" — true, and it does not lean on a statistic whose caveat will
not fit on screen.

**Do not claim a rank.** The page says it would sit third of five *if*
submitted, and that it currently sits nowhere.

---

## 4. On camera, safe to run

```bash
cd /home/ubuntu/Certonomous && python3 scripts/gate_table.py --filmed --md
```

Eight acts, every row citing the artifact it came from. Names in a footer the
one act it withheld, so the table never hides that it is filtered.

Drop `--filmed` for the full nine rows including the honest UNCONVERGED one —
good for a "we grade ourselves" beat, wrong mid-highlight-reel.

## 5. Camera OFF

`scripts/audit_transcripts.sh`, `scripts/verify_warm_replay.sh`,
`scripts/package_caches.sh`. Nothing wrong with them; their output is internal
housekeeping and names file paths.
