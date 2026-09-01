# Filename clock note (chief, 2026-09-01, box clock ~20:20Z)

Captures earlier on 2026-09-01 were named from the chief's estimated times,
which ran ~2h40m AHEAD of this box's clock (e.g. files named 2130Z-2200Z
were written when the box read ~19:00-19:30Z). From the file named
2026-09-01T2006Z onward, names come from `date -u` on this box. Therefore
FILENAME ORDER IS NOT DELIVERY ORDER across that boundary: files named
2130Z/2145Z/2200Z were captured BEFORE files named 2006Z/2010Z/2014Z.
The authoritative sequence is each capture's git commit order, not its name.
The discrepancy is the chief's naming error, not a clock fault on either
machine.
