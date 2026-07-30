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

The Monte Carlo race runs about 194 seconds, so it is the one most exposed.
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

~17 s. The compute numbers it shows are **read live** — no rebuild needed, it
will pick up the current figures on the day. As of now the lab ledger stands at
**208,102 solver evaluations** and **239.3 core-hours**.

### Monte Carlo race vs reduced-order — unchanged

Upload `naca0012_wing.stl` with the button, then type **only**:

> Race a Monte Carlo uncertainty study against a reduced-order model.

~194 s. This is the longest act — plan your talking track around three minutes.

### B-52 — unchanged act, updated numbers

Upload `b52.stl` with the button, then:

> Solve the external aerodynamics of the supplied B-52 geometry.

~51 s.

### NASA wall-mounted hump

> Solve the NASA wall-mounted hump and check separation and reattachment.

~25 s. Separation x/c 0.6544 vs 0.665 experiment (−1.6%); reattachment 1.2534
vs 1.100 (+13.9%). The reattachment error is the *point* of this segment — it
is a known, published RANS weakness, and our uncertainty band predicted it in
writing before the run. Talking points: `demo-output/website/campaign/D9_TALKING_POINTS.md`.

### Adjoint design optimization — BEING BUILT TONIGHT

Not in the control room yet. This section will be filled in with the exact
prompt and duration when it lands.

The real material exists and passes: a discrete-adjoint wing case whose
gradient was finite-difference verified across 105 design variables with no
flagged component, then driven by IPOPT to a **28.3% drag reduction at matched
lift** over 47 major iterations. It was time-boxed at 60 minutes and stopped
short of the optimizer's own tolerance — say that on camera, it is an honest
partial result and stating it costs nothing.

**Do not describe the existing cylinder `shape-optimization` act as adjoint.**
It is a surrogate-gradient study — a differentiable model fitted to four solver
runs. Real design optimization, genuinely good, but a technical audience will
know the difference and the distinction is not worth losing.

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
