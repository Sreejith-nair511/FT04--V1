# CogniShield Backend - Dark-Pattern Auditor for FinTech

This is the production-grade backend for the CogniShield AI dark-pattern auditing system. It provides REST APIs for analyzing fintech applications for deceptive design patterns.

## Quick Start (5 minutes)

### Prerequisites

- Python 3.11 or higher
- pip or venv

### 1. Create Virtual Environment

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
copy .env.example .env
```

### 4. Add Gemini API Key (Optional for Demo)

Edit `.env`:
```
GEMINI_API_KEY=your_actual_api_key_here
```

Without an API key, the system runs in **DEMO MODE** and returns synthetic analysis results.

### 5. Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

The backend will:
- Create storage directories
- Initialize the SQLite database
- Start listening on http://localhost:8000

Visit http://localhost:8000/docs for interactive API documentation.

---

## System Requirements

### Minimum
- Python 3.11+
- 100MB disk space
- 256MB RAM

### Recommended
- Python 3.11+
- 1GB disk space (for video storage)
- 512MB RAM

---

## Backend Architecture

```
Frontend (Next.js)
    ↓ REST API
FastAPI Backend
    ↓
Analysis Service
    ├── Gemini Service (AI Analysis)
    ├── Database Service (SQLite)
    └── Storage Service (Local FS)
    ↓
SQLite Database + Local Storage
```

### Key Components

1. **FastAPI** - REST API framework
2. **SQLAlchemy 2.x** - ORM for database operations
3. **SQLite** - Local database (no external DB needed)
4. **Gemini API** - Google's AI for image/video analysis
5. **Pydantic** - Data validation

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database setup
│   ├── api/                       # API routes
│   │   ├── health.py
│   │   ├── audits.py
│   │   ├── findings.py
│   │   ├── evidence.py
│   │   └── reports.py
│   ├── models/                    # SQLAlchemy models
│   │   ├── audit.py
│   │   ├── finding.py
│   │   ├── evidence.py
│   │   └── analysis_job.py
│   ├── schemas/                   # Pydantic schemas
│   │   ├── audit.py
│   │   ├── finding.py
│   │   ├── evidence.py
│   │   └── analysis.py
│   ├── services/                  # Business logic
│   │   ├── gemini_service.py
│   │   └── analysis_service.py
│   ├── utils/                     # Helper functions
│   │   ├── security.py
│   │   ├── validators.py
│   │   ├── scoring.py
│   │   └── json_parser.py
│   └── prompts/                   # AI system prompts
│       ├── image_analysis.txt
│       └── video_analysis.txt
├── data/                          # SQLite database (created at runtime)
├── storage/                       # Uploaded files and reports
├── requirements.txt
├── .env.example
└── README.md
```

---

## Configuration

### Environment Variables (`.env`)

```bash
# Gemini API - REQUIRED for production
GEMINI_API_KEY=sk_...
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_THINKING_LEVEL=medium

# Database
DATABASE_URL=sqlite:///./data/cognishield.db

# Storage
STORAGE_DIR=./storage
MAX_IMAGE_SIZE_MB=20
MAX_VIDEO_SIZE_MB=200

# CORS - Frontend URL
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Demo Mode
DEMO_MODE=false
```

### Key Configuration Notes

- **`GEMINI_API_KEY`**: Leave blank to run in DEMO MODE
- **`DATABASE_URL`**: SQLite file path. Creates `data/cognishield.db`
- **`CORS_ORIGINS`**: Must match your frontend URL
- **`DEMO_MODE`**: Set to `true` to ignore API key and use synthetic data

---

## API Endpoints

### Health

- `GET /api/health` - Backend health check
- `GET /api/health/gemini` - Gemini API connectivity

### Audits

- `POST /api/analyze/image` - Upload and analyze screenshot
- `POST /api/analyze/video` - Upload and analyze video
- `GET /api/analysis/{audit_id}` - Get audit with findings
- `GET /api/analysis/{audit_id}/status` - Get analysis progress
- `GET /api/analyses` - List all audits (with pagination)
- `DELETE /api/audits/{audit_id}` - Delete audit

### Findings

- `GET /api/findings` - List findings (with filters)
- `GET /api/findings/{finding_id}` - Get single finding

### Evidence

- `GET /api/evidence/{evidence_id}` - Get evidence details

### Reports

- `POST /api/reports/{audit_id}/pdf` - Generate PDF report
- `POST /api/reports/{audit_id}/json` - Generate JSON report
- `GET /api/reports/{audit_id}` - Get report metadata

---

## Database

### SQLite Storage

Database file: `backend/data/cognishield.db`

Created automatically on first run. No external database needed.

### Schema

**Audits Table**
- Stores uploaded analysis requests
- Links to findings and evidence
- Tracks analysis status and risk scores

**Findings Table**
- Detected dark patterns
- Severity, confidence scores
- Remediation guidance

**Evidence Table**
- Visual bounding boxes for findings
- Normalized coordinates (0.0-1.0)
- Timestamps for video evidence

