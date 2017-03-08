# -*- coding: utf-8 -*-

"""
    Event system for python
"""

from collections import defaultdict


class HandlerNotFound(Exception):
    """Raised if a handler wasn't found"""

    def __init__(self, event, handler):
        self.event = event
        self.handler = handler

    def __str__(self):
        return "Handler {} wasn't found for event {}".format(self.handler,
                                                             self.event)


class EventNotFound(Exception):
    """Raised if an event wasn't found"""

    def __init__(self, event):
        self.event = event

    def __str__(self):
        return "Event {} wasn't found".format(self.event)


class Observable(object):
    """Event system for python"""

    def __init__(self):
        self.events = defaultdict(list)

    def on(self, event, *handlers):  # pylint: disable=invalid-name
        """Register a handler to a specified event"""

        def _on_wrapper(*handlers):
            """wrapper for on decorator"""
            self.events[event].extend(handlers)
            return handlers[0]

        if handlers:
            return _on_wrapper(*handlers)
        return _on_wrapper

    def off(self, event=None, *handlers):
        """Unregister an event or handler from an event"""

        if not event:
            self.events.clear()
            return True

        if not event in self.events:
            raise EventNotFound(event)

        if not handlers:
            self.events.pop(event)
            return True

        for callback in handlers:
            if not callback in self.events[event]:
                raise HandlerNotFound(event, callback)
            while callback in self.events[event]:
                self.events[event].remove(callback)
        return True

    def once(self, event, *handlers):
        """Register a handler to a specified event, but remove it when it is triggered"""

        def _once_wrapper(*handlers):
            """Wrapper for 'once' decorator"""

            def _wrapper(*args, **kw):
                """Call wrapper"""
                for handler in handlers:
                    handler(*args, **kw)

                self.off(event, _wrapper)

            return _wrapper

        if handlers:
            return self.on(event, _once_wrapper(*handlers))
        return lambda x: self.on(event, _once_wrapper(x))

    def trigger(self, event, *args, **kw):
        """Trigger all functions which are subscribed to an event"""

        functions = self.events.get(event)
        if not functions:
            return False

        for event in functions:
            event(*args, **kw)

        return True
