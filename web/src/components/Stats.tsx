import type { FileMetadata } from '../types';
import { FileService } from '../services/fileService';

interface StatsProps {
  files: FileMetadata[];
}

export default function Stats({ files }: StatsProps) {
  const totalFiles = files.length;
  const totalSize = files.reduce((sum, file) => sum + file.size, 0);
  
  // Archivos por tipo
  const fileTypes = files.reduce((acc, file) => {
    const extension = file.filename.split('.').pop()?.toLowerCase() || 'sin extensión';
    acc[extension] = (acc[extension] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const topFileTypes = Object.entries(fileTypes)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  // Archivos recientes (últimos 7 días)
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  
  const recentFiles = files.filter(file => 
    new Date(file.uploaded_at) > sevenDaysAgo
  ).length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      {/* Total de archivos */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center">
          <div className="p-2 bg-blue-100 rounded-lg">
            <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Total Archivos</p>
            <p className="text-2xl font-semibold text-gray-900">{totalFiles}</p>
          </div>
        </div>
      </div>

      {/* Espacio usado */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center">
          <div className="p-2 bg-green-100 rounded-lg">
            <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m-9 0h10M7 4v16m10-16v16M7 20H5a1 1 0 01-1-1V7a1 1 0 011-1h2m10 0h2a1 1 0 011 1v12a1 1 0 01-1 1h-2" />
            </svg>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Espacio Usado</p>
            <p className="text-2xl font-semibold text-gray-900">{FileService.formatFileSize(totalSize)}</p>
          </div>
        </div>
      </div>

      {/* Archivos recientes */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center">
          <div className="p-2 bg-yellow-100 rounded-lg">
            <svg className="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Últimos 7 días</p>
            <p className="text-2xl font-semibold text-gray-900">{recentFiles}</p>
          </div>
        </div>
      </div>

      {/* Tipos de archivos */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center mb-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Tipos más comunes</p>
          </div>
        </div>
        
        {topFileTypes.length > 0 ? (
          <div className="space-y-1">
            {topFileTypes.map(([type, count]) => (
              <div key={type} className="flex justify-between text-sm">
                <span className="text-gray-600 truncate">.{type}</span>
                <span className="text-gray-900 font-medium">{count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Sin archivos</p>
        )}
      </div>
    </div>
  );
}
