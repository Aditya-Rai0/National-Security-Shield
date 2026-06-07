# System Architecture

## High-Level Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        CLI["CLI (main.py)"]
        UI["Web Dashboard (frontend/index.html)"]
    end

    subgraph "API Layer (FastAPI)"
        API["server.py"]
        CACHE["Cache Service"]
        TELE["Azure Monitor Telemetry"]
    end

    subgraph "LangGraph Workflow"
        WF["Workflow Orchestrator"]
        INDEXER["Indexer Node"]
        AUDITOR["Auditor Node"]
    end

    subgraph "Azure Cloud Services"
        VI["Video Indexer"]
        SEARCH["AI Search (Vector DB)"]
        MONITOR["Azure Monitor"]
    end

    subgraph "External AI Services"
        GROQ["Groq Llama 3.3-70B"]
        HF["HuggingFace Embeddings + Translation"]
    end

    subgraph "Data Storage"
        DISK_CACHE["Disk Cache (backend/cache/)"]
        PDF_KB["PDF Knowledge Base (backend/data/)"]
    end

    CLI --> API
    UI --> API
    API --> CACHE
    API --> TELE --> MONITOR
    API --> WF
    WF --> INDEXER
    WF --> AUDITOR
    INDEXER --> VI
    AUDITOR --> GROQ
    AUDITOR --> HF
    AUDITOR --> SEARCH
    SEARCH --> PDF_KB
    CACHE --> DISK_CACHE
```

## Request Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as Web Dashboard
    participant API as FastAPI Server
    participant Cache as Cache Service
    participant WF as LangGraph Workflow
    participant Indexer as Indexer Node
    participant VI as Azure Video Indexer
    participant Auditor as Auditor Node
    participant LLM as Groq LLM
    participant KB as Azure AI Search
    
    User->>UI: Paste YouTube URL
    UI->>API: POST /scan {video_url}
    API->>Cache: Check cache
    alt Cache HIT
        Cache-->>API: Return cached result
        API-->>UI: Instant response (from_cache=true)
    else Cache MISS
        API->>WF: Invoke workflow
        WF->>Indexer: index_video_node()
        Indexer->>Indexer: yt-dlp download
        Indexer->>VI: Upload video
        VI-->>Indexer: Return transcript + OCR
        Indexer-->>WF: Return extracted data
        WF->>Auditor: audit_content_node()
        Auditor->>Auditor: Language detection
        Auditor->>Auditor: Hindi->English translation
        Auditor->>Auditor: Fiction content classification
        Auditor->>KB: RAG similarity search
        KB-->>Auditor: Retrieved rules
        Auditor->>LLM: Threat analysis prompt
        LLM-->>Auditor: JSON flags + status
        Auditor->>Auditor: Normalize categories
        Auditor->>Auditor: Map timestamps
        Auditor->>Auditor: Build report
        Auditor-->>WF: Return flags + report
        WF-->>API: Return final state
        API->>Cache: Save result
        API-->>UI: Return response
    end
    UI-->>User: Display results dashboard
```

## Authentication Flow

```mermaid
flowchart LR
    A[User] --> B[FastAPI Server]
    B --> C{Cache?}
    C -->|Yes| D[Return Cached]
    C -->|No| E[Azure Video Indexer]
    E --> F[Groq LLM]
    F --> G[Generate Report]
    G --> H[Store in Cache]
    H --> I[Return to User]
```

**Note:** There is currently NO authentication layer. The API is open access.

## LangGraph Workflow (DAG)

```mermaid
graph LR
    START --> INDEXER[index_video_node]
    INDEXER --> AUDITOR[audit_content_node]
    AUDITOR --> END
    
    subgraph INDEXER["Indexer Node"]
        A1[Download YouTube] --> A2[Upload to Azure VI]
        A2 --> A3[Wait for Processing]
        A3 --> A4[Extract Transcript + OCR]
    end
    
    subgraph AUDITOR["Auditor Node"]
        B1[Language Detection] --> B2[Hindi->English Translation]
        B2 --> B3[Fiction Classification]
        B3 --> B4[RAG KB Query]
        B4 --> B5[LLM Threat Analysis]
        B5 --> B6[Category Normalization]
        B6 --> B7[Timestamp Mapping]
        B7 --> B8[Report Generation]
    end
```

## Component Details

### 1. API Layer (`backend/src/api/server.py`)
- FastAPI application (v3.0.0)
- CORS: Allow all origins (`*`)
- Serves static frontend from `frontend/`
- Endpoints: POST `/scan`, DELETE `/scan/cache`, GET `/cache`, DELETE `/cache`, GET `/health`

### 2. LangGraph Workflow (`backend/src/graph/workflow.py`)
- `StateGraph(VideoSecurityState)` with 2 nodes
- Entry: `indexer` → `auditor` → END
- State: TypedDict with `video_url`, `video_id`, `transcript`, `ocr_text`, `security_flags`, `final_status`, `final_report`, `errors`

### 3. Cache Service (`backend/src/services/cache_service.py`)
- Location: `backend/cache/`
- Key: SHA-256 hash of YouTube video ID (first 16 chars)
- Format: JSON files with `{video_url, cached_at, expires_in, result}`
- Expiry: Configurable via `CACHE_EXPIRY_DAYS` (default: 7)

### 4. Video Indexer Service (`backend/src/services/video_indexer.py`)
- Azure Video Indexer integration
- yt-dlp for YouTube downloads
- Token-based authentication (ARM → Account token)
- Polling-based processing status check (30s intervals)

### 5. Threat Analysis (`backend/src/graph/nodes.py`)
- Language detection via `langdetect`
- Hindi translation via `Helsinki-NLP/opus-mt-hi-en`
- Content type classification (6 categories)
- RAG via Azure AI Search with HuggingFace embeddings
- LLM analysis via Groq `llama-3.3-70b-versatile`
- Category normalization (keyword-based)
- Intelligence report formatting
