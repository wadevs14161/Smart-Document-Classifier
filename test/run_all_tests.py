#!/usr/bin/env python3
"""
Comprehensive test runner for Smart Document Classifier
Runs all test scripts and provides a summary report
"""
import subprocess
import sys
import os
from pathlib import Path
import time

def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print(f"\n🔄 Running {description}...")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, 
            f"test/{script_name}"
        ], capture_output=False, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def check_server_running():
    """Check if the server is running"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test runner"""
    print("🧪 Smart Document Classifier - Comprehensive Test Suite")
    print("=" * 70)
    print("This test suite will run all available tests for the application")
    
    # Check if server is running
    if not check_server_running():
        print("\n⚠️  WARNING: Server is not running!")
        print("Please start the server first: python run.py")
        print("Tests may fail without a running server.")
        
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Test run cancelled.")
            return
    else:
        print("\n✅ Server is running and accessible")
    
    # Define test scripts
    tests = [
        ("test_api.py", "API Endpoint Tests"),
        ("test_upload.py", "Upload Functionality Tests"),
        ("test_error_handling.py", "Error Handling Tests")
    ]
    
    # Run tests
    results = {}
    start_time = time.time()
    
    for script, description in tests:
        if os.path.exists(f"test/{script}"):
            success = run_test_script(script, description)
            results[description] = success
        else:
            print(f"⚠️  Skipping {description} - {script} not found")
            results[description] = None
    
    # Generate summary report
    total_time = time.time() - start_time
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY REPORT")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result is True)
    failed = sum(1 for result in results.values() if result is False)
    skipped = sum(1 for result in results.values() if result is None)
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"⏱️  Total Time: {total_time:.2f} seconds")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        print(f"  {status} - {test_name}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("💡 RECOMMENDATIONS")
    print("=" * 70)
    
    if failed > 0:
        print("❌ Some tests failed. Please review the output above and:")
        print("   - Check server configuration")
        print("   - Verify API endpoints are working")
        print("   - Check for dependency issues")
    elif passed == len([r for r in results.values() if r is not None]):
        print("✅ All tests passed! Your application is working correctly.")
        print("   - API endpoints are functioning properly")
        print("   - Upload functionality is working")
        print("   - Error handling is robust")
    
    print("\n📚 For more testing:")
    print("   - Manual testing via web interface: http://localhost:3000")
    print("   - API documentation: http://localhost:8000/docs")
    print("   - Individual test scripts can be run separately")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
