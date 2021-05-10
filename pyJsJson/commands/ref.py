import os
import posixpath as pp

from ..util import (
    URI, posix_path_to_os_path,
    collections_abc,
)

from ..dependency_graph.base import (
    BaseDependencyObject,
    Primitive as DependencyPrimitive,
    ExpansionRvCode,
    ExpansionRv,
)

from . import (
    base,
    exceptions,
)

class RefSchemaExpander(BaseDependencyObject):
    """Base class for $ref schema expanders."""

    scheme = 'unknown'

    @classmethod
    def match(cls, maybe_uri):
        try:
            child_scheme = maybe_uri.scheme
        except AttributeError:
            # Not an uri
            return False
        return child_scheme == cls.scheme


class FileSchemaExpander(RefSchemaExpander):
    """Expands local file."""

    scheme = 'file'

    def doExpand(self, namespace):
        tree = namespace.loadJsonFile(posix_path_to_os_path(self.data.path))
        trees_api = namespace.root.trees
        token = trees_api.add(self, tree)
        if trees_api.isExpanded(token):
            out = trees_api.getResult(token)
        else:
            out = ExpansionRv(
                ExpansionRvCode.BLOCKED_BY,
                DependencyPrimitive(self.name, token)
            )
        return out


class Ref(base.Base):
    """$ref expander."""

    key = '$ref'

    def _walkAnchor(self, data, path):
        path = tuple(el for el in path if el)
        out = data
        for el in path:
            out = out.data[el]
        return out

    def _applyMyAction(self, namespace, data):
        assert isinstance(data, str), data
        uri = URI.fromString(data)
        expanderCls = self._getExpander(uri)
        expander = expanderCls(
            name=f"{expanderCls.__name__}({namespace.var.uri.toString()}, {data!r})",
            data=uri
        )
        with namespace.child(name='expander') as expander_ns:
            full_out = expander.doExpand(expander_ns)

        if full_out.state == ExpansionRvCode.SUCCESS:
            anchor_path = pp.split(uri.anchor or '')
            try:
                out = ExpansionRv(
                    ExpansionRvCode.SUCCESS,
                    self._walkAnchor(full_out.result, anchor_path)
                )
            except (KeyError, IndexError) as el:
                raise exceptions.InvalidReference(uri, el)
        else:
            out = full_out
        return out

    def _getExpander(self, uri):
        expanders = (
            FileSchemaExpander,
        )
        matches = [
            exp for exp in expanders
            if exp.match(uri)
        ]
        if not matches:
            supported_schemes = sorted(set(el.scheme for el in expanders))  # useful in error generation
            raise exceptions.UnsupportedOperation(f"Unable to find URI expander for {uri!r} (supported schemes: {supported_schemes})")
        elif len(matches) > 1:
            raise exceptions.ExpansionFailure(f"Multiple ref expanders found for scheme {uri!r}: {matches}")
        # else
        assert len(matches) == 1, matches
        return matches[0]