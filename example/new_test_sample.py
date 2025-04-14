#!/usr/bin/env python
"""
Sample nose test file for migration demonstration.
"""

import unittest
import pytest, assert_equal, assert_true, assert_false, assert_in, assert_is, assert_is_none, assert_almost_equal, istest, nottest

class TestSample:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.value = 42
        self.list = [1, 2, 3]
        self.dict = {"key": "value"}
        
    @pytest.fixture(autouse=True)
    def teardown_method(self):
        self.value = None
        self.list = None
        self.dict = None
        
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
        
    def test_additional_assertions(self):
        assert "key" in self.dict
        assert self.dict is self.dict
        assert None is None
        assert self.value is not None
        assert pytest.approx(0.1 + 0.2) == 0.3, places=1
        
# Test with the istest decorator

class AdditionalTests:
    def test_something(self):
        assert True
        
# Test with nottest decorator
@pytest.mark.skip(reason="Not a test")
def helper_function():
    return True
        
# Sample yield test
@pytest.mark.parametrize("i", range(3))
def test_yield_sample(i):
    check_number(i)

def check_number(value):
    assert value < 3
    
# Multiple parameter yield test
def test_yield_multi_params():
    for i in range(2):
        for j in ["a", "b"]:
            yield check_pair, i, j
            
def check_pair(num, letter):
    assert isinstance(num, int)
    assert isinstance(letter, str)
    
# Test function with non-test naming convention
def validate_test():
    return True