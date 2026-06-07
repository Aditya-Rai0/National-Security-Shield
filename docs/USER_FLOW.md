# User Flow

## Web Dashboard Flow

```mermaid
flowchart TD
    A[User Opens Dashboard] --> B[Land on Scan View]
    B --> C{Paste YouTube URL}
    C --> D[Click "Scan Video"]
    D --> E[Progress View]
    
    E --> F[Step 1: Download & Index]
    F --> G[Step 2: Extract Transcript & OCR]
    G --> H[Step 3: Language Detection & Translation]
    H --> I[Step 4: Query Knowledge Base]
    I --> J[Step 5: LLM Threat Analysis]
    
    J --> K{Result}
    K -->|Safe| L[Results View: Safe Banner]
    K -->|Flagged| M[Results View: Flagged Banner]
    
    L --> N[View Intelligence Report]
    M --> N
    
    N --> O[Threat Cards + Timeline]
    O --> P[Analytics View]
    
    subgraph "Cache Path"
        C --> Q{Cache Hit?}
        Q -->|Yes| R[Instant Results]
        Q -->|No| D
    end
```

## CLI Flow

```mermaid
flowchart TD
    A[Terminal] --> B[python main.py -u <youtube_url>]
    B --> C{Check Cache}
    C -->|Hit| D[Print Cached Report]
    C -->|Miss| E[Invoke LangGraph Workflow]
    E --> F[Indexer Node: Download + Azure VI]
    F --> G[Auditor Node: Analyze + LLM]
    G --> H[Save to Cache]
    H --> I[Print Final Report]
    D --> J[Exit]
    I --> J
```

## Content Analysis Decision Tree

```mermaid
flowchart TD
    A[Video Transcript] --> B[Language Detection]
    B --> C{Hindi/Urdu?}
    C -->|Yes| D[Translate to English]
    C -->|No| E[Keep English]
    D --> F
    E --> F[Content Type Classification]
    
    F --> G{Fiction?}
    G -->|News Broadcast| H[SAFE - News]
    G -->|Movie/Web Series| I[SAFE - Fiction]
    G -->|Music/Rap| J[SAFE - Artistic]
    G -->|Video Game| K[SAFE - Gaming]
    G -->|Comedy/Satire| L[SAFE - Satire]
    G -->|Documentary| M[SAFE - Educational]
    G -->|Not Fiction| N[Proceed to Threat Analysis]
    
    N --> O[RAG Query to Knowledge Base]
    O --> P[LLM Threat Analysis]
    
    P --> Q{Threats Found?}
    Q -->|Yes| R[Generate Flags + Report]
    Q -->|No| S[Status: SAFE]
    
    R --> T[Status: FLAGGED_FOR_TAKEDOWN]
    T --> U[Build Intelligence Report]
    S --> U
```

## Security Analyst Workflow (Target)

```mermaid
flowchart TD
    A[Analyst Login] --> B[Dashboard View]
    B --> C[Review Flagged Videos]
    C --> D{Review Each Flag}
    D --> E[View Threat Details]
    E --> F[View Intelligence Report]
    F --> G{Decision}
    G -->|Confirm Threat| H[Request Takedown]
    G -->|False Positive| I[Dismiss Flag]
    G -->|Escalate| J[Forward to Agency]
    H --> K[IT Act Section 69A]
    J --> L[NIA / CERT-In]
```

## Threat Categories Detected

| Category | Description | Example Signals |
|----------|-------------|-----------------|
| **TERRORISM** | Bombings, attacks, explosions, killings | "bomb", "attack", "blast", "terror", "shoot" |
| **BORDER_SECURITY** | Military/troop movements, patrol gaps | "border", "army", "troop", "CRPF", "BSF" |
| **CYBER_THREAT** | Hacking, malware, phishing | "hack", "cyber", "malware", "ransomware" |
| **FAKE_NEWS** | Disinformation, propaganda | "fake", "rumor", "misinformation", "propaganda" |
| **HATE_SPEECH** | Communal violence, religious targeting | "hate", "communal", "religion", "violence against" |
| **ESPIONAGE** | Intelligence leaks, spy activity | "spy", "ISI", "secret leak", "intelligence leak" |

## Severity Levels

| Level | Meaning | Action Required |
|-------|---------|-----------------|
| **CRITICAL** | Imminent threat, actionable intelligence | Immediate takedown (IT Act 69A), forward to NIA |
| **HIGH** | Significant threat, communal hate speech | Escalate to CERT-In within 24 hours |
| **WARNING** | Suspicious pattern, possible propaganda | Routine monitoring |
