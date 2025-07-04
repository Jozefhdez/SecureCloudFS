import type { FileMetadata } from '../types';
import { FileService } from '../services/fileService';

interface FileListProps {
  files: FileMetadata[];
  onFileDelete: (fileId: string) => void;
  onFileDownload: (file: FileMetadata) => void;
}

export default function FileList({ files, onFileDelete, onFileDownload }: FileListProps) {
  return (
    <div className="file-list-container">
      {/* Header */}
      <div className="file-list-header">
        <h2 className="file-list-title">My Files ({files.length})</h2>
      </div>

      {/* File List */}
      {files.length === 0 ? (
        <div className="empty-state">
          <p>No files uploaded yet</p>
        </div>
      ) : (
        <div className="file-list">
          {files.map((file) => (
            <div key={file.id} className="file-item">
              <div className="file-info">
                <div className="file-name">{file.filename}</div>
                <div className="file-meta">
                  {FileService.formatFileSize(file.size)} • {FileService.formatDate(file.uploaded_at)}
                </div>
              </div>
              <div className="file-actions">
                <button
                  onClick={() => onFileDownload(file)}
                  className="btn btn-secondary btn-sm"
                  title="Download file"
                >
                  Download
                </button>
                <button
                  onClick={() => onFileDelete(file.id)}
                  className="btn btn-danger btn-sm"
                  title="Delete file"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
