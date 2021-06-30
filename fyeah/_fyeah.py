import builtins
import inspect
from types import CodeType
from typing import Any, NewType, Union


CompiledFstring = NewType("CompiledFstring", CodeType)


def f(template: Union[str, CompiledFstring]) -> str:
    if isinstance(template, str):
        # add quotes around template
        template = "f" + repr(template)
    elif not isinstance(template, CodeType):
        raise TypeError(f"Cannot format {type(template)}")
    parent_frame = inspect.stack()[1].frame
    formatted = eval(template, parent_frame.f_globals, parent_frame.f_locals)
    return formatted


def compile(template: str) -> CompiledFstring:
    if not isinstance(template, str):
        raise TypeError(f"Cannot compile {type(template)}")
    template = "f" + repr(template)
    compstring = builtins.compile(template, "<fyeah>", "eval")
    return compstring
