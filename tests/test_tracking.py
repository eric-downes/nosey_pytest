#!/usr/bin/env python
"""
Tests for the tracking module of nosey-pytest.
"""

import os
import sys
import json
import tempfile
import shutil
import pytest
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tracking import (
    create_default_migration_data, update_test_status, get_test_status,
    rescan_tests
)

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with test files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test directory
    test_dir = os.path.join(temp_dir, "tests")
    os.makedirs(test_dir)
    
    # Create a nose test file
    nose_test_file = os.path.join(test_dir, "test_nose.py")
    with open(nose_test_file, 'w') as f:
        f.write("""
from nose.tools import assert_equal

def test_sample():
    assert_equal(2 + 2, 4)
""")
    
    # Create a pytest test file
    pytest_test_file = os.path.join(test_dir, "test_pytest.py")
    with open(pytest_test_file, 'w') as f:
        f.write("""
import pytest

def test_sample():
    assert 2 + 2 == 4
""")
    
    # Set environment variables for tracking
    os.environ["PROJECT_ROOT"] = temp_dir
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

def test_create_default_migration_data(temp_project_dir):
    """Test creation of default migration data."""
    # Set test directories in config
    from src.tracking import CONFIG
    CONFIG["test_directories"] = ["tests"]
    CONFIG["project_root"] = temp_project_dir
    
    # Create migration data
    data = create_default_migration_data()
    
    # Check data structure
    assert "migrated_files" in data
    assert "total_tests" in data
    assert "nose_tests" in data
    assert "pytest_tests" in data
    assert "directory_status" in data
    assert "tests" in data["directory_status"]
    
    # Check counts
    assert data["total_tests"] == 2
    assert data["nose_tests"] == 1
    assert data["pytest_tests"] == 1

def test_update_test_status(temp_project_dir):
    """Test updating test status."""
    # Set test directories in config
    from src.tracking import CONFIG, MIGRATION_DATA_PATH
    CONFIG["test_directories"] = ["tests"]
    CONFIG["project_root"] = temp_project_dir
    CONFIG["migration_data_path"] = ".pytest_migration.json"
    
    # Create initial data
    create_default_migration_data()
    
    # Update test status
    nose_test_file = os.path.join(temp_project_dir, "tests", "test_nose.py")
    update_test_status(nose_test_file)
    
    # Get updated status
    status = get_test_status()
    
    # Check updated counts
    assert status["nose_tests"] == 0
    assert status["pytest_tests"] == 2
    assert os.path.relpath(nose_test_file, temp_project_dir) in status["migrated_files"]
    assert status["directory_status"]["tests"]["migrated"] == 2
    assert status["directory_status"]["tests"]["status"] == "DONE"

def test_rescan_tests(temp_project_dir):
    """Test rescanning test files."""
    # Set test directories in config
    from src.tracking import CONFIG
    CONFIG["test_directories"] = ["tests"]
    CONFIG["project_root"] = temp_project_dir
    
    # Create initial data
    create_default_migration_data()
    
    # Add a new nose test
    new_nose_test = os.path.join(temp_project_dir, "tests", "test_new_nose.py")
    with open(new_nose_test, 'w') as f:
        f.write("""
from nose.tools import assert_true

def test_sample():
    assert_true(True)
""")
    
    # Rescan tests
    rescan_tests()
    
    # Get updated status
    status = get_test_status()
    
    # Check updated counts
    assert status["total_tests"] == 3
    assert status["nose_tests"] == 2
    assert status["pytest_tests"] == 1
    assert status["directory_status"]["tests"]["total"] == 3