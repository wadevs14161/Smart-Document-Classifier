#!/usr/bin/env python3
"""
Run script for the Smart Document Classifier API
"""
import os
import sys
import subprocess

def main():
    """Start the FastAPI application"""
    print("🚀 Starting Smart Document Classifier API...")
    print("=" * 50)
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_root, ".venv-compuj", "bin", "python")
    
    # Check if virtual environment exists
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv .venv-compuj")
        print("Then activate it and install dependencies.")
        sys.exit(1)
    
    # Change to project directory
    os.chdir(project_root)
    
    # Start the server
    cmd = [
        venv_python, "-m", "uvicorn", 
        "backend.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    
    print("🌐 Server will be available at:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Web Interface: http://localhost:8000/interface")
    print("   • Health Check: http://localhost:8000/health")
    print("\n📋 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")

if __name__ == "__main__":
    main()
