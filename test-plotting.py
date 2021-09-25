#!/usr/bin/env python3

# test-plotting.py - job scheduling with weighted intervals
#                    (wi.Plotter.plot test script)
#
# Copyright (C) 2021 Eliah Kagan <degeneracypressure@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

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
