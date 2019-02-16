#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from fissix.pytree import Leaf, Node

from ..helpers import dotted_parts, power_parts, print_selector_pattern, print_tree
from .lib import BowlerTestCase


class PrintTreeTest(BowlerTestCase):
    def test_print_tree_node(self):
        node = self.parse_line("x + 1")
        expected = """\
[arith_expr] ''
.  [NAME] '' 'x'
.  [PLUS] ' ' '+'
.  [NUMBER] ' ' '1'
"""
        print_tree(node)
        self.assertMultiLineEqual(expected, self.buffer.getvalue())

    def test_print_tree_captures(self):
        node = self.parse_line("x + 1 + 2")
        expected = """\
[arith_expr] ''
.  [NAME] '' 'x'
.  [PLUS] ' ' '+'
.  [NUMBER] ' ' '1'
.  [PLUS] ' ' '+'
.  [NUMBER] ' ' '2'
results['op'] =
.  [PLUS] ' ' '+'
results['rhs'] = [Leaf(2, '1'), Leaf(14, '+'), Leaf(2, '2')]
"""
        print_tree(node, {"op": node.children[1], "rhs": node.children[2:]})
        self.assertMultiLineEqual(expected, self.buffer.getvalue())

    def test_print_tree_recurse_limit(self):
        node = self.parse_line("(((x+1)+2)+3)")
        expected = """\
[atom] ''
.  [LPAR] '' '('
.  [arith_expr] ''
.  .  [atom] ''
.  .  .  [LPAR] '' '('
.  .  .  [arith_expr] ''
.  .  .  .  ...
.  .  .  [RPAR] '' ')'
.  .  [PLUS] '' '+'
.  .  [NUMBER] '' '3'
.  [RPAR] '' ')'
"""
        print_tree(node, recurse=3)
        self.assertMultiLineEqual(expected, self.buffer.getvalue())


class PrintSelectorPatternTest(BowlerTestCase):
    def test_print_selector_pattern(self):
        node = self.parse_line("x + 1")
        expected = """\
arith_expr < 'x' '+' '1' > """
        print_selector_pattern(node)
        self.assertMultiLineEqual(expected, self.buffer.getvalue())

    def test_print_selector_pattern_capture(self):
        node = self.parse_line("x + 1")
        expected = """\
arith_expr < 'x' op='+' '1' > """
        print_selector_pattern(node, {"op": node.children[1]})
        self.assertMultiLineEqual(expected, self.buffer.getvalue())

    def test_print_selector_pattern_capture_list(self):
        node = self.parse_line("x + 1")
        # This is not ideal, but hard to infer a good pattern
        expected = """\
arith_expr < 'x' rest='+' rest='1' > """
        print_selector_pattern(node, {"rest": node.children[1:]})
        self.assertMultiLineEqual(expected, self.buffer.getvalue())


class PowerPartsTest(unittest.TestCase):
    def test_power_parts_include_trailer(self):
        self.assertEqual(["'Model'"], power_parts("Model"))
        self.assertEqual(
            ["'models'", "trailer<", "'.'", "'Model'", ">"], power_parts("models.Model")
        )


class DottedPartsTest(unittest.TestCase):
    def test_dotted_parts(self):
        self.assertEqual(["Model"], dotted_parts("Model"))
        self.assertEqual(["models", ".", "Model"], dotted_parts("models.Model"))
        self.assertEqual(
            ["models", ".", "utils", ".", "Model"], dotted_parts("models.utils.Model")
        )
