#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requires = f.read().strip().splitlines()

setup(
    install_requires=requires,
    use_scm_version={"write_to": "bowler/version.py"},
)
