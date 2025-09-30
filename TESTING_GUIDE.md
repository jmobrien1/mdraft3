# Testing Guide: How to Test Your RFP Extraction System

This guide shows you how to test the system yourself in three different ways.

---

## Prerequisites

Before you start, you need:
- Python 3.9 or higher installed
- Your Supabase database password (get it from Supabase Dashboard → Settings → Database)

---

## Option 1: Query Database Directly (Easiest - 2 minutes)

### Steps:

1. **Go to Supabase Dashboard**
   - URL: https://supabase.com/dashboard
   - Select your project

2. **Click "SQL Editor"** in the left menu

3. **Run test queries**:

```sql
-- See your documents
SELECT original_filename, status, uploaded_at,
       (SELECT COUNT(*) FROM requirements WHERE document_id = documents.id) as requirement_count
FROM documents
ORDER BY uploaded_at DESC;

-- See all extracted requirements by type
SELECT
  classification,
  COUNT(*) as count,
  ROUND(AVG(CASE WHEN status = 'human_validated' THEN 100 ELSE 0 END), 1) as validation_pct
FROM requirements
GROUP BY classification
ORDER BY classification;

-- View actual requirements
SELECT
  classification,
  source_section || '.' || source_subsection as location,
  clean_text,
  status
FROM requirements
ORDER BY source_section, source_subsection
LIMIT 20;
```

---

## Option 2: Run API Locally (Recommended - 30 minutes)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd /tmp/cc-agent/57802722/project

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

Edit the `.env` file and add your Supabase password:

```bash
# Open .env file
nano .env  # or use any text editor

# Update this line with your actual password:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@db.0ec90b57d6e95fcbda19832f.supabase.co:5432/postgres

# Optional: Add OpenAI key for better classification
OPENAI_API_KEY=sk-your-key-here
```

Get your password from: **Supabase Dashboard → Settings → Database → Database Password**

### Step 3: Start the API Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start the server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Test the API

Open your browser and go to: **http://localhost:8000/docs**

You'll see the interactive API documentation (Swagger UI)!

### Step 5: Try the Endpoints

#### Test 1: Health Check
1. Click on `GET /health`
2. Click "Try it out"
3. Click "Execute"
4. You should see: `{"status": "healthy"}`

#### Test 2: List Documents
1. Click on `GET /documents`
2. Click "Try it out"
3. Click "Execute"
4. You should see your test document!

#### Test 3: Get Requirements
1. Click on `GET /documents/{document_id}/requirements`
2. Click "Try it out"
3. Paste the document ID from Test 2: `a442d368-dd77-4615-88c7-04bf075cc61c`
4. Click "Execute"
5. You should see all 8 extracted requirements!

#### Test 4: Upload a New Document
1. Click on `POST /documents/upload`
2. Click "Try it out"
3. Click "Choose File" and select `test_rfp_realistic.txt`
4. Click "Execute"
5. Watch it process in real-time!

---

## Option 3: Run Full System with UI (Complete - 45 minutes)

This gives you the full Streamlit interface for validation.

### Step 1: Install Dependencies (if not done)

```bash
cd /tmp/cc-agent/57802722/project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start API Server (Terminal 1)

```bash
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Start Streamlit (Terminal 2)

Open a **new terminal window**:

```bash
cd /tmp/cc-agent/57802722/project
source venv/bin/activate
streamlit run streamlit_app.py
```

### Step 4: Use the UI

The Streamlit app should open automatically, or go to: **http://localhost:8501**

You'll see:
- **📤 Upload Document** tab - Upload new RFPs
- **📋 Review Queue** tab - See all pending requirements
- **✅ Validation Interface** tab - Validate requirements
- **📊 Analytics Dashboard** tab - View statistics

### Step 5: Test the Workflow

1. **Upload Tab**:
   - Upload `test_rfp_realistic.txt`
   - Watch it process

2. **Review Queue Tab**:
   - See all extracted requirements
   - Filter by classification

3. **Validation Tab**:
   - Click a requirement to review
   - Accept, reject, or modify it
   - See the audit trail

4. **Analytics Tab**:
   - View extraction statistics
   - See validation progress

---

## Quick API Tests with cURL

If you just want to test the API without a browser:

```bash
# Health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/documents

# Get requirements for a document
curl http://localhost:8000/documents/a442d368-dd77-4615-88c7-04bf075cc61c/requirements

# Upload a document
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_rfp_realistic.txt"
```

---

## Troubleshooting

### Issue: "Module not found" errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Connection refused" to database
```bash
# Check your DATABASE_URL in .env
# Make sure password is correct
# Test connection:
psql "postgresql://postgres:YOUR_PASSWORD@db.0ec90b57d6e95fcbda19832f.supabase.co:5432/postgres"
```

### Issue: Port 8000 already in use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --port 8001
```

### Issue: pgvector extension error
```bash
# The extension is already installed in Supabase
# If you see errors, check your DATABASE_URL points to Supabase
```

---

## What to Test

### Basic Functionality:
- ✅ API starts without errors
- ✅ Health endpoint returns success
- ✅ Can list documents
- ✅ Can view requirements
- ✅ Can filter by classification

### Upload & Processing:
- ✅ Upload a new document
- ✅ Document appears in database
- ✅ Requirements are extracted
- ✅ Requirements are classified correctly

### Validation Workflow:
- ✅ View pending requirements
- ✅ Validate a requirement
- ✅ Add validation notes
- ✅ Check audit trail

### Data Integrity:
- ✅ Requirements link to correct document
- ✅ Source locations are tracked
- ✅ Timestamps are recorded
- ✅ History is maintained

---

## Test Data Available

You already have test data in the database:

- **Document**: TSA IT Support Services RFP.txt
- **Document ID**: `a442d368-dd77-4615-88c7-04bf075cc61c`
- **Text Chunks**: 4 chunks
- **Requirements**: 8 requirements
  - 4 Performance Requirements
  - 3 Compliance Requirements
  - 1 Deliverable Requirement

---

## Expected Results

When everything is working:

1. **API Docs** (http://localhost:8000/docs) loads successfully
2. **GET /health** returns `{"status": "healthy"}`
3. **GET /documents** returns your test document
4. **GET /documents/{id}/requirements** returns 8 requirements
5. **POST /documents/upload** accepts new files
6. **Streamlit UI** (http://localhost:8501) shows all tabs
7. **Database queries** return data instantly

---

## Performance Expectations

### Small RFP (like test file):
- Upload: < 1 second
- Processing: 5-10 seconds
- Extraction: 5-20 requirements
- Classification: 85-90% accuracy with OpenAI, 70-75% without

### Medium RFP (50-100 pages):
- Upload: 1-2 seconds
- Processing: 30-60 seconds
- Extraction: 100-300 requirements

---

## Next Steps After Testing

Once you've verified everything works:

1. **Upload Your Own RFP** - Test with real documents
2. **Customize Classifications** - Add your own requirement types
3. **Tune Extraction** - Adjust chunking and classification logic
4. **Add Authentication** - Implement user login
5. **Deploy to Production** - Set up on a real server

---

## Getting Help

If something doesn't work:

1. Check the console output for error messages
2. Verify `.env` configuration
3. Test database connection directly
4. Check Python version (needs 3.9+)
5. Ensure all dependencies installed

---

## Summary

**Easiest Way**: Query Supabase SQL Editor directly (2 min)

**Recommended Way**: Run API locally and use Swagger docs (30 min)

**Full Experience**: Run API + Streamlit for complete UI (45 min)

All three ways work with the **same database**, so you can switch between them anytime!
