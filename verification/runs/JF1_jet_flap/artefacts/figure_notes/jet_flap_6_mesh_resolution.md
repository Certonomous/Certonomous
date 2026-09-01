# How well the grid resolves the two places that matter

The slot is 5.0 mm tall, one two-hundredth of the chord, and the sheet of air it releases is the whole point of the design. The other place that matters is the skin of the wing, where the drag is made. Both are counted here rather than asserted.

Panels B and C are properties of the grid and the solved flow together, so they are read from the calculation and not from the grid alone. All 200 wall cells sit below the wall-resolved limit, the largest being 0.436, so the flow next to the wall is computed rather than assumed from a formula. The near-wall spacing stopped moving well before the calculation ended: over the last 2,000 steps its largest value varies by 0.001 %. That calculation reached its step limit before it met its convergence target, so its flow field should be read as indicative.

Panel D sets two different grids beside each other in one table. They are never drawn on shared axes. Both are made only of six-sided boxes and no cell was cut or collapsed. The stretch figure is large in the outer wake because cells are deliberately long there, in the flow direction, where nothing is changing across the flow: the stretching lies along the direction being resolved.
