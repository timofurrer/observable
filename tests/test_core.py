import threading

import pytest

from observable import Observable, EventNotFound, HandlerNotFound


def test_on_decorator():
    """test event registering with the on decorator"""
    obs = Observable()

    @obs.on("on_test")
    def on_test():
        pass

    assert on_test in obs._events["on_test"]


def test_on():
    """test event registering with the on method"""
    obs = Observable()

    def on_test():
        pass

    obs.on("on_test", on_test)
    assert on_test in obs._events["on_test"]


def test_once_decorator():
    """test event registering with the once decorator"""
    obs = Observable()

    @obs.once("once_test")
    def once_test():
        pass

    assert once_test in obs._events["once_test"]
    assert obs.trigger("once_test")
    assert once_test not in obs._events["once_test"]


def test_once():
    """test event registering with the once method"""
    obs = Observable()

    def once_test():
        pass

    obs.once("once_test", once_test)

    assert len(obs._events["once_test"]) == 1
    assert obs.trigger("once_test")
    assert obs._events["once_test"] == []


def test_on_trigger():
    """test event triggering with event registered with on"""
    obs = Observable()

    obj = threading.local()
    obj.called = False

    @obs.on("on_test")
    def on_test(obj):
        obj.called = True

    assert obs._events == {"on_test": [on_test]}
    assert obs.trigger("on_test", obj)
    assert obj.called


def test_once_trigger():
    """test event triggering with event registered with once"""
    obs = Observable()

    obj = threading.local()
    obj.called = False

    @obs.once("once_test")
    def once_test(obj):
        obj.called = True

    assert len(obs._events["once_test"]) == 1
    assert obs._events["once_test"] == [once_test]
    assert obs.trigger("once_test", obj)
    assert obj.called
    assert obs._events["once_test"] == []
    assert not obs.trigger("once_test", obj)


def test_no_event_for_trigger():
    """test exception raising for not existing events"""
    obs = Observable()

    assert not obs.trigger("no_existing_event")

    with pytest.raises(EventNotFound):
        obs.off("no_existing_event")


def test_off():
    """test obs.off method"""
    obs = Observable()

    @obs.on("on_test")
    def on_test():
        pass

    assert obs._events["on_test"] == [on_test]
    assert obs.trigger("on_test")

    obs.off("on_test", on_test)

    assert obs._events["on_test"] == []

    obs.off()

    assert not obs._events

    @obs.on("more_than_one_event")
    def func1():
        pass

    @obs.on("more_than_one_event")
    def func2():
        pass

    @obs.on("more_than_one_event")
    def func3():
        pass

    assert obs._events["more_than_one_event"] == [func1, func2, func3]
    obs.off("more_than_one_event", func2)
    assert obs._events["more_than_one_event"] == [func1, func3]
    obs.off("more_than_one_event")
    assert obs._events["more_than_one_event"] == []


def test_off_exceptions():
    """test exception raising in the off method"""
    obs = Observable()

    with pytest.raises(EventNotFound):
        obs.off("non_existing_event")

    @obs.on("some_event")
    def some_assigned_handler():
        pass

    def some_non_assigned_handler():
        pass

    assert some_assigned_handler in obs._events["some_event"]
    assert some_non_assigned_handler not in obs._events["some_event"]

    with pytest.raises(HandlerNotFound):
        obs.off("some_event", some_non_assigned_handler)


def test_trigger_arg():
    """test event triggering with arguments"""
    obs = Observable()

    @obs.on("some_test")
    def some_test(some_data):
        assert some_data == "some data"

    assert obs.trigger("some_test", "some data")


def test_trigger_args():
    """test event triggering with argument list"""
    obs = Observable()

    @obs.on("some_test")
    def some_test(some_data, some_other_data):
        assert some_data is True
        assert some_other_data is False

    assert obs.trigger("some_test", *[True, False])


def test_trigger_kwargs():
    """test event triggering with keyword-arguments"""
    obs = Observable()

    @obs.on("some_test")
    def some_test(some_data=True, some_other_data=False):
        assert some_data is False
        assert some_other_data is True

    assert obs.trigger("some_test", some_other_data=True, some_data=False)


def test_on_multiple_handlers():
    """test event registering with the on method and multiple handlers"""
    obs = Observable()

    results = []

    def some_test(*args, **kw):
        results.append(1)

    def some_test_2(*args, **kw):
        results.append(2)

    obs.on("some_test", some_test, some_test_2)
    assert len(obs._events["some_test"]) == 2

    obs.trigger("some_test")
    assert results == [1, 2]


def test_off_multiple_handlers():
    """test event unregistering with the off method and multiple handlers"""
    obs = Observable()

    results = []

    def some_test(*args, **kw):
        results.append(1)

    def some_test_2(*args, **kw):
        results.append(2)

    obs.on("some_test", some_test, some_test_2)
    assert len(obs._events["some_test"]) == 2

    obs.off("some_test", some_test, some_test_2)
    assert len(obs._events["some_test"]) == 0
    assert not obs.trigger("some_test")


def test_multiple_inheritance():
    """Test using class inheritance without calling Observable.__init__"""

    class SomeBaseClass(object):
        pass

    class SomeBaseAndObservable(SomeBaseClass, Observable):
        def __init__(self):
            super(SomeBaseAndObservable, self).__init__()

        def test(self):
            self.trigger("some", True)

    def some_test(data):
        assert data is True

    obj = SomeBaseAndObservable()
    obj.on("some", some_test)

    obj.test()


def test_get_all_handlers():
    """test get_all_handlers() after registering handlers for two events"""
    obs = Observable()

    def some_test():
        pass

    def other_test():
        pass

    assert not obs.get_all_handlers()

    obs.on("some_event", some_test)
    assert "some_event" in obs.get_all_handlers()
    assert some_test in obs.get_all_handlers()["some_event"]

    obs.on("other_event", other_test)
    assert "other_event" in obs.get_all_handlers()
    assert other_test in obs.get_all_handlers()["other_event"]
    assert other_test not in obs.get_all_handlers()["some_event"]


def test_get_handlers():
    """test get_handlers() after registering handlers for two events"""
    obs = Observable()

    def some_test():
        pass

    def other_test():
        pass

    assert not obs.get_handlers("some_event")

    obs.on("some_event", some_test)
    assert some_test in obs.get_handlers("some_event")

    obs.on("other_event", other_test)
    assert other_test in obs.get_handlers("other_event")
    assert other_test not in obs.get_handlers("some_event")


def test_is_registered():
    """test is_registered() after registering an event"""
    obs = Observable()

    def some_test():
        pass

    assert not obs.is_registered("some_event", some_test)
    obs.on("some_event", some_test)
    assert obs.is_registered("some_event", some_test)
