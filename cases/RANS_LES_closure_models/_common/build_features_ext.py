#!/usr/bin/env python3
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_dataset as BD, features_ext as FE
OUT = "/home/ubuntu/closure-data/tbnn/features_ext.npz"
F, names = [], []
for c, p, fam in BD.all_cases():
    f = FE.extended_features(c, p, fam)
    F.append(f); names.append(c)
    print(f"[ok] {c:24s} {f.shape} finite={np.isfinite(f).all()}", flush=True)
np.savez_compressed(OUT, F=np.concatenate(F), names=np.array(names),
                    feature_names=np.array(FE.NAMES))
print("wrote", OUT)
