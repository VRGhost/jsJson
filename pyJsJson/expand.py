"""Main functional class."""

import logging
import os

from . import (
    dataSource,
    expansion_loop,
    dependency_graph,
    namespace,
    util,
    trees,
)


logger = logging.getLogger(__name__)

class JsonExpand:

    def __init__(self, allowed_search_roots, follow_symlinks:bool=True):
        """
            allowed_search_roots - list of dirnames from which this expander is allowed to load the files.
        """
        self.fileSource = dataSource.FileSource(
            allowed_search_dirs=allowed_search_roots,
            follow_symlinks=follow_symlinks,
        )
        self.commandConstructors = tuple()

    def loadCommands(self, newCommands):
        self.commandConstructors += tuple(newCommands)

    def expand(self, tree, search_dirs=(), max_iter=1000):
        out = []
        iter_idx = 0

        expansion_namespace = namespace.RootNamespace(
            name=f"Root namespace for {tree.uri.toString()}",
            var={
                'root_uri': tree.uri,
                'uri': tree.uri,
                '_json_expander': self,
            }
        )
        root_token = expansion_namespace.trees.add(self, tree)
        loop = expansion_loop.ExpansionLoop(
            expansion_namespace
        )

        for (idx, loop_rv) in enumerate(loop):
            if idx >= max_iter:
                logger.warn(f"Expansion of {tree.uri} stopped by max iteration limit.")
                break
            if expansion_namespace.trees.isFullyExpanded():
                break
        expand_rv = expansion_namespace.trees.getResult(root_token)
        return expand_rv.result.getPlainObject()

    def loadJsonFile(self, filePath):
        """Expand a particular file."""
        raw_json = self.fileSource.loadJsonFile(filePath)
        return self._toTree(
            util.URI(
                scheme=trees.TREE_URI_SCHEME,
                path=util.os_path_to_posix_path(filePath),
                anchor=None
            ),
            raw_json
        )

    def loadData(self, data):
        return self._toTree(
            util.URI(
                scheme=trees.TREE_URI_SCHEME,
                path='<data>',
                anchor=None
            ),
            data
        )

    def _toTree(self, root_uri, data):
        graph = dependency_graph.construct(
            data,
            name=root_uri.toString(),
            extra_constructors=self.commandConstructors,
        )
        return trees.Tree(
            uri=root_uri,
            graph=graph
        )
