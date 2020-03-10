#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from bowler.tests.lib import BowlerTestCase


class Tests(BowlerTestCase):
    def test_pass(self):
        pass

    def test_fail(self):
        assert False
