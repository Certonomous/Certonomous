import json

# Kussoy & Horstman, NASA TM 101075, Table II -- "FLOW FIELD SURVEY, UPSTREAM
# BOUNDARY LAYER", measured 133 cm from the model nose (the undisturbed,
# fully-developed turbulent boundary-layer station this case's inlet is
# meant to represent). Y in cm from the wall; ratios are to the freestream
# (M=7.05) reference values already used elsewhere in this case (U_INF=1274
# m/s, T_INF=81.2K, matching Table I).
TABLE_II = [
    # Y_cm,  U/Uinf, T/Tinf
    (0.000, 0.000, 3.711),
    (0.065, 0.470, 4.600),
    (0.093, 0.601, 3.793),
    (0.120, 0.699, 3.223),
    (0.180, 0.759, 2.959),
    (0.250, 0.791, 2.760),
    (0.320, 0.822, 2.576),
    (0.390, 0.836, 2.359),
    (0.460, 0.858, 2.204),
    (0.620, 0.896, 1.862),
    (0.770, 0.929, 1.555),
    (0.940, 0.954, 1.371),
    (1.090, 0.967, 1.260),
    (1.260, 0.982, 1.192),
    (1.450, 0.986, 1.110),
    (1.640, 0.992, 1.051),
    (1.900, 0.999, 1.023),
    (2.150, 1.000, 1.007),
    (2.400, 1.000, 1.000),
    (2.700, 1.000, 1.000),
    (3.000, 1.000, 1.000),
]

R_CYL = 0.1015
U_INF = 1274.0
T_INF = 81.2


def interp(y_cm, col):
    if y_cm <= TABLE_II[0][0]:
        return TABLE_II[0][col]
    if y_cm >= TABLE_II[-1][0]:
        return TABLE_II[-1][col]
    for i in range(len(TABLE_II) - 1):
        y0, *_ = TABLE_II[i]
        y1, *_ = TABLE_II[i + 1]
        if y0 <= y_cm <= y1:
            f = (y_cm - y0) / (y1 - y0)
            v0 = TABLE_II[i][col]
            v1 = TABLE_II[i + 1][col]
            return v0 + f * (v1 - v0)
    raise RuntimeError(y_cm)


def profile(r_list):
    U_vals, T_vals = [], []
    for r in r_list:
        y_cm = (r - R_CYL) * 100.0
        uR = interp(y_cm, 1)
        tR = interp(y_cm, 2)
        U_vals.append(uR * U_INF)
        T_vals.append(tR * T_INF)
    return U_vals, T_vals


if __name__ == "__main__":
    import sys
    r_list = json.load(open(sys.argv[1]))
    U_vals, T_vals = profile(r_list)
    print("r range:", r_list[0], r_list[-1])
    print("U range:", min(U_vals), max(U_vals))
    print("T range:", min(T_vals), max(T_vals))
    json.dump({"r": r_list, "U": U_vals, "T": T_vals},
               open(sys.argv[2], "w"))
