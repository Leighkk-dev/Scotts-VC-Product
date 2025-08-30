"""
Document management endpoints with file upload and processing
"""

import os
import uuid
import mimetypes
from typing import Any, List, Optional
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.venture import Venture
from app.services.document_processor import document_processor, DocumentProcessingError
from app.services.nlp_processor import nlp_processor
from app.services.scoring_engine import scoring_engine
from app.schemas.document import DocumentResponse, DocumentCreate, DocumentUpdate

router = APIRouter()


async def process_document_background(
    document_id: str,
    file_path: str,
    file_type: str,
    db: AsyncSession
):
    """Background task for document processing"""
    try:
        # Update status to processing
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(
                processing_status='processing',
                processing_started_at=datetime.utcnow()
            )
        )
        await db.commit()
        
        # Process the document
        processing_result = await document_processor.process_document(
            file_path, file_type, document_id
        )
        
        # Run NLP analysis on extracted content
        extracted_text = processing_result.get('extracted_content', {}).get('full_text', '')
        nlp_result = await nlp_processor.analyze_text(extracted_text)
        
        # Calculate investment scores
        score_result = await scoring_engine.calculate_investment_score(
            nlp_result, processing_result
        )
        
        # Update document with results
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(
                processing_status='completed',
                processing_completed_at=datetime.utcnow(),
                extracted_content=processing_result.get('extracted_content'),
                structured_data=nlp_result,
                entities=nlp_result.get('entities'),
                financial_data=nlp_result.get('financial_metrics'),
                confidence_score=str(nlp_result.get('confidence_score', 0.5)),
                text_quality=str(processing_result.get('quality_metrics', {}).get('text_quality_score', 0.5)),
                data_completeness=str(score_result.confidence_interval[1] / 100)
            )
        )
        await db.commit()
        
    except Exception as e:
        # Update status to failed
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(
                processing_status='failed',
                processing_error=str(e),
                processing_completed_at=datetime.utcnow()
            )
        )
        await db.commit()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    venture_id: str = Form(...),
    document_type: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Upload and process a document"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Validate file type
    file_type = file.content_type
    if file_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_type} not supported. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    # Verify venture exists and user has access
    result = await db.execute(
        select(Venture)
        .where(Venture.id == venture_id)
    )
    venture = result.scalar_one_or_none()
    
    if not venture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venture not found"
        )
    
    # TODO: Check if user has access to this venture (organization membership)
    
    try:
        # Create unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create document record
        document = Document(
            venture_id=venture_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_type=file_type,
            mime_type=file_type,
            file_size=len(content),
            storage_path=str(file_path),
            processing_status='pending',
            document_type=document_type,
            virus_scan_status='pending'  # TODO: Implement virus scanning
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        # Start background processing
        background_tasks.add_task(
            process_document_background,
            str(document.id),
            str(file_path),
            file_type,
            db
        )
        
        return DocumentResponse(
            id=document.id,
            venture_id=document.venture_id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            processing_status=document.processing_status,
            document_type=document.document_type,
            created_at=document.created_at
        )
        
    except Exception as e:
        # Clean up file if document creation failed
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    venture_id: Optional[str] = None,
    processing_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List documents with optional filtering"""
    
    query = select(Document)
    
    if venture_id:
        query = query.where(Document.venture_id == venture_id)
    
    if processing_status:
        query = query.where(Document.processing_status == processing_status)
    
    # TODO: Filter by user's accessible ventures (organization membership)
    
    query = query.offset(skip).limit(limit).order_by(Document.created_at.desc())
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [
        DocumentResponse(
            id=doc.id,
            venture_id=doc.venture_id,
            filename=doc.filename,
            original_filename=doc.original_filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            processing_status=doc.processing_status,
            document_type=doc.document_type,
            confidence_score=float(doc.confidence_score) if doc.confidence_score else None,
            text_quality=float(doc.text_quality) if doc.text_quality else None,
            created_at=doc.created_at,
            processing_completed_at=doc.processing_completed_at
        )
        for doc in documents
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get document details"""
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # TODO: Check if user has access to this document
    
    return DocumentResponse(
        id=document.id,
        venture_id=document.venture_id,
        filename=document.filename,
        original_filename=document.original_filename,
        file_type=document.file_type,
        file_size=document.file_size,
        processing_status=document.processing_status,
        document_type=document.document_type,
        confidence_score=float(document.confidence_score) if document.confidence_score else None,
        text_quality=float(document.text_quality) if document.text_quality else None,
        data_completeness=float(document.data_completeness) if document.data_completeness else None,
        created_at=document.created_at,
        processing_started_at=document.processing_started_at,
        processing_completed_at=document.processing_completed_at,
        processing_error=document.processing_error
    )


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get extracted document content and analysis"""
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # TODO: Check if user has access to this document
    
    if document.processing_status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document processing not completed. Status: {document.processing_status}"
        )
    
    return {
        'document_id': document.id,
        'processing_status': document.processing_status,
        'extracted_content': document.extracted_content,
        'structured_data': document.structured_data,
        'entities': document.entities,
        'financial_data': document.financial_data,
        'quality_metrics': {
            'confidence_score': float(document.confidence_score) if document.confidence_score else None,
            'text_quality': float(document.text_quality) if document.text_quality else None,
            'data_completeness': float(document.data_completeness) if document.data_completeness else None
        }
    }


@router.get("/{document_id}/status")
async def get_processing_status(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get document processing status"""
    
    result = await db.execute(
        select(Document.processing_status, Document.processing_started_at, 
               Document.processing_completed_at, Document.processing_error)
        .where(Document.id == document_id)
    )
    document_status = result.first()
    
    if not document_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Calculate processing time if applicable
    processing_time = None
    if document_status.processing_started_at:
        end_time = document_status.processing_completed_at or datetime.utcnow()
        processing_time = (end_time - document_status.processing_started_at).total_seconds()
    
    return {
        'document_id': document_id,
        'status': document_status.processing_status,
        'started_at': document_status.processing_started_at,
        'completed_at': document_status.processing_completed_at,
        'processing_time_seconds': processing_time,
        'error': document_status.processing_error
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete a document"""
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # TODO: Check if user has permission to delete this document
    
    try:
        # Delete file from storage
        file_path = Path(document.storage_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete database record
        await db.delete(document)
        await db.commit()
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Reprocess a document"""
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # TODO: Check if user has permission to reprocess this document
    
    # Check if file still exists
    file_path = Path(document.storage_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original file no longer exists"
        )
    
    # Reset processing status
    await db.execute(
        update(Document)
        .where(Document.id == document_id)
        .values(
            processing_status='pending',
            processing_started_at=None,
            processing_completed_at=None,
            processing_error=None,
            extracted_content=None,
            structured_data=None,
            entities=None,
            financial_data=None
        )
    )
    await db.commit()
    
    # Start background processing
    background_tasks.add_task(
        process_document_background,
        document_id,
        str(file_path),
        document.file_type,
        db
    )
    
    return {"message": "Document reprocessing started"}


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Download original document file"""
    
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # TODO: Check if user has access to this document
    
    file_path = Path(document.storage_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on storage"
        )
    
    from fastapi.responses import FileResponse
    
    return FileResponse(
        path=str(file_path),
        filename=document.original_filename,
        media_type=document.file_type
    )