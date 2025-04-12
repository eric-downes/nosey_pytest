#!/usr/bin/env python
"""
Examples of using nosey-pytest programmatically.
"""

import os
import sys
from src.automigrate import find_nose_test_files, migrate_file, verify_migration
from src.tracking import create_default_migration_data, update_test_status, display_status

def migrate_project_example(project_path):
    """Example of migrating a project."""
    print(f"Migrating project at {project_path}...")
    
    # Set project root for tracking
    os.environ["PROJECT_ROOT"] = project_path
    
    # Initialize migration tracking
    create_default_migration_data()
    
    # Find nose tests
    nose_files = find_nose_test_files(project_path)
    print(f"Found {len(nose_files)} nose test files.")
    
    # Migrate each file
    for file_path in nose_files:
        print(f"\nMigrating {os.path.relpath(file_path, project_path)}...")
        
        # Apply transformations
        success, summary = migrate_file(file_path)
        
        if not success:
            print("  No transformations applied.")
            continue
        
        print("  Applied transformations:")
        print(summary)
        
        # Verify migration
        verification_success, stdout, stderr = verify_migration(file_path)
        
        if verification_success:
            print("  ✅ Verification successful!")
            update_test_status(file_path)
        else:
            print("  ❌ Verification failed!")
            if stderr.strip():
                print(f"  Error: {stderr.strip()}")
    
    # Display final status
    display_status()

if __name__ == "__main__":
    # Use the example directory by default
    project_path = os.path.join(os.path.dirname(__file__), "example")
    
    # Allow specifying a different path
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        
    migrate_project_example(project_path)