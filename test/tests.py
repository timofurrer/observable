# -*- coding: utf-8 -*-

import nose.tools as nose
from observable import Observable


def test_on_decorator():
    """test event registering with the on decorator"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    @obs.on("on_test")
    def on_test():
        pass

    nose.assert_in(on_test, obs._events["on_test"])


def test_on():
    """test event registering with the on method"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    def on_test():
        pass

    obs.on("on_test", on_test)
    nose.assert_in(on_test, obs._events["on_test"])


def test_once_decorator():
    """test event registering with the once decorator"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    @obs.once("once_test")
    def once_test():
        pass

    nose.assert_in(once_test, obs._events["once_test"])
    nose.assert_true(obs.trigger("once_test"))
    nose.assert_not_in(once_test, obs._events["once_test"])


def test_once():
    """test event registering with the once method"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    def once_test():
        pass

    obs.once("once_test", once_test)

    nose.assert_equals(len(obs._events["once_test"]), 1)
    nose.assert_true(obs.trigger("once_test"))
    nose.assert_equals(obs._events["once_test"], [])


def test_on_trigger():
    """test event triggering with event registered with on"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    @obs.on("on_test")
    def on_test():
        pass

    nose.assert_equals(obs._events, {"on_test": [on_test]})
    nose.assert_true(obs.trigger("on_test"))
    nose.assert_true(obs.trigger("on_test"))


def test_once_trigger():
    """test event triggering with event registered with once"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    @obs.once("once_test")
    def once_test():
        pass

    nose.assert_equals(obs._events, {"once_test": [once_test]})
    nose.assert_true(obs.trigger("once_test"))
    nose.assert_equals(obs._events, {"once_test": []})
    nose.assert_false(obs.trigger("once_test"))


def test_no_event_for_trigger():
    """test exception raising for not existing events"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    nose.assert_raises(Observable.EventNotFound, obs.trigger, "no_existing_event")


def test_off():
    """test obs.off method"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    @obs.on("on_test")
    def on_test():
        pass

    nose.assert_equals(obs._events, {"on_test": [on_test]})
    nose.assert_true(obs.trigger("on_test"))
    obs.off("on_test", on_test)
    nose.assert_equals(obs._events, {"on_test": []})

    obs.off()
    nose.assert_equals(obs._events, {})

    @obs.on("more_than_one_event")
    def func1():
        pass

    @obs.on("more_than_one_event")
    def func2():
        pass

    @obs.on("more_than_one_event")
    def func3():
        pass

    nose.assert_equals(obs._events["more_than_one_event"], [func1, func2, func3])
    obs.off("more_than_one_event", func2)
    nose.assert_equals(obs._events["more_than_one_event"], [func1, func3])
    obs.off("more_than_one_event")
    nose.assert_equals(obs._events["more_than_one_event"], [])


def test_off_exceptions():
    """test exception raising in the off method"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    nose.assert_raises(Observable.EventNotFound, obs.off, "non_existing_event")

    @obs.on("some_event")
    def some_assigned_handler():
        pass

    def some_non_assigned_handler():
        pass

    nose.assert_in(some_assigned_handler, obs._events["some_event"])
    nose.assert_not_in(some_non_assigned_handler, obs._events["some_event"])
    nose.assert_raises(Observable.HandlerNotFound, obs.off, "some_event", some_non_assigned_handler)


def test_trigger_arg():
    """test event triggering with arguments"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    @obs.on("some_test")
    def some_test(some_data):
        nose.assert_equals(some_data, "some data")

    nose.assert_true(obs.trigger("some_test", "some data"))


def test_trigger_args():
    """test event triggering with argument list"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    @obs.on("some_test")
    def some_test(some_data, some_other_data):
        nose.assert_true(some_data)
        nose.assert_false(some_other_data)

    nose.assert_true(obs.trigger("some_test", *[True, False]))


def test_trigger_kwargs():
    """test event triggering with keyword-arguments"""
    obs = Observable()
    nose.assert_equals(obs._events, {})

    @obs.on("some_test")
    def some_test(some_data=True, some_other_data=False):
        nose.assert_false(some_data)
        nose.assert_true(some_other_data)

    nose.assert_true(obs.trigger("some_test", some_other_data=True, some_data=False))
