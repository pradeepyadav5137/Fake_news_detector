#!/usr/bin/env python3
"""
Test script to verify TruthLens merge was successful
"""

import os
import sys

def test_imports():
    """Test if all required packages are available"""
    try:
        import streamlit
        import pandas
        import requests
        import joblib
        import sklearn
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_files():
    """Test if required files exist"""
    required_files = ['app.py', 'model95.jb', 'vectorizer95.jb']
    missing = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_app_structure():
    """Test if app.py has the required functions"""
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        required_functions = [
            'SAMPLE_ARTICLES',
            'render_sample_section',
            'render_input',
            'render_results',
            'main'
        ]
        
        missing = []
        for func in required_functions:
            if func not in content:
                missing.append(func)
        
        if missing:
            print(f"❌ Missing functions in app.py: {', '.join(missing)}")
            return False
        else:
            print("✅ All required functions found in app.py")
            return True
            
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_sample_functionality():
    """Test if sample articles are properly defined"""
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        if 'SAMPLE_ARTICLES = {' in content:
            # Count sample articles
            sample_count = content.count('"Real News') + content.count('"Fake News')
            if sample_count >= 4:
                print("✅ Sample articles properly defined")
                return True
            else:
                print(f"⚠️  Only {sample_count} sample articles found, expected 4")
                return False
        else:
            print("❌ SAMPLE_ARTICLES not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking samples: {e}")
        return False

def main():
    print("🔍 TruthLens Merge Verification")
    print("=" * 40)
    
    tests = [
        ("Package imports", test_imports),
        ("Required files", test_files), 
        ("App structure", test_app_structure),
        ("Sample functionality", test_sample_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your merge was successful.")
        print("💡 Run 'streamlit run app.py' to test the application")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("📋 Refer to the merge guide to fix missing components.")

if __name__ == "__main__":
    main()