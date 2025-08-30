"""
Document schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str
    original_filename: str
    file_type: str
    document_type: Optional[str] = None


class DocumentCreate(BaseModel):
    """Document creation schema"""
    venture_id: str
    document_type: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Document update schema"""
    document_type: Optional[str] = None


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: uuid.UUID
    venture_id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    processing_status: str
    document_type: Optional[str] = None
    confidence_score: Optional[float] = None
    text_quality: Optional[float] = None
    data_completeness: Optional[float] = None
    created_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentContent(BaseModel):
    """Document content schema"""
    document_id: uuid.UUID
    processing_status: str
    extracted_content: Optional[Dict[str, Any]] = None
    structured_data: Optional[Dict[str, Any]] = None
    entities: Optional[Dict[str, Any]] = None
    financial_data: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None


class ProcessingStatus(BaseModel):
    """Processing status schema"""
    document_id: uuid.UUID
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    error: Optional[str] = None
