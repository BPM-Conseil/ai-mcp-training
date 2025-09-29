# English-only comments as requested
import os
import uuid
import json
from typing import List, Dict, Any

import psycopg
from psycopg.rows import dict_row
import requests

DB_URL = os.getenv("DATABASE_URL")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBED_DIM = 1536  # for text-embedding-3-small


async def init_db():
    # psycopg (v3) sync client; simple blocking operations during startup
    print("Initializing database...")
    try:
        with psycopg.connect(DB_URL, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Enable pgvector extension
                print("Creating pgvector extension...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # Verify extension is loaded
                cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
                result = cur.fetchone()
                if result:
                    print("✓ pgvector extension is active")
                else:
                    raise RuntimeError("Failed to create pgvector extension")
                
                # Create documents table
                print("Creating documents table...")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS documents (
                      id UUID PRIMARY KEY,
                      filename TEXT NOT NULL,
                      mime_type TEXT,
                      content TEXT,
                      created_at TIMESTAMP DEFAULT NOW()
                    );
                    """
                )
                
                # Create doc_chunks table with vector column
                print(f"Creating doc_chunks table with vector dimension {EMBED_DIM}...")
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS doc_chunks (
                      id UUID PRIMARY KEY,
                      doc_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                      chunk_index INT NOT NULL,
                      chunk_text TEXT NOT NULL,
                      embedding VECTOR({EMBED_DIM})
                    );
                    """
                )
                
                # Create indexes
                print("Creating indexes...")
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_doc_chunks_doc_id ON doc_chunks(doc_id);
                    """
                )
                
                # Create vector index (only if table has data)
                cur.execute("SELECT COUNT(*) FROM doc_chunks;")
                count = cur.fetchone()[0]
                if count > 0:
                    print("Creating vector similarity index...")
                    cur.execute(
                        """
                        CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding 
                        ON doc_chunks USING ivfflat (embedding vector_cosine_ops);
                        """
                    )
                else:
                    print("Skipping vector index creation (no data yet)")
                
                print("✓ Database initialization complete")
                
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise

def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks by words.
    - chunk_size and overlap are approx. character lengths, not exact.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0

    for word in words:
        wlen = len(word) + 1  # +1 for the space
        # If adding this word exceeds chunk_size → close current chunk
        if current_len + wlen > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            # Start new chunk with overlap
            overlap_words = current_chunk[-(overlap // 5):] if overlap > 0 else []
            current_chunk = overlap_words + [word]
            current_len = sum(len(w) + 1 for w in current_chunk)
        else:
            current_chunk.append(word)
            current_len += wlen

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return [c.strip() for c in chunks if c.strip()]

def _embed_texts(texts: List[str]) -> List[List[float]]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for embeddings in MCP server")
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": EMBED_MODEL,
        "input": texts
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=payload,
            timeout=30  # 30 second timeout
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"OpenAI API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return [d["embedding"] for d in data["data"]]
    except requests.exceptions.Timeout:
        raise RuntimeError("OpenAI API request timed out")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OpenAI API request failed: {str(e)}")


async def add_document(filename: str, content: str, mime_type: str | None = None) -> Dict[str, Any]:
    if not filename or content is None:
        raise ValueError("filename and content are required")
    doc_id = uuid.uuid4()
    chunks = _chunk_text(content)
    embeddings = _embed_texts(chunks) if chunks else []

    with psycopg.connect(DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (id, filename, mime_type, content) VALUES (%s, %s, %s, %s)",
                (doc_id, filename, mime_type, content),
            )
            for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                # Convert embedding to string format for pgvector
                emb_str = "[" + ",".join(map(str, emb)) + "]"
                cur.execute(
                    "INSERT INTO doc_chunks (id, doc_id, chunk_index, chunk_text, embedding) VALUES (%s, %s, %s, %s, %s)",
                    (uuid.uuid4(), doc_id, idx, chunk, emb_str),
                )
    return {"id": str(doc_id), "chunks": len(chunks)}


async def list_documents() -> List[Dict[str, Any]]:
    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, filename, mime_type, created_at FROM documents ORDER BY created_at DESC")
            rows = cur.fetchall()
            for r in rows:
                r["id"] = str(r["id"])  # ensure JSON serializable
            return rows


async def delete_document(doc_id: str) -> Dict[str, Any]:
    with psycopg.connect(DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
    return {"deleted": doc_id}


async def search_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    if not query:
        return {"matches": []}
    
    try:
        q_emb = _embed_texts([query])[0]
        
        # Convert embedding to proper format for pgvector
        emb_str = "[" + ",".join(map(str, q_emb)) + "]"
        print(f"Searching with embedding format: {emb_str[:50]}...")

        with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # First, verify pgvector extension is available
                cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
                if not cur.fetchone():
                    raise RuntimeError("pgvector extension not found")
                
                # Check if we have any data
                cur.execute("SELECT COUNT(*) FROM doc_chunks;")
                count = cur.fetchone()[0]
                if count == 0:
                    print("No document chunks found in database")
                    return {"matches": []}
                
                print(f"Searching {count} document chunks...")
                cur.execute(
                    """
                    SELECT d.id as doc_id, d.filename, c.chunk_index, c.chunk_text,
                           1 - (c.embedding <=> %s::vector) AS score
                    FROM doc_chunks c
                    JOIN documents d ON d.id = c.doc_id
                    ORDER BY c.embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (emb_str, emb_str, top_k),
                )
                rows = cur.fetchall()
                print(f"Found {len(rows)} matching chunks")
                for r in rows:
                    r["doc_id"] = str(r["doc_id"])  # JSON serializable
                return {"matches": rows}
                
    except Exception as e:
        print(f"Search error: {e}")
        # Return empty results instead of crashing
        return {"matches": [], "error": str(e)}
