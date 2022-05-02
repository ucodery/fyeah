import inspect


def f(template: str) -> str:
    if not isinstance(template, str):
        raise TypeError(f"Cannot format {type(template)}")
    parent_frame = inspect.stack()[1].frame
    # add quotes around template
    f_template = "f" + repr(template)
    try:
        formatted = eval(f_template, parent_frame.f_globals, parent_frame.f_locals)
    except SyntaxError:
        # wrapping template string in f triple quoted string is expensive and only
        # necessary in very unusual scenarios
        f_template = "f" + _triple_repr(template)
        formatted = eval(f_template, parent_frame.f_globals, parent_frame.f_locals)
    assert isinstance(formatted, str)
    return formatted


def _triple_repr(original_str):
    """repr can sometimes place additional backslashes in a string where
    there were none in the literal python file. This happens when the
    original string was triple quoted and both style of quotes are
    also used within the tripple quoted string because repr always
    returns a single quoted string
    """  # example: '''{""" 'quoted' """}'''
    expression_idxs = []
    original_repr = repr(original_str)

    next_expression_start = _find_opening_expression(original_repr, 0)
    while next_expression_start >= 0:
        next_expression_end = _find_closing_expression(
            original_repr, next_expression_start
        )
        if next_expression_end < 0:
            raise SyntaxError("f-string: expecting '}'")
        expression_idxs.insert(0, (next_expression_start, next_expression_end))
        next_expression_start = _find_opening_expression(
            original_repr, next_expression_end
        )

    found_tripple_single = False
    found_tripple_double = False
    unescaped_quote = '"' if original_repr[0] == "'" else "'"
    lit_end = len(original_repr) - 1
    for exp_start, exp_end in expression_idxs:
        for idx in range(lit_end, exp_end, -1):
            if original_repr[idx] == unescaped_quote:
                original_repr = original_repr[:idx] + "\\" + original_repr[idx:]
        single_quote_found = 0
        double_quote_found = 0
        escape_found = 0
        for idx in range(exp_end, exp_start, -1):
            if original_repr[idx] == "\\":
                if not single_quote_found and not double_quote_found:
                    raise SyntaxError(
                        "f-string expression part cannot include a backslash"
                    )
                escape_found += 1
                original_repr = original_repr[:idx] + original_repr[idx + 1 :]
            elif escape_found:
                if escape_found % 2 == 0:
                    raise SyntaxError(
                        "f-string expression part cannot include a backslash"
                    )
                escape_found = 0

            if original_repr[idx] not in ("'", "\\"):
                single_quote_found = 0
            if original_repr[idx] not in ('"', "\\"):
                double_quote_found = 0

            if original_repr[idx] == "'":
                single_quote_found += 1
                if single_quote_found >= 3:
                    found_tripple_single = True
            elif original_repr[idx] == '"':
                double_quote_found += 1
                if double_quote_found >= 3:
                    found_tripple_double = True
        lit_end = exp_start
    for idx in range(lit_end, 0, -1):
        if original_repr[idx] == unescaped_quote:
            original_repr = original_repr[:idx] + "\\" + original_repr[idx:]

    if found_tripple_single and found_tripple_double:
        # there is no way to support both ''' and """ without backslashes
        raise SyntaxError("f-string expression part cannot include a backslash")
    elif found_tripple_single:
        original_repr = '"""' + original_repr[1:-1] + '"""'
    else:
        original_repr = "'''" + original_repr[1:-1] + "'''"
    return original_repr


def _find_opening_expression(string, start):
    string_len = len(string)
    brace_idx = first_brace_idx = string.find("{", start)
    while brace_idx >= 0:
        while brace_idx + 1 < string_len and string[brace_idx + 1] == "{":
            brace_idx += 1
        if (brace_idx - first_brace_idx + 1) % 2 == 0:
            # just some literal { characters
            brace_idx = string.find("{", brace_idx)
            continue
        break
    return brace_idx


def _find_closing_expression(string, start):
    return string.find("}", start)
