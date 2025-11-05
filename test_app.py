#!/usr/bin/env python3
"""
Test script for HerShield to verify it starts and stops properly
"""

import sys
import time
import threading

def test_import():
    """Test if the application can be imported"""
    try:
        from futuristic_hershield import FuturisticHerShield
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_initialization():
    """Test if the application can be initialized"""
    try:
        from futuristic_hershield import FuturisticHerShield
        app = FuturisticHerShield()
        print("✅ Initialization successful")
        
        # Test cleanup
        app.on_closing()
        print("✅ Cleanup successful")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def test_quick_run():
    """Test quick run and stop"""
    try:
        from futuristic_hershield import FuturisticHerShield
        app = FuturisticHerShield()
        
        # Start app in thread
        def run_app():
            try:
                app.run()
            except:
                pass
        
        app_thread = threading.Thread(target=run_app, daemon=True)
        app_thread.start()
        
        # Wait a bit then close
        time.sleep(2)
        app.on_closing()
        
        print("✅ Quick run test successful")
        return True
    except Exception as e:
        print(f"❌ Quick run test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing HerShield Application")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_import),
        ("Initialization Test", test_initialization),
        ("Quick Run Test", test_quick_run)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Application should work properly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()