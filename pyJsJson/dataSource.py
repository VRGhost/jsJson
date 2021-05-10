"""A class that provides input data for the expansion process (e.g. reads files)."""

import os
import logging
import copy
import json

from . import exceptions

logger = logging.getLogger(__name__)


class FileSource:

    def __init__(self, allowed_search_dirs:tuple, follow_symlinks):
        self._cache = {}
        self._decoder = json.JSONDecoder()
        self._dirs = DirChecker(allowed_search_dirs, follow_symlinks=follow_symlinks)

    def loadJsonFile(self, path):
        key = os.path.normpath(path)
        try:
            out = self._cache[key]
        except KeyError:
            # not cached
            pass
        else:
            # no exception
            return copy.deepcopy(out)

        allowed_path = self._dirs.findFile(path)
        try:
            with open(allowed_path, 'r') as fin:
                out = self._decoder.decode(fin.read())
        except:
            logging.exception(f"Error loading JSON from file {allowed_path!r}")
            raise
        logger.debug(f'{path!r} loaded')
        self._cache = out
        return copy.deepcopy(out)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.search_paths)


class DirChecker:

    def __init__(self, allowed_roots, follow_symlinks:bool):
        self.roots = tuple(
            os.path.abspath(pth)
            for pth in allowed_roots
        )
        self.follow_symlinks = bool(follow_symlinks)
        if __debug__:
            assert all(os.path.isdir(pth) for pth in self.roots), self.roots

    def findFile(self, path):
        """Find 'path' in any of the allowed roots.

        The "path" can be either absolure or relative path.
        """
        for tryRoot in self.roots:
            maybeFile = os.path.join(tryRoot, path)
            if maybeFile.startswith(tryRoot + os.sep) and os.path.isfile(maybeFile):
                return maybeFile
        else:
            raise exceptions.FsError(f"File not found: {path!r} (checked in {self.roots}, follow sym links is {self.follow_symlinks})")

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.searchDirs)
