#!/usr/bin/env python
"""
Pytest Migration Tool Main Package

This package provides tools for migrating from nose to pytest.
It exposes the main functionality of the pytest_migration_lib package.
"""

import os
import sys
import argparse

try:
    from pytest_migration_lib import tracking, automigrate
except ImportError:
    # Add parent directory to path for development mode
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    try:
        from pytest_migration_lib import tracking, automigrate
    except ImportError:
        print("Error: Could not import pytest_migration_lib.")
        print("Make sure it's correctly installed.")
        sys.exit(1)

__version__ = "0.1.0"

def main():
    """Main entry point for the migration tool."""
    parser = argparse.ArgumentParser(description="Universal nose to pytest migration toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Command group")
    
    # Track commands
    track_parser = subparsers.add_parser("track", help="Migration tracking commands")
    track_subparsers = track_parser.add_subparsers(dest="subcommand", help="Tracking command")
    
    track_subparsers.add_parser("init", help="Initialize migration tracking")
    track_subparsers.add_parser("status", help="Show migration status")
    
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
    
    auto_subparsers.add_parser("verify", help="Verify migrated tests")
    auto_subparsers.add_parser("config", help="Configure auto-migration settings")
    auto_subparsers.add_parser("patterns", help="List transformation patterns")
    auto_subparsers.add_parser("add-pattern", help="Add a new transformation pattern")
    
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

def track_command(args):
    """Handle tracking commands."""
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
        if hasattr(args, 'path') and args.path:
            dir_path = os.path.abspath(args.path) if os.path.isabs(args.path) else os.path.join(os.getcwd(), args.path)
        tracking.rescan_tests(dir_path)
    else:
        print("Unknown track command.")
        return 1
    
    return 0

def run_command(args):
    """Handle run commands."""
    if not args.path:
        print("Error: Missing test path.")
        return 1
    
    return tracking.run_test(args.path)

def auto_command(args):
    """Handle auto commands."""
    if args.subcommand == 'scan':
        automigrate.scan_command(args.path if hasattr(args, 'path') else None)
    elif args.subcommand == 'migrate':
        automigrate.migrate_command(args.path if hasattr(args, 'path') else None)
    elif args.subcommand == 'verify':
        automigrate.verify_command()
    elif args.subcommand == 'config':
        automigrate.update_config()
    elif args.subcommand == 'patterns':
        automigrate.list_patterns_command()
    elif args.subcommand == 'add-pattern':
        automigrate.add_pattern_command()
    else:
        print("Unknown auto command.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())