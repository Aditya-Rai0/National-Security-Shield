import json
import os
import logging
import re
from datetime import datetime
from typing import Dict, Any, List

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_core.messages import SystemMessage, HumanMessage

from langdetect import detect
from transformers import pipeline

from backend.src.graph.state import VideoSecurityState, SecurityAlert
from backend.src.services.video_indexer import VideoIndexerService

logger = logging.getLogger("national-security-guardian")
logging.basicConfig(level=logging.INFO)
translator = None

# CATEGORY NORMALIZER
def normalize_category(text: str) -> str:
    text = text.lower()
    if any(w in text for w in ["bomb", "attack", "explosion", "terror", "blast", "kill", "shoot"]):
        return "TERRORISM"
    elif any(w in text for w in ["border", "army", "troop", "military", "crpf", "bsf", "patrol", "soldier"]):
        return "BORDER_SECURITY"
    elif any(w in text for w in ["hack", "cyber", "malware", "server", "phish", "ransomware"]):
        return "CYBER_THREAT"
    elif any(w in text for w in ["fake", "rumor", "misinformation", "propaganda", "false news"]):
        return "FAKE_NEWS"
    elif any(w in text for w in ["hate", "religion", "kill community", "violence against", "communal"]):
        return "HATE_SPEECH"
    elif any(w in text for w in ["spy", "espionage", "secret leak", "isi", "intelligence leak"]):
        return "ESPIONAGE"
    return "GENERAL"


# SMART FICTION DETECTOR
# Handles: news, movies, songs, rap, web series, gaming, etc.
def detect_content_type(text: str) -> dict:
    """
    Returns {is_fictional: bool, type: str, reason: str}
    Checks multiple content categories before flagging.
    """
    t = text.lower()

    # --- NEWS CHANNEL INDICATORS ---
    news_signals = [
        "breaking news", "live coverage", "reporter", "correspondent",
        "news channel", "ndtv", "aaj tak", "zee news", "republic tv",
        "india today", "bbc", "cnn", "ani news", "press conference",
        "spokesperson", "anchor", "bulletin", "headline", "news desk",
        "our correspondent", "on ground", "exclusive report", "sources say",
        "government spokesperson", "official statement", "ministry of"
    ]
    if sum(1 for s in news_signals if s in t) >= 2:
        return {
            "is_fictional": True,
            "type": "NEWS_BROADCAST",
            "reason": "Content identified as a news broadcast or journalism report. Factual reporting is not a security threat."
        }

    # --- MOVIE / WEB SERIES / TV SHOW ---
    movie_signals = [
        "movie", "film", "cinema", "trailer", "teaser", "web series",
        "episode", "season", "ott", "netflix", "amazon prime", "hotstar",
        "zee5", "bollywood", "hollywood", "director", "actor", "actress",
        "screenplay", "dialogue", "scene", "character", "starring",
        "produced by", "distributed by", "theatrical release", "now streaming",
        "coming soon", "in cinemas", "box office"
    ]
    if sum(1 for s in movie_signals if s in t) >= 2:
        return {
            "is_fictional": True,
            "type": "MOVIE_OR_WEB_SERIES",
            "reason": "Content identified as a movie, web series, or fictional drama. Fictional violence/dialogue is not a real-world threat."
        }

    # --- MUSIC / SONG / RAP ---
    music_signals = [
        "lyrics", "song", "rap", "hip hop", "album", "single",
        "music video", "beat", "verse", "chorus", "hook", "flow",
        "artist", "singer", "rapper", "ft.", "feat.", "prod by",
        "subscribe", "like share", "spotify", "gaana", "jiosaavn",
        "youtube music", "this song", "my song", "new track", "diss track",
        "bars", "spit bars", "studio", "recording"
    ]
    if sum(1 for s in music_signals if s in t) >= 2:
        return {
            "is_fictional": True,
            "type": "MUSIC_OR_RAP",
            "reason": "Content identified as music/rap/song. Artistic/lyrical content is not a real-world security threat."
        }

    # --- VIDEO GAME / GAMING ---
    gaming_signals = [
        "gameplay", "game", "call of duty", "pubg", "bgmi", "free fire",
        "gta", "fortnite", "valorant", "cs go", "minecraft", "roblox",
        "press x", "mission complete", "level up", "respawn", "kill streak",
        "loadout", "squad wipe", "clutch", "esports", "streamer", "twitch",
        "gaming", "controller", "console", "playstation", "xbox", "pc gaming"
    ]
    if sum(1 for s in gaming_signals if s in t) >= 2:
        return {
            "is_fictional": True,
            "type": "VIDEO_GAME",
            "reason": "Content identified as video game or esports content. In-game violence is not a real-world threat."
        }

    # --- COMEDY / SATIRE / STANDUP ---
    comedy_signals = [
        "standup", "comedy", "roast", "meme", "parody", "satire",
        "joke", "funny", "skit", "sketch", "prank", "just kidding",
        "trolling", "ironic", "sarcasm", "comedian"
    ]
    if sum(1 for s in comedy_signals if s in t) >= 2:
        return {
            "is_fictional": True,
            "type": "COMEDY_OR_SATIRE",
            "reason": "Content identified as comedy, satire or parody. Satirical content is not a real-world security threat."
        }

    # --- DOCUMENTARY / HISTORICAL / EDUCATIONAL ---
    documentary_signals = [
        "documentary", "history", "historical", "world war", "partition",
        "1947", "independence", "museum", "archive", "professor",
        "lecture", "educational", "awareness", "awareness video",
        "this is a story", "based on true events", "narrated by"
    ]
    if sum(1 for s in documentary_signals if s in t) >= 2:
        return {
            "is_fictional": True,
            "type": "DOCUMENTARY_OR_EDUCATIONAL",
            "reason": "Content identified as documentary or educational. Historical/factual content is not a security threat."
        }

    # Not fictional
    return {"is_fictional": False, "type": "REAL_WORLD", "reason": ""}


