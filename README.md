
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


## Storage Backends

HomeFix supports two storage backends:

- **JSON:** Default for local development and testing.
- **Amazon DynamoDB:** Persistent cloud storage for repair records.

To use DynamoDB, create a table named `HomeFixRepairs` with `repair_id` as its String partition key.

Configure the environment:

```powershell
$env:HOMEFIX_STORAGE_BACKEND = "dynamodb"
$env:HOMEFIX_DYNAMODB_TABLE = "HomeFixRepairs"
$env:AWS_REGION = "eu-west-2"
```

AWS credentials and DynamoDB permissions must be configured separately. Never commit AWS credentials.

## Verification

Run the full automated test suite:

```bash
python -m pytest -q
```

Latest verified result: 26 tests passing.

The MCP server has been tested locally using Streamable HTTP, with all five tools successfully discovered.

Live DynamoDB integration has also been verified using synthetic repair records, including creation, retrieval, search, priority changes and repair updates.



## Current Limitations

HomeFix is a working MCP prototype with local JSON storage and tested AWS DynamoDB integration.

AWS AgentCore hosting and direct Alexa+ integration are not yet complete.

Property-level checks and confirmation safeguards are implemented, but tenant identity is not independently authenticated. The prototype must use synthetic demonstration data only and should not be exposed to real tenants until authentication and authorisation are completed.