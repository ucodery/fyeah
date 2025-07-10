from collections import defaultdict
from itertools import chain, zip_longest
from string.templatelib import Interpolation, Template

import pytest

from fyeah import t


# fmt: off
# ruff: noqa: F541
# ruff: noqa: F841

# Global vars for use in t-strings outside of test functions
name = 'foo'
outside = 3.1


def serialize_template(template, lossy=False):
    if lossy:
        serialize_interpolations = (
           (
               serialize_template(i.value) if isinstance(i.value, Template) else i.value,
               i.conversion,
               i.format_spec
           )
           for i in template.interpolations
        )
    else:
        serialize_interpolations = (
           (
               serialize_template(i.value) if isinstance(i.value, Template) else i.value,
               i.expression,
               i.conversion,
               i.format_spec
           )
           for i in template.interpolations
        )
    return list(
       chain.from_iterable(
           zip_longest(
               template.strings,
               serialize_interpolations,
               fillvalue=()
            )
        )
    )


def assert_equivalent_templates(first_t, second_t):
    """test that two Template objects look the same

    Two Templates, or two Interpolations, are only equal when identical
    objects, which is not very helpful for testing.
    i.e. == only returns True in cases is returns True
    """
    first_template = serialize_template(first_t)
    second_template = serialize_template(second_t)

    # compare the fully unpacked types instead of lazily comparing one entry at a time
    # so that the test diff will show all the problems on the first fail
    assert first_template == second_template


def assert_close_templates(first_t, second_t):
    """test that two Template objects look close enough

    This function throws away the expression portion of Interpolations
    This is because translating a string object back into syntactically
    correct code can be a lossy process. As long as the value remains
    the same, it is still correct.
    """
    first_template = serialize_template(first_t, lossy=True)
    second_template = serialize_template(second_t, lossy=True)

    assert first_template == second_template



def test_debug_expr():
    assert_equivalent_templates(t('look {name=}'), t'look {name=}')
    assert_equivalent_templates(t('look {outside  = }'), t'look {outside  = }')


@pytest.mark.parametrize('template', ['', 'Hello World'])
def test_no_expressions(template):
    assert_equivalent_templates(t(template), Template(template))


@pytest.mark.parametrize(
    'template,final',
    [
        ('Hello World', t'Hello World'),
        ("Hello World", t'Hello World'),
        (r'Hello World', t'Hello World'),
        (r"Hello World", t'Hello World'),
        (u'Hello World', t'Hello World'),
        (u"Hello World", t'Hello World'),
        (f'Hello World', t'Hello World'),
        (f"Hello World", t'Hello World'),
        ('''Hello World''', t'Hello World'),
        ("""Hello World""", t'Hello World'),
        (r'''Hello World''', t'Hello World'),
        (r"""Hello World""", t'Hello World'),
        (u'''Hello World''', t'Hello World'),
        (u'''Hello World''', t'Hello World'),
        (f"""Hello World""", t'Hello World'),
        (f"""Hello World""", t'Hello World'),
    ],
)
def test_str_prefixes_no_expressions(template, final):
    assert_equivalent_templates(t(template), final)


@pytest.mark.parametrize(
    'template,final',
    [
        ('value: {s}', Template('value: ', Interpolation('foo', 's', None, ''))),
        ('value: {i}', Template('value: ', Interpolation(21, 'i', None, ''))),
        ('value: {j}', Template('value: ', Interpolation(3.14, 'j', None, ''))),
        ('value: {n}', Template('value: ', Interpolation(None, 'n', None, ''))),
        ('value: {b}', Template('value: ', Interpolation(True, 'b', None, ''))),
    ],
)
def test_variable_evaluation(template, final):
    b = True
    i = 21
    j = 3.14
    n = None
    s = 'foo'
    assert_equivalent_templates(t(template), final)


@pytest.mark.parametrize(
    'template,final',
    [
        ('value: {c + s}', Template('value: ', Interpolation('afoo', 'c + s', None, ''))),
        ('value: {i + j}', Template('value: ', Interpolation(24.14, 'i + j', None, ''))),
        ('value: {b or n}', Template('value: ', Interpolation(True, 'b or n', None, ''))),
        ('value: {b & i}', Template('value: ', Interpolation(1, 'b & i', None, ''))),
        ('value: {c * i}', Template('value: ', Interpolation('aaaaaaaaaaaaaaaaaaaaa', 'c * i', None, ''))),
    ],
)
def test_simple_expression(template, final):
    b = True
    c = 'a'
    i = 21
    j = 3.14
    n = None
    s = 'foo'
    assert_equivalent_templates(t(template), final)


@pytest.mark.parametrize(
    'template,final',
    [
        ('"hello" world', t'"hello" world'),
        ("\"hello\" world", t'"hello" world'),
        ('\'hello\' world', t"'hello' world"),
        ("'hello' world", t"'hello' world"),
        ('"hello" \'world\'', t'"hello" \'world\''),
        ("\"hello\" 'world'", t'"hello" \'world\''),
    ],
)
def test_quotes(template, final):
    assert_equivalent_templates(t(template), final)


def test_t_scope_not_leaked():
    with pytest.raises(NameError):
        t('secret is {template}')


def test_modifiable_var():
    explicit = [0, 1, 2, 3]
    implicit = defaultdict(int)
    formatted = t(
        "start {explicit} {implicit}\n"
        "modify {explicit.extend([4,5])} {implicit['key1'] == implicit['key2']}\n"
        "end {explicit} {implicit}"
    )
    final = t'''start {explicit} {implicit}
modify {explicit.extend([4,5])} {implicit['key1'] == implicit['key2']}
end {explicit} {implicit}'''
    assert_equivalent_templates(formatted, final)


