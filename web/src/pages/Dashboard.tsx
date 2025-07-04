import { useEffect, useState } from "react";
import { supabase } from "../services/supabaseClient";
import { useNavigate } from "react-router-dom";
import type { FileMetadata, User } from "../types";
import { FileService } from "../services/fileService";
import FileList from "../components/FileList";
import Stats from "../components/Stats";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const initializeDashboard = async () => {
      try {
        // Obtener información del usuario
        const { data: { user: authUser }, error: authError } = await supabase.auth.getUser();

        if (authError || !authUser) {
          navigate("/");
          return;
        }

        setUser({
          id: authUser.id,
          email: authUser.email || '',
          created_at: authUser.created_at || ''
        });

        // Configurar API con credenciales (si están disponibles)
        const storedCredentials = sessionStorage.getItem('scfs_credentials');
        if (storedCredentials) {
          const { email, password } = JSON.parse(storedCredentials);
          const { SecureCloudAPI } = await import('../services/apiService');
          SecureCloudAPI.setCredentials(email, password);
          console.log('[API] Credentials configured');
        }

        // Cargar archivos del usuario
        await loadFiles(authUser.id);
      } catch (err) {
        console.error('Error initializing dashboard:', err);
        setError('Error al cargar el dashboard');
      } finally {
        setLoading(false);
      }
    };

    initializeDashboard();
  }, [navigate]);

  const loadFiles = async (userId: string) => {
    try {
      // Intentar usar la API local primero
      const { SecureCloudAPI } = await import('../services/apiService');
      
      if (SecureCloudAPI.isAPIAvailable()) {
        const apiFiles = await SecureCloudAPI.getFiles();
        setFiles(apiFiles);
      } else {
        // Fallback a Supabase directo
        const userFiles = await FileService.getFilesByUser(userId);
        setFiles(userFiles);
      }
    } catch (err) {
      console.error('Error loading files:', err);
      // Intentar fallback a Supabase
      try {
        const userFiles = await FileService.getFilesByUser(userId);
        setFiles(userFiles);
      } catch (fallbackErr) {
        console.error('Fallback error:', fallbackErr);
        setError('Error al cargar archivos');
      }
    }
  };

  const handleFileDelete = async (fileId: string) => {
    try {
      // Intentar usar la API local primero
      const { SecureCloudAPI } = await import('../services/apiService');
      
      if (SecureCloudAPI.isAPIAvailable()) {
        await SecureCloudAPI.deleteFile(fileId);
      } else {
        // Fallback a Supabase directo
        await FileService.deleteFile(fileId);
      }
      
      setFiles(files.filter(file => file.id !== fileId));
    } catch (err) {
      console.error('Error deleting file:', err);
      alert('Error al eliminar archivo');
    }
  };

  const handleFileDownload = async (file: FileMetadata) => {
    try {
      console.log('[DOWNLOAD] Attempting to download:', file.filename);
      
      // Try using local API first
      const { SecureCloudAPI } = await import('../services/apiService');
      
      console.log('[CHECK] Verifying API availability...');
      const isAvailable = SecureCloudAPI.isAPIAvailable();
      
      if (isAvailable) {
        console.log('[SUCCESS] API available, downloading...');
        await SecureCloudAPI.downloadFile(file.id, file.filename);
      } else {
        console.log('[WARNING] API not available');
        // Show file information as fallback
        alert(`Download functionality for: ${file.filename}\nSize: ${FileService.formatFileSize(file.size)}\nUploaded: ${FileService.formatDate(file.uploaded_at)}\n\nTo download files, start the API with:\npython scfs_api.py`);
      }
    } catch (err) {
      console.error('[ERROR] Error downloading file:', err);
      alert('Error downloading file: ' + err);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate("/");
  };

  const refreshFiles = async () => {
    if (user) {
      setLoading(true);
      await loadFiles(user.id);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="loading">
          <div className="error-message">
            <p>{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="btn btn-primary"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">SecureCloudFS</h1>
          <div className="user-info">
            <span className="user-email">Welcome, {user?.email}</span>
          </div>
        </div>
        
        <div className="user-info">
          <button
            onClick={refreshFiles}
            className="btn btn-secondary header-btn"
            title="Refresh files"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          
          <button
            onClick={handleLogout}
            className="btn btn-danger header-btn"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </div>

      {/* Statistics */}
      <Stats files={files} />

      {/* File List */}
      <FileList 
        files={files} 
        onFileDelete={handleFileDelete}
        onFileDownload={handleFileDownload}
      />
    </div>
  );
}

