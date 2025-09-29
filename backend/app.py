# English-only comments as requested
import os
import io
from typing import List, Dict, Any

try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    from openai import OpenAI
    import PyPDF2
    
    from mcp_client import add_document as mcp_add, list_documents as mcp_list, delete_document as mcp_delete, search_documents as mcp_search
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    raise

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


@app.get("/")
async def root():
    return FileResponse("static/chat.html")


@app.get("/admin")
async def admin():
    return FileResponse("static/admin.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


# Admin endpoints
def extract_text_from_pdf(content_bytes: bytes) -> str:
    """Extract text from PDF bytes"""
    try:
        pdf_file = io.BytesIO(content_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

@app.post("/admin/upload")
async def admin_upload(file: UploadFile = File(...)):
    try:
        content_bytes = await file.read()
        content = ""
        
        # Handle different file types
        if file.content_type == "application/pdf" or file.filename.lower().endswith('.pdf'):
            content = extract_text_from_pdf(content_bytes)
        else:
            # Try to decode as text
            try:
                content = content_bytes.decode("utf-8", errors="ignore")
            except Exception:
                content = ""
        
        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="Empty or unsupported file content")
        
        # Add document with better error handling
        res = await mcp_add(filename=file.filename, content=content, mime_type=file.content_type)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/admin/documents")
async def admin_documents():
    res = await mcp_list()
    return res


@app.delete("/admin/documents/{doc_id}")
async def admin_delete(doc_id: str):
    res = await mcp_delete(doc_id)
    return res


class ChatRequest(BaseModel):
    message: str
    top_k: int = 5


@app.post("/chat")
async def chat(req: ChatRequest):
    # search context
    search = await mcp_search(req.message, req.top_k)
    matches = search.get("matches", [])

    # build system prompt with sources
    sources_text = "\n\n".join([f"[Source {i+1}: {m['filename']}]\n{m['chunk_text']}" for i, m in enumerate(matches)])
    system_prompt = (
        "You are a helpful assistant. Use the provided sources to answer the user's question. "
        "Cite sources as [Source N] when relevant. If unsure, say you don't know.\n\n"
        f"Sources:\n{sources_text if sources_text else 'No sources available.'}"
    )

    if not client:
        # if no LLM key, return a mock response with sources
        return {"answer": "LLM not configured. Here are matching sources only.", "sources": matches}

    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.message},
        ],
        temperature=0.2,
    )
    answer = completion.choices[0].message.content
    return {"answer": answer, "sources": matches}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
