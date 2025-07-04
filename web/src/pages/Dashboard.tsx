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
  const [apiAvailable, setApiAvailable] = useState(false);
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
          
          // Probar conexión
          const isConnected = await SecureCloudAPI.testConnection();
          setApiAvailable(isConnected);
          console.log('🔌 Conexión API:', isConnected);
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
        setApiAvailable(true);
      } else {
        // Fallback a Supabase directo
        const userFiles = await FileService.getFilesByUser(userId);
        setFiles(userFiles);
        setApiAvailable(false);
      }
    } catch (err) {
      console.error('Error loading files:', err);
      // Intentar fallback a Supabase
      try {
        const userFiles = await FileService.getFilesByUser(userId);
        setFiles(userFiles);
        setApiAvailable(false);
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
      console.log('🔽 Intentando descargar:', file.filename);
      
      // Intentar usar la API local primero
      const { SecureCloudAPI } = await import('../services/apiService');
      
      console.log('🔍 Verificando disponibilidad API...');
      const isAvailable = SecureCloudAPI.isAPIAvailable();
      
      if (isAvailable) {
        console.log('✅ API disponible, descargando...');
        await SecureCloudAPI.downloadFile(file.id, file.filename);
      } else {
        console.log('❌ API no disponible');
        // Mostrar información del archivo como fallback
        alert(`Funcionalidad de descarga para: ${file.filename}\nTamaño: ${FileService.formatFileSize(file.size)}\nSubido: ${FileService.formatDate(file.uploaded_at)}\n\nPara descargar archivos, inicia la API con:\npython scfs_api.py`);
      }
    } catch (err) {
      console.error('❌ Error downloading file:', err);
      alert('Error al descargar archivo: ' + err);
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️</div>
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SecureCloudFS</h1>
              <p className="mt-1 text-sm text-gray-600">
                Bienvenido, <strong>{user?.email}</strong>
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={refreshFiles}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Actualizar
              </button>
              
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Contenido principal */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* Estadísticas */}
          <Stats files={files} />

          {/* Información de sincronización y estado de API */}
          <div className="space-y-4 mb-6">
            {/* Estado de la API */}
            <div className={`border rounded-lg p-4 ${apiAvailable ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className={`h-5 w-5 ${apiAvailable ? 'text-green-400' : 'text-yellow-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={apiAvailable ? "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" : "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"} />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className={`text-sm font-medium ${apiAvailable ? 'text-green-800' : 'text-yellow-800'}`}>
                    {apiAvailable ? 'API de descarga activa' : 'API de descarga no disponible'}
                  </h3>
                  <div className={`mt-2 text-sm ${apiAvailable ? 'text-green-700' : 'text-yellow-700'}`}>
                    <p>
                      {apiAvailable 
                        ? 'Puedes descargar archivos directamente desde el dashboard.'
                        : 'Para descargar archivos, inicia la API con: python scfs_api.py'
                      }
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Información de sincronización */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    Sincronización Automática
                  </h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>
                      Los archivos se sincronizan automáticamente desde tu carpeta local. 
                      Para subir archivos, simplemente cópialos a tu carpeta de sincronización:
                    </p>
                    <code className="mt-1 block bg-blue-100 px-2 py-1 rounded text-xs">
                      /Users/jozefhdez/SecureCloudFS
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Lista de archivos */}
          <FileList 
            files={files} 
            onFileDelete={handleFileDelete}
            onFileDownload={handleFileDownload}
          />

        </div>
      </main>
    </div>
  );
}

