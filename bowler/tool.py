#!/usr/bin/env python3

import difflib
import logging
import multiprocessing
import os
import time
from queue import Empty
from typing import Iterator, List, Sequence, Tuple

import click
import sh
from fissix.pgen2.parse import ParseError
from fissix.refactor import RefactoringTool

from .types import (
    BowlerException,
    BowlerQuit,
    Filename,
    Fixers,
    Hunk,
    Processor,
    RetryFile,
)

PROMPT_HELP = {
    "y": "apply this hunk",
    "n": "skip this hunk",
    "a": "apply this hunk and all remaining hunks for this file",
    "d": "skip this hunk and all remaining hunks for this file",
    "q": "quit; do not apply this hunk or any remaining hunks",
    "?": "show help",
}

log = logging.getLogger(__name__)


def diff_texts(a: str, b: str, filename: str) -> Iterator[str]:
    lines_a = a.splitlines()
    lines_b = b.splitlines()
    return difflib.unified_diff(lines_a, lines_b, filename, filename, lineterm="")


def prompt_user(question: str, options: str, default: str = "") -> str:
    options = options.lower()
    default = default.lower()
    assert len(default) < 2 and default in options

    if "?" not in options:
        options += "?"

    prompt_options = ",".join(o.upper() if o == default else o for o in options)
    prompt = f"{question} [{prompt_options}]? "
    result = ""

    while True:
        result = input(prompt).strip().lower()
        if result == "?":
            for option in PROMPT_HELP:
                click.secho(f"{option} - {PROMPT_HELP[option]}", fg="red", bold=True)

        elif len(result) == 1 and result in options:
            return result

        elif result:
            click.echo(f'invalid response "{result}"')

        elif default:
            return default