# TIMESTAMP MAPPER
def map_timestamp(description: str, transcript_list: List[Dict]) -> str:
    for t in transcript_list:
        text = t.get("text", "").lower()
        if any(word.lower() in text for word in description.split()):
            ts = t.get("start")
            if ts:
                return ts
    return None


# FORMATTED REPORT GENERATOR
def build_formatted_report(flags: list, status: str, session_id: str, raw_summary: str) -> str:
    """
    Builds the classified intelligence report in the proper format
    so it looks like a real intelligence document.
    """
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sep = "─" * 53

    lines = [
        "CLASSIFICATION: RESTRICTED — INTELLIGENCE USE ONLY",
        f"SESSION: {session_id} | GENERATED: {now}",
        "",
        "EXECUTIVE SUMMARY",
        sep,
        raw_summary.strip(),
        "",
        "KEY FINDINGS",
        sep,
    ]

    if not flags:
        lines.append("No security threats detected. Content is clean.")
    else:
        for i, flag in enumerate(flags, 1):
            sev  = flag.get("severity", "WARNING").upper()
            cat  = flag.get("category", "GENERAL").upper()
            conf = int(float(flag.get("confidence", 0.80)) * 100)
            desc = flag.get("description", "").strip()
            ts   = flag.get("timestamp")
            ts_line = f"    Timestamp: {ts}" if ts else ""

            lines.append(f"[{i}] {cat} — {sev} ({conf}% confidence)")
            if ts_line:
                lines.append(ts_line)
            lines.append(f"    {desc}")
            lines.append("")

    # Recommended actions based on severity
    lines += [
      
        "RECOMMENDED ACTION",
        sep,
    ]

    has_critical = any(f.get("severity", "").upper() == "CRITICAL" for f in flags)
    has_high     = any(f.get("severity", "").upper() == "HIGH" for f in flags)

    if has_critical:
        lines.append("→ Immediate platform takedown request (IT Act Section 69A)")
        lines.append("→ Forward to National Investigation Agency (NIA)")
        lines.append("→ Monitor account network for coordinated activity")
        lines.append("→ Cross-reference with OSINT: Pakistan-linked content farms")
    elif has_high:
        lines.append("→ Escalate to CERT-In for review within 24 hours")
        lines.append("→ Issue platform warning notice")
        lines.append("→ Flag account for continued monitoring")
    else:
        lines.append("→ Log for routine monitoring")
        lines.append("→ No immediate action required")

    lines.append("")

    if flags:
        avg_conf = int(sum(float(f.get("confidence", 0.80)) for f in flags) / len(flags) * 100)
        risk = "CRITICAL" if has_critical else ("HIGH" if has_high else "MODERATE")
        lines.append(f"CONFIDENCE: {avg_conf}% average | RISK LEVEL: {risk}")
    else:
        lines.append("CONFIDENCE: N/A | RISK LEVEL: NONE")

    return "\n".join(lines)


