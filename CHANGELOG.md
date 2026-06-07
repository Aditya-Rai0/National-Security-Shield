# Changelog

All notable changes to the National Security Shield project will be documented in this file.

## [0.1.0] — 2026-06-07

### Added
- Initial MVP release
- YouTube video download via yt-dlp
- Azure Video Indexer integration for speech-to-text and OCR
- Language detection and Hindi→English translation (Helsinki-NLP)
- Smart content type classification (news, movies, music, games, comedy, documentary)
- RAG-based knowledge base query against Azure AI Search
- Groq Llama-3.3-70B threat analysis for 6 categories
- Intelligence report generation with formatted output
- Disk-based caching with 7-day configurable expiry
- Cache management API (list, invalidate, clear)
- FastAPI REST API with 6 endpoints
- Dark-themed web dashboard with Chart.js analytics
- CLI execution via `main.py`
- Azure Monitor OpenTelemetry integration
- PDF document indexing script for knowledge base population
- Comprehensive documentation (12 files, 1,272 lines)
- Project showcase page (PROJECT_SHOWCASE.md)
- MIT License
- Contribution guidelines (CONTRIBUTING.md)

### Security
- `.env` added to `.gitignore` to prevent credential leaks
- All credentials read from environment variables at runtime
- No hardcoded secrets in source code

### Known Issues
- No authentication on API endpoints
- CORS allows all origins (`*`)
- Zero test coverage
- No rate limiting
- YouTube-only platform support
- No persistent database (disk-based cache only)
- Synchronous video download blocks event loop
- Global translator variable not thread-safe
- Keyword-based category normalization (bypassable)
