#!/usr/bin/env python3
"""
Setup script for TruthLens: AI-Powered News Authenticator
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_model_files():
    """Check if model files exist"""
    required_files = ["model95.jb", "vectorizer95.jb"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing model files: {', '.join(missing_files)}")
        print("Please ensure these files are in the project directory.")
        return False
    else:
        print("✅ All model files found!")
        return True

def run_app():
    """Run the Streamlit app"""
    print("🚀 Starting TruthLens application...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Thanks for using TruthLens!")
    except Exception as e:
        print(f"❌ Error running app: {e}")

def main():
    print("🔍 TruthLens Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Install dependencies
    if not install_requirements():
        sys.exit(1)
    
    # Check model files
    if not check_model_files():
        print("\n📝 Note: You can still run the app, but predictions may not work without model files.")
        choice = input("Continue anyway? (y/n): ").lower().strip()
        if choice != 'y':
            sys.exit(1)
    
    print("\n🎉 Setup complete!")
    choice = input("Run the app now? (y/n): ").lower().strip()
    
    if choice == 'y':
        run_app()
    else:
        print("\n💡 To run the app later, use: streamlit run app.py")
        print("🌐 The app will be available at: http://localhost:8501")

if __name__ == "__main__":
    main()