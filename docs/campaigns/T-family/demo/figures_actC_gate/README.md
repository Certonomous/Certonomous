# Act C — gate screens

Three figures. **Every number on them is a convergence diagnostic, and not one
is a thermal result.**

| file | what it shows |
|---|---|
| `actC_gate_checks.pdf` | the three registered agreement checks against their limits |
| `actC_gate_over_run.pdf` | agreement between the 10-sweep and 20-sweep arms at every written frame |
| `actC_gate_sequence.pdf` | the sweep sequence 5 → 10 → 20 on the solid, at the 30 s frame |

Each carries a `.csv` beside it holding exactly the values plotted, so a reader
can check the picture against the numbers without opening the generator.

## The boundary these figures are built around

**ADMISSIBLE** — a *difference between two arms* that differ only in outer-sweep
count. `0.0232 K` is a statement about the **method**: the answer still moves
when an arbitrary iteration count is doubled. It tells a viewer nothing about
how hot anything got.

**WITHHELD** — anything that would tell a viewer how hot the module got: every
cell temperature, the rise, the outlet temperature, the acceptance criteria, the
energy ledger, and the adiabatic bounds, which would disclose the scale of the
answer by the back door.

**The mechanical form, enforced and not trusted:** every kelvin magnitude on
these screens is **below 0.1 K**. The admissible differences span 5.2e-04 to
2.4e-02 K and the limits are 1.234e-03 and 1.234e-02 K; every withheld quantity
is of order 1 K or 293 K. Two orders of separation, so the rule is decidable by
reading a number rather than by judging a sentence.
`../check_actC_gate_screen.py` enforces it, drives every rule to fire on its own
plant and to stay silent on its own negative, and asserts it actually read
numbers before reporting that it found none.

## Regenerating

```
python3 figures_actC_gate/make_actC_gate_screens.py   # figures, latexified
python3 build_actC_gate_sheet.py                      # sheet, tail verified
python3 check_actC_gate_screen.py                     # the guard
```

The generator reads the embedded font names back off each PDF and refuses
unless LaTeX really set the glyphs. An rcParam that silently falls back looks
exactly like success.
