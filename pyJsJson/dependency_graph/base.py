"""Tree base class."""

import collections
import enum
import copy
import collections.abc

from .. import util, exceptions

NEG_INF = float('-Inf')

class ExpansionRvCode(enum.IntEnum):

    # Please note that the enum is ordered in such way that the most serious offence has the
    #  highest int value

    SUCCESS = 1 # expansion success, result = expansion result
    TRY_AGAIN = 2 # something had been expanded, but not the thing you've asked to expand
    BLOCKED_BY = 3 # expansion is unable to proceed because of 'BLOCKED_BY'

ExpansionRv = collections.namedtuple('_ExpansionRv', ['state', 'result'])


class BaseDependencyObject:
    """Base class for all dependency graph objects."""

    def __init__(self, name, data):
        self.name = name
        self.data = data

    @classmethod
    def match(cls, obj):
        """Return `True` if input python `obj` is a representation of this dependency object."""
        raise NotImplementedError

    def doExpand(self, namespace):
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} {self.data!r}>"

    def getPlainObject(self):
        raise NotImplementedError


class Primitive(BaseDependencyObject):
    """Primitive data object - has no dependencies."""

    @classmethod
    def match(cls, obj):
        return isinstance(obj, (float, int, str, None.__class__))

    def doExpand(self, namespace):
        return ExpansionRv(ExpansionRvCode.SUCCESS, self)

    def getPlainObject(self):
        return self.data

class Tuple(BaseDependencyObject):

    @classmethod
    def match(cls, obj):
        return isinstance(obj, (list, tuple))

    def doExpand(self, namespace):
        rv_code = NEG_INF
        rv_data = []
        for (idx, value) in enumerate(self.data):
            with namespace.child(
                name=f"[{idx}]",
                var={
                    'uri': namespace.var.uri.appendAnchor(str(idx)),
                }
            ) as child_ns:
                value_exp = value.doExpand(child_ns)

            rv_code = max(rv_code, value_exp.state)
            rv_data.append(value_exp.result)
        return ExpansionRv(rv_code, Tuple(self.name, tuple(rv_data)))


class Mapping(BaseDependencyObject):

    @classmethod
    def match(cls, obj):
        return isinstance(obj, collections.abc.Mapping)

    def doExpand(self, namespace):
        rv_code = NEG_INF
        rv_data = {}
        for (key, value) in self.data.items():
            with namespace.child(
                name=key,
                var={
                    'uri': namespace.var.uri.appendAnchor(key),
                }
            ) as child_ns:
                value_exp = value.doExpand(child_ns)

            rv_code = max(rv_code, value_exp.state)
            rv_data[key] = value_exp.result
        return ExpansionRv(rv_code, Mapping(self.name, rv_data))

    def getPlainObject(self):
        return dict(
            (key, value.getPlainObject())
            for (key, value) in self.data.items()
        )