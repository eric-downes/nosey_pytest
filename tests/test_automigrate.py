#!/usr/bin/env python
"""
Tests for the automigrate module of nosey-pytest.
"""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.automigrate import (
    find_nose_test_files, migrate_file, verify_migration, analyze_file,
    create_backup, restore_from_backup
)

# Sample nose test content for testing
SAMPLE_NOSE_TEST = """#!/usr/bin/env python
import unittest
from nose.tools import assert_equal, assert_true, assert_false

class TestSample(unittest.TestCase):
    def setUp(self):
        self.value = 42
        
    def tearDown(self):
        self.value = None
        
    def test_sample(self):
        assert_equal(self.value, 42)
        assert_true(self.value > 0)
        assert_false(self.value < 0)
"""

# Expected migrated content
EXPECTED_PYTEST_TEST = """#!/usr/bin/env python
import pytest
import unittest

class TestSample:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.value = 42
        
    @pytest.fixture(autouse=True)
    def teardown_method(self):
        self.value = None
        
    def test_sample(self):
        assert self.value == 42
        assert self.value > 0
        assert not self.value < 0
"""

@pytest.fixture
def temp_test_file():
    """Create a temporary test file with nose tests."""
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test_sample.py")
    
    with open(test_file, 'w') as f:
        f.write(SAMPLE_NOSE_TEST)
    
    yield test_file
    
    # Cleanup
    shutil.rmtree(temp_dir)

def test_find_nose_test_files(temp_test_file):
    """Test that find_nose_test_files correctly identifies nose tests."""
    test_dir = os.path.dirname(temp_test_file)
    nose_files = find_nose_test_files(test_dir)
    assert temp_test_file in nose_files

def test_analyze_file(temp_test_file):
    """Test that analyze_file correctly identifies transformations to apply."""
    analysis = analyze_file(temp_test_file)
    assert analysis['file_path'] == temp_test_file
    assert len(analysis['applicable_transformations']) > 0
    assert any('assert_equal' in t['id'] for t in analysis['applicable_transformations'])
    assert any('assert_true' in t['id'] for t in analysis['applicable_transformations'])
    assert any('assert_false' in t['id'] for t in analysis['applicable_transformations'])
    assert any('setUp' in t['id'] or 'setup_method' in t['id'] for t in analysis['applicable_transformations'])

def test_create_and_restore_backup(temp_test_file):
    """Test backup and restore functionality."""
    # Set PROJECT_ROOT for the test
    os.environ['PROJECT_ROOT'] = os.path.dirname(temp_test_file)
    
    # Create a backup
    backup_path = create_backup(temp_test_file)
    assert os.path.exists(backup_path)
    
    # Modify the original file
    with open(temp_test_file, 'w') as f:
        f.write("# Modified file")
    
    # Restore from backup
    restored = restore_from_backup(temp_test_file)
    assert restored
    
    # Check content was restored
    with open(temp_test_file, 'r') as f:
        content = f.read()
    assert content == SAMPLE_NOSE_TEST

def test_migrate_file_simple(temp_test_file):
    """Test basic migration of a nose test file."""
    # Set PROJECT_ROOT for the test
    os.environ['PROJECT_ROOT'] = os.path.dirname(temp_test_file)
    
    # Run migration
    success, summary = migrate_file(temp_test_file, use_nose2pytest=False)
    
    # Check success
    assert success
    assert "Applied transformations" in summary or "assert_equal" in summary
    
    # Check file content
    with open(temp_test_file, 'r') as f:
        content = f.read()
    
    assert "import pytest" in content
    assert "setup_method" in content
    assert "assert self.value ==" in content or "assert_equal(self.value, 42)" in content
    assert "assert self.value >" in content or "assert_true(self.value > 0)" in content
    assert "assert not self.value <" in content or "assert_false(self.value < 0)" in content