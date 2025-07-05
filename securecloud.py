#!/usr/bin/env python3
"""
SecureCloudFS Client
===================
Secure encrypted file storage client

Download and run this single file to use SecureCloudFS.
No installation or setup required beyond Python dependencies.

Usage:
  python securecloud.py list --email your@email.com --password yourpass
  python securecloud.py upload --email your@email.com --password yourpass --file document.pdf
  python securecloud.py download --email your@email.com --password yourpass --file document.pdf --output ./document.pdf
  python securecloud.py sync --email your@email.com --password yourpass --folder /path/to/folder

Author: Jozef Hernandez
Website: https://secure-cloud-iof1dxs3d-jozefhdezs-projects.vercel.app/
"""

import os
import sys
import json
import time
import hashlib
import argparse
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

# Check and install dependencies
def check_dependencies():
    """Check if required packages are installed, install if missing"""
    required_packages = {
        'requests': 'requests>=2.28.0',
        'cryptography': 'cryptography>=41.0.0',
        'watchdog': 'watchdog>=3.0.0'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("🔧 Installing required dependencies...")
        import subprocess
        for package in missing_packages:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("✅ Dependencies installed successfully!\n")

# Check dependencies first
check_dependencies()

# Now import the packages
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration - Users don't need to change this
API_BASE_URL = "https://web-production-916e9.up.railway.app/api"
SUPABASE_URL = "https://fvnicaqyshvunwolriqn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ2bmljYXF5c2h2dW53b2xyaXFuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1OTg1MTUsImV4cCI6MjA2NzE3NDUxNX0.6zxPeWCF9P6bsG5hiWhJyUffEvmBAcDp_6hfaeheeec"

class SecureCloudClient:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.session = requests.Session()
        
        # Setup encryption
        self.password_bytes = password.encode()
        salt = hashlib.sha256(self.password_bytes).digest()[:16]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password_bytes))
        self.fernet = Fernet(key)
    
    def authenticate(self):
        """Authenticate with SecureCloudFS"""
        try:
            url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
            headers = {
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json"
            }
            data = {"email": self.email, "password": self.password}
            
            response = self.session.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                error = response.json().get("error_description", "Authentication failed")
                print(f"❌ {error}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def _api_request(self, method: str, endpoint: str, **kwargs):
        """Make API request with authentication headers"""
        headers = {
            'X-User-Email': self.email,
            'X-User-Password': self.password
        }
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
            
        url = f"{API_BASE_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        return response
    
    def list_files(self):
        """List user files"""
        if not self.authenticate():
            return []
        
        response = self._api_request('GET', '/files')
        
        if response.status_code == 200:
            return response.json().get('files', [])
        else:
            print(f"❌ Error listing files: {response.text}")
            return []
    
    def upload_file(self, file_path: str):
        """Upload and encrypt file"""
        if not self.authenticate():
            return False
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        print(f"🔒 Encrypting {os.path.basename(file_path)}...")
        
        # Read and encrypt file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        encrypted_data = self.fernet.encrypt(file_data)
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        print(f"☁️  Uploading {os.path.basename(file_path)}...")
        
        # Prepare multipart upload
        files = {
            'file': (os.path.basename(file_path), encrypted_data, 'application/octet-stream')
        }
        
        headers = {
            'X-User-Email': self.email,
            'X-User-Password': self.password
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/files/upload",
                files=files,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ File uploaded and encrypted successfully!")
                    return True
                else:
                    print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Upload failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def download_file(self, filename: str, output_path: str):
        """Download and decrypt file"""
        if not self.authenticate():
            return False
        
        files = self.list_files()
        target_file = None
        
        for file_data in files:
            if file_data['filename'] == filename:
                target_file = file_data
                break
        
        if not target_file:
            print(f"❌ File '{filename}' not found")
            return False
        
        print(f"📥 Downloading {filename}...")
        
        response = self._api_request('GET', f"/files/download/{target_file['id']}")
        
        if response.status_code == 200:
            print(f"🔓 Decrypting {filename}...")
            
            try:
                # Decrypt the file data
                decrypted_data = self.fernet.decrypt(response.content)
                
                # Save to output path
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(decrypted_data)
                
                print(f"✅ Downloaded to: {output_path}")
                return True
                
            except Exception as e:
                print(f"❌ Decryption failed: {e}")
                return False
        else:
            print(f"❌ Download failed: {response.text}")
            return False

class FolderSyncHandler(FileSystemEventHandler):
    def __init__(self, client: SecureCloudClient):
        self.client = client
    
    def on_created(self, event):
        if not event.is_directory:
            print(f"📁 New file detected: {event.src_path}")
            self.client.upload_file(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            print(f"📝 File modified: {event.src_path}")
            self.client.upload_file(event.src_path)

def sync_folder(client: SecureCloudClient, folder_path: str):
    """Sync folder continuously"""
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    print(f"👀 Watching folder: {folder_path}")
    print("🔄 Starting initial sync of existing files...")
    print("-" * 50)
    
    # Initial sync: upload all existing files
    def sync_existing_files(directory):
        """Recursively sync all existing files in directory"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip hidden files and system files
                if not os.path.basename(file).startswith('.'):
                    print(f"📄 Found existing file: {os.path.relpath(file_path, folder_path)}")
                    client.upload_file(file_path)
    
    # Perform initial sync
    sync_existing_files(folder_path)
    
    print("-" * 50)
    print("✅ Initial sync completed!")
    print("🔄 Now monitoring for changes. Press Ctrl+C to stop.")
    print("-" * 50)
    
    event_handler = FolderSyncHandler(client)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping sync...")
        observer.stop()
    observer.join()

def main():
    print("🔐 SecureCloudFS Client")
    print("======================")
    print("Secure encrypted file storage")
    print("Web App: https://secure-cloud-iof1dxs3d-jozefhdezs-projects.vercel.app/")
    print()
    
    parser = argparse.ArgumentParser(description='SecureCloudFS Client')
    
    # Add subcommands first
    subparsers = parser.add_subparsers(dest='command', help='Commands', required=True)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List your files')
    list_parser.add_argument('--email', required=True, help='Your SecureCloudFS email')
    list_parser.add_argument('--password', required=True, help='Your SecureCloudFS password')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a file')
    upload_parser.add_argument('--email', required=True, help='Your SecureCloudFS email')
    upload_parser.add_argument('--password', required=True, help='Your SecureCloudFS password')
    upload_parser.add_argument('--file', required=True, help='File to upload')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download a file')
    download_parser.add_argument('--email', required=True, help='Your SecureCloudFS email')
    download_parser.add_argument('--password', required=True, help='Your SecureCloudFS password')
    download_parser.add_argument('--file', required=True, help='Filename to download')
    download_parser.add_argument('--output', required=True, help='Output path')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync a folder automatically')
    sync_parser.add_argument('--email', required=True, help='Your SecureCloudFS email')
    sync_parser.add_argument('--password', required=True, help='Your SecureCloudFS password')
    sync_parser.add_argument('--folder', required=True, help='Folder to sync')
    
    args = parser.parse_args()
    
    client = SecureCloudClient(args.email, args.password)
    
    if args.command == 'list':
        files = client.list_files()
        if files:
            print(f"📁 Your files ({len(files)} total):")
            print("-" * 40)
            for file_data in files:
                print(f"📄 {file_data['filename']}")
                print(f"   Size: {file_data['size']} bytes")
                print(f"   Uploaded: {file_data['uploaded_at']}")
                print()
        else:
            print("📁 No files found. Upload some files first!")
    
    elif args.command == 'upload':
        client.upload_file(args.file)
    
    elif args.command == 'download':
        client.download_file(args.file, args.output)
    
    elif args.command == 'sync':
        sync_folder(client, args.folder)

if __name__ == "__main__":
    main()
