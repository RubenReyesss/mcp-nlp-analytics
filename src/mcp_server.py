"""
Sentiment Evolution Tracker MCP Server
Analyzes sentiment trajectories in conversations to detect opinion changes and predict risks.

Key MCP Protocol Requirements:
1. MUST use stdio_server() for communication with Claude Desktop
2. MUST NOT log to stdout (reserved for protocol messages)
3. MUST log to stderr or file only
4. MUST return TextContent with proper formatting
5. MUST handle async/await correctly
"""

import json
import logging
import asyncio
import sys
import os
from typing import Any

# MCP imports - CRITICAL: correct imports for MCP protocol
from mcp.server import Server
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Import analysis modules
from sentiment_analyzer import SentimentAnalyzer
from pattern_detector import PatternDetector
from risk_predictor import RiskPredictor
from database_manager import AnalysisDatabase

# ============================================================================
# LOGGING SETUP - CRITICAL FOR DEBUGGING
# Log to file and stderr ONLY (never stdout - that's for MCP protocol)
# ============================================================================

# Get absolute path for log file
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mcp_server.log')

# Configure logging to file
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Also send errors to stderr (Claude Desktop will capture these)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stderr_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)

logger.info("=" * 80)
logger.info("MCP Server starting up")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Log file: {log_file}")
logger.info("=" * 80)

# ============================================================================
# INITIALIZE MCP SERVER
# ============================================================================

server = Server("sentiment-evolution-tracker")

# Initialize analysis modules - CRITICAL: do this before accepting connections
logger.info("Initializing analysis modules...")
try:
    sentiment_analyzer = SentimentAnalyzer()
    pattern_detector = PatternDetector()
    risk_predictor = RiskPredictor()
    db = AnalysisDatabase()
    logger.info("✓ All analysis modules initialized successfully")
    logger.info(f"✓ Database: {db.db_path}")
except Exception as e:
    error_msg = f"FATAL: Failed to initialize modules: {str(e)}"
    logger.error(error_msg, exc_info=True)
    sys.stderr.write(error_msg + "\n")
    sys.exit(1)

# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    logger.debug("list_tools() called by Claude")
    
    tools = [
        Tool(
            name="analyze_sentiment_evolution",
            description="Analyzes sentiment evolution across a series of messages to detect trending patterns (improving, declining, or stable sentiment)",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of messages to analyze, ordered chronologically"
                    }
                },
                "required": ["messages"]
            }
        ),
        Tool(
            name="detect_risk_signals",
            description="Detects risk signals in conversations (competitor mentions, frustration, disengagement, pricing concerns)",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of messages to analyze for risk signals"
                    },
                    "context_type": {
                        "type": "string",
                        "enum": ["customer", "employee", "email"],
                        "description": "Type of conversation context"
                    }
                },
                "required": ["messages", "context_type"]
            }
        ),
        Tool(
            name="predict_next_action",
            description="Predicts the likely next action or outcome based on sentiment and signals (CHURN, RESOLUTION, ESCALATION)",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of messages for analysis"
                    },
                    "context_type": {
                        "type": "string",
                        "enum": ["customer", "employee", "email"],
                        "description": "Type of conversation context"
                    }
                },
                "required": ["messages", "context_type"]
            }
        ),
        Tool(
            name="get_customer_history",
            description="Retrieves historical analysis data for a specific customer, including all previous analyses, trends, and active alerts. THIS REQUIRES DATABASE ACCESS - Claude cannot do this alone!",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Unique customer identifier"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="get_high_risk_customers",
            description="Returns list of all customers currently at high risk of churn. THIS REQUIRES DATABASE ACCESS - Claude cannot do this alone!",
            inputSchema={
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "number",
                        "description": "Risk threshold (0-1, default 0.75)",
                        "default": 0.75
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_database_statistics",
            description="Returns overall statistics about analyzed customers and alerts. THIS REQUIRES DATABASE ACCESS - Claude cannot do this alone!",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="save_analysis",
            description="Explicitly save a sentiment analysis with a customer name to the database. Use this to save analysis results with a specific customer identifier.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Unique customer identifier (e.g., 'LUIS_RAMIREZ', 'CUST_001_ACME')"
                    },
                    "customer_name": {
                        "type": "string",
                        "description": "Customer display name (optional)"
                    },
                    "messages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of messages in the conversation"
                    },
                    "sentiment_score": {
                        "type": "number",
                        "description": "Overall sentiment score (0-100)"
                    },
                    "trend": {
                        "type": "string",
                        "enum": ["RISING", "DECLINING", "STABLE"],
                        "description": "Sentiment trend"
                    },
                    "risk_level": {
                        "type": "string",
                        "description": "Risk classification (LOW, MEDIUM, HIGH)"
                    },
                    "predicted_action": {
                        "type": "string",
                        "description": "Recommended action (CHURN, RESOLUTION, ESCALATION)"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence level (0-1.0)"
                    },
                    "context_type": {
                        "type": "string",
                        "enum": ["customer", "employee", "email"],
                        "description": "Type of conversation",
                        "default": "customer"
                    }
                },
                "required": ["customer_id", "messages", "sentiment_score", "trend", "predicted_action", "confidence"]
            }
        )
    ]
    
    logger.info(f"✓ Returning {len(tools)} tools to Claude")
    return tools


