#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

with open("bowler/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]

with open("requirements.txt") as f:
    requires = f.read().strip().splitlines()

setup(
    name="bowler",
    description="Safe code refactoring for modern Python projects",
    long_description=readme,
    long_description_content_type="text/markdown",
    version=version,
    author="John Reese, Facebook",
    author_email="jreese@fb.com",
    url="https://github.com/facebookincubator/bowler",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    license="MIT",
    packages=["bowler", "bowler.tests"],
    test_suite="bowler.tests",
    python_requires=">=3.6",
    setup_requires=["setuptools>=38.6.0"],
    install_requires=requires,
    entry_points={"console_scripts": ["bowler = bowler.main:main"]},
)
