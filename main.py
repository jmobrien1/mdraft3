"""
FastAPI Backend for RFP Extraction and Analysis Platform.

This is the main application server that provides RESTful API endpoints
for document upload, processing, validation, and analysis of government RFPs.
"""

import os
import uuid
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Depends,
    HTTPException,
    BackgroundTasks,
    Query,
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

# Local imports
from database import get_db, init_database, health_check as db_health_check, db_manager
from models import (
    Document,
    Requirement,
    TextChunk,
    ProcessingJob,
    CrossReference,
    ProcessingStatus,
    ValidationStatus,
    RequirementClassification
)
from schemas import (
    DocumentResponse,
    RequirementResponse,
    RequirementUpdate,
    ReviewQueueResponse,
    ReviewQueueItem,
    ValidationRequest,
    SearchRequest,
    SearchResponse,
    SearchResult,
    FileUploadResponse,
    SystemStats,
    DocumentStats,
    HealthCheckResponse,
    ErrorResponse,
    ComplianceMatrixResponse,
    ComplianceMatrixItem
)
from document_processor import process_document_async

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="RFP Extraction Platform API",
    description="AI-powered platform for extracting and analyzing U.S. Government RFPs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting RFP Extraction Platform API")
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down RFP Extraction Platform API")


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="Health check"
)
async def health_check() -> HealthCheckResponse:
    """
    Check system health status including database connectivity.
    """
    health_status = db_health_check()

    return HealthCheckResponse(
        status="healthy" if health_status["database_connection"] else "unhealthy",
        database_connection=health_status["database_connection"],
        tables_exist=health_status["tables_exist"],
        pgvector_available=health_status["pgvector_available"],
        error=health_status.get("error")
    )


# Statistics endpoints
@app.get(
    "/stats",
    response_model=SystemStats,
    tags=["System"],
    summary="Get system statistics"
)
async def get_system_stats(db: Session = Depends(get_db)) -> SystemStats:
    """
    Get overall system statistics including document counts and processing metrics.
    """
    try:
        # Count totals
        total_documents = db.query(func.count(Document.id)).scalar()
        total_requirements = db.query(func.count(Requirement.id)).scalar()
        total_chunks = db.query(func.count(TextChunk.id)).scalar()

        # Documents by status
        docs_by_status = {}
        status_counts = db.query(
            Document.status,
            func.count(Document.id)
        ).group_by(Document.status).all()
        for status_val, count in status_counts:
            docs_by_status[status_val] = count

        # Requirements by classification
        reqs_by_classification = {}
        classification_counts = db.query(
            Requirement.classification,
            func.count(Requirement.id)
        ).group_by(Requirement.classification).all()
        for classification, count in classification_counts:
            reqs_by_classification[classification] = count

        # Validation status counts
        validation_counts = {}
        val_status_counts = db.query(
            Requirement.status,
            func.count(Requirement.id)
        ).group_by(Requirement.status).all()
        for val_status, count in val_status_counts:
            validation_counts[val_status] = count

        # Get health status
        system_health = db_health_check()

        return SystemStats(
            total_documents=total_documents or 0,
            total_requirements=total_requirements or 0,
            total_chunks=total_chunks or 0,
            documents_by_status=docs_by_status,
            requirements_by_classification=reqs_by_classification,
            validation_status_counts=validation_counts,
            system_health=system_health
        )

    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system statistics: {str(e)}"
        )


