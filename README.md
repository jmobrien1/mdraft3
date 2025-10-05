# RFP Requirement Extractor

AI-powered requirement extraction and classification from RFP (Request for Proposal) documents.

## Features

- Upload PDF, DOCX, and TXT documents
- Automatic requirement extraction using pattern matching
- Classify requirements into:
  - Performance Requirements
  - Compliance Requirements
  - Deliverable Requirements
- Human validation workflow
- Real-time statistics and tracking
- Persistent storage with Supabase

## Tech Stack

### Backend
- FastAPI (REST API)
- Supabase (PostgreSQL + Storage)
- PyPDF2 & python-docx (Document parsing)
- Pattern-based extraction

### Frontend
- React
- Vite
- Axios
- Modern responsive UI

## Quick Start

### 1. Clone and Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
cp ../.env .env

# Frontend
cd ../frontend
npm install
cp ../.env .env
```

### 2. Run Locally

Terminal 1 (Backend):
```bash
cd backend
uvicorn main:app --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Visit http://localhost:5173

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   React     │─────>│   FastAPI    │─────>│   Supabase   │
│   Frontend  │      │   Backend    │      │   Database   │
└─────────────┘      └──────────────┘      └──────────────┘
                            │
                            v
                     ┌──────────────┐
                     │   Supabase   │
                     │   Storage    │
                     └──────────────┘
```

## API Endpoints

- `GET /` - Health check
- `GET /documents` - List all documents
- `POST /documents/upload` - Upload and process document
- `GET /documents/{id}` - Get document with requirements
- `GET /documents/{id}/stats` - Get document statistics
- `PATCH /requirements/{id}` - Update requirement status

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

Quick deploy options:
- **Backend**: Railway, Render, or Docker
- **Frontend**: Vercel or Netlify

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── document_parser.py   # PDF/DOCX parsing
│   ├── requirement_extractor.py  # Extraction logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   └── App.css         # Styles
│   └── package.json        # Node dependencies
└── .env                    # Environment variables
```

## Database Schema

### documents
- id, filename, file_path, file_size, file_type, mime_type
- status, uploaded_by, uploaded_at, processed_at

### requirements
- id, document_id, source_chunk_id
- raw_text, clean_text, classification
- source_section, source_subsection
- ai_confidence_score, status
- validated_by, validated_at

## Requirement Classification

The system uses pattern matching to classify requirements:

### Performance Requirements
- Uptime percentages (99.9%)
- Response times
- Processing speeds
- Latency requirements

### Compliance Requirements
- Security standards (FISMA, NIST, ISO)
- Encryption requirements
- Audit requirements
- Authentication standards

### Deliverable Requirements
- Reports and documentation
- Submission deadlines
- Deliverable schedules

## Future Enhancements

- [ ] OpenAI GPT integration for better extraction
- [ ] Semantic search with embeddings
- [ ] Export to Excel/PDF
- [ ] Multi-user authentication
- [ ] Requirement dependency mapping
- [ ] Batch document processing
- [ ] API webhooks for integrations
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Start the Streamlit frontend (in a new terminal):**
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

5. **Access the applications:**
- **API Documentation**: http://localhost:8000/docs
- **Streamlit App**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

## 📋 Core Features

### Document Processing Pipeline
1. **Upload**: Accept PDF/DOCX files via web interface or API
2. **Extraction**: Dual-engine processing with automatic escalation
3. **Chunking**: Intelligent text segmentation preserving RFP structure
4. **Classification**: AI-powered requirement categorization
5. **Validation**: Human review and correction workflow

### Human-in-the-Loop Workflow
- **Review Queue**: Requirements ordered by AI confidence (lowest first)
- **Validation Interface**: Side-by-side source document and editable form
- **Audit Trail**: Complete history of all changes and approvals
- **Batch Operations**: Efficient processing of multiple requirements

### Compliance Features
- **Full Traceability**: Every piece of data linked to source file, page, paragraph
- **Immutable History**: Complete audit trail for protest defense
- **Status Tracking**: Document and requirement processing status
- **Export Capabilities**: Compliance matrices and structured data export

## 🔧 Configuration

### Database Configuration
The system automatically detects the database type:
- **Development**: SQLite (default) - `sqlite:///./rfp_extraction.db`
- **Production**: PostgreSQL with pgvector - Set `DATABASE_URL` environment variable

### Environment Variables
```bash
# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost:5432/rfp_extraction

# Google Cloud (for Document AI)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# OpenAI (for embeddings and classification)
OPENAI_API_KEY=your-openai-api-key
```

## 📊 API Endpoints

### Core Endpoints
- `POST /documents/upload` - Upload documents for processing
- `GET /documents/{id}/status` - Check processing status
- `GET /requirements/review_queue` - Get requirements pending validation
- `PUT /requirements/{id}` - Update requirement with human validation
- `POST /search` - Semantic search requirements
- `GET /documents/{id}/compliance-matrix` - Generate compliance matrix

### Health & Statistics
- `GET /health` - System health check
- `GET /stats` - System-wide statistics
- `GET /documents/{id}/stats` - Document-specific statistics

## 🎨 Streamlit Interface

### Review Queue Tab
- **Prioritized List**: Requirements ordered by AI confidence
- **Validation Interface**: Edit clean text, classification, and notes
- **Action Buttons**: Approve, Correct & Approve, or Flag for Review
- **Filters**: Filter by confidence level and classification

### Documents Tab
- **Upload Interface**: Drag-and-drop file upload
- **Document List**: View all uploaded documents with status
- **Processing Status**: Real-time processing progress

### Search Tab
- **Semantic Search**: Find related requirements across documents
- **Results Display**: Highlighted search results with context

### Analytics Tab
- **System Statistics**: Document counts, processing metrics
- **Health Monitoring**: Database and system status
- **Performance Metrics**: Processing times and success rates

## 🔒 Security & Compliance

### Data Security
- **Secure File Handling**: Temporary file storage with cleanup
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Graceful error handling with audit logging

### Compliance Features
- **Audit Trail**: Complete history of all data transformations
- **Source Traceability**: Every requirement linked to source location
- **Status Tracking**: Document and requirement processing status
- **Export Capabilities**: Structured data export for compliance reporting

## 🚧 Development Status

### ✅ Completed
- [x] Database schema with full audit trail
- [x] FastAPI backend with core endpoints
- [x] Streamlit correction console
- [x] Document upload and status tracking
- [x] Human validation workflow
- [x] System health monitoring
- [x] SQLite compatibility for development

### 🚧 In Progress
- [ ] Document processing pipeline implementation
- [ ] AI classification and extraction
- [ ] Vector similarity search
- [ ] Cross-reference resolution

### 📋 Planned
- [ ] Google Document AI integration
- [ ] Advanced analytics and reporting
- [ ] Batch processing capabilities
- [ ] Export to Excel/CSV
- [ ] User authentication and authorization
- [ ] Production deployment configuration

## 🤝 Contributing

This is a development implementation of the RFP extraction platform. The system is designed to be:

- **Modular**: Each component can be developed and tested independently
- **Extensible**: Easy to add new processing engines and AI models
- **Scalable**: Designed for production deployment with proper configuration
- **Compliant**: Built with government contracting requirements in mind

## 📄 License

This project implements the strategic blueprint outlined in the RFP document for building an AI-powered RFP extraction and analysis platform.

---

**Note**: This is a development implementation. For production deployment, ensure proper security configuration, database setup, and Google Cloud integration as outlined in the original RFP blueprint.

