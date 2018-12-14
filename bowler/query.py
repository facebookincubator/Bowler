#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import inspect
import logging
import pathlib
import re
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

from attr import Factory, dataclass
from fissix.fixer_base import BaseFix
from fissix.fixer_util import Attr, Comma, Dot, LParen, Name, Newline, RParen
from fissix.pytree import Leaf, Node, type_repr

from .helpers import (
    Once,
    dotted_parts,
    find_first,
    find_last,
    find_previous,
    get_class,
    power_parts,
    print_selector_pattern,
    print_tree,
    quoted_parts,
)
from .imr import FunctionArgument, FunctionSpec
from .tool import BowlerTool
from .types import (
    LN,
    SENTINEL,
    START,
    SYMBOL,
    TOKEN,
    BowlerException,
    Callback,
    Capture,
    Filename,
    FilenameMatcher,
    Filter,
    Hunk,
    Processor,
    Stringish,
    Transform,
)

SELECTORS = {}
Q = TypeVar("Q", bound="Query")
QM = Callable[..., Q]

log = logging.getLogger(__name__)


def selector(pattern: str) -> Callable[[QM], QM]:
    def wrapper(fn: QM) -> QM:
        selector = fn.__name__.replace("select_", "").lower()
        SELECTORS[selector] = pattern

        signature = inspect.signature(fn)
        arg_names = list(signature.parameters)[1:]

        @wraps(fn)
        def wrapped(self: Q, *args, **kwargs) -> Q:
            for arg, value in zip(arg_names, args):
                if hasattr(value, "__name__"):
                    kwargs["source"] = value
                    kwargs[arg] = value.__name__
                else:
                    kwargs[arg] = str(value)

            if "name" in kwargs:
                kwargs["dotted_name"] = " ".join(quoted_parts(kwargs["name"]))
                kwargs["power_name"] = " ".join(power_parts(kwargs["name"]))
            self.transforms.append(Transform(selector, kwargs))
            return self

        return wrapped

    return wrapper


