# motorBike website video — shotlist

Five beats, one still each, captured on the live lab (port 8770) by
`sdk/scripts/capture_motorbike_video.py`. Narration lines are the on-screen /
voice-over copy: bullet style, <=14 words, method language, no file paths, no
tool-vendor names. Every number shown is read from the real solve.

**Dependency:** the motorBike act must be green first (ACT-FIXER's D2 — the WSL
case directory is theirs). Run the capture once the act completes. Stills land
beside this file; `capture-manifest.json` records which beats fired.

---

## Beat 1 — Upload & route  (`01-upload-route.png`)
Trigger: `mission.routed`

- A surface goes in; the lab reads the objective, not a filename.
- It routes itself to a full geometry study, unprompted.
- One human touchpoint: the objective. Everything after is autonomous.

## Beat 2 — Mesh gates with real numbers  (`02-mesh-gates.png`)
Trigger: transcript line carrying `Mesh:` (cells, non-orthogonality, skewness)

- The body is meshed; quality is measured, not assumed.
- Non-orthogonality and skewness are checked against the acceptance gate.
- A mesh that fails the gate caps trust honestly.

## Beat 3 — Cp-painted body  (`03-cp-painted.png`)
Trigger: `field.ready`

- The body wears its own solved surface pressure.
- High on the leading surfaces, low over the top.
- This is the solution on the geometry, not a wireframe.

## Beat 4 — Drag + envelope  (`04-drag-envelope.png`)
Trigger: `result.verdict`

- Drag arrives with a settling confidence envelope.
- The tier is stated plainly, with the reason named.
- No claim rises above the evidence behind it.

## Beat 5 — Certificate  (`05-certificate.png`)
Trigger: `certificate.ready`

- A sealed certificate closes the mission.
- Result, uncertainty channels, and provenance seal, all in one page.
- Reproducible from the sealed evidence bundle.

---

## Capture command

```
# start YOUR server on 8770 first (see docs/DEMO_RUNBOOK.md), then:
python sdk/scripts/capture_motorbike_video.py \
    --geometry-path sdk/geometry/motorBike.obj \
    --port 8770
```

Output: `01-upload-route.png` ... `05-certificate.png` + `capture-manifest.json`
under `demo-output/website/motorbike-video/`.
