#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from pathlib import Path
from unittest import TestCase, mock

from ..query import Query
from ..tool import BadTransform, BowlerTool, log
from ..types import BowlerQuit

target = Path(__file__).parent / "smoke-target.py"
hunks = [
    [
        f"--- {target}",
        f"+++ {target}",
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
        f"--- {target}",
        f"+++ {target}",
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


class ToolTest(TestCase):
    def setUp(self):
        echo_patcher = mock.patch("bowler.tool.click.echo")
        secho_patcher = mock.patch("bowler.tool.click.secho")
        self.addCleanup(echo_patcher.stop)
        self.addCleanup(secho_patcher.stop)
        self.mock_echo = echo_patcher.start()
        self.mock_secho = secho_patcher.start()

    @mock.patch("bowler.tool.apply_single_file")
    def test_process_hunks_patch_called_correctly(self, mock_patch):
        tool = BowlerTool(Query().compile(), write=True, interactive=False, silent=True)
        mock_patch.side_effect = lambda f, _: f

        tool.process_hunks(target, hunks)
        string_hunks = ""
        for hunk in hunks:
            string_hunks += "\n".join(hunk[2:]) + "\n"
        string_hunks = f"--- {target}\n+++ {target}\n" + string_hunks
        with open(target) as f:
            input = f.read()

        mock_patch.assert_called_with(input, string_hunks)

    @mock.patch.object(log, "exception")
    def test_process_hunks_invalid_hunks(self, mock_log):
        tool = BowlerTool(Query().compile(), write=True, interactive=False, silent=True)

        tool.process_hunks(target, hunks)
        mock_log.assert_called_with(
            f"failed to apply patch hunk: context error 4: start before range_start"
        )

    @mock.patch.object(log, "exception")
    def test_process_hunks_no_hunks(self, mock_log):
        tool = BowlerTool(Query().compile(), write=True, interactive=False)
        empty_hunks = [[]]
        tool.process_hunks(target, empty_hunks)
        patch_stderr = "Lines without hunk header at '\\n'"
        mock_log.assert_called_with(f"failed to apply patch hunk: {patch_stderr}")

    @mock.patch("bowler.tool.prompt_user")
    @mock.patch("bowler.tool.apply_single_file")
    def test_process_hunks_after_skip_rest(self, mock_patch, mock_prompt):
        # Test that we apply the hunks that have been 'yessed' and nothing more
        tool = BowlerTool(Query().compile(), silent=False)
        mock_patch.side_effect = lambda f, _: f
        mock_prompt.side_effect = ["y", "d"]
        tool.process_hunks(target, hunks)
        mock_patch.assert_called_once_with(mock.ANY, "\n".join(hunks[0]) + "\n")

    @mock.patch("bowler.tool.prompt_user")
    @mock.patch("bowler.tool.apply_single_file")
    def test_process_hunks_after_quit(self, mock_patch, mock_prompt):
        # Test that we apply the hunks that have been 'yessed' and nothing more
        tool = BowlerTool(Query().compile(), silent=False)
        mock_patch.side_effect = lambda f, _: f
        mock_prompt.side_effect = ["y", "q"]
        with self.assertRaises(BowlerQuit):
            tool.process_hunks(target, hunks)
        mock_patch.assert_called_once_with(mock.ANY, "\n".join(hunks[0]) + "\n")

    @mock.patch("bowler.tool.prompt_user")
    @mock.patch("bowler.tool.apply_single_file")
    def test_process_hunks_after_auto_yes(self, mock_patch, mock_prompt):
        tool = BowlerTool(Query().compile(), silent=False)
        mock_patch.side_effect = lambda f, _: f
        mock_prompt.side_effect = ["a"]
        tool.process_hunks(target, hunks)
        joined_hunks = "".join(["\n".join(hunk[2:]) + "\n" for hunk in hunks])
        encoded_hunks = f"--- {target}\n+++ {target}\n{joined_hunks}"
        mock_patch.assert_called_once_with(mock.ANY, encoded_hunks)

    @mock.patch("bowler.tool.prompt_user")
    @mock.patch("bowler.tool.apply_single_file")
    def test_process_hunks_after_no_then_yes(self, mock_patch, mock_prompt):
        tool = BowlerTool(Query().compile(), silent=False)
        mock_patch.side_effect = lambda f, _: f
        mock_prompt.side_effect = ["n", "y"]
        tool.process_hunks(target, hunks)
        mock_patch.assert_called_once_with(mock.ANY, "\n".join(hunks[1]) + "\n")

    @mock.patch("bowler.tool.prompt_user")
    @mock.patch("bowler.tool.apply_single_file")
    def test_process_hunks_after_only_no(self, mock_patch, mock_prompt):
        tool = BowlerTool(Query().compile(), silent=False)
        mock_patch.side_effect = lambda f, _: f
        mock_prompt.side_effect = ["n", "n"]
        tool.process_hunks(target, hunks)
        mock_patch.assert_not_called()

    def test_validate_print(self):
        tool = BowlerTool(Query().compile(), silent=False)
        # Passes
        tool.processed_file(
            new_text="print('str')", filename="foo.py", old_text="print('str')"
        )
        # Fails
        with self.assertRaises(BadTransform):
            tool.processed_file(
                new_text="print 'str'", filename="foo.py", old_text="print('str')"
            )

    def test_validate_completely_invalid(self):
        tool = BowlerTool(Query().compile(), silent=False)
        with self.assertRaises(BadTransform):
            tool.processed_file(new_text="x=1///2", filename="foo.py", old_text="x=1/2")
