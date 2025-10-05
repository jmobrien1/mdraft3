# Deploy to Render (Backend) and Vercel (Frontend)

Complete step-by-step guide to deploy your RFP Extractor application.

---

## Part 1: Deploy Backend to Render

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done):
```bash
cd /path/to/project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### Step 3: Create a Web Service

1. Click "New +" button in the top right
2. Select "Web Service"
3. Connect your GitHub repository
4. Click "Connect" next to your repository

### Step 4: Configure the Service

Fill in these settings:

**Basic Settings:**
- **Name**: `rfp-extractor-api` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build Settings:**
- **Build Command**:
  ```
  pip install -r requirements.txt
  ```

**Start Command**:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
- Select **Free** (or **Starter** for better performance - $7/month)

### Step 5: Add Environment Variables

Scroll down to "Environment Variables" section and add:

Click "Add Environment Variable" for each:

1. **Key**: `VITE_SUPABASE_URL`
   **Value**: `https://0ec90b57d6e95fcbda19832f.supabase.co`

2. **Key**: `VITE_SUPABASE_KEY`
   **Value**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJib2x0IiwicmVmIjoiMGVjOTBiNTdkNmU5NWZjYmRhMTk4MzJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODE1NzQsImV4cCI6MTc1ODg4MTU3NH0.9I8-U0x86Ak8t2DGaIk0HfvTSLsAyzdnz-Nw00mMkKw`

### Step 6: Deploy

1. Click "Create Web Service"
2. Render will start building your application
3. Wait 3-5 minutes for the build to complete
4. Once done, you'll see "Live" status with a green dot

### Step 7: Get Your Backend URL

1. At the top of your service page, you'll see a URL like:
   `https://rfp-extractor-api.onrender.com`
2. **Copy this URL** - you'll need it for the frontend!

### Step 8: Test Your Backend

Visit: `https://YOUR-SERVICE-NAME.onrender.com`

You should see:
```json
{
  "message": "RFP Extractor API",
  "version": "2.0"
}
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend Environment

Before deploying, update your frontend `.env` file:

```bash
cd frontend
```

Edit `.env`:
```env
VITE_SUPABASE_URL=https://0ec90b57d6e95fcbda19832f.supabase.co
VITE_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJib2x0IiwicmVmIjoiMGVjOTBiNTdkNmU5NWZjYmRhMTk4MzJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODE1NzQsImV4cCI6MTc1ODg4MTU3NH0.9I8-U0x86Ak8t2DGaIk0HfvTSLsAyzdnz-Nw00mMkKw
VITE_API_URL=https://YOUR-RENDER-SERVICE-NAME.onrender.com
```

**Important**: Replace `YOUR-RENDER-SERVICE-NAME` with your actual Render URL!

Commit and push:
```bash
git add .
git commit -m "Update API URL for production"
git push
```

### Step 2: Sign Up for Vercel

1. Go to https://vercel.com
2. Click "Sign Up"
3. Sign up with GitHub (recommended)
4. Authorize Vercel to access your repositories

### Step 3: Import Your Project

1. Click "Add New..." → "Project"
2. Find your repository in the list
3. Click "Import"

### Step 4: Configure Build Settings

Vercel should auto-detect these settings:

**Framework Preset**: `Vite`

**Root Directory**:
- Click "Edit" next to Root Directory
- Enter: `frontend`
- Click "Continue"

**Build Settings** (should auto-fill):
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Step 5: Add Environment Variables

Click "Environment Variables" dropdown:

Add each variable:

1. **Key**: `VITE_SUPABASE_URL`
   **Value**: `https://0ec90b57d6e95fcbda19832f.supabase.co`

2. **Key**: `VITE_SUPABASE_KEY`
   **Value**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJib2x0IiwicmVmIjoiMGVjOTBiNTdkNmU5NWZjYmRhMTk4MzJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODE1NzQsImV4cCI6MTc1ODg4MTU3NH0.9I8-U0x86Ak8t2DGaIk0HfvTSLsAyzdnz-Nw00mMkKw`

3. **Key**: `VITE_API_URL`
   **Value**: `https://YOUR-RENDER-SERVICE-NAME.onrender.com`

   **Replace with your actual Render URL!**

