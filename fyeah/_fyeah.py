import inspect


def f(template: str) -> str:
    if not isinstance(template, str):
        raise TypeError(f'Cannot format {type(template)}')
    parent_frame = inspect.stack()[1].frame
    # add quotes around template
    f_template = 'f' + repr(template)
    try:
        formatted = eval(f_template, parent_frame.f_globals, parent_frame.f_locals)
    except SyntaxError as repr_error:
        # wrapping template string in f triple quoted string is expensive and only
        # necessary in very unusual scenarios
        f_template = 'f' + _literal_only_repr(template)
        try:
            formatted = eval(f_template, parent_frame.f_globals, parent_frame.f_locals)
        except SyntaxError:
            # custom quoting didn't help, show the original error
            raise repr_error from None
    assert isinstance(formatted, str)
    return formatted


def _literal_only_repr(original_str):
    """repr can sometimes place too many backslashes in expression fields
    because f-string expression can contain backslashes starting with 3.12
    but the parser sees most '\' as the line continuation token

    example: '{None\n}' should tokenize as "None then a Newline" not
             "None then LineContinuation then 'n'"; the second is illegal
    """
    # zero-width expression so the 0-position literal also gets checked
    expression_idxs = [(-1, -1)]
    next_expression_start = _find_opening_expression(original_str, 0)
    while next_expression_start >= 0:
        next_expression_end = _find_closing_expression(
            original_str, next_expression_start
        )
        expression_idxs.insert(0, (next_expression_start, next_expression_end))
        next_expression_start = _find_opening_expression(
            original_str, next_expression_end
        )

    original_repr = original_str
    literal_end = len(original_str) - 1
    for expression_start, expression_end in expression_idxs:
        for idx in range(literal_end, expression_end, -1):
            chr = original_str[idx]
            if chr in ('"', "'"):
                # repr of a single quote will never add a backslash, instead it always uses opposite quotes to contain it
                original_repr = original_repr[:idx] + '\\' + original_repr[idx:]
            raw_repr = repr(chr)[1:-1]
            if chr != raw_repr:
                original_repr = (
                    original_repr[:idx] + raw_repr + original_repr[idx + 1 :]
                )
        literal_end = expression_start

    return "'" + original_repr + "'"


def _find_opening_expression(string, start):
    string_len = len(string)
    brace_idx = first_brace_idx = string.find('{', start)
    while brace_idx >= 0:
        while brace_idx + 1 < string_len and string[brace_idx + 1] == '{':
            brace_idx += 1
        if (brace_idx - first_brace_idx + 1) % 2 == 0:
            # just some literal { characters
            brace_idx = string.find('{', brace_idx)
            continue
        break
    return brace_idx


def _find_closing_expression(string, start):
    next_line = start
    while 0 <= next_line < len(string):
        brace_idx = string.find('}', next_line)
        if brace_idx < 0:
            raise SyntaxError("f-string: expecting '}'")

        comment_idx = string.find('#', next_line)
        singleq_idx = string.find("'", next_line)
        doubleq_idx = string.find('"', next_line)

        # brace before any comment or string
        if (
            (comment_idx == -1 or brace_idx < comment_idx)
            and (singleq_idx == -1 or brace_idx < singleq_idx)
            and (doubleq_idx == -1 or brace_idx < doubleq_idx)
        ):
            return brace_idx

        # comment before any string
        if comment_idx != -1 and (
            (singleq_idx == -1 or comment_idx < singleq_idx)
            and (doubleq_idx == -1 or comment_idx < doubleq_idx)
        ):
            nextnl_idx = string.find('\n', comment_idx)
            if nextnl_idx == -1:
                raise SyntaxError("'{' was never closed")
            next_line = nextnl_idx + 1
            continue

        elif singleq_idx != -1 and (doubleq_idx == -1 or singleq_idx < doubleq_idx):
            quote_idx = singleq_idx
        else:
            # doubleq_idx must be >=0 or else brace_idx would have already been returned
            quote_idx = doubleq_idx
        quote, fstring = _quote_type(string, quote_idx)
        if quote is None:
            next_line += 1
        elif fstring:
            inside_fstring = quote_idx + 1
            while 0 <= inside_fstring < len(string):
                next_quote_end = _find_string_end(string, inside_fstring, quote)
                next_expr_open = _find_opening_expression(string, inside_fstring)
                if next_expr_open == -1 or next_quote_end < next_expr_open:
                    next_line = next_quote_end + 1
                    break
                else:
                    inside_fstring = _find_closing_expression(string, next_expr_open)
            else:
                raise SyntaxError("f-string: expecting '}'")
        else:
            next_line = _find_string_end(string, quote_idx, quote) + 1

    raise SyntaxError("f-string: expecting '}'")


def _quote_type(string, qidx):
    """Given the index of a quote character, figure out what string it is starting

    This function assumes that for a repeating sequence of quotes, qidx is
    the first, or that all earlier quotes have already been checked.

    Possible options are:
    single-quote string
    double-quote string
    triple single-quote string
    triple double-quote string
    single-quote f-string
    double-quote f-string
    triple single-quote f-string
    triple double-quote f-string
    not a string (escaped quote)

    Returns a tuple of
      quote: one of ' " ''' \"\"\" or None
      f-string: bool
    """
    escapes = 0
    for c in range(qidx - 1, -1, -1):
        if c != '\\':
            break
        escapes += 1
    if escapes % 2 == 1:
        return None, False

    if string[qidx - 1 : qidx] in ('f', 'F') or (
        string[qidx - 1 : qidx] in ('r', 'R')
        and string[qidx - 2 : qidx - 1] in ('f', 'F')
    ):
        fstring = True
    else:
        fstring = False

    if string[qidx + 1 : qidx + 3] == string[qidx] * 2:
        return string[qidx : qidx + 3], fstring
    else:
        return string[qidx], fstring


def _find_string_end(string, start, quote):
    """Return the index of the final quote closing the string

    quote can be " ' \"\"\" or '''
    raises a SyntaxError when the string has no end
    """
    nextq_idx = string.find(quote, start)
    if nextq_idx == -1 and len(quote) == 3:
        raise SyntaxError('unterminated triple-quoted string literal')
    else:
        nextnl_idx = string.find('\n', start)
        if nextq_idx == -1 or nextnl_idx != -1 and (nextnl_idx < nextq_idx):
            raise SyntaxError('unterminated string literal')

    escapes = 0
    for c in range(nextq_idx - 1, -1, -1):
        if c != '\\':
            break
        escapes += 1
    if escapes % 2 == 1:
        return _find_string_end(string, nextq_idx + 1, quote)

    if len(quote) == 3:
        return nextq_idx + 2
    else:
        return nextq_idx
