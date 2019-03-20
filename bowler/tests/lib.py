#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import functools
import multiprocessing
import sys
import tempfile
import unittest
from contextlib import contextmanager
from io import StringIO

import click
from fissix import pygram, pytree
from fissix.pgen2.driver import Driver

from bowler import Query
from bowler.types import LN, SYMBOL, TOKEN


class BowlerTestCase(unittest.TestCase):
    """Subclass of TestCase that captures stdout and makes it easier to run Bowler."""

    def setUp(self):
        self.buffer = StringIO()
        # Replace the write method instead of stdout so that already-existing
        # loggers end up writing here.
        sys.stdout._saved_write = sys.stdout.write
        sys.stdout.write = self.buffer.write
        sys.stdout._saved_isatty = sys.stdout.isatty
        sys.stdout.isatty = lambda: False

    def tearDown(self):
        if hasattr(sys.stdout, "_saved_write"):
            sys.stdout.write = sys.stdout._saved_write
            del sys.stdout._saved_write
        if hasattr(sys.stdout, "_saved_isatty"):
            sys.stdout.isatty = sys.stdout._saved_isatty
            del sys.stdout._saved_isatty

    def _formatMessage(self, msg1, msg2):
        stdout_text = self.buffer.getvalue()
        msg = msg1 or msg2
        if stdout_text:
            msg += "\n"
            msg += "-" * 20 + "< captured stdout >" + "-" * 20 + "\n"
            msg += stdout_text + "\n"
            msg += "-" * 20 + "<    end stdout   >" + "-" * 20 + "\n"
        return msg

    def run_bowler_modifier(
        self,
        input_text,
        selector=None,
        modifier=None,
        selector_func=None,
        modifier_func=None,
        in_process=True,
        query_func=None,
    ):
        """Returns the modified text."""

        if not (selector or selector_func or query_func):
            raise ValueError("Pass selector")
        if not (modifier or modifier_func or query_func):
            raise ValueError("Pass modifier")

        exception_queue = multiprocessing.Queue()

        def store_exceptions_on(func):
            @functools.wraps(func)
            def inner(node, capture, filename):
                # When in_process=False, this runs in another process.  See notes below.
                try:
                    return func(node, capture, filename)
                except Exception as e:
                    exception_queue.put(e)

            return inner

        def default_query_func(files):
            if selector_func:
                q = selector_func(files)
            else:
                q = Query(files).select(selector)

            if modifier_func:
                q = modifier_func(q)
            else:
                q = q.modify(modifier)

            return q

        if query_func is None:
            query_func = default_query_func

        with tempfile.NamedTemporaryFile(suffix=".py") as f:
            # TODO: I'm almost certain this will not work on Windows, since
            # NamedTemporaryFile has it already open for writing.  Consider
            # using mktemp directly?
            with open(f.name, "w") as fw:
                fw.write(input_text + "\n")

            query = query_func([f.name])
            assert query is not None, "Remember to return the Query"
            assert query.retcode is None, "Return before calling .execute"
            assert len(query.transforms) == 1, "TODO: Support multiple"

            for i in range(len(query.current.callbacks)):
                query.current.callbacks[i] = store_exceptions_on(
                    query.current.callbacks[i]
                )

            # We require the in_process parameter in order to record coverage properly,
            # but it also helps in bubbling exceptions and letting tests read state set
            # by modifiers.
            query.execute(
                interactive=False, write=True, silent=False, in_process=in_process
            )

            # In the case of in_process=False (mirroring normal use of the tool) we use
            # the queue to ship back exceptions from local_process, which can actually
            # fail the test.  Normally exceptions in modifiers are not printed
            # at all unless you pass --debug, and even then you don't get the
            # traceback.
            # See https://github.com/facebookincubator/Bowler/issues/63
            if not exception_queue.empty():
                raise AssertionError from exception_queue.get()

            with open(f.name, "r") as fr:
                return fr.read().rstrip()

    def run_bowler_modifiers(
        self, cases, selector=None, modifier=None, query_func=None
    ):
        for input, expected in cases:
            with self.subTest(input):
                output = self.run_bowler_modifier(
                    input, selector, modifier, query_func=query_func
                )
                self.assertMultiLineEqual(expected, output)

    def parse_line(self, source: str) -> LN:
        grammar = pygram.python_grammar_no_print_statement
        driver = Driver(grammar, convert=pytree.convert)
        # Skip file_input, simple_stmt
        return driver.parse_string(source + "\n").children[0].children[0]


class BowlerTestCaseTest(BowlerTestCase):
    def test_stdout_capture(self):
        print("hi")
        print("there")
        self.assertIn("hi\n", self.buffer.getvalue())

    def test_stdout_click_no_colors(self):
        # This tests that we patched isatty correctly.
        click.echo(click.style("hi", fg="red", bold=True))
        self.assertEqual("hi\n", self.buffer.getvalue())

    def test_run_bowler_modifier(self):
        input = "x=a*b"

        selector = "term< any op='*' any >"

        def modifier(node, capture, filename):
            capture["op"].value = "/"
            capture["op"].changed()

        output = self.run_bowler_modifier(input, selector, modifier)
        self.assertEqual("x=a/b", output)

    def test_run_bowler_modifier_parse_error(self):
        input = "    if x:\n bad"
        selector = "any"
        output = self.run_bowler_modifier(input, selector, lambda *args: None)
        self.assertFalse("None" in output)

    def test_run_bowler_modifier_query_func(self):
        input = "x=a*b"

        selector = "term< any op='*' any >"

        def modifier(node, capture, filename):
            capture["op"].value = "/"
            capture["op"].changed()

        def query_func(arg):
            return Query(arg).select(selector).modify(modifier)

        output = self.run_bowler_modifier(input, query_func=query_func)
        self.assertEqual("x=a/b", output)

    def test_run_bowler_modifier_modifier_func(self):
        input = "x=a*b"

        selector = "term< any op='*' any >"

        def selector_func(arg):
            return Query(arg).select(selector)

        def modifier(node, capture, filename):
            capture["op"].value = "/"
            capture["op"].changed()

        def modifier_func(q):
            return q.modify(modifier)

        output = self.run_bowler_modifier(
            input, selector_func=selector_func, modifier_func=modifier_func
        )
        self.assertEqual("x=a/b", output)

    def test_run_bowler_modifier_ferries_exception(self):
        input = "x=a*b"

        selector = "term< any op='*' any >"

        def modifier(not_enough_args):
            pass

        # Should work in both modes
        self.assertRaises(
            AssertionError,
            lambda: self.run_bowler_modifier(
                input, selector, modifier, in_process=False
            ),
        )

        self.assertRaises(
            AssertionError,
            lambda: self.run_bowler_modifier(
                input, selector, modifier, in_process=True
            ),
        )

    def test_parse_line_leaf(self):
        input = "2.5"
        tree = self.parse_line(input)
        self.assertEqual(TOKEN.NUMBER, tree.type)
        self.assertEqual("2.5", tree.value)

    def test_parse_line_node(self):
        input = "x = (y+1)"
        tree = self.parse_line(input)
        self.assertEqual(SYMBOL.expr_stmt, tree.type)

        self.assertEqual(TOKEN.NAME, tree.children[0].type)
        self.assertEqual(TOKEN.EQUAL, tree.children[1].type)
        self.assertEqual(SYMBOL.atom, tree.children[2].type)

        self.assertEqual("x", tree.children[0].value)
