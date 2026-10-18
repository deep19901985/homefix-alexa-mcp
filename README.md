
# HomeFix — Alexa+ MCP Repair Assistant

HomeFix is an AI-powered repair reporting assistant designed for tenants, built for the Amazon Developer Hackathon 2026.

## Problem

Tenants often need to contact property managers to report repairs, check their progress, or provide updates. Duplicate reports and incomplete information can make the process inefficient.

## Solution

HomeFix enables an AI assistant to interact with a repair management backend through the Model Context Protocol (MCP).

The assistant can:

- Search existing repair reports
- Detect potential duplicate issues
- Retrieve repair status
- Create new repair reports after confirmation
- Change repair priorities after confirmation
- Add updates to existing repairs

## Technology Stack

- Python 3.11
- Pydantic for data models
- MCP Python SDK
- FastMCP with Streamable HTTP
- JSON-based prototype storage
- Pytest for automated testing

## Development Status

- Five MCP tools implemented
- 15 automated tests passing
- MCP protocol 2025-11-25 supported
- Local Streamable HTTP connectivity verified

**Security note:** Property-level filtering is implemented, but authenticated tenant identity and production-grade authorisation are not yet available. Use synthetic demonstration data only.


## Installation

### 1. Clone the repository

```bash
git clone https://github.com/deep19901985/homefix-alexa-mcp.git
cd homefix-alexa-mcp
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
```

## Running the MCP Server

Start the server:

```bash
python -m mcp_server.server
```

The Streamable HTTP server runs locally at:

`http://127.0.0.1:8000/mcp`

Keep the server running while testing.

## Testing

Run the automated unit tests:

```bash
python -m pytest tests/test_database.py tests/test_safeguards.py tests/test_validation.py tests/test_security.py -v
```

Run the MCP connectivity check in a second terminal:

```bash
python check_mcp_connection.py
```

The connectivity check discovers all five HomeFix MCP tools.

## Current Limitations

HomeFix currently runs as a local prototype with JSON storage and synthetic repair data.

Alexa+ integration, publicly accessible HTTPS hosting, and trusted tenant authentication remain future development tasks.
