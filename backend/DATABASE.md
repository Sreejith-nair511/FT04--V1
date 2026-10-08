# CogniShield Database Guide

## Overview

CogniShield uses **SQLite** for local data storage. No external database server needed.

### Why SQLite?

✓ **Zero configuration** - No installation or setup  
✓ **File-based** - Backed up with simple file copy  
✓ **Self-contained** - Entire app in one folder  
✓ **Perfect for MVP** - Easy to migrate to PostgreSQL later  
✓ **Python native** - Built-in support  

---

## Database Location

```
backend/data/cognishield.db
```

This file is created automatically on first startup.

### Backup

Simply copy the database file:
```bash
# Backup
cp backend/data/cognishield.db backend/data/cognishield.db.backup

# Restore
cp backend/data/cognishield.db.backup backend/data/cognishield.db
```

---

## Database Schema

### Tables Overview

```
audits (1)
├── findings (N)
│   └── evidence (N)
└── analysis_jobs (1)
```

### Detailed Schema

#### AUDITS Table

Represents an audit of a fintech application.

```sql
CREATE TABLE audits (
  id VARCHAR(36) PRIMARY KEY,           -- UUID
  application_name VARCHAR(255) NOT NULL,
  platform VARCHAR(50),                  -- iOS, Android, Web
  input_type VARCHAR(50),                -- image, video
  original_filename VARCHAR(255),
  file_path VARCHAR(500),                -- Path to uploaded file
  
  status VARCHAR(50),                    -- queued, processing, completed, failed
  risk_score FLOAT,                      -- 0-100
  risk_level VARCHAR(20),                -- LOW, MEDIUM, HIGH, CRITICAL
  summary VARCHAR(1000),                 -- Analysis summary
  
  model_name VARCHAR(100),               -- gemini-2.0-flash-exp
  model_version VARCHAR(50),
  
  created_at DATETIME,
  updated_at DATETIME,
  completed_at DATETIME
);

-- Indexes
CREATE INDEX idx_audits_status ON audits(status);
CREATE INDEX idx_audits_created ON audits(created_at DESC);
CREATE INDEX idx_audits_application ON audits(application_name);
```

**Fields Explanation:**

- **id**: Unique identifier (UUID v4)
- **application_name**: "FinFlow", "PayPal", etc.
- **platform**: Where the app runs
- **input_type**: "image" for screenshot, "video" for recording
- **file_path**: Where file is stored on disk
- **status**: Processing state
  - `queued` - Waiting to be analyzed
  - `processing` - Currently being analyzed
  - `completed` - Done (may be success or failure)
  - `failed` - Analysis error
- **risk_score**: Calculated score 0-100
- **risk_level**: Derived from risk_score
- **model_name**: Which AI model analyzed it

---

#### FINDINGS Table

Detected dark patterns within an audit.

```sql
CREATE TABLE findings (
  id VARCHAR(36) PRIMARY KEY,
  audit_id VARCHAR(36) NOT NULL,        -- Foreign key to audits
  
  finding_number INT,                    -- 1, 2, 3... (sequential in audit)
  category VARCHAR(100),                 -- subscription_trap, forced_action, etc.
  title VARCHAR(255),                    -- "Subscription Trap"
  
  severity VARCHAR(20),                  -- low, medium, high, critical
  confidence FLOAT,                      -- 0-100 (AI confidence %)
  
  evidence_text TEXT,                    -- Exact UI text found
  why_problematic TEXT,                  -- Why it's deceptive
  user_impact TEXT,                      -- How users are affected
  recommended_fix TEXT,                  -- How to remedy
  
  status VARCHAR(50),                    -- open, reviewed, resolved
  created_at DATETIME,
  
  FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_findings_audit ON findings(audit_id);
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_findings_category ON findings(category);
```

**Fields Explanation:**

- **category**: Dark pattern type (from taxonomy)
- **severity**: How bad is it?
  - `low` = informational, minor UX issue
  - `medium` = concerning, impacts some users
  - `high` = serious, affects user autonomy
  - `critical` = severe, legal/compliance risk
- **confidence**: How certain is the AI? (0-100%)
  - 95% = Almost certain
  - 80% = Very likely
  - 60% = Probably
  - <50% = Uncertain
- **status**: Tracking remediation
  - `open` = Not yet addressed
  - `reviewed` = Team discussed
  - `resolved` = Fixed in code

---

#### EVIDENCE Table

Visual or textual proof of a dark pattern.

```sql
CREATE TABLE evidence (
  id VARCHAR(36) PRIMARY KEY,
  finding_id VARCHAR(36),                -- Foreign key to findings (nullable)
  audit_id VARCHAR(36) NOT NULL,         -- Foreign key to audits
  
  evidence_type VARCHAR(50),             -- box, text, interactive
  frame_number INT,                      -- For video: which frame?
  timestamp_seconds FLOAT,               -- For video: at what time?
  
  -- Bounding box (normalized 0.0 - 1.0)
  x FLOAT,                               -- Left position
  y FLOAT,                               -- Top position
  width FLOAT,                           -- Box width
  height FLOAT,                          -- Box height
  
  image_path VARCHAR(500),               -- Path to evidence image
  text TEXT,                             -- Optional text content
  
  created_at DATETIME,
  
  FOREIGN KEY (finding_id) REFERENCES findings(id) ON DELETE CASCADE,
  FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_evidence_finding ON evidence(finding_id);
CREATE INDEX idx_evidence_audit ON evidence(audit_id);
```

