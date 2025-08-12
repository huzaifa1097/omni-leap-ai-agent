#!/usr/bin/env python3
"""
Check project structure to help with troubleshooting
Save as: E:\omni-leap-final\check_structure.py
"""

import os
from pathlib import Path

def print_directory_structure(path, max_depth=3, current_depth=0, prefix=""):
    """Print directory structure"""
    if current_depth > max_depth:
        return
    
    path = Path(path)
    if not path.exists():
        print(f"❌ Path does not exist: {path}")
        return
    
    items = []
    try:
        items = sorted(path.iterdir())
    except PermissionError:
        print(f"{prefix}❌ Permission denied")
        return
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "
        
        if item.name.startswith('.'):
            continue  # Skip hidden files/folders
        
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth:
            print_directory_structure(
                item, max_depth, current_depth + 1, prefix + next_prefix
            )

def check_critical_files():
    """Check for critical files"""
    print("🔍 Checking Critical Files...")
    
    critical_files = [
        "backend/main.py",
        "backend/app/__init__.py", 
        "backend/app/api/__init__.py",
        "backend/app/api/v1/__init__.py",
        "backend/app/api/v1/chat.py",
        "backend/app/core/__init__.py",
        "backend/app/core/crews/__init__.py", 
        "backend/app/core/crews/blog_crew.py",
        ".env",
        "venv/",
    ]
    
    for file_path in critical_files:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                print(f"✅ {file_path} ({size} bytes)")
            else:
                print(f"✅ {file_path} (directory)")
        else:
            print(f"❌ Missing: {file_path}")
    
    print()

def check_python_path():
    """Check Python path configuration"""
    print("🐍 Python Path Information...")
    import sys
    
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path entries:")
    for i, path in enumerate(sys.path[:5]):  # Show first 5 entries
        print(f"  {i}: {path}")
    if len(sys.path) > 5:
        print(f"  ... and {len(sys.path) - 5} more entries")
    print()

def main():
    print("📁 Project Structure Analysis")
    print("=" * 60)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    print()
    
    # Check Python environment
    check_python_path()
    
    # Check critical files
    check_critical_files()
    
    # Print directory structure
    print("📂 Directory Structure:")
    print("omni-leap-final/")
    print_directory_structure(current_dir, max_depth=4)
    
    print("\n" + "=" * 60)
    print("📋 Analysis Complete!")
    print("\nIf any critical files are missing, please:")
    print("1. Check your project structure")
    print("2. Ensure all __init__.py files exist")
    print("3. Verify blog_crew.py is in the correct location")

if __name__ == "__main__":
    main()