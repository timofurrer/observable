# observable

[![Build Status](https://travis-ci.com/timofurrer/observable.svg?branch=master)](https://travis-ci.com/timofurrer/observable)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

**pyobservable** is a minimalist event system for python. It provides you an easy-to-use interface to trigger arbitrary functions when specific events occur.

```python
from observable import Observable

obs = Observable()

@obs.on("error")
def error_handler(message):
    # do some fancy error handling
    logging.error(f"An error occured: {message}")

...

def do_time_travel():
    # do some time traveling
    ...
    if year != 1291:
        obs.trigger("error", "Time travel to 1291 didn't work")
```

An ``ObservableProperty`` type is included as well, which makes observing
object properties a breeze.

**Note:** We are Python 3 only! Only Python Versions >= 3.5 are supported. Use [v0.3.2](https://pypi.org/project/observable/0.3.2/) for older Python Versions.


## How to use

Use a `pip` to install it from PyPI:

    pip install observable

After completion you can start using `observable`:

```python
from observable import Observable

obs = Observable()
```


## Usage of ``observable.Observable``

### `on`: Register event handler with `on`
There are two ways to register a function to an event.<br />
The first way is to register the event with a decorator like this:

```python
@obs.on("error")
def error_func(message):
    print("Error: %s" % message)
```

The second way is to register it with a method call:

```python
def error_func(message):
    print("Error: %s" % message)
obs.on("error", error_func)
```

### `once`: Register event handler with `once`
`once` works like `on`, but once the event handler is triggered it will be removed and cannot be triggered again.

### `trigger`: trigger event
You can trigger a registered event with the `trigger` method:

```python
obs.trigger("error", "This is my error message")
```

If no handler for the event `error` could be found an `Observable.NoHandlerFound`-Exception will be raised.

### `off`: remove handler and events
Remove a handler from a specified event:

```python
obs.off("error", error_func)
```

```python
obs.off("error", [error_func, second_error_func])
```

Remove all handlers from a specified event:

```python
obs.off("error")
```

Clear all events:

```python
obs.off()
```

### `get_all_handlers`, `get_handlers` and `is_registered`: Check which handlers are registered
Imagine you registered the following handlers:

```python
@obs.on("success")
def success_func():
    print("Success!")

@obs.on("error")
def error_func(message):
    print("Error: %s" % message)
```

Then you can do the following to inspect the registered handlers:
```python
>>> obs.get_all_handlers()
{'success': [<function success_func at 0x7f7f32d0a1e0>], 'error': [<function error_func at 0x7f7f32d0a268>]}
>>> obs.get_handlers("success")
[<function success_func at 0x7f7f32d0a1e0>]
>>> obs.get_handlers("other_event")
[]
```


## Usage of ``observable.property.ObservableProperty``

A property that can be observed easily by listening for some special,
auto-generated events. Its API is identical to that of the build-in
``property``.

The ``ObservableProperty`` needs an ``Observable`` object for
triggering events. If the property is an attribute of an object of
type ``Observable``, that one will be used automatically. To specify a
different ``Observable`` object, pass it as the ``observable`` keyword
argument when initializing the ``ObservableProperty``. You may also pass
a string for ``observable``, which looks for an attribute of that
name in the containing object. This is useful to specify the name of an
attribute which will only be created at object initialization and thus
isn't there when defining the property.

The following events, of which ``"after_set_<name>"`` is probably the
one used most, are triggered:

* ``"before_get_<name>"()`` and ``"after_get_<name>"(value)``
* ``"before_set_<name>"(value)`` and ``"after_set_<name>"(value)``
* ``"before_del_<name>"()`` and ``"after_del_<name>"()``

``<name>`` has to be replaced with the property's name. Note that names
are taken from the individual functions supplied as getter, setter and
deleter, so please name those functions like the property itself.
Alternatively, the name to use can be specified with the ``name``
keyword argument when initializing the ObservableProperty.

The convenience helper ``ObservableProperty.create_with()`` can be used
as a decorator for creating ``ObservableProperty`` objects with custom
``event`` and/or ``observable``. It returns a ``functools.partial()``
with the chosen attributes pre-set.

Here's an example for using the ``event`` and ``observable`` keyword
arguments:

```python
>>> from observable import Observable
>>> from observable.property import ObservableProperty
>>> class MyObject:
...     def __init__(self):
...         self.events = Observable()
...         self._value = 10
...     @ObservableProperty.create_with(event="prop", observable="events")
...     def some_obscure_name(self):
...         return self._value
...     @some_obscure_name.setter
...     def some_obscure_name(self, value):
...         self._value += value
...
>>> obj = MyObject()
>>> obj.obs.on("after_get_prop", lambda v: print("got", v))
>>> obj.obs.on("before_set_prop",
...            lambda v: print("setting", obs.some_obscure_name, v))
>>> obj.obs.on("after_set_prop", lambda v: print("set", v))
>>> obj.some_obscure_name = 32
got 10
setting 10 32
set 32
>>> obj.some_obscure_name
got 42
42
```


***

*<p align="center">This project is published under [MIT](LICENSE).<br>A [Timo Furrer](https://tuxtimo.me) project.<br>- :tada: -</p>*
