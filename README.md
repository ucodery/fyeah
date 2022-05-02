[![fyeah - reusable f-strings](https://raw.githubusercontent.com/ucodery/fyeah/master/art/logo.png)](https://github.com/ucodery/fyeah)
------

[![PyPI version](https://badge.fury.io/py/f-yeah.svg)](https://badge.fury.io/py/f-yeah)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.org/project/f-yeah/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

#### Reusable f-strings
Unify on one format style.
With F-yeah Just add parentheses and be on your way.

## Usage
Keep using f-string formatting, but when you need to re-use a template, use the
`f` function instead of the `f` literal

These two lines are equivalent
```python
print(f'about to put {os.getpid()} to sleep')
print(f('about to put {os.getpid()} to sleep'))
# "about to put 421 to sleep"
```

No longer choose between copying around f-string literals or continuing to use
old-style format() calls.

Instead of this
```python
def mul(value):
    assert isinstance(value, int), 'Expected value to be an integer, got {type(value)} instead'
    return value * value

def pow(value):
    assert isinstance(value, int), 'Expected value to be an integer, got {type(value)} instead'
    return value ** value
```
Or this
```python
bad_check = 'expected value to be an integer, got {type(value)} instead'

def mul(value):
    assert isinstance(value, int), bad_check.format(value=value)
    return value * value

def pow(value):
    assert isinstance(value, int), bad_check.format(value=value)
    return value ** value
```
Just write the template once to get consistent strings that stay in sync.
```python
from fyeah import f
bad_check = 'Expected value to be an integer, got {type(value)} instead'

def mul(value):
    assert isinstance(value, int), f(bad_check)
    return value * value

def pow(value):
    assert isinstance(value, int), f(bad_check)
    return value ** value
```

#### Why would I use a function over the literal?
f-string literals are evaluated when they are created. This makes situations like the
following impossible.
```python
class BaseListRunner:
    command = ['ls']
    args = []
    notify_running = '{self.__class__.__name__} is executing {self.command} with "{" ".join(self.args)}"'

    def run(self):
        log.debug(f(self.notify_running))
        subprocess.call(self.command + args)

class AllListRunner:
    def __init__(self):
        self.args.append('-A')

AllListRunner().run()
# DEBUG: AllListRunnner is executing ls with "-A"
```

#### Why would I use F-yeah instead of the format() builtin?
Although the format mini-language and f-strings share a lot of syntax, they have
diverged somewhat. You could use only format() for all your strings, but format()
is more verbose and less flexible as compared to f-strings; enough so that f-strings
were adopted into the language. Using F-yeah makes the following possible.
```python
G_COUNT = 0
count_tracker = '{G_COUNT=} at {datetime.datetime.utcnow():%H:%M:%S}'

def acquire():
    G_COUNT += 1
    log.debug(f(count_tracker))

def release():
    G_COUNT -= 1
    log.debug(f(count_tracker))

def check():
    log.debug(f(count_tracker))
    return G_COUNT
```
