# RFP Requirement Extractor - As-Built Technical Design Document

**Document Version:** 1.0
**Last Updated:** October 5, 2025
**Project Status:** Development Complete

---

## Executive Summary

The RFP Requirement Extractor is an AI-powered web application designed to automate the extraction, classification, and validation of requirements from U.S. Government Request for Proposal (RFP) documents. The system provides a human-in-the-loop validation workflow, ensuring high accuracy while reducing manual processing time by up to 80%.

### Key Capabilities
- **Multi-format Document Processing**: PDF, DOCX, and TXT file support
- **Intelligent Requirement Extraction**: Pattern-based extraction with AI classification
- **Three-tier Classification System**: Performance, Compliance, and Deliverable requirements
- **Human Validation Workflow**: Review queue with approve/correct/flag actions
- **Full Audit Trail**: Complete history tracking for compliance and protest defense
- **Dual Frontend Options**: Modern React SPA and Streamlit validation console

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
├─────────────────┬───────────────────────────────────────────────┤
│  React Frontend │           Streamlit Console                   │
│   (Port 5173)   │             (Port 8501)                       │
└────────┬────────┴──────────────┬────────────────────────────────┘
         │                       │
         │    HTTP/REST API      │
         └───────────┬───────────┘
                     │
         ┌───────────▼────────────┐
         │   FastAPI Backend      │
         │     (Port 8000)        │
         │                        │
         │  ┌──────────────────┐  │
         │  │ Document Processor│  │
         │  ├──────────────────┤  │
         │  │ Requirement       │  │
         │  │ Extractor        │  │
         │  ├──────────────────┤  │
         │  │ Classification    │  │
         │  │ Engine           │  │
         │  └──────────────────┘  │
         └────────┬───────────────┘
                  │
         ┌────────▼────────────────┐
         │    Supabase Platform    │
         ├─────────────────────────┤
         │  PostgreSQL + pgvector  │
         │  (Database + Embeddings)│
         ├─────────────────────────┤
         │    Storage Bucket       │
         │  (Document Files)       │
         └─────────────────────────┘
```

### Technology Stack

#### Backend
- **Python 3.11+**: Core runtime environment
- **FastAPI**: Modern async web framework for REST API
- **SQLAlchemy 2.0**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **PyMuPDF (fitz)**: PDF text extraction
- **python-docx**: DOCX document parsing
- **PyPDF2**: Alternative PDF processor
- **Sentence Transformers**: Local embedding generation (MiniLM)
- **OpenAI API** (Optional): Advanced classification

#### Frontend Options

**Option 1: React SPA**
- **React 18**: Component-based UI library
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API communication
- **Modern CSS**: Custom styling without framework dependencies

**Option 2: Streamlit**
- **Streamlit**: Python-based rapid prototyping framework
- **Ideal for**: Internal validation console and quick demos

#### Database
- **Supabase**: Managed PostgreSQL with built-in APIs
- **PostgreSQL 15+**: Relational database with JSONB support
- **pgvector Extension**: Vector similarity search for embeddings
- **Row Level Security (RLS)**: Fine-grained access control

---

## Database Design

### Schema Overview

The database implements a comprehensive schema designed for compliance, auditability, and traceability in government contracting environments.

#### Entity-Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│  documents  │1      N │ text_chunks  │1      N │ requirements │
│             ├────────>│              ├────────>│              │
│  - id (PK)  │         │  - id (PK)   │         │  - id (PK)   │
│  - filename │         │  - doc_id(FK)│         │  - doc_id(FK)│
│  - status   │         │  - embedding │         │  - chunk(FK) │
│  - metadata │         │  - raw_text  │         │  - raw_text  │
└─────────────┘         └──────────────┘         │  - class     │
                                                  │  - status    │
                                                  │  - history   │
                                                  └──────┬───────┘
                                                         │N
                                                         │
                                                    ┌────▼──────────┐
                                                    │cross_references│
                                                    │               │
                                                    │  - id (PK)    │
                                                    │  - req_id(FK) │
                                                    │  - target(FK) │
                                                    └───────────────┘
```

### Core Tables

#### 1. **documents**
Stores metadata about uploaded RFP documents.

**Key Fields:**
- `id` (UUID): Primary key, auto-generated
- `filename` (VARCHAR): Original uploaded filename
- `file_path` (VARCHAR): Storage path in Supabase
- `file_size` (INTEGER): Size in bytes
- `file_type` (VARCHAR): Extension (pdf, docx, txt)
- `status` (VARCHAR): Processing status
  - `uploaded` → `processing` → `completed` / `error`
