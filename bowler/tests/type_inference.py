#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
import unittest
from io import StringIO

from fissix import pygram, pytree
from fissix.pgen2.driver import Driver

from ..type_inference import OP_MIN_TYPE, InferredType, numeric_expr_type
from ..types import LN, SYMBOL, TOKEN

BINARY_OPERATORS = ["+", "-", "*", "**", "<<", ">>", "|", "&", "^", "%", "<"]

UNARY_OPERATORS = ["~", "-", "+"]
# TODO 'is', 'not'

SAMPLE_EXPRESSIONS = [
    # and/or
    ("True", InferredType.BOOL),
    ("True or False", InferredType.BOOL),
    ("True or 1", InferredType.INT),
    ("1 or 1.0", InferredType.FLOAT),
    # Calls
    ("bool(x)", InferredType.BOOL),
    ("int(x)", InferredType.INT),
    ("len(x)", InferredType.INT),
    ("float(x)", InferredType.FLOAT),
    # Basic
    ("func()", InferredType.INT_OR_FLOAT),
    ("x+1", InferredType.INT_OR_FLOAT),
    ("x*1", InferredType.INT_OR_FLOAT),
    ("1+x", InferredType.INT_OR_FLOAT),
    ("1*x", InferredType.INT_OR_FLOAT),
    # Single
    ("1+1", InferredType.INT),
    ("1.0+1.0", InferredType.FLOAT),
    # Mixed
    ("1+1.0", InferredType.FLOAT),
    ("1+x/2", InferredType.FLOAT),  # py3
    ("1.0+x/2", InferredType.FLOAT),
    # Division
    ("1/1", InferredType.FLOAT),
    ("1/2.0", InferredType.FLOAT),
    ("1.0/2", InferredType.FLOAT),
    ("1/x", InferredType.FLOAT),
    ("1.0/x", InferredType.FLOAT),
    ("True/True", InferredType.FLOAT),
    ("1j/2", InferredType.COMPLEX),
    # Floor Division
    ("1//2", InferredType.INT),
    ("1.0//2.0", InferredType.INT),
]

SAMPLE_PY2_EXPRESSIONS = [
    # Py2 Division
    ("1/1", InferredType.INT),
    ("1/2.0", InferredType.FLOAT),
    ("1.0/2", InferredType.FLOAT),
    ("1/x", InferredType.INT_OR_FLOAT),
    ("1.0/x", InferredType.FLOAT),
    ("True/True", InferredType.INT),
    ("1j/2", InferredType.COMPLEX),
]


def _produce_test(lcals, gen_func, args):
    t = gen_func(*args)
    t.__name__ += str(args)
    lcals[t.__name__] = t


def tree(input: str) -> LN:
    print(f"Input is {repr(input)}")
    driver = Driver(pygram.python_grammar_no_print_statement, convert=pytree.convert)
    return driver.parse_string(input)


def map_type(o):
    if isinstance(o, complex):
        return InferredType.COMPLEX
    elif isinstance(o, float):
        return InferredType.FLOAT
    elif isinstance(o, bool):
        return InferredType.BOOL
    elif isinstance(o, int):
        return InferredType.INT


class OpMinTypeTest(unittest.TestCase):
    """
    Verifies that the generated OP_MIN_TYPE matches that of the current Python
    interpreter, and that `numeric_expr_type` agrees.
    """

    def _run_test(self, expression_str, expected_type):
        t = tree(expression_str)
        expr = t.children[0].children[0]
        # t_op = expr.children[1].type
        # expr_type = pytree.type_repr(expr.type)
        # key_type = TOKEN.tok_name[t_op]

        inferred_result = numeric_expr_type(expr)

        self.assertEqual(expected_type, inferred_result, repr(expr))

    def gen_test_binop(op):
        def test_binop(self):
            for lhs in ("True", "1", "1.0", "2j"):
                for rhs in ("True", "1", "1.0", "2j"):
                    snippet = f"{lhs} {op} {rhs}\n"
                    try:
                        real_result = eval(snippet, {}, {})
                    except TypeError:
                        continue
                    self._run_test(snippet, map_type(real_result))

        return test_binop

    def gen_test_uniop(op):
        def test_uniop(self):
            for rhs in ("True", "1", "1.0", "2j"):
                snippet = f"{op} {rhs}\n"
                try:
                    real_result = eval(snippet, {}, {})
                except TypeError:
                    continue
                self._run_test(snippet, map_type(real_result))

        return test_uniop

    def gen_test_min_type(op):
        def test_min_type(self):
            snippet = f"True {op} True\n"
            real_result = eval(snippet, {}, {})

            t = tree(snippet)
            expr = t.children[0].children[0]
            t_op = expr.children[1].type
            expr_type = pytree.type_repr(expr.type)
            key_type = TOKEN.tok_name[t_op]

            self.assertEqual(map_type(real_result), OP_MIN_TYPE.get(t_op), key_type)

        return test_min_type

    def gen_test_min_type_unary(op):
        def test_min_type_unary(self):
            snippet = f"{op} True\n"
            real_result = eval(snippet, {}, {})

            t = tree(snippet)

            expr = t.children[0].children[0]
            t_op = expr.children[0].type
            expr_type = pytree.type_repr(expr.type)
            key_type = TOKEN.tok_name[t_op]

            self.assertEqual(map_type(real_result), OP_MIN_TYPE.get(t_op), expr_type)

        return test_min_type_unary

    # This produces real methods that can have normal decorators on them, with
    # a proper pass/fail count (unlike subTest).
    for i, op in enumerate(BINARY_OPERATORS):
        _produce_test(locals(), gen_test_binop, (op,))
        _produce_test(locals(), gen_test_min_type, (op,))

    for i, op in enumerate(UNARY_OPERATORS):
        _produce_test(locals(), gen_test_uniop, (op,))
        _produce_test(locals(), gen_test_min_type_unary, (op,))


class ExpressionTest(unittest.TestCase):
    def gen_test_expression(expression_str, expected_type, use_py2_division=False):
        def test_expression(self):
            expr = tree(expression_str).children[0].children[0]
            inferred_type = numeric_expr_type(
                expr, use_py2_division, type_for_unknown=InferredType.INT_OR_FLOAT
            )
            self.assertEqual(expected_type, inferred_type)

        return test_expression

    for expr, expected in SAMPLE_EXPRESSIONS:
        _produce_test(locals(), gen_test_expression, (expr + "\n", expected))
    for expr, expected in SAMPLE_PY2_EXPRESSIONS:
        _produce_test(locals(), gen_test_expression, (expr + "\n", expected, True))
