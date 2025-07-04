#!/usr/bin/env python3
"""
SecureCloudFS CLI - Command line utilities
Author: Jozef Hernandez
"""

import os
import sys
import argparse
from pathlib import Path
from scfs_sync import SecureCloudFS, SecureCloudAuth

def list_files(email: str, password: str):
    """List user files"""
    try:
        scfs = SecureCloudFS(email, password, "/tmp")  # Temporary folder
        files = scfs.list_user_files()
        
        if not files:
            print("No synchronized files")
            return
        
        print(f"\nFiles for {email}:")
        print("-" * 60)
        for file_data in files:
            print(f"[FILE] {file_data['filename']}")
            print(f"   Path: {file_data['original_path']}")
            print(f"   Size: {file_data['size']} bytes")
            print(f"   Uploaded: {file_data['uploaded_at']}")
            print(f"   Hash: {file_data['hash_sha256'][:16]}...")
            print()
    
    except Exception as e:
        print(f"[ERROR] {e}")

def download_file(email: str, password: str, filename: str, output_path: str):
    """Download specific file"""
    try:
        scfs = SecureCloudFS(email, password, "/tmp")  # Temporary folder
        files = scfs.list_user_files()
        
        # Search file by name
        target_file = None
        for file_data in files:
            if file_data['filename'] == filename:
                target_file = file_data
                break
        
        if not target_file:
            print(f"[ERROR] File '{filename}' not found")
            return
        
        # Download file
        print(f"Downloading {filename}...")
        if scfs.download_file(target_file['oci_object_name'], output_path):
            print(f"[SUCCESS] File downloaded to: {output_path}")
        else:
            print("[ERROR] Error downloading file")
    
    except Exception as e:
        print(f"[ERROR] {e}")

def sync_folder(email: str, password: str, folder_path: str):
    """Synchronize specific folder"""
    try:
        print(f"Starting synchronization of: {folder_path}")
        scfs = SecureCloudFS(email, password, folder_path)
        scfs.sync_existing_files()
        print("[SUCCESS] Synchronization completed")
    
    except Exception as e:
        print(f"[ERROR] {e}")

def check_auth(email: str, password: str):
    """Verify credentials"""
    try:
        auth = SecureCloudAuth()
        access_token, refresh_token, user = auth.login(email, password)
        print("[SUCCESS] Valid credentials")
        print(f"User: {user['email']}")
        print(f"ID: {user['id']}")
    
    except Exception as e:
        print(f"[ERROR] Authentication error: {e}")

def main():
    parser = argparse.ArgumentParser(description="SecureCloudFS CLI")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--password", required=True, help="User password")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    subparsers.add_parser("list", help="List user files")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download file")
    download_parser.add_argument("filename", help="Name of file to download")
    download_parser.add_argument("output", help="Output path")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Synchronize folder")
    sync_parser.add_argument("folder", help="Path of folder to synchronize")
    
    # Auth command
    subparsers.add_parser("auth", help="Verify credentials")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        list_files(args.email, args.password)
    elif args.command == "download":
        download_file(args.email, args.password, args.filename, args.output)
    elif args.command == "sync":
        sync_folder(args.email, args.password, args.folder)
    elif args.command == "auth":
        check_auth(args.email, args.password)

if __name__ == "__main__":
    main()
