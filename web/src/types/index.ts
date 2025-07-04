export interface FileMetadata {
  id: string;
  user_id: string;
  filename: string;
  original_path: string;
  encrypted_path: string;
  size: number;
  hash_sha256: string;
  uploaded_at: string;
  oci_object_name: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface FileUploadProgress {
  filename: string;
  progress: number;
  status: 'uploading' | 'encrypting' | 'complete' | 'error';
  error?: string;
}
