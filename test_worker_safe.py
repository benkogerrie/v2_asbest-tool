#!/usr/bin/env python3
"""
Safe local test for worker code without running actual worker.
This tests the code structure and imports without dependencies.
"""
import sys
import os

def test_worker_code_structure():
    """Test worker code structure and syntax."""
    print("🧪 Testing worker code structure...")
    
    try:
        # Test 1: Check if worker directory exists
        print("1. Checking worker directory...")
        if not os.path.exists("worker"):
            print("❌ Worker directory not found")
            return False
        print("✅ Worker directory exists")
        
        # Test 2: Check if required files exist
        print("2. Checking required files...")
        required_files = ["worker/__init__.py", "worker/run.py"]
        for file_path in required_files:
            if not os.path.exists(file_path):
                print(f"❌ Required file not found: {file_path}")
                return False
            print(f"✅ {file_path} exists")
        
        # Test 3: Check Python syntax
        print("3. Checking Python syntax...")
        import py_compile
        try:
            py_compile.compile("worker/run.py", doraise=True)
            print("✅ worker/run.py syntax is valid")
        except py_compile.PyCompileError as e:
            print(f"❌ Syntax error in worker/run.py: {e}")
            return False
        
        # Test 4: Check if we can read the file content
        print("4. Checking file content...")
        with open("worker/run.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "from rq import Worker, Queue, Connection" in content:
                print("✅ RQ imports found")
            else:
                print("❌ RQ imports not found")
                return False
            
            if "def wait_for_redis" in content:
                print("✅ Redis wait function found")
            else:
                print("❌ Redis wait function not found")
                return False
            
            if "worker.work(with_scheduler=True)" in content:
                print("✅ Worker start code found")
            else:
                print("❌ Worker start code not found")
                return False
        
        # Test 5: Check app imports structure
        print("5. Checking app imports structure...")
        app_files = [
            "app/__init__.py",
            "app/config.py", 
            "app/database.py",
            "app/queue/__init__.py",
            "app/queue/conn.py",
            "app/queue/jobs.py",
            "app/queue/pdf_generator.py",
            "app/services/__init__.py",
            "app/services/storage.py"
        ]
        
        missing_files = []
        for file_path in app_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing app files: {missing_files}")
            return False
        else:
            print("✅ All required app files exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_requirements():
    """Test if requirements.txt has necessary dependencies."""
    print("\n🧪 Testing requirements...")
    
    try:
        if not os.path.exists("requirements.txt"):
            print("❌ requirements.txt not found")
            return False
        
        with open("requirements.txt", "r") as f:
            content = f.read()
            
        required_deps = ["rq", "weasyprint", "jinja2", "boto3", "redis"]
        missing_deps = []
        
        for dep in required_deps:
            if dep not in content:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing dependencies: {missing_deps}")
            return False
        else:
            print("✅ All required dependencies found in requirements.txt")
            return True
            
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Safe Worker Code Test")
    print("=" * 50)
    
    # Run tests
    structure_ok = test_worker_code_structure()
    requirements_ok = test_requirements()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Code Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    print(f"Requirements: {'✅ PASS' if requirements_ok else '❌ FAIL'}")
    
    if structure_ok and requirements_ok:
        print("\n🎉 All tests PASSED!")
        print("✅ Worker code structure looks correct")
        print("✅ All dependencies are listed")
        print("✅ The issue is likely in Railway deployment or environment variables")
    else:
        print("\n💥 Some tests FAILED!")
        print("❌ There are issues with the worker code structure")
    
    sys.exit(0 if (structure_ok and requirements_ok) else 1)
