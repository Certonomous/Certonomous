import numpy as np
TOL = 1.4901161193847656e-08

def getmag(v): return np.sqrt(v[0]**2+v[1]**2+v[2]**2+1e-30)
def skew(w): return np.array([[0.,-w[2],w[1]],[w[2],0.,-w[0]],[-w[1],w[0],0.]])
def cross3(v1,v2): return np.array([v1[1]*v2[2]-v1[2]*v2[1],
                                    v1[2]*v2[0]-v1[0]*v2[2],
                                    v1[0]*v2[1]-v1[1]*v2[0]])

def getmag_b(v, vb, magb):
    s = v[0]**2+v[1]**2+v[2]**2+1e-30
    tempb = 0.0 if s==0.0 else magb/(2.0*np.sqrt(s))
    vb = vb.copy(); vb += 2*v*tempb
    return vb

def cross_b(v1,v1b,v2,v2b,crossb):
    v1b=v1b.copy(); v2b=v2b.copy(); cb=crossb.copy()
    v1b[0]+= v2[1]*cb[2]-v2[2]*cb[1]
    v2b[1]+= v1[0]*cb[2]-v1[2]*cb[0]
    v1b[1]+= v2[2]*cb[0]-v2[0]*cb[2]
    v2b[0]+= v1[2]*cb[1]-v1[1]*cb[2]
    cb[2]=0.0
    v1b[2]+= v2[0]*cb[1]-v2[1]*cb[0]
    v2b[2]+= v1[1]*cb[0]-v1[0]*cb[1]
    return v1b,v2b

def getrotationmatrix3d_b(v1, v2, mib):
    """Faithful transcription of GETROTATIONMATRIX3D_B, vectorUtils_b.f90:7-154."""
    magv1=getmag(v1); magv2=getmag(v2)
    axis_raw=cross3(v1,v2); axismag=getmag(axis_raw)
    if axismag < TOL:
        angle=0.0; axis_saved=axis_raw.copy()
        axis=np.array([1.,0.,0.]); branch=0; minbranch=None; arg=None
    else:
        axis_saved=axis_raw.copy()
        axis=axis_raw/axismag
        vv1=v1/magv1; vv2=v2/magv2
        dot=vv1[0]*vv2[0]+vv1[1]*vv2[1]+vv1[2]*vv2[2]
        if 1.0>dot: arg=dot; minbranch=0
        else:       arg=1.0; minbranch=1
        angle=np.arccos(arg); branch=1
    a=skew(axis); c=a@a
    ab=np.sin(angle)*mib; cb=(1.0-np.cos(angle))*mib
    angleb=np.cos(angle)*np.sum(a*mib)+np.sin(angle)*np.sum(c*mib)
    # lines 90-122, in order
    ab[2,0]+= a[0,2]*cb[2,2]+a[0,1]*cb[2,1]+(a[0,0]+a[2,2])*cb[2,0]+a[1,2]*cb[1,0]+a[0,2]*cb[0,0]
    ab[0,2]+= a[2,0]*cb[2,2]+a[1,0]*cb[1,2]+(a[0,0]+a[2,2])*cb[0,2]+a[2,1]*cb[0,1]+a[2,0]*cb[0,0]
    ab[2,1]+= a[1,2]*cb[2,2]+(a[1,1]+a[2,2])*cb[2,1]+a[1,0]*cb[2,0]+a[1,2]*cb[1,1]+a[0,2]*cb[0,1]
    ab[1,2]+= a[2,1]*cb[2,2]+(a[1,1]+a[2,2])*cb[1,2]+a[2,1]*cb[1,1]+a[2,0]*cb[1,0]+a[0,1]*cb[0,2]
    ab[0,1]+= a[2,0]*cb[2,1]+a[1,0]*cb[1,1]+a[1,2]*cb[0,2]+(a[0,0]+a[1,1])*cb[0,1]+a[1,0]*cb[0,0]
    ab[0,0]+= a[2,0]*cb[2,0]+a[1,0]*cb[1,0]+a[0,2]*cb[0,2]+a[0,1]*cb[0,1]+2*a[0,0]*cb[0,0]
    ab[1,0]+= a[2,1]*cb[2,0]+a[0,2]*cb[1,2]+a[0,1]*cb[1,1]+(a[0,0]+a[1,1])*cb[1,0]+a[0,1]*cb[0,0]
    axisb=np.zeros(3)
    axisb[0]+= ab[2,1]-ab[1,2]
    axisb[1]+= ab[0,2]-ab[2,0]
    axisb[2]+= ab[1,0]-ab[0,1]
    v2b=np.zeros(3)
    if branch==0:
        magv2b=0.0; axisb=np.zeros(3); axismagb=0.0          # <<< lines 126-128
    else:
        argb = 0.0 if (arg==1.0 or arg==-1.0) else -(angleb/np.sqrt(1.0-arg**2))  # <<< line 133
        vv2b=np.zeros(3)
        if minbranch==0:
            vv2b += (v1/magv1)*argb
        v2b = v2b + vv2b/magv2
        magv2b = -(np.sum(v2*vv2b)/magv2**2)
        axismagb = -(np.sum(axis_saved*axisb)/axismag**2)
        axisb = axisb/axismag
    axisb = getmag_b(axis_saved, axisb, axismagb)
    v1b=np.zeros(3)
    v1b,v2b = cross_b(v1,v1b,v2,v2b,axisb)
    v2b = getmag_b(v2, v2b, magv2b)
    return v2b

def truth_v2b(v1,v2,mib):
    """Analytic reverse of the SMOOTH map, via Richardson FD of the singularity-free form."""
    def Msf(a,b):
        a=a/np.linalg.norm(a); b=b/np.linalg.norm(b)
        v=cross3(a,b); c=float(np.dot(a,b)); V=skew(v)
        return np.eye(3)+V+V@V/(1.0+c)
    g=np.zeros(3)
    for k in range(3):
        e=np.zeros(3); e[k]=1.0
        def J(t): return float(np.sum(mib*Msf(v1,v2+t*e)))
        h=1e-3
        g1=(J(h)-J(-h))/(2*h); g2=(J(h/2)-J(-h/2))/h
        g[k]=(4*g2-g1)/3.0
    return g

np.random.seed(3)
v1=np.array([0.,0.,1.]); mib=np.random.randn(3,3)
print("Shipped GETROTATIONMATRIX3D_B vs the true derivative, as a function of tilt angle.")
print("v1 = z (reference normal), v2 tilted by theta about y.  Random fixed mib.")
print()
print("  theta       branch     ||v2b_shipped||     ||v2b_true||     rel err")
print("  --------------------------------------------------------------------------")
for th in [1e-1,1e-2,1e-3,1e-4,1e-5,1e-6,1e-7,5e-8,3e-8,2e-8,1e-8,0.0]:
    v2=np.array([np.sin(th),0.,np.cos(th)])
    got=getrotationmatrix3d_b(v1,v2,mib.copy())
    tru=truth_v2b(v1,v2,mib)
    axismag=getmag(cross3(v1,v2))
    br="guard(0)" if axismag<TOL else "live(1) "
    rel=np.linalg.norm(got-tru)/max(np.linalg.norm(tru),1e-300)
    print(f"  {th:<11.0e} {br}  {np.linalg.norm(got):<18.10f} {np.linalg.norm(tru):<16.10f} {rel:.3e}")