- `processing_engine_used` (VARCHAR): Engine used (pymupdf, unstructured, document_ai)
- `extraction_confidence` (VARCHAR): Overall confidence (low, medium, high)
- `uploaded_by` (VARCHAR): User identifier (future: link to auth)
- `uploaded_at` (TIMESTAMPTZ): Upload timestamp
- `processed_at` (TIMESTAMPTZ): Processing completion time
- `validated_at` (TIMESTAMPTZ): Validation completion time

**Indexes:**
- `idx_documents_status`: Query by processing status
- `idx_documents_uploaded_at`: Chronological queries
- `idx_documents_file_type`: Filter by document type

#### 2. **text_chunks**
Intelligently segmented text from documents with semantic embeddings.

**Key Fields:**
- `id` (UUID): Primary key
- `document_id` (UUID): Foreign key to documents
- `chunk_index` (INTEGER): Sequential order within document
- `section_identifier` (VARCHAR): Section label (e.g., "Section C")
- `subsection_identifier` (VARCHAR): Subsection label (e.g., "3.1.1")
- `raw_text` (TEXT): Original extracted text
- `cleaned_text` (TEXT): Normalized/cleaned version
- `source_page` (INTEGER): Page number in source document
- `source_paragraph` (INTEGER): Paragraph number on page
- `embedding` (vector(384)): Sentence transformer embedding for semantic search
- `chunk_type` (VARCHAR): Type of content (paragraph, table, list, header)
- `confidence_score` (VARCHAR): Extraction confidence

**Indexes:**
- `idx_text_chunks_document_id`: Find chunks by document
- `idx_text_chunks_section`: Filter by section
- `idx_text_chunks_embedding` (ivfflat): Vector similarity search

**Embedding Strategy:**
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Enables semantic search across requirements
- Future: Upgrade to OpenAI embeddings (1536 dimensions)

#### 3. **requirements**
Extracted requirements with AI classification and validation status.

**Key Fields:**
- `id` (UUID): Primary key
- `document_id` (UUID): Source document
- `source_chunk_id` (UUID): Source text chunk
- `raw_text` (TEXT): Original requirement text
- `clean_text` (TEXT): Human-edited version
- `classification` (VARCHAR): Requirement type
  - `PERFORMANCE_REQUIREMENT`
  - `COMPLIANCE_REQUIREMENT`
  - `DELIVERABLE_REQUIREMENT`
  - `EVALUATION_CRITERIA`
  - `INSTRUCTION`
  - `FAR_CLAUSE`
  - `OTHER`
- `source_page` (INTEGER): Page number
- `source_section` (VARCHAR): Section identifier
- `ai_confidence_score` (VARCHAR): AI confidence (low, medium, high)
- `extraction_method` (VARCHAR): Processing engine used
- `status` (VARCHAR): Validation status
  - `ai_extracted`: Initial AI extraction
  - `human_validated`: Approved by human
  - `human_corrected`: Modified by human
  - `flagged_for_review`: Needs expert review
- `validation_notes` (TEXT): Human reviewer comments
- `history` (JSONB): Immutable audit trail
- `validated_by` (VARCHAR): User who validated
- `validated_at` (TIMESTAMPTZ): Validation timestamp

**Indexes:**
- `idx_requirements_document_id`: Find by document
- `idx_requirements_status`: Filter by validation status
- `idx_requirements_classification`: Filter by type
- `idx_requirements_source_chunk`: Link to source text

**Audit Trail (history field):**
```json
[
  {
    "timestamp": "2025-10-05T14:32:10Z",
    "action": "approve",
    "user": "john.doe@agency.gov",
    "previous_status": "ai_extracted",
    "previous_clean_text": "Original text",
    "previous_classification": "OTHER",
    "notes": "Confirmed as performance requirement"
  }
]
```

#### 4. **cross_references**
Links between requirements and related document sections.

**Key Fields:**
- `id` (UUID): Primary key
- `requirement_id` (UUID): Source requirement
- `target_chunk_id` (UUID): Referenced text chunk
- `reference_type` (VARCHAR): Type of reference (attachment, section, clause, instruction)
- `reference_text` (TEXT): The actual reference text
- `reference_target` (VARCHAR): Target identifier (e.g., "Attachment 3", "Section M.2.1")
- `confidence_score` (VARCHAR): Resolution confidence
- `similarity_score` (VARCHAR): Vector similarity score
- `created_by` (VARCHAR): System or user identifier

**Use Cases:**
- Resolve references like "See Attachment 3"
- Link evaluation criteria to requirements
- Build requirement dependency graph

#### 5. **processing_jobs**
Tracks asynchronous background processing tasks.

