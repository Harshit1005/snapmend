# SnapMend Frontend

Vue 3 + Vite frontend for municipal street pavement assessment platform.

## Features

- 📸 Multi-image assessment form
- 🤖 Real-time AI analysis feedback
- 📊 Repair history & statistics
- 🗺️ GPS-based location tracking
- 💰 Cost estimates & priority scores
- 📱 Mobile-responsive design
- ✅ Zero backend billing required

## Tech Stack

- **Framework**: Vue 3
- **Build Tool**: Vite 5
- **Styling**: Scoped CSS
- **API**: Axios
- **Routing**: Vue Router 4

## Development

### Setup

```bash
cd frontend
npm install
```

### Environment

```bash
cp .env.example .env
# Edit .env with your backend URL
```

```
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_MAPS_API_KEY=AIza...
```

### Run Development Server

```bash
npm run dev
```

Frontend available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Output in `dist/` directory ready for deployment.

## Project Structure

```
src/
├── main.js              # Vue app entry point
├── App.vue              # Root component
├── router.js            # Route definitions
├── components/
│   ├── AssessmentForm.vue    # Image upload & analysis
│   └── RepairHistory.vue     # Historical repair records
├── views/
│   ├── Dashboard.vue    # Landing/status page
│   └── Assessment.vue   # Assessment workflow
└── services/
    └── api.js           # API client functions
```

## Components

### Dashboard (`views/Dashboard.vue`)
- System status indicators
- Quick start guide
- Feature overview
- Assessment navigation

### Assessment (`views/Assessment.vue`)
- Integrates AssessmentForm & RepairHistory
- Assessment workflow management

### AssessmentForm (`components/AssessmentForm.vue`)
- Street segment & inspector info
- Multi-image upload
- Form validation
- Results display with severity badges

### RepairHistory (`components/RepairHistory.vue`)
- Fetches historical repairs for street segment
- Cost & contractor info
- Timeline view

## API Integration

All API calls through `services/api.js`:

```javascript
// Assessment
assessmentAPI.evaluate(formData)
assessmentAPI.getHealth()

// Repair History
repairAPI.getHistory(streetId, limit)
repairAPI.getNearby(lat, lon, radius)
repairAPI.createWorkOrder(streetId, priority, cost)
repairAPI.getHealth()

// System
systemAPI.getInfo()
systemAPI.getHealth()
```

## Deployment

### Vercel (Recommended)

1. **Connect to GitHub**:
   - Push code to GitHub
   - Go to [vercel.com](https://vercel.com)
   - Import repository
   - Select root: `frontend`

2. **Configure Environment**:
   - Set `VITE_API_BASE_URL` to your Render backend URL
   - Example: `https://snapmend-backend.onrender.com`

3. **Deploy**:
   - Vercel auto-deploys on push
   - Frontend available at `snapmend-frontend.vercel.app`

### Netlify

```bash
# Build
npm run build

# Deploy
netlify deploy --prod --dir=dist
```

## Styling

Uses scoped CSS with responsive grid layouts:
- Mobile-first design (320px+)
- Tablet optimized (768px+)
- Desktop optimized (1200px+)

Color scheme:
- Primary: #667eea (purple)
- Secondary: #764ba2 (dark purple)
- Success: #4caf50 (green)
- Error: #d32f2f (red)

## Performance

- **Lazy loading**: Routes loaded on demand
- **Code splitting**: Automatic with Vite
- **Minimal bundle**: Vue 3 tree-shaking
- **Image optimization**: Browser caching

## Troubleshooting

**API connection failing?**
- Check `VITE_API_BASE_URL` in `.env`
- Ensure backend is running and accessible
- Check browser console for CORS errors

**Images not uploading?**
- Verify file input accepts image/* MIME types
- Check backend multipart form-data handling
- File size limits on Render/Vercel

**Styling looks broken?**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard reload page (Ctrl+Shift+R)
- Check scoped CSS selectors

## Next Steps

- [ ] Add Google Maps integration for location
- [ ] Implement user authentication
- [ ] Add offline-first capability with IndexedDB
- [ ] Build mobile app with Capacitor
- [ ] Add data export/PDF reports
- [ ] Implement real-time collaboration features
- [ ] Add advanced filtering & analytics
