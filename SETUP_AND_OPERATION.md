# CogniShield - Setup & Operation Guide

**For: Development teams, Kiro agents, and other hackathon participants**

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Full Setup (15 minutes)](#full-setup)
3. [Running the Application](#running-the-application)
4. [API Testing](#api-testing)
5. [Frontend Usage](#frontend-usage)
6. [Troubleshooting](#troubleshooting)
7. [Architecture Overview](#architecture-overview)

---

## Quick Start

### Prerequisites
- **Windows 10+** (or macOS/Linux with equivalent tools)
- **Node.js 18+** (for frontend)
- **Python 3.9+** (for backend)
- **Git** (optional)
- **Gemini API Key** (from Google Cloud Console)

### 30-Second Start
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Frontend
npm install
npm run dev
```

Then:
- Open `http://localhost:3000` (frontend)
- API at `http://localhost:8000`
- API docs at `http://localhost:8000/docs`

---

## Full Setup

### Step 1: Clone/Navigate to Project
```bash
cd c:\Users\<username>\Downloads\COGNISHIELD
```

### Step 2: Set Up Backend

#### 2.1 Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM for database
- `google-generativeai` - Gemini API client
- `python-multipart` - File upload handling
- `pytest` - Testing framework

#### 2.2 Configure Environment Variables
Create `.env` file in `backend/` directory:

```bash
# Backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
DATABASE_URL=sqlite:///./data/cognishield.db
STORAGE_DIR=./storage
MAX_IMAGE_SIZE_MB=20
MAX_VIDEO_SIZE_MB=200
MAX_VIDEO_DURATION_SECONDS=120
ENABLE_CACHING=true
ENABLE_RULE_ENGINE=true
ENABLE_GUARDRAILS=true
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**How to get Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key into `.env`

#### 2.3 Create Data Directory
```bash
mkdir backend\data
mkdir backend\storage
mkdir backend\storage\uploads
mkdir backend\storage\.cache
```

### Step 3: Set Up Frontend

#### 3.1 Install Node Dependencies
```bash
npm install
```

**Note:** If npm install fails, try:
```bash
npm install --legacy-peer-deps
```

#### 3.2 Environment Variables (Frontend)
Create `.env.local` in root directory:

```bash
# .env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000/api
```

### Step 4: Verify Installation

#### Backend Health Check
```bash
# In backend directory
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "database": "ok",
  "storage": "ok",
  "gemini_configured": true,
  "gemini_model": "gemini-2.0-flash-exp"
}
```

#### Frontend Build Check
```bash
npm run build
```

Should complete without errors.

---

## Running the Application

### Method 1: Two Terminal Windows (Recommended for Development)

#### Terminal 1: Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Output should show:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

#### Terminal 2: Frontend Development Server
```bash
npm run dev
```

Output should show:
```
▲ Next.js 16.0.0
- ready started server on 0.0.0.0:3000
- event compiled successfully
```

Then open: **http://localhost:3000**

### Method 2: Single Terminal (Production Build)

```bash
# Build frontend
npm run build

# Start backend
cd backend
uvicorn app.main:app --port 8000

# In separate terminal, start frontend
npm start
```

### Method 3: Using Docker (Optional)

```bash
# Build images
docker-compose build

# Start both services
docker-compose up
```

---

## API Testing

### 1. Test Health Endpoint

```bash
curl http://localhost:8000/api/health
```

### 2. List Audits

```bash
curl http://localhost:8000/api/analyses?page=1&page_size=10
```

### 3. Upload and Analyze Image

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/analyze/image \
  -F "file=@screenshot.png" \
  -F "application_name=FinFlow" \
  -F "platform=iOS" \
  -F "analysis_depth=Deep analysis"
```

**Response:**
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 5,
  "current_stage": "Queued for analysis"
}
```

### 4. Get Audit Results

```bash
# Use audit_id from previous response
curl http://localhost:8000/api/analysis/550e8400-e29b-41d4-a716-446655440000
```

### 5. List All Findings

```bash
curl http://localhost:8000/api/findings?page=1&page_size=20
```

### 6. Filter by Severity

```bash
curl http://localhost:8000/api/findings?severity=high
```

### Interactive API Testing

Open: **http://localhost:8000/docs**

This opens Swagger UI where you can:
- Test all endpoints
- See request/response schemas
- Authorize (if auth is enabled)
- View error responses

---

## Frontend Usage

### Dashboard Page
1. **URL:** `http://localhost:3000`
2. **View:** Latest audit summary
3. **Shows:**
   - Risk score visualization
   - Finding count by severity
   - Sample findings with evidence

### New Audit Page
1. **Navigation:** Click "New Audit" in sidebar
2. **Upload:**
   - Select Screenshot or Screen Recording tab
   - Click "Browse files" or drag & drop
   - Supports: PNG, JPG, WEBP (images) or MP4, MOV (video)
   - Max size: 20MB (images), 200MB (video)
3. **Metadata:**
   - Application name: e.g., "FinFlow Mobile Banking"
   - Platform: iOS, Android, or Web
   - Analysis depth: Deep analysis (default) or Quick scan
4. **Submit:** Click "Run AI Audit"

### Evidence Page
1. **Navigation:** Click "View Sample Audit" or "Evidence" in sidebar
2. **View:**
   - Phone preview with annotated evidence boxes
   - Finding cards on the right
   - Click on finding to see details
3. **Annotations:**
   - Red box = High severity
   - Amber box = Medium severity
   - Green box = Low severity

### Findings Page
1. **Navigation:** Click "Findings" in sidebar
2. **View:** Table of all findings
3. **Columns:** Pattern, Application, Severity, Confidence, Detected, Status
4. **Filter:**
   - All findings (default)
   - High severity only
   - Medium severity only
5. **Search:** Search by pattern name

### Reports Page
1. **Navigation:** Click "Reports" in sidebar
2. **Actions:**
   - Export JSON report
   - Export PDF report (coming soon)
3. **Contents:**
   - Full audit summary
   - All findings with details
   - Risk scoring methodology

---

## Troubleshooting

### Issue: "Cannot find module 'react'"

**Solution:**
```bash
npm install
npm run build
```

Then restart dev server.

### Issue: "Connection refused" when frontend tries to reach API

**Cause:** Backend not running

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# If failed, start backend
cd backend
uvicorn app.main:app --reload
```

### Issue: "Gemini API key not configured"

**Cause:** `.env` file missing or invalid key

**Solution:**
1. Verify `.env` exists in `backend/` directory
2. Check key format (should be ~40 characters)
3. Get new key from [Google AI Studio](https://makersuite.google.com/app/apikey)
4. Restart backend after updating

### Issue: "Database locked" error

**Cause:** SQLite file already open in another process

**Solution:**
```bash
# Windows: Kill Python processes
taskkill /IM python.exe /F

# Then restart backend
cd backend
uvicorn app.main:app --reload
```

### Issue: Port 3000 or 8000 already in use

**Solution:**
```bash
# Windows: Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue: Image upload fails

**Cause:** File size > 20MB or unsupported format

**Solution:**
- Use PNG, JPG, or WEBP
- Compress image if >20MB
- Check file type: `file screenshot.png`

### Issue: Backend tests failing

**Solution:**
```bash
cd backend
pytest tests/ -v

# Run specific test
pytest tests/test_guardrails.py -v

# If Windows file locking issue:
pytest tests/ -v --tb=short
```

Expected output:
```
45 passed in 2.34s
```

---

## Architecture Overview

### Directory Structure

```
COGNISHIELD/
├── app/                          # Next.js Frontend
│   ├── page.tsx                  # Main dashboard
│   ├── layout.tsx                # Layout wrapper
│   └── globals.css               # Global styles
│
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── main.py              # Entry point, startup
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # DB connection
│   │   ├── api/                 # API routes
│   │   │   ├── audits.py        # Upload & analysis
│   │   │   ├── findings.py      # Finding endpoints
│   │   │   ├── evidence.py      # Evidence endpoints
│   │   │   ├── reports.py       # Report generation
│   │   │   └── health.py        # Health checks
│   │   ├── models/              # Database models
│   │   │   ├── audit.py         # Audit model
│   │   │   ├── finding.py       # Finding model
│   │   │   ├── evidence.py      # Evidence model
│   │   │   ├── pattern_rule.py  # Rules model
│   │   │   └── analysis_job.py  # Job tracking
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── analysis_service.py     # Orchestration
│   │   │   ├── gemini_service.py       # LLM API
│   │   │   ├── rule_engine.py          # Rule matching
│   │   │   └── cache_service.py        # Content caching
│   │   ├── utils/               # Helpers
│   │   │   ├── guardrails.py    # Validation
│   │   │   ├── validators.py    # File validation
│   │   │   └── scoring.py       # Risk scoring
│   │   └── prompts/             # AI prompts
│   │
│   ├── tests/                   # Test suite (45 tests)
│   │   ├── test_guardrails.py
│   │   ├── test_rule_engine.py
│   │   ├── test_caching.py
│   │   └── test_validators.py
│   │
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment config
│   └── data/                     # Database storage
│
├── components/                  # Reusable React components
├── lib/                        # Utility functions
├── public/                     # Static assets
│
├── package.json               # Node dependencies
├── tsconfig.json             # TypeScript config
├── next.config.mjs           # Next.js config
│
├── HACKATHON_PRESENTATION.md  # Presentation slides
└── SETUP_AND_OPERATION.md     # This file
```

### Data Flow

```
User Action
    ↓
Frontend (Next.js) sends HTTP request
    ↓
FastAPI Router receives request
    ↓
Service Layer processes:
    ├─ CacheService (check cache)
    ├─ RuleEngine (detect patterns)
    ├─ GeminiService (if needed)
    ├─ HallucinationGuardrails (validate)
    └─ Database (store results)
    ↓
Response sent back to Frontend
    ↓
Frontend renders results
```

### Key Services

| Service | Responsibility | Files |
|---------|---|---|
| **AnalysisService** | Orchestrate analysis pipeline | `app/services/analysis_service.py` |
| **RuleEngine** | Fast pattern detection | `app/services/rule_engine.py` |
| **CacheService** | Content-hash based caching | `app/services/cache_service.py` |
| **GeminiService** | LLM API integration | `app/services/gemini_service.py` |
| **HallucinationGuardrail** | Validate AI findings | `app/utils/guardrails.py` |

---

## Common Tasks

### Task: Analyze a New Fintech App

1. Take screenshot of the app UI
2. Go to `http://localhost:3000/new-audit`
3. Upload screenshot
4. Enter app name and platform
5. Click "Run AI Audit"
6. Wait for analysis (typically <30 seconds)
7. View results in Evidence tab

### Task: Export Audit Report

1. Go to Evidence page
2. Click "Export Report" button
3. Choose format: JSON or PDF
4. File downloads to your computer

### Task: Compare Before/After

1. Make changes to fintech app UI
2. Take new screenshot
3. Upload as new audit
4. System will use same file hash if unchanged (instant)
5. Or re-analyze if changed
6. View side-by-side comparison

### Task: Run Backend Tests

```bash
cd backend
pytest tests/ -v

# Or specific test file
pytest tests/test_guardrails.py -v

# Or specific test function
pytest tests/test_guardrails.py::test_validate_finding -v
```

### Task: Check API Documentation

1. Go to `http://localhost:8000/docs`
2. Swagger UI opens
3. Expand any endpoint
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"
7. View response

### Task: Debug Backend Issues

```bash
# Enable debug logging
set ENVIRONMENT=development
set LOG_LEVEL=DEBUG
uvicorn app.main:app --reload

# Check database
sqlite3 backend/data/cognishield.db
.tables
SELECT COUNT(*) FROM audits;
```

### Task: Reset Database

```bash
# Delete database file
del backend\data\cognishield.db

# Restart backend (recreates schema)
cd backend
uvicorn app.main:app --reload
```

---

## Performance Tips

### Frontend Optimization
- Images are lazy-loaded on dashboard
- Evidence page uses React.memo for phone preview
- Findings table is paginated (default 20 per page)

### Backend Optimization
- Caching layer saves 50% of Gemini API calls
- Rule engine detects obvious patterns in milliseconds
- Database queries use indexed fields
- Cascade delete prevents orphaned records

### API Rate Limiting
Currently unlimited. For production, add:
- 100 requests/minute per IP
- 10 video uploads/day per user
- 1000 requests/day per API key

---

## Support & Debugging

### Getting Help

1. **Check logs:** Look at terminal output for error messages
2. **API docs:** Visit `http://localhost:8000/docs` for full reference
3. **Backend tests:** Run `pytest tests/ -v` to identify issues
4. **Health check:** Verify `http://localhost:8000/api/health` returns 200

### Reporting Issues

Include:
- Error message (full text)
- Steps to reproduce
- Environment (Windows version, Python version, Node version)
- Log output (from terminal)

### Contact

For questions during hackathon, reach out to the development team.

---

## Production Deployment (Future)

### Environment Setup

```bash
# Production .env
ENVIRONMENT=production
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://cognishield.example.com
GEMINI_API_KEY=... (use secrets manager)
```

### Deployment Platforms

- **Frontend:** Vercel (optimized for Next.js)
- **Backend:** AWS EC2 / Google Cloud Run / Digital Ocean
- **Database:** PostgreSQL (on managed service)
- **Storage:** AWS S3 or Google Cloud Storage

### Scaling

- Add load balancer for multiple backend instances
- Use Redis for distributed caching
- Implement request queuing for video analysis
- Monitor with Datadog / NewRelic

---

**END OF SETUP & OPERATION GUIDE**

For more details, see `HACKATHON_PRESENTATION.md` for the full project overview.
