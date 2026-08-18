import json, os, re, sys, numpy as np
D = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/certonomous-runs/S1-fiml/ramp_kw"
plan = json.load(open(os.path.join(D, "fdpts/fd_plan.json")))
def J(name):
    p = os.path.join(D, "fdlogs", name + ".log")
    if not os.path.exists(p): return None
    m = re.findall(r"OBJ UFieldVar: ([-0-9.eE+]+)", open(p).read())
    return float(m[-1]) if m else None

ja, jb = J("base_a"), J("base_b")
print("=== reproducibility control (two identical fresh runs) ===")
print("  base_a = %.16e" % ja); print("  base_b = %.16e" % jb)
print("  |diff| = %.3e   relative = %.3e" % (abs(ja-jb), abs(ja-jb)/abs(ja)))

gn = plan["grad_norm"]; gr = plan["dir_rand_dot"]
print("\n=== DIRECTIONAL FD (the real-objective-seed test) ===")
print("%-14s %-8s %-22s %-22s %10s" % ("direction","h","FD","adjoint (g.d)","rel err %"))
rows=[]
for kind, adj, lbl in (("dirg", gn, "grad dir (REAL)"), ("dirr", gr, "random dir")):
    for h in (1e-3, 1e-4):
        t = "%g" % h
        jp, jm = J("%s_p_%s" % (kind, t)), J("%s_m_%s" % (kind, t))
        if jp is None or jm is None: continue
        fd = (jp - jm) / (2*h)
        err = abs(fd-adj)/abs(adj)*100
        sgn = "" if np.sign(fd)==np.sign(adj) else "  <-- SIGN FLIP"
        print("%-14s %-8s %-22.12e %-22.12e %9.4f%s" % (lbl, t, fd, adj, err, sgn))
        rows.append((lbl,h,fd,adj,err))

print("\n=== COMPONENT FD ===")
print("%-8s %-8s %-22s %-22s %10s" % ("cell","h","FD","adjoint g[i]","rel err %"))
for h in (1e-2, 1e-3):
    t = "%g" % h
    for i in plan["picks"]:
        jp, jm = J("comp%d_p_%s" % (i,t)), J("comp%d_m_%s" % (i,t))
        if jp is None or jm is None: continue
        fd = (jp-jm)/(2*h); adj = plan["comp_adj"][str(i)]
        if abs(adj) < 1e-11:
            print("%-8d %-8s %-22.12e %-22.12e %10s" % (i,t,fd,adj,"(adj~0)")); continue
        err = abs(fd-adj)/abs(adj)*100
        sgn = "" if np.sign(fd)==np.sign(adj) else "  <-- SIGN FLIP"
        print("%-8d %-8s %-22.12e %-22.12e %9.4f%s" % (i,t,fd,adj,err,sgn))
