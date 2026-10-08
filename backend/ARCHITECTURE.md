# CogniShield Backend Architecture

## System Overview

```
┌─────────────────────────────────────┐
│   Next.js Frontend (Port 3000)      │
│   - Upload UI                       │
│   - Analysis Dashboard              │
│   - Evidence Viewer                 │
└────────────────┬────────────────────┘
                 │ REST API
                 ↓ (JSON)
┌─────────────────────────────────────┐
│     FastAPI Backend (Port 8000)     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   API Layer                 │   │
│  │  - /api/analyze/image       │   │
│  │  - /api/analyze/video       │   │
│  │  - /api/findings            │   │
│  │  - /api/reports             │   │
│  └────────┬────────────────────┘   │
│           │                        │
│  ┌────────▼────────────────────┐   │
│  │   Service Layer             │   │
│  │  - Analysis Service         │   │
│  │  - Gemini Service           │   │
│  │  - Storage Service          │   │
│  └────────┬────────────────────┘   │
│           │                        │
│  ┌────────▼────────────────────┐   │
│  │   Data Layer (SQLAlchemy)   │   │
│  │  - ORM Models               │   │
│  │  - Relationships            │   │
│  └────────┬────────────────────┘   │
│           │                        │
└───────────┼──────────────────────────┘
            │
    ┌───────┴────────────┬──────────────┐
    ↓                    ↓              ↓
┌─────────┐      ┌──────────────┐  ┌──────────┐
│ SQLite  │      │  Local FS    │  │ Gemini   │
│ Database│      │  - Uploads   │  │   API    │
│         │      │  - Frames    │  │          │
│ audits  │      │  - Reports   │  │ Analysis │
│ findings│      └──────────────┘  └──────────┘
│ evidence│
└─────────┘
```

---

## Data Flow

### Image Upload & Analysis Flow

```
1. User uploads screenshot
   POST /api/analyze/image
   - File validation
   - Create Audit record (status: queued)
   - Create AnalysisJob record
   - Save file to storage/uploads/

2. Background task starts
   - Update job: processing, 20%
   - Read image file
   - Send to Gemini API
   - Wait for response

3. Gemini Response
   - Parse JSON response
   - Extract findings array
   - Validate with Pydantic

4. Create Database Records
   - For each finding:
     - Create Finding record
     - Create Evidence record (with bounding box)
   - Calculate overall risk score

5. Update Audit
   - Set status: completed
   - Set risk_score, risk_level
   - Set completed_at timestamp

6. Return to Frontend
   - audit_id for polling
   - status: completed
   - findings appear in UI
```

### Video Upload & Analysis Flow

```
1. User uploads video
   POST /api/analyze/video
   - File validation (MP4, MOV, WEBM)
   - Create Audit record (status: queued)
   - Create AnalysisJob record
   - Save file to storage/uploads/

2. Background task starts
   - Update job: processing, 15%
   - Upload video to Gemini (or process locally)
   - Gemini analyzes for patterns

3. Frame Extraction
   - For each finding with timestamp_seconds:
     - Extract frame at that time using OpenCV
     - Save to storage/frames/{audit_id}/
     - Link to Evidence record

4. Create Database Records
   - For each finding:
     - Create Finding (with timestamp_seconds)
     - Create Evidence (with frame_number, normalized coords)

5. Complete Audit
   - Risk score calculation
   - Set status: completed
```

---

## Component Responsibilities

### API Layer (`app/api/`)

**health.py**
- `/api/health` - System status
- `/api/health/gemini` - Gemini connectivity

**audits.py**
- Image upload & analysis
- Video upload & analysis
- Audit retrieval
- Audit listing with pagination

**findings.py**
- Finding listing with filters
- Single finding retrieval
- Severity filtering

**evidence.py**
- Evidence item retrieval
- Evidence coordinates

**reports.py**
- PDF report generation
- JSON export
- Report metadata

### Service Layer (`app/services/`)

**GeminiService**
```python
class GeminiService:
    def analyze_image(image_path) → Dict
    def analyze_video(video_path) → Dict
    def health_check() → bool
    
    # Private helpers
    def _read_image() → str
    def _load_system_prompt() → str
    def _parse_gemini_response() → Dict
```

