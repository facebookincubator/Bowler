#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from unittest import mock

from ..query import SELECTORS, Query
from ..types import TOKEN, BowlerException, Leaf
from .lib import BowlerTestCase


class QueryTest(BowlerTestCase):
    fake_paths = ["foo/bar", "baz.py"]

    def test_basic(self):
        query = Query(self.fake_paths)
        self.assertEqual(len(query.transforms), 0)
        self.assertEqual(query.paths, self.fake_paths)
        with self.assertRaises(ValueError):
            transform = query.current
            self.assertEqual(transform, None)

        query.select_root().is_filename("frob.py")
        self.assertEqual(len(query.transforms), 1)
        self.assertEqual(query.current.selector, "root")
        self.assertEqual(len(query.current.kwargs), 0)
        self.assertEqual(len(query.current.filters), 1)
        self.assertEqual(len(query.current.filters), 1)

        fixers = query.compile()
        self.assertEqual(len(fixers), 1)
        self.assertEqual(fixers[0].PATTERN, SELECTORS["root"].strip())

    def test_rename_func(self):
        input = """\
def f(x): pass
def g(x): pass
[f(), g()]"""

        def selector(arg):
            return Query(arg).select_function("f")

        def modifier(q):
            return q.rename("foo")

        output = self.run_bowler_modifier(
            input, selector_func=selector, modifier_func=modifier
        )
        expected = """\
def foo(x): pass
def g(x): pass
[foo(), g()]"""
        self.assertMultiLineEqual(expected, output)

    def test_rename_class(self):
        input = """\
class Bar(Foo):
    pass"""

        def selector(arg):
            return Query(arg).select_class("Bar")

        def modifier(q):
            return q.rename("FooBar")

        output = self.run_bowler_modifier(
            input, selector_func=selector, modifier_func=modifier
        )
        expected = """\
class FooBar(Foo):
    pass"""
        self.assertMultiLineEqual(expected, output)

    def test_rename_module(self):
        input = """\
from a.b.c.d import E"""

        def selector(arg):
            return Query(arg).select_module("a.b.c")

        def modifier(q):
            return q.rename("a.f")

        output = self.run_bowler_modifier(
            input, selector_func=selector, modifier_func=modifier
        )
        expected = """\
from a.f.d import E"""
        self.assertMultiLineEqual(expected, output)

    def test_rename_module_callsites(self):
        input = """\
a.b.c.d.f()
w.bar()"""

        def selector(pattern):
            def _selector(arg):
                return Query(arg).select_module(pattern)

            return _selector

        def modifier(pattern):
            def _modifier(q):
                return q.rename(pattern)

            return _modifier

        # Same length
        output = self.run_bowler_modifier(
            input, selector_func=selector("a.b.c"), modifier_func=modifier("x.y.z")
        )
        expected = """\
x.y.z.d.f()
w.bar()"""
        self.assertMultiLineEqual(expected, output)

        # Shorter replacement
        output = self.run_bowler_modifier(
            input, selector_func=selector("a.b.c"), modifier_func=modifier("x.y")
        )
        expected = """\
x.y.d.f()
w.bar()"""
        self.assertMultiLineEqual(expected, output)

        # Longer replacement
        output = self.run_bowler_modifier(
            input, selector_func=selector("a.b.c"), modifier_func=modifier("w.x.y.z")
        )
        expected = """\
w.x.y.z.d.f()
w.bar()"""
        self.assertMultiLineEqual(expected, output)

        # Single character replacements replacement
        output = self.run_bowler_modifier(
            input, selector_func=selector("w"), modifier_func=modifier("x.y.z")
        )
        expected = """\
a.b.c.d.f()
x.y.z.bar()"""
        self.assertMultiLineEqual(expected, output)

    def test_rename_subclass(self):
        input = """\
class Bar(Foo):
    pass"""

        def selector(arg):
            return Query(arg).select_subclass("Foo")

        def modifier(q):
            return q.rename("somepackage.Foo")

        output = self.run_bowler_modifier(
            input, selector_func=selector, modifier_func=modifier
        )
        expected = """\
class Bar(somepackage.Foo):
    pass"""
        self.assertMultiLineEqual(expected, output)

    def test_add_argument(self):
        input = """\
def f(x): pass
def g(x): pass
[f(), g()]"""

        def selector(arg):
            return Query(arg).select_function("f")

        def add_modifier(q):
            return q.add_argument("y", "5")

        output = self.run_bowler_modifier(
            input, selector_func=selector, modifier_func=add_modifier
        )
        expected = """\
def f(x, y=5): pass
def g(x): pass
[f(), g()]"""
        self.assertMultiLineEqual(expected, output)

    def test_modifier_return_value(self):
        input = "a+b"

        def modifier(node, capture, filename):
            new_op = Leaf(TOKEN.MINUS, "-")
            return new_op

        output = self.run_bowler_modifier(input, "'+'", modifier)
        self.assertEqual("a-b", output)

    def test_modifier_return_value_multiple(self):
        input = "a+b"

        def noop_modifier(node, capture, filename):
            print("Noop modifier")
            pass

        def modifier(node, capture, filename):
            print("Modifier")
            new_op = Leaf(TOKEN.MINUS, "-")
            return new_op

        def add_ok_modifier(q):
            return q.modify(noop_modifier).modify(modifier)

        output = self.run_bowler_modifier(input, "'+'", modifier_func=add_ok_modifier)
        self.assertEqual("a-b", output)

        def add_bad_modifier(q):
            return q.modify(modifier).modify(noop_modifier)

        with mock.patch("bowler.tool.log.error") as error:
            output = self.run_bowler_modifier(
                input, "'+'", modifier_func=add_bad_modifier
            )
            self.assertEqual("a+b", output)  # unmodified
            self.assertTrue(error.call_args)
            self.assertIn(
                "Only the last fixer/callback may return", error.call_args[0][0]
            )
