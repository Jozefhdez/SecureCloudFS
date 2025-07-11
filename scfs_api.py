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
    print("OCI library imported successfully")
    OCI_AVAILABLE = True
except ImportError as e:
    print(f"OCI library not available: {e}")

try:
    from supabase import create_client, Client
    print("Supabase library imported successfully")
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"Supabase library not available: {e}")

# Configuration from environment
def get_oci_key_content():
    """Get OCI private key content from env variable or file"""
    key_content = os.getenv("OCI_KEY_CONTENT", "")
    if key_content:
        return key_content
    
    key_file = os.getenv("OCI_KEY_FILE", "")
    if key_file:
        try:
            key_path = os.path.join(os.path.dirname(__file__), key_file)
            with open(key_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Failed to read OCI key file {key_file}: {e}")
    return ""

OCI_CONFIG = {
    "user": os.getenv("OCI_USER_OCID", ""),
    "fingerprint": os.getenv("OCI_FINGERPRINT", ""),
    "tenancy": os.getenv("OCI_TENANCY_OCID", ""),
    "region": os.getenv("OCI_REGION", "mx-queretaro-1"),
    "key_content": get_oci_key_content()
}

OCI_NAMESPACE = os.getenv("OCI_NAMESPACE", "")
OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")

# Initialize clients only if available and configured
if OCI_AVAILABLE and all([OCI_CONFIG["user"], OCI_CONFIG["fingerprint"], OCI_CONFIG["tenancy"]]):
    try:
        object_storage_client = oci.object_storage.ObjectStorageClient(OCI_CONFIG)
        print("OCI client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize OCI client: {e}")
        object_storage_client = None
else:
    print("OCI client not initialized (missing config or library)")

if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")
        supabase = None
else:
    print("Supabase client not initialized (missing config or library)")

def authenticate_user(email: str, password: str):
    """Authenticate user with Supabase"""
    if not supabase:
        # Fallback: simulate successful auth for development
        print(f"Supabase not available, simulating auth for {email}")
        return True, type('MockAuth', (), {
            'user': type('MockUser', (), {
                'id': email,  # Using email as fallback for development
                'email': email
            })()
        })()
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if hasattr(response, 'user') and response.user:
            print(f"User authenticated successfully: {response.user.id}")
            return True, response
        else:
            print(f"Authentication failed: No user returned")
            return False, "Authentication failed"
    except Exception as e:
        print(f"Authentication error: {e}")
        return False, str(e)

def get_user_files(user_id: str):
    """Get user files from Supabase database"""
    if not supabase:
        # Fallback: return empty list for development
        print(f"Supabase not available, returning empty file list for {user_id}")
        return []
    
    try:
        response = supabase.table("file_metadata").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting user files: {e}")
        return []

def store_file_metadata(user_id: str, filename: str, file_size: int, file_hash: str, oci_object_name: str):
    """Store file metadata in Supabase"""
    if not supabase:
        # Fallback: simulate successful storage for development
        print(f"Supabase not available, simulating metadata storage for {filename}")
        return True, {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "filename": filename,
            "size": file_size,
            "hash_sha256": file_hash,
            "oci_object_name": oci_object_name,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    try:
        file_data = {
            "user_id": user_id,
            "filename": filename,
            "original_path": filename,  # Using filename as original_path for now
            "encrypted_path": oci_object_name,  # OCI path as encrypted path
            "size": file_size,
            "hash_sha256": file_hash,
            "oci_object_name": oci_object_name,
            "uploaded_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        print(f"🔍 Storing metadata for {filename} (user: {user_id})")
        response = supabase.table("file_metadata").insert(file_data).execute()
        
        if response.data:
            print(f"Metadata stored successfully for {filename}")
            return True, response.data[0]
        else:
            print(f"No data returned when storing metadata for {filename}")
            return False, "No data returned from database"
            
    except Exception as e:
        print(f"Database error storing metadata for {filename}: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
        return False, str(e)

def upload_to_oci(file_data: bytes, object_name: str):
    """Upload file to OCI Object Storage"""
    if not object_storage_client:
        # Fallback: simulate successful upload for development
        print(f"OCI not available, simulating upload for {object_name}")
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

def delete_from_oci(object_name: str):
    """Delete file from OCI Object Storage"""
    if not object_storage_client:
        # Fallback: simulate successful deletion for development
        print(f"OCI not available, simulating deletion for {object_name}")
        return True, "Simulated deletion successful"
    
    try:
        print(f"🗑️  Deleting from OCI: {object_name}")
        object_storage_client.delete_object(
            namespace_name=OCI_NAMESPACE,
            bucket_name=OCI_BUCKET_NAME,
            object_name=object_name
        )
        print(f"File deleted successfully from OCI: {object_name}")
        return True, "File deleted successfully"
    except Exception as e:
        print(f"Failed to delete from OCI: {object_name} - Error: {e}")
        return False, str(e)

def delete_file_metadata(user_id: str, file_id: str):
    """Delete file metadata from Supabase"""
    if not supabase:
        # Fallback: simulate successful deletion for development
        print(f"Supabase not available, simulating metadata deletion for {file_id}")
        return True, {"oci_object_name": f"simulated/{file_id}"}
    
    try:
        # First get the file metadata to retrieve OCI object name
        print(f"🔍 Getting metadata for file {file_id} (user: {user_id})")
        response = supabase.table("file_metadata").select("*").eq("id", file_id).eq("user_id", user_id).execute()
        
        if not response.data:
            print(f"File not found: {file_id}")
            return False, "File not found"
        
        file_metadata = response.data[0]
        print(f"Found file metadata: {file_metadata['filename']} -> {file_metadata['oci_object_name']}")
        
        # Delete the record from database
        print(f"Deleting metadata from database for file {file_id}")
        delete_response = supabase.table("file_metadata").delete().eq("id", file_id).eq("user_id", user_id).execute()
        
        verify_response = supabase.table("file_metadata").select("id").eq("id", file_id).eq("user_id", user_id).execute()
        
        if not verify_response.data:
            print(f"Metadata deleted successfully for file {file_id}")
            return True, file_metadata
        else:
            print(f"Metadata deletion failed - record still exists for {file_id}")
            return False, "Failed to delete metadata"
            
    except Exception as e:
        print(f"Database error deleting metadata for {file_id}: {e}")
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
    debug_data = {
        "service": "SecureCloudFS API Debug",
        "environment": {
            "OCI_USER_OCID": "configured" if os.getenv("OCI_USER_OCID") else "missing",
            "OCI_FINGERPRINT": "configured" if os.getenv("OCI_FINGERPRINT") else "missing",
            "OCI_TENANCY_OCID": "configured" if os.getenv("OCI_TENANCY_OCID") else "missing",
            "OCI_REGION": os.getenv("OCI_REGION", "not set"),
            "OCI_NAMESPACE": os.getenv("OCI_NAMESPACE", "not set"),
            "OCI_BUCKET_NAME": os.getenv("OCI_BUCKET_NAME", "not set"),
            "OCI_KEY_CONTENT": "configured" if get_oci_key_content() else "missing",
            "OCI_KEY_FILE": os.getenv("OCI_KEY_FILE", "not set"),
            "SUPABASE_URL": "configured" if os.getenv("SUPABASE_URL") else "missing",
            "SUPABASE_API_KEY": "configured" if os.getenv("SUPABASE_API_KEY") else "missing"
        },
        "clients": {
            "oci_available": OCI_AVAILABLE,
            "supabase_available": SUPABASE_AVAILABLE,
            "oci_client": object_storage_client is not None,
            "supabase_client": supabase is not None
        }
    }
    
    # Test Supabase connection
    if supabase:
        try:
            response = supabase.table("file_metadata").select("id").limit(1).execute()
            debug_data["supabase_table_test"] = "success"
        except Exception as e:
            debug_data["supabase_table_test"] = f"failed: {str(e)}"
    else:
        debug_data["supabase_table_test"] = "client not available"
    
    return jsonify(debug_data)

@app.route('/api/files', methods=['GET'])
def list_files():
    """List user files"""
    try:
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
        
        # Check file limit (10 files per user)
        if supabase:
            try:
                file_count_response = supabase.table("file_metadata").select("id", count="exact").eq("user_id", user_id).execute()
                current_file_count = file_count_response.count if hasattr(file_count_response, 'count') else len(file_count_response.data)
                
                if current_file_count >= 10:
                    return jsonify({
                        "success": False,
                        "error": f"File limit exceeded. You have {current_file_count}/10 files. Please delete some files before uploading new ones."
                    }), 400
                    
                print(f"User {user_id} has {current_file_count}/10 files")
            except Exception as e:
                print(f"Warning: Could not check file count: {e}")
        
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
        
        # Check file size limit (5 MB maximum)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                "success": False,
                "error": f"File too large. Maximum size is 5 MB, but your file is {file_size / (1024 * 1024):.2f} MB."
            }), 400
        
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Check if file already exists (by hash and user)
        try:
            existing_file = supabase.table("file_metadata").select("*").eq("user_id", user_id).eq("hash_sha256", file_hash).execute()
            if existing_file.data:
                return jsonify({
                    "success": True,
                    "message": "File already exists (duplicate detected)",
                    "file_id": existing_file.data[0]["id"],
                    "filename": existing_file.data[0]["filename"],
                    "size": existing_file.data[0]["size"],
                    "duplicate": True
                })
        except Exception as e:
            print(f"Warning: Could not check for duplicates: {e}")
        
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
            response = supabase.table("file_metadata").select("*").eq("id", file_id).eq("user_id", user_id).execute()
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

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file"""
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
        
        # Delete metadata from Supabase and get OCI object name
        metadata_success, metadata_result = delete_file_metadata(user_id, file_id)
        if not metadata_success:
            return jsonify({
                "success": False,
                "error": f"File not found or metadata deletion failed: {metadata_result}"
            }), 404 if "not found" in str(metadata_result).lower() else 500
        
        # Get OCI object name from metadata
        oci_object_name = metadata_result.get("oci_object_name")
        if not oci_object_name:
            return jsonify({
                "success": False,
                "error": "No OCI object name found in metadata"
            }), 500
        
        # Delete from OCI Object Storage
        oci_success, oci_result = delete_from_oci(oci_object_name)
        if not oci_success:
            print(f"Warning: File metadata deleted but OCI deletion failed: {oci_result}")
        
        return jsonify({
            "success": True,
            "message": "File deleted successfully",
            "file_id": file_id,
            "oci_deletion": "success" if oci_success else f"failed: {oci_result}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Delete failed: {str(e)}"
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "SecureCloudFS API",
        "status": "running",
        "message": "This is the backend API. Use the SecureCloudFS client to interact with the service.",
        "client_download": "https://raw.githubusercontent.com/Jozefhdez/SecureCloudFS/main/securecloud.py",
        "endpoints": {
            "health": "/api/health",
            "debug": "/api/debug",
            "files": "/api/files",
            "upload": "/api/files/upload",
            "download": "/api/files/download/<file_id>",
            "delete": "/api/files/<file_id>"
        }
    })

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return "OK"

def main():
    """Main function to start the Flask server"""
    parser = argparse.ArgumentParser(description='SecureCloudFS Backend API')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    
    args = parser.parse_args()
    
    print("Starting SecureCloudFS Backend API")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   OCI Available: {OCI_AVAILABLE}")
    print(f"   Supabase Available: {SUPABASE_AVAILABLE}")
    print(f"   OCI Client: {'Available' if object_storage_client else 'Not Available'}")
    print(f"   Supabase Client: {'Available' if supabase else 'Not Available'}")
    print("=" * 40)
    
    try:
        app.run(host=args.host, port=args.port, debug=False)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
