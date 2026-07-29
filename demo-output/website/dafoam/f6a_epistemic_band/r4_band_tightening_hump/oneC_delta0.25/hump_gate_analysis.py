import numpy as np, json, sys

def read_raw(path, ncols):
    xs=[]; vals=[]
    with open(path) as f:
        for line in f:
            if line.startswith('#') or not line.strip(): continue
            p=line.split()
            xs.append(float(p[0]))
            vals.append([float(v) for v in p[3:3+ncols]])
    return np.array(xs), np.array(vals)

case = sys.argv[1]
time = sys.argv[2]
c = 0.42
Uinf = 34.62531106959954  # Mref*sqrt(gamma*R*Tref), from caseDef
q = 0.5*Uinf**2

x_tau, tau = read_raw(f"{case}/postProcessing/wallValues/{time}/wallShearStress_wallValues.raw", 3)
x_p, pvals = read_raw(f"{case}/postProcessing/wallValues/{time}/p_wallValues.raw", 1)

order = np.argsort(x_tau); x_tau = x_tau[order]; tau = tau[order]
order2 = np.argsort(x_p); x_p = x_p[order2]; p = pvals[order2,0]

xc_tau = x_tau / c
xc_p = x_p / c

# OpenFOAM wallShearStress convention = force-on-wall by fluid; standard skin-friction
# sign (positive = attached, flow in +x) is the negative of the x-component.
cf = -tau[:,0] / q

# Reference static pressure: mean p over the most-upstream ~5 wall points
# (x/c <~ -1.9), approximating the undisturbed upstream/freestream condition,
# consistent with how the NASA validation Cp is referenced to the upstream
# tunnel condition. Documented choice, not asserted as identical to NASA's exact method.
upstream_mask = xc_p < (xc_p.min() + 0.15)
p_ref = p[upstream_mask].mean()
cp = (p - p_ref) / q

def crossings(xc, f):
    out = []
    for i in range(len(xc)-1):
        if f[i] == 0: continue
        if np.sign(f[i]) != np.sign(f[i+1]):
            xc0 = xc[i] - f[i]*(xc[i+1]-xc[i])/(f[i+1]-f[i])
            typ = 'sep(+->-)' if f[i] > 0 else 'reattach(-->+)'
            out.append((float(xc0), typ))
    return out

cr = crossings(xc_tau, cf)
print(f"=== time={time} ===")
print("x/c range (tau):", xc_tau.min(), xc_tau.max(), "N=", len(xc_tau))
print("Cf sign crossings (x/c, type):")
for xc0, typ in cr:
    print(f"  {xc0:.4f}  {typ}")

# main separation/reattachment = the crossing pair bracketing x/c in [0.3, 1.5]
main = [cx for cx in cr if 0.3 < cx[0] < 1.6]
print("Main bubble crossings:", main)

result = {
    "time": time,
    "Uinf": Uinf,
    "q_inf": q,
    "n_wall_points": int(len(xc_tau)),
    "cf_min": float(cf.min()),
    "cf_max": float(cf.max()),
    "cp_min": float(cp.min()),
    "cp_max": float(cp.max()),
    "all_crossings": cr,
    "p_ref_upstream_mean": float(p_ref),
}
with open(f"{case}/gate_result_{time}.json", "w") as f:
    json.dump(result, f, indent=2)

# save arrays for plotting/reference
np.savetxt(f"{case}/cf_xc_{time}.csv", np.column_stack([xc_tau, cf]), header="xc,cf", delimiter=",", comments='')
np.savetxt(f"{case}/cp_xc_{time}.csv", np.column_stack([xc_p, cp]), header="xc,cp", delimiter=",", comments='')
print("Saved:", f"{case}/gate_result_{time}.json")
