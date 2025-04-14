#!/usr/bin/env python
"""
Universal nose to pytest migration package.

This package provides tools for:
1. Tracking migration progress
2. Automatically converting nose tests to pytest
3. Managing and verifying the migration process

Usage:
  ./pytest_migration.py track init           # Initialize migration tracking 
  ./pytest_migration.py track status         # Show migration status
  ./pytest_migration.py track update <path>  # Mark a file as migrated
  ./pytest_migration.py run <path>           # Run tests with pytest
  
  ./pytest_migration.py auto scan            # Scan for nose tests
  ./pytest_migration.py auto migrate [path]  # Run automated migration
  ./pytest_migration.py auto verify          # Verify migrated tests
  ./pytest_migration.py auto config          # Configure settings
  ./pytest_migration.py auto patterns        # Show transformation patterns
  ./pytest_migration.py auto add-pattern     # Add a transformation pattern

Learn more: https://github.com/eric-downes/nosey_pytest

Copyright (c) 2025 eric-downes
Licensed under the MIT License (see LICENSE file for details)
"""

import os
import sys
import argparse
import importlib.util

# Detect if this is the first run or if modules are already available
modules_available = False
try:
    from pytest_migration_lib import tracking, automigrate
    modules_available = True
except ImportError:
    pass

def ensure_modules():
    """Ensure migration modules are available."""
    global modules_available
    
    # If modules are already imported, we're good
    if modules_available:
        return True
        
    # Check if modules are in the expected location
    module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pytest_migration_lib')
    
    if not os.path.isdir(module_dir):
        # Create the module directory
        os.makedirs(module_dir, exist_ok=True)
        
        # Create __init__.py
        with open(os.path.join(module_dir, '__init__.py'), 'w') as f:
            f.write('# Pytest migration library\n')
        
        print(f"Created module directory at {module_dir}")
        print("Please copy the migration modules to this directory.")
        return False
    
    # Check if tracking module exists
    tracking_path = os.path.join(module_dir, 'tracking.py')
    automigrate_path = os.path.join(module_dir, 'automigrate.py')
    
    if not os.path.exists(tracking_path) or not os.path.exists(automigrate_path):
        print("Migration modules not found in expected location.")
        print(f"Please copy migration modules to {module_dir}:")
        print(f"  - tracking.py (migration tracking module)")
        print(f"  - automigrate.py (automated migration module)")
        return False
    
    # Try to import the modules
    try:
        sys.path.insert(0, os.path.dirname(module_dir))
        from pytest_migration_lib import tracking, automigrate
        modules_available = True
        return True
    except ImportError as e:
        print(f"Error importing migration modules: {e}")
        return False

def track_command(args):
    """Handle tracking commands."""
    if not ensure_modules():
        return 1
        
    from pytest_migration_lib import tracking
    
    if args.subcommand == 'init':
        return tracking.initialize_migration()
    elif args.subcommand == 'status':
        tracking.display_status()
    elif args.subcommand == 'update':
        if not args.path:
            print("Error: Missing file path.")
            return 1
        abs_path = os.path.abspath(args.path) if os.path.isabs(args.path) else os.path.join(os.getcwd(), args.path)
        tracking.update_test_status(abs_path)
    elif args.subcommand == 'scan':
        dir_path = None
        if args.path:
            dir_path = os.path.abspath(args.path) if os.path.isabs(args.path) else os.path.join(os.getcwd(), args.path)
        tracking.rescan_tests(dir_path)
    else:
        print("Unknown track command.")
        return 1
    
    return 0

def run_command(args):
    """Handle run commands."""
    if not ensure_modules():
        return 1
        
    from pytest_migration_lib import tracking
    
    if not args.path:
        print("Error: Missing test path.")
        return 1
    
    return tracking.run_test(args.path)