**AnalysisService**
```python
class AnalysisService:
    def create_audit() → Audit
    def create_analysis_job() → AnalysisJob
    def update_job_progress()
    def create_findings_from_analysis()
    def complete_audit()
    def fail_audit()
    def get_audit_with_findings()
```

### Database Models (`app/models/`)

**Audit**
- application_name, platform, input_type
- status, risk_score, risk_level
- file_path, model_name
- created_at, updated_at, completed_at

**Finding**
- category, title
- severity, confidence
- evidence_text, why_problematic, user_impact, recommended_fix
- One-to-many with Evidence

**Evidence**
- evidence_type (box, text, interactive)
- x, y, width, height (normalized 0.0-1.0)
- timestamp_seconds (for videos)
- image_path
- Many-to-one with Finding

**AnalysisJob**
- status, progress, current_stage
- error_message
- started_at, completed_at
- One-to-one with Audit

### Utility Layer (`app/utils/`)

**security.py**
- `generate_safe_filename()` - Prevent path traversal
- `validate_file_path()` - Check file is in base dir
- `ensure_directory()` - Create dir if needed

**validators.py**
- `validate_image_file()` - Check PNG/JPG/WEBP, size
- `validate_video_file()` - Check MP4/MOV, size

**scoring.py**
- `severity_to_weight()` - low=3, medium=8, high=15, critical=25
- `calculate_risk_score()` - Sum weighted severities, cap at 100

---

## Coordinate System

### Normalized Coordinates (Backend → Database)

All coordinates stored as **0.0 to 1.0** normalized values:
- Independent of image resolution
- Easy to scale to any screen size

```
x: 0.0 (left edge) → 1.0 (right edge)
y: 0.0 (top edge) → 1.0 (bottom edge)
width: 0.0 (none) → 1.0 (full width)
height: 0.0 (none) → 1.0 (full height)
```

### CSS Percentage Conversion (Database → Frontend)

Frontend converts to CSS percentages for the phone preview:

```typescript
// Backend: { x: 0.18, y: 0.57, width: 0.64, height: 0.14 }
// Frontend:
left: "18%"    // x * 100
top: "57%"     // y * 100
width: "64%"   // width * 100
height: "14%"  // height * 100
```

---

## Risk Scoring Algorithm

### Deterministic Calculation

```
Base Score = 0

For each finding:
  weight = severity_to_weight(severity)
  // critical=25, high=15, medium=8, low=3
  
  normalized_confidence = confidence / 100
  finding_score = weight * normalized_confidence
  
  base_score += finding_score

final_score = min(base_score, 100)
```

### Risk Level Mapping

```
0-24     → LOW
25-49    → MEDIUM
50-74    → HIGH
75-100   → CRITICAL
```

### Example

```
Finding 1: high severity, 94% confidence
  → 15 * 0.94 = 14.1

Finding 2: high severity, 89% confidence
  → 15 * 0.89 = 13.35

Finding 3: medium severity, 82% confidence
  → 8 * 0.82 = 6.56

Total: 14.1 + 13.35 + 6.56 = 34.01
Risk Level: MEDIUM
```

---

## State Transitions

### Audit Status Flow

```
       ┌─────────┐
       │ created │
       └────┬────┘
            │ (AnalysisJob created)
            ↓
       ┌─────────┐
       │ queued  │
       └────┬────┘
            │ (Background task starts)
            ↓
    ┌───────────────┐
    │  processing   │
    │  (% progress) │
    └────┬────┬────┐
         │    │    │
         │    │    └─(Error)→┌─────────┐
         │    │               │ failed  │
         │    │               └─────────┘
         │    │
         │    └─(Analysis fails)→┌────────┐
         │                       │ failed │
         │                       └────────┘
         │
         └─(Success)→┌───────────┐
                     │ completed │
                     └───────────┘
```

### Analysis Job Stages

```
1. Queued (0%)
2. Uploading evidence (20%)
3. Extracting interface (40%)
4. Analyzing visual hierarchy (60%)
5. Detecting dark patterns (80%)
6. Calculating risk (90%)
7. Saving results (95%)
8. Complete (100%)
```

---

## Concurrency Model

### Background Task Processing

```python
# FastAPI BackgroundTasks (not Celery for MVP)

@router.post("/analyze/image")
async def analyze_image():
    background_tasks.add_task(process_image_analysis, ...)
    # Returns immediately to client
    # Task processes in background
```

