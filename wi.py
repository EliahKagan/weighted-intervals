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
    increasingly from 0.
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
        Returns a path of maximal cost (total weight), and that cost.
        The graph must be acyclic. Single-vertex "paths" are considered.
        """
        vertices, cost = self._compute_max_cost_path_vertices()

        path = [WeightedVertex(vertex=vertex, weight=self._weights[vertex])
                for vertex in vertices]

        return PathCostPair(path=path, cost=cost)

    def _compute_max_cost_path_vertices(self):
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
        if not 0 <= vertex < self.order:
            raise ValueError(f'vertex {vertex} is out of range')

    def _find_roots(self):
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
    """A collection of possibly overlapping positive-length intervals."""

    __slots__ = ('_graph',)

    def __init__(self):
        """Creates an initially empty set of intervals."""
        self._graph = Graph()

    def add(self, start, finish, weight):
        """Adds a weighted interval from start to finish to the collection."""
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
        Solves the weighted job scheduling problem on the intervals.
        The algorithm's running time is quadratic in the number of intervals.
        """
        graph_path, cost = self._graph.compute_max_cost_path()

        weighted_intervals = [WeightedInterval(start=interval.start,
                                               finish=interval.finish,
                                               weight=weight)
                              for interval, weight in graph_path]

        return PathCostPair(path=weighted_intervals, cost=cost)

    @staticmethod
    def _check_values(start, finish, weight):
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
        """
        if weighted_interval.start >= weighted_interval.finish:
            raise ValueError('refusing to plot nonpositive-duration interval')

        self._min_start = min(self._min_start, weighted_interval.start)
        self._max_finish = max(self._max_finish, weighted_interval.finish)

        mwi = MarkedWeightedInterval(start=weighted_interval.start,
                                     finish=weighted_interval.finish,
                                     weight=weighted_interval.weight,
                                     mark=highlight)

        for row in self._rows:
            if self._try_insert(row, mwi):
                return

        self._rows.append([mwi])

    # TODO: (1) Use symbolic constants for magic numbers. (2) Annotate weights.
    def plot(self):
        """Creates a plot of all added intervals, as SVG code."""
        if not self._rows:  # TODO: Should this really be an IndexError?
            raise IndexError('no intervals to plot')

        assert math.isfinite(self._min_start), 'no left (lower) bound'
        assert math.isfinite(self._max_finish), 'no right (upper) bound'
        pad = (self._max_finish - self._min_start) * 0.01

        fig, ax = plt.subplots()
        fig.set_figwidth(10)
        fig.set_figheight(4)
        for side in ('left', 'right', 'top'):
            ax.spines[side].set_visible(False)
        ax.yaxis.set_visible(False)
        ax.set_xlim(xmin=(self._min_start - pad),
                    xmax=(self._max_finish + pad))
        ax.set_ylim(ymin=-0.1, ymax=(len(self._rows) + 0.1))
        ax.invert_yaxis()

        for i, row in enumerate(self._rows):
            for start, finish, _weight, highlight in row:
                ax.add_patch(Rectangle(
                    xy=(start, i + 0.05),
                    width=(finish - start), height=0.8,
                    edgecolor='black',
                    facecolor=('green' if highlight else 'gray'),
                    lw=0.3))

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
        thinking of in using binary search. A series of comparisons--each
        dereferencing a pointer to access a Python object--are usually slower,
        by a constant factor, than moving contiguous memory. (This rationale is
        analogous to the reason one might sometimes use bisect.insort.)
        """
        finish_times = MappedView(row, operator.attrgetter('finish'))
        index = bisect.bisect_right(finish_times, interval.start)

        if index == len(row) or interval.finish <= row[index].start:
            row.insert(index, interval)
            return True

        return False


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


if __name__ == '__main__':
    test_run()
