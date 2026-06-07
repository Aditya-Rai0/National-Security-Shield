# Folder Structure

```
national-security-shield/
│
├── .env                              # Environment variables & secrets (API keys, connection strings)
├── .gitignore                        # Git ignore rules
├── .python-version                   # Python version: 3.13
├── main.py                           # CLI entry point for security audits
├── pyproject.toml                    # Project metadata + dependencies (38 packages)
├── README.md                         # Usage notes (HTML comments)
├── uv.lock                           # uv package manager lock file (527 KB)
├── temp_security_video.mp4           # Temporary downloaded video file (4 MB)
│
├── backend/
│   ├── cache/                        # Disk-based scan result cache
│   │   ├── 077dfb704f792983.json     # Cached scan result (no transcript)
│   │   ├── 369a992dfa07ddc5.json     # Cached scan: HATE_SPEECH CRITICAL
│   │   ├── 5698da2d1c0730db.json     # Cached scan result (no transcript)
│   │   ├── 5ffce1cdd659747a.json     # Cached scan result (no transcript)
│   │   └── 838709f7d0abffbf.json     # Cached scan: HATE_SPEECH CRITICAL
│   │
│   ├── data/                         # Knowledge base documents (PDFs)
│   │   └── Official_National_Security_Protocols_2026.pdf  # Indexed into Azure AI Search
│   │
│   ├── scripts/                      # Utility scripts
│   │   └── index_documents.py        # PDF → Azure AI Search indexing script
│   │
│   └── src/                          # Application source code
│       ├── api/                      # REST API layer
│       │   ├── server.py             # FastAPI server (6 endpoints)
│       │   └── telemetry.py          # Azure Monitor OpenTelemetry setup
│       │
│       ├── graph/                    # LangGraph workflow orchestration
│       │   ├── __init__.py           # Empty
│       │   ├── state.py              # VideoSecurityState TypedDict
│       │   ├── nodes.py              # Workflow nodes (indexer + auditor)
│       │   └── workflow.py           # StateGraph DAG definition
│       │
│       └── services/                 # Business logic services
│           ├── __init__.py           # Empty
│           ├── cache_service.py      # Disk-based cache (SHA-256 keyed)
│           └── video_indexer.py      # Azure Video Indexer + yt-dlp
│
├── frontend/                         # Web dashboard
│   └── index.html                    # Single-page UI (HTML/CSS/JS, 1015 lines)
│
└── docs/                             # Documentation (newly created)
    ├── PROJECT_CONTEXT.md
    ├── PROJECT_OVERVIEW.md
    ├── SYSTEM_ARCHITECTURE.md
    ├── FOLDER_STRUCTURE.md
    ├── DATABASE_DESIGN.md
    ├── API_DOCUMENTATION.md
    ├── USER_FLOW.md
    ├── SECURITY_ANALYSIS.md
    ├── DEPLOYMENT_GUIDE.md
    ├── IMPROVEMENT_SUGGESTIONS.md
    ├── CLAUDE.md
    └── REPOSITORY_ANALYSIS_REPORT.md
```

## Key Source Files

| File | Lines | Purpose |
|------|-------|---------|
| `backend/src/graph/nodes.py` | 485 | Core business logic — threat analysis pipeline |
| `frontend/index.html` | 1015 | Web dashboard with Chart.js analytics |
| `backend/src/api/server.py` | 181 | FastAPI REST endpoints |
| `backend/src/services/cache_service.py` | 207 | Disk cache with expiry management |
| `backend/src/services/video_indexer.py` | 143 | Azure Video Indexer integration |
| `backend/src/graph/workflow.py` | 56 | LangGraph DAG definition |
| `backend/src/graph/state.py` | 37 | State schema (TypedDict) |
| `backend/src/api/telemetry.py` | 48 | Azure Monitor configuration |
| `backend/scripts/index_documents.py` | 129 | PDF document ingestion script |
| `main.py` | 124 | CLI entry point |
