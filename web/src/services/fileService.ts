import { supabase } from './supabaseClient';
import type { FileMetadata } from '../types';

export class FileService {
  
  static async getFilesByUser(userId: string): Promise<FileMetadata[]> {
    const { data, error } = await supabase
      .from('file_metadata')
      .select('*')
      .eq('user_id', userId)
      .order('uploaded_at', { ascending: false });

    if (error) {
      console.error('Error fetching files:', error);
      throw new Error('Error getting files');
    }

    return data || [];
  }

  static async deleteFile(fileId: string): Promise<boolean> {
    const { error } = await supabase
      .from('file_metadata')
      .delete()
      .eq('id', fileId);

    if (error) {
      console.error('Error deleting file:', error);
      throw new Error('Error deleting file');
    }

    return true;
  }

  static async searchFiles(userId: string, query: string): Promise<FileMetadata[]> {
    const { data, error } = await supabase
      .from('file_metadata')
      .select('*')
      .eq('user_id', userId)
      .or(`filename.ilike.%${query}%,original_path.ilike.%${query}%`)
      .order('uploaded_at', { ascending: false });

    if (error) {
      console.error('Error searching files:', error);
      throw new Error('Error searching files');
    }

    return data || [];
  }

  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  static formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  static getFileIcon(filename: string): string {
    const extension = filename.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'doc':
      case 'docx':
        return '📝';
      case 'xls':
      case 'xlsx':
        return '📊';
      case 'ppt':
      case 'pptx':
        return '📊';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'svg':
        return '🖼️';
      case 'mp3':
      case 'wav':
      case 'flac':
        return '🎵';
      case 'mp4':
      case 'avi':
      case 'mov':
        return '🎬';
      case 'zip':
      case 'rar':
      case '7z':
        return '🗜️';
      case 'js':
      case 'ts':
      case 'py':
      case 'java':
      case 'cpp':
        return '💻';
      case 'txt':
        return '📄';
      default:
        return '📎';
    }
  }
}
