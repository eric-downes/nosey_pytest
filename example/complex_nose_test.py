#!/usr/bin/env python
"""
A complex nose test file showcasing various nose features that need migration.
This file is a comprehensive example used to test all migration features.
"""

import unittest
import os
import tempfile
import shutil
from nose.tools import (
    assert_equal, assert_not_equal, assert_true, assert_false,
    assert_is_none, assert_is_not_none, assert_raises, raises,
    assert_in, assert_not_in, assert_is, assert_is_not,
    assert_greater, assert_greater_equal, assert_less, assert_less_equal,
    assert_almost_equal, assert_dict_contains_subset, istest, nottest
)

# Create a complex example class that uses unittest.TestCase inheritance
class TestComplexSample(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("Test content")
        self.values = [1, 2, 3, 4, 5]
        self.dict = {"name": "test", "value": 42}
        
    def tearDown(self):
        """Clean up after test."""
        shutil.rmtree(self.temp_dir)
        
    def test_file_operations(self):
        """Test file operations."""
        assert_true(os.path.exists(self.test_file))
        with open(self.test_file, 'r') as f:
            content = f.read()
        assert_equal(content, "Test content")
        
    def test_assertions(self):
        """Test various assertion types."""
        # Equality assertions
        assert_equal(2 + 2, 4)
        assert_not_equal(2 + 2, 5)
        
        # Boolean assertions
        assert_true(True)
        assert_false(False)
        
        # None assertions
        x = None
        y = "not none"
        assert_is_none(x)
        assert_is_not_none(y)
        
        # Containment assertions
        assert_in(3, self.values)
        assert_not_in(10, self.values)
        
        # Identity assertions
        a = []
        b = a
        c = []
        assert_is(a, b)
        assert_is_not(a, c)
        
        # Comparison assertions
        assert_greater(5, 4)
        assert_greater_equal(5, 5)
        assert_less(4, 5)
        assert_less_equal(5, 5)
        
        # Approximate equality
        assert_almost_equal(0.1 + 0.2, 0.3, places=1)
        
        # Dict subset
        assert_dict_contains_subset({"name": "test"}, self.dict)
        
    @raises(ZeroDivisionError)
    def test_division_by_zero(self):
        """Test division by zero with @raises decorator."""
        return 1 / 0
        
    def test_exception_context(self):
        """Test exception with context manager."""
        with assert_raises(ValueError):
            raise ValueError("Test error")

# Define test function with yield for parametrization
def test_yield_values():
    """Test multiple values with yield."""
    for value in [1, 2, 3, 4, 5]:
        yield check_value, value

def check_value(value):
    """Check that value is positive."""
    assert_true(value > 0)
    
# Define complex yield test with multiple parameters
def test_combinations():
    """Test combinations of values with yield."""
    for x in range(1, 3):
        for y in ['a', 'b']:
            yield check_combination, x, y
            
def check_combination(x, y):
    """Check combination of values."""
    assert_equal(type(x), int)
    assert_equal(type(y), str)

# Use istest decorator for a class that doesn't follow naming convention
@istest
class SampleTests:
    def sample_test(self):
        """Test with non-standard name."""
        assert_true(True)
        
    def test_sample(self):
        """Test with standard name."""
        assert_false(False)

# Mark a helper function as not a test
@nottest
def helper_function():
    """Helper function that shouldn't be treated as a test."""
    return True

# Define a test function that doesn't follow naming convention
def verify_something():
    """Non-standard test function name."""
    assert_equal(2 * 2, 4)