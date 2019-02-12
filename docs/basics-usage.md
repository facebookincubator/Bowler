---
id: basics-usage
title: Usage
---

Bowler provides two primary mechanisms for refactoring.  It provides a
[fluent API](fixers) for standalone applications to import and use, and it also
provides a simple command line tool for executing one or more refactoring scripts
on a given set of directories or files.


## Command Line

Bowler has multiple commands, which allow you to debug or execute code refactoring
scripts in the most convenient format for you.  See the
[Command Reference](api-commands.md) for more details.

```bash
bowler <command> [<options> ...]
```

## Fluent API

Bowler uses a "fluent" `Query` API to build refactoring scripts through a series
of selectors, filters, and modifiers.  Many simple modifications are already possible
using the existing API, but you can also provide custom selectors, filters, and
modifiers as needed to build more complex or custom refactorings.  See the
[Query Reference](api-query.md) for more details.

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

## Refactoring Scripts

Refactoring scripts combine the mechanisms above to provide self-contained, reusable
components for refactoring large code bases.  They consist of one or more queries or
fixers in a single Python file, ready to be imported and executed by Bowler.  This
allows the user to run these predefined or parameterized refactors on future code,
enabling long term benefits from the initial effort.

For example, if we have a simple refactoring script named `rename_func.py`:

```python
from bowler import Query


old_name, new_name = sys.argv[1:]
(
    Query(".")
    .select_function(old_name)
    .rename(new_name)
    .idiff()
)
```

That script can then be executed directly as a normal python application, or with the
following Bowler command, to interactively rename and function called `foo` to `bar`,
including all references:

```bash
bowler run rename_func.py -- foo bar
```