**Key Fields:**
- `id` (UUID): Job identifier
- `document_id` (UUID): Associated document
- `job_type` (VARCHAR): extraction, validation, cross_reference
- `status` (VARCHAR): pending, running, completed, failed
- `total_items` (INTEGER): Total items to process
- `processed_items` (INTEGER): Completed items
- `error_count` (INTEGER): Number of errors
- `error_message` (TEXT): Human-readable error
- `error_details` (JSONB): Detailed error information
- `created_at`, `started_at`, `completed_at`: Timing information

**Enables:**
- Real-time progress tracking in UI
- Error recovery and retry logic
- Performance monitoring

#### 6. **user_sessions**
User authentication and session management (future implementation).

**Key Fields:**
- `id` (UUID): Session identifier
- `user_id` (VARCHAR): User identifier
- `session_token` (VARCHAR): Secure session token
- `user_email` (VARCHAR): User email
- `user_role` (VARCHAR): User role (admin, validator, viewer)
- `created_at`, `expires_at`, `last_activity`: Session lifecycle

### Row Level Security (RLS)

All tables have RLS enabled. Current policies are permissive for development:

```sql
-- Current development policy (INSECURE - replace in production)
CREATE POLICY "Allow all operations for development"
ON documents FOR ALL
USING (true) WITH CHECK (true);
```

**Production RLS Requirements:**
- Restrict access based on `auth.uid()`
- Implement role-based access control (RBAC)
- Audit all data access
- Example production policy:
```sql
CREATE POLICY "Users can view own documents"
ON documents FOR SELECT
TO authenticated
USING (uploaded_by = auth.uid());
```

---

## Application Components

### Backend API (FastAPI)

#### Core Modules

**1. main.py** - FastAPI Application
- **Purpose**: Main API server with RESTful endpoints
- **Key Endpoints**:
  - `GET /health` - System health check
  - `POST /documents/upload` - Upload and process document
  - `GET /documents` - List all documents
  - `GET /documents/{id}` - Get document with requirements
  - `GET /documents/{id}/stats` - Document statistics
  - `GET /requirements/review_queue` - Validation queue
  - `PUT /requirements/{id}` - Update requirement
  - `POST /search` - Search requirements
  - `GET /documents/{id}/compliance-matrix` - Generate compliance report
  - `GET /stats` - System-wide statistics

**Features:**
- CORS middleware for cross-origin requests
- Pydantic schemas for request/response validation
- SQLAlchemy ORM for database operations
- Background task processing with BackgroundTasks
- Comprehensive error handling with HTTP status codes

**2. models.py** - SQLAlchemy ORM Models
- **Purpose**: Database models and enums
- **Key Models**: Document, TextChunk, Requirement, CrossReference, ProcessingJob, UserSession
- **Enums**: ProcessingStatus, RequirementClassification, ValidationStatus
- **Features**:
  - UUID primary keys
  - Relationship definitions
  - Index definitions for performance
  - Optional pgvector support with SQLite fallback

**3. schemas.py** - Pydantic Validation Schemas
- **Purpose**: API request/response validation
- **Key Schemas**:
  - DocumentResponse, RequirementResponse
  - ReviewQueueResponse, ValidationRequest
  - SearchRequest, SearchResponse
  - ComplianceMatrixResponse
  - SystemStats, HealthCheckResponse
- **Features**:
  - Field validation with min/max constraints
  - Custom validators
  - JSON serialization with datetime formatting
  - ORM integration with `from_attributes = True`

**4. database.py** - Database Connection Management
- **Purpose**: Connection pooling, session management, health checks
- **Key Functions**:
  - `get_db()`: Dependency injection for FastAPI
  - `get_db_session()`: Context manager for background tasks
  - `init_database()`: Create tables and extensions
  - `health_check()`: Comprehensive health status
- **Features**:
  - Dual support for SQLite (development) and PostgreSQL (production)
  - Automatic pgvector extension setup
  - Connection pooling with pre-ping
  - Database manager class for maintenance operations

**5. document_processor.py** - Document Processing Pipeline
- **Purpose**: Core document extraction and chunking logic
- **Key Classes**: DocumentProcessor
- **Processing Pipeline**:
  1. File type detection and engine selection
  2. Text extraction (PyMuPDF, Unstructured.io, Document AI)
  3. Intelligent chunking with RFP-aware segmentation
  4. Embedding generation (sentence transformers)
  5. Requirement extraction and classification
  6. Database persistence

**Extraction Engines:**
- **PyMuPDF** (Primary): Fast, cost-effective PDF extraction
- **Unstructured.io** (Fallback): Complex layout handling
- **Document AI** (Future): Google Cloud high-fidelity OCR

**Chunking Strategy:**
- Split by page markers
- Detect RFP sections (Section A, B, C, etc.)
- Segment by paragraphs and bullet points
- Preserve source location metadata (page, paragraph, line)
- Minimum chunk size: 50 characters
- Maximum chunk size: ~2000 characters (configurable)

