<!--
  ALGORITHM.md - job scheduling with weighted intervals (algorithm description)

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

# The Algorithm

This program solves the weighted interval scheduling problem in
*O(n<sup>2</sup>)* time on *n* intervals. This is:

- Faster than the naive
*O(2<sup>n</sup>)* brute-force algorithm of checking every subset.

- Slower than an *O(n log n)* dynamic programming algorithm given by Jon
  Kleinberg and Éva Tardos. See [*Algorithm
  Design*](https://www.pearson.com/us/higher-education/program/Kleinberg-Algorithm-Design/PGM319216.html),
  1st edition (published 2006), section 6.1, pages 252-260. See also [Kevin
  Wayne&rsquo;s revised lecture
  slides](https://www.cs.princeton.edu/~wayne/kleinberg-tardos/pdf/06DynamicProgrammingI.pdf#page=7).

(Note: As a practical matter, currently, in the web version of this program,
slow operation is usually due mostly to the visualization. See
[`BUGS.md`](BUGS.md).)

## Stages

The quadratic algorithm I&rsquo;ve used has two stages:

### 1. Build a forward-compatibility DAG.

First it builds a vertex-weighted directed
acyclic graph whose vertices are intervals. The edge *(u, v)* is in the graph
iff *u* finishes no later than *v* starts. For *n* intervals, there are up to
*n(n - 1)* such edges, so this takes *O(n<sup>2</sup>)* time.

### 2. Find the max-cost path.

Then it finds a path through the graph that maximizes the total cost, where a
path is permitted to consist of even a single vertex. Another way to think of
this as finding the graph&rsquo;s (vertex-weighted) diameter.

This is similar to the more common problem of finding single-source shortest
paths in an edge-weighted directed acyclic graph: it first linearizes the DAG,
then performs relaxations in that topologically sorted order, i.e., if *u*
comes before *v* in the topological sort, then all of *u*&rsquo;s outgoing
edges are relaxed before any of *v*&rsquo;s outgoing edges. There are three
significant differences:

- We are finding a path of maximum, not minimum, cost (total weight).

- The weights are on the vertices, not the edges. For each vertex *v*,
  *best-cost-so-far(v)* starts at *weight(v)*. To relax an edge *(u, v)* is to
  update *best-cost-so-far(v)* to *best-cost(u) + weight(v)* if the latter is
  greater (and update *v*&rsquo;s predecessor/parent accordingly).

- Since we are maximizing cost and all weights are positive, any optimal path
  begins at a root. We find all roots&rsquo; optimal paths in *O(|E|)* time,
  and the result is some optimal choice of those. It is as if we inserted a new
  root of weight 0 with edges to all the old roots.

The set of intervals appearing on that path can all be scheduled together and
their total weight is maximal.

Like constructing the graph, finding the maximum cost path also takes
*O(|V| + |E|)* time, which is *O(n<sup>2</sup>)* since *|E| =
O(n<sup>2</sup>)*. So that is the running time of the whole algorithm.

## Discussion

It is not really necessary to build an explicit graph as its own data structure
before finding a path of maximum cost. A collection of the intervals, either in
input order or sorted, could be treated as an implicit graph.

Likewise, topological sorting does not have to be done as a distinct step. This
could be, in effect, interleaved with the operation of updating each
vertex&rsquo;s information about the best known path to it so far.

I used [Kahn&rsquo;s
algorithm](https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm),
with a queue (FIFO), to compute a topological sort of the forward-compatibility
DAG. This is one of [various possible
approaches](#Variations-on-the-algorithm-should-be-supported) for finding a
topological sort. I chose Kahn&rsquo;s algorithm because I find it to be the
simplest to understand when implemented iteratively.

In most environments,
recursively implemented DFS will overflow the stack on common problem sizes in
the setting of this problem, since recursion depth is as great as the
cardinality of the largest solution (regardless of which solution is actually
chosen). DFS toposort can be implemented iteratively in such a way as to
produce the same result as recursive implementation&mdash;such as with a state
machine, or by mutating the graph to remove edges&mdash;but that code is more
complicated to understand.

I used a queue because I think that&rsquo;s the most intuitive, and the most
common implementation choice for Kahn&rsquo;s algorithm. But a stack works just
as well. (These will produce different&mdash;but both correct&mdash;topological
orderings in some cases.)

Arguably, the most elegant way to implement this whole algorithm is to
interleave all the steps, and do everything recursively.
