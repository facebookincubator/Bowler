---
id: basics-intro
title: Introduction
---

## What is Bowler?

Bowler is a refactoring tool for manipulating Python at the syntax tree level. It
enables safe, large scale code modifications while guaranteeing that the resulting code
compiles and runs. It provides both a simple command line interface and a fluent API in
Python for generating complex code modifications in code.

Bowler is built on **lib2to3** from the standard Python library, and requires only a few
third party dependencies, like [click][], for common components.


## Why lib2to3

**lib2to3** provides a concrete syntax tree (CST) implementation that recognizes and
supports the grammar of all Python versions back to 2.6.  By nature of being a CST,
**lib2to3** enables modifications to the syntax tree while maintaining all formatting and
comments, preventing modifications from destroying valuable information.

By building on **lib2to3**, Bowler is capable of reading and modifying source files
written for both Python 2 and 3.  That said, Bowler requires Python 3.6 or newer to run,
as it uses a large number of modern features of the language to enable more readable
and maintainable code.

> Technical detail: Bowler actually uses **[fissix][]**, a backport of lib2to3 that
> includes a few minor improvements and features that have not yet been upstreamed
> to CPython.  This allows Bowler to parse grammars and utilize features from newer
> versions of Python than might otherwise be supported by the local runtime.


[click]: http://click.pocoo.org/
[fissix]: https://github.com/jreese/fissix
