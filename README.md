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

This solves the weighted interval scheduling problem and visualizes the
solution. It shows text-based output and also plots all input intervals,
highlighting the ones that part of the solution that was found.

This is *alpha 1* of weighted-intervals. The web version is implemented, but
buggy. The documentation is also meager&mdash;I&rsquo;ve described the
algorithm I used, somewhat, in [`wi.py`](wi.py), but there should really be a
Markdown file that explains it clearly. The CLI version is not yet implemented
(except in the sense that you could import [`wi.py`](wi.py) and interact with
it as you please).

[**Try weighted-intervals on the web
here.**](https://eliahkagan.github.io/weighted-intervals/)

## License

**weighted-intervals** is written by Eliah Kagan. It is licensed under
[0BSD](https://spdx.org/licenses/0BSD.html). See [**`LICENSE`**](LICENSE).

Its [dependencies](#dependencies) are written by different authors have
different licenses, though they are all free open-source software. Furthermore,
none of them are included in this repository&mdash;they are obtained from CDNs
(for the web version) or via [pipenv](https://github.com/pypa/pipenv) (if you
work locally and use the provided
[`Pipfile`](Pipfile)/[`Pipfile.lock`](Pipfile.lock)). So this whole repository
is offered under 0BSD.

## How it Works

*This describes how the web version of the software works, not the algorithm it
uses. In summary: a whole Python interpreter runs in your web browser, and the
interesting code is in [`wi.py`](wi.py).*

The algorithm used here could be implemented in just about any language,
including JavaScript, but I&rsquo;ve use Python, which I think is a nice
language for *expressing* algorithms to humans while still letting them run
(albeit not always as fast as in some other languages). By Python code does not
traditionally run in web browsers.

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

Until then, if one is just interested in the algorithm, one might prefer to
look at [the shorter `wi.py` from *alpha
0*](https://github.com/EliahKagan/weighted-intervals/blob/alpha-0/wi.py).

## Dependencies

The dependencies [are obtained externally](#license) rather than being included
in this repository.

**weighted-intervals** uses these libraries:

- [**Pyodide**](https://pyodide.org/en/stable/) (latest version), by the
  [Pyodide development team](https://pyodide.org/en/stable/project/about.html)
  ([Mozilla Public License
  2.0](https://github.com/pyodide/pyodide/blob/main/LICENSE)). This supplies [a
  WebAssembly port](https://github.com/pyodide/pyodide/tree/main/cpython) of
  [CPython](https://www.python.org/) (currently version 3.9) and various
  libraries. All recent versions of [CPython
  itself](https://github.com/python/cpython) are [licensed
  under](https://github.com/python/cpython/blob/main/LICENSE) the [Python
  Software Foundation License 2.0](https://spdx.org/licenses/PSF-2.0.html).
- [**Matplotlib**](https://matplotlib.org/) ([as of this writing, version
  3.3.3](https://github.com/pyodide/pyodide/blob/main/packages/matplotlib/meta.yaml)
  in the web version; but my [`Pipfile`](Pipfile) requests 3.4.3) by the
  Matplotlib Development Team. Matplotlib is licensed under the [License
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

I&rsquo;m thankful to the authors and contributors of all those projects.