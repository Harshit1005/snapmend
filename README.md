# SnapMend - Municipal Pavement Assessment Platform

Transform street maintenance with AI-powered pavement condition analysis. **Zero billing required** — uses free-tier Google Cloud services and Render hosting.

![Status](https://img.shields.io/badge/status-building-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Cost](https://img.shields.io/badge/monthly%20cost-$0-brightgreen)

## 🎯 Overview

SnapMend is a mobile-first web platform designed for municipal inspectors to assess street pavement conditions using AI. Instead of expensive enterprise solutions requiring billing accounts, SnapMend uses **free-tier APIs** and **free hosting**.

### Key Features

- 🤖 **AI-Powered Assessment**: Gemini 2.0 Flash API analyzes pavement images
- 📱 **Mobile-First**: Responsive design works on phones, tablets, desktops
- 📊 **Data Integration**: BigQuery for repair history, geospatial queries
- ☁️ **Serverless**: Zero infrastructure management needed
- ✅ **Zero Cost**: All services on free tier — no billing account required
- 🚀 **Fast Deployment**: GitHub → Render pipeline (15 minutes)

### Architecture

```
Frontend (Vue 3 + Vite)     Backend (FastAPI)           Data (GCP Free Tier)
┌─────────────────┐        ┌──────────────┐            ┌──────────────┐
│  Assessment UI  │────→   │  Render.com  │───→────→   │  Gemini API  │
│  (Vercel/etc)   │        │   (Free)     │            │  (Free)      │
│                 │        │              │            │              │
│  Dashboard      │        │  FastAPI     │            │ BigQuery     │
│  Repair History │←───────│  Uvicorn     │←───────→   │ (Free tier)  │
│  Repair Form    │        │              │            │              │
└─────────────────┘        └──────────────┘            │ Cloud Storage│
                           │  routes/      │            │ (Free tier)  │
                           │  - assessment │            └──────────────┘
                           │  - repair     │
                           │  - health     │
                           └──────────────┘
```

## 📁 Project Structure

```
snapmend/
├── backend/                    # FastAPI server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings from .env
│   │   ├── models.py           # Request/response schemas
│   │   ├── gemini_service.py   # Gemini API integration
│   │   └── routes/
│   │       ├── assessment.py   # /api/assessment/* endpoints
│   │       └── repair.py       # /api/repair/* endpoints
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Container image
│   ├── .env.example            # Environment template
│   └── README.md               # Backend docs
│
├── frontend/                   # Vue 3 SPA
│   ├── src/
│   │   ├── main.js            # Entry point
│   │   ├── App.vue            # Root component
│   │   ├── router.js          # Routes
│   │   ├── components/
│   │   │   ├── AssessmentForm.vue     # Image upload/analysis
│   │   │   └── RepairHistory.vue      # Repair records
│   │   ├── views/
│   │   │   ├── Dashboard.vue  # Home page
│   │   │   └── Assessment.vue # Assessment flow
│   │   └── services/
│   │       └── api.js         # API client
│   ├── index.html             # HTML template
│   ├── package.json           # npm dependencies
│   ├── vite.config.js         # Build config
│   ├── .env.example           # Environment template
│   └── README.md              # Frontend docs
│
├── PRD_PART1_ARCHITECTURE.md   # System design
├── PRD_PART2_BACKEND.md        # Implementation guide
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- GitHub account (for code hosting)
- Render account (for backend hosting)
- Vercel account (optional, for frontend hosting)

### 1. Get Gemini API Key (5 minutes)

Free, no credit card required:

```bash
1. Go to https://ai.google.dev
2. Click "Get API Key"
3. Copy the key
4. Save as environment variable
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Gemini API key and GCP project ID

# Run locally
python main.py
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL (http://localhost:8000)

# Run development server
npm run dev
```

Frontend available at `http://localhost:5173`

### 4. Deploy to Render (Backend)

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

**Quick steps:**
1. Push backend code to GitHub
2. Create Render Web Service
3. Select your GitHub repository
4. Set environment variables
5. Deploy (automatic on git push)

### 5. Deploy to Vercel (Frontend)

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set `VITE_API_BASE_URL` to your Render backend URL
4. Deploy

## 📚 Documentation

- [Architecture](./PRD_PART1_ARCHITECTURE.md) - System design, database schema, API specification
- [Backend Guide](./PRD_PART2_BACKEND.md) - Implementation details, code structure, deployment
- [Backend README](./backend/README.md) - API endpoints, development, troubleshooting
- [Frontend README](./frontend/README.md) - Components, routing, styling
- [Deployment Guide](./DEPLOYMENT.md) - Step-by-step deployment instructions

## 🔌 API Endpoints

All endpoints require `GEMINI_API_KEY` environment variable.

### Assessment
- `POST /api/assessment/evaluate` - Analyze pavement from images
- `GET /api/assessment/health` - Service health check

### Repair Management
- `GET /api/repair/history/{street_segment_id}` - Repair history
- `GET /api/repair/nearby` - Nearby streets (geospatial)
- `POST /api/repair/work-order` - Create work order
- `GET /api/repair/health` - Service health check

### System
- `GET /` - API info & endpoints
- `GET /health` - System health status

[Full API Documentation](./PRD_PART1_ARCHITECTURE.md#51-api-specification)

## 🌐 Environment Variables

### Backend (`.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | ✅ |
| `GCS_BUCKET_NAME` | Cloud Storage bucket name | ✅ |
| `BQ_DATASET` | BigQuery dataset name | ✅ |
| `GEMINI_API_KEY` | Gemini API key (free from ai.google.dev) | ✅ |
| `RESEND_API_KEY` | Email API key | ✅ |
| `NOTIFICATION_FROM_EMAIL` | From address | ✅ |
| `NOTIFICATION_TO_EMAIL` | Supervisor email | ✅ |
| `FRONTEND_URL` | Frontend URL for CORS | ❌ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account path (local dev) | ❌ |

### Frontend (`.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_BASE_URL` | Backend URL | ✅ |
| `VITE_GOOGLE_MAPS_API_KEY` | Google Maps API key | ❌ |

## 💰 Cost Analysis

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Gemini API | Free | $0 |
| BigQuery | Free tier (1 TB/mo) | $0 |
| Cloud Storage | Free tier (5 GB/mo) | $0 |
| Render Backend | Free | $0 |
| Vercel Frontend | Free | $0 |
| Resend Email | Free tier (100/day) | $0 |
| **TOTAL** | | **$0** |

Scaling to production (10k+ users)? Services scale from free to paid, but no billing surprises.

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.111.0
- **Server**: Uvicorn 0.30.1
- **Validation**: Pydantic 2.8.2
- **AI**: Google Gemini API 0.6.0
- **Database**: BigQuery (free tier)
- **Storage**: Cloud Storage (free tier)
- **Email**: Resend 2.3.0
- **Hosting**: Render (free tier)

### Frontend
- **Framework**: Vue 3
- **Build Tool**: Vite 5
- **Routing**: Vue Router 4
- **HTTP**: Axios
- **Styling**: Scoped CSS
- **Hosting**: Vercel (optional)

## 📋 Workflow

1. **Inspector takes photos** of street pavement
2. **Uploads to SnapMend** with location & notes
3. **Gemini AI analyzes** damage types & severity
4. **System calculates** repair priority & cost estimate
5. **BigQuery records** assessment for future reference
6. **Supervisor reviews** and creates work orders
7. **Repair crew executes** based on priority

## 🔐 Security

- ✅ CORS protection on API
- ✅ Environment variable secrets (no hardcoding)
- ✅ HTTPS only (Render, Vercel enforcement)
- ✅ Service account credentials isolated (local dev only)
- ✅ API key from Google's secure key management

For production: Add OAuth2, rate limiting, API key rotation.

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version (need 3.11+)
python --version

# Verify dependencies installed
pip list | grep fastapi

# Check Gemini API key
echo $GEMINI_API_KEY
```

### API returns 500 errors

```bash
# Check Render logs
# Check backend console for traceback
# Verify .env variables are set
curl http://localhost:8000/health
```

### Frontend can't connect to backend

```bash
# Verify VITE_API_BASE_URL in .env
# Check CORS headers: curl -I http://localhost:8000
# Check browser console for errors
# Ensure backend is running
```

See [Backend README](./backend/README.md) for more troubleshooting.

## 📈 Roadmap

- [x] Core assessment API
- [x] Gemini AI integration
- [x] Frontend dashboard
- [ ] BigQuery integration (repair history)
- [ ] Geospatial queries (nearby streets)
- [ ] Email notifications
- [ ] Work order management
- [ ] Mobile app (Capacitor)
- [ ] User authentication
- [ ] Advanced analytics
- [ ] PDF report generation
- [ ] Offline-first capability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/assessment-improvements`)
3. Commit changes (`git commit -m 'Add improved assessment logic'`)
4. Push to branch (`git push origin feature/assessment-improvements`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- 📖 Check [PRD_PART1_ARCHITECTURE.md](./PRD_PART1_ARCHITECTURE.md) for design questions
- 💻 Check [PRD_PART2_BACKEND.md](./PRD_PART2_BACKEND.md) for implementation questions
- 🔗 Check [backend/README.md](./backend/README.md) for API & deployment questions
- 🎨 Check [frontend/README.md](./frontend/README.md) for UI & styling questions

## 🎓 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Vue 3 Docs](https://vuejs.org)
- [Google Gemini API](https://ai.google.dev)
- [BigQuery Free Tier](https://cloud.google.com/bigquery/docs/free-tier)
- [Render Hosting](https://render.com/docs)

---

**Made for the hackathon without any billing account required!** ✨

Zero cost. Zero billing surprises. 100% open source.
