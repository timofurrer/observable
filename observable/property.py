"""
    API for observing properties easily.
"""

import typing as T

from .core import Observable


class ObservableProperty(property):
    """
    A property that can be observed easily by listening for some special,
    auto-generated events. It's API is identical to that of the build-in
    property class.

    The getter, setter and deleter of ObservableProperty have to be
    methods of an object inheriting from Observable, so that ``on()``,
    ``trigger()`` etc. are available on the object holding the property..

    The following events are triggered:
    * "<name>_get"(value): Triggered whenever the property's value
      is retrieved.
    * "<name>_set"(value): Triggered after the property's value has
      been set.
    * "<name>_del"(): Triggered before the property is deleted.
    * "<name>_deleted"(): Triggered after the property deletion finished.

    <name> has to be replaced with the property's name. Note that names
    are taken from the individual functions supplied as getter, setter
    and deleter, so please name those functions like the property itself.
    """

    def __init__(
            self,
            fget: T.Callable = None, fset: T.Callable = None,
            fdel: T.Callable = None, doc: str = None
    ) -> None:
        if fdel:
            fdel = self._build_fdel(fdel)
        if fget:
            fget = self._build_fget(fget)
        if fset:
            fset = self._build_fset(fset)
        super().__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)

    @staticmethod
    def _build_fdel(
            fdel: T.Callable[[Observable], None],
    ) -> T.Callable[[Observable], None]:
        def handler(obj: Observable) -> None:
            obj.trigger("{}_del".format(fdel.__name__))
            fdel(obj)
            obj.trigger("{}_deleted".format(fdel.__name__))
        return handler

    @staticmethod
    def _build_fget(
            fget: T.Callable[[Observable], T.Any],
    ) -> T.Callable[[Observable], T.Any]:
        def handler(obj: Observable) -> T.Any:
            value = fget(obj)
            obj.trigger("{}_get".format(fget.__name__), value)
            return value
        return handler

    @staticmethod
    def _build_fset(
            fset: T.Callable[[Observable, T.Any], None],
    ) -> T.Callable[[Observable, T.Any], None]:
        def handler(obj: Observable, value: T.Any) -> None:
            fset(obj, value)
            obj.trigger("{}_set".format(fset.__name__), value)
        return handler

    def deleter(self, fdel: T.Callable[[Observable], None]) -> property:
        """Decorator to change the deleter of the property."""
        return super().deleter(self._build_fdel(fdel))

    def getter(self, fget: T.Callable[[Observable], T.Any]) -> property:
        """Decorator to change the getter of the property."""
        return super().getter(self._build_fget(fget))

    def setter(
            self, fset: T.Callable[[Observable, T.Any], None],
    ) -> property:
        """Decorator to change the setter of the property."""
        return super().setter(self._build_fset(fset))
