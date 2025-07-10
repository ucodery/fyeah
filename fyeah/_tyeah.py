import inspect
from string.templatelib import Template

from ._escaping import escape


def t(template: str) -> Template:
    if not isinstance(template, str):
        raise TypeError(f'Cannot templatize {type(template)}')
    parent_frame = inspect.stack()[1].frame

    t = escape(template, 't')
    templated = eval(t, parent_frame.f_globals, parent_frame.f_locals)

    assert isinstance(templated, Template)
    return templated
