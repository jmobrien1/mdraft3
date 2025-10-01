# 🚀 Deploy RFP Extractor to Streamlit Cloud

Deploy your RFP extraction app to the cloud in 5 minutes - **completely free!**

## 📋 Prerequisites

1. A GitHub account (free)
2. A Streamlit Cloud account (free - sign up at https://share.streamlit.io)

---

## 🎯 Step-by-Step Deployment

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Name your repository: `rfp-extractor`
3. Choose "Public" (required for free Streamlit Cloud)
4. Click "Create repository"

### Step 2: Push Your Code to GitHub

Open Terminal on your Mac and run:

```bash
# Navigate to your project folder
cd /path/to/your/project

# Initialize git (if not already done)
git init

# Add all files
git add rfp_extractor_standalone.py
git add requirements_standalone.txt
git add .streamlit/config.toml

# Create initial commit
git commit -m "Initial commit - RFP Extractor"

# Connect to your GitHub repo (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/rfp-extractor.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "Sign in" and use your GitHub account
3. Click "New app"
4. Fill in the form:
   - **Repository**: Select `YOUR_USERNAME/rfp-extractor`
   - **Branch**: `main`
   - **Main file path**: `rfp_extractor_standalone.py`
   - **App URL**: Choose a custom URL (e.g., `your-rfp-extractor`)
5. Click "Advanced settings"
   - **Python version**: `3.11`
   - **Requirements file**: `requirements_standalone.txt`
6. Click "Deploy!"

### Step 4: Wait for Deployment

- Deployment takes 2-5 minutes
- You'll see logs as it installs dependencies
- When complete, your app will be live!

---

## 🎉 Your App is Live!

Your app will be available at:
```
https://YOUR-CUSTOM-NAME.streamlit.app
```

**Share this URL with your team!**

---

## 🔧 Making Updates

After deployment, any time you push changes to GitHub:

```bash
git add .
git commit -m "Update features"
git push
```

Streamlit Cloud will automatically redeploy your app!

---

## 📊 Features After Deployment

Your deployed app includes:

✅ File upload (TXT files)
✅ Automatic requirement extraction
✅ AI classification (Performance, Compliance, Deliverable)
✅ Review and validation interface
✅ Analytics dashboard
✅ SQLite database (stored in cloud)

---

## ⚠️ Important Notes

### Data Persistence

- **SQLite data is temporary** in Streamlit Cloud
- Data resets when the app restarts (every few days)
- For permanent storage, upgrade to the full system with Supabase

### File Size Limits

- Free tier: 1GB total storage
- Individual files: ~200MB max
- Should be fine for most RFP documents

### Usage Limits

- Free tier: Unlimited public apps
- App sleeps after 7 days of inactivity
- Wakes up automatically when accessed

---

## 🚀 Upgrade to Production (Optional)

For a production system with permanent data storage:

1. Use the full system with Supabase database
2. Add authentication
3. Deploy to your own server
4. Add API integrations (OpenAI, Document AI)

---

## 🆘 Troubleshooting

### "App is having trouble loading"
- Check deployment logs in Streamlit Cloud dashboard
- Verify `requirements_standalone.txt` is in the repo
- Make sure Python version is 3.11

### "Module not found" errors
- Add missing packages to `requirements_standalone.txt`
- Redeploy the app

### Database resets
- This is normal behavior for free tier
- For persistent data, contact me about Supabase setup

---

## 📞 Need Help?

If you run into issues:
1. Check Streamlit Cloud docs: https://docs.streamlit.io/deploy/streamlit-community-cloud
2. Check deployment logs for specific errors
3. Ask for help in Streamlit Community Forum

---

## 🎊 Next Steps

After your app is deployed:

1. **Test it** - Upload sample RFP documents
2. **Share it** - Send the URL to your team
3. **Enhance it** - Add more requirement types
4. **Upgrade** - Move to production with Supabase

Enjoy your cloud-deployed RFP extraction system!
