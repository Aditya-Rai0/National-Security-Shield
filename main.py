"""
Main Execution Entry Point for National Security Guardian AI.

This file is the "control center" that starts and manages the entire 
security audit workflow. Think of it as the master switch that:
1. Sets up the audit request
2. Checks cache — same URL = instant result, no re-processing
3. Runs the AI workflow only if cache miss
4. Saves result to cache for future use
5. Displays the final security report
"""

import argparse
import uuid
import json
import logging
from pprint import pprint

from dotenv import load_dotenv
load_dotenv(override=True)

from backend.src.graph.workflow import app

# ✅ Cache service import
from backend.src.services.cache_service import get_cached_result, save_to_cache

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("national-security-runner")


def run_cli_simulation(video_url: str):
    """
    Simulates a Video National Security Audit request.
    Same URL dobara doge to cache se instant result milega.
    """

    # ========== STEP 1: GENERATE SESSION ID ==========
    session_id = str(uuid.uuid4())
    logger.info(f"Starting Security Audit Session: {session_id}")

    # ========== STEP 2: DEFINE INITIAL STATE ==========
    initial_inputs = {
        "video_url":      video_url,
        "video_id":       f"vid_{session_id[:8]}",
        "security_flags": [],
        "errors":         []
    }

    print("\n--- 1. INITIALIZING WORKFLOW ---")
    print(f"Input Payload: \n{json.dumps(initial_inputs, indent=2)}")

    # ========== STEP 3: CACHE CHECK ==========
    # Same URL pehle scan ho chuki hai? Cache se instant result do.
    cached = get_cached_result(video_url)

    if cached is not None:
        print("\n⚡ CACHE HIT — Returning stored result instantly (no Azure credit used)\n")

        print("\n=== 🛡️ NATIONAL SECURITY AUDIT REPORT (FROM CACHE) ===")
        print(f"Video ID:    {cached.get('video_id', 'N/A')}")
        print(f"Status:      {cached.get('final_status', 'UNKNOWN')}")

        print("\n[ SECURITY THREATS DETECTED ]")
        results = cached.get('security_flags', [])
        if results:
            for issue in results:
                print(f"- [{issue.get('severity')}] {issue.get('category')}: {issue.get('description')}")
        else:
            print("✅ No security threats or hate speech detected. Video is safe.")

        print("\n[ FINAL SUMMARY ]")
        print(cached.get('final_report', 'No report available.'))
        return  # Pipeline nahi chalega — kaam khatam

    # ========== STEP 4: CACHE MISS — FULL PIPELINE CHALAO ==========
    logger.info("Cache MISS — running full scan pipeline (Azure + LLM)")
    print("\n--- 2. CACHE MISS — Running full AI pipeline... ---\n")

    try:
        final_state = app.invoke(initial_inputs)

        # ========== STEP 5: RESULT CACHE MEIN SAVE KARO ==========
        # Agla request same URL ke liye instant hoga
        save_to_cache(video_url, {
            "video_id":       final_state.get("video_id", initial_inputs["video_id"]),
            "final_status":   final_state.get("final_status", "UNKNOWN"),
            "final_report":   final_state.get("final_report", ""),
            "security_flags": final_state.get("security_flags", []),
        })
        logger.info("Result saved to cache — next run will be instant.")

        # ========== STEP 6: OUTPUT RESULTS ==========
        print("\n--- 3. WORKFLOW EXECUTION COMPLETE ---")
        print("\n=== 🛡️ NATIONAL SECURITY AUDIT REPORT ===")

        print(f"Video ID:    {final_state.get('video_id')}")
        print(f"Status:      {final_state.get('final_status')}")

        print("\n[ SECURITY THREATS DETECTED ]")
        results = final_state.get('security_flags', [])
        if results:
            for issue in results:
                print(f"- [{issue.get('severity')}] {issue.get('category')}: {issue.get('description')}")
        else:
            print("✅ No security threats or hate speech detected. Video is safe.")

        print("\n[ FINAL SUMMARY ]")
        print(final_state.get('final_report'))

    except Exception as e:
        logger.error(f"Workflow Execution Failed: {str(e)}")
        raise e


# ========== PROGRAM ENTRY POINT ==========
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run National Security AI Guardian")
    parser.add_argument("-u", "--url", required=True, help="YouTube Video URL to audit")
    args = parser.parse_args()

    run_cli_simulation(args.url)