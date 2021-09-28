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

For full details of the algorithm and how I implemented it, the code itself is
fairly readable, and includes docstrings. See [`wi.py`](wi.py). However, that
file also contains code for visualizing the solution and for helping to marshal
data between Python and JavaScript. So [the shorter `wi.py` from *alpha
0*](https://github.com/EliahKagan/weighted-intervals/blob/alpha-0/wi.py) may be
of interest (though it does not have as detailed docstrings).

A high-level description of the algorithm, and discussion, follows.

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
this is that it is finding the graph&rsquo;s (vertex-weighted) diameter.

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

## Implementation Notes

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
simplest to understand when implemented iteratively (compared to iterative
implementations of other algorithms).

In most environments, recursively implemented DFS will overflow the stack on
common problem sizes in the setting of this problem, since recursion depth can
be as great as the cardinality of the largest solution (even if that solution
is not chosen). DFS toposort can be implemented iteratively in such a way as to
produce the same result&mdash;such as with a state machine, or by mutating the
graph to remove edges&mdash;but that code is more complicated to understand.

I used a queue because I think that&rsquo;s the most intuitive, and the most
common, implementation choice for Kahn&rsquo;s algorithm. But a stack works
just as well. (These will produce different&mdash;but both
correct&mdash;topological orderings, in some cases.)

### Another Implementation Approach

Arguably, the most elegant way to implement this whole algorithm is to
interleave all the steps, and do everything recursively, by DFS. While any
interval is unvisited, pick an unvisited interval and start DFS from there,
advancing as far as possible. During DFS, while retreating from an interval *v*
to an interval *u*, check if including *v* gives a higher-cost subset than
previously seen at *u*. If so, update *u* with the new cost (and record *v* as
its successor/child). After all this, find the interval of highest recorded
cost (which should not be confused with that interval&rsquo;s weight).
Following the path from that root interval to a leaf interval (one with no
successor) gives all the intervals in an optimal solution.

(This does not affect asymptotic time complexity.)

I didn&rsquo;t do it that way, because:

- Doing this recursively would cause stack overflows on moderate or large input
  sizes.
- I thought the algorithm would be easier to understand if modularized and
  expressed in terms of abstract data types for graphs.
- I wanted to convey, and also explore, the way this can be viewed abstractly
  as a graph problem.

But I&rsquo;ve come to think there are two disadvantages to the implementation
approach I chose:

- This is more code than if I had interleaved the parts would likely be (even
  compared to structuring it around Kahn&rsquo;s algorithm rather than
  recursive DFS). That makes it hard to figure out how complicated this
  algorithm really is, compared to other algorithms (such as Kleinberg &
  Tardos&rsquo;s faster dynamic programming algorithm).
- It seems to me that the relationship between this algorithm and that of
  Kleinberg & Tardos would be better elucidated by interleaving the steps.

## Kleinberg & Tardos&rsquo;s algorithm

In the algorithm given by Jon Kleinberg and Éva Tardos in [*Algorithm
Design*](https://www.pearson.com/us/higher-education/program/Kleinberg-Algorithm-Design/PGM319216.html),
intervals are sorted by finishing time (with ties broken arbitrarily) and
numbered 1 through *n*. The solution to each subproblem consisting of the first
*j* intervals (or that solution&rsquo;s cost) is to be memoized or tabulated in
*M[j]*. A subroutine *p(j)* returns the highest *i* whose finishing time is no
later than *j*&rsquo;s start time; as mentioned in the [revised version of the
slides by Kevin
Wayne](https://www.cs.princeton.edu/~wayne/kleinberg-tardos/pdf/06DynamicProgrammingI.pdf#page=7)
that complement the book, *p(j)* can be computed in *O(log j)* time with binary
search.

The solution to subproblem 0 is the empty set (or a cost of zero). The solution
to subproblem *j > 0* either does not contain the interval *j*, in which case
it is the same as the solution to *j - 1*, or does contain the interval *j*, in
which case it is the result of adding the interval *j* to the solution to
subproblem *p(j)*. Whichever of these produces a higher total weight is to be
chosen (with ties broken arbitrarily). Each subproblem need only be solved
once, and subproblems may be solved in the order *0, 1, 2, &hellip;, n - 1, n*.

## Relationship between the two algorithms

*I might update this section in the future when I have more precise insights into
the relationship between these two algorithms, or with corrections.*

In Kleinberg & Tardos&rsquo;s presentation, the costs were stored in *M*. The
actual solution&mdash;a subset of intervals&mdash;was built from them
afterwards. Storing the subsets, separately, at each position in *M*, would use
asymptotically more space, and also take asymptotically more time to process.

An alternative approach to implementing their algorithm is for *M[j]* to store,
for each interval *j > 0*:

- a cost
- the &ldquo;predecessor&rdquo; *i* whose solution was used to solve *j*, which
  is *j - 1* or *p(j)*
- a boolean value indicating whether interval *j* is included in the solution
  for the subproblem up to *j*

For *j = 0*, the cost is 0, the predecessor is *nil*, and the boolean value
indicating if it is to be included is *false*.

This is a compact way of storing the full solution. Enumerating the elements of
the solution still requires another pass, but this pass just reads off the
results, rather than recomputing anything. (In particular, values of *p(j)*
need neither be recomputed nor all computed and stored ahead of time.) Then,
after all subproblems are solved, the path back through the
&ldquo;predecessors,&rdquo; starting at *n*, can be followed, and the subset of
intervals that appear along the path and whose boolean values indicate they are
to be included can be constructed.

This now resembles an algorithm for finding an optimal path in a graph.
Choosing between including and not including an interval (in the first pass)
sort of looks like a relaxation, in which a parent/predecessor is updated when
a better cost is achieved. Representing the solution compactly as a tree of
paths in the reverse of the order in which they are naturally followed
resembles the way many algorithms for finding shortest or longest paths in a
graph return results, including Dijkstra&rsquo;s algorithm and my algorithm for
solving this problem. The particular way 0 is treated specially&mdash;as a root
added for convenience of computation&mdash;is, as [phrased
above](#2-find-the-max-cost-path), &ldquo;as if we inserted a new root of
weight 0 with edges to all the old roots.&rdquo;

Based on this, I am *tempted* to say that my algorithm is an unnecessarily
redundant, slower variant of Kleinberg & Tardos&rsquo;s algorithm. Suppose,
instead of checking the solutions to two previous subproblems, one checked
*all* the solutions that were available so far (rejecting those for intervals
that overlap the current interval). This quadratic algorithm&mdash;a worsening
of Kleinberg & Tardos&rsquo;s algorithm&mdash;seems a lot like my algorithm,
especially if my algorithm is implemented in [the alternative way described
above](#another-implementation-approach).

But I think that is not quite correct. Kleinberg & Tardos&rsquo;s algorithm
does not simply check the two subproblems that the current subproblem depends
on (rather than all *O(n)* subproblems whose solutions are available). It also
*causes* the current subproblem to depend only on (up to) two preceding
subproblems. It does this by propagating best-solution information even through
subproblems ending at intervals that are not part of the optimal subset being
built. That is, *M[j]* is correct for the subset of intervals from 1 to *j*
even when the solution does not include *j*.

This is to say that it&rsquo;s not just that my algorithm happens to relax more
edges in the DAG than necessary. It also doesn&rsquo;s store enough information
to avoid doing so. When an edge *(u, v)* is relaxed, the cost at *v* is updated
only if the path through *u* is better than the best path including *v* so far.
Relaxations don&rsquo;t update *v* with information from *u* about other
vertices, when *u* is not to be used.
