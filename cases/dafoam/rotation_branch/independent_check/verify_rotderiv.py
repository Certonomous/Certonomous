import numpy as np
np.random.seed(7)

TOL = 1.4901161193847656e-08

def getmag(v):
    return np.sqrt(v[0]**2+v[1]**2+v[2]**2+1e-30)

def skew(w):
    return np.array([[0.0,-w[2],w[1]],[w[2],0.0,-w[0]],[-w[1],w[0],0.0]])

def Mi_shipped(v1,v2):
    """Verbatim transcription of getRotationMatrix3d, vectorUtils.f90:31-103."""
    magv1=getmag(v1); magv2=getmag(v2)
    axis=np.cross(v1,v2)
    axismag=getmag(axis)
    if axismag < TOL:
        angle=0.0; axis=np.array([1.0,0.0,0.0])
    else:
        axis=axis/axismag
        vv1=v1/magv1; vv2=v2/magv2
        arg=min(1.0, float(np.dot(vv1,vv2)))
        angle=np.arccos(arg)
    A=skew(axis); C=A@A
    return np.eye(3)+np.sin(angle)*A+(1.0-np.cos(angle))*C

def Mi_singfree(v1,v2):
    """Independent, singularity-free reference: R = I + [v]x + [v]x^2/(1+c), unit vectors."""
    a=v1/np.linalg.norm(v1); b=v2/np.linalg.norm(v2)
    v=np.cross(a,b); c=float(np.dot(a,b)); V=skew(v)
    return np.eye(3)+V+V@V/(1.0+c)

def claimed_v2b(v1,v2,mib):
    """The patch's claim (R): v2b += (axial(mib-mib^T) x v1)/(magv1*magv2)."""
    a=np.array([mib[2,1]-mib[1,2], mib[0,2]-mib[2,0], mib[1,0]-mib[0,1]])
    return np.cross(a,v1)/(getmag(v1)*getmag(v2))

print("--- A. reference forms agree away from degeneracy (sanity) ---")
for _ in range(3):
    a=np.random.randn(3); a/=np.linalg.norm(a)
    b=np.random.randn(3); b/=np.linalg.norm(b)
    print("   max|shipped-singfree| =", np.abs(Mi_shipped(a,b)-Mi_singfree(a,b)).max())

print()
print("--- B. shipped primal Jacobian at v2=v1 via central FD (the TRUE derivative) ---")
print("--- vs claimed (R), contracted with 20 random mib and random direction d ---")
worst=0.0
for k in range(20):
    v1=np.random.randn(3); v1/=np.linalg.norm(v1)
    v2=v1.copy()                      # the degenerate evaluation point
    mib=np.random.randn(3,3)
    d=np.random.randn(3); d/=np.linalg.norm(d)
    # J(v2) = sum(mib*Mi(v1,v2)); FD along d using the SINGULARITY-FREE reference
    # (the shipped primal is exact away from the guard, but ill-conditioned near it,
    #  so Richardson on the reference is the honest FD of the same mathematical map)
    def J(t):
        return float(np.sum(mib*Mi_singfree(v1,v2+t*d)))
    h=1e-3
    g1=(J(h)-J(-h))/(2*h); g2=(J(h/2)-J(-h/2))/h
    fd=(4*g2-g1)/3.0                  # Richardson
    an=float(np.dot(claimed_v2b(v1,v2,mib),d))
    err=abs(fd-an)/max(abs(fd),1e-300)
    worst=max(worst,err)
print("   worst relative error over 20 draws:", worst)

print()
print("--- C. is the shipped primal's OWN FD the same thing? (guard vs live) ---")
v1=np.array([0.0,0.0,1.0]); v2=v1.copy()
mib=np.zeros((3,3)); mib[0,2]=1.0
print("   hand case v1=z, mib=e_13 -> claimed v2b =", claimed_v2b(v1,v2,mib))
for h in [1e-2,1e-3,1e-4]:
    d=np.array([1.0,0.0,0.0])
    fd=(np.sum(mib*Mi_shipped(v1,v2+h*d))-np.sum(mib*Mi_shipped(v1,v2-h*d)))/(2*h)
    print(f"   shipped-primal FD along x, h={h:.0e}: {fd:.12f}")

print()
print("--- D. what the SHIPPED reverse returns at the degenerate point ---")
print("   branch 0 zeroes magv2b, axisb, axismagb and never increments v2b")
print("   -> dMi/dv2 = [0. 0. 0.]  (structural, read off vectorUtils_b.f90:123-128)")
