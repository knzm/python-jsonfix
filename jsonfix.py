# -*- coding: utf-8 -*-

import sys
import json.scanner

__all__ = ['FixedJSONDecoder']

if sys.version_info >= (3, 0, 0):
    has_encoding = False
    has_memo = True
    which_json = 'new'
elif sys.version_info[:2] == (2, 7):
    has_encoding = True
    has_memo = False
    which_json = 'new'
elif sys.version_info[:2] == (2, 6):
    has_encoding = False
    has_memo = False
    which_json = 'old'
else:
    has_encoding = False
    has_memo = False
    which_json = None


class JSONScanner(object):
    """
    Object-oriented equivalent to json.scanner.py_make_scanner()

    Used in Python 2.7 and later.
    """
    def __init__(self, context):
        self.context = context
        self.match_number = json.scanner.NUMBER_RE.match

    def parse_error(self, string, idx):
        raise StopIteration

    def scan_once(self, string, idx):
        try:
            return self._scan_once(string, idx)
        finally:
            if has_memo:
                self.context.memo.clear()

    def _scan_once(self, string, idx):
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration

        if nextchar == '"':
            args = [string, idx + 1]
            if has_encoding:
                args.append(self.context.encoding)
            args.append(self.context.strict)
            return self.context.parse_string(*args)
        elif nextchar == '{':
            args = [(string, idx + 1)]
            if has_encoding:
                args.append(self.context.encoding)
            args += [
                self.context.strict,
                self,
                self.context.object_hook,
                self.context.object_pairs_hook,
                ]
            if has_memo:
                args.append(self.context.memo)
            return self.context.parse_object(*args)
        elif nextchar == '[':
            return self.context.parse_array((string, idx + 1), self)
        elif nextchar == 'n' and string[idx:idx + 4] == 'null':
            return None, idx + 4
        elif nextchar == 't' and string[idx:idx + 4] == 'true':
            return True, idx + 4
        elif nextchar == 'f' and string[idx:idx + 5] == 'false':
            return False, idx + 5

        m = self.match_number(string, idx)
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = self.context.parse_float(
                    integer + (frac or '') + (exp or ''))
            else:
                res = self.context.parse_int(integer)
            return res, m.end()
        elif nextchar == 'N' and string[idx:idx + 3] == 'NaN':
            return self.context.parse_constant('NaN'), idx + 3
        elif nextchar == 'I' and string[idx:idx + 8] == 'Infinity':
            return self.context.parse_constant('Infinity'), idx + 8
        elif nextchar == '-' and string[idx:idx + 9] == '-Infinity':
            return self.context.parse_constant('-Infinity'), idx + 9
        else:
            return self.parse_error(string, idx)

    __call__ = scan_once


class FixedJSONScanner(JSONScanner):
    def parse_error(self, string, idx):
        nextchar = string[idx]
        if nextchar == 'n' and string[idx:idx + 3] == 'nan':
            return self.context.parse_constant('NaN'), idx + 3
        elif nextchar == 'i' and string[idx:idx + 3] == 'inf':
            return self.context.parse_constant('Infinity'), idx + 3
        elif nextchar == '-' and string[idx:idx + 4] == '-inf':
            return self.context.parse_constant('-Infinity'), idx + 4
        else:
            raise StopIteration


def patch_json_decoder():
    """
    Apply patches to json.decoder module.

    Used in Python 2.6.
    """
    import json.decoder
    from json.scanner import pattern, Scanner
    constants = json.decoder._CONSTANTS
    constants['nan'] = constants['NaN']
    constants['inf'] = constants['Infinity']
    constants['-inf'] = constants['-Infinity']
    JSONConstant = json.decoder.JSONConstant
    pattern('(-?inf|nan|-?Infinity|NaN|true|false|null)')(JSONConstant)
    json.decoder.JSONScanner = Scanner(json.decoder.ANYTHING)


if which_json == 'new':
    class FixedJSONDecoder(json.JSONDecoder):
        def __init__(self, **kw):
            super(FixedJSONDecoder, self).__init__(**kw)
            self.scan_once = FixedJSONScanner(self)

elif which_json == 'old':
    patch_json_decoder()
    FixedJSONDecoder = json.JSONDecoder

else:
    # fallback
    FixedJSONDecoder = json.JSONDecoder
