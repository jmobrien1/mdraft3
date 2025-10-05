from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from config import get_settings
from document_parser import DocumentParser
from requirement_extractor import RequirementExtractor
import uuid
from datetime import datetime

app = FastAPI(title="RFP Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

parser = DocumentParser()
extractor = RequirementExtractor()

@app.get("/")
def read_root():
    return {"message": "RFP Extractor API", "version": "2.0"}

@app.get("/documents")
async def list_documents():
    try:
        response = supabase.table("documents").select("*").order("uploaded_at", desc=True).execute()
        return {"documents": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()

        doc_id = str(uuid.uuid4())

        text = parser.parse(content, file.content_type)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found in document")

        storage_path = f"{doc_id}/{file.filename}"
        supabase.storage.from_("documents").upload(storage_path, content)

        doc_data = {
            "id": doc_id,
            "filename": file.filename,
            "original_filename": file.filename,
            "file_path": storage_path,
            "file_size": len(content),
            "file_type": file.filename.split('.')[-1],
            "mime_type": file.content_type,
            "status": "processing",
            "uploaded_by": "anonymous",
            "uploaded_at": datetime.utcnow().isoformat()
        }

        supabase.table("documents").insert(doc_data).execute()

        requirements = extractor.extract(text, doc_id)

        if requirements:
            for req in requirements:
                req_with_chunk = {
                    **req,
                    "source_chunk_id": doc_id,
                    "source_page": 1,
                    "source_paragraph": 0
                }
                supabase.table("requirements").insert(req_with_chunk).execute()

        supabase.table("documents").update({
            "status": "completed",
            "processed_at": datetime.utcnow().isoformat()
        }).eq("id", doc_id).execute()

        return {
            "document_id": doc_id,
            "filename": file.filename,
            "requirements_extracted": len(requirements)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    try:
        doc = supabase.table("documents").select("*").eq("id", document_id).single().execute()

        reqs = supabase.table("requirements").select("*").eq("document_id", document_id).order("source_subsection").execute()

        return {
            "document": doc.data,
            "requirements": reqs.data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

@app.get("/documents/{document_id}/stats")
async def get_document_stats(document_id: str):
    try:
        reqs = supabase.table("requirements").select("classification, status").eq("document_id", document_id).execute()

        total = len(reqs.data)
        performance = sum(1 for r in reqs.data if r.get("classification") == "PERFORMANCE_REQUIREMENT")
        compliance = sum(1 for r in reqs.data if r.get("classification") == "COMPLIANCE_REQUIREMENT")
        deliverable = sum(1 for r in reqs.data if r.get("classification") == "DELIVERABLE_REQUIREMENT")
        validated = sum(1 for r in reqs.data if r.get("status") == "human_validated")

        return {
            "total": total,
            "performance": performance,
            "compliance": compliance,
            "deliverable": deliverable,
            "validated": validated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/requirements/{requirement_id}")
async def update_requirement(requirement_id: str, status: str, validated_by: str = None):
    try:
        update_data = {
            "status": status,
            "validated_at": datetime.utcnow().isoformat()
        }
        if validated_by:
            update_data["validated_by"] = validated_by

        supabase.table("requirements").update(update_data).eq("id", requirement_id).execute()

        return {"message": "Requirement updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
