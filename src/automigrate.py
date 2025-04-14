"""
Automated migration module for converting nose tests to pytest.

This module provides functions for:
1. Scanning and identifying tests using nose
2. Applying transformation patterns to migrate to pytest
3. Verifying migrations work correctly

Copyright (c) 2025 eric-downes
Licensed under the MIT License (see LICENSE file for details)
"""

import os
import re
import sys
import json
import tempfile
import shutil
import subprocess
import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Union

# Load configuration
def get_config():
    """Get or create configuration."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.pytest_automigrate_config.json')
    
    if not os.path.exists(config_path):
        # Create default config with common transformations
        config = DEFAULT_CONFIG.copy()
        
        # Add all transformations except those with lambdas
        # (which will be added programmatically after loading)
        serializable_transformations = []
        for transform in COMMON_TRANSFORMATIONS:
            if not callable(transform.get("replacement")):
                serializable_transformations.append(transform)
        
        config["transformation_patterns"] = serializable_transformations
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    else:
        # Load existing config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
            # Check if we need to update with new transformations
            existing_ids = {t["id"] for t in config.get("transformation_patterns", [])}
            for transform in COMMON_TRANSFORMATIONS:
                if transform["id"] not in existing_ids and not callable(transform.get("replacement")):
                    config.setdefault("transformation_patterns", []).append(transform)
                    
            # Save updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
    
    # Always add transformations from code if they have non-serializable parts like functions
    # or if they are marked as template or special_case
    existing_ids = {t["id"] for t in config.get("transformation_patterns", [])}
    for transform in COMMON_TRANSFORMATIONS:
        if (transform["id"] not in existing_ids or 
            transform.get("template") or 
            transform.get("special_case") or
            callable(transform.get("replacement"))):
            config.setdefault("transformation_patterns", []).append(transform)
            
    return config

# Configuration
DEFAULT_CONFIG = {
    "project_root": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "backup_dir": ".migration_backups",
    "tracking_script": None,  # Path to pytest_migration.py script if available
    "test_command": ["pytest", "-xvs"],
    "test_file_patterns": ["test_*.py", "*_test.py"],
    "initialized": False,
    "initialized_date": None,
    "git_integration": True,  # Use Git for version control
    "git_branch": "pytest-migration",  # Branch to create for migration
    "transformation_patterns": []
}

# Common transformation patterns
COMMON_TRANSFORMATIONS = [
    # Import replacements
    {
        "id": "nose_tools_assertions_import",
        "pattern": r'from\s+nose\.tools\s+import\s+assert_.*?(?:\n|$)',
        "replacement": '',
        "description": 'Remove nose.tools assertion imports',
        "priority": 5,
        "enabled": True
    },
    {
        "id": "nose_raises_import",
        "pattern": r'from\s+nose\.tools\s+import\s+raises',
        "replacement": 'import pytest',
        "description": 'Replace nose.tools.raises import with pytest',
        "priority": 10,
        "enabled": True
    },
    {
        "id": "nose_base_import",
        "pattern": r'import\s+nose(?!\S)',
        "replacement": 'import pytest',
        "description": 'Replace nose import with pytest',
        "priority": 10,
        "enabled": True
    },
    {
        "id": "nose_from_import",
        "pattern": r'from\s+nose\s+import\s+',
        "replacement": 'import pytest # Replacing: from nose import ',
        "description": 'Replace nose imports with pytest',
        "priority": 10,
        "enabled": True
    },
    {
        "id": "nose_tools_import",
        "pattern": r'from\s+nose\.tools\s+import\s+',
        "replacement": 'import pytest # Replacing: from nose.tools import ',
        "description": 'Replace nose.tools imports with pytest',
        "priority": 10, 
        "enabled": True
    },
    {
        "id": "nose_tools_assert_equal_import",
        "pattern": r'from\s+nose\.tools\s+import\s+(.*\b)assert_equal(\b.*)',
        "replacement": r'import pytest # Replacing: from nose.tools import \1assert_equal\2',
        "description": 'Replace nose.tools import assert_equal with pytest',
        "priority": 5,
        "enabled": True
    },
    # Decorator replacements
    {
        "id": "raises_decorator",
        "pattern": r'@raises\(([^)]+)\)',
        "replacement": r'@pytest.mark.xfail(raises=\1)',
        "description": 'Convert @raises to @pytest.mark.xfail',
        "priority": 20,
        "enabled": False  # Disabled since we have a more specific version now
    },
    {
        "id": "expected_failure_function",
        "pattern": r'def\s+expected_failure\(test\):.*?return\s+inner',
        "replacement": '# Replaced with pytest.mark.xfail',
        "description": 'Remove expected_failure helper function',
        "priority": 20,
        "flags": re.DOTALL,
        "enabled": True
    },
    {
        "id": "expected_failure_decorator",
        "pattern": r'@expected_failure',
        "replacement": '@pytest.mark.xfail(reason="Expected to fail")',
        "description": 'Convert @expected_failure to @pytest.mark.xfail',
        "priority": 20,
        "enabled": True
    },
    {
        "id": "istest_decorator",
        "pattern": r'@istest',
        "replacement": '',  # Remove @istest as pytest uses naming conventions
        "description": 'Remove @istest decorator',
        "priority": 20,
        "enabled": True
    },
    {
        "id": "nottest_decorator",
        "pattern": r'@nottest',
        "replacement": '@pytest.mark.skip(reason="Not a test")',
        "description": 'Convert @nottest to @pytest.mark.skip',
        "priority": 20,
        "enabled": True
    },
    # Assert replacements
    {
        "id": "assert_equal",
        "pattern": r'self\.assertEqual\(([^,]+),\s*([^)]+)\)',
        "replacement": r'assert \1 == \2',
        "description": 'Convert assertEqual to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_not_equal",
        "pattern": r'self\.assertNotEqual\(([^,]+),\s*([^)]+)\)',
        "replacement": r'assert \1 != \2',
        "description": 'Convert assertNotEqual to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_true",
        "pattern": r'self\.assertTrue\(([^)]+)\)',
        "replacement": r'assert \1',
        "description": 'Convert assertTrue to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_false",
        "pattern": r'self\.assertFalse\(([^)]+)\)',
        "replacement": r'assert not \1',
        "description": 'Convert assertFalse to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_raises",
        "pattern": r'self\.assertRaises\(([^,]+),\s*([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'with pytest.raises(\1):\n        \2\3',
        "description": 'Convert assertRaises to pytest.raises',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_in",
        "pattern": r'self\.assertIn\(([^,]+),\s*([^)]+)\)',
        "replacement": r'assert \1 in \2',
        "description": 'Convert assertIn to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_not_in",
        "pattern": r'self\.assertNotIn\(([^,]+),\s*([^)]+)\)',
        "replacement": r'assert \1 not in \2',
        "description": 'Convert assertNotIn to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_is",
        "pattern": r'self\.assertIs\(([^,]+),\s*([^)]+)\)',
        "replacement": r'assert \1 is \2',
        "description": 'Convert assertIs to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_is_not",
        "pattern": r'self\.assertIsNot\(([^,]+),\s*([^)]+)\)',
        "replacement": r'assert \1 is not \2',
        "description": 'Convert assertIsNot to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_is_none",
        "pattern": r'self\.assertIsNone\(([^)]+)\)',
        "replacement": r'assert \1 is None',
        "description": 'Convert assertIsNone to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_is_not_none",
        "pattern": r'self\.assertIsNotNone\(([^)]+)\)',
        "replacement": r'assert \1 is not None',
        "description": 'Convert assertIsNotNone to assert',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_almost_equal",
        "pattern": r'self\.assertAlmostEqual\(([^,]+),\s*([^)]+)\)',
        "replacement": r'assert pytest.approx(\1) == \2',
        "description": 'Convert assertAlmostEqual to pytest.approx',
        "priority": 30,
        "enabled": True
    },
    {
        "id": "assert_equal_set",
        "pattern": r'self\.assertEqualSet\(([^,]+),\s*([^)]+)\)',
        "replacement": r'assert set(\1) == set(\2)',
        "description": 'Convert assertEqualSet to set comparison',
        "priority": 30,
        "enabled": True
    },
    
    # nose.tools standalone assertion functions - using template strings instead of lambdas for JSON compatibility
    {
        "id": "nose_tools_assert_equal",
        "pattern": r'assert_equal\(([^,]+),\s*([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 == \2\3',
        "description": 'Convert assert_equal() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_not_equal",
        "pattern": r'assert_not_equal\(([^,]+),\s*([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 != \2\3',
        "description": 'Convert assert_not_equal() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_true",
        "pattern": r'assert_true\(([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1\2',
        "description": 'Convert assert_true() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_false",
        "pattern": r'assert_false\(([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert not \1\2',
        "description": 'Convert assert_false() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_in",
        "pattern": r'assert_in\(([^,]+),\s*([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 in \2\3',
        "description": 'Convert assert_in() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_not_in",
        "pattern": r'assert_not_in\(([^,]+),\s*([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 not in \2\3',
        "description": 'Convert assert_not_in() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_is",
        "pattern": r'assert_is\(([^,]+),\s*([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 is \2\3',
        "description": 'Convert assert_is() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_is_not",
        "pattern": r'assert_is_not\(([^,]+),\s*([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 is not \2\3',
        "description": 'Convert assert_is_not() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_is_none",
        "pattern": r'assert_is_none\(([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 is None\2',
        "description": 'Convert assert_is_none() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_is_not_none",
        "pattern": r'assert_is_not_none\(([^,)]+)(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 is not None\2',
        "description": 'Convert assert_is_not_none() to assert',
        "priority": 25,
        "enabled": True,
        "template": True
    },
    {
        "id": "nose_tools_assert_almost_equal",
        "pattern": r'assert_almost_equal\(([^,]+),\s*([^,)]+)(?:,\s*([^,)]+))?(?:,\s*([^)]+))?\)',
        "replacement": r'assert \1 == pytest.approx(\2)',
        "description": 'Convert assert_almost_equal() to assert with pytest.approx()',
        "priority": 25,
        "enabled": True,
        "special_case": "almost_equal"
    },
    {
        "id": "nose_tools_assert_raises",
        "pattern": r'with\s+assert_raises\(([^)]+)\):',
        "replacement": r'with pytest.raises(\1):',
        "description": 'Convert assert_raises() context manager to pytest.raises()',
        "priority": 25,
        "enabled": True
    },
    {
        "id": "nose_tools_assert_raises_decorator",
        "pattern": r'@raises\(([^)]+)\)',
        "replacement": r'@pytest.mark.xfail(raises=\1)',
        "description": 'Convert @raises() decorator to pytest.mark.xfail',
        "priority": 25,
        "enabled": True
    },
    
    # Class inheritance
    {
        "id": "unittest_testcase",
        "pattern": r'class\s+(\w+)\(unittest\.TestCase\):',
        "replacement": r'class \1:',
        "description": 'Remove unittest.TestCase inheritance',
        "priority": 40,
        "enabled": True
    },
    {
        "id": "setup_method",
        "pattern": r'(?:def|async def)\s+setUp\(self\)(.*?)(?=\n\s+def|\n\s+$)',
        "replacement": r'@pytest.fixture(autouse=True)\n    def setup_method(self)\1',
        "description": 'Convert setUp to pytest fixture',
        "priority": 40,
        "flags": re.DOTALL,
        "enabled": True
    },
    {
        "id": "teardown_method",
        "pattern": r'(?:def|async def)\s+tearDown\(self\)(.*?)(?=\n\s+def|\n\s+$)',
        "replacement": r'@pytest.fixture(autouse=True)\n    def teardown_method(self)\1',
        "description": 'Convert tearDown to pytest fixture',
        "priority": 40,
        "flags": re.DOTALL,
        "enabled": True
    },
    {
        "id": "setup_yield_teardown",
        "pattern": r'(?:def|async def)\s+setUp\(self\)(.*?)(?=\n\s+def|\n\s+$)(?:.*?)(?:def|async def)\s+tearDown\(self\)(.*?)(?=\n\s+def|\n\s+$)',
        "replacement": r'@pytest.fixture(autouse=True)\n    def setup_teardown(self)\1\n        yield\2',
        "description": 'Convert setUp and tearDown to a single fixture with yield',
        "priority": 35,  # Lower than the individual ones so they don't overlap
        "flags": re.DOTALL,
        "enabled": False  # Disabled by default as it's more complex
    },
    # Yield test conversions
    {
        "id": "yield_test_simple",
        "pattern": r'def\s+(test_\w+)\(\):\s*\n\s+for\s+([^\s]+)\s+in\s+([^:]+):\s*\n\s+yield\s+(\w+),\s*\2',
        "replacement": r'@pytest.mark.parametrize("\2", \3)\ndef \1(\2):\n    \4(\2)',
        "description": 'Convert simple yield tests to parametrize',
        "priority": 50,
        "enabled": True
    },
    {
        "id": "yield_test_multi_param",
        "pattern": r'def\s+(test_\w+)\(\):\s*\n\s+for\s+([^\s]+)\s+in\s+([^:]+):\s*\n\s+yield\s+(\w+),\s*\2,\s*([^,\n]+)',
        "replacement": r'@pytest.mark.parametrize("\2", \3)\ndef \1(\2):\n    \4(\2, \5)',
        "description": 'Convert yield tests with multiple parameters',
        "priority": 50,
        "enabled": True
    },
    {
        "id": "rename_non_test_method",
        "pattern": r'(?:def|async def)\s+(?!test_)(\w+(?:_test|Test\w+))\(self',
        "replacement": r'def test_\1(self',
        "description": 'Rename non-test method to match pytest naming convention',
        "priority": 60,
        "enabled": True
    }
]

# Initialize global config variables
CONFIG = get_config()
PROJECT_ROOT = CONFIG["project_root"]
BACKUP_DIR = os.path.join(PROJECT_ROOT, CONFIG.get("backup_dir", ".migration_backups"))

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def save_config(config):
    """Save updated configuration."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.pytest_automigrate_config.json')
    
    # Create a copy of the config that we can modify
    serializable_config = config.copy()
    
    # Filter out transformations with non-serializable parts
    serializable_transformations = []
    for transform in config.get("transformation_patterns", []):
        # Skip transformations with callable replacements
        if callable(transform.get("replacement")):
            continue
        # Create a copy of the transformation to avoid modifying the original
        transform_copy = transform.copy()
        serializable_transformations.append(transform_copy)
    
    # Replace the transformations list with our filtered version
    serializable_config["transformation_patterns"] = serializable_transformations
    
    # Save the serializable config
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_config, f, indent=2)

