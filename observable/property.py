"""
    API for observing properties easily.
"""

import typing as T

import functools

from .core import Observable


__all__ = ["ObservableProperty"]


def _preserve_settings(method: T.Callable) -> T.Callable:
    """Decorator that ensures ObservableProperty-specific attributes
    are kept when using methods to change deleter, getter or setter."""

    @functools.wraps(method)
    def _wrapper(
            old: "ObservableProperty", handler: T.Callable
    ) -> "ObservableProperty":
        new = method(old, handler)
        new.event = old.event
        new.observable = old.observable
        return new

    return _wrapper


class ObservableProperty(property):
    """
    A property that can be observed easily by listening for some special,
    auto-generated events. It's API is identical to that of the build-in
    property class.

    The ObservableProperty needs an Observable object for triggering
    events. If the property is a member of an object of type Observable,
    that one will be used automatically. To specify a different Observable
    object, pass it as the observable keyword argument when initializing
    the ObservableProperty. You may also pass a string for observable,
    it's then looked for an attribute of that name in the containing
    object. This is useful to specify the name of an attribute which
    will only be created at object initialization and thus isn't there
    when defining the property.

    The following events, of which "after_set_<name>" is probably the
    one used most, are triggered:
    * "before_get_<name>"() and "after_get_<name>"(value)
    * "before_set_<name>"(value) and "after_set_<name>"(value)
    * "before_del_<name>"() and "after_del_<name>"()

    <name> has to be replaced with the property's name. Note that names
    are taken from the individual functions supplied as getter, setter
    and deleter, so please name those functions like the property itself.
    Alternatively, the name can be overwritten by specifying the name
    keyword argument when initializing the ObservableProperty.

    The convenience helper ObservableProperty.create_with() can be used
    as a decorator for creating ObservableProperty objects with custom
    event and/or observable. It returns a functools.partial() with the
    chosen attributes pre-set.

    Here's an example for using the event and observable keyword
    arguments:

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
    """

    def __init__(
            self, *args: T.Any,
            event: str = None, observable: T.Union[Observable, str] = None,
            **kwargs: T.Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.event = event
        self.observable = observable

    def __delete__(self, instance: T.Any) -> None:
        if self.fdel is not None:
            self._trigger_event(instance, self.fdel.__name__, "before_del")
        super().__delete__(instance)
        self._trigger_event(instance, self.fdel.__name__, "after_del")

    def __get__(self, instance: T.Any, owner: T.Any = None) -> T.Any:
        if instance is None:
            return super().__get__(instance, owner)
        if self.fget is not None:
            self._trigger_event(instance, self.fget.__name__, "before_get")
        value = super().__get__(instance, owner)
        if instance is None:
            return value
        self._trigger_event(instance, self.fget.__name__, "after_get", value)
        return value

    def __set__(self, instance: T.Any, value: T.Any) -> None:
        if self.fset is not None:
            self._trigger_event(instance, self.fset.__name__,
                                "before_set", value)
        super().__set__(instance, value)
        self._trigger_event(instance, self.fset.__name__, "after_set", value)

    def _trigger_event(
            self, holder: T.Any, alt_name: str, action: str, *event_args: T.Any
    ) -> None:
        """Triggers an event on the associated Observable object.
        The Holder is the object this property is a member of, alt_name
        is used as the event name when self.event is not set, action is
        prepended to the event name and event_args are passed through
        to the registered event handlers."""

        if isinstance(self.observable, Observable):
            observable = self.observable
        elif isinstance(self.observable, str):
            observable = getattr(holder, self.observable)
        elif isinstance(holder, Observable):
            observable = holder
        else:
            raise TypeError(
                "This ObservableProperty is no member of an Observable "
                "object. Specify where to find the Observable object for "
                "triggering events with the observable keyword argument "
                "when initializing the ObservableProperty."
            )

        name = alt_name if self.event is None else self.event
        event = "{}_{}".format(action, name)
        observable.trigger(event, *event_args)

    deleter = _preserve_settings(property.deleter)
    getter = _preserve_settings(property.getter)
    setter = _preserve_settings(property.setter)

    @classmethod
    def create_with(
            cls, event: str = None, observable: T.Union[str, Observable] = None
    ) -> T.Callable[..., "ObservableProperty"]:
        """Creates a partial application of ObservableProperty with
        event and observable preset."""

        return functools.partial(cls, event=event, observable=observable)
