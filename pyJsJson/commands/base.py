import logging

from .. import dependency_graph

logger = logging.getLogger(__name__)

from ..dependency_graph.base import (
    # To be used in children
    ExpansionRvCode,
    ExpansionRv,
)


class Base(dependency_graph.base.Mapping):
    """Base class for commands."""

    key = '$UNKNOWN'

    @classmethod
    def match(cls, obj):
        if not super(Base, cls).match(obj):
            # obj must be a mapping
            return False
        keys = frozenset(obj.keys())
        if len(keys) == 1 and keys == {cls.key}:
            # Must have a single key and the key must match self.key
            return True
        return False

    def _applyMyAction(self, namespace, data):
        # Please note that this has to return 'ExpansionRv' result
        raise NotImplementedError(f"{self.__class__} ==> {data!r}")

    def doExpand(self, namespace):
        expanded_children_rv = super(Base, self).doExpand(namespace)
        if expanded_children_rv.state == ExpansionRvCode.SUCCESS:
            old_data = expanded_children_rv.result.data

            out = self._applyMyAction(
                namespace, old_data[self.key].getPlainObject()
            )
        else:
            out = expanded_children_rv
        return out