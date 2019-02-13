---
id: basics-refactoring
title: Refactoring
---

Bowler builds on top of the Concrete Syntax Tree (CST) provided by **lib2to3** in the
standard library.  This enables direct modifications to the tree, without losing
formatting, comments, or whitespace, and without needing to directly support every
new version of Python as they get released.

## Fixers

Fixers are a core concept of refactoring in **lib2to3**, and they contain both
a grammar-based search "pattern" for finding nodes in the CST as well as methods for
transforming nodes that match the pattern.  They are relatively self-contained, and
form the core component of the `2to3` tool used for migrating older Python structures
to modern Python 3 analogues.

Bowler wraps much of its framework around generating a set of fixers, and then using
a modified version of the **lib2to3** refactoring framework to apply these fixers
to the target Python source files.  This allows Bowler to reuse and benefit from most
of the features in **lib2to3** while still allowing it to provide custom behaviors
and functionality not found in the standard library.

## Queries

Bowler operates by building "queries" against the CST.  Queries consist of one or more
"transforms", which specify what elements of the syntax tree to modify, as well as how
to modify those elements.  Each transform represents a search against the syntax tree,
along with a programmatic modification to any matched tree elements. These transforms
generate a fixer for **lib2to3**, and Bowler will execute multiple transforms
simultaneously on each file processed.  By combining multiple transforms together,
Bowler enables a wide range of refactoring, from simple renames to complicated upgrades
from old APIs to their modern replacements.

The primary mechanism for building queries and transforms in Bowler is by using a
"fluent" API:

> A fluent interface is a method for designing object oriented APIs based extensively
> on method chaining with the goal of making the readability of the source code close
> to that of ordinary written prose, essentially creating a domain-specific language
> within the interface. -- [Fluent Interface][fi]

This allows you to chain method calls to the `Query` class one after the other, without
needing to assign a query object to a variable or reference that variable for every
method call.  In practice, that looks something like this:

```python
(
    Query()
    .select(...)
    .modify(...)
    .execute()
)
```

## Transforms

Transforms are implicitly created by the `Query` API while defining the desired query.
Each transform begins with a "selector" (the syntax tree pattern to search for), or an
existing fixer class that already contains a selector pattern. Then, any number of
"filters" are specified, followed by one or more "modifiers". Each time a selector or
fixer is added to the query, a new transform is generated, and subsequent filters or
modifiers are added to the transform.

Repeating this pattern of selector, filters, and modifiers will generate further
transforms, each of which will be executed as elements in the syntax tree match the
selector patterns for a given transform.

### Selectors

These represents **lib2to3** search patterns to select syntax tree nodes matching the
given pattern, while capturing relevant child nodes or leaves when available.  Bowler
includes a set of common selectors that attempt to find all definitions or references
of a specific type, and uses a consistent naming scheme for all captured elements.

An example selector to find all uses of the `print` function might look like:

```python
pattern = """
    power< "print"
        trailer< "(" print_args=any* ")" >
    >
"""

(
    Query()
    .select(pattern)
    ...
)
```

This example finds all function calls named `print`, followed immediately by the
parenthetical trailer, and captures everything contained in those parentheses using the
name `print_args`.

### Filters

Once elements are found matching the active selector, filters can further limit which
elements are passed to the modifiers by inspecting the original matches and returning
`True` if it still matches, or `False` if the element should be excluded.  Elements
will only be considered as matches if they successfully pass all filter functions.
If an element fails one filter function, it will not be passed or considered for any
other filter functions.

An example filter, to pair with the example selector above, that only matches calls
to the print function with string literal arguments:

```python
def print_string(node: LN, capture: Capture, filename: Filename) -> bool:
    args = capture.get("print_args")

    # args will be a list because we captured `any*`
    if args:
        return len(args) == 1 and args[0].type == TOKEN.STRING:

    return False

(
    Query()
    ...
    .filter(print_string)
    ...
)
```

This filter function will only return `True` if the matched print call contained
exactly one argument, and that argument's type was a string literal.

### Modifiers

After matched elements have been filtered, all remaining matches will be passed to all
modifier functions in sequence.  The modifier function may then transform the syntax
tree at any point from the root to the leaves, without being restricted to the branch
corresponding to the matched element.  Transformations can include modifying existing
nodes or leaves, removing or replacing elements, or inserting elements into the tree.

An example modifier, which builds the above selector and filter examples, transforms
the string literal arguments of the print function to wrap them in a hypothetical
translation function (`tr`):

```python
def translate_string(node: LN, capture: Capture, filename: Filename) -> None:
    args = capture.get("print_args")

    # make sure the arguments haven't already been modified
    if args and args[0].type == TOKEN.STRING:
        args[0].replace(
            Call(
                Name("tr"),
                args=[args[0].clone()],
            )
        )

(
    Query()
    ...
    .modify(translate_string)
    ...
)
```

The modifier function replaces the existing string literal element with the nested
nodes to represent a call to the hypothetical translation function (`tr`), with a clone
of the existing string literal as the only argument.

> Note: take care to ensure that matched and captured elements still meet the
> expectations of your modifier function.  They may have already been transformed
> (or entirely removed or replaced) by previous modifiers.

### Processors

Bowler recognizes that there are cases where it's useful to post-process final changes
to the codebase, and provides a mechanism for attaching "processors" to the query.
These are functions that will be executed for each individual "hunk", or change, to
a file – the same "hunks" that you would see in a unified diff format – and optionally
decide whether that hunk should be applied or skipped.  This allows for behavior such
as extra logging, selective application of hunks based on conditions, record keeping
for future queries, and much more.

An example processor that keeps track of every file touched by the query:

```python
MODIFIED: Set[Filename] = set()

def modified_files(filename: Filename, hunk: Hunk) -> bool:
    MODIFIED.add(filename)
    return True

(
    Query()
    ...
    .process(modified_files)
    ...
)
```

## Execution

After building a query with some combination of selectors, filters, modifiers, and/or
processors, there are a few different execution commands that Bowler takes to determine
how it will apply the query to the codebase.  The default behavior when calling
`.execute()` on the query is to generate an interactive diff – similar to that provided
by `git add -p` – and show each hunk in series, asking the user to apply or skip that
hunk.  This is the "safest" option, as the user can verify that each change is intended
and meets the expectations of the refactoring.  There are also options to just generate
a diff without applying hunks, or to apply all hunks without asking, and there are
shortcut methods for each of these options as well.

```python
(
    Query()
    ...
    .execute(
        interactive = True,  # ask about each hunk
        write = False,  # automatically apply each hunk
        silent = False,  # don't ask or print hunks at all
    )
)
```


[fi]: https://en.wikipedia.org/wiki/Fluent_interface