**Classification Logic:**
- **Pattern-based**: Regex patterns for requirement indicators
  - "shall", "must", "required to"
  - Performance indicators: "uptime", "response time", "latency"
  - Compliance indicators: "FISMA", "NIST", "encryption"
  - Deliverable indicators: "submit", "provide", "deliver"
- **AI-based** (Optional): OpenAI GPT-3.5 for advanced classification
- **Confidence scoring**: Low/Medium/High based on pattern matches

**6. Additional Backend Modules**

**backend/document_parser.py**:
- Lightweight parser for simple document types
- Methods: `parse_pdf()`, `parse_docx()`, `parse_text()`
- Used by simplified backend API

**backend/requirement_extractor.py**:
- Pattern-based requirement extraction
- Three classification patterns:
  - `PERFORMANCE_REQUIREMENT`: Uptime, response time, latency patterns
  - `COMPLIANCE_REQUIREMENT`: Security standards, encryption, audit
  - `DELIVERABLE_REQUIREMENT`: Submission, reporting, documentation
- Confidence scoring based on pattern matches
- Section/subsection tracking

**backend/main.py** (Simplified API):
- Alternative lightweight FastAPI implementation
- Direct Supabase integration without SQLAlchemy
- Endpoints:
  - `POST /documents/upload`: Upload and extract requirements
  - `GET /documents`: List documents
  - `GET /documents/{id}`: Get document with requirements
  - `GET /documents/{id}/stats`: Statistics
  - `PATCH /requirements/{id}`: Update requirement status

### Frontend Applications

#### Option 1: React SPA (frontend/)

**Technology Stack:**
- React 18 with Hooks
- Vite for development and bundling
- Axios for HTTP requests
- Modern CSS with no framework dependencies

**Key Components:**

**App.jsx** - Main Application Component
- **State Management**:
  - `documents`: List of uploaded documents
  - `selectedDoc`: Currently selected document
  - `requirements`: Requirements for selected document
  - `stats`: Document statistics
  - `uploading`, `loading`: UI state flags

**Features:**
- **Document Upload**: Drag-and-drop file upload with progress indication
- **Document List**: Sidebar with all uploaded documents
- **Requirement Display**: Card-based layout with classification badges
- **Validation Actions**: Validate or reject individual requirements
- **Statistics Dashboard**: Real-time counts by classification and status

