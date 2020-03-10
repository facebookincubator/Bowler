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
        def query_func(arg):
            return Query(arg).select_function("f").rename("foo")

        self.run_bowler_modifiers(
            [
                ("def f(x): pass", "def foo(x): pass"),
                ("def g(x): pass", "def g(x): pass"),
                ("f()", "foo()"),
                ("g()", "g()"),
            ],
            query_func=query_func,
        )

    def test_rename_class(self):
        self.run_bowler_modifiers(
            [("class Bar(Foo):\n  pass", "class FooBar(Foo):\n  pass")],
            query_func=lambda x: Query(x).select_class("Bar").rename("FooBar"),
        )

    def test_rename_module(self):
        self.run_bowler_modifiers(
            [("from a.b.c.d import E", "from a.f.d import E")],
            query_func=lambda x: Query(x).select_module("a.b.c").rename("a.f"),
        )

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
        def query_func(x):
            return Query(x).select_subclass("Foo").rename("somepackage.Foo")

        self.run_bowler_modifiers(
            [("class Bar(Foo):\n  pass", "class Bar(somepackage.Foo):\n  pass")],
            query_func=query_func,
        )

    def test_filter_contains_parameter(self):
        def f(x, y):
            pass

        def query_func(x):
            return Query(x).select_function(f).contains_parameter("y").rename("g")

        self.run_bowler_modifiers(
            [
                ("def f(x, y):\n   pass", "def g(x, y):\n   pass"),
                ("def f(x, y, z):\n   pass", "def g(x, y, z):\n   pass"),
                ("def f(x):\n   pass", "def f(x):\n   pass"),
                ("def x(y):\n   pass", "def x(y):\n   pass"),
                ("def f(*_):\n   pass", "def f(*_):\n   pass"),
                ("def f(**_):\n   pass", "def f(**_):\n   pass"),
                ("f(1, y=2)", "g(1, y=2)"),
                ("f(1, 2)", "g(1, 2)"),
                ("f(1, 2, z=3)", "g(1, 2, z=3)"),
                ("f(y=2)", "g(y=2)"),
                ("f(x=2, **a)", "f(x=2, **a)"),
                ("f(*a, **a)", "f(*a, **a)"),
                ("f(*_)", "f(*_)"),
                ("f(**_)", "f(**_)"),
                ("f(x=1)", "f(x=1)"),
                ("f(1)", "f(1)"),
                ("f(1, x=2)", "f(1, x=2)"),
            ],
            query_func=query_func,
        )

    def test_filter_missing_parameter(self):
        def f(x, y):
            pass

        def query_func(x):
            return Query(x).select_function(f).missing_parameter("y").rename("g")

        self.run_bowler_modifiers(
            [
                ("def f(x, z):\n   pass", "def g(x, z):\n   pass"),
                ("def f(x, y, z):\n   pass", "def f(x, y, z):\n   pass"),
                ("f(1, z=2)", "g(1, z=2)"),
                ("f(1)", "g(1)"),
                ("f(x=2, **a)", "g(x=2, **a)"),
                ("f(*a, **a)", "g(*a, **a)"),
                ("f(1, 2, z=3)", "f(1, 2, z=3)"),
                ("f(y=2)", "f(y=2)"),
            ],
            query_func=query_func,
        )

    def test_filter_in_class(self):
        def query_func_bar(x):
            return Query(x).select_function("f").in_class("Bar", False).rename("g")

        def query_func_foo(x):
            return Query(x).select_function("f").in_class("Foo", False).rename("g")

        def query_func_foo_subclasses(x):
            return Query(x).select_function("f").in_class("Foo", True).rename("g")

        # Does not have subclasses enabled
        self.run_bowler_modifiers(
            [
                (
                    "class Bar(Foo):\n  def f(self): pass",
                    "class Bar(Foo):\n  def f(self): pass",
                )
            ],
            query_func=query_func_foo,
        )
        # Does
        self.run_bowler_modifiers(
            [
                (
                    "class Bar(Foo):\n  def f(self2): pass",
                    "class Bar(Foo):\n  def g(self2): pass",
                ),
                (
                    "class Bar(Baz):\n  def f(self2): pass",
                    "class Bar(Baz):\n  def f(self2): pass",
                ),
            ],
            query_func=query_func_foo_subclasses,
        )
        # Operates directly on class
        self.run_bowler_modifiers(
            [
                (
                    "class Bar(Foo):\n  def f(self3): pass",
                    "class Bar(Foo):\n  def g(self3): pass",
                )
            ],
            [("class Bar:\n  def f(self3): pass", "class Bar:\n  def g(self3): pass")],
            query_func=query_func_bar,
        )
        # Works on functions too, not just methods
        self.run_bowler_modifiers(
            [("def f(): pass", "def f(): pass")], query_func=query_func_bar
        )

    def test_add_keyword_argument(self):
        def f(z, x):
            pass

        def def_query_func(x):
            return Query(x).select_function(f).is_def().add_argument("y", "5")

        def call_query_func(x):
            return Query(x).select_function(f).is_call().add_argument("x", "5")

        def conditional_call_query_func(x):
            return (
                Query(x)
                .select_function(f)
                .is_call()
                .missing_parameter("x")
                .add_argument("x", "5")
            )

        # Definition kwarg tests
        self.run_bowler_modifiers(
            [
                ("def f(z, x): pass", "def f(z, x, y=5): pass"),
                ("def g(x): pass", "def g(x): pass"),
            ],
            query_func=def_query_func,
        )
        with self.assertRaises(AssertionError):
            self.run_bowler_modifier("def f(z, x, y): pass", query_func=def_query_func)

        # Callsite kwarg tests
        self.run_bowler_modifiers(
            [
                ("f(1)", "f(1, x=5)"),
                ("f(z=1)", "f(z=1, x=5)"),
                ("f(z=1, **a)", "f(z=1, x=5, **a)"),
                ("g()", "g()"),
            ],
            query_func=call_query_func,
        )
        with self.assertRaises(AssertionError):
            self.run_bowler_modifier("f(1, 2)", query_func=call_query_func)

        # Conditional callsite kwarg tests
        self.run_bowler_modifiers(
            [
                ("f(1)", "f(1, x=5)"),
                ("f(1, 2)", "f(1, 2)"),
                ("f(z=1)", "f(z=1, x=5)"),
                ("f(z=1, x=2)", "f(z=1, x=2)"),
                ("f(z=1, **a)", "f(z=1, x=5, **a)"),
                ("f(z=1, x=2)", "f(z=1, x=2)"),
                ("f(z=1, **a)", "f(z=1, x=5, **a)"),
                ("g()", "g()"),
            ],
            query_func=conditional_call_query_func,
        )

    def test_add_positional_argument(self):
        def query_func(x):
            return Query(x).select_function("f").add_argument("y", "5", True)

        self.run_bowler_modifiers(
            [
                ("def f(x): pass", "def f(x, y): pass"),
                ("def g(x): pass", "def g(x): pass"),
                ("f()", "f(5)"),
                ("g()", "g()"),
            ],
            query_func=conditional_call_query_func,
        )

    def test_add_positional_argument(self):
        def query_func(x):
            return Query(x).select_function("f").add_argument("y", "5", True)

        self.run_bowler_modifiers(
            [
                ("def f(x): pass", "def f(x, y): pass"),
                ("def g(x): pass", "def g(x): pass"),
                ("f()", "f(5)"),
            ],
            query_func=query_func,
        )
        with self.assertRaises(AssertionError):
            self.run_bowler_modifier("def f(x, y): pass", query_func=query_func)

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
