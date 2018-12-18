#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""bowler.type_inference

Given an expression, find its result type.

For sufficiently obvious expressions, we can find this using only local
knowledge (numeric literals, and functions/names which have a standard
meaning).  Some obvious examples:

`1.0` -> InferredType.FLOAT
`2L` -> InferredType.INT
`1/2` -> Depends on use_py2_division

Even in cases where we don't know the full inputs, we can make some reasonable
assumptions.  For example when passing `use_py2_division=False,
type_for_unknown=InferredType.INT_OR_FLOAT`:

`x+1.0` -> InferredType.FLOAT
`x/y` -> InferredType.FLOAT
`len(x) + 1` -> InferredType.INT
`float(z)` -> InferredType.FLOAT

This is intended to be useful for either refactoring or flagging for humans
syntax like `range(float(...))` or `"%d" % (float(...),)`.
"""

import enum
from typing import Dict, Sequence, Union

from fissix import pygram, pytree
from fissix.pgen2 import token
from fissix.pgen2.driver import Driver

from .helpers import is_call_to
from .types import LN, SYMBOL, TOKEN

__all__ = ["InferredType", "numeric_expr_type"]


class InferredType(enum.IntEnum):
    # The order of these is important, such that an expression using py3
    # semantics most operators take max(OP_MIN_TYPE[op], max(children)) as the
    # result.
    UNSET = 0
    BOOL = 1
    INT = 2
    # This represents UNKNOWN but assumed to be restricted to normal numeric
    # values.  It can still be promoted to COMPLEX or FLOAT, but if is the
    # final result should be treated as INT (or better).
    INT_OR_FLOAT = 3
    FLOAT = 4
    COMPLEX = 5
    UNKNOWN = 6


# Note: SLASH and DOUBLESLASH are specialcased.
OP_MIN_TYPE: Dict = {
    TOKEN.PLUS: InferredType.INT,
    TOKEN.MINUS: InferredType.INT,
    TOKEN.STAR: InferredType.INT,
    TOKEN.PERCENT: InferredType.INT,
    TOKEN.SLASH: InferredType.INT,
    TOKEN.DOUBLESLASH: InferredType.INT,
    TOKEN.TILDE: InferredType.INT,  # bitwise not
    TOKEN.DOUBLESTAR: InferredType.INT,
    TOKEN.LEFTSHIFT: InferredType.INT,
    TOKEN.RIGHTSHIFT: InferredType.INT,
    TOKEN.VBAR: InferredType.BOOL,
    TOKEN.CIRCUMFLEX: InferredType.BOOL,
    TOKEN.AMPER: InferredType.BOOL,
    TOKEN.LESS: InferredType.BOOL,
}


def numeric_expr_type(
    node: LN,
    use_py2_division=False,
    type_for_unknown: InferredType = InferredType.UNKNOWN,
) -> "InferredType":
    """Infer the type of an expression from its literals.

    We broaden the definition of "literal" a bit to also include calls to
    certain functions like int() and float() where the return type does not
    change based on the arguments.

    Args:
        node: A Node or leaf.
        use_py2_division: Whether to use magical python 2 style division.
        type_for_unknown: An InferredType to customize how you wan unknown
            handled.  Use `INT_OR_FLOAT` if you trust your input to only work
            on numbers, but `UNKNOWN` if you want objects to be an option.

    Returns: InferredType
    """
    if node.type == TOKEN.NUMBER:
        # It's important that we do not use eval here; some literals like `2L`
        # may be invalid in the current interpreter.
        if "j" in node.value:
            return InferredType.COMPLEX
        elif "." in node.value or "e" in node.value:
            return InferredType.FLOAT
        return InferredType.INT
    elif node.type == TOKEN.NAME and node.value in ("True", "False"):
        return InferredType.BOOL
    # TODO let the caller provide other known return types, or even a
    # collection of locals and their types.
    elif is_call_to(node, "bool"):
        return InferredType.BOOL
    elif is_call_to(node, "int") or is_call_to(node, "len"):
        return InferredType.INT
    elif is_call_to(node, "float"):
        return InferredType.FLOAT

    elif node.type in (SYMBOL.comparison, SYMBOL.not_test):
        return InferredType.BOOL
    elif node.type == SYMBOL.factor:
        # unary ~ + -, always [op, number]
        return max(
            OP_MIN_TYPE[node.children[0].type],
            numeric_expr_type(node.children[1], use_py2_division, type_for_unknown),
        )
    elif node.type == SYMBOL.shift_expr:
        # << only valid on int
        return InferredType.INT

    elif node.type == SYMBOL.power:
        # a**b, but also f(...)
        if node.children[1].type != TOKEN.DOUBLESTAR:
            # probably f(...)
            return type_for_unknown

        return max(
            max(OP_MIN_TYPE[c.type] for c in node.children[1::2]),
            max(
                numeric_expr_type(c, use_py2_division, type_for_unknown)
                for c in node.children[::2]
            ),
        )
    elif node.type in (
        SYMBOL.arith_expr,
        SYMBOL.xor_expr,
        SYMBOL.and_expr,
        SYMBOL.expr,
    ):
        return max(
            max(OP_MIN_TYPE[c.type] for c in node.children[1::2]),
            max(
                numeric_expr_type(c, use_py2_division, type_for_unknown)
                for c in node.children[::2]
            ),
        )
    elif node.type == SYMBOL.term:
        # */%
        # This is where things get interesting, as we handle use_py2_division.
        t = InferredType.UNSET
        last_op = None
        for i in range(len(node.children)):
            if i % 2 == 0:
                new = numeric_expr_type(
                    node.children[i], use_py2_division, type_for_unknown
                )
                if last_op == TOKEN.DOUBLESLASH:
                    t = InferredType.INT
                elif last_op == TOKEN.SLASH:
                    if use_py2_division:
                        if t == InferredType.INT and new == InferredType.INT:
                            t = InferredType.INT
                        else:
                            t = max(t, max(OP_MIN_TYPE[last_op], new))
                    else:
                        t = max(t, InferredType.FLOAT)
                else:
                    if last_op:
                        t = max(t, OP_MIN_TYPE[last_op])
                    t = max(t, new)
            else:
                last_op = node.children[i].type
        return t
    elif node.type in (SYMBOL.or_test, SYMBOL.and_test):
        return max(
            numeric_expr_type(c, use_py2_division, type_for_unknown)
            for c in node.children[::2]
        )

    return type_for_unknown
