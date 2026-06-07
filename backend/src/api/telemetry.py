import os           
import logging      
from azure.monitor.opentelemetry import configure_azure_monitor  

logger = logging.getLogger("national-security-telemetry")


def setup_telemetry():
    """
    Initializes Azure Monitor OpenTelemetry.
    
    What is OpenTelemetry?
    - Industry-standard observability framework
    - Tracks: HTTP requests, database queries, errors, performance metrics
    - Sends this data to Azure Monitor (like a "flight data recorder" for your app)
    
    What does "hooks into FastAPI automatically" mean?
    - Once configured, it auto-captures every API request/response
    - No need to manually log each endpoint
    - Tracks response times, error rates, dependencies (like Azure Search calls)
    """
    
    # ========== STEP 1: RETRIEVE CONNECTION STRING ==========
    # Reads the Azure Monitor connection string from environment variables
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    # ========== STEP 2: CHECK IF CONFIGURED ==========
    if not connection_string:
        # If the environment variable is missing/empty, telemetry won't work
        logger.warning("No Instrumentation Key found. Telemetry is DISABLED.")
        return  # Exit function early - don't try to configure Azure Monitor

    # ========== STEP 3: CONFIGURE AZURE MONITOR ==========
    try:
        # configure_azure_monitor() does the heavy lifting:
        # 1. Registers automatic instrumentation for HTTP, DBs, and Logs
        # 2. Starts background thread to send data to Azure
        configure_azure_monitor(
            connection_string=connection_string,  # Where to send data
            logger_name="national-security-tracer"   # Updated custom tracer name
        )
        logger.info("✅ Azure Monitor Tracking Enabled & Connected!")
        
    except Exception as e:
        # ========== ERROR HANDLING ==========
        # If configuration fails (bad connection string, network issue, etc.)
        logger.error(f"Failed to initialize Azure Monitor: {e}")
        # Note: Function doesn't raise the error - telemetry failure shouldn't crash the app