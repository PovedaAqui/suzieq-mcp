# server.py
# Implements the MCP server logic and SuzieQ tools.

import httpx  # Using httpx for asynchronous HTTP requests
import os
import json
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv # Import dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# --- Configuration ---
# Get SuzieQ API endpoint and key from environment variables
SUZIEQ_API_ENDPOINT = os.getenv("SUZIEQ_API_ENDPOINT", None) # Default to None if not set
SUZIEQ_API_KEY = os.getenv("SUZIEQ_API_KEY", None) # Default to None if not set

# --- MCP Server Setup ---
# Initialize FastMCP server with a name
mcp = FastMCP("SuzieQ MCP Server")

# --- SuzieQ API Interaction Helper (Generalized) ---
async def _query_suzieq_api(verb: str, table: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Asynchronously queries the SuzieQ REST API for a given verb and table.

    Args:
        verb: The SuzieQ verb to execute (e.g., 'show', 'summarize').
        table: The SuzieQ table name (e.g., 'device', 'bgp', 'interface').
        params: A dictionary of query parameters for filtering (e.g., {'hostname': 'leaf01', 'vrf': 'default'}).

    Returns:
        A dictionary containing the API response or an error message.
    """
    # Check if configuration is missing
    if not SUZIEQ_API_ENDPOINT or not SUZIEQ_API_KEY:
        error_msg = "SuzieQ API endpoint or key not configured. Set SUZIEQ_API_ENDPOINT and SUZIEQ_API_KEY environment variables or in .env file."
        print(f"[ERROR] {error_msg}") # Log configuration error
        return {"error": error_msg}

    # Construct the API URL using the provided verb and table
    api_endpoint_clean = SUZIEQ_API_ENDPOINT.rstrip('/')
    # Assuming the API structure follows /{table}/{verb} pattern
    api_url = f"{api_endpoint_clean}/{table}/{verb}"

    # --- Authentication ---
    # Prepare parameters, adding the API key as 'access_token' query parameter
    query_params = params if params else {}
    query_params["access_token"] = SUZIEQ_API_KEY # Add key as query param
    query_params["format"] = "json" # Ensure response is JSON
    headers = {} # No custom headers needed now for auth
    # ---------------------------

    async with httpx.AsyncClient() as client:
        try:
            # Use headers={}, params=query_params
            print(f"[INFO] Querying SuzieQ API: {api_url} with params: {query_params}") # Debug print
            response = await client.get(api_url, headers=headers, params=query_params, timeout=30.0)
            print(f"[INFO] SuzieQ API Response Status: {response.status_code}") # Debug print
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            if response.status_code == 204:
                return {"warning": f"Received empty response (204 No Content) from SuzieQ API for {verb} {table}"}

            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                return response.json()
            else:
                error_detail = f"Unexpected content type received: {content_type}. Response text: {response.text}"
                print(f"[ERROR] {error_detail}")
                return {"error": error_detail}
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            print(f"[ERROR] {error_detail}") # Debug print
            return {"error": error_detail}
        except httpx.RequestError as e:
            error_detail = f"An error occurred while requesting {e.request.url!r}: {e}"
            print(f"[ERROR] {error_detail}") # Debug print
            return {"error": error_detail}
        except json.JSONDecodeError as e:
            error_detail = f"Failed to decode JSON response from SuzieQ API: {e}. Response text: {response.text}"
            print(f"[ERROR] {error_detail}")
            return {"error": error_detail}
        except Exception as e:
            error_detail = f"An unexpected error occurred: {str(e)}"
            print(f"[ERROR] {error_detail}") # Debug print
            return {"error": error_detail}

# --- MCP Tool Definitions ---
@mcp.tool()
async def run_suzieq_show(table: str, filters: Optional[Dict[str, Any]] = None) -> str:
    """
    Runs a SuzieQ 'show' query via its REST API.

    Args:
        table: The name of the SuzieQ table to query (e.g., 'device', 'bgp', 'interface', 'route').
        filters: An optional dictionary of filter parameters for the SuzieQ query
                 (e.g., {"hostname": "leaf01", "vrf": "default", "state": "Established"}).
                 Keys should match SuzieQ filter names. Values can be strings or lists of strings.
                 If no filters are needed, this can be None, null, or an empty dictionary.

    Returns:
        A JSON string representing the result from the SuzieQ API, or a JSON string with an error message.
    """
    actual_filters = filters if isinstance(filters, dict) else None

    # Call the generalized helper function with verb='show'
    result = await _query_suzieq_api(verb="show", table=table, params=actual_filters)

    try:
        # Serialize the result dictionary to a JSON string
        return json.dumps(result, indent=2, ensure_ascii=False)
    except TypeError as e:
        error_message = f"Error serializing SuzieQ 'show' response to JSON: {str(e)}"
        print(f"[ERROR] {error_message}") # Debug print
        return json.dumps({"error": error_message})

@mcp.tool()
async def run_suzieq_summarize(table: str, filters: Optional[Dict[str, Any]] = None) -> str:
    """
    Runs a SuzieQ 'summarize' query via its REST API.

    Args:
        table: The name of the SuzieQ table to summarize (e.g., 'device', 'bgp', 'interface', 'route').
        filters: An optional dictionary of filter parameters for the SuzieQ query
                 (e.g., {"hostname": "leaf01", "vrf": "default"}).
                 Keys should match SuzieQ filter names. Values can be strings or lists of strings.
                 If no filters are needed, this can be None, null, or an empty dictionary.

    Returns:
        A JSON string representing the summarized result from the SuzieQ API,
        or a JSON string with an error message.
    """
    actual_filters = filters if isinstance(filters, dict) else None

    # Call the generalized helper function with verb='summarize'
    result = await _query_suzieq_api(verb="summarize", table=table, params=actual_filters)

    try:
        # Serialize the result dictionary to a JSON string
        return json.dumps(result, indent=2, ensure_ascii=False)
    except TypeError as e:
        error_message = f"Error serializing SuzieQ 'summarize' response to JSON: {str(e)}"
        print(f"[ERROR] {error_message}") # Debug print
        return json.dumps({"error": error_message})

# --- Main Execution (Example) ---
# You would typically run this server using an ASGI server like uvicorn:
# uvicorn server:mcp --reload
# Or integrate it into a larger application framework.