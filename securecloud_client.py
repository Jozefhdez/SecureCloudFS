#!/usr/bin/env python3
"""
SecureCloudFS Client - Simplified client for end users
Author: Jozef Hernandez
Version: 1.0.0

This client connects to the SecureCloudFS service for secure file storage.
No backend setup required - just install and use!
"""

import os
import sys
import argparse
import requests
import json
from pathlib import Path

# Production API endpoint - users don't need to configure this
API_BASE_URL = "https://web-production-916e9.up.railway.app/api"

class SecureCloudClient:
    def __init__(self):
        self.api_url = API_BASE_URL
        self.session = requests.Session()
    
    def authenticate(self, email: str, password: str):
        """Authenticate with SecureCloudFS service"""
        try:
            response = self.session.post(f"{self.api_url}/auth/login", 
                                       json={"email": email, "password": password})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully authenticated as {email}")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            print("Make sure you have internet connection.")
            return False
    
    def list_files(self, email: str, password: str):
        """List user files"""
        if not self.authenticate(email, password):
            return
        
        try:
            headers = {
                'X-User-Email': email,
                'X-User-Password': password
            }
            
            response = self.session.get(f"{self.api_url}/files", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                files = data.get('files', [])
                
                if not files:
                    print("📁 No files found")
                    return
                
                print(f"\n📁 Your files ({len(files)} total):")
                print("-" * 60)
                
                for file_data in files:
                    print(f"📄 {file_data['filename']}")
                    print(f"   Size: {file_data['size']} bytes")
                    print(f"   Uploaded: {file_data['uploaded_at']}")
                    print()
            else:
                print(f"❌ Error listing files: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
    
    def download_file(self, email: str, password: str, filename: str, output_path: str):
        """Download a specific file"""
        if not self.authenticate(email, password):
            return
        
        try:
            headers = {
                'X-User-Email': email,
                'X-User-Password': password
            }
            
            # First, get the file list to find the file ID
            response = self.session.get(f"{self.api_url}/files", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Error accessing files: {response.text}")
                return
            
            files = response.json().get('files', [])
            target_file = None
            
            for file_data in files:
                if file_data['filename'] == filename:
                    target_file = file_data
                    break
            
            if not target_file:
                print(f"❌ File '{filename}' not found")
                return
            
            # Download the file
            download_url = f"{self.api_url}/files/download/{target_file['id']}"
            response = self.session.get(download_url, headers=headers)
            
            if response.status_code == 200:
                output_dir = Path(output_path).parent
                output_dir.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Downloaded '{filename}' to '{output_path}'")
            else:
                print(f"❌ Error downloading file: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")

def main():
    print("🔐 SecureCloudFS Client v1.0.0")
    print("Secure encrypted file storage service")
    print("Web Dashboard: https://your-app.vercel.app")
    print()
    
    parser = argparse.ArgumentParser(description="SecureCloudFS Client")
    parser.add_argument("--email", required=True, help="Your SecureCloudFS email")
    parser.add_argument("--password", required=True, help="Your SecureCloudFS password")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List your files')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download a file')
    download_parser.add_argument('--file', required=True, help='Filename to download')
    download_parser.add_argument('--output', required=True, help='Output path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = SecureCloudClient()
    
    if args.command == 'list':
        client.list_files(args.email, args.password)
    elif args.command == 'download':
        client.download_file(args.email, args.password, args.file, args.output)

if __name__ == "__main__":
    main()