### Step 6: Deploy

1. Click "Deploy"
2. Vercel will build and deploy your app (takes 1-2 minutes)
3. Once complete, you'll see "Congratulations!" with confetti

### Step 7: Get Your Frontend URL

Your app will be live at:
`https://YOUR-PROJECT-NAME.vercel.app`

Click "Visit" to open your application!

---

## Part 3: Update CORS Settings

Your backend needs to allow requests from your frontend domain.

### Update Backend CORS

1. Go back to your Render dashboard
2. Open your web service
3. Click "Shell" in the left sidebar (to edit files) OR update locally and push

Edit `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://YOUR-PROJECT-NAME.vercel.app",  # Production
        "https://*.vercel.app"  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Better approach**: Update locally and push:
```bash
cd backend
# Edit main.py with the CORS changes above
cd ..
git add .
git commit -m "Update CORS for production"
git push
```

Render will automatically redeploy!

---

## Part 4: Test Your Deployed Application

1. Visit your Vercel URL: `https://YOUR-PROJECT-NAME.vercel.app`
2. Click "Upload Document"
3. Upload a test RFP file (PDF, DOCX, or TXT)
4. Watch requirements get extracted!

---

## Troubleshooting

### Backend Issues

**Build fails on Render:**
- Check the build logs in Render dashboard
- Verify `requirements.txt` is in the `backend/` directory
- Ensure Python version is compatible (3.9+)

**API returns 500 errors:**
- Check Render logs: Click "Logs" in your service dashboard
- Verify environment variables are set correctly
- Check Supabase credentials

**"Module not found" errors:**
- Add missing packages to `backend/requirements.txt`
- Redeploy

### Frontend Issues

**Build fails on Vercel:**
- Check build logs in Vercel dashboard
- Verify `package.json` is in `frontend/` directory
- Try building locally: `npm run build`

**"Network Error" when uploading:**
- Check CORS settings in backend
- Verify `VITE_API_URL` environment variable
- Check browser console for errors

**Environment variables not working:**
- Vercel requires `VITE_` prefix for client-side variables
- Redeploy after adding variables: "Deployments" → "..." → "Redeploy"

### CORS Errors

If you see CORS errors in browser console:

1. Check backend CORS settings include your Vercel URL
2. Make sure backend redeployed after CORS changes
3. Clear browser cache
4. Try incognito/private window

### Render Free Tier Limitations

**Service spins down after 15 minutes of inactivity:**
- First request after spin-down takes 30-60 seconds
- Upgrade to Starter ($7/month) for always-on service
- Or use a service like UptimeRobot to ping your API every 14 minutes

---

## Post-Deployment Checklist

- [ ] Backend is live and returns JSON at root endpoint
- [ ] Frontend is live and shows UI
- [ ] Can upload a document
- [ ] Requirements are extracted and displayed
- [ ] Can validate/reject requirements
- [ ] CORS is configured correctly
- [ ] Environment variables are set in both services

---

## Updating Your Application

### Update Backend:
```bash
# Make changes to backend code
git add .
git commit -m "Update backend"
git push
# Render auto-deploys!
```

### Update Frontend:
```bash
# Make changes to frontend code
git add .
git commit -m "Update frontend"
git push
# Vercel auto-deploys!
```

---

## Cost Summary

**Render Free Tier:**
- 750 hours/month free
- Spins down after 15 minutes inactivity
- Good for testing and demos

**Render Starter ($7/month):**
- Always-on
- Better for production

**Vercel Hobby (Free):**
- Unlimited deployments
- 100GB bandwidth/month
- Perfect for personal projects

**Total Cost**: $0 (Free) or $7/month (Starter)

---

## Need Help?

**Render Support:**
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Community: https://community.render.com

**Vercel Support:**
- Dashboard: https://vercel.com/dashboard
- Docs: https://vercel.com/docs
- Support: https://vercel.com/support

**Application Issues:**
- Check Render logs for backend errors
- Check Vercel logs for frontend errors
- Check browser console for client-side errors
