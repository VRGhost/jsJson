import os

import urllib.parse
import posixpath as pp


class URI:
    """URI object."""

    sep = pp.sep

    def __init__(self, scheme, path, anchor):
        self.scheme = scheme
        self.path = path
        self.anchor = anchor

    @classmethod
    def fromString(cls, val):
        parseResult = urllib.parse.urlparse(val)

        full_path = []
        if parseResult.netloc:
            full_path.append(parseResult.netloc)
        if parseResult.path:
            full_path.append(parseResult.path)

        return cls(
            scheme=parseResult.scheme or None,
            path=pp.join(*full_path) if full_path else None,
            anchor=parseResult.fragment or None
        )

    def defaults(self, scheme=None, path=None, anchor=None):
        """Return a new URI object with any missing elements replaced with new defaults."""
        cls = self.__class__
        return cls(
            scheme=self.scheme or scheme,
            path=self.path or path,
            anchor=self.anchor or anchor,
        )

    def appendPath(self, *els):
        """Add new els to the path."""
        parent_path = self.path or ''
        return URI(self.scheme, pp.join(parent_path, *els), self.anchor)

    def appendAnchor(self, *els):
        """Add new els to the path."""
        parent_anchor = self.anchor or ''
        return URI(self.scheme, self.path, pp.join(parent_anchor, *els))

    def toString(self):
        out = []
        if self.scheme:
            out.extend([self.scheme, ':'])
        if self.path:
            out.append(self.path)
        if self.anchor:
            out.extend(['#', self.anchor])
        return ''.join(out)

    def __repr__(self):
        return "<{} '{}'>".format(
            self.__class__.__name__,
            self.toString()
        )

def posix_path_to_os_path(posix_path):
    parts = pp.split(posix_path)
    out = os.path.join(*parts)
    if posix_path.startswith(pp.sep):
        out = os.path.abspath(out)
    return out

def os_path_to_posix_path(os_path):
    parts = os_path.split(os.sep)
    out = pp.join(*parts)
    if os_path.startswith(os.sep):
        out = pp.normpath(pp.sep + out)
    return out