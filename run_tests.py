#!/usr/bin/env python
"""
Test runner script for the research platform project.
This script provides various options for running tests.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')

def run_command(command, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"
    
    # Ensure we're in the project directory
    os.chdir(project_root)
    
    # Available test commands
    commands = {
        "all": {
            "command": ["python", "-m", "pytest", "-v", "--tb=short"],
            "description": "Run all tests"
        },
        "unit": {
            "command": ["python", "-m", "pytest", "-v", "-m", "unit", "--tb=short"],
            "description": "Run unit tests only"
        },
        "api": {
            "command": ["python", "-m", "pytest", "-v", "-m", "api", "--tb=short"],
            "description": "Run API tests only"
        },
        "models": {
            "command": ["python", "-m", "pytest", "-v", "-m", "models", "--tb=short"],
            "description": "Run model tests only"
        },
        "services": {
            "command": ["python", "-m", "pytest", "-v", "services/tests.py", "--tb=short"],
            "description": "Run services app tests"
        },
        "accounts": {
            "command": ["python", "-m", "pytest", "-v", "accounts/tests.py", "--tb=short"],
            "description": "Run accounts app tests"
        },
        "training": {
            "command": ["python", "-m", "pytest", "-v", "training/tests.py", "--tb=short"],
            "description": "Run training app tests"
        },
        "content": {
            "command": ["python", "-m", "pytest", "-v", "content/tests.py", "--tb=short"],
            "description": "Run content app tests"
        },
        "coverage": {
            "command": ["python", "-m", "pytest", "--cov=.", "--cov-report=html", "--cov-report=term"],
            "description": "Run tests with coverage report"
        },
        "django": {
            "command": ["python", "manage.py", "test", "--verbosity=2"],
            "description": "Run tests using Django test runner"
        },
        "check": {
            "command": ["python", "manage.py", "check"],
            "description": "Run Django system checks"
        },
        "migrations": {
            "command": ["python", "manage.py", "makemigrations", "--check", "--dry-run"],
            "description": "Check for missing migrations"
        }
    }
    
    if test_type not in commands:
        print(f"Unknown test type: {test_type}")
        print("Available options:")
        for key, value in commands.items():
            print(f"  {key}: {value['description']}")
        sys.exit(1)
    
    # Run the selected command
    command_info = commands[test_type]
    success = run_command(command_info["command"], command_info["description"])
    
    if not success:
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("Tests completed successfully!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
