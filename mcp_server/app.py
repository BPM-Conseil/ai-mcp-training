# English-only comments as requested
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any

try:
    import uvicorn
    from fastapi import FastAPI
    from pydantic import BaseModel
    from db import init_db, add_document, list_documents, delete_document, search_documents
    print("✓ MCP Server imports successful")
except Exception as e:
    print(f"✗ MCP Server import error: {e}")
    raise

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (if needed)

# FastAPI app with lifespan
app = FastAPI(title="Document MCP Server", lifespan=lifespan)

# Pydantic models for HTTP API
class AddDocumentRequest(BaseModel):
    filename: str
    content: str
    mime_type: str = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# HTTP API endpoints for backward compatibility
@app.get("/health")
async def health():
    return {"status": "ok", "service": "mcp-server"}

@app.get("/ping")
async def ping():
    return {"ping": "pong"}

@app.post("/add_document")
async def http_add_document(req: AddDocumentRequest):
    return await add_document(req.filename, req.content, req.mime_type)

@app.get("/list_documents")
async def http_list_documents():
    return await list_documents()

@app.delete("/delete_document/{doc_id}")
async def http_delete_document(doc_id: str):
    return await delete_document(doc_id)

@app.post("/search_documents")
async def http_search_documents(req: SearchRequest):
    return await search_documents(req.query, req.top_k)

# ---- Run FastAPI ----
if __name__ == "__main__":
    async def main():
        # Run FastAPI HTTP server on port 8765
        uvicorn_task = asyncio.create_task(
            uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
        )

        await asyncio.gather(mcp_task, uvicorn_task)

    asyncio.run(main())
