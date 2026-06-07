# Improvement Suggestions

## Critical (Security)

| # | Issue | File | Severity | Suggested Fix |
|---|-------|------|----------|---------------|
| 1 | **Live API keys in .env** | `.env` | CRITICAL | Rotate all keys immediately; use Azure Key Vault or GitHub Secrets |
| 2 | **No authentication** | `backend/src/api/server.py` | CRITICAL | Add JWT authentication with role-based access control (analyst, admin, agency) |
| 3 | **CORS allows all origins** | `backend/src/api/server.py:44` | HIGH | Restrict to specific domains in production |
| 4 | **No rate limiting** | — | HIGH | Add `slowapi` or custom rate limiting middleware |
| 5 | **No HTTPS** | — | HIGH | Configure TLS; use reverse proxy (nginx, Azure Front Door) |
| 6 | **Plaintext secrets in code** | `backend/src/graph/nodes.py:344-347` | MEDIUM | Read API key from env only, never hardcode |

## Architecture

| # | Issue | File | Impact | Suggested Fix |
|---|-------|------|--------|---------------|
| 7 | **Hardcoded video filename** | `backend/src/graph/nodes.py:235` | Race condition on concurrent scans | Use `tempfile.NamedTemporaryFile` with UUID |
| 8 | **No database persistence** | — | No historical data | Implement PostgreSQL with SQLAlchemy (dependencies already listed) |
| 9 | **Redis dependency unused** | `pyproject.toml` | Bloat | Remove or implement Redis for distributed cache |
| 10 | **Streamlit dependency unused** | `pyproject.toml` | Bloat | Remove (increases attack surface) |
| 11 | **firecrawl-py dependency unused** | `pyproject.toml` | Bloat | Remove |
| 12 | **Pandas dependency unused** | `pyproject.toml` | Bloat | Remove |
| 13 | **No async video processing** | `backend/src/graph/nodes.py` | Poor UX for long videos | Implement background task queue (Celery + Redis) |
| 14 | **No WebSocket updates** | `frontend/index.html` | Polling-based progress | Add WebSocket for real-time progress updates |

## Code Quality

| # | Issue | File | Impact | Suggested Fix |
|---|-------|------|--------|---------------|
| 15 | **Zero tests** | — | Untrusted production readiness | Add pytest tests: unit, integration, e2e |
| 16 | **No type hints in some functions** | Various | Maintainability | Add full type annotations |
| 17 | **Magic strings for categories** | `backend/src/graph/nodes.py:24-38` | Brittle | Use Enum for threat categories |
| 18 | **Exception handling swallows errors** | `backend/src/graph/nodes.py:257-264` | Silent failures | Better error propagation and alerting |
| 19 | **Global translator variable** | `backend/src/graph/nodes.py:21` | Thread safety | Use local initialization with caching |
| 20 | **No configuration management** | — | Hardcoded paths | Use pydantic-settings for config |
| 21 | **Duplicate code in report display** | `main.py:66-75` and `main.py:102-111` | Maintainability | Extract to shared function |

## Features

| # | Issue | Current Limitation | Suggested Enhancement |
|---|-------|-------------------|----------------------|
| 22 | **YouTube-only support** | Only YouTube URLs accepted | Add Instagram Reels, Twitter/X, Facebook video support |
| 23 | **No retry mechanism** | Azure VI failures cause full pipeline failure | Add retry with exponential backoff |
| 24 | **No processing timeout** | Long videos may hang indefinitely | Configurable timeout per pipeline step |
| 25 | **No batch scanning** | One video at a time | Add batch queue processing |
| 26 | **No export functionality** | Results only visible in UI/CLI | Add PDF/CSV export of reports |
| 27 | **No user management** | No multi-user support | Add user registration, roles, permissions |
| 28 | **Hardcoded demo data in frontend** | `frontend/index.html:937-983` | Replace with real API data |
| 29 | **Static analytics numbers** | `frontend/index.html:986-1012` | Dynamic analytics from database |
| 30 | **No notification system** | Analysts must manually check | Add email/Slack alerts for critical flags |

## Performance

| # | Issue | Impact | Suggested Fix |
|---|-------|--------|---------------|
| 31 | **Synchronous video download** | Blocks API thread during download | Use async HTTP client with background tasks |
| 32 | **LLM on critical path** | Pipeline waits for LLM response | Consider streaming LLM responses |
| 33 | **No connection pooling** | New Azure token per request | Reuse tokens with refresh logic |
| 34 | **Polling-based Azure VI** | 30s fixed interval | Use webhook callback when available |
| 35 | **Large file cleanup** | `temp_security_video.mp4` persists on failure | Ensure cleanup in `finally` block |

## Documentation

| # | Issue | Suggested Fix |
|---|-------|---------------|
| 36 | **No API docs generated** | Add FastAPI auto-docs (already available at `/docs`) |
| 37 | **No architecture diagrams** | Now provided in `docs/` |
| 38 | **No contribution guide** | Add CONTRIBUTING.md |
| 39 | **No changelog** | Add CHANGELOG.md |
| 40 | **No license** | Add LICENSE file |

## DevOps

| # | Issue | Suggested Fix |
|---|-------|---------------|
| 41 | **No Dockerfile** | Containerize for consistent deployment |
| 42 | **No CI/CD** | Add GitHub Actions for test + lint + deploy |
| 43 | **No terraform/ARM templates** | Infrastructure as Code for Azure resources |
| 44 | **No monitoring dashboard** | Azure Dashboard for pipeline metrics |
| 45 | **No log aggregation** | Centralized logging (Azure Log Analytics) |
