#!/usr/bin/env python3
"""Build the CRM wing Mach 0.85 demo plot folder from what is on disk.

🔴 NO OPTIMISATION RAN. ZERO DESIGN ITERATIONS HAVE EVER COMPLETED IN THIS ITEM.
There is no CD-versus-design-iteration history, no optimised geometry and no drag
reduction. Nothing built here is labelled optimisation, optimised, before/after or
improvement, and the sidecar says why on its first screen.

What IS on disk and is plotted:
  * the VERBATIM BASELINE PRIMAL, P00 -- the published DAFoam CRM_Wing tutorial run
    exactly as shipped, converged, rc = 0;
  * the MULTIPOINT TRIM AT ITERATION ZERO, MP_R1 -- three lift targets trimmed from a
    common angle of attack; the run then died in its first adjoint;
  * the DECOMPOSITION SWEEP -- a real graded result about rank count and the
    residual floor.

Every number is read from the run's own logs and grade files at build time. Zero
solver compute; nothing is written into the run tree.
"""
import csv, hashlib, json, os, re, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_SP")
RUN = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085"
P00_LOG = os.path.join(RUN, "P00_20260913T192711Z.log")
MP_LOG = os.path.join(RUN, "MP_R1_20260913T215100Z.log")
ROLLUP = os.path.join(RUN, "DECOMP_SWEEP_ROLLUP.json")
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_plots_lib import force_history, sweep_curve, residual_history
from workflows.act_residual_frames import residual_frames

CD_PUBLISHED = 0.02090      # DAFoam's own published figure for this tutorial
CL_TARGET = 0.5             # the tutorial's lift constraint
DECOMP_GATE = 1.0e-6        # DAFoam's residual threshold, from the grade files
prov = []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def note(fig, path, tdir):
    prov.append((fig, path, tdir, sha(path)))


