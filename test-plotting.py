#!/usr/bin/env python3
"""Simple test for wi.Plotter.plot."""

import wi

a = wi.WeightedInterval(10, 20, 1)
b = wi.WeightedInterval(15, 25, 2)
c = wi.WeightedInterval(20, 30, 3)

p = wi.Plotter()

p.add(a, False)
p.add(b, False)
p.add(c, True)

with open('abc.svg', mode='w', encoding='utf-8') as f:
    f.write(p.plot())
