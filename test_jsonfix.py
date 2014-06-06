# -*- coding: utf-8 -*-

import unittest
import math

inf = float("inf")
nan = float("nan")


def get_MUT():
    import jsonfix as m
    return m


class FixedJSONDecoderTest(unittest.TestCase):
    def get_one(self):
        return get_MUT().FixedJSONDecoder()

    def test_decode_numbers(self):
        result = self.get_one().decode('{"int":0,"float":3.14}')
        expected = {u'int': 0, u'float': 3.14}
        self.assertEquals(result, expected)

    def test_decode_constants(self):
        result = self.get_one().decode(
            '{"true":true,"false":false,"null":null}')
        expected = {u'true': True, u'false': False, u'null': None}
        self.assertEquals(result, expected)

    def test_decode_nans(self):
        result = self.get_one().decode('{"key":[NaN,Infinity,-Infinity]}')
        self.assertEquals(list(result.keys()), ["key"])
        self.assertEquals(len(result["key"]), 3)
        self.assertTrue(math.isnan(result["key"][0]))
        self.assertEquals(result["key"][1:], [inf, -inf])

    def test_decode_malformed_nans(self):
        result = self.get_one().decode('{"key":[nan,inf,-inf]}')
        self.assertEquals(list(result.keys()), ["key"])
        self.assertEquals(len(result["key"]), 3)
        self.assertTrue(math.isnan(result["key"][0]))
        self.assertEquals(result["key"][1:], [inf, -inf])

    def test_decode_nested(self):
        result = self.get_one().decode('{"key":[{"nan":nan}]}')
        self.assertEquals(list(result.keys()), ["key"])
        self.assertEquals(len(result["key"]), 1)
        self.assertEquals(list(result["key"][0].keys()), ["nan"])
        self.assertTrue(math.isnan(result["key"][0]["nan"]))

    def test_borken_json(self):
        def target():
            self.get_one().decode('{"key":[')
        self.assertRaises(ValueError, target)

    def test_unknown_literal(self):
        def target():
            self.get_one().decode('{"key":aaa}')
        self.assertRaises(ValueError, target)


if __name__ == '__main__':
    unittest.main()
