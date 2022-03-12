<!--
  README.md - job scheduling with weighted intervals (readme file)

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

# weighted-intervals - job scheduling with weighted intervals

This solves instances of the weighted interval scheduling problem and
visualizes its solutions. It shows text-based output and also plots all input
intervals, highlighting the ones that are part of the solution it found.

This is *alpha 3+* of weighted-intervals. The web version is implemented,
though there are some bugs and missing features. See [`BUGS.md`](BUGS.md). The
CLI version is not yet implemented (except in the sense that you could import
[`wi.py`](wi.py) and interact with it as you please).

[**Try weighted-intervals on the web
here.**](https://eliahkagan.github.io/weighted-intervals/)

[`ALGORITHM.md`](ALGORITHM.md) describes the algorithm I used and compares it
to other algorithms for this problem.

## License

**weighted-intervals** is written by Eliah Kagan. It is licensed under
[0BSD](https://spdx.org/licenses/0BSD.html). See [**`LICENSE`**](LICENSE).

Its [dependencies](#dependencies) are written by different authors and have
different licenses, though they are all free open-source software. Furthermore,
none of them are included in this repository&mdash;they are obtained from CDNs
(for the web version) or via [pipenv](https://github.com/pypa/pipenv) (if you
work locally and use the provided
[`Pipfile`](Pipfile)/[`Pipfile.lock`](Pipfile.lock)). So this whole repository
is offered under 0BSD.

## The Problem

Given a set of weighted intervals, where each interval&rsquo;s start time is
strictly less than its finish time, and each weight is strictly positive, the
goal is to find a subset of intervals that maximizes the sum of all the
weights. The weights are sometimes called values; their sum is known as the
total weight, or cost.

## The Algorithm

**I wrote this program to explore a particular algorithm**, which runs in
*O(n<sup>2</sup>)* time on *n* intervals. Although this algorithm is faster
than a *O(2<sup>n</sup>)* brute force check of all subsets, **it is not the
fastest algorithm**; the problem can be solved in *O(n log n)* time with
dynamic programming. It is possible that a future version of this program might
showcase multiple algorithms (which would be valuable in part because different
algorithms can pick different equally good subsets as solutions).

For information on the algorithm used, and how it relates to other algorithms,
see [`ALGORITHM.md`](ALGORITHM.md) (and docstrings in [`wi.py`](wi.py)).

## How This Program Works

*This describes how the web version of the software works, not the algorithm it
uses. In summary: a whole Python interpreter runs in your web browser, and the
interesting code is in [`wi.py`](wi.py).*

The algorithm used here could be implemented in just about any language,
including JavaScript, but I&rsquo;ve used Python, which I think is a nice
language for *expressing* algorithms to humans while still letting them run
(albeit not always as fast as in some other languages). But Python code does
not traditionally run in web browsers.

The web version of weighted-intervals uses
[Pyodide](https://pyodide.org/en/stable/) to run a Python interpreter in the
user&rsquo;s web browser. Pyodide supplies and runs a
[WebAssembly](https://webassembly.org/) port of
[CPython](https://www.python.org/).

Intervals are plotted using [Matplotlib](https://matplotlib.org/), a popular
Python library. Pyodide supplies packaged/ported versions of Matplotlib and its
dependencies.

[`wi.py`](wi.py) contains the weighted-interval scheduling implementation as
well as the visualization code. [`bridge.js`](bridge.js) uses Pyodide to run
code in [`wi.py`](wi.py) and to marshal data between Python and JavaScript.

It would be clearer&mdash;and better software engineering&mdash;to put the
algorithmic code and the visualization in separate Python modules, rather than
having both in [`wi.py`](wi.py). I haven&rsquo;t done that yet because of the
way I&rsquo;m having Pyodide load [`wi.py`](wi.py)&mdash;by downloading its
contents and executing them in the Python interpreter. This places everything
in the global namespace, unlike what happens when a module is imported. Doing
this with multiple modules would be confusing even if there are no clashes. (If
necessary, I can solve this by [packaging my Python modules in a
wheel](https://pyodide.org/en/stable/usage/loading-packages.html#installing-wheels-from-arbitrary-urls).)

Until then, if one is just interested in the algorithm implementation, one
might prefer to look at [the shorter `wi.py` from *alpha
0*](https://github.com/EliahKagan/weighted-intervals/blob/alpha-0/wi.py).

## Dependencies

The dependencies [are obtained externally](#license) rather than being included
in this repository.

**weighted-intervals** uses these libraries:

- [**Pyodide**](https://pyodide.org/en/stable/) 0.19.1, by the [Pyodide
  development team](https://pyodide.org/en/stable/project/about.html) ([Mozilla
  Public License 2.0](https://github.com/pyodide/pyodide/blob/main/LICENSE)).
  This supplies [a WebAssembly
  port](https://github.com/pyodide/pyodide/tree/main/cpython) of
  [CPython](https://www.python.org/) 3.9.5 and various libraries. All recent
  versions of [CPython itself](https://github.com/python/cpython) are [licensed
  under](https://github.com/python/cpython/blob/main/LICENSE) the [Python
  Software Foundation License 2.0](https://spdx.org/licenses/PSF-2.0.html).
- [**Matplotlib**](https://matplotlib.org/)
  [3.5.1](https://github.com/pyodide/pyodide/blob/main/packages/matplotlib/meta.yaml)
  by the Matplotlib Development Team. Matplotlib is licensed under the [License
  agreement for matplotlib versions 1.3.0 and
  later](https://github.com/matplotlib/matplotlib/blob/master/LICENSE/LICENSE).
  It includes some components by other authors with other licenses. See the
  [Matplotlib license page](https://matplotlib.org/stable/users/license.html)
  and the files in [the Matplotlib `LICENSE`
  directory](https://github.com/matplotlib/matplotlib/tree/master/LICENSE) for
  further details.
- [**normalize.css**](https://necolas.github.io/normalize.css/) 8.0.1 by
  Nicolas Gallagher and Jonathan Neal ([MIT
  License](https://github.com/necolas/normalize.css/blob/8.0.1/LICENSE.md))
- [***Fork me on GitHub* CSS
  ribbon**](https://simonwhitaker.github.io/github-fork-ribbon-css/) 0.2.3 by
  Simon Whitaker ([MIT
  License](https://github.com/simonwhitaker/github-fork-ribbon-css/blob/0.2.3/LICENSE))

And these fonts:

- [**Source Sans Pro**](https://adobe-fonts.github.io/source-sans/), designed
  by Paul D. Hunt and licensed under the [SIL OFL
  1.1](https://github.com/adobe-fonts/source-sans/blob/release/LICENSE.md)
  (&copy; Adobe, with reserved font name &ldquo;Source&rdquo;). This font is
  now called [Source Sans 3](https://github.com/adobe-fonts/source-sans) in the
  current version, but I&rsquo;m using [Source Sans
  Pro](https://fonts.google.com/specimen/Source+Sans+Pro), an earlier version.
- [**Source Code Pro**](https://adobe-fonts.github.io/source-code-pro/),
  designed by Paul D. Hunt and licensed under the [SIL OFL
  1.1](https://github.com/adobe-fonts/source-code-pro/blob/release/LICENSE.md)
  (&copy; Adobe, with reserved font name &ldquo;Source&rdquo;).

## Acknowledgements

I&rsquo;d like to thank:

- [**Professor Aparna Das**](https://web.lemoyne.edu/~dasa/), who introduced me
  to the weighted interval scheduling problem and to the work of Jon Kleinberg
  and Éva Tardos on this problem.
- [**Jon Kleinberg**](https://www.cs.cornell.edu/home/kleinber/) and [**Éva
  Tardos**](https://www.cs.cornell.edu/~eva/), who presented a different (and
  better) solution than mine to this problem, in [*Algorithm
  Design*](https://www.pearson.com/us/higher-education/program/Kleinberg-Algorithm-Design/PGM319216.html),
  1st ed. (pub. 2006), sec. 6.1, pp. 252-260; and [**Kevin
  Wayne**](https://www.cs.princeton.edu/~wayne/contact/), who made [reference
  slides](https://www.cs.princeton.edu/~wayne/kleinberg-tardos/pdf/06DynamicProgrammingI.pdf#page=7)
  on that material, which I also found useful.
- The authors/contributors of the dependencies listed above.

(None of those people is responsible for bugs in this program or in its
documentation.)
