#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from ..query import SELECTORS, Query
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

    def test_add_argument(self):
        input = """\
def f(x): pass
def g(x): pass
[f(), g()]"""

        def selector(arg):
            return Query(arg).select_function("f")

        def modifier(q):
            return q.add_argument("y", "5")

        output = self.run_bowler_modifier(
            input, selector_func=selector, modifier_func=modifier
        )
        expected = """\
def f(x, y=5): pass
def g(x): pass
[f(), g()]"""
        self.assertMultiLineEqual(expected, output)
