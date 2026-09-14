#!/usr/bin/env python3
"""The six CRM act board tiles, from the MP_R2 log and the decomposition rollup.

🔴 NO DESIGN ITERATION HAS EVER COMPLETED. These are the converged ITERATION-ZERO
primals of the published transonic CRM wing at three trimmed lift conditions,
M 0.8497, 579,072 cells, baseline geometry. Nothing is labelled optimised, improved
or before/after. The optimisation itself is PENDING.

Tiles, named exactly as ordered:
    baseline_drag_three_conditions   C_D at the three lift conditions
    trimmed_alpha                    the common start and the three trimmed angles
    decomposition_study              residual floor against rank count
    cd_history                       C_D against primal iteration, per condition
    cl_history                       C_L against primal iteration, per condition
    residuals                        residual evolution, with a frame series per condition

Zero solver compute; nothing is written into the run tree.
"""
import csv, hashlib, json, os, re, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_MP")
RUN = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085"
MP_LOG = os.path.join(RUN, "MP_R2_20260914T011050Z.log")
ROLLUP = os.path.join(RUN, "DECOMP_SWEEP_ROLLUP.json")
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_plots_lib import force_history, sweep_curve
from workflows.act_residual_frames import residual_frames

CD_PUBLISHED = 0.02090          # DAFoam's published figure for this tutorial at CL 0.5
TARGETS = [0.400, 0.500, 0.600]
ALPHA_START = 2.11031707
ALPHA_TRIM = [1.32496937, 2.11023869, 2.88211463]
DECOMP_GATE = 1.0e-6
EQ = ("U0", "U1", "U2", "he", "nuTilda", "p")
LAB = {"U0": "$U_x$", "U1": "$U_y$", "U2": "$U_z$", "he": "$h_e$",
       "nuTilda": r"$\tilde\nu$", "p": "$p$"}
COND = ["cl04", "cl05", "cl06"]
prov = []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def note(fig, path, tag):
    prov.append((fig, path, tag, sha(path)))


