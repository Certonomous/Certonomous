#!/usr/bin/env python3
import re, sys, math, os
from collections import defaultdict

a = 0.05715
g = 9.81

def read_scalar(path):
    txt = open(path).read()
    m = re.search(r'internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\n\(\n(.*?)\n\)\s*;', txt, re.S)
    n = int(m.group(1))
    vals = [float(x) for x in m.group(2).split('\n')]
    assert len(vals) == n
    return vals

def read_vector(path):
    txt = open(path).read()
    m = re.search(r'internalField\s+nonuniform\s+List<vector>\s*\n(\d+)\n\(\n(.*?)\n\)\s*;', txt, re.S)
    n = int(m.group(1))
    vecs = []
    for line in m.group(2).split('\n'):
        line = line.strip().strip('()')
        vecs.append(tuple(float(x) for x in line.split()))
    assert len(vecs) == n
    return vecs

def integrated_front(alpha, C, dy, threshold_frac=0.01):
    cols = defaultdict(float)
    for i, c in enumerate(C):
        x = round(c[0], 8)
        cols[x] += alpha[i] * dy
    xs = sorted(cols.keys())
    heights = [cols[x] for x in xs]
    threshold = threshold_frac * a
    front = None
    for i in range(len(xs) - 1, 0, -1):
        if heights[i] < threshold <= heights[i-1]:
            frac = (threshold - heights[i-1]) / (heights[i] - heights[i-1]) if heights[i] != heights[i-1] else 0.0
            front = xs[i-1] + frac * (xs[i] - xs[i-1])
            break
    return front

if __name__ == "__main__":
    case_dir = sys.argv[1]
    c_path = sys.argv[2]
    dy = float(sys.argv[3])
    threshold_frac = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
    C = read_vector(c_path)
    time_dirs = []
    for d in os.listdir(case_dir):
        try:
            t = float(d)
            if t > 0:
                time_dirs.append((t, d))
        except ValueError:
            continue
    time_dirs.sort()
    print("t(s)      T          Z_integrated")
    rows = []
    for t, d in time_dirs:
        apath = os.path.join(case_dir, d, "alpha.water")
        if not os.path.exists(apath):
            continue
        alpha = read_scalar(apath)
        front = integrated_front(alpha, C, dy, threshold_frac)
        T = t * math.sqrt(g / a)
        if front is not None:
            print(f"{t:8.4f}  {T:8.4f}   {front/a:8.4f}")
            rows.append((T, front/a))
        else:
            print(f"{t:8.4f}  {T:8.4f}   NO FRONT FOUND")
    import json
    json.dump(rows, open(sys.argv[5], 'w')) if len(sys.argv) > 5 else None
