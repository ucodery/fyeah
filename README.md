# F-yeah!
#### Reusable f-strings
Shed all outdated format sytles from your code.
With F-yeah Just add parentheses and be on your way.

## Usage
#### No more copying around f-strings
Keep your templates DRY without reverting to older format styles.
```python
def action1(value):
    assert isinstance(value, int), 'Expected value to be an integer, got {type(value)} instead'
    return value * value

def action2(value):
    assert isinstance(value, int), 'Expected value to be an integer, got {type(value)} instead'
    return value ** value
```
Just write the template once to get consistent strings that stay in sync.
```python
from fyeah import f
bad_check = 'Expected value to be an integer, got {type(value)} instead'

def action1(value):
    assert isinstance(value, int), f(bad_check)
    return value * value

def action2(value):
    assert isinstance(value, int), f(bad_check)
    return value ** value
```
----
#### No more format calls, ever!
Consolidate on f-string style format for all templates, local or global.
```python
bad_check = 'expected value to be an integer, got {type(value)} instead'

def action1(value):
    assert isinstance(value, int), bad_check.format(value=value)
    return value * value

def action2(value):
    assert isinstance(value, int), bad_check.format(value=value)
    return value ** value
```
Just use the same format string as a reusable f-string instead.
```python
from fyeah import f
bad_check = 'Expected value to be an integer, got {type(value)} instead'

def action1(value):
    assert isinstance(value, int), f(bad_check)
    return value * value

def action2(value):
    assert isinstance(value, int), f(bad_check)
    return value ** value
```
