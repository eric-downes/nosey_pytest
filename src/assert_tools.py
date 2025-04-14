"""
Drop-in replacement for nose.tools.assert_* functions that don't have direct pytest raw assert equivalents.
Adapted from nose2pytest's assert_tools.py to work with our migration toolkit.

These functions can be used by projects migrating from nose to pytest for the handful
of assert functions that nose2pytest doesn't convert to raw asserts.

Copyright (c) 2025 eric-downes
Portions derived from nose2pytest (Copyright (c) 2016 Oliver Schoenborn)
Licensed under the MIT License (see LICENSE file for details)
"""

import pytest
import unittest

__all__ = [
    'assert_dict_contains_subset',
    'assert_raises_regex',
    'assert_raises_regexp',
    'assert_regexp_matches',
    'assert_warns_regex',
]

def assert_dict_contains_subset(subset, dictionary, msg=None):
    """
    Checks whether dictionary is a superset of subset. If not, the assertion message will have useful details,
    unless msg is given, then msg is output.
    """
    dictionary = dictionary
    missing_keys = sorted(list(set(subset.keys()) - set(dictionary.keys())))
    mismatch_vals = {k: (subset[k], dictionary[k]) for k in subset if k in dictionary and subset[k] != dictionary[k]}
    if msg is None:
        assert missing_keys == [], 'Missing keys = {}'.format(missing_keys)
        assert mismatch_vals == {}, 'Mismatched values (s, d) = {}'.format(mismatch_vals)
    else:
        assert missing_keys == [], msg
        assert mismatch_vals == {}, msg

# Make other unittest.TestCase methods available as-is as functions; trick taken from Nose
class _Dummy(unittest.TestCase):
    def do_nothing(self):
        pass

_t = _Dummy('do_nothing')

assert_raises_regex = _t.assertRaisesRegex
assert_raises_regexp = _t.assertRaisesRegex
assert_regexp_matches = _t.assertRegex
assert_warns_regex = _t.assertWarnsRegex

del _Dummy
del _t

# Register with pytest plugin system
def pytest_configure():
    for name, obj in globals().items():
        if name.startswith('assert_'):
            setattr(pytest, name, obj)