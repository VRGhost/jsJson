"""Test $ref command. """
import pytest

import pyJsJson


def test_file_not_found(UnittestFs, expand_data):
    with pytest.raises(pyJsJson.exceptions.FsError) as err:
        expand_data({'$ref': 'file:idontexist.json'})
    assert 'File not found' in str(err)


def test_full_file_ref(UnittestFs, expand_data):
    UnittestFs.mockFile('/unittest/base.json', {'$ref': 'file:target.json'})
    UnittestFs.mockFile('/unittest/target.json', {'hello': 'world'})
    out = expand_data({'$ref': 'file:base.json'})
    assert out == {'hello': 'world'}


@pytest.mark.parametrize('path, exp_out', [
    ('top-key', {'sub-key': 'value'}),
    ('top-key/sub-key', 'value'),
])
def test_field_in_file_ref(UnittestFs, expand_data, path, exp_out):
    UnittestFs.mockFile('/unittest/target.json', {
        'top-key': {
            'sub-key': 'value'
        }
    })
    out = expand_data({
        '$ref': 'file:target.json#{}'.format(path)
    })
    assert out == exp_out


@pytest.mark.parametrize('uri', [
    'file:idontexist.json',
    'file:idontexist.json#key',
    'file:target.json#missing-key'
])
def test_missing_ref(UnittestFs, expand_data, uri):
    """Test that passing in incorrect ref uri raises an exception."""
    UnittestFs.mockFile('/unittest/target.json', {
        'top-key': {
            'sub-key': 'value'
        }
    })
    with pytest.raises((
        pyJsJson.commands.exceptions.InvalidReference,
        pyJsJson.exceptions.FsError,
    )):
        rv = expand_data({'$ref': uri})
        print("RESULT WAS {!r} INSTEAD".format(rv))


@pytest.mark.parametrize('path', [
    '/value',
    'value',
    '/sub-dict/value',
    '/sub-list/1',
])
def test_self_ref(UnittestFs, expand_data, path):
    out = expand_data({
        'value': 'hello-world',
        'sub-dict': {
            'key': 'value',
            'value': 'hello-world'
        },
        'sub-list': [
            'nope',
            'hello-world',
            'nope',
        ],
        'output': {'$ref': '#' + path}
    })
    assert out['output'] == 'hello-world'


# def test_array_access(UnittestFs, expand_data):
#     UnittestFs.mockFile('/unittest/target.json', {
#         'top-key': [
#             {'val': -1},
#             {'val': -2},
#             {'val': -3}
#         ]
#     })
#     out = expand_data({
#         '$ref': 'file:target.json#top-key/1/val'
#     })
#     assert out == -2, 'Array indeces start at zero'


# def test_accessing_array_with_key(UnittestFs, expand_data):
#     UnittestFs.mockFile('/unittest/target.json', {
#         'top-key': [
#             {'val': -1},
#             {'val': -2},
#             {'val': -3}
#         ]
#     })
#     with pytest.raises(pyJsJson.commands.exceptions.InvalidReference):
#         rv = expand_data({'$ref': 'file:target.json#top-key/mykey'})
#         print("RESULT WAS {!r} INSTEAD".format(rv))
