import numpy as np
TOL = 1.4901161193847656e-08
def getmag(v): return np.sqrt(v[0]**2+v[1]**2+v[2]**2+1e-30)
def skew(w): return np.array([[0.,-w[2],w[1]],[w[2],0.,-w[0]],[-w[1],w[0],0.]])
def Mi_shipped(v1,v2):
    magv1=getmag(v1); magv2=getmag(v2)
    axis=np.cross(v1,v2); axismag=getmag(axis)
    if axismag < TOL:
        angle=0.0; axis=np.array([1.,0.,0.])
    else:
        axis=axis/axismag; vv1=v1/magv1; vv2=v2/magv2
        arg=min(1.0,float(np.dot(vv1,vv2))); angle=np.arccos(arg)
    A=skew(axis); C=A@A
    return np.eye(3)+np.sin(angle)*A+(1.-np.cos(angle))*C

v1=np.array([0.,0.,1.]); mib=np.zeros((3,3)); mib[0,2]=1.0; d=np.array([1.,0.,0.])
def J(v2): return float(np.sum(mib*Mi_shipped(v1,v2)))

print("guard half-width in angle: %.6e rad" % np.arcsin(TOL))
print("AD (shipped reverse, branch 0) returns exactly: 0.0")
print("true derivative of the smooth map            : 1.0")
print()
print("   h          axisMag at v2+h*d    branch      FD           agrees with")
print("  ----------------------------------------------------------------------")
for h in [1e-3,1e-5,1e-7,1e-8,2e-8,1.6e-8,1.5e-8,1.4e-8,1e-9,1e-11]:
    v2p=v1+h*d; v2m=v1-h*d
    am=getmag(np.cross(v1,v2p))
    br = "guard(0)" if am < TOL else "live(1) "
    fd=(J(v2p)-J(v2m))/(2*h)
    who = "AD" if abs(fd)<1e-12 else ("truth" if abs(fd-1.0)<1e-6 else "neither")
    print(f"  {h:<10.1e} {am:<20.6e} {br}   {fd:< 14.10f} {who}")
print()
print("=== the same flat spot, but embedded in an O(1) displacement term ===")
print("(what the real warp finite-differences: rotation term + Xu displacement)")
print("   h        FD of (rotation + 1.0*displacement)   roundoff floor eps*|f|/h")
for h in [1e-6,1e-8,1e-9,1e-10]:
    def Jfull(v2, s): return J(v2) + s*float(v2[0])*1.0
    fd=(Jfull(v1+h*d,1.0)-Jfull(v1-h*d,1.0))/(2*h)
    print(f"  {h:<8.0e}  {fd:< 22.12f}  {2.2e-16/h:.2e}")
