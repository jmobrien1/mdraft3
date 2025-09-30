# Setup Instructions - RFP Extraction Platform

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 2GB free disk space
- Internet connection

---

## Step-by-Step Setup Guide

### Step 1: Download the Project

If you haven't already, get the project files to your local machine:

```bash
# Navigate to your project directory
cd /path/to/your/project
# Example: cd ~/mdraft3
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 3: Upgrade pip

```bash
# Make sure pip is up to date
pip install --upgrade pip
```

### Step 4: Install Dependencies

```bash
# Install all required packages (this may take 5-10 minutes)
pip install -r requirements.txt

# If you get errors, try installing in batches:
# Batch 1: Core dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary

# Batch 2: Document processing
pip install python-docx pymupdf

# Batch 3: AI/ML
pip install openai sentence-transformers

# Batch 4: Frontend
pip install streamlit

# Batch 5: Others
pip install python-dotenv requests pandas pydantic
```

**Common Installation Issues:**

**Issue:** `error: Microsoft Visual C++ 14.0 or greater is required` (Windows)
```bash
# Install Visual C++ Build Tools from:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or install pre-built wheels:
pip install --only-binary :all: psycopg2-binary
```

**Issue:** `Failed building wheel for numpy`
```bash
# Install pre-built versions
pip install --upgrade pip setuptools wheel
pip install numpy --only-binary :all:
```

**Issue:** Out of memory during torch installation
```bash
# Install CPU-only version of PyTorch (smaller)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Step 5: Configure Environment Variables

```bash
# Create .env file if it doesn't exist
touch .env

# Add your OpenAI API key (optional but recommended)
echo "OPENAI_API_KEY=sk-your-actual-key-here" >> .env

# Note: Without OpenAI key, system will use rule-based classification
# which still works, just less accurate
```

### Step 6: Initialize Database

```bash
# Run database initialization
python3 database.py

# Expected output:
# INFO:__main__:Database tables created successfully
# INFO:__main__:Database initialization completed
# Database initialization complete!
# Health check results: {'database_connection': True, 'tables_exist': True, ...}
```

**If you see errors:**
```bash
# Delete old database and retry
rm -f rfp_extraction.db
python3 database.py
```

### Step 7: Start the API Server

```bash
# Start FastAPI backend (Terminal 1)
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Test it works:**
```bash
# In another terminal, test the health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database_connection":true,"tables_exist":true,...}
```

### Step 8: Start Streamlit UI (Optional)

```bash
# Open a new terminal, activate venv again
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Streamlit
streamlit run streamlit_app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501
```

### Step 9: Verify Everything Works

Open your browser and visit:

1. **API Documentation:** http://localhost:8000/docs
   - You should see Swagger UI with all 11 endpoints

2. **API Health Check:** http://localhost:8000/health
   - Should show `"status": "healthy"`

3. **Streamlit UI:** http://localhost:8501
   - Should show the RFP Extraction Platform interface

---

## Quick Test

### Test 1: Create a Sample RFP File

```bash
# Create a simple test RFP
cat > test_sample_rfp.txt << 'EOF'
SECTION C: STATEMENT OF WORK

1. INTRODUCTION
The contractor shall provide IT support services for the Department.

2. TECHNICAL REQUIREMENTS
2.1 Performance Requirements
The system shall respond to user requests within 2 seconds.
The contractor shall maintain 99.9% system uptime.

2.2 Security Requirements
The contractor shall comply with NIST 800-171 security controls.
All data must be encrypted at rest and in transit.

3. DELIVERABLES
The contractor shall deliver:
- Monthly status reports
- Technical documentation
- Training materials

SECTION L: INSTRUCTIONS TO OFFERORS

Offerors shall submit proposals in the following format:
- Volume 1: Technical Approach
- Volume 2: Management Plan
- Volume 3: Price Proposal

SECTION M: EVALUATION CRITERIA

Proposals will be evaluated based on:
1. Technical Approach (40 points)
2. Past Performance (30 points)
3. Price (30 points)
EOF
```

### Test 2: Upload via API

```bash
# Upload the test file
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_sample_rfp.txt"

# Save the document_id from the response
# Example response:
# {
#   "job_id": "123e4567-...",
#   "document_id": "456e7890-...",
#   "message": "Document uploaded successfully. Processing started.",
#   "status": "processing"
# }
```

### Test 3: Check Processing Status

```bash
# Replace {document_id} with actual ID from step 2
curl "http://localhost:8000/documents/{document_id}/status"

# Wait a few seconds and check again
# Status should change from "processing" to "extraction_complete"
```

### Test 4: View Requirements

```bash
# Get the review queue
curl "http://localhost:8000/requirements/review_queue?limit=10"