class BowlerTool(RefactoringTool):
    NUM_PROCESSES = os.cpu_count() or 1

    def __init__(
        self,
        fixers: Fixers,
        *args,
        interactive: bool = True,
        write: bool = False,
        silent: bool = False,
        hunk_processor: Processor = None,
        **kwargs,
    ) -> None:
        options = kwargs.pop("options", {})
        options["print_function"] = True
        super().__init__(fixers, *args, options=options, **kwargs)
        self.queue_count = 0
        self.queue = multiprocessing.JoinableQueue()  # type: ignore
        self.results = multiprocessing.Queue()  # type: ignore
        self.semaphore = multiprocessing.Semaphore(self.NUM_PROCESSES)
        self.interactive = interactive
        self.write = write
        self.silent = silent
        if hunk_processor is not None:
            self.hunk_processor = hunk_processor
        else:
            self.hunk_processor = lambda f, h: True

    def get_fixers(self) -> Tuple[Fixers, Fixers]:
        fixers = [f(self.options, self.fixer_log) for f in self.fixers]
        pre: Fixers = [f for f in fixers if f.order == "pre"]
        post: Fixers = [f for f in fixers if f.order == "post"]
        return pre, post

    def processed_file(
        self, new_text: str, filename: str, old_text: str = "", *args, **kwargs
    ) -> List[Hunk]:
        self.files.append(filename)
        hunks: List[Hunk] = []
        if old_text != new_text:
            a, b, *lines = list(diff_texts(old_text, new_text, filename))

            hunk: Hunk = []
            for line in lines:
                if line.startswith("@@"):
                    if hunk:
                        hunks.append([a, b, *hunk])
                        hunk = []
                hunk.append(line)

            if hunk:
                hunks.append([a, b, *hunk])

        return hunks

    def refactor_file(self, filename: str, *a, **k) -> List[Hunk]:
        try:
            hunks: List[Hunk] = []
            input, encoding = self._read_python_source(filename)
            if input is None:
                # Reading the file failed.
                return hunks
        except OSError:
            self.log_debug("Failed to read %s, skipping", filename)
            return hunks

        try:
            tree = self.refactor_string(input, filename)
            hunks = self.processed_file(str(tree), filename, input)

        except ParseError:
            self.log_debug("Failed to parse %s, skipping", filename)

        return hunks

    def refactor_dir(self, dir_name: str, *a, **k) -> None:
        """Descends down a directory and refactor every Python file found.

        Python files are assumed to have a .py extension.

        Files and subdirectories starting with '.' are skipped.
        """
        py_ext = os.extsep + "py"
        for dirpath, dirnames, filenames in os.walk(dir_name):
            self.log_debug("Descending into %s", dirpath)
            dirnames.sort()
            filenames.sort()
            for name in filenames:
                if not name.startswith(".") and os.path.splitext(name)[1] == py_ext:
                    fullname = os.path.join(dirpath, name)
                    self.queue_work(Filename(fullname))
            # Modify dirnames in-place to remove subdirs with leading dots
            dirnames[:] = [dn for dn in dirnames if not dn.startswith(".")]

    def refactor_queue(self) -> None:
        self.semaphore.acquire()
        while True:
            filename = self.queue.get()

            if filename is None:
                break

            try:
                hunks = self.refactor_file(filename)
                self.results.put((filename, hunks))

            except RetryFile:
                self.log_debug(f"Retrying {filename} later...")
                self.queue.put(filename)
            except BowlerException as e:
                self.log_debug(f"Bowler exception during transform: {e}")
                self.results.put((filename, []))

            finally:
                self.queue.task_done()
        self.semaphore.release()

    def queue_work(self, filename: Filename) -> None:
        self.queue.put(filename)
        self.queue_count += 1

    def refactor(self, items: Sequence[str], *a, **k) -> None:
        """Refactor a list of files and directories."""

        child_count = max(1, min(self.NUM_PROCESSES, len(items)))
        self.log_debug(f"starting {child_count} processes")
        children = [
            multiprocessing.Process(target=self.refactor_queue)
            for i in range(child_count)
        ]
        for child in children:
            child.start()

        for dir_or_file in sorted(items):
            if os.path.isdir(dir_or_file):
                self.refactor_dir(dir_or_file)
            else:
                self.queue_work(Filename(dir_or_file))

        for _child in children:
            self.queue.put(None)

        results_count = 0

        while True:
            try:
                filename, hunks = self.results.get_nowait()
                self.log_debug(f"results: got {len(hunks)} hunks for {filename}")
                results_count += 1
                self.process_hunks(filename, hunks)

            except Empty:
                if self.queue.empty() and results_count == self.queue_count:
                    break

                elif not any(child.is_alive() for child in children):
                    self.log_debug(f"child processes stopped without consuming work")
                    break

                else:
                    time.sleep(0.05)

            except BowlerQuit:
                for child in children:
                    child.terminate()
                return

        self.log_debug(f"all children stopped and all diff hunks processed")

    def process_hunks(self, filename: Filename, hunks: List[Hunk]) -> None:
        auto_yes = False
        result = ""
        for hunk in hunks:
            if self.hunk_processor(filename, hunk) is False:
                continue

            if not self.silent:
                for line in hunk:
                    if line.startswith("---"):
                        click.secho(line, fg="red", bold=True)
                    elif line.startswith("+++"):
                        click.secho(line, fg="green", bold=True)
                    elif line.startswith("-"):
                        click.secho(line, fg="red")
                    elif line.startswith("+"):
                        click.secho(line, fg="green")
                    else:
                        click.echo(line)

                if self.interactive:
                    if auto_yes:
                        click.echo(f"Applying remaining hunks to {filename}")
                        result = "y"
                    else:
                        result = prompt_user("Apply this hunk", "ynqad", "n")

                    self.log_debug(f"result = {result}")

                    if result == "q":
                        raise BowlerQuit()
                    elif result == "d":
                        break  # skip all remaining hunks
                    elif result == "n":
                        continue
                    elif result == "a":
                        auto_yes = True
                        result = "y"
                    elif result != "y":
                        raise ValueError("unknown response")

            if result == "y" or self.write:
                patch = ("\n".join(hunk) + "\n").encode("utf-8")
                args = ["patch", "-u", filename]
                self.log_debug(f"running {args}")
                try:
                    sh.patch("-u", filename, _in=patch)  # type: ignore
                except sh.ErrorReturnCode:
                    log.exception("failed to apply patch hunk")
                    return  # TODO: better response?

    def run(self, paths: Sequence[str]) -> int:
        if not self.errors:
            self.refactor(paths)
            self.summarize()

        return int(bool(self.errors))