def wcsv(stem, header, rows):
    with open(os.path.join(HERE, stem + ".csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


# ------------------------------------------------------------------ parse the six primals
# THE SEGMENTATION IS THE ITERATION COUNTER, NOT THE `Case :` HEADER. Those headers all
# sit in the log's setup section (lines 69-3179) and none appears again once the primals
# start, so splitting on them puts every checkpoint in the last case named. Splitting
# where `Time` resets to 1 gives SIX groups of 21 checkpoints -- the six converged
# primals -- and their final C_L identifies which condition each one is.
recs, t, pend = [], None, {}
for ln in open(MP_LOG, errors="ignore"):
    m = re.match(r"^Time = (\d+)", ln)
    if m:
        t = int(m.group(1)); pend = {}; continue
    if t is None:
        continue
    m = re.match(r"^(\w+) initRes: ([0-9.eE+-]+)", ln)
    if m and m.group(1) in EQ:
        pend[m.group(1)] = float(m.group(2)); continue
    m = re.match(r"^CD: ([0-9.eE+-]+)", ln)
    if m:
        pend["CD"] = float(m.group(1)); continue
    m = re.match(r"^CL: ([0-9.eE+-]+)", ln)
    if m:
        pend["CL"] = float(m.group(1))
        if "CD" in pend and all(k in pend for k in EQ):
            recs.append((t, pend["CD"], pend["CL"], {k: pend[k] for k in EQ}))
        t = None
groups, cur = [], []
for r in recs:
    if r[0] == 1 and cur:
        groups.append(cur); cur = []
    cur.append(r)
if cur:
    groups.append(cur)
if len(groups) != 6:
    raise SystemExit("expected six primals, segmented %d" % len(groups))
note("cd_history.png", MP_LOG, "six primals")

# the FIRST pass of each condition is the one the supervisor's CL column reports
first = {}
for g in groups:
    cl_end = g[-1][2]
    for tgt, name in zip(TARGETS, COND):
        if abs(cl_end - tgt) < 5.0e-4 and name not in first:
            first[name] = g
if sorted(first) != sorted(COND):
    raise SystemExit("could not identify all three conditions: %s" % sorted(first))
for name in COND:
    print("  %s: %d checkpoints, CD_final %.12f, CL_final %.10f"
          % (name, len(first[name]), first[name][-1][1], first[name][-1][2]))

SY = {"cl04": r"$C_L=0.4$", "cl05": r"$C_L=0.5$", "cl06": r"$C_L=0.6$"}
it = [r[0] for r in first["cl04"]]

# ------------------------------------------------------------------ tile: cd_history
force_history(os.path.join(HERE, "cd_history.png"), it,
              series={SY[n]: [r[1] for r in first[n]] for n in COND},
              xlabel="iteration", ylabel="$C_D$  [–]",
              limits={"published 0.02090": CD_PUBLISHED})
wcsv("cd_history", ["iteration"] + COND,
     [[it[i]] + [first[n][i][1] for n in COND] for i in range(len(it))])

# ------------------------------------------------------------------ tile: cl_history
force_history(os.path.join(HERE, "cl_history.png"), it,
              series={SY[n]: [r[2] for r in first[n]] for n in COND},
              xlabel="iteration", ylabel="$C_L$  [–]",
              limits={"target 0.400": 0.400, "target 0.500": 0.500,
                      "target 0.600": 0.600})
wcsv("cl_history", ["iteration"] + COND,
     [[it[i]] + [first[n][i][2] for n in COND] for i in range(len(it))])
note("cl_history.png", MP_LOG, "six primals")

# ------------------------------------------------------------------ tile: baseline drag
cd_final = [first[n][-1][1] for n in COND]
sweep_curve(os.path.join(HERE, "baseline_drag_three_conditions.png"), TARGETS,
            series={"$C_D$": {"y": cd_final, "band": None}},
            xlabel="$C_L$ target  [–]", ylabel="$C_D$  [–]",
            limits={"published 0.02090": CD_PUBLISHED})
wcsv("baseline_drag_three_conditions",
     ["CL_target", "Cd_converged", "CL_converged"],
     [[TARGETS[i], cd_final[i], first[COND[i]][-1][2]] for i in range(3)])
note("baseline_drag_three_conditions.png", MP_LOG, "six primals")

# ------------------------------------------------------------------ tile: trimmed alpha
# THE THREE TRIMMED ANGLES ARE ASSERTED PRESENT IN THIS LOG. The common starting
# angle 2.11031707 deg is NOT: it belongs to MP_R1 and appears zero times in MP_R2's
# output, so it is not drawn on an MP_R2 tile. A number a run did not print does not
# reach a figure, even when another run printed it.
_txt = open(MP_LOG, errors="ignore").read()
for _a in ALPHA_TRIM:
    if ("%.8f" % _a) not in _txt:
        raise SystemExit("alpha %.8f does not appear in the log" % _a)
if ("%.8f" % ALPHA_START) in _txt:
    raise SystemExit("ALPHA_START unexpectedly present; revisit the comment above")
sweep_curve(os.path.join(HERE, "trimmed_alpha.png"), TARGETS,
            series={r"$\alpha$": {"y": ALPHA_TRIM, "band": None}},
            xlabel="$C_L$ target  [–]", ylabel=r"$\alpha$  [deg]")
wcsv("trimmed_alpha", ["CL_target", "alpha_trimmed_deg"],
     [[TARGETS[i], ALPHA_TRIM[i]] for i in range(3)])
note("trimmed_alpha.png", MP_LOG, "asserted present in the log")

# ------------------------------------------------------------------ tile: decomposition
roll = json.load(open(ROLLUP))
cells = sorted(roll["cells"], key=lambda c: c["ranks"])
ranks = [c["ranks"] for c in cells]
sweep_curve(os.path.join(HERE, "decomposition_study.png"), ranks,
            series={"position 1": {"y": [float(c["position1_max_residual"]) for c in cells],
                                   "band": None},
                    "position 2": {"y": [float(c["position2_max_residual"]) for c in cells],
                                   "band": None}},
            xlabel="ranks  [–]", ylabel="max residual  [–]",
            limits={"threshold 1e-06": DECOMP_GATE})
wcsv("decomposition_study",
     ["ranks", "position1_max_residual", "position2_max_residual", "positions_reached"],
     [[c["ranks"], c["position1_max_residual"], c["position2_max_residual"],
       c.get("positions_reached")] for c in cells])
note("decomposition_study.png", ROLLUP, "-")

# ------------------------------------------------------------------ tile: residuals
for name in COND:
    g = first[name]
    ser = {LAB[k]: [r[3][k] for r in g] for k in EQ}
    fin = "residuals.png" if name == "cl05" else None
    for _f, _p, _n in residual_frames(HERE, "residuals_%s" % name,
                                      [r[0] for r in g], ser, final_name=fin):
        note(os.path.basename(_p), MP_LOG, name)
    wcsv("residuals_%s" % name, ["iteration"] + [LAB[k] for k in EQ],
         [[g[i][0]] + [g[i][3][k] for k in EQ] for i in range(len(g))])

with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as f:
    f.write("figure\tartifact\ttag\tsha256\n")
    for r in prov:
        f.write("\t".join(str(x) for x in r) + "\n")
print("pngs:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
