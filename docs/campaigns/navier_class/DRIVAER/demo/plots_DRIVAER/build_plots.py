#!/usr/bin/env python3
"""Build the DrivAer demo plot folder from what is on disk NOW.

Zero solver compute, and NOTHING IS WRITTEN INTO EITHER RUN TREE -- `fine_R1` is
LIVE (mpirun -np 4 simpleFoam, pid 1486309 at the time of writing) and is read only.

Sources
  coarse_R1  the Wolf Dynamics COARSE case, 669,416 cells, COMPLETE at iteration
             1000, graded PASS on G1, G2 and G3
             (verification/campaign/WOLFDYNAMICS_DRIVAER_COARSE_RESULTS.md)
  fine_R1    the Wolf Dynamics FINE case, 4,048,483 cells, RUNNING -- whatever
             iteration it had reached when this ran, recorded in the sidecar

No verdict word and no band annotation is drawn on any image; both live in
SIDECAR.md and README.md.
"""
import csv, hashlib, os, re, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/navier_class/DRIVAER/demo/plots_DRIVAER")
RUNS = "/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER"
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_plots_lib import force_history, residual_history, grid_family

# Every one of these is a transcription of a cited clause, not a choice made here.
CD_ENDPOINT = 0.291163      # prereg s.6d, their shipped coarse forceCoeffs at 1000
CD_WINDOW = 0.283631        # prereg s.6d, their own fieldAverage window 200 -> 1000
CD_TUM = 0.247              # prereg s.6, Ref.[1] EXP TUM ASME
CD_SETUP2 = 0.2426          # prereg s.6b, the setup the shipped BCs imply
CD_SETUP3 = 0.2569          # prereg s.6b, the setup their shipped fine data lands on
WINDOW = (200.0, 1000.0)    # their fieldAverage timeStart, registered verbatim
CELLS_COARSE, CELLS_FINE = 669416, 4048483

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


def forces(case):
    """Their forceCoeffs, columns resolved BY NAME from the header (prereg s.2.0)."""
    p = os.path.join(RUNS, case, "postProcessing/all/0/forceCoeffs.dat")
    hdr, rows = None, []
    for ln in open(p):
        if ln.startswith("#"):
            if "Time" in ln:
                hdr = ln.lstrip("#").split()
            continue
        c = ln.split()
        if hdr and len(c) == len(hdr):
            rows.append([float(x) for x in c])
    if hdr is None:
        raise SystemExit("no header in %s" % p)
    idx = {k: hdr.index(k) for k in ("Time", "Cd", "Cl", "Cm")}
    return p, hdr, rows, idx


# ------------------------------------------------------------------ 1. coarse Cd
p, hdr, rows, idx = forces("coarse_R1")
it = [r[idx["Time"]] for r in rows]
cd = [r[idx["Cd"]] for r in rows]
cl = [r[idx["Cl"]] for r in rows]
cm = [r[idx["Cm"]] for r in rows]
note("drivaer_cd_history.png", p, "1000")
force_history(os.path.join(HERE, "drivaer_cd_history.png"), it, series={"$C_D$": cd},
              window=WINDOW, xlabel="iteration", ylabel="$C_D$  [–]",
              title="Coarse level drag against iteration",
              limits={"their endpoint 0.291163": CD_ENDPOINT,
                      "their window mean 0.283631": CD_WINDOW,
                      "TUM experiment 0.247": CD_TUM})
wcsv("drivaer_cd_history", ["iteration", "Cd"], list(zip(it, cd)))

# ------------------------------------------------------------------ 2. coarse forces
force_history(os.path.join(HERE, "drivaer_forces.png"), it,
              series={"$C_D$": cd, "$C_L$": cl, "$C_m$": cm}, window=WINDOW,
              xlabel="iteration", ylabel="coefficient  [–]",
              title="Coarse level force coefficients")
note("drivaer_forces.png", p, "1000")
wcsv("drivaer_forces", ["iteration", "Cd", "Cl", "Cm"], list(zip(it, cd, cl, cm)))

