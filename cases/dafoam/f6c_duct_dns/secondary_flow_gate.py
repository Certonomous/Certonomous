import re, numpy as np, json, sys

def read_of_vector_field(path):
    with open(path) as f:
        txt = f.read()
    # Two formats seen in this repo:
    # (a) full field file: "internalField   nonuniform List<vector> \n N \n ( ... ) ;"
    # (b) bare macro fragment (e.g. 0/U_LES): "U_LES nonuniform List<vector>\n N \n ( ... )"
    m = re.search(r'nonuniform List<vector>\s*\n(\d+)\s*\n\((.*?)\n\)\s*;?', txt, re.S)
    n = int(m.group(1))
    body = m.group(2)
    vecs = re.findall(r'\(([^()]+)\)', body)
    arr = np.array([[float(x) for x in v.split()] for v in vecs])
    assert arr.shape[0] == n, f"{arr.shape[0]} != {n}"
    return arr

def analyze(case_dir, rans_time, Ub=None):
    U_rans = read_of_vector_field(f"{case_dir}/{rans_time}/U")
    U_les  = read_of_vector_field(f"{case_dir}/0/U_LES")
    if Ub is None:
        Ub = float(np.mean(U_rans[:,0]))  # arithmetic mean of Ux over cells, approx bulk velocity
    sec_rans = np.sqrt(U_rans[:,1]**2 + U_rans[:,2]**2)
    sec_les  = np.sqrt(U_les[:,1]**2 + U_les[:,2]**2)
    result = {
        "n_cells": int(U_rans.shape[0]),
        "Ubulk_approx_ms": Ub,
        "rans_secondary_rms": float(np.sqrt(np.mean(sec_rans**2))),
        "rans_secondary_max": float(sec_rans.max()),
        "les_secondary_rms": float(np.sqrt(np.mean(sec_les**2))),
        "les_secondary_max": float(sec_les.max()),
        "rans_secondary_rms_pct_Ubulk": float(100*np.sqrt(np.mean(sec_rans**2))/Ub),
        "les_secondary_rms_pct_Ubulk": float(100*np.sqrt(np.mean(sec_les**2))/Ub),
    }
    return result

if __name__ == "__main__":
    case_dir = sys.argv[1]
    rans_time = sys.argv[2]
    r = analyze(case_dir, rans_time)
    print(json.dumps(r, indent=2))
    with open(f"{case_dir}/secondary_flow_gate.json", "w") as f:
        json.dump(r, f, indent=2)
