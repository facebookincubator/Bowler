#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Callable, Dict, List, NewType, Optional, Type, Union

from fissix.fixer_base import BaseFix
from fissix.pgen2 import token
from fissix.pygram import python_symbols
from fissix.pytree import Leaf, Node

from attr import Factory, dataclass


class Passthrough:
    def __init__(self, target: Any) -> None:
        self._target = target

    def __getattr__(self, name: str) -> Any:
        return getattr(self._target, name)


TOKEN = Passthrough(token)
SYMBOL = Passthrough(python_symbols)

SENTINEL = object()
START = object()
DROP = object()

STARS = {TOKEN.STAR, TOKEN.DOUBLESTAR}
ARG_END = {TOKEN.RPAR, TOKEN.COMMA}
ARG_LISTS = {SYMBOL.typedargslist, SYMBOL.arglist}  # function def, function call
ARG_ELEMS = {
    TOKEN.NAME,  # single argument
    SYMBOL.tname,  # type annotated
    SYMBOL.argument,  # keyword argument
    SYMBOL.star_expr,  # vararg
} | STARS

LN = Union[Leaf, Node]
Stringish = Union[str, object]
Filename = NewType("Filename", str)
FilenameMatcher = Callable[[Filename], bool]
Capture = Dict[str, Any]
Callback = Callable[[Node, Capture, Filename], Any]
Filter = Callable[[Node, Capture, Filename], bool]
Fixers = List[Type[BaseFix]]
Hunk = List[str]
Processor = Callable[[Filename, Hunk], bool]


@dataclass
class Transform:
    selector: str = ""
    kwargs: Dict[str, Any] = Factory(dict)
    filters: List[Filter] = Factory(list)
    callbacks: List[Callback] = Factory(list)
    fixer: Optional[Type[BaseFix]] = None


class BowlerException(Exception):
    def __init__(
        self, message: str = "", *, filename: str = "", hunks: List[Hunk] = None
    ) -> None:
        super().__init__(message)
        self.filename = filename
        self.hunks = hunks


class BowlerQuit(BowlerException):
    pass


class IMRError(BowlerException):
    pass


class RetryFile(BowlerException):
    pass


class BadTransform(BowlerException):
    pass
