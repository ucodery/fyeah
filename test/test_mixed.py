import pytest

from fyeah import f, t


# fmt: off
# ruff: noqa: F541
# ruff: noqa: F841


@pytest.mark.parametrize(
    'template,final',
    [
        (' { t(" {1+2} ") } ', f" { t(" {1+2} ") } "),
        (' { t" {1+2} " } ', f" { t" {1+2} " } "),
    ],
)
def test_mixed_fexprs(template, final):
    f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        (' { f(" {1+2} ") } ', t' { f(" {1+2} ") } '),
        (' { f" {1+2} " } ', t' { f" {1+2} " } '),
    ],
)
def test_mixed_texprs(template, final):
    t(template) == final
