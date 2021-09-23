"""
This is a design for the WeightedInterval type that I'm not going to use.
(See fixme comments.)
"""

@functools.total_ordering
class WeightedInterval:
    """A weighted time interval. Supports comparison and compact printing."""

    __slots__ = ('_start', '_finish', '_weight')

    def __init__(self, start, finish, weight):
        """Creates a weighted interval with the given bounds and weight."""
        self._start = start
        self._finish = finish
        self._weight = weight

    def __repr__(self):
        """An eval-able representation."""
        return ('WeightedInterval('
                f'start={self._start}, finish={self._finish}, '
                f'weight={self._weight})')

    def __str__(self):
        """Simple string representation as space-separated numbers."""
        return f'{self.start:g} {self.finish:g} {self.weight:g}'

    def __eq__(self, other):
        """Tells if two intervals coincide in time and have the same weight."""
        # FIXME: Should the weight really be included in this comparison?
        # As a corollary, does comparing WeightedInterval objects make sense?
        # This wouldn't do the right thing with __le__ or __lt__ with
        # functools.total_ordering, would it? (This design shouldn't be used.)
        return self._start == other._start and self._finish == other._finish

    def __le__(self, other):
        """Tells if one weighted interval can be placed before another."""
        return self._finish <= other.start

    @property
    def start(self):
        """The left endpoint."""
        return self._start

    @property
    def finish(self):
        """The right endpoint."""
        return self._finish

    @property
    def weight(self):
        """The weight."""
        return self._weight
