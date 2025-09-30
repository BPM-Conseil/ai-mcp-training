FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastmcp

# Copy application code
COPY . /app

# Expose application ports
EXPOSE 8765
EXPOSE 8766

# Production command - runs both FastAPI app and MCP server
# CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8765 & fastmcp run mcp_server.py"]
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8765 & fastmcp run mcp_server.py --transport sse --port 8766 --host 0.0.0.0"]