# You should see extracted requirements with classifications
```

### Test 5: Test via Streamlit

1. Open http://localhost:8501
2. Click "Documents" tab
3. Upload `test_sample_rfp.txt`
4. Wait for processing
5. Go to "Review Queue" tab
6. You should see extracted requirements ready for validation

---

## Verification Checklist

After setup, verify these work:

- [ ] ✅ Virtual environment activated
- [ ] ✅ All dependencies installed (`pip list | wc -l` shows 50+ packages)
- [ ] ✅ Database initialized (`rfp_extraction.db` file exists)
- [ ] ✅ API server starts without errors
- [ ] ✅ Health check returns "healthy"
- [ ] ✅ Swagger docs accessible at `/docs`
- [ ] ✅ Can upload a document
- [ ] ✅ Document gets processed
- [ ] ✅ Requirements appear in review queue
- [ ] ✅ Streamlit UI loads and connects to API

---

## Troubleshooting Common Issues

### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "Address already in use" for port 8000

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
uvicorn main:app --port 8001
```

### Issue: Database errors

**Solution:**
```bash
# Reset database
rm -f rfp_extraction.db
python3 database.py
```

### Issue: OpenAI API errors (403, 429, etc.)

**Solution:**
```bash
# System will automatically fall back to rule-based classification
# Check your API key
echo $OPENAI_API_KEY

# Or comment out the key to use rule-based only
# No changes needed - fallback is automatic
```

### Issue: Streamlit won't connect to API

**Solution:**
```bash
# Check API is running
curl http://localhost:8000/health

# Check Streamlit API_BASE_URL in streamlit_app.py
# Should be: API_BASE_URL = "http://localhost:8000"

# Restart both services
```

### Issue: Processing takes too long or hangs

**Solution:**
```bash
# Check logs in terminal where API is running
# Look for errors in document processing

# Check job status
curl "http://localhost:8000/documents/{document_id}/status"

# If stuck, check database
sqlite3 rfp_extraction.db
sqlite> SELECT * FROM processing_jobs ORDER BY created_at DESC LIMIT 5;
sqlite> .quit
```

---

## Advanced Configuration

### Use PostgreSQL Instead of SQLite

```bash
# Install PostgreSQL client
pip install psycopg2-binary

# Set DATABASE_URL in .env
echo "DATABASE_URL=postgresql://user:password@localhost:5432/rfp_db" >> .env

# Create database
createdb rfp_db

# Initialize
python3 database.py
```

### Add More Memory for Processing

```bash
# Increase Python memory limit
export PYTHONMALLOC=malloc

# Start with more workers
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Enable Detailed Logging

```bash
# Add to .env
echo "LOG_LEVEL=DEBUG" >> .env

# Or run with debug flag
uvicorn main:app --log-level debug
```

---

## Production Deployment Notes

For production deployment, you'll need to:

1. **Use PostgreSQL** (not SQLite)
2. **Add authentication** (JWT tokens)
3. **Configure CORS** properly (not `*`)
4. **Use proper secrets management** (not .env file)
5. **Add HTTPS** (nginx/Caddy)
6. **Use process manager** (systemd/supervisor)
7. **Add monitoring** (Prometheus/Grafana)
8. **Implement rate limiting**
9. **Use cloud storage** (S3/GCS) for files
10. **Set up CI/CD** pipeline

See `DEPLOYMENT.md` for detailed production setup (to be created).

---

## System Requirements

### Minimum:
- 2GB RAM
- 2 CPU cores
- 5GB disk space
- Python 3.9+

### Recommended:
- 4GB RAM
- 4 CPU cores
- 10GB disk space
- Python 3.11+
- SSD storage

### For Production:
- 8GB+ RAM
- 8+ CPU cores
- 50GB+ SSD storage
- PostgreSQL database
- Redis for caching

---

## Getting Help

If you encounter issues:

1. **Check the logs** - Terminal output shows detailed errors
2. **Check database** - Use `sqlite3 rfp_extraction.db` to inspect
3. **Test API directly** - Use curl or http://localhost:8000/docs
4. **Review documentation**:
   - `IMPLEMENTATION_COMPLETE.md` - Technical details
   - `TESTING_REPORT.md` - Known issues and gaps
   - `README.md` - Project overview

---

## Success!

If you can:
- ✅ Upload a document via API or Streamlit
- ✅ See it appear in the documents list
- ✅ See requirements in the review queue
- ✅ Validate a requirement in Streamlit

**Then your system is fully operational! 🎉**

Next step: Upload a real government RFP PDF and see it extract requirements automatically!