**Why BackgroundTasks?**
- Simple, no external dependencies
- Perfect for MVP/hackathon
- Easy to upgrade to Celery later

**Polling Pattern**
```
Client: GET /api/analysis/{audit_id}/status
Loop every 2s:
  → status = processing, progress = 45%
  → status = processing, progress = 75%
  → status = completed
```

---

## Error Handling Strategy

### Validation Errors (4xx)

```
Invalid file:
  400 Bad Request
  {
    "error": {
      "code": "INVALID_FILE",
      "message": "Invalid image format...",
      "details": "Allowed: PNG, JPG, WEBP"
    }
  }
```

### Analysis Errors (5xx)

```
Gemini API failure:
  500 Internal Error
  Audit marked as "failed"
  Job stores error_message
  User can retry
```

### Graceful Degradation

```
Missing Gemini API key:
  → DEMO_MODE enabled
  → Returns synthetic data
  → Frontend works normally
  → User knows it's demo via UI label
```

---

## Database Relationships

### Audit → Finding → Evidence

```
1 Audit
  ├─ N Findings (cascade delete)
  │   ├─ N Evidence (cascade delete)
  │   └─ status (open, reviewed, resolved)
  │
  └─ 1 AnalysisJob (cascade delete)
      └─ Tracks progress
```

**Why cascade delete?**
- Deleting audit removes all findings/evidence automatically
- Prevents orphaned records
- Maintains referential integrity

---

## Performance Characteristics

### Image Analysis
- Upload: ~1s (depends on network)
- Gemini processing: ~5-15s
- Database: ~100ms
- **Total: 10-30s typical**

### Video Analysis
- Upload: ~5-30s (depends on file size)
- Frame extraction: ~10s
- Gemini processing: ~20-60s
- Database: ~500ms
- **Total: 40-100s typical**

### Scaling Considerations

For MVP:
- Single backend instance sufficient
- BackgroundTasks queues locally
- SQLite handles concurrent reads

For production:
- Multiple workers (Gunicorn)
- Redis for task queue (Celery)
- PostgreSQL for database
- S3 for file storage

---

## Security Architecture

### File Upload Security

```
User File → Validation → Safe Naming → Storage
            ↓
            - File type whitelist
            - Size check
            - MIME type verify
            
            → {uuid}_original.{ext}
            → Never trust original filename
            → Prevent ../../../ traversal
```

### API Security

```
CORS Whitelist:
  ✓ http://localhost:3000
  ✗ http://evil.com

Input Validation:
  - SQLAlchemy ORM (no SQL injection)
  - Pydantic schemas (type validation)
  - File validators (extension check)
```

### Data Security

```
Gemini API Key:
  - Never sent to frontend
  - Stored only in backend .env
  - Not logged or exposed

Database:
  - Foreign keys enabled
  - No sensitive PII stored
  - Timestamps track access
```

---

## Testing Strategy

### Unit Tests

- Model creation and relationships
- Risk score calculations
- File validation
- Coordinate conversions

### Integration Tests

- API endpoint flows
- Database operations
- File upload and storage
- Gemini response parsing (mocked)

### E2E Tests

- Upload → Analysis → Results
- Real Gemini API (optional)
- Frontend integration

---

## Deployment Checklist

- [ ] Python 3.11+ installed
- [ ] `.env` file configured with Gemini key
- [ ] Storage directories created
- [ ] Database initialized
- [ ] CORS origins configured
- [ ] Frontend can reach backend
- [ ] Health checks passing
- [ ] Sample upload succeeds
- [ ] Findings appear correctly
- [ ] Evidence coordinates display
- [ ] Risk scores calculated
- [ ] Reports generate
- [ ] Error handling works

---

## Next Steps for Production

1. **Async Processing** - Add Celery + Redis for scalability
2. **Database** - Migrate to PostgreSQL
3. **Storage** - Use S3 or similar cloud storage
4. **Caching** - Add Redis for frequently accessed data
5. **Monitoring** - Add logging and alerting
6. **Authentication** - Add user auth and audit ownership
7. **Rate Limiting** - Prevent abuse
8. **API Versioning** - Support multiple API versions

