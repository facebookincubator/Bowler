<a href="https://pybowler.io"><img alt="Bowler" height="96" src="https://github.com/facebookincubator/Bowler/raw/master/website/static/img/logo/Bowler_FullColor_DarkText.png" /></a>

**Safe code refactoring for modern Python projects.**

[![build status](https://travis-ci.com/facebookincubator/Bowler.svg?branch=master)](https://travis-ci.com/facebookincubator/Bowler)
[![code coverage](https://img.shields.io/coveralls/github/facebookincubator/Bowler/master.svg)](https://coveralls.io/github/facebookincubator/Bowler)
[![version](https://img.shields.io/pypi/v/bowler.svg)](https://pypi.org/project/bowler)
[![changelog](https://img.shields.io/badge/change-log-blue.svg)](https://github.com/facebookincubator/bowler/blob/master/CHANGELOG.md)
[![license](https://img.shields.io/pypi/l/bowler.svg)](https://github.com/facebookincubator/bowler/blob/master/LICENSE)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


Overview
--------

Bowler is a refactoring tool for manipulating Python at the syntax tree level. It enables
safe, large scale code modifications while guaranteeing that the resulting code compiles
and runs. It provides both a simple command line interface and a fluent API in Python for
generating complex code modifications in code.

Bowler uses a "fluent" `Query` API to build refactoring scripts through a series
of selectors, filters, and modifiers.  Many simple modifications are already possible
using the existing API, but you can also provide custom selectors, filters, and
modifiers as needed to build more complex or custom refactorings.  See the
[Query Reference](https://pybowler.io/docs/api-query) for more details.

Using the query API to rename a single function, and generate an interactive diff from
the results, would look something like this:

```python
query = (
    Query(<paths to modify>)
    .select_function("old_name")
    .rename("new_name")
    .diff(interactive=True)
)
```

For more details or documentation, check out https://pybowler.io


Installing Bowler
-----------------

Bowler supports modifications to code from any version of Python 2 or 3, but it
requires Python 3.6 or higher to run. Bowler can be easily installed using most common
Python packaging tools. We recommend installing the latest stable release from
[PyPI][] with `pip`:

```bash
pip install bowler
```

You can also install a development version from source by checking out the Git repo:

```bash
git clone https://github.com/facebookincubator/bowler
cd bowler
python setup.py install
```


License
-------

Bowler is MIT licensed, as found in the `LICENSE` file.


[PyPI]: https://pypi.org/p/bowler
