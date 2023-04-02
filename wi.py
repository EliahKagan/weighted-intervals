#!/usr/bin/env python3

# wi.py - job scheduling with weighted intervals (main implementation file)
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

"""wi - job scheduling with weighted intervals"""

import bisect
import collections
import io
import math
import operator

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


WeightedVertex = collections.namedtuple('WeightedVertex', ('vertex', 'weight'))

WeightedVertex.__doc__ = """A vertex together with its associated weight."""


PathCostPair = collections.namedtuple('PathCostPair', ('path', 'cost'))

PathCostPair.__doc__ = """A path through a graph, and its cost."""


class IntGraph:
    """
    A vertex-weighted directed graph whose vertices are integers, numbered
    increasingly from 0. Supports finding a maximum-cost path ("diameter").
    """

    __slots__ = ('_adj', '_indegrees', '_weights', '_size')

    def __init__(self):
        """Creates a graph with no vertices and no edges."""
        self._adj = []
        self._indegrees = []
        self._weights = []
        self._size = 0

    @property
    def order(self):
        """The number of vertices in the graph."""
        return len(self._adj)

    @property
    def size(self):
        """The number of edges in the graph."""
        return self._size

    def add_vertex(self, weight):
        """Adds a vertex with the given weight. Returns the vertex."""
        self._adj.append([])
        self._indegrees.append(0)
        self._weights.append(weight)
        return self.order - 1

    def increase_weight(self, vertex, weight):
        """Increases the vertex's weight to the new weight, if larger."""
        self._ensure_exists(vertex)
        self._weights[vertex] = max(self._weights[vertex], weight)

    def add_edge(self, src, dest):
        """Adds a directed edge with the given endpoints."""
        self._ensure_exists(src)
        self._ensure_exists(dest)

        self._adj[src].append(dest)
        self._indegrees[dest] += 1
        self._size += 1

    def compute_max_cost_path(self):
        """
        Returns a path of maximal cost (total weight), and that cost. The graph
        must be acyclic. Single-vertex "paths" are considered. (Another way to
        think of this as finding the "diameter" of a vertex-weighted DAG.) This
        takes O(n + m) on a graph of n vertices and m edges.

        This is similar to the linear-time algorithm for finding single-source
        shortest paths in a weighted (i.e., edge-weighted) DAG: it first finds
        a topological sort of the vertices, then performs relaxations in that
        order. There are three significant differences:

        (1) We are finding a path of maximum, not minimum, cost (total weight).

        (2) The weights are on the vertices, not the edges. For each vertex v,
            best-cost-so-far(v) starts at weight(v). To relax an edge (u, v) is
            to update best-cost-so-far(v) to best-cost(u) + weight(v) if the
            latter is greater (and update v's predecessor/parent accordingly).

        (3) We are maximizing cost and all weights are positive, so any optimal
            path begins at a root. We find all roots' optimal paths in linear
            time (and the result is some optimal choice of those). It is as if
            we inserted a new root of weight 0 with edges to all the old roots.

        See also ALGORITHM.md.
        """
        vertices, cost = self._compute_max_cost_path_vertices()

        path = [WeightedVertex(vertex=vertex, weight=self._weights[vertex])
                for vertex in vertices]

        return PathCostPair(path=path, cost=cost)

    def _compute_max_cost_path_vertices(self):
        """Helper for compute_max_cost_path. Emits vertices without weights."""
        if self.order == 0:
            raise ValueError("can't find max weight path in empty graph")

        parents, costs = self._compute_max_weight_paths_tree()
        finish = max(range(self.order), key=lambda vertex: costs[vertex])
        path = []

        dest = finish
        while dest is not None:
            path.append(dest)
            dest = parents[dest]

        path.reverse()
        return PathCostPair(path=path, cost=costs[finish])

    def _compute_max_weight_paths_tree(self):
        """
        Helper for compute_max_cost_path.
        Emits the parents forest of all max-cost paths from root vertices.
        """
        parents = [None] * self.order
        costs = self._weights[:]

        for src in self._kahn_toposort():
            for dest in self._adj[src]:
                new_cost = costs[src] + self._weights[dest]
                if costs[dest] < new_cost:
                    parents[dest] = src
                    costs[dest] = new_cost

        return parents, costs

    def _kahn_toposort(self):
        """
        Linearizes (topologically sorts) the graph by Kahn's algorithm.
        (If the graph has a cycle, this detects it and throws an exception.)
        """
        tsort = []
        indegs = self._indegrees[:]
        roots = collections.deque(self._find_roots())

        while roots:
            src = roots.popleft()

            for dest in self._adj[src]:
                indegs[dest] -= 1
                if indegs[dest] == 0:
                    roots.append(dest)

            tsort.append(src)

        if len(tsort) != self.order:
            raise ValueError('cyclic graph cannot be topologically sorted')

        return tsort

    def _ensure_exists(self, vertex):
        """Throws an exception if the vertex is not in range."""
        if not 0 <= vertex < self.order:
            raise ValueError(f'vertex {vertex} is out of range')

    def _find_roots(self):
        """Yields the vertices in the graph that have no incoming edges."""
        return (vertex for vertex, indeg in enumerate(self._indegrees)
                if indeg == 0)


