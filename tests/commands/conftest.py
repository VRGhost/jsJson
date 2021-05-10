import os

import pytest


@pytest.fixture
def expand_data(UnittestDefaultJsonExpand):
    """Returns a callable to expand an input command."""

    def _doExpand(data):
        tree = UnittestDefaultJsonExpand.loadData(data)
        return UnittestDefaultJsonExpand.expand(tree)

    return _doExpand