**Fields Explanation:**

- **evidence_type**:
  - `box` = Bounding box around UI element
  - `text` = Direct textual evidence
  - `interactive` = User interaction event
- **Coordinates** (0.0 - 1.0 normalized):
  ```
  x: 0.0 = left edge,  1.0 = right edge
  y: 0.0 = top,        1.0 = bottom
  width: element width as % of screen
  height: element height as % of screen
  ```
- **timestamp_seconds**: For videos, when does this occur?
- **frame_number**: Which frame extracted from video?

**Example Coordinates:**
```
UI element at:
  Left:   18% of screen   → x = 0.18
  Top:    57% of screen   → y = 0.57
  Width:  64% of screen   → width = 0.64
  Height: 14% of screen   → height = 0.14

Stored in database: { x: 0.18, y: 0.57, width: 0.64, height: 0.14 }
Frontend CSS:       { left: "18%", top: "57%", width: "64%", height: "14%" }
```

---

#### ANALYSIS_JOBS Table

Tracks progress of ongoing analyses.

```sql
CREATE TABLE analysis_jobs (
  id VARCHAR(36) PRIMARY KEY,
  audit_id VARCHAR(36) NOT NULL UNIQUE,  -- Foreign key to audits
  
  status VARCHAR(50),                    -- queued, processing, completed, failed
  progress INT,                          -- 0-100
  current_stage VARCHAR(255),            -- "Detecting dark patterns"
  
  error_message TEXT,                    -- If failed, why?
  
  started_at DATETIME,
  completed_at DATETIME,
  created_at DATETIME,
  updated_at DATETIME,
  
  FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);

-- Index
CREATE INDEX idx_jobs_audit ON analysis_jobs(audit_id);
```

**Fields Explanation:**

- **progress**: 0-100, what % done?
- **current_stage**: Where are we in the pipeline?
  - "Uploading evidence"
  - "Extracting interface structure"
  - "Analyzing visual hierarchy"
  - "Detecting dark patterns"
  - "Calculating risk score"
  - "Analysis complete"
- **error_message**: If something went wrong, what was it?

---

## Common Queries

### Get an audit with all findings

```sql
SELECT 
  a.*,
  COUNT(f.id) as finding_count,
  AVG(f.confidence) as avg_confidence
FROM audits a
LEFT JOIN findings f ON a.id = f.audit_id
WHERE a.id = '550e8400-e29b-41d4-a716-446655440000'
GROUP BY a.id;
```

### Find all high-severity findings

```sql
SELECT f.*, a.application_name
FROM findings f
JOIN audits a ON f.audit_id = a.id
WHERE f.severity = 'high'
ORDER BY f.confidence DESC;
```

### Get evidence for a finding

```sql
SELECT * FROM evidence
WHERE finding_id = 'f123...'
ORDER BY created_at;
```

### Track analysis progress

```sql
SELECT aj.*, a.application_name, a.status
FROM analysis_jobs aj
JOIN audits a ON aj.audit_id = a.id
WHERE aj.status = 'processing'
ORDER BY aj.updated_at DESC;
```

### Audit statistics

```sql
SELECT
  COUNT(*) as total_audits,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
  AVG(risk_score) as avg_risk,
  MAX(risk_score) as max_risk,
  COUNT(DISTINCT application_name) as unique_apps
FROM audits
WHERE created_at > datetime('now', '-7 days');
```

### Findings by category

```sql
SELECT
  category,
  COUNT(*) as count,
  AVG(confidence) as avg_confidence,
  AVG(CASE WHEN severity = 'high' THEN 1 WHEN severity = 'critical' THEN 1 ELSE 0 END) as high_severity_pct
FROM findings
GROUP BY category
ORDER BY count DESC;
```

---

## Database Operations

### Inspect Database

#### Using Python

```python
import sqlite3

conn = sqlite3.connect('backend/data/cognishield.db')
cursor = conn.cursor()

# Get all audits
cursor.execute('SELECT * FROM audits LIMIT 5')
for row in cursor.fetchall():
    print(row)

conn.close()
```

#### Using SQLite CLI

```bash
# Open database
sqlite3 backend/data/cognishield.db

# List tables
.tables

# Show schema
.schema audits

# Query
SELECT * FROM audits LIMIT 5;

# Exit
.quit
```

#### Using GUI (SQLite Browser)

1. Download: https://sqlitebrowser.org/
2. Open file: `backend/data/cognishield.db`
3. Browse tables visually

---

### Reset Database

```bash
# Delete the database file
# Windows:
del backend\data\cognishield.db

# macOS/Linux:
rm backend/data/cognishield.db

# Restart backend - it will recreate empty database
uvicorn app.main:app --reload
```

