# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

**Currently: NONE** — The API has no authentication. All endpoints are publicly accessible.

## Endpoints

### 1. Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "Active",
  "service": "National Security Guardian AI",
  "version": "3.0.0",
  "cache_entries": 5
}
```

---

### 2. Serve Frontend UI

```
GET /
```

**Response:** `frontend/index.html` (served as `FileResponse`)

---

### 3. Scan Video

```
POST /scan
Content-Type: application/json
```

**Request Body:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=...",
  "force_rescan": false
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `video_url` | string | Yes | — | YouTube video URL |
| `force_rescan` | bool | No | `false` | Bypass cache and force re-scan |

**Response (200):**
```json
{
  "session_id": "a3f7c2b1-...",
  "video_id": "vid_a3f7c2b1",
  "status": "FLAGGED_FOR_TAKEDOWN",
  "final_report": "CLASSIFICATION: RESTRICTED...",
  "security_flags": [
    {
      "category": "HATE_SPEECH",
      "severity": "CRITICAL",
      "description": "...",
      "timestamp": "01:24",
      "confidence": 0.94
    }
  ],
  "from_cache": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique scan session ID (UUID v4) |
| `video_id` | string | Short video identifier |
| `status` | string | `SAFE` or `FLAGGED_FOR_TAKEDOWN` |
| `final_report` | string | Formatted intelligence report (multi-line) |
| `security_flags[]` | array | List of detected security threats |
| `from_cache` | bool | Whether result was served from cache |

**Response (500):**
```json
{
  "detail": "National Security Workflow Execution Failed: ..."
}
```

---

### 4. Invalidate Single Cache Entry

```
DELETE /scan/cache?video_url=https://youtube.com/watch?v=...
```

**Query Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `video_url` | string | Yes | YouTube URL to remove from cache |

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared for this URL."
}
```

---

### 5. List All Cache Entries

```
GET /cache
```

**Response:**
```json
{
  "total": 5,
  "entries": [
    {
      "key": "369a992dfa07ddc5",
      "video_url": "https://youtube.com/shorts/xkJ7Ma5KzJg?si=...",
      "status": "FLAGGED_FOR_TAKEDOWN",
      "cached_at": "2026-03-21T15:00:20.011923",
      "age_hours": 72
    }
  ]
}
```

---

### 6. Wipe All Cache

```
DELETE /cache
```

**Response:**
```json
{
  "deleted": 5,
  "message": "Cleared 5 cached entries successfully."
}
```

## Request Models (Pydantic)

```python
class AuditRequest(BaseModel):
    video_url: str
    force_rescan: bool = False

class SecurityAlertModel(BaseModel):
    category: str
    severity: str
    description: str
    timestamp: Optional[str] = None
    confidence: Optional[float] = None

class AuditResponse(BaseModel):
    session_id: str
    video_id: str
    status: str
    final_report: str
    security_flags: List[SecurityAlertModel]
    from_cache: bool = False
```

## Error Handling

Errors during workflow execution return HTTP 500 with a descriptive detail message. Cache corruption is handled silently (corrupt files are deleted).

## Rate Limiting

**None implemented.** The API has no rate limiting or abuse protection.

## CORS

Currently allows all origins (`*`) with all methods and headers — should be restricted in production.
