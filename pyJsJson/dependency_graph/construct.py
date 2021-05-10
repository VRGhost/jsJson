# from . import (
#     JsonTreeRoot,
#     DictTree, ListTree,
# )

import collections.abc

from . import base



def remap_python_objects(data, prefix, constructurs):
    """Remaps input 'data' into dependency graph objects."""
    if isinstance(data, collections.abc.Mapping):
        recurse_results = dict(
            (key, remap_python_objects(value, f"{prefix}.{key}", constructurs))
            for (key, value) in data.items()
        )
    elif isinstance(data, (list, tuple)):
        recurse_results = tuple(
            remap_python_objects(value, f"{prefix}[{idx}]", constructurs)
            for (idx, value) in enumerate(data)
        )
    else:
        recurse_results = data
    # Recurse_results must be defined now
    for constructor in constructurs:
        if constructor.match(recurse_results):
            return constructor(
                name=prefix,
                data=recurse_results
            )
    # else
    raise NotImplementedError(data, constructurs)

def construct(data, name, extra_constructors=()):
    actual_constructors = tuple(extra_constructors) + (
        # Please note that the default dependency objects are added at the end of the
        # actual_constructors, therefore any extra_constructors specified take precedence
        base.Tuple, base.Mapping,
        base.Primitive,
    )
    return remap_python_objects(
        data, name,
        actual_constructors
    )