# ------------------------------------------------------------------ 3. residuals
LOG = os.path.join(RUNS, "coarse_R1/log.solver")
pat = re.compile(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)")
rit, res, n = [], {}, 0
for ln in open(LOG, errors="ignore"):
    if ln.startswith("Time = "):
        n += 1
        for k in res:
            if len(res[k]) < n - 1:
                res[k] += [float("nan")] * (n - 1 - len(res[k]))
        rit.append(n)
        continue
    m = pat.search(ln)
    if m and n:
        k, v = m.group(1), float(m.group(2))
        res.setdefault(k, [])
        if len(res[k]) < n:
            res[k].append(v)
for k in res:
    res[k] += [float("nan")] * (n - len(res[k]))
want = [("Ux", "$U_x$"), ("Uy", "$U_y$"), ("Uz", "$U_z$"), ("p", "$p$"),
        ("k", "$k$"), ("omega", "$\\omega$")]
ser = {lab: res[k] for k, lab in want if k in res}
residual_history(os.path.join(HERE, "drivaer_residuals.png"), rit, series=ser,
                 target=1e-5, title="Coarse level initial residuals")
note("drivaer_residuals.png", LOG, "1000")
wcsv("drivaer_residuals", ["iteration"] + list(ser),
     [[rit[i]] + [ser[k][i] for k in ser] for i in range(len(rit))])

# ------------------------------------------------------------------ 4. fine, in progress
pf, hf, rf, idf = forces("fine_R1")
itf = [r[idf["Time"]] for r in rf]
cdf = [r[idf["Cd"]] for r in rf]
note("drivaer_cd_history_fine.png", pf, str(int(itf[-1])))
force_history(os.path.join(HERE, "drivaer_cd_history_fine.png"), itf,
              series={"$C_D$": cdf}, xlabel="iteration", ylabel="$C_D$  [–]",
              title="Fine level drag, run in progress",
              limits={"their shipped fine mean 0.256412": CD_SETUP3,
                      "TUM experiment 0.247": CD_TUM})
wcsv("drivaer_cd_history_fine", ["iteration", "Cd"], list(zip(itf, cdf)))

# ------------------------------------------------------------------ 5. the family
win = [c for t, c in zip(it, cd) if WINDOW[0] <= t <= WINDOW[1]]
cd_coarse = sum(win) / len(win)
tail = cdf[-100:] if len(cdf) >= 100 else cdf
cd_fine_sofar = sum(tail) / len(tail)
grid_family(os.path.join(HERE, "drivaer_family.png"),
            levels=[{"cells": CELLS_COARSE, "value": cd_coarse,
                     "label": "coarse  %s" % format(CELLS_COARSE, ",")},
                    {"cells": CELLS_FINE, "value": cd_fine_sofar,
                     "label": "fine  %s" % format(CELLS_FINE, ",")}],
            quantity="$C_D$", unit="[–]", band=(CD_SETUP2, CD_SETUP3),
            reference=CD_TUM, title="Grid family against the published band")
wcsv("drivaer_family", ["level", "cells", "Cd", "basis"],
     [["coarse", CELLS_COARSE, cd_coarse, "mean over their window 200-1000, COMPLETE"],
      ["fine", CELLS_FINE, cd_fine_sofar,
       "mean over the last %d iterations of %d, RUN IN PROGRESS" % (len(tail), int(itf[-1]))]])

with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as f:
    f.write("figure\tartifact\ttime_dir\tsha256\n")
    for r in prov:
        f.write("\t".join(str(x) for x in r) + "\n")
print("coarse: %d iterations, window mean Cd %.9f, endpoint %.12f"
      % (len(it), cd_coarse, cd[-1]))
print("fine: %d iterations so far, last Cd %.6f, last-%d mean %.6f"
      % (int(itf[-1]), cdf[-1], len(tail), cd_fine_sofar))
print("residual keys:", list(res))
print("pngs:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
