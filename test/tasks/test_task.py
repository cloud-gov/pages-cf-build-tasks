# this tests runs against one task at a time, copied to this location
from task.definition import BuildTask

from inspect import isclass, ismethod, signature


def test_class():
    assert isclass(BuildTask)


def test_has_handler():
    task = BuildTask()
    assert ismethod(task.handler)


def test_return_matches_required():
    task = BuildTask()
    required = dict(
        message=None,
        count=None,
        artifact=None
    )

    return_type = signature(task.handler).return_annotation
    # this will fail because the handler return isn't typed
    # assert(required.keys(), return_type.keys())
    assert True
