#!/usr/bin/env python
"""
Nose to pytest migration tool.

This script clones a Git repository and automatically migrates nose tests to pytest.

Usage:
  ./migrate.py REPO_URL [TARGET_DIR]
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import git  # GitPython library

# Import local modules
try:
    from src.automigrate import find_nose_test_files, migrate_file, verify_migration
    from src.tracking import create_default_migration_data, update_test_status
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from src.automigrate import find_nose_test_files, migrate_file, verify_migration
    from src.tracking import create_default_migration_data, update_test_status

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Migrate nose tests to pytest')
    parser.add_argument('repo_url', help='Git repository URL to clone')
    parser.add_argument('target_dir', nargs='?', default=None, 
                        help='Target directory for the repository (optional)')
    return parser.parse_args()

def clone_repository(repo_url: str, target_dir: Optional[str] = None) -> str:
    """
    Clone a Git repository to the specified directory or a temporary directory.
    
    Args:
        repo_url: URL of the Git repository to clone
        target_dir: Target directory for the repository (optional)
        
    Returns:
        Path to the cloned repository
    """
    if target_dir:
        target_path = os.path.abspath(target_dir)
        if os.path.exists(target_path):
            print(f"Warning: Directory {target_path} already exists")
            response = input("Do you want to proceed and potentially overwrite files? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    else:
        target_path = tempfile.mkdtemp(prefix="nosey_pytest_")
    
    print(f"Cloning repository {repo_url} to {target_path}...")
    try:
        git.Repo.clone_from(repo_url, target_path)
        
        # Create a migration branch
        repo = git.Repo(target_path)
        migration_branch = "pytest-migration"
        
        # Check if the branch already exists
        if migration_branch in [b.name for b in repo.branches]:
            print(f"Branch {migration_branch} already exists. Using existing branch.")
            repo.git.checkout(migration_branch)
        else:
            print(f"Creating new branch {migration_branch} for migration...")
            repo.git.checkout('-b', migration_branch)
        
        return target_path
    except git.GitCommandError as e:
        print(f"Error cloning repository: {e}")
        if not target_dir:  # Clean up temp dir if we created it
            shutil.rmtree(target_path, ignore_errors=True)
        sys.exit(1)

def scan_repository(repo_path: str) -> List[str]:
    """
    Scan the repository for nose tests.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        List of nose test files
    """
    print(f"Scanning repository for nose tests...")
    nose_files = find_nose_test_files(repo_path)
    return nose_files

def migrate_tests(repo_path: str, nose_files: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Migrate nose tests to pytest.
    
    Args:
        repo_path: Path to the repository
        nose_files: List of nose test files
        
    Returns:
        Tuple of (successful_migrations, failed_migrations)
    """
    print(f"Migrating {len(nose_files)} nose tests to pytest...")
    
    successful_migrations = []
    failed_migrations = []
    
    for file_path in nose_files:
        rel_path = os.path.relpath(file_path, repo_path)
        print(f"\nMigrating {rel_path}...")
        
        # Apply transformations
        success, summary = migrate_file(file_path)
        
        if not success:
            print("  No transformations applied.")
            failed_migrations.append((rel_path, "No transformations applied"))
            continue
        
        print("  Applied transformations:")
        print(summary)
        
        # Verify the migrated file works
        print("  Verifying migration...")
        verification_success, stdout, stderr = verify_migration(file_path)
        
        if verification_success:
            print("  ✅ Verification successful!")
            successful_migrations.append(rel_path)
            
            # Update migration tracking
            update_test_status(file_path)
        else:
            print("  ❌ Verification failed!")
            if stderr.strip():
                print(f"  Error: {stderr.strip()}")
            failed_migrations.append((rel_path, "Verification failed"))
    
    return successful_migrations, failed_migrations