@app.get(
    "/documents/{document_id}/stats",
    response_model=DocumentStats,
    tags=["Documents"],
    summary="Get document statistics"
)
async def get_document_stats(
    document_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> DocumentStats:
    """
    Get statistics for a specific document.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

        # Count totals
        total_chunks = db.query(func.count(TextChunk.id)).filter(
            TextChunk.document_id == document_id
        ).scalar()

        total_requirements = db.query(func.count(Requirement.id)).filter(
            Requirement.document_id == document_id
        ).scalar()

        # Requirements by classification
        reqs_by_classification = {}
        classification_counts = db.query(
            Requirement.classification,
            func.count(Requirement.id)
        ).filter(Requirement.document_id == document_id).group_by(
            Requirement.classification
        ).all()
        for classification, count in classification_counts:
            reqs_by_classification[classification] = count

        # Validation status counts
        validation_counts = {}
        val_status_counts = db.query(
            Requirement.status,
            func.count(Requirement.id)
        ).filter(Requirement.document_id == document_id).group_by(
            Requirement.status
        ).all()
        for val_status, count in val_status_counts:
            validation_counts[val_status] = count

        # Confidence distribution
        confidence_dist = {}
        conf_counts = db.query(
            Requirement.ai_confidence_score,
            func.count(Requirement.id)
        ).filter(Requirement.document_id == document_id).group_by(
            Requirement.ai_confidence_score
        ).all()
        for conf_score, count in conf_counts:
            if conf_score:
                confidence_dist[conf_score] = count

        # Calculate processing time
        processing_time = None
        if document.processed_at and document.uploaded_at:
            delta = document.processed_at - document.uploaded_at
            processing_time = delta.total_seconds()

        return DocumentStats(
            document_id=document_id,
            total_chunks=total_chunks or 0,
            total_requirements=total_requirements or 0,
            requirements_by_classification=reqs_by_classification,
            validation_status_counts=validation_counts,
            processing_time_seconds=processing_time,
            confidence_distribution=confidence_dist
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document statistics: {str(e)}"
        )


# Document upload endpoint
@app.post(
    "/documents/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Documents"],
    summary="Upload RFP document"
)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
) -> FileUploadResponse:
    """
    Upload an RFP document for processing. Accepts PDF, DOCX, and TXT files.

    The file will be saved and a background processing job will be created.
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not supported. Allowed: {ALLOWED_EXTENSIONS}"
            )

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size {file_size} exceeds maximum {MAX_FILE_SIZE} bytes"
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        # Generate unique IDs
        doc_id = uuid.uuid4()
        job_id = uuid.uuid4()

        # Save file
        file_path = UPLOAD_DIR / f"{doc_id}{file_ext}"
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"File saved: {file_path}")

        # Create document record
        document = Document(
            id=doc_id,
            filename=file.filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_ext.lstrip('.'),
            mime_type=file.content_type or "application/octet-stream",
            status=ProcessingStatus.UPLOADED,
            uploaded_by="system",  # TODO: Get from auth context
            uploaded_at=datetime.utcnow()
        )
        db.add(document)

        # Create processing job
        job = ProcessingJob(
            id=job_id,
            document_id=doc_id,
            job_type="extraction",
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(job)

        db.commit()

        logger.info(f"Document {doc_id} and job {job_id} created")

        # Start background processing
        background_tasks.add_task(process_document_async, doc_id, job_id)

        return FileUploadResponse(
            job_id=job_id,
            document_id=doc_id,
            message=f"Document uploaded successfully. Processing started.",
            status="processing"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


# Document status endpoint
@app.get(
    "/documents/{document_id}/status",
    tags=["Documents"],
    summary="Get document processing status"
)
async def get_document_status(
    document_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the processing status of a document.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

        # Get associated job
        job = db.query(ProcessingJob).filter(
            ProcessingJob.document_id == document_id
        ).order_by(ProcessingJob.created_at.desc()).first()

        response = {
            "document_id": str(document_id),
            "status": document.status,
            "uploaded_at": document.uploaded_at.isoformat(),
            "processed_at": document.processed_at.isoformat() if document.processed_at else None
        }

        if job:
            response["job"] = {
                "job_id": str(job.id),
                "status": job.status,
                "total_items": job.total_items,
                "processed_items": job.processed_items,
                "error_count": job.error_count,
                "error_message": job.error_message
            }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document status: {str(e)}"
        )


# List documents endpoint
@app.get(
    "/documents",
    response_model=List[DocumentResponse],
    tags=["Documents"],
    summary="List all documents"
)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[ProcessingStatus] = None,
    db: Session = Depends(get_db)
) -> List[DocumentResponse]:
    """
    List all uploaded documents with optional filtering.
    """
    try:
        query = db.query(Document).order_by(Document.uploaded_at.desc())

        if status_filter:
            query = query.filter(Document.status == status_filter)

        documents = query.offset(skip).limit(limit).all()

        return [DocumentResponse.from_orm(doc) for doc in documents]

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


# Review queue endpoint
@app.get(
    "/requirements/review_queue",
    response_model=ReviewQueueResponse,
    tags=["Requirements"],
    summary="Get requirements pending validation"
)
async def get_review_queue(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    confidence_filter: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    classification_filter: Optional[RequirementClassification] = None,
    db: Session = Depends(get_db)
) -> ReviewQueueResponse:
    """
    Get a queue of requirements pending human validation, ordered by confidence (lowest first).
    """
    try:
        # Base query: requirements needing validation
        query = db.query(Requirement).filter(
            Requirement.status == ValidationStatus.AI_EXTRACTED
        )

        # Apply filters
        if confidence_filter:
            query = query.filter(Requirement.ai_confidence_score == confidence_filter)

        if classification_filter:
            query = query.filter(Requirement.classification == classification_filter)

        # Order by confidence (low confidence first)
        confidence_order = {
            'low': 1,
            'medium': 2,
            'high': 3
        }

        # Get total count
        total_count = query.count()

        # Get paginated results
        requirements = query.order_by(
            Requirement.created_at.asc()
        ).offset(skip).limit(limit).all()

        items = [ReviewQueueItem.from_orm(req) for req in requirements]

        return ReviewQueueResponse(
            items=items,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
            has_more=(skip + limit) < total_count
        )

    except Exception as e:
        logger.error(f"Error getting review queue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get review queue: {str(e)}"
        )


# Update requirement endpoint
@app.put(
    "/requirements/{requirement_id}",
    response_model=RequirementResponse,
    tags=["Requirements"],
    summary="Update and validate a requirement"
)
async def update_requirement(
    requirement_id: uuid.UUID,
    validation: ValidationRequest,
    db: Session = Depends(get_db)
) -> RequirementResponse:
    """
    Update a requirement with human validation. Supports approve, correct, and flag actions.
    """
    try:
        requirement = db.query(Requirement).filter(
            Requirement.id == requirement_id
        ).first()

        if not requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Requirement {requirement_id} not found"
            )

        # Store previous state in history
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": validation.action,
            "user": "system",  # TODO: Get from auth context
            "previous_status": requirement.status,
            "previous_clean_text": requirement.clean_text,
            "previous_classification": requirement.classification,
            "notes": validation.validation_notes
        }

        if requirement.history:
            requirement.history.append(history_entry)
        else:
            requirement.history = [history_entry]

        # Update fields based on action
        if validation.action == "approve":
            requirement.status = ValidationStatus.HUMAN_VALIDATED
            if validation.clean_text:
                requirement.clean_text = validation.clean_text
            if validation.classification:
                requirement.classification = validation.classification

        elif validation.action == "correct":
            requirement.status = ValidationStatus.HUMAN_CORRECTED
            if validation.clean_text:
                requirement.clean_text = validation.clean_text
            if validation.classification:
                requirement.classification = validation.classification

        elif validation.action == "flag":
            requirement.status = ValidationStatus.FLAGGED_FOR_REVIEW

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {validation.action}"
            )

        # Add validation notes
        if validation.validation_notes:
            requirement.validation_notes = validation.validation_notes

        # Update audit fields
        requirement.validated_by = "system"  # TODO: Get from auth context
        requirement.validated_at = datetime.utcnow()
        requirement.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(requirement)

        logger.info(f"Requirement {requirement_id} updated: {validation.action}")

        return RequirementResponse.from_orm(requirement)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating requirement: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update requirement: {str(e)}"
        )


