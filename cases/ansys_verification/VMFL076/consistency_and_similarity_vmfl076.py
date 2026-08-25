import math
# ---- manual's OWN stated inputs, VM2026R1 p.219 ----
rho, mu, cp, k = 900.0, 0.01, 42.6, 142.0
Uinf, Tinf, Tw, L = 1.0, 300.0, 350.0, 1.0
nu    = mu/rho
alpha = k/(rho*cp)
Pr    = mu*cp/k
ReL   = rho*Uinf*L/mu
PeL   = ReL*Pr
Ec    = Uinf**2/(cp*abs(Tw-Tinf))
print("=== MANDATORY CONSISTENCY CHECK, from the manual's OWN p.219 inputs ===")
print("  nu    = mu/rho      = %.6g m2/s" % nu)
print("  alpha = k/(rho cp)  = %.6g m2/s" % alpha)
print("  Pr    = mu cp/k     = %.6g   <- VERY LOW; the page says 'very low Prandtl numbers,"%Pr)
print("                                    typically encountered in liquid metal flows', and the")
print("                                    reference's own title is 'EXACT LOW PRANDTL NUMBER")
print("                                    BOUNDARY-LAYER SOLUTIONS'.  CONSISTENT.")
print("  Re_L  = rho U L/mu  = %.6g   <- below the ~5e5 transition; 'laminar steady' CONSISTENT" % ReL)
print("  Pe_L  = Re_L Pr     = %.6g" % PeL)
print("  Ec    = U^2/(cp dT) = %.3e  <- viscous dissipation NEGLIGIBLE; Sparrow-Gregg forced" % Ec)
print("                                    convection carries none, so none is modelled.")
print("  alpha/nu = 1/Pr     = %.6g   -> the THERMAL layer is ~%.1fx THICKER than the momentum one"
      % (1.0/Pr, 1.0/math.sqrt(Pr)))
d_mom = 5.0/math.sqrt(ReL)
print("  delta_mom(x=L)  ~ 5/sqrt(Re_L)          = %.5g m" % d_mom)
print("  delta_th (x=L)  ~ delta_mom/sqrt(Pr)    = %.5g m   <- THE DOMAIN MUST CONTAIN THIS" % (d_mom/math.sqrt(Pr)))
print("  => EVERY driving input needed is on the page: rho, mu, cp, k, U, T_inf, T_wall, L.")

# ================= THE SIMILARITY (Sparrow-Gregg) SOLUTION =================
# Blasius:  f''' + (1/2) f f'' = 0,  f(0)=f'(0)=0, f'(inf)=1
# Energy :  th'' + (Pr/2) f th' = 0, th(0)=0, th(inf)=1,  th = (T-Tw)/(Tinf-Tw)
def blasius(fpp0, eta_max=40.0, h=1e-4):
    f, fp, fpp = 0.0, 0.0, fpp0
    n = int(eta_max/h)
    for _ in range(n):
        def d(f,fp,fpp): return (fp, fpp, -0.5*f*fpp)
        k1=d(f,fp,fpp)
        k2=d(f+h/2*k1[0], fp+h/2*k1[1], fpp+h/2*k1[2])
        k3=d(f+h/2*k2[0], fp+h/2*k2[1], fpp+h/2*k2[2])
        k4=d(f+h*k3[0],   fp+h*k3[1],   fpp+h*k3[2])
        f  += h/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0])
        fp += h/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        fpp+= h/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2])
    return fp
lo, hi = 0.1, 1.0
for _ in range(200):
    mid=(lo+hi)/2
    if blasius(mid) < 1.0: lo=mid
    else: hi=mid
FPP0=(lo+hi)/2
print()
print("=== BLASIUS, solved here by RK4 + shooting (no table consulted) ===")
print("  f''(0) = %.10f   (the classical value is 0.3320573362)" % FPP0)
if abs(FPP0-0.3320573362) > 2e-7:
    raise SystemExit("BLASIUS CONTROL FAILED: f''(0) is not the classical value")
print("  -> matches the classical Blasius constant to %.1e : THE ODE SOLVER IS CONFIRMED" % abs(FPP0-0.3320573362))

def profiles(Pr, eta_max=200.0, h=1e-3):
    """Integrate Blasius and the energy equation together on one eta grid."""
    f,fp,fpp = 0.0,0.0,FPP0
    I=0.0; etas=[0.0]; Is=[0.0]; fs=[0.0]
    n=int(eta_max/h)
    for i in range(n):
        def d(f,fp,fpp): return (fp,fpp,-0.5*f*fpp)
        k1=d(f,fp,fpp); k2=d(f+h/2*k1[0],fp+h/2*k1[1],fpp+h/2*k1[2])
        k3=d(f+h/2*k2[0],fp+h/2*k2[1],fpp+h/2*k2[2]); k4=d(f+h*k3[0],fp+h*k3[1],fpp+h*k3[2])
        f  += h/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0])
        fp += h/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        fpp+= h/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2])
        if fp>1.0: fp=1.0
        etas.append((i+1)*h); fs.append(f)
    # th'(eta) proportional to exp(-(Pr/2) int_0^eta f)
    g=[0.0]*len(etas); acc=0.0
    for i in range(1,len(etas)):
        acc += 0.5*h*(fs[i]+fs[i-1])
        g[i] = math.exp(-0.5*Pr*acc)
    g[0]=1.0
    th=[0.0]*len(etas); s=0.0
    for i in range(1,len(etas)):
        s += 0.5*h*(g[i]+g[i-1]); th[i]=s
    Tot=th[-1]
    th=[x/Tot for x in th]
    thp0 = g[0]/Tot
    return etas, th, thp0

etas, th, thp0 = profiles(Pr)
print()
print("=== SPARROW-GREGG SIMILARITY SOLUTION at the manual's Pr = %.6g ===" % Pr)
print("  theta = (T - Tw)/(Tinf - Tw),  eta = y sqrt(U/(nu x))")
print("  theta'(0) = %.10f" % thp0)
print("  Nu_x / sqrt(Re_x) = theta'(0) = %.10f" % thp0)
slug = math.sqrt(Pr/math.pi)
print("  low-Pr SLUG-FLOW asymptote sqrt(Pr/pi) = %.10f  (ratio %.6f)" % (slug, thp0/slug))
print("  -> at Pr = %.4g the exact solution sits %.3f%% from the slug limit, so the SLUG LIMIT" % (Pr, 100*abs(thp0/slug-1)))
print("     IS NOT ACCURATE ENOUGH TO GATE ON and the full similarity ODE is used instead.")
print()
print("  theta at selected eta (the gated profile):")
for e in (0.0,5.0,10.0,20.0,40.0,80.0,120.0):
    i=min(range(len(etas)), key=lambda j: abs(etas[j]-e))
    print("    eta=%6.1f  theta=%.9f   (y at x=L is %.5g m)" % (etas[i], th[i], etas[i]*math.sqrt(nu*L/Uinf)))
print()
print("  eta_99 (theta = 0.99): %.4g  -> y = %.5g m at x = L  <- domain height must exceed this"
      % (next(etas[i] for i in range(len(th)) if th[i]>=0.99),
         next(etas[i] for i in range(len(th)) if th[i]>=0.99)*math.sqrt(nu*L/Uinf)))