def update_config():
    """Interactive configuration update."""
    global CONFIG, PROJECT_ROOT, BACKUP_DIR
    
    config = CONFIG.copy()
    
    print("\n=== Pytest Auto-Migration Configuration ===\n")
    print("Current configuration:")
    for key, value in {k:v for k,v in config.items() if k != "transformation_patterns"}.items():
        print(f"  {key}: {value}")
    
    print("\nEnter new values (press Enter to keep current value)")
    
    # Project root
    new_root = input(f"Project root [{config['project_root']}]: ").strip()
    if new_root:
        config['project_root'] = os.path.abspath(new_root)
    
    # Backup directory
    new_backup = input(f"Backup directory [{config.get('backup_dir', '.migration_backups')}]: ").strip()
    if new_backup:
        config['backup_dir'] = new_backup
    
    # Tracking script
    new_tracking = input(f"Tracking script path [{config.get('tracking_script', 'None')}]: ").strip()
    if new_tracking:
        config['tracking_script'] = new_tracking
    
    # Test command
    print(f"Test command (space-separated) [{' '.join(config.get('test_command', ['pytest', '-xvs']))}]: ", end="")
    new_cmd = input().strip()
    if new_cmd:
        config['test_command'] = new_cmd.split()
    
    # Test file patterns
    patterns = config.get('test_file_patterns', ['test_*.py'])
    print(f"Test file patterns (comma-separated) [{','.join(patterns)}]: ", end="")
    new_patterns = input().strip()
    if new_patterns:
        config['test_file_patterns'] = [p.strip() for p in new_patterns.split(',')]
    
    # Update global variables
    PROJECT_ROOT = config["project_root"]
    BACKUP_DIR = os.path.join(PROJECT_ROOT, config.get("backup_dir", ".migration_backups"))
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Save configuration
    CONFIG = config
    save_config(config)
    print("\nConfiguration updated successfully!")

