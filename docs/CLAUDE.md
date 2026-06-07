# CLAUDE.md — AI Memory File for National Security Shield

## Project Summary

**National Security Shield** is an AI-powered YouTube video threat detection system for Indian national security. It downloads videos, extracts transcripts/OCR via Azure Video Indexer, translates Hindi to English, queries a national security knowledge base (RAG), and uses Groq's Llama-3.3-70B to analyze content for threats: terrorism, border security, cyber, fake news, hate speech, espionage. Results are cached for 7 days.

**Version:** 0.1.0 | **Python:** 3.13 | **Status:** MVP Prototype (~45% production-ready)

## Architecture Overview

```
CLI (main.py) ─┐
               ├── FastAPI (server.py) ── LangGraph Workflow ── Indexer Node ── Azure Video Indexer
Web Dashboard   │                                               └── Auditor Node ── Groq LLM
(index.html)    │                                                               └─ Azure AI Search (RAG)
                └── Cache Service (disk, SHA-256 key, 7-day expiry)
```

- **2-node LangGraph DAG:** `indexer` → `auditor` → END
- **State:** `VideoSecurityState` (TypedDict with video_url, transcript, ocr_text, security_flags, final_status, final_report, errors)

## Folder Structure

| Path | Purpose |
|------|---------|
| `main.py` | CLI entry point (argparse) |
| `backend/src/api/server.py` | FastAPI server (6 endpoints) |
| `backend/src/api/telemetry.py` | Azure Monitor setup |
| `backend/src/graph/state.py` | LangGraph state schema |
| `backend/src/graph/nodes.py` | Pipeline nodes (485 lines — core logic) |
| `backend/src/graph/workflow.py` | DAG definition |
| `backend/src/services/cache_service.py` | Disk cache with expiry |
| `backend/src/services/video_indexer.py` | Azure VI + yt-dlp |
| `backend/scripts/index_documents.py` | PDF ingestion to Azure AI Search |
| `backend/cache/` | JSON cache files |
| `backend/data/` | PDF knowledge base |
| `frontend/index.html` | Dark-themed dashboard (1015 lines) |
| `.env` | **Contains live secrets — ROTATE BEFORE COMMIT** |

## Key Features

1. YouTube video download (yt-dlp)
2. Azure Video Indexer (STT, OCR, timestamps)
3. Language detection (langdetect) + Hindi→English translation (Helsinki-NLP)
4. Smart fiction/content type classification (6 types)
5. RAG query against national security protocols
6. Groq Llama-3.3-70B threat analysis
7. Intelligence report generation (formatted for legal/agency action)
8. Disk-based caching (7-day configurable expiry)
9. Dark-themed web dashboard with Chart.js analytics
10. Cache management API

## Important Workflows

### Scan Pipeline
1. User submits YouTube URL via CLI or web dashboard
2. Cache check — instant return if same URL scanned within 7 days
3. Indexer: yt-dlp download → Azure VI upload → wait for processing → extract transcript+OCR
4. Auditor: Detect language → translate Hindi→English → classify content type → RAG query → LLM threat analysis → normalize categories → map timestamps → build report
5. Cache result → return to user

### Content Classification
If fiction detected (news, movie, music, game, comedy, documentary), immediately returns SAFE without LLM analysis — reduces false positives.

### Threat Categories
TERRORISM, BORDER_SECURITY, CYBER_THREAT, FAKE_NEWS, HATE_SPEECH, ESPIONAGE, GENERAL

### Severity Levels
CRITICAL → IT Act 69A takedown + NIA referral
HIGH → CERT-In escalation within 24h
WARNING → Routine monitoring

## APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve frontend UI |
| POST | `/scan` | Scan YouTube video for threats |
| DELETE | `/scan/cache?video_url=...` | Invalidate single cache entry |
| GET | `/cache` | List all cached results |
| DELETE | `/cache` | Wipe entire cache |
| GET | `/health` | Health check + cache entry count |

**Request body (POST /scan):** `{"video_url": "...", "force_rescan": false}`

## Database

- **No SQL database.** Currently disk-based JSON cache only.
- **Azure AI Search** serves as vector database for RAG.
- PostgreSQL, Redis, SQLAlchemy are listed in pyproject.toml but **not implemented**.
- Recommended production schema in `docs/DATABASE_DESIGN.md`.

## Security Model

**Current state: NO SECURITY.** Critical issues:
- Live API keys in `.env` file — **must rotate immediately**
- No authentication on any endpoint
- CORS allows all origins (`*`)
- No rate limiting
- No HTTPS
- No audit logging

See `docs/SECURITY_ANALYSIS.md` for full assessment and remediation plan.

## Known Issues

1. **Zero tests** — no pytest or other test infrastructure
2. **Hardcoded temp file** — `temp_security_video.mp4` race condition
3. **Global translator variable** — not thread-safe
4. **Synchronous blocking** — video download blocks the event loop
5. **YouTube-only** — no Instagram/Twitter/Facebook support
6. **No retry logic** — Azure VI failures abort the pipeline
7. **Keyword-based category normalization** — easily bypassed
8. **Unused dependencies** — streamlit, firecrawl-py, pandas, psycopg2-binary, redis, sqlalchemy
9. **Static demo data in frontend** — analytics numbers are hardcoded
10. **No background task queue** — long scans block HTTP responses

## Pending Tasks

1. Rotate all exposed secrets
2. Implement authentication (JWT)
3. Add rate limiting
4. Restrict CORS
5. Write unit/integration tests
6. Create Dockerfile
7. Set up CI/CD pipeline
8. Implement persistent database
9. Add multi-platform video support
10. Replace static frontend data with dynamic API calls

## Commands

```bash
# Start server
uvicorn backend.src.api.server:app --reload --port 8000

# Index documents
uv run python backend/scripts/index_documents.py

# Run CLI scan
uv run python main.py -u <youtube_url>

# Install dependencies
uv sync
```
