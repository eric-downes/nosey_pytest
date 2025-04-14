#!/usr/bin/env python
"""
Sample nose test file for migration demonstration.
"""

import unittest
import pytest, assert_equal, assert_true, assert_false

class TestSample:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.value = 42
        self.list = [1, 2, 3]
        
    @pytest.fixture(autouse=True)
    def teardown_method(self):
        self.value = None
        self.list = None
        
    def test_sample_equality(self):
        assert_equal(self.value, 42)
        assert self.value == 42
        
    @pytest.mark.xfail(raises=ZeroDivisionError)
    def test_division_by_zero(self):
        return 1 / 0
        
    def test_boolean_conditions(self):
        assert_true(self.value > 0)
        assert_false(self.value < 0)
        assert self.value > 0
        assert not self.value < 0
        
    def test_list_manipulation(self):
        self.list.append(4)
        assert_equal(len(self.list), 4)
        assert self.list[-1] == 4
        
# Sample yield test
@pytest.mark.parametrize("i", range(3))
def test_yield_sample(i):
    check_number(i)

def check_number(value):
    assert value < 3