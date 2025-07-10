def escape(string, stype):
    return _Escape(stype)(string)


class _Escape:
    """Given a string containing expression components, return an escaped view of that string that is valid source representation"""

    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, original_str):
        self.original_str = original_str
        self.looking = 0
        self.repr_parts = []
        self._escape()
        return ''.join((self.prefix, "'", *self.repr_parts, "'"))

    def _escape(self, end=None):
        # all strings start as a literal; literal can be 0-width
        done = self._escape_literal(end)
        while not done:
            self._escape_expr()
            done = self._escape_literal(end)

    def _escape_literal(self, end=None):
        while self.looking < len(self.original_str):
            if self.original_str[self.looking : self.looking + 2] == '{{':
                # two {{ don't start an expr
                self.repr_parts.append('{{')
                self.looking += 2
                continue
            if self.original_str[self.looking] == '{':
                self.repr_parts.append('{')
                self.looking += 1
                return False
            if end and end == self.original_str[self.looking : self.looking + len(end)]:
                # found the other end of a nested expr-containing string
                # don't need to escape quotes as this is a string token
                self.repr_parts.append(end)
                self.looking += len(end)
                return True

            raw_chr = self.original_str[self.looking]
            raw_repr = repr(raw_chr)[1:-1]
            if raw_chr in ('"', "'"):
                # repr of a single quote will never add a backslash, instead it always uses opposite quotes to contain it
                raw_repr = '\\' + raw_chr
            if raw_chr != raw_repr:
                self.repr_parts.append(raw_repr)
            else:
                self.repr_parts.append(raw_chr)
            self.looking += 1

        if end:
            raise SyntaxError('unterminated string literal')
        return True

    def _escape_expr(self):
        braces = 0
        while self.looking < len(self.original_str):
            here = self.original_str[self.looking]
            if here == '}':
                self.repr_parts.append(here)
                self.looking += 1
                if braces > 0:
                    braces -= 1
                else:
                    return
            elif here == '#':
                nl = self.original_str.find('\n', self.looking)
                if nl == -1:
                    raise SyntaxError("'{' was never closed")
                self.repr_parts.append(self.original_str[self.looking : nl + 1])
                self.looking = nl + 1
            elif here in ('"', "'"):
                quote, contains_exprs = _quote_type(self.original_str, self.looking)
                if contains_exprs:
                    self.repr_parts.append(quote)
                    self.looking += len(quote)
                    self._escape(end=quote)
                elif quote is not None:
                    there = _find_string_end(self.original_str, self.looking, quote)
                    if len(quote) == 1:
                        new_string = self.original_str[self.looking + 1 : there]
                    else:
                        new_string = self.original_str[self.looking + 3 : there - 2]
                    self.repr_parts.append(repr(new_string))
                    self.looking = there + 1
                else:
                    self.repr_parts.append(self.original_str[self.looking])
                    self.looking += 1
            else:
                self.repr_parts.append(here)
                self.looking += 1
                if here == '{':
                    # dict or set or format expr
                    braces += 1

        raise SyntaxError(f"{self.prefix}-string: expecting '}}'")


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
    single-quote t-string
    double-quote t-string
    triple single-quote t-string
    triple double-quote t-string
    not a string (escaped quote)

    Returns a tuple of
      quote: one of ' " ''' \"\"\" or None
      contains_exprs: bool
    """
    escapes = 0
    for c in range(qidx - 1, -1, -1):
        if c != '\\':
            break
        escapes += 1
    if escapes % 2 == 1:
        return None, False

    if string[qidx - 1 : qidx] in ('f', 'F', 't', 'T') or (
        string[qidx - 1 : qidx] in ('r', 'R')
        and string[qidx - 2 : qidx - 1] in ('f', 'F', 't', 'T')
    ):
        contains_exprs = True
    else:
        contains_exprs = False

    if string[qidx + 1 : qidx + 3] == string[qidx] * 2:
        return string[qidx : qidx + 3], contains_exprs
    else:
        return string[qidx], contains_exprs


def _find_string_end(string, start, quote):
    """Return the index of the final quote closing the string

    quote can be " ' \"\"\" or '''
    raises a SyntaxError when the string has no end
    """
    start += len(quote)
    nextq_idx = string.find(quote, start)
    if nextq_idx == -1:
        if len(quote) == 3:
            raise SyntaxError('unterminated triple-quoted string literal')
        # note, at this point we can't tell what the difference between what
        # was a newline or a \n in the original source, so don't check for
        # unterminated string literals by line-end, they will all get escaped to \n
        raise SyntaxError('unterminated string literal')

    escapes = 0
    for c in range(nextq_idx - 1, -1, -1):
        if c != '\\':
            break
        escapes += 1
    if escapes % 2 == 1:
        return _find_string_end(string, nextq_idx, quote)

    if len(quote) == 3:
        return nextq_idx + 2
    else:
        return nextq_idx
