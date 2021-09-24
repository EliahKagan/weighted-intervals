#!/usr/bin/env python3
"""Simple test for wi.Plotter.plot."""

import wi

WI = wi.WeightedInterval

p = wi.Plotter()

p.add(WI(10, 20, 1), False)
p.add(WI(15, 25, 2), False)
p.add(WI(20, 30, 3), True)
p.add(WI(-1, 9, 0.5), False)
p.add(WI(5, 20, 2), True)
p.add(WI(7, 12, 0.7), False)
p.add(WI(12.1, 13, 0.1), False)
p.add(WI(24, 27, 2.2), False)
p.add(WI(27.5, 29, 4), True)
p.add(WI(29, 35, 5.1), True)
p.add(WI(2, 8, 9), False)

with open('test-plotting.svg', mode='w', encoding='utf-8') as f:
    f.write(p.plot())
