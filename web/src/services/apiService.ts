import type { FileMetadata } from '../types';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api';

export class SecureCloudAPI {
  private static email: string | null = null;
  private static password: string | null = null;

  static setCredentials(email: string, password: string) {
    this.email = email;
    this.password = password;
    console.log('[INFO] API credentials configured for:', email);
  }

  private static getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.email && this.password) {
      headers['X-User-Email'] = this.email;
      headers['X-User-Password'] = this.password;
      console.log('[AUTH] Sending credentials for:', this.email);
    } else {
      console.warn('[WARN] No credentials configured');
    }

    return headers;
  }

  static async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/files`, {
        headers: this.getHeaders(),
      });
      
      console.log('[NETWORK] API connection test:', response.status);
      return response.ok;
    } catch (error) {
      console.error('[ERROR] Error connecting to API:', error);
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
      return { success: false, error: 'Connection error with API' };
    }
  }

  static async getFiles(): Promise<FileMetadata[]> {
    try {
      console.log('[FILES] Getting files from API...');
      const response = await fetch(`${API_BASE_URL}/files`, {
        headers: this.getHeaders(),
      });

      console.log('[FILES] API response status:', response.status);
      const data = await response.json();
      
      if (data.success) {
        console.log('[SUCCESS] Files obtained:', data.files.length);
        return data.files;
      } else {
        console.error('[ERROR] API error:', data.error);
        throw new Error(data.error);
      }
    } catch (error) {
      console.error('[ERROR] Error fetching files:', error);
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
        throw new Error('Error downloading file');
      }

      // Create blob and download
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
    console.log('[CHECK] API available:', available, this.email ? `(${this.email})` : '(no credentials)');
    return available;
  }
}
