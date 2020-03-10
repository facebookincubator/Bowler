#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import io
import logging
import subprocess
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock

from fissix.fixer_util import Call, Name

from ..query import Query
from ..types import TOKEN, BadTransform

STDERR = io.StringIO()


class SmokeTest(TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(stream=STDERR)

    def test_tr(self):
        target = Path(__file__).parent / "smoke-target.py"

        def takes_string_literal(node, capture, fn):
            args = capture.get("args")
            return args and args[0].type == TOKEN.STRING

        def wrap_string(node, capture, fn):
            args = capture["args"]
            if args and args[0].type == TOKEN.STRING:
                literal = args[0]
                literal.replace(Call(Name("tr"), [literal.clone()]))

        files_processed = []
        hunks_processed = 0

        def verify_hunk(filename, hunk):
            nonlocal hunks_processed
            files_processed.append(filename)
            hunks_processed += 1

            self.assertIn("""-print("Hello world!")""", hunk)
            self.assertIn("""+print(tr("Hello world!"))""", hunk)
            self.assertIn("""-def foo():""", hunk)
            self.assertIn("""+def foo(bar="something"):""", hunk)

        (
            Query(target)
            .select(
                """
                power< "print" trailer< "(" args=any* ")" > >
                """
            )
            .filter(takes_string_literal)
            .modify(wrap_string)
            .select_function("foo")
            .add_argument("bar", '"something"')
            .process(verify_hunk)
            .silent()
        )

        self.assertEqual(hunks_processed, 1)
        self.assertEqual(len(files_processed), 1)
        self.assertIn("smoke-target.py", files_processed[0])

    def test_check_ast(self):
        target = Path(__file__).parent / "smoke-target.py"
        mock_processor = Mock()

        query = (
            Query(str(target))
            .select_function("foo")
            .rename("foo/")
            .process(mock_processor)
            .silent()
        )
        self.assertTrue(any(isinstance(e, BadTransform) for e in query.exceptions))
        mock_processor.assert_not_called()

    def test_click_test(self):
        proc = subprocess.run(
            [sys.executable, "-m", "bowler", "test", "bowler/tests/smoke-selftest.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )
        self.assertIn("Ran 2 tests", proc.stderr)
        self.assertEqual(1, proc.returncode)
