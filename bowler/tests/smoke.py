#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from pathlib import Path
from unittest import TestCase

from fissix.fixer_util import Call, Name

from ..query import Query
from ..types import TOKEN


class SmokeTest(TestCase):
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