class Query:
    def __init__(
        self,
        *paths: Union[str, List[str]],
        filename_matcher: Optional[FilenameMatcher] = None,
    ) -> None:
        self.paths: List[str] = []
        self.transforms: List[Transform] = []
        self.processors: List[Processor] = []
        self.retcode: Optional[int] = None
        self.filename_matcher = filename_matcher

        for path in paths:
            if isinstance(path, str):
                self.paths.append(path)
            elif isinstance(path, pathlib.Path):
                self.paths.append(str(path))
            else:
                self.paths.extend(path)

        if not self.paths:
            self.paths.append(".")

    @selector(
        """
        file_input< any* >
    """
    )
    def select_root(self) -> "Query":
        ...

    @selector(
        """
        (
            import_name< 'import'
                (
                    module_name='{name}'
                |
                    module_name=dotted_name< {dotted_name} any* >
                |
                    dotted_as_name<
                        (
                            module_name='{name}'
                        |
                            module_name=dotted_name< {dotted_name} any* >
                        )
                        'as' module_nickname=any
                    >
                )
            >
        |
            import_from< 'from'
                (
                    module_name='{name}'
                |
                    module_name=dotted_name< {dotted_name} any* >
                )
                'import' ['(']
                (
                    import_as_name<
                        module_import=any
                        'as'
                        module_nickname=any
                    >*
                |
                    import_as_names<
                        module_imports=any*
                    >
                |
                    module_import=any
                )
             [')'] >
        |
            module_name=power<
                [TOKEN]
                {power_name}
                module_access=trailer< any* >*
            >
        )
    """
    )
    def select_module(self, name: str) -> "Query":
        ...

    @selector(
        """
        (
            class_def=classdef<
                'class' class_name='{name}'
                any*
                suite<
                    any*
                >
                any*
            >
        |
            class_call=power<
                class_name='{name}'
                trailer< '(' class_arguments=any* ')' >
            >
        |
            class_subclass=classdef< any*
                (
                    any* class_name='{name}' any*
                |
                    arglist< any* class_name='{name}' any* >
                )
                any*
                suite<
                    any*
                >
                any*
            >
        |
            class_import=import_from<
                'from' module_name=any
                'import' ['(']
                (
                    import_as_names<
                        any*
                        class_name='{name}'
                        any*
                    >
                |
                    any*
                    class_name='{name}'
                    any*
                )
            [')'] >
        )
    """
    )
    def select_class(self, name: str) -> "Query":
        ...

    @selector(
        """
        (
            class_def=classdef<
                'class' class_name=any '('
                (
                    any* class_ancestor='{name}' any*
                |
                    arglist< any* class_ancestor='{name}' any* >
                )
                any*
                suite<
                    any*
                >
                any*
            >
        )
    """
    )
    def select_subclass(self, name: str) -> "Query":
        ...

    @selector(
        """
        (
            attr_class=classdef< any*
                suite< any*
                    simple_stmt< any*
                        attr_assignment=expr_stmt<
                            attr_name='{name}' attr_value=any*
                        >
                    any* >
                any* >
            any* >
        |
            attr_assignment=expr_stmt<
                power<
                    any*
                    trailer< any* >*
                    trailer< '.'
                        attr_name='{name}'
                    >
                >
                attr_value=any*
            >
        |
            attr_access=power<
                any*
                trailer< any* >*
                trailer< '.'
                    attr_name='{name}'
                any* >
            any* >
        )
    """
    )
    def select_attribute(self, name: str) -> "Query":
        ...

    @selector(
        """
        (
            decorated=decorated<
                decorators=decorators
                function_def=funcdef<
                    'def' function_name='{name}'
                    function_parameters=parameters< '('
                        function_arguments=typedargslist< ( 'self' | 'cls' ) any* >*
                    ')' >
                    any*
                >
            >
        |
            function_def=funcdef<
                'def' function_name='{name}'
                function_parameters=parameters< '('
                    function_arguments=typedargslist< ( 'self' | 'cls' ) any* >*
                ')' >
                any*
            >
        |
            function_call=power<
                any*
                trailer< any* >*
                trailer<
                    '.' function_name='{name}'
                >
                function_parameters=trailer< '(' function_arguments=any* ')' >
                any*
            >
        )

    """
    )
    def select_method(self, name: str) -> "Query":
        ...

    @selector(
        """
        (
            decorated=decorated<
                decorators=decorators
                function_def=funcdef<
                    'def' function_name='{name}'
                    function_parameters=parameters< '(' function_arguments=any* ')' >
                    any*
                >
            >
        |
            function_def=funcdef<
                'def' function_name='{name}'
                function_parameters=parameters< '(' function_arguments=any* ')' >
                any*
            >
        |
            function_call=power<
                [TOKEN]
                function_name='{name}'
                function_parameters=trailer< '(' function_arguments=any* ')' >
                remainder=any*
            >
        |
            function_import=import_from<
                'from' module_name=any
                'import' ['(']
                (
                    import_as_names<
                        any*
                        function_name='{name}'
                        any*
                    >
                |
                    any*
                    function_name='{name}'
                    any*
                )
            [')'] >
        )
    """
    )
    def select_function(self, name: str) -> "Query":
        ...

    @selector(
        """
        (
            var_assignment=expr_stmt<
                var_name='{name}'
                var_value=any*
            >
        |
            var_name='{name}'
        )
    """
    )
    def select_var(self, name: str) -> "Query":
        ...

    @selector("""{pattern}""")
    def select_pattern(self, pattern: str) -> "Query":
        ...

    def select(self, pattern: str) -> "Query":
        return self.select_pattern(pattern)

    @property
    def current(self) -> Transform:
        if not self.transforms:
            raise ValueError("no selectors used")

        return self.transforms[-1]

    def is_filename(self, include: str = None, exclude: str = None) -> "Query":
        if include:
            regex = re.compile(include)

            def filter_filename_include(
                node: LN, capture: Capture, filename: Filename
            ) -> bool:
                return regex.search(filename) is not None

            self.current.filters.append(filter_filename_include)

        if exclude:
            regex = re.compile(exclude)

            def filter_filename_exclude(
                node: LN, capture: Capture, filename: Filename
            ) -> bool:
                return regex.search(filename) is None

            self.current.filters.append(filter_filename_exclude)

        return self

    def is_call(self) -> "Query":
        def filter_is_call(node: LN, capture: Capture, filename: Filename) -> bool:
            return bool("function_call" in capture or "class_call" in capture)

        self.current.filters.append(filter_is_call)
        return self

    def is_def(self) -> "Query":
        def filter_is_def(node: LN, capture: Capture, filename: Filename) -> bool:
            return bool("function_def" in capture or "class_def" in capture)

        self.current.filters.append(filter_is_def)
        return self

    def in_class(self, class_name: str, include_subclasses: bool = True) -> "Query":
        def filter_in_class(node: LN, capture: Capture, filename: Filename) -> bool:
            while node.parent is not None:
                if node.type == SYMBOL.classdef:
                    if node.children[1].value == class_name:
                        return True
                    if not include_subclasses:
                        return False
                    for leaf in node.leaves():
                        if leaf.type == TOKEN.COLON:
                            break
                        elif leaf.type == TOKEN.NAME and leaf.value == class_name:
                            return True
                    return False
                node = node.parent
            return False

        self.current.filters.append(filter_in_class)
        return self

    def move(self, new_module: str, filename: str = None) -> "Query":
        transform = self.current
        if transform.selector not in ("class", "function"):
            raise ValueError("move requires select_function or select_class")

        if not filename:
            filename = new_module.replace(".", "/") + ".py"

        def transform_move(node: LN, capture: Capture, filename: Filename) -> None:
            pass

        transform.callbacks.append(transform_move)
        return self

    def encapsulate(self, internal_name: str = "") -> "Query":
        transform = self.current
        if transform.selector not in ("attribute"):
            raise ValueError("encapsulate requires select_attribute")

        if not any("filter_in_class" in f.__name__ for f in transform.filters):
            raise ValueError("encapsulate requires in_class filter")

        make_property = Once()
        old_name = transform.kwargs["name"]
        new_name = internal_name or f"_{old_name}"

        if new_name.startswith("__"):
            raise ValueError(
                "renaming {old_name} -> {new_name} is dangerous, "
                "please specify internal_name to avoid name mangling"
            )

        def encapsulate_transform(
            node: LN, capture: Capture, filename: Filename
        ) -> None:
            if "attr_assignment" in capture:
                leaf = capture["attr_name"]
                leaf.replace(Name(new_name, prefix=leaf.prefix))

                if make_property:
                    # TODO: capture and use type annotation from original assignment

                    class_node = get_class(node)
                    suite = find_first(class_node, SYMBOL.suite)
                    assert isinstance(suite, Node)
                    indent_node = find_first(suite, TOKEN.INDENT)
                    assert isinstance(indent_node, Leaf)
                    indent = indent_node.value

                    getter = Node(
                        SYMBOL.decorated,
                        [
                            Node(
                                SYMBOL.decorator,
                                [
                                    Leaf(TOKEN.AT, "@"),
                                    Name("property"),
                                    Leaf(TOKEN.NEWLINE, "\n"),
                                ],
                            ),
                            Node(
                                SYMBOL.funcdef,
                                [
                                    Name("def", indent),
                                    Name(old_name, prefix=" "),
                                    Node(
                                        SYMBOL.parameters,
                                        [LParen(), Name("self"), RParen()],
                                    ),
                                    Leaf(TOKEN.COLON, ":"),
                                    Node(
                                        SYMBOL.suite,
                                        [
                                            Newline(),
                                            Leaf(TOKEN.INDENT, indent.value + "    "),
                                            Node(
                                                SYMBOL.simple_stmt,
                                                [
                                                    Node(
                                                        SYMBOL.return_stmt,
                                                        [
                                                            Name("return"),
                                                            Node(
                                                                SYMBOL.power,
                                                                Attr(
                                                                    Name("self"),
                                                                    Name(new_name),
                                                                ),
                                                                prefix=" ",
                                                            ),
                                                        ],
                                                    ),
                                                    Newline(),
                                                ],
                                            ),
                                            Leaf(TOKEN.DEDENT, "\n" + indent),
                                        ],
                                    ),
                                ],
                                prefix=indent,
                            ),
                        ],
                    )

                    setter = Node(
                        SYMBOL.decorated,
                        [
                            Node(
                                SYMBOL.decorator,
                                [
                                    Leaf(TOKEN.AT, "@"),
                                    Node(
                                        SYMBOL.dotted_name,
                                        [Name(old_name), Dot(), Name("setter")],
                                    ),
                                    Leaf(TOKEN.NEWLINE, "\n"),
                                ],
                            ),
                            Node(
                                SYMBOL.funcdef,
                                [
                                    Name("def", indent),
                                    Name(old_name, prefix=" "),
                                    Node(
                                        SYMBOL.parameters,
                                        [
                                            LParen(),
                                            Node(
                                                SYMBOL.typedargslist,
                                                [
                                                    Name("self"),
                                                    Comma(),
                                                    Name("value", prefix=" "),
                                                ],
                                            ),
                                            RParen(),
                                        ],
                                    ),
                                    Leaf(TOKEN.COLON, ":"),
                                    Node(
                                        SYMBOL.suite,
                                        [
                                            Newline(),
                                            Leaf(TOKEN.INDENT, indent + "    "),
                                            Node(
                                                SYMBOL.simple_stmt,
                                                [
                                                    Node(
                                                        SYMBOL.expr_stmt,
                                                        [
                                                            Node(
                                                                SYMBOL.power,
                                                                Attr(
                                                                    Name("self"),
                                                                    Name(new_name),
                                                                ),
                                                            ),
                                                            Leaf(
                                                                TOKEN.EQUAL,
                                                                "=",
                                                                prefix=" ",
                                                            ),
                                                            Name("value", prefix=" "),
                                                        ],
                                                    ),
                                                    Newline(),
                                                ],
                                            ),
                                            Leaf(TOKEN.DEDENT, "\n" + indent),
                                        ],
                                    ),
                                ],
                                prefix=indent,
                            ),
                        ],
                    )

                    suite.insert_child(-1, getter)
                    suite.insert_child(-1, setter)

                    prev = find_previous(getter, TOKEN.DEDENT, recursive=True)
                    curr = find_last(setter, TOKEN.DEDENT, recursive=True)
                    assert isinstance(prev, Leaf) and isinstance(curr, Leaf)
                    prev.prefix, curr.prefix = curr.prefix, prev.prefix
                    prev.value, curr.value = curr.value, prev.value

        transform.callbacks.append(encapsulate_transform)
        return self

    def rename(self, new_name: str) -> "Query":
        transform = self.current
        old_name = transform.kwargs["name"]

        def rename_transform(node: LN, capture: Capture, filename: Filename) -> None:
            log.debug(f"{filename} [{list(capture)}]: {node}")
            for _key, value in capture.items():
                log.debug(f"{_key}: {value}")
                if isinstance(value, Leaf) and value.type == TOKEN.NAME:
                    if value.value == old_name and value.parent is not None:
                        value.replace(Name(new_name, prefix=value.prefix))
                        break
                elif isinstance(value, Node):
                    if type_repr(value.type) == "dotted_name":
                        parts = zip(
                            dotted_parts(old_name),
                            dotted_parts(new_name),
                            value.children,
                        )
                        for old, new, leaf in parts:
                            if old != leaf.value:
                                break
                            if old != new:
                                leaf.replace(Name(new, prefix=leaf.prefix))
                    elif type_repr(value.type) == "power":
                        pows = zip(dotted_parts(old_name), dotted_parts(new_name))
                        it = iter(value.children)
                        leaf = next(it)
                        for old, new in pows:
                            if old == ".":
                                leaf = leaf.children[1]
                                continue

                            if old != leaf.value:
                                break

                            if old == leaf.value and old != new:
                                leaf.replace(Name(new, prefix=leaf.prefix))

                            leaf = next(it)

        transform.callbacks.append(rename_transform)
        return self

    def add_argument(
        self,
        name: str,
        value: str,
        positional: bool = False,
        after: Stringish = SENTINEL,
        type_annotation: Stringish = SENTINEL,
    ) -> "Query":
        keyword = not positional

        transform = self.current
        if transform.selector not in ("function", "method"):
            raise ValueError("add_argument must follow select_function/select_method")

        # determine correct position (excluding self/cls) to add new argument
        stop_at = -1
        if positional and after not in (SENTINEL, START):
            if "source" not in transform.kwargs:
                raise ValueError(
                    "using after= with positional= requires passing original function"
                )
            signature = inspect.signature(transform.kwargs["source"])
            if after not in (SENTINEL, START) and after not in signature.parameters:
                raise ValueError(f"{after} does not exist in original function")

            names = list(signature.parameters)
            stop_at = names.index(cast(str, after))
            if names[0] in ("self", "cls", "meta"):
                stop_at -= 1

        def add_argument_transform(
            node: Node, capture: Capture, filename: Filename
        ) -> None:
            spec = FunctionSpec.build(node, capture)
            done = False
            value_leaf = Name(value)

            if spec.is_def:
                new_arg = FunctionArgument(
                    name,
                    value_leaf if keyword else None,
                    cast(str, type_annotation) if type_annotation != SENTINEL else "",
                )
                for index, argument in enumerate(spec.arguments):
                    if (
                        after == START
                        or after == argument.name
                        or (positional and (argument.value or argument.star))
                        or (
                            keyword
                            and argument.star
                            and argument.star.type == TOKEN.DOUBLESTAR
                        )
                    ):
                        spec.arguments.insert(index, new_arg)
                        done = True
                        break

                if not done:
                    spec.arguments.append(new_arg)

            elif positional:
                new_arg = FunctionArgument(value=value_leaf)
                for index, argument in enumerate(spec.arguments):
                    if argument.star and argument.star.type == TOKEN.STAR:
                        log.debug(f"noping out due to *{argument.name}")
                        done = True
                        break

                    if (
                        after == START
                        or index == stop_at
                        or argument.name
                        or argument.star
                    ):
                        spec.arguments.insert(index, new_arg)
                        done = True
                        break

                if not done:
                    spec.arguments.append(new_arg)

            spec.explode()

        transform.callbacks.append(add_argument_transform)
        return self

    def modify_argument(
        self,
        name: str,
        new_name: Stringish = SENTINEL,
        type_annotation: Stringish = SENTINEL,
        default_value: Stringish = SENTINEL,
    ) -> "Query":
        transform = self.current
        if transform.selector not in ("function", "method"):
            raise ValueError(f"modifier must follow select_function or select_method")

        def modify_argument_transform(
            node: Node, capture: Capture, filename: Filename
        ) -> None:
            spec = FunctionSpec.build(node, capture)

            for argument in spec.arguments:
                if argument.name == name:
                    if new_name is not SENTINEL:
                        argument.name = str(new_name)
                    if spec.is_def and type_annotation is not SENTINEL:
                        argument.annotation = str(type_annotation)
                    if spec.is_def and default_value is not SENTINEL:
                        argument.value = Name(default_value, prefix=" ")

            spec.explode()

        transform.callbacks.append(modify_argument_transform)
        return self

    def remove_argument(self, name: str) -> "Query":
        transform = self.current
        if transform.selector not in ("function", "method"):
            raise ValueError(f"modifier must follow select_function or select_method")

        # determine correct position (excluding self/cls) to add new argument
        stop_at = -1
        if "source" not in transform.kwargs:
            raise ValueError("remove_argument requires passing original function")
        signature = inspect.signature(transform.kwargs["source"])
        if name not in signature.parameters:
            raise ValueError(f"{name} does not exist in original function")

        if signature.parameters[name].kind in (
            inspect.Parameter.VAR_KEYWORD,
            inspect.Parameter.VAR_POSITIONAL,
        ):
            raise ValueError("can't remove *args or **kwargs")

        positional = signature.parameters[name].kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
        names = list(signature.parameters)
        stop_at = names.index(name)
        if names[0] in ("self", "cls", "meta"):
            stop_at -= 1

        def remove_argument_transform(
            node: Node, capture: Capture, filename: Filename
        ) -> None:
            spec = FunctionSpec.build(node, capture)

            if spec.is_def or not positional:
                for argument in spec.arguments:
                    if argument.name == name:
                        spec.arguments.remove(argument)
                        break

            else:
                for index, argument in reversed(list(enumerate(spec.arguments))):
                    if argument.name == name:
                        spec.arguments.pop(index)
                        break

                    if index == stop_at and not argument.name and not argument.star:
                        spec.arguments.pop(index)
                        break

            spec.explode()

        transform.callbacks.append(remove_argument_transform)
        return self

    def fixer(self, fx: Type[BaseFix]) -> "Query":
        self.transforms.append(Transform(fixer=fx))
        return self

    def filter(self, callback: Union[str, Callback]) -> "Query":
        if isinstance(callback, str):
            code = compile(callback, "<string>", "eval")

            def callback(node: Node, capture: Capture, filename: Filename) -> bool:
                return bool(eval(code))  # noqa: developer tool

        callback = cast(Callback, callback)
        self.current.filters.append(callback)
        return self

    def modify(self, callback: Union[str, Callback]) -> "Query":
        if isinstance(callback, str):
            code = compile(callback, "<string>", "exec")

            def callback(node: Node, capture: Capture, filename: Filename) -> None:
                exec(code)

        callback = cast(Callback, callback)
        self.current.callbacks.append(callback)
        return self

    def process(self, callback: Processor) -> "Query":
        self.processors.append(callback)
        return self

    def create_fixer(self, transform):
        if transform.fixer:
            bm_compat = transform.fixer.BM_compatible
            pattern = transform.fixer.PATTERN

        else:
            bm_compat = False
            log.debug(f"select {transform.selector}[{transform.kwargs}]")
            pattern = SELECTORS[transform.selector].format(**transform.kwargs)

            pattern = " ".join(
                line
                for wholeline in pattern.splitlines()
                for line in (wholeline.strip(),)
                if line
            )

            log.debug(f"generated pattern: {pattern}")

        filters = transform.filters
        callbacks = transform.callbacks

        log.debug(f"registered {len(filters)} filters: {filters}")
        log.debug(f"registered {len(callbacks)} callbacks: {callbacks}")

        class Fixer(BaseFix):
            PATTERN = pattern  # type: ignore
            BM_compatible = bm_compat

            def transform(self, node: LN, capture: Capture) -> Optional[LN]:
                filename = cast(Filename, self.filename)
                returned_node = None
                if not filters or all(f(node, capture, filename) for f in filters):
                    if transform.fixer:
                        returned_node = transform.fixer().transform(node, capture)
                    for callback in callbacks:
                        if returned_node and returned_node is not node:
                            raise BowlerException(
                                "Only the last fixer/callback may return "
                                "a different node.  See "
                                "https://pybowler.io/docs/api-modifiers"
                            )
                        returned_node = callback(node, capture, filename)
                return returned_node

        return Fixer

    def compile(self) -> List[Type[BaseFix]]:
        if not self.transforms:
            log.debug(f"no selectors chosen, defaulting to select_root")
            self.select_root()

        fixers: List[Type[BaseFix]] = []
        for transform in self.transforms:
            fixers.append(self.create_fixer(transform))

        return fixers

    def execute(self, **kwargs) -> "Query":
        fixers = self.compile()
        if self.processors:

            def processor(filename: Filename, hunk: Hunk) -> bool:
                apply = True
                for p in self.processors:
                    if p(filename, hunk) is False:
                        apply = False
                return apply

            kwargs["hunk_processor"] = processor

        kwargs.setdefault("filename_matcher", self.filename_matcher)
        self.retcode = BowlerTool(fixers, **kwargs).run(self.paths)
        return self

    def dump(self, selector_pattern=False) -> "Query":
        if not selector_pattern:
            for transform in self.transforms:
                transform.callbacks.append(print_tree)
        else:
            for transform in self.transforms:
                transform.callbacks.append(print_selector_pattern)
        return self.execute(write=False)

    def diff(self, interactive: bool = False, **kwargs) -> "Query":
        return self.execute(write=False, interactive=interactive, **kwargs)

    def idiff(self, **kwargs) -> "Query":
        return self.diff(interactive=True, **kwargs)

    def silent(self, **kwargs) -> "Query":
        return self.execute(silent=True, **kwargs)

    def write(self, **kwargs) -> "Query":
        return self.execute(write=True, **kwargs)
