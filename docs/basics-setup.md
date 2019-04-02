---
id: basics-setup
title: Setup
---

## Installing Bowler

Bowler supports modifications to code from any version of Python 3, as well as
Python 2.6+ with use of print functions from `__future__`, but it requires
Python 3.6 or higher to run. Bowler can be easily installed using most common
Python packaging tools. We recommend installing the latest stable release from
[PyPI][] with `pip`:

```bash
pip install bowler
```

You can also install a development version from source by checking out the Git repo:

```bash
git clone https://github.com/facebookincubator/Bowler
cd Bowler
python setup.py install
```


## Configuration

Bowler tries to minimize the need for configuration.  It does not currently support
any configuration files, and has no command line parameters other than to control
logging output.  All configuration needed for Bowler can be done via the API while
executing any refactoring or code modification scripts.


[PyPI]: https://pypi.org/p/bowler
