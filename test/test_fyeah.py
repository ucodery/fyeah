from collections import defaultdict

import pytest

from fyeah import f


# fmt: off
# ruff: noqa: F541
# ruff: noqa: F841

# Global vars for use in f-strings outside of test functions
name = 'foo'
outside = 3.1


def test_debug_expr():
    assert f('look {name=}') == "look name='foo'"
    assert f('look {outside  = }') == 'look outside  = 3.1'


@pytest.mark.parametrize('template', ['', 'Hello World'])
def test_no_expressions(template):
    assert f(template) == template
    assert f(f(template)) == template
    assert f(f(f(template))) == template


@pytest.mark.parametrize(
    'template,final',
    [
        ('Hello World', 'Hello World'),
        ("Hello World", 'Hello World'),
        (r'Hello World', 'Hello World'),
        (r"Hello World", 'Hello World'),
        (u'Hello World', 'Hello World'),
        (u"Hello World", 'Hello World'),
        (f'Hello World', 'Hello World'),
        (f"Hello World", 'Hello World'),
        ('''Hello World''', 'Hello World'),
        ("""Hello World""", 'Hello World'),
        (r'''Hello World''', 'Hello World'),
        (r"""Hello World""", 'Hello World'),
        (u'''Hello World''', 'Hello World'),
        (u'''Hello World''', 'Hello World'),
        (f"""Hello World""", 'Hello World'),
        (f"""Hello World""", 'Hello World'),
    ],
)
def test_str_prefixes_no_expressions(template, final):
    assert f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        ('value: {s}', 'value: foo'),
        ('value: {i}', 'value: 21'),
        ('value: {j}', 'value: 3.14'),
        ('value: {n}', 'value: None'),
        ('value: {b}', 'value: True'),
    ],
)
def test_variable_insertion(template, final):
    b = True
    i = 21
    j = 3.14
    n = None
    s = 'foo'
    assert f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        ('value: {c + s}', 'value: afoo'),
        ('value: {i + j}', 'value: 24.14'),
        ('value: {b or n}', 'value: True'),
        ('value: {b & i}', 'value: 1'),
        ('value: {c * i}', 'value: aaaaaaaaaaaaaaaaaaaaa'),
    ],
)
def test_simple_expression(template, final):
    b = True
    c = 'a'
    i = 21
    j = 3.14
    n = None
    s = 'foo'
    assert f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        ('"hello" world', '"hello" world'),
        ("\"hello\" world", '"hello" world'),
        ('\'hello\' world', "'hello' world"),
        ("'hello' world", "'hello' world"),
        ('"hello" \'world\'', '"hello" \'world\''),
        ("\"hello\" 'world'", '"hello" \'world\''),
    ],
)
def test_quotes(template, final):
    assert f(template) == final


def test_reformat_template():
    template = 'Global name: {name}; Local name: {{name}}'
    first_format = f(template)
    assert first_format == 'Global name: foo; Local name: {name}'
    name = 'bar'
    second_format = f(first_format)
    assert second_format == 'Global name: foo; Local name: bar'


@pytest.mark.parametrize(
    'template,final', [('Hello World', 'Hello World'), ('Hello {name}', 'Hello foo')]
)
def test_no_expr_itempotent(template, final):
    """Test that passing the same string, with no bracket pairs, through f produces no changes"""
    for _ in range(8):
        template = f(template)
        assert f(template) == final


def test_f_scope_not_leaked():
    with pytest.raises(NameError):
        f('secret is {template}')


def test_modifiable_var():
    explicit = [0, 1, 2, 3]
    implicit = defaultdict(int)
    formatted = f(
        'start {explicit} {implicit}\n'
        'modify {explicit.extend([4,5])} {implicit["key1"] == implicit["key2"]}\n'
        'end {explicit} {implicit}'
    )
    final = (
        "start [0, 1, 2, 3] defaultdict(<class 'int'>, {})\n"
        'modify None True\n'
        "end [0, 1, 2, 3, 4, 5] defaultdict(<class 'int'>, {'key1': 0, 'key2': 0})"
    )
    assert formatted == final


