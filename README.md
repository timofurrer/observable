# pyobservable
> observable module for python
> *Version: 0.00.01*

***

Writing this module was an inspiration by https://github.com/js-coder/observable.<br /><br/>

**Author:** Timo Furrer <tuxtimo@gmail.com><br />
**Version:** 0.00.01<br />

## How to install
Just clone this repository with:

    $ git clone https://github.com/timofurrer/pyobservable.git

and install it with:

    # python setup.py install

*Note: you may need root privileges to execute setup.py*

### with `make`

When you have cloned the repository you can install it with

    sudo make install

If you want to install just if all nose tests are passing

    sudo make

## nose tests

There are some `nose` tests in the `test/` directory. <br />
If you haven't installed `nose` yet - do it with

    sudo pip install nose

After you've `nose` installed - test `pyobservable` with:

    make tests

The output should be something like:

    nosetests -v
    test event registering with the on decorator ... ok
    test event registering with the on method ... ok
    test event registering with the once decorator ... ok
    test event registering with the once method ... ok
    test event triggering with event registered with on ... ok
    test event triggering with event registered with once ... ok
    test exception raising for not existing events ... ok
    test obs.off method ... ok
    test exception raising in the off method ... ok
    test event triggering with arguments ... ok
    test event triggering with argument list ... ok
    test event triggering with keyword-arguments ... ok

    ----------------------------------------------------------------------
    Ran 12 tests in 0.003s

    OK

... where just the last `OK` is important!

## How to use
Import it with the following statement in your own program

```python
from observable import Observable

obs = Observable()
```

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
