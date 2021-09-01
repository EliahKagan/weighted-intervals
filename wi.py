#!/usr/bin/env python3
"""wi - job scheduling with weighted intervals"""

import collections


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

    def add_edge(self, src, dest):
        """Adds a directed edge with the given endpoints."""
        self._ensure_exists(src)
        self._ensure_exists(dest)

        self._adj[src].append(dest)
        self._indegrees[dest] += 1
        self._size += 1

    def compute_max_weight_path(self):
        """
        Returns a path of maximal cost (total weight), and that cost.
        The graph must be acyclic. Single-vertex "paths" are considered.
        """
        if self.order == 0:
            raise ValueError("can't find max weight path in empty graph")

        parents, costs = self._compute_all_max_weight_paths()
        finish = max(range(self.order), key=lambda vertex: costs[vertex])
        path = []

        dest = finish
        while dest is not None:
            path.append(dest)
            dest = parents[dest]

        path.reverse()
        return PathCostPair(path=path, cost=costs[finish])

    def _compute_all_max_weight_paths(self):
        parents = [None] * self.order
        costs = self._weights[:]

        for src in self._kahn_toposort():
            for dest in self._adj[src]:
                new_cost = costs[src] + costs[dest]
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

    def add_vertex(self, key, weight):
        """Adds the key as a vertex with the given weight."""
        if key in self._table:
            raise KeyError(f'vertex key #{key:r} already exists')

        index = self._graph.add_vertex(weight)
        assert index == len(self._keys)
        self._keys.append(key)
        self._table[key] = index

    def add_edge(self, src, dest):
        """Adds a directed edge with the given endpoint keys."""
        self._graph.add_edge(self._table[src], self._table[dest])

    def compute_max_weight_path(self):
        """
        Returns a path of maximal cost (total weight), and that cost.
        The graph must be acyclic. Single-vertex "paths" are considered.
        """
        int_path, cost = self._graph.compute_max_weight_path()

        return PathCostPair(path=[self._keys[index] for index in int_path],
                            cost=cost)
