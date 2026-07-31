"""Generate beta perturbation files for FD verification of the field-inversion gradient.
Central differences, fresh-process evaluation, two step sizes (step independence),
a directional test along the REAL objective gradient (not a random seed), and a
reproducibility control (two identical baseline points)."""
import numpy as np, json, os, sys
outdir = sys.argv[1]
gradfile = sys.argv[2]
beta0val = float(sys.argv[3])
os.makedirs(outdir, exist_ok=True)
g = np.load(gradfile)
n = g.size
b0 = np.ones(n) * beta0val
d = g / np.linalg.norm(g)          # REAL objective direction (the seed that matters)
rng = np.random.default_rng(12345)
r = rng.normal(size=n); r /= np.linalg.norm(r)   # random control direction

jobs = []
def emit(name, vec, meta):
    f = os.path.join(outdir, name + ".npy"); np.save(f, vec)
    jobs.append(dict(name=name, file=f, **meta))

emit("base_a", b0, {"kind": "baseline"})
emit("base_b", b0, {"kind": "baseline_repeat"})   # noise-floor control

for h in (1e-3, 1e-4):
    tag = "%g" % h
    emit("dirg_p_%s" % tag, b0 + h * d, {"kind": "dir_grad", "h": h, "sign": +1})
    emit("dirg_m_%s" % tag, b0 - h * d, {"kind": "dir_grad", "h": h, "sign": -1})
    emit("dirr_p_%s" % tag, b0 + h * r, {"kind": "dir_rand", "h": h, "sign": +1})
    emit("dirr_m_%s" % tag, b0 - h * r, {"kind": "dir_rand", "h": h, "sign": -1})

# component picks: spread across the gradient magnitude distribution
a = np.abs(g); order = np.argsort(a)
picks = [int(order[-1]), int(order[-2]), int(order[n//2]), int(order[n//4]),
         int(order[3*n//4]), int(order[5])]
for h in (1e-2, 1e-3):
    tag = "%g" % h
    for i in picks:
        for s, sn in ((+1, "p"), (-1, "m")):
            v = b0.copy(); v[i] += s * h
            emit("comp%d_%s_%s" % (i, sn, tag), v,
                 {"kind": "component", "idx": i, "h": h, "sign": s})

json.dump({"jobs": jobs, "picks": picks, "grad_norm": float(np.linalg.norm(g)),
           "dir_grad_dot": float(g @ d), "dir_rand_dot": float(g @ r),
           "comp_adj": {str(i): float(g[i]) for i in picks}},
          open(os.path.join(outdir, "fd_plan.json"), "w"), indent=2)
print("jobs:", len(jobs))
print("grad_norm (= g.d for d=g/|g|):", np.linalg.norm(g))
print("g.r (random dir):", g @ r)
for i in picks: print("  comp %5d adjoint g=%.10e" % (i, g[i]))
