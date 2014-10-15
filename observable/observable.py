from collections import defaultdict


class HandlerNotFound(Exception):
    """Raised if an handler was not found"""

    def __init__(self, event, handler):
        super(HandlerNotFound, self).__init__(
            "Handler '%s' was not found for event '%s'" % (event, handler))


class EventNotFound(Exception):
    """Raised if an event was not found"""

    def __init__(self, event):
        super(EventNotFound, self).__init__("Event '%s' was not found" % event)


class Observable(object):
    """event system for python"""

    HandlerNotFound = HandlerNotFound  # backward compatibiliy
    EventNotFound = EventNotFound  # backward compatibiliy

    def on(self, event, *handlers):
        """register a handler to a specified event"""

        def _on_wrapper(*handlers):
            self.events[event].extend(handlers)
            return handlers[0]

        if handlers:
            return _on_wrapper(*handlers)
        return _on_wrapper

    def off(self, event=None, *handlers):
        """unregister an event or handler from an event"""

        if not event:
            self.events.clear()
            return True

        if not event in self.events:
            raise EventNotFound(event)

        if not handlers:
            self.events.pop(event, None)
            return True

        for callback in handlers:
            if not callback in self.events[event]:
                raise HandlerNotFound(event, callback)
            while callback in self.events[event]:
                self.events[event].remove(callback)
        return True

    def once(self, event, *handlers):
        """register a handler to a specified event, but remove it when it is triggered"""

        def _once_wrapper(*handlers):
            def _wrapper(*args, **kw):
                list(map(lambda x: x(*args, **kw), handlers))
                self.off(event, _wrapper)
            return _wrapper

        if handlers:
            return self.on(event, _once_wrapper(*handlers))
        return lambda x: self.on(event, _once_wrapper(x))

    def trigger(self, event, *args, **kw):
        """trigger all functions from an event"""

        if not event in self.events or not self.events[event]:
            return False
        list(map(lambda x: x(*args, **kw), self.events[event]))
        return True

    @property
    def events(self):
        try:
            return self._events
        except AttributeError:
            self._events = defaultdict(list)
        return self._events
