# MCP Server with Document Search Tools
from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio

# Import database functions
from db import search_documents, list_documents, add_document, delete_document

mcp = FastMCP("Document Search MCP Server")

@mcp.tool
def search_in_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search for information in the document database using semantic similarity.
    
    Args:
        query: The search query to find relevant information
        top_k: Maximum number of results to return (default: 5)
    
    Returns:
        Dictionary with 'matches' containing relevant document chunks with scores
    """
    # Run async function in sync context
    return asyncio.run(search_documents(query, top_k))


@mcp.tool
def get_all_documents() -> List[Dict[str, Any]]:
    """
    List all documents in the database.
    
    Returns:
        List of documents with their metadata (id, filename, mime_type, created_at)
    """
    return asyncio.run(list_documents())

if __name__ == "__main__":
    mcp.run()