def test_outer_scopes_reachable():
    top = None

    def outer():
        mid = 0

        def inner():
            low = 'A'
            nonlocal mid, top
            mid = 1
            top = False
            global outside
            outside = 6.2
            assert_equivalent_templates(
                t('out: {outside}; top: {top}; mid: {mid}; low: {low}'),
                t'out: {outside}; top: {top}; mid: {mid}; low: {low}'
            )

        assert_equivalent_templates(
            t('mid: {mid}'),
            t'mid: {mid}'
        )
        inner()
        assert_equivalent_templates(
            t('mid: {mid}'),
            t'mid: {mid}'
        )
        nonlocal top
        top = True
        global outside
        outside = 12.4
        assert_equivalent_templates(
            t('out: {outside}; top: {top}; mid: {mid}'),
            t'out: {outside}; top: {top}; mid: {mid}'
        )

    assert_equivalent_templates(t('top: {top}'), t'top: {top}')
    outer()
    assert_equivalent_templates(t('top: {top}'), t'top: {top}')
    global outside
    outside = 24.8
    assert_equivalent_templates(
        t('out: {outside}; top: {top}'),
        t'out: {outside}; top: {top}'
    )


def test_outer_scopes_modifiable():
    explicit = [0, 1, 2, 3]
    implicit = defaultdict(int)

    def inner():
        assert_equivalent_templates(t('{explicit.append(4)}'), Template(Interpolation(None, 'explicit.append(4)', None, '')))
        assert explicit == [0, 1, 2, 3, 4]
        assert implicit == {}
        assert_equivalent_templates(t("{implicit['first']}"), Template(Interpolation(0, "implicit['first']", None, '')))
        assert implicit == {'first': 0}

    inner()
    assert explicit == [0, 1, 2, 3, 4]
    assert implicit == {'first': 0}


@pytest.mark.parametrize('template,final', [('{name:*^{3+4}}', t'{name:*^{3+4}}')])
def test_nested_formats(template, final):
    assert_equivalent_templates(t(template), final)


@pytest.mark.parametrize(
    'template,final',
    [
        ('''" \'\'\'{"""'" "'"""}\'\'\' "''',
        t'''" \'\'\'{"""'" "'"""}\'\'\' "''',
        ),
        ('''"""{" \'\'\' "}"""''',
        t'''"""{" \'\'\' "}"""'''
        ),
        (''' {""" \'\'\' \'\'\' """} ''',
        t''' {""" \'\'\' \'\'\' """} ''',
        ),
        (''' {""" \\"\\"\\" """} ''',
        t''' {""" \\"\\"\\" """} ''',
        ),
    ],
)
def test_nested_quotes(template, final):
    assert_close_templates(t(template), final)


@pytest.mark.parametrize(
    'template,final',
    [
        ("""' \"\"\"{'''"' '"'''}\"\"\" '""",
        t"""' \"\"\"{'''"' '"'''}\"\"\" '"""),
        ('''"'{"'"''"'"}'"''',
        t'''"'{"'"''"'"}'"'''),
        (""" \'\'\'{''' ' '''}\'\'\' """,
        t''' \'\'\'{''' ' '''}\'\'\' '''),
        ('{None\n}',
        t'{None
}'),
        ('{1\t+\t2}',
        t'{1	+	2}'),
    ],
)
def test_requote(template, final):
    """These examples are known to trigger the _triple_repr fallback"""
    assert_close_templates(t(template), final)


@pytest.mark.parametrize(
    'template,final',
    [
        (
            ''' {t""" { t\'\'\' { t"{'X'}" } \'\'\' } """} ''',
            t''' {t""" { t''' { t"{'X'}" } ''' } """} ''',
        ),
        (
            ''' {t" { t' { t("{'X'}") } ' } "} ''',
            t''' {t" { t' { t("{'X'}") } ' } "} ''',
        ),
        (
            ''' {t(""" { t' { "X" } ' } """)} ''',
            t''' {t(""" { t' { "X" } ' } """)} ''',
        ),
        (
            ''' {t(""" { t(" { 'X' } ") } """)} ''',
            t''' {t(""" { t(" { 'X' } ") } """)} ''',
        ),
    ],
)
def test_recursive(template, final):
    assert_close_templates(t(template), final)


@pytest.mark.parametrize(
    'template,final',
    [
        ('{ord("\n")}', t"{ord('\n')}"),
        ('{"\t"}', t"{'\t'}"),
    ],
)
def test_escape(template, final):
    assert_equivalent_templates(t(template), final)


@pytest.mark.parametrize(
    'template,final',
    [
        ('{name # nothing to see here\n }', Template(Interpolation('foo', 'name', None, ''))),
        ('''{name # nothing to see here
         }''',
         Template(Interpolation('foo', 'name', None, '')),
        ),
        ('''{(name # fake bracket }
             * 2)}''',
         Template(Interpolation('foofoo', '(name \n             * 2)', None, '')),
        ),
    ],
)
def test_comment(template, final):
    assert_equivalent_templates(t(template), final)


@pytest.mark.parametrize(
    'error',
    [
        '{',
        '}',
        'foo }',
        'foo { bar',
        '{}',
        '{    }',
        '{name!x}',
    ],
)
def test_fstring_errors(error):
    with pytest.raises(SyntaxError) as why:
        t(error)
    assert 't-string' in why.exconly()


@pytest.mark.parametrize(
    'error',
    [
        '{pass}',
        '{\t}',
        '{ \\ }',
        '{name# from global space}',
        "{name + 'uniquote}",
    ],
)
def test_fstring_expr_errors(error):
    with pytest.raises(SyntaxError):
        t(error)
