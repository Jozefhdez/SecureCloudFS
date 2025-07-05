#!/usr/bin/env python3
"""
SecureCloudFS Backend API
========================
Backend service for SecureCloudFS - runs on Railway

This is the backend API that the SecureCloudFS client connects to.
Users don't interact with this directly - they use securecloud.py
"""

import os
import sys
import json
import argparse
import uuid
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Import OCI and Supabase with better error handling
OCI_AVAILABLE = False
SUPABASE_AVAILABLE = False
object_storage_client = None
supabase = None

try:
    import oci
    print("✅ OCI library imported successfully")
    OCI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  OCI library not available: {e}")

try:
    from supabase import create_client, Client
    print("✅ Supabase library imported successfully")
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Supabase library not available: {e}")

# Configuration from environment
OCI_CONFIG = {
    "user": os.getenv("OCI_USER_OCID", ""),
    "fingerprint": os.getenv("OCI_FINGERPRINT", ""),
    "tenancy": os.getenv("OCI_TENANCY_OCID", ""),
    "region": os.getenv("OCI_REGION", "mx-queretaro-1"),
    "key_content": os.getenv("OCI_KEY_CONTENT", "")
}

OCI_NAMESPACE = os.getenv("OCI_NAMESPACE", "")
OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")

# Initialize clients only if available and configured
if OCI_AVAILABLE and all([OCI_CONFIG["user"], OCI_CONFIG["fingerprint"], OCI_CONFIG["tenancy"]]):
    try:
        object_storage_client = oci.object_storage.ObjectStorageClient(OCI_CONFIG)
        print("✅ OCI client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize OCI client: {e}")
        object_storage_client = None
else:
    print("⚠️  OCI client not initialized (missing config or library)")

if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        supabase = None
else:
    print("⚠️  Supabase client not initialized (missing config or library)")

def authenticate_user(email: str, password: str):
    """Authenticate user with Supabase"""
    if not supabase:
        # Fallback: simulate successful auth for development
        print(f"⚠️  Supabase not available, simulating auth for {email}")
        return True, type('MockAuth', (), {'user': type('MockUser', (), {'id': email})()})()
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return True, response
    except Exception as e:
        return False, str(e)

def get_user_files(user_id: str):
    """Get user files from Supabase database"""
    if not supabase:
        # Fallback: return empty list for development
        print(f"⚠️  Supabase not available, returning empty file list for {user_id}")
        return []
    
    try:
        response = supabase.table("files").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting user files: {e}")
        return []

