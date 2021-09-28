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

This is an incomplete list of areas where **weighted-intervals** could or
should be improved.

## Bugs

### The interface is not responsive enough.

The web version reruns the algorithm and replots the visualization whenever the
user make a change to the input &ldquo;All intervals&rdquo;
textarea&mdash;after waiting 200 milliseconds, to maintain responsive typing.

That wait, even though it is only a fifth of a second, is less gratifying than
an immediate change. At the same time, and more seriously, for problems of
several hundred intervals or more, at least in some browsers on some systems,
the time to update is much longer than 200 ms. Then characters entered into the
textarea appear slowly, which is frustrating.

It seems the slowest step is plotting the intervals. As a stopgap measure,
there could be a checkbox to disable that. It would be nice to figure out a way
to make the plotting significantly faster.

But the real, most important solution here is to allow the user keep entering
input even once the computation has started, and to cancel the computation,
either if the input describes a different problem instance or always. (The
latter should be easier and also sufficient.)

### The plot doesn&rsquo;t show the intervals&rsquo; weights.

The text-based output shows solution intervals&rsquo; start times, finish
times, and weights. But the weights do not appear in the visualization.

Users might not always want the intervals to have weight labels in the plot,
because of the increased visual noise when there are many intervals. But I
think this should at least be an option.

### The Python code should be separated into multiple modules.

As [detailed in `README.md`](README.md#how-this-program-works), currently all
the Python code is in a single module. The reason is that, in the web version,
the way I&rsquo;m loading the Python code into the WebAssembly CPython
interpreter provided by Pyodide runs it in the calling module. With multiple
modules, this situation would be confusion, even if there were no name clashes.

This can be fixed, though I&rsquo;m hoping there&rsquo;s an alternative to
making a wheel and shipping it in the repository (and making sure to recreate
it every time there is a change). I&rsquo;m willing to do that if necessary.

It&rsquo;s not that the single `.py` file is excessively long at this time.
Rather, having it all in one module makes it harder to identify, and to just
read, the code for the algorithm, which I consider undesirable.

## Missing Features

### Variations on the algorithm should be supported.

The user should be able to specify the algorithm used for the topological sort.
This can affect which solutions is found, when there is more than one optimal
subset.

Currently, I&rsquo;m using [Kahn&rsquo;s
algorithm](https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm)
with a queue (FIFO). It would be nice also to support recursive DFS with a
reliable error message on stack overflow (which should be possible *in the web
version* as it is running in a separate interpreter), DFS implemented
iteratively with a state machine (which emits vertices in the same order),
Kahn&rsquo;s algorithm with a stack (LIFO), and Kahn&rsquo;s algorithm
implemented recursively (this is an unusual way to implement Kahn&rsquo;s
algorithm but it can be done&mdash;it recurses from each of the DAG&rsquo;s
original roots).

### Kleinberg & Tardos&rsquo;s algorithm should be supported, too.

In addition to supporting my *O(n<sup>2</sup>)* algorithm with a choice of
topological sort algorithm as detailed above, it would be nice also to support
the faster dynamic programming algorithm. The main reason to do so would be to
showcase, and better elucidate the connection to, their algorithm. It would
also allow users to compare results between algorithms, which can be different
when there is more than one correct solution.

*If* visualization were also made
to run much faster, than it is possible that runs would be noticeable faster
with that algorithm, too.

### The plot should be customizable.

At least the plot&rsquo;s color scheme should be customizable. It might be
worth having the size and spacing customizable too.

### The plot is not interactive.

It would be nice if the plot were interactive, with numerical information about
an interval appearing somewhere when the user hovers their mouse over an
interval. (It would be good to facilitate keyboard interactivity too, for
greater accessibility than with a mouse alone.)

Likewise, it would be nice if the user could resize the plot, zoom, scroll, and
so forth.

But making the plot interactive might not be worth doing in the current design.
Iodide, of which Pyodide originated as a part, does this, at least to some
degree.

### The plot should be faster.

I&rsquo;m not sure how to make the plot faster, other than by marshaling the
information to create it from Python to JavaScript and using a JavaScript
library. But it would be nice.

*If successful*, such a change would also likely improve
[responsiveness](#the-interface-is-not-responsive-enough) and facilitate [plot
interaction](#the-plot-is-not-interactive).

### [The DAG](ALGORITHM.md#build-a-forward-compatibility-DAG) should also be visualized.

I tried drawing the DAG using NetworkX (which Pyodide conveniently supplies, as
it does Matplotlib), but this was too slow. I also did not figure out a way to
draw it with NetworkX that visualized it intuitively, though I think that is
probably possible. It should appear roughly linearized in order to make sense
to the user; roots should not be in the center.

This is another feature that might require more work to be done outside the
WASM-ported CPython interpreter in order to perform well.

(If Kleinberg & Tardos&rsquo;s algorithm is supported in the future, as
suggested above, there would be no corresponding DAG shown for that.)
