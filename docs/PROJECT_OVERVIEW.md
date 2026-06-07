# Project Overview

## Vision

An AI-powered national security intelligence platform that automatically detects, analyzes, and reports threats in video content — protecting India's digital sovereignty by identifying hostile content before it causes harm.

## Problem Statement

Social media platforms are weaponized for reconnaissance, hate speech, disinformation, and radicalization. Manual moderation cannot scale. Existing automated tools lack:
- Contextual understanding of Indian security threats
- Hindi/Urdu language support
- Intelligence-grade reporting formatted for legal/agency action
- Fiction vs. real-world content discrimination

## Goals

1. **Automate threat detection** in YouTube videos at scale
2. **Support Indian languages** (Hindi/Urdu) with translation
3. **Minimize false positives** through content type classification
4. **Generate actionable intelligence reports** suitable for legal action
5. **Cache results** to avoid redundant processing
6. **Provide a web dashboard** for analysts to review and triage

## Existing Features

| Feature | Status | Location |
|---------|--------|----------|
| YouTube video download | Complete | `backend/src/services/video_indexer.py` |
| Azure Video Indexer integration | Complete | `backend/src/services/video_indexer.py` |
| Speech-to-text with timestamps | Complete | `backend/src/services/video_indexer.py` |
| OCR text extraction | Complete | `backend/src/services/video_indexer.py` |
| Language detection | Complete | `backend/src/graph/nodes.py` |
| Hindi-to-English translation | Complete | `backend/src/graph/nodes.py` |
| Smart content type classification | Complete | `backend/src/graph/nodes.py` |
| RAG query against knowledge base | Complete | `backend/src/graph/nodes.py` |
| Groq Llama-3.3-70B threat analysis | Complete | `backend/src/graph/nodes.py` |
| Category normalization | Complete | `backend/src/graph/nodes.py` |
| Timestamp mapping | Complete | `backend/src/graph/nodes.py` |
| Formatted intelligence report | Complete | `backend/src/graph/nodes.py` |
| Disk-based caching (7-day expiry) | Complete | `backend/src/services/cache_service.py` |
| Cache management API | Complete | `backend/src/api/server.py` |
| CLI execution entry point | Complete | `main.py` |
| Web dashboard UI | Complete | `frontend/index.html` |
| Azure Monitor telemetry | Complete | `backend/src/api/telemetry.py` |
| Document indexing script | Complete | `backend/scripts/index_documents.py` |

## Future Possibilities

| Feature | Priority | Notes |
|---------|----------|-------|
| Multi-platform support (Instagram, Twitter, Facebook) | High | Currently YouTube-only |
| User authentication & RBAC | Critical | No auth on API |
| Rate limiting | High | No abuse protection |
| Unit & integration tests | Critical | Zero tests exist |
| PostgreSQL persistent storage | Medium | Dependency listed but unused |
| Redis caching layer | Medium | Dependency listed but unused |
| CI/CD pipeline | High | No automated deployment |
| Docker containerization | High | No Dockerfile |
| Kubernetes deployment | Medium | For production scaling |
| WebSocket real-time updates | Low | Polling-based now |
| Face/object detection | Medium | Azure VI supports it |
| Audio sentiment analysis | Low | Transcript-only currently |
| API key authentication | Critical | Currently open access |
| Audit logging | High | No request audit trail |
| Load balancing & auto-scaling | Medium | For production |
