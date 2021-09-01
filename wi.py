#!/usr/bin/env python3
"""wi - job scheduling with weighted intervals"""

import collections
import bidict


class IntGraph:
    """A vertex-weighted directed graph whose vertices are integers."""

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
        """Adds a vertex with the specified weight. Returns the vertex."""
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

    def toposort(self):
        """
        Yields all vertices, in a topologically sorted order.
        Uses Kahn's algorithm.
        """
        indegs = self._indegrees[:]
        roots = collections.deque(self._find_roots())

        while roots:
            src = roots.popleft()

            for dest in self._adj[src]:
                indegs[dest] -= 1
                if indegs[dest] == 0:
                    roots.append(dest)

            yield src

    def _ensure_exists(self, vertex):
        if not 0 <= vertex < self.order:
            raise ValueError(f'vertex {vertex} is out of range')

    def _find_roots(self):
        return (vertex for vertex, indeg in enumerate(self._indegrees)
                if indeg == 0)


class Graph:
    """A vertex-weighted directed graph whose vertices are hashable objects."""

    __slots__ = ('_lookup', '_graph')

    def __init__(self):
        """Creates a graph with no vertices and no edges."""
        self._lookup = bidict.bidict()
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
        """Adds the key as a vertex with the specified weight."""
        if key in self._lookup[key]:
            raise KeyError(f'vertex key #{key:r} already exists')

        self._lookup[key] = self._graph.add_vertex(weight)

    def add_edge(self, src, dest):
        """Adds a directed edge with the given endpoint keys."""
        self._graph.add_edge(self._lookup[src], self._lookup[dest])