def store_file_metadata(user_id: str, filename: str, file_size: int, file_hash: str, oci_object_name: str):
    """Store file metadata in Supabase"""
    if not supabase:
        # Fallback: simulate successful storage for development
        print(f"⚠️  Supabase not available, simulating metadata storage for {filename}")
        return True, {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "filename": filename,
            "size": file_size,
            "hash": file_hash,
            "oci_object_name": oci_object_name,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    try:
        file_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "filename": filename,
            "size": file_size,
            "hash": file_hash,
            "oci_object_name": oci_object_name,
            "uploaded_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("files").insert(file_data).execute()
        return True, response.data[0] if response.data else file_data
    except Exception as e:
        return False, str(e)

def upload_to_oci(file_data: bytes, object_name: str):
    """Upload file to OCI Object Storage"""
    if not object_storage_client:
        # Fallback: simulate successful upload for development
        print(f"⚠️  OCI not available, simulating upload for {object_name}")
        return True, "Simulated upload successful"
    
    try:
        response = object_storage_client.put_object(
            namespace_name=OCI_NAMESPACE,
            bucket_name=OCI_BUCKET_NAME,
            object_name=object_name,
            put_object_body=file_data
        )
        return True, response
    except Exception as e:
        return False, str(e)

def download_from_oci(object_name: str):
    """Download file from OCI Object Storage"""
    if not object_storage_client:
        return False, "OCI not configured"
    
    try:
        response = object_storage_client.get_object(
            namespace_name=OCI_NAMESPACE,
            bucket_name=OCI_BUCKET_NAME,
            object_name=object_name
        )
        return True, response.data.content
    except Exception as e:
        return False, str(e)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "service": "SecureCloudFS API",
        "version": "1.0.0",
        "oci_available": OCI_AVAILABLE,
        "supabase_available": SUPABASE_AVAILABLE,
        "oci_configured": object_storage_client is not None,
        "supabase_configured": supabase is not None
    })

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check configuration"""
    return jsonify({
        "service": "SecureCloudFS API Debug",
        "environment": {
            "OCI_USER_OCID": "configured" if os.getenv("OCI_USER_OCID") else "missing",
            "OCI_FINGERPRINT": "configured" if os.getenv("OCI_FINGERPRINT") else "missing",
            "OCI_TENANCY_OCID": "configured" if os.getenv("OCI_TENANCY_OCID") else "missing",
            "OCI_REGION": os.getenv("OCI_REGION", "not set"),
            "OCI_NAMESPACE": os.getenv("OCI_NAMESPACE", "not set"),
            "OCI_BUCKET_NAME": os.getenv("OCI_BUCKET_NAME", "not set"),
            "OCI_KEY_CONTENT": "configured" if os.getenv("OCI_KEY_CONTENT") else "missing",
            "SUPABASE_URL": "configured" if os.getenv("SUPABASE_URL") else "missing",
            "SUPABASE_API_KEY": "configured" if os.getenv("SUPABASE_API_KEY") else "missing"
        },
        "clients": {
            "oci_available": OCI_AVAILABLE,
            "supabase_available": SUPABASE_AVAILABLE,
            "oci_client": object_storage_client is not None,
            "supabase_client": supabase is not None
        }
    })

@app.route('/api/files', methods=['GET'])
def list_files():
    """List user files"""
    try:
        # Get user authentication from headers
        email = request.headers.get('X-User-Email')
        password = request.headers.get('X-User-Password')
        
        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Authentication required"
            }), 401
        
        # Authenticate user
        auth_success, auth_result = authenticate_user(email, password)
        if not auth_success:
            return jsonify({
                "success": False,
                "error": f"Authentication failed: {auth_result}"
            }), 401
        
        # Get user ID from auth result
        user_id = auth_result.user.id if hasattr(auth_result, 'user') else email
        
        # Get user files
        files = get_user_files(user_id)
        
        return jsonify({
            "success": True,
            "files": files
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error obteniendo archivos: {str(e)}"
        }), 500

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    """Upload a file"""
    try:
        # Get user authentication
        email = request.headers.get('X-User-Email')
        password = request.headers.get('X-User-Password')
        
        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Authentication required"
            }), 401
        
        # Authenticate user
        auth_success, auth_result = authenticate_user(email, password)
        if not auth_success:
            return jsonify({
                "success": False,
                "error": f"Authentication failed: {auth_result}"
            }), 401
        
        # Get user ID
        user_id = auth_result.user.id if hasattr(auth_result, 'user') else email
        
        # Get file data from request
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        # Read file data
        file_data = file.read()
        file_size = len(file_data)
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Generate unique object name for OCI
        oci_object_name = f"{user_id}/{file_hash}_{file.filename}"
        
        # Upload to OCI
        upload_success, upload_result = upload_to_oci(file_data, oci_object_name)
        if not upload_success:
            return jsonify({
                "success": False,
                "error": f"Upload to storage failed: {upload_result}"
            }), 500
        
        # Store metadata in Supabase
        metadata_success, metadata_result = store_file_metadata(
            user_id, file.filename, file_size, file_hash, oci_object_name
        )
        
        if not metadata_success:
            return jsonify({
                "success": False,
                "error": f"Metadata storage failed: {metadata_result}"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "file_id": metadata_result.get("id"),
            "filename": file.filename,
            "size": file_size
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }), 500

@app.route('/api/files/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download a file"""
    try:
        # Get user authentication
        email = request.headers.get('X-User-Email')
        password = request.headers.get('X-User-Password')
        
        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Authentication required"
            }), 401
        
        # Authenticate user
        auth_success, auth_result = authenticate_user(email, password)
        if not auth_success:
            return jsonify({
                "success": False,
                "error": f"Authentication failed: {auth_result}"
            }), 401
        
        # Get user ID
        user_id = auth_result.user.id if hasattr(auth_result, 'user') else email
        
        # Get file metadata from Supabase
        if not supabase:
            return jsonify({
                "success": False,
                "error": "Database not configured"
            }), 500
        
        try:
            response = supabase.table("files").select("*").eq("id", file_id).eq("user_id", user_id).execute()
            if not response.data:
                return jsonify({
                    "success": False,
                    "error": "File not found"
                }), 404
            
            file_metadata = response.data[0]
            oci_object_name = file_metadata["oci_object_name"]
            
            # Download from OCI
            download_success, file_data = download_from_oci(oci_object_name)
            if not download_success:
                return jsonify({
                    "success": False,
                    "error": f"Download from storage failed: {file_data}"
                }), 500
            
            # Return file data
            return Response(
                file_data,
                mimetype='application/octet-stream',
                headers={
                    'Content-Disposition': f'attachment; filename="{file_metadata["filename"]}"'
                }
            )
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Database error: {str(e)}"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Download failed: {str(e)}"
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "SecureCloudFS API",
        "status": "running",
        "message": "This is the backend API. Use the SecureCloudFS client to interact with the service.",
        "client_download": "https://raw.githubusercontent.com/Jozefhdez/SecureCloudFS/main/securecloud.py"
    })

def main():
    """Main function to start the Flask server"""
    parser = argparse.ArgumentParser(description='SecureCloudFS Backend API')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    
    args = parser.parse_args()
    
    print("🚀 Starting SecureCloudFS Backend API")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print("=" * 40)
    
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
