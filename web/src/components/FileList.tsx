import { useState } from 'react';
import type { FileMetadata } from '../types';
import { FileService } from '../services/fileService';

interface FileListProps {
  files: FileMetadata[];
  onFileDelete: (fileId: string) => void;
  onFileDownload: (file: FileMetadata) => void;
}

export default function FileList({ files, onFileDelete, onFileDownload }: FileListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const filteredAndSortedFiles = files
    .filter(file => 
      file.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      file.original_path.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      let aValue: string | number;
      let bValue: string | number;

      switch (sortBy) {
        case 'name':
          aValue = a.filename.toLowerCase();
          bValue = b.filename.toLowerCase();
          break;
        case 'size':
          aValue = a.size;
          bValue = b.size;
          break;
        case 'date':
        default:
          aValue = new Date(a.uploaded_at).getTime();
          bValue = new Date(b.uploaded_at).getTime();
          break;
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header con búsqueda y controles */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Mis Archivos ({files.length})
          </h2>
          
          <div className="flex flex-col sm:flex-row gap-3">
            {/* Búsqueda */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Buscar archivos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Ordenar */}
            <select
              value={`${sortBy}_${sortOrder}`}
              onChange={(e) => {
                const [newSortBy, newSortOrder] = e.target.value.split('_') as [typeof sortBy, typeof sortOrder];
                setSortBy(newSortBy);
                setSortOrder(newSortOrder);
              }}
              className="block w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="date_desc">Más reciente</option>
              <option value="date_asc">Más antiguo</option>
              <option value="name_asc">Nombre A-Z</option>
              <option value="name_desc">Nombre Z-A</option>
              <option value="size_desc">Mayor tamaño</option>
              <option value="size_asc">Menor tamaño</option>
            </select>
          </div>
        </div>
      </div>

      {/* Lista de archivos */}
      <div className="divide-y divide-gray-200">
        {filteredAndSortedFiles.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            {searchQuery ? 'No se encontraron archivos' : 'No hay archivos subidos'}
          </div>
        ) : (
          filteredAndSortedFiles.map((file) => (
            <FileListItem
              key={file.id}
              file={file}
              onDelete={() => onFileDelete(file.id)}
              onDownload={() => onFileDownload(file)}
            />
          ))
        )}
      </div>
    </div>
  );
}

interface FileListItemProps {
  file: FileMetadata;
  onDelete: () => void;
  onDownload: () => void;
}

function FileListItem({ file, onDelete, onDownload }: FileListItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (confirm(`¿Estás seguro de que quieres eliminar "${file.filename}"?`)) {
      setIsDeleting(true);
      try {
        await onDelete();
      } catch (error) {
        console.error('Error deleting file:', error);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div className="p-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          {/* Icono del archivo */}
          <div className="text-2xl">
            {FileService.getFileIcon(file.filename)}
          </div>
          
          {/* Información del archivo */}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {file.filename}
            </p>
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span>{FileService.formatFileSize(file.size)}</span>
              <span>{FileService.formatDate(file.uploaded_at)}</span>
              {file.original_path !== file.filename && (
                <span className="truncate">📁 {file.original_path}</span>
              )}
            </div>
          </div>
        </div>

        {/* Acciones */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onDownload}
            className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-full transition-colors"
            title="Descargar archivo"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </button>
          
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-full transition-colors disabled:opacity-50"
            title="Eliminar archivo"
          >
            {isDeleting ? (
              <div className="h-4 w-4 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