def generate_report(repo_path: str, successful: List[str], failed: List[Tuple[str, str]]) -> str:
    """
    Generate a migration report.
    
    Args:
        repo_path: Path to the repository
        successful: List of successfully migrated files
        failed: List of failed migrations with reasons
        
    Returns:
        Path to the generated report file
    """
    report_path = os.path.join(repo_path, "pytest_migration_report.md")
    
    with open(report_path, 'w') as f:
        f.write("# Nose to Pytest Migration Report\n\n")
        f.write(f"Generated on: {subprocess.check_output(['date']).decode().strip()}\n\n")
        
        # Summary
        total = len(successful) + len(failed)
        success_rate = (len(successful) / total) * 100 if total > 0 else 0
        
        f.write("## Summary\n\n")
        f.write(f"- Total test files scanned: {total}\n")
        f.write(f"- Successfully migrated: {len(successful)} ({success_rate:.1f}%)\n")
        f.write(f"- Failed migrations: {len(failed)}\n\n")
        
        # Successful migrations
        f.write("## Successfully Migrated Files\n\n")
        if successful:
            for path in successful:
                f.write(f"- ✅ {path}\n")
        else:
            f.write("No files were successfully migrated.\n")
        
        # Failed migrations
        f.write("\n## Failed Migrations\n\n")
        if failed:
            for path, reason in failed:
                f.write(f"- ❌ {path} - {reason}\n")
        else:
            f.write("No migration failures.\n")
        
        # Next steps
        f.write("\n## Next Steps\n\n")
        if failed:
            f.write("1. Manually review failed migration files\n")
            f.write("2. Consider addressing issues and re-running the migration tool\n")
        f.write("3. Run your test suite to ensure all migrated tests pass\n")
        f.write("4. Update your CI configuration to use pytest instead of nose\n")
        f.write("5. Remove nose from your dependencies\n")
    
    print(f"Generated migration report: {report_path}")
    return report_path

def commit_changes(repo_path: str, successful_migrations: List[str]) -> bool:
    """
    Commit the migrated files to the Git repository.
    
    Args:
        repo_path: Path to the repository
        successful_migrations: List of successfully migrated files
        
    Returns:
        True if commit was successful, False otherwise
    """
    if not successful_migrations:
        print("No successful migrations to commit.")
        return False
    
    try:
        repo = git.Repo(repo_path)
        
        # Check if there are changes to commit
        if not repo.is_dirty() and not repo.untracked_files:
            print("No changes to commit.")
            return False
        
        # Add all successfully migrated files
        for file_path in successful_migrations:
            abs_path = os.path.join(repo_path, file_path)
            repo.git.add(abs_path)
        
        # Add the migration report if it exists
        report_path = os.path.join(repo_path, "pytest_migration_report.md")
        if os.path.exists(report_path):
            repo.git.add(report_path)
        
        # Commit the changes
        commit_message = "Migrate nose tests to pytest\n\n"
        commit_message += f"Successfully migrated {len(successful_migrations)} tests:\n"
        
        # Add up to 10 files to the commit message
        for file_path in successful_migrations[:10]:
            commit_message += f"- {file_path}\n"
        
        if len(successful_migrations) > 10:
            commit_message += f"- and {len(successful_migrations) - 10} more files\n"
        
        repo.git.commit('-m', commit_message)
        
        print(f"Changes committed to branch {repo.active_branch.name}")
        return True
        
    except git.GitCommandError as e:
        print(f"Error committing changes: {e}")
        return False

def main():
    args = parse_args()
    
    # Clone the repository
    repo_path = clone_repository(args.repo_url, args.target_dir)
    
    # Scan for nose tests
    nose_files = scan_repository(repo_path)
    
    if not nose_files:
        print("No nose tests found in the repository.")
        return 0
    
    print(f"Found {len(nose_files)} nose test files.")
    
    # Create migration tracking
    os.environ["PROJECT_ROOT"] = repo_path
    migration_data = create_default_migration_data()
    
    # Migrate tests
    successful, failed = migrate_tests(repo_path, nose_files)
    
    # Generate report
    report_path = generate_report(repo_path, successful, failed)
    
    # Commit changes if there were successful migrations
    if successful:
        commit_result = commit_changes(repo_path, successful)
        if commit_result:
            print("Migration changes committed to Git repository.")
    
    # Show summary
    print("\n=== Migration Summary ===")
    print(f"Repository: {args.repo_url}")
    print(f"Local path: {repo_path}")
    print(f"Total test files: {len(nose_files)}")
    print(f"Successfully migrated: {len(successful)}")
    print(f"Failed migrations: {len(failed)}")
    print(f"Report: {report_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())