# Search endpoint
@app.post(
    "/search",
    response_model=SearchResponse,
    tags=["Search"],
    summary="Search requirements"
)
async def search_requirements(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
) -> SearchResponse:
    """
    Search requirements using text matching. Vector search will be implemented when embeddings are available.
    """
    try:
        query = db.query(Requirement)

        # Text search (basic implementation)
        search_term = f"%{search_request.query}%"
        query = query.filter(
            or_(
                Requirement.raw_text.ilike(search_term),
                Requirement.clean_text.ilike(search_term)
            )
        )

        # Apply filters
        if search_request.document_ids:
            query = query.filter(Requirement.document_id.in_(search_request.document_ids))

        if search_request.classifications:
            query = query.filter(Requirement.classification.in_(search_request.classifications))

        if search_request.statuses:
            query = query.filter(Requirement.status.in_(search_request.statuses))

        # Get results
        total_count = query.count()
        requirements = query.limit(search_request.limit).all()

        results = [SearchResult.from_orm(req) for req in requirements]

        return SearchResponse(
            results=results,
            total_count=total_count,
            query=search_request.query
        )

    except Exception as e:
        logger.error(f"Error searching requirements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# Compliance matrix endpoint
@app.get(
    "/documents/{document_id}/compliance-matrix",
    response_model=ComplianceMatrixResponse,
    tags=["Documents"],
    summary="Generate compliance matrix"
)
async def get_compliance_matrix(
    document_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> ComplianceMatrixResponse:
    """
    Generate a compliance matrix for a document showing all requirements,
    their classifications, and cross-references.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

        # Get all requirements for this document
        requirements = db.query(Requirement).filter(
            Requirement.document_id == document_id
        ).order_by(
            Requirement.source_page,
            Requirement.source_paragraph
        ).all()

        # Build compliance matrix items
        items = []
        for req in requirements:
            # Get cross-references
            cross_refs = db.query(CrossReference).filter(
                CrossReference.requirement_id == req.id
            ).all()

            item = ComplianceMatrixItem(
                requirement_id=req.id,
                requirement_text=req.clean_text or req.raw_text,
                classification=req.classification,
                source_section=req.source_section or "Unknown",
                source_subsection=req.source_subsection,
                source_page=req.source_page,
                related_instructions=[],  # TODO: Implement
                evaluation_criteria=[],  # TODO: Implement
                cross_references=[ref.reference_text for ref in cross_refs],
                status=req.status
            )
            items.append(item)

        # Calculate counts
        total_requirements = len(items)
        validated_requirements = sum(
            1 for item in items
            if item.status in [ValidationStatus.HUMAN_VALIDATED, ValidationStatus.HUMAN_CORRECTED]
        )
        pending_requirements = sum(
            1 for item in items
            if item.status == ValidationStatus.AI_EXTRACTED
        )

        return ComplianceMatrixResponse(
            document_id=document_id,
            document_name=document.original_filename,
            items=items,
            total_requirements=total_requirements,
            validated_requirements=validated_requirements,
            pending_requirements=pending_requirements,
            generated_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating compliance matrix: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate compliance matrix: {str(e)}"
        )


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "RFP Extraction Platform API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
