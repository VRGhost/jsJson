"""Expansion trees (root data objects)."""

import logging

from .dependency_graph.base import (
    BaseDependencyObject,
    ExpansionRvCode,
    ExpansionRv,
)

TREE_URI_SCHEME = 'expand.tree.uri'

logger = logging.getLogger(__name__)

class Tree:

    def __init__(self, uri, graph):
        self.uri = uri
        self.graph = graph
        self._cb = []

    def addExpandCallback(self, fn):
        assert callable(fn), fn
        self._cb.append(fn)

    def doExpand(self, *args, **kwargs):
        rv = self.graph.doExpand(*args, **kwargs)
        for fn in tuple(self._cb):
            fn(rv)
        return rv


class ExpansionTrees:
    """Object to manage expansion trees inside the root namespace."""

    def __init__(self, namespace):
        self.namespace = namespace
        self._targets = {} # key -> tree
        self._results = {} # Cache of already existing results.

    def __repr__(self):
        return f"<{self.__class__.__name__} of {self.namespace!r}>"

    def getResult(self, key):
        return self._results[key]

    def isExpanded(self, key):
        try:
            my_code = self._results[key].state
        except (KeyError, AttributeError):
            return False
        return my_code == ExpansionRvCode.SUCCESS

    def add(self, owner, tree):
        """The `owner` asks for the `tree` to be expanded as part of the current expansion process."""
        logger.debug(f"{owner!r} registered tree {tree} for expansion")
        key = f"[{self.namespace.name}]::[{tree.uri.toString()}]"
        self._targets.setdefault(key, tree) # will NOT change the value if it already exists
        tree.addExpandCallback(lambda data: self._registerTreeExpandResult(key, data))
        return key

    def _registerTreeExpandResult(self, key, result):
        """Register trees' expansion result."""
        assert isinstance(result, ExpansionRv), result
        assert isinstance(result.result, BaseDependencyObject), result.result
        self._results[key] = result

    def iterUnexpanded(self):
        # Constructing a list so addition of trees during expansion process do not change this iterable
        out = [
            tree
            for (key, tree) in self._targets.items()
            if not self.isExpanded(key)
        ]
        return iter(out)

    def isFullyExpanded(self):
        all_keys = self._targets.keys()

        return all_keys == self._results.keys() and all(
            self.isExpanded(key) for key in all_keys
        )