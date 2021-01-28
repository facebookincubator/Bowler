<a href="https://pybowler.io"><img alt="Bowler" height="96" src="https://github.com/facebookincubator/Bowler/raw/master/website/static/img/logo/Bowler_FullColor_DarkText.png" /></a>

**Safe code refactoring for modern Python projects.**

[![build status](https://github.com/facebookincubator/Bowler/workflows/Build/badge.svg)](https://github.com/facebookincubator/Bowler/actions)
[![code coverage](https://img.shields.io/codecov/c/github/facebookincubator/Bowler)](https://codecov.io/gh/facebookincubator/Bowler)
[![version](https://img.shields.io/pypi/v/bowler.svg)](https://pypi.org/project/bowler)
[![changelog](https://img.shields.io/badge/change-log-blue.svg)](https://github.com/facebookincubator/bowler/blob/master/CHANGELOG.md)
[![license](https://img.shields.io/pypi/l/bowler.svg)](https://github.com/facebookincubator/bowler/blob/master/LICENSE)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


Current Development Status
--------------------------

Bowler 0.x is based on fissix (a fork of lib2to3) which was never intended to be a
stable api.  We've pretty much reached the limit of being able to add new language
features, so while we can support 3.8's walrus, that's basically the last it's going to
get.

See discussion for [`f(**not x)`](https://bugs.python.org/issue36541) for one example --
a proper fix for things like this would mean invalidating all current patterns since
there's no way to match against a specific revision of the grammar.

If you need to do codemods today, we recommend looking at 
[LibCST codemods](https://libcst.readthedocs.io/en/stable/codemods_tutorial.html) which
are a bit more verbose, but work well on modern python grammars.  We have contributed
[support for Python 3.0-3.3 grammars](https://github.com/Instagram/LibCST/pull/261)
and have a draft PR going even further [back to 2.3](https://github.com/Instagram/LibCST/pull/275).

The longer term plan for Bowler is to build Bowler 2.x on top of libcst's parser, while
still supporting a very simple fluent api.  That's unlikely to materialize in a final
release during 2021.


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
