# -*- coding: utf-8 -*-


class Observable:
    """event system for python"""
    class EventNotFound(Exception):
        """Raised if an event was not found"""
        def __init__(self, event):
            Exception.__init__(self, "Event '%s' was not found" % event)

    class HandlerNotFound(Exception):
        """Raised if an handler was not found"""
        def __init__(self, event, handler):
            Exception.__init__(self, "Handler '%s' was not found for event '%s'" % (event, handler))

    def __init__(self):
        self._events = {}

    def register_event(self, event):
        """register an event if it does not exist yet"""
        if event not in self._events:
            self._events[event] = {}

    def on(self, event, func=None):
        """register a handler to a specified event"""
        def _on_wrapper(func):
            if event not in self._events:
                self._events[event] = []
            self._events[event].append(func)
            return func

        if func:
            return _on_wrapper(func)
        else:
            return _on_wrapper

    def once(self, event, func=None):
        """register a handler to a specified event, but remove it when it is triggered"""
        def _once_wrapper(func):
            def _wrapper(*args, **kwargs):
                func(*args, **kwargs)
                self.off(event, _wrapper)
            return _wrapper

        if func:
            return self.on(event, _once_wrapper(func))
        else:
            return lambda func: self.on(event, _once_wrapper(func))

    def off(self, event=None, func=None):
        """unregister an event or handler from an event"""
        if not event:
            self._events = {}
            return True
        if event not in self._events:
            raise Observable.EventNotFound(event)
        if not func:
            self._events[event] = []
            return True
        if not isinstance(func, list):
            func = [func]
        for f in func:
            if f not in self._events[event]:
                raise Observable.HandlerNotFound(event, f.func_name)
            self._events[event].remove(f)

    def trigger(self, event, *args, **kwargs):
        """trigger all functions from an event"""
        if event not in self._events:
            raise Observable.EventNotFound(event)

        handled = False
        for func in self._events[event]:
            func(*args, **kwargs)
            handled = True
        return handled
