Reference values and pass bands parsed at run time out of `docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`, Sections 2.3 and 2.4, and re-derived independently from the primary ERCOFTAC Case 079 data files in `../reference-data/betts_bokhari/`.  
Reference tier: PRIMARY EXPERIMENTAL DATA (the database's own files; the paper is paywalled and was not read).  
Deviation is graded on the FINE mesh of the mandatory pair; the COARSE mesh is carried in every row.

| Ra | quantity | reference | coarse mesh | FINE mesh | **deviation** | band | unit | verdict |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0.86e6 | core stratification S (bound) | 0 | 0.2287 | 0.2209 | **0.2209** | 0.07 | absolute | FAIL |
| 0.86e6 | mid-height peak upward velocity (magnitude) | 0.14 | 0.1631 | 0.1623 | **15.9352** | 15 | percent | FAIL |
| 0.86e6 | mid-height peak upward velocity (location) | 71.2 | 71.2925 | 71.0035 | **0.1965** | 5 | mm | PASS |
| 0.86e6 | mid-height peak downward velocity (magnitude) | -0.135 | -0.1631 | -0.1623 | **20.2253** | 15 | percent | FAIL |
| 0.86e6 | mid-height peak downward velocity (location) | 6.2 | 4.7075 | 4.9965 | **1.2035** | 5 | mm | PASS |
| 0.86e6 | mid-width temperature at y/H = 0.30 | 25.07 | 23.8308 | 23.8623 | **1.2077** | 1 | K | FAIL |
| 0.86e6 | mid-width temperature at y/H = 0.50 | 25.26 | 24.7704 | 24.7703 | **0.4897** | 1 | K | PASS |
| 0.86e6 | mid-width temperature at y/H = 0.70 | 25.39 | 25.7090 | 25.6771 | **0.2871** | 1 | K | PASS |
| 0.86e6 | antisymmetry defect of the two peaks | 3.6 | 0.0026 | 0.0032 | **0.0032** | 10 | percent | PASS |
| 1.43e6 | core stratification S | 0.095 | 0.2428 | 0.2353 | **0.1403** | 0.05 | absolute | FAIL |
| 1.43e6 | mid-height peak upward velocity (magnitude) | 0.19 | 0.2226 | 0.2211 | **16.3758** | 15 | percent | FAIL |
| 1.43e6 | mid-height peak upward velocity (location) | 70.2 | 71.2925 | 71.6499 | **1.4499** | 5 | mm | PASS |
| 1.43e6 | mid-height peak downward velocity (magnitude) | -0.189 | -0.2227 | -0.2211 | **16.9980** | 15 | percent | FAIL |
| 1.43e6 | mid-height peak downward velocity (location) | 5 | 4.7075 | 4.3501 | **0.6499** | 5 | mm | PASS |
| 1.43e6 | mid-width temperature at y/H = 0.30 | 34.58 | 32.4863 | 32.5511 | **2.0289** | 2 | K | FAIL |
| 1.43e6 | mid-width temperature at y/H = 0.50 | 34.74 | 34.5099 | 34.5132 | **0.2268** | 2 | K | PASS |
| 1.43e6 | mid-width temperature at y/H = 0.70 | 36.02 | 36.5391 | 36.4808 | **0.4608** | 2 | K | PASS |
| 1.43e6 | antisymmetry defect of the two peaks | 0.5 | 0.0748 | 0.0055 | **0.0055** | 10 | percent | PASS |

**GATE FAIL** -- 8 of 18 graded rows failed.
