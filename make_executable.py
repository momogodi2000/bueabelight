#!/usr/bin/env python
"""
Make scripts executable and create necessary directories
"""

import os
import stat
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    
    # Scripts to make executable
    scripts = [
        'dev_server.py',
        'setup.py',
        'build.sh',
        'run_tests.py',
        'make_executable.py'
    ]
    
    print("🔧 Making scripts executable...")
    
    for script in scripts:
        script_path = base_dir / script
        if script_path.exists():
            # Make executable
            current_mode = script_path.stat().st_mode
            script_path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print(f"✅ {script} is now executable")
        else:
            print(f"⚠️  {script} not found")
    
    # Create template directories
    template_dirs = [
        'templates',
        'backend/templates',
        'backend/templates/backend',
        'backend/templates/backend/admin',
        'backend/templates/backend/admin/products',
        'backend/templates/backend/admin/orders',
        'backend/templates/backend/admin/categories',
        'backend/templates/backend/admin/messages',
        'backend/templates/backend/admin/catering',
    ]
    
    print("\n📁 Creating template directories...")
    
    for template_dir in template_dirs:
        dir_path = base_dir / template_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {template_dir}")
    
    # Create other necessary directories
    other_dirs = [
        'static/css',
        'static/js',
        'static/images',
        'backend/static/backend/css',
        'backend/static/backend/js',
        'backend/static/backend/images',
        'media',
        'logs',
        'staticfiles',
        'backend/management',
        'backend/management/commands'
    ]
    
    print("\n📂 Creating other directories...")
    
    for other_dir in other_dirs:
        dir_path = base_dir / other_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {other_dir}")
    
    # Create __init__.py files
    init_files = [
        'backend/management/__init__.py',
        'backend/management/commands/__init__.py'
    ]
    
    print("\n📄 Creating __init__.py files...")
    
    for init_file in init_files:
        init_path = base_dir / init_file
        if not init_path.exists():
            init_path.touch()
            print(f"✅ Created {init_file}")
    
    print("\n🎉 All scripts and directories are ready!")
    print("\n🚀 Next steps:")
    print("1. Run: python setup.py")
    print("2. Start development: python dev_server.py")
    print("3. Open browser: http://localhost:8000")

if __name__ == '__main__':
    main()