# RFP Extractor - Deployment Guide

This is a production-ready RFP requirement extraction application with a FastAPI backend and React frontend.

## Architecture

- **Backend**: FastAPI REST API
- **Frontend**: React + Vite
- **Database**: Supabase PostgreSQL
- **Storage**: Supabase Storage
- **Document Processing**: PyPDF2, python-docx

## Prerequisites

- Supabase project (already configured)
- Python 3.9+
- Node.js 18+

## Backend Deployment (Railway/Render)

### Option 1: Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
cd backend
railway init
```

3. Add environment variables in Railway dashboard:
```
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_KEY=your-anon-key
```

4. Deploy:
```bash
railway up
```

### Option 2: Render

1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
4. Add environment variables in Settings
5. Deploy

### Option 3: Docker

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Frontend Deployment (Vercel/Netlify)

### Option 1: Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd frontend
vercel
```

3. Add environment variables in Vercel dashboard:
```
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_KEY=your-anon-key
VITE_API_URL=https://your-backend-url.com
```

### Option 2: Netlify

1. Build:
```bash
cd frontend
npm run build
```

2. Deploy:
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

3. Add environment variables in Netlify dashboard

## Local Development

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

## Environment Variables

Create `.env` file in both `backend/` and `frontend/`:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your-anon-key
VITE_API_URL=http://localhost:8000  # For local dev
```

## Database Setup

The database is already set up with:
- Documents table
- Requirements table
- Text chunks table
- Storage bucket for file uploads

## Testing

Upload a test document:
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@test_rfp.txt"
```

## Production Checklist

- [ ] Set up proper CORS origins in backend
- [ ] Add authentication (Supabase Auth)
- [ ] Enable rate limiting
- [ ] Set up monitoring (Sentry/LogRocket)
- [ ] Configure CDN for frontend
- [ ] Set up automated backups
- [ ] Add error tracking
- [ ] Implement proper logging

## Troubleshooting

### CORS Issues
Update `main.py` CORS settings to your frontend domain:
```python
allow_origins=["https://your-frontend-domain.com"]
```

### Storage Issues
Verify the storage bucket exists in Supabase dashboard under Storage

### Database Connection
Check that your Supabase URL and keys are correct in `.env`
