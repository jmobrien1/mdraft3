/*
  # Create Storage Bucket for Documents

  1. Storage
    - Create a public bucket named 'documents' for storing uploaded RFP files
    - Set appropriate policies to allow authenticated uploads and public downloads

  2. Security
    - Allow authenticated users to upload documents
    - Allow public read access to documents (for simplicity in this version)
*/

-- Create the storage bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('documents', 'documents', true)
ON CONFLICT (id) DO NOTHING;

-- Allow authenticated users to upload
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'storage'
    AND tablename = 'objects'
    AND policyname = 'Allow authenticated uploads'
  ) THEN
    CREATE POLICY "Allow authenticated uploads"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (bucket_id = 'documents');
  END IF;
END $$;

-- Allow public downloads
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'storage'
    AND tablename = 'objects'
    AND policyname = 'Allow public downloads'
  ) THEN
    CREATE POLICY "Allow public downloads"
    ON storage.objects FOR SELECT
    TO public
    USING (bucket_id = 'documents');
  END IF;
END $$;