# ============================================================================
# TOOL HANDLERS
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Execute tool based on name and arguments.
    ALL ERRORS are logged to stderr and file.
    """
    
    try:
        logger.info(f"Tool call received: {name}")
        logger.debug(f"Arguments: {arguments}")
        
        if name == "analyze_sentiment_evolution":
            # Extract messages - must be non-empty
            messages = arguments.get("messages", [])
            if not messages or not isinstance(messages, list):
                error_msg = "Missing or invalid 'messages' parameter (must be non-empty array)"
                logger.warning(f"analyze_sentiment_evolution: {error_msg}")
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
            
            logger.info(f"Analyzing sentiment evolution for {len(messages)} messages")
            result = sentiment_analyzer.analyze_evolution(messages)
            
            # Save to database
            customer_id = arguments.get("customer_id", f"customer_{hash(str(messages))}")
            db.save_analysis(customer_id, "conversation", messages, result)
            logger.info(f"✓ analyze_sentiment_evolution completed and saved to database")
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "detect_risk_signals":
            messages = arguments.get("messages", [])
            context_type = arguments.get("context_type", "customer")
            
            if not messages or not isinstance(messages, list):
                error_msg = "Missing or invalid 'messages' parameter (must be non-empty array)"
                logger.warning(f"detect_risk_signals: {error_msg}")
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
            
            if context_type not in ["customer", "employee", "email"]:
                context_type = "customer"
                logger.info(f"Invalid context_type, defaulting to 'customer'")
            
            logger.info(f"Detecting risk signals for {len(messages)} messages (context: {context_type})")
            result = pattern_detector.detect_signals(messages, context_type)
            
            # Save to database
            customer_id = arguments.get("customer_id", f"customer_{hash(str(messages))}")
            db.save_analysis(customer_id, context_type, messages, result)
            logger.info(f"✓ detect_risk_signals completed and saved to database")
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "predict_next_action":
            messages = arguments.get("messages", [])
            context_type = arguments.get("context_type", "customer")
            
            if not messages or not isinstance(messages, list):
                error_msg = "Missing or invalid 'messages' parameter (must be non-empty array)"
                logger.warning(f"predict_next_action: {error_msg}")
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
            
            if context_type not in ["customer", "employee", "email"]:
                context_type = "customer"
                logger.info(f"Invalid context_type, defaulting to 'customer'")
            
            logger.info(f"Predicting next action for {len(messages)} messages (context: {context_type})")
            result = risk_predictor.predict_action(messages, context_type)
            
            # Save to database
            customer_id = arguments.get("customer_id", f"customer_{hash(str(messages))}")
            db.save_analysis(customer_id, context_type, messages, result)
            logger.info(f"✓ predict_next_action completed and saved to database")
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "get_customer_history":
            customer_id = arguments.get("customer_id", "")
            if not customer_id:
                error_msg = "Missing 'customer_id' parameter"
                logger.warning(f"get_customer_history: {error_msg}")
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
            
            logger.info(f"Retrieving history for customer: {customer_id}")
            result = db.get_customer_history(customer_id)
            logger.info(f"✓ get_customer_history completed - found {len(result.get('analyses', []))} analyses")
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "get_high_risk_customers":
            threshold = float(arguments.get("threshold", 0.75))
            
            logger.info(f"Retrieving high-risk customers (threshold: {threshold})")
            result = db.get_high_risk_customers(threshold)
            logger.info(f"✓ get_high_risk_customers completed - found {len(result)} at-risk customers")
            
            return [TextContent(type="text", text=json.dumps({
                'high_risk_customers': result,
                'count': len(result),
                'threshold': threshold
            }))]
        
        elif name == "get_database_statistics":
            logger.info("Retrieving database statistics")
            result = db.get_statistics()
            logger.info(f"✓ get_database_statistics completed")
            
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "save_analysis":
            """Save analysis results explicitly with customer identifier"""
            customer_id = arguments.get("customer_id", "")
            if not customer_id:
                error_msg = "Missing 'customer_id' parameter"
                logger.warning(f"save_analysis: {error_msg}")
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
            
            messages = arguments.get("messages", [])
            if not messages or not isinstance(messages, list):
                error_msg = "Missing or invalid 'messages' parameter (must be non-empty array)"
                logger.warning(f"save_analysis: {error_msg}")
                return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
            
            # Build analysis dictionary from parameters
            analysis = {
                "current_sentiment": arguments.get("sentiment_score", 50),
                "trend": arguments.get("trend", "STABLE"),
                "risk_level": arguments.get("risk_level", "MEDIUM"),
                "predicted_action": arguments.get("predicted_action", "UNKNOWN"),
                "confidence": arguments.get("confidence", 0.5)
            }
            
            context_type = arguments.get("context_type", "customer")
            if context_type not in ["customer", "employee", "email"]:
                context_type = "customer"
            
            logger.info(f"Saving analysis for customer: {customer_id}")
            logger.debug(f"Analysis data: {analysis}")
            
            # Save to database
            analysis_id = db.save_analysis(customer_id, context_type, messages, analysis)
            
            logger.info(f"✓ Analysis saved successfully - ID: {analysis_id}, Customer: {customer_id}")
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "analysis_id": analysis_id,
                "customer_id": customer_id,
                "message": f"Analysis saved for {customer_id} with {len(messages)} messages"
            }))]
        
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
    
    except Exception as e:
        error_msg = f"Error in tool {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        sys.stderr.write(f"ERROR: {error_msg}\n")
        return [TextContent(type="text", text=json.dumps({"error": error_msg}))]


# ============================================================================
# MAIN SERVER LOOP
# ============================================================================

async def main():
    """
    Run the MCP server with stdio transport.
    This is the CRITICAL function that handles protocol communication.
    
    IMPORTANT: stdio_server() yields a tuple (read_stream, write_stream)
    """
    logger.info("main() called - entering async loop")
    
    try:
        # Use stdio_server context manager for proper protocol handling
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✓ stdio_server initialized - streams ready")
            logger.info("✓ Creating InitializationOptions...")
            
            # Create initialization options required by MCP protocol
            init_options = InitializationOptions(
                server_name="sentiment-evolution-tracker",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
            
            logger.info("✓ Connecting to Claude Desktop...")
            logger.info(f"✓ Server capabilities: {init_options.capabilities}")
            
            # Start the server with stdin/stdout streams and initialization options
            # This blocks until connection is closed
            await server.run(read_stream, write_stream, init_options)
            
            logger.info("✓ Server loop completed (connection closed)")
    
    except Exception as e:
        error_msg = f"Server error in main(): {str(e)}"
        logger.error(error_msg, exc_info=True)
        sys.stderr.write(f"FATAL ERROR: {error_msg}\n")
        raise


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("MCP Server Process Starting")
    logger.info("=" * 80)
    
    try:
        # Windows compatibility: set event loop policy
        if sys.platform == "win32":
            logger.info("Windows detected - setting WindowsSelectorEventLoopPolicy")
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Run the server
        logger.info("Calling asyncio.run(main())")
        asyncio.run(main())
        logger.info("MCP Server exited normally")
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user (KeyboardInterrupt)")
        sys.exit(0)
    
    except Exception as e:
        error_msg = f"FATAL ERROR in main process: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        sys.stderr.write(f"\n{error_msg}\n")
        sys.exit(1)
