# English-only comments as requested
import os
import asyncio
import httpx
from typing import Any, Dict

MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://mcp-server:8765")

# Increase timeout for embedding operations
TIMEOUT = httpx.Timeout(60.0, connect=10.0)

async def _retry_request(func, max_retries=3, delay=2):
    """Retry HTTP requests with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if attempt == max_retries - 1:
                raise httpx.ConnectError(f"Failed to connect to MCP server after {max_retries} attempts: {str(e)}")
            await asyncio.sleep(delay * (2 ** attempt))
        except Exception as e:
            raise e


async def add_document(filename: str, content: str, mime_type: str | None) -> Dict[str, Any]:
    async def _request():
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{MCP_BASE_URL}/add_document",
                json={"filename": filename, "content": content, "mime_type": mime_type}
            )
            response.raise_for_status()
            return response.json()
    return await _retry_request(_request)


async def list_documents() -> Dict[str, Any]:
    async def _request():
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{MCP_BASE_URL}/list_documents")
            response.raise_for_status()
            return response.json()
    return await _retry_request(_request)


async def delete_document(doc_id: str) -> Dict[str, Any]:
    async def _request():
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.delete(f"{MCP_BASE_URL}/delete_document/{doc_id}")
            response.raise_for_status()
            return response.json()
    return await _retry_request(_request)


async def search_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    async def _request():
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{MCP_BASE_URL}/search_documents",
                json={"query": query, "top_k": top_k}
            )
            response.raise_for_status()
            return response.json()
    return await _retry_request(_request)
