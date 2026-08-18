import numpy as np, json

exp = np.loadtxt('/tmp/claude-1000/-home-ubuntu-Certonomous/982d6244-5800-47f3-a450-80ce0b0a24b7/scratchpad/nasa_hump_ref/noflow_cp.exp.dat', comments=['#','variables','zone'], skiprows=4)
exp_x, exp_cp = exp[:,0], exp[:,1]

ours = np.loadtxt('/home/ubuntu/Certonomous/demo-output/website/dafoam/f6a_nasa_hump/case/cp_xc_1772.csv', delimiter=',', skiprows=1)
ox, ocp = ours[:,0], ours[:,1]

# interpolate our cp onto experimental x points within overlap
mask = (exp_x >= ox.min()) & (exp_x <= ox.max())
exp_x_ov = exp_x[mask]; exp_cp_ov = exp_cp[mask]
ocp_interp = np.interp(exp_x_ov, ox, ocp)

mae = np.mean(np.abs(ocp_interp - exp_cp_ov))
scaled_mae = mae / (exp_cp_ov.max() - exp_cp_ov.min())
print(f"N overlap points: {len(exp_x_ov)}")
print(f"Cp MAE (ours vs experiment): {mae:.4f}")
print(f"Cp range (experiment): {exp_cp_ov.min():.4f} to {exp_cp_ov.max():.4f}")
print(f"Cp scaled MAE (MAE / exp range): {scaled_mae:.4f} ({scaled_mae*100:.2f}%)")

# Also print a coarse table at key stations
stations = [-0.5, 0.0, 0.3, 0.5, 0.65, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]
print("\nx/c    Cp_ours   Cp_exp")
for s in stations:
    if ox.min()<=s<=ox.max() and exp_x.min()<=s<=exp_x.max():
        co = np.interp(s, ox, ocp)
        ce = np.interp(s, exp_x, exp_cp)
        print(f"{s:5.2f}  {co:8.4f}  {ce:8.4f}")

with open('/home/ubuntu/Certonomous/demo-output/website/dafoam/f6a_nasa_hump/case/cp_vs_experiment.json','w') as f:
    json.dump({"n_overlap": int(len(exp_x_ov)), "mae": float(mae), "exp_cp_range": [float(exp_cp_ov.min()), float(exp_cp_ov.max())], "scaled_mae_pct": float(scaled_mae*100)}, f, indent=2)