def auto_command(args):
    """Handle auto commands."""
    if not ensure_modules():
        return 1
        
    from pytest_migration_lib import automigrate
    
    # Set use_nose2pytest flag
    use_nose2pytest = not getattr(args, 'no_nose2pytest', False)
    
    if args.subcommand == 'scan':
        automigrate.scan_command(args.path if hasattr(args, 'path') else None)
    elif args.subcommand == 'migrate':
        if hasattr(args, 'path'):
            automigrate.migrate_command(args.path, use_nose2pytest=use_nose2pytest)
        else:
            automigrate.migrate_command(None, use_nose2pytest=use_nose2pytest)
    elif args.subcommand == 'verify':
        automigrate.verify_command()
    elif args.subcommand == 'config':
        automigrate.update_config()
    elif args.subcommand == 'patterns':
        automigrate.list_patterns_command()
    elif args.subcommand == 'add-pattern':
        automigrate.add_pattern_command()
    elif args.subcommand == 'install-assert-tools':
        # Copy assert_tools.py to the current directory
        import shutil
        assert_tools_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'assert_tools.py')
        assert_tools_dest = os.path.join(os.getcwd(), 'pytest_assert_tools.py')
        shutil.copy2(assert_tools_src, assert_tools_dest)
        print(f"Installed pytest_assert_tools.py to {assert_tools_dest}")
        print("To use it, add this to your test modules that need nose.tools assert functions:")
        print("  from pytest_assert_tools import *")
    else:
        print("Unknown auto command.")
        return 1
    
    return 0

def main():
    """Main entry point for the migration tool."""
    parser = argparse.ArgumentParser(description="Universal nose to pytest migration toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Command group")
    
    # Track commands
    track_parser = subparsers.add_parser("track", help="Migration tracking commands")
    track_subparsers = track_parser.add_subparsers(dest="subcommand", help="Tracking command")
    
    init_parser = track_subparsers.add_parser("init", help="Initialize migration tracking")
    
    status_parser = track_subparsers.add_parser("status", help="Show migration status")
    
    update_parser = track_subparsers.add_parser("update", help="Mark a file as migrated")
    update_parser.add_argument("path", help="Path to migrated test file")
    
    scan_parser = track_subparsers.add_parser("scan", help="Scan for test files")
    scan_parser.add_argument("path", nargs="?", help="Directory to scan (optional)")
    
    # Run commands
    run_parser = subparsers.add_parser("run", help="Run tests with pytest")
    run_parser.add_argument("path", help="Path to test file or directory")
    
    # Auto commands
    auto_parser = subparsers.add_parser("auto", help="Automated migration commands")
    auto_subparsers = auto_parser.add_subparsers(dest="subcommand", help="Automation command")
    
    auto_scan_parser = auto_subparsers.add_parser("scan", help="Scan for nose tests")
    auto_scan_parser.add_argument("path", nargs="?", help="Directory to scan (optional)")
    
    auto_migrate_parser = auto_subparsers.add_parser("migrate", help="Run automated migration")
    auto_migrate_parser.add_argument("path", nargs="?", help="Path to migrate (file or directory)")
    auto_migrate_parser.add_argument("--no-nose2pytest", action="store_true", 
                                     help="Disable using nose2pytest for assertion transformations")
    
    auto_verify_parser = auto_subparsers.add_parser("verify", help="Verify migrated tests")
    
    auto_config_parser = auto_subparsers.add_parser("config", help="Configure auto-migration settings")
    
    auto_patterns_parser = auto_subparsers.add_parser("patterns", help="List transformation patterns")
    
    auto_add_pattern_parser = auto_subparsers.add_parser("add-pattern", help="Add a new transformation pattern")
    
    auto_install_assert_tools_parser = auto_subparsers.add_parser(
        "install-assert-tools", 
        help="Install assert_tools.py for the remaining assert functions not converted by nose2pytest"
    )
    
    args = parser.parse_args()
    
    if args.command == "track":
        return track_command(args)
    elif args.command == "run":
        return run_command(args)
    elif args.command == "auto":
        return auto_command(args)
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())