import inspect

from ._escaping import escape


def f(template: str) -> str:
    if not isinstance(template, str):
        raise TypeError(f'Cannot format {type(template)}')
    parent_frame = inspect.stack()[1].frame
    # add quotes around template
    f = 'f' + repr(template)
    try:
        formatted = eval(f, parent_frame.f_globals, parent_frame.f_locals)
    except SyntaxError as repr_error:
        # custom escaping, in Python, of the string is expensive and only
        # necessary in very unusual scenarios
        f = escape(template, 'f')
        try:
            formatted = eval(f, parent_frame.f_globals, parent_frame.f_locals)
        except SyntaxError:
            # custom escaping didn't help, show the original error
            raise repr_error from None
    assert isinstance(formatted, str)
    return formatted