class Graph:
    """A vertex-weighted directed graph whose vertices are hashable objects."""

    __slots__ = ('_keys', '_table', '_graph')

    def __init__(self):
        """Creates a graph with no vertices and no edges."""
        self._keys = []
        self._table = {}
        self._graph = IntGraph()

    @property
    def order(self):
        """The number of vertices in the graph."""
        return self._graph.order

    @property
    def size(self):
        """The number of edges in the graph."""
        return self._graph.size

    @property
    def vertices(self):
        """Yields all vertex keys."""
        return iter(self._keys)

    def add_vertex(self, key, weight):
        """Adds the key as a vertex with the given weight."""
        if key in self._table:
            raise KeyError(f'vertex key #{key!r} already exists')

        index = self._graph.add_vertex(weight)
        assert index == len(self._keys)
        self._keys.append(key)
        self._table[key] = index

    def increase_weight(self, key, weight):
        """Increases the key's vertex's weight to the new weight, if larger."""
        self._graph.increase_weight(self._table[key], weight)

    def add_edge(self, src, dest):
        """Adds a directed edge with the given endpoint keys."""
        self._graph.add_edge(self._table[src], self._table[dest])

    def compute_max_cost_path(self):
        """
        Returns a path of maximal cost (total weight), and that cost.
        The graph must be acyclic. Single-vertex "paths" are considered.

        See IntGraph.compute_max_cost_path for the algorithm.
        """
        int_path, cost = self._graph.compute_max_cost_path()

        path = [WeightedVertex(vertex=self._keys[index], weight=weight)
                for index, weight in int_path]

        return PathCostPair(path=path, cost=cost)


Interval = collections.namedtuple('Interval', ('start', 'finish'))

Interval.__doc__ = """A time interval."""


WeightedInterval = collections.namedtuple('WeightedInterval',
                                          ('start', 'finish', 'weight'))

WeightedInterval.__doc__ = """A weighted time interval."""


MarkedWeightedInterval = collections.namedtuple(
    'MarkedWeightedInterval',
    ('start', 'finish', 'weight', 'mark'))

MarkedWeightedInterval.__doc__ = """
A weighted time interval that carries a marking.
This is used to specify if it should be highlighted in a plot.
"""


class IntervalSet:
    """
    A collection of possibly overlapping positive-length weighted intervals.

    This data structure solves the weighted interval scheduling problem in
    quadratic time. This is faster than the exponential-time brute-force
    algorithm, but slower than an O(n log n) dynamic programming algorithm
    given by Jon Kleinberg and Éva Tardos (*Algorithm Design*, pp. 252-260,
    pub. 2006).

    The quadratic algorithm implemented here first builds a vertex-weighted
    directed acyclic graph whose vertices are intervals. The edge (u, v) is in
    the graph iff u finishes no later than v starts. For n intervals, there are
    up to n(n - 1) such edges, so this takes O(n**2) time. That takes place
    incrementally as the user repeatedly calls add().

    Then, the graph is topologically sorted and a path that maximizes total
    weight is found. These operations are each linear in the size (number of
    edges) of the graph. Finding a max-cost path -- which can also be regarded
    as finding the "diameter" of the graph -- is similar to finding shortest
    paths in a DAG. See IntGraph.compute_max_cost_path() for how this is done.
    There are O(n**2) edges for n intervals, so this also takes O(n**2) time.
    This happens when the user calls compute_max_cost_nonoverlapping_subset().

    See ALGORITHM.md for a more detailed description of this algorithm, and its
    conceptual connection to the faster algorithm by Kleinberg and Tardos.
    """

    __slots__ = ('_graph',)

    def __init__(self):
        """Creates an initially empty set of intervals."""
        self._graph = Graph()

    def add(self, start, finish, weight):
        """
        Adds a weighted interval from start to finish to the collection.

        In the graph representation (see the class docstring), this adds edges
        into the new interval from each interval that could be scheduled before
        it, and out of the new interval to each interval that could be
        scheduled after it.
        """
        self._check_values(start, finish, weight)
        new_interval = Interval(start, finish)

        try:
            self._graph.add_vertex(new_interval, weight)
        except KeyError:
            self._graph.increase_weight(new_interval, weight)
            return  # Changing the weight doesn't add (or remove) any edges.

        for old_interval in self._graph.vertices:
            if finish <= old_interval.start:
                self._graph.add_edge(new_interval, old_interval)
            elif old_interval.finish <= start:
                self._graph.add_edge(old_interval, new_interval)

    def compute_max_cost_nonoverlapping_subset(self):
        """
        Solves the weighted job scheduling problem on the intervals. Running
        time is quadratic in the number of intervals.

        See the class docstring for details on the algorithm.
        """
        graph_path, cost = self._graph.compute_max_cost_path()

        weighted_intervals = [WeightedInterval(*interval, weight=weight)
                              for interval, weight in graph_path]

        return PathCostPair(path=weighted_intervals, cost=cost)

    @staticmethod
    def _check_values(start, finish, weight):
        """Checks that an interval's values make sense and throws if not."""
        named = (('start', start), ('finish', finish), ('weight', weight))
        for name, value in named:
            if not math.isfinite(value):
                raise ValueError(f'non-finite {name}')

        duration = finish - start
        if not math.isfinite(duration):
            raise ValueError(
                f'{start:g} to {finish:g} has non-finite duration')
        if duration <= 0:
            raise ValueError(
                f'{start:g} to {finish:g} has nonpositive duration')

        if weight <= 0:
            raise ValueError(f'nonpositive weight {weight:g}')