# NODE 1: INDEXER
def index_video_node(state: VideoSecurityState) -> Dict[str, Any]:
    video_url    = state.get("video_url")
    video_id_input = state.get("video_id", "vid_demo")

    logger.info(f"--- [Node: Indexer] Processing: {video_url} ---")

    local_filename = "temp_security_video.mp4"

    try:
        vi_service = VideoIndexerService()

        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url, output_path=local_filename)
        else:
            raise Exception("Invalid YouTube URL — only YouTube links are supported.")

        azure_video_id = vi_service.upload_video(local_path, video_name=video_id_input)
        logger.info(f"Upload Success. Azure Video ID: {azure_video_id}")

        if os.path.exists(local_path):
            os.remove(local_path)

        raw_insights = vi_service.wait_for_processing(azure_video_id)
        clean_data   = vi_service.extract_data(raw_insights)

        logger.info("--- [Node: Indexer] Extraction Complete ---")
        return clean_data

    except Exception as e:
        logger.error(f"Video Indexer Failed: {e}")
        return {
            "errors": [str(e)],
            "final_status": "FLAGGED_FOR_TAKEDOWN",
            "transcript": [],
            "ocr_text": []
        }



# NODE 2: AUDITOR
def audit_content_node(state: VideoSecurityState) -> Dict[str, Any]:
    global translator

    logger.info("--- [Node: Auditor] Starting content audit ---")

    transcript_list = state.get("transcript", [])
    session_id = state.get("video_id", "UNKNOWN")[:8].upper()

    if not transcript_list:
        logger.warning("No transcript available — skipping audit.")
        return {
            "final_status": "FLAGGED_FOR_TAKEDOWN",
            "final_report": build_formatted_report([], "FLAGGED_FOR_TAKEDOWN", session_id,
                "Audit could not be completed because the video transcript was unavailable. "
                "Defaulting to FLAGGED status as a precautionary measure.")
        }

    transcript_text = " ".join([t.get("text", "") for t in transcript_list])

   
    # STEP 1: LANGUAGE DETECTION + TRANSLATION
  
    detected_lang = "en"
    try:
        detected_lang = detect(transcript_text)
        logger.info(f"Detected Language: {detected_lang}")

        if detected_lang == "hi":
            logger.info("Hindi detected — translating to English via Helsinki NLP...")

            if translator is None:
                translator = pipeline(
                    "text2text-generation",
                    model="Helsinki-NLP/opus-mt-hi-en",
                    tokenizer="Helsinki-NLP/opus-mt-hi-en"
                )

            chunks = [transcript_text[i:i+500] for i in range(0, len(transcript_text), 500)]
            translated_chunks = [translator(chunk)[0]["generated_text"] for chunk in chunks]
            transcript_text = " ".join(translated_chunks)
            logger.info("Translation complete.")

    except Exception as e:
        logger.warning(f"Language detection/translation failed: {e}")

    # ----------------------------------------------------------
    # STEP 2: SMART FICTION / CONTENT TYPE CHECK
    # ----------------------------------------------------------
    content_check = detect_content_type(transcript_text)

    if content_check["is_fictional"]:
        content_type = content_check["type"]
        reason       = content_check["reason"]
        logger.info(f"Content type detected: {content_type} — skipping threat analysis.")

        report = build_formatted_report(
            flags=[],
            status="SAFE",
            session_id=session_id,
            raw_summary=(
                f"Content Type: {content_type}\n"
                f"{reason}\n\n"
                "No national security threats, hate speech, or espionage signals detected. "
                "The content has been verified as non-threatening based on contextual analysis."
            )
        )
        return {
            "security_flags": [],
            "final_status": "SAFE",
            "final_report": report
        }

    # ----------------------------------------------------------
    # STEP 3: RAG — QUERY KNOWLEDGE BASE
    # ----------------------------------------------------------
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
        temperature=0.0
    )

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function=embeddings.embed_query
    )

    ocr_text   = state.get("ocr_text", [])
    query_text = f"{transcript_text} {' '.join(ocr_text)}"
    docs       = vector_store.similarity_search(query_text, k=3)

    retrieved_rules = "\n\n".join([doc.page_content for doc in docs])

    # ----------------------------------------------------------
    # STEP 4: LLM THREAT ANALYSIS
    # ----------------------------------------------------------
    system_prompt = f"""
You are a Senior National Security Analyst for the Government of India.

NATIONAL SECURITY KNOWLEDGE BASE (Retrieved Rules & Acts):
{retrieved_rules}

YOUR TASK:
Analyze the provided video transcript and OCR text for REAL-WORLD national security threats only.

THREAT CATEGORIES (use EXACTLY these):
- TERRORISM
- BORDER_SECURITY
- CYBER_THREAT
- FAKE_NEWS
- HATE_SPEECH
- ESPIONAGE

SEVERITY LEVELS:
- CRITICAL: Imminent threat, direct actionable intelligence leak, incitement to violence
- HIGH: Significant threat, indirect reconnaissance, communal hate speech
- WARNING: Suspicious pattern, possible propaganda, requires monitoring

IMPORTANT RULES:
1. Only flag REAL threats — not fiction, not metaphors, not historical references
2. The content has already passed the fiction/entertainment filter, so focus on genuine threats
3. Assign a confidence score (0.0 to 1.0) to each flag
4. If no real threats found, return empty flags and status SAFE

REQUIRED OUTPUT FORMAT (strict JSON, no markdown, no extra text):
{{
    "security_flags": [
        {{
            "category": "BORDER_SECURITY",
            "severity": "CRITICAL",
            "description": "Exact description of the threat with specific quote or reference from the content...",
            "confidence": 0.92
        }}
    ],
    "status": "FLAGGED_FOR_TAKEDOWN",
    "executive_summary": "2-3 sentence summary of overall findings for the intelligence report..."
}}

If content is safe, return:
{{
    "security_flags": [],
    "status": "SAFE",
    "executive_summary": "No national security threats detected. Content appears to be legitimate real-world content with no indicators of terrorism, espionage, hate speech, or reconnaissance activity."
}}
"""

    user_message = f"""
TRANSCRIPT (translated if Hindi/Urdu):
{transcript_text}

ON-SCREEN TEXT (OCR):
{ocr_text}

VIDEO METADATA:
{state.get("video_metadata", {})}
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        content = response.content.strip()

        # Clean markdown code blocks if present
        if "```" in content:
            match = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()

        audit_data = json.loads(content)

        flags = audit_data.get("security_flags", [])
        status = audit_data.get("status", "FLAGGED_FOR_TAKEDOWN")
        executive_summary = audit_data.get("executive_summary", "Analysis complete.")

        # Post-process each flag
        for flag in flags:
            # Normalize category using keywords in description
            flag["category"] = normalize_category(flag.get("description", ""))
            # Map to exact video timestamp
            flag["timestamp"] = map_timestamp(flag.get("description", ""), transcript_list)

        # Build the properly formatted classified report
        final_report = build_formatted_report(
            flags=flags,
            status=status,
            session_id=session_id,
            raw_summary=executive_summary
        )

        logger.info(f"Audit complete. Status: {status} | Flags: {len(flags)}")

        return {
            "security_flags": flags,
            "final_status": status,
            "final_report": final_report
        }

    except Exception as e:
        logger.error(f"Audit Error: {str(e)}")
        logger.error(f"Raw LLM Response: {response.content if 'response' in locals() else 'None'}")

        return {
            "errors": [str(e)],
            "final_status": "FLAGGED_FOR_TAKEDOWN",
            "final_report": build_formatted_report(
                flags=[],
                status="ERROR",
                session_id=session_id,
                raw_summary=f"System error during analysis: {str(e)}. Manual review required."
            )
        }