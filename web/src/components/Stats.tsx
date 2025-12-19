import type { FileMetadata } from '../types';
import { FileService } from '../services/fileService';

interface StatsProps {
  files: FileMetadata[];
}

export default function Stats({ files }: StatsProps) {
  const totalFiles = files.length;
  const totalSize = files.reduce((sum, file) => sum + file.size, 0);

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
        <div className="stat-value">
          {totalSize === 0 ? '0 ' : FileService.formatFileSize(totalSize).replace(/([A-Za-z]+)$/, '')}
          <span className="unit">{totalSize === 0 ? 'Bytes' : FileService.formatFileSize(totalSize).match(/[A-Za-z]+$/)?.[0]}</span>
        </div>
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
    </div>
  );
}
