"""
Test file with nose assertions to test our migration tool.
"""

import pytest

def test_basic_assertions():
    # Basic assertions with two parameters
    assert 1 == 1
    assert 1 != 2
    assert True
    assert not False
    assert 1 is 1
    assert 1 is not 2
    assert None is None
    assert 42 is not None
    assert 'a' in 'abc'
    assert 'd' not in 'abc'
    
    # Assertions with message parameter
    assert 1 == 1, "Values should be equal"
    assert 1 != 2, "Values should not be equal"
    assert True, "Value should be true"
    assert not False, "Value should be false"
    assert 1 is 1, "Objects should be identical"
    assert 1 is not 2, "Objects should not be identical"
    assert None is None, "Value should be None"
    assert 42 is not None, "Value should not be None"
    assert 'a' in 'abc', "Value should be in the collection"
    assert 'd' not in 'abc', "Value should not be in the collection"
    
    # Complex assertions
    assert 1.001 == pytest.approx(1.002, abs=2)  # Places parameter
    assert 1.001 == pytest.approx(1.002, abs=2), "Should be almost equal with 2 places"  # Places and message
    assert 1.001 == pytest.approx(1.002), "Should be almost equal by default"  # Just message