**API Integration:**
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Upload document
await axios.post(`${API_URL}/documents/upload`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

// Get document with requirements
const [docResponse, statsResponse] = await Promise.all([
  axios.get(`${API_URL}/documents/${docId}`),
  axios.get(`${API_URL}/documents/${docId}/stats`)
]);

// Update requirement status
await axios.patch(`${API_URL}/requirements/${reqId}`, null, {
  params: { status, validated_by: 'user' }
});
```

**UI/UX Features:**
- Color-coded classification badges:
  - Performance: Green (#10b981)
  - Compliance: Orange (#f59e0b)
  - Deliverable: Blue (#3b82f6)
- Confidence percentage display
- Empty states with helpful messages
- Loading states during async operations
- Responsive layout (sidebar + main content)

**Configuration:**
- Environment variables in `.env`:
  ```
  VITE_API_URL=http://localhost:8000
  VITE_SUPABASE_URL=<your-supabase-url>
  VITE_SUPABASE_ANON_KEY=<your-key>
  ```

#### Option 2: Streamlit Console (streamlit_app.py)

**Purpose**: Internal validation console for proposal managers

**Key Features:**
- **Review Queue Tab**: Priority-ordered requirements for validation
  - Low confidence requirements first
  - Inline editing of clean text and classification
  - Action buttons: Approve, Correct & Approve, Flag
  - Filtering by confidence and classification
- **Documents Tab**: Upload and browse documents
  - File uploader with drag-and-drop
  - Document list with status indicators
  - Processing status tracking
- **Search Tab**: Text-based requirement search
  - Full-text search across all requirements
  - Result display with context
- **Analytics Tab**: System-wide statistics
  - Document status distribution
  - Classification breakdown
  - Validation progress metrics
  - System health monitoring

**Custom Styling:**
- Custom CSS for professional appearance
- Color-coded confidence levels (high/medium/low)
- Status badges for validation status
- Card-based layout for requirements

**API Integration:**
```python
API_BASE_URL = "http://localhost:8000"

def get_api_data(endpoint: str, params: Dict = None) -> Optional[Dict]:
    response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
    return response.json()

def put_api_data(endpoint: str, data: Dict) -> Optional[Dict]:
    response = requests.put(f"{API_BASE_URL}{endpoint}", json=data)
    return response.json()
```

**Validation Workflow:**
1. Load review queue from `/requirements/review_queue`
2. Display requirement with source information
3. Allow editing of clean_text and classification
4. Submit validation action (approve/correct/flag)
5. Update requirement via `PUT /requirements/{id}`
6. Reload queue and show next item

---

## Data Flow and Processing

### Document Upload Flow

```
┌──────────────┐
│  User Upload │
│  (PDF/DOCX)  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  POST /documents/upload              │
│                                      │
│  1. Validate file (type, size)      │
│  2. Generate UUIDs (doc, job)       │
│  3. Save file to uploads/           │
│  4. Create document record          │
│  5. Create processing job           │
│  6. Trigger background processing   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Background: process_document_async()│
│                                      │
│  1. Update job status: running      │
│  2. Select processing engine        │
│  3. Extract text (PyMuPDF/etc)      │
│  4. Intelligent chunking            │
│  5. Generate embeddings             │
│  6. Store text_chunks               │
│  7. Extract requirements            │
│  8. Classify requirements           │
│  9. Store requirements              │
│  10. Update doc status: completed   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Database State                      │
│                                      │
│  • Document: status=completed        │
│  • TextChunks: N chunks with vectors │
│  • Requirements: M requirements      │
│  • ProcessingJob: status=completed   │
└──────────────────────────────────────┘
```

### Human Validation Flow

```
┌──────────────────────┐
│  Validator opens UI  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  GET /requirements/review_queue      │
│                                      │
│  • Filter: status=ai_extracted      │
│  • Order: confidence ASC            │
│  • Paginate: 20 per page            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  UI displays requirement             │
│                                      │
│  • Raw text (read-only)             │
│  • Clean text (editable)            │
│  • Classification (dropdown)        │
│  • Source info (page, section)      │
│  • Confidence score                 │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Validator takes action              │
│                                      │
│  [Approve] → no changes             │
│  [Correct] → edited text/class      │
│  [Flag] → needs expert review       │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PUT /requirements/{id}              │
│                                      │
│  1. Load requirement from DB        │
│  2. Create audit history entry      │
│  3. Update fields based on action   │
│     - approve: status=validated     │
│     - correct: status=corrected     │
│     - flag: status=flagged          │
│  4. Add validation_notes            │
│  5. Set validated_by, validated_at  │
│  6. Commit to database              │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  UI updates                          │
│                                      │
│  • Show success message             │
│  • Remove from review queue         │
│  • Load next requirement            │
│  • Update statistics                │
└──────────────────────────────────────┘
```

### Search Flow (Semantic + Text)

```
┌──────────────────────┐
│  User enters query   │
│  "99.9% uptime"      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  POST /search                        │
│                                      │
│  Input:                              │
│  {                                   │
│    "query": "99.9% uptime",         │
│    "limit": 20,                     │
│    "document_ids": [...],           │
│    "classifications": [...]         │
│  }                                   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Current: Text search                │
│                                      │
│  SELECT * FROM requirements          │
│  WHERE raw_text ILIKE '%99.9%' OR    │
│        clean_text ILIKE '%uptime%'   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Future: Vector search               │
│                                      │
│  1. Generate query embedding         │
│  2. Vector similarity search         │
│     SELECT *,                        │
│       1 - (embedding <=> $1) AS sim  │
│     FROM requirements                │
│     ORDER BY sim DESC                │
│     LIMIT 20                         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Return results                      │
│                                      │
│  {                                   │
│    "results": [                     │
│      {                              │
│        "id": "...",                 │
│        "raw_text": "...",           │
│        "classification": "...",     │
│        "similarity_score": 0.85     │
│      }                              │
│    ],                               │
│    "total_count": 15                │
│  }                                   │
└──────────────────────────────────────┘
```

---

## API Reference

### Document Endpoints

#### POST /documents/upload
Upload and process a new document.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (binary)

**Response:**
```json
{
  "job_id": "uuid",
  "document_id": "uuid",
  "message": "Document uploaded successfully",
  "status": "processing"
}
```

**Status Codes:**
- 201: Created
- 400: Invalid file type or empty file
- 413: File too large (>100MB)
- 500: Server error

#### GET /documents
List all documents with pagination.

**Query Parameters:**
- `skip` (int, default=0): Offset for pagination
- `limit` (int, default=50, max=200): Items per page
- `status_filter` (string, optional): Filter by ProcessingStatus

**Response:**
```json
[
  {
    "id": "uuid",
    "filename": "rfp_2025.pdf",
    "file_type": "pdf",
    "file_size": 2048576,
    "status": "completed",
    "uploaded_at": "2025-10-05T14:30:00Z",
    "processed_at": "2025-10-05T14:32:15Z"
  }
]
```

#### GET /documents/{document_id}/status
Get processing status of a document.

**Response:**
```json
{
  "document_id": "uuid",
  "status": "processing",
  "uploaded_at": "2025-10-05T14:30:00Z",
  "processed_at": null,
  "job": {
    "job_id": "uuid",
    "status": "running",
    "total_items": 150,
    "processed_items": 75,
    "error_count": 0
  }
}
```

#### GET /documents/{document_id}/stats
Get statistics for a document.

**Response:**
```json
{
  "document_id": "uuid",
  "total_chunks": 145,
  "total_requirements": 78,
  "requirements_by_classification": {
    "PERFORMANCE_REQUIREMENT": 25,
    "COMPLIANCE_REQUIREMENT": 30,
    "DELIVERABLE_REQUIREMENT": 23
  },
  "validation_status_counts": {
    "ai_extracted": 20,
    "human_validated": 50,
    "human_corrected": 8
  },
  "processing_time_seconds": 45.3
}
```

### Requirement Endpoints

#### GET /requirements/review_queue
Get requirements pending validation.

**Query Parameters:**
- `skip`, `limit`: Pagination
- `confidence_filter` (string): "low", "medium", "high"
- `classification_filter` (string): RequirementClassification enum

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "document_id": "uuid",
      "raw_text": "The system shall maintain 99.9% uptime",
      "clean_text": "System uptime shall be 99.9%",
      "classification": "PERFORMANCE_REQUIREMENT",
      "ai_confidence_score": "medium",
      "source_page": 12,
      "source_section": "Section C",
      "status": "ai_extracted"
    }
  ],
  "total_count": 45,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

#### PUT /requirements/{requirement_id}
Update and validate a requirement.

**Request Body:**
```json
{
  "action": "approve",  // or "correct", "flag"
  "clean_text": "Updated text",  // optional
  "classification": "PERFORMANCE_REQUIREMENT",  // optional
  "validation_notes": "Confirmed as performance req"  // optional
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "human_validated",
  "clean_text": "Updated text",
  "validated_by": "system",
  "validated_at": "2025-10-05T14:45:00Z",
  "history": [
    {
      "timestamp": "2025-10-05T14:45:00Z",
      "action": "approve",
      "user": "system",
      "previous_status": "ai_extracted"
    }
  ]
}
```

### Search and Analytics Endpoints

#### POST /search
Search requirements.

**Request Body:**
```json
{
  "query": "security encryption",
  "document_ids": ["uuid1", "uuid2"],  // optional
  "classifications": ["COMPLIANCE_REQUIREMENT"],  // optional
  "statuses": ["human_validated"],  // optional
  "limit": 50
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "document_id": "uuid",
      "raw_text": "All data shall be encrypted using AES-256",
      "classification": "COMPLIANCE_REQUIREMENT",
      "source_page": 8,
      "similarity_score": 0.87
    }
  ],
  "total_count": 12,
  "query": "security encryption"
}
```

#### GET /stats
Get system-wide statistics.

**Response:**
```json
{
  "total_documents": 25,
  "total_requirements": 1250,
  "total_chunks": 3420,
  "documents_by_status": {
    "uploaded": 2,
    "processing": 1,
    "completed": 22
  },
  "requirements_by_classification": {
    "PERFORMANCE_REQUIREMENT": 450,
    "COMPLIANCE_REQUIREMENT": 380,
    "DELIVERABLE_REQUIREMENT": 420
  },
  "validation_status_counts": {
    "ai_extracted": 300,
    "human_validated": 800,
    "human_corrected": 150
  },
  "system_health": {
    "database_connection": true,
    "tables_exist": true,
    "pgvector_available": true
  }
}
```

#### GET /health
System health check.

**Response:**
```json
{
  "status": "healthy",
  "database_connection": true,
  "tables_exist": true,
  "pgvector_available": true,
  "timestamp": "2025-10-05T14:50:00Z"
}
```

#### GET /documents/{document_id}/compliance-matrix
Generate compliance matrix.

**Response:**
```json
{
  "document_id": "uuid",
  "document_name": "RFP_2025.pdf",
  "items": [
    {
      "requirement_id": "uuid",
      "requirement_text": "System shall maintain 99.9% uptime",
      "classification": "PERFORMANCE_REQUIREMENT",
      "source_section": "Section C",
      "source_page": 12,
      "cross_references": ["Section M.2.1"],
      "status": "human_validated"
    }
  ],
  "total_requirements": 78,
  "validated_requirements": 60,
  "pending_requirements": 18,
  "generated_at": "2025-10-05T14:55:00Z"
}
```

---

## Deployment Architecture

### Local Development Setup

**Prerequisites:**
- Python 3.11+
- Node.js 18+ (for React frontend)
- Supabase account
- PostgreSQL with pgvector (via Supabase)

**Environment Configuration:**

**.env (root)**
```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Database (automatically configured by Supabase)
DATABASE_URL=postgresql://user:pass@host:5432/db

