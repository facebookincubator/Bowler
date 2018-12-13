#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import importlib
import logging
import sys
from pathlib import Path
from typing import List

import click

from .query import Query
from .tool import BowlerTool
from .types import START, SYMBOL, TOKEN


@click.group(invoke_without_command=True)
@click.option("--debug/--quiet", default=False, help="Logging output level")
@click.option("--version", "-V", is_flag=True, help="Print version string and exit")
@click.pass_context
def main(ctx: click.Context, debug: bool, version: bool) -> None:
    """Safe Python code modification and refactoring."""
    if version:
        from bowler import __version__

        click.echo(f"bowler {__version__}")
        return

    if debug:
        BowlerTool.NUM_PROCESSES = 1
    logging.basicConfig(level=(logging.DEBUG if debug else logging.WARNING))

    if ctx.invoked_subcommand is None:
        return do(None, None)


@main.command()
@click.option("--selector-pattern", is_flag=True)
@click.argument("paths", type=click.Path(exists=True), nargs=-1, required=False)
def dump(selector_pattern: bool, paths: List[str]) -> None:
    """Dump the CST representation of each file in <paths>."""
    return Query(paths).select_root().dump(selector_pattern).retcode


@main.command()
@click.option("-i", "--interactive", is_flag=True)
@click.argument("query", required=False)
@click.argument("paths", type=click.Path(exists=True), nargs=-1, required=False)
def do(interactive: bool, query: str, paths: List[str]) -> None:
    """Execute a query or enter interactive mode."""
    if not query or query == "-":

        namespace = {"Query": Query, "START": START, "SYMBOL": SYMBOL, "TOKEN": TOKEN}

        try:
            import IPython

            IPython.start_ipython(argv=[], user_ns=namespace)

        except ImportError:
            import code as _code

            _code.interact(local=namespace)

        finally:
            return

    code = compile(query, "<console>", "eval")
    result = eval(code)  # noqa eval() - developer tool, hopefully they're not dumb

    if isinstance(result, Query):
        if result.retcode is not None:
            exc = click.ClickException("query failed")
            exc.exit_code = result.retcode
            raise exc
        result.diff(interactive=interactive)
    elif result:
        click.echo(repr(result))


@main.command()
@click.argument("codemod", required=True, type=str)
@click.argument("argv", required=False, type=str, nargs=-1)
def run(codemod: str, argv: List[str]) -> None:
    """
    Execute a file-based code modification.

    Takes either a path to a python script, or an importable module name, and attempts
    to import and run a "main()" function from that script/module if found.
    Extra arguments to this command will be supplied to the script/module.
    Use `--` to forcibly pass through all following options or arguments.
    """

    try:
        original_argv = sys.argv[1:]
        sys.argv[1:] = argv

        path = Path(codemod)
        if path.exists():
            if path.is_dir():
                raise click.ClickException("running directories not supported")

            spec = importlib.util.spec_from_file_location(  # type: ignore
                path.name, path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore

        else:
            module = importlib.import_module(codemod)

        main = getattr(module, "main", None)
        if main is not None:
            main()

    except ImportError as e:
        raise click.ClickException(f"failed to import codemod: {e}") from e

    finally:
        sys.argv[1:] = original_argv


if __name__ == "__main__":
    main()
