# Speed, certified — NACA 4412 finite wing race (measured)

Subject: NACA 4412 finite wing (chord 1 m, span 3 m, Re_c 1e6).
Question: peak L/D over alpha 0-10 deg, located to ±0.5 deg, with an envelope.

Every evaluation on both sides is a real VSPAERO solve. The two
envelopes mean different things: the Monte-Carlo envelope is the
stated Reynolds input uncertainty propagated through direct solves;
the reduced-order envelope is the surrogate's error measured against
one real confirmation solve. Core-minutes = solve wall-time × the
solver's 4 OpenMP threads. No choreographed delays anywhere; any
time-compression in the video must be labeled with its factor.

| pass | path | real solves | wall [s] | core-min | answer | load |
|---|---|---|---|---|---|---|
| pass1 | full Monte-Carlo | 88 | 116 | 45.4 | peak L/D 18.10 ± 0.07 at 0° | 3/14 free, load 9.32 |
| pass1 | reduced-order | 5 | 32 | 2.1 | peak L/D 18.14 at 0° (surrogate err 0.084) | 1/14 free, load 11.26 |
| pass1 | **speedup** |  |  | **21.53×** (wall 3.67×) |  |  |

For the website speed-benchmark panel (N2), from the headline pass:
- full MC: 45.4 core-min
- reduced: 2.1 core-min
- speedup: 21.53×