### Export Data

```bash
# Export to CSV
sqlite3 backend/data/cognishield.db ".mode csv" ".output export.csv" "SELECT * FROM findings;"

# Export to JSON (need to convert)
sqlite3 backend/data/cognishield.db ".mode json" "SELECT * FROM audits;" > audits.json
```

---

## Relationships

### Cascade Delete

Deleting an audit automatically deletes:
- All findings
- All evidence
- Analysis job

```python
# This works because of CASCADE
db.delete(audit)
db.commit()
# All related data gone too
```

### Foreign Keys

SQLite has foreign keys enabled:

```python
# This will fail - referencing non-existent audit
finding = Finding(audit_id='invalid_id', ...)
db.add(finding)
db.commit()  # ← Error: FOREIGN KEY constraint failed
```

### Relationships in Code

```python
# Access findings from audit
audit = db.query(Audit).first()
for finding in audit.findings:
    print(finding.title)

# Access audit from finding
finding = db.query(Finding).first()
print(finding.audit.application_name)

# Access evidence from finding
for evidence in finding.evidence_items:
    print(evidence.x, evidence.y)
```

---

## Performance Considerations

### Indexes

Current indexes:
- `audits.status` - Fast filtering
- `audits.created_at DESC` - Fast sorting
- `findings.audit_id` - Fast joins
- `findings.severity` - Fast filtering

For MVP, this is sufficient.

### Typical Queries

| Query | Time | Notes |
|-------|------|-------|
| Get 1 audit | <10ms | Direct ID lookup |
| List 100 audits | 20-50ms | Sorted by date |
| Get findings for audit | 5-20ms | Includes evidence |
| Filter findings | 30-100ms | Depends on WHERE |

### SQLite Limits

For MVP:
- 1000 audits: no problem
- 10,000 findings: still fine
- 1GB database: SQLite handles easily

For enterprise:
- Migrate to PostgreSQL
- Add caching layer
- Partition old data

---

## Transactions

All database operations use transactions:

```python
# Atomic: either all succeed or all fail
try:
    audit = Audit(...)
    db.add(audit)
    db.flush()  # Get ID
    
    finding = Finding(audit_id=audit.id, ...)
    db.add(finding)
    
    db.commit()  # Both or neither
except Exception:
    db.rollback()  # Undo everything
```

---

## Backups

### Automatic Backups

None currently. For production:
```bash
# Schedule daily backup
0 0 * * * cp /path/to/cognishield.db /backups/cognishield-$(date +%Y%m%d).db
```

### Manual Backup

```bash
# Copy database file
cp backend/data/cognishield.db backend/data/cognishield.db.$(date +%s).backup
```

### Recovery

```bash
# Replace corrupted database
cp backend/data/cognishield.db.backup backend/data/cognishield.db
# Restart backend
```

---

## Migrations (Alembic)

Not needed for MVP, but for reference:

```bash
# Initialize migrations (one-time)
alembic init alembic

# Create migration after model change
alembic revision --autogenerate -m "Add new_field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Troubleshooting

### "Database is locked"

**Problem:** Multiple processes accessing database

**Solution:**
```bash
# Ensure only one backend running
# Restart backend
# Or use: PRAGMA journal_mode=WAL;
```

### "Foreign key constraint failed"

**Problem:** Referencing invalid ID

**Solution:** Check ID exists before referencing
```python
# Before:
finding = Finding(audit_id='invalid')

# After:
audit = db.query(Audit).filter(Audit.id == audit_id).first()
if audit:
    finding = Finding(audit_id=audit.id, ...)
```

### "Disk I/O error"

**Problem:** File system issue

**Solution:**
- Check disk space: `df -h`
- Check permissions: `ls -la backend/data/`
- Restore from backup

### Database file huge

**Problem:** Old data taking space

**Solution:**
```bash
# Delete old audits
DELETE FROM audits WHERE created_at < datetime('now', '-30 days');

# Vacuum to reclaim space
sqlite3 backend/data/cognishield.db "VACUUM;"
```

---

## Data Privacy

### Sensitive Data

Currently stored:
- Application names (not sensitive)
- UI screenshots (consider sensitive)
- Analysis results (not sensitive)

### Recommendations

For production:
- Encrypt at rest
- Encrypt in transit (HTTPS)
- Access control
- Data retention policies
- Regular backups
- Audit logging

---

## Future Improvements

1. **Encryption** - Encrypt uploaded files
2. **Archival** - Move old audits to compressed archive
3. **Analytics** - Dashboards on SQLite data
4. **PostgreSQL** - For multi-user deployments
5. **Replication** - Database backups to cloud

---

## Summary

- **SQLite file**: `backend/data/cognishield.db`
- **No setup needed**: Created automatically
- **4 tables**: audits, findings, evidence, analysis_jobs
- **Cascade delete**: Deleting audit cleans up everything
- **Coordinates**: Normalized 0.0-1.0 for resolution independence
- **Backups**: Manual copy of database file
- **Perfect for**: MVP, hackathon, single-user deployment

Ready to store audits! 🗄️