**AnalysisJobs Table**
- Tracks analysis progress
- Status and current stage
- Error messages if failed

---

## Working with the Database

### View Database

```bash
# Using SQLite CLI
sqlite3 backend/data/cognishield.db

# Example queries:
sqlite> SELECT * FROM audits;
sqlite> SELECT * FROM findings WHERE severity='high';
```

### Reset Database

```bash
# Windows
del backend\data\cognishield.db

# macOS/Linux
rm backend/data/cognishield.db

# Database recreates on next run
```

---

## Gemini API Integration

### Getting an API Key

1. Visit: https://aistudio.google.com/app/apikeys
2. Click "Create API Key"
3. Copy the key to `.env`: `GEMINI_API_KEY=...`

### Models Supported

- **gemini-2.0-flash-exp** (default, recommended)
- Other Gemini models by updating `GEMINI_MODEL` in `.env`

### Analysis Workflow

1. **Image Analysis**
   - Client sends PNG/JPG/WEBP
   - Backend uploads to Gemini
   - Gemini analyzes for dark patterns
   - Results stored in database

2. **Video Analysis**
   - Client sends MP4/MOV/WEBM
   - Backend processes with Gemini
   - Extracts key frames
   - Stores timestamps and evidence

### Without Gemini API Key

Set `DEMO_MODE=true` or omit API key. System returns:
- Pre-defined "FinFlow" sample audit
- 3 synthetic dark pattern findings
- Full audit UI functionality

---

## File Storage

### Storage Locations

```
storage/
├── uploads/          # Original uploaded files
├── frames/           # Extracted video frames
└── reports/          # Generated PDF/JSON reports
```

### File Naming

All files use safe naming to prevent path traversal:
```
{audit_uuid}_original.{extension}

Example:
550e8400-e29b-41d4-a716-446655440000_original.png
```

### Cleanup

Delete storage folder to clear all uploaded files:
```bash
# Windows
rmdir /s /q storage

# macOS/Linux
rm -rf storage
```

---

## Testing

### Unit Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=app
```

### Example Tests

- Health endpoint connectivity
- File upload validation
- Database operations
- Risk score calculation
- Gemini response parsing

---

## Troubleshooting

### "Connection refused" on port 8000

**Problem:** Another app is using port 8000

**Solution:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

Or kill the process:
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000 | kill -9
```

### "No module named 'app'"

**Problem:** Running from wrong directory

**Solution:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### "Gemini API key missing"

**Problem:** No API key configured

**Solution:**
1. Get key from https://aistudio.google.com/app/apikeys
2. Add to `.env`: `GEMINI_API_KEY=...`
3. Or run in DEMO MODE: `DEMO_MODE=true`

### "Database locked" error

**Problem:** SQLite is being accessed by multiple processes

**Solution:**
- Restart backend
- Ensure only one backend instance is running
- Delete and recreate database

### "File too large" error

**Problem:** Uploaded file exceeds limits

**Solution:**
- Images: max 20MB (set `MAX_IMAGE_SIZE_MB`)
- Videos: max 200MB (set `MAX_VIDEO_SIZE_MB`)
- Compress media or update `.env`

### "CORS error from frontend"

**Problem:** Frontend can't reach backend

**Solution:**
1. Check backend is running: `http://localhost:8000/api/health`
2. Frontend has correct API URL: `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Check `.env`: `CORS_ORIGINS=http://localhost:3000`

---

## Performance Tips

### Image Analysis

- Resize images < 5MB for faster processing
- JPEG format preferred for Gemini
- Quality 85% is sufficient for pattern detection

### Video Analysis

- 15-60 second videos optimal
- Resolution 720p-1080p sufficient
- MP4 format recommended

### Database

- Add indexes for frequent queries (not needed for MVP)
- Periodic cleanup of old audits
- SQLite handles concurrent reads fine

---

## Security Considerations

### File Upload

- File types strictly validated (PNG, JPG, MP4, MOV)
- Filenames sanitized to prevent path traversal
- File sizes capped (20MB images, 200MB videos)
- Uploaded files stored outside web root

### API Security

- CORS restricted to frontend origin
- No sensitive data in error responses
- Gemini API key never exposed to frontend
- Input validation on all endpoints

### Database

- SQLite foreign keys enabled
- No direct SQL injection possible (ORM used)
- Automatic data cleanup on audit deletion

---

## Production Deployment

### Local Development

```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --port 8000
```

### Production Ready

```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Docker (Optional)

```bash
docker build -t cognishield-backend .
docker run -p 8000:8000 --env-file .env cognishield-backend
```

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Database Guide**: See `DATABASE.md`
- **Gemini Integration**: See `GEMINI_INTEGRATION.md`
- **Architecture**: See `ARCHITECTURE.md`

---

## Next Steps

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev` (in project root)
3. Visit http://localhost:3000
4. Upload a screenshot
5. See analysis appear in real-time

Happy auditing! 🛡️
