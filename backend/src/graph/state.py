import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict

# 1. Define the Schema for a Single Security Alert
class SecurityAlert(TypedDict):
    category: str           # e.g., "NATIONAL_SECURITY_LEAK", "HATE_SPEECH", "RIOT_INCITEMENT", "ESPIONAGE"
    description: str        # Violation ki exact detail (e.g., "Mention of troop movement in XYZ sector")
    severity: str           # "CRITICAL" | "HIGH" | "WARNING"
    timestamp: Optional[str]# Video me kis time par ye bola gaya/dikhaya gaya (e.g., "01:24")

# 2. Define the Global Graph State
class VideoSecurityState(TypedDict):
    """
    Defines the data schema for the LangGraph execution context for National Security auditing.
    """
    # --- Input Parameters ---
    video_url: str
    video_id: str

    # --- Ingestion & Extraction Data ---
    # Optional because they are populated asynchronously by the Indexer Node.
    local_file_path: Optional[str]  
    video_metadata: Dict[str, Any]  # e.g., {"duration": 15, "platform": "YouTube"}
    transcript: Optional[str]       # Full extracted speech-to-text (Video me kya bola gaya)
    ocr_text: List[str]             # List of recognized on-screen text (Screen par kya likha tha)

    # --- Analysis Output ---
    # annotated with operator.add to allow append-only updates from multiple nodes.
    security_flags: Annotated[List[SecurityAlert], operator.add]
    
    # --- Final Deliverables ---
    final_status: str               # "SAFE" | "FLAGGED_FOR_TAKEDOWN"
    final_report: str               # Markdown summary security agency/moderators ke liye
    
    # --- System Observability ---
    # Appends system-level errors (e.g., API timeouts) without halting execution logic.
    errors: Annotated[List[str], operator.add]