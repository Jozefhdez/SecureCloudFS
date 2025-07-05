#!/usr/bin/env python3
"""
SecureCloudFS API - HTTP server for frontend system interaction
"""

import os
import json
import tempfile
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import logging
from datetime import datetime

from scfs_sync import SecureCloudFS, SecureCloudAuth

# Configurar CORS
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-User-Email, X-User-Password',
    'Access-Control-Max-Age': '86400'
}

class SecureCloudAPIHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Manejar preflight requests de CORS"""
        self.send_response(200)
        for header, value in CORS_HEADERS.items():
            self.send_header(header, value)
        self.end_headers()
        return
    
    def do_GET(self):
        """Manejar requests GET"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        try:
            if path == '/api/files':
                self.handle_list_files(query_params)
            elif path.startswith('/api/files/download/'):
                file_id = path.split('/')[-1]
                self.handle_download_file(file_id, query_params)
            elif path == '/api/auth/verify':
                self.handle_verify_auth(query_params)
            elif path == '/api/health':
                self.handle_health_check()
            else:
                self.send_error_response(404, "Endpoint no encontrado")
                
        except Exception as e:
            logging.error(f"Error en GET {path}: {str(e)}")
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        """Manejar requests POST"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/api/auth/login':
                self.handle_login()
            elif path == '/api/files/upload':
                self.handle_upload_file()
            else:
                self.send_error_response(404, "Endpoint no encontrado")
                
        except Exception as e:
            logging.error(f"Error en POST {path}: {str(e)}")
            self.send_error_response(500, str(e))
    
    def do_DELETE(self):
        """Manejar requests DELETE"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path.startswith('/api/files/'):
                file_id = path.split('/')[-1]
                self.handle_delete_file(file_id)
            else:
                self.send_error_response(404, "Endpoint no encontrado")
                
        except Exception as e:
            logging.error(f"Error en DELETE {path}: {str(e)}")
            self.send_error_response(500, str(e))
    
    def handle_login(self):
        """Autenticar usuario"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            self.send_error_response(400, "Email y contraseña son requeridos")
            return
        
        try:
            auth = SecureCloudAuth()
            access_token, refresh_token, user = auth.login(email, password)
            
            response_data = {
                'success': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user
            }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            self.send_error_response(401, f"Error de autenticación: {str(e)}")
    
    def handle_verify_auth(self, query_params):
        """Verificar token de autenticación"""
        token = self.get_auth_token()
        if not token:
            self.send_error_response(401, "Token no proporcionado")
            return
        
        try:
            auth = SecureCloudAuth()
            user = auth.verify_token(token)
            
            self.send_json_response({
                'success': True,
                'user': user
            })
            
        except Exception as e:
            self.send_error_response(401, f"Token inválido: {str(e)}")
    
    def handle_list_files(self, query_params):
        """Listar archivos del usuario"""
        email, password = self.get_credentials()
        if not email or not password:
            return
        
        try:
            # Usar carpeta temporal para evitar conflictos
            temp_folder = tempfile.mkdtemp()
            scfs = SecureCloudFS(email, password, temp_folder)
            files = scfs.list_user_files()
            
            self.send_json_response({
                'success': True,
                'files': files
            })
            
        except Exception as e:
            self.send_error_response(500, f"Error obteniendo archivos: {str(e)}")
    
    def handle_download_file(self, file_id, query_params):
        """Descargar archivo específico"""
        email, password = self.get_credentials()
        if not email or not password:
            return
        
        try:
            temp_folder = tempfile.mkdtemp()
            scfs = SecureCloudFS(email, password, temp_folder)
            files = scfs.list_user_files()
            
            # Buscar archivo por ID
            target_file = None
            for file_data in files:
                if file_data['id'] == file_id:
                    target_file = file_data
                    break
            
            if not target_file:
                self.send_error_response(404, "Archivo no encontrado")
                return
            
            # Crear archivo temporal para descarga
            temp_download_path = os.path.join(temp_folder, target_file['filename'])
            
            if scfs.download_file(target_file['oci_object_name'], temp_download_path):
                # Leer archivo y enviarlo
                with open(temp_download_path, 'rb') as f:
                    file_content = f.read()
                
                self.send_response(200)
                for header, value in CORS_HEADERS.items():
                    self.send_header(header, value)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{target_file["filename"]}"')
                self.send_header('Content-Length', str(len(file_content)))
                self.end_headers()
                
                self.wfile.write(file_content)
                
                # Limpiar archivo temporal
                os.remove(temp_download_path)
            else:
                self.send_error_response(500, "Error descargando archivo")
                
        except Exception as e:
            self.send_error_response(500, f"Error en descarga: {str(e)}")
    
    def handle_delete_file(self, file_id):
        """Eliminar archivo"""
        email, password = self.get_credentials()
        if not email or not password:
            return
        
        try:
            temp_folder = tempfile.mkdtemp()
            scfs = SecureCloudFS(email, password, temp_folder)
            
            # Obtener información del archivo
            files = scfs.list_user_files()
            target_file = None
            for file_data in files:
                if file_data['id'] == file_id:
                    target_file = file_data
                    break
            
            if not target_file:
                self.send_error_response(404, "Archivo no encontrado")
                return
            
            # Eliminar de la base de datos
            if scfs.db.delete_file(file_id):
                # TODO: También eliminar de OCI
                self.send_json_response({
                    'success': True,
                    'message': 'Archivo eliminado correctamente'
                })
            else:
                self.send_error_response(500, "Error eliminando archivo")
                
        except Exception as e:
            self.send_error_response(500, f"Error eliminando archivo: {str(e)}")
    
    def handle_health_check(self):
        """Health check endpoint for deployment platforms"""
        self.send_json_response({
            'status': 'healthy',
            'service': 'SecureCloudFS API',
            'timestamp': datetime.now().isoformat()
        })
    
    def get_auth_token(self):
        """Extraer token de autenticación del header"""
        auth_header = self.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remover "Bearer "
        return None
    
    def get_credentials(self):
        """Obtener credenciales básicas (para desarrollo - usar JWT en producción)"""
        email = self.headers.get('X-User-Email')
        password = self.headers.get('X-User-Password')
        
        if not email or not password:
            self.send_error_response(401, "Credenciales no proporcionadas")
            return None, None
        
        return email, password
    
    def send_json_response(self, data, status_code=200):
        """Enviar respuesta JSON"""
        response_json = json.dumps(data, ensure_ascii=False, default=str)
        
        self.send_response(status_code)
        for header, value in CORS_HEADERS.items():
            self.send_header(header, value)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
        self.end_headers()
        
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """Enviar respuesta de error"""
        error_data = {
            'success': False,
            'error': message,
            'status_code': status_code
        }
        self.send_json_response(error_data, status_code)
    
    def log_message(self, format, *args):
        """Silenciar logs automáticos del servidor HTTP"""
        pass

def start_api_server(port=8080):
    """Start API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SecureCloudAPIHandler)
    
    print(f"SecureCloudFS API running on http://localhost:{port}")
    print("Available endpoints:")
    print("   POST /api/auth/login - Authenticate user")
    print("   GET  /api/auth/verify - Verify token")
    print("   GET  /api/files - List files")
    print("   GET  /api/files/download/{id} - Download file")
    print("   DELETE /api/files/{id} - Delete file")
    print("\nPress Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping API server...")
        httpd.shutdown()

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="SecureCloudFS API Server")
    
    # Use PORT environment variable for cloud deployment, fallback to 8080 for local
    default_port = int(os.environ.get('PORT', 8080))
    parser.add_argument("--port", type=int, default=default_port, help="Server port (default: 8080 or PORT env var)")
    args = parser.parse_args()
    
    start_api_server(args.port)
