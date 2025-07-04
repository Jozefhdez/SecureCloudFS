#!/usr/bin/env python3
"""
Configuration verification script for SecureCloudFS
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python {version.major}.{version.minor} (requires 3.8+)"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"

def check_dependencies():
    """Check installed dependencies"""
    required_packages = [
        'cryptography',
        'oci',
        'watchdog',
        'dotenv',
        'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        return False, f"Missing: {', '.join(missing)}"
    return True, "All dependencies installed"

def check_env_file():
    """Check .env file"""
    env_path = Path('.env')
    if not env_path.exists():
        return False, ".env file not found"
    
    load_dotenv()
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_API_KEY',
        'OCI_USER_OCID',
        'OCI_KEY_FILE',
        'OCI_FINGERPRINT',
        'OCI_TENANCY_OCID',
        'OCI_REGION',
        'OCI_NAMESPACE',
        'OCI_BUCKET_NAME'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        return False, f"Missing variables: {', '.join(missing)}"
    return True, "All environment variables configured"

def check_oci_key_file():
    """Check OCI key file"""
    key_file = os.getenv('OCI_KEY_FILE')
    if not key_file:
        return False, "OCI_KEY_FILE not configured"
    
    key_path = Path(key_file)
    if not key_path.exists():
        return False, f"Key file not found: {key_file}"
    
    # Check permissions
    stat = key_path.stat()
    if stat.st_mode & 0o077:
        return False, f"Incorrect permissions on {key_file} (should be 600)"
    
    return True, "OCI key file configured correctly"

def check_supabase_connection():
    """Check Supabase connection"""
    try:
        import requests
        
        url = os.getenv('SUPABASE_URL')
        api_key = os.getenv('SUPABASE_API_KEY')
        
        if not url or not api_key:
            return False, "Supabase credentials not configured"
        
        # Test connection
        headers = {'apikey': api_key}
        response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "Supabase connection successful"
        else:
            return False, f"Connection error: HTTP {response.status_code}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_oci_connection():
    """Check OCI connection"""
    try:
        import oci
        
        config = {
            "user": os.getenv("OCI_USER_OCID"),
            "key_file": os.getenv("OCI_KEY_FILE"),
            "fingerprint": os.getenv("OCI_FINGERPRINT"),
            "tenancy": os.getenv("OCI_TENANCY_OCID"),
            "region": os.getenv("OCI_REGION")
        }
        
        # Test client initialization
        client = oci.object_storage.ObjectStorageClient(config)
        
        # Test listing (without making real request)
        namespace = os.getenv("OCI_NAMESPACE")
        if not namespace:
            return False, "OCI_NAMESPACE not configured"
        
        return True, "OCI configuration valid"
    
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Main verification function"""
    print("Checking SecureCloudFS configuration...\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        (".env File", check_env_file),
        ("OCI Key", check_oci_key_file),
        ("Supabase Connection", check_supabase_connection),
        ("OCI Configuration", check_oci_connection)
    ]
    
    all_ok = True
    
    for name, check_func in checks:
        try:
            ok, message = check_func()
            status = "[OK]" if ok else "[ERROR]"
            print(f"{status} {name}: {message}")
            if not ok:
                all_ok = False
        except Exception as e:
            print(f"[ERROR] {name}: Unexpected error - {str(e)}")
            all_ok = False
    
    print("\n" + "="*50)
    
    if all_ok:
        print("Configuration complete and correct!")
        print("SecureCloudFS is ready to use")
        print("\nSuggested commands:")
        print("  python scfs_sync.py        # Run main application")
        print("  python scfs_cli.py --help  # View CLI commands")
    else:
        print("Configuration issues need to be resolved")
        print("Run ./setup.sh to install dependencies")
        sys.exit(1)

if __name__ == "__main__":
    main()
