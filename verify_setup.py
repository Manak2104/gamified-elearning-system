#!/usr/bin/env python3
"""
Quick verification script for EduGamify setup
Tests that all required files exist and Python modules can be imported
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} - NOT FOUND")
        return False

def main():
    print("=" * 60)
    print("EduGamify Setup Verification")
    print("=" * 60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    all_good = True
    
    # Check backend files
    print("\n📂 Backend Files:")
    all_good &= check_file_exists(os.path.join(base_dir, 'backend', 'app.py'), 'Flask App')
    all_good &= check_file_exists(os.path.join(base_dir, 'backend', 'models.py'), 'Database Models')
    all_good &= check_file_exists(os.path.join(base_dir, 'backend', 'routes.py'), 'API Routes')
    all_good &= check_file_exists(os.path.join(base_dir, 'backend', 'requirements.txt'), 'Requirements')
    
    # Check database
    print("\n📂 Database Files:")
    all_good &= check_file_exists(os.path.join(base_dir, 'database', 'schema.sql'), 'Database Schema')
    
    # Check frontend files
    print("\n📂 Frontend Files:")
    all_good &= check_file_exists(os.path.join(base_dir, 'frontend', 'login.html'), 'Login Page')
    all_good &= check_file_exists(os.path.join(base_dir, 'frontend', 'register.html'), 'Registration Page')
    all_good &= check_file_exists(os.path.join(base_dir, 'frontend', 'forgot-password.html'), 'Password Reset')
    all_good &= check_file_exists(os.path.join(base_dir, 'frontend', 'student-dashboard.html'), 'Student Dashboard')
    all_good &= check_file_exists(os.path.join(base_dir, 'frontend', 'teacher-dashboard.html'), 'Teacher Dashboard')
    all_good &= check_file_exists(os.path.join(base_dir, 'frontend', 'admin-dashboard.html'), 'Admin Dashboard')
    
    # Check Python syntax
    print("\n🐍 Python Syntax Check:")
    try:
        import py_compile
        backend_path = os.path.join(base_dir, 'backend')
        
        py_compile.compile(os.path.join(backend_path, 'models.py'), doraise=True)
        print("✓ models.py syntax OK")
        
        py_compile.compile(os.path.join(backend_path, 'app.py'), doraise=True)
        print("✓ app.py syntax OK")
        
        py_compile.compile(os.path.join(backend_path, 'routes.py'), doraise=True)
        print("✓ routes.py syntax OK")
    except SyntaxError as e:
        print(f"✗ Syntax error found: {e}")
        all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✓ All checks passed! System is ready.")
        print("\nNext steps:")
        print("1. Install MySQL and create database: mysql -u root -p < database/schema.sql")
        print("2. Install dependencies: cd backend && pip install -r requirements.txt")
        print("3. Run application: cd backend && python app.py")
    else:
        print("✗ Some checks failed. Please review the output above.")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == '__main__':
    main()
