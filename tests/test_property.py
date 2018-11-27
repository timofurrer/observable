import pytest

from observable import Observable
from observable.property import ObservableProperty


class _TestObject(Observable):
    def __init__(self, initial_value):
        super().__init__()
        self.value = initial_value

    @ObservableProperty
    def prop(self):
        return self.value

    @prop.setter
    def prop(self, value):
        self.value = value

    @prop.deleter
    def prop(self):
        self.value = 0


def _test_action(action):
    obj = _TestObject(1)

    @obj.on("before_" + action + "_prop")
    def handle_before(*args):
        nonlocal before, after
        assert before is False
        assert after is False
        if before_value is None:
            assert len(args) == 0
        else:
            assert len(args) == 1
            assert args[0] == before_value
        before = True

    @obj.on("after_" + action + "_prop")
    def handle_after(*args):
        nonlocal before, after
        assert before is True
        assert after is False
        if after_value is None:
            assert len(args) == 0
        else:
            assert len(args) == 1
            assert args[0] == after_value
        after = True

    before = False
    after = False
    if action == "get":
        before_value = None
        after_value = 1
        obj.prop
        assert obj.value == 1
    elif action == "set":
        before_value = 42
        after_value = 42
        obj.prop = 42
        assert obj.value == 42
    elif action == "del":
        before_value = None
        after_value = None
        del obj.prop
        assert obj.value == 0
    else:
        raise ValueError("invalid test action: {}".format(repr(action)))

    assert before is True
    assert after is True


def test_getter():
    """Verifies the before_get and after_get events are called with
    proper arguments at the right times."""

    _test_action("get")


def test_setter():
    """Verifies the before_set and after_set events are called with
    proper arguments at the right times."""

    _test_action("set")


def test_deleter():
    """Verifies the before_del and after_del events are called with
    proper arguments at the right times."""

    _test_action("del")


def test_unsupported_actions():
    """Verifies no events are triggered when get/set/del is not allowed
    on a property."""

    class Obj(Observable):
        prop = ObservableProperty()

    obj = Obj()

    @obj.on("before_get_prop")
    def handle_before():
        nonlocal before
        before = True

    @obj.on("after_get_prop")
    def handle(_after):
        nonlocal after
        after = True

    before = False
    after = False

    with pytest.raises(AttributeError):
        obj.prop
    assert before is False
    assert after is False

    with pytest.raises(AttributeError):
        obj.prop = 42
    assert before is False
    assert after is False

    with pytest.raises(AttributeError):
        del obj.prop
    assert before is False
    assert after is False


def test_create_with():
    """Verifies using ObservableProperty.create_with() results in correct
    event and observable parameters set."""

    prop = ObservableProperty.create_with(event="evt", observable="obs")()
    assert prop.event == "evt"
    assert prop.observable == "obs"


def test_custom_event():
    """Sets a custom event name and verifies that's used."""

    class Obj(Observable):
        @ObservableProperty.create_with(event="custom")
        def prop(self):
            return

    obj = Obj()

    @obj.on("before_get_custom")
    def handle():
        nonlocal called
        called = True

    called = False
    obj.prop
    assert called is True


def test_custom_observable_obj():
    """Sets a custom Observable object and verifies that's used."""

    obs = Observable()

    class Obj:
        @ObservableProperty.create_with(observable=obs)
        def prop(self):
            return

    obj = Obj()

    @obs.on("before_get_prop")
    def handle():
        nonlocal called
        called = True

    called = False
    obj.prop
    assert called is True


def test_custom_observable_attr():
    """Sets the attribute name of a custom Observable object and verifies
    that's used."""

    class Obj:
        def __init__(self):
            self.events = Observable()

        @ObservableProperty.create_with(observable="events")
        def prop(self):
            return

    obj = Obj()

    @obj.events.on("before_get_prop")
    def handle():
        nonlocal called
        called = True

    called = False
    obj.prop
    assert called is True