class MappedView:
    """
    A mapped read-only view of a list.

    This enables bisect_left and bisect/bisect_right to use custom keys.
    """

    __slots__ = ('_elems', '_mapper')

    def __init__(self, elems, mapper):
        """Creates a view of elems via mapper."""
        self._elems = elems
        self._mapper = mapper

    def __bool__(self):
        """Tells if the list has any elements."""
        return bool(self._elems)

    def __len__(self):
        """Returns the number of elements in the list."""
        return len(self._elems)

    def __getitem__(self, index):
        """Gets the mapped value at the given index."""
        return self._mapper(self._elems[index])


class Plotter:
    """Visualizes all input intervals, with solution intervals colored."""

    # Plot geometry.
    FIGURE_WIDTH = 10
    FIGURE_HEIGHT = 4
    TOP_MARGIN = 0.05
    X_PADDING_FRACTION = 0.01
    Y_PADDING = 0.1
    BAR_HEIGHT = 0.8
    BORDER_THICKNESS = 0.3

    # Plot colors.
    BORDER_COLOR = 'black'
    BAR_COLOR = 'gray'
    HIGHLIT_BAR_COLOR = 'green'

    __slots__ = ('_rows', '_min_start', '_max_finish')

    def __init__(self):
        """Creates a new plotter, initially holding no intervals."""
        self._rows = []
        self._min_start = math.inf
        self._max_finish = -math.inf

    def add(self, weighted_interval, highlight):
        """
        Adds an interval to be plotted in the first row where it fits.

        This can take time linear in the number of intervals added so far. So
        to add all intervals takes quadratic time (like the solving algorithm).
        See _try_intervals below.
        """
        if weighted_interval.start >= weighted_interval.finish:
            raise ValueError('refusing to plot nonpositive-duration interval')

        self._min_start = min(self._min_start, weighted_interval.start)
        self._max_finish = max(self._max_finish, weighted_interval.finish)

        mwi = MarkedWeightedInterval(*weighted_interval, mark=highlight)

        for row in self._rows:
            if self._try_insert(row, mwi):
                return

        self._rows.append([mwi])

    # TODO: Annotate weights.
    def plot(self):
        """Creates a plot of all added intervals, as SVG code."""
        fig, ax = self._initialize_plot()

        for i, row in enumerate(self._rows):
            for start, finish, _weight, highlight in row:
                bc = (self.HIGHLIT_BAR_COLOR if highlight else self.BAR_COLOR)

                ax.add_patch(Rectangle(
                    xy=(start, i + self.TOP_MARGIN),
                    width=(finish - start), height=self.BAR_HEIGHT,
                    edgecolor=self.BORDER_COLOR, facecolor=bc,
                    lw=self.BORDER_THICKNESS))

        with io.StringIO() as dump:
            fig.savefig(dump, format='svg', bbox_inches='tight')
            return dump.getvalue()

    @staticmethod
    def _try_insert(row, interval):
        """
        Inserts an interval into a row if it would not overlap with any
        interval already there. This takes time linear in the size of the row
        if an insertion is performed, and logarithmic time otherwise.

        Implementation note: This is called repeatedly in such a way that
        binary search (bisect.bisect_right) may afford no asymptotic speedup
        overall, as many intervals may be placed (before others) in the same
        row. Nonetheless, insertion into a large row is actually the case I am
        thinking of in using binary search. A sequence of comparisons -- each
        dereferencing a pointer to access a Python object -- is usually slower,
        by a constant factor, than moving contiguous memory. (This rationale is
        analogous to the reason one might sometimes use bisect.insort.)
        """
        finish_times = MappedView(row, operator.attrgetter('finish'))
        index = bisect.bisect_right(finish_times, interval.start)

        if index == len(row) or interval.finish <= row[index].start:
            row.insert(index, interval)
            return True

        return False

    def _initialize_plot(self):
        """Creates and returns our customized Figure and Axes objects."""
        x_range = self._compute_x_range()  # Do this first, to fail sooner.

        fig, ax = plt.subplots()

        fig.set_figwidth(self.FIGURE_WIDTH)
        fig.set_figheight(self.FIGURE_HEIGHT)

        self._style_axes(ax)
        self._set_axes_geometry(ax, x_range * self.X_PADDING_FRACTION)

        return fig, ax

    def _compute_x_range(self):
        """Checks there are intervals to plot and computes the x-range."""
        if not self._rows:
            # TODO: Should this really be an IndexError?
            raise IndexError('no intervals to plot')

        # If the endpoints themselves are infinite or NaN, that's a bug.
        assert math.isfinite(self._min_start), 'no left (lower) bound'
        assert math.isfinite(self._max_finish), 'no right (upper) bound'

        x_range = self._max_finish - self._min_start
        if not math.isfinite(x_range):
            raise ValueError('plot x-range overflow '
                             f'({self._min_start} to {self._max_finish})')

        return x_range

    @staticmethod
    def _style_axes(ax):
        """Hides all but the lower axis on a Matplotlib Axes object."""
        # Pyodide has Matplotlib 3.3.3, which doesn't support [[...]] syntax.
        for side in ('left', 'right', 'top'):
            ax.spines[side].set_visible(False)

        ax.yaxis.set_visible(False)

    def _set_axes_geometry(self, ax, x_padding):
        """Applies custom range and orientation for the axes."""
        ax.set_xlim(xmin=(self._min_start - x_padding),
                    xmax=(self._max_finish + x_padding))

        ax.set_ylim(ymin=-self.Y_PADDING,
                    ymax=(len(self._rows) + self.Y_PADDING))

        ax.invert_yaxis()


