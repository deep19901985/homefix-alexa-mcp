
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY mcp_server/ ./mcp_server/
COPY data/ ./data/

ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "mcp_server.server"]