# Optional: OpenAI for advanced classification
OPENAI_API_KEY=sk-...
```

**backend/.env**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

**frontend/.env**
```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

**Start Commands:**

```bash
# Terminal 1: Main FastAPI backend
cd /project/root
python -m uvicorn main:app --reload --port 8000

# Terminal 2: React frontend
cd frontend
npm run dev  # Runs on http://localhost:5173

# Terminal 3 (Optional): Streamlit console
streamlit run streamlit_app.py  # Runs on http://localhost:8501

# Alternative: Simplified backend
cd backend
uvicorn main:app --reload --port 8000
```

### Production Deployment

**Recommended Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer / CDN                   │
│                    (Cloudflare, AWS)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
┌────────▼──────┐  ┌──────▼───────┐
│  React Frontend│  │FastAPI Backend│
│  (Vercel/      │  │(Render/Railway)│
│   Netlify)     │  │  (Docker)      │
└────────────────┘  └──────┬─────────┘
                           │
                   ┌───────▼────────┐
                   │    Supabase    │
                   │  (PostgreSQL + │
                   │    Storage)    │
                   └────────────────┘
```

**Backend Deployment Options:**

1. **Railway** (Recommended for MVP)
   - Dockerfile-based deployment
   - Automatic HTTPS
   - Built-in monitoring
   - Environment variable management
   - Cost: ~$5-20/month

2. **Render**
   - Free tier available
   - Docker support
   - Auto-deploy from Git
   - Cost: Free - $25/month

3. **AWS ECS/Fargate**
   - Enterprise-grade scalability
   - VPC isolation
   - Load balancing
   - Cost: Variable (~$50-200/month)

**Dockerfile for Backend:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Deployment Options:**

1. **Vercel** (Recommended for React)
   - Native Vite support
   - Automatic deployments
   - Built-in analytics
   - Cost: Free - $20/month

2. **Netlify**
   - Similar to Vercel
   - Form handling
   - Cost: Free - $19/month

**Database: Supabase**
- Managed PostgreSQL with pgvector
- Automatic backups
- Built-in authentication (future use)
- File storage buckets
- Cost: Free tier (500MB), Pro $25/month

### Security Considerations

**Production Checklist:**

- [ ] **Replace RLS policies** with restrictive rules
- [ ] **Enable authentication** (Supabase Auth)
- [ ] **Use HTTPS only** for all endpoints
- [ ] **Set CORS origins** to specific domains
- [ ] **Rotate Supabase keys** to service role for backend
- [ ] **Enable rate limiting** on API endpoints
- [ ] **Implement input sanitization** for all user inputs
- [ ] **Enable SQL injection protection** (Supabase handles this)
- [ ] **Add API key authentication** for sensitive endpoints
- [ ] **Implement user session management**
- [ ] **Add request logging and monitoring**
- [ ] **Set up error tracking** (Sentry, Rollbar)

**Environment Variables (Production):**
```bash
# Backend
DATABASE_URL=<supabase-postgres-url>
SUPABASE_URL=<your-prod-url>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>  # NOT anon key
OPENAI_API_KEY=<your-key>
ENVIRONMENT=production
LOG_LEVEL=info

