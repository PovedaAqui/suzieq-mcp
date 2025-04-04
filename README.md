# MCP Server for SuzieQ

This project provides a Model Context Protocol (MCP) server that allows language models and other MCP clients to interact with a SuzieQ network observability instance via its REST API.

## Overview

The server exposes SuzieQ's commands as MCP tools:
- `run_suzieq_show`: Access the 'show' command to query detailed network state tables
- `run_suzieq_summarize`: Access the 'summarize' command to get aggregated statistics and summaries

These tools enable clients (like Claude Desktop) to query various network state tables (e.g., interfaces, BGP, routes) and apply filters, retrieving the results directly from your SuzieQ instance.

## Prerequisites

* **Python:** Version 3.8 or higher is recommended.
* **uv:** A fast Python package installer and resolver. ([Installation guide](https://docs.astral.sh/uv/install/))
* **SuzieQ Instance:** A running SuzieQ instance with its REST API enabled and accessible.
* **SuzieQ API Endpoint & Key:** You need the URL for the SuzieQ API (e.g., `http://your-suzieq-host:8000/api/v2`) and a valid API key (`access_token`).

## Installation & Setup

1. **Get the Code:** Clone this repository or download the `main.py` and `server.py` files into a dedicated project directory.

2. **Create Virtual Environment:** Navigate to your project directory in the terminal and create a virtual environment using `uv`:
   ```bash
   uv venv
   ```

3. **Activate Environment:**
   * On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   * On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   *(You should see `(.venv)` preceding your prompt)*

4. **Install Dependencies:** Install the required Python packages using `uv`:
   ```bash
   uv pip install mcp httpx python-dotenv
   ```
   * `mcp`: The Model Context Protocol SDK.
   * `httpx`: An asynchronous HTTP client used to communicate with the SuzieQ API.
   * `python-dotenv`: Used to load environment variables from a `.env` file for configuration.

## Configuration

The server needs your SuzieQ API endpoint and API key. Use a `.env` file for secure and easy configuration:

1. **Create `.env` file:** In the **root of your project directory** (the same place as `main.py`), create a file named `.env`.

2. **Add Credentials:** Add your SuzieQ endpoint and key to the `.env` file. **Ensure there are no quotes around the values unless they are part of the key/endpoint itself.**
   ```dotenv
   # .env
   SUZIEQ_API_ENDPOINT=http://your-suzieq-host:8000/api/v2
   SUZIEQ_API_KEY=your_actual_api_key
   ```
   *Replace the placeholder values with your actual endpoint and key.*

3. **Secure `.env` file:** Add `.env` to your `.gitignore` file to prevent accidentally committing secrets.
   ```bash
   echo ".env" >> .gitignore
   ```

4. **Code Integration:** The provided `server.py` automatically uses `python-dotenv` to load these variables when the server starts.

## Running the Server

Make sure your virtual environment is activated. The server will load configuration from the `.env` file in the current directory.

### 1. Directly

Run the server directly from your terminal:

```bash
uv run python main.py
```

The server will start, print `Starting SuzieQ MCP Server...`, and listen for MCP connections on standard input/output (stdio). You should see `[INFO]` logs if it successfully queries the API via the tool. Press `Ctrl+C` to stop it.

### 2. With MCP Inspector (for Debugging)

The MCP Inspector is useful for testing the tool directly. If you have the mcp CLI tools installed (via `uv pip install "mcp[cli]"`), run:

```bash
uv run mcp dev main.py
```

This launches an interactive debugger. Go to the "Tools" tab, select `run_suzieq_show`, enter parameters (e.g., table: "device"), and click "Call Tool" to test.

## Using with Claude Desktop

Integrate the server with Claude Desktop for seamless use:

1. **Find Claude Desktop Config:** Locate the `claude_desktop_config.json` file.
   * macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   * Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   * Create the file and the Claude directory if they don't exist.

2. **Edit Config File:** Add an entry for this server. Use the absolute path to `main.py`. The server loads secrets from `.env`, so they don't need to be in this config.

```json
{
  "mcpServers": {
    "suzieq-server": {
      // Use 'uv' if it's in the system PATH Claude uses,
      // otherwise provide the full path to the uv executable.
      "command": "uv",
      "args": [
        "run",
        "python",
        // --- VERY IMPORTANT: Use the ABSOLUTE path below ---
        "/full/path/to/your/project/mcp-suzieq-server/main.py"
      ],
      // 'env' block is not needed here if .env is in the project directory above
      "workingDirectory": "/full/path/to/your/project/mcp-suzieq-server/" // Optional, but recommended
    }
    // Add other servers here if needed
  }
}
```

* Replace `/full/path/to/your/project/mcp-suzieq-server/main.py` with the correct absolute path on your system.
* Replace `/full/path/to/your/project/mcp-suzieq-server/` with the absolute path to the directory containing `main.py` and `.env`. Setting `workingDirectory` helps ensure the `.env` file is found.
* If `uv` isn't found by Claude, replace `"uv"` with its absolute path (find via `which uv` or `where uv`).
* On Windows, you might need `"env": { "PYTHONUTF8": "1" }` if you encounter text encoding issues.

3. **Restart Claude Desktop:** Completely close and reopen Claude Desktop.

4. **Verify:** Look for the MCP tool indicator (hammer icon 🔨) in Claude Desktop. Clicking it should show both the `run_suzieq_show` and `run_suzieq_summarize` tools.

## Tool Usage (run_suzieq_show)

```
run_suzieq_show(table: str, filters: Optional[Dict[str, Any]] = None) -> str
```

* **table**: (String, Required) The SuzieQ table name (e.g., "device", "interface", "bgp").
* **filters**: (Dictionary, Optional) Key-value pairs for filtering (e.g., `"hostname": "leaf01"`). Omit or use `{}` for no filters.
* **Returns**: A JSON string with the results or an error.

### Example Invocations (Conceptual):

Show all devices:
```json
{ "table": "device" }
```

Show BGP neighbors for hostname 'spine01':
```json
{ "table": "bgp", "filters": { "hostname": "spine01" } }
```

Show 'up' interfaces in VRF 'default':
```json
{ "table": "interface", "filters": { "vrf": "default", "state": "up" } }
```

## Tool Usage (run_suzieq_summarize)

```
run_suzieq_summarize(table: str, filters: Optional[Dict[str, Any]] = None) -> str
```

* **table**: (String, Required) The SuzieQ table name to summarize (e.g., "device", "interface", "bgp").
* **filters**: (Dictionary, Optional) Key-value pairs for filtering (e.g., `"hostname": "leaf01"`). Omit or use `{}` for no filters.
* **Returns**: A JSON string with the summarized results or an error.

### Example Invocations (Conceptual):

Summarize all devices:
```json
{ "table": "device" }
```

Summarize BGP sessions by hostname 'spine01':
```json
{ "table": "bgp", "filters": { "hostname": "spine01" } }
```

Summarize interface states in VRF 'default':
```json
{ "table": "interface", "filters": { "vrf": "default" } }
```

## Troubleshooting

### Error: "SuzieQ API endpoint or key not configured...":
* Ensure the `.env` file is in the same directory as `main.py`.
* Verify `SUZIEQ_API_ENDPOINT` and `SUZIEQ_API_KEY` are correctly spelled and have valid values in `.env`.
* If using Claude Desktop, ensure the `workingDirectory` in `claude_desktop_config.json` points to the directory containing `.env`.

### HTTP Errors (4xx, 5xx):
* Check the SuzieQ API key (`SUZIEQ_API_KEY`) is correct (401/403 errors).
* Verify the `SUZIEQ_API_ENDPOINT` is correct and the API server is running.