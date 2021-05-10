import os

import pytest
import pyJsJson

import pyJsJsonTestUtil

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def PROJECT_ROOT():
    return os.path.join(THIS_DIR, os.pardir)


@pytest.fixture
def PY_JS_JSON_ROOT(PROJECT_ROOT):
    return os.path.join(PROJECT_ROOT, 'pyJsJson')


@pytest.fixture
def UnittestFs(mocker):
    overlay = pyJsJsonTestUtil.TestFs(root='/unittest')
    overlay.activate(mocker)
    return overlay

@pytest.fixture
def UnittestDefaultJsonExpand(UnittestFs):


    expander = pyJsJson.expand.JsonExpand(
        allowed_search_roots=[ UnittestFs.root.name ]
    )
    expander.loadCommands(pyJsJson.commands.DEFAULT_COMMANDS)
    return expander