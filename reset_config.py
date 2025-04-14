"""
Script to reset the configuration file.
"""

import os
import json

def reset_config():
    """Reset the configuration file to default settings."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.pytest_automigrate_config.json')
    
    # Create empty config
    config = {
        "project_root": os.path.dirname(os.path.abspath(__file__)),
        "backup_dir": ".migration_backups",
        "tracking_script": None,
        "test_command": ["pytest", "-xvs"],
        "test_file_patterns": ["test_*.py", "*_test.py"],
        "initialized": False,
        "initialized_date": None,
        "git_integration": True,
        "git_branch": "pytest-migration",
        "transformation_patterns": []
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration reset successfully to: {config_path}")
    
if __name__ == "__main__":
    reset_config()