# Database Design

## Current State

This project does **not** use a traditional relational database. The current data storage architecture consists of:

### 1. Disk Cache (JSON files)

**Location:** `backend/cache/`

**Structure:**
```json
{
  "video_url": "https://youtube.com/watch?v=...",
  "cached_at": "2026-03-21T15:00:20.011923",
  "expires_in": "7 days",
  "result": {
    "video_id": "vid_02eb979e",
    "final_status": "FLAGGED_FOR_TAKEDOWN",
    "final_report": "CLASSIFICATION: RESTRICTED...",
    "security_flags": [
      {
        "category": "HATE_SPEECH",
        "severity": "CRITICAL",
        "description": "...",
        "confidence": 0.98,
        "timestamp": "0:00:09.59"
      }
    ]
  }
}
```

**Key:** SHA-256 hash of YouTube video ID (16-character hex string)

**Cache Metadata (per entry):**
| Field | Type | Description |
|-------|------|-------------|
| `video_url` | string | Original YouTube URL |
| `cached_at` | ISO datetime | When the result was cached |
| `expires_in` | string | TTL duration |
| `result.video_id` | string | Generated video session ID |
| `result.final_status` | string | `SAFE` or `FLAGGED_FOR_TAKEDOWN` |
| `result.final_report` | string | Formatted intelligence report |
| `result.security_flags[]` | array | List of detected threats |

**Security Alert Schema:**
| Field | Type | Values |
|-------|------|--------|
| `category` | string | TERRORISM, BORDER_SECURITY, CYBER_THREAT, FAKE_NEWS, HATE_SPEECH, ESPIONAGE, GENERAL |
| `severity` | string | CRITICAL, HIGH, WARNING |
| `description` | string | Human-readable threat description |
| `confidence` | float | 0.0–1.0 |
| `timestamp` | string | Video timestamp (HH:MM:SS.mmm) |

### 2. Azure AI Search (Vector Database)

**Service:** Azure AI Search (index name: `national-security-rules`)

**Data Origin:** `backend/data/Official_National_Security_Protocols_2026.pdf`

**Chunking Strategy:**
- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Embedding model: `all-MiniLM-L6-v2` (384-dimensional vectors)
- Source metadata: filename tagged per chunk

### 3. Unused Dependencies (available but not implemented)

| Technology | Listed In | Status |
|-----------|-----------|--------|
| PostgreSQL (`psycopg2-binary`) | `pyproject.toml` | **Not used** |
| Redis (`redis`) | `pyproject.toml` | **Not used** |
| SQLAlchemy (`sqlalchemy`) | `pyproject.toml` | **Not used** |
| Pandas (`pandas`) | `pyproject.toml` | **Not used** |

## Recommended Production Database Schema

If migrating to PostgreSQL:

```sql
-- Videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_url TEXT NOT NULL UNIQUE,
    platform VARCHAR(50) DEFAULT 'youtube',
    video_id VARCHAR(100),
    local_file_path TEXT,
    duration_seconds INTEGER,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security alerts table
CREATE TABLE security_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id),
    category VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    confidence DECIMAL(4,3),
    video_timestamp VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scan sessions table
CREATE TABLE scan_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id),
    status VARCHAR(50) DEFAULT 'COMPLETED',
    from_cache BOOLEAN DEFAULT FALSE,
    report_text TEXT,
    total_flags INTEGER DEFAULT 0,
    avg_confidence DECIMAL(4,3),
    risk_level VARCHAR(20),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Users table (for future auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'analyst',
    password_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```
