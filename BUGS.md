<!--
  BUGS.md - job scheduling with weighted intervals (known issues list)

  Copyright (C) 2021 Eliah Kagan <degeneracypressure@gmail.com>

  Permission to use, copy, modify, and/or distribute this software for any
  purpose with or without fee is hereby granted.

  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
  REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
  AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
  INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
  LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
  OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
  PERFORMANCE OF THIS SOFTWARE.
-->

# Known Bugs & Missing Features

This is an incomplete list of areas where **weighted-intervals** should be
improved.

## Bugs

### The interface is not responsive enough.

The web version reruns the algorithm and replots the visualization whenever the
user make a change to the input &ldquo;All intervals&rdquo;
textarea&mdash;after waiting 200 milliseconds, to maintain responsive typing.

That wait, even though it is only a fifth of a second, is less gratifying than
an immediate change. At the same time, and more seriously, for problems of
several hundred intervals or more, at least in some browsers on some systems,
the time to update is much longer than 200 ms.

It seems the slowest step is plotting the intervals. As a stopgap measure,
there could be a checkbox to disable that. It would be nice to figure out a way
to make the plotting significantly faster.

But the real, most important solution here is to allow the user keep entering
input even once the computation has started, and to cancel the computation
either *(a)* if the input describes a different problem instance or *(b)*
always.

## Missing Features
