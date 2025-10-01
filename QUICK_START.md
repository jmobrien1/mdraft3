# 🚀 Quick Start - Standalone RFP Extractor

Get up and running in **5 minutes** on your Mac!

## Step 1: Copy the File

1. Copy the contents of `rfp_extractor_standalone.py` to your Mac
2. Save it anywhere (e.g., `~/Desktop/rfp_extractor_standalone.py`)

## Step 2: Install Dependencies

Open Terminal on your Mac and run:

```bash
pip3 install streamlit sqlite-utils
```

That's it! Just 2 packages.

## Step 3: Run It

```bash
# Navigate to where you saved the file
cd ~/Desktop

# Run the application
streamlit run rfp_extractor_standalone.py
```

Your browser will automatically open to `http://localhost:8501`

## Step 4: Test It

1. **Upload Tab**: Upload a .txt file with RFP content
2. **Review Tab**: See extracted requirements, validate them
3. **Analytics Tab**: View statistics and progress

## 📝 Sample Test File

Create a file called `test_rfp.txt` with this content:

```
Section C.2.1.1 Performance Requirements

The contractor shall maintain 99.9% uptime for all mission-critical systems.

The contractor shall ensure that all web applications respond within 2 seconds.

Section C.2.2.2 Security Requirements

The contractor shall implement encryption for all data at rest using AES-256.

All data in transit shall be encrypted using TLS 1.3 or higher.

Section C.3.1 Deliverables

The contractor shall submit monthly status reports by the 5th business day.
```

Upload this file to see the extraction in action!

## 🎯 What This Does

- ✅ Extracts requirements from RFP documents
- ✅ Classifies them (Performance, Compliance, Deliverable)
- ✅ Provides confidence scores
- ✅ Tracks validation status
- ✅ Shows analytics dashboard
- ✅ Stores everything in local SQLite database

## 📊 Features

- **No server setup** - Everything runs locally
- **No database config** - Uses SQLite automatically
- **No API calls** - Pure pattern matching (no OpenAI needed)
- **Single file** - Easy to understand and modify
- **Web interface** - User-friendly Streamlit UI

## 🔧 Troubleshooting

**Port 8501 already in use?**
```bash
streamlit run rfp_extractor_standalone.py --server.port 8502
```

**Module not found?**
```bash
pip3 install --upgrade streamlit
```

**Permission denied?**
```bash
chmod +x rfp_extractor_standalone.py
```

## 🚀 Next Steps

1. Test with the sample file above
2. Upload your own RFP documents
3. Customize the classification patterns (lines 128-154)
4. Add more requirement types
5. Integrate with OpenAI for better accuracy

## 💡 Pro Tips

- **Use .txt files** - The standalone version only supports plain text
- **Format matters** - Use "Section X.Y.Z" headers for better extraction
- **Keywords count** - Requirements must contain "shall" or "must"
- **Validation helps** - Review and validate for better insights

## 📞 Need Help?

The code is heavily commented. Look for these sections:
- Line 85: Database setup
- Line 192: Extraction patterns
- Line 300+: UI components

Modify any section to customize for your needs!

---

**That's it!** You now have a working RFP extraction system running locally on your Mac. No cloud, no APIs, no complex setup. Just copy, install, and run!
