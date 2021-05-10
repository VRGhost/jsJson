# ->  Namespaces are one honking great idea -- let's do more of those!
# These objects serve as a namespace for variables/callback functions that are provided to the commands during the expansion process.

import os
import copy
import contextlib
import collections.abc
import logging

from .util import posix_path_to_os_path
from . import exceptions, trees

logger = logging.getLogger(__name__)

class NamespaceVar(collections.abc.Mapping):
    """A proxy object for Namespaces' variable read-only access."""

    def __init__(self, my_vars, parent=None):
        self._var = my_vars
        self._parentVar = parent.var if parent else {}

    def copy(self):
        """Return copy of the namespace."""
        return self.__class__(
            self._var.copy(),
            self._parentVar.copy(),
        )

    def _getMergedDict(self):
        out = dict(self._parentVar)
        out.update(self._var)
        return out

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        return self._getMergedDict()[key]

    def __iter__(self):
        return iter(self._getMergedDict())

    def __len__(self):
        return len(self._getMergedDict())

class Namespace:

    root = property(lambda s: s.parent.root)

    def __init__(
        self,
        name:str, parent,
        var=None, # dict of value -> payload. Please ensure that this dict won't be mutable.
    ):
        self.name = name
        self.parent = parent
        self.var = NamespaceVar(
            my_vars=(var or {}).copy(),
            parent=self.parent,
        )

    @contextlib.contextmanager
    def child(self, name, var=None):
        """Create a child namespace."""
        fqn = f"{self.name}.{name}"
        child_ns = Namespace(name=fqn, parent=self, var=var)
        yield child_ns

    def loadJsonFile(self, path):
        """Callback for graph objects to load json trees."""
        root_uri_path = self.var.root_uri.path
        root_dir_path = os.path.dirname(posix_path_to_os_path(root_uri_path))
        load_path = os.path.normpath(
            os.path.join(
                root_dir_path,
                path
            )
        )
        logger.debug(f"Namespace {self} is loading {path} as {load_path}.")
        return self.var._json_expander.loadJsonFile(load_path)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"


class RootNamespace(Namespace):

    root = property(lambda s: s)

    def __init__(self, name, **kwargs):
        super(RootNamespace, self).__init__(name=name, parent=None, **kwargs)
        self.trees = trees.ExpansionTrees(self)

    def setVars(self, extra_vars: dict):
        """(Root only) - add extra functions after object's creation.

            Everyone except for the root has to declare variables & functions at the moment of creation of the namespace
        """
        new_keys = extra_vars.keys()
        old_keys = self.var._var.keys()
        any_overrides = set(new_keys).intersection(old_keys)
        if any_overrides:
            raise exceptions.PyJsJsonException(f"{any_overrides} are already defined")
        self.var._var.update(extra_vars)