# Frontend
VITE_API_URL=https://api.yourdomain.com
VITE_SUPABASE_URL=<your-prod-url>
VITE_SUPABASE_ANON_KEY=<anon-key>  # Safe for frontend
```

---

## Future Enhancements

### Phase 2: Advanced AI Features

1. **OpenAI GPT Integration**
   - Replace rule-based classification with GPT-4
   - Intelligent requirement summarization
   - Automated cross-reference resolution
   - Question answering over documents

2. **Vector Semantic Search**
   - Upgrade to OpenAI embeddings (1536d)
   - Hybrid search (text + vector)
   - Similar requirement detection
   - Automatic duplicate identification

3. **Knowledge Graph**
   - Build requirement dependency graph
   - Visualize relationships between requirements
   - Impact analysis for changes
   - Export to Neo4j or visualization tools

### Phase 3: Collaboration and Workflow

1. **Multi-User Authentication**
   - Supabase Auth integration
   - Role-based access control (Admin, Validator, Viewer)
   - User-specific validation queues
   - Assignment and workload distribution

2. **Collaborative Validation**
   - Real-time collaboration (multiple validators)
   - Comment threads on requirements
   - @mentions and notifications
   - Validation approval workflow

3. **Export and Integration**
   - Excel/CSV export with formatting
   - PDF report generation
   - API webhooks for external systems
   - Integration with proposal management tools

### Phase 4: Enterprise Features

1. **Advanced Analytics**
   - Processing time trends
   - Validation accuracy metrics
   - User productivity dashboards
   - Document complexity scoring

2. **Batch Processing**
   - Multi-document upload
   - Bulk validation operations
   - Scheduled processing jobs
   - Priority queue management

3. **Compliance and Audit**
   - Detailed audit logs
   - Export compliance reports
   - Role-based data access logs
   - FISMA/FedRAMP compliance preparation

4. **Performance Optimization**
   - Redis caching layer
   - Background job queue (Celery)
   - CDN for document serving
   - Database query optimization

---

## Testing Strategy

### Unit Tests
- **Database Models**: Test CRUD operations, relationships
- **API Endpoints**: Test request/response validation
- **Document Processing**: Test extraction, chunking, classification
- **Authentication**: Test user permissions, session management

### Integration Tests
- **End-to-End Flows**: Upload → Process → Validate
- **Database Transactions**: Test rollback, commit, consistency
- **External APIs**: Mock OpenAI, Supabase responses

### Performance Tests
- **Load Testing**: 100+ concurrent document uploads
- **Database Queries**: Optimize slow queries (>100ms)
- **Vector Search**: Benchmark search latency
- **Memory Profiling**: Monitor memory usage during processing

### Test Files Created
- `test_system.py`: Comprehensive integration tests
- `test_system_simple.py`: Basic sanity checks
- `test_rfp.txt`, `test_rfp_realistic.txt`: Sample RFP documents

---

## Maintenance and Operations

### Monitoring

**Key Metrics:**
- API response times (p50, p95, p99)
- Database connection pool utilization
- Document processing success rate
- Validation queue size
- Error rates by endpoint

**Tools:**
- Supabase Dashboard: Database metrics
- FastAPI built-in docs: API testing
- Custom health check endpoint: System status
- Log aggregation: Structured logging to file/service

### Backup and Recovery

**Database Backups:**
- Supabase automatic daily backups (retained 7 days)
- Point-in-time recovery available
- Manual backup: `pg_dump` via Supabase CLI

**File Storage:**
- Documents stored in Supabase Storage
- Automatic replication across zones
- Versioning enabled for file recovery

### Common Maintenance Tasks

**Database Maintenance:**
```bash
# Run vacuum (Supabase auto-vacuums)
# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Reindex for performance
REINDEX INDEX CONCURRENTLY idx_text_chunks_embedding;
```

**Clean Up Old Data:**
```python
# Programmatically delete old sessions
db_manager.cleanup_old_sessions(days_old=30)

