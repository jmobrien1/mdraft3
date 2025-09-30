# 🚀 Quick Start Guide - RFP Extraction System

## Step 1: Download the Project

**Option A: Copy from this environment**
```bash
# The project archive is at: ~/rfp-extraction-system.tar.gz
# You'll need to download/copy it to your Mac
```

**Option B: Files are in this directory**
Copy all files from `/tmp/cc-agent/57802722/project` to your local machine.

---

## Step 2: Setup on Your Mac

```bash
# 1. Create a project directory
mkdir ~/rfp-extraction-system
cd ~/rfp-extraction-system

# 2. Extract files (if using archive)
tar -xzf ~/Downloads/rfp-extraction-system.tar.gz

# 3. Install Python dependencies
pip3 install -r requirements.txt

# 4. Create uploads directory
mkdir -p uploads
```

---

## Step 3: Configure Database

You have **two options**:

### Option A: Use Your Own Supabase (Recommended)

1. Go to https://supabase.com and create a free account
2. Create a new project
3. Copy the connection details
4. Edit `.env` file:

```bash
# Replace with your Supabase credentials
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
VITE_SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
VITE_SUPABASE_SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
```

5. Run the migration:
```bash
# Copy the SQL from supabase/migrations/20250930213419_create_rfp_extraction_schema.sql
# Paste it into Supabase SQL Editor and run it
```

### Option B: Use SQLite (Quick Testing)

1. Install dependencies:
```bash
pip3 install sqlalchemy sqlite-utils
```

2. The system will auto-create a local SQLite database

---

## Step 4: Start the System

### Terminal 1 - Start API Server
```bash
cd ~/rfp-extraction-system
python3 main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Start Web Interface
```bash
cd ~/rfp-extraction-system
streamlit run streamlit_app.py
```

You should see:
```
Local URL: http://localhost:8501
```

---

## Step 5: Test It!

1. Open browser to **http://localhost:8501**
2. Upload a test RFP document
3. Watch the extraction happen
4. Review and validate requirements
5. Export results

---

## 📋 What You Need Installed

Check your Mac has these:

```bash
# Python 3.8+
python3 --version

# Pip
pip3 --version

# If missing, install Python from: https://www.python.org/downloads/
```

---

## 🔧 Troubleshooting

**Port 8000 already in use?**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

**Port 8501 already in use?**
```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502
```

**Missing dependencies?**
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

**Database connection errors?**
- Check your `.env` file has correct credentials
- Verify Supabase project is active
- Check firewall/network settings

---

## 🎯 Next Steps After Setup

1. **Test with sample data**: Use `test_rfp_realistic.txt`
2. **Upload real RFPs**: Try your own documents
3. **Customize classifications**: Edit the patterns in `document_processor.py`
4. **Add OpenAI**: Improve accuracy with AI classification
5. **Deploy to cloud**: Make it accessible to your team

---

## 📞 Need Help?

Common issues and solutions in the main README.md
