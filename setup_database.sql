-- Script SQL para configurar Supabase Database
-- Ejecutar este script en el SQL Editor de Supabase

-- Crear tabla para metadatos de archivos
CREATE TABLE IF NOT EXISTS file_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    original_path TEXT NOT NULL,
    encrypted_path TEXT NOT NULL,
    size BIGINT NOT NULL,
    hash_sha256 TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    oci_object_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_file_metadata_user_id ON file_metadata(user_id);
CREATE INDEX IF NOT EXISTS idx_file_metadata_filename ON file_metadata(filename);
CREATE INDEX IF NOT EXISTS idx_file_metadata_hash ON file_metadata(hash_sha256);

-- Habilitar Row Level Security (RLS)
ALTER TABLE file_metadata ENABLE ROW LEVEL SECURITY;

-- Crear política RLS: Los usuarios solo pueden ver sus propios archivos
CREATE POLICY "Users can only see their own files" ON file_metadata
    FOR ALL USING (auth.uid() = user_id);

-- Crear política RLS: Los usuarios solo pueden insertar archivos para sí mismos
CREATE POLICY "Users can only insert their own files" ON file_metadata
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Crear política RLS: Los usuarios solo pueden actualizar sus propios archivos
CREATE POLICY "Users can only update their own files" ON file_metadata
    FOR UPDATE USING (auth.uid() = user_id);

-- Crear política RLS: Los usuarios solo pueden eliminar sus propios archivos
CREATE POLICY "Users can only delete their own files" ON file_metadata
    FOR DELETE USING (auth.uid() = user_id);

-- Crear función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear trigger para actualizar updated_at automáticamente
CREATE TRIGGER update_file_metadata_updated_at 
    BEFORE UPDATE ON file_metadata 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comentarios para documentación
COMMENT ON TABLE file_metadata IS 'Metadatos de archivos cifrados almacenados en OCI';
COMMENT ON COLUMN file_metadata.user_id IS 'ID del usuario propietario del archivo';
COMMENT ON COLUMN file_metadata.filename IS 'Nombre original del archivo';
COMMENT ON COLUMN file_metadata.original_path IS 'Ruta relativa original del archivo';
COMMENT ON COLUMN file_metadata.encrypted_path IS 'Ruta del archivo cifrado (temporal)';
COMMENT ON COLUMN file_metadata.size IS 'Tamaño del archivo original en bytes';
COMMENT ON COLUMN file_metadata.hash_sha256 IS 'Hash SHA256 del archivo original';
COMMENT ON COLUMN file_metadata.oci_object_name IS 'Nombre del objeto en Oracle Cloud Storage';