def test_outer_scopes_reachable():
    top = None

    def outer():
        mid = 0

        def inner():
            low = 'A'
            assert (
                f('out: {outside}; top: {top}; mid: {mid}; low: {low}')
                == 'out: 3.1; top: None; mid: 0; low: A'
            )
            nonlocal mid, top
            mid = 1
            top = False
            global outside
            outside = 6.2
            assert (
                f('out: {outside}; top: {top}; mid: {mid}; low: {low}')
                == 'out: 6.2; top: False; mid: 1; low: A'
            )

        assert (
            f('out: {outside}; top: {top}; mid: {mid}') == 'out: 3.1; top: None; mid: 0'
        )
        inner()
        assert (
            f('out: {outside}; top: {top}; mid: {mid}')
            == 'out: 6.2; top: False; mid: 1'
        )
        nonlocal top
        top = True
        global outside
        outside = 12.4
        assert (
            f('out: {outside}; top: {top}; mid: {mid}')
            == 'out: 12.4; top: True; mid: 1'
        )

    assert f('out: {outside}; top: {top}') == 'out: 3.1; top: None'
    outer()
    assert f('out: {outside}; top: {top}') == 'out: 12.4; top: True'
    global outside
    outside = 24.8
    assert f('out: {outside}; top: {top}') == 'out: 24.8; top: True'


def test_outer_scopes_modifiable():
    explicit = [0, 1, 2, 3]
    implicit = defaultdict(int)

    def inner():
        assert f('{explicit.append(4)}') == 'None'
        assert explicit == [0, 1, 2, 3, 4]
        assert implicit == {}
        assert f('{implicit["first"]}') == '0'
        assert implicit == {'first': 0}

    inner()
    assert explicit == [0, 1, 2, 3, 4]
    assert implicit == {'first': 0}


@pytest.mark.parametrize('template,final', [('{name:*^{3+4}}', '**foo**')])
def test_nested_formats(template, final):
    assert f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        # this was the deepest level of quoting that could occur in an fstring expression
        # because backslashes and quote release were disallowed prior to 3.12
        ('''" \'\'\'{"""'" "'"""}\'\'\' "''', '''" \'\'\'\'" "\'\'\'\' "'''),
        ('''"""{" \'\'\' "}"""''', '''""" \'\'\' """'''),
        # starting with 3.12 there is no maximum quote depth
        (''' {""" \'\'\' \'\'\' """} ''', """  ''' '''  """),
        (''' {""" \\"\\"\\" """} ''', """  \\"\\"\\"  """),
    ],
)
def test_nested_quotes(template, final):
    assert f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        ("""' \"\"\"{'''"' '"'''}\"\"\" '""", """' \"\"\"\"' '\"\"\"\" '"""),
        ('''"'{"'"''"'"}'"''', '''"\'\'\'\'"'''),
        (''' \'\'\'{\'\'\' \' \'\'\'}\'\'\' ''', """ ''' ' ''' """),
        ('{None\n}', 'None'),
        ('{1\t+\t2}', '3'),
    ],
)
def test_requote(template, final):
    """These examples are known to trigger the _triple_repr fallback"""
    assert f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        (''' {f" { f' { f"{'X'}" } ' } "} ''', '   X   '),
        (''' {f" { f' { f("{'X'}") } ' } "} ''', '   X   '),
        (''' {f(" { f' { 'X' } ' } ")} ''', '   X   '),
        (''' {f(""" { f(" { 'X' } ") } """)} ''', '   X   '),
    ],
)
def test_recursive(template, final):
    assert f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        ('{ord("\n")}', '10'),
        ('{"\t"}', '\t'),
    ],
)
def test_escape(template, final):
    assert f(template) == final


@pytest.mark.parametrize(
    'template,final',
    [
        ('{name # nothing to see here\n }', 'foo'),
        ('''{name # nothing to see here
         }''',
         'foo',
        ),
        ('''{(name # fake bracket }
             * 2)}''',
         'foofoo',
        ),
    ],
)
def test_comment(template, final):
    assert f(template) == final


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
        f(error)
    assert 'f-string' in why.exconly()


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
        f(error)


@pytest.mark.parametrize(
    'template,final',
    [
        ("unlock {d['key']}", 'unlock door'),
        ("debug {d=}", "debug d={'key': 'door'}"),
    ]
)
def test_not_in_format(template, final):
    d = {'key': 'door'}
    assert f(template) == final
