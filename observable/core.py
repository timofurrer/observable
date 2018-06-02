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
        self._events = defaultdict(list)

    def get_all_handlers(self):
        """Returns a dict with event names as keys and lists of
        registered handlers as values."""

        events = {}
        for event, handlers in self._events.items():
            events[event] = list(handlers)
        return events

    def get_handlers(self, event):
        """Returns a list of handlers registered for the given event."""

        return list(self._events.get(event, []))

    def is_registered(self, event, handler):
        """Returns whether the given handler is registered for the
        given event."""

        return handler in self._events.get(event, [])

    def on(self, event, *handlers):  # pylint: disable=invalid-name
        """Register a handler to a specified event"""

        def _on_wrapper(*handlers):
            """wrapper for on decorator"""
            self._events[event].extend(handlers)
            return handlers[0]

        if handlers:
            return _on_wrapper(*handlers)
        return _on_wrapper

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

    def off(self, event=None, *handlers):
        """Unregister an event or handler from an event"""

        if not event:
            self._events.clear()
            return True

        if not event in self._events:
            raise EventNotFound(event)

        if not handlers:
            self._events.pop(event)
            return True

        for callback in handlers:
            if not callback in self._events[event]:
                raise HandlerNotFound(event, callback)
            while callback in self._events[event]:
                self._events[event].remove(callback)
        return True


    def trigger(self, event, *args, **kw):
        """Trigger all functions which are subscribed to an event"""

        functions = self._events.get(event)
        if not functions:
            return False

        for event in functions:
            event(*args, **kw)

        return True
