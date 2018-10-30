#!/usr/bin/env python3

import os
from pathlib import Path
from unittest import TestCase, mock

from ..tool import BowlerTool, log
from ..query import Query


class ToolTest(TestCase):

    target = Path(__file__).parent / "smoke-target.py"

    def setUp(self):
        # If the target file has been patched, undo it
        self.orig_file = Path(__file__).parent / "smoke-target.py.orig"
        self.rej_file = Path(__file__).parent / "smoke-target.py.rej"
        if os.path.isfile(self.orig_file):
            os.rename(self.orig_file, self.target)
        if os.path.isfile(self.rej_file):
            os.remove(self.rej_file)

    @mock.patch("bowler.tool.sh.patch")
    def test_process_hunks_patch_called_correctly(self, mock_patch):
        tool = BowlerTool(Query().compile(), write=True, interactive=False, silent=True)
        hunks = [
            [
                "--- {self.target}",
                "+++ {self.target}",
                "@@ -7,8 +7,8 @@",
                " ",
                " ",
                " # todo: i18n",
                '-print("Hello world!")',
                '+print(tr("Hello world!"))',
                " ",
                " ",
                "-def foo():",
                '+def foo(bar="something"):',
                "     pass",
            ],
            [
                "--- {self.target}",
                "+++ {self.target}",
                "@@ -10,11 +10,11 @@",
                " ",
                " ",
                " # todo: i18n",
                '-print("Hello world!")',
                '+print(tr("Hello world!"))',
                " ",
                " ",
                "-def foo():",
                '+def foo(bar="something"):',
                "     pass",
            ],
        ]
        tool.process_hunks(self.target, hunks)
        string_hunks = ""
        for hunk in hunks:
            string_hunks += "\n".join(hunk[2:]) + "\n"
        string_hunks = f"--- {self.target}\n+++ {self.target}\n" + string_hunks
        mock_patch.assert_called_with(
            "-u", self.target, _in=string_hunks.encode("utf-8")
        )

    @mock.patch.object(log, "exception")
    def test_process_hunks_invalid_hunks(self, mock_log):
        tool = BowlerTool(Query().compile(), write=True, interactive=False, silent=True)
        hunks = [
            [
                "--- {self.target}",
                "+++ {self.target}",
                "@@ -7,8 +7,8 @@",
                " ",
                " ",
                " # todo: i18n",
                '-print("Hello world!")',
                '+print(tr("Hello world!"))',
                " ",
                " ",
                "-def foo():",
                '+def foo(bar="something"):',
                "     pass",
            ],
            [
                "--- {self.target}",
                "+++ {self.target}",
                "@@ -10,11 +10,11 @@",
                " ",
                " ",
                " # todo: i18n",
                '-print("Hello world!")',
                '+print(tr("Hello world!"))',
                " ",
                " ",
                "-def foo():",
                '+def foo(bar="something"):',
                "     pass",
            ],
        ]
        tool.process_hunks(self.target, hunks)
        mock_log.assert_called_with(
            f"hunks failed to apply, rejects saved to {self.target}.rej"
        )
        self.assertTrue(os.path.isfile(self.rej_file))
        self.assertTrue(os.path.isfile(self.orig_file))

    @mock.patch.object(log, "exception")
    def test_process_hunks_no_hunks(self, mock_log):
        tool = BowlerTool(Query().compile(), write=True, interactive=False)
        empty_hunks = [[]]
        out = tool.process_hunks(self.target, empty_hunks)
        patch_stderr = "/usr/bin/patch: **** Only garbage was found in the patch input."
        mock_log.assert_called_with(f"failed to apply patch hunk: {patch_stderr}")
        self.assertIsNone(out)
