"""
Pydantic models for deck generation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class DeckGenerationRequest(BaseModel):
    """Request model for deck generation"""
    request: str = Field(..., description="Natural language description of desired presentation")
    max_slides: Optional[int] = Field(None, description="Maximum number of slides (calculated from duration if not provided)")
    add_agenda: bool = Field(True, description="Whether to add an agenda slide")
    add_notes: bool = Field(True, description="Whether to generate presenter notes")
    client_name: Optional[str] = Field(None, description="Client name for customization")
    custom_title: Optional[str] = Field(None, description="Custom title for the presentation")


class SlideInfo(BaseModel):
    """Information about a selected slide"""
    id: int
    title: Optional[str]
    filename: str
    slide_number: int
    relevance_score: float
    image_url: str


class DeckGenerationResponse(BaseModel):
    """Response model for deck generation"""
    success: bool
    message: Optional[str] = None
    deck_id: Optional[str] = None
    download_url: Optional[str] = None
    slide_count: int = 0
    estimated_duration_minutes: int = 0
    parsed_request: Optional[Dict] = None
    slides: List[SlideInfo] = []


class DeckPreviewResponse(BaseModel):
    """Response model for deck preview (before generation)"""
    success: bool
    message: Optional[str] = None
    slide_count: int = 0
    estimated_duration_minutes: int = 0
    parsed_request: Optional[Dict] = None
    slides: List[SlideInfo] = []
    suggested_title: str = "Generated Presentation"


class EmbeddingStatsResponse(BaseModel):
    """Response model for embedding statistics"""
    total_embeddings: int
    collection_name: str
    persist_directory: str


class EmbeddingGenerationRequest(BaseModel):
    """Request model for generating embeddings"""
    slide_ids: Optional[List[int]] = Field(None, description="Specific slide IDs to process. If None, processes all slides.")


class EmbeddingGenerationResponse(BaseModel):
    """Response model for embedding generation"""
    success: bool
    message: str
    stats: Dict[str, int]

# Made with Bob
