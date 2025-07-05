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
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "service": "SecureCloudFS API",
        "version": "1.0.0"
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
        
        # For now, return empty list (backend storage integration needed)
        return jsonify({
            "success": True,
            "files": []
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
        
        # For now, simulate successful upload
        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "file_id": "temp_id_123"
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
        
        # For now, return error (storage integration needed)
        return jsonify({
            "success": False,
            "error": "File not found"
        }), 404
        
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
