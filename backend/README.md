# SnapMend Backend API

FastAPI-based backend for municipal street pavement assessment and repair management system.

## Features

- 🤖 **Pavement Assessment**: Uses Google Gemini API for intelligent image analysis
- 📊 **Repair History**: BigQuery integration for historical repair data
- 🗺️ **Geospatial Queries**: Find nearby streets using BigQuery spatial functions
- 📧 **Notifications**: Email notifications via Resend API
- ☁️ **Zero Billing**: Uses free-tier GCP services (BigQuery, Cloud Storage)

## Tech Stack

- **Framework**: FastAPI 0.111.0
- **Server**: Uvicorn 0.30.1
- **AI**: Google Gemini API (free tier)
- **Database**: BigQuery (free tier)
- **Storage**: Cloud Storage (free tier)
- **Deployment**: Render (free tier)

## Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Get Gemini API Key**:
   - Go to [ai.google.dev](https://ai.google.dev)
   - Click "Get API Key"
   - Copy to GEMINI_API_KEY in .env

4. **Run locally**:
   ```bash
   python main.py
   ```
   - API available at `http://localhost:8000`
   - Interactive docs at `http://localhost:8000/docs`

## API Endpoints

### Assessment
- `POST /api/assessment/evaluate` - Assess pavement condition from images
- `GET /api/assessment/health` - Health check

### Repair Management
- `GET /api/repair/history/{street_segment_id}` - Get repair history
- `GET /api/repair/nearby` - Find nearby streets
- `POST /api/repair/work-order` - Create repair work order
- `GET /api/repair/health` - Health check

### System
- `GET /` - API info
- `GET /health` - System health

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | ✅ |
| `GCS_BUCKET_NAME` | Cloud Storage bucket name | ✅ |
| `BQ_DATASET` | BigQuery dataset name | ✅ |
| `GEMINI_API_KEY` | Gemini API key (free from ai.google.dev) | ✅ |
| `RESEND_API_KEY` | Email API key | ✅ |
| `NOTIFICATION_FROM_EMAIL` | From address for emails | ✅ |
| `NOTIFICATION_TO_EMAIL` | Supervisor email address | ✅ |
| `FRONTEND_URL` | Frontend URL for CORS | ❌ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account path (local dev only) | ❌ |

## Deployment to Render

1. **Push to GitHub**:
   ```bash
   git push origin main
   ```

2. **Create Render Service**:
   - Go to [render.com](https://render.com)
   - New > Web Service
   - Connect GitHub repository
   - Select branch: `main`
   - Runtime: `Python 3.11`
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`

3. **Environment Variables** (in Render dashboard):
   - Add all variables from `.env`

4. **Deploy**:
   - Backend URL: `https://snapmend-backend.onrender.com`

## Development Notes

- Assessment service returns mock data until BigQuery integration complete
- Images are base64-encoded for Gemini API
- Free tier Gemini doesn't support GCS URIs directly
- For production image upload, use Cloud Storage signed URLs

## Testing

Get Gemini API response:
```bash
curl -X POST http://localhost:8000/api/assessment/evaluate \
  -F "street_segment_id=STR001" \
  -F "inspector_name=John Doe" \
  -F "gps_latitude=40.7128" \
  -F "gps_longitude=-74.0060" \
  -F "images=@pavement.jpg"
```

Check API health:
```bash
curl http://localhost:8000/health
```

## Next Steps

- [ ] Integrate BigQuery for repair history queries
- [ ] Implement geospatial queries for nearby streets
- [ ] Add image upload to Cloud Storage
- [ ] Implement email notifications with Resend
- [ ] Add authentication/authorization
- [ ] Add database models for caching
- [ ] Performance monitoring and logging

## Cost Analysis

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Render Backend | Free | $0 |
| Gemini API | Free | $0 |
| BigQuery | Free tier (1 TB/mo) | $0 |
| Cloud Storage | Free tier (5 GB/mo) | $0 |
| Resend Email | Free tier (100/day) | $0 |
| **TOTAL** | | **$0** |

## Support

For issues or questions, check the [PRD documentation](../PRD_PART2_BACKEND.md).
