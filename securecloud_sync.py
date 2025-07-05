#!/usr/bin/env python3
"""
SecureCloudFS Sync Client - Simplified sync client for end users
Author: Jozef Hernandez
Version: 1.0.0

Automatically syncs a local folder with SecureCloudFS service.
No backend setup required - just install and use!
"""

import os
import sys
import time
import argparse
from pathlib import Path
from scfs_sync import SecureCloudFS

# Production API endpoint - users don't need to configure this
API_BASE_URL = "https://web-production-916e9.up.railway.app/api"

def main():
    print("🔐 SecureCloudFS Sync Client v1.0.0")
    print("Automatic encrypted file synchronization")
    print("Web Dashboard: https://your-app.vercel.app")
    print()
    
    parser = argparse.ArgumentParser(description="SecureCloudFS Sync Client")
    parser.add_argument("--email", required=True, help="Your SecureCloudFS email")
    parser.add_argument("--password", required=True, help="Your SecureCloudFS password")
    parser.add_argument("--watch", required=True, help="Folder to watch and sync")
    parser.add_argument("--interval", type=int, default=5, help="Sync interval in seconds (default: 5)")
    
    args = parser.parse_args()
    
    # Validate folder
    watch_folder = Path(args.watch)
    if not watch_folder.exists():
        print(f"❌ Folder '{args.watch}' does not exist")
        return
    
    if not watch_folder.is_dir():
        print(f"❌ '{args.watch}' is not a directory")
        return
    
    print(f"📁 Watching folder: {watch_folder.absolute()}")
    print(f"👤 User: {args.email}")
    print(f"🔄 Sync interval: {args.interval} seconds")
    print(f"🌐 Service: {API_BASE_URL}")
    print()
    
    try:
        # Initialize SecureCloudFS with the production service
        scfs = SecureCloudFS(args.email, args.password, str(watch_folder))
        
        print("🔐 Authenticating with SecureCloudFS service...")
        
        # Test authentication by trying to list files
        try:
            files = scfs.list_user_files()
            print(f"✅ Authentication successful!")
            print(f"📊 Current files in cloud: {len(files)}")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("Please check your email and password.")
            return
        
        print("🚀 Starting automatic synchronization...")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        # Start monitoring
        scfs.start_monitoring()
        
        # Keep the script running
        while True:
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping synchronization...")
        print("Your files remain safely encrypted in the cloud.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
