import os
import uuid
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# ========== STEP 1: LOAD ENVIRONMENT VARIABLES ==========
from dotenv import load_dotenv
load_dotenv(override=True)

# ========== STEP 2: INITIALIZE TELEMETRY ==========
from backend.src.api.telemetry import setup_telemetry
setup_telemetry()

# ========== STEP 3: IMPORT WORKFLOW GRAPH ==========
from backend.src.graph.workflow import app as security_graph

# ========== STEP 4: IMPORT CACHE SERVICE ==========
from backend.src.services.cache_service import (
    get_cached_result,
    save_to_cache,
    invalidate_cache,
    list_cache,
    clear_all_cache,
)

# ========== STEP 5: CONFIGURE LOGGING ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("national-security-api")


# ========== STEP 6: CREATE FASTAPI APPLICATION ==========
app = FastAPI(
    title="National Security Guardian API",
    description="AI-powered video threat detection with intelligent caching. Same URL = instant result.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== SERVE FRONTEND UI ==========
# frontend/index.html ko http://localhost:8000 pe serve karega
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("frontend/index.html")


# ========== STEP 7: PYDANTIC MODELS ==========

class AuditRequest(BaseModel):
    """Request body structure."""
    video_url: str
    force_rescan: bool = False


class SecurityAlertModel(BaseModel):
    """Single security threat ka structure."""
    category:    str
    severity:    str
    description: str
    timestamp:   Optional[str]   = None
    confidence:  Optional[float] = None


class AuditResponse(BaseModel):
    """API response structure."""
    session_id:     str
    video_id:       str
    status:         str
    final_report:   str
    security_flags: List[SecurityAlertModel]
    from_cache:     bool = False


# ========== STEP 8: MAIN SCAN ENDPOINT ==========

@app.post("/scan", response_model=AuditResponse)
async def scan_video(request: AuditRequest):
    session_id     = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"

    logger.info(f"Scan Request | URL: {request.video_url[:70]} | Force: {request.force_rescan}")

    # Cache check
    if not request.force_rescan:
        cached = get_cached_result(request.video_url)
        if cached is not None:
            logger.info("Cache HIT — returning stored result instantly")
            return AuditResponse(
                session_id     = session_id,
                video_id       = cached.get("video_id", video_id_short),
                status         = cached.get("final_status", "UNKNOWN"),
                final_report   = cached.get("final_report", "No report available."),
                security_flags = cached.get("security_flags", []),
                from_cache     = True,
            )

    # Cache miss — full pipeline
    logger.info("Cache MISS — running full scan pipeline")

    initial_inputs = {
        "video_url":      request.video_url,
        "video_id":       video_id_short,
        "security_flags": [],
        "errors":         []
    }

    try:
        final_state = security_graph.invoke(initial_inputs)

        # Save to cache
        save_to_cache(request.video_url, {
            "video_id":       final_state.get("video_id", video_id_short),
            "final_status":   final_state.get("final_status", "UNKNOWN"),
            "final_report":   final_state.get("final_report", ""),
            "security_flags": final_state.get("security_flags", []),
        })

        return AuditResponse(
            session_id     = session_id,
            video_id       = final_state.get("video_id", video_id_short),
            status         = final_state.get("final_status", "UNKNOWN"),
            final_report   = final_state.get("final_report", "No report generated."),
            security_flags = final_state.get("security_flags", []),
            from_cache     = False,
        )

    except Exception as e:
        logger.error(f"Audit Failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"National Security Workflow Execution Failed: {str(e)}"
        )


# ========== STEP 9: CACHE MANAGEMENT ENDPOINTS ==========

@app.delete("/scan/cache")
def clear_url_cache(video_url: str):
    deleted = invalidate_cache(video_url)
    return {
        "success": deleted,
        "message": "Cache cleared for this URL." if deleted else "No cached entry found for this URL."
    }


@app.get("/cache")
def view_all_cache():
    entries = list_cache()
    return {"total": len(entries), "entries": entries}


@app.delete("/cache")
def wipe_all_cache():
    count = clear_all_cache()
    return {"deleted": count, "message": f"Cleared {count} cached entries successfully."}


# ========== STEP 10: HEALTH CHECK ==========

@app.get("/health")
def health_check():
    cache_entries = len(list_cache())
    return {
        "status":        "Active",
        "service":       "National Security Guardian AI",
        "version":       "3.0.0",
        "cache_entries": cache_entries,
    }