#!/usr/bin/env python3

from unittest import TestCase

from ..query import SELECTORS, Query


class QueryTest(TestCase):
    fake_paths = ["foo/bar", "baz.py"]

    def test_basic(self):
        query = Query(self.fake_paths)
        self.assertEqual(len(query.transforms), 0)
        self.assertEqual(query.paths, self.fake_paths)
        with self.assertRaises(ValueError):
            transform = query.current
            self.assertEqual(transform, None)

        query.select_root().is_filename("frob.py")
        self.assertEqual(len(query.transforms), 1)
        self.assertEqual(query.current.selector, "root")
        self.assertEqual(len(query.current.kwargs), 0)
        self.assertEqual(len(query.current.filters), 1)
        self.assertEqual(len(query.current.filters), 1)

        fixers = query.compile()
        self.assertEqual(len(fixers), 1)
        self.assertEqual(fixers[0].PATTERN, SELECTORS["root"].strip())