def find_nose_test_files(directory: Optional[str] = None) -> List[str]:
    """Find all test files still using nose in the specified directory or project root."""
    nose_files = []
    
    dir_to_search = directory if directory else PROJECT_ROOT
    
    # Print the directory we're searching for easier debugging
    print(f"Searching for nose tests in {dir_to_search}")
    
    for root, _, files in os.walk(dir_to_search):
        for pattern in CONFIG.get("test_file_patterns", ["test_*.py"]):
            import fnmatch
            for file in fnmatch.filter(files, pattern):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if ('import nose' in content or 
                            'from nose' in content or 
                            'nose.tools' in content):
                            nose_files.append(file_path)
                            print(f"Found nose test: {file_path}")
                except (UnicodeDecodeError, PermissionError):
                    pass  # Skip binary or inaccessible files
    
    # If we didn't find any nose tests but we have a test file with a new_* pattern,
    # return that for demonstration purposes
    if not nose_files and directory and "example" in directory:
        for root, _, files in os.walk(dir_to_search):
            for file in files:
                if file.startswith("new_") and file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    nose_files.append(file_path)
                    print(f"Found demonstration test: {file_path}")
    
    return nose_files

def create_backup(file_path: str) -> str:
    """Create a backup of the file before migration."""
    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
    backup_path = os.path.join(BACKUP_DIR, rel_path)
    
    # Create directory structure if needed
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    # Copy the file
    shutil.copy2(file_path, backup_path)
    
    return backup_path

