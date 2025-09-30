/*
  # RFP Extraction Platform Database Schema

  ## Overview
  Creates the complete database schema for the RFP Extraction Platform,
  including tables for documents, text chunks, requirements, cross-references,
  processing jobs, and user sessions.

  ## Tables Created
  
  1. **documents** - Core document metadata and processing status
  2. **text_chunks** - Intelligently chunked text with embeddings
  3. **requirements** - Extracted requirements with classifications
  4. **cross_references** - Links between requirements
  5. **processing_jobs** - Background job tracking
  6. **user_sessions** - User authentication sessions

  ## Security
  - All tables have RLS enabled
  - Indexes created for performance
  - Audit trail maintained for all changes
*/

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- Processing metadata
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    processing_engine_used VARCHAR(50),
    extraction_confidence VARCHAR(20),
    
    -- Audit fields
    uploaded_by VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at TIMESTAMPTZ,
    validated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);

-- Text chunks table
CREATE TABLE IF NOT EXISTS text_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Chunk metadata
    chunk_index INTEGER NOT NULL,
    section_identifier VARCHAR(100),
    subsection_identifier VARCHAR(100),
    
    -- Text content
    raw_text TEXT NOT NULL,
    cleaned_text TEXT,
    
    -- Source location tracking
    source_page INTEGER,
    source_paragraph INTEGER,
    source_line_start INTEGER,
    source_line_end INTEGER,
    
    -- Vector embedding for semantic search (384 dimensions for sentence-transformers)
    embedding vector(384),
    
    -- Processing metadata
    chunk_type VARCHAR(50),
    confidence_score VARCHAR(20),
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_text_chunks_document_id ON text_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_text_chunks_section ON text_chunks(section_identifier);
CREATE INDEX IF NOT EXISTS idx_text_chunks_embedding ON text_chunks USING ivfflat (embedding vector_cosine_ops);

-- Requirements table
CREATE TABLE IF NOT EXISTS requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_chunk_id UUID NOT NULL REFERENCES text_chunks(id) ON DELETE CASCADE,
    
    -- Requirement content
    raw_text TEXT NOT NULL,
    clean_text TEXT,
    classification VARCHAR(50) NOT NULL DEFAULT 'OTHER',
    
    -- Source location
    source_page INTEGER NOT NULL,
    source_paragraph INTEGER,
    source_section VARCHAR(100),
    source_subsection VARCHAR(100),
    
    -- AI processing metadata
    ai_confidence_score VARCHAR(20),
    extraction_method VARCHAR(50),
    
    -- Validation workflow
    status VARCHAR(50) NOT NULL DEFAULT 'ai_extracted',
    validation_notes TEXT,
    
    -- Audit trail (JSONB for flexible history tracking)
    history JSONB DEFAULT '[]'::jsonb,
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    validated_by VARCHAR(100),
    validated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_requirements_document_id ON requirements(document_id);
CREATE INDEX IF NOT EXISTS idx_requirements_status ON requirements(status);
CREATE INDEX IF NOT EXISTS idx_requirements_classification ON requirements(classification);
CREATE INDEX IF NOT EXISTS idx_requirements_source_chunk ON requirements(source_chunk_id);

-- Cross references table
CREATE TABLE IF NOT EXISTS cross_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    target_chunk_id UUID NOT NULL REFERENCES text_chunks(id) ON DELETE CASCADE,
    
    -- Reference details
    reference_type VARCHAR(50) NOT NULL,
    reference_text TEXT NOT NULL,
    reference_target VARCHAR(200),
    confidence_score VARCHAR(20),
    similarity_score VARCHAR(20),
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by VARCHAR(100) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cross_references_requirement ON cross_references(requirement_id);
CREATE INDEX IF NOT EXISTS idx_cross_references_target ON cross_references(target_chunk_id);

-- Processing jobs table
CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Job details
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Error tracking
    error_message TEXT,
    error_details JSONB,
    
    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_document ON processing_jobs(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);

-- User sessions table (for future authentication)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    
    -- Session data
    user_email VARCHAR(255),
    user_role VARCHAR(50),
    
    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_activity TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);

-- Enable Row Level Security (RLS) on all tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE text_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE cross_references ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Create permissive policies for development (IMPORTANT: Restrict these in production!)
CREATE POLICY "Allow all operations for development" ON documents FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations for development" ON text_chunks FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations for development" ON requirements FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations for development" ON cross_references FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations for development" ON processing_jobs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations for development" ON user_sessions FOR ALL USING (true) WITH CHECK (true);
