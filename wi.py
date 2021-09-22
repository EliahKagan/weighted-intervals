#!/usr/bin/env python3
"""wi - job scheduling with weighted intervals"""

import collections
import math


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


class WeightedInterval(collections.namedtuple('WeightedIntervalBase',
                                              ('start', 'finish', 'weight'))):
    """A weighted time interval."""

    __slots__ = ()

    def __str__(self):
        """Simple string representation as space-separated numbers."""
        return f'{self.start:g} {self.finish:g} {self.weight:g}'


class IntervalSet:
    """A collection of possibly overlapping positive-length intervals."""

    __slots__ = ('_graph',)

    def __init__(self):
        """Creates an initially empty set of intervals."""
        self._graph = Graph()

    def add(self, start, finish, weight):
        """Adds the interval from start to finish to the collection."""
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
        """Solves the weighted job scheduling problem on the intervals."""
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
            raise ValueError(f'{start} to {finish} has non-finite duration')
        if duration <= 0:
            raise ValueError(f'{start} to {finish} has nonpositive duration')

        if weight <= 0:
            raise ValueError(f'nonpositive weight {weight}')


def parse_lines(lines):
    """Parses lines of triples of numbers."""
    for line in lines:
        comment_index = line.find('#')
        uncommented = (line if comment_index < 0 else line[:comment_index])
        tokens = uncommented.split()
        if tokens:
            yield map(float, tokens)


def solve_text_input(lines):
    """Solves weighted job scheduling, with text-based input and output."""
    intervals = IntervalSet()

    for start, finish, weight in parse_lines(lines):
        intervals.add(start, finish, weight)

    path, cost = intervals.compute_max_cost_nonoverlapping_subset()
    return [str(interval) for interval in path], cost


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
