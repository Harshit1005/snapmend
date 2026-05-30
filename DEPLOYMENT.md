# SnapMend Deployment Guide

Complete step-by-step instructions for deploying SnapMend to production.

## Prerequisites

- ✅ GitHub account with code pushed
- ✅ Gemini API key from [ai.google.dev](https://ai.google.dev)
- ✅ GCP project (free tier) with billing enabled for service accounts
- ✅ Render account at [render.com](https://render.com)
- ✅ Vercel account at [vercel.com](https://vercel.com) (optional)

## Phase 1: Backend Deployment (Render)

### Step 1: Prepare GitHub Repository

1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: SnapMend backend & frontend"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/snapmend.git
   git push -u origin main
   ```

2. **Repository structure should look like**:
   ```
   snapmend/
   ├── backend/
   │   ├── app/
   │   ├── main.py
   │   ├── requirements.txt
   │   ├── Dockerfile
   │   └── .env.example
   ├── frontend/
   ├── PRD_PART1_ARCHITECTURE.md
   └── README.md
   ```

### Step 2: Get Gemini API Key

1. Go to [ai.google.dev](https://ai.google.dev)
2. Click **"Get API Key"** (top-right)
3. Create new API key
4. **Copy the key** (you'll need it in Step 5)

### Step 3: Set Up GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: **"snapmend"**
3. Enable these APIs:
   - BigQuery API
   - Cloud Storage API
4. Create BigQuery dataset: **"mcd_dataset"**
5. Create Cloud Storage bucket: **"your-project-id-mcd-assets"**

### Step 4: Create Render Web Service

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Select **"Connect a repository"**
4. Choose your GitHub repository
5. Fill in details:

   | Setting | Value |
   |---------|-------|
   | Name | `snapmend-backend` |
   | Root Directory | `backend` |
   | Runtime | `Python 3.11` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port 8000` |
   | Branch | `main` |
   | Pricing Plan | `Free` |

### Step 5: Configure Environment Variables

In Render dashboard, add these variables:

```
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-project-id-mcd-assets
BQ_DATASET=mcd_dataset
BQ_REPAIR_HISTORY_TABLE=mcd_dataset.repair_history
BQ_STREETS_TABLE=mcd_dataset.streets
BQ_WORK_ORDERS_TABLE=mcd_dataset.work_orders
GEMINI_API_KEY=<paste your key from Step 2>
RESEND_API_KEY=<get from resend.com>
NOTIFICATION_FROM_EMAIL=noreply@snapmend.app
NOTIFICATION_TO_EMAIL=supervisor@snapmend.demo
FRONTEND_URL=https://snapmend.vercel.app
CORS_ORIGINS=["https://snapmend.vercel.app","https://snapmend.onrender.com"]
```

**Note**: Leave `GOOGLE_APPLICATION_CREDENTIALS` empty (only for local development)

### Step 6: Deploy Backend

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start the server
   - Generate a URL like: `https://snapmend-backend.onrender.com`
3. **Wait 3-5 minutes** for first deployment

### Step 7: Verify Backend

```bash
# Check health endpoint
curl https://snapmend-backend.onrender.com/health

# Should return:
# {
#   "status": "healthy",
#   "service": "snapmend-backend",
#   "gemini_api_configured": true,
#   "gcp_project": "your-project-id"
# }
```

## Phase 2: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

1. **Update backend URL in frontend**:
   ```bash
   cd frontend
   cp .env.example .env
   ```

2. **Edit `frontend/.env`**:
   ```
   VITE_API_BASE_URL=https://snapmend-backend.onrender.com
   VITE_GOOGLE_MAPS_API_KEY=YOUR_KEY_HERE
   ```

3. **Push to GitHub**:
   ```bash
   git add frontend/.env
   git commit -m "Update backend URL for production"
   git push
   ```

### Step 2: Deploy on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New..."** → **"Project"**
3. Select your **snapmend** repository
4. Fill in configuration:

   | Setting | Value |
   |---------|-------|
   | Framework Preset | `Other` |
   | Root Directory | `frontend` |
   | Build Command | `npm run build` |
   | Output Directory | `dist` |

5. Add Environment Variables:
   ```
   VITE_API_BASE_URL=https://snapmend-backend.onrender.com
   VITE_GOOGLE_MAPS_API_KEY=YOUR_KEY_HERE
   ```

6. Click **"Deploy"**
7. **Wait 2-3 minutes** for deployment
8. Your frontend URL: `https://snapmend-frontend.vercel.app`

### Step 3: Verify Frontend

1. Open `https://snapmend-frontend.vercel.app` in browser
2. Check that dashboard loads
3. Check that "New Assessment" button works
4. Verify API calls in browser DevTools (Network tab)

## Phase 3: Local Development Testing

### Before Deploying

Test everything locally first:

1. **Start backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   cp .env.example .env
   # Edit .env with your Gemini API key
   python main.py
   ```

2. **Start frontend** (new terminal):
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env: VITE_API_BASE_URL=http://localhost:8000
   npm run dev
   ```

3. **Test assessment form**:
   - Open http://localhost:5173
   - Click "New Assessment"
   - Fill form with test data
   - Upload a test image
   - Should see Gemini response

4. **Check health endpoints**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/assessment/health
   curl http://localhost:8000/api/repair/health
   ```

## Phase 4: Post-Deployment Configuration

### Enable BigQuery Authentication (Local Development)

1. **Create GCP Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Go to "Service Accounts"
   - Create new service account: "snapmend-dev"
   - Grant roles:
     - `BigQuery Data Editor`
     - `Storage Object Viewer`
   - Create JSON key
   - Download and save to `backend/service-account.json`

2. **Update `.env`** (local only):
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
   ```

3. **Never commit service account to GitHub!**
   - Already in `.gitignore`
   - Only for local development

### Set Up Email Notifications

1. Go to [resend.com](https://resend.com)
2. Get free API key
3. Add to Render environment variables:
   ```
   RESEND_API_KEY=re_your_key_here
   ```

## Phase 5: Continuous Deployment

### Auto-Deploy on Git Push

1. **Render** auto-deploys on push to `main` branch
2. **Vercel** auto-deploys on push to `main` branch
3. **No manual steps needed** after initial setup

### Monitor Deployments

1. **Render Dashboard**:
   - Check "Deploy Log" for errors
   - Monitor "Metrics" for uptime

2. **Vercel Dashboard**:
   - Check "Deployments" for build status
   - Check "Analytics" for performance

## Phase 6: Production Monitoring

### Health Checks

```bash
# Backend health
curl https://snapmend-backend.onrender.com/health

# Frontend is running
curl https://snapmend-frontend.vercel.app

# Full system test
curl -X GET https://snapmend-backend.onrender.com/api/assessment/health
```

### Logs

1. **Render Logs**:
   - Dashboard → snapmend-backend → Logs

2. **Vercel Logs**:
   - Dashboard → snapmend-frontend → Logs

### Debugging

If deployment fails:

1. **Check Render build logs**:
   - Dashboard → snapmend-backend → Logs
   - Look for Python errors

2. **Check Vercel build logs**:
   - Dashboard → snapmend-frontend → Deployments

3. **Test locally first**:
   - `python main.py` (backend)
   - `npm run build && npm run preview` (frontend)

## Common Issues & Solutions

### "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Ensure `requirements.txt` is in root of backend directory
```bash
# Correct structure:
backend/
├── main.py
├── requirements.txt  # HERE
└── app/
```

### "Cannot find module 'vue'"

**Solution**: Run `npm install` in frontend directory before building
- Render/Vercel should do this automatically via build command

### "GEMINI_API_KEY is not set"

**Solution**: Add to Render environment variables in dashboard
- Must be set before deployment or restart service

### "CORS error: blocked by CORS policy"

**Solution**: Update `CORS_ORIGINS` in Render environment variables
```
CORS_ORIGINS=["https://snapmend.vercel.app"]
```

### "API returns 500 error"

**Solution**: Check Render logs
```bash
1. Go to Render dashboard
2. Select snapmend-backend
3. Click "Logs"
4. Look for error traceback
5. Fix and push to GitHub
6. Render auto-redeploys
```

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Test end-to-end flow
4. ✅ Configure BigQuery (optional, for history)
5. ✅ Set up email notifications (optional)
6. 🔜 Build mobile APK with Capacitor
7. 🔜 Add user authentication
8. 🔜 Implement advanced features

## Timeline

| Phase | Time | Status |
|-------|------|--------|
| Backend setup | 10 min | ✅ |
| Frontend setup | 10 min | ✅ |
| Local testing | 15 min | ✅ |
| Render deployment | 5 min | ✅ |
| Vercel deployment | 5 min | ✅ |
| Production testing | 10 min | ✅ |
| **TOTAL** | **~55 min** | 🚀 |

**Total cost**: $0

---

Happy deploying! 🚀