# Delete test documents
DELETE FROM documents WHERE uploaded_by = 'test_user';
```

### Troubleshooting

**Common Issues:**

1. **"No text extracted from document"**
   - Cause: Scanned PDF without OCR
   - Solution: Use Document AI engine or pre-process with OCR

2. **"Database connection failed"**
   - Cause: Invalid DATABASE_URL or network issue
   - Solution: Check environment variables, verify Supabase project status

3. **"Vector index not found"**
   - Cause: pgvector extension not enabled
   - Solution: Run `CREATE EXTENSION vector;` in Supabase SQL editor

4. **"Requirement classification is always OTHER"**
   - Cause: Patterns not matching document text
   - Solution: Review regex patterns, enable OpenAI classification

---

## Appendix

### A. Database Schema SQL

See `/supabase/migrations/20250930213419_create_rfp_extraction_schema.sql` for complete schema.

### B. API Response Examples

See API Reference section above.

### C. Configuration Files

**requirements.txt** (root)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.0
PyMuPDF==1.23.8
python-docx==1.1.0
PyPDF2==3.0.1
sentence-transformers==2.2.2
openai==1.3.0
pgvector==0.2.4
streamlit==1.28.0
requests==2.31.0
```

**backend/requirements.txt** (simplified backend)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
supabase==2.0.3
pydantic==2.5.0
python-dotenv==1.0.0
PyPDF2==3.0.1
python-docx==1.1.0
```

**frontend/package.json**
```json
{
  "name": "rfp-extractor-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
```

### D. Glossary

- **RFP**: Request for Proposal - Government solicitation document
- **RLS**: Row Level Security - PostgreSQL security feature
- **ORM**: Object-Relational Mapping - SQLAlchemy
- **Embedding**: Numerical vector representation of text
- **pgvector**: PostgreSQL extension for vector similarity search
- **Human-in-the-Loop**: Workflow requiring human validation
- **Audit Trail**: Immutable history of all data changes
- **Confidence Score**: AI certainty level (low/medium/high)
- **Classification**: Requirement type categorization
- **Chunking**: Splitting documents into semantic segments
- **Cross-Reference**: Link between related document sections

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-05 | System | Initial comprehensive as-built documentation |

---

**End of Document**
