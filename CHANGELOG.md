## v0.6.0

* Fix matching for functions with more than one decorators (#10)
* Fix matching function/method calls preceded by the `await` keyword (#6)
* Fix silent failures when processing files without trailing newlines (#20)
* Better patching behavior for large files with many hunks (#21)
* Support passing `pathlib.Path` values to `Query()` (#23)
* Fix interactive mode when IPython not available (#31)
* Better error logging and debugging (#38, #39)
* Support refactoring arbitrary file extensions (#37)
* Better testing framework and more unit tests (#43)
* New helpers for numeric type inference (#42)
* Support returning leaf/node elements from modifiers (#14, #44)
* Fix lint/type checking on Python 3.7+ (#45)
* Fixes and improvements to documentation (#13, #30, #32)
* Consistent shebang/copyright headers in source files (#24, #25, #33)

```bash
$ git shortlog -sn v0.5.1...
    22  John Reese
    18  Tim Hatch
     8  Lisa Roach
     3  Syrus Akbary
     1  Sadie Bartholomew
     1  Bruno Oliveira
     1  Łukasz Langa
     1  Christian Delahousse
     1  Loren Carvalho
     1  Qingzhuo Aw Young
```
