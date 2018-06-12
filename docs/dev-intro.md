---
id: dev-intro
title: Developing Bowler
---

We want to make contributing to this project as easy and transparent as
possible.

## Getting Started

When developing Bowler, follow these steps to setup your environment,
format your code, and run linters and unit  tests:

1. Fork [Bowler][] on Github.

1. Clone the git repo:
```bash
$ git clone https://github.com/$USERNAME/bowler
$ cd bowler
```

1. Setup the virtual environment with dependencies and tools:
```bash
$ make dev
$ source .venv/bin/activate
```

1. Format your code using [*Black*](https://github.com/ambv/black) and
  [isort](https://pypi.org/project/isort/):
```bash
$ make format
```

1. Run linter, type checks, and unit tests:
```bash
$ make lint test
```

## Pull Requests

We actively welcome your pull requests.

1. If you've added code that should be tested, add unit tests.
1. If you've changed APIs, update the documentation.
1. Ensure the test suite passes.
1. Make sure your code lints.
1. If you haven't already, complete the Contributor License Agreement ("CLA").

## Contributor License Agreement ("CLA")

In order to accept your pull request, we need you to submit a CLA. You only need
to do this once to work on any of Facebook's open source projects.

Complete your CLA here: <https://code.facebook.com/cla>

## Issues

We use GitHub issues to track public bugs. Please ensure your description is
clear and has sufficient instructions to be able to reproduce the issue.

Facebook has a [bounty program](https://www.facebook.com/whitehat/) for the safe
disclosure of security bugs. In those cases, please go through the process
outlined on that page and do not file a public issue.

## License

By contributing to Bowler, you agree that your contributions will be licensed
under the `LICENSE` file in the root directory of this source tree.


[Bowler]: https://github.com/facebookincubator/bowler
