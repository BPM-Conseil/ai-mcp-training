# Dockerized Chatbot with MCP-like Server and Admin UI

This project provides:

- **Backend** (`backend/`): FastAPI server exposing Admin endpoints (upload/list/delete) and a Chat endpoint. Serves static UIs for Admin and Chat.
- **MCP Server** (`mcp_server/`): WebSocket JSON-RPC server exposing tools: `add_document`, `list_documents`, `delete_document`, `search_documents`. Stores data in Postgres with `pgvector` and uses OpenAI embeddings.
- **Database**: Postgres with `pgvector` extension.

The system is orchestrated with Docker Compose.

## Services

- **db**: Postgres with pgvector.
- **mcp-server**: FastAPI WebSocket at `ws://localhost:8765/ws`.
- **backend**: FastAPI HTTP at `http://localhost:8000` serving Admin and Chat UIs.

## Quick Start

1. Create a `.env` file from `.env.example` and set your variables (OpenAI keys, etc.).
2. Build and run:

```bash
docker compose up --build
```

3. Open:
- Admin UI: http://localhost:8000/admin
- Chat UI: http://localhost:8000/

## Environment Variables

- `POSTGRES_USER` (default `mcp`)
- `POSTGRES_PASSWORD` (default `mcppassword`)
- `POSTGRES_DB` (default `mcpdb`)
- `EMBEDDING_MODEL_NAME` (default `text-embedding-3-small`)
- `OPENAI_API_KEY` (required for embeddings in MCP server, optional for backend chat)
- `OPENAI_MODEL` (default `gpt-4o-mini`)
- `MCP_WS_URL` (backend to MCP WS, default `ws://mcp-server:8765` inside compose)

## How It Works

- Admin uploads a file to `POST /admin/upload`.
- Backend reads content and calls MCP `add_document` over WS.
- MCP chunks and embeds, storing in Postgres+pgvector.
- Chat calls MCP `search_documents` and optionally calls OpenAI to produce an answer augmented with sources.

## Notes

- Only UTF-8 text content is processed. For PDF/DOCX, add a converter or a text extraction step.
- If `OPENAI_API_KEY` is not provided:
  - MCP server cannot embed text; add your key or replace embeddings with local models.
  - Backend chat will return a mock response with sources only.

## Development

- Health checks: `GET /health` (backend) and `GET /health` (mcp-server).
- Update chunking, dimensions, and model per your needs.

## Future Improvements

- Authentication for Admin routes.
- PDF/DOCX extraction.
- Streaming responses in chat.
- Persistent object storage for original files.


## Connect to database

```bash
psql -h localhost -p 5432 -U mcp -d mcpdb
```