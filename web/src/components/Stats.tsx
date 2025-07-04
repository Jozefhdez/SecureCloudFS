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
    <div className="stats-grid">
      {/* Total Files */}
      <div className="stat-card">
        <div className="stat-header">
          <div className="stat-icon blue">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="stat-content">
            <h3>Total Files</h3>
            <p>Encrypted and stored</p>
          </div>
        </div>
        <div className="stat-value">{totalFiles}</div>
      </div>

      {/* Storage Used */}
      <div className="stat-card">
        <div className="stat-header">
          <div className="stat-icon green">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
            </svg>
          </div>
          <div className="stat-content">
            <h3>Storage Used</h3>
            <p>Total space</p>
          </div>
        </div>
        <div className="stat-value">{FileService.formatFileSize(totalSize)}</div>
      </div>

      {/* Recent Files */}
      <div className="stat-card">
        <div className="stat-header">
          <div className="stat-icon purple">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="stat-content">
            <h3>Recent Files</h3>
            <p>Last 7 days</p>
          </div>
        </div>
        <div className="stat-value">{recentFiles}</div>
      </div>

      {/* File Types */}
      <div className="stat-card">
        <div className="stat-header">
          <div className="stat-icon purple">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div className="stat-content">
            <h3>File Types</h3>
            <p>Distribution by extension</p>
          </div>
        </div>
        
        {topFileTypes.length > 0 ? (
          <div className="file-types-list">
            {topFileTypes.map(([type, count]) => (
              <div key={type} className="file-type-item">
                <div className="file-type-info">
                  <div className="file-type-dot"></div>
                  <span className="file-type-name">{type}</span>
                </div>
                <div className="file-type-count">
                  <span className="file-count-number">{count}</span>
                  <span className="file-count-label">files</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No files uploaded yet</p>
          </div>
        )}
      </div>
    </div>
  );
}