def parse_lines(lines):
    """Parses lines of triples of numbers to weighted intervals."""
    for line in lines:
        comment_index = line.find('#')
        uncommented = (line if comment_index < 0 else line[:comment_index])

        tokens = uncommented.split()
        if not tokens:
            continue

        if len(tokens) != 3:
            raise ValueError(f'bad interval: need 3 values, got {len(tokens)}')

        yield WeightedInterval._make(map(float, tokens))


def do_solve(weighted_intervals):
    """Core solving helper, for solve_text_input."""
    interval_set = IntervalSet()
    for start, finish, weight in weighted_intervals:
        interval_set.add(start, finish, weight)

    return interval_set.compute_max_cost_nonoverlapping_subset()


def build_plotter(all_weighted_intervals, weighted_intervals_to_highlight):
    """Plotter-building helper, for solve_text_input."""
    need_marks = set(weighted_intervals_to_highlight)
    plotter = Plotter()

    for weighted_interval in all_weighted_intervals:
        if weighted_interval in need_marks:
            plotter.add(weighted_interval, highlight=True)
            need_marks.remove(weighted_interval)
        else:
            plotter.add(weighted_interval, highlight=False)

    return plotter


def solve_text_input(lines):
    """
    Solves weighted job scheduling. Takes line-based input. Returns line-based
    and SVG plot output. (The web version uses this; see bridge.js.)
    """
    weighted_intervals = list(parse_lines(lines))
    path, cost = do_solve(weighted_intervals)
    path_lines = [f'{interval.start:g} {interval.finish:g} {interval.weight:g}'
                  for interval in path]

    svg_plot = build_plotter(weighted_intervals, path).plot()

    return path_lines, cost, svg_plot


# TODO: This should probably just be a doctest on the IntervalSet type.
def test_run():
    """Tries out the IntervalSet type with a fairly simple test case."""
    intervals = IntervalSet()
    intervals.add(10, 20, 2)
    intervals.add(20, 30, 2)
    print(intervals.compute_max_cost_nonoverlapping_subset())

    intervals.add(15, 25, 5)
    print(intervals.compute_max_cost_nonoverlapping_subset())

    intervals.add(-1, -0.5, 50)
    print(intervals.compute_max_cost_nonoverlapping_subset())


__all__ = [thing.__name__ for thing in (
        WeightedVertex,
        PathCostPair,
        IntGraph,
        Graph,
        Interval,
        WeightedInterval,
        IntervalSet,
        Plotter,
        solve_text_input,
    )]


if __name__ == '__main__':
    test_run()
