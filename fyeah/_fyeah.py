import inspect


def f(template: str) -> str:
    if not isinstance(template, str):
        raise TypeError(f"Cannot format {type(template)}")
    # add quotes around template
    template = "f" + repr(template)
    parent_frame = inspect.stack()[1].frame
    formatted = eval(template, parent_frame.f_globals, parent_frame.f_locals)
    assert isinstance(template, str)
    return formatted
