from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import tempfile
import json

from src.rag.generator import Generator
from src.ingestion.pipeline import ingest_directory
from src.vectorstore.store import VectorStore

router = APIRouter()
generator = Generator()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: AskRequest):
    def event_stream():
        for token in generator.ask_stream(request.question):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/ingest")
async def ingest_files(files: list[UploadFile] = File(...)):
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for file in files:
            file_path = tmp_path / file.filename
            content = await file.read()
            file_path.write_bytes(content)

        count = ingest_directory(tmp_path)

    return {"message": f"Ingested {count} chunks from {len(files)} file(s)"}


@router.get("/documents")
def list_documents():
    store = VectorStore()
    return {"documents": store.list_documents(), "total_chunks": store.count}


@router.delete("/documents")
def delete_all_documents():
    store = VectorStore()
    store.delete_collection()
    return {"message": "All documents deleted"}
