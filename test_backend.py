#!/usr/bin/env python3
"""
Test script for SecureCloudFS backend
"""

import sys
import os

# Add current directory to path to import scfs_api
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🧪 Testing SecureCloudFS Backend")
    print("=" * 40)
    
    try:
        from scfs_api import app
        print("✅ Backend imported successfully")
        
        # Test the app in debug mode locally
        print("🚀 Starting test server on localhost:5000")
        print("   Health check: http://localhost:5000/api/health")
        print("   Debug info: http://localhost:5000/api/debug")
        print("   Press Ctrl+C to stop")
        
        app.run(host='127.0.0.1', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)
