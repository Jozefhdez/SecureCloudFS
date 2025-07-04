import type { FileMetadata } from '../types';

const API_BASE_URL = 'http://localhost:8080/api';

export class SecureCloudAPI {
  private static email: string | null = null;
  private static password: string | null = null;

  static setCredentials(email: string, password: string) {
    this.email = email;
    this.password = password;
    console.log('✅ Credenciales API configuradas para:', email);
  }

  private static getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.email && this.password) {
      headers['X-User-Email'] = this.email;
      headers['X-User-Password'] = this.password;
      console.log('🔑 Enviando credenciales para:', this.email);
    } else {
      console.warn('⚠️ No hay credenciales configuradas');
    }

    return headers;
  }

  static async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/files`, {
        headers: this.getHeaders(),
      });
      
      console.log('🌐 Test conexión API:', response.status);
      return response.ok;
    } catch (error) {
      console.error('❌ Error conectando con API:', error);
      return false;
    }
  }

  static async login(email: string, password: string): Promise<{ success: boolean; user?: any; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      
      if (data.success) {
        this.setCredentials(email, password);
        return { success: true, user: data.user };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Error de conexión con la API' };
    }
  }

  static async getFiles(): Promise<FileMetadata[]> {
    try {
      console.log('📁 Obteniendo archivos desde API...');
      const response = await fetch(`${API_BASE_URL}/files`, {
        headers: this.getHeaders(),
      });

      console.log('📁 Respuesta API status:', response.status);
      const data = await response.json();
      
      if (data.success) {
        console.log('✅ Archivos obtenidos:', data.files.length);
        return data.files;
      } else {
        console.error('❌ Error API:', data.error);
        throw new Error(data.error);
      }
    } catch (error) {
      console.error('❌ Error fetching files:', error);
      throw error;
    }
  }

  static async deleteFile(fileId: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Error deleting file:', error);
      throw error;
    }
  }

  static async downloadFile(fileId: string, filename: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/files/download/${fileId}`, {
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Error descargando archivo');
      }

      // Crear blob y descargar
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading file:', error);
      throw error;
    }
  }

  static isAPIAvailable(): boolean {
    const available = this.email !== null && this.password !== null;
    console.log('🔍 API disponible:', available, this.email ? `(${this.email})` : '(sin credenciales)');
    return available;
  }
}