def wcsv(stem, header, rows):
    with open(os.path.join(HERE, stem + ".csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


# ------------------------------------------------------------------ read P00
# The log records CHECKPOINTS, not every iteration: `Time = 0, 1, 100, 200 … 2000`,
# each followed by six per-equation `initRes` lines and one CD / CL pair. 21 samples
# over 2000 iterations is what exists, so 21 samples is what is drawn -- the history
# is NOT interpolated up to 2000 points to look denser than the record is.
EQ = ("U0", "U1", "U2", "he", "nuTilda", "p")
t_now, times, cd, cl = None, [], [], []
res = {k: [] for k in EQ}
pend = {}
for ln in open(P00_LOG, errors="ignore"):
    m = re.match(r"^Time = (\d+)", ln)
    if m:
        t_now = int(m.group(1)); pend = {}
        continue
    if t_now is None:
        continue
    m = re.match(r"^(\w+) initRes: ([0-9.eE+-]+)", ln)
    if m and m.group(1) in res:
        pend[m.group(1)] = float(m.group(2))
        continue
    m = re.match(r"^CD: ([0-9.eE+-]+)", ln)
    if m:
        pend["CD"] = float(m.group(1)); continue
    m = re.match(r"^CL: ([0-9.eE+-]+)", ln)
    if m:
        pend["CL"] = float(m.group(1))
        if "CD" in pend and all(k in pend for k in EQ):
            times.append(t_now); cd.append(pend["CD"]); cl.append(pend["CL"])
            for k in EQ:
                res[k].append(pend[k])
        t_now = None
if not times:
    raise SystemExit("no checkpoints parsed from %s" % P00_LOG)
note("crm_cd_history.png", P00_LOG, str(times[-1]))

LAB = {"U0": "$U_x$", "U1": "$U_y$", "U2": "$U_z$", "he": "$h_e$",
       "nuTilda": r"$\tilde\nu$", "p": "$p$"}
force_history(os.path.join(HERE, "crm_cd_history.png"), times, series={"$C_D$": cd},
              xlabel="iteration", ylabel="$C_D$  [–]",
              limits={"published 0.02090": CD_PUBLISHED})
wcsv("crm_cd_history", ["iteration", "Cd"], list(zip(times, cd)))
force_history(os.path.join(HERE, "crm_cl_history.png"), times, series={"$C_L$": cl},
              xlabel="iteration", ylabel="$C_L$  [–]",
              limits={"target 0.500": CL_TARGET})
wcsv("crm_cl_history", ["iteration", "Cl"], list(zip(times, cl)))

for _f, _p, _n in residual_frames(HERE, "crm_residuals", times,
                                  {LAB[k]: res[k] for k in EQ},
                                  final_name="crm_residuals.png"):
    note(os.path.basename(_p), P00_LOG, str(int(_n)))
wcsv("crm_residuals", ["iteration"] + [LAB[k] for k in EQ],
     [[times[i]] + [res[k][i] for k in EQ] for i in range(len(times))])

# ------------------------------------------------------------------ read MP_R1, J0 only
# THE CONVERGED CD OF EACH TRIMMED CONDITION IS MEASURED, NOT RELAYED: the log's CD and
# CL are read as pairs and the LAST pair whose CL sits within 1e-3 of each target is
# taken. Nothing is transcribed from a message.
pairs, last_cd = [], None
for ln in open(MP_LOG, errors="ignore"):
    m = re.match(r"^CD: ([0-9.eE+-]+)", ln)
    if m:
        last_cd = float(m.group(1)); continue
    m = re.match(r"^CL: ([0-9.eE+-]+)", ln)
    if m and last_cd is not None:
        pairs.append((last_cd, float(m.group(1)))); last_cd = None
targets = [0.40, 0.50, 0.60]
trim_cd = []
for tgt in targets:
    hits = [c for c, l in pairs if abs(l - tgt) < 1.0e-3]
    if not hits:
        raise SystemExit("no converged CD found for CL target %.2f" % tgt)
    trim_cd.append(hits[-1])
J0 = 0.25 * trim_cd[0] + 0.50 * trim_cd[1] + 0.25 * trim_cd[2]
note("crm_trim_cd.png", MP_LOG, "J0")
sweep_curve(os.path.join(HERE, "crm_trim_cd.png"), targets,
            series={"$C_D$": {"y": trim_cd, "band": None}},
            xlabel="$C_L$ target  [–]", ylabel="$C_D$  [–]")
wcsv("crm_trim_cd", ["CL_target", "Cd_converged"], list(zip(targets, trim_cd)))

# the angles of attack: a common start separating onto three targets
ALPHA_START = 2.11031707
ALPHA_TRIM = [1.32496937, 2.11023869, 2.88211463]
# ASSERTED PRESENT IN THE LOG, not transcribed on trust: each angle must appear as a
# literal string in MP_R1's own output before it is drawn.
_mp_text = open(MP_LOG, errors="ignore").read()
for _a in [ALPHA_START] + ALPHA_TRIM:
    if ("%.8f" % _a) not in _mp_text:
        raise SystemExit("alpha %.8f does not appear in %s -- refusing to plot a "
                         "number the run did not print" % (_a, MP_LOG))
print("all four angles of attack asserted present in the MP_R1 log")
sweep_curve(os.path.join(HERE, "crm_trim_alpha.png"), targets,
            series={"start": {"y": [ALPHA_START] * 3, "band": None},
                    "trimmed": {"y": ALPHA_TRIM, "band": None}},
            xlabel="$C_L$ target  [–]", ylabel=r"$\alpha$  [deg]")
wcsv("crm_trim_alpha", ["CL_target", "alpha_start_deg", "alpha_trimmed_deg"],
     [[targets[i], ALPHA_START, ALPHA_TRIM[i]] for i in range(3)])

# ------------------------------------------------------------------ decomposition sweep
roll = json.load(open(ROLLUP))
note("crm_decomposition.png", ROLLUP, "-")
cells = sorted(roll["cells"], key=lambda c: c["ranks"])
ranks = [c["ranks"] for c in cells]
pos1 = [float(c["position1_max_residual"]) for c in cells]
pos2 = [float(c["position2_max_residual"]) for c in cells]
sweep_curve(os.path.join(HERE, "crm_decomposition.png"), ranks,
            series={"position 1": {"y": pos1, "band": None},
                    "position 2": {"y": pos2, "band": None}},
            xlabel="ranks  [–]", ylabel="max residual  [–]",
            limits={"threshold 1e-06": DECOMP_GATE})
wcsv("crm_decomposition",
     ["ranks", "position1_max_residual", "position2_max_residual",
      "position1_field", "position2_field", "position1_Cd", "positions_reached"],
     [[c["ranks"], c["position1_max_residual"], c["position2_max_residual"],
       c["position1_max_field"], c["position2_max_field"],
       c.get("position1_CD"), c.get("positions_reached")] for c in cells])

with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as f:
    f.write("figure\tartifact\ttime_dir\tsha256\n")
    for r in prov:
        f.write("\t".join(str(x) for x in r) + "\n")
print("P00 checkpoints: %d over %d iterations; final CD %.17f CL %.16f"
      % (len(times), times[-1], cd[-1], cl[-1]))
print("trim CD measured from the log: %s ; J0 = %.9f" % (trim_cd, J0))
print("decomposition ranks %s pos1 %s" % (ranks, pos1))
print("pngs:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
