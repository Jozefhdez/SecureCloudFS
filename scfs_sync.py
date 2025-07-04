#!/usr/bin/env python3
"""
SecureCloudFS - Encrypted virtual filesystem with automatic synchronization
Author: Jozef Hernandez
License: MIT
"""

import os
import json
import time
import hashlib
import base64
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# External dependencies
from dotenv import load_dotenv
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import oci

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('securecloud.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class FileMetadata:
    """File metadata for synchronization"""
    filename: str
    original_path: str
    encrypted_path: str
    size: int
    hash_sha256: str
    user_id: str
    uploaded_at: datetime
    oci_object_name: str

class SecureCloudAuth:
    """Supabase authentication management"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_api_key = os.getenv("SUPABASE_API_KEY")
        if not self.supabase_url or not self.supabase_api_key:
            raise ValueError("SUPABASE_URL and SUPABASE_API_KEY are required")
    
    def login(self, email: str, password: str) -> Tuple[str, str, Dict]:
        """
        Authenticate user with Supabase
        
        Returns:
            Tuple[access_token, refresh_token, user_data]
        """
        url = f"{self.supabase_url}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": self.supabase_api_key,
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                json_resp = response.json()
                access_token = json_resp.get("access_token")
                refresh_token = json_resp.get("refresh_token")
                user = json_resp.get("user")
                
                if not access_token or not user:
                    raise Exception("Respuesta de autenticación inválida")
                
                logger.info(f"Usuario autenticado exitosamente: {user.get('email')}")
                return access_token, refresh_token, user
            else:
                error_msg = response.json().get("error_description", "Error desconocido")
                raise Exception(f"Login failed: {error_msg}")
                
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")
    
    def verify_token(self, access_token: str) -> Dict:
        """Verify JWT token validity"""
        url = f"{self.supabase_url}/auth/v1/user"
        headers = {
            "apikey": self.supabase_api_key,
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Invalid or expired token")

class SecureCloudCrypto:
    """AES-256 encryption management for files"""
    
    def __init__(self, password: str):
        """
        Initialize with user password
        
        Args:
            password: Password to derive encryption key
        """
        self.password = password.encode()
        self._setup_encryption()
    
    def _setup_encryption(self):
        """Setup encryption using PBKDF2 + AES-256"""
        # Use fixed salt derived from password (in production should be random per file)
        salt = hashlib.sha256(self.password).digest()[:16]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        self.fernet = Fernet(key)
    
    def encrypt_file(self, file_path: str, output_path: str) -> str:
        """
        Cifrar archivo y guardarlo en output_path
        
        Returns:
            SHA256 hash del archivo original
        """
        try:
            # Leer archivo original
            with open(file_path, 'rb') as file:
                original_data = file.read()
            
            # Calcular hash del archivo original
            hash_sha256 = hashlib.sha256(original_data).hexdigest()
            
            # Cifrar datos
            encrypted_data = self.fernet.encrypt(original_data)
            
            # Guardar archivo cifrado
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as file:
                file.write(encrypted_data)
            
            logger.info(f"Archivo cifrado: {file_path} -> {output_path}")
            return hash_sha256
            
        except Exception as e:
            logger.error(f"Error cifrando archivo {file_path}: {str(e)}")
            raise
    
    def decrypt_file(self, encrypted_path: str, output_path: str) -> bool:
        """Decrypt file"""
        try:
            with open(encrypted_path, 'rb') as file:
                encrypted_data = file.read()
            
            # Descifrar datos
            original_data = self.fernet.decrypt(encrypted_data)
            
            # Guardar archivo descifrado
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as file:
                file.write(original_data)
            
            logger.info(f"Archivo descifrado: {encrypted_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error descifrando archivo {encrypted_path}: {str(e)}")
            return False

class SecureCloudOCI:
    """Oracle Cloud Infrastructure client"""
    
    def __init__(self):
        """Initialize OCI client using environment variables"""
        try:
            # Configuración OCI desde variables de entorno
            config = {
                "user": os.getenv("OCI_USER_OCID"),
                "key_file": os.getenv("OCI_KEY_FILE"),
                "fingerprint": os.getenv("OCI_FINGERPRINT"),
                "tenancy": os.getenv("OCI_TENANCY_OCID"),
                "region": os.getenv("OCI_REGION", "us-ashburn-1")
            }
            
            # Validar configuración
            required_keys = ["user", "key_file", "fingerprint", "tenancy"]
            for key in required_keys:
                if not config[key]:
                    raise ValueError(f"Variable de entorno OCI_{key.upper()} es requerida")
            
            self.config = config
            self.namespace = os.getenv("OCI_NAMESPACE")
            self.bucket_name = os.getenv("OCI_BUCKET_NAME")
            
            if not self.namespace or not self.bucket_name:
                raise ValueError("OCI_NAMESPACE y OCI_BUCKET_NAME son requeridos")
            
            # Inicializar cliente
            self.object_storage = oci.object_storage.ObjectStorageClient(config)
            logger.info("Cliente OCI inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando OCI: {str(e)}")
            raise
    
    def upload_file(self, file_path: str, object_name: str) -> bool:
        """
        Subir archivo a OCI Object Storage
        
        Args:
            file_path: Ruta local del archivo a subir
            object_name: Nombre del objeto en OCI (incluye prefijo del usuario)
        """
        try:
            with open(file_path, 'rb') as file:
                self.object_storage.put_object(
                    namespace_name=self.namespace,
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    put_object_body=file
                )
            
            logger.info(f"Archivo subido a OCI: {object_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error subiendo archivo a OCI {object_name}: {str(e)}")
            return False
    
    def download_file(self, object_name: str, file_path: str) -> bool:
        """Descargar archivo desde OCI"""
        try:
            response = self.object_storage.get_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as file:
                for chunk in response.data.raw.stream(1024 * 1024, decode_content=False):
                    file.write(chunk)
            
            logger.info(f"Archivo descargado desde OCI: {object_name} -> {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error descargando archivo desde OCI {object_name}: {str(e)}")
            return False
    
    def list_objects(self, prefix: str) -> List[str]:
        """Listar objetos con prefijo específico"""
        try:
            response = self.object_storage.list_objects(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                prefix=prefix
            )
            
            return [obj.name for obj in response.data.objects]
            
        except Exception as e:
            logger.error(f"Error listando objetos OCI con prefijo {prefix}: {str(e)}")
            return []

class SecureCloudDatabase:
    """Manejo de metadatos en Supabase"""
    
    def __init__(self, access_token: str):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_api_key = os.getenv("SUPABASE_API_KEY")
        self.access_token = access_token
        self.headers = {
            "apikey": self.supabase_api_key,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def save_file_metadata(self, metadata: FileMetadata) -> bool:
        """Guardar metadatos de archivo en Supabase"""
        try:
            url = f"{self.supabase_url}/rest/v1/file_metadata"
            data = {
                "filename": metadata.filename,
                "original_path": metadata.original_path,
                "encrypted_path": metadata.encrypted_path,
                "size": metadata.size,
                "hash_sha256": metadata.hash_sha256,
                "user_id": metadata.user_id,
                "uploaded_at": metadata.uploaded_at.isoformat(),
                "oci_object_name": metadata.oci_object_name
            }
            
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            if response.status_code in [200, 201]:
                logger.info(f"Metadatos guardados para: {metadata.filename}")
                return True
            else:
                logger.error(f"Error guardando metadatos: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error guardando metadatos: {str(e)}")
            return False
    
    def get_user_files(self, user_id: str) -> List[Dict]:
        """Obtener archivos del usuario"""
        try:
            url = f"{self.supabase_url}/rest/v1/file_metadata"
            params = {"user_id": f"eq.{user_id}"}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo archivos del usuario: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo archivos: {str(e)}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """Eliminar archivo por ID"""
        try:
            url = f"{self.supabase_url}/rest/v1/file_metadata"
            params = {"id": f"eq.{file_id}"}
            
            response = requests.delete(url, params=params, headers=self.headers, timeout=10)
            if response.status_code in [200, 204]:
                logger.info(f"Archivo eliminado: {file_id}")
                return True
            else:
                logger.error(f"Error eliminando archivo: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando archivo: {str(e)}")
            return False

class SecureCloudFileWatcher(FileSystemEventHandler):
    """Monitor de cambios en el sistema de archivos"""
    
    def __init__(self, sync_handler):
        self.sync_handler = sync_handler
        self.ignore_patterns = {'.DS_Store', '.git', '__pycache__', '.tmp'}
    
    def should_ignore(self, file_path: str) -> bool:
        """Verificar si el archivo debe ser ignorado"""
        filename = os.path.basename(file_path)
        return any(pattern in filename for pattern in self.ignore_patterns)
    
    def on_created(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            logger.info(f"Archivo nuevo detectado: {event.src_path}")
            self.sync_handler.sync_file(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            logger.info(f"Archivo modificado detectado: {event.src_path}")
            self.sync_handler.sync_file(event.src_path)

class SecureCloudFS:
    """Clase principal del sistema SecureCloudFS"""
    
    def __init__(self, email: str, password: str, sync_folder: str):
        """
        Inicializar SecureCloudFS
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            sync_folder: Carpeta local para sincronización
        """
        self.email = email
        self.password = password
        self.sync_folder = Path(sync_folder)
        
        # Crear carpeta de sincronización si no existe
        self.sync_folder.mkdir(parents=True, exist_ok=True)
        
        # Carpeta para archivos cifrados temporales
        self.encrypted_folder = self.sync_folder / ".encrypted"
        self.encrypted_folder.mkdir(exist_ok=True)
        
        # Inicializar componentes
        self.auth = SecureCloudAuth()
        self.crypto = SecureCloudCrypto(password)
        self.oci_client = SecureCloudOCI()
        
        # Autenticar usuario
        self.access_token, self.refresh_token, self.user = self.auth.login(email, password)
        self.user_id = self.user["id"]
        
        # Inicializar database client
        self.db = SecureCloudDatabase(self.access_token)
        
        # Monitor de archivos
        self.observer = None
        
        logger.info(f"SecureCloudFS inicializado para usuario: {email}")
        logger.info(f"Carpeta de sincronización: {self.sync_folder}")
    
    def sync_file(self, file_path: str) -> bool:
        """
        Sincronizar un archivo específico
        
        Args:
            file_path: Ruta del archivo a sincronizar
        """
        try:
            # Verificar que el archivo existe y no está en la carpeta cifrada
            if not os.path.exists(file_path) or ".encrypted" in file_path:
                return False
            
            filename = os.path.basename(file_path)
            relative_path = os.path.relpath(file_path, self.sync_folder)
            
            # Crear ruta para archivo cifrado
            encrypted_filename = f"{filename}.enc"
            encrypted_path = self.encrypted_folder / encrypted_filename
            
            # Cifrar archivo
            file_hash = self.crypto.encrypt_file(file_path, str(encrypted_path))
            
            # Crear nombre único en OCI con prefijo del usuario
            timestamp = int(time.time())
            oci_object_name = f"users/{self.user_id}/{timestamp}_{encrypted_filename}"
            
            # Subir a OCI
            if self.oci_client.upload_file(str(encrypted_path), oci_object_name):
                # Crear metadatos
                metadata = FileMetadata(
                    filename=filename,
                    original_path=relative_path,
                    encrypted_path=str(encrypted_path),
                    size=os.path.getsize(file_path),
                    hash_sha256=file_hash,
                    user_id=self.user_id,
                    uploaded_at=datetime.now(),
                    oci_object_name=oci_object_name
                )
                
                # Guardar metadatos en database
                if self.db.save_file_metadata(metadata):
                    # Eliminar archivo cifrado temporal
                    os.remove(str(encrypted_path))
                    logger.info(f"Archivo sincronizado exitosamente: {filename}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sincronizando archivo {file_path}: {str(e)}")
            return False
    
    def start_monitoring(self):
        """Iniciar monitoreo automático de la carpeta"""
        if self.observer:
            return
        
        event_handler = SecureCloudFileWatcher(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.sync_folder), recursive=True)
        self.observer.start()
        
        logger.info(f"Monitoreo iniciado en: {self.sync_folder}")
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Monitoreo detenido")
    
    def sync_existing_files(self):
        """Sincronizar todos los archivos existentes en la carpeta"""
        logger.info("Sincronizando archivos existentes...")
        
        for root, dirs, files in os.walk(self.sync_folder):
            # Ignorar carpeta cifrada
            if ".encrypted" in root:
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                self.sync_file(file_path)
    
    def list_user_files(self) -> List[Dict]:
        """Listar archivos del usuario"""
        return self.db.get_user_files(self.user_id)
    
    def download_file(self, oci_object_name: str, local_path: str) -> bool:
        """
        Descargar y descifrar archivo desde OCI
        
        Args:
            oci_object_name: Nombre del objeto en OCI
            local_path: Ruta local donde guardar el archivo
        """
        try:
            # Crear ruta temporal para archivo cifrado
            temp_encrypted = self.encrypted_folder / f"temp_{int(time.time())}.enc"
            
            # Descargar desde OCI
            if self.oci_client.download_file(oci_object_name, str(temp_encrypted)):
                # Descifrar archivo
                if self.crypto.decrypt_file(str(temp_encrypted), local_path):
                    # Eliminar archivo temporal
                    os.remove(str(temp_encrypted))
                    logger.info(f"Archivo descargado y descifrado: {local_path}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error descargando archivo {oci_object_name}: {str(e)}")
            return False

def main():
    """Función principal del script"""
    print("=== SecureCloudFS - Sistema de Archivos Cifrado ===")
    print()
    
    # Solicitar credenciales
    email = input("Email: ").strip()
    password = input("Contraseña: ").strip()
    
    # Solicitar carpeta de sincronización
    default_folder = os.path.join(os.path.expanduser("~"), "SecureCloudFS")
    sync_folder = input(f"Carpeta de sincronización [{default_folder}]: ").strip()
    if not sync_folder:
        sync_folder = default_folder
    
    try:
        # Inicializar SecureCloudFS
        print("\nInicializando SecureCloudFS...")
        scfs = SecureCloudFS(email, password, sync_folder)
        
        # Sincronizar archivos existentes
        print("Sincronizando archivos existentes...")
        scfs.sync_existing_files()
        
        # Iniciar monitoreo
        print("Iniciando monitoreo automático...")
        scfs.start_monitoring()
        
        print(f"\n✅ SecureCloudFS está ejecutándose!")
        print(f"📁 Carpeta monitoreada: {sync_folder}")
        print("💡 Los archivos se cifrarán y subirán automáticamente")
        print("⏹️  Presiona Ctrl+C para detener")
        
        # Mantener el script ejecutándose
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo SecureCloudFS...")
            scfs.stop_monitoring()
            print("✅ SecureCloudFS detenido correctamente")
            
    except Exception as e:
        logger.error(f"Error en main: {str(e)}")
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
