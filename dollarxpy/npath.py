from typedpy import ImmutableStructure, PositiveInt

from dollarxpy.basic_path import BasicPath
from dollarxpy.relation_operator import RelationOpField, RelationOperation


def at_least(n):
    return _NPathBuilder(n = n, qualifier = RelationOperation.OrMore)

def at_most(n):
    return _NPathBuilder(n = n, qualifier = RelationOperation.OrLess)

def exactly(n):
    return _NPathBuilder(n = n, qualifier = RelationOperation.Exactly)


class NPath(ImmutableStructure):
    path = BasicPath
    n = PositiveInt
    qualifier = RelationOpField



class _NPathBuilder(ImmutableStructure):
    n = PositiveInt
    qualifier = RelationOpField

    def occurrences_of(self, path):
        return NPath(path = path, n = self.n, qualifier = self.qualifier)