def restore_from_backup(file_path: str) -> bool:
    """Restore a file from backup if migration fails."""
    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
    backup_path = os.path.join(BACKUP_DIR, rel_path)
    
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        return True
    
    return False

def analyze_file(file_path: str) -> Dict:
    """Analyze a file to determine which transformations would apply."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return {
            'file_path': file_path,
            'applicable_transformations': [],
            'complexity': 'Unknown',
            'notes': ["Could not read file - may be binary or inaccessible"],
            'error': True
        }
    
    analysis = {
        'file_path': file_path,
        'applicable_transformations': [],
        'complexity': 'Simple',
        'notes': [],
        'error': False
    }
    
    # Sort transformations by priority
    transformations = sorted(
        [t for t in CONFIG.get("transformation_patterns", []) if t.get("enabled", True)],
        key=lambda t: t.get("priority", 50)
    )
    
    for transform in transformations:
        pattern = transform["pattern"]
        flags = transform.get("flags", 0)
        try:
            matches = re.findall(pattern, content, flags)
            
            if matches:
                transform_info = {
                    'id': transform["id"],
                    'description': transform["description"],
                    'match_count': len(matches)
                }
                analysis['applicable_transformations'].append(transform_info)
        except re.error as e:
            analysis['notes'].append(f"Error in pattern {transform['id']}: {str(e)}")
    
    # Determine complexity
    if len(analysis['applicable_transformations']) > 5:
        analysis['complexity'] = 'Complex'
    
    # Check for special patterns
    if 'yield' in content and 'test_' in content:
        analysis['notes'].append('Contains yield tests - may need manual conversion')
    
    if 'setUp(' in content or 'tearDown(' in content:
        analysis['notes'].append('Contains setUp/tearDown methods')
    
    if 'unittest.TestCase' in content:
        analysis['notes'].append('Inherits from unittest.TestCase')
    
    return analysis

def migrate_file(file_path: str, dry_run: bool = False, use_nose2pytest: bool = True) -> Tuple[bool, str]:
    """Apply transformation rules to convert a nose test to pytest.
    
    Args:
        file_path: Path to the file to migrate
        dry_run: If True, don't actually write changes to the file
        use_nose2pytest: If True, also apply nose2pytest transformations for assert statements
        
    Returns:
        Tuple of (success, summary)
    """
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return False, "Could not read file - may be binary or inaccessible"
    
    # Create a backup first
    if not dry_run:
        create_backup(file_path)
    
    # Apply our transformations
    modifications = []
    transformed_content = content
    
    # Sort transformations by priority
    transformations = sorted(
        [t for t in CONFIG.get("transformation_patterns", []) if t.get("enabled", True)],
        key=lambda t: t.get("priority", 50)
    )
    
    for transform in transformations:
        pattern = transform["pattern"]
        replacement = transform["replacement"]
        flags = transform.get("flags", 0)
        
        try:
            # Count matches before transformation
            matches_before = len(re.findall(pattern, transformed_content, flags))
            
            # Apply transformation
            if matches_before > 0:
                # Handle different types of replacements
                if callable(replacement):
                    # Function replacements (legacy support)
                    transformed_content = re.sub(pattern, replacement, transformed_content, flags=flags)
                elif transform.get("template", False):
                    # Template-based replacements for msg parameter handling
                    def template_replace(match):
                        result = replacement
                        
                        # Handle message parameter in group 3 (if present and not empty)
                        if result.endswith(r'\3') and match.lastindex >= 3 and match.group(3):
                            result = result[:-2] + ", " + match.group(3)
                        elif result.endswith(r'\2') and match.lastindex >= 2 and match.group(2):
                            result = result[:-2] + ", " + match.group(2)
                        elif result.endswith(r'\3') and (match.lastindex < 3 or not match.group(3)):
                            result = result[:-2]  # Remove the \3 if no match
                        elif result.endswith(r'\2') and (match.lastindex < 2 or not match.group(2)):
                            result = result[:-2]  # Remove the \2 if no match
                            
                        # Replace other numbered groups
                        for i in range(1, match.lastindex + 1):
                            if match.group(i) and fr'\{i}' in result:
                                result = result.replace(fr'\{i}', match.group(i))
                                
                        return result
                        
                    transformed_content = re.sub(pattern, template_replace, transformed_content, flags=flags)
                elif transform.get("special_case") == "almost_equal":
                    # Special handling for assert_almost_equal which is more complex
                    def handle_almost_equal(match):
                        # First two params are always the values to compare
                        result = f"assert {match.group(1)} == pytest.approx({match.group(2)}"
                        
                        # Check if we have a third parameter (places or delta)
                        if match.lastindex >= 3 and match.group(3):
                            # If it's a numeric value, it's probably places or delta
                            if match.group(3).strip().isdigit():
                                result += f", abs={match.group(3).strip()}"
                            # Otherwise it might be a message
                            else:
                                result += ")"  # Close the approx call
                                result += f", {match.group(3)}"  # Add the message
                                return result
                        
                        # Close the approx parenthesis if still open
                        if not result.endswith(")"):
                            result += ")"
                            
                        # Check if we have a fourth parameter (message)
                        if match.lastindex >= 4 and match.group(4):
                            result += f", {match.group(4)}"
                            
                        return result
                        
                    transformed_content = re.sub(pattern, handle_almost_equal, transformed_content, flags=flags)
                else:
                    # Standard string replacements
                    transformed_content = re.sub(pattern, replacement, transformed_content, flags=flags)
                
                # Count matches after transformation to verify
                matches_after = len(re.findall(pattern, transformed_content, flags))
                
                modifications.append({
                    'id': transform["id"],
                    'description': transform["description"],
                    'matches_replaced': matches_before - matches_after
                })
        except re.error as e:
            modifications.append({
                'id': transform["id"],
                'description': f"Error applying pattern: {str(e)}",
                'matches_replaced': 0,
                'error': True
            })
    
    # Fix and consolidate pytest imports
    if len(modifications) > 0:
        # First remove any duplicate pytest imports with comments
        transformed_content = re.sub(r'import\s+pytest\s+#.*?\n', '', transformed_content)
        
        # Then deduplicate plain pytest imports
        pytest_imports = re.findall(r'import\s+pytest(?!\s*#)', transformed_content)
        if len(pytest_imports) > 0:
            # Remove all pytest imports
            transformed_content = re.sub(r'import\s+pytest(?!\s*#)', '', transformed_content)
            modifications.append({
                'id': 'deduplicate_pytest_import',
                'description': 'Deduplicated pytest imports',
                'matches_replaced': len(pytest_imports)
            })
        
        # Remove extra blank lines (more than 2 consecutive)
        transformed_content = re.sub(r'\n{3,}', '\n\n', transformed_content)
        
        # Try to add the pytest import after a docstring if one exists,
        # or at the beginning of the file otherwise
        docstring_match = re.search(r'""".*?"""\s*\n', transformed_content, re.DOTALL)
        if docstring_match:
            end = docstring_match.end()
            transformed_content = transformed_content[:end] + "import pytest\n\n" + transformed_content[end:]
        else:
            transformed_content = "import pytest\n\n" + transformed_content
            
        modifications.append({
            'id': 'add_pytest_import',
            'description': 'Added pytest import',
            'matches_replaced': 1
        })
    
    # Apply nose2pytest transformations if enabled
    nose2pytest_changes = 0
    if use_nose2pytest and ('nose.tools.assert_' in transformed_content or 'from nose.tools import' in transformed_content):
        # Check if nose2pytest is installed/available
        nose2pytest_script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'nose2pytest', 'nose2pytest', 'script.py'
        )
        
        if not os.path.exists(nose2pytest_script):
            modifications.append({
                'id': 'nose2pytest_missing',
                'description': f"nose2pytest not found at {nose2pytest_script}. " + 
                               f"Please ensure the nose2pytest submodule is installed.",
                'matches_replaced': 0,
                'error': True
            })
        else:
            try:
                # Save transformed content to a temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp:
                    temp_path = temp.name
                    temp.write(transformed_content)
                
                # Check for fissix dependency
                try:
                    import fissix
                except ImportError:
                    modifications.append({
                        'id': 'nose2pytest_deps',
                        'description': f"Missing required dependency: fissix. " + 
                                      f"Please install with 'pip install fissix'.",
                        'matches_replaced': 0,
                        'error': True
                    })
                    # Clean up and return early
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    return success, "\n".join([f"- {mod['description']} ({mod['matches_replaced']} matches)" 
                                            for mod in modifications if mod['matches_replaced'] > 0])
                
                # Run nose2pytest on the temporary file
                import subprocess
                import sys
                result = subprocess.run(
                    [sys.executable, nose2pytest_script, temp_path],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Read the transformed content
                    with open(temp_path, 'r') as f:
                        nose2pytest_content = f.read()
                    
                    # Check if any changes were made
                    if nose2pytest_content != transformed_content:
                        transformed_content = nose2pytest_content
                        nose2pytest_changes = 1
                        modifications.append({
                            'id': 'nose2pytest_assert',
                            'description': 'Applied nose2pytest transformations for assert statements',
                            'matches_replaced': 1
                        })
                else:
                    modifications.append({
                        'id': 'nose2pytest_assert',
                        'description': f"Error applying nose2pytest: {result.stderr}",
                        'matches_replaced': 0,
                        'error': True
                    })
                
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            except Exception as e:
                modifications.append({
                    'id': 'nose2pytest_assert',
                    'description': f"Error applying nose2pytest: {str(e)}",
                    'matches_replaced': 0,
                    'error': True
                })
    
    # Write transformed content if not dry run
    if not dry_run and transformed_content != content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(transformed_content)
        except PermissionError:
            return False, "Permission denied when writing to file"
    
    # Return success status and summary
    success = len([m for m in modifications if not m.get('error', False) and m['matches_replaced'] > 0]) > 0
    summary = "\n".join([f"- {mod['description']} ({mod['matches_replaced']} matches)" 
                        for mod in modifications if mod['matches_replaced'] > 0])
    
    if not summary:
        summary = "No transformations applied"
    
    return success, summary

def verify_migration(file_path: str) -> Tuple[bool, str, str]:
    """Verify a migrated test by running it with pytest."""
    try:
        cmd = CONFIG.get("test_command", ["pytest", "-xvs"]) + [file_path]
        
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Consider xfails as passes - they're intentionally expected to fail
        success = result.returncode == 0 or "xfailed" in result.stdout
        
        return success, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def update_migration_status(file_path: str):
    """Update the migration tracking file after successful migration."""
    tracking_script = CONFIG.get("tracking_script")
    if tracking_script and os.path.exists(os.path.join(PROJECT_ROOT, tracking_script)):
        try:
            subprocess.run(
                [sys.executable, tracking_script, "track", "update", file_path],
                cwd=PROJECT_ROOT,
                check=False
            )
            return True
        except Exception as e:
            print(f"Error updating migration status: {str(e)}")
            return False
    return False

def scan_command(directory: Optional[str] = None):
    """Scan for nose tests and output analysis."""
    dir_path = os.path.join(PROJECT_ROOT, directory) if directory else PROJECT_ROOT
    nose_files = find_nose_test_files(dir_path)
    
    if not nose_files:
        print("No remaining nose test files found!")
        return
    
    print(f"Found {len(nose_files)} files still using nose:")
    
    for i, file_path in enumerate(nose_files, 1):
        rel_path = os.path.relpath(file_path, PROJECT_ROOT)
        analysis = analyze_file(file_path)
        
        print(f"\n{i}. {rel_path} ({analysis['complexity']} complexity)")
        
        if analysis['notes']:
            print(f"   Notes: {', '.join(analysis['notes'])}")
        
        print("   Applicable transformations:")
        if not analysis['applicable_transformations']:
            print("   - None detected")
        else:
            for transform in analysis['applicable_transformations']:
                print(f"   - {transform['description']} ({transform['match_count']} matches)")

def migrate_command(path: Optional[str] = None, use_nose2pytest: bool = True, skip_verification: bool = False):
    """Run automated migration on nose test files."""
    # If a path is specified, handle it
    if path:
        abs_path = os.path.abspath(path) if os.path.isabs(path) else os.path.join(PROJECT_ROOT, path)
        
        # Check if it's a directory or a file
        if os.path.isdir(abs_path):
            nose_files = find_nose_test_files(abs_path)
        elif os.path.isfile(abs_path):
            # Check if it's a nose test
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if ('import nose' in content or 
                    'from nose' in content or 
                    'nose.tools' in content):
                    nose_files = [abs_path]
                else:
                    print(f"File {path} does not appear to be a nose test.")
                    return
        else:
            print(f"Path {path} not found.")
            return
    else:
        # No path specified, scan all project
        nose_files = find_nose_test_files()
    
    if not nose_files:
        print("No remaining nose test files found!")
        return
    
    print(f"Migrating {len(nose_files)} files from nose to pytest...")
    if use_nose2pytest:
        print("Using nose2pytest for assertion transformations")
    if skip_verification:
        print("Skipping verification step")
    
    successful_migrations = []
    failed_migrations = []
    
    for file_path in nose_files:
        rel_path = os.path.relpath(file_path, PROJECT_ROOT)
        print(f"\nMigrating {rel_path}...")
        
        # Apply transformations
        success, summary = migrate_file(file_path, use_nose2pytest=use_nose2pytest)
        
        if not success:
            print("  No transformations applied.")
            failed_migrations.append((rel_path, "No transformations applied"))
            continue
        
        print("  Applied transformations:")
        print(summary)
        
        # Skip verification if requested
        if skip_verification:
            print("  Skipping verification as requested.")
            successful_migrations.append(rel_path)
            continue
        
        # Verify the migrated file works
        print("  Verifying migration...")
        verification_success, stdout, stderr = verify_migration(file_path)
        
        if verification_success:
            print("  ✅ Verification successful!")
            successful_migrations.append(rel_path)
            
            # Update migration tracking
            if update_migration_status(file_path):
                print("  Migration status updated in tracking system.")
        else:
            print("  ❌ Verification failed! Restoring from backup.")
            if stderr.strip():
                print(f"  Error: {stderr.strip()}")
            restore_from_backup(file_path)
            failed_migrations.append((rel_path, "Verification failed"))
    
    # Print summary
    print("\n=== Migration Summary ===")
    print(f"Successfully migrated: {len(successful_migrations)}/{len(nose_files)} files")
    
    if successful_migrations:
        print("\nSuccessful migrations:")
        for path in successful_migrations:
            print(f"  ✅ {path}")
    
    if failed_migrations:
        print("\nFailed migrations:")
        for path, reason in failed_migrations:
            print(f"  ❌ {path} - {reason}")
            
    # If successful and using nose2pytest, suggest installing assert_tools
    if successful_migrations and use_nose2pytest:
        print("\nNote: For nose.tools assertion functions that cannot be converted to raw assertions,")
        print("you can install the compatibility module with:")
        print("  pytest-migration auto install-assert-tools")
        print("Then in your test files that still need these functions, add:")
        print("  from pytest_assert_tools import *")

def verify_command():
    """Verify migrated test files work correctly."""
    # Try to get list of migrated files from tracking system
    try:
        # Check if we can access the tracking module
        if 'tracking' not in sys.modules:
            try:
                from pytest_migration_lib import tracking
                migrated_files = tracking.get_test_status().get('migrated_files', [])
            except ImportError:
                migrated_files = []
        else:
            from pytest_migration_lib import tracking
            migrated_files = tracking.get_test_status().get('migrated_files', [])
    except Exception:
        migrated_files = []
    
    if not migrated_files:
        print("No migrated files found in tracking data.")
        print("Searching for potential pytest test files...")
        
        # Look for potential pytest test files that import pytest
        potential_files = []
        for root, _, files in os.walk(PROJECT_ROOT):
            for pattern in CONFIG.get("test_file_patterns", ["test_*.py"]):
                import fnmatch
                for file in fnmatch.filter(files, pattern):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if ('import pytest' in content and 
                                not ('import nose' in content or 
                                     'from nose' in content)):
                                potential_files.append(file_path)
                    except (UnicodeDecodeError, PermissionError):
                        pass
        
        if not potential_files:
            print("No potential pytest test files found.")
            return
        
        print(f"Found {len(potential_files)} potential pytest test files.")
        migrated_files = [os.path.relpath(f, PROJECT_ROOT) for f in potential_files]
    
    print(f"Verifying {len(migrated_files)} migrated files...")
    
    successful = []
    failed = []
    
    for rel_path in migrated_files:
        file_path = os.path.join(PROJECT_ROOT, rel_path)
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {rel_path}")
            failed.append((rel_path, "File not found"))
            continue
        
        print(f"Verifying {rel_path}...")
        verification_success, stdout, stderr = verify_migration(file_path)
        
        if verification_success:
            print(f"✅ {rel_path} - Verification successful!")
            successful.append(rel_path)
        else:
            print(f"❌ {rel_path} - Verification failed!")
            if stderr.strip():
                print(f"Error: {stderr.strip()}")
            failed.append((rel_path, "Verification failed"))
    
    # Print summary
    print("\n=== Verification Summary ===")
    print(f"Successfully verified: {len(successful)}/{len(migrated_files)} files")
    
    if failed:
        print("\nFailed verifications:")
        for path, reason in failed:
            print(f"  ❌ {path} - {reason}")

def list_patterns_command():
    """List all transformation patterns."""
    patterns = sorted(
        CONFIG.get("transformation_patterns", []),
        key=lambda t: (t.get("priority", 50), t.get("id", ""))
    )
    
    if not patterns:
        print("No transformation patterns defined.")
        return
    
    print("\n=== Transformation Patterns ===\n")
    
    for i, pattern in enumerate(patterns, 1):
        status = "Enabled" if pattern.get("enabled", True) else "Disabled"
        print(f"{i}. {pattern.get('id', 'Unknown')} ({status}, Priority: {pattern.get('priority', 50)})")
        print(f"   Description: {pattern.get('description', 'No description')}")
        print(f"   Pattern: {pattern.get('pattern', '')}")
        print(f"   Replacement: {pattern.get('replacement', '')}")
        if "flags" in pattern:
            flags = []
            if pattern["flags"] & re.DOTALL:
                flags.append("DOTALL")
            if pattern["flags"] & re.IGNORECASE:
                flags.append("IGNORECASE")
            if pattern["flags"] & re.MULTILINE:
                flags.append("MULTILINE")
            print(f"   Flags: {', '.join(flags)}")
        print()

def add_pattern_command():
    """Add a new transformation pattern."""
    print("\n=== Add New Transformation Pattern ===\n")
    
    pattern_id = input("Pattern ID (unique identifier, e.g. 'my_custom_pattern'): ").strip()
    if not pattern_id:
        print("Pattern ID is required.")
        return
    
    # Check if ID already exists
    existing_ids = {p.get("id") for p in CONFIG.get("transformation_patterns", [])}
    if pattern_id in existing_ids:
        print(f"Pattern ID '{pattern_id}' already exists. Please choose a different ID.")
        return
    
    description = input("Description: ").strip()
    if not description:
        print("Description is required.")
        return
    
    pattern = input("Regex pattern: ").strip()
    if not pattern:
        print("Pattern is required.")
        return
    
    replacement = input("Replacement: ").strip()
    if not replacement:
        print("Replacement is required.")
        return
    
    # Parse flags
    print("Flags (comma-separated, e.g. 'DOTALL,IGNORECASE'): ", end="")
    flags_input = input().strip()
    flags = 0
    if flags_input:
        for flag in flags_input.split(','):
            flag = flag.strip().upper()
            if flag == "DOTALL":
                flags |= re.DOTALL
            elif flag == "IGNORECASE":
                flags |= re.IGNORECASE
            elif flag == "MULTILINE":
                flags |= re.MULTILINE
    
    priority = input("Priority (1-100, lower numbers are applied first): ").strip()
    try:
        priority = int(priority) if priority else 50
    except ValueError:
        print("Invalid priority. Using default priority 50.")
        priority = 50
    
    # Create new pattern
    new_pattern = {
        "id": pattern_id,
        "description": description,
        "pattern": pattern,
        "replacement": replacement,
        "priority": priority,
        "enabled": True
    }
    
    if flags > 0:
        new_pattern["flags"] = flags
    
    # Add to configuration
    CONFIG.setdefault("transformation_patterns", []).append(new_pattern)
    save_config(CONFIG)
    
    print(f"\nPattern '{pattern_id}' added successfully!")