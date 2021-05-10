"""Expansion loop(s)."""

import itertools
import logging

from pyJsJson.dependency_graph.base import ExpansionRvCode


logger = logging.getLogger(__name__)


class ExpansionLoop:
    """An object that successively calls expansions of any expandable objects it is tracking."""

    def __init__(self, root_namespace):
        self._ns = root_namespace
        self._lastRootGraphCount = None

    def iterTargetGraphs(self):
        idx = -1 # in case there is nothing to enumerate
        for (idx, tree) in enumerate(self._ns.trees.iterUnexpanded()):
            yield tree
        total_cnt = idx + 1
        if self._lastRootGraphCount is not None:
            # Not a first loop
            if self._lastRootGraphCount != total_cnt:
                logger.debug(f"Number of graphs being expanded changed from {self._lastRootGraphCount} to {total_cnt}.")
        self._lastRootGraphCount = total_cnt


    def __iter__(self, max_iter=100):
        """Iterate over expansions."""
        max_iter -= 1
        for idx in itertools.count():
            if idx > max_iter:
                break
            for target in self.iterTargetGraphs():
                yield target.doExpand(self._ns)