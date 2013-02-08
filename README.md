# pyobservable
> observable module for python
> *Version: 0.00.01*

***

For this module I was inspired by https://github.com/js-coder/observable.<br /><br/>

**Author:** Timo Furrer<br />
**Email:** tuxtimo@gmail.com<br />
**Version:** 0.00.01<br />

## How to install
Just clone this repository with:

    $ git clone https://github.com/timofurrer/pyobservable.git

and install it with:

    # python setup.py install

*Note: you may need root privileges to execute setup.py*

## How to use
Import it with the following statement in your own program

```python
from observable import Observable

obs = Observable()
```

### Register event handler with `on`
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

### Register event handler with `once`
`once` works like `on`, but once the event handler is triggered it will be removed and cannot be triggered again.

### trigger event
You can trigger a registered event with the `trigger` method:

```python
obs.trigger("error", "This is my error message")
```

If no handler for the event `error` could be found an `Observable.NoHandlerFound`-Exception will be raised.

### remove handler and events
Remove a handler from a specified event:

```python
obs.remove_handler("error", error_func)
```

Remove all handlers from a specified event:

```python
obs.clear_handlers("error")
```

Clear all events:

```python
obs.clear_events()
```
